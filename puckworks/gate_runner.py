"""Typed, complete gate evaluation (P0.2).

The legacy `registry.run_all_gates()` delegated through `all(...)`, which short-circuits: a failing
component stopped every later component from running, an exception aborted the whole run, and a
zero-gate component vacuously passed. This module runs EVERY applicable gate, captures each
result (including exceptions) as a typed `GateResult`, and reports zero-gate components explicitly
rather than as a silent pass.

    from puckworks.gate_runner import evaluate_all_gates
    suite = evaluate_all_gates()
    suite.passed            # bool: no FAIL and no ERROR
    suite.to_dict()         # deterministic JSON-able report (runtime fields optional)

`registry.run_gates` / `run_all_gates` remain as Boolean compatibility wrappers.
"""
from __future__ import annotations

import platform
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

SCHEMA_VERSION = 1


class GateStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"
    ACKNOWLEDGED_EXCEPTION = "ACKNOWLEDGED_EXCEPTION"


# statuses that make a suite fail
_FAILING = (GateStatus.FAIL, GateStatus.ERROR)


@dataclass
class GateResult:
    component_id: str
    gate_id: str
    status: GateStatus
    summary: str = ""
    metrics: dict = field(default_factory=dict)
    artifacts: list = field(default_factory=list)
    evidence_links: list = field(default_factory=list)
    exception_type: Optional[str] = None
    exception_message: Optional[str] = None
    duration_s: Optional[float] = None
    schema_version: int = SCHEMA_VERSION

    def to_dict(self, include_runtime=True):
        d = asdict(self)
        d["status"] = self.status.value
        if not include_runtime:
            d.pop("duration_s", None)
        return d


@dataclass
class GateSuiteResult:
    results: list  # list[GateResult]
    started_at: Optional[float] = None
    commit: Optional[str] = None
    environment: dict = field(default_factory=dict)
    schema_version: int = SCHEMA_VERSION

    @property
    def counts_by_status(self):
        c = {s.value: 0 for s in GateStatus}
        for r in self.results:
            c[r.status.value] += 1
        return c

    @property
    def passed(self):
        return not any(r.status in _FAILING for r in self.results)

    def to_dict(self, include_runtime=True):
        d = {
            "schema_version": self.schema_version,
            "passed": self.passed,
            "counts_by_status": self.counts_by_status,
            "results": [r.to_dict(include_runtime=include_runtime) for r in self.results],
        }
        if include_runtime:
            d["started_at"] = self.started_at
            d["commit"] = self.commit
            d["environment"] = self.environment
        return d

    def summary_text(self):
        c = self.counts_by_status
        head = "gates: %s  (%s)" % (
            "PASSED" if self.passed else "FAILED",
            ", ".join("%s=%d" % (k, v) for k, v in c.items() if v))
        lines = [head]
        for r in self.results:
            if r.status in (GateStatus.FAIL, GateStatus.ERROR):
                extra = r.exception_message or r.summary or ""
                lines.append("  %-5s %s::%s  %s" % (r.status.value, r.component_id, r.gate_id,
                                                    extra[:120]))
        return "\n".join(lines)


# --------------------------------------------------------------------------- evaluation
def _coerce_legacy(component_id, gate_id, raw, duration_s):
    """Turn a legacy gate return value into a typed GateResult. A mapping must carry `passed`;
    anything else is an ERROR (never a silent pass)."""
    if not isinstance(raw, dict):
        return GateResult(component_id, gate_id, GateStatus.ERROR,
                          summary="gate did not return a mapping",
                          exception_type="TypeError",
                          exception_message="expected dict, got %s" % type(raw).__name__,
                          duration_s=duration_s)
    if "passed" not in raw:
        return GateResult(component_id, gate_id, GateStatus.ERROR,
                          summary="gate result missing 'passed'",
                          exception_type="KeyError", exception_message="'passed'",
                          duration_s=duration_s)
    status = GateStatus.PASS if bool(raw["passed"]) else GateStatus.FAIL
    metrics = {k: v for k, v in raw.items() if k != "passed"}
    summary = str(metrics.get("reading") or metrics.get("summary") or "")
    return GateResult(component_id, gate_id, status, summary=summary, metrics=metrics,
                      duration_s=duration_s)


def evaluate_gate(component_id: str, gate: Callable[[], Any]) -> GateResult:
    """Run one gate, capturing exceptions as ERROR (never propagating)."""
    gate_id = getattr(gate, "__name__", repr(gate))
    t0 = time.perf_counter()
    try:
        raw = gate()
    except Exception as e:   # noqa: BLE001 - every gate exception becomes an ERROR result
        return GateResult(component_id, gate_id, GateStatus.ERROR,
                          summary="gate raised %s" % type(e).__name__,
                          exception_type=type(e).__name__, exception_message=str(e),
                          duration_s=time.perf_counter() - t0)
    return _coerce_legacy(component_id, gate_id, raw, time.perf_counter() - t0)


def _zero_gate_result(component_id):
    """Explicit status for a component with no gate — SKIP, or ACKNOWLEDGED_EXCEPTION when the
    evidence policy records it. NEVER a PASS."""
    try:
        from puckworks.paper3.evidence_graph import ZERO_GATE_EXCEPTIONS
    except Exception:   # pragma: no cover
        ZERO_GATE_EXCEPTIONS = {}
    if component_id in ZERO_GATE_EXCEPTIONS:
        return GateResult(component_id, "<none>", GateStatus.ACKNOWLEDGED_EXCEPTION,
                          summary=ZERO_GATE_EXCEPTIONS[component_id])
    return GateResult(component_id, "<none>", GateStatus.SKIP,
                      summary="component has no gate (not represented as a pass)")


def evaluate_component_gates(component_id: str, component=None) -> list:
    """Every gate of one component, deterministically ordered. Zero-gate -> one explicit result."""
    if component is None:
        from puckworks import registry as R
        component = R.get(component_id)
    gates = sorted(component.gates, key=lambda g: getattr(g, "__name__", ""))
    if not gates:
        return [_zero_gate_result(component_id)]
    return [evaluate_gate(component_id, g) for g in gates]


def _commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parents[1]).stdout.strip() or None
    except Exception:   # pragma: no cover
        return None


def evaluate_all_gates(components=None) -> GateSuiteResult:
    """Evaluate EVERY component's gates, deterministically, WITHOUT short-circuiting on failure."""
    if components is None:
        from puckworks import registry as R
        components = sorted(R.components(), key=lambda c: c.name)
    results = []
    for c in components:
        results.extend(evaluate_component_gates(c.name, c))
    env = {"python": sys.version.split()[0], "platform": platform.platform(),
           "numpy": _pkg_version("numpy"), "scipy": _pkg_version("scipy")}
    return GateSuiteResult(results=results, started_at=None, commit=_commit(), environment=env)


def _pkg_version(name):
    try:
        import importlib
        return getattr(importlib.import_module(name), "__version__", None)
    except Exception:   # pragma: no cover
        return None


def write_report(path, suite: GateSuiteResult):
    import json
    Path(path).write_text(json.dumps(suite.to_dict(), indent=2, default=str) + "\n",
                          encoding="utf-8")
    return path


def main(argv=None):
    import json
    argv = sys.argv[1:] if argv is None else argv
    suite = evaluate_all_gates()
    if "--json" in argv:
        print(json.dumps(suite.to_dict(), indent=2, default=str))
    else:
        print(suite.summary_text())
    out = [a for a in argv if a.startswith("--report=")]
    if out:
        write_report(out[0].split("=", 1)[1], suite)
    return 0 if suite.passed else 1


if __name__ == "__main__":   # pragma: no cover
    raise SystemExit(main())

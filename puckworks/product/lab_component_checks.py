"""Rights-aware, Laboratory-facing component-check runner (Phase 3, #43 / #70).

`run_component_checks` executes a SELECTED set of components' REGISTERED gate(s) — the Laboratory never
exposes an unfiltered `evaluate_all_gates()`. Rights are resolved BEFORE any gate/model/import call: a
`RIGHTS_BLOCKED` component receives ZERO execution calls; in public contexts affirmative code (and, for
`PUBLIC_ARTIFACT`, output) clearance is required — this never broadens public availability. It reuses the
authoritative `puckworks.gate_runner` (gate thresholds/formulas are NOT copied here), preserves
per-component AND per-gate failure isolation, and keeps these outcomes distinct:

  EXECUTED · CHECK_FAILED (a gate FAILed) · EXECUTION_ERROR (a gate raised) · RIGHTS_BLOCKED ·
  RIGHTS_NOT_CLEARED (public gap) · OPTIONAL_DEPENDENCY_UNAVAILABLE · NO_GATE_ACKNOWLEDGED · NOT_SELECTED

A gate pass is a code/consistency check — NOT experimental validation and NOT a full model simulation. A
numerical exception is represented as an ERROR, never as a scientific zero. Blocked/unavailable/not-run
results carry no metrics and no scientific hash.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import time
from enum import Enum


class ComponentCheckStatus(str, Enum):
    EXECUTED = "EXECUTED"
    CHECK_FAILED = "CHECK_FAILED"
    EXECUTION_ERROR = "EXECUTION_ERROR"
    RIGHTS_BLOCKED = "RIGHTS_BLOCKED"
    RIGHTS_NOT_CLEARED = "RIGHTS_NOT_CLEARED"
    OPTIONAL_DEPENDENCY_UNAVAILABLE = "OPTIONAL_DEPENDENCY_UNAVAILABLE"
    NO_GATE_ACKNOWLEDGED = "NO_GATE_ACKNOWLEDGED"
    NOT_SELECTED = "NOT_SELECTED"


# metric-name → unit convention (best-effort; the gate owns the number, we only label it for display)
_UNIT_SUFFIX = {"_pct": "percent", "_bar": "bar", "_s": "s", "_g": "g", "_m2": "m^2", "_ratio": "ratio",
                "_c": "degC", "_k": "K"}


def _metric_unit(name: str) -> str:
    for suf, unit in _UNIT_SUFFIX.items():
        if name.endswith(suf):
            return unit
    return ""


@dataclasses.dataclass(frozen=True)
class ComponentCheckResult:
    component_id: str
    stage: str
    execution_status: str
    rights_state: str                 # the component's code rights state
    rights_decision: dict
    blocker: str
    gates: list                       # [{gate_id, status, metrics, units, summary, exception_type, duration_seconds}]
    scientific_hash: str | None
    duration_seconds: float | None
    evidence: dict
    fidelity_ceiling: str
    message: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def context_clearance(component_id: str, execution_context: str):
    """(allowed, blocker). LOCAL_PRIVATE: blocked only on RIGHTS_BLOCKED (NOT_REVIEWED stays inspectable
    under existing policy). Public: affirmative code (and output for PUBLIC_ARTIFACT) required — never
    broadened here."""
    from puckworks import rights
    if execution_context in ("PUBLIC_BATCH", "PUBLIC_ARTIFACT"):
        code = rights.may_execute_in_public_batch(component_id)
        if not code.allowed:
            return False, f"code not cleared for {execution_context} ({code.governing_state})"
        if execution_context == "PUBLIC_ARTIFACT":
            out = rights.may_publish_outputs(component_id)
            if not out.allowed:
                return False, f"output not cleared for publication ({out.governing_state})"
        return True, ""
    d = rights.may_execute_locally(component_id)
    return d.allowed, ("" if d.allowed else f"rights-blocked ({d.governing_state})")


def _rights_decision(component_id: str) -> dict:
    from puckworks import rights
    r = rights.rights_record(component_id)
    return {"code_rights_state": r.code_rights_state, "data_rights_state": r.data_rights_state,
            "output_redistribution_state": r.output_redistribution_state, "decision_issue": r.decision_issue}


def _evidence(component) -> dict:
    return {"evidence_strength": getattr(component, "evidence_strength", ""),
            "note": "a gate pass is a code/consistency check, NOT experimental validation"}


_FIDELITY = ("registered scientific check on the gate's own fixture; NOT a full model simulation and NOT "
             "experimental validation")


def _blocked_result(component, status: ComponentCheckStatus, blocker: str) -> ComponentCheckResult:
    from puckworks import rights
    cid = component.name
    return ComponentCheckResult(
        component_id=cid, stage=getattr(component, "stage", ""), execution_status=status.value,
        rights_state=rights.rights_record(cid).code_rights_state, rights_decision=_rights_decision(cid),
        blocker=blocker, gates=[], scientific_hash=None, duration_seconds=None,
        evidence={}, fidelity_ceiling="", message=blocker or status.value)


def _run_one(component, execution_context: str) -> ComponentCheckResult:
    from puckworks import rights
    cid = component.name
    # RIGHTS FIRST — a rights-blocked component NEVER reaches its gates/model/import path.
    allowed, blocker = context_clearance(cid, execution_context)
    if not allowed:
        blocked = rights.is_code_rights_blocked(cid)
        status = ComponentCheckStatus.RIGHTS_BLOCKED if blocked else ComponentCheckStatus.RIGHTS_NOT_CLEARED
        return _blocked_result(component, status, blocker)
    from puckworks import gate_runner as G
    t0 = time.perf_counter()
    try:
        gate_results = G.evaluate_component_gates(cid, component)   # per-gate isolation inside
    except Exception as exc:                                        # pragma: no cover - defensive
        return _blocked_result(component, ComponentCheckStatus.EXECUTION_ERROR, f"{type(exc).__name__}: {exc}")
    dur = time.perf_counter() - t0
    statuses = [gr.status.value for gr in gate_results]
    if "ERROR" in statuses:
        status = ComponentCheckStatus.EXECUTION_ERROR
    elif "FAIL" in statuses:
        status = ComponentCheckStatus.CHECK_FAILED
    elif statuses and all(s in ("SKIP", "ACKNOWLEDGED_EXCEPTION") for s in statuses):
        status = ComponentCheckStatus.NO_GATE_ACKNOWLEDGED
    else:
        status = ComponentCheckStatus.EXECUTED
    gates = [{"gate_id": gr.gate_id, "status": gr.status.value, "metrics": gr.metrics,
              "units": {k: _metric_unit(k) for k in gr.metrics if _metric_unit(k)},
              "summary": gr.summary, "exception_type": gr.exception_type,
              "duration_seconds": gr.duration_s} for gr in gate_results]
    # canonical scientific content EXCLUDES durations/exception messages/paths
    payload = {"component_id": cid, "gates": [{"gate_id": gr.gate_id, "status": gr.status.value,
               "metrics": gr.metrics} for gr in gate_results]}
    return ComponentCheckResult(
        component_id=cid, stage=getattr(component, "stage", ""), execution_status=status.value,
        rights_state=rights.rights_record(cid).code_rights_state, rights_decision=_rights_decision(cid),
        blocker="", gates=gates,
        scientific_hash=hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest(),
        duration_seconds=dur, evidence=_evidence(component), fidelity_ceiling=_FIDELITY,
        message="ran the component's registered scientific gate(s)")


def run_component_checks(component_ids, *, execution_context: str,
                         all_component_ids=None) -> tuple:
    """Run the REGISTERED gate(s) of the selected components, rights-checked FIRST, with per-component and
    per-gate failure isolation. Deterministic order. An unregistered id raises (fails distinctly). When
    ``all_component_ids`` is given, every non-selected id in it is returned as a NOT_SELECTED resolution
    (never silently dropped)."""
    from puckworks.product import lab_rights_gate as gate
    if execution_context not in gate.EXECUTION_CONTEXTS:
        raise ValueError(f"execution_context must be one of {gate.EXECUTION_CONTEXTS}, "
                         f"got {execution_context!r}")
    import puckworks
    registered = {c.name: c for c in puckworks.components()}
    selected = list(dict.fromkeys(component_ids))          # dedupe, preserve first-seen
    unknown = [c for c in selected if c not in registered]
    if unknown:
        raise ValueError(f"unknown component id(s): {sorted(set(unknown))} (not registered)")
    results = [_run_one(registered[cid], execution_context) for cid in sorted(selected)]
    if all_component_ids is not None:
        sel = set(selected)
        for cid in sorted(set(all_component_ids) - sel):
            if cid in registered:                          # a real component that was simply not selected
                results.append(_blocked_result(registered[cid], ComponentCheckStatus.NOT_SELECTED,
                                               "not selected for this check run"))
    return tuple(results)

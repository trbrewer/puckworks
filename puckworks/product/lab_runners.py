"""Native reference runners for the Guided Pull Laboratory (PV-19B, #70).

A native reference runner executes a registered component's OWN provenance-bound reference case (the
same authoritative callables the validation gates use), for registry visibility — NOT a prediction of
the common Guided Pull shot. Two authority rules keep a runner honest:

1. **The gate owns the pass/band decision.** Every pass/fail band or threshold (the wadsworth
   `0.7 < ratio < 1.2` collapse band, the foster `> 0.5 g` first-drip threshold, the waszkiewicz refit
   tolerances) lives in ONE place — the component's quick gate. Each runner *calls its gate* and surfaces
   that verdict verbatim rather than re-deriving a duplicated literal, so a magic number can never drift
   between the runner and the authority.
2. **No invented crossing.** The foster runner detects the first-drip crossing explicitly; when the
   weight never crosses the threshold there is NO first drip (reported unavailable), never a spurious
   `argmax`-of-all-False sample at t[0].

Each result carries native inputs (units + provenance), outputs (units + roles), the component's registry
evidence (never upgraded), a fidelity ceiling, the authoritative gate verdict, and a scientific-payload
hash. Results are schema-validated and finite (no NaN/Infinity). Failures are isolated: one runner
erroring never erases the others. Selection is explicit — an unknown runner id raises, never a silent drop.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json

# runtime classes (interactive-fast runners are safe to run in the UI/CLI by default)
RUNTIME_CLASSES = ("interactive-fast", "interactive-optional", "batch-only", "optional-accelerator",
                   "unavailable")


@dataclasses.dataclass(frozen=True)
class RunnerSpec:
    runner_id: str
    version: str
    component_id: str
    runtime_class: str
    dependency_requirements: tuple = ()
    # NOTE: rights are NOT asserted here. A runner has no local "clear" claim; its rights come from the
    # centralized puckworks.rights record for its component (consumed in execute_runner).

    def __post_init__(self):
        if not self.runner_id or not self.version or not self.component_id:
            raise ValueError("RunnerSpec requires non-empty runner_id, version, component_id")
        if self.runtime_class not in RUNTIME_CLASSES:
            raise ValueError(f"{self.runner_id}: runtime_class {self.runtime_class!r} not in "
                             f"{RUNTIME_CLASSES}")


def _evidence(component_id: str) -> dict:
    import puckworks
    for c in puckworks.components():
        if c.name == component_id:
            return {"evidence_strength": c.evidence_strength, "provenance_class": c.provenance_class,
                    "n_gates": len(c.gates), "validity_range": c.valid_range,
                    "card": f"docs/cards/{component_id.split('.')[0]}.md"}
    return {}


def _num(x):
    return round(float(x), 6)


def _plain(obj):
    """Coerce numpy scalars (np.bool_/np.floating/np.integer) to plain JSON types so a gate verdict is
    serializable + hashable. Leaves ordinary Python values untouched."""
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    if isinstance(obj, bool):
        return bool(obj)
    item = getattr(obj, "item", None)                 # numpy scalar -> python scalar
    if callable(item) and getattr(obj, "ndim", None) == 0:
        return obj.item()
    return obj


def _gate(name: str) -> dict:
    """Call a component's authoritative quick gate and return its verdict dict (the single source of the
    pass/band decision — never re-derived as a duplicated literal in this module). Verdict values are
    coerced to plain JSON types."""
    from puckworks.validation import gates as G
    return _plain(dict(getattr(G, name)()))


# display rounding is SEPARATE from the stored full-precision value (never round before hashing)
def _out(name, value, unit, role, **extra):
    """One output carrying the full-precision `value` plus a display-rounded companion (no rounding of the
    scientific value itself)."""
    disp = round(value, 6) if isinstance(value, float) else value
    return {"name": name, "value": value, "display_value": disp, "unit": unit, "role": role, **extra}


def _first_crossing_time(t, w, threshold: float):
    """Back-compat alias for the authoritative model helper (single-sourced in foster2025.infiltration)."""
    from puckworks.models.foster2025 import infiltration as inf
    return inf.observed_first_drip_s(t, w, threshold)


# ── the runners (each consumes ONE shared full-precision summary + surfaces the gate verdict) ──
def _run_waszkiewicz_static() -> dict:
    from puckworks.product import lab_reference_producers as P
    s = P.waszkiewicz_static_summary()
    v = s["values"]
    gate = _gate(s["gate"])                            # authoritative refit tolerances live in the gate
    return {
        "native_inputs": s["native_inputs"],
        "outputs": [
            _out("refit_P_c", v["refit_P_c"], "bar", "fitted"),
            _out("refit_Q_c", v["refit_Q_c"], "g/s", "fitted"),
            _out("published_P_c", v["published_P_c"], "bar", "reference"),
            _out("published_Q_c", v["published_Q_c"], "g/s", "reference"),
            _out("refit_matches_published_gate", bool(gate["passed"]), "boolean", "derived")],
        "gate_authority": {"gate": s["gate"], "verdict": gate},
        "method": s["method"] + "; the recovery verdict is the authoritative gate result",
        "fidelity_ceiling": "one rig/coffee; post-fit reconstruction within the rig; not portable",
        "assumptions": ["quasi-static saturated poroelastic bed"],
        "caveat": "this is the component's native static-calibration reference, not the common scenario",
    }


def _run_wadsworth_permeability() -> dict:
    from puckworks.product import lab_reference_producers as P
    s = P.wadsworth_collapse_summary()
    v = s["values"]
    gate = _gate(s["gate"])                            # the 0.7 < ratio < 1.2 band lives in the gate
    return {
        "native_inputs": s["native_inputs"],
        "outputs": [
            _out("percolation_collapse_gm_ratio", v["percolation_collapse_gm_ratio"], "ratio", "reference"),
            _out("collapse_within_gate_band", bool(gate["passed"]), "boolean", "derived",
                 note="the band is defined by gate_wadsworth_collapse, not this runner")],
        "gate_authority": {"gate": s["gate"], "verdict": gate},
        "method": s["method"] + "; the pass band is the authoritative gate verdict",
        "fidelity_ceiling": "source-curve reproduction of the authors' own Table 1; untamped regime",
        "assumptions": ["percolation permeability closure"],
        "caveat": "this is the component's native permeability-collapse reference, not the common scenario",
    }


def _run_foster_infiltration() -> dict:
    from puckworks.product import lab_reference_producers as P
    s = P.foster_first_drip_summary()
    v = s["values"]
    t_drip = v["observed_first_drip_s"]
    lo, hi = v["predicted_bracket_lo_s"], v["predicted_bracket_hi_s"]
    gate = _gate(s["gate"])                            # the bracket verdict lives in the gate
    thr = s["threshold"]["first_drip_threshold_g"]
    drip_out = (_out("observed_first_drip_s", t_drip, "s", "measured", status="available")
                if t_drip is not None else
                {"name": "observed_first_drip_s", "value": None, "display_value": None, "unit": "s",
                 "role": "measured", "status": "unavailable",
                 "note": f"weight never crosses {thr} g in this fixture; no first drip (not zero)"})
    return {
        "native_inputs": s["native_inputs"],
        "outputs": [
            drip_out,
            {"name": "predicted_first_drip_bracket_s", "value": [lo, hi],
             "display_value": [None if lo is None else round(lo, 6), None if hi is None else round(hi, 6)],
             "unit": "s", "role": "predicted"},
            _out("observation_within_bracket_gate", bool(gate["passed"]), "boolean", "derived",
                 note="authoritative bracket verdict is gate_infiltration_triangle"),
            _out("observation_within_bracket_runner", v["observation_within_bracket"], "boolean", "derived",
                 note="None when there is no observed first drip; never plotted as zero")],
        "gate_authority": {"gate": s["gate"], "verdict": gate},
        "threshold": s["threshold"],
        "method": s["method"],
        "fidelity_ceiling": "sign/compatibility only; one fixture; a bracket, not a point prediction",
        "assumptions": ["sharp wetting front", "porosity between 0.173 and 0.322"],
        "caveat": "this is the component's native first-drip reference, not the common scenario",
    }


RUNNERS: dict[str, tuple] = {
    "waszkiewicz2025.poroelastic": (
        RunnerSpec("waszkiewicz_static_reference", "1", "waszkiewicz2025.poroelastic",
                   "interactive-fast"), _run_waszkiewicz_static),
    "wadsworth2026.permeability": (
        RunnerSpec("wadsworth_permeability_reference", "1", "wadsworth2026.permeability",
                   "interactive-fast"), _run_wadsworth_permeability),
    "foster2025.infiltration": (
        RunnerSpec("foster_infiltration_reference", "1", "foster2025.infiltration",
                   "interactive-fast"), _run_foster_infiltration),
}

INTERACTIVE_FAST = tuple(cid for cid, (spec, _) in RUNNERS.items()
                         if spec.runtime_class == "interactive-fast")


def _assert_no_rights_blocked_runners() -> None:
    """Policy guard: a code-rights-blocked component (centralized puckworks.rights) can never have a
    native reference runner. Fails loudly at import if one is ever registered."""
    from puckworks import rights
    bad = [cid for cid in RUNNERS if rights.is_code_rights_blocked(cid)]
    if bad:
        raise RuntimeError(f"rights-blocked components must not have native runners: {bad} (see #73)")


def validate_runners() -> list:
    """Authority audit: every runner targets a REGISTERED component, its spec key matches its
    component_id, its runtime_class is valid, and it is not rights-blocked. Returns the list of problems
    (empty == clean); also called at import as a hard guard."""
    import puckworks
    from puckworks import rights
    registered = {c.name for c in puckworks.components()}
    problems = []
    for key, (spec, fn) in RUNNERS.items():
        if spec.component_id != key:
            problems.append(f"runner key {key!r} != spec.component_id {spec.component_id!r}")
        if spec.component_id not in registered:
            problems.append(f"runner {key!r} targets an unregistered component")
        if spec.runtime_class not in RUNTIME_CLASSES:
            problems.append(f"runner {key!r} has invalid runtime_class {spec.runtime_class!r}")
        if rights.is_code_rights_blocked(spec.component_id):
            problems.append(f"runner {key!r} targets a code-rights-blocked component (#73)")
        if not callable(fn):
            problems.append(f"runner {key!r} has a non-callable producer")
    return problems


_assert_no_rights_blocked_runners()
_runner_problems = validate_runners()
if _runner_problems:                                  # pragma: no cover - import-time guard
    raise RuntimeError("invalid native runner registration: " + "; ".join(_runner_problems))


def has_runner(component_id: str) -> bool:
    return component_id in RUNNERS


def available_runners() -> list:
    """Deterministic list of registered runner component ids (the selectable set)."""
    return sorted(RUNNERS)


def runtime_class(component_id: str) -> str:
    return RUNNERS[component_id][0].runtime_class


# ── sanitized result schema (units + roles present; finite; no NaN/Infinity) ─────────
_REQUIRED_RESULT_KEYS = ("component_id", "runner_id", "status", "native_inputs", "outputs", "evidence")


def _assert_finite(obj, path="$") -> None:
    if isinstance(obj, float):
        if obj != obj or obj in (float("inf"), float("-inf")):
            raise ValueError(f"non-finite float at {path}: {obj!r}")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _assert_finite(v, f"{path}.{k}")
    elif isinstance(obj, (list, tuple)):
        for i, v in enumerate(obj):
            _assert_finite(v, f"{path}[{i}]")


def _validate_result_schema(result: dict) -> None:
    """A sanitized native-reference result: required keys present, every output carries a unit + role,
    and the whole payload is finite. Raises on violation (the caller turns it into a FAILED result)."""
    missing = [k for k in _REQUIRED_RESULT_KEYS if k not in result]
    if missing:
        raise ValueError(f"result missing required keys: {missing}")
    for o in result.get("outputs", []):
        if "unit" not in o or "role" not in o:
            raise ValueError(f"output {o.get('name')!r} missing unit/role")
    _assert_finite(result)


# finite per-runner execution-state vocabulary (one consistent, case-consistent set)
EXECUTION_STATES = (
    "EXECUTED", "FAILED", "RIGHTS_BLOCKED", "RIGHTS_REVIEW_REQUIRED", "OPTIONAL_DEPENDENCY_UNAVAILABLE",
    "RUNTIME_BUDGET_EXCEEDED", "NOT_REQUESTED", "NOT_APPLICABLE",
)


def _sanitize_error(exc: Exception) -> str:
    """A concise, path-free, user-facing failure message — never a stack trace or a filesystem path
    (developer detail is logged separately, not embedded in the published result)."""
    import re
    msg = str(exc)
    # strip absolute filesystem paths (>=2 segments, at a word boundary) — not inline slashes like unit/role
    msg = re.sub(r"(?<![\w])(?:/[\w.\-]+){2,}", "<path>", msg)
    msg = msg.replace(chr(10), " ").strip()
    if len(msg) > 200:
        msg = msg[:197] + "..."
    return f"{type(exc).__name__}: {msg}" if msg else type(exc).__name__


def _sci_hash(result: dict) -> str:
    payload = {k: v for k, v in result.items() if k != "scientific_payload_hash"}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def execute_runner(component_id: str) -> dict:
    """Execute one native reference runner. Never raises: a producer failure OR a schema/finite violation
    becomes a FAILED result so other runners still report."""
    if component_id not in RUNNERS:
        raise KeyError(f"unknown runner id {component_id!r}; available: {available_runners()}")
    spec, fn = RUNNERS[component_id]
    from puckworks import rights
    rec = rights.rights_record(component_id)             # centralized rights truth, not a local "clear"
    publish = rights.may_publish_outputs(component_id)   # may these outputs enter a public artifact?
    base = {"component_id": component_id, "runner_id": spec.runner_id, "runner_version": spec.version,
            "runtime_class": spec.runtime_class,
            "code_rights_state": rec.code_rights_state, "data_rights_state": rec.data_rights_state,
            "output_redistribution_state": rec.output_redistribution_state,
            "rights_state": rec.code_rights_state,       # back-compat alias = code rights
            "output_publication_allowed": publish.allowed,
            "output_publication_severity": publish.severity,
            "label": "This is the component's native reference case, not the common Guided Pull scenario.",
            "evidence": _evidence(component_id),
            # a failure/skip result satisfies the full schema too (empty is explicit, not missing)
            "native_inputs": [], "outputs": [], "gate_authority": None, "fidelity_ceiling": None,
            "assumptions": [], "caveat": "", "error_code": None, "error": None,
            "scientific_payload_hash": None}
    try:
        out = fn()
        result = {**base, "status": "executed", "execution_state": "EXECUTED", **out}
        _validate_result_schema(result)                # sanitized + finite before we publish it
    except Exception as exc:                            # isolate failure (producer OR schema violation)
        return {**base, "status": "FAILED", "execution_state": "FAILED",
                "error_code": type(exc).__name__, "error": _sanitize_error(exc)}
    result["scientific_payload_hash"] = _sci_hash(result)
    return result


def run_selected(component_ids, *, strict: bool = True) -> list:
    """Execute the requested runners (deterministic ordering; per-runner failure isolation). An unknown
    id raises by default (never a silent drop); pass strict=False only for a best-effort sweep."""
    ids = list(component_ids)
    unknown = [c for c in ids if c not in RUNNERS]
    if unknown and strict:
        raise ValueError(f"unknown runner id(s): {sorted(set(unknown))}; available: {available_runners()}")
    known = sorted({c for c in ids if c in RUNNERS})
    return [execute_runner(c) for c in known]

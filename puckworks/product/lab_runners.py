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


# ── the runners (each calls the component's authoritative reference callables + its gate) ──────
def _run_waszkiewicz_static() -> dict:
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    P, Q = wz.steady_state_curve()
    (P_c, Q_c), _ = wz.fit_static(P, Q)
    P_pub, Q_pub = wz.published_calibration()
    gate = _gate("gate_waszkiewicz_static_refit")     # authoritative refit tolerances live in the gate
    return {
        "native_inputs": [
            {"name": "equilibrium_curve", "value": f"{len(P)} basket-pressure points",
             "unit": "bar; g/s", "provenance": "waszkiewicz2025 static calibration (Zenodo, CC-BY)"}],
        "outputs": [
            {"name": "refit_P_c", "value": _num(P_c), "unit": "bar", "role": "fitted"},
            {"name": "refit_Q_c", "value": _num(Q_c), "unit": "g/s", "role": "fitted"},
            {"name": "published_P_c", "value": _num(P_pub), "unit": "bar", "role": "reference"},
            {"name": "published_Q_c", "value": _num(Q_pub), "unit": "g/s", "role": "reference"},
            {"name": "refit_matches_published_gate", "value": bool(gate["passed"]), "unit": "boolean",
             "role": "derived"}],
        "gate_authority": {"gate": "gate_waszkiewicz_static_refit", "verdict": gate},
        "method": "refit Eq.16 to the published 11-point equilibrium curve; the (P_c,Q_c) recovery "
                  "verdict is the authoritative gate_waszkiewicz_static_refit result",
        "fidelity_ceiling": "one rig/coffee; post-fit reconstruction within the rig; not portable",
        "assumptions": ["quasi-static saturated poroelastic bed"],
        "caveat": "this is the component's native static-calibration reference, not the common scenario",
    }


def _run_wadsworth_permeability() -> dict:
    import numpy as np
    from puckworks.models.wadsworth2026 import permeability as wp
    rows = wp.table1()
    ratios = [r["k_m2"] / wp.k_star(r["phi_p"], r["s_p"]) / r["phi_p"] ** wp.B_PERC for r in rows]
    gm = float(np.exp(np.mean(np.log(ratios))))
    gate = _gate("gate_wadsworth_collapse")           # the 0.7 < ratio < 1.2 band lives in the gate
    return {
        "native_inputs": [
            {"name": "table1", "value": f"{len(rows)} measured (k, phi_p, s_p) rows", "unit": "m^2; -; -",
             "provenance": "wadsworth2026 Table 1 (measured permeability + packing)"}],
        "outputs": [
            {"name": "percolation_collapse_gm_ratio", "value": _num(gm), "unit": "ratio",
             "role": "reference"},
            {"name": "collapse_within_gate_band", "value": bool(gate["passed"]), "unit": "boolean",
             "role": "derived",
             "note": "band (0.7 < ratio < 1.2) is defined by gate_wadsworth_collapse, not this runner"}],
        "gate_authority": {"gate": "gate_wadsworth_collapse", "verdict": gate},
        "method": "collapse Table 1 onto the percolation k*(phi_p, s_p) * phi_p^B form; the pass band is "
                  "the authoritative gate_wadsworth_collapse verdict",
        "fidelity_ceiling": "source-curve reproduction of the authors' own Table 1; untamped regime",
        "assumptions": ["percolation permeability closure"],
        "caveat": "this is the component's native permeability-collapse reference, not the common scenario",
    }


def _first_crossing_time(t, w, threshold: float):
    """First time the weight strictly crosses `threshold`, or None if it never does (NO first drip — never
    a spurious argmax-of-all-False at t[0])."""
    import numpy as np
    above = np.flatnonzero(np.asarray(w) > threshold)
    return float(np.asarray(t)[above[0]]) if above.size else None


def _load_data_fixture(filename: str) -> dict:
    """Load a packaged data fixture (module-level so tests can substitute one)."""
    import os
    data_dir = os.path.join(os.path.dirname(__import__("puckworks").__file__), "data")
    with open(os.path.join(data_dir, filename)) as fh:
        return json.load(fh)


def _run_foster_infiltration() -> dict:
    from puckworks.models.foster2025 import infiltration as inf
    d = _load_data_fixture("de1_fixtureA.json")
    import numpy as np
    t = np.array(d["elapsed_s"]); P = np.array(d["pressure_bar"]); w = np.array(d["weight_g"])
    # the 0.5 g first-drip threshold is the gate's; detect the crossing explicitly (no false crossing)
    _DRIP_G = 0.5
    t_drip = _first_crossing_time(t, w, _DRIP_G)
    k, L = inf.k_from_kappa(d["grind_setting_assumed"], d["dose_g"] / 1000, d["kappa_fitted"])
    ts = {phiT: inf.front_from_pressure(t, P, k, phiT, L)["t_saturate"] for phiT in (0.173, 0.322)}
    lo, hi = ts[0.173], ts[0.322]
    gate = _gate("gate_infiltration_triangle")        # the bracket verdict lives in the gate
    drip_out = ({"name": "observed_first_drip_s", "value": _num(t_drip), "unit": "s", "role": "measured",
                 "status": "available"}
                if t_drip is not None else
                {"name": "observed_first_drip_s", "value": None, "unit": "s", "role": "measured",
                 "status": "unavailable",
                 "note": f"weight never crosses {_DRIP_G} g in this fixture; no first drip (not zero)"})
    within = (bool(lo is not None and t_drip is not None and lo < t_drip < hi)
              if t_drip is not None else None)
    return {
        "native_inputs": [
            {"name": "de1_fixtureA_pressure_trace", "value": f"{len(t)} samples", "unit": "s; bar; g",
             "provenance": "DE1 fixture A (recorded pressure/weight); k from fitted kappa"}],
        "outputs": [
            drip_out,
            {"name": "predicted_first_drip_bracket_s",
             "value": [None if lo is None else _num(lo), None if hi is None else _num(hi)],
             "unit": "s", "role": "predicted"},
            {"name": "observation_within_bracket_gate", "value": bool(gate["passed"]), "unit": "boolean",
             "role": "derived",
             "note": "authoritative bracket verdict is gate_infiltration_triangle"},
            {"name": "observation_within_bracket_runner", "value": within, "unit": "boolean",
             "role": "derived",
             "note": "None when there is no observed first drip; never plotted as zero"}],
        "gate_authority": {"gate": "gate_infiltration_triangle", "verdict": gate},
        "method": "parameter-free wetting-front saturation time from the recorded pressure at two "
                  "porosities; the observed first drip is an explicit threshold crossing (or unavailable)",
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
            "evidence": _evidence(component_id)}
    try:
        out = fn()
        result = {**base, "status": "executed", **out}
        _validate_result_schema(result)                # sanitized + finite before we publish it
    except Exception as exc:                            # isolate failure (producer OR schema violation)
        return {**base, "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"}
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

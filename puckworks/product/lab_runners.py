"""Native reference runners for the Guided Pull Laboratory (PV-19B, #70).

A native reference runner executes a registered component's OWN provenance-bound reference case (the
same authoritative callables the validation gates use), for registry visibility — NOT a prediction of
the common Guided Pull shot. Every runner **reuses an existing producer**; none re-derives an equation.
Each result carries native inputs (with units + provenance), outputs (with units + roles), the
component's registry evidence (never upgraded), a fidelity ceiling, and a scientific-payload hash.
Failures are isolated: one runner erroring never erases the others.
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
    rights_state: str = "clear"


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


# ── the runners (each calls the component's authoritative reference callables) ──────
def _run_waszkiewicz_static() -> dict:
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    P, Q = wz.steady_state_curve()
    (P_c, Q_c), _ = wz.fit_static(P, Q)
    P_pub, Q_pub = wz.published_calibration()
    return {
        "native_inputs": [
            {"name": "equilibrium_curve", "value": f"{len(P)} basket-pressure points",
             "unit": "bar; g/s", "provenance": "waszkiewicz2025 static calibration (Zenodo, CC-BY)"}],
        "outputs": [
            {"name": "refit_P_c", "value": _num(P_c), "unit": "bar", "role": "fitted"},
            {"name": "refit_Q_c", "value": _num(Q_c), "unit": "g/s", "role": "fitted"},
            {"name": "published_P_c", "value": _num(P_pub), "unit": "bar", "role": "reference"},
            {"name": "published_Q_c", "value": _num(Q_pub), "unit": "g/s", "role": "reference"},
            {"name": "P_c_matches_published", "value": bool(abs(P_c - P_pub) < 0.05), "unit": "boolean",
             "role": "derived"}],
        "method": "refit Eq.16 to the published 11-point equilibrium curve; compare to published (P_c,Q_c)",
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
    return {
        "native_inputs": [
            {"name": "table1", "value": f"{len(rows)} measured (k, phi_p, s_p) rows", "unit": "m^2; -; -",
             "provenance": "wadsworth2026 Table 1 (measured permeability + packing)"}],
        "outputs": [
            {"name": "percolation_collapse_gm_ratio", "value": _num(gm), "unit": "ratio",
             "role": "reference"},
            {"name": "collapse_within_band", "value": bool(0.7 < gm < 1.2), "unit": "boolean",
             "role": "derived"}],
        "method": "collapse Table 1 onto the percolation k*(phi_p, s_p) * phi_p^B form; geometric-mean ratio",
        "fidelity_ceiling": "source-curve reproduction of the authors' own Table 1; untamped regime",
        "assumptions": ["percolation permeability closure"],
        "caveat": "this is the component's native permeability-collapse reference, not the common scenario",
    }


def _run_foster_infiltration() -> dict:
    import json as _json
    import os

    import numpy as np
    from puckworks.models.foster2025 import infiltration as inf
    data_dir = os.path.join(os.path.dirname(__import__("puckworks").__file__), "data")
    d = _json.load(open(os.path.join(data_dir, "de1_fixtureA.json")))
    t = np.array(d["elapsed_s"]); P = np.array(d["pressure_bar"]); w = np.array(d["weight_g"])
    t_drip = float(t[np.argmax(w > 0.5)])
    k, L = inf.k_from_kappa(d["grind_setting_assumed"], d["dose_g"] / 1000, d["kappa_fitted"])
    ts = {phiT: inf.front_from_pressure(t, P, k, phiT, L)["t_saturate"] for phiT in (0.173, 0.322)}
    lo, hi = ts[0.173], ts[0.322]
    return {
        "native_inputs": [
            {"name": "de1_fixtureA_pressure_trace", "value": f"{len(t)} samples", "unit": "s; bar; g",
             "provenance": "DE1 fixture A (recorded pressure/weight); k from fitted kappa"}],
        "outputs": [
            {"name": "observed_first_drip_s", "value": _num(t_drip), "unit": "s", "role": "measured"},
            {"name": "predicted_first_drip_bracket_s",
             "value": [None if lo is None else _num(lo), None if hi is None else _num(hi)],
             "unit": "s", "role": "predicted"},
            {"name": "observation_within_bracket",
             "value": bool(lo is not None and lo < t_drip < hi), "unit": "boolean", "role": "derived"}],
        "method": "parameter-free wetting-front saturation time from the recorded pressure at two "
                  "porosities; bracket the observed first drip",
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


def has_runner(component_id: str) -> bool:
    return component_id in RUNNERS


def _sci_hash(result: dict) -> str:
    payload = {k: v for k, v in result.items() if k != "scientific_payload_hash"}
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def execute_runner(component_id: str) -> dict:
    """Execute one native reference runner. Never raises: a failure becomes a FAILED result so other
    runners still report."""
    spec, fn = RUNNERS[component_id]
    base = {"component_id": component_id, "runner_id": spec.runner_id, "runner_version": spec.version,
            "runtime_class": spec.runtime_class, "rights_state": spec.rights_state,
            "label": "This is the component's native reference case, not the common Guided Pull scenario.",
            "evidence": _evidence(component_id)}
    try:
        out = fn()
    except Exception as exc:                              # isolate failure
        return {**base, "status": "FAILED", "error": f"{type(exc).__name__}: {exc}"}
    result = {**base, "status": "executed", **out}
    result["scientific_payload_hash"] = _sci_hash(result)
    return result


def run_selected(component_ids) -> list:
    """Execute the requested runners (deterministic ordering; per-runner failure isolation)."""
    ids = [c for c in component_ids if c in RUNNERS]
    return [execute_runner(c) for c in sorted(set(ids))]

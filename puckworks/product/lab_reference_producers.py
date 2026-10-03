"""Single-source reference-summary producers for the Lab native runners (PV-19B Phase 4, #70).

Each function calls a component's authoritative model callables ONCE and returns a full-precision summary
(native inputs with units + provenance, raw producer-precision outputs, the intermediate quantities the
gate needs, threshold/config metadata). The native runner serializes this summary and surfaces the
gate's verdict; it does NOT re-derive the fitted quantity, collapse statistic, first-drip threshold, or
bracket independently. Producer precision is preserved here — display rounding happens only in the
Markdown/Streamlit/plot layers, never before canonical hashing.
"""
from __future__ import annotations

import json
import os


def _data_fixture(filename: str) -> dict:
    data_dir = os.path.join(os.path.dirname(__import__("puckworks").__file__), "data")
    with open(os.path.join(data_dir, filename)) as fh:
        return json.load(fh)


def waszkiewicz_static_summary() -> dict:
    """Static poroelastic refit summary (full precision). Consumed by the runner; the gate applies its
    own tolerances to the same (P_c, Q_c) recovery."""
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    P, Q = wz.steady_state_curve()
    (P_c, Q_c), _ = wz.fit_static(P, Q)
    P_pub, Q_pub = wz.published_calibration()
    return {
        "native_inputs": [
            {"name": "equilibrium_curve", "value": f"{len(P)} basket-pressure points",
             "unit": "bar; g/s", "provenance": "waszkiewicz2025 static calibration (Zenodo, CC-BY)"}],
        "values": {"refit_P_c": float(P_c), "refit_Q_c": float(Q_c),
                   "published_P_c": float(P_pub), "published_Q_c": float(Q_pub)},
        "gate": "gate_waszkiewicz_static_refit",
        "method": "refit Eq.16 to the published 11-point equilibrium curve; recover (P_c, Q_c)",
    }


def wadsworth_collapse_summary() -> dict:
    """Percolation-collapse summary (full precision geometric-mean ratio)."""
    import numpy as np
    from puckworks.models.wadsworth2026 import permeability as wp
    rows = wp.table1()
    ratios = [r["k_m2"] / wp.k_star(r["phi_p"], r["s_p"]) / r["phi_p"] ** wp.B_PERC for r in rows]
    gm = float(np.exp(np.mean(np.log(ratios))))
    return {
        "native_inputs": [
            {"name": "table1", "value": f"{len(rows)} measured (k, phi_p, s_p) rows", "unit": "m^2; -; -",
             "provenance": "wadsworth2026 Table 1 (measured permeability + packing)"}],
        "values": {"percolation_collapse_gm_ratio": gm, "n_rows": len(rows)},
        "gate": "gate_wadsworth_collapse",
        "method": "collapse Table 1 onto k*(phi_p, s_p) * phi_p^B; geometric-mean ratio",
    }


def foster_first_drip_summary() -> dict:
    """First-drip bracket summary. The threshold is the SINGLE authoritative model constant
    (foster.FIRST_DRIP_THRESHOLD_G); the observed drip is an explicit crossing (or None), never a false
    argmax-of-all-False at t[0]."""
    import numpy as np
    from puckworks.models.foster2025 import infiltration as inf
    d = _data_fixture("de1_fixtureA.json")
    t = np.array(d["elapsed_s"]); P = np.array(d["pressure_bar"]); w = np.array(d["weight_g"])
    t_drip = inf.observed_first_drip_s(t, w)             # shared constant + explicit crossing
    k, L = inf.k_from_kappa(d["grind_setting_assumed"], d["dose_g"] / 1000, d["kappa_fitted"])
    ts = {phiT: inf.front_from_pressure(t, P, k, phiT, L)["t_saturate"] for phiT in (0.173, 0.322)}
    lo, hi = ts[0.173], ts[0.322]
    within = (bool(lo is not None and t_drip is not None and lo < t_drip < hi)
              if t_drip is not None else None)
    return {
        "native_inputs": [
            {"name": "de1_fixtureA_pressure_trace", "value": f"{len(t)} samples", "unit": "s; bar; g",
             "provenance": "DE1 fixture A (recorded pressure/weight); k from fitted kappa"}],
        "values": {"observed_first_drip_s": t_drip,
                   "predicted_bracket_lo_s": None if lo is None else float(lo),
                   "predicted_bracket_hi_s": None if hi is None else float(hi),
                   "observation_within_bracket": within},
        "threshold": {"first_drip_threshold_g": inf.FIRST_DRIP_THRESHOLD_G},
        "gate": "gate_infiltration_triangle",
        "method": "parameter-free wetting-front saturation time at two porosities; observed first drip "
                  "is an explicit threshold crossing (or unavailable)",
    }


def lb_reference_channel_summary() -> dict:
    """Plane-channel LB code-verification summary (full precision). The component solves its OWN canonical
    synthetic channel once (no third-party dataset) and reports the simulated lattice permeability against
    the exact plane-Poiseuille reference k = h^2/12. The gate (gate_lb_channel) independently owns the
    acceptance band; this producer never re-derives that threshold. Deterministic."""
    from puckworks.models.brewer2026 import lb_reference as lb
    case = dict(lb.CHANNEL_VERIFICATION_CASE)
    v = lb.channel_verification(**case)                  # canonical shared computation (no threshold here)
    fluid_nodes = case["Nz"] - 2                          # resolved fluid width between the two bounce-back walls
    return {
        "native_inputs": [
            {"name": "lattice_dimensions", "value": f"{case['N']}x{case['N']}x{case['Nz']}",
             "unit": "lattice nodes", "provenance": "synthetic plane channel constructed in code; no dataset"},
            {"name": "resolved_fluid_node_count", "value": fluid_nodes, "unit": "lattice nodes",
             "provenance": "channel width between the two full-way bounce-back walls"},
            {"name": "body_force_g", "value": case["g"], "unit": "lattice units",
             "provenance": "constant body force in +x (documented lattice units)"},
            {"name": "relaxation_tau_plus", "value": case["tau_plus"], "unit": "dimensionless",
             "provenance": "TRT symmetric relaxation time (magic Lambda = 3/16 fixes the wall location)"},
            {"name": "max_iterations", "value": case["max_steps"], "unit": "iterations",
             "provenance": "solver iteration ceiling"},
            {"name": "convergence_check_interval", "value": case["check"], "unit": "iterations",
             "provenance": "steps between Darcy-velocity convergence checks"},
            {"name": "convergence_tolerance", "value": case["rtol"], "unit": "dimensionless",
             "provenance": "relative Darcy-velocity convergence tolerance"}],
        "values": {"k_meas": v["k_meas"], "k_exact": v["k_exact"], "err_pct": v["err_pct"],
                   "converged": v["converged"], "steps": v["steps"], "max_steps": v["max_steps"]},
        "gate": "gate_lb_channel",
        "case": case,
        "method": "solve the canonical synthetic plane channel once; compare the lattice permeability to "
                  "the exact plane-Poiseuille k = h^2/12; the pass/fail band is the authoritative gate",
    }


SUMMARIES: dict = {
    "waszkiewicz2025.poroelastic": waszkiewicz_static_summary,
    "wadsworth2026.permeability": wadsworth_collapse_summary,
    "foster2025.infiltration": foster_first_drip_summary,
    "brewer2026.lb_reference": lb_reference_channel_summary,
}


def grudeva2026_reference_summary(*, controls=None, parameters=None) -> dict:
    """One native EJAM producer, guarded before any calculation or fixture access."""
    from puckworks import rights
    cid = "grudeva2026.reduced"
    decisions = [rights.may_execute_locally(cid), rights.may_publish_outputs(cid),
                 rights.may_include_data_in_release(cid)]
    if any(not decision.allowed for decision in decisions):
        raise PermissionError("Grudeva EJAM source/use preflight did not clear this producer")
    from puckworks.models.grudeva2026 import Controls, Parameters, simulate
    from puckworks.models.grudeva2026.verification import (
        publication_comparison, quick_verification, reference_fixture, reference_times)
    p = Parameters() if parameters is None else parameters
    c = Controls() if controls is None else controls
    fixture = reference_fixture("publication_reference.json")
    z = sorted(set([i/100 for i in range(101)]+[row['z'] for row in fixture['figure3']]))
    result = simulate(p, c, times=reference_times(), profile_z=z)
    comparisons = publication_comparison(result) if p == Parameters() else {
        "status": "NOT_APPLICABLE_SYNTHETIC_PARAMETERS", "physical_validation": "NOT_ESTABLISHED"}
    return {
        "native_inputs": [
            {"name": "publication_case", "value": result.parameters, "unit": "dimensionless",
             "provenance": "EJAM Eqs.21,29,67-77; Eq.76 fractions; Table 2 initial concentrations "
                           "1.388 (not 310/224); Q_i recomputed from fractions; DOI 10.1017/S095679252500018X"},
            {"name": "prescribed_flow", "value": 1., "unit": "dimensionless Darcy flux",
             "provenance": "Eq.29, fixed flow; no hydraulic prediction"},
            {"name": "numerical_controls", "value": result.controls, "unit": "dimensionless",
             "provenance": "MODEL-GRUDEVA2026-REDUCED-001 explicit numerical controls"}],
        "values": {"first_drip": result.events.get("first_drip"),
                   "desaturation_exit": result.events.get("desaturation_exit"),
                   "saturation_plateau_duration": result.events.get("saturation_plateau_duration"),
                   "final_discharged_solute": result.cumulative_discharged_solute[-1]
                   if result.cumulative_discharged_solute else None},
        "scientific_result": result.to_dict(), "reference_qualification": comparisons,
        "gate": "gate_grudeva2026_reduced", "gate_verdict": quick_verification(),
        "source_preflight": [decision.to_dict() for decision in decisions],
        "method": "Independent equation-based conservative fixed-flow reduced model; native publication case. "
                  "NOT A COMMON-SCENARIO PREDICTION / NOT EXPERIMENTAL VALIDATION",
    }

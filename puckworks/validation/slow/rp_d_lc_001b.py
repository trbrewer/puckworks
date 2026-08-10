"""RP-D-LC-001b — slow driver SCAFFOLD.

NO LATTICE-BOLTZMANN SOLVE HAS BEEN PERFORMED FOR THIS TRANCHE, AND THIS MODULE REFUSES TO
PERFORM ONE. Authorisation is PHASE-SPECIFIC (erratum PE-11): ``AUTHORISED_SOLVING_PHASES`` is
empty at this head, so every solving phase raises ``ExecutionNotAuthorised``. Authorising the
pre-freeze phases cannot authorise P3 or P4; each addition is its own reviewed source commit,
and the resulting exact head is the object reviewed for execution.

Independently of that allowlist, P3 and P4 refuse without the reviewed bridge freeze AND the
reviewed instantiated P3/P4 matrix, and every phase refuses without valid completion manifests
for its predecessors — both checked BEFORE the allowlist, so neither gate is shadowed by it.

What IS implemented here is everything that can be checked without a solver: the per-case
record construction from already-computed fields, the phase ordering, the freeze gate and the
execution-authority record. Heavy execution never enters normal CI (CLAUDE.md rule 3).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib

import numpy as np

from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

#: The PHASE-SPECIFIC reviewed allowlist (erratum PE-11). Superseded: one module-level
#: EXECUTION_AUTHORISED boolean, which would have authorised the primary experiment and Arm J in
#: the same act as the pre-freeze phases.
#:
#: It is deliberately a source-level constant rather than a flag or an environment variable:
#: adding a phase must be a reviewable change to the repository, and the resulting exact head is
#: the object reviewed for execution. Authorising P0/P1a/P1b/P2a does NOT authorise P3 or P4, and
#: P3 stays hard-refused even when a syntactically valid freeze exists.
AUTHORISED_SOLVING_PHASES = ()

AUTHORISATION_NOTE = (
    "RP-D-LC-001b is PRE-EXECUTION. The protocol, the corrected fixture, the conserved-quantity "
    "contract, the similarity law, the negative-control gate and the reachable-set margin are "
    "frozen and awaiting substantive scientific review at an exact head. No solve may run before "
    "that review, and each phase must be added to AUTHORISED_SOLVING_PHASES by its own reviewed "
    "source commit."
)

#: Every mode that would invoke the solver, in the only order they may run.
SOLVING_MODES = ("P0", "P1a", "P1b", "P2a", "P3", "P4")
#: Modes that do no solving at all.
NON_SOLVING_MODES = ("P2b", "freeze", "assemble", "plan")
MODES = SOLVING_MODES + NON_SOLVING_MODES

#: Phases whose start additionally requires the reviewed freeze AND instantiated matrix.
FREEZE_GATED_MODES = vf.FREEZE_GATED_PHASES

#: The macroscopic fields the eventual solve must request. ``rho`` is needed for BOTH the
#: pressure normalisation and the density-weighted mass flux; ``uy`` for the transverse bridge
#: flux; ``uz`` for the FULL three-component low-Mach control (erratum PE-4) — uz is not assumed
#: to vanish from nominal symmetry. No solver change is required: all three are already in
#: lb_reference.EXPORTABLE_FIELDS, and ux is returned unconditionally.
REQUIRED_FIELDS = ("rho", "uy", "uz")


class ExecutionNotAuthorised(RuntimeError):
    """Raised by every solving mode while the tranche is pre-execution."""


def _refuse(phase):
    raise ExecutionNotAuthorised(
        "phase %r would run an RP-D-LC-001b lattice-Boltzmann solve, which is NOT AUTHORISED: "
        "AUTHORISED_SOLVING_PHASES = %r. %s" % (phase, AUTHORISED_SOLVING_PHASES,
                                                AUTHORISATION_NOTE))


def require_execution_authorisation(phase, backend="reference", runs_dir=None):
    """The complete fail-closed runtime gate (erratum PE-11), in the order a reviewer would
    check it:

      1. the phase is on the reviewed source-controlled allowlist;
      2. the freeze AND the instantiated P3/P4 matrix exist and match, for freeze-gated phases;
      3. every predecessor phase has a completion manifest bound to THIS configuration;
      4. the execution authority itself resolves — clean tree, real git identity, exact
         protocol/config/matrix hashes, complete non-null input-file hashes, supported backend,
         exact solver configuration.

    Steps 2 and 3 run BEFORE step 1 so the freeze and manifest gates are demonstrably
    load-bearing rather than shadowed by the allowlist.
    """
    if phase not in vf.PHASE_PREREQUISITES:
        raise ValueError("unknown phase %r" % (phase,))
    if phase in FREEZE_GATED_MODES:
        vf.require_freeze(phase)
    vf.require_phase_manifests(phase, runs_dir=runs_dir)
    if phase not in AUTHORISED_SOLVING_PHASES:
        _refuse(phase)
    return vf.execution_authority(phase, backend=backend)         # pragma: no cover - unreached


def solve(mask, g, phase, backend="reference", tau=None, fields=REQUIRED_FIELDS, steps=None,
          min_steps=None, **kw):
    """The single solver call site. It refuses unless its phase is on the reviewed allowlist, so
    no code path in this module can reach the kernel by accident."""
    if phase not in AUTHORISED_SOLVING_PHASES:
        _refuse(phase)
    if backend not in vf.SUPPORTED_BACKENDS:                      # pragma: no cover - unreached
        raise ExecutionNotAuthorised("backend %r is not supported" % (backend,))
    from puckworks.models.brewer2026 import lb_reference          # pragma: no cover - unreached
    return lb_reference.solve(                                    # pragma: no cover - unreached
        mask, g=g, tau_plus=(vf.TAU_PLUS if tau is None else tau),
        max_steps=(vf.MAX_STEPS if steps is None else steps), check=vf.CHECK, rtol=vf.RTOL,
        min_steps=(vf.MIN_STEPS if min_steps is None else min_steps),
        verbose=False, return_fields=tuple(fields), **kw)


# ------------------------------------------------------------------------------------------
# Record construction — pure, solver-free, and therefore testable in CI with synthetic fields.
# ------------------------------------------------------------------------------------------

#: The named measurement planes, in frozen order. These are REPORTED and feed the observables;
#: they are never admitted to the adjudicative conservation set (erratum PE-1).
NAMED_AXIAL_PLANES = ("x_node_in", "x_meas_in", "x_meas_b", "x_meas_a", "x_node_out")


def named_axial_records(res, mask, meta, g):
    """The named measurement records: node planes (kept for PRESSURE) and the two outlet-flux
    planes (kept for the observables). Reported separately from the conservation set."""
    ux, rho = res["ux"], res["rho"]
    return [vf.axial_plane_record(pid, meta[pid], ux, rho, mask, g)
            for pid in NAMED_AXIAL_PLANES]


def conservation_axial_records(res, mask, meta, g):
    """Exactly the nine adjudicative axial conservation records, in frozen order."""
    ux, rho = res["ux"], res["rho"]
    recs = [vf.axial_plane_record("cons_%d" % i, x, ux, rho, mask, g)
            for i, x in enumerate(meta["axial_conservation_planes"])]
    return vf.assert_conservation_records(recs)


def lane_records(res, mask, meta, g):
    """Per-lane records at the two frozen outlet planes — the volume fluxes the inverse uses,
    each accompanied by its mass-flux counterpart."""
    ux, rho = res["ux"], res["rho"]
    out = []
    for pid, x in (("x_meas_a", meta["x_meas_a"]), ("x_meas_b", meta["x_meas_b"])):
        for lane, key in ((1, "lane1_y"), (2, "lane2_y")):
            out.append(vf.axial_plane_record("%s_lane%d" % (pid, lane), x, ux, rho, mask, g,
                                             y_slice=meta[key]))
    return out


#: The four frozen transverse bridge-control planes, in frozen order: entry port, both duct
#: planes, exit port. On a BLOCKED candidate the two duct planes are structurally solid and their
#: records carry n_fluid = 0 — which is exactly what the blocked-state check asserts.
TRANSVERSE_PLANES = ("y_portA_in", "y_duct_a", "y_duct_b", "y_portB_out")


def transverse_records(res, mask, meta):
    """The four frozen transverse bridge-control planes. Empty for a fixture with no bridge."""
    if meta["bridge"] is None:
        return []
    uy, rho = res["uy"], res["rho"]
    fx, fz = meta["bridge_x"], meta["bridge_z"]
    return [vf.transverse_plane_record(pid, meta[pid], uy, rho, mask, fx, fz)
            for pid in TRANSVERSE_PLANES]


def pressure_face_records(res, mask, meta, g):
    """The two frozen lateral pressure faces over the exact bridge footprint (erratum PE-15).
    Empty for a fixture with no bridge."""
    if meta["bridge"] is None:
        return []
    fx, fz = meta["bridge_x"], meta["bridge_z"]
    return [vf.pressure_face_record(pid, meta[pid], res["rho"], mask, g, fx, fz)
            for pid in vf.PRESSURE_FACE_IDS]


def case_record(res, mask, meta, g, stage, lateral_driver_is_zero=None):
    """The complete compact record for one solved case. Large field arrays are NEVER retained;
    only the frozen plane records and scalars are.

    ``lateral_driver_is_zero`` defaults to the identical-path variant, for which the
    cross-product gap X vanishes EXACTLY and no lateral pressure difference exists at any bridge
    conductance — the case the zero-safe transverse metric exists for (erratum PE-2).
    """
    missing = [f for f in ("ux", "rho") + REQUIRED_FIELDS if f not in res]
    if missing:
        raise ValueError(
            "case_record fails closed: the solve result is missing %r. Every case must request "
            "return_fields=%r so the density-weighted mass flux and the FULL three-component "
            "low-Mach control can be formed (errata PE-1, PE-4)." % (missing, REQUIRED_FIELDS))
    named = named_axial_records(res, mask, meta, g)
    cons = conservation_axial_records(res, mask, meta, g)
    ln = lane_records(res, mask, meta, g)
    tr = transverse_records(res, mask, meta)
    by = {r["plane_id"]: r for r in named + ln}
    if lateral_driver_is_zero is None:
        # The geometry supplies only the EXPECTATION; the measured gap must confirm it (PE-15).
        lateral_driver_is_zero = (meta["variant"] == "identical")
    axial_mass_scale = by["x_meas_a"]["sum_rho_ux"]
    dP = by["x_node_in"]["p_mean"] - by["x_node_out"]["p_mean"]
    faces = pressure_face_records(res, mask, meta, g)
    lateral = None
    if faces:
        q_lat_mass = None
        for r in tr:
            if r["plane_id"] == "y_duct_a":
                q_lat_mass = r["sum_rho_uy"]
        delta = vf.lateral_pressure_delta_record(res["rho"], mask, meta, g)
        lateral = vf.lateral_pressure_gap(faces, delta, dP, g, q_lat_mass=q_lat_mass,
                                          expected_zero_driver=bool(lateral_driver_is_zero))
    rec = {
        "stage": stage, "S": meta["S"], "g": float(g), "state": meta["state"],
        "variant": meta["variant"], "swapped": meta["swapped"],
        "perturbation": meta["perturbation"], "bridge": meta["bridge"],
        "mask_sha256": meta["mask_sha256"],
        "steps": int(res["steps"]), "converged": bool(res["steps"] < vf.MAX_STEPS),
        "named_axial_planes": named, "conservation_planes": cons,
        "lane_planes": ln, "transverse_planes": tr, "pressure_faces": faces,
        "conservation": vf.conservation_residuals(cons, named_plane_records=named + ln),
        "transverse_conservation": vf.transverse_conservation(
            meta["state"], tr, axial_mass_scale,
            lateral_driver_is_zero=bool(lateral_driver_is_zero)),
        "lateral_pressure": lateral,
        "mach": vf.mach_record(res["ux"], res["uy"], res["uz"], mask),
        # the inverse's observables, formed from VOLUME flux only, kept explicitly labelled
        "Q_volume": by["x_meas_a"]["sum_ux"],
        "q1_volume": by["x_meas_a_lane1"]["sum_ux"],
        "q2_volume": by["x_meas_a_lane2"]["sum_ux"],
        "Q_mass_diagnostic": axial_mass_scale,
        "dP": dP,
        "p_node_in_sd": by["x_node_in"]["p_sd"], "p_node_out_sd": by["x_node_out"]["p_sd"],
    }
    return rec


def boundary_record(open_rec, blocked_rec, orientation="nominal"):
    """Assemble the SIX boundary numbers, and only those. Every other key in the case records —
    mass flux, transverse flux, internal pressures, geometry — is excluded by construction, and
    the result is validated against the frozen allowlist before it can reach the inverse."""
    rec = {
        "Q0": blocked_rec["Q_volume"], "dP0": blocked_rec["dP"],
        "q1": open_rec["q1_volume"], "q2": open_rec["q2_volume"], "dP": open_rec["dP"],
        "orientation": orientation,
        "converged": bool(open_rec["converged"] and blocked_rec["converged"]),
    }
    return vf.assert_boundary_record(rec)


# ------------------------------------------------------------------------------------------
# Phase entry points — all refuse.
# ------------------------------------------------------------------------------------------

# ------------------------------------------------------------------------------------------
# The pre-freeze EXECUTOR (erratum PE-19). Real, deterministic, and unreachable at this head
# because AUTHORISED_SOLVING_PHASES is empty.
# ------------------------------------------------------------------------------------------

def resolve_row(row):
    """Resolve one matrix row to EXACTLY ONE fixture or coupon. Raises if a row is ambiguous."""
    kind, S = row["kind"], row["S"]
    if kind == "axial_coupon":
        mask, meta = vf.build_axial_coupon(S, row["coupon_level"], row["coupon_orientation"])
        return mask, meta, "coupon"
    if kind == "bridge_coupon":
        b = row["bridge"]
        mask, meta = vf.build_bridge_coupon(S, b["w"], b["kz"])
        return mask, meta, "coupon"
    variant = row["variant"] if row["variant"] in ("mirror", "identical") else "mirror"
    bridge = row["bridge"] if isinstance(row["bridge"], dict) else None
    if kind == "reference_blocked_ladder" or kind == "tau_cross_check":
        bridge = None
    mask, meta = vf.build_fixture(S, bridge=bridge, connected=(row["state"] == "open"),
                                  variant=variant, swapped=bool(row["swapped"]),
                                  perturbation=row["perturbation"])
    return mask, meta, "fixture"


def _coupon_scientific(res, mask, meta, g, row):
    """Compact record for a duct coupon: in a uniform x-periodic duct the pressure drop is g*L
    exactly, so the conductance needs no density field. The density-based value is retained
    alongside so the two can be compared, exactly as 001 did."""
    ux = res["ux"]
    n = mask.shape[0] // 2
    Q = float(np.where(mask[n], 0.0, ux[n]).sum())
    L = float(meta["length_vox"])
    G = Q / (g * L)
    out = {"kind": meta["kind"], "Q_volume": Q, "length_vox": L, "conductance": G,
           "mask_sha256": meta["mask_sha256"],
           "mach": vf.mach_record(res["ux"], res["uy"], res["uz"], mask)}
    if meta["kind"] == "bridge_coupon":
        out["G_bridge_coupon"] = G
    else:
        out["level"] = meta["level"]
        out["orientation"] = meta["orientation"]
    return out


def _fixture_scientific(res, mask, meta, g, row):
    """Compact record for a fixture case: the frozen plane records and every derived scalar the
    assembler will RECOMPUTE from — no large fields."""
    rec = case_record(res, mask, meta, g, stage=row["phase"])
    named = {r["plane_id"]: r for r in rec["named_axial_planes"]}
    lanes = {r["plane_id"]: r for r in rec["lane_planes"]}
    sci = {
        "named_axial_planes": rec["named_axial_planes"],
        "conservation_planes": rec["conservation_planes"],
        "lane_planes": rec["lane_planes"],
        "transverse_planes": rec["transverse_planes"],
        "pressure_faces": rec["pressure_faces"],
        "conservation": rec["conservation"],
        "transverse_conservation": rec["transverse_conservation"],
        "lateral_pressure": rec["lateral_pressure"],
        "mach": rec["mach"],
        "Q_volume": rec["Q_volume"], "Q_mass_diagnostic": rec["Q_mass_diagnostic"],
        "q1_volume": rec["q1_volume"], "q2_volume": rec["q2_volume"],
        "dP": rec["dP"],
        "p_node_in": named["x_node_in"]["p_mean"], "p_node_out": named["x_node_out"]["p_mean"],
        "p_node_in_sd": rec["p_node_in_sd"], "p_node_out_sd": rec["p_node_out_sd"],
        "s_outlet_share_a": rec["q1_volume"] / (rec["q1_volume"] + rec["q2_volume"]),
        "s_outlet_share_b": (lanes["x_meas_b_lane1"]["sum_ux"]
                             / (lanes["x_meas_b_lane1"]["sum_ux"]
                                + lanes["x_meas_b_lane2"]["sum_ux"])),
    }
    lp = rec["lateral_pressure"]
    if lp:
        sci["p_face1"] = lp["p_face1"]
        sci["p_face2"] = lp["p_face2"]
        sci["delta_p_lateral_over_g"] = lp["delta_p_lateral_over_g"]
        sci["q_lat_mass_over_g"] = lp["q_lat_mass_over_g"]
    return sci


def _decision_bearing_ok(row, sci, status):
    """Stop conditions for one case. An UNCONVERGED normal case stops the phase and may never be
    rescued by an audit (erratum PE-16)."""
    if status == "NORMAL_UNCONVERGED":
        return False, "NORMAL_UNCONVERGED"
    if status == "FIXED_STEP_AUDIT_INCOMPLETE":
        return False, "FIXED_STEP_AUDIT_INCOMPLETE"
    mach = sci.get("mach") or {}
    if mach and not mach.get("pass"):
        return False, "LOW_MACH_FAILED"
    cons = sci.get("conservation")
    if cons and not cons.get("mass_conservation_pass"):
        return False, "MASS_CONSERVATION_FAILED"
    tc = sci.get("transverse_conservation")
    if tc and tc.get("pass") is False:
        return False, "TRANSVERSE_CONTROL_FAILED"
    lp = sci.get("lateral_pressure")
    if lp and lp.get("measured_zero_driver_pass") is False:
        return False, "MEASURED_LATERAL_DRIVER_NONZERO"
    return True, None


def execute_phase(phase, runs_dir, result_provider=None, backend="reference", authority=None):
    """The deterministic pre-freeze executor for P0/P1a/P1b/P2a, and arithmetic-only P2b.

    ``result_provider`` exists solely so a unit test can inject a fake solver. It is a Python
    keyword argument and is NOT reachable from the CLI: the user-facing path always resolves to
    the single guarded call site, which refuses unless the phase is on the reviewed allowlist.
    """
    if phase not in vf.PHASE_PREREQUISITES:
        raise ValueError("unknown phase %r" % (phase,))
    base = pathlib.Path(runs_dir)

    # 1-4: authorization, authority, predecessor manifests -- all fail closed, in that order.
    require_execution_authorisation(phase, backend=backend, runs_dir=base)
    auth = authority or vf.execution_authority(phase, backend=backend)   # pragma: no cover
    manifests, records = ({}, {})                                        # pragma: no cover
    if vf.PHASE_PREREQUISITES[phase]:                                    # pragma: no cover
        manifests, records = vf.require_phase_manifests(phase, runs_dir=base, authority=auth)
    if phase == "P2b":                                                   # pragma: no cover
        return vf.assemble_p2b_from_runs(base, authority=auth)           # NO solver call
    return _execute_solving_phase(phase, base, auth, manifests, records, # pragma: no cover
                                  result_provider, backend)


def _execute_solving_phase(phase, base, auth, manifests, records, result_provider, backend):
    """Steps 5-13. Factored out so a test can drive it with a fake result provider without ever
    reaching the authorization gate's refusal."""
    matrix = vf.execution_matrix()["rows"]
    expected, adaptive = vf.derive_expected_rows(phase, matrix, predecessor_records=records)
    planned = {r["case_id"] for r in expected}
    pre_sha = {k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
               for k in manifests if (base / ("manifest_%s.json" % k)).exists()}
    completed, refused, failed = [], [], []
    written = {}
    terminal, stop_reason = "PHASE_COMPLETE", None

    for row in [r for r in matrix if r["phase"] == phase]:               # matrix order, jobs=1
        if row["case_id"] not in planned:
            refused.append({"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                            "reason": "NOT_ELIGIBLE_UNDER_THE_DERIVED_ADAPTIVE_PLAN"})
            continue
        if terminal != "PHASE_COMPLETE":
            refused.append({"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                            "reason": "REFUSED_AFTER_PHASE_STOP"})
            continue
        mask, meta, kind = resolve_row(row)
        audit_plan = None
        if row["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X":
            base_rec, _ = vf.read_case_record(base, row["audit_of_case_id"])
            audit_plan = vf.fixed_step_audit_plan(base_rec["completed_steps"],
                                                  base_rec["status"])
            audit_plan["base_case_id"] = base_rec["case_id"]
            audit_plan["base_record_sha256"] = vf.record_hash(base_rec)
        provider = result_provider or _guarded_result_provider
        g = vf.row_forcing(row)
        res = provider(mask=mask, g=g, phase=phase, row=row,
                       tau=row["tau_plus"], audit=audit_plan, backend=backend)
        sci = (_coupon_scientific(res, mask, meta, g, row) if kind == "coupon"
               else _fixture_scientific(res, mask, meta, g, row))
        geometry = {"kind": kind, "mask_sha256": meta["mask_sha256"], "S": row["S"],
                    "bridge": row["bridge"] if isinstance(row["bridge"], dict) else None,
                    "state": row["state"], "variant": row["variant"]}
        rec = vf.make_case_record(row, auth, pre_sha, geometry, sci,
                                  completed_steps=int(res["steps"]),
                                  run_mode=row["run_mode"], audit=audit_plan)
        vf.validate_case_record(rec, row=row, authority=auth, phase=phase)
        path, how = vf.write_case_record(base, rec)
        written[row["case_id"]] = rec
        entry = {"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                 "record_path": path.name, "write_mode": how,
                 "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                 "status": rec["status"]}
        ok, why = _decision_bearing_ok(row, sci, rec["status"])
        if ok:
            completed.append(entry)
        else:
            entry["reason"] = why
            failed.append(entry)
            terminal = ("PHASE_STOPPED_UNCONVERGED" if why == "NORMAL_UNCONVERGED"
                        else "PHASE_STOPPED_INVALID_CASE")
            stop_reason = why

    manifest = vf.make_phase_manifest(phase, expected, completed, refused, failed, auth,
                                      pre_sha, adaptive, terminal, stop_reason)
    mpath = base / ("manifest_%s.json" % phase)
    tmp = base / (mpath.name + ".tmp")
    tmp.write_text(vf.canonical_json(manifest) + "\n")
    tmp.replace(mpath)
    vf.validate_phase_manifest(phase, base, authority=auth, matrix_rows=matrix,
                               predecessor_records=records)
    return manifest


def _guarded_result_provider(mask, g, phase, row, tau=None, audit=None, backend="reference"):
    """The ONLY production path to a solve. It refuses unless the phase is on the allowlist."""
    steps = None if audit is None else audit["target_steps"]
    return solve(mask, g, phase, backend=backend, tau=tau, steps=steps,
                 min_steps=(None if audit is None else audit["min_steps"]))


def run_phase(mode, out_dir=None, backend="reference", runs_dir=None):
    if mode not in MODES:
        raise ValueError("unknown mode %r; expected one of %r" % (mode, MODES))
    if mode == "plan":
        return vf.execution_matrix()
    if mode in SOLVING_MODES or mode == "P2b":
        rd = runs_dir if runs_dir is not None else (REPO_ROOT / vf.RUNS_REL)
        return execute_phase(mode, rd, backend=backend)      # refuses: allowlist is empty
    if mode == "freeze":
        raise ExecutionNotAuthorised(
            "the bridge freeze is DERIVED by P2b from real hashed P0/P1a/P1b/P2a records, none "
            "of which exist. %s" % AUTHORISATION_NOTE)
    raise ExecutionNotAuthorised(
        "mode %r has nothing to assemble: no RP-D-LC-001b case record exists. %s"
        % (mode, AUTHORISATION_NOTE))


def main(argv=None):                                             # pragma: no cover - thin CLI
    ap = argparse.ArgumentParser(description="RP-D-LC-001b slow driver (PRE-EXECUTION: refuses)")
    ap.add_argument("--mode", required=True, choices=list(MODES))
    ap.add_argument("--backend", default="reference")
    ap.add_argument("--output", default=None)
    ap.add_argument("--jobs", type=int, default=1)
    a = ap.parse_args(argv)
    try:
        res = run_phase(a.mode, out_dir=a.output, backend=a.backend)
    except (ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
            vf.ExecutionAuthorityError) as exc:
        print("REFUSED: %s" % exc)
        return 2
    print(json.dumps({"mode": a.mode, "n_planned_rows": res.get("n_rows")}, indent=2))
    return 0


if __name__ == "__main__":                                       # pragma: no cover
    raise SystemExit(main())

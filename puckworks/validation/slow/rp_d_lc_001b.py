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

#: The SEPARATE assembly allowlist (erratum PE-39). P2b is arithmetic and must never share the
#: solving gate: authorising P0-P2a must not authorise the assembly, and authorising the assembly
#: must not authorise P3/P4. Both are empty at this head.
AUTHORISED_ASSEMBLY_PHASES = ()

#: The only supported job count at this stage. A larger value is refused rather than ignored.
SUPPORTED_JOBS = (1,)

AUTHORISATION_NOTE = (
    "RP-D-LC-001b is PRE-EXECUTION. The protocol, the corrected fixture, the conserved-quantity "
    "contract, the similarity law, the negative-control gate and the reachable-set margin are "
    "frozen and awaiting substantive scientific review at an exact head. No solve may run before "
    "that review, and each phase must be added to AUTHORISED_SOLVING_PHASES by its own reviewed "
    "source commit."
)

#: Every mode that would invoke the solver, in the only order they may run.
SOLVING_MODES = ("P0", "P1a", "P1b", "P2a", "P3", "P4")
#: Arithmetic assembly phases — they never call the solver.
ASSEMBLY_MODES = ("P2b",)
#: Modes that do no solving at all.
NON_SOLVING_MODES = ASSEMBLY_MODES + ("plan",)
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


def require_assembly_authorisation(phase, backend="reference", runs_dir=None):
    """The assembly gate (erratum PE-39). Separate from the solving gate in both directions."""
    if phase not in ASSEMBLY_MODES:
        raise ValueError("phase %r is not an assembly phase" % (phase,))
    vf.require_phase_manifests(phase, runs_dir=runs_dir)
    if phase not in AUTHORISED_ASSEMBLY_PHASES:
        raise ExecutionNotAuthorised(
            "phase %r is an ARITHMETIC assembly phase and is NOT AUTHORISED: "
            "AUTHORISED_ASSEMBLY_PHASES = %r. Authorising the solving phases does not authorise "
            "the assembly. %s" % (phase, AUTHORISED_ASSEMBLY_PHASES, AUTHORISATION_NOTE))
    return vf.execution_authority(phase, backend=backend)         # pragma: no cover - unreached


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

KNOWN_ROW_KINDS = ("reference_blocked_ladder", "axial_coupon", "tau_cross_check",
                   "determinism_replicate", "identical_path_control",
                   "pressure_plane_diagnostic", "bridge_coupon", "candidate_blocked_mirror",
                   "primary_mirror_open", "path_swap_control", "adversarial_perturbation",
                   "fixed_step_audit", "arm_j_return_path")


def resolve_row(row):
    """Resolve one matrix row to EXACTLY ONE fixture or coupon. Raises if a row is ambiguous,
    if its kind, variant or state is unknown, or if a declared obstruction cannot be built."""
    kind, S = row["kind"], row["S"]
    if kind not in KNOWN_ROW_KINDS:
        raise ValueError("unknown row kind %r on row %r" % (kind, row["case_id"]))
    if kind == "axial_coupon":
        mask, meta = vf.build_axial_coupon(S, row["coupon_level"], row["coupon_orientation"])
        return mask, meta, "coupon"
    if kind == "bridge_coupon":
        b = row["bridge"]
        mask, meta = vf.build_bridge_coupon(S, b["w"], b["kz"])
        return mask, meta, "coupon"
    if row["variant"] not in ("mirror", "identical", "axial_coupon", "bridge_coupon"):
        raise ValueError("unknown fixture variant %r on row %r" % (row["variant"], row["case_id"]))
    if row["state"] not in vf.FIXTURE_STATES + ("coupon",):
        raise ValueError("unknown fixture state %r on row %r" % (row["state"], row["case_id"]))
    variant = row["variant"] if row["variant"] in ("mirror", "identical") else "mirror"
    bridge = row["bridge"] if isinstance(row["bridge"], dict) else None
    if kind in ("reference_blocked_ladder", "tau_cross_check"):
        bridge = None
    if bridge is None and isinstance(row["bridge"], str):
        raise ValueError("row %r still carries an UNRESOLVED placeholder bridge %r; a P3/P4 "
                         "template must be instantiated before it can be resolved"
                         % (row["case_id"], row["bridge"]))
    mask, meta = vf.build_fixture(S, bridge=bridge, connected=(row["state"] == "open"),
                                  variant=variant, swapped=bool(row["swapped"]),
                                  perturbation=row["perturbation"],
                                  obstructed=bool(row["obstructed"]))
    if row["obstructed"] and not meta.get("obstructed"):     # pragma: no cover - guarded above
        raise ValueError("row %r declares obstructed=True but the obstruction was not applied"
                         % (row["case_id"],))
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


def execute_phase(phase, runs_dir, backend="reference"):
    """The PRODUCTION pre-freeze executor (erratum PE-34).

    The signature accepts **no** result provider, **no** authority override and **no** scientific
    payload: the superseded API took both a solver callback and an authority object, and would
    run the gate and then use the caller's authority instead of the gate's. Here the authority
    used is exactly the one the gate returns, and the only path to a solve is the single guarded
    call site.
    """
    if phase not in vf.PHASE_PREREQUISITES:
        raise ValueError("unknown phase %r; expected one of %r"
                         % (phase, sorted(vf.PHASE_PREREQUISITES)))
    base = pathlib.Path(runs_dir)
    if phase in ASSEMBLY_MODES:
        require_assembly_authorisation(phase, backend=backend, runs_dir=base)
        return vf.assemble_p2b_from_runs(base, backend=backend)   # pragma: no cover - unreached
    auth = require_execution_authorisation(phase, backend=backend, runs_dir=base)
    manifests, records = ({}, {})                                 # pragma: no cover - unreached
    if vf.PHASE_PREREQUISITES[phase]:                             # pragma: no cover - unreached
        manifests, records = vf.require_phase_manifests(phase, runs_dir=base, authority=auth)
    return _orchestrate(phase, base, auth, manifests, records,    # pragma: no cover - unreached
                        _guarded_result_provider, backend, "PRODUCTION")


def _orchestrate(phase, base, auth, manifests, records, provider, backend, provenance_mode):
    """Steps 5-13, over the FULL PHASE UNIVERSE (erratum PE-26).

    Private. The production entry point never exposes ``provider`` or ``provenance_mode``; the
    test seam supplies them and every record it writes is marked TEST_ONLY, which the production
    manifest and freeze validators reject.
    """
    matrix = vf.execution_matrix()["rows"]
    universe = vf.phase_universe(phase, matrix)
    eligible, adaptive = vf.derive_expected_rows(phase, matrix, predecessor_records=records)
    elig_ids = {r["case_id"] for r in eligible}
    pre_sha = {k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
               for k in manifests if (base / ("manifest_%s.json" % k)).exists()}
    completed, refused, failed, replicates = [], [], [], []
    payloads = {}
    terminal, stop_reason = "PHASE_COMPLETE", None

    for row in universe:                                          # matrix order, jobs = 1
        if row["case_id"] not in elig_ids:
            refused.append({"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                            "reason": "ADAPTIVELY_INELIGIBLE"})
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
        g = vf.row_forcing(row)
        cfg = vf.effective_solver_config(row, backend=backend, audit=audit_plan)
        res = provider(mask=mask, g=g, phase=phase, row=row, tau=row["tau_plus"],
                       audit=audit_plan, backend=backend)
        if row["kind"] == "pressure_plane_diagnostic":
            sci = _pressure_plane_scientific(res, mask, meta, g, row, base)
        elif kind == "coupon":
            sci = _coupon_scientific(res, mask, meta, g, row)
        else:
            sci = _fixture_scientific(res, mask, meta, g, row)
        geometry = {"kind": kind, "mask_sha256": meta["mask_sha256"], "S": row["S"],
                    "shape": list(meta.get("shape") or mask.shape),
                    "bridge": row["bridge"] if isinstance(row["bridge"], dict) else None,
                    "state": row["state"], "variant": row["variant"],
                    "obstructed": bool(meta.get("obstructed"))}
        payload = vf.scientific_payload_hash(cfg, sci, meta["mask_sha256"])
        rec = vf.make_case_record(row, auth, pre_sha, geometry, sci,
                                  completed_steps=int(res["steps"]),
                                  run_mode=row["run_mode"], audit=audit_plan,
                                  provenance_mode=provenance_mode,
                                  scientific_payload_sha256=payload)
        vf.validate_case_record(rec, row=row, authority=auth, phase=phase)
        path, how = vf.write_case_record(base, rec)
        payloads[row["case_id"]] = payload
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

    # PE-37: a determinism replicate must actually reproduce its base scientific payload
    done = {e["case_id"] for e in completed}
    for row in universe:
        if row["kind"] != "determinism_replicate" or row["case_id"] not in done:
            continue
        base_row = next((r for r in universe
                         if r["case_id"] != row["case_id"] and r["kind"] != "determinism_replicate"
                         and r["S"] == row["S"] and r["state"] == row["state"]
                         and r["variant"] == row["variant"]
                         and r["forcing_level"] == row["forcing_level"]
                         and r["run_mode"] == "NORMAL"), None)
        if base_row is None or base_row["case_id"] not in done:   # pragma: no cover - frozen set
            continue
        replicates.append({
            "replicate_case_id": row["case_id"], "base_case_id": base_row["case_id"],
            "scientific_payload_sha256": payloads[row["case_id"]],
            "base_scientific_payload_sha256": payloads[base_row["case_id"]],
            "pass": bool(payloads[row["case_id"]] == payloads[base_row["case_id"]]),
            "rule": ("canonical scientific payload over the effective configuration, the compact "
                     "outputs and the mask, excluding case identity and file metadata"),
        })

    manifest = vf.make_phase_manifest(phase, universe, eligible, completed, refused, failed,
                                      auth, pre_sha, adaptive, terminal, stop_reason,
                                      provenance_mode=provenance_mode, replicates=replicates)
    mpath = base / ("manifest_%s.json" % phase)
    tmp = base / (mpath.name + ".tmp")
    tmp.write_text(vf.canonical_json(manifest) + "\n")
    tmp.replace(mpath)
    vf.validate_phase_manifest(phase, base, authority=auth, matrix_rows=matrix,
                               predecessor_records=records,
                               require_production=(provenance_mode == "PRODUCTION"))
    return manifest


def _pressure_plane_scientific(res, mask, meta, g, row, runs_dir):
    """R on each frozen node-surface offset of the SAME solution (erratum PE-32).

    Needs no extra solve — the offsets are different planes of one field — but it does need a
    record, so a missing one now FAILS the artifact evidence rather than contributing zero.
    """
    ux, rho = res["ux"], res["rho"]
    offsets = [0] + list(meta["node_offsets"])
    vals, planes = [], []
    for off in offsets:
        xin, xout = meta["x_node_in"] - off, meta["x_node_out"] + off
        p_in = vf.axial_plane_record("x_node_in_off%d" % off, xin, ux, rho, mask, g)
        p_out = vf.axial_plane_record("x_node_out_off%d" % off, xout, ux, rho, mask, g)
        q = vf.axial_plane_record("x_meas_a", meta["x_meas_a"], ux, rho, mask, g)
        dP = p_in["p_mean"] - p_out["p_mean"]
        vals.append(q["sum_ux"] / dP if dP else float("inf"))
        planes += [p_in, p_out]
    base = vals[0]
    return {
        "node_offsets": list(offsets),
        "conductance_at_node_offsets": vals,
        "R_at_node_offsets": [v / base for v in vals],
        "offset_planes": planes,
        "base_case_id": row.get("audit_of_case_id"),
        "mach": vf.mach_record(res["ux"], res["uy"], res["uz"], mask),
        "note": ("re-reads the frozen node-surface offsets of one solution; it is a DIAGNOSTIC "
                 "record, not an additional solve"),
    }


def _guarded_result_provider(mask, g, phase, row, tau=None, audit=None, backend="reference"):
    """The ONLY production path to a solve. It refuses unless the phase is on the allowlist."""
    steps = None if audit is None else audit["target_steps"]
    return solve(mask, g, phase, backend=backend, tau=tau, steps=steps,
                 min_steps=(None if audit is None else audit["min_steps"]))


def run_phase(mode, out_dir=None, backend="reference", runs_dir=None, jobs=1):
    if mode not in MODES:
        raise ValueError("unknown mode %r; expected one of %r" % (mode, MODES))
    if jobs not in SUPPORTED_JOBS:
        raise ValueError("--jobs %r is not supported at this stage; only %r is accepted. The "
                         "matrix order is the execution order and no concurrency is implemented."
                         % (jobs, SUPPORTED_JOBS))
    if backend not in vf.SUPPORTED_BACKENDS:
        raise ValueError("backend %r is not supported; only %r exists. A backend argument is "
                         "never accepted and then silently routed to the reference solver."
                         % (backend, vf.SUPPORTED_BACKENDS))
    if mode == "plan":
        return vf.execution_matrix()
    rd = runs_dir if runs_dir is not None else out_dir
    if rd is None:
        rd = REPO_ROOT / vf.RUNS_REL
    return execute_phase(mode, rd, backend=backend)


def _test_only_execute(phase, runs_dir, provider, authority, manifests=None, records=None,
                       backend="reference"):
    """PRIVATE test seam (erratum PE-34).

    Not reachable from the production API or the CLI. Every record it writes carries
    ``provenance_mode = "TEST_ONLY"``, and the production manifest and freeze validators reject
    those records, so a synthetic pipeline can never masquerade as evidence.
    """
    return _orchestrate(phase, pathlib.Path(runs_dir), authority, manifests or {}, records or {},
                        provider, backend, "TEST_ONLY")


def main(argv=None):                                             # pragma: no cover - thin CLI
    ap = argparse.ArgumentParser(description="RP-D-LC-001b driver (PRE-EXECUTION: refuses)")
    ap.add_argument("--mode", required=True, choices=list(MODES))
    ap.add_argument("--backend", default="reference",
                    help="only 'reference' exists; anything else fails before execution")
    ap.add_argument("--output", default=None,
                    help="the runs directory actually used (default: the bundle's runs/)")
    ap.add_argument("--jobs", type=int, default=1,
                    help="only 1 is supported at this stage; a larger value is refused")
    a = ap.parse_args(argv)
    try:
        res = run_phase(a.mode, out_dir=a.output, backend=a.backend, jobs=a.jobs)
    except (ExecutionNotAuthorised, vf.FreezeMissing, vf.ManifestMissing,
            vf.ExecutionAuthorityError, vf.DesignBlocked, ValueError) as exc:
        print("REFUSED: %s" % exc)
        return 2
    if a.mode == "plan":
        print(json.dumps({"mode": "plan", "n_rows": res["n_rows"],
                          "planned_normal_solves": res["planned_normal_solves"],
                          "planned_fixed_step_audits": res["planned_fixed_step_audits"],
                          "planned_pressure_plane_diagnostics":
                              res["planned_pressure_plane_diagnostics"],
                          "solves_executed": res["solves_executed"]}, indent=2))
        return 0
    if a.mode in ASSEMBLY_MODES:
        print(json.dumps({"mode": a.mode, "phase_kind": res.get("phase_kind"),
                          "n_declared_candidates": res.get("n_declared_candidates"),
                          "n_eligible_candidates": res.get("n_eligible_candidates"),
                          "selection_status": res.get("selection_status"),
                          "terminal_status": res.get("terminal_status"),
                          "terminal_stop_reason": res.get("terminal_stop_reason"),
                          "artifacts_written": res.get("artifacts_written")}, indent=2))
        return 0
    print(json.dumps({"mode": a.mode, "terminal_status": res.get("terminal_status"),
                      "counts": res.get("counts")}, indent=2))
    return 0


if __name__ == "__main__":                                       # pragma: no cover
    raise SystemExit(main())

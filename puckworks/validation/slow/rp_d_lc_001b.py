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

#: The POST-FREEZE executor is NOT READY (erratum PE-76).
#:
#: P3/P4 orchestration still derives its universe from ``phase_universe()``, which returns the
#: PLANNING TEMPLATES — rows whose ``bridge`` is the placeholder string ``frozen_slot_N``. The
#: approved instantiated-matrix loader described by PE-54 does not exist yet and has not passed
#: exact-head review. This is a HARD REFUSAL, not a comment: P3 and P4 refuse even if they are
#: added to ``AUTHORISED_SOLVING_PHASES``, so an accidental allowlist edit cannot reach a
#: provider with an unresolved template.
#:
#: What the later P3/P4 authorization tranche must do, in its own reviewed source commit:
#:   1. validate the APPROVED freeze;
#:   2. load ``instantiated_p3_p4_matrix.json`` from the runs directory actually in use;
#:   3. use ITS rows as the phase universe, in place of the templates;
#:   4. bind its exact ``rows_sha256`` and file hash into every record and manifest it writes.
POST_FREEZE_EXECUTOR_READY = False
POST_FREEZE_PHASES = ("P3", "P4")
POST_FREEZE_NOT_READY_NOTE = (
    "the approved instantiated-matrix loader has not yet passed exact-head review: P3/P4 "
    "orchestration would still derive its universe from the planning TEMPLATES, whose bridge is "
    "an unresolved placeholder. Loading the approved instantiated matrix, using its rows as the "
    "phase universe and binding its exact hashes is reserved for a later authorization tranche."
)


class ExecutionNotAuthorised(RuntimeError):
    """Raised by every solving mode while the tranche is pre-execution."""


class PostFreezeExecutorNotReady(ExecutionNotAuthorised):
    """P3/P4 are refused INDEPENDENTLY of the solving allowlist (erratum PE-76).

    A subclass, so every existing refusal contract still holds, with a distinct type and reason
    for the one refusal an allowlist edit cannot lift.
    """


def _refuse_post_freeze(phase):
    raise PostFreezeExecutorNotReady(
        "phase %r is refused: POST_FREEZE_EXECUTOR_READY = %r. %s"
        % (phase, POST_FREEZE_EXECUTOR_READY, POST_FREEZE_NOT_READY_NOTE))

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
    # PE-76: checked FIRST and independently of the allowlist, so adding P3/P4 to
    # AUTHORISED_SOLVING_PHASES cannot reach a provider with an unresolved template.
    if phase in POST_FREEZE_PHASES and not POST_FREEZE_EXECUTOR_READY:
        _refuse_post_freeze(phase)
    if phase in FREEZE_GATED_MODES:
        vf.require_freeze(phase, runs_dir=runs_dir)      # PE-56: the directory ACTUALLY in use
    vf.require_phase_manifests(phase, runs_dir=runs_dir)
    if phase not in AUTHORISED_SOLVING_PHASES:
        _refuse(phase)
    return vf.execution_authority(phase, backend=backend)         # pragma: no cover - unreached


def solve(mask, g, phase, backend="reference", tau=None, fields=REQUIRED_FIELDS, steps=None,
          min_steps=None, **kw):
    """The single solver call site. It refuses unless its phase is on the reviewed allowlist, so
    no code path in this module can reach the kernel by accident."""
    if phase in POST_FREEZE_PHASES and not POST_FREEZE_EXECUTOR_READY:
        _refuse_post_freeze(phase)                # PE-76: the single call site refuses too
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
        "node_offsets": vf.node_offset_summary(res["ux"], res["rho"], mask, meta, g),
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
                   "bridge_coupon", "candidate_blocked_mirror",
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
        # PE-41/PE-42: extracted from THIS case's own field; no separate solve, and the
        # per-offset quantity is a conductance, never a ratio.
        "node_offsets": vf.node_offset_summary(res["ux"], res["rho"], mask, meta, g,
                                               case_id=row["case_id"]),
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
    """Delegates to the ONE shared classification (erratum PE-58), so the executor and the
    manifest validator can never disagree about whether a case passed."""
    v = vf.case_decision_verdict(row, sci, status)
    return v["pass"], v["reason"]


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
    if phase in POST_FREEZE_PHASES and not POST_FREEZE_EXECUTOR_READY:
        _refuse_post_freeze(phase)                             # PE-76
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
    """Steps 5-13, over the FULL PHASE UNIVERSE (erratum PE-26), with TRUE PRE-SOLVE RESUME
    (erratum PE-74).

    Private. The production entry point never exposes ``provider`` or ``provenance_mode``; the
    test seam supplies them and every record it writes is marked TEST_ONLY, which the production
    manifest and freeze validators reject.

    For every eligible row the record path is derived FIRST. An existing record is reopened and
    fully revalidated and, on an exact match, reused with **no provider call**; a differing
    record fails closed **before** the provider; only a missing record reaches the guarded
    provider. ``n_provider_calls == n_newly_executed`` is asserted at the end of the phase.
    """
    matrix = vf.execution_matrix()["rows"]
    universe = vf.phase_universe(phase, matrix)
    eligible, adaptive = vf.derive_expected_rows(phase, matrix, predecessor_records=records)
    elig_ids = {r["case_id"] for r in eligible}
    pre_sha = {k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
               for k in manifests if (base / ("manifest_%s.json" % k)).exists()}

    # PE-75: manifest resume. An existing FINAL manifest is reopened and fully validated; an
    # exact valid completion under this authority returns with ZERO provider calls, and anything
    # else fails closed rather than being overwritten.
    mpath = base / ("manifest_%s.json" % phase)
    if mpath.exists():
        return vf.validate_phase_manifest(phase, base, authority=auth, matrix_rows=matrix,
                                          predecessor_records=records,
                                          require_production=(provenance_mode == "PRODUCTION"))

    completed, refused, failed, replicates = [], [], [], []
    diagnostic_completed, diagnostic_failed = [], []       # erratum PE-79
    payloads = {}
    terminal, stop_reason = "PHASE_COMPLETE", None
    n_new = n_reused = n_calls = 0

    for row in universe:                                          # matrix order, jobs = 1
        if row["case_id"] not in elig_ids:
            refused.append({"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                            "reason": "ADAPTIVELY_INELIGIBLE"})
            continue
        if terminal != "PHASE_COMPLETE":
            refused.append({"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                            "reason": "REFUSED_AFTER_PHASE_STOP"})
            continue
        # ---- 1. resolve the row and its effective configuration WITHOUT solving --------------
        if isinstance(row.get("bridge"), str):                 # PE-76: never a placeholder
            _refuse_post_freeze(row["phase"])
        mask, meta, kind = resolve_row(row)
        audit_plan = None
        if row["run_mode"] == "FIXED_STEP_REEXECUTION_1P5X":
            # the exact normal base and its audit plan are validated BEFORE either reuse or
            # execution of the audit
            base_rec, _ = vf.read_case_record(base, row["audit_of_case_id"])
            base_row = next((r for r in matrix if r["case_id"] == base_rec["case_id"]), None)
            if base_row is None:                     # pragma: no cover - matrix is exhaustive
                raise ValueError("audit %r names a base outside the canonical matrix"
                                 % (row["case_id"],))
            vf.assert_audit_compatible(row, base_row)
            audit_plan = vf.fixed_step_audit_plan(base_rec["completed_steps"],
                                                  base_rec["status"])
            audit_plan["base_case_id"] = base_rec["case_id"]
            audit_plan["base_record_sha256"] = vf.record_hash(base_rec)
        g = vf.row_forcing(row)
        cfg = vf.effective_solver_config(row, backend=backend, audit=audit_plan)
        geometry = {"kind": kind, "mask_sha256": meta["mask_sha256"], "S": row["S"],
                    "shape": list(meta.get("shape") or mask.shape),
                    "bridge": row["bridge"] if isinstance(row["bridge"], dict) else None,
                    "state": row["state"], "variant": row["variant"],
                    "obstructed": bool(meta.get("obstructed"))}
        # ---- 2/3/4. derive the record path and reuse or fail closed BEFORE the provider ------
        existing = vf.load_resumable_case_record(base, row, auth, phase, pre_sha, geometry,
                                                 provenance_mode=provenance_mode,
                                                 audit=audit_plan)
        if existing is not None:
            rec, path = existing
            sci = rec.get("scientific")
            payload = rec["scientific_payload_sha256"]
            how = "REUSED_EXACT_MATCH"
            n_reused += 1
        else:
            # ---- 5. only now may the guarded provider be called ------------------------------
            n_calls += 1
            res = provider(mask=mask, g=g, phase=phase, row=row, tau=row["tau_plus"],
                           audit=audit_plan, backend=backend)
            if kind == "coupon":
                sci = _coupon_scientific(res, mask, meta, g, row)
            else:
                sci = _fixture_scientific(res, mask, meta, g, row)
            payload = vf.scientific_payload_hash(cfg, sci, meta["mask_sha256"])
            rec = vf.make_case_record(row, auth, pre_sha, geometry, sci,
                                      completed_steps=int(res["steps"]),
                                      run_mode=row["run_mode"], audit=audit_plan,
                                      provenance_mode=provenance_mode,
                                      scientific_payload_sha256=payload)
            vf.validate_case_record(rec, row=row, authority=auth, phase=phase)
            path, how = vf.write_case_record(base, rec)
            n_new += 1
        payloads[row["case_id"]] = payload
        entry = {"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                 "record_path": path.name, "write_mode": how,
                 "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                 "status": rec["status"]}
        # erratum PE-79: the ROLE-AWARE classifier decides both the ledger and the effect. A
        # non-adjudicative diagnostic is filed in its own ledger and NEVER stops the phase, valid
        # or not; an adjudicative failure stops it exactly as before.
        verdict = vf.case_decision_verdict(row, sci, rec["status"])
        entry["scientific_role"] = verdict["scientific_role"]
        if not verdict["pass"]:
            entry["reason"] = verdict["reason"]
        ledger = {"completed": completed, "failed": failed,
                  "diagnostic_completed": diagnostic_completed,
                  "diagnostic_failed": diagnostic_failed}[verdict["ledger"]]
        ledger.append(entry)
        if verdict["effect"] == "STOPS_THE_PHASE":
            terminal = ("PHASE_STOPPED_UNCONVERGED" if verdict["reason"] == "NORMAL_UNCONVERGED"
                        else "PHASE_STOPPED_INVALID_CASE")
            stop_reason = verdict["reason"]

    # PE-37: a determinism replicate must actually reproduce its base scientific payload. Its
    # EXECUTION_ASSURANCE_REPLICATE role is adjudicative and its semantics are unchanged by C6.
    done = {e["case_id"] for e in completed}
    for row in universe:
        if row["kind"] != "determinism_replicate" or row["case_id"] not in done:
            continue
        # erratum PE-59: the base is EXPLICIT, never inferred by searching for the first row
        # that happens to share a few fields.
        base_id = row.get("replicate_of_case_id")
        if base_id is None:
            raise ValueError("replicate row %r carries no replicate_of_case_id" % (row["case_id"],))
        base_row = next((r for r in universe if r["case_id"] == base_id), None)
        if base_row is None or base_id not in done:
            raise ValueError("replicate row %r names base %r, which is not a completed row"
                             % (row["case_id"], base_id))
        vf.assert_replicate_compatible(row, base_row)
        replicates.append({
            "replicate_case_id": row["case_id"], "base_case_id": base_row["case_id"],
            "scientific_payload_sha256": payloads[row["case_id"]],
            "base_scientific_payload_sha256": payloads[base_row["case_id"]],
            "pass": bool(payloads[row["case_id"]] == payloads[base_row["case_id"]]),
            "rule": ("canonical scientific payload over the effective configuration, the compact "
                     "outputs and the mask, excluding case identity and file metadata"),
        })

    # PE-64: the phase's durable AGGREGATE scientific verdict, computed from the records this
    # phase completed. The validator recomputes it, so the executor cannot assert one.
    phase_science = None
    if phase in vf.PHASE_AGGREGATE_SCIENCE:
        # erratum PE-81: only ADJUDICATIVE completed records reach the aggregate. The tau
        # diagnostics are in their own ledger and enter no aggregate truth.
        done_ids = {e["case_id"] for e in completed}
        phase_records = {}
        for cid in sorted(done_ids):
            rec, _ = vf.read_case_record(base, cid)
            phase_records[cid] = rec
        phase_science = vf.PHASE_AGGREGATE_SCIENCE[phase](phase_records)
    # PE-74: a provider call may only ever construct a NEW record. A resumed phase legitimately
    # has fewer provider calls than completed rows; it may never have more than newly executed.
    if n_calls != n_new:                                  # pragma: no cover - guarded by control
        raise RuntimeError("phase %r made %d provider calls for %d newly executed rows"
                           % (phase, n_calls, n_new))
    execution_counts = {"n_newly_executed": n_new, "n_reused": n_reused,
                        "n_provider_calls": n_calls, "n_completed": len(completed),
                        "n_failed": len(failed), "n_refused": len(refused),
                        "n_diagnostic_completed": len(diagnostic_completed),
                        "n_diagnostic_failed": len(diagnostic_failed)}
    manifest = vf.make_phase_manifest(phase, universe, eligible, completed, refused, failed,
                                      auth, pre_sha, adaptive, terminal, stop_reason,
                                      provenance_mode=provenance_mode, replicates=replicates,
                                      phase_science=phase_science,
                                      execution_counts=execution_counts,
                                      diagnostic_completed=diagnostic_completed,
                                      diagnostic_failed=diagnostic_failed)
    # PE-75: atomic, no-overwrite / exact-match write. A differing existing manifest is never
    # silently replaced.
    vf._atomic_write_json(base / ("manifest_%s.json" % phase), manifest)
    vf.validate_phase_manifest(phase, base, authority=auth, matrix_rows=matrix,
                               predecessor_records=records,
                               require_production=(provenance_mode == "PRODUCTION"))
    return manifest


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


#: The exact keys ``--mode plan`` prints. Kept OUT of the thin-CLI pragma and asserted by test:
#: the superseded C4 form named ``planned_pressure_plane_diagnostics``, a key that never existed
#: in the matrix, so the documented command raised KeyError and nothing caught it.
PLAN_SUMMARY_KEYS = ("n_rows", "planned_normal_solves", "planned_fixed_step_audits",
                     "planned_pressure_plane_diagnostic_rows", "planned_solver_invocations",
                     "same_field_node_offset_summaries",
                     "provider_calls_fresh_full_pre_freeze_run",
                     "provider_calls_on_exact_resume", "p3_p4_planning_template_rows",
                     "post_freeze_executor_ready", "solves_executed")


def plan_summary(matrix):
    """The machine-derived plan summary. Every key is read from the matrix, so a key that does
    not exist there fails here rather than only at the terminal."""
    missing = [k for k in PLAN_SUMMARY_KEYS if k not in matrix]
    if missing:
        raise KeyError("the execution matrix carries no %r" % (missing,))
    out = {"mode": "plan"}
    out.update({k: matrix[k] for k in PLAN_SUMMARY_KEYS})
    out["authorised_solving_phases"] = list(AUTHORISED_SOLVING_PHASES)
    out["authorised_assembly_phases"] = list(AUTHORISED_ASSEMBLY_PHASES)
    return out


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
    except (ExecutionNotAuthorised, PostFreezeExecutorNotReady, vf.FreezeMissing,
            vf.ManifestMissing, vf.ExecutionAuthorityError, vf.DesignBlocked, ValueError) as exc:
        print("REFUSED: %s" % exc)
        return 2
    if a.mode == "plan":
        print(json.dumps(plan_summary(res), indent=2))
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

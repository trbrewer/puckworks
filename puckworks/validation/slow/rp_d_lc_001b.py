"""RP-D-LC-001b — slow driver SCAFFOLD.

NO LATTICE-BOLTZMANN SOLVE HAS BEEN PERFORMED FOR THIS TRANCHE, AND THIS MODULE REFUSES TO
PERFORM ONE. Authorisation is PHASE-SPECIFIC (erratum PE-11): ``AUTHORISED_SOLVING_PHASES`` is
empty at this head, so every solving phase raises ``ExecutionNotAuthorised``.

The PRE-FREEZE authorization is an ATOMIC SOURCE COHORT (erratum PE-124). ONE exact reviewed
authorization commit authorizes the complete P0-through-P2b cohort: a committed head may declare
either no pre-freeze phase authorized or all four solving phases in canonical order plus P2b in the
assembly allowlist, and every partial state is refused. That is the fact the code already required —
``require_phase_manifests`` requires every predecessor's authority to carry this phase's own
``source_commit`` and ``source_tree``, so under sequential per-phase authorization commits P1a could
never consume P0. Each phase nevertheless remains SEPARATELY gated by its prerequisites, so a shared
authorization head does not make execution monolithic. P3 and P4 require a LATER source commit, are
never part of the pre-freeze cohort, and stay unavailable while ``POST_FREEZE_EXECUTOR_READY`` is
false. The resulting exact head is the object reviewed for execution.

Independently of that allowlist, P3 and P4 refuse without the reviewed bridge freeze AND the
reviewed instantiated P3/P4 matrix, and every phase refuses without valid completion manifests
for its predecessors — both checked BEFORE the allowlist, so neither gate is shadowed by it.

Every production execution and assembly mode additionally REQUIRES an explicit absolute runs
directory OUTSIDE this repository (erratum PE-114). There is no default: the production authority
requires a clean Git worktree, and a repository-internal bundle would destroy that before the next
phase could construct its own authority. ``--mode plan`` reads the canonical matrix, writes
nothing, and needs no output path.

What IS implemented here is everything that can be checked without a solver: the per-case
record construction from already-computed fields, the phase ordering, the freeze gate and the
execution-authority record. Heavy execution never enters normal CI (CLAUDE.md rule 3).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import time
import traceback

import numpy as np

from puckworks.analysis import rp_d_lc_001b_virtual_fixture as vf
from puckworks.validation.slow import rp_d_lc_001b_process_pool as pool_engine

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]

#: The PHASE-SPECIFIC reviewed allowlist (erratum PE-11). Superseded: one module-level
#: EXECUTION_AUTHORISED boolean, which would have authorised the primary experiment and Arm J in
#: the same act as the pre-freeze phases.
#:
#: It is deliberately a source-level constant rather than a flag or an environment variable:
#: authorising the cohort must be a reviewable change to the repository, and the resulting exact head
#: is the object reviewed for execution. Authorising P0/P1a/P1b/P2a does NOT authorise P3 or P4, and
#: P3 stays hard-refused even when a syntactically valid freeze exists.
#:
#: erratum PE-124: the PRE-FREEZE entries are ATOMIC. This tuple may contain none of
#: ``vf.PREFREEZE_SOLVING_AUTHORIZATION_COHORT`` or all of it, in canonical order, and the parser
#: refuses every partial state. It is not filled in one phase at a time.
#:
#: AUTHORIZED at this exact head: the COMPLETE pre-freeze solving cohort. The committed state is
#: ``COMPLETE_PREFREEZE_COHORT_AUTHORIZED``. This authorizes nothing beyond the pre-freeze cohort: P3
#: and P4 are absent, and are independently hard-refused by POST_FREEZE_EXECUTOR_READY below.
#:
#: Authorization is not a schedule. The existing predecessor gates still control the order
#: P0 -> P1a -> P1b -> P2a -> P2b: every phase after P0 refuses without a validated completion
#: manifest for each of its prerequisites, so a shared authorization head does not let a later phase
#: start early. Nothing has run at this head.
AUTHORISED_SOLVING_PHASES = ()

#: The SEPARATE assembly allowlist (erratum PE-39). P2b is arithmetic and must never share the
#: solving gate: authorising P0-P2a must not authorise the assembly, and authorising the assembly
#: must not authorise P3/P4. Both carry the pre-freeze cohort at this head, and neither names a
#: phase belonging to the other gate.
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


#: ONE shared implementation, defined beside the committed-authorization parser and re-exported
#: here so the driver and the assembler cannot drift apart (erratum PE-104).
ExecutionNotAuthorised = vf.ExecutionNotAuthorised

#: The frozen runtime-bundle policy (errata PE-114 … PE-116), re-exported from the ONE pure
#: validator the driver and the P2b assembler share. There is no repository-internal default: the
#: production authority requires a clean worktree, so runtime output may never be written beneath
#: it. The absolute pathname is a property of one workstation and enters no scientific hash.
PRODUCTION_RUNS_DIRECTORY_POLICY = vf.PRODUCTION_RUNS_DIRECTORY_POLICY
RunsDirectoryPolicyError = vf.RunsDirectoryPolicyError


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
SUPPORTED_JOBS = tuple(range(1, pool_engine.MAX_REFERENCE_WORKERS + 1))

AUTHORISATION_NOTE = (
    "RP-D-LC-001b is PRE-EXECUTION. The protocol, the corrected fixture, the conserved-quantity "
    "contract, the similarity law, the negative-control gate and the reachable-set margin are "
    "frozen and awaiting substantive scientific review at an exact head. No solve may run before "
    "that review. ONE exact reviewed authorization commit then authorizes the COMPLETE "
    "P0-through-P2b cohort — the pre-freeze allowlists are atomic and every partial state is "
    "refused — while each phase remains separately gated by its own prerequisites. P3 and P4 "
    "require a later source commit and remain unavailable (erratum PE-124)."
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


def require_assembly_authorisation(phase, backend="reference", runs_dir=None, jobs=1):
    """The assembly gate (erratum PE-39). Separate from the solving gate in both directions."""
    if phase not in ASSEMBLY_MODES:
        raise ValueError("phase %r is not an assembly phase" % (phase,))
    vf.require_phase_manifests(phase, runs_dir=runs_dir)
    # erratum PE-104: the SHARED gate, reading the committed constants. The local tuple above is
    # the source of truth it parses, so the two can never disagree.
    vf.assert_stage_authorised(phase)
    return vf.execution_authority(
        phase, backend=backend,
        execution_engine=pool_engine.execution_engine_identity(jobs))  # pragma: no cover


def require_execution_authorisation(phase, backend="reference", runs_dir=None, jobs=1):
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
    vf.assert_stage_authorised(phase)                             # pragma: no cover - unreached
    return vf.execution_authority(
        phase, backend=backend,
        execution_engine=pool_engine.execution_engine_identity(jobs))  # pragma: no cover


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


def execute_phase(phase, runs_dir, backend="reference", jobs=1):
    """The PRODUCTION pre-freeze executor (erratum PE-34).

    The signature accepts **no** result provider, **no** authority override and **no** scientific
    payload: the superseded API took both a solver callback and an authority object, and would
    run the gate and then use the caller's authority instead of the gate's. Here the authority
    used is exactly the one the gate returns, and the only path to a solve is the single guarded
    call site.

    ``runs_dir`` is MANDATORY and must be an explicit absolute path outside the repository
    (erratum PE-114). It is validated FIRST — before the post-freeze refusal, the freeze gate,
    predecessor validation, authority construction, any provider call and any artifact — because
    the authority every later phase needs requires a clean worktree, and a repository-internal
    bundle destroys that before the next phase can ask for it.
    """
    if phase not in vf.PHASE_PREREQUISITES:
        raise ValueError("unknown phase %r; expected one of %r"
                         % (phase, sorted(vf.PHASE_PREREQUISITES)))
    base = vf.validate_production_runs_dir(runs_dir, require_production=True)
    if phase in POST_FREEZE_PHASES and not POST_FREEZE_EXECUTOR_READY:
        _refuse_post_freeze(phase)                             # PE-76
    if phase in ASSEMBLY_MODES:
        if jobs != 1:
            raise ValueError("P2b is arithmetic and accepts --jobs 1 only")
        require_assembly_authorisation(phase, backend=backend, runs_dir=base, jobs=1)
        return vf.assemble_p2b_from_runs(base, backend=backend)   # pragma: no cover - unreached
    auth = require_execution_authorisation(phase, backend=backend, runs_dir=base, jobs=jobs)
    # PE-114: only now, with the policy passed and the phase authorized, is the bundle created.
    vf.validate_production_runs_dir(base, require_production=True,  # pragma: no cover - unreached
                                    create=True)
    manifests, records = ({}, {})                                 # pragma: no cover - unreached
    if vf.PHASE_PREREQUISITES[phase]:                             # pragma: no cover - unreached
        manifests, records = vf.require_phase_manifests(phase, runs_dir=base, authority=auth)
    if jobs == 1:
        return _orchestrate(phase, base, auth, manifests, records,  # pragma: no cover
                            _guarded_result_provider, backend, "PRODUCTION")
    return _orchestrate_parallel(phase, base, auth, manifests, records, jobs)  # pragma: no cover


#: The result fields every provider must return. Checked EXPLICITLY, so a missing field is a
#: named result-contract failure rather than a KeyError from somewhere inside the extraction.
def _failure_traceback(failure):
    """The full traceback text, retained only as a SHA-256 in the envelope (erratum PE-92)."""
    if failure.exc is None:
        return None
    return "".join(traceback.format_exception(type(failure.exc), failure.exc,
                                              failure.exc.__traceback__))


REQUIRED_RESULT_FIELDS = ("ux", "rho", "uy", "uz", "steps")


def _exact_steps(value):
    """An EXACT non-negative integer step count (erratum PE-112).

    C7 wrote ``int(res["steps"])`` inside a ``try``, so ``2000.5`` truncated silently to 2000
    and ``True`` became 1. A NumPy integer scalar is accepted; everything lossy is refused.
    """
    if isinstance(value, bool):
        raise vf.DiagnosticAttemptFailed(
            "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
            detail="the result's step count is a bool, not an integer")
    if isinstance(value, int):
        out = int(value)
    elif isinstance(value, np.integer):
        out = int(value)
    else:
        raise vf.DiagnosticAttemptFailed(
            "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
            detail=("the result's step count is %s, not an integer; a float, a numeric string, "
                    "a complex value and any lossy conversion are all refused"
                    % type(value).__name__))
    if out < 0:
        raise vf.DiagnosticAttemptFailed(
            "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
            detail="the result's step count is negative")
    return out


#: Real numeric NumPy kinds. Object, string, bytes, complex, void and datetime arrays are all
#: refused BY NAME rather than allowed to raise TypeError out of the contract (erratum PE-111).
NUMERIC_KINDS = ("i", "u", "f")


def _assert_result_contract(res, mask):
    """The provider/result boundary, checked explicitly (errata PE-91, PE-111, PE-112).

    Raises ``vf.DiagnosticAttemptFailed`` with a frozen code. The CALLER decides whether that is
    eligible to become a diagnostic envelope: for an adjudicative row it is re-raised as the
    fatal or phase-stopping failure it has always been.
    """
    if not isinstance(res, dict):
        raise vf.DiagnosticAttemptFailed(
            "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
            detail="the provider returned %s, not a result mapping" % type(res).__name__)
    missing = [f for f in REQUIRED_RESULT_FIELDS if f not in res]
    if missing:
        raise vf.DiagnosticAttemptFailed(
            "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
            detail="the result is missing %r" % (missing,))
    _exact_steps(res["steps"])
    for f in ("ux", "rho", "uy", "uz"):
        # erratum PE-111: np.asarray itself can raise on an incompatible representation, and
        # np.isfinite raises TypeError on an object, string, bytes or complex array. Both are
        # caught and mapped to a NAMED code rather than escaping the contract.
        try:
            arr = np.asarray(res[f])
        except vf.DIAGNOSTIC_NEVER_CAUGHT:
            raise
        except (TypeError, ValueError) as exc:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
                detail="field %r could not be read as an array (%s)" % (f, type(exc).__name__))
        if arr.dtype.kind not in NUMERIC_KINDS:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
                detail="field %r has dtype %r; a real numeric dtype is required"
                       % (f, str(arr.dtype)))
        if arr.shape != mask.shape:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
                detail="field %r has shape %r; the mask is %r" % (f, arr.shape, mask.shape))
        try:
            finite = bool(np.isfinite(arr[~mask]).all())
        except vf.DIAGNOSTIC_NEVER_CAUGHT:
            raise
        except (TypeError, ValueError) as exc:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_RESULT_CONTRACT_INVALID", "RESULT_CONTRACT",
                detail="field %r cannot be finite-checked (%s)" % (f, type(exc).__name__))
        if not finite:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_RESULT_NONFINITE", "RESULT_CONTRACT",
                detail="field %r carries a non-finite value at a fluid node" % (f,))
    return res


def _attempt_case(provider, mask, meta, g, phase, row, kind, audit_plan, backend):
    """Call the provider and form the compact science, with a NAMED failure at each boundary.

    Every failure raised here is row-local and result-specific. Authority, repository,
    persistence and orchestration failures are raised by their own code paths and never pass
    through this function (erratum PE-90 §5.2).
    """
    try:
        res = provider(mask=mask, g=g, phase=phase, row=row, tau=row["tau_plus"],
                       audit=audit_plan, backend=backend)
    except vf.DIAGNOSTIC_NEVER_CAUGHT:
        raise
    except Exception as exc:
        raise vf.DiagnosticAttemptFailed("DIAGNOSTIC_PROVIDER_EXCEPTION", "PROVIDER_CALL",
                                         exc=exc)
    _assert_result_contract(res, mask)
    try:
        sci = (_coupon_scientific(res, mask, meta, g, row) if kind == "coupon"
               else _fixture_scientific(res, mask, meta, g, row))
    except vf.DIAGNOSTIC_NEVER_CAUGHT:
        raise
    except vf.NonFiniteValue as exc:
        raise vf.DiagnosticAttemptFailed("DIAGNOSTIC_RESULT_NONFINITE",
                                         "SCIENTIFIC_EXTRACTION", exc=exc)
    except Exception as exc:
        raise vf.DiagnosticAttemptFailed("DIAGNOSTIC_SCIENTIFIC_EXTRACTION_FAILED",
                                         "SCIENTIFIC_EXTRACTION", exc=exc)
    return res, sci


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

    # ---- erratum PE-105: persist the COMPLETE authority BEFORE the first provider call -------
    # An interrupted phase must leave records whose authority preimage is on disk, not only in
    # this process's memory. On a resumed phase the existing artifact is reopened FIRST and must
    # equal the authority this run was invoked under; anything else fails closed before any
    # provider call.
    pa_doc = vf.make_phase_authority_document(phase, auth, pre_sha,
                                              provenance_mode=provenance_mode)
    pa_path, pa_write_mode = vf.write_phase_authority(base, pa_doc)
    pa_sha = hashlib.sha256(pa_path.read_bytes()).hexdigest()
    vf.validate_phase_authority_document(
        pa_doc, phase, require_production=(provenance_mode == "PRODUCTION"),
        expected_current_authority=auth, expected_predecessors=pre_sha)

    # PE-75: manifest resume. An existing FINAL manifest is reopened and fully validated; an
    # exact valid completion under this authority returns with ZERO provider calls, and anything
    # else fails closed rather than being overwritten.
    mpath = base / ("manifest_%s.json" % phase)
    if mpath.exists():
        return vf.validate_phase_manifest(phase, base, authority=auth, matrix_rows=matrix,
                                          predecessor_records=records,
                                          require_production=(provenance_mode == "PRODUCTION"))

    completed, refused, failed = [], [], []
    diagnostic_completed, diagnostic_failed = [], []       # erratum PE-79
    #: erratum PE-120: every fixed-step plan this phase reconstructed from its exact normal base,
    #: retained so the assurance contract and the manifest validator use the SAME plans.
    audit_plans = {}
    terminal, stop_reason = "PHASE_COMPLETE", None
    n_new = n_reused = n_calls = 0
    n_new_env = n_reused_env = 0                           # erratum PE-92

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
            # erratum PE-120: the base's status is RECOMPUTED from its own run mode and step count,
            # never read from its stored field, and the same plan the manifest validator will
            # independently reconstruct is retained here.
            audit_plan = vf.fixed_step_audit_plan(base_rec["completed_steps"],
                                                  vf.recomputed_case_status(base_rec))
            audit_plan["base_case_id"] = base_rec["case_id"]
            audit_plan["base_record_sha256"] = vf.record_hash(base_rec)
            audit_plans[row["case_id"]] = audit_plan
        g = vf.row_forcing(row)
        cfg = vf.effective_solver_config(row, backend=backend, audit=audit_plan)
        geometry = {"kind": kind, "mask_sha256": meta["mask_sha256"], "S": row["S"],
                    "shape": list(meta.get("shape") or mask.shape),
                    "bridge": row["bridge"] if isinstance(row["bridge"], dict) else None,
                    "state": row["state"], "variant": row["variant"],
                    "obstructed": bool(meta.get("obstructed"))}
        # ---- 2/3/4. derive the record path and reuse or fail closed BEFORE the provider ------
        # PE-92: a normal record and a diagnostic envelope may never coexist for one case ID
        vf.assert_no_coexisting_artifacts(base, row["case_id"])
        role = vf.row_scientific_role(row)
        envelope_eligible = role in vf.DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES
        existing = vf.load_resumable_case_record(base, row, auth, phase, pre_sha, geometry,
                                                 provenance_mode=provenance_mode,
                                                 audit=audit_plan,
                                                 phase_authority_file_sha256=pa_sha)
        existing_env = None
        if existing is None and envelope_eligible:
            existing_env = vf.load_resumable_diagnostic_failure(
                base, row, auth, phase, pre_sha, geometry,
                provenance_mode=provenance_mode, audit=audit_plan,
                phase_authority_file_sha256=pa_sha)
        if existing_env is not None:
            # an EXACT resumed envelope: zero provider calls, exactly as for a record
            env, path = existing_env
            n_reused_env += 1
            diagnostic_failed.append({
                "case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                "artifact_kind": "DIAGNOSTIC_FAILURE_ENVELOPE",
                "record_path": path.name, "write_mode": "REUSED_EXACT_MATCH",
                "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "status": env["status"], "scientific_role": env["scientific_role"],
                "reason": env["failure_code"], "failure_stage": env["failure_stage"]})
            continue
        if existing is not None:
            rec, path = existing
            sci = rec.get("scientific")
            how = "REUSED_EXACT_MATCH"
            n_reused += 1
        else:
            # ---- 5. only now may the guarded provider be called ------------------------------
            n_calls += 1
            try:
                res, sci = _attempt_case(provider, mask, meta, g, phase, row, kind, audit_plan,
                                         backend)
                # erratum PE-111 §9.3: a failure caused SOLELY by the returned result during
                # strict payload formation or record construction is a named diagnostic code.
                # An authority, geometry, matrix, filesystem or persistence failure is not, and
                # is raised by its own code path outside this boundary.
                try:
                    payload = vf.scientific_payload_hash(cfg, sci, meta["mask_sha256"])
                    rec = vf.make_case_record(row, auth, pre_sha, geometry, sci,
                                              completed_steps=_exact_steps(res["steps"]),
                                              run_mode=row["run_mode"], audit=audit_plan,
                                              provenance_mode=provenance_mode,
                                              scientific_payload_sha256=payload,
                                              phase_authority_file_sha256=pa_sha)
                except vf.DIAGNOSTIC_NEVER_CAUGHT:
                    raise
                except vf.DiagnosticAttemptFailed:
                    raise
                except vf.NonFiniteValue as exc:
                    raise vf.DiagnosticAttemptFailed(
                        "DIAGNOSTIC_RESULT_NONFINITE", "RECORD_CONSTRUCTION", exc=exc)
                except (TypeError, ValueError) as exc:
                    raise vf.DiagnosticAttemptFailed(
                        "DIAGNOSTIC_SCIENTIFIC_EXTRACTION_FAILED", "RECORD_CONSTRUCTION",
                        exc=exc)
            except vf.DiagnosticAttemptFailed as failure:
                # erratum PE-89: ONLY a non-adjudicative diagnostic may absorb a failed attempt.
                # For every adjudicative role the original failure is re-raised unchanged.
                if not envelope_eligible:
                    if failure.exc is not None:
                        raise failure.exc
                    raise ValueError(
                        "row %r carries the adjudicative role %r and its result violated the "
                        "provider contract (%s at %s): %s. Only a non-adjudicative diagnostic "
                        "may absorb a failed attempt (erratum PE-89)."
                        % (row["case_id"], role, failure.code, failure.stage, failure.detail))
                env = vf.make_diagnostic_failure_envelope(
                    row, auth, pre_sha, geometry, failure,
                    provenance_mode=provenance_mode, audit=audit_plan,
                    traceback_text=_failure_traceback(failure),
                    phase_authority_file_sha256=pa_sha)
                path, how = vf.write_diagnostic_failure_envelope(base, env)
                n_new_env += 1
                diagnostic_failed.append({
                    "case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                    "artifact_kind": "DIAGNOSTIC_FAILURE_ENVELOPE",
                    "record_path": path.name, "write_mode": how,
                    "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "status": env["status"], "scientific_role": env["scientific_role"],
                    "reason": env["failure_code"], "failure_stage": env["failure_stage"]})
                continue
            vf.validate_case_record(rec, row=row, authority=auth, phase=phase,
                                    expected_predecessors=pre_sha,
                                    phase_authority_file_sha256=pa_sha,
                                    geometry=geometry, audit=audit_plan,
                                    provenance_mode=provenance_mode)
            path, how = vf.write_case_record(base, rec)
            n_new += 1
        entry = {"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
                 "artifact_kind": "CASE_RECORD",
                 "record_path": path.name, "write_mode": how,
                 "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                 "status": rec["status"]}
        # erratum PE-79: the ROLE-AWARE classifier decides both the ledger and the effect. A
        # non-adjudicative diagnostic is filed in its own ledger and NEVER stops the phase, valid
        # or not; an adjudicative failure stops it exactly as before.
        # erratum PE-117: the RECOMPUTED status, from the record's own run mode, step count and
        # audit plan — never the stored field.
        verdict = vf.case_decision_verdict(row, sci,
                                           vf.recomputed_case_status(rec, audit=audit_plan))
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

    # errata PE-37, PE-59, PE-121 … PE-123: the assurance set is DERIVED from the canonical eligible
    # rows, its base binding is explicit, and its payload equality is RECOMPUTED from each record's
    # own configuration, compact payload and mask rather than read from the stored identities.
    #
    # PE-123: the contract is validated HERE, before any manifest is persisted, so the executor
    # never writes a manifest claiming PHASE_COMPLETE and only then discovers that its assurance
    # check fails. The frozen failure semantics are unchanged — a violation is fatal to the phase.
    done = {e["case_id"] for e in completed}
    expected_pairs = vf.derive_expected_replicates(phase, eligible, matrix)
    replicates = vf.build_execution_assurance_entries(base, expected_pairs, done,
                                                      audit_plans=audit_plans)
    vf.validate_execution_assurance_replicates(
        phase, base, terminal, eligible, matrix, replicates, done,
        {e["case_id"] for e in refused}, audit_plans=audit_plans)

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
    # every provider call constructs exactly ONE new artifact: a case record or, for the
    # non-adjudicative tau role only, a diagnostic-attempt failure envelope (erratum PE-92).
    if n_calls != n_new + n_new_env:                      # pragma: no cover - guarded by control
        raise RuntimeError("phase %r made %d provider calls for %d new case records and %d new "
                           "diagnostic envelopes" % (phase, n_calls, n_new, n_new_env))
    execution_counts = {
        # erratum PE-105: the authority artifact costs NO provider call and is no solver row.
        "n_phase_authority_files": 1,
        "phase_authority_write_mode": pa_write_mode,
        # erratum PE-92: the two NEW-artifact classes are counted separately, and
        # n_newly_executed is retained as their exact sum for compatibility.
        "n_new_case_records": n_new,
        "n_new_diagnostic_failure_envelopes": n_new_env,
        "n_reused_case_records": n_reused,
        "n_reused_diagnostic_failure_envelopes": n_reused_env,
        "n_newly_executed": n_new + n_new_env, "n_reused": n_reused + n_reused_env,
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
                                      diagnostic_failed=diagnostic_failed,
                                      phase_authority_file_sha256=pa_sha)
    # PE-75: atomic, no-overwrite / exact-match write. A differing existing manifest is never
    # silently replaced.
    vf._atomic_write_json(base / ("manifest_%s.json" % phase), manifest)
    vf.validate_phase_manifest(phase, base, authority=auth, matrix_rows=matrix,
                               predecessor_records=records,
                               require_production=(provenance_mode == "PRODUCTION"))
    return manifest


def _phase_authority_of(runs_dir, phase):
    """The complete historical authority a phase persisted (erratum PE-93)."""
    doc = vf._load_json(pathlib.Path(runs_dir) / ("manifest_%s.json" % phase),
                        "the %s completion manifest" % phase)
    return doc.get("execution_authority")


def _guarded_result_provider(mask, g, phase, row, tau=None, audit=None, backend="reference"):
    """The ONLY production path to a solve. It refuses unless the phase is on the allowlist."""
    steps = None if audit is None else audit["target_steps"]
    return solve(mask, g, phase, backend=backend, tau=tau, steps=steps,
                 min_steps=(None if audit is None else audit["min_steps"]))


def _process_pool_case_worker(task):
    """Child-side solve only: no authority decision, verdict, manifest, or durable write."""
    started, pid, cid = time.monotonic(), os.getpid(), task["case_id"]
    try:
        row = task["row"]
        mask, _meta, _kind = resolve_row(row)
        audit = task.get("audit")
        result = _guarded_result_provider(
            mask=mask, g=vf.row_forcing(row), phase=row["phase"], row=row,
            tau=row["tau_plus"], audit=audit, backend="reference")
        return pool_engine.success_result(cid, pid, started, time.monotonic(), result)
    except BaseException as exc:
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        return pool_engine.failure_result(cid, pid, started, time.monotonic(), exc)


def _row_dependency_ids(row):
    return tuple(x for x in (row.get("audit_of_case_id"), row.get("replicate_of_case_id")) if x)


def _parallel_progress(event):
    """Operational parent telemetry. It is never persisted or included in a scientific hash."""
    print("RP_D_LC_001B_PARALLEL_PROGRESS " + json.dumps(event, sort_keys=True), flush=True)


def _parallel_geometry_context(row, matrix, base, backend):
    """Resolve one ready row in the parent and reconstruct any frozen base-derived plan."""
    if isinstance(row.get("bridge"), str):
        _refuse_post_freeze(row["phase"])
    mask, meta, kind = resolve_row(row)
    audit_plan = None
    dependency = row.get("audit_of_case_id") or row.get("replicate_of_case_id")
    if dependency:
        base_rec, _ = vf.read_case_record(base, dependency)
        base_row = next((r for r in matrix if r["case_id"] == dependency), None)
        if base_row is None:
            raise ValueError("row %r names a base outside the canonical matrix" % row["case_id"])
        if row.get("audit_of_case_id"):
            vf.assert_audit_compatible(row, base_row)
            base_status = vf.recomputed_case_status(base_rec)
            if base_status != "NORMAL_CONVERGED":
                raise ValueError("audit %r base %r is not NORMAL_CONVERGED"
                                 % (row["case_id"], dependency))
            audit_plan = vf.fixed_step_audit_plan(base_rec["completed_steps"], base_status)
            audit_plan["base_case_id"] = dependency
            audit_plan["base_record_sha256"] = vf.record_hash(base_rec)
        else:
            vf.assert_replicate_compatible(row, base_row)
            # Recompute now rather than trusting the stored identity; the final assurance builder
            # repeats this check from the official records.
            vf.recomputed_payload_sha256(base_rec, base_row)
    g = vf.row_forcing(row)
    cfg = vf.effective_solver_config(row, backend=backend, audit=audit_plan)
    geometry = {"kind": kind, "mask_sha256": meta["mask_sha256"], "S": row["S"],
                "shape": list(meta.get("shape") or mask.shape),
                "bridge": row["bridge"] if isinstance(row["bridge"], dict) else None,
                "state": row["state"], "variant": row["variant"],
                "obstructed": bool(meta.get("obstructed"))}
    return {"mask": mask, "meta": meta, "kind": kind, "audit": audit_plan,
            "g": g, "cfg": cfg, "geometry": geometry}


def _parallel_record_entry(row, rec, path, how, sci, audit_plan, state):
    entry = {"case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
             "artifact_kind": "CASE_RECORD", "record_path": path.name,
             "write_mode": how, "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
             "status": rec["status"]}
    verdict = vf.case_decision_verdict(
        row, sci, vf.recomputed_case_status(rec, audit=audit_plan))
    entry["scientific_role"] = verdict["scientific_role"]
    if not verdict["pass"]:
        entry["reason"] = verdict["reason"]
    state[verdict["ledger"]].append(entry)
    if verdict["effect"] == "STOPS_THE_PHASE" and state["terminal"] == "PHASE_COMPLETE":
        state["terminal"] = ("PHASE_STOPPED_UNCONVERGED"
                             if verdict["reason"] == "NORMAL_UNCONVERGED"
                             else "PHASE_STOPPED_INVALID_CASE")
        state["stop_reason"] = verdict["reason"]
    return verdict


def _parallel_prepare_row(row, state):
    """Parent-only exact resume and task construction; returns None for an exact reuse."""
    ctx = _parallel_geometry_context(
        row, state["matrix"], state["base"], state["backend"])
    if ctx["audit"] is not None:
        state["audit_plans"][row["case_id"]] = ctx["audit"]
    vf.assert_no_coexisting_artifacts(state["base"], row["case_id"])
    role = vf.row_scientific_role(row)
    envelope_eligible = role in vf.DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES
    existing = vf.load_resumable_case_record(
        state["base"], row, state["auth"], state["phase"], state["pre_sha"],
        ctx["geometry"], provenance_mode=state["provenance_mode"], audit=ctx["audit"],
        phase_authority_file_sha256=state["pa_sha"])
    existing_env = None
    if existing is None and envelope_eligible:
        existing_env = vf.load_resumable_diagnostic_failure(
            state["base"], row, state["auth"], state["phase"], state["pre_sha"],
            ctx["geometry"], provenance_mode=state["provenance_mode"], audit=ctx["audit"],
            phase_authority_file_sha256=state["pa_sha"])
    if existing_env is not None:
        env, path = existing_env
        state["n_reused_env"] += 1
        state["diagnostic_failed"].append({
            "case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
            "artifact_kind": "DIAGNOSTIC_FAILURE_ENVELOPE", "record_path": path.name,
            "write_mode": "REUSED_EXACT_MATCH",
            "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "status": env["status"], "scientific_role": env["scientific_role"],
            "reason": env["failure_code"], "failure_stage": env["failure_stage"]})
        return None
    if existing is not None:
        rec, path = existing
        state["n_reused"] += 1
        _parallel_record_entry(row, rec, path, "REUSED_EXACT_MATCH", rec["scientific"],
                               ctx["audit"], state)
        return None
    state["contexts"][row["case_id"]] = ctx
    return {"case_id": row["case_id"], "row": row, "audit": ctx["audit"]}


def _parallel_consume_result(row, worker_result, state):
    """Convert one raw worker result through the serial official scientific/record path."""
    ctx = state["contexts"].pop(row["case_id"])
    role = vf.row_scientific_role(row)
    envelope_eligible = role in vf.DIAGNOSTIC_ENVELOPE_ELIGIBLE_ROLES
    try:
        if not worker_result["success"]:
            failure = worker_result["failure"]
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_PROVIDER_EXCEPTION", "PROVIDER_CALL",
                exc=RuntimeError("worker row-local %s: %s"
                                 % (failure.get("type"), failure.get("message"))))
        res, sci = _attempt_case(
            lambda **_kw: worker_result["payload"], ctx["mask"], ctx["meta"], ctx["g"],
            state["phase"], row, ctx["kind"], ctx["audit"], state["backend"])
        try:
            payload = vf.scientific_payload_hash(
                ctx["cfg"], sci, ctx["meta"]["mask_sha256"])
            rec = vf.make_case_record(
                row, state["auth"], state["pre_sha"], ctx["geometry"], sci,
                completed_steps=_exact_steps(res["steps"]), run_mode=row["run_mode"],
                audit=ctx["audit"], provenance_mode=state["provenance_mode"],
                scientific_payload_sha256=payload,
                phase_authority_file_sha256=state["pa_sha"])
        except vf.DIAGNOSTIC_NEVER_CAUGHT:
            raise
        except vf.DiagnosticAttemptFailed:
            raise
        except vf.NonFiniteValue as exc:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_RESULT_NONFINITE", "RECORD_CONSTRUCTION", exc=exc)
        except (TypeError, ValueError) as exc:
            raise vf.DiagnosticAttemptFailed(
                "DIAGNOSTIC_SCIENTIFIC_EXTRACTION_FAILED", "RECORD_CONSTRUCTION", exc=exc)
    except vf.DiagnosticAttemptFailed as failure:
        if not envelope_eligible:
            if failure.exc is not None:
                raise failure.exc
            raise ValueError("adjudicative row %r failed at %s: %s"
                             % (row["case_id"], failure.stage, failure.detail))
        env = vf.make_diagnostic_failure_envelope(
            row, state["auth"], state["pre_sha"], ctx["geometry"], failure,
            provenance_mode=state["provenance_mode"], audit=ctx["audit"],
            traceback_text=_failure_traceback(failure),
            phase_authority_file_sha256=state["pa_sha"])
        path, how = vf.write_diagnostic_failure_envelope(state["base"], env)
        state["n_new_env"] += 1
        state["diagnostic_failed"].append({
            "case_id": row["case_id"], "row_sha256": vf.row_sha256(row),
            "artifact_kind": "DIAGNOSTIC_FAILURE_ENVELOPE", "record_path": path.name,
            "write_mode": how, "record_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "status": env["status"], "scientific_role": env["scientific_role"],
            "reason": env["failure_code"], "failure_stage": env["failure_stage"]})
        return True
    vf.validate_case_record(
        rec, row=row, authority=state["auth"], phase=state["phase"],
        expected_predecessors=state["pre_sha"], phase_authority_file_sha256=state["pa_sha"],
        geometry=ctx["geometry"], audit=ctx["audit"],
        provenance_mode=state["provenance_mode"])
    path, how = vf.write_case_record(state["base"], rec)
    state["n_new"] += 1
    verdict = _parallel_record_entry(row, rec, path, how, sci, ctx["audit"], state)
    return verdict["effect"] != "STOPS_THE_PHASE"


def _run_parallel_waves(canonical_rows, jobs, worker, prepare, consume, initially_complete=(),
                        progress=None, phase=None):
    """Private parent seam: readiness, exact resume, complete waves, canonical consumption."""
    rows = list(canonical_rows)
    order = {r["case_id"]: i for i, r in enumerate(rows)}
    pending = {r["case_id"]: r for r in rows}
    complete = set(initially_complete)
    refused = []
    counts = {"ready_rows": 0, "reused_rows": 0, "newly_dispatched_rows": 0,
              "completed_worker_results": 0, "failed_worker_results": 0,
              "waves_dispatched": 0, "worker_calls": 0}
    phase_started = time.monotonic()
    with pool_engine.DeterministicWavePool(jobs, worker) as pool:
        while pending:
            ready = [r for r in rows if r["case_id"] in pending
                     and set(_row_dependency_ids(r)) <= complete]
            if not ready:
                raise RuntimeError("parallel row dependency graph is blocked")
            counts["ready_rows"] += len(ready)
            tasks, selected = [], []
            for row in ready:
                task = prepare(row)
                if task is None:
                    complete.add(row["case_id"])
                    pending.pop(row["case_id"])
                    counts["reused_rows"] += 1
                    continue
                tasks.append(task)
                selected.append(row)
                if len(tasks) == jobs:
                    break
            if not tasks:
                continue
            wave_started = time.monotonic()
            results = pool.run_wave(tasks)
            counts["waves_dispatched"] += 1
            counts["newly_dispatched_rows"] += len(tasks)
            keep_going = True
            pairs = sorted(zip(selected, results), key=lambda x: order[x[0]["case_id"]])
            for row, result in pairs:
                counts["completed_worker_results"] += int(result["success"])
                counts["failed_worker_results"] += int(not result["success"])
                keep_going = bool(consume(row, result)) and keep_going
                complete.add(row["case_id"])
                pending.pop(row["case_id"])
            if not keep_going:
                refused = [r["case_id"] for r in rows if r["case_id"] in pending]
            if progress is not None:
                progress({
                    "phase": phase, "jobs": jobs, "execution_mode": "PROCESS_POOL_REFERENCE",
                    "wave_index": counts["waves_dispatched"], "wave_case_count": len(tasks),
                    "wave_case_ids": [row["case_id"] for row in selected],
                    "completed_worker_count": counts["completed_worker_results"],
                    "failed_worker_count": counts["failed_worker_results"],
                    "reused_rows": counts["reused_rows"], "refused_rows": len(refused),
                    "elapsed_phase_seconds": time.monotonic() - phase_started,
                    "elapsed_wave_seconds": time.monotonic() - wave_started,
                    "cumulative_worker_calls": pool.worker_calls,
                    "eligible_to_continue": bool(keep_going),
                })
            if not keep_going:
                break
        counts["worker_calls"] = pool.worker_calls
    if counts["worker_calls"] != counts["newly_dispatched_rows"]:
        raise RuntimeError("worker-call accounting differs from newly dispatched rows")
    return {"accounting": counts, "refused_after_parallel_stop": refused,
            "completed_case_ids": [r["case_id"] for r in rows if r["case_id"] in complete]}


def _orchestrate_parallel(phase, base, auth, manifests, records, jobs,
                          provenance_mode="PRODUCTION", worker=_process_pool_case_worker,
                          progress=_parallel_progress):
    """Official PROCESS_POOL_V1 parent path. The public gate remains source-deauthorized."""
    matrix = vf.execution_matrix()["rows"]
    universe = vf.phase_universe(phase, matrix)
    eligible, adaptive = vf.derive_expected_rows(phase, matrix, predecessor_records=records)
    elig_ids = {r["case_id"] for r in eligible}
    pre_sha = {k: hashlib.sha256((base / ("manifest_%s.json" % k)).read_bytes()).hexdigest()
               for k in manifests if (base / ("manifest_%s.json" % k)).exists()}
    pa_doc = vf.make_phase_authority_document(
        phase, auth, pre_sha, provenance_mode=provenance_mode)
    pa_path, pa_write_mode = vf.write_phase_authority(base, pa_doc)
    pa_sha = hashlib.sha256(pa_path.read_bytes()).hexdigest()
    vf.validate_phase_authority_document(
        pa_doc, phase, require_production=(provenance_mode == "PRODUCTION"),
        expected_current_authority=auth,
        expected_predecessors=pre_sha)
    mpath = base / ("manifest_%s.json" % phase)
    if mpath.exists():
        return vf.validate_phase_manifest(
            phase, base, authority=auth, matrix_rows=matrix, predecessor_records=records,
            require_production=(provenance_mode == "PRODUCTION"))

    state = {"phase": phase, "base": base, "auth": auth, "matrix": matrix,
             "backend": "reference", "provenance_mode": provenance_mode, "pre_sha": pre_sha,
             "pa_sha": pa_sha, "contexts": {}, "audit_plans": {},
             "completed": [], "failed": [], "diagnostic_completed": [],
             "diagnostic_failed": [], "terminal": "PHASE_COMPLETE", "stop_reason": None,
             "n_new": 0, "n_reused": 0, "n_new_env": 0, "n_reused_env": 0}
    refused = [{"case_id": r["case_id"], "row_sha256": vf.row_sha256(r),
                "reason": "ADAPTIVELY_INELIGIBLE"}
               for r in universe if r["case_id"] not in elig_ids]
    scheduled = [r for r in universe if r["case_id"] in elig_ids]
    def emit_progress(event):
        event.update({
            "newly_persisted_records": state["n_new"],
            "newly_persisted_diagnostic_envelopes": state["n_new_env"],
            "reused_records": state["n_reused"],
            "reused_diagnostic_envelopes": state["n_reused_env"],
            "failed_rows": len(state["failed"]),
            "diagnostic_failures": len(state["diagnostic_failed"]),
        })
        if progress is not None:
            progress(event)
    wave_result = _run_parallel_waves(
        scheduled, jobs, worker,
        lambda row: _parallel_prepare_row(row, state),
        lambda row, result: _parallel_consume_result(row, result, state),
        progress=emit_progress, phase=phase)
    stopped = set(wave_result["refused_after_parallel_stop"])
    refused.extend({"case_id": r["case_id"], "row_sha256": vf.row_sha256(r),
                    "reason": "REFUSED_AFTER_PHASE_STOP"}
                   for r in universe if r["case_id"] in stopped)
    # Preserve canonical ledger and refusal ordering independent of wave return order.
    order = {r["case_id"]: i for i, r in enumerate(universe)}
    for key in ("completed", "failed", "diagnostic_completed", "diagnostic_failed"):
        state[key].sort(key=lambda entry: order[entry["case_id"]])
    refused.sort(key=lambda entry: order[entry["case_id"]])

    done = {entry["case_id"] for entry in state["completed"]}
    expected_pairs = vf.derive_expected_replicates(phase, eligible, matrix)
    replicates = vf.build_execution_assurance_entries(
        base, expected_pairs, done, audit_plans=state["audit_plans"])
    vf.validate_execution_assurance_replicates(
        phase, base, state["terminal"], eligible, matrix, replicates, done,
        {entry["case_id"] for entry in refused}, audit_plans=state["audit_plans"])
    phase_science = None
    if phase in vf.PHASE_AGGREGATE_SCIENCE:
        phase_records = {cid: vf.read_case_record(base, cid)[0] for cid in sorted(done)}
        phase_science = vf.PHASE_AGGREGATE_SCIENCE[phase](phase_records)
    counts = wave_result["accounting"]
    if counts["worker_calls"] != state["n_new"] + state["n_new_env"]:
        raise RuntimeError("parallel worker calls do not equal newly persisted artifacts")
    execution_counts = {
        "n_phase_authority_files": 1, "phase_authority_write_mode": pa_write_mode,
        "n_new_case_records": state["n_new"],
        "n_new_diagnostic_failure_envelopes": state["n_new_env"],
        "n_reused_case_records": state["n_reused"],
        "n_reused_diagnostic_failure_envelopes": state["n_reused_env"],
        "n_newly_executed": state["n_new"] + state["n_new_env"],
        "n_reused": state["n_reused"] + state["n_reused_env"],
        "n_provider_calls": counts["worker_calls"], "n_worker_calls": counts["worker_calls"],
        "n_waves": counts["waves_dispatched"], "n_completed": len(state["completed"]),
        "n_failed": len(state["failed"]), "n_refused": len(refused),
        "n_diagnostic_completed": len(state["diagnostic_completed"]),
        "n_diagnostic_failed": len(state["diagnostic_failed"])}
    manifest = vf.make_phase_manifest(
        phase, universe, eligible, state["completed"], refused, state["failed"], auth, pre_sha,
        adaptive, state["terminal"], state["stop_reason"], provenance_mode=provenance_mode,
        replicates=replicates, phase_science=phase_science, execution_counts=execution_counts,
        diagnostic_completed=state["diagnostic_completed"],
        diagnostic_failed=state["diagnostic_failed"], phase_authority_file_sha256=pa_sha)
    vf._atomic_write_json(mpath, manifest)
    vf.validate_phase_manifest(
        phase, base, authority=auth, matrix_rows=matrix, predecessor_records=records,
        require_production=(provenance_mode == "PRODUCTION"))
    return manifest


def run_phase(mode, out_dir=None, backend="reference", runs_dir=None, jobs=1):
    if mode not in MODES:
        raise ValueError("unknown mode %r; expected one of %r" % (mode, MODES))
    pool_engine.validate_jobs(jobs)
    if backend not in vf.SUPPORTED_BACKENDS:
        raise ValueError("backend %r is not supported; only %r exists. A backend argument is "
                         "never accepted and then silently routed to the reference solver."
                         % (backend, vf.SUPPORTED_BACKENDS))
    if mode == "plan":
        # the PLAN mode reads the canonical matrix and writes nothing, so it needs no output path
        return vf.execution_matrix()
    # erratum PE-114: there is NO default. Every non-plan mode -- P0, P1a, P1b, P2a, P2b and
    # eventually P3/P4 -- requires an explicit runs directory outside the repository. The
    # superseded fallback was REPO_ROOT / vf.RUNS_REL, i.e. docs/analysis/rp_d_lc_001b/runs, which
    # the tracked .gitignore does not exclude, so P0 dirtied the worktree whose cleanliness P1a's
    # own authority then required.
    rd = runs_dir if runs_dir is not None else out_dir
    return execute_phase(mode, rd, backend=backend, jobs=jobs)


def _test_only_execute(phase, runs_dir, provider, authority, manifests=None, records=None,
                       backend="reference"):
    """PRIVATE test seam (erratum PE-34).

    Not reachable from the production API or the CLI. Every record it writes carries
    ``provenance_mode = "TEST_ONLY"``, and the production manifest and freeze validators reject
    those records, so a synthetic pipeline can never masquerade as evidence.
    """
    # erratum PE-94: the authority must be the one for THIS stage. Production obtains it from
    # the gate; the seam is handed one, and reusing an earlier phase's would assert that a
    # stage-P0 authority produced a P1a record.
    if authority.get("stage") != phase:
        raise ValueError(
            "the TEST_ONLY seam was given a stage-%r authority for phase %r; each phase is "
            "executed under its own stage-correct authority (erratum PE-94)"
            % (authority.get("stage"), phase))
    # erratum PE-114: TEST_ONLY may use a temporary directory, but it goes through the SAME pure
    # validator, so the seam and production never diverge on how the bundle is resolved.
    base = vf.validate_production_runs_dir(runs_dir, require_production=False, create=True)
    return _orchestrate(phase, base, authority, manifests or {}, records or {},
                        provider, backend, "TEST_ONLY")


def _test_only_execute_parallel(phase, runs_dir, worker, authority, jobs=4, manifests=None,
                                records=None, progress=None):
    """PRIVATE fake-worker seam for official parent integration tests; never production evidence."""
    if authority.get("stage") != phase:
        raise ValueError("parallel TEST_ONLY authority stage differs from phase")
    expected_engine = pool_engine.execution_engine_identity(jobs)
    if authority.get("execution_engine") != expected_engine:
        raise ValueError("parallel TEST_ONLY authority does not bind the requested engine/jobs")
    base = vf.validate_production_runs_dir(runs_dir, require_production=False, create=True)
    return _orchestrate_parallel(
        phase, base, authority, manifests or {}, records or {}, jobs,
        provenance_mode="TEST_ONLY", worker=worker, progress=progress)


#: The exact keys ``--mode plan`` prints. Kept OUT of the thin-CLI pragma and asserted by test:
#: the superseded C4 form named ``planned_pressure_plane_diagnostics``, a key that never existed
#: in the matrix, so the documented command raised KeyError and nothing caught it.
PLAN_SUMMARY_KEYS = ("n_rows", "planned_normal_solves", "planned_fixed_step_audits",
                     "planned_pressure_plane_diagnostic_rows", "planned_solver_invocations",
                     # erratum PE-78: the role-resolved counts are reported SEPARATELY, so a
                     # non-adjudicative diagnostic is never read as a decision-bearing solve.
                     "decision_bearing_rows", "decision_bearing_normal_solves",
                     "decision_bearing_fixed_step_audits", "tau_diagnostic_rows",
                     "execution_assurance_rows", "mandatory_decision_bearing_rows",
                     "mandatory_minimum", "adaptive_maximum", "refused_after_earliest_stop",
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
    # erratum PE-124 §9.2: the plan's authorization state is DERIVED from the same strictly parsed
    # committed driver source the authority reads, not restated from this module's imported
    # constants. The two are then required to agree, so a live checkout whose imported module and
    # tracked source have drifted apart is reported rather than silently trusted.
    authz = vf.committed_authorization_status()
    if (tuple(authz["authorised_solving_phases"]) != tuple(AUTHORISED_SOLVING_PHASES)
            or tuple(authz["authorised_assembly_phases"]) != tuple(AUTHORISED_ASSEMBLY_PHASES)
            or bool(authz["post_freeze_executor_ready"]) != bool(POST_FREEZE_EXECUTOR_READY)):
        raise vf.SourceAuthorizationError(
            "the imported driver constants (%r / %r / %r) differ from the tracked driver source "
            "(%r / %r / %r); the plan may not report an authorization state the committed source "
            "does not declare (erratum PE-124)"
            % (AUTHORISED_SOLVING_PHASES, AUTHORISED_ASSEMBLY_PHASES, POST_FREEZE_EXECUTOR_READY,
               authz["authorised_solving_phases"], authz["authorised_assembly_phases"],
               authz["post_freeze_executor_ready"]))
    out.update(authz)
    return out


def main(argv=None):                                             # pragma: no cover - thin CLI
    ap = argparse.ArgumentParser(description="RP-D-LC-001b driver (PRE-EXECUTION: refuses)")
    ap.add_argument("--mode", required=True, choices=list(MODES))
    ap.add_argument("--backend", default="reference",
                    help="only 'reference' exists; anything else fails before execution")
    ap.add_argument("--output", default=None,
                    help="REQUIRED for every mode except 'plan': an explicit ABSOLUTE runs "
                         "directory OUTSIDE the repository. There is no default — the production "
                         "authority requires a clean worktree, so runtime output may never be "
                         "written beneath it (erratum PE-114)")
    ap.add_argument("--jobs", type=int, default=pool_engine.DEFAULT_REFERENCE_WORKERS,
                    help="reference workers, 1..32; jobs=1 preserves the serial path")
    a = ap.parse_args(argv)
    try:
        res = run_phase(a.mode, out_dir=a.output, backend=a.backend, jobs=a.jobs)
    except (ExecutionNotAuthorised, PostFreezeExecutorNotReady, vf.FreezeMissing,
            vf.ManifestMissing, vf.RunsDirectoryPolicyError, vf.ExecutionAuthorityError,
            vf.DesignBlocked, ValueError) as exc:
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

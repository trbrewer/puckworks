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
import json
import pathlib

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
          **kw):
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
        min_steps=vf.MIN_STEPS, verbose=False, return_fields=tuple(fields), **kw)


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
        lateral_driver_is_zero = (meta["variant"] == "identical")
    axial_mass_scale = by["x_meas_a"]["sum_rho_ux"]
    rec = {
        "stage": stage, "S": meta["S"], "g": float(g), "state": meta["state"],
        "variant": meta["variant"], "swapped": meta["swapped"],
        "perturbation": meta["perturbation"], "bridge": meta["bridge"],
        "mask_sha256": meta["mask_sha256"],
        "steps": int(res["steps"]), "converged": bool(res["steps"] < vf.MAX_STEPS),
        "named_axial_planes": named, "conservation_planes": cons,
        "lane_planes": ln, "transverse_planes": tr,
        "conservation": vf.conservation_residuals(cons, named_plane_records=named + ln),
        "transverse_conservation": vf.transverse_conservation(
            meta["state"], tr, axial_mass_scale,
            lateral_driver_is_zero=bool(lateral_driver_is_zero)),
        "mach": vf.mach_record(res["ux"], res["uy"], res["uz"], mask),
        # the inverse's observables, formed from VOLUME flux only, kept explicitly labelled
        "Q_volume": by["x_meas_a"]["sum_ux"],
        "q1_volume": by["x_meas_a_lane1"]["sum_ux"],
        "q2_volume": by["x_meas_a_lane2"]["sum_ux"],
        "Q_mass_diagnostic": axial_mass_scale,
        "dP": by["x_node_in"]["p_mean"] - by["x_node_out"]["p_mean"],
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

def run_phase(mode, out_dir=None, backend="reference", runs_dir=None):
    if mode not in MODES:
        raise ValueError("unknown mode %r; expected one of %r" % (mode, MODES))
    if mode == "plan":
        return vf.execution_matrix()
    if mode in SOLVING_MODES:
        require_execution_authorisation(mode, backend=backend, runs_dir=runs_dir)
        raise ExecutionNotAuthorised(                             # pragma: no cover - unreached
            "phase %r is authorised but no runner is implemented at this head" % (mode,))
    if mode in ("P2b", "freeze"):
        raise ExecutionNotAuthorised(
            "the bridge freeze is built from REAL hashed P0/P1/P2a records, none of which "
            "exist. %s" % AUTHORISATION_NOTE)
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

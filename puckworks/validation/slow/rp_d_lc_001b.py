"""RP-D-LC-001b — slow driver SCAFFOLD.

NO LATTICE-BOLTZMANN SOLVE HAS BEEN PERFORMED FOR THIS TRANCHE, AND THIS MODULE REFUSES TO
PERFORM ONE. Execution is authorised only from an expressly approved frozen head: until then
``EXECUTION_AUTHORISED`` is False and every solving mode raises ``ExecutionNotAuthorised``.
Independently of that switch, the primary mirror phase P3 also refuses to start unless the
bridge freeze artifact exists AND is bound to the exact configuration about to run.

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

#: Flipped only by an explicit, reviewed commit at the approved head. It is deliberately a
#: source-level constant rather than a flag or an environment variable: starting the primary
#: computation must be a reviewable change to the repository, not a command-line choice.
EXECUTION_AUTHORISED = False

AUTHORISATION_NOTE = (
    "RP-D-LC-001b is PRE-EXECUTION. The protocol, the corrected fixture, the conserved-quantity "
    "contract, the similarity law, the negative-control gate and the reachable-set margin are "
    "frozen and awaiting substantive scientific review at an exact head. No solve may run before "
    "that review."
)

#: Every mode that would invoke the solver, in the only order they may run.
SOLVING_MODES = ("p0", "p1", "p2", "p3", "armj")
#: Modes that do no solving at all.
NON_SOLVING_MODES = ("freeze", "assemble", "plan")
MODES = SOLVING_MODES + NON_SOLVING_MODES

#: Phases whose output would reveal a primary mirror observable. These carry the freeze gate.
FREEZE_GATED_MODES = ("p3", "armj")

#: The macroscopic fields the eventual solve must request. ``rho`` is needed for BOTH the
#: pressure normalisation and the density-weighted mass flux; ``uy`` for the transverse bridge
#: flux. No solver change is required: these are already in lb_reference.EXPORTABLE_FIELDS.
REQUIRED_FIELDS = ("rho", "uy")


class ExecutionNotAuthorised(RuntimeError):
    """Raised by every solving mode while the tranche is pre-execution."""


def _refuse(mode):
    raise ExecutionNotAuthorised(
        "mode %r would run an RP-D-LC-001b lattice-Boltzmann solve, which is NOT AUTHORISED. %s"
        % (mode, AUTHORISATION_NOTE))


def solve(mask, g, backend="reference", tau=None, fields=REQUIRED_FIELDS, steps=None, **kw):
    """The single solver call site. It refuses while the tranche is pre-execution, so no code
    path in this module can reach the kernel by accident."""
    if not EXECUTION_AUTHORISED:
        _refuse("solve")
    from puckworks.models.brewer2026 import lb_reference          # pragma: no cover - unreached
    return lb_reference.solve(                                    # pragma: no cover - unreached
        mask, g=g, tau_plus=(vf.TAU_PLUS if tau is None else tau),
        max_steps=(vf.MAX_STEPS if steps is None else steps), check=vf.CHECK, rtol=vf.RTOL,
        min_steps=vf.MIN_STEPS, verbose=False, return_fields=tuple(fields), **kw)


# ------------------------------------------------------------------------------------------
# Record construction — pure, solver-free, and therefore testable in CI with synthetic fields.
# ------------------------------------------------------------------------------------------

def axial_records(res, mask, meta, g):
    """Every frozen axial plane's compact record, in frozen order."""
    ux, rho = res["ux"], res["rho"]
    out = []
    named = (("x_node_in", meta["x_node_in"]), ("x_meas_in", meta["x_meas_in"]),
             ("x_meas_b", meta["x_meas_b"]), ("x_meas_a", meta["x_meas_a"]),
             ("x_node_out", meta["x_node_out"]))
    for pid, x in named:
        out.append(vf.axial_plane_record(pid, x, ux, rho, mask, g))
    for i, x in enumerate(meta["axial_conservation_planes"]):
        out.append(vf.axial_plane_record("cons_%d" % i, x, ux, rho, mask, g))
    return out


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


def transverse_records(res, mask, meta):
    """The four frozen transverse bridge-control planes. Empty for a fixture with no bridge."""
    if meta["bridge"] is None:
        return []
    uy, rho = res["uy"], res["rho"]
    fx, fz = meta["bridge_x"], meta["bridge_z"]
    out = []
    for pid in ("y_portA_in", "y_duct_a", "y_duct_b", "y_portB_out"):
        out.append(vf.transverse_plane_record(pid, meta[pid], uy, rho, mask, fx, fz))
    return out


def case_record(res, mask, meta, g, stage):
    """The complete compact record for one solved case. Large field arrays are NEVER retained;
    only the frozen plane records and scalars are."""
    ax = axial_records(res, mask, meta, g)
    ln = lane_records(res, mask, meta, g)
    tr = transverse_records(res, mask, meta)
    by = {r["plane_id"]: r for r in ax + ln}
    rec = {
        "stage": stage, "S": meta["S"], "g": float(g), "state": meta["state"],
        "variant": meta["variant"], "swapped": meta["swapped"],
        "perturbation": meta["perturbation"], "bridge": meta["bridge"],
        "mask_sha256": meta["mask_sha256"],
        "steps": int(res["steps"]), "converged": bool(res["steps"] < vf.MAX_STEPS),
        "axial_planes": ax, "lane_planes": ln, "transverse_planes": tr,
        "conservation": vf.conservation_residuals(ax, tr),
        # the inverse's observables, formed from VOLUME flux only, kept explicitly labelled
        "Q_volume": by["x_meas_a"]["sum_ux"],
        "q1_volume": by["x_meas_a_lane1"]["sum_ux"],
        "q2_volume": by["x_meas_a_lane2"]["sum_ux"],
        "Q_mass_diagnostic": by["x_meas_a"]["sum_rho_ux"],
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

def run_phase(mode, out_dir=None, backend="reference"):
    if mode not in MODES:
        raise ValueError("unknown mode %r; expected one of %r" % (mode, MODES))
    if mode in FREEZE_GATED_MODES:
        # Fail-closed and BEFORE the authorisation check, so the freeze gate is demonstrably
        # load-bearing rather than shadowed by the pre-execution switch.
        vf.require_freeze(mode)
    if mode in SOLVING_MODES:
        _refuse(mode)
    if mode == "plan":
        return vf.execution_matrix()
    if mode == "freeze":
        raise ExecutionNotAuthorised(
            "the bridge freeze is written from P1 and P2 output, neither of which exists. %s"
            % AUTHORISATION_NOTE)
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
    except (ExecutionNotAuthorised, vf.FreezeMissing) as exc:
        print("REFUSED: %s" % exc)
        return 2
    print(json.dumps({"mode": a.mode, "n_planned_rows": res.get("n_rows")}, indent=2))
    return 0


if __name__ == "__main__":                                       # pragma: no cover
    raise SystemExit(main())

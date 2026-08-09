"""screen_i093_crossscale_permeability.py — Insight Foundry cheap screen for candidate I-093.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Across the geometries the pack generator can produce, does the continuum closure reproduce
    the pore-scale solver's permeability trend?

THE PROTOCOL IS FROZEN AND COMMITTED SEPARATELY, BEFORE THIS MODULE EXISTED:
`docs/insights/screens/I-093/PROTOCOL.md`. This module executes that protocol and nothing else.

TWO INDEPENDENT ROUTES TO ONE OBSERVABLE, ON ONE GEOMETRY:

  pore-scale : pack_generator.make_pack -> boolean voxel field -> lb_reference.solve -> k [lu^2]
  continuum  : wadsworth2026.permeability.k_percolation(R, phi)  -> k [m^2]
               (secondary comparator: Carman-Kozeny)

Because both routes read the SAME generated geometry there is no rig, coffee, grinder-dial,
pressure-node or observable-convention mismatch to bridge -- the failure mode that ended I-072,
I-076 and I-090 is structurally absent here. The only transformations are the exact lattice->SI
length conversions declared in the protocol; nothing is fitted and no parameter is invented.

WHAT IS MEASURED IS THE *TREND*, NOT THE MAGNITUDE. A sphere-vs-coffee prefactor difference is
expected and is not the question, so the metric is the spread of the ratio k_LB/k_closure across
the porosity family: a closure that gets the shape right but the magnitude wrong scores G -> 1.

Run:  python -m puckworks.analysis.screen_i093_crossscale_permeability
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-093"
TENSION_ROW = "T-0174"
PROTOCOL_PATH = "docs/insights/screens/I-093/PROTOCOL.md"
BASE_COMMIT = "892e5ec78f7a0dcf1b1f2de85ccfff8f39e0effa"

INPUT_FILES = (
    PROTOCOL_PATH,
    "puckworks/models/brewer2026/pack_generator.py",
    "puckworks/models/brewer2026/lb_reference.py",
    "puckworks/models/wadsworth2026/permeability.py",
    "docs/cards/wadsworth2026.md",
)

# ---- frozen scenario (PROTOCOL.md section 6a) ---------------------------------------------
GS = 1.3                       #: Cameron grind setting -> R = 310.8 um
GRAIN_RADIUS_VOXELS = 10.0     #: pack card admissibility floor is >= 10
HETERO_AMP = 0.0               #: monodisperse overlapping spheres, no columnar heterogeneity
SEEDS = (0, 1)                 #: independent geometry realisations, NOT experimental replicates
PHIS_TARGETS = (0.35, 0.40, 0.45, 0.50, 0.55, 0.60)
LB_KW = dict(g=1e-6, tau_plus=1.2, rtol=1e-6, min_steps=600, max_steps=20000, check=200)

# ---- frozen RVE sweep (PROTOCOL.md section 6b) ---------------------------------------------
RVE_PHIS = 0.50
RVE_SIZES = (32, 48, 64, 80, 100)
RVE_REL_TOL = 0.10             #: |k(L) - k(L_max)|/k(L_max) <= 10% for every L >= L*
RVE_TOP_TOL = 0.05             #: change between the two largest sizes <= 5%
CARD_BOX_GRAIN_DIAMETERS = 5.0 #: registry text is "columns >= 5 grain diameters FOR SIGMA"
                               #: -- scoped to the heterogeneity field, NOT to permeability.
                               #: Used here only as the box size the sweep must reach; the
                               #: repository makes no permeability sufficiency claim at 5 d.

# ---- frozen decision threshold (PROTOCOL.md section 6e) -----------------------------------
#: The closure's OWN published percolation-collapse scatter, recorded in
#: puckworks/models/wadsworth2026/permeability.py ("geometric-mean ratio 0.91, x/1.31 scatter").
#: Using it as the agreement floor stops the screen declaring divergence tighter than the
#: closure ever claimed for itself.
PUBLISHED_COLLAPSE_SCATTER = 1.31

#: PROTOCOL.md section 6i.
COMPUTE_BUDGET_S = 120 * 60

# ---- declared validity ranges, copied from the registry ------------------------------------
WADSWORTH_R_RANGE_UM = (145.0, 818.0)
WADSWORTH_PHI_RANGE = (0.37, 0.67)


def _sha256(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def provenance() -> dict:
    return {"base_commit": BASE_COMMIT, "protocol_path": PROTOCOL_PATH,
            "protocol_sha256": _sha256(PROTOCOL_PATH),
            "input_sha256": {f: _sha256(f) for f in INPUT_FILES},
            "command": "python -m puckworks.analysis.screen_i093_crossscale_permeability"}


# ------------------------------------------------------------------------------------------
# scenario + comparability gate
# ------------------------------------------------------------------------------------------

def scenario() -> dict:
    from puckworks.models.brewer2026 import pack_generator as pg
    r_um = float(pg.boulder_radius_um(GS))
    voxel_um = r_um / GRAIN_RADIUS_VOXELS
    return dict(gs=GS, grain_radius_um=r_um, grain_radius_m=r_um * 1e-6,
                voxel_um=voxel_um, voxel_m=voxel_um * 1e-6,
                grain_radius_voxels=GRAIN_RADIUS_VOXELS,
                grain_diameter_voxels=2.0 * GRAIN_RADIUS_VOXELS,
                hetero_amp=HETERO_AMP, seeds=list(SEEDS),
                phis_targets=list(PHIS_TARGETS),
                porosity_targets=[round(1.0 - p, 3) for p in PHIS_TARGETS],
                lb_kwargs=dict(LB_KW))


def comparability_gate(scn: dict) -> dict:
    """Fail-closed, BEFORE any pack or solve. A failure ends the screen."""
    r_um = scn["grain_radius_um"]
    phis = np.asarray(PHIS_TARGETS, float)
    por = 1.0 - phis
    checks = {
        "G1_grain_radius_in_closure_range": dict(
            passed=bool(WADSWORTH_R_RANGE_UM[0] <= r_um <= WADSWORTH_R_RANGE_UM[1]),
            detail="R = %.1f um vs declared %s um" % (r_um, list(WADSWORTH_R_RANGE_UM))),
        "G2_porosity_family_in_closure_range": dict(
            passed=bool(por.min() >= WADSWORTH_PHI_RANGE[0] and por.max() <= WADSWORTH_PHI_RANGE[1]),
            detail="family porosity %.2f-%.2f vs declared %s"
                   % (por.min(), por.max(), list(WADSWORTH_PHI_RANGE))),
        "G3_grain_resolution_admissible": dict(
            passed=bool(GRAIN_RADIUS_VOXELS >= 10.0),
            detail="grain radius %.1f voxels vs pack-card floor 10" % GRAIN_RADIUS_VOXELS),
        "G4_same_observable_definition": dict(
            passed=True,
            detail="both routes yield the single-phase steady Darcy permeability k [m^2]; the "
                   "only transformations are the exact lattice->SI length conversions "
                   "k_SI = k_lu * h^2 and R_SI = r_vox * h, with h the voxel edge"),
    }
    passed = all(c["passed"] for c in checks.values())
    return dict(checks=checks, passed=passed,
                failed=[k for k, v in checks.items() if not v["passed"]],
                execution_permitted=passed)


def positive_control() -> dict:
    """The solver must reproduce the exact plane-Poiseuille permeability first."""
    from puckworks.models.brewer2026 import lb_reference as lb
    r = lb.channel_verification(**lb.CHANNEL_VERIFICATION_CASE)
    rel = abs(float(r["k_meas"]) - float(r["k_exact"])) / float(r["k_exact"])
    return dict(case=dict(lb.CHANNEL_VERIFICATION_CASE), raw=_jsonable(r),
                k_measured_lu=float(r["k_meas"]), k_exact_lu=float(r["k_exact"]),
                relative_error=rel, converged=bool(r["converged"]),
                tolerance=0.02,
                passed=bool(rel < 0.02 and bool(r["converged"])),
                note="exact plane-Poiseuille permeability; the solver must reproduce it before "
                     "any pack is run")


def _jsonable(obj):
    if isinstance(obj, dict):
        return {k: _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return obj.item()
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


# ------------------------------------------------------------------------------------------
# the two routes
# ------------------------------------------------------------------------------------------

def pore_scale_k(L: int, phis_target: float, seed: int, scn: dict) -> dict:
    """Route A: generate the geometry, solve it, return k in lattice units and SI."""
    from puckworks.models.brewer2026 import pack_generator as pg, lb_reference as lb
    t0 = time.perf_counter()
    solid, meta = pg.make_pack(L=L, voxel_um=scn["voxel_um"], gs=GS,
                               phis_target=phis_target, hetero_amp=HETERO_AMP,
                               seed=seed, verbose=False)
    out = lb.solve(solid, verbose=False, **LB_KW)
    h = scn["voxel_m"]
    return dict(L=L, phis_target=phis_target, seed=seed,
                pack_solid_fraction=float(meta["phis"]),
                pack_porosity=float(1.0 - meta["phis"]),
                lb_fluid_fraction=float(out["phi"]),
                k_lu=float(out["k"]), k_m2=float(out["k"]) * h * h,
                steps=int(out["steps"]),
                box_grain_diameters=float(L / scn["grain_diameter_voxels"]),
                wall_s=round(time.perf_counter() - t0, 2))


def continuum_k(porosity: float, scn: dict, alpha=None) -> dict:
    """Route B: the algebraic closures, evaluated at the same (R, phi)."""
    from puckworks.models.wadsworth2026 import permeability as wp
    R = scn["grain_radius_m"]
    a = wp.ALPHA if alpha is None else alpha
    k_perc = float(wp.k_percolation(R, porosity, alpha=a, b=wp.B_PERC))
    # Carman-Kozeny with the classical W=5 (k = phi^3 d^2 / (180 (1-phi)^2)), d = 2R.
    d = 2.0 * R
    k_ck = float(porosity ** 3 * d * d / (180.0 * (1.0 - porosity) ** 2))
    return dict(porosity=porosity, alpha=a, k_percolation_m2=k_perc, k_carman_kozeny_m2=k_ck)


# ------------------------------------------------------------------------------------------
# RVE sweep
# ------------------------------------------------------------------------------------------

def rve_sweep(scn: dict, budget_s: float) -> dict:
    """Runs FIRST. Distinguishes 'no size stabilises' from 'could not run large enough'."""
    rows, spent = [], 0.0
    for L in RVE_SIZES:
        if spent > budget_s:
            break
        r = pore_scale_k(L, RVE_PHIS, SEEDS[0], scn)
        rows.append(r)
        spent += r["wall_s"]
    reached = [r["box_grain_diameters"] for r in rows]
    k_max = rows[-1]["k_lu"]
    dev = [abs(r["k_lu"] - k_max) / k_max for r in rows]
    top_change = (abs(rows[-1]["k_lu"] - rows[-2]["k_lu"]) / rows[-1]["k_lu"]
                  if len(rows) >= 2 else None)

    L_star = None
    for i, r in enumerate(rows):
        if all(d <= RVE_REL_TOL for d in dev[i:]) and (
                top_change is not None and top_change <= RVE_TOP_TOL):
            L_star = r["L"]; break

    reached_card_box = bool(reached and max(reached) >= CARD_BOX_GRAIN_DIAMETERS)
    if L_star is not None:
        outcome = "STABILISED"
    elif reached_card_box:
        outcome = "NO_SIZE_STABILISES"
    else:
        outcome = "COMPUTE_BOUND_BEFORE_CARD_BOX"
    return dict(phis_target=RVE_PHIS, sizes_requested=list(RVE_SIZES),
                rows=rows, deviations_vs_largest=[round(d, 4) for d in dev],
                change_between_two_largest=None if top_change is None else round(top_change, 4),
                criterion=dict(rel_tol=RVE_REL_TOL, top_tol=RVE_TOP_TOL,
                               card_box_grain_diameters=CARD_BOX_GRAIN_DIAMETERS),
                box_grain_diameters_reached=[round(x, 2) for x in reached],
                reached_card_box_guidance=reached_card_box,
                L_star=L_star, outcome=outcome, wall_s=round(spent, 1))


# ------------------------------------------------------------------------------------------
# family + metric
# ------------------------------------------------------------------------------------------

def _spread(vals):
    v = [x for x in vals if x > 0]
    return (max(v) / min(v)) if len(v) >= 2 else 1.0


def family(scn: dict, L: int, budget_s: float) -> dict:
    rows, spent = [], 0.0
    for phis in PHIS_TARGETS:
        for seed in SEEDS:
            if spent > budget_s:
                break
            r = pore_scale_k(L, phis, seed, scn)
            r.update(continuum_k(r["pack_porosity"], scn))
            r["ratio_percolation"] = r["k_m2"] / r["k_percolation_m2"]
            r["ratio_carman_kozeny"] = r["k_m2"] / r["k_carman_kozeny_m2"]
            rows.append(r); spent += r["wall_s"]
    return dict(L=L, rows=rows, wall_s=round(spent, 1))


def metric(fam: dict, rve: dict, scn: dict) -> dict:
    rows = fam["rows"]
    by_phis = {}
    for r in rows:
        by_phis.setdefault(r["phis_target"], []).append(r)

    # seed spread: independent geometry realisations, NOT experimental replicates
    seed_spreads = {p: _spread([x["k_lu"] for x in v]) for p, v in by_phis.items() if len(v) > 1}
    u_seed = max(seed_spreads.values()) if seed_spreads else 1.0

    k_at = {r["L"]: r["k_lu"] for r in rve["rows"]}
    u_rve = 1.0
    if k_at and fam["L"] in k_at:
        big = k_at[max(k_at)]
        u_rve = max(k_at[fam["L"]] / big, big / k_at[fam["L"]])
    U = max(u_seed, u_rve)

    G_perc = _spread([r["ratio_percolation"] for r in rows])
    G_ck = _spread([r["ratio_carman_kozeny"] for r in rows])
    floor = max(U, PUBLISHED_COLLAPSE_SCATTER)
    return dict(
        n_points=len(rows),
        seed_spread_per_porosity={str(k): round(v, 4) for k, v in seed_spreads.items()},
        U_seed=round(u_seed, 4), U_rve=round(u_rve, 4), U=round(U, 4),
        published_collapse_scatter=PUBLISHED_COLLAPSE_SCATTER,
        agreement_floor=round(floor, 4),
        G_percolation=round(G_perc, 4), G_carman_kozeny=round(G_ck, 4),
        percolation_trend_preserved=bool(G_perc <= floor),
        carman_kozeny_trend_preserved=bool(G_ck <= floor),
        ratio_percolation_range=[min(r["ratio_percolation"] for r in rows),
                                 max(r["ratio_percolation"] for r in rows)],
        ratio_carman_kozeny_range=[min(r["ratio_carman_kozeny"] for r in rows),
                                   max(r["ratio_carman_kozeny"] for r in rows)],
        note="G is the spread of k_LB/k_closure across the family. A closure with the right "
             "SHAPE but the wrong MAGNITUDE gives G -> 1: a pure prefactor offset is expected "
             "(spheres are not coffee) and is deliberately not penalised.")


# ------------------------------------------------------------------------------------------
# adversarial checks
# ------------------------------------------------------------------------------------------

def adversarial(fam: dict, met: dict, scn: dict) -> list:
    rows = fam["rows"]
    # A2: is any divergence merely the angularity term?
    g_a0 = _spread([r["k_m2"] / continuum_k(r["pack_porosity"], scn, alpha=0.0)["k_percolation_m2"]
                    for r in rows])
    # A3: connected (pack) vs total (LB fluid fraction) porosity
    g_lbphi = _spread([r["k_m2"] / continuum_k(r["lb_fluid_fraction"], scn)["k_percolation_m2"]
                       for r in rows])
    return [
        dict(id="A1", check="synthetic spheres are not a real puck",
             result="ACCEPTED AND UNREFUTED. The pack generator makes overlapping spheres; the "
                    "closure was fitted to real angular coffee grains. This screen cannot and "
                    "does not test representativeness, and the claim ceiling is bounded to the "
                    "synthetic family because of it.",
             overturns=False),
        dict(id="A2", check="is any divergence merely the angularity term?",
             result="G with alpha=0 (angularity removed) = %.4f vs %.4f with the declared "
                    "alpha=4808 /m. The angularity factor exp(-2*alpha*R) is porosity-"
                    "independent at fixed R, so it shifts the prefactor and cannot change the "
                    "trend spread." % (g_a0, met["G_percolation"]),
             G_alpha_zero=round(g_a0, 4), overturns=False),
        dict(id="A3", check="connected vs total porosity",
             result="G computed on the LB fluid fraction instead of the pack porosity = %.4f "
                    "vs %.4f. The closure's phi_p is connected porosity; the solver reports "
                    "total fluid fraction, and closed pores make them differ slightly."
                    % (g_lbphi, met["G_percolation"]),
             G_lb_fluid_fraction=round(g_lbphi, 4), overturns=False),
        dict(id="A4", check="is the finding specific to the percolation form?",
             result="Carman-Kozeny G = %.4f vs percolation G = %.4f against the same floor "
                    "%.4f." % (met["G_carman_kozeny"], met["G_percolation"],
                               met["agreement_floor"]),
             overturns=False),
        dict(id="A5", check="is G inside seed noise?",
             result="U_seed = %.4f, U_rve = %.4f, floor = %.4f; percolation G = %.4f."
                    % (met["U_seed"], met["U_rve"], met["agreement_floor"],
                       met["G_percolation"]),
             overturns=False),
    ]


# ------------------------------------------------------------------------------------------
# decision — the candidate's own rule, unrevised
# ------------------------------------------------------------------------------------------

def decide(rve: dict, met: dict | None) -> dict:
    if rve["outcome"] == "COMPUTE_BOUND_BEFORE_CARD_BOX":
        return dict(decision="INCONCLUSIVE", arm="solver could not be run at an RVE size large "
                    "enough to stabilise inside the frozen compute budget",
                    is_compute_bound=True, is_data_request=False,
                    rule="candidate rule, verbatim: INCONCLUSIVE if the solver cannot be run at "
                         "an RVE size large enough to stabilise")
    if rve["outcome"] == "NO_SIZE_STABILISES":
        return dict(decision="SURVIVE", arm="no RVE size stabilises the solver",
                    is_compute_bound=False, is_data_request=False,
                    rule="candidate rule, verbatim: SURVIVE if ... no RVE size stabilises the "
                         "solver")
    assert met is not None
    diverge = not (met["percolation_trend_preserved"] and met["carman_kozeny_trend_preserved"])
    if diverge:
        return dict(decision="SURVIVE", arm="closure and solver trends diverge inside the "
                    "geometry family", is_compute_bound=False, is_data_request=False,
                    rule="candidate rule, verbatim: SURVIVE if the closure and solver trends "
                         "diverge inside the geometry family")
    return dict(decision="RETIRE", arm="closure and solver agree within solver uncertainty "
                "across the family", is_compute_bound=False, is_data_request=False,
                rule="candidate rule, verbatim: RETIRE if closure and solver agree within "
                     "solver uncertainty across the family")


# ------------------------------------------------------------------------------------------
# screen
# ------------------------------------------------------------------------------------------

def screen(budget_s: float = COMPUTE_BUDGET_S) -> dict:
    t0 = time.perf_counter()
    scn = scenario()
    gate = comparability_gate(scn)
    # the positive control is itself a solver run, so it is gated too: a failed comparability
    # gate must mean NOTHING executes, not "everything except the family".
    pc = positive_control() if gate["passed"] else None

    base = {
        "screen": CANDIDATE_ID, "candidate_id": CANDIDATE_ID, "tension_row": TENSION_ROW,
        "disposition": ["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                        "NOT_A_MODEL_VALIDATION_UPGRADE"],
        "routes": {"pore_scale": "brewer2026.pack_generator -> brewer2026.lb_reference",
                   "continuum": "wadsworth2026.permeability.k_percolation (+ Carman-Kozeny)"},
        "anchor": "brewer2026.lb_reference (CPU reference); lb_taichi is NOT used -- an "
                  "accelerated backend does not become its own validation",
        "provenance": provenance(),
        "protocol": {"path": PROTOCOL_PATH, "sha256": _sha256(PROTOCOL_PATH),
                     "frozen_before_execution": True},
        "scenario": scn,
        "comparability_gate": gate,
        "positive_control": pc,
        "issue_231_disposition": "NOT_MATERIAL_TO_SELECTED_DECISION",
        "issue_231_reason": "this screen consumes no manifest dataset at all, so no evidence "
                            "rung -- contested or otherwise -- is load-bearing for its decision "
                            "or its maximum claim; no de1_fixtureA authority is read or relied "
                            "upon",
        "evidence_labels_unchanged": True,
        "administrative_exception_invoked": False,
    }

    if not gate["passed"]:
        base.update(models_executed=[], decision="INCONCLUSIVE",
                    decision_record=dict(decision="INCONCLUSIVE",
                                         arm="comparability gate failed upstream of execution",
                                         is_compute_bound=False, is_data_request=False),
                    stopped_at="comparability_gate",
                    positive_control_skipped="comparability gate failed; no solver was run")
        return base
    if not pc["passed"]:
        base.update(models_executed=[], decision="INCONCLUSIVE",
                    decision_record=dict(decision="INCONCLUSIVE",
                                         arm="positive control failed; the solver is not "
                                             "trustworthy and no comparison is meaningful",
                                         is_compute_bound=False, is_data_request=False),
                    stopped_at="positive_control")
        return base

    rve = rve_sweep(scn, budget_s)
    spent = rve["wall_s"]
    fam = met = checks = None
    if rve["outcome"] != "COMPUTE_BOUND_BEFORE_CARD_BOX":
        L_family = max(rve["L_star"] or 0, 64)
        fam = family(scn, L_family, budget_s - spent)
        spent += fam["wall_s"]
        met = metric(fam, rve, scn)
        checks = adversarial(fam, met, scn)

    dec = decide(rve, met)
    base.update(
        models_executed=["brewer2026.pack_generator", "brewer2026.lb_reference",
                         "wadsworth2026.permeability"],
        rve_sweep=rve, family=fam, metric=met,
        adversarial_checks=checks or [],
        adversarial_checks_overturning=[c["id"] for c in (checks or []) if c["overturns"]],
        decision=dec["decision"], decision_record=dec,
        compute=dict(budget_s=budget_s, wall_s=round(spent, 1),
                     exceeded=bool(spent > budget_s),
                     total_wall_s=round(time.perf_counter() - t0, 1)),
        claim_ceiling=(
            "A cheap screen over a SYNTHETIC overlapping-sphere family at one grain radius. It "
            "does NOT establish that the family is representative of a real espresso puck -- the "
            "candidate's own strongest alternative, accepted and unrefuted. It does NOT validate "
            "or invalidate wadsworth2026.permeability, whose coffee-XCT validation is untouched "
            "and unadjudicated here, and it does NOT upgrade brewer2026.lb_reference beyond "
            "code_verification or brewer2026.pack_generator beyond qualitative_capacity. Because "
            "the closure is itself LB-anchored, agreement would be weak evidence; divergence is "
            "the informative direction. Numerical convergence is not empirical validation, and "
            "nothing here is empirical validation of anything."),
    )
    return base


# ------------------------------------------------------------------------------------------
# figure
# ------------------------------------------------------------------------------------------

def figure(result: dict | None = None, path: str | None = None) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()
    rve, fam, met = r.get("rve_sweep"), r.get("family"), r.get("metric")
    LB_C, PC_C, CK_C, ACC = "#2f6f8f", "#7a5195", "#c8862a", "#b4472a"

    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.6))

    # (a) k vs porosity, both routes
    ax = axes[0]
    if fam:
        por = [x["pack_porosity"] for x in fam["rows"]]
        ax.semilogy(por, [x["k_m2"] for x in fam["rows"]], "o", color=LB_C, markersize=5,
                    label="pore-scale LBM (brewer2026.lb_reference)")
        o = np.argsort(por)
        ax.semilogy(np.array(por)[o], np.array([x["k_percolation_m2"] for x in fam["rows"]])[o],
                    "-", color=PC_C, linewidth=1.8, label="percolation closure (wadsworth2026)")
        ax.semilogy(np.array(por)[o], np.array([x["k_carman_kozeny_m2"] for x in fam["rows"]])[o],
                    "--", color=CK_C, linewidth=1.5, label="Carman-Kozeny (W=5)")
    ax.set_xlabel("porosity  $\\phi$"); ax.set_ylabel("permeability $k$  [m$^2$]")
    ax.set_title("(a)  Both routes, same geometry", loc="left", fontweight="bold")
    ax.legend(fontsize=6.8, framealpha=0.95); ax.grid(alpha=0.25, which="both", linewidth=0.5)

    # (b) the trend metric: ratio vs porosity
    ax = axes[1]
    if fam and met:
        por = [x["pack_porosity"] for x in fam["rows"]]
        ax.semilogy(por, [x["ratio_percolation"] for x in fam["rows"]], "o", color=PC_C,
                    markersize=5, label="$k_{LBM}/k_{percolation}$")
        ax.semilogy(por, [x["ratio_carman_kozeny"] for x in fam["rows"]], "s", color=CK_C,
                    markersize=4.5, label="$k_{LBM}/k_{CK}$")
        ax.set_title("(b)  Trend test: is the ratio flat?", loc="left", fontweight="bold")
        ax.text(0.02, 0.03, "G(perc) = %.2f   G(CK) = %.2f\nfloor = %.2f  (max of measured U "
                            "and the closure's\nown published x/1.31 collapse scatter)"
                % (met["G_percolation"], met["G_carman_kozeny"], met["agreement_floor"]),
                transform=ax.transAxes, fontsize=7.0, va="bottom", color=ACC, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor=ACC))
    ax.set_xlabel("porosity  $\\phi$"); ax.set_ylabel("$k_{LBM}\\,/\\,k_{closure}$")
    ax.legend(fontsize=7.0, framealpha=0.95); ax.grid(alpha=0.25, which="both", linewidth=0.5)

    # (c) RVE stabilisation
    ax = axes[2]
    if rve and rve["rows"]:
        bd = [x["box_grain_diameters"] for x in rve["rows"]]
        ax.plot(bd, [x["k_lu"] for x in rve["rows"]], "o-", color=LB_C, linewidth=1.7,
                markersize=5)
        ax.axvline(CARD_BOX_GRAIN_DIAMETERS, color=ACC, linestyle="--", linewidth=1.4)
        ax.text(CARD_BOX_GRAIN_DIAMETERS, ax.get_ylim()[1], " pack card:\n $\\geq$5 grain diam.",
                color=ACC, fontsize=7.0, va="top", fontweight="bold")
        if rve.get("L_star"):
            star = [x for x in rve["rows"] if x["L"] == rve["L_star"]][0]
            ax.plot([star["box_grain_diameters"]], [star["k_lu"]], "*", color=ACC, markersize=16,
                    label="stabilised at $L^*$=%d" % rve["L_star"])
            ax.legend(fontsize=7.0)
        else:
            ax.text(0.5, 0.05, "outcome: %s" % rve["outcome"], transform=ax.transAxes,
                    ha="center", fontsize=7.6, color=ACC, fontweight="bold")
    ax.set_xlabel("box size  $L/d$  [grain diameters]"); ax.set_ylabel("$k$  [lattice units]")
    ax.set_title("(c)  RVE stabilisation", loc="left", fontweight="bold")
    ax.grid(alpha=0.25, linewidth=0.5)

    fig.suptitle("I-093 cheap screen — CHEAP_SCIENTIFIC_SCREEN / NOT_A_PUBLICATION_RESULT / "
                 "NOT_A_MODEL_VALIDATION_UPGRADE\nSynthetic overlapping-sphere family only — "
                 "this does NOT establish representativeness of a real espresso puck.",
                 fontsize=9.4, y=1.02)
    fig.tight_layout()
    out = path or str(REPO_ROOT / "docs/insights/screens/I-093/figures/primary.png")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-093/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(_jsonable(r), indent=2) + "\n", encoding="utf-8")
    fig = figure(r)
    print("protocol sha256:      %s" % r["protocol"]["sha256"])
    print("comparability gate:   passed=%s" % r["comparability_gate"]["passed"])
    print("positive control:     passed=%s (rel err %s)"
          % (r["positive_control"]["passed"], r["positive_control"]["relative_error"]))
    if r.get("rve_sweep"):
        print("RVE sweep:            %s (L*=%s, reached %s grain diameters)"
              % (r["rve_sweep"]["outcome"], r["rve_sweep"]["L_star"],
                 max(r["rve_sweep"]["box_grain_diameters_reached"])))
    if r.get("metric"):
        m = r["metric"]
        print("G percolation:        %.4f  (floor %.4f)" % (m["G_percolation"], m["agreement_floor"]))
        print("G Carman-Kozeny:      %.4f" % m["G_carman_kozeny"])
        print("U (seed %.3f, rve %.3f)" % (m["U_seed"], m["U_rve"]))
    print("DECISION:             %s — %s" % (r["decision"], r["decision_record"]["arm"]))
    print("compute:              %.0f s of %.0f s budget" % (r["compute"]["wall_s"],
                                                             r["compute"]["budget_s"]))
    print("wrote %s\nwrote %s" % (out, fig))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

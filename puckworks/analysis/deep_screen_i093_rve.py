"""deep_screen_i093_rve.py — IF-7 deep screen for candidate I-093.

    DEEP_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Frozen protocol: `docs/insights/screens/I-093/DEEP_SCREEN_PROTOCOL.md`, committed before this
module existed.

THE ONE QUESTION: the cheap screen swept box size at a SINGLE seed and concluded that no RVE size
stabilises the solver. Realisation variance at fixed box size is 5-39%, the same order as its 18%
signal, so that conclusion is confounded. This deep screen runs N independent seeds per box size
and restates the stabilisation criterion on ENSEMBLE MEANS against the seed standard error, which
is the only way to separate:

    a real representative-volume requirement   from   single-realisation scatter.

The protocol predeclares BOUNDED_NULL as a first-class outcome: if the means stabilise, the cheap
screen's SURVIVE was driven by an under-powered sweep and the record must say so.

Run:  python -m puckworks.analysis.deep_screen_i093_rve
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import time

import numpy as np

from puckworks.analysis import screen_i093_crossscale_permeability as CHEAP

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
CANDIDATE_ID = "I-093"
DEEP_PROTOCOL_PATH = "docs/insights/screens/I-093/DEEP_SCREEN_PROTOCOL.md"
BASE_COMMIT = CHEAP.BASE_COMMIT

# ---- frozen deep design (DEEP_SCREEN_PROTOCOL.md sections 3-4) -----------------------------
N_SEEDS = 4
DEEP_SEEDS = tuple(range(N_SEEDS))
DEEP_SIZES = (48, 64, 80, 100)          #: L=32 dropped: 1.6 grain diameters is below any RVE
DEEP_PHIS = 0.50
SIGMA_K = 2.0                           #: 2-sigma stabilisation criterion on ensemble means
EXTREME_PHIS = (0.35, 0.60)             #: porosity-dependence check (section 4.2)
EXTREME_SIZES = (64, 100)
TOL_SENSITIVITY = dict(rtol=1e-7, min_steps=2000)   #: section 4.1
TOL_MOVE_LIMIT = 0.01                   #: >1% means the cheap criterion was too loose
COMPUTE_BUDGET_S = 150 * 60


def _sha256(rel: str) -> str:
    return hashlib.sha256((REPO_ROOT / rel).read_bytes()).hexdigest()


def _run(L, phis, seed, scn, lb_kw=None):
    """One (L, phis, seed) pore-scale run. Reuses the cheap screen's frozen route."""
    from puckworks.models.brewer2026 import pack_generator as pg, lb_reference as lb
    t0 = time.perf_counter()
    solid, meta = pg.make_pack(L=L, voxel_um=scn["voxel_um"], gs=CHEAP.GS,
                               phis_target=phis, hetero_amp=CHEAP.HETERO_AMP,
                               seed=seed, verbose=False)
    kw = dict(CHEAP.LB_KW)
    if lb_kw:
        kw.update(lb_kw)
    out = lb.solve(solid, verbose=False, **kw)
    h = scn["voxel_m"]
    return dict(L=L, phis_target=phis, seed=seed,
                pack_porosity=float(1.0 - meta["phis"]),
                k_lu=float(out["k"]), k_m2=float(out["k"]) * h * h,
                steps=int(out["steps"]),
                box_grain_diameters=float(L / scn["grain_diameter_voxels"]),
                wall_s=round(time.perf_counter() - t0, 2))


def _stats(ks):
    a = np.asarray(ks, float)
    n = a.size
    sd = float(a.std(ddof=1)) if n > 1 else 0.0
    return dict(n=int(n), mean=float(a.mean()), sd=sd,
                se=float(sd / np.sqrt(n)) if n > 1 else 0.0,
                spread=float(a.max() / a.min()) if a.min() > 0 else None)


# ------------------------------------------------------------------------------------------
# section 3 — the decisive multi-seed sweep
# ------------------------------------------------------------------------------------------

def multiseed_rve(scn, budget_s):
    rows, spent = [], 0.0
    for L in DEEP_SIZES:
        for seed in DEEP_SEEDS:
            if spent > budget_s:
                break
            r = _run(L, DEEP_PHIS, seed, scn)
            rows.append(r); spent += r["wall_s"]
    per_L = {}
    for L in DEEP_SIZES:
        ks = [r["k_lu"] for r in rows if r["L"] == L]
        if ks:
            per_L[L] = _stats(ks)

    Ls = sorted(per_L)
    Lmax = Ls[-1]
    mmax, semax = per_L[Lmax]["mean"], per_L[Lmax]["se"]

    # frozen criterion: |mean(L) - mean(Lmax)| <= 2*sqrt(SE(L)^2 + SE(Lmax)^2)
    resolved = {}
    for L in Ls:
        d = abs(per_L[L]["mean"] - mmax)
        band = SIGMA_K * float(np.hypot(per_L[L]["se"], semax))
        resolved[L] = dict(delta=d, band=band, within=bool(d <= band),
                           delta_pct=100.0 * d / mmax)
    L_star = None
    for i, L in enumerate(Ls):
        if all(resolved[x]["within"] for x in Ls[i:]):
            L_star = L; break

    # separation statistic between the two largest sizes
    L1, L2 = Ls[-2], Ls[-1]
    denom = float(np.hypot(per_L[L1]["se"], per_L[L2]["se"]))
    R_sep = abs(per_L[L2]["mean"] - per_L[L1]["mean"]) / denom if denom > 0 else float("inf")

    return dict(phis_target=DEEP_PHIS, seeds=list(DEEP_SEEDS), sizes=list(DEEP_SIZES),
                rows=rows, per_L={str(k): v for k, v in per_L.items()},
                criterion=dict(sigma=SIGMA_K,
                               text="|mean(L)-mean(Lmax)| <= 2*sqrt(SE(L)^2+SE(Lmax)^2)"),
                resolved={str(k): v for k, v in resolved.items()},
                L_star=L_star, R_sep=float(R_sep),
                box_grain_diameters={str(L): L / scn["grain_diameter_voxels"] for L in Ls},
                stabilised=bool(L_star is not None),
                wall_s=round(spent, 1))


# ------------------------------------------------------------------------------------------
# section 4 — robustness
# ------------------------------------------------------------------------------------------

def tolerance_sensitivity(scn, budget_s):
    """Was the cheap screen's convergence criterion too loose?"""
    if budget_s <= 0:
        return dict(skipped="budget")
    base = _run(64, DEEP_PHIS, 0, scn)
    tight = _run(64, DEEP_PHIS, 0, scn, lb_kw=TOL_SENSITIVITY)
    move = abs(tight["k_lu"] - base["k_lu"]) / base["k_lu"]
    return dict(case=dict(L=64, phis=DEEP_PHIS, seed=0),
                baseline=base, tightened=dict(TOL_SENSITIVITY, **tight),
                relative_move=float(move), limit=TOL_MOVE_LIMIT,
                cheap_criterion_adequate=bool(move <= TOL_MOVE_LIMIT),
                note="if k moves more than 1%% the cheap screen's rtol/min_steps were too loose "
                     "and every number inherits that numerical-uncertainty term")


def porosity_dependence(scn, budget_s):
    """Is the box-size behaviour porosity-dependent? That is the one way realisation noise
    could fake a porosity-correlated trend."""
    out, spent = {}, 0.0
    for phis in EXTREME_PHIS:
        per_L = {}
        for L in EXTREME_SIZES:
            ks = []
            for seed in DEEP_SEEDS:
                if spent > budget_s:
                    break
                r = _run(L, phis, seed, scn)
                ks.append(r["k_lu"]); spent += r["wall_s"]
            if ks:
                per_L[str(L)] = _stats(ks)
        if len(per_L) == 2:
            a, b = per_L[str(EXTREME_SIZES[0])], per_L[str(EXTREME_SIZES[1])]
            denom = float(np.hypot(a["se"], b["se"]))
            out[str(phis)] = dict(per_L=per_L,
                                  delta_pct=100.0 * abs(b["mean"] - a["mean"]) / b["mean"],
                                  R_sep=float(abs(b["mean"] - a["mean"]) / denom) if denom else None)
    return dict(sizes=list(EXTREME_SIZES), by_phis=out, wall_s=round(spent, 1))


def trend_on_stabilised_means(scn, rve, budget_s):
    """Recompute G from seed-AVERAGED k at the largest affordable box (protocol 4.3)."""
    L = max(int(k) for k in rve["per_L"])
    rows, spent = [], 0.0
    for phis in CHEAP.PHIS_TARGETS:
        ks, por = [], []
        for seed in DEEP_SEEDS[:2]:                       # 2 seeds per porosity at the big box
            if spent > budget_s:
                break
            r = _run(L, phis, seed, scn)
            ks.append(r["k_m2"]); por.append(r["pack_porosity"]); spent += r["wall_s"]
        if not ks:
            continue
        kbar, pbar = float(np.mean(ks)), float(np.mean(por))
        c = CHEAP.continuum_k(pbar, scn)
        rows.append(dict(phis_target=phis, n_seeds=len(ks), porosity=pbar, k_m2_mean=kbar,
                         k_percolation_m2=c["k_percolation_m2"],
                         k_carman_kozeny_m2=c["k_carman_kozeny_m2"],
                         ratio_percolation=kbar / c["k_percolation_m2"],
                         ratio_carman_kozeny=kbar / c["k_carman_kozeny_m2"],
                         seed_spread=(max(ks) / min(ks)) if len(ks) > 1 else 1.0))
    if len(rows) < 2:
        return dict(skipped="insufficient budget", rows=rows, wall_s=round(spent, 1))
    gp = max(r["ratio_percolation"] for r in rows) / min(r["ratio_percolation"] for r in rows)
    gc = max(r["ratio_carman_kozeny"] for r in rows) / min(r["ratio_carman_kozeny"] for r in rows)
    useed = max(r["seed_spread"] for r in rows)
    floor = max(useed, CHEAP.PUBLISHED_COLLAPSE_SCATTER)
    return dict(L=L, rows=rows, G_percolation=float(gp), G_carman_kozeny=float(gc),
                U_seed=float(useed), agreement_floor=float(floor),
                percolation_trend_preserved=bool(gp <= floor),
                carman_kozeny_trend_preserved=bool(gc <= floor),
                cheap_G_percolation=CHEAP_G_PERC, wall_s=round(spent, 1),
                note="G recomputed on SEED-AVERAGED k at the largest box, not on single "
                     "realisations at L=64 as in the cheap screen")


CHEAP_G_PERC = 2.9357        #: from the committed cheap-screen result, for side-by-side reporting


# ------------------------------------------------------------------------------------------
# decision
# ------------------------------------------------------------------------------------------

def decide(rve, tol, trend):
    if rve.get("stabilised"):
        return dict(outcome="BOUNDED_NULL",
                    basis="ensemble means satisfy the frozen 2-sigma stabilisation criterion at "
                          "L* = %s (L/d = %.1f): once realisation noise is averaged the solver "
                          "IS stabilised, so the cheap screen's RVE arm was single-realisation "
                          "scatter produced by an under-powered one-seed sweep"
                          % (rve["L_star"], rve["box_grain_diameters"][str(rve["L_star"])]),
                    cheap_screen_arm_withdrawn=True)
    if rve["R_sep"] > SIGMA_K:
        return dict(outcome="INSIGHT_SURVIVES",
                    basis="ensemble means still fail the stabilisation criterion and the largest "
                          "box-size step is resolved above seed noise (R_sep = %.2f > %.1f): a "
                          "genuine RVE requirement beyond 5 grain diameters exists on this family"
                          % (rve["R_sep"], SIGMA_K),
                    cheap_screen_arm_withdrawn=False)
    return dict(outcome="BOUNDED_NULL",
                basis="ensemble means fail the stabilisation criterion but the largest box-size "
                      "step is NOT resolved above seed noise (R_sep = %.2f <= %.1f): the "
                      "apparent box-size dependence cannot be distinguished from realisation "
                      "scatter, so the cheap screen's RVE arm is not established"
                      % (rve["R_sep"], SIGMA_K),
                cheap_screen_arm_withdrawn=True)


def deep_screen(budget_s=COMPUTE_BUDGET_S):
    t0 = time.perf_counter()
    scn = CHEAP.scenario()
    rve = multiseed_rve(scn, budget_s)
    spent = rve["wall_s"]
    tol = tolerance_sensitivity(scn, budget_s - spent); spent += tol.get("baseline", {}).get("wall_s", 0) + \
        tol.get("tightened", {}).get("wall_s", 0)
    pdep = porosity_dependence(scn, budget_s - spent); spent += pdep["wall_s"]
    trend = trend_on_stabilised_means(scn, rve, budget_s - spent); spent += trend.get("wall_s", 0)
    dec = decide(rve, tol, trend)
    return {
        "screen": CANDIDATE_ID, "kind": "DEEP_SCREEN",
        "disposition": ["DEEP_SCREEN", "NOT_A_PUBLICATION_RESULT",
                        "NOT_A_MODEL_VALIDATION_UPGRADE"],
        "provenance": dict(base_commit=BASE_COMMIT,
                           deep_protocol_path=DEEP_PROTOCOL_PATH,
                           deep_protocol_sha256=_sha256(DEEP_PROTOCOL_PATH),
                           cheap_protocol_sha256=CHEAP._sha256(CHEAP.PROTOCOL_PATH),
                           command="python -m puckworks.analysis.deep_screen_i093_rve"),
        "scenario": scn,
        "multiseed_rve": rve,
        "tolerance_sensitivity": tol,
        "porosity_dependence": pdep,
        "trend_on_stabilised_means": trend,
        "deep_decision": dec,
        "compute": dict(budget_s=budget_s, wall_s=round(spent, 1),
                        exceeded=bool(spent > budget_s),
                        total_wall_s=round(time.perf_counter() - t0, 1)),
        "holdout_claim": None,
        "holdout_note": "nothing is held out and no independent evidence exists: both routes are "
                        "computations on generated geometry, so no holdout claim is made",
        "issue_231_disposition": "NOT_MATERIAL_TO_SELECTED_DECISION",
        "evidence_labels_unchanged": True,
    }


def figure(result=None, path=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or deep_screen()
    rve = r["multiseed_rve"]
    C, ACC = "#2f6f8f", "#b4472a"
    fig, axes = plt.subplots(1, 2, figsize=(10.6, 4.4))

    ax = axes[0]
    Ls = sorted(int(k) for k in rve["per_L"])
    bd = [rve["box_grain_diameters"][str(L)] for L in Ls]
    mean = [rve["per_L"][str(L)]["mean"] for L in Ls]
    se = [rve["per_L"][str(L)]["se"] for L in Ls]
    for L, x in zip(Ls, bd):
        ks = [q["k_lu"] for q in rve["rows"] if q["L"] == L]
        ax.plot([x] * len(ks), ks, "o", color=C, alpha=0.35, markersize=4)
    ax.errorbar(bd, mean, yerr=[SIGMA_K * s for s in se], fmt="s-", color=C, linewidth=1.8,
                capsize=4, markersize=6, label="seed mean $\\pm 2\\,SE$  (N=%d)" % rve["per_L"][str(Ls[0])]["n"])
    ax.axvline(CHEAP.CARD_BOX_GRAIN_DIAMETERS, color=ACC, linestyle="--", linewidth=1.3)
    ax.set_xlabel("box size $L/d$  [grain diameters]"); ax.set_ylabel("$k$  [lattice units]")
    ax.set_title("(a)  Multi-seed RVE: means vs realisations", loc="left", fontweight="bold")
    ax.legend(fontsize=7.2); ax.grid(alpha=0.25, linewidth=0.5)
    ax.text(0.02, 0.03, "$R_{sep}$ = %.2f   L* = %s" % (rve["R_sep"], rve["L_star"]),
            transform=ax.transAxes, fontsize=8, color=ACC, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=ACC))

    ax = axes[1]
    t = r["trend_on_stabilised_means"]
    if t.get("rows"):
        por = [x["porosity"] for x in t["rows"]]
        ax.semilogy(por, [x["ratio_percolation"] for x in t["rows"]], "o-", color="#7a5195",
                    label="$k_{LBM}/k_{percolation}$ (seed-averaged)")
        ax.semilogy(por, [x["ratio_carman_kozeny"] for x in t["rows"]], "s--", color="#c8862a",
                    label="$k_{LBM}/k_{CK}$ (seed-averaged)")
        ax.set_title("(b)  Trend on seed-averaged means", loc="left", fontweight="bold")
        ax.text(0.02, 0.04, "G(perc) = %.2f  (cheap: %.2f)\nfloor = %.2f"
                % (t["G_percolation"], CHEAP_G_PERC, t["agreement_floor"]),
                transform=ax.transAxes, fontsize=7.4, color=ACC, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=ACC))
        ax.legend(fontsize=7.0)
    ax.set_xlabel("porosity $\\phi$"); ax.set_ylabel("$k_{LBM}/k_{closure}$")
    ax.grid(alpha=0.25, which="both", linewidth=0.5)

    fig.suptitle("I-093 DEEP SCREEN — %s\nSynthetic overlapping-sphere family only; numerical "
                 "convergence is not empirical validation." % r["deep_decision"]["outcome"],
                 fontsize=9.4, y=1.03)
    fig.tight_layout()
    out = path or str(REPO_ROOT / "docs/insights/screens/I-093/figures/deep_primary.png")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main(argv=None):
    r = deep_screen()
    out = REPO_ROOT / "docs/insights/screens/I-093/deep_result.json"
    out.write_text(json.dumps(CHEAP._jsonable(r), indent=2) + "\n", encoding="utf-8")
    fig = figure(r)
    rve = r["multiseed_rve"]
    print("multi-seed RVE (N=%d seeds x %s):" % (len(DEEP_SEEDS), list(DEEP_SIZES)))
    for L in sorted(int(k) for k in rve["per_L"]):
        s = rve["per_L"][str(L)]
        print("  L=%-4d L/d=%.1f  mean k=%.4f  sd=%.4f  se=%.4f  seed spread=%.3f"
              % (L, rve["box_grain_diameters"][str(L)], s["mean"], s["sd"], s["se"], s["spread"]))
    print("stabilised=%s  L*=%s  R_sep=%.2f" % (rve["stabilised"], rve["L_star"], rve["R_sep"]))
    t = r["tolerance_sensitivity"]
    if "relative_move" in t:
        print("tolerance sensitivity: k moves %.3f%% (limit %.1f%%) -> cheap criterion adequate=%s"
              % (100 * t["relative_move"], 100 * t["limit"], t["cheap_criterion_adequate"]))
    tr = r["trend_on_stabilised_means"]
    if "G_percolation" in tr:
        print("trend on means: G_perc=%.3f (cheap %.3f) floor=%.3f preserved=%s"
              % (tr["G_percolation"], CHEAP_G_PERC, tr["agreement_floor"],
                 tr["percolation_trend_preserved"]))
    print("DEEP OUTCOME: %s" % r["deep_decision"]["outcome"])
    print("  %s" % r["deep_decision"]["basis"])
    print("compute: %.0f s of %.0f s" % (r["compute"]["wall_s"], r["compute"]["budget_s"]))
    print("wrote %s\nwrote %s" % (out, fig))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

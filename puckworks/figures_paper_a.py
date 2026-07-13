"""figures_paper_a.py — the six Paper-A figures (review §7), from the CORRECTED
matched-mass analysis.

Because Paper A's analysis is SLOW (PDE solves), the figures render from a cached
results file that one command regenerates:

    python -m puckworks.figures_paper_a compute   # ~25 min slow; -> results.json
    python -m puckworks.figures_paper_a render    # fast; -> docs/figures/paper_a/

`compute` runs every slow analysis function ONCE (no hand-typed numbers) and dumps
`docs/figures/paper_a/results.json`; `render` draws Fig 1-6 from it. matplotlib is a
lazy `[figures]` extra (module imports cleanly without it), reusing the Paper-B
figure style. Figures track the corrected findings: single-grind non-identifiability
(strong) but predictive transfer that WORKS at matched mass (identifiability !=
transfer).
"""
from __future__ import annotations
import json
import os

from .figures import _plt, _save, INK, ACCENT, NULL, GOOD, WARN, BAD, GRID

OUTDIR = "docs/figures/paper_a"
RESULTS = os.path.join(OUTDIR, "results.json")
_SOL_COLOR = {"caffeine": ACCENT, "trigonelline": GOOD, "5CQA": "#4a6fa5"}


# ---------------------------------------------------------------------------
def compute_all(out_path=RESULTS):
    """Run every slow analysis ONCE and cache to JSON (provenance: source commit)."""
    import subprocess
    from .validation.slow import angeloni_bracket as ab
    from .validation.slow import identifiability as idn
    from .validation.slow import external_waszkiewicz as ew
    from . import data as d
    inv = {(r["variety"], r["species"]): r["C0_s_mg_L"] / 1000.0
           for r in d.angeloni_inventories()}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                         stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = "UNKNOWN"
    # EVERY slow analysis the manuscript cites is regenerated here (review MAJ-19):
    # not just the six that feed the figures, but also the blind bracket, per-condition
    # result, flow-map refinement, refit summary, geometry sensitivity, sampled-aggregate
    # audit, and the external Waszkiewicz analysis.
    res = dict(
        source_commit=commit,
        schema_version=2,                                  # bumped: SSE/coupling relabel,
                                                           # g/L units, cluster CI, full-prec
        table7=dict(caffeine=inv.get(("Arabica", "CF")),
                    trigonelline=inv.get(("Arabica", "TR"))),
        panel_caffeine=ab.identifiability_panel("Arabica", "caffeine"),
        panel_trigonelline=ab.identifiability_panel("Arabica", "trigonelline"),
        transfer=ab.validate_refit_granulometry(),
        joint=ab.joint_multigrind_fit(),
        loco=ab.loco_cv_refit(),
        positive_control=idn.identifiability_fractions_vs_cup(),
        full_cup_sim=idn.full_cup_simulation_identifiability(),
        # --- previously-omitted manuscript analyses (MAJ-19 / A2-05) ---
        refit_summary=ab.refit_pannusch_angeloni(),        # Result 1 8.4%/11.5% (A2-05)
        species_bracket=ab.gate_pannusch_angeloni_species_bracket(),
        per_condition=ab.gate_pannusch_angeloni_per_condition(),
        flow_map_refinement=ab.flow_map_refinement(),
        geometry_sensitivity=ab.geometry_sensitivity_transfer(),
        sampled_aggregate_audit=idn.sampled_aggregate_vs_actual_cup(),
        external_waszkiewicz=ew.waszkiewicz_external_tds(),
    )
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(_jsonable(res), f)
    return res


def _jsonable(o):
    """Recursively make JSON-safe: stringify non-str dict keys (some analysis
    functions key by (variety, solute) tuples), pass everything else through."""
    if isinstance(o, dict):
        return {(k if isinstance(k, (str, int, float, bool)) or k is None
                 else str(k)): _jsonable(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_jsonable(x) for x in o]
    return o


def _logclean(ax, ticks=(0.2, 0.5, 1.0, 2.0, 5.0)):
    """Tidy a log x-axis on a sub-decade range: matplotlib otherwise stacks
    garbled minor-tick labels (e.g. '2x10^-1x10^0'). Pin explicit round ticks,
    label them plainly, and silence the minor labels."""
    from matplotlib.ticker import FixedLocator, FixedFormatter, NullFormatter
    lo, hi = ax.get_xlim()
    tk = [t for t in ticks if lo <= t <= hi]
    ax.xaxis.set_major_locator(FixedLocator(tk))
    ax.xaxis.set_major_formatter(FixedFormatter([("%g" % t) for t in tk]))
    ax.xaxis.set_minor_formatter(NullFormatter())


def _load(results):
    if results is None:
        results = RESULTS
    if isinstance(results, str):
        with open(results) as f:
            return json.load(f)
    return results


# ---------------------------------------------------------------------------
def fig1_design(outdir=OUTDIR):
    """Fig 1 — study & evidence design with CAMPAIGN-ACCURATE evidence categories
    (review MAJ-18): 'external' is used ONLY for a genuinely different rig/coffee not
    used for target fitting; the within-Angeloni O->C/F holdout is a within-campaign
    holdout, Table 7 is an orthogonal measurement from the same study, and the
    Waszkiewicz external trajectory is shown."""
    plt = _plt()
    # evidence-category palette (data use, not verb)
    CAT = {"source": ("#8a8f98", "source calibration"),
           "insample": ("#4a6fa5", "in-sample localization"),
           "sim": ("#9a6f2f", "same-model simulation"),
           "target": (ACCENT, "target recalibration"),
           "within": (GOOD, "within-campaign holdout"),
           "orth": ("#2f6f4f", "orthogonal measurement (same study)"),
           "external": (BAD, "independent external")}
    fig, ax = plt.subplots(figsize=(9.8, 5.6))
    ax.set_xlim(0, 12); ax.set_ylim(0, 8); ax.axis("off")

    def box(x, y, w, h, text, cat):
        col = CAT[cat][0]
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor="#f6f2ea", edgecolor=col,
                                   lw=2.2))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=7.6)

    def arrow(x0, y0, x1, y1, col=NULL):
        ax.annotate("", (x1, y1), (x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.5))

    # lane 1 — Schmieder/Pannusch lineage (top)
    ax.text(0.1, 7.5, "Schmieder / Pannusch lineage", fontsize=8, style="italic",
            color=NULL)
    box(0.2, 6.0, 2.6, 1.2, "Schmieder fractions\n→ Pannusch calibration", "source")
    box(3.4, 6.0, 2.7, 1.2, "Fraction-vs-cup\nprofile (in-sample\nlocalization)", "insample")
    box(6.7, 6.0, 2.7, 1.2, "Same-model exact-cup\nsimulation (synthetic\nillustration)", "sim")
    arrow(2.8, 6.6, 3.4, 6.6); arrow(6.1, 6.6, 6.7, 6.6)

    # lane 2 — Angeloni campaign (middle)
    ax.text(0.1, 4.6, "Angeloni campaign (one study; different rig/coffee/basket)",
            fontsize=8, style="italic", color=NULL)
    box(0.2, 3.1, 2.6, 1.2, "Angeloni O\n→ target recalibration", "target")
    box(3.4, 3.1, 2.7, 1.2, "Held-out O conditions\n(leave-one-condition-\nout CV)", "within")
    box(6.7, 3.1, 2.7, 1.2, "Angeloni C / F\ncross-grind holdout\n(within-campaign)", "within")
    box(9.6, 3.1, 2.2, 1.2, "Table 7 inventory\n(orthogonal\nmeasurement)", "orth")
    arrow(2.8, 3.7, 3.4, 3.7); arrow(6.1, 3.7, 6.7, 3.7); arrow(9.4, 3.7, 9.6, 3.7)
    arrow(1.5, 6.0, 1.5, 4.3)          # calibration -> target recalibration

    # lane 3 — Waszkiewicz external (bottom)
    ax.text(0.1, 1.9, "Waszkiewicz (independent second rig / coffee)", fontsize=8,
            style="italic", color=NULL)
    box(0.2, 0.4, 4.0, 1.2, "Waszkiewicz 5 s TDS fractions →\nexternal-data objective "
        "localization\n(measured flow; target-profiled level)", "external")
    arrow(2.2, 3.1, 2.2, 1.6)

    # legend
    hs = [plt.Line2D([0], [0], marker="s", ls="", mfc="#f6f2ea", mec=c[0], mew=2.2,
                     ms=9, label=c[1]) for c in CAT.values()]
    ax.legend(handles=hs, loc="lower right", fontsize=6.6, ncol=2, framealpha=0.9)
    ax.text(6.0, 2.15, "‘external’ = genuinely different rig/coffee NOT used for target "
            "fitting; O→C/F and Table 7 are within the Angeloni study.",
            ha="center", fontsize=6.6, color=NULL)
    fig.suptitle("Fig 1 — Paper A study & evidence design (campaign-accurate categories)",
                 y=0.97, fontsize=10.5, fontweight="bold")
    return _save(fig, outdir, "fig1_design.png")


def fig2_objective_surface(results=None, outdir=OUTDIR):
    """Fig 2 — inventory-rate SSE surface (top) + the 1-D profiled SSE (bottom) for
    caffeine & trigonelline. Objective = unweighted concentration-scale SSE with a
    least-squares nuisance level, plotted as the NORMALIZED increase (J-Jmin)/Jmin so
    the two panels share one interpretable colour scale (review Fig 2). The dimensionless
    rate scale is on a log axis; inventory carries g/L. The profile row shows the SSE
    optimised over c_s0 with the 10 % tolerance band that defines the reported width."""
    import numpy as np
    r = _load(results); plt = _plt()
    fig, axes = plt.subplots(2, 2, figsize=(9.6, 7.0), height_ratios=[1.6, 1.0])
    im = None
    for col, (key, sol) in enumerate((("panel_caffeine", "caffeine"),
                                      ("panel_trigonelline", "trigonelline"))):
        p = r[key]; s = p["surface"]
        rates = np.array(s["rates"]); cs0 = np.array(s["cs0"]); S = np.array(s["sse"])
        Jn = (S - S.min()) / S.min()                         # normalized objective increase
        RR, CC = np.meshgrid(rates, cs0, indexing="ij")
        ax = axes[0, col]
        im = ax.contourf(RR, CC, Jn, levels=np.linspace(0.0, 2.0, 21),
                         cmap="YlOrBr", extend="max")
        ax.contour(RR, CC, Jn, levels=[0.10], colors=[INK], linewidths=1.1,
                   linestyles="--")                          # the 10% tolerance contour
        prof = p["profile"]
        ax.plot(prof["rates"], prof["c_star"], color=ACCENT, lw=2.0,
                label="profiled valley $c^*(\\mathrm{rate})$")
        t7 = r["table7"].get(sol)
        if t7:
            ax.axhline(t7, color="#2f6f4f", ls=":", lw=1.6, label="Table 7 inventory")
        ax.plot(p["rate_star"], p["c_s0_star"], "o", color=INK, ms=7,
                label="SSE optimum", zorder=5)
        ax.set_xscale("log"); _logclean(ax)
        ax.set_title("(%s) %s" % ("a" if col == 0 else "b", sol), fontsize=10)
        ax.text(0.03, 0.03, "cond. no. %d\ncoupling %.2f"
                % (int(p["condition_number"]), p["local_curvature_coupling"]),
                transform=ax.transAxes, fontsize=7.2, va="bottom", ha="left",
                bbox=dict(boxstyle="round", fc="white", ec=NULL, alpha=0.8))
        ax.set_xlabel("rate scale (dimensionless, log)")
        ax.set_ylabel("inventory $c_{s,0}$ (g L$^{-1}$)")
        ax.legend(fontsize=6.8, loc="upper right")
        # --- 1-D profile (SSE optimised over c_s0) with the 10% band ---
        axp = axes[1, col]
        pr = np.array(prof["rates"]); ss = np.array(prof["sse"]); smin = prof["sse_min"]
        axp.plot(pr, (ss - smin) / smin, color=ACCENT, lw=1.8)
        axp.axhline(0.10, color=INK, ls="--", lw=1.0)
        within = (ss - smin) / smin <= 0.10
        axp.fill_between(pr, 0, 0.10, where=within, color=WARN, alpha=0.18,
                         label="within 10 %% (%.0f%% of grid)"
                         % (100 * p["profile_fraction_of_log_grid"]))
        axp.set_xscale("log"); _logclean(axp)
        axp.set_ylim(0, 0.6)
        axp.set_xlabel("rate scale (dimensionless, log)")
        axp.set_ylabel("profiled $(J-J_{\\min})/J_{\\min}$")
        axp.legend(fontsize=6.8, loc="upper center")
    cb = fig.colorbar(im, ax=axes[0, :].tolist(), shrink=0.85, pad=0.02,
                      label="normalized SSE increase $(J-J_{\\min})/J_{\\min}$")
    fig.suptitle("Fig 2 — inventory–rate SSE surface + profile: a flat valley "
                 "(practical non-identifiability)", y=0.99, fontsize=10.5,
                 fontweight="bold")
    return _save(fig, outdir, "fig2_objective_surface.png")


def fig3_holdouts(results=None, outdir=OUTDIR):
    """Fig 3 — every leave-one-condition-out held-out point (observed vs predicted),
    by solute and variety — the distribution the pooled mean hides."""
    import numpy as np
    r = _load(results); plt = _plt()
    pts = r["loco"]["points"]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.4))
    for ax, variety in zip(axes, ("Arabica", "Robusta")):
        mx = 0
        for sol in ("caffeine", "trigonelline", "5CQA"):
            pp = pts.get(f"{variety}:{sol}", [])
            obs = [x["obs"] for x in pp]; pred = [x["pred"] for x in pp]
            ax.scatter(obs, pred, s=28, color=_SOL_COLOR[sol], label=sol,
                       edgecolor="white", lw=0.5, zorder=3)
            mx = max([mx] + obs + pred)
        ax.plot([0, mx * 1.1], [0, mx * 1.1], color=NULL, ls=":", lw=1.2)
        ax.set_title("(%s) %s — held-out O conditions"
                     % ("a" if variety == "Arabica" else "b", variety))
        ax.set_xlabel("observed (g L$^{-1}$)"); ax.set_ylabel("predicted (g L$^{-1}$)")
        ax.legend(fontsize=7.5, loc="upper left")
    lc = r["loco"]
    fig.suptitle("Fig 3 — leave-one-condition-out holdouts (pooled %.1f%%, median "
                 "%.1f%%; descriptive condition-level resampling %s)"
                 % (lc["pooled_loco_mean_mape"], lc["pooled_loco_median_mape"],
                    lc["condition_cluster_resampling95"]),
                 y=1.02, fontsize=10, fontweight="bold")
    return _save(fig, outdir, "fig3_holdouts.png")


def fig4_transfer(results=None, outdir=OUTDIR):
    """Fig 4 — matched-cup O->C/F frozen transfer: observed vs predicted by
    condition, held-out grinds C and F."""
    import numpy as np
    r = _load(results); plt = _plt()
    pts = r["transfer"]["points"]
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.4))
    for ax, g in zip(axes, ("C", "F")):
        mx = 0
        for variety in ("Arabica", "Robusta"):
            for sol in ("caffeine", "trigonelline", "5CQA"):
                pp = pts.get(f"{variety}:{sol}:{g}", [])
                obs = [x["obs"] for x in pp]; pred = [x["pred"] for x in pp]
                mk = "o" if variety == "Arabica" else "s"
                ax.scatter(obs, pred, s=26, color=_SOL_COLOR[sol], marker=mk,
                           edgecolor="white", lw=0.5, zorder=3,
                           label=f"{sol} ({variety[:3]})")
                mx = max([mx] + obs + pred)
        ax.plot([0, mx * 1.1], [0, mx * 1.1], color=NULL, ls=":", lw=1.2)
        ax.set_title("(%s) held-out grind %s (matched 40 g cups)"
                     % ("a" if g == "C" else "b", g))
        ax.set_xlabel("observed (g L$^{-1}$)"); ax.set_ylabel("predicted (g L$^{-1}$)")
        ax.legend(fontsize=6, loc="upper left", ncol=2)
    fig.suptitle("Fig 4 — frozen O->C/F transfer at matched mass (transfers "
                 "reasonably; ≤1 pp geometry-sensitive)", y=1.02, fontsize=10,
                 fontweight="bold")
    return _save(fig, outdir, "fig4_transfer.png")


def fig5_joint_residual(results=None, outdir=OUTDIR):
    """Fig 5 — joint shared-fit vs per-grind residual structure (variety x solute x
    grind), with the cost-of-sharing and rate-boundary flags."""
    import numpy as np
    r = _load(results); plt = _plt()
    j = r["joint"]["per_variety"]
    labels, Mj, Mi = [], [], []
    for variety in ("Arabica", "Robusta"):
        for sol in ("caffeine", "trigonelline", "5CQA"):
            x = j[variety][sol]
            Mj.append([x["joint_per_grind_mape"][g] for g in ("O", "C", "F")])
            Mi.append([x["independent_per_grind_mape"][g] for g in ("O", "C", "F")])
            bnd = " *" if x["joint_rate_at_boundary"] else ""
            labels.append(f"{variety[:3]}:{sol}{bnd}")
    Mj = np.array(Mj, float); Mi = np.array(Mi, float); D = Mj - Mi
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 4.6))
    vmax = max(20.0, Mj.max(), Mi.max())

    def _heat(ax, M, title, cmap, vmin, vmax, center_white=0.6):
        im = ax.imshow(M, cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
        ax.set_xticks(range(3)); ax.set_xticklabels(["O", "C", "F"])
        ax.set_yticks(range(len(labels)))
        ax.set_yticklabels(labels if ax is axes[0] else [""] * len(labels), fontsize=7.2)
        thr = vmin + center_white * (vmax - vmin)
        for i in range(M.shape[0]):
            for k in range(M.shape[1]):
                ax.text(k, i, "%.1f" % M[i, k], ha="center", va="center", fontsize=6.8,
                        color=INK if M[i, k] < thr else "white")
        ax.set_title(title, fontsize=9)
        return im
    im0 = _heat(axes[0], Mj, "(a) joint shared-fit MAPE (%)", "YlOrBr", 0, vmax)
    _heat(axes[1], Mi, "(b) independent per-grind MAPE (%)", "YlOrBr", 0, vmax)
    dmax = float(np.abs(D).max())
    imd = _heat(axes[2], D, "(c) cost of sharing = (a)−(b) (pp)", "RdBu_r",
                -dmax, dmax, center_white=1.0)
    fig.colorbar(im0, ax=axes[:2].tolist(), shrink=0.7, label="MAPE (%)")
    fig.colorbar(imd, ax=axes[2], shrink=0.7, label="Δ MAPE (pp)")
    fig.suptitle("Fig 5 — joint shared-$(c_{s,0},\\mathrm{rate})$ vs independent per-grind; "
                 "pooled %.1f%% vs %.1f%% (mean cost ~%.1f pp); * = rate at domain boundary"
                 % (r["joint"]["mean_joint_pooled_mape"],
                    r["joint"]["mean_independent_per_grind_mape"],
                    r["joint"]["cost_of_sharing_pp"]), y=1.0, fontsize=9.5,
                 fontweight="bold")
    return _save(fig, outdir, "fig5_joint_residual.png")


def fig6_fraction_vs_endpoint(results=None, outdir=OUTDIR):
    """Fig 6 — rate profiles: fraction scoring (sharp) vs endpoint scoring (flat),
    both the empirical sampled aggregate and the exact-integral simulation."""
    import numpy as np
    r = _load(results); plt = _plt()
    pc = r["positive_control"]["per_solute"]; sim = r["full_cup_sim"]["per_solute"]
    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.6), sharey=False)
    for ax, sol in zip(axes, ("caffeine", "trigonelline", "5CQA")):
        x = pc[sol]; rr = np.array(x["rates"])
        ax.plot(rr, x["fraction_mape"], "o-", color=ACCENT, lw=1.7, ms=4,
                label="fraction (empirical)")
        ax.plot(rr, x["sampled_agg_mape"], "s--", color=NULL, lw=1.5, ms=4,
                label="sampled aggregate")
        sx = sim[sol]; sr = np.array(sx["rates"])
        ax.plot(sr, sx["exact_cup_mape"], "^:", color=GOOD, lw=1.5, ms=4,
                label="exact whole cup (sim)")
        ax.axvline(1.0, color=WARN, ls=":", lw=1.0)
        ax.set_xscale("log"); ax.set_title(sol)
        ax.set_xlabel("rate scale (log)"); ax.set_ylabel("MAPE (%)")
        _logclean(ax)
        ax.legend(fontsize=6.5, loc="upper center")
    fig.suptitle("Fig 6 — fraction-resolved scoring localizes the rate objective more "
                 "strongly than aggregated scoring (in the tested designs); "
                 "empirical + same-model simulation",
                 y=1.03, fontsize=10, fontweight="bold")
    return _save(fig, outdir, "fig6_fraction_vs_endpoint.png")


def render_all(results=None, outdir=OUTDIR):
    res = _load(results)
    return [fig1_design(outdir), fig2_objective_surface(res, outdir),
            fig3_holdouts(res, outdir), fig4_transfer(res, outdir),
            fig5_joint_residual(res, outdir), fig6_fraction_vs_endpoint(res, outdir)]


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.figures_paper_a")
    p.add_argument("cmd", choices=["compute", "render", "all"], nargs="?", default="all")
    p.add_argument("--out", default=OUTDIR)
    a = p.parse_args(argv)
    if a.cmd in ("compute", "all"):
        print("computing (slow)...")
        compute_all()
    if a.cmd in ("render", "all"):
        print("rendered:", render_all(outdir=a.out))


if __name__ == "__main__":
    main()

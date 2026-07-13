"""figures_paper_a.py — the six Paper-A figures (review §7), from the CORRECTED
matched-mass analysis.

Because Paper A's analysis is SLOW (PDE solves), the figures render from a cached
results file that one command regenerates:

    python -m puckworks.figures_paper_a compute   # ~25 min slow; -> results.json
    python -m puckworks.figures_paper_a render    # fast; -> docs/figures/paper_a/

`compute` runs every slow analysis function ONCE (no hand-typed numbers) and dumps
`docs/figures/paper_a/results.json`; `render` draws Fig 1-8 (six main + two
condition-structure diagnostics) from it. matplotlib is a
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
        identifiability_convergence=ab.identifiability_panel_convergence(),  # A2-06/07 + MAJ-04
        transfer=ab.validate_refit_granulometry(),
        transfer_skill=ab.transfer_skill_vs_baselines(),   # A3-01 null-benchmark skill
        reduced_model_ladder=ab.reduced_model_ladder(),    # A3-19 nested ladder
        joint=ab.joint_multigrind_fit(),
        loco=ab.loco_cv_refit(),
        positive_control=idn.identifiability_fractions_vs_cup(),
        full_cup_sim=idn.full_cup_simulation_identifiability(),
        full_cup_discrepancy=idn.full_cup_simulation_discrepancy(),  # MAJ-13 discrepancy control
        full_cup_discrepancy_large=idn.full_cup_simulation_discrepancy(  # larger dose (bias emerges)
            temp_offset_C=8.0, flow_scale=1.25),
        full_cup_offgrid_noise=idn.full_cup_simulation_offgrid_noise(),  # A3-15/16 off-grid + noise
        # --- previously-omitted manuscript analyses (MAJ-19 / A2-05) ---
        refit_summary=ab.refit_pannusch_angeloni(),        # Result 1 8.4%/11.5% (A2-05)
        species_bracket=ab.gate_pannusch_angeloni_species_bracket(),
        per_condition=ab.gate_pannusch_angeloni_per_condition(),
        flow_map_refinement=ab.flow_map_refinement(),
        endpoint_mass_sensitivity=ab.endpoint_mass_sensitivity(),  # A2-09 endpoint caveat
        geometry_sensitivity=ab.geometry_sensitivity_transfer(),
        sampled_aggregate_audit=idn.sampled_aggregate_vs_actual_cup(),
        external_waszkiewicz=ew.waszkiewicz_external_tds(),
        external_waszkiewicz_sensitivity=ew.waszkiewicz_sensitivity(),  # A2-13b nuisance sweep
    )
    # A3-13: Table 7 orthogonal-inventory rate constraint (PDE-free post-processing of
    # the panels: where the measured inventory intersects the profiled valley).
    res["table7_rate_constraint"] = {
        sol: ab.table7_rate_constraint(res[k], res["table7"].get(sol))
        for k, sol in (("panel_caffeine", "caffeine"),
                       ("panel_trigonelline", "trigonelline"))
        if res["table7"].get(sol)}
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
        # A3-04/A3-27: mark right-censoring where the 10% set reaches the tested boundary
        if p.get("profile_upper_censored"):
            rmax = float(pr[-1])
            axp.annotate("", xy=(rmax, 0.05), xytext=(rmax / 1.7, 0.05),
                         arrowprops=dict(arrowstyle="->", color=BAD, lw=1.6))
            axp.text(rmax, 0.085, "set open\n(≥ %.1f, censored)" % rmax, color=BAD,
                     ha="right", va="bottom", fontsize=6.2)
        axp.text(0.03, 0.95, "MAPE set: %.0f%% of grid\nSSE∩MAPE Jaccard %.2f"
                 % (100 * p["mape_profile_fraction_within10pct"],
                    p.get("sse_mape_threshold_jaccard") or float("nan")),
                 transform=axp.transAxes, va="top", ha="left", fontsize=6.2, color=NULL)
        axp.set_xlabel("rate scale (dimensionless, log)")
        axp.set_ylabel("profiled $(J-J_{\\min})/J_{\\min}$")
        axp.legend(fontsize=6.8, loc="upper center")
    cb = fig.colorbar(im, ax=axes[0, :].tolist(), shrink=0.85, pad=0.02,
                      label="normalized SSE increase $(J-J_{\\min})/J_{\\min}$")
    fig.suptitle("Fig 2 — inventory–rate SSE surface and profiled objective "
                 "(10 % tolerance set right-censored at the domain edge)", y=0.99,
                 fontsize=10.0, fontweight="bold")
    return _save(fig, outdir, "fig2_objective_surface.png")


def fig3_holdouts(results=None, outdir=OUTDIR):
    """Fig 3 — leave-one-condition-out holdouts (review A3-05/6.28): (a) observed vs
    predicted for all held-out O conditions (the calibration diagonal looks favourable
    because between-solute concentration differences dominate); (b,c) the SIGNED residual
    faceted against temperature and pressure, which exposes the within-group condition
    structure the pooled MAPE and the near-diagonal cloud hide."""
    import numpy as np
    r = _load(results); plt = _plt()
    pts = r["loco"]["points"]
    mk = {"Arabica": "o", "Robusta": "s"}
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.2))
    # (a) observed vs predicted
    axa = axes[0]; mx = 0
    for variety in ("Arabica", "Robusta"):
        for sol in ("caffeine", "trigonelline", "5CQA"):
            pp = pts.get(f"{variety}:{sol}", [])
            obs = [x["obs"] for x in pp]; pred = [x["pred"] for x in pp]
            axa.scatter(obs, pred, s=24, color=_SOL_COLOR[sol], marker=mk[variety],
                        edgecolor="white", lw=0.4, zorder=3,
                        label=f"{sol} ({variety[:3]})")
            mx = max([mx] + obs + pred)
    axa.plot([0, mx * 1.1], [0, mx * 1.1], color=NULL, ls=":", lw=1.2)
    axa.set_title("(a) observed vs predicted", fontsize=9)
    axa.set_xlabel("observed (g L$^{-1}$)"); axa.set_ylabel("predicted (g L$^{-1}$)")
    axa.legend(fontsize=5.6, loc="upper left", ncol=2)
    # (b,c) signed residual vs T and p
    for ax, xkey, xlabel, pan in ((axes[1], "T", "brew temperature (°C)", "b"),
                                  (axes[2], "p", "pressure (bar)", "c")):
        for variety in ("Arabica", "Robusta"):
            for sol in ("caffeine", "trigonelline", "5CQA"):
                pp = pts.get(f"{variety}:{sol}", [])
                xv = [x[xkey] for x in pp]
                res = [(x["pred"] - x["obs"]) / x["obs"] * 100.0 for x in pp]
                ax.scatter(xv, res, s=24, color=_SOL_COLOR[sol], marker=mk[variety],
                           edgecolor="white", lw=0.4, alpha=0.9)
        ax.axhline(0.0, color=INK, lw=1.0)
        ax.set_title("(%s) signed residual vs %s" % (pan, "temperature" if xkey == "T"
                                                     else "pressure"), fontsize=9)
        ax.set_xlabel(xlabel); ax.set_ylabel("(pred−obs)/obs [%]")
    lc = r["loco"]
    fig.suptitle("Fig 3 — leave-one-condition-out holdouts: calibration diagonal + signed "
                 "residual structure vs (T, p) (pooled %.1f%%, median %.1f%%; descriptive "
                 "condition-level resampling %s, not a CI)"
                 % (lc["pooled_loco_mean_mape"], lc["pooled_loco_median_mape"],
                    lc["condition_cluster_resampling95"]),
                 y=1.02, fontsize=8.8, fontweight="bold")
    return _save(fig, outdir, "fig3_holdouts.png")


def fig4_transfer(results=None, outdir=OUTDIR):
    """Fig 4 — matched-volume O->C/F transfer with a NULL BENCHMARK (review A3-01/A3-05):
    panels (a,b) observed vs predicted for held-out C and F; panel (c) the mechanistic
    model's held-out MAPE against an O-trained level-only constant per fit x grind, with
    the pooled skill. Neutral title; the central message is that the model barely beats
    the constant."""
    import numpy as np
    r = _load(results); plt = _plt()
    pts = r["transfer"]["points"]
    envs = r["transfer"].get("condition_envelopes", {})
    ts = r.get("transfer_skill")
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.3),
                             gridspec_kw=dict(width_ratios=[1, 1, 1.25]))
    for ax, g in zip(axes[:2], ("C", "F")):
        mx = 0
        for variety in ("Arabica", "Robusta"):
            for sol in ("caffeine", "trigonelline", "5CQA"):
                pp = pts.get(f"{variety}:{sol}:{g}", [])
                obs = [x["obs"] for x in pp]; pred = [x["pred"] for x in pp]
                mk = "o" if variety == "Arabica" else "s"
                # A3-11: vertical profile-set PREDICTION ENVELOPE (pred_min..pred_max
                # across the 10% near-optimal set) at each held-out condition
                ev = envs.get(f"{variety}:{sol}:{g}", [])
                if ev:
                    for x in ev:
                        ax.plot([x["obs"], x["obs"]], [x["pred_min"], x["pred_max"]],
                                color=_SOL_COLOR[sol], lw=2.4, alpha=0.28,
                                solid_capstyle="round", zorder=2)
                ax.scatter(obs, pred, s=26, color=_SOL_COLOR[sol], marker=mk,
                           edgecolor="white", lw=0.5, zorder=3,
                           label=f"{sol} ({variety[:3]})")
                mx = max([mx] + obs + pred)
        ax.plot([0, mx * 1.1], [0, mx * 1.1], color=NULL, ls=":", lw=1.2)
        ax.set_title("(%s) grind %s — point + profile-set envelope"
                     % ("a" if g == "C" else "b", g), fontsize=8.5)
        ax.set_xlabel("observed (g L$^{-1}$)"); ax.set_ylabel("predicted (g L$^{-1}$)")
        ax.legend(fontsize=6, loc="upper left", ncol=2)
    # (c) model vs O-trained-constant baseline: paired MAPE per fit x grind
    axc = axes[2]
    if ts is not None:
        labels, model_v, const_v = [], [], []
        for key, x in ts["per_fit"].items():
            var, sol = key.split(":")
            for g in ("C", "F"):
                labels.append(f"{var[:3]}:{sol[:4]}:{g}")
                model_v.append(x[g]["model_mape"]); const_v.append(x[g]["const_mape"])
        idx = np.arange(len(labels)); w = 0.4
        axc.barh(idx - w / 2, const_v, w, color=NULL, label="O-trained constant")
        axc.barh(idx + w / 2, model_v, w, color=ACCENT, label="mechanistic model")
        axc.set_yticks(idx); axc.set_yticklabels(labels, fontsize=5.6)
        axc.invert_yaxis()
        axc.set_xlabel("held-out MAPE (%)")
        axc.set_title("(c) model vs null baseline — pooled skill %.0f%%"
                      % (100 * ts["skill_vs_const"]), fontsize=9)
        axc.legend(fontsize=6.5, loc="lower right")
        axc.text(0.97, 0.30, "model worse than\nconstant on %d/%d points"
                 % (ts["n_model_worse_than_const"], ts["n_points"]),
                 transform=axc.transAxes, ha="right", va="bottom", fontsize=6.2,
                 color=BAD)
    fig.suptitle("Fig 4 — O→C/F transfer vs an O-trained level-only baseline "
                 "(matched-volume proxy for the 40 g endpoint)", y=1.02, fontsize=9.6,
                 fontweight="bold")
    return _save(fig, outdir, "fig4_transfer.png")


def fig5_joint_residual(results=None, outdir=OUTDIR):
    """Fig 5 — IN-SAMPLE shared-parameter compatibility (review A3-19/A3-29): top row,
    joint shared-fit vs independent per-grind residual heatmaps + cost-of-sharing; bottom
    row, the nested REDUCED-MODEL LADDER (constant / per-grind constant / shared mech /
    per-grind mech) so the cost of sharing is read against level-only comparators."""
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
    fig = plt.figure(figsize=(11.4, 6.6))
    gs = fig.add_gridspec(2, 3, height_ratios=[1.35, 1.0], hspace=0.42, wspace=0.16)
    axes = [fig.add_subplot(gs[0, c]) for c in range(3)]
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
    fig.colorbar(im0, ax=[axes[0], axes[1]], shrink=0.7, label="MAPE (%)")
    fig.colorbar(imd, ax=axes[2], shrink=0.7, label="Δ MAPE (pp)")

    # (d) reduced-model ladder spanning the bottom row
    lad = r.get("reduced_model_ladder")
    axd = fig.add_subplot(gs[1, :])
    if lad is not None:
        keys = list(lad["per_fit"].keys())
        models = [("model0_const", "constant (1p)", NULL),
                  ("model1_pergrind_const", "per-grind const (3p)", "#8a8f98"),
                  ("model2_shared_mech", "shared mech (2p)", ACCENT),
                  ("model3_pergrind_mech", "per-grind mech (6p)", GOOD)]
        idx = np.arange(len(keys)); w = 0.2
        for mi, (mk, lab, cc) in enumerate(models):
            axd.bar(idx + (mi - 1.5) * w, [lad["per_fit"][k][mk] for k in keys], w,
                    color=cc, label=lab)
        axd.set_xticks(idx)
        axd.set_xticklabels([k.replace("Arabica", "Ara").replace("Robusta", "Rob")
                             for k in keys], fontsize=6.6, rotation=20, ha="right")
        axd.set_ylabel("in-sample macro-MAPE (%)")
        axd.set_title("(d) reduced-model ladder — shared mechanistic (2p) beats per-grind "
                      "constants (3p) in only %d/%d fits"
                      % (lad["n_fits_mech_beats_pergrind_const"], lad["n_fits"]),
                      fontsize=9)
        axd.legend(fontsize=6.6, ncol=4, loc="upper center")
    fig.suptitle("Fig 5 — in-sample shared-parameter compatibility + reduced-model ladder; "
                 "pooled shared %.1f%% vs per-grind %.1f%% (cost ~%.1f pp); * = rate at "
                 "domain boundary"
                 % (r["joint"]["mean_joint_pooled_mape"],
                    r["joint"]["mean_independent_per_grind_mape"],
                    r["joint"]["cost_of_sharing_pp"]), y=1.0, fontsize=9.3,
                 fontweight="bold")
    return _save(fig, outdir, "fig5_joint_residual.png")


def fig6_fraction_vs_endpoint(results=None, outdir=OUTDIR):
    """Fig 6 — fraction-resolved vs aggregated scoring, in THREE clearly separated
    evidence tiers (review A3-05/6.30): (a-c) in-sample Schmieder empirical fraction +
    same-model exact-cup simulation with the ±1σ seed band; (d) the INDEPENDENT external
    Waszkiewicz TDS trajectory as a target-profiled SHAPE test -- a shallow, high-residual
    minimum with an alignment-sensitivity band, and the algebraically-flat single cup."""
    import numpy as np
    r = _load(results); plt = _plt()
    pc = r["positive_control"]["per_solute"]; sim = r["full_cup_sim"]["per_solute"]
    fig, axes = plt.subplots(1, 4, figsize=(14.8, 3.7), sharey=False)
    for ax, sol in zip(axes[:3], ("caffeine", "trigonelline", "5CQA")):
        x = pc[sol]; rr = np.array(x["rates"])
        ax.plot(rr, x["fraction_mape"], "o-", color=ACCENT, lw=1.7, ms=4,
                label="fraction (empirical)")
        ax.plot(rr, x["sampled_agg_mape"], "s--", color=NULL, lw=1.5, ms=4,
                label="sampled aggregate")
        sx = sim[sol]; sr = np.array(sx["rates"])
        ax.plot(sr, sx["exact_cup_mape"], "^:", color=GOOD, lw=1.5, ms=4,
                label="exact whole cup (sim)")
        if "exact_cup_mape_seed_mean" in sx and "exact_cup_mape_seed_std" in sx:
            cmean = np.array(sx["exact_cup_mape_seed_mean"]); cstd = np.array(sx["exact_cup_mape_seed_std"])
            ax.fill_between(sr, cmean - cstd, cmean + cstd, color=GOOD, alpha=0.18, lw=0,
                            label="exact-cup ±1σ over 20 seeds")
        ax.axvline(1.0, color=WARN, ls=":", lw=1.0)
        ax.set_xscale("log"); ax.set_title("(%s) %s · in-sample+sim"
                                           % ("abc"[list(("caffeine", "trigonelline",
                                              "5CQA")).index(sol)], sol), fontsize=8.2)
        ax.set_xlabel("rate scale (log)"); ax.set_ylabel("MAPE (%)")
        _logclean(ax)
        ax.legend(fontsize=6.0, loc="upper center")
    # (d) EXTERNAL tier: Waszkiewicz target-profiled shape test
    axe = axes[3]
    ew = r.get("external_waszkiewicz")
    if ew is not None:
        er = np.array(ew["rates"], float)
        cases = [v["fraction_mape"] for v in ew["per_case"].values()]
        stack = np.array(cases, float)                    # (n_case, n_rate) alignment band
        head = ew["per_case"].get("offset0s_no_first_bin") or list(ew["per_case"].values())[0]
        axe.fill_between(er, stack.min(0), stack.max(0), color="#4a6fa5", alpha=0.18, lw=0,
                         label="alignment/first-bin band")
        axe.plot(er, head["fraction_mape"], "o-", color="#4a6fa5", lw=1.7, ms=4,
                 label="fraction (target-profiled)")
        axe.plot(er, head["cup_mape"], "^:", color=NULL, lw=1.5, ms=4,
                 label="single cup (algebraically flat)")
        bi = head["fraction_best_rate"]; mn = head["fraction_min_mape"]
        axe.axvline(bi, color=WARN, ls=":", lw=1.0)
        axe.annotate("shallow min ~%.0f%%\n(best rate %.1f, ratio %.1f×)"
                     % (mn, bi, head["fraction_range_ratio"]),
                     (bi, mn), textcoords="offset points", xytext=(6, 18), fontsize=6.2,
                     color=BAD)
        axe.set_xscale("log"); _logclean(axe)
        axe.set_title("(d) EXTERNAL Waszkiewicz shape test", fontsize=8.2)
        axe.set_xlabel("rate scale (log)"); axe.set_ylabel("MAPE (%)")
        axe.legend(fontsize=6.0, loc="upper center")
    fig.suptitle("Fig 6 — temporal resolution moves the rate objective more than an "
                 "aggregate (three evidence tiers: in-sample · same-model sim · "
                 "independent external shape test)", y=1.04, fontsize=9.4,
                 fontweight="bold")
    return _save(fig, outdir, "fig6_fraction_vs_endpoint.png")


def fig7_per_group_diagnostics(results=None, outdir=OUTDIR):
    """Fig 7 — per-group refit diagnostics (review A2-16 / MAJ-17). The per-condition
    residual is decomposed by variety x solute (n=9 conditions each): blind vs
    inventory-matched MAPE, and the model-vs-data shape correlation. It makes the
    per_condition note visible: inventory-matching HELPS caffeine but HURTS trigonelline
    (so the residual is not pure inventory), and the shape correlations cluster near
    zero -- the (T,p) transfer residual is not removed by the tested flow maps + inventory
    match. HONEST SCOPE: this shows per-GROUP metrics; the per-condition residual-vs-(T,p)
    SCATTER is Fig 8."""
    import numpy as np
    r = _load(results); plt = _plt()
    pv = r["per_condition"]["per_variety"]
    n_cond = r["per_condition"]["n_conditions_per_variety"]
    varieties = [v for v in ("Arabica", "Robusta") if v in pv]
    solutes = ["caffeine", "trigonelline", "5CQA", "tds"]
    labels, blind, matched, shape = [], [], [], []
    for var in varieties:
        for sol in solutes:
            x = pv[var].get(sol)
            if not x:
                continue
            labels.append(f"{var[:3]}:{sol}")
            blind.append(x.get("mape_blind"))
            matched.append(x.get("mape_inv_matched"))    # None for 5CQA/tds (no inventory)
            shape.append(x.get("shape_corr"))
    idx = np.arange(len(labels)); w = 0.38
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4))

    # (a) blind vs inventory-matched MAPE
    ax = axes[0]
    b = np.array([np.nan if v is None else v for v in blind], float)
    m = np.array([np.nan if v is None else v for v in matched], float)
    ax.bar(idx - w / 2, b, w, color=NULL, label="blind (no inventory match)")
    ax.bar(idx + w / 2, np.nan_to_num(m), w, color=ACCENT,
           label="inventory-matched (caffeine/trig only)")
    # mark where matching HURTS (matched > blind) vs HELPS
    for i, (bi, mi) in enumerate(zip(b, m)):
        if not np.isnan(mi):
            worse = mi > bi
            ax.annotate("↑ worse" if worse else "↓ better",
                        (i + w / 2, mi), textcoords="offset points", xytext=(0, 3),
                        ha="center", fontsize=6.3, color=BAD if worse else GOOD)
    ax.set_xticks(idx); ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=7.4)
    ax.set_ylabel("per-condition MAPE (%)")
    ax.set_title("(a) blind vs inventory-matched residual (n=%d cond./group)" % n_cond,
                 fontsize=9)
    ax.legend(fontsize=7, loc="upper left")

    # (b) model-vs-data shape correlation per group
    ax = axes[1]
    sh = np.array([np.nan if v is None else v for v in shape], float)
    cols = [GOOD if (not np.isnan(v) and v > 0.4) else
            (BAD if (not np.isnan(v) and v < 0) else NULL) for v in sh]
    ax.barh(idx, sh, color=cols)
    ax.axvline(0.0, color=INK, lw=0.8)
    ax.set_yticks(idx); ax.set_yticklabels(labels, fontsize=7.4)
    ax.invert_yaxis()
    ax.set_xlabel("model–data shape correlation")
    ax.set_xlim(-0.6, 0.8)
    ax.set_title("(b) cross-condition model–data response correlation (n=9 conditions; "
                 "not a temporal trajectory)", fontsize=8.5)
    fig.suptitle("Fig 7 — per-group blind and inventory-matched errors, with "
                 "cross-condition model–data association (n=9 O conditions/group; "
                 "40 mL proxy endpoint)", y=1.02, fontsize=9.0, fontweight="bold")
    return _save(fig, outdir, "fig7_per_group_diagnostics.png")


def fig8_residuals_vs_conditions(results=None, outdir=OUTDIR):
    """Fig 8 — signed transfer residuals vs the (T, p) conditions (review A-MAJ17). For
    each variety x solute, the per-condition BLIND residual (pred-meas)/meas is plotted
    against brew temperature (a) and pressure (b) at the three DoE levels each. The clear
    structure is a solute-consistent SIGN OFFSET -- every condition under-predicts (all
    residuals negative), ordered by solute (5CQA most negative, then trigonelline, then
    caffeine) and separated by variety -- exactly what a pure inventory (level) rescale
    CANNOT remove, since a level shift moves all conditions together but not the
    solute/variety-specific offsets. This is the residual-vs-(T,p) scatter the per-group
    Fig 7 could not show; it consumes the per-condition residual vectors now surfaced by
    the harness."""
    import numpy as np
    r = _load(results); plt = _plt()
    pv = r["per_condition"]["per_variety"]
    varieties = [v for v in ("Arabica", "Robusta") if v in pv]
    solutes = ["caffeine", "trigonelline", "5CQA", "tds"]
    vcol = {"Arabica": ACCENT, "Robusta": "#4a6fa5"}
    smark = {"caffeine": "o", "trigonelline": "s", "5CQA": "^", "tds": "D"}
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 4.4))
    for ax, xkey, xlabel in ((axes[0], "T_degC", "brew temperature (°C)"),
                             (axes[1], "p_bar", "pressure (bar)")):
        for var in varieties:
            for sol in solutes:
                x = pv[var].get(sol)
                if not x or "conditions" not in x:
                    continue
                cs = x["conditions"]
                xv = [c[xkey] for c in cs]
                yv = [c["signed_resid_blind_pct"] for c in cs]
                ax.scatter(xv, yv, marker=smark[sol], s=26, facecolor=vcol[var],
                           edgecolor="white", lw=0.4, alpha=0.85, label="_nolegend_")
        ax.axhline(0.0, color=INK, lw=1.0)
        ax.set_xlabel(xlabel); ax.set_ylabel("signed blind residual (pred−meas)/meas [%]")
        ax.set_title("(a) residual vs temperature" if xkey == "T_degC"
                     else "(b) residual vs pressure", fontsize=9)
    # a compact combined legend (variety = colour, solute = marker)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", mfc=vcol[v], mec="white", label=v)
               for v in varieties]
    handles += [Line2D([], [], marker=smark[s], ls="", mfc=NULL, mec="white", label=s)
                for s in solutes]
    axes[1].legend(handles=handles, fontsize=6.8, loc="upper right", ncol=2)
    fig.suptitle("Fig 8 — blind source-model residuals by operating condition "
                 "(pre target-level fit); solute/variety group offsets motivate the "
                 "per-group target-level recalibration (a group level CAN remove these "
                 "offsets; within-group (T,p) structure after level-fitting is not "
                 "shown here — A4-08)", y=1.02, fontsize=8.2, fontweight="bold")
    return _save(fig, outdir, "fig8_residuals_vs_conditions.png")


def export_source_data(results=None, outdir=OUTDIR):
    """Write the numeric data behind the data-bearing figures as tidy CSVs (review
    A2-16): reviewers can re-plot without the PDE stack. One CSV per figure series, from
    the SAME bundle the figures render from (single source of truth). Returns the paths."""
    import csv
    r = _load(results)
    sd = os.path.join(outdir, "source_data")
    os.makedirs(sd, exist_ok=True)
    written = []

    def _w(name, header, rows):
        path = os.path.join(sd, name)
        with open(path, "w", newline="") as f:
            wr = csv.writer(f); wr.writerow(header); wr.writerows(rows)
        written.append(path)

    # Fig 2 — identifiability profiles (rate, best c_s0 level, profiled SSE) per panel
    for key, sol in (("panel_caffeine", "caffeine"), ("panel_trigonelline", "trigonelline")):
        p = r.get(key)
        prof = p.get("profile") if isinstance(p, dict) else None
        if prof and "rates" in prof:
            rows = list(zip(prof["rates"], prof.get("c_star", []), prof.get("sse", [])))
            _w(f"fig2_{sol}_profile.csv", ["rate_scale", "best_c_s0", "profiled_sse"], rows)

    # Fig 5 — joint vs independent per-grind MAPE (variety x solute x grind)
    j = r.get("joint", {}).get("per_variety") if isinstance(r.get("joint"), dict) else None
    if j:
        rows = []
        for var, sols in j.items():
            for sol, x in sols.items():
                for g in ("O", "C", "F"):
                    rows.append([var, sol, g, x["joint_per_grind_mape"].get(g),
                                 x["independent_per_grind_mape"].get(g)])
        _w("fig5_joint_vs_independent.csv",
           ["variety", "solute", "grind", "joint_shared_mape_pct", "independent_mape_pct"], rows)

    # Fig 6 — fraction vs endpoint MAPE profiles per solute (empirical + simulation)
    pc = r.get("positive_control", {}).get("per_solute", {})
    sim = r.get("full_cup_sim", {}).get("per_solute", {})
    for sol in ("caffeine", "trigonelline", "5CQA"):
        x = pc.get(sol)
        if x:
            rows = list(zip(x["rates"], x["fraction_mape"], x.get("sampled_agg_mape", []),
                            sim.get(sol, {}).get("exact_cup_mape", [])))
            _w(f"fig6_{sol}_profiles.csv",
               ["rate_scale", "fraction_mape", "sampled_aggregate_mape", "exact_cup_mape"], rows)

    # Fig 7/8 — per-condition residuals (variety x solute x (T,p))
    pv = r.get("per_condition", {}).get("per_variety", {})
    rows = []
    for var, sols in pv.items():
        for sol, x in sols.items():
            for c in x.get("conditions", []):
                rows.append([var, sol, c["T_degC"], c["p_bar"], c["meas"],
                             c["pred_blind"], c["signed_resid_blind_pct"],
                             c.get("pred_matched"), c.get("signed_resid_matched_pct")])
    if rows:
        _w("fig7_8_per_condition_residuals.csv",
           ["variety", "solute", "T_degC", "p_bar", "meas", "pred_blind",
            "signed_resid_blind_pct", "pred_matched", "signed_resid_matched_pct"], rows)
    return written


def render_all(results=None, outdir=OUTDIR):
    res = _load(results)
    return [fig1_design(outdir), fig2_objective_surface(res, outdir),
            fig3_holdouts(res, outdir), fig4_transfer(res, outdir),
            fig5_joint_residual(res, outdir), fig6_fraction_vs_endpoint(res, outdir),
            fig7_per_group_diagnostics(res, outdir),
            fig8_residuals_vs_conditions(res, outdir)]


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
        print("source data:", export_source_data(outdir=a.out))


if __name__ == "__main__":
    main()

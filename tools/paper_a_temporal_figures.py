#!/usr/bin/env python3
"""Figures for the temporal-model-discrepancy screen.

    EXPLORATORY_SCIENTIFIC_SCREEN
    NOT_A_FORMAL_P0_GATE_RESULT

Palette: validated categorical slots 1-3 (blue / orange / aqua) plus violet for the fourth model,
assigned in fixed order and never cycled. The residual heatmap uses a DIVERGING ramp with a neutral
grey midpoint at zero, because the quantity has a meaningful zero and a sign; sequential would hide
exactly the thing being looked for. Every figure ships with its numeric table in the Markdown, which
is the documented relief for the low-contrast slot.
"""
from __future__ import annotations

import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm   # noqa: E402

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "docs" / "paper1_resource" / "exploratory" / "temporal_discrepancy"
FIG_DIR = OUT_DIR / "figures"

SERIES = {"SRC_EXP": "#1baf7a", "BASE": "#2a78d6", "BIEXP": "#eda100", "SLOW_TAIL": "#eb6834"}
ORDER = ("SRC_EXP", "BASE", "BIEXP", "SLOW_TAIL")
INK, INK_2, MUTED = "#0b0b0b", "#52514e", "#8a8880"
GRID, SURFACE = "#e3e2dd", "#fcfcfb"

#: Diverging ramp: cool for over-prediction, warm for under-prediction, neutral grey at zero.
DIVERGING = LinearSegmentedColormap.from_list(
    "resid", ["#2a78d6", "#9dc2ec", "#e8e8e4", "#f4b492", "#eb6834"])


def _style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, which="major", color=GRID, linewidth=0.8, zorder=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=8, length=3)
    ax.xaxis.label.set_color(INK_2)
    ax.yaxis.label.set_color(INK_2)


def fig_residual_heatmap(residuals, fractions, solutes, shot_labels):
    """1 — shot-level residual heatmap by solute and fraction."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    n = len(solutes)
    fig, axes = plt.subplots(1, n, figsize=(4.3 * n, 5.4), dpi=160, sharey=True)
    fig.patch.set_facecolor(SURFACE)
    vmax = max(np.abs(residuals[s]).max() for s in solutes)
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    for ax, sol in zip(np.atleast_1d(axes), solutes):
        R = residuals[sol]
        im = ax.imshow(R, aspect="auto", cmap=DIVERGING, norm=norm)
        ax.set_xticks(range(len(fractions)))
        ax.set_xticklabels(["f%d" % f for f in fractions], fontsize=8)
        ax.set_title(sol, color=INK, fontsize=10, loc="left", pad=6)
        ax.set_xlabel("fraction")
        ax.tick_params(colors=INK_2, labelsize=7.5, length=0)
        for sp in ax.spines.values():
            sp.set_visible(False)
    np.atleast_1d(axes)[0].set_yticks(range(len(shot_labels)))
    np.atleast_1d(axes)[0].set_yticklabels(shot_labels, fontsize=6.5)
    np.atleast_1d(axes)[0].set_ylabel("shot")
    cb = fig.colorbar(im, ax=list(np.atleast_1d(axes)), fraction=0.028, pad=0.02)
    cb.set_label("signed relative residual (%)   negative = model under-predicts", color=INK_2,
                 fontsize=8)
    cb.ax.tick_params(colors=INK_2, labelsize=7.5)
    cb.outline.set_visible(False)
    fig.suptitle("Shot-level residuals, current solver (EXPLORATORY)", color=INK, fontsize=11,
                 x=0.01, ha="left")
    path = FIG_DIR / "temporal_residual_heatmap.png"
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    return path


def fig_mean_residual_ci(per_fraction, fractions, solutes):
    """2 — mean residual with experiment-cluster bootstrap intervals."""
    fig, ax = plt.subplots(figsize=(7.8, 4.4), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    x = np.arange(len(fractions))
    for i, sol in enumerate(solutes):
        m = [per_fraction[sol]["fraction_%d" % f]["mean_signed_pct"] for f in fractions]
        lo = [per_fraction[sol]["fraction_%d" % f]["cluster_bootstrap"]["ci95"][0] for f in fractions]
        hi = [per_fraction[sol]["fraction_%d" % f]["cluster_bootstrap"]["ci95"][1] for f in fractions]
        off = (i - 1) * 0.16
        c = list(SERIES.values())[i]
        ax.errorbar(x + off, m, yerr=[np.array(m) - np.array(lo), np.array(hi) - np.array(m)],
                    fmt="o", markersize=7, color=c, ecolor=c, elinewidth=2.0, capsize=0,
                    label=sol, zorder=4 + i, markeredgecolor=SURFACE, markeredgewidth=1.2)
    ax.axhline(0.0, color=MUTED, linewidth=1.2, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(["f%d" % f for f in fractions])
    ax.set_xlabel("fraction")
    ax.set_ylabel("mean signed relative residual (%)")
    ax.set_title("Late-fraction means run negative, but every experiment-cluster interval "
                 "includes zero", color=INK, fontsize=10, loc="left", pad=6)
    ax.legend(fontsize=8, labelcolor=INK_2, loc="lower left", framealpha=1.0,
              facecolor=SURFACE, edgecolor="none")
    _style(ax)
    fig.tight_layout()
    path = FIG_DIR / "temporal_mean_residual_ci.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def fig_observed_vs_predicted(cases):
    """3 — observed versus predicted fraction curves, representative and worst cases."""
    n = len(cases)
    fig, axes = plt.subplots(1, n, figsize=(4.5 * n, 4.1), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for ax, c in zip(np.atleast_1d(axes), cases):
        ax.plot(c["mass_g"], c["observed"], marker="o", markersize=8, linewidth=0, color=INK,
                markeredgecolor=SURFACE, markeredgewidth=1.3, zorder=8, label="observed")
        for m in ORDER:
            if m in c["predicted"]:
                ax.plot(c["mass_g"], c["predicted"][m], marker="s", markersize=5, linewidth=1.8,
                        color=SERIES[m], markeredgecolor=SURFACE, markeredgewidth=0.9,
                        zorder=4, label=m)
        ax.set_yscale("log")
        ax.set_xlabel("fraction midpoint, cumulative beverage mass (g)")
        ax.set_ylabel("concentration (mg/g)")
        ax.set_title(c["title"], color=INK, fontsize=9.5, loc="left", pad=6)
        _style(ax)
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=7.5, labelcolor=INK_2)
    fig.suptitle("Observed versus predicted fraction curves (EXPLORATORY)", color=INK,
                 fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = FIG_DIR / "temporal_observed_vs_predicted.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def fig_heldout_late(comp, solutes):
    """4 — held-out late-fraction error by model and solute."""
    fig, ax = plt.subplots(figsize=(8.0, 4.4), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    x = np.arange(len(solutes))
    w = 0.19
    for i, m in enumerate(ORDER):
        vals = [comp["solutes"][s][m].get("late_fraction_mape", np.nan) for s in solutes]
        bars = ax.bar(x + (i - 1.5) * (w + 0.015), vals, w, color=SERIES[m], label=m, zorder=4,
                      edgecolor=SURFACE, linewidth=2.0)
        for b, v in zip(bars, vals):
            if np.isfinite(v):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.2, "%.1f" % v, ha="center",
                        fontsize=7, color=INK_2)
    ax.set_xticks(x)
    ax.set_xticklabels(solutes)
    ax.set_ylabel("held-out late-fraction MAPE (pp), f7 and f10")
    ax.set_title("Lower is better — the principal score is RAW fraction error", color=INK,
                 fontsize=10, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_2, ncol=2)
    _style(ax)
    fig.tight_layout()
    path = FIG_DIR / "temporal_heldout_late.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def fig_integrated_vs_raw(comp, solutes):
    """5 — integrated-target error versus raw-fraction error."""
    fig, ax = plt.subplots(figsize=(6.8, 4.8), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for m in ORDER:
        xs = [comp["solutes"][s][m].get("all_fraction_mape", np.nan) for s in solutes]
        ys = [comp["solutes"][s][m].get("derived_cumulative_mape", np.nan) for s in solutes]
        ax.scatter(xs, ys, s=80, color=SERIES[m], label=m, zorder=4, edgecolor=SURFACE,
                   linewidth=1.4)
        for xx, yy, lb in zip(xs, ys, solutes):
            ax.annotate(lb, (xx, yy), textcoords="offset points", xytext=(7, 4), fontsize=7,
                        color=INK_2)
    lim = max(ax.get_xlim()[1], ax.get_ylim()[1])
    ax.plot([0, lim], [0, lim], color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)), zorder=2)
    ax.set_xlabel("held-out RAW fraction MAPE (pp)")
    ax.set_ylabel("error against the DERIVED cumulative targets (pp)")
    ax.set_title("Integrated targets are far easier than raw fractions — points sit below the "
                 "diagonal", color=INK, fontsize=9.5, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_2)
    _style(ax)
    fig.tight_layout()
    path = FIG_DIR / "temporal_integrated_vs_raw.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def fig_parameter_stability(comp, solutes):
    """6 — fitted slow-tail parameter distributions across folds."""
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for ax, key, lab in zip(axes, ("alpha_slow", "rate_ratio"),
                            (r"$\alpha_{slow}$", "rate ratio")):
        for i, sol in enumerate(solutes):
            vals = comp["solutes"][sol]["SLOW_TAIL"]["parameter_stability"].get(key, [])
            c = list(SERIES.values())[i]
            ax.scatter(np.full(len(vals), i) + np.linspace(-0.12, 0.12, max(len(vals), 1)),
                       vals, s=60, color=c, zorder=4, edgecolor=SURFACE, linewidth=1.2)
        ax.set_xticks(range(len(solutes)))
        ax.set_xticklabels(solutes)
        ax.set_ylabel(lab)
        ax.set_title("%s across held-out folds" % lab, color=INK, fontsize=10, loc="left", pad=6)
        _style(ax)
    axes[1].set_yscale("log")
    fig.suptitle("Boundary-pinned parameters are not interpreted mechanistically", color=INK,
                 fontsize=10, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    path = FIG_DIR / "temporal_parameter_stability.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path


def fig_conservation(checks):
    """7 — cumulative mass and positivity checks."""
    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    labels = [c["label"] for c in checks]
    minfrac = [c["min_prediction"] for c in checks]
    ax.bar(np.arange(len(labels)), minfrac, 0.5, color=SERIES["SLOW_TAIL"], zorder=4,
           edgecolor=SURFACE, linewidth=2.0)
    ax.axhline(0.0, color=MUTED, linewidth=1.4, zorder=5)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=7.5, rotation=20, ha="right")
    ax.set_ylabel("minimum predicted concentration (unit inventory)")
    ax.set_title("Positivity: every configuration stays strictly above zero", color=INK,
                 fontsize=10, loc="left", pad=6)
    _style(ax)
    for i, c in enumerate(checks):
        ax.text(i, minfrac[i], "mono %s" % ("ok" if c["cumulative_monotone"] else "FAIL"),
                ha="center", va="bottom", fontsize=7, color=INK_2)
    fig.tight_layout()
    path = FIG_DIR / "temporal_conservation_checks.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    return path

#!/usr/bin/env python3
"""Figures for the exploratory scientific viability screen (Parts A and B).

    EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
    NOT_A_FROZEN_P0_GATE_RESULT

Palette: categorical slots 1-3 of the validated default (blue / orange / aqua), assigned in fixed
order and never cycled. Three slots clear the all-pairs CVD and normal-vision floors in light mode;
the aqua slot sits below 3:1 contrast on the light surface, so every figure ships with its numeric
table in the accompanying Markdown — that is the documented relief rule, not an omission.

One measure per axis, thin marks, recessive grid, legend whenever more than one series is drawn.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt          # noqa: E402
import numpy as np                       # noqa: E402

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "docs" / "paper1_resource" / "exploratory"
FIG_DIR = OUT_DIR / "figures"

#: Validated categorical slots (light mode), fixed order.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a")
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#8a8880"
GRID = "#e3e2dd"
SURFACE = "#fcfcfb"


def _style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(True, which="major", color=GRID, linewidth=0.8, zorder=0)
    ax.grid(True, which="minor", color=GRID, linewidth=0.4, alpha=0.6, zorder=0)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=8, length=3)
    ax.xaxis.label.set_color(INK_2)
    ax.yaxis.label.set_color(INK_2)


def _profile_axes(ax, kappa, J, group, J_ref, kappa_ref, t_rel10, t_abs25, J_inf, label_y=True):
    ax.plot(kappa, J, color=SERIES[0], linewidth=2.0, zorder=4, label=r"$J(\kappa)$ on $D_{WIDE}$")
    if J_ref is not None:
        ax.axhline(J_ref, color=MUTED, linewidth=1.0, linestyle=(0, (4, 3)), zorder=2,
                   label=r"$J_{ref}$")
        ax.axhline(t_rel10, color=SERIES[1], linewidth=1.4, linestyle=(0, (5, 3)), zorder=3,
                   label="10 % relative threshold")
        ax.axhline(t_abs25, color=SERIES[2], linewidth=1.4, linestyle=(0, (1, 2)), zorder=3,
                   label="0.25 pp absolute threshold")
        for k in kappa_ref:
            ax.plot([k], [J_ref], marker="o", markersize=5, color=MUTED,
                    markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=5)
    ax.axhline(J_inf, color=INK, linewidth=1.6, zorder=6, label=r"$J_\infty$ (analytical endpoint)")
    ax.plot([kappa[-1]], [J_inf], marker="D", markersize=7, color=INK,
            markeredgecolor=SURFACE, markeredgewidth=1.4, zorder=7, clip_on=False)
    ax.set_xscale("log")
    ax.set_xlim(kappa[0], kappa[-1])
    ax.set_xlabel(r"rate multiplier  $\kappa$")
    if label_y:
        ax.set_ylabel("profiled MAPE (percentage points)")
    ax.set_title(group, color=INK, fontsize=10, loc="left", pad=6)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi + 0.32 * (hi - lo))       # headroom for the legend
    _style(ax)


def part_a_figures(endpoint_json, profiles):
    """One profile figure per group, plus a compact six-panel summary."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(pathlib.Path(endpoint_json).read_text(encoding="utf-8"))
    written = []

    for g in data["groups"]:
        name = g["group"]
        kappa, J = profiles[name]["kappa"], profiles[name]["J"]
        J_ref = g["J_ref"]
        t_rel10 = g["conventions"]["rel_q010"]["threshold_point"] if J_ref else None
        t_abs25 = g["conventions"]["abs_a025"]["threshold_point"] if J_ref else None
        fig, ax = plt.subplots(figsize=(6.2, 4.0), dpi=160)
        fig.patch.set_facecolor(SURFACE)
        _profile_axes(ax, kappa, J, name, J_ref, g["kappa_ref"] or [], t_rel10, t_abs25, g["J_inf"])
        ax.legend(fontsize=7.5, loc="upper right", labelcolor=INK_2, framealpha=1.0,
              facecolor=SURFACE, edgecolor="none")
        if J_ref is None:
            ax.text(0.02, 0.04, "reference minimum unresolved", transform=ax.transAxes,
                    fontsize=8, color=SERIES[1],
                    bbox=dict(facecolor=SURFACE, edgecolor="none", pad=2.0))
        fig.tight_layout()
        path = FIG_DIR / ("endpoint_%s.png" % name.replace(":", "_"))
        fig.savefig(path, facecolor=SURFACE)
        plt.close(fig)
        written.append(path)

    fig, axes = plt.subplots(2, 3, figsize=(13.5, 7.2), dpi=150)
    fig.patch.set_facecolor(SURFACE)
    for ax, g in zip(axes.ravel(), data["groups"]):
        name = g["group"]
        kappa, J = profiles[name]["kappa"], profiles[name]["J"]
        J_ref = g["J_ref"]
        _profile_axes(ax, kappa, J, name, J_ref,
                      g["kappa_ref"] or [],
                      g["conventions"]["rel_q010"]["threshold_point"] if J_ref else None,
                      g["conventions"]["abs_a025"]["threshold_point"] if J_ref else None,
                      g["J_inf"], label_y=(ax in (axes[0][0], axes[1][0])))
        cls = g["conventions"]["rel_q010"]["endpoint_classification"]
        note = cls.replace("_", " ")
        if J_ref is None:
            note += "  (reference minimum unresolved)"
        ax.text(0.02, 0.04, note, transform=ax.transAxes, fontsize=8,
                color=SERIES[1] if cls != "endpoint_included" else SERIES[2],
                bbox=dict(facecolor=SURFACE, edgecolor="none", pad=2.0))
    axes[0][0].legend(fontsize=7, loc="upper right", labelcolor=INK_2, framealpha=1.0,
                      facecolor=SURFACE, edgecolor="none")
    fig.suptitle("Endpoint against the WIDE-referenced tolerance, six groups "
                 "(EXPLORATORY — not a frozen gate result)",
                 color=INK, fontsize=11, x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    path = FIG_DIR / "endpoint_summary_six_panel.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    written.append(path)
    return written


def part_b_figures(op_json, profiles, loeo, heldout_examples):
    """Profile overlays, accepted-width comparison, LOEO kappa spread, held-out shape, summary."""
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    data = json.loads(pathlib.Path(op_json).read_text(encoding="utf-8"))
    arms = data["arms"]
    written = []

    # 1 — profile overlay by solute
    solutes = [s["solute"] for s in data["solutes"]]
    fig, axes = plt.subplots(1, len(solutes), figsize=(4.6 * len(solutes), 4.0), dpi=160,
                             sharey=False)
    fig.patch.set_facecolor(SURFACE)
    for ax, sol in zip(np.atleast_1d(axes), solutes):
        for i, arm in enumerate(arms):
            p = profiles[(sol, arm)]
            ax.plot(p["kappa"], p["J"], color=SERIES[i], linewidth=2.0, zorder=4 + i, label=arm)
        ax.set_xscale("log")
        ax.set_xlabel(r"rate multiplier  $\kappa$")
        ax.set_ylabel("shot-balanced MAPE (pp)")
        ax.set_title(sol, color=INK, fontsize=10, loc="left", pad=6)
        _style(ax)
    np.atleast_1d(axes)[0].legend(frameon=False, fontsize=8, labelcolor=INK_2)
    fig.suptitle("Rate profiles by observation operator (EXPLORATORY)", color=INK, fontsize=11,
                 x=0.01, ha="left")
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    path = FIG_DIR / "operator_profiles_by_solute.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    written.append(path)

    # 2 — accepted-width comparison
    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    x = np.arange(len(solutes))
    width = 0.26
    for i, arm in enumerate(arms):
        vals = []
        for sol in solutes:
            rec = next(r for r in data["solutes"] if r["solute"] == sol)["arms"][arm]
            w = rec["accepted_log10_width_rel10"]
            vals.append(w if w is not None else np.nan)
        bars = ax.bar(x + (i - 1) * (width + 0.02), vals, width, color=SERIES[i], label=arm,
                      zorder=4, edgecolor=SURFACE, linewidth=2.0)
        for b, v in zip(bars, vals):
            if np.isfinite(v):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.03, "%.2f" % v, ha="center",
                        fontsize=7.5, color=INK_2)
    ax.set_xticks(x)
    ax.set_xticklabels(solutes)
    ax.set_ylabel(r"accepted-set width (decades of $\kappa$)")
    ax.set_title("Narrower is better localised — 10 % relative accepted set", color=INK,
                 fontsize=10, loc="left", pad=6)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_2)
    _style(ax)
    fig.tight_layout()
    path = FIG_DIR / "operator_accepted_width.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    written.append(path)

    # 3 — leave-one-experiment-out kappa distribution
    fig, ax = plt.subplots(figsize=(7.4, 4.2), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for i, arm in enumerate(arms):
        pts = []
        for j, sol in enumerate(solutes):
            ks = loeo.get((sol, arm), {}).get("fold_kappa", [])
            for k in ks:
                if k and k > 0:
                    pts.append((j + (i - 1) * 0.22, math.log10(k)))
        if pts:
            xs, ys = zip(*pts)
            ax.scatter(xs, ys, s=42, color=SERIES[i], label=arm, zorder=4 + i,
                       edgecolor=SURFACE, linewidth=1.2)
    ax.set_xticks(range(len(solutes)))
    ax.set_xticklabels(solutes)
    ax.set_ylabel(r"$\log_{10}\kappa$ per held-out fold")
    ax.set_title("Fold-to-fold stability of the fitted rate", color=INK, fontsize=10,
                 loc="left", pad=6)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_2)
    _style(ax)
    fig.tight_layout()
    path = FIG_DIR / "operator_loeo_kappa.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    written.append(path)

    # 4 — representative held-out temporal predictions
    if heldout_examples:
        n = len(heldout_examples)
        fig, axes = plt.subplots(1, n, figsize=(4.6 * n, 4.0), dpi=160)
        fig.patch.set_facecolor(SURFACE)
        for ax, ex in zip(np.atleast_1d(axes), heldout_examples):
            ax.plot(ex["mass_g"], ex["observed"], marker="o", markersize=7, linewidth=0,
                    color=INK, markeredgecolor=SURFACE, markeredgewidth=1.2, zorder=6,
                    label="observed")
            for i, arm in enumerate(("FRACTION_6", "CUP_CURVE_3")):
                if arm in ex["predicted"]:
                    ax.plot(ex["mass_g"], ex["predicted"][arm], marker="s", markersize=6,
                            linewidth=1.6, color=SERIES[i], markeredgecolor=SURFACE,
                            markeredgewidth=1.0, zorder=4 + i, label=arm)
            ax.set_xlabel("cumulative beverage mass (g)")
            ax.set_ylabel("concentration (mg/g)")
            ax.set_title(ex["title"], color=INK, fontsize=9.5, loc="left", pad=6)
            _style(ax)
        np.atleast_1d(axes)[0].legend(frameon=False, fontsize=8, labelcolor=INK_2)
        fig.suptitle("Held-out temporal shape: level anchored on the first observation only",
                     color=INK, fontsize=11, x=0.01, ha="left")
        fig.tight_layout(rect=(0, 0, 1, 0.94))
        path = FIG_DIR / "operator_heldout_shape.png"
        fig.savefig(path, facecolor=SURFACE)
        plt.close(fig)
        written.append(path)

    # 5 — localisation versus held-out error
    fig, ax = plt.subplots(figsize=(6.6, 4.6), dpi=160)
    fig.patch.set_facecolor(SURFACE)
    for i, arm in enumerate(arms):
        xs, ys, labels = [], [], []
        for sol in solutes:
            rec = next(r for r in data["solutes"] if r["solute"] == sol)["arms"][arm]
            w = rec["accepted_log10_width_rel10"]
            h = loeo.get((sol, arm), {}).get("heldout_mape")
            if w is not None and h is not None:
                xs.append(w)
                ys.append(h)
                labels.append(sol)
        if xs:
            ax.scatter(xs, ys, s=70, color=SERIES[i], label=arm, zorder=4 + i,
                       edgecolor=SURFACE, linewidth=1.4)
            for xx, yy, lb in zip(xs, ys, labels):
                ax.annotate(lb, (xx, yy), textcoords="offset points", xytext=(7, 4),
                            fontsize=7.5, color=INK_2)
    ax.set_xlabel(r"accepted-set width (decades of $\kappa$)  —  narrower is better localised")
    ax.set_ylabel("held-out temporal MAPE (pp)  —  lower is better")
    ax.set_title("Does better localisation cost prediction?", color=INK, fontsize=10,
                 loc="left", pad=6)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_2)
    _style(ax)
    fig.tight_layout()
    path = FIG_DIR / "operator_localisation_vs_heldout.png"
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    written.append(path)
    return written

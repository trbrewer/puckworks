"""Class-1 functional 2D diagrams — the honest, print-neutral figures.

Each draw takes (spec, outdir, ...) and returns {'id','thumb','outputs'}; it draws
onto a matplotlib figure, applies the badge/provenance stamp, and saves thumb.png.
matplotlib is the `[viz]` extra, imported lazily via `figures._plt` (this module
imports without it). These route through the SAME producers the paper figures use
(harness.kappa_t_ladder, the identifiability panel); `figures.py` /
`figures_paper_a.py` remain the canonical full-page paper figures (unchanged), so
`python -m puckworks.figures` still emits the same Paper-B PNGs.
"""
from __future__ import annotations
import os

import numpy as np

from ..figures import _plt, INK, ACCENT, NULL, GOOD, GRID
from .palette import BADGE_COLORS, STAGE_FILL, STAGE_EDGE
from .registry import save_figure


def _save_thumb(fig, spec, outdir, name="thumb.png"):
    return save_figure(fig, spec, outdir, name=name)


def draw_process_schematic(spec, outdir, with_3d=False, video=False):
    """The 6+ stage map: one box per registry stage, each carrying its OWN lens badge
    (per-stage labelling, Note 1). Data from the process_stages producer."""
    plt = _plt()
    stages = spec.producer.compute()["stages"]
    n = len(stages)
    fig, ax = plt.subplots(figsize=(min(13, 1.7 * n), 3.4))
    ax.set_xlim(0, n); ax.set_ylim(0, 1); ax.axis("off")
    for i, st in enumerate(stages):
        bc = BADGE_COLORS.get(st["badge"], NULL)
        ax.add_patch(plt.Rectangle((i + 0.06, 0.30), 0.88, 0.5,
                                   facecolor=STAGE_FILL, edgecolor=STAGE_EDGE, lw=1.4))
        ax.text(i + 0.5, 0.66, st["stage"], ha="center", va="center",
                fontsize=9, fontweight="bold", color=INK)
        # per-stage badge chip (the honest unit of labelling)
        ax.add_patch(plt.Rectangle((i + 0.06, 0.30), 0.88, 0.075, facecolor=bc,
                                   edgecolor="none"))
        ax.text(i + 0.5, 0.337, st["badge"].replace("EXPLORATORY_SIMULATION", "EXPLOR-SIM"),
                ha="center", va="center", fontsize=4.6, color="white", fontweight="bold")
        ax.text(i + 0.5, 0.22, st["component"], ha="center", va="top", fontsize=4.8,
                color=NULL, style="italic")
        if i < n - 1:
            ax.annotate("", xy=(i + 1.02, 0.55), xytext=(i + 0.96, 0.55),
                        arrowprops=dict(arrowstyle="-|>", color=NULL, lw=1.2))
    ax.set_title("Espresso process map — each stage its own lens & badge "
                 "(composite; not one mega-model)", loc="left", fontsize=10)
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}


def draw_shot_metric_frame(spec, outdir, with_3d=False, video=False):
    """P(t), Q(t), cumulative mass on a MEASURED pressure-controlled trace."""
    plt = _plt()
    d = spec.producer.compute()
    t = np.array([np.nan if x is None else x for x in d["t"]], float)
    P = np.array([np.nan if x is None else x for x in d["P"]], float)
    Q = np.array([np.nan if x is None else x for x in d["Q"]], float)
    m = np.array([np.nan if x is None else x for x in d["m"]], float)
    fig, ax = plt.subplots(figsize=(7.6, 4.0))
    ax.plot(t, P, color=ACCENT, lw=2.0, label="basket pressure [bar]")
    ax.set_xlabel("time [s]"); ax.set_ylabel("pressure [bar]", color=ACCENT)
    ax.tick_params(axis="y", labelcolor=ACCENT)
    ax2 = ax.twinx()
    ax2.plot(t, Q, color=GOOD, lw=1.8, label="mass flow [g/s]")
    ax2.plot(t, m / np.nanmax(m) * np.nanmax(Q), color=NULL, lw=1.2, ls="--",
             label="cumulative mass (scaled)")
    ax2.set_ylabel("mass flow [g/s]", color=GOOD); ax2.tick_params(axis="y", labelcolor=GOOD)
    ax2.grid(False)
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [l.get_label() for l in lines], loc="upper right", fontsize=7)
    ax.set_title("Measured shot — one public rig (OBSERVED, within-rig)", loc="left",
                 fontsize=10)
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}


def draw_kappa_t_ladder(spec, outdir, with_3d=False, video=False):
    """Compact κ(t) ladder: RMSE of each rung (routed through the same
    harness.kappa_t_ladder the full Paper-B Fig 3 uses). Full figure stays
    `figures.fig3_ladder` (unchanged)."""
    plt = _plt()
    r = spec.producer.compute()   # {phi_rmse, const_null, cubic}
    lad = __import__("puckworks.harness", fromlist=["kappa_t_ladder"]).kappa_t_ladder()
    rungs = [("best constant", lad["rung1_const_kappa"], NULL),
             ("static κ(P)", lad["rung3_static_kappaP"], NULL),
             ("Φ(t) poroelastic", lad["rung4_phi_of_t"], ACCENT),
             ("flexible cubic", lad["flexible_cubic_null"], GOOD)]
    fig, ax = plt.subplots(figsize=(6.8, 3.8))
    ys = np.arange(len(rungs))[::-1]
    ax.barh(ys, [x[1] for x in rungs], color=[x[2] for x in rungs], height=0.62)
    for y, (lab, val, _) in zip(ys, rungs):
        ax.text(val, y, f"  {val:.3f}", va="center", fontsize=8, color=INK)
    ax.set_yticks(ys); ax.set_yticklabels([x[0] for x in rungs], fontsize=8)
    ax.set_xlabel("RMSE [g/s] (15–95 s window)")
    ax.set_title("κ(t) null-first ladder — Φ(t) beats constants, TIES the cubic",
                 loc="left", fontsize=10)
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}


def draw_identifiability_valley(spec, outdir, with_3d=False, video=False):
    """Compact SSE-valley view (slow: routes through the identifiability panel the
    Paper-A Fig 2 uses). Local-only — the producer is a slow PDE analysis."""
    plt = _plt()
    res = spec.producer  # the slow identifiability Producer
    mod = __import__(res.module, fromlist=[res.function])
    panel = getattr(mod, res.function)(**res.kwargs)
    surf = panel["surface"]
    rates = np.array(surf["rates"], float); cs0 = np.array(surf["cs0"], float)
    S = np.array(surf["sse"], float)
    Jn = (S - S.min()) / S.min()
    RR, CC = np.meshgrid(rates, cs0, indexing="ij")
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    im = ax.contourf(RR, CC, Jn, levels=np.linspace(0, 2, 21), cmap="cividis",
                     extend="max")
    ax.contour(RR, CC, Jn, levels=[0.10], colors=[INK], linewidths=1.1, linestyles="--")
    ax.set_xscale("log")
    ax.set_xlabel("dimensionless rate scale (log)"); ax.set_ylabel("inventory c_s0 [g/L]")
    ax.set_title("Inventory↔kinetics SSE valley — a flat ridge (NON-identifiability)",
                 loc="left", fontsize=9)
    fig.colorbar(im, ax=ax, label="(J − Jmin)/Jmin")
    return {"id": spec.id, "thumb": _save_thumb(fig, spec, outdir),
            "outputs": ["thumb.png"]}

"""Plot only the authenticated decomposition table; never evaluate a model."""
from __future__ import annotations

import numpy as np

from .turnover_replay_decomposition_001 import MODELS, SCOPES


def figure(rows, output):
    """Stable-clock stacked flow contributions and observed total beverage flow."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    plt.rcParams.update({"font.size": 9, "svg.hashsalt": "TURNOVER_REPLAY_DECOMPOSITION_001"})
    fig, axes = plt.subplots(4, 3, figsize=(13, 13), sharex=True, sharey=True)
    colors = ("#4a9e9a", "#e49b48")
    for i, (model, scope) in enumerate((m, s) for m in MODELS for s in SCOPES):
        for j, pressure in enumerate((9., 11., 13.)):
            selected = sorted((r for r in rows if r["model"] == model and r["scope"] == scope
                and r["clock"] == "stable_pressure" and r["nominal_pressure_bar"] == pressure), key=lambda r: r["time_s"])
            t = np.array([r["time_s"] for r in selected])
            positive, negative = np.zeros(len(t)), np.zeros(len(t))
            for name, color in zip(("liquid", "solute"), colors):
                values = np.array([r[name+"_flow_g_s"] for r in selected])
                # Keep any negative observer contribution; never clip it out of the figure.
                up, down = np.maximum(values, 0), np.minimum(values, 0)
                axes[i, j].fill_between(t, positive, positive+up, color=color, alpha=.85)
                axes[i, j].fill_between(t, negative, negative+down, color=color, alpha=.85)
                positive += up
                negative += down
            axes[i, j].plot(t, [r["total_flow_g_s"] for r in selected], color="#225e5b", lw=1.3)
            axes[i, j].plot(t, [r["observed_flow_g_s"] for r in selected], "ko-", ms=3.3, lw=1.4)
            axes[i, j].axhline(0, color=".5", lw=.5)
            axes[i, j].grid(alpha=.15)
            axes[i, j].set_xticks([10, 40, 60, 100])
            if i == 0:
                axes[i, j].set_title(f"Nominal {pressure:g} bar")
            if j == 0:
                label = "A-J1 λ=1" if model == "A-J1" else "D0 diagnostic R0"
                label += "\n" + ("LOCO (pooled fits)" if scope == "LOCO" else "DESCRIPTIVE_ALL (in-sample)")
                axes[i, j].set_ylabel(label + "\nWindow flow (g/s)")
            if i == 3:
                axes[i, j].set_xlabel("Time since stable pressure (s)")
    handles = [Patch(facecolor=colors[0], alpha=.85, label="Predicted liquid contribution"),
               Patch(facecolor=colors[1], alpha=.85, label="Predicted discharged-solute contribution"),
               Line2D([], [], color="#225e5b", label="Predicted beverage total"),
               Line2D([], [], color="black", marker="o", label="Observed beverage total")]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .035), ncol=2, frameon=False)
    fig.suptitle("Saved Waszkiewicz replays: liquid and solute contributions", fontsize=14)
    fig.text(.5, .012, "2-s centered windows · unchanged native mass observer · connections guide the eye · observed mass has no measured split", ha="center", fontsize=9)
    fig.subplots_adjust(left=.14, right=.98, bottom=.13, top=.94, hspace=.18, wspace=.10)
    fig.savefig(output / "FLOW_DECOMPOSITION.svg", metadata={"Date": None})
    plt.close(fig)

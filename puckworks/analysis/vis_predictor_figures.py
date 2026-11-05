"""Render only released aggregates and shared fitted parameters for VIS-PREDICTOR-001."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np

from puckworks.empirical.visualizer import MODELS, log_capacity, load_model

OUT = Path(__file__).resolve().parents[2] / "docs/research/VIS_PREDICTOR_001"
CREDIT = "Visualizer and contributing public-shot users · reported signals · no physical validation"


def rows(name):
    with (OUT / name).open() as f:
        return list(csv.DictReader(f))


def main():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with plt.rc_context({"font.size": 10, "svg.hashsalt": "PW-VIS-PREDICTOR-001"}):
        contrasts = rows("CONTRASTS.csv")
        fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
        for ax, subset in zip(axes, ("overall", "pressure_varying")):
            values = [r for r in contrasts if r["subset"] == subset and r["metric"] == "rmse_g_s"]
            for i, row in enumerate(values):
                x, lo, hi = (float(row[k]) for k in ("difference", "low", "high"))
                ax.errorbar(x, i, xerr=[[x - lo], [hi - x]], fmt="o", color="#2166ac", capsize=3)
            ax.set_yticks(range(len(values)), [r["contrast"] for r in values])
            ax.axvline(0, color="0.55", lw=1)
            ax.set_title(subset.replace("_", " "))
            ax.set_xlabel("Paired mean RMSE difference (g/s)\nnegative favors first model")
            ax.grid(axis="x", alpha=.2)
        fig.suptitle("Early-calibrated later flow: complete-user bootstrap, 95% intervals")
        fig.text(.5, .01, CREDIT, ha="center", fontsize=8)
        fig.tight_layout(rect=(0, .05, 1, 1))
        fig.savefig(OUT / "PAIRED_DIFFERENCES.svg", metadata={"Date": None})
        plt.close(fig)

        panel = rows("AGGREGATED_EXAMPLE.csv")
        fig, ax = plt.subplots(figsize=(9, 4.5))
        for model in ("observed", *MODELS):
            values = [r for r in panel if r["model"] == model]
            ax.plot([float(r["start_s"]) + 1 for r in values],
                    [float(r["mean_flow_g_s"]) for r in values],
                    label=model, lw=2 if model == "observed" else 1.2,
                    color="black" if model == "observed" else None,
                    marker="o" if model == "observed" else None, markersize=3)
        ax.axvspan(0, 6, color="#92c5de", alpha=.3, label="calibration")
        ax.axvspan(6, 8, color="grey", alpha=.2, label="guard")
        ax.set(xlabel="Seconds from delivery onset (window midpoint)",
               ylabel="Equal-user mean reported flow (g/s)",
               title="Aggregated example: early calibration and frozen-amplitude later predictions")
        ax.legend(ncol=5, fontsize=8)
        ax.grid(alpha=.15)
        fig.text(.5, .025, "Changing supported cohort by time; mean curves can conceal large individual errors.",
                 ha="center", fontsize=8)
        fig.text(.5, .005, CREDIT, ha="center", fontsize=8)
        fig.tight_layout(rect=(0, .07, 1, 1))
        fig.savefig(OUT / "AGGREGATED_EXAMPLE.svg", metadata={"Date": None})
        plt.close(fig)

        fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
        pressure = np.linspace(0, 15, 500)
        for ax, model in zip(axes, ("M0R", "AR")):
            for fold in range(5):
                saved = load_model(OUT / "models" / f"fold_{fold}" / (model + ".json"))
                p = saved["parameters"]
                h = log_capacity(pressure, p["n"], p["Pd"], p.get("kappa", 0))
                # Shape comparison removes the arbitrary amplitude convention.
                reference = log_capacity(6.0, p["n"], p["Pd"], p.get("kappa", 0))
                ax.plot(pressure, np.exp(h - reference), label=f"fold {fold + 1}")
            ax.set(title=model, xlabel="Recorded machine pressure (bar)", ylabel="Capacity / capacity at 6 bar")
            ax.grid(alpha=.2)
            ax.legend(fontsize=8)
        fig.suptitle("Shared capacity curves; amplitude and mass recovery omitted")
        fig.text(.5, .01, CREDIT, ha="center", fontsize=8)
        fig.tight_layout(rect=(0, .05, 1, 1))
        fig.savefig(OUT / "CAPACITY_CURVES.svg", metadata={"Date": None})
        plt.close(fig)
    spec = dict(task="PW-VIS-PREDICTOR-001", evidence="empirical held-out-user reported-signal benchmark",
                claim_ceiling="No mechanism, causal law, universal peak or physical validation",
                registry="research-only task-local VizSpec; no production entry",
                figures=[dict(file="PAIRED_DIFFERENCES.svg", source="CONTRASTS.csv",
                              semantics="paired user means and complete-user bootstrap intervals"),
                         dict(file="AGGREGATED_EXAMPLE.svg", source="AGGREGATED_EXAMPLE.csv",
                              semantics="released aggregates, changing supported cohorts, not a shot trace"),
                         dict(file="CAPACITY_CURVES.svg", source="models/fold_*/*.json",
                              semantics="shared fitted shapes normalized at 6 bar, may extrapolate")],
                credit=CREDIT)
    (OUT / "VIZ_SPEC.json").write_text(json.dumps(spec, indent=2) + "\n")


if __name__ == "__main__":
    main()

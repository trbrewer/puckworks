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
    from . import data as d
    inv = {(r["variety"], r["species"]): r["C0_s_mg_L"] / 1000.0
           for r in d.angeloni_inventories()}
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"],
                                         stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        commit = "UNKNOWN"
    res = dict(
        source_commit=commit,
        table7=dict(caffeine=inv.get(("Arabica", "CF")),
                    trigonelline=inv.get(("Arabica", "TR"))),
        panel_caffeine=ab.identifiability_panel("Arabica", "caffeine"),
        panel_trigonelline=ab.identifiability_panel("Arabica", "trigonelline"),
        transfer=ab.validate_refit_granulometry(),
        joint=ab.joint_multigrind_fit(),
        loco=ab.loco_cv_refit(),
        positive_control=idn.identifiability_fractions_vs_cup(),
        full_cup_sim=idn.full_cup_simulation_identifiability(),
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
    """Fig 1 — study & evidence design: calibration -> O fit -> holdout -> transfer,
    with each arrow labelled by evidence type."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis("off")

    def box(x, y, w, h, text, fc="#f3ece2"):
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=INK, lw=1.3))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.2,
                wrap=True)

    def arrow(x0, y0, x1, y1, label, col):
        ax.annotate("", (x1, y1), (x0, y0),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6))
        ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 0.18, label, ha="center", fontsize=6.8,
                color=col, style="italic")

    box(0.2, 4.3, 2.3, 1.3, "Schmieder / Pannusch\nfraction kinetics\n(model calibration)")
    box(3.6, 4.3, 2.3, 1.3, "Angeloni O\non-grid fit\n(new calibration)")
    box(7.1, 4.3, 2.6, 1.3, "Held-out O conditions\n(leave-one-out CV)")
    box(3.6, 1.6, 2.3, 1.3, "Angeloni C / F\nfrozen transfer")
    box(7.1, 1.6, 2.6, 1.3, "Table 7 inventory\n(independent tie-breaker)")
    box(0.2, 1.6, 2.3, 1.3, "Fraction vs cup\n(in-sample verification)")

    arrow(2.5, 5.0, 3.6, 5.0, "calibration", NULL)
    arrow(5.9, 5.0, 7.1, 5.0, "internal holdout (CV)", GOOD)
    arrow(4.75, 4.3, 4.75, 2.9, "external prediction", ACCENT)
    arrow(5.9, 2.25, 7.1, 2.25, "external constraint", WARN)
    arrow(2.5, 4.5, 2.4, 2.9, "in-sample\nverification", "#4a6fa5")
    ax.text(5, 0.5, "Evidence types are colour-coded; the paper reports "
            "identification, transfer, and verification as SEPARATE properties.",
            ha="center", fontsize=7.2, color=NULL)
    fig.suptitle("Fig 1 — Paper A study & evidence design", y=0.98, fontsize=11,
                 fontweight="bold")
    return _save(fig, outdir, "fig1_design.png")


def fig2_objective_surface(results=None, outdir=OUTDIR):
    """Fig 2 — inventory-rate objective surface for caffeine & trigonelline: SSE
    contours, the profiled valley path, and the Table 7 inventory line."""
    import numpy as np
    r = _load(results); plt = _plt()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
    for ax, key, sol in ((axes[0], "panel_caffeine", "caffeine"),
                         (axes[1], "panel_trigonelline", "trigonelline")):
        p = r[key]; s = p["surface"]
        rates = np.array(s["rates"]); cs0 = np.array(s["cs0"]); S = np.array(s["sse"])
        RR, CC = np.meshgrid(rates, cs0, indexing="ij")
        lo = S.min()
        cs = ax.contourf(RR, CC, S, levels=np.linspace(lo, lo * 3, 14),
                         cmap="YlOrBr_r", extend="max")
        ax.contour(RR, CC, S, levels=[lo * 1.1], colors=[INK], linewidths=1.0)
        prof = p["profile"]
        ax.plot(prof["rates"], prof["c_star"], color=ACCENT, lw=2.0,
                label="profiled valley (c* per rate)")
        t7 = r["table7"].get(sol)
        if t7:
            ax.axhline(t7, color=GOOD, ls="--", lw=1.4, label="Table 7 inventory")
        ax.set_xscale("log")
        ax.plot(p["rate_star"], p["c_s0_star"], "o", color=INK, ms=6)
        ax.set_title("(%s) %s — cond. no. %s"
                     % ("a" if sol == "caffeine" else "b", sol,
                        int(p["condition_number"])))
        ax.set_xlabel("rate scale (log)"); ax.set_ylabel("inventory c_s0")
        _logclean(ax)
        ax.legend(fontsize=7, loc="upper right")
    fig.suptitle("Fig 2 — inventory-rate objective surface: a flat valley "
                 "(practical non-identifiability)", y=1.02, fontsize=10.5,
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
        ax.set_xlabel("observed (mg/g)"); ax.set_ylabel("predicted (mg/g)")
        ax.legend(fontsize=7.5, loc="upper left")
    lc = r["loco"]
    fig.suptitle("Fig 3 — leave-one-condition-out holdouts (pooled %.1f%%, median "
                 "%.1f%%, 95%% CI %s)" % (lc["pooled_loco_mean_mape"],
                 lc["pooled_loco_median_mape"], lc["pooled_loco_ci95"]),
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
        ax.set_xlabel("observed (mg/g)"); ax.set_ylabel("predicted (mg/g)")
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
    rows, labels = [], []
    for variety in ("Arabica", "Robusta"):
        for sol in ("caffeine", "trigonelline", "5CQA"):
            x = j[variety][sol]
            rows.append([x["joint_per_grind_mape"][g] for g in ("O", "C", "F")])
            bnd = " *" if x["joint_rate_at_boundary"] else ""
            labels.append(f"{variety[:3]}:{sol}{bnd}")
    M = np.array(rows, float)
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    im = ax.imshow(M, cmap="YlOrBr", aspect="auto", vmin=0, vmax=max(20, M.max()))
    ax.set_xticks(range(3)); ax.set_xticklabels(["O", "C", "F"])
    ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=7.5)
    for i in range(M.shape[0]):
        for k in range(M.shape[1]):
            ax.text(k, i, "%.0f" % M[i, k], ha="center", va="center", fontsize=7.5,
                    color=INK if M[i, k] < 0.6 * M.max() else "white")
    fig.colorbar(im, ax=ax, shrink=0.7, label="joint-fit MAPE (%)")
    ax.set_title("Fig 5 — joint shared-(c_s0,rate) residual by grind\n"
                 "pooled %d%% vs %d%% per-grind (cost ~%d pp); * = rate at boundary"
                 % (r["joint"]["mean_joint_pooled_mape"],
                    r["joint"]["mean_independent_per_grind_mape"],
                    r["joint"]["cost_of_sharing_pp"]), fontsize=9.5)
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
    fig.suptitle("Fig 6 — fraction scoring identifies the rate (sharp); the whole "
                 "cup does not (flat) — empirical + exact-integral simulation",
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

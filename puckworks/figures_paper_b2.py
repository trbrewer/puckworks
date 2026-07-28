"""figures_paper_b2.py — render the Paper 2 (temporal) figures from the committed results bundle.

Paper 2 review item 4.7 asked for residual diagnostics as a first-class result and the figure set
was specified but never built: the manuscript carried four figure specifications and four
"Figure N near here" placeholders, and there was no `figures_paper_b*` module at all.

Three properties are enforced rather than intended, following the pattern proven for the
identifiability and registry papers:

* **Every plotted numerical field comes from the committed bundle**, `docs/figures/
  paper_b_results.json` — the same object `paper_b2.build.verify` checks its registered claims
  against. Rendering therefore needs no re-analysis, and a plotted VALUE cannot disagree with a
  verified one.

  That is a narrower guarantee than the one this docstring used to make. It previously said
  "figures therefore cannot disagree with the claims", and carried a hard-coded count of 122 that
  had already drifted from the manifest. Both were wrong in the same way. A figure can reproduce a
  numeric field exactly while **mislabelling its estimand** — plotting the leave-in dispersion and
  captioning it a noise floor, or plotting a Fourier bin and captioning it a physical period. This
  repository has done both. Labels are therefore checked separately, by
  `tests/test_paper_b2_semantic_audit.py`, and the claim count is not restated here because a
  restated count is a thing that drifts.
* **Every data-bearing figure exports a tidy CSV**, so a reviewer can re-plot without the solver
  stack.
* **Every figure carries alt text**, because the finding must not be reachable only through the
  image.

One panel deserves a note. Figure 2c and the residual panels do not recompute predictions: the
bundle stores each branch's residual against the measured trace, so the prediction is recovered as
`measured − residual` on the declared 1 s diagnostic grid. That keeps the plotted curves identical
to the ones the diagnostics were computed from, rather than merely consistent with them.

Figure 4 is a **declared** prediction matrix, not a computed one, and says so on its face: the
mechanism-by-perturbation cells are qualitative expectations conditional on the cited model
structures, and no data from those protocols exists in the repository.

matplotlib is imported lazily (`_plt()`), so this module imports cleanly without the `[figures]`
extra.

Run:  python -m puckworks.figures_paper_b2        # -> docs/figures/paper_b2/
"""
from __future__ import annotations

import json
import os

from .figures import ACCENT, BAD, GOOD, GRID, INK, NULL, WARN, _plt, _save

OUTDIR = "docs/figures/paper_b2"
BUNDLE = "docs/figures/paper_b_results.json"

#: Branch key -> (display label, colour, line style). Status is never conveyed by colour alone:
#: every branch is also labelled directly on the axes.
BRANCHES = (
    ("rung1_const", "best constant", NULL, ":"),
    ("rung3_static", "static $\\kappa(P)$", WARN, "-."),
    ("rung4_phi_of_t", "empirical $\\Phi(t)$", ACCENT, "-"),
    ("flexible_cubic", "flexible cubic (in-sample)", GOOD, "--"),
)

#: Length of the residual-diagnostic window in seconds. The spectrum's frequency resolution is
#: 1/this, which is why k = 1 and k = 2 correspond to 80 s and 40 s -- a property of the window.
_WINDOW_LENGTH_S = 80

ALT_TEXT = {
    "fig1_machine_nonuniqueness":
        "Three panels on machine-side non-uniqueness. Panel a is a schematic of the Foster machine "
        "path: pump outlet, pipe resistance, trapped-air headspace, ponding height, wetting front "
        "and porous bed, with the four pressure nodes labelled explicitly. Panel b shows the "
        "reconstructed Foster normalised flow curve, which dips to a mid-shot minimum and recovers "
        "with no extraction-driven bed mechanism -- the bed state that does evolve is the wetted "
        "fraction, through sharp-front infiltration. Panel c shows the measured Waszkiewicz 9-bar "
        "rising-flow trace on its own axes, included only to establish that it is a separate "
        "evidence object that the Foster parameterisation does not fit. The take-away is that a "
        "machine-and-wetting system can generate a non-monotone flow shape, so a shape alone does "
        "not identify an extraction-driven bed mechanism.",
    "fig2_null_first_ladder":
        "Four panels on the null-first temporal ladder over the 15 to 95 second scoring window. "
        "Panel a shows the measured 9-bar flow trace with the predictions of the best constant, "
        "the static pressure-dependent branch, the empirical temporal trajectory and the flexible "
        "cubic overlaid. Panel b is a horizontal bar chart of reconstruction error by branch, each "
        "bar annotated with how many free parameters were fitted to the scored trace; the temporal "
        "trajectory fits none. Panel c shows residual against time for every branch on the "
        "declared one-second grid, with the pointwise between-shot band drawn behind so residuals "
        "can be read against shot-to-shot variability. Panel d shows conditional moving-block "
        "intervals for the temporal branch minus the best constant, which excludes zero, and minus "
        "the cubic, which does not. The cubic is labelled a same-trace descriptive comparator, not a "
        "predictive model.",
    "fig3_cross_pressure":
        "Four panels on cross-pressure assessment. Panel a shows per-pressure reconstruction error "
        "for the static, temporal and RC-3b branches against nominal pressure, with the band "
        "containing the primary 9-bar analysis marked; the best branch changes three times across "
        "the range. Panel b compares leave-one-pressure-out held-out errors, drawn with open "
        "markers, against shared-calibration errors for the same branches. Panel c shows the "
        "fitted equilibrium parameters when each pressure is omitted in turn, showing the "
        "calibration drift is small. Panel d shows the nominal setting against the recorded basket "
        "pressure at each condition, which is below nominal everywhere. The assessment is "
        "within-rig and conditional on a fixed dissolved-mass trajectory.",
    "fig4_residual_structure":
        "Three panels showing that every branch leaves coherent low-frequency lack of fit. "
        "Panel a shows the autocorrelation of each branch's residual across twenty lags, decaying "
        "slowly for every branch. Panel b shows the share of residual power in the lowest-frequency "
        "quarter of the spectrum, above 0.95 for all four branches. Panel c shows where each "
        "residual spectrum peaks: the two static branches at the first nonzero Fourier period of "
        "the window, eighty seconds, and both temporal branches at the second, forty seconds. "
        "Those two values are properties of the eighty-point window rather than measured "
        "timescales, and the paper withdraws the earlier reading of them as physical "
        "periodicities. The take-away is that the residual power sits at the lowest frequencies "
        "the window can express, for every branch.",
    "fig5_perturbation_matrix":
        "A declared prediction matrix with five candidate contributions as rows — machine and "
        "headspace response, dissolution-linked opening, fines migration and deposition, "
        "compaction and elastic recovery, and particle swelling — and five experimental "
        "perturbations as columns. Each cell states a directional or hysteresis expectation only. "
        "The figure is explicitly labelled as qualitative and conditional on the cited model "
        "structures: the repository contains no data from any of these protocols, so nothing here "
        "is a result.",
}

#: Figure 5 is DECLARED, not computed. Each cell is a directional expectation conditional on the
#: cited model structure, transcribed from the manuscript's Table 4 so the two cannot drift; a test
#: checks the row and column vocabulary against the manuscript.
PERTURBATIONS = ("Fixed-pressure\nforward trace", "Pressure step\nupward",
                 "Flow reversal at\nmatched |ΔP|", "Rebrew of\nspent puck",
                 "Depth-resolved\nend state")
MECHANISMS = ("Machine/headspace", "Dissolution opening", "Fines migration",
              "Compaction/recovery", "Particle swelling")
#: (mechanism, perturbation) -> a short directional token for the cell. Full prose stays in Table 4;
#: the figure carries the direction only, which is all the model structures support.
PREDICTIONS = {
    ("Machine/headspace", 0): "dip+recovery\nno extraction-driven\nbed change",
    ("Machine/headspace", 1): "immediate,\nrepeatable",
    ("Machine/headspace", 2): "apparatus-only",
    ("Machine/headspace", 3): "repeats",
    ("Machine/headspace", 4): "no signature",
    ("Dissolution opening", 0): "rising with\nmass removed",
    ("Dissolution opening", 1): "static jump",
    ("Dissolution opening", 2): "direction-\nindependent",
    ("Dissolution opening", 3): "near-flat",
    ("Dissolution opening", 4): "distributed",
    ("Fines migration", 0): "resistance ↑",
    ("Fines migration", 1): "remobilize/\nrestart",
    ("Fines migration", 2): "direction-\nASYMMETRIC",
    ("Fines migration", 3): "reopen +\nre-clog",
    ("Fines migration", 4): "outlet-side",
    ("Compaction/recovery", 0): "history-\ndependent",
    ("Compaction/recovery", 1): "transient\nstrain",
    ("Compaction/recovery", 2): "more\nsymmetric",
    ("Compaction/recovery", 3): "hysteresis",
    ("Compaction/recovery", 4): "strain profile",
    ("Particle swelling", 0): "resistance ↑",
    ("Particle swelling", 1): "own\ntimescale",
    ("Particle swelling", 2): "direction-\nindependent",
    ("Particle swelling", 3): "persists/\nrelaxes",
    ("Particle swelling", 4): "exposure\nprofile",
}
#: Cells whose direction DISCRIMINATES: the only column where the mechanisms disagree in sign
#: rather than in degree. Highlighted so the figure shows where an experiment would actually pay.
DISCRIMINATING = {("Fines migration", 2)}


def _bundle(path=BUNDLE):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _trace():
    """Measured 9-bar trace, from the intaken dataset (not from the manuscript)."""
    import numpy as np

    from puckworks import data as d
    rec = d.waszkiewicz_traces()[9.0]
    return (np.asarray(rec["time__s"], dtype=float),
            np.asarray(rec["mass_flow_rate__g_per_s"], dtype=float))


def _diagnostic_grid(b):
    """(time, measured, {branch: prediction}) on the DECLARED 1 s diagnostic grid.

    Predictions are recovered as measured - residual rather than recomputed, so the plotted curves
    are exactly the ones the residual diagnostics were computed from. Recomputing would give
    curves that merely ought to agree.
    """
    import numpy as np

    rd = b["shot_level"]["residuals_1s"]
    t = np.asarray(rd["time_s"], dtype=float)
    t_full, q_full = _trace()
    measured = np.interp(t, t_full, q_full)
    preds = {}
    for key, *_ in BRANCHES:
        resid = np.asarray(rd["branches"][key]["residual_vs_time_g_per_s"], dtype=float)
        preds[key] = measured - resid
    return t, measured, preds


# ---------------------------------------------------------------------------
def fig1_machine_nonuniqueness(outdir=OUTDIR):
    """Foster machine path can produce a non-monotone flow shape with no EXTRACTION-DRIVEN bed
    change.

    Its sharp wetting front does advance through an initially dry bed, so the wetted fraction and
    hydraulic path length evolve; the fourth review of Paper B2 was right that calling this
    "machine-only" or "no evolving bed" overstated the null. What is held fixed is the saturated-bed
    constitutive law: no swelling, fines migration, particle rearrangement or damage-induced
    permeability evolution.
    """
    import numpy as np

    from puckworks.models.foster2025 import machine_mode as fm
    from puckworks.validation.gates import gates_data

    plt = _plt()
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.4))

    # -- panel a: schematic of the machine path and its pressure nodes -------------------
    ax = axes[0]
    ax.set_title("a  Machine path and pressure nodes")
    ax.set_xlim(0, 1), ax.set_ylim(0, 1), ax.axis("off")
    nodes = [("pump\noutlet", 0.10, 0.80), ("pipe\nresistance", 0.34, 0.80),
             ("trapped-air\nheadspace", 0.60, 0.80), ("ponding\nheight", 0.60, 0.52),
             ("wetting\nfront", 0.60, 0.28), ("porous\nbed", 0.60, 0.08)]
    for label, x, y in nodes:
        ax.add_patch(plt.Rectangle((x - 0.09, y - 0.06), 0.18, 0.12,
                                   facecolor="white", edgecolor=INK, linewidth=0.9))
        ax.text(x, y, label, ha="center", va="center", fontsize=6.5)
    for (x0, y0), (x1, y1) in (((0.19, 0.80), (0.25, 0.80)), ((0.43, 0.80), (0.51, 0.80)),
                               ((0.60, 0.74), (0.60, 0.58)), ((0.60, 0.46), (0.60, 0.34)),
                               ((0.60, 0.22), (0.60, 0.14))):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
    ax.text(0.02, 0.58,
            "Node identity is documented,\nnot a typed contract field:\n"
            "a \u201c9 bar\u201d statement must\nname which node it means.",
            fontsize=6.2, style="italic", color=NULL, va="top")

    # -- panel b: reconstructed Foster normalised flow ----------------------------------
    ax = axes[1]
    # flow_minimum returns (Q_min/Q_m, t) -- value FIRST. Unpacking it as (t, Q) put the marker at
    # the top of the axes and mislabelled the annotation; the gate's own call is the reference.
    q_min, t_min = fm.flow_minimum()
    published = gates_data().foster_fig15_flow()
    pt = np.array([row["t_s"] for row in published])
    pq = np.array([row["Q_norm"] for row in published])
    ax.plot(pt, pq, "o", color=NULL, ms=2.2, alpha=0.55, label="published Fig 15")
    # Draw the reconstruction only over the interval the model covers -- [t_p, t_s] shifted -- which
    # is also the interval the gate scores. Extending it past t_s draws an extrapolation beside
    # published data and invites reading the divergence as disagreement.
    r = fm.solve()
    lo_t, hi_t = r["t_p"] + r["p"].t_shift, r["t_s"] + r["p"].t_shift
    tt = np.linspace(lo_t, hi_t, 400)
    qq = np.array([fm.bed_flow_norm(float(x), r) for x in tt])
    ax.plot(tt, qq, color=ACCENT, lw=1.8, label="repository reconstruction")
    ax.axvspan(hi_t, pt.max(), color=GRID, alpha=0.5, zorder=0)
    ax.text(hi_t + 0.15, 0.13, "outside the\nmodelled interval", fontsize=5.8, va="bottom",
            color=NULL, style="italic")
    ax.plot([t_min], [q_min], "o", color=BAD, ms=6, zorder=5)
    ax.annotate("minimum %.3f at %.2f s\n(no extraction-driven\nbed change)" % (q_min, t_min),
                xy=(t_min, q_min), xytext=(t_min + 1.4, q_min + 0.18),
                fontsize=7, color=BAD,
                arrowprops=dict(arrowstyle="->", color=BAD, lw=0.8))
    ax.set_title("b  Foster machine mode: published vs reconstruction")
    ax.set_xlabel("time (s)"), ax.set_ylabel("normalised bed flow")
    ax.legend(fontsize=6.6, loc="upper right")

    # -- panel c: the measured trace, deliberately on its own axes ----------------------
    ax = axes[2]
    t, q = _trace()
    ax.plot(t, q, color=INK, lw=1.4)
    ax.axvspan(15, 95, color=GRID, alpha=0.55, zorder=0)
    ax.set_title("c  Waszkiewicz 9-bar trace (separate object)")
    ax.set_xlabel("time (s)"), ax.set_ylabel("flow (g s$^{-1}$)")
    ax.text(0.98, 0.06, "NOT fitted by the Foster\nparameterisation", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=6.6, style="italic", color=NULL)

    fig.suptitle("Machine-side capacity for a flow shape is not a bed mechanism",
                 fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    return _save(fig, outdir, "fig1_machine_nonuniqueness.png")


def fig2_null_first_ladder(outdir=OUTDIR, bundle=None):
    """The ladder, its errors, its residuals, and the intervals that do and do not resolve."""
    import numpy as np

    b = bundle or _bundle()
    plt = _plt()
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.0))

    t, measured, preds = _diagnostic_grid(b)
    lad = b["ladder"]

    # -- a: measured trace with every branch overlaid -----------------------------------
    ax = axes[0, 0]
    ax.plot(t, measured, color=INK, lw=2.0, label="measured", zorder=5)
    for key, label, colour, style in BRANCHES:
        ax.plot(t, preds[key], color=colour, ls=style, lw=1.4, label=label)
    ax.set_title("a  Branch predictions on the 15–95 s window")
    ax.set_xlabel("time (s)"), ax.set_ylabel("flow (g s$^{-1}$)")
    ax.legend(fontsize=6.6, ncol=2, loc="lower right")

    # -- b: RMSE by branch with parameter provenance ------------------------------------
    ax = axes[0, 1]
    rows = [("best constant", lad["rung1_const_kappa"], 1),
            ("late-window constant", lad["rung1b_longrun_const"], 1),
            ("static $\\kappa(P)$", lad["rung3_static_kappaP"], 0),
            ("empirical $\\Phi(t)$", lad["rung4_phi_of_t"], 0),
            ("flexible cubic", lad["flexible_cubic_null"], 4)]
    ypos = np.arange(len(rows))[::-1]
    cols = [NULL, NULL, WARN, ACCENT, GOOD]
    ax.barh(ypos, [r[1] for r in rows], color=cols, height=0.6)
    for y, (label, val, nfree) in zip(ypos, rows):
        ax.text(val + 0.012, y, "%.3f   (%d fitted to this trace)" % (val, nfree),
                va="center", fontsize=6.8)
    ax.set_yticks(ypos), ax.set_yticklabels([r[0] for r in rows], fontsize=7.5)
    ax.set_xlim(0, max(r[1] for r in rows) * 1.55)
    ax.set_xlabel("RMSE (g s$^{-1}$)")
    ax.set_title("b  Error against free parameters fitted to the scored trace")
    ax.text(0.98, 0.06, "the cubic is a same-trace descriptive comparator,\nnot a predictive model",
            transform=ax.transAxes, ha="right", va="bottom", fontsize=6.6,
            style="italic", color=NULL)

    # -- c: residual vs time against the shot-to-shot band ------------------------------
    ax = axes[1, 0]
    band = b["shot_level"]["residuals_1s"]["between_shot_sd_mean_g_per_s"]
    ax.axhspan(-band, band, color=GRID, alpha=0.8, zorder=0,
               label="mean pointwise between-shot sd (±%.3f)" % band)
    ax.axhline(0.0, color=INK, lw=0.8)
    rd = b["shot_level"]["residuals_1s"]["branches"]
    for key, label, colour, style in BRANCHES:
        ax.plot(t, rd[key]["residual_vs_time_g_per_s"], color=colour, ls=style, lw=1.3,
                label=label)
    ax.set_title("c  Residuals at the declared 1 s resolution")
    ax.set_xlabel("time (s)"), ax.set_ylabel("residual (g s$^{-1}$)")
    ax.legend(fontsize=6.2, ncol=2, loc="lower right", framealpha=0.9, frameon=True)

    # -- d: moving-block intervals -------------------------------------------------------
    ax = axes[1, 1]
    r2 = b["result2_residuals"]
    items = [("$\\Phi(t)$ − best constant", r2["rmse_diff_phi_minus_best_const"], GOOD),
             ("$\\Phi(t)$ − cubic", r2["rmse_diff_phi_minus_cubic"], WARN)]
    for i, (label, rec, colour) in enumerate(items):
        lo, hi = rec["ci95"]
        ax.plot([lo, hi], [i, i], color=colour, lw=3.0, solid_capstyle="butt")
        ax.plot([rec["median"]], [i], "o", color=colour, ms=7, zorder=5)
        ax.text(hi + 0.02, i, "excludes zero" if rec["excludes_zero"] else "does NOT resolve",
                va="center", fontsize=7,
                color=(BAD if not rec["excludes_zero"] else INK))
    ax.axvline(0.0, color=INK, lw=1.0, ls="--")
    ax.set_yticks(range(len(items))), ax.set_yticklabels([i[0] for i in items], fontsize=7.5)
    ax.set_ylim(-0.6, len(items) - 0.1)
    ax.set_xlabel("RMSE difference (g s$^{-1}$); negative favours $\\Phi(t)$")
    ax.set_title("d  Conditional moving-block intervals (%d s blocks)" % r2["block_length_s"])

    fig.suptitle("Null-first temporal ladder on the 9-bar trace",
                 fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _save(fig, outdir, "fig2_null_first_ladder.png")


def fig3_cross_pressure(outdir=OUTDIR, bundle=None):
    """Per-pressure structure, LOPO-EC mean trace errors, calibration drift, and the nominal/recorded gap."""
    import numpy as np

    b = bundle or _bundle()
    plt = _plt()
    fig, axes = plt.subplots(2, 2, figsize=(11.0, 7.0))

    cp, lo = b["cross_pressure"], b["loco"]
    pressures = sorted(cp["per_pressure"], key=float)
    px = [float(p) for p in pressures]
    styles = (("static", "static $\\kappa(P)$", WARN, "-."),
              ("phi", "empirical $\\Phi(t)$", ACCENT, "-"),
              ("rc3b", "RC-3b variant", GOOD, "--"))

    # -- a: per-pressure RMSE; the winner changes ---------------------------------------
    ax = axes[0, 0]
    for key, label, colour, style in styles:
        ax.plot(px, [cp["per_pressure"][p][key] for p in pressures],
                marker="o", ms=4, color=colour, ls=style, lw=1.4, label=label)
    ax.axvspan(7, 11, color=GRID, alpha=0.7, zorder=0)
    ax.text(9, ax.get_ylim()[1] * 0.97, "band containing\nthe primary 9-bar analysis",
            ha="center", va="top", fontsize=6.6, style="italic", color=NULL)
    best = [min(styles, key=lambda s: cp["per_pressure"][p][s[0]])[1] for p in pressures]
    # Read the producer's field rather than recomputing. The figure and the producer had
    # DIFFERENT definitions of "rank change" -- the figure counted adjacent transitions (3), the
    # producer counted distinct winners minus one (2) -- so the bundle and the figure disagreed
    # depending on which a consumer read (fourth review 6.6). One definition, one source.
    from puckworks.analysis import waszkiewicz_cross_pressure as _wcp
    changes = _wcp.cross_pressure_heterogeneity()["n_rank_changes"]
    assert changes == sum(1 for i in range(1, len(best)) if best[i] != best[i - 1]), (
        "the producer's n_rank_changes disagrees with the winner sequence this panel plots")
    ax.set_title("a  Per-pressure RMSE — best branch changes %d times" % changes)
    ax.set_xlabel("nominal pressure (bar)"), ax.set_ylabel("RMSE (g s$^{-1}$)")
    ax.legend(fontsize=6.8)

    # -- b: held-out vs shared calibration ----------------------------------------------
    ax = axes[0, 1]
    keys = [s[0] for s in styles]
    xs = np.arange(len(keys))
    ax.bar(xs - 0.18, [lo["shared_calibration_mean"][k] for k in keys], width=0.34,
           color=[s[2] for s in styles], label="shared calibration")
    ax.bar(xs + 0.18, [lo["heldout_mean"][k] for k in keys], width=0.34,
           facecolor="white", edgecolor=[s[2] for s in styles], linewidth=1.6, hatch="//",
           label="leave-one-pressure-out (held out)")
    for x, k in zip(xs, keys):
        ax.text(x - 0.18, lo["shared_calibration_mean"][k] + 0.008,
                "%.3f" % lo["shared_calibration_mean"][k], ha="center", fontsize=6.6)
        ax.text(x + 0.18, lo["heldout_mean"][k] + 0.008,
                "%.3f" % lo["heldout_mean"][k], ha="center", fontsize=6.6)
    ax.set_xticks(xs), ax.set_xticklabels([s[1] for s in styles], fontsize=7.2)
    ax.set_ylabel("mean trace RMSE (g s$^{-1}$)")
    ax.set_title("b  LOPO-EC mean trace errors track shared calibration")
    ax.legend(fontsize=6.6)

    # -- c: calibration drift when each pressure is omitted -----------------------------
    ax = axes[1, 0]
    # RELATIVE drift, not absolute. On absolute axes a 2.2 % excursion in P_c fills the panel and
    # reads as instability; the claim is about the fraction, so plot the fraction and draw the
    # stated bound beside it.
    pc = np.array([lo["per_pressure"][p]["P_c"] for p in pressures], dtype=float)
    qc = np.array([lo["per_pressure"][p]["Q_c"] for p in pressures], dtype=float)
    # Reference the ALL-PRESSURE fit, which is what `max_calibration_drift` is measured against.
    # Referencing the median of the leave-one-out fits instead put a point at -3.0 %, outside the
    # stated +-2.83 % band -- a panel contradicting its own title.
    pdom = b["shot_level"]["pressure_domains"]
    pc_ref = float(pdom["fitted_equilibrium_P_c_bar"])
    qc_ref = float(pdom["fitted_equilibrium_Q_c_g_per_s"])
    bound = 100 * lo["max_calibration_drift"]
    ax.axhspan(-bound, bound, color=GRID, alpha=0.65, zorder=0,
               label="stated bound \u00b1%.1f%%" % bound)
    ax.axhline(0.0, color=INK, lw=0.8)
    ax.plot(px, 100 * (pc - pc_ref) / pc_ref, "o-", color=WARN, ms=4, lw=1.4,
            label="$P_c$ drift")
    ax.plot(px, 100 * (qc - qc_ref) / qc_ref, "s--", color=GOOD, ms=4, lw=1.4,
            label="$Q_c$ drift")
    ax.set_xlabel("pressure omitted (bar)")
    ax.set_ylabel("drift from all-pressure fit (%)")
    ax.set_ylim(-bound * 2.2, bound * 2.2)
    ax.set_title("c  Equilibrium calibration drift \u2264 %.1f%%" % bound)
    ax.legend(fontsize=6.8, loc="upper left")

    # -- d: nominal vs recorded basket pressure -----------------------------------------
    ax = axes[1, 1]
    pd_ = b["shot_level"]["pressure_domains"]
    nominal = sorted(float(p) for p in pd_["recorded_basket_pressure_mean_bar"])
    recorded = [pd_["recorded_basket_pressure_mean_bar"][str(p)] for p in nominal]
    ax.plot(nominal, nominal, color=NULL, ls=":", lw=1.2, label="nominal = recorded")
    ax.plot(nominal, recorded, "o-", color=BAD, ms=4, lw=1.5, label="recorded basket pressure")
    for n, r in zip(nominal, recorded):
        ax.plot([n, n], [r, n], color=BAD, lw=0.7, alpha=0.5)
    ax.set_xlabel("nominal setting (bar)"), ax.set_ylabel("recorded basket pressure (bar)")
    ax.set_title("d  Recorded is below nominal everywhere (max %.2f bar)"
                 % pd_["max_nominal_recorded_gap_bar"])
    ax.legend(fontsize=6.8, loc="upper left")

    fig.suptitle("Cross-pressure assessment: within-rig, conditional on a fixed "
                 "dissolved-mass trajectory", fontsize=10, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return _save(fig, outdir, "fig3_cross_pressure.png")


def fig4_residual_structure(outdir=OUTDIR, bundle=None):
    """Every branch leaves residual power in the lowest resolvable frequency bins of the window.

    This docstring used to say the residuals "drift, they do not oscillate -- and the branches
    differ in period". The Results withdrew both readings: on an 80-point, 1 s-decimated series,
    80 s and 40 s are simply the first and second nonzero Fourier periods available, so they are
    properties of the window, not measured timescales, and the transform cannot separate drift from
    oscillation over a single window. The figure said one thing while §5.4 said another (fourth
    review 6.4). Panel (c) now plots the spectral INDEX k, with the period shown only as a
    parenthetical property of the window.
    """
    import numpy as np

    b = bundle or _bundle()
    plt = _plt()
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 3.6))
    rd = b["shot_level"]["residuals_1s"]["branches"]

    # -- a: ACF across lags ---------------------------------------------------------------
    ax = axes[0]
    for key, label, colour, style in BRANCHES:
        acf = rd[key]["acf_by_lag"]
        ax.plot(range(1, len(acf) + 1), acf, color=colour, ls=style, lw=1.4, label=label)
    ax.axhline(0.0, color=INK, lw=0.8)
    ax.set_xlabel("lag (s)"), ax.set_ylabel("autocorrelation")
    ax.set_title("a  Slow decay in every branch")
    ax.legend(fontsize=6.2, loc="upper right")
    # The two constant-level branches differ only by an offset, so their CENTRED residuals -- and
    # therefore every diagnostic here -- are identical by construction. Without this note the
    # overplotted curve reads as a missing one.
    coincide = np.allclose(rd["rung1_const"]["acf_by_lag"], rd["rung3_static"]["acf_by_lag"],
                           atol=1e-9)

    # -- b: share of power at the slow end -----------------------------------------------
    ax = axes[1]
    keys = [k for k, *_ in BRANCHES]
    shares = [rd[k]["spectrum"]["power_in_slowest_quarter"] for k in keys]
    ax.bar(range(len(keys)), shares, color=[c for _, _, c, _ in BRANCHES])
    for i, s in enumerate(shares):
        ax.text(i, s + 0.012, "%.3f" % s, ha="center", fontsize=7)
    ax.axhline(0.95, color=BAD, ls="--", lw=1.0)
    ax.text(-0.46, 0.945, "0.95", ha="left", va="top", fontsize=6.6, color=BAD)
    ax.set_xticks(range(len(keys)))
    ax.set_xticklabels([lab for _, lab, _, _ in BRANCHES], fontsize=6.4, rotation=18,
                       ha="right")
    ax.set_ylim(0, 1.12), ax.set_ylabel("power in lowest-frequency quarter of bins")
    ax.set_title("b  Low-frequency concentration")

    # -- c: spectral INDEX k of the peak bin. Plotting seconds invited exactly the physical
    # reading the Results withdraw, so the axis is the bin index and the period appears only as a
    # parenthetical window property (fourth review 6.4).
    ax = axes[2]
    window_s = float(_WINDOW_LENGTH_S)
    periods = [rd[k]["spectrum"]["peak_bin_period_s"] for k in keys]
    ks = [rd[k]["spectrum"]["peak_bin_index"] for k in keys]
    ax.barh(np.arange(len(keys))[::-1], ks, color=[c for _, _, c, _ in BRANCHES], height=0.6)
    for y, (kk, pp) in zip(np.arange(len(keys))[::-1], zip(ks, periods)):
        ax.text(kk + 0.08, y, "k = %d  (= %g s of an %g s window)" % (kk, pp, window_s),
                va="center", fontsize=6.4)
    ax.set_yticks(np.arange(len(keys))[::-1])
    ax.set_yticklabels([lab for _, lab, _, _ in BRANCHES], fontsize=6.8)
    ax.set_xlim(0, max(ks) * 2.9 if ks else 1)
    ax.set_xticks(range(0, max(ks) + 2 if ks else 2))
    ax.set_xlabel("spectral index $k$ of the peak bin (resolution $1/%g$ Hz)" % window_s)
    ax.set_title("c  Peak bin index")

    fig.suptitle("Residual power sits in the lowest resolvable frequency bins of the "
                 "%g s window" % window_s, fontsize=10, fontweight="bold")
    note = ("The series has %d points at 1 s, so the frequency resolution is 1/%g Hz and k = 1 and "
            "k = 2 are the first two nonzero bins available. The bars locate a BIN INDEX, not a "
            "physical periodicity: this panel shows coherent low-frequency lack of fit and does "
            "not distinguish drift from oscillation."
            % (int(window_s), window_s))
    if coincide:
        note += ("\nThe best constant and static $\\kappa(P)$ curves coincide exactly in a and b: "
                 "both leave a constant-offset residual, so every centred diagnostic is identical "
                 "by construction.")
    fig.text(0.5, 0.015, note, ha="center", fontsize=6.5, style="italic", color=NULL)
    fig.tight_layout(rect=(0, 0.10, 1, 0.92))
    return _save(fig, outdir, "fig4_residual_structure.png")


def fig5_perturbation_matrix(outdir=OUTDIR):
    """DECLARED, not computed: directional expectations conditional on the cited model structures."""
    plt = _plt()
    fig, ax = plt.subplots(figsize=(11.0, 4.6))
    ax.set_xlim(0, len(PERTURBATIONS)), ax.set_ylim(0, len(MECHANISMS))
    ax.set_xticks([i + 0.5 for i in range(len(PERTURBATIONS))])
    ax.set_xticklabels(PERTURBATIONS, fontsize=7)
    ax.set_yticks([i + 0.5 for i in range(len(MECHANISMS))])
    ax.set_yticklabels(MECHANISMS[::-1], fontsize=7.6)
    ax.grid(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)

    for row, mech in enumerate(MECHANISMS[::-1]):
        for col in range(len(PERTURBATIONS)):
            cell = PREDICTIONS[(mech, col)]
            hot = (mech, col) in DISCRIMINATING
            ax.add_patch(plt.Rectangle((col + 0.02, row + 0.02), 0.96, 0.96,
                                       facecolor=("#fdf0e6" if hot else "white"),
                                       edgecolor=(BAD if hot else GRID),
                                       linewidth=(1.6 if hot else 0.9)))
            ax.text(col + 0.5, row + 0.5, cell, ha="center", va="center", fontsize=6.3,
                    color=(BAD if hot else INK), fontweight=("bold" if hot else "normal"))

    ax.set_title("Mechanism-by-perturbation prediction matrix — DECLARED, not measured",
                 fontsize=10, fontweight="bold", pad=14)
    fig.text(0.01, 0.015,
             "Every cell is a qualitative directional expectation conditional on the cited model "
             "structure. The repository contains NO data from any of these protocols, so no cell "
             "is a result.\nHighlighted: flow reversal is the one column where the candidates "
             "differ in SIGN rather than in degree — a deposited outlet layer becomes an "
             "upstream structure, the others do not.",
             fontsize=6.4, style="italic", color=NULL)
    fig.tight_layout(rect=(0, 0.075, 1, 1))
    return _save(fig, outdir, "fig5_perturbation_matrix.png")


FIGURES = (fig1_machine_nonuniqueness, fig2_null_first_ladder, fig3_cross_pressure,
           fig4_residual_structure, fig5_perturbation_matrix)


def render_all(outdir=OUTDIR):
    return [f(outdir=outdir) for f in FIGURES]


def export_source_data(outdir=OUTDIR, bundle=None):
    """Tidy CSVs behind every data-bearing figure, from the same bundle the figures render from."""
    import csv

    b = bundle or _bundle()
    sub = os.path.join(outdir, "source_data")
    os.makedirs(sub, exist_ok=True)
    written = []

    def _w(name, header, rows):
        path = os.path.join(sub, name)
        with open(path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        written.append(path)

    t, measured, preds = _diagnostic_grid(b)
    rd = b["shot_level"]["residuals_1s"]["branches"]
    _w("fig2_predictions_and_residuals.csv",
       ["time_s", "measured_g_per_s"]
       + [f"{k}_prediction_g_per_s" for k, *_ in BRANCHES]
       + [f"{k}_residual_g_per_s" for k, *_ in BRANCHES],
       [[round(float(t[i]), 3), round(float(measured[i]), 4)]
        + [round(float(preds[k][i]), 4) for k, *_ in BRANCHES]
        + [rd[k]["residual_vs_time_g_per_s"][i] for k, *_ in BRANCHES]
        for i in range(len(t))])

    lad = b["ladder"]
    _w("fig2_ladder_rmse.csv", ["branch", "rmse_g_per_s", "free_params_fitted_to_scored_trace"],
       [["best_constant", lad["rung1_const_kappa"], 1],
        ["late_window_constant", lad["rung1b_longrun_const"], 1],
        ["static_kappa_P", lad["rung3_static_kappaP"], 0],
        ["empirical_phi_of_t", lad["rung4_phi_of_t"], 0],
        ["flexible_cubic", lad["flexible_cubic_null"], 4]])

    r2 = b["result2_residuals"]
    _w("fig2_block_intervals.csv", ["comparison", "median", "ci95_lo", "ci95_hi", "excludes_zero"],
       [[name, rec["median"], rec["ci95"][0], rec["ci95"][1], rec["excludes_zero"]]
        for name, rec in (("phi_minus_best_const", r2["rmse_diff_phi_minus_best_const"]),
                          ("phi_minus_cubic", r2["rmse_diff_phi_minus_cubic"]))])

    cp, lo = b["cross_pressure"], b["loco"]
    _w("fig3_per_pressure.csv",
       ["pressure_bar", "static", "phi", "rc3b", "heldout_P_c_bar", "heldout_Q_c_g_per_s"],
       [[p, cp["per_pressure"][p]["static"], cp["per_pressure"][p]["phi"],
         cp["per_pressure"][p]["rc3b"], lo["per_pressure"][p]["P_c"],
         lo["per_pressure"][p]["Q_c"]]
        for p in sorted(cp["per_pressure"], key=float)])

    pd_ = b["shot_level"]["pressure_domains"]
    _w("fig3_nominal_vs_recorded.csv", ["nominal_bar", "recorded_mean_bar", "gap_bar"],
       [[p, pd_["recorded_basket_pressure_mean_bar"][p], pd_["nominal_minus_recorded_bar"][p]]
        for p in sorted(pd_["recorded_basket_pressure_mean_bar"], key=float)])

    # Column names say what the quantity IS: a bin index and a partition of the available bins.
    # `peak_bin_period_s` is retained but named as the window property it is (fourth review 6.4).
    _w("fig4_residual_structure.csv",
       ["branch", "lag1_acf", "durbin_watson", "power_in_slowest_quarter_of_available_bins",
        "peak_bin_index_k", "frequency_resolution_hz", "peak_bin_period_s_window_property"],
       [[k, rd[k]["lag1_autocorrelation"], rd[k]["durbin_watson"],
         rd[k]["spectrum"]["power_in_slowest_quarter_of_bins"],
         rd[k]["spectrum"]["peak_bin_index"],
         rd[k]["spectrum"]["frequency_resolution_hz"],
         rd[k]["spectrum"]["peak_bin_period_s"]] for k, *_ in BRANCHES])

    _w("fig4_acf_by_lag.csv", ["lag_s"] + [k for k, *_ in BRANCHES],
       [[lag + 1] + [rd[k]["acf_by_lag"][lag] for k, *_ in BRANCHES]
        for lag in range(len(rd[BRANCHES[0][0]]["acf_by_lag"]))])

    _w("fig5_perturbation_matrix.csv", ["mechanism", "perturbation", "declared_prediction",
                                        "discriminating"],
       [[mech, PERTURBATIONS[col].replace("\n", " "), PREDICTIONS[(mech, col)].replace("\n", " "),
         (mech, col) in DISCRIMINATING]
        for mech in MECHANISMS for col in range(len(PERTURBATIONS))])

    return written


def write_alt_text(outdir=OUTDIR):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "ALT_TEXT.md")
    lines = ["# Paper 2 — figure text alternatives", "",
             "Each entry states what the figure shows and what the reader should take from it, so "
             "no finding is reachable only through the image.", ""]
    for stem, alt in ALT_TEXT.items():
        lines += ["## `%s`" % stem, "", alt, ""]
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    return path


def main(argv=None):                                          # pragma: no cover
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.figures_paper_b2")
    p.add_argument("--out", default=OUTDIR)
    a = p.parse_args(argv)
    print("rendered:", render_all(outdir=a.out))
    print("source data:", export_source_data(outdir=a.out))
    print("alt text:", write_alt_text(outdir=a.out))


if __name__ == "__main__":                                    # pragma: no cover
    main()

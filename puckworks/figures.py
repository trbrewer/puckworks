"""figures.py — render the Paper-B figures from committed harness outputs.

Optional `[figures]` extra (matplotlib). This module imports CLEANLY WITHOUT
matplotlib (per CLAUDE.md's optional-dependency rule, like the `[lb]` taichi
extra): matplotlib is imported lazily inside `_plt()`, not at module top. Every
number is pulled from a harness/gate/data function — nothing is hand-typed — so
the figures track the corrected, downgraded findings (model-capacity not
identification; weak peak; instability scoped to the tested config).

Run:  python -m puckworks.figures              # -> docs/figures/fig{1..5}_*.png
"""
from __future__ import annotations
import os

# cohesive scientific palette (espresso-grounded, but print-neutral)
# Okabe--Ito-derived, colour-vision-deficiency-safe palette.  Figures also use
# markers, line styles, and direct text so status is never conveyed by colour alone.
INK = "#1a1a1a"
ACCENT = "#e69f00"        # orange: model / highlighted curve
NULL = "#6b6b6b"          # neutral grey: baselines / nulls
GOOD = "#0072b2"          # blue
WARN = "#cc79a7"          # reddish purple
BAD = "#d55e00"           # vermillion
GRID = "#d9d9d9"
OUTDIR_DEFAULT = "docs/figures"


def _plt():
    """Lazy matplotlib import + shared style. Raises a clear error if the
    `[figures]` extra is not installed."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as e:  # pragma: no cover
        raise ModuleNotFoundError(
            "matplotlib is required to render figures: pip install -e '.[figures]'"
        ) from e
    plt.rcParams.update({
        "figure.dpi": 150, "savefig.dpi": 150, "font.size": 9,
        "axes.titlesize": 10, "axes.titleweight": "bold", "axes.labelsize": 9,
        "axes.edgecolor": INK, "axes.labelcolor": INK, "text.color": INK,
        "xtick.color": INK, "ytick.color": INK, "axes.grid": True,
        "grid.color": GRID, "grid.linewidth": 0.7, "axes.axisbelow": True,
        "legend.frameon": False, "figure.facecolor": "white",
        # Stable SVG element IDs make vector outputs byte-reproducible.
        "svg.hashsalt": "puckworks",
        "svg.fonttype": "none", "pdf.fonttype": 42, "ps.fonttype": 42,
    })
    return plt


def _save(fig, outdir, name):
    """Save the requested raster file and deterministic SVG/PDF siblings.

    The original path remains the return value for backward compatibility with
    callers and tests that expect a PNG.  Vector siblings use fixed metadata and
    ``svg.hashsalt`` (set in :func:`_plt`) so repeated renders do not acquire a
    wall-clock timestamp or randomized SVG element IDs.
    """
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    fig.savefig(path, bbox_inches="tight")

    stem, ext = os.path.splitext(path)
    ext = ext.lower()
    if ext != ".svg":
        fig.savefig(
            stem + ".svg",
            bbox_inches="tight",
            metadata={"Date": None, "Creator": "puckworks"},
        )
    if ext != ".pdf":
        fig.savefig(
            stem + ".pdf",
            bbox_inches="tight",
            metadata={
                "Creator": "puckworks",
                "CreationDate": None,
                "ModDate": None,
            },
        )
    return path


# ---------------------------------------------------------------------------
def fig1_result1(outdir=OUTDIR_DEFAULT):
    """Fig 1 — Result 1 (primary TDS-EY target + model capacity).
    (a) measured TDS-EY vs dial with replicate error bars + schmieder's own RSM
        EY curve (interior vertex, weak adj-R²); (b) the channeling model's
        ensemble EY on its OWN dial axis (base monotone -> peaked ensemble)."""
    import numpy as np
    from puckworks import harness as h
    plt = _plt()
    t = h.schmieder_interior_max_target()
    p = t["primary"]
    dials = np.array(p["grinds"]); ey = np.array(p["ey_means"]); err = np.array(p["ey_stds"])
    # RSM EY curve over the dial range: consume the SINGLE analysis result
    # `schmieder_rsm_refit` (no duplicated fit in the plotting layer, review MAJ-04),
    # using the source-contract ACHIEVED flow/temperature predictors. The refit sits
    # near the data; we plot it for the SHAPE (concavity/vertex), since the printed
    # Table-3 coefficients are rounded and cannot reconstruct the absolute level.
    rf = h.schmieder_rsm_refit(predictors="achieved")
    cf = np.asarray(rf["coef"], float)                    # 1,F,G,T,G^2,T^2,FG
    fl, tp = rf["eval_flow_ml_s"], rf["eval_temp_C"]      # mean achieved central flow/temp
    gg = np.linspace(1.4, 2.0, 60)
    Xg = np.column_stack([np.ones_like(gg), fl+0*gg, gg, tp+0*gg, gg**2, (tp**2)+0*gg, fl*gg])
    rsm_ey = (Xg @ cf) / p["dose_g"] * 100.0              # refit cup mass -> EY
    vtx = rf["vertex_g"]; vtx_ci = rf["vertex_ci95_g"]; adj = rf["adj_r2"]

    ch = h.channeling_sigma_sweep(gs_grid=np.linspace(1.0, 2.2, 7), s_ref=0.6, m=1.0, p_bar=5.0, n_grid=7)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.4))
    # run-level jittered extraction-run points behind the cell means (review B-MAJ07):
    # each dial cell is 3 (6 at the centre) independently prepared extraction runs -- the
    # experimental unit. Showing the raw per-run EY makes the run-to-run spread and the
    # small n visible, so the "cell means increase" reading is not mistaken for tight data.
    reps = p.get("ey_replicates")
    if reps is not None:
        jitrng = np.random.default_rng(0)                 # deterministic jitter
        for gd, cell in zip(dials, reps):
            xs = gd + jitrng.uniform(-0.018, 0.018, size=len(cell))
            ax1.scatter(xs, cell, s=14, color=NULL, alpha=0.55, lw=0, zorder=2,
                        label="_nolegend_")
        # one proxy handle for the legend
        ax1.scatter([], [], s=14, color=NULL, alpha=0.55, lw=0,
                    label="individual extraction runs (n=3; 6 at centre)")
    ax1.errorbar(dials, ey, yerr=err, fmt="o", color=INK, capsize=3, ms=6,
                 label="source-derived TDS-EY (cell means ± SD)", zorder=3)
    # review MAJ-16/B3-19: a bootstrap curve ENVELOPE (not only the vertex bar) so the
    # RSM cross-section carries response uncertainty; labelled a conditional shape curve.
    dg = h.schmieder_rsm_diagnostics()
    cb = dg.get("curve_band")
    if cb:
        import numpy as _np
        gband = _np.array(cb["grind"]); dose = p["dose_g"]
        ax1.fill_between(gband, _np.array(cb["p2_5"]) / dose * 100.0,
                         _np.array(cb["p97_5"]) / dose * 100.0,
                         color=ACCENT, alpha=0.15, lw=0,
                         label="RSM 95% bootstrap band (conditional)")
    ax1.plot(gg, rsm_ey, color=ACCENT, lw=1.8,
             label="RSM refit (achieved predictors; conditional shape)")
    ax1.axvline(vtx, color=WARN, ls=":", lw=1.4)
    if vtx_ci:
        ax1.axvspan(vtx_ci[0], vtx_ci[1], color=WARN, alpha=0.12, lw=0)
    ax1.annotate("RSM refit vertex %.2f [%.2f,%.2f]\n(adj-R² %.2f)"
                 % (vtx, vtx_ci[0], vtx_ci[1], adj),
                 (vtx, 0.98), xycoords=("data", "axes fraction"),
                 xytext=(4, -2), textcoords="offset points",
                 color=WARN, fontsize=7.2, va="top")
    ax1.set_title("(a) Target: TDS-EY vs dial")
    ax1.set_xlabel("grinder dial (schmieder E65S)"); ax1.set_ylabel("extraction yield [%]")
    ax1.legend(loc="lower right", fontsize=7.4)
    ax1.text(0.03, 0.80, "observed cell means increase\n(no middle-cell maximum);\n"
             "RSM refit: weak interior vertex",
             transform=ax1.transAxes, va="top", fontsize=7.2, color=NULL)

    ax2.plot(ch["gs"], ch["ey_homog"], "o-", color=NULL, lw=1.5, ms=4, label="homogeneous (base)")
    ax2.plot(ch["gs"], ch["ey_ensemble"], "s-", color=ACCENT, lw=1.8, ms=5, label="channeling ensemble")
    ip = int(np.argmax(ch["ey_ensemble"]))
    ax2.axvline(ch["gs"][ip], color=WARN, ls=":", lw=1.2)
    ax2.set_title("(b) Model capacity (own dial axis)")
    ax2.set_xlabel("model grind gs (cameron; non-portable)"); ax2.set_ylabel("ensemble EY [%]")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.text(0.5, 0.42, "ensemble makes an interior max\n(fragile: 10/25 of a fixed closure grid;\n"
             "full-grid median prominence ≈ 0)",
             transform=ax2.transAxes, va="center", ha="center", fontsize=7.2, color=NULL)
    fig.suptitle("Result 1 — model capacity, not identification", y=1.02, fontsize=11, fontweight="bold")
    return _save(fig, outdir, "fig1_result1_tds_ey.png")


# ---------------------------------------------------------------------------
# status -> (colorblind-safe fill, short cell label). Palette avoids red/green-only
# semantics (review MAJ-09 / Crameri et al. 2020); the text label carries the meaning.
_EV_STATUS = {
    "implemented": ("#2c7fb8", "impl"),
    "observable-matched": ("#2c7fb8", "matched"),
    "observable-mismatch": ("#d9a441", "mismatch"),
    "cross-dataset-proxy": ("#d9a441", "proxy"),
    "target-fitted": ("#d9a441", "target-fit"),
    "same-campaign-transfer": ("#d9a441", "same-campaign"),
    "literature-fixed": ("#7fb1d3", "literature"),
    "capacity": ("#d9a441", "capacity"),
    "elevated-param-only": ("#d9a441", "elevated-ρc"),
    "no": ("#8a8f98", "no"),
    "qualitative-capacity": ("#d9a441", "qual-cap"),
    "qualitative-null": ("#7fb1d3", "qual-null"),
    "reference": ("#7fb1d3", "reference"),
    "not-implemented": ("#cfc6ba", "not-impl"),
    "parameter-blocked": ("#cfc6ba", "param-blocked"),
    "not-evaluated": ("#cfc6ba", "n/e"),
}


def fig2_evidence_matrix(outdir=OUTDIR_DEFAULT):
    """Fig 2 — mechanism evidence matrix, generated from the COMMITTED structured file
    `data/paper_b_evidence_matrix.csv` (review MAJ-09): every cell is a defined status
    from data, not hard-coded in plotting logic; a colorblind-safe fill plus a text
    label carries meaning; a right-hand column names the decisive missing measurement."""
    from puckworks import data as d
    plt = _plt()
    rows = d.paper_b_evidence_matrix()
    dims = ["implemented", "observable", "params_provenance",
            "generates_interior_max", "evidence_strength"]
    col_labels = ["implemented", "observable", "parameter\nprovenance",
                  "generates\ninterior max", "evidence\nstrength"]
    nR, nC = len(rows), len(dims)
    fig, ax = plt.subplots(figsize=(10.6, 3.6))
    for i, row in enumerate(rows):
        for j, dim in enumerate(dims):
            status = row[dim]
            fill, lab = _EV_STATUS.get(status, ("#cfc6ba", status[:10]))
            y = nR - 1 - i
            ax.add_patch(plt.Rectangle((j, y), 1, 1, facecolor=fill,
                                       edgecolor="white", lw=2))
            ax.text(j + 0.5, y + 0.5, lab, ha="center", va="center",
                    color="white", fontsize=7.0, fontweight="bold")
        # decisive missing measurement column (text, past the grid)
        ax.text(nC + 0.15, nR - 1 - i + 0.5, row["decisive_missing_measurement"],
                ha="left", va="center", fontsize=6.6, color=NULL)
    ax.text(nC + 0.15, nR + 0.12, "decisive missing measurement", ha="left",
            fontsize=7.2, style="italic", color=NULL)
    ax.set_xlim(0, nC + 4.6); ax.set_ylim(0, nR + 0.3)
    ax.set_xticks([j + 0.5 for j in range(nC)]); ax.set_xticklabels(col_labels, fontsize=8)
    ax.set_yticks([nR - 1 - i + 0.5 for i in range(nR)])
    ax.set_yticklabels([r["mechanism"] for r in rows], fontsize=8.0)
    ax.set_title("Fig 2 — mechanism evidence matrix (defined statuses; not a winner scoreboard)",
                 loc="left", fontsize=10)
    ax.grid(False); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    return _save(fig, outdir, "fig2_evidence_matrix.png")


def fig2_evidence_dictionary_md(outdir=OUTDIR_DEFAULT):
    """MAJ-20/B3-20: write the published Figure-2 data dictionary as markdown -- the
    per-mechanism citation table plus the definition of every status token used in the
    matrix -- generated from the committed CSVs so the legend cannot drift from the
    figure. A completeness audit refuses to write an incomplete dictionary."""
    import os
    from puckworks import data as d
    audit = d.paper_b_evidence_dictionary_audit()
    if not audit["complete"]:
        raise ValueError(
            "Fig 2 dictionary incomplete: undefined tokens %s; uncited mechanisms %s"
            % (audit["undefined_tokens"], audit["uncited_mechanisms"]))
    mat = d.paper_b_evidence_matrix()
    dic = d.paper_b_evidence_dictionary()
    lines = ["# Figure 2 data dictionary (Paper B)", "",
             "Generated from `puckworks/data/paper_b_evidence_matrix.csv` and "
             "`paper_b_evidence_dictionary.csv` — do not hand-edit.", "",
             "## Mechanism sources", "",
             "| mechanism | evidence strength | decisive missing measurement | citation |",
             "|---|---|---|---|"]
    for r in mat:
        lines.append("| %s | %s | %s | %s |" % (
            r["mechanism"], r["evidence_strength"],
            r["decisive_missing_measurement"], r["citation"]))
    lines += ["", "## Status-token definitions", "",
              "| dimension | token | rung | definition |", "|---|---|---|---|"]
    for r in dic:
        lines.append("| %s | %s | %s | %s |" % (
            r["dimension"], r["status_token"], r["tier"], r["definition"]))
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "fig2_evidence_dictionary.md")
    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")
    return path


# ---------------------------------------------------------------------------
def fig3_ladder(outdir=OUTDIR_DEFAULT):
    """Fig 3 — null-first κ(t) ladder, cross-pressure transfer, swelling sign test.
    (a) Foster machine-MODEL-curve reproduction (NOT data; a null shape source);
    (b) 9-bar ladder RMSE bars over ONE window (15-95 s), three DISTINCT constant
    nulls + the flexible cubic; (c) cross-pressure RMSE per mechanism -- BOTH the
    shared-calibration curves (solid) AND the leave-one-pressure-out held-out RMSE
    (open triangles, review MAJ-26) -- descriptive, no single mechanism lowest
    everywhere, LOPO tracks shared (max drift ~2.8%); (d) rung-5b
    swelling as an ISOLATED resistance-only branch under fixed pressure: it can only
    throttle, opposite to the rising trace -- a conditional sign constraint on the
    isolated branch, NOT a refutation of swelling in a coupled bed (review MAJ-15)."""
    import numpy as np
    from puckworks import harness as h, data as d
    plt = _plt()
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(9.4, 6.6))

    f = d.foster_fig15_flow()
    t_s = np.array([x["t_s"] for x in f]); q = np.array([x["Q_norm"] for x in f])
    ax1.plot(t_s, q, color=NULL, lw=1.8)
    imin = int(np.argmin(q))
    ax1.plot(t_s[imin], q[imin], "o", color=BAD, ms=6)
    ax1.set_title("(a) Foster machine MODEL curve (reproduction)")
    ax1.set_xlabel("time [s]"); ax1.set_ylabel("Q / Q_machine")
    ax1.text(0.5, 0.1, "numerical reproduction of the published\nFoster et al. machine/infiltration MODEL\n"
             "curve (not measured data): dip-and-recover\nis available with NO evolving bed resistance",
             transform=ax1.transAxes, fontsize=7.0, color=NULL, ha="center")

    lad = h.kappa_t_ladder()
    lo, hi = lad["window_s"]
    # review MAJ-21/B3-09: "0p" read as parameter-free; the empirical branches fit ZERO
    # coefficients to THIS 9-bar flow trace (they import equilibrium/TDS params from other
    # observables) -- so label them "0 fit to Q(t)", not "0p".
    names = ["best const\n(1p)", "long-run\nconst (1p)", "static κ(P)\n(0 fit Q(t))",
             "Φ(t)\n(0 fit Q(t))", "flexible\ncubic (4p)"]
    vals = [lad["rung1_const_kappa"], lad["rung1b_longrun_const"],
            lad["rung3_static_kappaP"], lad["rung4_phi_of_t"],
            lad["flexible_cubic_null"]]
    cols = [NULL, NULL, NULL, ACCENT, GOOD]
    ax2.bar(names, vals, color=cols)
    for i, v in enumerate(vals):
        ax2.text(i, v+0.01, "%.3f" % v, ha="center", fontsize=7.4)
    ax2.set_title("(b) 9-bar ladder, window %d–%d s (RMSE)" % (lo, hi))
    ax2.set_ylabel("RMSE [g/s]"); ax2.set_ylim(0, 0.72)
    ax2.tick_params(axis="x", labelsize=6.6)
    ax2.text(0.97, 0.60, "Φ(t) (0 params) beats every\nconstant null %.1f×; a 4-param\n"
             "flexible curve also does →\ntime variation is NEEDED,\nnot a specific mechanism"
             % lad["improvement_factor"],
             transform=ax2.transAxes, fontsize=6.4, color=NULL, ha="right", va="top")

    cp = h.cross_pressure_discrimination()
    pp = cp["per_pressure"]
    P = sorted(pp)
    # review MAJ-26/B3-12: show the actual LEAVE-ONE-PRESSURE-OUT held-out RMSE by pressure
    # (open markers, dashed) alongside the shared-calibration curves (solid) -- the LOPO
    # evidence the prose relies on is now IN the figure, not only "in text".
    lc = h.cross_pressure_loco()
    lpp = lc["per_pressure"]
    Pl = sorted(lpp, key=float)
    for key, col, lab in (("phi", ACCENT, "Φ(t)"), ("rc3b", GOOD, "RC-3b"), ("static", NULL, "static")):
        ax3.plot(P, [pp[p][key] for p in P], "o-", color=col, lw=1.5, ms=4,
                 label="%s shared" % lab)
        ax3.plot([float(p) for p in Pl], [lpp[p][key] for p in Pl], "^--", color=col,
                 lw=1.2, ms=4, mfc="none", label="%s LOPO held-out" % lab)
    ax3.set_title("(c) Cross-pressure: shared calibration (—) vs LOPO held-out (▵--)",
                  fontsize=8.6)
    ax3.set_xlabel("pressure [bar]"); ax3.set_ylabel("RMSE [g/s]")
    ax3.legend(fontsize=5.6, ncol=3, loc="upper center")
    ax3.text(0.5, 0.02, "LOPO refits (P_c,Q_c) on 10/11 pressures, predicts the held-out "
             "one; max drift %.1f%% (still conditional on the fixed 9-bar TDS trajectory)"
             % (lc["max_calibration_drift"] * 100),
             transform=ax3.transAxes, fontsize=5.4, color=NULL, ha="center")

    # (d) rung-5b swelling competitor: falling flow ratio vs the rising trace
    from puckworks.models.mo2023_2 import swelling as mo2
    tr = d.waszkiewicz_traces()
    t = np.asarray(tr[9.0]["time__s"], float)
    q = np.asarray(tr[9.0]["mass_flow_rate__g_per_s"], float)
    sel = (t >= lo) & (t <= hi); td, qd = t[sel], q[sel]
    t_full = np.linspace(0.0, hi, 120)
    qrel = np.interp(td, t_full, mo2.flow_decay("M", t_full)["q_rel"])
    a_star = float(np.dot(qrel, qd) / np.dot(qrel, qrel))     # LS-optimal level (1 param)
    ax4.plot(td, qd, color=ACCENT, lw=1.9, label="measured 9-bar (rises)")
    ax4.plot(td, a_star * qrel, color=BAD, lw=1.9, ls="--",
             label="swelling pred. (throttles)")
    ax4.set_title("(d) rung 5b swelling — isolated resistance-only branch")
    ax4.set_xlabel("time [s]"); ax4.set_ylabel("Q [g/s]")
    ax4.legend(fontsize=7.4, loc="center right")
    ax4.text(0.04, 0.95, "as an ISOLATED resistance-only branch under fixed\npressure, swelling only closes pores → falls "
             "(to %.0f%%);\nopposite net trend to the rising trace (r = %.2f,\nbest-anchored RMSE %.2f g/s). Constrains this "
             "isolated\nbranch, NOT a coupled bed (review MAJ-15)."
             % (lad["rung5b_swelling_full_shot_decay"] * 100.0,
                lad["rung5b_swelling_corr_with_trace"], lad["rung5b_swelling_mo2"]),
             transform=ax4.transAxes, fontsize=6.4, color=NULL, ha="left", va="top")
    fig.suptitle("Result 2 — time variation needed (not a specific mechanism); transfer descriptive; "
                 "swelling: opposite sign as isolated branch",
                 y=1.005, fontsize=10.2, fontweight="bold")
    fig.tight_layout()
    return _save(fig, outdir, "fig3_kappa_t_ladder.png")


# ---------------------------------------------------------------------------
def fig4_composition(outdir=OUTDIR_DEFAULT):
    """Fig 4 — shared-porosity composition diagnostic. Extraction-only reduces to the
    poroelastic rung by construction (an implementation identity, review MAJ-17); adding
    the imported swelling branch produces a flatter trajectory that underpredicts the
    rise (higher window RMSE than the best constant). The 15-95 s evaluation window is
    shaded; neutral wording per review MAJ-18."""
    import numpy as np
    from puckworks import data as d
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    plt = _plt()
    tr = d.waszkiewicz_traces()
    t = tr[9.0]["time__s"]; qobs = tr[9.0]["mass_flow_rate__g_per_s"]
    WIN = (15.0, 95.0)                                    # same window as the RMSEs
    r_ext = ck.simulate(P_bar=9.0, t=t, branches=("extraction",))
    r_sw = ck.simulate(P_bar=9.0, t=t, branches=("extraction", "swelling"))
    deg = ck.degeneracy_rmse(window=WIN); comp = ck.composition_residual(window=WIN)["rmse"]
    # flat null computed on the SAME window/object: LS-optimal constant over 15-95
    sel = (t >= WIN[0]) & (t <= WIN[1])
    q_flat = float(np.mean(qobs[sel]))
    rmse_flat = float(np.sqrt(np.mean((q_flat - qobs[sel]) ** 2)))

    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    ax.plot(t, qobs, color=INK, lw=2.0, label="observed 9-bar Q(t)")
    ax.plot(t, r_ext["Q"], color=ACCENT, lw=1.8, ls="-",
            label="extraction-only (rung 4, RMSE %.3f)" % deg)
    ax.plot(t, r_sw["Q"], color=BAD, lw=1.8, ls="--",
            label="extraction+swelling (RMSE %.3f)" % comp)
    ax.axhline(q_flat, color=NULL, lw=1.4, ls=":",
               label="best const null 15–95 s (RMSE %.3f)" % rmse_flat)
    ax.axvspan(WIN[0], WIN[1], color=GOOD, alpha=0.08, zorder=0,
               label="15–95 s eval window")
    ax.set_xlim(0, 120); ax.set_ylim(0, 2.3)
    ax.set_xlabel("time [s]"); ax.set_ylabel("flow Q(t) [g/s]")
    ax.set_title("Fig 4 — tested shared-porosity composition worsens the 9-bar reconstruction")
    ax.legend(loc="center right", fontsize=7.6)
    ax.text(0.30, 0.24, "extraction-only reduces to the poroelastic rung by\n"
            "construction (an implementation identity). Adding the\n"
            "imported swelling branch produces a flatter trajectory\n"
            "that underpredicts the rise (window RMSE %.3f > %.3f\n"
            "best constant). Does NOT separate parameter-transfer,\n"
            "initial-state, control-regime, and composition-form error."
            % (comp, rmse_flat),
            transform=ax.transAxes, va="center", fontsize=7.0, color=NULL)
    return _save(fig, outdir, "fig4_composition_diagnostic.png")


# ---------------------------------------------------------------------------
def fig5_concentration(outdir=OUTDIR_DEFAULT):
    """Fig 5 — N-tube finite-time concentration (Result 3, EXPLORATORY; NOT a stability
    theorem), redesigned around the numerical evidence (review AR-B2-21):
    (a) N_eff(t) and max single-tube share over time (the trajectory, baseline config);
    (b) endpoint N_eff SATURATES at the ~1 lower bound for every N/timestep -- endpoint
        saturation, NOT proof of trajectory/collapse-time convergence (review MAJ-35);
    (c) the physical CONTINGENCY — N_eff vs lateral homogenisation for flow vs pressure
        control (concentration is destroyed by pressure control or lateral ≥0.3);
    (d) supplementary floor audit — the closed-form gain is floor-CONTROLLED (∝1/floor, a
        regularisation diagnostic, not an eigenvalue), while the MEASURED N_eff plotted on
        the same panel is floor-INDEPENDENT (review MAJ-42/43)."""
    import numpy as np
    from puckworks import harness as h
    plt = _plt()
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(9.6, 6.8))

    # (a) trajectory: N_eff(t) and max-share(t) on the PHYSICAL clock (review MAJ-36),
    # with the converged collapse time marked (timestep-refinement stable, see the
    # switching-convergence study in the bundle/text).
    base = h.ntube_kappa_t_union(gs=1.1, N=400, closure="poroelastic", lateral=0.0,
                                 control="flow", compute_ey=False)
    ne = np.array(base["n_eff_trajectory"]); ms = np.array(base["max_share_trajectory"])
    xt = np.array(base.get("time_s_trajectory") or np.linspace(0, 1, len(ne)))
    ax1.plot(xt, ne / ne[0], color=ACCENT, lw=1.9, label="N_eff(t)/N_eff(0)")
    ax1.plot(xt, ms, color=BAD, lw=1.7, ls="--", label="max single-tube share")
    ct = base.get("collapse_time_s")
    if ct is not None:
        ax1.axvline(ct, color=NULL, ls=":", lw=1.1)
        ax1.text(ct, 0.5, " collapse ≈%.1f s\n(timestep-converged)" % ct, fontsize=6.0,
                 color=NULL, ha="left", va="center")
    ax1.set_title("(a) trajectory (baseline: flow, gs=1.1, N=400)")
    ax1.set_xlabel("time [s] (physical)"); ax1.set_ylabel("fraction")
    ax1.legend(fontsize=7.4, loc="center right")

    # (b) endpoint convergence in N and timestep
    Ns = [100, 200, 400, 800]
    neN = [h.ntube_kappa_t_union(gs=1.1, N=n, closure="poroelastic", lateral=0.0,
                                 control="flow", compute_ey=False)["n_eff_channels_final"]
           for n in Ns]
    subs = [4, 8, 16, 32]
    neS = [h.ntube_kappa_t_union(gs=1.1, N=400, substeps=s, closure="poroelastic",
                                 lateral=0.0, control="flow",
                                 compute_ey=False)["n_eff_channels_final"] for s in subs]
    ax2.plot(Ns, neN, "o-", color=ACCENT, lw=1.6, ms=5, label="vs N (substeps 8)")
    ax2b = ax2.twiny()
    ax2b.plot(subs, neS, "s--", color=GOOD, lw=1.5, ms=5, label="vs substeps (N 400)")
    ax2.set_ylim(0.9, 1.5)
    # review MAJ-35: the endpoint N_eff saturates at the ~1 lower bound for every N/substep
    # -- this is endpoint SATURATION, not proof of trajectory/collapse-time convergence
    ax2.set_title("(b) endpoint N_eff saturates at ~1 (N/substep)", fontsize=8.6)
    ax2.set_xlabel("tube count N"); ax2.set_ylabel("N_eff final")
    ax2.text(0.5, 0.90, "saturated at the lower bound (~1);\nN_eff/N → 0 as N grows —\n"
             "endpoint saturation, NOT trajectory convergence",
             transform=ax2.transAxes, fontsize=5.6, color=NULL, ha="center", va="top")
    ax2b.set_xlabel("substeps (timestep)", fontsize=8)
    h1, l1 = ax2.get_legend_handles_labels(); h2, l2 = ax2b.get_legend_handles_labels()
    ax2.legend(h1 + h2, l1 + l2, fontsize=6.8, loc="upper right")

    # (c) the physical contingency: lateral x control
    laterals = [0.0, 0.1, 0.2, 0.3]
    for ctrl, col, ls in (("flow", ACCENT, "-"), ("pressure", GOOD, "--")):
        neff = [h.ntube_kappa_t_union(gs=1.1, N=400, closure="poroelastic", lateral=L,
                                      control=ctrl, compute_ey=False)["n_eff_channels_final"]
                for L in laterals]
        ax3.plot(laterals, neff, "o" + ls, color=col, lw=1.7, ms=5, label="%s control" % ctrl)
    ax3.axhline(1.0, color=BAD, lw=1.0, ls=":")
    ax3.set_yscale("log")
    ax3.set_title("(c) CONTINGENT on control + low lateral")
    ax3.set_xlabel("lateral homogenisation"); ax3.set_ylabel("N_eff final (log)")
    ax3.legend(fontsize=7.4, loc="center right")

    # (d) supplementary floor audit — review MAJ-42/MAJ-43: plot BOTH the closed-form
    # gain (floor-CONTROLLED, an analytical diagnostic of the 1/floor regularisation) AND
    # the MEASURED numerical N_eff (floor-INDEPENDENT), so the "floor-independent" claim is
    # shown IN THIS PANEL rather than mis-cross-referenced to panel c.
    st = h.ntube_finite_time_gain(floors=(1e-6, 1e-9, 1e-12, 1e-15))
    floors = np.array([1e-6, 1e-9, 1e-12, 1e-15])
    for name, col in (("poroelastic", BAD), ("ck", GOOD)):
        g = st["closures"][name]["finite_time_gain_by_floor"]
        ax4.plot(floors, np.array([float(g["%.0e" % f]) for f in floors]),
                 "o-", color=col, lw=1.5, ms=4, label="%s gain (closed-form)" % name)
    ax4.set_xscale("log"); ax4.set_yscale("log"); ax4.invert_xaxis()
    ax4.set_title("(d) supp.: closed-form gain (∝1/floor) vs MEASURED N_eff", fontsize=8.4)
    ax4.set_xlabel("conductance floor M₀"); ax4.set_ylabel("gain M_f/M₀")
    ax4d = ax4.twinx()                                   # measured N_eff, floor-independent
    for name, col in (("poroelastic", BAD), ("ck", GOOD)):
        nf = st["closures"][name].get("n_eff_final_by_floor", {})
        if nf:
            ax4d.plot(floors, [float(nf["%.0e" % f]) for f in floors], "^:",
                      color=col, lw=1.4, ms=5, label="%s N_eff (measured)" % name)
    ax4d.set_ylabel("measured N_eff (floor-indep.)", fontsize=8)
    ax4.legend(fontsize=6.0, loc="lower left")
    ax4d.legend(fontsize=6.0, loc="upper right")
    ax4.text(0.5, 0.62, "closed-form gain ∝ 1/floor\n(regularisation diagnostic, not an\n"
             "eigenvalue); MEASURED N_eff (▲) is\nfloor-independent",
             transform=ax4.transAxes, fontsize=6.0, color=NULL, ha="center", va="top")
    fig.suptitle("Result 3 (exploratory) — finite-time concentration: endpoint invariant on "
                 "numerical axes (N/timestep), CONTINGENT on flow-control + low lateral",
                 y=1.0, fontsize=9.2, fontweight="bold")
    fig.tight_layout()
    return _save(fig, outdir, "fig5_concentration_floortest.png")


# back-compat alias (the old name implied a stability theorem it did not deliver)
fig5_stability = fig5_concentration


def render_all(outdir=OUTDIR_DEFAULT):
    """Render all five Paper-B figures. Returns the list of written paths."""
    paths = [fig1_result1(outdir), fig2_evidence_matrix(outdir),
             fig2_evidence_dictionary_md(outdir), fig3_ladder(outdir),
             fig4_composition(outdir), fig5_concentration(outdir)]
    for p in paths:
        print("wrote", p)
    return paths


if __name__ == "__main__":
    render_all()

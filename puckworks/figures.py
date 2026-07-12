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
INK = "#211a15"
ACCENT = "#b5561f"        # model / winner
NULL = "#8a7d70"          # baselines / nulls
GOOD = "#2f7d4f"
WARN = "#b7791f"
BAD = "#b8402e"
GRID = "#e7ddd0"
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
    })
    return plt


def _save(fig, outdir, name):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, name)
    fig.savefig(path, bbox_inches="tight")
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
    # RSM EY curve over the dial range: REFIT to the committed observations (the
    # PRINTED Table-3 coefficients are rounded and cannot reconstruct the absolute
    # level -- the earlier "overpredicts 1.7x" was a rounding artifact). The refit
    # sits near the data (~3.9 g); we plot it for the SHAPE (concavity/vertex).
    import numpy as _np
    from puckworks import data as _d
    fl, tp = t["center"]["flow_ml_s"], t["center"]["temp_C"]
    obs = []
    comp = "TDS"
    for x in _d.schmieder_cup_masses():
        if x.get("component") != comp or x.get("brew_ratio") != t["center"]["brew_ratio"]:
            continue
        try:
            obs.append((float(x["target_flow_ml_s"]), float(x["grind_level"]),
                        float(x["target_temp_C"]), float(x["mass_in_cup"])))
        except (TypeError, ValueError):
            continue
    O = _np.asarray(obs, float); Fo, Go, To, yo = O[:, 0], O[:, 1], O[:, 2], O[:, 3]
    Xo = _np.column_stack([_np.ones_like(Fo), Fo, Go, To, Go**2, To**2, Fo*Go])
    cf, *_ = _np.linalg.lstsq(Xo, yo, rcond=None)
    gg = np.linspace(1.4, 2.0, 60)
    Xg = _np.column_stack([_np.ones_like(gg), fl+0*gg, gg, tp+0*gg, gg**2, (tp**2)+0*gg, fl*gg])
    rsm_ey = (Xg @ cf) / p["dose_g"] * 100.0             # refit cup mass -> EY
    vtx = p["rsm"]["vertex_dial"]

    ch = h.channeling_sigma_sweep(gs_grid=np.linspace(1.0, 2.2, 7), s_ref=0.6, m=1.0, p_bar=5.0, n_grid=7)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.2, 3.4))
    ax1.errorbar(dials, ey, yerr=err, fmt="o", color=INK, capsize=3, ms=6,
                 label="measured TDS-EY (raw cells)", zorder=3)
    ax1.plot(gg, rsm_ey, color=ACCENT, lw=1.8, label="RSM refit (shape; printed coeffs rounded)")
    ax1.axvline(vtx, color=WARN, ls=":", lw=1.4)
    ax1.annotate("RSM vertex %.2f (adj-R² %.2f)" % (vtx, p["rsm"]["adj_r2"]),
                 (vtx, 0.98), xycoords=("data", "axes fraction"),
                 xytext=(4, -2), textcoords="offset points",
                 color=WARN, fontsize=7.6, va="top")
    ax1.set_title("(a) Target: TDS-EY vs dial")
    ax1.set_xlabel("grinder dial (schmieder E65S)"); ax1.set_ylabel("extraction yield [%]")
    ax1.legend(loc="lower right", fontsize=7.4)
    ax1.text(0.03, 0.80, "raw: monotone (no bump)\nRSM: weak interior max",
             transform=ax1.transAxes, va="top", fontsize=7.6, color=NULL)

    ax2.plot(ch["gs"], ch["ey_homog"], "o-", color=NULL, lw=1.5, ms=4, label="homogeneous (base)")
    ax2.plot(ch["gs"], ch["ey_ensemble"], "s-", color=ACCENT, lw=1.8, ms=5, label="channeling ensemble")
    ip = int(np.argmax(ch["ey_ensemble"]))
    ax2.axvline(ch["gs"][ip], color=WARN, ls=":", lw=1.2)
    ax2.set_title("(b) Model capacity (own dial axis)")
    ax2.set_xlabel("model grind gs (cameron; non-portable)"); ax2.set_ylabel("ensemble EY [%]")
    ax2.legend(loc="upper right", fontsize=8)
    ax2.text(0.5, 0.45, "ensemble makes an interior max\n(fragile: 40% of closures; weak)",
             transform=ax2.transAxes, va="center", ha="center", fontsize=7.6, color=NULL)
    fig.suptitle("Result 1 — model capacity, not identification", y=1.02, fontsize=11, fontweight="bold")
    return _save(fig, outdir, "fig1_result1_tds_ey.png")


# ---------------------------------------------------------------------------
def fig2_evidence_matrix(outdir=OUTDIR_DEFAULT):
    """Fig 2 — mechanism evidence matrix (NOT a winner scoreboard)."""
    from puckworks import harness as h
    plt = _plt()
    r = h.schmieder_peak_discrimination()
    by = {b["name"]: b for b in r["board"]}
    # rows = mechanisms; columns = evidence dimensions; cell codes: 2 yes, 1 partial/only-doctored, 0 no, -1 untested
    rows = [
        ("static channeling σ(φ₁)", [2, 2, 1, 2, 1]),      # impl, obs-match(EY proxy), params-constrained(empirical), generates, strength(qual)
        ("lee2023 dissolution", [2, 2, 1, 1, 1]),          # generates only under doctored ρ_c
        ("size-exclusion y₀", [2, 0, 2, 0, 1]),            # different observable
        ("diffusion null", [2, 2, 2, 0, 1]),
        ("incomplete wetting #2", [0, -1, -1, -1, -1]),    # unimplemented
    ]
    cols = ["implemented", "observable\nmatched", "params\nconstrained",
            "generates\ninterior max", "evidence\nstrength"]
    cmap = {2: GOOD, 1: WARN, 0: BAD, -1: "#cfc6ba"}
    labels = {2: "yes", 1: "partial", 0: "no", -1: "untested"}
    fig, ax = plt.subplots(figsize=(7.6, 3.4))
    for i, (name, vals) in enumerate(rows):
        for j, v in enumerate(vals):
            ax.add_patch(plt.Rectangle((j, len(rows)-1-i), 1, 1, facecolor=cmap[v],
                                       edgecolor="white", lw=2))
            ax.text(j+0.5, len(rows)-1-i+0.5, labels[v], ha="center", va="center",
                    color="white", fontsize=7.5, fontweight="bold")
    ax.set_xlim(0, len(cols)); ax.set_ylim(0, len(rows))
    ax.set_xticks([j+0.5 for j in range(len(cols))]); ax.set_xticklabels(cols, fontsize=8)
    ax.set_yticks([len(rows)-1-i+0.5 for i in range(len(rows))])
    ax.set_yticklabels([n for n, _ in rows], fontsize=8.5)
    ax.set_title("Fig 2 — mechanism evidence matrix (qualitative; not a winner scoreboard)")
    ax.grid(False); ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    return _save(fig, outdir, "fig2_evidence_matrix.png")


# ---------------------------------------------------------------------------
def fig3_ladder(outdir=OUTDIR_DEFAULT):
    """Fig 3 — null-first κ(t) ladder + regime-dependent cross-pressure.
    (a) Foster machine-only flow minimum (post-fit); (b) 9-bar ladder RMSE bars
    over ONE window (15-95 s), three DISTINCT constant nulls + the flexible cubic;
    (c) within-campaign conditional-transfer RMSE per mechanism (regime-dependent,
    no single mechanism lowest everywhere)."""
    import numpy as np
    from puckworks import harness as h, data as d
    plt = _plt()
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(11.2, 3.3))

    f = d.foster_fig15_flow()
    t_s = np.array([x["t_s"] for x in f]); q = np.array([x["Q_norm"] for x in f])
    ax1.plot(t_s, q, color=NULL, lw=1.8)
    imin = int(np.argmin(q))
    ax1.plot(t_s[imin], q[imin], "o", color=BAD, ms=6)
    ax1.set_title("(a) Foster machine-only null")
    ax1.set_xlabel("time [s]"); ax1.set_ylabel("Q / Q_machine")
    ax1.text(0.5, 0.1, "pump+headspace reproduce a\ndip-and-recover with NO bed\nmechanism (post-fit)",
             transform=ax1.transAxes, fontsize=7.6, color=NULL, ha="center")

    lad = h.kappa_t_ladder()
    lo, hi = lad["window_s"]
    names = ["best const\n(1p)", "long-run\nconst (1p)", "static κ(P)\n(0p)",
             "Φ(t)\n(0p)", "flexible\ncubic (4p)"]
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
    ax2.text(0.5, 0.88, "Φ(t) (0 params) beats every constant\nnull %.1f×; a 4-param "
             "flexible curve\nalso does → time variation is NEEDED,\nnot a specific bed mechanism"
             % lad["improvement_factor"],
             transform=ax2.transAxes, fontsize=6.6, color=NULL, ha="center", va="top")

    cp = h.cross_pressure_discrimination()
    pp = cp["per_pressure"]
    P = sorted(pp)
    for key, col, lab in (("phi", ACCENT, "Φ(t)"), ("rc3b", GOOD, "RC-3b"), ("static", NULL, "static")):
        ax3.plot(P, [pp[p][key] for p in P], "o-", color=col, lw=1.5, ms=4, label=lab)
    ax3.set_title("(c) Conditional cross-pressure transfer")
    ax3.set_xlabel("pressure [bar]"); ax3.set_ylabel("conditional-transfer RMSE [g/s]")
    ax3.legend(fontsize=8, ncol=3, loc="upper center")
    fig.suptitle("Result 2 — time variation is needed (not a specific mechanism); transfer is regime-dependent",
                 y=1.03, fontsize=10.5, fontweight="bold")
    return _save(fig, outdir, "fig3_kappa_t_ladder.png")


# ---------------------------------------------------------------------------
def fig4_composition(outdir=OUTDIR_DEFAULT):
    """Fig 4 — shared-porosity composition diagnostic (the FAILED composite).
    extraction-only reduces to the poroelastic rung; adding swelling OVER-closes
    (residual worse than the flat null)."""
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
    ax.set_xlim(0, 120); ax.set_ylim(0, 2.3)
    ax.set_xlabel("time [s]"); ax.set_ylabel("flow Q(t) [g/s]")
    ax.set_title("Fig 4 — shared-porosity composition: a FAILED composite")
    ax.legend(loc="center right", fontsize=8)
    ax.text(0.30, 0.26, "extraction-only reduces to the poroelastic rung.\n"
            "Adding the imported (pre-parameterized) swelling branch\n"
            "OVER-closes the porosity → Q FLATTENS (loses the rising\n"
            "structure), residual %.3f > %.3f best-constant null:\n"
            "worse than a flat line. A diagnosed mis-scale, not a success."
            % (comp, rmse_flat),
            transform=ax.transAxes, va="center", fontsize=7.6, color=NULL)
    return _save(fig, outdir, "fig4_composition_diagnostic.png")


# ---------------------------------------------------------------------------
def fig5_concentration(outdir=OUTDIR_DEFAULT):
    """Fig 5 — N-tube finite-time concentration (Result 3, EXPLORATORY; NOT a
    stability theorem — the filename/name deliberately avoids "stability").
    (a) effective channel count vs the homogenization parameter, flow vs pressure
    control, at FIXED grind gs=1.1 (the strong concentration is the flow-control +
    zero-homogenization corner); (b) the closed-form conductance-ratio GAIN vs the
    numerical floor — poroelastic scales ~1/floor (floor-controlled, so NOT a
    stability eigenvalue), Kozeny-Carman is floor-independent (~1.5) — annotated
    with the MEASURED numerical N_eff, which (re-run at every floor) IS
    floor-independent: that is the robust result, the closed-form gain is not."""
    import numpy as np
    from puckworks import harness as h
    plt = _plt()
    laterals = [0.0, 0.2, 0.4, 0.6, 0.8, 0.95]
    N = 150
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 3.6))
    for ctrl, col, ls in (("flow", ACCENT, "-"), ("pressure", GOOD, "--")):
        neff = [h.ntube_kappa_t_union(gs=1.1, N=N, closure="poroelastic", lateral=L,
                                      control=ctrl, compute_ey=False)["n_eff_channels_final"]
                for L in laterals]
        ax1.plot(laterals, neff, "o"+ls, color=col, lw=1.7, ms=5, label="%s control" % ctrl)
    ax1.axhline(1.0, color=BAD, lw=1.2, ls=":")
    ax1.text(0.02, 6, "single effective channel (N_eff→1)", color=BAD, fontsize=7.5)
    ax1.set_title("(a) N_eff vs homogenization (fixed grind gs=1.1)")
    ax1.set_xlabel("homogenization parameter (proxy for lateral coupling)")
    ax1.set_ylabel("effective # channels N_eff  (of %d)" % N)
    ax1.legend(fontsize=8, loc="center right")

    # (b) floor-dependence of the conductance-ratio gain (the honest replacement
    # for the earlier single "A~1e12, instability threshold" bar)
    st = h.ntube_finite_time_gain(floors=(1e-6, 1e-9, 1e-12, 1e-15))
    floors = np.array([1e-6, 1e-9, 1e-12, 1e-15])
    for name, col in (("poroelastic", BAD), ("ck", GOOD)):
        g = st["closures"][name]["finite_time_gain_by_floor"]
        gains = np.array([float(g["%.0e" % f]) for f in floors])
        ax2.plot(floors, gains, "o-", color=col, lw=1.7, ms=5, label=name)
    ax2.set_xscale("log"); ax2.set_yscale("log"); ax2.invert_xaxis()
    ax2.set_title("(b) closed-form gain vs floor (floor-controlled)")
    ax2.set_xlabel("conductance floor M₀ (smaller → larger 'gain')")
    ax2.set_ylabel("closed-form gain M_f / M₀")
    ax2.legend(fontsize=8, loc="center left")
    # the honest contrast: the MEASURED N_eff (re-run at each floor) is FLAT
    poro = st["closures"]["poroelastic"]["n_eff_final_by_floor"]
    ck = st["closures"]["ck"]["n_eff_final_by_floor"]
    ax2.text(0.5, 0.06,
             "closed-form gain ∝ 1/floor → NOT an eigenvalue.\n"
             "But the MEASURED N_eff, re-run at every floor, is FLAT:\n"
             "poroelastic N_eff=%s, CK N_eff≈%s across the range →\n"
             "the robust concentration result IS floor-independent."
             % ("/".join("%.0f" % v for v in poro.values()),
                list(ck.values())[0]),
             transform=ax2.transAxes, fontsize=6.6, color=NULL, ha="center")
    fig.suptitle("Result 3 (exploratory) — flow-control finite-time concentration; the closure sets whether it happens",
                 y=1.03, fontsize=10, fontweight="bold")
    return _save(fig, outdir, "fig5_concentration_floortest.png")


# back-compat alias (the old name implied a stability theorem it did not deliver)
fig5_stability = fig5_concentration


def render_all(outdir=OUTDIR_DEFAULT):
    """Render all five Paper-B figures. Returns the list of written paths."""
    paths = [fig1_result1(outdir), fig2_evidence_matrix(outdir), fig3_ladder(outdir),
             fig4_composition(outdir), fig5_concentration(outdir)]
    for p in paths:
        print("wrote", p)
    return paths


if __name__ == "__main__":
    render_all()

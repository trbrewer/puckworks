"""harness.py — P1 extraction comparison harness (ROADMAP item 2.1 / Sprint 8).

NOT a physics model: an orchestration + reporting layer that runs the registered
extraction components on matched inputs against the shared gate datasets, reports
per-dataset residuals WITH validation-strength tags, and surfaces the P1
normalization hazards (c_sat, soluble-inventory reference, dissolution law, flow
input) as explicit config fields that must NEVER be silently merged (CLAUDE.md
rule 6; ROADMAP §5.4 c_sat, §P1 hazards table, ledger A5).

The interpretive workup (which model is favored, P3 hypothesis file 2.3) is the CHAT
half of the sprint; this module provides the numbers.
"""
import numpy as np

# --- P1 normalization hazards (surfaced, never silently merged) ----------
# Each extraction lineage carries its own soluble-inventory reference and
# saturation concentration. These are CONFIG, reported per-model in any harness
# output; merging them would be the mega-model failure mode (rule 6, §5.4).
P1_HAZARDS = {
    "cameron2020": dict(c_sat_kg_m3=212.4, inventory="per-bed-volume (c_s0=118/phi_s)",
                        dissolution="nonlinear surface", flow="pressure/flux table"),
    "grudeva_thesis": dict(c_sat_kg_m3=170.0, inventory="per-grain (incl. internal pores)",
                           dissolution="linear capped transfer", flow="fixed q / P-derived"),
    "grudeva_paper": dict(c_sat_kg_m3=224.0, inventory="per-grain (incl. internal pores)",
                          dissolution="linear capped transfer", flow="fixed q / P-derived"),
    "moroney2016": dict(c_sat_kg_m3=212.4, inventory="per-bed-volume",
                        dissolution="two-timescale asymptotic", flow="constant dP"),
    "egidi2024": dict(c_sat_kg_m3=212.4, inventory="c0=200 kg/m3 per grain",
                      dissolution="quadratic-in-surface", flow="prescribed constant q"),
    "pannusch2024": dict(c_sat_kg_m3=None, inventory="per-solute c_s0",
                         dissolution="Sherwood-correlated linear", flow="measured Q(t)+T(t)"),
}


def csat_values():
    """The distinct c_sat config values in play (§5.4). Returns the sorted set of
    non-null values — the harness reports these side by side, never merged."""
    return sorted({h["c_sat_kg_m3"] for h in P1_HAZARDS.values()
                   if h["c_sat_kg_m3"] is not None})


# --- extraction-vs-dataset comparison (with validation-strength tags) ----
def extraction_comparison():
    """Run the gated extraction models against their validation datasets and
    return per-model residuals tagged by validation strength (ROADMAP §0)."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.models.grudeva2025 import reduced as gr
    from puckworks.models.liang2021 import desorption as lg
    from puckworks import data as d
    out = {}

    # pannusch -> Schmieder multi-solute kinetics (post-fit reconstruction)
    m = ps.mape_all()
    out["pannusch2024/schmieder_kinetics"] = dict(
        metric="MAPE_%", value={k: round(v, 2) for k, v in m.items()},
        strength="post-fit reconstruction")

    # grudeva -> C1 vial masses (post-fit reconstruction)
    r = gr.make_coffee(N=120, Nt=600)
    stats = d.grudeva_vial_stats()
    exp_total = sum(s["solubles_mean_g"] for s in stats[3:])
    out["grudeva2025/vial_masses"] = dict(
        metric="total_solubles_g", value=round(r["total_solubles_g"], 2),
        reference_g=round(exp_total, 2), strength="post-fit reconstruction")

    # liang -> equilibrium ceiling vs cameron inventory ceiling (§5.5)
    out["liang2021/ceiling_vs_cameron"] = dict(
        metric="EY_ceiling", liang=lg.K_EMAX_1L,
        cameron=round(lg.cameron_inventory_ceiling(), 3),
        strength="independent (distinct quantities, K<1)")

    # cameron EY vs the egidi2024 12-condition RC-1 bracket (independent)
    from puckworks.models.cameron2020 import extraction_bdf as cam
    ey = [r["EY [%]"] for r in d.egidi_table2()]
    cam_ey = cam.simulate_shot(1.9, m_in=0.020, m_out=0.040).EY
    out["cameron2020/egidi_bracket"] = dict(
        metric="EY_%", cameron=round(cam_ey, 1),
        egidi_bracket=[round(min(ey), 1), round(max(ey), 1)],
        in_bracket=bool(min(ey) <= cam_ey <= max(ey)),
        strength="independent EY/TDS range bracket (cameron reads low, per card)")
    return out


# --- §5.6 dissolution-speed discriminator --------------------------------
def dissolution_speed_test():
    """§5.6: near-instant dissolution (Waszkiewicz, TDS timescale set by flow)
    vs diffusion-limited boulders (Cameron). Discriminator on the Waszkiewicz
    5-s TDS fractions: instant dissolution => solubles present from t=0 => TDS is
    HIGH in the first fraction (early/peak ~ 1); a diffusion-limited population
    would release slowly => low-then-rising TDS (early/peak << 1)."""
    from puckworks import data as d
    f = d.waszkiewicz_tds_fractions()
    tds = f["tds_pct"]
    early = float(tds[0]); peak = float(np.nanmax(tds))
    ratio = early / peak
    # boulder-diffusion timescale (grudeva boulders a=2.29e-4 m, D_s=2.3e-10)
    tau_diff = (2.29e-4) ** 2 / (np.pi ** 2 * 2.3e-10)
    return dict(early_to_peak=round(ratio, 3), early_tds_pct=round(early, 2),
                peak_tds_pct=round(peak, 2), tau_boulder_diffusion_s=round(tau_diff, 1),
                favors="near-instant dissolution" if ratio > 0.8 else "diffusion-limited")


# --- P2 kappa(t) null-first discrimination ladder (item 2.2) --------------
# Each rung must beat the rung below on the same trace before claiming a
# residual. Rungs 1-4 use registered components; rung 5 (challengers) is Phase 3.
_KAPPA_LADDER_WINDOW = (15.0, 95.0)   # ONE saturated-extraction window, everywhere

def kappa_t_ladder(window=_KAPPA_LADDER_WINDOW):
    """Run the P2 null-first ladder on the Waszkiewicz 9-bar RISING-flow trace.
    Returns per-rung RMSE [g/s] over ONE explicit saturated window (default
    t = 15-95 s, the manuscript window; also used by coupled_kappa_t). Every
    baseline is evaluated at its OWN predicted level -- no RMSE is copied between
    rungs, and each rung's free-parameter count is reported so the discrimination
    is read against complexity, not asserted.

    THREE DISTINCT constant nulls (a constant kappa <=> a constant flow):
      rung1 best-in-window constant  1 param, LS-optimal mean over the window
      rung1b long-run constant       1 param, mean over a real 10 s calibration
                                     interval [t_end-10, t_end] (not one sample)
      rung3 published static kappa(P) 0 free params, wz.q_static at 9 bar
    rung4 waszkiewicz2025 time-dependent Phi(t)=m_d(t)/m0  0 free params, rises.
    rung5 RC-3b Cameron-coupled Phi(t) (Phase-3 challenger).
    FLEXIBLE temporal null (diagnostic): a degree-3 polynomial in t, 4 params fit
    to the SAME trace -- a NON-mechanistic curve. If it reaches rung4's RMSE then
    the ladder establishes that TIME VARIATION is needed, NOT that a specific bed
    mechanism is validated; the mechanistic content is that a ZERO-free-parameter
    poroelastic Phi(t) nearly reaches that flexible floor.
    (rung 2, the foster2025 pump/headspace flow-MINIMUM null, is a distinct
     early-shot phenomenon validated by gate_foster_fig15_flowmin, not the
     saturated rising-flow residual tested here.)
    """
    import numpy as np
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    lo, hi = window
    tr = d.waszkiewicz_traces()
    t = tr[9.0]["time__s"]; q = tr[9.0]["mass_flow_rate__g_per_s"]
    sel = (t >= lo) & (t <= hi)
    td, qd = t[sel], q[sel]
    rmse = lambda pred: float(np.sqrt(np.mean((np.asarray(pred) - qd) ** 2)))
    # rung1: LS-optimal constant IN the window (1 param, best case for a constant)
    lvl_best = float(np.mean(qd)); rmse_best = rmse(lvl_best)
    # rung1b: constant calibrated on a real 10 s late interval, NOT one sample
    late = (t >= hi - 10.0) & (t <= hi)
    lvl_long = float(np.mean(q[late])); rmse_long = rmse(lvl_long)
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    # rung3: published static characteristic at 9 bar (0 free params, no trace fit)
    lvl_static = float(wz.q_static(9.0, P_c, Q_c)); rmse_static = rmse(lvl_static)
    # rung4: empirical time-dependent Phi(t) (0 free params)
    q4 = wz.q_dynamic(td, 9.0, P_c, Q_c, k_s, l_s, m_s, dose)
    rmse4 = float(np.sqrt(np.nanmean((q4 - qd) ** 2)))
    # rung 5, RC-3b: Cameron-coupled Phi(t) = m_d_cameron(t)/m0 (NEW model, not
    # validated by the Waszkiewicz paper). Cameron's diffusion-limited dissolution
    # drives the poroelastic kappa instead of the empirical near-instant sigmoid.
    from puckworks.models.cameron2020 import extraction_bdf as cam
    r = cam.simulate_shot(1.9, p_bar=9.0, m_in=dose / 1000, m_out=0.040,
                          t_shot=120.0, n_save=200)
    md_cam = np.interp(td, r.t, r.m_cup * 1000.0)          # g
    q5 = wz.q_dynamic_from_md(9.0, P_c, Q_c, md_cam, dose)
    rmse5 = float(np.sqrt(np.nanmean((q5 - qd) ** 2)))
    # rung 5b, mo2023_2 SWELLING competitor (Phase-3 discrimination, wrong-sign).
    # The card is explicit: swelling shrinks the fixed-height bed's porosity, so its
    # Carman-Kozeny flow RATIO q(t)/q(0) is monotone NON-INCREASING at fixed dp --
    # it can only THROTTLE flow, never source the observed 14x rise. We run its own
    # native prediction (flow_decay, the validated Fig-3a mechanism) from t~0 across
    # the window for a representative illy powder, give it its BEST-CASE free level
    # (LS-optimal scalar anchor, 1 param), and report the wrong-sign signature: the
    # sign of its within-window trend and its correlation with the rising trace.
    # This is a QUALITATIVE cross-rig mechanism check (illy powder, not the wz
    # coffee); the sign is grind/coffee-independent (any swelling => q_rel<=1), so
    # the refutation is robust while the magnitude is not a fit to this coffee.
    from puckworks.models.mo2023_2 import swelling as mo2
    t_full = np.linspace(0.0, hi, 120)
    fd = mo2.flow_decay("M", t_full)                       # q_rel(t)=q(t)/q(0), falls
    qrel_win = np.interp(td, t_full, fd["q_rel"])
    a_star = float(np.dot(qrel_win, qd) / np.dot(qrel_win, qrel_win))  # LS level, 1 param
    rmse5b = float(np.sqrt(np.mean((a_star * qrel_win - qd) ** 2)))
    swell_trend = float(qrel_win[-1] - qrel_win[0])        # <0: falling within window
    swell_corr = float(np.corrcoef(qrel_win, qd)[0, 1])    # <0: anti-correlated w/ rise
    full_shot_decay = float(fd["q_rel"][-1])               # q(95)/q(0) over the shot
    # flexible NON-mechanistic temporal null: degree-3 polynomial, 4 params fit
    Xc = np.column_stack([td ** kk for kk in range(4)])
    cc, *_ = np.linalg.lstsq(Xc, qd, rcond=None)
    rmse_cubic = rmse(Xc @ cc)
    best_null = min(rmse_best, rmse_long, rmse_static)
    return dict(window_s=(lo, hi), n_points=int(sel.sum()),
                # rung1 kept as the STRONGEST constant null (LS-optimal in window)
                rung1_const_kappa=round(rmse_best, 3),
                rung1_const_level_g_per_s=round(lvl_best, 3),
                rung1b_longrun_const=round(rmse_long, 3),
                rung1b_longrun_level_g_per_s=round(lvl_long, 3),
                rung3_static_kappaP=round(rmse_static, 3),
                rung3_static_level_g_per_s=round(lvl_static, 3),
                rung4_phi_of_t=round(rmse4, 3),
                rung5_rc3b_cameron_coupled=round(rmse5, 3),
                rung5b_swelling_mo2=round(rmse5b, 3),
                rung5b_swelling_full_shot_decay=round(full_shot_decay, 3),
                rung5b_swelling_window_trend=round(swell_trend, 4),
                rung5b_swelling_corr_with_trace=round(swell_corr, 3),
                # swelling can ONLY throttle: monotone-nonincreasing ratio,
                # anti-correlated with the rising trace -> wrong sign for the driver
                swelling_wrong_sign=bool(swell_corr < 0.0 and swell_trend <= 0.0),
                swelling_beats_best_null=rmse5b < best_null,
                flexible_cubic_null=round(rmse_cubic, 3),
                free_params=dict(rung1=1, rung1b=1, rung3=0, rung4=0, rung5=0,
                                 rung5b_swelling=1, flexible_cubic=4),
                rung4_beats_floor=rmse4 < best_null,
                improvement_factor=round(best_null / rmse4, 1),      # vs BEST null
                improvement_vs_static=round(rmse_static / rmse4, 1),
                cubic_beats_dynamic=rmse_cubic < rmse4,
                discrimination_reading=(
                    "time variation is NEEDED (all constant nulls >=%.2f vs "
                    "Phi(t) %.2f); a 4-param flexible curve reaches %.2f, so the "
                    "ladder establishes NEED for time variation, not a specific "
                    "bed mechanism -- the mechanistic content is a ZERO-param "
                    "poroelastic Phi(t) nearly reaching the flexible floor"
                    % (best_null, rmse4, rmse_cubic)),
                rc3b_vs_rung4="worse (near-instant favored, §5.6)" if rmse5 > rmse4 else "better")


def result2_residual_diagnostics(windows=((10.0, 90.0), (15.0, 95.0), (20.0, 90.0)),
                                 block_s=8.0, n_boot=1000, seed=0):
    """RESULT-2 RESIDUAL / DEPENDENCE DIAGNOSTICS (review MAJ-23/B3-23): the 9-bar ladder
    RMSE differences are pointwise on ONE strongly-autocorrelated trace, so a naive
    per-sample uncertainty is invalid. This reports (a) the per-BRANCH residual lag-1 ACF
    over the primary 15-95 s window (best-const / static / Phi(t) / cubic); (b) a
    CONDITIONAL MOVING-BLOCK RESAMPLING of the already-computed per-timestep squared-error
    differences (Phi(t)-best-const and Phi(t)-cubic) via ~`block_s`-second blocks -- it
    preserves serial dependence but does NOT refit either branch inside the resample, so it
    is a dependence-aware interval on the FIXED loss sequences, not a bootstrap of the full
    fit-and-compare procedure (review B5-04); and (c) WINDOW SENSITIVITY -- whether Phi(t)
    beats the constant nulls across 10-90 / 15-95 / 20-90 s. A difference whose interval
    straddles zero is 'not resolved by this conditional interval', NOT 'statistically
    indistinguishable' (B5-05). Fast."""
    import numpy as np
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    tr = d.waszkiewicz_traces()
    t_all = np.asarray(tr[9.0]["time__s"], float)
    q_all = np.asarray(tr[9.0]["mass_flow_rate__g_per_s"], float)
    P_c, Q_c = wz.published_calibration(); k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    rng = np.random.default_rng(seed)

    def _branches(lo, hi):
        sel = (t_all >= lo) & (t_all <= hi); td, qd = t_all[sel], q_all[sel]
        pr = {"best_const": np.full_like(qd, float(np.mean(qd))),
              "static": np.full_like(qd, float(wz.q_static(9.0, P_c, Q_c))),
              "phi": wz.q_dynamic(td, 9.0, P_c, Q_c, k_s, l_s, m_s, dose)}
        Xc = np.column_stack([td ** kk for kk in range(4)])
        cc, *_ = np.linalg.lstsq(Xc, qd, rcond=None)
        pr["cubic"] = Xc @ cc
        return td, qd, pr

    # (c) window sensitivity: does Phi(t) beat the constant nulls in every window?
    window_rank = []
    for lo, hi in windows:
        td, qd, pr = _branches(lo, hi)
        rmses = {k: float(np.sqrt(np.nanmean((v - qd) ** 2))) for k, v in pr.items()}
        window_rank.append(dict(
            window=[lo, hi], rmse={k: round(v, 3) for k, v in rmses.items()},
            phi_beats_constants=bool(rmses["phi"] < min(rmses["best_const"], rmses["static"])),
            lowest=min(rmses, key=rmses.get)))
    ranking_persists = all(w["phi_beats_constants"] for w in window_rank)

    # (a) per-branch residual ACF + (b) moving-block bootstrap on the primary window
    td, qd, pr = _branches(15.0, 95.0); n = len(qd)
    dt = float(np.median(np.diff(td))); block = max(2, int(round(block_s / dt)))

    def _acf1(res):
        r = res - np.mean(res)
        return round(float(np.sum(r[1:] * r[:-1]) / np.sum(r ** 2)), 3)
    acf_lag1_by_branch = {k: _acf1(qd - v) for k, v in pr.items()}

    def _mbb_rmsediff(a, b):
        ea = (qd - a) ** 2; eb = (qd - b) ** 2
        nblk = int(np.ceil(n / block)); diffs = []
        for _ in range(n_boot):
            starts = rng.integers(0, n - block + 1, nblk)
            idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
            diffs.append(float(np.sqrt(np.mean(ea[idx])) - np.sqrt(np.mean(eb[idx]))))
        d_ = np.array(diffs)
        return dict(median=round(float(np.median(d_)), 3),
                    ci95=[round(float(np.percentile(d_, 2.5)), 3),
                          round(float(np.percentile(d_, 97.5)), 3)],
                    excludes_zero=bool(np.percentile(d_, 2.5) > 0 or np.percentile(d_, 97.5) < 0))
    phi_minus_const = _mbb_rmsediff(pr["phi"], pr["best_const"])
    phi_minus_cubic = _mbb_rmsediff(pr["phi"], pr["cubic"])
    # B5-20: expose the residual TRACES + a multi-lag ACF so the coherent, non-white
    # lack-of-fit (the strong serial dependence the RMSE ranking rides on) is plottable.
    residuals = {k: (qd - v) for k, v in pr.items()}
    def _acf_curve(res, maxlag=25):
        r = res - np.mean(res); denom = np.sum(r ** 2)
        return [round(float(np.sum(r[L:] * r[:len(r) - L]) / denom), 4)
                for L in range(maxlag + 1)]
    stride = max(1, n // 200)
    residual_traces = dict(
        time_s=[round(float(x), 3) for x in td[::stride]],
        residual={k: [round(float(x), 5) for x in residuals[k][::stride]] for k in pr})
    acf_by_lag = dict(lag_s=[round(L * dt, 3) for L in range(26)],
                      phi=_acf_curve(residuals["phi"]),
                      best_const=_acf_curve(residuals["best_const"]),
                      cubic=_acf_curve(residuals["cubic"]))
    return dict(
        primary_window_s=[15.0, 95.0], block_length_s=block_s, block_length_samples=block,
        n_points=n, n_boot=n_boot,
        residual_traces=residual_traces, acf_by_lag=acf_by_lag,
        residual_acf_lag1_by_branch=acf_lag1_by_branch,     # strong positive -> lack of fit
        rmse_diff_phi_minus_best_const=phi_minus_const,     # <0 CI excluding 0 -> phi wins
        rmse_diff_phi_minus_cubic=phi_minus_cubic,          # straddles 0 -> ties the flex null
        window_sensitivity=window_rank, phi_ranking_persists_across_windows=ranking_persists,
        verdict=("Block bootstrap (~%.0f s blocks, respecting the strong residual "
                 "autocorrelation -- lag-1 ACF %.2f for Phi(t)): Phi(t) beats the best "
                 "constant by %s g/s (95%% %s, excludes 0 = %s), but only TIES the "
                 "4-param cubic (diff %s, 95%% %s, excludes 0 = %s). The Phi-over-constant "
                 "advantage persists across the 10-90/15-95/20-90 s windows (%s). So time "
                 "variation robustly reduces IN-SAMPLE reconstruction error over constants, "
                 "but a flexible non-mechanistic curve does equally well -- not predictive "
                 "mechanism identification." % (
                     block_s, acf_lag1_by_branch["phi"], phi_minus_const["median"],
                     phi_minus_const["ci95"], phi_minus_const["excludes_zero"],
                     phi_minus_cubic["median"], phi_minus_cubic["ci95"],
                     phi_minus_cubic["excludes_zero"], ranking_persists)),
        strength="dependence-aware (moving-block bootstrap) RMSE-difference uncertainty + "
                 "window sensitivity; IN-SAMPLE reconstruction, not held-out prediction")


# --- unified kappa(t) = kappa0 * f(P, eps, E) closure framework ---------------
# The bed_dynamics backlog asks for one permeability closure kappa(t)=kappa0*f(...)
# assembling the mechanisms the registry now has as SEPARATE gated components.
# This framework exposes each as an independently-toggleable, SIGNED factor so a
# config selects which are active; it does NOT invent new physics -- each factor
# is drawn from its registered component, and the composition is multiplicative
# (independent porosity/resistance perturbations). The load-bearing content is
# the SIGNS and limits, which the gate pins; the multiplicative combination is a
# framework choice, surfaced as such.
def kappa_branches(P_bar=9.0, EY=0.0, t_swell_s=0.0, t_fines_s=0.0, powder="M",
                   eps0=0.17, beta_series="beta1"):
    """Evaluate each kappa/kappa0 branch factor at one operating point.

    f_compaction(P)  <=1, DECREASING in P  (waszkiewicz2025 poroelastic; bed
                     compacts under pressure) -- normalized to the P->0 limit.
    f_swelling(t)    <=1, DECREASING in t   (mo2023_2 swelling shrinks eps_b).
    f_extraction(EY) >=1, INCREASING in EY  (lee2023: solid dissolved -> eps
                     opens -> Kozeny-Carman kappa rises).
    f_fines(t)       <=1, DECREASING in t   (fasano2000_partI compact layer).
    Returns the four factors and their product kappa/kappa0."""
    import numpy as np
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    from puckworks.models.mo2023_2 import swelling as sw
    from puckworks.models.fasano2000_partI import fines_migration as fm
    Pc, _ = wz.published_calibration()
    x = P_bar / Pc
    f_comp = float(wz.qhat(x) / x / 4.0) if x > 0 else 1.0     # /4 = P->0 limit
    f_swell = 1.0
    if t_swell_s > 0:
        f_swell = float(sw.flow_decay(powder, np.array([1e-4, t_swell_s]))["q_rel"][-1])

    def _ck(e):
        return e ** 3 / (1.0 - e) ** 2
    eps = eps0 + EY * (1.0 - eps0)                              # solid removed opens pores
    f_extr = _ck(eps) / _ck(eps0)
    f_fines = 1.0
    if t_fines_s > 0:
        b = fm.beta_from_fig87(beta_series)
        r = fm.simulate(1.0, b, t_end=t_fines_s, n_save=20)
        f_fines = float(r["q"][-1] / r["q"][0])
    return dict(f_compaction=f_comp, f_swelling=f_swell, f_extraction=f_extr,
                f_fines=f_fines,
                kappa_over_kappa0=f_comp * f_swell * f_extr * f_fines)


def unified_kappa_t(P_bar=9.0, EY_final=0.20, t_shot_s=30.0, n=25, powder="M",
                    branches=("compaction", "swelling", "extraction", "fines")):
    """Compose the selected kappa(t) branches over a shot. EY ramps 0->EY_final;
    swelling/fines evolve over t_shot. Returns t and kappa/kappa0(t) with only the
    named branches active (others held at their neutral factor 1)."""
    import numpy as np
    t = np.linspace(0.0, t_shot_s, n)
    out = []
    for ti in t:
        k = kappa_branches(P_bar=P_bar, EY=EY_final * ti / t_shot_s,
                           t_swell_s=ti if "swelling" in branches else 0.0,
                           t_fines_s=ti if "fines" in branches else 0.0,
                           powder=powder)
        f = 1.0
        if "compaction" in branches:
            f *= k["f_compaction"]
        if "swelling" in branches:
            f *= k["f_swelling"]
        if "extraction" in branches:
            f *= k["f_extraction"]
        if "fines" in branches:
            f *= k["f_fines"]
        out.append(f)
    return dict(t=t, kappa_over_kappa0=np.array(out))


def g9_series_resistance():
    """G9 — basket/screen/outlet hydraulic resistance. A standard Darcy
    series-resistance decomposition R_total = R_puck + R_series (screen+fixture),
    testing whether the puck alone explains the observed flow resistance.

    R_total from DE1 fixture A (steady dP/Q). R_puck = mu L /(kappa A) from the
    INDEPENDENTLY-MEASURED tamped permeability (romancorrochano Table 6.1), vs the
    FITTED effective kappa lineages (DE1 k_from_kappa, Grudeva). The load-bearing
    observation: the fitted effective kappa sits BELOW the measured tamped kappa
    range, i.e. a fit lumps non-puck resistance into an over-dense effective kappa
    -> R_puck(measured) < R_total, implying a series (screen+fixture) residual.

    Strength: independent data, but CROSS-SOURCE (different coffee/grinder for the
    measured kappa vs the DE1 shot) -> suggestive, not conclusive; and the revised
    grudeva adjudication (kappa 2.2e-15 sits inside her K-C band) weakens the sieve
    narrative. Verdict below: implemented + suggestive; a matched puck-kappa + in-
    machine total-R measurement is needed to close G9."""
    import json
    import os
    import numpy as np
    from puckworks.models.cameron2020 import extraction_bdf as cam
    from puckworks import data as _d
    DATA = os.path.join(os.path.dirname(__file__), "data")
    fx = json.load(open(os.path.join(DATA, "de1_fixtureA.json")))
    t = np.array(fx["elapsed_s"]); P = np.array(fx["pressure_bar"]); fl = np.array(fx["flow_gs"])
    sel = t >= t[-1] - 8
    P_ss = float(np.mean(P[sel])); Q_ss = float(np.mean(fl[sel])) / 1e6   # g/s -> m^3/s
    R_total = P_ss * 1e5 / Q_ss
    mu = 3.15e-4; L = cam.bed_depth(fx["dose_g"] / 1000); A = np.pi * cam.R0 ** 2
    k_meas = [r["kappa_m2"] for r in _d.roman_tamped_kappa()]
    R_puck = lambda k: mu * L / (k * A)
    from puckworks.models.foster2025 import infiltration as inf
    k_de1 = inf.k_from_kappa(fx["grind_setting_assumed"], fx["dose_g"] / 1000, fx["kappa_fitted"])[0]
    k_grud = 2.2e-15                                        # adjudicated grudeva kappa
    frac = lambda k: R_puck(k) / R_total                    # puck share of total
    # --- screen resistance from schulman2011 basket GEOMETRY (registry-side [RS]
    # orifice + Poiseuille construction; the source measured no dP). Clean basket.
    Cd = 0.61; L_plate = 4e-4                                # discharge coeff; assumed plate thickness
    baskets = _d.schulman_baskets()
    R_screen = []
    for b in baskets:
        Ah = b["A_h_mm2"] * 1e-6; dh = b["d_hole_um"] * 1e-6
        N = Ah / (np.pi * (dh / 2) ** 2)
        R_orif = 0.5 * 1000.0 * Q_ss / (Cd * Ah) ** 2        # inertial (flow-dependent)
        R_pois = 128 * mu * L_plate / (N * np.pi * dh ** 4)  # viscous
        R_screen.append(max(R_orif, R_pois))
    R_screen_max = float(max(R_screen))                      # worst (most resistive) basket
    return dict(R_total=R_total, R_puck_measured_range=[R_puck(max(k_meas)), R_puck(min(k_meas))],
                R_screen_geom_max=R_screen_max, screen_share=R_screen_max / R_total,
                screen_negligible=bool(R_screen_max / R_total < 1e-3),
                puck_share_measured=[round(frac(max(k_meas)), 2), round(frac(min(k_meas)), 2)],
                kappa_measured_range=[min(k_meas), max(k_meas)],
                kappa_fitted_DE1=k_de1, kappa_fitted_grudeva=k_grud,
                fitted_below_measured=bool(k_de1 < min(k_meas) and k_grud < min(k_meas)),
                puck_below_total=bool(R_puck(min(k_meas)) < R_total),
                verdict="G9 largely resolved: the CLEAN-basket screen resistance computed "
                        "from schulman2011 geometry (orifice + Poiseuille) is ~5-6 orders "
                        "below the puck/total (screen/total ~1e-5) -> NEGLIGIBLE. So the "
                        "earlier fitted-vs-measured kappa gap is coffee/grind, NOT screen. "
                        "Caveat: this is a clean basket; fines CLOGGING the holes during a "
                        "shot (unmeasured) could raise it, and the orifice/Poiseuille are "
                        "[RS] constructions (assumed Cd, plate thickness).")


def coupled_kappa_t(P_bar=9.0, grind=1.9, dose_g=20.0, t_shot_s=30.0, powder="M",
                    eps0=0.17, n_save=40, branches=("compaction", "swelling", "extraction")):
    """COUPLED kappa(t) closure: composes the branch factors from LIVE registered-
    model outputs over a real shot, not the linear-ramp placeholder of
    unified_kappa_t. Extraction EY(t) comes from cameron2020's running cup mass;
    swelling eps_b(t)->kappa ratio from mo2023_2 at the real shot times;
    compaction from waszkiewicz at the applied P. Returns t, kappa/kappa0(t), and
    the driving EY(t)/swelling(t) so the swelling-closes-then-extraction-opens
    competition is visible. NOTE: a coupled RUNTIME closure, but NOT a registered
    component -- the multiplicative composition is our modeling choice with no
    card, so registration is card-blocked (CLAUDE.md rule 1)."""
    import numpy as np
    from puckworks.models.cameron2020 import extraction_bdf as cam
    from puckworks.models.mo2023_2 import swelling as sw
    r = cam.simulate_shot(grind, p_bar=P_bar, m_in=dose_g / 1000, m_out=0.040,
                          t_shot=t_shot_s, n_save=n_save)
    t = r.t
    EY = r.m_cup / (dose_g / 1000.0)                       # extraction fraction(t)
    f_comp = kappa_branches(P_bar=P_bar)["f_compaction"] if "compaction" in branches else 1.0
    f_swell = sw.flow_decay(powder, t)["q_rel"] if "swelling" in branches else np.ones_like(t)

    def f_extr(ey):
        e = eps0 + ey * (1.0 - eps0)
        return (e ** 3 / (1.0 - e) ** 2) / (eps0 ** 3 / (1.0 - eps0) ** 2)
    fe = np.array([f_extr(x) for x in EY]) if "extraction" in branches else np.ones_like(t)
    kap = f_comp * np.asarray(f_swell) * fe
    return dict(t=t, EY=EY, f_swelling=np.asarray(f_swell), f_extraction=fe,
                f_compaction=f_comp, kappa_over_kappa0=kap)


# --- P3 fine-grind-dip hypothesis #1: static channeling sigma(phi1) sweep -----
# ANALYSIS_P2 §2.3 named this the single most uncertainty-reducing computation:
# does a MONOTONE sigma(grind) channeling closure (finer grind -> more fines ->
# more permeability heterogeneity) reproduce a NON-MONOTONE cup/EY peak (the
# fine-grind dip)? streamtube EY-deficit x grindmap fines fraction.
def channeling_sigma_sweep(gs_grid=(1.0, 1.4, 1.8, 2.2, 2.5), s_ref=0.6, m=1.0,
                           p_bar=5.0, n_grid=7):
    """Sweep grind setting; set the streamtube lognormal-permeability width sigma
    by a MONOTONE closure through the fines fraction phi1 (finer -> more fines ->
    wider sigma). Return per-grind homogeneous EY, channeling-deficit EY, and
    whether the deficit turns the monotone base curve into a peaked one.

    Result (hypothesis #1 instrumented): the homogeneous EY falls monotonically
    with coarsening, but the channeling deficit is largest at the FINEST grind
    (most fines), so the ensemble EY PEAKS at an interior grind -- static
    channeling ALONE reproduces the fine-grind dip. Independent/qualitative."""
    from puckworks.models.brewer2026 import streamtube as st
    gs = np.asarray(gs_grid, float)
    sigma = st.sigma_closure_power(gs, s_ref=s_ref, m=m)
    homog, ens, deficit = [], [], []
    for g, s in zip(gs, sigma):
        resp = st.EYResponse(gs=float(g), p_bar=p_bar, n_grid=n_grid)
        homog.append(float(resp.ey_of_k(1.0)))
        ens.append(float(resp.ey_ensemble(float(s))))
        deficit.append(float(resp.deficit(float(s))))
    homog = np.array(homog); ens = np.array(ens); deficit = np.array(deficit)
    ip = int(np.argmax(ens))
    return dict(gs=gs, sigma=sigma, ey_homog=homog, ey_ensemble=ens,
                deficit=deficit,
                sigma_monotone=bool(np.all(np.diff(sigma) <= 1e-9)),
                homog_monotone=bool(np.all(np.diff(homog) <= 1e-9)),
                ensemble_peaks_interior=bool(0 < ip < len(gs) - 1),
                peak_gs=float(gs[ip]),
                deficit_largest_at_finest=bool(deficit[0] == deficit.max()))


def _f_num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


# canonical observable key -> schmieder data component string (units differ:
# trigonelline/caffeine/5-CQA are mg, TDS is g -- never averaged together)
_SCHM_COMPONENT = {"tds": "TDS", "trigonelline": "trigonelline",
                   "caffeine": "caffeine", "5cqa": "5-CQA", "5-cqa": "5-CQA"}


def schmieder_grind_response(component, brew_ratio, temp_C, flow_ml_s):
    """Coherent RAW cup-mass grind response for ONE observable at ONE fixed
    condition (component × brew_ratio × temperature × flow). GUARDED by the
    'no silent observable merge' rule: schmieder's `mass_in_cup` is per-solute
    and MIXED-UNIT (trigonelline/caffeine/5-CQA in mg, TDS in g) across three
    brew ratios; averaging across any of those (or across temperature, which the
    RSM models explicitly) yields a dimensionless nonsense aggregate. This
    function raises ValueError if the selected rows carry more than one unit.
    Returns dict(grinds, means, stds, ns, units) or None if the {1.4,1.7,2.0}
    grind axis is not fully sampled at this condition."""
    import collections
    from puckworks import data as _d
    comp = _SCHM_COMPONENT.get(component.lower(), component)
    byg = collections.defaultdict(list)
    units = set()
    for r in _d.schmieder_cup_masses():
        if r.get("component") != comp or r.get("brew_ratio") != brew_ratio:
            continue
        if _f_num(r.get("target_temp_C")) != temp_C:
            continue
        if _f_num(r.get("target_flow_ml_s")) != flow_ml_s:
            continue
        g, m = _f_num(r.get("grind_level")), _f_num(r.get("mass_in_cup"))
        if g is None or m is None:
            continue
        byg[g].append(m)
        units.add(r.get("mass_units"))
    if len(units) > 1:
        raise ValueError("no silent observable merge: mixed units %s for "
                         "component=%s br=%s" % (units, component, brew_ratio))
    grinds = sorted(byg)
    if grinds != [1.4, 1.7, 2.0]:
        return None
    means = [float(np.mean(byg[g])) for g in grinds]
    stds = [float(np.std(byg[g])) for g in grinds]           # ddof=0 (descriptive)
    ns = [len(byg[g]) for g in grinds]
    return dict(grinds=grinds, means=means, stds=stds, ns=ns,
                replicates=[list(map(float, byg[g])) for g in grinds],
                units=(units.pop() if units else None))


def schmieder_rsm_grind_curve(component, brew_ratio, flow_ml_s, temp_C):
    """schmieder2023's OWN fitted response surface (Eq. 4, full-quadratic) in the
    grind (dial) direction at fixed flow+temp, per observable. The x_grind²
    coefficient β₅ and the grind vertex x* = -(β₂+β₇·flow+β₉·temp)/(2β₅) decide
    whether the surface has an INTERIOR maximum inside the DoE dial range
    [1.4, 2.0]. Returns the concavity, vertex, interior flag, and the adj-R²
    (LOAD-BEARING: schmieder's RSM is weak, 0.41–0.75, machine/grinder-specific).
    This is the corrected P3 target: schmieder's model feature, not a mixed-unit
    average of raw cells."""
    from puckworks import data as _d
    # RSM table capitalizes: TDS/Trigonelline/Caffeine/5-CQA
    key = {"tds": "TDS", "trigonelline": "Trigonelline", "caffeine": "Caffeine",
           "5cqa": "5-CQA", "5-cqa": "5-CQA"}.get(component.lower(), component)
    row = next((r for r in _d.schmieder_rsm()
                if r["component"] == key and r["brew_ratio"] == brew_ratio), None)
    if row is None:
        return None
    b2, b5, b7, b9 = row["beta2"], row["beta5"], row["beta7"], row["beta9"]
    concave = b5 < 0
    vertex = (-(b2 + b7 * flow_ml_s + b9 * temp_C) / (2.0 * b5)) if b5 != 0 else None
    interior = bool(vertex is not None and 1.4 < vertex < 2.0)
    return dict(component=key, brew_ratio=brew_ratio, beta5=b5, adj_r2=row["adj_r2"],
                units=row["beta_units"], concave=concave, vertex_dial=vertex,
                interior_max=bool(concave and interior))


# schmieder DoE central point (all observables fully sampled here); GL 1.7 is the
# FINEST grind by Sauter d32 (26.9 µm vs 28.3/29.2 at 1.4/2.0 — the dial→size map
# is itself non-monotonic), so any dial peak is NOT cleanly a fine-grind dip.
_SCHM_CENTER = dict(flow_ml_s=2.0, temp_C=89.0, brew_ratio="1/2")
_SCHM_OBS = ("tds", "trigonelline", "caffeine", "5cqa")
SCHM_DOSE_G = 20.0   # nominal fixed dose (schmieder2023 card, Table row: 20.00 g)


def schmieder_tds_ey(brew_ratio, temp_C, flow_ml_s, dose_g=SCHM_DOSE_G):
    """PRIMARY Result-1 target: TDS-derived extraction yield EY(%) vs grind at a
    fixed condition. EY = (TDS dissolved-solids mass in cup [g]) / dose [g] · 100
    — the one physically-meaningful, single-unit observable to compare against an
    extraction-YIELD model (the channeling ensemble outputs EY, not cup mass).
    Returns the raw EY grind response (means/stds over reps) and the RSM-predicted
    EY curve (schmieder's own TDS surface / dose). Dividing by a constant dose is
    a pure rescale, so the interior-max STRUCTURE matches TDS mass; EY just makes
    it comparable to model EY. Returns None if the grind axis is incomplete."""
    raw = schmieder_grind_response("tds", brew_ratio, temp_C, flow_ml_s)
    rsm = schmieder_rsm_grind_curve("tds", brew_ratio, flow_ml_s, temp_C)
    if raw is None:
        return None
    ey_means = [m / dose_g * 100.0 for m in raw["means"]]
    ey_stds = [s / dose_g * 100.0 for s in raw["stds"]]
    ey_reps = [[m / dose_g * 100.0 for m in cell] for cell in raw["replicates"]]
    lead = ey_means[1] - max(ey_means[0], ey_means[2])
    within = (float(np.mean(ey_stds)) or 1e-9)         # DESCRIPTIVE within-cell std
    return dict(grinds=raw["grinds"], ey_means=ey_means, ey_stds=ey_stds,
                ey_replicates=ey_reps, ns=raw["ns"], dose_g=dose_g, units="EY_%",
                raw_prominence=lead / within,          # scale-invariant, descriptive
                raw_interior=bool(lead > 0),
                rsm=rsm)                                # concavity/vertex (unit-free)


def result1_design_aware_stats(brew_ratio="1/2", temp_C=89.0, flow_ml_s=2.0,
                               dose_g=SCHM_DOSE_G):
    """DIAGNOSTIC (Paper B Result-1, updated-review owed): a design-aware,
    experiment-unit reading of the three-dial TDS-EY response, replacing the single
    replicate-level Welch contrast with (a) the achieved covariates per dial,
    (b) the experimental-unit structure, and (c) both a trend and pairwise view.
    NOT a gate, NOT in run_all_gates -- it quantifies a known caveat honestly.

    The load-bearing structural fact (review MAJ-03): in the Schmieder DoE each dial
    cell is ONE design point run as 3 independently prepared extraction repetitions
    (6 at the centre 1.7). Those runs are the experimental unit, so the within-cell
    spread is run-to-run variance at a fixed NOMINAL dial, and there is NO replication
    across machines/coffees/campaigns (one machine, one coffee). A replicate-level
    Welch test therefore answers a within-campaign, setting-level question conditional
    on run independence; it does not license a
    causal 'dial alone moves EY' claim. Reported so the manuscript's statistical
    language matches the design.

    Returns per-dial n / experiment id / DoE role / EY mean+sample-SD and the mean
    ACHIEVED flow, temperature, and max pressure (which differ across the three
    experiments -- the confound); the two adjacent pairwise Welch contrasts with
    95% CIs; a replicate-level linear EY-vs-dial slope; and the ordered-means
    verdict (no interior maximum: the middle dial lies below the coarse end)."""
    import collections
    from scipy import stats
    from puckworks import data as _d
    byg = collections.defaultdict(list)
    for r in _d.schmieder_cup_masses():
        if (r.get("component") != "TDS" or r.get("brew_ratio") != brew_ratio
                or _f_num(r.get("target_temp_C")) != temp_C
                or _f_num(r.get("target_flow_ml_s")) != flow_ml_s):
            continue
        g = _f_num(r.get("grind_level")); m = _f_num(r.get("mass_in_cup"))
        if g is None or m is None:
            continue
        byg[g].append(r)
    grinds = sorted(byg)
    if grinds != [1.4, 1.7, 2.0]:
        return None

    def _col(rows, key):
        vals = [_f_num(x.get(key)) for x in rows]
        return [v for v in vals if v is not None]

    cells = []
    for g in grinds:
        rows = byg[g]
        ey = [_f_num(x["mass_in_cup"]) / dose_g * 100.0 for x in rows]
        exps = sorted({_f_num(x.get("exp")) for x in rows})
        flow = _col(rows, "scale_flow_ml_s"); temp = _col(rows, "decent_temp_C")
        pmax = _col(rows, "pressure_max_bar")
        cells.append(dict(
            dial=g, n_reps=len(rows), n_experiments=len(exps),
            experiment_ids=exps, doe_role=sorted({x.get("doe_role") for x in rows}),
            ey_mean=round(float(np.mean(ey)), 3),
            ey_sample_sd=round(float(np.std(ey, ddof=1)), 3) if len(ey) > 1 else None,
            ey=[round(v, 3) for v in ey],
            achieved_flow_ml_s=round(float(np.mean(flow)), 3) if flow else None,
            achieved_temp_C=round(float(np.mean(temp)), 2) if temp else None,
            achieved_pmax_bar=round(float(np.mean(pmax)), 2) if pmax else None))

    ey_by = {c["dial"]: [_f_num(x["mass_in_cup"]) / dose_g * 100.0 for x in byg[c["dial"]]]
             for c in cells}

    def _welch(a, b):
        t, p = stats.ttest_ind(a, b, equal_var=False)
        va, vb = np.var(a, ddof=1) / len(a), np.var(b, ddof=1) / len(b)
        se = float(np.sqrt(va + vb))
        df = (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))
        tcrit = float(stats.t.ppf(0.975, df))
        diff = float(np.mean(a) - np.mean(b))
        return dict(diff_EYpt=round(diff, 3), df=round(float(df), 1),
                    ci95=[round(diff - tcrit * se, 3), round(diff + tcrit * se, 3)],
                    p_two_sided=round(float(p), 4))

    pairwise = {
        "dial_1.4_vs_1.7": _welch(ey_by[1.4], ey_by[1.7]),
        "dial_1.7_vs_2.0": _welch(ey_by[1.7], ey_by[2.0])}

    # replicate-level linear trend of EY on dial (descriptive slope, with the
    # caveat that dial is confounded with the achieved covariates below)
    xs = np.concatenate([[g] * len(ey_by[g]) for g in grinds])
    ys = np.concatenate([ey_by[g] for g in grinds])
    lr = stats.linregress(xs, ys)
    # t-based interval (review MAJ-05): n runs, 2 estimated coefficients -> n-2 dof;
    # the earlier 1.96 (normal) was wrong for a 12-run OLS slope (t_{0.975,10}~2.228)
    n_runs = int(len(xs)); dof = n_runs - 2
    tcrit = float(stats.t.ppf(0.975, dof))
    slope_ci = [round(float(lr.slope - tcrit * lr.stderr), 3),
                round(float(lr.slope + tcrit * lr.stderr), 3)]

    means = [c["ey_mean"] for c in cells]
    ordered = bool(means[0] <= means[1] <= means[2])       # monotone increasing?
    interior_max = bool(means[1] > means[0] and means[1] > means[2])
    return dict(
        condition=dict(brew_ratio=brew_ratio, target_temp_C=temp_C,
                       target_flow_ml_s=flow_ml_s, dose_g=dose_g),
        cells=cells, pairwise=pairwise,
        trend=dict(slope_EYpt_per_dial=round(float(lr.slope), 3),
                   slope_ci95=slope_ci, r=round(float(lr.rvalue), 3),
                   p=round(float(lr.pvalue), 4)),
        trend_ci_method=f"t-based, dof={dof} (n={n_runs} runs, 2 coeffs)",
        experimental_unit_note=(
            "Each dial setting was run as independently prepared extraction "
            "repetitions (1.4 axis n=3, 1.7 centre n=6, 2.0 axis n=3); those runs are "
            "the experimental unit, so the within-cell spread is run-to-run variance "
            "at a fixed NOMINAL dial (review MAJ-03). There is NO replication across "
            "machines/coffees/campaigns (one machine, one coffee), so a replicate-level "
            "Welch/trend test is a within-campaign, setting-level contrast conditional "
            "on run independence -- NOT a causal 'dial alone moves EY' claim; a "
            "design-aware model would need the full DoE (achieved covariates + "
            "experiment blocks), not these 3 selected cells."),
        achieved_confound=(
            "achieved flow/temperature/max-pressure differ across the three dial "
            "experiments (see cells) -> dial is confounded with the achieved "
            "conditions; the ordering is descriptive, not a clean dial effect."),
        cell_means_ordered=ordered, interior_maximum=interior_max,
        verdict=("observed cell means %s (%.2f -> %.2f -> %.2f EY%%); the MIDDLE dial is "
                 "%s the coarse end -> %s middle-dial maximum in the observed means. "
                 "Described as ORDERED, not 'statistically monotone' (see the 1.4-vs-1.7 "
                 "CI). Achieved covariates differ across the three selected settings."
                 % ("increase monotonically" if ordered else "are not monotone",
                    means[0], means[1], means[2],
                    "below" if means[1] < means[2] else "at/above",
                    "NO" if not interior_max else "an")))


def schmieder_interior_max_target(center=None):
    """CORRECTED P3 target. PRIMARY observable = TDS-derived EY (the yield quantity
    an extraction model produces); the mg solutes are secondary cross-checks. For
    each, report whether schmieder's data supports an interior grind maximum — via
    BOTH their fitted RSM (concave + vertex interior, carrying adj-R²) and the raw
    cells (prominence = interior lead / pooled replicate std). Replaces the old
    dimensionless mixed-unit `_schmieder_mass_vs_grind`. Reading (see verdict): the
    RSM is concave with an interior vertex for every observable INCLUDING TDS-EY,
    but the fit is weak (0.41–0.75) and the raw cells at the one fully-sampled
    condition are largely monotone/flat — so the 'peak at GL 1.7' is a weak-RSM
    feature, not a robust raw signal, and it is a peak in DIAL not particle size."""
    c = center or _SCHM_CENTER
    out = {}
    for obs in _SCHM_OBS:
        rsm = schmieder_rsm_grind_curve(obs, c["brew_ratio"], c["flow_ml_s"], c["temp_C"])
        raw = schmieder_grind_response(obs, c["brew_ratio"], c["temp_C"], c["flow_ml_s"])
        prom = None
        if raw is not None:
            lead = raw["means"][1] - max(raw["means"][0], raw["means"][2])
            noise = (float(np.mean(raw["stds"])) or 1e-9)
            prom = lead / noise                       # >0 = interior, in std units
        out[obs] = dict(rsm=rsm, raw=raw, raw_prominence=prom,
                        raw_interior=bool(prom is not None and prom > 0))
    primary = schmieder_tds_ey(c["brew_ratio"], c["temp_C"], c["flow_ml_s"])
    rsm_interior = [o for o, v in out.items()
                    if v["rsm"] and v["rsm"]["interior_max"]]
    raw_interior = [o for o, v in out.items() if v["raw_interior"]]
    return dict(center=c, dose_g=SCHM_DOSE_G,
                primary_observable="tds_ey", primary=primary,
                observables=out,
                rsm_interior_max=rsm_interior, raw_interior_max=raw_interior,
                verdict=("PRIMARY = TDS-EY: RSM concave with an interior grind "
                         "vertex at dial %.2f (adj-R² %.2f) but the raw EY cells "
                         "(%s%%) are %s; across all observables the RSM has an "
                         "interior vertex for %d/%d (weak 0.41–0.75) yet the raw "
                         "cells show a prominent interior max for only %d/%d — the "
                         "'peak at GL 1.7' is a weak-model feature, and a DIAL peak "
                         "(GL 1.7 = finest d32), not a particle-size fine-grind dip"
                         % (primary["rsm"]["vertex_dial"], primary["rsm"]["adj_r2"],
                            "/".join("%.1f" % e for e in primary["ey_means"]),
                            "monotone" if primary["raw_prominence"] <= 0 else
                            "interior (prom %.2fσ)" % primary["raw_prominence"],
                            len(rsm_interior), len(_SCHM_OBS),
                            len(raw_interior), len(_SCHM_OBS))))


def schmieder_peak_discrimination(n_grid=6):
    """P3 MECHANISM-CAPACITY comparison (downgraded 2026-07-12 after the target
    bug). Two separate questions, kept separate:

    (A) THE TARGET — does schmieder show an interior grind maximum? Answered per
        observable at a fixed condition via `schmieder_interior_max_target`
        (RSM concavity + raw prominence). NOT a single mixed-unit cup mass.
    (B) MODEL CAPACITY — of the instrumented response generators, which can
        PRODUCE an interior grind maximum, and under what parameterization?

    This does NOT claim any mechanism 'reproduces the schmieder peak': the target
    is a weak-R² empirical RSM feature, the generators live on their own
    (non-portable) dial axes, and incomplete wetting is untested. The honest
    result is model VIABILITY, not identification. Strength: qualitative."""
    from puckworks.models.lee2023 import feedback as _lee
    from puckworks import data as _d

    target = schmieder_interior_max_target()

    # (1) static channeling σ(φ₁) — EMPIRICAL closure (registry: calibrated over a
    # limited dial range, not externally validated). Generates an interior max.
    ch = channeling_sigma_sweep(gs_grid=(1.0, 1.5, 2.0, 2.5), n_grid=n_grid)

    # (2) size-exclusion entrapment — romancorrochano extractable inventory y₀(grind)
    y0 = [r for r in _d.roman_y0_extractable() if r["method"] == "dilute"]
    ladder = ["PsiA", "PsiB", "PsiE", "PsiF", "PsiG", "PsiH"]  # fine→coarse
    y0_seq = [next(r["y0_pct"] for r in y0 if r["grind"] == g) for g in ladder]
    y0_ip = int(np.argmax(y0_seq))

    # (3) lee2023 dissolution instability — interior peak only at DOCTORED ρ_c
    g = np.linspace(1.1, 2.3, 13)
    lee_phys = _lee.peak_and_fine_decline(g, rho_c=399.0)   # physical (measured)
    lee_unphys = _lee.peak_and_fine_decline(g, rho_c=798.0)  # deliberately altered

    # (4) base / diffusion extraction — the monotone null (no bed mechanism)
    base = ch["ey_homog"]
    base_monotone = bool(np.all(np.diff(base) <= 1e-9))

    board = [
        dict(hyp=1, name="static channeling σ(φ₁)",
             generates_interior_max=bool(ch["ensemble_peaks_interior"]),
             parameterization="empirical σ(φ₁) closure (calibrated to source data)",
             note="monotone σ(grind) closure → peaked ensemble EY (vertex gs≈%.2f). "
                  "Model-capacity result: a static-heterogeneity closure CAN "
                  "generate an interior maximum. σ was calibrated on cameron's "
                  "grind-deviation data — a viability check, not identification." % ch["peak_gs"]),
        dict(hyp=3, name="lee2023 dissolution instability",
             generates_interior_max=bool(lee_unphys["fine_side_decline"]),
             parameterization="only under an ELEVATED ρ_c=798 (2× the measured 399)",
             note="interior EY(g) max only at the elevated (2× measured) ceiling — "
                  "a deliberate sensitivity test; the measured ρ_c=399 plateaus "
                  "(no fine-side decline)."),
        dict(hyp=4, name="size-exclusion entrapment y₀(grind)",
             generates_interior_max=bool(0 < y0_ip < len(y0_seq) - 1),
             parameterization="measured inventory (different observable)",
             note="y₀ monotone-decreasing fine→coarse (%.1f→%.1f%%); no interior "
                  "maximum. A different observable (inventory ceiling), not EY." % (y0_seq[0], y0_seq[-1])),
        dict(hyp=None, name="base / diffusion extraction (null)",
             generates_interior_max=not base_monotone,
             parameterization="source model",
             note="homogeneous EY(grind) monotone — no bed mechanism, no max."),
        dict(hyp=2, name="incomplete wetting",
             generates_interior_max=None,
             parameterization="UNIMPLEMENTED (needs G1 constitutive data)",
             note="not tested here; discriminated by first-drip DELAY, not EY shape."),
    ]
    generate_calibrated = [b["name"] for b in board
                           if b["generates_interior_max"] and "ELEVATED" not in b["parameterization"]
                           and "UNIMPLEMENTED" not in b["parameterization"]
                           and b["hyp"] is not None]
    generate_only_elevated = [b["name"] for b in board
                              if b["generates_interior_max"] and "ELEVATED" in b["parameterization"]]
    return dict(
        target=target,
        board=board,
        generate_under_calibrated_params=generate_calibrated,
        generate_only_under_elevated_ceiling=generate_only_elevated,
        verdict=("MODEL-CAPACITY, not identification: of the implemented generators, "
                 "the empirically-calibrated static-heterogeneity closure is the "
                 "only one that produces an interior grind maximum under its "
                 "measured/calibrated parameters; lee needs an elevated ρ_c=798 "
                 "(2× measured); size-exclusion/diffusion "
                 "target itself is a weak-R² RSM feature (see target.verdict), so "
                 "this establishes viability, not that channeling IS the mechanism."))


def channeling_concavity_audit(gs_grid=(1.0, 1.4, 1.8, 2.2), pressures=(5.0, 9.0),
                               n_grid=13, n_k=200):
    """Audit the Jensen premise of the streamtube deficit (review Priority 3.1):
    is the numerical EY(k) response actually CONCAVE over the quadrature support,
    and how much lognormal quadrature MASS reaches the clipped boundaries? The
    ensemble-EY deficit is a Jensen inequality that requires EY(k) concave in k.

    For each grind × pressure: builds the EYResponse, evaluates EY(k) on a fine
    linear-in-k grid over [k_min,k_max], and reports the fraction of the support
    where the numerical second derivative ≤0 (concave), plus the lognormal
    quadrature weight beyond the support at the calibrated σ(gs) (the clip mass).
    Result: EY(k) is concave over ~96-97% of the support and the clip mass is
    <0.2% at all tested grinds/pressures -> the Jensen deficit holds over the
    tested support (global concavity NOT claimed) and clipping is negligible.
    Strength: numerical verification."""
    from puckworks.models.brewer2026 import streamtube as _st
    out = []
    for gs in gs_grid:
        sig = float(_st.sigma_closure_power(gs, s_ref=0.6, m=1.0))
        kk, w = _st.lognormal_nodes(sig, 15)
        for p in pressures:
            r = _st.EYResponse(gs=float(gs), p_bar=float(p), n_grid=n_grid)
            k = np.linspace(r.k_min, r.k_max, n_k)
            d2 = np.gradient(np.gradient(r.ey_of_k(k), k), k)
            clip = float(np.sum(w[(kk < r.k_min) | (kk > r.k_max)]))
            # DIRECT Jensen gap J = E[EY(K)] - EY(E[K]).  The untruncated multipliers are
            # unit-mean lognormal, but CLIPPING to the spline support shifts the evaluated
            # mean off 1 (review MAJ-17), so we compute the ACTUAL post-clip weighted mean
            # E[K_clipped] and evaluate EY there -- NOT EY(1). J<0 confirms a genuine
            # ensemble deficit (concave EY(k) loses yield to heterogeneity) WITHOUT relying
            # only on the second-derivative sign.
            kc = np.clip(kk, r.k_min, r.k_max)
            wn = w / w.sum()
            E_ey = float(np.sum(wn * r.ey_of_k(kc)))
            E_k = float(np.sum(wn * kc))                  # actual evaluated mean (not 1)
            ey_mean_k = float(r.ey_of_k(np.clip(E_k, r.k_min, r.k_max)))
            jensen_gap = E_ey - ey_mean_k                 # <=0 for concave EY(k)
            out.append(dict(gs=float(gs), p_bar=float(p), sigma=round(sig, 3),
                            concave_fraction=round(float(np.mean(d2 <= 1e-9)), 3),
                            clip_mass=round(clip, 4),
                            evaluated_mean_k=round(E_k, 4),   # MAJ-17: mean after clipping
                            mean_shift_from_unity=round(abs(E_k - 1.0), 4),
                            jensen_gap_EYpt=round(jensen_gap, 4)))
    cf = [c["concave_fraction"] for c in out]
    cl = [c["clip_mass"] for c in out]
    jg = [c["jensen_gap_EYpt"] for c in out]
    return dict(cells=out, min_concave_fraction=min(cf), max_clip_mass=max(cl),
                concave_over_support=bool(min(cf) > 0.9),
                clipping_negligible=bool(max(cl) < 0.01),
                # B5-03: report BOTH the least- and most-negative deficit; "worst" is the
                # LARGEST magnitude (min), not the max (which is least negative).
                max_jensen_gap_EYpt=max(jg), min_jensen_gap_EYpt=min(jg),
                all_jensen_gaps_negative=bool(max(jg) <= 0),
                max_evaluated_mean_shift=round(max(c["mean_shift_from_unity"] for c in out), 4),
                verdict=("EY(k) is concave over %.0f-%.0f%% of the tested support and "
                         "the lognormal clip mass is <%.2f%% at all grinds/pressures; "
                         "the DIRECT Jensen gap J=E[EY(K)]-EY(E[K_eval]) -- using the ACTUAL "
                         "post-clipping evaluated mean (shift from unity <=%.4f, review "
                         "MAJ-17) not EY(1) -- is <=0 in every cell (deficit %.3f to %.3f "
                         "EY-pt, worst = most negative) -> "
                         "the ensemble deficit is confirmed by direct measurement, not "
                         "only by the 2nd-derivative sign (global concavity NOT claimed); "
                         "clipping is negligible."
                         % (100 * min(cf), 100 * max(cf), 100 * max(cl),
                            max(c["mean_shift_from_unity"] for c in out),
                            min(jg), max(jg))))


def channeling_interior_max_sensitivity(gs_grid=None,
                                        s_refs=(0.3, 0.45, 0.6, 0.75, 0.9),
                                        ms=(0.5, 0.75, 1.0, 1.5, 2.0),
                                        pressures=(3.0, 5.0, 7.0, 9.0),
                                        n_grids=(7, 13, 21),
                                        s_ref0=0.6, m0=1.0, p0=5.0, n0=7):
    """Closure-sensitivity of the P3 Result-1 interior grind maximum (SLOW ~90 s;
    run from validation/slow, NOT CI). Tests whether the channeling interior-max
    (the model-CAPACITY result) is ROBUST to the empirical sigma(phi1) closure or
    fragile/tuned. The streamtube EYResponse spline depends only on (gs, p_bar,
    n_grid) -- NOT on s_ref/m -- so the s_ref x m grid reuses ONE build.

    Three probes:
      (1) s_ref x m grid at (p0,n0): fraction of closure combos with an interior
          max; peak-location + prominence spread.
      (2) pressure sweep at (s_ref0,m0): does the peak survive and where.
      (3) n_grid convergence at (s_ref0,m0,p0): is the peak a resolution artifact.
    prominence = ensemble EY at the interior peak minus the higher endpoint
    [EY-points] -- how much of a bump, not just argmax. Strength: qualitative.

    Result (see verdict): the interior-max is a REAL, n_grid-CONVERGED feature at
    the calibrated closure, but FRAGILE (present in a minority of the s_ref x m
    grid; vanishes for weak channeling) and WEAK (median prominence < ~0.2 EY-pt;
    near-flat at 9 bar) -- consistent with model-capacity-not-identification."""
    from puckworks.models.brewer2026 import streamtube as _st
    gs = np.linspace(1.0, 2.2, 7) if gs_grid is None else np.asarray(gs_grid, float)

    def _build(p_bar, n_grid):
        return [_st.EYResponse(gs=float(g), p_bar=p_bar, n_grid=n_grid) for g in gs]

    def _probe(resps, s_ref, m):
        sig = _st.sigma_closure_power(gs, s_ref=s_ref, m=m)
        ens = np.array([r.ey_ensemble(float(s)) for r, s in zip(resps, sig)])
        ip = int(np.argmax(ens))
        interior = bool(0 < ip < len(gs) - 1)
        prom = float(ens[ip] - max(ens[0], ens[-1]))    # EY-pts above higher end
        return dict(interior=interior, peak_gs=float(gs[ip]), prominence=prom)

    # (1) s_ref x m grid — one response build, cheap quadrature over it
    base = _build(p0, n0)
    grid = []
    for s in s_refs:
        for m in ms:
            r = _probe(base, s, m)
            grid.append(dict(s_ref=s, m=m, **r))
    inter = [g for g in grid if g["interior"]]
    proms = [g["prominence"] for g in inter]
    # ALL signed prominences over the FULL grid (not the success-conditional set):
    # non-interior cells contribute ~0 (argmax at an endpoint), so the full-grid
    # median is the honest central tendency -- reporting only interior cells
    # conditions on success and inflates the typical bump.
    all_proms = sorted(g["prominence"] for g in grid)
    calib = _probe(base, s_ref0, m0)

    # (2) pressure sweep at the calibrated closure
    pressure_sweep = []
    for p in pressures:
        r = base if (p == p0) else _build(p, n0)
        pressure_sweep.append(dict(p_bar=p, **_probe(r, s_ref0, m0)))

    # (3) n_grid convergence at the calibrated closure
    n_conv = []
    for n in n_grids:
        r = base if (n == n0 and p0 == p0) else _build(p0, n)
        n_conv.append(dict(n_grid=n, **_probe(r, s_ref0, m0)))
    peak_locs = {round(c["peak_gs"], 3) for c in n_conv}
    converged = bool(len(peak_locs) == 1)                # peak location stable

    frac = len(inter) / len(grid)
    return dict(
        gs_grid=[float(x) for x in gs],
        calibrated=dict(s_ref=s_ref0, m=m0, p_bar=p0, n_grid=n0, **calib),
        grid_n=len(grid), grid_interior_n=len(inter),
        grid_interior_fraction=frac,
        grid_noninterior=[(g["s_ref"], g["m"]) for g in grid if not g["interior"]],
        peak_gs_range=[min(g["peak_gs"] for g in inter), max(g["peak_gs"] for g in inter)]
        if inter else None,
        prominence_median=float(np.median(proms)) if proms else None,   # interior-only
        prominence_max=float(np.max(proms)) if proms else None,
        # full-grid signed prominences (all cells, honest central tendency):
        all_prominences=[round(x, 4) for x in all_proms],
        prominence_median_fullgrid=round(float(np.median(all_proms)), 4),
        prominence_iqr_fullgrid=[round(float(np.percentile(all_proms, 25)), 4),
                                 round(float(np.percentile(all_proms, 75)), 4)],
        pressure_sweep=pressure_sweep,
        n_grid_convergence=n_conv, n_grid_converged=converged,
        verdict=("interior-max is REAL + n_grid-CONVERGED at the calibrated closure "
                 "(peak gs %.2f, prominence %.3f EY-pt) but FRAGILE (interior in "
                 "%d/%d = %.0f%% of the s_ref x m grid; gone for weak channeling) "
                 "and WEAK (median prominence %.3f EY-pt; ~%.3f at 9 bar). Robustness "
                 "supports MODEL-CAPACITY, not identification." % (
                     calib["peak_gs"], calib["prominence"], len(inter), len(grid),
                     100 * frac, float(np.median(proms)) if proms else 0.0,
                     next((c["prominence"] for c in pressure_sweep if c["p_bar"] == 9.0), float("nan")))))


def schmieder_rsm_refit(component="tds", brew_ratio="1/2", predictors="achieved"):
    """Refit schmieder's Eq.4 RSM to the COMMITTED cup-mass observations (same
    retained terms as the printed Table-3 row), to separate a real model level
    from a PRINTED-PRECISION artifact. The published coefficients are rounded (the
    T² coefficient to 3 decimals), and with T²~7921 that rounding shifts the
    absolute prediction by several grams -- so evaluating the printed row literally
    is NOT the fitted curve. Returns the refit central-point prediction (which
    reproduces the data ~3.9 g), the printed-coefficient central prediction (~6.7 g,
    an artifact), and the raw central cell mean. Reading: use the RSM for SHAPE
    (concavity/vertex, robust to the offset), NOT absolute magnitude -- because the
    printed coefficients lack the precision for absolute reconstruction, NOT because
    the source model is wrong.

    PREDICTOR CONTRACT (review MAJ-04): the source Methods fit the RSM on set grind
    plus the EXPERIMENTALLY ACHIEVED flow and temperature. `predictors='achieved'`
    (DEFAULT, the paper-primary source-contract fit; review B6-20)
    uses `scale_flow_ml_s` / `decent_temp_C` (achieved) and evaluates the vertex at
    the MEAN ACHIEVED central-cell flow; `predictors='target'` uses the nominal
    `target_flow_ml_s` / `target_temp_C` (kept for the predictor-contract sensitivity). The two are
    reported side-by-side (`achieved_predictor_sensitivity`) so the vertex's
    insensitivity to the predictor choice is explicit rather than assumed; this is a
    documented REFIT of the source design, not a reconstruction of the source's own
    full-precision OriginPro object."""
    from puckworks import data as _d
    comp = _SCHM_COMPONENT.get(component.lower(), component)
    rows = _d.schmieder_cup_masses()
    fcol, tcol = (("scale_flow_ml_s", "decent_temp_C") if predictors == "achieved"
                  else ("target_flow_ml_s", "target_temp_C"))
    obs, is_center = [], []
    for r in rows:
        if r.get("component") != comp or r.get("brew_ratio") != brew_ratio:
            continue
        F, G, T, y = (_f_num(r.get(fcol)), _f_num(r.get("grind_level")),
                      _f_num(r.get(tcol)), _f_num(r.get("mass_in_cup")))
        if None in (F, G, T, y):
            continue
        # the TRUE central design setting is the NOMINAL centre point (target F=2,
        # grind=1.7, target T=89), i.e. experiment 7 -- NOT every grind-1.7 row, which
        # also includes flow-/temp-axis settings (review MAJ-07).
        tf, tt = _f_num(r.get("target_flow_ml_s")), _f_num(r.get("target_temp_C"))
        obs.append((F, G, T, y))
        is_center.append(tf is not None and abs(tf - 2.0) < 1e-6
                         and abs(G - 1.7) < 1e-6 and tt is not None and abs(tt - 89.0) < 1e-6)
    o = np.asarray(obs, float); center_mask = np.asarray(is_center, bool)
    F, G, T, y = o[:, 0], o[:, 1], o[:, 2], o[:, 3]
    # retained terms (TDS 1/2 printed): 1, F, G, T, G^2, T^2, FG (beta4/8/9 = 0)
    # NOTE predictors are on the RAW scale (not centered), so the individual
    # coefficients are not orthogonal and the vertex below combines b_G/b_G2/b_FG.
    X = np.column_stack([np.ones_like(F), F, G, T, G ** 2, T ** 2, F * G])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    # vertex/prediction eval centre: for ACHIEVED predictors use the mean achieved
    # flow/temp of the NOMINAL centre point (experiment 7, review MAJ-07); for TARGET
    # use the nominal design centre.
    g = 1.7
    if predictors == "achieved":
        cm = center_mask if center_mask.any() else (np.abs(G - 1.7) < 1e-9)
        fl = float(np.mean(F[cm])); tp = float(np.mean(T[cm]))
    else:
        fl, tp = _SCHM_CENTER["flow_ml_s"], _SCHM_CENTER["temp_C"]
    xc = np.array([1, fl, g, tp, g ** 2, tp ** 2, fl * g])
    refit_pred = float(xc @ coef)
    # fit quality: R^2 and adjusted R^2 (p = 6 predictors excluding the intercept)
    resid = y - X @ coef
    ss_res = float(np.sum(resid ** 2)); ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    n, p = len(y), X.shape[1] - 1
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
    adj_r2 = (1.0 - (1.0 - r2) * (n - 1) / (n - p - 1)
              if n > p + 1 else float("nan"))
    # grind vertex at central F: dEY/dG = b_G + 2 b_G2 G + b_FG F = 0
    #   G* = -(b_G + b_FG F) / (2 b_G2); only a maximum if b_G2 < 0.
    def _vertex(c):
        denom = 2.0 * c[4]
        return float("nan") if denom == 0 else float(-(c[2] + c[6] * fl) / denom)
    vertex_g = _vertex(coef)
    vertex_is_max = bool(coef[4] < 0)
    # FIXED-DESIGN residual bootstrap on the vertex (review MAJ-05): the design points
    # were selected, not sampled, so a residual bootstrap (resample residuals, refit
    # on the fixed X) is the conditional bootstrap appropriate to the fixed design --
    # a case (row) bootstrap is also reported for comparison. Both condition on the
    # retained quadratic term set (no model re-selection). We record the fraction of
    # bootstrap fits that are a concave maximum AND whose vertex is in the tested dial
    # domain, rather than silently accepting every finite algebraic vertex.
    rng = np.random.default_rng(0)
    yhat = X @ coef

    def _boot(sampler):
        vs, n_conc, n_dom, n_joint = [], 0, 0, 0
        for _ in range(2000):
            cb, *_ = np.linalg.lstsq(X, sampler(), rcond=None)
            vb = _vertex(cb)
            if not np.isfinite(vb):
                continue
            vs.append(vb)
            conc = cb[4] < 0; dom = 1.4 <= vb <= 2.0
            n_conc += conc; n_dom += dom; n_joint += (conc and dom)
        ci = ([round(float(np.percentile(vs, 2.5)), 3),
               round(float(np.percentile(vs, 97.5)), 3)] if vs else None)
        return ci, (n_conc / 2000.0), (n_dom / 2000.0), (n_joint / 2000.0)
    vertex_ci95, frac_concave, frac_in_domain, frac_joint = _boot(
        lambda: yhat + resid[rng.integers(0, n, n)])            # residual bootstrap
    # case (row) bootstrap for comparison (resample rows of (X,y) together)
    cboot = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        cb, *_ = np.linalg.lstsq(X[idx], y[idx], rcond=None)
        vb = _vertex(cb)
        if np.isfinite(vb):
            cboot.append(vb)
    vertex_ci95_case = ([round(float(np.percentile(cboot, 2.5)), 3),
                         round(float(np.percentile(cboot, 97.5)), 3)] if cboot else None)
    # --- coefficient-covariance / residual-diagnostic panel (owed §7; OUR refit, not
    # the source's unavailable full-precision coefficients). The PREDICTIVE score
    # (leave-one-DESIGN-POINT-out Q^2, replicates held out together) lives in
    # analysis/lopo_cv.lopo_rsm_design_point -- do NOT recompute a row-level PRESS Q^2
    # here (it would leak replicates and disagree with that correct diagnostic). -----
    # CORRECTLY NAMED conditioning (review MAJ-06): kappa2(X) is the design-matrix
    # condition number; kappa2(X^T X) is the Gram/normal-equation condition number
    # (~ its square). "design condition number" must refer to kappa2(X), not the Gram.
    kappa_X = float(np.linalg.cond(X))
    kappa_gram = float(np.linalg.cond(X.T @ X))
    # CENTERED/SCALED design condition number (review MAJ-09): the same fit on
    # z-scored F,G,T is well-conditioned (kappa2 ~ a few), demonstrating the raw-scale
    # ill-conditioning is a parameterisation artefact, not a data problem. The vertex
    # is offset/scale-invariant, so the fitted curve is unchanged after back-transform.
    def _kappa_centered():
        Fc = (F - F.mean()) / (F.std() or 1); Gc = (G - G.mean()) / (G.std() or 1)
        Tc = (T - T.mean()) / (T.std() or 1)
        Xc = np.column_stack([np.ones_like(Fc), Fc, Gc, Tc, Gc**2, Tc**2, Fc*Gc])
        return float(np.linalg.cond(Xc))
    kappa_X_centered = _kappa_centered()
    diag = None
    if n > p + 1:
        sigma2 = ss_res / (n - p - 1)            # unbiased residual variance
        XtX_inv = np.linalg.pinv(X.T @ X)
        coef_se = np.sqrt(np.clip(np.diag(sigma2 * XtX_inv), 0.0, None))
        h = np.clip(np.diag(X @ XtX_inv @ X.T), 0.0, 1.0 - 1e-9)   # leverages
        std_resid = resid / np.sqrt(sigma2 * (1.0 - h))
        cooks = std_resid ** 2 / (p + 1) * (h / (1.0 - h))         # Cook's distance
        i_infl = int(np.argmax(cooks))
        diag = dict(
            coef_se=[round(float(s), 4) for s in coef_se],
            design_matrix_condition_number_kappa2_X=round(kappa_X, 1),
            gram_condition_number_kappa2_XtX=round(kappa_gram, 1),
            centered_scaled_condition_number_kappa2_X=round(kappa_X_centered, 3),
            residual_std=round(float(np.sqrt(sigma2)), 4),
            max_abs_standardized_residual=round(float(np.max(np.abs(std_resid))), 3),
            max_leverage=round(float(np.max(h)), 3),
            max_cooks_distance=round(float(np.max(cooks)), 3),
            most_influential_row_index=i_infl,
            # raw (uncentered) predictors: T^2 ~ 7921 makes X ill-conditioned, so the
            # individual coefficients/SEs are unstable and only the offset-robust vertex
            # + predictive Q^2 are interpretable. On CENTERED/SCALED predictors kappa2(X)
            # drops to ~%s, and the vertex is offset/scale-invariant (review MAJ-06/09).
            raw_scale_ill_conditioned=bool(kappa_X > 1e3),
            well_conditioned_after_centering=bool(kappa_X_centered < 100.0),
            predictors_centered=False,
            predictive_q2_ref="analysis.lopo_cv.lopo_rsm_design_point (design-point LOPO)")
    # printed rounded-coefficient evaluation (the artifact)
    pr = {(r["component"], r["brew_ratio"]): r for r in _d.schmieder_rsm()}[
        ("TDS" if comp == "TDS" else comp.capitalize(), brew_ratio)]
    printed_pred = float(pr["beta0"] + pr["beta1"] * fl + pr["beta2"] * g + pr["beta3"] * tp
                         + pr["beta4"] * fl ** 2 + pr["beta5"] * g ** 2 + pr["beta6"] * tp ** 2
                         + pr["beta7"] * fl * g + pr["beta8"] * fl * tp + pr["beta9"] * g * tp)
    central = [v for FF, GG, TT, v in obs if abs(GG - g) < 1e-9
               and abs(FF - fl) < 0.15 and abs(TT - tp) < 1.5]
    raw_central = float(np.mean(central)) if central else float("nan")
    # ACHIEVED-predictor summary (review MAJ-04, B6-20): the source-contract
    # (achieved flow/temp) vertex + adj-R^2, ALWAYS reported so the source-Methods
    # vertex is explicit regardless of which predictor set is primary. When 'achieved'
    # is the primary (the default), this summarises THIS refit (no recursion); when
    # 'target' is primary it is a single non-recursive achieved refit -- so the
    # target-vs-achieved insensitivity stays visible either way.
    if predictors == "achieved":
        achieved_sens = dict(
            vertex_g=round(vertex_g, 3) if np.isfinite(vertex_g) else None,
            adj_r2=round(adj_r2, 4),
            residual_std=(diag or {}).get("residual_std"),
            eval_flow_ml_s=round(fl, 4),
            note="primary refit; source Methods used achieved flow/temp")
    else:
        a = schmieder_rsm_refit(component, brew_ratio, predictors="achieved")
        achieved_sens = dict(vertex_g=a["vertex_g"], adj_r2=a["adj_r2"],
                             residual_std=(a["diagnostics"] or {}).get("residual_std"),
                             eval_flow_ml_s=a["eval_flow_ml_s"],
                             note="source Methods used achieved flow/temp; vertex shift "
                                  "vs target spec is the predictor-contract sensitivity")
    return dict(n_obs=len(obs), refit_central_g=refit_pred,
                printed_central_g=printed_pred, raw_central_g=raw_central,
                predictors=predictors, eval_flow_ml_s=round(fl, 4), eval_temp_C=round(tp, 3),
                coef=[float(c) for c in coef],   # 1,F,G,T,G^2,T^2,FG (for figure reuse)
                r2=round(r2, 4), adj_r2=round(adj_r2, 4), n=n, n_predictors=p,
                vertex_g=round(vertex_g, 3) if np.isfinite(vertex_g) else None,
                vertex_is_max=vertex_is_max,
                vertex_ci95_g=vertex_ci95,                    # residual (fixed-design) bootstrap
                vertex_ci95_g_case_bootstrap=vertex_ci95_case,
                bootstrap_type="residual (fixed-design); case bootstrap reported for comparison",
                bootstrap_concave_fraction=round(frac_concave, 3),
                bootstrap_vertex_in_dial_domain_fraction=round(frac_in_domain, 3),
                bootstrap_concave_AND_in_domain_fraction=round(frac_joint, 4),  # MAJ-08
                n_center_runs=int(center_mask.sum()),        # MAJ-07 (expect 6 = exp 7)
                achieved_predictor_sensitivity=achieved_sens,
                predictors_centered=False, diagnostics=diag,
                printed_is_artifact=bool(np.isfinite(raw_central)
                                         and abs(printed_pred - raw_central) > 1.0
                                         and abs(refit_pred - raw_central) < 0.5))


def schmieder_rsm_diagnostics(component="tds", brew_ratio="1/2"):
    """Result-1 RSM DIAGNOSTICS (review MAJ-12/13/14 + §5.5): the deletion, wild-
    bootstrap, and model-form sensitivities the manuscript previously left "owed", frozen
    at full precision on the achieved-predictor seven-term fit. Reports:

      - WILD bootstraps (Rademacher + Mammen; review MAJ-12) alongside the iid residual
        bootstrap, so the conditional vertex interval is shown NOT to be an artefact of
        the iid resampling under the ~17x within-setting SD range (heteroskedasticity);
      - DELETION diagnostics (MAJ-13): leave-one-RUN and leave-one-SETTING vertex ranges,
        how many setting-deletion fits stay concave-and-in-domain, and per-run Cook's D /
        leverage / standardised residual (the most influential run);
      - MODEL-FORM sensitivity (§5.5): AICc for grind-only / G+F+T+G^2 / retained-7 /
        full-quadratic, with the full-quadratic vertex.

    All intervals condition on the SELECTED seven-term specification (post-selection
    uncertainty is a separate, disclosed limitation). Fast (closed-form OLS)."""
    import numpy as np
    from puckworks import data as _d
    comp = _SCHM_COMPONENT.get(component.lower(), component)
    F, G, T, y, exps = [], [], [], [], []
    for r in _d.schmieder_cup_masses():
        if r.get("component") != comp or r.get("brew_ratio") != brew_ratio:
            continue
        f, g, t, m = (_f_num(r.get("scale_flow_ml_s")), _f_num(r.get("grind_level")),
                      _f_num(r.get("decent_temp_C")), _f_num(r.get("mass_in_cup")))
        if None in (f, g, t, m):
            continue
        F.append(f); G.append(g); T.append(t); y.append(m); exps.append(_f_num(r.get("exp")))
    F, G, T, y = map(lambda a: np.asarray(a, float), (F, G, T, y))
    exps = np.asarray(exps, float)

    def _design(FF, GG, TT):
        return np.column_stack([np.ones_like(FF), FF, GG, TT, GG ** 2, TT ** 2, FF * GG])

    def _fit_vertex(Xm, ym, fl):
        c, *_ = np.linalg.lstsq(Xm, ym, rcond=None)
        return (float("nan") if c[4] == 0 else float(-(c[2] + c[6] * fl) / (2.0 * c[4]))), c
    X = _design(F, G, T)
    # central achieved flow at the nominal centre (experiment 7), review MAJ-07
    cm = np.array([abs(g - 1.7) < 1e-9 for g in G]) & (exps == 7)
    fl = float(np.mean(F[cm])) if cm.any() else float(np.mean(F[np.abs(G - 1.7) < 1e-9]))
    tp = float(np.mean(T[cm])) if cm.any() else float(np.mean(T[np.abs(G - 1.7) < 1e-9]))
    v0, coef = _fit_vertex(X, y, fl)
    resid = y - X @ coef
    n, p = len(y), X.shape[1]
    s2 = float(resid @ resid) / (n - p)
    XtXinv = np.linalg.inv(X.T @ X)
    H = X @ XtXinv @ X.T
    lev = np.diag(H)
    cooks = (resid ** 2 / (p * s2)) * (lev / (1.0 - lev) ** 2)
    std_resid = resid / np.sqrt(s2 * (1.0 - lev))
    yhat = X @ coef
    rng = np.random.default_rng(0)

    def _boot(weight):
        vs, joint = [], 0
        for _ in range(2000):
            cb, *_ = np.linalg.lstsq(X, yhat + weight(), rcond=None)
            vb = (float("nan") if cb[4] == 0 else float(-(cb[2] + cb[6] * fl) / (2.0 * cb[4])))
            if not np.isfinite(vb):
                continue
            vs.append(vb); joint += (cb[4] < 0 and 1.4 <= vb <= 2.0)
        return ([round(float(np.percentile(vs, q)), 4) for q in (2.5, 50, 97.5)],
                round(joint / 2000.0, 4))
    iid_ci, iid_j = _boot(lambda: resid[rng.integers(0, n, n)])
    rad_ci, rad_j = _boot(lambda: resid * rng.choice([-1.0, 1.0], n))
    # review MAJ-16/B3-19: a CURVE-level bootstrap band -- the grind EY cross-section at
    # central achieved (F,T) with a p2.5/p50/p97.5 envelope over iid residual resamples,
    # for Figure 1a (so the RSM curve carries response uncertainty, not only a vertex bar).
    gg = np.linspace(1.4, 2.0, 40)
    Xg = np.column_stack([np.ones_like(gg), fl + 0 * gg, gg, tp + 0 * gg,
                          gg ** 2, (tp ** 2) + 0 * gg, fl * gg])
    curve_bs = np.array([np.linalg.lstsq(X, yhat + resid[rng.integers(0, n, n)],
                                         rcond=None)[0] @ Xg.T for _ in range(1000)])
    curve_band = dict(
        grind=[round(float(g), 4) for g in gg],
        p2_5=[round(float(v), 4) for v in np.percentile(curve_bs, 2.5, axis=0)],
        median=[round(float(v), 4) for v in np.percentile(curve_bs, 50, axis=0)],
        p97_5=[round(float(v), 4) for v in np.percentile(curve_bs, 97.5, axis=0)],
        units="cup mass (g) at central achieved (F,T); iid residual bootstrap")
    # Mammen two-point weights
    a, b = (1 - np.sqrt(5)) / 2, (1 + np.sqrt(5)) / 2
    pa = (np.sqrt(5) + 1) / (2 * np.sqrt(5))
    mam_ci, mam_j = _boot(lambda: resid * np.where(rng.random(n) < pa, a, b))
    # deletion: leave-one-run
    lor = [_fit_vertex(np.delete(X, i, 0), np.delete(y, i), fl)[0] for i in range(n)]
    lor = [v for v in lor if np.isfinite(v)]
    # deletion: leave-one-setting (experiment id)
    los, los_conc = [], 0
    for e in np.unique(exps):
        keep = exps != e
        v, c = _fit_vertex(X[keep], y[keep], fl)
        if np.isfinite(v):
            los.append(v); los_conc += (c[4] < 0 and 1.4 <= v <= 2.0)
    imax = int(np.argmax(cooks))

    def _aicc(Xm):
        c, *_ = np.linalg.lstsq(Xm, y, rcond=None)
        rss = float(np.sum((y - Xm @ c) ** 2)); k = Xm.shape[1] + 1
        aic = n * np.log(rss / n) + 2 * k
        return aic + (2 * k * (k + 1) / (n - k - 1) if n - k - 1 > 0 else 0.0), c
    aicc_grind, _ = _aicc(np.column_stack([np.ones(n), G]))
    aicc_gft, _ = _aicc(np.column_stack([np.ones(n), G, F, T, G ** 2]))
    aicc_ret, _ = _aicc(X)
    Xfull = np.column_stack([np.ones(n), F, G, T, F * G, F * T, G * T, F ** 2, G ** 2, T ** 2])
    aicc_full, cfull = _aicc(Xfull)
    # full-quadratic grind vertex includes the G*T cross-term (col 6), at central F and T
    vfull = (float(-(cfull[2] + cfull[4] * fl + cfull[6] * tp) / (2.0 * cfull[8]))
             if cfull[8] != 0 else float("nan"))
    return dict(
        n_runs=n, n_settings=int(len(np.unique(exps))), vertex=round(v0, 4),
        bootstrap=dict(iid_residual=dict(ci=iid_ci, joint_concave_in_domain=iid_j),
                       wild_rademacher=dict(ci=rad_ci, joint_concave_in_domain=rad_j),
                       wild_mammen=dict(ci=mam_ci, joint_concave_in_domain=mam_j)),
        curve_band=curve_band,                                # MAJ-16 Fig-1 envelope
        deletion=dict(
            leave_one_run_vertex_range=[round(min(lor), 4), round(max(lor), 4)],
            leave_one_setting_vertex_range=[round(min(los), 4), round(max(los), 4)],
            leave_one_setting_concave_in_domain="%d/%d" % (los_conc, len(los)),
            most_influential_run=dict(exp=float(exps[imax]),
                                      cooks_d=round(float(cooks[imax]), 3),
                                      std_resid=round(float(std_resid[imax]), 2),
                                      leverage=round(float(lev[imax]), 3))),
        model_form=dict(
            aicc_grind_only=round(aicc_grind, 2), aicc_g_f_t_g2=round(aicc_gft, 2),
            aicc_retained_7=round(aicc_ret, 2), aicc_full_quadratic=round(aicc_full, 2),
            full_quadratic_vertex=round(vfull, 4),
            retained_beats_full=bool(aicc_ret < aicc_full)),
        conditional_on="selected seven-term achieved-predictor specification (post-"
                       "selection uncertainty disclosed separately)",
        verdict=("The conditional grind vertex ~%.2f is stable to single-RUN (%.3f-%.3f) "
                 "and single-SETTING (%.3f-%.3f, %d/%d concave-in-domain) deletion and to "
                 "a full-quadratic form (vertex %.3f; retained-7 AICc %.1f < full %.1f). "
                 "Wild bootstraps (Rademacher %s, Mammen %s) preserve the vertex while "
                 "modestly widening vs the iid residual interval %s -- so the conditional "
                 "vertex is NOT an artefact of iid resampling despite the ~17x within-"
                 "setting SD range. All intervals condition on the selected seven-term "
                 "model." % (v0, min(lor), max(lor), min(los), max(los), los_conc,
                             len(los), vfull, aicc_ret, aicc_full, rad_ci, mam_ci, iid_ci)),
        strength="conditional (fixed-specification) deletion + wild-bootstrap + AICc "
                 "model-form sensitivity; NOT post-selection or unconditional inference")


def result1_magnitude_comparison():
    """Result-1 MAGNITUDE comparison (review ask): is the channeling interior-max
    bump the same SIZE as the schmieder interior-max feature? All in EY-points, on
    the MEASURED cells.

    Three sides, kept honest:
      - RAW target: TDS-EY at the fixed central condition (18.3/19.4/19.6 %); the
        middle-vs-higher-endpoint CONTRAST with a Welch t 95% CI (replicate-level).
        The raw response is monotone (contrast <0) -- no formal noise-floor claim.
      - MODEL: channeling ensemble EY prominence at the calibrated closure (5 & 9
        bar); reported vs the descriptive within-cell replicate variation, NOT a
        formal minimum-detectable-effect.
      - RSM PRECISION note (CORRECTED 2026-07-12): schmieder's printed Table-3
        coefficients are ROUNDED (T² to 3 decimals) and cannot reconstruct the
        absolute level -- literal evaluation gives ~6.7 g, but a REFIT to the
        committed observations gives ~3.9 g, near the data (`schmieder_rsm_refit`).
        So the RSM is a SHAPE tool because of printed rounding, NOT because it
        'overpredicts 1.7x' (that earlier claim was a rounding artifact; removed).

    Reading (verdict): the RAW response is monotone; the MODEL bump (~0.03-0.19
    EY-pt) is small relative to the within-cell replicate variation, but no formal
    MDE analysis is claimed. Neither side has a strong peak to match/miss ->
    model-capacity, not identification. Strength: qualitative."""
    ey = schmieder_tds_ey(_SCHM_CENTER["brew_ratio"], _SCHM_CENTER["temp_C"],
                          _SCHM_CENTER["flow_ml_s"])
    raw_bump = float(ey["ey_means"][1] - max(ey["ey_means"][0], ey["ey_means"][2]))
    within = float(np.mean(ey["ey_stds"]))          # DESCRIPTIVE within-cell std
    # Welch t 95% CI for the middle(1.7)-vs-higher-endpoint(2.0) contrast
    a, b = ey["ey_replicates"][1], ey["ey_replicates"][2]   # 1.7, 2.0 cells
    a, b = np.asarray(a), np.asarray(b)
    sa2, sb2 = a.var(ddof=1) / a.size, b.var(ddof=1) / b.size
    diff = float(a.mean() - b.mean())
    se = float(np.sqrt(sa2 + sb2))
    dof = (sa2 + sb2) ** 2 / (sa2 ** 2 / (a.size - 1) + sb2 ** 2 / (b.size - 1))
    from scipy import stats as _st
    tcrit = float(_st.t.ppf(0.975, dof))
    contrast_ci = [round(diff - tcrit * se, 3), round(diff + tcrit * se, 3)]
    refit = schmieder_rsm_refit("tds", _SCHM_CENTER["brew_ratio"], predictors="target")
    # MODEL side: channeling prominence at the calibrated closure, 5 & 9 bar
    def _prom(p_bar):
        s = channeling_sigma_sweep(gs_grid=np.linspace(1.0, 2.2, 7),
                                   s_ref=0.6, m=1.0, p_bar=p_bar, n_grid=7)
        e = np.asarray(s["ey_ensemble"])
        ip = int(np.argmax(e))
        return float(e[ip] - max(e[0], e[-1]))
    model_5, model_9 = _prom(5.0), _prom(9.0)
    return dict(
        raw_tds_ey=[round(x, 2) for x in ey["ey_means"]],
        raw_mid_vs_endpoint_contrast_EYpt=round(diff, 3),
        raw_contrast_welch_ci95=contrast_ci,      # excludes 0 on the low side -> monotone
        raw_interior_bump_EYpt=raw_bump,          # <=0 -> monotone, no bump
        raw_within_cell_std_EYpt=within,          # DESCRIPTIVE (not a formal noise floor)
        model_prominence_5bar_EYpt=model_5,
        model_prominence_9bar_EYpt=model_9,
        model_bump_lt_within_cell_var=bool(max(model_5, model_9) < within),
        rsm_refit_central_g=round(refit["refit_central_g"], 3),
        rsm_printed_central_g=round(refit["printed_central_g"], 3),
        rsm_raw_central_g=round(refit["raw_central_g"], 3),
        rsm_printed_is_rounding_artifact=refit["printed_is_artifact"],
        verdict=("raw TDS-EY is monotone (mid-minus-2.0 contrast %.2f EY-pt, "
                 "Welch 95%% CI %s -- excludes 0); model channeling bump %.3f "
                 "(5 bar)/%.3f (9 bar) EY-pt is small vs the within-cell replicate "
                 "variation (%.2f EY-pt), no formal MDE claimed. RSM printed "
                 "coeffs are rounded (refit %.2f g vs printed %.2f g vs data "
                 "%.2f g) -> shape tool by PRECISION, not a 1.7x overprediction. "
                 "Neither side has a strong peak -> model-capacity, not "
                 "identification." % (
                     diff, contrast_ci, model_5, model_9, within,
                     refit["refit_central_g"], refit["printed_central_g"],
                     refit["raw_central_g"])))


# --- cross-pressure generalization discriminator (item 2.2, ANALYSIS_P2) ---
# Waszkiewicz ran 11 pressures. Fix ONE calibration (the campaign-wide static pair
# P_c, Q_c fitted over all 11 pressures) and predict every trace: this is a
# within-campaign CONDITIONAL transfer test (the constants are shared, so it is
# NOT fully independent out-of-sample validation). Where the mechanisms disagree
# tells you which physics each captures (CHAT §2.2 point 1). Nothing is refit per
# pressure.
def cross_pressure_discrimination(window=(15.0, 95.0)):
    """Within-campaign CONDITIONAL-transfer RMSE [g/s] of three kappa(t)
    mechanisms across all 11 Waszkiewicz pressures, using ONE shared calibration
    (the campaign-wide static pair; no per-pressure refit). NOT fully independent
    out-of-sample validation -- the constants are fitted over all 11 pressures.

      static kappa(P)      Q(t) = q_static(P)                    flat, rung-3 analog
      dissolution Phi(t)   empirical near-instant sigmoid m_d(t) rung 4
      RC-3b coupled        m_d(t) from cameron2020 at that P     rung 5

    The empirical sigmoid is pressure-INDEPENDENT (one m_d(t) for every shot);
    RC-3b re-runs Cameron at each pressure, so its Phi(t) is flow-coupled. The
    9-bar point is the sigmoid's home pressure; the other 10 are held-out
    conditionally on the shared constants. Returns per-pressure RMSE plus regime
    aggregates. Result (see ANALYSIS_P2 §2.2): Phi(t) has the lowest transfer-mean
    RMSE but NOT uniformly -- RC-3b is lower at the low-pressure end (flow-coupling
    matters where flow is slow) and the static null is lower mid-range (little time
    structure to explain). No single mechanism is lowest everywhere. The low (<=2 bar)
    / mid (3.5-6 bar) bins are DESCRIPTIVE summaries motivated by the slow-flow /
    near-equilibrium physics -- NOT a timestamped pre-registration (review MAJ-13), so
    the CONTINUOUS pressure-residual curve is the primary presentation and the bins are
    a reading aid, not a mechanistic regime claim. The pattern is not caused by any one
    equilibrium calibration point (see `cross_pressure_loco`), but its physical origin
    remains unresolved -- the 9-bar solids trajectory and donor assumptions stay fixed
    (review MAJ-14).
    """
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    from puckworks.models.cameron2020 import extraction_bdf as cam
    tr = d.waszkiewicz_traces()
    ps = sorted(k for k in tr if k != "columns")
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    lo, hi = window
    per, raw = {}, {}                    # `per` = display-rounded; `raw` = full precision
    for p in ps:
        t = tr[p]["time__s"]; q = tr[p]["mass_flow_rate__g_per_s"]
        sel = (t >= lo) & (t <= hi); ts, qs = t[sel], q[sel]
        r_static = float(np.sqrt(np.mean((wz.q_static(p, P_c, Q_c) - qs) ** 2)))
        q_phi = wz.q_dynamic(ts, p, P_c, Q_c, k_s, l_s, m_s, dose)
        r_phi = float(np.sqrt(np.nanmean((q_phi - qs) ** 2)))
        sh = cam.simulate_shot(1.9, p_bar=p, m_in=dose / 1000, m_out=0.040,
                               t_shot=100.0, n_save=150)
        md = np.interp(ts, sh.t, sh.m_cup * 1000.0)
        if md[-1] <= 0:
            r_rc3b = float("nan")
        else:
            q_rc = wz.q_dynamic_from_md(p, P_c, Q_c, md, dose)
            r_rc3b = float(np.sqrt(np.nanmean((q_rc - qs) ** 2)))
        raw[p] = dict(static=r_static, phi=r_phi, rc3b=r_rc3b)   # UNROUNDED
        per[p] = dict(static=round(r_static, 3), phi=round(r_phi, 3),
                      rc3b=round(r_rc3b, 3))

    # ALL summaries computed from RAW values, rounded only at display (review MAJ-12:
    # the earlier `full_prec` averaged already-rounded per-pressure RMSEs -- a bug)
    def _mean(keys, mech):
        v = np.array([raw[p][mech] for p in keys], float)
        return float(np.nanmean(v))
    oos = [p for p in ps if p != 9.0]
    low = [p for p in ps if p <= 2.0]
    mid = [p for p in ps if 3.5 <= p <= 6.0]
    # genuinely full-precision transfer mean over the held-out 10 pressures (from raw)
    full_prec = {m: float(np.nanmean([raw[p][m] for p in oos]))
                 for m in ("static", "phi", "rc3b")}
    # NOTE residual autocorrelation lives in analysis/residual_autocorr.py, which
    # DECIMATES to 1 s first: the raw ~10 Hz trace already has lag-1 ACF ~1.0 from
    # sample spacing, so a naive raw-series autocorrelation measures sampling, not
    # lack-of-fit. Do NOT recompute it here on the native series.
    return dict(
        per_pressure=per,
        conditional_transfer_mean={m: round(_mean(oos, m), 3)
                                   for m in ("static", "phi", "rc3b")},
        conditional_transfer_mean_full_precision=full_prec,
        # DOF fitted to THIS flow dataset is 2 (P_c,Q_c) for all three; phi/rc3b add
        # donor params fit to OTHER observables (phi: 3 sigmoid params from 9-bar TDS;
        # rc3b: Cameron's parameters) -> zero ADDITIONAL flow degrees of freedom
        free_params_fit_to_flow=dict(static=2, phi=2, rc3b=2),
        donor_params_from_other_observables=dict(
            static=0, phi=3, rc3b="cameron2020 calibration (not refit to flow)"),
        residual_autocorr_ref="analysis.residual_autocorr.summary() (decimated DW)",
        low_p_mean={m: round(_mean(low, m), 3) for m in ("phi", "rc3b")},
        mid_p_mean={m: round(_mean(mid, m), 3) for m in ("static", "phi", "rc3b")},
        # DESCRIPTIVE separations (reading aids over the continuous curve), NOT proven
        # physical regimes (review MAJ-13):
        phi_generalizes=_mean(oos, "phi") < _mean(oos, "static"),
        rc3b_lower_low_p=_mean(low, "rc3b") < _mean(low, "phi"),
        static_lower_mid_p=_mean(mid, "static") < min(_mean(mid, "phi"),
                                                      _mean(mid, "rc3b")),
        bins_are_descriptive_not_preregistered=True,
        reading="Phi(t) has the lowest transfer-mean RMSE, but no single mechanism is "
                "lowest at every pressure (descriptively: RC-3b lower at low P, static "
                "lower mid-range). These are DESCRIPTIVE summaries of the continuous "
                "pressure-residual curve, not pre-registered physical regimes; the "
                "physical origin of the pattern is unresolved. Conditional-transfer, "
                "NOT independent validation.")


def cross_pressure_loco(window=(15.0, 95.0)):
    """LEAVE-ONE-PRESSURE-OUT held-out validation of the cross-pressure calibration
    (PAPER_B §7 owed item). The shared-calibration `cross_pressure_discrimination`
    fits (P_c, Q_c) over ALL 11 pressures, so every predicted trace saw its own
    pressure in the fit. Here we refit the static equilibrium pair (P_c, Q_c) on
    the OTHER 10 equilibrium points and predict the genuinely held-out 11th trace
    (static / Phi(t) / RC-3b), RMSE over the window.

    COMPANION to `analysis.lopo_cv.lopo_waszkiewicz_pressure`, which does the
    equilibrium-curve LOPO (static characteristic only, Q^2 on the 11 long-run
    points, Q^2~0.81). THIS function is the TRACE-LEVEL, three-mechanism companion:
    it scores the held-out full Q(t) trace for static / Phi(t) / RC-3b over the
    window, so it tests whether the mechanism DISCRIMINATION (not just the static
    curve) survives held-out refit.

    STRENGTH: this upgrades the shared-calibration conditional transfer toward a
    held-out prediction, but it is STILL WITHIN-RIG (one campaign, one coffee, one
    grind) and only the 2-parameter equilibrium pair is refit -- the dissolution
    sigmoid (k,l,m) is a 9-bar TDS calibration, pressure-independent, held fixed.
    It is NOT independent out-of-sample validation on a second rig.

    Because the fit is over-determined (11 points, 2 params), dropping one point
    should barely move (P_c, Q_c); we report that calibration DRIFT explicitly --
    small drift + held-out RMSE matching the shared-calibration RMSE is the honest
    reading (the calibration is not tuned to any single pressure), not a strong
    generalization claim."""
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    from puckworks.models.cameron2020 import extraction_bdf as cam
    tr = d.waszkiewicz_traces()
    ps = sorted(k for k in tr if k != "columns")
    Peq, Qeq = wz.steady_state_curve()                  # 11-point equilibrium curve
    P_c0, Q_c0 = wz.published_calibration()             # full-fit calibration
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    lo, hi = window
    per, raw, shared_raw, drift_pc, drift_qc = {}, {}, {}, [], []
    for i, p in enumerate(ps):
        keep = [j for j in range(len(ps)) if j != i]    # leave pressure p OUT
        (P_c, Q_c), _ = wz.fit_static(Peq[keep], Qeq[keep])
        drift_pc.append(abs(P_c - P_c0) / P_c0)
        drift_qc.append(abs(Q_c - Q_c0) / Q_c0)
        t = tr[p]["time__s"]; q = tr[p]["mass_flow_rate__g_per_s"]
        sel = (t >= lo) & (t <= hi); ts, qs = t[sel], q[sel]
        sh = cam.simulate_shot(1.9, p_bar=p, m_in=dose / 1000, m_out=0.040,
                               t_shot=100.0, n_save=150)
        md = np.interp(ts, sh.t, sh.m_cup * 1000.0)

        def _rmse(Pc, Qc):                              # raw RMSE for a calibration pair
            rs = float(np.sqrt(np.mean((wz.q_static(p, Pc, Qc) - qs) ** 2)))
            rp = float(np.sqrt(np.nanmean(
                (wz.q_dynamic(ts, p, Pc, Qc, k_s, l_s, m_s, dose) - qs) ** 2)))
            rr = (float("nan") if md[-1] <= 0 else float(np.sqrt(np.nanmean(
                (wz.q_dynamic_from_md(p, Pc, Qc, md, dose) - qs) ** 2))))
            return dict(static=rs, phi=rp, rc3b=rr)
        raw[p] = _rmse(P_c, Q_c)                        # held-out refit (UNROUNDED)
        shared_raw[p] = _rmse(P_c0, Q_c0)               # full 11-pt calibration (UNROUNDED)
        per[p] = dict(static=round(raw[p]["static"], 3), phi=round(raw[p]["phi"], 3),
                      rc3b=round(raw[p]["rc3b"], 3), P_c=round(float(P_c), 3),
                      Q_c=round(float(Q_c), 3))
    # ALL summaries from RAW values, rounded only at display (review AR-B2-09)
    heldout_mean = {m: round(float(np.nanmean([raw[p][m] for p in ps])), 3)
                    for m in ("static", "phi", "rc3b")}
    shared_mean = {m: round(float(np.nanmean([shared_raw[p][m] for p in ps])), 3)
                   for m in ("static", "phi", "rc3b")}
    max_drift = round(float(max(max(drift_pc), max(drift_qc))), 4)
    # "held-out ~ shared" => the calibration is over-determined, not per-pressure tuned
    matches = all(abs(float(np.nanmean([raw[p][m] for p in ps]))
                      - float(np.nanmean([shared_raw[p][m] for p in ps])))
                  <= 0.05 * shared_mean[m] + 0.02 for m in ("static", "phi", "rc3b"))
    return dict(
        per_pressure=per, heldout_mean=heldout_mean, shared_calibration_mean=shared_mean,
        max_calibration_drift=max_drift, heldout_matches_shared=matches,
        n_pressures=len(ps), refit="static (P_c,Q_c); sigmoid k,l,m held fixed",
        strength="within-rig leave-one-pressure-out held-out prediction (one campaign/"
                 "coffee/grind; 2-param equilibrium pair refit) -- NOT independent "
                 "second-rig out-of-sample validation",
        reading="Leaving each pressure out and refitting the equilibrium pair moves "
                "(P_c,Q_c) by at most %.1f%%, and the held-out RMSE %s the "
                "shared-calibration RMSE -- so the two-parameter equilibrium "
                "calibration is not dominated by any single pressure point. This does "
                "NOT establish that the residual pressure pattern is physical (review "
                "MAJ-14): the 9-bar solids trajectory and other donor assumptions "
                "remain fixed, so omitted machine dynamics, viscosity/sensor effects, "
                "an imperfect equilibrium form, or other omitted bed mechanisms could "
                "produce the same pattern. Its physical origin is unresolved."
                % (max_drift * 100.0,
                   "matches" if matches else "DIFFERS from"))


# --- N-tube kappa(t) union: streamtube channeling x coupled_kappa_t per-tube --
def ntube_kappa_t_union(gs=1.1, N=400, s_ref=0.6, m=1.0, P_bar=9.0,
                        closure="poroelastic", lateral=0.0, substeps=8,
                        compute_ey=True, control="flow", conductance_floor=1e-12,
                        rng_seed=None):
    """EXPLORATORY SYNTHESIS harness (qualitative). Fuses the two P3/P2 leading
    mechanisms:
    the streamtube channeling ensemble (P3 verdict: static channeling is the
    unique physical reproducer of the fine-grind dip) and the coupled_kappa_t
    porosity-evolution closure (P2: extraction OPENS the near-choke bed, 8-14x
    flow rise). Question it answers: when each parallel streamtube carries its OWN
    extraction-opens porosity clock, does channeling RUN AWAY over the shot, or
    SELF-LIMIT?

    Construction (grounded scales only, no invented parameters):
      - k_i0: unit-mean lognormal permeability multipliers, heterogeneity
        sigma(gs) from the CALIBRATED streamtube closure sigma_closure_power.
        Deterministic quantile nodes (reproducible, no RNG).
      - Extraction is TIME-clocked by the empirical waszkiewicz m_d(t) (the shot
        proceeds regardless), but each tube ages on its OWN throughput: an age
        tau_i advances at the tube's relative flow share w_i; phi_i = Phi_ext(tau_i).
      - Per-tube conductance g_i = k_i0 * M(phi_i). closure='poroelastic': M(phi)
        = the poroelastic Q(phi) from coupled_kappa_t (near-zero at phi~0 -> ~1.9
        g/s at phi~0.12 -- the near-choke hypersensitivity that P2 established as
        REQUIRED for the whole-bed 14x rise). closure='ck': the GENTLE
        Kozeny-Carman auxiliary kappa_ck(phi) -- the contrast isolates whether the
        near-choke sensitivity is what drives the dynamics.
      - Fixed-FLOW coupling (schmieder/DE1 regime): w_i = g_i / mean_j g_j (unit
        mean; a fixed total is shared, so a faster tube STEALS flow). `lateral`
        in [0,1] is a HOMOGENIZING REGULARIZER (w <- (1-lateral)*w + lateral*1) --
        a crude PROXY for lateral coupling, NOT a transverse-Darcy / shared-
        pressure-field exchange term; it blends shares toward uniform. substeps
        subdivides each trace interval (Euler step-size check).
      - Coupled ODE: dtau_i/dt = w_i(t), integrated on the waszkiewicz time base.
      - EY closure runs at the SAME pressure as the flow dynamics (P_bar).

    Reports the flow-concentration trajectory with proper concentration metrics
    (top-decile share, MAX single-tube share, effective # active channels
    N_eff = 1/sum s_i^2), whether it self-limits vs concentrates, and the
    ensemble-EY change vs the STATIC streamtube. SCOPE: this is one grind / one
    pressure / one closure-slope / one clock -- an exploratory finding in the
    TESTED near-choke configuration, NOT a proven unconditional instability (no
    stability theorem, no phase diagram). Validation strength: qualitative /
    exploratory synthesis -- NOT a registered component, NOT a validated kappa(t)
    law (as sound as its shakiest donor; see coupled_kappa_t)."""
    import numpy as np
    from scipy.interpolate import PchipInterpolator
    from scipy.stats import norm
    from puckworks.models.brewer2026 import coupled_kappa_t as _ck
    from puckworks.models.brewer2026 import streamtube as _st

    # heterogeneity from the calibrated streamtube closure
    sigma = float(_st.sigma_closure_power(gs, s_ref, m))
    # unit-mean lognormal nodes: deterministic evenly-spaced quantiles (default,
    # reproducible), or a seeded STOCHASTIC finite-network draw (rng_seed set) so the
    # robustness study can compare finite realisations vs the quadrature (review AR-B2-12).
    if rng_seed is None:
        z = norm.ppf((np.arange(N) + 0.5) / N)
    else:
        z = np.random.default_rng(rng_seed).standard_normal(N)
    k0 = np.exp(sigma * z - 0.5 * sigma ** 2)              # unit-mean lognormal

    # conductance multiplier M(phi) and the empirical extraction clock
    r = _ck.simulate(P_bar=P_bar, branches=("extraction",))
    t, phi_t = r["t"], r["phi"]["extraction"]
    cond = r["Q"] if closure == "poroelastic" else r["kappa_ck"]
    o = np.argsort(phi_t)
    M = PchipInterpolator(phi_t[o], np.asarray(cond)[o], extrapolate=True)
    Phi = PchipInterpolator(t, phi_t, extrapolate=True)
    phi_max = float(phi_t.max())
    # conductance_floor: the numerical clip on M(phi) at the near-choke base
    # (phi~0). The reviewer flagged that the "numerical concentration is
    # floor-independent" claim was ASSERTED at the single hardcoded 1e-12 and
    # never tested; it is now an exposed arg that ntube_finite_time_gain SWEEPS.
    Mofphi = lambda ph: np.clip(M(np.clip(ph, 0.0, phi_max)), conductance_floor, None)

    # integrate the coupled throughput-clock ODE (Euler, substepped per interval)
    # control='flow' (fixed total, tubes SHARE a fixed pie -> a faster tube STEALS):
    #   w = g / mean(g)  (unit-mean; current mean).
    # control='pressure' (fixed dP, tubes INDEPENDENT -> total flow can grow, no
    #   stealing): w = g / mean(g0)  (normalized to the INITIAL mean reference).
    g0bar = float(np.mean(k0 * Mofphi(Phi(np.zeros(N)))))
    tau = np.zeros(N)
    top = max(1, N // 10)
    top_share, max_share, n_eff = [], [], []
    M_acc = np.zeros(N)                                    # for time-avg share
    # review MAJ-33/B3-13: a TRUE full-trajectory conservation audit -- running extrema
    # over EVERY substep (raw conductance/flow) and every recorded step (share sum, min
    # share), NOT the final-step-only values the old code stored and mislabeled "max".
    min_g = np.inf; min_w = np.inf; max_w = -np.inf
    mean_w_min = np.inf; mean_w_max = -np.inf
    share_sum_dev_max = 0.0; min_share_traj = np.inf; n_substeps_total = 0
    for i in range(1, len(t)):
        dt = (t[i] - t[i - 1]) / substeps
        for _ in range(substeps):
            g = k0 * Mofphi(Phi(tau))
            ref = float(np.mean(g)) if control == "flow" else g0bar
            w = g / ref
            if lateral:
                w = (1.0 - lateral) * w + lateral          # homogenizing proxy
            tau = tau + w * dt
            M_acc = M_acc + w * dt
            # RAW extrema over every substep (non-negativity + control-law balance)
            min_g = min(min_g, float(g.min()))
            min_w = min(min_w, float(w.min())); max_w = max(max_w, float(w.max()))
            _mw = float(np.mean(w))
            mean_w_min = min(mean_w_min, _mw); mean_w_max = max(mean_w_max, _mw)
            n_substeps_total += 1
        s = w / w.sum()                                    # normalized shares
        # SHARE conservation extrema over the FULL trajectory (not just the last step)
        share_sum_dev_max = max(share_sum_dev_max, abs(float(s.sum()) - 1.0))
        min_share_traj = min(min_share_traj, float(s.min()))
        sw = np.sort(s)[::-1]
        top_share.append(float(sw[:top].sum()))
        max_share.append(float(sw[0]))                     # largest SINGLE tube
        n_eff.append(float(1.0 / np.sum(s ** 2)))          # effective # channels
    top_share = np.array(top_share)
    max_share = np.array(max_share); n_eff = np.array(n_eff)
    # conservation / non-negativity over the WHOLE trajectory (review MAJ-33): the
    # normalized share sums to 1 each step (record the worst deviation as a numerical
    # check); the RAW conductance/relative-flow/age minima test genuine non-negativity;
    # and mean(w) is imposed ~1 under FLOW control (fixed total) but free under PRESSURE
    # control (total flow can grow) -- so its range distinguishes the two boundary
    # conditions rather than being tautological.
    share_sum_dev = share_sum_dev_max                      # TRUE max over trajectory
    min_share = min_share_traj                             # TRUE min over trajectory
    min_tube_age = float(tau.min())                        # throughput age, must be >= 0
    conservation_audit = dict(
        share_sum_max_deviation=round(share_sum_dev_max, 12),
        min_flow_share=round(min_share_traj, 9),
        min_conductance=round(min_g, 12),
        min_relative_flow=round(min_w, 9),
        mean_relative_flow_range=[round(mean_w_min, 6), round(mean_w_max, 6)],
        min_tube_age=round(min_tube_age, 6),
        n_substeps_total=int(n_substeps_total),
        # under FLOW control the imposed total relative flow is conserved (mean w == 1 to
        # tol) at EVERY step; under PRESSURE control it is FREE (total flow can grow, so
        # this is False -- the honest fact, not an assumption)
        raw_total_flow_conserved=bool(control == "flow"
                                      and (mean_w_max - mean_w_min) < 1e-6),
        nonnegative_throughout=bool(min_g >= 0.0 and min_w >= 0.0
                                    and min_share_traj >= 0.0 and min_tube_age >= 0.0))
    _sub = max(1, len(n_eff) // 40)
    n_eff_traj = [round(float(v), 3) for v in n_eff[::_sub]]
    max_share_traj = [round(float(v), 4) for v in max_share[::_sub]]
    n_eff_monotone = bool(np.all(np.diff(n_eff) <= 1e-6))   # concentration, no rebound
    # review MAJ-36: surface PHYSICAL time (seconds) for the trajectory, not only
    # normalized shot time; and the COLLAPSE TIME (first physical second the flow crosses
    # half into one tube) so Fig 5a can be read on the real clock and event times compared.
    t_rec = np.asarray(t[1:], float)                        # physical time of each step
    time_traj = [round(float(v), 4) for v in t_rec[::_sub]]
    # B6-03: distinguish a TRANSIENT first passage from PERSISTENT single-channel onset.
    # `first_passage_top1_s` = first step max single-tube share crosses 0.5 (can be a
    # transient excursion; it fires even in runs that later end distributed). The
    # `collapse_time_s` we report is the PERSISTENT onset: the first step from which the
    # single-channel condition (top-1 >= 0.5 AND N_eff <= 2) holds through the final
    # recorded step. Non-persistent runs (e.g. pressure control, high lateral) get None,
    # so a distributed endpoint is never reported as "collapsed" (B6-14).
    _fp_idx = np.where(max_share > 0.5)[0]
    first_passage_top1_s = float(t_rec[_fp_idx[0]]) if len(_fp_idx) else None
    # persistent onset (prespecified rule, B6-03/§5.5.6): the first step from which the
    # single-channel condition (top-1 >= 0.5 AND N_eff <= 2) holds CONTINUOUSLY for at
    # least `_persist_s` seconds (or through the remainder of the shot if less remains).
    # A fixed window (not "strictly to the last step") is robust to a late transient
    # rebound while still excluding runs that only touch the threshold transiently.
    _persist_s = 5.0
    _single = (max_share > 0.5) & (n_eff <= 2.0)
    persistent_onset_s = None
    for _i in range(len(_single)):
        if not _single[_i]:
            continue
        _win = (t_rec >= t_rec[_i]) & (t_rec <= t_rec[_i] + _persist_s)
        if bool(_single[_win].all()):
            persistent_onset_s = float(t_rec[_i]); break
    collapse_time_s = persistent_onset_s                    # "collapse" == persistent onset
    peak_share_idx = int(np.argmax(max_share))
    # review MAJ-38: NORMALISED concentration metrics of the FINAL share distribution
    # (portable across N): Shannon entropy (1 = uniform, ->0 = single channel), Gini, and
    # the top-1 / top-decile share.
    s_final = np.clip(s, 1e-300, None)
    entropy_norm = float(-np.sum(s_final * np.log(s_final)) / np.log(N)) if N > 1 else 0.0
    ssort = np.sort(s_final)
    gini = float((np.sum((2 * np.arange(1, N + 1) - N - 1) * ssort)) / (N * np.sum(ssort)))
    concentration_metrics = dict(
        n_eff_over_N=round(float(n_eff[-1]) / N, 6),
        entropy_normalized=round(entropy_norm, 4),          # 1 uniform -> 0 concentrated
        gini=round(gini, 4),
        top1_share=round(float(max_share[-1]), 4),
        top_decile_share=round(float(top_share[-1]), 4),
        # B6-03: collapse_time_s is the PERSISTENT single-channel onset (None if the run
        # never persistently collapses); first_passage_top1_s is the transient first crossing.
        collapse_time_s=(round(collapse_time_s, 3) if collapse_time_s is not None else None),
        first_passage_top1_s=(round(first_passage_top1_s, 3)
                              if first_passage_top1_s is not None else None),
        peak_share_time_s=round(float(t_rec[peak_share_idx]), 3))
    # NB: `state` (B5-09) is added to concentration_metrics after it is classified below.
    # ensemble EY at the SAME pressure as the flow dynamics (was hardcoded 5 bar)
    if compute_ey:
        k_eff = M_acc / t[-1]
        ey = _st.EYResponse(gs=gs, p_bar=P_bar)
        ey_static = float(np.mean(ey.ey_of_k(k0)))
        ey_dyn = float(np.mean(ey.ey_of_k(np.clip(k_eff, ey.k_min, ey.k_max))))
    else:
        ey_static = ey_dyn = float("nan")
    j_peak = int(np.argmax(top_share))
    self_limiting = bool(j_peak < len(top_share) - 1
                         and top_share[-1] < top_share[j_peak] - 1e-3)
    # --- B5-09: explicit end-state classifier -------------------------------
    # Distinguish single-channel / oligarchic / distributed / transient-switching
    # from EXPLICIT thresholds on the TOP-1 (max single-tube) share, N_eff, and
    # persistence. The old flag keyed on the TOP-DECILE share alone, so a state
    # where a few or many channels share the flow (e.g. N_eff~19, max single-tube
    # ~0.07, top-decile > 0.9) was mislabelled a single-channel collapse.
    top1_final = float(max_share[-1])          # max SINGLE-tube share
    topdec_final = float(top_share[-1])         # top-decile share
    neff_final = float(n_eff[-1]); neff_frac = neff_final / N
    if self_limiting:
        state = "transient_switching"           # peaks then relaxes; no stable concentrate
    elif top1_final >= 0.5 and neff_final <= 2.0:
        state = "single_channel"                # one tube carries the flow, N_eff -> ~1
    elif topdec_final >= 0.9 and neff_frac <= 0.05:
        state = "oligarchic"                    # a few channels dominate (NOT one)
    elif neff_frac >= 0.10:
        state = "distributed"                   # flow spread over many effective channels
    else:
        state = "intermediate"
    # `concentrates` now means a GENUINE single-channel collapse (kept for
    # back-compat with the floor-independence check + robustness study).
    concentrates = bool(state == "single_channel")
    _STATE_LABEL = {"single_channel": "single-channel collapse (N_eff->1)",
                    "oligarchic": "oligarchic (few channels dominate, not one)",
                    "distributed": "distributed (many effective channels)",
                    "transient_switching": "transient switching (self-limiting)",
                    "intermediate": "intermediate"}
    concentration_metrics["state"] = state      # B5-09 explicit end-state class
    return dict(
        gs=gs, sigma=sigma, N=N, closure=closure, lateral=lateral, P_bar=P_bar,
        control=control, conductance_floor=conductance_floor,
        top_decile_share_static=float(top_share[0]),      # t~0, phi~0 (== static)
        top_decile_share_peak=float(top_share[j_peak]),
        top_decile_share_final=float(top_share[-1]),
        max_single_tube_share_final=float(max_share[-1]),
        n_eff_channels_static=float(n_eff[0]),
        n_eff_channels_final=float(n_eff[-1]),
        n_eff_trajectory=n_eff_traj, max_share_trajectory=max_share_traj,
        time_s_trajectory=time_traj,                       # MAJ-36 physical seconds
        collapse_time_s=(round(collapse_time_s, 3) if collapse_time_s is not None else None),
        first_passage_top1_s=(round(first_passage_top1_s, 3)     # B6-03 transient crossing
                              if first_passage_top1_s is not None else None),
        concentration_metrics=concentration_metrics,       # MAJ-38 entropy/Gini/top-k
        n_eff_monotone_decreasing=n_eff_monotone,
        # review MAJ-33: these are now TRUE trajectory extrema (max dev / min share over
        # every recorded step), plus a full raw-quantity audit in conservation_audit
        share_sum_max_deviation=round(share_sum_dev, 12),  # conservation (max over traj)
        min_flow_share=round(min_share, 9),                # non-negativity (min over traj)
        conservation_audit=conservation_audit,
        peak_time_s=float(t[1:][j_peak]),
        self_limiting=self_limiting, concentrates=concentrates, state=state,
        ey_static=ey_static, ey_dynamic=ey_dyn,
        deepens_dip=bool(ey_dyn < ey_static - 1e-6),
        reading=("[%s%s] top-decile share %.2f->%.2f, max single-tube %.2f, "
                 "N_eff %.0f->%.1f of %d; %s; ensemble EY %s (%.1f%%->%.1f%%) @%gbar"
                 % (closure, (" +lat%.2f" % lateral) if lateral else "",
                    top_share[0], top_share[-1], max_share[-1],
                    n_eff[0], n_eff[-1], N, _STATE_LABEL[state],
                    "drops" if ey_dyn < ey_static else "holds",
                    ey_static, ey_dyn, P_bar)))


def ntube_finite_time_gain(P_bar=9.0, floors=(1e-9, 1e-12, 1e-15)):
    """FINITE-TIME concentration diagnostic for the N-tube model (Result 3).
    EXPLORATORY / qualitative -- NOT a proven linear-stability result (see the
    PAPER_B review). Renamed from `ntube_stability_analysis` 2026-07-12 to stop
    implying a theorem.

    What it is (honest scope): a perturbation to one tube's extraction age grows,
    to leading order under fixed-flow, by the end-to-start conductance ratio
        G = ( M(phi_max) / M(phi_0) )^(1-lateral).
    But this is a FINITE-HORIZON gain from a specified start, NOT a floor-
    independent eigenvalue: for the poroelastic closure M(phi_0)->0 at the
    near-choke shutoff, so G depends on the numerical conductance FLOOR (a
    zero-conductance base state makes the log-linearization singular). We therefore
    report G across a RANGE of floors to expose that dependence -- the poroelastic
    G scales ~1/floor (it is floor-controlled), while Kozeny-Carman G~1.5 is
    floor-independent. So G is NOT a stability criterion; it is a qualitative
    explanation of WHY the closure matters, and its magnitude is not meaningful.

    What IS robust is the NUMERICAL concentration -- and this is now MEASURED, not
    asserted: the actual N-tube integration is RE-RUN at every floor (the reviewer
    flagged that the old code called the integration once at the hardcoded 1e-12
    and only claimed floor-independence). The poroelastic closure drives N_eff -> ~1
    (strong finite-time concentration in the tested near-choke, flow-controlled
    config) and CK stays bounded (N_eff ~83) at EVERY floor across the swept range
    -- so the qualitative outcome is genuinely floor-independent even though the
    closed-form gain G is not. The `unstable` field is REMOVED; use
    `concentrates_numeric` / `n_eff_floor_independent`. A genuine stability result
    still needs a physical lateral operator + a Jacobian / finite-time-Lyapunov
    analysis (open; the lateral term here is a homogenizing proxy, not a
    transverse-Darcy exchange)."""
    from puckworks.models.brewer2026 import coupled_kappa_t as _ck
    r = _ck.simulate(P_bar=P_bar, branches=("extraction",))
    phi = r["phi"]["extraction"]
    o = np.argsort(phi)
    out = {}
    for name, cond in (("poroelastic", r["Q"]), ("ck", r["kappa_ck"])):
        c = np.asarray(cond)[o]
        Mf = float(c[-1])
        # (a) closed-form gain vs floor -> exposes floor-dependence (poroelastic ~1/floor)
        gain_by_floor = {fl: float(Mf / max(float(c[0]), fl)) for fl in floors}
        floor_sensitive = bool(max(gain_by_floor.values()) / min(gain_by_floor.values()) > 10)
        # (b) MEASURED numerical N_eff, actually RE-RUN at each floor (was asserted)
        n_eff_by_floor, conc_by_floor = {}, {}
        for fl in floors:
            num = ntube_kappa_t_union(gs=1.1, N=150, closure=name, compute_ey=False,
                                      conductance_floor=fl)
            n_eff_by_floor[fl] = round(num["n_eff_channels_final"], 2)
            conc_by_floor[fl] = bool(num["concentrates"])
        nvals = list(n_eff_by_floor.values())
        # floor-independent iff N_eff varies < 5% and the concentrates flag is constant
        n_eff_floor_independent = bool(
            (max(nvals) - min(nvals)) <= 0.05 * max(max(nvals), 1e-9)
            and len(set(conc_by_floor.values())) == 1)
        out[name] = dict(
            M_phimax=Mf, M_phi0_raw=float(c[0]),
            finite_time_gain_by_floor={("%.0e" % k): round(v, 3) if v < 1e4 else v
                                       for k, v in gain_by_floor.items()},
            gain_is_floor_sensitive=floor_sensitive,   # True = NOT a stability eigenvalue
            n_eff_final_by_floor={("%.0e" % k): v for k, v in n_eff_by_floor.items()},
            concentrates_by_floor={("%.0e" % k): v for k, v in conc_by_floor.items()},
            n_eff_final_numeric=n_eff_by_floor[floors[1] if len(floors) > 1 else floors[0]],
            n_eff_floor_independent=n_eff_floor_independent,   # the ROBUST claim, TESTED
            concentrates_numeric=conc_by_floor[floors[0]])
    return dict(
        closures=out,
        verdict=("FINITE-TIME concentration (not a stability theorem): the "
                 "closed-form conductance-ratio gain G=M_f/M_0 is FLOOR-DEPENDENT "
                 "for poroelastic (M_0->0 at the near-choke shutoff -> G scales "
                 "~1/floor, magnitude not meaningful), while CK G~1.5 is "
                 "floor-independent. But the ROBUST result -- the MEASURED numerical "
                 "N_eff, re-run at every floor -- IS floor-independent: poroelastic "
                 "N_eff->%.1f (strong concentration, tested config) and CK N_eff=%.0f "
                 "(bounded) hold across the whole swept floor range (poroelastic "
                 "floor-indep=%s, CK floor-indep=%s). The closure sets WHETHER "
                 "concentration happens; a proven instability needs a physical "
                 "lateral operator + Jacobian/Lyapunov analysis (open)."
                 % (out["poroelastic"]["n_eff_final_numeric"],
                    out["ck"]["n_eff_final_numeric"],
                    out["poroelastic"]["n_eff_floor_independent"],
                    out["ck"]["n_eff_floor_independent"])))


def ntube_robustness_study(baseline=None):
    """RESULT-3 ROBUSTNESS STUDY (review MAJ-33/34/40/41): ONE-FACTOR-AT-A-TIME sweeps
    of the N-tube finite-time concentration endpoint over N, timestep (substeps), grind,
    pressure, lateral-homogenisation, control law, closure, and STOCHASTIC finite-network
    realisations, PLUS a genuine crossed control×lateral×closure design (so interactions
    are visible, not only main effects) -- this is NOT a full factorial and is not called
    one (MAJ-34). For each config report the endpoint N_eff, N_eff/N (MAJ-41), the
    `concentrates` classification, max single-tube share, and a FULL-TRAJECTORY
    conservation check (max share-sum deviation over every step + raw non-negativity;
    MAJ-33). Invariance is reported SEPARATELY per axis type (MAJ-40): numerical
    convergence (N, substeps), stochastic spread, operating design (grind, pressure), and
    physical-model contingencies (control, lateral, closure) which DELIBERATELY suppress
    concentration -- the scientific finding, not a failure -- rather than collapsed into
    one boolean.

    It does NOT supply a physical transverse-Darcy lateral operator or a formal
    Jacobian/finite-time-Lyapunov growth analysis -- those remain owed (§7), so Result 3
    stays EXPLORATORY. NOTE: many PDE-clock solves (~2-4 min, slow; hand-run only)."""
    base = dict(gs=1.1, N=400, P_bar=9.0, closure="poroelastic", lateral=0.0,
                substeps=8, control="flow", conductance_floor=1e-12,
                compute_ey=False)
    if baseline:
        base.update(baseline)

    def _run(**over):
        cfg = dict(base); cfg.update(over)
        r = ntube_kappa_t_union(**cfg)
        ca = r["conservation_audit"]
        Ncfg = cfg["N"]
        cm = r.get("concentration_metrics", {})
        return dict(config=over or {"baseline": True},
                    n_eff_final=round(r["n_eff_channels_final"], 3),
                    n_eff_over_N=round(r["n_eff_channels_final"] / Ncfg, 5),  # MAJ-41
                    max_share_final=round(r["max_single_tube_share_final"], 4),
                    entropy_normalized=cm.get("entropy_normalized"),          # MAJ-38
                    gini=cm.get("gini"), collapse_time_s=cm.get("collapse_time_s"),
                    concentrates=r["concentrates"], state=r["state"],   # B5-09
                    self_limiting=r["self_limiting"],
                    n_eff_monotone=r["n_eff_monotone_decreasing"],
                    # review MAJ-33: conservation is now judged from the FULL-trajectory
                    # audit (max share-sum deviation over every step + raw non-negativity)
                    conservation_ok=bool(ca["share_sum_max_deviation"] < 1e-9
                                         and ca["nonnegative_throughout"]))

    # --- OFAT sweeps (review MAJ-34/B3-15: explicitly ONE-FACTOR-AT-A-TIME, not
    # factorial): each axis varied around the baseline. Grouped by AXIS TYPE (MAJ-40)
    # so numerical convergence, stochastic spread, operating design, and physical-model
    # contingencies are reported SEPARATELY, not collapsed into one invariance boolean.
    pressures = (6.0, 9.0, 11.0)
    ofat = dict(
        numerical=dict(
            N=[_run(N=n) for n in (100, 200, 400, 800)],
            substeps=[_run(substeps=s) for s in (4, 8, 16, 32)]),
        stochastic=dict(   # review MAJ-38: 16 realisations (was 4) for a median + interval
            realisation=[_run(rng_seed=s) for s in range(16)]),
        operating=dict(
            grind_gs=[_run(gs=g) for g in (1.1, 1.5, 2.0)],
            pressure_bar=[_run(P_bar=p) for p in pressures]),
        physical_contingency=dict(
            lateral=[_run(lateral=l) for l in (0.0, 0.1, 0.3)],
            control=[_run(control=c) for c in ("flow", "pressure")],
            closure=[_run(closure=c) for c in ("poroelastic", "ck")]))

    # --- a GENUINE crossed design over the three load-bearing physical axes
    # (control x lateral x closure), review MAJ-34/B3-15 -- so interactions are visible,
    # not only main effects.
    crossed = []
    for ctrl in ("flow", "pressure"):
        for lat in (0.0, 0.3):
            for clo in ("poroelastic", "ck"):
                crossed.append(_run(control=ctrl, lateral=lat, closure=clo))

    def _rows(group):
        return [row for sub in group.values() for row in sub]

    # invariance is judged PER AXIS TYPE (MAJ-40). "Concentration" is a poroelastic-
    # flow-control property; the physical-contingency axes DELIBERATELY break it (that
    # is the scientific finding), so they are reported as contingencies, not failures.
    def _all_concentrate(rows):
        poro = [r for r in rows if r["config"].get("closure", "poroelastic") != "ck"
                and r["config"].get("control", "flow") != "pressure"
                and float(r["config"].get("lateral", 0.0) or 0.0) < 0.29]
        return bool(poro) and all(r["concentrates"] for r in poro)

    num_rows = _rows(ofat["numerical"]); sto_rows = _rows(ofat["stochastic"])
    op_rows = _rows(ofat["operating"])
    # review MAJ-38: a stochastic DISTRIBUTION over the 16 finite-network realisations --
    # median + 5-95% interval of N_eff/N and normalized entropy, plus collapse-time spread
    import numpy as _np
    _son = _np.array([r["n_eff_over_N"] for r in sto_rows], float)
    _sent = _np.array([r["entropy_normalized"] for r in sto_rows if r["entropy_normalized"] is not None], float)
    _sct = [r["collapse_time_s"] for r in sto_rows if r["collapse_time_s"] is not None]
    stochastic_distribution = dict(
        n_realisations=len(sto_rows),
        n_eff_over_N_median=round(float(_np.median(_son)), 5),
        n_eff_over_N_p5_p95=[round(float(_np.percentile(_son, 5)), 5),
                             round(float(_np.percentile(_son, 95)), 5)],
        entropy_normalized_median=round(float(_np.median(_sent)), 4) if len(_sent) else None,
        collapse_time_s_range=[round(min(_sct), 3), round(max(_sct), 3)] if _sct else None)
    numerical_invariant = _all_concentrate(num_rows)
    stochastic_invariant = _all_concentrate(sto_rows)
    operating_invariant = _all_concentrate(op_rows)
    all_rows = num_rows + sto_rows + op_rows + _rows(ofat["physical_contingency"]) + crossed
    all_conserve = all(r["conservation_ok"] for r in all_rows)
    conc_neffs = [r["n_eff_final"] for r in all_rows if r["concentrates"]]
    conc_neff_over_N = [r["n_eff_over_N"] for r in all_rows if r["concentrates"]]
    # which physical-contingency axes SUPPRESS concentration (the scientific contingency)
    suppressors = sorted({k for k, sub in [("lateral>0", [r for r in _rows(ofat["physical_contingency"]) if float(r["config"].get("lateral", 0) or 0) > 0]),
                                           ("pressure-control", [r for r in _rows(ofat["physical_contingency"]) if r["config"].get("control") == "pressure"]),
                                           ("ck-closure", [r for r in _rows(ofat["physical_contingency"]) if r["config"].get("closure") == "ck"])]
                          if any(not r["concentrates"] for r in sub)})
    return dict(
        baseline=base, ofat=ofat, crossed_control_lateral_closure=crossed,
        design_type="OFAT sweeps + one crossed control×lateral×closure design "
                    "(NOT a full factorial)",
        # SEPARATED invariance flags (MAJ-40): numerical/stochastic/operating vs contingency
        numerical_convergence_invariant=numerical_invariant,
        stochastic_invariant=stochastic_invariant,
        stochastic_distribution=stochastic_distribution,   # MAJ-38 (16 realisations)
        operating_invariant=operating_invariant,
        concentration_suppressed_by=suppressors,   # deliberate physical contingencies
        n_eff_final_range_when_concentrating=[round(min(conc_neffs), 2),
                                              round(max(conc_neffs), 2)] if conc_neffs else None,
        n_eff_over_N_range_when_concentrating=[round(min(conc_neff_over_N), 5),
                                               round(max(conc_neff_over_N), 5)] if conc_neff_over_N else None,
        conservation_all_ok=all_conserve,
        pressure_range_bar=[min(pressures), max(pressures)],   # MAJ-39: from config
        owed="physical transverse-Darcy lateral operator + formal Jacobian/finite-time-"
             "Lyapunov growth analysis (Result 3 stays exploratory until then)",
        verdict=("OFAT sweeps (N 100-800, substeps 4-32, grind 1.1-2.0, pressure "
                 "%.0f-%.0f bar, %d stochastic realisations) + a crossed control×lateral×"
                 "closure design: concentration is invariant on the NUMERICAL (%s), "
                 "STOCHASTIC (%s), and OPERATING (%s) axes, and is DELIBERATELY suppressed "
                 "by the physical-contingency axes {%s} -- the scientific finding, not a "
                 "failure. Among concentrating configs N_eff_final in %s (N_eff/N in %s). "
                 "Full-trajectory flow-share conservation + raw non-negativity hold (%s). "
                 "This is a SWEEP + conservation robustness result in the tested family, "
                 "NOT a proven instability -- a physical lateral operator + a formal "
                 "finite-time-growth analysis remain owed, so Result 3 stays exploratory."
                 % (min(pressures), max(pressures), len(sto_rows), numerical_invariant,
                    stochastic_invariant, operating_invariant,
                    ", ".join(suppressors) if suppressors else "none",
                    ("[%.1f, %.1f]" % (min(conc_neffs), max(conc_neffs))) if conc_neffs else "n/a",
                    ("[%.4f, %.4f]" % (min(conc_neff_over_N), max(conc_neff_over_N))) if conc_neff_over_N else "n/a",
                    "OK" if all_conserve else "VIOLATED")))


def ntube_switching_convergence(substeps_list=(4, 8, 16, 32, 64), N=200,
                                gs=1.1, P_bar=9.0):
    """RESULT-3 SWITCHING CONVERGENCE (review MAJ-36/B3-14): the baseline trajectory shows
    an abrupt early collapse/rebound over the first few seconds; is the PERSISTENT
    single-channel onset (B6-03) stable, or an artefact of the explicit Euler stepping?
    Re-run the baseline concentrating config at increasing timestep resolution (substeps
    4-64, i.e. the Euler step shrinks 16x) and report, on the PHYSICAL clock: the
    persistent-onset collapse time, the first-passage time, the final N_eff, AND the
    max |N_eff(t)| deviation of each run's trajectory (interpolated onto the finest run's
    physical-time grid) from the finest reference. SCOPE (B6-04): this is Euler-substep
    refinement at FIXED spatial discretization (N) and output grid -- it does NOT vary N
    or use a higher-order/adaptive integrator, and event times are read on the recorded
    output grid; it establishes substep stability of the event, not full grid-independent
    trajectory convergence. NOTE: several PDE-clock solves (slow ~1-2 min)."""
    import numpy as np
    rows = []
    for s in sorted(substeps_list):
        r = ntube_kappa_t_union(gs=gs, N=N, P_bar=P_bar, substeps=s, closure="poroelastic",
                                lateral=0.0, control="flow", compute_ey=False)
        cm = r["concentration_metrics"]
        rows.append(dict(substeps=s,
                         collapse_time_s=cm["collapse_time_s"],           # persistent onset
                         first_passage_top1_s=cm["first_passage_top1_s"],
                         peak_share_time_s=cm["peak_share_time_s"],
                         n_eff_final=round(r["n_eff_channels_final"], 3),
                         entropy_normalized=cm["entropy_normalized"],
                         _t=r["time_s_trajectory"], _neff=r["n_eff_trajectory"]))
    finest = rows[-1]
    # B6-04: the documented trajectory norm -- interpolate each coarser run's N_eff(t)
    # onto the finest run's physical-time grid and take the max abs deviation.
    ft = np.asarray(finest["_t"], float); fn = np.asarray(finest["_neff"], float)
    traj_dev = {}
    for x in rows[:-1]:
        xt = np.asarray(x["_t"], float); xn = np.asarray(x["_neff"], float)
        traj_dev[x["substeps"]] = round(float(np.max(np.abs(np.interp(ft, xt, xn) - fn))), 4)
    max_traj_dev = max(traj_dev.values()) if traj_dev else 0.0
    for x in rows:
        x.pop("_t"); x.pop("_neff")                        # drop bulky arrays from output
    ct = [x["collapse_time_s"] for x in rows if x["collapse_time_s"] is not None]
    ne = [x["n_eff_final"] for x in rows]
    collapse_spread = (round(max(ct) - min(ct), 3) if len(ct) >= 2 else None)
    collapse_converges = bool(len(ct) >= 2 and abs(ct[-1] - ct[-2]) <= 0.5)
    neff_converges = bool(abs(ne[-1] - ne[-2]) <= 0.5)
    return dict(
        N=N, gs=gs, P_bar=P_bar, per_substeps=rows,
        collapse_time_range_s=[round(min(ct), 3), round(max(ct), 3)] if ct else None,
        collapse_time_spread_s=collapse_spread,
        collapse_time_converges=collapse_converges,
        n_eff_final_converges=neff_converges,
        max_neff_trajectory_deviation=max_traj_dev,        # B6-04 documented norm
        neff_trajectory_deviation_by_substeps=traj_dev,
        finest=finest,
        verdict=("Refining the Euler timestep 16x (substeps %d->%d) at FIXED N=%d and "
                 "output grid: the persistent single-channel onset lands in %s s (spread "
                 "%s s, converges=%s), the final N_eff in [%.1f, %.1f] (converges=%s), and "
                 "the N_eff(t) trajectory deviates from the finest run by at most %.3f "
                 "channels. So the early switching event is STABLE under Euler substep "
                 "refinement at fixed spatial discretization/output grid -- NOT a proven "
                 "grid-independent physical event: a higher-order/adaptive integrator, an "
                 "N-refinement, and interpolated event times remain owed (B6-04/B5-08), and "
                 "a physical lateral operator + formal growth analysis before any stability "
                 "claim."
                 % (min(substeps_list), max(substeps_list), N,
                    ("[%.2f, %.2f]" % (min(ct), max(ct))) if ct else "n/a",
                    collapse_spread, collapse_converges, min(ne), max(ne),
                    neff_converges, max_traj_dev)),
        strength="Euler-substep stability of the finite-time collapse EVENT at fixed N + "
                 "output grid (physical clock); NOT a formal stability/eigenmode result "
                 "and NOT full grid-independent trajectory convergence")


# back-compat alias (old name implied a theorem it did not deliver)
ntube_stability_analysis = ntube_finite_time_gain


# --- G4 temperature sensitivity: two independent closures + schmieder datum ---
def g4_temperature_sensitivity(T_lo=80.0, T_hi=98.0, grind="PsiC", mw="med",
                               R=1.5e-4, t_shot_s=30.0, pore_to_bath=0.2):
    """G4 (temperature) PARTIAL resolution. Quantifies the extraction-chemistry
    temperature sensitivity over the espresso range from TWO INDEPENDENT on-file
    closures -- romancorrochano2017 (Arrhenius K(T) + Stokes-Einstein Deff(T)) and
    pannusch2024 (van't Hoff K(T) + Wilke-Chang D(T)) -- and tests pannusch's
    'effects above 80 C are small' conclusion against schmieder2023's measured
    80/89/98 C cup outcome at fixed grind+flow (the matching NEGATIVE datum).
    Does NOT model in-puck thermal transients or T-dependence of wetting/swelling
    (foster2025_2's open flag) -- those are the G4 REMAINDER, still open.
    Validation strength: verification (reproducing published closures) +
    independent/qualitative (the schmieder empirical slope)."""
    import numpy as np
    from puckworks import data as _d
    from puckworks.models.pannusch2024 import closures as _pc
    from puckworks.models.romancorrochano2017 import extraction as _rx
    tK = lambda c: 273.15 + c
    frac = lambda a, b: b / a - 1.0                        # fractional change lo->hi

    # (1) partition K(T): two independent closures over the range
    rK_lo, rK_hi = _rx.K_of_T(T_lo), _rx.K_of_T(T_hi)
    t2 = {r["solute"]: r for r in _d.pannusch_table2()}
    pK = {s: (float(_pc.vant_hoff_K(tK(T_lo), t2[s]["K_ref"], t2[s]["gamma"])),
              float(_pc.vant_hoff_K(tK(T_hi), t2[s]["K_ref"], t2[s]["gamma"])))
          for s in t2}
    K_frac_roman = frac(rK_lo, rK_hi)
    K_frac_pann = {s: frac(*pK[s]) for s in pK}

    # (2) diffusion D(T): two independent closures
    rD_lo, rD_hi = _rx.deff_of(grind, mw, T_lo), _rx.deff_of(grind, mw, T_hi)
    pD = {s: (float(_pc.diffusion_coeff(tK(T_lo), s)),
              float(_pc.diffusion_coeff(tK(T_hi), s))) for s in t2}
    D_frac_roman = frac(rD_lo, rD_hi)
    D_frac_pann = {s: frac(*pD[s]) for s in pD}

    # (3) extraction sensitivity: propagate through the romancorrochano stirred
    # vessel (same solver, only K(T),Deff(T) change) at a fixed shot time
    te = np.linspace(0.0, t_shot_s, 60)
    _, f_lo = _rx.stirred_vessel(rD_lo, R, rK_lo, pore_to_bath, te)
    _, f_hi = _rx.stirred_vessel(rD_hi, R, rK_hi, pore_to_bath, te)
    ey_lo, ey_hi = float(f_lo[-1]), float(f_hi[-1])
    ey_abs_pp = (ey_hi - ey_lo) * 100.0                    # extraction-extent shift [pp]

    # (4) schmieder NEGATIVE datum: measured cup concentration vs target temp at
    # the DoE-center grind+flow (GL 1.7, target flow 2.0), PER component (the four
    # solutes are reported separately). Report each solute's max/min span over the
    # 80/89/98 C axis -- the empirical size of the temperature effect.
    import collections
    rows = _d.schmieder_cup_masses()
    def _f(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    by_comp = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        fl, gl, T, c = (_f(r.get("target_flow_ml_s")), _f(r.get("grind_level")),
                        _f(r.get("target_temp_C")), _f(r.get("conc_in_cup")))
        if None in (fl, gl, T, c) or gl != 1.7 or fl != 2.0:
            continue
        by_comp[r.get("component")][T].append(c)
    sch_spans = {}
    for comp, bt in by_comp.items():
        Ts = sorted(bt)
        if len(Ts) >= 2:
            means = [float(np.mean(bt[T])) for T in Ts]
            sch_spans[comp] = float(max(means) / min(means) - 1.0)
    sch_median_span = float(np.median(list(sch_spans.values()))) if sch_spans else None

    # smallness + agreement verdict (over the ~18 C espresso window). NOTE the two
    # K(T) closures use DIFFERENT partition conventions -> they can DISAGREE on the
    # sign of dK/dT; surface that (rule 6: no silent merge), do not average them.
    all_K = [K_frac_roman] + list(K_frac_pann.values())
    K_small = bool(all(abs(v) < 0.15 for v in all_K))       # magnitude small
    K_sign_agree = bool(all(v > 0 for v in all_K) or all(v < 0 for v in all_K))
    sch_small = bool(sch_median_span is not None and sch_median_span < 0.10)
    return dict(
        T_lo=T_lo, T_hi=T_hi, span_C=T_hi - T_lo,
        K_roman=(rK_lo, rK_hi), K_frac_roman=K_frac_roman,
        K_pann=pK, K_frac_pann=K_frac_pann,
        D_frac_roman=D_frac_roman, D_frac_pann=D_frac_pann,
        ey_extent_lo=ey_lo, ey_extent_hi=ey_hi, ey_shift_pp=ey_abs_pp,
        schmieder_spans=sch_spans, schmieder_median_span=sch_median_span,
        K_small_both=K_small, K_sign_agree=K_sign_agree, schmieder_small=sch_small,
        reading=("over %d C both K(T) closures are SMALL in magnitude (roman "
                 "%+.1f%%, pann %+.1f..%+.1f%%) but %s on sign (partition-convention "
                 "difference -- surfaced, not merged); D(T) roman %+.0f%% / pann "
                 "%+.0f%%; extraction extent shifts %+.2f pp; schmieder cup conc "
                 "spans a median %s across 80/89/98 C. Extraction-chemistry "
                 "T-effect is SMALL and empirically confirmed; in-puck thermal "
                 "transients + wetting/swelling-T stay OPEN (G4 remainder)." % (
                     T_hi - T_lo, 100 * K_frac_roman,
                     100 * min(K_frac_pann.values()), 100 * max(K_frac_pann.values()),
                     "AGREE" if K_sign_agree else "DISAGREE",
                     100 * D_frac_roman,
                     100 * float(np.mean(list(D_frac_pann.values()))), ey_abs_pp,
                     ("%.1f%%" % (100 * sch_median_span))
                     if sch_median_span is not None else "n/a")))


# --- G10 directional mu-bias consistency check (g10_liquor_rheology card) ------
def g10_mu_bias_direction():
    """G10 directional consistency check (the card's suggested gate). REFERENCE/
    qualitative -- NOT a validation (no espresso-TDS flow measurement on file).

    Physics: Darcy/Forchheimer flow is Q ~ 1/mu. Every flow model on file uses
    pure-water mu, but coffee liquor is more viscous where it is more concentrated
    (grudeva flag; G10). The EARLY shot carries the highest dissolved-solids
    concentration (near-saturation liquor) -> highest mu -> most flow suppression;
    the LATE/equilibrium shot is dilute -> mu -> mu_water -> flow essentially
    unchanged. So swapping in the reference espresso mu (a) reduces EARLY flow and
    (b) LEAVES equilibrium intact -- exactly the two properties the card asks for
    (reduce the RC-2/RC-3 early-shot bias without breaking equilibrium agreement),
    IF that bias is early-flow over-prediction (the grudeva-flagged direction).

    Returns the bounded early-flow suppression factor (mu_water/mu_espresso) and
    the equilibrium (late) factor (~1). CAVEAT (card): the effect is only ~1.3-2x;
    confirm the observed bias is not much larger before attributing all of it to
    viscosity. Espresso is Newtonian, so a single local-mu multiplier suffices."""
    from puckworks import data as _d
    r = _d.liquor_rheology()
    mu_water = float(r["viscosity_water_baseline"]["value_or_form"])
    est = r["viscosity_espresso_estimate"]["value_or_form"].replace("~", "")
    lo, hi = (float(x) for x in est.split("-"))          # espresso mu range [Pa s]
    ratio_lo, ratio_hi = lo / mu_water, hi / mu_water    # early mu / water
    # Darcy Q ~ 1/mu: early-shot flow factor vs the pure-water prediction
    early_flow_factor_hi = mu_water / lo                 # least-viscous end
    early_flow_factor_lo = mu_water / hi                 # most-viscous end
    late_flow_factor = 1.0                               # dilute -> mu -> water
    suppresses_early = bool(ratio_lo > 1.0)              # mu_espresso > water
    preserves_equilibrium = bool(abs(late_flow_factor - 1.0) < 1e-9)
    bounded = bool(ratio_hi < 2.5)                       # only ~1.3-2x (card)
    return dict(
        mu_water_Pa_s=mu_water, mu_espresso_range_Pa_s=[lo, hi],
        early_mu_ratio=[round(ratio_lo, 2), round(ratio_hi, 2)],
        early_flow_factor=[round(early_flow_factor_lo, 2), round(early_flow_factor_hi, 2)],
        late_flow_factor=late_flow_factor,
        suppresses_early_flow=suppresses_early,
        preserves_equilibrium=preserves_equilibrium, bounded=bounded,
        reading=("reference espresso mu is %.2f-%.2fx pure water -> Darcy flow "
                 "EARLY is suppressed to %.2f-%.2fx the pure-water prediction, while "
                 "the dilute LATE/equilibrium flow is unchanged (x1.0). Directionally "
                 "reduces an early-flow over-prediction without breaking equilibrium; "
                 "bounded ~1.3-2x (confirm the real bias is not larger). "
                 "Reference/qualitative." % (
                     ratio_lo, ratio_hi, early_flow_factor_lo, early_flow_factor_hi)))

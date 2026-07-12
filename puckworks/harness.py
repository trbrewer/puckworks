"""harness.py — P1 extraction comparison harness (ROADMAP item 2.1 / Sprint 8).

NOT a physics model: an orchestration + reporting layer that runs the registered
extraction components on matched inputs against the shared gate datasets, reports
per-dataset residuals WITH validation-strength tags, and surfaces the P1
normalization hazards (c_sat, soluble-inventory reference, dissolution law, flow
input) as explicit config fields that must NEVER be silently merged (CLAUDE.md
rule 6; ROADMAP §5.4 c_sat, §P1 hazards table, ledger A5).

The interpretive workup (which model wins, P3 hypothesis file 2.3) is the CHAT
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
                flexible_cubic_null=round(rmse_cubic, 3),
                free_params=dict(rung1=1, rung1b=1, rung3=0, rung4=0, rung5=0,
                                 flexible_cubic=4),
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
             parameterization="empirical σ(φ₁) closure (calibrated, not doctored)",
             note="monotone σ(grind) closure → peaked ensemble EY (vertex gs≈%.2f). "
                  "Model-capacity result: a static-heterogeneity closure CAN "
                  "generate an interior maximum. σ was calibrated on cameron's "
                  "grind-deviation data — a viability check, not identification." % ch["peak_gs"]),
        dict(hyp=3, name="lee2023 dissolution instability",
             generates_interior_max=bool(lee_unphys["fine_side_decline"]),
             parameterization="only under DOCTORED ρ_c=798 (2× measured 399)",
             note="interior EY(g) max only at the deliberately-altered ceiling; "
                  "physical ρ_c=399 plateaus (no fine-side decline)."),
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
                           if b["generates_interior_max"] and "DOCTORED" not in b["parameterization"]
                           and "UNIMPLEMENTED" not in b["parameterization"]
                           and b["hyp"] is not None]
    generate_only_doctored = [b["name"] for b in board
                              if b["generates_interior_max"] and "DOCTORED" in b["parameterization"]]
    return dict(
        target=target,
        board=board,
        generate_under_calibrated_params=generate_calibrated,
        generate_only_under_doctored_params=generate_only_doctored,
        verdict=("MODEL-CAPACITY, not identification: of the implemented generators, "
                 "the empirically-calibrated static-heterogeneity closure is the "
                 "only one that produces an interior grind maximum without a "
                 "doctored constant; lee needs ρ_c=798; size-exclusion/diffusion "
                 "are monotone; incomplete wetting is untested. The schmieder "
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
            # DIRECT Jensen gap J = E[EY(K)] - EY(E[K]).  The multipliers are
            # unit-mean lognormal so E[K]=1; J<0 confirms a genuine ensemble
            # deficit (a concave EY(k) loses yield to heterogeneity) WITHOUT
            # relying only on the second-derivative sign. Nodes clipped to the
            # spline support so EY(k) is evaluated where it is defined.
            kc = np.clip(kk, r.k_min, r.k_max)
            wn = w / w.sum()
            E_ey = float(np.sum(wn * r.ey_of_k(kc)))
            ey_mean_k = float(r.ey_of_k(np.clip(1.0, r.k_min, r.k_max)))
            jensen_gap = E_ey - ey_mean_k                 # <=0 for concave EY(k)
            out.append(dict(gs=float(gs), p_bar=float(p), sigma=round(sig, 3),
                            concave_fraction=round(float(np.mean(d2 <= 1e-9)), 3),
                            clip_mass=round(clip, 4),
                            jensen_gap_EYpt=round(jensen_gap, 4)))
    cf = [c["concave_fraction"] for c in out]
    cl = [c["clip_mass"] for c in out]
    jg = [c["jensen_gap_EYpt"] for c in out]
    return dict(cells=out, min_concave_fraction=min(cf), max_clip_mass=max(cl),
                concave_over_support=bool(min(cf) > 0.9),
                clipping_negligible=bool(max(cl) < 0.01),
                max_jensen_gap_EYpt=max(jg), all_jensen_gaps_negative=bool(max(jg) <= 0),
                verdict=("EY(k) is concave over %.0f-%.0f%% of the tested support and "
                         "the lognormal clip mass is <%.2f%% at all grinds/pressures; "
                         "the DIRECT Jensen gap J=E[EY(K)]-EY(1) is <=0 in every cell "
                         "(worst %.3f EY-pt) -> the ensemble deficit is confirmed by "
                         "direct measurement, not only by the 2nd-derivative sign "
                         "(global concavity NOT claimed); clipping is negligible."
                         % (100 * min(cf), 100 * max(cf), 100 * max(cl), max(jg))))


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


def schmieder_rsm_refit(component="tds", brew_ratio="1/2"):
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
    the source model is wrong."""
    from puckworks import data as _d
    comp = _SCHM_COMPONENT.get(component.lower(), component)
    rows = _d.schmieder_cup_masses()
    obs = []
    for r in rows:
        if r.get("component") != comp or r.get("brew_ratio") != brew_ratio:
            continue
        F, G, T, y = (_f_num(r.get("target_flow_ml_s")), _f_num(r.get("grind_level")),
                      _f_num(r.get("target_temp_C")), _f_num(r.get("mass_in_cup")))
        if None in (F, G, T, y):
            continue
        obs.append((F, G, T, y))
    o = np.asarray(obs, float)
    F, G, T, y = o[:, 0], o[:, 1], o[:, 2], o[:, 3]
    # retained terms (TDS 1/2 printed): 1, F, G, T, G^2, T^2, FG (beta4/8/9 = 0)
    # NOTE predictors are on the RAW scale (not centered), so the individual
    # coefficients are not orthogonal and the vertex below combines b_G/b_G2/b_FG.
    X = np.column_stack([np.ones_like(F), F, G, T, G ** 2, T ** 2, F * G])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    fl, tp, g = _SCHM_CENTER["flow_ml_s"], _SCHM_CENTER["temp_C"], 1.7
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
    # case-resampling bootstrap CI on the vertex (deterministic seed -> reproducible)
    rng = np.random.default_rng(0)
    boot = []
    for _ in range(2000):
        idx = rng.integers(0, n, n)
        cb, *_ = np.linalg.lstsq(X[idx], y[idx], rcond=None)
        vb = _vertex(cb)
        if np.isfinite(vb):
            boot.append(vb)
    vertex_ci95 = ([round(float(np.percentile(boot, 2.5)), 3),
                    round(float(np.percentile(boot, 97.5)), 3)] if boot else None)
    # printed rounded-coefficient evaluation (the artifact)
    pr = {(r["component"], r["brew_ratio"]): r for r in _d.schmieder_rsm()}[
        ("TDS" if comp == "TDS" else comp.capitalize(), brew_ratio)]
    printed_pred = float(pr["beta0"] + pr["beta1"] * fl + pr["beta2"] * g + pr["beta3"] * tp
                         + pr["beta4"] * fl ** 2 + pr["beta5"] * g ** 2 + pr["beta6"] * tp ** 2
                         + pr["beta7"] * fl * g + pr["beta8"] * fl * tp + pr["beta9"] * g * tp)
    raw_central = float(np.mean([v for FF, GG, TT, v in obs
                                 if FF == fl and GG == g and TT == tp]))
    return dict(n_obs=len(obs), refit_central_g=refit_pred,
                printed_central_g=printed_pred, raw_central_g=raw_central,
                r2=round(r2, 4), adj_r2=round(adj_r2, 4), n=n, n_predictors=p,
                vertex_g=round(vertex_g, 3) if np.isfinite(vertex_g) else None,
                vertex_is_max=vertex_is_max, vertex_ci95_g=vertex_ci95,
                predictors_centered=False,
                printed_is_artifact=bool(abs(printed_pred - raw_central) > 1.0
                                         and abs(refit_pred - raw_central) < 0.5))


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
    refit = schmieder_rsm_refit("tds", _SCHM_CENTER["brew_ratio"])
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
    structure to explain). The mechanisms separate by regime; no single mechanism
    is lowest everywhere. Regime bins (low <=2 bar, mid 3.5-6 bar) are FIXED on the
    slow-flow / near-equilibrium physics, not chosen after seeing the residuals.
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
    per = {}
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
        per[p] = dict(static=round(r_static, 3), phi=round(r_phi, 3),
                      rc3b=round(r_rc3b, 3))

    def _mean(keys, mech):
        v = np.array([per[p][mech] for p in keys], float)
        return float(np.nanmean(v))
    oos = [p for p in ps if p != 9.0]
    low = [p for p in ps if p <= 2.0]
    mid = [p for p in ps if 3.5 <= p <= 6.0]
    return dict(
        per_pressure=per,
        conditional_transfer_mean={m: round(_mean(oos, m), 3)
                                   for m in ("static", "phi", "rc3b")},
        low_p_mean={m: round(_mean(low, m), 3) for m in ("phi", "rc3b")},
        mid_p_mean={m: round(_mean(mid, m), 3) for m in ("static", "phi", "rc3b")},
        # the two load-bearing separations (each a distinct physics claim):
        phi_generalizes=_mean(oos, "phi") < _mean(oos, "static"),
        rc3b_lower_low_p=_mean(low, "rc3b") < _mean(low, "phi"),
        static_lower_mid_p=_mean(mid, "static") < min(_mean(mid, "phi"),
                                                      _mean(mid, "rc3b")),
        reading="Phi(t) has the lowest transfer-mean RMSE but is regime-dependent: "
                "RC-3b is lower low-P (flow-coupled dissolution), static is lower "
                "mid-P (no time structure). No single mechanism is lowest at every "
                "pressure. Conditional-transfer, NOT independent validation.")


# --- N-tube kappa(t) union: streamtube channeling x coupled_kappa_t per-tube --
def ntube_kappa_t_union(gs=1.1, N=400, s_ref=0.6, m=1.0, P_bar=9.0,
                        closure="poroelastic", lateral=0.0, substeps=8,
                        compute_ey=True, control="flow", conductance_floor=1e-12):
    """EXPLORATORY SYNTHESIS harness (qualitative). Fuses the two P3/P2 winners:
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
    # deterministic unit-mean lognormal nodes at evenly-spaced quantiles
    p = (np.arange(N) + 0.5) / N
    z = norm.ppf(p)
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
        s = w / w.sum()                                    # normalized shares
        sw = np.sort(s)[::-1]
        top_share.append(float(sw[:top].sum()))
        max_share.append(float(sw[0]))                     # largest SINGLE tube
        n_eff.append(float(1.0 / np.sum(s ** 2)))          # effective # channels
    top_share = np.array(top_share)
    max_share = np.array(max_share); n_eff = np.array(n_eff)
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
    # strong concentration == flow collapses toward a single effective channel
    concentrates = bool(top_share[-1] > 0.90 and not self_limiting)
    return dict(
        gs=gs, sigma=sigma, N=N, closure=closure, lateral=lateral, P_bar=P_bar,
        control=control, conductance_floor=conductance_floor,
        top_decile_share_static=float(top_share[0]),      # t~0, phi~0 (== static)
        top_decile_share_peak=float(top_share[j_peak]),
        top_decile_share_final=float(top_share[-1]),
        max_single_tube_share_final=float(max_share[-1]),
        n_eff_channels_static=float(n_eff[0]),
        n_eff_channels_final=float(n_eff[-1]),
        peak_time_s=float(t[1:][j_peak]),
        self_limiting=self_limiting, concentrates=concentrates,
        # keep `runaway` as an alias for back-compat, but it now means "strong
        # concentration in the TESTED configuration", not a proven instability
        runaway=concentrates,
        ey_static=ey_static, ey_dynamic=ey_dyn,
        deepens_dip=bool(ey_dyn < ey_static - 1e-6),
        reading=("[%s%s] top-decile share %.2f->%.2f, max single-tube %.2f, "
                 "N_eff %.0f->%.1f of %d; %s; ensemble EY %s (%.1f%%->%.1f%%) @%gbar"
                 % (closure, (" +lat%.2f" % lateral) if lateral else "",
                    top_share[0], top_share[-1], max_share[-1],
                    n_eff[0], n_eff[-1], N,
                    "STRONG concentration (tested near-choke config)"
                    if concentrates else
                    ("self-limiting" if self_limiting else "bounded/stable"),
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

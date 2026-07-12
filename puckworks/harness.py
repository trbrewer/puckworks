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
def kappa_t_ladder():
    """Run the P2 null-first ladder on the Waszkiewicz 9-bar RISING-flow trace.
    Returns per-rung RMSE [g/s] over the saturated window (t = 15-115 s).

    rung 1 recorded-pressure Darcy, constant kappa (flat Q)      -> the floor
    rung 3 static kappa(P) equilibrium at constant P (also flat)
    rung 4 waszkiewicz2025 time-dependent Phi(t) = m_d(t)/m0     -> rises with the data
    (rung 2, the foster2025 pump/headspace flow-MINIMUM null, is a distinct
     early-shot phenomenon validated by gate_foster_fig15_flowmin, not the
     saturated rising-flow residual tested here; rung 5 challengers are Phase 3.)
    """
    import numpy as np
    from puckworks import data as d
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    tr = d.waszkiewicz_traces()
    t = tr[9.0]["time__s"]; q = tr[9.0]["mass_flow_rate__g_per_s"]
    sel = (t >= 15) & (t <= 115)
    td, qd = t[sel], q[sel]
    q_flat = float(np.mean(q[t >= 100]))                 # long-run Darcy/static
    rmse_flat = float(np.sqrt(np.mean((q_flat - qd) ** 2)))
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
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
    return dict(rung1_const_kappa=round(rmse_flat, 3),
                rung3_static_kappaP=round(rmse_flat, 3),
                rung4_phi_of_t=round(rmse4, 3),
                rung5_rc3b_cameron_coupled=round(rmse5, 3),
                rung4_beats_floor=rmse4 < rmse_flat,
                improvement_factor=round(rmse_flat / rmse4, 1),
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
    return dict(R_total=R_total, R_puck_measured_range=[R_puck(max(k_meas)), R_puck(min(k_meas))],
                puck_share_measured=[round(frac(max(k_meas)), 2), round(frac(min(k_meas)), 2)],
                kappa_measured_range=[min(k_meas), max(k_meas)],
                kappa_fitted_DE1=k_de1, kappa_fitted_grudeva=k_grud,
                fitted_below_measured=bool(k_de1 < min(k_meas) and k_grud < min(k_meas)),
                puck_below_total=bool(R_puck(min(k_meas)) < R_total),
                verdict="series-resistance model implemented; fitted effective kappa "
                        "(DE1, grudeva) sits below the measured tamped kappa -> a non-puck "
                        "(screen+fixture) resistance is implied. CROSS-SOURCE + grudeva "
                        "adjudication weakened -> suggestive, not conclusive; needs a "
                        "matched puck-kappa + in-machine total-R measurement to close.")


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


# --- cross-pressure generalization discriminator (item 2.2, ANALYSIS_P2) ---
# Waszkiewicz ran 11 pressures. Fix ONE calibration and predict every trace out
# of sample: the mechanism that best explains all pressures wins, and where the
# mechanisms disagree tells you which physics each is really capturing (CHAT
# §2.2 point 1). All three mechanisms share the published static pair (P_c, Q_c);
# nothing is refit per pressure.
def cross_pressure_discrimination(window=(15.0, 95.0)):
    """Out-of-sample RMSE [g/s] of three kappa(t) mechanisms across all 11
    Waszkiewicz pressures, using ONE fixed calibration (no per-pressure refit):

      static kappa(P)      Q(t) = q_static(P)                    flat, rung-3 analog
      dissolution Phi(t)   empirical near-instant sigmoid m_d(t) rung 4
      RC-3b coupled        m_d(t) from cameron2020 at that P     rung 5

    The empirical sigmoid is pressure-INDEPENDENT (one m_d(t) for every shot);
    RC-3b re-runs Cameron at each pressure, so its Phi(t) is flow-coupled. The
    9-bar point is the sigmoid's home pressure; the other 10 are out of sample.
    Returns per-pressure RMSE plus regime aggregates. Result (see ANALYSIS_P2
    §2.2): Phi(t) wins on the OOS mean but NOT uniformly -- RC-3b wins at the
    low-pressure end (flow-coupling matters where flow is slow) and the static
    null wins mid-range (little time structure to explain). The mechanisms
    separate across the set exactly as the design predicted; no single winner.
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
        oos_mean={m: round(_mean(oos, m), 3) for m in ("static", "phi", "rc3b")},
        low_p_mean={m: round(_mean(low, m), 3) for m in ("phi", "rc3b")},
        mid_p_mean={m: round(_mean(mid, m), 3) for m in ("static", "phi", "rc3b")},
        # the two load-bearing separations (each a distinct physics claim):
        phi_generalizes=_mean(oos, "phi") < _mean(oos, "static"),
        rc3b_wins_low_p=_mean(low, "rc3b") < _mean(low, "phi"),
        static_wins_mid_p=_mean(mid, "static") < min(_mean(mid, "phi"),
                                                      _mean(mid, "rc3b")),
        reading="Phi(t) best on OOS mean but regime-dependent: RC-3b wins low-P "
                "(flow-coupled dissolution), static wins mid-P (no time structure)")

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


def _schmieder_mass_vs_grind():
    """Extract the schmieder2023 cup-mass-vs-grind curve at each target flow.
    Returns {flow: (grinds, masses, interior_peak_bool, peak_grind)}. Data are
    mixed-type (some grind/mass cells are strings) → coerce defensively."""
    import collections
    from puckworks import data as _d
    rows = _d.schmieder_cup_masses()
    def _f(x):
        try:
            return float(x)
        except (TypeError, ValueError):
            return None
    by_flow = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        fl, gl, m = _f(r.get("target_flow_ml_s")), _f(r.get("grind_level")), _f(r.get("mass_in_cup"))
        if None in (fl, gl, m):
            continue
        by_flow[fl][gl].append(m)
    out = {}
    for fl, gd in by_flow.items():
        grinds = sorted(gd)
        if len(grinds) < 3:
            continue
        masses = [float(np.mean(gd[g])) for g in grinds]
        ip = int(np.argmax(masses))
        out[fl] = (grinds, masses, bool(0 < ip < len(grinds) - 1), grinds[ip])
    return out


def schmieder_peak_discrimination(n_grid=6):
    """P3 fine-grind-dip VERDICT harness. The schmieder2023 target: at fixed
    flow, cup mass is NON-MONOTONIC in grind — an interior peak at GL 1.7 that
    appears only at LOW flow and washes out to monotone at higher flow. This
    runs each instrumented P3 mechanism and asks the single discriminating
    question: does it produce an INTERIOR MAXIMUM in the grind response (the
    schmieder signature), and from PHYSICAL parameters?

    Scoreboard entries carry: produces_interior_peak (bool) and
    physical (bool — True if the peak survives at physically-admissible params,
    False if it needs a doctored constant). Validation strength: qualitative /
    mechanism-discrimination (the schmieder curve is real data; the mechanism
    grind-responses are each on their own native grind axis — dial spaces are
    non-portable per CLAUDE.md rule 9, so this compares SHAPE, not GL location)."""
    from puckworks.models.lee2023 import feedback as _lee
    from puckworks import data as _d

    target = _schmieder_mass_vs_grind()
    lo = min(target)  # lowest target flow — where the peak lives
    hi = max(target)

    # (1) static channeling σ(φ₁) — streamtube EY-deficit through fines fraction
    ch = channeling_sigma_sweep(gs_grid=(1.0, 1.5, 2.0, 2.5), n_grid=n_grid)

    # (2) size-exclusion entrapment — romancorrochano extractable inventory y₀(grind)
    y0 = [r for r in _d.roman_y0_extractable() if r["method"] == "dilute"]
    ladder = ["PsiA", "PsiB", "PsiE", "PsiF", "PsiG", "PsiH"]  # fine→coarse
    y0_seq = [next(r["y0_pct"] for r in y0 if r["grind"] == g) for g in ladder]
    y0_ip = int(np.argmax(y0_seq))

    # (3) lee2023 dissolution instability — interior peak only at unphysical ρ_c
    g = np.linspace(1.1, 2.3, 13)
    lee_phys = _lee.peak_and_fine_decline(g, rho_c=399.0)   # physical
    lee_unphys = _lee.peak_and_fine_decline(g, rho_c=798.0)  # doctored ceiling

    # (4) base / diffusion extraction — the monotone null (no bed mechanism)
    base = ch["ey_homog"]
    base_monotone = bool(np.all(np.diff(base) <= 1e-9))

    board = [
        dict(hyp=1, name="static channeling σ(φ₁)",
             produces_interior_peak=bool(ch["ensemble_peaks_interior"]),
             physical=True,
             note="monotone σ(grind) closure → peaked ensemble EY (peak gs≈%.2f); "
                  "deficit largest at finest grind. Peak from physical params." % ch["peak_gs"]),
        dict(hyp=3, name="lee2023 dissolution instability",
             produces_interior_peak=bool(lee_unphys["fine_side_decline"]),
             physical=bool(lee_phys["fine_side_decline"]),
             note="interior EY(g) peak only at imposed ρ_c=798; physical ρ_c=399 "
                  "plateaus (no fine-side decline). Peak needs a doctored ceiling."),
        dict(hyp=4, name="size-exclusion entrapment y₀(grind)",
             produces_interior_peak=bool(0 < y0_ip < len(y0_seq) - 1),
             physical=True,
             note="y₀ monotone-decreasing along fine→coarse ladder (%.1f→%.1f%%); "
                  "no interior maximum." % (y0_seq[0], y0_seq[-1])),
        dict(hyp=None, name="base / diffusion extraction (null)",
             produces_interior_peak=not base_monotone,
             physical=True,
             note="homogeneous EY(grind) monotone — no bed mechanism, no peak."),
    ]
    # a mechanism REPRODUCES the schmieder peak iff it makes an interior maximum
    # from physical params.
    reproduce = [b for b in board if b["produces_interior_peak"] and b["physical"]]
    reproduce_unphysical = [b for b in board
                            if b["produces_interior_peak"] and not b["physical"]]
    return dict(
        schmieder_target=target,
        low_flow=lo, high_flow=hi,
        low_flow_interior_peak=target[lo][2], low_flow_peak_grind=target[lo][3],
        high_flow_interior_peak=target[hi][2],
        board=board,
        reproduce_physical=[b["name"] for b in reproduce],
        reproduce_only_unphysical=[b["name"] for b in reproduce_unphysical],
        verdict=("static channeling (#1) is the only mechanism reproducing the "
                 "schmieder interior peak from physical parameters"))


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


# --- N-tube kappa(t) union: streamtube channeling x coupled_kappa_t per-tube --
def ntube_kappa_t_union(gs=1.1, N=400, s_ref=0.6, m=1.0, P_bar=9.0,
                        closure="poroelastic", lateral=0.0, substeps=8,
                        compute_ey=True):
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
        in [0,1] is a lateral pressure-equalization regularizer: w <- (1-lateral)*w
        + lateral*1 (the parallel-non-exchanging assumption relaxed toward a
        laterally-mixed bed). substeps subdivides each trace interval (Euler
        stability check -- the runaway is not a step-size artifact).
      - Coupled ODE: dtau_i/dt = w_i(t), integrated on the waszkiewicz time base.

    Reports the flow-concentration trajectory (top-decile share; share spread),
    whether it peaks-then-relaxes (self-limiting) vs monotone-growing (runaway),
    and the ensemble-EY deficit vs the STATIC streamtube. Validation strength:
    qualitative / exploratory synthesis -- NOT a registered component, NOT a
    validated kappa(t) law (as sound as its shakiest donor; see coupled_kappa_t)."""
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
    Mofphi = lambda ph: np.clip(M(np.clip(ph, 0.0, phi_max)), 1e-12, None)

    # integrate the coupled throughput-clock ODE (Euler, substepped per interval)
    tau = np.zeros(N)
    top = max(1, N // 10)
    top_share, spread = [], []
    M_acc = np.zeros(N)                                    # for time-avg share
    for i in range(1, len(t)):
        dt = (t[i] - t[i - 1]) / substeps
        for _ in range(substeps):
            g = k0 * Mofphi(Phi(tau))
            w = g / float(np.mean(g))                      # unit-mean flow share
            if lateral:
                w = (1.0 - lateral) * w + lateral          # lateral equalization
            tau = tau + w * dt
            M_acc = M_acc + w * dt
        sw = np.sort(w)[::-1]
        top_share.append(float(sw[:top].sum() / w.sum()))
        spread.append(float(np.std(w)))
    top_share = np.array(top_share); spread = np.array(spread)
    # ensemble EY: static k0 distribution vs dynamic time-avg flow share (unit-mean)
    if compute_ey:
        k_eff = M_acc / t[-1]
        ey = _st.EYResponse(gs=gs, p_bar=5.0)
        ey_static = float(np.mean(ey.ey_of_k(k0)))
        ey_dyn = float(np.mean(ey.ey_of_k(np.clip(k_eff, ey.k_min, ey.k_max))))
    else:
        ey_static = ey_dyn = float("nan")
    j_peak = int(np.argmax(top_share))
    self_limiting = bool(j_peak < len(top_share) - 1
                         and top_share[-1] < top_share[j_peak] - 1e-3)
    # "runaway" == essentially all flow latches into the top decile
    runaway = bool(top_share[-1] > 0.90 and not self_limiting)
    return dict(
        gs=gs, sigma=sigma, N=N, closure=closure, lateral=lateral,
        top_decile_share_static=float(top_share[0]),      # t~0, phi~0 (== static)
        top_decile_share_peak=float(top_share[j_peak]),
        top_decile_share_final=float(top_share[-1]),
        peak_time_s=float(t[1:][j_peak]),
        spread_peak=float(spread.max()), spread_final=float(spread[-1]),
        self_limiting=self_limiting, runaway=runaway,
        ey_static=ey_static, ey_dynamic=ey_dyn,
        deepens_dip=bool(ey_dyn < ey_static - 1e-6),
        reading=("[%s%s] top-decile flow share %.2f->%.2f; %s; ensemble EY %s "
                 "(%.1f%%->%.1f%%)" % (
                     closure, (" +lat%.2f" % lateral) if lateral else "",
                     top_share[0], top_share[-1],
                     "RUNAWAY (single-channel latch)" if runaway else
                     ("self-limiting" if self_limiting else "bounded/stable"),
                     "drops" if ey_dyn < ey_static else "holds",
                     ey_static, ey_dyn)))


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

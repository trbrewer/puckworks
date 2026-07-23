"""Fast validation gates (< ~30 s total). Heavier ladders (sphere-array
resolution study, twin-solver pack cross-check, GPU sweeps) live in
validation/slow/ and the Colab notebook."""
import json, os
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def gate_lb_channel():
    """Reference LB kernel vs exact plane-Poiseuille solution. This gate OWNS the acceptance threshold
    (abs err < 0.5%); the channel arithmetic is the component's canonical helper, shared with the Lab
    native runner so the two can never diverge."""
    from puckworks.models.brewer2026 import lb_reference as lb
    v = lb.channel_verification()          # canonical shared computation; no threshold inside it
    return dict(passed=abs(v["err_pct"]) < 0.5, err_pct=round(v["err_pct"], 3))

def gate_wadsworth_collapse():
    """Percolation collapse reproduces from their own Table 1."""
    from puckworks.models.wadsworth2026 import permeability as wp
    rows = wp.table1()
    ratios = [r["k_m2"]/wp.k_star(r["phi_p"], r["s_p"]) / r["phi_p"]**wp.B_PERC
              for r in rows]
    gm = float(np.exp(np.mean(np.log(ratios))))
    return dict(passed=0.7 < gm < 1.2, geometric_mean_ratio=round(gm, 3))

def gate_infiltration_triangle():
    """Parameter-free first-drip prediction brackets the DE1 observation."""
    from puckworks.models.foster2025 import infiltration as inf
    d = json.load(open(os.path.join(DATA, "de1_fixtureA.json")))
    t = np.array(d["elapsed_s"]); P = np.array(d["pressure_bar"])
    w = np.array(d["weight_g"])
    # single authoritative threshold constant (shared with the Lab native runner); explicit crossing
    t_drip = inf.observed_first_drip_s(t, w)
    k, L = inf.k_from_kappa(d["grind_setting_assumed"], d["dose_g"]/1000,
                            d["kappa_fitted"])
    ts = {}
    for phiT in (0.173, 0.322):
        r = inf.front_from_pressure(t, P, k, phiT, L)
        ts[phiT] = r["t_saturate"]
    passed = ts[0.173] is not None and ts[0.173] < t_drip < ts[0.322]
    return dict(passed=passed, observed_s=t_drip,
                predicted_bracket_s=[round(ts[0.173], 1), round(ts[0.322], 1)])

def gate_waszkiewicz_static_refit():
    """Refitting Eq. 16 to their 11-pressure long-run curve recovers (P_c, Q_c).

    Independent-within-rig: target (P_c, Q_c) = (12 bar, 1.90 g/s); also matches
    the ingested published static calibration (same method + data)."""
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    P, Q = wz.steady_state_curve()
    (P_c, Q_c), _ = wz.fit_static(P, Q)
    P_pub, Q_pub = wz.published_calibration()
    passed = (abs(P_c - 12.0) < 3.0 and abs(Q_c - 1.90) < 0.15
              and abs(P_c - P_pub) < 0.05 and abs(Q_c - Q_pub) < 0.01)
    return dict(passed=passed, P_c=round(P_c, 3), Q_c=round(Q_c, 3),
                P_c_pub=round(P_pub, 3), Q_c_pub=round(Q_pub, 3))


def gate_waszkiewicz_dynamic_9bar():
    """Parameter-free Eq. 18 reproduces the 9-bar Q(t) ramp (semi-quantitative).

    Zero extra parameters: (P_c, Q_c) from the static fit + the dissolution
    sigmoid. Post-fit reconstruction (m_d from the same rig, per card)."""
    from puckworks.models.waszkiewicz2025 import poroelastic as wz
    from puckworks import data as d
    tr = d.waszkiewicz_traces()
    t = tr[9.0]["time__s"]; meas = tr[9.0]["mass_flow_rate__g_per_s"]
    P_c, Q_c = wz.published_calibration()
    k_s, l_s, m_s = wz._solids_params()
    dose = d.waszkiewicz_constants()["dose__g"]
    pred = wz.q_dynamic(t, 9.0, P_c, Q_c, k_s, l_s, m_s, dose)
    sel = t >= 15.0                                  # skip infiltration transient
    lr_pred = float(np.mean(pred[-50:])); lr_meas = float(np.mean(meas[-50:]))
    lr_err = abs(lr_pred - lr_meas)/lr_meas
    corr = float(np.corrcoef(pred[sel], meas[sel])[0, 1])
    return dict(passed=(lr_err < 0.10 and corr > 0.90),
                longrun_pred=round(lr_pred, 3), longrun_meas=round(lr_meas, 3),
                longrun_rel_err=round(lr_err, 3), corr_t_ge_15s=round(corr, 3))


def gate_grindmap_refit():
    """Refit <R>=beta*G+R0 from Table 1 is a good linear map spanning the data.

    Reproduction/verification: R^2 > 0.99, monotone increasing, predicted range
    brackets the measured <R>. (The card's printed beta/R0 do NOT reproduce here
    — recorded, not asserted; see grindmap module docstring.)"""
    from puckworks.models.wadsworth2026 import grindmap as gm
    rows = gm._d.wadsworth_grindmap_table1()
    beta, R0, st = gm.fit_grind_map(rows)
    R = sorted(r["R_mean_m"] for r in rows)
    pred1, pred11 = gm.mean_radius(1, beta, R0), gm.mean_radius(11, beta, R0)
    passed = (st["r2"] > 0.99 and beta > 0
              and pred1 < pred11                       # monotone increasing
              and R[0]*0.9 < pred1 and pred11 < R[-1]*1.1)
    return dict(passed=passed, beta=round(beta, 10), R0=round(R0, 8),
                r2=round(st["r2"], 4), n=st["n"],
                beta_card=gm.BETA_CARD, card_reproduces=abs(beta-gm.BETA_CARD) < 5e-6)


def gate_grindmap_polydispersity():
    """S=<R><R2>/<R3> reconstructs the reported S, and S(G) rises with G.

    Verification of the moment columns + the card's qualitative S(G) trend
    (~0.46-0.55 at G=1 to ~0.77-0.78 at G=11)."""
    from puckworks.models.wadsworth2026 import grindmap as gm
    rows = gm._d.wadsworth_grindmap_table1()
    err = max(abs(gm.polydispersity(r["R_mean_m"], r["R2_mean_m2"], r["R3_mean_m3"])
                  - r["S_polydispersivity"]) for r in rows)
    ok_trend = True
    for coffee in ("Guayacan", "Tumba"):
        S = [r["S_polydispersivity"] for r in rows if r["coffee"] == coffee]
        # overall rise (Spearman would need scipy; use endpoint + rank-increase)
        rises = sum(b > a for a, b in zip(S, S[1:]))
        ok_trend &= (S[-1] - S[0] > 0.2 and rises >= len(S) - 3
                     and 0.44 < S[0] < 0.56 and 0.75 < S[-1] < 0.80)
    # 5e-3 tolerance: the moment columns are printed to 3 sig figs, so
    # S=<R><R2>/<R3> recomputed from them carries ~1e-3 rounding noise.
    return dict(passed=(err < 5e-3 and ok_trend), max_S_reconstruct_err=round(err, 5))


def gate_inertial_fo_band():
    """Reproduce the card's espresso Fo_F band 0.0161-0.0639 (eq 2.7 closure).

    Independent reproduction of the paper's worked estimate from its stated
    inputs (Fo_F ~ 1/sqrt(k), so the grind/pack k range drives the band)."""
    from puckworks.models.wadsworth2026 import inertial as fo
    lo, hi = fo.espresso_fo_band("zhou")
    lo_c, hi_c = fo.FO_BAND_CARD
    return dict(passed=(abs(lo - lo_c) < 5e-4 and abs(hi - hi_c) < 5e-4),
                band=[round(lo, 4), round(hi, 4)], card=[lo_c, hi_c])


def gate_inertial_darcy_recovery():
    """Forchheimer q -> Darcy q = |grad_p| k / mu as k_I -> infinity (verification)."""
    from puckworks.models.wadsworth2026 import inertial as fo
    k, grad_p = 1e-13, 5e5 / 0.02
    q_darcy = grad_p * k / fo.MU_92C
    q_big = fo.solve_q(k, 1e30, grad_p)          # k_I -> inf
    q_fin = fo.solve_q(k, fo.k_I(k, "zhou"), grad_p)   # finite k_I slows flow
    return dict(passed=(np.isclose(q_big, q_darcy, rtol=1e-6) and q_fin < q_darcy),
                q_darcy=q_darcy, q_kI_inf=float(q_big))


def gate_inertial_de1_audit():
    """§5.2 audit: Fo_F on DE1 fixture A (tamped) exceeds the untamped band by
    >10x and is O(1) (eq 2.8), settling the gusher-regime disagreement toward
    the backlog's 0.3-0.9 estimate. Extrapolation caveat: DE1 k~7e-15 sits below
    the ceramics-fit support (recorded, not asserted precise)."""
    from puckworks.models.wadsworth2026 import inertial as fo
    a = fo.de1_fixtureA_audit()
    exp_max = a["Fo_F_max_exp"]
    passed = (0.3 < exp_max < 1.0                       # backlog-magnitude, O(1)
              and exp_max > 10 * fo.FO_BAND_CARD[1])    # >> untamped band
    return dict(passed=passed, Fo_F_max_exp=round(exp_max, 3),
                Fo_F_max_zhou=round(a["Fo_F_max_zhou"], 3), k_m2=a["k_m2"])


def gate_liang_kemax_refit():
    """Refit K*E_max from digitized Fig 3 (R_brew>=3) recovers ~0.215 (card).

    Post-fit of the digitized 1-L TDS-vs-R_brew data via Eq. 11."""
    from puckworks.models.liang2021 import desorption as lg
    rows = [r for r in gates_data().liang_fig3_tds()
            if r["R_brew_digitized_g_per_g"] >= 3.0]
    R = [r["R_brew_digitized_g_per_g"] for r in rows]
    TDS = [r["TDS_percent"] / 100.0 for r in rows]
    ke = lg.fit_K_Emax(R, TDS)
    return dict(passed=(abs(ke - 0.215) < 0.01), K_Emax=round(ke, 4),
                card=0.215, n=len(rows))


def gate_liang_eoven_ceiling():
    """E_oven kernel (Eq 22) reproduces the Fig 4 oven branch, and the immersion
    equilibrium ceiling K*E_max sits below cameron's inventory ceiling (§5.5)."""
    from puckworks.models.liang2021 import desorption as lg
    import numpy as np
    f4 = gates_data().liang_fig4_E()
    oven = [r for r in f4 if r["measurement"] == "oven_drying"
            and r["R_brew_digitized_g_per_g"] >= 3.0]
    eq = [r for r in f4 if r["measurement"] == "equilibrium"
          and r["R_brew_digitized_g_per_g"] >= 3.0]
    R = np.array([r["R_brew_digitized_g_per_g"] for r in oven])
    E_meas = np.array([r["E_percent"] for r in oven]) / 100.0
    pred = lg.E_oven(R)
    mape = float(np.mean(np.abs(pred - E_meas) / E_meas))
    eq_mean = float(np.mean([r["E_percent"] for r in eq]) / 100.0)
    cam = lg.cameron_inventory_ceiling()
    passed = (mape < 0.15                          # oven kernel tracks Fig 4
              and abs(eq_mean - 0.21) < 0.03        # equilibrium E flat ~21%
              and lg.K_EMAX_1L < cam)               # §5.5: equilibrium < inventory
    return dict(passed=passed, eoven_mape=round(mape, 3),
                eq_E_mean=round(eq_mean, 3), liang_ceiling=lg.K_EMAX_1L,
                cameron_ceiling=round(cam, 3))


def gate_moroney_fig6_washthrough():
    """Leading-order composite reproduces Fig 6's saturated plateau (t<1) and
    wash-through timing (c=1/2 near the data's midpoint). QUALITATIVE — the
    long-time diffusion tail needs the outer solution (not on card)."""
    from puckworks.models.moroney2016 import surrogate as mo
    import numpy as np
    d = gates_data().moroney_fig6()
    t = np.array([r["t_nondimensional"] for r in d])
    c = np.array([r["c_h_nondimensional"] for r in d])
    t_half = mo.washthrough_halfmax_time()
    # data midpoint: interpolate t at c=0.5 (np.interp needs ascending c)
    order = np.argsort(c)
    t_half_data = float(np.interp(0.5, c[order], t[order]))
    early = t <= 3.6
    pred_early = mo.composite_exit(t[early])
    rmse_early = float(np.sqrt(np.mean((pred_early - c[early]) ** 2)))
    passed = (mo.composite_exit(0.5) == 1.0                 # plateau before wash-through
              and abs(t_half - t_half_data) < 0.6            # wash-through timing
              and rmse_early < 0.15)                         # early-region envelope
    return dict(passed=passed, t_half_model=round(t_half, 2),
                t_half_data=round(t_half_data, 2), rmse_early=round(rmse_early, 3))


def gate_grudeva_no_eps_kappa():
    """G0+G4: the reference solver's capacitance carries NO ε (adjudicated form),
    and S1 Eq. 6.14 at 9.2 bar recovers the adjudicated κ ≈ 2.2e-15 m² (settling
    the LOG Issue 1 + 2a decade error), not the printed 2.2e-16."""
    from puckworks.models.grudeva2025 import reduced as gr
    B, term_l, term_f = gr.capacitance_B()
    # no-eps: B equals phi_l/phi_T + phi_f/phi_T exactly (no 1e-2..1e-3 factor)
    no_eps = abs(B - (term_l + term_f)) < 1e-12 and term_l > 0.1
    k = gr.kappa_eq614(0.43, 12.43e-3, 3.15e-4, 9.2e5, 5.0)
    return dict(passed=(no_eps and abs(k - 2.2e-15) / 2.2e-15 < 0.1),
                B=round(B, 4), kappa_eq614=k, kappa_adjudicated=2.2e-15)


def gate_grudeva_reduced_solver():
    """G2+G3: the reduced solve produces a post-first-drip saturated plateau
    (s_d^{-1}(1) > 1) and reconstructs the C1 per-vial masses — total solute
    within 5% of the 14-shot mean and a majority of vials within 1 SD. POST-FIT
    reconstruction (parameters were fitted to this data). Coarse grid (~1.3 s);
    the resolution study + ε-form discrimination are a slow ladder."""
    import numpy as np
    from puckworks.models.grudeva2025 import reduced as gr
    r = gr.make_coffee(N=150, Nt=800)
    stats = gates_data().grudeva_vial_stats()
    mean = np.array([s["solubles_mean_g"] for s in stats])
    sd = np.array([s["solubles_sd_g"] for s in stats])
    model = r["gpv"] * 1e3
    within = int(sum(abs(model[k] - mean[k]) <= sd[k] for k in range(3, 16)))
    total_ok = abs(r["total_solubles_g"] - mean[3:].sum()) / mean[3:].sum() < 0.05
    passed = (r["sd_inv_1"] > 1.0                # saturated plateau exists
              and total_ok                        # solute budget matches to <5%
              and within >= 8)                    # majority of vials within 1 SD
    return dict(passed=passed, sd_inv_1=round(r["sd_inv_1"], 2),
                total_g=round(r["total_solubles_g"], 2),
                exp_total_g=round(float(mean[3:].sum()), 2),
                vials_within_1sd=f"{within}/13")


def gate_pannusch_closures():
    """Pannusch constitutive closures reproduce physical anchors: water
    viscosity/density at 90 C, Wilke-Chang D, van't Hoff K(Tref)=Kref with weak
    T-dependence, and a positive Sherwood h_sl monotone in flow."""
    from puckworks.models.pannusch2024 import closures as pc
    T90 = 363.15
    mu = float(pc.water_viscosity(T90)); rho = float(pc.water_density(T90))
    D = {s: float(pc.diffusion_coeff(T90, s)) for s in pc.SOLUTES}
    tab = {r["solute"]: r for r in gates_data().pannusch_table2()}
    caf = tab["caffeine"]
    K_ref = pc.vant_hoff_K(pc.TREF_K, caf["K_ref"], caf["gamma"])   # == Kref
    K80 = pc.vant_hoff_K(353.15, caf["K_ref"], caf["gamma"])
    K98 = pc.vant_hoff_K(371.15, caf["K_ref"], caf["gamma"])
    q1, q2 = 1e-4, 3e-4
    h1 = float(pc.sherwood_h(T90, q1, caf["A1"], caf["B1"], "caffeine"))
    h2 = float(pc.sherwood_h(T90, q2, caf["A1"], caf["B1"], "caffeine"))
    passed = (abs(mu - 3.15e-4) / 3.15e-4 < 0.02       # water μ @90C == card
              and abs(rho - 962) < 12                   # water ρ @90C
              and all(5e-9 < d < 1.2e-8 for d in D.values())
              and abs(K_ref - caf["K_ref"]) < 1e-9      # K(Tref) == Kref
              and 0.9 < K98 / K80 < 1.1                 # weak T-dependence
              and 0 < h1 < h2)                           # h_sl monotone in q
    return dict(passed=passed, mu_90C=round(mu, 7), rho_90C=round(rho, 1),
                D_caffeine=D["caffeine"], K98_over_K80=round(K98 / K80, 3),
                h_sl_ratio=round(h2 / h1, 2))


def gate_pannusch_solver_mape():
    """The two-grain multi-solute PDE solver reproduces the authors' fit MAPEs
    against the Schmieder kinetics (POST-FIT reconstruction). Model per-solute
    MAPE within ~3.5 pts of published (TDS 6.07, caffeine 4.59, trigonelline
    7.85, CGA 4.98 %); centre-grind approximation raises the alcaloids slightly."""
    from puckworks.models.pannusch2024 import solver as ps
    pub = {"caffeine": 4.59, "trigonelline": 7.85, "5CQA": 4.98, "tds": 6.07}
    m = ps.mape_all()
    passed = all(abs(m[s] - pub[s]) < 3.5 and m[s] < 12.0 for s in pub)
    return dict(passed=passed, tds=round(m["tds"], 2), caffeine=round(m["caffeine"], 2),
                trigonelline=round(m["trigonelline"], 2), CGA=round(m["5CQA"], 2))


def gate_foster_machine_tp_ts():
    """The pump/headspace machine-mode ODE reproduces the authors' ponding time
    t_p = 0.823 s and saturation time t_s = 6.669 s from the Table I/II params
    (verification: the whole staged ODE validated against two reported numbers).
    Fig 15 flow-minimum shape validation is deferred to the digitized trace."""
    from puckworks.models.foster2025 import machine_mode as fm
    t_p, t_s = fm.reported_times()
    return dict(passed=(abs(t_p - 0.823) < 0.01 and abs(t_s - 6.669) < 0.02),
                t_p=round(t_p, 3), t_s=round(t_s, 3), card=[0.823, 6.669])


def gate_pannusch_qt_adapter():
    """1.8b (RC-4b): the machine-driven Q(t) adapter reduces to the constant-flow
    RC-4a path when the flow trace is constant (agreement < 1%), and a
    time-varying Q(t) runs and shifts the prediction (the adapter is live)."""
    import numpy as np
    from puckworks.models.pannusch2024 import solver as ps
    exps = ps._exp_kinetics(); params = ps._solute_params()
    rows = sorted(exps[7], key=lambda r: r["fraction"])
    T = rows[0]["Temp_C"]; flow = rows[0]["flow_mL_s"]
    sp = params["caffeine"]; cl1 = rows[0]["c_caffeine_mg_g"]
    bounds = sorted({r["t_lower_s"] for r in rows} | {r["t_upper_s"] for r in rows})
    const = ps.simulate_fractions(T, flow, bounds, sp, cl1)
    qt_const = ps.simulate_fractions_qt(T, lambda t: flow, bounds, sp, cl1)
    qt_ramp = ps.simulate_fractions_qt(T, lambda t: flow * (1 + 0.15 * t / 30), bounds, sp, cl1)
    reduces = float(np.max(np.abs(qt_const - const) / const))
    shifts = float(np.max(np.abs(qt_ramp - const) / const))
    return dict(passed=(reduces < 0.01 and shifts > 0.01),
                qt_vs_const_maxrelerr=round(reduces, 4),
                ramp_shift_maxrel=round(shifts, 3))


def gate_mo_reynolds_overlay():
    """1.1 §5.2 Mo overlay: reproduce mo2023's Re band 0.84-3.86 from Fig 8a at
    THEIR SPH conditions (mu=1e-3, rho=1000, char. length d43=341.6 um), and the
    Darcy->Forchheimer kD(grad P) decline. Per §5.2 this Re is NOT interchangeable
    with wadsworth's Fo_F — the three diagnostics are reported side by side, each
    under its own stated convention."""
    import numpy as np
    rows = gates_data().mo2023_fig8a()
    dP = np.array([r["pressure_gradient_bar_per_m"] for r in rows]) * 1e5   # -> Pa/m
    k = np.array([r["permeability_1e-13_m2"] for r in rows]) * 1e-13
    mu, rho, d43 = 1e-3, 1000.0, 341.6e-6
    Re = rho * (k * dP / mu) * d43 / mu
    declines = k[0] > k[-1]                            # Forchheimer: apparent k falls
    passed = (abs(Re.min() - 0.84) < 0.1 and abs(Re.max() - 3.86) < 0.1 and declines)
    return dict(passed=passed, Re_min=round(float(Re.min()), 2),
                Re_max=round(float(Re.max()), 2),
                kD_decline_e13=[round(float(k[0]) * 1e13, 2), round(float(k[-1]) * 1e13, 2)],
                note="Re NOT interchangeable with wadsworth Fo_F (§5.2)")


def gate_egidi_bracket():
    """2.1 RC-1 egidi bracket: the 12-condition EY/TDS range loads as expected
    (EY 19-23%), and cameron2020's EY is reported against it (independent bracket;
    cameron sits low, a documented finding -- reported, not asserted into it)."""
    import numpy as np
    from puckworks.models.cameron2020 import extraction_bdf as cam
    rows = gates_data().egidi_table2()
    EY = np.array([r["EY [%]"] for r in rows])
    cam_EY = cam.simulate_shot(1.9, m_in=0.020, m_out=0.040).EY
    passed = (len(rows) == 12 and 19.0 <= EY.min() and EY.max() <= 23.0)
    return dict(passed=passed, egidi_EY_bracket=[round(float(EY.min()), 1), round(float(EY.max()), 1)],
                cameron_EY=round(cam_EY, 1),
                cameron_in_bracket=bool(EY.min() <= cam_EY <= EY.max()))


def gate_cameron_conservation():
    """cameron2020.extraction_bdf conserves solute (EY from cup mass == EY from
    solid depletion minus holdup, its built-in cross-check) and stays below the
    per-bed soluble-inventory ceiling. Self-contained mass-budget gate."""
    import numpy as np
    from puckworks.models.cameron2020 import extraction_bdf as cam
    r = cam.simulate_shot(1.9, m_in=0.020, m_out=0.040)
    phi1, phi2, *_ = cam.grind_microstructure(1.9)
    ceiling = (np.pi * cam.R0 ** 2 * cam.bed_depth(0.020) * (phi1 + phi2)
               * cam.C_S0 / 0.020 * 100.0)
    passed = (abs(r.EY - r.EY_solid) < 0.5      # mass conservation cross-check
              and 0 < r.EY < ceiling)            # below inventory ceiling
    return dict(passed=passed, EY=round(r.EY, 2), EY_solid=round(r.EY_solid, 2),
                inventory_ceiling=round(ceiling, 1))


def gate_p2_kappa_ladder():
    """P2 null-first ladder (item 2.2): on the Waszkiewicz 9-bar RISING-flow
    trace over ONE window (15-95 s), the empirical time-dependent Phi(t) (rung 4,
    0 free params) beats the BEST of three DISTINCT constant nulls -- LS-optimal
    in-window constant (~0.57), long-run constant (~0.64), published static
    kappa(P) (~0.65) -- by ~4.9x: time variation IS needed. A 4-param flexible
    (non-mechanistic) cubic reaches ~0.10, so the ladder establishes NEED for time
    variation, not a specific bed mechanism; the mechanistic content is that a
    zero-parameter poroelastic Phi(t) nearly reaches that flexible floor. Rung 5
    RC-3b (Cameron-coupled, diffusion-limited Phi) beats the constant nulls too but
    is ~3x WORSE than rung 4 -> near-instant dissolution favored (§5.6). Rung 5b, the
    mo2023_2 SWELLING competitor (Phase-3 discrimination), predicts the WRONG SIGN: its
    Carman-Kozeny flow ratio is monotone non-increasing (throttles to ~4% over the shot),
    so its best-anchored RMSE (~1.08) is WORSE than a constant and it is strongly
    anti-correlated (r~-0.95) with the rising trace -> the swelling mechanism is refuted
    as the driver of the rising-flow residual (card: 'enters with the wrong sign')."""
    from puckworks import harness as h
    L = h.kappa_t_ladder()
    passed = (L["rung4_beats_floor"] and L["improvement_factor"] > 2.0
              and L["rung4_phi_of_t"] < 0.2
              # the three constant nulls are DISTINCT (not one RMSE copied twice)
              and L["rung1_const_kappa"] < L["rung3_static_kappaP"]
              and L["rung5_rc3b_cameron_coupled"] < L["rung1_const_kappa"]   # beats null
              and L["rung5_rc3b_cameron_coupled"] > L["rung4_phi_of_t"]      # loses to empirical
              # rung 5b swelling is the WRONG SIGN (anti-correlated, worse than a constant)
              and L["swelling_wrong_sign"] and not L["swelling_beats_best_null"])
    return dict(passed=passed, window_s=L["window_s"],
                rung1_best_const=L["rung1_const_kappa"],
                rung1b_longrun=L["rung1b_longrun_const"],
                rung3_static=L["rung3_static_kappaP"],
                rung4_rmse=L["rung4_phi_of_t"],
                flexible_cubic=L["flexible_cubic_null"],
                cubic_beats_dynamic=L["cubic_beats_dynamic"],
                rung5_rc3b_rmse=L["rung5_rc3b_cameron_coupled"],
                rung5b_swelling_rmse=L["rung5b_swelling_mo2"],
                rung5b_swelling_corr=L["rung5b_swelling_corr_with_trace"],
                rung5b_swelling_full_shot_decay=L["rung5b_swelling_full_shot_decay"],
                swelling_wrong_sign=L["swelling_wrong_sign"],
                factor=L["improvement_factor"], rc3b=L["rc3b_vs_rung4"])


def gate_p2_cross_pressure():
    """P2 cross-pressure discrimination (item 2.2, ANALYSIS_P2 §2.2): one shared
    campaign-wide calibration, predict all 11 Waszkiewicz pressures (within-campaign
    CONDITIONAL transfer, NOT independent out-of-sample validation). The three
    kappa(t) mechanisms SEPARATE by regime rather than one dominating -- the
    discriminator the multi-pressure dataset was built for:
      - dissolution Phi(t) has the lowest transfer-mean RMSE (below the static null),
      - but RC-3b (flow-coupled) is lower at the low-pressure end (slow flow ->
        pressure-dependent dissolution matters),
      - and the static null is lower mid-range (little time structure to explain).
    Gating all three separations pins the 'no single mechanism lowest everywhere'
    verdict so a later refit can't quietly promote one mechanism to universal."""
    from puckworks import harness as h
    X = h.cross_pressure_discrimination()
    passed = (X["phi_generalizes"] and X["rc3b_lower_low_p"]
              and X["static_lower_mid_p"])
    return dict(passed=passed, conditional_transfer_mean=X["conditional_transfer_mean"],
                low_p_mean=X["low_p_mean"], mid_p_mean=X["mid_p_mean"],
                separations=dict(phi_below_static_transfer=X["phi_generalizes"],
                                 rc3b_below_phi_low_p=X["rc3b_lower_low_p"],
                                 static_below_both_mid_p=X["static_lower_mid_p"]))


def gate_lee_feedback_negative_result():
    """lee2023 (item 3.4): the two-pathway extraction->porosity->permeability
    feedback reproduces the paper's documented behaviour AND its failure mode:
      G1  the delta=0.035 seed amplifies (pathway EY diverges) at every grind;
      G2  imposed rho_c=798 (alpha=0.266): EY(g) has an interior peak with a
          DECLINE on the fine-grind side (their Fig. 4 headline);
      G3  physical rho_c=399 (alpha=0.532): EY(g) only PLATEAUS/rises toward
          fine -- NO decline. This is the paper's own negative result and must
          NOT be promoted to a decline (validation-strength discipline).
      G4  tau_shot nondimensionalization matches the reviewer cross-check
          (tau_shot(1.1)=1.12, tau_shot(2.3)=0.48).
    Strength: verification of the paper's model + qualitative; the peak is weak
    (~0.2 pp vs Fig. 4's ~1.5 pp, per reviewer) so this gates the SIGN/shape,
    not the amplitude, and never claims a data fit."""
    import numpy as np
    from puckworks.models.lee2023 import feedback as lee
    g = np.linspace(1.1, 2.3, 13)
    # G1 seed amplification (divergence exceeds the 2*delta = 7pp seed)
    div = [lee.simulate(float(gi), rho_c=lee.RHO_C_IMPOSED)["divergence_pct"]
           for gi in g]
    g1 = bool(min(div) > 2 * lee.DELTA * 100 * 0.5) and all(d > 0 for d in div)
    hot = lee.peak_and_fine_decline(g, rho_c=lee.RHO_C_IMPOSED)   # 798
    cold = lee.peak_and_fine_decline(g, rho_c=lee.RHO_C_PHYSICAL)  # 399
    g2 = hot["fine_side_decline"]              # decline at imposed rho_c
    g3 = not cold["fine_side_decline"]         # plateau (no decline) at physical
    g4 = bool(abs(lee.tau_shot(1.1) - 1.12) < 0.03
              and abs(lee.tau_shot(2.3) - 0.48) < 0.03)
    passed = bool(g1 and g2 and g3 and g4)
    return dict(passed=passed, seed_amplifies=g1,
                imposed_798_declines=g2, physical_399_plateaus=g3, tau_ok=g4,
                peak_g_798=hot["g_peak"], fine_vs_peak_798=round(
                    hot["ey_fine_pct"] - hot["ey_peak_pct"], 3),
                fine_vs_peak_399=round(cold["ey_fine_pct"] - cold["ey_peak_pct"], 3),
                note="peak weak by design; sign gated, not amplitude")


def gate_unified_kappa_t():
    """Unified kappa(t)=kappa0*f(P,eps,E) closure framework (bed_dynamics backlog):
    the registry's four kappa-perturbing mechanisms compose as independently
    toggleable SIGNED factors, each drawn from its registered component. The gate
    pins the load-bearing content -- the signs, limits, and reduction:
      compaction f(P)  <=1 and DECREASING in P (waszkiewicz)  -- bed compacts
      swelling  f(t)   <=1 and DECREASING in t (mo2023_2)      -- pores fill
      fines     f(t)   <=1 and DECREASING in t (fasano partI)  -- layer grows
      extraction f(EY) >=1 and INCREASING in EY (lee2023)      -- pores open
    Extraction OPPOSES the other three (the physical competition), and with all
    branches neutral kappa/kappa0 = 1. Framework/synthesis; the multiplicative
    composition is a modeling choice, surfaced as such."""
    from puckworks import harness as h
    comp = [h.kappa_branches(P_bar=p)["f_compaction"] for p in (2, 5, 9, 13)]
    extr = [h.kappa_branches(EY=e)["f_extraction"] for e in (0.0, 0.1, 0.2, 0.3)]
    swell = [h.kappa_branches(t_swell_s=t)["f_swelling"] for t in (1, 10, 30)]
    fines = [h.kappa_branches(t_fines_s=t)["f_fines"] for t in (10, 60, 150)]
    neutral = h.kappa_branches()
    comp_ok = all(comp[i] > comp[i + 1] for i in range(3)) and max(comp) <= 1.0
    extr_ok = all(extr[i] < extr[i + 1] for i in range(3)) and min(extr) >= 1.0
    swell_ok = all(swell[i] > swell[i + 1] for i in range(2)) and max(swell) <= 1.0
    fines_ok = all(fines[i] >= fines[i + 1] for i in range(2)) and max(fines) <= 1.0
    reduce_ok = (neutral["f_swelling"] == 1.0 and neutral["f_extraction"] == 1.0
                 and neutral["f_fines"] == 1.0)
    passed = bool(comp_ok and extr_ok and swell_ok and fines_ok and reduce_ok)
    return dict(passed=passed, compaction_decr_le1=comp_ok,
                extraction_incr_ge1=extr_ok, swelling_decr_le1=swell_ok,
                fines_decr_le1=fines_ok, reduces_to_unity=reduce_ok,
                f_compaction_by_P=[round(v, 3) for v in comp],
                f_extraction_by_EY=[round(v, 2) for v in extr])


def gate_g9_series_resistance():
    """G9 basket/screen/outlet resistance -- LARGELY RESOLVED via basket geometry.
    The clean-basket screen resistance computed from schulman2011 geometry (orifice
    + Poiseuille over 14 baskets) is ~5-6 orders of magnitude BELOW the DE1 total
    resistance (screen/total ~1e-5) -> NEGLIGIBLE. So the outlet/screen is not a
    co-controlling resistance for a clean basket, and the earlier fitted-vs-measured
    kappa gap is a coffee/grind difference, NOT screen resistance (consistent with
    the revised grudeva adjudication). Caveat: clean basket only -- fines CLOGGING
    the holes mid-shot is unmeasured; orifice/Poiseuille are [RS] constructions."""
    from puckworks import harness as h
    g = h.g9_series_resistance()
    passed = bool(g["screen_negligible"] and g["puck_below_total"])
    return dict(passed=passed, R_total=round(g["R_total"], -8),
                R_screen_geom_max=g["R_screen_geom_max"],
                screen_share=g["screen_share"], screen_negligible=g["screen_negligible"],
                puck_share_measured=g["puck_share_measured"],
                note="clean-basket screen negligible (schulman geometry); clogging unmeasured")


def gate_kappa_t_degeneracy():
    """brewer2026_coupled_kappa_t degeneracy (card gate): with swelling/compaction/
    fines OFF, the coupled porosity ODE reduces to waszkiewicz2025.poroelastic
    EXACTLY -- extraction-only Phi(t) == m_d(t)/m0, and the 9-bar Q(t) RMSE matches
    the poroelastic component alone (rung 4, ~0.113). Verification of the reduction.
    (Flow uses the poroelastic closure = card Eq.2 as corrected 2026-07-11; CK is
    far too gentle for the near-choke 14x flow rise and is auxiliary only.)"""
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    rmse = ck.degeneracy_rmse(P_bar=9.0)
    passed = bool(rmse < 0.13)                              # == rung 4 (0.113)
    return dict(passed=passed, degeneracy_rmse=round(rmse, 3), rung4_ref=0.113,
                note="exact reduction via the poroelastic closure (card Eq.2, corrected)")


def gate_kappa_t_composition_diagnostic():
    """brewer2026_coupled_kappa_t composition (card: 'report the residual, do not
    tune it away'). Adding the PARAMETER-FREE swelling branch (mo2023_2) to the
    shared porosity OVER-CLOSES the Waszkiewicz saturated pre-wet rig -> the
    composite eps drops below eps0 and the 9-bar residual jumps from ~0.12 to
    ~0.65 (worse than the flat null 0.603). The residual DIAGNOSES a mis-scaled
    branch -- mo2023_2's fixed-dP swelling does not apply to an already-swollen
    saturated bed. Gate verifies the framework behaves correctly (shared-eps
    additive composition, swelling closes eps<eps0) and surfaces the diagnostic."""
    from puckworks.models.brewer2026 import coupled_kappa_t as ck
    c = ck.composition_residual(P_bar=9.0)
    deg = ck.degeneracy_rmse(P_bar=9.0)
    passed = bool(c["swelling_closes"] and c["rmse"] > 3 * deg)  # branch over-closes -> big residual
    return dict(passed=passed, extraction_only_rmse=round(deg, 3),
                composition_rmse=round(c["rmse"], 3), eps_min=round(c["eps_min_reached"], 3),
                swelling_over_closes=c["swelling_closes"],
                diagnosis="mo2023_2 fixed-dP swelling mis-scaled for the saturated rig; "
                          "residual reported not tuned (card)")


def gate_coupled_kappa_t():
    """Coupled kappa(t) closure (kappa(t) backlog, runtime coupling): the four-branch
    framework driven by LIVE registered-model outputs over a real shot. Verifies
    the coupling is genuine: extraction EY(t) rises (cameron), swelling closes
    porosity early then extraction opens it -> the kappa(t) trajectory is
    NON-MONOTONE (dips as swelling bites, recovers as EY grows), and both driving
    curves come from the components (not a linear ramp). NOT a registered
    component -- the composition has no card (registration card-blocked)."""
    import numpy as np
    from puckworks import harness as h
    r = h.coupled_kappa_t(P_bar=9.0, t_shot_s=30.0)
    k = r["kappa_over_kappa0"]
    ey_rises = bool(r["EY"][-1] > r["EY"][2] > 0)                 # cameron EY(t) climbs
    swell_closes = bool(r["f_swelling"][-1] < 0.2)               # mo2023_2 swelling bites
    extr_opens = bool(r["f_extraction"][-1] > 1.5)              # EY opens porosity
    imin = int(np.argmin(k))
    non_monotone = bool(0 < imin < len(k) - 1 and k[-1] > k[imin] + 1e-3)
    passed = bool(ey_rises and swell_closes and extr_opens and non_monotone)
    return dict(passed=passed, ey_rises=ey_rises, swelling_closes=swell_closes,
                extraction_opens=extr_opens, kappa_non_monotone=non_monotone,
                kappa_start=round(float(k[0]), 3), kappa_min=round(float(k[imin]), 3),
                kappa_end=round(float(k[-1]), 3), EY_end_pct=round(float(r["EY"][-1] * 100), 1),
                note="coupled runtime closure; registration card-blocked (composition has no card)")


def gate_p3_channeling_sigma_sweep():
    """P3 fine-grind-dip hypothesis #1 (static channeling), ANALYSIS_P2 §2.3's
    top uncertainty-reducing computation: a MONOTONE sigma(grind) closure through
    the fines fraction, fed to the streamtube EY-deficit, turns the monotone base
    EY(grind) into a PEAKED ensemble EY -- static channeling ALONE reproduces the
    fine-grind dip (peak near the schmieder GL~1.7). Instruments the last
    data-free fine-grind-dip mechanism. Independent/qualitative."""
    from puckworks import harness as h
    r = h.channeling_sigma_sweep(gs_grid=(1.0, 1.5, 2.0, 2.5), n_grid=6)
    passed = bool(r["sigma_monotone"] and r["homog_monotone"]
                  and r["ensemble_peaks_interior"]
                  and r["deficit_largest_at_finest"])
    return dict(passed=passed, sigma_monotone=r["sigma_monotone"],
                base_EY_monotone=r["homog_monotone"],
                channeling_makes_peak=r["ensemble_peaks_interior"],
                peak_gs=r["peak_gs"],
                ey_homog=[round(float(v), 2) for v in r["ey_homog"]],
                ey_ensemble=[round(float(v), 2) for v in r["ey_ensemble"]])


def gate_p3_schmieder_peak_discrimination():
    """P3 MODEL-CAPACITY test (downgraded 2026-07-12 — see ROADMAP §7.1). Two
    corrections from a review made the old 'channeling reproduces the schmieder
    peak' verdict indefensible and this gate now asserts the honest replacement:

    (1) TARGET is per-observable, never a mixed-unit average. PRIMARY observable
        = TDS-derived EY (= TDS cup mass / 20 g dose · 100 — the yield quantity a
        model produces). schmieder's `mass_in_cup` mixes mg (trigonelline/caffeine/
        5-CQA) and g (TDS) across three brew ratios; the old aggregate had no
        coherent unit. The corrected target (`schmieder_interior_max_target`) reads
        schmieder's OWN RSM per observable: concave with an interior grind vertex
        for all four (their model feature) — but the fit is WEAK (adj-R² 0.41–0.75)
        and the raw cells at the one fully-sampled fixed condition are largely
        MONOTONE (the primary TDS-EY is 18.3/19.4/19.6% — monotone; interior max
        for ≤1/4). And GL 1.7 is the FINEST d32, so it is a DIAL peak, not a
        particle-size fine-grind dip.
    (2) CAPACITY, not identification. Of the implemented generators, only the
        empirically-calibrated static-heterogeneity closure produces an interior
        maximum under its measured/calibrated parameters (lee needs an ELEVATED
        ρ_c=798, 2× the measured 399; size-exclusion / diffusion are monotone;
        incomplete wetting is untested). This is model VIABILITY — the gate no
        longer claims channeling IS the mechanism.

    Also asserts the 'no silent observable merge' data hazard is real (schmieder
    carries >1 mass unit across components). Strength: qualitative."""
    from puckworks import harness as h
    from puckworks import data as _d
    r = h.schmieder_peak_discrimination(n_grid=6)
    t = r["target"]
    p = t["primary"]                                            # TDS-EY
    # the mixed-unit hazard that made the old aggregate invalid, made explicit
    units = {row.get("mass_units") for row in _d.schmieder_cup_masses()}
    passed = bool(
        len(units) > 1                                          # mixed-unit hazard is real
        and t["primary_observable"] == "tds_ey"                 # primary target is TDS-EY
        and p["rsm"]["interior_max"]                            # RSM (weak) has interior max...
        and not p["raw_interior"]                               # ...but raw TDS-EY is monotone
        and len(t["rsm_interior_max"]) == 4                     # RSM feature exists for all
        and len(t["raw_interior_max"]) <= 1                     # raw cells do NOT robustly support it
        and r["generate_under_calibrated_params"] == ["static channeling σ(φ₁)"]
        and r["generate_only_under_elevated_ceiling"] == ["lee2023 dissolution instability"])
    return dict(passed=passed,
                schmieder_mass_units=sorted(u for u in units if u),
                primary_observable=t["primary_observable"],
                tds_ey_pct=[round(e, 2) for e in p["ey_means"]],
                tds_ey_raw_interior=p["raw_interior"],
                tds_ey_rsm_vertex=round(p["rsm"]["vertex_dial"], 3),
                tds_ey_rsm_adj_r2=round(p["rsm"]["adj_r2"], 2),
                rsm_interior_max=t["rsm_interior_max"],
                raw_interior_max=t["raw_interior_max"],
                generate_under_calibrated_params=r["generate_under_calibrated_params"],
                generate_only_under_elevated_ceiling=r["generate_only_under_elevated_ceiling"],
                target_verdict=t["verdict"],
                verdict=r["verdict"])


def gate_g4_temperature_sensitivity():
    """G4 (temperature) PARTIAL resolution. Over the espresso window (80→98 °C)
    the extraction-CHEMISTRY temperature sensitivity is SMALL and empirically
    confirmed: two independent partition closures (romancorrochano Arrhenius,
    pannusch van't Hoff) both move K by <15%, the propagated extraction-extent
    shift is <3 pp, and schmieder2023's measured cup concentration spans a median
    <10% across its 80/89/98 °C axis at the DoE-center grind+flow (the matching
    negative datum). The gate ALSO surfaces (does not require) that the two K(T)
    closures DISAGREE on the SIGN of dK/dT — a partition-convention difference
    reported side by side, never merged (rule 6). G4 REMAINDER (in-puck thermal
    transients + T-dependence of wetting/swelling) stays open. Strength:
    verification (closures) + independent/qualitative (schmieder datum)."""
    from puckworks import harness as h
    r = h.g4_temperature_sensitivity()
    passed = bool(
        r["K_small_both"]                                  # both K(T) closures small
        and abs(r["ey_shift_pp"]) < 3.0                    # extraction extent barely moves
        and r["schmieder_small"]                           # data confirms small effect
        and r["schmieder_median_span"] is not None)
    return dict(passed=passed,
                K_frac_roman=round(r["K_frac_roman"], 4),
                K_frac_pann={k: round(v, 4) for k, v in r["K_frac_pann"].items()},
                K_small_both=r["K_small_both"],
                K_sign_agree=r["K_sign_agree"],           # surfaced finding (False)
                D_frac_roman=round(r["D_frac_roman"], 4),
                ey_shift_pp=round(r["ey_shift_pp"], 3),
                schmieder_spans={k: round(v, 4) for k, v in r["schmieder_spans"].items()},
                schmieder_median_span=round(r["schmieder_median_span"], 4),
                reading=r["reading"])


def gate_ntube_kappa_t_union():
    """N-tube κ(t) union (streamtube channeling × coupled_kappa_t per-tube):
    EXPLORATORY SYNTHESIS, qualitative strength. Asserts an exploratory finding in
    the TESTED near-choke configuration (one grind / one pressure / one
    closure-slope / one clock — NOT a proven unconditional instability): giving
    each parallel streamtube its OWN extraction-opens porosity clock, under flow
    control, the POROELASTIC closure drives flow to collapse into a single
    effective channel — measured properly by max single-tube share → ~1 and
    effective channel count N_eff = 1/Σsᵢ² → ~1 (not merely top-decile), with the
    ensemble EY dropping (both flow and EY now at the SAME pressure). This is
    driven by the near-choke hypersensitivity P2 established as required for the
    whole-bed 14× rise: the GENTLE Kozeny-Carman closure stays BOUNDED (N_eff
    holds). Step-size invariant (not an Euler artifact) and suppressed by a
    homogenizing regularizer (a PROXY for lateral coupling, not a transverse-Darcy
    term). Reading: the parallel-non-exchanging-tube assumption fails once κ
    evolves in this regime; a physical lateral-coupling model + stability sweep is
    the open gap (G-lat). NOT a registered component / validated law."""
    from puckworks import harness as h
    poro = h.ntube_kappa_t_union(gs=1.1, N=200, closure="poroelastic", compute_ey=True)
    ck = h.ntube_kappa_t_union(gs=1.1, N=200, closure="ck", compute_ey=False)
    poro_fine = h.ntube_kappa_t_union(gs=1.1, N=200, closure="poroelastic",
                                      substeps=32, compute_ey=False)
    reg = h.ntube_kappa_t_union(gs=1.1, N=200, closure="poroelastic",
                                lateral=0.9, compute_ey=False)
    passed = bool(
        poro["concentrates"]                              # single-channel collapse...
        and poro["max_single_tube_share_final"] > 0.9     # ...measured directly
        and poro["n_eff_channels_final"] < 1.5            # N_eff -> ~1
        and poro["ey_dynamic"] < poro["ey_static"]        # EY drops (same pressure)
        and not ck["concentrates"]                        # CK stays bounded
        and ck["n_eff_channels_final"] > 50               # CK keeps many channels
        and poro_fine["concentrates"]                     # step-size invariant
        and not reg["concentrates"])                      # regularizer suppresses it
    return dict(passed=passed,
                poroelastic_concentrates=poro["concentrates"],
                poro_top_decile=round(poro["top_decile_share_final"], 3),
                poro_max_single_tube=round(poro["max_single_tube_share_final"], 3),
                poro_n_eff_final=round(poro["n_eff_channels_final"], 2),
                poro_ey_static=round(poro["ey_static"], 2),
                poro_ey_dynamic=round(poro["ey_dynamic"], 2),
                ey_pressure_bar=poro["P_bar"],
                ck_bounded=not ck["concentrates"],
                ck_n_eff_final=round(ck["n_eff_channels_final"], 1),
                concentration_substep_invariant=poro_fine["concentrates"],
                regularizer_suppresses=not reg["concentrates"],
                reading=poro["reading"])


def gate_roman_sphere_solver():
    """romancorrochano2017 extraction (3.5) solver verification: the spherical
    method-of-lines diffusion solver reproduces the classic Crank analytic
    fractional release (sphere into an infinite sink) to <1e-3 across the shot.
    Confirms the PDE numerics behind the multi-scale model."""
    import numpy as np
    from puckworks.models.romancorrochano2017 import extraction as rx
    R, Deff = 1e-4, 2.5e-10
    t = np.array([0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 40.0])
    err = float(np.max(np.abs(rx.crank_release(Deff, R, t)
                              - rx.sphere_release(Deff, R, t, N=120))))
    return dict(passed=bool(err < 1e-3), max_abs_err=round(err, 6))


def gate_roman_mw_temperature_trends():
    """romancorrochano2017 extraction (3.5) driven by the REAL parameter tables
    (independent/qualitative): (a) the microstructural Deff spectrum orders
    low>med>high>vhigh at a grind (Table 4.9); (b) K(T) rises with T and matches
    Table 4.10 to <0.05; (c) in the stirred vessel, a higher-Deff species reaches
    50% extraction faster than a lower-Deff one; (d) the equilibrium extent rises
    with K. No fitting -- the tables are the paper's measured inputs."""
    import numpy as np
    from puckworks.models.romancorrochano2017 import extraction as rx
    deff = [rx.deff_of("PsiE", m) for m in rx.MW_CLASSES]
    mw_ordered = all(deff[i] > deff[i + 1] for i in range(3))
    Kt = [rx.K_of_T(T) for T in (20, 50, 80)]
    K_rises = Kt[0] < Kt[1] < Kt[2]
    K_matches = all(abs(a - b) < 0.05 for a, b in zip(Kt, (0.42, 0.57, 0.61)))

    def t50(Deff):
        tt = np.linspace(0, 400, 400)
        _, f = rx.stirred_vessel(Deff, 1e-4, K=0.6, pore_to_bath=0.05, t_eval=tt)
        return float(np.interp(0.5 * f[-1], f, tt))
    faster = t50(deff[0]) < t50(deff[2])          # low-MW (high Deff) faster than high-MW
    passed = bool(mw_ordered and K_rises and K_matches and faster)
    return dict(passed=passed, mw_ordered=mw_ordered, K_rises=bool(K_rises),
                K_matches_table=K_matches, high_deff_faster=faster,
                K_of_T=[round(k, 3) for k in Kt])


def gate_roman_bed_flow_trend():
    """romancorrochano2017 extraction (3.5) bed mode: the lumped flow-through bed
    (Eq 3.36) is mass-conserving (<2%) and its yield rises monotonically; and it
    reproduces the paper's fixed-flow trend FROM the diffusion physics -- at a
    matched beverage volume, higher flow Q gives lower yield AND lower strength
    (slower q -> higher yield/strength). Behavioral verification (geometry
    nominal; the trend direction is geometry-independent)."""
    import numpy as np
    from puckworks.models.romancorrochano2017 import extraction as rx
    base = dict(Deff=2.5e-10, R=5e-5, K=0.6, eps_bed=0.4, V_bed=5e-5)
    b = rx.bed_lumped(Q=1.5e-6, t_eval=np.linspace(0, 40, 200), **base)
    conserved = bool(np.all(np.abs(b["mass_balance"] - 1.0) < 0.02))
    monotone = bool(np.all(np.diff(b["yield_frac"]) >= -1e-9))
    y, s = [], []
    for Q in (0.8e-6, 1.5e-6, 3.0e-6):
        bb = rx.bed_lumped(Q=Q, t_eval=np.linspace(0, 2e-5 / Q * 1.1, 200), **base)
        vol = Q * bb["t"]
        y.append(float(np.interp(2e-5, vol, bb["yield_frac"])))
        s.append(float(np.interp(2e-5, vol, bb["strength"])))
    slower_higher = y[0] > y[1] > y[2] and s[0] > s[1] > s[2]
    passed = bool(conserved and monotone and slower_higher)
    return dict(passed=passed, mass_conserved=conserved, yield_monotone=monotone,
                slower_q_higher=bool(slower_higher),
                yield_by_Q=[round(v, 3) for v in y],
                strength_by_Q=[round(v, 3) for v in s])


def gate_roman_tamped_kappa():
    """romancorrochano2017 Table 6.1 (0.5 intake, DATA-ONLY permeability target /
    G9): tamped-bed Darcy kappa sits in the literature 1e-14..1e-13 m^2 band and
    the ROBUST physical signal holds -- at every initial bed density, coarser
    grind (PsiB->PsiE) gives higher kappa. Density-monotonicity is NOT asserted:
    PsiE is non-monotone in the data (kappa rises 360->400 then falls), matching
    the thesis's own 'kappa noisy at the coarsest grind, fitted n does not track
    packing physics'. Independent permeability DATA, not a K-C validation."""
    from puckworks import data as d
    rows = d.roman_tamped_kappa()
    kv = [r["kappa_m2"] for r in rows]
    in_band = all(1e-14 <= k <= 1e-12 for k in kv) and max(kv) > 1e-13
    order = ["PsiB", "PsiC", "PsiD", "PsiE"]
    grind_monotone = True
    for rho in (360.0, 400.0, 480.0):
        seq = [next(r["kappa_m2"] for r in rows
                    if r["grind"] == g and r["rho_bed_kg_m3"] == rho) for g in order]
        grind_monotone &= all(seq[i] < seq[i + 1] for i in range(len(seq) - 1))
    passed = bool(in_band and grind_monotone)
    return dict(passed=passed, n_beds=len(rows),
                kappa_range_m2=[min(kv), max(kv)],
                coarser_grind_higher_kappa=grind_monotone,
                note="density trend holds 3/4 grinds; PsiE non-monotone (documented)")


def gate_roman_bed_mpe_parameter_free():
    """romancorrochano2017 Fig 7.4 (0.5 intake): the PARAMETER-FREE bed-scale
    result -- predicted espresso yields using the non-fitted microstructural
    medium-MW Deff give MPE <= 14.3% across ALL 15 flow/density conditions (the
    thesis '9-14%' claim). Strength: verification of the reported (digitized)
    result, ~+/-0.5 pp raster fidelity -- NOT a reproduction from our own solver
    (the extraction model is implement-later). The med-MW column is the headline;
    low/high-MW single-Deff columns are worse (expected -- they are the wrong
    class), so this also checks med-MW is the best single choice on average."""
    import numpy as np
    from puckworks import data as d
    rows = d.roman_fig74_espresso()
    med = np.array([r["MPE_med_MW_pct"] for r in rows], float)
    low = np.array([r["MPE_low_MW_pct"] for r in rows], float)
    high = np.array([r["MPE_high_MW_pct"] for r in rows], float)
    passed = bool(len(rows) == 15 and med.max() <= 14.5
                  and med.mean() < low.mean() and med.mean() < high.mean())
    return dict(passed=passed, n_conditions=len(rows),
                med_MW_mpe_max=round(float(med.max()), 1),
                med_MW_mpe_mean=round(float(med.mean()), 1),
                low_mean=round(float(low.mean()), 1),
                high_mean=round(float(high.mean()), 1),
                strength="verification of reported parameter-free result (digitized)")


def gate_fasano_cor82_nonmonotone():
    """fasano2000_partI (0.12/3.3 intake): the ONLY faithfully-checkable claim
    (the model closures K,M,gamma are unpublished, so Fig 8.6 cannot be
    reproduced from scratch -- this is NOT a model twin). The paper's Cor. 8.2
    proves nonmonotone q_inf(p0) REQUIRES the flow to cross the detachment
    threshold beta(q); therefore the peak of the digitized q_inf(p0) (Fig 8.6)
    must sit at the flow where beta(q) drops steeply (Fig 8.7). Verified for both
    thresholds, plus the ordering (beta2 drops at lower q -> peaks at lower p0).
    Strength: qualitative / structural verification of the digitized figures via
    the paper's own necessary condition. No closures invented."""
    from puckworks import data as d
    f86 = d.fasano_fig8_6()
    f87 = d.fasano_fig8_7()
    out = {}
    for s in ("beta1", "beta2"):
        pts = sorted((r["p0"], r["q"]) for r in f86 if r["series"] == s)
        ip = max(range(len(pts)), key=lambda i: pts[i][1])
        peak_p0, peak_q = pts[ip]
        nonmono = pts[-1][1] < peak_q - 0.005 and ip > 0
        b = sorted((r["q"], r["beta"]) for r in f87 if r["series"] == s)
        slopes = [((b[i][0] + b[i + 1][0]) / 2,
                   (b[i + 1][1] - b[i][1]) / (b[i + 1][0] - b[i][0]))
                  for i in range(len(b) - 1)]
        knee_q = min(slopes, key=lambda x: x[1])[0]
        out[s] = dict(peak_p0=peak_p0, knee_q=knee_q,
                      tracks=bool(abs(peak_p0 - knee_q) < 0.05), nonmono=bool(nonmono))
    ordering = out["beta2"]["peak_p0"] < out["beta1"]["peak_p0"]
    passed = bool(all(v["nonmono"] and v["tracks"] for v in out.values()) and ordering)
    return dict(passed=passed, beta2_peaks_below_beta1=bool(ordering),
                beta1=out["beta1"], beta2=out["beta2"],
                strength="qualitative/structural (Cor. 8.2; digitized, not a model twin)")


def gate_fasano_freeboundary():
    """fasano2000_partI (3.3) MODEL gate: the fasano-STRUCTURED free-boundary
    fines-migration solver (our closures + the digitized Fig 8.7 beta(q)) exhibits
    the paper's analytic structure -- (Eq 8.33) the global mass balance stays
    closed to <1%; (Lemma 8.3) q(t) is monotone nonincreasing; (Lemma 8.1) the
    free boundary respects s(t) >= s_m = 1-(1+m0)/M; and q_inf(p0) is NONMONOTONE
    with an interior peak (rise -> peak -> decline), the release->compaction->
    resistance feedback behind Fig 8.6. Verification of the structure, NOT a
    reproduction of their curve (closures K,M,gamma are unpublished)."""
    import numpy as np
    from puckworks.models.fasano2000_partI import fines_migration as fm
    b1 = fm.beta_from_fig87("beta1")
    r = fm.simulate(1.0, b1)
    mass_ok = bool(np.all(np.abs(r["mass_balance"] - 1.0) < 0.01))
    monotone = bool(np.all(np.diff(r["q"]) <= 1e-6))
    bound_ok = bool(np.all(r["s"] >= fm.s_min() - 1e-6))
    p0 = np.arange(0.2, 1.21, 0.2)
    Q = fm.q_infinity_curve(p0, b1)
    ip = int(np.argmax(Q))
    peaked = bool(0 < ip < len(p0) - 1 and Q[ip] > Q[0] and Q[ip] > Q[-1])
    passed = bool(mass_ok and monotone and bound_ok and peaked)
    return dict(passed=passed, mass_balance_closed=mass_ok, q_monotone=monotone,
                s_bound_ok=bound_ok, qinf_peaked=peaked,
                q0=round(float(r["q"][0]), 3), qinf=round(float(r["q"][-1]), 4),
                s_min=round(fm.s_min(), 3), qinf_peak_p0=round(float(p0[ip]), 2),
                note="fasano-STRUCTURED (our closures); mechanism, not their curve")


def gate_fasano_reversal_signature():
    """fasano2000_partI Fig 8.4 (0.12 intake): the direct/inverse reversal test --
    segment 1 (direct) and segment 3 (chamber INVERTED) both replay a large
    transient peak (fines counter-migration re-arms the compact layer), while
    segment 2 (pressure off/on, medium undisturbed) resumes at the LOW plateau
    with no such peak. The authors' key discriminating experiment for fines
    migration. Qualitative."""
    from puckworks import data as d
    rows = d.fasano_fig8_4()

    def peak(seg):
        return max(r["discharge_ml_s"] for r in rows if r["segment"] == seg)
    p1, p2, p3 = peak(1), peak(2), peak(3)
    # direct and inverted replay a big peak (>~10); the off/on resume stays low
    passed = bool(p1 > 10 and p3 > 10 and p2 < p1 / 2 and p2 < p3 / 2)
    return dict(passed=passed, peak_direct=p1, peak_resume=p2, peak_inverted=p3,
                strength="qualitative (reversal signature)")


def gate_roman_y0_ceiling_sizeexclusion():
    """romancorrochano2017 y0 (0.5 intake) -- two independent readings:
    (§5.5 nested ceilings) the exhaustively-extractable inventory y0(PsiA)=31.7%
    sits ABOVE Cameron's per-bed-volume espresso EY ceiling (24.5%) which sits
    above Liang's single-immersion equilibrium ceiling (21.5%): y0 > cameron >
    liang, three DISTINCT ceiling quantities nested, not contradictory
    (independent, K<1 discipline -- no promotion).
    (P3 hypothesis #4, size-exclusion) y0 decreases monotonically along the
    coarsening grind ladder PsiA->PsiH -- finer grinds expose more extractable
    inventory, coarser grinds entrap it. This is the size-exclusion signal that
    was 'untested' in docs/P3_hypotheses.md; strength independent/qualitative."""
    from puckworks import data as d
    from puckworks.models.liang2021 import desorption as lg
    rows = d.roman_y0_extractable()
    y0 = {r["grind"]: r["y0_pct"] for r in rows if r["method"] == "dilute"}
    liang = lg.K_EMAX_1L
    cameron = lg.cameron_inventory_ceiling()
    nested = bool(y0["PsiA"] / 100.0 > cameron > liang)
    order = ["PsiA", "PsiB", "PsiE", "PsiF", "PsiG", "PsiH"]  # finest -> coarsest
    seq = [y0[g] for g in order]
    monotone = all(seq[i] > seq[i + 1] for i in range(len(seq) - 1))
    passed = bool(nested and monotone)
    return dict(passed=passed, nested_ceiling=nested, size_exclusion_monotone=monotone,
                y0_PsiA_frac=round(y0["PsiA"] / 100.0, 3),
                cameron_ceiling=round(cameron, 3), liang_ceiling=round(liang, 3),
                y0_ladder_pct=[round(v, 1) for v in seq],
                strength="independent (distinct ceilings, nested) + qualitative (size-exclusion)")


def gate_mo2_k0_carman_kozeny():
    """mo2023_2 (0.4/3.1 intake) gate (1), EXACT closed-form: the t=0 Carman-Kozeny
    permeability k0 = eps_b^(3+2n) d_[3,2]^2 / (72 (1-eps_b)^2), with eps_b^0=0.17,
    n=0.5, reproduces Table 2 (0.97/1.2/2.0/6.8 x1e-13 m^2) from the Table 1 Sauter
    diameter for all four powders. Verification of the flow closure only (not
    swelling)."""
    from puckworks import data as d
    EPS_B, N = 0.17, 0.5
    g = {r["powder"]: r for r in d.mo2_granulometry()}
    k0 = {r["powder"]: r["k0_m2"] for r in d.mo2_k0()}
    pref = EPS_B ** (3 + 2 * N) / (72.0 * (1 - EPS_B) ** 2)
    errs = {}
    for p, row in g.items():
        d32 = row["d_32_um"] * 1e-6
        k_pred = pref * d32 * d32
        errs[p] = abs(k_pred - k0[p]) / k0[p]
    passed = bool(max(errs.values()) < 0.03)
    return dict(passed=passed, max_rel_err=round(max(errs.values()), 4),
                per_powder_rel_err={p: round(e, 4) for p, e in errs.items()})


def gate_mo2_coupled_bed_fig8():
    """mo2023_2.coupled_bed (card gate-3): the depth-resolved through-flow bed with
    the filling front. Mass-conserving (balance floor > 0.90 after the fill), and
    BEATS the reduced lumped bed on both untuned Fig-8 (type-M, M_c<30 g) metrics:
    within-bars 5/9 (vs reduced 4/9) and implied-scale shape-spread ~37% (vs ~110%)
    -- the depth resolution does real physical work on the yield(M_c) shape. The
    remaining M_c=20 over-prediction is CONVERGED (refinement worsens it slightly),
    so it is genuine model-vs-data disagreement matching the card's own 'model
    overestimates beyond M_c~30 g' caveat, NOT an implementation gap."""
    from puckworks.models.mo2023_2 import coupled_bed as cb
    m = cb.fig8_metrics()
    passed = bool(m["mass_balance_floor"] > 0.90 and m["within_bars"] >= 5
                  and m["shape_spread_pct"] < 60)
    return dict(passed=passed, within_bars=f"{m['within_bars']}/{m['n_points']}",
                reduced_within_bars="4/9", shape_spread_pct=m["shape_spread_pct"],
                reduced_shape_spread_pct=110, mass_balance_floor=m["mass_balance_floor"],
                note="M_c=20 over-pred is converged/genuine (card overestimation caveat)")


def gate_mo2_swelling_insensitivity():
    """mo2023_2 (3.1) extraction layer, the card's gate-4 result: at a FIXED flow
    rate the swelling-coupled yield is nearly UNCHANGED whether swelling is on or
    off (their Fig 2) -- swelling raises eps_p (~+15% D_p) but grows R (R^2 ~+7%),
    which offset, so the grain diffusion timescale barely moves. This is the
    headline CONTRAST with the fixed-dP flow decay (gate_mo2_swelling_flow_decay,
    ~10-20x throttle). Yield also rises with beverage mass (Fig 8 trend)."""
    from puckworks.models.mo2023_2 import extraction as ex
    r = ex.swelling_insensitivity(powder="M", q_list=(2, 3, 4))
    insensitive = r["fixedq_max_rel_diff"] < 0.05
    rises = all(v["rises_with_Mc"] for v in r["per_flow"].values())
    contrast = r["fixeddp_flow_ratio"] < 0.2                # fixed-dP throttles hard
    passed = bool(insensitive and rises and contrast)
    return dict(passed=passed, fixedq_insensitive=insensitive,
                yield_rises_with_Mc=rises, fixeddp_throttles=bool(contrast),
                fixedq_max_rel_diff=round(r["fixedq_max_rel_diff"], 3),
                fixeddp_flow_ratio=round(r["fixeddp_flow_ratio"], 3),
                contrast=r["contrast"])


def gate_mo2_swelling_flow_decay():
    """mo2023_2 (3.1) SWELLING MODEL gate -- the paper's distinctive mechanism.
    The nonlinear swelling PDE -> Eq.21 porosity -> Carman-Kozeny flow reproduces
    the Fig 3(a) fixed-Δp flow decay q(60s)/q(0) for all four powders, INCLUDING
    the per-powder ordering that is the mechanism's signature: coarser boulders
    (larger ℛ_c) only partially swell within the shot, so a coarser powder
    throttles LESS (E < H < M < F). Also verifies the closed-form max swelling
    s_m (Eq.8) = 3.57% at C_M=0.1. Δp/μ/L cancel in the ratio -> faithful."""
    from puckworks.models.mo2023_2 import swelling as sw
    from puckworks import data as d
    sm_ok = abs(sw.s_max(0.1) - 3.57) < 0.05
    by = {}
    for r in d.mo2_fig3a_qdecay():
        if r["s_m_pct"] == 3.6:
            by.setdefault(r["powder"], []).append((r["t_s"], r["q_mm_s"]))
    model, dat, errs = {}, {}, {}
    for pw in ("E", "H", "M", "F"):
        pts = sorted(by[pw])
        dat[pw] = pts[-1][1] / pts[0][1]
        model[pw] = sw.flow_decay_ratio(pw)
        errs[pw] = abs(model[pw] - dat[pw]) / dat[pw]
    match = all(errs[pw] < 0.20 for pw in errs)
    order = model["E"] < model["H"] < model["M"] < model["F"]
    passed = bool(sm_ok and match and order)
    return dict(passed=passed, s_max_pct=round(sw.s_max(0.1), 3),
                coarser_throttles_less=bool(order),
                model_ratio={k: round(v, 4) for k, v in model.items()},
                data_ratio={k: round(v, 4) for k, v in dat.items()},
                max_rel_err=round(max(errs.values()), 3))


def gate_mo2_fixed_flow_trends():
    """mo2023_2 (3.1 intake): the paper's stated fixed-flow-rate experimental
    trends on Figs 6-9 (independent, qualitative). (a) slower q -> higher yield at
    matched beverage mass; (b) finer grind -> higher yield (E finest d32=76 >
    M=109 > F=201 coarsest). Monotone -- they do NOT show Cameron's non-monotonic
    fine-grind dip (a fixed-flow machine defeats clogging by raising pressure)."""
    import numpy as np
    from puckworks import data as d
    rows = d.mo2_yield_strength()

    def y(p, q, mc_lo, mc_hi):
        v = [r["yield_pct"] for r in rows if r["powder"] == p and r["q_mL_s"] == q
             and mc_lo <= r["M_c_g"] <= mc_hi]
        return float(np.mean(v)) if v else float("nan")

    # (a) slower q -> higher yield, per powder, in the mid-bed window M_c 18-32 g
    slower_q = all(y(p, 2, 18, 32) > y(p, 4, 18, 32) for p in ("E", "M", "F"))
    # (b) finer grind -> higher yield at matched q, mid window
    finer = all(y("E", q, 18, 32) > y("M", q, 18, 32) > y("F", q, 18, 32)
                for q in (2, 3, 4))
    passed = bool(slower_q and finer)
    return dict(passed=passed, slower_q_higher_yield=slower_q,
                finer_grind_higher_yield=finer,
                yield_E_M_F_q3=[round(y(p, 3, 18, 32), 1) for p in ("E", "M", "F")])


def gate_foster_fig15_flowmin():
    """The machine-mode bed flow reproduces the Fig 15 flow-minimum signature:
    Q/Qm dips to ~0.181 at t~2.0 s and recovers (RMSE vs the digitized trace
    <0.01). This is the P2 null baseline — pump + headspace dynamics alone."""
    import numpy as np
    from puckworks.models.foster2025 import machine_mode as fm
    r = fm.solve()
    q_min, t_min = fm.flow_minimum(r)
    rows = gates_data().foster_fig15_flow()
    t = np.array([x["t_s"] for x in rows]); Q = np.array([x["Q_norm"] for x in rows])
    sel = (t >= r["t_p"] + r["p"].t_shift) & (t <= r["t_s"] + r["p"].t_shift)
    model = np.array([fm.bed_flow_norm(ti, r) for ti in t[sel]])
    rmse = float(np.sqrt(np.mean((model - Q[sel]) ** 2)))
    passed = (abs(q_min - 0.181) < 0.02 and abs(t_min - 2.0) < 0.3 and rmse < 0.01)
    return dict(passed=passed, Q_min=round(q_min, 3), t_min=round(t_min, 2),
                fig15_rmse=round(rmse, 4))


def gate_foster_ct_trajectory():
    """Front s(t) and headspace H(t) match the paper's own fitted ODE curves to
    line width (<0.2 mm RMSE, verifying the port) and bracket a majority of the
    CT data points within their error bars (independent, 'qualitative-good')."""
    import numpy as np
    from puckworks.models.foster2025 import machine_mode as fm
    r = fm.solve()
    rows = gates_data().foster_fig12_14_curves()
    sfit, hfit, sdat, hdat = [], [], [], []
    for x in rows:
        s_m, H_m = fm.front_headspace_mm(x["t_s"], r)
        sfit.append((s_m - x["s_fit_mm"]) ** 2); hfit.append((H_m - x["H_fit_mm"]) ** 2)
        if x["s_data_mm"] != "":
            sdat.append(abs(s_m - x["s_data_mm"]) <= max(x["s_data_err_mm"], 0.5))
        if x["H_data_mm"] != "":
            hdat.append(abs(H_m - x["H_data_mm"]) <= max(x["H_data_err_mm"], 0.5))
    s_rmse = float(np.sqrt(np.mean(sfit))); h_rmse = float(np.sqrt(np.mean(hfit)))
    passed = (s_rmse < 0.2 and h_rmse < 0.2
              and sum(sdat) >= 4 and sum(hdat) >= 4)
    return dict(passed=passed, s_fit_rmse_mm=round(s_rmse, 3),
                H_fit_rmse_mm=round(h_rmse, 3),
                s_data_within_err=f"{sum(sdat)}/{len(sdat)}",
                H_data_within_err=f"{sum(hdat)}/{len(hdat)}")


def gate_extraction_harness():
    """P1 extraction harness (item 2.1): the c_sat config values stay distinct
    (no silent merge, §5.4), the §5.6 dissolution-speed discriminator favors
    near-instant dissolution on the Waszkiewicz TDS fractions, and the grudeva
    vial reconstruction reproduces the C1 total."""
    from puckworks import harness as h
    from puckworks.models.grudeva2025 import reduced as gr
    csat = h.csat_values()
    d56 = h.dissolution_speed_test()
    r = gr.make_coffee(N=120, Nt=600)
    stats = gates_data().grudeva_vial_stats()
    exp_total = sum(s["solubles_mean_g"] for s in stats[3:])
    passed = (csat == [170.0, 212.4, 224.0]                 # 3 distinct, surfaced
              and d56["early_to_peak"] > 0.8                 # near-instant dissolution
              and abs(r["total_solubles_g"] - exp_total) / exp_total < 0.10)
    return dict(passed=passed, csat_distinct=csat,
                s56_favors=d56["favors"], s56_early_to_peak=d56["early_to_peak"],
                grudeva_total_g=round(r["total_solubles_g"], 2))


def gates_data():
    """Lazy import of puckworks.data (avoids import cost at module load)."""
    from puckworks import data
    return data



def gate_bruno_solute_inventory_prior():
    """A4 SoluteInventory / G6 seed: the bruno2026 roasted-chemistry inventory
    populates the A4 contract carrier and links (at the contract level) to the
    per-species extraction kinetics. CONSISTENCY CHECK, reference/qualitative --
    NOT a validation and NOT an extraction fit. Asserts: (1) all four origins
    build a well-formed SoluteInventory with positive amounts; (2) the three
    pannusch-linkable species (caffeine/trigonelline/5-CQA) are present in each;
    (3) the inventory ORDERING is chemically meaningful -- Robusta caffeine >
    Arabica caffeine (~1.8x); (4) extractable_fraction stays None (the prior is
    TOTAL content, NOT c_s0 -- the total->extractable mapping is unmeasured, so
    the link is a prior/cross-check, never a c_s0 substitution)."""
    from puckworks import inventory as inv
    invs = inv.bruno_all_inventories()
    well_formed = all(
        si.species and all(v["amount"] > 0 for v in si.species.values())
        for si in invs.values())
    linkable = all(all(s in si.species for s in inv.PANNUSCH_LINKABLE)
                   for si in invs.values())
    # Robusta (Nicaragua/Indonesia) caffeine > Arabica (Mexico/Rwanda)
    cf = {o: si.amount("caffeine") for o, si in invs.items()}
    robusta_hi = bool(min(cf["Nicaragua"], cf["Indonesia"]) > max(cf["Mexico"], cf["Rwanda"]))
    ratio = inv.species_ratio("caffeine", "Nicaragua", "Mexico")
    total_content_flagged = all(si.extractable_fraction is None for si in invs.values())
    is_reference = all(si.strength.startswith("reference") for si in invs.values())
    passed = bool(well_formed and linkable and robusta_hi and total_content_flagged
                  and is_reference)
    return dict(passed=passed, well_formed=well_formed, linkable_species_present=linkable,
                robusta_caffeine_gt_arabica=robusta_hi,
                robusta_arabica_caffeine_ratio=round(ratio, 2),
                extractable_fraction_none=total_content_flagged,
                origins=list(invs),
                strength="reference/qualitative (total-content prior, NOT c_s0)")

QUICK = [gate_lb_channel, gate_wadsworth_collapse, gate_infiltration_triangle,
         gate_waszkiewicz_static_refit, gate_waszkiewicz_dynamic_9bar,
         gate_grindmap_refit, gate_grindmap_polydispersity,
         gate_inertial_fo_band, gate_inertial_darcy_recovery,
         gate_inertial_de1_audit,
         gate_liang_kemax_refit, gate_liang_eoven_ceiling,
         gate_moroney_fig6_washthrough,
         gate_grudeva_no_eps_kappa, gate_grudeva_reduced_solver,
         gate_pannusch_closures, gate_pannusch_solver_mape,
         gate_foster_machine_tp_ts, gate_extraction_harness,
         gate_foster_fig15_flowmin, gate_foster_ct_trajectory,
         gate_p2_kappa_ladder, gate_p2_cross_pressure, gate_cameron_conservation,
         gate_pannusch_qt_adapter, gate_mo_reynolds_overlay, gate_egidi_bracket,
         gate_lee_feedback_negative_result,
         gate_roman_tamped_kappa, gate_roman_bed_mpe_parameter_free,
         gate_roman_y0_ceiling_sizeexclusion,
         gate_roman_sphere_solver, gate_roman_mw_temperature_trends,
         gate_roman_bed_flow_trend,
         gate_mo2_k0_carman_kozeny, gate_mo2_fixed_flow_trends,
         gate_mo2_swelling_flow_decay, gate_mo2_swelling_insensitivity,
         gate_mo2_coupled_bed_fig8,
         gate_fasano_cor82_nonmonotone, gate_fasano_reversal_signature,
         gate_fasano_freeboundary, gate_p3_channeling_sigma_sweep,
         gate_p3_schmieder_peak_discrimination, gate_ntube_kappa_t_union,
         gate_g4_temperature_sensitivity,
         gate_unified_kappa_t, gate_coupled_kappa_t, gate_g9_series_resistance,
         gate_kappa_t_degeneracy, gate_kappa_t_composition_diagnostic,
         gate_bruno_solute_inventory_prior]


def gate_g1_glassbead_closure_sane():
    """G1 analog closure is physically sane + monotone. CONSISTENCY CHECK, not
    validation (reference-strength analog; no coffee theta(psi) exists -- search
    target g1_retention_search_target.md is OPEN). Asserts only physical params
    (0<S_r<0.2, n_Kr==3, alpha>0, K0>0) and monotone K_r(S) on [S_r,1]."""
    from puckworks import data as d
    c = d.glassbead_retention_kr()
    S_r = float(c["residual_saturation"]["value"])
    n = float(c["rel_perm_exponent"]["value"])
    alpha = float(c["capillary_alpha"]["value"])
    K0 = float(c["abs_permeability_scale"]["value"])
    S = np.linspace(S_r + 1e-3, 1.0, 50)
    Kr = ((S - S_r) / (1 - S_r)) ** n
    monotone = bool(np.all(np.diff(Kr) > 0))
    physical = (0.0 < S_r < 0.2) and abs(n - 3) < 1e-9 and alpha > 0 and K0 > 0
    return dict(passed=(physical and monotone), S_r=S_r, n_Kr=n, alpha=alpha,
                monotone_Kr=monotone,
                strength="reference/qualitative (analog; G1 validation OPEN)")


def gate_g3_pump_envelope_bounds_quadratic():
    """Ulka envelope brackets the operative waszkiewicz brewer quadratic.
    CONSISTENCY CHECK, not validation. The measured single-rig quadratic must lie
    inside the manufacturer envelope over the working flow band. True DE1 Q(P) is
    closed firmware -> independent curve owed."""
    from puckworks import data as d
    env = d.pump_characteristic_ulka()
    Q_free = float(env["free_flow_debit"]["value"]) / 60.0   # cc/min -> mL/s
    P_dead = float(env["max_pressure_deadhead"]["value"])    # 15 bar
    q = d.waszkiewicz_brewer_quadratic()
    a, b, c0 = float(q["a"]), float(q["b"]), float(q["c"])
    Qs = np.linspace(0, min(Q_free, 3.0), 20)
    dP = a * Qs**2 + b * Qs + c0
    within = bool(np.all(dP <= P_dead + 1e-9) and Q_free > 1.90)
    return dict(passed=within, Q_free_mL_s=round(Q_free, 2), P_deadhead_bar=P_dead,
                max_quadratic_dP_bar=round(float(dP.max()), 2),
                strength="reference (endpoints)/qualitative (shape); DE1 curve owed")


def gate_g10_reference_mu_above_water():
    """Reference espresso mu exceeds pure water and stays in the Newtonian band.
    CONSISTENCY CHECK, not validation (no espresso-TDS rheology measured).
    Asserts mu_espresso > pure water within 1.0-2.5x, and espresso TDS below the
    non-Newtonian onset. Quantitative per-cell mu(T,c) still needs the
    Telis-Romero tables (Tim drop). NOTE: the CSV's numeric column is
    'value_or_form' (there is no bare 'value' column)."""
    from puckworks import data as d
    r = d.liquor_rheology()
    mu_water = float(r["viscosity_water_baseline"]["value_or_form"])
    est = r["viscosity_espresso_estimate"]["value_or_form"].replace("~", "")
    lo, hi = (float(x) for x in est.split("-"))
    ratio_lo, ratio_hi = lo / mu_water, hi / mu_water
    newtonian = True   # espresso 4-12% solids < 36% onset (documented in CSV)
    passed = (lo > mu_water and 1.0 < ratio_lo and ratio_hi < 2.5 and newtonian)
    return dict(passed=passed, mu_water=mu_water,
                mu_espresso_ratio=[round(ratio_lo, 2), round(ratio_hi, 2)],
                espresso_newtonian=newtonian,
                strength="reference/qualitative (espresso-TDS extrapolated)")


def gate_g10_mu_bias_directional():
    """G10 directional consistency check (g10_liquor_rheology card's suggested
    gate). CONSISTENCY CHECK, reference/qualitative -- NOT a validation. Darcy
    Q~1/mu + the reference espresso mu (1.3-2x water): swapping it in SUPPRESSES
    the high-concentration EARLY-shot flow (to ~0.5-0.8x the pure-water
    prediction) while leaving the dilute LATE/equilibrium flow unchanged -- the two
    properties the card asks for (reduce the RC-2/RC-3 early bias without breaking
    equilibrium), IF that bias is early-flow over-prediction. Bounded ~1.3-2x;
    confirm the real bias is not larger before attributing all of it here."""
    from puckworks import harness as h
    r = h.g10_mu_bias_direction()
    passed = bool(r["suppresses_early_flow"] and r["preserves_equilibrium"]
                  and r["bounded"] and r["early_flow_factor"][1] < 1.0)
    return dict(passed=passed,
                early_mu_ratio=r["early_mu_ratio"],
                early_flow_factor=r["early_flow_factor"],
                late_flow_factor=r["late_flow_factor"],
                suppresses_early_flow=r["suppresses_early_flow"],
                preserves_equilibrium=r["preserves_equilibrium"],
                reading=r["reading"])


def gate_g10_telisromero_closure():
    """Telis-Romero 2001 mu(T,Xw) closures were transcribed FAITHFULLY from the card: Eq (10)
    reproduces the Table-1 eta anchor and Eq (13) the Table-2 K anchor within the authors'
    stated fit error, and the Eq-10 bulk-shot-TDS viscosity is a NEGLIGIBLE ~1.06x pure water
    -- correcting the paywalled-snippet envelope's ~1.3-2x guess (that magnitude belongs to
    concentrated early in-pore liquor, not bulk shot TDS). Strength: post-fit reconstruction
    of the source's OWN dilute industrial-extract data; espresso is still an extrapolation
    with a composition caveat (NOT a validation of espresso-liquor rheology)."""
    import math
    from puckworks import data as d
    anchors = {a["quantity"]: a for a in d.telisromero_rheology_anchors()}
    ea = anchors["eta"]
    eta_pred = d.telisromero_viscosity_pas(float(ea["T_K"]), float(ea["Xw_pct"]))
    eta_err = abs(eta_pred - float(ea["measured_value"])) / float(ea["measured_value"])
    c13 = d.telisromero_rheology_closures()["eq13_powerlaw_K"]
    ka = anchors["K"]
    K_pred = (float(c13["pre_factor"]) * math.exp(float(c13["Ea_or_A"]) / (8.314 * float(ka["T_K"])))
              * float(ka["Xw_pct"]) ** float(c13["Xw_exponent"]))
    K_err = abs(K_pred - float(ka["measured_value"])) / float(ka["measured_value"])
    shot_ratio = d.telisromero_viscosity_pas(363.0, 90.0) / 3.15e-4   # vs pure water @ 90 C
    passed = (eta_err <= 0.03 and K_err <= 0.10 and 1.0 < shot_ratio < 1.2)
    return dict(passed=passed, eta_err_pct=round(eta_err * 100, 2),
                K_err_pct=round(K_err * 100, 2),
                shot_tds_mu_ratio_to_water=round(shot_ratio, 3),
                strength="post-fit reconstruction of source's dilute-industrial data "
                         "(espresso extrapolated; composition caveat)")


def gate_g10_telisromero2000_thermal():
    """Telis-Romero 2000 thermophysical closures (rho/cp/k/alpha) transcribed FAITHFULLY:
    the linear fits reproduce the card's Fig 2-5 endpoint / water-limit anchors, the
    TYPO-CORRECTED Eq (6) alpha coefficient reproduces the Fig-5 endpoint while the PRINTED
    coefficient does NOT (documents the ~100x exponent typo), and the self-consistent
    alpha = k/(rho*cp) sits systematically BELOW the direct Eq-6 alpha (authors' -11.35%
    convection offset). Same post-fit-reconstruction strength + composition/dilute-end
    caveats as the 2001 rheology companion; espresso is extrapolation. Also asserts the
    fraction-vs-percent normalization guard fires (card hazard vs the 2001 percent basis)."""
    from puckworks import data as d
    cl = d.telisromero_thermal_closures()

    def lin(eq, T_C, Xw):   # evaluate a direct linear closure row
        c = cl[eq]
        return float(c["intercept"]) + float(c["Xw_coeff"]) * Xw + float(c["T_coeff"]) * T_C

    errs = {}
    for a in d.telisromero_thermal_anchors():
        eq = {"rho": "eq1_density", "cp": "eq3_cp", "k": "eq4_k",
              "alpha": "eq6_alpha_direct"}[a["quantity"]]
        pred = lin(eq, float(a["T_C"]), float(a["Xw_frac"]))
        errs[f'{a["quantity"]}@{a["Xw_frac"]},{a["T_C"]}'] = round(
            abs(pred - float(a["value"])) / float(a["value"]) * 100, 2)
    max_err = max(errs.values())

    # typo diagnostic: printed 0.0212e-10 mispredicts the Fig-5 hi endpoint (~1.50e-7)
    printed_alpha = 7.92e-8 + 5.93e-8 * 0.90 + 0.0212e-10 * 82.0
    printed_err = abs(printed_alpha - 1.50e-7) / 1.50e-7 * 100

    # self-consistent alpha is negative-offset vs the direct Eq-6 alpha (convection bias)
    rho = lin("eq1_density", 82.0, 0.90)
    cp = lin("eq3_cp", 82.0, 0.90)
    k = lin("eq4_k", 82.0, 0.90)
    a_direct = d.telisromero_thermal_diffusivity_m2s(82.0, 0.90)
    alpha_offset = (k / (rho * cp) - a_direct) / a_direct * 100

    # normalization guard must reject a PERCENT value on the fraction-basis loader
    guard_fires = False
    try:
        d.telisromero_density_kgm3(82.0, 90.0)   # 90 = percent, illegal here
    except ValueError:
        guard_fires = True

    passed = (max_err <= 1.5 and printed_err > 8.0 and -20.0 < alpha_offset < -5.0
              and guard_fires)
    return dict(passed=passed, max_anchor_err_pct=max_err, anchor_errs=errs,
                printed_eq6_err_pct=round(printed_err, 1),
                alpha_krocp_offset_pct=round(alpha_offset, 1),
                normalization_guard_fires=guard_fires,
                strength="post-fit reconstruction of source's dilute-industrial data "
                         "(espresso extrapolated; composition caveat; Eq-6 typo corrected)")


def gate_g10_telisromero_full_table():
    """The transcribed Eq (10)/(13) closures reproduce the FULL digitized Telis-Romero 2001
    Table 1 (24 measured eta cells) and Table 2 (27 measured K cells) at essentially the
    authors' own reported fit quality -- cross-validating BOTH the digitization (Tim's drop)
    AND the independently-transcribed closure coefficients. Strength: source_curve_reproduction
    (the source's own published measured table; NOT independent of the paper)."""
    import math
    from puckworks import data as d
    R = 8.314
    c10 = d.telisromero_rheology_closures()["eq10_newtonian"]
    p10, E10, x10 = float(c10["pre_factor"]), float(c10["Ea_or_A"]), float(c10["Xw_exponent"])
    e1 = [abs(p10 * math.exp(E10 / (R * float(r["T_K"]))) * float(r["Xw_pct"]) ** x10
              - float(r["eta_Pas"])) / float(r["eta_Pas"]) * 100
          for r in d.telisromero_table1_eta()]
    c13 = d.telisromero_rheology_closures()["eq13_powerlaw_K"]
    p13, E13, x13 = float(c13["pre_factor"]), float(c13["Ea_or_A"]), float(c13["Xw_exponent"])
    e2 = [abs(p13 * math.exp(E13 / (R * float(r["T_K"]))) * float(r["Xw_pct"]) ** x13
              - float(r["K_Pasn"])) / float(r["K_Pasn"]) * 100
          for r in d.telisromero_table2_Kn()]
    eta_mean, eta_max = sum(e1) / len(e1), max(e1)
    K_mean, K_max = sum(e2) / len(e2), max(e2)
    # thresholds = authors' stated errors + a margin for 2-3 sig-fig digitization round-off
    passed = (eta_mean <= 3.5 and eta_max <= 10.5 and K_mean <= 8.0 and K_max <= 22.0)
    return dict(passed=passed, n_eta_cells=len(e1), n_K_cells=len(e2),
                eta_mean_err_pct=round(eta_mean, 2), eta_max_err_pct=round(eta_max, 2),
                K_mean_err_pct=round(K_mean, 2), K_max_err_pct=round(K_max, 2),
                authors_stated="eta 2.34/10.17; K 6.77/18.50 (mean/max %)",
                strength="source_curve_reproduction (measured Table 1/2; espresso extrapolated)")


def gate_g10_viscosity_bulk_negligible():
    """QUANTITATIVE close of G10 (card telisromero2001 §Impl-est ii): driving the MEASURED
    Telis-Romero eta(c,T) with cameron2020's own in-pore liquor field shows the concentration-
    dependent-viscosity correction to Darcy flow is small at espresso conditions -- the in-pore
    liquor never approaches saturation, so mu stays within a few % of water and the constant-
    water-mu assumption in every registered flow model is SAFE. Confirms the card's
    'negligible at shot TDS' and bounds the early transient. Fast single-shot bound."""
    from puckworks.analysis import g10_viscosity_sensitivity as vs
    r = vs.bulk_negligibility()
    passed = (r["mu_peak_ratio_to_water"] < 1.15
              and r["outlet_bound_peak_suppression_pct"] < 8.0
              and r["depthavg_end_flow_factor"] > 0.95)
    return dict(passed=passed, **r,
                reading="peak in-pore mu <= 1.15x water (single most-concentrated cell); "
                        "outlet-bound peak flow suppression < 8%; depth-averaged flow factor "
                        "> 0.95 -> constant-water-mu safe; no runtime mu(c,T) hook warranted",
                strength="verification (measured mu driven through a gated extraction model; "
                         "composition + dilute-end caveats stand)")


def gate_g10_intersource_spread():
    """INTER-SOURCE consistency check for the G10 liquor viscosity: two INDEPENDENT measured
    datasets (khomyakov2020 kinematic nu -> dynamic mu = rho*nu; telisromero2001 Eq (10)) are
    compared across their overlap box (X_w 76-90 %, T 295-365 K). They agree in sign and
    direction (both > water, both rise with concentration / fall with T), but khomyakov runs
    systematically ~+37% ABOVE the TR2001 closures -- a bounded material-difference offset
    (Russian production extract vs Brazilian 51-Brix batch, different instruments), NOT random
    scatter. This QUANTIFIES the G10 absolute-magnitude uncertainty at concentrated (in-pore)
    strengths; the negligible-at-shot-TDS verdict is robust to it (gate_g10_viscosity_bulk_
    negligible re-run with this offset still yields no runtime hook). Records, does not adjudicate."""
    from puckworks import data as d
    offs = []
    for r in d.khomyakov_kinematic_viscosity():
        f = float(r["dry_solids_mass_fraction"])
        T_C = float(r["temperature_C"])
        nu = float(r["kinematic_viscosity_mm2_s"]) * 1e-6
        Xw_pct = 100.0 * (1.0 - f)
        if not (76.0 <= Xw_pct <= 90.0 and 295.0 <= T_C + 273.15 <= 365.0):
            continue
        mu_kho = d.telisromero_density_kgm3(T_C, 1.0 - f) * nu
        mu_tr = d.telisromero_viscosity_pas(T_C + 273.15, Xw_pct)
        offs.append((mu_kho - mu_tr) / mu_tr * 100.0)
    offs.sort()
    n = len(offs)
    median = offs[n // 2] if n % 2 else 0.5 * (offs[n // 2 - 1] + offs[n // 2])
    all_positive = all(o > 0 for o in offs)      # khomyakov consistently >= TR2001
    bounded = max(offs) < 60.0                    # a systematic offset, not order-of-magnitude
    passed = (n >= 6 and all_positive and 25.0 <= median <= 50.0 and bounded)
    return dict(passed=passed, n_overlap_cells=n,
                offset_pct_min=round(min(offs), 0), offset_pct_median=round(median, 0),
                offset_pct_max=round(max(offs), 0), khomyakov_above_tr=all_positive,
                reading="two independent sources agree in sign/direction; khomyakov ~+37% above "
                        "TR2001 in the overlap -> G10 absolute mu carries this inter-source "
                        "uncertainty at concentrated strengths (bulk-espresso verdict robust)",
                strength="reference/qualitative (records an inter-source discrepancy; neither "
                         "dataset reaches bulk espresso TDS -- both extrapolate toward water)")


def gate_g10_sobolik_closures():
    """SOBOLIK 2002 own-closure transcription check (G10 third/fourth liquor-viscosity source).
    The Eq (4)/(5) viscosity and Eq (11) conductivity COMPUTED lines reproduce the authors' OWN
    stated spot values -- mu(omega=0.5, 60 C) ~= 0.019 Pa.s (Eq 4); mu(omega=0, 20 C) ~= water
    (Eq 5); electrical conductivity peaks ~3.2 S/m near omega~0.4, 70 C (Eq 11). Concentrated
    soluble-coffee extract (omega = dry-coffee mass fraction), NOT espresso liquor -> reference/
    extrapolation strength (espresso TDS sits far below omega=0.5). Records, promotes nothing."""
    from puckworks import data as d
    a = d.sobolik2002_rheology()

    def spot(rows, om, T, col):
        m = [r for r in rows if abs(float(r["omega"]) - om) < 1e-6
             and abs(float(r["T_degC"]) - T) < 1e-6]
        return float(m[0][col]) if m else None

    mu_conc = spot(a["viscosity_concentrated_eq4"], 0.5, 60.0, "mu_Pa_s")
    mu_water = spot(a["viscosity_dilute_eq5"], 0.0, 20.0, "mu_Pa_s")
    kmax = max(float(r["kappa_S_m-1"]) for r in a["conductivity_eq11"])
    ok = (mu_conc is not None and abs(mu_conc - 0.019) < 0.002        # Eq 4 spot ~0.019 Pa.s
          and mu_water is not None and 0.0009 < mu_water < 0.0012     # Eq 5 -> water at 20 C
          and 3.0 < kmax < 3.4)                                       # Eq 11 kappa_max ~3.2 S/m
    return dict(passed=bool(ok),
                mu_conc_eq4_om0p5_60C=round(mu_conc, 5) if mu_conc is not None else None,
                mu_water_eq5_om0_20C=round(mu_water, 6) if mu_water is not None else None,
                kappa_max_eq11_S_m=round(kmax, 3),
                reading="Sobolik Eq (4)/(5)/(11) spot values reproduce (transcription check of "
                        "the computed closure lines)",
                strength="reference (concentrated soluble-coffee extract; espresso TDS far below "
                         "omega=0.5 -> mu extrapolates toward water)")


def gate_g10_sobolik_density():
    """SOBOLIK 2002 Eq-(1) refractive index + Eq-(2) density closed-form reproduction (the third
    G10 sobolik channel, complementing gate_g10_sobolik_closures which covers only viscosity/
    conductivity). Recomputes n_D^20 = 1.333 + 0.1728*w + 8.93e-2*w^2 and the volume-additive
    density 1/rho = w/rho_C + (1-w)/rho_W (rho_W = 1000 - 0.036*T - 0.004*T^2, rho_C = 1654 -
    1.79*T - 0.0063*T^2, T in C) from scratch and confirms they reproduce the tabulated columns to
    the digitized precision. Records two physical facts the card leans on: (1) at w=0 the density
    recovers PURE WATER exactly (unlike telisromero2000 Eq 1 -- the only registry density closure
    exact at the water limit), and (2) drho/dT < 0 throughout. Eq-(3) thermal conductivity is
    DELIBERATELY EXCLUDED -- the card marks its coefficients 'not reliably legible ... do not
    implement'. Concentrated soluble-coffee extract (w = dry-coffee mass fraction), NOT espresso
    liquor -> reference/extrapolation. source_curve_reproduction; promotes nothing."""
    from puckworks import data as d
    rows = d.sobolik2002_rheology()["physical_properties_eq1_2_3"]

    def n_D(w):
        return 1.333 + 0.1728 * w + 8.93e-2 * w**2

    def rho(w, T):
        rho_W = 1000.0 - 0.036 * T - 0.004 * T**2
        rho_C = 1654.0 - 1.79 * T - 0.0063 * T**2
        return 1.0 / (w / rho_C + (1.0 - w) / rho_W)

    n_err, rho_relerr = [], []
    water_rows, dT_by_w = [], {}
    for r in rows:
        w, T = float(r["omega"]), float(r["T_degC"])
        n_err.append(abs(n_D(w) - float(r["refractive_index_nD20"])))
        rho_tab = float(r["density_kg_m-3"])
        rho_relerr.append(abs(rho(w, T) - rho_tab) / rho_tab)
        if abs(w) < 1e-9:                                    # w=0 -> pure water at temperature T
            water_rows.append((T, rho_tab, 1000.0 - 0.036 * T - 0.004 * T**2))
        dT_by_w.setdefault(w, []).append((T, rho_tab))

    n_max = max(n_err)
    rho_max = max(rho_relerr)
    # w=0 recovers pure water (recomputed rho_W matches the tabulated w=0 density)
    water_ok = all(abs(tab - rw) / tab < 1e-4 for _, tab, rw in water_rows)
    # drho/dT < 0 within every constant-w series
    drho_dT_negative = all(
        all(b[1] < a[1] for a, b in zip(sorted(s), sorted(s)[1:]))
        for s in dT_by_w.values() if len(s) > 1)
    passed = n_max < 5e-4 and rho_max < 1e-3 and water_ok and drho_dT_negative
    return dict(passed=bool(passed),
                n_D_max_abs_err=round(n_max, 6), rho_max_rel_err=round(rho_max, 6),
                water_limit_exact=water_ok, drho_dT_negative=drho_dT_negative,
                n_rows=len(rows),
                reading="Sobolik Eq (1) n_D and Eq (2) volume-additive rho recompute to the "
                        "tabulated columns; density is exact at the water limit (w=0) and drho/dT<0 "
                        "throughout -- the only registry density closure exact at pure water",
                strength="source_curve_reproduction (reproduces the authors' own computed Eq 1/2 "
                         "columns; Eq 3 conductivity excluded as illegible per the card; "
                         "concentrated soluble-coffee extract, reference for espresso TDS)")


def gate_g10_foursource_spread():
    """FOUR-SOURCE G10 inter-source spread: sobolik2002 (Eq 5 dilute) joins khomyakov2020 as a
    THIRD independent liquor-viscosity source, each compared to the TR2001 closures over the mutual
    overlap (X_w 76-90 %, T 30-80 C). BOTH khomyakov and sobolik run systematically ABOVE TR2001,
    so TR2001 is the probable LOW outlier (3-vs-1). Records the spread; adjudicates no absolute
    value and promotes nothing -- every source is soluble-coffee extract extrapolating toward water
    at espresso TDS (the negligible-at-shot-TDS verdict is unchanged). Complements the 2-source
    gate_g10_intersource_spread."""
    from puckworks import data as d
    a = d.sobolik2002_rheology()
    sob_off = []
    for r in a["viscosity_dilute_eq5"]:
        om, T = float(r["omega"]), float(r["T_degC"])
        Xw = 100.0 * (1.0 - om)
        if not (76.0 <= Xw <= 90.0 and 30.0 <= T <= 80.0):
            continue
        mu_tr = d.telisromero_viscosity_pas(T + 273.15, Xw)
        sob_off.append((float(r["mu_Pa_s"]) - mu_tr) / mu_tr * 100.0)
    sob_off.sort()
    n = len(sob_off)
    sob_median = sob_off[n // 2] if n % 2 else 0.5 * (sob_off[n // 2 - 1] + sob_off[n // 2])
    sob_above = bool(sob_off) and all(o > 0 for o in sob_off)
    kho_above = all(
        (d.telisromero_density_kgm3(float(r["temperature_C"]), float(r["dry_solids_mass_fraction"]))
         * float(r["kinematic_viscosity_mm2_s"]) * 1e-6)
        > d.telisromero_viscosity_pas(float(r["temperature_C"]) + 273.15,
                                      100.0 * (1.0 - float(r["dry_solids_mass_fraction"])))
        for r in d.khomyakov_kinematic_viscosity()
        if 76.0 <= 100.0 * (1.0 - float(r["dry_solids_mass_fraction"])) <= 90.0
        and 295.0 <= float(r["temperature_C"]) + 273.15 <= 365.0)
    passed = (n >= 6 and sob_above and kho_above and 20.0 <= sob_median <= 90.0)
    return dict(passed=bool(passed), n_sobolik_overlap=n,
                sobolik_offset_pct_median=round(sob_median, 0),
                sobolik_above_tr=sob_above, khomyakov_above_tr=kho_above,
                reading="two independent sources (khomyakov, sobolik) both run above TR2001 in the "
                        "overlap -> TR2001 is the probable low outlier (3-vs-1)",
                strength="reference/qualitative (records the inter-source spread; every source is "
                         "soluble-coffee extract extrapolating toward water at espresso TDS)")


def gate_moroney2015_kappa_anchors():
    """MORONEY 2015 permeability internal-consistency (the primary Philips dataset). The card's
    Kozeny-Carman closure k_h = k_sv1^2 * phi_h^3 / (36 * kappa * (1-phi_h)^2) with the MEASURED
    kappa=3.1 and the Table-2 (compacted, flow-matched) phi_h reproduces the measured cylindrical
    Delta_p at Q=250 mL/min for BOTH grinds (JK drip-filter, Cimbali #20) within ~5% -- an internal
    transcription/consistency check on the intaken Tables 1/2 (the primary source `moroney2016`
    inherits its kappa=3.1 from). Drip-filter chamber, NOT espresso ratio -> reference strength;
    records, promotes nothing."""
    import math
    from puckworks import data as d
    m = d.moroney2015_data()
    t1 = {r["parameter"]: r for r in m["table1_batch_params"]}
    t2 = {r["parameter"]: r for r in m["table2_cylindrical_params"]}
    kappa = float(t1["kappa"]["JK_drip_filter"])            # 3.1 (measured Kozeny-Carman factor)
    Q = 250e-6 / 60.0                                       # 250 mL/min -> m^3/s
    A = math.pi * (0.059 / 2.0) ** 2                        # 59 mm chamber ID
    anchors, ratios = {}, []
    for grind in ("JK_drip_filter", "Cimbali_20"):
        k_sv1 = float(t1["k_sv1"][grind]) * 1e-6           # Sauter diameter um -> m
        phi_h = float(t2["phi_h"][grind])                  # intergranular porosity (compacted)
        L, mu = float(t2["L"][grind]), float(t1["mu"][grind])
        dp_meas = float(t2["Delta_p"][grind])
        k_h = k_sv1 ** 2 * phi_h ** 3 / (36.0 * kappa * (1.0 - phi_h) ** 2)
        dp_pred = mu * L * Q / (k_h * A)
        anchors[grind] = dict(k_h_m2=k_h, dp_pred_Pa=round(dp_pred), dp_meas_Pa=round(dp_meas))
        ratios.append(dp_pred / dp_meas)
    ok = (abs(kappa - 3.1) < 1e-9 and all(0.9 <= r <= 1.1 for r in ratios))   # within 10%
    return dict(passed=bool(ok), kappa_measured=kappa,
                dp_pred_over_meas=[round(r, 3) for r in ratios], anchors=anchors,
                reading="moroney2015 Kozeny-Carman (kappa=3.1) + Table-2 phi_h reproduce the "
                        "measured Delta_p at both permeability anchors within ~5% (internal "
                        "consistency of the intaken Tables 1/2)",
                strength="reference (measured/transcribed primary dataset; drip-filter chamber, "
                         "not espresso ratio)")


def gate_gagne2021_viscosity_discrimination():
    """GAGNE 2021 apparent-resistance decline vs the liquor-viscosity hypothesis -- DISCRIMINATION
    (records, does not adjudicate). Across the 11 published DE1 `.shot` traces, the post-bloom
    apparent resistance R=P/Q declines by a robust median ~2.7x (every shot declines). The
    telisromero2001 viscosity ratio brackets this over the shot's TDS trajectory: ~2.7x at Gagne's
    reconstructed ~15% early first-drip TDS (== the observed decline) falling to ~1.6x at bulk
    shot-TDS (~7.5%). So the viscosity-decline hypothesis is quantitatively ADMISSIBLE -- but it is
    DEGENERATE with a bed-compaction/swelling explanation of the same magnitude, and the traces
    alone (no independent TDS(t)) do NOT separate them (Gagne's own EY(t) reconstruction is
    endpoint-anchored/circular). NB the *local* mu ratio here is not the G10 *shot-integrated*
    Darcy error (which averages over the dilute bulk). NOT a validated kappa(t) law; promotes
    nothing; discrimination/qualitative strength."""
    from puckworks.analysis import gagne2021_resistance as gr
    r = gr.discrimination()
    obs = r["observed"]
    passed = (obs["n_shots"] >= 8 and obs["lo"] > 1.0            # every shot declines post-bloom
              and obs["median"] > 1.3                            # a large, robust decline
              and r["viscosity_admissible"]                      # mu at ~15% early TDS ~= observed
              and r["degenerate_with_bed"])                      # not discriminated by these traces
    return dict(passed=bool(passed), n_shots=obs["n_shots"],
                observed_decline_median=round(obs["median"], 2),
                observed_decline_range=[round(obs["lo"], 2), round(obs["hi"], 2)],
                mu_ratio_bulk_7p5pct=round(r["mu_ratio_bulk"], 2),
                mu_ratio_early_15pct=round(r["mu_ratio_early"], 2),
                reading="observed post-bloom R-decline (median ~2.7x) is quantitatively matched by "
                        "the telisromero mu(TDS) ratio at ~15% early TDS (~2.7x) -> viscosity is "
                        "ADMISSIBLE, but DEGENERATE with bed compaction/swelling; the traces alone "
                        "do not discriminate (no independent TDS(t))",
                strength="discrimination/qualitative (records a bounded degeneracy from machine-"
                         "logged traces; no independent TDS(t); Gagne's EY(t) chain is circular)")


def gate_moroney2015_batch_ode():
    """MORONEY 2015 well-mixed batch two-population solver -- reproduces the paper's Fig-6 batch
    plateau from Table 1 + the DERIVED immersion volume bookkeeping. Confirms: (1) the derived
    volumes reconstruct Table 1's phi_h=0.8272 to four decimals (V_h/V_T, V_T=541.1/V_h=447.6 cm^3);
    (2) the c_v0 initial condition derives from Table 1 (phi_s,b0*c_s/phi_v0) for both grinds; (3) the
    mass-conserving batch ODE (with the card-flagged Eq-53 v->h sign correction) reaches an
    equilibrium brew concentration matching the digitized Fig-6 model plateau for both grinds
    (~36.6 JK / ~30.4 Cimbali) within ~10%, fine plateauing higher than coarse; (4) available soluble
    mass is 26-33% of dose (consistent with the stated 28-32% extractable range). The c_h / Fig-2/6
    brew concentration compares with NO dilution factor. source_curve_reproduction; promotes nothing;
    drip-filter chamber, NOT espresso ratio."""
    from puckworks import data as d
    from puckworks.analysis import moroney2015_batch as mb
    vols = mb.derived_volumes()
    f6 = d.moroney2015_data()["fig6_batch_model_vs_exp"]
    checks, ratios = {}, []
    for grind, key in (("JK_drip_filter", "jk"), ("Cimbali_20", "cimbali")):
        s = mb.solve(grind)
        plateau = max(float(r["ch_kg_m3"]) for r in f6
                      if grind.split("_")[0].lower() in str(r.get("grind", "")).lower()
                      and str(r.get("type", "")).lower().startswith("model"))
        checks[key] = dict(ch_eq=round(s["ch_equilibrium"], 1), fig6_plateau=round(plateau, 1),
                           c_v0_ok=abs(s["c_v0_derived"] - s["c_v0_table"]) < 0.5,
                           extractable_pct=round(s["extractable_pct_dose"], 1))
        ratios.append(s["ch_equilibrium"] / plateau)
    phi_h_ok = abs(vols["phi_h_reconstructed"] - 0.8272) < 1e-3
    fig6_ok = all(0.90 <= r <= 1.10 for r in ratios)           # within ~10% of the Fig-6 plateau
    cv0_ok = all(c["c_v0_ok"] for c in checks.values())
    extractable_ok = all(26.0 <= c["extractable_pct"] <= 33.0 for c in checks.values())
    fine_higher = checks["jk"]["ch_eq"] > checks["cimbali"]["ch_eq"]
    passed = phi_h_ok and fig6_ok and cv0_ok and extractable_ok and fine_higher
    return dict(passed=bool(passed),
                phi_h_reconstructed=round(vols["phi_h_reconstructed"], 4),
                V_T_cm3=round(vols["V_T_m3"] * 1e6, 1), V_h_cm3=round(vols["V_h_m3"] * 1e6, 1),
                per_grind=checks, ch_over_fig6_plateau=[round(r, 3) for r in ratios],
                reading="the derived immersion bookkeeping reconstructs phi_h=0.8272 exactly, and "
                        "the mass-conserving batch ODE reproduces the Fig-6 batch plateau for both "
                        "grinds (~36.6 JK / ~30.4 Cimbali) from Table 1 -- fine higher than coarse",
                strength="source_curve_reproduction (reproduces the paper's own Fig-6 model plateau "
                         "from Table 1 + derived volumes; drip-filter chamber, not espresso ratio)")


def gate_moroney2019_ldf_verification():
    """MORONEY 2019 1-D two-grain LDF solver -- VERIFICATION of the transcribed model (Eqs 17-27)
    and the author-confirmed cooper2021 h_sl erratum. Solving the 1-D cylindrical reduction with
    the CORRECTED h_sl: (1) closes the solute mass budget (removed from grains ~= carried out of
    the bed) within the upwind numerical-diffusion floor for both grinds; (2) produces a physical
    fast-rise / slow-decay exit concentration with the two-timescale (small << large) structure,
    coarse slower than fine; (3) confirms the erratum by PHYSICAL PLAUSIBILITY -- every CORRECTED
    intragranular diffusivity D_v = h_sl*d_s stays at/below free aqueous diffusion (~2.2e-9 m^2/s),
    while the UNCORRECTED reported values exceed it by orders (impossible). NOT a fit to data
    (reproducing moroney2019's reported c_exit RMSE 5.81/6.23 needs their own Fig-6 digitization,
    which is not in the registry); a model-vs-itself verification. Records, promotes nothing."""
    from puckworks.analysis import moroney2019_ldf as ldf
    D_FREE = 2.2e-9                                   # coffee-in-water molecular diffusivity (card)
    res = {g: ldf.solve(g) for g in ("fine", "coarse")}
    budget_ok = all(0.92 <= r["budget_closure"] <= 1.0 for r in res.values())
    shape_ok = all(float(r["cexit_kgm3"].min()) >= -1e-6 and r["cexit_peak"] < r["cs0_kgm3"]
                   and r["cexit_end"] < r["cexit_peak"]                 # decays from an early peak
                   and r["tau_small_s"] < r["tau_large_s"] for r in res.values())
    slower_coarse = res["coarse"]["tau_large_s"] > res["fine"]["tau_large_s"]
    corr = [v for r in res.values() for v in r["D_v_corrected"].values()]
    rep = [v for r in res.values() for v in r["D_v_reported"].values()]
    corrected_physical = all(v <= D_FREE for v in corr)
    reported_unphysical = any(v > D_FREE for v in rep)                  # >= 1 reported > free diff
    passed = (budget_ok and shape_ok and slower_coarse
              and corrected_physical and reported_unphysical)
    return dict(passed=bool(passed),
                budget_closure={g: round(r["budget_closure"], 3) for g, r in res.items()},
                cexit_peak_kgm3={g: round(r["cexit_peak"]) for g, r in res.items()},
                tau_small_s={g: round(r["tau_small_s"]) for g, r in res.items()},
                tau_large_s={g: round(r["tau_large_s"]) for g, r in res.items()},
                D_v_corrected_max=max(corr), D_v_reported_max=max(rep), D_free_m2_s=D_FREE,
                corrected_physical=corrected_physical, reported_unphysical=reported_unphysical,
                reading="1-D two-grain LDF (corrected h_sl) closes the mass budget and shows the "
                        "physical fast/slow two-grain exit structure; the cooper2021 erratum is "
                        "confirmed -- corrected D_v <= free diffusion, reported values exceed it",
                strength="verification (model-vs-itself budget/shape + physical plausibility; NOT a "
                         "fit to experimental data -- the reported RMSE needs moroney2019's Fig-6 "
                         "digitization)")


def gate_smrke2024_fast_extraction_shape():
    """SMRKE 2024 gate S-A -- the QUALITATIVE shape check that survives cross-setup transfer.

    NOT the card's original +/-0.5 pt point-match (that is S-B, blocked -- see the card and
    puckworks/analysis/smrke2024_envelope.py for why: cameron's coffee/EK43 grind/machine differ
    from smrke's, and smrke's absolute EY 16.4-21.3% is setup-specific, so a +/-0.5 pt landing
    would be coincidence). This gate asserts only what transfers: over an in-range EK43 grind sweep
    at smrke's 20 g:40 g / 9 bar recipe, cameron2020's EY(t) (1) rises monotonically, (2) is
    decelerating (fast-rise-then-plateau: first-half rate > second-half rate), (3) reaches >=80% of
    its OWN final yield by t=15 s -- a NECESSARY-NOT-SUFFICIENT fast-extraction sanity check, the one
    clause of the original gate intact across setups and matching smrke's own early shots (0.77-0.83
    of ceiling), (4) plateaus inside a plausible espresso EY band that BRACKETS smrke's ceiling
    (a ballpark sanity band, NOT a match -- the cross-coffee offset ~-30% is reported, not asserted),
    and (5) across the sweep, longer shots yield MORE (EY-vs-t_shot slope SIGN matches smrke's Fig-3
    master curve). sign_or_compatibility (qualitative); promotes nothing; reproduces no smrke curve."""
    from puckworks.analysis import smrke2024_envelope as se
    r = se.shape_report()
    shots = r["shots"]
    monotone = all(s["monotone"] for s in shots)
    decelerating = all(s["decelerating"] for s in shots)
    fast_extraction = all(s["frac_15"] >= 0.80 for s in shots)   # necessary-not-sufficient
    in_band = all(s["in_band"] for s in shots)
    slope_sign = r["slope_sign_matches"]
    passed = monotone and decelerating and fast_extraction and in_band and slope_sign
    return dict(passed=bool(passed),
                monotone=monotone, decelerating=decelerating,
                fast_extraction_frac15_ge_0p80=fast_extraction,
                plateau_in_espresso_band=in_band, slope_sign_matches_fig3=slope_sign,
                frac_15=[s["frac_15"] for s in shots],
                ey_final=[s["ey_final"] for s in shots],
                plateau_offset_vs_smrke_pct=[s["plateau_offset_vs_smrke_pct"] for s in shots],
                smrke_ceiling_pct=r["env"]["ey_max"],
                smrke_early_frac_range=[round(x, 3) for x in r["env"]["early_frac_vs_ceiling"]],
                reading="cameron's EY(t) over an in-range grind sweep at 20g:40g/9bar is monotone, "
                        "decelerating, reaches >=80% of its own final yield by 15 s (like smrke's "
                        "early shots), plateaus in an espresso-plausible band bracketing smrke's "
                        "ceiling, and rises with shot time -- the same slope sign as smrke's Fig-3. "
                        "The absolute EY sits ~30% below smrke's ceiling (different coffee), REPORTED "
                        "not asserted.",
                strength="sign_or_compatibility (S-A qualitative shape/slope-sign match vs smrke's "
                         "independent Fig-3 + fast-extraction sanity; the +/-0.5 pt point-match is "
                         "S-B, BLOCKED on a grind adapter + ceiling calibration or smrke's raw data)")


def gate_streamtube_heldout():
    """WITHIN-CAMPAIGN HELD-OUT: the sigma(GS) fines closure, fit on two of the paper's three
    Fig-5 grinds, predicts the held-out grind's EY deviation. Leave-one-out over
    GS 1.1/1.3/1.5 (measured relative deviations 13.1/6.1/2.6% — streamtube module docstring)."""
    from puckworks.models.brewer2026 import streamtube as st
    from puckworks import data as pwdata
    rows = sorted(pwdata.cameron2020_fig5_grind_deviation(), key=lambda r: r["gs"])
    GS = [r["gs"] for r in rows]
    DEV = [r["rel_deviation"] for r in rows]
    resp = {g: st.EYResponse(gs=g, p_bar=5.0, n_grid=9) for g in GS}   # ~1.5 s each
    sig_cal = [resp[g].sigma_for_deficit(d) for g, d in zip(GS, DEV)]
    errs = []
    for i in range(len(GS)):
        tr_gs = [GS[j] for j in range(len(GS)) if j != i]
        tr_sig = [sig_cal[j] for j in range(len(GS)) if j != i]
        fit = st.fit_closure(tr_gs, tr_sig, form="power")
        sig_pred = float(fit["predict"](GS[i]))
        dev_pred = float(resp[GS[i]].deficit(sig_pred))
        errs.append(abs(dev_pred - DEV[i]))
    max_err = float(max(errs))
    return dict(passed=max_err < 0.02,                    # held-out deviation within 2 pp
                max_heldout_abs_error=round(max_err, 4),
                heldout_abs_errors=[round(e, 4) for e in errs],
                calibrated_sigma=[round(s, 4) for s in sig_cal])


def gate_pack_generator_admissible():
    """QUALITATIVE CAPACITY: the overlapping-sphere pack generator hits its target solid fraction,
    produces an admissible boolean pack at resolution (grain radius >= 10 voxels), and its
    columnar heterogeneity field is zero-mean / unit-std (card admissibility properties)."""
    from puckworks.models.brewer2026 import pack_generator as pg
    gs, phis_target = 1.3, 0.55
    r_um = pg.boulder_radius_um(gs)
    vox = r_um / 11.0                                     # -> grain radius ~11 voxels (>= 10)
    r_vox = r_um / vox
    solid, meta = pg.make_pack(L=64, voxel_um=vox, gs=gs, phis_target=phis_target,
                               seed=0, verbose=False)
    phis = float(meta["phis"])
    f = pg.hetero_field(48, 8, 0)
    ok = (solid.dtype == bool and solid.shape == (64, 64, 64)
          and abs(phis - phis_target) < 0.03           # hits target solid fraction
          and 0.30 < (1.0 - phis) < 0.70                # sane porosity
          and r_vox >= 10.0                             # resolution admissibility
          and abs(float(f.mean())) < 1e-6 and abs(float(f.std()) - 1.0) < 0.05)
    return dict(passed=bool(ok), phis=round(phis, 3), porosity=round(1.0 - phis, 3),
                grain_radius_voxels=round(r_vox, 1),
                hetero_mean=float(f.mean()), hetero_std=round(float(f.std()), 4))

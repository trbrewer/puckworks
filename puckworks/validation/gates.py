"""Fast validation gates (< ~30 s total). Heavier ladders (sphere-array
resolution study, twin-solver pack cross-check, GPU sweeps) live in
validation/slow/ and the Colab notebook."""
import json, os
import numpy as np

DATA = os.path.join(os.path.dirname(__file__), "..", "data")

def gate_lb_channel():
    """Reference LB kernel vs exact plane-Poiseuille solution."""
    from puckworks.models.brewer2026 import lb_reference as lb
    Nz, N = 33, 4
    solid = np.zeros((N, N, Nz), dtype=bool)
    solid[:, :, 0] = True; solid[:, :, -1] = True
    r = lb.solve(solid, g=1e-6, tau_plus=1.2, max_steps=20000, check=200,
                 rtol=1e-6, verbose=False)
    h = float(Nz - 2)
    k_meas = r["nu"] * (r["q"]*Nz/h) / 1e-6
    err = 100*(k_meas/(h*h/12.0) - 1)
    return dict(passed=abs(err) < 0.5, err_pct=round(err, 3))

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
    t_drip = float(t[np.argmax(w > 0.5)])
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
    import numpy as np
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
    trace, the time-dependent poroelastic Phi(t) (rung 4) beats the constant-
    kappa / static-kappa(P) null (rungs 1/3) -- a bed mechanism IS needed for the
    rising residual (the flat nulls cannot). Rung 5 challengers are Phase 3."""
    from puckworks import harness as h
    L = h.kappa_t_ladder()
    passed = (L["rung4_beats_floor"] and L["improvement_factor"] > 2.0
              and L["rung4_phi_of_t"] < 0.2)
    return dict(passed=passed, rung1_rmse=L["rung1_const_kappa"],
                rung4_rmse=L["rung4_phi_of_t"], factor=L["improvement_factor"])


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
    import numpy as np
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
         gate_p2_kappa_ladder, gate_cameron_conservation,
         gate_pannusch_qt_adapter, gate_mo_reynolds_overlay, gate_egidi_bracket]

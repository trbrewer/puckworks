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
         gate_moroney_fig6_washthrough]

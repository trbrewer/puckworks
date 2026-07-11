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


QUICK = [gate_lb_channel, gate_wadsworth_collapse, gate_infiltration_triangle,
         gate_waszkiewicz_static_refit, gate_waszkiewicz_dynamic_9bar]

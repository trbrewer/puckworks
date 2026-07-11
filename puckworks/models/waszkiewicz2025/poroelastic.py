"""poroelastic.py — Waszkiewicz et al. 2025 poroelastic flow regulation.

Card: docs/cards/waszkiewicz2025.md (ROADMAP item 1.2). Runtime bed_dynamics /
flow closure for a saturated tamped puck: pressure compacts the bed and reduces
its Carman-Kozeny permeability, so the equilibrium pressure-flow curve is
Darcy-linear below ~5 bar and saturates in the 9-bar regime. A time-dependent
extension makes the stress-free porosity track the dissolved-mass fraction,
giving a *parameter-free* predictor of Q(t) once the two rig constants
(P_c, Q_c) and the dissolution sigmoid are fixed.

Everything here is the authors' own closed form (their arXiv:2512.21528 code,
Zenodo 10.5281/zenodo.18046315), re-expressed; nothing beyond their Phi->0 limit
(Eq. 16) is simplified. RC-3a SCOPE ONLY: the empirical m_d(t) sigmoid is used;
the Cameron-coupled m_d(t) variant (RC-3b) is a *different* model and does not
enter here (see ROADMAP P2 ladder rung 5).

Validation (see validation/gates.py):
 - static:  refitting Eq. 16 to their 11-pressure long-run curve recovers
   (P_c, Q_c) = (12.39 bar, 1.897 g/s) == their published static calibration.
 - dynamic: the parameter-free Eq. 18 reproduces the 9-bar Q(t) ramp
   (long-run flow within ~2%, correlation ~0.98) — semi-quantitative, per card.

Scope limits (card): silent on the first ~5-10 s (wetting/air/swelling); pure
Hookean, no plasticity/hysteresis (their CT shows delamination it cannot model);
Phi(t)=m_d(t)/m0 attributes all porosity change to dissolution; constants are
per-rig/coffee/grind and NOT transferable. Quantitatively wrong below ~5 bar.
"""
import numpy as np

from puckworks import data as _d


def qhat(p_hat):
    """Universal dimensionless equilibrium curve, Phi->0 limit (Eq. 16).

    Qhat = Phat (4 - 6 Phat + 4 Phat^2 - Phat^3), monotone and =1 at Phat=1
    (zero slope there); the model cannot produce the slight high-pressure flow
    *decrease* the data hint at above ~12 bar (card).
    """
    p = np.asarray(p_hat, float)
    return p * (4.0 - 6.0*p + 4.0*p*p - p*p*p)


def phi_factor(phi):
    """F(Phi) (Eq. 14): Q_m(Phi) = Q_ref * F(Phi). Their exact expression."""
    phi = np.asarray(phi, float)
    return (phi*(phi*(11.0*phi - 15.0) + 6.0)
            - 6.0*(phi - 1.0)**3 * np.log(1.0 - phi)) / (6.0*(phi - 1.0)**2)


def q_static(P_bar, P_c, Q_c):
    """Equilibrium flow Q(P) = Q_c * Qhat(P/P_c) (Eqs. 16 with calibration pair).

    P_c = Y*Phi_m [bar], Q_c = Q_m(Phi_m) [g/s]. Valid for P <= P_c; the caller
    decides clamping above P_c (their reference code does not clamp the static
    curve, only the time-dependent one)."""
    return Q_c * qhat(np.asarray(P_bar, float) / P_c)


def fit_static(P_bar, Q_g_s):
    """Refit (P_c, Q_c) of Eq. 16 to a steady-state pressure-flow curve.

    Replicates the authors' fit (scipy curve_fit, same bounds/guess). Returns
    ((P_c, Q_c), (P_c_std, Q_c_std)). Feed the long-run BASKET pressure and mass
    flow rate (one point per reference pressure)."""
    from scipy.optimize import curve_fit
    P = np.asarray(P_bar, float); Q = np.asarray(Q_g_s, float)
    popt, pcov = curve_fit(lambda p, pref, qref: q_static(p, pref, qref), P, Q,
                           p0=(20.0, 1.0),
                           bounds=((P.max(), 0.01), (100.0*P.max(), 100.0)),
                           maxfev=20000)
    return tuple(popt), tuple(np.sqrt(np.diag(pcov)))


def solids_sigmoid(t, k_solids, l_solids, m_solids):
    """Dissolved-mass sigmoid m_d(t) (Eq. 20): 0.5 k (1 + tanh((t-l)/m)) [g]."""
    return 0.5*k_solids*(1.0 + np.tanh((np.asarray(t, float) - l_solids)/m_solids))


def q_dynamic(t, P_applied_bar, P_c, Q_c, k_solids, l_solids, m_solids, dose_g):
    """Time-dependent flow Q(t) at constant applied pressure (Eq. 18).

    Phi(t) = m_d(t)/m0 rises during the shot; with NO extra free parameters the
    universal curve is re-referenced per-timestep. Returns Q(t) [g/s], clipped
    at 0 (the model predicts complete shut-off for P > Phi*Y). This is the RC-3a
    empirical-sigmoid form. P_applied_bar follows the authors' code: the nominal
    applied (basket) pressure of the shot, scalar."""
    t = np.asarray(t, float)
    phi_m = k_solids/dose_g
    q_master = Q_c/phi_factor(phi_m)
    p_master = P_c/phi_m
    phi_t = solids_sigmoid(t, k_solids, l_solids, m_solids)/dose_g
    q_ref_td = q_master*phi_factor(phi_t)
    p_ref_td = p_master*phi_t
    return np.clip(qhat(P_applied_bar/p_ref_td)*q_ref_td, 0.0, None)


# --- convenience: pull calibration + the steady-state curve from the data ----
def published_calibration():
    """(P_c, Q_c) from the ingested static_calibration.csv (their fit)."""
    c = _d.waszkiewicz_static_calibration()
    return c["P_c_bar"], c["Q_c_g_per_s"]


def steady_state_curve():
    """Long-run (last-timepoint) basket pressure & mass flow per reference
    pressure — the 11-point equilibrium curve their static fit consumes."""
    tr = _d.waszkiewicz_traces()
    ps = sorted(k for k in tr if k != "columns")
    P = np.array([tr[p]["basket_pressure__bar"][-1] for p in ps])
    Q = np.array([tr[p]["mass_flow_rate__g_per_s"][-1] for p in ps])
    return P, Q


def _solids_params():
    p = _d._params(_d.WASZ / "solids_calibration.csv")
    return p["k_solids__g"], p["l_solids__s"], p["m_solids__s"]

"""inertial.py — Wadsworth et al. 2026 Forchheimer / inertial flow closure.

Card: docs/cards/wadsworth2026_inertial.md (ROADMAP item 1.1). Same paper as
wadsworth2026.{permeability,grindmap}. RUNTIME flow-stage wrapper that extends
Darcy with the Forchheimer inertial term, closed by an empirical k_I(k) law
argued microstructure-agnostic (ceramics/sintered-media collapse). A Forchheimer
number Fo_F diagnoses when inertia matters.

    grad_p = -(mu/k) q - (rho/k_I) |q| q                     (Forchheimer, eq 2.1)
    Fo_F   = rho k q / (mu k_I)   (eq 5.2b);  f = grad_p k_I/(rho q^2) (eq 5.2a)
    model curve  f = 1/Fo_F + 1   (Darcy-only: f = 1/Fo_F)

Two published k_I(k) closures (both implemented; **strict SI k [m^2]** — the
expressions carry hidden units and fail silently off-SI, ledger A7):
  - exp   (eq 2.8, ceramics fit; authors' PREFERRED shape): k_I = exp(g2 k^tau).
          Nearly k-independent Fo_F (the k-k_I covariance collapse).
  - zhou  (eq 2.7, power law; captures the RANGE not the curvature):
          k_I = g1 k^(tau'/2). Fo_F ~ 1/sqrt(k), so grind/pack spread drives it.

Naming: Fo_F = Forchheimer number (this module); NOT Fo_diff (Fourier). Bare
"Fo" is banned (ROADMAP P6 / CLAUDE.md rule 8).

Scope (card): steady incompressible single-phase; silent on preinfusion
transients, two-phase/degassing, and channel jets where local Re exceeds the
bed average. k_I(k) never calibrated on coffee by these authors; tamped-coffee k
sits at/below the low edge of the ceramics fit support — extrapolation caveat.
"""
import numpy as np

from puckworks.contracts import assert_si_permeability

# eq 2.8 exp closure (ceramics fit; k in m^2, k_I in m)
GAMMA2, TAU = -1.71588, -0.08093
# eq 2.7 Zhou power law (best fit gamma1=1e10, tau'=3)
GAMMA1, TAU_P = 1e10, 3.0
# nominal water at ~92 C (card)
MU_92C, RHO_92C = 3e-4, 960.0

# The espresso worked-estimate inputs on the card, and their reported Fo band.
FO_BAND_CARD = (0.0161, 0.0639)


def k_I(k_m2, closure="zhou"):
    """Inertial permeability k_I [m] from Darcy k [m^2]. closure='zhou'(eq 2.7,
    reproduces the Fo band) or 'exp'(eq 2.8, preferred shape). Strict SI."""
    assert_si_permeability(k_m2, "k")
    k = np.asarray(k_m2, float)
    if closure == "zhou":
        return GAMMA1 * k ** (TAU_P / 2.0)
    if closure == "exp":
        return np.exp(GAMMA2 * k ** TAU)
    raise ValueError(f"unknown closure {closure!r}")


def solve_q(k_m2, k_I_m, grad_p, mu=MU_92C, rho=RHO_92C):
    """Darcy velocity q [m/s] from |grad_p| via the Forchheimer quadratic
    (rho/k_I) q^2 + (mu/k) q - |grad_p| = 0, numerically stable positive root.
    Recovers Darcy q = |grad_p| k / mu as k_I -> inf."""
    a = rho / np.asarray(k_I_m, float)
    b = mu / np.asarray(k_m2, float)
    c = np.abs(np.asarray(grad_p, float))
    return 2.0 * c / (b + np.sqrt(b * b + 4.0 * a * c))


def forchheimer_number(k_m2, q, k_I_m, mu=MU_92C, rho=RHO_92C):
    """Fo_F = rho k q / (mu k_I) (eq 5.2b). Inertia matters as Fo_F -> O(0.1-1)."""
    return rho * np.asarray(k_m2, float) * np.asarray(q, float) / (
        mu * np.asarray(k_I_m, float))


def friction_factor(grad_p, q, k_I_m, rho=RHO_92C):
    """f = grad_p k_I / (rho q^2) (eq 5.2a)."""
    q = np.asarray(q, float)
    return np.abs(np.asarray(grad_p, float)) * np.asarray(k_I_m, float) / (rho * q * q)


# --- gate helpers --------------------------------------------------------
def espresso_fo_band(closure="zhou"):
    """Reproduce the card's worked espresso Fo band from its stated inputs:
    <R> 145-276 um, phi_p 0.3-0.5 (k via the percolation eq 5.3), q 5.36-5.74e-4
    m/s. Returns (Fo_min, Fo_max)."""
    from puckworks.models.wadsworth2026 import permeability as wp
    fo = []
    for R in (145e-6, 276e-6):
        for phi in (0.3, 0.5):
            k = wp.k_percolation(R, phi)
            for q in (5.36e-4, 5.74e-4):
                fo.append(float(forchheimer_number(k, q, k_I(k, closure))))
    return min(fo), max(fo)


def de1_fixtureA_audit():
    """§5.2 shared-dimensional audit on DE1 fixture A with the fitted kappa=1.196.

    Computes q, grad_p, k, k_I, Fo_F along the recorded trace under ONE stated
    convention (Darcy velocity; k from the Cameron/Foster kappa->SI chain). This
    settles the registry's Fo-regime disagreement on real tamped traces. Returns
    a summary dict; per §5.2 do NOT compare these Fo_F to Mo's Re as
    interchangeable (Mo Re overlay needs item 0.4)."""
    import json
    import os
    from puckworks.models.foster2025 import infiltration as inf
    from puckworks.models.cameron2020 import extraction_bdf as em
    DATA = os.path.join(os.path.dirname(__file__), "..", "..", "data")
    d = json.load(open(os.path.join(DATA, "de1_fixtureA.json")))
    k, L = inf.k_from_kappa(d["grind_setting_assumed"], d["dose_g"] / 1000.0,
                            d["kappa_fitted"])
    A = np.pi * em.R0 ** 2
    q = np.array(d["flow_gs"]) / 1000.0 / RHO_92C / A          # m/s
    grad_p = np.array(d["pressure_bar"]) * 1e5 / L             # Pa/m
    out = {"k_m2": k, "L_m": L, "A_m2": A, "q_peak_m_s": float(q.max())}
    for c in ("zhou", "exp"):
        Fo = forchheimer_number(k, q, k_I(k, c))
        out[f"Fo_F_max_{c}"] = float(np.nanmax(Fo))
    return out

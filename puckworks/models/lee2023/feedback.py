"""feedback.py — Lee & Smith 2023 two-pathway extraction->porosity->permeability
feedback (fine-grind-dip hypothesis (c)).

Card: docs/cards/lee2023.md (ROADMAP item 3.4). Two parallel flow pathways share
a constant total flow Q; a small initial porosity seed delta grows because
extraction opens porosity (Eq. 3), which raises Kozeny-Carman permeability
(kappa = eps^3/(1-eps)^2), which reroutes flow (Eqs. 1-2), which accelerates the
faster pathway's extraction -- a positive feedback from an arbitrarily small
seed. The headline claim is a *saturation* reinterpretation of the espresso EY(g)
peak: past a critical grind the fast pathway hits EY_max and the slow one is
starved, so the beverage EY stops climbing and turns over.

This is NOT a validated predictive model. Its own authors need an UNPHYSICAL
rho_c = 798 kg/m3 (2x measured) to make EY(g) actually decline; at the physical
rho_c = 399 it only plateaus. We reproduce BOTH as the documented behaviour /
failure mode (verification + qualitative), never promoting the plateau to a
decline. It enters the fine-grind-dip hypothesis registry as a discriminable
third mechanism, not as a component that fits any dataset better than the others.

Conventions (docs/cards/lee2023.md "Errata", reviewer-adjudicated with the paper
in evidence):
 - alpha = c_sat/rho_c (Eq. 9; Table I's 3.76 is a reciprocal typo). rho_c enters
   the dynamics ONLY through alpha.
 - EY_tot = [(e1-e10)+(e2-e20)] / [(1-e10)+(1-e20)]  (solid-depletion, mass-wtd).
 - tau_shot(g) = t_shot(g)*(D/lam)*S(g)*c_sat*(1-eps0)/M_dose  (rho_c cancels).
 - kappa = eps^3/(1-eps)^2 (Kozeny-Carman).

Nondimensional system integrated (their Eqs. 7-8):
   dε_i/dτ      = (1-C_i) θ(EY_max-EY_i)
   α ε_i dC_i/dτ = (1-C_i)(1-α C_i) θ(EY_max-EY_i) - [2β κ_i/(κ1+κ2)] C_i
with β = Q λ/(D S), κ_i = ε_i^3/(1-ε_i)^2, θ the Heaviside dissolution cutoff.
"""
import numpy as np
from scipy.integrate import solve_ivp

# --- fixed constants (docs/cards/lee2023.md Parameters + Errata) -------------
C_SAT = 212.4          # kg/m3, surface saturation (Cameron 2020)
EPS0 = 0.173           # initial bed porosity (Cameron 2020)
M_DOSE = 0.020         # kg dry coffee
D_OVER_LAM = 8.0e-6    # m/s, D/lambda (= 1 / (lambda/D=0.125e6 s/m))
RHO_W = 997.0          # kg/m3
# fitted (Table I): the seed, dissolution cutoff, and lambda/D
DELTA = 0.035          # initial porosity perturbation, eps_{1,2}(0)=eps0 +/- delta
EY_MAX = 0.338         # dissolution Heaviside cutoff (fraction)
LAM_OVER_D = 1.0 / D_OVER_LAM   # s/m
# imposed vs physical coffee solid density (the paper's key caveat)
RHO_C_IMPOSED = 798.0  # kg/m3 -- unphysical 2x, required for the DECLINE
RHO_C_PHYSICAL = 399.0 # kg/m3 -- measured, gives only a PLATEAU (negative result)

# auxiliary grinder maps fitted linearly to Cameron 2020 (their Figs. 2-3)
_T0, _T1 = 50.5, -11.5   # t_shot(g) = 50.5 - 11.5 g  [s]
_S0, _S1 = 0.543, -0.112  # S(g)     = 0.543 - 0.112 g [m^2]


def t_shot(g):
    """Shot duration [s] at EK43 grind setting g (Cameron Fig. 2 linear fit)."""
    return _T0 + _T1 * np.asarray(g, float)


def surface_area(g):
    """Total grain surface area S(g) [m^2] (Cameron Fig. 3 linear fit)."""
    return _S0 + _S1 * np.asarray(g, float)


def tau_shot(g):
    """Dimensionless integration endpoint (Errata; rho_c cancels). Cross-check:
    tau_shot(1.1)=1.12, tau_shot(2.3)=0.48 -- their Figs. 6-7 time axes."""
    return t_shot(g) * D_OVER_LAM * surface_area(g) * C_SAT * (1.0 - EPS0) / M_DOSE


def _kappa(eps):
    return eps ** 3 / (1.0 - eps) ** 2


def simulate(g, rho_c=RHO_C_IMPOSED, delta=DELTA, ey_max=EY_MAX,
             lam_over_d=LAM_OVER_D):
    """Integrate the two-pathway system to tau_shot(g). Returns a dict with the
    beverage EY_tot [%], the per-pathway EY1/EY2 [%] (fast/slow), and the seed
    amplification EY1-EY2. alpha = c_sat/rho_c enters only here."""
    alpha = C_SAT / rho_c
    S = float(surface_area(g))
    ts = float(t_shot(g))
    Q = M_DOSE / (RHO_W * ts)          # m^3/s, constant total flow
    beta = Q * lam_over_d / S
    e10 = EPS0 + delta
    e20 = EPS0 - delta

    def rhs(tau, y):
        e1, C1, e2, C2 = y
        k1 = _kappa(e1); k2 = _kappa(e2)
        ey1 = (e1 - e10) / (1.0 - e10)
        ey2 = (e2 - e20) / (1.0 - e20)
        th1 = 1.0 if ey1 < ey_max else 0.0
        th2 = 1.0 if ey2 < ey_max else 0.0
        de1 = (1.0 - C1) * th1
        de2 = (1.0 - C2) * th2
        dC1 = ((1.0 - C1) * (1.0 - alpha * C1) * th1
               - 2.0 * beta * k1 / (k1 + k2) * C1) / (alpha * e1)
        dC2 = ((1.0 - C2) * (1.0 - alpha * C2) * th2
               - 2.0 * beta * k2 / (k1 + k2) * C2) / (alpha * e2)
        return [de1, dC1, de2, dC2]

    sol = solve_ivp(rhs, [0.0, float(tau_shot(g))], [e10, 0.0, e20, 0.0],
                    method="BDF", rtol=1e-8, atol=1e-11)
    e1, _, e2, _ = sol.y[:, -1]
    ey1 = (e1 - e10) / (1.0 - e10)
    ey2 = (e2 - e20) / (1.0 - e20)
    ey_tot = ((e1 - e10) + (e2 - e20)) / ((1.0 - e10) + (1.0 - e20))
    return dict(EY_tot_pct=ey_tot * 100.0, EY1_pct=ey1 * 100.0,
                EY2_pct=ey2 * 100.0, divergence_pct=(ey1 - ey2) * 100.0,
                beta=beta, alpha=alpha, tau_end=float(tau_shot(g)), ok=bool(sol.success))


def ey_curve(g_values, rho_c=RHO_C_IMPOSED, **kw):
    """Beverage EY_tot [%] vs grind setting. Returns (g, EY_tot)."""
    g = np.asarray(g_values, float)
    ey = np.array([simulate(float(gi), rho_c=rho_c, **kw)["EY_tot_pct"] for gi in g])
    return g, ey


def peak_and_fine_decline(g_values, rho_c=RHO_C_IMPOSED, min_drop_pct=0.05, **kw):
    """Classify an EY(g) curve: does it have an interior peak with a decline on
    the FINE-grind side (small g)? Returns dict with peak location and whether
    the finest-grind EY sits below the peak by >= min_drop_pct. This is the
    load-bearing G2/G3 discriminator: True for the imposed rho_c=798 (decline),
    False for the physical rho_c=399 (plateau, the documented negative result)."""
    g, ey = ey_curve(g_values, rho_c=rho_c, **kw)
    i_peak = int(np.argmax(ey))
    # fine grind = smallest g (longest shot). decline on the fine side means the
    # finest point is below an interior peak.
    fine_decline = bool(ey[0] < ey[i_peak] - min_drop_pct and i_peak > 0)
    return dict(g_peak=float(g[i_peak]), ey_peak_pct=float(ey[i_peak]),
                ey_fine_pct=float(ey[0]), ey_coarse_pct=float(ey[-1]),
                fine_side_decline=fine_decline,
                peak_amplitude_pct=float(ey[i_peak] - min(ey[0], ey[-1])))

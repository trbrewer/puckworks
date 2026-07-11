"""fines_migration.py — a fasano2000-Part-I-STRUCTURED fines-migration model.

Card: docs/cards/fasano2000_partI.md (ROADMAP item 3.3).

IMPORTANT — this is NOT a faithful port. Fasano/Talamucci/Petracco leave the
constitutive closures **K(b,m), M (packing), gamma (release rate)** unspecified
("not provided", card Parameters), so their Fig 8.6 curve cannot be reproduced
from scratch. This module implements the paper's PDE *structure* (their
nondimensional system 8.15-8.25 with the compact-layer free boundary) using OUR
chosen closures and the ONE function the paper does supply: the digitized beta(q)
detachment threshold from Fig 8.7. It therefore enters the registry by GATE, not
by inheritance -- a fasano-structured demonstration of the mechanism, exactly the
"mechanism plausibility, not validation" level the card assigns the source.

Governing structure (nondimensional, their eqs; bars dropped):
  release (8.16)   db/dt = -q [b - beta(q)]^+                 (bound fines detach)
  advection (8.23) d(m+b)/dt + mu q d(m+b)/dx = 0            (mobile fines advect)
  free bdry (8.19) (M - (m+b)|_s) ds/dt = -mu q m|_s          (deposit at the front)
  Darcy flux (8.25) q = p0 / ( s <R(m+b)> + R_c (1-s) )       (resistance closure)
  IC/BC            b=1, m=m0, s=1 ; m(0,t)=0 (clean inflow)
Solved on a Landau-mapped grid xi = x/s(t) in [0,1] (front pinned at xi=1),
method of lines, upwind advection.

OUR closures (documented, tunable -- NOT the paper's): resistivity R(u)=1+a*u
(rises with total fines u=m+b), packing M, compact-layer resistivity R_c>>R,
particle slowing mu=0.5 (the paper's Fig 8.6 value), initial mobile m0.

What this reproduces (mechanism, gate_fasano_freeboundary): mass balance 8.33
closed; q(t) monotone-nonincreasing (Lemma 8.3); s(t) >= s_m = 1-(1+m0)/M
(Lemma 8.1); and a NONMONOTONE q_inf(p0) with an interior peak (rise -> peak ->
decline, the Fig 8.6 headline) driven by the release->compaction->resistance
feedback. The peak vs the digitized Fig 8.6/8.7 is checked separately by
gate_fasano_cor82_nonmonotone (Cor. 8.2, data level).
"""
import numpy as np
from scipy.integrate import solve_ivp

from puckworks import data as _d

# --- OUR chosen closures (fasano-STRUCTURED, not the paper's values) ---------
MU = 0.5               # particle slowing mu = alpha L/(eps gamma) (paper's Fig 8.6 value)
M_PACK = 5.0           # compact-layer packing concentration (M > b0 + m0)
R_C = 50.0             # compact-layer resistivity R_c >> R(active)
A_R = 1.0              # resistivity slope R(u) = 1 + A_R u
M0 = 0.0               # initial mobile-fines concentration


def beta_from_fig87(series="beta1"):
    """Digitized detachment threshold beta(q) from Fig 8.7 (the one constitutive
    function the paper DOES supply). Returns a clamped linear interpolator."""
    pts = sorted((r["q"], r["beta"]) for r in _d.fasano_fig8_7() if r["series"] == series)
    qs = np.array([p[0] for p in pts]); bs = np.array([p[1] for p in pts])
    return lambda q: float(np.interp(q, qs, bs, left=bs[0], right=bs[-1]))


def _R(u, a_R=A_R):
    return 1.0 + a_R * u


def s_min(M_pack=M_PACK, m0=M0):
    """Lemma 8.1 lower bound on the free boundary: s >= 1 - (1+m0)/M."""
    return 1.0 - (1.0 + m0) / M_pack


def simulate(p0, beta, t_end=600.0, Ng=40, M_pack=M_PACK, R_c=R_C, mu=MU,
             a_R=A_R, m0=M0, n_save=80):
    """Integrate the free-boundary system at applied pressure p0 with threshold
    beta(q). Returns dict: t, q(t), s(t), mass_balance(t) (should equal 1+m0 by
    Eq 8.33). u = m+b on the mapped grid xi in [0,1]."""
    xi = np.linspace(0.0, 1.0, Ng + 1)
    dxi = 1.0 / Ng

    def flow(u, s):
        return p0 / (s * np.trapezoid(_R(u, a_R), xi) + R_c * (1.0 - s))

    def rhs(t, y):
        u = y[:Ng + 1].copy(); b = y[Ng + 1:2 * Ng + 2].copy(); s = max(y[-1], 1e-3)
        u[0] = b[0]                                       # m(0)=0 clean inflow
        q = flow(u, s)
        m1 = u[-1] - b[-1]
        sdot = -mu * q * max(m1, 0.0) / (M_pack - u[-1])  # Eq 8.19 (s decreases)
        adv = (mu * q - xi * sdot) / s                    # Landau-mapped advection speed
        du = np.zeros(Ng + 1); db = np.zeros(Ng + 1)
        du[1:] = -adv[1:] * (u[1:] - u[:-1]) / dxi        # upwind (outward flow)
        db[1:] = (xi[1:] * sdot / s) * (b[1:] - b[:-1]) / dxi \
            - q * np.clip(b[1:] - beta(q), 0.0, None)     # release (8.16)
        db[0] = -q * max(b[0] - beta(q), 0.0)
        return np.concatenate([du, db, [sdot]])

    y0 = np.concatenate([np.full(Ng + 1, 1.0 + m0), np.full(Ng + 1, 1.0), [1.0]])
    sol = solve_ivp(rhs, [0.0, t_end], y0, method="BDF", rtol=1e-7, atol=1e-9,
                    t_eval=np.linspace(0.0, t_end, n_save))
    U = sol.y[:Ng + 1]; S = sol.y[-1]
    U0 = U.copy(); U0[0] = sol.y[Ng + 1]                  # apply inflow BC to node 0
    q = np.array([flow(U0[:, k], S[k]) for k in range(len(S))])
    # Eq 8.33 global mass balance: int_0^s (m+b) dx + M(1-s) = s<u> + M(1-s)
    mb = np.array([S[k] * np.trapezoid(U0[:, k], xi) + M_pack * (1.0 - S[k])
                   for k in range(len(S))])
    return dict(t=sol.t, q=q, s=S, mass_balance=mb)


def q_infinity(p0, beta, **kw):
    """Asymptotic discharge q_inf at applied pressure p0."""
    return float(simulate(p0, beta, **kw)["q"][-1])


def q_infinity_curve(p0_array, beta, **kw):
    """q_inf(p0) sweep -- nonmonotone with an interior peak (Fig 8.6 shape)."""
    return np.array([q_infinity(float(p), beta, **kw) for p in p0_array])

"""machine_mode.py — Foster et al. 2025 pump/headspace machine mode.

Card: docs/cards/foster2025_2.md (ROADMAP item 1.6). RUNTIME machine stage: the
pump-characteristic + trapped-air-headspace infiltration model (their Eqs. 2-27)
that generates the pressure-node set and early-shot flow transient WITHOUT a
recorded pressure trace. Complements foster2025.infiltration (which consumes a
measured P(t)); this is the "machine mode" that produces it.

Three stages:
  pre-ponding   (t < t_p): pump-limited, front moves linearly (H = 0).
  post-ponding  (t_p <= t < t_s): coupled (s, H) ODEs as the headspace fills.
  post-saturation (t >= t_s): s = L, headspace relaxes.
Ponding position/time have closed forms (Eqs. 24-25). The authors report times
shifted by a fitted start-time alignment t_shift; reported = model + t_shift.

Notably the pump + headspace dynamics alone produce a mid-shot flow decline (the
P2 null baseline against which any kappa(t) compaction/swelling closure must be
gated) — its full minimum/recovery shape is validated against Fig 15 once the
digitized trace lands (deferred gate).

Verification (see validation/gates.py): reproduces the authors' ponding time
t_p = 0.823 s and saturation time t_s = 6.669 s from the Table I/II parameters.
"""
from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp


@dataclass
class FosterParams:
    """Table I (fine-grind fit). SI units."""
    L: float = 9.975e-3
    H0: float = 7.8e-3
    A: float = 0.002734
    mu: float = 0.315e-3
    rho: float = 965.0
    p_a: float = 1.01325e5
    Q_m: float = 317e-6 / 60
    R_f: float = 3.83e6
    g: float = 9.81
    p_c: float = 0.1e5
    p_m: float = 15e5
    beta: float = 1.226
    k: float = 2.97e-15
    phi_T: float = 0.322
    t_shift: float = 0.796


def p_h(H, p):
    """Headspace pressure (Eqs. 4-5): ideal trapped gas heated by beta."""
    return p.p_a * p.H0 * p.beta / (p.H0 - H)


def Q_pump(H, p):
    """Pump flow for a given headspace height (Eq. 7, positive root)."""
    disc = p.R_f ** 2 + 4 * ((p.p_m - p.p_a) / p.Q_m ** 2) * (p.p_m - p_h(H, p))
    return -p.Q_m ** 2 / (2 * (p.p_m - p.p_a)) * (p.R_f - np.sqrt(disc))


def f_bed(H, s, p):
    """Darcy flow into the bed top q|z=0 (Eq. 16/52)."""
    return -(p.k / (p.mu * s)) * (p.p_a - p.p_c - p_h(H, p) - p.rho * p.g * (H + s))


def ponding(p=None):
    """Closed-form ponding: (s_p [m], t_p_model [s], Q_p [m^3/s]) (Eqs. 24-25)."""
    p = p or FosterParams()
    Q_p = float(Q_pump(0.0, p))
    s_p = p.k * p.A * (p.p_a * (1 - p.beta) - p.p_c) / (p.k * p.A * p.rho * p.g - p.mu * Q_p)
    t_p = p.A * p.phi_T * s_p / Q_p
    return s_p, t_p, Q_p


def solve(p=None):
    """Integrate the post-ponding (s, H) ODEs to saturation. Returns a dict with
    the dense-output trajectory `sol` (model time), s_p, t_p, t_s (model times),
    Q_p. Used by the reported-time and figure-validation helpers."""
    p = p or FosterParams()
    s_p, t_p, Q_p = ponding(p)

    def rhs(t, y):
        s, H = y
        f = f_bed(H, s, p)
        return [f / p.phi_T, float(Q_pump(H, p)) / p.A - f]

    def hit_L(t, y):
        return y[0] - p.L
    hit_L.terminal = True; hit_L.direction = 1
    sol = solve_ivp(rhs, [t_p, 30.0], [s_p, 0.0], method="LSODA", events=hit_L,
                    rtol=1e-9, atol=1e-11, max_step=0.005, dense_output=True)
    return dict(sol=sol, s_p=s_p, t_p=t_p, t_s=float(sol.t_events[0][0]),
                Q_p=Q_p, p=p)


def _sH(t_model, r):
    """(s, H) at model time t_model [s] from a solve() result, staged."""
    p = r["p"]
    if t_model <= r["t_p"]:
        s = max(0.0, r["Q_p"] * t_model / (p.A * p.phi_T)) if t_model > 0 else 0.0
        return s, 0.0
    if t_model >= r["t_s"]:
        return p.L, float(r["sol"].sol(r["t_s"])[1])
    s, H = r["sol"].sol(t_model)
    return float(s), float(H)


def front_headspace_mm(t_exp, r=None):
    """(s, H) [mm] at experiment time t_exp [s] (= model time + t_shift)."""
    r = r or solve()
    s, H = _sH(t_exp - r["p"].t_shift, r)
    return s * 1e3, H * 1e3


def bed_flow_norm(t_exp, r=None):
    """Flow through the bed q|z=0 = min(Q_p, f(H,s)) normalised by Q_m
    (Fig 15(b) convention) at experiment time t_exp [s]."""
    r = r or solve()
    p = r["p"]
    tm = t_exp - p.t_shift
    if tm <= r["t_p"]:
        return r["Q_p"] / p.Q_m
    s, H = _sH(tm, r)
    return min(r["Q_p"], f_bed(H, s, p) * p.A) / p.Q_m


def flow_minimum(r=None):
    """(Q_min/Q_m, t_exp of the minimum) of the bed-flow trace (Fig 15)."""
    import numpy as np
    r = r or solve()
    t = np.linspace(r["t_p"], r["t_s"], 400) + r["p"].t_shift
    q = np.array([bed_flow_norm(ti, r) for ti in t])
    i = int(np.argmin(q))
    return float(q[i]), float(t[i])


def reported_times(p=None):
    """Ponding and saturation times in the experiment frame (+ t_shift), as the
    authors report them: t_p ~ 0.823 s, t_s ~ 6.669 s."""
    r = solve(p)
    return r["t_p"] + r["p"].t_shift, r["t_s"] + r["p"].t_shift

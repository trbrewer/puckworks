"""
puck_ensemble.py — Stage 4: mechanistic channeling / fines-migration model
===========================================================================

The Cameron et al. (2020) model assumes *homogeneous* flow through the puck.
Below grind setting ~1.7 the measured flow becomes uneven and the observed
extraction yield DROPS as grinding gets finer, while the homogeneous model
keeps rising (their Fig. 5: relative deviations of 13.1 / 6.1 / 2.6 % at
GS 1.1 / 1.3 / 1.5). This module supplies the missing mechanism in two rungs.

Rung A — static streamtube ensemble (calibrated)
------------------------------------------------
The puck is treated as K parallel streamtubes sharing the same pressure drop.
Tube i has a permeability multiplier k_i drawn from a unit-mean lognormal
with heterogeneity parameter sigma (physically: distribution / tamp quality,
made worse by fine, cohesive grinds). Darcy flux is linear in permeability,
so tube i sees superficial velocity q*k_i for the common shot duration T
(the shot ends when the *total* beverage mass hits target; unit-mean k keeps
mean flow, hence T, equal to the homogeneous shot).

Key trick: running the validated 1-D solver with pressure p*k_i and beverage
target m_out*k_i is exactly "flux k_i for duration T" — no solver changes.
Because EY is concave in k (fast tubes deplete and run blonde; slow tubes
stay rich but deliver little), any heterogeneity LOWERS ensemble EY
(Jensen's inequality). The ensemble average is computed by Gauss–Hermite
quadrature over ln k using a per-grind EY(k) response spline.

The closure sigma(GS) is calibrated to the paper's three experimental
deviation points through the fines volume fraction phi_1(GS) that the
microstructure model already tracks — no free GS dependence is introduced.

Rung B — dynamic fines migration (research, qualitative)
--------------------------------------------------------
Per tube, a detachable fraction of the fines erodes at a rate proportional
to local flow, opening the tube (channel erosion) while the mobilised fines
load the bottom of the bed / screen (blinding). Permeability responds as

    kappa_i(t) = k_i0 * (1 + a_open * E_i) / (1 + a_clog * E_i)^2,
    dE_i/dt    = lam_e * (q_i / q_ref) * (1 - E_i),

which contains the channeling instability: a slightly fast tube erodes
faster, opens further, and steals flow. Depending on (a_open, a_clog) the
same physics produces gushing channels, stable shots, or choking pucks.
Extraction runs on a vectorised port of the operator-split scheme validated
against the BDF reference in Stages 2–3.

Provenance: model constants and the homogeneous solver come from
espresso_model.py (Stage 1), which reproduces Cameron et al., Matter 2,
631–648 (2020) with mass-consistent accounting.
"""
from __future__ import annotations

import numpy as np
from dataclasses import dataclass, field
from numpy.polynomial.hermite import hermgauss
from scipy.interpolate import PchipInterpolator
from scipy.optimize import brentq, least_squares

from puckworks.models.cameron2020 import extraction_bdf as em

# Streamtube's per-bed-volume reinterpretation of the initial soluble concentration cs0 (Stage 1
# "physical mode"). This is a STREAMTUBE-LOCAL constant passed explicitly into Cameron via the
# simulate_shot(c_s0=...) parameter — importing this module must NOT mutate Cameron's global C_S0
# (that made Cameron import-order dependent). See extraction_bdf.simulate_shot's c_s0 parameter.
C_S0_STREAMTUBE = 118.0 / em.PHI_S


# ======================================================================
# Rung A — static streamtube ensemble
# ======================================================================

def lognormal_nodes(sigma: float, n: int = 15):
    """Unit-mean lognormal quadrature nodes/weights via Gauss-Hermite."""
    x, w = hermgauss(n)
    xi = np.sqrt(2.0) * x                    # standard normal nodes
    k = np.exp(sigma * xi - 0.5 * sigma ** 2)
    return k, w / np.sqrt(np.pi)


@dataclass
class EYResponse:
    """EY(k) response of the 1-D model at one grind setting.

    Built once from n_grid full solves (pressure p*k, target m_out*k), then
    any ensemble average EY(sigma) is a cheap quadrature over the spline.
    """
    gs: float
    p_bar: float = 5.0
    m_in: float = 0.020
    m_out: float = 0.040
    k_min: float = 0.02
    k_max: float = 8.0
    n_grid: int = 13
    lnk: np.ndarray = field(init=False)
    ey: np.ndarray = field(init=False)
    _spl: PchipInterpolator = field(init=False)

    def __post_init__(self):
        self.lnk = np.linspace(np.log(self.k_min), np.log(self.k_max), self.n_grid)
        eys = []
        for lk in self.lnk:
            k = float(np.exp(lk))
            r = em.simulate_shot(self.gs, p_bar=self.p_bar * k,
                                 m_in=self.m_in, m_out=self.m_out * k, c_s0=C_S0_STREAMTUBE)
            eys.append(r.EY)
        self.ey = np.array(eys)
        self._spl = PchipInterpolator(self.lnk, self.ey)

    def ey_of_k(self, k):
        lk = np.clip(np.log(np.asarray(k, float)), self.lnk[0], self.lnk[-1])
        return self._spl(lk)

    def ey_ensemble(self, sigma: float, n_gh: int = 15) -> float:
        if sigma <= 1e-9:
            return float(self.ey_of_k(1.0))
        k, w = lognormal_nodes(sigma, n_gh)
        return float(np.sum(w * self.ey_of_k(k)))

    def deficit(self, sigma: float) -> float:
        """Relative EY deficit vs the homogeneous shot, 0..1."""
        e0 = self.ey_of_k(1.0)
        return float(1.0 - self.ey_ensemble(sigma) / e0)

    def sigma_for_deficit(self, d_target: float) -> float:
        f = lambda s: self.deficit(s) - d_target
        return brentq(f, 1e-4, 3.0, xtol=1e-4)


# ---- sigma(GS) closure through the fines fraction --------------------

def phi1(gs) -> np.ndarray:
    return np.interp(gs, em.GS_GRID, em.PHI_S1_GRID)


def sigma_closure_power(gs, s_ref: float, m: float, gs_ref: float = 1.9):
    """sigma = s_ref * (phi1(gs)/phi1(gs_ref))^m — steepness via exponent."""
    return s_ref * (phi1(gs) / phi1(gs_ref)) ** m


def sigma_closure_exp(gs, a: float, b: float):
    """sigma = a * exp(b * phi1(gs)) — exponential sensitivity to fines."""
    return a * np.exp(b * phi1(gs))


def fit_closure(gs_pts, sigma_pts, form: str = "power"):
    """Least-squares fit of a closure through calibrated sigma points."""
    gs_pts = np.asarray(gs_pts, float)
    sig = np.asarray(sigma_pts, float)
    if form == "power":
        fun = lambda p: sigma_closure_power(gs_pts, p[0], p[1]) - sig
        res = least_squares(fun, x0=[0.05, 6.0], bounds=([1e-4, 0.1], [3.0, 40.0]))
        return {"form": "power", "s_ref": res.x[0], "m": res.x[1],
                "predict": lambda g: sigma_closure_power(g, *res.x), "cost": res.cost}
    fun = lambda p: sigma_closure_exp(gs_pts, p[0], p[1]) - sig
    res = least_squares(fun, x0=[1e-3, 40.0], bounds=([1e-8, 1.0], [10.0, 200.0]))
    return {"form": "exp", "a": res.x[0], "b": res.x[1],
            "predict": lambda g: sigma_closure_exp(g, *res.x), "cost": res.cost}


# ======================================================================
# Rung B — dynamic fines-migration ensemble (vectorised operator split)
# ======================================================================

def _sphere_grid(a: float, M: int):
    dr = a / (M - 1)
    r = np.arange(M) * dr
    edge = np.empty(M + 1)
    edge[0], edge[-1] = 0.0, a
    edge[1:M] = 0.5 * (r[:-1] + r[1:])
    V = (4.0 / 3.0) * np.pi * (edge[1:] ** 3 - edge[:-1] ** 3)
    Af = 4.0 * np.pi * edge[1:M] ** 2
    return r, V, Af, dr


def _thomas_factors(V, Af, dr, D, dt):
    M = len(V)
    lo = np.zeros(M); di = V / dt; up = np.zeros(M)
    w = Af * D / dr
    lo[1:] = -w;  di[1:] += w
    up[:-1] = -w; di[:-1] += w
    cp = np.empty(M); den = np.empty(M)
    cp[0] = up[0] / di[0]; den[0] = 1.0 / di[0]
    for k in range(1, M):
        mm = di[k] - lo[k] * cp[k - 1]
        den[k] = 1.0 / mm
        cp[k] = up[k] * den[k]
    return lo, cp, den


def _diffuse(cs, V, dt, lo, cp, den):
    """Implicit radial diffusion for cs[..., M] (batched Thomas)."""
    M = cs.shape[-1]
    d = np.empty_like(cs)
    d[..., 0] = (V[0] / dt) * cs[..., 0] * den[0]
    for k in range(1, M):
        d[..., k] = ((V[k] / dt) * cs[..., k] - lo[k] * d[..., k - 1]) * den[k]
    cs[..., M - 1] = d[..., M - 1]
    for k in range(M - 2, -1, -1):
        cs[..., k] = d[..., k] - cp[k] * cs[..., k + 1]


@dataclass
class DynamicResult:
    t: np.ndarray                # sample times
    q_tubes: np.ndarray          # (n_t, K) superficial velocity, m/s
    kappa: np.ndarray            # (n_t, K) permeability multiplier
    flow_gs: np.ndarray          # total beverage flow, g/s
    weight: np.ndarray           # cumulative beverage, g
    ey_cum: np.ndarray           # cumulative EY, %
    EY: float
    EY_tubes: np.ndarray         # (K,)
    tds: float
    t_shot: float
    target_reached: bool
    k0: np.ndarray               # initial multipliers
    E_final: np.ndarray          # eroded fines fraction per tube
    fines_mobilised_g: float     # detached fines mass (deposit + cup), g
    ey_homog_ref: float | None = None


def simulate_ensemble_dynamic(gs=1.9, p_bar=5.0, m_in=0.020, m_out=0.040,
                              K=12, sigma=0.5,
                              lam_e=0.0, a_open=0.0, a_clog=0.0, f_det=0.30,
                              N=32, M=18, dt_max=0.01, t_cap=120.0,
                              n_snap=140):
    """K coupled streamtubes with eroding fines and evolving permeability.

    sigma:   initial lognormal heterogeneity (quantile-midpoint sampling,
             deterministic and unit-mean).
    lam_e:   fines detachment rate per unit (q/q_ref), 1/s.
    a_open:  permeability gain from eroded fines (channel opening).
    a_clog:  permeability loss from mobilised fines loading the bed bottom
             (screen blinding); the (1+a_clog*E)^2 law is a Kozeny-type
             damage function.
    f_det:   detachable fraction of the fines family (affects extraction
             surface and the mobilised-mass bookkeeping).
    """
    # ---- microstructure & flow (from the Stage-1 module) ----
    phi_1, phi_2, a2, bet1, bet2 = em.grind_microstructure(gs)
    L_ref = em.bed_depth(0.020)
    L = em.bed_depth(m_in)
    q_ref = float(np.interp(gs, em.GS_Q_GRID, em.Q5_GRID)) * (p_bar / em.P_REF) * (L_ref / L)
    eps = 1.0 - em.PHI_S
    area = np.pi * em.R0 ** 2
    hz = L / N
    cs0, csat, krate = C_S0_STREAMTUBE, em.C_SAT, em.K_RATE

    # ---- tubes: deterministic unit-mean lognormal quantile midpoints ----
    from scipy.stats import norm
    xi = norm.ppf((np.arange(K) + 0.5) / K)
    k0 = np.exp(sigma * xi - 0.5 * sigma ** 2)
    k0 *= 1.0 / k0.mean()                      # exact unit mean at finite K
    wK = np.full(K, 1.0 / K)

    # ---- radial grids / diffusion operators ----
    _, V1, Af1, dr1 = _sphere_grid(em.A1, M)
    _, V2, Af2, dr2 = _sphere_grid(a2, M)
    sig1 = 4.0 * np.pi * em.A1 ** 2 / V1[-1]
    sig2 = 4.0 * np.pi * a2 ** 2 / V2[-1]

    kappa_bound = k0.max() * (1.0 + max(a_open, 0.0))
    dt = min(dt_max, 0.4 * hz * eps / (q_ref * kappa_bound))
    lo1, cp1, den1 = _thomas_factors(V1, Af1, dr1, em.D_S, dt)
    lo2, cp2, den2 = _thomas_factors(V2, Af2, dr2, em.D_S, dt)

    # ---- state ----
    cl = np.zeros((K, N))
    cs1 = np.full((K, N, M), cs0)
    cs2 = np.full((K, N, M), cs0)
    E = np.zeros(K)                            # eroded fines fraction
    m_cup = 0.0
    m_cup_tube = np.zeros(K)
    m_bev = 0.0
    t = 0.0

    steps = int(np.ceil(t_cap / dt))
    snap_every = max(1, int(np.ceil((m_out / (em.RHO_OUT * area * q_ref)) / dt / n_snap)))

    ts, qs, kap_s, flow_s, w_s, ey_s = [], [], [], [], [], []

    def kappa_of(Evec):
        return k0 * (1.0 + a_open * Evec) / (1.0 + a_clog * Evec) ** 2

    target = False
    for s in range(1, steps + 1):
        kap = kappa_of(E)
        q = q_ref * kap                        # (K,)

        # ---- 1) dissolution exchange (sub-cycled, vectorised) ----
        rem = dt
        guard = 0
        while rem > 1e-12 and guard < 400:
            guard += 1
            s1 = cs1[..., -1]; s2 = cs2[..., -1]
            b1 = bet1 * (1.0 - f_det * E)[:, None]     # fines surface shrinks
            G1 = krate * s1 * (s1 - cl) * (csat - cl)
            G2 = krate * s2 * (s2 - cl) * (csat - cl)
            ds1 = -sig1 * G1; ds2 = -sig2 * G2
            dcl = (b1 * G1 + bet2 * G2) / eps
            h = rem
            for v, dv in ((s1, ds1), (s2, ds2), (csat - cl, dcl)):
                a = np.abs(dv)
                mask = a > 1e-30
                if mask.any():
                    h = min(h, float((0.2 * np.maximum(np.abs(v), 1.0)[mask] / a[mask]).min()))
            cs1[..., -1] = np.maximum(s1 + h * ds1, 0.0)
            cs2[..., -1] = np.maximum(s2 + h * ds2, 0.0)
            cl = cl + h * dcl
            rem -= h

        # ---- 1b) fines erosion ODE ----
        if lam_e > 0.0:
            E = E + dt * lam_e * (q / q_ref) * (1.0 - E)
            E = np.clip(E, 0.0, 1.0)

        # ---- 2) intragrain diffusion (implicit) ----
        _diffuse(cs1, V1, dt, lo1, cp1, den1)
        _diffuse(cs2, V2, dt, lo2, cp2, den2)

        # ---- 3) advection (upwind, per tube) ----
        cadv = (dt * q / (eps * hz))[:, None]
        cl_up = np.empty_like(cl)
        cl_up[:, 0] = 0.0
        cl_up[:, 1:] = cl[:, :-1]
        cl = cl + cadv * (cl_up - cl)

        dm = area * q * cl[:, -1] * dt         # dissolved mass per tube (per w)
        m_cup_tube += wK * dm
        m_cup += float(np.sum(wK * dm))
        m_bev += float(np.sum(wK * area * q * em.RHO_OUT * dt))
        t += dt

        done = s == steps
        if m_bev >= m_out:
            target = True; done = True
        if s % snap_every == 0 or done:
            ts.append(t); qs.append(q.copy()); kap_s.append(kap.copy())
            flow_s.append(float(np.sum(wK * area * q * em.RHO_OUT)) * 1000.0)
            w_s.append(m_bev * 1000.0)
            ey_s.append(100.0 * m_cup / m_in)
        if done:
            break

    fines_mob = f_det * phi_1 * L * area * em.RHO_GROUNDS / em.PHI_S * float(np.sum(wK * E)) * 1000.0
    return DynamicResult(
        t=np.array(ts), q_tubes=np.array(qs), kappa=np.array(kap_s),
        flow_gs=np.array(flow_s), weight=np.array(w_s), ey_cum=np.array(ey_s),
        EY=100.0 * m_cup / m_in,
        EY_tubes=100.0 * m_cup_tube / (wK * m_in),
        tds=100.0 * m_cup / max(m_bev, 1e-9),
        t_shot=t, target_reached=target, k0=k0, E_final=E.copy(),
        fines_mobilised_g=fines_mob)


if __name__ == "__main__":
    # validation: sigma=0, no migration -> must match the BDF reference (streamtube's cs0 basis)
    ref = em.simulate_shot(1.9, c_s0=C_S0_STREAMTUBE)
    dyn = simulate_ensemble_dynamic(gs=1.9, K=1, sigma=0.0)
    print(f"BDF reference EY = {ref.EY:.3f} | dynamic port EY = {dyn.EY:.3f} "
          f"(diff {abs(ref.EY - dyn.EY):.3f})")

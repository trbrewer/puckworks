"""reduced.py — Grudeva et al. reduced infiltration-coupled extraction model.

RIGHTS STATUS — code RIGHTS_BLOCKED (issue #73). This module is a self-documented direct port of the
unlicensed upstream solver (github.com/YoanaGrudeva/espresso-model, licence: null); no permission is on
record. The EJAM article (CC-BY) licenses the equations/text, NOT this solver code. Rights truth is the
centralized `puckworks.rights` record. Retained in current history (shipped in v0.3.0) but NOT available
for Guided Pull Laboratory execution, native reference runners, adapters, or a newly approved release,
pending the #73 maintainer decision. Do NOT extend, re-enable, or promote without resolving #73; a
replacement must be an independent clean-room reimplementation from permitted equations/data only.

Card: docs/cards/grudeva2025.md (merged card of record; ROADMAP item 1.7b).
RUNTIME infiltration+extraction: a sharp wetting front sweeps the dry bed; behind
it two-population (fines/boulders) extraction proceeds, with matched asymptotics
collapsing the wet bed into a saturated region, a moving fines-depletion front
s_d(t), and a boulder-limited inlet region. Outputs first drip, a saturated exit
plateau of duration s_d^{-1}(1)-1, then blonding decay.

This is a FAITHFUL PORT of the authors' released reference solver
(https://github.com/YoanaGrudeva/espresso-model, espresso.ipynb) — S1 ref 45,
the code that generated S2 Figs 3-5. Porting the reference (rather than
re-deriving from the display equations) also settles LOG Issue 1 (G0): the
capacitance in BOTH the saturation-front ODE (`dsdt`) and the region-(i) update
(`A`) is B = phi_l/phi_T + phi_f/phi_T with **NO epsilon** — confirming the
adjudicated no-ε form is what the published solver implements.

Validation (see validation/gates.py + validation/slow/):
 - G0: capacitance carries no ε (asserted numerically).
 - G1/G2: reduced solve gives s_d^{-1}(1) ≈ 6.4 (published) and closes an
   order-of-magnitude solute budget.
 - G3: per-vial solubles reproduce the 14-shot vial dataset (data/grudeva2025/
   exp13_per_vial_stats.csv) — POST-FIT reconstruction (parameters fitted to it).
 - G4: κ from S1 Eq. 6.14 at 9.2 bar recovers the adjudicated κ ≈ 2.2e-15 m².

Scope (card): sharp planar front, instantaneous grain wetting, no capillarity /
CO2 / swelling / channeling; constant μ,ρ; single lumped solute; prescribed flow
(Darcy pre-drip + empirical post-drip). verification-gated (RC-2) until the
forthcoming companion dataset provides independent outlet-concentration data.
"""
from dataclasses import dataclass

import numpy as np


@dataclass
class GrudevaConfig:
    """Reference-solver config (espresso.ipynb). Dimensional SI + fitted chem."""
    phi_s: float = 0.85        # solid volume fraction
    phi_fs: float = 0.10       # fines fraction of solids
    phi_lb: float = 0.40       # boulder internal porosity
    af: float = 3.65e-6        # fines radius [m]
    ab: float = 228.69e-6      # boulder radius [m]
    Ptot: float = 9.2e6        # applied pressure [Pa] (reference solver value)
    L: float = 0.0084          # bed height [m]
    mu: float = 0.0003149      # viscosity [Pa s]
    t_drip: float = 5.0        # first-drip time [s]
    # flow post-drip linear fit (reference solver, from C1 data)
    flow_m: float = 2.3621915934596956e-05
    flow_c: float = -7.442495159999556e-06
    # chemistry (dimensional [kg/m^3], reference solver CELL 14)
    Dsb: float = 0.021         # dimensionless boulder diffusivity
    csat: float = 190.0
    cb0: float = 238.0
    cf0: float = 277.0

    def derived(self):
        phi_f = self.phi_fs * self.phi_s
        phi_l = 1 - self.phi_s
        phi_b = (1 - self.phi_fs) * self.phi_s
        phi_T = phi_l + phi_b * self.phi_lb
        b_f = 3 * phi_f / self.af
        b_b = 3 * phi_b / self.ab
        kappa = phi_T * self.L ** 2 * self.mu / (2 * self.Ptot * self.t_drip)
        qapp = 2 * kappa * self.Ptot / (self.L * self.mu)
        b0 = (b_f + b_b) / 2
        return dict(phi_f=phi_f, phi_l=phi_l, phi_b=phi_b, phi_T=phi_T,
                    b_f=b_f, b_b=b_b, kappa=kappa, qapp=qapp, b0=b0,
                    Qf=phi_T / (self.af * b0), Qb=phi_T / (self.ab * b0),
                    bf=b_f / b0, bb=b_b / b0)


def capacitance_B(cfg=None):
    """Region-(i) storage capacitance B = phi_l/phi_T + phi_f/phi_T (NO epsilon).

    This is the adjudicated no-ε form (LOG Issue 1 / G0): S1's bf/(3 Qf) equals
    S2's 1/(3 Qf) equals phi_f/phi_T. Returned as (B, phi_l/phi_T, phi_f/phi_T)."""
    cfg = cfg or GrudevaConfig()
    d = cfg.derived()
    term_l = d["phi_l"] / d["phi_T"]
    term_f = d["bf"] / (3 * d["Qf"])              # = phi_f/phi_T
    return term_l + term_f, term_l, term_f


def kappa_eq614(phi_T, L, mu, P_app, t_drip):
    """S1 Eq. 6.14: κ = φ_T L^2 μ / (2 P_app t_drip)."""
    return phi_T * L ** 2 * mu / (2 * P_app * t_drip)


def _dim_flow(t, cfg, d):
    with np.errstate(divide="ignore", invalid="ignore"):
        flow = (d["kappa"] / cfg.mu * cfg.Ptot
                / np.sqrt(2 * d["kappa"] * cfg.Ptot / (cfg.mu * d["phi_T"]) * t))
    data_flow = cfg.flow_m * t + cfg.flow_c
    on = 0.5 * (1 + np.tanh(6 * (t - cfg.t_drip)))
    return (1 - on) * flow + on * data_flow


def _boulder_rhs(c, cl_out, Dsb):
    M = len(c); dudt = np.zeros(M); dr2 = (1 / (M - 1)) ** 2
    c[-1] = cl_out
    dudt[0] = 6 / dr2 * (c[1] - c[0])
    ii = np.arange(1, M - 1)
    dudt[1:-1] = 1 / (ii * dr2) * ((ii + 1) * c[2:] - 2 * ii * c[1:-1] + (ii - 1) * c[:-2])
    return Dsb * dudt


def make_coffee(cfg=None, N=400, Nt=3000, n_vials=16, eps=None):
    """Solve the reduced model. Returns dict with s_d(t), t (nondim), and
    per-vial solubles gpv [g]. Faithful port of the reference solver.

    eps: None (default) uses the adjudicated no-ε capacitance B = phi_l/phi_T +
    phi_f/phi_T. Passing a value reproduces the S2 *printed* (erroneous) form
    B_ε = eps·phi_l/phi_T + phi_f/phi_T — used ONLY by the G1 discrimination
    ladder to show it does NOT match the published s_d^{-1}(1) (LOG Issue 1)."""
    cfg = cfg or GrudevaConfig()
    d = cfg.derived()
    phi_l, phi_T, bf, Qf, bb, Qb = (d["phi_l"], d["phi_T"], d["bf"], d["Qf"],
                                    d["bb"], d["Qb"])
    e = 1.0 if eps is None else eps               # ε-multiplier on phi_l/phi_T
    cf0, cb0 = cfg.cf0 / cfg.csat, cfg.cb0 / cfg.csat
    z = np.linspace(0, 1, N); dz = 1 / (N - 1)
    tend_nd = 32 / cfg.t_drip
    t_int = np.linspace(0, tend_nd, Nt); dt = tend_nd / (Nt - 1)
    cl = np.zeros((Nt, N)); sd = np.zeros(Nt); G_z = np.zeros(N)
    q = _dim_flow(t_int * cfg.t_drip, cfg, d) / d["qapp"]
    A = e * phi_l / phi_T + bf / (3 * Qf)         # capacitance (e=1 => no-ε)
    M = 30; dr = 1 / (M - 1)
    cb_all = np.zeros((N, M)) + cb0 + cfg.phi_lb
    wet = 0
    for i in range(Nt - 1):
        cl_last = cl[i, :]
        if sd[i] < 1:
            cl_s = cl_last[-1]
            sd[i + 1] = sd[i] + dt * q[i + 1] / (
                e * phi_l / phi_T + bf / (3 * Qf) * (cf0 - cl_s) / (1 - cl_s))
            wet = np.where(z <= sd[i + 1])[0][-1]
        else:
            sd[i + 1] = 1; wet = N - 1
        eta = z; cl_z = np.zeros(N)
        cl_z[:wet + 1] = np.interp(z[0:wet + 1], eta * sd[i + 1], cl_last)
        for j in range(wet + 1):
            cb_all[j, :] = cb_all[j, :] + dt * _boulder_rhs(cb_all[j, :], cl_z[j], cfg.Dsb)
            Fb = -cfg.Dsb * (cb_all[j, -1] - cb_all[j, -2]) / dr
            G_z[j] = Fb * bb / Qb
        G_eta = np.interp(eta, z[:wet + 1] / sd[i + 1], G_z[:wet + 1])
        ds = (sd[i + 1] - sd[i]) / dt
        for j in range(len(eta) - 1):
            cl[i + 1, j + 1] = (
                1 / (1 / dt + q[i + 1] / (A * sd[i + 1] * dz) - eta[j + 1] / dz * ds / sd[i + 1])
                * (G_eta[j] / A + 1 / dt * cl[i, j + 1]
                   - (-q[i + 1] / (A * sd[i + 1] * dz) + eta[j + 1] / dz * ds / sd[i + 1]) * cl[i + 1, j]))
    # per-vial solubles (16 vials x 2 s), exit saturated during the plateau
    t_vals = t_int * cfg.t_drip
    at = np.where(sd >= 1)[0][0]; t_at = t_vals[at]
    cl_out = cl[:, -1].copy()
    plateau = (t_vals <= t_at) & (t_vals > cfg.t_drip)
    cl_out[plateau] = 1.0
    R = 0.0295; Abed = np.pi * R ** 2
    vials_t = np.linspace(0, 30, n_vials); gpv = np.zeros(n_vials)
    for i in range(n_vials):
        vs, ve = vials_t[i], vials_t[i] + 2
        sel = (t_vals >= vs) & (t_vals < ve)
        if t_vals[sel][0] < cfg.t_drip < t_vals[sel][-1]:
            sel &= t_vals >= cfg.t_drip
        ti = t_vals[sel]
        clv = cl_out[sel] * cfg.csat
        with np.errstate(invalid="ignore"):
            vflow = _dim_flow(ti, cfg, d)
            gpv[i] = np.trapezoid(vflow * clv, ti) * Abed
    # s_d^{-1}(1): FIRST time the depletion front reaches the exit (sd stays
    # clamped at 1 afterwards, so interpolate the first crossing, not np.interp
    # over the whole flat-topped array).
    hit = np.where(sd >= 1.0)[0]
    if len(hit) and hit[0] > 0:
        i1 = hit[0]; s0, s1 = sd[i1 - 1], sd[i1]
        sd_inv_1 = float(t_int[i1 - 1] + (1.0 - s0) / (s1 - s0) * (t_int[i1] - t_int[i1 - 1]))
    else:
        sd_inv_1 = float("nan")
    return dict(sd=sd, t=t_int, gpv=gpv, sd_inv_1=sd_inv_1,
                total_solubles_g=float(gpv[3:].sum() * 1e3))

"""coupled_bed.py — mo2023_2 depth-resolved coupled bed extraction (Fig 8) [WIP].

*** STATUS: WIP / not registered, not gated. ***
(a) NORMALIZATION BUG FIXED (2026-07-11): the grain->bed flux took du/dxi where
    it needed dC/dxi (state is u=xi*C) -> ~12x solute loss, un-conserving mass;
    plus a spurious eps_p in the inventory. Fixed: with adequate time sampling
    mass conserves to 0.993 and eluted_frac -> ~1.0 of the grain inventory at
    full extraction. yield_frac is now a true fraction of the grain content.
(b) STILL TODO: the card's REQUIRED initial filling front (Eqs 29-30) -- until
    it is in, every cell extracts from t=0 and over-extracts, so do NOT score
    within-bars yet (check foster2025.infiltration reuse first).
(c) STILL TODO: reconcile with the paper's exact Appendix A.2 numerics.
Preserved as a continuation point, not a finished component.



The full model behind the card's gate-3 (type-M yield/strength within replicate
bars, M_c<30 g). The reduced mo2023_2.extraction treated the bed as one well-mixed
pool and under-extracted at low beverage mass; here the bed is depth-resolved
(their Eqs 19-24): clean water enters the top, flows down through N_z layers, and
picks up solute from the fine+coarse representative grains in each layer (their
Eqs 9-17 hindered-diffusion grains with the partition surface BC c(R)=c_b/K), so
the outlet concentration integrates the whole column and the early-shot yield
rises correctly.

Fixed-flow mode (their fixed-q case, which is what Fig 8 measures; swelling is
near-invisible there, mo2023_2.extraction gate-4). Grain diffusion is solved on a
shared normalized radius xi=r/R with a per-grain rate Deff/R^2 (vectorized over
all N_z x 2 grains). Observables: yield = eluted solute / dose (Eq 37), strength
= eluted / eluted-volume (Eq 38). Absolute level uses a single extractable-
inventory scale (the max EY), NOT tuned per point.
"""
import numpy as np
from scipy.integrate import solve_ivp

from puckworks import data as _d

EPS_P0 = 0.4; BETA = 3.2; H_C = 2.0; D_B = 2.0e-9    # grain diffusion (card)
K_PART = 0.9; EPS_B = 0.17                            # partition, bed porosity
BED_RADIUS_M = 0.029; BED_HEIGHT_M = 0.0135           # 2-shot rig geometry
RHO_W = 997.0


def _deff():
    return EPS_P0 * D_B / (BETA * H_C)                 # hindered intraparticle diffusivity


def simulate_bed(powder, q_mL_s, dose_g=None, t_end=40.0, N_z=14, M=8,
                 K=K_PART, eps_b=EPS_B, n_save=120):
    """Depth-resolved fixed-flow extraction. Returns t, beverage_mass(t) [g],
    yield_frac(t) (eluted / extractable inventory), strength(t) (eluted conc)."""
    row = {r["powder"]: r for r in _d.mo2_granulometry()}[powder]
    tf, tc = row["theta_f"], row["theta_c"]
    Rf, Rc = row["2R_f_um"] / 2e6, row["2R_c_um"] / 2e6
    A = np.pi * BED_RADIUS_M ** 2; L = BED_HEIGHT_M
    Q = q_mL_s * 1e-6                                   # m^3/s
    v = Q / (eps_b * A)                                # pore velocity (down the bed)
    dz = L / N_z
    Deff = _deff()
    # two grain populations per layer -> N_g = 2*N_z grains, flattened (pop, z)
    R = np.concatenate([np.full(N_z, Rf), np.full(N_z, Rc)])
    theta = np.concatenate([np.full(N_z, tf), np.full(N_z, tc)])
    zidx = np.concatenate([np.arange(N_z), np.arange(N_z)])   # layer of each grain
    rate = Deff / R ** 2                                # per-grain diffusion rate (1/s)
    Vgrain = 4.0 / 3.0 * np.pi * R ** 3
    # grains per unit bed volume in a layer, weighted by population fraction
    n_per_vol = (1.0 - eps_b) * theta / Vgrain
    xi = np.linspace(0.0, 1.0, M + 1); dxi = 1.0 / M
    Ng = len(R)
    # state: u = xi*C_s for interior nodes 1..M-1 per grain (C_s0=1 normalized) + c_b[N_z]
    nU = Ng * (M - 1)

    def unpack(y):
        u = y[:nU].reshape(Ng, M - 1); c_b = y[nU:nU + N_z]
        return u, c_b

    def rhs(t, y):
        u, c_b = unpack(y)
        c_surf = np.clip(c_b[zidx] / K, 0.0, None)      # partition surface (extraction-only)
        full = np.empty((Ng, M + 1))
        full[:, 0] = 0.0; full[:, M] = c_surf * 1.0     # u(xi=1)=1*C_surf
        full[:, 1:M] = u
        d2 = (full[:, 2:] - 2.0 * full[:, 1:M] + full[:, :M - 1]) / dxi ** 2
        du = rate[:, None] * d2
        # grain outflux (per grain) = -Deff 4pi R dC/dxi|_1. State is u=xi*C, so
        # reconstruct C = u/xi at the surface nodes BEFORE the gradient (the bug
        # was taking du/dxi here, which broke grain<->bed mass conservation).
        Cn = full[:, M]                                 # xi=1 -> C = u
        Cn1 = full[:, M - 1] / xi[M - 1]
        Cn2 = full[:, M - 2] / xi[M - 2]
        dCdxi_R = (3.0 * Cn - 4.0 * Cn1 + Cn2) / (2.0 * dxi)
        flux = -Deff * 4.0 * np.pi * R * dCdxi_R        # >0 leaving the grain
        src_grain = n_per_vol * flux                    # per grain-type, per bed volume
        # sum fine+coarse source into each layer
        src = np.zeros(N_z)
        np.add.at(src, zidx, src_grain)
        # bed advection (upwind, downward): c_b[z] fed by c_b[z-1]; inlet c_b top = 0
        c_up = np.concatenate([[0.0], c_b[:-1]])
        dc_b = src / eps_b - v * (c_b - c_up) / dz
        return np.concatenate([du.ravel(), dc_b])

    y0 = np.concatenate([(xi[1:M] * 1.0)[None, :].repeat(Ng, 0).ravel(), np.zeros(N_z)])
    t_eval = np.linspace(0.0, t_end, n_save)
    sol = solve_ivp(rhs, [0.0, t_end], y0, method="BDF", t_eval=t_eval,
                    rtol=1e-6, atol=1e-9)
    c_out = sol.y[nU + N_z - 1, :]                       # outlet layer concentration
    t = sol.t
    elut = np.concatenate([[0.0], np.cumsum(0.5 * (c_out[1:] + c_out[:-1]) * np.diff(t)) * Q])
    vol = Q * t
    inv = (1.0 - eps_b) * A * L                          # grain solute content (C_s0=1 over grain)
    yield_frac = elut / inv
    strength = np.divide(elut, vol, out=np.zeros_like(elut), where=vol > 0)
    bev_g = vol * RHO_W * 1e3
    # --- mass balance (diagnostic): grain content + bed pore + eluted vs initial ---
    Vcell = A * dz
    n_grains = n_per_vol * Vcell                          # grains of each type per its layer
    xi_full = xi
    grain_tot = np.zeros(len(t))
    for k in range(len(t)):
        u_k = sol.y[:nU, k].reshape(Ng, M - 1)
        c_surf_k = np.clip(sol.y[nU + zidx, k] / K, 0.0, None)
        full = np.empty((Ng, M + 1)); full[:, 0] = 0.0; full[:, M] = c_surf_k; full[:, 1:M] = u_k
        Cr = np.zeros((Ng, M + 1)); Cr[:, 1:] = full[:, 1:] / xi_full[1:]; Cr[:, 0] = full[:, 1] / xi_full[1]
        content_per_grain = 4.0 * np.pi * R ** 3 * np.trapezoid(Cr * xi_full ** 2, xi_full, axis=1)
        grain_tot[k] = float(np.sum(n_grains * content_per_grain))
    pore_tot = np.array([float(np.sum(sol.y[nU:nU + N_z, k])) for k in range(len(t))]) * eps_b * Vcell
    inv_true = float(np.sum(n_grains * (4.0 * np.pi * R ** 3 / 3.0)))   # initial grain content
    balance = (grain_tot + pore_tot + elut) / inv_true
    return dict(t=t, beverage_g=bev_g, yield_frac=yield_frac, strength=strength,
                mass_balance=balance, inv_true=inv_true, inv_used=inv,
                grain_frac=grain_tot / inv_true, eluted_frac=elut / inv_true,
                pore_frac=pore_tot / inv_true)


def yield_strength_curve(powder, q_mL_s, M_c_targets, EY_scale, **kw):
    """Absolute yield [%] and strength at target beverage masses, using a single
    inventory scale EY_scale (max EY). Returns dict M_c -> (yield%, strength)."""
    r = simulate_bed(powder, q_mL_s, t_end=max(M_c_targets) / q_mL_s * 1.4, **kw)
    out = {}
    for mc in M_c_targets:
        yf = np.interp(mc, r["beverage_g"], r["yield_frac"])
        st = np.interp(mc, r["beverage_g"], r["strength"])
        out[mc] = (float(yf * EY_scale), float(st))
    return out

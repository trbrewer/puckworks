"""coupled_bed.py — mo2023_2 depth-resolved coupled bed extraction (Fig 8) [WIP].

*** STATUS: registered (mo2023_2.coupled_bed, extraction/runtime). *** Resolved
via the (a)->(b)->(c) plan:
(a) mass-conservation bug FIXED: the grain->bed flux took du/dxi where it needed
    dC/dxi (state u=xi*C) -> ~12x solute loss; plus a spurious eps_p in the
    inventory. Now conserves to ~0.99 (converged), eluted_frac -> ~1.0.
(b) filling front (Eqs 29-30) added: fixed-q linear plug-fill dz_f/dt=q/(eps_b A)
    with the cup = pumped - dead-volume correction (the first ~eps_b V_bed of
    water fills the puck and never reaches the cup). -> 5/9 within bars (vs the
    reduced lumped bed's 4/9) and shape-spread 37% (vs 110%), UNTUNED.
(c) Appendix-A.2 numerics NOT matched -- moot: the M_c=20 residual is CONVERGED
    (refinement worsens it slightly), so it is genuine model-vs-data disagreement
    matching the card's 'overestimates beyond M_c~30 g', not an implementation gap.



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
                 K=K_PART, eps_b=EPS_B, n_save=120, filling_front=False):
    """Depth-resolved fixed-flow extraction. Returns t, beverage_mass(t) [g],
    yield_frac(t) (eluted / extractable inventory), strength(t) (eluted conc).

    filling_front (card Eqs 29-30): a plug-flow dry->wet fill from the top at the
    pore velocity dz_f/dt = q/(eps_b A) (LINEAR front, the fixed-flow analog of
    foster2025.infiltration's fixed-pressure sqrt-time sharp front -- same
    infiltration<->extraction coupling family, different driving). Cells below
    the front are dry: their grains do not extract until wetted."""
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
    v_fill = Q / (eps_b * A)                            # front speed dz_f/dt (m/s)
    z_center = (np.arange(N_z) + 0.5) * dz              # cell centres
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
        if filling_front:                                # dry cells (ahead of z_f) don't extract
            z_f = min(v_fill * t, L)
            wet = (z_center[zidx] < z_f).astype(float)
            flux = flux * wet
            du = du * wet[:, None]                        # freeze grain diffusion when dry
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
    # CUP beverage lags the pumped water by the bed dead volume when a filling
    # front is on (that water fills the puck and never reaches the cup); the
    # outlet only flows after the front reaches the bottom at t_fill.
    t_fill = (eps_b * A * L / Q) if filling_front else 0.0
    vol = Q * np.maximum(t - t_fill, 0.0)                # volume out of the CUP
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


def fig8_metrics(powder="M", N_z=12, M=8, n_save=220):
    """Both scoring metrics for the card gate-3 (type-M, M_c<30 g), untuned: the
    within-bars count at the single best EY_scale, and the implied-scale SHAPE
    spread (how consistent the yield(M_c) shape is -- the real signal of whether
    depth resolution does physical work). Also the mass-balance floor. Filling
    front ON (required). The reduced lumped bed scores 4/9 with a ~110% spread."""
    from puckworks import data as _d
    ys = [r for r in _d.mo2_yield_strength() if r["powder"] == powder and r["M_c_g"] < 30]
    pts = {}
    mb = 1.0
    for q in (2, 3, 4):
        r = simulate_bed(powder, q, t_end=35.0, N_z=N_z, M=M, n_save=n_save,
                         filling_front=True)
        mb = min(mb, float(np.min(r["mass_balance"][r["t"] > 3.0])))
        for x in [z for z in ys if z["q_mL_s"] == q]:
            pts[(q, x["M_c_g"])] = (float(np.interp(x["M_c_g"], r["beverage_g"],
                                    r["yield_frac"])), x)
    scs = [x["yield_pct"] / yf for (yf, x) in pts.values() if yf > 0]
    scales = np.linspace(15.0, 120.0, 200)
    nwin = lambda sc: sum(1 for (yf, x) in pts.values()
                          if abs(yf * sc - x["yield_pct"]) <= max(x["yield_err_pct"], 0.5))
    best = max(scales, key=nwin)
    return dict(within_bars=nwin(best), n_points=len(pts), best_EY_scale=round(best, 1),
                shape_spread_pct=round((max(scs) / min(scs) - 1) * 100, 0),
                mass_balance_floor=round(mb, 3))


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

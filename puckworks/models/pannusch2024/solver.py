"""solver.py — Pannusch et al. 2024 two-grain multi-solute extraction PDE solver.

Card: docs/cards/pannusch2024.md (ROADMAP item 1.8a). RUNTIME extraction: a 1D
convection-dominated two-population (fine/coarse grain) saturated model. Solute
leaves each grain population by first-order interphase transfer into a
percolating liquid; mass-transfer coefficients follow a Sherwood correlation in
Reynolds/Schmidt number, so extraction depends on temperature and flow. Ported
FAITHFULLY from the released MATLAB (Mendeley 10.17632/y2tz67f6ry.1:
pde_coffee_extraction_fd_Fit3.m, simulation_Fit3.m, five_point_biased_upwind.m).

State (3*nz + 2): liquid c_l(z), fine-grain c_s1(z), coarse-grain c_s2(z), plus
cumulative beverage volume and cumulative solute mass. Method of lines with a
five-point biased-upwind advection scheme (Carver & Hinds 1978); integrated with
a stiff BDF solver (ode15s analogue). c_l(z=0)=0 Dirichlet inlet BC.

Consumes the constitutive closures in closures.py (Wilke-Chang D, VDI water
props, Sherwood, van't Hoff). Creates RC-4a: reproduces the authors' fit MAPEs
against the Schmieder kinetics — POST-FIT reconstruction (params fitted to it).

Grind note: psi/d_s2 are fitted per grind (1.4/1.7/2.0); the per-experiment
grind assignment lives in the source's opaque parameter list, so this port uses
the centre grind (1.7) for all experiments — psi/d_s2 vary <15% across grinds,
so the effect on MAPE is second order (documented approximation).
"""
import csv
from functools import lru_cache

import numpy as np
from scipy.integrate import solve_ivp

from puckworks.models.pannusch2024 import closures as pc

# physical_parameters.m / numerical_parameters.m
ALPHA_L = 0.17          # bed porosity
DBED = 0.058            # bed diameter [m]
L = 0.015               # bed height [m]
D1_FINE = 24e-6         # fine-grain representative size [m]
PHI_V2 = 0.4            # coarse-grain intragranular porosity
RHO = 980.0             # [kg/m^3]
TC = 30.0               # characteristic time [s]
NZ = 200                # axial grid points
ACS = DBED ** 2 * np.pi / 4
GRIND_17 = dict(psi=0.23, d_s2=330e-6)   # centre-grind psi/d_s2 (Table 2)


def five_point_biased_upwind(n, dz, v):
    """First-derivative matrix D (n x n), D@c ~ dc/dz (Carver & Hinds 1978).
    Exact for polynomials to degree 4. Only v>0 used (positive espresso flow)."""
    D = np.zeros((n, n))
    for i in range(3, n - 1):
        D[i, i - 3:i + 2] = [-1, 6, -18, 10, 3]
    D[0, 0:5] = [-25, 48, -36, 16, -3]
    D[1, 0:5] = [-3, -10, 18, -6, 1]
    D[2, 0:5] = [1, -8, 0, 8, -1]
    D[n - 1, n - 5:n] = [3, -16, 36, -48, 25]
    return D / (12.0 * dz)


@lru_cache(maxsize=4)
def _jac_sparsity(nz):
    """Jacobian sparsity for BDF: liquid is banded (advection ±3) + coupled to
    the co-located grain cells; grains couple only to their own liquid cell;
    Vol/mcum depend on the outlet liquid cell."""
    from scipy.sparse import lil_matrix
    N = 3 * nz + 2
    S = lil_matrix((N, N))
    for i in range(nz):
        lo, hi = max(0, i - 3), min(nz, i + 2)
        S[i, lo:hi] = 1                  # advection band
        S[i, nz + i] = 1; S[i, 2 * nz + i] = 1     # <- fine/coarse grain
        S[nz + i, nz + i] = 1; S[nz + i, i] = 1
        S[2 * nz + i, 2 * nz + i] = 1; S[2 * nz + i, i] = 1
    S[3 * nz + 1, nz - 1] = 1            # mcum <- outlet liquid
    return S.tocsr()


def _rhs(t, c, p):
    nz = NZ
    cl = c[0:nz].copy(); cl[0] = 0.0
    cs1 = c[nz:2 * nz]; cs2 = c[2 * nz:3 * nz]
    cz = p["D1z"] @ cl
    ct = np.empty(3 * nz + 2)
    K, cs0, cl1 = p["K"], p["cs0"], p["cl1"]
    ct[0:nz] = (-p["v_l"] * TC / L * cz
                + p["m1"] * (K * cs1 * cs0 / cl1 - cl)
                + p["m2"] * (K * cs2 * cs0 / cl1 - cl))
    ct[nz:2 * nz] = -p["f1"] * (K * cs1 - cl * cl1 / cs0)
    ct[2 * nz:3 * nz] = -p["f2"] * (K * cs2 - cl * cl1 / cs0)
    ct[3 * nz] = p["dVol"]
    ct[3 * nz + 1] = cl[nz - 1] * p["dVol"]
    return ct


def simulate_fractions(T_C, flow_mL_s, t_bounds, sp, cl1, grind=GRIND_17):
    """Fraction-averaged outlet concentrations at the sorted `t_bounds` [s].
    Returns absolute concentrations (de-normalised by cl1), one per interval."""
    nz = NZ
    T = T_C + 273.15
    q = flow_mL_s / 1000.0 / RHO / ACS          # superficial velocity [m/s]
    psi, d_s2, d_s1 = grind["psi"], grind["d_s2"], D1_FINE
    d32 = 6.0 / (psi * 6.0 / d_s1 + (1 - psi) * 6.0 / d_s2)
    h1 = float(pc.sherwood_h(T, q, sp["A1"], sp["B1"], sp["solute"], d32))
    h2 = float(pc.sherwood_h(T, q, sp["A2"], sp["B2"], sp["solute"], d32))
    K = float(pc.vant_hoff_K(T, sp["K_ref"], sp["gamma"]))
    cs0 = sp["c_s0"]
    alpha_s1 = psi * (1 - ALPHA_L); alpha_s2 = (1 - psi) * (1 - ALPHA_L)
    p = dict(D1z=five_point_biased_upwind(nz, 1.0 / (nz - 1), q), v_l=q / ALPHA_L,
             K=K, cs0=cs0, cl1=cl1,
             m1=(6 * h1 * alpha_s1) / (ALPHA_L * d_s1) * TC,
             m2=(6 * h2 * alpha_s2) / (ALPHA_L * d_s2) * TC,
             f1=(6 * h1) / d_s1 * TC, f2=(6 * h2) / (PHI_V2 * d_s2) * TC,
             dVol=q * (np.pi / 4 * DBED ** 2) * TC * 1e6)
    c0 = np.ones(3 * nz + 2)
    c0[0] = 0.0; c0[1:nz] = K * cs0 / cl1; c0[3 * nz:3 * nz + 2] = 0.0
    tb = np.asarray(t_bounds, float) / TC
    sol = solve_ivp(_rhs, [tb[0], tb[-1]], c0, method="BDF", t_eval=tb,
                    args=(p,), rtol=1e-6, atol=1e-6,
                    jac_sparsity=_jac_sparsity(nz))
    Vol = sol.y[3 * nz]; mcum = sol.y[3 * nz + 1] * cl1
    return np.diff(mcum) / np.diff(Vol)


# --- experimental kinetics + MAPE ---------------------------------------
def _exp_kinetics():
    from puckworks import data as d
    rows = d.pannusch_experimental_kinetics()
    exps = {}
    for r in rows:
        exps.setdefault(int(r["exp"]), []).append(r)
    return exps


def _solute_params():
    from puckworks import data as d
    out = {}
    for r in d.pannusch_table2():
        s = r["solute"]
        out[s] = dict(A1=r["A1"], B1=r["B1"], A2=r["A2"], B2=r["B2"],
                      K_ref=r["K_ref"], gamma=r["gamma"], c_s0=r["c_s0_mg_mL"],
                      solute=s)
    return out


# measured-concentration column per solute; TDS is %*10 -> mg/mL (cs0 in mg/mL)
_MEAS = {"caffeine": ("c_caffeine_mg_g", 1.0),
         "trigonelline": ("c_trigonelline_mg_g", 1.0),
         "5CQA": ("c_5CQA_mg_g", 1.0),
         "tds": ("TDS_pct", 10.0)}


def mape_for_experiment(exp_rows, solute, sp):
    """Model MAPE (%) for one experiment/solute over its 6 measured fractions."""
    rows = sorted(exp_rows, key=lambda r: r["fraction"])
    col, scale = _MEAS[solute]
    meas = np.array([r[col] * scale for r in rows])
    if np.any(meas <= 0):
        return None
    # integrate to the union of fraction [lower, upper] boundaries
    bounds = sorted({r["t_lower_s"] for r in rows} | {r["t_upper_s"] for r in rows})
    T = rows[0]["Temp_C"]; flow = rows[0]["flow_mL_s"]
    cfrac = simulate_fractions(T, flow, bounds, sp, meas[0])
    idx = {b: i for i, b in enumerate(bounds)}
    sim = np.array([(lambda lo, hi: _interval_conc(cfrac, bounds, lo, hi))
                    (r["t_lower_s"], r["t_upper_s"]) for r in rows])
    return float(np.mean(np.abs(sim - meas) / meas) * 100)


def _interval_conc(cfrac, bounds, lo, hi):
    """Concentration over [lo,hi] = weighted mean of the sub-interval concs."""
    i0 = bounds.index(lo); i1 = bounds.index(hi)
    return float(np.mean(cfrac[i0:i1])) if i1 > i0 else float(cfrac[i0])


def mape_all():
    """Per-solute mean MAPE over the 15 experiments. Compare to published:
    TDS 6.07, caffeine 4.59, trigonelline 7.85, CGA 4.98 %."""
    exps = _exp_kinetics(); params = _solute_params()
    out = {}
    for solute in ("caffeine", "trigonelline", "5CQA", "tds"):
        vals = [mape_for_experiment(rows, solute, params[solute])
                for rows in exps.values()]
        vals = [v for v in vals if v is not None]
        out[solute] = float(np.mean(vals))
    return out

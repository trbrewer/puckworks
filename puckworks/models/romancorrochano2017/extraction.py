"""extraction.py — Roman-Corrochano 2017 multi-scale diffusion extraction.

Card: docs/cards/romancorrochano2017_extraction.md (ROADMAP item 3.5). A pure
Fickian, MW-resolved extraction model: soluble solids diffuse out of spherical
grains (effective diffusivity Deff, hindered by microstructure) into either a
well-mixed vessel (particle/stirred scale, Eqs. 3.28-3.34) or a lumped bed with
flow-through (bed scale, Eqs. 3.35-3.38, del Valle & de la Fuente linear-axial
reduction). No surface-dissolution kinetics (contrast cameron2020) -- the surface
is held at partition equilibrium C_s(R) = C_b/K.

The model's headline is a *parameter-free* chain: microstructural Deff (Table 4.9,
never fitted) -> espresso yield within the reported MPE. We reproduce it at the
levels we can verify WITHOUT the raw experimental curves (which the thesis never
published in machine-readable form): the spherical-diffusion solver is verified
against the classic Crank analytic release, and the Deff/MW/temperature TRENDS
are checked against the real parameter tables. The reported MPE numbers stay as
data gates (gate_roman_bed_mpe_parameter_free, gate_roman_y0_ceiling_...); this
module supplies the solver behind them, not a re-derivation of their MPE.

MW classes (species) are independent (own Deff, K, inventory) -> summed for the
total yield. Concentrations are normalized (C_s0 = 1); absolute EY = fraction x y0.

Not modeled (card): swelling (S=1, none observed), external film resistance (Biot
small), axial dispersion, re-adsorption; the lumped bed assumes L ~ 2 R_bed.
"""
import numpy as np
from scipy.integrate import solve_ivp

from puckworks import data as _d

# --- MW-class labels used across the Deff table -----------------------------
MW_CLASSES = ("low", "med", "high", "vhigh")


# --- analytic reference (Crank, constant-surface / infinite sink) ------------
def crank_release(Deff, R, t, nterms=200):
    """Fractional release M_t/M_inf from a sphere into an infinite sink
    (surface concentration held at 0), Crank Eq.: 1 - 6/pi^2 sum 1/n^2 exp(-Deff
    n^2 pi^2 t / R^2). The verification twin for the numerical solver."""
    tau = Deff * np.asarray(t, float) / R ** 2
    n = np.arange(1, nterms + 1)[:, None]
    s = np.sum(np.exp(-(n * np.pi) ** 2 * tau[None, :]) / n ** 2, axis=0)
    return 1.0 - 6.0 / np.pi ** 2 * s


# --- core spherical-diffusion solver (method of lines, u = r C_s) ------------
def _sphere_rhs_factory(Deff, R, N):
    """Build the interior-node RHS for u = r*C_s on r in [0,R] with N cells.
    u(0)=0 (finiteness at the centre); u(R) = R*C_surface is supplied per step."""
    dr = R / N

    def rhs(u_int, c_surface):
        full = np.empty(N + 1)
        full[0] = 0.0
        full[N] = R * c_surface
        full[1:N] = u_int
        d2 = (full[2:] - 2.0 * full[1:-1] + full[:-2]) / dr ** 2
        return Deff * d2, full

    return rhs, dr


def _content(full, r, C0=1.0):
    """Solid solute content = integral C_s dV = 4pi integral u r dr (C=u/r)."""
    Cr = np.empty_like(full)
    Cr[0] = full[1] / r[1] if r[1] > 0 else C0     # centre by continuity
    Cr[1:] = full[1:] / r[1:]
    return np.trapezoid(Cr * r ** 2, r)


def sphere_release(Deff, R, t_eval, N=100):
    """Numerical fractional release into an infinite sink (surface pinned to 0),
    for verification against crank_release."""
    rhs, dr = _sphere_rhs_factory(Deff, R, N)
    r = np.linspace(0.0, R, N + 1)

    def ode(t, u):
        d2, _ = rhs(u, 0.0)
        return d2
    u0 = r[1:N] * 1.0
    sol = solve_ivp(ode, [0.0, t_eval[-1]], u0, t_eval=t_eval, method="BDF",
                    rtol=1e-9, atol=1e-11)
    Minf = np.trapezoid(np.ones(N + 1) * 1.0 * r ** 2, r)
    out = []
    for k in range(sol.y.shape[1]):
        full = np.empty(N + 1); full[0] = 0.0; full[N] = 0.0; full[1:N] = sol.y[:, k]
        out.append(1.0 - _content(full, r) / Minf)
    return np.array(out)


# --- stirred vessel: sphere coupled to a finite well-mixed bath (Eqs 3.28-34) -
def stirred_vessel(Deff, R, K, pore_to_bath, t_eval, N=100):
    """Fractional extraction into a finite well-mixed bath. pore_to_bath =
    V_pore_total / V_bath sets the dilution; surface BC C_s(R) = C_b/K.

    Returns (t, frac) where frac = extracted / total-extractable-solute. At
    equilibrium frac -> 1/(1 + pore_to_bath/K) (dilute bath -> 1, i.e. y0)."""
    rhs, dr = _sphere_rhs_factory(Deff, R, N)
    r = np.linspace(0.0, R, N + 1)
    Vsphere = 4.0 / 3.0 * np.pi * R ** 3
    # bath volume scaled so that (pore volume seen by one representative sphere)
    # / V_bath = pore_to_bath. Work per representative particle: V_bath_eff.
    V_bath = Vsphere / pore_to_bath

    def ode(t, y):
        u = y[:N - 1]; c_b = y[N - 1]
        d2, full = rhs(u, c_b / K)
        # flux OUT of the sphere surface = -Deff * A * dC/dr|_R
        dCdr_R = ((c_b / K) - full[N - 1] / r[N - 1]) / dr
        flux = -Deff * 4.0 * np.pi * R ** 2 * dCdr_R      # >0 leaving the solid
        dcb = flux / V_bath
        return np.concatenate([d2, [dcb]])
    y0 = np.concatenate([r[1:N] * 1.0, [0.0]])
    sol = solve_ivp(ode, [0.0, t_eval[-1]], y0, t_eval=t_eval, method="BDF",
                    rtol=1e-8, atol=1e-10)
    M_total = np.trapezoid(np.ones(N + 1) * r ** 2, r)     # initial solid content
    extracted = sol.y[N - 1, :] * V_bath / (4.0 * np.pi)   # C_b*Vb as sphere-content units
    return sol.t, extracted / M_total


# --- lumped bed with flow-through (Eqs 3.35-3.38) ----------------------------
def bed_lumped(Deff, R, K, Q, eps_bed, V_bed, t_eval, N=100, C_s0=1.0):
    """Reduced (linear-axial-profile) bed extraction with constant flow Q. State
    is the representative grain profile (u = r C_s) + the lumped bed-pore
    concentration C_bed. Explicit solute accounting: each of n_grains =
    (1-eps) V_bed / V_grain grains loses its surface flux into the bed pore
    (Vpore = eps V_bed), which is swept out at rate Q C_bed (Eq 3.36); surface BC
    C_s(R) = C_bed/K. Returns t, yield_frac(t) = eluted/initial-inventory (x y0
    for absolute EY), strength(t) = eluted/eluted-volume, C_bed(t), and the
    closed mass balance (grains + pore + eluted = initial)."""
    rhs, dr = _sphere_rhs_factory(Deff, R, N)
    r = np.linspace(0.0, R, N + 1)
    Vsphere = 4.0 / 3.0 * np.pi * R ** 3
    n_grains = (1.0 - eps_bed) * V_bed / Vsphere
    Vpore = eps_bed * V_bed
    inv = (1.0 - eps_bed) * V_bed * C_s0                 # total initial solute

    def ode(t, y):
        u = y[:N - 1]; c_bed = y[N - 1]
        d2, full = rhs(u, c_bed / K)
        # 2nd-order one-sided surface gradient dC_s/dr|_R (C = u/r), for a
        # tightly-closed mass balance
        cN = c_bed / K
        cN1 = full[N - 1] / r[N - 1]
        cN2 = full[N - 2] / r[N - 2]
        dCdr_R = (3.0 * cN - 4.0 * cN1 + cN2) / (2.0 * dr)
        flux = -Deff * 4.0 * np.pi * R ** 2 * dCdr_R      # per grain, >0 leaving solid
        dcbed = (n_grains * flux - Q * c_bed) / Vpore
        return np.concatenate([d2, [dcbed]])
    y0 = np.concatenate([r[1:N] * C_s0, [0.0]])
    sol = solve_ivp(ode, [0.0, t_eval[-1]], y0, t_eval=t_eval, method="BDF",
                    rtol=1e-9, atol=1e-11)
    c_bed = sol.y[N - 1, :]
    t = sol.t
    elut = np.concatenate([[0.0], np.cumsum(0.5 * (c_bed[1:] + c_bed[:-1])
                                            * np.diff(t)) * Q])
    vol = Q * t
    yield_frac = elut / inv
    strength = np.divide(elut, vol, out=np.zeros_like(elut), where=vol > 0)
    # closed mass balance: grain content (4pi int u r dr) * n_grains + pore + eluted
    grain = np.array([_content(np.concatenate([[0.0], sol.y[:N - 1, k],
                     [R * c_bed[k] / K]]), r) for k in range(len(t))]) * 4.0 * np.pi
    balance = (grain * n_grains + c_bed * Vpore + elut) / inv
    return dict(t=t, yield_frac=yield_frac, strength=strength, c_bed=c_bed,
                mass_balance=balance)


# --- data-driven parameter helpers ------------------------------------------
def deff_of(grind, mw, T_degC=80.0):
    """Microstructural Deff [m^2/s] for a grind x MW class (Table 4.9, 80 C),
    Stokes-Einstein-corrected to T via the ratio of absolute temperatures (the
    thesis's temperature correction for the espresso conditions)."""
    rows = {r["grind"]: r for r in _d.roman_deff()}
    d80 = rows[grind][f"Deff_{mw}_x1e-11"] * 1e-11
    return d80 * (273.15 + T_degC) / (273.15 + 80.0)


def K_of_T(T_degC):
    """Partition coefficient K(T) from the thesis Arrhenius fit ln K = -657/T +
    1.4 (T in K), consistent with Table 4.10 (0.42/0.57/0.61 at 20/50/80 C)."""
    return float(np.exp(-657.0 / (273.15 + T_degC) + 1.4))

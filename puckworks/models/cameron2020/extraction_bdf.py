"""
espresso_model.py
=================
Python reimplementation of the multiscale espresso extraction model from:

    Cameron, Morisco, Hofstetter, Uman, Wilkinson, Kennedy, Fontenot,
    Lee, Hendon & Foster, "Systematically Improving Espresso: Insights from
    Mathematical Modeling and Experiment", Matter 2, 631-648 (2020).
    https://doi.org/10.1016/j.matt.2019.12.019

Model structure (homogenised, 1D-in-z, valid in the homogeneous-flow regime):

  Macroscale (liquid phase, Eq. 18-20 of the paper):
      (1 - phi_s) dc_l/dt = d/dz( D_eff dc_l/dz - q c_l ) + bet1*G1 + bet2*G2
      with zero total soluble flux at the inlet and zero diffusive flux at
      the outlet. Advection dominates (Pe >> 1), so D_eff is negligible; we
      solve the advective problem with a conservative first-order upwind
      finite-volume scheme.

  Microscale (two spherical particle families -- "fines" i=1 and
  "boulders" i=2 -- at every macroscopic station, Eq. 21-22):
      dc_si/dt = (1/r^2) d/dr( r^2 D_s dc_si/dr )
      D_s dc_si/dr|_{r=0}  = 0
      D_s dc_si/dr|_{r=ai} = -G_i
  discretised with a mass-conservative control-volume scheme that carries
  the surface concentration as an explicit unknown (in the spirit of
  Zeng et al. 2013, cited in the paper's SI).

  Interfacial dissolution rate (Eq. 16):
      G_i = k * c_si(surface) * (c_si(surface) - c_l) * (c_sat - c_l)

  Extraction yield (Eq. 24):
      EY = pi R0^2 q * integral_0^tshot c_l(z=L, t) dt / M_in

Parameters are taken from Tables S1-S5 of the Supplemental Information.
Note on pressure bookkeeping: the SI tables quote pump OVERPRESSURE
(P_tot = 5 bar corresponds to the "6 bar" static-pressure experiments in
the main text). Darcy flux scales linearly with overpressure (Darcy's law),
which reproduces Table S5 exactly.

Author: generated for Tim Brewer's Stage-1 espresso project, July 2026.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np
from scipy.integrate import solve_ivp
from scipy import sparse

# ----------------------------------------------------------------------------
# Parameters from the Supplemental Information
# ----------------------------------------------------------------------------

# --- Table S1: physical constants and default recipe -------------------------
R0 = 29.2e-3          # basket radius, m
MU = 3.15e-4          # viscosity of water at ~90 C, Pa s   (unused directly;
                      #   flow enters via measured Darcy flux, Table S3/S5)
RHO_OUT = 997.0       # beverage (~water) density, kg/m^3
RHO_GROUNDS = 330.0   # roasted-coffee bulk density, kg/m^3
C_SAT = 212.4         # saturation concentration, kg/m^3
C_S0 = 118.0          # initial soluble concentration in grounds, kg/m^3
PHI_S = 0.8272        # solid volume fraction of the packed bed

# --- Eq. 28: kinetic parameters fitted by the authors ------------------------
D_S = 6.25e-10        # intragrain diffusivity, m^2/s
K_RATE = 6.0e-7       # dissolution rate constant, m^7 kg^-2 s^-1

# --- Table S2: grind-dependent microstructure (measured at GS = 1.0..2.5) ----
# NOTE on an internal inconsistency in the paper's Table S2: the boulder BET
# values satisfy Supplemental Eq. 3 (bet_i = 3 phi_i / a_i) exactly, but the
# tabulated fines BET values imply a fines radius of 49.7 um rather than the
# stated a1 = 12 um (constant ratio 0.241 across all grind settings). Taking
# the tabulated bet1 together with a1 = 12 um under-represents the fines'
# soluble mass by ~4x and caps EY well below the model curve in Fig. 5.
# We therefore honor the *measured volume fractions* (which fix the soluble
# inventory and the max possible EY) and derive BET areas from them via
# Suppl. Eq. 3. Because fines equilibrate in << t_shot for any a1 in the
# 12-50 um range, predictions are insensitive to which radius is adopted.
GS_GRID = np.array([1.0, 1.5, 2.0, 2.5])
PHI_S1_GRID = np.array([0.1689, 0.1343, 0.1200, 0.0780])      # fines vol. frac.
PHI_S2_GRID = np.array([0.6583, 0.6929, 0.7072, 0.7492])      # boulders
A2_GRID = np.array([273.86, 335.41, 335.41, 410.79]) * 1e-6   # boulder radius, m
A1 = 12e-6            # fines radius, m (fixed, per SI)
BET1_GRID = 3.0 * PHI_S1_GRID / A1                            # 1/m (Suppl. Eq. 3)
BET2_GRID = 3.0 * PHI_S2_GRID / A2_GRID                       # 1/m (= Table S2)

# --- Table S3: measured shot times and Darcy fluxes at P_tot = 5 bar ---------
GS_Q_GRID = np.array([1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3])
TSHOT_GRID = np.array([37.6, 35.7, 33.9, 30.5, 28.5, 26.6, 24.0])       # s
Q5_GRID = np.array([3.98, 4.20, 4.42, 4.91, 5.26, 5.63, 6.24]) * 1e-4   # m/s

P_REF = 5.0           # bar overpressure at which Q5_GRID was measured


# ----------------------------------------------------------------------------
# Helper: grind-setting interpolation
# ----------------------------------------------------------------------------

def grind_microstructure(gs: float):
    """Linearly interpolate Table S2 quantities to an arbitrary grind setting."""
    phi1 = np.interp(gs, GS_GRID, PHI_S1_GRID)
    phi2 = np.interp(gs, GS_GRID, PHI_S2_GRID)
    a2 = np.interp(gs, GS_GRID, A2_GRID)
    bet1 = np.interp(gs, GS_GRID, BET1_GRID)
    bet2 = np.interp(gs, GS_GRID, BET2_GRID)
    return phi1, phi2, a2, bet1, bet2


def darcy_flux(gs: float, p_bar: float = P_REF, L: float | None = None,
               L_ref: float | None = None) -> float:
    """Darcy flux q(GS, P). Linear in overpressure (Darcy), matching Table S5.

    If a bed depth L different from the 20 g reference L_ref is supplied,
    q is rescaled by L_ref/L (q = kappa_eff * P_tot / (mu L), Suppl. Eq. 5),
    which is how the dose sweep of Fig. 3A is generated.
    """
    q = np.interp(gs, GS_Q_GRID, Q5_GRID) * (p_bar / P_REF)
    if L is not None and L_ref is not None:
        q *= L_ref / L
    return float(q)


def bed_depth(m_in: float) -> float:
    """Bed depth from Eq. 25:  pi R0^2 L = (M_in / rho_grounds) * phi_s.

    (Reproduces Table S4: 20 g -> 18.7 mm.)
    """
    return (m_in / RHO_GROUNDS) * PHI_S / (np.pi * R0**2)


# ----------------------------------------------------------------------------
# Spherical control-volume machinery
# ----------------------------------------------------------------------------

@dataclass
class SphereGrid:
    """Mass-conservative control-volume grid for a sphere of radius a.

    Nodes sit at r_k = k*dr (k = 0..M-1), node M-1 on the surface, so the
    surface concentration (which sets the dissolution rate) is an explicit
    unknown. Cell faces at midpoints between nodes; cell k owns the shell
    between its faces. Total soluble mass = sum(V_k * c_k) is conserved up
    to the surface flux term exactly.
    """
    a: float
    M: int
    r: np.ndarray = field(init=False)
    dr: float = field(init=False)
    V: np.ndarray = field(init=False)       # shell volumes, len M
    A_face: np.ndarray = field(init=False)  # face areas, len M-1 (between k,k+1)

    def __post_init__(self):
        self.r = np.linspace(0.0, self.a, self.M)
        self.dr = self.r[1] - self.r[0]
        faces = 0.5 * (self.r[:-1] + self.r[1:])           # interior faces
        edges = np.concatenate(([0.0], faces, [self.a]))   # cell boundaries
        self.V = 4.0 / 3.0 * np.pi * (edges[1:] ** 3 - edges[:-1] ** 3)
        self.A_face = 4.0 * np.pi * faces**2


# ----------------------------------------------------------------------------
# The simulator
# ----------------------------------------------------------------------------

@dataclass
class ShotResult:
    gs: float
    p_bar: float
    m_in: float
    m_out: float
    t_shot: float
    EY: float                 # extraction yield, mass %
    EY_solid: float           # cross-check: EY from solid depletion minus holdup, %
    tds: float                # beverage strength, mass % (M_cup / M_out)
    t: np.ndarray             # time samples
    m_cup: np.ndarray         # cumulative dissolved mass in cup, kg
    cl_out: np.ndarray        # outlet liquid concentration, kg/m^3
    z: np.ndarray             # macroscale grid
    cl_final: np.ndarray      # liquid concentration profile at t_shot
    cs1_final: np.ndarray     # (N, M) fines concentration field at t_shot
    cs2_final: np.ndarray     # (N, M) boulder concentration field at t_shot
    r1: np.ndarray
    r2: np.ndarray


def simulate_shot(gs: float,
                  p_bar: float = P_REF,
                  m_in: float = 0.020,
                  m_out: float = 0.040,
                  N: int = 40,
                  M: int = 24,
                  q: float | None = None,
                  t_shot: float | None = None,
                  n_save: int = 120,
                  rtol: float = 1e-6,
                  atol: float = 1e-8,
                  c_s0: float | None = None) -> ShotResult:
    """Simulate one espresso shot and return the extraction yield.

    Parameters
    ----------
    gs      : grinder setting (EK43 dial units, 1.0-2.5 valid range)
    p_bar   : pump overpressure in bar (5 bar <-> the paper's '6 bar' recipe)
    m_in    : dry dose, kg
    m_out   : beverage mass, kg
    N, M    : number of macroscale cells / radial nodes per particle family
    q       : override the Darcy flux (m/s); default from Table S3/S5 scaling
    t_shot  : override the shot time (s); default M_out/(pi R0^2 rho_out q)
    """
    L_ref = bed_depth(0.020)
    L = bed_depth(m_in)

    if q is None:
        q = darcy_flux(gs, p_bar, L=L, L_ref=L_ref)
    if t_shot is None:
        t_shot = m_out / (np.pi * R0**2 * RHO_OUT * q)   # Eq. 26 rearranged

    phi1, phi2, a2, bet1, bet2 = grind_microstructure(gs)
    eps = 1.0 - PHI_S                                    # bed porosity

    g1, g2 = SphereGrid(A1, M), SphereGrid(a2, M)
    hz = L / N

    # State vector: [ cl (N) | cs1 (N*M) | cs2 (N*M) | M_cup (1) ]
    n_cl = N
    n_cs = N * M
    i_cs1 = n_cl
    i_cs2 = n_cl + n_cs
    i_mcup = n_cl + 2 * n_cs
    n_tot = i_mcup + 1

    area = np.pi * R0**2

    def rhs(t, u):
        cl = u[:n_cl]
        cs1 = u[i_cs1:i_cs2].reshape(N, M)
        cs2 = u[i_cs2:i_mcup].reshape(N, M)

        cs1_surf = cs1[:, -1]
        cs2_surf = cs2[:, -1]

        # Dissolution rates, Eq. 16 (per unit grain surface area)
        G1 = K_RATE * cs1_surf * (cs1_surf - cl) * (C_SAT - cl)
        G2 = K_RATE * cs2_surf * (cs2_surf - cl) * (C_SAT - cl)

        # ---- liquid phase: conservative upwind advection + sources ----
        dcl = np.empty(N)
        influx = np.concatenate(([0.0], cl[:-1]))        # upwind face values
        dcl = (q * (influx - cl) / hz + bet1 * G1 + bet2 * G2) / eps

        # ---- solid phases: spherical control volumes ----
        def sphere_rhs(cs, grid, G):
            F = grid.A_face * D_S * (cs[:, 1:] - cs[:, :-1]) / grid.dr  # (N, M-1)
            dcs = np.empty_like(cs)
            dcs[:, 0] = F[:, 0] / grid.V[0]
            dcs[:, 1:-1] = (F[:, 1:] - F[:, :-1]) / grid.V[1:-1]
            dcs[:, -1] = (-4.0 * np.pi * grid.a**2 * G - F[:, -1]) / grid.V[-1]
            return dcs

        dcs1 = sphere_rhs(cs1, g1, G1)
        dcs2 = sphere_rhs(cs2, g2, G2)

        dmcup = area * q * cl[-1]                        # Eq. 23

        return np.concatenate((dcl, dcs1.ravel(), dcs2.ravel(), [dmcup]))

    # ---- Jacobian sparsity pattern (keeps BDF cheap) ----
    S = sparse.lil_matrix((n_tot, n_tot), dtype=np.int8)
    for j in range(N):
        S[j, j] = 1
        if j > 0:
            S[j, j - 1] = 1
        S[j, i_cs1 + j * M + (M - 1)] = 1                # cl <- cs1 surface
        S[j, i_cs2 + j * M + (M - 1)] = 1                # cl <- cs2 surface
        for fam_base in (i_cs1, i_cs2):
            base = fam_base + j * M
            for k in range(M):
                S[base + k, base + k] = 1
                if k > 0:
                    S[base + k, base + k - 1] = 1
                if k < M - 1:
                    S[base + k, base + k + 1] = 1
            S[base + M - 1, j] = 1                       # surface node <- cl
    S[i_mcup, n_cl - 1] = 1

    # initial soluble concentration in the grounds; defaults to the module constant C_S0 (118 kg/m^3).
    # Passing c_s0 explicitly lets a caller (e.g. brewer2026.streamtube) use its own calibrated basis
    # WITHOUT mutating this module's global — imports must never rewrite another model's constant.
    c_s0 = C_S0 if c_s0 is None else c_s0
    u0 = np.concatenate((np.zeros(N),                    # cl(z, 0) = 0
                         np.full(n_cs, c_s0),            # cs(z, r, 0) = cs0
                         np.full(n_cs, c_s0),
                         [0.0]))

    t_eval = np.linspace(0.0, t_shot, n_save)
    sol = solve_ivp(rhs, (0.0, t_shot), u0, method="BDF",
                    jac_sparsity=S.tocsr(), t_eval=t_eval,
                    rtol=rtol, atol=atol)
    if not sol.success:
        raise RuntimeError(f"Integration failed at GS={gs}: {sol.message}")

    cl_hist = sol.y[:n_cl, :]
    m_cup = sol.y[i_mcup, :]
    EY = 100.0 * m_cup[-1] / m_in

    # ---- conservation cross-check: EY from solid depletion minus bed holdup ----
    cs1_f = sol.y[i_cs1:i_cs2, -1].reshape(N, M)
    cs2_f = sol.y[i_cs2:i_mcup, -1].reshape(N, M)
    bed_vol = area * L

    def mean_conc(cs, grid):
        return (cs * grid.V).sum(axis=1) / grid.V.sum()

    n1 = bet1 / (4 * np.pi * A1**2)      # number density of fines, 1/m^3 bed
    n2 = bet2 / (4 * np.pi * a2**2)
    solid_mass = lambda cs1_, cs2_: bed_vol * hz / L * 0  # placeholder
    m_solid_0 = bed_vol * (phi1 + phi2) * c_s0
    m_solid_f = (bed_vol / N) * (
        n1 * (4 / 3 * np.pi * A1**3) * 0 +  # kept explicit below
        0)
    # explicit: per-cell solid soluble mass
    m1_f = (bed_vol / N) * n1 * (mean_conc(cs1_f, g1) * (4 / 3 * np.pi * A1**3)).sum()
    m2_f = (bed_vol / N) * n2 * (mean_conc(cs2_f, g2) * (4 / 3 * np.pi * a2**3)).sum()
    m_liq_hold = (bed_vol / N) * eps * cl_hist[:, -1].sum()
    EY_solid = 100.0 * (m_solid_0 - (m1_f + m2_f) - m_liq_hold) / m_in

    return ShotResult(
        gs=gs, p_bar=p_bar, m_in=m_in, m_out=m_out, t_shot=t_shot,
        EY=EY, EY_solid=EY_solid, tds=100.0 * m_cup[-1] / m_out,
        t=sol.t, m_cup=m_cup, cl_out=cl_hist[-1, :],
        z=np.linspace(hz / 2, L - hz / 2, N), cl_final=cl_hist[:, -1],
        cs1_final=cs1_f, cs2_final=cs2_f, r1=g1.r, r2=g2.r,
    )


# ----------------------------------------------------------------------------
# Convenience sweeps
# ----------------------------------------------------------------------------

def sweep_grind(gs_values, **kwargs):
    return [simulate_shot(gs, **kwargs) for gs in gs_values]


if __name__ == "__main__":
    # quick smoke test: the paper's reference recipe at GS = 2.1
    res = simulate_shot(2.1)
    print("GS=2.1, 20 g in / 40 g out, 5 bar overpressure:")
    print(f"  shot time        = {res.t_shot:6.1f} s   (Table S3: 26.6 s)")
    print(f"  extraction yield = {res.EY:6.2f} %  (Fig. 5 model, std-flow regime)")
    print(f"  EY (mass check)  = {res.EY_solid:6.2f} %")
    print(f"  beverage TDS     = {res.tds:6.2f} %")

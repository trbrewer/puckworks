"""desorption.py — Liang et al. 2021 immersion equilibrium desorption.

Card: docs/cards/liang2021.md (ROADMAP item 1.3). CALIBRATION provider for the
extraction/observables stages: a pseudo-equilibrium desorption model for FULL
IMMERSION brewing (NOT flow extraction). All species lumped into one equilibrium
constant K; at steady state a fixed fraction K*E_max of the grounds dissolves,
independent of brew ratio. Closed-form algebra, endpoints only (no kinetics).

    TDS  = K*E_max / (R_brew + K*E_max)                     (Eq. 11)
    E    = K*E_max                                          (Eq. 13; flat in R_brew)
    E_oven = K*E_max (1 - R_ret/(R_brew + K*E_max)) + R_vol (Eq. 22 oven kernel)

Two registry uses (card): (1) an equilibrium-ceiling consistency check on
cameron2020 — K<1 means not all soluble inventory (E_max) dissolves even at
infinite time, so the equilibrium ceiling sits BELOW cameron's per-bed
soluble-inventory ceiling (§5.5); (2) the oven-drying/retention kernel for the
observables backlog.

Scope (card): immersion pseudo-equilibrium only; single lumped species; valid
R_brew >= 3 (fails at 2, "moist sludge"); 80-99 C; E_max=0.30 ASSUMED not
measured, so all K values inherit it. NOT a model of espresso/flow extraction.
"""
import numpy as np

E_MAX = 0.30              # nominal, assumed (card); all K conditional on this
K_EMAX_1L = 0.215         # fitted lumped ceiling, 1-L brews (card)
R_RET = 2.48              # g/g liquid retained in spent grounds (card)
R_VOL = 0.0234            # g/g solids volatilized during oven baking (card)


def tds_eq11(R_brew, K_Emax=K_EMAX_1L):
    """Equilibrium TDS fraction vs brew ratio (Eq. 11)."""
    return K_Emax / (np.asarray(R_brew, float) + K_Emax)


def fit_K_Emax(R_brew, TDS):
    """Refit the lumped ceiling K*E_max from (R_brew, TDS) via Eq. 11."""
    from scipy.optimize import curve_fit
    (ke,), _ = curve_fit(tds_eq11, np.asarray(R_brew, float),
                         np.asarray(TDS, float), p0=[0.2])
    return float(ke)


def E_equilibrium(K_Emax=K_EMAX_1L):
    """Equilibrium extraction yield E = K*E_max (Eq. 13), flat in R_brew."""
    return K_Emax


def E_oven(R_brew, K_Emax=K_EMAX_1L, R_ret=R_RET, R_vol=R_VOL):
    """Oven-drying measurement of E (Eq. 22): under-reads the true equilibrium E
    by the retained-liquid term, partly offset by volatilized solids R_vol."""
    R_brew = np.asarray(R_brew, float)
    return K_Emax * (1.0 - R_ret / (R_brew + K_Emax)) + R_vol


def cameron_inventory_ceiling(gs=1.9, dose_kg=0.020):
    """Cameron's per-bed soluble-inventory ceiling (analytic, no PDE solve):
    m_solid_0 / dose. A DIFFERENT physical quantity from the equilibrium ceiling
    K*E_max (§5.5) — this is total dissolvable inventory, not the partition
    endpoint."""
    from puckworks.models.cameron2020 import extraction_bdf as em
    phi1, phi2, *_ = em.grind_microstructure(gs)
    L = em.bed_depth(dose_kg)
    area = np.pi * em.R0 ** 2
    return area * L * (phi1 + phi2) * em.C_S0 / dose_kg

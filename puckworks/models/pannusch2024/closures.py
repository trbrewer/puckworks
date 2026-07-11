"""closures.py — Pannusch et al. 2024 constitutive closures (scoped slice of 1.8a).

Card: docs/cards/pannusch2024.md (ROADMAP item 1.8a). CALIBRATION provider: the
temperature/flow constitutive laws of the two-grain multi-solute extraction
model, ported FAITHFULLY from the authors' released MATLAB
(Mendeley 10.17632/y2tz67f6ry.1: diffusionCoeff.m, SherwoodFunction.m,
vantHoff_solubility.m, physical_parameters.m).

This is the DE-RISKING slice: the reusable closures that the full 4-solute PDE
forward solver (funvalue_fd_simulation_Fit3.m) consumes. The PDE solve + fit-MAPE
reproduction (RC-4a) is deferred — see docs/cards note; this module lands the
verifiable constitutive layer.

  water_viscosity(T)  VDI heat-atlas correlation [Pa s]
  water_density(T)    Rackett (VDI) [kg/m^3]
  diffusion_coeff(T, solute)  Wilke-Chang (1955) [m^2/s]
  sherwood_h(T, q, A, B, solute)  Sh = A Re^B Sc^(1/3); h = Sh D / d32 [m/s]
  vant_hoff_K(T, Kref, gamma, Tref)  K = Kref exp(gamma (1/Tref - 1/T))

Validity (card): T 80-98 C, Q 1-3 mL/s; effects above 80 C are small (K weakly
T-dependent). Fitted parameters "lack physical meaning and generality" (authors);
Wilke-Chang over-predicts absolute D vs measured, but is the model's own closure.
"""
import numpy as np

TREF_K = 360.15            # van't Hoff reference temperature [K] (paramPh.Tref)
D32 = 84e-6               # Sauter mean diameter of the bed [m] (physical_parameters)

# Wilke-Chang molecular weight [g/mol] and Le Bas molar volume [cm^3/mol] per
# solute (diffusionCoeff.m); TDS is modelled as a caffeine-like pseudo-molecule.
SOLUTES = {
    "tds":          dict(M=194.19, MV=195.3),
    "caffeine":     dict(M=194.19, MV=195.3),
    "trigonelline": dict(M=137.14, MV=154.1),
    "5CQA":         dict(M=354.31, MV=356.4),
}


def water_viscosity(T_K):
    """Dynamic viscosity of water [Pa s] (VDI heat-atlas fit). ~3.13e-4 at 90 C."""
    T = np.asarray(T_K, float)
    return np.exp(-22.968 + 3275.89 / T + 0.017637 * T
                  + 0.000000693 * T ** 2 - 0.000000012933 * T ** 3)


def water_density(T_K):
    """Density of water [kg/m^3] (parameterised Rackett equation, VDI)."""
    T = np.asarray(T_K, float)
    return 1.5053957 / (0.03642 ** (1 + (1 - T / 617.774) ** 0.05871))


def diffusion_coeff(T_K, solute):
    """Wilke-Chang diffusion coefficient [m^2/s] (association factor 2.6)."""
    s = SOLUTES[solute]
    vis_cP = water_viscosity(T_K) * 1000.0                 # Pa s -> cP
    D_cm2_s = 7.4e-8 * (2.6 * s["M"]) ** 0.5 * np.asarray(T_K, float) \
        / (vis_cP * s["MV"] ** 0.6)
    return D_cm2_s / 1e4                                    # cm^2/s -> m^2/s


def sherwood_h(T_K, q, A, B, solute, d32=D32):
    """Lumped mass-transfer coefficient h_sl [m/s] from the Sherwood correlation
    Sh = A Re^B Sc^(1/3), with h = Sh D / d32 (SherwoodFunction.m). q = superficial
    (Darcy) velocity [m/s]."""
    D = diffusion_coeff(T_K, solute)
    kin_vis = water_viscosity(T_K) / water_density(T_K)    # [m^2/s]
    Re = d32 * np.asarray(q, float) / kin_vis
    Sc = kin_vis / D
    Sh = A * Re ** B * Sc ** (1.0 / 3.0)
    return Sh / d32 * D


def vant_hoff_K(T_K, Kref, gamma, Tref=TREF_K):
    """Solid-liquid distribution constant K(T) (van't Hoff): equals Kref at Tref."""
    return Kref * np.exp(gamma * (1.0 / Tref - 1.0 / np.asarray(T_K, float)))

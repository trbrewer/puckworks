"""puckworks.contracts — v0 typed state passed between stage implementations.

Deliberately minimal: fields are those our registered components actually
exchange. Extend by adding fields (never repurposing them); bump SCHEMA_VERSION
on breaking change.
"""
from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np

SCHEMA_VERSION = "0.5"   # 0.5: A8 per-depth-cell porosity / fines fields (additive)
# history: 0.4 A1 pressure-node fields; 0.3 GrindState.fines_radius_m; 0.2 A7

# Plausible SI permeability window [m^2]. The Forchheimer k_I closures
# (k_I = exp(g2 k^tau)) fail SILENTLY off-SI (ledger A7), so k is asserted, not
# trusted (CLAUDE.md rule 7). Window spans untamped coffee (~1e-10) down to
# well below tamped/screen-limited beds (~1e-15) with margin.
K_SI_MIN, K_SI_MAX = 1e-18, 1e-6


def assert_si_permeability(k_m2, name="k"):
    """Raise unless k is inside the SI [m^2] window (ledger A7 unit guard)."""
    kk = np.asarray(k_m2, float)
    if not np.all(np.isfinite(kk) & (kk > K_SI_MIN) & (kk < K_SI_MAX)):
        raise ValueError(
            f"{name}={k_m2} outside SI window [{K_SI_MIN:g}, {K_SI_MAX:g}] m^2; "
            "Forchheimer k_I closures require strict SI permeability (A7).")

@dataclass
class GrindState:
    setting: float                    # grinder dial (Cameron EK43 convention)
    fines_fraction: Optional[float] = None      # phi_1
    boulder_radius_m: Optional[float] = None    # a_2
    fines_radius_m: Optional[float] = None       # a_1 (grudeva2025 needs a*_f; G5-pre)
    mean_radius_m: Optional[float] = None       # <R> (Wadsworth convention)

@dataclass
class BedState:
    dose_kg: float
    depth_m: float
    area_m2: float
    porosity: float                   # water-accessible or intergrain: document which
    k_m2: Optional[float] = None      # permeability (SI)
    k_I_m: Optional[float] = None     # inertial (Forchheimer) permeability [m] (A7)
    kappa: float = 1.0                # multiplier on a reference flux law
    sigma: float = 0.0                # streamtube lognormal heterogeneity spread
    # A8: spatial (per-depth-cell) state for dynamic bed_dynamics mechanisms
    # (fasano I/II fines migration, mo2023_2 swelling, waszkiewicz-coupled). The
    # scalar `kappa`/`porosity` above cannot host these; these are per-cell arrays.
    porosity_profile: Optional[np.ndarray] = None    # phi(z) per depth cell
    fines_mobile: Optional[np.ndarray] = None        # mobile fines inventory(z)
    fines_bound: Optional[np.ndarray] = None         # bound/deposited fines(z)

@dataclass
class FlowLaw:
    """Forchheimer flow-closure state (ledger A7). A Darcy law is the k_I=None
    case. k_m2 [m^2] Darcy permeability; k_I_m [m] inertial permeability;
    closure names the k_I(k) constitutive law used ('darcy' | 'zhou' | 'exp')."""
    k_m2: float
    k_I_m: Optional[float] = None
    closure: str = "darcy"


@dataclass
class PumpHeadspace:
    """Machine-mode pump + trapped-air headspace parameters (ledger A1;
    foster2025_2 Eqs. 2-7). Enables generating the pressure-node set from a
    machine model instead of consuming a recorded trace."""
    p_m: float                        # pump shut-off pressure [Pa]
    Q_m: float                        # pump max flow [m^3/s]
    R_f: float                        # pipe resistance [Pa s / m^3]
    H0: float                         # initial headspace height [m]
    beta: float = 1.0                 # trapped-air heating ratio T1/T0
    p_c: float = 0.0                  # capillary suction at the front [Pa]


@dataclass
class MachineState:
    P_of_t: Optional[Callable[[float], float]] = None   # bar, gauge overpressure
    profile_t: Optional[np.ndarray] = None
    profile_p: Optional[np.ndarray] = None
    # A1 pressure-node set (RC-3 node table): each is a callable of t [s] -> Pa,
    # or a scalar. Do NOT apply two pressure-drop corrections to one segment.
    p_p: Optional[Callable[[float], float]] = None      # pump outlet
    p_h: Optional[Callable[[float], float]] = None      # headspace / bed top
    P_basket: Optional[Callable[[float], float]] = None  # basket gauge / puck
    dP_bed: Optional[Callable[[float], float]] = None   # drop across the wet bed
    pump: Optional[PumpHeadspace] = None                # machine-mode source (A1)

@dataclass
class ShotResultState:
    EY_pct: float
    tds_pct: float
    t_shot_s: float
    beverage_g: float
    traces: dict = field(default_factory=dict)   # t, flow, weight, pressure arrays

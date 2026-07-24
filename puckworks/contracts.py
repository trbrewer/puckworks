"""puckworks.contracts — v0 typed state passed between stage implementations.

Deliberately minimal: fields are those our registered components actually
exchange. Extend by adding fields (never repurposing them); bump SCHEMA_VERSION
on breaking change.
"""
import math
from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np

SCHEMA_VERSION = "0.6"   # 0.6: A4 SoluteInventory (per-species initial chemistry, additive)
# history: 0.5 A8 per-depth-cell porosity/fines; 0.4 A1 pressure-node fields;
#          0.3 GrindState.fines_radius_m; 0.2 A7

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


# PW-CORE-001 — boundary validators for the core physics contracts. Conservative on purpose:
# finiteness + positivity + fraction bounds only, so a construction that carried a latent NaN /
# negative dimension / out-of-[0,1] porosity now fails loudly instead of silently propagating.
def _finite(name, v):
    if isinstance(v, bool):
        raise ValueError(f"{name} must be a number, not a bool")
    try:
        ok = bool(np.isfinite(v))
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a finite number, got {v!r}")
    if not ok:
        raise ValueError(f"{name} must be finite (no NaN/inf), got {v!r}")


def _finite_pos(name, v):
    _finite(name, v)
    if v <= 0:
        raise ValueError(f"{name} must be positive, got {v!r}")


def _fraction(name, v):
    _finite(name, v)
    if not (0.0 <= v <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {v!r}")

@dataclass
class GrindState:
    setting: float                    # grinder dial (Cameron EK43 convention)
    fines_fraction: Optional[float] = None      # phi_1
    boulder_radius_m: Optional[float] = None    # a_2
    fines_radius_m: Optional[float] = None       # a_1 (grudeva2025 needs a*_f; G5-pre)
    mean_radius_m: Optional[float] = None       # <R> (Wadsworth convention)

    def __post_init__(self):
        _finite("GrindState.setting", self.setting)
        if self.fines_fraction is not None:
            _fraction("GrindState.fines_fraction", self.fines_fraction)
        for n in ("boulder_radius_m", "fines_radius_m", "mean_radius_m"):
            v = getattr(self, n)
            if v is not None:
                _finite_pos(f"GrindState.{n}", v)

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

    def __post_init__(self):
        _finite_pos("BedState.dose_kg", self.dose_kg)
        _finite_pos("BedState.depth_m", self.depth_m)
        _finite_pos("BedState.area_m2", self.area_m2)
        _fraction("BedState.porosity", self.porosity)
        _finite("BedState.kappa", self.kappa)
        _finite("BedState.sigma", self.sigma)
        if self.k_m2 is not None:
            _finite_pos("BedState.k_m2", self.k_m2)
        if self.k_I_m is not None:
            _finite_pos("BedState.k_I_m", self.k_I_m)

@dataclass
class FlowLaw:
    """Forchheimer flow-closure state (ledger A7). A Darcy law is the k_I=None
    case. k_m2 [m^2] Darcy permeability; k_I_m [m] inertial permeability;
    closure names the k_I(k) constitutive law used ('darcy' | 'zhou' | 'exp')."""
    k_m2: float
    k_I_m: Optional[float] = None
    closure: str = "darcy"

    def __post_init__(self):
        _finite_pos("FlowLaw.k_m2", self.k_m2)
        if self.k_I_m is not None:
            _finite_pos("FlowLaw.k_I_m", self.k_I_m)
        if not isinstance(self.closure, str) or not self.closure:
            raise ValueError("FlowLaw.closure must be a non-empty string")


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

    def __post_init__(self):
        for n in ("p_m", "Q_m", "R_f", "H0"):
            _finite_pos(f"PumpHeadspace.{n}", getattr(self, n))
        _finite("PumpHeadspace.beta", self.beta)
        _finite("PumpHeadspace.p_c", self.p_c)


@dataclass
class MachineState:
    # UNITS (see docs/UNITS_POLICY.md): P_of_t is the machine-facing recorded profile in
    # BAR-GAUGE overpressure; the A1 pressure-node callables below are SI (Pa). Convert with
    # puckworks.validate.bar_gauge_to_pa at the boundary — never mix bar and Pa in one expression.
    P_of_t: Optional[Callable[[float], float]] = None   # bar-gauge overpressure (machine boundary)
    profile_t: Optional[np.ndarray] = None              # s
    profile_p: Optional[np.ndarray] = None              # bar-gauge (aligned with profile_t)
    # A1 pressure-node set (RC-3 node table): each is a callable of t [s] -> Pa (SI),
    # or a scalar. Do NOT apply two pressure-drop corrections to one segment.
    p_p: Optional[Callable[[float], float]] = None      # pump outlet
    p_h: Optional[Callable[[float], float]] = None      # headspace / bed top
    P_basket: Optional[Callable[[float], float]] = None  # basket gauge / puck
    dP_bed: Optional[Callable[[float], float]] = None   # drop across the wet bed
    pump: Optional[PumpHeadspace] = None                # machine-mode source (A1)

@dataclass
class SoluteInventory:
    """A4 — per-species INITIAL solute chemistry (ledger A4). The contract carrier
    that links a measured roasted-chemistry inventory (bruno2026) to per-species
    extraction kinetics (pannusch2024 / romancorrochano2017): Bruno provides
    INVENTORY, not kinetics; before this, no contract carried species.

    LOAD-BEARING CAVEAT: `species[name]["amount"]` is a per-species CONTENT on
    `basis` (e.g. total roasted-bean content, mg/kg) -- it is NOT an extractable
    solid inventory c_s0. The total->extractable mapping needs a per-species
    EXTRACTABILITY factor that Bruno does not measure; `extractable_fraction`
    holds it (default None = UNKNOWN). A consumer MUST NOT substitute a
    total-content amount for c_s0 without an explicit extractability assumption
    (that would be an unvalidated leap). Used as a PRIOR / cross-check, never as
    a fitted inventory, and never `Bruno-ODE -> extraction` (bruno card)."""
    species: dict                         # canonical name -> {amount, sd, unit, basis}
    origin: Optional[str] = None          # e.g. "Nicaragua" / species "Robusta"
    source: Optional[str] = None          # provenance (DOI / card)
    strength: str = "reference"           # §0 validation strength of the prior
    extractable_fraction: Optional[dict] = None   # canonical name -> f_extractable (None = unknown)

    def __post_init__(self):
        if not isinstance(self.species, dict):
            raise ValueError("SoluteInventory.species must be a mapping")
        for name, s in self.species.items():
            if not isinstance(name, str) or not name:
                raise ValueError("SoluteInventory species name must be a non-empty string, got %r" % (name,))
            if not isinstance(s, dict) or "amount" not in s:
                raise ValueError("SoluteInventory species %r must be a mapping carrying an 'amount'" % (name,))
            amt = s["amount"]
            if isinstance(amt, bool) or not isinstance(amt, (int, float)) or not math.isfinite(float(amt)):
                raise ValueError("SoluteInventory species %r amount must be a finite number, got %r" % (name, amt))
            if not s.get("unit") or not s.get("basis"):
                raise ValueError("SoluteInventory species %r must declare a unit and a basis" % (name,))
        if self.extractable_fraction is not None:
            for k, v in self.extractable_fraction.items():
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(float(v)) \
                        or not (0.0 <= float(v) <= 1.0):
                    raise ValueError("extractable_fraction[%r] must be a finite fraction in [0,1], got %r" % (k, v))

    def amount(self, name):
        """Content [on its unit/basis] for a canonical species, or None if absent."""
        s = self.species.get(name)
        return None if s is None else s.get("amount")


@dataclass
class ShotResultState:
    EY_pct: float
    tds_pct: float
    t_shot_s: float
    beverage_g: float
    traces: dict = field(default_factory=dict)   # t, flow, weight, pressure arrays

    def __post_init__(self):
        _finite("ShotResultState.EY_pct", self.EY_pct)
        _finite("ShotResultState.tds_pct", self.tds_pct)
        _finite_pos("ShotResultState.t_shot_s", self.t_shot_s)
        _finite_pos("ShotResultState.beverage_g", self.beverage_g)

"""puckworks.contracts — v0 typed state passed between stage implementations.

Deliberately minimal: fields are those our registered components actually
exchange. Extend by adding fields (never repurposing them); bump SCHEMA_VERSION
on breaking change.
"""
from dataclasses import dataclass, field
from typing import Callable, Optional
import numpy as np

SCHEMA_VERSION = "0.1"

@dataclass
class GrindState:
    setting: float                    # grinder dial (Cameron EK43 convention)
    fines_fraction: Optional[float] = None      # phi_1
    boulder_radius_m: Optional[float] = None    # a_2
    mean_radius_m: Optional[float] = None       # <R> (Wadsworth convention)

@dataclass
class BedState:
    dose_kg: float
    depth_m: float
    area_m2: float
    porosity: float                   # water-accessible or intergrain: document which
    k_m2: Optional[float] = None      # permeability (SI)
    kappa: float = 1.0                # multiplier on a reference flux law
    sigma: float = 0.0                # streamtube lognormal heterogeneity spread

@dataclass
class MachineState:
    P_of_t: Optional[Callable[[float], float]] = None   # bar, gauge overpressure
    profile_t: Optional[np.ndarray] = None
    profile_p: Optional[np.ndarray] = None

@dataclass
class ShotResultState:
    EY_pct: float
    tds_pct: float
    t_shot_s: float
    beverage_g: float
    traces: dict = field(default_factory=dict)   # t, flow, weight, pressure arrays

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum, IntEnum
import math


class SupportStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED_RELATIONSHIP = "UNSUPPORTED_RELATIONSHIP"
    UNSUPPORTED_FOR_CASE = "UNSUPPORTED_FOR_CASE"
    OUTSIDE_VALID_RANGE = "OUTSIDE_VALID_RANGE"
    MISSING_REQUIRED_INPUT = "MISSING_REQUIRED_INPUT"
    NUMERICAL_FAILURE = "NUMERICAL_FAILURE"
    NOT_EVALUATED = "NOT_EVALUATED"


class ComparabilityLevel(IntEnum):
    DIRECTLY_COMPARABLE = 1
    COMPARABLE_THROUGH_DECLARED_ADAPTER = 2
    SAME_INTERVENTION_DIFFERENT_OBSERVABLE = 3
    SAME_LABEL_DIFFERENT_PHYSICAL_OR_REFERENCE_BASIS = 4
    NOT_COMPARABLE = 5


@dataclass(frozen=True)
class ResultCell:
    component_id: str
    case_id: str
    observable: str
    support_status: str
    unit: str
    value: float | None = None
    reason: str | None = None
    pressure_node: str = "NOT_APPLICABLE"
    pressure_reference: str = "NOT_APPLICABLE"
    reference_basis: str = "NOT_PROVIDED"
    evidence_strength: str = "NOT_PROVIDED"
    source_kind: str = "SOURCE_NATIVE"

    def __post_init__(self):
        if self.support_status not in {s.value for s in SupportStatus}:
            raise ValueError("unknown support status")
        if self.support_status == SupportStatus.SUPPORTED.value:
            if self.value is None or not math.isfinite(float(self.value)):
                raise ValueError("SUPPORTED requires a finite numeric value")
        elif self.value is not None:
            raise ValueError("unsupported result cannot carry a numeric value")

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class QuantityRow:
    component_id: str
    stage: str
    quantity_name: str
    direction: str
    unit: str
    reference_basis: str
    physical_definition: str
    role: str
    provenance: str
    valid_range: object
    evidence_strength: str
    independently_variable: str
    relationship_kind: str
    comparable_observable_group: str
    support_status: str
    control_mode: str
    pressure_node: str = "NOT_APPLICABLE"
    pressure_reference: str = "NOT_APPLICABLE"
    flow_basis: str = "NOT_APPLICABLE"
    mass_basis: str = "NOT_APPLICABLE"
    temperature_basis: str = "NOT_PROVIDED"
    spatial_basis: str = "LUMPED"
    initialization: str = "SOURCE_DEFAULT"
    history_dependence: str = "NONE"
    adapter_id: str = "NONE"
    adapter_version: str = "NONE"
    card_identity: str = "NOT_PROVIDED"
    registry_identity: str = "NOT_PROVIDED"
    notes: str = ""

    def __post_init__(self):
        required = asdict(self)
        if any(v is None for v in required.values()):
            raise ValueError("inventory fields cannot be omitted or null")
        if self.valid_range == "":
            raise ValueError("unknown valid range must be NOT_PROVIDED")

    def to_dict(self):
        return asdict(self)


def numeric_residual(left: ResultCell, right: ResultCell, level: int) -> float:
    if level not in (1, 2):
        raise ValueError("numeric residuals require comparability level 1 or 2")
    if left.support_status != "SUPPORTED" or right.support_status != "SUPPORTED":
        raise ValueError("numeric residuals require supported cells")
    return float(left.value) - float(right.value)


def flow_conversion(*, darcy_velocity_m_s, area_m2=None, density_kg_m3=None):
    if area_m2 is None or density_kg_m3 is None:
        raise ValueError("flow conversion requires explicit area and density")
    return {"volumetric_flow_m3_s": darcy_velocity_m_s * area_m2,
            "mass_flow_kg_s": darcy_velocity_m_s * area_m2 * density_kg_m3}


def permeability_to_resistance(*, permeability_m2, length_m=None, area_m2=None, viscosity_pa_s=None):
    if None in (length_m, area_m2, viscosity_pa_s):
        raise ValueError("conversion requires geometry and viscosity")
    return viscosity_pa_s * length_m / (permeability_m2 * area_m2)

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
from enum import Enum, IntEnum
import math
from typing import Any, ClassVar


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


PAIR_ROLES = {"SCIENTIFICALLY_COMPETING", "NESTED_LIMIT", "OBSERVATION_OPERATOR_COMPARISON", "NONCOMPETING_COMPONENTS"}
ELIGIBILITY = {"eligible", "ineligible", "unresolved"}
REQUIREMENT_STATUS = {"relevant", "irrelevant", "unresolved"}
QUESTION_RELEVANCE = {"RELEVANT", "EXCLUDED_NONCOMPETING_COMPONENTS",
    "EXCLUDED_OBSERVATION_OPERATOR_RELATIONSHIP", "EXCLUDED_NESTED_LIMIT_ONLY",
    "EXCLUDED_OUTSIDE_EVIDENCE_DOMAIN", "EXCLUDED_DIFFERENT_SCIENTIFIC_QUESTION",
    "EXCLUDED_NO_COMMON_INTERVENTION", "EXCLUDED_NO_DEFENSIBLE_COMPARISON_BASIS"}
MEASUREMENT_CLASSES = {"ROBUSTLY_DISCRIMINATING", "NOMINALLY_DISCRIMINATING_BUT_UNCERTAINTY_OVERLAPS", "NOT_DISCRIMINATING", "UNSUPPORTED", "NOT_ADJUDICATED_MISSING_UNCERTAINTY"}
OUTCOMES = {"SCI_MD_003_RP_A_001_APPARATUS_OBSERVATION_EXPLANATION_SURVIVES", "SCI_MD_003_RP_A_001_DYNAMIC_BED_SIGNATURE_DISTINGUISHABLE", "SCI_MD_003_RP_A_001_SPATIAL_LOCALIZATION_ONLY_DISTINGUISHABLE_ROUTE", "SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED"}


class Record:
    required_nonempty: ClassVar[tuple[str, ...]] = ()

    def __post_init__(self):
        for name in self.required_nonempty:
            if getattr(self, name) in (None, ""):
                raise ValueError(f"{type(self).__name__}.{name} is required")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)  # type: ignore[call-overload]

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        expected = {f.name for f in fields(cls)}  # type: ignore[arg-type]
        if set(data) != expected:
            raise ValueError(f"{cls.__name__} fields mismatch: {set(data) ^ expected}")
        return cls(**data)


@dataclass(frozen=True)
class ResultCell(Record):
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
    time_basis: str = "NOT_APPLICABLE"
    evidence_strength: str = "NOT_PROVIDED"
    evidence_domain_status: str = "NOT_PROVIDED"
    adjudicative: bool = True
    source_kind: str = "SOURCE_NATIVE"
    adapter_id: str = "NONE"
    adapter_version: str = "NONE"
    required_nonempty = ("component_id", "case_id", "observable", "unit")

    def __post_init__(self):
        super().__post_init__()
        if self.support_status not in {s.value for s in SupportStatus}:
            raise ValueError("unknown support status")
        if self.support_status == "SUPPORTED":
            if self.value is None or not math.isfinite(float(self.value)):
                raise ValueError("SUPPORTED requires a finite numeric value")
            if self.unit in ("", "NOT_PROVIDED"):
                raise ValueError("numeric result requires units")
            if "pressure" in self.observable and (self.pressure_node == "NOT_APPLICABLE" or self.pressure_reference == "NOT_APPLICABLE"):
                raise ValueError("pressure result requires node and reference")
            if ("time" in self.observable or self.unit == "s") and self.time_basis == "NOT_APPLICABLE":
                raise ValueError("timing result requires time basis")
        elif self.value is not None:
            raise ValueError("unsupported result cannot carry a numeric value")
        if self.adapter_id == "NONE" and self.adapter_version != "NONE":
            raise ValueError("adapter version requires adapter identity")


@dataclass(frozen=True)
class QuantityRow(Record):
    component_id: str; stage: str; quantity_name: str; direction: str; unit: str
    reference_basis: str; physical_definition: str; role: str; provenance: str
    valid_range: object; evidence_strength: str; independently_variable: str
    relationship_kind: str; comparable_observable_group: str; support_status: str; control_mode: str
    pressure_node: str = "NOT_APPLICABLE"; pressure_reference: str = "NOT_APPLICABLE"
    flow_basis: str = "NOT_APPLICABLE"; mass_basis: str = "NOT_APPLICABLE"
    temperature_basis: str = "NOT_PROVIDED"; spatial_basis: str = "LUMPED"
    initialization: str = "SOURCE_DEFAULT"; history_dependence: str = "NONE"
    adapter_id: str = "NONE"; adapter_version: str = "NONE"
    card_identity: str = "NOT_PROVIDED"; registry_identity: str = "NOT_PROVIDED"; notes: str = ""
    mathematical_domain_status: str = "NOT_PROVIDED"; declared_valid_range: object = "NOT_PROVIDED"
    evidence_domain: str = "NOT_PROVIDED"; evidence_domain_status: str = "NOT_PROVIDED"
    adjudicative_support: str = "NOT_PROVIDED"; adjudicative_exclusion_reason: str = "NOT_APPLICABLE"
    required_nonempty = ("component_id", "stage", "quantity_name", "direction", "unit", "reference_basis", "physical_definition", "role", "provenance")

    def __post_init__(self):
        super().__post_init__()
        if any(v is None for v in asdict(self).values()):
            raise ValueError("inventory fields cannot be omitted or null")
        if self.valid_range == "":
            raise ValueError("unknown valid range must be NOT_PROVIDED")
        if self.support_status not in {s.value for s in SupportStatus}:
            raise ValueError("unknown support status")


@dataclass(frozen=True)
class ExplanationRecord(Record):
    explanation_id: str; component_id: str; scientific_role: str; stage: str
    question_addressed: str; producer_identity: str; card_identity: str; registry_identity: str
    physical_assumptions: list[str]; control_mode: str; pressure_node: str; pressure_reference: str
    input_domain: str; output_observables: list[str]; evidence_domain_status: str
    explanation_kind: str; claim_ceiling: str
    required_nonempty = ("explanation_id", "component_id", "scientific_role", "stage")


@dataclass(frozen=True)
class ScientificQuestionRecord(Record):
    question_id: str; pair_id: str; left_explanation: str; right_explanation: str
    pair_semantics: str; pair_role: str; scientific_purpose: str; scenario_id: str
    control_mode: str; intervention_id: str; comparison_basis: str
    model_roles: list[str]; competing_explanations: bool; observation_operator: bool
    nested_limit: bool; evidence_domain_status: str; relevance_status: str
    exclusion_reason: str; provenance: str; protocol_identity: str
    observation_family: str; candidate_channel_classes: list[str]
    required_nonempty = ("question_id", "pair_id", "left_explanation", "right_explanation",
                         "scenario_id", "intervention_id", "comparison_basis")

    def __post_init__(self):
        super().__post_init__()
        if self.pair_role not in PAIR_ROLES or self.relevance_status not in QUESTION_RELEVANCE:
            raise ValueError("invalid scientific question")


@dataclass(frozen=True)
class ObservationContractRecord(Record):
    observation_contract_id: str; contract_sha256: str; quantity_name: str
    comparable_observable_group: str; channel: str; unit: str; value_type: str
    control_mode: str; pressure_node: str; pressure_reference: str; flow_basis: str
    mass_basis: str; concentration_basis: str; deformation_basis: str
    temperature_basis: str; time_origin: str; event_definition: str
    summary_operator: str; observation_window_start: object; observation_window_end: object
    window_reference: str; spatial_basis: str; aggregation_basis: str
    initialization_history_basis: str; mediation_status: str; adapter_id: str
    adapter_version: str; adapter_contract_hash: str; uncertainty_basis: str
    provenance: str
    required_nonempty = ("observation_contract_id", "contract_sha256", "quantity_name",
                         "channel", "unit", "value_type", "adapter_id", "adapter_version")

    def __post_init__(self):
        super().__post_init__()
        if len(self.contract_sha256) != 64 or not self.adapter_contract_hash:
            raise ValueError("observation contract requires canonical hashes")
        if self.mediation_status == "SOURCE_NATIVE" and self.adapter_id != "DIRECT_NATIVE":
            raise ValueError("source-native contract requires DIRECT_NATIVE")
        applicable = {
            "pressure": ("pressure_node", "pressure_reference"),
            "flow": ("flow_basis",),
            "delivered_mass": ("mass_basis", "time_origin"),
            "first_drip_timing": ("time_origin", "event_definition"),
            "bed_height_or_deformation": ("deformation_basis", "spatial_basis"),
            "spatial_flow_variance": ("spatial_basis", "aggregation_basis"),
            "local_extraction": ("concentration_basis", "spatial_basis"),
        }
        for family, names in applicable.items():
            if family in self.channel and any(getattr(self, name) == "NOT_PROVIDED" for name in names):
                raise ValueError(f"{self.channel} observation contract is incomplete")


@dataclass(frozen=True)
class ComparisonEligibilityRecord(Record):
    pair_id: str; left_explanation: str; right_explanation: str; scientific_question: str
    scenario: str; candidate_observable: str; common_intervention: str; common_output_basis: str
    comparability_level: int; pair_role: str; eligibility: str; reason_code: str
    adapter_id: str; adapter_version: str; uncertainty_available: bool; eligibility_id: str = ""
    requirement_id: str = ""; intervention_id: str = ""; basis_id: str = ""
    support_status: str = "NOT_EVALUATED"; adapter_contract_hash: str = "NOT_APPLICABLE"
    question_id: str = ""; observation_contract_id: str = ""; observation_contract_hash: str = ""
    required_nonempty = ("pair_id", "left_explanation", "right_explanation", "scenario", "candidate_observable", "reason_code")

    def __post_init__(self):
        super().__post_init__()
        if self.comparability_level not in range(1, 6) or self.pair_role not in PAIR_ROLES or self.eligibility not in ELIGIBILITY:
            raise ValueError("invalid pair record")
        if self.eligibility == "eligible" and (self.comparability_level > 2 or self.pair_role not in {"SCIENTIFICALLY_COMPETING", "NESTED_LIMIT"}):
            raise ValueError("ineligible pair presented as discrimination-eligible")
        if self.adapter_id in ("", "NONE") or self.adapter_version in ("", "NONE"):
            raise ValueError("eligibility requires explicit adapter identity and version")
        if self.comparability_level == 1 and self.adapter_id != "DIRECT_NATIVE":
            raise ValueError("level 1 requires DIRECT_NATIVE")
        if self.support_status not in {s.value for s in SupportStatus}:
            raise ValueError("unknown eligibility support status")
        expected = f"ELIG__{self.requirement_id}__{self.candidate_observable}__{self.adapter_id}__{self.adapter_version}"
        if self.eligibility_id != expected:
            raise ValueError("eligibility identity must bind requirement, channel, and adapter")
        if not self.question_id or not self.observation_contract_id or len(self.observation_contract_hash) != 64:
            raise ValueError("eligibility requires question and observation contract identity")


@dataclass(frozen=True)
class DiscriminationRequirementRecord(Record):
    requirement_id: str; pair_id: str; left_explanation: str; right_explanation: str
    scenario: str; control_mode: str; intervention_id: str; pressure_node: str
    pressure_reference: str; basis_id: str; time_basis: str; pair_role: str
    scientific_question: str; relevant_to_final_decision: bool
    applicable_candidate_channels: list[str]; requirement_status: str; reason_code: str
    provenance: str
    question_id: str = ""; observation_family: str = ""; observation_contract_id: str = ""
    spatial_basis: str = "NOT_APPLICABLE"; relevance_status: str = ""
    required_nonempty = ("requirement_id", "pair_id", "left_explanation", "right_explanation",
                         "scenario", "intervention_id", "basis_id", "reason_code")

    def __post_init__(self):
        super().__post_init__()
        if self.pair_role not in PAIR_ROLES or self.requirement_status not in REQUIREMENT_STATUS:
            raise ValueError("invalid discrimination requirement")
        expected = f"REQ__{self.question_id}__{self.pair_id}__{self.scenario}__{self.intervention_id}__{self.basis_id}"
        if self.requirement_id != expected:
            raise ValueError("requirement identity must bind question, pair, scenario, intervention, and basis")
        if self.relevance_status not in QUESTION_RELEVANCE:
            raise ValueError("requirement requires controlled relevance")


@dataclass(frozen=True)
class PredictionIntervalRecord(Record):
    prediction_id: str; explanation_id: str; case_id: str; channel: str; source_result_field: str
    unit: str; pressure_node: str; pressure_reference: str; time_basis: str
    nominal_value: float; lower_bound: float; upper_bound: float
    parameter_uncertainty: object; numerical_uncertainty: object; adapter_uncertainty: object
    initialization_history_uncertainty: object; evidence_domain_status: str; provenance: str
    missing_uncertainty_flags: list[str]
    required_nonempty = ("prediction_id", "explanation_id", "case_id", "channel", "unit")

    def __post_init__(self):
        super().__post_init__()
        if not all(math.isfinite(float(v)) for v in (self.nominal_value, self.lower_bound, self.upper_bound)) or not self.lower_bound <= self.nominal_value <= self.upper_bound:
            raise ValueError("invalid prediction interval")
        if "pressure" in self.channel and (self.pressure_node == "NOT_APPLICABLE" or self.pressure_reference == "NOT_APPLICABLE"):
            raise ValueError("pressure prediction requires node/reference")
        if ("timing" in self.channel or self.unit == "s") and self.time_basis == "NOT_APPLICABLE":
            raise ValueError("timing prediction requires time basis")


@dataclass(frozen=True)
class MeasurementValueRecord(Record):
    measurement_record_id: str; pair_id: str; left_explanation: str; right_explanation: str
    scenario: str; channel: str; comparability_level: int; left_support_state: str; right_support_state: str
    left_prediction_id: str | None; right_prediction_id: str | None
    declared_measurement_uncertainty: object; measurement_uncertainty_provenance: str
    expanded_left_interval: list[float] | None; expanded_right_interval: list[float] | None
    interval_combination_method: str; classification: str; reason_code: str; evidence_label: str
    robustly_covers_pair: bool; claim_ceiling: str; eligibility_id: str = ""
    requirement_id: str = ""; measurement_option_id: str = ""
    adapter_id: str = ""; adapter_version: str = ""; adapter_contract_hash: str = "NOT_APPLICABLE"
    intervention_id: str = ""; basis_id: str = ""; evidence_references: list[str] | None = None
    observation_contract_id: str = ""; observation_contract_hash: str = ""
    required_nonempty = ("measurement_record_id", "pair_id", "scenario", "channel", "reason_code")

    def __post_init__(self):
        super().__post_init__()
        if self.classification not in MEASUREMENT_CLASSES:
            raise ValueError("unknown measurement classification")
        if self.left_support_state not in {s.value for s in SupportStatus} or self.right_support_state not in {s.value for s in SupportStatus}:
            raise ValueError("unknown support state")
        if self.robustly_covers_pair != (self.classification == "ROBUSTLY_DISCRIMINATING"):
            raise ValueError("coverage must derive from robust classification")
        if self.classification == "ROBUSTLY_DISCRIMINATING" and (self.declared_measurement_uncertainty == "NOT_PROVIDED" or self.expanded_left_interval is None or self.expanded_right_interval is None):
            raise ValueError("robust classification requires complete uncertainty")
        if not self.eligibility_id:
            raise ValueError("measurement record requires channel-specific eligibility identity")
        if not all((self.requirement_id, self.measurement_option_id, self.adapter_id,
                    self.adapter_version, self.intervention_id, self.basis_id)):
            raise ValueError("measurement record requires exact requirement and adapter provenance")
        if not self.observation_contract_id or len(self.observation_contract_hash) != 64:
            raise ValueError("measurement record requires observation contract")


@dataclass(frozen=True)
class CoverageEdgeRecord(Record):
    coverage_edge_id: str; requirement_id: str; measurement_record_id: str
    measurement_option_id: str; scenario: str; channel: str; adapter_id: str
    adapter_version: str; classification: str; robust: bool; provenance: str
    observation_contract_id: str = ""; observation_contract_hash: str = ""
    required_nonempty = ("coverage_edge_id", "requirement_id", "measurement_record_id",
                         "measurement_option_id", "scenario", "channel", "adapter_id",
                         "adapter_version")

    def __post_init__(self):
        super().__post_init__()
        if self.classification not in MEASUREMENT_CLASSES:
            raise ValueError("unknown coverage classification")
        if self.robust != (self.classification == "ROBUSTLY_DISCRIMINATING"):
            raise ValueError("coverage edge robustness must derive from classification")
        if not self.observation_contract_id or len(self.observation_contract_hash) != 64:
            raise ValueError("coverage edge requires observation contract")


APPARATUS_GATE_STATUSES = {"PASS", "FAIL", "UNRESOLVED", "NOT_APPLICABLE"}
APPARATUS_EVALUATION_STATUSES = {"NOT_EVALUATED", "PARTIALLY_EVALUATED",
    "SURVIVES_ALL_APPLICABLE_GATES", "RULED_OUT_BY_MATCHED_GATE",
    "UNRESOLVED_MISSING_UNCERTAINTY", "UNRESOLVED_UNSUPPORTED_GATE", "NOT_APPLICABLE"}


@dataclass(frozen=True)
class ApparatusGateSpec(Record):
    gate_id: str; gate_name: str; primary: bool; applicability_rule: str
    required_evidence_type: str; maximum_comparability_level: int
    uncertainty_required: bool; pass_criterion: str; fail_criterion: str
    contract_version: str
    gate_class: str = "conditional"; gate_purpose: str = ""
    applicable_response_summary_ids: list[str] | None = None
    applicable_observation_class: str = ""; required_scenarios: list[str] | None = None
    evidence_query: str = ""; unresolved_rule: str = ""; not_applicable_rule: str = ""
    rule_out_capable: bool = False; protocol_identity: str = ""
    required_nonempty = ("gate_id", "gate_name", "applicability_rule", "contract_version")


@dataclass(frozen=True)
class ApparatusGateResult(Record):
    gate_result_id: str; gate_id: str; apparatus_explanation_id: str
    comparator_explanation_id: str; scenario: str; applicability: str; status: str
    comparison_record_ids: list[str]; measurement_record_ids: list[str]
    uncertainty_state: str; reason_code: str; evidence_provenance: list[str]
    requirement_id: str = ""; observation_contract_id: str = ""
    prediction_interval_ids: list[str] | None = None; gate_evidence_ids: list[str] | None = None
    required_nonempty = ("gate_result_id", "gate_id", "apparatus_explanation_id",
                         "comparator_explanation_id", "scenario", "status", "reason_code")

    def __post_init__(self):
        super().__post_init__()
        if self.status not in APPARATUS_GATE_STATUSES:
            raise ValueError("invalid apparatus gate status")
        if self.status in {"PASS", "FAIL"} and (not self.comparison_record_ids or
                                                 self.uncertainty_state != "COMPLETE"):
            raise ValueError("apparatus pass/fail requires matched evidence and complete uncertainty")
        if self.status == "NOT_APPLICABLE" and self.applicability != "NOT_APPLICABLE_BY_PROTOCOL":
            raise ValueError("apparatus gate cannot be marked not applicable without protocol basis")


@dataclass(frozen=True)
class ApparatusGateEvidenceRecord(Record):
    gate_evidence_id: str; gate_id: str; apparatus_explanation_id: str
    comparator_explanation_id: str; requirement_id: str; scenario: str
    observation_contract_id: str; comparison_record_ids: list[str]
    measurement_record_ids: list[str]; prediction_interval_ids: list[str]
    uncertainty_state: str; derived_comparison_state: str; provenance: list[str]
    required_nonempty = ("gate_evidence_id", "gate_id", "apparatus_explanation_id",
                         "comparator_explanation_id", "requirement_id", "scenario")


@dataclass(frozen=True)
class ApparatusEvaluationRecord(Record):
    evaluation_id: str; apparatus_explanation_ids: list[str]; status: str
    applicable_gate_result_ids: list[str]; passing_gate_result_ids: list[str]
    failing_gate_result_ids: list[str]; unresolved_gate_result_ids: list[str]
    apparatus_gate_coverage_complete: bool; matched_scenario_ids: list[str]
    reason_code: str; contract_version: str
    not_applicable_gate_result_ids: list[str] | None = None
    gate_evidence_ids: list[str] | None = None; uncertainty_complete: bool = False
    rule_out_evidence_ids: list[str] | None = None; survival_evidence_ids: list[str] | None = None
    claim_ceiling: str = "MODEL_RESPONSE_COMPARISON_ONLY__PHYSICAL_VALIDATION_NOT_ESTABLISHED"

    def __post_init__(self):
        if self.status not in APPARATUS_EVALUATION_STATUSES:
            raise ValueError("invalid apparatus evaluation status")


@dataclass(frozen=True)
class ResidualRecord(Record):
    contrast_id: str; left_model_case: str; right_model_case: str; observable: str; unit: str
    comparability_level: int; nested: bool; numeric_difference: float | None; uncertainty: object
    attribution: str; closure_error: float | None; numerical_tolerance: float | None
    decomposition_method: str; causal_eligibility: bool; causal_share: float | None; claim_ceiling: str

    def __post_init__(self):
        if self.numeric_difference is not None and self.comparability_level not in (1, 2):
            raise ValueError("numeric residuals require comparability level 1 or 2")
        if not self.nested and self.causal_share is not None:
            raise ValueError("non-nested comparison cannot carry additive causal share")
        if self.nested and self.closure_error is not None and self.numerical_tolerance is not None and abs(self.closure_error) > self.numerical_tolerance:
            raise ValueError("nested residual does not close")


@dataclass(frozen=True)
class DecisionRecord(Record):
    decision_id: str; selected_outcome: str; decision_rule_version: str; decision_input_hash: str
    eligible_pair_count: int; robust_measurement_record_ids: list[str]
    disqualifying_measurement_record_ids: list[str]; qualifying_comparison_record_ids: list[str]
    qualifying_explanation_ids: list[str]; qualifying_scenario_ids: list[str]
    qualifying_channel_ids: list[str]; minimum_measurement_sets: object; zero_pair_status: str
    unresolved_or_missing_uncertainty_record_ids: list[str]; unsupported_record_summary: dict[str, int]
    nonselection_reasons: dict[str, list[str]]; physical_validation: str; claim_ceiling: str
    apparatus_status: str = "NOT_EVALUATED"; apparatus_gate_coverage_complete: bool = False
    global_coverage_complete: bool = False; qualifying_requirement_ids: list[str] | None = None
    coverage_edge_ids: list[str] | None = None; minimum_set_ids: list[str] | None = None
    apparatus_gate_ids: list[str] | None = None; unresolved_requirement_ids: list[str] | None = None

    def __post_init__(self):
        if self.selected_outcome not in OUTCOMES or self.physical_validation != "NOT_ESTABLISHED":
            raise ValueError("invalid decision")
        if not self.decision_rule_version or len(self.decision_input_hash) != 64:
            raise ValueError("decision requires rule version and SHA-256 input hash")
        if self.apparatus_status not in APPARATUS_EVALUATION_STATUSES:
            raise ValueError("decision requires valid apparatus status")
        if self.eligible_pair_count == 0 and (self.zero_pair_status != "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM" or self.minimum_measurement_sets != "NO_COMPLETE_MEASUREMENT_SET"):
            raise ValueError("empty pair universe cannot produce a successful set")


def numeric_residual(left: ResultCell, right: ResultCell, level: int) -> float:
    if level not in (1, 2) or left.support_status != "SUPPORTED" or right.support_status != "SUPPORTED":
        raise ValueError("numeric residuals require level 1/2 supported cells")
    assert left.value is not None and right.value is not None
    return float(left.value) - float(right.value)


def validate_level_one(left: ResultCell, right: ResultCell) -> None:
    if (left.unit, left.pressure_node, left.pressure_reference, left.reference_basis) != (right.unit, right.pressure_node, right.pressure_reference, right.reference_basis):
        raise ValueError("level 1 requires matching unit, node, reference, and basis")


def flow_conversion(*, darcy_velocity_m_s, area_m2=None, density_kg_m3=None):
    if area_m2 is None or density_kg_m3 is None:
        raise ValueError("flow conversion requires explicit area and density")
    return {"volumetric_flow_m3_s": darcy_velocity_m_s * area_m2, "mass_flow_kg_s": darcy_velocity_m_s * area_m2 * density_kg_m3}


def permeability_to_resistance(*, permeability_m2, length_m=None, area_m2=None, viscosity_pa_s=None):
    if None in (length_m, area_m2, viscosity_pa_s):
        raise ValueError("conversion requires geometry and viscosity")
    return viscosity_pa_s * length_m / (permeability_m2 * area_m2)

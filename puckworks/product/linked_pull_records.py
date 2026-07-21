"""Typed records + deterministic hashing for the Espresso Model Relay (illustrative_linked_pull_v1).

This is PRODUCT-level orchestration bookkeeping, NOT a new scientific component. Every value shown or
handed forward in the relay is a typed `LinkedValue` (name + unit + basis + origin + provenance +
assumption ids); every hand-off between two components is a typed `LinkRecord` (source/target field, unit,
basis, link kind, adapter, assumptions, domain status); every assumption is a first-class
`AssumptionRecord`. The relay's honesty rests on these being explicit and serialized — never a validation
claim inherited from an individual component.

Finite enums (never free-form strings) classify link kinds, value origins, scenario relationships, and
stage statuses. Hashes are computed over canonical JSON with wall-clock timestamps excluded, so a
`--mode fast` run is byte-for-byte reproducible.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
from collections.abc import Mapping
from enum import Enum

RELAY_SCHEMA_VERSION = "1.0"


class LinkKind(str, Enum):
    DIRECT_MODEL_OUTPUT = "DIRECT_MODEL_OUTPUT"        # solid line — a model output consumed as-is
    DOCUMENTED_ADAPTER = "DOCUMENTED_ADAPTER"          # dashed line — a documented product-level adapter
    ILLUSTRATIVE_ASSUMPTION = "ILLUSTRATIVE_ASSUMPTION"  # dotted line — a substantial assumed bridge
    SHARED_INPUT_ONLY = "SHARED_INPUT_ONLY"            # thin grey — same recipe input, no model transfer
    DIAGNOSTIC_ONLY = "DIAGNOSTIC_ONLY"                # thin grey — a read-out, nothing handed forward
    ALTERNATIVE_BRANCH = "ALTERNATIVE_BRANCH"          # branch — an alternative model of the same thing
    REFERENCE_CONSTRAINT = "REFERENCE_CONSTRAINT"      # a reference/source-data constraint, not executed
    OPTIONAL_SLOW_PATH = "OPTIONAL_SLOW_PATH"          # extended-mode-only expensive link
    RIGHTS_BLOCKED = "RIGHTS_BLOCKED"                  # blocked symbol — zero execution


class ValueOrigin(str, Enum):
    USER_INPUT = "USER_INPUT"
    STIPULATED_DEFAULT = "STIPULATED_DEFAULT"
    MODEL_OUTPUT = "MODEL_OUTPUT"
    DOCUMENTED_DERIVATION = "DOCUMENTED_DERIVATION"
    ASSUMED_BRIDGE = "ASSUMED_BRIDGE"
    MEASURED_REFERENCE = "MEASURED_REFERENCE"
    FITTED_REFERENCE = "FITTED_REFERENCE"


class ScenarioRelationship(str, Enum):
    SAME_SCENARIO = "SAME_SCENARIO"
    ADAPTED_SCENARIO = "ADAPTED_SCENARIO"
    NEAREST_VALID_CASE = "NEAREST_VALID_CASE"
    NATIVE_REFERENCE = "NATIVE_REFERENCE"
    NOT_EXECUTED = "NOT_EXECUTED"


class StageStatus(str, Enum):
    EXECUTED = "EXECUTED"
    EXECUTED_WITH_ASSUMPTIONS = "EXECUTED_WITH_ASSUMPTIONS"
    ADAPTED_SCENARIO = "ADAPTED_SCENARIO"
    DOMAIN_REJECTED = "DOMAIN_REJECTED"
    RIGHTS_BLOCKED = "RIGHTS_BLOCKED"
    OPTIONAL_DEPENDENCY_UNAVAILABLE = "OPTIONAL_DEPENDENCY_UNAVAILABLE"
    REFERENCE_ONLY = "REFERENCE_ONLY"
    NOT_SELECTED = "NOT_SELECTED"
    EXECUTION_ERROR = "EXECUTION_ERROR"


# statuses in which a component's producer actually ran (used by engine/tests for the "executed" count)
EXECUTED_STATUSES = (StageStatus.EXECUTED, StageStatus.EXECUTED_WITH_ASSUMPTIONS,
                     StageStatus.ADAPTED_SCENARIO)


@dataclasses.dataclass(frozen=True)
class LinkedValue:
    name: str
    value: object
    unit: str
    basis: str
    origin: ValueOrigin
    source_component_id: str | None = None
    source_field: str | None = None
    assumption_ids: tuple[str, ...] = ()
    notes: str = ""

    def __post_init__(self):
        if self.origin in (ValueOrigin.ASSUMED_BRIDGE,) and not self.assumption_ids:
            raise ValueError(f"assumed value {self.name!r} must reference at least one assumption id")


@dataclasses.dataclass(frozen=True)
class LinkRecord:
    edge_id: str
    source_component_id: str | None
    source_field: str
    target_component_id: str
    target_field: str
    kind: LinkKind
    source_unit: str
    target_unit: str
    source_basis: str
    target_basis: str
    adapter_id: str | None = None
    assumption_ids: tuple[str, ...] = ()
    domain_status: str = "IN_DOMAIN"
    conversion: str = ""              # documented unit/basis conversion formula, when units/bases differ

    def __post_init__(self):
        # a documented adapter or assumed bridge MUST name how it bridged (adapter id and/or assumption)
        if self.kind == LinkKind.DOCUMENTED_ADAPTER and not (self.adapter_id or self.conversion):
            raise ValueError(f"edge {self.edge_id}: DOCUMENTED_ADAPTER needs an adapter_id or conversion")
        if self.kind == LinkKind.ILLUSTRATIVE_ASSUMPTION and not self.assumption_ids:
            raise ValueError(f"edge {self.edge_id}: ILLUSTRATIVE_ASSUMPTION needs an assumption id")
        # a DIRECT hand-off may not silently change unit or basis
        if self.kind == LinkKind.DIRECT_MODEL_OUTPUT:
            if self.source_unit != self.target_unit:
                raise ValueError(f"edge {self.edge_id}: DIRECT link changes unit "
                                 f"{self.source_unit!r}->{self.target_unit!r} without an adapter")
            if self.source_basis != self.target_basis:
                raise ValueError(f"edge {self.edge_id}: DIRECT link changes basis "
                                 f"{self.source_basis!r}->{self.target_basis!r} without an adapter")


@dataclasses.dataclass(frozen=True)
class AssumptionRecord:
    assumption_id: str
    category: str
    statement: str
    rationale: str
    introduced_at_stage: str
    affected_components: tuple[str, ...]
    affected_fields: tuple[str, ...]
    consequence: str
    validation_needed: str
    mathematical_transform: str | None = None


@dataclasses.dataclass
class StageResult:
    component_id: str
    station_id: str
    public_heading: str
    status: StageStatus
    scenario_relationship: ScenarioRelationship
    rights_decision: str
    inputs: list           # list[LinkedValue]
    outputs: list          # list[LinkedValue]
    links_received: list   # list[str] edge_ids
    links_emitted: list    # list[str] edge_ids
    assumption_ids: list   # list[str]
    domain_findings: list  # list[str]
    warnings: list         # list[str]
    evidence_badge: str = ""
    evidence_strength: str = ""
    fidelity_ceiling: str = ""
    producer_ref: str = ""
    figure_ids: list = dataclasses.field(default_factory=list)
    narrative: object = None      # linked_pull_narrative.LinkedStageNarrative
    message: str = ""

    def content_hash(self) -> str:
        return _sha(_stage_payload(self))


# ── serialization + hashing ───────────────────────────────────────────────────────────────
def _enum(v):
    return v.value if isinstance(v, Enum) else v


def value_to_dict(v: LinkedValue) -> dict:
    d = dataclasses.asdict(v)
    d["origin"] = _enum(v.origin)
    d["assumption_ids"] = list(v.assumption_ids)
    d["value"] = _jsonable(v.value)
    return d


def link_to_dict(link: LinkRecord) -> dict:
    d = dataclasses.asdict(link)
    d["kind"] = _enum(link.kind)
    d["assumption_ids"] = list(link.assumption_ids)
    return d


def assumption_to_dict(a: AssumptionRecord) -> dict:
    d = dataclasses.asdict(a)
    d["affected_components"] = list(a.affected_components)
    d["affected_fields"] = list(a.affected_fields)
    return d


class NonCanonicalValue(TypeError):
    """A value cannot be canonically serialized (unsupported type, non-finite float, non-string key)."""


def normalize_for_json(value):
    """Strict, explicit normalization for canonical provenance — NEVER `default=str`.

    Supports dataclasses, enums, str-keyed mappings, tuples/lists, finite floats, ints, bools, str, None,
    approved NumPy scalars, and NumPy arrays (-> deterministic lists). REJECTS NaN/inf, non-string mapping
    keys, and unsupported objects (raising NonCanonicalValue) so a defect surfaces instead of being hidden.
    """
    import numpy as np
    if value is None or isinstance(value, (str, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (int, np.integer)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        f = float(value)
        if not math.isfinite(f):
            raise NonCanonicalValue(f"non-finite float is not canonical: {f!r}")
        return f
    if isinstance(value, np.ndarray):
        return [normalize_for_json(v) for v in value.tolist()]
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {k: normalize_for_json(v) for k, v in dataclasses.asdict(value).items()}
    if isinstance(value, Mapping):
        out = {}
        for k, v in value.items():
            if not isinstance(k, str):
                raise NonCanonicalValue(f"non-string mapping key is not canonical: {k!r}")
            out[k] = normalize_for_json(v)
        return out
    if isinstance(value, (list, tuple)):
        return [normalize_for_json(v) for v in value]
    raise NonCanonicalValue(f"unsupported type for canonical serialization: {type(value).__name__}")


def canonical_json_bytes(value) -> bytes:
    """Deterministic UTF-8 JSON bytes over `normalize_for_json(value)`; rejects NaN/inf (allow_nan=False)."""
    text = json.dumps(normalize_for_json(value), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)
    return text.encode("utf-8")


def canonical_json_text(value, *, indent=2) -> str:
    """Human-readable pretty JSON derived from the SAME normalized object (same values as the hash path)."""
    return json.dumps(normalize_for_json(value), sort_keys=True, indent=indent,
                      ensure_ascii=False, allow_nan=False)


def _jsonable(x):
    """Backwards-compatible alias used by value_to_dict (now strict)."""
    return normalize_for_json(x)


def _stage_payload(s: StageResult) -> dict:
    """Deterministic per-stage payload for the MODEL-OUTPUT hash (no narrative prose, no figures)."""
    return {
        "component_id": s.component_id, "station_id": s.station_id, "status": _enum(s.status),
        "scenario_relationship": _enum(s.scenario_relationship),
        "inputs": [value_to_dict(v) for v in s.inputs],
        "outputs": [value_to_dict(v) for v in s.outputs],
        "links_received": sorted(s.links_received), "links_emitted": sorted(s.links_emitted),
        "assumption_ids": sorted(s.assumption_ids), "domain_findings": list(s.domain_findings),
    }


def _sha(obj) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def model_output_hash(stages: list) -> str:
    """Hash of MODEL outputs + link topology only — reproducible, and independent of prose/figures/clock.
    This is NOT a validation or scientific-certainty hash; it only proves the numbers are deterministic."""
    return _sha([_stage_payload(s) for s in stages])


def artifact_hash(result_dict: dict) -> str:
    """Hash of the complete serialized artifact, with volatile fields (timestamps) already excluded by the
    serializer. NOT a validation hash."""
    volatile = {"generated_at", "wall_clock_s", "runtime_s", "artifact_hash"}
    return _sha({k: v for k, v in result_dict.items() if k not in volatile})

"""Frozen, typed product records (issue #32, PR 1).

Design rules: no NumPy in the public contract; no repository-relative paths; no NaN/infinity; no
mutable containers inside a frozen public record; explicit units; full lowercase digests; unavailable
results carry no fabricated numerical series; stable identifiers rather than display labels; every
cross-reference resolves; each serialized top-level record carries its own schema version.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Optional

from ._enums import (
    AvailabilityStatus,
    CompatibilityStatus,
    ProvenanceSource,
    RecordKind,
    RedistributionStatus,
    RightsReviewStatus,
    SeriesKind,
)

SHOT_INPUT_SCHEMA_VERSION = 1
SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION = 1
MAX_EXPLANATION_CANDIDATES = 3

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _require_nonempty(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_sha256(value, field_name: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.match(value):
        raise ValueError(f"{field_name} must be a full lowercase 64-hex SHA-256; got {value!r}")


def _require_commit(value, field_name: str) -> None:
    if not isinstance(value, str) or not _COMMIT_RE.match(value):
        raise ValueError(f"{field_name} must be a full lowercase 40-hex Git commit; got {value!r}")


def _check_number(v, field_name: str) -> None:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        raise ValueError(f"{field_name} must be a real number (not bool); got {v!r}")
    if math.isnan(v) or math.isinf(v):
        raise ValueError(f"{field_name} must be finite (no NaN/infinity)")


def _require_finite(values, field_name: str) -> None:
    for v in values:
        _check_number(v, field_name)


def _require_finite_nonneg(values, field_name: str) -> None:
    for v in values:
        _check_number(v, field_name)
        if v < 0:
            raise ValueError(f"{field_name} must be non-negative")


def _require_tuple(value, field_name: str) -> None:
    if not isinstance(value, tuple):
        raise ValueError(f"{field_name} must be a tuple (immutable), got {type(value).__name__}")


def _no_duplicates(ids, field_name: str) -> None:
    seen = set()
    for i in ids:
        if i in seen:
            raise ValueError(f"{field_name} has a duplicate id: {i!r}")
        seen.add(i)


@dataclass(frozen=True)
class UnitBinding:
    """An immutable (quantity, unit) pair — replaces a mutable units dict."""

    quantity: str
    unit: str

    def __post_init__(self) -> None:
        _require_nonempty(self.quantity, "UnitBinding.quantity")
        _require_nonempty(self.unit, "UnitBinding.unit")


@dataclass(frozen=True)
class TransformationStep:
    """One documented deterministic transformation applied to source data."""

    step_id: str
    description: str

    def __post_init__(self) -> None:
        _require_nonempty(self.step_id, "TransformationStep.step_id")
        _require_nonempty(self.description, "TransformationStep.description")


@dataclass(frozen=True)
class EvidenceReference:
    """A pointer into the source evidence graph. Preserves the source strength; never upgrades it."""

    evidence_id: str
    source_scheme: str
    source_id: str
    source_evidence_strength: str
    source_gate_status: str
    provenance: str

    def __post_init__(self) -> None:
        _require_nonempty(self.evidence_id, "EvidenceReference.evidence_id")
        _require_nonempty(self.source_scheme, "source_scheme")
        _require_nonempty(self.source_id, "source_id")
        _require_nonempty(self.source_evidence_strength, "source_evidence_strength")
        _require_nonempty(self.source_gate_status, "source_gate_status")
        _require_nonempty(self.provenance, "EvidenceReference.provenance")


@dataclass(frozen=True)
class BuildProvenance:
    """How the bundle-generating build identifies itself. Never sourced from a runtime Git call.

    ``source_commit`` is mandatory and full-length: an ``unset`` public bundle is not permitted.
    """

    package_version: str
    provenance_source: ProvenanceSource
    source_commit: str
    build_identifier: Optional[str] = None
    generation_timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.package_version, "package_version")
        if not isinstance(self.provenance_source, ProvenanceSource):
            raise ValueError("provenance_source must be a ProvenanceSource")
        _require_commit(self.source_commit, "source_commit")
        if self.build_identifier is not None:
            _require_nonempty(self.build_identifier, "build_identifier")
        if self.generation_timestamp is not None:
            _require_nonempty(self.generation_timestamp, "generation_timestamp")


@dataclass(frozen=True)
class FixtureProvenance:
    """Where a bundled fixture came from, under what license, and its rights-review state."""

    fixture_id: str
    record_kind: RecordKind
    source_record: str
    source_version: str
    source_member: str
    license_expression: str
    license_url: str
    attribution: str
    original_sha256: str
    packaged_sha256: str
    rights_basis: str
    rights_review_status: RightsReviewStatus
    redistribution_status: RedistributionStatus
    modification_notice: str
    transformations: tuple = ()
    rights_basis_url: Optional[str] = None
    rights_review_date: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.fixture_id, "fixture_id")
        if not isinstance(self.record_kind, RecordKind):
            raise ValueError("record_kind must be a RecordKind")
        _require_nonempty(self.source_record, "source_record")
        _require_nonempty(self.source_version, "source_version")
        _require_nonempty(self.source_member, "source_member")
        _require_nonempty(self.license_expression, "license_expression")
        _require_nonempty(self.license_url, "license_url")
        _require_nonempty(self.attribution, "attribution")
        _require_nonempty(self.modification_notice, "modification_notice")
        _require_nonempty(self.rights_basis, "rights_basis")
        _require_sha256(self.original_sha256, "original_sha256")
        _require_sha256(self.packaged_sha256, "packaged_sha256")
        if not isinstance(self.rights_review_status, RightsReviewStatus):
            raise ValueError("rights_review_status must be a RightsReviewStatus")
        if not isinstance(self.redistribution_status, RedistributionStatus):
            raise ValueError("redistribution_status must be a RedistributionStatus")
        _require_tuple(self.transformations, "transformations")
        for t in self.transformations:
            if not isinstance(t, TransformationStep):
                raise ValueError("transformations must be TransformationStep instances")

    @property
    def is_redistributable(self) -> bool:
        return (
            self.rights_review_status is RightsReviewStatus.APPROVED
            and self.redistribution_status is RedistributionStatus.REDISTRIBUTABLE
        )


@dataclass(frozen=True)
class TimeAxis:
    """A shared, strictly increasing time base for observed series."""

    time_axis_id: str
    unit: str
    origin: str
    values: tuple

    def __post_init__(self) -> None:
        _require_nonempty(self.time_axis_id, "time_axis_id")
        _require_nonempty(self.unit, "unit")
        _require_nonempty(self.origin, "origin")
        _require_tuple(self.values, "time_axis.values")
        if not self.values:
            raise ValueError("time axis must have values")
        _require_finite(self.values, "time_axis.values")
        if any(b <= a for a, b in zip(self.values, self.values[1:])):
            raise ValueError("time axis must be strictly increasing (no duplicate/backward times)")


@dataclass(frozen=True)
class ObservedSeries:
    """One numerical channel with an explicit origin and availability."""

    series_id: str
    quantity: str
    unit: str
    series_kind: SeriesKind
    availability: AvailabilityStatus
    time_axis_id: str
    values: tuple = ()
    provenance: Optional[str] = None
    uncertainty: Optional[tuple] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.series_id, "series_id")
        _require_nonempty(self.quantity, "quantity")
        if not isinstance(self.series_kind, SeriesKind):
            raise ValueError("series_kind must be a SeriesKind")
        if not isinstance(self.availability, AvailabilityStatus):
            raise ValueError("availability must be an AvailabilityStatus")
        _require_tuple(self.values, f"values[{self.series_id}]")
        if self.availability is AvailabilityStatus.AVAILABLE:
            _require_nonempty(self.unit, "unit")
            _require_nonempty(self.time_axis_id, "time_axis_id")
            _require_nonempty(self.provenance, f"provenance[{self.series_id}]")
            if not self.values:
                raise ValueError(f"available series {self.series_id!r} must carry values")
            _require_finite(self.values, f"values[{self.series_id}]")
            if self.uncertainty is not None:
                _require_tuple(self.uncertainty, f"uncertainty[{self.series_id}]")
                _require_finite_nonneg(self.uncertainty, f"uncertainty[{self.series_id}]")
                if len(self.uncertainty) != len(self.values):
                    raise ValueError("uncertainty length must match values length")
        else:
            if self.values:
                raise ValueError(
                    f"series {self.series_id!r} is {self.availability.value} and must not carry values"
                )
            if self.uncertainty:
                raise ValueError(
                    f"series {self.series_id!r} is {self.availability.value} and must not carry uncertainty"
                )


@dataclass(frozen=True)
class DetectedEvent:
    event_id: str
    time_s: float
    origin: SeriesKind
    provenance: str
    uncertainty_s: Optional[float] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.event_id, "event_id")
        _check_number(self.time_s, "event.time_s")
        if not isinstance(self.origin, SeriesKind):
            raise ValueError("event origin must be a SeriesKind")
        _require_nonempty(self.provenance, "event.provenance")
        if self.uncertainty_s is not None:
            _check_number(self.uncertainty_s, "event.uncertainty_s")
            if self.uncertainty_s < 0:
                raise ValueError("event uncertainty must be non-negative")


@dataclass(frozen=True)
class Caveat:
    caveat_id: str
    category: str
    statement: str
    affected_ids: tuple = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.caveat_id, "caveat_id")
        _require_nonempty(self.category, "caveat.category")
        _require_nonempty(self.statement, "statement")
        _require_tuple(self.affected_ids, "caveat.affected_ids")
        for i in self.affected_ids:
            _require_nonempty(i, "caveat.affected_ids[]")


@dataclass(frozen=True)
class NextMeasurement:
    measurement_id: str
    measurement: str
    rationale: str
    separates_hypotheses: tuple = ()
    required_channel: Optional[str] = None
    caveat_ids: tuple = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.measurement_id, "measurement_id")
        _require_nonempty(self.measurement, "measurement")
        _require_nonempty(self.rationale, "rationale")
        _require_tuple(self.separates_hypotheses, "separates_hypotheses")
        _require_tuple(self.caveat_ids, "next_measurement.caveat_ids")
        if self.required_channel is not None:
            _require_nonempty(self.required_channel, "required_channel")


@dataclass(frozen=True)
class ExplanationCandidate:
    candidate_id: str
    compatibility: CompatibilityStatus
    statement: str
    supporting_observation_ids: tuple = ()
    contradicting_observation_ids: tuple = ()
    missing_evidence: tuple = ()
    evidence_reference_ids: tuple = ()
    caveat_ids: tuple = ()
    next_measurement_id: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.candidate_id, "candidate_id")
        _require_nonempty(self.statement, "statement")
        if not isinstance(self.compatibility, CompatibilityStatus):
            raise ValueError("compatibility must be a CompatibilityStatus")
        for name in ("supporting_observation_ids", "contradicting_observation_ids",
                     "missing_evidence", "evidence_reference_ids", "caveat_ids"):
            _require_tuple(getattr(self, name), f"candidate.{name}")
        _no_duplicates(self.supporting_observation_ids, "supporting_observation_ids")
        _no_duplicates(self.contradicting_observation_ids, "contradicting_observation_ids")
        overlap = set(self.supporting_observation_ids) & set(self.contradicting_observation_ids)
        if overlap:
            raise ValueError(f"observation is both supporting and contradicting: {sorted(overlap)}")


@dataclass(frozen=True)
class ShotInput:
    """The measured input for one shot (or reference case). PR 1 stops here — no analysis."""

    schema_version: int
    fixture_id: str
    provenance: FixtureProvenance
    time_axis: TimeAxis
    series: tuple

    def __post_init__(self) -> None:
        if self.schema_version != SHOT_INPUT_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported ShotInput schema_version {self.schema_version!r}; "
                f"this build supports {SHOT_INPUT_SCHEMA_VERSION}"
            )
        _require_nonempty(self.fixture_id, "fixture_id")
        if not isinstance(self.provenance, FixtureProvenance):
            raise ValueError("provenance must be a FixtureProvenance")
        if self.fixture_id != self.provenance.fixture_id:
            raise ValueError("fixture_id must equal provenance.fixture_id")
        if not isinstance(self.time_axis, TimeAxis):
            raise ValueError("time_axis must be a TimeAxis")
        _require_tuple(self.series, "series")
        if not self.series:
            raise ValueError("a measured fixture must have at least one series")
        _no_duplicates([s.series_id for s in self.series], "series ids")
        for s in self.series:
            if not isinstance(s, ObservedSeries):
                raise ValueError("series must be ObservedSeries instances")
            if s.availability is AvailabilityStatus.AVAILABLE:
                if s.time_axis_id != self.time_axis.time_axis_id:
                    raise ValueError(f"series {s.series_id!r} references an unknown time axis")
                if len(s.values) != len(self.time_axis.values):
                    raise ValueError(f"series {s.series_id!r} length must match the time axis")


@dataclass(frozen=True)
class ShotExplanationBundle:
    """The versioned, deterministic product result. PR 1 emits it with no scientific explanations."""

    schema_version: int
    package_version: str
    build_provenance: BuildProvenance
    fixture_provenance: FixtureProvenance
    normalized_units: tuple = ()
    observations: tuple = ()
    events: tuple = ()
    explanation_candidates: tuple = ()
    evidence_references: tuple = ()
    warnings: tuple = ()
    caveats: tuple = ()
    next_measurement: Optional[NextMeasurement] = None

    def __post_init__(self) -> None:
        if self.schema_version != SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION:
            raise ValueError(
                f"unsupported bundle schema_version {self.schema_version!r}; "
                f"this build supports {SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION}"
            )
        _require_nonempty(self.package_version, "package_version")
        if not isinstance(self.build_provenance, BuildProvenance):
            raise ValueError("build_provenance must be a BuildProvenance")
        if not isinstance(self.fixture_provenance, FixtureProvenance):
            raise ValueError("fixture_provenance must be a FixtureProvenance")
        if self.package_version != self.build_provenance.package_version:
            raise ValueError("package_version must equal build_provenance.package_version")
        for name in ("normalized_units", "observations", "events", "explanation_candidates",
                     "evidence_references", "warnings", "caveats"):
            _require_tuple(getattr(self, name), name)
        for u in self.normalized_units:
            if not isinstance(u, UnitBinding):
                raise ValueError("normalized_units must be UnitBinding instances")
        for o in self.observations:
            if not isinstance(o, ObservedSeries):
                raise ValueError("observations must be ObservedSeries instances")
        # unique ids within each namespace
        obs_ids = [o.series_id for o in self.observations]
        _no_duplicates(obs_ids, "observation ids")
        evid_ids = [e.evidence_id for e in self.evidence_references]
        _no_duplicates(evid_ids, "evidence ids")
        _no_duplicates([e.event_id for e in self.events], "event ids")
        _no_duplicates([c.caveat_id for c in self.caveats], "caveat ids")
        cand_ids = [c.candidate_id for c in self.explanation_candidates]
        _no_duplicates(cand_ids, "candidate ids")
        if len(self.explanation_candidates) > MAX_EXPLANATION_CANDIDATES:
            raise ValueError(f"at most {MAX_EXPLANATION_CANDIDATES} explanation candidates allowed")
        # referential integrity
        obs_set, evid_set, cav_set = set(obs_ids), set(evid_ids), {c.caveat_id for c in self.caveats}
        nm_ids = {self.next_measurement.measurement_id} if self.next_measurement else set()
        for c in self.explanation_candidates:
            for oid in (*c.supporting_observation_ids, *c.contradicting_observation_ids):
                if oid not in obs_set:
                    raise ValueError(f"candidate {c.candidate_id!r} references unknown observation {oid!r}")
            for rid in c.evidence_reference_ids:
                if rid not in evid_set:
                    raise ValueError(f"candidate {c.candidate_id!r} references unknown evidence {rid!r}")
            for cid in c.caveat_ids:
                if cid not in cav_set:
                    raise ValueError(f"candidate {c.candidate_id!r} references unknown caveat {cid!r}")
            if c.next_measurement_id is not None and c.next_measurement_id not in nm_ids:
                raise ValueError(f"candidate {c.candidate_id!r} references unknown next_measurement")


__all__ = [
    "SHOT_INPUT_SCHEMA_VERSION",
    "SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION",
    "MAX_EXPLANATION_CANDIDATES",
    "UnitBinding",
    "TransformationStep",
    "EvidenceReference",
    "BuildProvenance",
    "FixtureProvenance",
    "TimeAxis",
    "ObservedSeries",
    "DetectedEvent",
    "Caveat",
    "NextMeasurement",
    "ExplanationCandidate",
    "ShotInput",
    "ShotExplanationBundle",
]

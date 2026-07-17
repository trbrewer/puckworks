"""Frozen, typed product records (issue #32, PR 1).

Design rules: no NumPy in the public contract; no repository-relative paths; no NaN/infinity; no
mutable containers inside a frozen public record; every public sequence is parameterized and every
element validated; explicit units; full lowercase digests; unavailable results carry no fabricated
numerical series; stable identifiers resolve; a serialized bundle is self-contained (it carries its
own time axes); each serialized top-level record carries its own schema version.
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
_RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)


def _require_nonempty(value, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_nonempty_or_none(value, field_name: str) -> None:
    if value is not None:
        _require_nonempty(value, field_name)


def _require_sha256(value, field_name: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.match(value):
        raise ValueError(f"{field_name} must be a full lowercase 64-hex SHA-256; got {value!r}")


def _require_commit(value, field_name: str) -> None:
    if not isinstance(value, str) or not _COMMIT_RE.match(value):
        raise ValueError(f"{field_name} must be a full lowercase 40-hex Git commit; got {value!r}")


def _require_timestamp(value, field_name: str) -> None:
    if not isinstance(value, str) or not _RFC3339_RE.match(value):
        raise ValueError(f"{field_name} must be an RFC 3339 timestamp with timezone; got {value!r}")


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


def _require_str_tuple(value, field_name: str) -> None:
    _require_tuple(value, field_name)
    for i in value:
        _require_nonempty(i, f"{field_name}[]")


def _no_duplicates(ids, field_name: str) -> None:
    seen: set = set()
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
        _require_nonempty_or_none(self.build_identifier, "build_identifier")
        if self.generation_timestamp is not None:
            _require_timestamp(self.generation_timestamp, "generation_timestamp")


@dataclass(frozen=True)
class FixtureProvenance:
    """Where a bundled fixture came from, its record- and member-level license, and rights state.

    ``record_license_expression`` is what the source *record* displays (e.g. the Zenodo record
    license). ``member_license_expression`` is the license confirmed for the *selected member* — it is
    ``None`` until an authoritative rights review establishes it. These are different facts and are
    kept separate.
    """

    fixture_id: str
    record_kind: RecordKind
    source_record: str
    source_version: str
    source_member: str
    record_license_expression: str
    record_license_url: str
    attribution: str
    original_sha256: str
    packaged_sha256: str
    rights_basis: str
    rights_review_status: RightsReviewStatus
    redistribution_status: RedistributionStatus
    modification_notice: str
    transformations: tuple[TransformationStep, ...] = ()
    member_license_expression: Optional[str] = None
    member_license_url: Optional[str] = None
    rights_basis_url: Optional[str] = None
    rights_review_date: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.fixture_id, "fixture_id")
        if not isinstance(self.record_kind, RecordKind):
            raise ValueError("record_kind must be a RecordKind")
        _require_nonempty(self.source_record, "source_record")
        _require_nonempty(self.source_version, "source_version")
        _require_nonempty(self.source_member, "source_member")
        _require_nonempty(self.record_license_expression, "record_license_expression")
        _require_nonempty(self.record_license_url, "record_license_url")
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
        _require_nonempty_or_none(self.member_license_expression, "member_license_expression")
        _require_nonempty_or_none(self.member_license_url, "member_license_url")
        _require_nonempty_or_none(self.rights_basis_url, "rights_basis_url")
        if self.rights_review_date is not None:
            _require_nonempty(self.rights_review_date, "rights_review_date")
        # consistency: an approved/redistributable fixture must have a member license.
        approved = (
            self.rights_review_status is RightsReviewStatus.APPROVED
            or self.redistribution_status is RedistributionStatus.REDISTRIBUTABLE
        )
        if approved and (self.member_license_expression is None or self.member_license_url is None):
            raise ValueError(
                "an approved/redistributable fixture requires member_license_expression + _url"
            )

    @property
    def is_redistributable(self) -> bool:
        return (
            self.rights_review_status is RightsReviewStatus.APPROVED
            and self.redistribution_status is RedistributionStatus.REDISTRIBUTABLE
            and self.member_license_expression is not None
            and self.member_license_url is not None
        )


@dataclass(frozen=True)
class TimeAxis:
    """A shared, strictly increasing time base for observed series."""

    time_axis_id: str
    unit: str
    origin: str
    values: tuple[float, ...]

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
    values: tuple[float, ...] = ()
    provenance: Optional[str] = None
    uncertainty: Optional[tuple[float, ...]] = None

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
    affected_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.caveat_id, "caveat_id")
        _require_nonempty(self.category, "caveat.category")
        _require_nonempty(self.statement, "statement")
        _require_str_tuple(self.affected_ids, "caveat.affected_ids")


@dataclass(frozen=True)
class NextMeasurement:
    measurement_id: str
    measurement: str
    rationale: str
    separates_hypotheses: tuple[str, ...] = ()
    required_channel: Optional[str] = None
    caveat_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.measurement_id, "measurement_id")
        _require_nonempty(self.measurement, "measurement")
        _require_nonempty(self.rationale, "rationale")
        _require_str_tuple(self.separates_hypotheses, "separates_hypotheses")
        _require_str_tuple(self.caveat_ids, "next_measurement.caveat_ids")
        _require_nonempty_or_none(self.required_channel, "required_channel")


@dataclass(frozen=True)
class ExplanationCandidate:
    candidate_id: str
    compatibility: CompatibilityStatus
    statement: str
    supporting_observation_ids: tuple[str, ...] = ()
    contradicting_observation_ids: tuple[str, ...] = ()
    missing_evidence: tuple[str, ...] = ()
    evidence_reference_ids: tuple[str, ...] = ()
    caveat_ids: tuple[str, ...] = ()
    next_measurement_id: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.candidate_id, "candidate_id")
        _require_nonempty(self.statement, "statement")
        if not isinstance(self.compatibility, CompatibilityStatus):
            raise ValueError("compatibility must be a CompatibilityStatus")
        _require_str_tuple(self.supporting_observation_ids, "supporting_observation_ids")
        _require_str_tuple(self.contradicting_observation_ids, "contradicting_observation_ids")
        _require_str_tuple(self.missing_evidence, "missing_evidence")
        _require_str_tuple(self.evidence_reference_ids, "evidence_reference_ids")
        _require_str_tuple(self.caveat_ids, "candidate.caveat_ids")
        _no_duplicates(self.supporting_observation_ids, "supporting_observation_ids")
        _no_duplicates(self.contradicting_observation_ids, "contradicting_observation_ids")
        _no_duplicates(self.evidence_reference_ids, "evidence_reference_ids")
        overlap = set(self.supporting_observation_ids) & set(self.contradicting_observation_ids)
        if overlap:
            raise ValueError(f"observation is both supporting and contradicting: {sorted(overlap)}")
        _require_nonempty_or_none(self.next_measurement_id, "next_measurement_id")


@dataclass(frozen=True)
class ShotInput:
    """The measured input for one shot (or reference case). PR 1 stops here — no analysis."""

    schema_version: int
    fixture_id: str
    provenance: FixtureProvenance
    time_axis: TimeAxis
    series: tuple[ObservedSeries, ...]

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
    """The versioned, deterministic, self-contained product result.

    It carries its own ``time_axes`` so a consumer can interpret every observation without loading
    the original fixture. PR 1 emits it with no scientific explanations.
    """

    schema_version: int
    package_version: str
    build_provenance: BuildProvenance
    fixture_provenance: FixtureProvenance
    normalized_units: tuple[UnitBinding, ...] = ()
    time_axes: tuple[TimeAxis, ...] = ()
    observations: tuple[ObservedSeries, ...] = ()
    events: tuple[DetectedEvent, ...] = ()
    explanation_candidates: tuple[ExplanationCandidate, ...] = ()
    evidence_references: tuple[EvidenceReference, ...] = ()
    warnings: tuple[str, ...] = ()
    caveats: tuple[Caveat, ...] = ()
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
        # tuple + element types
        for name, typ in (("normalized_units", UnitBinding), ("time_axes", TimeAxis),
                          ("observations", ObservedSeries), ("events", DetectedEvent),
                          ("explanation_candidates", ExplanationCandidate),
                          ("evidence_references", EvidenceReference), ("caveats", Caveat)):
            seq = getattr(self, name)
            _require_tuple(seq, name)
            for el in seq:
                if not isinstance(el, typ):
                    raise ValueError(f"{name} must contain {typ.__name__} instances")
        _require_str_tuple(self.warnings, "warnings")
        if self.next_measurement is not None and not isinstance(self.next_measurement, NextMeasurement):
            raise ValueError("next_measurement must be a NextMeasurement or None")
        # unique ids
        _no_duplicates([u.quantity for u in self.normalized_units], "normalized_units quantities")
        axis_ids = [a.time_axis_id for a in self.time_axes]
        _no_duplicates(axis_ids, "time_axis ids")
        obs_ids = [o.series_id for o in self.observations]
        _no_duplicates(obs_ids, "observation ids")
        evid_ids = [e.evidence_id for e in self.evidence_references]
        _no_duplicates(evid_ids, "evidence ids")
        _no_duplicates([e.event_id for e in self.events], "event ids")
        cav_ids = [c.caveat_id for c in self.caveats]
        _no_duplicates(cav_ids, "caveat ids")
        cand_ids = [c.candidate_id for c in self.explanation_candidates]
        _no_duplicates(cand_ids, "candidate ids")
        if len(self.explanation_candidates) > MAX_EXPLANATION_CANDIDATES:
            raise ValueError(f"at most {MAX_EXPLANATION_CANDIDATES} explanation candidates allowed")
        # observation -> time-axis resolution (self-contained)
        axis_set = set(axis_ids)
        axis_len = {a.time_axis_id: len(a.values) for a in self.time_axes}
        for o in self.observations:
            if o.availability is AvailabilityStatus.AVAILABLE:
                if o.time_axis_id not in axis_set:
                    raise ValueError(f"observation {o.series_id!r} references unknown time axis {o.time_axis_id!r}")
                if len(o.values) != axis_len[o.time_axis_id]:
                    raise ValueError(f"observation {o.series_id!r} length != its time axis")
        # referential integrity for candidates
        obs_set, evid_set, cav_set = set(obs_ids), set(evid_ids), set(cav_ids)
        nm_ids = {self.next_measurement.measurement_id} if self.next_measurement else set()
        if self.next_measurement is not None:
            for cid in self.next_measurement.caveat_ids:
                if cid not in cav_set:
                    raise ValueError(f"next_measurement references unknown caveat {cid!r}")
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

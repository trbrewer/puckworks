"""Frozen, typed product records (issue #32, PR 1).

Design rules: no NumPy in the public contract; no repository-relative paths; no NaN/infinity; explicit
units; full lowercase SHA-256 digests; unavailable results carry no fabricated numerical series;
stable identifiers rather than display labels as references.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Optional

from ._enums import AvailabilityStatus, CompatibilityStatus, RecordKind, SeriesKind

_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def _require_nonempty(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string")


def _require_sha256(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not _SHA256_RE.match(value):
        raise ValueError(f"{field_name} must be a full lowercase 64-hex SHA-256; got {value!r}")


def _require_finite(values: tuple, field_name: str) -> None:
    for v in values:
        if not isinstance(v, (int, float)) or isinstance(v, bool):
            raise ValueError(f"{field_name} must contain only real numbers; got {v!r}")
        if math.isnan(v) or math.isinf(v):
            raise ValueError(f"{field_name} must not contain NaN or infinity")


@dataclass(frozen=True)
class EvidenceReference:
    """A pointer into the source evidence graph. Preserves the source strength; never upgrades it."""

    source_scheme: str
    source_id: str
    source_evidence_strength: str
    source_gate_status: str
    provenance: str

    def __post_init__(self) -> None:
        _require_nonempty(self.source_scheme, "source_scheme")
        _require_nonempty(self.source_id, "source_id")
        _require_nonempty(self.source_evidence_strength, "source_evidence_strength")


@dataclass(frozen=True)
class BuildProvenance:
    """How the bundle-generating build identifies itself. Never sourced from a runtime Git call."""

    package_version: str
    provenance_source: str
    source_commit: Optional[str] = None
    build_identifier: Optional[str] = None
    generation_timestamp: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.package_version, "package_version")
        _require_nonempty(self.provenance_source, "provenance_source")
        if self.source_commit is not None and not _COMMIT_RE.match(self.source_commit):
            raise ValueError("source_commit must be a full 40-hex lowercase commit or None")


@dataclass(frozen=True)
class FixtureProvenance:
    """Where a bundled fixture came from and under what terms it may be redistributed."""

    fixture_id: str
    record_kind: RecordKind
    source_record: str
    source_version: str
    source_member: str
    license: str
    attribution: str
    original_sha256: str
    packaged_sha256: str
    redistribution_status: str
    transformations: tuple = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.fixture_id, "fixture_id")
        if not isinstance(self.record_kind, RecordKind):
            raise ValueError("record_kind must be a RecordKind")
        _require_nonempty(self.source_record, "source_record")
        _require_nonempty(self.license, "license")
        _require_nonempty(self.attribution, "attribution")
        _require_sha256(self.original_sha256, "original_sha256")
        _require_sha256(self.packaged_sha256, "packaged_sha256")


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
        if self.availability is AvailabilityStatus.AVAILABLE:
            _require_nonempty(self.unit, "unit")
            _require_nonempty(self.time_axis_id, "time_axis_id")
            if not self.values:
                raise ValueError(f"available series {self.series_id!r} must carry values")
            _require_finite(self.values, f"values[{self.series_id}]")
            if self.uncertainty is not None:
                _require_finite(self.uncertainty, f"uncertainty[{self.series_id}]")
                if len(self.uncertainty) != len(self.values):
                    raise ValueError("uncertainty length must match values length")
        else:
            if self.values:
                raise ValueError(
                    f"series {self.series_id!r} is {self.availability.value} and must not carry values"
                )


@dataclass(frozen=True)
class TimeAxis:
    """A shared time base for observed series."""

    time_axis_id: str
    unit: str
    origin: str
    values: tuple

    def __post_init__(self) -> None:
        _require_nonempty(self.time_axis_id, "time_axis_id")
        _require_nonempty(self.unit, "unit")
        _require_nonempty(self.origin, "origin")
        if not self.values:
            raise ValueError("time axis must have values")
        _require_finite(self.values, "time_axis.values")
        if any(b <= a for a, b in zip(self.values, self.values[1:])):
            raise ValueError("time axis must be strictly increasing")


@dataclass(frozen=True)
class DetectedEvent:
    event_id: str
    time_s: float
    origin: SeriesKind
    provenance: str
    uncertainty_s: Optional[float] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.event_id, "event_id")
        _require_finite((self.time_s,), "time_s")
        if not isinstance(self.origin, SeriesKind):
            raise ValueError("event origin must be a SeriesKind")


@dataclass(frozen=True)
class Caveat:
    caveat_id: str
    category: str
    statement: str
    affected_ids: tuple = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.caveat_id, "caveat_id")
        _require_nonempty(self.statement, "statement")


@dataclass(frozen=True)
class NextMeasurement:
    measurement_id: str
    measurement: str
    rationale: str
    separates_hypotheses: tuple = ()
    required_channel: Optional[str] = None
    caveats: tuple = ()

    def __post_init__(self) -> None:
        _require_nonempty(self.measurement_id, "measurement_id")
        _require_nonempty(self.measurement, "measurement")
        _require_nonempty(self.rationale, "rationale")


@dataclass(frozen=True)
class ExplanationCandidate:
    candidate_id: str
    compatibility: CompatibilityStatus
    statement: str
    supporting_observation_ids: tuple = ()
    contradicting_observation_ids: tuple = ()
    missing_evidence: tuple = ()
    evidence_references: tuple = ()
    caveat_ids: tuple = ()
    next_measurement_id: Optional[str] = None

    def __post_init__(self) -> None:
        _require_nonempty(self.candidate_id, "candidate_id")
        _require_nonempty(self.statement, "statement")
        if not isinstance(self.compatibility, CompatibilityStatus):
            raise ValueError("compatibility must be a CompatibilityStatus")
        for ref in self.evidence_references:
            if not isinstance(ref, EvidenceReference):
                raise ValueError("evidence_references must be EvidenceReference instances")


@dataclass(frozen=True)
class ShotInput:
    """The measured input for one shot (or reference case). PR 1 stops here — no analysis."""

    fixture_id: str
    provenance: FixtureProvenance
    time_axis: TimeAxis
    series: tuple

    def __post_init__(self) -> None:
        _require_nonempty(self.fixture_id, "fixture_id")
        if not isinstance(self.provenance, FixtureProvenance):
            raise ValueError("provenance must be a FixtureProvenance")
        if not isinstance(self.time_axis, TimeAxis):
            raise ValueError("time_axis must be a TimeAxis")
        for s in self.series:
            if not isinstance(s, ObservedSeries):
                raise ValueError("series must be ObservedSeries instances")
            if s.availability is AvailabilityStatus.AVAILABLE and s.time_axis_id != self.time_axis.time_axis_id:
                raise ValueError(f"series {s.series_id!r} references an unknown time axis")
            if s.availability is AvailabilityStatus.AVAILABLE and len(s.values) != len(self.time_axis.values):
                raise ValueError(f"series {s.series_id!r} length must match the time axis")


@dataclass(frozen=True)
class NormalizedShot:
    """Reserved contract for PR 2. PR 1 defines the type but does not implement normalization."""

    shot_input: ShotInput

    def __post_init__(self) -> None:
        if not isinstance(self.shot_input, ShotInput):
            raise ValueError("shot_input must be a ShotInput")


@dataclass(frozen=True)
class ShotExplanationBundle:
    """The versioned, deterministic product result. PR 1 emits it with no scientific explanations."""

    schema_version: int
    package_version: str
    build_provenance: BuildProvenance
    fixture_provenance: FixtureProvenance
    normalized_units: dict
    observations: tuple = ()
    events: tuple = ()
    explanation_candidates: tuple = ()
    evidence_references: tuple = ()
    warnings: tuple = ()
    caveats: tuple = ()
    next_measurement: Optional[NextMeasurement] = None

    def __post_init__(self) -> None:
        if self.schema_version != 1:
            raise ValueError(f"unsupported schema_version {self.schema_version}; this build supports 1")
        _require_nonempty(self.package_version, "package_version")
        if not isinstance(self.build_provenance, BuildProvenance):
            raise ValueError("build_provenance must be a BuildProvenance")
        if not isinstance(self.fixture_provenance, FixtureProvenance):
            raise ValueError("fixture_provenance must be a FixtureProvenance")
        for o in self.observations:
            if not isinstance(o, ObservedSeries):
                raise ValueError("observations must be ObservedSeries instances")
        for c in self.explanation_candidates:
            if not isinstance(c, ExplanationCandidate):
                raise ValueError("explanation_candidates must be ExplanationCandidate instances")


SCHEMA_VERSION = 1

__all__ = [
    "EvidenceReference",
    "BuildProvenance",
    "FixtureProvenance",
    "ObservedSeries",
    "TimeAxis",
    "DetectedEvent",
    "Caveat",
    "NextMeasurement",
    "ExplanationCandidate",
    "ShotInput",
    "NormalizedShot",
    "ShotExplanationBundle",
    "SCHEMA_VERSION",
]

"""Canonical, deterministic serialization for the product contract (issue #32, PR 1).

Canonical JSON: UTF-8; sorted keys; ``allow_nan=False``; compact separators; a single trailing
newline; identical bytes across supported Python 3.10-3.13 for a given object. No wall-clock and no
Git lookup happen here — provenance values are explicit inputs.
"""
from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum

from ._enums import AvailabilityStatus, CompatibilityStatus, RecordKind, SeriesKind
from ._records import (
    SCHEMA_VERSION,
    BuildProvenance,
    Caveat,
    DetectedEvent,
    EvidenceReference,
    ExplanationCandidate,
    FixtureProvenance,
    NextMeasurement,
    ObservedSeries,
    ShotExplanationBundle,
    ShotInput,
    TimeAxis,
)


def _encode(obj):
    if is_dataclass(obj):
        return {f.name: _encode(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (list, tuple)):
        return [_encode(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _encode(v) for k, v in obj.items()}
    return obj


def to_dict(obj) -> dict:
    """Plain-``dict`` view of a product record (enums as strings, tuples as lists)."""
    return _encode(obj)


def to_json(obj) -> str:
    """Canonical JSON bytes-as-str for a product record."""
    return json.dumps(
        _encode(obj),
        ensure_ascii=False,
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    ) + "\n"


# ---- typed decoders ---------------------------------------------------------

def _tuple(seq):
    return tuple(seq) if seq is not None else ()


def _evidence_reference(d) -> EvidenceReference:
    return EvidenceReference(**d)


def _build_provenance(d) -> BuildProvenance:
    return BuildProvenance(**d)


def _fixture_provenance(d) -> FixtureProvenance:
    return FixtureProvenance(
        fixture_id=d["fixture_id"],
        record_kind=RecordKind(d["record_kind"]),
        source_record=d["source_record"],
        source_version=d["source_version"],
        source_member=d["source_member"],
        license=d["license"],
        attribution=d["attribution"],
        original_sha256=d["original_sha256"],
        packaged_sha256=d["packaged_sha256"],
        redistribution_status=d["redistribution_status"],
        transformations=_tuple(d.get("transformations")),
    )


def _time_axis(d) -> TimeAxis:
    return TimeAxis(
        time_axis_id=d["time_axis_id"], unit=d["unit"], origin=d["origin"], values=_tuple(d["values"])
    )


def _observed_series(d) -> ObservedSeries:
    unc = d.get("uncertainty")
    return ObservedSeries(
        series_id=d["series_id"],
        quantity=d["quantity"],
        unit=d["unit"],
        series_kind=SeriesKind(d["series_kind"]),
        availability=AvailabilityStatus(d["availability"]),
        time_axis_id=d["time_axis_id"],
        values=_tuple(d.get("values")),
        provenance=d.get("provenance"),
        uncertainty=_tuple(unc) if unc is not None else None,
    )


def _detected_event(d) -> DetectedEvent:
    return DetectedEvent(
        event_id=d["event_id"],
        time_s=d["time_s"],
        origin=SeriesKind(d["origin"]),
        provenance=d["provenance"],
        uncertainty_s=d.get("uncertainty_s"),
    )


def _caveat(d) -> Caveat:
    return Caveat(
        caveat_id=d["caveat_id"],
        category=d["category"],
        statement=d["statement"],
        affected_ids=_tuple(d.get("affected_ids")),
    )


def _next_measurement(d):
    if d is None:
        return None
    return NextMeasurement(
        measurement_id=d["measurement_id"],
        measurement=d["measurement"],
        rationale=d["rationale"],
        separates_hypotheses=_tuple(d.get("separates_hypotheses")),
        required_channel=d.get("required_channel"),
        caveats=_tuple(d.get("caveats")),
    )


def _explanation_candidate(d) -> ExplanationCandidate:
    return ExplanationCandidate(
        candidate_id=d["candidate_id"],
        compatibility=CompatibilityStatus(d["compatibility"]),
        statement=d["statement"],
        supporting_observation_ids=_tuple(d.get("supporting_observation_ids")),
        contradicting_observation_ids=_tuple(d.get("contradicting_observation_ids")),
        missing_evidence=_tuple(d.get("missing_evidence")),
        evidence_references=tuple(_evidence_reference(x) for x in d.get("evidence_references", [])),
        caveat_ids=_tuple(d.get("caveat_ids")),
        next_measurement_id=d.get("next_measurement_id"),
    )


def shot_input_from_dict(d) -> ShotInput:
    return ShotInput(
        fixture_id=d["fixture_id"],
        provenance=_fixture_provenance(d["provenance"]),
        time_axis=_time_axis(d["time_axis"]),
        series=tuple(_observed_series(s) for s in d["series"]),
    )


def bundle_from_dict(d) -> ShotExplanationBundle:
    version = d.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ValueError(
            f"unsupported bundle schema_version {version!r}; this build supports {SCHEMA_VERSION}"
        )
    return ShotExplanationBundle(
        schema_version=version,
        package_version=d["package_version"],
        build_provenance=_build_provenance(d["build_provenance"]),
        fixture_provenance=_fixture_provenance(d["fixture_provenance"]),
        normalized_units=dict(d["normalized_units"]),
        observations=tuple(_observed_series(o) for o in d.get("observations", [])),
        events=tuple(_detected_event(e) for e in d.get("events", [])),
        explanation_candidates=tuple(
            _explanation_candidate(c) for c in d.get("explanation_candidates", [])
        ),
        evidence_references=tuple(_evidence_reference(r) for r in d.get("evidence_references", [])),
        warnings=_tuple(d.get("warnings")),
        caveats=tuple(_caveat(c) for c in d.get("caveats", [])),
        next_measurement=_next_measurement(d.get("next_measurement")),
    )


def bundle_from_json(s: str) -> ShotExplanationBundle:
    return bundle_from_dict(json.loads(s))


def shot_input_from_json(s: str) -> ShotInput:
    return shot_input_from_dict(json.loads(s))


__all__ = [
    "to_dict",
    "to_json",
    "bundle_from_dict",
    "bundle_from_json",
    "shot_input_from_dict",
    "shot_input_from_json",
]

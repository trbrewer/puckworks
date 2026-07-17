"""Canonical, deterministic serialization for the product contract (issue #32, PR 1).

Only the explicit top-level records — :class:`ShotInput` and :class:`ShotExplanationBundle` — have
public serializers/readers. Canonical JSON: UTF-8; sorted keys; ``allow_nan=False``; compact
separators; a single trailing newline; identical bytes across supported Python 3.10-3.13. No
wall-clock and no Git lookup happen here. Readers are strict: they require the top-level mapping and
its ``schema_version``, reject unsupported versions, reject unknown top-level fields, and reject
duplicate JSON keys — they never silently ignore or default a supplied field.
"""
from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from enum import Enum

from ._enums import (
    AvailabilityStatus,
    CompatibilityStatus,
    ProvenanceSource,
    RecordKind,
    RedistributionStatus,
    RightsReviewStatus,
    SeriesKind,
)
from ._records import (
    SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION,
    SHOT_INPUT_SCHEMA_VERSION,
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
    TransformationStep,
    UnitBinding,
)


class SchemaError(ValueError):
    """Raised when a serialized product record fails strict decoding."""


# ---- encoding (private) -----------------------------------------------------

def _encode(obj):
    if is_dataclass(obj):
        return {f.name: _encode(getattr(obj, f.name)) for f in fields(obj)}
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, (list, tuple)):
        return [_encode(x) for x in obj]
    return obj


def _canonical_json(payload: dict) -> str:
    return json.dumps(
        payload, ensure_ascii=False, sort_keys=True, allow_nan=False, separators=(",", ":")
    ) + "\n"


# ---- strict decoding helpers ------------------------------------------------

def _no_duplicate_keys(pairs):
    out: dict = {}
    for k, v in pairs:
        if k in out:
            raise SchemaError(f"duplicate JSON key: {k!r}")
        out[k] = v
    return out


def _require_mapping(data, where: str) -> dict:
    if not isinstance(data, dict):
        raise SchemaError(f"{where} must be a JSON object, got {type(data).__name__}")
    return data


def _require_keys(data: dict, expected: set, where: str) -> None:
    keys = set(data)
    unknown = keys - expected
    if unknown:
        raise SchemaError(f"{where} has unknown field(s): {sorted(unknown)}")
    missing = expected - keys
    if missing:
        raise SchemaError(f"{where} is missing required field(s): {sorted(missing)}")


def _require_version(data: dict, expected: int, where: str) -> None:
    v = data.get("schema_version")
    if isinstance(v, bool) or not isinstance(v, int):
        raise SchemaError(f"{where}.schema_version must be an integer, got {v!r}")
    if v != expected:
        raise SchemaError(f"{where} unsupported schema_version {v!r}; this build supports {expected}")


def _tup(seq):
    return tuple(seq) if seq is not None else ()


# ---- nested reconstructors --------------------------------------------------

def _transformation(d) -> TransformationStep:
    return TransformationStep(step_id=d["step_id"], description=d["description"])


def _unit_binding(d) -> UnitBinding:
    return UnitBinding(quantity=d["quantity"], unit=d["unit"])


def _evidence_reference(d) -> EvidenceReference:
    return EvidenceReference(
        evidence_id=d["evidence_id"], source_scheme=d["source_scheme"], source_id=d["source_id"],
        source_evidence_strength=d["source_evidence_strength"], source_gate_status=d["source_gate_status"],
        provenance=d["provenance"],
    )


def _build_provenance(d) -> BuildProvenance:
    return BuildProvenance(
        package_version=d["package_version"],
        provenance_source=ProvenanceSource(d["provenance_source"]),
        source_commit=d["source_commit"],
        build_identifier=d.get("build_identifier"),
        generation_timestamp=d.get("generation_timestamp"),
    )


def _fixture_provenance(d) -> FixtureProvenance:
    return FixtureProvenance(
        fixture_id=d["fixture_id"], record_kind=RecordKind(d["record_kind"]),
        source_record=d["source_record"], source_version=d["source_version"],
        source_member=d["source_member"], license_expression=d["license_expression"],
        license_url=d["license_url"], attribution=d["attribution"],
        original_sha256=d["original_sha256"], packaged_sha256=d["packaged_sha256"],
        rights_basis=d["rights_basis"], rights_review_status=RightsReviewStatus(d["rights_review_status"]),
        redistribution_status=RedistributionStatus(d["redistribution_status"]),
        modification_notice=d["modification_notice"],
        transformations=tuple(_transformation(t) for t in d.get("transformations", [])),
        rights_basis_url=d.get("rights_basis_url"), rights_review_date=d.get("rights_review_date"),
    )


def _time_axis(d) -> TimeAxis:
    return TimeAxis(time_axis_id=d["time_axis_id"], unit=d["unit"], origin=d["origin"],
                    values=_tup(d["values"]))


def _observed_series(d) -> ObservedSeries:
    unc = d.get("uncertainty")
    return ObservedSeries(
        series_id=d["series_id"], quantity=d["quantity"], unit=d["unit"],
        series_kind=SeriesKind(d["series_kind"]), availability=AvailabilityStatus(d["availability"]),
        time_axis_id=d["time_axis_id"], values=_tup(d.get("values")), provenance=d.get("provenance"),
        uncertainty=_tup(unc) if unc is not None else None,
    )


def _detected_event(d) -> DetectedEvent:
    return DetectedEvent(event_id=d["event_id"], time_s=d["time_s"], origin=SeriesKind(d["origin"]),
                         provenance=d["provenance"], uncertainty_s=d.get("uncertainty_s"))


def _caveat(d) -> Caveat:
    return Caveat(caveat_id=d["caveat_id"], category=d["category"], statement=d["statement"],
                  affected_ids=_tup(d.get("affected_ids")))


def _next_measurement(d):
    if d is None:
        return None
    return NextMeasurement(
        measurement_id=d["measurement_id"], measurement=d["measurement"], rationale=d["rationale"],
        separates_hypotheses=_tup(d.get("separates_hypotheses")), required_channel=d.get("required_channel"),
        caveat_ids=_tup(d.get("caveat_ids")),
    )


def _explanation_candidate(d) -> ExplanationCandidate:
    return ExplanationCandidate(
        candidate_id=d["candidate_id"], compatibility=CompatibilityStatus(d["compatibility"]),
        statement=d["statement"], supporting_observation_ids=_tup(d.get("supporting_observation_ids")),
        contradicting_observation_ids=_tup(d.get("contradicting_observation_ids")),
        missing_evidence=_tup(d.get("missing_evidence")),
        evidence_reference_ids=_tup(d.get("evidence_reference_ids")), caveat_ids=_tup(d.get("caveat_ids")),
        next_measurement_id=d.get("next_measurement_id"),
    )


# ---- public top-level serializers -------------------------------------------

_SHOT_INPUT_KEYS = {"schema_version", "fixture_id", "provenance", "time_axis", "series"}
_BUNDLE_KEYS = {
    "schema_version", "package_version", "build_provenance", "fixture_provenance", "normalized_units",
    "observations", "events", "explanation_candidates", "evidence_references", "warnings", "caveats",
    "next_measurement",
}


def shot_input_to_dict(shot: ShotInput) -> dict:
    if not isinstance(shot, ShotInput):
        raise TypeError("shot_input_to_dict expects a ShotInput")
    return _encode(shot)


def shot_input_to_json(shot: ShotInput) -> str:
    return _canonical_json(shot_input_to_dict(shot))


def shot_input_from_dict(data) -> ShotInput:
    d = _require_mapping(data, "ShotInput")
    _require_version(d, SHOT_INPUT_SCHEMA_VERSION, "ShotInput")
    _require_keys(d, _SHOT_INPUT_KEYS, "ShotInput")
    return ShotInput(
        schema_version=d["schema_version"], fixture_id=d["fixture_id"],
        provenance=_fixture_provenance(_require_mapping(d["provenance"], "ShotInput.provenance")),
        time_axis=_time_axis(_require_mapping(d["time_axis"], "ShotInput.time_axis")),
        series=tuple(_observed_series(s) for s in d["series"]),
    )


def shot_input_from_json(text: str) -> ShotInput:
    return shot_input_from_dict(json.loads(text, object_pairs_hook=_no_duplicate_keys))


def bundle_to_dict(bundle: ShotExplanationBundle) -> dict:
    if not isinstance(bundle, ShotExplanationBundle):
        raise TypeError("bundle_to_dict expects a ShotExplanationBundle")
    return _encode(bundle)


def bundle_to_json(bundle: ShotExplanationBundle) -> str:
    return _canonical_json(bundle_to_dict(bundle))


def bundle_from_dict(data) -> ShotExplanationBundle:
    d = _require_mapping(data, "ShotExplanationBundle")
    _require_version(d, SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION, "ShotExplanationBundle")
    _require_keys(d, _BUNDLE_KEYS, "ShotExplanationBundle")
    return ShotExplanationBundle(
        schema_version=d["schema_version"], package_version=d["package_version"],
        build_provenance=_build_provenance(_require_mapping(d["build_provenance"], "build_provenance")),
        fixture_provenance=_fixture_provenance(_require_mapping(d["fixture_provenance"], "fixture_provenance")),
        normalized_units=tuple(_unit_binding(u) for u in d["normalized_units"]),
        observations=tuple(_observed_series(o) for o in d["observations"]),
        events=tuple(_detected_event(e) for e in d["events"]),
        explanation_candidates=tuple(_explanation_candidate(c) for c in d["explanation_candidates"]),
        evidence_references=tuple(_evidence_reference(r) for r in d["evidence_references"]),
        warnings=_tup(d["warnings"]),
        caveats=tuple(_caveat(c) for c in d["caveats"]),
        next_measurement=_next_measurement(d["next_measurement"]),
    )


def bundle_from_json(text: str) -> ShotExplanationBundle:
    return bundle_from_dict(json.loads(text, object_pairs_hook=_no_duplicate_keys))


__all__ = [
    "SchemaError",
    "shot_input_to_dict",
    "shot_input_to_json",
    "shot_input_from_dict",
    "shot_input_from_json",
    "bundle_to_dict",
    "bundle_to_json",
    "bundle_from_dict",
    "bundle_from_json",
]

"""Canonical, deterministic serialization for the product contract (issue #32, PR 1).

Only the explicit top-level records — :class:`ShotInput` and :class:`ShotExplanationBundle` — have
public serializers/readers. Canonical JSON: UTF-8; sorted keys; ``allow_nan=False``; compact
separators; a single trailing newline; identical bytes across supported Python 3.10-3.13. No
wall-clock and no Git lookup happen here. Decoding is strict and **recursive**: every nested record
requires its exact key set, rejects unknown fields, rejects duplicate JSON keys, validates container
types, reports a path-aware :class:`SchemaError`, and never silently ignores or defaults a field.
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


def _fieldset(record_type) -> set:
    return {f.name for f in fields(record_type)}


def _obj(data, record_type, path: str) -> dict:
    """Require a mapping whose keys are exactly ``record_type``'s fields."""
    if not isinstance(data, dict):
        raise SchemaError(f"{path} must be a JSON object, got {type(data).__name__}")
    expected = _fieldset(record_type)
    keys = set(data)
    unknown = keys - expected
    if unknown:
        raise SchemaError(f"{path} has unknown field(s): {sorted(unknown)}")
    missing = expected - keys
    if missing:
        raise SchemaError(f"{path} is missing field(s): {sorted(missing)}")
    return data


def _arr(data, path: str) -> list:
    if not isinstance(data, list):
        raise SchemaError(f"{path} must be a JSON array, got {type(data).__name__}")
    return data


def _enum(cls, value, path: str):
    try:
        return cls(value)
    except ValueError as exc:
        raise SchemaError(f"{path}: invalid {cls.__name__} {value!r}") from exc


def _construct(ctor, path: str, **kw):
    try:
        return ctor(**kw)
    except (ValueError, TypeError) as exc:
        raise SchemaError(f"{path}: {exc}") from exc


def _opt_tuple(seq, path: str):
    if seq is None:
        return None
    return tuple(_arr(seq, path))


# ---- nested reconstructors (strict, path-aware) -----------------------------

def _transformation(d, path) -> TransformationStep:
    d = _obj(d, TransformationStep, path)
    return _construct(TransformationStep, path, step_id=d["step_id"], description=d["description"])


def _unit_binding(d, path) -> UnitBinding:
    d = _obj(d, UnitBinding, path)
    return _construct(UnitBinding, path, quantity=d["quantity"], unit=d["unit"])


def _evidence_reference(d, path) -> EvidenceReference:
    d = _obj(d, EvidenceReference, path)
    return _construct(EvidenceReference, path, evidence_id=d["evidence_id"],
                      source_scheme=d["source_scheme"], source_id=d["source_id"],
                      source_evidence_strength=d["source_evidence_strength"],
                      source_gate_status=d["source_gate_status"], provenance=d["provenance"])


def _build_provenance(d, path) -> BuildProvenance:
    d = _obj(d, BuildProvenance, path)
    return _construct(BuildProvenance, path, package_version=d["package_version"],
                      provenance_source=_enum(ProvenanceSource, d["provenance_source"], f"{path}.provenance_source"),
                      source_commit=d["source_commit"], build_identifier=d["build_identifier"],
                      generation_timestamp=d["generation_timestamp"])


def _fixture_provenance(d, path) -> FixtureProvenance:
    d = _obj(d, FixtureProvenance, path)
    return _construct(
        FixtureProvenance, path, fixture_id=d["fixture_id"],
        record_kind=_enum(RecordKind, d["record_kind"], f"{path}.record_kind"),
        source_record=d["source_record"], source_version=d["source_version"],
        source_member=d["source_member"], record_license_expression=d["record_license_expression"],
        record_license_url=d["record_license_url"], attribution=d["attribution"],
        original_sha256=d["original_sha256"], packaged_sha256=d["packaged_sha256"],
        rights_basis=d["rights_basis"],
        rights_review_status=_enum(RightsReviewStatus, d["rights_review_status"], f"{path}.rights_review_status"),
        redistribution_status=_enum(RedistributionStatus, d["redistribution_status"], f"{path}.redistribution_status"),
        modification_notice=d["modification_notice"],
        transformations=tuple(_transformation(t, f"{path}.transformations[{i}]")
                              for i, t in enumerate(_arr(d["transformations"], f"{path}.transformations"))),
        member_license_expression=d["member_license_expression"],
        member_license_url=d["member_license_url"], rights_basis_url=d["rights_basis_url"],
        rights_review_date=d["rights_review_date"],
    )


def _time_axis(d, path) -> TimeAxis:
    d = _obj(d, TimeAxis, path)
    return _construct(TimeAxis, path, time_axis_id=d["time_axis_id"], unit=d["unit"],
                      origin=d["origin"], values=tuple(_arr(d["values"], f"{path}.values")))


def _observed_series(d, path) -> ObservedSeries:
    d = _obj(d, ObservedSeries, path)
    return _construct(ObservedSeries, path, series_id=d["series_id"], quantity=d["quantity"],
                      unit=d["unit"], series_kind=_enum(SeriesKind, d["series_kind"], f"{path}.series_kind"),
                      availability=_enum(AvailabilityStatus, d["availability"], f"{path}.availability"),
                      time_axis_id=d["time_axis_id"], values=tuple(_arr(d["values"], f"{path}.values")),
                      provenance=d["provenance"], uncertainty=_opt_tuple(d["uncertainty"], f"{path}.uncertainty"))


def _detected_event(d, path) -> DetectedEvent:
    d = _obj(d, DetectedEvent, path)
    return _construct(DetectedEvent, path, event_id=d["event_id"], time_s=d["time_s"],
                      origin=_enum(SeriesKind, d["origin"], f"{path}.origin"),
                      provenance=d["provenance"], uncertainty_s=d["uncertainty_s"])


def _caveat(d, path) -> Caveat:
    d = _obj(d, Caveat, path)
    return _construct(Caveat, path, caveat_id=d["caveat_id"], category=d["category"],
                      statement=d["statement"], affected_ids=tuple(_arr(d["affected_ids"], f"{path}.affected_ids")))


def _next_measurement(d, path):
    if d is None:
        return None
    d = _obj(d, NextMeasurement, path)
    return _construct(NextMeasurement, path, measurement_id=d["measurement_id"],
                      measurement=d["measurement"], rationale=d["rationale"],
                      separates_hypotheses=tuple(_arr(d["separates_hypotheses"], f"{path}.separates_hypotheses")),
                      required_channel=d["required_channel"],
                      caveat_ids=tuple(_arr(d["caveat_ids"], f"{path}.caveat_ids")))


def _explanation_candidate(d, path) -> ExplanationCandidate:
    d = _obj(d, ExplanationCandidate, path)
    return _construct(
        ExplanationCandidate, path, candidate_id=d["candidate_id"],
        compatibility=_enum(CompatibilityStatus, d["compatibility"], f"{path}.compatibility"),
        statement=d["statement"],
        supporting_observation_ids=tuple(_arr(d["supporting_observation_ids"], f"{path}.supporting_observation_ids")),
        contradicting_observation_ids=tuple(_arr(d["contradicting_observation_ids"], f"{path}.contradicting_observation_ids")),
        missing_evidence=tuple(_arr(d["missing_evidence"], f"{path}.missing_evidence")),
        evidence_reference_ids=tuple(_arr(d["evidence_reference_ids"], f"{path}.evidence_reference_ids")),
        caveat_ids=tuple(_arr(d["caveat_ids"], f"{path}.caveat_ids")),
        next_measurement_id=d["next_measurement_id"],
    )


# ---- version helper ---------------------------------------------------------

def _require_version(data: dict, expected: int, where: str) -> None:
    v = data.get("schema_version")
    if isinstance(v, bool) or not isinstance(v, int):
        raise SchemaError(f"{where}.schema_version must be an integer, got {v!r}")
    if v != expected:
        raise SchemaError(f"{where} unsupported schema_version {v!r}; this build supports {expected}")


# ---- public top-level serializers -------------------------------------------

def shot_input_to_dict(shot: ShotInput) -> dict:
    if not isinstance(shot, ShotInput):
        raise TypeError("shot_input_to_dict expects a ShotInput")
    return _encode(shot)


def shot_input_to_json(shot: ShotInput) -> str:
    return _canonical_json(shot_input_to_dict(shot))


def shot_input_from_dict(data) -> ShotInput:
    d = _obj(data, ShotInput, "ShotInput")
    _require_version(d, SHOT_INPUT_SCHEMA_VERSION, "ShotInput")
    return _construct(
        ShotInput, "ShotInput", schema_version=d["schema_version"], fixture_id=d["fixture_id"],
        provenance=_fixture_provenance(d["provenance"], "ShotInput.provenance"),
        time_axis=_time_axis(d["time_axis"], "ShotInput.time_axis"),
        series=tuple(_observed_series(s, f"ShotInput.series[{i}]")
                     for i, s in enumerate(_arr(d["series"], "ShotInput.series"))),
    )


def shot_input_from_json(text: str) -> ShotInput:
    try:
        data = json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"invalid JSON: {exc}") from exc
    return shot_input_from_dict(data)


def bundle_to_dict(bundle: ShotExplanationBundle) -> dict:
    if not isinstance(bundle, ShotExplanationBundle):
        raise TypeError("bundle_to_dict expects a ShotExplanationBundle")
    return _encode(bundle)


def bundle_to_json(bundle: ShotExplanationBundle) -> str:
    return _canonical_json(bundle_to_dict(bundle))


def bundle_from_dict(data) -> ShotExplanationBundle:
    d = _obj(data, ShotExplanationBundle, "ShotExplanationBundle")
    _require_version(d, SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION, "ShotExplanationBundle")
    B = "ShotExplanationBundle"
    return _construct(
        ShotExplanationBundle, B, schema_version=d["schema_version"], package_version=d["package_version"],
        build_provenance=_build_provenance(d["build_provenance"], f"{B}.build_provenance"),
        fixture_provenance=_fixture_provenance(d["fixture_provenance"], f"{B}.fixture_provenance"),
        normalized_units=tuple(_unit_binding(u, f"{B}.normalized_units[{i}]")
                               for i, u in enumerate(_arr(d["normalized_units"], f"{B}.normalized_units"))),
        time_axes=tuple(_time_axis(a, f"{B}.time_axes[{i}]")
                        for i, a in enumerate(_arr(d["time_axes"], f"{B}.time_axes"))),
        observations=tuple(_observed_series(o, f"{B}.observations[{i}]")
                           for i, o in enumerate(_arr(d["observations"], f"{B}.observations"))),
        events=tuple(_detected_event(e, f"{B}.events[{i}]")
                     for i, e in enumerate(_arr(d["events"], f"{B}.events"))),
        explanation_candidates=tuple(_explanation_candidate(c, f"{B}.explanation_candidates[{i}]")
                                     for i, c in enumerate(_arr(d["explanation_candidates"], f"{B}.explanation_candidates"))),
        evidence_references=tuple(_evidence_reference(r, f"{B}.evidence_references[{i}]")
                                  for i, r in enumerate(_arr(d["evidence_references"], f"{B}.evidence_references"))),
        warnings=tuple(_arr(d["warnings"], f"{B}.warnings")),
        caveats=tuple(_caveat(c, f"{B}.caveats[{i}]")
                      for i, c in enumerate(_arr(d["caveats"], f"{B}.caveats"))),
        next_measurement=_next_measurement(d["next_measurement"], f"{B}.next_measurement"),
    )


def bundle_from_json(text: str) -> ShotExplanationBundle:
    try:
        data = json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise SchemaError(f"invalid JSON: {exc}") from exc
    return bundle_from_dict(data)


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

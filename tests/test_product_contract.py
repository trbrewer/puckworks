"""PR 1 contract tests for ``puckworks.product`` (issue #32).

Covers public API, schema versioning, immutability, numeric validation, referential integrity,
self-contained time axes, recursive strict decoding, record/member license separation, rights-gated
fixtures, build provenance (no Git), serialization + golden regression.
"""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

import pytest

import puckworks
from puckworks import product as p
from puckworks.product import _fixtures

FIXTURE_ID = "waszkiewicz2025_9bar_single_shot"
GOLDEN = Path(__file__).parent / "product" / "golden_shot_input.json"
GOLDEN_SHA256 = "7a0eb5366f49c70ebd649110fb9aab61f8d0d33f3e3060c9de5ec444d983fa74"
FULL_COMMIT = "a" * 40

_EXPECTED_PUBLIC = {
    "SHOT_INPUT_SCHEMA_VERSION", "SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION", "MAX_EXPLANATION_CANDIDATES",
    "SeriesKind", "AvailabilityStatus", "CompatibilityStatus", "RecordKind", "ProvenanceSource",
    "RightsReviewStatus", "RedistributionStatus", "UnitBinding", "TransformationStep",
    "EvidenceReference", "BuildProvenance", "FixtureProvenance", "TimeAxis", "ObservedSeries",
    "DetectedEvent", "Caveat", "NextMeasurement", "ExplanationCandidate", "ShotInput",
    "ShotExplanationBundle", "shot_input_to_dict", "shot_input_to_json", "shot_input_from_dict",
    "shot_input_from_json", "bundle_to_dict", "bundle_to_json", "bundle_from_dict", "bundle_from_json",
    "build_provenance", "dev_build_identifier", "available_fixtures", "load_bundled_shot",
    "SchemaError", "ProvenanceUnavailableError", "FixtureManifestError", "FixtureRightsError",
}


def _shot():
    return _fixtures._load(FIXTURE_ID, require_rights=False)


def _bundle(**over):
    shot = _shot()
    kw = dict(
        schema_version=1, package_version=puckworks.__version__,
        build_provenance=p.build_provenance(source_commit=FULL_COMMIT),
        fixture_provenance=shot.provenance,
        normalized_units=(p.UnitBinding("time", "s"), p.UnitBinding("mass", "g")),
        time_axes=(shot.time_axis,), observations=tuple(shot.series), warnings=("PR1 contract only",),
    )
    kw.update(over)
    return p.ShotExplanationBundle(**kw)


# ---- 1. public API ----------------------------------------------------------

def test_all_is_unique_list_and_matches_expected():
    assert isinstance(p.__all__, list)
    assert len(p.__all__) == len(set(p.__all__))
    assert set(p.__all__) == _EXPECTED_PUBLIC   # deliberate change only


def test_every_public_symbol_exists():
    for name in p.__all__:
        assert hasattr(p, name), name


def test_no_underscore_modules_or_placeholders_public():
    assert "NormalizedShot" not in p.__all__ and not hasattr(p, "NormalizedShot")
    for name in ("to_json", "to_dict", "_encode", "_records", "_serialize", "_fixtures"):
        assert name not in p.__all__


def test_docs_api_agrees():
    api = (Path(__file__).parents[1] / "docs" / "API.md").read_text()
    for token in ("puckworks.product", "shot_input_to_json", "time_axes", "SHOT_INPUT_SCHEMA_VERSION"):
        assert token in api, token


# ---- 2. schema versioning ---------------------------------------------------

def test_schema_versions_present():
    assert json.loads(p.shot_input_to_json(_shot()))["schema_version"] == p.SHOT_INPUT_SCHEMA_VERSION
    assert json.loads(p.bundle_to_json(_bundle()))["schema_version"] == p.SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION


@pytest.mark.parametrize("mut", [
    lambda d: d.pop("schema_version"),
    lambda d: d.update(schema_version=99),
    lambda d: d.update(schema_version=True),
    lambda d: d.update(surprise=1),
])
def test_bad_top_level_schema_fails(mut):
    d = p.bundle_to_dict(_bundle())
    mut(d)
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_duplicate_json_keys_fail():
    with pytest.raises(p.SchemaError):
        p.shot_input_from_json('{"schema_version":1,"schema_version":1}')


def test_invalid_json_becomes_schema_error():
    with pytest.raises(p.SchemaError):
        p.bundle_from_json("{not json")


def test_shot_input_dict_rejected_by_bundle_reader():
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(p.shot_input_to_dict(_shot()))


# ---- 3. recursive strict decoding -------------------------------------------

def test_nested_unknown_field_rejected():
    d = p.bundle_to_dict(_bundle())
    d["observations"][0]["surprise"] = 1
    with pytest.raises(p.SchemaError, match=r"observations\[0\]"):
        p.bundle_from_dict(d)


def test_nested_missing_field_rejected():
    d = p.bundle_to_dict(_bundle())
    d["observations"][0].pop("unit")
    with pytest.raises(p.SchemaError, match=r"observations\[0\]"):
        p.bundle_from_dict(d)


def test_nested_wrong_container_type_rejected():
    d = p.bundle_to_dict(_bundle())
    d["time_axes"][0]["values"] = "notarray"
    with pytest.raises(p.SchemaError, match=r"time_axes\[0\].values"):
        p.bundle_from_dict(d)


def test_nested_bad_enum_rejected():
    d = p.bundle_to_dict(_bundle())
    d["observations"][0]["series_kind"] = "bogus"
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_nested_invalid_number_rejected():
    d = p.bundle_to_dict(_bundle())
    d["observations"][0]["values"][0] = "x"
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


# ---- 4. immutability + numeric ---------------------------------------------

def test_records_frozen():
    with pytest.raises(Exception):
        _bundle().package_version = "x"


def test_no_mutable_dict_in_records():
    assert isinstance(_bundle().normalized_units, tuple)


@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_rejected(bad):
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "u", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (1.0, bad), provenance="prov")


def test_bool_as_number_rejected():
    with pytest.raises(ValueError):
        p.TimeAxis("t", "s", "o", (True, False))


def test_time_strictly_increasing():
    with pytest.raises(ValueError):
        p.TimeAxis("t", "s", "o", (0.0, 0.0))


def test_unavailable_series_rejects_values():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "bar", p.SeriesKind.PREDICTED, p.AvailabilityStatus.UNAVAILABLE,
                         "t", (1.0,))


def test_uncertainty_sign_and_length():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "b", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (1.0,), provenance="p", uncertainty=(-0.1,))
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "b", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (1.0, 2.0), provenance="p", uncertainty=(0.1,))


# ---- 5. self-contained time axes --------------------------------------------

def test_bundle_carries_time_axes():
    assert '"time_axes"' in p.bundle_to_json(_bundle())


def test_observation_unknown_time_axis_fails():
    shot = _shot()
    with pytest.raises(ValueError):
        _bundle(time_axes=())  # observations reference an axis that isn't bundled


def test_duplicate_time_axis_ids_fail():
    a = _shot().time_axis
    with pytest.raises(ValueError):
        _bundle(time_axes=(a, a))


def test_observation_axis_length_mismatch_fails():
    shot = _shot()
    short_axis = p.TimeAxis(shot.time_axis.time_axis_id, "s", "o", (0.0, 1.0))
    with pytest.raises(ValueError):
        _bundle(time_axes=(short_axis,))


# ---- 6. identity + references -----------------------------------------------

def test_more_than_three_candidates_fails():
    cands = tuple(p.ExplanationCandidate(f"c{i}", p.CompatibilityStatus.INSUFFICIENT_EVIDENCE, "s")
                  for i in range(4))
    with pytest.raises(ValueError):
        _bundle(explanation_candidates=cands)


def test_candidate_unknown_refs_fail():
    with pytest.raises(ValueError):
        _bundle(explanation_candidates=(p.ExplanationCandidate(
            "c1", p.CompatibilityStatus.COMPATIBLE, "s", supporting_observation_ids=("nope",)),))
    with pytest.raises(ValueError):
        _bundle(explanation_candidates=(p.ExplanationCandidate(
            "c1", p.CompatibilityStatus.COMPATIBLE, "s", evidence_reference_ids=("nope",)),))


def test_support_contradict_overlap_fails():
    with pytest.raises(ValueError):
        p.ExplanationCandidate("c1", p.CompatibilityStatus.PARTLY_COMPATIBLE, "s",
                               supporting_observation_ids=("o",), contradicting_observation_ids=("o",))


def test_duplicate_evidence_ids_fail():
    e = p.EvidenceReference("e1", "paper3", "claim", "post_fit", "PASS", "prov")
    with pytest.raises(ValueError):
        _bundle(evidence_references=(e, e))


def test_next_measurement_caveat_must_resolve():
    nm = p.NextMeasurement("m1", "measure", "why", caveat_ids=("missing",))
    with pytest.raises(ValueError):
        _bundle(next_measurement=nm)


def test_package_version_must_match_provenance():
    with pytest.raises(ValueError):
        _bundle(package_version="9.9.9")


# ---- 7. evidence semantics --------------------------------------------------

def test_evidence_strength_survives_round_trip():
    e = p.EvidenceReference("e1", "paper3", "claim-x", "post_fit_reconstruction", "ACKNOWLEDGED", "prov")
    c = p.ExplanationCandidate("c1", p.CompatibilityStatus.COMPATIBLE, "s", evidence_reference_ids=("e1",))
    b2 = p.bundle_from_json(p.bundle_to_json(_bundle(evidence_references=(e,), explanation_candidates=(c,))))
    assert b2.evidence_references[0].source_evidence_strength == "post_fit_reconstruction"
    assert b2.evidence_references[0].source_gate_status == "ACKNOWLEDGED"


# ---- 8. license separation + rights gate ------------------------------------

def test_record_and_member_license_are_separate():
    prov = _shot().provenance
    assert prov.record_license_expression == "CC-BY-4.0"
    assert prov.member_license_expression is None   # pending
    assert prov.member_license_url is None
    assert not prov.is_redistributable


def test_available_fixtures_empty_while_pending():
    assert p.available_fixtures() == ()


def test_public_loader_refuses_pending():
    with pytest.raises(p.FixtureRightsError):
        p.load_bundled_shot(FIXTURE_ID)


def test_approved_fixture_requires_member_license():
    # constructing an approved provenance without a member license must fail.
    prov = _shot().provenance
    with pytest.raises(ValueError):
        p.FixtureProvenance(
            fixture_id=prov.fixture_id, record_kind=prov.record_kind, source_record=prov.source_record,
            source_version=prov.source_version, source_member=prov.source_member,
            record_license_expression=prov.record_license_expression,
            record_license_url=prov.record_license_url, attribution=prov.attribution,
            original_sha256=prov.original_sha256, packaged_sha256=prov.packaged_sha256,
            rights_basis=prov.rights_basis, rights_review_status=p.RightsReviewStatus.APPROVED,
            redistribution_status=p.RedistributionStatus.REDISTRIBUTABLE,
            modification_notice=prov.modification_notice, transformations=prov.transformations,
        )


# ---- 9. fixture manifest ----------------------------------------------------

def _good_manifest():
    return json.loads(_fixtures._read_bytes(_fixtures._FIXTURES[FIXTURE_ID]).decode("utf-8"))


def test_manifest_validates_clean():
    _fixtures._validate_manifest(FIXTURE_ID, _good_manifest())


@pytest.mark.parametrize("mutate", [
    lambda m: m.update(fixture_id="other"),
    lambda m: m.update(record_kind="aggregate_reference_case"),
    lambda m: m.update(schema_version=2),
    lambda m: m.update(normalized_sha256="NOTAHASH"),
    lambda m: m.update(packaged_file="other.csv"),
    lambda m: m.update(columns=["time_s", "extra"]),
    lambda m: m.update(surprise=1),
    lambda m: m.pop("record_license_url"),
    lambda m: m.update(rights_review_status="bogus"),
    lambda m: m.update(rights_review_status="approved"),  # approved w/o member license
    lambda m: m.update(member_license_expression="CC-BY-4.0"),  # member set while pending
    lambda m: m["channels"][0].update(surprise=1),
    lambda m: m.update(transformations="notalist"),
])
def test_manifest_rejects_bad(mutate):
    m = _good_manifest()
    mutate(m)
    with pytest.raises(_fixtures.FixtureManifestError):
        _fixtures._validate_manifest(FIXTURE_ID, m)


def test_manifest_and_attribution_agree():
    m = _good_manifest()
    attrib = (Path(__file__).parents[1] / "puckworks" / "data" / "product" / "ATTRIBUTION.md").read_text()
    assert "10.5281/zenodo.18046315" in attrib
    assert m["record_license_expression"] in attrib
    assert m["original_sha256"] in attrib and m["normalized_sha256"] in attrib
    assert m["rights_basis_url"] in attrib  # upstream issue link


# ---- 10. build provenance ---------------------------------------------------

def test_missing_commit_raises():
    with pytest.raises(p.ProvenanceUnavailableError):
        p.build_provenance()


@pytest.mark.parametrize("bad", ["abc", "A" * 40, "a" * 39, ""])
def test_bad_commit_rejected(bad):
    with pytest.raises(ValueError):
        p.build_provenance(source_commit=bad)


def test_never_calls_git(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("no subprocess allowed")
    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "check_output", _boom)
    assert p.build_provenance(source_commit=FULL_COMMIT).source_commit == FULL_COMMIT


def test_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert p.build_provenance(source_commit=FULL_COMMIT).source_commit == FULL_COMMIT


@pytest.mark.parametrize("ts,ok", [
    ("2026-07-17T00:00:00Z", True), ("2026-07-17T00:00:00+02:00", True),
    ("2026-07-17 00:00:00", False), ("not-a-time", False),
])
def test_timestamp_validation(ts, ok):
    if ok:
        assert p.build_provenance(source_commit=FULL_COMMIT, generation_timestamp=ts)
    else:
        with pytest.raises(ValueError):
            p.build_provenance(source_commit=FULL_COMMIT, generation_timestamp=ts)


# ---- 11. serialization + golden ---------------------------------------------

def test_bundle_round_trip_byte_stable():
    j1 = p.bundle_to_json(_bundle())
    assert p.bundle_to_json(p.bundle_from_json(j1)) == j1


def test_canonical_json_sorted_nan_free():
    j = p.bundle_to_json(_bundle())
    d = json.loads(j)
    assert j.endswith("\n") and list(d) == sorted(d)
    assert "NaN" not in j and "Infinity" not in j


def test_golden_regression():
    assert p.shot_input_to_json(_shot()) == GOLDEN.read_text(encoding="utf-8")


def test_golden_byte_hash_pinned():
    got = hashlib.sha256(p.shot_input_to_json(_shot()).encode("utf-8")).hexdigest()
    assert got == GOLDEN_SHA256

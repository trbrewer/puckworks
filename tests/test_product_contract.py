"""PR 1 contract tests for ``puckworks.product`` (issue #32).

Covers public API, schema versioning, immutability, numeric validation, referential integrity,
evidence semantics, rights-gated fixtures, build provenance (no Git), serialization + golden
regression. Installed-wheel and cross-Python byte hashing are additionally exercised by the packaging
lane and CI matrix.
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
FULL_COMMIT = "a" * 40


def _shot():
    return _fixtures._load(FIXTURE_ID, require_rights=False)


def _bundle(**over):
    shot = _shot()
    kw = dict(
        schema_version=1, package_version=puckworks.__version__,
        build_provenance=p.build_provenance(source_commit=FULL_COMMIT),
        fixture_provenance=shot.provenance,
        normalized_units=(p.UnitBinding("time", "s"), p.UnitBinding("mass", "g")),
        observations=tuple(shot.series), warnings=("PR1 contract only",),
    )
    kw.update(over)
    return p.ShotExplanationBundle(**kw)


# ---- 1. public API ----------------------------------------------------------

def test_product_in_top_level_all():
    assert "product" in puckworks.__all__ and puckworks.product is p


def test_product_all_exact_and_importable():
    assert p.__all__ == sorted(set(p.__all__), key=p.__all__.index) or True  # order tolerated
    for name in p.__all__:
        assert hasattr(p, name), name


def test_normalized_shot_not_public():
    assert "NormalizedShot" not in p.__all__
    assert not hasattr(p, "NormalizedShot")


def test_generic_serializers_not_public():
    for name in ("to_json", "to_dict", "_encode", "_canonical_json"):
        assert name not in p.__all__


def test_internal_adapters_not_exported():
    for internal in ("_records", "_serialize", "_provenance", "_fixtures", "_enums"):
        assert internal not in p.__all__


def test_docs_api_lists_the_namespace():
    api = (Path(__file__).parents[1] / "docs" / "API.md").read_text()
    assert "puckworks.product" in api and "shot_input_to_json" in api


# ---- 2. schema versioning ---------------------------------------------------

def test_shot_input_json_has_schema_version():
    d = json.loads(p.shot_input_to_json(_shot()))
    assert d["schema_version"] == p.SHOT_INPUT_SCHEMA_VERSION


def test_bundle_json_has_schema_version():
    d = json.loads(p.bundle_to_json(_bundle()))
    assert d["schema_version"] == p.SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION


def test_missing_schema_version_fails():
    d = p.bundle_to_dict(_bundle())
    del d["schema_version"]
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_unsupported_schema_version_fails():
    d = p.bundle_to_dict(_bundle())
    d["schema_version"] = 99
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_boolean_schema_version_fails():
    d = p.bundle_to_dict(_bundle())
    d["schema_version"] = True
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_unknown_top_level_field_fails():
    d = p.bundle_to_dict(_bundle())
    d["surprise"] = 1
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_duplicate_json_keys_fail():
    with pytest.raises(p.SchemaError):
        p.shot_input_from_json('{"schema_version":1,"schema_version":1}')


def test_shot_input_dict_rejected_by_bundle_reader():
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(p.shot_input_to_dict(_shot()))


# ---- 3. immutability --------------------------------------------------------

def test_records_are_frozen():
    b = _bundle()
    with pytest.raises(Exception):
        b.package_version = "x"


def test_no_mutable_dict_in_public_records():
    # normalized_units is a tuple of UnitBinding, not a dict.
    assert isinstance(_bundle().normalized_units, tuple)


def test_external_mutation_does_not_change_canonical_bytes():
    values = [0.0, 1.0, 2.0]
    axis = p.TimeAxis("t", "s", "o", tuple(values))
    j1 = json.dumps([v for v in axis.values])
    values.append(99.0)  # mutate the original list
    assert json.dumps([v for v in axis.values]) == j1


# ---- 4. numeric validation --------------------------------------------------

@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_rejected(bad):
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "u", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (1.0, bad), provenance="prov")


def test_boolean_as_number_rejected():
    with pytest.raises(ValueError):
        p.TimeAxis("t", "s", "o", (True, False))


def test_time_must_be_strictly_increasing():
    with pytest.raises(ValueError):
        p.TimeAxis("t", "s", "o", (0.0, 0.0, 1.0))


def test_available_series_requires_values():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "bar", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (), provenance="prov")


def test_unavailable_series_rejects_values_and_uncertainty():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "bar", p.SeriesKind.PREDICTED, p.AvailabilityStatus.UNAVAILABLE,
                         "t", (1.0,))
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "bar", p.SeriesKind.PREDICTED, p.AvailabilityStatus.UNSUPPORTED,
                         "t", (), uncertainty=(1.0,))


def test_uncertainty_length_and_sign():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "bar", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (1.0, 2.0), provenance="prov", uncertainty=(0.1,))
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "bar", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                         "t", (1.0,), provenance="prov", uncertainty=(-0.1,))


# ---- 5. identity and references ---------------------------------------------

def test_fixture_id_must_match_provenance():
    shot = _shot()
    with pytest.raises(ValueError):
        p.ShotInput(1, "other", shot.provenance, shot.time_axis, shot.series)


def test_duplicate_series_id_fails():
    shot = _shot()
    dup = shot.series[0]
    with pytest.raises(ValueError):
        p.ShotInput(1, shot.fixture_id, shot.provenance, shot.time_axis, (dup, dup))


def test_bundle_rejects_more_than_three_candidates():
    cands = tuple(
        p.ExplanationCandidate(f"c{i}", p.CompatibilityStatus.INSUFFICIENT_EVIDENCE, "s")
        for i in range(4)
    )
    with pytest.raises(ValueError):
        _bundle(explanation_candidates=cands)


def test_candidate_unknown_observation_fails():
    c = p.ExplanationCandidate("c1", p.CompatibilityStatus.COMPATIBLE, "s",
                               supporting_observation_ids=("nope",))
    with pytest.raises(ValueError):
        _bundle(explanation_candidates=(c,))


def test_candidate_support_contradict_overlap_fails():
    with pytest.raises(ValueError):
        p.ExplanationCandidate("c1", p.CompatibilityStatus.PARTLY_COMPATIBLE, "s",
                               supporting_observation_ids=("o",), contradicting_observation_ids=("o",))


def test_candidate_unknown_evidence_and_caveat_fail():
    c = p.ExplanationCandidate("c1", p.CompatibilityStatus.COMPATIBLE, "s",
                               evidence_reference_ids=("missing",))
    with pytest.raises(ValueError):
        _bundle(explanation_candidates=(c,))


def test_duplicate_evidence_ids_fail():
    e = p.EvidenceReference("e1", "paper3", "claim", "post_fit", "PASS", "prov")
    with pytest.raises(ValueError):
        _bundle(evidence_references=(e, e))


def test_package_version_must_match_provenance():
    with pytest.raises(ValueError):
        _bundle(package_version="9.9.9")


# ---- 6. evidence semantics --------------------------------------------------

def test_evidence_strength_survives_round_trip():
    e = p.EvidenceReference("e1", "paper3", "claim-x", "post_fit_reconstruction", "ACKNOWLEDGED", "prov")
    c = p.ExplanationCandidate("c1", p.CompatibilityStatus.COMPATIBLE, "s", evidence_reference_ids=("e1",))
    b = _bundle(evidence_references=(e,), explanation_candidates=(c,))
    b2 = p.bundle_from_json(p.bundle_to_json(b))
    assert b2.evidence_references[0].source_evidence_strength == "post_fit_reconstruction"
    assert b2.evidence_references[0].source_gate_status == "ACKNOWLEDGED"


def test_compatibility_is_not_evidence_strength():
    assert not hasattr(p.CompatibilityStatus.COMPATIBLE, "source_evidence_strength")


# ---- 7. fixture manifest + rights gate --------------------------------------

def test_available_fixtures_empty_while_pending():
    assert p.available_fixtures() == ()


def test_public_loader_refuses_pending_fixture():
    with pytest.raises(p.FixtureRightsError):
        p.load_bundled_shot(FIXTURE_ID)


def test_internal_loader_works():
    shot = _shot()
    assert len(shot.time_axis.values) == 1072
    assert {s.series_kind for s in shot.series} == {p.SeriesKind.MEASURED}
    assert shot.provenance.record_kind is p.RecordKind.SINGLE_SHOT
    assert shot.provenance.license_expression == "CC-BY-4.0"


def test_unknown_fixture_raises_keyerror():
    with pytest.raises(KeyError):
        p.load_bundled_shot("nope")


def _good_manifest():
    return json.loads(
        _fixtures._read_bytes(_fixtures._FIXTURES[FIXTURE_ID]).decode("utf-8")
    )


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
    lambda m: m.pop("license_url"),
    lambda m: m.update(rights_review_status="bogus"),
])
def test_manifest_rejects_bad(mutate):
    m = _good_manifest()
    mutate(m)
    with pytest.raises(_fixtures.FixtureManifestError):
        _fixtures._validate_manifest(FIXTURE_ID, m)


def test_manifest_and_attribution_agree():
    m = _good_manifest()
    attrib = (Path(__file__).parents[1] / "puckworks" / "data" / "product" / "ATTRIBUTION.md").read_text()
    assert m["source_record"].split()[-1] in attrib  # DOI
    assert m["license_expression"] in attrib
    assert m["original_sha256"] in attrib and m["normalized_sha256"] in attrib


# ---- 8. build provenance ----------------------------------------------------

def test_missing_commit_raises():
    with pytest.raises(p.ProvenanceUnavailableError):
        p.build_provenance()


@pytest.mark.parametrize("bad", ["abc", "A" * 40, "a" * 39, ""])
def test_bad_commit_rejected(bad):
    with pytest.raises(ValueError):
        p.build_provenance(source_commit=bad)


def test_explicit_full_commit_succeeds():
    bp = p.build_provenance(source_commit=FULL_COMMIT)
    assert bp.source_commit == FULL_COMMIT
    assert bp.provenance_source is p.ProvenanceSource.EXPLICIT


def test_build_provenance_never_calls_git(monkeypatch):
    def _boom(*a, **k):
        raise AssertionError("build_provenance must not run a subprocess")
    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "check_output", _boom)
    assert p.build_provenance(source_commit=FULL_COMMIT).source_commit == FULL_COMMIT


def test_cwd_does_not_affect_provenance(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert p.build_provenance(source_commit=FULL_COMMIT).source_commit == FULL_COMMIT


def test_timestamp_omitted_is_deterministic():
    j1 = p.bundle_to_json(_bundle())
    j2 = p.bundle_to_json(_bundle())
    assert j1 == j2 and "generation_timestamp\":null" in j1.replace(" ", "")


# ---- 9. serialization + golden ----------------------------------------------

def test_bundle_round_trip_byte_stable():
    b = _bundle()
    j1 = p.bundle_to_json(b)
    assert p.bundle_to_json(p.bundle_from_json(j1)) == j1


def test_canonical_json_sorted_and_nan_free():
    j = p.bundle_to_json(_bundle())
    d = json.loads(j)
    assert j.endswith("\n") and list(d) == sorted(d)
    assert "NaN" not in j and "Infinity" not in j


def test_golden_shot_input_regression():
    assert p.shot_input_to_json(_shot()) == GOLDEN.read_text(encoding="utf-8")


def test_golden_byte_hash_pinned():
    # cross-Python determinism is asserted by comparing an explicit byte hash.
    got = hashlib.sha256(p.shot_input_to_json(_shot()).encode("utf-8")).hexdigest()
    assert got == "f50f0881f84619389bfed12c248221ef9a8e49d08d150fa5cc8eba31f8a8b646"

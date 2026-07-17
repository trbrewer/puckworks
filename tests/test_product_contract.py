"""PR 1A contract tests for ``puckworks.product`` (issue #32) — rights-independent.

Uses a deterministic **synthetic** object built in test code (no bundled runtime fixture, no upstream
data, no fixture loader). Simulated series use ``SeriesKind.SIMULATED`` and the provenance identifies
a Puckworks-generated test object. The real redistributable fixture + loader are deferred to PR 1B.

Covers public API, schema versioning (bool-safe), semantic RFC 3339 + ISO dates, the three-state
rights machine, pressure/channel semantics, self-contained bundle time axes, recursive strict
decoding, record/member license separation, build provenance (no Git), and serialization + golden.
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

GOLDEN = Path(__file__).parent / "product" / "synthetic_golden_bundle.json"
GOLDEN_SHA256 = "707b51340d29c795738bb46a89c6d65d52f01697aeb3b8d6aec705ea24ee353d"
FULL_COMMIT = "0" * 40

_EXPECTED_PUBLIC = {
    "SHOT_INPUT_SCHEMA_VERSION", "SHOT_EXPLANATION_BUNDLE_SCHEMA_VERSION", "MAX_EXPLANATION_CANDIDATES",
    "SeriesKind", "AvailabilityStatus", "CompatibilityStatus", "RecordKind", "ProvenanceSource",
    "RightsReviewStatus", "RedistributionStatus", "ChannelSemantics", "UnitBinding",
    "TransformationStep", "EvidenceReference", "BuildProvenance", "FixtureProvenance", "TimeAxis",
    "ObservedSeries", "DetectedEvent", "Caveat", "NextMeasurement", "ExplanationCandidate",
    "ShotInput", "ShotExplanationBundle", "shot_input_to_dict", "shot_input_to_json",
    "shot_input_from_dict", "shot_input_from_json", "bundle_to_dict", "bundle_to_json",
    "bundle_from_dict", "bundle_from_json", "build_provenance", "dev_build_identifier",
    "SchemaError", "ProvenanceUnavailableError",
}


# ---- synthetic (test-only) builders -----------------------------------------

def _syn_prov(review=None, redist=None, member=None, url=None, date=None, basis_url=None):
    review = review or p.RightsReviewStatus.PENDING
    redist = redist or p.RedistributionStatus.PENDING
    return p.FixtureProvenance(
        fixture_id="puckworks-synthetic-test", record_kind=p.RecordKind.SINGLE_SHOT,
        source_record="puckworks:synthetic-test-object", source_version="test",
        source_member="synthetic (no upstream data)", record_license_expression="MIT",
        record_license_url="https://opensource.org/licenses/MIT",
        attribution="Puckworks-generated synthetic test object; contains no upstream data.",
        original_sha256="0" * 64, packaged_sha256="1" * 64,
        rights_basis="synthetic test object; not a redistributable dataset",
        rights_review_status=review, redistribution_status=redist,
        modification_notice="synthetic; no source data", selection_method="synthetic (no selection)",
        scientific_caveats=("synthetic test object; not an experimental observation",),
        member_license_expression=member, member_license_url=url, rights_basis_url=basis_url,
        rights_review_date=date,
    )


def _axis():
    return p.TimeAxis("syn:time", "s", "synthetic zero", (0.0, 0.1, 0.2))


def _series(sid, quantity="pressure_estimate", unit="bar", node="synthetic-node", ref="gauge"):
    return p.ObservedSeries(sid, quantity, unit, p.SeriesKind.SIMULATED, p.AvailabilityStatus.AVAILABLE,
                            "syn:time", p.ChannelSemantics(node, ref, "synthetic; no missing values"),
                            (1.0, 2.0, 3.0), provenance="puckworks:synthetic")


def _syn_shot():
    return p.ShotInput(1, "puckworks-synthetic-test", _syn_prov(), _axis(),
                       (_series("syn:p"), _series("syn:mass", "mass", "g", None, None)))


def _syn_bundle(**over):
    axis = _axis()
    obs = (_series("syn:p"), _series("syn:mass", "mass", "g", None, None))
    kw = dict(
        schema_version=1, package_version=puckworks.__version__,
        build_provenance=p.build_provenance(source_commit=FULL_COMMIT),
        fixture_provenance=_syn_prov(),
        normalized_units=(p.UnitBinding("pressure", "bar"), p.UnitBinding("mass", "g")),
        time_axes=(axis,), observations=obs, warnings=("synthetic contract test object",),
    )
    kw.update(over)
    return p.ShotExplanationBundle(**kw)


# ---- 1. public API ----------------------------------------------------------

def test_all_unique_and_expected():
    assert isinstance(p.__all__, list)
    assert len(p.__all__) == len(set(p.__all__))
    assert set(p.__all__) == _EXPECTED_PUBLIC   # deliberate change only


def test_every_symbol_exists():
    for name in p.__all__:
        assert hasattr(p, name), name


def test_no_fixture_loader_or_placeholders_public():
    for name in ("NormalizedShot", "available_fixtures", "load_bundled_shot", "release_ready_fixtures",
                 "FixtureManifestError", "FixtureRightsError", "to_json", "to_dict"):
        assert name not in p.__all__ and not hasattr(p, name)


def test_no_fixtures_module():
    import importlib
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("puckworks.product._fixtures")


def test_docs_api_agrees():
    api = (Path(__file__).parents[1] / "docs" / "API.md").read_text()
    for token in ("puckworks.product", "shot_input_to_json", "time_axes", "measurement node"):
        assert token in api, token


# ---- 2. schema versioning ---------------------------------------------------

def test_schema_versions_present():
    assert json.loads(p.shot_input_to_json(_syn_shot()))["schema_version"] == 1
    assert json.loads(p.bundle_to_json(_syn_bundle()))["schema_version"] == 1


@pytest.mark.parametrize("bad", [True, 1.0, "1", None])
def test_direct_bool_and_nonint_schema_rejected(bad):
    shot = _syn_shot()
    with pytest.raises(ValueError):
        p.ShotInput(bad, shot.fixture_id, shot.provenance, shot.time_axis, shot.series)


@pytest.mark.parametrize("mut", [
    lambda d: d.pop("schema_version"), lambda d: d.update(schema_version=99),
    lambda d: d.update(schema_version=True), lambda d: d.update(surprise=1),
])
def test_bad_top_level_schema_reader_fails(mut):
    d = p.bundle_to_dict(_syn_bundle())
    mut(d)
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


def test_duplicate_keys_and_bad_json():
    with pytest.raises(p.SchemaError):
        p.shot_input_from_json('{"schema_version":1,"schema_version":1}')
    with pytest.raises(p.SchemaError):
        p.bundle_from_json("{not json")
    with pytest.raises(p.SchemaError):
        p.bundle_from_json(123)


# ---- 3. recursive strict decoding -------------------------------------------

def test_nested_unknown_field_path_aware():
    d = p.bundle_to_dict(_syn_bundle())
    d["observations"][0]["surprise"] = 1
    with pytest.raises(p.SchemaError, match=r"observations\[0\]"):
        p.bundle_from_dict(d)


def test_nested_wrong_container_path_aware():
    d = p.bundle_to_dict(_syn_bundle())
    d["time_axes"][0]["values"] = "notarray"
    with pytest.raises(p.SchemaError, match=r"time_axes\[0\].values"):
        p.bundle_from_dict(d)


def test_nested_bad_enum():
    d = p.bundle_to_dict(_syn_bundle())
    d["observations"][0]["series_kind"] = "bogus"
    with pytest.raises(p.SchemaError):
        p.bundle_from_dict(d)


# ---- 4. pressure & channel semantics ----------------------------------------

def test_pressure_series_requires_node_and_reference():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "line_pressure", "bar", p.SeriesKind.SIMULATED,
                         p.AvailabilityStatus.AVAILABLE, "t",
                         p.ChannelSemantics(None, None, "n/a"), (1.0,), provenance="prov")
    assert _series("s", "line_pressure", "bar", "line/pump-side", "gauge")


def test_available_series_requires_channel_semantics():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "mass", "g", p.SeriesKind.SIMULATED, p.AvailabilityStatus.AVAILABLE,
                         "t", None, (1.0,), provenance="prov")


def test_channel_semantics_round_trip():
    b2 = p.bundle_from_json(p.bundle_to_json(_syn_bundle()))
    ps = next(o for o in b2.observations if o.quantity == "pressure_estimate")
    assert ps.channel_semantics.measurement_node == "synthetic-node"
    assert ps.channel_semantics.reference == "gauge"


def test_selection_and_caveats_round_trip():
    si2 = p.shot_input_from_json(p.shot_input_to_json(_syn_shot()))
    assert si2.provenance.selection_method == "synthetic (no selection)"
    assert si2.provenance.scientific_caveats


# ---- 5. self-contained time axes --------------------------------------------

def test_bundle_carries_time_axes():
    assert '"time_axes"' in p.bundle_to_json(_syn_bundle())


def test_observation_unknown_axis_fails():
    with pytest.raises(ValueError):
        _syn_bundle(time_axes=())


def test_duplicate_axis_ids_fail():
    a = _axis()
    with pytest.raises(ValueError):
        _syn_bundle(time_axes=(a, a))


def test_axis_length_mismatch_fails():
    with pytest.raises(ValueError):
        _syn_bundle(time_axes=(p.TimeAxis("syn:time", "s", "o", (0.0, 1.0)),))


# ---- 6. numeric + immutability ----------------------------------------------

@pytest.mark.parametrize("bad", [math.nan, math.inf, -math.inf])
def test_nonfinite_rejected(bad):
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "mass", "g", p.SeriesKind.SIMULATED, p.AvailabilityStatus.AVAILABLE,
                         "t", p.ChannelSemantics(None, None, "n/a"), (1.0, bad), provenance="prov")


def test_bool_as_number_rejected():
    with pytest.raises(ValueError):
        p.TimeAxis("t", "s", "o", (True, False))


def test_records_frozen():
    with pytest.raises(Exception):
        _syn_bundle().package_version = "x"


# ---- 7. references ----------------------------------------------------------

def test_more_than_three_candidates_fails():
    cands = tuple(p.ExplanationCandidate(f"c{i}", p.CompatibilityStatus.INSUFFICIENT_EVIDENCE, "s")
                  for i in range(4))
    with pytest.raises(ValueError):
        _syn_bundle(explanation_candidates=cands)


def test_candidate_unknown_observation_fails():
    with pytest.raises(ValueError):
        _syn_bundle(explanation_candidates=(p.ExplanationCandidate(
            "c1", p.CompatibilityStatus.COMPATIBLE, "s", supporting_observation_ids=("nope",)),))


def test_duplicate_ids_fail():
    with pytest.raises(ValueError):
        p.Caveat("c", "cat", "s", affected_ids=("x", "x"))
    with pytest.raises(ValueError):
        p.ExplanationCandidate("c1", p.CompatibilityStatus.COMPATIBLE, "s", missing_evidence=("a", "a"))


def test_next_measurement_refs_resolve():
    with pytest.raises(ValueError):
        _syn_bundle(next_measurement=p.NextMeasurement("m1", "measure", "why", caveat_ids=("missing",)))
    with pytest.raises(ValueError):
        _syn_bundle(next_measurement=p.NextMeasurement("m1", "measure", "why", separates_hypotheses=("nocand",)))


# ---- 8. rights state machine (direct construction) --------------------------

def test_rights_pending_ok():
    assert not _syn_prov().is_redistributable


def test_rights_approved_ok():
    prov = _syn_prov(p.RightsReviewStatus.APPROVED, p.RedistributionStatus.REDISTRIBUTABLE,
                     member="MIT", url="https://opensource.org/licenses/MIT", date="2026-07-17",
                     basis_url="https://example/1")
    assert prov.is_redistributable


@pytest.mark.parametrize("review,redist", [
    (p.RightsReviewStatus.APPROVED, p.RedistributionStatus.PENDING),
    (p.RightsReviewStatus.PENDING, p.RedistributionStatus.REDISTRIBUTABLE),
    (p.RightsReviewStatus.PROHIBITED, p.RedistributionStatus.PENDING),
    (p.RightsReviewStatus.APPROVED, p.RedistributionStatus.PROHIBITED),
])
def test_mixed_rights_rejected(review, redist):
    with pytest.raises(ValueError):
        _syn_prov(review, redist, member="MIT", url="https://x", date="2026-07-17", basis_url="https://x/1")


def test_approved_requires_member_and_date():
    with pytest.raises(ValueError):
        _syn_prov(p.RightsReviewStatus.APPROVED, p.RedistributionStatus.REDISTRIBUTABLE,
                  date="2026-07-17", basis_url="https://x/1")


def test_pending_must_not_assert_member_license():
    with pytest.raises(ValueError):
        _syn_prov(member="MIT", url="https://x")


def test_member_pair_both_or_neither():
    with pytest.raises(ValueError):
        _syn_prov(p.RightsReviewStatus.APPROVED, p.RedistributionStatus.REDISTRIBUTABLE,
                  member="MIT", url=None, date="2026-07-17", basis_url="https://x/1")


# ---- 9. build provenance ----------------------------------------------------

def test_missing_commit_raises():
    with pytest.raises(p.ProvenanceUnavailableError):
        p.build_provenance()


@pytest.mark.parametrize("bad", ["abc", "A" * 40, "a" * 39, ""])
def test_bad_commit_rejected(bad):
    with pytest.raises(ValueError):
        p.build_provenance(source_commit=bad)


def test_never_calls_git(monkeypatch):
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError()))
    monkeypatch.setattr(subprocess, "check_output", lambda *a, **k: (_ for _ in ()).throw(AssertionError()))
    assert p.build_provenance(source_commit=FULL_COMMIT).source_commit == FULL_COMMIT


def test_cwd_independent(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert p.build_provenance(source_commit=FULL_COMMIT).source_commit == FULL_COMMIT


@pytest.mark.parametrize("ts,ok", [
    ("2026-07-17T00:00:00Z", True), ("2026-07-17T00:00:00.5+02:00", True),
    ("2026-99-99T00:00:00Z", False), ("2026-07-17T25:00:00Z", False),
    ("2026-07-17T00:00:00", False), ("2026-07-17T00:00:00+99:99", False),
])
def test_timestamp_semantic(ts, ok):
    if ok:
        assert p.build_provenance(source_commit=FULL_COMMIT, generation_timestamp=ts)
    else:
        with pytest.raises(ValueError):
            p.build_provenance(source_commit=FULL_COMMIT, generation_timestamp=ts)


# ---- 10. serialization + synthetic golden -----------------------------------

def test_bundle_round_trip_byte_stable():
    j1 = p.bundle_to_json(_syn_bundle())
    assert p.bundle_to_json(p.bundle_from_json(j1)) == j1


def test_canonical_json_sorted_nan_free():
    j = p.bundle_to_json(_syn_bundle())
    assert j.endswith("\n") and list(json.loads(j)) == sorted(json.loads(j))
    assert "NaN" not in j and "Infinity" not in j


def test_synthetic_golden_regression():
    assert p.bundle_to_json(_syn_bundle()) == GOLDEN.read_text(encoding="utf-8")


def test_golden_byte_hash_pinned():
    assert hashlib.sha256(p.bundle_to_json(_syn_bundle()).encode("utf-8")).hexdigest() == GOLDEN_SHA256


def test_golden_is_test_only_not_package_data():
    assert "tests" in str(GOLDEN)
    # no product runtime fixture data ships in the contract-only PR 1A
    prod = Path(__file__).parents[1] / "puckworks" / "data" / "product"
    if prod.exists():
        shipped = [f for f in prod.rglob("*") if f.is_file() and f.suffix in (".csv", ".json", ".md")]
        assert not shipped, shipped

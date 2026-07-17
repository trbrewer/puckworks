"""PR 1 contract tests for ``puckworks.product`` (issue #32).

Covers: public API surface, enum orthogonality, validation, canonical serialization + golden
regression, fixture provenance, and the byte-stable round trip. Installed-wheel and cross-Python
byte-stability are exercised by the packaging lane and CI matrix.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

import puckworks
from puckworks import product as p

FIXTURE_ID = "waszkiewicz2025_9bar_single_shot"
GOLDEN = Path(__file__).parent / "product" / "golden_shot_input.json"


# ---- 1. public API ----------------------------------------------------------

def test_product_in_top_level_all():
    assert "product" in puckworks.__all__
    assert puckworks.product is p


def test_product_all_is_explicit_and_importable():
    assert p.__all__
    for name in p.__all__:
        assert hasattr(p, name), name


def test_internal_adapters_not_exported():
    for internal in ("_records", "_serialize", "_provenance", "_fixtures", "_enums"):
        assert internal not in p.__all__


# ---- 2. enum orthogonality --------------------------------------------------

def test_series_kind_values():
    assert {k.value for k in p.SeriesKind} == {"measured", "derived", "fitted", "predicted", "simulated"}


def test_availability_disjoint_from_series_kind():
    assert {a.value for a in p.AvailabilityStatus} == {"available", "unavailable", "unsupported", "failed"}
    assert not ({a.value for a in p.AvailabilityStatus} & {k.value for k in p.SeriesKind})


def test_compatibility_is_separate_dimension():
    assert {c.value for c in p.CompatibilityStatus} == {
        "compatible", "partly_compatible", "contradicted", "insufficient_evidence", "outside_model_scope"
    }


def test_compatibility_does_not_carry_evidence_strength():
    # Evidence strength lives only on EvidenceReference and is a free-form source label.
    ref = p.EvidenceReference("paper3", "claim-x", "post_fit_reconstruction", "PASS", "prov")
    assert ref.source_evidence_strength == "post_fit_reconstruction"
    assert not hasattr(p.CompatibilityStatus, "source_evidence_strength")


# ---- 3. validation ----------------------------------------------------------

def _axis(n=3):
    return p.TimeAxis("t", "s", "first-sample", tuple(float(i) for i in range(n)))


def test_available_series_requires_values_and_unit():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "pressure", "", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE, "t", ())


def test_unavailable_series_cannot_carry_values():
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "pressure", "bar", p.SeriesKind.MEASURED,
                         p.AvailabilityStatus.UNAVAILABLE, "t", (1.0, 2.0))


def test_unavailable_series_is_valid_when_empty():
    s = p.ObservedSeries("s", "pressure", "bar", p.SeriesKind.PREDICTED,
                         p.AvailabilityStatus.UNSUPPORTED, "t", ())
    assert s.availability is p.AvailabilityStatus.UNSUPPORTED
    assert s.values == ()


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_nan_and_inf_rejected(bad):
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "pressure", "bar", p.SeriesKind.MEASURED,
                         p.AvailabilityStatus.AVAILABLE, "t", (1.0, bad, 3.0))


def test_malformed_digest_rejected():
    with pytest.raises(ValueError):
        p.FixtureProvenance("f", p.RecordKind.SINGLE_SHOT, "rec", "v", "m", "CC-BY", "attr",
                            "NOTAHASH", "a" * 64, "redistributable")


def test_bad_source_commit_rejected():
    with pytest.raises(ValueError):
        p.BuildProvenance("0.2.0", "explicit", source_commit="xyz")
    assert p.BuildProvenance("0.2.0", "explicit", source_commit="a" * 40).source_commit == "a" * 40


def test_time_axis_must_be_increasing():
    with pytest.raises(ValueError):
        p.TimeAxis("t", "s", "origin", (0.0, 0.0, 1.0))


def test_series_length_must_match_axis():
    axis = _axis(3)
    prov = _fixture_prov()
    series = p.ObservedSeries("x", "q", "u", p.SeriesKind.MEASURED, p.AvailabilityStatus.AVAILABLE,
                              "t", (1.0, 2.0))  # only 2 values
    with pytest.raises(ValueError):
        p.ShotInput("f", prov, axis, (series,))


def test_unsupported_schema_version_rejected():
    prov = _fixture_prov()
    with pytest.raises(ValueError):
        p.ShotExplanationBundle(2, "0.2.0", p.build_provenance(source_commit="a" * 40), prov, {})


# ---- 4. serialization -------------------------------------------------------

def _fixture_prov():
    return p.FixtureProvenance("f", p.RecordKind.SINGLE_SHOT, "rec", "v", "m", "CC-BY", "attr",
                               "a" * 64, "b" * 64, "redistributable", ("t1",))


def _minimal_bundle():
    shot = p.load_bundled_shot(FIXTURE_ID)
    return p.ShotExplanationBundle(
        schema_version=1, package_version=puckworks.__version__,
        build_provenance=p.build_provenance(source_commit="c" * 40),
        fixture_provenance=shot.provenance,
        normalized_units={"time": "s", "line_pressure": "bar", "mass": "g"},
        observations=tuple(shot.series),
        warnings=("PR1: contract only",),
    )


def test_bundle_json_round_trip_byte_stable():
    b = _minimal_bundle()
    j1 = p.to_json(b)
    j2 = p.to_json(p.bundle_from_json(j1))
    assert j1 == j2


def test_canonical_json_is_sorted_and_nan_free():
    j = p.to_json(_minimal_bundle())
    d = json.loads(j)
    assert j.endswith("\n")
    # sorted keys at top level
    assert list(d.keys()) == sorted(d.keys())
    assert "NaN" not in j and "Infinity" not in j


def test_to_json_rejects_nonfinite_via_construction():
    # Non-finite cannot enter a record, so canonical JSON can never contain NaN.
    with pytest.raises(ValueError):
        p.ObservedSeries("s", "q", "u", p.SeriesKind.DERIVED, p.AvailabilityStatus.AVAILABLE,
                         "t", (math.nan,))


def test_bundle_from_dict_rejects_bad_schema():
    d = p.to_dict(_minimal_bundle())
    d["schema_version"] = 99
    with pytest.raises(ValueError):
        p.bundle_from_dict(d)


def test_shot_input_round_trip():
    shot = p.load_bundled_shot(FIXTURE_ID)
    again = p.shot_input_from_json(p.to_json(shot))
    assert again.fixture_id == shot.fixture_id
    assert again.time_axis.values == shot.time_axis.values
    assert len(again.series) == len(shot.series)


def test_golden_shot_input_regression():
    shot = p.load_bundled_shot(FIXTURE_ID)
    assert p.to_json(shot) == GOLDEN.read_text(encoding="utf-8")


# ---- 5. fixture provenance --------------------------------------------------

def test_fixture_provenance_fields():
    shot = p.load_bundled_shot(FIXTURE_ID)
    prov = shot.provenance
    assert prov.record_kind is p.RecordKind.SINGLE_SHOT
    assert "CC-BY" in prov.license
    assert prov.attribution
    assert len(prov.original_sha256) == 64
    assert len(prov.packaged_sha256) == 64
    assert prov.original_sha256 != prov.packaged_sha256  # source != normalized
    assert "9-4.txt" in prov.source_member  # individually identified member
    assert prov.transformations


def test_fixture_series_are_measured():
    shot = p.load_bundled_shot(FIXTURE_ID)
    assert {s.series_kind for s in shot.series} == {p.SeriesKind.MEASURED}
    assert all(s.availability is p.AvailabilityStatus.AVAILABLE for s in shot.series)
    assert {s.unit for s in shot.series} == {"bar", "g"}


def test_unknown_fixture_raises():
    with pytest.raises(KeyError):
        p.load_bundled_shot("does-not-exist")


def test_manifest_digest_matches_packaged_csv():
    # The loader already verifies this; assert the packaged bytes independently too.
    import hashlib
    import importlib.resources as res
    pkg = "puckworks.data.product"
    manifest = json.loads(res.files(pkg).joinpath(f"{FIXTURE_ID}.manifest.json").read_text())
    csv_bytes = res.files(pkg).joinpath(f"{FIXTURE_ID}.csv").read_bytes()
    assert hashlib.sha256(csv_bytes).hexdigest() == manifest["normalized_sha256"]


# ---- provenance: no Git dependency ------------------------------------------

def test_build_provenance_no_git(monkeypatch):
    # build_provenance must never shell out; simulate a hostile PATH and cwd.
    import subprocess
    def _boom(*a, **k):
        raise AssertionError("build_provenance must not run a subprocess")
    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "check_output", _boom)
    bp = p.build_provenance()
    assert bp.package_version == puckworks.__version__
    assert bp.provenance_source in ("unset", "packaged_resource")

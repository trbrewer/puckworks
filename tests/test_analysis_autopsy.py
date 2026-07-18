"""PV-04 "How We Falsified Our Own Espresso Headline" — data-contract audit + traceability tests.

Offline. The first implementation slice of PV-04 (issue #62): it binds the compact public snapshot to
the authoritative producer (result1_magnitude_comparison) and to the CC-BY Schmieder source files, and
guards the corrected-analysis facts so a silent regression to the superseded interior-maximum headline
fails the suite. The static site is a later slice.
"""
import hashlib
import json
from pathlib import Path

import pytest

from puckworks.public import analysis_autopsy as AA

_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = _ROOT / "puckworks" / "public" / "data" / "pv04_analysis_autopsy.json"


@pytest.fixture(scope="module")
def snap():
    return json.loads(SNAPSHOT.read_text(encoding="utf-8"))


def test_snapshot_schema_and_labels(snap):
    for f in ("schema_version", "story_id", "title", "generator", "producer", "source_commit",
              "source_data_sha256", "dataset_manifest_ids", "attribution", "redistribution_class",
              "badge", "evidence_strength", "values", "units", "series", "revision_record", "scope",
              "caveat", "fidelity_ceiling"):
        assert f in snap, f"missing {f}"
    assert snap["story_id"] == "PV-04"
    assert snap["producer"] == "puckworks.harness.result1_magnitude_comparison"
    # evidence labels are carried UNCHANGED (not upgraded)
    assert snap["badge"] == "OBSERVED"
    assert snap["evidence_strength"] == "independent"


def test_every_value_has_a_unit_and_is_finite(snap):
    for k, v in snap["values"].items():
        assert k in snap["units"] and str(snap["units"][k]).strip(), f"{k} has no unit"
        assert AA._all_finite(v), f"{k} non-finite"


def test_deterministic_and_matches_snapshot():
    a = AA._canonical_json(AA.build_payload(source_commit="x"))
    b = AA._canonical_json(AA.build_payload(source_commit="x"))
    assert a == b
    stored = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    fresh = AA.build_payload(source_commit=stored["source_commit"])
    assert AA._canonical_json(fresh) == SNAPSHOT.read_text(encoding="utf-8"), "snapshot stale (run export)"


def test_source_data_sha_binds(snap):
    for name, path in AA._SOURCE_DATA_FILES.items():
        assert snap["source_data_sha256"][name] == AA._sha256_file(path)


def test_verify_clean_on_committed_state():
    assert AA.verify() == []


def test_values_trace_to_the_authoritative_producer(snap):
    # every public value is regenerable from result1_magnitude_comparison via _VALUE_PATHS
    from puckworks import harness
    res = harness.result1_magnitude_comparison()
    for key, path in AA._VALUE_PATHS.items():
        live = AA._dig(res, path)
        want = snap["values"][key]
        if isinstance(want, bool):
            assert bool(live) == want, f"{key}: {live} != {want}"
        else:
            assert abs(float(live) - float(want)) <= 5e-3, f"{key}: {live} != {want}"


def test_corrected_analysis_facts_hold(snap):
    v = snap["values"]
    # the corrected raw replicates are ORDERED with the middle BELOW the coarse dial (no interior max)
    assert v["ey_dial_1p7_pct"] < v["ey_dial_2p0_pct"]
    # the Welch 95% interval on the middle-vs-coarse contrast excludes zero (both ends negative)
    assert v["welch_ci95_lo_EYpt"] < 0 and v["welch_ci95_hi_EYpt"] < 0
    # the model's interior bump is smaller than the replicate spread -> capacity, not identification
    assert v["model_bump_lt_within_cell_var"] is True
    assert v["model_prominence_9bar_EYpt"] < v["within_cell_std_EYpt"]
    # the superseded headline's printed RSM coefficient is a rounding artifact of a smaller refit
    assert v["rsm_printed_is_rounding_artifact"] is True
    assert v["rsm_printed_central_g"] > v["rsm_refit_central_g"]


def test_verify_flags_a_regression_to_the_superseded_headline(tmp_path, monkeypatch, snap):
    bad = json.loads(json.dumps(snap))
    bad["values"]["ey_dial_1p7_pct"] = 99.0            # pretend the middle dial became an interior max
    snap_file = tmp_path / "pv04.json"
    snap_file.write_text(AA._canonical_json(bad), encoding="utf-8")
    monkeypatch.setattr(AA, "SNAPSHOT", snap_file)
    monkeypatch.setattr(AA, "build_payload", lambda source_commit=None: bad)
    problems = AA.verify(out_dir=tmp_path)
    assert any("no longer ordered" in p for p in problems)


def test_rights_are_cc_by_and_attributed(snap):
    assert "CC-BY" in snap["attribution"]
    assert "10.3390/foods12152871" in snap["attribution"]
    for did in snap["dataset_manifest_ids"]:
        assert did.startswith("schmieder2023/")


def test_no_humiliation_or_overclaim_in_static_summary():
    txt = (_ROOT / "docs" / "public" / "site" / "analysis-autopsy" / "static-summary.txt").read_text()
    low = txt.lower()
    # the honest framing IS present
    assert "model capacity is not parameter identification" in low
    assert "does not prove every current result" in low
    # no confidence claim beyond the actual design; no universal optimum
    assert "too-fine optimum" in low  # only ever as a NOT
    for m in low.split("."):
        if "too-fine optimum" in m:
            assert "not" in m or "does not" in m or "no " in m


def test_pv04_values_returns_snapshot_values(snap):
    assert AA.pv04_values() == snap["values"]


def test_packaging_declares_exact_pv04_snapshot():
    pj = (_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    import re
    m = re.search(r'"puckworks\.public"\s*=\s*\[([^\]]*)\]', pj)
    assert m and "data/pv04_analysis_autopsy.json" in m.group(1)
    assert "*.json" not in m.group(1)


def _sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def test_site_data_matches_snapshot():
    site = _ROOT / "docs" / "public" / "site" / "analysis-autopsy" / "data.json"
    assert _sha(site) == _sha(SNAPSHOT)

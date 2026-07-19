"""Research-radar 51-candidate adjudication fixture + precision metrics (issue #42/#46).

Offline + deterministic. Locks the FIRST real research-radar scan (workflow run 29666830887, source commit
5f300c00, artifact SHA 21a53ad1…) as a regression fixture and checks the precision metrics computed over
its recorded human adjudication: 51 retained, 0 relevant, precision@retained 0.00, every generic query
family 0.00, and the coffee-anchored families quiet. This guards against a classifier change silently
turning off-domain noise into apparent relevance. No network; the fixture is the artifact verbatim.
"""
import hashlib
import json
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_FIX = _ROOT / "tests" / "fixtures" / "research_radar"
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

SCAN = _FIX / "first_scan_2026-07-18.json"
ADJ = _FIX / "first_scan_adjudication.json"
# the SHA-256 recorded on issue #42 for candidates.json of run 29666830887 (independently reproduced here)
EXPECTED_SHA = "21a53ad19d5be3db3596eb32eb8460ff2b5bf5c0e1956313862f96522fda83f8"


@pytest.fixture(scope="module")
def scan():
    return json.loads(SCAN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def adjudication():
    return json.loads(ADJ.read_text(encoding="utf-8"))


def test_fixture_is_the_verbatim_artifact_with_the_recorded_hash(adjudication):
    # the committed scan fixture reproduces the exact SHA-256 recorded on #42 for the workflow artifact
    assert hashlib.sha256(SCAN.read_bytes()).hexdigest() == EXPECTED_SHA
    assert adjudication["provenance"]["candidates_sha256"] == EXPECTED_SHA
    assert adjudication["provenance"]["run_id"] == "29666830887"
    assert adjudication["provenance"]["source_commit"] == "5f300c00ca9464eb0db0b2f866b6db58248824d9"


def test_scan_has_exactly_51_retained_candidates(scan):
    assert scan["counts"]["retained"] == 51
    assert len(scan["candidates"]) == 51


def test_every_candidate_is_adjudicated_no_silent_gap(scan, adjudication):
    gold = adjudication["gold_labels"]
    idents = {c["identity"] for c in scan["candidates"]}
    assert set(gold) == idents                          # exactly the retained set, nothing missing/extra
    assert len(gold) == 51


def test_precision_metrics_match_the_recorded_zero_relevant_adjudication(scan, adjudication):
    import research_radar as R
    m = R.adjudication_metrics(scan["candidates"], adjudication["gold_labels"])
    assert m["retained"] == 51
    assert m["adjudicated"] == 51 and m["unlabelled"] == []
    assert m["relevant"] == 0
    assert m["precision_at_retained"] == 0.0
    assert m["by_triage_state"] == {"out-of-scope": 51}   # all off-domain per #42


def test_every_query_family_has_zero_precision_and_generic_families_dominate(scan, adjudication):
    import research_radar as R
    m = R.adjudication_metrics(scan["candidates"], adjudication["gold_labels"])
    fam = m["by_query_family"]
    assert fam, "no family breakdown"
    for name, d in fam.items():
        assert d["precision"] == 0.0, f"{name} unexpectedly relevant"
        assert d["relevant"] == 0
    # the noisy generic families are present and account for retained candidates
    assert {"identifiability", "inverse-problems", "system-identification-doe"} <= set(fam)


def test_coffee_anchored_families_are_quiet_in_this_scan(scan):
    # no coffee-anchored family retained anything (they were correctly silent); the only coffee-keyword
    # candidate is a social LCA under a generic family, not an extraction-physics paper
    families = {c["query_id"] for c in scan["candidates"]}
    assert not ({"espresso-extraction", "coffee-porous-bed", "coffee-chemistry-measurement"} & families)
    coffee_titles = [c["title"] for c in scan["candidates"]
                     if any(w in (c["title"] or "").lower() for w in ("espresso", "coffee"))]
    assert coffee_titles == ["Social life cycle assessment of primary coffee production in Brazil: "
                             "A risk-based identification of social hotspots"]


def test_adjudication_metrics_rejects_a_non_vocabulary_label(scan):
    import research_radar as R
    bad = {c["identity"]: "totally-relevant" for c in scan["candidates"]}
    with pytest.raises(ValueError):
        R.adjudication_metrics(scan["candidates"], bad)


def test_adjudication_metrics_flags_an_unlabelled_candidate_not_silently(scan, adjudication):
    import research_radar as R
    gold = dict(adjudication["gold_labels"])
    dropped = scan["candidates"][0]["identity"]
    gold.pop(dropped)
    m = R.adjudication_metrics(scan["candidates"], gold)
    assert dropped in m["unlabelled"] and m["adjudicated"] == 50   # the gap is surfaced, not hidden

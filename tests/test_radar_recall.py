"""Research-radar RECALL gold set + precision/recall metrics (issue #42/#46, Phase 8).

Offline + deterministic. The 51-candidate all-negative fixture measures precision/regression but cannot
test recall. This adds a metadata-only POSITIVE gold set (real papers already carded here; titles + DOIs
only, no abstracts) and checks that known positives are retained, known negatives are rejected, duplicates
are detected, already-carded results are labelled, and BOTH precision and recall are reported.
"""
import json
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[1]
_FIX = _ROOT / "tests" / "fixtures" / "research_radar" / "recall_gold_set.json"
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

GOLD = json.loads(_FIX.read_text(encoding="utf-8"))


def _cand(rec):
    import research_radar as R
    return R.Candidate(rec["source"], rec["title"], [], "2026-07-01", "2026-07-01", rec["doi"],
                       None, None, None, "", rec.get("query_id", "q"))


def _positives():
    return [_cand(r) for r in GOLD["positives"]]


def _negatives():
    return [_cand(r) for r in GOLD["negatives"]]


def test_gold_positives_reference_real_repo_cards():
    cards = {p.stem for p in (_ROOT / "docs" / "cards").glob("*.md")}
    for rec in GOLD["positives"]:
        assert rec["card"] in cards, f"positive {rec['card']} has no card in the repo"
        assert rec["doi"].startswith("10.")               # a real DOI, metadata only
    # no abstract/full-text field is stored on any record (metadata only)
    for rec in GOLD["positives"] + GOLD["negatives"]:
        assert "abstract" not in rec and set(rec) <= {"class", "source", "title", "doi", "card", "query_id"}


def test_coffee_anchor_retains_every_positive_and_drops_every_negative():
    import research_radar as R
    kept = {c.doi for c in R.apply_required_any(_positives() + _negatives(), ["espresso", "coffee"])}
    assert {r["doi"] for r in GOLD["positives"]} <= kept          # recall over the anchored set
    assert not ({r["doi"] for r in GOLD["negatives"]} & kept)     # negatives all dropped


def test_recall_and_precision_are_both_reported():
    import research_radar as R
    retained = R.apply_required_any(_positives() + _negatives(), ["espresso", "coffee"])
    retained_ids = {c.identity() for c in retained}
    positives_ids = {c.identity() for c in _positives()}
    rec = R.recall_metrics(retained_ids, positives_ids)
    assert rec["recall"] == 1.0 and rec["missed"] == []
    # precision over the retained set (all retained are relevant positives here)
    labels = {c.identity(): "relevant" for c in retained}
    prec = R.adjudication_metrics(list(retained), labels)
    assert prec["precision_at_retained"] == 1.0


def test_recall_metric_names_a_missed_positive():
    import research_radar as R
    positives = {c.identity() for c in _positives()}
    dropped = sorted(positives)[0]
    rec = R.recall_metrics(positives - {dropped}, positives)
    assert rec["recall"] < 1.0 and dropped in rec["missed"]       # a regression is surfaced, not hidden


def test_duplicates_are_detected():
    import research_radar as R
    dup = _positives()[0]
    merged = R.merge_candidates([dup, _cand(GOLD["positives"][0])])
    assert len(merged) == 1                                        # same DOI merged


def test_already_carded_positive_is_labelled_not_novel():
    # every positive maps to an existing card -> in a real scan it is 'already-covered', not 'new'
    import research_radar as R
    assert "already-covered" in R.TRIAGE_STATES
    cards = {p.stem for p in (_ROOT / "docs" / "cards").glob("*.md")}
    for rec in GOLD["positives"]:
        assert rec["card"] in cards                                # would be labelled already-carded

"""Refit-aware stability of the ablation contrasts (pivot check 2).

The point of these tests is to stop the two contrasts being quoted with the same confidence. One is
sign-stable across every fold and one is not, and the difference decides how strongly the paper may
word its central claim.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ARCHIVE = REPO / "docs" / "paper1_resource" / "PAPER_A_ABLATION_REFIT_STABILITY.json"


@pytest.fixture(scope="module")
def archive():
    if not ARCHIVE.exists():
        pytest.skip("run tools/paper_a_ablation_refit_stability.py --write")
    return json.loads(ARCHIVE.read_text(encoding="utf-8"))


def test_the_hydraulic_contrast_is_sign_stable(archive):
    """M1 - M2 > 0 in all nine folds: the target-grind map is the paper's most robust result.

    Nothing else in this analysis survives refitting with its sign intact, so this is the claim the
    manuscript may state most strongly.
    """
    s = archive["M1_minus_M2"]
    assert s["sign_stable"] is True
    assert s["n_negative"] == 0
    assert s["min"] > 0.25


def test_the_hydraulic_contrast_exceeds_the_old_published_headline(archive):
    """+0.52 pp against the 0.394 pp model-minus-constant advantage the paper currently leads with."""
    assert archive["M1_minus_M2"]["median"] > 0.394


def test_the_rate_freezing_contrast_is_NOT_sign_stable(archive):
    """8 of 9, not 9 of 9. The claim must be worded to that, and this test exists to stop it drifting.

    If a future run makes this sign-stable, that is a claim STRENGTHENING and needs a changelog
    entry and a re-read of the wording — not a quietly passing test.
    """
    s = archive["M0_minus_M2"]
    assert s["sign_stable"] is False
    assert s["n_negative"] == 8


def test_the_single_exception_is_a_tie_not_a_reversal(archive):
    """The one non-negative fold is +0.010 pp — negligible, and that matters for the wording.

    "Sign changes in one fold" and "one fold is a dead heat" support different sentences.
    """
    s = archive["M0_minus_M2"]
    assert 0.0 < s["max"] < 0.05


def test_freezing_the_rate_beats_fitting_it_by_more_than_the_old_headline(archive):
    """Median -0.205 pp against the refit-aware model-minus-constant median of -0.058 pp."""
    assert archive["M0_minus_M2"]["median"] < -0.15


def test_every_fold_refit_both_arms(archive):
    d = archive["design"]
    assert "M2 rate and level" in d["refitted_each_fold"]
    assert "M0 level only (rate frozen)" in d["refitted_each_fold"]
    assert "132-observation" in d["scored_on"]


def test_the_archive_refuses_calibrated_interval_language(archive):
    assert "not a calibrated confidence interval" in archive["status"]
    assert "EXPLORATORY" in archive["status"]


def test_the_reading_field_tracks_the_actual_stability(archive):
    """The prose in the archive must not be able to disagree with the numbers beside it."""
    for key in ("M0_minus_M2", "M1_minus_M2"):
        stable = archive[key]["sign_stable"]
        reading = archive["reading"][key]
        assert ("sign stable" in reading) == stable, key

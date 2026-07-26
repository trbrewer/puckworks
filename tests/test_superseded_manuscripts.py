"""Superseded manuscripts must announce themselves.

`docs/PAPER_B_DRAFT.md` is frozen: CLAIM_OWNERSHIP.md records it as superseded as a publication
unit and retained only as a technical synthesis. But the file itself opened with a live-sounding
title and a "**Reviewers:** please read ... " instruction, and a 2026-07-26 audit confirmed its
cross-pressure RC-3b values had drifted from the producers (0.525/0.519/0.530 against
0.516/0.510/0.522). A frozen document with stale numbers is only safe if nobody can mistake it for
a current one.

These tests keep the banner in place and keep the file out of the live-manuscript machinery.
"""
import json
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
SUPERSEDED = _ROOT / "docs" / "PAPER_B_DRAFT.md"
BUNDLE = _ROOT / "docs" / "figures" / "paper_b_results.json"

CURRENT = {
    "Paper 1": _ROOT / "docs" / "PAPER_A_DRAFT.md",
    "Paper 2": _ROOT / "docs" / "PAPER_B2_TEMPORAL_DRAFT.md",
    "Paper 3": _ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md",
}


def test_the_superseded_draft_declares_itself_superseded():
    text = SUPERSEDED.read_text(encoding="utf-8")
    head = text[:2000]
    assert "SUPERSEDED" in head, "the supersession banner is gone from the top of the file"
    assert "DO NOT CITE" in head
    assert "not a current manuscript" in head


def test_the_banner_comes_before_the_stale_reviewer_instruction():
    """The frozen text still says 'Reviewers: please read ...'. The banner must precede it, or a
    reader meets the solicitation first."""
    text = SUPERSEDED.read_text(encoding="utf-8")
    banner = text.index("SUPERSEDED")
    reviewers = text.find("**Reviewers:**")
    assert reviewers != -1, "the frozen reviewer instruction is gone -- re-check this guard"
    assert banner < reviewers
    assert "no longer applies" in text[:text.index("**Reviewers:**")]


def test_the_banner_points_at_every_current_manuscript():
    text = SUPERSEDED.read_text(encoding="utf-8")
    for name, path in CURRENT.items():
        assert path.name in text, f"{name} ({path.name}) is not named in the banner"
        assert path.exists(), path


def test_the_banner_states_the_known_drift_against_the_live_producers():
    """Naming the stale values is what stops someone quoting them. If the producers move, this
    fails rather than leaving the banner quietly wrong."""
    bundle = json.loads(BUNDLE.read_text(encoding="utf-8"))
    lo = bundle["loco"]
    current = (lo["heldout_mean"]["rc3b"],
               lo["shared_calibration_mean"]["rc3b"],
               bundle["cross_pressure"]["conditional_transfer_mean_full_precision"]["rc3b"])
    text = SUPERSEDED.read_text(encoding="utf-8")
    banner = text[:text.index("**Reviewers:**")]
    for value in current:
        assert ("%.3f" % value) in banner, (
            f"the banner does not state the current producer value {value:.3f}")
    for stale in ("0.525", "0.519", "0.530"):
        assert stale in banner, f"the banner no longer names the stale value {stale}"


def test_the_superseded_draft_is_not_a_numeral_audit_target():
    """It is unmaintained by design, so it must not be wired into the live claim coverage -- and
    equally must not be silently swapped in for a current manuscript."""
    from puckworks.paper3 import claim_coverage as P3
    from puckworks.paper_a import claim_coverage as P1
    from puckworks.paper_b2 import claim_coverage as P2
    targets = {P1.MANUSCRIPT.resolve(), P2.MANUSCRIPT.resolve(), P3.MANUSCRIPT.resolve()}
    assert SUPERSEDED.resolve() not in targets
    assert targets == {p.resolve() for p in CURRENT.values()}


def test_claim_ownership_still_records_the_supersession():
    """The banner and the governance record must agree; one without the other drifts."""
    text = (_ROOT / "docs" / "CLAIM_OWNERSHIP.md").read_text(encoding="utf-8")
    assert "PAPER_B_DRAFT.md" in text
    assert "superseded" in text.lower()


@pytest.mark.parametrize("name,path", list(CURRENT.items()))
def test_current_manuscripts_do_not_carry_a_supersession_banner(name, path):
    """Non-vacuity for the banner tests: the marker must distinguish, not appear everywhere."""
    assert "DO NOT CITE" not in path.read_text(encoding="utf-8")[:2000], name

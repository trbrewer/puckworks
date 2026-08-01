"""The design-separability archive (pivot plan §5), and the discipline around it.

The producer is slow (PDE solves), so these tests read its archive rather than recomputing — with
one exception: the empirical/prospective split is checked structurally, because that boundary is
what keeps a model-based design recommendation from being read as an experimental result.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ARCHIVE = REPO / "docs" / "paper1_resource" / "PAPER_A_DESIGN_SEPARABILITY.json"


@pytest.fixture(scope="module")
def archive():
    if not ARCHIVE.exists():
        pytest.skip("run tools/paper_a_design_separability.py --write")
    return json.loads(ARCHIVE.read_text(encoding="utf-8"))


def _designs(archive, name):
    return [d for g in archive["groups"] for d in g["designs"] if d["design"] == name]


# ── 1. the empirical / prospective boundary ──────────────────────────────────────────────────
def test_prospective_designs_carry_no_profile_and_say_why(archive):
    """Angeloni measured one cup per condition; there is no observation at 20 g or 60 g."""
    for d in (d for g in archive["groups"] for d in g["designs"] if not d["empirical"]):
        assert "profile" not in d, (d["design"], "a prospective design cannot have a profile")
        assert "no_profile_reason" in d


def test_the_admission_test_uses_only_empirical_designs(archive):
    """Ranking a model-based design against measured ones would be circular."""
    assert archive["admission_test"]["designs_compared_are_empirical_only"] is True


def test_no_prospective_design_is_described_as_validation(archive):
    blob = json.dumps(archive).lower()
    assert "model-based" in blob
    for d in (d for g in archive["groups"] for d in g["designs"] if not d["empirical"]):
        assert "no observation exists" in d["no_profile_reason"]


# ── 2. unresolved values must not be ranked ──────────────────────────────────────────────────
def test_unresolved_rsi_values_are_reported_not_dropped(archive):
    sc = archive["step_convergence"]
    assert sc["n_unresolved"] > 0, (
        "if everything now resolves, the primary/secondary split can be simplified — but check "
        "first, do not just delete the guard")
    for u in sc["unresolved"]:
        assert u["rsi"] <= archive["resolution_factor"] * u["max_step_change"]


def test_unresolved_designs_all_have_near_zero_separability(archive):
    """The convergence criterion is relative to the spread, so it must fail only where spread ~0.

    If a design with substantial RSI ever failed to resolve, that would be a numerical problem
    rather than a finding, and the step or the solver tolerance would need revisiting.
    """
    for u in archive["step_convergence"]["unresolved"]:
        assert u["rsi"] < 0.005, (u["group"], u["design"], u["rsi"])


def test_the_primary_admission_test_is_the_stricter_one(archive):
    """Reporting only the all-designs figure would overstate the agreement."""
    a = archive["admission_test"]
    primary = a["primary_resolved_designs_only"]
    secondary = a["secondary_all_designs"]
    assert primary["n_groups_consistent_with_expectation"] <= \
        secondary["n_groups_consistent_with_expectation"]
    assert "SCREENING tool" in a["reading"]


def test_rsi_is_admitted_only_as_a_screen(archive):
    """The honest reading: 5 of 6 groups, not 6 of 6, once noise-limited designs are excluded."""
    primary = archive["admission_test"]["primary_resolved_designs_only"]
    assert primary["median_spearman"] < 0
    assert primary["n_groups_consistent_with_expectation"] < primary["n_groups"], (
        "if every group now agrees, RSI may be promoted beyond a screen — but that is a claim "
        "change and needs a changelog entry, not a silently passing test")


# ── 3. the substantive design findings ───────────────────────────────────────────────────────
def test_whole_cup_designs_have_very_little_rate_sensitivity_diversity(archive):
    """The paper's central claim, as a number: RSI is ~1e-2 everywhere, not order unity."""
    every = [d["rsi"] for g in archive["groups"] for d in g["designs"]]
    assert max(every) < 0.05


def test_varying_pressure_creates_far_more_diversity_than_varying_temperature(archive):
    """Concrete design guidance, and it is not a small difference."""
    iso = [d["rsi"] for g in archive["groups"] for d in g["designs"]
           if d["design"].startswith("isothermal")]        # pressure varies
    iba = [d["rsi"] for g in archive["groups"] for d in g["designs"]
           if d["design"].startswith("isobaric")]          # temperature varies
    assert np.median(iso) > 10 * np.median(iba)


def test_two_well_separated_conditions_beat_the_full_nine_point_grid(archive):
    """The theory's sharpest prediction: diversity, not count, is what buys separability."""
    corners = np.median([d["rsi"] for d in _designs(archive, "corners_2")])
    full = np.median([d["rsi"] for d in _designs(archive, "full_grid_9")])
    assert corners > full


def test_a_single_condition_scores_exactly_zero(archive):
    for d in _designs(archive, "single_condition"):
        assert d["rsi"] == pytest.approx(0.0, abs=1e-9)
        assert d["n_observations"] == 1


def test_varying_the_collected_mass_endpoint_beats_the_whole_process_grid(archive):
    """Why the Schmieder brew ratios were worth understanding even after they proved reconstructed."""
    multi = np.median([d["rsi"] for d in _designs(archive, "multi_endpoint_20_40_60")])
    full = np.median([d["rsi"] for d in _designs(archive, "full_grid_9")])
    assert multi > 2.0 * full


# ── 4. scope language ────────────────────────────────────────────────────────────────────────
def test_the_archive_refuses_the_overclaims_the_plan_names(archive):
    status = archive["status"]
    assert "LOCAL" in status
    assert "not a Fisher information matrix" in status
    assert "not an uncertainty interval" in status

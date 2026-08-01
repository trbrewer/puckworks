"""The rate multiplier is not bounded above by this design (pivot check 1).

Three groups fitted a rate of exactly 6.5 — the upper edge of the published rate domain — and those
were the groups where freezing the rate transferred better. Before that could be used, the boundary
had to be explained: a grid artefact concealing a true optimum would mean the published rates were
simply wrong, and the transfer comparison would need redoing.

It is not an artefact. Widening the domain by a factor of 77 finds that the objective SATURATES in
every group: a tenfold change in the rate multiplier moves the predicted cup concentration by less
than one part in two thousand, and five of six near-optimal sets are still right-censored at the
widened cap. The rate is unidentified in the strongest available sense.

These tests pin that, because the whole "fitting an unidentified parameter degrades transfer"
argument rests on the rate genuinely being unidentified rather than merely mis-gridded.
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

ARCHIVE = REPO / "docs" / "paper1_resource" / "PAPER_A_RATE_DOMAIN_CHECK.json"


@pytest.fixture(scope="module")
def archive():
    if not ARCHIVE.exists():
        pytest.skip("run tools/paper_a_rate_domain_check.py --write")
    return json.loads(ARCHIVE.read_text(encoding="utf-8"))


def test_every_group_saturates(archive):
    """The finding. Not one group has an interior optimum that the published domain missed."""
    assert archive["verdict_counts"] == {"SATURATING_DEGENERACY": 6}


def test_a_tenfold_rate_change_barely_moves_the_prediction(archive):
    """The physical content: at the matched endpoint the cup stops responding to the kinetics.

    Across the top decade of the widened grid the predicted unit-inventory concentration changes by
    <0.1 %. That is what "the design cannot see the rate" means concretely — not a wide confidence
    interval, but a response that has gone flat.
    """
    for g in archive["groups"]:
        assert g["top_decade_prediction_relative_spread"] < 1e-3, g["group"]
        assert g["top_decade_objective_relative_spread"] < 1e-3, g["group"]


def test_the_near_optimal_set_is_still_right_censored_at_the_widened_cap(archive):
    """77x more room and the rate is STILL not bounded above in most groups."""
    censored = sum(1 for g in archive["groups"] if g["near_optimal_10pct"]["right_censored"])
    assert censored >= 5, "if this drops, the domain finally bounds the rate and the claim changes"


def test_widening_buys_almost_nothing_in_objective(archive):
    """Rates moved by more than an order of magnitude for essentially no fit improvement.

    Robusta trigonelline's optimum moves 6.5 -> 62 and Robusta 5-CQA 6.5 -> 144, each for less than
    0.1 pp of MAPE. A reported optimum that can move 20x at no cost is not an estimate.
    """
    moved = [g for g in archive["groups"] if g["rate_at_min_widened"] > 6.5]
    assert moved, "expected at least one group to relocate once the cap was lifted"
    for g in moved:
        assert g["improvement_from_widening_pp"] < 0.1, (g["group"], "moved far AND improved a lot")


def test_the_transfer_conclusion_survives_widening(archive):
    """The reason the check was run: does M0-vs-M2 change once the rates are re-found?"""
    t = archive["transfer_after_widening"]
    assert t["macro_M0_minus_M2_pp"] < 0, "freezing the rate must still transfer better"
    assert t["n_groups_M0_better"] >= 5


def test_the_transfer_gap_did_not_shrink_when_the_rates_were_freed(archive):
    """Refitting at the true (unbounded) optima does not rescue the fitted arm; it widens the gap.

    Published domain gave M0 - M2 = -0.157 pp. If freeing the rate had closed that, the effect would
    have been a capping artefact.
    """
    assert archive["transfer_after_widening"]["macro_M0_minus_M2_pp"] <= -0.15


def test_m0_is_unchanged_by_the_domain(archive):
    """M0 freezes the rate at the inherited value, so widening the search cannot touch it.

    A moved M0 would mean the two runs are not comparable.
    """
    pooled = float(np.mean([g["M0"]["pooled"] for g in archive["groups"]]))
    assert pooled == pytest.approx(8.281, abs=0.01)


def test_saturation_is_declared_with_an_explicit_tolerance(archive):
    """The verdict must be reproducible from a stated threshold, not from inspection."""
    assert archive["saturation_tolerance"] == 0.01
    for g in archive["groups"]:
        if g["verdict"] == "SATURATING_DEGENERACY":
            assert g["top_decade_objective_relative_spread"] < archive["saturation_tolerance"]

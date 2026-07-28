"""Cross-pressure heterogeneity, pressure domains and provenance graph (Paper B2 P1.1/P1.2/P1.3).

Also binds Table 3 to its producers. Every static and phi value in that table already matched the
producers exactly while all three rc3b values were stale by ~0.009 -- a one-column transcription
that survived because nothing checked it. These tests make that class of drift fail.
"""
import pathlib
import re

import numpy as np
import pytest

from puckworks import harness as h
from puckworks.analysis import waszkiewicz_cross_pressure as X

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_DRAFT = _ROOT / "docs/PAPER_B2_TEMPORAL_DRAFT.md"


@pytest.fixture(scope="module")
def het():
    return X.cross_pressure_heterogeneity()


# --- P1.1 ------------------------------------------------------------------------------------
def test_every_pressure_is_scored_and_ranked(het):
    assert het["n_pressures"] == 11
    for p, row in het["per_pressure"].items():
        assert row["best"] in row["rmse"], p
        assert sorted(row["rank"].values()) == list(range(1, len(row["rmse"]) + 1)), p
        assert row["n_shots"] > 0, p


def test_the_best_branch_is_not_constant_across_pressure(het):
    """The finding the macro mean hides. If this ever becomes True, the manuscript's localisation
    caveat is wrong and must be revisited rather than left standing."""
    assert het["best_branch_is_constant_across_pressure"] is False
    assert len(het["branch_wins"]) >= 3, het["branch_wins"]


def test_phi_wins_the_band_containing_the_primary_analysis(het):
    """The primary 9-bar result sits inside the band Phi(t) wins, which is why the paper must not
    generalise it across pressure."""
    assert het["per_pressure"][9.0]["best"] == "phi"
    neighbours = [het["per_pressure"][p]["best"] for p in (7.0, 8.0, 9.0, 11.0)]
    assert set(neighbours) == {"phi"}, neighbours
    assert het["per_pressure"][4.0]["best"] != "phi"


def test_the_averaging_scheme_changes_the_ordering(het):
    """Equal-pressure and shot-weighted means answer different questions; the paper reports both
    because they disagree below first place."""
    assert het["averaging_scheme_changes_order"] is True
    assert het["equal_pressure_order"][0] == het["shot_weighted_order"][0] == "phi"


def test_shot_counts_are_uneven_enough_for_the_weighting_to_matter(het):
    lo, hi = het["n_shots_range"]
    assert hi >= 2 * lo, (lo, hi)


# --- Table 3 bound to its producers -----------------------------------------------------------
def _table3_rows():
    text = _DRAFT.read_text(encoding="utf-8")
    block = text[text.index("**Table 3."):]
    rows = {}
    for line in block.splitlines():
        m = re.match(r"\|\s*(LOPO-EC[^|]*|Shared calibration[^|]*)\|\s*([\d.]+)\s*\|"
                     r"\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|", line)
        if m:
            rows[m.group(1).strip()] = tuple(float(m.group(i)) for i in (2, 3, 4))
        elif rows and line.strip() == "":
            break
    return rows


def test_table3_matches_its_producers():
    """All three columns, all three rows. rc3b was wrong in every row before this test existed."""
    rows = _table3_rows()
    assert len(rows) == 3, sorted(rows)
    lo = h.cross_pressure_loco()
    disc = h.cross_pressure_discrimination()
    per = disc["per_pressure"]
    off9 = [p for p in per if abs(float(p) - 9.0) > 1e-9]
    expected = {
        "LOPO-EC (equilibrium calibration withheld), all 11 pressures": lo["heldout_mean"],
        "Shared calibration, all 11 pressures": lo["shared_calibration_mean"],
        "Shared calibration, 10 off-9-bar pressures":
            {b: float(np.mean([per[p][b] for p in off9 if b in per[p]]))
             for b in ("static", "phi", "rc3b")},
    }
    for label, (s, phi, rc) in rows.items():
        want = expected[label]
        for got, key in ((s, "static"), (phi, "phi"), (rc, "rc3b")):
            assert abs(got - want[key]) < 5e-4, (label, key, got, want[key])


# --- P1.2 ------------------------------------------------------------------------------------
def test_pressure_domains_separate_the_four_quantities():
    d = X.pressure_domains()
    assert d["model_valid_pressure_range_bar"] == [1.0, 13.0]
    # recorded basket pressure is BELOW nominal at every setting -- the conflation hazard
    gaps = d["nominal_minus_recorded_bar"]
    assert all(v > 0 for v in gaps.values()), gaps
    assert d["primary_analysis_recorded_bar"] < d["primary_analysis_pressure_bar"]
    # P_c is a fitted parameter, not a rig setting, and is barely exercised
    assert d["n_pressures_at_or_above_P_c"] <= 2


def test_manuscript_states_the_recorded_pressure_gap():
    text = _DRAFT.read_text(encoding="utf-8")
    d = X.pressure_domains()
    assert "%.2f bar" % d["primary_analysis_recorded_bar"] in text
    assert "%.2f bar" % d["fitted_equilibrium_P_c_bar"] in text


# --- P1.3 ------------------------------------------------------------------------------------
def test_zero_free_parameters_does_not_imply_held_out():
    """The distinction P1.3 exists to make. Phi(t) has no coefficient fitted to the scored trace
    and is still not held out, because its sigmoid channel reuses the target."""
    g = X.provenance_graph()
    phi = g["branches"]["rung4_phi_of_t"]
    assert phi["free_params_fitted_to_scored_trace"] == 0
    assert phi["is_held_out"] is False
    assert phi["most_target_proximal_access"] == "indirect_target"


def test_only_the_null_comparator_is_held_out():
    g = X.provenance_graph()
    held = {b for b, v in g["branches"].items() if v["is_held_out"]}
    assert held == {"penalized_spline_loso"}, held


def test_every_branch_declares_its_inputs_with_known_access_levels():
    g = X.provenance_graph()
    for b, v in g["branches"].items():
        assert v["inputs"], b
        for inp in v["inputs"]:
            assert inp["access"] in g["access_levels"], (b, inp)
            assert inp["why"], (b, inp)


# ── rank-transition counting (Paper B2 fourth review 5.4) ─────────────────────────────────────
def _transitions(winners):
    """The definition under test, extracted so it can be driven on synthetic sequences."""
    return sum(a != b for a, b in zip(winners, winners[1:]))


def test_rank_changes_counts_transitions_not_distinct_winners():
    """`len(set(winners)) - 1` is not a transition count, and undercounts re-entrant sequences.

    The review's example: for `A, A, B, B, A` the winner returns to A, so there are TWO adjacent
    transitions, while `len(set) - 1` gives one. The bug survived a verification manifest because
    the manifest confirmed the reported number against a bundle that carried the same wrong
    definition -- value matching cannot catch a definition error.
    """
    reentrant = ["A", "A", "B", "B", "A"]
    assert _transitions(reentrant) == 2
    assert len(set(reentrant)) - 1 == 1, "the review's counterexample no longer distinguishes them"

    # The real pressure-ordered sequence: three transitions, three distinct winners.
    real = ["rc3b", "rc3b", "static", "static", "static", "static",
            "phi", "phi", "phi", "phi", "rc3b"]
    assert _transitions(real) == 3
    assert len(set(real)) - 1 == 2

    # Degenerate cases the expression must still handle.
    assert _transitions([]) == 0
    assert _transitions(["A"]) == 0
    assert _transitions(["A", "A", "A"]) == 0
    assert _transitions(["A", "B", "A", "B"]) == 3


def test_producer_reports_the_transition_count():
    """The shipped producer must use the transition definition, not the distinct-winner one."""
    from puckworks.analysis import waszkiewicz_cross_pressure as cp

    het = cp.cross_pressure_heterogeneity()
    winners = [het["per_pressure"][p]["best"] for p in het["pressures"]]
    assert het["n_rank_changes"] == _transitions(winners), (
        f"producer reports {het['n_rank_changes']} rank changes but its own pressure-ordered "
        f"winner sequence {winners} has {_transitions(winners)} transitions")
    assert het["n_rank_changes"] == 3
    assert het["best_branch_is_constant_across_pressure"] is False


# ── late-window constant access (Paper B2 fifth review P0.2) ──────────────────────────────────
def test_the_late_window_constant_is_recorded_as_an_in_sample_subset_fit():
    """Its calibration interval lies INSIDE the scored window, so it is not held out.

    The provenance graph recorded 0 free parameters fitted to the scored trace, `same_shot` access
    (defined as "outside the scored window") and "the scored window, but not the shot" held out.
    All three were false: `harness.kappa_t_ladder` defines the late interval as `hi - 10` to `hi`,
    and the scored window is 15-95 s, so the level is fitted on 85-95 s -- the final eighth of the
    interval it is then scored on.

    This is checked against the PRODUCER's own window arithmetic rather than a transcribed 85, so
    changing the scoring window cannot silently make the record wrong again.
    """
    from puckworks.analysis import waszkiewicz_cross_pressure as cp

    lo, hi = cp.WINDOW
    late_lo, late_hi = hi - 10.0, hi
    assert lo <= late_lo < late_hi <= hi, (
        f"the late interval [{late_lo}, {late_hi}] is no longer inside the scored window "
        f"[{lo}, {hi}]; the access classification below must be revisited")

    b = cp.provenance_graph()["branches"]["rung1b_longrun_const"]
    assert b["free_params_fitted_to_scored_trace"] == 1, (
        "the late constant fits one level on data inside the scored window")
    assert b["most_target_proximal_access"] == "direct_target", (
        f"access recorded as {b['most_target_proximal_access']!r}; a level fitted inside the "
        f"scored interval has direct access to the trace it is scored on")
    assert b["is_held_out"] is False
    assert "same_shot" not in b["access_levels_present"], (
        "`same_shot` is defined as 'outside the scored window', which this is not")


def test_the_manuscript_does_not_claim_the_late_constant_is_free_or_held_out():
    """Table 1 said '0 on scoring interval'; the access graph said 'outside the scored window'."""
    import pathlib
    import re

    text = (pathlib.Path(__file__).resolve().parents[1] / "docs"
            / "PAPER_B2_TEMPORAL_DRAFT.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    assert "0 on scoring interval" not in flat
    m = re.search(r"\| Late-window constant \|([^|]*)\|", flat)
    assert m, "Table 1's late-window row is gone"
    assert "1" in m.group(1), f"late-window row still claims no fitted parameter: {m.group(1)!r}"
    assert "85–95" in flat or "85-95" in flat, (
        "the manuscript does not state the actual calibration interval")

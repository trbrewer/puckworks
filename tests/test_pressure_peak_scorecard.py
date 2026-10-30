"""Saved-result scorecard: owner bands, source reproduction and no-fit curves."""

import json

import numpy as np
import pytest

from puckworks.analysis import pressure_peak_scorecard as S


@pytest.mark.parametrize("comparison,rmse,expected", [
    ("TIE", 1.2, "MEETS"), ("BETTER", .8, "MEETS"),
    ("UNRESOLVED", .999, "NEAR"), ("UNRESOLVED", 1., "MISSES"),
    ("UNRESOLVED", 1.01, "MISSES"), ("WORSE", 1.3, "MISSES"),
])
def test_accuracy_bands(comparison, rmse, expected):
    assert S.accuracy_grade(rmse, 1., comparison) == expected


@pytest.mark.parametrize("bounds,expected", [
    ((5, 5), "MEETS"), ((7, 8), "MEETS"), ((4, 5), "MEETS"),
    ((4, 4), "NEAR"), ((8, 8), "NEAR"), ((3.5, 3.5), "MISSES"),
    ((9, 13), "MISSES"), ((4.1, 4.9), "MISSES"),
])
def test_saved_peak_bands(bounds, expected):
    assert S.peak_grade(bounds) == expected


@pytest.mark.parametrize("bounds,expected", [
    ((-.088, -.088), "MEETS"), ((-.0403, -.03), "MEETS"),
    ((-.176, -.09), "NEAR"), ((-.04, -.020), "NEAR"),
    ((-.177, -.09), "MISSES"), ((-.04, -.019), "MISSES"),
    ((-.1, 0), "MISSES"), ((-.1, .01), "MISSES"), ((0, .1), "MISSES"),
])
def test_saved_slope_bands(bounds, expected):
    assert S.slope_grade(bounds) == expected


@pytest.mark.parametrize("matches,expected", [(None, S.NS), (0, "MISSES"),
    (2, "MISSES"), (3, "NEAR"), (4, "MEETS"), (5, "MEETS")])
def test_resolved_trend_bands(matches, expected):
    assert S.trend_grade(matches) == expected


def test_invalid_inputs_and_timing_touch():
    with pytest.raises(ValueError):
        S.accuracy_grade(1., 1., "unknown")
    with pytest.raises(ValueError):
        S.trend_grade(6)
    assert S.timing_overlap((4, 5), (5, 6)) == "YES"
    assert S.timing_overlap((4, 4.9), (5, 6)) == "NO"


def test_continuous_peak_known_quadratic():
    q = 2 - (S.GRID - 6.35)**2
    assert S.continuous_peak(S.GRID, q) == pytest.approx(6.35)
    p = np.array([4., 5., 6., 7., 8.])
    assert S.observed_quadratic_peak(p, 2 - (p-6.25)**2) == pytest.approx(6.25)
    assert S.observed_quadratic_peak(p, p) == pytest.approx(8.)
    with pytest.raises(ValueError):
        S.continuous_peak(S.GRID, q * np.nan)


def test_consistency_revised_tolerance_and_largest_deviation():
    saved = np.ones(11)
    curve = saved.copy()
    curve[0] = 1.049
    assert S.consistency(curve, saved)["curve_status"] == "CONSISTENT"
    assert S.consistency(curve, saved, interpolated=True)["curve_status"] == "INTERPOLATED_INPUTS"
    curve[2] = 1.051
    result = S.consistency(curve, saved, interpolated=True)
    assert result["curve_status"] == "INCONSISTENT"
    assert result["curve_checks_passed"] == 10
    assert result["curve_max_deviation_g_s"] == pytest.approx(.051)
    assert result["curve_max_deviation_pressure_bar"] == 3.5
    assert S.consistency(np.full(11, .019), np.zeros(11))["curve_checks_passed"] == 11
    assert S.consistency(np.full(11, .021), np.zeros(11))["curve_checks_passed"] == 0


def test_training_interpolation_excludes_held_out_and_has_explicit_edges():
    saved = {1.: 1., 2.: 99., 3.5: 3.5, 4.: 4.}
    np.testing.assert_allclose(S.interpolate_training_inputs([0., 2., 5.], 2., saved), [1., 2., 4.])


def test_replay_hierarchy_and_ramp_are_separate():
    reference = np.zeros(11)
    replay = np.full(11, .015)
    result = S.replay_check(replay, reference)
    assert result["curve_status"] == "CONSISTENT_IDEALISATION"
    assert result["check_tier"] == "PREDICTION"
    assert result["replay_checks_passed"] == 11
    replay[5] = .016
    result = S.replay_check(replay, reference)
    assert result["curve_status"] == "INCONSISTENT"
    assert result["replay_checks_passed"] == 10
    assert result["replay_max_deviation_pressure_bar"] == 6
    result = S.score_check(.0049, 0.)
    assert result["curve_status"] == "CONSISTENT_IDEALISATION_AGGREGATE"
    assert result["score_checks_passed"] == result["score_checks_total"] == 1
    assert "replay_checks_passed" not in result
    assert S.score_check(.0051, 0.)["curve_status"] == "INCONSISTENT"
    assert S.score_check(1.009, 1.)["curve_status"] == "CONSISTENT_IDEALISATION_AGGREGATE"
    result = S.score_check(np.ones(11), np.ones(11), "FOLD_SCORE")
    assert result["curve_status"] == "CONSISTENT_IDEALISATION_FOLD_SCORE"
    assert result["score_checks_total"] == 11
    effect = S.ramp_effect(np.full(11, 2.), np.ones(11))
    assert effect["ramp_effect_median_g_s"] == 1.
    assert json.loads(effect["ramp_effect_range_g_s"]) == [1., 1.]


def test_saved_csv_values_and_cohort_selection_are_reproduced():
    rows, sources, omitted = S.load_scorecard()
    assert not omitted and len(rows) == 20
    for row in rows:
        source = sources[row["stage"], row["candidate"]]
        base = sources[row["stage"], "B1"]
        rmse_key = "endpoint RMSE g/s" if "endpoint RMSE g/s" in source else "RMSE g/s"
        assert row["endpoint_rmse_g_s"] == float(source[rmse_key])
        assert row["b1_endpoint_rmse_g_s"] == float(base[rmse_key])
        assert row["saved_comparison"] == source["COMPARISON"]
        assert row["endpoint_rmse_change_percent"] == pytest.approx(100 * (float(source[rmse_key]) / float(base[rmse_key]) - 1))
        assert row["pressure_basis"] == "raw (line)"
        assert not any(k.startswith("basket_") and k.endswith("_grade") for k in row)
        if row["stage"] == "B0":
            assert row["saved_scenario"] == "raw sensitivity"
        if row["stage"] == "B0c":
            assert row["saved_fit_stage"] == "T4 REFIT"
        if row["stage"] == "B0b":
            assert row["saved_scenario"] == "T4 RAW PRIMARY"
    # The owner's revised criterion changes the leader; no old ranking survives.
    leaders = S.rank_rows(rows)
    assert [(r["stage"], r["candidate"]) for r in leaders[:2]] == [("B0c", "E1"), ("B0d", "F1")]
    assert len(leaders) == 13
    assert not any(r["candidate"] in {"B1", "D3", "E2"} for r in leaders)


def test_resolved_signs_are_from_saved_conditions_not_original_eleven_count():
    resolved, _ = S.resolved_trends()
    assert resolved == {2.: 1, 3.5: 1, 4.: 1, 5.: 1, 6.: 1}
    rows, _, _ = S.load_scorecard()
    d1 = next(r for r in rows if (r["stage"], r["candidate"]) == ("B0b", "D1"))
    assert d1["original_late_trend_agreement_ungraded"] == "7/11"
    assert d1["resolved_trend_matches"] == 4
    assert d1["trend_grade"] == "MEETS"


def test_observed_bootstrap_preserves_saved_condition_means():
    observed = S.observed_response()
    saved = S.read_rows(S.ROOT / "docs/research/PRESSURE_PEAK_STAGE_B0/DATA_CHECKS.csv")
    saved = json.loads(next(r for r in saved if r["check"] == "endpoint_pressure_scale_0")["per-pressure mean flow and interval"])
    assert sum(m["brews"] for m in observed["means"]) == 56
    for actual, expected in zip(observed["means"], saved):
        assert actual["pressure_bar"] == expected["pressure"]
        assert actual["mean_g_s"] == pytest.approx(expected["mean"], abs=1e-12)
    assert observed == S.observed_response()
    assert 4 <= observed["peak_bar"] <= 8


def test_saved_reference_curves_never_call_a_fitter(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("No mechanism fitter may run in scorecard evaluation")
    monkeypatch.setattr(S.A, "fit", forbidden)
    monkeypatch.setattr(S.B, "fit", forbidden)
    source = S.select_stage("B0d")["B1"][0]
    curves = S.saved_fold_curves("B0d", "B1", source, grid=S.NOMINAL, time_grid=[0., 100.])
    bank = json.loads(source["parameters by fold"])
    expected = []
    for p in S.NOMINAL:
        a, b, c = bank[f"HYD-LOCO-{p}"]
        expected.append(np.maximum(0, a+b*S.NOMINAL+c*S.NOMINAL**2))
    np.testing.assert_allclose(curves, expected)
    assert curves.shape == (11, 11)  # Evaluation grid only; not 121 reference replays.
    with pytest.raises(ValueError, match="observed onset"):
        S.saved_fold_curves("B0c", "E2", S.select_stage("B0c")["E2"][0])


def test_committed_scorecard_reproduces_saved_values_and_consistency_checks():
    stored = S.read_rows(S.OUTPUT / "SCORECARD.csv")
    rows, _, _ = S.load_scorecard()
    assert len(stored) == len(rows)
    for actual, expected in zip(stored, rows):
        for key in ("candidate", "stage", "endpoint_rmse_g_s", "peak_interval_bar", "slope_interval_g_s_bar", *S.GRADES):
            assert actual[key] == str(expected[key])
        if actual["curve_status"] != S.NA:
            checks = json.loads(actual["curve_consistency_by_fold"])
            assert len(checks) == 11
            assert sum(c["within_tolerance"] for c in checks) == int(actual["curve_checks_passed"])
            for check in checks:
                assert check["tolerance_g_s"] == max(.02, .05 * abs(check["saved_endpoint_mean_g_s"]))
                assert check["within_tolerance"] == (check["deviation_g_s"] <= check["tolerance_g_s"])
        if actual["check_tier"] == "PREDICTION":
            checked = S.replay_check(json.loads(actual["replay_endpoint_means_g_s"]), json.loads(actual["saved_endpoint_reference_g_s"]))
            assert actual["curve_status"] == checked["curve_status"]
            assert int(actual["replay_checks_passed"]) == checked["replay_checks_passed"]
        elif actual["check_tier"] == "AGGREGATE":
            assert actual["replay_checks_passed"] == S.NA
            assert actual["score_checks_total"] == "1"
            assert abs(float(actual["replay_endpoint_rmse_g_s"]) - float(actual["endpoint_rmse_g_s"])) <= .005
        if actual["candidate"] == "E2":
            assert actual["curve_status"] == S.NA
            assert actual["continuous_peak_median_bar"] == S.NA


def test_visible_summary_and_no_overall_candidate_verdict():
    text = (S.OUTPUT / "SUMMARY.md").read_text()
    assert "Retrospective re-score of saved fits. Raw pressure primary; basket pressure reported separately as sensitivity. No refitting." in text
    assert "Grades measure capability on retrospective data, not validation. Bands were set by the owner before results were produced." in text
    assert text.index("Owner-set criteria") < text.index("| Candidate |")
    assert "MEETS  = TIE or BETTER." in text
    assert "MEETS  = ≥4/5 matching signs." in text
    assert S.CURVE_LABEL in text
    assert "PASS" not in S.markdown_table(S.load_scorecard()[0])

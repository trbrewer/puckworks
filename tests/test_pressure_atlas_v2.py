"""WP2.10 — analytic adversarial fixtures for the time-weighted pressure atlas. Expected
time-weighted metrics are computed by hand so the engine's behaviour is asserted exactly
(not just "runs"). Builds shot dicts directly (bypasses normalization) to control the traces.
"""
import pytest

from puckworks.analysis import controller_atlas as atlas

_BAR = 1.0e5


def _shot(time, achieved_bar, goal_bar):
    return {"hydraulic": {"time__s": list(map(float, time)),
                          "pressure__Pa": [x * _BAR for x in achieved_bar],
                          "pressure_goal__Pa": [x * _BAR for x in goal_bar]}}


def test_perfect_constant_goal_tracking_is_zero_error():
    m = atlas.pressure_tracking_metrics(_shot([0, 1, 2, 3, 4], [9] * 5, [9] * 5))
    assert m["tw_mae_bar"] == pytest.approx(0.0)
    assert m["tw_rmse_bar"] == pytest.approx(0.0)
    assert m["frac_time_within_0p5bar"] == pytest.approx(1.0)
    assert m["command_shape"] == "constant"


def test_known_constant_bias_is_recovered_time_weighted():
    # achieved 0.7 bar below goal everywhere -> TW-MAE 0.7, signed bias -0.7
    m = atlas.pressure_tracking_metrics(_shot([0, 1, 2, 3], [8.3] * 4, [9.0] * 4))
    assert m["tw_mae_bar"] == pytest.approx(0.7, abs=1e-6)
    assert m["tw_signed_bias_bar"] == pytest.approx(-0.7, abs=1e-6)
    assert m["frac_time_within_0p5bar"] == pytest.approx(0.0)
    assert m["frac_time_within_1bar"] == pytest.approx(1.0)


def test_irregular_sampling_time_weights_not_sample_weights():
    # goal 9 everywhere; a +2 bar spike at t=0 lasts only 0.1 s, then 1.9 s at zero error.
    # sample-weighted MAE ~ 0.67 (1 of 3 samples off by 2); time-weighted MAE is tiny because
    # the spike occupies almost no TIME. All intervals <= gap_threshold, so nothing is dropped.
    t = [0.0, 0.1, 2.0]
    m = atlas.pressure_tracking_metrics(_shot(t, [11.0, 9.0, 9.0], [9.0, 9.0, 9.0]))
    # node weights w=[0.05, 1.0, 0.95], W=2.0; |err|=[2,0,0] -> TW-MAE = 0.05*2/2.0 = 0.05
    assert m["tw_mae_bar"] == pytest.approx(0.05, abs=1e-6)
    assert m["sample_rmse_bar"] > m["tw_rmse_bar"]        # sample-weighting over-weights the spike


def test_gap_is_not_bridged():
    # a 10 s gap (> gap_threshold 2 s) between two 2 s brewing segments: the gap interval
    # contributes NO weight, so active_time = 2 (seg1) + 2 (seg2) = 4, not 14.
    t = [0.0, 1.0, 2.0, 12.0, 13.0, 14.0]
    m = atlas.pressure_tracking_metrics(_shot(t, [9] * 6, [9] * 6))
    assert m["active_time_s"] == pytest.approx(4.0)


def test_idle_preroll_and_tail_excluded():
    # goal below 1 bar at the ends (idle pre-roll + tail) -> only the middle brewing region counts
    t = [0.0, 1.0, 2.0, 3.0, 4.0]
    m = atlas.pressure_tracking_metrics(_shot(t, [0.2, 9, 9, 9, 0.2], [0.2, 9, 9, 0.2, 0.2]))
    # only interval [1,2] has BOTH ends' goal >= 1 bar (node3 goal=0.2 is idle) -> active_time = 1.0
    assert m["active_time_s"] == pytest.approx(1.0)


def test_short_trace_excluded():
    assert atlas.pressure_tracking_metrics(_shot([0.0, 0.3], [9, 9], [9, 9])) is None


def test_lag_is_secondary_not_headline():
    # achieved lags goal by one sample; the UNSHIFTED tw_mae is the headline and is > 0,
    # while the lag-corrected diagnostic is smaller. The primary is never the lag-corrected one.
    t = list(range(8))
    goal = [3, 9, 9, 9, 9, 9, 9, 9]
    ach = [3, 3, 9, 9, 9, 9, 9, 9]                       # one-sample delay on the step
    m = atlas.pressure_tracking_metrics(_shot(t, ach, goal))
    assert m["tw_mae_bar"] > 0.0                          # headline sees the lag error
    assert m["lag_s"] is not None
    assert m["lag_corrected_tw_mae_bar"] <= m["tw_mae_bar"]


def test_spec_hash_in_output():
    from puckworks.analysis.controller_atlas import SPEC, SPEC_HASH
    assert SPEC["spec_version"] == "pressure-atlas/v1" and len(SPEC_HASH) == 16

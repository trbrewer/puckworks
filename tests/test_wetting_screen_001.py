"""Structural verification of the approved screen; no observed target fitting."""
import math

import numpy as np
import pytest
from unittest.mock import patch

from puckworks.analysis import wetting_screen_001 as W

THETA = np.array([.5, 10., 2.5, 4., 28.7])


def test_sharp_front_integral_and_half_pore_mass_are_equivalent():
    r = W.R0()
    k, pw, p = 5e-15, 5., 6.
    expected = r.phi*r.mu*r.length**2/(2*k*math.exp(-p/pw)*p*1e5)
    t = np.linspace(0, 100, 1001)
    front, actual = W.wetting_grid(t, [0, 100], [p, p], THETA, "W2", [k, pw])
    assert actual == pytest.approx(expected)
    eq = 1000*r.rho*r.area*k*math.exp(-p/pw)*p*1e5/(r.mu*r.length)
    assert eq*actual == pytest.approx(r.pore_g/2)
    assert front[-1] == 1.


def test_fold_tuple_is_outer_fold_even_for_training_brews():
    bank = {"HYD-LOCO-2.0": THETA, "HYD-LOCO-6.0": THETA*2, "DESCRIPTIVE_ALL": THETA*3}
    outer = W.freeze_tuple(bank, 2.)
    for training_condition in (1., 6., 13.):
        np.testing.assert_array_equal(outer, THETA)
    outer[0] = 999.
    np.testing.assert_array_equal(bank["HYD-LOCO-2.0"], THETA)


def test_w1_trajectory_and_zero_delay_fresh_bed():
    t = np.array([0., 2.5, 10., 100.])
    front, tb = W.wetting_grid(t, [0, 100], [9, 9], THETA, "W1", [10.])
    np.testing.assert_allclose(front, [0., .5, 1., 1.])
    assert tb == 10.
    z = W.predict([0, 100], [9, 9], THETA, "Z", dt=.1, cells=16)
    w = W.predict([0, 100], [9, 9], THETA, "W1", [0.], dt=.1, cells=16)
    for name in ("liquid_g", "beverage_g", "remaining_g", "stored_solute_g"):
        np.testing.assert_array_equal(z[name], w[name])
    assert z["stored_solute_g"][0] == 0.
    assert z["remaining_g"][0] == pytest.approx(.02*.28*1000)


def test_wetting_state_is_carried_and_total_solute_is_conserved():
    p = W.predict([0, 100], [9, 9], THETA, "W1", [10.], dt=.1, cells=32)
    j = np.flatnonzero(p["time"] == 10.)[0]
    assert p["liquid_g"][j] == 0.
    assert p["stored_solute_g"][j] > 0.
    assert p["remaining_g"][j] < p["remaining_g"][0]
    np.testing.assert_allclose(p["remaining_g"]+p["stored_solute_g"]+p["solute_g"]+p["inlet_loss_g"], 5.6, atol=1e-12)
    assert np.all(np.diff(p["remaining_g"]) <= 0.)


def test_observation_lag_shifts_both_scale_quantities_without_changing_bed():
    p = dict(time=np.arange(101.), beverage_g=np.arange(101.)**2,
             bed_flow_g_s=np.arange(101.)+1)
    before = p["bed_flow_g_s"].copy()
    b, q = W.scale_prediction(p, np.array([0., 5., 10., 100.]), 10.)
    np.testing.assert_array_equal(b, [0., 0., 0., 8100.])
    np.testing.assert_array_equal(q, [0., 0., 1., 91.])
    np.testing.assert_array_equal(p["bed_flow_g_s"], before)


def test_w2t_uses_the_same_pressure_history_and_internal_bed_as_w2():
    times, pressure = [0., 25., 100.], [2., 6., 13.]
    bed = W.predict(times, pressure, THETA, "W2", [1e-14, 5.], dt=.1, cells=16)
    diagnostic = W.predict(times, pressure, THETA, "W2T", [1e-14, 5., 12.], dt=.1, cells=16)
    for field in ("front_fraction", "liquid_g", "bed_flow_g_s", "beverage_g", "remaining_g"):
        np.testing.assert_array_equal(bed[field], diagnostic[field])
    _, observed = W.scale_prediction(diagnostic, [20., 40.], 12.)
    np.testing.assert_allclose(observed, np.interp([8., 28.], bed["time"], bed["bed_flow_g_s"]))


def test_missing_prediction_support_is_not_a_shorter_censor_bound():
    t = np.linspace(.03, 99.93, 1000)
    p = dict(time=np.array([0., 100.]), beverage_g=np.zeros(2), bed_flow_g_s=np.zeros(2))
    obs = W.observe(p, t)
    assert obs["onset_s"] is None
    assert obs["censor_bound_s"] == t[np.flatnonzero(t[-1]-t >= 2.)[-1]]
    p["time"][-1] = 90.
    with pytest.raises(ValueError, match="coverage"):
        W.observe(p, t)


def test_zero_delay_uses_empty_prewetting_baseline_not_first_positive_sample():
    t = np.arange(.07, 100., .1)
    prediction = dict(time=np.array([0., 100.]), beverage_g=np.array([0., 100.]),
                      bed_flow_g_s=np.ones(2))
    result = W.observe(prediction, t)
    assert result["onset_s"] == t[np.flatnonzero(t > .5)[0]]


def test_censored_median_is_never_the_detected_subset():
    exact, bound = W.median_with_censor([10., None, None], [98., 98., 98.])
    assert exact is None
    assert bound == 98.
    exact, bound = W.median_with_censor([10., 20., None], [98., 98., 98.])
    assert exact == 20.


def test_actual_training_objective_never_uses_inner_brew_fold_or_held_target():
    from puckworks.analysis.wetting_screen_001_run import FoldObjective
    bank = {f"HYD-LOCO-{p:.1f}": THETA*p for p in W.NOMINAL}
    sources = [dict(brew=str(p), nominal_pressure_bar=p, times_s=[0., 100.],
                    pressure_bar=[p, p], observed_onset_for_scoring_only_s=12.)
               for p in W.NOMINAL]
    contexts = {r["brew"]: np.linspace(0., 100., 1001) for r in sources}
    seen = []

    def predictor(source, theta, arm, parameters, dt, cells):
        seen.append((source["brew"], theta.copy()))
        return dict(time=np.array([0., 100.]), beverage_g=np.array([0., 100.]),
                    bed_flow_g_s=np.ones(2))

    # A poisoned held target must never enter the loss.
    sources[1]["observed_onset_for_scoring_only_s"] = float("nan")
    objective = FoldObjective(sources, bank, contexts, 2., "W2", .02, 256)
    with patch("puckworks.analysis.wetting_screen_001_run.numerical_prediction", predictor):
        assert math.isfinite(objective(np.log([1e-14, 5.])))
    assert len(seen) == 10 and "2.0" not in [name for name, _ in seen]
    for _, theta in seen:
        np.testing.assert_array_equal(theta, bank["HYD-LOCO-2.0"])


def test_paired_interval_uses_identical_brew_draws_and_cancels_equal_errors():
    from puckworks.analysis.wetting_screen_001_report import paired_samples, score_and_draws
    conditions = np.repeat(W.NOMINAL, 2)
    groups, draws = paired_samples(conditions)
    errors = np.arange(len(conditions), dtype=float)**2
    points, resampled = score_and_draws([errors, errors], groups, draws)
    assert points[0] == points[1]
    np.testing.assert_array_equal(resampled[:, 0], resampled[:, 1])
    expected = np.mean([np.sqrt(errors[group].mean()) for group in groups])
    assert points[0] == pytest.approx(expected)


def test_censored_onset_grade_cannot_claim_near_or_meets():
    from puckworks.analysis.wetting_screen_001_report import onset_grade
    assert onset_grade(3., True) == "NOT_SCORED/unresolved"
    assert onset_grade(4.53, True) == "NOT_SCORED/unresolved"
    assert onset_grade(4.53001, True) == "MISSES"
    assert onset_grade(3.51, False) == "MEETS"
    assert onset_grade(4.53, False) == "NEAR"


"""Native onset timing and the nested swelling mechanism, without source data."""

import numpy as np
import pytest

from puckworks.analysis import pressure_peak_stage_b0 as B


def test_onset_requires_both_thresholds_and_sustained_flow():
    t = np.arange(0., 30.01, .1)
    mass = np.maximum(t-10., 0.)*.5
    flow = np.where(t >= 10., .5, 0.)
    flow[(t >= 7.) & (t < 8.)] = .5  # Short noise pulse cannot establish onset.
    onset = B.sustained_onset(t, mass, flow)
    assert onset == pytest.approx(11.1)  # Start, not the confirmation at 13.1 s.
    flow[(t >= 11.5) & (t < 12.)] = 0.
    assert B.sustained_onset(t, mass, flow) == pytest.approx(12.)
    assert np.isnan(B.sustained_onset(t, mass, flow, flow_threshold=.6))


def test_onset_threshold_sensitivity_preserves_undetected_low_flow():
    t = np.arange(0., 60.01, .1)
    flow = np.where(t >= 10., .12, 0.)
    mass = np.maximum(t-10., 0.)*.12
    assert np.isfinite(B.sustained_onset(t, mass, flow))
    assert np.isnan(B.sustained_onset(t, mass, flow, .75, .15))


def test_e1_infinite_swelling_time_reduces_to_c4():
    t = np.linspace(0., 120., 241)
    p = np.array([3+.1*np.sin(t/10), 11+.2*np.cos(t/20)])
    expected = B.predict_course("C4", [1.2, 7., 60.], p, t)[0]
    actual = B.predict_swelling("E1", [1.2, 7., np.inf], p, t, np.array([25., 15.]), 60.)[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("model,compaction", [("E1", 7.), ("E2", 7.), ("E3", 210.)])
def test_swelling_jacobian_and_conductance_are_inside_mass_evolution(model, compaction):
    t = np.linspace(0., 120., 241)
    p = np.array([4+.1*np.sin(t/10), 11+.2*np.cos(t/20)])
    delay = np.array([25., 15.])
    x = np.log([1.4, compaction, 30.])
    q, jac = B.predict_swelling(model, np.exp(x), p, t, delay, 60.)
    base = "D1" if model == "E3" else "C4"
    for i in range(2):
        expected = B.predict_course(base, [1.4*np.exp(-delay[i]/30), compaction, 60.], p[i:i+1], t)[0]
        np.testing.assert_allclose(q[i], expected[0])
    for k in range(3):
        step = np.zeros(3); step[k] = 1e-5
        plus = B.predict_swelling(model, np.exp(x+step), p, t, delay, 60.)[0]
        minus = B.predict_swelling(model, np.exp(x-step), p, t, delay, 60.)[0]
        np.testing.assert_allclose(jac[:, :, k], (plus-minus)/2e-5, rtol=3e-4, atol=1e-6)


def test_predictive_onset_fit_never_uses_held_out_delay():
    from types import SimpleNamespace
    pressure = np.array([1., 1., 3., 3., 9., 9.])
    brews = SimpleNamespace(condition=pressure)
    delay = 30/pressure**.8
    train = np.array([0, 1, 2, 3])
    fitted = B.onset_power_fit(brews, pressure, delay, train, np.ones(6))
    np.testing.assert_allclose(fitted, [30., .8])
    delay[4:] = 1000.
    np.testing.assert_allclose(B.onset_power_fit(brews, pressure, delay, train, np.ones(6)), fitted)

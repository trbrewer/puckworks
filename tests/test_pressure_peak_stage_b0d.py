"""Independent limits and derivatives for timing/air research equations."""

import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from puckworks.analysis import pressure_peak_stage_b0 as B


@pytest.mark.parametrize("pstar", [2., 5., 9.])
def test_w1_minimum_is_analytic_pstar(pstar):
    parameters = [3., 12., pstar, 0.]
    result = minimize_scalar(lambda p: B.timing_predict(parameters, p),
                             bounds=(.1, 30.), method="bounded")
    assert result.x == pytest.approx(pstar, abs=1e-5)
    assert B.timing_predict(parameters, pstar*.9) > result.fun
    assert B.timing_predict(parameters, pstar*1.1) > result.fun


def test_boyle_saturation_limits_and_absolute_pressure():
    for s0 in (0., .3, 1.):
        assert B.boyle_saturation(0., s0) == pytest.approx(1-s0)
        assert B.boyle_saturation(1e12, s0) == pytest.approx(1., abs=2e-12)
        assert B.boyle_saturation(B.P_ATM, s0) == pytest.approx(1-s0/2)


@pytest.mark.parametrize("m", [2, 3, 4])
def test_f1_no_air_reduces_to_c4(m):
    t = np.linspace(0., 100., 1000)
    pressure = np.array([3+.2*np.sin(t/10), 11+.3*np.cos(t/20)])
    expected = B.predict("C4", [1.2, 7., 60.], pressure, t)
    actual = B.air_endpoint(np.array([1.2, 7., 60., 0.]), pressure, t, 0, m)[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)


def test_f2_reparameterization_preserves_d1_and_static_peak():
    t = np.linspace(0., 100., 1000)
    pressure = np.array([3+.2*np.sin(t/10), 11+.3*np.cos(t/20)])
    pstar = 210*B.D1_PEAK_RATIO
    actual = B.air_endpoint(np.array([1.2, pstar, 60., 0.]), pressure, t, 1, 3)[0]
    np.testing.assert_allclose(actual, B.predict("D1", [1.2, 210., 60.], pressure, t), rtol=1e-12)
    peak = minimize_scalar(lambda p: -p*B.locked_ratio(p, 210.),
                           bounds=(.1, 20.), method="bounded")
    assert peak.x == pytest.approx(pstar, abs=1e-5)


@pytest.mark.parametrize("kind", [0, 1])
def test_air_conductance_peak_matches_timing_minimum_and_excludes_mc(kind):
    pstar, s0, m = 6., .7, 3
    peak = B.conductance_peak(pstar, s0, m, kind)
    result = minimize_scalar(lambda p: B.timing_predict([5., 10., pstar, s0], p, kind, m),
                             bounds=(.1, 14.), method="bounded")
    assert result.x == pytest.approx(peak, abs=1e-5)
    assert peak > pstar  # Air shifts both extrema; do not compare pstar alone.


@pytest.mark.parametrize("kind", [0, 1])
def test_air_endpoint_jacobian(kind):
    t = np.linspace(0., 100., 201)
    p = np.array([3+.3*np.sin(t/10), 11+.4*np.cos(t/20)])
    x = np.array([np.log(1.3), np.log(7.), np.log(60.), .6])
    parameters = x.copy(); parameters[:3] = np.exp(parameters[:3])
    _, jac = B.air_endpoint(parameters, p, t, kind, 3)
    for j in range(4):
        h = np.zeros(4); h[j] = 1e-5
        plus, minus = x+h, x-h
        plus[:3] = np.exp(plus[:3]); minus[:3] = np.exp(minus[:3])
        expected = (B.air_endpoint(plus, p, t, kind, 3)[0]-B.air_endpoint(minus, p, t, kind, 3)[0])/2e-5
        np.testing.assert_allclose(jac[:, j], expected, rtol=2e-5, atol=1e-7)


def test_synthetic_timing_recovers_offset_and_compaction():
    p = np.linspace(1., 13., 26)
    truth = np.array([4., 12., 5.5, 0.])
    q = B.timing_predict(truth, p)
    actual = B.fit_timing(p, q, np.ones(len(p))/len(p), 0, 0, B.A.FitBudget())
    np.testing.assert_allclose(actual, truth, rtol=1e-5, atol=1e-6)


def test_held_out_pressure_cannot_change_timing_or_fixed_mc(monkeypatch):
    monkeypatch.setattr(B, "timing_specs", lambda: {"W1": (0, 0)})
    monkeypatch.setattr(B, "flow_specs", lambda: {
        "C4": (0, 0, "REFERENCE", "W1"), "T2-W1": (0, 0, "T2", "W1"),
        "F1": (0, 3, "F", "W1")})
    condition = np.repeat([2., 4., 7., 11.], 2)
    pressure = np.repeat(condition[:, None], 201, axis=1)
    t = np.linspace(0., 100., 201)
    target = B.air_endpoint(np.array([1.2, 6., 60., .5]), pressure, t)[0]
    brews = B.A.Brews([str(i) for i in range(8)], condition, pressure, target, t, {},
                      [str(p) for p in condition], 0.)
    course = B.Course(brews, t, pressure, np.zeros_like(pressure), np.ones_like(pressure, bool),
                      np.zeros_like(pressure), np.zeros(8), np.full(8, 100.))
    delay = B.timing_predict([4., 12., 5.5, 0.], condition)
    original = B.air_joint_fit(brews, course, condition, delay, np.ones(8), B.A.FitBudget())
    altered_target = target.copy(); altered_target[:2] += 1.
    altered_delay = delay.copy(); altered_delay[:2] += 20.
    changed = B.air_joint_fit(B.replace(brews, target=altered_target), course, condition,
                              altered_delay, np.ones(8), B.A.FitBudget())
    fold = "2.0"
    for group in ("timing", "flow"):
        for model in original[group]:
            np.testing.assert_array_equal(original[group][model]["by_fold"][fold],
                                          changed[group][model]["by_fold"][fold])
    assert original["flow"]["F1"]["by_fold"][fold][2] == original["flow"]["C4"]["by_fold"][fold][2]

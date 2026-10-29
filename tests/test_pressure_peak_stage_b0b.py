"""Time-course mechanism signs, state continuity, and scoring protections."""

import numpy as np
import pytest

from puckworks.analysis import pressure_peak_stage_b0 as B


@pytest.mark.parametrize("model,parameters,sign", [
    ("B1", [0., .5, -.02], 0),
    ("C4", [1., 7., 60.], 1),
    ("D1", [1.4, 210., 65.], 1),
    ("D2", [.6, .025, 1.3], -1),
    ("D3", [1.4, 210., 2., .05, .7], -1),
])
def test_mechanism_late_trend_at_constant_pressure(model, parameters, sign):
    t = np.linspace(0., 120., 241)
    p = np.full((1, len(t)), 11.)
    q = B.predict_course(model, parameters, p, t)[0][0]
    trend = B.A.slope(t[t >= 90], q[t >= 90])
    if sign == 0:
        assert abs(trend) < 1e-12
    else:
        assert trend*sign > 1e-5


def test_combined_mechanism_can_rise_when_jamming_is_absent():
    t = np.linspace(0., 120., 241)
    p = np.full((1, len(t)), 11.)
    q = B.predict_course("D3", [1.4, 210., 65., 0., .7], p, t)[0][0]
    assert B.A.slope(t[t >= 90], q[t >= 90]) > 0


@pytest.mark.parametrize("model,parameters", [
    ("B1", [0., .5, -.02]), ("C4", [1., 7., 60.]),
    ("D1", [1.4, 210., 65.]), ("D2", [.6, .025, 1.3]),
    ("D3", [1.4, 210., 65., .025, .7]),
])
def test_course_preserves_b0_endpoint_and_has_correct_jacobian(model, parameters):
    t = np.linspace(0., 100., 201)
    p = np.array([4+.5*np.sin(t/20), 9+.4*np.cos(t/30)])
    q, jac = B.predict_course(model, parameters, p, t)
    np.testing.assert_allclose(q[:, -1], B.predict(model, parameters, p, t), atol=6e-6)
    x = np.array(parameters) if model == "B1" else np.log(parameters)
    for k in range(len(x)):
        h = np.zeros(len(x)); h[k] = 1e-5
        plus = x+h if model == "B1" else np.exp(x+h)
        minus = x-h if model == "B1" else np.exp(x-h)
        finite = (B.predict_course(model, plus, p, t)[0]-B.predict_course(model, minus, p, t)[0])/2e-5
        np.testing.assert_allclose(jac[:, :, k], finite, rtol=2e-4, atol=1e-6)


def test_terminal_jump_is_removed_before_smoothing():
    t = np.arange(0., 121., .1)
    p, m = np.full(len(t), 9.), 2*t
    p[t >= 115] = 0.
    m[t >= 115] -= 100.
    clean_t, _, q, trend = B.clean_course(t, p, m)
    assert clean_t[-1] < 115
    np.testing.assert_allclose(q, 2., atol=1e-10)
    assert abs(trend) < 1e-12


def test_fast_jamming_does_not_numerically_overshoot_threshold():
    from scipy.integrate import solve_ivp
    t = np.linspace(0., 120., 241)
    p = np.full((1, len(t)), 13.)
    a, beta, critical = .33, 4., 1.8
    q = B.predict_course("D2", [a, beta, critical], p, t)[0][0]
    solved = solve_ivp(lambda s, z: [beta*max(a*13/(1+z[0])-critical, 0.)],
                       (0., 120.), [0.], t_eval=t, rtol=1e-10, atol=1e-12, max_step=.05)
    reference = a*13/(1+solved.y[0])
    np.testing.assert_allclose(q, reference, atol=2e-5)
    assert np.min(q) >= critical-1e-9


def test_fast_combined_evolution_matches_independent_adaptive_reference():
    from scipy.integrate import solve_ivp
    t = np.linspace(0., 120., 241)
    p = np.full((1, len(t)), 13.)
    parameters = [1.4, 210., 2., 4., .7]
    mobility = parameters[0]*B.locked_ratio(13., parameters[1])

    def ode(s, state):
        mass, jam = state
        flow = mobility*13/(np.exp(np.exp(-mass/parameters[2]))+jam)
        return [flow, parameters[3]*max(flow-parameters[4], 0.)]

    solved = solve_ivp(ode, (0., 120.), [0., 0.], t_eval=t,
                       rtol=1e-10, atol=1e-12, max_step=.05)
    reference = np.array([ode(s, state)[0] for s, state in zip(t, solved.y.T)])
    q = B.predict_course("D3", parameters, p, t)[0][0]
    np.testing.assert_allclose(q, reference, atol=2e-5)


def test_b0b_criteria_use_entire_slope_interval_and_peak_overlap():
    valid = {"slope": [-.15, -.03], "peak": [7., 9.]}
    assert B.b0b_pass("D1", "TIE", valid, 8)
    assert not B.b0b_pass("D1", "TIE", {**valid, "slope": [-.2, -.03]}, 8)
    assert not B.b0b_pass("D1", "TIE", {**valid, "slope": [-.15, -.01]}, 8)
    assert not B.b0b_pass("D1", "TIE", {**valid, "peak": [8., 9.]}, 8)
    assert not B.b0b_pass("D1", "TIE", valid, 7)
    assert not B.b0b_pass("D3", "BETTER", valid, 11)
    assert not B.b0b_pass("D1", "BETTER", valid, 11, primary=False)

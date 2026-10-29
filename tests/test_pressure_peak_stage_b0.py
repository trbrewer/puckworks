"""Independent synthetic ODE recovery and limiting cases for the B0 screen."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from puckworks.analysis import pressure_peak_stage_b0 as B


@pytest.mark.slow
@pytest.mark.parametrize("model,truth", [
    ("D1", [1.4, 210., 65.]),
    ("D2", [.6, .025, 1.3]),
    ("D3", [1.4, 210., 65., .025, .7]),
])
def test_synthetic_recovery(model, truth):
    t = np.linspace(0, 100, 501)
    starting = np.linspace(1, 13, 22)
    ending = .8+11*(.5+.5*np.sin(np.arange(len(starting))*1.7))
    histories = np.array([np.interp(t, [0, 25, 55, 100], [p0, p0, p1, p1])
                          for p0, p1 in zip(starting, ending)])
    observed = []
    for pressure in histories:
        phi = max(.122-(1-.122)*pressure[0]/truth[1], 0) if model != "D2" else .122
        mobility = truth[0]*(phi/.122)**3*((1-.122)/(1-phi))**2

        def ode(s, state):
            mass, jam = state
            factor = np.exp(np.exp(-mass/truth[2])) if model != "D2" else 1.
            q = mobility*np.interp(s, t, pressure)/(factor+jam)
            beta, threshold = truth[-2:] if model != "D1" else (0., 0.)
            return [q, beta*max(q-threshold, 0.)]

        solved = solve_ivp(ode, (0, 100), [0., 0.], rtol=1e-10, atol=1e-11, max_step=.2)
        observed.append(ode(100, solved.y[:, -1])[0])
    recovered = B.fit(model, histories, t, np.array(observed),
                      np.ones(len(histories))/len(histories), B.A.FitBudget())
    np.testing.assert_allclose(recovered, truth, rtol=3e-3, atol=2e-5)
    np.testing.assert_allclose(B.predict(model, recovered, histories, t), observed, atol=2e-5)


def test_infinite_dry_modulus_reduces_to_darcy_after_transient():
    pressure = np.repeat(np.linspace(.5, 14, 20)[:, None], 2, axis=1)
    np.testing.assert_array_equal(B.locked_ratio(pressure, np.inf), np.ones_like(pressure))
    actual = B.predict("D1", [1.2, np.inf, .01], pressure, np.array([0., 100.]))
    np.testing.assert_allclose(actual, 1.2*pressure[:, -1], atol=1e-12)
    # Y alone cannot remove the separately requested finite-time W-H2 factor.
    early = B.predict("D1", [1.2, np.inf, 60.], pressure, np.array([0., .01]))
    assert np.all(early < 1.2*pressure[:, -1])


def test_d3_zero_jamming_reduces_to_d1():
    t = np.linspace(0, 100, 1001)
    p = np.array([5+2*np.sin(t/20), 8+.5*np.cos(t/30)])
    expected = B.predict("D1", [1.3, 220., 65.], p, t)
    actual = B.predict("D3", [1.3, 220., 65., 0., 1.], p, t)
    np.testing.assert_allclose(actual, expected, atol=1e-6)


@pytest.mark.parametrize("model,parameters", [("D2", [.6, .025, 1.3]),
                                              ("D3", [1.4, 210., 65., .025, .7])])
def test_forward_sensitivities_against_finite_difference(model, parameters):
    t = np.linspace(0, 100, 201)
    p = np.array([4+.5*np.sin(t/20), 9+.4*np.cos(t/30)])
    x = np.log(parameters)
    _, jac = B.dynamic_with_gradient(p, t, np.exp(x), model == "D3")
    for k in range(len(x)):
        step = np.zeros(len(x)); step[k] = 1e-5
        finite = (B.predict(model, np.exp(x+step), p, t)-
                  B.predict(model, np.exp(x-step), p, t))/(2e-5)
        np.testing.assert_allclose(jac[:, k], finite, rtol=1e-4, atol=1e-7)


def test_refit_pass_rules_and_exploratory_exclusion():
    response, refit = {"peak": 6.}, {"slope": [-.1, -.01], "peak": [5., 8.]}
    assert B.passes("D1", response, refit, "TIE")
    assert not B.passes("D3", response, refit, "BETTER")
    assert not B.passes("D1", {"peak": 8.}, refit, "TIE")
    assert not B.passes("D1", response, {"slope": [-.1, .01], "peak": [5., 6.]}, "TIE")


@pytest.mark.slow
def test_parallel_refit_bootstrap_is_seed_identical():
    condition = np.repeat(np.arange(1., 12.), 3)
    pressure = np.repeat(condition[:, None], 2, axis=1)
    target = .6*condition-.025*condition**2+np.tile([-.05, 0., .05], 11)
    brews = B.A.Brews([str(i) for i in range(33)], condition, pressure, target,
                      np.array([0., 100.]), {}, [str(p) for p in condition], 0.)
    single = B.refit_bootstrap("B1", brews, 6, B.A.FitBudget(), workers=1)
    parallel = B.refit_bootstrap("B1", brews, 6, B.A.FitBudget(), workers=2)
    assert parallel == single

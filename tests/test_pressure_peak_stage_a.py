"""Synthetic recovery and mathematical controls; no private/source fitting."""

import numpy as np
import pytest
from scipy.integrate import solve_ivp

from puckworks.analysis import pressure_peak_stage_a as stage


@pytest.mark.parametrize("model,truth", [
    ("B1", [.05, .6, -.03]),
    ("W-H0A", [.7, .8]),
    ("C1-exp", [1.1, 6.0]),
    ("C1-power", [1.1, 1/8, 2.7/8]),
    ("C2-m1", [2.2, .025]),
    ("C2-m2", [2.2, .025]),
    ("C3", [1.1, 6.0, 40.0]),
    ("C4", [1.1, 6.0, 60.0]),
])
def test_synthetic_parameter_recovery(model, truth):
    """ODE candidates recover parameters from independent solve_ivp targets."""
    t = np.linspace(0, 100, 201)
    p = np.linspace(.8, 14, 14)
    pressure = np.repeat(p[:, None], len(t), axis=1)
    if model == "C3":
        # Different falling-pressure histories identify memory separately from
        # the two steady-law parameters; monotonically falling P needs no clamp.
        initial = p + 2 + 4*np.sin(np.arange(len(p)))**2
        pressure = p[:, None] + (initial-p)[:, None]*np.maximum(1-t/40, 0)
        sol = solve_ivp(lambda s, state: (
            np.array([np.interp(s, t, row) for row in pressure])-state)/truth[2],
            (0, 100), initial, rtol=1e-10, atol=1e-11, max_step=.5)
        target = truth[0]*p*np.exp(-sol.y[:, -1]/truth[1])
    elif model.startswith("C2"):
        m = int(model[-1])
        sol = solve_ivp(lambda s, r: truth[1]*(p/r)**m*truth[0],
                        (0, 100), np.full(len(p), truth[0]), rtol=1e-11, atol=1e-12)
        target = p/sol.y[:, -1]
    elif model == "C4":
        base = truth[0]*p*np.exp(-p/truth[1])
        sol = solve_ivp(lambda s, mass: base*np.exp(-np.exp(-mass/truth[2])),
                        (0, 100), np.zeros(len(p)), rtol=1e-11, atol=1e-12)
        target = base*np.exp(-np.exp(-sol.y[:, -1]/truth[2]))
    elif model == "C1-exp":
        target = truth[0]*p*np.exp(-p/truth[1])
    elif model == "C1-power":
        target = truth[0]*p/(1+p*truth[1])**(truth[2]/truth[1])
    elif model == "B1":
        target = np.maximum(0, truth[0]+truth[1]*p+truth[2]*p*p)
    else:
        # Solve the pressure balance independently, including machine loss.
        a, b, c = stage.MACHINE
        resistance = np.exp(truth[0])*p**truth[1]
        target = (np.sqrt((b+resistance)**2+4*a*(p-c))-b-resistance)/(2*a)
    estimated = stage.fit(model, pressure, t, target, np.ones(len(p))/len(p))
    np.testing.assert_allclose(estimated, truth, rtol=2e-4, atol=1e-6)
    np.testing.assert_allclose(stage.predict(model, estimated, pressure, t), target, atol=2e-6)


def test_local_quasistatic_compaction_cannot_peak():
    pressure = np.linspace(0, 20, 1001)
    flow = stage.local_compaction_flow(pressure)
    assert np.all(np.diff(flow) > 0)
    np.testing.assert_allclose(np.gradient(flow, pressure)[1:-1],
                               np.exp(-pressure[1:-1]/3), rtol=1e-5)
    # Discrete integration of arbitrary positive, strongly decreasing k is
    # monotone too; the conclusion is not specific to exponential permeability.
    for permeability in (np.exp(-pressure**2), (1+pressure)**-8):
        integral = np.cumsum((permeability[1:]+permeability[:-1])/2*np.diff(pressure))
        assert np.all(np.diff(integral) >= 0)


def test_power_law_exponential_limit_has_no_artificial_pressure_ceiling():
    p = np.repeat(np.linspace(.5, 15, 30)[:, None], 2, axis=1)
    t = np.array([0., 100.])
    expected = stage.predict("C1-exp", [1., 6.], p, t)
    np.testing.assert_allclose(stage.predict("C1-power", [1., 0., 1/6], p, t), expected)
    recovered = stage.fit("C1-power", p, t, expected, np.ones(len(p))/len(p))
    assert recovered[1] < 1e-5
    np.testing.assert_allclose(stage.predict("C1-power", recovered, p, t), expected, atol=1e-5)


@pytest.mark.parametrize("model", ["C2-m1", "C2-m2"])
def test_clogging_is_monotone_at_common_age_and_does_not_reset(model):
    p = np.linspace(1, 14, 60)
    history = np.repeat(p[:, None], 2, axis=1)
    early = stage.predict(model, [2, .02], history, np.array([0, 75]))
    late = stage.predict(model, [2, .02], history, np.array([0, 100]))
    assert np.all(np.diff(early) > 0)
    assert np.all(late < early)


def test_memory_recompacts_on_restart_at_same_pressure():
    pressure = np.array([[8., 8., 0., 0., 8.]])
    state = stage.relaxation_state(pressure, np.array([0., 75., 75.1, 85., 85.1]), 20.)
    assert state[0] == pytest.approx(8.)


@pytest.mark.parametrize("model", ["C2-m1", "C2-m2", "C4"])
def test_time_resolved_history_against_independent_ode(model):
    t = np.linspace(0, 100, 1001)
    p = 5+2*np.sin(t/17)
    if model.startswith("C2"):
        parameters = [2.2, .025]
        m = int(model[-1])
        sol = solve_ivp(lambda s, r: .025*(np.interp(s, t, p)/r)**m*2.2,
                        (0, 100), [2.2], rtol=1e-10, atol=1e-11, max_step=.05)
        expected = p[-1]/sol.y[0, -1]
    else:
        parameters = [1.1, 6., 60.]

        def derivative(s, mass):
            current = np.interp(s, t, p)
            return 1.1*current*np.exp(-current/6-np.exp(-mass/60))

        sol = solve_ivp(derivative, (0, 100), [0.], rtol=1e-10, atol=1e-11, max_step=.05)
        expected = derivative(100, sol.y[0, -1])
    actual = stage.predict(model, parameters, p[None, :], t)[0]
    assert actual == pytest.approx(expected, abs=2e-6)


def test_verdict_precedence_and_budget():
    assert stage.comparison([-.1, -.01]) == "BETTER"
    assert stage.comparison([.01, .1]) == "WORSE"
    assert stage.comparison([-.1, .1]) == "TIE"
    assert stage.comparison([-.3, .1]) == "UNRESOLVED"
    assert stage.capability([.1, .2], -.01) == "CAPABLE"
    assert stage.capability([.2, .3], -.01) == "UNRESOLVED"
    assert stage.capability([.1, .2], .01) == "NOT CAPABLE"
    with pytest.raises(TimeoutError):
        stage.fit("C1-exp", np.ones((3, 2)), np.array([0., 100.]), np.ones(3),
                  np.ones(3)/3, stage.FitBudget(limit=-1))

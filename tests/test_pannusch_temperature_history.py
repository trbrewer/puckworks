"""Small-mesh, external-data-free verification; no qualification sweep in CI."""
from dataclasses import FrozenInstanceError, replace
import json
from unittest.mock import patch

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.models.pannusch2024 import closures as pc
from puckworks.models.pannusch2024 import solver as ps
from puckworks.models.pannusch2024 import temperature_history as th
from tools.pannusch_temperature_history_reference import physical_operator, reference_initial

S = th.TemperatureHistorySettings(nz=7, max_step_s=.03, diagnostic_step_s=.02)


def run(history=None, **kwargs):
    args = dict(flow_m3_s=2e-6, t_span_s=(0., 2.), solute="caffeine", grind=1.7,
                observation_times_s=(0., .5, 1., 1.5, 2.), fraction_bounds_s=(0., 1., 2.), settings=S)
    args.update(kwargs)
    h = history or th.TemperatureHistory.linear_celsius((0., 2.), (88., 93.))
    return th.simulate_temperature_history(h, **args)


def reduced(tr):
    return np.column_stack((tr.liquid_kg_m3[:, 1:], tr.fine_kg_m3,
                            tr.coarse_kg_m3, tr.outlet_solute_kg))


@pytest.mark.parametrize("solute", th.SPECIES)
@pytest.mark.parametrize("T", [353.15, 361.15, 371.15])
def test_equations_jacobian_and_local_inventory(solute, T):
    n, Q = 7, 2e-6
    sys = th._PhysicalSystem(solute, 1.7, Q, n)
    y = np.random.default_rng(923).normal(size=3*n)
    independent = physical_operator(T, Q, solute, 1.7, n)
    np.testing.assert_allclose(sys.physical_rhs(T, y), independent@y, rtol=2e-14, atol=1e-13)
    jac = sys.physical_jacobian(T).toarray()
    np.testing.assert_allclose(jac, independent.toarray(), rtol=2e-14, atol=1e-13)
    eps = 1e-5
    finite = np.column_stack([(sys.physical_rhs(T, y+eps*e)-sys.physical_rhs(T, y-eps*e))/(2*eps)
                              for e in np.eye(3*n)])
    np.testing.assert_allclose(jac, finite, rtol=2e-7, atol=2e-9)
    assert jac[0, 2] != 0 and jac[0, 3] != 0 and jac[1, 3] != 0
    assert jac[n-2, n-6] != 0 and jac[-1, n-2] == Q
    K, f1, f2, m1, m2 = sys.coefficients(T)
    e1, e2 = K*y[n-1:2*n-1]-np.r_[0., y[:n-1]], K*y[2*n-1:-1]-np.r_[0., y[:n-1]]
    exchange = ps.ALPHA_L*(m1*e1+m2*e2)-sys.as1*f1*e1-ps.PHI_V2*sys.as2*f2*e2
    np.testing.assert_allclose(exchange, 0, atol=3e-15)


def test_time_dependent_coefficients_source_d32_and_no_mutation():
    before = json.dumps([ps.GRINDS, ps._solute_params()], sort_keys=True)
    system = th._PhysicalSystem("caffeine", 1.7, 2e-6, 7)
    assert system.d32 != pc.D32
    assert system.coefficients(353.15) != system.coefficients(371.15)
    r = run()
    assert r.status == "COMPLETE"
    assert before == json.dumps([ps.GRINDS, ps._solute_params()], sort_keys=True)
    assert ps.NZ == 200
    assert np.all(r.observations.liquid_kg_m3[:, 0] == 0)
    np.testing.assert_array_equal(r.observations.hydraulic_volume_m3, 2e-6*r.observations.times_s)
    with pytest.raises(FrozenInstanceError):
        r.solute = "tds"
    with pytest.raises(ValueError):
        r.observations.fine_kg_m3.setflags(write=True)
    with pytest.raises(FrozenInstanceError):
        r.history.kind = "constant"


def check_step_reference(r):
    y = reference_initial(361.15, "caffeine", 7)
    y = expm(physical_operator(361.15, 2e-6, "caffeine", 1.7, 7).toarray())@y
    y = expm(physical_operator(371.15, 2e-6, "caffeine", 1.7, 7).toarray())@y
    np.testing.assert_allclose(reduced(r.observations)[-1], y, rtol=1e-7, atol=1e-9)


def test_steps_one_sided_endpoints_and_carried_physical_state():
    h = th.TemperatureHistory.constant_celsius((0., 1., 2.), (88., 98.))
    assert h.value_K(1.) == 371.15 and h.value_K(2.) == 371.15
    assert h.integration_segments(0, 2)[0].value_K(1.) == 361.15
    assert h.integration_segments(0, 2)[1].value_K(1.) == 371.15
    r = run(h)
    check_step_reference(r)
    assert r.segments[0].end_state_sha256 == r.segments[1].start_state_sha256
    assert list(r.observations.times_s).count(1.) == 1
    assert r.observations.temperature_K[2] == 371.15
    knot = expm(physical_operator(361.15, 2e-6, "caffeine", 1.7, 7).toarray())@reference_initial(
        361.15, "caffeine", 7)
    np.testing.assert_allclose(reduced(r.observations)[2], knot, rtol=1e-7, atol=1e-9)


def test_frozen_temperature_mutant_is_detected():
    h = th.TemperatureHistory.constant_celsius((0., 1., 2.), (88., 98.))
    original = th._PhysicalSystem.coefficients
    with patch.object(th._PhysicalSystem, "coefficients", lambda self, T: original(self, 361.15)):
        mutant = run(h)
    with pytest.raises(AssertionError):
        check_step_reference(mutant)


def test_reinitialized_state_mutant_is_detected():
    h = th.TemperatureHistory.constant_celsius((0., 1., 2.), (88., 98.))
    original = th.BDF
    def resetting(fun, t0, y0, *args, **kwargs):
        if t0:
            y0 = reference_initial(371.15, "caffeine", 7)
        return original(fun, t0, y0, *args, **kwargs)
    with patch.object(th, "BDF", resetting):
        mutant = run(h)
    with pytest.raises(AssertionError):
        check_step_reference(mutant)


def test_noop_segmentation_translation_delayed_observations_and_repeat():
    h = th.TemperatureHistory.constant_celsius((0., 2.), (88.,))
    a = run(h)
    b = run(th.TemperatureHistory.constant_celsius((0., 1., 2.), (88., 88.)))
    np.testing.assert_allclose(reduced(a.observations), reduced(b.observations), rtol=1e-7, atol=1e-9)
    shift = run(th.TemperatureHistory.constant_celsius((100., 102.), (88.,)),
                t_span_s=(100., 102.), observation_times_s=(100., 100.5, 101., 101.5, 102.),
                fraction_bounds_s=(100., 101., 102.))
    np.testing.assert_allclose(reduced(a.observations), reduced(shift.observations), rtol=1e-8, atol=1e-10)
    late = run(h, observation_times_s=(1., 2.), fraction_bounds_s=(1., 2.))
    np.testing.assert_array_equal(reduced(late.observations), reduced(a.observations)[[2, 4]])
    assert late.fractions[0].concentration_kg_m3 == a.fractions[1].concentration_kg_m3
    again = run(h)
    np.testing.assert_array_equal(reduced(a.checked_trajectory), reduced(again.checked_trajectory))
    assert a.to_json() == again.to_json()


@pytest.mark.parametrize("kw", [
    {"flow_m3_s": 2.}, {"flow_m3_s": float("nan")}, {"flow_m3_s": 0.},
    {"flow_m3_s": 3.01e-6}, {"solute": "CQA"}, {"grind": 1.5},
    {"observation_times_s": (.5, .5)}, {"observation_times_s": (1., .5)},
    {"observation_times_s": (-1., 1.)}, {"observation_times_s": (1., 3.)},
    {"observation_times_s": [[1.], [2.]]}, {"observation_times_s": (float("inf"),)},
    {"fraction_bounds_s": (1., 1.)}, {"fraction_bounds_s": (1.,)},
    {"fraction_bounds_s": (0., 1e-15)}, {"t_span_s": (0., 0.)},
    {"t_span_s": (-1., 2.)}, {"t_span_s": (0., 1., 2.)},
])
def test_input_rejection_precedes_integration(kw):
    with patch.object(th, "BDF", side_effect=AssertionError("must not integrate")):
        with pytest.raises(th.InvalidTemperatureHistoryInput) as exc:
            run(**kw)
    assert json.loads(exc.value.to_json())["status"] == "INVALID_INPUT"


@pytest.mark.parametrize("args", [((0, 1, 1), (360, 361, 362), "linear"),
                                   ((0, 1), (360,), "linear"),
                                   ((0, 1), (360, 361), "constant"),
                                   ((0, 1), (352, 360), "linear"),
                                   ((0, 1), (360, float("nan")), "linear"),
                                   ((0, 1), (360, 361), "spline")])
def test_malformed_histories(args):
    with pytest.raises(th.InvalidTemperatureHistoryInput):
        th.TemperatureHistory(*args)


@pytest.mark.parametrize("kw", [{"nz": 4}, {"nz": 7.5}, {"rtol": 0},
                                 {"normalized_atol": float("nan")}, {"max_steps": True},
                                 {"max_step_s": float("inf")}, {"diagnostic_step_s": -1}])
def test_invalid_settings(kw):
    with pytest.raises(th.InvalidTemperatureHistoryInput):
        th.TemperatureHistorySettings(**kw)


def test_failure_partial_prefix_and_strict_serialization():
    r = run(settings=replace(S, max_steps=2))
    assert not r.integration_complete and r.status == "INTEGRATION_FAILED"
    assert 0 < r.actual_span_s[1] < .5
    assert all(f.concentration_kg_m3 is None for f in r.fractions)
    assert len(r.observations.times_s) == 1
    assert np.isfinite(reduced(r.checked_trajectory)).all()
    assert r.observation_status[-1] == "OUTSIDE_ACTUAL_SUPPORT"
    json.loads(r.to_json(), parse_constant=lambda x: pytest.fail(x))
    with patch.object(th, "BDF", side_effect=RuntimeError("forced")):
        r = run(observation_times_s=(1., 2.))
    assert r.actual_span_s == (0., 0.) and len(r.observations.times_s) == 0
    assert r.reason == "INTEGRATOR_EXCEPTION:RuntimeError"
    json.loads(r.to_json(), parse_constant=lambda x: pytest.fail(x))


def test_dense_failure_keeps_preceding_checked_prefix():
    original = th.BDF.dense_output
    calls = []
    def corrupt(self):
        calls.append(self.t)
        dense = original(self)
        if len(calls) == 3:
            return lambda t: dense(t)*float("nan")
        return dense
    with patch.object(th.BDF, "dense_output", corrupt):
        r = run()
    assert r.reason == "NONFINITE_DENSE_OUTPUT"
    assert r.actual_span_s[1] == calls[1]
    assert np.isfinite(reduced(r.checked_trajectory)).all()


def test_clock_origin_is_not_query_origin_and_fraction_guard():
    r = run(observation_times_s=(1.5, 2.), fraction_bounds_s=(1.5, 2.))
    assert r.checked_trajectory.times_s[0] == 0.
    assert r.observations.hydraulic_volume_m3[0] == 3e-6
    assert r.observations.outlet_solute_kg[0] > 0
    tiny = run(fraction_bounds_s=(1., 1.+1e-10))
    assert tiny.integration_complete and tiny.status == "OBSERVER_UNRESOLVED"
    assert tiny.fractions[0].concentration_kg_m3 is None


@pytest.mark.parametrize("n", [5, 8, 12])
def test_independent_stencil_budget_and_jacobian_multiple_meshes(n):
    Q, T = 2e-6, 364.15
    sys = th._PhysicalSystem("trigonelline", 1.4, Q, n)
    rng = np.random.default_rng(105+n)
    for _ in range(3):
        y = rng.uniform(.1, 4, 3*n)
        rhs = sys.physical_rhs(T, y)
        np.testing.assert_allclose(rhs, physical_operator(T, Q, "trigonelline", 1.4, n)@y,
                                   rtol=3e-14, atol=1e-12)
        cl, s1, s2 = np.r_[0., y[:n-1]], y[n-1:2*n-1], y[2*n-1:-1]
        dcl, ds1, ds2 = np.r_[0., rhs[:n-1]], rhs[n-1:2*n-1], rhs[2*n-1:-1]
        w = np.full(n, ps.L/(n-1)); w[[0, -1]] *= .5
        weighted = ps.ACS*np.dot(w, ps.ALPHA_L*dcl+sys.as1*ds1+ps.PHI_V2*sys.as2*ds2)+rhs[-1]
        K, f1, f2, _, _ = sys.coefficients(T)
        transport = Q*(cl[-1]-np.dot(w[1:], (sys.D@cl)[1:]))
        inlet = -ps.ACS*w[0]*K*(sys.as1*f1*s1[0]+ps.PHI_V2*sys.as2*f2*s2[0])
        np.testing.assert_allclose(weighted, transport+inlet, atol=2e-19)
    initial = sys.initial_state(T)
    cl = np.r_[0., initial[:n-1]]
    m0h = ps.ACS*np.dot(w, ps.ALPHA_L*cl+sys.as1*initial[n-1:2*n-1]
                        +ps.PHI_V2*sys.as2*initial[2*n-1:-1])
    expected_offset = -ps.ACS*w[0]*ps.ALPHA_L*cl[-1]
    assert m0h-sys.continuum_inventory(T) == pytest.approx(expected_offset, abs=2e-19)


def test_partial_solve_cannot_return_complete_fraction_set():
    original = th.BDF.step
    def fail_late(self):
        if self.t > .8:
            self.status = "failed"
            return "forced integration failure"
        return original(self)
    with patch.object(th.BDF, "step", fail_late):
        r = run(observation_times_s=(0., .1, .5, 2.), fraction_bounds_s=(0., .1, .5, 2.))
    assert r.status == "INTEGRATION_FAILED"
    assert [f.status for f in r.fractions] == ["PREFIX_SUPPORTED", "PREFIX_SUPPORTED", "UNSUPPORTED"]
    assert r.fractions[-1].concentration_kg_m3 is None
    assert r.actual_span_s[1] > .8


def test_history_lists_are_copied_and_model_end_at_jump_is_left_sided():
    t, T = [0., 1., 2.], [88., 98.]
    h = th.TemperatureHistory.constant_celsius(t, T)
    t[1], T[0] = .5, 80.
    assert h.times_s == (0., 1., 2.) and h.temperatures_K[0] == 361.15
    r = run(h, t_span_s=(0., 1.), observation_times_s=(0., 1.), fraction_bounds_s=(0., 1.))
    expected = expm(physical_operator(361.15, 2e-6, "caffeine", 1.7, 7).toarray())@reference_initial(
        361.15, "caffeine", 7)
    np.testing.assert_allclose(reduced(r.observations)[-1], expected, rtol=1e-7, atol=1e-9)
    assert r.observations.temperature_K[-1] == 371.15
    assert r.segments[-1].endpoint_temperature_K[-1] == 361.15

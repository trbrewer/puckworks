"""N<=12 algebraic/API checks; no external data, target outcomes or qualification sweep."""
from dataclasses import FrozenInstanceError, replace
import json
from unittest.mock import patch

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.models.pannusch2024 import temperature_history_fv as fv
from puckworks.models.pannusch2024 import solver as ps
from tools import pannusch_positive_fv_reference as ref

S = fv.FVSettings(cells=5, h_max_s=.02, diagnostic_step_s=.0125)


def run(history=None, **kw):
    history = history or fv.TemperatureHistory.linear_celsius((0, .08), (88, 93))
    args = dict(flow_m3_s=2e-6, t_span_s=(0, .08), solute="caffeine", grind=1.7,
                observation_times_s=(0, .02, .04, .08), fraction_bounds_s=(0, .04, .08), settings=S)
    args.update(kw)
    return fv.simulate_temperature_history_fv(history, **args)


def off_diagonal(B):
    a = B.toarray().copy(); np.fill_diagonal(a, 0)
    return a


@pytest.mark.parametrize("n", [1, 4, 12])
@pytest.mark.parametrize("solute", fv.th.SPECIES)
@pytest.mark.parametrize("T", [353.15, 371.15])
def test_independent_balance_assembly_and_generator_structure(n, solute, T):
    sys = fv._System(solute, 1.7, 2e-6, n)
    B = sys.generator(T).toarray()
    scales = np.r_[sys.capacities, 1.]
    A = ref.operator_factory(2e-6, solute, 1.7, n)(T).toarray()
    np.testing.assert_allclose(B, scales[:, None]*A/scales[None, :], atol=2e-13, rtol=2e-14)
    assert np.min(off_diagonal(sys.generator(T))) >= 0
    assert np.max(np.abs(B.sum(axis=0)))/max(1., np.max(np.abs(B))) <= 1e-12
    state = np.random.default_rng(710).random(3*n+1)
    derivative = B@state
    assert abs(derivative.sum()) <= 1e-12*max(1., np.linalg.norm(derivative, 1))
    assert np.all(sys.initial(T) >= 0)
    assert abs(sys.initial(T).sum()-sys.M0(T)) <= 2e-15*sys.M0(T)
    assert sys.initial(T)[0] > 0  # first cell stores its full average, not an inlet boundary node
    assert abs(sys.capacities[2*n]/(sys.W*ps.PHI_V2*sys.as2)-1) < 1e-14
    # Two arbitrary nonnegative states, including a single donor, remain nonnegative.
    for y in (state, np.eye(3*n+1)[0]):
        got = expm(B*.1)@y
        assert got.min() >= -1e-14 and abs(got.sum()-y.sum()) <= 1e-12*max(1., y.sum())


def test_exchange_cancellation_and_flux_telescoping_independently():
    s = fv._System("tds", 1.4, 3e-6, 7)
    c = np.random.default_rng(912).random((3, 7))
    K, k1, k2 = s.coefficients(363.15)
    R1 = s.W*s.as1*k1*(K*c[1]-c[0])
    R2 = s.W*ps.PHI_V2*s.as2*k2*(K*c[2]-c[0])
    F = np.r_[0., s.Q*c[0]]
    balances = np.r_[F[:-1]-F[1:]+R1+R2, -R1, -R2, F[-1]]
    mass = np.r_[c.reshape(-1)*s.capacities, .1]
    np.testing.assert_allclose(s.generator(363.15)@mass, balances, atol=1e-20, rtol=2e-14)
    assert abs(balances.sum()) < 1e-19
    np.testing.assert_allclose((R1+R2)-R1-R2, 0, atol=1e-22)


def test_closed_cell_equilibrium_relaxation_and_zero_exchange_transport():
    B = fv._mass_generator(3, 0., .4, .2, .1, .05).toarray()
    equilibrium = np.r_[np.arange(1, 4), 4*np.arange(1, 4), 4*np.arange(1, 4), 0.]
    np.testing.assert_allclose(B@equilibrium, 0, atol=2e-16)
    start = np.r_[np.ones(3), np.zeros(7)]
    relaxed = expm(B*200)@start
    assert relaxed.min() >= 0 and abs(relaxed.sum()-start.sum()) < 1e-12
    np.testing.assert_allclose(relaxed[:-1], np.tile([1/9]*3, 3)*np.repeat([1, 4, 4], 3), atol=2e-6)
    transport = fv._mass_generator(3, 2., 0., 0., 0., 0.).toarray()
    got = expm(transport*.5)@np.eye(10)[0]
    np.testing.assert_allclose(got[:3], np.exp(-1)*np.array([1, 1, .5]), rtol=1e-14)
    assert abs(got.sum()-1) < 1e-14
    # A negative off-diagonal old nodal transport coupling must fail the structural assertion.
    old = -ps.five_point_biased_upwind(7, ps.L/6, 1.)
    np.fill_diagonal(old, 0)
    with pytest.raises(AssertionError):
        assert old.min() >= 0


def test_constant_dense_reference_and_independent_radau():
    h = fv.TemperatureHistory.constant_celsius((0, .08), (88,))
    r = run(h)
    A = ref.operator_factory(2e-6, "caffeine", 1.7, 5)(361.15).toarray()
    y, M0 = ref.initial_and_inventory(361.15, "caffeine", 1.7, 5)
    expected = expm(A*.08)@y
    got = np.r_[r.observations.liquid_cell_average_kg_m3[-1], r.observations.fine_cell_average_kg_m3[-1],
                r.observations.coarse_cell_average_kg_m3[-1], r.observations.outlet_solute_kg[-1]]
    np.testing.assert_allclose(got, expected, rtol=2e-13, atol=1e-15)
    ramp = run(settings=replace(S, h_max_s=.001))
    independent, _, _, _ = ref.radau(ramp.history, 2e-6, "caffeine", 1.7, 5,
                                     ramp.observations.times_s, t_span_s=(0, .08))
    np.testing.assert_allclose(ramp.observations.liquid_cell_average_kg_m3, independent[:, :5], rtol=1e-7)
    assert r.numerical_admissibility == "PASSED_SAMPLED_CHECKS"
    assert r.M0_cont_kg == M0 and abs(r.M0_fv_kg-M0) < 1e-18
    for order in (4, 8):
        use = r.quadrature.order == order
        integral = np.sum(r.quadrature.weights_s[use]*r.quadrature.outlet_flux_kg_s[use])
        assert abs(integral-r.observations.outlet_solute_kg[-1]) < 1e-13*M0


def test_observation_independence_and_same_frozen_generator_partial_extension():
    h = fv.TemperatureHistory.linear_celsius((0, .08), (80, 98))
    a = run(h)
    b = run(h, observation_times_s=(0, .003, .02, .027, .04, .08))
    np.testing.assert_array_equal(a.trace.masses_kg, b.trace.masses_kg)
    np.testing.assert_array_equal(a.trace.times_s, b.trace.times_s)
    system = fv._System("caffeine", 1.7, 2e-6, 5)
    Tmid = h.value_K(.01)
    expected = expm(system.generator(Tmid).toarray()*.003)@system.initial(h.value_K(0))
    np.testing.assert_allclose(b.observations.liquid_cell_average_kg_m3[1], expected[:5]/system.capacities[:5], rtol=3e-15)
    assert Tmid != h.value_K(.0015)


def test_steps_knots_no_reset_delayed_window_translation_and_noop_segments():
    h = fv.TemperatureHistory.constant_celsius((0, .04, .08), (88, 98))
    r = run(h)
    first, second = map(dict, r.segments)
    assert first["end_state_sha256"] == second["start_state_sha256"]
    sys = fv._System("caffeine", 1.7, 2e-6, 5)
    expected = expm(sys.generator(371.15).toarray()*.04)@expm(sys.generator(361.15).toarray()*.04)@sys.initial(361.15)
    np.testing.assert_allclose(r.trace.masses_kg[-1], expected, rtol=3e-14)
    late = run(h, observation_times_s=(.04, .08), fraction_bounds_s=(.04, .08))
    np.testing.assert_array_equal(r.observations.fine_cell_average_kg_m3[-2:], late.observations.fine_cell_average_kg_m3)
    assert late.fractions[0].concentration_kg_m3 == r.fractions[1].concentration_kg_m3
    shift = run(fv.TemperatureHistory.constant_celsius((10, 10.04, 10.08), (88, 98)),
                t_span_s=(10, 10.08), observation_times_s=(10, 10.02, 10.04, 10.08), fraction_bounds_s=(10, 10.04, 10.08))
    np.testing.assert_allclose(shift.observations.liquid_cell_average_kg_m3, r.observations.liquid_cell_average_kg_m3, rtol=2e-13)
    a = run(fv.TemperatureHistory.constant_celsius((0, .08), (88,)))
    b = run(fv.TemperatureHistory.constant_celsius((0, .04, .08), (88, 88)))
    np.testing.assert_allclose(a.trace.masses_kg[-1], b.trace.masses_kg[-1], rtol=1e-14)


def test_immutability_repeatability_and_strict_serialization():
    before = json.dumps([ps.GRINDS, ps._solute_params()], sort_keys=True)
    a, b = run(), run()
    np.testing.assert_array_equal(a.trace.masses_kg, b.trace.masses_kg)
    np.testing.assert_array_equal(a.quadrature.outlet_flux_kg_s, b.quadrature.outlet_flux_kg_s)
    assert before == json.dumps([ps.GRINDS, ps._solute_params()], sort_keys=True) and ps.NZ == 200
    with pytest.raises(FrozenInstanceError):
        a.solute = "tds"
    with pytest.raises(ValueError):
        a.trace.masses_kg.setflags(write=True)
    assert isinstance(a.segments[0], tuple)
    raw = json.loads(a.to_json(), parse_constant=lambda x: pytest.fail(x))
    assert raw["backend"] == fv.BACKEND and raw["accuracy_status"] == "NOT_ASSESSED"
    assert all(x["physical_prediction_status"] == "NOT_VALIDATED" for x in raw["fractions"])
    assert all(x == 0 for x in a.observations.hydraulic_volume_m3-2e-6*a.observations.times_s)


@pytest.mark.parametrize("kw", [
    {"flow_m3_s": 0}, {"flow_m3_s": 3.1e-6}, {"flow_m3_s": np.complex128(2e-6)},
    {"grind": 1.5}, {"grind": np.complex128(1.7)}, {"solute": "CQA"},
    {"t_span_s": (0, 0)}, {"t_span_s": (-1, .08)}, {"t_span_s": (0, .04, .08)},
    {"observation_times_s": (0, .02, .02)}, {"observation_times_s": (.09,)},
    {"observation_times_s": np.array([0+1j, .08+1j])},
    {"fraction_bounds_s": (0, 1e-20)}, {"fraction_bounds_s": (.02,)},
])
def test_invalid_input_before_any_exponential(kw):
    with patch.object(fv, "expm_multiply", side_effect=AssertionError("must reject first")):
        with pytest.raises(fv.InvalidTemperatureHistoryInput):
            run(**kw)


@pytest.mark.parametrize("kw", [{"cells": 0}, {"cells": True}, {"cells": 3.5}, {"h_max_s": np.complex128(.02)},
                                 {"wall_time_limit_s": 121}, {"diagnostic_step_s": float("nan")}])
def test_invalid_settings(kw):
    with pytest.raises(fv.InvalidTemperatureHistoryInput):
        fv.FVSettings(**kw)


def test_finite_prefix_and_completed_but_inadmissible_output():
    r = run(settings=replace(S, max_steps=1))
    assert not r.integration_complete and r.actual_span_s == (0, .02)
    assert r.reason == "STEP_LIMIT" and r.fractions[-1].concentration_kg_m3 is None
    json.loads(r.to_json(), parse_constant=lambda x: pytest.fail(x))
    original = fv.expm_multiply
    count = 0
    def fail_second(*args, **kw):
        nonlocal count
        count += 1
        return np.full_like(args[1], np.nan) if count == 2 else original(*args, **kw)
    with patch.object(fv, "expm_multiply", fail_second):
        r = run()
    assert r.actual_span_s == (0, .02) and np.isfinite(r.trace.masses_kg).all()
    def bad(B, x, **kw):
        out = x.copy(); out[0] = -abs(x[0]); return out
    with patch.object(fv, "expm_multiply", bad):
        r = run()
    assert r.integration_complete and r.numerical_admissibility == "FAILED"
    assert all(f.concentration_kg_m3 is None for f in r.fractions)
    assert r.observations.liquid_cell_average_kg_m3.min() < 0


def test_observer_failure_discards_unchecked_suffix_and_runtime_caps():
    original = fv.expm_multiply
    counter = 0
    def fail_observer(*args, **kw):
        nonlocal counter
        counter += 1
        if counter == 20:
            raise RuntimeError("forced")
        return original(*args, **kw)
    with patch.object(fv, "expm_multiply", fail_observer):
        r = run()
    assert r.status == "INTEGRATION_FAILED" and r.actual_span_s[1] < .08
    assert r.trace.times_s[-1] == r.actual_span_s[1]
    assert r.checked_trajectory.times_s[-1] == r.actual_span_s[1]
    assert r.propagations == 4  # attempted primary work is counted even though suffix is withheld
    r = run(settings=replace(S, max_exponential_applications=1))
    assert r.reason == "EXPONENTIAL_APPLICATION_LIMIT" and r.exponential_applications == 1
    with patch.object(fv.time, "monotonic", side_effect=range(1000)):
        r = run(settings=replace(S, wall_time_limit_s=.5))
    assert r.reason == "WALL_TIME_LIMIT" and r.actual_span_s == (0, 0)


def test_small_mesh_input_envelope_corners_and_passive_analytical_initial_averages():
    for T, Q, grind in ((80, 1e-6, 1.4), (98, 3e-6, 2.0)):
        h = fv.TemperatureHistory.constant_celsius((0, .02), (T,))
        r = run(h, flow_m3_s=Q, grind=grind, t_span_s=(0, .02), observation_times_s=(0, .02),
                fraction_bounds_s=(0, .02), settings=replace(S, cells=12))
        assert r.numerical_admissibility == "PASSED_SAMPLED_CHECKS"
    exact, out, M0 = ref.passive_exact(12, [0, ps.ACS*ps.ALPHA_L*ps.L/2e-6*1.25], 2e-6)
    assert abs(exact[0].sum()*ps.L/12-ps.L/2) < 1e-17
    assert exact[0, 0] > 0 and np.all(exact[-1] == 0) and out[-1] == M0

"""005 deterministic offline N<=12 verification; no full-mesh campaign here."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import json
import math
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.models.pannusch2024 import state_envelope as se, stateful_fv as sf
from tools import pannusch_flow_temp_fv_reference as reference


def plan(n=4, kind='linear', origin=7., h=.02):
    t = origin
    T = (sf.TemperatureHistory.linear_celsius((t, t+.043, t+.11), (80, 95, 86))
         if kind == 'linear' else sf.TemperatureHistory.constant_celsius((t, t+.033, t+.11), (80, 98)))
    Q = sf.FlowHistory((t, t+.071, t+.11),
        (1.2e-6, 2.8e-6, 1.6e-6) if kind == 'linear' else (1e-6, 2.7e-6), kind)
    return sf.FVPlan(T, Q, (t, t+.11), sf.FVSettings(cells=n, h_max_s=h))


def state(n=4, species='caffeine', grind=1.7, origin=7., concentrations=None):
    x = (np.arange(n)+.5)/n
    c = np.array([1+3*x, 9-4*x, 2+5*x*x]) if concentrations is None else np.asarray(concentrations)
    return sf.FVChemicalState.from_cell_averages(solute=species, grind=grind, time_s=origin,
        edges_m=np.linspace(0., .015, n+1), liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])


def singleton(s):
    return se.FVChemicalStateSet(s, s, (0., 2*s.inventory_kg), 'SYNTHETIC_SINGLETON')


def response(p=None, window=None, species='caffeine', grind=1.7, **kw):
    p = p or plan()
    return se.build_delivery_response(p, solute=species, grind=grind,
        window_s=window or (p.t_span_s[0]+.013, p.t_span_s[1]-.007), **kw)


def dense_response(p, window, species='caffeine', grind=1.7):
    """Independent concentration balance assembly; no production generator read."""
    n = p.settings.cells
    psi = sf.fv.ps.GRINDS[grind]['psi']
    W = sf.fv.ps.ACS*(sf.fv.ps.L/n)
    cap = np.repeat(W*np.array([sf.fv.ps.ALPHA_L, psi*(1-sf.fv.ps.ALPHA_L),
        sf.fv.ps.PHI_V2*(1-psi)*(1-sf.fv.ps.ALPHA_L)]), n)
    assemble = reference.operator_factory(species, grind, n)
    transfer = np.eye(3*n)
    reward = np.zeros(3*n)
    for a, b, T, Q in p.primary_steps:
        C = assemble(T, Q).toarray()  # independently assembled concentration equations
        factors = np.r_[cap, 1.]
        B = factors[:, None]*C/factors[None, :]
        lo, hi = max(a, window[0]), min(b, window[1])
        if hi > lo:
            before = expm(B*(lo-a))[:3*n, :3*n]@transfer
            reward += expm(B*(hi-lo))[-1, :3*n]@before
        transfer = expm(B*(b-a))[:3*n, :3*n]@transfer
    return reward, cap


@pytest.mark.parametrize('species', sf.fv.th.SPECIES)
@pytest.mark.parametrize('grind', (1.4, 1.7, 2.0))
@pytest.mark.parametrize('origin', (0., 7.))
def test_singleton_replays_unchanged_forward_for_every_source_species(species, grind, origin):
    p, s = plan(origin=origin), state(species=species, grind=grind, origin=origin)
    u = singleton(s)
    r = response(p, species=species, grind=grind)
    out = se.replay_extrema(se.bound_delivery(u, r, epsilon_kg=1e-10))
    assert out.numerical_status == 'NUMERICALLY_QUALIFIED'
    assert out.forward_calls == 2 and out.optimization_calls == 2
    for e in (out.minimum, out.maximum):
        assert e.witness.residuals.feasible
        w = e.witness.replays[0]
        assert abs(w.discrepancy_kg) <= 1e-11*s.inventory_kg
        assert e.interval_kg[0] <= w.forward_delivery_kg <= e.interval_kg[1]
        assert w.parent_accuracy == 'NOT_ASSESSED'
    assert out.concentration_interval_kg_m3[0] == out.outer_delivery_interval_kg[0]/r.volume_m3


@pytest.mark.parametrize('n', (1, 4, 12))
@pytest.mark.parametrize('kind', ('linear', 'constant'))
@pytest.mark.parametrize('window', ((7., 7.11), (7.013, 7.104), (7.031, 7.031001)))
def test_independent_dense_capacities_order_and_original_step_rewards(n, kind, window):
    p = plan(n=n, kind=kind)
    r = response(p, window)
    g, cap = dense_response(p, window)
    u = singleton(state(n=n))
    np.testing.assert_allclose(u.capacities_m3, cap, rtol=5e-16)
    assert r.status == 'RESPONSE_QUALIFIED'
    assert np.all(np.abs(r.weights-g) <= r.coefficient_allowances)
    np.testing.assert_allclose(r.weights, g, atol=1e-13, rtol=1e-11)
    assert np.all(r.weights >= -r.coefficient_allowances)
    assert np.all(r.weights <= 1+r.coefficient_allowances)


def test_no_exchange_manufactured_advection_uses_existing_seam():
    p = plan(n=1, kind='constant')
    with patch.object(sf.fv._System, 'coefficients', return_value=(1., 0., 0.)):
        r = response(p, (7., 7.11))
    capacity = sf.fv.ps.ACS*.015*sf.fv.ps.ALPHA_L
    integrated_rate = math.fsum((b-a)*Q/capacity for a, b, T, Q in p.primary_steps)
    assert r.weights[0] == pytest.approx(-math.expm1(-integrated_rate), rel=1e-13)
    assert np.array_equal(r.weights[1:], np.zeros(2))


def test_zero_advection_manufactured_reward_is_zero_without_public_physics_switch():
    def closed(self, T, Q):
        return sf.fv._mass_generator(self.n, 0., .1, .2, .3, .4)
    with patch.object(sf.fv._System, 'generator', closed):
        r = response()
    np.testing.assert_array_equal(r.weights, np.zeros(12))
    # This manufactured closed system is outside the public positive-flow
    # response domain; do not promote an unresolved positive-window zero.
    assert r.status == 'NUMERICALLY_UNRESOLVED'


def test_malformed_response_payloads_and_decision_arguments_are_rejected():
    r, u = response(), singleton(state())
    for kwargs in (dict(weights=np.zeros(2)), dict(weights=np.ones(12, dtype=bool)),
                   dict(volume_m3=1.), dict(window_s=(6., 7.1)), dict(coefficient_allowances=None)):
        with pytest.raises(ValueError): replace(r, **kwargs)
    with pytest.raises(ValueError): se.bound_delivery(u, r, epsilon_kg=0.)
    with pytest.raises(ValueError): se.contrast_deliveries(u, r, r, epsilon_kg=1e-9,
        delta_kg=True, comparison_basis='MATCHED_COLLECTED_VOLUME')
    with pytest.raises(ValueError): se.contrast_deliveries(u, r, r, epsilon_kg=1e-9,
        delta_kg=1e-9, comparison_basis='UNQUALIFIED_SUPERIORITY')


def inventory_fixture(total=None, n=2, phases=None):
    upper = np.zeros((3, n)); upper[0] = 10.
    lo, hi = state(n=n, concentrations=np.zeros((3, n))), state(n=n, concentrations=upper)
    cap = sf.fv._System('caffeine', 1.7, n).capacities[0]
    M = cap*10.
    return se.FVChemicalStateSet(lo, hi, (M, M) if total is None else total,
                              'MANUFACTURED_INVENTORY', phases), M


def synthetic_optima(u, coefficients):
    g = np.zeros(len(u.lower_masses_kg)); g[:len(coefficients)] = coefficients
    return tuple(se._optimize(u, g, np.zeros(len(g)), sense, se.FVEnvelopeSettings())
                 for sense in ('minimum', 'maximum'))


def assert_contains(e, expected):
    assert e.status == 'OPTIMIZATION_QUALIFIED', e.termination
    assert e.interval_kg[0] <= expected <= e.interval_kg[1]
    assert e.witness.residuals.feasible
    assert e.optimization.checked_dual_lower_kg is not None
    assert e.optimization.dual_roundoff_allowance_kg >= 0
    assert e.gap_kg <= 1e-10*e.optimization.scale_kg


def test_analytical_inventory_extrema_and_checked_dual_evidence():
    u, M = inventory_fixture()
    minimum, maximum = synthetic_optima(u, (.8, .2))
    assert_contains(minimum, .2*M); assert_contains(maximum, .8*M)
    for e in (minimum, maximum):
        assert np.all(e.optimization.inequality_duals <= 0)
        assert e.witness.residuals.total_kg == M


def test_direct_shared_inventory_contrast_not_subtracted_envelopes():
    u, M = inventory_fixture()
    A, B = synthetic_optima(u, (.8, .6)), synthetic_optima(u, (.6, .4))
    d = synthetic_optima(u, np.array([.8, .6])-np.array([.6, .4]))
    assert A[0].interval_kg[0] <= B[1].interval_kg[1]
    for e in d:
        assert_contains(e, .2*M)
    assert d[1].interval_kg[1]-d[0].interval_kg[0] < 1e-10*M


def test_required_manufactured_reversal_has_feasible_common_state_witnesses():
    u, M = inventory_fixture()
    ga, gb = np.array([.8, .2]), np.array([.2, .8])
    low, high = synthetic_optima(u, ga-gb)
    assert_contains(low, -.6*M); assert_contains(high, .6*M)
    # Independent analytical functional replay, using each identical mass state
    # for A and B. Actual source-model replay is covered separately end to end.
    intervals = []
    for e in (low, high):
        m = e.witness.masses_kg[:2]
        delta = math.fsum(ga*m)-math.fsum(gb*m)
        intervals.append((delta-1e-12*M, delta+1e-12*M))
    decision, opposite, material = se._decision((-.6*M, .6*M), .1*M, intervals, True)
    assert decision == 'DEMONSTRATED_MATERIAL_REVERSAL' and opposite and material


@pytest.mark.parametrize('outer, witnesses, expected, opposite, material', [
    ((1.1, 2), ((1.1, 1.2), (1.9, 2)), 'A_UNIFORMLY_EXCEEDS_B_BY_MARGIN', False, False),
    ((-2, -1.1), ((-2, -1.9), (-1.2, -1.1)), 'B_UNIFORMLY_EXCEEDS_A_BY_MARGIN', False, False),
    ((-.4, .4), ((-.4, -.3), (.3, .4)), 'NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET', True, False),
    ((.2, 2), ((.2, .3), (1.9, 2)), 'NO_UNIFORM_MATERIAL_CONCLUSION', False, False),
    ((-2, 2), ((-.2, .2), (-.2, .2)), 'NO_UNIFORM_MATERIAL_CONCLUSION', False, False),
    ((-2, 2), ((-2, -1.9), (1.9, 2)), 'DEMONSTRATED_MATERIAL_REVERSAL', True, True),
    ((-1, 1), ((-1, -1), (1, 1)), 'NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET', True, False),
])
def test_decision_precedence_and_zero_crossing_is_not_a_reversal(outer, witnesses, expected, opposite, material):
    assert se._decision(outer, 1., witnesses, True) == (expected, opposite, material)
    assert se._decision(outer, 1., witnesses, False)[0] == 'NUMERICALLY_UNRESOLVED'


def test_phase_constraints_redundancy_empty_and_collapsed_bounds():
    u, M = inventory_fixture()
    redundant = replace(u, phase_inventory_kg=((M, M), (0., 0.), (0., 0.)))
    for a, b in zip(synthetic_optima(u, (.8, .2)), synthetic_optima(redundant, (.8, .2))):
        np.testing.assert_allclose(a.interval_kg, b.interval_kg, atol=1e-15*M)
    assert replace(u, total_inventory_kg=(3*M, 4*M)).feasibility == 'EMPTY_FEASIBLE_SET'
    assert replace(u, phase_inventory_kg=((0., M/2), (0., 0.), (0., 0.))).feasibility == 'EMPTY_FEASIBLE_SET'
    lo = state(n=1, concentrations=np.zeros((3, 1)))
    hi = state(n=1, concentrations=np.ones((3, 1))*10)
    cap = sf.fv._System('caffeine', 1.7, 1).capacities
    mixed = se.FVChemicalStateSet(lo, hi, (float(sum(cap)), float(sum(cap))*4), 'mixed',
        ((cap[0], 2*cap[0]), (cap[1], 3*cap[1]), (0., 4*cap[2])))
    out = synthetic_optima(mixed, (.2, .8, .4))
    assert_contains(out[0], .8*cap[1]+.4*cap[2])
    assert_contains(out[1], .4*cap[0]+2.4*cap[1]+1.6*cap[2])
    for e in out:
        assert e.status == 'OPTIMIZATION_QUALIFIED', e.termination
        assert e.witness.residuals.feasible
    collapsed = singleton(state(n=1))
    e = synthetic_optima(collapsed, (.2, .3, .4))
    assert e[0].witness.state.inventory_kg == e[1].witness.state.inventory_kg


def test_multiple_windows_additivity_and_original_plan_immutability():
    p = plan()
    identity = p.identity_sha256
    whole = response(p, (7.013, 7.104))
    parts = [response(p, w) for w in ((7.013, 7.031001), (7.031001, 7.073), (7.073, 7.104))]
    assert np.all(np.abs(sum(r.weights for r in parts)-whole.weights) <=
                  whole.coefficient_allowances+sum(r.coefficient_allowances for r in parts))
    assert p.identity_sha256 == identity
    assert whole.volume_m3 == pytest.approx(sum(r.volume_m3 for r in parts), rel=1e-14)
    repeat = response(p, (7.013, 7.104))
    assert repeat.identity_sha256 == whole.identity_sha256


@pytest.mark.parametrize('value', (0., 1e-250))
def test_genuine_zero_and_small_inventory_have_no_kg_floor(value):
    s = state(concentrations=np.full((3, 4), value))
    u = singleton(s)
    r = response()
    out = se.replay_extrema(se.bound_delivery(u, r, epsilon_kg=1e-12 if value == 0 else 1e-265))
    assert out.numerical_status == 'NUMERICALLY_QUALIFIED'
    if value == 0:
        assert out.outer_delivery_interval_kg == (0., 0.)
        assert out.optimization_calls == 0
    else:
        assert out.outer_delivery_interval_kg[0] > 0


def test_zero_duration_and_identical_plans_and_explicit_unequal_volume():
    u = singleton(state())
    zero = response(window=(7.03, 7.03))
    out = se.replay_extrema(se.bound_delivery(u, zero, epsilon_kg=1e-12))
    assert out.numerical_status == 'NUMERICALLY_QUALIFIED'
    assert out.outer_delivery_interval_kg == (0., 0.) and out.concentration_interval_kg_m3 is None
    r = response()
    contrast = se.contrast_deliveries(u, r, r, epsilon_kg=1e-10, delta_kg=1e-8,
                                    comparison_basis='MATCHED_COLLECTED_VOLUME')
    assert contrast.numerical_status == 'WITNESS_REPLAY_REQUIRED'
    out = se.replay_extrema(contrast)
    assert out.numerical_status == 'NUMERICALLY_QUALIFIED'
    assert out.decision_status == 'NO_MATERIAL_DIFFERENCE_THROUGHOUT_SET'
    assert out.forward_calls == 4 and not out.opposite_sign_reversal_supported
    r2 = response(window=(7., 7.11))
    with pytest.raises(ValueError, match='VOLUMES'):
        se.contrast_deliveries(u, r, r2, epsilon_kg=1e-10, delta_kg=1e-8,
                             comparison_basis='MATCHED_COLLECTED_VOLUME')
    out = se.contrast_deliveries(u, r, r2, epsilon_kg=1e-10, delta_kg=1e-8,
                               comparison_basis='EXPLICIT_UNEQUAL_VOLUME')
    assert out.comparison_basis == 'EXPLICIT_UNEQUAL_VOLUME'
    assert out.volume_difference_m3 != 0


def test_aliases_are_immutable_and_reuse_checks_all_model_identities():
    u, r = singleton(state()), response()
    with pytest.raises(ValueError): u.lower_masses_kg.setflags(write=True)
    with pytest.raises(ValueError): r.weights[0] = 7.
    with pytest.raises(FrozenInstanceError): u.assumption_label = 'changed'
    for other in (singleton(state(n=3)), singleton(state(species='tds')),
                  singleton(state(grind=1.4)), singleton(state(origin=0.))):
        with pytest.raises(ValueError, match='INCOMPATIBLE_RESPONSE'):
            se.bound_delivery(other, r, epsilon_kg=1e-9)
    out = se.bound_delivery(u, r, epsilon_kg=1e-9)
    with pytest.raises(ValueError): out.minimum.witness.optimizer_masses_kg.setflags(write=True)
    json.loads(out.to_json(), parse_constant=lambda v: pytest.fail(v))
    # Another compatible set reuses the response without any propagation.
    with patch.object(se, 'expm_multiply', side_effect=AssertionError('unexpected propagation')):
        assert se.bound_delivery(replace(u, assumption_label='another set'), r,
            epsilon_kg=1e-9).numerical_status == 'WITNESS_REPLAY_REQUIRED'


@pytest.mark.parametrize('bad', (True, '0.1', 1+0j, np.nan, np.inf, -1., Fraction(1, 10**400)))
def test_hostile_inventory_and_resolution_inputs(bad):
    s = state()
    with pytest.raises(ValueError): se.FVChemicalStateSet(s, s, (bad, 1.), 'bad')
    with pytest.raises(ValueError): se.bound_delivery(singleton(s), response(), epsilon_kg=bad)


def test_wrong_shapes_bases_identities_labels_and_underflow():
    s = state()
    for kwargs in (dict(total_inventory_kg=(0.,)), dict(inventory_units='g'),
                   dict(phase_inventory_kg=((0., 1.),)), dict(assumption_label=''),
                   dict(upper=state(n=3)), dict(total_inventory_kg=(2., 1.))):
        with pytest.raises(ValueError):
            se.FVChemicalStateSet(**dict(dict(lower=s, upper=s, total_inventory_kg=(0., 1.), assumption_label='x'), **kwargs))
    with pytest.raises(ValueError): replace(s, units_and_bases=(('concentration', 'kg/kg'),))
    with pytest.raises(ValueError): replace(s, edges_m=np.linspace(0., .016, 5))
    with pytest.raises(ValueError): replace(s, source_identities=())
    with pytest.raises(ValueError): state(concentrations=np.full((3, 4), 1e-320))
    with pytest.raises(ValueError): response(window=(6., 7.11))


def test_limited_failed_optimization_responses_and_resolution_floor():
    u, r = singleton(state()), response()
    limited = response(settings=se.FVEnvelopeSettings(max_exponential_actions=1))
    assert limited.status == 'NUMERICALLY_UNRESOLVED' and limited.termination == 'EXPONENTIAL_ACTION_LIMIT'
    out = se.bound_delivery(u, limited, epsilon_kg=1.)
    assert out.numerical_status == 'NUMERICALLY_UNRESOLVED'
    assert 'FALLBACK' in out.termination and out.minimum is None
    with patch.object(se, 'linprog', return_value=SimpleNamespace(success=False, status=1, nit=1)):
        out = se.bound_delivery(u, r, epsilon_kg=1.)
    assert out.numerical_status == 'NUMERICALLY_UNRESOLVED'
    assert out.minimum.optimization.solver_status == 1
    with patch.object(se, 'linprog', side_effect=RuntimeError('synthetic failure')):
        assert se.bound_delivery(u, r, epsilon_kg=1.).numerical_status == 'NUMERICALLY_UNRESOLVED'
    out = se.bound_delivery(u, r, epsilon_kg=1e-30)
    assert out.numerical_status == 'NUMERICALLY_UNRESOLVED' and out.minimum.gap_kg > 1e-30


def test_forward_rejection_remains_unresolved_without_discarding_set():
    u, r = singleton(state()), response()
    out = se.bound_delivery(u, r, epsilon_kg=1e-9)
    with patch.object(sf, 'simulate_stateful_fv', side_effect=ValueError('synthetic rejection')):
        failed = se.replay_extrema(out)
    assert failed.numerical_status == 'NUMERICALLY_UNRESOLVED'
    assert failed.outer_delivery_interval_kg == out.outer_delivery_interval_kg
    assert failed.minimum.witness.replays[0].forward_status == 'FORWARD_REJECTED'


def test_repair_is_explicit_preserves_original_residuals_and_rechecks_objective():
    u, M = inventory_fixture()
    raw = u.lower_masses_kg.copy(); raw[0] = M+1e-12*M
    w = se._witness(u, raw, np.ones(len(raw)), se.FVEnvelopeSettings())
    assert w.original_residuals.maximum_violation_kg > 0
    assert w.status == 'FEASIBLE' and w.residuals.feasible
    assert w.repair != 'NONE' and w.repair_updates > 0
    assert w.prediction_kg == M
    assert w.conversion_mass_change_kg > 0


def test_bad_dual_evidence_cannot_be_qualified_by_success_flag():
    u, M = inventory_fixture()
    actual = se.linprog
    def false_dual(*args, **kwargs):
        result = actual(*args, **kwargs)
        result.ineqlin.marginals[:] = 1.
        return result
    with patch.object(se, 'linprog', side_effect=false_dual):
        result = synthetic_optima(u, (.8, .2))
    assert all(e.status == 'NUMERICALLY_UNRESOLVED' for e in result)


@pytest.mark.parametrize('settings, reason', [
    (se.FVEnvelopeSettings(max_steps=1), 'RESPONSE_STEP_LIMIT'),
    (se.FVEnvelopeSettings(response_wall_s=1e-200), 'RESPONSE_WALL_LIMIT')])
def test_additional_response_resource_limits(settings, reason):
    r = response(settings=settings)
    assert r.status == 'NUMERICALLY_UNRESOLVED' and r.termination == reason


def test_unrepresentable_positive_window_volume_and_numerical_inventory():
    r = response(plan(origin=0.), (0., 1e-320))
    assert r.status == 'NUMERICALLY_UNRESOLVED' and r.termination == 'UNREPRESENTABLE_POSITIVE_VOLUME'
    u = se.FVChemicalStateSet(state(concentrations=np.zeros((3, 4))), state(),
                             (1e-320, 1e-320), 'TINY_POSITIVE_NOT_ZERO')
    out = se.bound_delivery(u, response(), epsilon_kg=1e-300)
    assert out.numerical_status == 'NUMERICALLY_UNRESOLVED'
    assert out.outer_delivery_interval_kg[1] > 0
    assert 'UNREPRESENTABLE' in out.minimum.termination


def test_failed_response_inventory_check_is_not_hidden_by_fallback():
    with patch.object(se, 'expm_multiply', side_effect=lambda B, v, **kw: np.full_like(v, 2.)):
        r = response()
    assert r.status == 'NUMERICALLY_UNRESOLVED'
    assert r.termination == 'RESPONSE_POSITIVITY_OR_INVENTORY_CHECK_FAILED'
    out = se.bound_delivery(singleton(state()), r, epsilon_kg=1.)
    assert out.numerical_status == 'NUMERICALLY_UNRESOLVED' and 'FALLBACK' in out.termination


def test_primary_contrast_replays_both_plans_from_identical_unknown_states():
    p = plan()
    other = sf.FVPlan(sf.TemperatureHistory.linear_celsius((7., 7.027, 7.11), (97, 81, 93)),
                     p.flow_history, p.t_span_s, p.settings)
    lo, hi = state(concentrations=np.ones((3, 4))), state(concentrations=np.ones((3, 4))*9)
    u = se.FVChemicalStateSet(lo, hi, (lo.inventory_kg, hi.inventory_kg), 'NONUNIFORM_BOUNDS')
    a, b = response(p), response(other)
    out = se.replay_extrema(se.contrast_deliveries(u, a, b, epsilon_kg=1e-9, delta_kg=1e-8,
        comparison_basis='MATCHED_COLLECTED_VOLUME'))
    assert out.numerical_status == 'NUMERICALLY_QUALIFIED'
    for e in (out.minimum, out.maximum):
        assert e.witness.replays[0].state_identity == e.witness.replays[1].state_identity
        np.testing.assert_allclose(e.witness.prediction_kg,
            math.fsum((a.weights-b.weights)*e.witness.masses_kg), rtol=1e-12)
    assert out.forward_calls == 4


def test_checked_dual_support_bounds_remain_global_without_stationarity():
    u, M = inventory_fixture()
    actual = se.linprog
    def zero_dual(*args, **kwargs):
        result = actual(*args, **kwargs)
        result.ineqlin.marginals[:] = 0.
        return result
    with patch.object(se, 'linprog', side_effect=zero_dual):
        low, high = synthetic_optima(u, (.8, .2))
    assert low.interval_kg[0] <= .2*M <= low.interval_kg[1]
    assert high.interval_kg[0] <= .8*M <= high.interval_kg[1]
    assert low.optimization.stationarity_residual_inf > 0
    assert low.gap_kg > .1*M  # a success flag cannot erase the global gap

"""006 small analytical/manufactured and fixed-model tests, N<=12 only."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import json
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from puckworks.models.pannusch2024 import prefix_conditioned as pc, state_envelope as se, stateful_fv as sf
from test_pannusch_state_envelope import plan, state, singleton, dense_response

M = 2.**-10


def simplex(m=M):
    return pc._Polytope(np.zeros(3), np.full(3, m), np.array([[1., 1., 1.], [-1., -1., -1.]]),
                        np.array([m, -m]), m, ('total:upper', 'total:lower'))


def exact_query(bands=None, m=M, error=None, epsilon=None):
    bands = [('early', np.array([.5, .25, 0.]), np.zeros(3), m/4, m/4)] if bands is None else bands
    return pc._query_core(simplex(m), bands, np.array([.5, .25, .125]),
                          np.zeros(3) if error is None else error, m*1e-10 if epsilon is None else epsilon)


def assert_bracket(bracket, value, m=M):
    assert bracket[0] <= value <= bracket[1]
    assert bracket[1]-bracket[0] <= 1e-10*m


def test_exact_nonunique_fixture_with_rational_vertices_and_explicit_duals():
    result = exact_query()
    assert result.compatibility == 'ESTABLISHED' and result.bounds == 'QUALIFIED'
    assert_bracket(result.minimum_bracket_kg, M/4)
    assert_bracket(result.maximum_bracket_kg, 5*M/16)
    np.testing.assert_array_equal(result.inner_optimizations[0].raw_masses_kg, [0, M, 0])
    np.testing.assert_array_equal(result.inner_optimizations[1].raw_masses_kg, [M/2, 0, M/2])
    # Rational parameterization is the independent oracle, not another LP.
    for t in (Fraction(0), Fraction(1, 8), Fraction(1, 4), Fraction(1, 2)):
        masses = np.array([float(t)*M, (1-2*float(t))*M, float(t)*M])
        assert pc._residuals(result.inner, masses).feasible
        assert pc._dotq([.5, .25, .125], masses) == Fraction.from_float(M)*(Fraction(1, 4)+t/8)
    D, _, _ = pc._weak_dual(result.outer, np.array([.5, .25, .125]), np.array([0., 0., 0., -1.]))
    assert D == M/4
    D, _, _ = pc._weak_dual(result.outer, -np.array([.5, .25, .125]), np.array([-.125, 0., -.75, 0.]))
    assert D == -5*M/16
    control = exact_query([])
    assert_bracket(control.minimum_bracket_kg, M/8)
    assert_bracket(control.maximum_bracket_kg, M/2)
    assert pc.conservation_bound(M, [('early', (0, 1), (M/4, M/4))]).interval_kg == (0, 3*M/4)


def test_joint_contradiction_requires_positive_checked_phase_one_bound():
    bands = [('one', np.array([.5, 0, 0]), np.zeros(3), 3*M/8, M/2),
             ('two', np.array([0, .5, 0]), np.zeros(3), 3*M/8, M/2)]
    for band in bands:
        assert exact_query([band]).compatibility == 'ESTABLISHED'
    result = exact_query(bands)
    assert result.compatibility == 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'
    assert result.bounds == 'NOT_APPLICABLE'
    assert 0 < result.feasibility.checked_dual_lower_kg <= M/10
    assert abs(result.feasibility.checked_dual_lower_kg-M/10) <= 1e-10*M
    with patch.object(pc, 'linprog', return_value=SimpleNamespace(success=False, status=2, nit=0)):
        unresolved = exact_query(bands)
    assert unresolved.compatibility == 'UNRESOLVED'
    assert unresolved.bounds == 'NUMERICALLY_UNRESOLVED'


@pytest.mark.parametrize('m', [2.**-10, 2.**-500, 2.**-900])
def test_small_representable_inventory_no_kg_floor(m):
    r = exact_query(m=m)
    assert r.bounds == 'QUALIFIED'
    assert_bracket(r.minimum_bracket_kg, m/4, m)
    assert_bracket(r.maximum_bracket_kg, 5*m/16, m)
    assert r.outer.scale_kg == m


def test_duplicates_reordering_wider_and_uninformative_bands():
    band = ('a', np.array([.5, .25, 0.]), np.zeros(3), M/4, M/4)
    duplicate = ('b', *band[1:])
    a, b = exact_query([band, duplicate]), exact_query([duplicate, band])
    assert a.outer_interval_kg == b.outer_interval_kg == exact_query().outer_interval_kg
    wider = exact_query([('a', *band[1:3], M/8, 3*M/8)])
    for mass in ([0., M, 0.], [M/2, 0., M/2], [M/4, M/2, M/4]):
        assert pc._residuals(wider.inner, np.array(mass)).feasible
    uninformative = exact_query([('a', *band[1:3], 0., M)])
    assert_bracket(uninformative.minimum_bracket_kg, M/8)
    assert_bracket(uninformative.maximum_bracket_kg, M/2)


def test_response_error_outer_nonempty_inner_empty_is_not_incompatibility():
    band = ('a', np.array([.5, .25, 0.]), np.full(3, .125), M/4, M/4)
    r = exact_query([band], error=np.full(3, .0625))
    assert r.compatibility == 'UNRESOLVED'
    assert r.bounds == 'NUMERICALLY_UNRESOLVED'
    assert r.outer_interval_kg[0] < M/4 and r.outer_interval_kg[1] > 5*M/16
    # A nominally impossible band can be compatible with an uncertain response.
    r = exact_query([('a', np.full(3, .25), np.full(3, .125), .3*M, .3*M)])
    assert r.compatibility != 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'


def test_near_contradiction_and_nearly_dependent_rows():
    rows = [('a', np.array([.5, .25, 0.]), np.zeros(3), M/4, M/4),
            ('b', np.array([.5, .25, 0.])+2.**-40, np.zeros(3), M/4, M/4)]
    r = exact_query(rows)
    # The exact rows differ by a positive multiple of total inventory. Solver
    # tolerance may miss it, but no fabricated feasible state may survive.
    assert r.compatibility != 'ESTABLISHED'
    almost = exact_query([('a', np.array([.5, .25, 0.]), np.zeros(3), M/2+2.**-50*M, M)])
    assert almost.compatibility != 'ESTABLISHED'


@pytest.mark.parametrize('status', [1, 2, 4])
def test_solver_limits_and_failures_do_not_become_incompatibility(status):
    with patch.object(pc, 'linprog', return_value=SimpleNamespace(success=False, status=status, nit=7)):
        r = exact_query()
    assert r.compatibility == 'UNRESOLVED' and r.bounds == 'NUMERICALLY_UNRESOLVED'
    assert r.feasibility.solver_status == status and r.feasibility.iterations == 7


def test_bad_duals_and_zero_duals_cannot_hide_extremum_gap():
    original = pc.linprog
    def bad(*a, **kw):
        r = original(*a, **kw); r.ineqlin.marginals[:] = 1.; return r
    with patch.object(pc, 'linprog', side_effect=bad):
        r = exact_query()
    assert r.bounds == 'NUMERICALLY_UNRESOLVED'
    assert all(e.termination == 'DUAL_SIGN_CHECK_FAILED' for e in r.outer_optimizations)
    def loose(*a, **kw):
        r = original(*a, **kw); r.ineqlin.marginals[:] = 0.; return r
    with patch.object(pc, 'linprog', side_effect=loose):
        r = exact_query()
    assert r.bounds == 'NUMERICALLY_UNRESOLVED'
    assert r.minimum_bracket_kg[1]-r.minimum_bracket_kg[0] > M/10


def test_positive_normalized_bound_and_product_underflow_are_visible():
    base = pc._Polytope(np.zeros(2), np.array([1e-280, 1e280]), np.ones((1, 2)),
                       np.array([1e280]), 1e280, ('total',))
    e = pc._solve(base, np.ones(2), se.FVEnvelopeSettings())
    assert e.status == 'UNRESOLVED' and e.calls == 0
    assert e.termination == 'UNREPRESENTABLE_LP_SCALING'
    with pytest.raises(RuntimeError, match='UNREPRESENTABLE'):
        pc._dotq([1e-300], [1e-300])
    with pytest.raises(RuntimeError, match='UNREPRESENTABLE'):
        pc._coefficient_bounds([1e308], [1e308])


def fixed_query(n=4, *, singleton_set=False, zero=False, epsilon=1e-9, band=None, settings=None):
    p = plan(n=n)
    s = state(n=n, concentrations=np.zeros((3, n)) if zero else None)
    u = singleton(s) if singleton_set or zero else se.FVChemicalStateSet(
        state(n=n, concentrations=np.zeros((3, n))), s, (0., 2*s.inventory_kg), 'SYNTHETIC_BOX')
    early = se.build_delivery_response(p, solute='caffeine', window_s=(7.013, 7.051),
        settings=settings or se.FVEnvelopeSettings())
    future = se.build_delivery_response(p, solute='caffeine', window_s=(7.051, 7.104))
    obs = pc.FVFractionObservation('early', early, band or (0., u.inventory_scale_kg), 'SYNTHETIC_KG_BAND')
    conditioned = pc.condition_on_fractions(u, p, [obs])
    return pc.bound_future_delivery(conditioned, future, epsilon_kg=epsilon)


def test_empty_observations_exactly_delegate_bounds_and_replay_including_failure():
    p, u = plan(), singleton(state())
    target = se.build_delivery_response(p, solute='caffeine', window_s=(7.05, 7.11))
    c = pc.condition_on_fractions(u, p, [])
    with patch.object(se, 'build_delivery_response', side_effect=AssertionError('duplicate propagation')):
        a = pc.bound_future_delivery(c, target, epsilon_kg=1e-9)
        b = se.bound_delivery(u, target, epsilon_kg=1e-9)
    assert isinstance(a, se.FVEnvelopeResult) and a.to_json() == b.to_json()
    assert pc.replay_conditioned_extrema(a).to_json() == se.replay_extrema(b).to_json()
    with patch.object(se, 'linprog', return_value=SimpleNamespace(success=False, status=1, nit=1)):
        a = pc.bound_future_delivery(c, target, epsilon_kg=1e-9)
        b = se.bound_delivery(u, target, epsilon_kg=1e-9)
    assert a.to_json() == b.to_json() and a.numerical_status == 'NUMERICALLY_UNRESOLVED'


@pytest.mark.parametrize('n', [1, 4, 12])
def test_fixed_api_batched_off_grid_replays_and_independent_dense_reference(n):
    result = fixed_query(n=n)
    before = result.target.plan.primary_steps.copy()
    result = pc.replay_conditioned_extrema(result)
    assert result.bounds == 'QUALIFIED', result.termination
    assert result.compatibility == 'ESTABLISHED' and result.forward_calls == 2
    np.testing.assert_array_equal(before, result.target.plan.primary_steps)
    g, cap = dense_response(result.target.plan, result.target.window_s)
    u = result.conditioned_set.original
    for e in (result.minimum, result.maximum):
        w = e.witness
        assert w.final_residuals.feasible and w.original_set_residuals.feasible
        assert all(r.contained and r.status == 'CHECKED' for r in w.replay.windows)
        assert len(w.replay.windows) == 2 and w.replay.parent_accuracy == 'NOT_ASSESSED'
        q = float(np.dot(g, w.masses_kg))
        assert abs(q-w.replay.windows[-1].prediction_kg) <= 1e-11*u.inventory_scale_kg
        for r in w.replay.windows:
            assert abs(r.discrepancy_kg) <= 1e-11*u.inventory_scale_kg
            assert abs(r.discrepancy_kg) <= r.response_allowance_kg+r.forward_allowance_kg


def test_singleton_zero_and_positive_observation_against_zero():
    zero = pc.replay_conditioned_extrema(fixed_query(zero=True))
    assert zero.bounds == 'QUALIFIED' and zero.conditioned_outer_interval_kg == (0., 0.)
    assert zero.relative_width_reduction is None
    assert zero.minimum.gap_kg == zero.maximum.gap_kg == 0.
    contradiction = fixed_query(zero=True, band=(1e-20, 2e-20))
    assert contradiction.compatibility == 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'
    assert contradiction.conservation.status == 'CONSERVATION_CONTRADICTION'
    single = pc.replay_conditioned_extrema(fixed_query(singleton_set=True))
    assert single.compatibility == 'ESTABLISHED' and single.bounds == 'QUALIFIED'


def test_failed_response_replay_and_subresolution_epsilon_stay_unresolved():
    failed = fixed_query(settings=se.FVEnvelopeSettings(max_exponential_actions=1))
    assert failed.bounds == 'NUMERICALLY_UNRESOLVED' and failed.compatibility == 'UNRESOLVED'
    with patch.object(sf, 'simulate_stateful_fv', side_effect=ValueError('injected failure')):
        failed = pc.replay_conditioned_extrema(fixed_query())
    assert failed.bounds == 'NUMERICALLY_UNRESOLVED' and failed.compatibility == 'UNRESOLVED'
    tiny = pc.replay_conditioned_extrema(fixed_query(singleton_set=True, epsilon=1e-30))
    assert tiny.compatibility == 'ESTABLISHED' and tiny.bounds == 'NUMERICALLY_UNRESOLVED'
    assert tiny.minimum.gap_kg > 1e-30


def test_conservation_does_not_double_count_overlap_or_duplicates():
    r = pc.conservation_bound(M, [('a', (0, 2), (.2*M, .3*M)),
        ('b', (1, 3), (.3*M, .4*M)), ('c', (3, 4), (.1*M, .2*M)),
        ('d', (1, 3), (.3*M, .4*M))])
    assert set(r.selected_labels) == {'b', 'c'}
    assert r.interval_kg[1] >= .6*M and r.interval_kg[1] <= np.nextafter(.6*M, np.inf)
    bad = pc.conservation_bound(M, [('a', (0, 1), (M, M)), ('b', (1, 2), (M, M))])
    assert bad.status == 'CONSERVATION_CONTRADICTION' and bad.interval_kg[1] == -M


@pytest.mark.parametrize('bad', [True, '1', 1+2j, float('nan'), float('inf'), -1., Fraction(1, 10**400)])
def test_malformed_mass_bands_and_epsilon_are_input_errors(bad):
    result = fixed_query()
    obs = result.conditioned_set.observations[0]
    with pytest.raises(ValueError): replace(obs, mass_interval_kg=(bad, 1.))
    with pytest.raises(ValueError): pc.bound_future_delivery(result.conditioned_set, result.target, epsilon_kg=bad)


def test_chronology_identity_count_labels_immutability_and_strict_json():
    r = fixed_query()
    c, target = r.conditioned_set, r.target
    with pytest.raises(ValueError, match='CONDITIONING'):
        pc.bound_future_delivery(c, c.observations[0].response, epsilon_kg=1e-9)
    other = se.build_delivery_response(plan(n=3), solute='caffeine', window_s=(7.051, 7.104))
    with pytest.raises(ValueError): pc.bound_future_delivery(c, other, epsilon_kg=1e-9)
    obs = c.observations[0]
    with pytest.raises(ValueError): replace(obs, mass_interval_kg=(1., 0.))
    with pytest.raises(ValueError): replace(obs, label='')
    with pytest.raises(ValueError): pc.condition_on_fractions(c.original, c.plan, [obs]*33)
    with pytest.raises(ValueError): pc.condition_on_fractions(c.original, c.plan, [obs, obs])
    with pytest.raises(ValueError): pc.condition_on_fractions(c.original, c.plan, iter([obs]))
    with pytest.raises(FrozenInstanceError): c.observations = ()
    with pytest.raises(ValueError): r.core.outer.A.setflags(write=True)
    text = r.to_json()
    assert text == r.to_json() and 'elapsed_wall_s' not in text
    json.loads(text, parse_constant=lambda x: pytest.fail(x))
    assert 'sha256' in text and 'row_violations_kg' in text
    json.loads(r.to_json(include_arrays=True, include_timing=True))


def test_old_inventory_repair_does_not_certify_observation_feasibility():
    r = fixed_query()
    u = r.conditioned_set.original
    # Narrow the early band around zero; an inventory-feasible upper-box state
    # violates it. Reconstruction itself must reject, with all rows visible.
    band = ('zero', r.conditioned_set.observations[0].response.weights,
            r.conditioned_set.observations[0].response.coefficient_allowances, 0., 0.)
    inner = pc._intersect(pc._base_polytope(u), [band], inner=True)
    w = pc._reconstruct(u, inner, u.upper_masses_kg, r.target)
    assert w.status == 'UNRESOLVED'
    assert w.original_set_residuals.feasible and not w.final_residuals.feasible
    assert 'JOINT_CONSTRAINTS' in w.termination


def test_public_observation_reordering_and_duplicate_windows_keep_all_rows():
    r = fixed_query()
    c = r.conditioned_set
    obs = c.observations[0]
    second = replace(obs, label='second')
    a = pc.condition_on_fractions(c.original, c.plan, [obs, second])
    b = pc.condition_on_fractions(c.original, c.plan, [second, obs])
    assert a.identity_sha256 == b.identity_sha256
    qa = pc.bound_future_delivery(a, r.target, epsilon_kg=1e-9)
    qb = pc.bound_future_delivery(b, r.target, epsilon_kg=1e-9)
    assert qa.to_json() == qb.to_json()
    assert len(qa.core.outer.b) == len(pc._base_polytope(c.original).b)+4
    assert len(qa.conservation.selected_labels) <= 1


def test_all_model_clock_source_and_plan_mismatches_are_input_errors():
    r = fixed_query()
    c = r.conditioned_set
    for other in (singleton(state(n=3)), singleton(state(species='tds')),
                  singleton(state(grind=1.4)), singleton(state(origin=0.))):
        with pytest.raises(ValueError): pc.condition_on_fractions(other, c.plan, c.observations)
    other_plan = sf.FVPlan(c.plan.temperature_history, c.plan.flow_history,
                          c.plan.t_span_s, sf.FVSettings(cells=4, h_max_s=.01))
    with pytest.raises(ValueError): pc.condition_on_fractions(c.original, other_plan, c.observations)
    with pytest.raises(ValueError): replace(c, algorithm_source_sha256='stale').validate()
    with pytest.raises(ValueError): replace(r.target.model, source_identities=())
    with pytest.raises(ValueError): replace(r.target.model, units_and_bases=())
    with pytest.raises(ValueError): replace(r.target, algorithm_source_sha256='stale').validate()
    zero_window = se.build_delivery_response(c.plan, solute='caffeine', window_s=(7.1, 7.1))
    with pytest.raises(ValueError): pc.bound_future_delivery(c, zero_window, epsilon_kg=1e-9)
    with pytest.raises(ValueError): pc.FVFractionObservation('zero', zero_window, (0, 0), 'synthetic')


def test_replay_overlap_alone_cannot_certify_compatibility():
    r = fixed_query(singleton_set=True)
    original = sf.simulate_stateful_fv
    def misplaced(**kw):
        f = original(**kw)
        early = replace(f.fractions[0], solute_kg=r.conditioned_set.observations[0].mass_interval_kg[1])
        return replace(f, fractions=(early, *f.fractions[1:]))
    with patch.object(sf, 'simulate_stateful_fv', side_effect=misplaced):
        failed = pc.replay_conditioned_extrema(r)
    assert failed.compatibility == 'UNRESOLVED'
    assert all(e.witness.replay.status == 'UNRESOLVED' for e in (failed.minimum, failed.maximum))


def test_injected_elapsed_lp_limit_is_reported_independently_of_success():
    with patch.object(pc.time, 'monotonic', side_effect=[0., 31., 31.]):
        e = pc._solve(simplex(), np.array([.5, .25, .125]), se.FVEnvelopeSettings())
    assert e.status == 'UNRESOLVED' and e.termination == 'LP_WALL_LIMIT'


def test_coefficient_and_allowance_products_cannot_underflow_silently():
    tiny = pc._Polytope(np.array([1e-300]), np.array([1e-300]), np.ones((1, 1)),
                        np.array([1e-300]), 1e-300, ('inventory',))
    e = pc._solve(tiny, np.array([1e-300]), se.FVEnvelopeSettings())
    assert e.status == 'UNRESOLVED' and 'UNREPRESENTABLE' in e.termination
    with pytest.raises(RuntimeError, match='UNREPRESENTABLE'):
        pc._dotq([1e-100], [1e-300])


def test_bounded_box_projection_is_only_accepted_after_all_joint_rows():
    r = fixed_query(singleton_set=True)
    u, inner = r.conditioned_set.original, r.core.inner
    raw = u.lower_masses_kg.copy()
    raw[::2] = np.nextafter(raw[::2], np.inf)
    raw[1::2] = np.nextafter(raw[1::2], 0.)
    evidence = pc._LPEvidence(inner, r.target.weights, raw_masses_kg=raw)
    with patch.object(pc, 'linprog', side_effect=AssertionError('projection needs no LP')):
        w = pc._candidate(u, inner, evidence, r.target)
    assert w.status == 'CHECKED_REPLAY_REQUIRED'
    assert w.repair_method == 'BOUNDED_BOX_PROJECTION_ALL_JOINT_ROWS_RECHECKED'
    assert w.final_residuals.feasible and w.original_set_residuals.feasible
    assert not w.raw_residuals.feasible and w.mass_change_kg > 0
    # A box-feasible point whose observation is incompatible is still rejected.
    bad_inner = pc._intersect(pc._base_polytope(u), [('zero',
        r.conditioned_set.observations[0].response.weights, np.zeros(len(raw)), 0., 0.)], inner=True)
    with patch.object(pc, 'linprog', return_value=SimpleNamespace(success=False, status=2, nit=0)):
        bad = pc._candidate(u, bad_inner, evidence, r.target)
    assert bad.status == 'UNRESOLVED'


def test_search_reserve_is_not_confused_with_actual_sufficient_constraints():
    bands = [('a', np.array([.5, .25, 0.]), np.zeros(3), M/8, 3*M/8)]
    search = [('a', np.array([.5, .25, 0.]), np.full(3, .01), M/8, 3*M/8)]
    r = pc._query_core(simplex(), bands, np.array([.5, .25, .125]), np.zeros(3), M/10,
                       search_bands=search)
    mass = np.array([0., M/2, M/2])
    assert pc._residuals(r.inner, mass).feasible
    assert not pc._residuals(r.search, mass).feasible
    assert not np.array_equal(r.inner.A, r.search.A)

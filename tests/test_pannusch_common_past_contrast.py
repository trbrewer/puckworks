"""007 independent exact/manufactured and native N<=12 capability verification."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import json
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from puckworks.models.pannusch2024 import common_past_contrast as cc, prefix_conditioned as pc, state_envelope as se, stateful_fv as sf
from test_pannusch_state_envelope import state, singleton, dense_response

M = 2.**-10


def simplex(m=M):
    return pc._Polytope(np.zeros(3), np.full(3, m), np.array([[1., 1., 1.], [-1., -1., -1.]]),
                       np.array([m, -m]), m, ('total:upper', 'total:lower'))


def manufactured(m=M, bands=None, error=0., reverse=False, epsilon=None):
    ga, gb = np.array([.125, .5, .125]), np.array([.375, .375, 0.])
    if reverse:
        ga, gb = gb, ga
    d, a, _ = cc._signed_coefficients(ga, np.full(3, error), gb, np.full(3, error))
    if bands is None:
        bands = [('early', np.array([.5, 0., 0.]), np.zeros(3), m/4, 3*m/8)]
    return pc._query_core(simplex(m), bands, d, a, m*1e-10 if epsilon is None else epsilon)


def plans(n=4, h=.02, end=7.2, kind='linear'):
    knots = (7., 7.1, end)
    ts = ((90, 90, 86), (90, 90, 94)) if kind == 'linear' else ((90, 86), (90, 94))
    ctor = sf.TemperatureHistory.linear_celsius if kind == 'linear' else sf.TemperatureHistory.constant_celsius
    return tuple(sf.FVPlan(ctor(knots, t), sf.FlowHistory(knots, q, 'constant'), (7., end),
                          sf.FVSettings(cells=n, h_max_s=h))
                 for t, q in zip(ts, ((2e-6, 1.5e-6), (2e-6, 2.5e-6))))


def inputs(n=4, observations=True, identical=False, kind='linear', delayed=False):
    pa, pb = plans(n=n, kind=kind)
    if identical:
        pb = pa
    s = state(n=n)
    # Multiple states, no arbitrary exact equality between rounded sums.
    lo = state(n=n, concentrations=se._concentrations(s).reshape(3, n)*.5)
    u = se.FVChemicalStateSet(lo, s, (0., 2*s.inventory_kg), 'SYNTHETIC_NOT_A_COFFEE_PRIOR')
    window = (7.13 if delayed else 7.1, 7.2)
    a, b = (se.build_delivery_response(p, solute='caffeine', window_s=window) for p in (pa, pb))
    early = se.build_delivery_response(pa, solute='caffeine', window_s=(7., 7.1))
    obs = (pc.FVFractionObservation('early', early, (0., u.inventory_scale_kg), 'SYNTHETIC_BAND'),) if observations else ()
    return pc.condition_on_fractions(u, pa, obs), a, b


def query(c=None, a=None, b=None, **kwargs):
    if c is None:
        c, a, b = inputs()
    options = dict(branch_time_s=7.1, epsilon_kg=1e-9, delta_kg=1e-6, comparison_basis='EXPLICIT_UNEQUAL_VOLUME')
    options.update(kwargs)
    return cc.bound_common_past_contrast(c, a, b, **options)


def test_new_rational_vertex_oracle_not_optimizer_and_marginal_overlap():
    m = F(1, 1024)
    ga, gb = (F(1, 8), F(1, 2), F(1, 8)), (F(3, 8), F(3, 8), F(0))
    vertices = [(t*m, s*(1-t)*m, (1-s)*(1-t)*m) for t in (F(1, 2), F(3, 4)) for s in (0, 1)]
    dot = lambda g, v: sum(x*y for x, y in zip(g, v))
    da, db = [dot(ga, v) for v in vertices], [dot(gb, v) for v in vertices]
    dd = [b-a for a, b in zip(da, db)]
    assert (min(da), max(da)) == (m/8, 5*m/16)
    assert (min(db), max(db)) == (3*m/16, 3*m/8)
    assert (min(dd), max(dd)) == (m/16, 5*m/32)
    assert max(min(da), min(db)) < min(max(da), max(db))
    assert min(db)-max(da) == -m/8 < m/32 < min(dd)
    d = [y-x for x, y in zip(ga, gb)]
    assert (min(d)*m, max(d)*m) == (-m/8, m/4)
    for r, expected in ((manufactured(), (M/16, 5*M/32)), (manufactured(bands=[]), (-M/8, M/4))):
        assert r.bounds == 'QUALIFIED'
        for bracket, value in zip((r.minimum_bracket_kg, r.maximum_bracket_kg), expected):
            assert bracket[0] <= value <= bracket[1]
            assert bracket[1]-bracket[0] <= 1e-10*M
    for g, expected in ((ga, (M/8, 5*M/16)), (gb, (3*M/16, 3*M/8))):
        r = pc._query_core(simplex(), [('e', np.array([.5, 0., 0.]), np.zeros(3), M/4, 3*M/8)],
                           np.array(g, dtype=float), np.zeros(3), M*1e-10)
        np.testing.assert_allclose(r.outer_interval_kg, expected, atol=1e-10*M, rtol=0.)
    assert cc._decision((M/16, 5*M/32), M/32, (), True)[0] == 'B_UNIFORMLY_EXCEEDS_A_BY_MARGIN'
    assert cc._decision((-5*M/32, -M/16), M/32, (), True)[0] == 'A_UNIFORMLY_EXCEEDS_B_BY_MARGIN'


@pytest.mark.parametrize('m', [M, 2.**-500, 2.**-900])
def test_signed_scaling_antisymmetry_and_negative_bounds(m):
    x, y = manufactured(m), manufactured(m, reverse=True)
    assert x.bounds == y.bounds == 'QUALIFIED'
    assert x.outer_interval_kg == tuple(-v for v in reversed(y.outer_interval_kg))
    assert y.outer_interval_kg[1] < 0


def test_nonzero_allowances_near_cancellation_and_outward_binary_difference():
    ga = np.array([1., .1, 2.**-100])
    gb = np.nextafter(ga, np.inf)
    aa = np.full(3, 1e-10)
    d, a, conversion = cc._signed_coefficients(ga, aa, gb, aa)
    for i in range(3):
        exact = F(float(gb[i]))-F(float(ga[i]))
        assert F(float(a[i])) >= 2*F(float(aa[i]))+abs(F(float(d[i]))-exact)
        assert a[i] >= 2e-10 and conversion[i] >= 0
    r = manufactured(error=.01)
    assert r.outer_interval_kg[0] < M/16 and r.outer_interval_kg[1] > 5*M/32
    assert r.bounds == 'NUMERICALLY_UNRESOLVED'
    with pytest.raises(RuntimeError, match='UNREPRESENTABLE'):
        pc._product(np.nextafter(0., 1.), .25)
    poly = replace(simplex(2.**-1020), scale_kg=1e300)
    e = pc._solve(poly, np.ones(3), se.FVEnvelopeSettings())
    assert e.status == 'UNRESOLVED' and 'SCALING' in e.termination


def test_joint_contradiction_and_empty_sufficient_inner_are_distinct():
    bands = [('one', np.array([.5, 0, 0]), np.zeros(3), 3*M/8, M/2),
             ('two', np.array([0, .5, 0]), np.zeros(3), 3*M/8, M/2)]
    assert all(manufactured(bands=[b]).compatibility == 'ESTABLISHED' for b in bands)
    r = manufactured(bands=bands)
    assert r.compatibility == 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'
    assert r.feasibility.checked_dual_lower_kg > 0
    bands = [('e', np.array([.5, 0., 0.]), np.full(3, .125), M/4, M/4)]
    r = manufactured(bands=bands)
    assert r.compatibility == 'UNRESOLVED' and r.bounds == 'NUMERICALLY_UNRESOLVED'
    with patch.object(pc, 'linprog', return_value=SimpleNamespace(success=False, status=2, nit=0)):
        r = manufactured()
    assert r.compatibility == 'UNRESOLVED' and r.bounds == 'NUMERICALLY_UNRESOLVED'
    with pytest.raises(RuntimeError, match='DUAL'):
        pc._weak_dual(simplex(), np.ones(3), np.ones(2))


@pytest.mark.parametrize('kind', ['linear', 'constant'])
@pytest.mark.parametrize('delayed', [False, True])
def test_common_past_jump_and_delayed_target_same_state_replays(kind, delayed):
    c, a, b = inputs(kind=kind, delayed=delayed)
    r = cc.replay_common_past_extrema(query(c, a, b))
    assert r.bounds == 'QUALIFIED', r.to_json()
    assert r.compatibility == 'ESTABLISHED' and r.forward_calls == 4
    assert r.receipt.orientation == 'B_MINUS_A'
    for e in (r.minimum, r.maximum):
        w = e.witness
        assert w.status == 'COMPATIBLE' and w.final_residuals.feasible
        p = w.replay
        assert p.prefix_bitwise_equal and p.maximum_prefix_mass_discrepancy_kg == 0
        assert p.prefix_trace_identities[0] == p.prefix_trace_identities[1]
        assert p.branch_state_identities[0] == p.branch_state_identities[1]
        assert p.prefix_deliveries_kg[0] == p.prefix_deliveries_kg[1]
        assert all(row.contained for branch in (p.branch_a, p.branch_b) for row in branch.windows)
        assert p.combined_interval_kg[0] <= p.forward_difference_kg <= p.combined_interval_kg[1]
        assert 0 <= e.gap_kg <= r.epsilon_kg
        assert p.branch_a.state_identity == p.branch_b.state_identity == w.state.identity_sha256


def test_native_dense_reference_signed_prediction_and_both_plan_local_fraction():
    c, a, b = inputs(n=3, delayed=True)
    refs = [dense_response(r.plan, r.window_s)[0] for r in (a, b)]
    for r, reference in zip((a, b), refs):
        assert np.all(np.abs(r.weights-reference) <= r.coefficient_allowances)
        assert np.max(np.abs(r.weights-reference)) <= 1e-11
    r = cc.replay_common_past_extrema(query(c, a, b))
    for e in (r.minimum, r.maximum):
        m = e.witness.masses_kg
        expected = pc._dotq(refs[1]-refs[0], m)
        actual = e.witness.replay.forward_difference_kg
        assert abs(float(expected)-actual) <= 1e-11*c.original.inventory_scale_kg


def test_empty_native_uses_reversed_005_evidence_and_exchange():
    c, a, b = inputs(observations=False)
    with patch.object(se, 'contrast_deliveries', wraps=se.contrast_deliveries) as call:
        r = query(c, a, b)
    assert call.call_args.args == (c.original, b, a)
    legacy = se.contrast_deliveries(c.original, b, a, epsilon_kg=1e-9, delta_kg=1e-6,
                                   comparison_basis='EXPLICIT_UNEQUAL_VOLUME')
    assert r.outer_interval_kg == legacy.outer_delivery_interval_kg
    assert r.optimization_calls == legacy.optimization_calls
    r = cc.replay_common_past_extrema(r)
    assert r.bounds == 'QUALIFIED', r.to_json()
    assert r.legacy_b_a.numerical_status == 'NUMERICALLY_QUALIFIED'
    swapped = cc.replay_common_past_extrema(query(pc.condition_on_fractions(c.original, b.plan, ()), b, a))
    assert np.allclose(r.outer_interval_kg, [-v for v in swapped.outer_interval_kg[::-1]], atol=1e-18, rtol=0)
    assert r.forward_calls == swapped.forward_calls == 4
    for e in (r.minimum, r.maximum):
        assert tuple(x.response_identity for x in e.witness.replay.legacy_receipts_b_a) == (b.identity_sha256, a.identity_sha256)
    # Existing 006 guard is unchanged, including for an otherwise valid common past.
    with pytest.raises(ValueError, match='TARGET_PLAN_MISMATCH'):
        pc.bound_future_delivery(c, b, epsilon_kg=1e-9)


@pytest.mark.parametrize('mode', ['compatible', 'contradictory', 'unresolved'])
def test_structural_exact_zero_preserves_compatibility(mode):
    c, a, b = inputs(identical=True)
    if mode != 'compatible':
        obs = c.observations[0]
        band = (2*c.original.inventory_scale_kg, 3*c.original.inventory_scale_kg) if mode == 'contradictory' else (0., 0.)
        c = pc.condition_on_fractions(c.original, c.plan, (replace(obs, mass_interval_kg=band),))
    r = cc.replay_common_past_extrema(query(c, a, b))
    assert r.receipt.exact_zero
    if mode == 'compatible':
        assert r.bounds == 'QUALIFIED' and r.outer_interval_kg == (0., 0.)
        assert r.decision == 'NO_MATERIAL_DIFFERENCE'
        assert r.minimum.gap_kg == r.maximum.gap_kg == 0
    else:
        assert r.bounds != 'QUALIFIED' and r.decision != 'NO_MATERIAL_DIFFERENCE'
        if mode == 'contradictory':
            assert r.compatibility == 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'


def test_zero_inventory_and_tiny_native_inventory():
    c, a, b = inputs(n=1)
    for scale in (0., 2.**-800):
        s = state(n=1, concentrations=np.full((3, 1), scale))
        u = singleton(s)
        obs = replace(c.observations[0], mass_interval_kg=(0., 2*s.inventory_kg))
        r = cc.replay_common_past_extrema(query(pc.condition_on_fractions(u, c.plan, (obs,)), a, b))
        assert r.bounds == 'QUALIFIED', r.to_json()
        if not scale:
            assert r.outer_interval_kg == (0., 0.)


@pytest.mark.parametrize('value', [True, float('nan'), float('inf'), -1.])
def test_invalid_scalars_before_optimizer(value):
    c, a, b = inputs()
    with patch.object(pc, 'linprog', side_effect=AssertionError('must not allocate LP')):
        with pytest.raises(ValueError):
            query(c, a, b, epsilon_kg=value)
        with pytest.raises(ValueError):
            query(c, a, b, delta_kg=value)
    with pytest.raises(ValueError):
        query(c, a, b, epsilon_kg=0.)


def test_reject_changed_history_interpolation_and_partition():
    c, a, b = inputs()
    bad = sf.FVPlan(sf.TemperatureHistory.linear_celsius((7., 7.1, 7.2), (89, 90, 94)),
                   b.plan.flow_history, b.plan.t_span_s, b.plan.settings)
    br = se.build_delivery_response(bad, solute='caffeine', window_s=b.window_s)
    with pytest.raises(ValueError, match='CHANGED_PRESCRIBED_PAST'):
        query(c, a, br)
    # Both branch times are primary boundaries, but the future affine endpoint
    # changes the executed past even though initial endpoint values agree.
    ps = [sf.FVPlan(sf.TemperatureHistory.linear_celsius((7., 7.2), (90, t)),
        sf.FlowHistory((7., 7.2), (2e-6,), 'constant'), (7., 7.2), sf.FVSettings(cells=4, h_max_s=.0251)) for t in (90, 94)]
    rs = [se.build_delivery_response(p, solute='caffeine', window_s=(7.1, 7.2)) for p in ps]
    with pytest.raises(ValueError, match='INTERPOLATION_LEAKAGE'):
        query(pc.condition_on_fractions(c.original, ps[0], ()), *rs)
    bad = sf.FVPlan(sf.TemperatureHistory.constant_celsius((7., 7.05, 7.1, 7.2), (90, 90, 94)),
                   b.plan.flow_history, b.plan.t_span_s, b.plan.settings)
    br = se.build_delivery_response(bad, solute='caffeine', window_s=b.window_s)
    with pytest.raises(ValueError, match='REPRESENTATION_OR_PARTITION'):
        query(c, a, br)


def test_invalid_branch_window_model_settings_clock_and_observation():
    c, a, b = inputs()
    for t, reason in ((7., 'STRICTLY_INSIDE'), (7.107, 'OFF_GRID'), (7.2, 'STRICTLY_INSIDE')):
        with pytest.raises(ValueError, match=reason): query(c, a, b, branch_time_s=t)
    for changed in (replace(b.plan, settings=sf.FVSettings(cells=5)),):
        br = se.build_delivery_response(changed, solute='caffeine', window_s=b.window_s)
        with pytest.raises(ValueError): query(c, a, br)
    for kw in (dict(solute='trigonelline'), dict(solute='caffeine', grind=1.4),
               dict(solute='caffeine', settings=se.FVEnvelopeSettings(max_steps=100)),
               dict(solute='caffeine', window_s=(7.11, 7.2))):
        options = dict(solute='caffeine', window_s=b.window_s); options.update(kw)
        br = se.build_delivery_response(b.plan, **options)
        with pytest.raises(ValueError): query(c, a, br)
    early = se.build_delivery_response(a.plan, solute='caffeine', window_s=(7., 7.11))
    obs = replace(c.observations[0], response=early)
    with pytest.raises(ValueError, match='BEYOND_BRANCH'):
        query(pc.condition_on_fractions(c.original, a.plan, (obs,)), a, b)
    with pytest.raises(ValueError, match='CONDITIONING_PLAN_A'):
        query(c, b, a)
    with pytest.raises(ValueError, match='VOLUMES_DO_NOT_MATCH'):
        query(c, a, b, comparison_basis='MATCHED_COLLECTED_VOLUME')


def test_duplicate_correlated_overlapping_observations_and_deterministic_serialization():
    c, a, b = inputs()
    one = c.observations[0]
    two = replace(one, label='duplicate')
    overlap = replace(one, label='overlap', response=se.build_delivery_response(a.plan, solute='caffeine', window_s=(7.02, 7.09)))
    x = pc.condition_on_fractions(c.original, c.plan, (one, two, overlap))
    y = pc.condition_on_fractions(c.original, c.plan, (overlap, two, one))
    assert x.identity_sha256 == y.identity_sha256
    r, s = query(x, a, b), query(y, a, b)
    assert r.to_json() == s.to_json()
    assert len(r.core.inner.b) == len(pc._base_polytope(c.original).b)+6
    json.loads(r.to_json())
    with pytest.raises(FrozenInstanceError): r.receipt.branch_time_s = 8.
    with pytest.raises(ValueError): r.objective.weights.setflags(write=True)
    with pytest.raises(ValueError): r.core.inner.A.setflags(write=True)
    changed = replace(r.objective.response_a, elapsed_wall_s=999.)
    assert changed.identity_sha256 == a.identity_sha256


def test_failed_response_solver_reconstruction_replay_and_small_gap_never_qualify():
    c, a, b = inputs()
    failed = se.build_delivery_response(b.plan, solute='caffeine', window_s=b.window_s,
        settings=se.FVEnvelopeSettings(max_exponential_actions=1))
    fa = se.build_delivery_response(a.plan, solute='caffeine', window_s=a.window_s, settings=failed.settings)
    empty = pc.condition_on_fractions(c.original, a.plan, ())
    r = query(empty, fa, failed)
    assert r.fallback == 'SIGNED_INVENTORY_ONLY' and r.bounds != 'QUALIFIED'
    with patch.object(pc, '_candidate', return_value=None):
        r = cc.replay_common_past_extrema(query(c, a, b))
    assert r.compatibility == 'UNRESOLVED'
    r = query(c, a, b)
    with patch.object(sf, 'simulate_stateful_fv', side_effect=RuntimeError('INJECTED_FAILURE')):
        failed = cc.replay_common_past_extrema(r)
    assert failed.compatibility == 'UNRESOLVED' and failed.forward_calls == 2
    assert failed.minimum.witness.replay.termination == 'INJECTED_FAILURE'
    narrow = cc.replay_common_past_extrema(query(c, a, b, epsilon_kg=1e-30))
    assert narrow.bounds == 'NUMERICALLY_UNRESOLVED'
    assert narrow.compatibility == 'ESTABLISHED'


def test_opposite_sign_and_material_reversal_are_separate():
    decision, opposite, reversal = cc._decision((-.5, .5), 1., [(-.4, -.3), (.3, .4)], True)
    assert decision == 'NO_MATERIAL_DIFFERENCE' and opposite and not reversal
    assert cc._decision((-2., 2.), 1., [], True) == ('NO_UNIFORM_MATERIAL_CONCLUSION', False, False)
    assert cc._decision((-2., 2.), 1., [(-2., -1.1), (1.1, 2.)], True) == ('DEMONSTRATED_MATERIAL_REVERSAL', True, True)


def test_exact_zero_unresolved_band_is_not_vacuous_equivalence():
    c, a, b = inputs(identical=True)
    u = singleton(c.original.upper)
    obs = c.observations[0]
    mass = se._concentrations(u.upper)*u.capacities_m3
    value = pc._rounded(pc._dotq(obs.response.weights, mass))
    c = pc.condition_on_fractions(u, c.plan, (replace(obs, mass_interval_kg=(value, value)),))
    r = cc.replay_common_past_extrema(query(c, a, b))
    assert r.receipt.exact_zero and r.core.outer_interval_kg == (0., 0.)
    assert r.compatibility == 'UNRESOLVED' and r.bounds != 'QUALIFIED'
    assert r.decision == 'NUMERICALLY_UNRESOLVED'


def test_small_difference_never_structurally_zero_and_legacy_gap_not_promoted():
    c, a, b = inputs(observations=False, identical=True)
    q = b.plan.flow_history
    future = np.nextafter(q.flows_m3_s[-1], np.inf)
    p = replace(b.plan, flow_history=sf.FlowHistory(q.times_s, (q.flows_m3_s[0], future), q.kind))
    b = se.build_delivery_response(p, solute='caffeine', window_s=b.window_s)
    r = query(c, a, b)
    assert not r.receipt.exact_zero and np.all(r.objective.coefficient_allowances > 0)
    # Preserve a legacy certificate independently when a stricter replay-inclusive
    # 007 gap cannot satisfy epsilon, without declaring failure of legacy software.
    r = cc.replay_common_past_extrema(query(c, a, b, epsilon_kg=1e-30))
    assert r.bounds != 'QUALIFIED'
    assert r.legacy_b_a is not None


def test_bad_duals_and_termination_remain_unresolved_without_physical_incompatibility():
    original = pc.linprog
    def bad(*args, **kwargs):
        result = original(*args, **kwargs)
        if result.success:
            result.ineqlin.marginals[:] = 1.
        return result
    with patch.object(pc, 'linprog', side_effect=bad):
        result = manufactured()
    assert result.bounds != 'QUALIFIED'
    assert result.compatibility != 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'
    assert all(e.status == 'UNRESOLVED' for e in result.outer_optimizations)


def test_nonfinite_boolean_arrays_and_tampered_sources_rejected_before_lp():
    for value in (True, float('nan'), float('inf')):
        with pytest.raises(ValueError):
            cc._signed_coefficients([value], [0.], [0.], [0.])
    c, a, b = inputs()
    object.__setattr__(b.plan.flow_history, 'flows_m3_s', (1e-6, 2e-6))
    with patch.object(pc, 'linprog', side_effect=AssertionError('must reject before LP')):
        with pytest.raises(ValueError, match='IDENTITY'):
            query(c, a, b)


def test_joint_native_duplicate_bands_individually_feasible_together_incompatible():
    c, a, b = inputs()
    o = c.observations[0]
    lower = pc._prediction(o.response, c.original.lower_masses_kg)
    upper = pc._prediction(o.response, c.original.upper_masses_kg)
    gap = (upper[0]-lower[1])/8
    one = replace(o, label='low', mass_interval_kg=(max(0., lower[0]-gap), lower[1]+gap))
    two = replace(o, label='high', mass_interval_kg=(upper[0]-gap, upper[1]+gap))
    assert one.mass_interval_kg[1] < two.mass_interval_kg[0]
    for observation in (one, two):
        r = cc.replay_common_past_extrema(query(pc.condition_on_fractions(c.original, c.plan, (observation,)), a, b))
        assert r.compatibility == 'ESTABLISHED'
    both = query(pc.condition_on_fractions(c.original, c.plan, (one, two)), a, b)
    assert both.compatibility == 'INCOMPATIBLE_UNDER_DECLARED_CONTRACT'


def test_different_compiled_primary_prefix_is_separate_from_history_guard():
    c, a, b = inputs()
    # Isolate the second proof obligation in a test-only validator seam. The
    # production response identities are native and never manufactured.
    p = replace(b.plan, temperature_history=sf.TemperatureHistory.linear_celsius((7., 7.07, 7.1, 7.2), (90, 90, 90, 94)))
    rb = se.build_delivery_response(p, solute='caffeine', window_s=b.window_s)
    with patch.object(cc, '_history_prefix', return_value=('same test seam',)):
        with pytest.raises(ValueError, match='DIFFERENT_ORIGINAL_PRIMARY_PARTITION'):
            query(c, a, rb)


def test_signed_objective_content_cannot_change_under_a_stored_identity():
    r = query()
    object.__setattr__(r.objective, 'weights', r.objective.weights*2)
    with patch.object(sf, 'simulate_stateful_fv', side_effect=AssertionError('validate first')):
        with pytest.raises(ValueError, match='OBJECTIVE_CHANGED'):
            cc.replay_common_past_extrema(r)

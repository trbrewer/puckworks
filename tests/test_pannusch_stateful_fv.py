"""004 small N<=12 analytical/API suite; no task qualification integrations."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import copy
import json
from unittest.mock import patch

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.models.pannusch2024 import stateful_fv as sf
from tools import pannusch_flow_temp_fv_reference as ref


@pytest.mark.parametrize('phase', range(3))
@pytest.mark.parametrize('value,reason', [
    (Fraction(1,10**400), 'UNREPRESENTABLE_PHASE_CONCENTRATION'),
    (Fraction(-1,10**400), 'NEGATIVE_CONCENTRATION')])
def test_original_real_phase_values_cannot_silently_round_to_zero(phase,value,reason):
    phases = np.zeros((3,4),dtype=object)
    phases[phase,0] = value
    assert value != 0 and float(value) == 0
    with pytest.raises(ValueError,match=reason):
        supplied(phases=phases)


def test_extended_precision_underflow_and_representable_rationals():
    tiny = np.finfo(np.longdouble).tiny
    if float(tiny) == 0:
        assert tiny > 0
        with pytest.raises(ValueError,match='UNREPRESENTABLE_PHASE_CONCENTRATION'):
            supplied(phases=np.full((3,4),tiny,dtype=np.longdouble))
    state = supplied(phases=np.full((3,4),Fraction(1,4),dtype=object))
    np.testing.assert_array_equal(state.liquid_cell_average_kg_m3,np.full(4,.25))
    assert state.inventory_kg > 0


S = sf.FVSettings(cells=4)


def plan(kind='constant', **kwargs):
    T = (sf.TemperatureHistory.constant_celsius((0, .033, .11), (80, 98)) if kind == 'constant'
         else sf.TemperatureHistory.linear_celsius((0, .043, .11), (80, 95, 86)))
    Q = sf.FlowHistory((0, .071, .11), (1e-6, 2.7e-6) if kind == 'constant' else (1.2e-6, 2.8e-6, 1.6e-6), kind)
    return sf.FVPlan(T, Q, (0, .11), **dict(settings=S, **kwargs))


def supplied(*, solute='caffeine', grind=1.7, cells=4, time=0., scale=1., phases=None):
    e = np.linspace(0, sf.fv.ps.L, cells+1)
    x = e/sf.fv.ps.L
    avg = (x[:-1]+x[1:])/2
    avg2 = (x[:-1]**2+x[:-1]*x[1:]+x[1:]**2)/3
    C0 = sf.fv.ps._solute_params()[solute]['c_s0']
    c = np.array([.15+.25*avg, .85-.55*avg, .10+.45*avg2])*C0*scale if phases is None else np.asarray(phases)
    return sf.FVChemicalState.from_cell_averages(solute=solute, grind=grind, time_s=time,
        edges_m=e, liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2])


def run(p=None, state=None, **kwargs):
    p = p or plan()
    args = dict(plan=p, observation_times_s=(0, .013, .033, .071, .11),
                fraction_windows_s=((0, .033), (.033, .071), (.071, .11)))
    if 'checkpoint' not in kwargs:
        args['initial_state'] = state or supplied()
    args.update(kwargs)
    return sf.simulate_stateful_fv(**args)


def packed(tr):
    return np.column_stack((tr.liquid_cell_average_kg_m3, tr.fine_cell_average_kg_m3,
                            tr.coarse_cell_average_kg_m3, tr.segment_outlet_solute_kg))


@pytest.mark.parametrize('solute', sf.fv.th.SPECIES)
@pytest.mark.parametrize('grind', (1.4, 1.7, 2.0))
def test_exact_cell_average_inventory_and_independent_ordered_solution(solute, grind):
    state = supplied(solute=solute, grind=grind)
    p = plan()
    r = run(p, state)
    psi = sf.fv.ps.GRINDS[grind]['psi']
    expected_M = sf.fv.ps.ACS*sf.fv.ps.L*sf.fv.ps._solute_params()[solute]['c_s0']*(
        sf.fv.ps.ALPHA_L*.275 + psi*(1-sf.fv.ps.ALPHA_L)*.575 + sf.fv.ps.PHI_V2*(1-psi)*(1-sf.fv.ps.ALPHA_L)*.25)
    assert state.inventory_kg == pytest.approx(expected_M, rel=4e-16)
    assert r.integration_complete and r.status == 'COMPLETE'
    initial = np.r_[state.liquid_cell_average_kg_m3, state.fine_cell_average_kg_m3, state.coarse_cell_average_kg_m3, 0.]
    A = ref.operator_factory(solute, grind, 4)
    y = initial.copy()
    for a, b, ti, qi in ref.segments(p.temperature_history, p.flow_history, (0, .11)):
        B = A(ref.value(p.temperature_history, a, interval=ti), ref.value(p.flow_history, a, interval=qi)).toarray()
        y = expm((b-a)*B)@y
    np.testing.assert_allclose(packed(r.observations)[-1], y, rtol=1e-12, atol=1e-18)
    assert all(r.exportable_primary)


@pytest.mark.parametrize('solute', sf.fv.th.SPECIES)
@pytest.mark.parametrize('kind', ('constant', 'linear'))
def test_genuine_stop_resume_multiple_resume_and_observer_independence(solute, kind):
    p, state = plan(kind), supplied(solute=solute)
    full = run(p, state)
    tc = p.primary_times_s[2]
    prefix = run(p, state, stop_time_s=tc, observation_times_s=(0, tc), fraction_windows_s=((0, tc),))
    assert prefix.propagations == 2 and prefix.status == 'PLANNED_STOP'
    assert prefix.integration_complete and not prefix.planned_horizon_complete
    cp = prefix.checkpoint(tc)
    suffix = run(checkpoint=cp, p=p, observation_times_s=(tc, .11), fraction_windows_s=((tc, .11),))
    np.testing.assert_array_equal(suffix.raw_primary_masses_kg, full.raw_primary_masses_kg[2:])
    np.testing.assert_array_equal(suffix.plan.primary_steps, full.plan.primary_steps)
    assert suffix.primary.origin_outlet_solute_kg[-1] == full.primary.origin_outlet_solute_kg[-1]
    assert suffix.primary.origin_volume_m3[-1] == pytest.approx(full.primary.origin_volume_m3[-1], rel=2e-16)
    tc2 = p.primary_times_s[4]
    second = run(checkpoint=cp, p=p, stop_time_s=tc2, observation_times_s=(tc, tc2), fraction_windows_s=())
    cp2 = second.checkpoint(tc2)
    third = run(checkpoint=cp2, p=p, observation_times_s=(tc2, .11), fraction_windows_s=())
    np.testing.assert_array_equal(third.raw_primary_masses_kg, full.raw_primary_masses_kg[4:])
    other = run(p, state, observation_times_s=(.001, .027, .049, .104), fraction_windows_s=())
    np.testing.assert_array_equal(other.raw_primary_masses_kg, full.raw_primary_masses_kg)
    assert other.plan.identity_sha256 == full.plan.identity_sha256
    assert other.identity_sha256 != full.identity_sha256
    assert cp.identity_sha256 == prefix.checkpoint(tc).identity_sha256


@pytest.mark.parametrize('solute', sf.fv.th.SPECIES)
def test_equilibrium_public_constructor_matches_existing_implicit_api(solute):
    p = plan()
    state = sf.FVChemicalState.source_equilibrium(p.temperature_history, time_s=0., solute=solute, cells=4)
    a = run(p, state)
    b = sf.fv.simulate_flow_temperature_history_fv(p.temperature_history, flow_history=p.flow_history,
        t_span_s=(0, .11), solute=solute, observation_times_s=a.observations.times_s,
        fraction_bounds_s=(0, .033, .071, .11), settings=S)
    np.testing.assert_array_equal(state.liquid_cell_average_kg_m3,
        b.observations.liquid_cell_average_kg_m3[0])
    assert state.liquid_cell_average_kg_m3[0] > 0
    expected = np.column_stack((b.observations.liquid_cell_average_kg_m3,
        b.observations.fine_cell_average_kg_m3, b.observations.coarse_cell_average_kg_m3, b.observations.outlet_solute_kg))
    np.testing.assert_allclose(packed(a.observations), expected, rtol=1e-12, atol=1e-18)
    np.testing.assert_allclose([f.concentration_kg_m3 for f in a.fractions],
                               [f.concentration_kg_m3 for f in b.fractions], rtol=1e-12)


@pytest.mark.parametrize('phases', [np.zeros((3, 4)), np.full((3, 4), 1e-250),
    np.array([[10.]*4, [0.]*4, [0.]*4]), np.array([[1.]*4, [0.]*4, [5.]*4]),
    np.array([[1.]*4, [5.]*4, [0.]*4])])
def test_zero_tiny_positive_depleted_and_reverse_transfer(phases):
    state = supplied(phases=phases)
    r = run(state=state)
    assert r.status == 'COMPLETE' and all(r.exportable_primary)
    for f in r.fractions:
        assert f.concentration_kg_m3 is not None
        assert (f.status == 'VALID_NUMERICAL_ZERO') == (state.inventory_kg == 0)
    if state.inventory_kg == 0:
        assert np.count_nonzero(packed(r.observations)) == 0
    if np.all(phases[1:] == 0) and np.any(phases[0] > 0):
        assert r.primary.fine_cell_average_kg_m3[-1].min() > 0
        assert r.primary.coarse_cell_average_kg_m3[-1].min() > 0
    json.loads(r.to_json(), parse_constant=lambda x: pytest.fail(x))


def test_branch_retains_state_offsets_parent_and_is_reusable():
    p = plan(); tc = p.primary_times_s[2]
    cp = run(p, stop_time_s=tc).checkpoint(tc)
    branch = sf.FVPlan(sf.TemperatureHistory.constant_celsius((tc, .11), (93,)),
                       sf.FlowHistory((tc, .11), (2.2e-6,), 'constant'), (tc, .11), S)
    kw = dict(plan=branch, observation_times_s=(tc, .11), fraction_windows_s=((tc, .11),))
    a = sf.branch_stateful_fv(cp, **kw); b = sf.branch_stateful_fv(cp, **kw)
    assert a.mode == 'BRANCH' and a.parent_identity == cp.identity_sha256
    assert branch.identity_sha256 != p.identity_sha256
    np.testing.assert_array_equal(a.raw_primary_masses_kg[0], cp.raw_masses_kg)
    np.testing.assert_array_equal(a.raw_primary_masses_kg, b.raw_primary_masses_kg)
    assert a.primary.origin_outlet_solute_kg[0] == cp.origin_outlet_solute_kg
    assert a.primary.origin_volume_m3[0] == cp.origin_volume_m3
    with patch.object(sf.fv._System, 'generator', side_effect=AssertionError('no propagation')):
        with pytest.raises(ValueError, match='EXPLICIT_BRANCH'):
            sf.simulate_stateful_fv(checkpoint=cp, **kw)


@pytest.mark.parametrize('change', [dict(liquid_kg_m3=[1.]), dict(fine_kg_m3=None),
    dict(coarse_kg_m3=[[1.]*4]), dict(liquid_kg_m3=[1j]*4), dict(fine_kg_m3=[True]*4),
    dict(coarse_kg_m3=['1']*4), dict(fine_kg_m3=[np.inf]*4), dict(liquid_kg_m3=[-1.]*4),
    dict(edges_m=np.linspace(0, .016, 5)), dict(solute='CGA'), dict(grind=1.8), dict(time_s=True),
    dict(liquid_kg_m3=[np.nextafter(0., 1.)]*4)])
def test_state_input_rejections_before_propagation(change):
    kw = dict(solute='caffeine', grind=1.7, time_s=0, edges_m=np.linspace(0, sf.fv.ps.L, 5),
              liquid_kg_m3=[1.]*4, fine_kg_m3=[2.]*4, coarse_kg_m3=[3.]*4)
    kw.update(change)
    with patch.object(sf.fv._System, 'generator', side_effect=AssertionError('no propagation')):
        with pytest.raises(ValueError): sf.FVChemicalState.from_cell_averages(**kw)


def test_immutability_basis_schema_source_checks_and_no_mutation():
    before = copy.deepcopy((sf.fv.ps.GRINDS, sf.fv.ps._solute_params(), sf.fv.pc.SOLUTES))
    state = supplied(); r = run(state=state); cp = r.checkpoint(r.primary.times_s[2])
    for arr in [state.edges_m, state.fine_cell_average_kg_m3, cp.raw_masses_kg, cp.plan.primary_steps,
                cp.liquid_cell_average_kg_m3, r.raw_primary_masses_kg]:
        with pytest.raises(ValueError): arr.setflags(write=True)
    with pytest.raises(FrozenInstanceError): cp.time_s = 99
    for kw in [dict(schema_version=2), dict(units_and_bases=('wrong',)), dict(source_identities=()), dict(geometry=())]:
        with pytest.raises(ValueError): replace(state, **kw)
    assert before == (sf.fv.ps.GRINDS, sf.fv.ps._solute_params(), sf.fv.pc.SOLUTES)


def test_checked_prefix_resource_failure_and_interior_rejection():
    p = plan()
    a = run(p, resource_settings=replace(S, max_diagnostic_samples=12))
    assert a.propagations == len(p.primary_steps)
    assert a.actual_end_s == 0
    assert all(f.concentration_kg_m3 is None for f in a.fractions)
    with pytest.raises(ValueError, match='CHECKED_PREFIX'): a.checkpoint(p.primary_times_s[2])
    b = run(p)
    with pytest.raises(ValueError, match='PRIMARY_ENDPOINT'): b.checkpoint(.013)
    c = run(p, resource_settings=replace(S, max_steps=2))
    assert c.actual_end_s == p.primary_times_s[2]
    cp = c.checkpoint(c.actual_end_s)
    assert cp.time_s == c.actual_end_s
    json.loads(a.to_json())


def test_zero_duration_undefined_and_tiny_interval_local_delivery():
    r = run(fraction_windows_s=((.071, .071), (.109, .109+1e-13)))
    assert r.fractions[0].concentration_kg_m3 is None
    assert r.fractions[0].reason == 'ZERO_DURATION_OR_UNREPRESENTABLE_VOLUME'
    assert r.fractions[1].solute_kg > 0 and r.fractions[1].concentration_kg_m3 > 0
    assert r.fractions[1].volume_m3 == ref.volume(plan().flow_history, .109, .109+1e-13)


def test_raw_checkpoint_data_only_roundtrip_and_corruption_rejection():
    p = plan(); cp = run(p).checkpoint(p.primary_times_s[2])
    other = sf.FVCheckpoint.from_json(cp.to_json())
    assert cp.identity_sha256 == other.identity_sha256
    np.testing.assert_array_equal(cp.raw_masses_kg, other.raw_masses_kg)
    a = run(p, checkpoint=cp, observation_times_s=(cp.time_s, .11), fraction_windows_s=())
    b = run(p, checkpoint=other, observation_times_s=(cp.time_s, .11), fraction_windows_s=())
    np.testing.assert_array_equal(a.raw_primary_masses_kg, b.raw_primary_masses_kg)
    with pytest.raises(TypeError): sf.FVCheckpoint()
    record = json.loads(cp.to_json())
    for key, value in [('time_s', 1.), ('schema_version', 2), ('remaining_inventory_kg', 1.),
                        ('outlet_terms_kg', [2.]), ('volume_terms_m3', [1.]), ('parent_identity', 'changed')]:
        broken = copy.deepcopy(record); broken['checkpoint'][key] = value
        with pytest.raises(ValueError): sf.FVCheckpoint.from_json(json.dumps(broken))
    broken = copy.deepcopy(record); broken['checkpoint']['plan']['primary_steps'][0][1] += 1e-5
    with pytest.raises(ValueError, match='SCHEDULE'): sf.FVCheckpoint.from_json(json.dumps(broken))
    with pytest.raises(ValueError): sf.FVCheckpoint.from_json('{"a":NaN}')
    with pytest.raises(ValueError): sf.FVCheckpoint.from_json('{"a":1,"a":2}')


def test_independent_inventory_injection_fails_with_unchanged_flux_samples():
    a = run(); original = sf.fv._inventory
    with patch.object(sf.fv, '_inventory', lambda c, m, s: original(c, m, s)+1e-5):
        b = run()
    np.testing.assert_array_equal(a.raw_primary_masses_kg, b.raw_primary_masses_kg)
    np.testing.assert_array_equal(a.raw_quadrature[:, 6:9], b.raw_quadrature[:, 6:9])
    assert b.status == 'SAMPLED_ADMISSIBILITY_FAILED'
    assert all(f.concentration_kg_m3 is None for f in b.fractions)
    with pytest.raises(ValueError, match='INADMISSIBLE'): b.checkpoint(b.primary.times_s[2])


def test_delayed_clock_knots_and_mass_volume_recombination():
    p = plan(); d = 16.
    T = p.temperature_history; Q = p.flow_history
    shifted = sf.FVPlan(sf.TemperatureHistory(tuple(t+d for t in T.times_s), T.temperatures_K, T.kind),
        sf.FlowHistory(tuple(t+d for t in Q.times_s), Q.flows_m3_s, Q.kind), (d, d+.11), S)
    a = run(); b = run(shifted, supplied(time=d), observation_times_s=tuple(t+d for t in a.observation_times_s),
                      fraction_windows_s=((d, d+.033), (d+.033, d+.071), (d+.071, d+.11)))
    np.testing.assert_allclose(packed(a.observations), packed(b.observations), rtol=2e-12, atol=1e-18)
    tc = .033
    prefix = run(p, stop_time_s=tc, observation_times_s=(0, tc), fraction_windows_s=((0, tc),))
    cp = prefix.checkpoint(tc)
    suffix = run(p, checkpoint=cp, observation_times_s=(tc, .11), fraction_windows_s=((tc, .11),))
    f, g = prefix.fractions[0], suffix.fractions[0]
    whole = run(p, fraction_windows_s=((0, .11),)).fractions[0]
    assert f.solute_kg+g.solute_kg == pytest.approx(whole.solute_kg, rel=1e-12)
    assert f.volume_m3+g.volume_m3 == pytest.approx(whole.volume_m3, rel=1e-15)
    assert (f.solute_kg+g.solute_kg)/(f.volume_m3+g.volume_m3) == pytest.approx(whole.concentration_kg_m3, rel=1e-12)
    assert suffix.continuation_start_s == tc and suffix.root_time_s == 0
    with pytest.raises(ValueError, match='CONTINUATION_SUPPORT'):
        run(p, checkpoint=cp, observation_times_s=(tc, .11), fraction_windows_s=((0, .11),))


@pytest.mark.parametrize('defect', ['equilibrate', 'wrong_phi', 'packing', 'inventory', 'clock', 'volume', 'offset_reset', 'offset_double', 'schedule'])
def test_adversarial_checkpoint_corruption_is_rejected_before_propagation(defect):
    p = plan(); cp = run(p).checkpoint(p.primary_times_s[2])
    record = json.loads(cp.to_json()); c = record['checkpoint']
    if defect == 'equilibrate': c['raw_masses_kg'] = sf.fv._System('caffeine', 1.7, 4).initial(353.15).tolist()
    if defect == 'wrong_phi': c['raw_masses_kg'][4:8] = [x*sf.fv.ps.PHI_V2 for x in c['raw_masses_kg'][4:8]]
    if defect == 'packing': c['raw_masses_kg'][:8] = c['raw_masses_kg'][4:8]+c['raw_masses_kg'][:4]
    if defect == 'inventory': c['remaining_inventory_kg'] = cp.root_state.inventory_kg
    if defect == 'clock': c['time_s'] = 0.
    if defect == 'volume': c['volume_terms_m3'] = [0.]*len(cp.volume_terms_m3)
    if defect == 'offset_reset': c['outlet_terms_kg'] = [0.]*len(cp.outlet_terms_kg)
    if defect == 'offset_double': c['outlet_terms_kg'] = [2*x for x in cp.outlet_terms_kg]
    if defect == 'schedule': c['plan']['primary_steps'][2][1] += 1e-6
    with patch.object(sf.fv._System, 'generator', side_effect=AssertionError('no propagation')):
        with pytest.raises(ValueError): sf.FVCheckpoint.from_json(json.dumps(record))


def test_large_prior_total_cannot_erase_small_remaining_delivery():
    # Manufactured N=1 zero-exchange draining prefix. No source parameter/global
    # mutation; the future branch then uses the unchanged source generator.
    settings = replace(S, cells=1, diagnostic_step_s=.025)
    p = sf.FVPlan(sf.TemperatureHistory.constant_celsius((0, .8), (90,)),
                   sf.FlowHistory((0, .8), (2e-6,), 'constant'), (0, .8), settings)
    st = supplied(cells=1, phases=[[1e12], [0.], [1e-20]])
    tc = p.primary_times_s[35]
    def drain(s, T, Q):
        return sf.fv._mass_generator(1, 1000., 0., 0., 0., 0.)
    with patch.object(sf.fv._System, 'generator', drain):
        prefix = sf.simulate_stateful_fv(plan=p, initial_state=st, observation_times_s=(0, tc), stop_time_s=tc)
    cp = prefix.checkpoint(tc)
    assert cp.origin_outlet_solute_kg/cp.remaining_inventory_kg > 1e25
    future = sf.FVPlan(sf.TemperatureHistory.constant_celsius((tc, .8), (93,)),
                      sf.FlowHistory((tc, .8), (2.2e-6,), 'constant'), (tc, .8), settings)
    r = sf.branch_stateful_fv(cp, plan=future, observation_times_s=(tc, .8), fraction_windows_s=((tc, .8),))
    assert r.status == 'COMPLETE'
    assert r.fractions[0].solute_kg > 0 and r.fractions[0].concentration_kg_m3 > 0
    assert r.primary.origin_outlet_solute_kg[-1] == r.primary.origin_outlet_solute_kg[0]
    assert r.primary.segment_outlet_solute_kg[-1] > 0
    assert dict(r.diagnostics)['local_inventory']['worst_scaled'] < 1e-8


@pytest.mark.parametrize('defect', ['equilibrium_reset', 'fine_phi_capacity', 'phase_packing'])
def test_injected_engine_initialization_defects_fail_independent_expectation(defect):
    good = run(); original = sf.fv._evolve
    def broken(system, history, flow, span, obs, bounds, settings, *, _stateful=None):
        context = dict(_stateful)
        state = context['state'].copy()
        if defect == 'equilibrium_reset': state = system.initial(history.value_K(span[0]))
        if defect == 'fine_phi_capacity': state[system.n:2*system.n] *= sf.fv.ps.PHI_V2
        if defect == 'phase_packing': state[:2*system.n] = np.r_[state[system.n:2*system.n], state[:system.n]]
        context['state'] = state
        return original(system, history, flow, span, obs, bounds, settings, _stateful=context)
    with patch.object(sf.fv, '_evolve', broken): bad = run()
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(bad.raw_primary_masses_kg, good.raw_primary_masses_kg, rtol=1e-12, atol=0)
    if defect != 'phase_packing': assert bad.status == 'SAMPLED_ADMISSIBILITY_FAILED'


def test_numerical_raw_negative_within_tolerance_is_retained_not_clipped():
    p = plan(); st = supplied(phases=[[0.]*4, [2.]*4, [3.]*4])
    original = sf.fv.expm_multiply
    calls = 0
    def small_roundoff(A, y, **kw):
        nonlocal calls
        z = original(A, y, **kw)
        calls += 1
        if calls == 1:
            move = z[0]+1e-20
            z[0] = -1e-20
            z[4] += move
        return z
    # This is a raw-state preservation test, not qualification of the injected integrator.
    # A tiny phase change is applied at the endpoint of a tiny first step.
    tiny = sf.FVPlan(sf.TemperatureHistory.constant_celsius((0, 1e-12), (90,)),
                     sf.FlowHistory((0, 1e-12), (2e-6,), 'constant'), (0, 1e-12),
                     replace(S, h_max_s=1e-12, diagnostic_step_s=1e-12))
    with patch.object(sf.fv, 'expm_multiply', small_roundoff):
        r = sf.simulate_stateful_fv(plan=tiny, initial_state=st, observation_times_s=(0, 1e-12))
    cp = r.checkpoint(1e-12)
    assert cp.raw_masses_kg[0] == -1e-20 and cp.liquid_cell_average_kg_m3[0] < 0
    restored = sf.FVCheckpoint.from_json(cp.to_json())
    np.testing.assert_array_equal(cp.raw_masses_kg, restored.raw_masses_kg)

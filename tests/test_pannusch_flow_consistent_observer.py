"""N<=4 analytical and API checks; no representative qualification in CI."""
from dataclasses import replace, FrozenInstanceError
import copy
import json
import math
import time
from unittest.mock import patch

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.models.pannusch2024 import flow_consistent_observer as ob
from puckworks.models.pannusch2024 import stateful_fv as sf
from tools import pannusch_flow_temp_fv_reference as ref


def fixture(kind='linear', solute='caffeine', scale=1.):
    p = sf.FVPlan(sf.TemperatureHistory.linear_celsius((0, .043, .11), (80, 95, 86)),
        sf.FlowHistory((0, .071, .11), (1.2e-6, 2.8e-6, 1.6e-6) if kind == 'linear' else (1e-6, 2.7e-6), kind),
        (0, .11), sf.FVSettings(cells=4))
    c = ref.stateful_u_fields(solute, 4)*scale
    state = sf.FVChemicalState.from_cell_averages(solute=solute, time_s=0,
        liquid_kg_m3=c[0], fine_kg_m3=c[1], coarse_kg_m3=c[2], edges_m=np.linspace(0, sf.fv.ps.L, 5))
    return p, state


def run(p=None, state=None, **kw):
    if p is None:
        p, state = fixture()
    return sf.simulate_stateful_fv(plan=p, initial_state=state, observation_times_s=(0, .013, .11),
        fraction_windows_s=((.007, .053),), **kw)


def test_declared_constant_concentration_integration_oracle():
    # Integration oracle only; no invented constant-outlet production trajectory.
    q = sf.FlowHistory((0, 1), (1e-6, 3e-6), 'linear')
    l, r, C = .81, .813, 7.
    expected_volume = 1e-6*(r-l)+1e-6*(r*r-l*l)
    actual = C*expected_volume/expected_volume
    frozen = C*2e-6*(r-l)/expected_volume
    assert actual == C and abs(frozen-C) > .1


@pytest.mark.parametrize('qa,qb', [(1e-6, 3e-6), (3e-6, 1e-6), (2e-6, 2e-6)])
def test_one_cell_passive_remaining_and_stable_delivery(qa, qb):
    q = sf.FlowHistory((0, .1), (qa, qb), 'linear')
    clock = ob._Clock(q, 0., .1, (qa+qb)/2)
    W, C0 = 4e-8, 2.3
    A = sf.fv._mass_generator(1, (qa+qb)/(2*W), 0, 0, 0, 0)
    initial = np.array([W*C0, 0., 0., 0.])
    action = ob._Actions(sf.FVSettings(cells=1), time.monotonic())
    beta = (qb-qa)/.1
    for l, r in [(0., .1), (.007, .093), (.073, np.nextafter(.073, 1.))]:
        # Independent polynomial antiderivative and expm1, not candidate helpers.
        vl = qa*l+beta*l*l/2
        dv = (qa+beta*l)*(r-l)+beta*(r-l)**2/2
        Cl = C0*math.exp(-vl/W)
        expected_mass = W*Cl*(-math.expm1(-dv/W))
        left = action.evolve(A, initial, clock.at(l))
        local = action.evolve(A, left, clock.delta(l, r))
        assert local[0] == pytest.approx(W*Cl*math.exp(-dv/W), rel=2e-14)
        assert local[-1] == pytest.approx(expected_mass, rel=2e-14, abs=0)
        assert local[-1] > 0
        assert math.fsum(local) == pytest.approx(left[0], rel=2e-14)
    s = .027
    assert clock.at(s)-s == pytest.approx(beta*s*(s-.1)/(qa+qb), abs=4e-17)
    assert abs(clock.at(s)-s) <= abs(beta)*.1**2/(4*(qa+qb))


@pytest.mark.parametrize('solute', sf.fv.th.SPECIES)
@pytest.mark.parametrize('kind', ['linear', 'constant'])
def test_independent_coupled_phase_balances_and_constant_equivalence(solute, kind):
    p, state = fixture(kind, solute)
    r = run(p, state)
    z = ob.observe_flow_consistent_fv(r, observation_times_s=(0, .013, .11), fraction_windows_s=((.007, .053),))
    assert z.request_support == 'COMPLETE', z.reason
    # Independent concentration matrix, independent initial fields, analytic Q integral.
    i = np.searchsorted(p.primary_times_s, .013)-1
    a, b, T, Q = p.primary_steps[i]
    initial = np.r_[ref.stateful_u_fields(solute, 4).ravel(), 0.]
    volume = ref.volume(p.flow_history, a, .013)
    tau = (b-a)*volume/ref.volume(p.flow_history, a, b)
    expected = expm(ref.operator_factory(solute, 1.7, 4)(T, Q).toarray()*tau)@initial
    actual = np.r_[z.observations.liquid_cell_average_kg_m3[1], z.observations.fine_cell_average_kg_m3[1],
                   z.observations.coarse_cell_average_kg_m3[1], z.observations.segment_outlet_solute_kg[1]]
    np.testing.assert_allclose(actual, expected, rtol=2e-13, atol=1e-20)
    if kind == 'constant':
        np.testing.assert_array_equal(z.observations.liquid_cell_average_kg_m3, r.observations.liquid_cell_average_kg_m3)
        assert z.fractions[0].solute_kg == r.fractions[0].solute_kg
    assert z.method != sf.ALGORITHM
    assert z.accuracy_status == 'NOT_ASSESSED'


def test_endpoints_no_mutation_batching_repeat_and_tiny_windows():
    r = run(); before = r.identity_sha256
    l, h = .079, np.nextafter(.079, 1.)
    windows = ((.007, .053), (.007, .071), (.071, .1), (.007, .1), (l, h), (.013, .013))
    a = ob.observe_flow_consistent_fv(r, observation_times_s=r.primary.times_s, fraction_windows_s=windows)
    b = ob.observe_flow_consistent_fv(r, observation_times_s=tuple(reversed(r.primary.times_s)), fraction_windows_s=windows[::-1])
    assert a.request_support == b.request_support == 'COMPLETE', (a.reason, b.reason)
    np.testing.assert_array_equal(a.observations.liquid_cell_average_kg_m3, r.primary.liquid_cell_average_kg_m3)
    np.testing.assert_array_equal(a.observations.segment_outlet_solute_kg, r.primary.segment_outlet_solute_kg)
    assert a.fractions == b.fractions[::-1]
    assert a.fractions[4].solute_kg > 0
    assert a.fractions[5].reason == 'ZERO_DURATION'
    assert math.fsum(f.solute_kg for f in a.fractions[1:3]) == pytest.approx(a.fractions[3].solute_kg, rel=1e-13)
    one = ob.observe_flow_consistent_fv(r, observation_times_s=(), fraction_windows_s=(windows[0],))
    assert one.fractions[0] == a.fractions[0]
    assert before == r.identity_sha256 == sf._hash(r)
    for array in (a.checks, a.clock_residuals, a.observations.liquid_cell_average_kg_m3):
        with pytest.raises(ValueError): array.setflags(write=True)
    with pytest.raises(FrozenInstanceError): a.method = 'wrong'
    assert json.loads(a.to_json())['PHYSICAL_VALIDATION'] == 'NOT_ESTABLISHED'


def test_genuine_stop_resume_branch_and_no_cross_checkpoint_service():
    p, state = fixture(); tc = p.primary_times_s[2]
    prefix = run(p, state, stop_time_s=tc); cp = prefix.checkpoint(tc)
    suffix = sf.simulate_stateful_fv(checkpoint=cp, observation_times_s=(tc, .11))
    full = run(p, state)
    z = ob.observe_flow_consistent_fv(prefix, observation_times_s=(tc, .11), fraction_windows_s=((.007, tc),))
    v = ob.observe_flow_consistent_fv(suffix, observation_times_s=(tc, .11), fraction_windows_s=((tc, .1), (.007, .1)))
    w = ob.observe_flow_consistent_fv(full, observation_times_s=(), fraction_windows_s=((.007, .1),))
    assert z.observation_status[-1] == 'OUTSIDE_UPSTREAM_CHECKED_PREFIX'
    assert v.fractions[-1].solute_kg is None
    assert v.fractions[-1].reason == 'BEFORE_CONTINUATION_START'
    assert math.fsum((z.fractions[0].solute_kg, v.fractions[0].solute_kg)) == pytest.approx(w.fractions[0].solute_kg, rel=1e-12)
    assert prefix.checkpoint(tc).identity_sha256 == cp.identity_sha256
    branch = sf.FVPlan(sf.TemperatureHistory.constant_celsius((tc, .11), (93,)),
        sf.FlowHistory((tc, .11), (2.2e-6,), 'constant'), (tc, .11), p.settings)
    br = sf.branch_stateful_fv(cp, plan=branch, observation_times_s=(tc, .11))
    assert ob.observe_flow_consistent_fv(br, observation_times_s=(tc, .11)).request_support == 'COMPLETE'


@pytest.mark.parametrize('scale', [0., 1e-250])
def test_exact_zero_and_tiny_positive(scale):
    p, s = fixture(scale=scale); r = run(p, s)
    z = ob.observe_flow_consistent_fv(r, observation_times_s=(), fraction_windows_s=((.079, np.nextafter(.079, 1.)),))
    f = z.fractions[0]
    assert f.concentration_kg_m3 is not None, z.reason
    assert (f.status == 'VALID_NUMERICAL_ZERO') == (scale == 0)
    assert (f.solute_kg > 0) == (scale > 0)


def test_failures_publish_only_complete_checked_intervals():
    r = run()
    z = ob.observe_flow_consistent_fv(r, observation_times_s=(0, .013, .11),
        fraction_windows_s=((0, .11),), resource_settings=replace(r.plan.settings, max_exponential_applications=2))
    assert z.actual_checked_end_s == 0 and z.observation_status == ('SUPPORTED', 'EXPONENTIAL_APPLICATION_LIMIT', 'EXPONENTIAL_APPLICATION_LIMIT')
    assert z.fractions[0].solute_kg is None and not z.panels
    bad = run(resource_settings=sf.FVSettings(cells=4, max_diagnostic_samples=12))
    assert bad.actual_end_s == 0 and bad.propagations > 0
    z = ob.observe_flow_consistent_fv(bad, observation_times_s=(0, .01))
    assert z.observation_status[-1] == 'OUTSIDE_UPSTREAM_CHECKED_PREFIX'
    retained = run(resource_settings=sf.FVSettings(cells=4, max_steps=2))
    z = ob.observe_flow_consistent_fv(retained, observation_times_s=(retained.actual_end_s, .11))
    assert z.observation_status == ('SUPPORTED', 'OUTSIDE_UPSTREAM_CHECKED_PREFIX')


@pytest.mark.parametrize('key', ['actual_end_s', 'step_volume_m3', 'exportable_primary', 'raw_primary_masses_kg', 'parent_identity'])
def test_corruption_even_with_rehashed_wrapper(key):
    r = run()
    changes = dict(actual_end_s=.2, step_volume_m3=r.step_volume_m3*1.01,
        exportable_primary=np.array([True, False, True]+[False]*(len(r.primary.times_s)-3)),
        raw_primary_masses_kg=r.raw_primary_masses_kg[:, :-1], parent_identity='fake')
    with pytest.raises(ValueError):
        ob.observe_flow_consistent_fv(replace(r, **{key:changes[key]}), observation_times_s=())
    damaged = copy.copy(r); object.__setattr__(damaged, 'identity_sha256', '')
    with pytest.raises(ValueError, match='IDENTITY'):
        ob.observe_flow_consistent_fv(damaged, observation_times_s=())


@pytest.mark.parametrize('window', [((.1, .01),), ((0, np.nan),), ((0, .1, .2),), ((False, .1),)])
def test_invalid_windows(window):
    with pytest.raises(ValueError): ob.observe_flow_consistent_fv(run(), observation_times_s=(), fraction_windows_s=window)


@pytest.mark.parametrize('q', [0., -1e-6, 3.1e-6, .9e-6])
def test_flow_domain_is_unchanged(q):
    with pytest.raises(ValueError): sf.FlowHistory((0, 1), (q,), 'constant')


def test_new_phase_failure_does_not_publish_partial_fraction():
    r = run(); original = sf.fv.expm_multiply
    def invalid(A,y,**kwargs):
        out = original(A,y,**kwargs)
        out[0] = -1.
        return out
    with patch.object(sf.fv,'expm_multiply',invalid):
        z = ob.observe_flow_consistent_fv(r, observation_times_s=(0,.013),fraction_windows_s=((0,.013),))
    assert z.reason == 'NEW_INTERIOR_ADMISSIBILITY_FAILED'
    assert z.fractions[0].solute_kg is None and z.observations.times_s.tolist() == [0]


def test_positive_underflow_is_not_exact_zero():
    p,s = fixture(scale=1e-300)
    r = run(p,s)
    z = ob.observe_flow_consistent_fv(r,observation_times_s=(),fraction_windows_s=((.079,np.nextafter(.079,1.)),))
    assert z.fractions[0].concentration_kg_m3 is None
    assert z.fractions[0].status != 'VALID_NUMERICAL_ZERO'


def test_large_prior_total_does_not_erase_local_delivery():
    settings=sf.FVSettings(cells=1,diagnostic_step_s=.025)
    p=sf.FVPlan(sf.TemperatureHistory.constant_celsius((0,.8),(90,)),sf.FlowHistory((0,.8),(2e-6,),'constant'),(0,.8),settings)
    s=sf.FVChemicalState.from_cell_averages(solute='caffeine',time_s=0,edges_m=(0,sf.fv.ps.L),
        liquid_kg_m3=(1e12,),fine_kg_m3=(0.,),coarse_kg_m3=(1e-20,))
    tc=p.primary_times_s[35]
    # Same manufactured draining seam as 004's regression; no source-law change.
    with patch.object(sf.fv._System,'generator',lambda *_:sf.fv._mass_generator(1,1000.,0.,0.,0.,0.)):
        prefix=sf.simulate_stateful_fv(plan=p,initial_state=s,observation_times_s=(0,tc),stop_time_s=tc)
    cp=prefix.checkpoint(tc)
    future=sf.FVPlan(sf.TemperatureHistory.constant_celsius((tc,.8),(93,)),
        sf.FlowHistory((tc,.8),(2e-6,2.8e-6),'linear'),(tc,.8),settings)
    r=sf.branch_stateful_fv(cp,plan=future,observation_times_s=(tc,.8))
    z=ob.observe_flow_consistent_fv(r,observation_times_s=(tc,.8),fraction_windows_s=((tc,.8),))
    assert z.request_support=='COMPLETE',z.reason
    assert z.fractions[0].solute_kg>0
    assert z.observations.origin_outlet_solute_kg[-1]==z.observations.origin_outlet_solute_kg[0]
    assert z.observations.segment_outlet_solute_kg[-1]>0


@pytest.mark.parametrize('value',[79.,99.])
def test_temperature_domain_unchanged(value):
    with pytest.raises(ValueError):sf.TemperatureHistory.constant_celsius((0,1),(value,))


def test_corrupted_histories_and_raw_physical_observation_views():
    r=run()
    corrupted=replace(r,observations=replace(r.observations,segment_volume_m3=r.observations.segment_volume_m3+1e-6))
    with pytest.raises(ValueError,match='ACCOUNTING'):
        ob.observe_flow_consistent_fv(corrupted,observation_times_s=(.013,))
    root=copy.copy(r.root_state);object.__setattr__(root,'source_identities',())
    with pytest.raises(ValueError,match='IDENTITY'):
        ob.observe_flow_consistent_fv(replace(r,root_state=root),observation_times_s=())
    broken=copy.copy(r.plan)
    object.__setattr__(broken,'flow_history',sf.FlowHistory((0,.11),(2e-6,),'constant'))
    with pytest.raises(ValueError,match='IDENTITY'):
        ob.observe_flow_consistent_fv(replace(r,plan=broken),observation_times_s=())


def test_constant_temperature_rising_flow_and_unavailable_future():
    p,s=fixture();p=sf.FVPlan(sf.TemperatureHistory.constant_celsius((0,.11),(90,)),p.flow_history,p.t_span_s,p.settings)
    tc=p.primary_times_s[2];r=run(p,s,stop_time_s=tc)
    original=sf.FlowHistory.value_m3_s
    def guarded(self,t):
        assert t<=tc, 'future forcing evaluated'
        return original(self,t)
    with patch.object(sf.FlowHistory,'value_m3_s',guarded):
        z=ob.observe_flow_consistent_fv(r,observation_times_s=(.001,.1),fraction_windows_s=((0,.1),))
    assert z.observation_status[0]=='SUPPORTED' and z.fractions[0].solute_kg is None


def test_request_conversion_cannot_hide_a_positive_window():
    from fractions import Fraction
    r=run()
    with pytest.raises(ValueError,match='UNREPRESENTABLE'):
        ob.observe_flow_consistent_fv(r,observation_times_s=(Fraction(1,10**400),))
    with pytest.raises(ValueError,match='UNREPRESENTABLE'):
        ob.observe_flow_consistent_fv(r,observation_times_s=(),fraction_windows_s=((0,Fraction(1,10**400)),))


def test_forcing_validation_allows_original_interpolation_roundoff():
    # N1, short subset; different operation order in history vs segment T lookup.
    p=sf.FVPlan(sf.TemperatureHistory.linear_celsius((0,11.3,30),(80,95,86)),
        sf.FlowHistory((0,17.2,30),(1.2e-6,2.8e-6,1.6e-6),'linear'),(0,.11),sf.FVSettings(cells=1))
    state=sf.FVChemicalState.source_equilibrium(p.temperature_history,time_s=0,solute='caffeine',cells=1)
    r=sf.simulate_stateful_fv(plan=p,initial_state=state,observation_times_s=(0,.11))
    assert ob.observe_flow_consistent_fv(r,observation_times_s=(.01,.11)).request_support=='COMPLETE'


def test_later_inadmissibility_retains_prefix_without_future_forcing():
    p,s=fixture(); original=sf.fv._inventory;calls=0
    def later_fault(c,m,system):
        nonlocal calls
        calls+=1
        return original(c,m,system)+(1. if calls>36 else 0.)
    with patch.object(sf.fv,'_inventory',later_fault):r=run(p,s)
    good=np.flatnonzero(r.exportable_primary)
    assert len(good)>1 and len(good)<len(r.primary.times_s)
    end=float(r.primary.times_s[good[-1]])
    value=sf.FlowHistory.value_m3_s;integral=sf.FlowHistory.integral
    def guarded_value(self,t):
        assert t<=end
        return value(self,t)
    def guarded_integral(self,l,h):
        assert h<=end
        return integral(self,l,h)
    with patch.object(sf.FlowHistory,'value_m3_s',guarded_value),patch.object(sf.FlowHistory,'integral',guarded_integral):
        z=ob.observe_flow_consistent_fv(r,observation_times_s=(end,.11))
    assert z.observation_status==('SUPPORTED','OUTSIDE_UPSTREAM_CHECKED_PREFIX')

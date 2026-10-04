"""Small N<=12 synthetic/algebraic tests; no empirical or full-bed campaign."""
from dataclasses import FrozenInstanceError, replace
import copy
import json
from unittest.mock import patch

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.models.pannusch2024 import flow_temperature_history_fv as fv
from puckworks.models.pannusch2024 import temperature_history_fv as old
from puckworks.models.pannusch2024 import solver as ps
from tools import pannusch_flow_temp_fv_reference as ref

S = fv.FVSettings(cells=4, h_max_s=.02, diagnostic_step_s=.0125)


def test_extreme_flow_clocks_keep_representable_values_and_strict_JSON():
    huge=fv.FlowHistory((0.,1e308),(1e-6,3e-6),'linear')
    assert huge.integral(9e307,1e308)==pytest.approx(2.9e301,rel=3e-15)
    tiny=fv.FlowHistory((0.,1e-320,.08),(1e-6,3e-6,3e-6),'linear')
    assert tiny.value_m3_s(1e-320)==3e-6
    segment=tiny.integration_segments(0,.08)[0]
    assert segment.value_m3_s(1e-320)==3e-6
    assert segment.value_m3_s(5e-321)==pytest.approx(2e-6,rel=1e-15)
    assert tiny.integral(0,1e-320)==0.  # actual volume rounds below float range
    result=run(T=fv.TemperatureHistory.constant_celsius((0,.08),(88,)),Q=tiny,
               settings=replace(S,cells=1))
    assert result.integration_complete
    json.loads(result.to_json(),parse_constant=lambda x: pytest.fail(x))


def test_nonfinite_legacy_temperature_segment_rejected_before_integration():
    T=fv.TemperatureHistory.linear_celsius((0,1e-320,.08),(80,98,98))
    with patch.object(fv._System,'generator',side_effect=AssertionError('integration forbidden')):
        with pytest.raises(fv.InvalidTemperatureHistoryInput,match='nonfinite forcing'):
            run(T=T)


def run(T=None, Q=None, **kwargs):
    T = T or fv.TemperatureHistory.linear_celsius((0,.08),(80,98))
    Q = Q or fv.FlowHistory((0,.03,.08),(1e-6,3e-6),'constant')
    args = dict(flow_history=Q,t_span_s=(0,.08),solute='caffeine',
        observation_times_s=(0,.011,.02,.03,.051,.08),fraction_bounds_s=(0,.02,.05,.08),settings=S)
    args.update(kwargs)
    return fv.simulate_flow_temperature_history_fv(T,**args)


def fields(tr):
    return np.column_stack((tr.liquid_cell_average_kg_m3,tr.fine_cell_average_kg_m3,
                            tr.coarse_cell_average_kg_m3,tr.outlet_solute_kg))


@pytest.mark.parametrize('kind', ['constant','linear'])
def test_flow_values_integrals_boundary_and_stable_tiny_delayed_window(kind):
    q=fv.FlowHistory([10,11,14],[1e-6,3e-6] if kind=='constant' else [1e-6,2e-6,3e-6],kind)
    assert q.value_m3_s(14)==3e-6 and q.value_m3_s(11)==(3e-6 if kind=='constant' else 2e-6)
    assert q.integral(11,11)==0
    for a,b in [(10,14),(10.5,12),(13.999999,13.999999000001)]:
        assert q.integral(a,b)==pytest.approx(ref.volume(q,a,b),rel=3e-15,abs=0)
    for a,b in [(9,10),(11,10),(14,15),(np.nan,13)]:
        with pytest.raises(ValueError): q.integral(a,b)
    with pytest.raises(FrozenInstanceError): q.kind='linear'


@pytest.mark.parametrize('args', [
    ((0,0),(1e-6,),'constant'), ((1,0),(1e-6,),'constant'),
    ((0,np.inf),(1e-6,),'constant'), ((0,1),(1e-6,2e-6),'constant'),
    ((0,1),(1e-6,),'linear'), ((0,1),(0,),'constant'),
    ((0,1),(-1e-6,),'constant'), ((0,1),(3.01e-6,),'constant'),
    ((0,1),(np.nan,),'constant'), ((0,1),(1e-6+0j,),'constant'),
    ((0,1),('0.000001',),'constant'), ((0,1),(True,),'constant'),
    ((0,1),[[1e-6]],'constant'), ((0,1),lambda t:1e-6,'constant'),
    ((0,1),(1e-6,),'spline'), ((0,1),(1e-6,),'constant','mL/s'),
    ((False,1),(1e-6,),'constant'), ((0,1+0j),(1e-6,),'constant'),
])
def test_flow_rejections(args):
    with pytest.raises(ValueError): fv.FlowHistory(*args)


@pytest.mark.parametrize('n',[1,4,12])
@pytest.mark.parametrize('solute',fv.th.SPECIES)
@pytest.mark.parametrize('T,Q',[(353.15,1e-6),(371.15,3e-6)])
def test_generator_independent_concentration_balances_and_positive_states(n,solute,T,Q):
    s=fv._System(solute,1.7,n)
    B=s.generator(T,Q).toarray(); A=ref.operator_factory(solute,1.7,n)(T,Q).toarray()
    cap=np.r_[s.capacities,1.]
    np.testing.assert_allclose(B,cap[:,None]*A/cap[None,:],rtol=3e-14,atol=2e-13)
    off=B.copy(); np.fill_diagonal(off,0)
    assert off.min()>=0 and abs(B.sum(axis=0)).max()/max(1,abs(B).max())<=1e-12
    assert s.initial(T).sum()==pytest.approx(s.M0(T),rel=3e-15)
    assert s.initial(T)[0]>0
    c=np.random.default_rng(73).random((3,n)); K,k1,k2=s.coefficients(T,Q)
    R1=s.W*s.as1*k1*(K*c[1]-c[0]); R2=s.W*ps.PHI_V2*s.as2*k2*(K*c[2]-c[0])
    F=np.r_[0,Q*c[0]]
    expected=np.r_[F[:-1]-F[1:]+R1+R2,-R1,-R2,F[-1]]
    np.testing.assert_allclose(B@np.r_[c.ravel()*s.capacities,0],expected,atol=1e-19,rtol=2e-13)
    for y in [np.random.default_rng(22).random(3*n+1),np.eye(3*n+1)[0]]:
        z=expm(B*.05)@y
        assert z.min()>=-1e-14 and abs(z.sum()-y.sum())<1e-12*max(1,y.sum())


def test_closed_exchange_equilibrium_and_relaxation():
    B=fv._mass_generator(2,0,.4,.2,.1,.05).toarray()
    eq=np.repeat([1.,4.,4.],2)
    np.testing.assert_allclose(B@np.r_[eq,0],0,atol=1e-15)
    y=np.r_[np.ones(2),np.zeros(5)]; z=expm(200*B)@y
    np.testing.assert_allclose(z[:-1],eq/9,atol=2e-6)
    assert z.sum()==pytest.approx(2,rel=1e-12)


@pytest.mark.parametrize('solute',fv.th.SPECIES)
@pytest.mark.parametrize('qkind',['constant','linear'])
@pytest.mark.parametrize('tkind',['constant','step','linear'])
def test_constant_Q_collapses_to_unchanged_FV(solute,qkind,tkind):
    T=(fv.TemperatureHistory.constant_celsius((0,.08),(88,)) if tkind=='constant' else
       fv.TemperatureHistory.constant_celsius((0,.025,.08),(80,98)) if tkind=='step' else
       fv.TemperatureHistory.linear_celsius((0,.025,.08),(80,90,98)))
    q=fv.FlowHistory((0,.08),(2e-6,) if qkind=='constant' else (2e-6,2e-6),qkind)
    a=run(T,q,solute=solute)
    b=old.simulate_temperature_history_fv(T,flow_m3_s=2e-6,t_span_s=(0,.08),solute=solute,
        observation_times_s=a.requested_observation_times_s,fraction_bounds_s=(0,.02,.05,.08),settings=S)
    np.testing.assert_array_equal(a.trace.times_s,b.trace.times_s)
    np.testing.assert_array_equal(a.trace.masses_kg,b.trace.masses_kg)
    np.testing.assert_array_equal(fields(a.observations),fields(b.observations))
    np.testing.assert_allclose(a.observations.hydraulic_volume_m3,b.observations.hydraulic_volume_m3,rtol=1e-15)
    np.testing.assert_allclose([f.concentration_kg_m3 for f in a.fractions],[f.concentration_kg_m3 for f in b.fractions],rtol=1e-14)


def test_ordered_noncommuting_dense_reference_and_union():
    T=fv.TemperatureHistory.constant_celsius((0,.02,.08),(80,98))
    Q=fv.FlowHistory((0,.03,.08),(1e-6,3e-6),'constant')
    r=run(T,Q); assemble=ref.operator_factory('caffeine',1.7,4)
    a=lambda T,Q:assemble(T,Q).toarray()
    y,_=ref.initial_and_inventory(353.15,'caffeine',1.7,4)
    expected=expm(a(371.15,3e-6)*.05)@expm(a(371.15,1e-6)*.01)@expm(a(353.15,1e-6)*.02)@y
    np.testing.assert_allclose(fields(r.observations)[-1],expected,rtol=2e-13,atol=1e-15)
    reverse=expm(a(353.15,1e-6)*.02)@expm(a(371.15,1e-6)*.01)@expm(a(371.15,3e-6)*.05)@y
    assert np.max(abs(reverse-expected))>1e-3
    assert [dict(s)['requested_span_s'] for s in r.segments]==[(0,.02),(.02,.03),(.03,.08)]
    for left,right in zip(r.segments,r.segments[1:]):
        assert dict(left)['end_state_sha256']==dict(right)['start_state_sha256']


@pytest.mark.parametrize('tk,qk',[('constant','linear'),('linear','constant'),('linear','linear')])
def test_mixed_histories_noncoincident_knots_and_actual_time_reference(tk,qk):
    T=fv.TemperatureHistory((0,.021,.08),(353.15,371.15) if tk=='constant' else (353.15,360,371.15),tk)
    Q=fv.FlowHistory((0,.033,.08),(1e-6,3e-6) if qk=='constant' else (1e-6,2e-6,3e-6),qk)
    r=run(T,Q,settings=replace(S,h_max_s=.001))
    z,*_=ref.reference(T,Q,'caffeine',1.7,4,r.observations.times_s,t_span_s=(0,.08))
    assert np.max(abs(fields(r.observations)[:,:-1]-z[:,:-1]))/10.8<5e-5


def test_observers_do_not_change_primary_and_partial_volume_is_analytic():
    T=fv.TemperatureHistory.constant_celsius((0,.08),(88,))
    Q=fv.FlowHistory((0,.08),(1e-6,3e-6),'linear')
    a=run(T,Q); b=run(T,Q,observation_times_s=(.001,.007,.013,.035,.073),fraction_bounds_s=(.007,.035,.073))
    np.testing.assert_array_equal(a.trace.masses_kg,b.trace.masses_kg)
    np.testing.assert_array_equal(a.trace.frozen_flow_m3_s,b.trace.frozen_flow_m3_s)
    s=fv._System('caffeine',1.7,4); dt=.007
    expected=expm(s.generator(361.15,Q.value_m3_s(.01)).toarray()*dt)@a.trace.masses_kg[0]
    np.testing.assert_allclose(fields(b.observations)[1],np.r_[expected[:-1]/s.capacities,expected[-1]],rtol=2e-14)
    actual=Q.integral(0,dt); wrong=Q.value_m3_s(.01)*dt
    assert abs(actual-wrong)>1e-10
    assert b.observations.hydraulic_volume_m3[1]==pytest.approx(actual,rel=1e-15)
    with pytest.raises(AssertionError): np.testing.assert_allclose(wrong,actual,rtol=1e-12,atol=0)


def test_delayed_origin_clock_translation_volume_weighted_recombination():
    T=fv.TemperatureHistory.linear_celsius((-1,.08),(80,98))
    Q=fv.FlowHistory((-1,0,.03,.08),(2e-6,1e-6,3e-6),'constant')
    r=run(T,Q)
    vols=np.array([f.volume_m3 for f in r.fractions]); cs=np.array([f.concentration_kg_m3 for f in r.fractions])
    whole=r.observations.outlet_solute_kg[-1]/Q.integral(0,.08)
    assert np.dot(vols,cs)/vols.sum()==pytest.approx(whole,rel=1e-14)
    duration=np.diff([0,.02,.05,.08]); wrong=np.dot(duration,cs)/.08
    with pytest.raises(AssertionError): assert wrong==pytest.approx(whole,rel=1e-10)
    d=16
    shift=run(fv.TemperatureHistory(tuple(t+d for t in T.times_s),T.temperatures_K,T.kind),
        fv.FlowHistory(tuple(t+d for t in Q.times_s),Q.flows_m3_s,Q.kind),
        t_span_s=(d,d+.08),observation_times_s=tuple(t+d for t in r.observations.times_s),
        fraction_bounds_s=(d,d+.02,d+.05,d+.08))
    np.testing.assert_allclose(fields(r.observations),fields(shift.observations),rtol=3e-11,atol=1e-15)
    assert r.observations.hydraulic_volume_m3[0]==0 and r.observations.outlet_solute_kg[0]==0


@pytest.mark.parametrize('kwargs', [dict(flow_history=lambda t:2e-6),dict(flow_history=fv.FlowHistory((.01,.08),(2e-6,),'constant')),
    dict(t_span_s=(-.01,.08)),dict(solute='unknown'),dict(grind=1.8),dict(observation_times_s=(.03,.02)),
    dict(fraction_bounds_s=(0,.081)),dict(t_span_s=(0,.03,.08)),dict(settings=replace(S,max_state_values=100))])
def test_invalid_call_rejected_before_generator(kwargs):
    with patch.object(fv._System,'generator',side_effect=AssertionError('integrated invalid input')):
        with pytest.raises(ValueError): run(**kwargs)


def test_arrays_json_identities_and_source_global_immutability():
    before=copy.deepcopy((ps.GRINDS,ps._solute_params(),fv.pc.SOLUTES))
    r=run(); j=json.loads(r.to_json())
    assert j['accuracy_status']=='NOT_ASSESSED' and 'flow_m3_s' not in j
    assert set(dict(r.source_identities)) >= {'flow_history.py','flow_temperature_history_fv.py','temperature_history_fv.py','temperature_history.py'}
    for a in (r.trace.masses_kg,r.trace.frozen_flow_m3_s,r.observations.prescribed_flow_m3_s,r.quadrature.panel_end_s):
        with pytest.raises(ValueError): a.setflags(write=True)
    assert before==(ps.GRINDS,ps._solute_params(),fv.pc.SOLUTES)


def test_resource_failure_checked_prefix_null_fractions_and_unresolved_tiny_mass():
    r=run(settings=replace(S,max_steps=1))
    assert not r.integration_complete and r.actual_span_s[1]==.015
    assert all(f.concentration_kg_m3 is None for f in r.fractions)
    assert r.trace.times_s[-1]==r.actual_span_s[-1] and r.quadrature.times_s.max()<=r.actual_span_s[-1]
    json.loads(r.to_json())
    z=run(settings=replace(S,max_exponential_applications=1))
    assert z.actual_span_s==(0,0) and len(z.observations.times_s)==1
    tiny=run(fraction_bounds_s=(.079,.079+1e-13))
    assert tiny.fractions[0].concentration_kg_m3 is None
    assert tiny.fractions[0].raw_diagnostic_concentration_kg_m3 is not None


@pytest.mark.parametrize('defect',['frozen_Q','T_only_cache','frozen_h','interstitial_Re'])
def test_deliberate_operator_defects_are_rejected(defect):
    T=fv.TemperatureHistory.constant_celsius((0,.08),(88,))
    Q=fv.FlowHistory((0,.03,.08),(1e-6,3e-6),'constant')
    good=run(T,Q); original=fv._System.generator
    cached={}
    def bad(s,T,Q):
        if defect=='frozen_Q': return original(s,T,1e-6)
        if defect=='T_only_cache':
            if T not in cached: cached[T]=original(s,T,Q)
            return cached[T]
        K,k1,k2=s.coefficients(T,1e-6 if defect=='frozen_h' else Q/ps.ALPHA_L)
        return fv._mass_generator(s.n,Q/(s.W*ps.ALPHA_L),s.as1*k1/ps.ALPHA_L,ps.PHI_V2*s.as2*k2/ps.ALPHA_L,K*k1,K*k2)
    with patch.object(fv._System,'generator',bad): broken=run(T,Q)
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(fields(broken.observations),fields(good.observations),rtol=1e-10,atol=1e-15)


def test_knot_reset_and_inventory_complement_defects_are_rejected():
    r=run(); s=fv._System('caffeine',1.7,4)
    restarted=s.initial(r.temperature_history.value_K(.03))
    at=np.flatnonzero(r.trace.times_s==.03)[0]
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(restarted,r.trace.masses_kg[at],rtol=1e-12,atol=1e-16)
    original=fv._inventory
    with patch.object(fv,'_inventory',lambda c,m,sys:original(c,m,sys)+.01*sys.M0(353.15)):
        broken=run()
    # Evolved Mout and independent sampled outlet fluxes stay fixed, yet accounting FAILS.
    np.testing.assert_array_equal(r.observations.outlet_solute_kg,broken.observations.outlet_solute_kg)
    np.testing.assert_array_equal(r.quadrature.numerical_frozen_step_flux_kg_s,broken.quadrature.numerical_frozen_step_flux_kg_s)
    assert broken.numerical_admissibility=='FAILED'
    assert all(f.concentration_kg_m3 is None for f in broken.fractions)


def test_both_flux_quadratures_use_frozen_state_and_actual_prescribed_flow():
    T=fv.TemperatureHistory.constant_celsius((0,.08),(88,))
    Q=fv.FlowHistory((0,.08),(1e-6,3e-6),'linear')
    r=run(T,Q)
    q=r.quadrature
    # One full panel plus interior panels; numerical flux integrates evolved mass.
    full=q.full_interval.astype(bool)
    for order in (4,8):
        select=full & (q.order==order)
        numerical=np.sum(q.weights_s[select]*q.numerical_frozen_step_flux_kg_s[select])
        assert abs(numerical-r.trace.masses_kg[-1,-1])<1e-12*r.M0_cont_kg
    i=q.primary_step_index.astype(int)
    expected=np.array([Q.value_m3_s(t) for t in q.times_s])/r.trace.frozen_flow_m3_s[i]
    np.testing.assert_allclose(q.prescribed_flow_diagnostic_flux_kg_s,
        q.numerical_frozen_step_flux_kg_s*expected,rtol=2e-15)
    assert np.any(abs(q.prescribed_flow_diagnostic_flux_kg_s-q.numerical_frozen_step_flux_kg_s)>1e-10)
    assert np.any(~full)


def test_diagnostic_resource_failure_and_empty_supported_observers_are_explicit():
    r=run(observation_times_s=(.08,),settings=replace(S,max_diagnostic_samples=7))
    assert r.actual_span_s==(0,0) and not r.integration_complete
    assert r.observations.liquid_cell_average_kg_m3.shape==(0,4)
    j=json.loads(r.to_json())
    assert j['unsupported_observations']==[dict(time_s=.08,values=None,reason='NOT_EVALUATED_IN_SUPPORTED_PREFIX')]
    assert all(f['volume_m3'] is None for f in j['fractions'])


def test_independent_histories_cover_a_model_start_inside_both_supports():
    T=fv.TemperatureHistory.linear_celsius((-1,.1),(80,98))
    Q=fv.FlowHistory((-.5,.03,.2),(1e-6,3e-6),'constant')
    r=run(T,Q,t_span_s=(.01,.08),observation_times_s=(.01,.03,.08),fraction_bounds_s=(.01,.04,.08))
    assert r.observations.hydraulic_volume_m3[0]==0 and r.observations.outlet_solute_kg[0]==0
    assert r.M0_fv_kg==pytest.approx(fv._System('caffeine',1.7,4).M0(T.value_K(.01)),rel=2e-15)
    assert r.observations.hydraulic_volume_m3[-1]==pytest.approx(1e-6*.02+3e-6*.05,rel=1e-15)

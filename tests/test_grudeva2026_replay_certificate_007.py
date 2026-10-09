"""Manufactured exact-arithmetic certificates; no canonical arrays or solver."""
from copy import deepcopy
from fractions import Fraction

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_replay_certificate_007 as c
from tools import grudeva2026_replay_reassessment_007_invoke as ctl


def point(t=100.,h=1.0001e-9,order=3,scale=1.):
    end=t+1e-9;d=np.array([.8,-.02,.001,-.0001][:order+1])*scale
    shifts=end-h*np.arange(order);den=h*(1+np.arange(order))
    tf,ef,hf=map(c.rational,(t,end,h))
    ideal=c.basis(tf,[ef-j*hf for j in range(order)],[(j+1)*hf for j in range(order)])
    expected=float(c.rational(d[0])+sum((c.rational(v)*p for v,p in zip(d[1:],ideal)),Fraction(0)))
    actual=float(c.obs.polynomial(t,d,shifts,den))
    return dict(order=order,t=t,interval=[t,end],dense_h=h,differences=d.tolist(),shifts=shifts.tolist(),
        denominators=den.tolist(),accepted_value=expected,reconstructed_value=actual,
        signed_difference=actual-expected,threshold=c.reassess.THRESHOLD,accepted_index=0,state_index=0,
        component='manufactured',cell=None,mode=None)


def test_coordinate_rounding_has_independent_certificate_and_unchanged_residual():
    p=point();r=c.certify_point(p)
    assert abs(p['signed_difference'])>c.reassess.THRESHOLD
    assert r['passed'] and r['coordinate_bound']['approximate']>0
    assert abs(r['coefficient_residual']['approximate'])<c.reassess.THRESHOLD
    assert r['evaluation_bound']['approximate']<c.reassess.THRESHOLD


@pytest.mark.parametrize('fault',['coefficient','evaluation','shifts','denominators','order','outside','nonfinite'])
def test_certificate_rejects_real_errors(fault):
    p=point()
    if fault=='coefficient':p['differences'][0]+=1e-5
    if fault=='evaluation':p['reconstructed_value']+=1e-5
    if fault=='shifts':p['shifts'][1]=np.nextafter(p['shifts'][1],np.inf)
    if fault=='denominators':p['denominators'][1]*=1.01
    if fault=='order':p['order']=6
    if fault=='outside':p['t']=p['interval'][1]+1
    if fault=='nonfinite':p['differences'][0]=np.nan
    try:r=c.certify_point(p)
    except ValueError:return
    assert not r['passed']


def test_exact_coordinates_zero_factors_and_dense_step_difference():
    p=point(t=1.,h=.125)
    # q>=2 has zero factors at an exactly represented Newton node.
    p.update(t=1.,interval=[.875,1.125],dense_h=.125,shifts=[1.125,1.,.875],denominators=[.125,.25,.375])
    p['accepted_value']=p['reconstructed_value']=p['differences'][0]-p['differences'][1]
    p['signed_difference']=0.
    r=c.certify_point(p)
    assert r['passed'] and r['coordinate_bound']['numerator']=='0'
    assert p['dense_h']!=p['interval'][1]-p['interval'][0]


@pytest.mark.parametrize('scale',[.001,1.,8.])
def test_bound_scales_with_state(scale):
    a=c.certify_point(point());b=c.certify_point(point(scale=scale))
    assert b['passed']
    assert b['coordinate_bound']['approximate']==pytest.approx(scale*a['coordinate_bound']['approximate'])


def test_subnormal_and_cancelling_coefficients():
    p=point();p['differences']=[5e-324,-5e-324,0.,0.]
    p['accepted_value']=p['reconstructed_value']=5e-324;p['signed_difference']=0.
    assert c.certify_point(p)['passed']
    p=point();p['differences']=[.8,.8,0.,0.]
    p['accepted_value']=float(c.rational(.8)+c.rational(.8)*(c.rational(p['t'])-c.rational(p['interval'][1]))/c.rational(p['dense_h']))
    p['reconstructed_value']=float(c.obs.polynomial(p['t'],np.array(p['differences']),np.array(p['shifts']),np.array(p['denominators'])))
    assert c.certify_point(p)['passed']


def test_certificate_cannot_cover_events_or_native_fidelity_failures():
    live=dict(allowance_fraction=0.,event_state_error=0.,accepted_state_error=1.)
    assert c.replay_admission(live,True)
    assert not c.replay_admission(live,False)
    live['event_state_error']=1.;assert not c.replay_admission(live,True)
    live['event_state_error']=0.;live['allowance_fraction']=2.;assert not c.replay_admission(live,True)


@pytest.mark.parametrize('fault',['missing','duplicate','extra','maximum','threshold'])
def test_offender_coverage_is_exhaustive(fault):
    p=point();d=dict(findings=[p],exceeding_locations=1,maximum=abs(p['signed_difference']))
    if fault=='missing':d['findings']=[]
    if fault=='duplicate':d['findings']=[p,deepcopy(p)];d['exceeding_locations']=2
    if fault=='extra':d['findings'].append(deepcopy(p))
    if fault=='maximum':d['maximum']*=2
    if fault=='threshold':p['threshold']*=2
    with pytest.raises(ValueError):c.validate_offenders(d)


def test_worker_stage_identity_binding():
    start=dict(stage='certify');audit=dict(starts={'certify-0001':start})
    ctl.validate_worker_stage(start,'certify','certify-0001',audit)
    with pytest.raises(ValueError,match='stage mismatch'):ctl.validate_worker_stage(start,'analyze','certify-0001',audit)
    with pytest.raises(ValueError,match='ordinal mismatch'):ctl.validate_worker_stage(start,'certify','certify-0002',audit)


def test_nested_binding_preserves_safe_hash_admission(tmp_path):
    folder=tmp_path/'nested';folder.mkdir();path=folder/'value.json';path.write_text('{"x": 1}')
    binding=dict(file='nested/value.json',sha256=c.obs.sha(path))
    assert c.bound_relative(tmp_path,binding)=={'x':1}
    with pytest.raises(ValueError):c.bound_relative(tmp_path,dict(binding,sha256='wrong'))
    with pytest.raises(ValueError):c.bound_relative(tmp_path,dict(binding,file='../outside.json'))
    with pytest.raises(ValueError):c.bound_relative(tmp_path,dict(binding,file=str(path)))
    link=folder/'escape';link.symlink_to(tmp_path.parent)
    with pytest.raises(ValueError):c.bound_relative(tmp_path,dict(binding,file='nested/escape/outside.json'))


def test_actual_gradual_underflow_guard_and_flushing_rejection(monkeypatch):
    c.floating_model()
    monkeypatch.setattr(c.np,'multiply',lambda a,b:np.zeros_like(a))
    with pytest.raises(ValueError,match='gradual underflow'):c.floating_model()


def manufactured_report():
    audits={k:True for k in c.task.GATES}
    metrics={k:dict(passed=True,included=1,unavailable=0) for k in c.reassess.report.BUDGETS}
    rows={f'007-{name}':dict(passed=True,gates=deepcopy(audits)) for name in
          ('repeat_512','modes_fine','time_fine','bed_fine')}
    rows['007-control_512']=dict(passed=True,neutrality={'passed':True})
    rows['007-repeat_512']['repeatability']={'passed':True}
    rows['007-combined']=dict(passed=False,status='EXECUTION_INCOMPLETE')
    prior=dict(disposition=c.task.INCOMPLETE,baseline_reuse_validated=True,baseline_gates=audits,
        rows=rows,prerequisites={'manufactured':{'passed':True}},
        comparisons={name:deepcopy(metrics) for name in ('modes_fine','time_fine','bed_fine','combined')},
        reasons={name:[] for name in ('integration_software','source_environment_rights','resources_execution',
            'individual_audits','refinements','neutrality_repeatability','persistence_replay_observation')})
    prior['reasons']['persistence_replay_observation']=['original failure']
    analysis=dict(gates=deepcopy(audits),individual_details={k:{} for k in audits},audits={},refinement=deepcopy(metrics))
    return prior,analysis


def test_full_assembly_does_not_rewrite_history():
    prior,analysis=manufactured_report();before=deepcopy(prior)
    final=c.assemble_qualification(prior,analysis,True,{}, {})
    assert final['disposition']==c.task.QUALIFIED and prior==before
    assert final['historical_reasons']==before['reasons']
    assert final['rows']['007-combined']['historical_execution']==before['rows']['007-combined']


@pytest.mark.parametrize('fault,category',[('replay','persistence_replay_observation'),
    ('audit','individual_audits'),('refinement','refinements'),('coverage','individual_audits'),
    ('neutrality','neutrality_repeatability'),('integration','integration_software')])
def test_full_assembly_reports_current_failures(fault,category):
    prior,analysis=manufactured_report();passed=True
    if fault=='replay':passed=False
    if fault=='audit':analysis['gates']['conservation']=False
    if fault=='refinement':analysis['refinement']['cup']['passed']=False
    if fault=='coverage':del analysis['individual_details']['conservation']
    if fault=='neutrality':prior['rows']['007-control_512']['neutrality']['passed']=False
    if fault=='integration':prior['reasons']['integration_software']=['manufactured software failure']
    final=c.assemble_qualification(prior,analysis,passed,{}, {})
    assert final['disposition']==c.task.INCOMPLETE and final['reasons'][category]

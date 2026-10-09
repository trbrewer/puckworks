"""Cheap manufactured control-flow tests; no canonical 006 fixture or trajectory."""
from dataclasses import asdict
import json
import os
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_spatial_resolution_006 as task
from puckworks.analysis import grudeva2026_spatial_resolution_006_report as report
from puckworks.analysis import grudeva2026_baseline_observation_005 as obs
from tools import grudeva2026_spatial_resolution_006_invoke as controller


@pytest.mark.parametrize('key,value', [('cells',128),('cells',256),('cells',1024),('modes',64),
    ('front_mesh_power',1.),('rtol',2e-9),('atol',2e-11),('max_step',.025)])
def test_exact_candidate_only(key,value):
    assert asdict(task.candidate_controls(task.CANDIDATE)) == task.CANDIDATE
    with pytest.raises(ValueError,match='exact 512/32'):
        task.candidate_controls(dict(task.CANDIDATE,**{key:value}))


def test_literal_fixture_eligibility_and_independent_oracle(monkeypatch):
    plan=task.fixture_plan()
    ages=[c['t']-z/.2 for c in plan['cases'] for z in c['z']]
    assert (len(ages),sum(a>=.02 for a in ages),sum(a<.02 for a in ages))==(139,84,55)
    # One small manufactured spectrum/case: corrupting the tested readout cannot alter the oracle.
    tr=SimpleNamespace(n=8,m=2,weights=np.array([.6,.4]),rates=np.array([1.,3.]),faces=np.linspace(0,1,9))
    case={'t':.2,'z':[0.,.02,.04]}
    original,averages,_=task.diagnosis.fixture_case(tr,case,[0.,0.,0.])
    monkeypatch.setattr(obs,'cell_reconstruction',lambda faces,values,z:np.zeros((2,len(z))))
    corrupted,same,_=task.diagnosis.fixture_case(tr,case,[0.,0.,0.])
    np.testing.assert_array_equal(averages,same)
    np.testing.assert_array_equal(original['exact'],corrupted['exact'])
    assert np.any(original['actual']!=corrupted['actual'])


def synthetic_family():
    plan=task.fixture_plan()
    return dict(cases=[dict(t=c['t'],z=c['z'],age=[c['t']-z/.2 for z in c['z']],
        signed_error=[0. for z in c['z']],positive_age_mask=[c['t']-z/.2>=.02 for z in c['z']]) for c in plan['cases']],
        independent_average_checks=[dict(t=0.,cell=0,mode=0,signed_difference=0.,quadrature_estimated_error=0.) for _ in range(18)])


def test_complete_support_younger_endpoint_and_reference_failure():
    family=synthetic_family();summary=task.summarize_fixture_family(family)
    assert (summary['requested'],summary['included'],summary['excluded'],summary['unavailable'])==(139,84,55,0)
    assert summary['younger']['included']==55
    assert summary['advancing_front_assignment']
    family['independent_average_checks'][0]['quadrature_estimated_error']=1e-5
    assert not task.summarize_fixture_family(family)['independent_reference']['passed']
    family['cases'][0]['signed_error'][0]=float('nan')
    with pytest.raises(ValueError,match='nonfinite'):task.summarize_fixture_family(family)


def test_failed_screen_prevents_production_and_tamper_rejected(tmp_path,monkeypatch):
    monkeypatch.setattr(task,'DOCS',tmp_path)
    (tmp_path/'PLAN.json').write_text('{}')
    path=tmp_path/(task.ATTEMPTS[0]+'.json')
    task.write_new(path,dict(task=task.TASK,passed=False,plan_sha256=obs.sha(tmp_path/'PLAN.json')))
    audit={'ends':{task.ATTEMPTS[0]:dict(exit_code=0,artifact_sha256=obs.sha(path))}}
    with pytest.raises(ValueError,match='production forbidden'):task.require_screen(tmp_path,{},audit)
    path.write_text('{}')
    with pytest.raises(ValueError,match='identity mismatch'):task.require_screen(tmp_path,{},audit)


def test_source_mismatch_and_immutable_output(tmp_path,monkeypatch):
    monkeypatch.setattr(task,'ROOT',tmp_path)
    source=tmp_path/'dependency.py';source.write_text('original')
    plan=dict(task=task.TASK,candidate=task.CANDIDATE,scientific_sources={'dependency.py':obs.sha(source)},adapter_sources={})
    source.write_text('changed')
    with pytest.raises(ValueError,match='source mismatch'):task.verify_sources(plan)
    path=tmp_path/'retained.json';task.write_new(path,{'original':True})
    with pytest.raises(FileExistsError):task.write_new(path,{'original':False})
    assert obs.read_json(path)=={'original':True}


def test_006_capture_identity_public_preservation_and_original_exception(tmp_path,monkeypatch):
    from puckworks.models.grudeva2026 import reduced
    monkeypatch.setattr(task,'DOCS',tmp_path)
    (tmp_path/'PLAN.json').write_text('{}')
    result={'status':'COMPLETED','manufactured':[1.,2.,3.]}
    calls=[]
    def simulate(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace(canonical_json=lambda:obs.canonical(result))
    monkeypatch.setattr(reduced,'simulate',simulate)
    # Force a diagnostic failure after the public checkpoint; no real solve_ivp call.
    monkeypatch.setattr(task.inherited,'check_run',lambda *a:['manufactured observation failure'])
    output=tmp_path/'capture.json'
    with pytest.raises(ValueError,match='manufactured observation failure'):
        task.capture(output,dict(candidate=task.CANDIDATE,adapter_sources={}))
    meta=obs.read_json(output)
    assert meta['task']==task.TASK and meta['row']==task.ROW and meta['schema']==obs.SCHEMA
    assert meta['attempt']==task.ATTEMPTS[1] and meta['status']=='EXECUTED_UNQUALIFIED'
    assert obs.read_json(tmp_path/meta['public_checkpoint']['file'])==result
    assert asdict(calls[0]['controls'])==task.CANDIDATE
    assert calls[0]['times']==obs.requests()['public_times']
    assert calls[0]['profile_z']==obs.requests()['public_z']
    error=RuntimeError('original solver exception')
    def failed(**kwargs):raise error
    monkeypatch.setattr(reduced,'simulate',failed)
    original=reduced.solve_ivp
    with pytest.raises(RuntimeError) as caught:task.capture(tmp_path/'exception.json',dict(candidate=task.CANDIDATE,adapter_sources={}))
    assert caught.value is error and reduced.solve_ivp is original
    assert obs.read_json(tmp_path/'exception.json')['original_exception']['message']==str(error)


def ledger(tmp_path):
    path=tmp_path/'invocations.jsonl'
    task.write_new(path,dict(event='freeze',task=task.TASK,plan_sha256='frozen',limits=controller.LIMITS))
    return path


def start(path,index,ceiling=None):
    controller.append(path,dict(event='start',name=task.ATTEMPTS[index],kind=controller.KINDS[index],
        ceiling=controller.ALLOCATIONS[index] if ceiling is None else ceiling,memory_bytes=controller.MEMORY,plan_sha256='frozen'))


def end(path,index,seconds):
    controller.append(path,dict(event='end',name=task.ATTEMPTS[index],seconds=seconds,exit_code=0))


def test_locked_ledger_unresolved_duplicate_sequence_and_reservations(tmp_path):
    path=ledger(tmp_path)
    a=controller.accounting(tmp_path,'frozen')
    assert controller.allocation(0,a)==90
    start(path,0)
    a=controller.accounting(tmp_path,'frozen')
    assert a['short']==1 and a['charged_or_reserved_seconds']==90 and not a['passed']
    with pytest.raises(ValueError,match='unresolved'):controller.allocation(1,a)
    end(path,0,50.)
    a=controller.accounting(tmp_path,'frozen')
    assert controller.allocation(1,a)==290
    with pytest.raises(ValueError,match='duplicate'):controller.allocation(0,a)
    with pytest.raises(ValueError,match='execution order'):controller.allocation(2,a)
    start(path,1);end(path,1,290.)
    start(path,2);end(path,2,180.)
    a=controller.accounting(tmp_path,'frozen')
    assert (a['full'],a['short'],a['seconds'])==(1,2,520.)
    with pytest.raises(ValueError):controller.allocation(2,a)
    start(path,2)
    with pytest.raises(ValueError,match='duplicate'):controller.accounting(tmp_path,'frozen')


def test_aggregate_per_call_and_address_space_enforcement(tmp_path):
    path=ledger(tmp_path);start(path,0);end(path,0,301.)
    assert not controller.accounting(tmp_path,'frozen')['passed']
    a=dict(passed=True,reasons=[],starts={task.ATTEMPTS[0]:{}},full=0,short=1,seconds=500.)
    with pytest.raises(ValueError,match='reserve'):controller.allocation(1,a)
    code='from tools.grudeva2026_spatial_resolution_006_invoke import child_limits; import os,resource,json; child_limits(os.getppid()); print(json.dumps(resource.getrlimit(resource.RLIMIT_AS)))'
    env=dict(os.environ,PYTHONPATH=str(task.ROOT),OPENBLAS_NUM_THREADS='1')
    result=subprocess.run([sys.executable,'-c',code],env=env,capture_output=True,text=True,check=True)
    assert json.loads(result.stdout)==[8589934592,8589934592]


def test_worker_cannot_run_without_live_controller(tmp_path):
    args=SimpleNamespace(action=task.ATTEMPTS[0],evidence=tmp_path)
    with pytest.raises(ValueError,match='requires the 006 controller'):controller.worker(args,{})


def test_failure_first_and_no_empty_support_promotion():
    passing={'x':dict(passed=True,included=1,unavailable=0)}
    assert report.disposition(False,True,{'all':True},passing)=='B'
    assert report.disposition(True,True,{'inlet':False},passing)=='C'
    assert report.disposition(True,False,{'all':True},passing)=='C'
    assert report.disposition(True,True,{'all':True},{'x':dict(passed=True,included=0,unavailable=0)})=='C'
    assert report.disposition(True,True,{'all':True},passing)=='C'  # omitted panels cannot qualify
    assert not report.extrema([],1.)['passed']
    assert not report.extrema([(float('nan'),{'t':1.})],1.)['passed']


def test_full_gate_panel_is_required_for_positive_conclusion():
    historical=obs.read_json(task.OLD_DOCS/'ATTRIBUTION.json')['qualification']
    gates=dict.fromkeys(historical['runs']['bed_fine']['gates'],True)
    panel={name:dict(passed=True,included=1,unavailable=0) for name in report.inherited.BUDGETS}
    assert report.disposition(True,True,gates,panel)=='A'
    gates['cup_quadrature']=False
    assert report.disposition(True,True,gates,panel)=='C'


def test_public_checkpoint_failure_still_retains_returned_result(tmp_path,monkeypatch):
    from puckworks.models.grudeva2026 import reduced
    monkeypatch.setattr(task,'DOCS',tmp_path)
    (tmp_path/'PLAN.json').write_text('{}')
    public={'complete':'manufactured public Result'}
    monkeypatch.setattr(reduced,'simulate',lambda **kw:SimpleNamespace(canonical_json=lambda:obs.canonical(public)))
    original=task.write_new
    def fail_checkpoint(path,value):
        if str(path).endswith('-public-result.json'):raise OSError('manufactured checkpoint failure')
        original(path,value)
    monkeypatch.setattr(task,'write_new',fail_checkpoint)
    with pytest.raises(OSError,match='checkpoint failure'):
        task.capture(tmp_path/'retained.json',dict(candidate=task.CANDIDATE,adapter_sources={}))
    saved=obs.read_json(tmp_path/'retained.json')
    assert saved['public_result']==public and saved['public_checkpoint_failure']


def test_controller_lock_excludes_concurrent_admission(tmp_path):
    import fcntl
    with (tmp_path/'controller.lock').open('a') as first:
        fcntl.flock(first,fcntl.LOCK_EX|fcntl.LOCK_NB)
        with (tmp_path/'controller.lock').open('a') as second:
            with pytest.raises(BlockingIOError):fcntl.flock(second,fcntl.LOCK_EX|fcntl.LOCK_NB)


def test_frozen_external_root_rejects_fresh_directory_reset(tmp_path):
    evidence=tmp_path/'006';historical=tmp_path/'005'
    plan=dict(evidence_root_sha256=obs.digest(str(evidence.resolve())),historical_root_sha256=obs.digest(str(historical.resolve())))
    controller.verify_roots(evidence,historical,plan)
    with pytest.raises(ValueError,match='consumption cannot move'):
        controller.verify_roots(tmp_path/'another-ledger',historical,plan)
    with pytest.raises(ValueError,match='historical evidence root'):
        controller.verify_roots(evidence,tmp_path/'different-005',plan)


@pytest.mark.parametrize('field,value',[('signed_difference',float('nan')),('signed_difference',float('inf')),
    ('quadrature_estimated_error',float('nan')),('quadrature_estimated_error',-1.)])
def test_nonfinite_or_negative_reference_uncertainty_cannot_pass(field,value):
    family=synthetic_family();family['independent_average_checks'][1][field]=value
    result=task.summarize_fixture_family(family)['independent_reference']
    assert not result['passed'] and result['unavailable']==1 and result['included']==17


def test_screen_early_failure_retains_all_unavailable_support(tmp_path,monkeypatch):
    monkeypatch.setattr(task,'DOCS',tmp_path);(tmp_path/'PLAN.json').write_text('{}')
    def fail(*a,**k):raise ValueError('manufactured historical identity failure')
    monkeypatch.setattr(task,'historical_inputs',fail)
    with pytest.raises(ValueError,match='historical identity'):task.screen(tmp_path,tmp_path,{})
    result=obs.read_json(tmp_path/(task.ATTEMPTS[0]+'.json'))
    assert not result['passed'] and result['failure']['reason']=='manufactured historical identity failure'
    assert all(f['unavailable']==139 for mesh in result['meshes'].values() for f in mesh['families'].values())


def test_memory_failure_is_resource_D_with_preserved_partial(tmp_path,monkeypatch):
    def exhausted(*a,**k):raise MemoryError('manufactured fixed-memory exhaustion')
    monkeypatch.setattr(task,'historical_inputs',exhausted)
    result=report.reduce(tmp_path,tmp_path,{},dict(ends={}))
    assert result['conclusion']=='D' and result['disposition']=='FIXED_RESOURCE_MEMORY_EXHAUSTED'
    assert all(not r['passed'] and r['unavailable']>0 for r in result['comparison_256_512'].values())
    assert obs.read_json(tmp_path/(task.ATTEMPTS[2]+'.json'))['integrity_reasons']


def test_three_grid_uses_one_physical_stencil_and_rejects_missing_domain(monkeypatch):
    faces={'128':np.array([0.,.2,.4,.6,.8,1.]),
           '256':np.linspace(0,1,11),'512':np.linspace(0,1,21)}
    offsets={'128':.03,'256':.01,'512':.005}
    trajectories={k:SimpleNamespace(grid=k,arrival=1.) for k in faces}
    def point(tr,t,z):
        f=faces[tr.grid];a,b=f[:-1],f[1:]
        means=1+(a*a+a*b+b*b)/3+offsets[tr.grid]
        p=dict(grain_mean=1+z*z+offsets[tr.grid],grain_age=1.,front=float(f[-1]),
               point_reconstruction_supported=True)
        return p,f,means
    monkeypatch.setattr(report.attribution,'point',point)
    r=report.three_grid(trajectories,2.,.5,['manufactured'])
    assert r['common_three_grid']['supported']
    assert set(r['common_three_grid']['projected_averages'])=={'128','256','512'}
    assert all(abs(v['closure'])<1e-14 for v in r['common_three_grid']['components'].values())
    faces['512']=np.linspace(0,.65,21)  # point exists, complete coarse stencil does not
    r=report.three_grid(trajectories,2.,.5,['manufactured'])
    assert not r['common_three_grid']['supported']
    assert r['values']['512'] is not None

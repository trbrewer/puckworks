"""Cheap manufactured orchestration tests; no canonical solver/fixture campaign."""
from copy import deepcopy
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace

import pytest

from puckworks.analysis import grudeva2026_fine_baseline_qualification_007 as t
from tools import grudeva2026_fine_baseline_qualification_007_invoke as c


def audit():
    return dict(starts={},ends={},full=0,short=0,seconds=0.,passed=True,reasons=[],unresolved_starts=[])


@pytest.mark.parametrize('row',t.ROWS)
def test_fixed_rows(row):
    assert asdict(t.controls(row,t.ROWS[row]))==t.ROWS[row]
    for key,value in dict(cells=2048,modes=96,front_mesh_power=3,atol=1e-11).items():
        with pytest.raises(ValueError): t.controls(row,dict(t.ROWS[row],**{key:value}))
    assert t.ROWS['time_fine']['atol']==2e-11
    with pytest.raises(ValueError): t.controls('extra',t.BASE)












@pytest.mark.parametrize('modes,count',[(32,18),(64,24)])
def test_reference_identities_not_just_count(modes,count):
    # Manufacture zero residuals at literal inherited support; do not evaluate any
    # canonical point, cell average, quadrature, spectrum or reconstruction.
    frozen=t.previous.fixture_plan();cells=1024
    cases=[dict(t=s['t'],z=s['z'],age=[s['t']-z/.2 for z in s['z']],
        signed_error=[0.]*len(s['z']),positive_age_mask=[s['t']-z/.2>=.02 for z in s['z']]) for s in frozen['cases']]
    checks=[dict(t=frozen['cases'][s['case_index']]['t'],cell=s['cell']%cells,mode=k,
        signed_difference=0.,quadrature_estimated_error=0.) for s in frozen['independent_average_subset'] for k in sorted({0,31,modes-1,modes})]
    family=dict(cases=cases,independent_average_checks=checks)
    result=t.fixture_summary(family,cells,modes,frozen)
    assert result['independent_reference']['requested']==count
    assert result['eligible']['included']==84 and result['younger']['included']==55
    assert result['independent_reference']['passed']
    family['independent_average_checks'][0]['mode']=4
    with pytest.raises(ValueError,match='identities'): t.fixture_summary(family,cells,modes,frozen)


def test_reference_uncertainty_and_missing_points_fail():
    frozen=t.previous.fixture_plan();cells=512;modes=32
    cases=[dict(t=s['t'],z=s['z'],age=[s['t']-z/.2 for z in s['z']],signed_error=[0.]*len(s['z']),
        positive_age_mask=[s['t']-z/.2>=.02 for z in s['z']]) for s in frozen['cases']]
    checks=[dict(t=frozen['cases'][s['case_index']]['t'],cell=s['cell']%cells,mode=k,
        signed_difference=0.,quadrature_estimated_error=2e-11) for s in frozen['independent_average_subset'] for k in (0,31,32)]
    r=t.fixture_summary(dict(cases=cases,independent_average_checks=checks),cells,modes,frozen)
    assert not r['independent_reference']['passed']
    assert r['eligible']['passed']  # independent validity is separate


def test_complete_public_and_scientific_envelope_equality():
    base={k:{} for k in ('public_result','controls','parameters','requests','sources','environment','geometry','state_layout')}
    base['segments']=[{k:0 for k in t.SEGMENT_SCIENCE}]
    other=deepcopy(base);other.update(task=t.TASK,attempt='repeat',phase_seconds=999)
    assert t.repeat_equality(base,other,{'audits':1},{'audits':1})['passed']
    other['public_result']['unavailable_reasons']={'x':'missing'}
    assert not t.repeat_equality(base,other,{}, {})['passed']
    other=deepcopy(base);other['segments'][0]['array_manifest']={'D_0':'different'}
    assert not t.repeat_equality(base,other,{}, {})['passed']
    assert not t.repeat_equality(base,base,{'audits':1},{'audits':2})['passed']


def test_missing_family_and_support_cannot_pass():
    metrics={k:dict(passed=True,included=1,unavailable=0) for k in t.report.BUDGETS}
    assert t.comparisons_pass(metrics)
    metrics['grain_histories']['unavailable']=1
    assert not t.comparisons_pass(metrics)
    metrics['grain_histories']['unavailable']=0;metrics['grain_histories']['included']=0
    assert not t.comparisons_pass(metrics)
    del metrics['grain_histories'];assert not t.comparisons_pass(metrics)


def test_control_does_not_enter_capture(tmp_path,monkeypatch):
    from puckworks.models.grudeva2026 import reduced
    from puckworks import rights
    calls=[]
    request=dict(public_times=[0.,8.],public_z=[0.,1.])
    plan=dict(rows=t.ROWS,requests=request,parameters={'manufactured':True},adapter_sources={})
    public=dict(status='COMPLETED',values=[1],unavailable_reasons={})
    class Result:
        def canonical_json(self): return t.obs.canonical(public)
    monkeypatch.setattr(reduced,'simulate',lambda **kw:(calls.append(kw) or Result()))
    def forbidden(*args,**kwargs): raise AssertionError('capture entered by control')
    monkeypatch.setattr(t.obs,'capture_returns',forbidden)
    monkeypatch.setattr(rights,'may_execute_locally',lambda n:SimpleNamespace(allowed=True))
    monkeypatch.setattr(t,'validate_new',lambda *a,**k:None)
    original_bound=t.bound_json
    monkeypatch.setattr(t,'bound_json',lambda folder,binding: {'public_result':public} if binding=={} else original_bound(folder,binding))
    monkeypatch.setattr(t.obs,'sha',lambda p:'hash')
    plan['reuse']={'metadata':{}}
    result=t.simulate_row(tmp_path,tmp_path,plan,'control_512')
    assert len(calls)==1 and result['neutrality']['passed'] and result['segments']==[]
    assert calls[0]['times']==[0.,8.]


@pytest.mark.parametrize('field,value',[('task','005'),('row','baseline_512'),('horizon',.4),('environment',{}),('adapter_sources',{'bad':'x'}),('observed',True)])
def test_genuine_metadata_rejects_mismatch(tmp_path,monkeypatch,field,value):
    from puckworks.models.grudeva2026.reduced import Parameters
    requests=t.obs.requests();parameters=asdict(Parameters());environment=t.obs.environment()
    plan=dict(requests=requests,parameters=parameters,adapter_sources={},environment=environment)
    monkeypatch.setattr(t.obs,'sha',lambda p:'hash')
    meta=dict(task=t.TASK,attempt='007-control_512',row='control_512',horizon=8.,controls=t.BASE,observed=False,
        matrix_sha256='hash',adapter_sources={},environment=environment,parameters=parameters,sources=t.obs.sources(),
        requests=requests,request_hashes={k:t.obs.digest(v) for k,v in requests.items()})
    meta[field]=value
    with pytest.raises(ValueError): t.validate_new(meta,'control_512',plan)






def test_orphan_worker_and_pilot_events(monkeypatch):
    monkeypatch.delenv('GRUDEVA007_LOCK_FD',raising=False)
    with pytest.raises(ValueError,match='controller'): c.worker(SimpleNamespace(action='007-pilot'),{},{})
    monkeypatch.setattr(t.report,'numeric_gates',lambda *a:{k:True for k in t.GATES})
    observed=dict(audits={'horizon':.4},events=[],arrival=None,records=[[.4,.08]],z=[0.,.1],activation=[0.,None],
        grain_history_z=[.025,.9],grain_history_activation=[.1,None])
    assert all(t.pilot_gates(observed,{ }).values())
    observed['activation'][1]=.5
    assert not t.pilot_gates(observed,{})['activation_support']






def test_reduction_after_failed_a_retains_missing_rows(tmp_path,monkeypatch):
    # Keep the exact helper behavior; all inputs here are manufactured metadata.
    planfile=tmp_path/'PLAN.json';t.write_new(planfile,{'manufactured':True})
    monkeypatch.setattr(t,'DOCS',tmp_path)
    r=dict(task=t.TASK,plan_sha256=t.obs.sha(planfile),passed=False,
        failure=dict(type='ValueError',reason='source mismatch',category='source_environment_rights'))
    t.write_new(tmp_path/'007-readout.json',r)
    a=audit();a['ends']={'007-readout':dict(artifact_sha256=t.obs.sha(tmp_path/'007-readout.json'),exit_code=1)}
    result=t.reduction(tmp_path,tmp_path,dict(reuse={'metadata':{'file':'original006'}}),a)
    assert result['disposition']==t.INCOMPLETE
    assert result['rows']['007-control_512']['status']=='NOT_RUN'
    assert set(result['comparisons'])==set(t.REFINEMENTS)
    assert all(not t.comparisons_pass(v) for v in result['comparisons'].values())
    assert result['reasons']['source_environment_rights'][0]['reason']=='source mismatch'


def test_repeat_is_separate_captured_call(tmp_path,monkeypatch):
    from contextlib import contextmanager
    from puckworks.models.grudeva2026 import reduced
    from puckworks import rights
    calls=[];entered=[]
    @contextmanager
    def capture(module):
        entered.append(module);yield []
    def simulate(**kwargs):
        calls.append(kwargs)
        raise RuntimeError('manufactured stop after independent production entry')
    monkeypatch.setattr(t.obs,'capture_returns',capture)
    monkeypatch.setattr(reduced,'simulate',simulate)
    monkeypatch.setattr(rights,'may_execute_locally',lambda n:SimpleNamespace(allowed=True))
    monkeypatch.setattr(t.obs,'sha',lambda p:'hash')
    plan=dict(rows=t.ROWS,requests=dict(public_times=[0.,8.],public_z=[0.,1.]),parameters={},adapter_sources={})
    with pytest.raises(RuntimeError,match='manufactured'):
        t.simulate_row(tmp_path,tmp_path,plan,'repeat_512')
    assert entered==[reduced] and len(calls)==1
    assert t.obs.read_json(tmp_path/'007-repeat_512.json')['original_exception']['type']=='RuntimeError'


def test_plan_and_horizon_binding(monkeypatch):
    from puckworks.models.grudeva2026.reduced import Parameters
    p=dict(task=t.TASK,rows=t.ROWS,horizon=8.,pilot_horizon=.4,parameters=asdict(Parameters()),
        requests=t.obs.requests(),pilot_requests=t.obs.requests(.4),segment_science_fields=list(t.SEGMENT_SCIENCE),
        scientific_sources={},adapter_sources={},contract_sha256='hash')
    monkeypatch.setattr(t.obs,'sha',lambda p:'hash')
    t.verify_plan(p)
    for field,val in [('horizon',.4),('pilot_horizon',8.),('pilot_requests',p['requests'])]:
        bad=dict(p,**{field:val})
        with pytest.raises(ValueError): t.verify_plan(bad)




def test_public_checkpoint_failure_keeps_returned_result(tmp_path,monkeypatch):
    from puckworks.models.grudeva2026 import reduced
    from puckworks import rights
    public=dict(status='COMPLETED',values=[1],unavailable_reasons={})
    monkeypatch.setattr(reduced,'simulate',lambda **kw:SimpleNamespace(canonical_json=lambda:t.obs.canonical(public)))
    monkeypatch.setattr(rights,'may_execute_locally',lambda n:SimpleNamespace(allowed=True))
    monkeypatch.setattr(t.obs,'sha',lambda p:'hash')
    original=t.write_new
    def write(path,value):
        if path.name.endswith('-public-result.json'): raise OSError('manufactured checkpoint failure')
        original(path,value)
    monkeypatch.setattr(t,'write_new',write)
    plan=dict(rows=t.ROWS,requests=dict(public_times=[0.,8.],public_z=[0.,1.]),parameters={},adapter_sources={})
    with pytest.raises(OSError,match='checkpoint'): t.simulate_row(tmp_path,tmp_path,plan,'control_512')
    assert t.obs.read_json(tmp_path/'007-control_512.json')['public_result']==public


def continuation_ledger(tmp_path):
    c.append(tmp_path/'invocations.jsonl',dict(event='override',task=t.TASK,policy_sha256='p'))
    return tmp_path/'invocations.jsonl'


def continuation_start(key='007-pilot-0001',stage='007-pilot'):
    return dict(event='start',execution_id=key,stage=stage,kind='short' if stage in ('007-pilot','007-reduction') else 'full',
        directory='attempts/'+key,policy_sha256='p')


def test_no_task_deadlines_quotas_or_memory_assignment():
    import ast
    tree=ast.parse(Path(c.__file__).read_text())
    forbidden={'setrlimit','setitimer','alarm'}
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)]
    assert not any(isinstance(n.func,ast.Attribute) and n.func.attr in forbidden for n in calls)
    assert not any(k.arg=='timeout' for n in calls for k in n.keywords)
    assert all(value is None for value in c.UNLIMITED.values())


def test_accounting_has_no_elapsed_or_attempt_cap(tmp_path):
    ledger=continuation_ledger(tmp_path)
    for i in range(10):
        key=f'007-pilot-{i+1:04d}'
        c.append(ledger,continuation_start(key))
        c.append(ledger,dict(event='end',execution_id=key,seconds=100000.,exit_code=1,failure_class='operational'))
    a=c.accounting(tmp_path,'p')
    assert a['passed'] and a['short']==10 and a['seconds']==1000000.


@pytest.mark.parametrize('problem',['duplicate','concurrent','wrong_policy','unsafe_path','unmatched_end','nan'])
def test_continuation_ledger_integrity(tmp_path,problem):
    ledger=continuation_ledger(tmp_path);s=continuation_start()
    if problem=='wrong_policy': s['policy_sha256']='other'
    if problem=='unsafe_path': s['directory']='../../elsewhere'
    c.append(ledger,s)
    if problem=='duplicate':
        c.append(ledger,dict(event='end',execution_id=s['execution_id'],seconds=1.,exit_code=0))
        c.append(ledger,s)
    if problem=='concurrent': c.append(ledger,continuation_start('007-pilot-0002'))
    if problem=='unmatched_end': c.append(ledger,dict(event='end',execution_id='other',seconds=1.))
    if problem=='nan':
        with ledger.open('a') as f: f.write('{"event":"end","execution_id":"007-pilot-0001","seconds":NaN}\n')
    with pytest.raises(ValueError): c.accounting(tmp_path,'p')


def test_live_unresolved_execution_cannot_be_restarted(tmp_path,monkeypatch):
    ledger=continuation_ledger(tmp_path);s=continuation_start();s.update(controller={'pid':123},wall_start=0.)
    c.append(ledger,s);a=c.accounting(tmp_path,'p')
    assert not a['passed']
    with pytest.raises(ValueError,match='unresolved'): c.prerequisites(tmp_path,'007-pilot',a)
    monkeypatch.setattr(c,'alive',lambda identity:True)
    with pytest.raises(ValueError,match='still active'): c.reconcile(tmp_path,a)
    assert c.accounting(tmp_path,'p')['unresolved_starts']==['007-pilot-0001']


def test_verified_crash_is_closed_and_charged(tmp_path,monkeypatch):
    ledger=continuation_ledger(tmp_path);s=continuation_start();s.update(controller={'pid':123},wall_start=1.)
    c.append(ledger,s);a=c.accounting(tmp_path,'p')
    monkeypatch.setattr(c,'alive',lambda identity:False)
    monkeypatch.setattr(c.time,'time',lambda:100001.)
    c.reconcile(tmp_path,a);a=c.accounting(tmp_path,'p')
    assert a['passed'] and a['seconds']==100000.
    assert a['ends'][s['execution_id']]['failure_class']=='controller_crash'


def test_operational_retry_is_explicit_and_never_scientific():
    a={'latest':{'007-pilot':'x'},'ends':{'x':{'failure_class':'operational'}}}
    with pytest.raises(ValueError): c.operational_retry(a,'007-pilot',None)
    c.operational_retry(a,'007-pilot','documented controller crash')
    for classification in ('scientific','integrity_or_scientific','none'):
        a['ends']['x']['failure_class']=classification
        with pytest.raises(ValueError): c.operational_retry(a,'007-pilot','try again')


def test_completed_reduction_reused_until_inputs_change():
    a=dict(latest={'007-pilot':'p','007-reduction':'r'},
        ends={'p':{'artifact_sha256':'old'},'r':{'exit_code':2}},
        starts={'r':{}})
    a['starts']['r']['input_signature']=c.input_signature(a)
    with pytest.raises(ValueError,match='already covers'): c.operational_retry(a,'007-reduction','unnecessary')
    a['ends']['p']['artifact_sha256']='new'
    c.operational_retry(a,'007-reduction','new completed input set')


def test_os_limits_are_observed_not_replaced(tmp_path,monkeypatch):
    monkeypatch.setattr(c.resource,'getrlimit',lambda n:(8*c.GIB,8*c.GIB))
    snapshot=c.capacity(tmp_path)
    assert snapshot['inherited_rlimit_as']==[8*c.GIB]*2
    assert 'requested_address_space_bytes' not in snapshot
    assert not c.safety_reasons(dict(snapshot,host_available_bytes=40*c.GIB,disk_free_bytes=100*c.GIB,cgroups=[]))


def test_pressure_requires_evidence_not_quiet_or_elapsed():
    s=dict(disk_free_bytes=100*c.GIB,disk_operating_margin_bytes=c.GIB,host_available_bytes=40*c.GIB,
        host_operating_margin_bytes=c.GIB,cgroups=[],process={'VmRSS':90*c.GIB},elapsed_seconds=1e12)
    assert c.safety_reasons(s,s)==[]
    low=dict(s,host_available_bytes=100,process={'VmRSS':91*c.GIB})
    assert c.safety_reasons(low,s)==[]
    assert c.safety_reasons(dict(low,process={'VmRSS':92*c.GIB}),low)


def test_pid_reuse_does_not_count_as_live(monkeypatch):
    monkeypatch.setattr(c,'process',lambda pid:dict(pid=pid,start_ticks=222,boot_id='b',state='R'))
    assert not c.alive(dict(pid=123,start_ticks=111,boot_id='b'))
    assert c.alive(dict(pid=123,start_ticks=222,boot_id='b'))


def test_policy_is_explicit_without_rewriting_scientific_plan(monkeypatch):
    from puckworks.models.grudeva2026.reduced import Parameters
    p=dict(task=t.TASK,rows=deepcopy(t.ROWS),horizon=8.,pilot_horizon=.4,parameters=asdict(Parameters()),
        requests=t.obs.requests(),pilot_requests=t.obs.requests(.4),segment_science_fields=list(t.SEGMENT_SCIENCE),
        scientific_sources={},adapter_sources={'adapter.py':'old'},contract_sha256='new')
    policy=dict(task=t.TASK,original_plan_sha256='new',original_adapter_sources={'adapter.py':'old'},adapter_sources={'adapter.py':'new'})
    monkeypatch.setattr(t.obs,'sha',lambda p:'new')
    before=deepcopy(p);t.verify_plan(p,policy);assert p==before
    policy['original_adapter_sources']={'adapter.py':'not original'}
    with pytest.raises(ValueError,match='ancestry'): t.verify_plan(p,policy)


@pytest.mark.parametrize('partial',[{'gates':{'conservation':False}}, {'neutrality':{'passed':False}},
    {'repeatability':{'passed':False}}, {'refinement':{}}, {'public_result':{'status':'FAILED'}}])
def test_scientific_stop_survives_later_operational_failure(tmp_path,monkeypatch,partial):
    ledger=continuation_ledger(tmp_path);s=continuation_start();s.update(controller={'pid':123},wall_start=0.)
    c.append(ledger,s);work=tmp_path/s['directory'];work.mkdir(parents=True)
    result=dict(partial,failure={'classification':'operational','type':'MemoryError'})
    t.write_new(work/'007-pilot.json',result)
    assert c.scientific_failure(result)
    monkeypatch.setattr(c,'alive',lambda identity:False)
    c.reconcile(tmp_path,c.accounting(tmp_path,'p'))
    a=c.accounting(tmp_path,'p');assert a['ends'][s['execution_id']]['failure_class']=='scientific'
    with pytest.raises(ValueError,match='scientific'): c.operational_retry(a,'007-pilot','controller died')


def test_dead_controller_completed_row_is_reused(tmp_path,monkeypatch):
    ledger=continuation_ledger(tmp_path);s=continuation_start();s.update(controller={'pid':123},wall_start=0.)
    c.append(ledger,s)
    monkeypatch.setattr(c,'alive',lambda identity:False)
    monkeypatch.setattr(c,'recovered_completion',lambda *a:0)
    c.reconcile(tmp_path,c.accounting(tmp_path,'p'),{}, {})
    end=c.accounting(tmp_path,'p')['ends'][s['execution_id']]
    assert end['exit_code']==0 and end['recovered_completion'] and end['controller_incident']
    assert end['termination'] is None


def test_null_output_retries_are_distinct_reduction_inputs():
    a=dict(latest={'007-pilot':'one'},ends={'one':{'artifact_sha256':None,'exit_code':1}})
    original=c.input_signature(a)
    a['latest']['007-pilot']='two';a['ends']['two']={'artifact_sha256':None,'exit_code':1}
    assert c.input_signature(a)!=original


def test_operational_reduction_can_retry_same_inputs():
    a=dict(latest={'007-pilot':'p','007-reduction':'r'},ends={'p':{'artifact_sha256':None},
        'r':{'exit_code':1,'failure_class':'operational'}},starts={'r':{}})
    a['starts']['r']['input_signature']=c.input_signature(a)
    c.operational_retry(a,'007-reduction','disk interruption investigated and resolved')


def test_receipt_failure_preserves_completed_row(tmp_path,monkeypatch):
    import json
    root=tmp_path/'evidence';work=root/'continuation/attempts/007-pilot-0001';work.mkdir(parents=True)
    docs=tmp_path/'docs';docs.mkdir();t.write_new(docs/'PLAN.json',{})
    policy=docs/'EXECUTION_POLICY_OVERRIDE.json';t.write_new(policy,{})
    monkeypatch.setattr(t,'DOCS',docs);monkeypatch.setattr(c,'POLICY',policy)
    result=dict(status='ROW_PASSED',passed=True,gates={'conservation':True})
    path=work/'007-pilot.json';t.write_new(path,result)
    def broken(*a): raise OSError('completion receipt write failed')
    monkeypatch.setattr(c,'worker',broken)
    monkeypatch.setattr(c,'accounting',lambda *a:{'starts':{'007-pilot-0001':{'stage':'007-pilot'}}})
    with pytest.raises(OSError,match='receipt'):
        c.main(['worker','--execution-id','007-pilot-0001','--evidence',str(root),'--prior',str(tmp_path/'prior'),'--historical',str(tmp_path/'history')])
    assert json.loads(path.read_text())==result
    assert (work/'worker-incident.json').exists()

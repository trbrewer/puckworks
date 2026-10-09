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


def test_reservations_and_failure_closeout():
    a=audit()
    assert sum(c.ALLOCATIONS.values())==4660
    assert c.allocations('007-readout',a)[0]==120
    with pytest.raises(ValueError): c.allocations('007-pilot',a)
    a.update(starts={'007-readout':{}},ends={'007-readout':{'exit_code':1}},short=1,seconds=15.)
    assert c.allocations('007-reduction',a)[0]==240
    with pytest.raises(ValueError): c.allocations('007-readout',a)
    a['seconds']=4561
    with pytest.raises(ValueError): c.allocations('007-reduction',a)
    a.update(passed=False,reasons=['unresolved start'])
    with pytest.raises(ValueError): c.allocations('007-reduction',a)


def ledger(tmp_path):
    p=tmp_path/'invocations.jsonl'
    c.append(p,dict(event='freeze',task=t.TASK,plan_sha256='p',limits=c.LIMITS))
    return p


def start(name='007-readout'):
    return dict(event='start',task=t.TASK,name=name,kind='short',plan_sha256='p',ceiling=c.ALLOCATIONS[name],memory_bytes=c.MEMORY)


@pytest.mark.parametrize('bad',['duplicate','concurrent','wrong_memory','wrong_plan','duration','nan','unresolved'])
def test_crash_accounting(tmp_path,bad):
    p=ledger(tmp_path);s=start()
    if bad=='wrong_memory': s['memory_bytes']=8*1024**3
    if bad=='wrong_plan': s['plan_sha256']='other'
    c.append(p,s)
    if bad in ('duplicate','concurrent'): c.append(p,start('007-readout' if bad=='duplicate' else '007-pilot'))
    if bad=='duration': c.append(p,dict(event='end',name='007-readout',seconds=121.,enforced_rlimit_as=[c.MEMORY]*2))
    if bad=='nan':
        with p.open('a') as f: f.write('{"event":"end","name":"007-readout","seconds":NaN}\n')
    if bad in ('duration','unresolved'):
        a=c.accounting(tmp_path,'p');assert not a['passed']
        if bad=='unresolved': assert a['charged_or_reserved_seconds']==120
    else:
        with pytest.raises(ValueError): c.accounting(tmp_path,'p')


def test_closed_failed_attempt_is_counted(tmp_path):
    p=ledger(tmp_path);c.append(p,start())
    c.append(p,dict(event='end',name='007-readout',seconds=3.,exit_code=-9,enforced_rlimit_as=[c.MEMORY]*2))
    a=c.accounting(tmp_path,'p')
    assert a['passed'] and a['short']==1 and a['seconds']==3.
    assert c.allocations('007-reduction',a)[0]==240


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


def test_root_binding_cannot_reset(tmp_path):
    args=SimpleNamespace(evidence=tmp_path/'a',prior=tmp_path/'b',historical=tmp_path/'c')
    plan={k+'_root_sha256':t.obs.digest(str(getattr(args,k).resolve())) for k in ('evidence','prior','historical')}
    c.roots(args,plan)
    args.evidence=tmp_path/'new'
    with pytest.raises(ValueError): c.roots(args,plan)


@pytest.mark.parametrize('available,limit,usage,free,allowed',[
    (40,64,1,100,True),(12,64,1,100,False),(40,20,1,100,False),
    (40,64,40,100,False),(40,64,1,8,False)])
def test_32_gib_admission_not_old_8(tmp_path,monkeypatch,available,limit,usage,free,allowed):
    original=Path.read_text
    def read(path,*a,**k):
        s=str(path)
        if s=='/proc/meminfo': return f'MemAvailable: {available*1024**2} kB\n'
        if s=='/proc/self/status': return 'VmSize: 1024 kB\nVmRSS: 512 kB\n'
        if s=='/proc/self/cgroup': return '0::/\n'
        if s.endswith('memory.current'): return str(usage*c.GIB)
        if s.endswith(('memory.max','memory.high')): return str(limit*c.GIB)
        return original(path,*a,**k)
    monkeypatch.setattr(Path,'read_text',read)
    original_exists=Path.exists
    monkeypatch.setattr(Path,'exists',lambda p:True if str(p).startswith('/sys/fs/cgroup/memory.') else original_exists(p))
    monkeypatch.setattr(c.resource,'getrlimit',lambda n:(-1,-1))
    monkeypatch.setattr(c.shutil,'disk_usage',lambda p:SimpleNamespace(free=free*c.GIB))
    if allowed: assert c.capacity(tmp_path,2*c.GIB)['requested_address_space_bytes']==34359738368
    else:
        with pytest.raises(ValueError): c.capacity(tmp_path,2*c.GIB)


def test_orphan_worker_and_pilot_events(monkeypatch):
    monkeypatch.delenv('GRUDEVA007_LOCK_FD',raising=False)
    with pytest.raises(ValueError,match='controller'): c.worker(SimpleNamespace(action='007-pilot'),{})
    monkeypatch.setattr(t.report,'numeric_gates',lambda *a:{k:True for k in t.GATES})
    observed=dict(audits={'horizon':.4},events=[],arrival=None,records=[[.4,.08]],z=[0.,.1],activation=[0.,None],
        grain_history_z=[.025,.9],grain_history_activation=[.1,None])
    assert all(t.pilot_gates(observed,{ }).values())
    observed['activation'][1]=.5
    assert not t.pilot_gates(observed,{})['activation_support']


def test_worker_keeps_closed_prefix_failure():
    a=audit();a.update(starts={'007-pilot':{'kind':'short'}},short=1,unresolved_starts=['007-pilot'],
        reasons=['unresolved start; full allocation reserved; numerical work blocked','earlier allocation exceeded'],passed=False)
    p=c.closed_prefix(a,'007-pilot')
    assert not p['passed'] and p['reasons']==['earlier allocation exceeded']
    with pytest.raises(ValueError): c.allocations('007-pilot',p)


def test_diagnostic_failure_retains_completed_gates(tmp_path):
    t.write_new(tmp_path/'007-repeat_512.json',dict(task=t.TASK,gates={'conservation':True},
        observation_binding={'file':'already-saved'},passed=True))
    c.retain_failure(tmp_path,'007-repeat_512','plan',ValueError('dense replay failed'))
    r=t.obs.read_json(tmp_path/'007-repeat_512.json')
    assert r['gates']=={'conservation':True} and r['observation_binding']['file']=='already-saved'
    assert not r['passed'] and r['failure']['reason']=='dense replay failed'


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


def test_first_full_requires_bound_admission(tmp_path,monkeypatch):
    # Fake only artifact reading; exercise actual admission link checks.
    monkeypatch.setattr(c,'artifact',lambda *a,**k:{'passed':True})
    monkeypatch.setattr(t.obs,'sha',lambda p:'hash')
    a=audit();a.update(starts={n:{} for n in t.ATTEMPTS[:2]},
        ends={n:dict(artifact_sha256='a',seconds=1.) for n in t.ATTEMPTS[:2]})
    receipt=dict(task=t.TASK,plan_sha256='hash',passed=True,full_allocations=c.FULL_ALLOCATIONS,
        final_reduction_reserve=240.,prerequisites={n:'a' for n in t.ATTEMPTS[:2]},estimates={'x':1},
        consumed_seconds=2.,reserved_total_seconds=4240.,aggregate_with_reservations=4242.,ledger_prefix_sha256='wrong')
    t.write_new(tmp_path/'ADMISSION.json',receipt)
    (tmp_path/'invocations.jsonl').write_text('{"event":"end"}\n')
    with pytest.raises(ValueError,match='prefix'): c.prerequisites(tmp_path,'007-control_512',{'full_panel_estimates':{'x':1}},a)
    receipt['estimates']={'x':2};t.checkpoint(tmp_path/'ADMISSION.json',receipt)
    with pytest.raises(ValueError,match='basis'): c.prerequisites(tmp_path,'007-control_512',{'full_panel_estimates':{'x':1}},a)


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

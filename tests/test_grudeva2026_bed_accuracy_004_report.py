"""Failure-first saved-result validation using analytical synthetic artifacts."""
from copy import deepcopy
import json
from pathlib import Path
import numpy as np
import pytest
from puckworks.analysis import grudeva2026_bed_accuracy_004 as core
from puckworks.analysis import grudeva2026_bed_accuracy_004_report as report
from puckworks.analysis import grudeva2026_conservative_003 as old


def synthetic_limit():
    controls=report.controls('limit');bed=controls['bed']
    requested,z=old.observation_support(8.)
    arrival=5.4416
    crossings=np.arange(1,bed+1)/bed*arrival
    times=sorted(set(requested)|set(crossings))
    rows=[];obs=[];accepted=[]
    for t in times:
        s=min(t/arrival,1.)
        f=np.r_[np.arange(0,s,1/bed),s] if s else np.array([0.,0.])
        c=np.zeros(len(f)-1);b=1.388*np.diff(f)
        cup=min(max(t-1,0.),arrival-1)
        phases=old.phase_integrals(t,s,f,c,b)
        outlet=float(1<=t<arrival)
        rows.append([t,s,outlet,cup,*phases,0.])
        cp=np.where((z>s)&(z<=min(t,1)),1.,0.)
        event='exit' if t==arrival else ('cell_crossing' if t in crossings else ('initial' if t==0 else None))
        obs.append(dict(t=t,event=event,faces=f.tolist(),liquid_cells=c.tolist(),grain_integrals=b.tolist(),liquid_profile=cp.tolist(),grain_profile=[1.388]*len(z),grain_history=[1.388]*7))
        if t: accepted.append([t,s,cup,*phases,0.,0.,0.,0.,11.104,0.])
    sources=report.scientific_sources()
    return dict(controls=controls,configuration_sha256=report.digest(controls),status='EXECUTED_UNQUALIFIED',reason=None,
                source_sha256=sources['puckworks/analysis/grudeva2026_bed_accuracy_004.py'],
                inherited_source_sha256=sources['puckworks/analysis/grudeva2026_conservative_003.py'],
                radial_source_sha256=sources['puckworks/analysis/grudeva2026_reference_002.py'],
                records=rows,observations=obs,accepted=accepted,arrival=arrival,z=z.tolist(),grain_history_z=report.HISTORY_Z,
                activation=(z*arrival).tolist(),grain_history_activation=(np.array(report.HISTORY_Z)*arrival).tolist(),
                events=[dict(t=1.,kind='first_drip',outlet_left=0.,outlet_right=1.),dict(t=arrival,kind='desaturation_exit',outlet_left=1.,outlet_right=0.)],
                aqueous_min=0.,aqueous_max=0.,grain_mean_min=1.388,independent_shell_integral_error=0.,seconds=0.)


@pytest.fixture(scope='module')
def artifact():
    return synthetic_limit()


def test_complete_analytical_artifact_passes_state_audit_only(artifact):
    audit=report.audit_run(artifact,report.controls('limit'))
    assert audit['passed']
    assert audit['support']['times']==395
    assert audit['support']['unavailable']==0
    assert audit['independent_split_cup_error']<1e-12


@pytest.mark.parametrize('defect', ['source','configuration','terminal','events','histories','empty','profile','crossing','activation'])
def test_missing_or_mismatched_artifacts_cannot_pass(artifact,defect):
    r=deepcopy(artifact)
    if defect=='source': r['source_sha256']='0'*64
    elif defect=='configuration': r['controls']['dt']=.002
    elif defect=='terminal': r['records']=r['records'][:-1]
    elif defect=='events': r['events']=r['events'][:1]
    elif defect=='histories': r['observations'][20].pop('grain_history')
    elif defect=='empty': r['records']=[]
    elif defect=='profile': r['observations'][20]['liquid_profile']=[]
    elif defect=='crossing':
        next(o for o in r['observations'] if o['event']=='cell_crossing')['event']=None
    elif defect=='activation': r['grain_history_activation'][0]=None
    with pytest.raises((ValueError,KeyError,IndexError)):
        report.audit_run(r,report.controls('limit'))


@pytest.mark.parametrize('value', ['NaN','Infinity','1e999'])
def test_nonfinite_json_cannot_pass(tmp_path,value):
    path=tmp_path/'bad.json';path.write_text('{"bad":'+value+'}')
    with pytest.raises(ValueError): report.read(path)


def test_failed_execution_and_continuous_phase_error_are_rejected(artifact):
    for defect in ('execution','phase','cup','bounds'):
        r=deepcopy(artifact)
        if defect=='execution':r['status']='RESOURCE_LIMIT'
        if defect=='phase':r['records'][200][4]+=.001
        if defect=='cup':r['accepted'][-1][2]+=.001
        if defect=='bounds':r['aqueous_min']=-.001
        assert not report.audit_run(r,report.controls('limit'))['passed']


@pytest.mark.parametrize('defect',['unresolved','seconds','full','memory'])
def test_resource_failures_cannot_pass(tmp_path,defect):
    count=25 if defect=='full' else 1
    rows=[]
    for i in range(count):
        rows.append(dict(name=str(i),event='start',kind='full',time_ceiling=900.,memory_bytes=1 if defect=='memory' else 2*1024**3))
        if defect!='unresolved':rows.append(dict(name=str(i),event='end',seconds=901. if defect=='seconds' else 1.))
    (tmp_path/'invocations.jsonl').write_text('\n'.join(json.dumps(r) for r in rows))
    with pytest.raises(ValueError):report.resource_audit(tmp_path)


@pytest.mark.parametrize('body',['{','{}','{"runs": {}}'])
def test_cli_malformed_missing_rows_never_returns_qualification_success(tmp_path,body):
    matrix=tmp_path/'matrix.json';matrix.write_text(body)
    output=tmp_path/'result.json'
    assert report.main(['--runs-directory',str(tmp_path),'--matrix',str(matrix),'--output',str(output)])==2
    result=json.loads(output.read_text())
    assert result['disposition']==report.INCOMPLETE and not result['qualified']


def test_reducer_does_not_import_or_call_execution_helpers():
    import ast
    tree=ast.parse(Path(report.__file__).read_text())
    calls=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert 'run' not in calls and 'step' not in calls and 'simulate' not in calls
    assert report.refinement is __import__('puckworks.analysis.grudeva2026_conservative_003_report',fromlist=['refinement']).refinement
    assert core.observation_support is old.observation_support

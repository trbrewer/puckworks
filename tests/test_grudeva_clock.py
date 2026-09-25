"""Synthetic-only tests: no upstream measurement payloads."""
from copy import deepcopy
import csv
import json

import numpy as np
import pytest

from puckworks.analysis import grudeva_clock as gc


def row(shot=1,vial=1,mass=2,b=0,t0=0,t1=2):
    return dict(shot=shot,vial=vial,mass_g=mass,b_start_g=b,t_start_s=t0,t_end_s=t1)


def fixture(path):
    with path.open('w') as f:
        writer=csv.writer(f)
        for j in range(14):
            writer.writerows([
                ['Vial No.']+list(range(1,19)),
                ['Vial Weight']+[10]*16+['',10],
                ['Vial+Coffee']+[10,11,12]+[13]*15,
                ['Weight']+[0,1,2]+[3]*15,
                ['TDS']+[0,0,'']+[12]*15])
    return path


def test_adapter_units_identity_and_missing(tmp_path):
    records=gc.parse_source(fixture(tmp_path/'synthetic.csv'))
    assert len(records)==252 and {r['shot'] for r in records}==set(range(1,15))
    assert records[0]['cohort']=='notebook13'
    assert records[-1]['cohort']=='extra_block_unqualified'
    assert records[16]['clock_authority']=='unqualified terminal clock'
    assert records[16]['tare_g'] is None
    obs=gc.observations(records)
    assert obs[0]['solute_g']==0 and not obs[0]['eligible']
    assert obs[1]['solute_g'] is None and obs[2]['solute_g'] is None
    assert obs[3]['vial']==4 and obs[3]['b_start_g']==3
    assert obs[3]['solute_g']==pytest.approx(.36)
    assert obs[3]['t_start_s']==6
    assert gc.observations(records,'literal')[1]['solute_g']==0
    assert records[1]['gross_minus_tare_g']==1
    records[1]['mass_g']=None
    with pytest.raises(ValueError,match='mass gap'):
        gc.observations(records)


def test_discrepancy(tmp_path):
    p=fixture(tmp_path/'synthetic.csv')
    p.write_text(p.read_text().replace('Weight,0,1,2','Weight,0,1.1,2',1))
    records=gc.parse_source(p)
    assert records[1]['net_discrepancy_g']==pytest.approx(.1)
    assert records[1]['discrepancy_at_source_precision']
    assert records[1]['recorded_net_g']==1.1


def test_constant_zero_and_analytic():
    rows=[row(),row(mass=0),row(b=2,t0=2,t1=4)]
    assert np.allclose(gc.deliver(rows,[.3,0,0,.25]),[.6,0,.6],atol=1e-13)
    theta=[.3,.1,.2,1]
    # Here b=t and m=duration=2; integrate exp(-.3 b).
    expected=.3/.3*(1-np.exp(-.6))
    assert gc.deliver(rows[:1],theta)[0]==pytest.approx(expected,abs=1e-12)
    assert np.array_equal(gc.deliver(rows,[0,0,0,4]),np.zeros(3))


@pytest.mark.parametrize('timing',['linear','u2','sqrt'])
def test_independent_bounds(timing):
    rows=[row(mass=5),row(b=5,t0=2,t1=4),row(mass=0)]
    for theta in ([1,10,10,.25],[1,10,10,4],[.5,0,0,.25],[.4,.03,.06,.8]):
        y=gc.deliver(rows,theta,timing)
        fine=gc.deliver(rows,theta,timing,order=256)
        check=np.array([gc.independent_delivery(r,theta,timing)[0] for r in rows])
        assert np.max(abs(y-check))<1e-6
        assert np.max(abs(y-fine))<1e-6
        assert np.all(y>=0) and np.all(y<=np.array([r['mass_g'] for r in rows])+1e-12)
        assert np.all(gc.deliver(rows,theta,timing,endpoint='end')<=y+1e-12)
        assert np.all(y<=gc.deliver(rows,theta,timing,endpoint='start')+1e-12)


def test_additivity_mass_timing_and_units():
    full=[row(mass=4,t1=4)]
    parts=[row(mass=1,t1=1),row(vial=2,mass=3,b=1,t0=1,t1=4)]
    theta=[.3,.05,.08,1.3]
    assert gc.deliver(full,theta)[0]==pytest.approx(gc.deliver(parts,theta).sum(),abs=1e-9)
    theta=[.3,0,.001,.8]
    for timing in ('linear','u2','sqrt'):
        assert gc.deliver(full,theta,timing)[0]==pytest.approx(gc.deliver(parts,theta,timing).sum(),abs=1e-9)
    kg=[dict(r,mass_g=r['mass_g']/1000,b_start_g=r['b_start_g']/1000) for r in full]
    # Reversible unit transform: am/kg=1000*am/g, output kg*1000=g.
    assert gc.deliver(full,theta)[0]==pytest.approx(1000*gc.deliver(kg,[.3,0,1,.8])[0],abs=1e-12)


def synthetic(candidate='TIME'):
    rows=[]
    for shot in (1,2,3):
        b=0.
        for vial in range(1,17):
            m=.5+.07*vial+.15*shot
            r=row(shot,vial,m,b,2*(vial-1),2*vial)
            theta=[.23,.065,0,1.2] if candidate=='TIME' else [.23,0,.09,1.2]
            y=float(gc.deliver([r],theta)[0])
            r.update(solute_g=y,tds_pct=100*y/m,eligible=True)
            rows.append(r);b+=m
    return rows


@pytest.mark.slow
@pytest.mark.parametrize('candidate',['TIME','MASS'])
def test_synthetic_recovery(candidate):
    rows=synthetic(candidate)
    fit=gc.fit(rows,candidate)
    assert fit['status']=='CONVERGED'
    expected=[.23,.065,0,1.2] if candidate=='TIME' else [.23,0,.09,1.2]
    assert np.allclose(fit['theta'],expected,atol=2e-5)
    assert len(fit['attempts'])==8 and all(r['calls']<=2000 for r in fit['attempts'])
    assert 'boundary_hits' in fit


def test_template_training_only_and_fallback():
    train=[dict(row(vial=v),eligible=True,tds_pct=c) for v,c in [(2,10),(2,20),(4,30)]]
    train.append(dict(row(vial=1,mass=0),eligible=False,tds_pct=100))
    y,record=gc.template(train,[row(vial=1,mass=0),row(vial=3)])
    assert np.allclose(y,[0,.3],atol=1e-14)  # tie goes to lower position 2
    assert record['effective_positions']==2 and record['support_counts'][2]==2
    assert record['fallbacks'][1]['used']==2


@pytest.mark.slow
def test_leakage_and_determinism():
    rows=synthetic();other=deepcopy(rows)
    for r in other:
        if r['shot']==3:
            r.update(tds_pct=999,solute_g=999,eligible=False)
    a=gc.fold_predict(rows,3);b=gc.fold_predict(other,3)
    assert json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)
    assert a['training_shots']==[1,2]
    assert a['fits']['MIXED']['attempts'][6]['start'][2]==0
    assert a['fits']['MIXED']['attempts'][7]['start'][1]==0


def test_constant_flow_nonidentifiability():
    rows=[row(vial=i+1,mass=4,b=4*i,t0=2*i,t1=2*i+2) for i in range(10)]
    # b=2t: only at+2am is identified, not its two components.
    a=gc.deliver(rows,[.2,.1,.2,1.3]);b=gc.deliver(rows,[.2,.3,.1,1.3])
    assert np.allclose(a,b,atol=1e-13)
    assert np.linalg.matrix_rank(np.array([[r['t_start_s'],r['b_start_g']] for r in rows]))==1


def test_metrics_support_and_rules():
    obs=synthetic()[:16]
    obs[1].update(eligible=False,solute_g=None)
    pred=[dict(**{k:r[k] for k in gc.COORDS},yhat_g=(r['solute_g'] or 0)+.01,numerical_allowance_g=1e-9) for r in obs]
    metrics=gc.metrics(obs,pred)
    assert metrics['n_positive']==15 and metrics['support']=='observed_support'
    assert metrics['signed_support_total_error_g']==pytest.approx(.15)
    assert metrics['vial_rmse_g']==pytest.approx(.01)
    assert gc.metrics(obs,pred)==metrics
    a=[dict(vial_rmse_g=.04,absolute_support_total_error_g=.1)]*13
    b=[dict(vial_rmse_g=.05,absolute_support_total_error_g=.1)]*13
    result=gc.comparison(a,b)
    assert result['material'] and result['shots_improved']==13
    assert result['required_shots']==10
    a=[dict(vial_rmse_g=.049,absolute_support_total_error_g=.1)]*13
    assert not gc.comparison(a,b)['material']


def test_freeze_requires_independent_approval(tmp_path):
    freeze=tmp_path/'freeze.json';review=tmp_path/'review.json'
    gc.write_json(freeze,{})
    gc.write_json(review,{'decision':'PENDING'})
    with pytest.raises(RuntimeError,match='approval'):
        gc.verify_freeze(freeze,review,tmp_path/'absent.csv')
    with pytest.raises(FileExistsError):
        gc.write_json(freeze,{})


@pytest.mark.slow
def test_failure_records_and_hard_budget(monkeypatch):
    def exhaust(fun,x0,**kwargs):
        for _ in range(2001):
            fun(x0)
    monkeypatch.setattr(gc,'least_squares',exhaust)
    failed=gc.fit(synthetic(),'TIME')
    assert failed['status']=='ALL_STARTS_FAILED' and failed['theta'] is None
    assert len(failed['attempts'])==8
    assert all(r['calls']==2000 and not r['success'] for r in failed['attempts'])
    mixed=gc.fit(synthetic(),'MIXED',nested={'TIME':failed,'MASS':failed})
    assert mixed['status']=='NESTED_SOLUTION_UNAVAILABLE'


def test_boundary_reporting():
    rows=synthetic()
    for r in rows:
        r.update(solute_g=0.,tds_pct=0.)
    result=gc.fit(rows,'MASS')
    assert result['status']=='CONVERGED'
    assert result['loss']<1e-10
    assert 'boundary_hits' in result


def synthetic_bundle(tmp_path,failed=False,allowance=0.):
    source=fixture(tmp_path/'source.csv')
    bundle=tmp_path/'predictions';bundle.mkdir()
    files={}
    for treatment,(zero,timing) in gc.TREATMENTS.items():
        obs=gc.observations(gc.parse_source(source),zero)
        for held in range(1,14):
            preds=[dict(**{k:r[k] for k in gc.COORDS},
                        yhat_g=(r['solute_g'] or 0),numerical_allowance_g=allowance)
                   for r in obs if r['shot']==held]
            record=dict(predictions={m:preds for m in ('TIME','MASS','MIXED','TEMPLATE')})
            if failed and held==1:
                record['predictions']['MASS']=None
            name=f'{treatment}-{held:02}.json';gc.write_json(bundle/name,record)
            files[name]=gc.digest(bundle/name)
    gc.write_json(bundle/'manifest.json',dict(files=files,source_sha256=gc.digest(source)))
    return source,bundle


def test_score_reproduction_and_once_only(tmp_path):
    source,bundle=synthetic_bundle(tmp_path)
    a=gc.score(source,bundle,tmp_path/'score-a');b=gc.score(source,bundle,tmp_path/'score-b')
    assert a==b
    assert a['primary']['disposition']=='NUMERICALLY_QUALIFIED'
    with pytest.raises(FileExistsError):
        gc.score(source,bundle,tmp_path/'score-a')


@pytest.mark.parametrize('failed,allowance',[(True,0.),(False,1e-3)])
def test_unresolved_reporting(tmp_path,failed,allowance):
    source,bundle=synthetic_bundle(tmp_path,failed,allowance)
    result=gc.score(source,bundle,tmp_path/'scores')
    assert result['primary']['disposition']=='NUMERICALLY_UNRESOLVED'
    assert result['primary']['scientific_dispositions']['mass_increment']=='NUMERICALLY_UNRESOLVED'
    if failed:
        assert 'aggregate' not in result['primary']
        assert result['primary']['expected_shots']==13
    pytest.importorskip('matplotlib')
    gc.report(bundle,tmp_path/'scores',tmp_path/'report',source)
    assert (tmp_path/'report/aggregate.json').is_file()


def test_numerical_gate_includes_chemistry_missing_predictions(tmp_path):
    source,bundle=synthetic_bundle(tmp_path)
    path=bundle/'primary-01.json';fold=gc.read_json(path)
    # Synthetic vial 2 has positive mass/ambiguous zero TDS: unavailable primary.
    fold['predictions']['TIME'][1]['numerical_allowance_g']=1e-3
    path.write_text(json.dumps(fold))
    manifest_path=bundle/'manifest.json';manifest=gc.read_json(manifest_path)
    manifest['files'][path.name]=gc.digest(path)
    manifest_path.write_text(json.dumps(manifest))
    result=gc.score(source,bundle,tmp_path/'scores')
    assert result['primary']['per_shot']['TIME'][0]['numerical_max_g']==0
    assert not result['primary']['numerically_qualified']
    assert result['primary']['disposition']=='NUMERICALLY_UNRESOLVED'

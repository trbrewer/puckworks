"""Synthetic verification, source identity QA, and information-flow contracts."""
from dataclasses import replace
import inspect
import json
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import smrke2024_transfer as s


def synthetic(beta=0.):
    return [s.Observation(s.Covariate(f'{g}:{i}', float(t), g),
            float(22-8*np.exp(-t/20)+beta*s.LEVELS[g]/20))
            for g in s.LEVELS for i,t in enumerate(np.linspace(10, 70, 9))]


@pytest.mark.parametrize('change', [dict(time_s=0), dict(time_s=-1), dict(time_s=np.nan),
    dict(time_s=np.inf), dict(level='0g'), dict(level='1g_fines '), dict(source='other'),
    dict(row_id=''), dict(units=('ms','source_yield_pp','g')),
    dict(units=('s','dry_coffee_yield_pp','g')), dict(units=('s','source_yield_pp','kg'))])
def test_invalid_covariate(change):
    with pytest.raises(ValueError):
        s.Covariate(**(dict(row_id='x',time_s=20,level='no_added_fines') | change))


@pytest.mark.parametrize('yield_pp', [np.nan,np.inf,-1,101])
def test_invalid_yield(yield_pp):
    with pytest.raises(ValueError):
        s.Observation(s.Covariate('x',20,'no_added_fines'),yield_pp)


def test_units_features_and_rows():
    rows=s.source_rows()
    assert [sum(r.covariate.level==l for r in rows) for l in s.LEVELS]==[20,10,9,7]
    assert [sum(r.covariate.level==l and r.primary for r in rows) for l in s.LEVELS]==[12,7,7,7]
    assert rows[0].covariate.row_id=='Fig3:L2'
    assert rows[0].covariate.f==.05
    assert rows[30].note=='partially occluded' and not rows[30].primary
    assert rows[10].blob==rows[11].blob==rows[30].blob=='mixed17'
    assert len({r.covariate.row_id for r in rows})==46


def test_fold_and_support_masks():
    rows=[r for r in s.source_rows() if r.primary]
    support=s.eligible_support(rows)
    assert support['sufficient']
    assert support['A']['4g_fines']['excluded']==['Fig3:L27']
    assert support['A']['1g_fines']['training_time_range']==[9.18,68.07]
    for p in ('A','B'):
        for level,train,test in s.folds(rows,p):
            assert not {r.covariate.row_id for r in train}&{r.covariate.row_id for r in test}
            assert all(r.covariate.level==level for r in test)
            assert not any(r.covariate.level==level for r in train)
    assert not s.eligible_support(rows[:2])['sufficient']


def test_equal_weights():
    rows=synthetic()[:20]
    w=s.weights(rows)
    for g in set(r.covariate.level for r in rows):
        assert sum(v for r,v in zip(rows,w) if r.covariate.level==g)==pytest.approx(1/3)
    assert sum(w)==pytest.approx(1.)


@pytest.mark.parametrize('model', s.MODELS)
def test_synthetic_bounds_determinism_and_prediction_interface(model):
    rows=synthetic()
    fit=s.fit(model,rows)
    assert fit==s.fit(model,rows)
    predictions=fit.predict([r.covariate for r in rows])
    assert all(p['time_supported'] and p['fitted_source']==s.SOURCE for p in predictions)
    assert fit.diagnostics['converged']
    points=[s.Covariate(str(i),float(t),g) for g in s.LEVELS for i,t in enumerate(np.linspace(*s.DOMAIN,200))]
    pred=fit.predict(points)
    assert min(p['prediction_pp'] for p in pred)>=-1e-7
    assert max(p['prediction_pp'] for p in pred)<=100+1e-7
    assert all(np.diff([p['prediction_pp'] for p in pred if p['level']==g]).min()>=-1e-7 for g in s.LEVELS)
    with pytest.raises(ValueError):
        fit.predict(rows)
    with pytest.raises(ValueError):
        fit.predict([s.Covariate('bad',81,'1g_fines')])
    assert 'yield_pp' not in s.Covariate.__dataclass_fields__
    assert 'yield_pp' not in inspect.getsource(s.Fitted.predict)
    # Changing the withheld target cannot change fitted or predicted objects.
    _,train,test=next(s.folds(rows,'B'))
    changed=[replace(r,yield_pp=90.) for r in test]
    fitted=s.fit(model,train)
    assert fitted.predict([r.covariate for r in test])==fitted.predict([r.covariate for r in changed])


def test_common_recovery_and_precision():
    rows=[r for r in synthetic() if r.covariate.level=='no_added_fines']
    fitted=s.fit('M0',rows)
    assert fitted.parameters==pytest.approx((22,8,20),abs=1e-4)
    tight=s.fit('M0',rows,tight=True)
    assert fitted.parameters==pytest.approx(tight.parameters,abs=1e-4)
    for m in ('M1','B1'):
        with pytest.raises(ValueError):
            s.fit(m,rows)


def test_synthetic_gain_and_zero_gain():
    for beta, expected in [(6.,True),(0.,False)]:
        parents=[]; corrections=[]
        for _,train,test in s.folds(synthetic(beta),'B'):
            for model,target in [('M0',parents),('M1',corrections)]:
                fitted=s.fit(model,train)
                pred=fitted.predict([r.covariate for r in test])
                target.append(s.metrics([p['prediction_pp']-r.yield_pp for p,r in zip(pred,test)]))
        assert s.gain(parents,corrections)['material'] is expected
    assert s.gain([],[])['material'] is None
    assert s.gain([s.metrics([])]*4,[s.metrics([])]*4)['material'] is None


def test_synthetic_empirical_gain():
    rows=[replace(r,yield_pp=10+2*np.log(r.covariate.time_s)+6*r.covariate.f) for r in synthetic()]
    parents=[]; corrections=[]
    for _,train,test in s.folds(rows,'B'):
        for model,target in [('B0',parents),('B1',corrections)]:
            pred=s.fit(model,train).predict([r.covariate for r in test])
            target.append(s.metrics([p['prediction_pp']-r.yield_pp for p,r in zip(pred,test)]))
    assert s.gain(parents,corrections)['material']


def test_endpoint_covariate_extrapolation():
    for level,train,test in s.folds(synthetic(2),'B'):
        preds=s.fit('B1',train).predict([r.covariate for r in test])
        assert all(p['intervention_supported']==(level in ('1g_fines','2g_fines')) for p in preds)


def test_sensitivity_dependence_and_no_hidden_rows():
    treatments=dict(s.treatments(s.source_rows()))
    assert len(treatments)==18
    for name,rows in treatments.items():
        central=treatments[name.split(':')[0]+':central']
        assert [r.covariate.row_id for r in rows]==[r.covariate.row_id for r in central]
        offsets={r.covariate.row_id:(r.covariate.time_s-o.covariate.time_s,r.yield_pp-o.yield_pp)
                 for r,o in zip(rows,central)}
        for blob in set(r.blob for r in rows)-{None}:
            shift=[offsets[r.covariate.row_id] for r in rows if r.blob==blob]
            assert np.ptp(shift,axis=0).max()<1e-12


def test_constraints_not_clipping():
    rows=synthetic()
    descending=[replace(r,yield_pp=99-r.covariate.time_s) for r in rows]
    for model in s.MODELS:
        fit=s.fit(model,descending)
        assert fit.diagnostics['active_constraints'] or fit.diagnostics['tau_bound_hit']
    assert 'clip(' not in inspect.getsource(s.Fitted.predict)


def test_convergence_failure_is_explicit(monkeypatch):
    from types import SimpleNamespace
    monkeypatch.setattr(s,'minimize',lambda *a,**k: SimpleNamespace(success=False,x=np.zeros(3),message='synthetic failure',nit=0))
    with pytest.raises(RuntimeError,match='Constrained fit failed'):
        s.fit('B0',synthetic())


def test_exclusive_output_and_existing_source_unchanged(tmp_path):
    path=tmp_path/'test.json'; s.write_json(path,{'a':1})
    with pytest.raises(FileExistsError):
        s.write_json(path,{'a':2})
    root=Path(s.__file__).resolve().parents[2]
    source=json.loads((s.DOC/'SOURCE.json').read_text())
    assert all(s.digest(root/name)==value for name,value in source['source_files'].items())


def test_gain_cannot_be_earned_by_endpoint_only_or_bad_arm():
    parent=[s.metrics([1.]*4)]*4
    def errors(values):
        return [s.metrics([v]*4) for v in values]
    assert not s.gain(parent,errors([0.,1.01,1.,0.]))['material']
    assert not s.gain(parent,errors([1.11,.1,.1,.1]))['material']
    assert not s.gain(parent,errors([.85]*4))['material']
    assert s.gain(parent,errors([.7]*4))['material']


def test_verdict_sensitivity_is_not_silently_selected():
    def report(a, gain):
        m=s.metrics([a]*4)
        return {'A':{l:{x:{'supported':m} for x in ('M0','B0')} for l in list(s.LEVELS)[1:]},
                'gain':{x:{'material':gain} for x in ('M1','B1')}}
    passing=report(.1,False); failing=report(1.,False)
    assert s.adjudicate({'a':passing},True)['COMMON_TIME_RESPONSE']=='ADEQUATE_FOR_TESTED_SOURCE_SUPPORT'
    assert s.adjudicate({'a':failing},True)['COMMON_TIME_RESPONSE']=='TESTED_COMMON_MODELS_INADEQUATE'
    assert s.adjudicate({'a':passing,'b':failing},True)['COMMON_TIME_RESPONSE']=='UNRESOLVED'
    assert s.adjudicate({'a':passing},False)['FINES_COVARIATE_INCREMENT']=='UNRESOLVED'
    assert s.adjudicate({'a':passing,'b':report(.1,True)},True)['FINES_COVARIATE_INCREMENT']=='UNRESOLVED'


@pytest.mark.parametrize('model', s.MODELS)
def test_noisy_synthetic_precision(model):
    rows=[replace(r,yield_pp=r.yield_pp+.35*np.sin(i*1.79)) for i,r in enumerate(synthetic(3.))]
    a=s.fit(model,rows); b=s.fit(model,rows,tight=True)
    aa=a.predict([r.covariate for r in rows]); bb=b.predict([r.covariate for r in rows])
    assert max(abs(x['prediction_pp']-y['prediction_pp']) for x,y in zip(aa,bb))<=.01

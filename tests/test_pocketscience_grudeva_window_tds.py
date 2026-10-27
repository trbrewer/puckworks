"""Synthetic-only transfer checks; no original measurements or private locators."""
from copy import deepcopy
import csv
from dataclasses import replace

import numpy as np
import pytest
from scipy.optimize import lsq_linear

from puckworks.analysis import grudeva_clock as clock
from puckworks.analysis import pocketscience_cup_tds as source
from puckworks.analysis import pocketscience_cross_style_tds as pn
from puckworks.analysis import pocketscience_grudeva_window_tds as model
from tools import pocketscience_grudeva_window_tds as runner


def source_fixture():
    shots=[]
    for sheet in ('Sworks High Flow','VST18'):
        for grinder,style in source.STYLE_MAP.items():
            for prep in ('N','Y'):
                for dispersion in (('Brass','Teflon') if sheet=='Sworks High Flow' else ('Teflon',)):
                    for i in range(5):
                        index=sum(s.sheet==sheet for s in shots)+1
                        row={9:25,25:9}.get(index,index) if sheet=='Sworks High Flow' else index
                        shots.append(source.Shot(sheet,row,(sheet,grinder,prep,dispersion),style,
                            .02,.034+.0005*index,6+.05*index,6.5+.06*index,
                            sheet=='Sworks High Flow' and row in (7,9,23)))
    return shots


def authority():
    return dict(status='QUALIFIED',pdf_sha256=model.THESIS_SHA,nominal_dose_kg=.0185,
                individual_doses_measured=False,authority='synthetic authority fixture',
                dose_passage='synthetic passage',scope_passage='synthetic scope')


def target_fixture(tmp_path):
    path=tmp_path/'synthetic.csv'
    with path.open('w',newline='') as f:
        writer=csv.writer(f)
        for shot in range(1,15):
            mass=[0 if v in ((1,4) if shot==13 else (1,2)) else 1+.02*shot+.01*v for v in range(1,19)]
            tds=[float('nan') if m==0 else 12-.3*v for v,m in enumerate(mass,1)]
            if shot==6:tds[2]=0
            if shot==13:tds[1]=0
            writer.writerows([['Vial No.']+list(range(1,19)),['Vial Weight']+[10]*18,
                              ['Vial+Coffee']+[m+10 for m in mass],['Weight']+mass,['TDS']+tds])
    return clock.parse_source(path)


def retained():
    return [s for s in source_fixture() if not s.source_excluded]


def test_exact_source_membership_and_order():
    all60=source_fixture();expected=source.membership_hash(retained())
    rows=model.source_cohort(all60,all60,expected)
    assert rows==retained() and len(rows)==57 and len({s.condition for s in rows})==12
    assert [sum(s.sheet==b for s in rows) for b in ('Sworks High Flow','VST18')]==[37,20]
    assert [sum(s.style==s0 for s in rows) for s0 in source.STYLES]==[29,28]
    with pytest.raises(ValueError,match='drift'):model.source_cohort(all60[::-1],all60,expected)
    with pytest.raises(ValueError,match='drift'):model.source_cohort(all60[:40],all60,expected)
    changed=list(all60);changed[0]=replace(changed[0],filtered_tds_pp=99)
    with pytest.raises(ValueError,match='drift'):model.source_cohort(changed,all60,expected)


def test_complete16_units_structural_zeros_and_whole_shot_exclusions(tmp_path):
    records=target_fixture(tmp_path)
    primary=model.aggregate(records,authority());literal=model.aggregate(records,authority(),True)
    assert primary['physical_n']==11 and literal['physical_n']==13
    assert [e['shot'] for e in primary['endpoints']]==[j for j in range(1,14) if j not in (6,13)]
    assert [e['shot'] for e in primary['excluded']]==[6,13]
    for e in literal['endpoints']:
        rows=[r for r in records if r['shot']==e['shot'] and r['vial']<=16]
        mass=sum(r['mass_g'] for r in rows)
        expected=sum(r['mass_g']*r['tds_pct'] for r in rows if r['mass_g']>0)/mass
        assert e['beverage_kg']==pytest.approx(mass/1000)
        assert e['target_pp']==pytest.approx(expected,abs=1e-10)
        assert e['x']==pytest.approx(.0185/(mass/1000))
        assert e['vials']==list(range(1,17)) and e['aggregation_check_pp']<=1e-10
    # Terminal and unqualified extra-block values cannot change either endpoint.
    other=deepcopy(records)
    for r in other:
        if r['shot']==14 or r['vial']>16:r.update(mass_g=999,tds_pct=99)
    assert model.aggregate(other,authority())==primary
    assert model.aggregate(other,authority(),True)==literal


@pytest.mark.parametrize('change',[{'status':'NOT_QUALIFIED'},{'nominal_dose_kg':.019},
                                  {'individual_doses_measured':True},{'pdf_sha256':'wrong'},
                                  {'scope_passage':''}])
def test_nominal_authority_required(tmp_path,change):
    with pytest.raises(ValueError,match='nominal dose'):
        model.aggregate(target_fixture(tmp_path),dict(authority(),**change))


def test_gaps_bad_mass_and_rectangular_order_stop(tmp_path):
    records=target_fixture(tmp_path)
    for field,value in [('mass_g',None),('mass_g',-1),('tds_pct',None)]:
        changed=deepcopy(records);changed[3][field]=value
        with pytest.raises(ValueError):model.aggregate(changed,authority())
    with pytest.raises(ValueError,match='identity/order'):model.aggregate(records[::-1],authority())
    with pytest.raises(ValueError,match='identity/order'):model.aggregate(records+[records[0]],authority())
    with pytest.raises(ValueError,match='incomplete regular'):model.aggregate(records[1:],authority())


def test_target_y_cannot_change_source_fits_predictions_or_resampling(tmp_path):
    target=model.aggregate(target_fixture(tmp_path),authority())['endpoints']
    changed=[dict(t,target_pp=t['target_pp']+25) for t in target]
    a,b=[model.evaluate(retained(),t,draws=6) for t in (target,changed)]
    assert a['source_fit']==b['source_fit']
    assert [p['predictions'] for p in a['predictions']]==[p['predictions'] for p in b['predictions']]
    for u,v in zip(a['bootstrap_samples'],b['bootstrap_samples'],strict=True):
        assert u['fit']==v['fit']
        assert u['source_multiplicities']==v['source_multiplicities']
        assert u['target_multiplicities']==v['target_multiplicities']
    assert a['scores']!=b['scores'] and a['coverage_per_arm']==11


def test_weighted_replication_independent_bvls_and_spawned_streams(tmp_path):
    shots=retained();targets=model.aggregate(target_fixture(tmp_path),authority())['endpoints']
    x,y,_,group=source.arrays(shots);tx=np.array([t['x'] for t in targets]);ty=np.array([t['target_pp'] for t in targets])
    result=model.evaluate(shots,targets,draws=5)
    srng,trng=[np.random.default_rng(s) for s in np.random.SeedSequence(model.SEED).spawn(2)]
    for draw in result['bootstrap_samples']:
        sw=np.array(draw['source_multiplicities']);tw=np.array(draw['target_multiplicities'])
        np.testing.assert_array_equal(sw,source.bootstrap_weights(group,srng))
        np.testing.assert_array_equal(tw,np.bincount(trng.choice(11,11,replace=True),minlength=11))
        assert all(sw[group==g].sum()==sum(group==g) for g in np.unique(group)) and tw.sum()==11
        copies=np.repeat(np.arange(len(x)),sw);held=np.repeat(np.arange(len(tx)),tw)
        fit,pred,_=model.source_fit_predict(x[copies],y[copies],tx)
        assert fit['coefficients']==pytest.approx(draw['fit']['coefficients'])
        weighted=model.scores(ty,pred,tw);literal=model.scores(ty[held],pred[held])
        for j,a in enumerate(model.ARMS):
            assert weighted[a]==pytest.approx(literal[a])
            z=x if a=='P' else np.ones(len(x))
            oracle=lsq_linear((z*np.sqrt(sw))[:,None],y*np.sqrt(sw),bounds=(0,100),method='bvls',tol=1e-14)
            np.testing.assert_allclose(pred[:,j],oracle.x[0]*(tx if a=='P' else np.ones(len(tx))),atol=1e-10,rtol=0)


def test_zero_individual_target_weights_and_raw_domain_predictions():
    pred=np.array([[200.,3.],[8.,4.]]);y=np.array([10.,5.])
    assert model.scores(y,pred,[0,2])==model.scores(y[1:],pred[1:])
    assert model.scores(y,pred)['P']['rmse']>100
    with pytest.raises(ValueError):model.scores(y,pred,[0,0])
    for bad in ([1,-1],[1,np.nan]):
        with pytest.raises(ValueError):model.scores(y,pred,bad)
    f,p,_=model.source_fit_predict(np.array([.3,.4]),np.array([30.,40.]),np.array([2.]))
    assert f['active_bounds']['P'] and p[0,0]==200


def test_zero_reference_failure_accounting_and_retained_extrapolations(monkeypatch):
    shots=[replace(s,filtered_tds_pp=0) for s in retained()]
    target=[dict(shot=j,x=2.+j,target_pp=0) for j in range(3)]
    zero=model.evaluate(shots,target,draws=3)
    c=zero['contrasts']['P/N']
    assert c['gain'] is None and c['gain_ci95'] is None and c['gain_undefined_draws']==3
    assert c['difference_ci95']==[0.,0.] and zero['decision']=='WINDOW_TRANSFER_COMPARISON_UNRESOLVED'
    assert zero['support']['extrapolation_count']==3 and zero['coverage_per_arm']==3
    original=model.source_fit_predict;calls=0
    def fail(*args,**kwargs):
        nonlocal calls
        calls+=1
        if calls==3:raise ValueError('synthetic draw failure')
        return original(*args,**kwargs)
    monkeypatch.setattr(model,'source_fit_predict',fail)
    failed=model.evaluate(shots,target,draws=5)
    b=failed['bootstrap'];assert (b['completed'],b['failed'],b['unattempted'])==(1,1,3)
    assert len(b['failures'][0]['source_multiplicities'])==57 and len(b['failures'][0]['target_multiplicities'])==3
    assert failed['scores']['P']['rmse_ci95'] is None and failed['contrasts']['P/N']['difference_ci95'] is None
    assert failed['decision']=='INCOMPLETE_BOOTSTRAP'


def test_source_deletions_refit_target_deletions_preserve_fit_and_report(tmp_path):
    shots=retained();target=model.aggregate(target_fixture(tmp_path),authority())['endpoints']
    point=model.evaluate(shots,target,draws=4);influence=model.influence(shots,target,point)
    assert len(influence['deletions'])==23
    for d in influence['deletions']:
        if d['side']=='target':assert d['source_fit']==point['source_fit'] and d['target_n']==10
        else:
            x,y,_,_=source.arrays([s for s in shots if s.condition!=d['deleted']])
            assert d['source_fit']==pn.fit_source(x,y,oracle=True) and d['target_n']==11
    result={name:deepcopy(point) for name in runner.ANALYSES}
    result.update(influence=influence,sensitivity_summary='Synthetic report; no original data.')
    assert len(runner.report(result).split())<=750
    assert pn.ARMS==('P','N') and source.ARMS==('M','C','N')


@pytest.mark.parametrize('ci,expected',[([-1,0],'WINDOW_TRANSFER_COMPARISON_UNRESOLVED'),
    ([0,1],'WINDOW_TRANSFER_COMPARISON_UNRESOLVED'),([-2,-1],'P_WINDOW_TRANSFER_ADDED_VALUE_OVER_N'),
    ([1,2],'N_LOWER_WINDOW_TRANSFER_LOSS')])
def test_zero_endpoint_decisions(ci,expected):
    assert model.decision({'P/N':{'difference_ci95':ci}})==expected

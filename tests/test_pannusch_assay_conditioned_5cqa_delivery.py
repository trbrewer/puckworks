"""In-memory source firewall and synthetic decision checks; no real scoring."""
import copy
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import pannusch_assay_conditioned_5cqa_delivery as p
from puckworks.analysis import assay_conditioned_5cqa_training as train
from test_assay_conditioned_5cqa_delivery import synthetic_model


def fixture():
    coords,rows,groups=[],[],{}
    for label,count,campaign in [('FIT',15,'FIT_2021_12'),('PRED',8,'PREDICTION_2022_03')]:
        for e in range(1,count+1):
            condition=f'{label}-C{e:02d}'
            if label=='FIT': groups[condition]=condition
            for rep in (1,2,3):
                shot=f'{label}-E{e:02d}-R{rep}'
                for fraction,a,b,mass in [(1,0.,.004,.004),(2,.004,.01,.006),
                    (3,.01,.015,.005),(5,.02,.025,.005),(7,.03,.035,.005),(10,.045,.05,.005)]:
                    coords.append(dict(campaign=campaign,condition=condition,shot=shot,fraction=fraction,
                        b0=a,b1=b,mass_kg=mass,coordinate_status='QUALIFIED'))
                    for species in ('5CQA','TDS','CQA_sum','caffeine'):
                        rows.append(dict(campaign_id=campaign,condition_id=condition,shot_id=shot,
                            physical_replicate_id=str(rep),fraction_id=str(fraction),analyte=species,
                            concentration_unit='mg/g' if species!='TDS' else 'percent',validity='VALID',
                            exclusion_reason='',source_id='P24-MAT-'+label,fraction_liquid_g_or_ml=str(mass*1000),
                            fraction_basis='MEASURED_MASS_G',source_object_or_cell=f'ExperimentalData({e}).run({rep}) fraction {fraction}',
                            concentration_value='1.0',measured_concentration='1.0'))
    return coords,rows,groups


def test_first_projection_exact_identity_units_zero_and_spills():
    coords,rows,_=fixture()
    for row in rows:
        if row['shot_id'] in ('FIT-E03-R1','FIT-E11-R3','FIT-E14-R3') and row['fraction_id']=='2' and row['analyte']=='5CQA':
            row.update(validity='INVALID',exclusion_reason='INVALID_SPILL',concentration_value='')
    early,projected=p.first_projection(coords,rows)
    assert len(projected)==69 and len(early)==69
    assert all(r['fraction']==1 and r['species']=='5CQA' for r in projected)
    target=next(r for r in rows if r['shot_id']=='FIT-E01-R1' and r['fraction_id']=='1' and r['analyte']=='5CQA')
    for changes in ({'source_id':'P24-MAT-PRED'},{'concentration_unit':'percent'},
                    {'condition_id':'FIT-C02'},{'physical_replicate_id':'2'},
                    {'validity':'INVALID'},{'concentration_value':''},{'concentration_value':'nan'}):
        changed=[dict(r,**changes) if r is target else r for r in rows]
        with pytest.raises(ValueError,match='SOURCE_CONTRACT_BLOCKED'): p.first_projection(coords,changed)
    with pytest.raises(ValueError,match='DUPLICATE'): p.first_projection(coords,rows+[target])
    with pytest.raises(ValueError,match='MISSING'): p.first_projection(coords,[r for r in rows if r is not target])
    with pytest.raises(ValueError,match='MISSING'):
        p.first_projection(coords,[dict(r,analyte='CQA_sum') if r is target else r for r in rows])
    changed=[dict(r,concentration_value='0') if r is target else r for r in rows]
    assert p.first_projection(coords,changed)[0]['FIT-E01-R1'][2]==0


def test_first_original_formula_projection_never_accesses_second_or_suffix(monkeypatch):
    coords,rows,_=fixture();early,projected=p.first_projection(coords,rows)
    class FirstOnly:
        def __getitem__(self,index):
            assert index==(0,2)
            return 1.0
    class MassOnly:
        def __getitem__(self,index):
            assert index==0
            return 4.0
    objects={label:[SimpleNamespace(run=[SimpleNamespace(cAlcaloids=FirstOnly(),mE=MassOnly()) for _ in range(3)])
                    for _ in range(count)] for label,count in [('FIT',15),('PRED',8)]}
    monkeypatch.setattr(p.source,'mat',lambda label:{'ExperimentalData':objects[label]})
    def books(label):
        sign,offset,slope=('-',78.923,24.513) if label=='FIT' else ('+',88.067,26.383)
        fs,cs={},{}
        for e in range(1,(15 if label=='FIT' else 8)+1):
            name=f'{3*e-2}-{3*e}'
            f=[[SimpleNamespace(value=None) for _ in range(25)] for _ in range(28)]
            c=copy.deepcopy(f);f[8][24].value='Chlorogenic acid'
            for rep in range(3):
                row=10+6*rep
                f[row-1][24].value=f'=(I{row}{sign}{offset})/({slope}*1000)*$C{row}*$B{row}'
                c[row-1][1].value=2.;c[row-1][2].value=10.
                c[row-1][8].value=4./20*slope*1000+(offset if label=='FIT' else -offset)
                c[row-1][24].value=4.
            fs[name],cs[name]=f,c
        return fs,cs
    monkeypatch.setattr(p,'source_books',books)
    paths={f'P24-{kind}-{label}':label for kind in ('MAT','HPLC') for label in ('FIT','PRED')}
    actual,audit=p.original_first_assays(paths,early,projected)
    assert actual==early and audit['first_fraction_reconciliations']=={'FIT':45,'PRED':24}
    assert audit['fraction_2_assays_projected']==0
    f,c=books('FIT');f['1-3'][9][24].value='=wrong_analyte'
    with pytest.raises(ValueError,match='SOURCE_CONTRACT_BLOCKED'):
        p.formula_cell(f,c,'FIT',1,1,1)


def test_later_pred_chemistry_and_forbidden_inputs_cannot_change_training_or_queries(tmp_path):
    coords,rows,groups=fixture()
    before=p.build_projections(coords,rows,groups)
    class Poison:
        def __float__(self): raise AssertionError('forbidden chemical value accessed')
        def __bool__(self): raise AssertionError('forbidden chemical missingness accessed')
    changed=copy.deepcopy(rows)
    for r in changed:
        permitted=r['analyte']=='5CQA' and (r['fraction_id']=='1' or
                   (r['campaign_id']=='FIT_2021_12' and int(r['fraction_id']) in p.SUFFIX))
        if not permitted:
            r['concentration_value']=Poison();r['measured_concentration']=Poison()
        r['temperature_start_C']=Poison();r['recipe']=Poison()
    after=p.build_projections(coords,changed,groups)
    assert before==after
    a,b=train.FitProblem(train.project_arm(before['training']),.01),train.FitProblem(train.project_arm(after['training']),.01)
    np.testing.assert_array_equal(a.starts,b.starts)
    np.testing.assert_array_equal(a.residual(a.starts[0]),b.residual(b.starts[0]))
    fitted=[]
    for index, projection in enumerate((before,after)):
        budget=train.Budget(tmp_path/str(index),synthetic=True)
        try:
            model,audit=train.fit(train.project_arm(projection['training']),.01,budget,
                                  'L1.synthetic','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
            assert audit['status']=='CONVERGED' and model is not None
            fitted.append(model.to_dict())
        finally:
            budget.worker_lock.close()
    assert fitted[0]==fitted[1]
    assert before['source_counts']['PRED_suffix_values_projected']==0
    assert before['source_counts']['PRED_first_assay_values_projected']==24
    assert all('q' not in q and 'measured_concentration' not in q for q in before['queries'])


def models():
    # Public retained models need no corpus and are unchanged historical controls.
    result={a:p.legacy.md.Model.load(p.legacy.DOC/'models'/f'{a}.json') for a in p.legacy.ARMS}
    result.update({a:synthetic_model(a) for a in p.md.ARMS})
    result['L1']=replace(result['L1'],theta=[[-6.,0.,0.,2.]]*5)
    return result


def test_permitted_first_assay_changes_new_arms_only_and_pred_poison_has_no_effect():
    coords,rows,groups=fixture();projected=p.build_projections(coords,rows,groups)
    query=projected['queries'][:1];early=projected['early_inputs'];ms=models()
    before,_=p.predict_records(ms,early,query)
    altered=copy.deepcopy(early);altered[query[0]['shot']][2]=.003
    after,_=p.predict_records(ms,altered,query)
    assert before['E0']==after['E0'] and before['D0']==after['D0']
    for arm in p.md.ARMS:
        assert before[arm][0]['five_cqa_kg']!=after[arm][0]['five_cqa_kg']
    poisoned=copy.deepcopy(rows)
    for row in poisoned:
        if row['campaign_id']=='PREDICTION_2022_03' and row['fraction_id']!='1':
            row['measured_concentration']='NaN'
    q=p.build_projections(coords,poisoned,groups)
    replay,_=p.predict_records(ms,q['early_inputs'],q['queries'][:1])
    assert replay==before


def synthetic_scores(errors):
    observations,predictions=[],{arm:[] for arm in p.ARMS}
    for i,condition in enumerate(sum((list(v) for v in p.PANELS.values()),[]),1):
        for rep in (1,2,3):
            for fraction in p.SUFFIX:
                shot=f'PRED-E{i:02d}-R{rep}'
                observations.append(dict(shot=shot,condition=condition,fraction=fraction,
                    analyte_eligible=True,q=.001,mass_kg=.005))
                for arm in p.ARMS:
                    e=errors[arm]*(1 if rep%2 else -1)
                    predictions[arm].append(dict(shot=shot,condition=condition,fraction=fraction,
                        supported=True,reason='',prediction_status='QUALIFIED',numerical_qualified=True,
                        five_cqa_mg_g=1+e,five_cqa_kg=.005*(1+e)/1000,allowance_kg=1e-14,feature_extrapolation=[]))
    return observations,predictions


@pytest.mark.parametrize('errors,label,least,earned',[
    ({'E0':.4,'D0':.4,'A1':.1,'L1':.09},'A1_ADEQUATE_LEARNED_INCREMENT_NOT_ESTABLISHED','A1',False),
    ({'E0':.4,'D0':.4,'A1':.1,'L1':.01},'L1_ADEQUATE_AND_EARNED','A1',True),
    ({'E0':.4,'D0':.12,'A1':.4,'L1':.1},'ADEQUATE_INCREMENT_NOT_ESTABLISHED','L1',False),
    ({'E0':.4,'D0':.4,'A1':.4,'L1':.4},'TESTED_FIRST_ASSAY_FIVE_CQA_FAMILIES_INADEQUATE',None,False)])
def test_adequacy_and_earned_increment_remain_separate(errors,label,least,earned):
    result,_=p.evaluate(*synthetic_scores(errors))
    assert result['disposition']==label and result['least_complex_adequate_new_arm']==least
    assert result['learned_route_earned']==earned
    assert set(result['pairwise_complexity'])=={'A1_vs_E0','A1_vs_D0','L1_vs_D0','L1_vs_A1'}
    metric=result['panels']['primary']['A1']['full_scope_metrics']
    assert metric['absB_mg_g']==pytest.approx(errors['A1'])
    assert metric['B_mg_g']==pytest.approx(errors['A1']/3)
    assert result['panels']['primary']['A1']['original_slots']==48


def test_missing_support_or_numerics_is_not_negative_scientific_result():
    observed,predicted=synthetic_scores(dict.fromkeys(p.ARMS,.05))
    for arm in p.ARMS:
        predicted[arm][0].update(supported=False,reason='SYNTHETIC_MISSING',numerical_qualified=False)
    result,_=p.evaluate(observed,predicted)
    assert result['disposition']=='SUPPORT_OR_NUMERICAL_RESULT_NOT_ADJUDICATED'
    assert result['panels']['primary']['A1']['original_slots']==48
    observed,predicted=synthetic_scores(dict.fromkeys(p.ARMS,.05))
    predicted['L1'][0]['numerical_qualified']=False
    result,_=p.evaluate(observed,predicted)
    assert result['disposition']=='SUPPORT_OR_NUMERICAL_RESULT_NOT_ADJUDICATED'


def test_numerical_metric_bounds_and_incomplete_failure_lower_bound():
    observed,predicted=synthetic_scores(dict.fromkeys(p.ARMS,.4))
    for arm in p.ARMS:
        predicted[arm][0].update(supported=False,reason='SYNTHETIC_MISSING',numerical_qualified=False)
    result,_=p.evaluate(observed,predicted)
    condition=result['panels']['primary']['A1']['conditions'][p.PANELS['primary'][0]]
    assert condition['adequacy']=='FAIL' and condition['original_slots']==12
    assert condition['complete_shot_full_condition_lower_bounds']['R_mg_g']>.25
    assert p.legacy.upper(.25,1e-9,.25)=='UNRESOLVED'
    assert p.legacy.upper(.25-2e-9,1e-9,.25)=='PASS'
    assert p.legacy.upper(.25+2e-9,1e-9,.25)=='FAIL'
    row=observed[1];pred=predicted['A1'][1]
    value=p.legacy.shot_metrics([row],[pred])
    assert value['R_allowance_mg_g']==pytest.approx(1000*pred['allowance_kg']/row['mass_kg'])


def test_single_score_guard_precedes_outcome_read(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'check_task_clock',lambda:None)
    def forbidden(*a,**k): pytest.fail('outcome reader before receipt guard')
    monkeypatch.setattr(p.source_geometry,'all_rows',forbidden)
    for name in ('score_receipt.json','scores.json','score_completion.json','observed_suffix.json','shot_results.json'):
        path=tmp_path/name;path.write_text('{}')
        with pytest.raises(ValueError,match='DUPLICATE_SCORE'): p.score(tmp_path,tmp_path/'absent_review.json')
        path.unlink()


def test_missing_independent_review_cannot_score(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'check_task_clock',lambda:None)
    with pytest.raises(FileNotFoundError): p.score(tmp_path,tmp_path/'absent_review.json')
    assert not (tmp_path/'score_receipt.json').exists()

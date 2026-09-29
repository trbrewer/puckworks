"""Synthetic source firewall, matched support and the complete decision matrix."""
import copy
from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import pannusch_early_assay_5cqa_delivery as p
from puckworks.analysis import early_assay_5cqa_training as train
from test_early_assay_5cqa_delivery import synthetic_model


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
    exclusions=[]
    for shot in p.EXCLUDED_SHOTS:
        exclusions.append(dict(shot_id=shot,campaign_id='FIT_2021_12',fraction_id='2',
                               analyte_or_measurement='ALL_HPLC_ANALYTES',normalized_status='INVALID_SPILL'))
    for row in rows:
        if row['shot_id'] in p.EXCLUDED_SHOTS and row['fraction_id']=='2' and row['analyte']=='5CQA':
            row.update(validity='INVALID',exclusion_reason='INVALID_SPILL',concentration_value='0')
    for c in coords:
        if (c['shot'],c['fraction']) in {('FIT-E01-R3',7),('FIT-E01-R3',10),('FIT-E06-R3',10)}:
            c.update(b0=None,b1=None,coordinate_status='UNAVAILABLE_MEASURED_MASS_PREFIX')
    return coords,rows,groups,exclusions


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



def test_matched_cohort_source_exclusions_and_valid_zero():
    coords,rows,groups,excluded=fixture()
    early,first,second=p.early_projection(coords,rows,excluded)
    assert len(first)==69 and len(second)==66
    assert all(early[s][3] is None for s in p.EXCLUDED_SHOTS)
    result=p.build_projections(coords,rows,groups,excluded)
    assert result['source_counts']['fit_original_physical_shots']==45
    assert result['source_counts']['fit_eligible_physical_shots']==42
    assert result['source_counts']['fit_eligible_intended_slots']==168
    assert result['source_counts']['fit_supported_slots']==165
    masks=[]
    for arm in p.ARMS:
        shots=train.project_arm(result['training'],arm)
        masks.append([(s.shot,[(w.fraction,w.start_kg,w.end_kg) for w in s.windows]) for s in shots])
    assert masks[0]==masks[1]==masks[2]
    for f in result['development_support']:
        assert not set(f['training_shots'])&set(f['held_shots'])
        assert len(f['training_shots'])+len(f['held_shots'])==42
    target=next(r for r in rows if r['shot_id']=='FIT-E01-R1' and r['fraction_id']=='2' and r['analyte']=='5CQA')
    target['concentration_value']='0'
    assert p.early_projection(coords,rows,excluded)[0]['FIT-E01-R1'][3]==0
    bad=copy.deepcopy(rows)
    for row in bad:
        if row['shot_id'] in p.EXCLUDED_SHOTS and row['fraction_id']=='2' and row['analyte']=='5CQA':
            row.update(validity='VALID',exclusion_reason='')
    with pytest.raises(ValueError,match='SPILL'): p.early_projection(coords,bad,excluded)
    with pytest.raises(ValueError,match='EXCLUSION'): p.early_projection(coords,rows,excluded[:-1])
    with pytest.raises(ValueError,match='IDENTITY'): p.early_projection(coords,rows+[target],excluded)


def test_pred_suffix_recipe_and_unused_identity_poisoning():
    coords,rows,groups,excluded=fixture()
    before=p.build_projections(coords,rows,groups,excluded)
    class Poison:
        def __float__(self): raise AssertionError('forbidden concentration')
        def __bool__(self): raise AssertionError('forbidden missingness')
    changed=copy.deepcopy(rows)
    for r in changed:
        permitted=r['analyte']=='5CQA' and (r['fraction_id'] in ('1','2') or
            (r['campaign_id']=='FIT_2021_12' and int(r['fraction_id']) in p.SUFFIX))
        if not permitted: r['concentration_value']=Poison();r['measured_concentration']=Poison()
        r['recipe']=Poison();r['temperature_start_C']=Poison();r['batch_id']=Poison()
    after=p.build_projections(coords,changed,groups,excluded)
    assert before==after
    for arm in p.ARMS:
        a,b=(train.FitProblem(train.project_arm(x['training'],arm),.01) for x in (before,after))
        np.testing.assert_array_equal(a.starts,b.starts)
        np.testing.assert_array_equal(a.features,b.features)
        np.testing.assert_array_equal(a.residual(a.starts[0]),b.residual(b.starts[0]))
    models={a:synthetic_model(a) for a in p.ARMS}
    original,_=p.predict_records(models,before['early_inputs'],before['queries'])
    replay,_=p.predict_records(models,after['early_inputs'],after['queries'])
    assert original==replay
    # Query identities are join labels, not model features. Relabel coherently.
    queries=copy.deepcopy(before['queries']);early={}
    for q in queries:
        old=q['shot'];q['shot']='RELABELED-'+old;q['condition']='RELABELED'
        early[q['shot']]=before['early_inputs'][old]
    relabeled,_=p.predict_records(models,early,queries)
    for arm in p.ARMS:
        assert [r['five_cqa_kg'] for r in original[arm]]==[r['five_cqa_kg'] for r in relabeled[arm]]
    assert before['source_counts']['PRED_suffix_values_projected']==0


def test_permitted_assay_changes_only_consuming_arms():
    c,r,g,e=fixture();data=p.build_projections(c,r,g,e)
    models={a:replace(synthetic_model(a),theta=[[-6.,0.,0.]+[2.]*(len(p.md.feature_names(a))-2)]*5) for a in p.ARMS}
    query=data['queries'][:1];early=data['early_inputs'];before,_=p.predict_records(models,early,query)
    for index,unchanged,changed in [(3,'L1M',('L2M','L12')),(2,'L2M',('L1M','L12'))]:
        altered=copy.deepcopy(early);altered[query[0]['shot']][index]=.003
        after,_=p.predict_records(models,altered,query)
        assert before[unchanged]==after[unchanged]
        for arm in changed: assert before[arm][0]['five_cqa_kg']!=after[arm][0]['five_cqa_kg']


def test_original_early_scalar_firewall(monkeypatch):
    c,r,_,e=fixture();early,first,second=p.early_projection(c,r,e)
    class EarlyOnly:
        def __getitem__(self,index):
            assert index in ((0,2),(1,2))
            return 1.
    class MassOnly:
        def __getitem__(self,index):
            assert index in (0,1)
            return (4.,6.)[index]
    objects={label:[SimpleNamespace(run=[SimpleNamespace(cAlcaloids=EarlyOnly(),mE=MassOnly()) for _ in range(3)])
                   for _ in range(count)] for label,count in [('FIT',15),('PRED',8)]}
    monkeypatch.setattr(p.source,'mat',lambda label:{'ExperimentalData':objects[label]})
    monkeypatch.setattr(p.previous,'source_books',lambda label:({},{}))
    monkeypatch.setattr(p,'source_books',lambda label:({},{}))
    def formula(f,c,label,e,j,fraction):
        assert fraction in (1,2)
        assert not (fraction==2 and f'{label}-E{e:02d}-R{j}' in p.EXCLUDED_SHOTS)
        return (4.,6.)[fraction-1]
    monkeypatch.setattr(p.previous,'formula_cell',formula);monkeypatch.setattr(p,'formula_cell',formula)
    paths={f'P24-{kind}-{label}':label for kind in ('MAT','HPLC') for label in ('FIT','PRED')}
    original,audit=p.original_early_assays(paths,early,first,second)
    assert original==early
    assert audit['second_fraction_reconciliations']=={'FIT':42,'PRED':24}
    assert audit['first_fraction_reconciliations']=={'FIT':45,'PRED':24}


@pytest.mark.parametrize('errors,label,singles,earned',[
    ({'L1M':.1,'L2M':.11,'L12':.01},'TWO_ASSAY_MAPPING_EARNED',['L1M','L2M'],True),
    ({'L1M':.4,'L2M':.1,'L12':.09},'SINGLE_ASSAY_ADEQUATE_NO_EARNED_TWO_ASSAY_COMPLEXITY',['L2M'],False),
    ({'L1M':.14,'L2M':.14,'L12':.12},'ADEQUATE_INCREMENT_NOT_ESTABLISHED',[],False),
    ({'L1M':.4,'L2M':.4,'L12':.4},'TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE',[],False)])
def test_adequacy_placement_and_both_increments_are_separate(errors,label,singles,earned):
    result,_=p.evaluate(*synthetic_scores(errors))
    assert result['disposition']==label and result['adequate_single_assay_contracts']==singles
    assert result['two_assay_route_earned']==earned
    assert set(result['pairwise_complexity'])=={'L2M_vs_L1M','L12_vs_L1M','L12_vs_L2M'}
    metric=result['panels']['primary']['L1M']['full_scope_metrics']
    assert metric['absB_mg_g']==pytest.approx(errors['L1M'])
    assert metric['B_mg_g']==pytest.approx(errors['L1M']/3)
    assert result['panels']['primary']['L1M']['original_slots']==48
    if errors['L1M']==.4 and errors['L2M']==.1:
        assert result['pairwise_complexity']['L12_vs_L1M']['status']=='PASS'
        assert result['pairwise_complexity']['L12_vs_L2M']['status']=='FAIL'
        assert result['single_assay_placement_earned']


def test_missing_support_numerical_unresolved_and_original_denominator_failure_bounds():
    for error,label in [(.05,'SOURCE_SUPPORT_INCOMPLETE'),(.4,'TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE')]:
        observed,predicted=synthetic_scores(dict.fromkeys(p.ARMS,error))
        for arm in p.ARMS: predicted[arm][0].update(supported=False,reason='MISSING',numerical_qualified=False)
        result,_=p.evaluate(observed,predicted)
        assert result['disposition']==label
        c=result['panels']['primary']['L1M']['conditions'][p.PANELS['primary'][0]]
        assert c['original_slots']==12
        if error==.4: assert c['complete_shot_full_condition_lower_bounds']['R_mg_g']>.25
    observed,predicted=synthetic_scores(dict.fromkeys(p.ARMS,.05))
    predicted['L12'][0]['numerical_qualified']=False
    result,_=p.evaluate(observed,predicted)
    assert result['disposition']=='NUMERICAL_OR_DECISION_UNRESOLVED'
    assert p.legacy.upper(.25,1e-9,.25)=='UNRESOLVED'
    assert p.legacy.upper(.25-2e-9,1e-9,.25)=='PASS'
    assert p.legacy.upper(.25+2e-9,1e-9,.25)=='FAIL'
    metric=p.legacy.shot_metrics([observed[1]],[predicted['L1M'][1]])
    assert metric['R_allowance_mg_g']==pytest.approx(1000e-14/.005)
    # A nominal material gain at its threshold must retain numerical ambiguity.
    result,_=p.evaluate(*synthetic_scores({'L1M':.1,'L2M':.1,'L12':.05}))
    assert result['pairwise_complexity']['L12_vs_L1M']['status']=='UNRESOLVED'
    assert result['disposition']=='NUMERICAL_OR_DECISION_UNRESOLVED'


def test_repeated_score_guard_precedes_source_or_review_access(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'check_task_clock',lambda:None)
    def forbidden(*a,**k): pytest.fail('forbidden access before score guard')
    monkeypatch.setattr(p.source_geometry,'all_rows',forbidden)
    monkeypatch.setattr(p,'task_run',forbidden)
    for name in ('score_receipt.json','scores.json','score_completion.json','observed_suffix.json','shot_results.json'):
        path=tmp_path/name;path.write_text('{}')
        with pytest.raises(ValueError,match='DUPLICATE_SCORE'): p.score(tmp_path,tmp_path/'absent.json')
        path.unlink()


def test_missing_review_cannot_join_outcomes(tmp_path,monkeypatch):
    monkeypatch.setattr(p,'check_task_clock',lambda:None)
    monkeypatch.setattr(p,'task_run',lambda out:out)
    with pytest.raises(FileNotFoundError): p.score(tmp_path,tmp_path/'absent.json')
    assert not (tmp_path/'score_receipt.json').exists()

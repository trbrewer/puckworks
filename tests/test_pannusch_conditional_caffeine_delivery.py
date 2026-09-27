"""Synthetic source firewall, denominator and decision adversaries."""
from copy import deepcopy
import json
from pathlib import Path

import pytest

from puckworks.analysis import conditional_caffeine_delivery as md
from puckworks.analysis import conditional_caffeine_scoring as scoring
from puckworks.analysis import pannusch_conditional_caffeine_delivery as pipeline


def source_fixture():
    coords=[];rows=[]
    for label,campaign in [('FIT','FIT_2021_12'),('PRED','PREDICTION_2022_03')]:
        for f in (1,2,3,5,7,10):
            c={'campaign':campaign,'condition':label+'-C01','shot':label+'-E01-R1','fraction':f,
               'b0':.008 if f==3 else .01+f*.001,'b1':.02+f*.001,'mass_kg':.01,
               'coordinate_status':'QUALIFIED'}
            coords.append(c)
            for analyte,unit in [('caffeine','mg/g'),('TDS','percent')]:
                rows.append({'campaign_id':campaign,'condition_id':c['condition'],'shot_id':c['shot'],
                    'fraction_id':str(f),'analyte':analyte,'concentration_unit':unit,'validity':'VALID',
                    'source_id':'SYNTHETIC','concentration_value':'2','measured_concentration':'2',
                    'exclusion_reason':''})
    return coords,rows


def test_no_early_caffeine_and_pred_target_permutation_invariance():
    coords,rows=source_fixture()
    pred=pipeline.target_slots(coords,rows,campaign='PREDICTION_2022_03')
    assert len(pred)==4 and all('q' not in r for r in pred)
    models={a:md.synthetic_model(a) for a in md.ARMS}
    early={'PRED-E01-R1':[.004,.004,.15,.1]}
    for q in pred:q.update(supported=True,reason='')
    before=pipeline.predict_records(models,early,pred)
    changed=deepcopy(rows)
    for r in changed:
        if r['campaign_id']=='PREDICTION_2022_03' and (r['analyte']=='caffeine' or int(r['fraction_id']) in (3,5,7,10)):
            r['measured_concentration']='987654321'
        if r['analyte']=='caffeine' and int(r['fraction_id']) in (1,2):
            r['concentration_value']='EARLY_CAFFEINE_CANARY'
    after=pipeline.target_slots(coords,changed,campaign='PREDICTION_2022_03')
    for q in after:q.update(supported=True,reason='')
    assert after==pred
    assert pipeline.predict_records(models,early,after)==before
    fit=pipeline.target_slots(coords,changed,campaign='FIT_2021_12',include_values=True)
    assert len(fit)==4 and all(r['q']==.002 for r in fit)


def test_invalid_analyte_missing_row_and_coordinate_status_kept():
    coords,rows=source_fixture()
    rows=[r for r in rows if not (r['shot_id']=='FIT-E01-R1' and r['analyte']=='caffeine' and r['fraction_id']=='5')]
    for r in rows:
        if r['shot_id']=='FIT-E01-R1' and r['analyte']=='caffeine' and r['fraction_id']=='3':
            r.update(validity='INVALID',exclusion_reason='INVALID_SPILL',concentration_value='0')
    slots=pipeline.target_slots(coords,rows,campaign='FIT_2021_12',include_values=True)
    assert len(slots)==4
    assert slots[0]['q'] is None and slots[0]['validity_reason']=='INVALID_SPILL'
    assert slots[1]['q'] is None and slots[1]['validity_reason']=='MISSING_CAFFEINE_SOURCE_ROW'
    assert all(r['validity']=='VALID' for r in rows if r['analyte']=='TDS')
    assert all(s['source_field'] for s in slots if s['analyte_eligible'])


def scored_fixture(errors):
    obs=[];pred={a:[] for a in md.ARMS}
    for c in range(1,9):
        for r in range(1,4):
            for f in pipeline.SUFFIX:
                shot=f'PRED-E{c:02}-R{r}';condition=f'PRED-C{c:02}'
                obs.append({'shot':shot,'condition':condition,'fraction':f,'analyte_eligible':True,'q':.002,'mass_kg':.004})
                for a in md.ARMS:
                    e=errors[a]*(1 if r!=2 else -1)
                    pred[a].append({'shot':shot,'condition':condition,'fraction':f,'supported':True,'reason':'',
                        'numerical_qualified':True,'caffeine_mg_g':2+e,'caffeine_kg':(2+e)*.004/1000,
                        'allowance_kg':1e-15,'feature_extrapolation':[],'prediction_status':'QUALIFIED'})
    return obs,pred


def test_absolute_bias_does_not_cancel_and_all_arms_scored():
    obs,pred=scored_fixture(dict.fromkeys(md.ARMS,.3))
    result,_=scoring.evaluate(obs,pred)
    assert result['adequacy_by_arm']==dict.fromkeys(md.ARMS,'FAIL')
    assert result['disposition']=='TESTED_CAFFEINE_MODELS_INADEQUATE'
    m=result['panels']['primary']['S2']['full_scope_metrics']
    assert m['B_mg_g']==pytest.approx(.1) and m['absB_mg_g']==pytest.approx(.3)
    assert m['assayed_interval_mass_MAE_mg']==pytest.approx(1.2)


def test_earned_and_simpler_and_no_posthoc_primary_selection():
    obs,pred=scored_fixture({'D0':.4,'S0':.4,'S1':.4,'S2':.1})
    result,_=scoring.evaluate(obs,pred)
    assert result['decision_vector']==dict.fromkeys('ABCD','PASS')
    assert result['disposition']=='TDS_CONDITIONED_CAFFEINE_MAPPING_EARNED'
    obs,pred=scored_fixture({'D0':.1,'S0':.4,'S1':.4,'S2':.1})
    result,_=scoring.evaluate(obs,pred)
    assert result['adequate_simpler_arms']==['D0']
    assert result['disposition']=='SIMPLER_CAFFEINE_PREDICTOR_ADEQUATE_NO_EARNED_COMPLEXITY'
    assert result['primary_candidate']=='S2'


def test_missing_or_numerical_slot_cannot_be_favorable_exclusion():
    obs,pred=scored_fixture(dict.fromkeys(md.ARMS,.1))
    for ps in pred.values():ps[0].update(supported=False,reason='SOURCE_MISSING',numerical_qualified=False)
    result,_=scoring.evaluate(obs,pred)
    assert result['decision_vector']['A']==scoring.INCOMPLETE
    entry=result['panels']['primary']['S2']
    assert entry['full_scope_metrics'] is None and entry['original_shots']==12
    assert entry['supported_subset_diagnostic']['R_mg_g']==pytest.approx(.1)
    obs,pred=scored_fixture(dict.fromkeys(md.ARMS,.1))
    for ps in pred.values():ps[0].update(numerical_qualified=False,prediction_status='NUMERICALLY_UNQUALIFIED')
    result,_=scoring.evaluate(obs,pred)
    assert result['disposition']==scoring.UNRESOLVED
    assert result['panels']['primary']['S2']['supported_subset_diagnostic'] is None


def test_common_support_and_fixed_denominators():
    obs,pred=scored_fixture(dict.fromkeys(md.ARMS,.1))
    pred['D0'][0].update(supported=False,reason='bad')
    with pytest.raises(ValueError,match='IDENTICAL_COMPARISON'):scoring.evaluate(obs,pred)
    with pytest.raises(ValueError):scoring.evaluate(obs[:-1],pred)


def test_borderline_not_rounded_and_strict_bias_budget():
    assert scoring.upper(.50,1e-10,.50)==scoring.UNRESOLVED
    obs,pred=scored_fixture({'D0':.3,'S0':.3,'S1':.3,'S2':.2})
    result,_=scoring.evaluate(obs,pred)
    assert result['decision_vector']['B'] == scoring.UNRESOLVED


def test_score_guard_rejects_missing_approval_before_outcomes(tmp_path,monkeypatch):
    monkeypatch.setattr(pipeline,'target_slots',lambda *a,**kw:pytest.fail('outcome access'))
    review=tmp_path/'review.json';review.write_text('{}')
    (tmp_path/'freeze.json').write_text(json.dumps({'producer_commit':'h','producer_tree':'t'}))
    with pytest.raises(ValueError):scoring.score(tmp_path,review)
    (tmp_path/'score_receipt.json').write_text('{}')
    with pytest.raises(ValueError,match='DUPLICATE'):scoring.verify_before_score(tmp_path,review)


def test_report_reads_only_retained_scores(tmp_path,monkeypatch):
    monkeypatch.setattr(pipeline,'target_slots',lambda *a,**kw:pytest.fail('outcomes'))
    monkeypatch.setattr(pipeline,'predict',lambda *a,**kw:pytest.fail('prediction'))
    (tmp_path/'scores.json').write_text('{"synthetic":true}')
    (tmp_path/'score_completion.json').write_text(json.dumps({'status':'COMPLETE','scores_sha256':pipeline.digest(tmp_path/'scores.json')}))
    assert scoring.report(tmp_path)=={'synthetic':True}
    (tmp_path/'scores.json').write_text('{}')
    with pytest.raises(ValueError):scoring.report(tmp_path)


def test_no_parent_refitting_in_pipeline_source():
    text=Path(pipeline.__file__).read_text()
    assert 'old_train.fit(' not in text and 'old.final_fit(' not in text

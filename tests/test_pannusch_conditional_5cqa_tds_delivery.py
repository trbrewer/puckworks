"""Synthetic source, decision and single-score adversaries; no physical observations."""
import copy
from dataclasses import replace
import pytest
from puckworks.analysis import pannusch_conditional_5cqa_tds_delivery as p
from puckworks.analysis import conditional_5cqa_tds_training as tr


def test_five_cqa_single_score_guard(tmp_path, monkeypatch):
    monkeypatch.setattr(p, 'check_task_clock', lambda: None)
    def forbidden():
        pytest.fail('outcome reader ran before the single-score guard')
    monkeypatch.setattr(p.source_geometry, 'all_rows', forbidden)
    for name in ('score_receipt.json', 'scores.json', 'score_completion.json', 'observed_suffix.json', 'shot_results.json'):
        path = tmp_path/name; path.write_text('{}')
        with pytest.raises(ValueError, match='DUPLICATE_SCORE'):
            p.score(tmp_path, tmp_path/'nonexistent-review.json')
        path.unlink()

def test_intervening_vials_and_unknown_prefix_are_never_reconstructed(monkeypatch):
    import numpy as np
    from types import SimpleNamespace
    masses=np.arange(1.,11.)
    run=SimpleNamespace(mE=masses,mE_cum=np.cumsum(masses),tE=np.arange(1.,11.))
    rows=p.source.mass_coordinates(run)
    fifth=next(r for r in rows if r['fraction']==5)
    assert fifth['b0']==.010 and fifth['b1']==.015
    assert fifth['b0']!=sum(masses[[0,1,2]])*.001
    class Sheet:
        def cell(self,row,col):
            if col==1: value=1
            elif col==6: value=None  # Missing intervening fourth vial.
            else: value=10. if row==3 else 10.+masses[col-3]
            return SimpleNamespace(value=value)
    monkeypatch.setattr(p.source, 'workbook', lambda path:{'SampleWeights':Sheet()})
    projected=p.source_geometry.fit_source.measured_coordinates(None,1,run)
    later=next(r for r in projected if r['fraction']==5)
    assert later['b0'] is None and later['b1'] is None
    assert later['coordinate_status']=='UNAVAILABLE_MEASURED_MASS_PREFIX'

def test_failed_score_is_durably_consumed_before_outcome_read(tmp_path,monkeypatch):
    monkeypatch.setattr(p, 'check_task_clock', lambda: None)
    for name in ('freeze.json','predictions.json','queries.json','review.json'):
        (tmp_path/name).write_text('[]' if name=='queries.json' else '{}')
    def checked(out,review): p.score_guard(out)
    monkeypatch.setattr(p,'verify_before_score',checked)
    def fail(): raise RuntimeError('synthetic source failure')
    monkeypatch.setattr(p.source_geometry,'all_rows',fail)
    with pytest.raises(RuntimeError,match='synthetic source failure'):
        p.score(tmp_path,tmp_path/'review.json')
    assert (tmp_path/'score_receipt.json').exists()
    with pytest.raises(ValueError,match='DUPLICATE_SCORE'):
        p.score(tmp_path,tmp_path/'review.json')

def test_independent_approval_requires_exact_identity_and_scope(tmp_path, monkeypatch):
    """Synthetic receipts exercise the existing verifier; they grant no real approval."""
    from puckworks.analysis import pannusch_conditioned_mass_delivery as receipt
    frozen = dict(task=p.TASK, arms=list(p.ARMS), producer_commit='SYNTHETIC_HEAD',
                  producer_tree='SYNTHETIC_TREE', code_and_protocol={}, artifacts={},
                  outcomes_attached=False)
    p.write(tmp_path/'freeze.json', frozen)
    p.write(tmp_path/'source.json', {})
    monkeypatch.setattr(receipt.old, 'verify_registers', lambda value: None)
    monkeypatch.setattr(p, 'verify_frozen', lambda out: frozen)
    monkeypatch.setattr(p, 'qualified_sources', lambda: ({}, {}))
    approved = dict(task=p.TASK, status='APPROVED', independent=True,
                    reviewer='SYNTHETIC_TEST_NOT_AN_APPROVAL',
                    freeze_sha256=p.digest(tmp_path/'freeze.json'),
                    reviewed_head='SYNTHETIC_HEAD', reviewed_tree='SYNTHETIC_TREE',
                    unresolved_blocking_findings=[], future_chemistry_attached=False,
                    approval_scope='ONE_PREDECLARED_FROZEN_PRED_SCORE_ONLY_NO_RETUNING')
    for i, (key, value) in enumerate([
        ('status', 'PENDING'), ('independent', False), ('freeze_sha256', 'wrong'),
        ('reviewed_head', 'wrong'), ('reviewed_tree', 'wrong'), ('task', 'wrong'),
        ('reviewer', ''), ('unresolved_blocking_findings', ['defect']),
        ('future_chemistry_attached', True), ('approval_scope', 'wrong')]):
        review = tmp_path/f'review-{i}.json'
        p.write(review, dict(approved, **{key:value}))
        with pytest.raises(ValueError): p.verify_before_score(tmp_path, review)
    review=tmp_path/'synthetic-valid-shape.json'
    p.write(review, approved)
    assert p.verify_before_score(tmp_path, review)==frozen

def test_report_reads_retained_result_without_outcome_join(tmp_path, monkeypatch):
    p.write(tmp_path/'freeze.json', {})
    p.write(tmp_path/'predictions.json', {})
    freeze_hash=p.digest(tmp_path/'freeze.json')
    p.write(tmp_path/'score_receipt.json', dict(task=p.TASK, freeze_sha256=freeze_hash,
            review_sha256='SYNTHETIC', predictions_sha256=p.digest(tmp_path/'predictions.json')))
    result={'task':p.TASK, 'disposition':'SYNTHETIC_RESULT'}
    p.write(tmp_path/'scores.json', result)
    p.write(tmp_path/'shot_results.json', {})
    p.write(tmp_path/'observed_suffix.json', [])
    p.write(tmp_path/'score_completion.json', dict(task=p.TASK, status='COMPLETE',
            scientific_score_passes=1, freeze_sha256=freeze_hash, review_sha256='SYNTHETIC',
            files={n:p.digest(tmp_path/n) for n in ('scores.json','shot_results.json',
                   'observed_suffix.json','score_receipt.json')}))
    monkeypatch.setattr(p, 'verify_frozen', lambda out: {})
    def forbidden(*args,**kwargs): pytest.fail('report attempted scientific recomputation')
    for name in ('score','evaluate','predict_records'):
        monkeypatch.setattr(p,name,forbidden)
    monkeypatch.setattr(p.source_geometry,'all_rows',forbidden)
    assert p.report(tmp_path)==result


def complete_source():
    coords, rows, groups = [], [], {}
    for label,count,campaign in [('FIT',15,'FIT_2021_12'),('PRED',8,'PREDICTION_2022_03')]:
        for e in range(1,count+1):
            condition=f'{label}-C{e:02}'
            if label=='FIT':groups[condition]=condition
            for rep in (1,2,3):
                shot=f'{label}-E{e:02}-R{rep}'
                for f in (1,2,3,5,7,10):
                    coords.append(dict(campaign=campaign,condition=condition,shot=shot,fraction=f,
                        b0=(f-1)*.004,b1=f*.004,mass_kg=.004,coordinate_status='QUALIFIED',source_id='SYNTHETIC'))
                    for analyte,unit,value in [('5CQA','mg/g','.5'),('TDS','percent','10')]:
                        rows.append(dict(campaign_id=campaign,condition_id=condition,shot_id=shot,
                            fraction_id=str(f),source_experiment_id=str(e),physical_replicate_id=str(rep),
                            analyte=analyte,concentration_unit=unit,validity='VALID',source_id='SYNTHETIC',
                            concentration_value=value,measured_concentration=value,exclusion_reason='',
                            fraction_basis='MEASURED_MASS_G',fraction_liquid_g_or_ml='4',
                            analyte_mass_mg='400',derived_analyte_mass_mg='400'))
    parents={}
    for group in groups:
        ids=[c['shot'] for c in coords if c['campaign']=='FIT_2021_12' and c['condition']!=group]
        parents[group]=replace(p.md.parent.synthetic_model('C2'),regularization=.0001,
            training_identity_json=p.canonical({'scope':'SYNTHETIC','shots':sorted(set(ids)),
                                                'groups':sorted(set(groups)-{group})}))
    final=replace(p.md.parent.synthetic_model('C2'),regularization=.0001)
    return coords,rows,groups,parents,final


def test_exact_support_missingness_and_analyte_specific_spill():
    coords,rows,groups,parents,final=complete_source()
    for r in rows:
        if r['analyte']=='5CQA' and r['shot_id']=='FIT-E01-R1' and r['fraction_id']=='3':
            r.update(validity='INVALID',exclusion_reason='SYNTHETIC_HPLC_SPILL')
    for c in coords:
        if (c['shot']=='FIT-E02-R1' and c['fraction'] in (7,10)) or (c['shot']=='PRED-E08-R3' and c['fraction']==10):
            c.update(coordinate_status='UNAVAILABLE_MEASURED_MASS_PREFIX',b0=None,b1=None)
    projected=p.build_projections(coords,rows,groups,parents,final)
    counts=projected['source_counts']
    assert counts['fit_intended_slots']==180 and counts['fit_supported_slots']==177
    assert counts['panels']['primary']==dict(original_shots=12,intended_slots=48,supported_slots=48)
    assert counts['panels']['temperature_stress']['supported_slots']==24
    assert counts['panels']['flow_stress']==dict(original_shots=6,intended_slots=24,supported_slots=23)
    assert len(projected['queries'])==96 and len(projected['fit_slots'])==180
    assert all(len(s['early_values'])==4 for s in projected['training'])
    assert projected['training'][0]['early_values'][2:]==[.1,.1]
    assert all('q' not in q for q in projected['queries'])
    with pytest.raises(ValueError,match='PARENT_MATRIX'):
        p.build_projections(coords,rows,groups,{k:v for k,v in parents.items() if k!='FIT-C01'},final)


def test_pred_chemistry_metadata_poisoning_cannot_change_fit_starts_or_predictions():
    coords,rows,groups,parents,final=complete_source()
    first=p.build_projections(coords,rows,groups,parents,final)
    poisoned=copy.deepcopy(rows);changed=copy.deepcopy(coords)
    for c in changed:c.update(temperature='POISON',flow='POISON',pressure='POISON',recipe='POISON')
    for r in poisoned:
        r.update(temperature='POISON',flow='POISON',pressure='POISON',recipe='POISON')
        if r['campaign_id']=='PREDICTION_2022_03' and (r['analyte']!='TDS' or int(r['fraction_id'])>2):
            r['concentration_value']=r['measured_concentration']='9999999'
        if r['analyte']=='5CQA' and int(r['fraction_id'])<3:
            r['concentration_value']=r['measured_concentration']='EARLY_5CQA_FORBIDDEN'
    second=p.build_projections(changed,poisoned,groups,parents,final)
    assert first==second
    for arm in p.md.ARMS:
        a=tr.FitProblem(tr.project_arm(first['training'],arm),None if arm=='S0' else .01,final,scope='SYNTHETIC')
        b=tr.FitProblem(tr.project_arm(second['training'],arm),None if arm=='S0' else .01,final,scope='SYNTHETIC')
        assert tr.provenance(a,'SYNTHETIC','SYNTHETIC')==tr.provenance(b,'SYNTHETIC','SYNTHETIC')
        assert [v.tolist() for v in a.starts]==[v.tolist() for v in b.starts]
    models={a:(legacy_synthetic_model(a) if a in p.legacy.ARMS else p.md.synthetic_model(a)) for a in p.ARMS}
    before=p.predict_records(models,first['early_inputs'],first['queries'])
    after=p.predict_records(models,second['early_inputs'],second['queries'])
    assert before==after and sum(len(v) for v in before[0].values())==480


def scored_fixture(errors):
    obs=[];pred={a:[] for a in p.ARMS}
    for c in range(1,9):
        for r in range(1,4):
            for f in p.SUFFIX:
                shot=f'PRED-E{c:02}-R{r}';condition=f'PRED-C{c:02}'
                obs.append(dict(shot=shot,condition=condition,fraction=f,analyte_eligible=True,q=.002,mass_kg=.004))
                for a in p.ARMS:
                    e=errors[a]*(1 if r!=2 else -1)
                    pred[a].append(dict(shot=shot,condition=condition,fraction=f,supported=True,reason='',
                        numerical_qualified=True,five_cqa_mg_g=2+e,five_cqa_kg=(2+e)*.004/1000,
                        allowance_kg=1e-15,feature_extrapolation=[],prediction_status='QUALIFIED'))
    return obs,pred


def test_all_families_inadequate_requires_definite_complete_evidence():
    obs,pred=scored_fixture(dict.fromkeys(p.ARMS,.3));result,_=p.evaluate(obs,pred)
    assert result['disposition']=='TESTED_TDS_CONDITIONED_FIVE_CQA_FAMILIES_INADEQUATE'
    m=result['panels']['primary']['S2']['full_scope_metrics']
    assert m['B_mg_g']==pytest.approx(.1) and m['absB_mg_g']==pytest.approx(.3)
    for ps in pred.values():ps[0].update(supported=False,reason='SOURCE_MISSING',numerical_qualified=False)
    result,_=p.evaluate(obs,pred)
    assert result['disposition']=='NOT_ADJUDICATED_PRIMARY_SUPPORT_OR_NUMERICAL_FAILURE'
    assert result['panels']['primary']['S2']['original_slots']==48
    assert result['panels']['primary']['S2']['full_scope_metrics'] is None


@pytest.mark.parametrize('errors,least,replacement,label',[
    ({'S0':.1,'S1':.09,'S2':.08},'S0',None,'CONSTANT_SHARE_FIVE_CQA_ADEQUATE'),
    ({'S0':.3,'S1':.12,'S2':.10},'S1','S1','MASS_CONDITIONED_SHARE_INCREMENT_EARNED'),
    ({'S0':.3,'S1':.2,'S2':.10},'S2','S2','TDS_CONDITIONED_SHARE_INCREMENT_EARNED'),
    ({'S0':.13,'S1':.12,'S2':.11},'S1',None,'ADEQUATE_INCREMENT_NOT_ESTABLISHED')])
def test_adequacy_least_complex_and_earned_replacement_are_separate(errors,least,replacement,label):
    obs,pred=scored_fixture(dict(E0=.4,D0=.4,**errors));result,_=p.evaluate(obs,pred)
    assert result['least_complex_adequate_new_arm']==least
    assert result['earned_replacement_arm']==replacement and result['disposition']==label
    assert set(result['pairwise_complexity'])=={'S1_vs_S0','S2_vs_S1','S2_vs_S0'}


def test_common_support_and_numerical_thresholds_cannot_pass_by_rounding():
    obs,pred=scored_fixture(dict.fromkeys(p.ARMS,.125));result,_=p.evaluate(obs,pred)
    assert result['disposition']=='NOT_ADJUDICATED_PRIMARY_THRESHOLD_OVERLAP'
    pred['S2'][0].update(supported=False,reason='BAD')
    with pytest.raises(ValueError,match='IDENTICAL_COMPARISON'):p.evaluate(obs,pred)
    with pytest.raises(ValueError):p.evaluate(obs[:-1],pred)


def test_frozen_predecessor_bytes_and_source_identities_preserved():
    for relative,sha in p.read(p.DOC/'DEPENDENCIES.json')['files'].items():
        assert p.digest(p.ROOT/relative)==sha
    assert p.read(p.DOC/'SOURCE_IDENTITIES.json')==p.read(p.ROOT/'docs/analysis/sci_md_5cqa_delivery_001/SOURCE_IDENTITIES.json')


def legacy_synthetic_model(arm):
    from scipy.special import logit
    return p.legacy.md.Model(arm, [[float(logit(.001)),0.,0.]]*5 if arm=='D0' else (),
        (.004,.006),(.002,.003),(.009,.01),.08,.01 if arm=='D0' else None,
        .001 if arm=='E0' else None,.03 if arm=='E0' else None,
        p.canonical({'scope':'SYNTHETIC'}),'SYNTHETIC_FIRST_PARTY')


def test_complexity_threshold_overlap_retains_adequacy_but_not_adjudication():
    obs,pred=scored_fixture(dict(E0=.3,D0=.3,S0=.15,S1=.1,S2=.1))
    result,_=p.evaluate(obs,pred)
    assert result['adequacy_by_arm']['S1']=='PASS'
    assert result['pairwise_complexity']['S1_vs_S0']['status']==p.UNRESOLVED
    assert result['disposition']=='NOT_ADJUDICATED_COMPLEXITY_THRESHOLD_OVERLAP'

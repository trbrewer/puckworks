import copy

import numpy as np
import pytest

from puckworks.analysis import pannusch_conditional_tail_delivery as s
from puckworks.analysis import conditional_tail_scoring as score


def coordinates():
    return [dict(campaign='FIT_2021_12' if label == 'FIT' else 'PREDICTION_2022_03',
        condition=f'{label}-C{i:02d}', shot=f'{label}-E{i:02d}-R{r}', fraction=f,
        b0=(f-1)*.005,b1=f*.005,mass_kg=.005,coordinate_status='QUALIFIED',source_id='P24-MAT-'+label)
        for label,n in [('FIT',15),('PRED',8)] for i in range(1,n+1) for r in (1,2,3) for f in (1,2)+s.SUFFIX]


def assay_rows(coords):
    return [dict(campaign_id=c['campaign'],condition_id=c['condition'],shot_id=c['shot'],
        source_experiment_id=c['shot'][6:8] if c['shot'].startswith('PRED') else c['shot'][5:7],
        physical_replicate_id=c['shot'][-1],fraction_id=str(c['fraction']),analyte='TDS',
        concentration_value='10',measured_concentration='10',concentration_unit='percent',
        fraction_basis='MEASURED_MASS_G',fraction_liquid_g_or_ml='5',analyte_mass_mg='500',
        derived_analyte_mass_mg='500',validity='VALID',exclusion_reason='',source_id=c['source_id']) for c in coords]


def test_pred_suffix_perturbation_leaves_training_and_predictions_unchanged():
    coords = coordinates(); rows = assay_rows(coords)
    before = s.projections(coords,rows)[:4]
    for row in rows:
        if row['shot_id'].startswith('PRED') and int(row['fraction_id']) in s.SUFFIX:
            row['measured_concentration'] = 'FORBIDDEN_CHEMISTRY_CANARY'
            row['derived_analyte_mass_mg'] = 'FORBIDDEN'
    after = s.projections(coords,list(reversed(rows)))[:4]
    assert before == after
    for arm in s.md.ARMS:
        a, b = (s.train.FitProblem(s.train.project_arm(x[0],arm),.01) for x in (before,after))
        assert np.array_equal(a.means,b.means) and a.domain == b.domain
        assert all(np.array_equal(x,y) for x,y in zip(a.starts,b.starts))
        theta = np.linspace(-1,1,a.size)
        assert np.array_equal(a.residual(theta),b.residual(theta))
        # Every fit input and objective is identical; model/state/prediction bytes
        # are consequently independent of the forbidden chemistry projection.
        ma,mb = [p.model(theta,{'scope':'SYNTHETIC'},'SYNTHETIC') for p in (a,b)]
        assert ma.to_dict() == mb.to_dict()
        inputs = s.md.EarlyInput(arm,tuple(before[1]['PRED-E01-R1']['values'][:len(ma.means)]))
        assert ma.condition(inputs).predict_intervals([.01],[.015]) == mb.condition(inputs).predict_intervals([.01],[.015])


def test_unknown_prefix_retained_and_hplc_flags_not_used():
    coords=coordinates(); rows=assay_rows(coords)
    coords[5].update(b0=None,b1=None,coordinate_status='UNAVAILABLE_MEASURED_MASS_PREFIX')
    rows.append(dict(rows[0],analyte='caffeine',validity='INVALID'))
    training,early,queries,statuses,_=s.projections(coords,rows)
    assert len(training)==45 and len(early)==24 and len(queries)==96
    assert len(statuses)==180 and sum(x['eligible'] for x in statuses)==179
    assert len(training[0]['windows'])==3
    assert all(x['supported'] for x in queries)


def fixture():
    coords=[c for c in coordinates() if c['shot'].startswith('PRED') and c['fraction'] in s.SUFFIX]
    observed=[dict(c,eligible=True,q=.1,solute_kg=.0005) for c in coords]
    predictions={}
    for arm in (*s.md.ARMS,s.LEGACY):
        e=.2 if arm=='C2' else .4
        predictions[arm]=[dict(c,supported=True,reason='',legacy_supported=True,legacy_reason='',
            predicted_tds_percent=10+e,predicted_solute_kg=.005*(10+e)/100,
            numerical_allowance_kg=0.,numerical_qualified=True,prediction_status='QUALIFIED',
            feature_extrapolation=[]) for c in coords]
    return observed,predictions


def test_decisions_condition_shot_balance_and_primary_fixed():
    o,p=fixture(); result,_=score.evaluate(o,p)
    assert result['decision_vector']=={'A':'PASS','B':'PASS','C':'PASS','D':'PASS','limitations':[]}
    assert result['disposition']=='LEARNED_TWO_ASSAY_MAPPING_EARNED'
    assert result['primary_candidate']=='C2'
    assert result['panels']['primary']['C2']['full_scope_metrics']['R_pp']==pytest.approx(.2)


def test_opposite_shot_bias_not_cancelled_before_absolute():
    o,p=fixture()
    for r in p['C2']:
        r['predicted_tds_percent']=10+(.6 if r['shot'].endswith('R1') else -.6)
    result,_=score.evaluate(o,p)
    c=result['panels']['primary']['C2']['conditions']['PRED-C01']['full_scope_metrics']
    assert c['B_pp']==pytest.approx(-.2) and c['absB_pp']==pytest.approx(.6)
    assert result['decision_vector']['A']=='FAIL'


def test_missing_windows_cannot_pass_or_hide_definite_failure():
    o,p=fixture()
    for arm in p:
        for r in p[arm]:
            if r['condition']=='PRED-C01' and r['shot'].endswith(('R1','R2')):
                r['predicted_tds_percent']=12
            if r['shot']=='PRED-E01-R3' and r['fraction']==10:
                r.update(supported=False,reason='MISSING_PREFIX',numerical_qualified=False,predicted_tds_percent=None)
    result,_=score.evaluate(o,p)
    c=result['panels']['primary']['C2']['conditions']['PRED-C01']
    assert c['complete_shots']==2 and c['full_scope_adequacy']=='FAIL'
    assert c['complete_shot_full_condition_lower_bounds']['absB_pp']==pytest.approx(4/3)
    assert result['decision_vector']['A']=='FAIL' and result['decision_vector']['B']!='PASS'
    assert result['panels']['primary']['C2']['full_scope_metrics'] is None
    p['C2'].pop()
    with pytest.raises(ValueError):
        score.evaluate(o,p)


def test_partial_signed_bias_is_not_full_bias_lower_bound():
    o,p=fixture()
    for arm in p:
        for r in p[arm]:
            r['predicted_tds_percent']=30
            if r['fraction']==10:
                r.update(supported=False,reason='MISSING_PREFIX',numerical_qualified=False,predicted_tds_percent=None)
    result,_=score.evaluate(o,p)
    c=result['panels']['primary']['C2']['conditions']['PRED-C01']
    assert c['complete_shot_full_condition_lower_bounds']=={'R_pp':0.,'absB_pp':0.}
    assert c['full_scope_adequacy']=='SOURCE_SUPPORT_INCOMPLETE'


def test_failure_and_legacy_overlap_do_not_improve_decision():
    o,p=fixture(); p['C2'][0]['numerical_qualified']=False
    result,_=score.evaluate(o,p)
    assert result['decision_vector']['A']!='PASS'
    o,p=fixture()
    for arm in p:
        p[arm][0]['legacy_supported']=False
    result,_=score.evaluate(o,p)
    assert result['decision_vector']['A']=='PASS' and result['decision_vector']['D']=='SOURCE_SUPPORT_INCOMPLETE'


def test_numerical_gate_and_zero_reference():
    o,p=fixture()
    for r in p['C2']:
        r.update(predicted_tds_percent=10.5,numerical_allowance_kg=1e-9)
    result,_=score.evaluate(o,p)
    assert result['decision_vector']['A']=='NUMERICALLY_UNRESOLVED'
    zero=copy.deepcopy(result['panels']['primary']['C0'])
    zero['full_scope_metrics']['R_pp']=0
    zero['full_scope_metrics']['R_allowance_pp']=0
    assert score.material_gain(result['panels']['primary']['C2'],zero)['status']=='FAIL'


def test_report_only_retained_artifacts_and_duplicate_receipt(tmp_path,monkeypatch):
    s.write(tmp_path/'score_receipt.json',{'status':'STARTED'})
    with pytest.raises(ValueError,match='DUPLICATE_SCORE'):
        score.verify_before_score(tmp_path,tmp_path/'missing_review.json')
    monkeypatch.setattr(score,'evaluate',lambda *a: pytest.fail('report rescored'))
    s.write(tmp_path/'scores.json',{'retained':True})
    s.write(tmp_path/'score_completion.json',{'status':'COMPLETE','scores_sha256':s.digest(tmp_path/'scores.json')})
    assert score.report(tmp_path)=={'retained':True}


def test_source_boundary_conversion_preserves_strict_runtime():
    model=s.md.synthetic_model()
    state=model.condition(s.md.EarlyInput('C2',(.006123,.009222200000000003,.15,.1)))
    before=float(np.nextafter(state.b_anchor,0))
    with pytest.raises(ValueError,match='BEFORE_FORECAST_ANCHOR'):
        state.predict_intervals([before],[.03])
    start,allowance=s.source_query_start({'fraction':3,'b0':before},state)
    assert start==state.b_anchor and allowance==2*(state.b_anchor-before)
    with pytest.raises(ValueError,match='ANCHOR_MISMATCH'):
        s.source_query_start({'fraction':3,'b0':before-.0001},state)
    assert s.source_query_start({'fraction':5,'b0':.03},state)==(.03,0.)

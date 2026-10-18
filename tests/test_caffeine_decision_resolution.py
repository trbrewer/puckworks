"""Invented fixtures fixed in SYNTHETIC_SPEC.md; no restricted observations."""
from copy import deepcopy
import ast
import json
from pathlib import Path

import pytest

from puckworks.analysis import caffeine_decision_resolution as c


def metric(r=0.2, b=0.1, u=0., windows=4):
    return {'R_mg_g': r, 'B_mg_g': b, 'absB_mg_g': abs(b),
            'R_allowance_mg_g': u, 'B_allowance_mg_g': u, 'absB_allowance_mg_g': u,
            'assayed_interval_mass_RMSE_mg': 1., 'assayed_mass_signed_error_mg': b,
            'assayed_interval_mass_MAE_mg': 1., 'windows': windows,
            'assayed_beverage_kg': .04, 'observed_assayed_caffeine_kg': .0001,
            'predicted_assayed_caffeine_kg': .00011}


def record(shot, condition, r=.2, b=.1, u=0., incomplete=False):
    m = metric(r, b, u, 3 if incomplete else 4)
    return {'shot': shot, 'condition': condition, 'full': None if incomplete else m,
            'support_diagnostic': m, 'coverage': {'intended': 4, 'supported': m['windows'], 'qualified': m['windows']}}


def cohort():
    out = {}
    for panel, conditions in c.PANELS.items():
        out[panel] = {}
        for arm in c.ARMS:
            out[panel][arm] = [record(f'SYNTHETIC-{condition}-{i}', condition,
                 r=.2 if arm == 'S2' else .22,
                 incomplete=panel == 'flow_stress' and condition == 'PRED-C07' and i == 0)
                 for condition in conditions for i in range(3)]
    return out


@pytest.mark.parametrize('v,u,t,expected', [(.375,.125,.5,'PASS'),(.625,.125,.5,c.UNRESOLVED),
    (.75,.125,.5,'FAIL'),(.5,0.,.5,'PASS'),(None,0.,.5,c.INCOMPLETE),(.5,None,.5,c.INCOMPLETE)])
def test_historical_boundaries(v,u,t,expected):
    assert c.upper(v,u,t) == expected


def test_failure_and_incomplete_precedence():
    assert c.conjunction(['FAIL', c.INCOMPLETE, c.UNRESOLVED]) == 'FAIL'
    assert c.conjunction(['PASS', c.INCOMPLETE, c.UNRESOLVED]) == c.INCOMPLETE
    assert c.conjunction(['PASS',c.UNRESOLVED]) == c.UNRESOLVED


def test_fraction_units_retained_concentration_total_allowance():
    # A deliberately different integration interval cannot change retained concentration.
    rows = [{'mass_kg': .001, 'q': .001}, {'mass_kg': .003, 'q': .001}]
    ps = [{'caffeine_mg_g':2., 'caffeine_kg':.000002, 'allowance_kg':1e-7,
           'coordinate_allowance_kg':5e-8, 'integration_start_kg':.00001},
          {'caffeine_mg_g':0., 'caffeine_kg':0., 'allowance_kg':3e-7,
           'coordinate_allowance_kg':1e-7}]
    m = c.fraction_metric(rows,ps)
    assert m['R_mg_g'] == 1
    assert m['B_mg_g'] == -.5
    assert m['absB_mg_g'] == .5
    assert m['R_allowance_mg_g'] == pytest.approx(.1)
    assert m['B_allowance_mg_g'] == pytest.approx(.1)
    assert m['assayed_interval_mass_RMSE_mg'] == pytest.approx(5**.5)
    assert m['assayed_interval_mass_MAE_mg'] == pytest.approx(2.)
    assert m['assayed_mass_signed_error_mg'] == pytest.approx(-2.)


def test_absolute_bias_before_average():
    m = c.mean_metrics([metric(1,1),metric(1,-1)])
    assert m['B_mg_g'] == 0
    assert m['absB_mg_g'] == 1


def test_equal_condition_weights_after_paired_deletion():
    rows = [record(f's{i}', 'one' if i < 3 else 'two', i+1) for i in range(6)]
    arms = {a:deepcopy(rows) for a in c.ARMS}
    baseline = c.reduce_scenario(arms, ('one','two'))
    deleted = c.reduce_scenario(arms, ('one','two'), deleted='s0')
    for a in c.ARMS:
        assert baseline['arms'][a]['balanced']['R_mg_g'] == 3.5
        assert deleted['arms'][a]['balanced']['R_mg_g'] == 3.75
    assert deleted['retained_shots'] == ['s1','s2','s3','s4','s5']


@pytest.mark.parametrize('r,status,lower',[(.9,'FAIL',.6),(.6,c.INCOMPLETE,.4)])
def test_incomplete_lower_bound_original_denominator(r,status,lower):
    rows = [record('a','c',r),record('b','c',r),record('d','c',incomplete=True)]
    got = c.condition_result(rows)
    assert got['full_scope_adequacy'] == status
    assert got['complete_shot_full_condition_lower_bounds']['R_mg_g'] == pytest.approx(lower)
    assert got['full_scope_metrics'] is None


def test_relative_denominator_guard_and_positive_failed_increment():
    data = c.reproduce(c.validate_shots(cohort()))
    assert data['adequacy_by_arm'] == dict.fromkeys(c.ARMS,'PASS')
    assert data['decision_vector'] == {'A':'PASS','B':'FAIL','C':'FAIL','D':'FAIL'}
    for v in data['increments'].values():
        assert v['R_improvement_mg_g'] == pytest.approx(.02)
        assert v['components']['absolute_gain'] == 'FAIL'
    cand = deepcopy(data['panels']['primary']['S2']); ref = deepcopy(cand)
    for con in cand['conditions'].values():
        con['full_scope_metrics'] = metric(0,0)
    cand['full_scope_metrics'] = metric(0,0)
    ref['full_scope_metrics'] = metric(1e-12,0)
    g = c.increment(cand,ref)
    assert g['components']['relative_gain'] == 'FAIL'
    assert g['relative_improvement'] is None
    ref['complete_scope'] = False
    assert c.increment(cand,ref)['status'] == c.INCOMPLETE


def test_strict_definite_and_possible_wins():
    assert c.wins({'x':metric(.25,u=.125)}, {'x':metric(.5,u=.125)}) == (0,1)
    assert c.wins({'x':metric(.25)}, {'x':metric(.5)}) == (1,1)
    assert c.wins({'x':metric(.5)}, {'x':metric(.5)}) == (0,0)


@pytest.mark.parametrize('definite,possible,expected',[(2,2,'FAIL'),(2,3,c.UNRESOLVED),(3,3,'PASS')])
def test_condition_win_accounting(definite,possible,expected):
    cs={};rs={}
    for i in range(4):
        cs[str(i)] = {'full_scope_metrics':metric(.25,u=.125 if definite <= i < possible else 0)}
        rs[str(i)] = {'full_scope_metrics':metric(.5 if i < possible else .1,u=.125 if definite <= i < possible else 0)}
    candidate={'complete_scope':True,'full_scope_metrics':metric(.2),'conditions':cs}
    reference={'complete_scope':True,'full_scope_metrics':metric(.4),'conditions':rs}
    got=c.increment(candidate,reference)
    assert got['definite_condition_wins']==definite
    assert got['possible_condition_wins']==possible
    assert got['components']['condition_wins']==expected


def test_deletion_counts_actual_membership_and_no_flow_deletion():
    data = c.validate_shots(cohort())
    before = deepcopy(data)
    public, private = c.analyze(data)
    assert data == before
    for panel,n in [('primary',12),('temperature_stress',6)]:
        scenarios=private[panel]['scenarios']
        assert len(scenarios)==n+1
        removed={s['deleted_shot'] for s in scenarios[1:]}
        assert removed==set(scenarios[0]['retained_shots'])
        for s in scenarios[1:]:
            assert len(s['retained_shots'])==n-1
            assert s['deleted_shot'] not in s['retained_shots']
            assert s['conditions']==list(c.PANELS[panel])
        for ref in c.REFS:
            summary=public[panel]['sensitivity'][ref]
            assert summary['deletion_gain_sign_counts']=={'positive':n,'zero':0,'negative':0}
            assert summary['policy_sensitivity']['contractual']=='UNAVAILABLE'
            assert summary['policy_sensitivity']['resolution']=='UNRESOLVED'
    assert len(private['flow_stress']['scenarios'])==1
    assert len(private['flow_stress']['scenarios'][0]['retained_shots'])==6
    text=json.dumps(public)
    for forbidden in ('SYNTHETIC-', 'deleted_shot', 'retained_shots', 'paired_shots', '/home/'):
        assert forbidden not in text


def test_separate_points_and_envelope_and_equality():
    def row(g,u):
        x=c.contrast(metric(.2),metric(.2+g,u=u));x['R_improvement_mg_g']=g
        x.update(definite_condition_wins=4,possible_condition_wins=4)
        return {'comparisons':{'S1':x}}
    scenarios=[row(.02,.001),row(.01,.02),row(.03,.001)]
    got,_=c.summarize_sensitivity(scenarios,'S1','synthetic')
    assert got['deletion_ranges']['R_improvement_mg_g']==[.01,.03]
    assert got['baseline_plus_deletions_envelopes']['R_improvement_mg_g']==[-.01,.031]
    assert got['all_deletion_point_gains_strictly_positive'] is True
    assert got['all_deletion_allowance_lower_endpoints_strictly_positive'] is False
    zero,_=c.summarize_sensitivity([row(0,0),row(0,0)],'S1','synthetic')
    assert zero['all_deletion_point_gains_strictly_positive'] is False


@pytest.mark.parametrize('mutation', ['duplicate','missing','wrong_condition','different_support','nan','negative_allowance','abs_bias'])
def test_reject_incompatible_shots(mutation):
    data=cohort(); rows=data['primary']['S1']
    if mutation=='duplicate': rows[1]=deepcopy(rows[0])
    if mutation=='missing': rows.pop()
    if mutation=='wrong_condition': rows[0]['condition']='PRED-C08'
    if mutation=='different_support': rows[0]['coverage']['supported']=3
    if mutation=='nan': rows[0]['full']['R_mg_g']=float('nan')
    if mutation=='negative_allowance': rows[0]['full']['R_allowance_mg_g']=-1
    if mutation=='abs_bias': rows[0]['full']['absB_mg_g']=-1
    with pytest.raises(ValueError): c.validate_shots(data)


def observations():
    return [dict(shot=f'SYN-{con}-{i}',condition=con,fraction=f,campaign='PREDICTION_2022_03',
            analyte='caffeine',source_id='P24-MAT-PRED',source_field='synthetic',analyte_eligible=True,
            coordinate_status='QUALIFIED',b0=.01+i*.001,b1=.02+i*.002,mass_kg=.01+i*.001,q=(i+1)/1000,
            supported=not(con=='PRED-C07' and i==0 and f==10))
        for cs in c.PANELS.values() for con in cs for i in range(3) for f in c.FRACTIONS]


def test_source_observed_variability_distinct_from_support():
    obs=observations(); cells=c.variability(obs,obs)
    assert len(cells)==32
    for v in cells:
        assert v['observation_n']==3
        assert v['mean']==2
        assert v['sample_sd']==1
        assert v['left_edge_range']==[.01,.012]
    restricted=next(v for v in cells if v['condition']=='PRED-C07' and v['fraction']==10)
    assert restricted['scoring_support_n']==2
    assert c.spread([1])['sd'] is None


def test_identity_units_crosswalk():
    obs=observations()
    bad=deepcopy(obs);bad[0]['analyte']='TDS'
    with pytest.raises(ValueError): c.validate_windows(bad)
    bad=deepcopy(obs);bad[0]['q']=1000
    with pytest.raises(ValueError): c.validate_windows(bad)
    bad=deepcopy(obs);bad[0]['mass_kg']=0
    with pytest.raises(ValueError): c.validate_windows(bad)
    bad=deepcopy(obs);bad[1]=deepcopy(bad[0])
    with pytest.raises(ValueError): c.validate_windows(bad)


def test_hash_binding_exclusive_output_and_determinism(tmp_path):
    p=tmp_path/'input';p.write_text('retained')
    tracker=c.Inputs()
    with pytest.raises(c.IntegrityStop): tracker.bytes(p,'0'*64)
    tracker.bytes(p);p.write_text('changed')
    with pytest.raises(c.IntegrityStop): tracker.recheck()
    out=c.private_output(tmp_path/'new')
    with pytest.raises(FileExistsError): c.private_output(out)
    with pytest.raises(ValueError): c.private_output(p/'new',(p,))
    with pytest.raises(ValueError): c.private_output(c.ROOT/'test-not-written')
    a,_=c.analyze(cohort());b,_=c.analyze(cohort())
    assert json.dumps(a,sort_keys=True)==json.dumps(b,sort_keys=True)


def test_no_historical_lifecycle_or_native_imports_or_calls():
    source=Path(c.__file__).read_text();tree=ast.parse(source)
    imports=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    assert not any('conditional_caffeine' in n or 'pannusch_' in n for n in imports)
    calls=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
    assert not set(calls)&{'fit','predict','score','prepare','develop','freeze','simulate','system','Popen'}


def test_crosswalk_geometry_and_common_support_adversaries():
    obs=observations()
    queries=[{**r,'reason':'' if r['supported'] else 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN'} for r in obs]
    c.crosswalk(obs,queries)
    bad=deepcopy(queries);bad[0]['b0']+=.001
    with pytest.raises(ValueError): c.crosswalk(obs,bad)
    bad=deepcopy(queries);bad[0]['supported']=False
    with pytest.raises(ValueError): c.crosswalk(obs,bad)
    bad=deepcopy(queries);bad.pop()
    with pytest.raises(ValueError): c.crosswalk(obs,bad)


def test_window_pairing_uses_all_slots_and_same_arm_masks():
    obs=observations();predictions={a:[] for a in c.ARMS}
    for a in c.ARMS:
        for r in obs:
            predictions[a].append({**r,'reason':'' if r['supported'] else 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN',
                'numerical_qualified':r['supported'],'caffeine_mg_g':1.,'caffeine_kg':.00001,
                'allowance_kg':1e-10,'coordinate_allowance_kg':0.})
    oi,pi=c.window_pairing(obs,predictions)
    assert len(oi)==96 and all(len(p)==96 for p in pi.values())
    bad=deepcopy(predictions);bad['S2'][0]['supported']=False;bad['S2'][0]['numerical_qualified']=False
    with pytest.raises(ValueError): c.window_pairing(obs,bad)
    bad=deepcopy(predictions);bad['D0'].pop()
    with pytest.raises(ValueError): c.window_pairing(obs,bad)
    bad=deepcopy(predictions);bad['S1'][0]['allowance_kg']=-1
    with pytest.raises(ValueError): c.window_pairing(obs,bad)


def test_public_receipt_fallback_when_private_run_is_unmounted(tmp_path):
    # Public byte commitments only: no restricted inputs or scientific reduction.
    data, available, _ = c.admit(tmp_path, c.Inputs())
    for name in ('scores.json', 'score_completion.json', 'score_receipt.json'):
        assert available[name]['status'] == 'ADMITTED'
        assert name in data
    assert available['shot_results.json']['status'] == 'UNAVAILABLE'
    assert 'shot_results.json' not in data

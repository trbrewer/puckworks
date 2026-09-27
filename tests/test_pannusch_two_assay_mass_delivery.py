"""Synthetic source/role and scoring tests; never require source data."""
import copy
from dataclasses import asdict, replace
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import pannusch_two_assay_mass_delivery as s
from puckworks.analysis import two_assay_mass_delivery as md


def coordinates():
    return [dict(campaign='PREDICTION_2022_03' if shot.startswith('PRED') else 'FIT_2021_12',
        condition=shot.split('-R')[0].replace('-E', '-C'), shot=shot, fraction=f,
        b0=(f-1)*.005, b1=f*.005, mass_kg=.005, coordinate_status='QUALIFIED',
        source_id='P24-MAT-PRED' if shot.startswith('PRED') else 'P24-MAT-FIT')
        for shot in s.SHOTS for f in (1, 2)+s.SUFFIX]


def assay_rows(coords):
    return [dict(campaign_id=c['campaign'], condition_id=c['condition'], shot_id=c['shot'],
        source_experiment_id=str(int(c['shot'].split('-E')[1].split('-')[0])), physical_replicate_id=c['shot'][-1],
        fraction_id=str(c['fraction']), analyte='TDS', concentration_value='10', measured_concentration='10',
        concentration_unit='percent', fraction_basis='MEASURED_MASS_G', fraction_liquid_g_or_ml='5',
        analyte_mass_mg='500', derived_analyte_mass_mg='500', validity='VALID', exclusion_reason='',
        source_id=c['source_id']) for c in coords]


def fixture():
    coords = coordinates()
    mask = s.support_mask(coords, assay_rows(coords), (0., .06))
    observed = [dict(q, eligible=True, q=.1, solute_kg=.0005, source_rounding_allowance_kg=0.) for q in mask]
    predictions = {a: [dict(q, predicted_solute_kg=.0005+q['mass_kg']*(.2 if a==s.PRIMARY else .6)/100,
        predicted_tds_percent=10.2 if a==s.PRIMARY else 10.6, numerical_allowance_kg=0.,
        numerical_qualified=True, tds_sensitivity_pp_per_pp=(1.,0.), prediction_status='QUALIFIED') for q in mask] for a in s.ARMS}
    return observed, predictions


def test_exact_rosters_and_reclassified_second_assay():
    assert len(s.SHOTS)==42 and sum(map(len,s.PANELS.values()))==14
    assert set(s.SUFFIX)=={3,5,7,10}
    assert not set(s.SHOTS)&set(s.fit_source.CALIBRATION)
    assert s.pred_source.SUFFIX==(2,3,5,7,10)  # historical role untouched
    assert s.fit_source.SUFFIX==(2,3,5,7,10)


def test_support_only_reads_flags_coordinates_and_keeps_missing_slots():
    coords=coordinates(); rows=assay_rows(coords)
    reference=s.support_mask(coords,rows,(0.,.06))
    for r in rows:
        r['concentration_value']=object(); r['measured_concentration']=object()
    assert s.support_mask(coords,rows,(0.,.06))==reference
    coords[5]['b1']=.08
    coords[4].update(coordinate_status='UNAVAILABLE_MEASURED_MASS_PREFIX',b0=None,b1=None)
    other=s.support_mask(coords,rows,(0.,.06))
    assert len(other)==168 and sum(q['primary_mask'] for q in other)==166
    assert len({q['shot'] for q in other})==42


def test_leakage_canary_pair_and_prediction_identity(monkeypatch):
    coords=coordinates(); rows=assay_rows(coords)
    original_pairs, _=s.extract_pairs(rows,coords)
    original_mask=s.support_mask(coords,rows,(0.,.06))
    for r in rows:
        if int(r['fraction_id']) in s.SUFFIX:
            r['concentration_value']='DO_NOT_PARSE'; r['measured_concentration']='DO_NOT_PARSE'
    rows.reverse()
    changed_pairs,_=s.extract_pairs(rows,coords)
    changed_mask=s.support_mask(coords,rows,(0.,.06))
    assert changed_pairs==original_pairs and changed_mask==original_mask
    # These are exactly the ONLY prediction-facing inputs; synthetic states
    # with constant observations keep this 1008-row end-to-end check inexpensive.
    bases=s.load_bases()
    before=s.predict_bundle(bases,original_pairs,original_mask)
    after=s.predict_bundle(bases,changed_pairs,changed_mask)
    assert before==after
    assert sum(map(len,before[0].values()))==1008
    assert before[3]['two_parameter_update_attempts']==84
    assert before[3]['analytical_amplitude_update_attempts']==168
    bad=copy.deepcopy(original_mask);bad[0]['later_tds']=4
    with pytest.raises(ValueError,match='COORDINATE_ONLY'):
        s.predict_bundle(bases,original_pairs,bad)


def test_missing_unassayed_vial_invalidates_only_later_prefix(monkeypatch):
    masses=np.arange(1.,11.)
    run=SimpleNamespace(mE=masses,mE_cum=np.cumsum(masses),tE=np.arange(1.,11.))
    class Sheet:
        def cell(self,row,col):
            if col==1:return SimpleNamespace(value=1)
            f=col-3
            return SimpleNamespace(value=None if f==5 else 10. if row==3 else 10.+masses[f])
    monkeypatch.setattr(s.source,'workbook',lambda _: {'SampleWeights':Sheet()})
    cc=s.fit_source.measured_coordinates('unused',1,run)
    assert cc[3]['b1']==pytest.approx(.015)
    assert cc[4]['fraction']==7 and cc[4]['b0'] is None and cc[4]['mass_kg']==.007
    assert all(c['coordinate_status']=='QUALIFIED' for c in cc[:4])


def test_invalid_anchor_not_silently_excluded_and_hplc_not_tds():
    coords=coordinates(); rows=assay_rows(coords)
    rows.append(dict(rows[0],analyte='caffeine',validity='INVALID'))
    pairs,_=s.extract_pairs(rows,coords)
    assert all(p is not None for p in pairs.values())
    rows[1]['validity']='INVALID'
    pairs,status=s.extract_pairs(rows,coords)
    assert pairs[rows[1]['shot_id']] is None and len(pairs)==42
    assert len(status)==42


def test_panel_balancing_material_rules_and_primary_selection():
    observed,predictions=fixture()
    result,_=s.evaluate(observed,predictions)
    assert result['disposition']=='TWO_ASSAY_RATE_ADAPTATION_EARNED_ON_DECLARED_SUPPORT'
    for panel in s.PANELS:
        p=result['restricted_primary']['panels'][panel]
        assert p['balanced_metrics'][s.PRIMARY]['R_pp']==pytest.approx(.2)
        assert p['axes']=={'AXIS_A':'PASS','AXIS_B':'PASS','AXIS_C':'PASS','AXIS_D':'FAIL','AXIS_E':'PASS'}
    assert result['primary_candidate']=='TWO_ASSAY_MASS'


def test_infeasible_arm_cannot_gain_by_removing_failed_windows():
    o,p=fixture(); p[s.PRIMARY][0].update(numerical_qualified=False,predicted_solute_kg=None,prediction_status='SCIENTIFICALLY_INCOMPATIBLE')
    result,shots=s.evaluate(o,p)
    first=shots['restricted'][s.PRIMARY][0]
    assert first['metrics'] is None and first['intended_windows']==4
    assert result['restricted_primary']['axes']['AXIS_A']!='PASS'
    assert result['restricted_primary']['axes']['AXIS_B']!='PASS'
    p[s.PRIMARY].pop(0)
    with pytest.raises(ValueError,match='IDENTICAL_FROZEN'):
        s.evaluate(o,p)


def test_definite_failure_survives_missing_condition_with_original_denominator():
    o,p=fixture()
    for arm in s.ARMS:
        for i,r in enumerate(p[arm]):
            if r['shot'] in ('FIT-E01-R1','FIT-E01-R2'):
                r.update(predicted_solute_kg=.0005+.005*2/100,predicted_tds_percent=12.)
            if r['shot']=='FIT-E01-R3' and r['fraction']==10:
                r.update(numerical_qualified=False,predicted_solute_kg=None,prediction_status='UNAVAILABLE_MEASURED_MASS_PREFIX')
                o[i].update(primary_mask=False,support_reason='UNAVAILABLE_MEASURED_MASS_PREFIX')
                r.update(primary_mask=False,support_reason='UNAVAILABLE_MEASURED_MASS_PREFIX')
    result,_=s.evaluate(o,p)
    cond=result['full_intended_suffix']['panels']['FIT-transfer']['conditions'][s.PRIMARY][0]
    assert cond['complete_shots']==2 and cond['intended_shots']==3
    assert cond['complete_shot_lower_bounds_original_denominator']['R_pp']==pytest.approx(4/3)
    assert cond['adequacy_status']=='FAIL'
    assert result['full_intended_suffix']['axes']['AXIS_A']=='FAIL'
    assert result['full_intended_suffix']['axes']['AXIS_C']=='FAIL'


def test_partial_signed_bias_never_used_as_full_shot_abs_bias_bound():
    o,p=fixture()
    for arm in s.ARMS:
        for r in p[arm]:
            if r['condition']=='FIT-C01':
                r.update(predicted_solute_kg=.005,predicted_tds_percent=100.)
                if r['fraction']==10:r.update(numerical_qualified=False,predicted_solute_kg=None,prediction_status='UNAVAILABLE')
    result,_=s.evaluate(o,p)
    c=result['full_intended_suffix']['panels']['FIT-transfer']['conditions'][s.PRIMARY][0]
    assert c['complete_shot_lower_bounds_original_denominator']['abs_B_pp']==0
    assert c['adequacy_status']!='FAIL'


def test_restricted_pass_never_full_suffix_pass():
    o,p=fixture()
    o[-1].update(primary_mask=False,support_reason='OUTSIDE_FROZEN_MASS_DOMAIN')
    for arm in s.ARMS:
        p[arm][-1].update(primary_mask=False,support_reason='OUTSIDE_FROZEN_MASS_DOMAIN',
            numerical_qualified=False,predicted_solute_kg=None,prediction_status='OUTSIDE_FROZEN_MASS_DOMAIN')
    result,_=s.evaluate(o,p)
    assert result['restricted_primary']['axes']['AXIS_A']=='PASS'
    assert result['full_intended_suffix']['axes']['AXIS_A']!='PASS'
    assert result['full_intended_suffix']['axes']['AXIS_C']!='PASS'


def test_numerical_allowance_is_carried_into_gate():
    o,p=fixture()
    for r in p[s.PRIMARY]:
        r.update(predicted_solute_kg=.000525,numerical_allowance_kg=1e-10,predicted_tds_percent=10.5)
    result,_=s.evaluate(o,p)
    assert result['restricted_primary']['axes']['AXIS_A']=='NUMERICALLY_UNRESOLVED'


def test_exclusive_score_attempt_guard(tmp_path):
    (tmp_path/'score_receipt.json').write_text('{}')
    with pytest.raises(ValueError,match='PRESERVED_FAILED_ATTEMPT'):
        s.verify_before_score(tmp_path,tmp_path/'missing_review.json')


def test_scorer_rejects_anchor_and_unequal_mask():
    o,p=fixture();o[0]['fraction']=2
    with pytest.raises(ValueError,match='EXACT_SIX_ARM'):
        s.evaluate(o,p)
    o,p=fixture();p[s.PRIMARY][0]['primary_mask']=False
    with pytest.raises(ValueError,match='IDENTICAL_FROZEN'):
        s.evaluate(o,p)


def test_pair_projection_has_no_source_condition_lookup():
    coords=coordinates(); rows=assay_rows(coords)
    pairs,_=s.extract_pairs(rows,coords)
    one=pairs[s.SHOTS[0]]
    assert set(asdict(one))=={'first','second'}
    assert not {'condition','temperature_K','source_flow_setting_code'} & set(asdict(one.first))
    # Changing IDs does not change fitted coefficients.
    other=md.ObservationPair(*(replace(x,shot_id='arbitrary') for x in (one.first,one.second)))
    b=s.load_bases()['MASS']
    assert md.FittedState(b,one).diagnostics==md.FittedState(b,other).diagnostics

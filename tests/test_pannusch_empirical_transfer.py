"""Offline synthetic tests for the explicit transfer cohort and once-only scorer."""
from copy import deepcopy
from types import SimpleNamespace
import json

import numpy as np
import pytest

from puckworks.analysis import pannusch_empirical_transfer as s
from puckworks.analysis import anchored_mass_delivery as md
from puckworks.analysis import mass_delivery as kernel


def bases():
    return {name: md.FrozenBase.from_model(kernel.Model('synthetic/'+name,
        'MASS' if name == 'MASS' else 'BOUNDARY_AWARE_EMPIRICAL',
        (.2, 50., 1.) if name == 'MASS' else (.2, .1, .12, .04), (0., .06),
        {'kind': 'SYNTHETIC'}, 'synthetic', knots_kg=() if name == 'MASS' else (0., .02, .04, .06)))
        for name in s.BASE_PATHS}


def coordinates():
    result = []
    for shot in s.SHOTS:
        for f in (1,)+s.SUFFIX:
            result.append(dict(campaign=s.CAMPAIGN, condition=shot.split('-R')[0].replace('-E', '-C'),
                shot=shot, fraction=f, b0=(f-1)*.005, b1=f*.005, mass_kg=.005,
                coordinate_status='QUALIFIED', source_id='P24-MAT-FIT'))
    return result


def assay_rows(coords):
    return [dict(campaign_id=s.CAMPAIGN, condition_id=c['condition'], shot_id=c['shot'],
        source_experiment_id=str(int(c['shot'][5:7])), physical_replicate_id=c['shot'][-1],
        fraction_id=str(c['fraction']), analyte='TDS', concentration_value='10',
        concentration_unit='percent', fraction_basis='MEASURED_MASS_G', fraction_liquid_g_or_ml='5',
        analyte_mass_mg='500', validity='VALID', exclusion_reason='', source_id='P24-MAT-FIT') for c in coords]


def synthetic_scores():
    obs = [dict(c, eligible=True, q=.1, solute_kg=c['mass_kg']*.1,
        source_rounding_allowance_kg=0., source_reason='') for c in coordinates() if c['fraction'] in s.SUFFIX]
    predictions = {a: [dict({k: o[k] for k in s.QUERY_KEYS}, in_domain=True, numerical_qualified=True,
        predicted_solute_kg=o['solute_kg']+o['mass_kg']*(.2 if a == s.PRIMARY else .6)/100,
        integration_allowance_kg=0., unsupported_reason='') for o in obs] for a in s.ARMS}
    return obs, predictions


def test_exact_cohort_and_roles_disjoint_from_calibration_and_march():
    assert len(s.SHOTS) == 30 and len(s.CONDITIONS) == 10
    assert set(s.GRINDS) == {1, 2, 3, 4, 5, 6, 7, 8, 12, 13}
    assert {i for i, g in s.GRINDS.items() if g == 1.4} == {1, 2, 5, 6, 12}
    assert not set(s.SHOTS) & set(s.CALIBRATION)
    assert s.role('FIT-E01-R1', 1) == 'ANCHOR_INPUT_ONLY'
    assert s.role('FIT-E01-R1', 2) == 'SCORING_ONLY'
    assert s.role('FIT-E01-R1', 4) == 'COORDINATE_PREFIX_ONLY'
    assert s.role('FIT-E09-R1', 2) == 'FROZEN_CALIBRATION_EXCLUDED'
    assert s.role('PRED-E01-R1', 2) == 'EXCLUDED'
    for b in s.load_bases().values():
        assert set(s.read_model(b)['fit_identity']['shots']) == set(s.CALIBRATION)


def test_qualified_register_checks_identities_and_source_fit_is_not_training():
    rr, dd, dates = [], {}, {}
    for i, g in s.GRINDS.items():
        t, f = s.RECIPES[i]
        dd[i] = dict(grind=g, dose=20, temp0=t, temp1=t, flow0=f, flow1=f)
        for j in (1, 2, 3):
            dates[i, j] = 'SYNTHETIC'
            rr.append(dict(campaign_id=s.CAMPAIGN, shot_id=f'FIT-E{i:02d}-R{j}', condition_id=f'FIT-C{i:02d}',
                source_experiment_id=str(i), physical_replicate_id=str(j), source_role='SOURCE_FIT_DATA',
                grind_setting=str(g), dose_g='20', machine='DE1', source_id='P24-MAT-FIT;P24-DOE-FIT',
                nominal_temperature_program_id=f'CONST-{t:g}C', nominal_flow_program_id=f'CONST-{f:g}ML_S',
                collection_date='SYNTHETIC'))
    assign = [dict(campaign_id=s.CAMPAIGN, source_experiment_id=str(i), grind_setting=str(g)) for i, g in s.GRINDS.items()]
    assert len(s.qualified_register(rr, assign, dd, dates)) == 30
    assert all(s.role(r['shot_id'], 2) == 'SCORING_ONLY' for r in rr)
    rr[0]['shot_id'] = rr[1]['shot_id']
    with pytest.raises(ValueError, match='EXACT_SHOT'):
        s.qualified_register(rr, assign, dd, dates)


def test_full_prefix_unassayed_gaps_and_no_source_imputation(monkeypatch):
    masses = np.arange(1., 11.)
    run = SimpleNamespace(mE=masses, mE_cum=np.cumsum(masses), tE=np.arange(1., 11.))
    class Sheet:
        def cell(self, row, col):
            if col == 1:
                return SimpleNamespace(value=1)
            f = col-3
            return SimpleNamespace(value=None if f == 5 else 10. if row == 3 else 10.+masses[f])
    monkeypatch.setattr(s.source, 'workbook', lambda p: {'SampleWeights': Sheet()})
    cc = s.measured_coordinates('unused', 1, run)
    assert cc[3]['fraction'] == 5 and cc[3]['b0'] == pytest.approx(.010)
    assert cc[3]['b1'] == pytest.approx(.015)  # includes unassayed vial 4
    assert cc[4]['fraction'] == 7 and cc[4]['b0'] is None
    assert cc[4]['mass_kg'] == .007  # measured assay mass retained, prefix unknown
    assert cc[4]['coordinate_status'] == 'UNAVAILABLE_MEASURED_MASS_PREFIX'
    assert cc[0]['coordinate_status'] == 'QUALIFIED'


def test_later_chemistry_mutation_cannot_change_anchors_or_predictions():
    cc = coordinates(); rows = assay_rows(cc)
    aa, _ = s.extract_anchors(rows, cc)
    p1 = s.predict_bundle(bases(), aa, s.project_queries(cc))
    for row in rows:
        if row['fraction_id'] != '1':
            row['concentration_value'] = 'THIS MUST NEVER BE PARSED'
            row['analyte_mass_mg'] = 'ALSO FORBIDDEN'
    ab, _ = s.extract_anchors(rows, cc)
    assert aa == ab
    assert s.predict_bundle(bases(), ab, s.project_queries(cc)) == p1
    assert set(p1[0]) == set(s.ARMS) and sum(map(len, p1[0].values())) == 750
    assert all([(p['shot'], p['fraction']) for p in pp] == [(q['shot'], q['fraction']) for q in s.project_queries(cc)] for pp in p1[0].values())
    assert len(p1[1]) == 60


def test_prediction_rejects_later_chemistry_even_extra_keys():
    q = s.project_queries(coordinates())[:1]
    q[0]['TDS'] = 2.
    with pytest.raises(ValueError, match='COORDINATE_ONLY'):
        s.predict_bundle(bases(), {}, q)


def test_missing_anchors_source_invalid_assays_and_hplc_exclusion():
    cc = coordinates(); rows = assay_rows(cc)
    rows[0]['validity'] = 'INVALID'; rows[0]['exclusion_reason'] = 'SYNTHETIC'
    aa, support = s.extract_anchors(rows, cc)
    pp, _, _ = s.predict_bundle(bases(), aa, s.project_queries(cc))
    assert support[0]['reason'].startswith('SOURCE_INVALID_TDS')
    for arm in ('ANCHORED_EMPIRICAL', 'ANCHORED_MASS', 'ANCHOR_PERSISTENCE'):
        assert pp[arm][0]['unsupported_reason'] == 'ANCHOR_UNAVAILABLE'
    assert pp['UNANCHORED_EMPIRICAL'][0]['numerical_qualified']
    rows[1]['exclusion_reason'] = 'ALL_HPLC_ANALYTES_INVALID_SPILL'
    assert s.assay_projection(rows, [cc[1]], s.SUFFIX)[0]['eligible']
    rows[1]['validity'] = 'INVALID'
    assert not s.assay_projection(rows, [cc[1]], s.SUFFIX)[0]['eligible']
    assert s.assay_projection([], [cc[1]], s.SUFFIX)[0]['source_reason'] == 'MISSING_TDS_ASSAY'


def test_out_of_domain_is_not_clipped_and_unknown_prefix_keeps_mass():
    cc = coordinates(); aa, _ = s.extract_anchors(assay_rows(cc), cc)
    qq = s.project_queries(cc)
    qq[-1]['b1'] = .061
    qq[-2].update(b0=None, b1=None, coordinate_status='UNAVAILABLE_MEASURED_MASS_PREFIX')
    pp, _, _ = s.predict_bundle(bases(), aa, qq)
    for arm in s.ARMS:
        assert pp[arm][-1]['predicted_solute_kg'] is None
        assert pp[arm][-1]['b1'] == .061
        assert pp[arm][-1]['unsupported_reason'] == 'OUTSIDE_FROZEN_MASS_DOMAIN'
        assert pp[arm][-2]['unsupported_reason'] == 'UNAVAILABLE_MEASURED_MASS_PREFIX'


def test_immutable_frozen_bytes_strict_state_and_zero_optimizer_calls():
    bb = bases(); before = {k: b.artifact_json for k, b in bb.items()}
    cc = coordinates(); aa, _ = s.extract_anchors(assay_rows(cc), cc)
    with s.no_optimization() as count:
        pp, states, _ = s.predict_bundle(bb, aa, s.project_queries(cc))
    assert count == {'optimizer_calls': 0, 'new_base_curve_fits': 0}
    assert before == {k: b.artifact_json for k, b in bb.items()}
    for state in states.values():
        assert md.AnchoredState.from_dict(state).to_dict() == state
    state = deepcopy(next(iter(states.values())))
    state['alpha'] *= 1.01
    with pytest.raises(ValueError):
        md.AnchoredState.from_dict(state)
    with pytest.raises(ValueError, match='DUPLICATE_JSON'):
        md.strict_json('{"alpha":1,"alpha":2}')
    with s.no_optimization() as count:
        with pytest.raises(RuntimeError, match='OPTIMIZATION_FORBIDDEN'):
            s.source.least_squares(None, None)
    assert count['optimizer_calls'] == 1
    assert len(pp[s.PRIMARY]) == 150


def test_independent_metric_arithmetic_mass_weights_condition_balance_and_sign():
    oo, pp = synthetic_scores()
    for o, p in zip(oo, pp[s.PRIMARY]):
        error = int(o['condition'][-2:])/100 + int(o['shot'][-1])/100
        o['mass_kg'] = o['fraction']*.001
        o['solute_kg'] = o['mass_kg']*.1
        p['predicted_solute_kg'] = o['solute_kg']+o['mass_kg']*error/100
    shots = s.shot_metrics(oo, pp[s.PRIMARY])
    conditions = s.source.condition_metrics(shots)
    value = s.source.aggregate(conditions, s.CONDITIONS)['metrics']
    expected = np.mean([i/100+.02 for i in s.GRINDS])
    assert value['R_pp'] == pytest.approx(expected)
    assert value['abs_B_pp'] == pytest.approx(expected)
    assert value['B_pp'] == pytest.approx(expected)
    # Independent unequal-weight calculation within one shot, with opposite errors.
    for i, (o, p) in enumerate(zip(oo[:5], pp[s.PRIMARY][:5])):
        p['predicted_solute_kg'] = o['solute_kg']+o['mass_kg']*(i-2)/100
    value = s.shot_metrics(oo, pp[s.PRIMARY])[0]['metrics']
    weights = np.array(s.SUFFIX, float)
    errors = np.arange(5)-2
    assert value['R_pp'] == pytest.approx(np.sqrt(np.sum(weights*errors**2)/weights.sum()))
    assert value['B_pp'] == pytest.approx(np.sum(weights*errors)/weights.sum())


def metric(r, b=.1, allowance=0.):
    return dict(R_pp=r, B_pp=b, abs_B_pp=abs(b), R_allowance_pp=allowance, B_allowance_pp=allowance)


def condition_fixture(wins):
    return {a: [dict(condition=c, metrics=metric(.2 if a == s.PRIMARY or i >= wins else 1.), adequacy='PASS')
            for i, c in enumerate(s.CONDITIONS)] for a in (s.PRIMARY, 'ANCHORED_MASS')}


@pytest.mark.parametrize('wins,expected', [(7, 'FAIL'), (8, 'PASS'), (10, 'PASS')])
def test_eight_of_ten_win_rule(wins, expected):
    result = s.compare(condition_fixture(wins), 'ANCHORED_MASS')
    assert result['material_gain_gates']['condition_wins'] == expected
    assert result['conditions_improved_definite'] == wins


def test_bias_numerical_thresholds_and_fail_preservation():
    cc = condition_fixture(10)
    cc[s.PRIMARY][0]['metrics']['abs_B_pp'] = 2.
    assert s.compare(cc, 'ANCHORED_MASS')['material_gain_gates']['bias'] == 'FAIL'
    assert s.source.threshold(1., 1e-8, 1.) == 'NUMERICALLY_UNRESOLVED'
    assert s.conjunction(['FAIL', 'UNSUPPORTED']) == 'FAIL'
    assert s.conjunction(['PASS', 'NUMERICALLY_UNRESOLVED']) == 'NUMERICALLY_UNRESOLVED'
    cc = condition_fixture(0); cc[s.PRIMARY][0]['metrics'] = None
    assert s.compare(cc, 'ANCHORED_MASS')['material_gain'] == 'FAIL'


def test_all_axes_and_denominator_preservation():
    oo, pp = synthetic_scores(); result, _ = s.evaluate(oo, pp)
    assert result['axes'] == dict.fromkeys('ABCDE', 'PASS')
    assert result['groups']['all_ten'][s.PRIMARY]['coverage']['intended']['count'] == 150
    assert result['groups']['common_89C_code2'][s.PRIMARY]['coverage']['intended']['count'] == 30
    oo[0].update(eligible=False, source_reason='MISSING_TDS_CHEMISTRY')
    pp[s.PRIMARY][20].update(in_domain=False, numerical_qualified=False, predicted_solute_kg=None, unsupported_reason='OUTSIDE_FROZEN_MASS_DOMAIN')
    result, _ = s.evaluate(oo, pp)
    assert result['axes']['A'] != 'PASS'
    assert result['groups']['all_ten'][s.PRIMARY]['coverage']['intended']['count'] == 150
    assert result['groups']['all_ten'][s.PRIMARY]['coverage']['numerically_qualified']['count'] == 148
    assert result['groups']['all_ten'][s.PRIMARY]['metrics'] is None
    assert result['groups']['all_ten'][s.PRIMARY]['supported_subset_diagnostic']['metrics']
    # A complete failing condition is not erased by another unsupported condition.
    for o, p in zip(oo, pp[s.PRIMARY]):
        if o['condition'] == s.CONDITIONS[-1]:
            p['predicted_solute_kg'] = o['solute_kg'] + .02*o['mass_kg']
    result, _ = s.evaluate(oo, pp)
    assert result['axes']['A'] == result['axes']['D'] == 'FAIL'


def test_scorer_rejects_anchor_and_mismatched_arm_suffix():
    oo, pp = synthetic_scores(); oo[0]['fraction'] = 1
    with pytest.raises(ValueError, match='EXACT_SUFFIX_NO_ANCHOR'):
        s.evaluate(oo, pp)
    oo, pp = synthetic_scores(); pp[s.PRIMARY].pop()
    with pytest.raises(ValueError, match='IDENTICAL_FROZEN_SUFFIX'):
        s.evaluate(oo, pp)


def freeze_fixture(tmp_path, monkeypatch):
    root = tmp_path/'code'; root.mkdir(); (root/'bound').write_text('code')
    out = tmp_path/'run'; out.mkdir()
    source_file = tmp_path/'source'; source_file.write_text('original')
    monkeypatch.setattr(s, 'ROOT', root); monkeypatch.setattr(s.receipt, 'ROOT', root)
    monkeypatch.setattr(s, 'FREEZE_PATHS', ('bound',)); monkeypatch.setattr(s, 'BUNDLE_FILES', ('source.json',))
    monkeypatch.setattr(s.source, 'verify_registers', lambda r: None)
    monkeypatch.setattr(s.source, 'source_paths', lambda: {'S': source_file})
    s.write_json(out/'source.json', {'source_files': {'S': s.digest(source_file)}})
    frozen = {'task': s.TASK, 'producer_commit': 'c'*40, 'producer_tree': 'd'*40,
        'code_and_protocol': {'bound': s.digest(root/'bound')}, 'artifacts': {'source.json': s.digest(out/'source.json')}}
    s.write_json(out/'freeze.json', frozen)
    review = tmp_path/'review.json'
    approved = {'task': s.TASK, 'status': 'APPROVED', 'independent': True, 'reviewer': 'SYNTHETIC_TEST_ONLY',
        'unresolved_blocking_findings': [], 'freeze_sha256': s.digest(out/'freeze.json'),
        'reviewed_head': frozen['producer_commit'], 'reviewed_tree': frozen['producer_tree']}
    s.write_json(review, approved)
    return root, out, review, approved


def test_freeze_drift_stale_review_duplicate_score_and_overwrite(tmp_path, monkeypatch):
    root, out, review, approval = freeze_fixture(tmp_path, monkeypatch)
    assert s.verify_before_score(out, review)['task'] == s.TASK
    (root/'bound').write_text('drift')
    with pytest.raises(ValueError, match='drift'):
        s.verify_before_score(out, review)
    (root/'bound').write_text('code')
    approval['freeze_sha256'] = 'wrong'; review.write_text(json.dumps(approval))
    with pytest.raises(ValueError, match='approval'):
        s.verify_before_score(out, review)
    (out/'score_receipt.json').write_text('{}')
    with pytest.raises(ValueError, match='DUPLICATE_SCORE'):
        s.verify_before_score(out, review)
    with pytest.raises(ValueError, match='REFUSES_OVERWRITE'):
        s.freeze(out)


def test_missing_numerics_cannot_pass_and_numerical_allowance_propagates():
    oo, pp = synthetic_scores()
    for p in pp[s.PRIMARY]:
        p['integration_allowance_kg'] = .004*p['b1']  # deliberately large synthetic allowance
    shot = s.shot_metrics(oo, pp[s.PRIMARY])[0]
    assert shot['metrics']['R_allowance_pp'] > 0
    pp[s.PRIMARY][0]['numerical_qualified'] = False
    result, _ = s.evaluate(oo, pp)
    assert result['axes']['A'] != 'PASS'

"""Synthetic verification only; no experimental rows enter these tests."""
import copy

import pytest

from puckworks.analysis import pannusch_conditional_5cqa_delivery as p


def synthetic_row(campaign='FIT_2021_12'):
    label = 'FIT' if campaign == 'FIT_2021_12' else 'PRED'
    coordinate = dict(campaign=campaign, condition=label+'-C01', shot=label+'-E01-R1',
                      fraction=3, b0=.01, b1=.015, mass_kg=.005, coordinate_status='QUALIFIED')
    row = dict(campaign_id=campaign, shot_id=coordinate['shot'], fraction_id='3',
               analyte='5CQA', concentration_unit='mg/g', validity='VALID',
               source_id='SYNTHETIC', concentration_value='0.5', measured_concentration='0.5')
    return coordinate, row


def test_five_cqa_source_identity_and_units():
    c, r = synthetic_row()
    value, = p.target_slots([c], [r], campaign=c['campaign'], include_values=True)
    assert value['q'] == .0005
    assert value['analyte'] == '5CQA'
    assert value['source_field'] == 'ExperimentalData(1).run(1).cAlcaloids(3,3)'
    assert value['shot'] == c['shot'] and value['fraction'] == 3
    bad = dict(r, concentration_unit='mg/L')
    with pytest.raises(ValueError, match='UNIT'):
        p.target_slots([c], [bad], campaign=c['campaign'], include_values=True)
    caffeine = dict(r, analyte='caffeine')
    absent, = p.target_slots([c], [caffeine], campaign=c['campaign'])
    assert not absent['analyte_eligible']


def test_projection_preserves_five_cqa_exclusions_without_filling():
    c, r = synthetic_row()
    bad = dict(r, validity='INVALID', exclusion_reason='SYNTHETIC_SPILL')
    projected, = p.target_slots([c], [bad], campaign=c['campaign'], include_values=True)
    assert projected['q'] is None and projected['source_reason'] == 'SYNTHETIC_SPILL'
    with pytest.raises(ValueError, match='DUPLICATE'):
        p.target_slots([c], [r, r], campaign=c['campaign'])
    with pytest.raises(ValueError):
        p.target_slots([c], [dict(r, concentration_value='nan')], campaign=c['campaign'])


def test_pred_projection_is_coordinate_and_validity_only():
    c, r = synthetic_row('PREDICTION_2022_03')
    before = copy.deepcopy(r)
    projected, = p.target_slots([c], [r], campaign=c['campaign'])
    assert 'q' not in projected and 'measured_concentration' not in projected
    assert r == before
    with pytest.raises(ValueError, match='SINGLE_APPROVED'):
        p.target_slots([c], [r], campaign=c['campaign'], include_values=True)


def test_early_projection_reads_only_original_vial_mass():
    c, _ = synthetic_row()
    first = dict(c, fraction=1, b0=0., b1=.004, mass_kg=.004, TDS='forbidden')
    second = dict(c, fraction=2, b0=.004, b1=.01, mass_kg=.006, five_cqa='forbidden')
    assert p.mass_projection([first, second]) == {c['shot']: [.004, .006]}
    with pytest.raises(ValueError, match='QUALIFIED'):
        p.mass_projection([first, dict(second, coordinate_status='UNAVAILABLE')])


def test_inherited_anchor_rule_remains_explicit_and_bounded():
    import numpy as np
    state = type('SyntheticAnchor', (), {'b_anchor': .01})()
    a = np.nextafter(.01, 0.)
    start, allowance = p.source_geometry.source_query_start({'fraction': 3, 'b0': a}, state)
    assert start == .01 and allowance == 2*abs(.01-a)
    with pytest.raises(ValueError, match='ANCHOR_MISMATCH'):
        p.source_geometry.source_query_start({'fraction': 3, 'b0': .009}, state)
    assert p.source_geometry.source_query_start({'fraction': 5, 'b0': a}, state) == (a, 0.)


def synthetic_panel(errors=(.1, -.1, .1), allowance=1e-12):
    observations, predictions = [], []
    for rep, error in enumerate(errors, 1):
        for fraction in p.SUFFIX:
            shot = f'PRED-E01-R{rep}'
            observations.append(dict(shot=shot, condition='PRED-C01', fraction=fraction,
                                     analyte_eligible=True, q=.001, mass_kg=.005))
            predictions.append(dict(shot=shot, condition='PRED-C01', fraction=fraction,
                                    supported=True, numerical_qualified=True, five_cqa_mg_g=1+error,
                                    five_cqa_kg=.005*(1+error)/1000, allowance_kg=allowance))
    return observations, predictions


def test_five_cqa_original_denominators():
    rows, predictions = synthetic_panel()
    result, _ = p.panel_metrics(rows, predictions, ['PRED-C01'])
    assert result['full_scope_metrics']['absB_mg_g'] == pytest.approx(.1)
    assert result['full_scope_metrics']['B_mg_g'] == pytest.approx(.1/3)
    damaged = copy.deepcopy(predictions); damaged[0]['numerical_qualified'] = False
    result, _ = p.panel_metrics(rows, damaged, ['PRED-C01'])
    assert result['full_scope_metrics'] is None
    assert result['original_shots'] == 3 and result['original_slots'] == 12
    assert result['conditions']['PRED-C01']['complete_shots'] == 2
    with pytest.raises(ValueError, match='THREE_SHOT'):
        p.panel_metrics(rows[:8], predictions[:8], ['PRED-C01'])
    with pytest.raises(ValueError, match='FOUR_FRACTION'):
        p.panel_metrics(rows[1:], predictions[1:], ['PRED-C01'])


def test_five_cqa_numerical_allowance_propagation():
    import numpy as np
    rows, predictions = synthetic_panel()
    rows, predictions = rows[:4], predictions[:4]
    errors = np.asarray([.1, -.2, .3, -.4])
    masses = np.asarray([.001, .002, .003, .004])
    allowances = np.asarray([1e-10, 2e-10, 4e-10, 8e-10])
    for r, pred, error, mass, allowance in zip(rows, predictions, errors, masses, allowances):
        r['mass_kg'] = mass
        pred.update(five_cqa_mg_g=1+error, allowance_kg=allowance)
    result = p.shot_metrics(rows, predictions)
    weights = masses/masses.sum(); concentration_allowances = 1000*allowances/masses
    assert result['R_mg_g'] == pytest.approx(np.sqrt(weights @ errors**2))
    assert result['R_allowance_mg_g'] == pytest.approx(np.sqrt(weights @ concentration_allowances**2))
    assert result['absB_allowance_mg_g'] == pytest.approx(weights @ concentration_allowances)
    assert p.upper(.25, 1e-9, .25) == p.UNRESOLVED
    assert p.upper(.25-2e-9, 1e-9, .25) == 'PASS'
    assert p.upper(.25+2e-9, 1e-9, .25) == 'FAIL'


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


def test_scientific_negative_is_a_resolved_disposition_and_overlap_is_not():
    assert p.disposition({'E0': 'FAIL', 'D0': 'FAIL'}, 'FAIL', True) == (
        'TESTED_FIVE_CQA_FAMILIES_INADEQUATE', None)
    assert p.disposition({'E0': 'PASS', 'D0': 'FAIL'}, 'FAIL', True)[0] == 'SIMPLE_FIVE_CQA_EXPONENTIAL_ADEQUATE'
    assert p.disposition({'E0': 'FAIL', 'D0': 'PASS'}, 'PASS', True)[0] == 'FIVE_CQA_CONDITIONED_MODEL_EARNED'
    assert p.disposition({'E0': 'FAIL', 'D0': 'PASS'}, 'FAIL', True)[0] == 'FIVE_CQA_D0_ADEQUATE_INCREMENT_NOT_ESTABLISHED'
    assert p.disposition({'E0': 'FAIL', 'D0': 'PASS'}, 'UNRESOLVED', True)[0] == 'NOT_ADJUDICATED'
    assert p.disposition({'E0': 'FAIL', 'D0': 'FAIL'}, 'FAIL', False)[0] == 'NOT_ADJUDICATED'


def test_mass_gain_requires_all_fixed_conditions():
    def panel(error):
        rows, preds = synthetic_panel((error, error, error), allowance=0.)
        one, _ = p.panel_metrics(rows, preds, ['PRED-C01'])
        condition = one['conditions']['PRED-C01']
        one['conditions'] = {f'PRED-C{i:02d}': copy.deepcopy(condition) for i in (1, 2, 5, 6)}
        return one
    gain = p.material_gain(panel(.1), panel(.2))
    assert gain['status'] == 'PASS' and gain['definite_condition_wins'] == 4
    assert p.material_gain(panel(.17), panel(.2))['components']['absolute_gain'] == 'FAIL'
    bad = panel(.1); bad['conditions']['PRED-C01']['full_scope_metrics']['R_mg_g'] = .3
    bad['conditions']['PRED-C02']['full_scope_metrics']['R_mg_g'] = .3
    assert p.material_gain(bad, panel(.2))['components']['condition_wins'] == 'FAIL'


def test_cli_is_fail_closed_before_creating_evidence(tmp_path):
    import subprocess
    import sys
    module = 'puckworks.analysis.pannusch_conditional_5cqa_delivery'
    for args in [('score',), ('prepare', '--review', 'unused'), ('prepare', '--parent-evidence', 'unused'),
                 ('prepare', '--ou', str(tmp_path))]:
        result = subprocess.run([sys.executable, '-m', module, *args, '--out', str(tmp_path/'not-created')],
                                capture_output=True, text=True)
        assert result.returncode != 0 and not (tmp_path/'not-created').exists()


def synthetic_complete_source():
    coords, rows, groups = [], [], {}
    for label, count, campaign in [('FIT', 15, 'FIT_2021_12'), ('PRED', 8, 'PREDICTION_2022_03')]:
        for e in range(1, count+1):
            condition = f'{label}-C{e:02d}'
            if label == 'FIT': groups[condition] = condition
            for rep in (1, 2, 3):
                shot = f'{label}-E{e:02d}-R{rep}'
                for fraction in p.ASSAY_FRACTIONS:
                    coords.append(dict(campaign=campaign, condition=condition, shot=shot, fraction=fraction,
                                       b0=(fraction-1)*.004, b1=fraction*.004, mass_kg=.004,
                                       coordinate_status='QUALIFIED'))
                    if fraction in p.SUFFIX:
                        rows.append(dict(campaign_id=campaign, shot_id=shot, fraction_id=str(fraction),
                                         analyte='5CQA', concentration_unit='mg/g', validity='VALID',
                                         source_id='SYNTHETIC', concentration_value='0.5', measured_concentration='0.5'))
    return coords, rows, groups


def test_complete_projection_keeps_all_slots_and_stops_on_primary_loss():
    coords, rows, groups = synthetic_complete_source()
    projection = p.build_projections(coords, rows, groups)
    assert len(projection['fit_slots']) == 180 and len(projection['queries']) == 96
    assert all(len(s['early_values']) == 2 for s in projection['training'])
    assert all('q' not in q for q in projection['queries'])
    damaged = copy.deepcopy(rows)
    next(r for r in damaged if r['shot_id'] == 'PRED-E01-R1')['validity'] = 'INVALID'
    with pytest.raises(ValueError, match='FORTY_EIGHT'):
        p.build_projections(coords, damaged, groups)
    damaged = copy.deepcopy(coords)
    for c in damaged:
        if c['shot'] in ('FIT-E01-R1', 'FIT-E01-R2') and c['fraction'] in (3, 5):
            c['coordinate_status'] = 'UNAVAILABLE_MEASURED_MASS_PREFIX'
    with pytest.raises(ValueError, match='TWO_PHYSICAL_SHOTS'):
        p.build_projections(damaged, rows, groups)


def test_numerical_gain_overlap_and_bias_deterioration_are_not_passes():
    rows, preds = synthetic_panel((.1, .1, .1), allowance=0.)
    candidate, _ = p.panel_metrics(rows, preds, ['PRED-C01'])
    candidate['conditions'] = {str(i): copy.deepcopy(candidate['conditions']['PRED-C01']) for i in range(4)}
    control = copy.deepcopy(candidate)
    control['full_scope_metrics']['R_mg_g'] = .15
    candidate['full_scope_metrics']['R_allowance_mg_g'] = 1e-8
    assert p.material_gain(candidate, control)['components']['absolute_gain'] == p.UNRESOLVED
    candidate['full_scope_metrics']['absB_mg_g'] = .14
    control['full_scope_metrics']['absB_mg_g'] = .1
    assert p.material_gain(candidate, control)['components']['abs_bias_deterioration'] == 'FAIL'


def test_pred_chemistry_poisoning_cannot_change_training_or_predictions(tmp_path):
    from puckworks.analysis import conditional_5cqa_training as train
    coords, rows, groups = synthetic_complete_source()
    first = p.build_projections(coords, rows, groups)
    poisoned = copy.deepcopy(rows)
    for row in poisoned:
        if row['campaign_id']=='PREDICTION_2022_03':
            row['measured_concentration']='999.0'
    second = p.build_projections(coords, poisoned, groups)
    assert first == second
    fitted = []
    for name, projection in [('before', first), ('poisoned', second)]:
        budget = train.Budget(tmp_path/name, synthetic=True)
        models = {}
        try:
            for arm in p.ARMS:
                models[arm], _ = train.fit(
                    train.project_arm(projection['training'], arm),
                    None if arm == 'E0' else .01, budget, arm+'.synthetic-poison',
                    'SYNTHETIC', 'SYNTHETIC_FIRST_PARTY', scope='SYNTHETIC')
        finally:
            budget.worker_lock.close()
        fitted.append(models)
    assert {a:m.sha256 for a,m in fitted[0].items()} == {a:m.sha256 for a,m in fitted[1].items()}
    assert p.predict_records(fitted[0], first['early_inputs'], first['queries']) == p.predict_records(fitted[1], second['early_inputs'], second['queries'])
    for arm in p.ARMS:
        lam = None if arm=='E0' else .01
        a=train.FitProblem(train.project_arm(first['training'],arm),lam,scope='SYNTHETIC')
        b=train.FitProblem(train.project_arm(second['training'],arm),lam,scope='SYNTHETIC')
        assert p.canonical([x.tolist() for x in a.starts])==p.canonical([x.tolist() for x in b.starts])


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
    for name in ('score','evaluate','original_rows','predict_records'):
        monkeypatch.setattr(p,name,forbidden)
    monkeypatch.setattr(p.source_geometry,'all_rows',forbidden)
    assert p.report(tmp_path)==result

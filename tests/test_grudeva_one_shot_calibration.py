"""Synthetic role isolation, one-shot fits, fixed denominators and saved reports."""
from copy import deepcopy
from dataclasses import asdict, replace

import numpy as np
import pytest

from puckworks.analysis import conditional_tail_delivery as md
from puckworks.analysis import source_calibrated_tail_delivery as api
from puckworks.analysis import grudeva_one_shot_calibration as task
from puckworks.analysis import grudeva_one_shot_scoring as scoring


def fixture(n=3, chemistry_shift=None):
    shots = list(range(1, n+1)); models = {a: md.synthetic_model(a) for a in ('C0', 'C2')}
    early, queries, outcomes, f2, artifacts = [], [], [], [], {}
    for i in shots:
        for a, m in models.items():
            values = list(m.means); values[0] += i*.0001
            early.append({'shot': i, 'arm': a, 'input': md.EarlyInput(a, tuple(values), 'SYNTHETIC').to_dict()})
        for k, (a, b) in enumerate(((.02, .025), (.025, .03)), start=15):
            q = {'shot': i, 'vial': k, 'mass_kg': b-a, 'start_kg': a, 'end_kg': b}; queries.append(q)
            observed = .09-i*.005+(chemistry_shift or {}).get(i, 0.)
            outcomes.append({'shot': i, 'vial': k, 'q': observed, 'solute_kg': (b-a)*observed, 'chemistry_status': 'AVAILABLE'})
    inputs = task.old.input_index(early)
    for q in queries:
        state = models['C2'].condition(inputs['C2', q['shot']]); p = asdict(state.predict_intervals([q['start_kg']], [q['end_kg']])[0])
        f2.append(dict(q, status='QUALIFIED', prediction=p, feature_extrapolation=[],
                       integration_start_kg=q['start_kg'], integration_end_kg=q['end_kg'], coordinate_allowance_kg=0.))
    for i in shots:
        obs = tuple(api.Observation(**q, q=o['q']) for q, o in zip(queries, outcomes) if q['shot'] == i)
        for a in ('A0', 'A2'):
            record = api.CalibrationRecord('a'*64, i, inputs['C'+a[1:], i], obs)
            artifacts[f'{i}/{a}'] = api.calibrate_source(models['C'+a[1:]], record).to_dict()
        artifacts[f'{i}/M'] = api.MassCalibration('a'*64, i, 'b'*64, (.1, 0., .01, 1.), .08, (.02, .03), 'QUALIFIED').to_dict()
    cohort = [{'shot': i, 'eligible': i <= n, 'k2': 14 if i <= n else None} for i in range(1, 14)]
    folds = {'calibrators': shots, 'targets': shots, 'pairs': [[j, i] for j in shots for i in shots if j != i],
             'intended_slots_per_arm': n*(n-1)*2, 'unique_suffix_windows': 2*n, 'original_shots': 13}
    binding = {'source': {'files': {'exp13.csv': 'a'*64}}, 'parent_models': {a: m.sha256 for a, m in models.items()},
               'accepted_007_prediction_sha256': 'f'*64}
    return artifacts, early, queries, folds, f2, binding, outcomes, cohort


def matrix(data):
    return task.predict_matrix(*data[:6])


def test_every_calibration_choice_forbidden_diagonal_constant_scalar_and_reference():
    data = fixture(); result = matrix(data)
    assert set(result) == set(task.ARMS)
    for a, rows in result.items():
        assert len(rows) == 12
        assert all(r['shot'] != r['calibrator'] for r in rows)
        if a != 'F2':
            for j in (1, 2, 3):
                assert len({r['calibration_sha256'] for r in rows if r['calibrator'] == j}) == 1
        else:
            for r in rows:
                saved = next(q for q in data[4] if (q['shot'], q['vial']) == (r['shot'], r['vial']))
                assert all(r[k] == v for k, v in saved.items())
    cal = api.OffsetCalibration.from_dict(data[0]['1/A2'])
    with pytest.raises(ValueError, match='FORBIDDEN_DIAGONAL'):
        task.predict_pair(cal, 1, md.EarlyInput.from_dict(data[1][1]['input']), [data[2][0]])
    bad = deepcopy(data); bad[3]['pairs'].pop()
    with pytest.raises(ValueError, match='ALL_OFF_DIAGONAL'):
        matrix(bad)
    bad = deepcopy(data); del bad[0]['1/A0']
    with pytest.raises(ValueError, match='ALL_CALIBRATION_CHOICES'):
        matrix(bad)


def test_fold_local_target_chemistry_exclusion_allows_legitimate_calibration_effect():
    base, changed = fixture(), fixture(chemistry_shift={2: .02})
    a, b = matrix(base), matrix(changed)
    for arm in ('A0', 'A2'):
        for ra, rb in zip(a[arm], b[arm]):
            if ra['shot'] == 2:
                assert ra == rb
        assert any(ra['prediction'] != rb['prediction'] for ra, rb in zip(a[arm], b[arm]) if ra['calibrator'] == 2)
    assert a['F2'] == b['F2']


def test_assays_cannot_cross_coordinate_or_mass_target_interface():
    data = fixture(); bad = deepcopy(data); bad[2][0]['suffix_tds'] = 17.
    with pytest.raises(ValueError, match='STRICT_FIELDS'):
        matrix(bad)
    cal = api.MassCalibration.from_dict(data[0]['1/M'])
    with pytest.raises(ValueError, match='INFORMATION_PRIVILEGE'):
        task.predict_pair(cal, 2, md.EarlyInput.from_dict(data[1][3]['input']), [q for q in data[2] if q['shot'] == 2])


def test_failed_a2_slots_preserved_without_rescue_and_mass_range_flag():
    data = fixture(); bad = api.OffsetCalibration.from_dict(data[0]['1/A2'])
    bad = replace(bad, delta=None, enclosure=None, status='CALIBRATION_RANGE_FAILURE', certificate_json='{}')
    data[0]['1/A2'] = bad.to_dict()
    mass = api.MassCalibration.from_dict(data[0]['1/M'])
    data[0]['1/M'] = replace(mass, calibration_range_kg=(.024, .027)).to_dict()
    result = matrix(data)
    blocked = [r for r in result['A2'] if r['calibrator'] == 1]
    assert len(blocked) == 4 and all(r['prediction'] is None and r['status'] == 'CALIBRATION_RANGE_FAILURE' for r in blocked)
    assert all(r['calibration_mass_extrapolation'] and r['prediction'] is not None for r in result['M'] if r['calibrator'] == 1)
    scored, _ = scoring.evaluate(data[2], data[6], result, data[7], data[3])
    assert scored['status_vector']['coverage'] == scoring.INCOMPLETE
    assert scored['increments']['I_CAL']['status'] == scoring.INCOMPLETE


def test_source_only_fit_objective_calls_starts_and_no_early_assays():
    theta = (.2, 0., .04, 1.)
    starts, ends = [.008, .015, .025, .04], [.015, .025, .04, .06]
    values = task.gc.deliver(api.gram_rows(starts, ends), theta)/1000
    windows = tuple(api.Observation(1, k+1, b-a, a, b, float(y/(b-a))) for k, (a, b, y) in enumerate(zip(starts, ends, values)))
    record = api.CalibrationRecord('a'*64, 1, None, windows)
    cal, attempts = task.fit_mass(record, .08)
    assert cal.status == 'QUALIFIED' and cal.theta[1] == 0.
    assert len(attempts) == 8 and [r['start'] for r in attempts] == [list(s) for s in task.STARTS]
    assert all(0 < r['actual_residual_calls'] <= 2000 for r in attempts)
    selected = [r for r in attempts if r['selected']]; assert len(selected) == 1
    assert selected[0]['objective'] <= 1e-12
    assert selected[0]['objective'] == min(r['objective'] for r in attempts if r['success'])
    assert all(r['numerical_jacobian_calls'] == r['actual_residual_calls']-r['nfev'] for r in attempts if r['success'])
    with pytest.raises(ValueError, match='SUFFIX_ONLY'):
        task.fit_mass(replace(record, early=md.EarlyInput('C0', (.004, .004))), .08)


def test_all_start_failure_and_actual_jacobian_cap_retained(monkeypatch):
    calls = []
    def fake(residual, start, **kwargs):
        for _ in range(2001):
            residual(np.array(start))
        raise AssertionError('cap failed')
    monkeypatch.setattr(task, 'least_squares', fake)
    rec = api.CalibrationRecord('a'*64, 1, None, (api.Observation(1, 1, .01, .01, .02, .1),))
    cal, attempts = task.fit_mass(rec, .08)
    assert cal.status == 'ALL_STARTS_FAILED' and cal.theta is None
    assert len(attempts) == 8 and all(r['actual_residual_calls'] == 2000 for r in attempts)
    assert all(r['last']['theta'][1] == 0. and r['termination'] == 'ACTUAL_RESIDUAL_CALL_CAP' for r in attempts)


def test_scoring_equal_pair_metrics_no_ensemble_and_fixed_denominators():
    data = fixture(); predictions = matrix(data)
    # Set opposite-signed pair biases that would cancel in an ensemble.
    for arm, rows in predictions.items():
        for r in rows:
            o = next(o for o in data[6] if (o['shot'], o['vial']) == (r['shot'], r['vial']))
            error = .6 if r['calibrator'] < r['shot'] else -.6
            r['prediction']['tds_percent'] = 100*o['q']+error
            r['prediction']['solute_kg'] = r['mass_kg']*r['prediction']['tds_percent']/100
    result, details = scoring.evaluate(data[2], data[6], predictions, data[7], data[3])
    assert result['original_shots'] == 13 and result['ordered_pairs'] == 6
    assert result['unique_suffix_windows'] == 6 and result['prediction_slots_per_arm'] == 12
    for a in task.ARMS:
        assert abs(result['arms'][a]['metrics']['absB_pp']-.6) < 1e-12
        assert result['arms'][a]['adequacy'] == 'FAIL'
        assert result['arms'][a]['required_adequate_calibration_choices'] == 3
        assert len(details[a]['calibration_rows']) == len(details[a]['target_columns']) == 3
    bad = deepcopy(predictions); bad['A2'].pop()
    with pytest.raises(ValueError, match='DENOMINATOR'):
        scoring.evaluate(data[2], data[6], bad, data[7], data[3])


def test_partial_signed_bias_cannot_prove_failure_and_threshold_straddle():
    data = fixture(2); pred = matrix(data)['A2'][:2]
    qs, obs = data[2][2:], data[6][2:]
    pred[0]['prediction']['tds_percent'] = 100*obs[0]['q']+.6
    pred[0]['prediction']['solute_kg'] = qs[0]['mass_kg']*pred[0]['prediction']['tds_percent']/100
    pred[1].update(prediction=None, status='UNSUPPORTED')
    pair = scoring.pair_metrics(qs, obs, pred)
    assert not pair['complete'] and pair['full_lower_absB_pp'] == 0 and pair['adequacy'] == scoring.INCOMPLETE
    assert scoring.leq([.999999, 1.000001], 1.) == scoring.UNRESOLVED
    assert scoring.at_least(8, 10, 9) == scoring.UNRESOLVED


def test_n11_required_counts_and_zero_comparator_no_manufactured_gain():
    metric = {'R_pp': .2, 'B_pp': 0., 'absB_pp': .1, 'R_bounds_pp': [.19, .21],
              'B_bounds_pp': [-.01, .01], 'absB_bounds_pp': [.09, .11],
              'signed_suffix_error_kg': 0., 'absolute_suffix_error_kg': .001, 'maximum_running_error_kg': .001}
    pair = {'complete': True, 'metrics': metric, 'adequacy': 'PASS', 'full_lower_R_pp': .19, 'full_lower_absB_pp': .09}
    row = scoring.summarize([pair]*10)
    assert row['required_adequate_pairs'] == 8
    overall = scoring.summarize([pair]*110)
    ref = deepcopy(overall); ref['metrics']['R_bounds_pp'] = [0., 1e-13]; ref['metrics']['R_pp'] = 1e-14
    inc = scoring.increment(overall, ref, [row]*11, [row]*11, [row]*11, [row]*11)
    assert inc['counts']['targets']['required'] == 9
    assert inc['relative_gain'] is None and inc['components']['relative_R_gain'] == 'FAIL'


def test_report_without_source_or_recomputation_and_replay_guard(tmp_path, monkeypatch):
    for name in ('evaluate',):
        monkeypatch.setattr(scoring, name, lambda *args: (_ for _ in ()).throw(AssertionError('recompute')))
    task.write(tmp_path/'scores.json', {'disposition': 'SYNTHETIC'})
    task.write(tmp_path/'score_completion.json', {'status': 'COMPLETE', 'scientific_score_passes': 1,
                                                 'scores_sha256': task.digest(tmp_path/'scores.json')})
    assert scoring.report(tmp_path) == {'disposition': 'SYNTHETIC'}
    with pytest.raises(ValueError, match='DUPLICATE_SCORE'):
        scoring.verify_before_score(tmp_path, tmp_path/'nonexistent', tmp_path/'no-source')

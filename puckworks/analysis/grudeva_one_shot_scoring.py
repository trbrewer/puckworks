"""008 once-only scoring; pair metrics precede all row/column aggregations.

No historical scorer is invoked. report() reads saved completed results only.
"""
from __future__ import annotations

from collections import Counter
import math
from pathlib import Path
import signal
import time

from . import grudeva_one_shot_calibration as task

INCOMPLETE = 'SOURCE_SUPPORT_INCOMPLETE'
UNRESOLVED = 'NUMERICALLY_UNRESOLVED'


def combine(statuses):
    values = list(statuses)
    return ('FAIL' if 'FAIL' in values else 'PASS' if values and all(s == 'PASS' for s in values)
            else INCOMPLETE if INCOMPLETE in values else UNRESOLVED)


def leq(bounds, threshold):
    if bounds is None:
        return INCOMPLETE
    return 'PASS' if bounds[1] <= threshold else 'FAIL' if bounds[0] > threshold else UNRESOLVED


def at_least(definite, possible, required, complete=True):
    return ('PASS' if definite >= required else 'FAIL' if possible < required
            else UNRESOLVED if complete else INCOMPLETE)


def avg(values):
    return math.fsum(values)/len(values)


def pair_metrics(queries, outcomes, predictions):
    """Fixed full mass denominator; missing signed errors cannot bound |B|."""
    total = math.fsum(q['mass_kg'] for q in queries) if all(q['mass_kg'] is not None for q in queries) else None
    complete = bool(queries) and total is not None and total > 0
    rows = []
    for q, o, r in zip(queries, outcomes, predictions):
        d, p = q['mass_kg'], r['prediction']
        good = r['status'] == 'QUALIFIED' and p is not None
        if good:
            for k in ('solute_kg', 'allowance_kg'):
                task.md.number(p[k])
            good = p['numerical_qualified'] is True and 0 <= p['allowance_kg'] <= 1e-9
            if d is not None and (p['solute_kg'] < -p['allowance_kg'] or p['solute_kg'] > d+p['allowance_kg']):
                raise ValueError('SCORED_SOLUTE_BOUND_FAILURE')
        if d == 0:
            complete = complete and good and p['solute_kg'] == 0 and p['tds_percent'] is None and o['q'] is None
            continue
        if not good or d is None or o['q'] is None:
            complete = False
            continue
        concentration = task.md.number(o['q'])
        if not 0 <= concentration <= 1 or o['chemistry_status'] != 'AVAILABLE':
            raise ValueError('OBSERVED_MASS_FRACTION_REQUIRED')
        observed = d*concentration
        if abs(observed-task.md.number(o['solute_kg'])) > 128*math.ulp(max(observed, 1e-300)):
            raise ValueError('OBSERVED_SOLUTE_UNITS_MISMATCH')
        e = task.md.number(p['tds_percent'])-100*concentration
        a = 100*p['allowance_kg']/d
        rows.append({'vial': q['vial'], 'mass_kg': d, 'error_pp': e, 'allowance_pp': a,
                     'solute_error_kg': p['solute_kg']-observed})
    if not rows:
        complete = False
    lower = 0.
    if rows and total is not None and total > 0:
        low = math.sqrt(math.fsum(r['mass_kg']*max(0., abs(r['error_pp'])-r['allowance_pp'])**2 for r in rows)/total)
        lower = max(0., low-128*math.ulp(max(1., low)))
    metric = None
    if complete:
        R = math.sqrt(math.fsum(r['mass_kg']*r['error_pp']**2 for r in rows)/total)
        B = math.fsum(r['mass_kg']*r['error_pp'] for r in rows)/total
        pad = 128*math.ulp(max(1., R, abs(B)))
        ra = math.sqrt(math.fsum(r['mass_kg']*r['allowance_pp']**2 for r in rows)/total)+pad
        ba = math.fsum(r['mass_kg']*r['allowance_pp'] for r in rows)/total+pad
        cumulative = []; value = 0.
        for r in rows:
            value += r['solute_error_kg']; cumulative.append(value)
        metric = {'R_pp': R, 'B_pp': B, 'absB_pp': abs(B),
                  'R_bounds_pp': [max(0., R-ra), R+ra], 'B_bounds_pp': [B-ba, B+ba],
                  'absB_bounds_pp': [max(0., abs(B)-ba), abs(B)+ba],
                  'signed_suffix_error_kg': value, 'absolute_suffix_error_kg': abs(value),
                  'maximum_running_error_kg': max(map(abs, cumulative))}
    status = combine([leq(metric['R_bounds_pp'], 1.), leq(metric['absB_bounds_pp'], .5)]) if metric else (
        'FAIL' if lower > 1. else INCOMPLETE)
    return {'complete': complete, 'metrics': metric, 'adequacy': status,
            'full_lower_R_pp': lower, 'full_lower_absB_pp': metric['absB_bounds_pp'][0] if metric else 0.,
            'declared_windows': len(queries), 'declared_mass_kg': total, 'scored_windows': len(rows), 'rows': rows}


def summarize(pairs):
    """Averages metrics, never predictions. All declared pairs remain counted."""
    N = len(pairs); required = math.ceil(.75*N)
    complete = N > 0 and all(p['complete'] for p in pairs)
    lower_R = avg([p['full_lower_R_pp'] for p in pairs])
    lower_B = avg([p['full_lower_absB_pp'] for p in pairs])
    lower_R = max(0., lower_R-128*math.ulp(max(1., lower_R)))
    lower_B = max(0., lower_B-128*math.ulp(max(1., lower_B)))
    definite = sum(p['adequacy'] == 'PASS' for p in pairs)
    possible = sum(p['adequacy'] != 'FAIL' for p in pairs)
    metric = None
    if complete:
        fields = ('R_pp', 'B_pp', 'absB_pp', 'signed_suffix_error_kg', 'absolute_suffix_error_kg', 'maximum_running_error_kg')
        metric = {k: avg([p['metrics'][k] for p in pairs]) for k in fields}
        for k in ('R_bounds_pp', 'B_bounds_pp', 'absB_bounds_pp'):
            bounds = [avg([p['metrics'][k][i] for p in pairs]) for i in (0, 1)]
            pad = 128*math.ulp(max(1., *map(abs, bounds)))
            metric[k] = [bounds[0]-pad if k == 'B_bounds_pp' else max(0., bounds[0]-pad), bounds[1]+pad]
    tests = {'mean_R': leq(metric['R_bounds_pp'], 1.) if metric else 'FAIL' if lower_R > 1. else INCOMPLETE,
             'mean_absB': leq(metric['absB_bounds_pp'], .5) if metric else 'FAIL' if lower_B > .5 else INCOMPLETE,
             'adequate_target_pairs': at_least(definite, possible, required, complete)}
    return {'complete': complete, 'declared_pairs': N, 'metrics': metric,
            'lower_R_pp': lower_R, 'lower_absB_pp': lower_B,
            'definite_adequate_pairs': definite, 'possible_adequate_pairs': possible,
            'required_adequate_pairs': required, 'adequacy_components': tests,
            'adequacy': combine(tests.values())}


def distribution(values):
    """Rights-safe descriptive distribution: no shot identities or ordered values."""
    if not values:
        return None
    import numpy as np
    return {'n': len(values), 'min': min(values), 'q25': float(np.quantile(values, .25)),
            'median': float(np.median(values)), 'q75': float(np.quantile(values, .75)),
            'max': max(values), 'mean': avg(values)}


def increment(candidate, reference, candidate_rows, reference_rows, candidate_columns, reference_columns):
    if not candidate['complete'] or not reference['complete']:
        return {'status': INCOMPLETE}
    c, r = candidate['metrics'], reference['metrics']
    cl, ch = c['R_bounds_pp']; rl, rh = r['R_bounds_pp']
    pad = 128*math.ulp(max(1., ch, rh))
    gain = [rl-ch-pad, rh-cl+pad]
    relative = [1-ch/rl-pad, 1-cl/rh+pad] if rl > 1e-12 else None
    deterioration = [c['absB_bounds_pp'][0]-r['absB_bounds_pp'][1]-pad,
                     c['absB_bounds_pp'][1]-r['absB_bounds_pp'][0]+pad]
    counts = {}; required = math.ceil(.75*len(candidate_rows))
    for label, cs, rs in (('calibration_choices', candidate_rows, reference_rows),
                          ('targets', candidate_columns, reference_columns)):
        definite = sum(a['metrics']['R_bounds_pp'][1] < b['metrics']['R_bounds_pp'][0] for a, b in zip(cs, rs))
        possible = sum(a['metrics']['R_bounds_pp'][0] < b['metrics']['R_bounds_pp'][1] for a, b in zip(cs, rs))
        counts[label] = {'definite': definite, 'possible': possible, 'required': required,
                         'status': at_least(definite, possible, required)}
    tests = {'absolute_R_gain': leq([-gain[1], -gain[0]], -.10),
             'relative_R_gain': leq([-relative[1], -relative[0]], -.15) if relative else 'FAIL',
             'target_wins': counts['targets']['status'], 'calibration_choice_wins': counts['calibration_choices']['status'],
             'mean_absB_deterioration': leq(deterioration, .10)}
    return {'status': combine(tests.values()), 'components': tests, 'counts': counts,
            'R_gain_pp': r['R_pp']-c['R_pp'], 'R_gain_bounds_pp': gain,
            'relative_gain': 1-c['R_pp']/r['R_pp'] if relative else None, 'relative_gain_bounds': relative,
            'absB_deterioration_pp': c['absB_pp']-r['absB_pp'], 'absB_deterioration_bounds_pp': deterioration}


def evaluate(queries, outcomes, predictions, cohort, folds):
    shots = sorted(c['shot'] for c in cohort if c['eligible'])
    if len(cohort) != 13 or {c['shot'] for c in cohort} != set(range(1, 14)):
        raise ValueError('ORIGINAL_13_SHOT_DENOMINATOR_REQUIRED')
    if (folds['calibrators'] != shots or folds['targets'] != shots
            or folds['pairs'] != [[j, i] for j in shots for i in shots if j != i]):
        raise ValueError('ALL_OFF_DIAGONAL_PAIRS_REQUIRED')
    expected = {(c['shot'], v) for c in cohort if c['eligible'] for v in range(c['k2']+1, 17)}
    def index(rows, keys, names):
        result = {tuple(r[n] for n in names): r for r in rows}
        if len(result) != len(rows) or set(result) != keys:
            raise ValueError('FIXED_DENOMINATOR_NO_MISSING_DUPLICATE_OR_ENSEMBLE_ROWS')
        return result
    qi = index(queries, expected, ('shot', 'vial')); oi = index(outcomes, expected, ('shot', 'vial'))
    slots = {(j, i, v) for j, i in folds['pairs'] for s, v in expected if s == i}
    if set(predictions) != set(task.ARMS) or len(slots) != folds['intended_slots_per_arm'] or len(expected) != folds['unique_suffix_windows']:
        raise ValueError('FOUR_ARM_FROZEN_SLOT_MATRIX_REQUIRED')
    for q in queries:
        task.old.checked_query(q)
    for o in outcomes:
        task.md.exact_keys(o, ('shot', 'vial', 'q', 'solute_kg', 'chemistry_status'))
    details, arms, rows, columns, numerical = {}, {}, {}, {}, {}
    for arm in task.ARMS:
        pi = index(predictions[arm], slots, ('calibrator', 'shot', 'vial'))
        pairs = {}
        for j, i in folds['pairs']:
            keys = sorted(k for k in expected if k[0] == i)
            preds = [pi[(j, *k)] for k in keys]
            for k, pred in zip(keys, preds):
                if any(pred[name] != value for name, value in qi[k].items()):
                    raise ValueError('PREDICTION_TARGET_GEOMETRY_MISMATCH')
            pairs[(j, i)] = pair_metrics([qi[k] for k in keys], [oi[k] for k in keys], preds)
        rows[arm] = [summarize([pairs[j, i] for i in shots if i != j]) for j in shots]
        columns[arm] = [summarize([pairs[j, i] for j in shots if j != i]) for i in shots]
        overall = summarize(list(pairs.values()))
        definite = sum(r['adequacy'] == 'PASS' for r in rows[arm]); possible = sum(r['adequacy'] != 'FAIL' for r in rows[arm])
        required = math.ceil(.75*len(shots))
        tests = {k: overall['adequacy_components'][k] for k in ('mean_R', 'mean_absB')}
        tests['calibration_choices'] = at_least(definite, possible, required, overall['complete'])
        overall.update(adequacy=combine(tests.values()), adequacy_components=tests,
                       adequate_calibration_choices=definite, possible_adequate_calibration_choices=possible,
                       required_adequate_calibration_choices=required)
        overall['calibration_choice_sensitivity'] = {k: distribution([r['metrics'][k] for r in rows[arm] if r['metrics']]) for k in ('R_pp', 'absB_pp')}
        overall['target_sensitivity'] = {k: distribution([r['metrics'][k] for r in columns[arm] if r['metrics']]) for k in ('R_pp', 'absB_pp')}
        overall['support_counts'] = dict(Counter(r['status'] for r in predictions[arm]))
        overall['feature_extrapolation_slots'] = sum(bool(r['feature_extrapolation']) for r in predictions[arm])
        overall['calibration_mass_extrapolation_slots'] = sum(r['calibration_mass_extrapolation'] for r in predictions[arm])
        numerical[arm] = 'PASS' if all(r['prediction'] and r['prediction']['numerical_qualified'] and r['prediction']['allowance_kg'] <= 1e-9 for r in predictions[arm]) else UNRESOLVED
        arms[arm] = overall
        details[arm] = {'pairs': [{'calibrator': j, 'target': i, **v} for (j, i), v in pairs.items()],
                        'calibration_rows': [{'calibrator': s, **r} for s, r in zip(shots, rows[arm])],
                        'target_columns': [{'target': s, **r} for s, r in zip(shots, columns[arm])]}
    increments = {name: increment(arms['A2'], arms[ref], rows['A2'], rows[ref], columns['A2'], columns[ref])
                  for name, ref in (('I_CAL', 'F2'), ('I_CHEM', 'A0'), ('I_LOCAL', 'M'))}
    complete = all(a['complete'] for a in arms.values())
    a2 = arms['A2']['adequacy']; findings = []
    if a2 == 'PASS' and all(v['status'] == 'PASS' for v in increments.values()) and complete:
        disposition = 'ONE_SHOT_SOURCE_ADAPTATION_EARNED_ON_DECLARED_COHORT'
    elif a2 == 'FAIL':
        disposition = 'ONE_SHOT_C2_ADAPTATION_INADEQUATE'
    elif a2 == 'PASS':
        disposition = 'ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED'
    else:
        disposition = 'SOURCE_CALIBRATION_SUPPORT_OR_NUMERICAL_BLOCK_UNRESOLVED'
    if arms['M']['adequacy'] == 'PASS' and increments['I_LOCAL']['status'] != 'PASS':
        findings.append('SOURCE_ONLY_MODEL_ADEQUATE_NO_EARNED_PRETRAINED_INCREMENT')
    if arms['A0']['adequacy'] == 'PASS' and increments['I_CHEM']['status'] != 'PASS':
        findings.append('EARLY_CHEMISTRY_COMPLEXITY_NOT_EARNED_AFTER_SOURCE_CALIBRATION')
    vector = {'source': 'PASS' if all(o['chemistry_status'] in ('AVAILABLE', 'STRUCTURAL_ZERO') for o in outcomes) else INCOMPLETE,
              'coverage': 'PASS' if complete else INCOMPLETE, 'numerical': numerical,
              'adequacy': {a: v['adequacy'] for a, v in arms.items()},
              'increments': {k: v['status'] for k, v in increments.items()}}
    return {'task': task.TASK, 'primary': 'A2', 'disposition': disposition, 'secondary_findings': findings,
            'status_vector': vector, 'arms': arms, 'increments': increments,
            'original_shots': 13, 'eligible_physical_shots': len(shots), 'ordered_pairs': len(folds['pairs']),
            'unique_suffix_windows': len(expected), 'prediction_slots_per_arm': len(slots),
            'claims': list(task.api.CLAIMS), 'statistical_independence_claimed': False,
            'physical_validation': 'NOT_ESTABLISHED'}, details


def verify_before_score(out, review, consumer):
    if any((out/n).exists() for n in ('score_receipt.json', 'scores.json', 'score_completion.json', 'score_failure.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    f, r = task.read(out/'freeze.json'), task.read(review)
    if (r.get('task') != task.TASK or r.get('status') != 'APPROVED' or r.get('independent') is not True
            or not r.get('reviewer') or r.get('unresolved_blocking_findings') != []
            or r.get('new_task_scores_seen') is not False or r.get('freeze_sha256') != task.digest(out/'freeze.json')):
        raise ValueError('FRESH_INDEPENDENT_EXACT_FREEZE_APPROVAL_REQUIRED')
    for name, root, label in (('producer', task.ROOT, 'reviewed'), ('consumer', Path(consumer), 'ewp_reviewed')):
        if (task.git(root, 'rev-parse', 'HEAD') != f[name+'_commit'] or task.git(root, 'rev-parse', 'HEAD^{tree}') != f[name+'_tree']
                or r.get(label+'_head') != f[name+'_commit'] or r.get(label+'_tree') != f[name+'_tree']
                or r.get(label+'_base') != f[name+'_base']):
            raise ValueError('EXACT_REVIEWED_CANDIDATE_REQUIRED')
    for group, root in (('code_and_protocol', task.ROOT), ('consumer_files', Path(consumer)), ('artifacts', out)):
        for name, expected in f[group].items():
            path = (root/name).resolve()
            if not path.is_relative_to(root.resolve()) or task.digest(path) != expected:
                raise ValueError('FROZEN_BYTES_CHANGED:'+name)
    task.verify_dependencies()


def score(out, review, consumer):
    out = task.private(out); verify_before_score(out, review, consumer)
    previous = task.read(out/'prediction_completion.json')['scientific_wall_seconds']
    task.limits(out, previous); tick = time.monotonic()
    task.write(out/'score_receipt.json', {'task': task.TASK, 'status': 'STARTED',
         'freeze_sha256': task.digest(out/'freeze.json'), 'review_sha256': task.digest(review),
         'predictions_sha256': task.digest(out/'predictions.json')})
    try:
        result, details = evaluate(*(task.read(out/name) for name in
                     ('queries.json', 'outcomes.json', 'predictions.json', 'cohort.json', 'folds.json')))
        manifest = task.read(out/'calibration_manifest.json')
        result['status_vector']['calibration'] = {a: 'PASS' if all(v['status'] == 'QUALIFIED' for k, v in manifest['calibrations'].items() if k.endswith('/'+a)) else 'CALIBRATION_BLOCKED'
                                                    for a in ('A2', 'A0', 'M')}
        result['conditioning_counts'] = task.read(out/'counts.json')
        result['execution'] = task.read(out/'calibration_completion.json')
        result['offset_distribution'] = {a: distribution([task.read(out/f'calibration-{j:02}-{a}.json')['delta']
            for j in task.read(out/'folds.json')['calibrators'] if task.read(out/f'calibration-{j:02}-{a}.json')['delta'] is not None]) for a in ('A0', 'A2')}
        attempts = [r for j in task.read(out/'folds.json')['calibrators'] for r in task.read(out/f'attempts-{j:02}.json')]
        result['mass_boundary_hits'] = dict(Counter(k for r in attempts for k in r['boundary_hits']))
        task.write(out/'pair_row_column_results.json', details); task.write(out/'scores.json', result)
        task.write(out/'score_completion.json', {'task': task.TASK, 'status': 'COMPLETE', 'scientific_score_passes': 1,
             'scores_sha256': task.digest(out/'scores.json'), 'details_sha256': task.digest(out/'pair_row_column_results.json'),
             'outcomes_sha256': task.digest(out/'outcomes.json'), 'score_receipt_sha256': task.digest(out/'score_receipt.json'),
             'wall_seconds': time.monotonic()-tick, 'scientific_wall_seconds': previous+time.monotonic()-tick})
        task.artifact_limit(out)
    except BaseException as exc:
        task.write(out/'score_failure.json', {'task': task.TASK, 'reason': str(exc), 'wall_seconds': time.monotonic()-tick})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def report(out):
    out = Path(out); completion = task.read(out/'score_completion.json')
    if (completion['status'] != 'COMPLETE' or completion['scientific_score_passes'] != 1
            or task.digest(out/'scores.json') != completion['scores_sha256']):
        raise ValueError('SAVED_COMPLETED_RESULT_REQUIRED')
    return task.read(out/'scores.json')

"""Nested conditional TDS comparison; Pocket Science Coffee (2024), private outputs.

The predecessor's observer, fitting, metrics, ordering and bootstrap stay unchanged.
"""
from dataclasses import asdict
import time

import numpy as np
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent

ARMS = (*parent.ARMS, 'P')
NEW_CONTRASTS = (('M', 'P'), ('P', 'N'))
TOLERANCE = 1e-10


def joint_predict(x, y, style, group, weights=None, oracle=False):
    legacy, fits = parent.cross_predict(x, y, style, group, weights)
    w = np.ones(len(y)) if weights is None else np.asarray(weights, dtype=float)
    pooled = np.full(len(y), np.nan)
    checks = []
    for fit in fits:
        g = fit['condition_index']
        train, held = (group != g) & (w > 0), group == g
        xt, yt, wt = x[train], y[train], w[train]
        denominator = np.sum(wt*xt*xt)
        if not np.isfinite(denominator) or denominator <= 0:
            raise ValueError('P training design rank deficient')
        alpha = float(np.clip(np.sum(wt*xt*yt)/denominator, 0, 100))
        pooled[held] = alpha*x[held]
        error = 0.
        if oracle:
            solved = lsq_linear((xt*np.sqrt(wt))[:, None], yt*np.sqrt(wt),
                               bounds=(0, 100), method='bvls', tol=1e-14)
            if not solved.success:
                raise ValueError('independent bounded least squares failed')
            error = float(np.max(abs((alpha-solved.x[0])*x[held])))
            if error > TOLERANCE:
                raise ValueError('P independent prediction check failed')
        theta = np.array(fit['parameters']['M']['coefficients'])
        sse_m = float(np.sum(wt*(theta[style[train]]*xt-yt)**2))
        sse_p = float(np.sum(wt*(alpha*xt-yt)**2))
        allowance = float(128*np.finfo(float).eps*max(1., np.sum(wt*yt*yt), sse_p))
        if sse_m > sse_p+allowance:
            raise ValueError('nested training SSE check failed')
        fit['parameters']['P'] = {'coefficients': [alpha], 'rank': 1,
                                  'active_bounds': [alpha in (0., 100.)]}
        checks.append({'condition_index': g, 'sse_M': sse_m, 'sse_P': sse_p,
                       'roundoff_allowance': allowance, 'oracle_max_difference_pp': error})
    if not np.all(np.isfinite(pooled)):
        raise ValueError('incomplete P prediction coverage')
    return np.column_stack((legacy, pooled)), fits, checks


def scores(y, predictions, group, weights=None):
    result = parent.metrics(y, predictions[:, :3], group, weights)
    # Reuse the identical metric implementation for P without changing parent.ARMS.
    result['P'] = parent.metrics(y, np.repeat(predictions[:, 3:4], 3, axis=1),
                                 group, weights)['M']
    return result


def contrasts(metrics):
    result = parent.contrasts(metrics)
    for a, b in NEW_CONTRASTS:
        reference = metrics[b]['rmse']
        result[a+'/'+b] = {'difference': metrics[a]['rmse']-reference,
                          'gain': 1-metrics[a]['rmse']/reference if reference else None}
    return result


def decision(comparison, failed=0):
    if failed:
        return {'status': 'INCOMPLETE_BOOTSTRAP', 'supported_parsimonious_alternative': False}
    mp, pn = [comparison[k]['gain_ci95'] for k in ('M/P', 'P/N')]
    supported = pn is not None and pn[0] > 0
    if mp is not None and mp[0] > 0:
        status = 'STRATIFICATION_EARNS_CONDITIONAL_PREDICTIVE_INCREMENT'
    elif mp is not None and mp[1] < 0 and supported:
        status = 'POOLED_SCALING_CONDITIONALLY_BETTER'
    elif mp is not None and mp[0] <= 0 <= mp[1]:
        status = 'M/P_UNRESOLVED'
    else:
        status = 'UNRESOLVED_RETAIN_HISTORICAL_M_QUALIFICATION'
    return {'status': status, 'supported_parsimonious_alternative': supported,
            'historical_M_qualification': 'PRESERVED_NOT_REVISED'}


def summarize_intervals(comparison, samples, failed):
    for key, value in comparison.items():
        for quantity in ('difference', 'gain'):
            values = [r['contrasts'][key][quantity] for r in samples
                      if r['contrasts'][key][quantity] is not None]
            value[quantity+'_defined_draws'] = len(values)
            value[quantity+'_ci95'] = (np.percentile(values, [2.5, 97.5]).tolist()
                                      if values and len(values) == len(samples) and not failed else None)
        value['grade'] = parent.grade(value['gain'])
        value['ci_grades'] = parent.interval_grades(value['gain_ci95'])
        value['boundary_check'] = [dict(lower=lo, upper=hi, point=parent.grade(value['gain'], lo, hi),
                                       ci_grades=parent.interval_grades(value['gain_ci95'], lo, hi))
                                  for lo in (.075, .10, .125) for hi in (.1875, .25, .3125)]


def evaluate(shots, observation='filtered', draws=2000, seed=20261026, deadline=None):
    x, y, style, group = parent.arrays(shots, observation)
    pred, fits, checks = joint_predict(x, y, style, group, oracle=True)
    metrics = scores(y, pred, group)
    comparison = contrasts(metrics)
    rng = np.random.default_rng(seed)
    samples, failures, active = [], [], {arm: 0 for arm in ARMS}
    maximum_sse_excess = max(c['sse_M']-c['sse_P'] for c in checks)
    for draw in range(draws):
        if deadline is not None and time.monotonic() > deadline:
            raise ValueError('scientific computation budget exceeded')
        w = parent.bootstrap_weights(group, rng)
        try:
            p, fit, nesting = joint_predict(x, y, style, group, w)
            draw_scores = scores(y, p, group, w)
            samples.append({'draw': draw, 'multiplicities': w.tolist(), 'scores': draw_scores,
                            'contrasts': contrasts(draw_scores)})
            for arm in ARMS:
                active[arm] += int(any(any(f['parameters'][arm]['active_bounds']) for f in fit))
            maximum_sse_excess = max(maximum_sse_excess, max(c['sse_M']-c['sse_P'] for c in nesting))
        except ValueError as exc:
            failures.append({'draw': draw, 'reason': str(exc)})
    summarize_intervals(comparison, samples, failures)
    predictions = []
    for i, shot in enumerate(shots):
        error = pred[i]-y[i]
        predictions.append(dict(asdict(shot), target_pp=float(y[i]), x=float(x[i]),
                                predictions=dict(zip(ARMS, pred[i].tolist())),
                                errors=dict(zip(ARMS, error.tolist())),
                                adverse={a+'/'+b: bool(abs(error[ARMS.index(a)]) > abs(error[ARMS.index(b)]))
                                         for a, b in NEW_CONTRASTS}))
    conditions = []
    for g, condition in enumerate(sorted({s.condition for s in shots})):
        held = group == g
        local = scores(y[held], pred[held], group[held])
        conditions.append({'condition': condition, 'n': int(held.sum()),
                           'scores': local, 'contrasts': contrasts(local)})
    return {'n': len(shots), 'conditions': len(conditions), 'observation': observation,
            'scores': metrics, 'contrasts': comparison, 'decision': decision(comparison, len(failures)),
            'predictions': predictions, 'folds': fits, 'condition_errors': conditions,
            'coverage_per_arm': len(shots), 'nesting_checks': checks,
            'maximum_training_SSE_M_minus_P': maximum_sse_excess,
            'P_bounded_lsq_max_difference_pp': max(c['oracle_max_difference_pp'] for c in checks),
            'worst_absolute_errors': {a: max(predictions, key=lambda r: abs(r['errors'][a])) for a in ARMS},
            'bootstrap': {'requested': draws, 'completed': len(samples), 'failed': len(failures),
                          'failures': failures, 'seed': seed, 'active_bound_draws': active},
            'bootstrap_samples': samples}


def verify_predecessor(result, old_result, old_draws):
    """Full-precision comparison; caller authenticates predecessor file hashes."""
    absolute_errors, gain_errors = [], []
    if result['n'] != old_result['n'] or result['conditions'] != old_result['conditions']:
        raise ValueError('predecessor cohort drift')
    for new, old in zip(result['predictions'], old_result['predictions'], strict=True):
        if (new['sheet'], new['row'], new['target_pp'], tuple(new['condition']), new['style'], new['x']) != (
                old['sheet'], old['row'], old['target_pp'], tuple(old['condition']), old['style'], old['x']):
            raise ValueError('predecessor observation/order drift')
        for arm in parent.ARMS:
            absolute_errors.append(abs(new['predictions'][arm]-old['predictions'][arm]))
    for arm in parent.ARMS:
        for metric, value in old_result['scores'][arm].items():
            absolute_errors.append(abs(result['scores'][arm][metric]-value))
    for new, old in zip(result['bootstrap_samples'], old_draws, strict=True):
        for key in old:
            absolute_errors.append(abs(new['contrasts'][key]['difference']-old[key]['difference']))
            a, b = new['contrasts'][key]['gain'], old[key]['gain']
            if (a is None) != (b is None):
                raise ValueError('predecessor gain definition drift')
            if a is not None:
                gain_errors.append(abs(a-b))
    for key, old in old_result['contrasts'].items():
        for metric in ('difference_ci95', 'gain_ci95'):
            if old[metric] is not None:
                errors = gain_errors if metric.startswith('gain') else absolute_errors
                errors.extend(abs(a-b) for a, b in zip(result['contrasts'][key][metric], old[metric], strict=True))
    max_absolute, max_gain = max(absolute_errors, default=0.), max(gain_errors, default=0.)
    if max(max_absolute, max_gain) > TOLERANCE:
        raise ValueError('unexplained predecessor numerical drift')
    return {'status': 'PASS', 'max_absolute_difference_pp': max_absolute,
            'max_gain_difference': max_gain, 'full_precision_bootstrap_draws': len(old_draws)}


def deletion_influence(shots):
    results = []
    for condition in sorted({s.condition for s in shots}):
        subset = [s for s in shots if s.condition != condition]
        x, y, style, group = parent.arrays(subset)
        pred, fit, checks = joint_predict(x, y, style, group, oracle=True)
        metrics = scores(y, pred, group)
        results.append({'deleted': condition, 'n': len(subset), 'scores': metrics,
                        'contrasts': contrasts(metrics), 'folds': fit, 'nesting_checks': checks})
    ranges = {}
    for key in results[0]['contrasts']:
        ranges[key] = {}
        for metric in ('difference', 'gain'):
            values = [r['contrasts'][key][metric] for r in results]
            ranges[key][metric] = None if None in values else [min(values), max(values)]
    return {'deletions': results, 'influence_ranges_not_ci': ranges}

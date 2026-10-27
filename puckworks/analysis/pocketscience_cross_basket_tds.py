"""Source-only conditional transfer; Pocket Science Coffee (2024), private outputs.

No target observations enter fit_source or predict. Predecessor globals are unchanged.
"""
from dataclasses import asdict
import time

import numpy as np
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled

ARMS = pooled.ARMS  # M, C, N, P; preserves the shared metric implementation.
CONTRASTS = (('P', 'N'), ('M', 'P'), ('M', 'C'), ('C', 'N'))
TOLERANCE = pooled.TOLERANCE
SOURCE = 'Sworks High Flow'
TARGET = 'VST18'


def split(shots):
    """Preserve physical order and use one global condition mapping on both sides."""
    parent.arrays(shots)  # Reject duplicate identities and invalid observations.
    source = np.array([s.sheet == SOURCE for s in shots])
    target = np.array([s.sheet == TARGET for s in shots])
    if not np.all(source | target) or not source.any() or not target.any():
        raise ValueError('incomplete source/target split')
    if {s.condition for s in shots if s.sheet == SOURCE} & {
            s.condition for s in shots if s.sheet == TARGET}:
        raise ValueError('source/target condition collision')
    if {s.style for s in shots if s.sheet == SOURCE} != set(parent.STYLES):
        raise ValueError('missing training style; rank deficient')
    return source, target


def design(x, style, arm):
    x, style = np.asarray(x, dtype=float), np.asarray(style)
    if (x.ndim != 1 or not len(x) or style.shape != x.shape
            or not np.all(np.isfinite(x)) or np.any(x <= 0)
            or not np.all(np.isin(style, (0, 1)))):
        raise ValueError('invalid prediction inputs or design rank')
    z = np.ones((len(x), 1)) if arm in ('P', 'N') else np.eye(2)[style.astype(int)]
    return z*x[:, None] if arm in ('P', 'M') else z


def fit_source(x, y, style, weights=None, oracle=False):
    """Fit all four arms using only explicitly supplied source observations."""
    x, y, style = np.asarray(x), np.asarray(y), np.asarray(style)
    w = np.ones(len(x)) if weights is None else np.asarray(weights, dtype=float)
    if (y.shape != x.shape or w.shape != x.shape or not np.all(np.isfinite(y))
            or not np.all(np.isfinite(w)) or np.any(w < 0) or w.sum() <= 0):
        raise ValueError('invalid source observations or multiplicities')
    params, independent, sse = {}, {}, {}
    for arm in ARMS:
        z = design(x, style, arm)
        a, b = z*np.sqrt(w[:, None]), y*np.sqrt(w)
        if np.linalg.matrix_rank(a) != a.shape[1]:
            raise ValueError('training design rank deficient or missing training style')
        # Disjoint columns make these the exact bounded unweighted/weighted SSE fits.
        coef = np.clip((a.T@b)/np.sum(a*a, axis=0), 0., 100.)
        if not np.all(np.isfinite(coef)):
            raise ValueError('nonfinite source coefficients')
        params[arm] = dict(coefficients=coef.tolist(), rank=a.shape[1],
                           active_bounds=((coef == 0) | (coef == 100)).tolist())
        sse[arm] = float(np.sum(w*(z@coef-y)**2))
        if oracle:
            solved = lsq_linear(a, b, bounds=(0, 100), method='bvls', tol=1e-14)
            if not solved.success:
                raise ValueError('independent bounded least squares failed')
            independent[arm] = solved.x.tolist()
    allowance = float(128*np.finfo(float).eps*max(1., np.sum(w*y*y), sse['P']))
    if sse['M'] > sse['P']+allowance:
        raise ValueError('nested training SSE check failed')
    return dict(parameters=params, training_weight=float(w.sum()), training_sse=sse,
                nesting_roundoff_allowance=allowance, independent_coefficients=independent)


def predict(fit, x, style):
    """Prediction inputs contain no target y, group offsets or recalibration."""
    pred = np.column_stack([design(x, style, a)@fit['parameters'][a]['coefficients']
                            for a in ARMS])
    if not np.all(np.isfinite(pred)):
        raise ValueError('incomplete prediction coverage')
    return pred


def oracle_error(fit, x, style):
    actual = predict(fit, x, style)
    independent = np.column_stack([design(x, style, a)@fit['independent_coefficients'][a]
                                   for a in ARMS])
    error = float(np.max(abs(actual-independent)))
    if error > TOLERANCE:
        raise ValueError('independent bounded prediction check failed')
    return error


def contrasts(scores):
    return {a+'/'+b: dict(difference=scores[a]['rmse']-scores[b]['rmse'],
                         gain=1-scores[a]['rmse']/scores[b]['rmse']
                         if scores[b]['rmse'] else None) for a, b in CONTRASTS}


def decision(comparison, failed=0):
    if failed:
        return 'INCOMPLETE_BOOTSTRAP'
    ci = comparison['P/N']['difference_ci95']
    if ci is not None and ci[1] < 0:
        return 'P_TRANSFER_ADDED_VALUE_OVER_N'
    if ci is not None and ci[0] > 0:
        return 'N_LOWER_TRANSFER_LOSS'
    return 'TRANSFER_COMPARISON_UNRESOLVED'


def support(shots):
    source, target = split(shots)
    x, _, style, _ = parent.arrays(shots)
    out = {}
    for k, name in enumerate(parent.STYLES):
        a, b = x[source & (style == k)], x[target & (style == k)]
        if not len(b):
            raise ValueError('missing evaluation style')
        lo, hi = max(a.min(), b.min()), min(a.max(), b.max())
        out[name] = dict(source_range=[float(a.min()), float(a.max())],
                         target_range=[float(b.min()), float(b.max())],
                         overlap=[float(lo), float(hi)] if lo <= hi else None,
                         target_extrapolation_count=int(((b < a.min()) | (b > a.max())).sum()))
    return out


def evaluate(shots, observation='filtered', draws=2000, seed=20261026, deadline=None):
    source, target = split(shots)
    x, y, style, group = parent.arrays(shots, observation)
    ranges = support(shots)
    fit = fit_source(x[source], y[source], style[source], oracle=True)
    pred = predict(fit, x[target], style[target])
    check = oracle_error(fit, x[target], style[target])
    metrics = pooled.scores(y[target], pred, group[target])
    comparison = contrasts(metrics)
    rng = np.random.default_rng(seed)
    samples, failures, active = [], [], {a: 0 for a in ARMS}
    for draw in range(draws):
        if deadline is not None and time.monotonic() > deadline:
            raise ValueError('scientific computation budget exceeded')
        try:
            w = parent.bootstrap_weights(group, rng)
            f = fit_source(x[source], y[source], style[source], w[source])
            p = predict(f, x[target], style[target])
            scores = pooled.scores(y[target], p, group[target], w[target])
            samples.append(dict(draw=draw, multiplicities=w.tolist(), fit=f,
                                scores=scores, contrasts=contrasts(scores)))
            for arm in ARMS:
                active[arm] += int(any(f['parameters'][arm]['active_bounds']))
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            failures.append(dict(draw=draw, reason=str(exc)))
    pooled.summarize_intervals(comparison, samples, failures)
    for value in comparison.values():
        for quantity in ('difference', 'gain'):
            value[quantity+'_undefined_draws'] = len(samples)-value[quantity+'_defined_draws']
    predictions = []
    for j, i in enumerate(np.flatnonzero(target)):
        shot, error = shots[i], pred[j]-y[i]
        low, high = ranges[shot.style]['source_range']
        predictions.append(dict(asdict(shot), target_pp=float(y[i]), x=float(x[i]),
                                extrapolation=bool(x[i] < low or x[i] > high),
                                predictions=dict(zip(ARMS, pred[j].tolist())),
                                errors=dict(zip(ARMS, error.tolist())),
                                adverse={a+'/'+b: bool(abs(error[ARMS.index(a)]) >
                                                      abs(error[ARMS.index(b)]))
                                         for a, b in CONTRASTS}))
    conditions = sorted({s.condition for s in shots})
    condition_errors = []
    for g in np.unique(group[target]):
        idx = group[target] == g
        local = pooled.scores(y[target][idx], pred[idx], group[target][idx])
        condition_errors.append(dict(condition=conditions[g], n=int(idx.sum()),
                                     scores=local, contrasts=contrasts(local)))
    return dict(training_n=int(source.sum()), evaluation_n=int(target.sum()),
                training_conditions=len(np.unique(group[source])),
                evaluation_conditions=len(np.unique(group[target])), observation=observation,
                source_fit=fit, support=ranges, scores=metrics, contrasts=comparison,
                decision=decision(comparison, len(failures)), predictions=predictions,
                condition_errors=condition_errors, coverage_per_arm=int(target.sum()),
                bounded_lsq_max_difference_pp=check,
                worst_absolute_errors={a: max(predictions, key=lambda r: abs(r['errors'][a]))
                                       for a in ARMS},
                bootstrap=dict(requested=draws, completed=len(samples), failed=len(failures),
                               failures=failures, seed=seed, active_bound_draws=active),
                bootstrap_samples=samples)


def deletion_influence(shots, point):
    source, target = split(shots)
    x, y, style, group = parent.arrays(shots)
    conditions = sorted({s.condition for s in shots})
    results = []
    for g, condition in enumerate(conditions):
        source_delete = bool(np.any(source & (group == g)))
        train = source & (group != g) if source_delete else source
        held = target if source_delete else target & (group != g)
        fit = (fit_source(x[train], y[train], style[train], oracle=True)
               if source_delete else point['source_fit'])
        pred = predict(fit, x[held], style[held])
        scores = pooled.scores(y[held], pred, group[held])
        results.append(dict(deleted=condition, side='source' if source_delete else 'target',
                            training_n=int(train.sum()), evaluation_n=int(held.sum()),
                            source_fit=fit, bounded_lsq_max_difference_pp=oracle_error(fit, x[held], style[held]),
                            scores=scores, contrasts=contrasts(scores)))
    ranges = {}
    for side in ('source', 'target'):
        rows = [r for r in results if r['side'] == side]
        ranges[side] = {}
        for key in point['contrasts']:
            values = {}
            for quantity in ('difference', 'gain'):
                v = [r['contrasts'][key][quantity] for r in rows]
                values[quantity] = None if None in v else [min(v), max(v)]
            values['sign_reversals'] = sum(r['contrasts'][key]['difference']*
                                           point['contrasts'][key]['difference'] < 0 for r in rows)
            values['ties'] = sum(r['contrasts'][key]['difference'] == 0 for r in rows)
            ranges[side][key] = values
    return dict(deletions=results, influence_ranges_not_ci=ranges)

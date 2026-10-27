"""Brass-to-teflon Sworks transfer; Pocket Science Coffee (2024), private results.

The four-arm fitting/metric contracts are reused unchanged. No VST row is accepted
by the scientific evaluator, and target observations never enter a source fit.
"""
from dataclasses import asdict
import time

import numpy as np

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled
from puckworks.analysis import pocketscience_cross_basket_tds as basket

ARMS = basket.ARMS
CONTRASTS = (('P', 'N'), ('M', 'C'), ('M', 'P'), ('C', 'N'))
BASKET = 'Sworks High Flow'
# Admitted only after the runner authenticates original raw J against pinned SHOTS.
DISPERSION = {'Brass': 'brass', 'Teflon': 'teflon'}
predict, oracle_error = basket.predict, basket.oracle_error


def split(shots):
    parent.arrays(shots)  # Physical identity uniqueness, unchanged global grouping.
    if not shots or any(s.sheet != BASKET for s in shots):
        raise ValueError('Sworks-only scientific cohort required; VST contamination')
    if any(len(s.condition) != 4 or s.condition[0] != BASKET
           or parent.STYLE_MAP.get(s.condition[1]) != s.style
           or s.condition[2] not in ('Y', 'N') or s.condition[3] not in DISPERSION for s in shots):
        raise ValueError('unresolved literal dispersion/condition mapping')
    source = np.array([DISPERSION[s.condition[3]] == 'brass' for s in shots])
    target = np.array([DISPERSION[s.condition[3]] == 'teflon' for s in shots])
    expected = {(style, preparation) for style in parent.STYLES for preparation in ('Y', 'N')}
    if not np.all(source ^ target):
        raise ValueError('incomplete or overlapping dispersion split')
    for mask in (source, target):
        if {(s.style, s.condition[2]) for s, keep in zip(shots, mask) if keep} != expected:
            raise ValueError('both styles and preparations required on each dispersion side')
    return source, target


def fit_source(x, y, style, weights=None, oracle=True):
    """Guard finite objectives, then use PR376's unchanged bounded four-arm fit."""
    x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    w = np.ones(x.size) if weights is None else np.asarray(weights, dtype=float)
    if (x.ndim != 1 or not x.size or y.shape != x.shape or w.shape != x.shape
            or not np.all(np.isfinite(x)) or not np.all(np.isfinite(y))
            or not np.all(np.isfinite(w)) or np.any(w < 0)
            or not np.isfinite(w.sum()) or w.sum() <= 0):
        raise ValueError('invalid finite training inputs/weights')
    denominator = np.sum(w*x*x)
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError('invalid P training denominator')
    fit = basket.fit_source(x, y, style, w, oracle=oracle)
    if not all(np.isfinite(v) for v in fit['training_sse'].values()):
        raise ValueError('nonfinite training objective')
    if oracle:
        oracle_error(fit, x, style)
    return fit


def scores(y, pred, group, weights=None):
    y, pred, group = np.asarray(y), np.asarray(pred), np.asarray(group)
    w = np.ones(len(y)) if weights is None else np.asarray(weights)
    if (y.ndim != 1 or not len(y) or pred.shape != (len(y), len(ARMS))
            or group.shape != y.shape or w.shape != y.shape
            or not np.all(np.isfinite(y)) or not np.all(np.isfinite(pred))
            or not np.all(np.isfinite(w)) or np.any(w < 0)
            or any(w[group == g].sum() <= 0 for g in np.unique(group))):
        raise ValueError('invalid target coverage or scoring weights')
    out = pooled.scores(y, pred, group, w)
    if not all(np.isfinite(v) for row in out.values() for v in row.values()):
        raise ValueError('nonfinite target scores')
    return out


def contrasts(metrics):
    result = basket.contrasts(metrics)
    return {a+'/'+b: result[a+'/'+b] for a, b in CONTRASTS}


def conclusion(contrast, failed=0):
    if failed:
        return 'INCOMPLETE'
    ci = contrast['difference_ci95']
    if ci is not None and ci[1] < 0:
        return 'FIRST_ARM_LOWER_LOSS'
    if ci is not None and ci[0] > 0:
        return 'REFERENCE_LOWER_LOSS'
    return 'UNRESOLVED'


def decision(comparison, failed=0):
    return {'FIRST_ARM_LOWER_LOSS': 'P_CROSS_DISPERSION_ADDED_VALUE_OVER_N',
            'REFERENCE_LOWER_LOSS': 'N_LOWER_CROSS_DISPERSION_LOSS',
            'UNRESOLVED': 'CROSS_DISPERSION_COMPARISON_UNRESOLVED',
            'INCOMPLETE': 'INCOMPLETE_BOOTSTRAP'}[conclusion(comparison['P/N'], failed)]


def mc_interpretation(comparison, failed=0):
    return {'FIRST_ARM_LOWER_LOSS': 'SCALING_ADDED_VALUE_BEYOND_STYLE_CONSTANTS',
            'REFERENCE_LOWER_LOSS': 'STYLE_CONSTANTS_LOWER_LOSS',
            'UNRESOLVED': 'INCREMENTAL_SCALING_CLAIM_UNESTABLISHED',
            'INCOMPLETE': 'INCOMPLETE_BOOTSTRAP'}[conclusion(comparison['M/C'], failed)]


def support(shots):
    source, target = split(shots)
    x, _, _, _ = parent.arrays(shots)
    def record(mask):
        a, b = x[source & mask], x[target & mask]
        ra = [float(a.min()), float(a.max())] if len(a) else None
        rb = [float(b.min()), float(b.max())] if len(b) else None
        lo, hi = (max(ra[0], rb[0]), min(ra[1], rb[1])) if ra and rb else (1, 0)
        flags = [dict(identity=shots[i].identity, x=float(x[i]),
                      extrapolation=bool(x[i] < ra[0] or x[i] > ra[1]) if ra else None)
                 for i in np.flatnonzero(target & mask)]
        return dict(training_n=len(a), evaluation_n=len(b), source_range=ra, target_range=rb,
                    overlap=[lo, hi] if lo <= hi else None, missing_training_support=ra is None,
                    target_extrapolation_count=sum(f['extrapolation'] for f in flags) if ra else None,
                    target_flags=flags)
    return dict(overall=record(np.ones(len(shots), dtype=bool)),
                by_style=[dict(style=style, **record(np.array([s.style == style for s in shots])))
                          for style in parent.STYLES],
                by_style_preparation=[dict(style=style, preparation=prep, **record(np.array([
                    (s.style, s.condition[2]) == (style, prep) for s in shots])))
                    for style in parent.STYLES for prep in ('Y', 'N')])


def evaluate(shots, observation='filtered', draws=2000, seed=20261026, deadline=None):
    if not isinstance(draws, int) or draws < 1:
        raise ValueError('positive requested draw count required')
    source, target = split(shots)
    x, y, style, group = parent.arrays(shots, observation)  # Eight Sworks conditions only.
    fit = fit_source(x[source], y[source], style[source])
    pred = predict(fit, x[target], style[target])
    check = oracle_error(fit, x[target], style[target])
    metric = scores(y[target], pred, group[target])
    comparison = contrasts(metric)
    rng = np.random.default_rng(seed)
    samples, failures, active = [], [], {a: 0 for a in ARMS}
    max_excess = fit['training_sse']['M']-fit['training_sse']['P']
    for draw in range(draws):
        w = parent.bootstrap_weights(group, rng)
        try:
            if deadline is not None and time.monotonic() > deadline:
                raise ValueError('scientific computation cap exceeded')
            f = fit_source(x[source], y[source], style[source], w[source])
            p = predict(f, x[target], style[target])
            check = max(check, oracle_error(f, x[target], style[target]))
            m = scores(y[target], p, group[target], w[target])
            samples.append(dict(draw=draw, multiplicities=w.tolist(), fit=f, scores=m, contrasts=contrasts(m)))
            for a in ARMS:
                active[a] += int(any(f['parameters'][a]['active_bounds']))
            max_excess = max(max_excess, f['training_sse']['M']-f['training_sse']['P'])
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            failures.append(dict(draw=draw, multiplicities=w.tolist(), reason=str(exc)))
            break
    pooled.summarize_intervals(comparison, samples, failures)
    for c in comparison.values():
        for quantity in ('difference', 'gain'):
            c[quantity+'_undefined_draws'] = len(samples)-c[quantity+'_defined_draws']
    ranges = support(shots)
    predictions = []
    for j, i in enumerate(np.flatnonzero(target)):
        shot, error = shots[i], pred[j]-y[i]
        strata = [ranges['overall'], next(v for v in ranges['by_style'] if v['style'] == shot.style),
                  next(v for v in ranges['by_style_preparation'] if
                       (v['style'], v['preparation']) == (shot.style, shot.condition[2]))]
        flags = {name: next(f['extrapolation'] for f in r['target_flags'] if f['identity'] == shot.identity)
                 for name, r in zip(('overall', 'style', 'style_preparation'), strata)}
        predictions.append(dict(asdict(shot), target_pp=float(y[i]), x=float(x[i]), extrapolation=flags,
            predictions=dict(zip(ARMS, pred[j].tolist())), errors=dict(zip(ARMS, error.tolist())),
            adverse={a+'/'+b: bool(abs(error[ARMS.index(a)]) > abs(error[ARMS.index(b)])) for a, b in CONTRASTS}))
    conditions, condition_errors, style_errors = sorted({s.condition for s in shots}), [], []
    for g in np.unique(group[target]):
        idx = group[target] == g
        local = scores(y[target][idx], pred[idx], group[target][idx])
        condition_errors.append(dict(condition=conditions[g], n=int(idx.sum()), scores=local, contrasts=contrasts(local)))
    for k, name in enumerate(parent.STYLES):
        idx = style[target] == k
        local = scores(y[target][idx], pred[idx], group[target][idx])
        style_errors.append(dict(style=name, n=int(idx.sum()), scores=local, contrasts=contrasts(local)))
    return dict(training_n=int(source.sum()), evaluation_n=int(target.sum()), training_conditions=4,
                evaluation_conditions=4, scientific_n=len(shots), conditions=8, vst_scientific_n=0,
                global_condition_indices=group.tolist(), observation=observation, source_fit=fit,
                support=ranges, scores=metric, contrasts=comparison, decision=decision(comparison, len(failures)),
                mc_interpretation=mc_interpretation(comparison, len(failures)),
                contrast_conclusions={k: conclusion(v, len(failures)) for k, v in comparison.items()},
                predictions=predictions, condition_errors=condition_errors, style_errors=style_errors,
                coverage_per_arm=int(target.sum()), bounded_lsq_max_difference_pp=check,
                maximum_training_SSE_M_minus_P=max_excess,
                worst_absolute_errors={a: max(predictions, key=lambda r: abs(r['errors'][a])) for a in ARMS},
                bootstrap=dict(requested=draws, completed=len(samples), failed=len(failures),
                    not_run=draws-len(samples)-len(failures), failures=failures, seed=seed, active_bound_draws=active),
                bootstrap_samples=samples)


def deletion_influence(shots, point):
    source, target = split(shots)
    x, y, style, group = parent.arrays(shots)
    rows = []
    for g, condition in enumerate(sorted({s.condition for s in shots})):
        source_delete = bool(np.any(source & (group == g)))
        train = source & (group != g) if source_delete else source
        held = target if source_delete else target & (group != g)
        fit = fit_source(x[train], y[train], style[train]) if source_delete else point['source_fit']
        pred = predict(fit, x[held], style[held])
        metric = scores(y[held], pred, group[held])
        rows.append(dict(deleted=condition, side='source' if source_delete else 'target',
                         training_n=int(train.sum()), evaluation_n=int(held.sum()), source_fit=fit,
                         bounded_lsq_max_difference_pp=oracle_error(fit, x[held], style[held]),
                         scores=metric, contrasts=contrasts(metric)))
    ranges = {}
    for side in ('source', 'target'):
        ranges[side] = {}
        for key, point_c in point['contrasts'].items():
            values = [r['contrasts'][key] for r in rows if r['side'] == side]
            summary = {}
            for quantity in ('difference', 'gain'):
                v = [r[quantity] for r in values]
                summary[quantity] = None if None in v else [min(v), max(v)]
            summary['sign_reversals'] = sum(r['difference']*point_c['difference'] < 0 for r in values)
            summary['ties'] = sum(r['difference'] == 0 for r in values)
            ranges[side][key] = summary
    return dict(deletions=rows, influence_ranges_not_ci=ranges)

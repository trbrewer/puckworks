"""Bounded-slope affine LOCO comparison; Pocket Science Coffee (2024).

Real observations and outputs remain private. No predecessor global is changed.
"""
from dataclasses import asdict
import time

import numpy as np
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled
from puckworks.analysis import pocketscience_cross_basket_tds as basket
from puckworks.analysis.pocketscience_cross_dispersion_tds import conclusion

ARMS = ('A', 'M', 'P', 'N')
CONTRASTS = (('A', 'M'), ('A', 'P'), ('A', 'N'))
TOLERANCE = 1e-10


def inputs(x, y, style, weights=None):
    x, y, style = np.asarray(x, dtype=float), np.asarray(y, dtype=float), np.asarray(style)
    w = np.ones(x.size) if weights is None else np.asarray(weights, dtype=float)
    if (x.ndim != 1 or not x.size or y.shape != x.shape or style.shape != x.shape
            or w.shape != x.shape or not np.all(np.isfinite(x)) or np.any(x <= 0)
            or not np.all(np.isfinite(y)) or not np.all(np.isin(style, (0, 1)))
            or not np.all(np.isfinite(w)) or np.any(w < 0)
            or not np.isfinite(w.sum()) or w.sum() <= 0):
        raise ValueError('invalid finite inputs or positive training/scoring weights')
    return x, y, style.astype(int), w


def design(x, style, arm):
    if arm not in ARMS:
        raise ValueError('unsupported arm')
    if arm == 'A':
        return np.column_stack((basket.design(x, style, 'N'), np.asarray(x)))
    return basket.design(x, style, arm)


def rank_record(z):
    singular = np.linalg.svd(z, compute_uv=False)
    tolerance = float(max(z.shape)*np.finfo(float).eps*singular[0])
    rank = int(np.sum(singular > tolerance))
    if rank != z.shape[1] or not np.all(np.isfinite(singular)):
        raise ValueError('weighted training design rank deficient')
    normalized = z/np.linalg.norm(z, axis=0)
    sv = np.linalg.svd(normalized, compute_uv=False)
    condition = float(sv[0]/sv[-1])
    if not np.isfinite(condition):
        raise ValueError('nonfinite column-normalized condition number')
    return dict(rank=rank, singular_values=singular.tolist(), svd_rank_tolerance=tolerance,
                column_normalized_condition_number=condition)


def predict(fit, x, style, independent=False):
    key = 'independent_coefficients' if independent else 'parameters'
    pred = np.column_stack([design(x, style, arm)@(
        fit[key][arm] if independent else fit[key][arm]['coefficients']) for arm in ARMS])
    if not np.all(np.isfinite(pred)):
        raise ValueError('nonfinite or incomplete raw predictions')
    return pred  # Deliberately no clipping, even outside nominal [0,100] TDS pp.


def oracle_error(fit, x, style):
    error = float(np.max(abs(predict(fit, x, style)-predict(fit, x, style, independent=True))))
    if not np.isfinite(error) or error > TOLERANCE:
        raise ValueError('independent bounded least-squares prediction failure')
    return error


def fit_source(x, y, style, weights=None):
    """Only training x/y/style/weights enter the exact independently checked fits."""
    x, y, style, w = inputs(x, y, style, weights)
    keep = w > 0
    x, y, style, w = x[keep], y[keep], style[keep], w[keep]
    if set(style) != {0, 1}:
        raise ValueError('both training styles required; M rank deficient')
    total = w.sum()
    xbar, ybar = np.sum(w*x)/total, np.sum(w*y)/total
    sxx = float(np.sum(w*(x-xbar)**2))
    sxy = float(np.sum(w*(x-xbar)*(y-ybar)))
    if not np.isfinite(sxx) or sxx <= 0 or not np.isfinite(sxy):
        raise ValueError('positive finite affine Sxx required')
    slope = float(np.clip(sxy/sxx, 0, 100))
    params, independent, sse = {}, {}, {}
    for arm in ARMS:
        z = design(x, style, arm)
        weighted, target = z*np.sqrt(w[:, None]), y*np.sqrt(w)
        diagnostic = rank_record(weighted)
        if arm == 'A':
            coef = np.array([ybar-slope*xbar, slope])
            bounds = ([-np.inf, 0], [np.inf, 100])
            active = [False, slope in (0., 100.)]
        else:
            denominator = np.sum(weighted*weighted, axis=0)
            if not np.all(np.isfinite(denominator)) or np.any(denominator <= 0):
                raise ValueError('positive finite retained-arm denominator required')
            coef = np.clip((weighted.T@target)/denominator, 0, 100)
            bounds = (0, 100)
            active = ((coef == 0) | (coef == 100)).tolist()
        if not np.all(np.isfinite(coef)):
            raise ValueError('nonfinite fitted coefficients')
        solved = lsq_linear(weighted, target, bounds=bounds, method='bvls', tol=1e-14)
        if not solved.success or not np.all(np.isfinite(solved.x)):
            raise ValueError('independent bounded least-squares solver failed')
        params[arm] = dict(coefficients=coef.tolist(), active_bounds=active, **diagnostic)
        independent[arm] = solved.x.tolist()
        sse[arm] = float(np.sum(w*(z@coef-y)**2))
    if not all(np.isfinite(v) for v in sse.values()):
        raise ValueError('nonfinite training objective')
    nesting = {}
    for a, b in (('A', 'P'), ('A', 'N'), ('M', 'P')):
        allowance = float(128*np.finfo(float).eps*max(1., np.sum(w*y*y), sse[a], sse[b]))
        if sse[a] > sse[b]+allowance:
            raise ValueError('training nesting failure '+a+'/'+b)
        nesting[a+'/'+b] = dict(sse_difference=sse[a]-sse[b], allowance=allowance)
    fit = dict(parameters=params, independent_coefficients=independent, training_sse=sse,
               training_weight=float(total), positive_training_rows=len(x), affine_Sxx=sxx,
               affine_Sxy=sxy, nesting_checks=nesting)
    fit['training_oracle_max_difference_pp'] = oracle_error(fit, x, style)
    return fit


def support_record(x, style, train, held):
    def record(a, b):
        low, high = float(x[a].min()), float(x[a].max())
        return dict(training_range=[low, high], held_indices=np.flatnonzero(b).tolist(),
                    held_extrapolation=((x[b] < low) | (x[b] > high)).tolist())
    return dict(overall=record(train, held), by_style={name: record(train & (style == k), held & (style == k))
                for k, name in enumerate(parent.STYLES)})


def cross_predict(x, y, style, group, weights=None, deadline=None):
    x, y, style, w = inputs(x, y, style, weights)
    group = np.asarray(group)
    if group.shape != x.shape or len(np.unique(group)) < 2 or not np.all(np.isfinite(group)):
        raise ValueError('invalid LOCO grouping')
    pred, coverage, fits = np.full((len(x), len(ARMS)), np.nan), np.zeros(len(x), int), []
    for g in np.unique(group):
        if deadline is not None and time.monotonic() > deadline:
            raise ValueError('scientific computation cap exceeded')
        train, held = (group != g) & (w > 0), group == g
        fit = fit_source(x[train], y[train], style[train], w[train])
        pred[held] = predict(fit, x[held], style[held])
        fit.update(condition_index=int(g), held_oracle_max_difference_pp=oracle_error(fit, x[held], style[held]),
                   support=support_record(x, style, train, held))
        fits.append(fit)
        coverage[held] += 1
    if not np.all(coverage == 1) or not np.all(np.isfinite(pred)):
        raise ValueError('incomplete or duplicate out-of-fold coverage')
    return pred, fits


def scores(y, pred, group, weights=None):
    y, pred, group = np.asarray(y), np.asarray(pred), np.asarray(group)
    w = np.ones(len(y)) if weights is None else np.asarray(weights)
    if (y.ndim != 1 or not len(y) or pred.shape != (len(y), len(ARMS)) or group.shape != y.shape
            or w.shape != y.shape or not np.all(np.isfinite(y)) or not np.all(np.isfinite(pred))
            or not np.all(np.isfinite(w)) or np.any(w < 0)
            or any(w[group == g].sum() <= 0 for g in np.unique(group))):
        raise ValueError('invalid score coverage or weights')
    # The unchanged metric helper has three named columns; map each arm explicitly.
    result = {arm: parent.metrics(y, np.repeat(pred[:, j:j+1], 3, axis=1), group, w)['M']
              for j, arm in enumerate(ARMS)}
    if not all(np.isfinite(v) for row in result.values() for v in row.values()):
        raise ValueError('nonfinite target loss')
    return result


def contrasts(metric):
    return {a+'/'+b: dict(difference=metric[a]['rmse']-metric[b]['rmse'],
                         gain=1-metric[a]['rmse']/metric[b]['rmse'] if metric[b]['rmse'] else None)
            for a, b in CONTRASTS}


def decisions(comparison, failed=0):
    conclusions = {k: conclusion(v, failed) for k, v in comparison.items()}
    primary = {'FIRST_ARM_LOWER_LOSS': 'AFFINE_LOWER_THAN_MATCHED_M',
               'REFERENCE_LOWER_LOSS': 'M_LOWER_THAN_AFFINE',
               'UNRESOLVED': 'AFFINE_MATCHED_COMPARISON_UNRESOLVED',
               'INCOMPLETE': 'INCOMPLETE_BOOTSTRAP'}[conclusions['A/M']]
    selection = ('INCOMPLETE_BOOTSTRAP' if failed else 'AFFINE_CONDITIONAL_ADDED_VALUE_OVER_M_P_N'
                 if all(v == 'FIRST_ARM_LOWER_LOSS' for v in conclusions.values())
                 else 'AFFINE_NOT_SELECTED_RETAIN_PRIOR_P_QUALIFICATION')
    return dict(primary=primary, selection=selection, contrasts=conclusions)


def domain_counts(pred, weights=None):
    w = np.ones(len(pred), int) if weights is None else np.asarray(weights)
    return {a: dict(physical_predictions=int(np.sum((pred[:, j] < 0) | (pred[:, j] > 100))),
                    weighted_predictions=int(np.sum(w*((pred[:, j] < 0) | (pred[:, j] > 100)))))
            for j, a in enumerate(ARMS)}


def fit_counts(fits):
    return {a: dict(fits=len(fits), active_fits=sum(any(f['parameters'][a]['active_bounds']) for f in fits),
                    interior_fits=sum(not any(f['parameters'][a]['active_bounds']) for f in fits),
                    active_coefficients=sum(sum(f['parameters'][a]['active_bounds']) for f in fits)) for a in ARMS}


def verify_reference_point(shots, y, x, pred, metric, reference):
    if len(shots) != reference['n'] or len({s.condition for s in shots}) != reference['conditions']:
        raise ValueError('PR375 reference cohort drift')
    differences = []
    for i, (shot, old) in enumerate(zip(shots, reference['predictions'], strict=True)):
        if (shot.sheet, shot.row, tuple(shot.condition), shot.style, y[i], x[i]) != (
                old['sheet'], old['row'], tuple(old['condition']), old['style'], old['target_pp'], old['x']):
            raise ValueError('PR375 observation/identity/order drift')
        differences += [abs(pred[i, ARMS.index(a)]-old['predictions'][a]) for a in ('M', 'P', 'N')]
    differences += [abs(metric[a][k]-v) for a in ('M', 'P', 'N') for k, v in reference['scores'][a].items()]
    maximum = float(max(differences))
    if maximum > TOLERANCE:
        raise ValueError('unexplained PR375 point reference drift')
    return maximum


def evaluate(shots, observation='filtered', draws=2000, seed=20261026, deadline=None, reference=None, reference_draws=None):
    if not isinstance(draws, int) or draws < 1:
        raise ValueError('positive requested draw count required')
    x, y, style, group = parent.arrays(shots, observation)
    pred, fits = cross_predict(x, y, style, group, deadline=deadline)
    metric = scores(y, pred, group)
    comparison = contrasts(metric)
    reproduction = dict(point_max_difference_pp=None, draw_max_difference_pp=0., multiplicities_verified=0)
    if reference is not None:
        reproduction['point_max_difference_pp'] = verify_reference_point(shots, y, x, pred, metric, reference)
    if reference_draws is not None and len(reference_draws) != draws:
        raise ValueError('PR375 requested draw-count drift')
    samples, failures = [], []
    rng = np.random.default_rng(seed)
    for draw in range(draws):
        w = parent.bootstrap_weights(group, rng)
        try:
            if reference_draws is not None:
                old = reference_draws[draw]
                if old['multiplicities'] != w.tolist() or old['draw'] != draw:
                    raise ValueError('PR375 deterministic multiplicity sequence drift')
                reproduction['multiplicities_verified'] += 1
            p, f = cross_predict(x, y, style, group, w, deadline=deadline)
            m = scores(y, p, group, w)
            if reference_draws is not None:
                maximum = max(abs(m[a][k]-v) for a in ('M', 'P', 'N') for k, v in old['scores'][a].items())
                if maximum > TOLERANCE:
                    raise ValueError('unexplained PR375 inline comparator draw drift')
                reproduction['draw_max_difference_pp'] = max(reproduction['draw_max_difference_pp'], maximum)
            samples.append(dict(draw=draw, multiplicities=w.tolist(), scores=m, contrasts=contrasts(m),
                                folds=f, domain=domain_counts(p, w)))
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            failures.append(dict(draw=draw, multiplicities=w.tolist(), reason=str(exc)))
            break
    pooled.summarize_intervals(comparison, samples, failures)
    for c in comparison.values():
        for q in ('difference', 'gain'):
            c[q+'_undefined_draws'] = len(samples)-c[q+'_defined_draws']
    for a in ARMS:
        metric[a]['rmse_ci95'] = np.percentile([d['scores'][a]['rmse'] for d in samples], [2.5, 97.5]).tolist() if samples and not failures else None
    predictions = [dict(asdict(s), x=float(x[i]), target_pp=float(y[i]),
        predictions=dict(zip(ARMS, pred[i].tolist())), errors=dict(zip(ARMS, (pred[i]-y[i]).tolist())),
        out_of_domain={a: bool(pred[i, j] < 0 or pred[i, j] > 100) for j, a in enumerate(ARMS)},
        adverse={a+'/'+b: bool(abs(pred[i, ARMS.index(a)]-y[i]) > abs(pred[i, ARMS.index(b)]-y[i])) for a, b in CONTRASTS})
        for i, s in enumerate(shots)]
    conditions = sorted({s.condition for s in shots})
    condition_errors = [dict(condition=conditions[g], n=int(sum(group == g)),
                            scores=scores(y[group == g], pred[group == g], group[group == g])) for g in np.unique(group)]
    style_errors = [dict(style=name, n=int(sum(style == k)), scores=scores(y[style == k], pred[style == k], group[style == k]))
                    for k, name in enumerate(parent.STYLES)]
    all_fits = fits+[f for d in samples for f in d['folds']]
    return dict(n=len(shots), conditions=len(conditions), observation=observation, scores=metric, contrasts=comparison,
                decision=decisions(comparison, len(failures)), predictions=predictions, folds=fits,
                condition_errors=condition_errors, style_errors=style_errors, coverage_per_arm=len(shots),
                worst_absolute_errors={a: max(predictions, key=lambda r: abs(r['errors'][a])) for a in ARMS},
                point_fit_counts=fit_counts(fits), point_domain=domain_counts(pred), reference_reproduction=reproduction,
                oracle_max_difference_pp=max(max(f['training_oracle_max_difference_pp'], f['held_oracle_max_difference_pp']) for f in all_fits),
                bootstrap=dict(requested=draws, completed=len(samples), failed=len(failures),
                    not_run=draws-len(samples)-len(failures), failures=failures, seed=seed,
                    fit_counts=fit_counts(all_fits[len(fits):]),
                    out_of_domain_draws={a: sum(d['domain'][a]['physical_predictions'] > 0 for d in samples) for a in ARMS}),
                bootstrap_samples=samples)


def deletion_influence(shots, point, deadline=None):
    rows = []
    for condition in sorted({s.condition for s in shots}):
        subset = [s for s in shots if s.condition != condition]
        x, y, style, group = parent.arrays(subset)
        pred, fits = cross_predict(x, y, style, group, deadline=deadline)
        metric = scores(y, pred, group)
        rows.append(dict(deleted=condition, n=len(subset), conditions=len(np.unique(group)),
                         scores=metric, contrasts=contrasts(metric), folds=fits, domain=domain_counts(pred)))
    ranges = {}
    for key, baseline in point['contrasts'].items():
        values = [r['contrasts'][key] for r in rows]
        ranges[key] = {q: None if any(v[q] is None for v in values) else [min(v[q] for v in values), max(v[q] for v in values)]
                       for q in ('difference', 'gain')}
        ranges[key].update(sign_reversals=sum(v['difference']*baseline['difference'] < 0 for v in values),
                           ties=sum(v['difference'] == 0 for v in values))
    return dict(deletions=rows, influence_ranges_not_ci=ranges,
                fit_counts=fit_counts([f for row in rows for f in row['folds']]),
                out_of_domain_deletions={a: sum(row['domain'][a]['physical_predictions'] > 0 for row in rows) for a in ARMS})

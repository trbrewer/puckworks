"""Traditional-only P/N transfer, Pocket Science Coffee (2024); private results.

No target observations enter fit_source or predict; predecessor globals stay intact.
"""
from dataclasses import asdict
import time

import numpy as np
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled

ARMS = ('P', 'N')
TOLERANCE = 1e-10


def split(shots):
    """Partition physical identities by the qualified style, preserving order."""
    parent.arrays(shots)
    source = np.array([s.style == 'traditional' for s in shots], dtype=bool)
    target = np.array([s.style == 'turbo' for s in shots], dtype=bool)
    if not len(shots) or not np.all(source ^ target) or not source.any() or not target.any():
        raise ValueError('incomplete style partition')
    if {s.condition for s, keep in zip(shots, source) if keep} & {
            s.condition for s, keep in zip(shots, target) if keep}:
        raise ValueError('source/target condition collision')
    return source, target


def predictor(x):
    x = np.asarray(x, dtype=float)
    if x.ndim != 1 or not len(x) or not np.all(np.isfinite(x)) or np.any(x <= 0):
        raise ValueError('invalid predictor or nonpositive P denominator')
    return x


def fit_source(x, y, weights=None, oracle=False):
    """Independently fit two bounded scalars to explicitly supplied training data."""
    x, y = predictor(x), np.asarray(y, dtype=float)
    w = np.ones(len(x)) if weights is None else np.asarray(weights, dtype=float)
    if (y.shape != x.shape or w.shape != x.shape or not np.all(np.isfinite(y))
            or not np.all(np.isfinite(w)) or np.any(w < 0)
            or not np.isfinite(w.sum()) or w.sum() <= 0):
        raise ValueError('invalid training observations or weights')
    denominator = np.sum(w*x*x)
    if not np.isfinite(denominator) or denominator <= 0:
        raise ValueError('nonpositive or nonfinite P denominator')
    coefficients = dict(P=float(np.clip(np.sum(w*x*y)/denominator, 0, 100)),
                        N=float(np.clip(np.sum(w*y)/w.sum(), 0, 100)))
    if not all(np.isfinite(v) for v in coefficients.values()):
        raise ValueError('nonfinite source coefficient')
    independent, sse = {}, {}
    for arm in ARMS:
        z = x if arm == 'P' else np.ones(len(x))
        sse[arm] = float(np.sum(w*(z*coefficients[arm]-y)**2))
        if not np.isfinite(sse[arm]):
            raise ValueError('nonfinite training objective')
        if oracle:
            solved = lsq_linear((z*np.sqrt(w))[:, None], y*np.sqrt(w),
                                bounds=(0, 100), method='bvls', tol=1e-14)
            if not solved.success:
                raise ValueError('independent bounded least squares failed')
            independent[arm] = float(solved.x[0])
    fit = dict(coefficients=coefficients, active_bounds={a: v in (0., 100.)
               for a, v in coefficients.items()}, training_weight=float(w.sum()),
               training_sse=sse, independent_coefficients=independent)
    if oracle:
        oracle_error(fit, x)
    return fit


def predict(coefficients, x):
    """Accept only source coefficients and evaluation x; no evaluation y."""
    x = predictor(x)
    if set(coefficients) != set(ARMS) or not all(
            np.isfinite(v) and 0 <= v <= 100 for v in coefficients.values()):
        raise ValueError('invalid bounded coefficients')
    pred = np.column_stack((coefficients['P']*x, np.full(len(x), coefficients['N'])))
    if not np.all(np.isfinite(pred)):
        raise ValueError('incomplete target coverage')
    return pred


def oracle_error(fit, x):
    error = float(np.max(abs(predict(fit['coefficients'], x)-
                              predict(fit['independent_coefficients'], x))))
    if error > TOLERANCE:
        raise ValueError('independent bounded prediction check failed')
    return error


def scores(y, pred, group, weights=None):
    y, pred, group = np.asarray(y), np.asarray(pred), np.asarray(group)
    w = np.ones(len(y)) if weights is None else np.asarray(weights, dtype=float)
    if (y.ndim != 1 or not len(y) or pred.shape != (len(y), 2) or group.shape != y.shape
            or w.shape != y.shape or not np.all(np.isfinite(y))
            or not np.all(np.isfinite(pred)) or not np.all(np.isfinite(w))
            or np.any(w < 0) or any(w[group == g].sum() <= 0 for g in np.unique(group))):
        raise ValueError('invalid scoring coverage or weights')
    # Reuse the established physical-shot metrics without modifying its arm globals.
    out = {a: parent.metrics(y, np.repeat(pred[:, j:j+1], 3, axis=1), group, w)['M']
           for j, a in enumerate(ARMS)}
    if not all(np.isfinite(v) for row in out.values() for v in row.values()):
        raise ValueError('nonfinite target score')
    return out


def contrasts(metrics):
    p, n = (metrics[a]['rmse'] for a in ARMS)
    return {'P/N': dict(difference=p-n, gain=1-p/n if n else None)}


def decision(comparison, failed=0):
    if failed:
        return 'INCOMPLETE_BOOTSTRAP'
    ci = comparison['P/N']['difference_ci95']
    if ci is not None and ci[1] < 0:
        return 'P_CROSS_STYLE_ADDED_VALUE_OVER_N'
    if ci is not None and ci[0] > 0:
        return 'N_LOWER_CROSS_STYLE_LOSS'
    return 'CROSS_STYLE_COMPARISON_UNRESOLVED'


def support(shots):
    source, target = split(shots)
    x, _, _, _ = parent.arrays(shots)
    def record(mask):
        a, b = x[source & mask], x[target & mask]
        ra = [float(a.min()), float(a.max())] if len(a) else None
        rb = [float(b.min()), float(b.max())] if len(b) else None
        lo, hi = (max(ra[0], rb[0]), min(ra[1], rb[1])) if ra and rb else (1, 0)
        return dict(training_n=len(a), evaluation_n=len(b), source_range=ra, target_range=rb,
                    overlap=[lo, hi] if lo <= hi else None,
                    missing_training_support=not len(a),
                    target_extrapolation_count=int(((b < ra[0]) | (b > ra[1])).sum()) if ra else None)
    baskets = sorted({s.sheet for s in shots})
    preparations = sorted({(s.sheet, *s.condition[2:]) for s in shots})
    return dict(overall=record(np.ones(len(shots), dtype=bool)),
                by_basket=[dict(basket=b, **record(np.array([s.sheet == b for s in shots])))
                           for b in baskets],
                by_preparation=[dict(preparation=k, **record(np.array([
                    (s.sheet, *s.condition[2:]) == k for s in shots]))) for k in preparations])


def evaluate(shots, observation='filtered', draws=2000, seed=20261026, deadline=None):
    if not isinstance(draws, int) or draws < 1:
        raise ValueError('positive requested draw count required')
    source, target = split(shots)
    x, y, _, group = parent.arrays(shots, observation)
    fit = fit_source(x[source], y[source], oracle=True)
    pred = predict(fit['coefficients'], x[target])
    check = oracle_error(fit, x[target])
    metrics = scores(y[target], pred, group[target])
    comparison = contrasts(metrics)
    rng = np.random.default_rng(seed)
    samples, failures, active = [], [], {a: 0 for a in ARMS}
    for draw in range(draws):
        w = parent.bootstrap_weights(group, rng)
        try:
            if deadline is not None and time.monotonic() > deadline:
                raise ValueError('scientific computation budget exceeded')
            f = fit_source(x[source], y[source], w[source], oracle=True)
            p = predict(f['coefficients'], x[target])
            check = max(check, oracle_error(f, x[target]))
            metric = scores(y[target], p, group[target], w[target])
            samples.append(dict(draw=draw, multiplicities=w.tolist(), fit=f,
                                scores=metric, contrasts=contrasts(metric)))
            for a in ARMS:
                active[a] += int(f['active_bounds'][a])
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            failures.append(dict(draw=draw, multiplicities=w.tolist(), reason=str(exc)))
            break  # Preserve the failed attempt and all unattempted draws explicitly.
    pooled.summarize_intervals(comparison, samples, failures)
    for value in comparison.values():
        for quantity in ('difference', 'gain'):
            value[quantity+'_undefined_draws'] = len(samples)-value[quantity+'_defined_draws']
    ranges = support(shots)
    predictions = []
    for j, i in enumerate(np.flatnonzero(target)):
        shot, error = shots[i], pred[j]-y[i]
        strata = [ranges['overall'], next(v for v in ranges['by_basket'] if v['basket'] == shot.sheet),
                  next(v for v in ranges['by_preparation']
                       if v['preparation'] == (shot.sheet, *shot.condition[2:]))]
        flags = {name: (bool(x[i] < r['source_range'][0] or x[i] > r['source_range'][1])
                        if r['source_range'] else None)
                 for name, r in zip(('overall', 'basket', 'preparation'), strata)}
        predictions.append(dict(asdict(shot), target_pp=float(y[i]), x=float(x[i]),
                                extrapolation=flags, predictions=dict(zip(ARMS, pred[j].tolist())),
                                errors=dict(zip(ARMS, error.tolist())),
                                adverse_P_vs_N=bool(abs(error[0]) > abs(error[1]))))
    condition_errors, basket_errors = [], []
    conditions = sorted({s.condition for s in shots})
    for g in np.unique(group[target]):
        idx = group[target] == g
        local = scores(y[target][idx], pred[idx], group[target][idx])
        condition_errors.append(dict(condition=conditions[g], n=int(idx.sum()),
                                     scores=local, contrasts=contrasts(local)))
    for basket in sorted({s.sheet for s, keep in zip(shots, target) if keep}):
        idx = np.array([s.sheet == basket for s, keep in zip(shots, target) if keep])
        local = scores(y[target][idx], pred[idx], group[target][idx])
        basket_errors.append(dict(basket=basket, n=int(idx.sum()), scores=local,
                                  contrasts=contrasts(local), descriptive_only=True))
    return dict(training_n=int(source.sum()), evaluation_n=int(target.sum()),
                training_conditions=len(np.unique(group[source])),
                evaluation_conditions=len(np.unique(group[target])), observation=observation,
                source_fit=fit, support=ranges, scores=metrics, contrasts=comparison,
                decision=decision(comparison, len(failures)), predictions=predictions,
                condition_errors=condition_errors, basket_errors=basket_errors,
                coverage_per_arm=int(target.sum()), bounded_lsq_max_difference_pp=check,
                worst_absolute_errors={a: max(predictions, key=lambda r: abs(r['errors'][a])) for a in ARMS},
                bootstrap=dict(requested=draws, completed=len(samples), failed=len(failures),
                               not_run=draws-len(samples)-len(failures), failures=failures,
                               seed=seed, active_bound_draws=active), bootstrap_samples=samples)


def deletion_influence(shots, point):
    source, target = split(shots)
    x, y, _, group = parent.arrays(shots)
    results = []
    for g, condition in enumerate(sorted({s.condition for s in shots})):
        source_delete = bool(np.any(source & (group == g)))
        train = source & (group != g) if source_delete else source
        held = target if source_delete else target & (group != g)
        fit = fit_source(x[train], y[train], oracle=True) if source_delete else point['source_fit']
        pred = predict(fit['coefficients'], x[held])
        metrics = scores(y[held], pred, group[held])
        results.append(dict(deleted=condition, side='source' if source_delete else 'target',
                            training_n=int(train.sum()), evaluation_n=int(held.sum()),
                            source_fit=fit, bounded_lsq_max_difference_pp=oracle_error(fit, x[held]),
                            scores=metrics, contrasts=contrasts(metrics)))
    ranges = {}
    for side in ('source', 'target'):
        rows = [r['contrasts']['P/N'] for r in results if r['side'] == side]
        values = {}
        for quantity in ('difference', 'gain'):
            v = [r[quantity] for r in rows]
            values[quantity] = None if None in v else [min(v), max(v)]
        values['sign_reversals'] = sum(r['difference']*point['contrasts']['P/N']['difference'] < 0
                                       for r in rows)
        values['ties'] = sum(r['difference'] == 0 for r in rows)
        ranges[side] = values
    return dict(deletions=results, influence_ranges_not_ci=ranges)

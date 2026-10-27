"""Offline conditional cup TDS, Pocket Science Coffee (2024).

Mass inputs are kg; targets/predictions are numeric TDS percentage points.
All real-source outputs are private. No production component is registered.
"""
from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math

import numpy as np

from puckworks.analysis.pocketscience2024_assay import inspect_workbook

SOURCE_SHA256 = '9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc'
STYLE_MAP = {'Niche Zero': 'traditional', 'Superjolly MP64': 'turbo'}
STYLES = ('traditional', 'turbo')
ARMS = ('M', 'C', 'N')
CONTRASTS = (('M', 'C'), ('M', 'N'), ('C', 'N'))
EXPOSURE = ('SOURCE_INTERNAL / TARGET_EXPOSED / RETROSPECTIVE / '
            'CONDITIONAL_ON_MEASURED_FINAL_BEVERAGE_MASS')


@dataclass(frozen=True)
class Shot:
    sheet: str
    row: int
    condition: tuple[str, ...]
    style: str
    dose_kg: float
    beverage_kg: float
    filtered_tds_pp: float
    unfiltered_tds_pp: float
    source_excluded: bool = False

    def __post_init__(self):
        if self.style not in STYLES:
            raise ValueError('unknown style')
        for name in ('dose_kg', 'beverage_kg', 'filtered_tds_pp', 'unfiltered_tds_pp'):
            v = getattr(self, name)
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError('missing/nonfinite cup primitive')
            if (name.endswith('_kg') and v <= 0) or (name.endswith('_pp') and not 0 <= v <= 100):
                raise ValueError('invalid primitive basis/range')

    @property
    def identity(self):
        return (self.sheet, self.row)


def observe_sheet(sheet):
    """Read raw columns, never cached derived EY or blank-as-zero values."""
    rows, failed_rejects = [], []
    header = None
    headers = {'B': 'TDS (filtered)', 'C': 'TDS (unfiltered)',
               'D': 'Dose', 'E': 'Output', 'F': 'Grinder',
               'I': 'Puck Screen', 'J': 'Dispersion block'}
    for cells in sheet:
        r = cells[0].row
        if cells[0].value == 'Shot':
            header = r
            if any(str(sheet[f'{c}{r}'].value).strip() != value for c, value in headers.items()):
                raise ValueError('unauthenticated source header')
        if isinstance(cells[0].value, bool) or not isinstance(cells[0].value, (int, float)):
            continue
        if header is None:
            raise ValueError('physical row lacks header')
        grinder = sheet[f'F{r}'].value
        if grinder not in STYLE_MAP:
            raise ValueError('unmapped source grinder')
        cond = (sheet.title, grinder, sheet[f'I{r}'].value, sheet[f'J{r}'].value)
        if cond[2] not in ('Y', 'N') or not isinstance(cond[3], str) or not cond[3]:
            raise ValueError('incomplete condition')
        note_col = {'Sworks High Flow': 'AV', 'VST18': 'AU'}[sheet.title]
        note = sheet[f'{note_col}{r}'].value
        excluded = bool(note and 'reject' in str(note).lower())
        try:
            vals = []
            for col in 'BCDE':
                cell = sheet[f'{col}{r}']
                if cell.data_type == 'f' or '%' in cell.number_format:
                    raise ValueError('cup primitive must be raw numeric percent or grams')
                v = cell.value
                if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                    raise ValueError('missing/nonfinite cup primitive')
                vals.append(v)
            b, c, d, e = vals
            rows.append(Shot(sheet.title, r, cond, STYLE_MAP[grinder], d/1000, e/1000, b, c, excluded))
        except ValueError as exc:
            if not excluded:
                raise ValueError('required primary cup primitive failed') from exc
            failed_rejects.append({'identity': [sheet.title, r], 'reason': str(exc)})
    return rows, failed_rejects


def read_source(path):
    if sha256(path.read_bytes()).hexdigest() != SOURCE_SHA256:
        raise ValueError('workbook SHA256 mismatch')
    f, cached = inspect_workbook(path)
    rows, failed = [], []
    try:
        if set(f.sheetnames) != {'Sworks High Flow', 'VST18', 'LRR'}:
            raise ValueError('unexpected source sheets')
        for name in ('Sworks High Flow', 'VST18'):
            good, bad = observe_sheet(f[name])
            rows.extend(good)
            failed.extend(bad)
        primary = [s for s in rows if not s.source_excluded]
        if (len(primary) != 57 or len({s.condition for s in primary}) != 12
                or sum(s.sheet == 'Sworks High Flow' for s in primary) != 37
                or len(rows)+len(failed) != 60
                or not any(s.sheet == 'Sworks High Flow' and s.row == 54 for s in primary)):
            raise ValueError('frozen primary cohort changed')
        if len({s.identity for s in rows}) != len(rows):
            raise ValueError('unresolved physical identity')
        return rows, failed
    finally:
        f.close()
        cached.close()


def membership_hash(shots):
    payload = [{'identity': s.identity, 'condition': s.condition, 'style': s.style}
               for s in sorted(shots, key=lambda s: s.identity)]
    return sha256(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def arrays(shots, observation='filtered'):
    if observation not in ('filtered', 'unfiltered'):
        raise ValueError('unsupported observation')
    if len({s.identity for s in shots}) != len(shots):
        raise ValueError('duplicate physical identity')
    conditions = sorted({s.condition for s in shots})
    x = np.array([s.dose_kg/s.beverage_kg for s in shots])
    y = np.array([getattr(s, observation+'_tds_pp') for s in shots])
    style = np.array([STYLES.index(s.style) for s in shots])
    group = np.array([conditions.index(s.condition) for s in shots])
    return x, y, style, group


def cross_predict(x, y, style, group, weights=None, oracle=False):
    """One global multiplicity vector; held y is never passed to a fit."""
    w = np.ones(len(y)) if weights is None else np.asarray(weights, dtype=float)
    if w.shape != y.shape or not np.all(np.isfinite(w)) or np.any(w < 0):
        raise ValueError('invalid multiplicities')
    pred = np.full((len(y), 3), np.nan)
    fits = []
    for g in np.unique(group):
        train, held = (group != g) & (w > 0), group == g
        params = {}
        for arm in ARMS:
            z = np.ones((len(y), 1)) if arm == 'N' else np.eye(2)[style]
            if arm == 'M':
                z = z*x[:, None]
            a = z[train]*np.sqrt(w[train, None])
            target = y[train]*np.sqrt(w[train])
            if np.linalg.matrix_rank(a) != a.shape[1]:
                raise ValueError('training design rank deficient')
            if oracle:
                raw = np.linalg.lstsq(a, target, rcond=None)[0]
            else:
                raw = (a.T@target)/np.sum(a*a, axis=0)
            coef = np.clip(raw, 0., 100.)
            pred[held, ARMS.index(arm)] = z[held]@coef
            params[arm] = {'coefficients': coef.tolist(),
                           'active_bounds': ((coef == 0) | (coef == 100)).tolist(), 'rank': a.shape[1]}
        fits.append({'condition_index': int(g), 'training_weight': float(w[train].sum()),
                     'parameters': params})
    if not np.all(np.isfinite(pred)):
        raise ValueError('incomplete prediction coverage')
    return pred, fits


def metrics(y, pred, group, weights=None):
    w = np.ones(len(y)) if weights is None else weights
    error = pred-y[:, None]
    out = {}
    for j, arm in enumerate(ARMS):
        mse = np.average(error[:, j]**2, weights=w)
        balanced = np.mean([np.average(error[group == g, j]**2, weights=w[group == g])
                            for g in np.unique(group)])
        out[arm] = {'rmse': float(np.sqrt(mse)),
                    'mae': float(np.average(abs(error[:, j]), weights=w)),
                    'bias': float(np.average(error[:, j], weights=w)),
                    'condition_balanced_rmse': float(np.sqrt(balanced))}
    return out


def contrasts(scores):
    return {a+'/'+b: {'difference': scores[a]['rmse']-scores[b]['rmse'],
                     'gain': 1-scores[a]['rmse']/scores[b]['rmse'] if scores[b]['rmse'] else None}
            for a, b in CONTRASTS}


def bootstrap_weights(group, rng):
    w = np.zeros(len(group), dtype=int)
    for g in np.unique(group):
        idx = np.flatnonzero(group == g)
        w += np.bincount(rng.choice(idx, len(idx), replace=True), minlength=len(group))
    return w


def grade(value, low=.10, high=.25):
    if value is None:
        return 'undefined'
    return 'worse' if value < 0 else 'small' if value < low else 'moderate' if value < high else 'large'


def interval_grades(ci, low=.10, high=.25):
    if ci is None:
        return ['undefined']
    left, right = ci
    return [name for name, a, b in [('worse', -np.inf, 0), ('small', 0, low),
                                  ('moderate', low, high), ('large', high, np.inf)]
            if right >= a and left < b]


def decide(comparison):
    def lower(k):
        ci = comparison[k]['gain_ci95']
        return ci[0] if ci is not None else -math.inf
    mc = comparison['M/C']['gain_ci95']
    unresolved = mc is not None and mc[0] <= 0 <= mc[1]
    if lower('M/C') > 0 and lower('M/N') > 0:
        selected = 'M_CONDITIONAL_RESEARCH_REUSE'
    elif lower('C/N') > 0:
        selected = 'C_LOWER_INPUT_REFERENCE'
    elif lower('M/N') > 0:
        selected = 'NO_SELECTED_WINNER'
    else:
        selected = 'N_REFERENCE_ADDED_VALUE_UNESTABLISHED'
    return {'selected': selected, 'mc_choice_unresolved': unresolved,
            'incremental_scaling_established': lower('M/C') > 0,
            'm_conditional_disadvantage': mc is not None and mc[1] < 0}


def evaluate(shots, observation='filtered', draws=2000, seed=20261026):
    x, y, style, group = arrays(shots, observation)
    pred, fits = cross_predict(x, y, style, group)
    oracle, _ = cross_predict(x, y, style, group, oracle=True)
    cross_error = float(np.max(abs(pred-oracle)))
    if cross_error > 1e-10:
        raise ValueError('independent least-squares cross-check failed')
    scores = metrics(y, pred, group)
    comparison = contrasts(scores)
    rng = np.random.default_rng(seed)
    samples, failures, active_draws = [], [], 0
    for i in range(draws):
        w = bootstrap_weights(group, rng)
        try:
            p, fit = cross_predict(x, y, style, group, w)
            samples.append(contrasts(metrics(y, p, group, w)))
            active_draws += any(any(v['active_bounds']) for f in fit for v in f['parameters'].values())
        except ValueError as exc:
            failures.append({'draw': i, 'reason': str(exc)})
    for key, item in comparison.items():
        for metric in ('difference', 'gain'):
            values = [s[key][metric] for s in samples if s[key][metric] is not None]
            item[metric+'_defined_draws'] = len(values)
            item[metric+'_ci95'] = (np.percentile(values, [2.5, 97.5]).tolist()
                                    if values and len(values) == len(samples) else None)
        item['grade'] = grade(item['gain'])
        item['ci_grades'] = interval_grades(item['gain_ci95'])
        item['boundary_check'] = [dict(lower=lo, upper=hi, point=grade(item['gain'], lo, hi),
                                       ci_grades=interval_grades(item['gain_ci95'], lo, hi))
                                  for lo in (.075, .10, .125) for hi in (.1875, .25, .3125)]
    conditions = sorted({s.condition for s in shots})
    condition_errors = []
    for g, condition in enumerate(conditions):
        idx = group == g
        local = metrics(y[idx], pred[idx], group[idx])
        condition_errors.append({'condition': condition, 'n': int(idx.sum()), 'scores': local,
                                 'contrasts': contrasts(local)})
    predictions = []
    for i, s in enumerate(shots):
        errors = pred[i]-y[i]
        predictions.append(dict(asdict(s), target_pp=float(y[i]), x=float(x[i]),
                                diagnostic_ey_pp=float(y[i]/x[i]),
                                predictions=dict(zip(ARMS, pred[i].tolist())),
                                errors=dict(zip(ARMS, errors.tolist())),
                                adverse={a+'/'+b: bool(abs(errors[ARMS.index(a)]) > abs(errors[ARMS.index(b)]))
                                         for a, b in CONTRASTS}))
    return {'n': len(shots), 'conditions': len(conditions), 'observation': observation,
            'scores': scores, 'contrasts': comparison, 'decision': decide(comparison),
            'bootstrap': {'requested': draws, 'completed': len(samples), 'failed': len(failures),
                          'failures': failures, 'seed': seed, 'active_bound_draws': active_draws},
            'bootstrap_samples': samples, 'folds': fits, 'predictions': predictions,
            'condition_errors': condition_errors, 'prediction_coverage_per_arm': len(shots),
            'worst_absolute_error': {a: max(predictions, key=lambda r: abs(r['errors'][a])) for a in ARMS},
            'least_squares_max_difference_pp': cross_error}


def deletion_influence(shots):
    results = []
    for condition in sorted({s.condition for s in shots}):
        subset = [s for s in shots if s.condition != condition]
        x, y, style, group = arrays(subset)
        p, fit = cross_predict(x, y, style, group)
        scores = metrics(y, p, group)
        results.append({'deleted': condition, 'n': len(subset), 'scores': scores,
                        'contrasts': contrasts(scores), 'folds': fit})
    ranges = {}
    for key in results[0]['contrasts']:
        ranges[key] = {}
        for metric in ('difference', 'gain'):
            values = [r['contrasts'][key][metric] for r in results]
            ranges[key][metric] = None if None in values else [min(values), max(values)]
    return {'deletions': results, 'influence_ranges_not_ci': ranges}

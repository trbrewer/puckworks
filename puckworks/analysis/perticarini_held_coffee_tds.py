"""Conditional reported-condition TDS transfer; Perticarini/Egidi factual tables.

No source artwork or blanket source licence. Research-only; no production default.
"""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
import math
import subprocess
import time
from pathlib import Path

import numpy as np

from puckworks.analysis import perticarini2024_pressure_chemistry as authority

TASK = 'SCI-MD-PERTICARINI-HELD-COFFEE-TDS-001'
ARMS = ('D3', 'R3', 'T2', 'N')
COFFEES = ('cibao', 'modoetia')
PAIRS = (('D3', 'R3'), ('D3', 'T2'), ('D3', 'N'), ('R3', 'T2'), ('R3', 'N'))
FEATURES = {'D3': ('xD', 'xT'), 'R3': ('xR', 'xT'), 'T2': ('xT',), 'N': ()}
STRATA = (('cibao', ('fine', 'optimal', 'coarse'), 3),
          ('cibao', ('extra_fine', 'extra_coarse'), 2),
          ('modoetia', ('fine', 'optimal', 'coarse'), 3))
PINS = dict(main='21669a427145194e1f4003e3cf1b97dedefe2679',
            base='08e02ccc1a7da6e2a323678ccdba60f3181e6f94',
            base_parent='6a97530d746269cf9e9d46dbcbdfd83e54a2caf5',
            chemistry='fab67de4e82f3b76352df794056a53d70f32029d',
            duration='7bc013d4e00e416fb747d4c37e3cc514dc2e098d',
            EWP='f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516')
BLOBS = ('0c657a30b7c8e048459e79a0b6e34980cba26f75',
         '2f83cd9b59349cd2cf0e9b085ccf5ac03263cff5')
METHODS = 'docs/analysis/sci_md_perticarini_held_coffee_tds_001/METHODS.md'


class QualificationError(ValueError):
    """A required contract failed; no rescue or partial inference."""


def require(ok, message):
    if not ok:
        raise QualificationError(message)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(',', ':')).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def save(path, obj):
    Path(path).write_bytes(canonical(obj)+b'\n')


def authenticate(root):
    """Pinned bytes then full-key, every-field and exact-order observation reproduction."""
    root = Path(root)
    observations, inputs = authority.load_observations(root/'puckworks/data')
    require(tuple(x['file_sha256'] for x in inputs) == authority.HASHES, 'source SHA256 drift')
    require(tuple(x['git_blob_sha1'] for x in inputs) == BLOBS, 'source Git blob drift')
    files = {}
    for label, producer in [('grind', PINS['duration']), ('chemistry', PINS['chemistry'])]:
        names = [f'puckworks/analysis/perticarini2024_pressure_{label}.py']
        names += [f'docs/analysis/sci_md_perticarini_pressure_{label}_001/{n}'
                  for n in ('SOURCE_NOTES.md', 'RESULT.md', 'observations.csv')]
        for name in names:
            raw = (root/name).read_bytes()
            pinned = subprocess.check_output(['git', 'show', producer+':'+name], cwd=root)
            require(raw == pinned, 'pinned operator/qualification drift: '+name)
            files[name] = dict(sha256=sha(raw), producer=producer)
    view = root/'docs/analysis/sci_md_perticarini_pressure_chemistry_001/observations.csv'
    with view.open(newline='', encoding='utf-8') as stream:
        accepted = list(csv.DictReader(stream))
    reconstructed = [{k: str(v) for k, v in o.items()} for o in observations]
    require(reconstructed == accepted, 'complete accepted observation view/order mismatch')
    require([sum(o['coffee_id'] == c for o in observations) for c in COFFEES] == [18, 12],
            'condition membership mismatch')
    return observations, dict(inputs=inputs, files=files, compared_fields=sum(map(len, accepted)),
        original_PDFs_reopened=False, raw_shot_records_available=0,
        reported_chemical_extractions=dict(cibao=54, modoetia=36),
        observations_sha256=sha(canonical(observations)))


def features(rows, arm):
    require(arm in ARMS, 'unknown arm')
    # No response, EY, SD, grind or coffee offset is read here.
    tau = np.array([float(o['tau_s']) for o in rows], dtype=np.float64)
    pressure = np.array([float(o['nominal_pressure_bar']) for o in rows], dtype=np.float64)
    temp = np.array([float(o['temperature_degC']) for o in rows], dtype=np.float64)
    require(np.all(np.isfinite(tau)) and np.all(tau > 0) and
            np.all(np.isfinite(pressure)) and np.all(pressure > 0) and
            np.all(np.isfinite(temp)), 'invalid reported predictor')
    values = dict(xD=np.log(tau/30), xR=np.log(pressure/9), xT=(temp-91.9)/1.5)
    return np.column_stack([values[k] for k in FEATURES[arm]]) if FEATURES[arm] else np.empty((len(rows), 0))


def weights_checked(weights, n):
    w = np.asarray(weights, dtype=np.float64)
    require(w.shape == (n,) and np.all(np.isfinite(w)) and np.all(w >= 0)
            and np.isfinite(w.sum()) and w.sum() > 0, 'invalid weights')
    return w


def fit(train, target, arm, weights):
    """One unrestricted fit, with source-only transforms and independent QR check."""
    w = weights_checked(weights, len(train))
    active = w > 0
    x, xt = features(train, arm), features(target, arm)
    y = np.array([float(o['tds_mean_pct']) for o in train], dtype=np.float64)
    require(np.all(np.isfinite(y)), 'nonfinite source TDS')
    center = np.average(x[active], weights=w[active], axis=0)
    scale = np.sqrt(np.average((x[active]-center)**2, weights=w[active], axis=0))
    require(np.all(np.isfinite(center)) and np.all(np.isfinite(scale)) and np.all(scale > 0),
            'zero/nonfinite training feature scale')
    source = np.column_stack((np.ones(len(train)), (x-center)/scale))
    query = np.column_stack((np.ones(len(target)), (xt-center)/scale))
    weighted = source[active]*np.sqrt(w[active, None])
    response = y[active]*np.sqrt(w[active])
    u, singular, vt = np.linalg.svd(weighted, full_matrices=False)
    threshold = np.finfo(float).eps*max(weighted.shape)*singular[0]
    rank = int(np.count_nonzero(singular > threshold))
    require(rank == source.shape[1], 'required coefficient rank failure')
    coefficient = vt.T @ ((u.T @ response)/singular)
    if arm == 'N':
        coefficient = np.array([np.average(y[active], weights=w[active])])
    q, r = np.linalg.qr(weighted, mode='reduced')
    qr = np.linalg.solve(r, q.T @ response)
    both = np.vstack((source, query))
    predicted = both @ coefficient
    alternate = both @ qr
    slopes = coefficient[1:]/scale
    intercept = coefficient[0]-center @ slopes
    mapped = intercept+np.vstack((x, xt)) @ slopes
    allowance = 1e-9*np.maximum(1, np.abs(predicted))
    require(np.all(np.isfinite(predicted)) and np.all(np.isfinite(mapped)) and
            np.all(np.isfinite(alternate)), 'nonfinite prediction/coefficient inverse map')
    require(np.all(np.abs(predicted-alternate) <= allowance), 'SVD/QR prediction disagreement')
    require(np.all(np.abs(predicted-mapped) <= allowance), 'coefficient inverse-map disagreement')
    sse = float(np.sum(w[active]*(predicted[:len(train)][active]-y[active])**2))
    require(np.isfinite(sse), 'nonfinite training SSE')
    low, high = x[active].min(axis=0), x[active].max(axis=0)
    flags = ((xt < low) | (xt > high)).tolist()
    diag = dict(arm=arm, coefficients=[float(intercept), *slopes.tolist()],
        feature_names=list(FEATURES[arm]), scaled_coefficients=coefficient.tolist(),
        center=center.tolist(), scale=scale.tolist(), rank=rank, rank_threshold=float(threshold),
        singular_values=singular.tolist(), condition_number=float(singular[0]/singular[-1]),
        weighted_shape=list(weighted.shape), training_sse=sse, training_weight=float(w.sum()),
        qr_max_difference=float(np.max(np.abs(predicted-alternate))),
        inverse_max_difference=float(np.max(np.abs(predicted-mapped))),
        source_ranges=list(zip(low.tolist(), high.tolist())), marginal_extrapolation=flags,
        outside_physical_range=((predicted[len(train):] < 0) | (predicted[len(train):] > 100)).tolist(),
        prediction_allowances=allowance[len(train):].tolist())
    return predicted[len(train):], diag


def nesting(diags):
    for a, b in [('D3', 'T2'), ('R3', 'T2'), ('T2', 'N')]:
        x, y = diags[a]['training_sse'], diags[b]['training_sse']
        require(x <= y+1e-12*max(1, y), 'nested training SSE failure: '+a+'/'+b)


def multiplicities(n, k):
    return [v for v in itertools.product(range(n+1), repeat=k) if sum(v) == n]


def combinations(rows):
    result = []
    for vectors in itertools.product(*(multiplicities(n, len(g)) for _, g, n in STRATA)):
        freq = math.prod(math.factorial(n)//math.prod(math.factorial(v) for v in vector)
                         for (_, _, n), vector in zip(STRATA, vectors))
        mapping = {(coffee, grind): v for (coffee, grinds, _), vector in zip(STRATA, vectors)
                   for grind, v in zip(grinds, vector)}
        weights = [mapping[(o['coffee_id'], o['grind_id'])] for o in rows]
        require([sum(w for o, w in zip(rows, weights) if o['coffee_id'] == c)
                 for c in COFFEES] == [18, 12], 'resampling condition weight totals')
        result.append(dict(index=len(result), vectors=[list(v) for v in vectors],
                           frequency=freq, weights=weights))
    require(len(result) == 300 and sum(r['frequency'] for r in result) == 2916,
            'exact enumeration accounting')
    return result


def deletions(rows):
    groups = list(dict.fromkeys((o['coffee_id'], o['grind_id']) for o in rows))
    result = [dict(kind='block', label=c+'/'+g,
                   removed=[i for i, o in enumerate(rows) if (o['coffee_id'], o['grind_id']) == (c, g)])
              for c, g in groups]
    result += [dict(kind='condition', label=o['source_condition_id'], removed=[i])
               for i, o in enumerate(rows)]
    require(len(groups) == 8 and len(result) == 38, 'deletion membership accounting')
    return result


def metrics(rows, predictions, weights):
    w = weights_checked(weights, len(rows))
    y = np.array([float(o['tds_mean_pct']) for o in rows])
    require(np.all(np.isfinite(y)), 'nonfinite target TDS')
    scores = {}
    for arm in ARMS:
        pred = np.asarray(predictions[arm])
        require(pred.shape == y.shape and np.all(np.isfinite(pred)), 'prediction coverage')
        error = pred-y
        parts = {}
        for c in COFFEES:
            ids = np.array([o['coffee_id'] == c for o in rows])
            wc = weights_checked(w[ids], int(ids.sum()))
            parts[c] = dict(rmse=float(np.sqrt(np.average(error[ids]**2, weights=wc))),
                            mae=float(np.average(np.abs(error[ids]), weights=wc)),
                            bias=float(np.average(error[ids], weights=wc)))
        parts['aggregate'] = dict(rmse=float(np.sqrt(np.mean([p['rmse']**2 for p in parts.values()]))),
            mae=float(np.mean([p['mae'] for p in parts.values()])),
            bias=float(np.mean([p['bias'] for p in parts.values()])))
        scores[arm] = parts
    return scores


def contrast(a, b):
    return dict(delta=a-b, gain=None if b == 0 else 1-a/b)


def intervals(values, frequencies):
    require(len(values) == len(frequencies), 'interval length mismatch')
    if any(v is None for v in values):
        return None
    require(all(isinstance(f, int) and f > 0 for f in frequencies), 'invalid frequency')
    x = np.repeat(np.asarray(values, dtype=np.float64), frequencies)
    require(np.all(np.isfinite(x)), 'nonfinite interval values')
    return np.quantile(x, [.025, .975], method='linear').tolist()


def grade(value, lower=.10, upper=.25):
    return None if value is None else ('worse' if value < 0 else 'small' if value < lower
                                     else 'moderate' if value < upper else 'large')


def grade_set(ci, lower=.10, upper=.25):
    if ci is None:
        return None
    lo, hi = ci
    return [g for g, ok in [('worse', lo < 0), ('small', hi >= 0 and lo < lower),
            ('moderate', hi >= lower and lo < upper), ('large', hi >= upper)] if ok]


def summarize(point, sampled, frequencies):
    scores, contrasts = {}, {}
    for arm in ARMS:
        scores[arm] = {s: {m: dict(point=point[arm][s][m], interval=intervals(
            [v[arm][s][m] for v in sampled], frequencies)) for m in ('rmse', 'mae', 'bias')}
            for s in ('aggregate', *COFFEES)}
    for a, b in PAIRS:
        contrasts[a+'/'+b] = {}
        for scope in ('aggregate', *COFFEES):
            p = contrast(point[a][scope]['rmse'], point[b][scope]['rmse'])
            draws = [contrast(v[a][scope]['rmse'], v[b][scope]['rmse']) for v in sampled]
            ci = {m: intervals([d[m] for d in draws], frequencies) for m in ('delta', 'gain')}
            changes = [dict(lower=lo, upper=hi, point=grade(p['gain'], lo, hi),
                            interval=grade_set(ci['gain'], lo, hi))
                       for lo, hi in itertools.product((.075, .10, .125), (.1875, .25, .3125))]
            contrasts[a+'/'+b][scope] = dict(point=p, interval=ci, point_grade=grade(p['gain']),
                interval_grades=grade_set(ci['gain']), boundary_checks=changes,
                undefined_combinations=sum(d['gain'] is None for d in draws),
                undefined_frequency=sum(f for d, f in zip(draws, frequencies) if d['gain'] is None))
    return scores, contrasts


def decisions(point, sampled, frequencies):
    ci = intervals([v['D3']['aggregate']['rmse']-v['R3']['aggregate']['rmse'] for v in sampled], frequencies)
    primary = ('DURATION_OBSERVER_LOWER_CONDITIONAL_TDS_LOSS' if ci[1] < 0 else
               'PRESSURE_OBSERVER_LOWER_CONDITIONAL_TDS_LOSS' if ci[0] > 0 else
               'DURATION_PRESSURE_COMPARISON_UNRESOLVED')
    checks = {}
    for arm in ('D3', 'R3'):
        checks[arm] = {}
        for other in ARMS:
            if other == arm:
                continue
            deltas = [contrast(v[arm]['aggregate']['rmse'], v[other]['aggregate']['rmse']) for v in sampled]
            bound = intervals([d['delta'] for d in deltas], frequencies)
            checks[arm][other] = dict(delta_interval=bound,
                gain_interval=intervals([d['gain'] for d in deltas], frequencies),
                aggregate_pass=bound[1] < 0, resolved_adverse=bound[0] > 0,
                adverse_directions=[c for c in COFFEES if point[arm][c]['rmse'] > point[other][c]['rmse']])
    selected = [a for a in checks if all(v['aggregate_pass'] and not v['adverse_directions']
                                        for v in checks[a].values())]
    return dict(primary=primary, overall='CONDITIONAL_PREFERENCE_OVER_TESTED_REFERENCES' if selected
                else 'NO_CONDITIONAL_OBSERVER_PREFERENCE', selected=selected, requirements=checks)


class Executor:
    """Durable per-fit starts/finishes; a campaign cannot be silently restarted."""
    def __init__(self, output, seconds=1800):
        self.output, self.seconds = Path(output), seconds
        self.clock = None
        self.started = self.finished = 0
        require(not (self.output/'EXECUTION.jsonl').exists(), 'execution already exists; no reset/retry')

    def event(self, data):
        with (self.output/'EXECUTION.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(canonical(data).decode()+'\n')
            stream.flush()

    def check(self):
        if self.clock is not None:
            require(time.monotonic()-self.clock <= self.seconds, 'scientific computation budget exhausted')

    def fit(self, train, target, arm, weights, label):
        if self.clock is None:
            self.clock = time.monotonic()
        self.check()
        self.started += 1
        self.event(dict(event='start', fit=self.started, arm=arm, label=label, epoch=time.time()))
        try:
            pred, diag = fit(train, target, arm, weights)
            self.check()
        except Exception as error:
            self.event(dict(event='failure', fit=self.started, error=str(error)))
            raise
        self.finished += 1
        self.event(dict(event='finish', fit=self.started, epoch=time.time()))
        return pred, diag


def evaluate(rows, weights, executor, label):
    predictions = {a: np.empty(len(rows)) for a in ARMS}
    folds = []
    w = weights_checked(weights, len(rows))
    for coffee in COFFEES:
        train_ids = [i for i, o in enumerate(rows) if o['coffee_id'] == coffee]
        target_ids = [i for i, o in enumerate(rows) if o['coffee_id'] != coffee]
        train, target = [rows[i] for i in train_ids], [rows[i] for i in target_ids]
        diags = {}
        for arm in ARMS:
            predictions[arm][target_ids], diags[arm] = executor.fit(train, target, arm, w[train_ids], label+'/'+coffee)
        nesting(diags)
        folds.append(dict(source=coffee, training=[o['source_condition_id'] for o in train],
                          evaluation=[o['source_condition_id'] for o in target], diagnostics=diags))
    return dict(predictions={a: p.tolist() for a, p in predictions.items()}, folds=folds,
                scores=metrics(rows, predictions, w), weights=w.tolist())


def influence(point, results):
    output = {}
    for a, b in PAIRS:
        output[a+'/'+b] = {}
        for scope in ('aggregate', *COFFEES):
            base = contrast(point[a][scope]['rmse'], point[b][scope]['rmse'])
            output[a+'/'+b][scope] = {}
            for kind in ('block', 'condition'):
                values = [(r['label'], contrast(r['result']['scores'][a][scope]['rmse'],
                                               r['result']['scores'][b][scope]['rmse']))
                          for r in results if r['kind'] == kind]
                output[a+'/'+b][scope][kind] = dict(
                    delta_range=[min(v['delta'] for _, v in values), max(v['delta'] for _, v in values)],
                    gain_range=None if any(v['gain'] is None for _, v in values) else
                        [min(v['gain'] for _, v in values), max(v['gain'] for _, v in values)],
                    ties=[label for label, v in values if v['delta'] == 0],
                    reversals=[label for label, v in values if v['delta']*base['delta'] < 0])
    return output


def run(root, output):
    """One frozen real campaign. All outputs are private and no old campaign runs."""
    root, output = Path(root), Path(output)
    frozen = json.loads((output/'FREEZE.json').read_text())
    for name, expected in frozen['files'].items():
        require(sha((root/name).read_bytes()) == expected, 'frozen implementation drift: '+name)
    rows, authentication = authenticate(root)
    require(sha(canonical(rows)) == frozen['observations_sha256'], 'frozen observation drift')
    cases = combinations(rows)
    require(sha(canonical(cases)) == frozen['combinations_sha256'], 'frozen enumeration drift')
    executor = Executor(output)
    completed, represented, failure = 0, 0, None
    samples, deletion_results = [], []
    stage = 'point'
    try:
        point = evaluate(rows, np.ones(len(rows)), executor, stage)
        save(output/'POINT.json', point)
        for case in cases:
            stage = 'combination/'+str(case['index'])
            save(output/'CURRENT_CASE.json', dict(stage=stage, case=case))
            result = evaluate(rows, case['weights'], executor, stage)
            if all(w == 1 for w in case['weights']):
                for arm in ARMS:
                    diff = np.abs(np.array(result['predictions'][arm])-point['predictions'][arm])
                    require(np.all(diff <= 1e-9*np.maximum(1, np.abs(point['predictions'][arm]))),
                            'all-one point reproduction failed')
            record = dict(**case, result=result)
            with (output/'COMBINATIONS.jsonl').open('a') as stream:
                stream.write(canonical(record).decode()+'\n')
            samples.append(result['scores'])
            completed += 1
            represented += case['frequency']
        for deletion in deletions(rows):
            stage = deletion['kind']+'/'+deletion['label']
            keep = [o for i, o in enumerate(rows) if i not in deletion['removed']]
            result = evaluate(keep, np.ones(len(keep)), executor, stage)
            deletion_results.append(dict(**deletion, result=result))
            save(output/'DELETIONS.json', deletion_results)
        require(executor.finished == 2712, 'required fit accounting')
        frequencies = [c['frequency'] for c in cases]
        scores, contrasts = summarize(point['scores'], samples, frequencies)
        decision = decisions(point['scores'], samples, frequencies)
        executor.check()
        result = dict(task=TASK, status='COMPLETED_PRIVATE', pins=PINS,
            freeze_sha256=sha((output/'FREEZE.json').read_bytes()), authentication=authentication,
            point=point, scores=scores, contrasts=contrasts, decisions=decision,
            influence=influence(point['scores'], deletion_results),
            counts=dict(requested=300, completed=completed, failed=0, unattempted=0,
                        represented_frequency=represented, requested_frequency=2916,
                        fits=executor.finished, fits_per_arm=678, block_deletions=8, condition_deletions=30),
            scientific_seconds=time.monotonic()-executor.clock)
        save(output/'RESULT_SCIENCE.json', result)
        return result
    except Exception as error:
        failure = dict(status='INCOMPLETE', stage=stage, blocker=str(error), requested=300,
            completed=completed, failed=int(stage.startswith('combination/')),
            unattempted=300-completed-int(stage.startswith('combination/')),
            represented_frequency=represented, started_fits=executor.started, finished_fits=executor.finished)
        save(output/'FAILURE.json', failure)
        raise

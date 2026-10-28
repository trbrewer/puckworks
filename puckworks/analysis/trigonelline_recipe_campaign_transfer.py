"""Frozen, retrospective trigonelline recipe campaign comparison.

Research only. Original observations and all numerical outputs stay outside Git.
The predecessor supplies authenticated source projection and pure quadrature only;
its executor, schemas, deadlines and counters are never modified or invoked.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
import fcntl
import hashlib
import json
import os
from pathlib import Path
import time

import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares
from scipy.special import expit, logit

from . import conditional_trigonelline_delivery as geometry

TASK = 'SCI-MD-TRIGONELLINE-RECIPE-CAMPAIGN-TRANSFER-001'
SCHEMA = 'trigonelline-recipe-campaign-transfer/1'
ARMS = ('R18', 'Q18', 'D0', 'K0')
NONLINEAR = ARMS[:3]
LAMBDAS = (.0001, .01, 1., 100.)
FIT_GROUPS = tuple(f'FIT-C{i:02d}' for i in range(1, 16))
TARGET_GROUPS = ('PRED-C01', 'PRED-C02', 'PRED-C05', 'PRED-C06')
FRACTIONS = (3, 5, 7, 10)
FIT_RECIPES = ((1.4, 80., 1.), (1.4, 98., 1.), (2., 80., 1.), (2., 98., 1.),
               (1.4, 80., 3.), (1.4, 98., 3.), (2., 80., 3.), (2., 98., 3.),
               (1.7, 89., 2.), (1.7, 89., 1.), (1.7, 89., 3.), (1.4, 89., 2.),
               (2., 89., 2.), (1.7, 80., 2.), (1.7, 98., 2.))
TARGET_RECIPES = ((1.7, 86., 2.), (1.7, 92., 2.), (1.7, 90., 1.7), (1.7, 90., 2.3))
OLD_FREEZE = '6f1b1afc73615eafb9b463b49089a1069d60179ea96b2a02a2951a9ec22f0b12'
OLD_PROJECTION = '58766702caa144e7641e87dca4d2d13e541459f276bb59c7cf4891261a91015e'
PINS = {'main': '21669a427145194e1f4003e3cf1b97dedefe2679',
        'base': '9f311e70bd08ae16387c9ac40aa9c71595f95a65',
        'parent': '7c04a644c7b74be53ffb1cf611ebfb7ab06c5fd2',
        'ewp': 'f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516',
        'scientific_baseline': 'de31200f272711ca6b2e9fc5dc7c4881c406ab56'}
LIMITS = {'iterative_starts': 18684, 'analytic_fits': 2016, 'calls_per_start': 8000,
          'science_seconds': 9000, 'qualification_seconds': 1800, 'session_seconds': 14400,
          'draws': 2000, 'workers': 1, 'blas_threads': 1}
RIGHTS = 'Pannusch/Schmieder; CC-BY-NC-3.0; Mendeley 10.17632/y2tz67f6ry.1'
ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/sci_md_trigonelline_recipe_campaign_transfer_001'


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def identity(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return geometry.strict_json(Path(path).read_text())


def write(path, value):
    with Path(path).open('x') as stream:
        stream.write(canonical(value) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


class Stop(RuntimeError):
    """A required qualification/fit failed; no retries or reduced campaign."""


def require(condition, reason):
    if not condition:
        raise Stop(reason)


def recipe_join(designs, register, prediction_register):
    """Authenticate condition-specific originals and every physical-shot join."""
    expected = dict(zip(FIT_GROUPS, FIT_RECIPES)) | dict(zip(TARGET_GROUPS, TARGET_RECIPES))
    result, inspected = {}, []
    for label, entries in designs.items():
        for d in entries:
            cid = f"{label}-C{d['exp']:02d}"
            if cid not in expected:
                continue
            require(cid not in result, 'DUPLICATE_RECIPE')
            value = (d['grind'], d['temp0'], d['flow0'])
            require(value == expected[cid] and d['dose'] == 20 and
                    d['temp0'] == d['temp1'] and d['flow0'] == d['flow1'],
                    'SOURCE_RECIPE_IDENTITY_MISMATCH:' + cid)
            shots = [r for r in register if r['condition_id'] == cid]
            require(len(shots) == 3 and {r['shot_id'] for r in shots} ==
                    {cid.replace('-C', '-E') + f'-R{j}' for j in (1, 2, 3)},
                    'PHYSICAL_SHOT_RECIPE_JOIN:' + cid)
            for r in shots:
                require(int(r['source_experiment_id']) == d['exp'] and
                        int(r['physical_replicate_id']) == int(r['shot_id'][-1]) and
                        r['campaign_id'] == ('FIT_2021_12' if label == 'FIT' else 'PREDICTION_2022_03') and
                        r['machine'] == 'DE1' and float(r['dose_g']) == 20 and
                        float(r['grind_setting']) == d['grind'], 'SHOT_CONTEXT_MISMATCH:' + cid)
                if label == 'FIT':
                    require(float(r['nominal_temperature_program_id'][6:-1]) == d['temp0'] and
                            float(r['nominal_flow_program_id'][6:-4]) == d['flow0'],
                            'FIT_PROGRAM_IDENTITY_MISMATCH:' + cid)
                inspected.append({k: r[k] for k in ('shot_id', 'condition_id', 'collection_date',
                                  'coffee_product', 'coffee_lot_id', 'roast_batch_id', 'source_id')})
            if label == 'PRED':
                matches = [r for r in prediction_register if r['condition_id'] == cid]
                require(len(matches) == 1, 'PRED_PROGRAM_IDENTITY_MISSING')
                r = matches[0]
                require([float(r[k]) for k in ('temperature_start_C', 'temperature_end_C',
                        'flow_start_mL_s', 'flow_end_mL_s')] ==
                        [d['temp0'], d['temp1'], d['flow0'], d['flow1']], 'PRED_PROGRAM_MISMATCH')
            result[cid] = list(value)
    require(set(result) == set(expected), 'ALL_FIFTEEN_FIT_AND_FOUR_TARGET_RECIPES_REQUIRED')
    return result, inspected


def support_guards(training, queries, folds):
    groups = sorted({s['group'] for s in training})
    require(groups == list(FIT_GROUPS) and len(training) == 45, 'ALL_45_ORIGINAL_SHOTS_REQUIRED')
    b = {}
    for s in training:
        require(s['windows'] and all(w['start_kg'] >= sum(s['early_values']) and
                w['end_kg'] > w['start_kg'] for w in s['windows']), 'SOURCE_PREFIX_BOUNDARY')
        b[s['shot']] = max(w['end_kg'] for w in s['windows'])
    require(len(b) == 45 and sum(len(s['windows']) for s in training) == 177,
            'ORIGINAL_QUALIFIED_DENOMINATORS')
    minima, deletions = {}, {}
    for g in groups:
        members = [s for s in training if s['group'] == g]
        require(len(members) == 3 and sum(len(s['windows']) >= 3 for s in members) >= 2,
                'DESIGN_SOURCE_SUPPORT:' + g)
        minima[g] = min(b[s['shot']] for s in members)
        deletions[g] = max(b[s['shot']] for s in training if s['group'] != g)
    floor = max(minima.values())
    require(len(queries) == 48 and {q['condition'] for q in queries} == set(TARGET_GROUPS) and
            len({q['shot'] for q in queries}) == 12, 'ALL_48_TARGET_WINDOWS_REQUIRED')
    require(all(q['supported'] and q['start_kg'] >= sum(q['early_values']) and
                q['b1'] > q['start_kg'] for q in queries), 'TARGET_PREFIX_BOUNDARY')
    target_max = max(q['b1'] for q in queries)
    require(floor >= target_max, 'BOOTSTRAP_SUPPORT_FLOOR_FAILED')
    require(all(v >= target_max for v in deletions.values()), 'SOURCE_DELETION_SUPPORT_FAILED')
    require(len(folds) == 15 and {f['group'] for f in folds} == set(groups), 'FOLD_MEMBERSHIPS')
    for f in folds:
        held = [s for s in training if s['group'] == f['group']]
        expected = [[s['shot'], w['fraction']] for s in held for w in s['windows']
                    if w['end_kg'] <= deletions[f['group']]]
        require([list(v) for v in f['support']] == expected and f['domain_kg'] == deletions[f['group']],
                'FROZEN_COORDINATE_MASK_MISMATCH')
        require(set(f['held_shots']) == {s['shot'] for s in held} and
                set(f['training_shots']) == {s['shot'] for s in training if s not in held},
                'FOLD_SHOT_MEMBERSHIP_MISMATCH')
        require(all(any(x[0] == s['shot'] for x in expected) for s in held),
                'HELD_SHOT_WITHOUT_SUPPORT')
    return {'B_floor_kg': floor, 'target_maximum_kg': target_max,
            'bootstrap_margin_kg': floor-target_max, 'per_design_minima_kg': minima,
            'deletion_domains_kg': deletions,
            'deletion_margins_kg': {g: v-target_max for g, v in deletions.items()},
            'held_counts': {f['group']: len(f['support']) for f in folds},
            'held_total': sum(len(f['support']) for f in folds)}


def qualify(out, old_out, started_unix):
    """Read-only authentication; never invokes the historical campaign CLI."""
    from . import pannusch_conditional_trigonelline_delivery as source
    from tools.pannusch2024_reconstruct import doe_conditions
    require(time.time()-started_unix < LIMITS['qualification_seconds'], 'INPUT_QUALIFICATION_TIME_CAP')
    out, old_out = source.private_directory(out), source.private_directory(old_out)
    out.mkdir(parents=True, exist_ok=False, mode=0o700)
    require(digest(old_out/'freeze.json') == OLD_FREEZE == digest(source.DOC/'FREEZE.json'),
            'OLD_FREEZE_AUTHORITY_DRIFT')
    frozen = read(old_out/'freeze.json')
    require(frozen['producer_commit'] == PINS['scientific_baseline'], 'OLD_PRODUCER_DRIFT')
    for n, h in frozen['artifacts'].items():
        require(digest(old_out/n) == h, 'OLD_ARTIFACT_DRIFT:' + n)
    completion = read(source.DOC/'SCORE_COMPLETION.json')
    require(completion['freeze_sha256'] == OLD_FREEZE, 'OLD_SCORE_FREEZE_DRIFT')
    for n, h in completion['files'].items():
        require(digest(old_out/n) == h, 'OLD_SCORE_ARTIFACT_DRIFT:' + n)
    for arm in ('TR-D0', 'TR-K0'):
        geometry.Model.load(old_out/'models'/f'{arm}.json')
    paths, authority = source.qualified_sources()
    coords, rows = source.source_geometry.coordinates(paths), source.source_geometry.all_rows()
    p = source.build_projections(coords, rows, source.source_geometry.condition_groups())
    require(source.identity(p) == OLD_PROJECTION, 'ACCEPTED_PROJECTION_DRIFT')
    for n in ('training', 'development_support'):
        require(source.identity(p[n]) == source.identity(read(old_out/(n+'.json'))),
                'BOUND_PREPARATION_DRIFT:' + n)
    q = [r for r in p['queries'] if r['condition'] in TARGET_GROUPS]
    require(source.original_reconciliation(paths, p['fit_slots']+q, rows) == 228,
            'ORIGINAL_ANALYTE_RECONCILIATION')
    designs = {'FIT': doe_conditions(paths['P24-DOE-FIT'], 15),
               'PRED': [d for d in doe_conditions(paths['P24-DOE-PRED'], 8, True)
                        if d['exp'] in (1, 2, 5, 6)]}
    recipes, inspection = recipe_join(designs, source.source.rows(source.source.DATA/'experiment_register.csv'),
                                     source.source.rows(source.source.DATA/'prediction_conditions.csv'))
    for label in ('FIT', 'PRED'):
        ws = source.source.workbook(paths['P24-DOE-'+label])['ExpSheet']
        headers = [str(ws.cell(1, j).value).replace('\\n', ' ').replace('\n', ' ') for j in range(1, 13)]
        tokens = ('Flow_0', 'Flow_E', 'T_0', 'T_E') if label == 'PRED' else ('Flow (ml/s)', 'Temp (°C)')
        require(all(any(t in h for h in headers) for t in tokens), 'RECIPE_HEADERS_CHANGED')
        for d in designs[label]:
            require(abs(float(ws.cell(3*(d['exp']-1)+2, 8).value)*d['flow0']-60) <= 1e-9,
                    'SOURCE_COLLECTION_DESIGN_CONVENTION')
    training = [dict(s, recipe=recipes[s['group']]) for s in p['training']]
    for r in q:
        early = p['early_inputs'][r['shot']]
        a, allowance = source.source_geometry.source_query_start(r, type('Anchor', (), {'b_anchor': sum(early)})())
        r.update(early_values=early, recipe=recipes[r['condition']], start_kg=a,
                 coordinate_allowance_kg=allowance)
    guards = support_guards(training, q, p['development_support'])
    require(p['source_counts']['fit_reasons'] == {'UNAVAILABLE_MEASURED_MASS_PREFIX': 3}, 'SOURCE_SLOT_STATUS')
    records = {'training.json': training, 'queries.json': q, 'fit_slots.json': p['fit_slots'],
               'folds.json': p['development_support'], 'coordinates.json': p['coordinates'],
               'recipes.json': recipes, 'recipe_originals.json': designs, 'inspection.json': inspection,
               'support.json': guards, 'sources.json': authority,
               'historical_authentication.json': {'freeze': OLD_FREEZE, 'artifacts': frozen['artifacts'],
                   'score_completion': completion, 'original_reconciliations': 228,
                   'projection': OLD_PROJECTION, 'historical_models_authenticated': True,
                   'private_locator_inspected': True, 'old_preparation_files_authenticated': True}}
    for n, v in records.items():
        write(out/n, v)
    require(time.time()-started_unix < LIMITS['qualification_seconds'], 'INPUT_QUALIFICATION_TIME_CAP')
    write(out/'QUALIFIED.json', {'task': TASK, 'status': 'PASS', 'completed_unix': time.time(),
         'started_unix': started_unix, 'elapsed_seconds': time.time()-started_unix,
         'files': {n: digest(out/n) for n in records}, 'augmented_projection_sha256': identity(records),
         'rights': RIGHTS})
    return guards


def training_weights(records, multiplicities):
    c = np.asarray(multiplicities)
    require(c.shape == (len(records),) and np.isfinite(c).all() and
            np.all(c >= 0) and np.all(c == np.floor(c)), 'NONNEGATIVE_INTEGER_MULTIPLICITIES_REQUIRED')
    groups = sorted({r['group'] for r, m in zip(records, c) if m > 0})
    require(bool(groups), 'EMPTY_TRAINING')
    totals = {g: sum(m for r, m in zip(records, c) if r['group'] == g) for g in groups}
    sw = np.array([m/(len(groups)*totals[r['group']]) if m else 0. for r, m in zip(records, c)])
    return sw


def added_raw(arm, x, recipes):
    if arm == 'R18':
        return np.asarray(recipes, dtype=np.float64)
    if arm == 'Q18':
        return np.c_[x[:, 0]**2, x[:, 0]*x[:, 1], x[:, 1]**2]
    return np.empty((len(x), 0), dtype=np.float64)


@dataclass(frozen=True)
class Model:
    arm: str
    parameters: list
    means: list
    extra_mean: list
    extra_sd: list
    minima: list
    maxima: list
    extra_min: list
    extra_max: list
    domain: float
    regularization: float | None
    feature_rank: int
    feature_condition: float | None
    training_hash: str
    schema: str = SCHEMA
    species: str = 'trigonelline'

    def __post_init__(self):
        require(self.schema == SCHEMA and self.species == 'trigonelline' and self.arm in ARMS,
                'TASK_LOCAL_MODEL_SCHEMA')
        require(len(self.parameters) == {'R18': 18, 'Q18': 18, 'D0': 15, 'K0': 1}[self.arm] and
                np.isfinite(self.parameters).all() and np.isfinite(self.domain) and self.domain > 0,
                'MODEL_PARAMETER_COUNT_OR_FINITE_DOMAIN')
        require((self.arm == 'K0' and self.regularization is None and self.parameters[0] >= 0) or
                (self.arm in NONLINEAR and self.regularization in LAMBDAS and
                 np.max(np.abs(self.parameters)) <= 20), 'MODEL_BOUNDS_OR_LAMBDA')
        k = 3 if self.arm in ('R18', 'Q18') else 0
        require(len(self.extra_mean) == len(self.extra_sd) == k and
                (not k or np.all(np.asarray(self.extra_sd) > 0)), 'MODEL_EXTRA_TRANSFORM')

    def logits(self, inputs, recipes):
        x = (np.asarray(inputs, dtype=np.float64)-self.means)/.01
        if self.arm == 'K0':
            return np.zeros((len(x), 5))
        values = np.c_[np.ones(len(x)), x] @ np.asarray(self.parameters[:15]).reshape(5, 3).T
        if self.arm in ('R18', 'Q18'):
            z = (added_raw(self.arm, x, recipes)-self.extra_mean)/self.extra_sd
            values += (z @ self.parameters[15:])[:, None]
        require(np.isfinite(values).all(), 'NONFINITE_LOGITS')
        return values


class Problem:
    def __init__(self, records, arm, regularization, multiplicities=None):
        require(arm in ARMS, 'DECLARED_ARM')
        require(regularization in LAMBDAS if arm != 'K0' else regularization is None, 'DECLARED_LAMBDA')
        require(records and all(r['shot'].startswith('FIT-') and r['group'].startswith('FIT-')
                for r in records), 'FIT_ONLY_TRAINING')
        c = np.ones(len(records), int) if multiplicities is None else np.asarray(multiplicities)
        all_weights = training_weights(records, c)
        self.records = [r for r, m in zip(records, c) if m > 0]
        sw = all_weights[c > 0]
        self.arm, self.lam = arm, regularization
        raw = np.asarray([s['early_values'] for s in self.records], dtype=np.float64)
        require(raw.shape == (len(self.records), 2) and np.isfinite(raw).all() and np.all(raw > 0),
                'EARLY_MASS_INPUTS')
        self.means = sw @ raw
        x = (raw-self.means)/.01
        self.features = np.c_[np.ones(len(raw)), x]
        extra = added_raw(arm, x, [s['recipe'] for s in self.records])
        self.extra_mean = sw @ extra
        self.extra_sd = np.sqrt(sw @ (extra-self.extra_mean)**2)
        require(np.isfinite(self.extra_sd).all() and np.all(self.extra_sd > 0) and
                np.all(np.ptp(extra, axis=0) > 0), 'NONFINITE_OR_ZERO_EXTRA_SCALE')
        self.z = (extra-self.extra_mean)/self.extra_sd
        matrix = np.c_[self.features, self.z]
        self.rank = int(np.linalg.matrix_rank(matrix))
        cond = float(np.linalg.cond(matrix))
        self.condition = cond if np.isfinite(cond) else None
        self.domain = max(w['end_kg'] for s in self.records for w in s['windows'])
        self.windows = [w for s in self.records for w in s['windows']]
        require(all(s['windows'] and all(w['start_kg'] >= sum(s['early_values']) and
                0 <= w['q'] and np.isfinite(w['q']) and w['mass_kg'] > 0 and
                w['end_kg'] > w['start_kg'] for w in s['windows']) for s in self.records),
                'QUALIFIED_TRAINING_WINDOWS')
        self.row_shots = np.array([i for i, s in enumerate(self.records) for w in s['windows']], int)
        self.weights = np.array([sw[i]*w['mass_kg']/sum(v['mass_kg'] for v in s['windows'])
                                for i, s in enumerate(self.records) for w in s['windows']])
        self.q = np.array([w['q'] for w in self.windows])
        self.widths = np.array([w['end_kg']-w['start_kg'] for w in self.windows])
        self.geometry = geometry.Geometry([w['start_kg'] for w in self.windows],
                           [w['end_kg'] for w in self.windows], self.domain, self.domain)
        self.raw, self.extra = raw, extra
        self.training_hash = identity({'records': records, 'multiplicities': c.tolist()})
        initial = float(logit(min(1-1e-8, max(1e-8, float(self.weights @ self.q)))))
        self.starts = []
        for ramp in (-1, 0, 1):
            theta = np.zeros((5, 3))
            theta[:, 0] = initial+ramp*np.linspace(-1, 1, 5)
            v = np.r_[theta.ravel(), np.zeros(self.z.shape[1])]
            require(np.max(np.abs(v)) <= 20, 'INITIALIZATION_OUTSIDE_BOUNDS')
            self.starts.append(v)

    def residual(self, parameters):
        theta = parameters[:15].reshape(5, 3)
        logits = self.features @ theta.T
        if self.z.shape[1]:
            logits += (self.z @ parameters[15:])[:, None]
        predicted = self.geometry.integrate(logits[self.row_shots])/self.widths
        data = 1000/.25*(predicted-self.q)*np.sqrt(self.weights)
        slopes = theta[:, 1:].ravel()
        second = (np.diff(theta, n=2, axis=0)/(.25**2)).ravel()
        base = np.r_[data, slopes*np.sqrt(self.lam/len(slopes)), second*np.sqrt(self.lam/len(second))]
        return np.r_[base, parameters[15:]*np.sqrt(self.lam/3)] if self.z.shape[1] else base

    def model(self, parameters):
        return Model(self.arm, list(map(float, parameters)), self.means.tolist(),
                     self.extra_mean.tolist(), self.extra_sd.tolist(), self.raw.min(axis=0).tolist(),
                     self.raw.max(axis=0).tolist(), self.extra.min(axis=0).tolist(),
                     self.extra.max(axis=0).tolist(), self.domain, self.lam, self.rank,
                     self.condition, self.training_hash)


class Executor:
    """One worker; append-only starts/finishes and one persistent byte per actual call."""
    def __init__(self, out, session_started):
        self.out = Path(out)
        self.lock = (self.out/'worker.lock').open('a')
        fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        require(not (self.out/'execution.jsonl').exists(), 'EXECUTION_ALREADY_STARTED_NO_RETRY')
        self.stream = (self.out/'execution.jsonl').open('x')
        self.calls = (self.out/'residual_calls.bin').open('xb', buffering=0)
        self.started = time.time()
        self.session_started = session_started
        self.starts = self.analytic = self.finished = self.unsuccessful = 0
        self.event({'event': 'CAMPAIGN_START', 'limits': LIMITS, 'started_unix': self.started})

    def event(self, record):
        os.fsync(self.calls.fileno())
        self.stream.write(canonical(dict(record, time_unix=time.time()))+'\n')
        self.stream.flush()
        os.fsync(self.stream.fileno())

    def check(self):
        require(time.time()-self.started < LIMITS['science_seconds'], 'SCIENTIFIC_COMPUTATION_TIME_CAP')
        require(time.time()-self.session_started < LIMITS['session_seconds'], 'SESSION_TIME_CAP')

    def fit(self, records, arm, lam, name, multiplicities=None):
        self.check()
        self.event({'event': 'FIT_PREPARE', 'fit': name, 'arm': arm, 'lambda': lam})
        problem = Problem(records, arm, lam, multiplicities)
        if arm == 'K0':
            require(self.analytic < LIMITS['analytic_fits'], 'ANALYTIC_FIT_CAP')
            self.analytic += 1
            self.event({'event': 'ANALYTIC_START', 'fit': name, 'count': self.analytic})
            model = problem.model([problem.weights @ problem.q])
            self.event({'event': 'ANALYTIC_FINISH', 'fit': name, 'model': asdict(model)})
            return model
        candidates = []
        for index, initial in enumerate(problem.starts):
            self.check()
            require(self.starts < LIMITS['iterative_starts'], 'ITERATIVE_START_CAP')
            self.starts += 1
            start = time.time()
            calls = 0
            self.event({'event': 'START', 'fit': name, 'arm': arm, 'lambda': lam,
                        'index': index, 'start_count': self.starts, 'initial': initial.tolist(),
                        'call_offset': self.calls.tell(), 'training_hash': problem.training_hash})
            def residual(x):
                nonlocal calls
                self.check()
                require(calls < LIMITS['calls_per_start'], 'ACTUAL_RESIDUAL_CALL_CAP')
                calls += 1
                self.calls.write(b'.')
                value = problem.residual(x)
                require(np.isfinite(value).all(), 'NONFINITE_RESIDUAL')
                return value
            try:
                result = least_squares(residual, initial, bounds=(-20., 20.), method='trf',
                    tr_solver='exact', loss='linear', jac='2-point', diff_step=1e-6, x_scale=1.,
                    ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=8000)
                objective = float(result.fun @ result.fun)
                require(np.isfinite(result.x).all() and np.isfinite(objective) and
                        np.all(np.abs(result.x) <= 20), 'NONFINITE_OR_INFEASIBLE_TERMINATION')
                converged = bool(result.success and result.status > 0)
                self.event({'event': 'FINISH', 'fit': name, 'index': index, 'calls': calls,
                            'elapsed_seconds': time.time()-start, 'converged': converged,
                            'status': int(result.status), 'message': str(result.message),
                            'objective': objective, 'parameters': result.x.tolist(),
                            'nfev': int(result.nfev), 'njev': int(result.njev),
                            'boundary_indices': np.flatnonzero(np.abs(result.x) >= 20-1e-7).tolist()})
                self.finished += 1
                self.unsuccessful += int(not converged)
                if converged:
                    candidates.append((objective, index, result.x))
            except Exception as exc:
                self.event({'event': 'FAILED', 'fit': name, 'index': index, 'calls': calls,
                            'exception_type': type(exc).__name__, 'reason': str(exc),
                            'elapsed_seconds': time.time()-start})
                raise
        require(bool(candidates), 'NO_CONVERGED_START:' + name)
        best = min(candidates, key=lambda x: (x[0], x[1]))
        model = problem.model(best[2])
        self.event({'event': 'FIT_SELECTED', 'fit': name, 'index': best[1], 'model': asdict(model)})
        return model


def predict(model, queries):
    inputs = np.asarray([q['early_values'] for q in queries], dtype=np.float64)
    a, b = np.asarray([q['start_kg'] for q in queries]), np.asarray([q['b1'] for q in queries])
    require(np.all(a >= inputs.sum(axis=1)) and np.all(b > a), 'QUERY_PREFIX_OR_WIDTH')
    recipes = [q['recipe'] for q in queries]
    logits = model.logits(inputs, recipes)
    share = model.parameters[0] if model.arm == 'K0' else None
    low = geometry.Geometry(a, b, model.domain, model.domain, 64).integrate(logits, share=share)
    high = geometry.Geometry(a, b, model.domain, model.domain, 128).integrate(logits, share=share)
    knots = np.linspace(0., model.domain, 5)
    x = (inputs-model.means)/.01
    extra = added_raw(model.arm, x, recipes)
    result = []
    for i, q in enumerate(queries):
        cuts = [a[i]]+[v for v in knots if a[i] < v < b[i]]+[b[i]]
        ref = err = 0.
        for left, right in zip(cuts[:-1], cuts[1:]):
            v, e = quad(lambda u: share if share is not None else float(expit(np.interp(u, knots, logits[i]))),
                        left, right, epsabs=1e-14, epsrel=2e-13, limit=200)
            ref += v
            err += e
        fp = 128*np.finfo(float).eps*(b[i]-a[i]+abs(low[i]))
        allowance = max(abs(low[i]-high[i]), abs(low[i]-ref)+err, abs(high[i]-ref)+err)+fp+q['coordinate_allowance_kg']
        require(np.isfinite([low[i], high[i], ref, err, allowance]).all() and allowance <= 1e-9,
                'NUMERICALLY_UNQUALIFIED_INTERVAL')
        flags = [f'm{j+1}' for j in range(2) if not model.minima[j] <= inputs[i, j] <= model.maxima[j]]
        flags += [f'extra{j+1}' for j in range(extra.shape[1]) if not model.extra_min[j] <= extra[i, j] <= model.extra_max[j]]
        result.append({'shot': q['shot'], 'condition': q['condition'], 'fraction': q['fraction'],
             'mass_kg': q['mass_kg'], 'prediction_mg_g': float(1000*low[i]/(b[i]-a[i])),
             'allowance_kg': float(allowance), 'allowance_mg_g': float(1000*allowance/q['mass_kg']),
             'difference_64_128_kg': float(abs(low[i]-high[i])), 'adaptive_difference_kg': float(abs(low[i]-ref)),
             'adaptive_error_kg': float(err), 'floating_point_allowance_kg': float(fp),
             'coordinate_allowance_kg': q['coordinate_allowance_kg'], 'feature_extrapolation': flags})
    return result


def score(predictions, observed, multiplicities=None, conditions=TARGET_GROUPS):
    ids = [(p['shot'], p['fraction']) for p in predictions]
    require(len(ids) == len(set(ids)), 'DUPLICATE_PREDICTION')
    values = {(r['shot'], r['fraction']): r['q']*1000 for r in observed}
    shots = sorted({p['shot'] for p in predictions if p['condition'] in conditions})
    c = np.ones(len(shots), int) if multiplicities is None else np.asarray(multiplicities)
    require(c.shape == (len(shots),) and np.all(c >= 0) and np.all(c == np.floor(c)), 'TARGET_MULTIPLICITIES')
    per_shot, per_condition = {}, {}
    for shot in shots:
        ps = [p for p in predictions if p['shot'] == shot]
        weights = np.array([p['mass_kg'] for p in ps]); weights /= weights.sum()
        errors = np.array([p['prediction_mg_g']-values[(shot, p['fraction'])] for p in ps])
        allowances = np.array([p['allowance_mg_g'] for p in ps])
        bias = float(weights @ errors)
        l1, l2 = float(weights @ allowances), float(np.sqrt(weights @ allowances**2))
        per_shot[shot] = {'condition': ps[0]['condition'], 'L': float(np.sqrt(weights @ errors**2)),
            'MAE': float(weights @ np.abs(errors)), 'bias': bias, 'absolute_shot_bias': abs(bias),
            'L_allowance': l2, 'MAE_allowance': l1, 'bias_allowance': l1,
            'absolute_shot_bias_allowance': l1, 'worst_absolute_error': float(np.max(np.abs(errors))),
            'windows': len(ps)}
    keys = ('L', 'MAE', 'bias', 'absolute_shot_bias', 'L_allowance', 'MAE_allowance',
            'bias_allowance', 'absolute_shot_bias_allowance')
    for group in conditions:
        indices = [i for i, s in enumerate(shots) if per_shot[s]['condition'] == group]
        require(indices and sum(c[i] for i in indices) > 0, 'TARGET_CONDITION_MISSING')
        per_condition[group] = {k: float(np.average([per_shot[shots[i]][k] for i in indices],
                                                  weights=c[indices])) for k in keys}
    aggregate = {k: float(np.mean([v[k] for v in per_condition.values()])) for k in keys}
    return {'aggregate': aggregate, 'conditions': per_condition, 'shots': per_shot}


def held_queries(records, fold):
    mask = {tuple(v) for v in fold['support']}
    return [dict(shot=s['shot'], condition=s['group'], early_values=s['early_values'], recipe=s['recipe'],
                 fraction=w['fraction'], mass_kg=w['mass_kg'], start_kg=w['start_kg'], b1=w['end_kg'],
                 coordinate_allowance_kg=w['coordinate_allowance_kg'])
            for s in records if s['group'] == fold['group'] for w in s['windows']
            if (s['shot'], w['fraction']) in mask]


def select_lambda(candidates):
    require(len(candidates) == 4 and {c['lambda'] for c in candidates} == set(LAMBDAS), 'COMPLETE_LAMBDA_GRID')
    best = min(c['loss'] for c in candidates)
    chosen = max(c['lambda'] for c in candidates if c['loss'] <= best+1e-6)
    low = min(c['loss']-c['allowance'] for c in candidates)
    high = min(c['loss']+c['allowance'] for c in candidates)
    # Sufficient interval check: eligibility of every candidate is invariant.
    for c in candidates:
        eligible = c['loss'] <= best+1e-6
        require((c['loss']+c['allowance'] <= low+1e-6) if eligible else
                (c['loss']-c['allowance'] > high+1e-6), 'NUMERICALLY_UNRESOLVED_LAMBDA_SELECTION')
    return chosen


def tune(records, folds, executor, out):
    selected, all_results = {}, {}
    for arm in NONLINEAR:
        candidates = []
        for lam in LAMBDAS:
            scores = []
            for fold in folds:
                training = [s for s in records if s['group'] != fold['group']]
                model = executor.fit(training, arm, lam, f'tune.{arm}.{lam}.{fold["group"]}')
                queries = held_queries(records, fold)
                predictions = predict(model, queries)
                observed = [dict(shot=s['shot'], fraction=w['fraction'], q=w['q'])
                            for s in records if s['group'] == fold['group'] for w in s['windows']]
                metrics = score(predictions, observed, conditions=(fold['group'],))
                scores.append(metrics['aggregate'])
                write(out/f'tune.{arm}.{lam}.{fold["group"]}.json',
                      {'model': asdict(model), 'predictions': predictions, 'score': metrics})
                executor.check()
            candidates.append({'lambda': lam, 'loss': float(np.mean([s['L'] for s in scores])),
                               'allowance': float(np.mean([s['L_allowance'] for s in scores])),
                               'fold_scores': scores})
        selected[arm] = select_lambda(candidates)
        all_results[arm] = candidates
        print(canonical({'stage': 'tuning', 'arm': arm, 'selected_lambda': selected[arm]}), flush=True)
    write(out/'TUNING.json', {'selected': selected, 'candidates': all_results,
                            'interpretation': 'TRAINING_ONLY_TUNING_DIAGNOSTICS_NOT_NESTED_VALIDATION'})
    return selected


def paired_multiplicities(draws=2000):
    require(draws == 2000, 'EXACTLY_2000_DRAWS_REQUIRED')
    streams = [np.random.default_rng(s) for s in np.random.SeedSequence(20261027).spawn(19)]
    values = np.empty((draws, 19, 3), dtype=np.int64)
    for i in range(draws):
        for j, rng in enumerate(streams):
            values[i, j] = np.bincount(rng.integers(0, 3, size=3), minlength=3)
    return values


def contrast(a, b):
    la, lb = a['L'], b['L']
    ea, eb = a['L_allowance'], b['L_allowance']
    gain = None if lb == 0 else 1-la/lb
    gain_bounds = None if lb-eb <= 0 else [1-(la+ea)/(lb-eb), 1-max(0., la-ea)/(lb+eb)]
    return {'delta': la-lb, 'delta_bounds': [la-lb-ea-eb, la-lb+ea+eb],
            'gain': gain, 'gain_bounds': gain_bounds}


def grade(value, lower=.10, upper=.25):
    return 'worse' if value < 0 else 'small' if value < lower else 'moderate' if value < upper else 'large'


def grades(bounds, lower=.10, upper=.25):
    if bounds is None:
        return None
    a, b = bounds
    return [name for name, yes in [('worse', a < 0), ('small', b >= 0 and a < lower),
            ('moderate', b >= lower and a < upper), ('large', b >= upper)] if yes]


def decision(intervals, condition_deltas, complete=True):
    if not complete:
        return {'comparison': 'INCOMPLETE', 'preference': 'INCOMPLETE'}
    q = intervals['Q18']
    comp = ('RECIPE_LOWER_THAN_MATCHED_MASS_CONTROL' if q[1] < 0 else
            'MATCHED_MASS_CONTROL_LOWER_THAN_RECIPE' if q[0] > 0 else
            'RECIPE_MASS_COMPARISON_UNRESOLVED')
    resolved_lower = [b for b in ARMS[1:] if intervals[b][0] > 0]
    failed_ci = [b for b in ARMS[1:] if intervals[b][1] >= 0]
    adverse = {b: [c for c, delta in condition_deltas[b].items() if delta > 0] for b in ARMS[1:]}
    pref = ('RECIPE_NOT_SELECTED' if resolved_lower else
            'RECIPE_CONDITIONAL_TRANSFER_PREFERENCE' if not failed_ci and not any(adverse.values()) else
            'RECIPE_INCREMENT_UNRESOLVED')
    return {'comparison': comp, 'preference': pref, 'resolved_lower_comparators': resolved_lower,
            'failed_aggregate_requirements': failed_ci, 'adverse_conditions': adverse}


def quantile(values):
    return np.quantile(np.asarray(values, dtype=np.float64), [.025, .975], method='linear').tolist()


def interval_summary(values, bounds):
    require(len(values) == 2000 and len(bounds) == 2000, 'COMPLETE_PAIRED_DRAWS_REQUIRED')
    undefined = sum(v is None for v in values)
    if undefined:
        return {'ci': None, 'numerical_ci_bounds': None, 'undefined': undefined}
    ci = quantile(values)
    envelope = None if any(b is None for b in bounds) else {
        'lower_endpoint': [quantile([b[0] for b in bounds])[0], quantile([b[1] for b in bounds])[0]],
        'upper_endpoint': [quantile([b[0] for b in bounds])[1], quantile([b[1] for b in bounds])[1]]}
    return {'ci': ci, 'numerical_ci_bounds': envelope, 'undefined': 0}


def summaries(point, draws):
    require(len(draws) == 2000 and [d['draw'] for d in draws] == list(range(2000)),
            'NO_SUCCESSFUL_ONLY_OR_REDUCED_INTERVALS')
    arm_results, contrasts = {}, {}
    for scope in ('aggregate', *TARGET_GROUPS):
        get = lambda record, arm: record[arm]['aggregate'] if scope == 'aggregate' else record[arm]['conditions'][scope]
        arm_results[scope], contrasts[scope] = {}, {}
        for arm in ARMS:
            p = get(point, arm)
            stats = {}
            for metric in ('L', 'MAE', 'bias', 'absolute_shot_bias'):
                vals = [get(d['scores'], arm)[metric] for d in draws]
                bounds = [[v-get(d['scores'], arm)[metric+'_allowance'],
                           v+get(d['scores'], arm)[metric+'_allowance']] for v, d in zip(vals, draws)]
                if metric != 'bias':
                    bounds = [[max(0., lo), hi] for lo, hi in bounds]
                stats[metric] = dict(interval_summary(vals, bounds), point=p[metric],
                    point_bounds=[p[metric]-p[metric+'_allowance'], p[metric]+p[metric+'_allowance']])
            arm_results[scope][arm] = stats
        for comparator in ARMS[1:]:
            p = contrast(get(point, 'R18'), get(point, comparator))
            samples = [contrast(get(d['scores'], 'R18'), get(d['scores'], comparator)) for d in draws]
            delta = interval_summary([c['delta'] for c in samples], [c['delta_bounds'] for c in samples])
            gain = interval_summary([c['gain'] for c in samples], [c['gain_bounds'] for c in samples])
            checks = [{'lower_boundary': lo, 'upper_boundary': hi,
                       'point_grade': None if p['gain'] is None else grade(p['gain'], lo, hi),
                       'ci_grades': grades(gain['ci'], lo, hi)}
                      for lo in (.075, .10, .125) for hi in (.1875, .25, .3125)]
            contrasts[scope][comparator] = {'point': p, 'delta': delta, 'gain': gain,
                'point_grade': None if p['gain'] is None else grade(p['gain']),
                'ci_grades': grades(gain['ci']), 'boundary_checks': checks}
    cis = {b: contrasts['aggregate'][b]['delta']['ci'] for b in ARMS[1:]}
    point_deltas = {b: {c: contrasts[c][b]['point']['delta'] for c in TARGET_GROUPS} for b in ARMS[1:]}
    verdict = decision(cis, point_deltas)
    # Every decision inequality must retain its sign under propagated numerical allowances.
    numeric_ok = True
    for b in ARMS[1:]:
        v = contrasts['aggregate'][b]['delta']
        env = v['numerical_ci_bounds']
        for endpoint, pair in zip(v['ci'], (env['lower_endpoint'], env['upper_endpoint'])):
            numeric_ok &= ((pair[1] < 0) if endpoint < 0 else (pair[0] > 0) if endpoint > 0 else pair == [0., 0.])
        for c in TARGET_GROUPS:
            p = contrasts[c][b]['point']
            numeric_ok &= (p['delta_bounds'][0] > 0 if p['delta'] > 0 else p['delta_bounds'][1] <= 0)
    if not numeric_ok:
        verdict = dict(verdict, comparison='NUMERICALLY_UNRESOLVED', preference='NUMERICALLY_UNRESOLVED')
    return arm_results, contrasts, verdict


def influence_summary(point_scores, deletions):
    result = {}
    for scope in ('source', 'target'):
        result[scope] = {}
        rows = [d for d in deletions if d['scope'] == scope]
        for b in ARMS[1:]:
            reference = contrast(point_scores['R18']['aggregate'], point_scores[b]['aggregate'])
            comparisons = [{'deleted': d['deleted'], **contrast(d['scores']['R18']['aggregate'],
                                                               d['scores'][b]['aggregate'])}
                           for d in rows]
            deltas = [v['delta'] for v in comparisons]
            gains = [v['gain'] for v in comparisons]
            result[scope][b] = {'comparisons': comparisons, 'delta_range': [min(deltas), max(deltas)],
                'gain_range': None if None in gains else [min(gains), max(gains)],
                'ties': [v['deleted'] for v in comparisons if v['delta'] == 0],
                'ranking_reversals': [v['deleted'] for v in comparisons if v['delta']*reference['delta'] < 0],
                'adverse_deletions': [v['deleted'] for v in comparisons if v['delta'] > 0],
                'adverse_conditions': {d['deleted']: [c for c in d['scores']['R18']['conditions']
                    if d['scores']['R18']['conditions'][c]['L'] > d['scores'][b]['conditions'][c]['L']]
                    for d in rows}}
    return result


def write_csv(path, rows):
    with Path(path).open('x', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: canonical(v) if isinstance(v, (dict, list)) else v for k, v in r.items()} for r in rows)


def freeze(out, session_started):
    out = Path(out)
    qualified = read(out/'QUALIFIED.json')
    for n, h in qualified['files'].items():
        require(digest(out/n) == h, 'QUALIFIED_INPUT_DRIFT:' + n)
    names = ('puckworks/analysis/trigonelline_recipe_campaign_transfer.py',
             'tools/trigonelline_recipe_campaign_transfer.py',
             'tests/test_trigonelline_recipe_campaign_transfer.py',
             'docs/analysis/sci_md_trigonelline_recipe_campaign_transfer_001/METHODS.md')
    c = paired_multiplicities()
    with (out/'multiplicities.npy').open('xb') as stream:
        np.save(stream, c, allow_pickle=False)
    import scipy
    import sys
    write(out/'FREEZE.json', {'task': TASK, 'schema': SCHEMA, 'pins': PINS,
        'session_started_unix': session_started, 'inputs': qualified,
        'code_and_methods': {n: digest(ROOT/n) for n in names}, 'old_freeze': OLD_FREEZE,
        'multiplicities_sha256': digest(out/'multiplicities.npy'),
        'seed': 20261027, 'stream_order': list(FIT_GROUPS+TARGET_GROUPS),
        'arms': list(ARMS), 'lambdas': list(LAMBDAS), 'limits': LIMITS,
        'reproduction_tolerance_mg_g': 1e-8, 'numerical_limit_kg': 1e-9,
        'methods_sha256': digest(DOC/'METHODS.md'), 'rights': RIGHTS,
        'synthetic_verification_sha256': digest(out/'synthetic-verification.log'),
        'runtime': {'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__},
        'uncertainty': 'MARGINAL_CONDITIONAL_REFIT_PERCENTILE_INTERVALS_FROZEN_LAMBDAS',
        'review': 'SYNTHETIC_TESTS_AND_SINGLE_CODE_REVIEW_NOT_INDEPENDENT_HUMAN_REVIEW'})


def verify_freeze(out):
    frozen = read(out/'FREEZE.json')
    require(frozen['task'] == TASK and frozen['limits'] == LIMITS and frozen['pins'] == PINS,
            'FROZEN_POLICY_DRIFT')
    for n, h in frozen['code_and_methods'].items():
        require(digest(ROOT/n) == h, 'FROZEN_CODE_OR_METHODS_DRIFT:' + n)
    for n, h in frozen['inputs']['files'].items():
        require(digest(out/n) == h, 'FROZEN_INPUT_DRIFT:' + n)
    require(digest(out/'multiplicities.npy') == frozen['multiplicities_sha256'], 'MULTIPLICITY_DRIFT')
    return frozen


def reproduce(out, old_out, point_predictions, point_scores, selected):
    prior = read(old_out/'predictions.json')
    comparisons = {}
    require(selected['D0'] == geometry.Model.load(old_out/'models/TR-D0.json').regularization,
            'HISTORICAL_D0_LAMBDA_MISMATCH')
    for arm, expected in [('D0', .13454953485410706), ('K0', .7295026781284552)]:
        old = {(p['shot'], p['fraction']): p['trigonelline_mg_g'] for p in prior['TR-'+arm]
               if p['condition'] in TARGET_GROUPS}
        maximum = max(abs(p['prediction_mg_g']-old[p['shot'], p['fraction']]) for p in point_predictions[arm])
        score_diff = abs(point_scores[arm]['aggregate']['L']-expected)
        comparisons[arm] = {'maximum_prediction_difference_mg_g': maximum,
                            'loss_difference_mg_g': score_diff, 'historical_loss': expected}
    write(out/'REPRODUCTION.json', {'lambda_agreement': True, 'tolerance_mg_g': 1e-8, 'arms': comparisons})
    require(all(v['maximum_prediction_difference_mg_g'] <= 1e-8 and v['loss_difference_mg_g'] <= 1e-8
                for v in comparisons.values()), 'HISTORICAL_POINT_REPRODUCTION_MISMATCH')


def run(out, old_out):
    """Execute exactly one campaign; stop on first required failure, preserving evidence."""
    out, old_out = Path(out), Path(old_out)
    frozen = verify_freeze(out)
    require(all(os.environ.get(k) == '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')),
            'ONE_BLAS_THREAD_REQUIRED')
    records, queries, folds = read(out/'training.json'), read(out/'queries.json'), read(out/'folds.json')
    executor = Executor(out, frozen['session_started_unix'])
    completed_draws, failed_draw, stage = 0, None, 'TUNING'
    point_predictions, point_scores = {}, {}
    numerics = {'scored_intervals_excluding_tuning': 0, 'maximum_allowance_kg': 0.,
                'maximum_allowance_mg_g': 0., 'extrapolated_intervals': {a: 0 for a in ARMS}}
    def accumulate(predictions):
        for arm, values in predictions.items():
            numerics['scored_intervals_excluding_tuning'] += len(values)
            numerics['maximum_allowance_kg'] = max(numerics['maximum_allowance_kg'], max(p['allowance_kg'] for p in values))
            numerics['maximum_allowance_mg_g'] = max(numerics['maximum_allowance_mg_g'], max(p['allowance_mg_g'] for p in values))
            numerics['extrapolated_intervals'][arm] += sum(bool(p['feature_extrapolation']) for p in values)
    try:
        selected = tune(records, folds, executor, out)
        stage = 'POINT_FITS'
        models = {}
        for arm in ARMS:
            models[arm] = executor.fit(records, arm, selected.get(arm), 'point.'+arm)
            write(out/f'point_model.{arm}.json', asdict(models[arm]))
            point_predictions[arm] = predict(models[arm], queries)
        write(out/'point_predictions.json', point_predictions)
        accumulate(point_predictions)
        # No new target outcome value has been projected into this executor before this receipt.
        write(out/'SELECTED_MODELS.json', {'task': TASK, 'freeze_sha256': digest(out/'FREEZE.json'),
            'selected_lambdas': selected, 'tuning_sha256': digest(out/'TUNING.json'),
            'models': {a: digest(out/f'point_model.{a}.json') for a in ARMS},
            'predictions_sha256': digest(out/'point_predictions.json'), 'target_outcomes_joined': False,
            'interpretation': 'LAMBDAS_INDEPENDENTLY_SELECTED_ON_FIT_THEN_FROZEN_NOT_NESTED'})
        verify_freeze(out)
        stage = 'TARGET_JOIN_AND_REPRODUCTION'
        write(out/'TARGET_JOIN_START.json', {'time_unix': time.time(),
              'selected_models_sha256': digest(out/'SELECTED_MODELS.json'), 'target_exposed': True})
        from . import pannusch_conditional_trigonelline_delivery as source
        rows = source.source.rows(source.source.DATA/'prediction_fraction_replicates.csv')
        index = source.analyte_index(rows, 'PREDICTION_2022_03')
        observed = [dict(shot=q['shot'], fraction=q['fraction'],
                    q=source.source_value(index[q['shot'], q['fraction']], 'PREDICTION_2022_03')) for q in queries]
        write(out/'observed.json', observed)
        point_scores = {a: score(point_predictions[a], observed) for a in ARMS}
        write(out/'point_scores.json', point_scores)
        reproduce(out, old_out, point_predictions, point_scores, selected)
        print(canonical({'stage': 'point_reproduction', 'status': 'PASS',
                         'losses': {a: v['aggregate']['L'] for a, v in point_scores.items()}}), flush=True)
        stage = 'BOOTSTRAP'
        multiplicities = np.load(out/'multiplicities.npy', allow_pickle=False)
        draws = []
        for i, c in enumerate(multiplicities):
            failed_draw = i
            executor.event({'event': 'DRAW_START', 'draw': i, 'multiplicities': c.tolist()})
            predictions, scores = {}, {}
            for arm in ARMS:
                model = executor.fit(records, arm, selected.get(arm), f'draw.{i:04d}.{arm}', c[:15].ravel())
                predictions[arm] = predict(model, queries)
                require(len(predictions[arm]) == 48, 'DRAW_TARGET_COVERAGE')
                scores[arm] = score(predictions[arm], observed, c[15:].ravel())
            d = {'draw': i, 'scores': scores}
            accumulate(predictions)
            write(out/f'draw.{i:04d}.json', dict(d, predictions=predictions, multiplicities=c.tolist()))
            draws.append(d)
            completed_draws += 1
            executor.event({'event': 'DRAW_FINISH', 'draw': i})
            failed_draw = None
            executor.check()
            if (i+1) % 50 == 0:
                print(canonical({'stage': 'bootstrap', 'completed': i+1, 'requested': 2000,
                                 'elapsed_seconds': time.time()-executor.started}), flush=True)
        stage = 'INFLUENCE'
        deletions = []
        for group in FIT_GROUPS:
            training = [s for s in records if s['group'] != group]
            predictions, scores = {}, {}
            for arm in ARMS:
                model = executor.fit(training, arm, selected.get(arm), f'delete.{group}.{arm}')
                predictions[arm] = predict(model, queries)
                scores[arm] = score(predictions[arm], observed)
            d = {'scope': 'source', 'deleted': group, 'scores': scores}
            accumulate(predictions)
            deletions.append(d)
            write(out/f'delete.{group}.json', dict(d, predictions=predictions))
            executor.check()
        for group in TARGET_GROUPS:
            conditions = tuple(g for g in TARGET_GROUPS if g != group)
            scores = {a: score(point_predictions[a], observed, conditions=conditions) for a in ARMS}
            d = {'scope': 'target', 'deleted': group, 'scores': scores}
            deletions.append(d)
            write(out/f'delete.{group}.json', d)
        stage = 'INFERENCE'
        arm_results, comparisons, verdict = summaries(point_scores, draws)
        influence = influence_summary(point_scores, deletions)
        require(executor.starts == 18684 and executor.analytic == 2016, 'COMPLETE_FIT_ACCOUNTING')
        executor.check()
        result = {'task': TASK, 'status': 'COMPLETE', 'decision': verdict, 'arms': arm_results,
            'contrasts': comparisons, 'influence': influence, 'selected_lambdas': selected,
            'support': read(out/'support.json'), 'reproduction': read(out/'REPRODUCTION.json'),
            'counts': {'source_physical_shots': 45, 'source_designs': 15, 'source_slots': 180,
                'source_qualified': 177, 'source_unavailable_mass_prefix': 3,
                'evaluation_physical_shots': 12, 'target_windows': 48,
                'draws_requested': 2000, 'draws_completed': 2000, 'draws_failed': 0, 'draws_unattempted': 0,
                'iterative_starts': executor.starts, 'iterative_finished': executor.finished,
                'finite_unsuccessful_starts': executor.unsuccessful, 'analytic_fits': executor.analytic,
                'actual_residual_calls': executor.calls.tell()},
            'science_elapsed_seconds': time.time()-executor.started, 'rights': RIGHTS,
            'numerics': numerics, 'point_feature_diagnostics': {a: {
                'rank': m.feature_rank, 'condition': m.feature_condition,
                'domain_kg': m.domain, 'extra_mean': m.extra_mean, 'extra_sd': m.extra_sd}
                for a, m in models.items()},
            'undefined_gain_draws': {scope: {b: v['gain']['undefined'] for b, v in cs.items()}
                                     for scope, cs in comparisons.items()},
            'exposure': ['SOURCE_INTERNAL', 'TARGET_EXPOSED', 'RETROSPECTIVE',
                        'CONDITIONAL_ON_MEASURED_EARLY_AND_QUERY_BEVERAGE_MASS'],
            'basis': 'cAlcaloids(:,2); HPLC T; mg/fraction / measured vial g; mg/g beverage; internal kg/kg',
            'tds_ey_basis': 'NOT_APPLICABLE',
            'uncertainty': 'Marginal conditional resampling intervals, uncalibrated coverage; frozen selected lambdas; not nested or tuning-aware.',
            'omitted_uncertainty': ['assay calibration/recovery', 'LOD/LOQ', 'shared systematic errors',
                'mass/assay covariance', 'campaign/population', 'tuning selection', 'prior family selection'],
            'successor': {'task': 'SCI-MD-TRIGONELLINE-RECIPE-INCREMENT-HELD-DESIGN-001',
                'execution': 'NOT_RUN', 'justification': 'PREFERENCE_SUPPORTED_FRESH_CREDIBLE_BUDGET_REQUIRED'
                if verdict['preference'] == 'RECIPE_CONDITIONAL_TRANSFER_PREFERENCE' else 'NOT_JUSTIFIED'},
            'qa': 'PENDING_END_OF_TASK_REPOSITORY_CHECKS', 'P1_blind_TDS': 'OPEN'}
        write(out/'RESULT.json', result)
        write_csv(out/'SCORES.csv', [dict(scope=s, arm=a, metric=m, **v)
                   for s, arms in arm_results.items() for a, metrics in arms.items() for m, v in metrics.items()])
        write_csv(out/'CONTRASTS.csv', [dict(scope=s, comparator=b, **v)
                   for s, cs in comparisons.items() for b, v in cs.items()])
        write_csv(out/'PREDICTIONS.csv', [dict(arm=a, **p) for a, ps in point_predictions.items() for p in ps])
        executor.event({'event': 'CAMPAIGN_FINISH', 'status': 'COMPLETE', 'counts': result['counts']})
        return result
    except Exception as exc:
        failure = {'task': TASK, 'status': 'INCOMPLETE', 'stage': stage,
            'exception_type': type(exc).__name__, 'reason': str(exc), 'failed_draw': failed_draw,
            'draws_requested': 2000, 'draws_completed': completed_draws,
            'draws_failed': int(failed_draw is not None),
            'draws_unattempted': 2000-completed_draws-int(failed_draw is not None),
            'iterative_starts': executor.starts, 'finished_starts': executor.finished,
            'analytic_fits': executor.analytic, 'actual_residual_calls': executor.calls.tell(),
            'elapsed_seconds': time.time()-executor.started, 'preference': 'INCOMPLETE'}
        write(out/'FAILURE.json', failure)
        executor.event({'event': 'CAMPAIGN_FAILED', **failure})
        raise


def artifact_manifest(out):
    out = Path(out)
    write(out/'ARTIFACTS.json', {'task': TASK, 'files': {str(p.relative_to(out)): digest(p)
          for p in sorted(out.rglob('*')) if p.is_file() and p.name not in ('ARTIFACTS.json', 'worker.lock')}})

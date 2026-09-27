"""Bounded FIT-only regression for SCI-MD-MASS-DELIVERY-006.

Only typed, arm-specific projections enter fitting. No source reader or scorer
is imported here. Development scores are not independent validation.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
import json
from pathlib import Path
import resource
import sys
import time

import numpy as np
from scipy.optimize import least_squares
from scipy.special import logit

from . import conditional_tail_delivery as md

LAMBDAS = (.0001, .01, 1., 100.)
START_ORDER = (-1, 0, 1)


@dataclass(frozen=True)
class Window:
    fraction: int
    start_kg: float
    end_kg: float
    q: float

    def __post_init__(self):
        if self.fraction not in (3, 5, 7, 10):
            raise ValueError('SUFFIX_RESPONSE_ONLY')
        for name in ('start_kg', 'end_kg', 'q'):
            object.__setattr__(self, name, md.number(getattr(self, name)))
        if not 0 <= self.start_kg < self.end_kg or not 0 <= self.q <= 1:
            raise ValueError('INVALID_TRAINING_WINDOW')


@dataclass(frozen=True)
class TrainingShot:
    shot: str
    group: str
    inputs: md.EarlyInput
    windows: tuple[Window, ...]
    campaign: str = 'FIT_2021_12'

    def __post_init__(self):
        object.__setattr__(self, 'windows', tuple(self.windows))
        if (self.campaign != 'FIT_2021_12' or not self.shot.startswith('FIT-')
                or not self.group.startswith('FIT-') or not isinstance(self.inputs, md.EarlyInput)
                or not self.windows or any(not isinstance(w, Window) for w in self.windows)
                or len({w.fraction for w in self.windows}) != len(self.windows)
                or any(w.start_kg < sum(self.inputs.values[:2])-1e-15 for w in self.windows)):
            raise ValueError('FIT_ONLY_INTACT_SHOT_CONTRACT')


def project_arm(records, arm):
    """Drop forbidden conditioning fields before constructing any fitting object."""
    n = len(md.feature_names(arm))
    return tuple(TrainingShot(r['shot'], r['group'],
        md.EarlyInput(arm, tuple(r['early_values'][:n]), 'SOURCE_EARLY_INPUT'),
        tuple(Window(**w) for w in r['windows'])) for r in records)


def validate_training(shots):
    if (not isinstance(shots, tuple) or not shots or any(not isinstance(s, TrainingShot) for s in shots)
            or len({s.shot for s in shots}) != len(shots)
            or len({s.inputs.arm for s in shots}) != 1):
        raise ValueError('IMMUTABLE_UNIQUE_ARM_TRAINING_REQUIRED')


def shot_weights(shots):
    groups = sorted({s.group for s in shots})
    return np.asarray([1/(len(groups)*sum(t.group == s.group for t in shots)) for s in shots])


class FitProblem:
    def __init__(self, shots, regularization):
        validate_training(shots)
        if regularization not in LAMBDAS:
            raise ValueError('UNDECLARED_LAMBDA')
        self.shots, self.regularization = shots, regularization
        self.arm = shots[0].inputs.arm
        raw = np.asarray([s.inputs.values for s in shots])
        sw = shot_weights(shots)
        self.means = sw @ raw
        self.minima, self.maxima = raw.min(axis=0), raw.max(axis=0)
        self.domain = max(w.end_kg for s in shots for w in s.windows)
        self.features = np.c_[np.ones(len(shots)), (raw-self.means)/md.SCALES[:raw.shape[1]]]
        self.row_shots = np.asarray([i for i, s in enumerate(shots) for w in s.windows], int)
        self.windows = tuple(w for s in shots for w in s.windows)
        masses = np.asarray([w.end_kg-w.start_kg for w in self.windows])
        self.masses, self.q = masses, np.asarray([w.q for w in self.windows])
        self.weights = np.asarray([sw[i]*(w.end_kg-w.start_kg)/sum(v.end_kg-v.start_kg for v in s.windows)
                                  for i, s in enumerate(shots) for w in s.windows])
        self.geometry = md.IntervalGeometry([w.start_kg for w in self.windows],
                                            [w.end_kg for w in self.windows], self.domain)
        self.shape = (5, raw.shape[1]+1)
        self.size = int(np.prod(self.shape))
        mean_q = float(self.weights @ self.q)
        # Initialization ONLY. Neither the source nor fitted predictions are clipped.
        initial = float(logit(min(1-1e-8, max(1e-8, mean_q))))
        self.starts = []
        for slope in START_ORDER:
            theta = np.zeros(self.shape)
            theta[:, 0] = initial+slope*np.linspace(-1, 1, 5)
            if np.any(np.abs(theta) > 20):
                raise ValueError('INITIALIZATION_OUTSIDE_BOUNDS')
            self.starts.append(theta.ravel())

    def residual(self, parameters):
        theta = np.asarray(parameters).reshape(self.shape)
        logits = (self.features @ theta.T)[self.row_shots]
        data = 100*(self.geometry.integrate(logits)/self.masses-self.q)*np.sqrt(self.weights)
        slopes = theta[:, 1:].ravel()
        second = (np.diff(theta, n=2, axis=0)/(.25**2)).ravel()
        penalty1 = slopes*np.sqrt(self.regularization/len(slopes)) if len(slopes) else np.empty(0)
        penalty2 = second*np.sqrt(self.regularization/len(second)) if len(second) else np.empty(0)
        return np.r_[data, penalty1, penalty2]

    def model(self, parameters, identity, rights):
        return md.Model(self.arm, np.asarray(parameters).reshape(self.shape), self.means,
                        self.minima, self.maxima, self.domain, self.regularization,
                        md.canonical(identity), rights)


class BudgetReached(RuntimeError):
    pass


def write_new(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


class Budget:
    """Persistent exclusive accounting; one worker, <=12 GiB address space."""
    def __init__(self, directory, *, apply_memory_limit=True):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.clock_path = self.directory/'clock.json'
        if not self.clock_path.exists():
            write_new(self.clock_path, {'started_unix': time.time(), 'max_wall_seconds': 14400,
                'max_starts': 600, 'max_calls_per_start': 8000, 'workers': 1,
                'blas_threads': 1, 'max_address_space_bytes': 12*1024**3,
                'max_private_bytes': 5*1024**3})
        self.clock = json.loads(self.clock_path.read_text())
        if apply_memory_limit:
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            cap = self.clock['max_address_space_bytes']
            resource.setrlimit(resource.RLIMIT_AS, (min(cap, soft) if soft > 0 else cap, hard))

    def check(self):
        if time.time()-self.clock['started_unix'] >= self.clock['max_wall_seconds']:
            raise BudgetReached('FOUR_HOUR_EXECUTION_CEILING')
        total = sum(p.stat().st_size for p in self.directory.parent.rglob('*') if p.is_file())
        if total >= self.clock['max_private_bytes']:
            raise BudgetReached('PRIVATE_ARTIFACT_CEILING')

    def start(self, fit_name, index, parameters):
        self.check()
        existing = list(self.directory.glob('*.start.json'))
        if len(existing) >= self.clock['max_starts']:
            raise BudgetReached('SIX_HUNDRED_START_CEILING')
        path = self.directory/f'{fit_name}.s{index}'
        write_new(path.with_suffix(path.suffix+'.start.json'),
                  {'fit': fit_name, 'start_index': index, 'started_unix': time.time(),
                   'initial_parameters': list(map(float, parameters))})
        return path


def fit(shots, regularization, budget, name, source_identity, rights):
    problem = FitProblem(shots, regularization)
    info = {'scope': 'FIT_ONLY', 'campaign': 'FIT_2021_12',
            'shots': [s.shot for s in shots], 'groups': sorted({s.group for s in shots}),
            'training_projection_sha256': md.identity([asdict(s) for s in shots]),
            'source_identity': source_identity, 'fit_name': name}
    results, candidates = [], []
    for index, initial in enumerate(problem.starts):
        prefix = budget.start(name, index, initial)
        started = time.monotonic()
        calls, numerical_calls, last, last_objective = 0, 0, initial.copy(), None
        def residual(x):
            nonlocal calls, numerical_calls, last, last_objective
            if calls >= 8000:
                raise BudgetReached('EIGHT_THOUSAND_ACTUAL_RESIDUAL_CALLS')
            if time.time()-budget.clock['started_unix'] >= 14400:
                raise BudgetReached('FOUR_HOUR_EXECUTION_CEILING')
            calls += 1
            frame = sys._getframe(1)
            while frame is not None:
                if frame.f_code.co_filename.endswith('/_numdiff.py'):
                    numerical_calls += 1
                    break
                frame = frame.f_back
            del frame
            last = x.copy()
            r = problem.residual(x)
            last_objective = float(r @ r)
            return r
        record = {'fit': name, 'start_index': index, 'initial_parameters': list(map(float, initial))}
        try:
            result = least_squares(residual, initial, bounds=(-20., 20.), method='trf',
                tr_solver='exact', loss='linear', jac='2-point', diff_step=1e-6,
                ftol=1e-10, xtol=1e-10, gtol=1e-10, x_scale=1., max_nfev=8000)
            objective = float(result.fun @ result.fun)
            converged = bool(result.success and result.status > 0
                             and np.isfinite(result.x).all() and np.isfinite(objective))
            record.update(status='CONVERGED' if converged else 'NONCONVERGED',
                solver_status=int(result.status), message=str(result.message),
                objective=objective, parameters=result.x.tolist(), optimality=float(result.optimality),
                nfev=int(result.nfev), njev=int(result.njev),
                numerical_jacobian_residual_calls=numerical_calls)
            if converged:
                candidates.append((objective, index, result.x))
        except (ValueError, FloatingPointError, BudgetReached) as exc:
            record.update(status='FAILED', message=str(exc), parameters=last.tolist(),
                objective=last_objective, nfev=None, njev=None,
                numerical_jacobian_residual_calls=numerical_calls)
        record.update(actual_residual_calls=calls, elapsed_seconds=time.monotonic()-started,
            boundary_indices=np.flatnonzero(np.abs(np.asarray(record['parameters'])) >= 20-1e-7).tolist(),
            peak_rss_kib=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
        write_new(prefix.with_suffix(prefix.suffix+'.end.json'), record)
        results.append(record)
        budget.check()
    if not candidates:
        return None, {'status': 'NONSELECTABLE_NO_CONVERGED_START', 'starts': results}
    best = min(candidates, key=lambda c: (c[0], c[1]))
    return problem.model(best[2], info, rights), {
        'status': 'CONVERGED', 'selected_start': best[1], 'objective': best[0], 'starts': results}


def folds(shots):
    validate_training(shots)
    out = []
    for group in sorted({s.group for s in shots}):
        train = tuple(s for s in shots if s.group != group)
        held = tuple(s for s in shots if s.group == group)
        domain = max(w.end_kg for s in train for w in s.windows)
        support = tuple((s.shot, w.fraction) for s in held for w in s.windows if w.end_kg <= domain)
        out.append((group, train, held, domain, support))
    return tuple(out)


def development_metrics(model, held, support):
    """Equal shot R on the predeclared source/domain support; failure is explicit."""
    shot_scores = []
    for shot in held:
        windows = [w for w in shot.windows if (shot.shot, w.fraction) in support]
        if not windows:
            raise ValueError('NO_HELD_SHOT_SUPPORT')
        state = model.condition(shot.inputs)
        geom = md.IntervalGeometry([w.start_kg for w in windows], [w.end_kg for w in windows], model.domain_kg)
        masses = np.asarray([w.end_kg-w.start_kg for w in windows])
        pred = geom.integrate(np.tile(state.logits, (len(windows), 1)))
        error = 100*(pred/masses-np.asarray([w.q for w in windows]))
        shot_scores.append(float(np.sqrt(np.average(error**2, weights=masses))))
    return float(np.mean(shot_scores))


def select_lambda(candidates):
    valid = [(float(c['balanced_R_pp']), float(c['lambda'])) for c in candidates if c['status'] == 'SELECTABLE']
    if not valid:
        raise ValueError('NO_SELECTABLE_LAMBDA')
    lowest = min(v for v, _ in valid)
    return max(lam for v, lam in valid if v <= lowest+1e-6)


def develop(records, out, budget, source_identity, rights):
    out = Path(out)
    summary = {'scope': 'DEVELOPMENT_DIAGNOSTICS_NOT_UNBIASED_NESTED_VALIDATION', 'arms': {}}
    for arm in md.ARMS:
        shots = project_arm(records, arm)
        candidates = []
        for lam in LAMBDAS:
            result = {'lambda': lam, 'status': 'SELECTABLE', 'folds': []}
            for group, train, held, domain, support in folds(shots):
                name = f'{arm}.{lam:g}.{group}'
                model, audit = fit(train, lam, budget, name, source_identity, rights)
                fold_result = {'group': group, 'domain_kg': domain, 'supported_windows': len(support),
                    'intended_windows': 4*len(held), 'source_eligible_windows': sum(len(s.windows) for s in held),
                    'original_shots': len(held), 'support_sha256': md.identity(support),
                    'fit_status': audit['status'], 'balanced_R_pp': None}
                try:
                    if model is None:
                        raise ValueError('MODEL_FIT_FAILED')
                    fold_result['balanced_R_pp'] = development_metrics(model, held, support)
                    model.save(out/f'{name}.model.json')
                except ValueError as exc:
                    result['status'] = 'NONSELECTABLE'
                    fold_result['failure'] = str(exc)
                write_new(out/f'{name}.audit.json', audit)
                result['folds'].append(fold_result)
                print(name, audit['status'], 'calls', sum(s['actual_residual_calls'] for s in audit['starts']), flush=True)
            result['balanced_R_pp'] = float(np.mean([f['balanced_R_pp'] for f in result['folds']])) if result['status'] == 'SELECTABLE' else None
            candidates.append(result)
        try:
            selected = select_lambda(candidates)
        except ValueError:
            selected = None
        summary['arms'][arm] = {'selected_lambda': selected, 'candidates': candidates}
        write_new(out/f'{arm}.selection.json', summary['arms'][arm])
    write_new(out/'development.json', summary)
    return summary

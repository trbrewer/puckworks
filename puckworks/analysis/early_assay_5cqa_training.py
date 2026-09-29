"""Bounded, FIT-only matched early-assay 5CQA curve training; no source reader or PRED scorer."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import fcntl
import os
from pathlib import Path
import resource
import sys
import time

import numpy as np
from scipy.optimize import least_squares
from scipy.special import logit

from . import early_assay_5cqa_delivery as md
from .conditional_tail_training import Budget as ReceiptBudget, BudgetReached, write_new

LAMBDAS = (.0001, .01, 1., 100.)
START_ORDER = (-1, 0, 1)
TASK_DEADLINE = datetime.fromisoformat('2026-09-29T22:34:51+00:00').timestamp()
LIMITS = {'max_wall_seconds': 3600, 'max_starts': 549, 'max_calls_per_start': 8000,
          'workers': 1, 'blas_threads': 1, 'max_address_space_bytes': 12*1024**3,
          'max_private_bytes': 5*1024**3}


@dataclass(frozen=True)
class Window:
    fraction: int
    start_kg: float
    end_kg: float
    q: float
    mass_kg: float
    coordinate_allowance_kg: float = 0.

    def __post_init__(self):
        for k in ('start_kg', 'end_kg', 'q', 'mass_kg', 'coordinate_allowance_kg'):
            object.__setattr__(self, k, md.number(getattr(self, k)))
        if (self.fraction not in (3, 5, 7, 10) or not 0 <= self.start_kg < self.end_kg
                or not 0 <= self.q <= 1 or self.mass_kg <= 0 or not 0 <= self.coordinate_allowance_kg <= 1e-9):
            raise ValueError('QUALIFIED_FIVE_CQA_TARGET_WINDOW_REQUIRED')


@dataclass(frozen=True)
class Shot:
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
                or any(w.start_kg < sum(self.inputs.values[:2]) for w in self.windows)):
            raise ValueError('FIT_ONLY_INTACT_FIVE_CQA_SHOT_REQUIRED')


def project_arm(records, arm):
    """Project the permitted named columns before any transform or fitting call."""
    names = md.feature_names(arm)
    result = []
    schema = {'L1M': md.L1MInput, 'L2M': md.L2MInput, 'L12': md.L12Input}[arm]
    for r in records:
        md.exact_keys(r, ('shot', 'group', 'early_values', 'windows'))
        if len(r['early_values']) != 4:
            raise ValueError('COMPLETE_ROLE_PROJECTION_REQUIRED')
        allowed = {n: r['early_values'][md.FEATURES.index(n)] for n in names}
        inputs = schema(**allowed, input_class='SOURCE_EARLY_INPUT')
        result.append(Shot(r['shot'], r['group'], inputs, tuple(Window(**w) for w in r['windows'])))
    return tuple(result)


def validate(shots):
    if (not isinstance(shots, tuple) or not shots or any(not isinstance(s, Shot) for s in shots)
            or len({s.shot for s in shots}) != len(shots)
            or len({s.inputs.arm for s in shots}) != 1):
        raise ValueError('UNIQUE_IMMUTABLE_ARM_TRAINING_REQUIRED')


def shot_weights(shots):
    groups = {s.group for s in shots}
    return np.asarray([1/(len(groups)*sum(t.group == s.group for t in shots)) for s in shots])


def weights(shots):
    sw = shot_weights(shots)
    return np.asarray([sw[i]*w.mass_kg/sum(v.mass_kg for v in s.windows)
                       for i, s in enumerate(shots) for w in s.windows])


def split_design(shots, group):
    validate(shots)
    training = tuple(s for s in shots if s.group != group)
    held = tuple(s for s in shots if s.group == group)
    if not training or not held:
        raise ValueError('NONEMPTY_WHOLE_ORIGINAL_DESIGN_FOLD_REQUIRED')
    return training, held


class FitProblem:
    def __init__(self, shots, regularization, *, scope='DEVELOPMENT'):
        validate(shots)
        self.arm, self.shots, self.regularization, self.scope = shots[0].inputs.arm, shots, regularization, scope
        if regularization not in LAMBDAS:
            raise ValueError('DECLARED_LAMBDA_REQUIRED')
        if scope not in ('DEVELOPMENT', 'FINAL_FIT', 'SYNTHETIC'):
            raise ValueError('DECLARED_FIT_SCOPE_REQUIRED')
        raw = np.asarray([s.inputs.values for s in shots])
        self.means = np.asarray([shot_weights(shots) @ raw[:, j] for j in range(raw.shape[1])])
        self.minima, self.maxima = raw.min(axis=0), raw.max(axis=0)
        self.domain = max(w.end_kg for s in shots for w in s.windows)
        if self.domain > md.HARD_UPPER_KG:
            raise ValueError('TRAINING_DOMAIN_EXCEEDS_HARD_CEILING')
        self.windows = tuple(w for s in shots for w in s.windows)
        self.row_shots = np.asarray([i for i, s in enumerate(shots) for w in s.windows], int)
        self.features = np.c_[np.ones(len(shots)), (raw-self.means)/md.scales(self.arm)]
        self.geometry = md.Geometry([w.start_kg for w in self.windows], [w.end_kg for w in self.windows], self.domain, self.domain)
        self.widths = np.asarray([w.end_kg-w.start_kg for w in self.windows])
        self.q = np.asarray([w.q for w in self.windows])
        self.weights = weights(shots)
        self.shape = (5, 1+len(md.feature_names(self.arm)))
        self.bounds = (np.full(5*self.shape[1], -20.), np.full(5*self.shape[1], 20.))
        initial = float(logit(min(1-1e-8, max(1e-8, float(self.weights @ self.q)))))
        self.starts = []
        for ramp in START_ORDER:
            theta = np.zeros(self.shape)
            theta[:, 0] = initial+ramp*np.linspace(-1, 1, 5)
            if np.any(np.abs(theta) > 20):
                raise ValueError('INITIALIZATION_OUTSIDE_BOUNDS')
            self.starts.append(theta.ravel())

    def residual(self, parameters):
        theta = np.asarray(parameters).reshape(self.shape)
        logits = (self.features @ theta.T)[self.row_shots]
        predicted = self.geometry.integrate(logits)/self.widths
        data = 1000/.25*(predicted-self.q)*np.sqrt(self.weights)
        # Keep D0's column norms intact; the assay column has separate norms.
        slopes = theta[:, 1:3].ravel()
        second = (np.diff(theta[:, :3], n=2, axis=0)/(.25**2)).ravel()
        penalties = [slopes*np.sqrt(self.regularization/10), second*np.sqrt(self.regularization/9)]
        for column in range(3, self.shape[1]):
            penalties.extend((theta[:, column]*np.sqrt(self.regularization/5),
                np.diff(theta[:, column], n=2)/(.25**2)*np.sqrt(self.regularization/3)))
        return np.concatenate([data, *penalties])


    def model(self, parameters, provenance, rights):
        return md.Model(self.arm, np.asarray(parameters).reshape(self.shape), self.means,
                        self.minima, self.maxima, self.domain, self.regularization,
                        md.canonical(provenance), rights)


class Budget(ReceiptBudget):
    """Reuse durable exclusive receipts with this task's stricter fixed limits."""
    def __init__(self, directory, *, synthetic=False, evidence_root=None):
        if not synthetic and any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
            raise ValueError('ONE_BLAS_THREAD_REQUIRED')
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.worker_lock = (directory / 'worker.lock').open('a')
        try:
            fcntl.flock(self.worker_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BudgetReached('ONE_WORKER_REQUIRED') from exc
        path = directory / 'clock.json'
        if not path.exists():
            write_new(path, dict(LIMITS, started_unix=time.time(), task='SCI-MD-5CQA-ASSAY-002',
                                 scope='SYNTHETIC' if synthetic else 'REAL_FIT'))
        clock = md.strict_json(path.read_text())
        if (any(clock.get(k) != v for k, v in LIMITS.items())
                or clock.get('scope') != ('SYNTHETIC' if synthetic else 'REAL_FIT')):
            raise BudgetReached('PERSISTENT_TASK_LIMITS_MISMATCH')
        self.synthetic = synthetic
        self.evidence_root = Path(evidence_root) if evidence_root else directory.parent
        super().__init__(directory, apply_memory_limit=not synthetic)
        starts = list(directory.glob('*.start.json'))
        if any(not s.with_name(s.name.replace('.start.json', '.end.json')).exists() for s in starts):
            raise BudgetReached('INCOMPLETE_ATTEMPT_RETAINED_NO_RESTART')
        self.check()

    def check(self):
        if not self.synthetic and time.time() >= TASK_DEADLINE:
            raise BudgetReached('SIX_HOUR_TASK_DEADLINE')
        if time.time()-self.clock['started_unix'] >= 3600:
            raise BudgetReached('SIXTY_MINUTE_REAL_FITTING_CEILING')
        if sum(p.stat().st_size for p in self.evidence_root.rglob('*') if p.is_file()) >= 5*1024**3:
            raise BudgetReached('FIVE_GIB_PRIVATE_EVIDENCE_CEILING')

    def start(self, fit_name, index, parameters):
        if len(list(self.directory.glob('*.start.json'))) >= 549:
            raise BudgetReached('FIVE_HUNDRED_FORTY_NINE_START_CEILING')
        arm = fit_name.split('.')[0]
        if arm not in md.ARMS:
            raise ValueError('ONLY_DECLARED_ARMS_AUTHORIZED')
        if len(list(self.directory.glob(arm+'.*.start.json'))) >= 183:
            raise BudgetReached('ARM_183_START_CEILING')
        return super().start(fit_name, index, parameters)


def provenance(problem, name, source_identity):
    return {'scope': problem.scope, 'fit_name': name, 'campaign': 'FIT_2021_12', 'species': md.SPECIES,
            'shots': [s.shot for s in problem.shots], 'groups': sorted({s.group for s in problem.shots}),
            'training_projection_sha256': md.identity([asdict(s) for s in problem.shots]),
            'source_identity': source_identity}


def fit(shots, regularization, budget, name, source_identity, rights, *, scope='DEVELOPMENT'):
    problem = FitProblem(shots, regularization, scope=scope)
    if name.split('.')[0] != problem.arm:
        raise ValueError('ATTEMPT_ARM_IDENTITY_MISMATCH')
    info = provenance(problem, name, source_identity)
    results, candidates = [], []
    for index, initial in enumerate(problem.starts):
        prefix = budget.start(name, index, initial)
        started = time.monotonic()
        calls, numerical_calls, last, last_objective = 0, 0, initial.copy(), None
        def residual(x):
            nonlocal calls, numerical_calls, last, last_objective
            if calls >= 8000:
                raise BudgetReached('EIGHT_THOUSAND_ACTUAL_RESIDUAL_CALLS')
            if time.time()-budget.clock['started_unix'] >= 3600 or (not budget.synthetic and time.time() >= TASK_DEADLINE):
                raise BudgetReached('FIXED_EXECUTION_TIME_CEILING')
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
            result = least_squares(residual, initial, bounds=problem.bounds, method='trf',
                tr_solver='exact', loss='linear', jac='2-point', diff_step=1e-6,
                ftol=1e-10, xtol=1e-10, gtol=1e-10, x_scale=1., max_nfev=8000)
            objective = float(result.fun @ result.fun)
            converged = bool(result.success and result.status > 0 and np.isfinite(result.x).all() and np.isfinite(objective))
            record.update(status='CONVERGED' if converged else 'NONCONVERGED', solver_status=int(result.status),
                message=str(result.message), objective=objective, parameters=result.x.tolist(), optimality=float(result.optimality),
                nfev=int(result.nfev), njev=int(result.njev))
            if converged:
                candidates.append((objective, index, result.x))
        except BaseException as exc:
            record.update(status='FAILED', message=str(exc), parameters=last.tolist(), objective=last_objective,
                          nfev=None, njev=None, budget_failure=isinstance(exc, BudgetReached))
            raise
        finally:
            x = np.asarray(record.get('parameters', last))
            lo, hi = problem.bounds
            record.update(arm=problem.arm, actual_residual_calls=calls,
                numerical_jacobian_residual_calls=numerical_calls,
                elapsed_seconds=time.monotonic()-started,
                boundary_indices=np.flatnonzero((x-lo <= 1e-7) | (hi-x <= 1e-7)).tolist(),
                peak_rss_kib=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
            write_new(prefix.with_suffix(prefix.suffix+'.end.json'), record)
        results.append(record)
        budget.check()
        if record.get('budget_failure'):
            raise BudgetReached(record['message'])
    if not candidates or any(r['status'] != 'CONVERGED' for r in results):
        return None, {'status': 'NONSELECTABLE', 'starts': results}
    best = min(candidates, key=lambda c: (c[0], c[1]))
    if results[best[1]]['boundary_indices']:
        return None, {'status': 'SELECTED_BOUNDARY_LIMITATION', 'starts': results}
    return problem.model(best[2], info, rights), {'status': 'CONVERGED', 'selected_start': best[1],
                                                'objective': best[0], 'starts': results}


def held_metrics(model, shots, support):
    scores, bounds, maximum = [], [], 0.
    for shot in shots:
        ws = [w for w in shot.windows if (shot.shot, w.fraction) in support]
        if not ws:
            raise ValueError('MISSING_ORIGINAL_HELD_SHOT_SUPPORT')
        ps = model.condition(shot.inputs).predict_intervals([w.start_kg for w in ws], [w.end_kg for w in ws])
        allowance = np.asarray([p.allowance_kg+w.coordinate_allowance_kg for p, w in zip(ps, ws)])
        if any(not p.numerical_qualified for p in ps) or np.any(allowance > 1e-9):
            raise ValueError('NUMERICALLY_UNQUALIFIED_FOLD')
        masses = np.asarray([w.mass_kg for w in ws])
        errors = np.asarray([p.five_cqa_mg_g-1000*w.q for p, w in zip(ps, ws)])
        scores.append(float(np.sqrt(np.average(errors**2, weights=masses))))
        bounds.append(float(np.sqrt(np.average((1000*allowance/masses)**2, weights=masses))))
        maximum = max(maximum, float(max(allowance)))
    return {'R_mg_g': float(np.mean(scores)), 'R_allowance_mg_g': float(np.mean(bounds)),
            'max_allowance_kg': maximum}


def select_lambda(candidates):
    valid = [c for c in candidates if c['status'] == 'SELECTABLE']
    if not valid:
        raise ValueError('NO_SELECTABLE_LAMBDA')
    low = min(c['balanced_R_mg_g'] for c in valid)
    chosen = max((c for c in valid if c['balanced_R_mg_g'] <= low+1e-6), key=lambda c: c['lambda'])
    lower_min = min(c['balanced_R_mg_g']-c['R_allowance_mg_g'] for c in valid)
    upper_min = min(c['balanced_R_mg_g']+c['R_allowance_mg_g'] for c in valid)
    if chosen['balanced_R_mg_g']+chosen['R_allowance_mg_g'] > lower_min+1e-6:
        raise ValueError('NUMERICALLY_UNRESOLVED_LAMBDA_SELECTION')
    for c in valid:
        if c['lambda'] > chosen['lambda'] and c['balanced_R_mg_g']-c['R_allowance_mg_g'] <= upper_min+1e-6:
            raise ValueError('NUMERICALLY_UNRESOLVED_LAMBDA_SELECTION')
    return chosen['lambda']



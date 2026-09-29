"""FIT-only grouped 5-CQA heads; retained parents are supplied, never fitted."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import resource
import sys
import time

import numpy as np
from scipy.optimize import least_squares
from scipy.special import logit

from . import conditional_5cqa_tds_delivery as md
from .conditional_tail_training import Budget as ReceiptBudget, BudgetReached, write_new
from datetime import datetime
import fcntl

LAMBDAS = (.0001, .01, 1., 100.)
START_ORDER = (-1, 0, 1)


TASK_DEADLINE = datetime.fromisoformat('2026-09-29T07:09:49+00:00').timestamp()
LIMITS = {'max_wall_seconds': 3600, 'max_starts': 366, 'max_calls_per_start': 8000,
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
                or self.q < 0 or self.mass_kg <= 0 or not 0 <= self.coordinate_allowance_kg <= 1e-9):
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
    result = []
    for r in records:
        md.exact_keys(r, ('shot', 'group', 'early_values', 'windows'))
        result.append(Shot(r['shot'], r['group'], md.EarlyInput(arm, r['early_values'], 'SOURCE_EARLY_INPUT'),
                           tuple(Window(**w) for w in r['windows'])))
    return tuple(result)


def validate(shots):
    if (not isinstance(shots, tuple) or not shots or any(not isinstance(s, Shot) for s in shots)
            or len({s.shot for s in shots}) != len(shots) or len({s.inputs.arm for s in shots}) != 1):
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


class Budget(ReceiptBudget):
    """Reuse durable exclusive receipts with this task's stricter fixed limits."""
    def __init__(self, directory, *, synthetic=False, evidence_root=None):
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        self.worker_lock = (directory / 'worker.lock').open('a')
        try:
            fcntl.flock(self.worker_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise BudgetReached('ONE_WORKER_REQUIRED') from exc
        path = directory / 'clock.json'
        if not path.exists():
            write_new(path, dict(LIMITS, started_unix=time.time(), task='SCI-MD-5CQA-TDS-001',
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
        if len(list(self.directory.glob('*.start.json'))) >= 366:
            raise BudgetReached('THREE_HUNDRED_SIXTY_SIX_START_CEILING')
        arm = fit_name.split('.')[0]
        if arm not in md.ARMS:
            raise ValueError('ARM_PREFIX_REQUIRED_IN_DURABLE_FIT_NAME')
        cap = 183
        if arm == 'S0':
            raise ValueError('S0_REQUIRES_ANALYTICAL_FIT')
        if len(list(self.directory.glob(arm+'.*.start.json'))) >= cap:
            raise BudgetReached('ARM_SPECIFIC_START_CEILING')
        return super().start(fit_name, index, parameters)


def fit(shots, regularization, parent_model, budget, name, source_identity, rights, *, scope='DEVELOPMENT'):
    problem = FitProblem(shots, regularization, parent_model, scope=scope)
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
            result = least_squares(residual, initial, bounds=(-20., 20.), method='trf',
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
                          nfev=None, njev=None, budget_failure=isinstance(exc, BudgetReached),
                          cancelled=isinstance(exc, (KeyboardInterrupt, SystemExit)))
            raise
        finally:
            record.update(arm=problem.arm, actual_residual_calls=calls,
                numerical_jacobian_residual_calls=numerical_calls,
                elapsed_seconds=time.monotonic()-started,
                boundary_indices=np.flatnonzero(np.abs(np.asarray(record['parameters'])) >= 20-1e-7).tolist(),
                peak_rss_kib=int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss))
            write_new(prefix.with_suffix(prefix.suffix+'.end.json'), record)
        results.append(record)
        budget.check()
    if not candidates or any(r.get('budget_failure') for r in results):
        return None, {'status': 'NONSELECTABLE', 'starts': results}
    best = min(candidates, key=lambda c: (c[0], c[1]))
    return problem.model(best[2], info, rights), {'status': 'CONVERGED', 'selected_start': best[1],
                                                'objective': best[0], 'starts': results}



class FitProblem:
    """Head-only objective; the supplied parent supplies every transform and curve."""
    def __init__(self, shots, regularization, parent_model, *, scope):
        validate(shots)
        self.arm, self.shots, self.regularization = shots[0].inputs.arm, shots, regularization
        if regularization not in LAMBDAS and not (self.arm == 'S0' and regularization is None):
            raise ValueError('DECLARED_LAMBDA_REQUIRED')
        if self.arm == 'S0' and regularization is not None:
            raise ValueError('S0_HAS_NO_LAMBDA')
        if scope not in ('SYNTHETIC', 'DEVELOPMENT', 'FINAL_FIT'):
            raise ValueError('DECLARED_FIT_SCOPE_REQUIRED')
        if not isinstance(parent_model, md.parent.Model) or parent_model.arm != 'C2':
            raise ValueError('VERIFIED_C2_PARENT_REQUIRED')
        pi = md.strict_json(parent_model.training_identity_json)
        ids, groups = {s.shot for s in shots}, {s.group for s in shots}
        if scope != 'SYNTHETIC':
            if pi.get('scope') != 'FIT_ONLY' or ids != set(pi['shots']) or groups != set(pi['groups']):
                raise ValueError('EXACT_PARENT_TRAINING_PROVENANCE_REQUIRED')
            if scope == 'FINAL_FIT' and parent_model.sha256 != md.FINAL_PARENT_SHA256:
                raise ValueError('FINAL_PARENT_CONTENT_MISMATCH')
        self.parent, self.scope = parent_model, scope
        n = len(md.head_feature_names(self.arm))
        self.means, self.minima, self.maxima = parent_model.means[:n], parent_model.minima[:n], parent_model.maxima[:n]
        self.domain = min(parent_model.domain_kg, max(w.end_kg for s in shots for w in s.windows))
        self.knots = parent_model.domain_kg
        self.windows = tuple(w for s in shots for w in s.windows)
        if any(w.end_kg > self.domain for w in self.windows):
            raise ValueError('TRAINING_WINDOW_OUTSIDE_PARENT_DOMAIN')
        self.row_shots = np.asarray([i for i, s in enumerate(shots) for w in s.windows], int)
        raw = np.asarray([s.inputs.values[:n] for s in shots]).reshape(len(shots), n)
        self.features = np.c_[np.ones(len(shots)), (raw-self.means)/md.SCALES[:n]]
        self.geometry = md.Geometry([w.start_kg for w in self.windows], [w.end_kg for w in self.windows], self.knots, self.domain)
        self.widths = np.asarray([w.end_kg-w.start_kg for w in self.windows])
        self.q = np.asarray([w.q for w in self.windows])
        self.weights = weights(shots)
        logits = np.asarray([parent_model.condition(md.parent.EarlyInput('C2', s.inputs.values, 'SOURCE_EARLY_INPUT')).logits for s in shots])
        self.parent_values = self.geometry.values(logits[self.row_shots])
        self.parent_average = self.geometry.integrate(logits[self.row_shots])/self.widths
        self.shape, self.size = (5, n+1), 5*(n+1)
        self.starts = []
        if self.arm == 'S0':
            return
        denominator = float(self.weights @ self.parent_average)
        if not np.isfinite(denominator) or denominator <= 0:
            raise ValueError('INVALID_PARENT_INITIALIZATION_DENOMINATOR')
        u = float(self.weights @ self.q)/denominator
        initial = float(logit(min(1-1e-8, max(1e-8, u))))
        for ramp in START_ORDER:
            theta = np.zeros(self.shape)
            theta[:, 0] = initial+ramp*np.linspace(-1, 1, 5)
            if np.any(np.abs(theta) > 20):
                raise ValueError('INITIALIZATION_OUTSIDE_BOUNDS')
            self.starts.append(theta.ravel())

    def residual(self, parameters):
        theta = np.asarray(parameters).reshape(self.shape)
        logits = (self.features @ theta.T)[self.row_shots]
        predicted = self.geometry.integrate(logits, self.parent_values)/self.widths
        data = 1000/.25*(predicted-self.q)*np.sqrt(self.weights)
        slopes = theta[:, 1:].ravel()
        second = (np.diff(theta, n=2, axis=0)/(.25**2)).ravel()
        return np.r_[data, slopes*np.sqrt(self.regularization/len(slopes)),
                     second*np.sqrt(self.regularization/len(second))]

    def model(self, parameters, provenance, rights, share=None):
        return md.Model(self.arm, () if self.arm == 'S0' else np.asarray(parameters).reshape(self.shape),
            self.means, self.minima, self.maxima, self.knots, self.domain, self.regularization, share,
            md.canonical(self.parent.to_dict()), md.canonical(provenance), rights)


def provenance(problem, name, source_identity):
    return {'scope': problem.scope, 'fit_name': name, 'campaign': 'FIT_2021_12', 'species': md.SPECIES,
            'shots': [s.shot for s in problem.shots], 'groups': sorted({s.group for s in problem.shots}),
            'training_projection_sha256': md.identity([asdict(s) for s in problem.shots]),
            'source_identity': source_identity, 'parent_content_sha256': problem.parent.sha256}


def bounded_scalar(x, y, w):
    x, y, w = (np.asarray(v, float) for v in (x, y, w))
    if (x.ndim != 1 or x.shape != y.shape or x.shape != w.shape or not len(x)
            or not np.isfinite([x, y, w]).all() or np.any(x < 0) or np.any(y < 0) or np.any(w <= 0)):
        raise ValueError('FINITE_NONNEGATIVE_SCALAR_DATA_AND_POSITIVE_WEIGHTS_REQUIRED')
    denominator, numerator = float(w @ x**2), float(w @ (x*y))
    if not np.isfinite([denominator, numerator]).all() or denominator <= 0:
        raise ValueError('INVALID_SCALAR_LS_DENOMINATOR')
    unconstrained = numerator/denominator
    if not np.isfinite(unconstrained):
        raise ValueError('NONFINITE_SCALAR_SOLUTION')
    r = float(np.clip(unconstrained, 0., 1.))
    return {'status': 'CLOSED_FORM', 'numerator': numerator, 'denominator': denominator,
            'unconstrained_share': unconstrained, 'share': r, 'boundary_solution': r in (0., 1.),
            'weighted_squared_residual_mg_g': float(w @ (1000*(r*x-y))**2)}


def fit_scalar(shots, parent_model, budget, name, source_identity, rights, *, scope='DEVELOPMENT'):
    budget.check()
    directory = budget.directory.parent/'scalar_fits'
    directory.mkdir(exist_ok=True)
    if len(list(directory.glob('*.start.json'))) >= 16:
        raise BudgetReached('SIXTEEN_CLOSED_FORM_FIT_CEILING')
    write_new(directory/(name+'.start.json'), {'fit': name, 'started_unix': time.time()})
    audit = {'fit': name, 'status': 'INCOMPLETE'}
    try:
        problem = FitProblem(shots, None, parent_model, scope=scope)
        audit.update(bounded_scalar(problem.parent_average, problem.q, problem.weights))
        model = problem.model(None, provenance(problem, name, source_identity), rights, share=audit['share'])
        audit['model_sha256'] = model.sha256
    except BaseException as exc:
        audit.update(status='FAILED', message=str(exc), cancelled=isinstance(exc, (KeyboardInterrupt, SystemExit)))
        raise
    finally:
        write_new(directory/(name+'.end.json'), audit)
    budget.check()
    return model, audit


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


def validate_parent_matrix(records, fold_specs, parents):
    groups = {r['group'] for r in records}
    if (len(groups) != 15 or set(parents) != groups or len(fold_specs) != 15
            or {s['group'] for s in fold_specs} != groups):
        raise ValueError('COMPLETE_FIFTEEN_PARENT_MATRIX_REQUIRED')
    for spec in fold_specs:
        group, parent = spec['group'], parents[spec['group']]
        held = {r['shot'] for r in records if r['group'] == group}
        retained = {r['shot'] for r in records if r['group'] != group}
        info = md.strict_json(parent.training_identity_json)
        if group in info['groups'] or held & set(info['shots']):
            raise ValueError('HELD_DESIGN_PARENT_LEAKAGE')
        if (set(info['shots']) != retained or set(info['groups']) != groups-{group}
                or parent.sha256 != spec['parent_sha256'] or parent.regularization != .0001):
            raise ValueError('EXACT_FOLD_PARENT_BINDING_REQUIRED')


def develop(records, fold_specs, parents, out, budget, source_identity, rights):
    validate_parent_matrix(records, fold_specs, parents)
    out = Path(out)
    summary = {'scope': 'DEVELOPMENT_NOT_UNBIASED_NESTED_VALIDATION', 'arms': {}}
    for arm in md.ARMS:
        shots = project_arm(records, arm)
        candidates = []
        for lam in (None,) if arm == 'S0' else LAMBDAS:
            result = {'lambda': lam, 'status': 'SELECTABLE', 'folds': []}
            for spec in fold_specs:
                group = spec['group']
                training, held = split_design(shots, group)
                parent_model = parents[group]
                name = f'{arm}.{lam}.{group}'
                model, audit = (fit_scalar(training, parent_model, budget, name, source_identity, rights)
                    if arm == 'S0' else fit(training, lam, parent_model, budget, name, source_identity, rights))
                fold = {'group': group, 'parent_sha256': parent_model.sha256,
                        'fit_status': audit['status'], 'support_sha256': md.identity(spec['support']), 'R_mg_g': None}
                try:
                    if model is None:
                        raise ValueError('FIT_FAILED')
                    fold.update(held_metrics(model, held, set(map(tuple, spec['support']))))
                    model.save(out/(name+'.model.json'))
                except ValueError as exc:
                    result['status'] = 'NONSELECTABLE'; fold['failure'] = str(exc)
                write_new(out/(name+'.audit.json'), audit)
                result['folds'].append(fold)
                print(name, fold['fit_status'], flush=True)
            for target, key in [('balanced_R_mg_g', 'R_mg_g'), ('R_allowance_mg_g', 'R_allowance_mg_g')]:
                result[target] = float(np.mean([f[key] for f in result['folds']])) if result['status'] == 'SELECTABLE' else None
            candidates.append(result)
        selected = select_lambda(candidates) if arm != 'S0' else None
        if arm == 'S0' and candidates[0]['status'] != 'SELECTABLE':
            raise ValueError('NONSELECTABLE_S0_DEVELOPMENT')
        summary['arms'][arm] = {'selected_lambda': selected, 'candidates': candidates}
        write_new(out/(arm+'.selection.json'), summary['arms'][arm])
    write_new(out/'development.json', summary)
    return summary

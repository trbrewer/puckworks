"""FIT-only grouped caffeine heads; retained parents are supplied, never fitted."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import resource
import sys
import time

import numpy as np
from scipy.optimize import least_squares
from scipy.special import logit

from . import conditional_caffeine_delivery as md
from .conditional_tail_training import Budget as Budget, BudgetReached, write_new

LAMBDAS = (.0001, .01, 1., 100.)
START_ORDER = (-1, 0, 1)


@dataclass(frozen=True)
class Window:
    fraction: int
    start_kg: float
    end_kg: float
    q: float

    def __post_init__(self):
        for k in ('start_kg', 'end_kg', 'q'):
            object.__setattr__(self, k, md.number(getattr(self, k)))
        if self.fraction not in (3, 5, 7, 10) or not 0 <= self.start_kg < self.end_kg or self.q < 0:
            raise ValueError('VALID_LATER_CAFFEINE_WINDOW_REQUIRED')


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
            raise ValueError('FIT_ONLY_INTACT_SHOT_REQUIRED')


def project_arm(records, arm):
    n = len(md.feature_names(arm))
    return tuple(Shot(r['shot'], r['group'], md.EarlyInput(arm, r['early_values'][:n], 'SOURCE_EARLY_INPUT'),
                      tuple(Window(**w) for w in r['windows'])) for r in records)


def validate(shots):
    if (not isinstance(shots, tuple) or not shots or any(not isinstance(s, Shot) for s in shots)
            or len({s.shot for s in shots}) != len(shots) or len({s.inputs.arm for s in shots}) != 1):
        raise ValueError('UNIQUE_IMMUTABLE_ARM_TRAINING_REQUIRED')


def weights(shots):
    groups = {s.group for s in shots}
    sw = [1/(len(groups)*sum(t.group == s.group for t in shots)) for s in shots]
    return np.asarray([sw[i]*(w.end_kg-w.start_kg)/sum(v.end_kg-v.start_kg for v in s.windows)
                       for i, s in enumerate(shots) for w in s.windows])


class FitProblem:
    def __init__(self, shots, regularization, parent_model, *, scope):
        validate(shots)
        self.arm, self.shots, self.regularization = shots[0].inputs.arm, shots, regularization
        if regularization not in LAMBDAS and not (self.arm == 'S0' and regularization is None):
            raise ValueError('DECLARED_LAMBDA_REQUIRED')
        if not isinstance(parent_model, md.parent.Model) or parent_model.arm != 'C2':
            raise ValueError('VERIFIED_C2_PARENT_REQUIRED')
        pi = md.strict_json(parent_model.training_identity_json)
        ids, groups = {s.shot for s in shots}, {s.group for s in shots}
        if scope != 'SYNTHETIC':
            if pi.get('scope') != 'FIT_ONLY' or not ids.issubset(pi['shots']) or not groups.issubset(pi['groups']):
                raise ValueError('PARENT_TRAINING_PROVENANCE_MISMATCH')
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
        self.masses = np.asarray([w.end_kg-w.start_kg for w in self.windows])
        self.q = np.asarray([w.q for w in self.windows])
        self.weights = weights(shots)
        self.parent_values = None
        self.parent_average = None
        if self.arm != 'D0':
            logits = np.asarray([parent_model.condition(md.parent.EarlyInput('C2', s.inputs.values, 'SOURCE_EARLY_INPUT')).logits for s in shots])
            self.parent_values = self.geometry.values(logits[self.row_shots])
            self.parent_average = self.geometry.integrate(logits[self.row_shots])/self.masses
        self.shape, self.size = (5, n+1), 5*(n+1)
        u = float(self.weights @ self.q)
        if self.arm != 'D0':
            denominator = float(self.weights @ self.parent_average)
            if denominator <= 0:
                raise ValueError('ZERO_PARENT_INITIALIZATION_DENOMINATOR')
            u /= denominator
        initial = float(logit(min(1-1e-8, max(1e-8, u))))
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
        predicted = self.geometry.integrate(logits, self.parent_values)/self.masses
        data = 1000/.50*(predicted-self.q)*np.sqrt(self.weights)
        slopes = theta[:, 1:].ravel()
        second = (np.diff(theta, n=2, axis=0)/(.25**2)).ravel()
        return np.r_[data, slopes*np.sqrt(self.regularization/len(slopes)),
                     second*np.sqrt(self.regularization/len(second))]

    def model(self, parameters, provenance, rights, share=None):
        return md.Model(self.arm, () if self.arm == 'S0' else np.asarray(parameters).reshape(self.shape),
            self.means, self.minima, self.maxima, self.knots, self.domain, self.regularization, share,
            md.canonical(self.parent.to_dict()) if self.arm != 'D0' else None,
            md.canonical(provenance), rights)


def provenance(problem, name, source_identity):
    return {'scope': problem.scope, 'fit_name': name, 'campaign': 'FIT_2021_12',
            'shots': [s.shot for s in problem.shots], 'groups': sorted({s.group for s in problem.shots}),
            'training_projection_sha256': md.identity([asdict(s) for s in problem.shots]),
            'source_identity': source_identity,
            'parent_content_sha256': problem.parent.sha256 if problem.arm != 'D0' else None}


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
            converged = bool(result.success and result.status > 0 and np.isfinite(result.x).all() and np.isfinite(objective))
            record.update(status='CONVERGED' if converged else 'NONCONVERGED', solver_status=int(result.status),
                message=str(result.message), objective=objective, parameters=result.x.tolist(), optimality=float(result.optimality),
                nfev=int(result.nfev), njev=int(result.njev))
            if converged:
                candidates.append((objective, index, result.x))
        except (ValueError, FloatingPointError, BudgetReached) as exc:
            record.update(status='FAILED', message=str(exc), parameters=last.tolist(), objective=last_objective,
                          nfev=None, njev=None, budget_failure=isinstance(exc, BudgetReached))
        record.update(actual_residual_calls=calls, numerical_jacobian_residual_calls=numerical_calls,
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


def fit_scalar(shots, parent_model, budget, name, source_identity, rights, *, scope='DEVELOPMENT'):
    budget.check()
    directory = budget.directory.parent/'scalar_fits'
    directory.mkdir(exist_ok=True)
    if len(list(directory.glob('*.start.json'))) >= 16:
        raise BudgetReached('SIXTEEN_CLOSED_FORM_FIT_CEILING')
    write_new(directory/(name+'.start.json'), {'fit': name, 'started_unix': time.time()})
    problem = FitProblem(shots, None, parent_model, scope=scope)
    x, y, w = problem.parent_average, problem.q, problem.weights
    denominator = float(w @ x**2)
    if denominator <= 0:
        raise ValueError('ZERO_SCALAR_LS_DENOMINATOR')
    unconstrained = float(w @ (x*y))/denominator
    r = min(1., max(0., unconstrained))
    model = problem.model(None, provenance(problem, name, source_identity), rights, share=r)
    audit = {'fit': name, 'unconstrained_share': unconstrained, 'share': r,
             'boundary_solution': r in (0., 1.), 'model_sha256': model.sha256,
             'weighted_squared_residual_mg_g': float(w @ (1000*(r*x-y))**2)}
    write_new(directory/(name+'.end.json'), audit)
    return model, audit


def held_metrics(model, shots, support):
    scores, allowance = [], 0.
    for shot in shots:
        ws = [w for w in shot.windows if (shot.shot, w.fraction) in support]
        if not ws:
            raise ValueError('MISSING_ORIGINAL_HELD_SHOT_SUPPORT')
        pred = model.condition(shot.inputs).predict_intervals([w.start_kg for w in ws], [w.end_kg for w in ws])
        if any(not p.numerical_qualified for p in pred):
            raise ValueError('NUMERICALLY_UNQUALIFIED_FOLD')
        err = [p.caffeine_mg_g-1000*w.q for p, w in zip(pred, ws)]
        mass = [w.end_kg-w.start_kg for w in ws]
        scores.append(float(np.sqrt(np.average(np.square(err), weights=mass))))
        allowance = max(allowance, max(p.allowance_kg for p in pred))
    return float(np.mean(scores)), allowance


def select_lambda(candidates):
    valid = [(c['balanced_R_mg_g'], c['lambda']) for c in candidates if c['status'] == 'SELECTABLE']
    if not valid:
        raise ValueError('NO_SELECTABLE_LAMBDA')
    low = min(v for v, _ in valid)
    return max(lam for v, lam in valid if v <= low+1e-6)


def develop(records, fold_specs, parents, out, budget, source_identity, rights):
    out = Path(out)
    summary = {'scope': 'DEVELOPMENT_NOT_UNBIASED_NESTED_VALIDATION', 'arms': {}}
    for arm in ('D0', 'S1', 'S2', 'S0'):
        shots = project_arm(records, arm)
        candidates = []
        for lam in (None,) if arm == 'S0' else LAMBDAS:
            result = {'lambda': lam, 'status': 'SELECTABLE', 'folds': []}
            for spec in fold_specs:
                group = spec['group']
                training = tuple(s for s in shots if s.group != group)
                held = tuple(s for s in shots if s.group == group)
                parent_model = parents[group]
                pi = md.strict_json(parent_model.training_identity_json)
                if group in pi['groups'] or any(s.shot in pi['shots'] for s in held):
                    raise ValueError('HELD_DESIGN_PARENT_LEAKAGE')
                name = f'{arm}.{lam}.{group}'
                model, audit = (fit_scalar(training, parent_model, budget, name, source_identity, rights)
                    if arm == 'S0' else fit(training, lam, parent_model, budget, name, source_identity, rights))
                fold = {'group': group, 'parent_sha256': parent_model.sha256, 'fit_status': audit.get('status', 'CLOSED_FORM'),
                        'support_sha256': md.identity(spec['support']), 'R_mg_g': None}
                try:
                    if model is None:
                        raise ValueError('FIT_FAILED')
                    fold['R_mg_g'], fold['max_allowance_kg'] = held_metrics(model, held, set(map(tuple, spec['support'])))
                    model.save(out/(name+'.model.json'))
                except ValueError as exc:
                    result['status'] = 'NONSELECTABLE'
                    fold['failure'] = str(exc)
                write_new(out/(name+'.audit.json'), audit)
                result['folds'].append(fold)
                print(name, fold['fit_status'], flush=True)
            result['balanced_R_mg_g'] = float(np.mean([f['R_mg_g'] for f in result['folds']])) if result['status'] == 'SELECTABLE' else None
            candidates.append(result)
        try:
            selected = select_lambda(candidates) if arm != 'S0' else None
        except ValueError:
            selected = None
        summary['arms'][arm] = {'selected_lambda': selected, 'candidates': candidates}
        write_new(out/(arm+'.selection.json'), summary['arms'][arm])
    write_new(out/'development.json', summary)
    return summary

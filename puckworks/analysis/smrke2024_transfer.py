"""Four source-conditioned, across-shot endpoint responses; never production physics.

Times are machine-reported seconds, yields source-basis percentage points, and
fines are nominal replacement grams / 20 g. See the frozen task CONTRACT.md.
Prediction accepts covariates only. No within-shot rates or physical tau claim.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
from typing import Literal, Sequence

import numpy as np
import scipy
from scipy.optimize import minimize, minimize_scalar

Model = Literal['M0', 'M1', 'B0', 'B1']
MODELS = ('M0', 'M1', 'B0', 'B1')
LEVELS = {'no_added_fines': 0., '1g_fines': 1., '2g_fines': 2., '4g_fines': 4.}
SOURCE = 'smrke2024/fig3_ey_vs_time'
UNITS = ('s', 'source_yield_pp', 'g')
DOMAIN = (7.9, 80.)
DOC = Path(__file__).resolve().parents[2] / 'docs/analysis/sci_md_smrke_transfer_001'
# Visually established connected/occluding positions, NOT area-derived identities.
BLOBS = {**dict.fromkeys([2, 3, 4], 'blue12'), **dict.fromkeys([12, 13, 32], 'mixed17'),
         **dict.fromkeys([28, 29, 31], 'black9'), **dict.fromkeys([35, 36], 'black23'),
         **dict.fromkeys([40, 41], 'black46')}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    """Exclusive deterministic writes preserve previous attempts and predictions."""
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


@dataclass(frozen=True)
class Covariate:
    row_id: str
    time_s: float
    level: str
    source: str = SOURCE
    units: tuple[str, str, str] = UNITS

    def __post_init__(self) -> None:
        if not isinstance(self.row_id, str) or not self.row_id or self.source != SOURCE:
            raise ValueError('Malformed row or incompatible fitted-source identity')
        if self.level not in LEVELS or tuple(self.units) != UNITS:
            raise ValueError('Malformed intervention label or incompatible units')
        if not np.isfinite(self.time_s) or self.time_s <= 0:
            raise ValueError('Time must be finite and positive')

    @property
    def f(self) -> float:
        return LEVELS[self.level] / 20.


@dataclass(frozen=True)
class Observation:
    covariate: Covariate
    yield_pp: float
    markers_in_blob: int = 1
    note: str = ''
    blob: str | None = None

    def __post_init__(self) -> None:
        if not np.isfinite(self.yield_pp) or not 0 <= self.yield_pp <= 100:
            raise ValueError('Invalid source-basis yield')
        if type(self.markers_in_blob) is not int or self.markers_in_blob < 1:
            raise ValueError('Invalid ambiguity metadata')

    @property
    def primary(self) -> bool:
        return self.markers_in_blob == 1 and not self.note.strip()


def source_rows() -> list[Observation]:
    """Load unchanged historical marker rows; row_id is CSV line, never shot ID."""
    from puckworks.data import smrke2024_figures
    rows = smrke2024_figures()['fig3_ey_vs_time']
    return [Observation(Covariate(f'Fig3:L{i}', float(r['extraction_time_s']), r['series']),
                        float(r['extraction_pct']), int(r['markers_in_blob']), r['note'],
                        BLOBS.get(i)) for i, r in enumerate(rows, 2)]


def weights(rows: Sequence[Observation]) -> np.ndarray:
    """Equal intervention weight, then equal marker weight within intervention."""
    groups = [r.covariate.level for r in rows]
    return np.array([1 / (len(set(groups)) * groups.count(g)) for g in groups])


def folds(rows: Sequence[Observation], protocol: str):
    """Whole-level folds with no row overlap; A trains only zero fines."""
    if protocol not in ('A', 'B'):
        raise ValueError('Unknown protocol')
    for level in LEVELS:
        if protocol == 'A' and level == 'no_added_fines':
            continue
        train = [r for r in rows if (r.covariate.level == 'no_added_fines' if protocol == 'A'
                                    else r.covariate.level != level)]
        test = [r for r in rows if r.covariate.level == level]
        yield level, train, test


def eligible_support(rows: Sequence[Observation]) -> dict:
    """Pre-fit coverage; at least three supported markers per scored arm/fold."""
    report = {}
    for protocol in ('A', 'B'):
        report[protocol] = {}
        for level, train, test in folds(rows, protocol):
            times = [r.covariate.time_s for r in train]
            bounds = [min(times), max(times)] if times else None
            kept = [r.covariate.row_id for r in test if bounds and
                    bounds[0] <= r.covariate.time_s <= bounds[1]]
            report[protocol][level] = dict(training_n=len(train), eligible_n=len(test),
                training_time_range=bounds, supported=kept,
                excluded=[r.covariate.row_id for r in test if r.covariate.row_id not in kept])
    report['sufficient'] = (len({r.covariate.time_s for r in rows
                                if r.covariate.level == 'no_added_fines'}) >= 3 and
                            all(len(v['supported']) >= 3 for p in ('A', 'B')
                                for v in report[p].values()))
    return report


def design(model: Model, time: np.ndarray, f: np.ndarray, tau: float = 1.) -> np.ndarray:
    if model.startswith('M'):
        columns = [np.ones_like(time), -np.exp(-time / tau)]
    else:
        x = np.log(time) - 3.2
        columns = [np.ones_like(time), x, x*x]
    if model.endswith('1'):
        columns.append(f / .2)  # internal scaling; output coefficient is per unit f
    return np.column_stack(columns)


def constraints(model: Model, tau: float, domain: tuple[float, float]):
    n = (2 if model.startswith('M') else 3) + model.endswith('1')
    time = np.array([domain[0], domain[1], domain[0], domain[1]])
    f = np.array([0., 0., .2, .2])
    ends = design(model, time, f, tau)
    c = [*ends, *(-ends)]
    d = [*np.zeros(4), *np.full(4, -100.)]
    if model.startswith('M'):
        # E_inf >= A >= 0 and E_inf <= 100
        v = np.zeros(n); v[0] = 1; v[1] = -1
        a = np.zeros(n); a[1] = 1
        upper = np.zeros(n); upper[0] = -1
        c += [v, a, upper]; d += [0., 0., -100.]
    else:
        # dE/dlog(t) linear: endpoints suffice throughout interval.
        for x in np.log(domain):
            v = np.zeros(n); v[1] = 1; v[2] = 2*(x-3.2)
            c.append(v); d.append(0.)
    return np.array(c), np.array(d)


@dataclass(frozen=True)
class Fitted:
    model: Model
    parameters: tuple[float, ...]
    train_ids: tuple[str, ...]
    time_support: tuple[float, float]
    fines_support: tuple[float, float]
    domain: tuple[float, float]
    source: str
    diagnostics: dict

    def predict(self, covariates: Sequence[Covariate]) -> list[dict]:
        """Predict without test yields, returning separate support flags; never clip."""
        p = list(self.parameters)
        tau = p.pop(2) if self.model.startswith('M') else 1.
        if self.model.startswith('B'):
            p[:3] = [p[0]+3.2*p[1]+3.2**2*p[2], p[1]+6.4*p[2], p[2]]
        if self.model.endswith('1'):
            p[-1] *= .2
        output = []
        for c in covariates:
            if not isinstance(c, Covariate) or c.source != self.source:
                raise ValueError('Prediction requires covariates from fitted source')
            if not self.domain[0] <= c.time_s <= self.domain[1]:
                raise ValueError('Outside declared admissible comparison domain')
            value = float((design(self.model, np.array([c.time_s]), np.array([c.f]), tau) @ p)[0])
            if not -1e-7 <= value <= 100 + 1e-7:
                raise RuntimeError('Inadmissible prediction; no clipping permitted')
            output.append(dict(row_id=c.row_id, time_s=c.time_s, level=c.level,
                prediction_pp=value, time_supported=self.time_support[0] <= c.time_s <= self.time_support[1],
                intervention_supported=self.fines_support[0] <= c.f <= self.fines_support[1],
                intervention_used=self.model.endswith('1'), fitted_source=self.source))
        return output


def fit(model: Model, rows: Sequence[Observation], *, domain: tuple[float, float] = DOMAIN,
        tight: bool = False) -> Fitted:
    """Deterministic constrained weighted least squares; M profiles log(tau).

    Fixed log grid plus bounded scalar refinement of each grid-local minimum.
    Inner convex quadratic uses analytic gradient and fixed feasible initialization.
    Failed optimization is explicit; no fallback fit or target-dependent rescue.
    """
    if model not in MODELS or len(rows) < 3:
        raise ValueError('Unknown model or insufficient training markers')
    if len(set(r.covariate.row_id for r in rows)) != len(rows):
        raise ValueError('Repeated observation identity')
    if len(domain) != 2 or not np.all(np.isfinite(domain)) or not 0 < domain[0] < domain[1]:
        raise ValueError('Invalid domain')
    t = np.array([r.covariate.time_s for r in rows])
    f = np.array([r.covariate.f for r in rows])
    y = np.array([r.yield_pp for r in rows])
    if min(t) < domain[0] or max(t) > domain[1] or len(set(t)) < 3:
        raise ValueError('Insufficient or out-of-domain training support')
    if model.endswith('1') and len(set(f)) < 2:
        raise ValueError('Fines coefficient unidentifiable in single-arm training')
    w = weights(rows)
    failures = []

    def solve(logtau: float):
        tau = float(np.exp(logtau))
        x = design(model, t, f, tau)
        c, d = constraints(model, tau, domain)
        start = np.zeros(x.shape[1]); start[0] = 50.
        result = minimize(lambda q: float(np.sum(w * (x @ q-y)**2)), start,
            jac=lambda q: 2*x.T @ (w*(x @ q-y)), method='SLSQP',
            constraints={'type': 'ineq', 'fun': lambda q: c @ q-d, 'jac': lambda q: c},
            options={'ftol': 1e-13 if tight else 1e-11, 'maxiter': 2000})
        if not result.success or np.min(c @ result.x-d) < -1e-7:
            failures.append(dict(logtau=logtau, message=str(result.message)))
            return float('inf'), result.x, tau, result.nit
        return float(result.fun), result.x, tau, result.nit

    candidates = []
    if model.startswith('M'):
        grid = np.linspace(np.log(.1), np.log(10000.), 129 if tight else 65)
        prof = [solve(float(v)) for v in grid]
        candidates = list(prof)
        for i in range(1, len(grid)-1):
            if prof[i][0] <= prof[i-1][0] and prof[i][0] <= prof[i+1][0]:
                result = minimize_scalar(lambda z: solve(float(z))[0], bounds=(grid[i-1], grid[i+1]),
                    method='bounded', options={'xatol': 1e-11 if tight else 1e-8, 'maxiter': 300})
                if not result.success:
                    raise RuntimeError('Outer profile did not converge')
                candidates.append(solve(float(result.x)))
    else:
        candidates = [solve(0.)]
    best = min(candidates, key=lambda v: v[0])
    if not np.isfinite(best[0]) or failures:
        raise RuntimeError(f'Constrained fit failed: {failures}')
    objective, q, tau, nit = best
    c, d = constraints(model, tau, domain)
    parameters = list(map(float, q))
    if model.startswith('B'):
        parameters[:3] = [float(q[0]-3.2*q[1]+3.2**2*q[2]), float(q[1]-6.4*q[2]), float(q[2])]
    if model.endswith('1'):
        parameters[-1] /= .2
    if model.startswith('M'):
        parameters.insert(2, tau)
    # Profile-near-optimum spread is numerical/identifiability diagnostic only.
    near = [v for v in candidates if v[0] <= objective + 1e-6]
    tt = np.linspace(*domain, 101)
    values = np.stack([design(model, tt, np.full_like(tt, .1), v[2]) @ v[1] for v in near])
    x = design(model, t, f, tau)
    if model.startswith('M'):
        x = np.column_stack([x, -q[1]*np.exp(-t/tau)*t/tau])  # log tau Jacobian
    singular = np.linalg.svd(np.sqrt(w)[:, None]*x, compute_uv=False)
    condition = float(singular[0]/singular[-1]) if singular[-1] > 1e-15 else None
    extrema = []
    if model.startswith('B') and q[2] != 0:
        vertex = 3.2-q[1]/(2*q[2])
        if np.log(domain[0]) < vertex < np.log(domain[1]):
            for ff in [0., .2]:
                value = float((design(model, np.array([np.exp(vertex)]), np.array([ff])) @ q)[0])
                if not -1e-7 <= value <= 100+1e-7:
                    raise RuntimeError('Invalid analytical quadratic extremum')
                extrema.append(dict(time_s=float(np.exp(vertex)), f=ff, yield_pp=value))
    return Fitted(model, tuple(parameters), tuple(r.covariate.row_id for r in rows),
        (float(min(t)), float(max(t))), (float(min(f)), float(max(f))), domain, SOURCE,
        dict(converged=True, objective=objective, iterations=nit, failures=failures,
             active_constraints=np.flatnonzero(c @ q-d < 1e-6).tolist(),
             tau_bound_hit=bool(model.startswith('M') and (tau < .100001 or tau > 9999.99)),
             near_profile_tau_range=[min(v[2] for v in near), max(v[2] for v in near)],
             near_profile_prediction_spread_pp=float(np.max(np.ptp(values, axis=0))),
             jacobian_condition=condition, analytical_interior_extrema=extrema))


def treatments(rows: Sequence[Observation]):
    """Central + four global and four connected-position sign perturbations."""
    for inclusion in ('primary', 'all'):
        selected = [r for r in rows if inclusion == 'all' or r.primary]
        yield inclusion + ':central', selected
        for kind in ('global', 'position'):
            for st, sy in itertools.product((-1, 1), repeat=2):
                changed = []
                for r in selected:
                    key = r.blob or r.covariate.row_id
                    # One common sign per genuine occluding position across colors.
                    sign = 1 if kind == 'global' else (1 if hashlib.sha256(key.encode()).digest()[0] % 2 else -1)
                    dt, dy = (.09, .011) if r.primary else (.30, .05)
                    changed.append(replace(r, covariate=replace(r.covariate,
                        time_s=r.covariate.time_s + st*sign*dt), yield_pp=r.yield_pp + sy*sign*dy))
                yield f'{inclusion}:{kind}:{st}:{sy}', changed


def metrics(residuals: Sequence[float]) -> dict:
    if not residuals:
        return dict(n=0, rmse=None, mae=None, mean_error=None, max_abs_error=None)
    e = np.array(residuals)
    return dict(n=len(e), rmse=float(np.sqrt(np.mean(e*e))), mae=float(np.mean(abs(e))),
                mean_error=float(np.mean(e)), max_abs_error=float(max(abs(e))))


def gain(parent: Sequence[dict], corrected: Sequence[dict]) -> dict:
    """Frozen equal-arm materiality test; zero/insufficient support never passes."""
    if len(parent) != 4 or len(corrected) != 4 or any(v['n'] < 3 for v in [*parent, *corrected]):
        return dict(material=None, reason='INSUFFICIENT_SUPPORT')
    p = np.array([v['rmse'] for v in parent]); c = np.array([v['rmse'] for v in corrected])
    bp, bc = float(np.sqrt(np.mean(p*p))), float(np.sqrt(np.mean(c*c)))
    reduction = (bp-bc)/bp if bp > 0 else 0.
    return dict(parent_balanced_rmse=bp, correction_balanced_rmse=bc,
        absolute_gain_pp=bp-bc, relative_gain=reduction, per_arm_rmse_change=(c-p).tolist(),
        interior_nonworse=bool(np.all(c[1:3] <= p[1:3])),
        interior_positive_gain=bool(np.any(c[1:3] < p[1:3])),
        material=bool(reduction >= .2 and bp-bc >= .1 and np.all(c[1:3] <= p[1:3]) and np.any(c[1:3] < p[1:3]) and np.all(c-p <= .1)))


def adjudicate(reports: dict, numerical_ok: bool) -> dict:
    """Require one named model/correction to survive every source treatment."""
    adequate = {m: [] for m in ('M0', 'B0')}
    material = {m: [] for m in ('M1', 'B1')}
    for report in reports.values():
        for model in adequate:
            arms = [report['A'][level][model]['supported'] for level in list(LEVELS)[1:]]
            adequate[model].append(None if any(a['n'] < 3 for a in arms) else
                all(a['rmse'] <= .5 and abs(a['mean_error']) <= .25 for a in arms))
        for model in material:
            material[model].append(report['gain'][model]['material'])
    common = ('ADEQUATE_FOR_TESTED_SOURCE_SUPPORT' if any(all(v is True for v in a) for a in adequate.values())
              else 'TESTED_COMMON_MODELS_INADEQUATE' if all(all(v is False for v in a) for a in adequate.values())
              else 'UNRESOLVED')
    fines = ('MATERIAL_OUT_OF_FIT_GAIN_FOR_TESTED_CORRECTION' if any(all(v is True for v in a) for a in material.values())
             else 'NO_MATERIAL_GAIN_FOR_TESTED_CORRECTIONS' if all(all(v is False for v in a) for a in material.values())
             else 'UNRESOLVED')
    return dict(COMMON_TIME_RESPONSE=common if numerical_ok else 'UNRESOLVED',
                FINES_COVARIATE_INCREMENT=fines if numerical_ok else 'UNRESOLVED',
                adequate_by_treatment=adequate, material_by_treatment=material)


def prepare(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    rows = source_rows()
    write_json(output/'observations.json', [asdict(r) for r in rows])
    write_json(output/'support.json', {name: eligible_support(rs) for name, rs in treatments(rows)})
    if not eligible_support([r for r in rows if r.primary])['sufficient']:
        raise RuntimeError('PRIMARY_SUPPORT_INSUFFICIENT; stop before fitting')


def read_rows(path: Path) -> list[Observation]:
    return [Observation(Covariate(**r['covariate']), r['yield_pp'], r['markers_in_blob'], r['note'], r['blob'])
            for r in json.loads(path.read_text())]


def verify_audit() -> dict:
    """Bind the real independent receipt to reviewed tree and scientific file hashes."""
    freeze = json.loads((DOC/'FREEZE.json').read_text())
    audit = json.loads((DOC/'AUDIT.json').read_text())
    root = DOC.parents[2]
    if audit.get('disposition') != 'PASS' or audit.get('freeze_sha256') != digest(DOC/'FREEZE.json'):
        raise RuntimeError('Independent pre-scoring PASS required')
    if not audit.get('reviewer') or not audit.get('independent_of_implementation_author'):
        raise RuntimeError('Independent reviewer identity missing')
    tree = subprocess.check_output(['git', 'rev-parse', audit['reviewed_head']+'^{tree}'], cwd=root, text=True).strip()
    if tree != audit['reviewed_tree'] or audit['base_commit'] != freeze['base_commit']:
        raise RuntimeError('Reviewed candidate/base mismatch')
    subprocess.run(['git', 'merge-base', '--is-ancestor', audit['base_commit'], audit['reviewed_head']], cwd=root, check=True)
    for name, expected in freeze['files'].items():
        if digest(root/name) != expected:
            raise RuntimeError('Frozen scientific file changed: '+name)
        reviewed = subprocess.check_output(['git', 'show', audit['reviewed_head']+':'+name], cwd=root)
        if hashlib.sha256(reviewed).hexdigest() != expected:
            raise RuntimeError('Receipt does not cover scientific file: '+name)
    return audit


def fit_predict(output: Path) -> None:
    audit = verify_audit()
    if digest(output/'observations.json') != digest(DOC/'observations.json'):
        raise RuntimeError('Prepared observation identity mismatch')
    rows = read_rows(output/'observations.json')
    bundles = {}
    for treatment, rs in treatments(rows):
        bundles[treatment] = {}
        for precision in ('standard', 'tight'):
            bundle = {}
            for protocol in ('A', 'B'):
                bundle[protocol] = {}
                common = {}
                for level, train, test in folds(rs, protocol):
                    bundle[protocol][level] = {}
                    for model in (('M0', 'B0') if protocol == 'A' else MODELS):
                        fitted = common.get(model) if protocol == 'A' else None
                        if fitted is None:
                            fitted = fit(model, train, tight=precision == 'tight')
                            if protocol == 'A':
                                common[model] = fitted
                        # Only covariates cross the prediction interface.
                        predictions = fitted.predict([r.covariate for r in test])
                        bundle[protocol][level][model] = dict(fit=asdict(fitted), predictions=predictions)
            bundles[treatment][precision] = bundle
    write_json(output/'predictions.json', bundles)
    write_json(output/'PREDICTION_RECEIPT.json', dict(predictions_sha256=digest(output/'predictions.json'),
        observations_sha256=digest(output/'observations.json'), audit_sha256=digest(DOC/'AUDIT.json'),
        freeze_sha256=digest(DOC/'FREEZE.json'), reviewed_head=audit['reviewed_head'],
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__))


def score(output: Path) -> None:
    verify_audit()
    receipt = json.loads((output/'PREDICTION_RECEIPT.json').read_text())
    for name, key in [('predictions.json', 'predictions_sha256'), ('observations.json', 'observations_sha256')]:
        if digest(output/name) != receipt[key]:
            raise RuntimeError('Prediction freeze or observations altered')
    if receipt['audit_sha256'] != digest(DOC/'AUDIT.json') or receipt['freeze_sha256'] != digest(DOC/'FREEZE.json'):
        raise RuntimeError('Audit/freeze changed after prediction')
    bundles = json.loads((output/'predictions.json').read_text())
    source = dict(treatments(read_rows(output/'observations.json')))
    reports, tight_reports, residuals = {}, {}, []
    differences = []
    for treatment, versions in bundles.items():
        truth = {r.covariate.row_id: r.yield_pp for r in source[treatment]}
        for precision, protocols in versions.items():
            report = {}
            for protocol, arms in protocols.items():
                report[protocol] = {}
                for level, models in arms.items():
                    report[protocol][level] = {}
                    for model, bundle in models.items():
                        rows = []
                        for pred in bundle['predictions']:
                            e = pred['prediction_pp']-truth[pred['row_id']]
                            row = dict(**pred, observed_pp=truth[pred['row_id']], residual_pp=e,
                                treatment=treatment, precision=precision, protocol=protocol, model=model)
                            residuals.append(row); rows.append(row)
                        report[protocol][level][model] = {
                            category: metrics([r['residual_pp'] for r in rows if r['time_supported'] == supported])
                            for category, supported in [('supported', True), ('extrapolation', False)]}
            report['gain'] = {model: gain([report['B'][l][parent]['supported'] for l in LEVELS],
                                          [report['B'][l][model]['supported'] for l in LEVELS])
                              for parent, model in [('M0', 'M1'), ('B0', 'B1')]}
            (reports if precision == 'standard' else tight_reports)[treatment] = report
    for treatment in reports:
        for protocol in ('A', 'B'):
            for level, models in reports[treatment][protocol].items():
                for model, categories in models.items():
                    for category, vals in categories.items():
                        other = tight_reports[treatment][protocol][level][model][category]
                        for metric in ('rmse', 'mae', 'mean_error', 'max_abs_error'):
                            if vals[metric] is not None:
                                differences.append(abs(vals[metric]-other[metric]))
    max_change = max(differences)
    verdict = adjudicate(reports, max_change <= .01)
    tight_verdict = adjudicate(tight_reports, True)
    for key in ('COMMON_TIME_RESPONSE', 'FINES_COVARIATE_INCREMENT'):
        if verdict[key] != tight_verdict[key]:
            verdict[key] = 'UNRESOLVED'
    write_json(output/'residuals.json', residuals)
    write_json(output/'metrics.json', dict(standard=reports, tight=tight_reports,
        numerical_max_metric_change_pp=max_change, verdict=verdict,
        predictions_sha256=receipt['predictions_sha256']))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', choices=['prepare', 'fit-predict', 'score'])
    parser.add_argument('--output', type=Path, default=DOC)
    args = parser.parse_args()
    {'prepare': prepare, 'fit-predict': fit_predict, 'score': score}[args.step](args.output)


if __name__ == '__main__':
    main()

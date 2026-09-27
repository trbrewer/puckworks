"""Research-only first-two-assay delivery; no source or outcome access.

See the task model card for the monotonicity proof and frozen numerical budgets.
First-party software; source-derived bases and observations retain their rights.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from . import anchored_mass_delivery as legacy
from . import mass_delivery as kernel

VERSION = 'two-assay-mass-delivery/1'
B_REF = .01
K_MAX = 10000.
ARMS = ('TWO_ASSAY_MASS', 'TWO_ASSAY_EXPONENTIAL', 'TWO_ASSAY_FIXED_MASS',
        'TWO_ASSAY_FIXED_EMPIRICAL', 'SECOND_ASSAY_EMPIRICAL', 'FIRST_ASSAY_EMPIRICAL')
UNITS = {'beverage': 'kg', 'solute': 'kg', 'TDS': 'percent', 'basis': 'MASS',
         'A': 'kg/kg', 'k': 'kg^-1', 'lambda': '1', 'TDS_sensitivity': 'pp/pp'}
CLAIMS = kernel.LIMITATIONS + ('TWO_ASSAY_CONDITIONED_NOT_RECIPE_ONLY',
    'SCALE_NOT_INVENTORY_RATE_NOT_PHYSICAL_KINETICS', 'NO_REAL_TIME_ASSAY_CLAIM',
    'ASSAYED_SUPPORT_NOT_MEASURED_WHOLE_CUP')
REAL_LABELS = ('SOURCE_INTERNAL', 'TARGET_EXPOSED',
               'RETROSPECTIVE_TWO_ASSAY_CONDITIONED_COMPARISON')
RUNTIME_MODULES = ('mass_delivery.py', 'conditioned_mass_delivery.py',
                   'anchored_mass_delivery.py', 'two_assay_mass_delivery.py')
IntervalQuery = legacy.IntervalQuery
FrozenBase = legacy.FrozenBase
finite = legacy.finite
strict_json = legacy.strict_json


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':'))


def runtime_identity():
    return {n: hashlib.sha256(Path(__file__).with_name(n).read_bytes()).hexdigest()
            for n in RUNTIME_MODULES}


@dataclass(frozen=True)
class Observation:
    shot_id: str
    source_id: str
    fraction_id: int
    start_kg: float
    end_kg: float
    tds_percent: float
    mass_basis: str
    rights: str
    input_class: str
    tds_basis: str = 'MASS'
    tds_unit: str = 'percent'

    def __post_init__(self):
        IntervalQuery(self.start_kg, self.end_kg)
        finite(self.tds_percent)
        if self.end_kg <= self.start_kg or not 0 <= self.tds_percent <= 100:
            raise ValueError('INVALID_OBSERVATION_MASS_OR_TDS')
        if type(self.fraction_id) is not int or self.fraction_id not in (1, 2):
            raise ValueError('FIRST_TWO_FRACTION_IDENTITIES_REQUIRED')
        if not all(isinstance(v, str) and v for v in (self.shot_id, self.source_id, self.rights)):
            raise ValueError('OBSERVATION_IDENTITY_AND_RIGHTS_REQUIRED')
        roles = {'SYNTHETIC_TWO_ASSAY_INPUT': 'SYNTHETIC_KG',
                 'MEASURED_SOURCE_TWO_ASSAY_INPUT': 'MEASURED_MASS_G_CONVERTED_TO_KG'}
        if roles.get(self.input_class) != self.mass_basis:
            raise ValueError('UNSUPPORTED_INFORMATION_ROLE_OR_MASS_BASIS')
        if self.tds_basis != 'MASS' or self.tds_unit != 'percent':
            raise ValueError('UNSUPPORTED_TDS_BASIS_OR_UNIT')

    @property
    def width(self):
        return self.end_kg-self.start_kg

    @property
    def q(self):
        return self.tds_percent/100


@dataclass(frozen=True)
class ObservationPair:
    first: Observation
    second: Observation

    def __post_init__(self):
        if type(self.first) is not Observation or type(self.second) is not Observation:
            raise ValueError('TYPED_OBSERVATION_PAIR_REQUIRED')
        a, b = self.first, self.second
        if (a.fraction_id, b.fraction_id) != (1, 2) or a.end_kg > b.start_kg:
            raise ValueError('ORDERED_NONOVERLAPPING_FIRST_TWO_REQUIRED')
        for key in ('shot_id', 'source_id', 'rights', 'input_class', 'mass_basis'):
            if getattr(a, key) != getattr(b, key):
                raise ValueError('PAIR_IDENTITY_RIGHTS_OR_ROLE_MISMATCH')

    @classmethod
    def from_dict(cls, value):
        try:
            if set(value) != {'first', 'second'}:
                raise ValueError('PAIR_SCHEMA_MISMATCH')
            return cls(Observation(**value['first']), Observation(**value['second']))
        except (TypeError, KeyError) as exc:
            raise ValueError('PAIR_SCHEMA_MISMATCH') from exc


class FitFailure(ValueError):
    """A scientific or numerical failure with every attempted solve retained."""
    def __init__(self, status, attempts=()):
        super().__init__(status)
        self.status = status
        self.attempts = tuple(attempts)


def shape_average(start, end, lam, p, method=128):
    """Unit-amplitude mean, with no reset of the original mass origin."""
    if lam == 0:
        return 1.
    if method == 'reference':
        if p == 1:
            k = lam/B_REF
            return math.exp(-k*start)*(-math.expm1(-k*(end-start)))/(k*(end-start))
        return float(quad(lambda u: math.exp(-lam*((start+(end-start)*u)/B_REF)**p),
                          0, 1, epsabs=1e-14, epsrel=2e-13, limit=200)[0])
    u, w = kernel.quadrature(method)
    return float(np.dot(w, np.exp(-lam*((start+(end-start)*u)/B_REF)**p))/sum(w))


def shape_derivative(start, end, lam, p):
    u, w = kernel.quadrature(256)
    x = ((start+(end-start)*u)/B_REF)**p
    return -float(np.dot(w, x*np.exp(-lam*x))/sum(w))


def qualified_average(start, end, lam, p):
    primary = shape_average(start, end, lam, p)
    if lam == 0:
        return primary, 0.
    refined = shape_average(start, end, lam, p, 256)
    reference = shape_average(start, end, lam, p, 'reference')
    error = 0.
    if p != 1:
        _, error = quad(lambda u: math.exp(-lam*((start+(end-start)*u)/B_REF)**p),
                        0, 1, epsabs=1e-14, epsrel=2e-13, limit=200)
    allowance = max(abs(primary-refined), abs(primary-reference)+error) + legacy.roundoff(primary)
    return primary, allowance


def ratio(pair, lam, p, method=128):
    a, b = pair.first, pair.second
    f1 = shape_average(a.start_kg, a.end_kg, lam, p, method)
    f2 = shape_average(b.start_kg, b.end_kg, lam, p, method)
    if f1 <= 0 or not math.isfinite(f1+f2):
        raise ValueError('NUMERICALLY_UNRESOLVED_RATIO_DENOMINATOR')
    return f2/f1


def ratio_bounds(pair, lam, p):
    (f1, e1), (f2, e2) = [qualified_average(o.start_kg, o.end_kg, lam, p)
                          for o in (pair.first, pair.second)]
    if f1-e1 <= 0 or e1/f1 > 1e-6 or f2 <= 0 or e2/f2 > 1e-6:
        raise ValueError('NUMERICALLY_UNRESOLVED_CONDITIONING_DENOMINATOR')
    return ((f2-e2)/(f1+e1), (f2+e2)/(f1-e1)), max(e1/f1, e2/f2)


def solve(pair, p, method, tolerance):
    target = pair.second.q/pair.first.q
    lo, hi = 0., (K_MAX*B_REF)**p
    record = {'method': str(method), 'atol': tolerance, 'rtol': tolerance,
              'initial_bracket_lambda': [lo, hi], 'function_calls': 0, 'iterations': 0}
    def fn(x):
        record['function_calls'] += 1
        return ratio(pair, x, p, method)-target
    try:
        low, high = fn(lo), fn(hi)
        record['endpoint_residuals'] = [low, high]
        if low < 0 or high > 0:
            raise ValueError('NO_FINITE_BRACKET_WITHIN_COMPUTATIONAL_RATE_CEILING')
        if high == 0:
            lo = hi
        for iteration in range(100):
            record['iterations'] = iteration+1
            if hi-lo <= tolerance+tolerance*abs((lo+hi)/2):
                break
            mid = (lo+hi)/2
            if fn(mid) > 0:
                lo = mid
            else:
                hi = mid
        else:
            raise ValueError('NUMERICALLY_UNRESOLVED_ITERATION_LIMIT')
        record.update(status='CONVERGED', bracket_lambda=[lo, hi], root_lambda=(lo+hi)/2)
    except (ValueError, FloatingPointError) as exc:
        record.update(status=str(exc), bracket_lambda=[lo, hi])
    return record


def rate_fit(pair, p):
    q1, q2 = pair.first.q, pair.second.q
    if q1 == q2 == 0:
        return {'status': 'ZERO_DELIVERY_RATE_UNIDENTIFIED', 'A': 0., 'k': None,
                'lambda': None, 'A_bounds': [0., 0.], 'lambda_bounds': None,
                'k_bounds': [0., K_MAX], 'attempts': [], 'denominator_relative_allowance': 0.}
    if q1 == 0 or q2 > q1 or q2 == 0:
        raise FitFailure('SCIENTIFICALLY_INCOMPATIBLE_FINITE_DECREASING_PAIR')
    if q1 == q2:
        return {'status': 'CONSTANT_RATE_BOUNDARY', 'A': q1, 'k': 0., 'lambda': 0.,
                'A_bounds': [q1, q1], 'lambda_bounds': [0., 0.], 'k_bounds': [0., 0.],
                'attempts': [], 'denominator_relative_allowance': 0.}
    attempts = [solve(pair, p, 128, 1e-12)]
    if attempts[0]['status'] != 'CONVERGED':
        # Distinguish a proved ceiling miss from uncertainty at that boundary.
        if attempts[0]['status'].startswith('NO_FINITE_BRACKET'):
            try:
                bounds, _ = ratio_bounds(pair, (K_MAX*B_REF)**p, p)
                status = ('SCIENTIFICALLY_NO_FINITE_BRACKET_WITHIN_RATE_CEILING'
                          if bounds[0] > q2/q1 else 'NUMERICALLY_UNRESOLVED_RATE_CEILING')
            except ValueError:
                status = 'NUMERICALLY_UNRESOLVED_RATE_CEILING'
        else:
            status = attempts[0]['status']
        raise FitFailure(status, attempts)
    attempts.append(solve(pair, p, 'reference', 1e-14))
    if attempts[1]['status'] != 'CONVERGED':
        raise FitFailure('NUMERICALLY_UNRESOLVED_REFINEMENT', attempts)
    lam, refined = (r['root_lambda'] for r in attempts)
    try:
        bounds, relative = ratio_bounds(pair, refined, p)
        a, b = pair.first, pair.second
        f1 = shape_average(a.start_kg, a.end_kg, refined, p)
        f2 = shape_average(b.start_kg, b.end_kg, refined, p)
        slope = (shape_derivative(b.start_kg, b.end_kg, refined, p)*f1
                 - f2*shape_derivative(a.start_kg, a.end_kg, refined, p))/f1**2
        if slope >= 0 or not math.isfinite(slope):
            raise ValueError('NUMERICALLY_UNRESOLVED_SINGULAR_RATIO')
        radius = (abs(lam-refined)+sum(r['bracket_lambda'][1]-r['bracket_lambda'][0] for r in attempts)
                  +8*(bounds[1]-bounds[0]+legacy.roundoff(q2/q1))/abs(slope)
                  +legacy.roundoff(refined))
        lo, hi = max(0., refined-radius), min((K_MAX*B_REF)**p, refined+radius)
        low_bounds, rel_lo = ratio_bounds(pair, lo, p)
        high_bounds, rel_hi = ratio_bounds(pair, hi, p)
        if low_bounds[0] < q2/q1 or high_bounds[1] > q2/q1:
            raise ValueError('NUMERICALLY_UNRESOLVED_ROOT_ENCLOSURE')
        f, fe = qualified_average(a.start_kg, a.end_kg, lam, p)
        flo, elo = qualified_average(a.start_kg, a.end_kg, lo, p)
        fhi, ehi = qualified_average(a.start_kg, a.end_kg, hi, p)
        amp = q1/f
        alo = q1/(flo+elo)-legacy.roundoff(amp)
        ahi = q1/(fhi-ehi)+legacy.roundoff(amp)
        if amp > 1:
            raise ValueError('SCIENTIFICALLY_INCOMPATIBLE_A_EXCEEDS_ONE')
        if ahi > 1 or alo < 0:
            raise ValueError('NUMERICALLY_UNRESOLVED_AMPLITUDE_BOUND')
        return {'status': 'QUALIFIED', 'A': amp, 'k': lam**(1/p)/B_REF, 'lambda': lam,
                'A_bounds': [alo, ahi], 'lambda_bounds': [lo, hi],
                'k_bounds': [lo**(1/p)/B_REF, hi**(1/p)/B_REF], 'attempts': attempts,
                'ratio_slope_per_lambda': slope,
                'denominator_relative_allowance': max(relative, rel_lo, rel_hi, fe/f)}
    except (ValueError, FloatingPointError) as exc:
        raise FitFailure(str(exc), attempts) from exc


def legacy_state(base, pair):
    data = asdict(pair.first)
    data['input_class'] = ('SYNTHETIC_ANCHOR_INPUT' if pair.first.input_class.startswith('SYNTHETIC')
                           else 'MEASURED_SOURCE_ANCHOR_INPUT')
    return legacy.anchor(base, legacy.AnchorInput(**data))


def amplitude_fit(base, pair, arm, first_state=None):
    if arm == 'FIRST_ASSAY_EMPIRICAL':
        state = first_state
        return {'status': 'QUALIFIED', 'alpha': state.alpha,
                'alpha_bounds': [state.alpha-state.alpha_allowance, state.alpha+state.alpha_allowance],
                'denominator_relative_allowance': state.anchor_integral_allowance_kg/state.anchor_integral_kg,
                'attempts': [], 'legacy_state': state.to_dict()}
    obs = (pair.first, pair.second)
    vals = [legacy.integral(base.curve(), o.start_kg, o.end_kg) for o in obs]
    g = [v/o.width for (v, _), o in zip(vals, obs)]
    e = [error/o.width for (_, error), o in zip(vals, obs)]
    if any(x-y <= 0 or y/x > 1e-6 for x, y in zip(g, e)):
        raise FitFailure('NUMERICALLY_UNRESOLVED_CONDITIONING_DENOMINATOR')
    indices = (1,) if arm == 'SECOND_ASSAY_EMPIRICAL' else (0, 1)
    n = sum(obs[j].width*g[j]*obs[j].q for j in indices)
    d = sum(obs[j].width*g[j]**2 for j in indices)
    alpha = n/d
    nlo = sum(obs[j].width*(g[j]-e[j])*obs[j].q for j in indices)
    nhi = sum(obs[j].width*(g[j]+e[j])*obs[j].q for j in indices)
    dlo = sum(obs[j].width*(g[j]-e[j])**2 for j in indices)
    dhi = sum(obs[j].width*(g[j]+e[j])**2 for j in indices)
    alo, ahi = (nlo/dhi-legacy.roundoff(alpha), nhi/dlo+legacy.roundoff(alpha)) if n else (0., 0.)
    if arm == 'SECOND_ASSAY_EMPIRICAL':
        alpha = obs[1].q/g[1]
        alo, ahi = ((obs[1].q/(g[1]+e[1])-legacy.roundoff(alpha),
                     obs[1].q/(g[1]-e[1])+legacy.roundoff(alpha)) if n else (0., 0.))
    maximum = legacy.maximum_concentration(base.curve(), pair.first.start_kg)
    if alpha*maximum > 1:
        raise FitFailure('SCIENTIFICALLY_INCOMPATIBLE_CONCENTRATION_EXCEEDS_ONE')
    if ahi*maximum > 1:
        raise FitFailure('NUMERICALLY_UNRESOLVED_CONCENTRATION_BOUND')
    rel = max(max(y/x for x, y in zip(g, e)), (dhi-dlo)/d)
    if rel > 1e-6:
        raise FitFailure('NUMERICALLY_UNRESOLVED_AMPLITUDE_DENOMINATOR')
    return {'status': 'QUALIFIED', 'alpha': alpha, 'alpha_bounds': [alo, ahi],
            'g': g, 'g_allowances': e, 'denominator': d,
            'denominator_relative_allowance': rel, 'attempts': []}


@dataclass(frozen=True)
class Prediction:
    start_kg: float
    end_kg: float
    solute_kg: float
    tds_percent: float | None
    numerical_allowance_kg: float
    tds_sensitivity_pp_per_pp: tuple | None
    sensitivity_status: str


@dataclass(frozen=True)
class FittedState:
    base: FrozenBase
    observations: ObservationPair
    arm: str = 'TWO_ASSAY_MASS'
    _diagnostics_json: str = field(init=False, repr=False)
    _first_state: object = field(init=False, repr=False, default=None)

    def __post_init__(self):
        if type(self.base) is not FrozenBase or type(self.observations) is not ObservationPair:
            raise ValueError('TYPED_BASE_AND_PAIR_REQUIRED')
        if self.arm not in ARMS:
            raise ValueError('UNDECLARED_ARM')
        curve = self.base.curve()
        family = 'MASS' if self.arm in ARMS[:3] else 'BOUNDARY_AWARE_EMPIRICAL'
        if curve.family != family:
            raise ValueError('ARM_BASE_FAMILY_MISMATCH')
        if (self.observations.first.start_kg < curve.domain_kg[0]
                or self.observations.second.end_kg > curve.domain_kg[1]):
            raise ValueError('UNSUPPORTED_CONDITIONING_INTERVAL')
        if self.arm in ARMS[:2]:
            p = 1. if self.arm == ARMS[1] else curve.coefficients[2]
            diagnostics = rate_fit(self.observations, p)
            diagnostics['p'] = p
            diagnostics.update(self._jacobian(diagnostics))
        else:
            first_state = legacy_state(self.base, self.observations) if self.arm == ARMS[5] else None
            object.__setattr__(self, '_first_state', first_state)
            diagnostics = amplitude_fit(self.base, self.observations, self.arm, first_state)
            diagnostics['jacobian_status'] = 'FIXED_SHAPE_ONE_PARAMETER'
        object.__setattr__(self, '_diagnostics_json', canonical(diagnostics))

    def _jacobian(self, d):
        if d['lambda'] is None:
            return {'jacobian_status': 'SINGULAR_ZERO_DELIVERY_RATE_UNIDENTIFIED',
                    'jacobian_q_by_A_lambda': None, 'jacobian_q_by_A_k': None,
                    'jacobian_condition_number': None}
        amp, lam, p = d['A'], d['lambda'], d['p']
        j = np.array([[shape_average(o.start_kg, o.end_kg, lam, p),
                       amp*shape_derivative(o.start_kg, o.end_kg, lam, p)]
                      for o in (self.observations.first, self.observations.second)])
        jk = None
        if d['k'] > 0 or p == 1:
            jk = j.copy()
            jk[:, 1] *= p*B_REF*(d['k']*B_REF)**(p-1)
        return {'jacobian_status': 'REGULAR' if jk is not None else 'NONREGULAR_K_ZERO_BOUNDARY',
                'jacobian_q_by_A_lambda': j.tolist(),
                'jacobian_q_by_A_k': jk.tolist() if jk is not None else None,
                'jacobian_condition_number': float(np.linalg.cond(j)),
                'jacobian_units': 'q kg/kg; A kg/kg; lambda dimensionless; k kg^-1'}

    @property
    def diagnostics(self):
        return strict_json(self._diagnostics_json)

    @property
    def future_domain_kg(self):
        return (self.observations.second.end_kg, self.base.curve().domain_kg[1])

    @property
    def claims(self):
        labels = REAL_LABELS if self.observations.first.input_class.startswith('MEASURED') else ('SYNTHETIC_TWO_ASSAY_INPUT',)
        return CLAIMS + labels

    def predict_intervals(self, queries):
        result = []
        d = self.diagnostics
        for q in queries:
            if type(q) is not IntervalQuery:
                raise ValueError('COORDINATE_ONLY_TYPED_QUERY_REQUIRED')
            if q.start_kg < self.future_domain_kg[0]:
                raise ValueError('QUERY_BEFORE_SECOND_ASSAY_COMPLETION')
            if q.end_kg > self.future_domain_kg[1]:
                raise ValueError('OUTSIDE_FROZEN_MASS_DOMAIN')
            width = q.end_kg-q.start_kg
            if not width:
                result.append(Prediction(q.start_kg, q.end_kg, 0., None, 0., None, 'ZERO_WIDTH_UNDEFINED_TDS'))
                continue
            if self.arm in ARMS[:2]:
                if d['lambda'] is None:
                    value, allowance, sensitivity = 0., 0., None
                    status = 'SINGULAR_ZERO_DELIVERY_RATE_UNIDENTIFIED'
                else:
                    avg, error = qualified_average(q.start_kg, q.end_kg, d['lambda'], d['p'])
                    value = d['A']*avg*width
                    alow, ahigh = d['A_bounds']
                    lo, hi = d['lambda_bounds']
                    flo, elo = qualified_average(q.start_kg, q.end_kg, hi, d['p'])
                    fhi, ehi = qualified_average(q.start_kg, q.end_kg, lo, d['p'])
                    lower, upper = alow*(flo-elo)*width, ahigh*(fhi+ehi)*width
                    allowance = max(abs(value-lower), abs(upper-value), d['A']*error*width)+legacy.roundoff(value)
                    gradient = np.array([avg, d['A']*shape_derivative(q.start_kg, q.end_kg, d['lambda'], d['p'])])
                    sensitivity = tuple(float(x) for x in np.linalg.solve(np.array(d['jacobian_q_by_A_lambda']).T, gradient))
                    status = 'IMPLICIT_LOCAL_PP_PER_PP' if d['lambda'] else 'ONE_SIDED_FEASIBLE_CONSTANT_BOUNDARY'
            elif self.arm == 'FIRST_ASSAY_EMPIRICAL':
                pred = self._first_state.predict_intervals((q,))[0]
                value, allowance = pred.solute_kg, pred.numerical_allowance_kg
                sensitivity = (pred.anchor_error_amplification, 0.)
                status = 'EXACT_LEGACY_FIRST_ASSAY'
            else:
                integral, error = legacy.integral(self.base.curve(), q.start_kg, q.end_kg)
                value = d['alpha']*integral
                lo, hi = d['alpha_bounds']
                allowance = max(abs(value-lo*(integral-error)), abs(hi*(integral+error)-value))+legacy.roundoff(value)
                obs = (self.observations.first, self.observations.second)
                sensitivity = tuple((integral/width)*o.width*d['g'][j]/d['denominator']
                    if self.arm != 'SECOND_ASSAY_EMPIRICAL' or j == 1 else 0. for j, o in enumerate(obs))
                status = 'ANALYTICAL_FIXED_SHAPE_PP_PER_PP'
            if not math.isfinite(value+allowance) or value < 0 or value > width:
                raise ValueError('NONPHYSICAL_OR_NONFINITE_PREDICTION')
            if allowance > 1e-9:
                raise ValueError('NUMERICALLY_UNRESOLVED_PROPAGATED_PREDICTION')
            result.append(Prediction(q.start_kg, q.end_kg, value, 100*value/width,
                                     allowance, sensitivity, status))
        return tuple(result)

    def remaining_solute(self, stop_kg):
        return self.predict_intervals((IntervalQuery(self.future_domain_kg[0], stop_kg),))[0]

    def to_dict(self):
        return {'version': VERSION, 'units': UNITS, 'base': asdict(self.base),
                'observations': asdict(self.observations), 'arm': self.arm,
                'diagnostics': self.diagnostics, 'future_domain_kg': list(self.future_domain_kg),
                'claims': list(self.claims), 'producer_modules': runtime_identity()}

    @classmethod
    def from_dict(cls, data):
        try:
            if data['producer_modules'] != runtime_identity():
                raise ValueError('PRODUCER_IDENTITY_MISMATCH')
            state = cls(FrozenBase(data['base']['artifact_json']),
                        ObservationPair.from_dict(data['observations']), data['arm'])
            if canonical(state.to_dict()) != canonical(data):
                raise ValueError('STATE_SCHEMA_OR_DERIVED_FIELDS_MISMATCH')
            return state
        except (KeyError, TypeError) as exc:
            raise ValueError('MALFORMED_TWO_ASSAY_STATE') from exc

    @classmethod
    def load(cls, path):
        return cls.from_dict(strict_json(Path(path).read_text()))

    def save(self, path):
        with Path(path).open('x') as stream:
            stream.write(canonical(self.to_dict())+'\n')


def synthetic_pair(p=.8327267294693588, A=.2, k=60.):
    observations = []
    for fraction, (start, end) in enumerate(((0., .003), (.003, .008)), 1):
        tds = 100*A*shape_average(start, end, (k*B_REF)**p, p, 'reference')
        observations.append(Observation('synthetic-shot', 'synthetic-source', fraction,
            start, end, tds, 'SYNTHETIC_KG', 'first-party synthetic fixture', 'SYNTHETIC_TWO_ASSAY_INPUT'))
    return ObservationPair(*observations)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stop-kg', type=float, default=.04)
    args = parser.parse_args()
    base = FrozenBase.from_model(kernel.Model('synthetic-base', 'MASS', (.2, 60., .8327267294693588),
        (0., .06), {'kind': 'SYNTHETIC_NO_SOURCE_DATA'}, 'first-party synthetic fixture'))
    state = FittedState(base, synthetic_pair())
    print(json.dumps({'input_class': 'SYNTHETIC_TWO_ASSAY_INPUT', 'state': state.to_dict(),
        'remaining': asdict(state.remaining_solute(args.stop_kg))}, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()

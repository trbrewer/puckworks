"""Research-only SI beverage-mass delivery. No inventory or hydraulic model.

First-party code; a loaded artifact declares its own source/rights restrictions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad

VERSION = 'mass-delivery/1'
UNITS = {'beverage': 'kg', 'solute': 'kg', 'concentration': 'kg/kg',
         'mass_rate': 'kg^-1', 'time': 's', 'time_rate': 's^-1', 'basis': 'MASS'}
LIMITATIONS = ('RESEARCH_ONLY', 'CONDITIONAL_ON_BEVERAGE_MASS',
               'NO_TIME_FLOW_PRESSURE_PREDICTION', 'NOT_INVENTORY_CLOSURE',
               'PHYSICAL_VALIDATION_NOT_ESTABLISHED')


def mass_to_kg(value, unit):
    factors = {'kg': 1., 'g': .001, 'mg': .000001}
    if unit not in factors:
        raise ValueError('unsupported mass unit')
    a = np.asarray(value, float)
    if not np.isfinite(a).all() or np.any(a < 0):
        raise ValueError('invalid mass')
    return a * factors[unit]


def concentration_to_fraction(value, unit, basis='MASS'):
    if unit not in ('percent', 'kg/kg') or basis != 'MASS':
        raise ValueError('unsupported concentration unit/basis')
    a = np.asarray(value, float) / (100 if unit == 'percent' else 1)
    if not np.isfinite(a).all() or np.any((a < 0) | (a > 1)):
        raise ValueError('invalid concentration')
    return a


def intervals(starts, ends):
    a, b = np.broadcast_arrays(np.asarray(starts, float), np.asarray(ends, float))
    if not np.isfinite(a).all() or not np.isfinite(b).all() or np.any(a < 0) or np.any(b < a):
        raise ValueError('negative, reversed or nonfinite interval')
    return a, b


@lru_cache(None)
def quadrature(order=128):
    if order not in (128, 256):
        raise ValueError('unsupported quadrature order')
    v, w = np.polynomial.legendre.leggauss(order)
    v = (v + 1) / 2
    return v**8, w / 2 * 8 * v**7


def compact_delivery(starts, ends, theta, *, time_bounds=None, timing='linear', order=128):
    """Integrated solute kg; TIME integrates q(t(u)) * measured mass, never dt."""
    a, b = intervals(starts, ends)
    c0, rate, p = theta
    rate_max = 10000 if time_bounds is None else 10
    if not np.isfinite(theta).all() or not (0 <= c0 <= 1 and 0 <= rate <= rate_max
                                          and .25 <= p <= 4):
        raise ValueError('invalid computational parameters')
    if timing not in ('linear', 'u2', 'sqrt'):
        raise ValueError('unsupported timing assumption')
    u, w = quadrature(order)
    if time_bounds is None:
        x = a[..., None] + (b-a)[..., None] * u
    else:
        t0, t1 = intervals(*time_bounds)
        if t0.shape != a.shape:
            raise ValueError('time/mass shape mismatch')
        f = {'linear': u, 'u2': u*u, 'sqrt': np.sqrt(u)}[timing]
        x = t0[..., None] + (t1-t0)[..., None] * f
    y = (b-a) * np.sum(w * c0 * np.exp(-(rate*x)**p), axis=-1)
    if np.any(y < 0) or np.any(y > b-a+1e-15) or not np.isfinite(y).all():
        raise FloatingPointError('nonphysical delivery bound')
    return y


def linear_basis_integral(starts, ends, knots):
    """Exact integrals of piecewise-linear hat bases; no midpoint observations."""
    a, b = intervals(starts, ends)
    knots = np.asarray(knots, float)
    if knots.ndim != 1 or len(knots) < 2 or not np.isfinite(knots).all() or np.any(np.diff(knots) <= 0):
        raise ValueError('invalid knots')
    if np.any(a < knots[0]) or np.any(b > knots[-1]):
        raise ValueError('out-of-domain basis query')
    out = np.zeros(a.shape + (len(knots),))
    for j, (lo, hi) in enumerate(zip(knots[:-1], knots[1:])):
        left, right = np.maximum(a, lo), np.minimum(b, hi)
        width = np.maximum(right-left, 0)
        right_hat = width * ((left+right)/2-lo)/(hi-lo)
        out[..., j] += width-right_hat
        out[..., j+1] += right_hat
    return out


@dataclass(frozen=True)
class Delivery:
    solute_kg: np.ndarray
    average_q: np.ndarray
    in_domain: np.ndarray
    positive_width: np.ndarray

    @property
    def tds_percent(self):
        return 100 * self.average_q


@dataclass(frozen=True)
class Model:
    model_id: str
    family: str
    coefficients: tuple[float, ...]
    domain_kg: tuple[float, float]
    fit_identity: dict
    rights: str
    claims: tuple[str, ...] = LIMITATIONS
    version: str = VERSION
    units: dict | None = None
    knots_kg: tuple[float, ...] = ()
    time_domain_s: tuple[float, float] | None = None
    timing: str = 'linear'

    def __post_init__(self):
        object.__setattr__(self, 'units', dict(UNITS) if self.units is None else self.units)
        if self.version != VERSION or self.units != UNITS:
            raise ValueError('unsupported schema/version/units/basis')
        if self.family not in ('MASS', 'TIME', 'BOUNDARY_AWARE_EMPIRICAL'):
            raise ValueError('unsupported model family')
        if not self.model_id or not self.fit_identity or not self.rights:
            raise ValueError('missing model/fit/rights identity')
        if not set(LIMITATIONS) <= set(self.claims):
            raise ValueError('required claim limitations missing')
        lo, hi = self.domain_kg
        intervals(lo, hi)
        if lo != 0 or hi <= 0:
            raise ValueError('domain must begin at collection origin')
        if self.timing not in ('linear', 'u2', 'sqrt'):
            raise ValueError('unsupported timing assumption')
        if self.family == 'BOUNDARY_AWARE_EMPIRICAL':
            if not self.knots_kg or self.knots_kg[0] != lo or self.knots_kg[-1] != hi:
                raise ValueError('knots must cover exactly the declared mass domain')
            if len(self.coefficients) != len(self.knots_kg):
                raise ValueError('knot/coefficient mismatch')
            linear_basis_integral(lo, hi, self.knots_kg)
            q = np.asarray(self.coefficients)
            if not np.isfinite(q).all() or np.any((q < 0) | (q > 1)):
                raise ValueError('invalid profile concentration')
        else:
            if len(self.coefficients) != 3:
                raise ValueError('three compact coefficients required')
            if self.family == 'TIME':
                if self.time_domain_s is None:
                    raise ValueError('TIME domain required')
                t0, t1 = self.time_domain_s
                intervals(t0, t1)
                if t0 != 0 or t1 <= 0:
                    raise ValueError('invalid time domain')
                compact_delivery(0, 0, self.coefficients, time_bounds=(0, 0))
            else:
                compact_delivery(0, 0, self.coefficients)

    def predict(self, starts, ends, *, time_bounds=None, strict=True, order=128):
        a, b = intervals(starts, ends)
        mask = (a >= self.domain_kg[0]) & (b <= self.domain_kg[1])
        tb = None
        if self.family == 'TIME':
            if time_bounds is None:
                raise ValueError('source-qualified time bounds required')
            t0, t1 = intervals(*time_bounds)
            if t0.shape != a.shape:
                raise ValueError('time/mass shape mismatch')
            mask &= (t0 >= self.time_domain_s[0]) & (t1 <= self.time_domain_s[1])
            tb = (t0[mask], t1[mask])
        elif time_bounds is not None:
            raise ValueError('time bounds apply only to TIME')
        if strict and not np.all(mask):
            raise ValueError('out-of-domain query; extrapolation prohibited')
        out = np.full(a.shape, np.nan)
        if self.family == 'BOUNDARY_AWARE_EMPIRICAL':
            out[mask] = linear_basis_integral(a[mask], b[mask], self.knots_kg) @ self.coefficients
        else:
            out[mask] = compact_delivery(a[mask], b[mask], self.coefficients,
                                        time_bounds=tb, timing=self.timing, order=order)
        avg = np.full(a.shape, np.nan)
        np.divide(out, b-a, out=avg, where=mask & (b > a))
        return Delivery(out, avg, mask, b > a)

    def cumulative_solute(self, stop_kg):
        """Modeled complete range, conditional on achieving stop mass (no future data)."""
        if self.family == 'TIME':
            raise ValueError('TIME cannot answer a mass-only stopping query')
        return self.predict(0, stop_kg).solute_kg

    def average_tds(self, start_kg, end_kg):
        return self.predict(start_kg, end_kg).tds_percent

    def to_dict(self):
        return asdict(self)

    def save(self, path):
        with Path(path).open('x') as f:
            json.dump(self.to_dict(), f, sort_keys=True, indent=2, allow_nan=False)
            f.write('\n')

    @classmethod
    def from_dict(cls, data):
        if set(data) != set(cls.__dataclass_fields__):
            raise ValueError('invalid model schema')
        d = dict(data)
        for key in ('coefficients', 'domain_kg', 'claims', 'knots_kg'):
            d[key] = tuple(d[key])
        if d['time_domain_s'] is not None:
            d['time_domain_s'] = tuple(d['time_domain_s'])
        return cls(**d)

    @classmethod
    def load(cls, path):
        return cls.from_dict(json.loads(Path(path).read_text()))


def integration_allowance(model, start, end, time_bounds=None):
    """Independent adaptive integration and refinement; kg numerical allowance."""
    primary = float(model.predict(start, end, time_bounds=time_bounds).solute_kg)
    refined = float(model.predict(start, end, time_bounds=time_bounds, order=256).solute_kg)
    if end == start:
        return 0.
    points = None
    if model.family == 'BOUNDARY_AWARE_EMPIRICAL':
        def fn(u):
            return (end-start)*np.interp(start+(end-start)*u, model.knots_kg, model.coefficients)
        points = [(k-start)/(end-start) for k in model.knots_kg if start < k < end]
    else:
        c0, k, p = model.coefficients
        def fn(u):
            x = start+(end-start)*u
            if model.family == 'TIME':
                f = {'linear': u, 'u2': u*u, 'sqrt': np.sqrt(u)}[model.timing]
                x = time_bounds[0]+(time_bounds[1]-time_bounds[0])*f
            return (end-start)*c0*np.exp(-(k*x)**p)
    reference, error = quad(fn, 0, 1, points=points, epsabs=1e-13, epsrel=1e-11, limit=200)
    return max(abs(primary-refined), abs(primary-reference)+error, 1e-17)


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path)
    parser.add_argument('--stop-kg', type=float, default=.04)
    args = parser.parse_args()
    model = Model.load(args.model) if args.model else Model(
        'synthetic-example-v1', 'MASS', (.15, 40., .8), (0., .06),
        {'kind': 'SYNTHETIC_NO_SOURCE_DATA'}, 'first-party synthetic fixture')
    result = model.predict([0., .01], [.01, .02])
    print(json.dumps({'model_id': model.model_id, 'claims': model.claims,
                      'interval_solute_kg': result.solute_kg.tolist(),
                      'interval_tds_percent': result.tds_percent.tolist(),
                      'conditional_stop_kg': args.stop_kg,
                      'modeled_cumulative_solute_kg': float(model.cumulative_solute(args.stop_kg))},
                     indent=2, allow_nan=False))


if __name__ == '__main__':
    main()

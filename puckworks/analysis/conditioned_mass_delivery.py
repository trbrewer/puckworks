"""Research-only nominal-recipe conditioned solute delivery; all masses in kg.

First-party software. Loaded source-derived artifacts retain their own rights.
This module uses relative imports so an explicit consumer can isolate BOTH files.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path

import numpy as np
from scipy.special import expit

from . import mass_delivery as kernel

VERSION = 'conditioned-mass-delivery/1'
FAMILIES = ('M0', 'MT', 'MF', 'MTF', 'SETTING_AWARE_EMPIRICAL')
SITES = ('center', 'temperature_negative', 'temperature_positive',
         'flow_negative', 'flow_positive')
BOUNDS = {'c_ref': [0., 1.], 'k_ref': [0., 10000.], 'p': [.25, 4.],
          'aT': [-3., 3.], 'aF': [-3., 3.], 'dT': [-3., 3.], 'dF': [-3., 3.],
          'empirical_q': [0., 1.]}
FEATURES = {'xT': '(T_set_K - 362.15) / 9.0',
            'xF': 'source_flow_setting_code - 2.0'}
HULL = {'rule': 'abs(xT) + abs(xF) <= 1', 'constant_settings_only': True,
        'product_with_mass_domain': 'MODELING_ASSUMPTION_NOT_COMPLETE_JOINT_COVERAGE'}
SEMANTICS = 'DIMENSIONLESS_SOURCE_SPECIFIC_NOMINAL_DESIGN_CODE_NOT_MEASURED_FLOW'
UNITS = {'beverage': 'kg', 'solute': 'kg', 'concentration': 'kg/kg',
         'average_TDS': 'percent', 'mass_rate': 'kg^-1', 'temperature': 'K',
         'source_flow_setting_code': 'source_design_code', 'basis': 'MASS'}
CLAIMS = kernel.LIMITATIONS + ('NOMINAL_SETTINGS_NOT_LOCAL_PUCK_STATE',
         'NO_CAUSAL_OR_MECHANISM_IDENTIFICATION', 'CONSTANT_SETTINGS_ONLY')


def temperature_to_kelvin(value, unit):
    if unit not in ('K', 'degC'):
        raise ValueError('temperature unit must be K or degC')
    a = np.asarray(value, float) + (273.15 if unit == 'degC' else 0.)
    if not np.isfinite(a).all() or np.any(a <= 0):
        raise ValueError('invalid nominal temperature')
    return a


def odds_shift(z, h):
    """Stable bounded odds shift with exact endpoints and exact identity shift."""
    z, h = np.broadcast_arrays(np.asarray(z, float), np.asarray(h, float))
    if not np.isfinite(z).all() or not np.isfinite(h).all() or np.any((z < 0) | (z > 1)):
        raise ValueError('invalid bounded odds shift')
    out = z.copy()
    mask = (z > 0) & (z < 1) & (h != 0)
    out[mask] = expit(np.log(z[mask])-np.log1p(-z[mask])+h[mask])
    return out


def features(temperature_K, source_flow_setting_code, *, temperature_unit='K',
             flow_unit='source_design_code'):
    if temperature_unit != 'K' or flow_unit != 'source_design_code':
        raise ValueError('SI kelvin and explicit source_design_code required')
    t, f = np.broadcast_arrays(temperature_to_kelvin(temperature_K, 'K'),
                              np.asarray(source_flow_setting_code, float))
    if not np.isfinite(f).all():
        raise ValueError('nonfinite source flow-setting code')
    return (t-362.15)/9., f-2.


def setting_weights(xT, xF):
    t, f = np.broadcast_arrays(np.asarray(xT, float), np.asarray(xF, float))
    if not np.isfinite(t).all() or not np.isfinite(f).all() or np.any(abs(t)+abs(f) > 1):
        raise ValueError('outside nominal-setting design diamond')
    return np.stack((1-abs(t)-abs(f), np.maximum(-t, 0), np.maximum(t, 0),
                     np.maximum(-f, 0), np.maximum(f, 0)), axis=-1)


def recipe_coefficients(theta, xT, xF):
    c, k, p, aT, aF, dT, dF = theta
    amplitude_shift, rate_shift = aT*xT+aF*xF, dT*xT+dF*xF
    # Exact zero-shift rate preserves the inherited MASS kernel's floating value.
    return (float(odds_shift(c, amplitude_shift)),
            k if rate_shift == 0 else 10000*float(odds_shift(k/10000, rate_shift)), p)


@dataclass(frozen=True)
class Delivery(kernel.Delivery):
    unsupported_reason: np.ndarray


@dataclass(frozen=True)
class Model:
    model_id: str
    family: str
    coefficients: tuple
    domain_kg: tuple[float, float]
    fit_identity: dict
    rights: str
    claims: tuple[str, ...] = CLAIMS
    version: str = VERSION
    units: dict = field(default_factory=lambda: dict(UNITS))
    parameter_bounds: dict = field(default_factory=lambda: {k: list(v) for k, v in BOUNDS.items()})
    feature_definitions: dict = field(default_factory=lambda: dict(FEATURES))
    setting_hull: dict = field(default_factory=lambda: dict(HULL))
    source_code_semantics: str = SEMANTICS
    knots_kg: tuple = ()
    sites: tuple = SITES

    def __post_init__(self):
        if (self.version != VERSION or self.units != UNITS or self.parameter_bounds != BOUNDS
                or self.feature_definitions != FEATURES or self.setting_hull != HULL
                or self.source_code_semantics != SEMANTICS or self.sites != SITES):
            raise ValueError('unsupported schema, units, bounds, features, hull or source semantics')
        if self.family not in FAMILIES or not isinstance(self.model_id, str) or not self.model_id:
            raise ValueError('explicit known model family/identity required')
        if (not isinstance(self.fit_identity, dict) or not self.fit_identity
                or not isinstance(self.rights, str) or not self.rights
                or not set(CLAIMS) <= set(self.claims)):
            raise ValueError('fit/source identity, rights and claim limits required')
        lo, hi = self.domain_kg
        kernel.intervals(lo, hi)
        if lo != 0 or hi <= 0:
            raise ValueError('mass domain must start at collection origin')
        q = np.asarray(self.coefficients, float)
        if not np.isfinite(q).all():
            raise ValueError('nonfinite coefficients')
        if self.family == 'SETTING_AWARE_EMPIRICAL':
            if q.shape != (5, len(self.knots_kg)) or len(self.knots_kg) not in (5, 9):
                raise ValueError('five site profiles with five or nine knots required')
            if self.knots_kg[0] != lo or self.knots_kg[-1] != hi:
                raise ValueError('knots must cover declared domain')
            expected = np.linspace(lo, hi, len(self.knots_kg))
            if not np.allclose(self.knots_kg, expected, rtol=0, atol=1e-16):
                raise ValueError('equally spaced knots required')
            kernel.linear_basis_integral(lo, hi, self.knots_kg)
            if np.any((q < 0) | (q > 1)):
                raise ValueError('profile outside concentration bounds')
        else:
            if q.shape != (7,) or self.knots_kg:
                raise ValueError('seven compact coefficients and no knots required')
            lower = [0, 0, .25, -3, -3, -3, -3]
            upper = [1, 10000, 4, 3, 3, 3, 3]
            if np.any(q < lower) or np.any(q > upper):
                raise ValueError('compact parameter outside frozen bounds')
            fixed = {'M0': [3, 4, 5, 6], 'MT': [4, 6], 'MF': [3, 5], 'MTF': []}[self.family]
            if np.any(q[fixed] != 0):
                raise ValueError('inactive setting slopes must be exactly zero')

    def predict(self, starts, ends, *, temperature_K, source_flow_setting_code,
                setting_kind='CONSTANT', temperature_unit='K',
                flow_unit='source_design_code', mass_unit='kg', strict=True, order=128):
        if mass_unit != 'kg':
            raise ValueError('mass contract requires kg')
        a, b = kernel.intervals(starts, ends)
        t, f = features(temperature_K, source_flow_setting_code,
                        temperature_unit=temperature_unit, flow_unit=flow_unit)
        a, b, t, f = np.broadcast_arrays(a, b, t, f)
        reason = np.full(a.shape, '', dtype=object)
        reason[(a < self.domain_kg[0]) | (b > self.domain_kg[1])] = 'OUTSIDE_FIT_MASS_DOMAIN'
        reason[abs(t)+abs(f) > 1] = 'OUTSIDE_SETTING_DESIGN_HULL'
        if setting_kind != 'CONSTANT':
            reason[...] = 'NOT_ADJUDICATED_VARIABLE_SETTING_INPUT'
        mask = reason == ''
        if strict and not np.all(mask):
            raise ValueError(';'.join(sorted(set(reason[~mask].flat))))
        out = np.full(a.shape, np.nan)
        # Group equal recipes to call the unchanged vectorized interval kernel.
        for ti, fi in sorted(set(zip(t[mask].flat, f[mask].flat))):
            use = mask & (t == ti) & (f == fi)
            if self.family == 'SETTING_AWARE_EMPIRICAL':
                profile = setting_weights(ti, fi) @ np.asarray(self.coefficients)
                out[use] = kernel.linear_basis_integral(a[use], b[use], self.knots_kg) @ profile
            else:
                theta = recipe_coefficients(self.coefficients, ti, fi)
                out[use] = kernel.compact_delivery(a[use], b[use], theta, order=order)
        avg = np.full(a.shape, np.nan)
        np.divide(out, b-a, out=avg, where=mask & (b > a))
        return Delivery(out, avg, mask, b > a, reason)

    def cumulative_solute(self, stop_kg, **recipe):
        """Conditional on achieving stop mass; no time, flow or inventory query."""
        return self.predict(0., stop_kg, **recipe).solute_kg

    def average_tds(self, start_kg, end_kg, **recipe):
        return self.predict(start_kg, end_kg, **recipe).tds_percent

    def to_dict(self):
        return asdict(self)

    def save(self, path):
        with Path(path).open('x') as stream:
            json.dump(self.to_dict(), stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')

    @classmethod
    def from_dict(cls, data):
        if not isinstance(data, dict) or set(data) != set(cls.__dataclass_fields__):
            raise ValueError('invalid model schema fields')
        d = dict(data)
        try:
            for key in ('coefficients', 'domain_kg', 'claims', 'knots_kg', 'sites'):
                d[key] = tuple(d[key])
            if d['family'] == 'SETTING_AWARE_EMPIRICAL':
                d['coefficients'] = tuple(tuple(v) for v in d['coefficients'])
            return cls(**d)
        except (TypeError, IndexError, KeyError) as error:
            raise ValueError('malformed model artifact') from error

    @classmethod
    def load(cls, path):
        def unique(pairs):
            out = {}
            for key, value in pairs:
                if key in out:
                    raise ValueError('duplicate JSON key')
                out[key] = value
            return out
        return cls.from_dict(json.loads(Path(path).read_text(), object_pairs_hook=unique))


def integration_allowance(model, start, end, *, temperature_K, source_flow_setting_code):
    """Reuse independent quadrature/refinement for this exact recipe-specific curve."""
    model.predict(start, end, temperature_K=temperature_K,
                  source_flow_setting_code=source_flow_setting_code)
    t, f = features(temperature_K, source_flow_setting_code)
    if model.family == 'SETTING_AWARE_EMPIRICAL':
        family = 'BOUNDARY_AWARE_EMPIRICAL'
        theta = setting_weights(t, f) @ np.asarray(model.coefficients)
    else:
        family = 'MASS'
        theta = recipe_coefficients(model.coefficients, float(t), float(f))
    curve = kernel.Model(model.model_id, family, tuple(theta), model.domain_kg,
                         model.fit_identity, model.rights, knots_kg=model.knots_kg)
    return kernel.integration_allowance(curve, start, end)


def synthetic_model():
    return Model('synthetic-nonzero-slopes-v1', 'MTF', (.2, 60., .8, .4, -.3, .2, .5),
                 (0., .06), {'kind': 'SYNTHETIC_NO_SOURCE_DATA'}, 'first-party synthetic fixture')


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, help='explicit serialized model; default synthetic MTF')
    parser.add_argument('--temperature-K', type=float, default=362.15)
    parser.add_argument('--source-flow-setting-code', type=float, default=2.)
    parser.add_argument('--stop-kg', type=float, default=.04)
    args = parser.parse_args()
    model = Model.load(args.model) if args.model else synthetic_model()
    recipes = [(args.temperature_K, args.source_flow_setting_code)] if args.model else [(353.15, 2.), (362.15, 2.), (371.15, 2.)]
    results = []
    for t, f in recipes:
        recipe = {'temperature_K': t, 'source_flow_setting_code': f}
        d = model.predict([0., .01], [.01, .02], **recipe)
        results.append(dict(recipe, interval_solute_kg=d.solute_kg.tolist(),
                            average_TDS_percent=d.tds_percent.tolist(),
                            conditional_solute_to_stop_kg=float(model.cumulative_solute(args.stop_kg, **recipe))))
    print(json.dumps({'model_id': model.model_id, 'family': model.family,
                      'actual_coefficients': model.coefficients, 'queries': results,
                      'claims': model.claims, 'rights': model.rights}, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()

"""Immutable research-only conditional interval delivery; no query-time fitting.

Mathematics and computational conventions: SCI-MD-MASS-DELIVERY-006/MODEL_CARD.md.
Source-derived fitted artifacts retain their own rights, separate from this code.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import expit

VERSION = 'conditional-tail-delivery/1'
ARMS = ('C0', 'C1', 'C2')
NAMES = ('MASS_CONTEXT_TAIL_SPLINE', 'FIRST_ASSAY_TAIL_SPLINE', 'CONDITIONAL_TAIL_SPLINE')
FEATURES = ('m1_kg', 'm2_kg', 'q1', 'q2')
SCALES = (.01, .01, .10, .10)
UNITS = {'beverage': 'kg', 'solute': 'kg', 'concentration': 'kg/kg',
         'TDS': 'percent', 'basis': 'MASS'}
SETTINGS = {'knots': 5, 'ftol': 1e-10, 'xtol': 1e-10, 'gtol': 1e-10,
            'jac': '2-point', 'diff_step': 1e-6, 'x_scale': 1., 'loss': 'linear',
            'method': 'trf', 'tr_solver': 'exact', 'coefficient_bound': 20.,
            'max_residual_calls': 8000, 'quad_epsabs_kg': 1e-14,
            'quad_epsrel': 2e-13, 'quad_limit': 200, 'max_solute_allowance_kg': 1e-9}
CLAIMS = ('RESEARCH_ONLY', 'SOURCE_INTERNAL', 'TARGET_EXPOSED',
          'RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION',
          'PHYSICAL_VALIDATION_NOT_ESTABLISHED', 'CONDITIONAL_ON_BEVERAGE_MASS',
          'NO_TIME_FLOW_PRESSURE_PREDICTION', 'NOT_INVENTORY_CLOSURE',
          'MODELED_GAPS_NOT_MEASURED_WHOLE_CUP', 'NO_REAL_TIME_ASSAY_CLAIM')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def identity(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def bad(value):
        raise ValueError('NONFINITE_JSON:'+value)
    return json.loads(text, object_pairs_hook=pairs, parse_constant=bad)


def exact_keys(value, keys):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise ValueError('STRICT_FIELDS_REQUIRED')


def number(value):
    if isinstance(value, (bool, str)) or value is None:
        raise ValueError('FINITE_NUMBER_REQUIRED')
    result = float(value)
    if not np.isfinite(result):
        raise ValueError('FINITE_NUMBER_REQUIRED')
    return result


def feature_names(arm):
    if arm not in ARMS:
        raise ValueError('UNKNOWN_ARM')
    return FEATURES[:2+ARMS.index(arm)]


@dataclass(frozen=True)
class EarlyInput:
    arm: str
    values: tuple[float, ...]
    input_class: str = 'SUPPLIED_EARLY_ASSAYS'
    mass_unit: str = 'kg'
    concentration_unit: str = 'kg/kg'
    basis: str = 'MASS'

    def __post_init__(self):
        names = feature_names(self.arm)
        v = tuple(number(x) for x in self.values)
        object.__setattr__(self, 'values', v)
        if len(v) != len(names) or any(x <= 0 for x in v[:2]):
            raise ValueError('INVALID_EARLY_MASSES_OR_FEATURE_COUNT')
        if any(not 0 <= x <= 1 for x in v[2:]):
            raise ValueError('INVALID_MASS_FRACTION_CONCENTRATION')
        if (self.mass_unit, self.concentration_unit, self.basis) != ('kg', 'kg/kg', 'MASS'):
            raise ValueError('UNSUPPORTED_UNITS_OR_BASIS')
        if self.input_class not in ('SUPPLIED_EARLY_ASSAYS', 'SOURCE_EARLY_INPUT', 'SYNTHETIC'):
            raise ValueError('EXPLICIT_INPUT_CLASS_REQUIRED')

    @classmethod
    def from_dict(cls, data):
        exact_keys(data, ('arm', 'values', 'input_class', 'mass_unit', 'concentration_unit', 'basis'))
        exact_keys(data['values'], feature_names(data['arm']))
        return cls(data['arm'], tuple(data['values'][n] for n in feature_names(data['arm'])),
                   *(data[k] for k in ('input_class', 'mass_unit', 'concentration_unit', 'basis')))

    def to_dict(self):
        return asdict(self) | {'values': dict(zip(feature_names(self.arm), self.values))}


def early_input(arm, *, input_class='SUPPLIED_EARLY_ASSAYS', **values):
    """Only active named features are accepted: C0 rejects q1/q2; C1 rejects q2."""
    exact_keys(values, feature_names(arm))
    return EarlyInput(arm, tuple(values[n] for n in feature_names(arm)), input_class)


def segment_average(left, right):
    """Stable softplus divided difference, including equal/extreme endpoints."""
    a, b = np.broadcast_arrays(np.asarray(left, float), np.asarray(right, float))
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError('NONFINITE_LOGIT')
    lo, hi = np.minimum(a, b), np.maximum(a, b)
    with np.errstate(over='ignore'):
        delta = hi-lo
    if not np.isfinite(delta).all():
        raise ValueError('LOGIT_RANGE_OVERFLOW')
    out = np.empty_like(delta)
    equal = delta == 0
    out[equal] = expit(lo[equal])
    near = (~equal) & (delta <= .5)
    out[near] = np.log1p(expit(lo[near])*np.expm1(delta[near]))/delta[near]
    pos = (delta > .5) & (lo >= 0)
    out[pos] = 1+(np.log1p(np.exp(-hi[pos]))-np.log1p(np.exp(-lo[pos])))/delta[pos]
    neg = (delta > .5) & (hi <= 0)
    out[neg] = (np.log1p(np.exp(hi[neg]))-np.log1p(np.exp(lo[neg])))/delta[neg]
    cross = (delta > .5) & (lo < 0) & (hi > 0)
    out[cross] = (hi[cross]+np.log1p(np.exp(-hi[cross]))-np.log1p(np.exp(lo[cross])))/delta[cross]
    if np.any(out < 0) or np.any(out > 1) or not np.isfinite(out).all():
        raise ValueError('CONCENTRATION_BOUND_FAILURE')
    return out


class IntervalGeometry:
    """Cached knot intersections; independent intervals never share a mass clock."""
    def __init__(self, starts, ends, domain):
        a, b = np.asarray(starts, float), np.asarray(ends, float)
        if (a.ndim != 1 or a.shape != b.shape or not np.isfinite(a).all()
                or not np.isfinite(b).all() or not np.isfinite(domain) or domain <= 0
                or np.any(a < 0) or np.any(b < a) or np.any(b > domain)):
            raise ValueError('INVALID_INTERVAL_OR_DOMAIN')
        self.count = len(a)
        self.knots = np.linspace(0, domain, 5)
        rows, knots, widths, u, v = [], [], [], [], []
        for i, (x, y) in enumerate(zip(a, b)):
            for j, (l, r) in enumerate(zip(self.knots[:-1], self.knots[1:])):
                start, end = max(x, l), min(y, r)
                if end > start:
                    rows.append(i); knots.append(j); widths.append(end-start)
                    u.append((start-l)/(r-l)); v.append((end-l)/(r-l))
        self.rows, self.segments = np.array(rows, int), np.array(knots, int)
        self.widths, self.u, self.v = map(np.asarray, (widths, u, v))

    def integrate(self, logits):
        values = np.asarray(logits, float)
        if values.shape != (self.count, 5) or not np.isfinite(values).all():
            raise ValueError('FIVE_FINITE_KNOT_LOGITS_PER_INTERVAL_REQUIRED')
        l = values[self.rows, self.segments]
        r = values[self.rows, self.segments+1]
        av = segment_average((1-self.u)*l+self.u*r, (1-self.v)*l+self.v*r)
        return np.bincount(self.rows, self.widths*av, minlength=self.count)


@dataclass(frozen=True)
class Model:
    arm: str
    theta: tuple[tuple[float, ...], ...]
    means: tuple[float, ...]
    minima: tuple[float, ...]
    maxima: tuple[float, ...]
    domain_kg: float
    regularization: float
    training_identity_json: str
    rights: str

    def __post_init__(self):
        n = len(feature_names(self.arm))
        for name in ('means', 'minima', 'maxima'):
            object.__setattr__(self, name, tuple(number(v) for v in getattr(self, name)))
        object.__setattr__(self, 'theta', tuple(tuple(number(v) for v in row) for row in self.theta))
        if (len(self.theta) != 5 or any(len(row) != n+1 for row in self.theta)
                or any(abs(v) > 20 for row in self.theta for v in row)
                or any(len(getattr(self, k)) != n for k in ('means', 'minima', 'maxima'))
                or any(not l-16*abs(np.spacing(l)) <= m <= h+16*abs(np.spacing(h))
                       for l, m, h in zip(self.minima, self.means, self.maxima))):
            raise ValueError('INVALID_COEFFICIENTS_OR_TRANSFORM')
        object.__setattr__(self, 'domain_kg', number(self.domain_kg))
        object.__setattr__(self, 'regularization', number(self.regularization))
        if self.domain_kg <= 0 or self.regularization not in (.0001, .01, 1., 100.):
            raise ValueError('INVALID_DOMAIN_OR_LAMBDA')
        info = strict_json(self.training_identity_json)
        if not isinstance(info, dict) or not info or not isinstance(self.rights, str) or not self.rights:
            raise ValueError('TRAINING_IDENTITY_AND_RIGHTS_REQUIRED')
        object.__setattr__(self, 'training_identity_json', canonical(info))

    def to_dict(self):
        return {'version': VERSION, 'arm': self.arm, 'family': NAMES[ARMS.index(self.arm)],
                'theta': [list(r) for r in self.theta], 'feature_order': list(feature_names(self.arm)),
                'means': list(self.means), 'minima': list(self.minima), 'maxima': list(self.maxima),
                'scales': list(SCALES[:len(self.means)]), 'domain_kg': [0., self.domain_kg],
                'regularization': self.regularization, 'units': dict(UNITS),
                'numerical_settings': dict(SETTINGS), 'limitations': list(CLAIMS),
                'training_identity': strict_json(self.training_identity_json), 'rights': self.rights}

    @property
    def sha256(self):
        return identity(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        exact_keys(data, ('version', 'arm', 'family', 'theta', 'feature_order', 'means', 'minima',
                         'maxima', 'scales', 'domain_kg', 'regularization', 'units',
                         'numerical_settings', 'limitations', 'training_identity', 'rights'))
        model = cls(data['arm'], data['theta'], data['means'], data['minima'], data['maxima'],
                    data['domain_kg'][1], data['regularization'], canonical(data['training_identity']), data['rights'])
        if canonical(model.to_dict()) != canonical(data):
            raise ValueError('MODEL_SCHEMA_TRANSFORM_UNITS_OR_SETTINGS_MISMATCH')
        return model

    def save(self, path):
        with Path(path).open('x') as stream:
            stream.write(canonical(self.to_dict())+'\n')

    @classmethod
    def load(cls, path):
        return cls.from_dict(strict_json(Path(path).read_text()))

    def condition(self, inputs):
        return State(self, inputs)


@dataclass(frozen=True)
class State:
    model: Model
    inputs: EarlyInput
    z: tuple[float, ...] = field(init=False)
    logits: tuple[float, ...] = field(init=False)
    feature_extrapolation: tuple[str, ...] = field(init=False)
    b_anchor: float = field(init=False)

    def __post_init__(self):
        if not isinstance(self.model, Model) or not isinstance(self.inputs, EarlyInput):
            raise ValueError('TYPED_IMMUTABLE_MODEL_AND_INPUT_REQUIRED')
        if self.inputs.arm != self.model.arm:
            raise ValueError('ARM_INFORMATION_CONTRACT_MISMATCH')
        anchor = sum(self.inputs.values[:2])
        if anchor > self.model.domain_kg:
            raise ValueError('ANCHOR_OUTSIDE_MASS_DOMAIN')
        z = tuple((v-m)/s for v, m, s in zip(self.inputs.values, self.model.means, SCALES))
        logits = np.asarray(self.model.theta) @ np.r_[1., z]
        if not np.isfinite(logits).all():
            raise ValueError('NONFINITE_FEATURE_LOGIT')
        object.__setattr__(self, 'z', z)
        object.__setattr__(self, 'logits', tuple(map(float, logits)))
        object.__setattr__(self, 'b_anchor', anchor)
        object.__setattr__(self, 'feature_extrapolation', tuple(n for n, v, l, h in zip(
            feature_names(self.model.arm), self.inputs.values, self.model.minima, self.model.maxima)
            if v < l or v > h))

    def to_dict(self):
        return {'version': VERSION, 'model': self.model.to_dict(), 'model_sha256': self.model.sha256,
                'inputs': self.inputs.to_dict(), 'z': list(self.z), 'logits': list(self.logits),
                'b_anchor': self.b_anchor, 'feature_extrapolation': list(self.feature_extrapolation)}

    @classmethod
    def from_dict(cls, data):
        exact_keys(data, ('version', 'model', 'model_sha256', 'inputs', 'z', 'logits',
                         'b_anchor', 'feature_extrapolation'))
        state = cls(Model.from_dict(data['model']), EarlyInput.from_dict(data['inputs']))
        if canonical(data) != canonical(state.to_dict()):
            raise ValueError('STATE_IDENTITY_OR_DERIVED_FIELD_MISMATCH')
        return state

    def predict_intervals(self, starts_kg, ends_kg, **kwargs):
        return predict_intervals(self, starts_kg, ends_kg, **kwargs)

    def remaining_solute(self, stop_mass_kg, **kwargs):
        return remaining_solute(self, stop_mass_kg, **kwargs)


@dataclass(frozen=True)
class Prediction:
    start_kg: float
    end_kg: float
    solute_kg: float
    tds_percent: float | None
    allowance_kg: float
    numerical_qualified: bool


def numerical_allowance(start, end, domain, logits, calculated):
    if start == end:
        return 0.
    knots = np.linspace(0, domain, 5)
    cuts = [start]+[b for b in knots if start < b < end]+[end]
    def f(b):
        return float(expit(np.interp(b, knots, logits)))
    totals, errors = [], []
    for refine in (False, True):
        total = error = 0.
        for lo, hi in zip(cuts[:-1], cuts[1:]):
            parts = (lo, (lo+hi)/2, hi) if refine else (lo, hi)
            for a, b in zip(parts[:-1], parts[1:]):
                value, err = quad(f, a, b, epsabs=1e-14, epsrel=2e-13, limit=200)
                total += value; error += err
        totals.append(total); errors.append(error)
    roundoff = 128*np.finfo(float).eps*((end-start)+abs(calculated))
    return float(max(abs(calculated-totals[0])+errors[0],
                     abs(calculated-totals[1])+errors[1],
                     abs(totals[0]-totals[1])+sum(errors))+roundoff)


def predict_intervals(state, starts_kg, ends_kg, *, mass_unit='kg', basis='MASS'):
    if not isinstance(state, State) or (mass_unit, basis) != ('kg', 'MASS'):
        raise ValueError('STATE_AND_KG_MASS_BASIS_REQUIRED')
    starts = tuple(number(v) for v in starts_kg)
    ends = tuple(number(v) for v in ends_kg)
    if any(x < state.b_anchor for x in starts):
        raise ValueError('QUERY_BEFORE_FORECAST_ANCHOR')
    geometry = IntervalGeometry(starts, ends, state.model.domain_kg)
    solutes = geometry.integrate(np.tile(state.logits, (len(starts), 1)))
    out = []
    for a, b, solute in zip(starts, ends, solutes):
        allowance = numerical_allowance(a, b, state.model.domain_kg, state.logits, solute)
        out.append(Prediction(a, b, float(solute), float(100*solute/(b-a)) if b > a else None,
                              allowance, bool(allowance <= 1e-9)))
    return tuple(out)


def remaining_solute(state, stop_mass_kg, **kwargs):
    return predict_intervals(state, (state.b_anchor,), (stop_mass_kg,), **kwargs)[0]


def synthetic_model(arm='C2'):
    n = len(feature_names(arm))
    return Model(arm, tuple(tuple([v]+[.1]*n) for v in (-1., -2., -3., -3.5, -4.)),
                 (.004, .004, .15, .10)[:n], (.002, .002, .05, .03)[:n],
                 (.008, .008, .25, .20)[:n], .08, .01,
                 canonical({'scope': 'SYNTHETIC_NOT_FITTED'}), 'SYNTHETIC_FIRST_PARTY')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--synthetic', action='store_true')
    parser.add_argument('--arm', choices=ARMS, default='C2')
    parser.add_argument('--save-model', type=Path)
    parser.add_argument('--load-model', type=Path)
    args = parser.parse_args()
    if not args.synthetic:
        parser.error('This public demonstration requires --synthetic; source commands are separate.')
    model = Model.load(args.load_model) if args.load_model else synthetic_model(args.arm)
    if args.save_model:
        model.save(args.save_model)
    state = model.condition(EarlyInput(model.arm, (.004, .004, .15, .10)[:len(model.means)], 'SYNTHETIC'))
    print(json.dumps({'input_class': 'SYNTHETIC', 'model_sha256': model.sha256,
        'predictions': [asdict(v) for v in predict_intervals(state, [.008, .02], [.02, .04])],
        'remaining': asdict(remaining_solute(state, .04)), 'claims': CLAIMS}, indent=2))


if __name__ == '__main__':
    main()

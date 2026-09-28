"""Saved-model trigonelline delivery; no source reader or optimizer.

Only the accepted D0 numerical geometry and strict JSON helpers are reused.
Neither a caffeine model nor its coefficients represent this species.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import expit

from . import conditional_caffeine_delivery as geometry_dependency

GEOMETRY_SHA256 = '4ce97309a213f017b6ada7f1ac595e4b59670a988f40de38191d642b54590e5a'
if hashlib.sha256(Path(geometry_dependency.__file__).read_bytes()).hexdigest() != GEOMETRY_SHA256:
    raise ValueError('ACCEPTED_D0_GEOMETRY_CHANGED')
Geometry = geometry_dependency.Geometry
canonical, identity, strict_json = (geometry_dependency.canonical, geometry_dependency.identity,
                                   geometry_dependency.strict_json)
number, exact_keys = geometry_dependency.number, geometry_dependency.exact_keys
VERSION = 'conditional-trigonelline-delivery/1'
SPECIES = 'trigonelline'
ARMS = ('TR-K0', 'TR-D0')
FEATURES = ('m1_kg', 'm2_kg')
SCALES = (.01, .01)
UNITS = {'beverage': 'kg', 'trigonelline': 'kg', 'concentration': 'kg/kg',
         'mass_display': 'mg', 'concentration_display': 'mg/g', 'basis': 'MASS'}
SETTINGS = {'knots': 5, 'quadrature_points': 64, 'reference_points': 128,
            'quad_epsabs_kg': 1e-14, 'quad_epsrel': 2e-13, 'quad_limit': 200,
            'max_trigonelline_allowance_kg': 1e-9, 'coefficient_bound': 20.}
CLAIMS = ('RESEARCH_ONLY', 'SOURCE_INTERNAL', 'TARGET_EXPOSED',
          'RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION',
          'NO_GOVERNING_PHYSICS_CHANGE', 'PHYSICAL_VALIDATION_NOT_ESTABLISHED',
          'ANALYTICAL_UNCERTAINTY_NOT_ESTABLISHED', 'TRIGONELLINE_IS_COMPONENT_OF_TDS',
          'MODELED_GAPS_NOT_MEASURED_WHOLE_CUP', 'NOT_INVENTORY_CLOSURE',
          'CONDITIONAL_ON_BEVERAGE_MASS', 'NO_QUERY_TIME_CHEMICAL_ASSAY')


@dataclass(frozen=True)
class EarlyInput:
    arm: str
    values: tuple[float, float]
    input_class: str = 'SUPPLIED_EARLY_INPUT'
    mass_unit: str = 'kg'
    basis: str = 'MASS'
    species: str = SPECIES

    def __post_init__(self):
        object.__setattr__(self, 'values', tuple(number(x) for x in self.values))
        if (self.arm not in ARMS or self.species != SPECIES or len(self.values) != 2
                or any(x <= 0 for x in self.values)):
            raise ValueError('TWO_POSITIVE_MASSES_AND_TRIGONELLINE_ARM_REQUIRED')
        if (self.mass_unit, self.basis) != ('kg', 'MASS'):
            raise ValueError('KG_MASS_BASIS_REQUIRED')
        if self.input_class not in ('SUPPLIED_EARLY_INPUT', 'SOURCE_EARLY_INPUT', 'SYNTHETIC'):
            raise ValueError('INPUT_CLASS_REQUIRED')

    def to_dict(self):
        return asdict(self) | {'values': dict(zip(FEATURES, self.values))}

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, ('arm', 'values', 'input_class', 'mass_unit', 'basis', 'species'))
        exact_keys(value['values'], FEATURES)
        return cls(value['arm'], tuple(value['values'][k] for k in FEATURES),
                   *(value[k] for k in ('input_class', 'mass_unit', 'basis', 'species')))


@dataclass(frozen=True)
class Model:
    arm: str
    theta: tuple[tuple[float, ...], ...]
    means: tuple[float, float]
    minima: tuple[float, float]
    maxima: tuple[float, float]
    domain_kg: float
    regularization: float | None
    constant_q: float | None
    training_identity_json: str
    rights: str
    species: str = SPECIES

    def __post_init__(self):
        if self.arm not in ARMS or self.species != SPECIES:
            raise ValueError('TRIGONELLINE_SPECIES_AND_ARM_REQUIRED')
        for name in ('means', 'minima', 'maxima'):
            object.__setattr__(self, name, tuple(number(v) for v in getattr(self, name)))
        object.__setattr__(self, 'theta', tuple(tuple(number(v) for v in r) for r in self.theta))
        object.__setattr__(self, 'domain_kg', number(self.domain_kg))
        if self.domain_kg <= 0 or any(len(getattr(self, k)) != 2 for k in ('means', 'minima', 'maxima')):
            raise ValueError('POSITIVE_DOMAIN_AND_TRAINING_MASS_TRANSFORM_REQUIRED')
        if any(not 0 < lo <= hi or not lo-16*abs(np.spacing(lo)) <= m <= hi+16*abs(np.spacing(hi))
               for lo, m, hi in zip(self.minima, self.means, self.maxima)):
            raise ValueError('INVALID_TRAINING_MASS_TRANSFORM')
        if self.arm == 'TR-K0':
            if self.theta or self.regularization is not None or self.constant_q is None:
                raise ValueError('ONE_CONSTANT_CONCENTRATION_ONLY')
            object.__setattr__(self, 'constant_q', number(self.constant_q))
            if self.constant_q < 0:
                raise ValueError('NONNEGATIVE_CONSTANT_REQUIRED')
        elif (len(self.theta) != 5 or any(len(r) != 3 for r in self.theta)
              or any(abs(v) > 20 for r in self.theta for v in r)
              or self.regularization not in (.0001, .01, 1., 100.) or self.constant_q is not None):
            raise ValueError('DECLARED_D0_COEFFICIENTS_AND_LAMBDA_REQUIRED')
        info = strict_json(self.training_identity_json)
        if not isinstance(info, dict) or not info or not self.rights:
            raise ValueError('TRAINING_PROVENANCE_AND_RIGHTS_REQUIRED')
        object.__setattr__(self, 'training_identity_json', canonical(info))

    def to_dict(self):
        return {'version': VERSION, 'species': SPECIES, 'arm': self.arm,
                'theta': [list(r) for r in self.theta], 'constant_q': self.constant_q,
                'input_order': list(FEATURES), 'feature_order': list(FEATURES) if self.arm == 'TR-D0' else [],
                'means': list(self.means), 'minima': list(self.minima), 'maxima': list(self.maxima),
                'scales': list(SCALES), 'domain_kg': [0., self.domain_kg],
                'regularization': self.regularization, 'geometry_sha256': GEOMETRY_SHA256,
                'training_identity': strict_json(self.training_identity_json), 'rights': self.rights,
                'units': dict(UNITS), 'settings': dict(SETTINGS), 'claims': list(CLAIMS)}

    @property
    def sha256(self):
        return identity(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        if data.get('species') != SPECIES or data.get('version') != VERSION:
            raise ValueError('STRICT_TRIGONELLINE_SPECIES_AND_VERSION_REQUIRED')
        model = cls(data['arm'], data['theta'], data['means'], data['minima'], data['maxima'],
                    data['domain_kg'][1], data['regularization'], data['constant_q'],
                    canonical(data['training_identity']), data['rights'], data['species'])
        if canonical(data) != canonical(model.to_dict()):
            raise ValueError('TRIGONELLINE_SCHEMA_UNITS_OR_IDENTITY_MISMATCH')
        return model

    def save(self, path):
        with Path(path).open('x') as stream:
            stream.write(canonical({'model': self.to_dict(), 'model_sha256': self.sha256})+'\n')

    @classmethod
    def load(cls, path):
        value = strict_json(Path(path).read_text())
        exact_keys(value, ('model', 'model_sha256'))
        model = cls.from_dict(value['model'])
        if model.sha256 != value['model_sha256']:
            raise ValueError('MODEL_CONTENT_HASH_MISMATCH')
        return model

    def condition(self, inputs):
        return State(self, inputs)


@dataclass(frozen=True)
class State:
    model: Model
    inputs: EarlyInput
    logits: tuple[float, ...] = field(init=False)
    b_anchor: float = field(init=False)
    feature_extrapolation: tuple[str, ...] = field(init=False)

    def __post_init__(self):
        if not isinstance(self.model, Model) or not isinstance(self.inputs, EarlyInput) or self.model.arm != self.inputs.arm:
            raise ValueError('MATCHING_TYPED_TRIGONELLINE_MODEL_AND_INPUT_REQUIRED')
        m, v = self.model, self.inputs.values
        anchor = sum(v)
        if anchor > m.domain_kg:
            raise ValueError('ANCHOR_OUTSIDE_HARD_DOMAIN')
        z = (np.asarray(v)-m.means)/SCALES
        logits = tuple(map(float, np.asarray(m.theta) @ np.r_[1., z])) if m.arm == 'TR-D0' else ()
        if not np.isfinite(logits).all():
            raise ValueError('NONFINITE_LOGITS')
        flags = tuple(k for k, x, lo, hi in zip(FEATURES, v, m.minima, m.maxima) if x < lo or x > hi)
        object.__setattr__(self, 'logits', logits)
        object.__setattr__(self, 'b_anchor', anchor)
        object.__setattr__(self, 'feature_extrapolation', flags)

    def to_dict(self):
        return {'version': VERSION, 'species': SPECIES, 'model': self.model.to_dict(),
                'model_sha256': self.model.sha256, 'inputs': self.inputs.to_dict(),
                'logits': list(self.logits), 'b_anchor': self.b_anchor,
                'feature_extrapolation': list(self.feature_extrapolation)}

    @classmethod
    def from_dict(cls, value):
        state = cls(Model.from_dict(value['model']), EarlyInput.from_dict(value['inputs']))
        if canonical(value) != canonical(state.to_dict()):
            raise ValueError('TRIGONELLINE_STATE_IDENTITY_OR_DERIVED_FIELD_MISMATCH')
        return state

    def predict_intervals(self, starts_kg, ends_kg, **kwargs):
        return predict_intervals(self, starts_kg, ends_kg, **kwargs)

    def remaining_trigonelline(self, stop_mass_kg, **kwargs):
        return predict_intervals(self, [self.b_anchor], [stop_mass_kg], **kwargs)[0]


def _integrals(state, a, b, points):
    g = Geometry(a, b, state.model.domain_kg, state.model.domain_kg, points)
    return g.integrate(np.tile(state.logits, (len(a), 1)), share=state.model.constant_q)


def _reference(state, a, b):
    if a == b:
        return 0., 0.
    knots = np.linspace(0., state.model.domain_kg, 5)
    def f(x):
        return state.model.constant_q if state.model.arm == 'TR-K0' else float(expit(np.interp(x, knots, state.logits)))
    cuts = [a]+[x for x in knots if a < x < b]+[b]
    total = error = 0.
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        value, err = quad(f, lo, hi, epsabs=1e-14, epsrel=2e-13, limit=200)
        total += value; error += err
    return total, error


@dataclass(frozen=True)
class Prediction:
    start_kg: float
    end_kg: float
    trigonelline_kg: float
    trigonelline_mg: float
    trigonelline_mg_g: float | None
    allowance_kg: float
    difference_64_128_kg: float
    difference_adaptive_kg: float
    reference_error_kg: float
    floating_point_allowance_kg: float
    numerical_qualified: bool
    support: str
    feature_extrapolation: tuple[str, ...]
    species: str = SPECIES
    claims: tuple[str, ...] = CLAIMS


def predict_intervals(state, starts_kg, ends_kg, *, mass_unit='kg', basis='MASS'):
    if not isinstance(state, State) or (mass_unit, basis) != ('kg', 'MASS'):
        raise ValueError('TRIGONELLINE_STATE_AND_KG_MASS_BASIS_REQUIRED')
    a, b = tuple(number(x) for x in starts_kg), tuple(number(x) for x in ends_kg)
    if any(x < state.b_anchor for x in a):
        raise ValueError('QUERY_BEFORE_ANCHOR')
    low, high = _integrals(state, a, b, 64), _integrals(state, a, b, 128)
    predictions = []
    for start, end, value, refined in zip(a, b, low, high):
        ref, err = _reference(state, start, end)
        delta, adaptive = abs(value-refined), abs(value-ref)
        fp = 128*np.finfo(float).eps*(end-start+abs(value))
        allowance = max(delta, adaptive+err, abs(refined-ref)+err)+fp
        qualified = bool(np.isfinite([value, allowance, ref, err]).all() and allowance <= 1e-9)
        predictions.append(Prediction(start, end, float(value), float(1e6*value),
            float(1000*value/(end-start)) if end > start else None, float(allowance),
            float(delta), float(adaptive), float(err), float(fp), qualified,
            'FEATURE_EXTRAPOLATION_DIAGNOSTIC' if state.feature_extrapolation else 'IN_DOMAIN',
            state.feature_extrapolation))
    return tuple(predictions)

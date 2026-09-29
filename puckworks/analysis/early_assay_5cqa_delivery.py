"""Strict species-tagged matched early-assay 5CQA research inference; no fitting or sources."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import ClassVar

import numpy as np
from scipy.integrate import quad
from scipy.special import expit

from . import conditional_5cqa_delivery as legacy

Geometry = legacy.Geometry
canonical, identity, strict_json = legacy.canonical, legacy.identity, legacy.strict_json
number, exact_keys = legacy.number, legacy.exact_keys
VERSION = 'early-assay-5cqa-delivery/1'
SPECIES = '5CQA'
ARMS = ('L1M', 'L2M', 'L12')
FEATURES = ('m1_kg', 'm2_kg', 'q1_kg_kg', 'q2_kg_kg')
HARD_UPPER_KG = 0.06971540000000001


def feature_names(arm):
    if arm not in ARMS:
        raise ValueError('DECLARED_EARLY_ASSAY_ARM_REQUIRED')
    return FEATURES if arm == 'L12' else FEATURES[:2]+(FEATURES[2 if arm == 'L1M' else 3],)


def scales(arm):
    return (.01,)*len(feature_names(arm))


UNITS = dict(legacy.UNITS)
SETTINGS = {'knots': 5, 'quadrature_points': 64, 'reference_points': 128,
            'quad_epsabs_kg': 1e-14, 'quad_epsrel': 2e-13, 'quad_limit': 200,
            'max_five_cqa_allowance_kg': 1e-9, 'coefficient_bound': 20.}
CLAIMS = tuple(c for c in legacy.CLAIMS if c != 'NO_QUERY_TIME_CHEMICAL_ASSAY') + (
    'ARM_SPECIFIC_EARLY_FIVE_CQA_ASSAY_REQUIRED', 'NO_JOINT_TDS_COMPOSITION_CLOSURE',
    'NO_REAL_TIME_HPLC_CONTROL',)


@dataclass(frozen=True)
class EarlyInput:
    """Base schema; construct a named arm subclass or use strict from_dict."""
    m1_kg: float
    m2_kg: float
    input_class: str = field(default='SUPPLIED_EARLY_INPUT', kw_only=True)
    mass_unit: str = field(default='kg', kw_only=True)
    concentration_unit: str = field(default='kg/kg', kw_only=True)
    basis: str = field(default='MASS', kw_only=True)
    species: str = field(default=SPECIES, kw_only=True)
    arm: ClassVar[str] = ''

    def __post_init__(self):
        if type(self) not in (L1MInput, L2MInput, L12Input):
            raise ValueError('EXACT_ARM_SPECIFIC_INPUT_SCHEMA_REQUIRED')
        for name in feature_names(self.arm):
            object.__setattr__(self, name, number(getattr(self, name)))
        if self.m1_kg <= 0 or self.m2_kg <= 0 or any(not 0 <= q <= 1 for q in self.values[2:]):
            raise ValueError('POSITIVE_MASSES_AND_VALID_EARLY_ASSAYS_REQUIRED')
        if (self.mass_unit, self.concentration_unit, self.basis, self.species) != (
                'kg', 'kg/kg', 'MASS', SPECIES):
            raise ValueError('STRICT_FIVE_CQA_SI_MASS_UNITS_REQUIRED')
        if self.input_class not in ('SUPPLIED_EARLY_INPUT', 'SOURCE_EARLY_INPUT', 'SYNTHETIC'):
            raise ValueError('INPUT_CLASS_REQUIRED')

    @property
    def values(self):
        return tuple(getattr(self, n) for n in feature_names(self.arm))

    def to_dict(self):
        return dict(asdict(self), arm=self.arm)

    @classmethod
    def from_dict(cls, value):
        arm = value.get('arm')
        names = feature_names(arm)
        exact_keys(value, (*names, 'arm', 'input_class', 'mass_unit', 'concentration_unit',
                           'basis', 'species'))
        schema = {'L1M': L1MInput, 'L2M': L2MInput, 'L12': L12Input}[arm]
        if cls is not EarlyInput and cls is not schema:
            raise ValueError('WRONG_ARM_INPUT_SCHEMA')
        return schema(**{k: v for k, v in value.items() if k != 'arm'})


@dataclass(frozen=True)
class L1MInput(EarlyInput):
    q1_kg_kg: float
    arm: ClassVar[str] = 'L1M'


@dataclass(frozen=True)
class L2MInput(EarlyInput):
    q2_kg_kg: float
    arm: ClassVar[str] = 'L2M'


@dataclass(frozen=True)
class L12Input(EarlyInput):
    q1_kg_kg: float
    q2_kg_kg: float
    arm: ClassVar[str] = 'L12'


def assay_from_mg_g(value, *, species=SPECIES, unit='mg/g'):
    """Named 5CQA interval average; percent is a different quantity."""
    if species != SPECIES or unit != 'mg/g':
        raise ValueError('FIVE_CQA_MG_PER_G_REQUIRED')
    q = number(value)/1000
    if not 0 <= q <= 1:
        raise ValueError('INVALID_EARLY_ASSAY')
    return q


@dataclass(frozen=True)
class Model:
    arm: str
    theta: tuple[tuple[float, ...], ...]
    means: tuple[float, ...]
    minima: tuple[float, ...]
    maxima: tuple[float, ...]
    domain_kg: float
    regularization: float | None
    training_identity_json: str
    rights: str
    species: str = SPECIES

    def __post_init__(self):
        if self.arm not in ARMS or self.species != SPECIES:
            raise ValueError('FIVE_CQA_SPECIES_AND_ARM_REQUIRED')
        for name in ('means', 'minima', 'maxima'):
            object.__setattr__(self, name, tuple(number(v) for v in getattr(self, name)))
        object.__setattr__(self, 'theta', tuple(tuple(number(v) for v in r) for r in self.theta))
        object.__setattr__(self, 'domain_kg', number(self.domain_kg))
        if (not 0 < self.domain_kg <= HARD_UPPER_KG
                or any(len(getattr(self, k)) != len(feature_names(self.arm)) for k in ('means', 'minima', 'maxima'))):
            raise ValueError('HARD_DOMAIN_AND_ARM_FEATURE_TRANSFORM_REQUIRED')
        for index, (lo, mean, hi) in enumerate(zip(self.minima, self.means, self.maxima)):
            if (lo > hi or (lo <= 0 if index < 2 else not 0 <= lo <= hi <= 1)
                    or not lo-16*abs(np.spacing(lo)) <= mean <= hi+16*abs(np.spacing(hi))):
                raise ValueError('INVALID_TRAINING_FEATURE_TRANSFORM')
        if self.regularization is not None:
            object.__setattr__(self, 'regularization', number(self.regularization))
        if (len(self.theta) != 5 or any(len(r) != 1+len(feature_names(self.arm)) for r in self.theta)
                or any(abs(v) > 20 for r in self.theta for v in r)
                or self.regularization not in (.0001, .01, 1., 100.)):
            raise ValueError('EXACT_20_20_25_BOUNDED_COEFFICIENTS_REQUIRED')
        info = strict_json(self.training_identity_json)
        if (not isinstance(info, dict) or info.get('species') != SPECIES
                or not isinstance(self.rights, str) or not self.rights):
            raise ValueError('SPECIES_TRAINING_PROVENANCE_AND_RIGHTS_REQUIRED')
        object.__setattr__(self, 'training_identity_json', canonical(info))

    def to_dict(self):
        return {'version': VERSION, 'species': SPECIES, 'arm': self.arm,
                'theta': [list(r) for r in self.theta], 'input_order': list(feature_names(self.arm)),
                'feature_order': list(feature_names(self.arm)),
                'means': list(self.means), 'minima': list(self.minima), 'maxima': list(self.maxima),
                'scales': list(scales(self.arm)), 'domain_kg': [0., self.domain_kg],
                'regularization': self.regularization,
                'geometry_sha256': legacy.GEOMETRY_SHA256,
                'training_identity': strict_json(self.training_identity_json), 'rights': self.rights,
                'units': dict(UNITS), 'settings': dict(SETTINGS), 'claims': list(CLAIMS)}

    @property
    def sha256(self):
        return identity(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        keys = ('version', 'species', 'arm', 'theta', 'input_order', 'feature_order',
                'means', 'minima', 'maxima', 'scales', 'domain_kg', 'regularization',
                'geometry_sha256',
                'training_identity', 'rights', 'units', 'settings', 'claims')
        exact_keys(data, keys)
        if (data['version'] != VERSION or data['species'] != SPECIES
                or not isinstance(data['domain_kg'], list) or len(data['domain_kg']) != 2):
            raise ValueError('STRICT_FIVE_CQA_SPECIES_SCHEMA_AND_VERSION_REQUIRED')
        model = cls(data['arm'], data['theta'], data['means'], data['minima'], data['maxima'],
                    data['domain_kg'][1], data['regularization'],
                    canonical(data['training_identity']), data['rights'], data['species'])
        if canonical(data) != canonical(model.to_dict()):
            raise ValueError('FIVE_CQA_SCHEMA_UNITS_OR_IDENTITY_MISMATCH')
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

    def condition(self, early_input):
        return State(self, early_input)


@dataclass(frozen=True)
class State:
    model: Model
    inputs: EarlyInput
    logits: tuple[float, ...] = field(init=False)
    b_anchor: float = field(init=False)
    feature_extrapolation: tuple[str, ...] = field(init=False)

    def __post_init__(self):
        if (not isinstance(self.model, Model) or not isinstance(self.inputs, EarlyInput)
                or self.model.arm != self.inputs.arm):
            raise ValueError('MATCHING_TYPED_FIVE_CQA_MODEL_AND_ARM_INPUT_REQUIRED')
        m, values = self.model, self.inputs.values
        anchor = sum(values[:2])
        if not np.isfinite(anchor) or anchor > m.domain_kg:
            raise ValueError('ANCHOR_OUTSIDE_HARD_DOMAIN')
        z = (np.asarray(values)-m.means)/scales(m.arm)
        logits = tuple(map(float, np.asarray(m.theta) @ np.r_[1., z]))
        if not np.isfinite(logits).all():
            raise ValueError('NONFINITE_LOGITS')
        flags = tuple(k for k, x, lo, hi in zip(feature_names(m.arm), values, m.minima, m.maxima)
                      if x < lo or x > hi)
        object.__setattr__(self, 'logits', logits)
        object.__setattr__(self, 'b_anchor', anchor)
        object.__setattr__(self, 'feature_extrapolation', flags)

    def to_dict(self):
        return {'version': VERSION, 'species': SPECIES, 'model': self.model.to_dict(),
                'model_sha256': self.model.sha256, 'inputs': self.inputs.to_dict(),
                'logits': list(self.logits),
                'b_anchor': self.b_anchor, 'feature_extrapolation': list(self.feature_extrapolation)}

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, ('version', 'species', 'model', 'model_sha256', 'inputs',
                           'logits', 'b_anchor', 'feature_extrapolation'))
        state = cls(Model.from_dict(value['model']), EarlyInput.from_dict(value['inputs']))
        if canonical(value) != canonical(state.to_dict()):
            raise ValueError('FIVE_CQA_STATE_IDENTITY_OR_DERIVED_FIELD_MISMATCH')
        return state

    def predict_intervals(self, starts_kg, ends_kg, **kwargs):
        return predict_intervals(self, starts_kg, ends_kg, **kwargs)

    def remaining_5cqa(self, stop_mass_kg, **kwargs):
        return predict_intervals(self, [self.b_anchor], [stop_mass_kg], **kwargs)[0]


def _integrals(state, a, b, points):
    geometry = Geometry(a, b, state.model.domain_kg, state.model.domain_kg, points)
    return geometry.integrate(np.tile(state.logits, (len(a), 1)))


def _reference(state, a, b):
    if a == b:
        return 0., 0.
    knots = np.linspace(0., state.model.domain_kg, 5)
    def f(x):
        return float(expit(np.interp(x, knots, state.logits)))
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
    five_cqa_kg: float
    five_cqa_mg: float
    five_cqa_mg_g: float | None
    allowance_kg: float
    difference_64_128_kg: float
    difference_adaptive_kg: float
    reference_error_kg: float
    floating_point_allowance_kg: float
    numerical_qualified: bool
    hard_domain_supported: bool
    support: str
    feature_extrapolation: tuple[str, ...]
    model_sha256: str
    training_identity_json: str
    rights: str
    units: tuple[tuple[str, str], ...] = tuple(UNITS.items())
    species: str = SPECIES
    claims: tuple[str, ...] = CLAIMS


def predict_intervals(state, starts_kg, ends_kg, *, mass_unit='kg', basis='MASS'):
    if not isinstance(state, State) or (mass_unit, basis) != ('kg', 'MASS'):
        raise ValueError('FIVE_CQA_STATE_AND_KG_MASS_BASIS_REQUIRED')
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
        qualified = bool(np.isfinite([value, allowance, ref, err]).all()
                         and 0 <= value <= end-start and allowance <= 1e-9)
        predictions.append(Prediction(start, end, float(value), float(1e6*value),
            float(1000*value/(end-start)) if end > start else None, float(allowance),
            float(delta), float(adaptive), float(err), float(fp), qualified, True,
            'FEATURE_EXTRAPOLATION_DIAGNOSTIC' if state.feature_extrapolation else 'IN_DOMAIN',
            state.feature_extrapolation, state.model.sha256, state.model.training_identity_json,
            state.model.rights))
    return tuple(predictions)

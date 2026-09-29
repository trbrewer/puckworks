"""Strict species-tagged first-assay 5CQA research inference; no fitting or sources."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.special import expit

from . import conditional_5cqa_delivery as legacy

Geometry = legacy.Geometry
canonical, identity, strict_json = legacy.canonical, legacy.identity, legacy.strict_json
number, exact_keys = legacy.number, legacy.exact_keys
VERSION = 'assay-conditioned-5cqa-delivery/1'
SPECIES = '5CQA'
ARMS = ('A1', 'L1')
FEATURES = ('m1_kg', 'm2_kg', 'q1_kg_kg')
SCALES = (.01, .01, .01)
TAU_KG = 0.02319173692244203
E0_SHA256 = 'f1c27d0c942234761a274ee52e38a9912fe0e5a47ae72269d43103c646a9106d'
HARD_UPPER_KG = 0.06971540000000001
UNITS = dict(legacy.UNITS)
SETTINGS = {'knots': 5, 'quadrature_points': 64, 'reference_points': 128,
            'quad_epsabs_kg': 1e-14, 'quad_epsrel': 2e-13, 'quad_limit': 200,
            'max_five_cqa_allowance_kg': 1e-9, 'coefficient_bound': 20.,
            'amplitude_bounds_kg_kg': (0., 1.)}
CLAIMS = tuple(c for c in legacy.CLAIMS if c != 'NO_QUERY_TIME_CHEMICAL_ASSAY') + (
    'FIRST_FRACTION_FIVE_CQA_ASSAY_REQUIRED', 'NO_JOINT_TDS_COMPOSITION_CLOSURE',
    'NO_REAL_TIME_HPLC_CONTROL',)


@dataclass(frozen=True)
class EarlyInput:
    m1_kg: float
    m2_kg: float
    q1_kg_kg: float
    input_class: str = 'SUPPLIED_EARLY_INPUT'
    mass_unit: str = 'kg'
    concentration_unit: str = 'kg/kg'
    basis: str = 'MASS'
    species: str = SPECIES

    def __post_init__(self):
        for name in FEATURES:
            object.__setattr__(self, name, number(getattr(self, name)))
        if self.m1_kg <= 0 or self.m2_kg <= 0 or not 0 <= self.q1_kg_kg <= 1:
            raise ValueError('POSITIVE_MASSES_AND_VALID_FIRST_ASSAY_REQUIRED')
        if (self.mass_unit, self.concentration_unit, self.basis, self.species) != (
                'kg', 'kg/kg', 'MASS', SPECIES):
            raise ValueError('STRICT_FIVE_CQA_SI_MASS_UNITS_REQUIRED')
        if self.input_class not in ('SUPPLIED_EARLY_INPUT', 'SOURCE_EARLY_INPUT', 'SYNTHETIC'):
            raise ValueError('INPUT_CLASS_REQUIRED')

    @property
    def values(self):
        return tuple(getattr(self, n) for n in FEATURES)

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, (*FEATURES, 'input_class', 'mass_unit', 'concentration_unit',
                           'basis', 'species'))
        return cls(**value)


def first_assay_from_mg_g(value, *, species=SPECIES, unit='mg/g'):
    """Explicit named-analyte conversion, never percent or generic CGA."""
    if species != SPECIES or unit != 'mg/g':
        raise ValueError('FIVE_CQA_MG_PER_G_REQUIRED')
    q = number(value)/1000
    if not 0 <= q <= 1:
        raise ValueError('INVALID_FIRST_ASSAY')
    return q


def normalized_amplitude(inputs):
    """The first assay is an interval average over [0,m1], not a point value."""
    if not isinstance(inputs, EarlyInput):
        raise ValueError('TYPED_FIRST_ASSAY_REQUIRED')
    ratio = inputs.m1_kg/TAU_KG
    denominator = -np.expm1(-ratio)
    amplitude = inputs.q1_kg_kg*(ratio/denominator)
    if not np.isfinite(amplitude) or not 0 <= amplitude <= 1:
        raise ValueError('UNPHYSICAL_NORMALIZED_AMPLITUDE')
    return float(amplitude)


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
                or any(len(getattr(self, k)) != 3 for k in ('means', 'minima', 'maxima'))):
            raise ValueError('HARD_DOMAIN_AND_THREE_FEATURE_TRANSFORM_REQUIRED')
        for index, (lo, mean, hi) in enumerate(zip(self.minima, self.means, self.maxima)):
            if (lo > hi or (lo <= 0 if index < 2 else not 0 <= lo <= hi <= 1)
                    or not lo-16*abs(np.spacing(lo)) <= mean <= hi+16*abs(np.spacing(hi))):
                raise ValueError('INVALID_TRAINING_FEATURE_TRANSFORM')
        if self.regularization is not None:
            object.__setattr__(self, 'regularization', number(self.regularization))
        if self.arm == 'A1':
            if self.theta or self.regularization is not None:
                raise ValueError('A1_HAS_NO_FITTED_GLOBAL_COEFFICIENTS')
        elif (len(self.theta) != 5 or any(len(r) != 4 for r in self.theta)
              or any(abs(v) > 20 for r in self.theta for v in r)
              or self.regularization not in (.0001, .01, 1., 100.)):
            raise ValueError('EXACT_TWENTY_BOUNDED_L1_COEFFICIENTS_REQUIRED')
        info = strict_json(self.training_identity_json)
        if (not isinstance(info, dict) or info.get('species') != SPECIES
                or not isinstance(self.rights, str) or not self.rights):
            raise ValueError('SPECIES_TRAINING_PROVENANCE_AND_RIGHTS_REQUIRED')
        object.__setattr__(self, 'training_identity_json', canonical(info))

    def to_dict(self):
        return {'version': VERSION, 'species': SPECIES, 'arm': self.arm,
                'theta': [list(r) for r in self.theta], 'input_order': list(FEATURES),
                'feature_order': list(FEATURES) if self.arm == 'L1' else [],
                'means': list(self.means), 'minima': list(self.minima), 'maxima': list(self.maxima),
                'scales': list(SCALES), 'domain_kg': [0., self.domain_kg],
                'regularization': self.regularization,
                'fixed_decay_kg': TAU_KG if self.arm == 'A1' else None,
                'E0_semantic_sha256': E0_SHA256 if self.arm == 'A1' else None,
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
                'fixed_decay_kg', 'E0_semantic_sha256', 'geometry_sha256',
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
    amplitude: float | None = field(init=False)
    b_anchor: float = field(init=False)
    feature_extrapolation: tuple[str, ...] = field(init=False)

    def __post_init__(self):
        if not isinstance(self.model, Model) or not isinstance(self.inputs, EarlyInput):
            raise ValueError('TYPED_FIVE_CQA_MODEL_AND_FIRST_ASSAY_REQUIRED')
        m, values = self.model, self.inputs.values
        anchor = sum(values[:2])
        if not np.isfinite(anchor) or anchor > m.domain_kg:
            raise ValueError('ANCHOR_OUTSIDE_HARD_DOMAIN')
        z = (np.asarray(values)-m.means)/SCALES
        logits = tuple(map(float, np.asarray(m.theta) @ np.r_[1., z])) if m.arm == 'L1' else ()
        if not np.isfinite(logits).all():
            raise ValueError('NONFINITE_LOGITS')
        flags = tuple(k for k, x, lo, hi in zip(FEATURES, values, m.minima, m.maxima)
                      if x < lo or x > hi)
        object.__setattr__(self, 'logits', logits)
        object.__setattr__(self, 'amplitude', normalized_amplitude(self.inputs) if m.arm == 'A1' else None)
        object.__setattr__(self, 'b_anchor', anchor)
        object.__setattr__(self, 'feature_extrapolation', flags)

    def to_dict(self):
        return {'version': VERSION, 'species': SPECIES, 'model': self.model.to_dict(),
                'model_sha256': self.model.sha256, 'inputs': self.inputs.to_dict(),
                'logits': list(self.logits), 'amplitude': self.amplitude,
                'b_anchor': self.b_anchor, 'feature_extrapolation': list(self.feature_extrapolation)}

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, ('version', 'species', 'model', 'model_sha256', 'inputs',
                           'logits', 'amplitude', 'b_anchor', 'feature_extrapolation'))
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
    if state.model.arm == 'A1':
        return legacy.exponential_integrals(a, b, state.amplitude, TAU_KG)
    return geometry.integrate(np.tile(state.logits, (len(a), 1)))


def _reference(state, a, b):
    if a == b:
        return 0., 0.
    knots = np.linspace(0., state.model.domain_kg, 5)
    def f(x):
        return (state.amplitude*np.exp(-x/TAU_KG) if state.model.arm == 'A1'
                else float(expit(np.interp(x, knots, state.logits))))
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

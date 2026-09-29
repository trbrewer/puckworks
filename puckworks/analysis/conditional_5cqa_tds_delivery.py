"""Species-specific research 5-CQA composition over immutable C2; no source reader or optimizer.

The source-derived artifacts have separate CC-BY-NC rights. 5-CQA is already
part of TDS. This module never changes EWP physics or the task-006 parent.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import importlib.util
from pathlib import Path
import sys

import numpy as np
from scipy.integrate import quad
from scipy.special import expit

PARENT_RUNTIME_SHA256 = '4fb20dd42e0ed7d5a758f549d616131988a1dab05ddc49b9253441606f155e33'
FINAL_PARENT_SHA256 = '960e0c7dd37d3ba876f95a44c00c69f222e53c022a641e4b092a2af686fb9516'


def verified_geometry():
    """Reuse numerical primitives from the verified sibling; no package fallback."""
    path = Path(__file__).resolve().with_name('conditional_caffeine_delivery.py')
    expected = '4ce97309a213f017b6ada7f1ac595e4b59670a988f40de38191d642b54590e5a'
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('IMMUTABLE_GEOMETRY_RUNTIME_MISMATCH')
    name = '_five_cqa_tds_geometry_'+expected
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError('VERIFIED_SIBLING_RUNTIME_REQUIRED')
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


geometry_dependency = verified_geometry()
parent = geometry_dependency.parent
Geometry = geometry_dependency.Geometry
canonical, identity, strict_json = parent.canonical, parent.identity, parent.strict_json
number, exact_keys = parent.number, parent.exact_keys
VERSION = 'conditional-5cqa-tds-delivery/1'
SPECIES = '5CQA'
ARMS = ('S0', 'S1', 'S2')
FEATURES = ('m1_kg', 'm2_kg', 'q1', 'q2')
SCALES = (.01, .01, .10, .10)
UNITS = {'beverage': 'kg', '5CQA': 'kg', 'mass_display': 'mg',
         'concentration': 'kg/kg', 'concentration_display': 'mg/g', 'basis': 'MASS'}
SETTINGS = {'knots': 5, 'quadrature_points': 64, 'reference_points': 128,
            'quad_epsabs_kg': 1e-14, 'quad_epsrel': 2e-13, 'quad_limit': 200,
            'max_five_cqa_allowance_kg': 1e-9, 'coefficient_bound': 20.}
CLAIMS = ('RESEARCH_ONLY', 'SOURCE_INTERNAL', 'TARGET_EXPOSED',
          'RETROSPECTIVE_CAMPAIGN_SEPARATED_CONDITIONAL_PREDICTION',
          'PHYSICAL_VALIDATION_NOT_ESTABLISHED', 'FIVE_CQA_IS_COMPONENT_OF_TDS',
          'MODEL_SHARE_CONSTRAINT_NOT_MEASURED_CHEMICAL_CLOSURE',
          'MODELED_GAPS_NOT_MEASURED_WHOLE_CUP', 'NOT_INVENTORY_CLOSURE',
          'CONDITIONAL_ON_BEVERAGE_MASS', 'NO_QUERY_TIME_FIVE_CQA_ASSAY', 'NO_GOVERNING_PHYSICS_CHANGE',
          'ANALYTICAL_UNCERTAINTY_NOT_ESTABLISHED')


def feature_names(arm):
    if arm not in ARMS:
        raise ValueError('UNKNOWN_ARM')
    return FEATURES


def head_feature_names(arm):
    return () if arm == 'S0' else FEATURES[:4 if arm == 'S2' else 2]


@dataclass(frozen=True)
class EarlyInput:
    arm: str
    values: tuple[float, ...]
    input_class: str = 'SUPPLIED_EARLY_INPUT'
    mass_unit: str = 'kg'
    concentration_unit: str = 'kg/kg'
    basis: str = 'MASS'
    species: str = SPECIES

    def __post_init__(self):
        if self.species != SPECIES:
            raise ValueError('FIVE_CQA_SPECIES_REQUIRED')
        values = tuple(number(x) for x in self.values)
        object.__setattr__(self, 'values', values)
        if len(values) != len(feature_names(self.arm)) or any(x <= 0 for x in values[:2]):
            raise ValueError('INVALID_EARLY_MASSES_OR_FEATURE_COUNT')
        if any(not 0 <= x <= 1 for x in values[2:]):
            raise ValueError('INVALID_TDS_MASS_FRACTION')
        if (self.mass_unit, self.concentration_unit, self.basis) != ('kg', 'kg/kg', 'MASS'):
            raise ValueError('WRONG_UNITS_OR_BASIS')
        if self.input_class not in ('SUPPLIED_EARLY_INPUT', 'SOURCE_EARLY_INPUT', 'SYNTHETIC'):
            raise ValueError('INPUT_CLASS_REQUIRED')

    def to_dict(self):
        return asdict(self) | {'values': dict(zip(feature_names(self.arm), self.values))}

    @classmethod
    def from_dict(cls, value):
        exact_keys(value, ('arm', 'values', 'input_class', 'mass_unit', 'concentration_unit', 'basis', 'species'))
        exact_keys(value['values'], feature_names(value['arm']))
        return cls(value['arm'], tuple(value['values'][k] for k in feature_names(value['arm'])),
                   *(value[k] for k in ('input_class', 'mass_unit', 'concentration_unit', 'basis', 'species')))


@dataclass(frozen=True)
class Model:
    arm: str
    theta: tuple[tuple[float, ...], ...]
    means: tuple[float, ...]
    minima: tuple[float, ...]
    maxima: tuple[float, ...]
    knot_domain_kg: float
    domain_kg: float
    regularization: float | None
    share: float | None
    parent_json: str
    training_identity_json: str
    rights: str
    species: str = SPECIES

    def __post_init__(self):
        if self.arm not in ARMS or self.species != SPECIES:
            raise ValueError('FIVE_CQA_SPECIES_AND_SHARE_ARM_REQUIRED')
        n = len(head_feature_names(self.arm))
        for name in ('means', 'minima', 'maxima'):
            object.__setattr__(self, name, tuple(number(v) for v in getattr(self, name)))
        object.__setattr__(self, 'theta', tuple(tuple(number(v) for v in r) for r in self.theta))
        for name in ('knot_domain_kg', 'domain_kg'):
            object.__setattr__(self, name, number(getattr(self, name)))
        if not 0 < self.domain_kg <= self.knot_domain_kg:
            raise ValueError('INVALID_HARD_DOMAIN')
        if any(len(getattr(self, k)) != n for k in ('means', 'minima', 'maxima')):
            raise ValueError('INVALID_TRANSFORM')
        if any(not lo-16*abs(np.spacing(lo)) <= m <= hi+16*abs(np.spacing(hi))
               for lo, m, hi in zip(self.minima, self.means, self.maxima)):
            raise ValueError('INVALID_TRANSFORM_RANGE')
        if self.arm == 'S0':
            if self.theta or self.regularization is not None or self.share is None:
                raise ValueError('SCALAR_SHARE_ONLY')
            object.__setattr__(self, 'share', number(self.share))
            if not 0 <= self.share <= 1:
                raise ValueError('INVALID_SHARE')
        elif (len(self.theta) != 5 or any(len(r) != n+1 for r in self.theta)
              or any(abs(v) > 20 for r in self.theta for v in r)
              or self.regularization not in (.0001, .01, 1., 100.) or self.share is not None):
            raise ValueError('INVALID_HEAD_COEFFICIENTS_OR_LAMBDA')
        info = strict_json(self.training_identity_json)
        if not isinstance(info, dict) or not info or not self.rights:
            raise ValueError('PROVENANCE_AND_RIGHTS_REQUIRED')
        object.__setattr__(self, 'training_identity_json', canonical(info))
        p = parent.Model.from_dict(strict_json(self.parent_json))
        if p.arm != 'C2' or p.domain_kg != self.knot_domain_kg:
            raise ValueError('C2_PARENT_AND_EXACT_KNOTS_REQUIRED')
        if any(tuple(getattr(self, k)) != tuple(getattr(p, k)[:n])
               for k in ('means', 'minima', 'maxima')):
            raise ValueError('EXACT_PARENT_TRANSFORMS_REQUIRED')
        if info.get('scope') == 'FINAL_FIT' and (
                p.sha256 != FINAL_PARENT_SHA256 or self.domain_kg > 0.06971540000000001):
            raise ValueError('FINAL_PARENT_CONTENT_OR_DOMAIN_MISMATCH')
        object.__setattr__(self, 'parent_json', canonical(p.to_dict()))

    def to_dict(self):
        return {'version': VERSION, 'species': self.species, 'arm': self.arm, 'theta': [list(r) for r in self.theta],
                'feature_order': list(head_feature_names(self.arm)), 'means': list(self.means),
                'minima': list(self.minima), 'maxima': list(self.maxima),
                'scales': list(SCALES[:len(self.means)]), 'knot_domain_kg': self.knot_domain_kg,
                'domain_kg': [0., self.domain_kg], 'regularization': self.regularization,
                'share': self.share, 'parent': strict_json(self.parent_json) if self.parent_json else None,
                'parent_sha256': identity(strict_json(self.parent_json)) if self.parent_json else None,
                'parent_runtime_sha256': PARENT_RUNTIME_SHA256 if self.parent_json else None,
                'training_identity': strict_json(self.training_identity_json), 'rights': self.rights,
                'units': dict(UNITS), 'settings': dict(SETTINGS), 'claims': list(CLAIMS)}

    @property
    def sha256(self):
        return identity(self.to_dict())

    @classmethod
    def from_dict(cls, data):
        model = cls(data['arm'], data['theta'], data['means'], data['minima'], data['maxima'],
                    data['knot_domain_kg'], data['domain_kg'][1], data['regularization'],
                    data['share'], canonical(data['parent']) if data['parent'] else None,
                    canonical(data['training_identity']), data['rights'], data['species'])
        if canonical(data) != canonical(model.to_dict()):
            raise ValueError('MODEL_SCHEMA_UNITS_OR_PARENT_MISMATCH')
        return model

    def save(self, path):
        with Path(path).open('x') as stream:
            stream.write(canonical({'model': self.to_dict(), 'model_sha256': self.sha256})+'\n')

    @classmethod
    def load(cls, path):
        data = strict_json(Path(path).read_text())
        exact_keys(data, ('model', 'model_sha256'))
        model = cls.from_dict(data['model'])
        if model.sha256 != data['model_sha256']:
            raise ValueError('MODEL_CONTENT_HASH_MISMATCH')
        return model

    def condition(self, inputs):
        return State(self, inputs)


@dataclass(frozen=True)
class State:
    model: Model
    inputs: EarlyInput
    logits: tuple[float, ...] = field(init=False)
    parent_state: object = field(init=False, repr=False)
    b_anchor: float = field(init=False)
    feature_extrapolation: tuple[str, ...] = field(init=False)

    def __post_init__(self):
        if not isinstance(self.model, Model) or not isinstance(self.inputs, EarlyInput) or self.model.arm != self.inputs.arm:
            raise ValueError('TYPED_MATCHING_MODEL_INPUT_REQUIRED')
        m, v = self.model, self.inputs.values
        anchor = sum(v[:2])
        if anchor > m.domain_kg:
            raise ValueError('ANCHOR_OUTSIDE_HARD_DOMAIN')
        n = len(m.means)
        z = (np.asarray(v[:n])-m.means)/SCALES[:n]
        logits = tuple(map(float, np.asarray(m.theta) @ np.r_[1., z])) if m.arm != 'S0' else ()
        if not np.isfinite(logits).all():
            raise ValueError('NONFINITE_LOGITS')
        ps = None
        if m.parent_json:
            p = parent.Model.from_dict(strict_json(m.parent_json))
            ps = p.condition(parent.EarlyInput('C2', v, 'SYNTHETIC' if self.inputs.input_class == 'SYNTHETIC' else 'SOURCE_EARLY_INPUT'))
        flags = tuple(k for k, x, lo, hi in zip(head_feature_names(m.arm), v, m.minima, m.maxima) if x < lo or x > hi)
        flags = tuple(sorted(set(flags) | set(ps.feature_extrapolation if ps else ())))
        for key, value in [('logits', logits), ('parent_state', ps), ('b_anchor', anchor), ('feature_extrapolation', flags)]:
            object.__setattr__(self, key, value)

    def to_dict(self):
        return {'version': VERSION, 'model': self.model.to_dict(), 'model_sha256': self.model.sha256,
                'inputs': self.inputs.to_dict(), 'logits': list(self.logits), 'b_anchor': self.b_anchor,
                'parent_state': self.parent_state.to_dict() if self.parent_state else None,
                'feature_extrapolation': list(self.feature_extrapolation)}

    @classmethod
    def from_dict(cls, data):
        state = cls(Model.from_dict(data['model']), EarlyInput.from_dict(data['inputs']))
        if canonical(data) != canonical(state.to_dict()):
            raise ValueError('STATE_HASH_OR_DERIVED_FIELD_MISMATCH')
        return state

    def predict_intervals(self, starts_kg, ends_kg, **kwargs):
        return predict_intervals(self, starts_kg, ends_kg, **kwargs)

    def remaining_5cqa(self, stop_mass_kg, **kwargs):
        return remaining_5cqa(self, stop_mass_kg, **kwargs)


def _integrals(state, a, b, points):
    g = Geometry(a, b, state.model.knot_domain_kg, state.model.domain_kg, points)
    pv = g.values(np.tile(state.parent_state.logits, (len(a), 1))) if state.parent_state else None
    return g.integrate(np.tile(state.logits, (len(a), 1)), pv, state.model.share)


def _reference(state, a, b):
    if a == b:
        return 0., 0.
    knots = np.linspace(0, state.model.knot_domain_kg, 5)
    def f(x):
        head = state.model.share if state.model.arm == 'S0' else expit(np.interp(x, knots, state.logits))
        return float(head*expit(np.interp(x, knots, state.parent_state.logits)) if state.parent_state else head)
    cuts = [a]+[x for x in knots if a < x < b]+[b]
    total = error = 0.
    for lo, hi in zip(cuts[:-1], cuts[1:]):
        val, err = quad(f, lo, hi, epsabs=1e-14, epsrel=2e-13, limit=200)
        total += val; error += err
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
    support: str
    feature_extrapolation: tuple[str, ...]
    parent_tds_percent: float | None
    model_sha256: str
    species: str = SPECIES
    claims: tuple[str, ...] = CLAIMS


def predict_intervals(state, starts_kg, ends_kg, *, mass_unit='kg', basis='MASS'):
    if not isinstance(state, State) or (mass_unit, basis) != ('kg', 'MASS'):
        raise ValueError('STATE_AND_KG_MASS_BASIS_REQUIRED')
    a, b = tuple(number(x) for x in starts_kg), tuple(number(x) for x in ends_kg)
    if any(x < state.b_anchor for x in a):
        raise ValueError('QUERY_BEFORE_ANCHOR')
    values, high = _integrals(state, a, b, 64), _integrals(state, a, b, 128)
    tds = parent.predict_intervals(state.parent_state, a, b) if state.parent_state else [None]*len(a)
    out = []
    for lo, hi, value, h, t in zip(a, b, values, high, tds):
        ref, err = _reference(state, lo, hi)
        diff, adaptive = abs(value-h), abs(value-ref)
        fp = 128*np.finfo(float).eps*(hi-lo+abs(value))
        allowance = max(diff, adaptive+err, abs(h-ref)+err)+fp
        finite = np.isfinite([value, allowance, ref, err]).all()
        out.append(Prediction(lo, hi, float(value), float(1e6*value),
            float(1000*value/(hi-lo)) if hi > lo else None, float(allowance), float(diff),
            float(adaptive), float(err), float(fp), bool(finite and allowance <= 1e-9),
            'FEATURE_EXTRAPOLATION_DIAGNOSTIC' if state.feature_extrapolation else 'IN_DOMAIN',
            state.feature_extrapolation, t.tds_percent if t else None, state.model.sha256))
    return tuple(out)


def remaining_5cqa(state, stop_mass_kg, **kwargs):
    return predict_intervals(state, [state.b_anchor], [stop_mass_kg], **kwargs)[0]


def synthetic_model(arm='S2'):
    p = parent.synthetic_model('C2')
    n = len(head_feature_names(arm))
    return Model(arm, () if arm == 'S0' else [[-3.]+[.1]*n]*5,
        p.means[:n], p.minima[:n], p.maxima[:n], p.domain_kg, p.domain_kg,
        None if arm == 'S0' else .01, .05 if arm == 'S0' else None,
        canonical(p.to_dict()), canonical({'scope': 'SYNTHETIC'}), 'SYNTHETIC_FIRST_PARTY')

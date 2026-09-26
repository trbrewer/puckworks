"""Research-only single-observation amplitude update of immutable frozen curves.

No corpus access. Future queries carry coordinates only. Source-derived states
inherit their base and observation rights and must remain outside public Git.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from . import mass_delivery as kernel
from . import conditioned_mass_delivery as conditioned

VERSION = 'anchored-mass-delivery/1'
UNITS = {'beverage': 'kg', 'solute': 'kg', 'concentration': 'kg/kg',
         'anchor_TDS': 'percent', 'average_TDS': 'percent', 'basis': 'MASS'}
CLAIMS = kernel.LIMITATIONS + ('EARLY_ASSAY_CONDITIONED_NOT_RECIPE_ONLY',
    'ALPHA_NOT_IDENTIFIED_INVENTORY', 'NO_REAL_TIME_ASSAY_OR_CONTROLLER_CLAIM',
    'ASSAYED_SUFFIX_NOT_MEASURED_WHOLE_CUP')
REAL_LABELS = ('SOURCE_INTERNAL', 'TARGET_EXPOSED',
               'RETROSPECTIVE_EARLY_ASSAY_CONDITIONED_COMPARISON')


def strict_json(text):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError('DUPLICATE_JSON_KEY')
            out[k] = v
        return out
    def invalid(_):
        raise ValueError('NONFINITE_JSON')
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)


def finite(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError('FINITE_SCALAR_REQUIRED')


def roundoff(value):
    return 16 * math.ulp(float(value))


@dataclass(frozen=True)
class IntervalQuery:
    start_kg: float
    end_kg: float

    def __post_init__(self):
        finite(self.start_kg)
        finite(self.end_kg)
        if self.start_kg < 0 or self.end_kg < 0:
            raise ValueError('NEGATIVE_QUERY')
        if self.end_kg < self.start_kg:
            raise ValueError('REVERSED_QUERY')


@dataclass(frozen=True)
class AnchorInput:
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
        if self.end_kg <= self.start_kg:
            raise ValueError('NONPOSITIVE_ANCHOR_MASS')
        if not 0 <= self.tds_percent <= 100:
            raise ValueError('INVALID_ANCHOR_TDS')
        if self.tds_basis != 'MASS' or self.tds_unit != 'percent':
            raise ValueError('UNSUPPORTED_TDS_BASIS_OR_UNIT')
        if type(self.fraction_id) is not int or self.fraction_id != 1:
            raise ValueError('SOURCE_FRACTION_ONE_REQUIRED')
        if not all(isinstance(x, str) and x for x in (self.shot_id, self.source_id, self.rights)):
            raise ValueError('ANCHOR_IDENTITY_AND_RIGHTS_REQUIRED')
        bases = {'SYNTHETIC_ANCHOR_INPUT': 'SYNTHETIC_KG',
                 'MEASURED_SOURCE_ANCHOR_INPUT': 'MEASURED_MASS_G_CONVERTED_TO_KG'}
        if bases.get(self.input_class) != self.mass_basis:
            raise ValueError('UNSUPPORTED_ANCHOR_MASS_BASIS')


@dataclass(frozen=True)
class NominalSetting:
    temperature_K: float
    source_flow_setting_code: float
    setting_kind: str = 'CONSTANT'

    def __post_init__(self):
        finite(self.temperature_K)
        finite(self.source_flow_setting_code)
        if self.setting_kind != 'CONSTANT':
            raise ValueError('NOT_ADJUDICATED_VARIABLE_SETTING_INPUT')
        conditioned.setting_weights(*conditioned.features(
            self.temperature_K, self.source_flow_setting_code))


@dataclass(frozen=True)
class FrozenBase:
    """Exact artifact bytes held as immutable text; no mutable model references."""
    artifact_json: str
    sha256: str = field(init=False)
    model_id: str = field(init=False)

    def __post_init__(self):
        if not isinstance(self.artifact_json, str):
            raise ValueError('ARTIFACT_JSON_TEXT_REQUIRED')
        data = strict_json(self.artifact_json)
        if not isinstance(data, dict):
            raise ValueError('MODEL_OBJECT_REQUIRED')
        cls = conditioned.Model if data.get('family') == 'SETTING_AWARE_EMPIRICAL' else kernel.Model
        model = cls.from_dict(data)
        if model.family not in ('MASS', 'BOUNDARY_AWARE_EMPIRICAL', 'SETTING_AWARE_EMPIRICAL'):
            raise ValueError('UNAUTHORIZED_BASE_FAMILY')
        object.__setattr__(self, 'sha256', hashlib.sha256(self.artifact_json.encode()).hexdigest())
        object.__setattr__(self, 'model_id', model.model_id)

    @classmethod
    def load(cls, path):
        return cls(Path(path).read_bytes().decode('utf-8'))

    @classmethod
    def from_model(cls, model):
        return cls(json.dumps(model.to_dict(), sort_keys=True, allow_nan=False))

    def curve(self, setting=None):
        data = strict_json(self.artifact_json)
        if data['family'] == 'SETTING_AWARE_EMPIRICAL':
            if type(setting) is not NominalSetting:
                raise ValueError('TYPED_NOMINAL_SETTING_REQUIRED')
            model = conditioned.Model.from_dict(data)
            t, f = conditioned.features(setting.temperature_K, setting.source_flow_setting_code)
            profile = conditioned.setting_weights(t, f) @ np.asarray(model.coefficients)
            # This is the inherited fixed-recipe projection, not a fit or shape change.
            return kernel.Model(model.model_id, 'BOUNDARY_AWARE_EMPIRICAL', tuple(profile),
                model.domain_kg, model.fit_identity, model.rights, claims=model.claims,
                knots_kg=model.knots_kg)
        if setting is not None:
            raise ValueError('SETTING_NOT_USED_BY_BASE')
        return kernel.Model.from_dict(data)


def integral(curve, start, end):
    value = float(curve.predict(start, end).solute_kg)
    allowance = kernel.integration_allowance(curve, start, end)
    if end > start:
        allowance += roundoff(value)
    if not math.isfinite(value + allowance) or value < 0:
        raise ValueError('NONPHYSICAL_OR_NONFINITE_DELIVERY')
    return value, allowance


def maximum_concentration(curve, start):
    """Analytical monotone maximum or exact linear-segment endpoint/knots maximum."""
    if curve.family == 'MASS':
        c, k, p = curve.coefficients
        return float(c * math.exp(-(k * start)**p))
    points = [start, curve.domain_kg[1]] + [k for k in curve.knots_kg if k >= start]
    return float(max(np.interp(points, curve.knots_kg, curve.coefficients)))


@dataclass(frozen=True)
class Prediction:
    start_kg: float
    end_kg: float
    solute_kg: float
    tds_percent: float | None
    numerical_allowance_kg: float
    anchor_error_amplification: float | None
    amplification_allowance: float | None


@dataclass(frozen=True)
class AnchoredState:
    base: FrozenBase
    observation: AnchorInput
    setting: NominalSetting | None = None
    alpha: float = field(init=False)
    alpha_allowance: float = field(init=False)
    anchor_integral_kg: float = field(init=False)
    anchor_integral_allowance_kg: float = field(init=False)
    maximum_anchored_concentration: float = field(init=False)
    future_domain_kg: tuple = field(init=False)
    claims: tuple = field(init=False)

    def __post_init__(self):
        if type(self.base) is not FrozenBase or type(self.observation) is not AnchorInput:
            raise ValueError('TYPED_BASE_AND_ANCHOR_REQUIRED')
        a = self.observation
        curve = self.base.curve(self.setting)
        if a.start_kg < curve.domain_kg[0] or a.end_kg > curve.domain_kg[1]:
            raise ValueError('UNSUPPORTED_ANCHOR_INTERVAL')
        denominator, error = integral(curve, a.start_kg, a.end_kg)
        if denominator <= 0 or denominator-error <= 0 or error/denominator > 1e-6:
            raise ValueError('NUMERICALLY_UNRESOLVED_ANCHOR_DENOMINATOR')
        observed = (a.end_kg-a.start_kg) * (a.tds_percent/100)
        alpha = observed/denominator
        # Includes floating numerator, division and inherited integral allowance;
        # never substitutes source rounding or an invented assay uncertainty.
        allowance = (observed+roundoff(observed))/(denominator-error) - alpha + roundoff(alpha)
        if a.tds_percent == 0:
            alpha, allowance = 0., 0.
        qmax = maximum_concentration(curve, a.start_kg)
        maximum = alpha*qmax
        if not math.isfinite(alpha+allowance+maximum) or maximum > 1:
            raise ValueError('ANCHORED_CONCENTRATION_EXCEEDS_ONE')
        bound_allowance = allowance*qmax + roundoff(maximum)
        # Exact constant unit concentration is admissible, despite generic
        # conservative numerical allowances on its exact denominator.
        exact_unit = (curve.family == 'MASS' and curve.coefficients[1] == 0
                      and a.tds_percent == 100)
        if maximum+bound_allowance > 1 and not exact_unit:
            raise ValueError('NUMERICALLY_UNRESOLVED_CONCENTRATION_BOUND')
        labels = REAL_LABELS if a.input_class == 'MEASURED_SOURCE_ANCHOR_INPUT' else ('SYNTHETIC_ANCHOR_INPUT',)
        for key, value in dict(alpha=alpha, alpha_allowance=allowance,
                anchor_integral_kg=denominator, anchor_integral_allowance_kg=error,
                maximum_anchored_concentration=maximum,
                future_domain_kg=(a.end_kg, curve.domain_kg[1]),
                claims=tuple(dict.fromkeys(CLAIMS + tuple(curve.claims) + labels))).items():
            object.__setattr__(self, key, value)

    @property
    def numerical_qualification(self):
        return 'QUALIFIED'

    def predict_intervals(self, queries):
        queries = tuple(queries)
        if any(type(q) is not IntervalQuery for q in queries):
            raise ValueError('COORDINATE_ONLY_TYPED_QUERY_REQUIRED')
        curve = self.base.curve(self.setting)
        out = []
        for q in queries:
            if q.start_kg < self.future_domain_kg[0]:
                raise ValueError('QUERY_BEFORE_ANCHOR_COMPLETION')
            if q.end_kg > self.future_domain_kg[1]:
                raise ValueError('OUTSIDE_FROZEN_MASS_DOMAIN')
            if q.start_kg == q.end_kg:
                out.append(Prediction(q.start_kg, q.end_kg, 0., None, 0., None, None))
                continue
            value, error = integral(curve, q.start_kg, q.end_kg)
            solute = self.alpha*value
            allowance = (self.alpha*error + self.alpha_allowance*(value+error)
                         + roundoff(solute)) if self.alpha else 0.
            if not math.isfinite(solute+allowance) or solute < 0:
                raise ValueError('NONPHYSICAL_OR_NONFINITE_DELIVERY')
            if allowance > 1e-9:
                raise ValueError('NUMERICALLY_UNRESOLVED_FUTURE_INTEGRAL')
            width = q.end_kg-q.start_kg
            mass = self.observation.end_kg-self.observation.start_kg
            amplification = mass*value/(width*self.anchor_integral_kg)
            upper = mass*(value+error)/(width*(self.anchor_integral_kg-self.anchor_integral_allowance_kg))
            amp_error = upper-amplification+roundoff(amplification)
            out.append(Prediction(q.start_kg, q.end_kg, solute, 100*solute/width,
                                  allowance, amplification, amp_error))
        return tuple(out)

    def remaining_solute(self, stop_kg):
        """Qualified delivery from anchor completion to a supplied stopping mass."""
        return self.predict_intervals((IntervalQuery(self.future_domain_kg[0], stop_kg),))[0]

    def to_dict(self):
        return {'version': VERSION, 'units': dict(UNITS), 'base': asdict(self.base),
            'anchor': asdict(self.observation), 'setting': asdict(self.setting) if self.setting else None,
            'alpha': self.alpha, 'alpha_allowance': self.alpha_allowance,
            'anchor_integral_kg': self.anchor_integral_kg,
            'anchor_integral_allowance_kg': self.anchor_integral_allowance_kg,
            'maximum_anchored_concentration': self.maximum_anchored_concentration,
            'future_domain_kg': list(self.future_domain_kg), 'claims': list(self.claims),
            'numerical_qualification': self.numerical_qualification}

    @classmethod
    def from_dict(cls, data):
        try:
            for key in ('alpha', 'alpha_allowance', 'anchor_integral_kg',
                        'anchor_integral_allowance_kg', 'maximum_anchored_concentration'):
                finite(data[key])
            base = FrozenBase(data['base']['artifact_json'])
            state = cls(base, AnchorInput(**data['anchor']),
                        NominalSetting(**data['setting']) if data['setting'] is not None else None)
            if state.to_dict() != data:
                raise ValueError('ANCHORED_STATE_SCHEMA_OR_DERIVED_VALUE_MISMATCH')
            return state
        except (KeyError, TypeError) as error:
            raise ValueError('MALFORMED_ANCHORED_STATE') from error

    @classmethod
    def load(cls, path):
        return cls.from_dict(strict_json(Path(path).read_text()))

    def save(self, path):
        with Path(path).open('x') as stream:
            json.dump(self.to_dict(), stream, sort_keys=True, indent=2, allow_nan=False)
            stream.write('\n')


def anchor(base, observation, *, setting=None):
    return AnchoredState(base, observation, setting)


def synthetic_observation():
    return AnchorInput('synthetic-shot', 'synthetic-source', 1, 0., .004, 12.,
                       'SYNTHETIC_KG', 'first-party synthetic fixture', 'SYNTHETIC_ANCHOR_INPUT')


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path, help='optional frozen base; anchor remains synthetic')
    parser.add_argument('--stop-kg', type=float, default=.04)
    args = parser.parse_args()
    base = FrozenBase.load(args.model) if args.model else FrozenBase.from_model(kernel.Model(
        'synthetic-base', 'MASS', (.15, 40., .8), (0., .06),
        {'kind': 'SYNTHETIC_NO_SOURCE_DATA'}, 'first-party synthetic fixture'))
    state = anchor(base, synthetic_observation())
    print(json.dumps({'input_class': 'SYNTHETIC_ANCHOR_INPUT', 'base_model_id': base.model_id,
        'base_sha256': base.sha256, 'alpha': state.alpha, 'claims': state.claims,
        'predictions': [asdict(p) for p in state.predict_intervals((IntervalQuery(.004, .01),))],
        'remaining': asdict(state.remaining_solute(args.stop_kg))}, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()

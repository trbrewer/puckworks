"""008 immutable source-calibration wrappers; the accepted parent is never mutated.

SI interfaces, strict role types, no target assays or query-time fitting.
Computational contract: sci_md_mass_delivery_008/MODEL_CARD.md.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
import math
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

from . import conditional_tail_delivery as md
from . import grudeva_clock as gc
from . import grudeva_pooled_tail_delivery as pooled

VERSION = 'source-calibrated-tail/1'
CLAIMS = ('RESEARCH_ONLY', 'TARGET_EXPOSED',
          'RETROSPECTIVE_ONE_CALIBRATION_SHOT_SOURCE_ADAPTATION',
          'CONDITIONAL_ON_COLLECTED_BEVERAGE_MASS_AND_PERMITTED_EARLY_CHEMISTRY',
          'PHYSICAL_VALIDATION_NOT_ESTABLISHED')
BRACKET = (-20., 20.)
RADII = (1e-10, 1e-9, 1e-8, 1e-7, 1e-6)
ROOT_SETTINGS = {'bracket': list(BRACKET), 'xtol': 1e-12,
                 'rtol': 4*np.finfo(float).eps, 'maxiter': 200, 'radii': list(RADII)}


def sha_string(value):
    if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        raise ValueError('SHA256_IDENTITY_REQUIRED')
    return value


def shot_number(value):
    if type(value) is not int or value < 1:
        raise ValueError('PHYSICAL_SHOT_ID_REQUIRED')
    return value


class Serialized:
    @property
    def sha256(self):
        return md.identity(self.to_dict())

    def save(self, path):
        with Path(path).open('x') as stream:
            stream.write(md.canonical(self.to_dict())+'\n')

    @classmethod
    def load(cls, path, **kwargs):
        return cls.from_dict(md.strict_json(Path(path).read_text()), **kwargs)


@dataclass(frozen=True)
class Observation:
    """One calibration-only observation; never accepted by a prediction state."""
    shot: int
    vial: int
    mass_kg: float
    start_kg: float
    end_kg: float
    q: float | None

    def __post_init__(self):
        shot_number(self.shot)
        pooled.checked_query({k: getattr(self, k) for k in ('shot', 'vial', 'mass_kg', 'start_kg', 'end_kg')})
        for k in ('mass_kg', 'start_kg', 'end_kg'):
            object.__setattr__(self, k, md.number(getattr(self, k)))
        if self.q is not None:
            object.__setattr__(self, 'q', md.number(self.q))
            if not 0 <= self.q <= 1 or self.mass_kg == 0:
                raise ValueError('MASS_FRACTION_OR_STRUCTURAL_ZERO_CONTRACT')

    @classmethod
    def from_dict(cls, value):
        md.exact_keys(value, cls.__dataclass_fields__)
        return cls(**value)


@dataclass(frozen=True)
class CalibrationRecord(Serialized):
    source_sha256: str
    shot: int
    early: md.EarlyInput | None
    windows: tuple[Observation, ...]

    def __post_init__(self):
        sha_string(self.source_sha256); shot_number(self.shot)
        object.__setattr__(self, 'windows', tuple(self.windows))
        if (not self.windows or any(not isinstance(w, Observation) or w.shot != self.shot for w in self.windows)
                or len({w.vial for w in self.windows}) != len(self.windows)):
            raise ValueError('ONE_SHOT_UNIQUE_WINDOWS_REQUIRED')
        if self.early is not None and (not isinstance(self.early, md.EarlyInput) or self.early.arm not in ('C0', 'C2')):
            raise ValueError('TYPED_PERMITTED_EARLY_INPUT_REQUIRED')

    def to_dict(self):
        return {'version': VERSION, 'units': dict(md.UNITS), 'source_sha256': self.source_sha256,
                'shot': self.shot, 'early': self.early.to_dict() if self.early else None,
                'windows': [asdict(w) for w in self.windows]}

    @classmethod
    def from_dict(cls, value):
        md.exact_keys(value, ('version', 'units', 'source_sha256', 'shot', 'early', 'windows'))
        obj = cls(value['source_sha256'], value['shot'],
                  md.EarlyInput.from_dict(value['early']) if value['early'] is not None else None,
                  tuple(Observation.from_dict(w) for w in value['windows']))
        if md.canonical(value) != md.canonical(obj.to_dict()):
            raise ValueError('CALIBRATION_RECORD_SCHEMA_OR_UNITS_MISMATCH')
        return obj


def shifted_integrals(parent_state, delta, starts, ends):
    geometry = md.IntervalGeometry(starts, ends, parent_state.model.domain_kg)
    return geometry.integrate(np.tile(np.asarray(parent_state.logits)+delta, (len(starts), 1)))


def mass_bounds(parent_state, delta, starts, ends, coordinate_allowance):
    values = shifted_integrals(parent_state, delta, starts, ends)
    logits = np.asarray(parent_state.logits)+delta
    uncertainty = math.fsum(md.numerical_allowance(a, b, parent_state.model.domain_kg, logits, v)
                            for a, b, v in zip(starts, ends, values))
    uncertainty += coordinate_allowance + 128*np.finfo(float).eps*math.fsum(abs(v) for v in values)
    total = math.fsum(values)
    return total-uncertainty, total+uncertainty


def certify_enclosure(parent_state, delta, starts, ends, observed, observed_allowance, coordinate_allowance):
    for radius in RADII:
        lo, hi = max(BRACKET[0], delta-radius), min(BRACKET[1], delta+radius)
        left = mass_bounds(parent_state, lo, starts, ends, coordinate_allowance)
        right = mass_bounds(parent_state, hi, starts, ends, coordinate_allowance)
        if left[1] < observed-observed_allowance and right[0] > observed+observed_allowance:
            return (lo, hi), {'radius': radius, 'left_mass_bounds_kg': list(left),
                             'right_mass_bounds_kg': list(right),
                             'observed_mass_bounds_kg': [observed-observed_allowance, observed+observed_allowance]}
    raise ValueError('NUMERICAL_ENCLOSURE_UNRESOLVED')


@dataclass(frozen=True)
class OffsetCalibration(Serialized):
    parent: md.Model
    source_sha256: str
    calibrator: int
    record_sha256: str
    delta: float | None
    enclosure: tuple[float, float] | None
    status: str
    certificate_json: str

    def __post_init__(self):
        if not isinstance(self.parent, md.Model) or self.parent.arm not in ('C0', 'C2'):
            raise ValueError('UNCHANGED_C0_OR_C2_PARENT_REQUIRED')
        sha_string(self.source_sha256); sha_string(self.record_sha256); shot_number(self.calibrator)
        cert = md.strict_json(self.certificate_json)
        if not isinstance(cert, dict):
            raise ValueError('NUMERICAL_CERTIFICATE_REQUIRED')
        object.__setattr__(self, 'certificate_json', md.canonical(cert))
        if self.status == 'QUALIFIED':
            delta = md.number(self.delta)
            if self.enclosure is None or len(self.enclosure) != 2:
                raise ValueError('ROOT_ENCLOSURE_REQUIRED')
            interval = tuple(md.number(x) for x in self.enclosure)
            if not BRACKET[0] <= interval[0] <= delta <= interval[1] <= BRACKET[1]:
                raise ValueError('ROOT_ENCLOSURE_OR_BRACKET_MISMATCH')
            object.__setattr__(self, 'delta', delta); object.__setattr__(self, 'enclosure', interval)
        elif self.delta is not None or self.enclosure is not None or self.status not in (
                'CALIBRATION_RANGE_FAILURE', 'NUMERICAL_ENCLOSURE_UNRESOLVED', 'CALIBRATION_SUPPORT_FAILURE', 'CALIBRATION_SOLVER_FAILURE'):
            raise ValueError('INVALID_CALIBRATION_FAILURE_ARTIFACT')

    @property
    def arm(self):
        return 'A'+self.parent.arm[1:]

    def to_dict(self):
        return {'version': VERSION, 'kind': 'SOURCE_OFFSET', 'arm': self.arm,
                'parent': self.parent.to_dict(), 'parent_sha256': self.parent.sha256,
                'source_sha256': self.source_sha256, 'calibrator': self.calibrator,
                'record_sha256': self.record_sha256, 'delta': self.delta,
                'enclosure': list(self.enclosure) if self.enclosure is not None else None,
                'status': self.status, 'certificate': md.strict_json(self.certificate_json),
                'units': dict(md.UNITS), 'settings': dict(ROOT_SETTINGS), 'claims': list(CLAIMS)}

    @classmethod
    def from_dict(cls, value, *, parent_sha256=None, calibrator=None, source_sha256=None):
        md.exact_keys(value, ('version', 'kind', 'arm', 'parent', 'parent_sha256', 'source_sha256',
                             'calibrator', 'record_sha256', 'delta', 'enclosure', 'status',
                             'certificate', 'units', 'settings', 'claims'))
        obj = cls(md.Model.from_dict(value['parent']), value['source_sha256'], value['calibrator'],
                  value['record_sha256'], value['delta'], value['enclosure'], value['status'], md.canonical(value['certificate']))
        if md.canonical(value) != md.canonical(obj.to_dict()):
            raise ValueError('CALIBRATION_IDENTITY_SCHEMA_OR_UNITS_MISMATCH')
        if ((parent_sha256 is not None and obj.parent.sha256 != parent_sha256)
                or (calibrator is not None and obj.calibrator != calibrator)
                or (source_sha256 is not None and obj.source_sha256 != source_sha256)):
            raise ValueError('WRONG_PARENT_SOURCE_OR_CALIBRATOR')
        return obj

    def condition(self, typed_early_input):
        return OffsetState(self, typed_early_input)


def calibrate_source(parent_model, calibration_record):
    if not isinstance(calibration_record, CalibrationRecord) or not isinstance(parent_model, md.Model):
        raise ValueError('TYPED_CALIBRATION_RECORD_AND_PARENT_REQUIRED')
    rec = calibration_record
    if rec.early is None or rec.early.arm != parent_model.arm:
        raise ValueError('CALIBRATION_ARM_INFORMATION_MISMATCH')
    base = (parent_model, rec.source_sha256, rec.shot, rec.sha256)
    try:
        if any(w.mass_kg > 0 and w.q is None for w in rec.windows):
            raise ValueError('CALIBRATION_SUPPORT_FAILURE')
        state = parent_model.condition(rec.early)
        used = [w for w in rec.windows if w.mass_kg > 0 and w.q is not None]
        if not used:
            raise ValueError('CALIBRATION_SUPPORT_FAILURE')
        xyz = [pooled.runtime_coordinates(asdict(w), state.b_anchor) for w in used]
        starts, ends = [x[0] for x in xyz], [x[1] for x in xyz]
        if any(a < state.b_anchor for a in starts):
            raise ValueError('CALIBRATION_SUPPORT_FAILURE')
        md.IntervalGeometry(starts, ends, parent_model.domain_kg)
        observed = math.fsum(w.mass_kg*w.q for w in used)
        oa = 128*np.finfo(float).eps*math.fsum(abs(w.mass_kg*w.q) for w in used)
        ca = math.fsum(x[2] for x in xyz)
        def objective(delta):
            return math.fsum(shifted_integrals(state, delta, starts, ends))-observed
        left, right = objective(BRACKET[0]), objective(BRACKET[1])
        if not left <= 0 <= right:
            raise ValueError('CALIBRATION_RANGE_FAILURE')
        delta, result = brentq(objective, *BRACKET, xtol=1e-12, rtol=4*np.finfo(float).eps,
                               maxiter=200, full_output=True)
        if not result.converged:
            raise ValueError('CALIBRATION_SOLVER_FAILURE')
        enclosure, cert = certify_enclosure(state, delta, starts, ends, observed, oa, ca)
        cert.update(root_calls=int(result.function_calls), coordinate_allowance_kg=ca,
                    observed_roundoff_kg=oa, observed_windows=len(used))
        return OffsetCalibration(*base, delta, enclosure, 'QUALIFIED', md.canonical(cert))
    except (ValueError, RuntimeError, FloatingPointError) as exc:
        named = str(exc)
        status = named if named in ('CALIBRATION_RANGE_FAILURE', 'NUMERICAL_ENCLOSURE_UNRESOLVED',
                                     'CALIBRATION_SUPPORT_FAILURE') else 'CALIBRATION_SOLVER_FAILURE'
        return OffsetCalibration(*base, None, None, status, md.canonical({'reason': named}))


@dataclass(frozen=True)
class OffsetState(Serialized):
    calibration: OffsetCalibration
    inputs: md.EarlyInput
    parent_state: md.State = field(init=False)

    def __post_init__(self):
        if not isinstance(self.calibration, OffsetCalibration) or not isinstance(self.inputs, md.EarlyInput):
            raise ValueError('IMMUTABLE_CALIBRATION_AND_TYPED_EARLY_INPUT_REQUIRED')
        if self.calibration.status != 'QUALIFIED':
            raise ValueError(self.calibration.status)
        object.__setattr__(self, 'parent_state', self.calibration.parent.condition(self.inputs))

    @property
    def b_anchor(self):
        return self.parent_state.b_anchor

    @property
    def feature_extrapolation(self):
        return self.parent_state.feature_extrapolation

    def to_dict(self):
        return {'version': VERSION, 'calibration': self.calibration.to_dict(),
                'calibration_sha256': self.calibration.sha256, 'inputs': self.inputs.to_dict(),
                'parent_state': self.parent_state.to_dict()}

    @classmethod
    def from_dict(cls, value, **expected):
        md.exact_keys(value, ('version', 'calibration', 'calibration_sha256', 'inputs', 'parent_state'))
        obj = cls(OffsetCalibration.from_dict(value['calibration'], **expected), md.EarlyInput.from_dict(value['inputs']))
        if md.canonical(value) != md.canonical(obj.to_dict()):
            raise ValueError('STATE_IDENTITY_OR_DERIVED_FIELD_MISMATCH')
        return obj

    def predict_intervals(self, starts_kg, ends_kg, *, mass_unit='kg', basis='MASS'):
        if (mass_unit, basis) != ('kg', 'MASS'):
            raise ValueError('KG_MASS_BASIS_REQUIRED')
        starts, ends = tuple(map(md.number, starts_kg)), tuple(map(md.number, ends_kg))
        if any(a < self.b_anchor for a in starts):
            raise ValueError('QUERY_BEFORE_FORECAST_ANCHOR')
        cal, parent = self.calibration, self.parent_state
        radius = max(cal.delta-cal.enclosure[0], cal.enclosure[1]-cal.delta)
        if cal.delta == 0:
            values = parent.predict_intervals(starts, ends)
            return tuple(md.Prediction(p.start_kg, p.end_kg, p.solute_kg, p.tds_percent,
                                      p.allowance_kg+(p.end_kg-p.start_kg)*radius/4,
                                      p.allowance_kg+(p.end_kg-p.start_kg)*radius/4 <= 1e-9) for p in values)
        solutes = shifted_integrals(parent, cal.delta, starts, ends)
        logits = np.asarray(parent.logits)+cal.delta
        out = []
        for a, b, solute in zip(starts, ends, solutes):
            allowance = md.numerical_allowance(a, b, parent.model.domain_kg, logits, solute)+(b-a)*radius/4
            out.append(qualified_prediction(a, b, float(solute), allowance))
        return tuple(out)

    def remaining_solute(self, stop_mass_kg, **kwargs):
        return self.predict_intervals([self.b_anchor], [stop_mass_kg], **kwargs)[0]


def qualified_prediction(a, b, solute, allowance):
    if not all(math.isfinite(x) for x in (a, b, solute, allowance)) or allowance < 0:
        raise ValueError('NONFINITE_OR_NEGATIVE_ALLOWANCE')
    if solute < -allowance or solute > b-a+allowance:
        raise ValueError('SOLUTE_CONSERVATION_BOUND_FAILURE')
    return md.Prediction(a, b, solute, 100*solute/(b-a) if b > a else None,
                         allowance, allowance <= 1e-9)


def gram_rows(starts, ends):
    """Explicit SI conversion; time is absent and its coefficient is exactly zero."""
    return [{'shot': 1, 'vial': k+1, 'mass_g': 1000*(b-a), 'b_start_g': 1000*a,
             't_start_s': 0., 't_end_s': 0.} for k, (a, b) in enumerate(zip(starts, ends))]


@dataclass(frozen=True)
class MassCalibration(Serialized):
    source_sha256: str
    calibrator: int
    record_sha256: str
    theta: tuple[float, ...] | None
    domain_kg: float
    calibration_range_kg: tuple[float, float]
    status: str

    def __post_init__(self):
        sha_string(self.source_sha256); sha_string(self.record_sha256); shot_number(self.calibrator)
        object.__setattr__(self, 'domain_kg', md.number(self.domain_kg))
        rg = tuple(map(md.number, self.calibration_range_kg))
        if len(rg) != 2 or not 0 <= rg[0] <= rg[1] <= self.domain_kg:
            raise ValueError('CALIBRATION_MASS_RANGE_REQUIRED')
        object.__setattr__(self, 'calibration_range_kg', rg)
        if self.status == 'QUALIFIED':
            if self.theta is None:
                raise ValueError('MASS_PARAMETERS_REQUIRED')
            t = tuple(map(md.number, self.theta))
            if len(t) != 4 or not (0 <= t[0] <= 1 and t[1] == 0 and 0 <= t[2] <= 10 and .25 <= t[3] <= 4):
                raise ValueError('MASS_BOUNDS_OR_ABSENT_TIME_RATE')
            object.__setattr__(self, 'theta', t)
        elif self.theta is not None or self.status not in ('ALL_STARTS_FAILED', 'CALIBRATION_SUPPORT_FAILURE'):
            raise ValueError('INVALID_MASS_FAILURE_ARTIFACT')

    def to_dict(self):
        return {'version': VERSION, 'kind': 'SOURCE_ONLY_MASS', 'source_sha256': self.source_sha256,
                'calibrator': self.calibrator, 'record_sha256': self.record_sha256,
                'theta': list(self.theta) if self.theta is not None else None,
                'domain_kg': self.domain_kg, 'calibration_range_kg': list(self.calibration_range_kg),
                'status': self.status, 'units': dict(md.UNITS), 'claims': list(CLAIMS),
                'parameter_units': ['kg/kg', '1/s (exactly zero)', '1/g', '1']}

    @classmethod
    def from_dict(cls, value, *, calibrator=None, source_sha256=None):
        md.exact_keys(value, ('version', 'kind', 'source_sha256', 'calibrator', 'record_sha256',
                             'theta', 'domain_kg', 'calibration_range_kg', 'status', 'units', 'claims', 'parameter_units'))
        obj = cls(*(value[k] for k in ('source_sha256', 'calibrator', 'record_sha256', 'theta',
                                     'domain_kg', 'calibration_range_kg', 'status')))
        if md.canonical(value) != md.canonical(obj.to_dict()):
            raise ValueError('MASS_SCHEMA_IDENTITY_OR_UNITS_MISMATCH')
        if ((calibrator is not None and obj.calibrator != calibrator)
                or (source_sha256 is not None and obj.source_sha256 != source_sha256)):
            raise ValueError('WRONG_SOURCE_OR_CALIBRATOR')
        return obj

    def condition(self, typed_early_input):
        return MassState(self, typed_early_input)


@dataclass(frozen=True)
class MassState(Serialized):
    calibration: MassCalibration
    inputs: md.EarlyInput

    def __post_init__(self):
        if (not isinstance(self.calibration, MassCalibration) or not isinstance(self.inputs, md.EarlyInput)
                or self.inputs.arm != 'C0'):
            raise ValueError('MASS_ONLY_TYPED_TARGET_INPUT_REQUIRED')
        if self.calibration.status != 'QUALIFIED':
            raise ValueError(self.calibration.status)
        if self.b_anchor > self.calibration.domain_kg:
            raise ValueError('ANCHOR_OUTSIDE_MASS_DOMAIN')

    @property
    def b_anchor(self):
        return sum(self.inputs.values)

    @property
    def feature_extrapolation(self):
        return ()

    def to_dict(self):
        return {'version': VERSION, 'calibration': self.calibration.to_dict(),
                'calibration_sha256': self.calibration.sha256, 'inputs': self.inputs.to_dict(),
                'b_anchor': self.b_anchor}

    @classmethod
    def from_dict(cls, value, **expected):
        md.exact_keys(value, ('version', 'calibration', 'calibration_sha256', 'inputs', 'b_anchor'))
        obj = cls(MassCalibration.from_dict(value['calibration'], **expected), md.EarlyInput.from_dict(value['inputs']))
        if md.canonical(value) != md.canonical(obj.to_dict()):
            raise ValueError('STATE_IDENTITY_OR_DERIVED_FIELD_MISMATCH')
        return obj

    def predict_intervals(self, starts_kg, ends_kg, *, mass_unit='kg', basis='MASS'):
        if (mass_unit, basis) != ('kg', 'MASS'):
            raise ValueError('KG_MASS_BASIS_REQUIRED')
        starts, ends = tuple(map(md.number, starts_kg)), tuple(map(md.number, ends_kg))
        md.IntervalGeometry(starts, ends, self.calibration.domain_kg)
        if any(a < self.b_anchor for a in starts):
            raise ValueError('QUERY_BEFORE_FORECAST_ANCHOR')
        rows = gram_rows(starts, ends); theta = self.calibration.theta
        values = gc.deliver(rows, theta)/1000
        refined = gc.deliver(rows, theta, order=256)/1000
        out = []
        for a, b, row, value, fine in zip(starts, ends, rows, values, refined):
            reference, error = gc.independent_delivery(row, theta)
            # Bound endpoints after both multiplications/divisions; q <= 1.
            conversion = 2*(math.ulp(1000*a)+math.ulp(1000*(b-a)))/1000
            allowance = (max(abs(value-fine), abs(value-reference/1000), abs(fine-reference/1000))
                         + error/1000 + conversion + 128*np.finfo(float).eps*((b-a)+abs(value))) if b > a else 0.
            out.append(qualified_prediction(a, b, float(value), float(allowance)))
        return tuple(out)

    def remaining_solute(self, stop_mass_kg, **kwargs):
        return self.predict_intervals([self.b_anchor], [stop_mass_kg], **kwargs)[0]


def condition(calibration_artifact, typed_early_input):
    if not isinstance(calibration_artifact, (OffsetCalibration, MassCalibration)):
        raise ValueError('FROZEN_CALIBRATION_ARTIFACT_REQUIRED')
    return calibration_artifact.condition(typed_early_input)


def predict_intervals(state, starts_kg, ends_kg, **kwargs):
    if not isinstance(state, (OffsetState, MassState)):
        raise ValueError('IMMUTABLE_TYPED_STATE_REQUIRED')
    return state.predict_intervals(starts_kg, ends_kg, **kwargs)


def remaining_solute(state, stop_mass_kg, **kwargs):
    return predict_intervals(state, [state.b_anchor], [stop_mass_kg], **kwargs)[0]

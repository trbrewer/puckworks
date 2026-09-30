"""Finite-assay-set delivery extrema over unchanged conditional-tail models.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. Exact-arithmetic bounds
and floating-point qualification are distinguished in the task README.
Source-derived model/output rights remain separate from first-party software.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, fields
from itertools import product
import math
from numbers import Real
import os
from pathlib import Path
from typing import Callable
import warnings

import numpy as np
from scipy.integrate import IntegrationWarning, quad
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as forward

VERSION = 'conditional-tail-envelope/1'
ABSOLUTE_GAP_KG = 1e-7
MAX_SUBDIVISIONS = 4096
MAX_POINT_EVALUATIONS = 16384
_EPS = float(np.finfo(float).eps)
Ranges = tuple[tuple[float, float], ...]


def _number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError('FINITE_REAL_NUMBER_REQUIRED')
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError('FINITE_REAL_NUMBER_REQUIRED') from exc
    if not math.isfinite(result):
        raise ValueError('FINITE_REAL_NUMBER_REQUIRED')
    return result


@dataclass(frozen=True, init=False)
class AssayBox:
    """Exact masses and only the arm's active named, closed assay intervals."""

    arm: str
    m1_kg: float
    m2_kg: float
    bounds: Ranges
    input_class: str
    mass_unit: str
    concentration_unit: str
    basis: str

    def __init__(self, arm: str, m1_kg: float, m2_kg: float, *,
                 input_class: str = 'SUPPLIED_EARLY_ASSAYS', mass_unit: str = 'kg',
                 concentration_unit: str = 'kg/kg', basis: str = 'MASS',
                 **assays: tuple[float, float]) -> None:
        names = forward.feature_names(arm)[2:]
        forward.exact_keys(assays, names)
        bounds = []
        for name in names:
            pair = assays[name]
            if not isinstance(pair, (tuple, list)) or len(pair) != 2:
                raise ValueError('CLOSED_ASSAY_INTERVAL_REQUIRED')
            lo, hi = map(_number, pair)
            if not 0 <= lo <= hi <= 1:
                raise ValueError('ORDERED_ASSAY_INTERVAL_WITHIN_ZERO_ONE_REQUIRED')
            bounds.append((lo, hi))
        m1, m2 = _number(m1_kg), _number(m2_kg)
        # Authoritative input object enforces the unchanged arm/units/role contract.
        forward.EarlyInput(arm, (m1, m2, *(lo for lo, _ in bounds)), input_class,
                           mass_unit, concentration_unit, basis)
        if not math.isfinite(m1 + m2):
            raise ValueError('FINITE_ANCHOR_REQUIRED')
        for key, value in dict(arm=arm, m1_kg=m1, m2_kg=m2, bounds=tuple(bounds),
                               input_class=input_class, mass_unit=mass_unit,
                               concentration_unit=concentration_unit, basis=basis).items():
            object.__setattr__(self, key, value)

    @property
    def anchor_kg(self) -> float:
        return self.m1_kg + self.m2_kg

    def inputs(self, assays: tuple[float, ...]) -> forward.EarlyInput:
        if len(assays) != len(self.bounds) or any(
                not lo <= q <= hi for q, (lo, hi) in zip(assays, self.bounds)):
            raise ValueError('WITNESS_OUTSIDE_ASSAY_BOX')
        return forward.EarlyInput(self.arm, (self.m1_kg, self.m2_kg, *assays),
                                  self.input_class, self.mass_unit,
                                  self.concentration_unit, self.basis)

    def to_dict(self) -> dict:
        result = asdict(self)
        del result['bounds']
        result.update(zip(forward.feature_names(self.arm)[2:], self.bounds))
        return forward.strict_json(forward.canonical(result))

    @classmethod
    def from_dict(cls, data: dict) -> AssayBox:
        if not isinstance(data, dict) or 'arm' not in data:
            raise ValueError('STRICT_BOX_FIELDS_REQUIRED')
        forward.exact_keys(data, ('arm', 'm1_kg', 'm2_kg', 'input_class', 'mass_unit',
                                 'concentration_unit', 'basis',
                                 *forward.feature_names(data['arm'])[2:]))
        return cls(**data)


@dataclass(frozen=True)
class EnvelopeQuery:
    start_kg: float
    end_kg: float
    absolute_gap_kg: float = ABSOLUTE_GAP_KG
    max_subdivisions: int = MAX_SUBDIVISIONS
    max_point_evaluations: int = MAX_POINT_EVALUATIONS
    mass_unit: str = 'kg'
    basis: str = 'MASS'

    def __post_init__(self) -> None:
        for key in ('start_kg', 'end_kg', 'absolute_gap_kg'):
            object.__setattr__(self, key, _number(getattr(self, key)))
        if not 0 <= self.start_kg <= self.end_kg:
            raise ValueError('ORDERED_NONNEGATIVE_QUERY_REQUIRED')
        if not 0 < self.absolute_gap_kg <= ABSOLUTE_GAP_KG:
            raise ValueError('POSITIVE_GAP_AT_MOST_DEFAULT_REQUIRED')
        for value, limit in ((self.max_subdivisions, MAX_SUBDIVISIONS),
                             (self.max_point_evaluations, MAX_POINT_EVALUATIONS)):
            if type(value) is not int or not 0 <= value <= limit:
                raise ValueError('INTEGER_RESOURCE_LIMIT_WITHIN_HARD_CAP_REQUIRED')
        if (self.mass_unit, self.basis) != ('kg', 'MASS'):
            raise ValueError('UNSUPPORTED_UNITS_OR_BASIS')

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> EnvelopeQuery:
        forward.exact_keys(data, (f.name for f in fields(cls)))
        return cls(**data)


@dataclass(frozen=True)
class Witness:
    inputs: forward.EarlyInput
    prediction: forward.Prediction
    state_sha256: str

    def to_dict(self) -> dict:
        return asdict(self) | {'inputs': self.inputs.to_dict()}


@dataclass(frozen=True)
class ExtremumBounds:
    lower_kg: float
    upper_kg: float
    gap_kg: float
    witness: Witness | None
    tds_percent_bounds: tuple[float, float] | None


@dataclass(frozen=True)
class NumericalAllowances:
    maximum_parent_kg: float | None
    maximum_envelope_integration_kg: float
    maximum_arithmetic_kg: float
    maximum_gradient_effect_kg: float


@dataclass(frozen=True)
class Resources:
    parent_point_evaluations: int
    failed_parent_evaluations: int
    bound_evaluations: int
    failed_bound_evaluations: int
    subdivisions: int
    retained_partition_boxes: int
    adaptive_quadrature_calls: int


@dataclass(frozen=True)
class DeliveryEnvelope:
    status: str
    termination_reason: str
    minimum: ExtremumBounds
    maximum: ExtremumBounds
    delivery_outer_kg: tuple[float, float]
    tds_outer_percent: tuple[float, float] | None
    numerical_allowances: NumericalAllowances
    resources: Resources
    box: AssayBox
    query: EnvelopeQuery
    model_sha256: str
    box_sha256: str
    query_sha256: str
    model_domain_kg: float
    model_training_identity_json: str
    feature_extrapolation: tuple[str, ...]
    rights: str
    claims: tuple[str, ...]
    version: str = VERSION
    physical_validation: str = 'NOT_ESTABLISHED'
    numerical_qualification: str = 'ALLOWANCE_BASED_NOT_INTERVAL_CERTIFIED'

    def to_dict(self) -> dict:
        result = asdict(self) | {'box': self.box.to_dict(), 'units': dict(forward.UNITS)}
        for name in ('minimum', 'maximum'):
            witness = getattr(self, name).witness
            result[name]['witness'] = witness.to_dict() if witness else None
        return forward.strict_json(forward.canonical(result))

    def to_json(self) -> str:
        return forward.canonical(self.to_dict()) + '\n'


@dataclass(frozen=True)
class _Node:
    bounds: Ranges
    lower: float
    upper: float
    order: int


class _Stop(Exception):
    """Sanitized numerical/resource reason, never input content."""


def _center(bounds: Ranges) -> tuple[float, ...]:
    return tuple(lo + (hi - lo) / 2 for lo, hi in bounds)


def _down(value: float) -> float:
    return math.nextafter(value, -math.inf)


def _up(value: float) -> float:
    return math.nextafter(value, math.inf)


class _Engine:
    def __init__(self, model: forward.Model, box: AssayBox, query: EnvelopeQuery) -> None:
        self.model, self.box, self.query = model, box, query
        self.width = query.end_kg - query.start_kg
        self.cache: dict[tuple[float, ...], tuple[forward.State, Witness]] = {}
        self.points = self.failed_points = self.bounds = self.failed_bounds = 0
        self.splits = self.quads = 0
        self.parent_allowance: float | None = None
        self.integration_allowance = self.arithmetic_allowance = self.gradient_allowance = 0.
        self.leaves = [_Node(box.bounds, 0., self.width, 0)]
        self.beta = tuple(tuple(row[j + 3] / forward.SCALES[j + 2]
                               for row in model.theta) for j in range(len(box.bounds)))
        self.beta_max = tuple(max(map(abs, column)) for column in self.beta)

    def observe(self, assays: tuple[float, ...]) -> tuple[forward.State, Witness]:
        if assays in self.cache:
            return self.cache[assays]
        if self.points >= self.query.max_point_evaluations:
            raise _Stop('PARENT_POINT_EVALUATION_LIMIT')
        self.points += 1
        try:
            with warnings.catch_warnings(), np.errstate(over='raise', invalid='raise'):
                warnings.simplefilter('error', IntegrationWarning)
                state = self.model.condition(self.box.inputs(assays))
                p = state.predict_intervals((self.query.start_kg,), (self.query.end_kg,))[0]
            if math.isfinite(p.allowance_kg):
                self.parent_allowance = max(self.parent_allowance or 0., p.allowance_kg)
            if (not p.numerical_qualified or not math.isfinite(p.allowance_kg)
                    or not 0 <= p.allowance_kg <= forward.SETTINGS['max_solute_allowance_kg']
                    or not math.isfinite(p.solute_kg) or not 0 <= p.solute_kg <= self.width
                    or (p.start_kg, p.end_kg) != (self.query.start_kg, self.query.end_kg)
                    or (self.width > 0 and (p.tds_percent is None
                        or not math.isfinite(p.tds_percent) or not 0 <= p.tds_percent <= 100))
                    or (self.width == 0 and p.tds_percent is not None)):
                raise _Stop('PARENT_POINT_NOT_NUMERICALLY_QUALIFIED')
        except (ArithmeticError, ValueError, IntegrationWarning) as exc:
            self.failed_points += 1
            raise _Stop('PARENT_POINT_NUMERICAL_FAILURE') from exc
        except _Stop:
            self.failed_points += 1
            raise
        witness = Witness(state.inputs, p, forward.identity(state.to_dict()))
        self.cache[assays] = state, witness
        return state, witness

    def reference(self, fun: Callable[[float], float]) -> tuple[float, float]:
        """Independent adaptive integration, then bisection/refinement, on [0,1]."""
        totals, errors = [], []
        for cuts in ((0., 1.), (0., .5, 1.)):
            values, errs = [], []
            for lo, hi in zip(cuts, cuts[1:]):
                self.quads += 1
                value, error = quad(fun, lo, hi, epsabs=1e-14, epsrel=2e-13, limit=200)
                if not math.isfinite(value) or not math.isfinite(error) or error < 0:
                    raise ValueError('NONFINITE_QUADRATURE')
                values.append(value)
                errs.append(error)
            totals.append(math.fsum(values))
            errors.append(math.fsum(errs))
        return totals[1], abs(totals[0] - totals[1]) + sum(errors)

    def node(self, bounds: Ranges, order: int, inherited: _Node) -> _Node:
        center = _center(bounds)
        state, witness = self.observe(center)
        self.bounds += 1
        try:
            with warnings.catch_warnings(), np.errstate(over='raise', invalid='raise'):
                warnings.simplefilter('error', IntegrationWarning)
                result = self._node(bounds, order, inherited, state, witness)
            if not 0 <= result.lower <= result.upper <= self.width:
                raise ValueError('INCONSISTENT_NODE_BOUND')
            p = witness.prediction
            if result.lower > p.solute_kg + p.allowance_kg or result.upper < p.solute_kg - p.allowance_kg:
                raise ValueError('BOUND_WITNESS_DISAGREEMENT')
            return result
        except (ArithmeticError, ValueError, IntegrationWarning) as exc:
            self.failed_bounds += 1
            raise _Stop('ENVELOPE_NUMERICAL_FAILURE') from exc

    def _node(self, bounds: Ranges, order: int, inherited: _Node,
              state: forward.State, witness: Witness) -> _Node:
        # This derives assay dependence only; all point predictions use the parent.
        center = state.inputs.values[2:]
        radii = tuple(max(c - lo, hi - c) for c, (lo, hi) in zip(center, bounds))
        knots = forward.IntervalGeometry((self.query.start_kg,), (self.query.end_kg,),
                                         self.model.domain_kg).knots
        if any(r <= l for l, r in zip(knots, knots[1:])):
            raise ValueError('DEGENERATE_KNOT_GEOMETRY')
        input_bounds = ((self.box.m1_kg,) * 2, (self.box.m2_kg,) * 2, *bounds)
        size = max(abs(row[0]) + math.fsum(abs(t) * (max(abs(lo), abs(hi)) + abs(mu)) / scale
                   for t, (lo, hi), mu, scale in zip(row[1:], input_bounds,
                                                    self.model.means, forward.SCALES))
                   for row in self.model.theta)
        arithmetic = 512 * _EPS * (abs(self.query.start_kg) + abs(self.query.end_kg)
                                    + self.width * (1 + size))
        lower_parts: list[float] = []
        upper_parts: list[float] = []
        integration_errors: list[float] = []
        gradients: list[list[float]] = [[] for _ in bounds]
        gradient_errors: list[list[float]] = [[] for _ in bounds]
        for k, (left, right) in enumerate(zip(knots, knots[1:])):
            start, end = max(float(left), self.query.start_kg), min(float(right), self.query.end_kg)
            if start >= end:
                continue
            cuts = [start, end]
            for column in self.beta:
                a, b = column[k], column[k + 1]
                if (a < 0 < b) or (b < 0 < a):
                    crossing = float(left + (right - left) * (a / (a - b)))
                    if start < crossing < end:
                        cuts.append(crossing)
            cuts = sorted(set(cuts))

            def affine(mass: float) -> tuple[float, tuple[float, ...]]:
                t = (mass - left) / (right - left)
                eta = (1 - t) * state.logits[k] + t * state.logits[k + 1]
                beta = tuple((1 - t) * col[k] + t * col[k + 1] for col in self.beta)
                return float(eta), beta

            def extremes(mass: float) -> tuple[float, float]:
                eta, beta = affine(mass)
                terms = [(b * (lo - c), b * (hi - c))
                         for b, (lo, hi), c in zip(beta, bounds, center)]
                return (eta + math.fsum(min(pair) for pair in terms),
                        eta + math.fsum(max(pair) for pair in terms))

            for a, b in zip(cuts, cuts[1:]):
                width = b - a
                endpoints = tuple(zip(extremes(a), extremes(b)))
                # Chords remain outer logit bounds even at a rounded sign crossing.
                for side, (lo, hi) in enumerate(endpoints):
                    value = width * float(forward.segment_average(lo, hi))
                    reference, error = self.reference(
                        lambda t: width * float(expit(extremes(a + width * t)[side])))
                    integration_errors.append(abs(value - reference) + error)
                    (lower_parts if side == 0 else upper_parts).append(value)
                for j in range(len(bounds)):
                    def derivative(t: float) -> float:
                        eta, beta = affine(a + width * t)
                        concentration = float(expit(eta))
                        return width * concentration * (1 - concentration) * beta[j]
                    value, error = self.reference(derivative)
                    gradients[j].append(value)
                    gradient_errors[j].append(error)
        integration_error = math.fsum(integration_errors)
        gradient_error = math.fsum(r * (math.fsum(errors) +
            512 * _EPS * self.width * beta * (1 + size))
            for r, errors, beta in zip(radii, gradient_errors, self.beta_max))
        linear_radius = math.fsum(abs(math.fsum(g)) * r for g, r in zip(gradients, radii))
        logit_radius = math.fsum(b * r for b, r in zip(self.beta_max, radii))
        remainder = self.width * logit_radius**2 / 8
        taylor_radius = (linear_radius + remainder + gradient_error + arithmetic
                         + 512 * _EPS * (linear_radius + remainder))
        p = witness.prediction
        numbers = (arithmetic, integration_error, gradient_error, taylor_radius)
        if not all(math.isfinite(v) and v >= 0 for v in numbers):
            raise ValueError('ARITHMETIC_ALLOWANCE_OVERFLOW')
        self.integration_allowance = max(self.integration_allowance, integration_error)
        self.arithmetic_allowance = max(self.arithmetic_allowance,
                                        arithmetic + 512 * _EPS * (linear_radius + remainder))
        self.gradient_allowance = max(self.gradient_allowance, gradient_error)
        lower = max(inherited.lower, 0.,
                    _down(math.fsum(lower_parts) - integration_error - arithmetic),
                    _down(p.solute_kg - p.allowance_kg - taylor_radius))
        upper = min(inherited.upper, self.width,
                    _up(math.fsum(upper_parts) + integration_error + arithmetic),
                    _up(p.solute_kg + p.allowance_kg + taylor_radius))
        return _Node(bounds, lower, upper, order)

    def extrema(self) -> tuple[float, float, float, float, Witness | None, Witness | None]:
        witnesses = [w for _, w in self.cache.values()]
        low = min(witnesses, key=lambda w: w.prediction.solute_kg + w.prediction.allowance_kg,
                  default=None)
        high = max(witnesses, key=lambda w: w.prediction.solute_kg - w.prediction.allowance_kg,
                   default=None)
        lo = min(n.lower for n in self.leaves)
        hi = max(n.upper for n in self.leaves)
        min_upper = min(self.width, _up(low.prediction.solute_kg + low.prediction.allowance_kg)) if low else self.width
        max_lower = max(0., _down(high.prediction.solute_kg - high.prediction.allowance_kg)) if high else 0.
        return lo, min_upper, max_lower, hi, low, high

    def run(self) -> str:
        if self.width == 0 or all(lo == hi for lo, hi in self.box.bounds):
            _, w = self.observe(_center(self.box.bounds))
            p = w.prediction
            self.leaves = [_Node(self.box.bounds, max(0., _down(p.solute_kg - p.allowance_kg)),
                                min(self.width, _up(p.solute_kg + p.allowance_kg)), 0)]
            lo, mu, ml, hi, _, _ = self.extrema()
            return ('BOTH_EXTREMA_WITHIN_REQUESTED_GAP' if
                    max(_up(mu - lo), _up(hi - ml)) <= self.query.absolute_gap_kg else
                    'PARENT_ALLOWANCE_RESOLUTION_LIMIT')
        self.leaves = [self.node(self.box.bounds, 0, self.leaves[0])]
        for corner in product(*self.box.bounds):
            self.observe(tuple(corner))
        while True:
            lo, min_upper, max_lower, hi, _, _ = self.extrema()
            if min_upper < lo or max_lower > hi:
                self.failed_bounds += 1
                raise _Stop('GLOBAL_BOUND_WITNESS_DISAGREEMENT')
            if max(_up(min_upper - lo), _up(hi - max_lower)) <= self.query.absolute_gap_kg:
                return 'BOTH_EXTREMA_WITHIN_REQUESTED_GAP'
            if self.splits >= self.query.max_subdivisions:
                return 'SUBDIVISION_LIMIT'
            # Keep every leaf. Resolve the greatest remaining contribution to either gap.
            node = max(self.leaves, key=lambda n: (max(min_upper - n.lower,
                                                       n.upper - max_lower), -n.order))
            choices = [(self.beta_max[j] * (b - a), -j, j, a + (b - a) / 2)
                       for j, (a, b) in enumerate(node.bounds)
                       if a < a + (b - a) / 2 < b and self.beta_max[j] > 0]
            if not choices:
                return 'NO_REPRESENTABLE_OR_INFLUENTIAL_ASSAY_SPLIT'
            _, _, j, middle = max(choices)
            left, right = list(node.bounds), list(node.bounds)
            left[j] = (node.bounds[j][0], middle)
            right[j] = (middle, node.bounds[j][1])
            self.splits += 1  # Count attempted splits, including a failure in either child.
            children = [self.node(tuple(left), 2 * self.splits - 1, node),
                        self.node(tuple(right), 2 * self.splits, node)]
            # Atomic partition replacement: failure above leaves the whole parent retained.
            self.leaves.remove(node)
            self.leaves.extend(children)

    def result(self, reason: str) -> DeliveryEnvelope:
        if self.failed_points or self.failed_bounds:
            # On a load-bearing numerical failure only the universal enclosure is asserted.
            self.leaves = [_Node(n.bounds, 0., self.width, n.order) for n in self.leaves]
        lo, mu, ml, hi, low, high = self.extrema()
        if self.width == 0:
            lo = mu = ml = hi = 0.

        def tds(a: float, b: float) -> tuple[float, float] | None:
            if not self.width:
                return None
            return (max(0., _down(_down(a / self.width) * 100)),
                    min(100., _up(_up(b / self.width) * 100)))

        def bound(a: float, b: float, w: Witness | None) -> ExtremumBounds:
            gap = min(self.width, _up(b - a)) if b > a else 0.
            return ExtremumBounds(a, b, gap, w, tds(a, b))

        inputs = ((self.box.m1_kg,) * 2, (self.box.m2_kg,) * 2, *self.box.bounds)
        extrapolation = tuple(n for n, (a, b), l, h in zip(forward.feature_names(self.model.arm),
                              inputs, self.model.minima, self.model.maxima) if a < l or b > h)
        qualified = reason == 'BOTH_EXTREMA_WITHIN_REQUESTED_GAP'
        return DeliveryEnvelope(
            'ENVELOPE_QUALIFIED' if qualified else 'NUMERICALLY_UNRESOLVED', reason,
            bound(lo, mu, low), bound(ml, hi, high), (lo, hi), tds(lo, hi),
            NumericalAllowances(self.parent_allowance, self.integration_allowance,
                                self.arithmetic_allowance, self.gradient_allowance),
            Resources(self.points, self.failed_points, self.bounds, self.failed_bounds,
                      self.splits, len(self.leaves), self.quads), self.box, self.query,
            self.model.sha256, forward.identity(self.box.to_dict()), forward.identity(self.query.to_dict()),
            self.model.domain_kg, self.model.training_identity_json, extrapolation,
            self.model.rights, forward.CLAIMS + (
                'CONDITIONAL_ON_THE_UNCHANGED_MODEL_AND_CALLER_SUPPLIED_ASSAY_SET',
                'DETERMINISTIC_SET_NOT_PROBABILITY_MODEL', 'MARGINAL_RANGES_NOT_JOINT_SUPPORT',
                'SEPARATE_QUERY_EXTREMA_NOT_JOINTLY_ATTAINABLE'))


def bound_interval_delivery(model: forward.Model, box: AssayBox,
                            query: EnvelopeQuery) -> DeliveryEnvelope:
    if not isinstance(model, forward.Model) or not isinstance(box, AssayBox) or not isinstance(query, EnvelopeQuery):
        raise TypeError('TYPED_MODEL_BOX_AND_QUERY_REQUIRED')
    if model.arm != box.arm:
        raise ValueError('ARM_INFORMATION_CONTRACT_MISMATCH')
    if not box.anchor_kg <= query.start_kg <= query.end_kg <= model.domain_kg:
        raise ValueError('QUERY_OUTSIDE_FUTURE_MODEL_DOMAIN')
    engine = _Engine(model, box, query)
    try:
        reason = engine.run()
    except _Stop as stop:
        reason = str(stop)
    return engine.result(reason)


def bound_remaining_solute(model: forward.Model, box: AssayBox, stop_mass_kg: float,
                           **query_options) -> DeliveryEnvelope:
    if not isinstance(box, AssayBox):
        raise TypeError('TYPED_ASSAY_BOX_REQUIRED')
    return bound_interval_delivery(model, box, EnvelopeQuery(box.anchor_kg, stop_mass_kg,
                                                           **query_options))


def _outside_git(path: Path) -> bool:
    resolved = path.resolve()
    return not any((p / '.git').exists() for p in (resolved, *resolved.parents))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--synthetic', action='store_true')
    mode.add_argument('--model', type=Path)
    parser.add_argument('--box', type=Path)
    parser.add_argument('--query', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.synthetic:
        if args.box or args.query or args.output:
            parser.error('--synthetic is a source-free stdout demonstration')
        model = forward.synthetic_model()
        box = AssayBox('C2', .004, .004, q1=(.14, .16), q2=(.09, .11), input_class='SYNTHETIC')
        query = EnvelopeQuery(.008, .04)
    else:
        if not args.box or not args.query or not args.output:
            parser.error('--model requires --box, --query and exclusive --output')
        try:
            if not all(_outside_git(p) for p in (args.box, args.query, args.output)):
                parser.error('supplied boxes, queries and results must remain outside Git')
            model = forward.Model.load(args.model)
            box = AssayBox.from_dict(forward.strict_json(args.box.read_text()))
            query = EnvelopeQuery.from_dict(forward.strict_json(args.query.read_text()))
        except (OSError, ArithmeticError, ValueError, TypeError, KeyError, IndexError, RuntimeError):
            parser.error('invalid saved model, box or query; input contents are not printed')
    try:
        result = bound_interval_delivery(model, box, query)
        if args.output:
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as stream:
                stream.write(result.to_json())
        else:
            print(result.to_json(), end='')
    except (OSError, ValueError, TypeError):
        parser.error('invalid query or unavailable exclusive output; no input contents printed')


if __name__ == '__main__':
    main()

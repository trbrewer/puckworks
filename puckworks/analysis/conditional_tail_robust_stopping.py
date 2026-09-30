"""Continuous assay-robust suffix stopping enclosures, conditional on a fixed model.

G0 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY. The task README separates
the exact-arithmetic enclosure argument from allowance-based qualification.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field, fields
from fractions import Fraction
import heapq
from itertools import product
import math
from numbers import Real
import os
from pathlib import Path
from typing import Callable
import warnings

from scipy.integrate import IntegrationWarning
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as forward
from puckworks.analysis import conditional_tail_envelope as envelope
from puckworks.analysis import conditional_tail_stopping as stopping

VERSION = 'conditional-tail-robust-stopping/1'
_EPS = 2.220446049250313e-16
_LIMITS = ('solute_min_kg', 'solute_max_kg',
           'suffix_tds_min_percent', 'suffix_tds_max_percent')


@dataclass(frozen=True)
class RobustStoppingOptions:
    mass_resolution_kg: float = 1e-6
    envelope_absolute_gap_kg: float = 1e-7
    tighter_envelope_absolute_gap_kg: float = 1e-9
    max_mass_subdivisions: int = 2048
    max_envelope_calls: int = 512
    max_parent_evaluations: int = 65536
    max_assay_subdivisions_per_call: int = 4096
    max_parent_evaluations_per_envelope: int = 16384

    def __post_init__(self) -> None:
        for name in ('mass_resolution_kg', 'envelope_absolute_gap_kg',
                     'tighter_envelope_absolute_gap_kg'):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError('FINITE_POSITIVE_RESOLUTION_REQUIRED')
            try:
                value = float(value)
            except OverflowError as exc:
                raise ValueError('FINITE_POSITIVE_RESOLUTION_REQUIRED') from exc
            if not math.isfinite(value) or value <= 0:
                raise ValueError('FINITE_POSITIVE_RESOLUTION_REQUIRED')
            object.__setattr__(self, name, value)
        if not self.tighter_envelope_absolute_gap_kg <= self.envelope_absolute_gap_kg <= 1e-7:
            raise ValueError('ORDERED_ENVELOPE_GAPS_AT_MOST_PARENT_DEFAULT_REQUIRED')
        for name, cap in (('max_mass_subdivisions', 2048), ('max_envelope_calls', 512),
                          ('max_parent_evaluations', 65536),
                          ('max_assay_subdivisions_per_call', 4096),
                          ('max_parent_evaluations_per_envelope', 16384)):
            value = getattr(self, name)
            if type(value) is not int or not 0 <= value <= cap:
                raise ValueError('INTEGER_RESOURCE_LIMIT_WITHIN_HARD_CAP_REQUIRED')

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> RobustStoppingOptions:
        forward.exact_keys(data, (f.name for f in fields(cls)))
        return cls(**data)


@dataclass(frozen=True)
class MassRegion:
    lower_kg: float
    upper_kg: float
    lower_included: bool = True
    upper_included: bool = True
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResourceUse:
    mass_subdivisions: int
    point_inverse_mass_refinements_reserved: int
    envelope_calls: int
    tighter_envelope_calls: int
    parent_delivery_evaluations: int
    failed_parent_evaluations: int
    failed_envelope_calls: int
    assay_subdivisions: int
    envelope_bound_evaluations: int
    envelope_adaptive_quadrature_calls: int
    nested_accounting_complete: bool
    point_inverse_calls: int
    retained_mass_cells: int


@dataclass(frozen=True)
class Allowances:
    maximum_parent_kg: float
    maximum_envelope_integration_kg: float
    maximum_envelope_arithmetic_kg: float
    maximum_envelope_gradient_effect_kg: float
    maximum_transport_arithmetic_kg: float
    logit_bound_allowance: float
    concentration_roundoff_allowance: float = 128 * _EPS
    parent_ceiling_kg: float = 1e-9


@dataclass(frozen=True)
class RobustStoppingResult:
    status: str
    feasible_regions: tuple[MassRegion, ...]
    excluded_regions: tuple[MassRegion, ...]
    unresolved_regions: tuple[MassRegion, ...]
    outer_possible_feasible_regions: tuple[MassRegion, ...]
    resolution_qualified: bool
    achieved_unresolved_neighborhood_kg: float
    box: envelope.AssayBox
    query: stopping.StoppingQuery
    options: RobustStoppingOptions
    model_sha256: str
    box_sha256: str
    query_sha256: str
    options_sha256: str
    anchor_kg: float
    model_domain_kg: float
    model_training_identity_json: str
    feature_extrapolation: tuple[str, ...]
    rights: str
    claims: tuple[str, ...]
    resources: ResourceUse
    numerical_allowances: Allowances
    point_result: stopping.StoppingResult | None
    version: str = VERSION
    physical_validation: str = 'NOT_ESTABLISHED'
    production_adoption_authorized: bool = False
    numerical_qualification: str = 'ALLOWANCE_BASED_NOT_INTERVAL_CERTIFIED'
    topology: str = 'NO_COMPONENT_TOPOLOGY_CLAIM_ACROSS_UNRESOLVED_REGIONS'

    def to_dict(self) -> dict:
        data = asdict(self) | {'box': self.box.to_dict(), 'units': dict(forward.UNITS),
                              'requested_mass_resolution_kg': self.options.mass_resolution_kg}
        data['numerical_settings'] = {
            'mass_cell_width_target_kg': self.options.mass_resolution_kg / 4,
            'tighter_gap_trigger_cell_width_kg': min(
                self.model_domain_kg, 8 * self.options.mass_resolution_kg),
            'machine_epsilon': _EPS, 'transport_and_logit_arithmetic_multiplier': 512,
            'sigmoid_roundoff_multiplier': 128,
            'point_inverse_mass_resolution_kg': stopping.MASS_RESOLUTION_KG,
            'point_inverse_max_refinements': stopping.MAX_REFINEMENTS,
            'forward_version': forward.VERSION, 'envelope_version': envelope.VERSION,
            'point_inverse_version': stopping.VERSION,
        }
        data['point_result'] = self.point_result.to_dict() if self.point_result else None
        return forward.strict_json(forward.canonical(data))

    def to_json(self) -> str:
        return forward.canonical(self.to_dict()) + '\n'


class _Stop(RuntimeError):
    """Sanitized stop that escapes the parents' numerical exception handlers."""


class _Accounting:
    def __init__(self, options: RobustStoppingOptions) -> None:
        self.options = options
        self.points = self.failed_points = 0
        self.parent_allowance = 0.

    def observe(self, call: Callable, count: int):
        # This guard executes BEFORE delegated delivery, including failed calls.
        if self.points + count > self.options.max_parent_evaluations:
            raise _Stop('GLOBAL_PARENT_EVALUATION_LIMIT')
        self.points += count
        try:
            with warnings.catch_warnings():
                warnings.simplefilter('error', IntegrationWarning)
                predictions = call()
            for p in predictions:
                if math.isfinite(p.allowance_kg):
                    self.parent_allowance = max(self.parent_allowance, p.allowance_kg)
                if (not p.numerical_qualified or not math.isfinite(p.allowance_kg)
                        or not 0 <= p.allowance_kg <= 1e-9
                        or not math.isfinite(p.solute_kg)
                        or not 0 <= p.solute_kg <= p.end_kg - p.start_kg
                        or (p.end_kg > p.start_kg and (p.tds_percent is None
                            or not math.isfinite(p.tds_percent) or not 0 <= p.tds_percent <= 100))
                        or (p.end_kg == p.start_kg and p.tds_percent is not None)):
                    self.failed_points += 1
            return predictions
        except Exception:
            self.failed_points += count
            raise


@dataclass(frozen=True)
class _TrackedState(forward.State):
    _account: _Accounting = field(repr=False, compare=False)

    def predict_intervals(self, starts_kg, ends_kg, **kwargs):
        starts, ends = tuple(starts_kg), tuple(ends_kg)
        return self._account.observe(
            lambda: forward.State.predict_intervals(self, starts, ends, **kwargs), len(starts))

    def remaining_solute(self, stop_mass_kg, **kwargs):
        return self._account.observe(
            lambda: (forward.State.remaining_solute(self, stop_mass_kg, **kwargs),), 1)[0]


@dataclass(frozen=True)
class _TrackedModel(forward.Model):
    _account: _Accounting = field(repr=False, compare=False)

    def condition(self, inputs):
        return _TrackedState(self, inputs, self._account)


def _merge(regions) -> tuple[MassRegion, ...]:
    out: list[MassRegion] = []
    for r in sorted(regions, key=lambda r: (r.lower_kg, not r.lower_included, r.upper_kg)):
        if r.lower_kg == r.upper_kg and not (r.lower_included and r.upper_included):
            continue
        if out and (r.lower_kg < out[-1].upper_kg or
                    (r.lower_kg == out[-1].upper_kg and
                     (r.lower_included or out[-1].upper_included))):
            p = out.pop()
            upper = max(p.upper_kg, r.upper_kg)
            included = ((p.upper_kg == upper and p.upper_included) or
                        (r.upper_kg == upper and r.upper_included))
            r = MassRegion(p.lower_kg, upper, p.lower_included, included,
                           tuple(sorted(set(p.reasons + r.reasons))))
        out.append(r)
    return tuple(out)


def _contains(r: MassRegion, lo: float, hi: float, point: bool) -> bool:
    return (r.lower_kg <= lo <= hi <= r.upper_kg and
            (not point or ((lo > r.lower_kg or r.lower_included) and
                           (hi < r.upper_kg or r.upper_included))))


def _point_partition(result: stopping.StoppingResult) -> list[tuple[str, MassRegion]]:
    """Translate endpoint brackets conservatively; retain the full parent result."""
    safe, possible, uncertain = [], [], []
    for c in result.components:
        possible.append(MassRegion(c.lower.lower_kg, c.upper.upper_kg))
        for e in (c.lower, c.upper):
            if e.lower_kg < e.upper_kg:
                uncertain.append(MassRegion(e.lower_kg, e.upper_kg,
                    reasons=('POINT_INVERSE_ROOT_ENCLOSURE',)))
            elif e.qualification in ('EXACT_STRUCTURAL_ROOT', 'QUALIFIED_QUERY_POINT'):
                safe.append(MassRegion(e.lower_kg, e.upper_kg))
        if c.interior_min_kg is not None and c.interior_max_kg is not None:
            safe.append(MassRegion(max(c.interior_min_kg, c.lower.upper_kg),
                                   min(c.interior_max_kg, c.upper.lower_kg),
                                   c.lower.qualification == 'QUERY_BOUNDARY',
                                   c.upper.qualification == 'QUERY_BOUNDARY'))
    for u in result.unresolved_regions:
        r = MassRegion(u.lower_kg, u.upper_kg, reasons=(u.reason,))
        possible.append(r)
        uncertain.append(r)
    cuts = sorted({result.query.stop_min_kg, result.query.stop_max_kg,
                   *(v for r in (*safe, *possible, *uncertain) for v in (r.lower_kg, r.upper_kg))})
    out = []
    atoms = [(x, x, True) for x in cuts] + [(a, b, False) for a, b in zip(cuts, cuts[1:])]
    for lo, hi, point in sorted(atoms):
        reasons: tuple[str, ...]
        if any(_contains(r, lo, hi, point) for r in safe):
            label, reasons = 'feasible', ('POINT_INVERSE_QUALIFIED_INTERIOR_OR_EXACT_POINT',)
        elif any(_contains(r, lo, hi, point) for r in possible):
            label = 'unresolved'
            reasons = tuple(sorted({s for r in uncertain if _contains(r, lo, hi, point)
                                    for s in r.reasons})) or ('POINT_INVERSE_ENDPOINT_UNCERTAINTY',)
        else:
            label, reasons = 'excluded', ('POINT_INVERSE_EXCLUDED',)
        out.append((label, MassRegion(lo, hi, point, point, reasons)))
    return out


def _point_refinement_reservation(state, query):
    """Bound parent frontier refinements without running or replacing its inverse.

    Every original knot piece has at most one stationary guard per TDS
    boundary, adding at most one non-guard piece. Each non-guard piece can
    run two MAX_REFINEMENTS/2 frontiers. Equal boundary functions are shared.
    The parent exposes a maximum iteration count, not a cumulative count;
    report this reservation separately from actual new mass-cell splits.
    """
    lo, hi = query.stop_min_kg, query.stop_max_kg
    if lo == hi:
        return 0
    knots = tuple(map(float, forward.IntervalGeometry([], [], state.model.domain_kg).knots))
    pieces = 1 + sum(lo < k < hi for k in knots)
    boundaries = {('tds' if 'tds' in n else 'solute', getattr(query, n))
                  for n in _LIMITS if getattr(query, n) is not None}
    total = 0
    for kind, target in boundaries:
        extra = 0
        if kind == 'tds' and 0 < target < 100:
            level = math.log(target) - math.log(100 - target)
            extra = sum(a < hi and lo < b and min(u, v) < level < max(u, v)
                        for a, b, u, v in zip(knots, knots[1:], state.logits, state.logits[1:]))
        total += (pieces + extra) * stopping.MAX_REFINEMENTS
    return total


class _Engine:
    def __init__(self, model, box, query, options):
        self.original, self.box, self.query, self.options = model, box, query, options
        self.account = _Accounting(options)
        self.model = _TrackedModel(**{f.name: getattr(model, f.name) for f in fields(forward.Model)},
                                   _account=self.account)
        self.calls = self.tight_calls = self.splits = self.failed_calls = 0
        self.assay_splits = self.bound_evals = self.quads = self.point_calls = 0
        self.point_reserved = 0
        self.accounting_complete = True
        self.integration = self.arithmetic = self.gradient = self.transport = 0.
        self.derivative_allowance = 0.
        self.cache: dict[tuple[float, float], envelope.DeliveryEnvelope] = {}
        self.partition: list[tuple[str, MassRegion]] = []
        self.point_result: stopping.StoppingResult | None = None

    def prepare_derivatives(self):
        # Affine logit extrema at corners are valid POINTWISE, not integral extrema.
        self.knots = tuple(map(float, forward.IntervalGeometry([], [], self.model.domain_kg).knots))
        if any(a >= b for a, b in zip(self.knots, self.knots[1:])):
            raise _Stop('DEGENERATE_KNOT_GEOMETRY')
        self.corner_logits = [self.original.condition(self.box.inputs(tuple(q))).logits
                              for q in product(*self.box.bounds)]
        bounds = ((self.box.m1_kg,) * 2, (self.box.m2_kg,) * 2, *self.box.bounds)
        size = max(abs(row[0]) + math.fsum(abs(t) * (max(abs(a), abs(b)) + abs(mu)) / s
                   for t, (a, b), mu, s in zip(row[1:], bounds, self.model.means, forward.SCALES))
                   for row in self.model.theta)
        allowance = 512 * _EPS * (1 + size)
        if not math.isfinite(allowance):
            raise _Stop('DERIVATIVE_ARITHMETIC_OVERFLOW')
        self.derivative_allowance = allowance

    def concentrations(self, lo, hi):
        values = []
        for logits in self.corner_logits:
            for k, (a, b) in enumerate(zip(self.knots, self.knots[1:])):
                if a <= hi and lo <= b:
                    for x in (max(a, lo), min(b, hi)):
                        t = (x - a) / (b - a)
                        values.append((1 - t) * logits[k] + t * logits[k + 1])
        error = self.derivative_allowance
        lower = float(expit(min(values) - error)) - 128 * _EPS
        upper = float(expit(max(values) + error)) + 128 * _EPS
        return max(0., lower), min(1., upper)

    def observe(self, b, gap):
        key = b, gap
        if key in self.cache:
            return self.cache[key]
        if self.calls >= self.options.max_envelope_calls:
            raise _Stop('GLOBAL_ENVELOPE_CALL_LIMIT')
        remaining = self.options.max_parent_evaluations - self.account.points
        if not remaining:
            raise _Stop('GLOBAL_PARENT_EVALUATION_LIMIT')
        self.calls += 1
        self.tight_calls += int(gap < self.options.envelope_absolute_gap_kg)
        q = envelope.EnvelopeQuery(self.box.anchor_kg, b, gap,
            self.options.max_assay_subdivisions_per_call,
            min(remaining, self.options.max_parent_evaluations_per_envelope))
        try:
            r = envelope.bound_interval_delivery(self.model, self.box, q)
        except Exception as exc:
            self.failed_calls += 1
            self.accounting_complete = False  # An exception supplies no nested audit.
            raise _Stop('ENVELOPE_API_FAILURE_NESTED_AUDIT_UNAVAILABLE') from exc
        self.assay_splits += r.resources.subdivisions
        self.bound_evals += r.resources.bound_evaluations
        self.quads += r.resources.adaptive_quadrature_calls
        self.integration = max(self.integration, r.numerical_allowances.maximum_envelope_integration_kg)
        self.arithmetic = max(self.arithmetic, r.numerical_allowances.maximum_arithmetic_kg)
        self.gradient = max(self.gradient, r.numerical_allowances.maximum_gradient_effect_kg)
        if r.resources.failed_parent_evaluations or r.resources.failed_bound_evaluations:
            self.failed_calls += 1
            raise _Stop('ENVELOPE_LOAD_BEARING_NUMERICAL_FAILURE')
        if r.status != 'ENVELOPE_QUALIFIED':
            raise _Stop('ENVELOPE_' + r.termination_reason)
        self.cache[key] = r
        return r

    def classify(self, lo, hi, b, r):
        c0, c1 = self.concentrations(lo, hi)
        satisfied = True
        for name in _LIMITS:
            limit = getattr(self.query, name)
            if limit is None:
                continue
            lower_constraint = '_min_' in name
            t = limit / 100 if 'tds' in name else 0.
            target = t * (b - self.box.anchor_kg) if 'tds' in name else limit
            extreme = r.minimum if lower_constraint else r.maximum
            low, high = extreme.lower_kg - target, extreme.upper_kg - target
            d0, d1 = c0 - t, c1 - t
            if not lower_constraint:
                low, high, d0, d1 = -high, -low, -d1, -d0
            changes = [d * dx for d in (d0, d1) for dx in (lo - b, hi - b)]
            arithmetic = 512 * _EPS * (abs(b) + abs(self.box.anchor_kg) + abs(target)
                + abs(extreme.lower_kg) + abs(extreme.upper_kg) + (hi - lo) * (1 + abs(t)))
            if not math.isfinite(arithmetic):
                raise _Stop('TRANSPORT_ARITHMETIC_OVERFLOW')
            self.transport = max(self.transport, arithmetic)
            low = math.nextafter(low + min(changes) - arithmetic, -math.inf)
            high = math.nextafter(high + max(changes) + arithmetic, math.inf)
            if high < 0:
                return 'excluded'
            if low < 0:
                satisfied = False
        return 'feasible' if satisfied else None

    def structural(self, lo, hi):
        """Only range/anchor identities; no rounded sigmoid zero/equality claims."""
        a = Fraction(self.box.anchor_kg)
        width_min, width_max = Fraction(lo) - a, Fraction(hi) - a
        all_true = True
        for name in _LIMITS:
            v = getattr(self.query, name)
            if v is None:
                continue
            value = Fraction(v)
            truth = None
            if name == 'solute_min_kg':
                if value == 0:
                    truth = True
                elif value >= width_max:
                    truth = False
            elif name == 'solute_max_kg':
                if value >= width_max:
                    truth = True
                elif value == 0 and width_min > 0:
                    truth = False
            elif name == 'suffix_tds_min_percent':
                truth = True if value == 0 else False if value == 100 else None
            else:
                truth = True if value == 100 else False if value == 0 else None
            if truth is False:
                return 'excluded'
            all_true &= truth is True
        return 'feasible' if all_true else None

    def run(self):
        q = self.query
        whole = MassRegion(q.stop_min_kg, q.stop_max_kg)
        if all(a == b for a, b in self.box.bounds):
            try:
                state = self.model.condition(self.box.inputs(tuple(a for a, _ in self.box.bounds)))
                reservation = _point_refinement_reservation(state, q)
                if reservation > self.options.max_mass_subdivisions:
                    raise _Stop('POINT_INVERSE_MASS_BUDGET_RESERVATION_UNAVAILABLE')
                self.point_reserved = reservation
                self.point_calls += 1
                self.point_result = stopping.solve_stopping_ranges(state, q)
                if self.account.failed_points:
                    raise _Stop('POINT_INVERSE_PARENT_NUMERICAL_FAILURE')
                self.partition = _point_partition(self.point_result)
            except Exception as exc:
                reason = str(exc) if isinstance(exc, _Stop) else 'POINT_INVERSE_NUMERICAL_FAILURE'
                self.partition = [('unresolved', MassRegion(whole.lower_kg, whole.upper_kg,
                                                           reasons=(reason,)))]
            return
        try:
            self.prepare_derivatives()
        except Exception:
            self.partition = [('unresolved', MassRegion(whole.lower_kg, whole.upper_kg,
                                                       reasons=('DERIVATIVE_PREPARATION_FAILURE',)))]
            return
        pending = [(-(whole.upper_kg - whole.lower_kg), whole.lower_kg, whole.upper_kg, True)]
        while pending:
            _, lo, hi, right_closed = heapq.heappop(pending)
            try:
                label = self.structural(lo, hi)
                middle = lo + (hi - lo) / 2
                if label is None:
                    r = self.observe(middle, self.options.envelope_absolute_gap_kg)
                    label = self.classify(lo, hi, middle, r)
                    if (label is None and hi - lo <= 8 * self.options.mass_resolution_kg
                            and self.options.tighter_envelope_absolute_gap_kg < r.query.absolute_gap_kg):
                        r = self.observe(middle, self.options.tighter_envelope_absolute_gap_kg)
                        label = self.classify(lo, hi, middle, r)
                if label:
                    self.partition.append((label, MassRegion(lo, hi, True, right_closed,
                                                           ('UNIFORM_CELL_BOUND',))))
                    continue
                if lo == hi:
                    reason = 'POINT_RESIDUAL_AMBIGUITY'
                elif not lo < middle < hi:
                    reason = 'NO_REPRESENTABLE_INTERIOR_MASS'
                elif hi - lo <= self.options.mass_resolution_kg / 4:
                    reason = 'MASS_RESOLUTION_BOUNDARY_NEIGHBORHOOD'
                elif self.splits >= self.options.max_mass_subdivisions:
                    raise _Stop('MASS_SUBDIVISION_LIMIT')
                else:
                    self.splits += 1
                    heapq.heappush(pending, (-(middle - lo), lo, middle, False))
                    heapq.heappush(pending, (-(hi - middle), middle, hi, right_closed))
                    continue
                self.partition.append(('unresolved', MassRegion(lo, hi, True, right_closed, (reason,))))
            except Exception as exc:
                reason = str(exc) if isinstance(exc, _Stop) else 'MASS_CELL_NUMERICAL_FAILURE'
                self.partition.append(('unresolved', MassRegion(lo, hi, True, right_closed, (reason,))))
                self.partition.extend(('unresolved', MassRegion(l, h, True, closed, (reason,)))
                                      for _, l, h, closed in pending)
                pending.clear()

    def result(self):
        feasible, excluded, unresolved = (_merge(r for label, r in self.partition if label == name)
                                          for name in ('feasible', 'excluded', 'unresolved'))
        outer = _merge((*feasible, *unresolved))
        extent = max((r.upper_kg - r.lower_kg for r in unresolved), default=0.)
        boundary_reasons = {'MASS_RESOLUTION_BOUNDARY_NEIGHBORHOOD', 'POINT_INVERSE_ROOT_ENCLOSURE',
                            'POINT_INVERSE_ENDPOINT_UNCERTAINTY'}
        qualified = (extent <= self.options.mass_resolution_kg and
                     all(set(r.reasons) <= boundary_reasons for r in unresolved))
        status = ('NO_ROBUST_FEASIBLE_RANGE' if not outer else
                  'ROBUST_STOPPING_ENCLOSED' if qualified else 'NUMERICALLY_UNRESOLVED')
        bounds = ((self.box.m1_kg,) * 2, (self.box.m2_kg,) * 2, *self.box.bounds)
        extrapolation = tuple(n for n, (lo, hi), a, b in zip(forward.feature_names(self.model.arm),
            bounds, self.model.minima, self.model.maxima) if lo < a or hi > b)
        return RobustStoppingResult(status, feasible, excluded, unresolved, outer, qualified, extent,
            self.box, self.query, self.options, self.original.sha256,
            forward.identity(self.box.to_dict()), forward.identity(self.query.to_dict()),
            forward.identity(self.options.to_dict()), self.box.anchor_kg, self.model.domain_kg,
            self.model.training_identity_json, extrapolation, self.model.rights,
            forward.CLAIMS + ('CONDITIONAL_ON_THE_UNCHANGED_MODEL_AND_CALLER_SUPPLIED_ASSAY_SET',
                'DETERMINISTIC_SET_NOT_PROBABILITY_MODEL',
                'MARGINAL_RANGES_NOT_JOINT_EXPERIMENTAL_SUPPORT',
                'ALLOWANCE_BASED_NOT_INTERVAL_CERTIFIED'),
            ResourceUse(self.splits, self.point_reserved, self.calls, self.tight_calls, self.account.points,
                self.account.failed_points, self.failed_calls, self.assay_splits, self.bound_evals,
                self.quads, self.accounting_complete, self.point_calls, len(self.partition)),
            Allowances(self.account.parent_allowance, self.integration, self.arithmetic,
                       self.gradient, self.transport, self.derivative_allowance), self.point_result)


def solve_robust_stopping_ranges(model: forward.Model, box: envelope.AssayBox,
                                 query: stopping.StoppingQuery, *,
                                 options: RobustStoppingOptions = RobustStoppingOptions()
                                 ) -> RobustStoppingResult:
    if (not isinstance(model, forward.Model) or not isinstance(box, envelope.AssayBox)
            or not isinstance(query, stopping.StoppingQuery)
            or not isinstance(options, RobustStoppingOptions)):
        raise TypeError('TYPED_MODEL_BOX_QUERY_AND_OPTIONS_REQUIRED')
    if model.arm != box.arm:
        raise ValueError('ARM_INFORMATION_CONTRACT_MISMATCH')
    if not box.anchor_kg <= query.stop_min_kg <= query.stop_max_kg <= model.domain_kg:
        raise ValueError('QUERY_OUTSIDE_ANCHOR_OR_MODEL_DOMAIN')
    if any(getattr(query, n) is not None for n in _LIMITS[2:]) and query.stop_min_kg <= box.anchor_kg:
        raise ValueError('TDS_REQUIRES_STRICTLY_POSITIVE_SUFFIX_WIDTH')
    engine = _Engine(model, box, query, options)
    engine.run()
    return engine.result()


def _outside_git(path: Path) -> bool:
    resolved = path.resolve()
    return not any((p / '.git').exists() for p in (resolved, *resolved.parents))


class _PrivateParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's default can echo unrecognized arguments, including private values.
        super().error('invalid arguments, saved input or exclusive output; contents and paths are not printed')


def main() -> None:
    parser = _PrivateParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--synthetic', action='store_true')
    mode.add_argument('--model', type=Path)
    parser.add_argument('--box', type=Path)
    parser.add_argument('--query', type=Path)
    parser.add_argument('--options', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    options = RobustStoppingOptions()
    if args.synthetic:
        if args.box or args.query or args.output or args.options:
            parser.error('--synthetic is a source-free stdout demonstration')
        model = forward.synthetic_model()
        box = envelope.AssayBox('C2', .004, .004, q1=(.14, .16), q2=(.09, .11),
                                input_class='SYNTHETIC')
        query = stopping.StoppingQuery(.009, .08, solute_min_kg=.001, suffix_tds_max_percent=12.)
    else:
        if not args.box or not args.query or not args.output:
            parser.error('--model requires --box, --query and exclusive --output')
        try:
            if not all(_outside_git(p) for p in (args.box, args.query, args.output, args.options) if p):
                raise ValueError('PRIVATE_PATH_REQUIRED')
            model = forward.Model.load(args.model)
            box = envelope.AssayBox.from_dict(forward.strict_json(args.box.read_text()))
            query = stopping.StoppingQuery.from_dict(forward.strict_json(args.query.read_text()))
            if args.options:
                options = RobustStoppingOptions.from_dict(forward.strict_json(args.options.read_text()))
        except (OSError, ArithmeticError, ValueError, TypeError, KeyError, IndexError, RuntimeError):
            parser.error('invalid saved input or private path; input contents are not printed')
    try:
        result = solve_robust_stopping_ranges(model, box, query, options=options)
        if args.output:
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, 'w') as stream:
                stream.write(result.to_json())
        else:
            print(result.to_json(), end='')
    except (OSError, ArithmeticError, ValueError, TypeError, RuntimeError):
        parser.error('invalid query or unavailable exclusive output; input contents are not printed')


if __name__ == '__main__':
    main()

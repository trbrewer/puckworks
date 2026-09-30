"""Complete research stopping sets over immutable conditional-tail states.

G0 / NO_GOVERNING_PHYSICS_CHANGE. See model_eng_mass_stop_001/README.md
for the completeness argument and the distinction between numerical allowances
and rigorous interval certificates. Source-derived rights follow the model;
first-party software licensing does not replace them.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, fields
from fractions import Fraction
import math
from numbers import Real
from pathlib import Path
import warnings

from scipy.integrate import IntegrationWarning

from puckworks.analysis import conditional_tail_delivery as forward

VERSION = 'conditional-tail-stopping/1'
MASS_RESOLUTION_KG = 1e-8
MAX_REFINEMENTS = 128
_EPS = 2.220446049250313e-16
_LIMITS = ('solute_min_kg', 'solute_max_kg',
           'suffix_tds_min_percent', 'suffix_tds_max_percent')


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


@dataclass(frozen=True)
class StoppingQuery:
    """Inclusive bounds; masses use the original collection origin, never reset."""

    stop_min_kg: float
    stop_max_kg: float
    solute_min_kg: float | None = None
    solute_max_kg: float | None = None
    suffix_tds_min_percent: float | None = None
    suffix_tds_max_percent: float | None = None
    mass_unit: str = 'kg'
    solute_unit: str = 'kg'
    tds_unit: str = 'percent'
    basis: str = 'MASS'

    def __post_init__(self) -> None:
        for name in ('stop_min_kg', 'stop_max_kg', *_LIMITS):
            value = getattr(self, name)
            if value is not None or name.startswith('stop_'):
                value = _number(value)
                if value < 0 or ('tds' in name and value > 100):
                    raise ValueError('INVALID_NONNEGATIVE_MASS_OR_TDS_PERCENT')
                object.__setattr__(self, name, value)
        if (self.mass_unit, self.solute_unit, self.tds_unit, self.basis) != (
                'kg', 'kg', 'percent', 'MASS'):
            raise ValueError('UNSUPPORTED_UNITS_OR_BASIS')
        for lo, hi in (('stop_min_kg', 'stop_max_kg'), (_LIMITS[0], _LIMITS[1]),
                       (_LIMITS[2], _LIMITS[3])):
            a, b = getattr(self, lo), getattr(self, hi)
            if a is not None and b is not None and a > b:
                raise ValueError('ORDERED_LIMITS_REQUIRED')
        if all(getattr(self, name) is None for name in _LIMITS):
            raise ValueError('DELIVERY_CONSTRAINT_REQUIRED')

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> StoppingQuery:
        allowed = {f.name for f in fields(cls)}
        required = allowed - set(_LIMITS)
        if not isinstance(data, dict) or not required <= data.keys() <= allowed:
            raise ValueError('STRICT_QUERY_FIELDS_AND_EXPLICIT_UNITS_REQUIRED')
        return cls(**data)


@dataclass(frozen=True)
class Endpoint:
    """An endpoint enclosure, not a recommended or exactly known stop mass."""

    lower_kg: float
    upper_kg: float
    qualification: str
    constraints: tuple[str, ...]
    residual_allowance_kg: float | None
    tds_residual_allowance_percent: float | None
    # |d(F-target)/db| and |d(F-t*(b-a))/db| are at most one.
    bracket_effect_kg: float
    tds_bracket_effect_percent: float | None


@dataclass(frozen=True)
class FeasibleComponent:
    lower: Endpoint
    upper: Endpoint
    # A qualified singleton root can be enclosed without a representable witness.
    interior_min_kg: float | None
    interior_max_kg: float | None
    isolated: bool = False
    partial: bool = False


@dataclass(frozen=True)
class UnresolvedRegion:
    lower_kg: float
    upper_kg: float
    reason: str
    constraints: tuple[str, ...]


@dataclass(frozen=True)
class StoppingResult:
    status: str
    reasons: tuple[str, ...]
    components: tuple[FeasibleComponent, ...]
    unresolved_regions: tuple[UnresolvedRegion, ...]
    query: StoppingQuery
    anchor_kg: float
    domain_kg: float
    model_sha256: str
    state_sha256: str
    arm: str
    input_class: str
    feature_extrapolation: tuple[str, ...]
    rights: str
    claims: tuple[str, ...]
    maximum_forward_allowance_kg: float | None
    forward_evaluations: int
    maximum_refinement_iterations: int
    version: str = VERSION
    physical_validation: str = 'NOT_ESTABLISHED'
    production_adoption_authorized: bool = False

    def to_dict(self) -> dict:
        # Fresh containers; callers cannot mutate this frozen result through them.
        return forward.strict_json(forward.canonical(asdict(self))) | {
            'units': dict(forward.UNITS), 'mass_resolution_target_kg': MASS_RESOLUTION_KG,
            'numerical_qualification': 'ALLOWANCE_BASED_NOT_INTERVAL_CERTIFIED',
        }


@dataclass(frozen=True)
class _Boundary:
    kind: str
    target: float
    senses: tuple[int, ...]  # +1: residual >= 0; -1: residual <= 0
    names: tuple[str, ...]


@dataclass(frozen=True)
class _Band:
    lo: float
    hi: float
    index: int


class _Evaluator:
    def __init__(self, state: forward.State) -> None:
        self.state = state
        self.knots = tuple(map(float, forward.IntervalGeometry([], [], state.model.domain_kg).knots))
        self.observations: dict[float, forward.Prediction | None] = {}
        self.failures: set[str] = set()
        self.forward_allowances: list[float] = []
        self.iterations = 0

    def observe(self, b: float) -> forward.Prediction | None:
        if b not in self.observations:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error', IntegrationWarning)
                    p = self.state.remaining_solute(b)
                if math.isfinite(p.allowance_kg):
                    self.forward_allowances.append(p.allowance_kg)
                if (not p.numerical_qualified or not math.isfinite(p.allowance_kg)
                        or p.allowance_kg > forward.SETTINGS['max_solute_allowance_kg']):
                    self.failures.add('PARENT_FORWARD_ALLOWANCE_NOT_QUALIFIED')
                    p = None
            except (ArithmeticError, ValueError, IntegrationWarning):
                self.failures.add('PARENT_FORWARD_NUMERICAL_FAILURE')
                p = None
            self.observations[b] = p
        return self.observations[b]

    def residual(self, boundary: _Boundary, b: float) -> tuple[float, float]:
        p = self.observe(b)
        if p is None:
            return 0., math.inf
        width = b - self.state.b_anchor
        target = boundary.target if boundary.kind == 'solute' else boundary.target / 100 * width
        # Covers subtraction, product, interpolated logits, and stationary-cut arithmetic.
        # This is a conservative engineering allowance, not outward interval arithmetic.
        arithmetic = 128 * _EPS * (
            abs(p.solute_kg) + abs(target) + width * (1 + max(map(abs, self.state.logits))))
        error = p.allowance_kg + arithmetic
        if not math.isfinite(error):
            self.failures.add('ARITHMETIC_ALLOWANCE_OVERFLOW')
        return p.solute_kg - target, error

    def sign(self, boundary: _Boundary, b: float, radius: float = 0.) -> int | None:
        if self.observe(b) is None:
            return None
        width = Fraction(b) - Fraction(self.state.b_anchor)
        target = Fraction(boundary.target)
        # Exact structural facts avoid treating underflow/saturation as q == 0 or 1.
        if not radius:
            if boundary.kind == 'solute':
                if not width:
                    return -1 if target else 0
                if not target:
                    return 1
                if target >= width:
                    return -1  # finite logits imply F < width
            elif boundary.target in (0., 100.):
                return 1 if not target else -1
            prefix_half = all(u == v == 0. for l, r, u, v in zip(
                self.knots, self.knots[1:], self.state.logits, self.state.logits[1:])
                if max(l, self.state.b_anchor) < min(r, b))
            if prefix_half:
                r = width / 2 - (target if boundary.kind == 'solute' else target * width / 100)
                return (r > 0) - (r < 0)
        value, error = self.residual(boundary, b)
        error += radius  # |h'| <= 1 on a stationary-point guard interval
        return 1 if value > error else -1 if value < -error else None

    def endpoint(self, lo: float, hi: float, kind: str,
                 boundaries: tuple[_Boundary, ...] = ()) -> Endpoint:
        errors = [self.residual(boundary, b)[1] for boundary in boundaries for b in (lo, hi)]
        if not errors:
            errors = [p.allowance_kg for b in (lo, hi) if (p := self.observe(b)) is not None]
        allowance = max(errors) if errors and all(map(math.isfinite, errors)) else None
        width = lo - self.state.b_anchor
        tds = allowance / width * 100 if allowance is not None and width > 0 else None
        if tds is not None and not math.isfinite(tds):
            tds = None
        bracket_tds = (hi - lo) / width * 100 if width > 0 else None
        if bracket_tds is not None and not math.isfinite(bracket_tds):
            bracket_tds = None
        return Endpoint(lo, hi, kind, tuple(n for c in boundaries for n in c.names),
                        allowance, tds, hi - lo, bracket_tds)


def _boundaries(query: StoppingQuery) -> tuple[_Boundary, ...]:
    out: dict[tuple[str, float], _Boundary] = {}
    for name in _LIMITS:
        value = getattr(query, name)
        if value is not None:
            kind = 'solute' if name.startswith('solute') else 'tds'
            key = kind, value
            old = out.get(key, _Boundary(kind, value, (), ()))
            out[key] = _Boundary(kind, value, old.senses + ((1 if '_min_' in name else -1),),
                                 old.names + (name,))
    return tuple(out.values())


def _frontier(ev: _Evaluator, c: _Boundary, good: float, bad: float,
              sign: int) -> tuple[float, int]:
    """Retain the confidently signed side; never discard an ambiguous midpoint."""
    for iteration in range(MAX_REFINEMENTS // 2):
        middle = good + (bad - good) / 2
        if middle in (good, bad):
            return good, iteration
        if ev.sign(c, middle) == sign:
            good = middle
        else:
            bad = middle
    return good, MAX_REFINEMENTS // 2


def _bands(ev: _Evaluator, c: _Boundary, index: int, query: StoppingQuery) -> list[_Band]:
    lo, hi = query.stop_min_kg, query.stop_max_kg
    if c.kind == 'tds' and c.target == 50 and all(v == 0 for v in ev.state.logits):
        return []  # identically zero, established algebraically
    cuts = {lo, hi, *(k for k in ev.knots if lo < k < hi)}
    guards: list[tuple[float, float]] = []
    if c.kind == 'tds' and 0 < c.target < 100:
        level = math.log(c.target) - math.log(100 - c.target)
        for a, b, u, v in zip(ev.knots, ev.knots[1:], ev.state.logits, ev.state.logits[1:]):
            if min(u, v) < level < max(u, v):
                delta = v - u
                if not math.isfinite(delta):
                    return [_Band(lo, hi, index)]
                x = a + (b - a) * ((level - u) / delta)
                radius = 32 * _EPS * ev.state.model.domain_kg * (
                    1 + (abs(u) + abs(v) + abs(level)) / abs(delta))
                left, right = max(lo, a, x - radius), min(hi, b, x + radius)
                if left < right:
                    guards.append((left, right))
                    cuts.update((left, right))
    ordered = sorted(cuts)
    out = []
    for a, b in zip(ordered, ordered[1:]):
        if any(l <= a and b <= r for l, r in guards):
            middle = a + (b - a) / 2
            if middle in (a, b) or ev.sign(c, middle, (b - a) / 2) is None:
                out.append(_Band(a, b, index))
            continue
        sa, sb = ev.sign(c, a), ev.sign(c, b)
        if sa == 0:
            out.append(_Band(a, a, index))
        if sb == 0:
            out.append(_Band(b, b, index))
        if sa is not None and sb is not None and (sa == sb or sa == 0 or sb == 0):
            continue
        left, right, na, nb = a, b, 0, 0
        if sa is not None:
            left, na = _frontier(ev, c, a, b, sa)
        if sb is not None:
            right, nb = _frontier(ev, c, b, left, sb)
        ev.iterations = max(ev.iterations, na + nb)
        out.append(_Band(left, right, index))
    # Join the uncertainty at a shared knot or stationary point before deciding topology.
    merged: list[_Band] = []
    for band in sorted(out, key=lambda x: (x.lo, x.hi)):
        if merged and band.lo <= merged[-1].hi:
            prior = merged.pop()
            band = _Band(prior.lo, max(prior.hi, band.hi), index)
        merged.append(band)
    return merged


def _truth(ev: _Evaluator, boundaries: tuple[_Boundary, ...], b: float,
           omit: set[int] | None = None) -> bool | None:
    unknown = False
    for i, c in enumerate(boundaries):
        if omit and i in omit:
            continue
        sign = ev.sign(c, b)
        if sign is None:
            unknown = True
        elif any(sign * sense < 0 for sense in c.senses):
            return False
    return None if unknown else True


def _unique_crossing(ev: _Evaluator, c: _Boundary, lo: float, hi: float) -> bool:
    a, b = ev.sign(c, lo), ev.sign(c, hi)
    if a not in (-1, 1) or b != -a or hi - lo > MASS_RESOLUTION_KG:
        return False
    if c.kind == 'solute' or c.target in (0., 100.):
        return True
    # No stationary point inside the enclosure, even if it spans an original knot.
    level = math.log(c.target) - math.log(100 - c.target)
    values = []
    for l, r, u, v in zip(ev.knots, ev.knots[1:], ev.state.logits, ev.state.logits[1:]):
        if max(l, lo) < min(r, hi):
            for x in (max(l, lo), min(r, hi)):
                f = (x - l) / (r - l)
                values.append((1 - f) * u + f * v - level)
    margin = 64 * _EPS * (1 + abs(level) + max(map(abs, ev.state.logits)))
    return bool(values) and (min(values) > margin or max(values) < -margin)


def solve_stopping_ranges(state: forward.State, query: StoppingQuery) -> StoppingResult:
    """Return all qualified components and explicit unresolved remainder regions.

    No preferred arm/stop is selected. A component next to an unresolved region
    is partial; two such pieces might belong to the same true component.
    """
    if not isinstance(state, forward.State) or not isinstance(query, StoppingQuery):
        raise TypeError('TYPED_IMMUTABLE_STATE_AND_QUERY_REQUIRED')
    lo, hi = query.stop_min_kg, query.stop_max_kg
    if not state.b_anchor <= lo <= hi <= state.model.domain_kg:
        raise ValueError('QUERY_OUTSIDE_ANCHOR_OR_MODEL_DOMAIN')
    if any(getattr(query, name) is not None for name in _LIMITS[2:]) and lo <= state.b_anchor:
        raise ValueError('TDS_REQUIRES_STRICTLY_POSITIVE_SUFFIX_WIDTH')
    ev = _Evaluator(state)
    boundaries = _boundaries(query)
    components: list[FeasibleComponent] = []
    unresolved: list[UnresolvedRegion] = []
    if any(a >= b for a, b in zip(ev.knots, ev.knots[1:])):
        unresolved.append(UnresolvedRegion(lo, hi, 'DEGENERATE_KNOT_GEOMETRY', ()))
    elif lo == hi:
        truth = _truth(ev, boundaries, lo)
        if truth:
            e = ev.endpoint(lo, lo, 'QUALIFIED_QUERY_POINT', boundaries)
            components.append(FeasibleComponent(e, e, lo, lo, isolated=True))
        elif truth is None:
            unresolved.append(UnresolvedRegion(lo, hi, 'POINT_RESIDUAL_AMBIGUITY',
                                               tuple(n for c in boundaries for n in c.names)))
    else:
        bands = sorted((band for i, c in enumerate(boundaries) for band in _bands(ev, c, i, query)),
                       key=lambda x: (x.lo, x.hi, x.index))
        clusters: list[list[_Band]] = []
        for band in bands:
            if clusters and band.lo <= max(v.hi for v in clusters[-1]):
                clusters[-1].append(band)
            else:
                clusters.append([band])
        edges: dict[float, Endpoint] = {}
        intervals = []
        cursor = lo
        for cluster in clusters:
            a, b = min(v.lo for v in cluster), max(v.hi for v in cluster)
            if cursor < a:
                intervals.append((cursor, a))
            cursor = b
            indices = {v.index for v in cluster}
            active = tuple(boundaries[i] for i in sorted(indices))
            other = _truth(ev, boundaries, a + (b - a) / 2, indices)
            if other is False:
                continue
            exact = a == b and all(ev.sign(c, a) == 0 for c in active)
            crossing = len(indices) == 1 and _unique_crossing(ev, active[0], a, b)
            if other is True and (exact or crossing):
                endpoint = ev.endpoint(a, b, 'EXACT_STRUCTURAL_ROOT' if exact else
                                       'QUALIFIED_CROSSING_BRACKET', active)
                edges[a] = edges[b] = endpoint
                components.append(FeasibleComponent(endpoint, endpoint, None, None, isolated=True))
            else:
                reason = ('OVERLAPPING_CONSTRAINT_BOUNDARIES' if len(indices) > 1 else
                          'TANGENCY_FLAT_ENDPOINT_OR_ILL_CONDITIONED_BOUNDARY')
                unresolved.append(UnresolvedRegion(a, b, reason,
                                                   tuple(n for c in active for n in c.names)))
        if cursor < hi:
            intervals.append((cursor, hi))
        for a, b in intervals:
            middle = a + (b - a) / 2
            truth = _truth(ev, boundaries, middle) if a < middle < b else None
            if ev.observe(a) is None or ev.observe(b) is None:
                truth = None
            if truth:
                left = edges.get(a) or ev.endpoint(a, a, 'QUERY_BOUNDARY' if a == lo else
                                                   'UNRESOLVED_ADJACENCY', boundaries)
                right = edges.get(b) or ev.endpoint(b, b, 'QUERY_BOUNDARY' if b == hi else
                                                    'UNRESOLVED_ADJACENCY', boundaries)
                partial = 'UNRESOLVED_ADJACENCY' in (left.qualification, right.qualification)
                components.append(FeasibleComponent(left, right, a, b, partial=partial))
            elif truth is None:
                reason = ('NO_REPRESENTABLE_INTERIOR_MASS' if middle in (a, b) else
                          'INTERIOR_NUMERICAL_AMBIGUITY')
                unresolved.append(UnresolvedRegion(a, b, reason,
                                                   tuple(n for c in boundaries for n in c.names)))
        merged: list[FeasibleComponent] = []
        for piece in sorted(components, key=lambda x: (x.lower.lower_kg, x.upper.upper_kg)):
            if merged and merged[-1].upper == piece.lower:
                prior = merged.pop()
                starts = [v for v in (prior.interior_min_kg, piece.interior_min_kg) if v is not None]
                ends = [v for v in (prior.interior_max_kg, piece.interior_max_kg) if v is not None]
                piece = FeasibleComponent(prior.lower, piece.upper, min(starts) if starts else None,
                                          max(ends) if ends else None,
                                          prior.isolated and piece.isolated, prior.partial or piece.partial)
            merged.append(piece)
        components = merged
    unresolved.sort(key=lambda x: (x.lower_kg, x.upper_kg, x.reason))
    # A retained point beside unresolved territory is not asserted to be isolated.
    qualified = []
    for c in components:
        adjacent = any(u.lower_kg <= e.upper_kg and e.lower_kg <= u.upper_kg
                       for u in unresolved for e in (c.lower, c.upper))
        qualified.append(FeasibleComponent(c.lower, c.upper, c.interior_min_kg,
                         c.interior_max_kg, c.isolated and not adjacent, c.partial or adjacent))
    components = qualified
    status = 'NUMERICALLY_UNRESOLVED' if unresolved else (
        'FEASIBLE_RANGES' if components else 'NO_FEASIBLE_RANGE')
    reasons = tuple(sorted(ev.failures)) + (('NUMERICAL_AMBIGUITY_RETAINED',) if unresolved else
              ('ALL_THRESHOLD_PIECES_ENUMERATED',))
    allowances = ev.forward_allowances
    return StoppingResult(status, reasons, tuple(components), tuple(unresolved), query,
                          state.b_anchor, state.model.domain_kg, state.model.sha256,
                          forward.identity(state.to_dict()), state.model.arm, state.inputs.input_class,
                          state.feature_extrapolation, state.model.rights, forward.CLAIMS,
                          max(allowances) if allowances else None, len(ev.observations), ev.iterations)


def _outside_git(path: Path) -> bool:
    resolved = path.resolve()
    return not any((p / '.git').exists() for p in (resolved, *resolved.parents))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--synthetic', action='store_true')
    mode.add_argument('--state', type=Path)
    parser.add_argument('--query', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.synthetic:
        if args.query or args.output:
            parser.error('--synthetic is a source-free stdout demonstration')
        model = forward.synthetic_model()
        state = model.condition(forward.EarlyInput('C2', model.means, 'SYNTHETIC'))
        query = StoppingQuery(.009, .08, solute_min_kg=.001, suffix_tds_max_percent=12.)
    else:
        if not args.query or not args.output:
            parser.error('--state requires --query and explicit --output')
        if not _outside_git(args.state) or not _outside_git(args.output):
            parser.error('saved states and results must remain outside Git')
        try:
            state = forward.State.from_dict(forward.strict_json(args.state.read_text()))
            query = StoppingQuery.from_dict(forward.strict_json(args.query.read_text()))
        except (OSError, ValueError, TypeError, KeyError, IndexError):
            parser.error('invalid saved state or query; input contents are not printed')
    try:
        result = solve_stopping_ranges(state, query)
        payload = forward.canonical(result.to_dict()) + '\n'
        if args.output:
            with args.output.open('x') as stream:
                stream.write(payload)
        else:
            print(payload, end='')
    except (OSError, ValueError, TypeError):
        parser.error('invalid query or unavailable exclusive output; no input contents printed')


if __name__ == '__main__':
    main()

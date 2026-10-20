"""Task-local enclosing arithmetic for retained polynomial/root readouts.

No solver or optimizer. Decimal directed rounding encloses coefficient assembly,
evaluation and subdivision. A derivative test proves monotonic pieces; unresolved
stationary regions are subdivided, never discarded by a floating root finder.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
import math

DOWN = Context(prec=60, rounding=ROUND_FLOOR)
UP = Context(prec=60, rounding=ROUND_CEILING)


def dec(x):
    if isinstance(x, Decimal):
        return x
    return Decimal.from_float(x) if isinstance(x, float) else Decimal(x)


@dataclass(frozen=True)
class Interval:
    lo: Decimal
    hi: Decimal

    def __init__(self, lo, hi=None):
        lo, hi = dec(lo), dec(lo if hi is None else hi)
        if not lo.is_finite() or not hi.is_finite() or lo > hi:
            raise ValueError('invalid finite interval')
        object.__setattr__(self, 'lo', lo)
        object.__setattr__(self, 'hi', hi)

    def __add__(self, other):
        b = interval(other)
        return Interval(DOWN.add(self.lo, b.lo), UP.add(self.hi, b.hi))

    __radd__ = __add__

    def __neg__(self):
        return Interval(self.hi.copy_negate(), self.lo.copy_negate())

    def __sub__(self, other):
        return self + -interval(other)

    def __rsub__(self, other):
        return interval(other) + -self

    def __mul__(self, other):
        b = interval(other)
        pairs = [(x, y) for x in (self.lo, self.hi) for y in (b.lo, b.hi)]
        return Interval(min(DOWN.multiply(x, y) for x, y in pairs),
                        max(UP.multiply(x, y) for x, y in pairs))

    __rmul__ = __mul__

    def __truediv__(self, other):
        b = interval(other)
        if b.lo <= 0 <= b.hi:
            raise ValueError('division interval contains zero')
        return self * Interval(DOWN.divide(Decimal(1), b.hi),
                               UP.divide(Decimal(1), b.lo))

    def __rtruediv__(self, other):
        return interval(other) / self

    def sqrt(self):
        if self.lo < 0:
            raise ValueError('negative square-root interval')
        # Decimal.sqrt is correctly rounded to nearest regardless of context
        # rounding. One representable Decimal on either side encloses it.
        lo = Decimal(0) if self.lo == 0 else DOWN.next_minus(DOWN.sqrt(self.lo))
        hi = Decimal(0) if self.hi == 0 else UP.next_plus(UP.sqrt(self.hi))
        return Interval(lo, hi)

    def floats(self):
        # Conversion is round-to-nearest. Move only if it rounded inward.
        lo, hi = float(self.lo), float(self.hi)
        if dec(lo) > self.lo:
            lo = math.nextafter(lo, -math.inf)
        if dec(hi) < self.hi:
            hi = math.nextafter(hi, math.inf)
        return [lo, hi]


def interval(x):
    return x if isinstance(x, Interval) else Interval(x)


def hull(values):
    return Interval(min(v.lo for v in values), max(v.hi for v in values))


def add(a, b):
    return [(a[i] if i < len(a) else Interval(0)) +
            (b[i] if i < len(b) else Interval(0)) for i in range(max(len(a), len(b)))]


def multiply(a, b):
    out = [Interval(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i+j] = out[i+j] + x*y
    return out


def translate(a, origin):
    """Coefficients in u=x-origin, with enclosing coefficient arithmetic."""
    out = [Interval(0)]
    for c in reversed(a):
        out = add(multiply(out, [interval(origin), Interval(1)]), [c])
    return out


def polynomial(a, x):
    # Centering avoids the dependency blowup of global BDF power coefficients.
    center = DOWN.divide(DOWN.add(x.lo, x.hi), Decimal(2))
    u, result = x - center, Interval(0)
    for c in reversed(translate(a, center)):
        result = result*u + c
    return result


def solve(matrix, values):
    """Small interval elimination; a zero-containing pivot fails closed."""
    a = [[interval(x) for x in row] + [interval(v)] for row, v in zip(matrix, values)]
    n = len(a)
    for j in range(n):
        k = max(range(j, n), key=lambda i: abs(float(a[i][j].lo + a[i][j].hi)))
        a[j], a[k] = a[k], a[j]
        pivot = a[j][j]
        a[j] = [x/pivot for x in a[j]]
        for i in range(n):
            if i != j:
                factor = a[i][j]
                a[i] = [x-factor*y for x, y in zip(a[i], a[j])]
    return [row[-1] for row in a]


@dataclass
class Function:
    """Polynomial plus root terms coefficient*sqrt(anchor-x)."""
    coefficients: list
    roots: tuple = ()

    def __post_init__(self):
        self.coefficients = [interval(v) for v in self.coefficients]
        combined = {}
        for c, a in self.roots:
            c, a = interval(c), interval(a)
            key = (a.lo, a.hi)
            combined[key] = combined.get(key, Interval(0)) + c
        self.roots = tuple((c, Interval(*a)) for a, c in combined.items() if c.lo != 0 or c.hi != 0)

    def __sub__(self, other):
        return Function(add(self.coefficients, [-v for v in other.coefficients]),
                        self.roots + tuple((-c, a) for c, a in other.roots))

    def value(self, x):
        result = polynomial(self.coefficients, x)
        for c, anchor in self.roots:
            result = result + c*(anchor-x).sqrt()
        return result

    def derivative(self, x):
        result = polynomial([i*c for i, c in enumerate(self.coefficients)][1:] or [Interval(0)], x)
        for c, anchor in self.roots:
            result = result - c/(2*(anchor-x).sqrt())
        return result

    def enclosure(self, x):
        # Intersection of natural and mean-value forms, both enclosing.
        natural = self.value(x)
        mid = DOWN.divide(DOWN.add(x.lo, x.hi), Decimal(2))
        try:
            centered = self.value(Interval(mid)) + (x-mid)*self.derivative(x)
            return Interval(max(natural.lo, centered.lo), min(natural.hi, centered.hi))
        except ValueError:  # square-root endpoint: derivative is unbounded
            return natural


@dataclass
class Piece:
    low: float
    high: float
    function: Function
    label: str = ''
    low_native: bool = True
    high_native: bool = False


def native_function(pieces, x):
    """Select the native value at x, separately from both limiting values.

    A degenerate piece is an explicit point override; the last override wins
    (e.g. the inlet overrides a zero-width saturated region at time zero).
    Otherwise endpoints belong to the side declared by their native reader.
    """
    overrides = [p for p in pieces if p.low == x == p.high]
    if overrides:
        return overrides[-1].function
    selected = [p for p in pieces if p.low < x < p.high or
                (x == p.low and p.low_native) or (x == p.high and p.high_native)]
    if len(selected) == 1:
        return selected[0].function
    # The outermost captured endpoints are included even for the left/right
    # search convention whose index is clamped at the edge of the capture.
    if not selected and x == min(p.low for p in pieces):
        return min(pieces, key=lambda p: p.low).function
    if not selected and x == max(p.high for p in pieces):
        return max(pieces, key=lambda p: p.high).function
    raise ValueError('ambiguous or unavailable native boundary value')


def enclose(function, low, high, tolerance=1e-11):
    """Full closed-piece range, including both endpoint one-sided limits.

    Endpoint values give inner min/max bounds. An interval is accepted only
    when monotonicity is proved or its full enclosure lies within tolerance
    of those bounds. Thus every stationary point is retained in an enclosing
    terminal bracket, even at a nearly multiple or boundary-adjacent root.
    The returned hull itself, not tolerance added to a sampled range, encloses.
    """
    low, high, tol = dec(low), dec(high), dec(tolerance)
    if low > high:
        raise ValueError('reversed support')
    samples = [(low, function.value(Interval(low))), (high, function.value(Interval(high)))]
    inner_low = min(v.hi for _, v in samples)
    inner_high = max(v.lo for _, v in samples)
    stack, boxes, stationary = [(low, high, 0)], [], []
    evaluations = 0
    while stack:
        a, b, depth = stack.pop()
        x = Interval(a, b)
        evaluations += 1
        if evaluations > 100000 or depth > 160:
            raise ValueError('range subdivision unresolved; no sample fallback')
        try:
            derivative = function.derivative(x)
            monotone = derivative.lo >= 0 or derivative.hi <= 0
        except ValueError:
            monotone = False
        if monotone or a == b:
            boxes.append(hull([function.value(Interval(a)), function.value(Interval(b))]))
            continue
        box = function.enclosure(x)
        if box.lo >= DOWN.subtract(inner_low, tol) and box.hi <= UP.add(inner_high, tol):
            boxes.append(box)
            stationary.append([float(a), float(b)])
            continue
        mid = DOWN.divide(DOWN.add(a, b), Decimal(2))
        if mid in (a, b):
            raise ValueError('subdivision precision exhausted')
        value = function.value(Interval(mid))
        samples.append((mid, value))
        inner_low, inner_high = min(inner_low, value.hi), max(inner_high, value.lo)
        stack.extend([(a, mid, depth+1), (mid, b, depth+1)])
    outer = hull(boxes)
    return dict(bounds=outer.floats(), evaluations=evaluations,
                stationary_brackets=stationary,
                candidates=[float(x) for x, _ in samples],
                outer_excess_bound=Interval(max(UP.subtract(inner_low, outer.lo),
                                                UP.subtract(outer.hi, inner_high), Decimal(0))).floats()[1])


def covering(pieces, low, high):
    """Require the full interval; never clip an unsupported query."""
    ordered = sorted((p for p in pieces if p.high >= low and p.low <= high), key=lambda p: p.low)
    cursor = low
    for p in ordered:
        if p.low > cursor:
            raise ValueError('unsupported full-interval coverage')
        cursor = max(cursor, p.high)
    if not ordered or cursor < high:
        raise ValueError('unsupported full-interval coverage')
    return ordered


def range_pieces(pieces, low, high):
    ordered = covering(pieces, low, high)
    out = []
    for p in ordered:
        a, b = max(low, p.low), min(high, p.high)
        result = enclose(p.function, a, b)
        out.append(dict(low=float(a), high=float(b), low_exact=str(dec(a)), high_exact=str(dec(b)),
                        label=p.label, **result))
    bounds = [min(r['bounds'][0] for r in out), max(r['bounds'][1] for r in out)]
    return dict(bounds=bounds, pieces=out, hull_is_not_attainability=True)


def paired_pieces(first, second, low, high):
    """Direct difference on the union of boundaries, never interval subtraction."""
    a, b = covering(first, low, high), covering(second, low, high)
    out = []
    for p in a:
        for q in b:
            left, right = max(low, p.low, q.low), min(high, p.high, q.high)
            if left < right:
                out.append(Piece(left, right, p.function-q.function, p.label+' / '+q.label))
    # At a shared breakpoint different readers can own opposite sides. That
    # actual point difference need not equal either same-side limiting
    # difference. Also retain an override present in only one arm.
    points = {low, high} | {x for p in a+b for x in (p.low, p.high) if low <= x <= high}
    for x in sorted(points):
        out.append(Piece(x, x, native_function(a, x)-native_function(b, x), 'native common-coordinate point'))
    return out

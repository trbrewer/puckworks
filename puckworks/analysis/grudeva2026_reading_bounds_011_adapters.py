"""Native retained-state adapters for the 011 observation reduction.

Permission-attributed 004 lineage remains governed by THIRD_PARTY_NOTICES.md.
No historical observer is edited; no trajectory is generated here.
"""
from __future__ import annotations

from decimal import Context, Decimal
import numpy as np

from . import grudeva2026_baseline_observation_005 as production
from . import grudeva2026_bed_accuracy_004 as comparator
from .grudeva2026_reading_bounds_011_range import (
    Interval as I, Function, Piece, add, multiply, solve,
)


def quadratic(faces, values, first, scale):
    """Three exact cell-average constraints in a well-scaled local basis."""
    f = [I(float(x)) for x in faces[first:first+4]]
    origin, width = f[0], f[-1]-f[0]
    u = [(x-origin)/width for x in f]
    matrix = [[1, (a+b)/2, (a*a+a*b+b*b)/3] for a, b in zip(u[:-1], u[1:])]
    co = solve(matrix, [I(float(v)) for v in values[first:first+3]])
    # u=(z/scale-origin)/width, using real arithmetic on retained state floats.
    linear = [-origin/width, 1/(I(scale)*width)]
    return Function(add(add([co[0]], [c*co[1] for c in linear]),
                        [c*co[2] for c in multiply(linear, linear)]))


def root_reconstruction(faces, values, cell, inlet=0.):
    """Native constant/linear/root basis, including one-cell/inlet closures."""
    f = [I(float(x)) for x in faces]
    anchor = f[-1]
    if len(values) == 1:
        return Function([inlet, (I(float(values[0]))-inlet)/((f[0]+f[1])/2)])
    indices = [0, 1] if cell <= 1 else list(range(cell-2, cell+1))
    x, p, v = [], [], []
    if cell <= 1:
        x.append(I(0)); p.append(anchor.sqrt()); v.append(I(inlet))
    for j in indices:
        u, w = (anchor-f[j]).sqrt(), (anchor-f[j+1]).sqrt()
        x.append((f[j]+f[j+1])/2)
        p.append(2*(u*u+u*w+w*w)/(3*(u+w)))
        v.append(I(float(values[j])))
    # Solve for A+B*z+C*sqrt(anchor-z); 60-digit directed arithmetic
    # encloses the cancellation in the divided-difference native formulation.
    a, b, c = solve([[1, xx, pp] for xx, pp in zip(x, p)], v)
    return Function([a, b], ((c, anchor),))


def spatial_pieces(faces, values, front, wet, low, high, kind):
    if not 0 <= low <= high <= 1 or front < 0 or front > wet+1e-10:
        raise ValueError('unsupported full spatial interval or regime')
    out = []
    # A product of two finite binary64 numbers has a terminating decimal
    # expansion of at most 2150 fractional places (including subnormals).
    # This context therefore represents the exact physical stencil cut, rather
    # than rounding it to a float and losing a neighboring one-sided limit.
    exact_product = Context(prec=2200)
    physical = ([exact_product.multiply(Decimal.from_float(float(f)), Decimal.from_float(float(front)))
                 for f in faces] if kind == 'production' else list(faces))
    for cell, (a, b) in enumerate(zip(physical[:-1], physical[1:])):
        if b < low or a > high or a == b:
            continue
        if kind == 'production':
            first = min(max(cell-1, 0), len(values)-3)
            function = quadratic(faces, values, first, front)
        else:
            function = root_reconstruction(faces, values, cell)
        out.append(Piece(a, b, function, kind+f' stencil {cell}'))
    if front <= wet:
        out.append(Piece(front, wet, Function([1]), 'saturated; right side at front', True, True))
    if wet < 1:
        out.append(Piece(wet, 1., Function([0]), 'dry; right limit at wetting', False, True))
    if low == 0:
        out.append(Piece(0., 0., Function([0]), 'native inlet'))
    return out


class Production:
    def __init__(self, trajectory):
        self.trajectory = trajectory
        self.states = {}

    def state(self, t):
        if t not in self.states:
            self.states[t] = self.trajectory.evaluate(t)[0]
        return self.states[t]

    def native(self, family, coord, x):
        tr = self.trajectory
        if family == 'figure3_concentration':
            return float(production.profiles(coord['t'], self.state(coord['t']), tr.n,
                         tr.weights, tr.faces, [x], tr.arrival, public=False)[0][0])
        y, _ = tr.evaluate(x)
        return production.outlet(x, y, tr.n, tr.faces, tr.arrival)

    def pieces(self, family, coord, low, high):
        tr = self.trajectory
        if family == 'figure3_concentration':
            y = self.state(coord['t'])
            if tr.arrival is not None and coord['t'] >= tr.arrival:
                raise ValueError('post-exit spatial extension is outside 011 scope')
            return spatial_pieces(tr.faces, y[1:tr.n+1], float(y[0]), min(coord['t'], 1.),
                                  low, high, 'production')
        return self.temporal(low, high)

    def temporal(self, low, high):
        tr = self.trajectory
        if not 0 <= low <= high <= tr.horizon or tr.arrival is None:
            raise ValueError('outside captured valid temporal support')
        out = []
        centers = [(I(float(a))+I(float(b)))/2 for a, b in zip(tr.faces[:-1], tr.faces[1:])]
        factor = (1-centers[-1])/(centers[-1]-centers[-2])
        for segment in tr.segments:
            for k, (a, b) in enumerate(zip(segment.breaks[:-1], segment.breaks[1:])):
                if b < low or a > high:
                    continue
                # Valid breakpoints, never the potentially longer step_bounds.
                cuts = sorted({float(a), float(b)} | {e for e in (1., tr.arrival) if a < e < b})
                co = None
                for left, right in zip(cuts[:-1], cuts[1:]):
                    if right <= 1:
                        function = Function([0])
                    elif right <= tr.arrival:
                        function = Function([1])
                    else:
                        if co is None:
                            d = segment.data[f'D_{k}'][:, [tr.n-1, tr.n]]
                            scalar = [I(float(v)) + factor*(I(float(v))-I(float(u))) for u, v in d]
                            co, product = [scalar[0]], [I(1)]
                            order = int(segment.orders[k])
                            for j in range(order):
                                shift, divisor = float(segment.shifts[k, j]), float(segment.denominators[k, j])
                                product = multiply(product, [-I(shift)/divisor, I(1)/divisor])
                                co = add(co, [c*scalar[j+1] for c in product])
                        function = Function(co)
                    side = segment.meta['dense_side']
                    out.append(Piece(left, right, function,
                                     f'BDF {side} interval {k}', side == 'right', side == 'left'))
        # Physical events use outlet's right side regardless of dense_side.
        for event in (1., tr.arrival):
            if low <= event <= high:
                right = [p for p in out if p.low == event and p.high > event]
                if len(right) != 1:
                    raise ValueError('native right event side unavailable')
                out.append(Piece(event, event, right[0].function, 'native right event value'))
        return out


class Comparator:
    def __init__(self, run):
        self.run = run
        self.times = np.asarray([o['t'] for o in run['observations']])
        self.arrival = run['arrival']
        self._temporal_ready = False

    def prepare_temporal(self):
        if self._temporal_ready:
            return
        run = self.run
        columns = run['accepted_columns']
        if len(set(columns)) != len(columns) or not {'t', 'cup', 'front_trace'} <= set(columns):
            raise ValueError('unknown accepted-step schema')
        a = np.asarray(run['accepted'])
        if a.ndim != 2 or a.shape[1] != len(columns):
            raise ValueError('malformed accepted trace')
        self.t = np.r_[0., a[:, columns.index('t')]]
        self.trace = np.r_[0., a[:, columns.index('front_trace')]]
        self.cup = np.r_[0., a[:, columns.index('cup')]]
        if np.any(np.diff(self.t) <= 0) or self.t[-1] != 8.:
            raise ValueError('incomplete accepted-step coverage')
        events = {e['kind']: e for e in run['events']}
        self.arrival = run['arrival']
        if set(events) != {'first_drip', 'desaturation_exit'}:
            raise ValueError('missing native event sides')
        for name, t in [('first_drip', 1.), ('desaturation_exit', self.arrival)]:
            event = events[name]
            if event['t'] != t or t not in self.t:
                raise ValueError('accepted trace does not split the event')
            right = 1. if name == 'first_drip' else self.trace[np.flatnonzero(self.t == t)[0]]
            left = 0. if name == 'first_drip' else 1.
            if event['outlet_left'] != left or event['outlet_right'] != right:
                raise ValueError('event sides disagree with native outlet')
        integral, maximum = 0., 0.
        for j in range(len(self.t)-1):
            a, b = self.t[j:j+2]
            if a >= 1:
                integral += (b-a)*(1. if a < self.arrival else (self.trace[j]+self.trace[j+1])/2)
            maximum = max(maximum, abs(integral-self.cup[j+1]))
        if maximum > 5e-12:  # unchanged audit_run cup consistency criterion
            raise ValueError('declared interpolant does not reproduce discrete cup convention')
        self.cup_consistency = maximum
        self._temporal_ready = True

    def observation(self, t):
        indices = np.flatnonzero(abs(self.times-t) <= 2e-13)
        if len(indices) != 1:
            raise ValueError('exact figure time unavailable')
        return self.run['observations'][int(indices[0])]

    def native(self, family, coord, x):
        if family == 'figure3_concentration':
            o = self.observation(coord['t'])
            front = o['faces'][-1]
            if x == 0:
                return 0.
            if x >= front:
                return float(x <= min(coord['t'], 1.))
            return comparator.point_liquid(x, np.asarray(o['faces']), np.asarray(o['liquid_cells']))
        self.prepare_temporal()
        if x < self.t[0] or x > self.t[-1]:
            raise ValueError('outside accepted-step support')
        if x < 1:
            return 0.
        if x < self.arrival:
            return 1.
        return float(np.interp(x, self.t, self.trace))

    def pieces(self, family, coord, low, high):
        if family == 'figure3_concentration':
            o = self.observation(coord['t'])
            if coord['t'] >= self.arrival:
                raise ValueError('post-exit spatial extension is outside 011 scope')
            return spatial_pieces(o['faces'], o['liquid_cells'], o['faces'][-1],
                                  min(coord['t'], 1.), low, high, 'comparator')
        self.prepare_temporal()
        if not self.t[0] <= low <= high <= self.t[-1]:
            raise ValueError('unsupported full accepted-step interval')
        out = []
        for j, (a, b) in enumerate(zip(self.t[:-1], self.t[1:])):
            if b < low or a > high:
                continue
            if b <= 1:
                function = Function([0])
            elif b <= self.arrival:
                function = Function([1])
            else:
                slope = (I(float(self.trace[j+1]))-float(self.trace[j]))/(I(float(b))-float(a))
                function = Function([I(float(self.trace[j]))-slope*float(a), slope])
            out.append(Piece(float(a), float(b), function, 'event-split accepted-step linear'))
        return out

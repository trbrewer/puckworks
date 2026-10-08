"""Non-invasive, task-local observation of the preserved EJAM production solver.

No alternative evolution is implemented. NPZ stores numerical BDF differences,
never executable objects. See the 005 contract for reconstruction/error meanings.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
import hashlib
import inspect
import json
import math
from pathlib import Path
import platform
import sys
from unittest.mock import patch

import numpy as np
from scipy.optimize import brentq

from .grudeva2026_conservative_003 import observation_support

TASK = 'MODEL-GRUDEVA2026-BASELINE-OBSERVATION-005'
SCHEMA = 'grudeva2026.baseline_observation.005.v1'
HISTORY_Z = [.025, .1, .25, .5, .75, .9, 1.]
ALGEBRA = 256 * np.finfo(float).eps
INITIAL = 1.388
INITIAL_MASS = 5.552
ROWS = {
    'normal': (128, 32, 2e-8, 2e-10, .05),
    'bed_fine': (256, 32, 2e-8, 2e-10, .05),
    'modes_fine': (128, 64, 2e-8, 2e-10, .05),
    'time_fine': (128, 32, 2e-9, 2e-11, .025),
    'combined': (256, 64, 2e-9, 2e-11, .025),
}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_json(path):
    def reject(value):
        raise ValueError('nonfinite JSON: ' + value)
    data = json.loads(Path(path).read_text(), parse_constant=reject)
    canonical(data)  # also rejects overflowing JSON numbers
    return data


def controls(name):
    n, m, rtol, atol, step = ROWS['normal' if name in ('repeat', 'control') else name]
    return dict(cells=n, modes=m, front_mesh_power=2., rtol=rtol, atol=atol, max_step=step)


def requests(horizon=8.):
    """Original public request and unchanged inherited diagnostic support, separately."""
    from puckworks.models.grudeva2026.verification import reference_times, reference_fixture
    fixture = reference_fixture('publication_reference.json')
    public_t = sorted(set(t for t in reference_times() if t <= horizon) | {0., horizon})
    public_z = sorted(set([i / 100 for i in range(101)] + [r['z'] for r in fixture['figure3']]))
    t, z = observation_support(horizon)
    return dict(public_times=public_t, public_z=public_z, diagnostic_times=t.tolist(),
                diagnostic_z=z.tolist(), history_z=HISTORY_Z)


def sources():
    root = Path(__file__).parents[2]
    names = ['puckworks/models/grudeva2026/reduced.py',
             'puckworks/models/grudeva2026/kernel.py',
             'puckworks/models/grudeva2026/verification.py',
             'puckworks/analysis/grudeva2026_conservative_003.py',
             'puckworks/analysis/grudeva2026_conservative_003_report.py',
             'puckworks/data/grudeva2026/analytic_reference.json',
             'puckworks/data/grudeva2026/publication_reference.json',
             'puckworks/analysis/grudeva2026_baseline_observation_005.py']
    return {name: sha(root / name) for name in names}


@contextmanager
def capture_returns(module):
    """One call, identical return object, unchanged argument references; serial only.

    No interpretation or serialization inside the seam can prevent a returned
    failure from reaching production. Original exceptions propagate unchanged.
    """
    original = module.solve_ivp
    captured = []

    def observe(*args, **kwargs):
        span = args[1] if len(args) > 1 else kwargs['t_span']
        record = dict(requested_interval=list(span), fixed=kwargs.get('events') is None,
                      dripping=span[0] >= 1., function=args[0] if args else kwargs['fun'],
                      solution=None)
        captured.append(record)
        result = original(*args, **kwargs)
        record['solution'] = result
        return result

    with patch.object(module, 'solve_ivp', observe):
        yield captured


def _production_geometry(captured):
    """Read constants from the exact captured RHS closure, without calling it."""
    rhs = inspect.getclosurevars(captured['function']).nonlocals['rhs']
    values = inspect.getclosurevars(rhs).nonlocals
    return {key: np.asarray(values[key]).tolist() for key in ('w', 'rates', 'face', 'xi')}


def polynomial(t, differences, shifts, denominators):
    """SciPy BDF Newton differences; same operation and summation order."""
    p = np.cumprod((t - shifts) / denominators)
    y = np.dot(differences[1:].T, p)
    y += differences[0]
    return y


def _array(data, name, shape=None, integer=False):
    value = data[name]
    if value.dtype.kind not in ('iu' if integer else 'fiu'):
        raise ValueError('invalid numeric dtype: ' + name)
    if shape is not None and value.shape != shape:
        raise ValueError('invalid shape: ' + name)
    if not np.all(np.isfinite(value)):
        raise ValueError('nonfinite array: ' + name)
    return value


class Segment:
    """Lazy safe numerical replay: only one interval's coefficients in memory."""

    def __init__(self, folder, meta, size, *, validate=True):
        self.meta = meta
        name = meta['file']
        if Path(name).name != name or not name.endswith('.npz'):
            raise ValueError('invalid segment filename')
        path = Path(folder) / name
        if sha(path) != meta['sha256']:
            raise ValueError('segment identity mismatch')
        self.data = np.load(path, allow_pickle=False)
        self.t = _array(self.data, 'accepted_t')
        self.y = _array(self.data, 'accepted_y', (size, len(self.t)))
        self.breaks = _array(self.data, 'breaks')
        self.orders = _array(self.data, 'orders', integer=True)
        self.shifts = _array(self.data, 'shifts', (len(self.orders), 5))
        self.denominators = _array(self.data, 'denominators', (len(self.orders), 5))
        self.step_bounds = _array(self.data, 'step_bounds', (len(self.orders), 2))
        self._cached_index, self._cached_d = None, None
        if self.t.ndim != 1 or not len(self.t) or np.any(np.diff(self.t) <= 0):
            raise ValueError('nonmonotone/empty accepted times')
        if self.breaks.shape != (len(self.orders) + 1,) or np.any(np.diff(self.breaks) <= 0):
            raise ValueError('nonmonotone/empty dense support')
        if not len(self.orders) or np.any((self.orders < 1) | (self.orders > 5)):
            raise ValueError('unsupported BDF interpolation order')
        if meta['dense_side'] not in ('left', 'right'):
            raise ValueError('invalid dense selection semantics')
        if [self.t[0], self.t[-1]] != meta['valid_interval'] or not np.array_equal(self.t, self.breaks):
            raise ValueError('accepted/dense segment coverage differs')
        lo, hi = meta['requested_interval']
        if self.t[0] != lo or not lo <= self.t[-1] <= hi:
            raise ValueError('captured interval exceeds requested segment')
        self.events = []
        for k in range(meta['event_channels']):
            t = _array(self.data, f'event_t_{k}')
            y = _array(self.data, f'event_y_{k}', (len(t), size))
            if t.ndim != 1 or np.any(np.diff(t) < 0) or np.any((t < self.t[0]) | (t > self.t[-1])):
                raise ValueError('invalid event support')
            self.events.append((t, y))
        if validate:
            for k, order in enumerate(self.orders):
                _array(self.data, f'D_{k}', (int(order) + 1, size))
                if np.any(self.denominators[k, :order] <= 0):
                    raise ValueError('invalid BDF divisor')
                if self.step_bounds[k, 0] > self.breaks[k] or self.step_bounds[k, 1] < self.breaks[k+1]:
                    raise ValueError('dense polynomial does not cover valid interval')

    def evaluate(self, t):
        if not np.isfinite(t) or not self.t[0] <= t <= self.t[-1]:
            raise ValueError('outside valid captured dense domain')
        k = min(max(int(np.searchsorted(self.breaks, t, side=self.meta['dense_side'])) - 1, 0),
                len(self.orders) - 1)
        if k != self._cached_index:
            self._cached_d = self.data[f'D_{k}']
            self._cached_index = k
        order = self.orders[k]
        return polynomial(t, self._cached_d, self.shifts[k, :order], self.denominators[k, :order])

    def close(self):
        self.data.close()


def save_segment(folder, name, captured, size):
    """Serialize after production returns, preserving terminal truncation."""
    r = captured['solution']
    if r is None:
        return {'unavailable_reason': 'original solve_ivp raised before returning'}
    meta = {k: captured[k] for k in ('requested_interval', 'fixed', 'dripping')}
    try:
        meta['geometry'] = _production_geometry(captured)
    except (KeyError, TypeError):
        # Manufactured interpolant fixtures have no production RHS closure.
        meta['geometry'] = None
    meta.update(success=bool(r.success), status=int(r.status), message=str(r.message),
                nfev=int(r.nfev), njev=int(r.njev), nlu=int(r.nlu),
                valid_interval=[float(r.t[0]), float(r.t[-1])])
    arrays = dict(accepted_t=r.t, accepted_y=r.y)
    events = [] if r.t_events is None else list(zip(r.t_events, r.y_events))
    meta['event_channels'] = len(events)
    for k, (t, y) in enumerate(events):
        arrays[f'event_t_{k}'] = t
        arrays[f'event_y_{k}'] = np.asarray(y).reshape(-1, size)
    if r.sol is None or not len(r.sol.interpolants):
        meta['unavailable_reason'] = 'returned solution has no dense output'
    elif not all(all(hasattr(x, key) for key in ('order', 'D', 't_shift', 'denom', 't_old', 't'))
                 for x in r.sol.interpolants):
        meta['unavailable_reason'] = 'unsupported returned dense interpolant; accepted/event states retained'
    else:
        interpolants = r.sol.interpolants
        meta['dense_side'] = r.sol.side
        arrays['breaks'] = r.sol.ts
        arrays['orders'] = np.array([x.order for x in interpolants], dtype=np.int64)
        arrays['shifts'] = np.zeros((len(interpolants), 5))
        arrays['denominators'] = np.zeros((len(interpolants), 5))
        arrays['step_bounds'] = np.array([[x.t_old, x.t] for x in interpolants])
        for k, x in enumerate(interpolants):
            arrays[f'D_{k}'] = x.D
            arrays['shifts'][k, :x.order] = x.t_shift
            arrays['denominators'][k, :x.order] = x.denom
    path = Path(folder) / name
    if any(np.asarray(value).dtype.kind not in 'fiu' for value in arrays.values()):
        raise ValueError('unsafe nonnumeric returned array; no pickle written')
    np.savez(path, **arrays)
    meta.update(file=name, sha256=sha(path), numerical_bytes=sum(x.nbytes for x in arrays.values()))
    if 'unavailable_reason' not in meta:
        replay = Segment(folder, meta, size)
        maximum = scaled = 0.
        # Actual live interpolants, accepted nodes, interval interiors, event sides.
        points = np.unique(np.r_[r.t, (r.sol.ts[:-1] + r.sol.ts[1:]) / 2,
                                  np.nextafter(r.t[0], r.t[-1]), np.nextafter(r.t[-1], r.t[0])])
        for t in points:
            expected, actual = r.sol(t), replay.evaluate(t)
            error = np.max(abs(actual - expected))
            scale = ALGEBRA * max(1., float(np.max(abs(expected))))
            maximum, scaled = max(maximum, float(error)), max(scaled, float(error / scale))
        accepted_error = max(float(np.max(abs(replay.evaluate(t)-y))) for t, y in zip(r.t, r.y.T))
        event_error = max([float(np.max(abs(replay.evaluate(t)-y)))
                           for ts, ys in events for t, y in zip(ts, ys)] or [0.])
        meta['live_replay'] = dict(points=len(points), max_absolute=maximum, allowance_fraction=scaled,
                                   accepted_state_error=accepted_error, event_state_error=event_error)
        replay.close()
    return meta


class Trajectory:
    def __init__(self, path, *, validate=True):
        self.path = Path(path)
        self.meta = read_json(path)
        if self.meta['schema'] != SCHEMA:
            raise ValueError('wrong observation schema')
        c = self.meta['controls']
        self.n, self.m = c['cells'], c['modes'] + 1
        self.size = 2 + self.n * (self.m + 1)
        if self.meta['state_layout'] != {'size': self.size, 'modal_shape': [self.m, self.n],
                                        'modal_axis': 0, 'order': 's,liquid,mode-major,cup'}:
            raise ValueError('state layout mismatch')
        g = self.meta['geometry']
        self.weights, self.rates = np.asarray(g['w']), np.asarray(g['rates'])
        self.faces = np.asarray(g['face'])
        if (self.weights.shape != (self.m,) or self.rates.shape != (self.m,)
                or self.faces.shape != (self.n + 1,)
                or not np.all(np.isfinite(np.r_[self.weights, self.rates, self.faces]))
                or np.any(self.weights <= 0) or np.any(self.rates <= 0)):
            raise ValueError('invalid captured spectrum/geometry')
        expected_faces = 1 - (1 - np.arange(self.n + 1) / self.n)**c['front_mesh_power']
        if not np.array_equal(self.faces, expected_faces):
            raise ValueError('physical mesh definition mismatch')
        self.segments = []
        try:
            for meta in self.meta['segments']:
                if 'unavailable_reason' in meta:
                    raise ValueError(meta['unavailable_reason'])
                if meta.get('geometry') != g:
                    raise ValueError('segment modal/geometry identity differs')
                s = Segment(self.path.parent, meta, self.size, validate=validate)
                self.segments.append(s)
            if not self.segments:
                raise ValueError('no returned solution segments')
            if self.segments[0].t[0] != 0:
                raise ValueError('missing initial support')
            for a, b in zip(self.segments, self.segments[1:]):
                if a.t[-1] != b.t[0] or not np.array_equal(a.y[:, -1], b.y[:, 0]):
                    raise ValueError('segment gap or state discontinuity')
        except BaseException:
            self.close()
            raise
        self.arrival = None
        for s in self.segments:
            if not s.meta['fixed'] and s.events and len(s.events[0][0]):
                if self.arrival is not None:
                    raise ValueError('duplicate desaturation exit')
                self.arrival = float(s.events[0][0][0])
        self.horizon = float(self.segments[-1].t[-1])

    def evaluate(self, t, *, side='right'):
        if side not in ('left', 'right'):
            raise ValueError('explicit left/right event side required')
        eligible = [s for s in self.segments if s.t[0] <= t <= s.t[-1]]
        if not eligible:
            raise ValueError('observation outside valid captured segments')
        segment = eligible[-1] if side == 'right' else eligible[0]
        return segment.evaluate(t), segment.meta

    def activation(self, z):
        if not np.isfinite(z) or not 0 <= z <= 1:
            raise ValueError('invalid physical position')
        if z == 0:
            return 0.
        if z == 1 and self.arrival is not None:
            return self.arrival
        for s in self.segments:
            if not s.meta['fixed']:
                for k in range(len(s.t) - 1):
                    if s.y[0, k] <= z <= s.y[0, k+1]:
                        return float(brentq(lambda t: s.evaluate(t)[0] - z,
                                            s.t[k], s.t[k+1], xtol=1e-12))
        return None

    def close(self):
        for s in self.segments:
            s.close()


def cell_reconstruction(faces, values, positions):
    """Local quadratic constrained by THREE cell averages, not center values.

    Each containing cell uses itself and its nearest neighbors (one-sided at
    boundaries). The local polynomial integrates back to that cell's average.
    No limiter, fitted coefficient, endpoint extension or square-root basis.
    """
    faces, values, positions = np.asarray(faces), np.asarray(values), np.asarray(positions)
    n = len(faces) - 1
    if n < 3 or np.any(np.diff(faces) <= 0) or values.shape[-1] != n:
        raise ValueError('positive nonuniform cells and matching averages required')
    if not np.all(np.isfinite(np.r_[faces, values.ravel(), positions])):
        raise ValueError('nonfinite reconstruction input')
    result = np.empty(values.shape[:-1] + positions.shape)
    for k, z in enumerate(positions):
        j = min(max(int(np.searchsorted(faces, z, side='right')) - 1, 0), n - 1)
        first = min(max(j - 1, 0), n - 3)
        local = faces[first:first+4]
        h = local[-1] - local[0]
        u = (local - z) / h
        moments = np.column_stack((np.ones(3), (u[1:] + u[:-1]) / 2,
                                   (u[1:]**2 + u[1:]*u[:-1] + u[:-1]**2) / 3))
        weights = np.linalg.solve(moments.T, [1., 0., 0.])
        result[..., k] = values[..., first:first+3] @ weights
    return result


def state_fields(y, n, m):
    if y.shape != (2 + n * (m + 1),) or not np.all(np.isfinite(y)):
        raise ValueError('invalid state shape or nonfinite state')
    return float(y[0]), y[1:n+1], y[n+1:-1].reshape(m, n)


def inventory(t, y, n, weights, faces):
    s, c, modal = state_fields(y, n, len(weights))
    widths = np.diff(s * faces)
    grain = weights @ modal
    ic = math.fsum(float(a*b) for a, b in zip(widths, c))
    ib = math.fsum(float(a*b) for a, b in zip(widths, grain))
    contributions = weights * (modal @ widths)
    reordered = math.fsum(float(v) for v in contributions)
    phases = np.array([ic + min(t, 1.) - s, 3.2 * (ic + INITIAL*(1-s)),
                       .8 * (ib + INITIAL*(1-s))])
    scale = max(1., abs(ic) + abs(ib) + math.fsum(abs(float(v)) for v in contributions))
    return phases, dict(liquid_integral=ic, grain_integral=ib,
                        modal_inventory_contributions=contributions.tolist(),
                        sum_error=abs(ib-reordered), sum_allowance=ALGEBRA*scale,
                        normalized_residual=float((math.fsum(phases) + y[-1] - INITIAL_MASS) / INITIAL_MASS))


def production_trace(c, faces):
    centers = (faces[:-1] + faces[1:]) / 2
    return float(c[-1] + (1-centers[-1]) * (c[-1]-c[-2]) / (centers[-1]-centers[-2]))


def outlet(t, y, n, faces, arrival, *, side='right'):
    if t < 1 or (t == 1 and side == 'left'):
        return 0.
    if arrival is None or t < arrival or (t == arrival and side == 'left'):
        return 1.
    return production_trace(y[1:n+1], faces)


def profiles(t, y, n, weights, faces, z, arrival, *, public=False):
    z = np.asarray(z)
    if z.ndim != 1 or np.any((z < 0) | (z > 1)) or not np.all(np.isfinite(z)):
        raise ValueError('invalid physical profile coordinates')
    s, c, modal = state_fields(y, n, len(weights))
    liquid = np.where(z <= min(t, 1.), 1., 0.)
    modes = np.full((len(weights), len(z)), INITIAL)
    active = z < s
    if s > 0:
        if public:
            centers = s * (faces[:-1] + faces[1:]) / 2
            trace = production_trace(c, faces)
            liquid[active] = np.interp(z[active], np.r_[0., centers, s], np.r_[0., c, trace])
            for k, row in enumerate(modal):
                modes[k, active] = np.interp(z[active], centers, row)
        else:
            # Normalized coordinates are equivalent physical integral constraints
            # and avoid losing precision on the initially tiny active domain.
            liquid[active] = cell_reconstruction(faces, c, z[active]/s)
            modes[:, active] = cell_reconstruction(faces, modal, z[active]/s)
    liquid[z == 0] = 0.
    if arrival is not None and t >= arrival:
        at_exit = z == 1
        if abs(s - 1) > 1e-10:
            raise ValueError('localized fixed domain does not reach physical outlet')
        if public:
            liquid[at_exit] = production_trace(c, faces)
            modes[:, at_exit] = modal[:, -1, None]
        else:
            liquid[at_exit] = cell_reconstruction(faces, c, z[at_exit]/s)
            modes[:, at_exit] = cell_reconstruction(faces, modal, z[at_exit]/s)
    return liquid, weights @ modes, modes


def spectrum_audit(weights, rates, diffusivity=1.):
    """Independent explicit sums plus Euler--Maclaurin remainder, no polygamma."""
    m, end = len(weights) - 1, 200000
    n = np.arange(m + 1, end + 1, dtype=float)
    # Sum over n>end, Euler--Maclaurin at end; omitted terms <1e-28 here.
    tail2 = math.fsum(1/n**2) + 1/end - 1/(2*end**2) + 1/(6*end**3) - 1/(30*end**5)
    tail4 = math.fsum(1/n**4) + 1/(3*end**3) - 1/(2*end**4) + 1/(3*end**5) - 1/(6*end**7)
    resolved = np.arange(1, m + 1, dtype=float)
    expected_w = np.r_[6/(np.pi*resolved)**2, 6/np.pi**2*tail2]
    expected_r = np.r_[(np.pi*resolved)**2*diffusivity,
                       (6/np.pi**2*tail2)/(6/(np.pi**4*diffusivity)*tail4)]
    return dict(weight_error=float(np.max(abs(weights-expected_w))),
                rate_relative_error=float(np.max(abs(rates/expected_r-1))),
                tail_weight=float(weights[-1]), tail_rate=float(rates[-1]),
                complement_tail=float(1-sum(weights[:-1])),
                complement_tail_difference=float(weights[-1]-(1-sum(weights[:-1]))),
                weight_sum=float(sum(weights)), allowance=ALGEBRA)


def cup_integral(trajectory, times, order):
    """Dense interval quadrature, including every cumulative request boundary."""
    times = np.asarray(times)
    if times.ndim != 1 or np.any(np.diff(times) < 0) or times[0] < 0 or times[-1] > trajectory.horizon:
        raise ValueError('cup requests outside captured support')
    nodes, weights = np.polynomial.legendre.leggauss(order)
    physical_breaks = {float(t) for s in trajectory.segments for t in s.breaks}
    breaks = sorted(set(times.tolist() + [0., trajectory.horizon]) | physical_breaks)
    # First drip and exit must be real captured splits if they are in the domain.
    if trajectory.horizon >= 1 and 1. not in physical_breaks:
        raise ValueError('missing first-drip segment split')
    if trajectory.arrival is not None and trajectory.arrival not in physical_breaks:
        raise ValueError('missing exit split')
    cumulative, total = {0.: 0.}, 0.
    for a, b in zip(breaks, breaks[1:]):
        mid, half = (a+b)/2, (b-a)/2
        if mid < 1:
            amount = 0.
        elif trajectory.arrival is None or mid < trajectory.arrival:
            amount = b-a
        else:
            values = []
            for x in nodes:
                t = mid + half*x
                y, _ = trajectory.evaluate(t)
                values.append(production_trace(y[1:trajectory.n+1], trajectory.faces))
            amount = half * float(weights @ values)
        total = math.fsum((total, amount))
        cumulative[b] = total
    return np.array([cumulative[float(t)] for t in times])


def environment():
    import scipy
    from scipy.integrate._ivp import bdf, common
    import os
    return dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                platform=platform.platform(), machine=platform.machine(),
                scipy_bdf_sha256=sha(bdf.__file__), scipy_dense_sha256=sha(common.__file__),
                threads={k: os.environ.get(k) for k in
                         ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')})


def execute(path, row='normal', *, pilot=False, observed=True, matrix_sha256=None):
    """One production call. External controller owns resource accounting."""
    from puckworks.models.grudeva2026 import reduced
    from puckworks import rights
    if not rights.may_execute_locally('grudeva2026.reduced').allowed:
        raise PermissionError('current Grudeva execution permissions do not clear')
    path = Path(path)
    if path.exists():
        raise FileExistsError('immutable attempt output already exists')
    path.parent.mkdir(parents=True, exist_ok=True)
    request = requests(.4 if pilot else 8.)
    c = controls(row)
    base = dict(schema=SCHEMA, task=TASK, status='EXECUTED_UNQUALIFIED', row=row,
                controls=c, parameters=asdict(reduced.Parameters()), requests=request,
                request_hashes={k: digest(v) for k, v in request.items()}, sources=sources(),
                environment=environment(), matrix_sha256=matrix_sha256,
                physical_validation='NOT_ESTABLISHED', observed=observed)
    original = reduced.solve_ivp
    if not observed:
        result = reduced.simulate(controls=reduced.Controls(**c), times=request['public_times'],
                                  profile_z=request['public_z'])
        base.update(public_result=result.to_dict(), public_result_sha256=digest(result.to_dict()))
        path.write_text(canonical(base) + '\n')
        return base
    captured = []
    size = 2 + c['cells']*(c['modes']+2)
    base['state_layout'] = {'size': size, 'modal_shape': [c['modes']+1, c['cells']],
                            'modal_axis': 0, 'order': 's,liquid,mode-major,cup'}
    try:
        with capture_returns(reduced) as captured:
            result = reduced.simulate(controls=reduced.Controls(**c), times=request['public_times'],
                                      profile_z=request['public_z'])
    except BaseException as exc:
        # Keep original exception identity/traceback even if diagnostic persistence fails.
        try:
            base.update(original_exception={'type': type(exc).__name__, 'message': str(exc)},
                        restored=reduced.solve_ivp is original,
                        solve_invocations=len(captured), returned=sum(x['solution'] is not None for x in captured),
                        segments=[])
            for i, segment in enumerate(captured):
                try:
                    if segment['solution'] is not None:
                        base.setdefault('geometry', _production_geometry(segment))
                    base['segments'].append(save_segment(path.parent, f'{path.stem}-segment-{i}.npz', segment, size))
                except Exception as persistence_error:
                    base['segments'].append({'unavailable_reason': str(persistence_error)})
            path.write_text(canonical(base) + '\n')
        except Exception:
            pass
        raise
    public_bytes = result.canonical_json()
    base.update(public_result=json.loads(public_bytes), public_result_sha256=hashlib.sha256(public_bytes.encode()).hexdigest(),
                restored=reduced.solve_ivp is original, solve_invocations=len(captured),
                returned=sum(x['solution'] is not None for x in captured),
                return_identity='same retained object returned by seam',
                state_layout={'size': size, 'modal_shape': [c['modes']+1, c['cells']],
                              'modal_axis': 0, 'order': 's,liquid,mode-major,cup'}, segments=[])
    if captured:
        base['geometry'] = _production_geometry(captured[0])
    for i, segment in enumerate(captured):
        try:
            base['segments'].append(save_segment(path.parent, f'{path.stem}-segment-{i}.npz', segment, size))
        except Exception as exc:
            # Observation failure cannot erase a returned public scientific Result.
            base['segments'].append({'unavailable_reason': type(exc).__name__+': '+str(exc)})
    base['public_result_unchanged_after_capture'] = result.canonical_json() == public_bytes
    base['retained_numerical_bytes'] = sum(s.get('numerical_bytes', 0) for s in base['segments'])
    path.write_text(canonical(base) + '\n')
    return base


def observe_saved(path):
    """Recompute observations and independent audits from safe retained states."""
    trajectory = Trajectory(path)
    r = trajectory.meta
    try:
        request = r['requests']
        z = np.asarray(request['diagnostic_z'])
        activation = [trajectory.activation(float(v)) for v in z]
        ha = [trajectory.activation(v) for v in HISTORY_Z]
        required = sorted(set(request['diagnostic_times']) |
                          {v for v in activation + ha + [trajectory.arrival] if v is not None} |
                          ({1.} if trajectory.horizon >= 1 else set()))
        records, observations, unavailable = [], [], []
        for t in required:
            if t > trajectory.horizon:
                unavailable.append(t)
                continue
            y, phase = trajectory.evaluate(t)
            phases, amounts = inventory(t, y, trajectory.n, trajectory.weights, trajectory.faces)
            cp, bp, modal = profiles(t, y, trajectory.n, trajectory.weights, trajectory.faces,
                                     z, trajectory.arrival)
            _, history, hm = profiles(t, y, trajectory.n, trajectory.weights, trajectory.faces,
                                      HISTORY_Z, trajectory.arrival)
            records.append([t, float(y[0]), outlet(t, y, trajectory.n, trajectory.faces, trajectory.arrival),
                            float(y[-1]), *phases.tolist(), amounts['normalized_residual']])
            observations.append(dict(t=t, liquid_profile=cp.tolist(), grain_profile=bp.tolist(),
                                     grain_history=history.tolist(), modal_profile=modal.tolist(),
                                     modal_history=hm.tolist(), **amounts))
        accepted, events = [], []
        aqueous_min, aqueous_max, grain_min, phase_min = 0., 0., INITIAL, 0.
        sum_fraction = max_conservation = front_excess = 0.
        front_decrease = 0.
        inventory_max_location = None
        for segment_id, segment in enumerate(trajectory.segments):
            front_decrease = max(front_decrease, float(np.max(-np.diff(segment.y[0]), initial=0.)))
            state_rows = [(float(t), y, 'accepted') for t, y in zip(segment.t, segment.y.T)]
            for channel, (ts, ys) in enumerate(segment.events):
                state_rows.extend((float(t), y, f'event:{channel}') for t, y in zip(ts, ys))
            for t, y, provenance in state_rows:
                s, c, modal = state_fields(y, trajectory.n, trajectory.m)
                phases, amounts = inventory(t, y, trajectory.n, trajectory.weights, trajectory.faces)
                grain = trajectory.weights @ modal
                trace = production_trace(c, trajectory.faces)
                aqueous_min = min(aqueous_min, float(c.min()), trace)
                aqueous_max = max(aqueous_max, float(c.max()), trace)
                grain_min = min(grain_min, float(grain.min()))
                phase_min = min(phase_min, float(phases.min()))
                sum_fraction = max(sum_fraction, amounts['sum_error']/amounts['sum_allowance'])
                residual = abs(amounts['normalized_residual'])
                if residual >= max_conservation:
                    max_conservation = residual
                    inventory_max_location = dict(t=t, segment=segment_id, provenance=provenance)
                front_excess = max(front_excess, s-min(t, 1.))
                accepted.append(dict(t=t, segment=segment_id, provenance=provenance, s=s,
                                     cup=float(y[-1]), phases=phases.tolist(),
                                     normalized_residual=amounts['normalized_residual']))
        for t, name in [(1., 'first_drip'), (trajectory.arrival, 'desaturation_exit')]:
            if t is None or t > trajectory.horizon:
                continue
            sides = []
            for side in ('left', 'right'):
                y, phase = trajectory.evaluate(t, side=side)
                sides.append(dict(side=side, fixed=phase['fixed'], dripping=phase['dripping'],
                                  s=float(y[0]), cup=float(y[-1]),
                                  outlet=outlet(t, y, trajectory.n, trajectory.faces, trajectory.arrival, side=side)))
            events.append(dict(t=t, kind=name, sides=sides))
        # Compare direct physical cell integrals with the complete public Result.
        public = r['public_result']
        algebra_fraction = public_profile_error = 0.
        public_outlet_error = public_cup_error = 0.
        public_grain_endpoint_difference = diagnostic_inlet_error = 0.
        names = ['external_liquid', 'fines', 'boulders_including_pores']
        for i, t in enumerate(public['time']):
            y, _ = trajectory.evaluate(t, side='left')  # production selects first segment
            phases, amounts = inventory(t, y, trajectory.n, trajectory.weights, trajectory.faces)
            expected = np.array([public['inventories'][name][i] for name in names])
            allowance = ALGEBRA * (INITIAL_MASS + np.sum(abs(phases)) + np.sum(abs(expected)))
            algebra_fraction = max(algebra_fraction, float(np.max(abs(phases-expected))/allowance))
            cp, bp, _ = profiles(t, y, trajectory.n, trajectory.weights, trajectory.faces,
                                 np.asarray(public['profile_z']), trajectory.arrival, public=True)
            public_profile_error = max(public_profile_error, float(np.max(abs(cp-public['liquid_profiles'][i]))),
                                       float(np.max(abs(bp-public['boulder_mean_profiles'][i]))))
            public_outlet_error = max(public_outlet_error, abs(outlet(t, y, trajectory.n, trajectory.faces,
                                        trajectory.arrival)-public['outlet_concentration'][i]))
            public_cup_error = max(public_cup_error, abs(y[-1]-public['cumulative_discharged_solute'][i]))
        for t in request['diagnostic_times']:
            if t > trajectory.horizon:
                continue
            y, _ = trajectory.evaluate(t)
            _, observed_b, _ = profiles(t, y, trajectory.n, trajectory.weights, trajectory.faces,
                                        np.array([0., 1.]), trajectory.arrival)
            _, public_b, _ = profiles(t, y, trajectory.n, trajectory.weights, trajectory.faces,
                                      np.array([0., 1.]), trajectory.arrival, public=True)
            inlet = float(trajectory.weights @ (INITIAL*np.exp(-trajectory.rates*t)))
            diagnostic_inlet_error = max(diagnostic_inlet_error, abs(observed_b[0]-inlet))
            public_grain_endpoint_difference = max(public_grain_endpoint_difference,
                                                   float(np.max(abs(observed_b-public_b))))
        cup_times = sorted(set([a['t'] for a in accepted] + [v[0] for v in records] + public['time']))
        coarse, fine = cup_integral(trajectory, cup_times, 4), cup_integral(trajectory, cup_times, 8)
        evolved = np.array([trajectory.evaluate(t)[0][-1] for t in cup_times])
        qdiff = abs(coarse-fine)
        bdf_diff = abs(fine-evolved)
        at = int(np.argmax(bdf_diff))
        return dict(controls=r['controls'], arrival=trajectory.arrival, z=z.tolist(), activation=activation,
                    grain_history_z=HISTORY_Z, grain_history_activation=ha,
                    records=records, observations=observations, accepted=accepted, events=events,
                    unavailable_times=unavailable,
                    audits=dict(accepted_states=sum(len(s.t) for s in trajectory.segments),
                                event_states=sum(len(t) for s in trajectory.segments for t, _ in s.events),
                                max_normalized_conservation=max_conservation,
                                conservation_location=inventory_max_location,
                                aqueous_min=aqueous_min, aqueous_max=aqueous_max,
                                grain_mean_min=grain_min, phase_min=phase_min,
                                front_wet_excess=front_excess, front_decrease=front_decrease,
                                independent_sum_allowance_fraction=sum_fraction,
                                public_inventory_allowance_fraction=algebra_fraction,
                                public_profile_reconstruction_error=public_profile_error,
                                public_outlet_error=public_outlet_error, public_cup_error=public_cup_error,
                                diagnostic_inlet_mean_error=diagnostic_inlet_error,
                                public_grain_endpoint_difference=public_grain_endpoint_difference,
                                cup_quadrature_refinement_max=float(qdiff.max()),
                                cup_state_integral_max=float(bdf_diff[at]), cup_max_time=cup_times[at],
                                cup_quadrature_points=len(cup_times),
                                horizon=trajectory.horizon, terminal_phases=records[-1][4:7] if records else None,
                                terminal_cup=records[-1][3] if records else None,
                                spectrum=spectrum_audit(trajectory.weights, trajectory.rates)),
                    physical_validation='NOT_ESTABLISHED')
    finally:
        trajectory.close()

"""Retrospective Gagné conditional machine-pressure comparison, research only.

This is a new response family, not an extraction solver. Concentration is a
latent coordinate. No permeability, viscosity causation or TDS claim follows.
All numeric contracts are frozen in the task's PLAN.json. Requires a source
checkout for the already-tracked .shot inputs; never redistributes raw traces.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import math

import numpy as np
from scipy.integrate import cumulative_trapezoid
from scipy.optimize import minimize

P_EXP = 6.07
A_MIN = 0.76**P_EXP
ARMS = ('V', 'B', 'N', 'W')
SEED = 20261026
STARTS = tuple(product((0., .5, 1.), repeat=2))


@dataclass
class Shots:
    ids: tuple[str, ...]
    t: np.ndarray
    pressure: np.ndarray
    flow: np.ndarray
    temperature: np.ndarray
    volume: np.ndarray
    span: np.ndarray
    wa: np.ndarray
    we: np.ndarray
    na: int

    def subset(self, indices):
        return Shots(tuple(self.ids[i] for i in indices),
                     *(getattr(self, k)[indices] for k in
                       ('t', 'pressure', 'flow', 'temperature', 'volume', 'span', 'wa', 'we')),
                     self.na)


def time_weights(t, left, right):
    """Native midpoint-cell quadrature, with exact window edges; no P interpolation."""
    t = np.asarray(t, dtype=np.float64)
    if len(t) < 2 or not np.all(np.diff(t) > 0) or t[0] < left or t[-1] > right:
        raise ValueError('Finite, strictly increasing native window support required')
    edges = np.r_[left, (t[:-1] + t[1:]) / 2, right]
    weights = np.diff(edges)
    if not np.all(np.isfinite(weights)) or not np.all(weights > 0):
        raise ValueError('Invalid time quadrature')
    return weights / (right - left)


def prepare(channels=None, drift=0.):
    """P [bar], Q [mL/s], basket T [degC] -> float64 K and logged mL.

    Only Q is interpolated, at volume integration endpoints. Pressure is always
    indexed at native samples. No pressure/flow outcome-based row rejection.
    """
    if channels is None:
        from puckworks.data import gagne2021_shots
        channels = gagne2021_shots()
    rows = []
    ids = tuple(sorted(channels))
    for sid in ids:
        c = channels[sid]
        arrays = [np.asarray(c[k], dtype=np.float64) for k in
                  ('espresso_elapsed', 'espresso_pressure', 'espresso_flow',
                   'espresso_temperature_basket')]
        t, pressure, flow, tc = arrays
        if len({x.shape for x in arrays}) != 1 or t.ndim != 1:
            raise ValueError('Misaligned native channels')
        if not all(np.isfinite(x).all() for x in arrays) or not np.all(np.diff(t) > 0):
            raise ValueError('Nonfinite or unordered native channels')
        if t[0] > 42 or t[-1] < 75:
            raise ValueError('Missing common time support')
        am, em = (t >= 42) & (t < 47), (t >= 47) & (t <= 75)
        use = am | em
        ts = t[use]
        if not (np.all(flow[use] >= 0) and np.all(flow[em] > 0)
                and np.all((tc[use] > 0) & (tc[use] < 150))):
            raise ValueError('Invalid volume flow or Celsius channel')
        # Interpolate measured Q first, then apply the coherent scenario at nodes.
        vt = np.unique(np.r_[42., ts, 75.])
        vq = np.interp(vt, t, flow) * (1 + drift * (vt - 42) / 33)
        vi = np.r_[0., cumulative_trapezoid(vq, vt)]
        q = flow[use] * (1 + drift * (ts - 42) / 33)
        rows.append((ts, pressure[use], q, tc[use] + 273.15,
                     np.interp(ts, vt, vi), vi[-1], time_weights(t[am], 42, 47),
                     time_weights(t[em], 47, 75), int(am.sum())))
    if len(set((len(x[0]), x[-1]) for x in rows)) != 1:
        raise ValueError('Unexpected native sample counts; do not silently resample')
    return Shots(ids, *(np.asarray([r[k] for r in rows]) for k in range(8)), rows[0][-1])


def training_counts(counts, held):
    """Remove ALL copies of one physical identity, retaining other multiplicities."""
    weights = np.asarray(counts, dtype=np.int64).copy()
    if np.any(weights < 0):
        raise ValueError('Negative shot multiplicity')
    weights[held] = 0
    if weights.sum() == 0:
        raise ValueError('Empty physical-shot training set')
    return weights


def bounds_for(shots, weights):
    indices = np.flatnonzero(weights)
    median = float(np.median(np.repeat(shots.span[indices], weights[indices])))
    return np.array([A_MIN, np.log(.1 * median)]), np.array([1., np.log(10 * median)])


def response(shots, arm, theta, use_temperature=True, derivatives=False):
    h = np.exp((14514 / 8.314) * (1 / shots.temperature - 1 / 365.15))
    if not use_temperature and arm in ('V', 'B'):
        h = np.ones_like(h)
    if arm == 'N':
        return np.ones_like(h), None
    if arm == 'W':
        return h, None
    a, logl = theta
    zeta = shots.volume / np.exp(logl)
    e = np.exp(-zeta)
    if arm == 'V':
        b = a**(1 / P_EXP)
        z = 1 - (1 - b) * e
        g = h * z**(-P_EXP)
        dlog = np.stack((-e * b / (a * z), P_EXP * (1-b) * e * zeta / z), -1)
    elif arm == 'B':
        z = a + (1-a) * e
        g = h * z
        dlog = np.stack(((1-e) / z, (1-a) * e * zeta / z), -1)
    else:
        raise ValueError('Unknown response family')
    return g, dlog if derivatives else None


def predict(shots, arm, theta=None, use_temperature=True, derivatives=False):
    g, dlog = response(shots, arm, theta, use_temperature, derivatives)
    x = shots.flow * g
    xa = x[:, :shots.na]
    pa = shots.pressure[:, :shots.na]
    numerator = np.sum(shots.wa * xa * pa, axis=1)
    denominator = np.sum(shots.wa * xa**2, axis=1)
    if not np.all(denominator > 0):
        raise ValueError('Nonfinite anchor support')
    amplitude = numerator / denominator
    prediction = amplitude[:, None] * x
    if not derivatives:
        return prediction, amplitude
    da = dlog[:, :shots.na]
    dn = np.sum((shots.wa * xa * pa)[..., None] * da, axis=1)
    dd = 2 * np.sum((shots.wa * xa**2)[..., None] * da, axis=1)
    d_amp = dn / denominator[:, None] - amplitude[:, None] * dd / denominator[:, None]
    jac = x[..., None] * (d_amp[:, None, :] + amplitude[:, None, None] * dlog)
    return prediction, jac


def per_shot_mse(shots, prediction):
    error = prediction[:, shots.na:] - shots.pressure[:, shots.na:]
    return np.sum(shots.we * error**2, axis=1)


class Objective:
    def __init__(self, shots, weights, arm, use_temperature=True):
        indices = np.flatnonzero(weights)
        self.shots = shots.subset(indices)  # evaluated identity is physically absent
        self.weights = weights[indices] / np.sum(weights)
        self.arm = arm
        self.temperature = use_temperature
        self.low, self.high = bounds_for(shots, weights)

    def __call__(self, u):
        theta = self.low + (self.high - self.low) * u
        pred, jac = predict(self.shots, self.arm, theta, self.temperature, True)
        err = pred[:, self.shots.na:] - self.shots.pressure[:, self.shots.na:]
        w = self.weights[:, None] * self.shots.we
        cost = np.sum(w * err**2)
        gradient = 2 * np.sum((w * err)[..., None] * jac[:, self.shots.na:], axis=(0, 1))
        return float(cost), gradient * (self.high - self.low)


def fit(shots, weights, arm, st, use_temperature=True, tighter=False):
    """Independent deterministic nine-start fit; hard 200-objective-call cap/start."""
    obj = Objective(shots, weights, arm, use_temperature)
    free = np.asarray(st) >= .01
    records = []
    best = (float('inf'), None)
    for start in STARTS:
        u0 = np.where(free, start, .5)
        calls = 0
        local_best = (float('inf'), u0.copy())

        def fun(x):
            nonlocal calls, local_best
            if calls >= 200:
                raise StopIteration('objective budget exhausted')
            u = np.full(2, .5)
            u[free] = x
            val, grad = obj(u)
            calls += 1
            if val < local_best[0]:
                local_best = (val, u.copy())
            return val, grad[free]

        if free.any():
            try:
                result = minimize(fun, u0[free], jac=True, method='L-BFGS-B',
                                  bounds=[(0., 1.)] * int(free.sum()),
                                  options=dict(maxfun=200, maxiter=200, maxls=20,
                                               ftol=1e-14 if tighter else 1e-11,
                                               gtol=1e-10 if tighter else 1e-7))
                success, message = bool(result.success), str(result.message)
            except StopIteration:
                success, message = False, 'hard 200 objective evaluation limit'
        else:
            val, _ = obj(u0)
            calls, local_best, success, message = 1, (val, u0.copy()), True, 'both fixed by ST'
        cost, u = local_best
        if cost < best[0]:
            best = (cost, u.copy())
        records.append(dict(start=list(start), effective_start=u0.tolist(),
                            end=u.tolist(), cost=cost, nfev=calls, success=success,
                            message=message, boundary=(np.minimum(u, 1-u) < 1e-7).tolist()))
    cost, u = best
    if u is None or not math.isfinite(cost):
        raise ValueError('No finite fit; failed shot cannot be dropped')
    return dict(theta=(obj.low + (obj.high-obj.low)*u).tolist(), u=u.tolist(), cost=cost,
                low=obj.low.tolist(), high=obj.high.tolist(), free_dimensions=int(free.sum()),
                fixed=(~free).tolist(), starts=records)


class Screening:
    """jaxgsa training-MSE screening; only unfit per-shot design losses are cached.

    The cache is additive bookkeeping, never a fitted all-data solution. Each
    diagnostic explicitly selects its training identities before reduction.
    """
    def __init__(self, shots, use_temperature=True):
        import jax
        import jaxgsa
        jax.config.update('jax_enable_x64', True)
        self.jax, self.gsa = jax, jaxgsa
        self.shots, self.temperature = shots, use_temperature
        self.cache = {}
        # Affine sampling in these unit coordinates is exactly uniform a/logL
        # within each training-derived rectangle; no adaptive design changes.
        self.design = jaxgsa.sobol.sample(
            jaxgsa.Problem(['a', 'logL'], [(0., 1.), (0., 1.)]),
            base_n=512, calc_second_order=False, seed=SEED, verbose=False)
        if self.design.base_n != 512 or self.design.n_expanded != 2048:
            raise ValueError('Frozen Sobol base/expanded count mismatch')
        self.samples = np.asarray(self.design.samples, dtype=np.float64)

    def losses(self, arm, low, high, shot_index):
        key = (arm, tuple(low), tuple(high), shot_index)
        if key not in self.cache:
            one = self.shots.subset([shot_index])
            theta = low + (high-low) * self.samples
            a, ll = theta[:, 0, None], theta[:, 1, None]
            e = np.exp(-one.volume / np.exp(ll))
            h = np.exp((14514/8.314) * (1/one.temperature - 1/365.15))
            if not self.temperature:
                h = np.ones_like(h)
            g = (h * (1-(1-a**(1/P_EXP))*e)**(-P_EXP) if arm == 'V'
                 else h * (a+(1-a)*e))
            x = one.flow * g
            xa = x[:, :one.na]
            amp = np.sum(one.wa*xa*one.pressure[:, :one.na], axis=1) / np.sum(
                one.wa*xa**2, axis=1)
            err = amp[:, None]*x[:, one.na:] - one.pressure[:, one.na:]
            self.cache[key] = np.sum(one.we*err**2, axis=1)
        return self.cache[key]

    def many(self, requests):
        ys = []
        for arm, weights in requests:
            lo, hi = bounds_for(self.shots, weights)
            indices = np.flatnonzero(weights)
            ys.append(sum(self.losses(arm, lo, hi, i) * weights[i] for i in indices)
                      / weights.sum())
        result = self.gsa.sobol.analyze(
            self.design, self.jax.numpy.asarray(np.stack(ys, axis=1)),
            estimator='saltelli-jansen', n_bootstrap=200,
            key=self.jax.random.key(SEED), conf_level=.95, ci_method='quantile',
            slice_chunk_size=16, verbose=False, on_invalid='raise')
        st, ci = np.asarray(result.ST), np.asarray(result.ST_conf)
        return [dict(ST=st[i].tolist(), ST_ci95=ci[:, i, :].T.tolist(),
                     free_dimensions=int((st[i] >= .01).sum())) for i in range(len(requests))]


def shot_scores(shots, pred):
    error = pred[:, shots.na:] - shots.pressure[:, shots.na:]
    # The N anchor amplitude is finite even for zero-flow anchor samples.
    anchor_r = predict(shots, 'N')[1]
    nr = error / shots.flow[:, shots.na:] / anchor_r[:, None]
    return dict(mse=np.sum(shots.we * error**2, axis=1),
                rmse=np.sqrt(np.sum(shots.we * error**2, axis=1)),
                mae=np.sum(shots.we * np.abs(error), axis=1),
                bias=np.sum(shots.we * error, axis=1),
                worst=np.max(np.abs(error), axis=1),
                normalized_resistance_rmse=np.sqrt(np.sum(shots.we * nr**2, axis=1)))


def independent_loss(shots, predictions):
    """Reference reducer deliberately avoids vectorized producer score routines."""
    shot_mses = []
    for i in range(len(shots.ids)):
        terms = [float(w) * (float(y) - float(p))**2
                 for w, y, p in zip(shots.we[i], predictions[i, shots.na:],
                                    shots.pressure[i, shots.na:], strict=True)]
        shot_mses.append(math.fsum(terms))
    return math.sqrt(math.fsum(shot_mses) / len(shot_mses))


def band(gain, lower=.1, upper=.25):
    return 'worse' if gain < 0 else 'small' if gain < lower else 'moderate' if gain < upper else 'large'


def intersected_bands(ci, lower=.1, upper=.25):
    lo, hi = ci
    out = []
    for name, left, right in [('worse', -np.inf, 0), ('small', 0, lower),
                              ('moderate', lower, upper), ('large', upper, np.inf)]:
        if hi >= left and lo < right:
            out.append(name)
    return out

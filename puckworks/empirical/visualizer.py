"""Empirical reported weight-derived flow, conditional on recorded covariates.

No hardware qualification or physical law is claimed. Extraction accepts SI inputs;
Window and saved parameters use explicit research units (bar, g, s, g/s). Later
pressure and start mass must be supplied: this is not an autonomous prefix forecast.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import brentq, minimize
from scipy.sparse import csr_matrix
from scipy.stats import qmc

from puckworks.analysis.cor15_shape_001 import amplitude_fit
from puckworks.analysis.pressure_peak_x1 import numeric, segment_flow, support_blocks

SEED = 20261105
MODELS = ("C0", "T0", "R0", "L0R", "M0R", "AR", "M0", "A")
PRIMARY = MODELS[:6]


@dataclass(frozen=True)
class Settings:
    """Frozen engineering constants, independent of observed model scores."""

    onset_g: float = 1.0
    window_s: float = 2.0
    calibration_windows: int = 3
    guard_s: float = 2.0
    minimum_scored_windows: int = 3
    max_gap_s: float = 2.0
    varying_bar: float = 2.0
    scale_floor_g_s: float = 0.1
    quadrature_order: int = 16


@dataclass
class Window:
    """Observed window plus quadrature covariates; mass is at START, not end."""

    start_s: float
    end_s: float
    mass_g: float
    flow_g_s: float
    pressure_bar: np.ndarray
    quadrature_weight: np.ndarray
    pressure_change_bar: float
    role: str
    supplied_flow_g_s: float = float("nan")

    @property
    def mean_pressure_bar(self):
        return float(self.pressure_bar @ self.quadrature_weight)


@dataclass
class Shot:
    """Private shot linkage and validated windows; never serialize to public output."""

    key: str
    user: str
    windows: list[Window]
    flags: dict
    fold: int = -1

    @property
    def pressure_varying(self):
        p = [w.mean_pressure_bar for w in self.windows if w.role == "score"]
        return bool(np.ptp(p) > Settings().varying_bar)


def pressure_quadrature(t, pressure_bar, start, end, order=16):
    """Integrate h(P(t)), using linear native P and Gauss nodes per native interval."""
    inside = (t > start) & (t < end)
    knots = np.r_[start, t[inside], end]
    pk = np.interp(knots, t, pressure_bar)
    x, weights = np.polynomial.legendre.leggauss(order)
    frac = (x + 1) / 2
    p = pk[:-1, None] + np.diff(pk)[:, None] * frac
    wt = np.diff(knots)[:, None] * weights / (2 * (end - start))
    return p.ravel(), wt.ravel()


def integration_nodes(windows, order=16, max_pressure_step_bar=.1):
    """Numerically refine original linear native intervals, retaining their time mass.

    Stored nodes are GL(order) per original native interval. Equal-time subdivision
    limits each piece's pressure span; it does not move observation boundaries or
    introduce a lag. None reproduces the original unrefined operator. Unbounded n
    still requires the independent selected-model accuracy audit.
    """
    pressure = np.concatenate([w.pressure_bar for w in windows])
    weights = np.concatenate([w.quadrature_weight for w in windows])
    if max_pressure_step_bar is None:
        node_window = np.repeat(np.arange(len(windows)), [len(w.pressure_bar) for w in windows])
        return pressure, weights, node_window
    if not np.isfinite(max_pressure_step_bar) or max_pressure_step_bar <= 0:
        raise ValueError("Pressure integration step must be positive or None")
    if any(len(w.pressure_bar) % order for w in windows):
        raise ValueError("Stored pressure nodes must encode complete native GL intervals")
    pp, wt = pressure.reshape(-1, order), weights.reshape(-1, order)
    nodes, gauss_weights = np.polynomial.legendre.leggauss(order)
    frac = (nodes + 1) / 2
    span = (pp[:, -1] - pp[:, 0]) / (frac[-1] - frac[0])
    left = np.maximum(pp[:, 0] - frac[0] * span, 0)
    right = np.maximum(left + span, 0)
    span = right - left
    parts = np.maximum(1, np.ceil(np.abs(span) / max_pressure_step_bar)).astype(int)
    owners = np.repeat(np.arange(len(parts)), parts)
    offsets = np.arange(len(owners)) - np.repeat(np.cumsum(parts) - parts, parts)
    local = (offsets[:, None] + frac) / parts[owners, None]
    refined_p = left[owners, None] + span[owners, None] * local
    refined_w = wt.sum(axis=1)[owners, None] / parts[owners, None] * (gauss_weights / 2)
    # Preserve untouched native intervals bitwise, avoiding gratuitous interpolation.
    unchanged = parts[owners] == 1
    refined_p[unchanged] = pp[owners[unchanged]]
    refined_w[unchanged] = wt[owners[unchanged]]
    segment_window = np.repeat(np.arange(len(windows)), [len(w.pressure_bar) // order for w in windows])
    return refined_p.ravel(), refined_w.ravel(), np.repeat(segment_window[owners], order)


def extract_windows(time_s, pressure_pa, weight_kg, supplied_flow_kg_s=None,
                    settings=Settings(), generic_flow_present=False):
    """Return windows, diagnostic flags, rejection reason; never repair weight.

    Invalid support is split, not bridged. Resets/clipping/noise are flags only.
    Uses X1's finite support and exact interpolated weight-increment operator.
    """
    t, p, w = (numeric(v) for v in (time_s, pressure_pa, weight_kg))
    if len(t) < 2 or len(p) != len(t) or len(w) != len(t):
        return [], {}, "channel_lengths"
    if not np.isfinite(t).all() or np.any(np.diff(t) <= 0):
        return [], {}, "timestamps"
    wg = w * 1000
    onset_indices = np.flatnonzero(np.isfinite(wg) & (wg > settings.onset_g))
    if not len(onset_indices):
        return [], {}, "no_delivery_onset"
    onset = t[onset_indices[0]]
    finite_w = wg[np.isfinite(wg)]
    diffs = np.diff(wg)
    maximum = np.max(finite_w)
    max_mask = (wg == maximum)
    clipping = any(t[b - 1] - t[a] >= 2 for a, b in support_blocks(
        t, np.where(max_mask, 1.0, np.nan)))
    flags = dict(negative_increment=bool(np.any(diffs < 0)),
                 reset_like=bool(np.any(diffs < -5)), clipping_like=clipping,
                 quantized_0p1g=bool(np.mean(np.abs(finite_w * 10 -
                                                  np.round(finite_w * 10)) < 1e-5) >= .95),
                 onset_left_censored=bool(onset_indices[0] == 0),
                 gap=bool(np.any(np.diff(t) > settings.max_gap_s)),
                 weight_authority="unknown", supplied_generic_flow=("present_estimated_or_unknown_quantity" if generic_flow_present else "absent"))
    valid_p = np.where(np.isfinite(w) & (p >= 0), p, np.nan)
    blocks = []
    for a, b in support_blocks(t, valid_p):
        edges = [a, *(np.flatnonzero(np.diff(t[a:b]) > settings.max_gap_s) + a + 1), b]
        blocks.extend(zip(edges[:-1], edges[1:]))
    flow = numeric(supplied_flow_kg_s) if supplied_flow_kg_s is not None else np.array([])
    windows = []
    cal_end = settings.calibration_windows * settings.window_s
    score_start = cal_end + settings.guard_s
    n = int(np.floor((t[-1] - onset) / settings.window_s + 1e-10))
    record = dict(id="private", label="unknown", t=t.tolist(), p=p.tolist())
    for j in range(n):
        start = onset + j * settings.window_s
        end = start + settings.window_s
        block = next(((a, b) for a, b in blocks
                      if b - a >= 2 and t[a] <= start and t[b - 1] >= end), None)
        if block is None:
            continue
        a, b = block
        # The X1 implementation owns interpolation of the two weight boundaries.
        seg = segment_flow(record, w.tolist(), dict(start=a, end=b, t0=start, t1=end,
                                                  phase="unknown"))
        pp, wt = pressure_quadrature(t[a:b], p[a:b] / 1e5, start, end,
                                     settings.quadrature_order)
        elapsed = j * settings.window_s
        role = "calibration" if elapsed < cal_end else (
            "score" if elapsed >= score_start else "guard")
        sf = float("nan")
        if len(flow) == len(t) and np.isfinite(flow[a:b]).all():
            knots = np.r_[start, t[(t > start) & (t < end)], end]
            sf = float(np.trapezoid(np.interp(knots, t, flow), knots) /
                       settings.window_s * 1000)
        windows.append(Window(elapsed, elapsed + settings.window_s, seg["w"][0],
                              seg["mean_flow_g_s"], pp, wt,
                              (seg["p"][-1] - seg["p"][0]) / 1e5, role, sf))
    if sum(w.role == "calibration" for w in windows) != settings.calibration_windows:
        return [], flags, "calibration_support"
    if sum(w.role == "score" for w in windows) < settings.minimum_scored_windows:
        return [], flags, "later_support"
    q = np.array([w.flow_g_s for w in windows])
    sf = np.array([w.supplied_flow_g_s for w in windows])
    mask = np.isfinite(sf)
    flags["supplied_agreement"] = ("missing" if not mask.all() else
        "agree" if np.sqrt(np.mean((q - sf) ** 2)) <= .5 else "disagree")
    flags["pressure_stable"] = bool(np.ptp([w.mean_pressure_bar for w in windows]) <= .5)
    flags["flow_stable"] = bool(np.std(q) <= .2)
    return windows, flags, "retained"


def recorded_pressure_range(windows, order=16):
    """Recover native-interval endpoint extrema from the stored linear GL nodes."""
    pressure = np.concatenate([w.pressure_bar for w in windows]).reshape(-1, order)
    x, _ = np.polynomial.legendre.leggauss(order)
    fraction = (x + 1) / 2
    span = (pressure[:, -1] - pressure[:, 0]) / (fraction[-1] - fraction[0])
    p0 = pressure[:, 0] - fraction[0] * span
    p1 = p0 + span
    return [float(max(0, min(p0.min(), p1.min()))), float(max(p0.max(), p1.max()))]


def grouped_folds(users, seed=SEED, n_folds=5):
    """Deterministic whole-user assignment, invariant to record order/duplicates."""
    distinct = sorted(set(users))
    if any(not u for u in distinct):
        raise ValueError("Missing user linkage")
    order = np.random.default_rng(seed).permutation(len(distinct))
    return {distinct[int(i)]: j % n_folds for j, i in enumerate(order)}


def coordinates(model):
    """Parameter names, optimizer bounds (log scales; linear n and kappa)."""
    if model == "C0":
        return [], []
    if model == "T0":
        return ["log_Tc"], [(np.log(.1), np.log(1000))]
    names, bounds = [], []
    if model in ("M0R", "AR", "M0", "A"):
        names += ["n", "log_Pd"]
        bounds += [(1, None), (np.log(.1), np.log(100))]
    if model in ("AR", "A"):
        names += ["kappa"]
        bounds += [(0, 2)]
    if model.endswith("R") or model == "R0":
        names += ["log_Mc"]
        bounds += [(np.log(.1), np.log(10000))]
    return names, bounds


def decode(model, theta):
    names, _ = coordinates(model)
    return {k[4:] if k.startswith("log_") else k:
            float(np.exp(v) if k.startswith("log_") else v) for k, v in zip(names, theta)}


def encode(model, params):
    return np.array([np.log(params[k[4:]]) if k.startswith("log_") else params[k]
                     for k in coordinates(model)[0]])


def log_capacity(p_bar, n, Pd, kappa=0, gradient=False):
    """Stable log Form A, including arbitrarily small positive capacity at large n.

    The small-opening expansion has relative error <4.7e-14. Exact P=0 alone
    gives -inf; numerical overflow at positive pressure raises instead of becoming
    a false zero response. Derivatives are w.r.t. n, log(Pd), kappa.
    """
    p = np.asarray(p_bar, dtype=float)
    if (np.any(p < 0) or not np.isfinite(p).all() or not np.isfinite([n, Pd, kappa]).all()
            or n < 1 or Pd <= 0 or kappa < 0):
        raise ValueError("Outside capacity domain")
    with np.errstate(divide="ignore", over="ignore", invalid="ignore"):
        logp = np.log(p) - np.log(Pd)
        z = n * logp
    x = np.exp(np.minimum(z, 7))
    opening = -np.expm1(-x)
    small = z < -30
    logopening = np.array(z, copy=True)
    np.log(opening, out=logopening, where=~small)
    result = np.log(Pd) + logopening - kappa * p
    if not np.isfinite(result[p > 0]).all():
        raise FloatingPointError("Positive-pressure log capacity is unrepresentable")
    if not gradient:
        return result
    ratio = np.ones_like(x)
    np.divide(x * np.exp(-x), opening, out=ratio, where=~small)
    dn = np.zeros_like(p)
    np.multiply(ratio, logp, out=dn, where=p > 0)
    return result, (dn, 1 - n * ratio, -p)


def capacity(p_bar, n, Pd, kappa=0):
    """Physical-unit Form A; use log_capacity for ratios below floating range."""
    return np.exp(log_capacity(p_bar, n, Pd, kappa))


def _signed_log_product(coefficient, log_factor):
    """Compute c*exp(log_factor) without an overflowing intermediate ratio."""
    c, logf = np.broadcast_arrays(np.asarray(coefficient), np.asarray(log_factor))
    result = np.zeros(c.shape, dtype=float)
    nonzero = c != 0
    with np.errstate(divide="ignore", over="ignore", invalid="ignore", under="ignore"):
        magnitude = np.log(np.abs(c[nonzero]).astype(np.longdouble)) + logf[nonzero]
        result[nonzero] = np.sign(c[nonzero]) * np.exp(magnitude).astype(float)
    return result


def _component_normalization(lp, lr, mask, shot_index, count):
    """Choose a supported reference and subtract pressure/recovery separately.

    Separate subtraction preserves pressure ratios when a very negative reported
    mass makes the common recovery logarithm enormous. No flow targets enter.
    """
    full = lp.astype(np.longdouble) + lr
    largest = np.full(count, -np.inf, dtype=np.longdouble)
    np.maximum.at(largest, shot_index[mask], full[mask])
    candidates = mask & (full == largest[shot_index]) & np.isfinite(lp)
    pressure_tie = np.full(count, -np.inf)
    np.maximum.at(pressure_tie, shot_index[candidates], lp[candidates])
    candidates &= lp == pressure_tie[shot_index]
    anchors = np.full(count, len(lp), dtype=int)
    indices = np.flatnonzero(candidates)
    np.minimum.at(anchors, shot_index[indices], indices)
    exists = anchors < len(lp)
    ps = np.zeros(count, dtype=np.longdouble)
    rs = np.zeros(count, dtype=np.longdouble)
    ps[exists] = lp[anchors[exists]]
    rs[exists] = lr[anchors[exists]]
    normalized = (lp.astype(np.longdouble) - ps[shot_index]) + (lr - rs[shot_index])
    return normalized, anchors, exists, ps, rs


def _recovery_log(coordinate, scale):
    """Extended-range log recovery; overflow is a numerical failure, never zero basis."""
    z = -np.asarray(coordinate, dtype=np.longdouble) / scale
    if np.any(z > np.log(np.finfo(np.longdouble).max) - 10):
        raise FloatingPointError("Recovery log exceeds this platform's numeric range")
    inner = np.exp(z)
    return -inner, z * inner


def capacity_maximum(params, pressure_range):
    """All stationary points: unique positive root for kappa>0; else supremum at infinity.

    n*x/(P*expm1(x)) strictly decreases for n>=1: its log derivative w.r.t.
    log(P) is n-1 - n*x/(1-exp(-x)) < -1. This exhausts stationary points.
    """
    n, pd, k = params["n"], params["Pd"], params.get("kappa", 0)
    if k == 0:
        return dict(peak_bar=None, peak_capacity=pd, stationary_points=0,
                    inside_training_range=False, maximum_status="supremum_at_infinity")
    def equation(logp):
        z = n * (logp - np.log(pd))
        if z > 6.5:
            return -k
        x = np.exp(z)
        ratio = 1.0 if x < 1e-6 else x / np.expm1(x)
        return n * ratio * np.exp(-logp) - k
    hi = max(np.log(pd), np.log(n / k) + 1)
    peak = float(np.exp(brentq(equation, -700, hi)))
    return dict(peak_bar=peak, peak_capacity=float(capacity(peak, n, pd, k)),
                stationary_points=1, inside_training_range=bool(pressure_range[0] <= peak <=
                pressure_range[1]), maximum_status="unique_global_maximum")


class Design:
    """Packed windows; differentiable user-balanced early-to-late objective."""

    def __init__(self, shots, quadrature_order=16, max_pressure_step_bar=.1):
        self.shots = shots
        self.integration = dict(max_pressure_step_bar=max_pressure_step_bar)
        windows = [w for s in shots for w in s.windows]
        self.windows = windows
        self.shot_index = np.repeat(np.arange(len(shots)), [len(s.windows) for s in shots])
        self.q = np.array([w.flow_g_s for w in windows])
        self.mass = np.array([w.mass_g for w in windows])
        self.time = np.array([w.start_s for w in windows])
        self.cal = np.array([w.role == "calibration" for w in windows])
        self.score = np.array([w.role == "score" for w in windows])
        pressure, weights, node_window = integration_nodes(windows, quadrature_order,
                                                           max_pressure_step_bar)
        # Exact-value deduplication only: no bins, rounding or changed quadrature.
        # Use exact hashing, avoiding the large-array sort failures observed on the
        # execution host. Python float keys preserve values; no quantization occurs.
        lookup, distinct = {}, []
        def pressure_indices():
            for value in pressure:
                value = float(value)
                index = lookup.get(value)
                if index is None:
                    index = len(distinct)
                    lookup[value] = index
                    distinct.append(value)
                yield index
        inverse = np.fromiter(pressure_indices(), dtype=np.int64, count=len(pressure))
        self.p = np.asarray(distinct)
        lookup.clear()
        distinct.clear()
        if not np.array_equal(self.p[inverse], pressure):
            raise RuntimeError("Exact pressure-node deduplication failed")
        self.pressure_operator = csr_matrix((weights, (node_window, inverse)),
                                            shape=(len(windows), len(self.p)))
        self.meanp = self.pressure_operator @ self.p
        self.pressure_rows = np.repeat(np.arange(len(windows)), np.diff(self.pressure_operator.indptr))
        self.log_pressure_weights = np.log(self.pressure_operator.data)
        self.positive_pressure = np.maximum.reduceat(self.p[self.pressure_operator.indices] > 0,
                                                    self.pressure_operator.indptr[:-1])
        if not np.allclose(self.meanp, [w.mean_pressure_bar for w in windows], rtol=1e-12, atol=1e-10):
            raise RuntimeError("Sparse pressure operator differs from native quadrature")
        for packed, original in ((self.q, [w.flow_g_s for w in windows]),
                                 (self.mass, [w.mass_g for w in windows]),
                                 (self.time, [w.start_s for w in windows])):
            if not np.array_equal(packed, original, equal_nan=True):
                raise RuntimeError("Window covariates changed during design construction")
        users, counts = np.unique([s.user for s in shots], return_counts=True)
        count = dict(zip(users, counts))
        self.shot_weight = np.array([1 / (len(users) * count[s.user]) for s in shots])

    def log_components(self, model, theta, gradient=False):
        """Pressure and recovery logs stay separate until after shot normalization."""
        pars = decode(model, theta)
        names = coordinates(model)[0]
        nw = len(self.windows)
        dpressure = np.zeros((nw, len(names)))
        drecovery = np.zeros((nw, len(names)), dtype=np.longdouble)
        if model in ("M0R", "AR", "M0", "A"):
            lh, derivatives = log_capacity(self.p, pars["n"], pars["Pd"],
                                            pars.get("kappa", 0), gradient=True)
            finite = lh[np.isfinite(lh)]
            # Algebraically identical sparse evaluation when one global log shift
            # keeps every positive node normal. Extreme dynamic range uses row-wise
            # log-sum-exp below; no tiny positive window becomes an exact zero.
            fast = bool(len(finite) and np.ptp(finite) < 500)
            if fast:
                shift = float(finite.max())
                h = np.exp(lh - shift)
                totals = self.pressure_operator @ h
                fast = bool(np.all(totals[self.positive_pressure] > 1e-250))
            if fast:
                with np.errstate(divide="ignore"):
                    lp = shift + np.log(totals)
                if gradient:
                    for key, derivative in zip(("n", "log_Pd", "kappa"), derivatives):
                        if key in names:
                            numerator = self.pressure_operator @ (h * derivative)
                            dpressure[:, names.index(key)] = np.divide(numerator, totals,
                                out=np.zeros(nw), where=totals > 0)
            else:
                indices = self.pressure_operator.indices
                starts = self.pressure_operator.indptr[:-1]
                terms = lh[indices] + self.log_pressure_weights
                maxima = np.maximum.reduceat(terms, starts)
                maxima[~np.isfinite(maxima)] = 0
                weighted = np.exp(terms - maxima[self.pressure_rows])
                totals = np.add.reduceat(weighted, starts)
                with np.errstate(divide="ignore"):
                    lp = maxima + np.log(totals)
                if gradient:
                    normalized = np.divide(weighted, totals[self.pressure_rows],
                                           out=np.zeros_like(weighted), where=totals[self.pressure_rows] > 0)
                    for key, derivative in zip(("n", "log_Pd", "kappa"), derivatives):
                        if key in names:
                            dpressure[:, names.index(key)] = np.add.reduceat(normalized * derivative[indices], starts)
        elif model == "L0R":
            with np.errstate(divide="ignore"):
                lp = np.log(self.meanp)
        else:
            lp = np.zeros(nw)
        lr = np.zeros(nw, dtype=np.longdouble)
        if model == "T0":
            lr, derivative = _recovery_log(self.time, pars["Tc"])
            drecovery[:, names.index("log_Tc")] = derivative
        elif "Mc" in pars:
            lr, derivative = _recovery_log(self.mass, pars["Mc"])
            drecovery[:, names.index("log_Mc")] = derivative
        return lp, lr, dpressure, drecovery

    def basis(self, model, theta, gradient=False):
        """Physical-unit bases for diagnostics; profile() avoids raw-basis underflow."""
        lp, lr, dp, dr = self.log_components(model, theta, gradient)
        base = np.exp(lp.astype(np.longdouble) + lr).astype(float)
        if gradient:
            return base, (base[:, None] * (dp + dr)).astype(float)
        return base

    def profile(self, model, theta, all_windows=False, gradient=False):
        """Direct LS on early observations, with signed-log later prediction.

        Shape normalization is numerical only. The physical amplitude is frozen;
        its returned float can overflow while predictions remain representable.
        """
        lp, lr, dp, dr = self.log_components(model, theta, gradient)
        mask = np.ones(len(lp), dtype=bool) if all_windows else self.cal
        si, ns = self.shot_index, len(self.shots)
        logb, anchors, exists, ps, rs = _component_normalization(lp, lr, mask, si, ns)
        bcal = np.exp(logb[mask])  # extended range is essential to the LS numerator
        if np.any(np.isfinite(logb[mask]) & (bcal == 0)):
            raise FloatingPointError("Calibration basis exceeds extended floating range")
        product = bcal * self.q[mask].astype(np.longdouble)
        if np.any((bcal != 0) & (self.q[mask] != 0) & (product == 0)):
            raise FloatingPointError("Calibration numerator exceeds extended floating range")
        counts = np.bincount(si[mask], minlength=ns)
        starts = np.r_[0, np.cumsum(counts)[:-1]]
        def grouped(values):
            # Neumaier compensation preserves an informative tiny term between
            # cancelling ordinary noisy increments. Primary calibration has 3 terms.
            total = np.zeros(ns, dtype=np.longdouble)
            correction = np.zeros_like(total)
            for j in range(int(counts.max())):
                active = np.flatnonzero(counts > j)
                value = values[starts[active] + j]
                previous = total[active]
                updated = previous + value
                correction[active] += np.where(np.abs(previous) >= np.abs(value),
                    (previous - updated) + value, (value - updated) + previous)
                total[active] = updated
            return total + correction
        den = grouped(bcal ** 2)
        num = grouped(product)
        amplitude = np.divide(num, den, out=np.zeros_like(num), where=den > 0)
        pred = _signed_log_product(amplitude[si], logb)
        raw_amplitude = _signed_log_product(amplitude, -ps - rs)
        if not gradient:
            return pred, raw_amplitude
        offset_p = np.zeros((ns, dp.shape[1]))
        offset_r = np.zeros((ns, dr.shape[1]), dtype=np.longdouble)
        offset_p[exists] = dp[anchors[exists]]
        offset_r[exists] = dr[anchors[exists]]
        dlog = (dp - offset_p[si]).astype(np.longdouble) + (dr - offset_r[si])
        dbcal = bcal[:, None] * dlog[mask]
        if dp.shape[1] == 0:
            return pred, raw_amplitude, np.empty((len(pred), 0))
        da = np.column_stack([np.divide(grouped(dbcal[:, j] *
              (self.q[mask] - 2 * amplitude[si[mask]] * bcal)), den,
              out=np.zeros(ns, dtype=np.longdouble), where=den > 0) for j in range(dp.shape[1])])
        first = _signed_log_product(da[si], logb[:, None])
        with np.errstate(over="ignore", invalid="ignore"):
            second = (pred[:, None].astype(np.longdouble) * dlog).astype(float)
        return pred, raw_amplitude, first + second

    def _amplitudes_scaled(self, basis, all_windows=False):
        """Direct grouped LS; the zero-basis case uses the minimum-norm zero solve."""
        mask = np.ones(len(basis), dtype=bool) if all_windows else self.cal
        ind = self.shot_index[mask]
        den = np.bincount(ind, basis[mask] ** 2, minlength=len(self.shots))
        num = np.bincount(ind, basis[mask] * self.q[mask], minlength=len(self.shots))
        return np.divide(num, den, out=np.zeros_like(num), where=den > 0)

    def scale_basis(self, basis, all_windows=False):
        """Per-shot calibration scaling avoids underflow; only exact zeros stay zero."""
        mask = np.ones(len(basis), dtype=bool) if all_windows else self.cal
        scales = np.zeros(len(self.shots))
        np.maximum.at(scales, self.shot_index[mask], np.abs(basis[mask]))
        scales[scales == 0] = 1
        return basis / scales[self.shot_index], scales

    def amplitudes(self, basis, all_windows=False):
        """Direct amplitudes in original basis units, using a scaled LS solve."""
        b, scales = self.scale_basis(basis, all_windows)
        return self._amplitudes_scaled(b, all_windows) / scales

    def predictions(self, basis, all_windows=False):
        """Stable profiled predictions without multiplying huge raw amplitudes."""
        b, _ = self.scale_basis(basis, all_windows)
        return self._amplitudes_scaled(b, all_windows)[self.shot_index] * b

    def objective(self, model, theta):
        """Equal-user mean per-shot later RMSE, with stable residual scaling."""
        try:
            pred, _, derivative = self.profile(model, theta, gradient=True)
        except (FloatingPointError, OverflowError, ValueError):
            return float("inf"), np.zeros(len(theta))
        si = self.shot_index[self.score]
        residual = pred[self.score] - self.q[self.score]
        derivative = derivative[self.score]
        if not np.isfinite(residual).all() or not np.isfinite(derivative).all():
            return float("inf"), np.zeros(len(theta))
        count = np.bincount(si, minlength=len(self.shots))
        scale = np.zeros(len(self.shots))
        np.maximum.at(scale, si, np.abs(residual))
        scaled = np.divide(residual, scale[si], out=np.zeros_like(residual), where=scale[si] > 0)
        rmse = scale * np.sqrt(np.bincount(si, scaled ** 2, minlength=len(self.shots)) / count)
        value = self.shot_weight @ rmse
        direction = np.divide(residual, rmse[si], out=np.zeros_like(residual), where=rmse[si] > 0)
        jac = (direction * (self.shot_weight / count)[si]) @ derivative
        if not np.isfinite(value) or not np.isfinite(jac).all():
            return float("inf"), np.zeros(len(theta))
        return float(value), jac


def solve_amplitude(observed, basis):
    """COR15 direct LS, with stable scale and defined all-zero minimum-norm solve."""
    y, b = np.asarray(observed), np.asarray(basis)
    if y.shape != b.shape or not len(y) or not np.isfinite(y).all() or not np.isfinite(b).all():
        raise ValueError("Calibration arrays must be finite, nonempty and matching")
    scale = np.max(np.abs(b))
    if scale == 0:
        return 0.0
    return amplitude_fit(y, b / scale)[0] / scale


def predict(model, early_windows, later_windows):
    """Freeze prefix amplitude and return later g/s predictions and amplitude.

    Returned raw amplitude may overflow for subnormal bases; normalized predictions
    remain computable. Later flow targets are ignored. Supply observed start mass and recorded pressure
    for each query window. No early/late overlap is accepted; guard is model metadata.
    """
    settings = Settings(**model["settings"])
    if len(early_windows) != settings.calibration_windows:
        raise ValueError("Wrong number of calibration windows")
    if any(w.start_s != i * settings.window_s or w.end_s != (i + 1) * settings.window_s
           for i, w in enumerate(early_windows)):
        raise ValueError("Calibration must begin at delivery onset")
    if any(w.start_s < early_windows[-1].end_s + settings.guard_s for w in later_windows):
        raise ValueError("Calibration/guard overlaps later prediction")
    shot = Shot("query", "query", [*[replace(w, role="calibration") for w in early_windows],
                                   *[replace(w, role="score") for w in later_windows]], {})
    integration = model.get("integration", {"max_pressure_step_bar": None})
    design = Design([shot], quadrature_order=settings.quadrature_order, **integration)
    result, amplitudes = design.profile(model["model"], encode(model["model"], model["parameters"]))
    return result[len(early_windows):], float(amplitudes[0])


def start_schedule(model, historical, nested=None):
    """Frozen historical and Latin-hypercube starts, never held-out-derived starts."""
    names, bounds = coordinates(model)
    if len(names) == 1:
        return [np.array([v]) for v in np.linspace(*bounds[0], 16)]
    rows = []
    if nested is not None:
        rows.append(encode(model, {**nested["parameters"], "kappa": 0.0}))
    for h in historical:
        rows.append(encode(model, {**h, "Mc": 28.709461834955388}))
    lhs = qmc.LatinHypercube(len(names), seed=SEED).random(16)
    for row in lhs:
        rows.append(np.array([lo + v * ((8 if hi is None else hi) - lo)
                              for v, (lo, hi) in zip(row, bounds)]))
    return rows


def fit_start(design, model, theta):
    """One scheduled optimizer start; returns diagnostics, never held-out predictions."""
    import time
    started = time.process_time()
    result = minimize(lambda x: design.objective(model, x), theta, jac=True,
                      method="L-BFGS-B", bounds=coordinates(model)[1],
                      options=dict(ftol=1e-9, gtol=1e-6, maxiter=400, maxfun=1000, maxls=40))
    return dict(theta=result.x.tolist(), objective=float(result.fun) if np.isfinite(result.fun) else None,
                finite_objective=bool(np.isfinite(result.fun)),
                success=bool(result.success and np.isfinite(result.fun)), message=str(result.message),
                evaluations=int(result.nfev), iterations=int(result.nit),
                core_hours=(time.process_time() - started) / 3600)


def fitted_model(model, params, metadata=None, settings=Settings(), max_pressure_step_bar=.1):
    """Portable scalar-parameter artifact. No individual amplitudes or identifiers."""
    return dict(schema="puckworks.reported-flow.v1", model=model, parameters=params,
                settings=asdict(settings), integration=dict(max_pressure_step_bar=max_pressure_step_bar),
                metadata=metadata or {})


def save_model(path, model):
    """Save canonical JSON and a detached SHA-256; return content hash."""
    path = Path(path)
    body = json.dumps(model, sort_keys=True, indent=2, allow_nan=False) + "\n"
    path.write_text(body)
    digest = hashlib.sha256(body.encode()).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(digest + "\n")
    return digest


def load_model(path):
    """Verify detached hash and schema before loading a saved predictor."""
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.with_suffix(path.suffix + ".sha256").read_text().strip() != digest:
        raise ValueError("Model hash mismatch")
    model = json.loads(path.read_text())
    if model.get("schema") != "puckworks.reported-flow.v1" or model.get("model") not in MODELS:
        raise ValueError("Unknown model/schema")
    return model


def audit_quadrature(shots, model, chunk_size=8192):
    """Covariate-only independent pressure-average check; no flow targets consulted.

    Compare the saved refined GL16 operator with original-native GL64; sharp pressure
    intervals additionally use QUADPACK
    with transition points and scaled integrands. This diagnoses actual selected
    models, not uniform accuracy over the unbounded n domain. A failure blocks scores.
    """
    from scipy.integrate import quad

    pars = model["parameters"]
    if "n" not in pars:
        return dict(passed=True, maximum_relative_error=0.0, adaptive_intervals=0)
    n, pd, k = pars["n"], pars["Pd"], pars.get("kappa", 0)
    windows = [w for s in shots for w in s.windows]
    order = model["settings"]["quadrature_order"]
    old_nodes, _ = np.polynomial.legendre.leggauss(order)
    old_frac = (old_nodes + 1) / 2
    pp = np.concatenate([w.pressure_bar for w in windows]).reshape(-1, order)
    wt = np.concatenate([w.quadrature_weight for w in windows]).reshape(-1, order)
    span = (pp[:, -1] - pp[:, 0]) / (old_frac[-1] - old_frac[0])
    p0 = np.maximum(pp[:, 0] - old_frac[0] * span, 0)
    p1 = np.maximum(p0 + span, 0)
    seg_window = np.repeat(np.arange(len(windows)), [len(w.pressure_bar) // order for w in windows])
    from scipy.special import logsumexp
    candidate_p, candidate_weights, candidate_window = integration_nodes(
        windows, order, model.get("integration", {}).get("max_pressure_step_bar"))
    terms = log_capacity(candidate_p, n, pd, k) + np.log(candidate_weights)
    candidate_starts = np.r_[0, np.flatnonzero(np.diff(candidate_window)) + 1]
    candidate_max = np.maximum.reduceat(terms, candidate_starts)
    candidate_max[~np.isfinite(candidate_max)] = 0
    candidate_sum = np.add.reduceat(np.exp(terms - candidate_max[candidate_window]), candidate_starts)
    with np.errstate(divide="ignore"):
        old = candidate_max + np.log(candidate_sum)
    del candidate_p, candidate_weights, candidate_window, terms
    sw = wt.sum(axis=1)
    starts = np.r_[0, np.cumsum([len(w.pressure_bar) // order for w in windows])[:-1]]

    def combine(log_segments):
        maximum = np.maximum.reduceat(log_segments, starts)
        maximum[~np.isfinite(maximum)] = 0
        total = np.add.reduceat(np.exp(log_segments - maximum[seg_window]), starts)
        with np.errstate(divide="ignore"):
            return maximum + np.log(total)

    new_nodes, new_weights = np.polynomial.legendre.leggauss(64)
    frac = (new_nodes + 1) / 2
    reference = np.zeros(len(p0))
    for a in range(0, len(p0), chunk_size):
        b = min(a + chunk_size, len(p0))
        pressures = p0[a:b, None] + (p1[a:b] - p0[a:b])[:, None] * frac
        reference[a:b] = logsumexp(log_capacity(np.maximum(pressures, 0), n, pd, k)
                                    + np.log(new_weights / 2), axis=1)
    lo, hi = np.minimum(p0, p1), np.maximum(p0, p1)
    with np.errstate(divide="ignore", invalid="ignore"):
        sharp = ((n * np.log(hi / lo) > 1) | (k * (hi - lo) > 1)) & (hi > lo)
    peak = capacity_maximum(pars, [0, float(np.max(hi))])["peak_bar"]
    transitions = pd * np.exp(np.array([-30, -20, -12, -8, -4, -2, -1, 0, 1, 2, 3, 4]) / n)
    for i in np.flatnonzero(sharp):
        left, right = lo[i], hi[i]
        levels = transitions[(transitions > left) & (transitions < right)]
        if peak is not None and left < peak < right:
            levels = np.r_[levels, peak]
        candidates = [left, right]
        if peak is not None and left < peak < right:
            candidates.append(peak)
        logscale = float(np.max(log_capacity(candidates, n, pd, k)))
        points = sorted(set(((levels - left) / (right - left)).tolist()))
        integral, error = quad(lambda u: float(np.exp(log_capacity(
            left + u * (right - left), n, pd, k) - logscale)),
            0, 1, points=points, epsabs=1e-11, epsrel=1e-11, limit=200)
        if error > 1e-8 or integral <= 0:
            raise RuntimeError("Independent quadrature reference unresolved")
        reference[i] = logscale + np.log(integral)
    new = combine(np.log(sw) + reference)
    lr = np.zeros(len(windows), dtype=np.longdouble)
    if "Mc" in pars:
        lr, _ = _recovery_log([w.mass_g for w in windows], pars["Mc"])
    si = np.repeat(np.arange(len(shots)), [len(s.windows) for s in shots])
    cal = np.array([w.role == "calibration" for w in windows])
    normalized, _, _, ps, rs = _component_normalization(new, lr, cal, si, len(shots))
    old_normalized = (old.astype(np.longdouble) - ps[si]) + (lr - rs[si])
    maximum = np.full(len(shots), -np.inf, dtype=np.longdouble)
    np.maximum.at(maximum, si[cal], normalized[cal])
    denominator = np.maximum(normalized, np.log(1e-12) + maximum[si])
    nonzero = np.isfinite(denominator)
    relative = np.zeros(len(windows), dtype=np.longdouble)
    relative[nonzero] = np.abs(np.exp(normalized[nonzero] - denominator[nonzero]) -
                              np.exp(old_normalized[nonzero] - denominator[nonzero]))
    error = float(np.max(relative))
    return dict(passed=bool(np.isfinite(error) and error <= 1e-5), maximum_relative_error=error,
                adaptive_intervals=int(sharp.sum()), windows=len(windows))

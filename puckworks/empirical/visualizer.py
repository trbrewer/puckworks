"""Empirical reported weight-derived flow, conditional on recorded covariates.

No hardware qualification or physical law is claimed. Extraction accepts SI inputs;
Window and saved parameters use explicit research units (bar, g, s, g/s). Later
pressure and start mass must be supplied: this is not an autonomous prefix forecast.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
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


def pressure_quadrature(t, pressure_bar, start, end, order=4):
    """Integrate h(P(t)), using linear native P and Gauss nodes per native interval."""
    inside = (t > start) & (t < end)
    knots = np.r_[start, t[inside], end]
    pk = np.interp(knots, t, pressure_bar)
    x, weights = np.polynomial.legendre.leggauss(order)
    frac = (x + 1) / 2
    p = pk[:-1, None] + np.diff(pk)[:, None] * frac
    wt = np.diff(knots)[:, None] * weights / (2 * (end - start))
    return p.ravel(), wt.ravel()


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


def capacity(p_bar, n, Pd, kappa=0):
    """Form A; kappa=0 is exactly the monotone model, including floating operations."""
    p = np.asarray(p_bar, dtype=float)
    if np.any(p < 0) or n < 1 or Pd <= 0 or kappa < 0:
        raise ValueError("Outside capacity domain")
    with np.errstate(divide="ignore", over="ignore"):
        z = n * np.log(p / Pd)
    x = np.exp(np.minimum(z, 7))  # exp(-exp(7)) is already below double precision.
    return Pd * (-np.expm1(-x)) * np.exp(-kappa * p)


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
        if z > 7:
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

    def __init__(self, shots):
        self.shots = shots
        windows = [w for s in shots for w in s.windows]
        self.windows = windows
        self.shot_index = np.repeat(np.arange(len(shots)), [len(s.windows) for s in shots])
        self.q = np.array([w.flow_g_s for w in windows])
        self.mass = np.array([w.mass_g for w in windows])
        self.time = np.array([w.start_s for w in windows])
        self.cal = np.array([w.role == "calibration" for w in windows])
        self.score = np.array([w.role == "score" for w in windows])
        pressure = np.concatenate([w.pressure_bar for w in windows])
        weights = np.concatenate([w.quadrature_weight for w in windows])
        node_window = np.repeat(np.arange(len(windows)), [len(w.pressure_bar) for w in windows])
        # Exact-value deduplication only: no bins, rounding or changed quadrature.
        self.p, _, inverse = np.unique(pressure, return_index=True, return_inverse=True)
        if not np.array_equal(self.p[inverse], pressure):
            raise RuntimeError("Exact pressure-node deduplication failed")
        self.pressure_operator = csr_matrix((weights, (node_window, inverse)),
                                            shape=(len(windows), len(self.p)))
        self.meanp = self.pressure_operator @ self.p
        users, counts = np.unique([s.user for s in shots], return_counts=True)
        count = dict(zip(users, counts))
        self.shot_weight = np.array([1 / (len(users) * count[s.user]) for s in shots])

    def basis(self, model, theta, gradient=False):
        """Covariates only: never consult observed window flow here."""
        pars = decode(model, theta)
        names = coordinates(model)[0]
        nw = len(self.windows)
        deriv = {}
        if model in ("M0R", "AR", "M0", "A"):
            n, pd, k = pars["n"], pars["Pd"], pars.get("kappa", 0)
            with np.errstate(divide="ignore"):
                logp = np.log(self.p / pd)
            x = np.exp(np.minimum(n * logp, 7))
            ex = np.exp(-x)
            decay = np.exp(-k * self.p)
            h = pd * (-np.expm1(-x)) * decay
            reduce = lambda v: self.pressure_operator @ v
            base = reduce(h)
            if gradient:
                xl = np.zeros_like(x)
                np.multiply(x, logp, out=xl, where=np.isfinite(logp))
                deriv["n"] = reduce(pd * ex * xl * decay)
                deriv["log_Pd"] = reduce(h - pd * ex * n * x * decay)
                if "kappa" in names:
                    deriv["kappa"] = reduce(-self.p * h)
        elif model == "L0R":
            base = self.meanp.copy()
        else:
            base = np.ones(nw)
        scale_name = "Tc" if model == "T0" else "Mc" if "Mc" in pars else None
        if scale_name:
            coordinate = self.time if scale_name == "Tc" else self.mass
            v = coordinate / pars[scale_name]
            z = np.exp(np.minimum(-v, 7))
            r = np.exp(-z)
            if gradient:
                for key in deriv:
                    deriv[key] *= r
                deriv["log_" + scale_name] = -base * r * z * v
            base *= r
        if gradient:
            return base, np.column_stack([deriv[k] for k in names])
        return base

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
        """Equal-user mean per-shot later RMSE, profiling prefix amplitude analytically."""
        b, db = self.basis(model, theta, gradient=True)
        b, scales = self.scale_basis(b)
        db = db / scales[self.shot_index, None]
        si, cal, score = self.shot_index, self.cal, self.score
        ns = len(self.shots)
        den = np.bincount(si[cal], b[cal] ** 2, minlength=ns)
        amp = self._amplitudes_scaled(b)
        da = np.column_stack([np.divide(
            np.bincount(si[cal], db[cal, j] * (self.q[cal] - 2 * amp[si[cal]] * b[cal]),
                        minlength=ns), den, out=np.zeros(ns), where=den > 0)
            for j in range(db.shape[1])])
        residual = amp[si[score]] * b[score] - self.q[score]
        count = np.bincount(si[score], minlength=ns)
        rmse = np.sqrt(np.bincount(si[score], residual ** 2, minlength=ns) / count)
        value = self.shot_weight @ rmse
        dr = da[si[score]] * b[score, None] + amp[si[score], None] * db[score]
        weight = self.shot_weight / (count * np.maximum(rmse, 1e-12))
        jac = (residual * weight[si[score]]) @ dr
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
    shot = Shot("query", "query", [*early_windows, *later_windows], {})
    design = Design([shot])
    b = design.basis(model["model"], encode(model["model"], model["parameters"]))
    scale = np.max(np.abs(b[:len(early_windows)]))
    scale = scale if scale > 0 else 1.0
    normalized = b / scale
    a = solve_amplitude([w.flow_g_s for w in early_windows], normalized[:len(early_windows)])
    return a * normalized[len(early_windows):], a / scale


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
    return dict(theta=result.x.tolist(), objective=float(result.fun),
                success=bool(result.success), message=str(result.message),
                evaluations=int(result.nfev), iterations=int(result.nit),
                core_hours=(time.process_time() - started) / 3600)


def fitted_model(model, params, metadata=None, settings=Settings()):
    """Portable scalar-parameter artifact. No individual amplitudes or identifiers."""
    return dict(schema="puckworks.reported-flow.v1", model=model, parameters=params,
                settings=asdict(settings), metadata=metadata or {})


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

    Compare stored GL16 with GL64; sharp pressure intervals additionally use QUADPACK
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
    old = np.bincount(seg_window, np.sum(capacity(pp, n, pd, k) * wt, axis=1))
    sw = wt.sum(axis=1)
    new_nodes, new_weights = np.polynomial.legendre.leggauss(64)
    frac = (new_nodes + 1) / 2
    reference = np.zeros(len(p0))
    for a in range(0, len(p0), chunk_size):
        b = min(a + chunk_size, len(p0))
        pressures = p0[a:b, None] + (p1[a:b] - p0[a:b])[:, None] * frac
        reference[a:b] = capacity(np.maximum(pressures, 0), n, pd, k) @ (new_weights / 2)
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
        scale = float(max(capacity(left, n, pd, k), capacity(right, n, pd, k),
                          capacity(peak, n, pd, k) if peak is not None and left < peak < right else 0))
        if scale == 0:
            reference[i] = 0
            continue
        points = sorted(set(((levels - left) / (right - left)).tolist()))
        integral, error = quad(lambda u: float(capacity(left + u * (right - left), n, pd, k)) / scale,
                               0, 1, points=points, epsabs=1e-11, epsrel=1e-11, limit=200)
        if error > 1e-8:
            raise RuntimeError("Independent quadrature reference unresolved")
        reference[i] = scale * integral
    new = np.bincount(seg_window, sw * reference)
    if "Mc" in pars:
        mass = np.array([w.mass_g for w in windows])
        recovery = np.exp(-np.exp(np.minimum(-mass / pars["Mc"], 7)))
        old *= recovery
        new *= recovery
    si = np.repeat(np.arange(len(shots)), [len(s.windows) for s in shots])
    cal = np.array([w.role == "calibration" for w in windows])
    maximum = np.zeros(len(shots))
    np.maximum.at(maximum, si[cal], new[cal])
    denominator = np.maximum(new, 1e-12 * maximum[si])
    relative = np.divide(np.abs(new - old), denominator, out=np.zeros_like(new), where=denominator > 0)
    error = float(np.max(relative))
    return dict(passed=bool(error <= 1e-5), maximum_relative_error=error,
                adaptive_intervals=int(sharp.sum()), windows=len(windows))

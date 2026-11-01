"""Owner-approved C3a diagnostics. Python only; parent evidence stays read-only.

capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED;
TARGET_EXPOSED. Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0.
The four flow screens are in-sample diagnostics, with no bootstrap or grades.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import brentq, least_squares, minimize_scalar
from scipy.signal import savgol_filter

from . import pressure_peak_stage_c2 as C2

C1, C0, A, B = C2.C1, C2.C0, C2.A, C2.B
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C3A"
CLAIM = C1.CLAIM
DETECTOR_READING = (
    "If the flow criterion is the last to become true for a majority of the "
    "1-bar brews, and the 1-bar mean paired x1-minus-x0.5 onset shift is larger "
    "than at every other condition, the 1-bar onset is treated as "
    "detector-limited and T3-O is carried into C3; otherwise T3-O is dropped. "
    "The x1.5 non-detection of all five 1-bar brews is reported alongside."
)
D_STARTS = ((1., 15., .5), (1.5, 30., 1.), (2., 8., 2.))
R_STARTS = ((1., 15., 1., 1.), (1.5, 30., .5, 10.), (2., 8., 1., 100.))
D_BOUNDS = ((.001, 20.), (.5, 100.), (.0001, 100.))
R_BOUNDS = ((.001, 20.), (.5, 100.), (-5., 5.), (.1, 1000.))


def plain(value):
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [plain(v) for v in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def write_table(rows, path):
    rows = [dict(claim=CLAIM, **plain(row)) for row in rows]
    B.write_csv(path, [{k: json.dumps(v, allow_nan=False) if isinstance(v, (dict, list, bool))
                       else "" if v is None else v for k, v in row.items()} for row in rows])


def read_table(path=OUT / "RESULT_TABLE.csv"):
    result = []
    for row in C2.read_results(path):
        parsed = {}
        for key, value in row.items():
            if not value:
                continue
            try:
                parsed[key] = json.loads(value)
            except (ValueError, TypeError):
                parsed[key] = value
        result.append(parsed)
    return result


class Budget(C0.Deadline):
    """Persist every completed or interrupted attempt against the same wall cap."""
    def __init__(self, work):
        self.work = Path(work)
        self.work.mkdir(parents=True, exist_ok=True)
        self.path = self.work / "runtime.json"
        self.records = json.loads(self.path.read_text()) if self.path.exists() else []
        self.prior = sum(r["seconds"] for r in self.records)
        self.started = time.monotonic()
        super().__init__(self.started + max(0., 7200. - self.prior))

    @property
    def cumulative(self):
        return self.prior + time.monotonic() - self.started

    def finish(self, status):
        self.records.append(dict(seconds=time.monotonic()-self.started, status=status))
        self.path.write_text(json.dumps(self.records, indent=2) + "\n")


@contextmanager
def timed_attempt(work):
    budget = Budget(work)
    status = "interrupted"
    try:
        budget.check()
        yield budget
        status = "complete"
    finally:
        budget.finish(status)


def condition_weights(condition):
    condition = np.asarray(condition)
    w = np.array([1. / np.sum(condition == p) for p in condition])
    return w / w.sum()


def grouped_rmse(condition, residual):
    if not len(residual):
        return None
    return float(np.mean([np.sqrt(np.mean(residual[condition == p]**2))
                          for p in np.unique(condition)]))


@dataclass
class Context:
    brews: object
    coarse: object
    fine: object
    native: list
    early: np.ndarray
    delays: np.ndarray
    saved: dict
    c2_diagnostics: dict
    cache: dict


def load_context(raw, cache_path):
    """Use C2's saved identity, without EWP reads or parent cache writers."""
    source = next(r for r in C2.read_results() if r["candidate"] == "T2-F")
    saved = json.loads(source["parameters_by_fold"])
    diagnostics = json.loads(source["diagnostics"])
    pairing = diagnostics["pairing"]
    ids, folds = pairing["brew_order"], pairing["brew_folds"]
    if len(ids) != 56 or len(set(ids)) != 56 or any("_alt" in i for i in ids):
        raise ValueError("C2 cohort identity changed")
    data = ROOT / "puckworks/data/waszkiewicz2025"
    traces = {i: [] for i in ids}
    for r in A.read_csv(data / "traces_per_brew.csv"):
        if r["shot_id"] in traces:
            traces[r["shot_id"]].append(r)
    for rows in traces.values():
        rows.sort(key=lambda r: int(r["time_index"]))
        if [int(r["time_index"]) for r in rows] != list(range(1000)):
            raise ValueError("Incomplete packaged trace")
    cond = np.array([float(traces[i][0]["reference_pressure_round__bar"]) for i in ids])
    if folds != [f"HYD-LOCO-{p}" for p in cond] or len(np.unique(cond)) != 11:
        raise ValueError("C2 fold identity changed")
    pressure = np.array([[float(r["pressure__bar"]) for r in traces[i]] for i in ids])
    windows = {(r["shot_id"], r["window"]): float(r["mass_flow_rate__g_per_s"])
               for r in A.read_csv(data / "equilibrium_windows.csv")}
    target = np.array([windows[i, "endpoint_100s"] for i in ids])
    brews = A.Brews(ids, cond, pressure, target, np.linspace(0, 100, 1000), {}, folds, 0.)
    cache_rows = A.read_csv(cache_path)
    cache = {r["brew"]: r for r in cache_rows}
    if len(cache_rows) != 56 or set(cache) != set(ids):
        raise ValueError("Onset cache does not cover exactly the C2 cohort")
    fields = ("delay lower thresholds s", "delay s", "delay upper thresholds s")
    delays = np.array([[float(cache[i][k]) for k in fields] for i in ids])
    native, early = [], []
    for i in ids:
        t, p, m, _ = B.raw_trace(raw / "measurements_time_dependent" / f"{i}.txt")
        clean_t, clean_p, q, _ = B.clean_course(t, p, m)
        baseline_mask = (t >= -2) & (t <= 0)
        baseline = np.median(m[baseline_mask]) if baseline_mask.any() else m[0]
        native.append(dict(t=t, p=np.maximum(p, 0.), clean_t=clean_t, q=q,
                           mass=np.interp(clean_t, t, m)-baseline))
        early.append(float(np.median(clean_p[clean_t <= 2])))
        np.testing.assert_allclose(-t[0], float(cache[i]["stable elapsed from first record s"]),
                                   rtol=1e-12, atol=0)
    early = np.array(early)
    np.testing.assert_allclose(early, pairing["early_pressure_bar"], rtol=1e-12, atol=0)
    coarse = B.retime_course(B.load_course(brews, raw), delays[:, 1])
    fine = B.retime_course(B.load_course(brews, raw, step=.1), delays[:, 1])
    return Context(brews, coarse, fine, native, early, delays, saved, diagnostics, cache)


def first_crossing(t, values, threshold):
    index = np.flatnonzero(values > threshold)
    return float(t[index[0]]) if len(index) else None


def last_criterion(t, mass, flow, onset):
    """Beginnings of the two true runs containing the cached joint interval."""
    j = int(np.searchsorted(t, onset))
    np.testing.assert_allclose(t[j], onset, rtol=1e-12, atol=0)
    witness = {}
    for name, values, threshold in (("flow", flow, .1), ("mass", mass, .5)):
        if not values[j] > threshold:
            raise ValueError("Cached onset fails a strict criterion")
        k = j
        while k > 0 and values[k-1] > threshold:
            k -= 1
        witness[name] = dict(crossing_s=float(t[k]), value=float(values[k]),
                             previous_s=float(t[k-1]) if k else None,
                             previous_value=float(values[k-1]) if k else None,
                             threshold=threshold, onset_value=float(values[j]),
                             run_min=float(np.min(values[k:j+1])))
    tf, tm = witness["flow"]["crossing_s"], witness["mass"]["crossing_s"]
    last = "flow" if tf > tm else "mass" if tm > tf else "simultaneous"
    end = j
    while end+1 < len(t) and mass[end+1] > .5 and flow[end+1] > .1:
        end += 1
    if t[end]-t[j] < 2.:
        raise ValueError("Cached onset is not sustained for two seconds")
    return dict(last_criterion=last, criterion_gap_s=abs(tf-tm),
                flow_minus_mass_crossing_s=tf-tm, criterion_witness=witness,
                qualifying_end_s=float(t[end]), flow_at_onset_g_s=float(flow[j]))


def audit_detector(ctx):
    rows = []
    for i, brew in enumerate(ctx.brews.ids):
        n = ctx.native[i]
        row = dict(record_type="detector_brew", brew=brew, condition_bar=ctx.brews.condition[i],
                   Pe_bar=ctx.early[i], endpoint_g_s=ctx.brews.target[i],
                   onset_x05_s=ctx.delays[i, 0], onset_x1_s=ctx.delays[i, 1],
                   onset_x15_s=ctx.delays[i, 2],
                   shift_x1_minus_x05_s=ctx.delays[i, 1]-ctx.delays[i, 0])
        row.update(last_criterion(n["clean_t"], n["mass"], n["q"], ctx.delays[i, 1]))
        row["onset_endpoint_ratio"] = (row["flow_at_onset_g_s"]/row["endpoint_g_s"]
                                       if row["endpoint_g_s"] != 0 else None)
        row["first_flow_crossings_s"] = {str(v): first_crossing(n["clean_t"], n["q"], v)
                                          for v in (.05, .1, .15)}
        row["first_mass_crossings_s"] = {str(v): first_crossing(n["clean_t"], n["mass"], v)
                                          for v in (.25, .5, .75)}
        rows.append(plain(row))
    conditions = []
    for p in np.unique(ctx.brews.condition):
        group = [r for r in rows if r["condition_bar"] == p]
        stats = {}
        fields = ("flow_at_onset_g_s", "endpoint_g_s", "onset_endpoint_ratio", "onset_x05_s",
                  "onset_x1_s", "onset_x15_s", "shift_x1_minus_x05_s", "criterion_gap_s")
        series = {k: [r[k] for r in group] for k in fields}
        for kind in ("flow", "mass"):
            for key in group[0][f"first_{kind}_crossings_s"]:
                series[f"first_{kind}_{key}_s"] = [r[f"first_{kind}_crossings_s"][key] for r in group]
        for field, values in series.items():
            finite = [v for v in values if v is not None]
            stats[field] = dict(detected=len(finite), undetected=len(group)-len(finite),
                                mean=np.mean(finite) if finite else None,
                                median=np.median(finite) if finite else None,
                                minimum=min(finite) if finite else None,
                                maximum=max(finite) if finite else None)
        conditions.append(plain(dict(record_type="detector_condition", condition_bar=p, n=len(group),
            last_counts={k: sum(r["last_criterion"] == k for r in group)
                         for k in ("flow", "mass", "simultaneous")}, statistics=stats)))
    low = conditions[0]
    carry = low["last_counts"]["flow"] > low["n"]/2 and all(
        low["statistics"]["shift_x1_minus_x05_s"]["mean"] >
        c["statistics"]["shift_x1_minus_x05_s"]["mean"] for c in conditions[1:])
    reading = dict(record_type="detector_reading", predeclared_reading=DETECTOR_READING,
                   T3O="carry into C3" if carry else "drop", successor_authorized=False)
    return rows + conditions + [reading]


def onset_fits(ctx, budget):
    result = []
    for scale, column in ((.5, 0), (1.5, 2)):
        for held in [None, *ctx.brews.groups]:
            budget.check()
            fold = "DESCRIPTIVE_ALL" if held is None else ctx.brews.fold[held[0]]
            train = np.isfinite(ctx.delays[:, column])
            if held is not None:
                train &= ctx.brews.condition != ctx.brews.condition[held[0]]
            selected = np.flatnonzero(train)
            w = condition_weights(ctx.brews.condition[train])
            c = ctx.coarse
            fit = C2.fit_t2("onset", c.pressure[train], c.t, c.flow[train], c.mask[train],
                            ctx.early[train], ctx.delays[train, column], w, 1., budget)
            pred = C0.onset_curve(C1.onset_parameters(fit), ctx.early)[0]
            margin = ctx.early - fit["P0_bar"]
            if np.any(margin[train] < C0.EPSILON):
                raise ValueError("Active training onset floor")
            evaluate = np.array([], dtype=int) if held is None else held
            detected_eval = evaluate[np.isfinite(ctx.delays[evaluate, column])]
            saved = ctx.saved[fold]
            details = [dict(brew=ctx.brews.ids[i], condition_bar=ctx.brews.condition[i],
                            Pe_bar=ctx.early[i], observed_onset_s=ctx.delays[i, column],
                            predicted_onset_s=pred[i], margin_bar=margin[i],
                            floor_used=bool(margin[i] < .01), role="training" if train[i] else
                            "held_out" if i in evaluate else "undetected_training")
                       for i in range(56)]
            result.append(plain(dict(record_type="onset_fit", threshold_scale=scale, fold=fold,
                parameters=fit, training_brews=[ctx.brews.ids[i] for i in selected],
                training_weights=w, P0_cap_bar=C2.onset_cap(ctx.early[train]),
                training_floor_uses=int(np.sum(margin[train] < .01)),
                held_out_floor_uses=int(np.sum(margin[evaluate] < .01)),
                training_min_margin_bar=min(margin[train]),
                onset_minimum_bar=fit["P0_bar"]+fit["Pd_bar"],
                training_rmse_s=grouped_rmse(ctx.brews.condition[train], pred[train]-ctx.delays[train,column]),
                held_out_rmse_s=grouped_rmse(ctx.brews.condition[detected_eval],
                                            pred[detected_eval]-ctx.delays[detected_eval,column]),
                held_out_detected=len(detected_eval), held_out_total=len(evaluate),
                plugin_peak_bar=saved["P0_bar"]+fit["Pd_bar"]*np.log1p(saved["Pstar_bar"]/fit["Pd_bar"]),
                plugin_saved_P0f_bar=saved["P0_bar"], plugin_saved_Pstar_bar=saved["Pstar_bar"],
                plugin_label="plug-in only; Pstar would refit", brew_predictions=details)))
            print("ONSET", scale, fold, fit["Pd_bar"], flush=True)
    return result


def threshold_factor(pressure, lam, pd):
    """Exponential-threshold convolution, with its removable singularity."""
    p = np.maximum(np.asarray(pressure, dtype=float), 0.)
    x = p / pd
    if lam == 0:
        return -np.expm1(-x), np.exp(-x)/pd
    z = p*(1/pd-1/lam)
    near = np.abs(z) < 1e-4
    # exprel(z)-1, stable at z=0; sixth-order remainder is negligible here.
    zn = np.where(near, z, 0.)
    rel_minus_one = zn*(.5+zn*(1/6+zn*(1/24+zn*(1/120+zn/720))))
    equal = -np.expm1(-x)-x*np.exp(-x)
    small = x < 1e-3
    xs = np.where(small, x, 0.)
    equal = np.where(small, np.exp(-xs)*xs**2*(.5+xs*(1/6+xs*(1/24+xs*(1/120+xs/720)))), equal)
    h = equal-np.exp(-x)*x*rel_minus_one
    hp = np.exp(-x)*p/(lam*pd)*(1+rel_minus_one)
    if lam != pd:
        e_l, e_d = np.exp(-p/lam), np.exp(-x)
        h = np.where(near, h, -np.expm1(-p/lam)-pd/(lam-pd)*(e_l-e_d))
        hp = np.where(near, hp, (e_l-e_d)/(lam-pd))
    # At low pressure the difference is quadratic, so use the convolution's
    # Taylor series as well. This avoids subtracting two nearly equal O(P) terms.
    small_p = np.maximum(x, p/lam) < .05
    if np.any(small_p):
        xs, ys = x[small_p], (p/lam)[small_p]
        polynomial, previous = np.ones_like(xs), np.zeros_like(xs)
        series, derivative = np.zeros_like(xs), np.zeros_like(xs)
        coefficient = .5
        for n in range(13):
            series += coefficient*polynomial
            derivative += (n+2)*coefficient*polynomial
            polynomial, previous = (xs+ys)*polynomial-xs*ys*previous, polynomial
            coefficient = -coefficient/(n+3)
        h = np.array(h, copy=True)
        hp = np.array(hp, copy=True)
        h[small_p] = xs*ys*series
        hp[small_p] = p[small_p]/(lam*pd)*derivative
    if np.any(h < 0) or not np.isfinite(h).all():
        raise ValueError("Invalid threshold capacity; no numerical floor applied")
    return h, hp


def capacity_d(parameters, pressure):
    a, ps, lam, pd = parameters
    p = np.maximum(np.asarray(pressure), 0.)
    return a*pd*np.exp(-p/ps)*threshold_factor(p, lam, pd)[0]


def mass_flow(capacity, t, mc, interval_on=None):
    """Parent exposure quadrature/inversion; optional restart off-interval gate."""
    capacity = np.asarray(capacity)
    increment = (capacity[..., :-1]+capacity[..., 1:])*np.diff(t)/2
    if interval_on is not None:
        increment = increment*np.asarray(interval_on)
    exposure = np.zeros_like(capacity)
    exposure[..., 1:] = np.cumsum(increment, axis=-1)/mc
    state = A.delivered_state(exposure)
    return capacity*np.exp(-np.exp(-state)), mc*state


@B.njit(cache=True)
def relaxation_native(t, pressure, tau):
    """Exact piecewise-linear forcing, S=0 at the first raw record."""
    state = np.zeros(len(t))
    if tau == 0.:
        return pressure.copy()
    for j in range(1, len(t)):
        h = (t[j]-t[j-1])/tau
        one_minus_e = -np.expm1(-h)
        ramp = (h*(.5+h*(-1/6+h*(1/24-h/120))) if h < 1e-4
                else 1-one_minus_e/h)
        state[j] = (state[j-1]*(1-one_minus_e)+pressure[j-1]*one_minus_e
                    +(pressure[j]-pressure[j-1])*ramp)
    return state


def relaxation_at(t, p, tau, query):
    state = relaxation_native(t, p, tau)
    if tau == 0:
        return np.interp(query, t, p)
    k = np.clip(np.searchsorted(t, query, side="right")-1, 0, len(t)-2)
    dt = np.maximum(0., np.minimum(query, t[-1])-t[k])
    h = dt/tau
    one_minus_e = -np.expm1(-h)
    ramp = np.empty_like(h)
    small = h < 1e-4
    ramp[small] = h[small]*(.5+h[small]*(-1/6+h[small]*(1/24-h[small]/120)))
    ramp[~small] = 1-one_minus_e[~small]/h[~small]
    interpolated = (state[k]*(1-one_minus_e)+p[k]*one_minus_e
                    +(p[k+1]-p[k])*dt/(t[k+1]-t[k])*ramp)
    return np.where(query >= t[-1], state[-1], interpolated)


def capacity_r(parameters, pressure, state, pd):
    a, ps, p0, _ = parameters
    p = np.maximum(np.asarray(pressure), 0.)
    return a*pd*np.exp(-state/ps)*(-np.expm1(-np.maximum(p-p0, 0.)/pd))


def flow_r(parameters, pressure, t, mc, pd, state=None):
    if parameters[3] == 0:
        # The exact limiting branch also preserves the parent's arithmetic.
        return C1.flow_curve([*parameters[:3], pd], pressure, t, mc)[0]
    if state is None:
        state = np.array([relaxation_native(t, p, parameters[3]) for p in pressure])
    return mass_flow(capacity_r(parameters, pressure, state, pd), t, mc)[0]


class FlowEvaluator:
    def __init__(self, ctx, kind, pd, mc):
        self.ctx, self.kind, self.pd, self.mc = ctx, kind, pd, mc
        self.last_tau, self.states = None, {}

    def predict(self, parameters, pressure, t, grid_name):
        if self.kind == "D":
            pd = parameters[3] if len(parameters) == 4 else self.pd
            return mass_flow(capacity_d([*parameters[:3], pd], pressure), t, self.mc)[0]
        tau = parameters[3]
        if tau != self.last_tau:
            self.states, self.last_tau = {}, tau
        if grid_name not in self.states:
            self.states[grid_name] = np.array([relaxation_at(n["t"], n["p"], tau, t)
                                                for n in self.ctx.native])
        return flow_r(parameters, pressure, t, self.mc, self.pd, self.states[grid_name])


def fit_screen(ctx, name, kind, pd, budget, free_pd=False):
    bounds = list(D_BOUNDS if kind == "D" else R_BOUNDS)
    starts = list(D_STARTS if kind == "D" else R_STARTS)
    fields = (["a_g_s_bar", "Pstar_bar", "lam_bar"] if kind == "D" else
              ["a_g_s_bar", "Pstar_bar", "P0_bar", "tau_s"])
    if free_pd:
        bounds.append((.1, 100.))
        starts = [(*s, d) for s, d in zip(starts, (3., 2., 6.))]
        fields.append("Pd_bar")
    logarithmic = np.array([k != "P0_bar" for k in fields])

    def coordinates(p):
        z = np.array(p, dtype=float)
        z[logarithmic] = np.log(z[logarithmic])
        return z

    def physical(z):
        p = z.copy()
        p[logarithmic] = np.exp(p[logarithmic])
        return p

    lower, upper = [coordinates([b[j] for b in bounds]) for j in (0, 1)]
    mc = ctx.saved["DESCRIPTIVE_ALL"]["Mc_fixed_g"]
    evaluator = FlowEvaluator(ctx, kind, pd, mc)
    c = ctx.coarse
    weights = condition_weights(ctx.brews.condition)
    trace_weight = np.sqrt(weights[:, None]*c.mask/c.mask.sum(axis=1)[:, None])

    def residual(z):
        budget.check()
        predicted = evaluator.predict(physical(z), c.pressure, c.t, "coarse")
        return ((predicted-c.flow)*trace_weight).ravel()

    fits, records = [], []
    for start in starts:
        fit = least_squares(residual, np.clip(coordinates(start), lower+1e-10, upper-1e-10),
                            bounds=(lower, upper), x_scale="jac", ftol=1e-8, xtol=1e-8,
                            gtol=1e-8, max_nfev=500)
        fits.append(fit)
        records.append(dict(start=list(start), parameters=dict(zip(fields, physical(fit.x))),
                            objective_sum_squares=2*fit.cost, success=fit.success,
                            nfev=fit.nfev, message=fit.message,
                            bound_hits=[f for f, hit in zip(fields, fit.active_mask) if hit]))
    valid = [f for f in fits if f.success and np.isfinite(f.fun).all()]
    if not valid:
        best = min(fits, key=lambda r: r.cost)
        retry = least_squares(residual, best.x, bounds=(lower, upper), method="dogbox",
                              x_scale="jac", ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500)
        records.append(dict(start="dogbox fallback", parameters=dict(zip(fields, physical(retry.x))),
                            objective_sum_squares=2*retry.cost, success=retry.success,
                            nfev=retry.nfev, message=retry.message))
        if not retry.success or not np.isfinite(retry.fun).all():
            raise RuntimeError(name + ": all starts and fallback failed")
        valid = [retry]
    best = min(valid, key=lambda r: r.cost)
    p = physical(best.x)
    params = dict(zip(fields, p))
    if not free_pd:
        params["Pd_bar"] = pd
    params["Mc_fixed_g"] = mc
    proximity = np.minimum(best.x-lower, upper-best.x)/(upper-lower)
    objectives = np.array([r["objective_sum_squares"] for r in records])
    disagreement = bool(np.max(objectives)-np.min(objectives) > 1e-6*max(1., 2*best.cost))
    tau_spread = None
    if kind == "R":
        taus = [r["parameters"]["tau_s"] for r in records]
        tau_spread = max(taus)/min(taus)-1
        disagreement |= tau_spread > .1
    row = dict(record_type="screen", candidate=name, model=kind, parameters=params,
               parameter_count=len(fields), eligibility="EXPLORATORY" if len(fields) == 4 else "DIAGNOSTIC",
               bounds=dict(zip(fields, bounds)), starts=records, start_disagreement=disagreement,
               tau_relative_start_spread=tau_spread,
               bound_hits=[f for f, hit, near in zip(fields, best.active_mask, proximity) if hit or near <= 1e-6],
               objective_sum_squares=2*best.cost,
               plugin_label="plug-in only; Pd comes from a sensitivity detection, not the primary onset target"
               if name == "T3-D x0.5 Pd" else None)
    print("SCREEN", name, plain(params), "J", 2*best.cost, flush=True)
    return row, evaluator, p


def screen_metrics(ctx, row, evaluator, parameters):
    q = evaluator.predict(parameters, ctx.coarse.pressure, ctx.coarse.t, "coarse")
    fine = evaluator.predict(parameters, ctx.fine.pressure, ctx.fine.t, "fine")
    endpoint = evaluator.predict(parameters, ctx.brews.pressure, ctx.brews.t, "endpoint")[:, -1]
    mse = ((q-ctx.coarse.flow)**2*ctx.coarse.mask).sum(axis=1)/ctx.coarse.mask.sum(axis=1)
    fine_mse = ((fine-ctx.fine.flow)**2*ctx.fine.mask).sum(axis=1)/ctx.fine.mask.sum(axis=1)
    weights = condition_weights(ctx.brews.condition)
    np.testing.assert_allclose(np.sum(weights*mse), row["objective_sum_squares"], rtol=1e-12, atol=0)
    observed, predicted, pressure = [np.array([v[g].mean() for g in ctx.brews.groups])
                                     for v in (ctx.brews.target, endpoint, ctx.brews.pressure[:, -1])]
    residuals = predicted-observed
    nominal = np.unique(ctx.brews.condition)
    high, low = nominal >= 9., nominal <= 3.5
    onset_pred = np.array([np.interp(d, ctx.fine.t, f) for d, f in zip(ctx.delays[:, 1], fine)])
    parent = C1.flow_curve(C1.flow_parameters(ctx.saved["DESCRIPTIVE_ALL"]),
                           ctx.fine.pressure, ctx.fine.t, evaluator.mc)[0]
    parent_onset = np.array([np.interp(d, ctx.fine.t, f) for d, f in zip(ctx.delays[:, 1], parent)])
    grid, t = C1.GRID, np.arange(0., 100.0001, .5)
    cp = np.broadcast_to(grid[:, None], (len(grid), len(t)))
    analytic = None
    if row["model"] == "D":
        pd = row["parameters"]["Pd_bar"]
        curve = mass_flow(capacity_d([*parameters[:3], pd], cp), t, evaluator.mc)[0][:, -1]
        ps, lam = parameters[1:3]
        def stationary(p):
            h, hp = threshold_factor(p, lam, pd)
            return float(ps*hp-h)
        analytic = brentq(stationary, 1e-5, 10000., xtol=1e-12)
        row.update(P0_eff_bar=-pd*np.log1p(-lam/pd) if lam < pd else None,
                   lam_Pd_relative_gap=abs(lam-pd)/pd,
                   lam_near_Pd=bool(abs(lam-pd)/pd < 1e-4))
    else:
        curve = flow_r(parameters, cp, t, evaluator.mc, evaluator.pd)[:, -1]
    row.update(objective_fine=np.sum(weights*fine_mse), conditions_bar=nominal,
               condition_endpoint_predicted_g_s=predicted, condition_endpoint_observed_g_s=observed,
               condition_endpoint_line_pressure_bar=pressure, condition_residuals_g_s=residuals,
               low_bias_g_s=residuals[low].mean(), low_mean_absolute_residual_g_s=np.abs(residuals[low]).mean(),
               slope_ge9_g_s_bar=A.slope(pressure[high], predicted[high]),
               analytic_capacity_peak_bar=analytic, flow_peak_bar=float(grid[np.argmax(curve)]),
               constant_pressure_grid_bar=grid, constant_pressure_endpoint_g_s=curve,
               onset_flow_g_s=[onset_pred[g].mean() for g in ctx.brews.groups],
               T2F_onset_flow_g_s=[parent_onset[g].mean() for g in ctx.brews.groups],
               onset_flow_difference_g_s=[(onset_pred-parent_onset)[g].mean() for g in ctx.brews.groups],
               brew_metrics=[dict(brew=b, condition_bar=c, weight=w, trace_mse=m, fine_trace_mse=f,
                                  predicted_endpoint_g_s=e, observed_endpoint_g_s=o)
                             for b, c, w, m, f, e, o in zip(ctx.brews.ids, ctx.brews.condition, weights,
                                                           mse, fine_mse, endpoint, ctx.brews.target)])
    return plain(row)


def replay_parent(ctx):
    saved = ctx.saved["DESCRIPTIVE_ALL"]
    params, mc = C1.flow_parameters(saved), saved["Mc_fixed_g"]
    c = ctx.coarse
    q = C1.flow_curve(params, c.pressure, c.t, mc)[0]
    mse = ((q-c.flow)**2*c.mask).sum(axis=1)/c.mask.sum(axis=1)
    weights = condition_weights(ctx.brews.condition)
    objective = float(np.sum(weights*mse))
    np.testing.assert_allclose(objective, saved["objective_sum_squares"], rtol=1e-12, atol=0)
    q0 = flow_r([*params[:3], 0.], c.pressure, c.t, mc, params[3])
    np.testing.assert_allclose(q0, q, rtol=1e-12, atol=0)
    fine = C1.flow_curve(params, ctx.fine.pressure, ctx.fine.t, mc)[0]
    fine_mse = ((fine-ctx.fine.flow)**2*ctx.fine.mask).sum(axis=1)/ctx.fine.mask.sum(axis=1)
    take = [np.flatnonzero(ctx.brews.condition == p)[0] for p in (6., 13.)]
    return plain(dict(record_type="T2F_replay", parameters=saved,
        saved_objective=saved["objective_sum_squares"], recomputed_objective=objective,
        objective_fine=np.sum(weights*fine_mse), weights=weights, brew_trace_mse=mse,
        brew_fine_trace_mse=fine_mse, mask_count=c.mask.sum(axis=1), fit_step_s=.5, report_step_s=.1,
        fit_times_s=c.t, clean_end_s=c.ends, primary_onset_s=ctx.delays[:, 1],
        tau0_max_abs_error=np.max(np.abs(q0-q)), replay_rtol=1e-12,
        numerical_fixture=dict(t=c.t[:31], pressure=c.pressure[take, :31],
                               reference_flow=q[take, :31], mc=mc, parameters=params)))


def ols_record(t, y):
    """C1's centered polyfit, plus sufficient statistics for independent CI."""
    centered = t-t.mean()
    slope = float(np.polynomial.polynomial.polyfit(centered, y, 1)[1])
    return dict(n=len(t), time_window_s=[float(t[0]), float(t[-1])],
                sum_centered_t_squared=float(np.dot(centered, centered)),
                sum_centered_t_y=float(np.dot(centered, y-y.mean())), slope=slope)


def restart_observations(path, saved):
    records = [(i+1, json.loads(line)) for i, line in enumerate(path.read_text().splitlines()) if line.strip()]
    lines = np.array([i for i, _ in records])
    t = np.array([r["t"]/1000 for _, r in records])
    p = np.array([r["p2"]/100 for _, r in records])
    mass = np.array([r["m"] for _, r in records])
    on = p > 6.
    edges = np.r_[0, np.flatnonzero(on[1:] != on[:-1])+1, len(on)]
    first_on = np.flatnonzero(on)[0]
    baseline = float(np.median(mass[:first_on])) if first_on else float(mass[0])
    rows, windows = [], []
    flow_count = 0
    for index, (start, stop) in enumerate(zip(edges[:-1], edges[1:])):
        use = np.arange(start, stop)
        duration = t[stop-1]-t[start]
        row = dict(record_type="restart_episode", episode=index+1, flowing=bool(on[start]),
                   source_lines=[int(lines[start]), int(lines[stop-1])], sample_count=len(use),
                   start_s=t[start], end_s=t[stop-1], duration_s=duration,
                   pressure_median_bar=np.median(p[use]), pressure_min_bar=np.min(p[use]),
                   baseline_g=baseline, mass_start_relative_g=mass[start]-baseline,
                   mass_end_relative_g=mass[stop-1]-baseline,
                   mass_change_g=mass[stop-1]-mass[start],
                   mean_mass_slope_g_s=(mass[stop-1]-mass[start])/duration if duration else None)
        if on[start]:
            flow_count += 1
            row["flow_episode"] = flow_count
            if duration >= 5.:
                last = use[t[use] >= t[stop-1]-5.]
                windows.append(last)
                stats = ols_record(t[last], mass[last])
                row.update(last5_stats=stats, last5_mass_slope_g_s=stats["slope"])
            else:
                row["last5_unavailable_reason"] = "episode shorter than five seconds"
            if flow_count > 1 and len(use) > 32:
                flow = savgol_filter(np.gradient(mass[use], t[use]), 31, 1)
                stats = ols_record(t[use][15:-15], flow[15:-15])
                row.update(within_flow_stats=stats, within_flow_slope_g_s_s=stats["slope"])
            elif flow_count > 1:
                row["within_flow_unavailable_reason"] = "insufficient interior smoothing support"
        rows.append(plain(row))
    slopes = [r["last5_mass_slope_g_s"] for r in rows if "last5_mass_slope_g_s" in r]
    np.testing.assert_allclose(slopes, [e["flow_g_s"] for e in saved["episodes"]], rtol=1e-12, atol=0)
    for row in rows:
        if "last5_mass_slope_g_s" in row:
            row["observed_ratio"] = row["last5_mass_slope_g_s"]/slopes[0]
    return rows, dict(t=t, p=p, on=on, windows=windows)


def restart_prediction(history, parameters, pd, mc, off_state):
    t, p, on = history["t"], history["p"], history["on"]
    forcing = np.where(on, p, 0.) if off_state == "zero" else p
    state = relaxation_native(t, forcing, parameters[3])
    capacity = np.where(on, capacity_r(parameters, p, state, pd), 0.)
    q, mass = mass_flow(capacity, t, mc, interval_on=on[:-1] & on[1:])
    stats = [ols_record(t[w], mass[w]) for w in history["windows"]]
    slopes = np.array([s["slope"] for s in stats])
    ratios = slopes[1:]/slopes[0]
    return dict(slopes=slopes, ratios=ratios, stats=stats, state=state, mass=mass, flow=q)


def needed_tau(history, screen, budget, target):
    params = screen["parameters"]
    fixed = [params[k] for k in ("a_g_s_bar", "Pstar_bar", "P0_bar")]
    pd, mc = params["Pd_bar"], params["Mc_fixed_g"]
    rows = []
    for scenario in ("zero", "line"):
        def ratios(logtau):
            budget.check()
            result = restart_prediction(history, [*fixed, np.exp(logtau)], pd, mc, scenario)
            return np.array([min(result["ratios"]), max(result["ratios"])])
        grid = np.linspace(np.log(.1), np.log(1000.), 401)
        profile = np.array([ratios(z) for z in grid])
        roots, envelopes = [], []
        for k, goal in enumerate(target):
            solutions = []
            for j in range(len(grid)-1):
                left, right = profile[j, k]-goal, profile[j+1, k]-goal
                if left*right < 0 or left == 0:
                    z = brentq(lambda v: ratios(v)[k]-goal, grid[j], grid[j+1], xtol=1e-12)
                    solutions.append(dict(tau_s=float(np.exp(z)), predicted_ratio=ratios(z)[k],
                                          bracket_tau_s=np.exp(grid[j:j+2]),
                                          bracket_ratios=profile[j:j+2, k]))
            # Bound extrema between log-grid nodes, including nonmonotonic gain.
            candidates = [(grid[0], profile[0, k]), (grid[-1], profile[-1, k])]
            for j in range(1, len(grid)-1):
                for sign in (-1., 1.):
                    if sign*profile[j, k] <= min(sign*profile[j-1, k], sign*profile[j+1, k]):
                        opt = minimize_scalar(lambda v: sign*ratios(v)[k],
                                              bounds=(grid[j-1], grid[j+1]), method="bounded",
                                              options={"xatol": 1e-10})
                        candidates.append((opt.x, ratios(opt.x)[k]))
            lo, hi = min(candidates, key=lambda r: r[1]), max(candidates, key=lambda r: r[1])
            envelopes.append(dict(minimum_ratio=lo[1], maximum_ratio=hi[1],
                                  minimum_at_tau_s=np.exp(lo[0]), maximum_at_tau_s=np.exp(hi[0])))
            roots.append(dict(target_ratio=goal, extremum="minimum" if k == 0 else "maximum",
                              solutions=solutions, status="solutions" if solutions else "unattainable within bounds"))
        all_roots = [r["tau_s"] for group in roots for r in group["solutions"]]
        complete = all(group["solutions"] for group in roots)
        needed_range = [min(all_roots), max(all_roots)] if complete else None
        tau = params["tau_s"]
        identified = "tau_s" not in screen["bound_hits"] and not screen["start_disagreement"]
        overlaps = bool(needed_range is not None and needed_range[0] <= tau <= needed_range[1])
        fitted = restart_prediction(history, [*fixed, tau], pd, mc, scenario)
        pause = ~history["on"]
        rows.append(plain(dict(record_type="restart_replay", off_state=scenario,
            pause_interpretation="q=0; S tracks off-state line pressure: bound, not a model of the pause"
            if scenario == "line" else "q=0; S relaxes toward zero puck pressure",
            parameters_fixed=params, tau_identified=identified, fitted_tau_s=tau,
            fitted_last5_slopes_g_s=fitted["slopes"], fitted_last5_stats=fitted["stats"],
            fitted_ratios=fitted["ratios"], needed_tau=roots, attainable_ratio_envelopes=envelopes,
            needed_tau_range_s=needed_range, fitted_tau_overlaps_needed=overlaps,
            reading="traces do not identify tau; only needed tau interpreted" if not identified else
            "one time constant serves traces and restart" if overlaps else "one time constant does not serve traces and restart",
            profile_tau_s=np.exp(grid), profile_min_max_ratios=profile,
            pause_max_abs_predicted_flow=float(np.max(np.abs(fitted["flow"][pause]))),
            pause_max_abs_mass_increment=float(np.max(np.abs(np.diff(fitted["mass"])[pause[:-1] & pause[1:]]))))))
    return rows


def numerical_checks(ctx):
    """Small serialized fixtures, with expected values from independent limits."""
    saved = ctx.saved["DESCRIPTIVE_ALL"]
    pd, mc = saved["Pd_bar"], saved["Mc_fixed_g"]
    p = np.array([0., 1e-6, .01, 1., 6., 13.])
    h, hp = threshold_factor(p, pd, pd)
    t = np.array([-4., -2., 0., 1., 5., 20.])
    pressure = np.array([0., 2., 5., 6., 9., 9.])
    tau = 7.
    state = relaxation_native(t, pressure, tau)
    constant = np.full(len(t), 8.)
    constant_state = relaxation_native(t, constant, tau)
    np.testing.assert_allclose(constant_state, 8*(-np.expm1(-(t-t[0])/tau)), rtol=1e-12, atol=0)
    tiny = capacity_d([1.2, 12., 1e-14, pd], p)
    limit = 1.2*pd*np.exp(-p/12)*(-np.expm1(-p/pd))
    np.testing.assert_allclose(tiny, limit, rtol=2e-8, atol=1e-14)
    return plain(dict(record_type="numerical_checks", pd=pd, mc=mc, pressure=p,
        equal_lambda_factor=h, equal_lambda_derivative=hp, zero_lambda_capacity=limit,
        tiny_lambda_capacity=tiny, lambda_sides=[threshold_factor(p, pd*(1+s*1e-8), pd)[0]
                                                for s in (-1, 1)],
        ramp_fixture=dict(t=t, pressure=pressure, tau=tau, state=state,
                          constant_pressure=8., constant_state=constant_state)))


def source_hashes(raw, cache, ids):
    paths = [ROOT / f"puckworks/analysis/pressure_peak_stage_{stage}.py" for stage in ("a", "b0", "c0", "c1", "c2")]
    paths += [ROOT / f"docs/research/PRESSURE_PEAK_STAGE_{stage}/RESULT_TABLE.csv" for stage in ("C0", "C1", "C2")]
    paths += [ROOT / f"puckworks/data/waszkiewicz2025/{name}.csv" for name in ("traces_per_brew", "equilibrium_windows")]
    paths += [raw / "measurements_time_dependent" / f"{i}.txt" for i in ids]
    paths += [raw / "measurements_brew_restarting/brew_restarting.txt", cache]
    return {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else
            "external/" + str(p.relative_to(raw)) if p.is_relative_to(raw) else "external/onset-cache.csv":
            hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def write_summary(rows, path):
    def selected(kind):
        return [r for r in rows if r["record_type"] == kind]
    detector = selected("detector_condition")
    low = detector[0]
    shift = low["statistics"]["shift_x1_minus_x05_s"]["mean"]
    other_shift = max(c["statistics"]["shift_x1_minus_x05_s"]["mean"] for c in detector[1:])
    reading = selected("detector_reading")[0]
    onset = [r for r in selected("onset_fit") if r["fold"] == "DESCRIPTIVE_ALL"]
    replay = selected("T2F_replay")[0]
    screens = selected("screen")
    relaxation = next(r for r in screens if r["candidate"] == "T3-R")
    taus = [s["parameters"]["tau_s"] for s in relaxation["starts"]]
    restart = selected("restart_replay")
    episodes = selected("restart_episode")
    flows = [r for r in episodes if r["flowing"]]
    pauses = [r for r in episodes[1:-1] if not r["flowing"]]
    elapsed = selected("provenance")[0]["cumulative_wall_seconds"]
    text = ["# PRESSURE-PEAK C3a: diagnostics", "", "**"+CLAIM+".** Ungraded; 56 brews, 11 conditions.", "",
        f"Flow became true last in {low['last_counts']['flow']}/{low['n']} one-bar brews, "
        f"versus zero in every other condition. Their mean x1-minus-x0.5 onset shift was {shift:.3f} s "
        f"(largest other condition {other_shift:.3f} s). The pre-declared reading is to "
        f"**T3-O: {reading['T3O']}**. All five one-bar x1.5 onsets were undetected. "
        "This supports a detector-limited one-bar onset, not an identified physical onset law.", "",
        "The x0.5 and x1.5 onset point fits give (Pd, P0, P0+Pd) = "
        + "; ".join(f"({r['parameters']['Pd_bar']:.3f}, {r['parameters']['P0_bar']:.3f}, "
                     f"{r['onset_minimum_bar']:.3f}) bar" for r in onset) +
        ". The x1.5 fit loses all one-bar targets and pins P0 at -5 bar; all twelve x1.5 fits "
        "hit a bound (eleven P0, one t0). The x0.5 fold holding out 1 bar also pins P0 at -5 bar. "
        "No training or held-out onset floors were active. Plug-in peaks keep saved flow parameters "
        "and do not replace flow refitting.", "", "## Screens", "",
        f"**T2-F objective replay first:** saved {replay['saved_objective']:.15g}; recomputed "
        f"{replay['recomputed_objective']:.17g}, agreeing at rtol=1e-12. This checks the C2 mask/grid "
        "before comparisons. In-sample screens can mislead and do not replace LOCO + refits.", "",
        "| Screen | Objective | 100-s flow peak, bar | Low-pressure signed bias, g/s |",
        "|---|---:|---:|---:|"]
    text += [f"| {r['candidate']} | {r['objective_sum_squares']:.9f} | {r['flow_peak_bar']:.2f} | "
             f"{r['low_bias_g_s']:+.3f} |" for r in screens]
    text += ["", "All T3-D objectives are worse than T2-F. The x0.5-Pd screen is plug-in only: "
        "Pd comes from a sensitivity detection, not the primary onset target. The free-Pd screen "
        "converges close to lam=Pd, requiring the series limit; P0_eff is undefined on its lam>=Pd side. "
        "No flow-screen parameter is bound-pinned and starts do not disagree under the declared checks.", "",
        f"T3-R fits tau={relaxation['parameters']['tau_s']:.4f} s; its three starts give "
        f"{min(taus):.5f} to {max(taus):.5f} s. The objective reduction is only "
        f"{replay['saved_objective']-relaxation['objective_sum_squares']:.2g}. "
        "Predicted flow at observed onset differs from T2-F by at most "
        f"{max(abs(v) for v in relaxation['onset_flow_difference_g_s']):.4f} g/s across conditions. "
        "Tau=0 replays T2-F at rtol=1e-12.", "", "## Restart", "",
        "Observed last-five-second slopes rise in order: "
        + ", ".join(f"{r['last5_mass_slope_g_s']:.3f}" for r in flows) + " g/s. "
        "Four of five post-restart segments decline slightly within the segment, but the successive "
        "levels ratchet upward instead of returning to the first level. Under the pre-declared reading, "
        "this points toward an irreversible change or mixed behavior, not a sufficient reversible lag. "
        f"The five intervening pauses add {min(r['mass_change_g'] for r in pauses):.3f} to "
        f"{max(r['mass_change_g'] for r in pauses):.3f} g "
        f"({min(r['mean_mass_slope_g_s'] for r in pauses):.3f} to "
        f"{max(r['mean_mass_slope_g_s'] for r in pauses):.3f} g/s).", "",
        "The replay uses q = 0 in pauses. In the line-pressure scenario, S tracks off-state line pressure "
        "while q = 0, which is a bound, not a model of the pause. Both fitted replays give only "
        "about 1.014 to 1.022 times the first slope. No tau in [0.1,1000] s reaches either observed "
        "ratio, 1.747 or 2.349. The largest attainable minimum/maximum restart ratios are "
        f"{restart[0]['attainable_ratio_envelopes'][0]['maximum_ratio']:.3f}/"
        f"{restart[0]['attainable_ratio_envelopes'][1]['maximum_ratio']:.3f} (zero off-state) and "
        f"{restart[1]['attainable_ratio_envelopes'][0]['maximum_ratio']:.3f}/"
        f"{restart[1]['attainable_ratio_envelopes'][1]['maximum_ratio']:.3f} (line off-state). "
        "One time constant does not serve traces and this qualitative restart record.", "",
        f"Cumulative analysis/check time through output: {elapsed:.2f} s; serial, one BLAS thread, "
        "two-hour cap. [Full brew/fold/condition/episode results and CI fixtures](RESULT_TABLE.csv). "
        "Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Diagnostics are ready for owner review. "
        "C3 is not authorized.", ""]
    path.write_text("\n".join(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--onset-cache", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.work.resolve().is_relative_to(ROOT):
        raise ValueError("Runtime ledger/checkpoints must be outside the checkout")
    args.out.mkdir(parents=True, exist_ok=True)
    with timed_attempt(args.work) as budget:
        ctx = load_context(args.raw, args.onset_cache)
        hashes = source_hashes(args.raw, args.onset_cache, ctx.brews.ids)
        rows = audit_detector(ctx)
        replay = replay_parent(ctx)
        rows.append(replay)
        print("T2F_REPLAY", replay["saved_objective"], replay["recomputed_objective"], flush=True)
        onsets = onset_fits(ctx, budget)
        rows.extend(onsets)
        pd = ctx.saved["DESCRIPTIVE_ALL"]["Pd_bar"]
        pd_half = next(r["parameters"]["Pd_bar"] for r in onsets
                       if r["fold"] == "DESCRIPTIVE_ALL" and r["threshold_scale"] == .5)
        for name, kind, fixed, free in (("T3-D primary Pd", "D", pd, False),
                                       ("T3-D free Pd", "D", pd, True),
                                       ("T3-D x0.5 Pd", "D", pd_half, False),
                                       ("T3-R", "R", pd, False)):
            row, evaluator, parameters = fit_screen(ctx, name, kind, fixed, budget, free)
            rows.append(screen_metrics(ctx, row, evaluator, parameters))
            write_table(rows, args.out / "RESULT_TABLE.csv")
        restart_rows, history = restart_observations(
            args.raw / "measurements_brew_restarting/brew_restarting.txt", ctx.c2_diagnostics["restart"])
        rows.extend(restart_rows)
        relaxation = next(r for r in rows if r.get("candidate") == "T3-R")
        rows.extend(needed_tau(history, relaxation, budget, ctx.c2_diagnostics["restart"]["observed_factor_range"]))
        rows.append(numerical_checks(ctx))
        if hashes != source_hashes(args.raw, args.onset_cache, ctx.brews.ids):
            raise ValueError("Parent/source inputs changed during execution")
        budget.check()
        rows.append(dict(record_type="provenance", source_sha256=hashes, cumulative_wall_seconds=budget.cumulative,
                         prior_attempt_seconds=budget.prior, execution="serial; one BLAS thread",
                         cap_seconds=7200, python_only=True, refit_count=0))
        write_table(rows, args.out / "RESULT_TABLE.csv")
        write_summary(rows, args.out / "SUMMARY.md")
        print("COMPLETE", budget.cumulative, "seconds", flush=True)


if __name__ == "__main__":
    main()

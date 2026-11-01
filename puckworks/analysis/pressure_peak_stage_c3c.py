"""Owner-approved C3c screen: capability demonstration, not validation.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED. The owner's implementation
authorization follows the two plan fixes at 025ddd7f. Earlier helpers, data,
bounds, starts and interpretation rules remain unchanged. Python only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import brentq, least_squares

from . import pressure_peak_stage_c3a as D
from . import pressure_peak_stage_c3b as O

C2, C1, C0, A, B = D.C2, D.C1, D.C0, D.A, D.B
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C3C"
CLAIM = D.CLAIM
FIX_COMMIT = "025ddd7f75b4baa87ae5bfb88b28a6eaac480630"
PLAN_SHA256 = "5564c0937754c2791ba75886fdd2a281d1f5e74070f53aa85303a07fa8004a6b"
FIELDS = ("a_g_s_bar", "Pstar_bar", "n", "P0_bar")
STARTS = ((1., 15., 1.), (1.5, 30., 2.), (2., 8., 4.))
CONDITIONS = (1., 2., 3.5, 4., 5., 6., 7., 8., 9., 11., 13.)
STANDARD = ("DESCRIPTIVE_ALL", *(f"HYD-LOCO-{p}" for p in CONDITIONS))
OMITTED = ("HYD-LOCO-1.0-OMIT-3.5", "HYD-LOCO-2.0-OMIT-3.5")
LOG_MAX = np.log(np.finfo(float).max)


def read_table(path=OUT / "RESULT_TABLE.csv"):
    return D.read_table(path)


def coordinates(parameters):
    z = np.array(parameters, dtype=float, copy=True)
    z[:2] = np.log(z[:2])
    return z


def physical(z):
    p = np.array(z, dtype=float, copy=True)
    p[:2] = np.exp(p[:2])
    return p


def bounds(form):
    size = 3 if form == "W3" else 4
    return (np.array([np.log(.001), np.log(.5), 1., -5.])[:size],
            np.array([np.log(20.), np.log(100.), np.inf, 5.])[:size])


def start_values(form, saved):
    starts = [list(s) for s in STARTS]
    if form == "W4":
        starts = [s + [0.] for s in starts]
        starts.append([saved["a_g_s_bar"], saved["Pstar_bar"], 1., saved["P0_bar"]])
    return starts


def parameter_record(p, pd, mc):
    return dict(zip(FIELDS, [*p, 0.] if len(p) == 3 else p), Pd_bar=pd, Mc_fixed_g=mc)


def parameters(record, form):
    return np.array([record[k] for k in FIELDS[:3 if form == "W3" else 4]])


def opening(x, n):
    """H, dH/dn and dH/dx; explicit zero and floating-point saturation limits."""
    x = np.asarray(x, dtype=float)
    h, hn, hx = (np.zeros_like(x) for _ in range(3))
    positive = x > 0
    lx = np.log(x[positive])
    with np.errstate(over="ignore"):
        logu = n * lx
    representable = logu < LOG_MAX
    u = np.full_like(lx, np.inf)
    u[representable] = np.exp(logu[representable])
    h[positive] = -np.expm1(-u)
    dn, dx = np.zeros_like(lx), np.zeros_like(lx)
    # exp(logu-u) evaluates u*exp(-u), including u underflow, without inf*0.
    with np.errstate(over="raise", invalid="raise"):
        dn[representable] = np.exp(logu[representable]-u[representable])*lx[representable]
        dx[representable] = np.exp(np.log(n)+(n-1)*lx[representable]-u[representable])
    hn[positive], hx[positive] = dn, dx
    return h, hn, hx


def capacity(p, pressure, pd):
    """Capacity and derivatives in log(a), log(Pstar), n[, P0]."""
    if not np.isfinite(p).all() or p[2] < 1 or pd <= 0:
        raise ValueError("Finite parameters, n>=1 and positive Pd are required")
    a, star, n = p[:3]
    p0 = p[3] if len(p) == 4 else 0.
    pressure = np.maximum(np.asarray(pressure, dtype=float), 0.)
    x = np.maximum(pressure-p0, 0.)/pd
    h, hn, hx = opening(x, n)
    prefactor = a*np.exp(-pressure/star)
    c = prefactor*pd*h
    dc = np.stack((c, c*pressure/star, prefactor*pd*hn, -prefactor*hx), axis=-1)
    return c, dc[..., :len(p)]


def flow(p, pressure, t, pd, mc, jacobian=True):
    """Use the unchanged parent exposure inversion; differentiate its integral."""
    c, dc = capacity(p, pressure, pd)
    q, mass = D.mass_flow(c, t, mc)
    if not jacobian:
        return q, mass, c
    integral = np.zeros_like(dc)
    integral[..., 1:, :] = np.cumsum(
        (dc[..., :-1, :]+dc[..., 1:, :])*np.diff(t)[:, None]/2, axis=-2)
    inner = np.exp(-mass/mc)
    factor = np.exp(-inner)
    jac = dc*factor[..., None] + (q*inner*factor/mc)[..., None]*integral
    return q, jac


def design(conditions, fold):
    conditions = np.asarray(conditions)
    source = fold.split("-OMIT-")[0]
    held = np.zeros(len(conditions), dtype=bool) if source == "DESCRIPTIVE_ALL" else (
        conditions == float(source.removeprefix("HYD-LOCO-")))
    omitted = (conditions == 3.5) if fold in OMITTED else np.zeros(len(conditions), dtype=bool)
    return source, np.flatnonzero(~held & ~omitted), np.flatnonzero(held), np.flatnonzero(omitted)


def trace_mse(q, target, mask):
    return ((q-target)**2*mask).sum(axis=1)/mask.sum(axis=1)


def objective_parts(conditions, mse):
    conditions, mse = np.asarray(conditions), np.asarray(mse)
    w = D.condition_weights(conditions)
    objective = float(w@mse)
    parts = [dict(condition_bar=float(c), n=int(np.sum(conditions == c)),
                  contribution=float(np.sum((w*mse)[conditions == c]))) for c in np.unique(conditions)]
    for row in parts:
        row["share"] = row["contribution"]/objective if objective else None
    return dict(objective=objective, conditions=parts, weights=w, brew_mse=mse)


def zero_capacity(p, pressure, mask, pd, conditions, ids):
    c = capacity(p, pressure, pd)[0]
    p0 = p[3] if len(p) == 4 else 0.
    zero = np.all((c == 0) | ~mask, axis=1)
    structural = np.all((pressure <= p0) | ~mask, axis=1)
    numerical = zero & ~structural
    return dict(total=int(sum(zero)), structural=int(sum(structural)), numerical=int(sum(numerical)),
        brew_ids=[b for b, flag in zip(ids, zero) if flag],
        by_condition={str(float(v)): dict(total=int(sum(zero[conditions == v])),
            structural=int(sum(structural[conditions == v])), numerical=int(sum(numerical[conditions == v])))
            for v in np.unique(conditions)})


def kink_counts(p, pressure, mask, ids):
    p0 = p[3] if len(p) == 4 else 0.
    within = ((np.where(mask, pressure, np.inf).min(axis=1) <= p0) &
              (np.where(mask, pressure, -np.inf).max(axis=1) >= p0))
    segment = (mask[:, 1:] & mask[:, :-1] &
               ((pressure[:, 1:]-p0)*(pressure[:, :-1]-p0) <= 0))
    return dict(P0_bar=float(p0), brews_bracketing=int(sum(within)),
        brew_ids=[b for b, flag in zip(ids, within) if flag],
        segments_bracketing_or_touching=int(segment.sum()),
        exact_coincidences=int(((pressure == p0) & mask).sum()))


class Evaluator:
    def __init__(self, pressure, t, target, mask, conditions, pd, mc, budget):
        self.pressure, self.t, self.target, self.mask = pressure, t, target, mask
        self.pd, self.mc, self.budget = pd, mc, budget
        self.weight = np.sqrt(D.condition_weights(conditions)[:, None]*mask/mask.sum(axis=1)[:, None])
        self.last_z, self.last = None, None

    def __call__(self, z):
        self.budget.check()
        if self.last_z is None or not np.array_equal(self.last_z, z):
            q, jac = flow(physical(z), self.pressure, self.t, self.pd, self.mc)
            value = (((q-self.target)*self.weight).ravel(),
                     (jac*self.weight[..., None]).reshape(-1, len(z)))
            if not all(np.isfinite(v).all() for v in value):
                raise FloatingPointError("Nonfinite residual/Jacobian; no bounds or starts changed")
            self.last_z, self.last = np.array(z, copy=True), value
        return self.last


def finite_difference(evaluate, z, lower, upper, multiplier=1.):
    residual, _ = evaluate(z)
    jac = np.empty((len(residual), len(z)))
    branches = evaluate.pressure > (physical(z)[3] if len(z) == 4 else 0.)
    switches = np.zeros_like(branches, dtype=bool)
    for k in range(len(z)):
        step = multiplier*1e-4*max(1., abs(z[k]))
        lo, hi = z.copy(), z.copy()
        if z[k]-step < lower[k]:
            hi[k] = min(z[k]+step, upper[k])
        elif z[k]+step > upper[k]:
            lo[k] -= step
        else:
            lo[k] -= step
            hi[k] += step
        jac[:, k] = (evaluate(hi)[0]-evaluate(lo)[0])/(hi[k]-lo[k])
        if len(z) == 4:
            switches |= ((evaluate.pressure > physical(lo)[3]) != branches)
            switches |= ((evaluate.pressure > physical(hi)[3]) != branches)
    return jac, int((switches & evaluate.mask).sum())


def jacobian_diagnostic(evaluate, z, lower, upper):
    analytic = evaluate(z)[1]
    full, switches = finite_difference(evaluate, z, lower, upper)
    half, half_switches = finite_difference(evaluate, z, lower, upper, .5)
    norm = float(np.linalg.norm(analytic))
    full_error, half_error = (float(np.linalg.norm(v-analytic)) for v in (full, half))
    difference = float(np.linalg.norm(full-half))
    return dict(analytic_norm=norm, full_absolute_error=full_error, half_absolute_error=half_error,
        full_relative_error=full_error/norm if norm else None,
        half_relative_error=half_error/norm if norm else None,
        half_step_absolute_change=difference, half_step_relative_change=difference/norm if norm else None,
        full_branch_switches=switches, half_branch_switches=half_switches,
        half_step_error_decreases=half_error < full_error)


def log_slope(p, pressure, pd):
    """Derivative of log capacity; its opening term decreases for n>=1."""
    x = (pressure-(p[3] if len(p) == 4 else 0.))/pd
    if x <= 0:
        return np.inf
    logu = p[2]*np.log(x)
    if logu >= LOG_MAX:
        ratio = 0.
    else:
        u = np.exp(logu)
        ratio = np.exp(logu-u)/(-np.expm1(-u)) if u else 1.
    return p[2]/(pd*x)*ratio-1/p[1]


def extrema(p, pd, mc, onset):
    grid = C1.GRID
    q = flow(p, np.repeat(grid[:, None], 2, axis=1), np.array([0., 100.]), pd, mc, False)[0][:, -1]
    p0 = p[3] if len(p) == 4 else 0.
    lower = max(1., np.nextafter(p0, np.inf))
    if log_slope(p, lower, pd) <= 0:
        peak = lower
    elif log_slope(p, 13., pd) >= 0:
        peak = 13.
    else:
        peak = brentq(lambda v: log_slope(p, v, pd), lower, 13., xtol=1e-12)
    index = int(np.argmax(q))
    nominal_ix = [int(np.flatnonzero(grid == c)[0]) for c in CONDITIONS]
    timing = C0.onset_curve(C1.onset_parameters(onset), grid)[0]
    return dict(grid_bar=grid, flow_grid_g_s=q, flow_peak_bar=float(grid[index]),
        analytic_capacity_peak_bar=float(peak), peak_boundary=peak in (1., 13.),
        nominal_peak_bar=CONDITIONS[int(np.argmax(q[nominal_ix]))],
        onset_minimum_bar=float(grid[np.argmin(timing)]),
        analytic_onset_minimum_bar=float(onset["P0_bar"]+onset["Pd_bar"]))


def brew_records(ctx, p, pd, mc, onset, train, held, omitted):
    q, mass, cap = flow(p, ctx.brews.pressure, ctx.brews.t, pd, mc, False)
    fine = flow(p, ctx.fine.pressure, ctx.fine.t, pd, mc, False)[0]
    mse = trace_mse(fine, ctx.fine.flow, ctx.fine.mask)
    trends = (fine*ctx.fine.late_weights).sum(axis=1)
    onsets = C0.onset_curve(C1.onset_parameters(onset), ctx.early)[0]
    records = []
    for i, brew in enumerate(ctx.brews.ids):
        records.append(dict(brew=brew, condition_bar=ctx.brews.condition[i],
            role="training" if i in train else "held_out" if i in held else "omitted",
            endpoint_pressure_bar=ctx.brews.pressure[i, -1], endpoint_observed_g_s=ctx.brews.target[i],
            endpoint_prediction_g_s=q[i, -1], endpoint_residual_g_s=q[i, -1]-ctx.brews.target[i],
            capacity_100_g_s=cap[i, -1], hydraulic_mass_100_g=mass[i, -1],
            memory_multiplier_100=np.exp(-np.exp(-mass[i, -1]/mc)),
            no_memory_plugin_endpoint_g_s=cap[i, -1], trace_mse=mse[i],
            predicted_late_trend_g_s_s=trends[i], observed_late_trend_g_s_s=ctx.fine.observed_trend[i],
            observed_onset_s=ctx.delays[i, 1], predicted_onset_s=onsets[i]))
    return records


def metrics(records):
    if not records:
        return None
    result = O.metrics(records)
    conditions = np.array([r["condition_bar"] for r in records])
    result["condition_trends_g_s_s"] = [float(np.mean([
        r["predicted_late_trend_g_s_s"] for r in records if r["condition_bar"] == c]))
        for c in np.unique(conditions)]
    result["resolved_trends"] = [dict(condition_bar=c, predicted=v,
        observed=float(np.mean([r["observed_late_trend_g_s_s"] for r in records if r["condition_bar"] == c])),
        sign=B.mean_trend_sign(v), matches_rising=B.mean_trend_sign(v) == "POSITIVE")
        for c, v in zip(np.unique(conditions), result["condition_trends_g_s_s"]) if c in (2., 3.5, 4., 5., 6.)]
    return result


def reference_folds(ctx):
    """Reference replay is first; no W3/W4 fits occur here."""
    rows = []
    for fold in (*STANDARD, *OMITTED):
        source, train, held, omitted = design(ctx.brews.condition, fold)
        saved = ctx.saved[source]
        coef, mc, pd = C1.flow_parameters(saved), saved["Mc_fixed_g"], saved["Pd_bar"]
        coarse = C1.flow_curve(coef, ctx.coarse.pressure[train], ctx.coarse.t, mc)[0]
        fine = C1.flow_curve(coef, ctx.fine.pressure[train], ctx.fine.t, mc)[0]
        parts = objective_parts(ctx.brews.condition[train], trace_mse(coarse, ctx.coarse.flow[train], ctx.coarse.mask[train]))
        fine_parts = objective_parts(ctx.brews.condition[train], trace_mse(fine, ctx.fine.flow[train], ctx.fine.mask[train]))
        if fold in STANDARD:
            np.testing.assert_allclose(parts["objective"], saved["objective_sum_squares"], rtol=1e-12, atol=0)
        if fold == "DESCRIPTIVE_ALL":
            np.testing.assert_allclose(parts["objective"], .0719361259858887, rtol=1e-12, atol=0)
            print("T2F_REPLAY_FIRST", saved["objective_sum_squares"], parts["objective"], flush=True)
        p = np.array([coef[0], coef[1], 1., coef[2]])
        np.testing.assert_allclose(flow(p, ctx.coarse.pressure[train], ctx.coarse.t, pd, mc)[0], coarse, rtol=1e-12, atol=0)
        records = brew_records(ctx, p, pd, mc, saved["onset_parameters"], train, held, omitted)
        rows.append(dict(record_type="reference", candidate="T2-F", fold=fold, source_fold=source,
            training_indices=train, held_out_indices=held, omitted_indices=omitted,
            parameters=saved, saved_objective=saved["objective_sum_squares"] if fold in STANDARD else None,
            reference_kind="replay" if fold in STANDARD else "reduced-training plug-in; not refitted",
            objective=parts, fine_objective=fine_parts, brew_predictions=records,
            held_out_metrics=metrics([r for r in records if r["role"] == "held_out"]),
            extrema=extrema(p, pd, mc, saved["onset_parameters"])))
    return D.plain(rows)


class UnresolvedFit(RuntimeError):
    def __init__(self, row):
        super().__init__(f"Unresolved fit: {row['candidate']} {row['fold']}; stop for owner review")
        self.row = row


def fit_fold(ctx, form, fold, reference, budget, work):
    source, train, held, omitted = design(ctx.brews.condition, fold)
    saved, coarse = ctx.saved[source], ctx.coarse
    pd, mc = saved["Pd_bar"], saved["Mc_fixed_g"]
    lower, upper = bounds(form)
    evaluate = Evaluator(coarse.pressure[train], coarse.t, coarse.flow[train], coarse.mask[train],
                         ctx.brews.condition[train], pd, mc, budget)
    ids = [ctx.brews.ids[i] for i in train]
    row = dict(record_type="fit", candidate=form, fold=fold, source_fold=source,
        parameter_count=len(lower), eligibility="EXPLORATORY" if form == "W4" else "DIAGNOSTIC",
        training_indices=train, held_out_indices=held, omitted_indices=omitted, training_brews=ids,
        Pd_fixed_bar=pd, Mc_fixed_g=mc, onset_parameters=saved["onset_parameters"],
        starts=[], fallback=None, status="running")
    attempt_path = work / f"{form}-{fold}-attempts.json"

    def save():
        attempt_path.write_text(json.dumps(D.plain(row), allow_nan=False)+"\n")

    def attempt(start, label, fallback=False):
        z = np.array(start, copy=True) if fallback else np.clip(coordinates(start), lower+1e-10, upper-1e-10)
        p = physical(z)
        record = dict(label=label, original_start_coordinates=np.array(start) if fallback else coordinates(start),
            initial_coordinates=z, initial_parameters=parameter_record(p, pd, mc),
            initial_training_counts=zero_capacity(p, coarse.pressure[train], coarse.mask[train], pd,
                                                   ctx.brews.condition[train], ids))
        if form == "W4" and (fallback or start[2] == 1.):
            record["initial_jacobian_check"] = jacobian_diagnostic(evaluate, z, lower, upper)
        record["initial_kink_counts"] = kink_counts(p, coarse.pressure[train], coarse.mask[train], ids)
        if label == "start-2" and record["initial_training_counts"]["total"]:
            raise RuntimeError("P0=0,n=2 safeguard unexpectedly has zero-capacity training brews")
        if fallback:
            row["fallback"] = record
        else:
            row["starts"].append(record)
        save()
        started = time.monotonic()
        try:
            result = least_squares(lambda v: evaluate(v)[0], z, jac=lambda v: evaluate(v)[1],
                bounds=(lower, upper), method="dogbox" if fallback else "trf", x_scale="jac",
                ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500 if fallback else 500)
        except Exception as exc:
            record.update(success=False, error=f"{type(exc).__name__}: {exc}", wall_seconds=time.monotonic()-started)
            if evaluate.last_z is not None:
                final = physical(evaluate.last_z)
                record.update(final_parameters=parameter_record(final, pd, mc),
                    final_training_counts=zero_capacity(final, coarse.pressure[train], coarse.mask[train], pd,
                                                          ctx.brews.condition[train], ids))
            row["status"] = "unresolved"
            save()
            raise UnresolvedFit(D.plain(row)) from exc
        final = physical(result.x)
        record.update(final_coordinates=result.x, final_parameters=parameter_record(final, pd, mc),
            objective=float(2*result.cost), success=bool(result.success and np.isfinite(result.fun).all()),
            message=result.message, nfev=result.nfev, njev=result.njev, active_mask=result.active_mask,
            wall_seconds=time.monotonic()-started,
            final_training_counts=zero_capacity(final, coarse.pressure[train], coarse.mask[train], pd,
                                                  ctx.brews.condition[train], ids),
            final_kink_counts=kink_counts(final, coarse.pressure[train], coarse.mask[train], ids))
        save()
        return result

    fits = [attempt(start, f"start-{i+1}") for i, start in enumerate(start_values(form, saved))]
    valid = [(i, r) for i, r in enumerate(fits) if r.success and np.isfinite(r.fun).all()]
    if not valid:
        finite = [r for r in fits if np.isfinite(r.cost) and np.isfinite(r.x).all()]
        if finite:
            retry = attempt(min(finite, key=lambda r: r.cost).x, "dogbox fallback", True)
            if retry.success and np.isfinite(retry.fun).all():
                valid = [(len(fits), retry)]
        if not valid:
            row["status"] = "unresolved"
            save()
            raise UnresolvedFit(D.plain(row))
    selected, best = min(valid, key=lambda pair: pair[1].cost)
    p = physical(best.x)
    coarse_q = flow(p, coarse.pressure[train], coarse.t, pd, mc, False)[0]
    fine_q = flow(p, ctx.fine.pressure[train], ctx.fine.t, pd, mc, False)[0]
    parts = objective_parts(ctx.brews.condition[train], trace_mse(coarse_q, coarse.flow[train], coarse.mask[train]))
    fine_parts = objective_parts(ctx.brews.condition[train], trace_mse(fine_q, ctx.fine.flow[train], ctx.fine.mask[train]))
    np.testing.assert_allclose(parts["objective"], 2*best.cost, rtol=1e-12, atol=0)
    records = brew_records(ctx, p, pd, mc, saved["onset_parameters"], train, held, omitted)
    attempts = row["starts"] + ([row["fallback"]] if row["fallback"] else [])
    objectives = [r["objective"] for r in attempts]
    finite_bounds = np.isfinite(upper)
    proximity = np.minimum(best.x[finite_bounds]-lower[finite_bounds], upper[finite_bounds]-best.x[finite_bounds]) / (upper[finite_bounds]-lower[finite_bounds])
    gain = reference["objective"]["objective"]-parts["objective"]
    fine_gain = reference["fine_objective"]["objective"]-fine_parts["objective"]
    row.update(status="complete", parameters=parameter_record(p, pd, mc), selected_start=selected,
        objective=parts, fine_objective=fine_parts, brew_predictions=records,
        training_metrics=metrics([r for r in records if r["role"] == "training"]),
        held_out_metrics=metrics([r for r in records if r["role"] == "held_out"]),
        extrema=extrema(p, pd, mc, saved["onset_parameters"]),
        onset_audit=C2.margin_audit(saved["onset_parameters"], ctx, train, held if len(held) else None),
        onset_bank_training_indices=design(ctx.brews.condition, source)[1],
        jacobian_check=jacobian_diagnostic(evaluate, best.x, lower, upper),
        start_disagreement=max(objectives)-min(objectives) > 1e-6*max(1., 2*best.cost),
        parameter_spreads={k: max(r["final_parameters"][k] for r in attempts)-min(r["final_parameters"][k] for r in attempts)
                           for k in FIELDS[:len(p)]},
        bound_hits=[k for k, active in zip(FIELDS, best.active_mask) if active],
        bound_proximity=[k for k, near in zip(np.array(FIELDS[:len(p)])[finite_bounds], proximity) if near <= 1e-6],
        n_lower_distance=float(p[2]-1), n_lower_active=bool(best.active_mask[2]),
        selected_training_counts=zero_capacity(p, coarse.pressure[train], coarse.mask[train], pd, ctx.brews.condition[train], ids),
        selected_kink_counts=kink_counts(p, coarse.pressure[train], coarse.mask[train], ids),
        coarse_gain_vs_T2F=gain, fine_gain_vs_T2F=fine_gain,
        grid_gain_unresolved=bool(gain > 0 and (fine_gain <= 0 or abs(gain-fine_gain) >= gain)))
    row["plateau_label"] = "possible flat-gradient dependence" if row["selected_training_counts"]["total"] else "none"
    save()
    return D.plain(row)


def input_fixture(ctx):
    return D.plain(dict(record_type="inputs", brew_ids=ctx.brews.ids,
        conditions_bar=ctx.brews.condition, early_pressure_bar=ctx.early,
        observed_onsets_s=ctx.delays[:, 1], clean_ends_s=ctx.coarse.ends,
        fit_times_s=ctx.coarse.t, fit_pressure=ctx.coarse.pressure,
        fit_observed_flow=ctx.coarse.flow, fit_mask=ctx.coarse.mask,
        fine_times_s=ctx.fine.t, fine_pressure=ctx.fine.pressure,
        fine_observed_flow=ctx.fine.flow, fine_mask=ctx.fine.mask,
        late_weights=ctx.fine.late_weights, observed_late_trend=ctx.fine.observed_trend,
        endpoint_times_s=ctx.brews.t, endpoint_pressure=ctx.brews.pressure,
        endpoint_observed_g_s=ctx.brews.target, saved_parameters_by_fold=ctx.saved))


def low_pressure_audit(ctx):
    rows = []
    ma, mb, mc = A.MACHINE
    for i, native in enumerate(ctx.native):
        if ctx.brews.condition[i] not in (1., 2.):
            continue
        t = native["clean_t"][native["clean_t"] <= 100]
        p = np.interp(t, native["t"], native["p"])
        q100, p100 = ctx.brews.target[i], ctx.brews.pressure[i, -1]
        correction = ma*q100*q100+mb*q100+mc
        rows.append(dict(record_type="pressure_audit", brew=ctx.brews.ids[i],
            condition_bar=ctx.brews.condition[i], early_pressure_bar=ctx.early[i],
            endpoint_pressure_bar=p100, min_pressure_bar=float(p.min()), max_pressure_bar=float(p.max()),
            native_times_through_100_s=t, native_pressure_through_100_bar=p,
            endpoint_observed_g_s=q100, machine_coefficients=A.MACHINE,
            basket_correction_bar=correction, basket_endpoint_bar=p100-correction,
            interpretation="derived using observed flow; not an independent pressure measurement or fit input"))
    return D.plain(rows)


def numerical_fixtures(budget):
    t = np.array([0., .5, 1., 2., 5., 12., 40., 100.])
    pressure = np.array([[0., .5, 1., 1.1, 1.4, 2., 2.5, 2.],
                         [2., 3., 4., 5., 7., 9., 11., 13.]])
    pd, mc = 4., 28.7
    cases = []
    for name, p in (("nested", [1.2, 12.2, 1., 1.]),
                    ("smooth", [1.2, 12.2, 2., -.2]),
                    ("zero-threshold", [1.2, 12.2, 2.]),
                    ("sharp", [1.2, 12.2, 30., 0.])):
        p = np.array(p)
        q, jac = flow(p, pressure, t, pd, mc)
        qq, mass, cap = flow(p, pressure, t, pd, mc, False)
        np.testing.assert_allclose(q, qq, rtol=1e-12, atol=0)
        if name == "nested":
            parent, parent_jac = C1.flow_curve([p[0], p[1], p[3], pd], pressure, t, mc)
            np.testing.assert_allclose(q, parent, rtol=1e-12, atol=0)
            np.testing.assert_allclose(jac[..., [0, 1, 3]], parent_jac[..., [0, 1, 2]], rtol=1e-12, atol=0)
        if name == "zero-threshold":
            np.testing.assert_allclose(q, flow([*p, 0.], pressure, t, pd, mc)[0], rtol=1e-12, atol=0)
        evaluator = Evaluator(pressure, t, np.zeros_like(pressure), np.ones_like(pressure, dtype=bool),
                              np.array([1., 2.]), pd, mc, budget)
        diagnostic = jacobian_diagnostic(evaluator, coordinates(p), *bounds("W3" if len(p) == 3 else "W4"))
        if name == "smooth" and not diagnostic["half_step_error_decreases"]:
            raise RuntimeError("Smooth synthetic Jacobian did not improve on halving; stop before fits")
        cases.append(dict(name=name, parameters=p, t=t, pressure=pressure, Pd_bar=pd, Mc_g=mc,
                          q=q, mass=mass, capacity=cap, jacobian=jac, diagnostic=diagnostic))
    large = opening(np.array([0., 1e-200, .5, 1., 2., 1e200]), 4.)
    if not all(np.isfinite(v).all() for v in large):
        raise RuntimeError("Nonfinite large-power fixture; stop before fits")
    return D.plain(dict(record_type="numerical_fixtures", cases=cases,
        large_x=[0., 1e-200, .5, 1., 2., 1e200], large_n=4., large_values=large))


def dependence(standard, omitted, reference):
    baseline = abs(standard-reference)
    change = omitted-standard
    before, after = abs(standard) < abs(reference), abs(omitted) < abs(reference)
    status = ("retained" if after else "lost" if abs(omitted) == abs(reference) else "reversed") if before else (
        "appears after omission" if after else "neither improves")
    return dict(standard_residual_g_s=standard, omitted_residual_g_s=omitted, T2F_residual_g_s=reference,
        baseline_g_s=baseline, change_g_s=change, material=abs(change) > baseline,
        improvement_status=status)


def reading(fits, references):
    rows = []
    for form in ("W3", "W4", "T2-F"):
        selected = [r for r in (references if form == "T2-F" else fits)
                    if r["candidate"] == form and r["fold"] in STANDARD]
        held = [b for r in selected for b in r["brew_predictions"] if b["role"] == "held_out"]
        if len(held) != 56 or len({r["brew"] for r in held}) != 56:
            raise RuntimeError("Ordinary LOCO coverage changed")
        loco = [r for r in selected if r["fold"] != "DESCRIPTIVE_ALL"]
        grid_peaks = [r["extrema"]["flow_peak_bar"] for r in loco]
        analytic_peaks = [r["extrema"]["analytic_capacity_peak_bar"] for r in loco]
        row = dict(record_type="reading", candidate=form, metrics=metrics(held),
            flow_peak_fold_median_bar=float(np.median(grid_peaks)), flow_peak_fold_range_bar=[min(grid_peaks), max(grid_peaks)],
            analytic_peak_fold_median_bar=float(np.median(analytic_peaks)),
            analytic_peak_fold_range_bar=[min(analytic_peaks), max(analytic_peaks)],
            inherited_onset_minimum_median_bar=float(np.median([r["extrema"]["onset_minimum_bar"] for r in loco])),
            successor_authorized=False)
        if form != "T2-F":
            all_form = [r for r in fits if r["candidate"] == form]
            row["n_by_fold"] = {r["fold"]: r["parameters"]["n"] for r in all_form}
            row["P0_by_fold"] = {r["fold"]: r["parameters"]["P0_bar"] for r in all_form}
            row["omission_dependence"] = []
            for h in (1., 2.):
                fold = f"HYD-LOCO-{h}"
                standard = next(r for r in selected if r["fold"] == fold)
                omitted = next(r for r in all_form if r["fold"] == fold+"-OMIT-3.5")
                ref = next(r for r in references if r["fold"] == fold)
                row["omission_dependence"].append(dict(condition_bar=h, **dependence(
                    standard["held_out_metrics"]["endpoint_residuals_g_s"][0],
                    omitted["held_out_metrics"]["endpoint_residuals_g_s"][0],
                    ref["held_out_metrics"]["endpoint_residuals_g_s"][0])))
            descriptive = next(r for r in selected if r["fold"] == "DESCRIPTIVE_ALL")
            without35 = next(r for r in selected if r["fold"] == "HYD-LOCO-3.5")
            row["in_sample_3_5_omission"] = [dict(condition_bar=h,
                descriptive_mean_g_s=float(np.mean([b["endpoint_prediction_g_s"] for b in descriptive["brew_predictions"] if b["condition_bar"] == h])),
                omitted_mean_g_s=float(np.mean([b["endpoint_prediction_g_s"] for b in without35["brew_predictions"] if b["condition_bar"] == h])),
                interpretation="in-sample curves, not the additional held-out tests") for h in (1., 2.)]
            row["both_low_conditions_improve"] = all(abs(d["standard_residual_g_s"]) < abs(d["T2F_residual_g_s"])
                                                       for d in row["omission_dependence"])
            row["start_disagreement_folds"] = [r["fold"] for r in all_form if r["start_disagreement"]]
            row["grid_unresolved_folds"] = [r["fold"] for r in all_form if r["grid_gain_unresolved"]]
        rows.append(row)
    return D.plain(rows)


def comparators():
    fields = ("endpoint_rmse_g_s", "trace_rmse_g_s", "onset_rmse_s", "slope_g_s_bar",
              "low_pressure_bias_g_s", "low_condition_mean_absolute_residual_g_s")
    return [dict(record_type="saved_comparator", candidate=r["candidate"],
        source=r.get("source") or "PRESSURE_PEAK_STAGE_C2/RESULT_TABLE.csv:"+r["candidate"],
        method="saved stage metrics; no refit; not a new objective comparison",
        **{k: float(r[k]) for k in fields if r.get(k)})
        for r in C2.read_results() if r.get("endpoint_rmse_g_s")]


def source_hashes(raw, cache, ids):
    paths = [ROOT / f"puckworks/analysis/pressure_peak_stage_{s}.py"
             for s in ("a", "b0", "c0", "c1", "c2", "c3a", "c3b", "c3c")]
    paths += [OUT / "PLAN.md", C2.OUT / "RESULT_TABLE.csv"]
    paths += [ROOT / f"puckworks/data/waszkiewicz2025/{name}.csv" for name in ("traces_per_brew", "equilibrium_windows")]
    paths += [raw / "measurements_time_dependent" / f"{i}.txt" for i in ids]
    paths.append(cache)
    result = {}
    for path in paths:
        key = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else (
            "external/"+str(path.relative_to(raw)) if path.is_relative_to(raw) else "external/onset-cache.csv")
        result[key] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def write_summary(rows, path):
    fits = [r for r in rows if r["record_type"] == "fit"]
    reads = {r["candidate"]: r for r in rows if r["record_type"] == "reading"}
    refs = [r for r in rows if r["record_type"] == "reference"]
    provenance = next(r for r in rows if r["record_type"] == "provenance")
    replay = next(r for r in refs if r["fold"] == "DESCRIPTIVE_ALL")
    text = ["# PRESSURE-PEAK C3c: low-pressure flow screen", "",
        "**"+CLAIM+".** Ungraded; W4 is exploratory. 56 brews, 11 ordinary LOCO folds, plus two omission fits per form. "
        "All 28 point fits and 98 starts ran; no bootstrap or onset refit.", "",
        f"**T2-F objective replay first:** saved {replay['saved_objective']:.16g}; recomputed "
        f"{replay['objective']['objective']:.17g}. All 12 saved standard-fold objectives agree at rtol=1e-12, atol=0. "
        "The objectives below are unscaled flow losses; joint scales remain 0.437 g/s and 4.534 s.", "",
        "| Form | Full-cohort J | Held-out residual: 1 / 2 / 3.5 bar, g/s | Endpoint / trace RMSE, g/s | Continuous peak, bar | >=9-bar slope, g/s/bar |",
        "|---|---:|---|---|---:|---:|"]
    for form in ("T2-F", "W3", "W4"):
        r, m = reads[form], reads[form]["metrics"]
        full = next(f for f in (refs if form == "T2-F" else fits) if f["candidate"] == form and f["fold"] == "DESCRIPTIVE_ALL")
        residual = " / ".join(f"{v:+.4f}" for v in m["endpoint_residuals_g_s"][:3])
        text.append(f"| {form} | {full['objective']['objective']:.9f} | {residual} | "
                    f"{m['endpoint_rmse_g_s']:.4f} / {m['trace_rmse_g_s']:.4f} | "
                    f"{r['analytic_peak_fold_median_bar']:.4f} | {m['slope_g_s_bar']:+.5f} |")
    text += ["", "Continuous peaks are medians of the 11 standard-fold capacity roots; constant-pressure mass memory preserves their locations. "
             "The 0.05-bar-grid peak medians [fold ranges], not confidence intervals, are " + "; ".join(
                 f"{form} {reads[form]['flow_peak_fold_median_bar']:.2f} "
                 f"[{reads[form]['flow_peak_fold_range_bar'][0]:.2f}, {reads[form]['flow_peak_fold_range_bar'][1]:.2f}]"
                 for form in ("T2-F", "W3", "W4")) + " bar.", ""]
    for form in ("W3", "W4"):
        r, m = reads[form], reads[form]["metrics"]
        conclusion = "reduces absolute held-out residuals at both 1 and 2 bar" if r["both_low_conditions_improve"] else "does not reduce absolute held-out residuals at both 1 and 2 bar"
        text.append(f"{form} {conclusion}. Its low-pressure signed bias is {m['low_bias_g_s']:+.4f} g/s; "
            f"mean absolute condition residual is {m['low_mae_g_s']:.4f} g/s. "
            f"Rising trends match {sum(v['matches_rising'] for v in m['resolved_trends'])}/5 resolved conditions.")
    text += ["", "The 3.5-bar condition has only three brews. The additional held-out tests remove it from flow training "
        "while retaining the standard fold's onset bank and Mc. Dependence uses each form's own difference from T2-F:", "",
        "| Form / held-out bar | Standard residual | 3.5 omitted residual | Absolute change / baseline | Material dependence |",
        "|---|---:|---:|---|---|"]
    for form in ("W3", "W4"):
        for d in reads[form]["omission_dependence"]:
            text.append(f"| {form} / {d['condition_bar']:g} | {d['standard_residual_g_s']:+.4f} | "
                f"{d['omitted_residual_g_s']:+.4f} | {abs(d['change_g_s']):.4f} / {d['baseline_g_s']:.4f} | "
                f"{'yes' if d['material'] else 'no'} |")
    text += ["", "Where flagged, the low-pressure result leans on 3.5 bar. Extra omission predictions are excluded from the ordinary LOCO metrics. "
        "The CSV also keeps the separate in-sample 3.5-omitted curves.", "",
        "| Fold | W3 n | W4 n | W4 P0, bar |", "|---|---:|---:|---:|"]
    for fold in (*STANDARD, *OMITTED):
        text.append(f"| {fold} | {reads['W3']['n_by_fold'][fold]:.4f} | "
                    f"{reads['W4']['n_by_fold'][fold]:.4f} | {reads['W4']['P0_by_fold'][fold]:.4f} |")
    text += ["", "Condition objective shares use the unchanged absolute-flow loss. Full-cohort largest contributions are " + "; ".join(
        form+": "+", ".join(f"{p['condition_bar']:g} bar {p['share']:.1%}" for p in sorted(
            next(f for f in fits if f['candidate'] == form and f['fold'] == 'DESCRIPTIVE_ALL')['objective']['conditions'],
            key=lambda v: v['contribution'], reverse=True)[:2]) for form in ("W3", "W4")) +
        ". All condition shares and frozen-parameter fine-grid gains are in the CSV.", ""]
    for form in ("W3", "W4"):
        selected = [f for f in fits if f["candidate"] == form]
        disagreement = reads[form]["start_disagreement_folds"]
        unresolved = reads[form]["grid_unresolved_folds"]
        bound = [f["fold"] for f in selected if f["bound_hits"] or f["bound_proximity"]]
        zeros = [f["fold"] for f in selected if f["selected_training_counts"]["total"]]
        checks = [f["jacobian_check"] for f in selected]
        text.append(f"{form}: start-objective disagreement {len(disagreement)}/14; bound/proximity flags {len(bound)}/14; "
            f"selected zero-capacity training folds {len(zeros)}/14; grid-unresolved improvements {len(unresolved)}/14. "
            f"Selected half-step relative Jacobian changes range {min(c['half_step_relative_change'] for c in checks):.3g} "
            f"to {max(c['half_step_relative_change'] for c in checks):.3g}. "
            f"Bound folds: {', '.join(bound) if bound else 'none'}. "
            f"Disagreeing-start folds: {', '.join(disagreement) if disagreement else 'none'}.")
    w4 = [f for f in fits if f['candidate'] == 'W4']
    switches = [f['fold'] for f in w4 if f['jacobian_check']['full_branch_switches'] or f['jacobian_check']['half_branch_switches']]
    text += ["", f"Selected W4 finite-difference branch switches occur in {len(switches)}/14 fits "
        f"({', '.join(switches) if switches else 'none'}). Initial n=1 checks, threshold brackets, every start's "
        "initial/final censor counts and parameter spreads are retained. A positive P0 comparable to the machine's "
        "0.28316-bar constant correction is consistent with an offset, not evidence of a physical entry threshold.", "",
        f"Onset RMSE remains {reads['T2-F']['metrics']['onset_rmse_s']:.4f} s and its fold-median minimum "
        f"{reads['T2-F']['inherited_onset_minimum_median_bar']:.2f} bar, inherited unchanged. Training floors are inactive; "
        "the 1-bar-omitted onset threshold remains bound-pinned at -5 bar. Fixed Pd cannot establish scale consistency. "
        "Both forms retain the exponential high-pressure decline; the slope tradeoff does not negate a low-pressure capability result.", "",
        "Saved C2 joint, C1/C0/E1/F1/B1 comparisons are included without refits. In-sample screens can mislead and point LOCO does not replace paired refits. "
        "No physical mechanism or independent validation is established.", "",
        f"Cumulative analysis/check wall time through output: {provenance['cumulative_wall_seconds']:.2f} s; "
        "serial, one BLAS thread, two-hour cumulative cap. [Full results and CI fixtures](RESULT_TABLE.csv). "
        "Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. C3c awaits owner review; no successor is authorized.", ""]
    path.write_text("\n".join(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--onset-cache", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--report-only", action="store_true", help="Rebuild reports from completed checkpoints; never refit")
    args = parser.parse_args()
    if args.work.resolve().is_relative_to(ROOT):
        raise ValueError("Cumulative runtime ledger must be outside the checkout")
    if hashlib.sha256((OUT / "PLAN.md").read_bytes()).hexdigest() != PLAN_SHA256:
        raise ValueError("Approved plan identity changed; stop")
    args.out.mkdir(parents=True, exist_ok=True)
    with D.timed_attempt(args.work) as budget:
        ctx = D.load_context(args.raw, args.onset_cache)
        sources = source_hashes(args.raw, args.onset_cache, ctx.brews.ids)
        references = reference_folds(ctx)
        fixtures = numerical_fixtures(budget)
        rows = [*references, input_fixture(ctx), fixtures, *low_pressure_audit(ctx), *comparators()]
        fits = []
        checkpoint = args.work / "completed-fits.json"
        identity = args.work / "fit-sources.json"
        if args.report_only:
            if json.loads(identity.read_text()) != sources:
                raise ValueError("Fit inputs/code changed; report-only cannot disguise a different calculation")
            fits = json.loads(checkpoint.read_text())
            if len(fits) != 28 or any(f["status"] != "complete" for f in fits):
                raise RuntimeError("Incomplete fits; stop for owner review")
        else:
            if checkpoint.exists():
                raise RuntimeError("Existing fit checkpoints: use report-only; no automatic repeat or retuning")
            identity.write_text(json.dumps(sources, indent=2)+"\n")
            for form in ("W3", "W4"):
                for fold in (*STANDARD, *OMITTED):
                    reference = next(r for r in references if r["fold"] == fold)
                    try:
                        fit = fit_fold(ctx, form, fold, reference, budget, args.work)
                    except UnresolvedFit as exc:
                        D.write_table([*rows, *fits, exc.row], args.out / "RESULT_TABLE.csv")
                        (args.out / "SUMMARY.md").write_text("# PRESSURE-PEAK C3c stopped\n\n**"+CLAIM+
                            ".** Ungraded. "+str(exc)+". No retuning or subsequent fits.\n")
                        raise
                    fits.append(fit)
                    checkpoint.write_text(json.dumps(fits, allow_nan=False)+"\n")
                    print("FIT_COMPLETE", form, fold, fit["objective"]["objective"], fit["parameters"], flush=True)
        rows += [*fits, *reading(fits, references)]
        if sources != source_hashes(args.raw, args.onset_cache, ctx.brews.ids):
            raise RuntimeError("Sources changed during execution")
        rows.append(dict(record_type="provenance", source_sha256=sources,
            source_base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            plan_fix_commit=FIX_COMMIT, plan_sha256=PLAN_SHA256,
            module_sha256=sources[str(Path(__file__).relative_to(ROOT))], python=sys.version,
            cumulative_wall_seconds=budget.cumulative, prior_attempt_seconds=budget.prior,
            cap_seconds=7200, execution="serial; one BLAS thread", fit_count=len(fits),
            start_count=sum(len(f["starts"]) for f in fits),
            fallback_count=sum(f["fallback"] is not None for f in fits), bootstrap_count=0,
            onset_refits=0, report_only=args.report_only, successor_authorized=False))
        budget.check()
        D.write_table(rows, args.out / "RESULT_TABLE.csv")
        write_summary(D.plain(rows), args.out / "SUMMARY.md")
        print("COMPLETE", budget.cumulative, "cumulative seconds", flush=True)


if __name__ == "__main__":
    main()

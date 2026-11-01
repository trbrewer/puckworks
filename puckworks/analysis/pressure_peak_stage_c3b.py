"""C3b T3-O: capability demonstration, not validation; TARGET_EXPOSED.

PHYSICAL_VALIDATION=NOT_ESTABLISHED. Owner-approved plan with amendment B1.
Python-only retrospective screen. Earlier stages and source data are read-only.
Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0; no upstream programs imported.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import least_squares

from . import pressure_peak_stage_c3a as C3A

C2, C1, C0, A, B = C3A.C2, C3A.C1, C3A.C0, C3A.A, C3A.B
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C3B"
CLAIM = C3A.CLAIM
FIELDS = ("a_g_s_bar", "Pstar_bar", "P0f_bar", "Pd_bar", "P0o_bar", "b_s_bar", "t0_s")
BOUNDS = ((.001, 20.), (.5, 100.), (-5., 5.), (.1, 100.), (-5., 5.), (.0001, 1e4), (0., 120.))
STARTS = ((1., 15., 1., 3., 1., 15., 0.), (1.5, 30., .5, 2., .5, 3., 8.),
          (2., 8., 1., 6., 1., 1., 10.), (1.2, 12.2, .5, 4., .54, 4.8, 9.1))
LOG = [0, 1, 3, 5]
READING = ("If no held-out 1-bar onset is censored and the continuous flow peak is below "
           "C2 T2-F's 6.90 bar, T3-O goes to a full C3 run with 200 paired refits. If any "
           "held-out 1-bar onset is censored, the kink flow law cannot support T3-O and "
           "the programme reports that finding instead.")


def read_table(path=OUT / "RESULT_TABLE.csv"):
    return C3A.read_table(path)


def coordinates(p):
    z = np.array(p, dtype=float, copy=True)
    z[LOG] = np.log(z[LOG])
    return z


def physical(z):
    p = np.array(z, dtype=float, copy=True)
    p[LOG] = np.exp(p[LOG])
    return p


def flow(parameters, pressure, t, mc):
    """C2 T2 capacity and the unchanged parent exposure/inversion helper."""
    a, star, p0, pd = parameters[:4]
    pressure = np.maximum(pressure, 0.)
    capacity = a * np.exp(-pressure/star) * pd * -np.expm1(-np.maximum(pressure-p0, 0.)/pd)
    return C3A.mass_flow(capacity, t, mc)[0]


def wetting(parameters, early):
    _, _, _, pd, p0, b, t0 = parameters
    return t0 + b*np.exp(np.asarray(early)/pd)/np.maximum(np.asarray(early)-p0, .01)


def crossing_observer(t, q, tw, end):
    """Continuous crossings of linear q, exact segment integrals, raw-end censor.

    The infimum of entry into q>0.1 is the strict-flow crossing; a flat equality
    never fires. A drop after the first flow crossing is flagged, not repaired.
    """
    result = dict(wetting_s=float(tw), record_end_s=float(end), t_mass_s=None,
                  t_flow_s=None, predicted_onset_s=float(end), censored=True,
                  criterion="censored", drop_back=False, followup_complete=False,
                  mass_witness=None, flow_witness=None)
    if tw >= end:
        return result
    inside = (t > tw) & (t < end)
    x = np.r_[tw, t[inside], end]
    y = np.interp(x, t, q)
    integral = np.r_[0., np.cumsum((y[1:]+y[:-1])*np.diff(x)/2)]
    j = int(np.searchsorted(integral, .5))
    if j < len(x):
        left, width = j-1, x[j]-x[j-1]
        slope = (y[j]-y[left])/width
        remainder = .5-integral[left]
        delta = 2*remainder/(y[left]+np.sqrt(max(0., y[left]**2+2*slope*remainder)))
        tm = x[left]+delta
        result.update(t_mass_s=float(tm), mass_witness=dict(
            left_s=x[left], right_s=x[j], left_q=y[left], right_q=y[j],
            mass_left_g=integral[left], mass_right_g=integral[j]))
    found = np.flatnonzero(y > .1)
    if len(found):
        j = int(found[0])
        tf = tw if j == 0 else x[j-1]+(.1-y[j-1])*(x[j]-x[j-1])/(y[j]-y[j-1])
        result.update(t_flow_s=float(tf), flow_witness=dict(
            left_s=x[max(0, j-1)], right_s=x[j], left_q=y[max(0, j-1)], right_q=y[j]))
    tm, tf = result["t_mass_s"], result["t_flow_s"]
    if tm is None or tf is None or max(tm, tf) >= end:
        return result
    onset = max(tm, tf)
    until = min(end, onset+2.)
    follow = np.r_[onset, x[(x > onset) & (x < until)], until]
    minimum = float(np.min(np.interp(follow, x, y)))
    result.update(predicted_onset_s=float(onset), censored=False,
                  criterion="mass" if tm > tf else "flow" if tf > tm else "tie",
                  drop_back=minimum < .1, minimum_followup_q_g_s=minimum,
                  flow_at_onset_g_s=float(np.interp(onset, x, y)),
                  followup_complete=onset+2 <= end)
    return result


def observe(parameters, t, pressure, early, ends, mc, q=None):
    q = flow(parameters, pressure, t, mc) if q is None else q
    return [crossing_observer(t, curve, tw, end)
            for curve, tw, end in zip(q, wetting(parameters, early), ends)]


def condition_counts(records, conditions):
    return {str(float(c)): dict(n=int(sum(conditions == c)),
        censored=sum(r["censored"] for r, p in zip(records, conditions) if p == c),
        **{k: sum(r["criterion"] == k for r, p in zip(records, conditions) if p == c)
           for k in ("flow", "mass", "tie")},
        drop_back=sum(r["drop_back"] for r, p in zip(records, conditions) if p == c),
        incomplete_followup=sum(not r["followup_complete"] and not r["censored"]
                                for r, p in zip(records, conditions) if p == c))
        for c in np.unique(conditions)}


def finite_jac(evaluate, z, lower, upper, multiplier=1.):
    """Plan's absolute transformed-coordinate steps; branches always recomputed."""
    center, records = evaluate(z)
    jac = np.empty((len(center), len(z)))
    switches, flat_censored = 0, 0
    labels = [(r["censored"], r["criterion"]) for r in records]
    for k in range(len(z)):
        step = multiplier*1e-4*max(1., abs(z[k]))
        lo, hi = z.copy(), z.copy()
        if z[k]-step < lower[k]:
            hi[k] = min(z[k]+step, upper[k])
        elif z[k]+step > upper[k]:
            lo[k] = max(z[k]-step, lower[k])
        else:
            lo[k] -= step
            hi[k] += step
        f0, r0 = evaluate(lo)
        f1, r1 = evaluate(hi)
        jac[:, k] = (f1-f0)/(hi[k]-lo[k])
        switches += sum((a["censored"], a["criterion"]) != label or
                        (b["censored"], b["criterion"]) != label
                        for a, b, label in zip(r0, r1, labels))
        flat_censored += sum(a["censored"] and b["censored"] and label[0]
                             for a, b, label in zip(r0, r1, labels))
    return jac, dict(branch_switches=switches, flat_censored_entries=flat_censored)


class Evaluator:
    def __init__(self, ctx, indices, mc, budget):
        self.ctx, self.indices, self.mc, self.budget = ctx, indices, mc, budget
        self.weights = C3A.condition_weights(ctx.brews.condition[indices])
        mask = ctx.coarse.mask[indices]
        self.trace_weights = np.sqrt(self.weights[:, None]*mask/mask.sum(axis=1)[:, None])/.437
        self.onset_weights = np.sqrt(self.weights)/4.534

    @lru_cache(maxsize=12)
    def curves(self, first_four):
        p, ctx, ix = np.asarray(first_four), self.ctx, self.indices
        return (flow(p, ctx.coarse.pressure[ix], ctx.coarse.t, self.mc),
                flow(p, ctx.observer_pressure[ix], ctx.observer_t, self.mc))

    def __call__(self, z):
        self.budget.check()
        p = physical(z)
        q, qo = self.curves(tuple(p[:4]))
        ctx, ix = self.ctx, self.indices
        records = observe(p, ctx.observer_t, ctx.observer_pressure[ix], ctx.early[ix],
                          ctx.raw_ends[ix], self.mc, qo)
        onset = np.array([r["predicted_onset_s"] for r in records])
        residual = np.r_[((q-ctx.coarse.flow[ix])*self.trace_weights).ravel(),
                         (onset-ctx.delays[ix, 1])*self.onset_weights]
        return residual, records


def add_raw_support(ctx):
    ctx.raw_ends = np.array([r["t"][-1] for r in ctx.native])
    ctx.observer_t = np.arange(0., np.ceil(max(ctx.raw_ends)*10)/10+.05, .1)
    ctx.observer_pressure = np.array([np.interp(ctx.observer_t, r["t"], r["p"])
                                      for r in ctx.native])
    return ctx


def metrics(records):
    conditions = np.array([r["condition_bar"] for r in records])
    residual = np.array([r["endpoint_residual_g_s"] for r in records])
    onset_error = np.array([r["predicted_onset_s"]-r["observed_onset_s"] for r in records])
    groups = [np.flatnonzero(conditions == c) for c in np.unique(conditions)]
    means = [float(residual[g].mean()) for g in groups]
    pressure = np.array([np.mean([records[i]["endpoint_pressure_bar"] for i in g]) for g in groups])
    predicted = np.array([np.mean([records[i]["endpoint_prediction_g_s"] for i in g]) for g in groups])
    low, high = np.unique(conditions) <= 3.5, np.unique(conditions) >= 9
    uncensored = np.array([not r.get("censored", False) for r in records])
    return dict(conditions_bar=np.unique(conditions), endpoint_residuals_g_s=means,
        endpoint_means_g_s=predicted, endpoint_pressures_bar=pressure,
        low_bias_g_s=float(np.mean(np.array(means)[low])) if low.any() else None,
        low_mae_g_s=float(np.mean(np.abs(np.array(means)[low]))) if low.any() else None,
        slope_g_s_bar=A.slope(pressure[high], predicted[high]) if sum(high) > 1 else None,
        endpoint_rmse_g_s=C3A.grouped_rmse(conditions, residual),
        onset_rmse_s=C3A.grouped_rmse(conditions, onset_error),
        uncensored_onset_rmse_s=C3A.grouped_rmse(conditions[uncensored], onset_error[uncensored]),
        trace_rmse_g_s=float(np.mean([np.sqrt(np.mean([records[i]["trace_mse"] for i in g])) for g in groups])))


def brew_records(ctx, p, mc, indices, train, parent_onset=None):
    qo = flow(p, ctx.observer_pressure[indices], ctx.observer_t, mc)
    obs = observe(p, ctx.observer_t, ctx.observer_pressure[indices], ctx.early[indices],
                  ctx.raw_ends[indices], mc, qo) if parent_onset is None else [
                      dict(predicted_onset_s=float(v), censored=False) for v in parent_onset]
    fine = flow(p, ctx.fine.pressure[indices], ctx.fine.t, mc)
    endpoint = flow(p, ctx.brews.pressure[indices], ctx.brews.t, mc)[:, -1]
    fm = ctx.fine.mask[indices]
    mse = ((fine-ctx.fine.flow[indices])**2*fm).sum(axis=1)/fm.sum(axis=1)
    rows = []
    for j, i in enumerate(indices):
        rows.append(dict(brew=ctx.brews.ids[i], condition_bar=float(ctx.brews.condition[i]),
            role="training" if i in train else "held_out", Pe_bar=ctx.early[i],
            clean_end_s=ctx.fine.ends[i], record_end_s=ctx.raw_ends[i],
            observed_onset_s=ctx.delays[i, 1], endpoint_observed_g_s=ctx.brews.target[i],
            endpoint_prediction_g_s=endpoint[j], endpoint_residual_g_s=endpoint[j]-ctx.brews.target[i],
            endpoint_pressure_bar=ctx.brews.pressure[i, -1], trace_mse=mse[j],
            **{k: v for k, v in obs[j].items() if k != "record_end_s"}))
        if len(p) == 7:
            rows[-1].update(margin_bar=ctx.early[i]-p[4], floor_used=ctx.early[i]-p[4] < .01-1e-12)
    return rows


def exposure_of_state(x):
    return x + sum(-np.expm1(-(k+1)*x)*v for k, v in enumerate(B._INVERSE_COEFFICIENTS))


def constant_onset(p, pressure, mc):
    """Uncensored constant-pressure crossings; no finite search horizon."""
    a, star, p0, pd = p[:4]
    capacity = a*np.exp(-pressure/star)*pd*(-np.expm1(-max(pressure-p0, 0.)/pd))
    if capacity <= .1:
        return np.inf
    tw = float(wetting(p, pressure))
    state = float(A.delivered_state(np.array(capacity*tw/mc)))
    tm = mc*exposure_of_state(state+.5/mc)/capacity
    flow_state = max(0., -np.log(-np.log(.1/capacity)))
    tf = max(tw, mc*exposure_of_state(flow_state)/capacity)
    return max(tm, tf)


def extrema(p, mc):
    grid = C1.GRID
    q = flow(p, np.repeat(grid[:, None], 2, axis=1), np.array([0., 100.]), mc)[:, -1]
    onset = np.array([constant_onset(p, v, mc) for v in grid])
    iq, it = int(np.argmax(q)), int(np.argmin(onset))
    return dict(grid_bar=grid, flow_grid_g_s=q, observer_onset_grid_s=onset,
        flow_peak_bar=float(grid[iq]), observer_onset_minimum_bar=float(grid[it]) if np.isfinite(onset[it]) else None,
        flow_peak_boundary=iq in (0, len(grid)-1),
        onset_minimum_boundary=it in (0, len(grid)-1),
        never_firing_pressures_bar=grid[~np.isfinite(onset)],
        analytic_capacity_peak_bar=float(p[2]+p[3]*np.log1p(p[1]/p[3])),
        analytic_wetting_minimum_bar=float(p[4]+p[3]))


def fit_fold(ctx, fold, budget):
    conditions = ctx.brews.condition
    train = np.arange(len(conditions)) if fold == "DESCRIPTIVE_ALL" else np.flatnonzero(
        conditions != float(fold.removeprefix("HYD-LOCO-")))
    cap = C2.onset_cap(ctx.early[train])
    lower, upper = (coordinates([v[j] for v in BOUNDS]) for j in (0, 1))
    upper[4] = cap
    mc = ctx.saved[fold]["Mc_fixed_g"]
    evaluate = Evaluator(ctx, train, mc, budget)
    starts, results = [], []
    for number, initial in enumerate(STARTS, 1):
        z0 = np.clip(coordinates(initial), lower+1e-10, upper-1e-10)
        f0, r0 = evaluate(z0)
        initial_counts = condition_counts(r0, conditions[train])
        started = time.monotonic()
        diagnostics = dict(branch_switches=0, flat_censored_entries=0, jacobian_calls=0)

        def jac(z):
            value, audit = finite_jac(evaluate, z, lower, upper)
            diagnostics["jacobian_calls"] += 1
            for k, v in audit.items():
                diagnostics[k] += v
            return value

        result = least_squares(lambda z: evaluate(z)[0], z0, jac=jac, bounds=(lower, upper),
                               x_scale="jac", ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=500)
        final_residual, final_records = evaluate(result.x)
        starts.append(dict(start=number, initial_parameters=dict(zip(FIELDS, physical(z0))),
            final_parameters=dict(zip(FIELDS, physical(result.x))),
            initial_training_counts=initial_counts,
            final_training_counts=condition_counts(final_records, conditions[train]),
            initial_objective=float(f0@f0), objective=float(final_residual@final_residual),
            success=bool(result.success), status=int(result.status), message=result.message,
            nfev=result.nfev, njev=result.njev, optimality=result.optimality,
            bound_hits=[k for k, flag in zip(FIELDS, result.active_mask) if flag],
            wall_seconds=time.monotonic()-started, **diagnostics))
        results.append(result)
        print(f"{fold} start {number}/4 J={2*result.cost:.9g} success={result.success} "
              f"training censored={sum(r['censored'] for r in final_records)}", flush=True)
        (budget.work / (fold+"-starts.json")).write_text(json.dumps(C3A.plain(starts), indent=2))
    valid = [i for i, r in enumerate(results) if r.success and np.isfinite(r.fun).all()]
    fallback = None
    if not valid:
        i = min(range(4), key=lambda j: results[j].cost)
        retry = least_squares(lambda z: evaluate(z)[0], results[i].x,
            jac=lambda z: finite_jac(evaluate, z, lower, upper)[0], bounds=(lower, upper),
            method="dogbox", x_scale="jac", ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500)
        f, r = evaluate(retry.x)
        fallback = dict(from_start=i+1, parameters=dict(zip(FIELDS, physical(retry.x))),
            objective=float(f@f), success=bool(retry.success), nfev=retry.nfev,
            training_counts=condition_counts(r, conditions[train]))
        if not retry.success or not np.isfinite(f).all():
            raise RuntimeError(f"{fold}: C2 fallback failed; no fit discarded")
        chosen, best = i, retry
    else:
        chosen = min(valid, key=lambda i: results[i].cost)
        best = results[chosen]
    p = physical(best.x)
    residual, records = evaluate(best.x)
    full_jac, audit = finite_jac(evaluate, best.x, lower, upper)
    half_jac, half_audit = finite_jac(evaluate, best.x, lower, upper, .5)
    prediction = brew_records(ctx, p, mc, np.arange(len(conditions)), train)
    training = [r for r in prediction if r["role"] == "training"]
    held = [r for r in prediction if r["role"] == "held_out"]
    if any(r["floor_used"] for r in training):
        raise RuntimeError("Training onset floor active")
    censored = sum(r["censored"] for r in training)
    near = (best.x-lower <= 1e-6*(upper-lower)) | (upper-best.x <= 1e-6*(upper-lower))
    return C3A.plain(dict(record_type="fit", candidate="T3-O", fold=fold, parameter_count=7,
        parameters=dict(zip(FIELDS, p)), Mc_fixed_g=mc, P0o_cap_bar=cap,
        lower_coordinates=lower, upper_coordinates=upper, selected_start=chosen+1,
        starts=starts, fallback=fallback, training_brews=[ctx.brews.ids[i] for i in train],
        training_weights=evaluate.weights, training_counts=condition_counts(records, conditions[train]),
        held_out_counts=condition_counts([r for r in prediction if r["role"] == "held_out"],
                                         np.array([r["condition_bar"] for r in held])),
        bound_hits=[k for k, flag in zip(FIELDS, best.active_mask) if flag],
        bound_proximity=[k for k, flag in zip(FIELDS, near) if flag],
        cap_binding=bool(upper[4]-best.x[4] <= 1e-6*(upper[4]-lower[4])),
        training_floor_uses=0, held_out_floor_uses=sum(r["floor_used"] for r in held),
        plateau_label="possible plateau artefact" if censored else "none",
        objective=float(residual@residual), flow_objective_component=float(residual[:-len(train)]@residual[:-len(train)]),
        onset_objective_component=float(residual[-len(train):]@residual[-len(train):]),
        start_disagreement=max(s["objective"] for s in starts)-min(s["objective"] for s in starts) >
                           1e-6*max(1., float(residual@residual)),
        parameter_spreads={k: max(s["final_parameters"][k] for s in starts)-min(s["final_parameters"][k] for s in starts)
                           for k in FIELDS},
        jacobian_check=dict(max_abs_half_step_change=float(np.max(np.abs(full_jac-half_jac))),
            relative_half_step_norm=float(np.linalg.norm(full_jac-half_jac)/max(np.linalg.norm(full_jac), 1e-300)),
            full_step=audit, half_step=half_audit),
        brew_predictions=prediction, training_metrics=metrics(training), held_out_metrics=metrics(held) if held else None,
        extrema=extrema(p, mc)))


def parent_replays(ctx):
    rows = []
    for source in C2.read_results():
        if source.get("candidate") not in ("T2-F", "T2 joint (capped)"):
            continue
        name = source["candidate"]
        bank = json.loads(source["parameters_by_fold"])
        saved = bank["DESCRIPTIVE_ALL"]
        coef, mc = C1.flow_parameters(saved), saved["Mc_fixed_g"]
        q = flow(coef, ctx.coarse.pressure, ctx.coarse.t, mc)
        reference = C1.flow_curve(coef, ctx.coarse.pressure, ctx.coarse.t, mc)[0]
        np.testing.assert_allclose(q, reference, rtol=1e-12, atol=0)
        mask = ctx.coarse.mask
        mse = ((q-ctx.coarse.flow)**2*mask).sum(axis=1)/mask.sum(axis=1)
        weights = C3A.condition_weights(ctx.brews.condition)
        timing = saved.get("onset_parameters", saved)
        onset = C0.onset_curve(C1.onset_parameters(timing), ctx.early)[0]
        error = onset-ctx.delays[:, 1]
        jflow, jonset = float(weights@mse), float(weights@(error**2))
        joint = jflow/.437**2+jonset/4.534**2
        objective = jflow if name == "T2-F" else joint
        np.testing.assert_allclose(objective, saved["objective_sum_squares"], rtol=1e-12, atol=0)
        predicted, full = [], []
        extrema_by_fold = {}
        for fold, parameters in bank.items():
            ix = np.arange(len(ctx.early)) if fold == "DESCRIPTIVE_ALL" else np.flatnonzero(
                ctx.brews.condition == float(fold.removeprefix("HYD-LOCO-")))
            timing = parameters.get("onset_parameters", parameters)
            delay = C0.onset_curve(C1.onset_parameters(timing), ctx.early[ix])[0]
            records = brew_records(ctx, C1.flow_parameters(parameters), parameters["Mc_fixed_g"],
                                    ix, set(ix) if fold == "DESCRIPTIVE_ALL" else set(), delay)
            if fold == "DESCRIPTIVE_ALL":
                full = records
            else:
                predicted.extend(records)
            curves = C1.continuous(parameters)
            extrema_by_fold[fold] = {k: curves[k] for k in
                ("flow_peak", "onset_minimum", "analytic_flow_peak", "analytic_onset_minimum")}
        observed_metrics = metrics(predicted)
        mapping = dict(endpoint_rmse_g_s="endpoint_rmse_g_s", trace_rmse_g_s="trace_rmse_g_s",
            onset_rmse_s="onset_rmse_s", slope_g_s_bar="slope_g_s_bar",
            low_bias_g_s="low_pressure_bias_g_s", low_mae_g_s="low_condition_mean_absolute_residual_g_s")
        for key, saved_key in mapping.items():
            np.testing.assert_allclose(observed_metrics[key], float(source[saved_key]), rtol=1e-12, atol=0)
        rows.append(dict(record_type="parent_replay", candidate=name, parameters=saved,
            parameters_by_fold=bank, saved_objective=saved["objective_sum_squares"],
            recomputed_objective=objective, flow_objective_unscaled=jflow, onset_objective_unscaled=jonset,
            joint_objective=joint, weights=weights, brew_trace_mse=mse, onset_errors_s=error,
            brew_predictions=predicted, descriptive_brew_predictions=full,
            metrics=observed_metrics, extrema_by_fold=extrema_by_fold,
            saved_metrics={k: float(source[v]) for k, v in mapping.items()}))
        print("PARENT_REPLAY", name, saved["objective_sum_squares"], objective, flush=True)
    return rows


def numerical_fixtures():
    cases = [
        ("mass", [0, 2, 4, 8], [.2, .2, .2, .2], 1., 8.),
        ("flow", [0, 5, 10, 15], [.09, .09, .09, .2], 0., 15.),
        ("tie", [0, 10, 15], [0, .1, .2], 0., 15.),
        ("strict equality", [0, 10, 20], [.1, .1, .1], 0., 20.),
        ("wet after end", [0, 5, 10], [1, 1, 1], 11., 10.),
        ("mass at end", [0, 1, 2], [.25, .25, .25], 0., 2.),
        ("drop back", [0, 2, 2.5, 3, 5, 8], [.3, .3, .3, 0, 0, 0], 0., 8.),
        ("short followup", [0, 2, 3], [.2, .2, .2], 0., 3.),
        ("beyond 100", [0, 100, 120, 160], [.2, .2, .2, .2], 130., 160.),
    ]
    result = []
    for name, times, values, tw, end in cases:
        result.append(dict(name=name, t=times, q=values, tw=tw, end=end,
                           expected=crossing_observer(np.array(times), np.array(values), tw, end)))
    pressure = np.array([[.5, .5, 1., 2., 7., 13.], [13., 9., 6., 3., 1., .5]])
    t = np.array([0., .5, 1., 2., 5., 100.])
    p, mc = np.array(STARTS[3]), 28.709461834955388
    return dict(record_type="numerical_fixtures", crossings=result,
        pressure=pressure, t=t, parameters=p, mc=mc,
        reference_flow=C1.flow_curve(p[:4], pressure, t, mc)[0],
        constant_pressures_bar=[1., 3.5, 6., 13.],
        constant_onsets_s=[constant_onset(p, v, mc) for v in (1., 3.5, 6., 13.)])


def input_fixture(ctx):
    return dict(record_type="inputs", brew_ids=ctx.brews.ids, conditions_bar=ctx.brews.condition,
        early_pressure_bar=ctx.early, observed_onsets_s=ctx.delays[:, 1], raw_ends_s=ctx.raw_ends,
        clean_ends_s=ctx.coarse.ends, fit_times_s=ctx.coarse.t, fit_pressure=ctx.coarse.pressure,
        fit_observed_flow=ctx.coarse.flow, fit_mask=ctx.coarse.mask,
        observer_times_s=ctx.observer_t, observer_pressure=ctx.observer_pressure,
        endpoint_observed_g_s=ctx.brews.target, endpoint_pressure_bar=ctx.brews.pressure[:, -1],
        saved_mc_by_fold={f: r["Mc_fixed_g"] for f, r in ctx.saved.items()})


def result_reading(fits):
    held = [r for f in fits for r in f["brew_predictions"] if r["role"] == "held_out"]
    one = [r for r in held if r["condition_bar"] == 1.]
    median = float(np.median([f["extrema"]["flow_peak_bar"] for f in fits if f["fold"] != "DESCRIPTIVE_ALL"]))
    censored = sum(r["censored"] for r in one)
    outcome = ("kink flow law cannot support T3-O" if censored else
               "recommend full C3 with 200 paired refits" if median < 6.90 else
               "advancement criterion unmet; return to owner")
    return dict(record_type="reading", predeclared_reading=READING, outcome=outcome,
        held_out_1bar_censored=censored, loco_median_flow_peak_bar=median,
        loco_median_observer_onset_minimum_bar=float(np.median([
            f["extrema"]["observer_onset_minimum_bar"] for f in fits if f["fold"] != "DESCRIPTIVE_ALL"])),
        possible_plateau_folds=[f["fold"] for f in fits if f["plateau_label"] != "none"],
        successor_authorized=False, metrics=metrics(held), held_out_1bar_predictions=one,
        held_out_counts=condition_counts(held, np.array([r["condition_bar"] for r in held])))


def write_summary(rows, path):
    fits = [r for r in rows if r["record_type"] == "fit"]
    reading = next(r for r in rows if r["record_type"] == "reading")
    parents = [r for r in rows if r["record_type"] == "parent_replay"]
    provenance = next(r for r in rows if r["record_type"] == "provenance")
    full = next(r for r in fits if r["fold"] == "DESCRIPTIVE_ALL")
    m = reading["metrics"]
    lines = ["# PRESSURE-PEAK C3b: T3-O onset observer", "", "**"+CLAIM+".** EXPLORATORY; ungraded.", "",
        "The screen fits seven parameters to 56 brews: DESCRIPTIVE_ALL plus 11 LOCO folds. "
        "All 48 starts ran. In-sample fits can mislead and point LOCO does not replace paired refits.", "",
        "C2 objective replays precede comparison: " + "; ".join(
            f"{r['candidate']} saved {r['saved_objective']:.16g}, recomputed {r['recomputed_objective']:.16g}"
            for r in parents) + ". Both agree at rtol=1e-12. T2-F's replay is unscaled flow loss; "
        "joint comparisons use the common 0.437 g/s and 4.534 s scales.", "",
        f"The full-cohort joint objective is {full['objective']:.6f}. Selected parameters "
        "(a, Pstar, P0f, Pd, P0o, b, t0) are " + ", ".join(f"{full['parameters'][k]:.4g}" for k in FIELDS) + ". "
        "Units are g/s/bar for a, bar for pressures, s·bar for b and s for t0.", "",
        "| Held-out metric | T3-O | C2 T2-F | C2 T2 joint (capped) |",
        "|---|---:|---:|---:|"]
    for label, key in (("Endpoint RMSE, g/s", "endpoint_rmse_g_s"), ("Trace RMSE, g/s", "trace_rmse_g_s"),
                       ("Onset RMSE, s", "onset_rmse_s"), ("Low-pressure bias, g/s", "low_bias_g_s"),
                       ("Low-pressure MAE, g/s", "low_mae_g_s"), (">=9-bar slope, g/s/bar", "slope_g_s_bar")):
        lines.append(f"| {label} | {m[key]:.4f} | " + " | ".join(f"{r['metrics'][key]:.4f}" for r in parents)+" |")
    lines += ["", f"The LOCO median 100-s flow peak is {reading['loco_median_flow_peak_bar']:.2f} bar "
        f"versus C2 T2-F's 6.90 bar; the observer-onset minimum is {reading['loco_median_observer_onset_minimum_bar']:.2f} bar. "
        f"Held-out 1-bar censoring is {reading['held_out_1bar_censored']}/5. "
        "Its predicted onsets / recorded ends (s), in brew order, are " + "; ".join(
            f"{r['brew']}: {r['predicted_onset_s']:.2f}/{r['record_end_s']:.2f}" for r in reading["held_out_1bar_predictions"]) + ".", ""]
    plateau = reading["possible_plateau_folds"]
    lines.append("Selected fits labelled **possible plateau artefact**: " + ", ".join(plateau) +
                 ". Their censored training brews are retained; no retuning, dropping or restarting was performed."
                 if plateau else "No selected fit censors a training brew; none receives the possible plateau artefact label.")
    lines.append(f"Start objectives disagree in {sum(f['start_disagreement'] for f in fits)}/12 fits. "
        f"Selected bound/proximity flags occur in {sum(bool(f['bound_proximity']) for f in fits)}/12 fits; "
        f"held-out onset-floor uses total {sum(f['held_out_floor_uses'] for f in fits)}. "
        f"Held-out drop-back flags total {sum(c['drop_back'] for c in reading['held_out_counts'].values())}. "
        "The CSV retains every start, initial/final training censor counts, switching/half-step diagnostics, "
        "all condition residuals and per-fold extrema. Numerical and optimizer flags limit interpretation.")
    lines += ["", "Pre-declared reading: **"+reading["outcome"]+"**. This is a capability screen, not a physical conclusion. "
        "C3 is not authorized; return to owner.", "",
        f"Cumulative wall time through output: {provenance['cumulative_wall_seconds']:.2f} s; "
        "serial, one BLAS thread, two-hour cap. [Full results and CI fixtures](RESULT_TABLE.csv). "
        "Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Earlier stages and source data are unchanged."]
    path.write_text("\n".join(lines)+"\n")


def hashes(raw, cache, ids):
    result = C3A.source_hashes(raw, cache, ids)
    for path in [Path(__file__), Path(C3A.__file__), OUT / "PLAN.md"]:
        result[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--onset-cache", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    if args.work.resolve().is_relative_to(ROOT):
        raise ValueError("Runtime ledger must be outside checkout")
    args.out.mkdir(parents=True, exist_ok=True)
    with C3A.timed_attempt(args.work) as budget:
        ctx = add_raw_support(C3A.load_context(args.raw, args.onset_cache))
        sources = hashes(args.raw, args.onset_cache, ctx.brews.ids)
        rows = [input_fixture(ctx), numerical_fixtures(), *parent_replays(ctx)]
        fits = []
        for fold in ctx.saved:
            row = fit_fold(ctx, fold, budget)
            fits.append(row)
            rows.append(row)
            (args.work / (fold+"-selected.json")).write_text(json.dumps(row))
            C3A.write_table(rows, args.out / "RESULT_TABLE.csv")
        rows.append(result_reading(fits))
        if sources != hashes(args.raw, args.onset_cache, ctx.brews.ids):
            raise RuntimeError("Sources changed during execution")
        rows.append(dict(record_type="provenance", source_sha256=sources,
            source_base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            module_sha256=sources[str(Path(__file__).relative_to(ROOT))], python=sys.version,
            cumulative_wall_seconds=budget.cumulative, prior_attempt_seconds=budget.prior,
            cap_seconds=7200, execution="serial; one BLAS thread", fit_count=12, start_count=48,
            bootstrap_count=0, labels=CLAIM, successor_authorized=False))
        budget.check()
        C3A.write_table(rows, args.out / "RESULT_TABLE.csv")
        write_summary(C3A.plain(rows), args.out / "SUMMARY.md")
        print("COMPLETE", budget.cumulative, "seconds", flush=True)


if __name__ == "__main__":
    main()

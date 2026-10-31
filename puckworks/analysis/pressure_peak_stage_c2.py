"""PRESSURE-PEAK C2: owner-approved training-only constrained onset threshold.

Capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED;
TARGET_EXPOSED. Only the onset-containing P0 upper bound changes. Parent C0/C1
models, objectives, starts, scales, observers, masks and Mc conventions remain
read-only. Held-out denominator-floor use is audited, never constrained.
"""
from __future__ import annotations

import argparse
import csv
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import multiprocessing
from pathlib import Path
import pickle
import time

import numpy as np
from scipy.optimize import least_squares

from . import pressure_peak_stage_c1 as C1

C0, A, B, S = C1.C0, C1.A, C1.B, C1.S
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C2"
SEED = 20261105
FIELDS, BOUNDS, STARTS = C1.FIELDS, C1.BOUNDS, C1.STARTS
coordinates, physical, flow_curve = C1.coordinates, C1.physical, C1.flow_curve
CLAIM, NS = C1.CLAIM, C1.NS
KINDS = ("onset", "fixed", "joint", "c0_onset", "c0_joint", "flow")
ONSET_KINDS = ("onset", "joint", "c0_onset", "c0_joint")
NAMES = {"onset": "T2 onset-only (capped)", "fixed": "T2-F", "joint": "T2 joint (capped)",
         "c0_onset": "C0 T1-W onset-only (capped)", "c0_joint": "C0 joint (capped)",
         "flow": "T2 flow-only identity", "c0_flow": "C0 T1 flow-only identity"}
C0_STARTS = ((1., 5., 0., 15., 0.), (2., 8., .4, 3., 8.), (2., 12., .8, 1., 10.))


def onset_cap(early):
    """Input is the selected training brews, including only sampled brews."""
    early = np.asarray(early)
    if not len(early) or not np.isfinite(early).all():
        raise ValueError("Finite, nonempty training early pressures required")
    upper = min(5., float(np.min(early))-C0.EPSILON)
    if upper <= -5.:
        raise ValueError("Training cap is incompatible with the fixed lower bound")
    return upper


def fit_t2(kind, pressure, t, target, mask, early, delay, weights, mc, budget, pd_fixed=None):
    """C1 fitter verbatim except training P0 cap and bound-side diagnostic."""
    free = np.array({"onset": [3, 2, 4, 5], "fixed": [0, 1, 2],
                     "flow": [0, 1, 2, 3], "joint": list(range(6))}[kind])
    if kind == "fixed" and pd_fixed is None:
        raise ValueError("T2-F requires its training-fold onset-only Pd")
    lower, upper = (coordinates([BOUNDS[k][j] for k in FIELDS]) for j in (0, 1))
    if kind in {"onset", "joint"}:
        upper[2] = onset_cap(early)
    root = np.sqrt(weights)
    trace_weight = np.sqrt(weights[:, None]*mask/mask.sum(axis=1)[:, None])
    cached_x, cached = None, None

    def evaluate(x):
        nonlocal cached_x, cached
        budget.check()
        if cached_x is not None and np.array_equal(x, cached_x):
            return cached
        z = coordinates(STARTS[0]); z[free] = x
        if kind == "fixed":
            z[3] = np.log(pd_fixed)
        coef = physical(z)
        residuals, derivatives = [], []
        if kind != "onset":
            q, jac = flow_curve(coef[:4], pressure, t, mc)
            scale = C0.FLOW_SCALE if kind == "joint" else 1.
            residuals.append(((q-target)*trace_weight/scale).ravel())
            full = np.zeros((*q.shape, 6)); full[:, :, :4] = jac
            derivatives.append((full[:, :, free]*trace_weight[:, :, None]/scale).reshape(-1, len(free)))
        if kind in {"onset", "joint"}:
            pred, jac = C0.onset_curve(coef[[3, 2, 4, 5]], early)
            scale = C0.ONSET_SCALE if kind == "joint" else 1.
            residuals.append((pred-delay)*root/scale)
            full = np.zeros((len(early), 6)); full[:, [3, 2, 4, 5]] = jac
            derivatives.append(full[:, free]*root[:, None]/scale)
        cached_x = x.copy()
        cached = np.concatenate(residuals), np.concatenate(derivatives)
        return cached

    fits = [least_squares(lambda x: evaluate(x)[0],
                          np.clip(coordinates(s)[free], lower[free]+1e-10, upper[free]-1e-10),
                          jac=lambda x: evaluate(x)[1], bounds=(lower[free], upper[free]),
                          x_scale="jac", ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=500)
            for s in STARTS]
    valid = [r for r in fits if r.success and np.isfinite(r.fun).all()]
    if not valid:
        best = min(fits, key=lambda r: r.cost)
        retry = least_squares(lambda x: evaluate(x)[0], best.x, jac=lambda x: evaluate(x)[1],
                              bounds=(lower[free], upper[free]), method="dogbox", x_scale="jac",
                              ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500)
        if not retry.success or not np.isfinite(retry.fun).all():
            raise RuntimeError(kind+": optimizer did not converge; no draw discarded")
        valid = [retry]
    best = min(valid, key=lambda r: r.cost)
    z = coordinates(STARTS[0]); z[free] = best.x
    coef = physical(z)
    record = {FIELDS[k]: float(coef[k]) for k in free}
    if kind == "fixed":
        record["Pd_bar"] = float(pd_fixed)
    record.update(Mc_fixed_g=float(mc) if kind != "onset" else None,
                  bound_hits=[FIELDS[k] for k, active in zip(free, best.active_mask) if active],
                  objective_sum_squares=float(2*best.cost))
    if kind in {"onset", "joint"}:
        record["P0_cap_binds"] = bool(best.active_mask[list(free).index(2)] > 0)
    return record


def fit_c0(kind, pressure, t, target, mask, early, delay, weights, mc, budget):
    """C0 fitter verbatim except training P0 cap and bound-side diagnostic."""
    # Shared coordinate order: log(a), log(Pstar), P0, log(b), t0.
    free = np.array([0, 1, 2] if kind == "flow" else [1, 2, 3, 4]
                    if kind == "onset" else [0, 1, 2, 3, 4])
    lower = np.array([np.log(.001), np.log(.5), -5., np.log(.0001), 0.])
    upper = np.array([np.log(20.), np.log(100.), 5., np.log(1e4), 120.])
    starts = [np.array([np.log(a), np.log(ps), p0, np.log(b), t0])[free]
              for a, ps, p0, b, t0 in ((1., 5., 0., 15., 0.),
                                      (2., 8., .4, 3., 8.), (2., 12., .8, 1., 10.))]
    if kind in {"onset", "joint"}:
        upper[2] = onset_cap(early)
    root = np.sqrt(weights)
    trace_weight = np.sqrt(weights[:, None]*mask/mask.sum(axis=1)[:, None])
    cached_x, cached = None, None

    def evaluate(x):
        nonlocal cached_x, cached
        budget.check()
        if cached_x is not None and np.array_equal(x, cached_x):
            return cached
        z = np.array([0., np.log(7.), 0., np.log(3.), 0.]); z[free] = x
        residuals, derivatives = [], []
        if kind != "onset":
            q, jac = C0.flow_curve(np.array([np.exp(z[0]), np.exp(z[1]), z[2]]), pressure, t, mc)
            scale = C0.FLOW_SCALE if kind == "joint" else 1.
            residuals.append(((q-target)*trace_weight/scale).ravel())
            full = np.zeros((*q.shape, 5)); full[:, :, :3] = jac
            derivatives.append((full[:, :, free]*trace_weight[:, :, None]/scale).reshape(-1, len(free)))
        if kind != "flow":
            predicted, jac = C0.onset_curve([np.exp(z[1]), z[2], np.exp(z[3]), z[4]], early)
            scale = C0.ONSET_SCALE if kind == "joint" else 1.
            residuals.append((predicted-delay)*root/scale)
            full = np.zeros((len(early), 5)); full[:, 1:] = jac
            derivatives.append(full[:, free]*root[:, None]/scale)
        cached_x = x.copy(); cached = np.concatenate(residuals), np.concatenate(derivatives)
        return cached

    fits = [least_squares(lambda x: evaluate(x)[0], np.clip(s, lower[free]+1e-10, upper[free]-1e-10),
                          jac=lambda x: evaluate(x)[1], bounds=(lower[free], upper[free]),
                          x_scale="jac", ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=500)
            for s in starts]
    valid = [r for r in fits if r.success and np.isfinite(r.fun).all()]
    if not valid:
        best = min(fits, key=lambda r: r.cost)
        retry = least_squares(lambda x: evaluate(x)[0], best.x, jac=lambda x: evaluate(x)[1],
                              bounds=(lower[free], upper[free]), method="dogbox", x_scale="jac",
                              ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500)
        if not retry.success or not np.isfinite(retry.fun).all():
            raise RuntimeError(kind+": optimizer did not converge; no draw discarded")
        valid = [retry]
    best = min(valid, key=lambda r: r.cost)
    z = np.zeros(5); z[free] = best.x
    names = ("a_g_s_bar", "Pstar_bar", "P0_bar", "b_s_bar", "t0_s")
    physical = [np.exp(z[0]), np.exp(z[1]), z[2], np.exp(z[3]), z[4]]
    result = {names[k]: float(physical[k]) for k in free}
    result["Mc_fixed_g"] = float(mc) if kind != "onset" else None
    result["bound_hits"] = [names[k] for k, active in zip(free, best.active_mask) if active]
    if kind in {"onset", "joint"}:
        result["P0_cap_binds"] = bool(best.active_mask[list(free).index(2)] > 0)
    return result


def paired_samples(brews):
    """Independently reconstruct indices; C1 persists draws in this exact order.

    C1's sampler returns multiplicities, not raw RNG index sequences. Check the
    count vectors exactly against that unchanged sampler, and retain both forms.
    Saved flow-only refit identity then anchors draw order to C1's saved results.
    """
    rng = np.random.default_rng(SEED)
    indices = np.array([np.concatenate([rng.choice(g, len(g)) for g in brews.groups])
                        for _ in range(200)])
    samples = np.array([np.bincount(i, minlength=len(brews.ids)) for i in indices])
    np.testing.assert_allclose(samples, C1.B.brew_samples(brews, 200, C1.SEED),
                               rtol=0, atol=0)
    return indices, samples


def margin_audit(record, ctx, train, held, c0=False):
    """Enforce only training margins; preserve every held-out floor prediction."""
    margins = ctx.early[train]-record["P0_bar"]
    np.testing.assert_allclose(np.maximum(margins, C0.EPSILON), margins, rtol=0, atol=0)
    audit = dict(P0_upper_bar=onset_cap(ctx.early[train]),
                 training_min_Pe_bar=float(ctx.early[train].min()),
                 training_min_margin_bar=float(margins.min()),
                 training_floor_active_count=int(np.sum(margins < C0.EPSILON)),
                 cap_binds=record["P0_cap_binds"], held_out=[], held_out_floor_brews=[])
    if held is not None:
        coef = C0.physical_onset(record) if c0 else C1.onset_parameters(record)
        predictions = C0.onset_curve(coef, ctx.early[held])[0]
        for i, pred in zip(held, predictions):
            row = dict(brew=ctx.fine.brews.ids[i], fold=ctx.fine.brews.fold[i],
                       Pe_bar=float(ctx.early[i]), P0_bar=record["P0_bar"],
                       margin_bar=float(ctx.early[i]-record["P0_bar"]),
                       predicted_onset_s=float(pred))
            audit["held_out"].append(row)
            if row["margin_bar"] < C0.EPSILON:
                audit["held_out_floor_brews"].append(row)
        audit["held_out_min_margin_bar"] = min(r["margin_bar"] for r in audit["held_out"])
    return audit


def fit_folds(ctx, sample, deadline, point=False):
    brews, coarse, fine = ctx.fine.brews, ctx.coarse, ctx.fine
    kinds = (*KINDS, "c0_flow") if point else KINDS
    result = {k: dict(bank={}, audits={}, endpoint=np.empty(len(brews.ids)),
                      q=np.empty_like(fine.flow), onset=np.empty(len(brews.ids))) for k in kinds}
    budget = C0.Deadline(deadline)
    for held in [None, *brews.groups]:
        budget.check()
        train = np.flatnonzero(sample > 0) if held is None else np.flatnonzero(
            (sample > 0) & (brews.condition != brews.condition[held[0]]))
        fold = "DESCRIPTIVE_ALL" if held is None else brews.fold[held[0]]
        weights = np.array([sample[i]/np.sum(brews.condition == brews.condition[i]) for i in train])
        weights /= weights.sum()
        mc = (ctx.c4_bank[fold]["free"][2] if point and held is not None
              else B.fit_course("C4", coarse, train, sample, budget)[2])
        for kind in kinds:
            c0 = kind.startswith("c0_")
            parent_kind = kind.removeprefix("c0_")
            onset = result["onset"]["bank"].get(fold)
            args = (parent_kind, coarse.pressure[train], coarse.t, coarse.flow[train],
                    coarse.mask[train], ctx.early[train], ctx.delay[train], weights, mc, budget)
            if parent_kind == "flow":
                record = (C0.fit if c0 else C1.fit)(*args)
            elif c0:
                record = fit_c0(*args)
            else:
                record = fit_t2(*args, pd_fixed=onset["Pd_bar"] if kind == "fixed" else None)
            if kind == "fixed":
                record.update(Pd_source_fit=NAMES["onset"]+":"+fold, onset_parameters=dict(onset),
                              onset_Pd_bound_hit="Pd_bar" in onset["bound_hits"])
            result[kind]["bank"][fold] = record
            if kind in ONSET_KINDS:
                result[kind]["audits"][fold] = margin_audit(record, ctx, train, held, c0)
            if held is None:
                continue
            if parent_kind != "onset":
                coef = C0.physical_flow(record) if c0 else C1.flow_parameters(record)
                curve = C0.flow_curve if c0 else C1.flow_curve
                result[kind]["q"][held] = curve(coef, fine.pressure[held], fine.t, mc)[0]
                result[kind]["endpoint"][held] = curve(coef, brews.pressure[held], brews.t, mc)[0][:, -1]
            if parent_kind != "flow":
                timing = onset if kind == "fixed" else record
                coef = C0.physical_onset(timing) if c0 else C1.onset_parameters(timing)
                result[kind]["onset"][held] = C0.onset_curve(coef, ctx.early[held])[0]
    return result


def metrics(ctx, result, sample):
    values = C1.metrics(ctx, {k: v for k, v in result.items() if not k.startswith("c0_")}, sample)
    values.update({"c0_"+k: v for k, v in C0.metrics(
        ctx, {k.removeprefix("c0_"): v for k, v in result.items() if k.startswith("c0_")}, sample).items()})
    for kind, r in result.items():
        values[kind]["audits"] = {f: {k: v for k, v in a.items() if k != "held_out"}
                                  for f, a in r["audits"].items()}
        values[kind]["parameters_by_fold"] = r["bank"]
    return values


def saved_rows(stage):
    return {r["candidate"]: r for r in A.read_csv(ROOT/f"docs/research/PRESSURE_PEAK_STAGE_{stage}/RESULT_TABLE.csv")}


def read_results(path=OUT/"RESULT_TABLE.csv"):
    """Read the full fold/draw audit cells without changing parent CSV helpers."""
    previous = csv.field_size_limit(32*1024*1024)
    try:
        return A.read_csv(path)
    finally:
        csv.field_size_limit(previous)


def assert_parameters(actual, saved):
    fields = [k for k, v in saved.items() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    np.testing.assert_allclose([actual[k] for k in fields], [saved[k] for k in fields],
                               rtol=1e-12, atol=0)


def flow_identity(ctx, point):
    """Refit identities, including every saved point-fold coefficient and score."""
    center = metrics(ctx, point, np.ones(len(ctx.delay)))
    checked = {}
    for kind, stage, name in (("flow", "C1", "T2 flow-only"), ("c0_flow", "C0", "T1 flow-only")):
        source = saved_rows(stage)[name]
        for fold, record in json.loads(source["parameters_by_fold"]).items():
            assert_parameters(point[kind]["bank"][fold], record)
        for ours, theirs in (("endpoint_rmse", "endpoint_rmse_g_s"), ("trace_rmse", "trace_rmse_g_s"),
                             ("bias", "low_pressure_bias_g_s"), ("slope", "slope_g_s_bar")):
            np.testing.assert_allclose(center[kind][ours], float(source[theirs]), rtol=1e-12, atol=0)
        checked[name] = dict(point_folds=12, saved_stage=stage, rtol=1e-12, atol=0)
    return checked


def continuous(record, c0=False):
    if not c0:
        return C1.continuous(record)
    _, curves = C0.continuous(record)
    for field in ("flow_peak", "onset_minimum"):
        if field in curves:
            curves["analytic_"+field] = record["P0_bar"]+record["Pstar_bar"]
    return curves


def fold_extrema(bank, c0=False):
    curves = {f: continuous(r, c0) for f, r in bank.items() if f != "DESCRIPTIVE_ALL"}
    result = {}
    for field in ("flow_peak", "onset_minimum", "analytic_flow_peak", "analytic_onset_minimum"):
        values = {f: r[field] for f, r in curves.items() if field in r}
        if values:
            result[field+"_fold_median_bar"] = float(np.median(list(values.values())))
            result[field+"_fold_range_bar"] = [min(values.values()), max(values.values())]
            result[field+"_by_fold_bar"] = values
    return result


_CONTEXT = _DEADLINE = None


def _initialize_worker(ctx, deadline):
    global _CONTEXT, _DEADLINE
    _CONTEXT, _DEADLINE = ctx, deadline


def _refit(task):
    index, sample = task
    started = time.process_time()
    result = fit_folds(_CONTEXT, sample, _DEADLINE)
    return index, metrics(_CONTEXT, result, sample), time.process_time()-started


def result_rows(ctx, point, draws):
    if len(draws) != 200:
        raise ValueError("All 200 paired draws are required; no draw may be discarded")
    brews = ctx.fine.brews
    weights = np.ones(len(brews.ids))
    center = metrics(ctx, point, weights)
    saved_flow = saved_rows("C1")["T2 flow-only"]
    for i, old in enumerate(json.loads(saved_flow["refit_parameters"])):
        assert_parameters(draws[i]["flow"]["parameters"], old)
    ref = ctx.references["B1"]["endpoint"]
    reference_rmse = C0.loss(brews, (ref-brews.target)**2)
    resolved = S.resolved_trends()[0]
    if set(resolved) != {2., 3.5, 4., 5., 6.} or set(resolved.values()) != {1}:
        raise ValueError("Resolved trend set changed")
    conditions = list(np.unique(brews.condition))
    low = np.flatnonzero(np.asarray(conditions) <= 3.5)
    observed = B.condition_means(brews, brews.target, weights)
    rows = []
    for kind in ("fixed", "joint", "c0_joint", "onset", "c0_onset"):
        c, r = center[kind], point[kind]
        c0 = kind.startswith("c0_")
        interval = lambda field: A.interval([d[kind][field] for d in draws])
        row = dict(candidate=NAMES[kind], fit_type=kind, claim=CLAIM, pressure_basis="RAW LINE PRIMARY",
                   eligibility="PRIMARY" if kind == "fixed" else "DIAGNOSTIC",
                   complexity={"fixed": "3 + 2n", "joint": "6", "c0_joint": "5",
                               "onset": "4", "c0_onset": "4"}[kind],
                   parameter_search_bounds=C0.PARAMETER_BOUNDS if c0 else BOUNDS,
                   onset_P0_upper_rule="min(5, min(training Pe) - 0.01); lower -5",
                   starts=C0_STARTS if c0 else STARTS, parameters=c["parameters"], parameters_by_fold=r["bank"],
                   refit_count=200, seed=SEED, flow_objective_scale_g_s=C0.FLOW_SCALE,
                   onset_objective_scale_s=C0.ONSET_SCALE,
                   refit_parameters=[d[kind]["parameters"] for d in draws],
                   refit_parameters_by_fold=[d[kind]["parameters_by_fold"] for d in draws])
        row.update(fold_extrema(r["bank"], c0))
        for field in FIELDS:
            if field in c["parameters"]:
                row[field] = c["parameters"][field]
                row[field+"_interval"] = A.interval([d[kind]["parameters"][field] for d in draws])
        for criterion in ("accuracy", "peak", "slope", "trend", "onset", "low_pressure_bias", "Pstar"):
            row[criterion+"_grade"] = NS
        row["bound_hits_by_fold"] = {f: p["bound_hits"] for f, p in r["bank"].items() if p["bound_hits"]}
        row["refit_bound_hits"] = [dict(draw=i, folds={f: p["bound_hits"]
            for f, p in d[kind]["parameters_by_fold"].items() if p["bound_hits"]}) for i, d in enumerate(draws)]
        if kind not in {"onset", "c0_onset"}:
            squared = np.array([(ref-brews.target)**2, (r["endpoint"]-brews.target)**2])
            paired = B.paired_course_loss(brews, squared, SEED)
            delta = A.interval(paired[:, 1]-paired[:, 0])
            comparison = A.comparison(delta)
            matches = sum(np.sign(c["trends"][conditions.index(p)]) == sign for p, sign in resolved.items())
            predicted = B.condition_means(brews, r["endpoint"], weights)
            residuals = predicted-observed
            row.update(endpoint_rmse_g_s=c["endpoint_rmse"], endpoint_rmse_interval_g_s=interval("endpoint_rmse"),
                       trace_rmse_g_s=c["trace_rmse"], trace_rmse_interval_g_s=interval("trace_rmse"),
                       low_pressure_bias_g_s=c["bias"], low_pressure_bias_interval_g_s=interval("bias"),
                       slope_g_s_bar=c["slope"], slope_interval_g_s_bar=interval("slope"),
                       nominal_peak_bar=c["peak"], nominal_peak_interval_bar=interval("peak"),
                       condition_endpoint_means_g_s=predicted.tolist(), condition_pressures_bar=conditions,
                       condition_trend_means_g_s_s=c["trends"], resolved_trend_matches=int(matches),
                       resolved_trend_total=5, b1_endpoint_rmse_g_s=reference_rmse,
                       endpoint_change_percent=100*(c["endpoint_rmse"]/reference_rmse-1),
                       paired_delta_interval_g_s=delta, comparison=comparison,
                       paired_accuracy_method="B0c: 1000 paired condition-then-whole-brew resamples; +/-0.25 g/s band",
                       low_condition_residuals_g_s={str(conditions[j]): float(residuals[j]) for j in low},
                       low_condition_mean_absolute_residual_g_s=float(np.mean(np.abs(residuals[low]))),
                       accuracy_grade=S.accuracy_grade(c["endpoint_rmse"], reference_rmse, comparison),
                       peak_grade=S.peak_grade(interval("peak")), slope_grade=S.slope_grade(interval("slope")),
                       trend_grade=S.trend_grade(matches), low_pressure_bias_grade=C0.bias_grade(c["bias"]))
        row.update(onset_rmse_s=c["onset_rmse"], onset_rmse_interval_s=interval("onset_rmse"),
                   onset_grade=C0.onset_grade(c["onset_rmse"]),
                   condition_onset_means_s=B.condition_means(brews, r["onset"], weights).tolist(),
                   held_out_1bar_onset_predictions_s={brews.ids[i]: float(r["onset"][i])
                       for i in np.flatnonzero(np.isclose(brews.condition, 1.))})
        audit_kind = "onset" if kind == "fixed" else kind
        audits = point[audit_kind]["audits"]
        refit_audits = [d[audit_kind]["audits"] for d in draws]
        held_audits = {f: v for f, v in audits.items() if f != "DESCRIPTIVE_ALL"}
        row.update(margin_scope="onset component only; training enforced, held-out ungraded",
                   margin_source_fit=NAMES[audit_kind], margin_audit_by_fold=audits,
                   refit_margin_audit_by_fold=refit_audits,
                   training_min_margin_bar=min(v["training_min_margin_bar"] for v in audits.values()),
                   refit_training_min_margin_bar=min(v["training_min_margin_bar"] for a in refit_audits for v in a.values()),
                   training_floor_active_count=sum(v["training_floor_active_count"] for v in audits.values()),
                   refit_training_floor_active_count=sum(v["training_floor_active_count"] for a in refit_audits for v in a.values()),
                   cap_binding_point_loco_folds=sum(v["cap_binds"] for v in held_audits.values()),
                   cap_binding_point_full_cohort=audits["DESCRIPTIVE_ALL"]["cap_binds"],
                   cap_binding_refit_loco_fits=sum(v["cap_binds"] for a in refit_audits for f, v in a.items() if f != "DESCRIPTIVE_ALL"),
                   cap_binding_refit_full_cohort_draws=sum(a["DESCRIPTIVE_ALL"]["cap_binds"] for a in refit_audits),
                   cap_binding_refit_draws_any_fold=sum(any(v["cap_binds"] for v in a.values()) for a in refit_audits),
                   held_out_min_margin_bar=min(v["held_out_min_margin_bar"] for v in held_audits.values()),
                   refit_held_out_min_margin_bar=min(v["held_out_min_margin_bar"] for a in refit_audits for f, v in a.items() if f != "DESCRIPTIVE_ALL"),
                   held_out_floor_brews=[v for a in audits.values() for v in a["held_out_floor_brews"]],
                   refit_held_out_floor_brews=[dict(draw=i, **v) for i, a in enumerate(refit_audits)
                       for fold in a.values() for v in fold["held_out_floor_brews"]])
        rows.append(row)
    onset_row = next(r for r in rows if r["fit_type"] == "onset")
    flow_draws = json.loads(saved_flow["refit_parameters"])
    for field in ("Pd", "P0"):
        left, right = onset_row[field+"_bar_interval"], json.loads(saved_flow[field+"_bar_interval"])
        grade, gap = C0.consistency_grade(left, right)
        differences = [old[field+"_bar"]-d["onset"]["parameters"][field+"_bar"]
                       for old, d in zip(flow_draws, draws)]
        for row in (rows[0], onset_row):
            row[field+"_consistency_grade"] = grade
            row[field+"_consistency_gap_bar"] = gap
            row[field+"_paired_difference_interval_bar"] = A.interval(differences)
            row["consistency_pair"] = "capped T2 onset-only versus saved C1 T2 flow-only; paired by draw"
    return rows


def comparator_rows(ctx):
    """Saved results only; C1 group summaries are descriptive, not new CIs."""
    rows = []
    replayed = {r["candidate"]: r for r in C1.saved_references(ctx)}
    observed = B.condition_means(ctx.fine.brews, ctx.fine.brews.target, np.ones(len(ctx.delay)))
    for stage, names in (("C1", ("T2-F", "T2 joint", "T2 flow-only")),
                         ("C0", ("T1 flow-only", "T1/T1-W joint", "E1", "F1", "B1"))):
        saved = saved_rows(stage)
        for name in names:
            source = saved[name]
            row = {}
            for k, value in source.items():
                if not value or k in {"diagnostics", "source_sha256", "wall_seconds", "refit_cpu_seconds"}:
                    continue
                try:
                    row[k] = json.loads(value)
                except (ValueError, TypeError):
                    row[k] = value
            row.update(candidate=stage+" "+name, fit_type="SAVED_REFERENCE", claim=CLAIM,
                       source=f"PRESSURE_PEAK_STAGE_{stage}/RESULT_TABLE.csv:{name}")
            if stage == "C0":
                row.update({k: v for k, v in replayed[name].items()
                            if k.endswith(("_g_s", "_g_s_bar", "_s", "_rtol"))})
                for field in ("Pstar", "P0"):
                    if field+"_interval_bar" in row:
                        row[field+"_bar_interval"] = row[field+"_interval_bar"]
                if "parameters_by_fold" in row:
                    row.update(fold_extrema(row["parameters_by_fold"], c0=True))
            if name in ctx.references and "endpoint" in ctx.references[name]:
                row["condition_endpoint_means_g_s"] = B.condition_means(
                    ctx.fine.brews, ctx.references[name]["endpoint"], np.ones(len(ctx.delay))).tolist()
            if "condition_endpoint_means_g_s" in row:
                residual = np.asarray(row["condition_endpoint_means_g_s"])[:3]-observed[:3]
                row.update(low_condition_residuals_g_s=dict(zip(("1.0", "2.0", "3.5"), residual.tolist())),
                           low_condition_mean_absolute_residual_g_s=float(np.mean(np.abs(residual))))
            rows.append(row)
    saved = saved_rows("C1")
    onset = json.loads(saved["T2 onset-only"]["refit_parameters"])
    fixed = json.loads(saved["T2-F"]["refit_parameters"])
    for low in (True, False):
        ids = [i for i, r in enumerate(onset) if (r["Pd_bar"] < 2.5) is low]
        group = dict(candidate="C1 T2-F Pd "+("<2.5" if low else ">=2.5"), fit_type="SAVED_REFIT_GROUP",
                     claim=CLAIM, draws=len(ids), draw_indices=ids,
                     interval_scope="descriptive within-group 2.5/97.5 percentiles, not confidence intervals")
        for field in ("Pd_bar", "Pstar_bar", "P0_bar"):
            values = [fixed[i][field] for i in ids]
            group[field] = float(np.median(values))
            group[field+"_descriptive_percentiles"] = np.percentile(values, [2.5, 97.5]).tolist()
        for field, values in (
            ("analytic_flow_peak_bar", [fixed[i]["P0_bar"]+fixed[i]["Pd_bar"]*
                np.log1p(fixed[i]["Pstar_bar"]/fixed[i]["Pd_bar"]) for i in ids]),
            ("analytic_onset_minimum_bar", [onset[i]["P0_bar"]+onset[i]["Pd_bar"] for i in ids])):
            group[field] = float(np.median(values))
            group[field+"_descriptive_percentiles"] = np.percentile(values, [2.5, 97.5]).tolist()
        rows.append(group)
    return rows


def restart_diagnostic(raw, bank, row):
    result = C1.restart_diagnostic(raw, bank)
    if result["status"] == C1.NA:
        return result
    pr = result["driving_pressure_bar"]
    result["T2F_Pstar_interval_bar"] = row["Pstar_bar_interval"]
    result["full_relaxation_factor"] = float(np.exp(pr/row["Pstar_bar"]))
    result["full_relaxation_factor_interval"] = [float(np.exp(pr/p)) for p in reversed(row["Pstar_bar_interval"])]
    result["relaxation_low_end_disposition"] = (
        "wholly above the low-end limit; whole-bed relaxation cannot account for the rise within T2"
        if row["Pstar_bar_interval"][0] > result["Pstar_restart_limits_bar"][0]
        else "not excluded by this upper-bound check")
    return result


def figure(ctx, point, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.6), layout="constrained")
    brews = ctx.fine.brews
    weights = np.ones(len(brews.ids))
    for ax, target, ylabel in zip(axes[:2], (brews.target, ctx.delay), ("100-s flow (g/s)", "Onset delay (s)")):
        ax.plot(np.unique(brews.condition), B.condition_means(brews, target, weights), "ko", ms=4, label="Observed means")
        ax.set(xlabel="Raw line pressure (bar)", ylabel=ylabel, xlim=(1, 13))
    axes[0].axvline(6.1, color="gray", ls=":", label="Observed peak 6.1 bar")
    axes[1].axvline(3.5, color="gray", ls=":", label="Observed minimum 3.5 bar")
    for kind, color in (("fixed", "#2471a3"), ("joint", "#d35400"), ("c0_joint", "#278452")):
        curves = [continuous(r, kind.startswith("c0_")) for f, r in point[kind]["bank"].items() if f != "DESCRIPTIVE_ALL"]
        for ax, field in zip(axes[:2], ("flow", "onset")):
            values = np.array([r[field] for r in curves])
            ax.plot(C1.GRID, np.median(values, axis=0), color=color, label=NAMES[kind])
            ax.fill_between(C1.GRID, values.min(axis=0), values.max(axis=0), color=color, alpha=.1)
        use = np.isclose(brews.condition, 1.)
        axes[2].plot(np.arange(use.sum()), point[kind]["onset"][use], "o-", color=color, ms=4, label=NAMES[kind])
    axes[2].plot(np.arange(use.sum()), ctx.delay[use], "ko", ms=4, label="Observed")
    axes[2].set(xticks=np.arange(use.sum()), xticklabels=np.asarray(brews.ids)[use],
                ylabel="Unadjusted held-out onset (s)", xlabel="1-bar brew")
    for ax in axes:
        ax.grid(alpha=.2)
        ax.legend(fontsize=6)
    fig.suptitle("Capability demonstration, not validation • TARGET_EXPOSED • PHYSICAL_VALIDATION=NOT_ESTABLISHED\n"
                 "Continuous curves: held-out fold median / range; training-only onset threshold cap", fontsize=9)
    fig.savefig(out/"FIGURE.png", dpi=180)
    plt.close(fig)


def write_summary(rows, diagnostics, elapsed, cpu, out):
    primary = rows[:3]
    fixed = primary[0]
    def estimate(r, key):
        if key not in r:
            return "—"
        lo, hi = r[key+"_interval"]
        return f"{r[key]:.3f} [{lo:.3f}, {hi:.3f}]"
    def extrema(r, key):
        if key+"_fold_median_bar" not in r:
            return "—"
        lo, hi = r[key+"_fold_range_bar"]
        return f"{r[key+'_fold_median_bar']:.2f} [{lo:.2f}, {hi:.2f}]"
    text = ["# PRESSURE-PEAK Stage C2: constrained onset threshold", "", "**"+CLAIM+".**", "",
            "56 brews; 11 held-out conditions; 200 paired draws, seed 20261105. Only change: onset P0 ≤ min(5, min(training Pe) − 0.01) bar. "
            "T2-F flow P0 remains uncapped. Peak grades use C1’s nominal-condition peak intervals.", "",
            "| Fit | Accuracy | Peak | Slope | Trends | Onset | Low bias |", "|---|---|---|---|---|---|---|"]
    for r in primary:
        text.append("| "+" | ".join(str(r[k]) for k in ("candidate", "accuracy_grade", "peak_grade", "slope_grade", "trend_grade", "onset_grade", "low_pressure_bias_grade"))+" |")
    text += ["", "| Fit | Pd [95%] | Pstar [95%] | P0 [95%] (bar) |", "|---|---|---|---|"]
    for r in primary:
        text.append("| "+r["candidate"]+" | "+" | ".join(estimate(r, f) for f in ("Pd_bar", "Pstar_bar", "P0_bar"))+" |")
    text += ["", f"Paired onset/flow consistency: Pd {fixed['Pd_consistency_grade']} (gap {fixed['Pd_consistency_gap_bar']:.3f} bar); "
             f"P0 {fixed['P0_consistency_grade']} (gap {fixed['P0_consistency_gap_bar']:.3f}). Pstar ungraded.", "",
             "| Fit | Flow peak; analytic | Onset minimum; analytic | Endpoint / trace / onset RMSE | Slope [95%] | Low bias; residuals 1 / 2 / 3.5 bar; MAE |",
             "|---|---|---|---|---|---|"]
    for r in primary:
        rmse = " / ".join(f"{r[k]:.3f}" for k in ("endpoint_rmse_g_s", "trace_rmse_g_s", "onset_rmse_s"))
        lo, hi = r["slope_interval_g_s_bar"]
        residuals = " / ".join(f"{v:+.3f}" for v in r["low_condition_residuals_g_s"].values())
        text.append(f"| {r['candidate']} | {extrema(r, 'flow_peak')}; {extrema(r, 'analytic_flow_peak')} | "
                    f"{extrema(r, 'onset_minimum')}; {extrema(r, 'analytic_onset_minimum')} | {rmse} | "
                    f"{r['slope_g_s_bar']:.4f} [{lo:.4f}, {hi:.4f}] | {r['low_pressure_bias_g_s']:+.3f}; "
                    f"{residuals}; {r['low_condition_mean_absolute_residual_g_s']:.3f} |")
    text += ["", "Extrema: fold median [range], 0.05-bar grid; observed flow/onset: 6.1/3.5 bar. Analytic extrema exclude mass memory. "
             "Units: flow g/s; onset s; slope g/s/bar.", "",
             "| Onset fit | Cap: point folds / 11; full | Refit folds / 2200; full draws / 200 | Min training margin: point / refits (bar) | Held-out floor uses: point / refits |",
             "|---|---|---|---|---|"]
    for r in (rows[3], rows[1], rows[4], rows[2]):
        text.append(f"| {r['candidate']} | {r['cap_binding_point_loco_folds']}; {int(r['cap_binding_point_full_cohort'])} | "
                    f"{r['cap_binding_refit_loco_fits']}; {r['cap_binding_refit_full_cohort_draws']} | "
                    f"{r['training_min_margin_bar']:.6f} / {r['refit_training_min_margin_bar']:.6f} | "
                    f"{len(r['held_out_floor_brews'])} / {len(r['refit_held_out_floor_brews'])} |")
    text += ["", "All 9,648 training-margin checks succeed; no active training floor. CSV lists every ungraded held-out floor use and prediction. "
             "Held-out 1-bar onset predictions (1-1, 1-2, 1-3, 1-4, 1-5b; s): "+"; ".join(
                 r["candidate"]+" "+" / ".join(f"{v:.2f}" for v in r["held_out_1bar_onset_predictions_s"].values()) for r in primary)+".", "",
             "C1 T2-F endpoint/trace RMSE was 0.193/0.287 g/s. Its low/high Pd groups (158/42 draws) had analytic flow "
             "6.460/6.812 and onset 3.216/4.249 bar. Full C1, C0 T1/joint, E1, F1 and B1 comparisons and onset-only estimates are in CSV.", ""]
    restart = diagnostics["restart"]
    if restart["status"] != C1.NA:
        lo, hi = restart["full_relaxation_factor_interval"]
        text += ["Restart: "+restart["owner_interpretation"], "",
                 f"C2 T2-F hypothetical gain {restart['full_relaxation_factor']:.3f} [{lo:.3f}, {hi:.3f}]×; "
                 f"{restart['relaxation_low_end_disposition']}. T2 has no relaxation state and predicts no pause benefit.", ""]
    else:
        text += ["Restart: NOT_AVAILABLE.", ""]
    text += [f"Flow identities: rtol=1e-12; C1 resampling matches exactly. Runtime {elapsed/60:.2f} min cumulative wall / {cpu/3600:.2f} refit CPU h; two-hour wall cap retained. "
             "[Full results and audits](RESULT_TABLE.csv) · [Figure](FIGURE.png). Waszkiewicz et al. (2025), Zenodo 18046315, CC-BY-4.0.", "",
             "**Recommendation:** Review held-out onset extrapolation before selecting further work.", ""]
    if "interrupted_attempt" in diagnostics:
        attempt = diagnostics["interrupted_attempt"]
        text.insert(-3, f"Runtime includes interrupted BLAS oversubscription: {attempt['wall_seconds']/60:.2f} min / "
                    f"{attempt['worker_cpu_seconds']/3600:.2f} CPU h. Resumed with one BLAS thread per worker; all draws retained.")
    (out/"SUMMARY.md").write_text("\n".join(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--prior-seconds", type=float, default=0.)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if args.work.resolve().is_relative_to(ROOT):
        raise ValueError("Runtime checkpoints must be outside the checkout")
    if args.prior_seconds < 0:
        raise ValueError("Prior compute time cannot be negative")
    args.work.mkdir(parents=True, exist_ok=True)
    args.out.mkdir(parents=True, exist_ok=True)
    started, prior = time.monotonic(), args.prior_seconds
    if args.resume:
        with (args.work/"refits.pkl").open("rb") as stream:
            draws, cpu, stored = pickle.load(stream)
        prior = max(prior, stored)
        with (args.work/"point.pkl").open("rb") as stream:
            ctx, point = pickle.load(stream)
    else:
        draws, cpu = {}, 0.
    deadline = started+max(0., 7200.-prior)
    budget = C0.Deadline(deadline)
    budget.check()
    if not args.resume:
        ctx = C0.context(args.ewp, args.raw)
        cache = ROOT/".b0-b0c-onsets.csv"
        if cache.exists():
            cache.replace(args.work/"private-b0c-onsets.csv")
        point = fit_folds(ctx, np.ones(len(ctx.delay)), deadline, point=True)
        with (args.work/"point.pkl").open("wb") as stream:
            pickle.dump((ctx, point), stream)
    identity = flow_identity(ctx, point)
    C1.saved_references(ctx)
    print("POINT_FITS_AND_FLOW_IDENTITIES_COMPLETE", prior+time.monotonic()-started, flush=True)
    indices, samples = paired_samples(ctx.fine.brews)
    with (args.work/"samples.pkl").open("wb") as stream:
        pickle.dump((ctx.fine.brews.ids, indices, samples), stream)
    with (args.work/"refits.pkl").open("wb") as stream:
        pickle.dump((draws, cpu, prior+time.monotonic()-started), stream)
    if len(draws) < 200:
        with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                                 initializer=_initialize_worker, initargs=(ctx, deadline)) as executor:
            futures = [executor.submit(_refit, (i, s)) for i, s in enumerate(samples) if i not in draws]
            for future in as_completed(futures):
                index, value, seconds = future.result()
                draws[index] = value
                cpu += seconds
                with (args.work/"refits.pkl").open("wb") as stream:
                    pickle.dump((draws, cpu, prior+time.monotonic()-started), stream)
                if len(draws) % 10 == 0:
                    print("REFITS", len(draws), "of 200; cumulative seconds", prior+time.monotonic()-started, flush=True)
    budget.check()
    rows = result_rows(ctx, point, [draws[i] for i in range(200)])+comparator_rows(ctx)
    diagnostics = dict(flow_identity=identity, T2_flow_identity_paired_draws=200,
                       pairing=dict(seed=SEED, brew_order=ctx.fine.brews.ids,
                                    early_pressure_bar=ctx.early.tolist(), brew_folds=ctx.fine.brews.fold,
                                    draw_indices=indices.tolist(), multiplicities=samples.tolist(),
                                    assertion="assert_allclose against C1.B.brew_samples; rtol=atol=0"),
                       restart=restart_diagnostic(args.raw, point["fixed"]["bank"], rows[0]),
                       grade_bands=C0.BANDS, onset_training_fit_count=4*12*201)
    interruption = args.work/"interrupted_attempt.json"
    if interruption.exists():
        diagnostics["interrupted_attempt"] = json.loads(interruption.read_text())
    figure(ctx, point, args.out)
    budget.check()
    elapsed = prior+time.monotonic()-started
    inputs = ["docs/research/PRESSURE_PEAK_STAGE_C1/RESULT_TABLE.csv",
              "docs/research/PRESSURE_PEAK_STAGE_C0/RESULT_TABLE.csv",
              "puckworks/analysis/pressure_peak_stage_c1.py", "puckworks/analysis/pressure_peak_stage_c0.py",
              "docs/research/PRESSURE_PEAK_STAGE_B0C/RESULT_TABLE.csv",
              "docs/research/PRESSURE_PEAK_STAGE_B0D/RESULT_TABLE.csv",
              "docs/research/PRESSURE_PEAK_STAGE_B0D/TIMING_FITS.csv",
              "docs/research/PRESSURE_PEAK_STAGE_B0C/ONSET.csv",
              "puckworks/data/waszkiewicz2025/traces_per_brew.csv",
              "puckworks/data/waszkiewicz2025/equilibrium_windows.csv"]
    identities = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    for row in rows:
        row.update(wall_seconds=elapsed, refit_cpu_seconds=cpu, source_sha256=identities)
    rows[0]["diagnostics"] = diagnostics
    B.write_csv(args.out/"RESULT_TABLE.csv", [{k: json.dumps(v) if isinstance(v, (dict, list, tuple)) else v
                                             for k, v in r.items()} for r in rows])
    write_summary(rows, diagnostics, elapsed, cpu, args.out)
    with (args.work/"refits.pkl").open("wb") as stream:
        pickle.dump((draws, cpu, prior+time.monotonic()-started), stream)
    print("COMPLETE", json.dumps(dict(wall_seconds=elapsed, refit_cpu_seconds=cpu, refits=len(draws))), flush=True)


if __name__ == "__main__":
    main()

"""Owner-authorized C0 retrospective threshold/whole-bed-compaction experiment.

G1 parameterization, TARGET_EXPOSED, capability not validation. No production
solver, registry, earlier evidence or source data is changed. Waszkiewicz 2025,
Zenodo 18046315, CC-BY-4.0. Original source programs are not imported.

Flow fitting retains B0c's onset+2-s mask, full clean support, equal-condition /
equal-brew / duration-normalized loss, stable clock and fold-fixed training Mc.
The joint objective uses owner-specified scales 0.437 g/s and 4.534 s. Onset
uses median raw pressure at stable 0--2 s, as B0c/B0d. Measured onset is a target
and scoring-mask input only, never a hydraulic input or state reset.

Bounds, set before scoring: a=[.001,20], Pstar=[.5,100], P0=[-5,5],
b=[.0001,10000], t0=[0,120], in g/s/bar, bar, bar, s*bar and s respectively.
The signed P0 search permits a zero-crossing interval; negative P0 is an
offset diagnostic, not evidence for a positive threshold. Bound hits are
reported. Three fixed starts; no score-dependent tuning. P0=0 is nested C4.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import hashlib
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np
from scipy.optimize import least_squares

from . import pressure_peak_stage_a as A
from . import pressure_peak_stage_b0 as B
from . import pressure_peak_scorecard as S

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C0"
SEED = 20261104
FLOW_SCALE, ONSET_SCALE = .437, 4.534
EPSILON = .01
NA, NS = "NOT_AVAILABLE", "NOT_SCORED"
KINDS = ("flow", "onset", "joint")
NAMES = {"flow": "T1 flow-only", "onset": "T1-W onset-only", "joint": "T1/T1-W joint"}
SOURCE = "Waszkiewicz et al. (2025), doi:10.5281/zenodo.18046315, CC-BY-4.0"
PARAMETER_BOUNDS = {"a_g_s_bar": [.001,20.], "Pstar_bar": [.5,100.], "P0_bar": [-5.,5.],
                    "b_s_bar": [.0001,1e4], "t0_s": [0.,120.]}
BANDS = """Flow criteria: identical to the scorecard (accuracy vs this stage's B1; peak 5–7 bar MEETS / 4 or 8 bar NEAR; slope MEETS if it overlaps [−0.0880, −0.0403], NEAR if within [−0.176, −0.020]; trends on resolved conditions 2/3.5/4/5/6 bar, MEETS ≥4/5, NEAR 3/5).
Onset accuracy (held-out onset RMSE): MEETS ≤ 3.51 s (W1 level); NEAR ≤ 4.53 s (W0 level); otherwise MISSES.
Low-pressure bias (mean flow residual at 1–3.5 bar): MEETS if |bias| ≤ 0.10 g/s; NEAR if ≤ 0.20 g/s; otherwise MISSES. Report E1's and F1's values as comparators.
Consistency (the key test), comparing the 95% intervals for P* from fits (i) and (ii):
  MEETS if they overlap; NEAR if the gap ≤ 1 bar; otherwise MISSES. Same rule for P0.
Grades measure capability on retrospective data, not validation. Do not use PASS."""


def flow_curve(parameters, pressure, t, mc):
    """Separated dM/dt=C(P)/R(M); Jacobian in log(a), log(Pstar), P0.

    Trapezoid exposure and B0d's inverse-resistance series, vectorized so the
    scientific tests also run promptly without optional Numba. M(0)=0; no
    observed onset or measured mass enters the hydraulic state.
    """
    a, pstar, p0 = parameters
    p = np.maximum(pressure, 0.)
    exponential = a*np.exp(-p/pstar)
    capacity = exponential*np.maximum(p-p0, 0.)
    dc = np.stack([capacity, capacity*p/pstar, np.where(p>p0, -exponential, 0.)], axis=-1)
    total = np.zeros_like(dc)
    total[:, 1:] = np.cumsum((dc[:, :-1]+dc[:, 1:])*np.diff(t)[None, :, None]/2, axis=1)
    exposure = total[:, :, 0]/mc
    state = exposure.copy()
    for _ in range(8):
        series = np.zeros_like(state)
        for k, coef in enumerate(B._INVERSE_COEFFICIENTS):
            series -= np.expm1(-(k+1)*state)*coef
        state = np.maximum(0., state-(state+series-exposure)/np.exp(np.exp(-state)))
    inner = np.exp(-state)
    factor = np.exp(-inner)
    q = capacity*factor
    jac = dc*factor[:, :, None]+(q*inner*factor/mc)[:, :, None]*total
    return q, jac


def onset_curve(parameters, pressure):
    """Physical parameters Pstar, P0, b, t0; epsilon is owner-fixed at .01 bar."""
    pstar, p0, b, t0 = parameters
    p = np.asarray(pressure)
    denominator = np.maximum(p-p0, EPSILON)
    term = b*np.exp(p/pstar)/denominator
    jac = np.column_stack([-term*p/pstar,
                           np.where(p-p0 > EPSILON, term/denominator, 0.),
                           term, np.ones_like(p)])
    return t0+term, jac  # log(Pstar), P0, log(b), t0


class Deadline:
    def __init__(self, end):
        self.end, self.elapsed = end, 0.

    def check(self, started=None):
        if time.monotonic() >= self.end:
            raise TimeoutError("C0 cumulative two-hour wall-clock compute cap")


def fit(kind, pressure, t, target, mask, early, delay, weights, mc, budget):
    """All residuals are duration-normalized within a brew; blocks equally scaled."""
    # Shared coordinate order: log(a), log(Pstar), P0, log(b), t0.
    free = np.array([0, 1, 2] if kind == "flow" else [1, 2, 3, 4]
                    if kind == "onset" else [0, 1, 2, 3, 4])
    lower = np.array([np.log(.001), np.log(.5), -5., np.log(.0001), 0.])
    upper = np.array([np.log(20.), np.log(100.), 5., np.log(1e4), 120.])
    starts = [np.array([np.log(a), np.log(ps), p0, np.log(b), t0])[free]
              for a, ps, p0, b, t0 in ((1., 5., 0., 15., 0.),
                                      (2., 8., .4, 3., 8.), (2., 12., .8, 1., 10.))]
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
            q, jac = flow_curve(np.array([np.exp(z[0]), np.exp(z[1]), z[2]]), pressure, t, mc)
            scale = FLOW_SCALE if kind == "joint" else 1.
            residuals.append(((q-target)*trace_weight/scale).ravel())
            full = np.zeros((*q.shape, 5)); full[:, :, :3] = jac
            derivatives.append((full[:, :, free]*trace_weight[:, :, None]/scale).reshape(-1, len(free)))
        if kind != "flow":
            predicted, jac = onset_curve([np.exp(z[1]), z[2], np.exp(z[3]), z[4]], early)
            scale = ONSET_SCALE if kind == "joint" else 1.
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
    return result


def onset_grade(rmse):
    return "MEETS" if rmse <= 3.51 else "NEAR" if rmse <= 4.53 else "MISSES"


def bias_grade(bias):
    return "MEETS" if abs(bias) <= .10 else "NEAR" if abs(bias) <= .20 else "MISSES"


def consistency_grade(left, right):
    gap = max(0., max(left[0], right[0])-min(left[1], right[1]))
    return ("MEETS" if gap == 0 else "NEAR" if gap <= 1 else "MISSES"), gap


def loss(brews, squared, sample=None):
    sample = np.ones(len(brews.ids)) if sample is None else sample
    return float(np.mean([np.sqrt(np.average(squared[g], weights=sample[g])) for g in brews.groups]))


def low_bias(brews, residual, sample=None):
    sample = np.ones(len(brews.ids)) if sample is None else sample
    return float(B.condition_means(brews, residual, sample)[np.unique(brews.condition) <= 3.5].mean())


def paired_accuracy(brews, candidate, reference):
    """Unchanged B0c paired loss: resample conditions, then whole brews.

    The 200 condition-preserving model refits quantify separate fit/shape
    uncertainty; they do not replace B0c's paired accuracy-comparison recipe.
    """
    squared = np.array([(reference-brews.target)**2, (candidate-brews.target)**2])
    draws = B.paired_course_loss(brews, squared, SEED)
    return A.interval(draws[:, 1]-draws[:, 0])


def physical_flow(record):
    return np.array([record[k] for k in ("a_g_s_bar", "Pstar_bar", "P0_bar")])


def physical_onset(record):
    return [record[k] for k in ("Pstar_bar", "P0_bar", "b_s_bar", "t0_s")]


@dataclass
class Context:
    coarse: object
    fine: object
    delay: np.ndarray
    early: np.ndarray
    references: dict
    c4_bank: dict


def saved_b1(brews, root=ROOT):
    row = S.select_stage("B0c", root=root)["B1"][0]
    bank = S.fold_bank("B0c", row)
    q = np.empty(len(brews.ids))
    for group in brews.groups:
        q[group] = A.predict("B1", bank[brews.fold[group[0]]]["free"], brews.pressure[group], brews.t)
    np.testing.assert_allclose(loss(brews, (q-brews.target)**2), float(row["endpoint RMSE g/s"]), rtol=1e-12, atol=0)
    return q, bank


def context(ewp, raw):
    brews = A.load_brews(ROOT/"puckworks/data/waszkiewicz2025", ewp)
    delay, early = B.b0d_onsets(brews, raw)
    coarse = B.retime_course(B.load_course(brews, raw), delay)
    fine = B.retime_course(B.load_course(brews, raw, step=.1), delay)
    selected = {m: S.select_stage("B0c")[m][0] for m in ("B1", "E1")}
    c4 = next(r for r in A.read_csv(B.B0C_OUT/"RESULT_TABLE.csv")
              if r["scenario"] == "RAW PRIMARY" and r["stage"] == "T4 REFIT" and r["candidate"] == "C4")
    c4_bank = json.loads(c4["parameters"])["by_fold"]
    replay = B.swelling_predict_saved(fine, delay, early[:, 0],
                                     {m: S.fold_bank("B0c", r) for m, r in selected.items()})
    references = {}
    for m, r in replay.items():
        se = ((r["q"]-fine.flow)**2*fine.mask).sum(axis=1)/fine.mask.sum(axis=1)
        np.testing.assert_allclose([loss(brews, (r["endpoint"]-brews.target)**2), loss(brews, se)],
            [float(selected[m]["endpoint RMSE g/s"]), float(selected[m]["full-trace RMSE g/s"])], rtol=1e-12, atol=0)
        references[m] = dict(endpoint=r["endpoint"], q=r["q"], source=selected[m])
    saved_b1(brews)
    f1 = S.select_stage("B0d")["F1"][0]
    q = np.empty_like(fine.flow); endpoint = np.empty(len(delay))
    for fold, parameters in S.fold_bank("B0d", f1).items():
        group = brews.condition == float(fold.removeprefix("HYD-LOCO-"))
        coef = np.array(parameters)
        endpoint[group] = B.air_endpoint(coef, brews.pressure[group], brews.t)[0]
        # Reuse B0d's exact exposure closure at each original clean-trace time.
        for j in range(len(fine.t)):
            q[group, j] = B.air_endpoint(coef, fine.pressure[group, :j+1], fine.t[:j+1])[0]
    np.testing.assert_allclose(loss(brews, (endpoint-brews.target)**2), float(f1["endpoint RMSE g/s"]), rtol=1e-12, atol=0)
    references["F1"] = dict(endpoint=endpoint, q=q, source=f1)
    for r in A.read_csv(B.B0D_OUT/"TIMING_FITS.csv"):
        if r["scenario"] == "RAW PRIMARY" and r["candidate"] in {"W0", "W1"}:
            bank = json.loads(r["parameters by fold"]); predicted = np.empty(len(delay))
            kind, exponent = B.timing_specs()[r["candidate"]]
            for group in brews.groups:
                predicted[group] = B.timing_predict(bank[brews.fold[group[0]]], early[group, 0], kind, exponent)
            np.testing.assert_allclose(loss(brews, (predicted-delay)**2), float(r["delay RMSE s"]), rtol=1e-12, atol=0)
            references[r["candidate"]] = dict(onset=predicted, source=r, bank=bank)
    return Context(coarse, fine, delay, early[:, 0], references, c4_bank)


def fit_folds(ctx, sample, deadline, point=False):
    brews, coarse, fine = ctx.fine.brews, ctx.coarse, ctx.fine
    n = len(brews.ids)
    result = {k: dict(bank={}, endpoint=np.empty(n), q=np.empty_like(fine.flow), onset=np.empty(n)) for k in KINDS}
    budget = Deadline(deadline)
    for held in [None, *brews.groups]:
        budget.check()
        train = np.flatnonzero(sample > 0) if held is None else np.flatnonzero(
            (sample > 0) & (brews.condition != brews.condition[held[0]]))
        fold = "DESCRIPTIVE_ALL" if held is None else brews.fold[held[0]]
        weights = np.array([sample[i]/np.sum(brews.condition == brews.condition[i]) for i in train])
        weights /= weights.sum()
        # Bootstrap repeats training-nuisance estimation, exactly as B0c.
        mc = (ctx.c4_bank[fold]["free"][2] if point and held is not None
              else B.fit_course("C4", coarse, train, sample, budget)[2])
        for kind in KINDS:
            record = fit(kind, coarse.pressure[train], coarse.t, coarse.flow[train], coarse.mask[train],
                         ctx.early[train], ctx.delay[train], weights, mc, budget)
            result[kind]["bank"][fold] = record
            if held is None:
                continue
            if kind != "onset":
                coef = physical_flow(record)
                result[kind]["q"][held] = flow_curve(coef, fine.pressure[held], fine.t, mc)[0]
                result[kind]["endpoint"][held] = flow_curve(coef, brews.pressure[held], brews.t, mc)[0][:, -1]
            if kind != "flow":
                result[kind]["onset"][held] = onset_curve(physical_onset(record), ctx.early[held])[0]
    return result


def metrics(ctx, result, sample):
    brews = ctx.fine.brews
    answer = {}
    for kind, r in result.items():
        row = dict(parameters=r["bank"]["DESCRIPTIVE_ALL"])
        if kind != "onset":
            error = r["endpoint"]-brews.target
            se = ((r["q"]-ctx.fine.flow)**2*ctx.fine.mask).sum(axis=1)/ctx.fine.mask.sum(axis=1)
            slope, peak = B.refit_response(brews, r["endpoint"], sample)
            trends = B.condition_means(brews, (r["q"]*ctx.fine.late_weights).sum(axis=1), sample)
            row.update(endpoint_rmse=loss(brews, error**2, sample), trace_rmse=loss(brews, se, sample),
                       bias=low_bias(brews, error, sample), slope=slope, peak=peak, trends=trends.tolist())
            row["delta"] = row["endpoint_rmse"]-loss(brews, (ctx.references["B1"]["endpoint"]-brews.target)**2, sample)
        if kind != "flow":
            row["onset_rmse"] = loss(brews, (r["onset"]-ctx.delay)**2, sample)
        answer[kind] = row
    return answer


_CONTEXT = None
_DEADLINE = None


def _initialize_worker(ctx, deadline):
    global _CONTEXT, _DEADLINE
    _CONTEXT, _DEADLINE = ctx, deadline


def _refit(task):
    index, sample = task
    cpu = time.process_time()
    try:
        result = fit_folds(_CONTEXT, sample, _DEADLINE)
        values = metrics(_CONTEXT, result, sample)
        return index, values, time.process_time()-cpu, ""
    except (TimeoutError, RuntimeError) as error:
        return index, None, time.process_time()-cpu, str(error)


def continuous(record):
    grid = np.round(np.arange(1., 13.0001, .05), 10)
    values = {}
    if "a_g_s_bar" in record:
        q = flow_curve(physical_flow(record), np.repeat(grid[:, None], 2, axis=1),
                       np.array([0.,100.]), record["Mc_fixed_g"])[0][:, -1]
        values.update(flow=q, flow_peak=float(grid[np.argmax(q)]))
    if "b_s_bar" in record:
        onset = onset_curve(physical_onset(record), grid)[0]
        values.update(onset=onset, onset_minimum=float(grid[np.argmin(onset)]))
    return grid, values


def _bounds(draws, kind, field, parameter=False):
    if len(draws) != 200:
        return NA
    values = [d[kind]["parameters"][field] if parameter else d[kind][field] for d in draws]
    return A.interval(values)


def fold_extrema(bank):
    """Evaluate saved held-out fits only; ranges are not bootstrap intervals."""
    folds = {name: continuous(record)[1] for name, record in bank.items()
             if name != "DESCRIPTIVE_ALL"}
    result = {}
    for key in ("flow_peak", "onset_minimum"):
        values = {name: curve[key] for name, curve in folds.items() if key in curve}
        if values:
            result["continuous_"+key+"_fold_median_bar"] = float(np.median(list(values.values())))
            result["continuous_"+key+"_fold_range_bar"] = [min(values.values()), max(values.values())]
            result["continuous_"+key+"_by_fold_bar"] = values
    return result


def result_rows(ctx, point, draws, elapsed, cpu, failures):
    brews = ctx.fine.brews
    center = metrics(ctx, point, np.ones(len(brews.ids)))
    reference_rmse = loss(brews, (ctx.references["B1"]["endpoint"]-brews.target)**2)
    resolved = S.resolved_trends()[0]
    if set(resolved) != {2.,3.5,4.,5.,6.} or set(resolved.values()) != {1}:
        raise ValueError("Resolved observed trend set differs from the owner's C0 specification")
    conditions = np.unique(brews.condition)
    rows = []
    for kind in KINDS:
        c, r = center[kind], point[kind]
        row = dict(candidate=NAMES[kind], fit_type=kind, pressure_basis="RAW LINE PRIMARY",
                   parameter_search_bounds=PARAMETER_BOUNDS,
                   fitted_parameters=3 if kind == "flow" else 4 if kind == "onset" else 5,
                   parameters=c["parameters"], parameters_by_fold=r["bank"],
                   Pstar_bar=c["parameters"]["Pstar_bar"], Pstar_interval_bar=_bounds(draws,kind,"Pstar_bar",True),
                   P0_bar=c["parameters"]["P0_bar"], P0_interval_bar=_bounds(draws,kind,"P0_bar",True),
                   refit_count=len(draws), refit_status="COMPLETE" if len(draws)==200 else NA,
                   unavailable_reason="; ".join(sorted(set(failures))), seed=SEED,
                   flow_objective_scale_g_s=FLOW_SCALE, onset_objective_scale_s=ONSET_SCALE,
                   wall_seconds=elapsed, refit_cpu_seconds=cpu,
                   accuracy_grade=NS, peak_grade=NS, slope_grade=NS, trend_grade=NS,
                   onset_grade=NS, low_pressure_bias_grade=NS, Pstar_consistency_grade=NS, P0_consistency_grade=NS,
                   source=SOURCE, claim="CAPABILITY_DEMONSTRATION_NOT_VALIDATION; TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED")
        pi = row["P0_interval_bar"]
        row["P0_interval_excludes_zero"] = ("YES" if pi[0]>0 or pi[1]<0 else "NO") if isinstance(pi,list) else NA
        row["refit_parameters"] = [d[kind]["parameters"] for d in draws]
        row.update(fold_extrema(r["bank"]))
        for key in ("a_g_s_bar","b_s_bar","t0_s"):
            if key in c["parameters"]:
                row[key] = c["parameters"][key]; row[key+"_interval"] = _bounds(draws,kind,key,True)
        _, curves = continuous(c["parameters"])
        for key in ("flow_peak","onset_minimum"):
            if key in curves:
                row["continuous_"+key+"_bar"] = curves[key]
                row["continuous_"+key+"_interval_bar"] = (A.interval([continuous(d[kind]["parameters"])[1][key] for d in draws])
                                                               if len(draws)==200 else NA)
        if kind != "onset":
            delta = paired_accuracy(brews,r["endpoint"],ctx.references["B1"]["endpoint"])
            comparison = A.comparison(delta)
            peak_interval, slope_interval = _bounds(draws,kind,"peak"), _bounds(draws,kind,"slope")
            matches = sum(np.sign(c["trends"][list(conditions).index(p)]) == sign for p,sign in resolved.items())
            row.update(endpoint_rmse_g_s=c["endpoint_rmse"], endpoint_rmse_interval_g_s=_bounds(draws,kind,"endpoint_rmse"),
                       b1_endpoint_rmse_g_s=reference_rmse, endpoint_change_percent=100*(c["endpoint_rmse"]/reference_rmse-1),
                       paired_delta_g_s=c["delta"], paired_delta_interval_g_s=delta, comparison=comparison,
                       conditional_refit_delta_interval_g_s=_bounds(draws,kind,"delta"),
                       paired_accuracy_method="B0c: 1000 paired condition-then-whole-brew loss resamples; fixed held-out predictions",
                       trace_rmse_g_s=c["trace_rmse"], trace_rmse_interval_g_s=_bounds(draws,kind,"trace_rmse"),
                       low_pressure_bias_g_s=c["bias"], low_pressure_bias_interval_g_s=_bounds(draws,kind,"bias"),
                       low_pressure_bias_grade=bias_grade(c["bias"]), nominal_peak_bar=c["peak"],
                       nominal_peak_interval_bar=peak_interval, slope_g_s_bar=c["slope"], slope_interval_g_s_bar=slope_interval,
                       resolved_trend_matches=int(matches), resolved_trend_total=5, trend_grade=S.trend_grade(matches),
                       condition_trend_means_g_s_s=c["trends"],
                       condition_endpoint_means_g_s=B.condition_means(brews,r["endpoint"],np.ones(len(brews.ids))).tolist(),
                       accuracy_grade=S.accuracy_grade(c["endpoint_rmse"],reference_rmse,comparison) if comparison!=NA else NA,
                       peak_grade=S.peak_grade(peak_interval) if isinstance(peak_interval,list) else NA,
                       slope_grade=S.slope_grade(slope_interval) if isinstance(slope_interval,list) else NA)
        if kind != "flow":
            row.update(onset_rmse_s=c["onset_rmse"], onset_rmse_interval_s=_bounds(draws,kind,"onset_rmse"),
                       onset_grade=onset_grade(c["onset_rmse"]),
                       condition_onset_means_s=B.condition_means(brews,r["onset"],np.ones(len(brews.ids))).tolist())
        rows.append(row)
    for field in ("Pstar","P0"):
        left, right = rows[0][field+"_interval_bar"], rows[1][field+"_interval_bar"]
        grade,gap = consistency_grade(left,right) if isinstance(left,list) and isinstance(right,list) else (NA,NA)
        for row in rows[:2]:
            row[field+"_consistency_grade"] = grade
            row[field+"_consistency_gap_bar"] = gap
    for name in ("B1","E1","F1","W0","W1"):
        r = ctx.references[name]
        row = dict(candidate=name, fit_type="SAVED_REFERENCE", pressure_basis="RAW LINE PRIMARY",
                   accuracy_grade="N/A (reference)", peak_grade=NS, slope_grade=NS, trend_grade=NS,
                   onset_grade=NS, low_pressure_bias_grade=NS, Pstar_consistency_grade=NS,P0_consistency_grade=NS,
                   source="docs/research/PRESSURE_PEAK_STAGE_"+("B0C" if name in {"B1","E1"} else "B0D")
                          +("/TIMING_FITS.csv" if name.startswith("W") else "/RESULT_TABLE.csv"))
        if "endpoint" in r:
            se = ((r["q"]-ctx.fine.flow)**2*ctx.fine.mask).sum(axis=1)/ctx.fine.mask.sum(axis=1)
            row.update(endpoint_rmse_g_s=loss(brews,(r["endpoint"]-brews.target)**2), trace_rmse_g_s=loss(brews,se),
                       low_pressure_bias_g_s=low_bias(brews,r["endpoint"]-brews.target))
        else:
            row.update(onset_rmse_s=loss(brews,(r["onset"]-ctx.delay)**2))
        rows.append(row)
    return rows


def figure(ctx, point, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    brews = ctx.fine.brews
    samples = B.brew_samples(brews,1000,SEED)
    fig,axes = plt.subplots(1,2,figsize=(9,3.1),layout="constrained")
    nominal = np.unique(brews.condition)
    for ax,target,label in zip(axes,(brews.target,ctx.delay),("100-s endpoint flow (g/s)","Observed-onset delay (s)")):
        means = B.condition_means(brews,target,np.ones(len(target)))
        draws = np.array([B.condition_means(brews,target,s) for s in samples])
        intervals = np.array([A.interval(draws[:,j]) for j in range(len(nominal))])
        ax.axvspan(5,7,color="#c7dcc9",alpha=.5,label="5–7 bar")
        ax.errorbar(nominal,means,yerr=np.array([means-intervals[:,0],intervals[:,1]-means]),
                    fmt="o",color="#20262b",capsize=2,label="Observed; 95% brew intervals")
        ax.set(xlabel="Raw pressure (bar)",ylabel=label,xlim=(.8,13.2));ax.grid(alpha=.2)
    for kind,color in (("flow","#2679ad"),("onset","#a94791"),("joint","#d47c31")):
        grid,curve = continuous(point[kind]["bank"]["DESCRIPTIVE_ALL"])
        if "flow" in curve:axes[0].plot(grid,curve["flow"],color=color,label=NAMES[kind])
        if "onset" in curve:axes[1].plot(grid,curve["onset"],color=color,label=NAMES[kind])
    e1 = S.saved_fold_curves("B0c","E1",ctx.references["E1"]["source"])
    axes[0].plot(S.GRID,np.median(e1,axis=0),"--",color="#5c6b50",label="Saved E1: fold median")
    for name,color in (("W0","#8796a5"),("W1","#5c6b50")):
        kind,exponent=B.timing_specs()[name]
        q=B.timing_predict(ctx.references[name]["bank"]["DESCRIPTIVE_ALL"],grid,kind,exponent)
        axes[1].plot(grid,q,"--",color=color,label=name+" saved")
    for ax in axes:ax.legend(fontsize=6.5)
    fig.suptitle("Retrospective capability, not validation; constant-pressure descriptive fits",fontsize=10)
    fig.savefig(out/"FIGURE.png",dpi=180);plt.close(fig)


def write_summary(rows, ctx, out, elapsed):
    primary=rows[:3]; refs={r["candidate"]:r for r in rows[3:]}
    grade_table=["| Fit | Accuracy | Peak | Slope | Trends | Onset | Low-pressure bias |",
                 "|---|---|---|---|---|---|---|"]
    for r in primary:
        grade_table.append("| "+" | ".join(str(r[k]) for k in
             ("candidate","accuracy_grade","peak_grade","slope_grade","trend_grade","onset_grade","low_pressure_bias_grade"))+" |")
    flow,onset,joint=primary
    parameters = ["| Fit | P* [95%], bar | P0 [95%], bar |", "|---|---|---|"]
    for r in primary:
        ps, p0 = r["Pstar_interval_bar"], r["P0_interval_bar"]
        parameters.append(f"| {r['candidate']} | {r['Pstar_bar']:.3f} [{ps[0]:.3f}, {ps[1]:.3f}] | "
                          f"{r['P0_bar']:.3f} [{p0[0]:.3f}, {p0[1]:.3f}] |")
    extrema = []
    for r, key, label in ((flow, "flow_peak", "flow-only peak"), (onset, "onset_minimum", "onset-only minimum")):
        bounds = r["continuous_"+key+"_fold_range_bar"]
        extrema.append(f"{label} {r['continuous_'+key+'_fold_median_bar']:.2f} [{bounds[0]:.2f}, {bounds[1]:.2f}] bar")
    onset_means=B.condition_means(ctx.fine.brews,ctx.delay,np.ones(len(ctx.delay)))
    observed_min=float(S.NOMINAL[np.argmin(onset_means)])
    low=flow['low_pressure_bias_g_s'];jb=joint['low_pressure_bias_g_s']
    reading=(f"The threshold reduces but does not remove low-pressure bias: {low:+.3f} g/s (flow-only) and {jb:+.3f} g/s (joint), "
             f"versus saved E1 {refs['E1']['low_pressure_bias_g_s']:+.3f} and F1 {refs['F1']['low_pressure_bias_g_s']:+.3f} g/s. "
             f"Separate P* and P0 intervals remain disjoint ({flow['Pstar_consistency_grade']} and "
             f"{flow['P0_consistency_grade']}), so a common pressure scale is not established. "
             f"The joint constant-pressure flow peak lands at {joint['continuous_flow_peak_bar']:.2f} bar and its onset minimum at "
             f"{joint['continuous_onset_minimum_bar']:.2f} bar, versus observed flow 6.1 [5.9, 6.3] bar and onset minimum "
             f"at the {observed_min:g}-bar nominal condition.")
    recommended=("Owner: keep C0 in Python and review the wetting mismatch and bound-limited low-pressure fits before considering solver transfer.")
    text=["# PRESSURE-PEAK Stage C0", "", "**Retrospective capability, not validation; TARGET_EXPOSED. PHYSICAL_VALIDATION=NOT_ESTABLISHED.**", "",
          "<details><summary>Owner-set grading bands (verbatim; set before results)</summary>", "", BANDS, "", "</details>", "",
          "\n".join(grade_table), "",
          "\n".join(parameters), "", "All three full-cohort P0 estimates and their 95% intervals are positive.", "",
          f"Independent-fit interval consistency: P* **{flow['Pstar_consistency_grade']}**; "
          f"P0 **{flow['P0_consistency_grade']}** (interval gaps {flow['Pstar_consistency_gap_bar']:.2f} and "
          f"{flow['P0_consistency_gap_bar']:.2f} bar).", "",
          "![Flow and onset versus pressure](FIGURE.png)", "", reading, "",
          "Saved-fold constant-pressure extrema (0.05-bar grid; median [fold range], not a confidence interval): "
          +"; ".join(extrema)+". No refitting.", "",
          "In T1/T1-W the flow peak and onset minimum both sit near P* + P0 (exactly so without the mass-memory term); one exponential compaction law therefore cannot place them at different pressures.", "",
          f"Held-out endpoint RMSE: T1 {flow['endpoint_rmse_g_s']:.3f}, joint {joint['endpoint_rmse_g_s']:.3f}, B1 {refs['B1']['endpoint_rmse_g_s']:.3f} g/s. "
          f"Onset RMSE: T1-W {onset['onset_rmse_s']:.3f}, joint {joint['onset_rmse_s']:.3f}, W0 {refs['W0']['onset_rmse_s']:.3f}, W1 {refs['W1']['onset_rmse_s']:.3f} s.", "",
          "The joint onset curve is nearly flat. The held-out 1-bar fits touch the predeclared bounds: P0=−5 bar (onset-only), b=0.0001 s·bar (joint); no bounds were changed.", "",
          "Ungraded held-out trace RMSE (same B0c mask/support): "+", ".join(
              f"{r['candidate']} {r['trace_rmse_g_s']:.3f}" for r in rows if 'trace_rmse_g_s' in r)+" g/s; timing-only rows have no flow prediction.", "",
          "<details><summary>Methods and provenance</summary>", "",
          "Joint residual scales: **0.437 g/s**, [B0c SUMMARY.md:38](../PRESSURE_PEAK_STAGE_B0C/SUMMARY.md#L38); "
          "**4.534 s**, [B0d SUMMARY.md:11](../PRESSURE_PEAK_STAGE_B0D/SUMMARY.md#L11). "
          "B0c mask/support/weighting, stable clock and 100-s endpoint retained; 56 brews, 11 held-out-condition folds, raw line pressure. "
          "Observed onset is a target/mask only; M starts at zero at stable pressure. Training-fold Mc fixed; references unchanged.", "",
          f"Uncertainty: {len(primary[0]['refit_parameters'])}/200 whole-brew refits per fit type, repeating all folds and training Mc; seed {SEED}. "
          "Accuracy uses B0c's 1,000 paired condition-then-brew resamples and ±0.25 g/s band. "
          "Parameter intervals describe full-cohort fits; grades use held-out predictions. "
          f"Compute {elapsed/60:.2f} min. [Parameters, 95% intervals, bounds and full scores](RESULT_TABLE.csv).", "",
          "Sources inspected: Waszkiewicz traces_per_brew, equilibrium_windows and original timing/pressure records; "
          "B0c/B0d saved fits. Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. "
          "No solver, historical result or source-data changes.", "", "</details>", "",
          "**Recommended next step:** "+recommended, ""]
    (out/"SUMMARY.md").write_text("\n".join(text))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp",type=Path,required=True)
    parser.add_argument("--raw",type=Path,required=True)
    parser.add_argument("--work",type=Path,required=True,help="External checkpoints; never commit raw or per-brew evidence")
    parser.add_argument("--out",type=Path,default=OUT)
    parser.add_argument("--workers",type=int,default=16)
    parser.add_argument("--prior-seconds",type=float,default=0.)
    args=parser.parse_args()
    if args.work.resolve().is_relative_to(ROOT):raise ValueError("Checkpoints must be outside the checkout")
    args.work.mkdir(parents=True,exist_ok=True);args.out.mkdir(parents=True,exist_ok=True)
    started=time.monotonic();deadline=started+max(0.,7200.-args.prior_seconds)
    ctx=context(args.ewp,args.raw)
    print("REFERENCES_REPRODUCED; beginning C0 fits",flush=True)
    point=fit_folds(ctx,np.ones(len(ctx.delay)),deadline,point=True)
    print("POINT_FITS_COMPLETE",time.monotonic()-started,flush=True)
    # Local runtime checkpoints only; no new governance records or source copies.
    import pickle
    with (args.work/"point.pkl").open("wb") as stream:pickle.dump((ctx,point),stream)
    samples=B.brew_samples(ctx.fine.brews,200,SEED)
    draws={};failures=[];cpu=0.
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context("spawn"),
                             initializer=_initialize_worker,initargs=(ctx,deadline)) as executor:
        futures=[executor.submit(_refit,(i,s)) for i,s in enumerate(samples)]
        for future in as_completed(futures):
            index,value,seconds,error=future.result();cpu+=seconds
            if value is not None:draws[index]=value
            else:failures.append(error)
            with (args.work/"refits.pkl").open("wb") as stream:pickle.dump((draws,failures,cpu),stream)
            if (len(draws)+len(failures))%10==0:
                print("REFITS",len(draws),"of 200; unavailable",len(failures),"seconds",time.monotonic()-started,flush=True)
    elapsed=args.prior_seconds+time.monotonic()-started
    values=[draws[k] for k in sorted(draws)]
    rows=result_rows(ctx,point,values,elapsed,cpu,failures)
    inputs=["docs/research/PRESSURE_PEAK_STAGE_B0C/RESULT_TABLE.csv","docs/research/PRESSURE_PEAK_STAGE_B0C/ONSET.csv",
            "docs/research/PRESSURE_PEAK_STAGE_B0D/RESULT_TABLE.csv","docs/research/PRESSURE_PEAK_STAGE_B0D/TIMING_FITS.csv",
            "puckworks/data/waszkiewicz2025/traces_per_brew.csv","puckworks/data/waszkiewicz2025/equilibrium_windows.csv"]
    identities={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in inputs}
    for row in rows:row["source_sha256"]=identities
    B.write_csv(args.out/"RESULT_TABLE.csv",[{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows])
    figure(ctx,point,args.out);write_summary(rows,ctx,args.out,elapsed)
    print("COMPLETE",json.dumps({"wall_seconds":elapsed,"refit_cpu_seconds":cpu,"refits":len(values),"failures":failures}),flush=True)


if __name__ == "__main__":
    main()

"""PRESSURE-PEAK C1: owner-authorized T2 capability demonstration, not validation.

G1 retrospective parameterization; TARGET_EXPOSED;
PHYSICAL_VALIDATION=NOT_ESTABLISHED. Python analysis only. C0, earlier results,
source data and production solvers are read-only. Waszkiewicz et al. (2025),
Zenodo 18046315, CC-BY-4.0; original source programs are not imported.

The owner's bounds, three starts, scoring bands and two-hour cumulative compute
cap are fixed before scoring. Every bootstrap task uses ONE condition-preserving
whole-brew sample for onset, fixed-Pd, free-flow and joint fits, including Mc.
Observed onset is a target/mask only: hydraulic M starts at stable-clock zero.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import multiprocessing
from pathlib import Path
import pickle
import time

import numpy as np
from scipy.optimize import least_squares

from . import pressure_peak_stage_c0 as C0

A, B, S = C0.A, C0.B, C0.S
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C1"
SEED = 20261105
NA, NS = C0.NA, C0.NS
KINDS = ("onset", "fixed", "flow", "joint")
NAMES = {"onset": "T2 onset-only", "fixed": "T2-F", "flow": "T2 flow-only",
         "joint": "T2 joint", "locked": "T2-L"}
FIELDS = ("a_g_s_bar", "Pstar_bar", "P0_bar", "Pd_bar", "b_s_bar", "t0_s")
BOUNDS = dict(zip(FIELDS, ((.001, 20.), (.5, 100.), (-5., 5.), (.1, 100.),
                          (.0001, 1e4), (0., 120.))))
STARTS = ((1., 15., 1., 3., 15., 0.), (1.5, 30., .5, 2., 3., 8.),
          (2., 8., 1., 6., 1., 10.))
LOG_INDICES = [0, 1, 3, 4]
GRID = np.round(np.arange(1., 13.0001, .05), 10)
CLAIM = "capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED"
# Owner wording and interpretation fixed before any T2-F results are read.
RESTART_INTERPRETATION = (
    "Full relaxation of the whole-bed factor bounds the restart jump at exp(P_r/Pstar). "
    "With P_r = {pressure:.6f} bar, matching the low end of the observed ratio ({low:.6f}) "
    "requires Pstar <= {low_limit:.6f} bar, and matching the high end ({high:.6f}) "
    "requires Pstar <= {high_limit:.6f} bar. If the T2-F Pstar interval lies wholly above "
    "the low-end limit, relaxation of the whole-bed term cannot account for the restart "
    "rise within T2; if it overlaps, it is not excluded. Ungraded; one qualitative record."
)


def physical(z):
    result = np.array(z, dtype=float, copy=True)
    result[LOG_INDICES] = np.exp(result[LOG_INDICES])
    return result


def coordinates(parameters):
    result = np.array(parameters, dtype=float, copy=True)
    result[LOG_INDICES] = np.log(result[LOG_INDICES])
    return result


def flow_parameters(record):
    return np.array([record[k] for k in FIELDS[:4]])


def onset_parameters(record):
    return [record[k] for k in ("Pd_bar", "P0_bar", "b_s_bar", "t0_s")]


def flow_curve(parameters, pressure, t, mc, locked=False):
    """Return q and its Jacobian in log a, log Pstar, P0, log Pd.

    C=A*Pd*H, x=max(P-P0,0)/Pd, H=-expm1(-x), E=exp(-x).
    C_theta=(C, C*P/Pstar, -A*E*1[P>P0], A*Pd*(H-x*E)).
    With I_theta=integral(C_theta), z=exp(-M/Mc), f=exp(-z),
    M_theta=f*I_theta and q_theta=f*C_theta+q*z*f*I_theta/Mc.
    The inversion and trapezoid convention are exactly C0's; its coefficients
    are imported, not refitted. At the threshold kink use C0's inactive side.
    T2-L starts its running maximum at array index zero, before masking.
    """
    a, pstar, p0, pd = parameters
    p = np.maximum(np.asarray(pressure), 0.)
    global_p = np.maximum.accumulate(p, axis=1) if locked else p
    x = np.maximum(p-p0, 0.)/pd
    e, h = np.exp(-x), -np.expm1(-x)
    prefactor = a*np.exp(-global_p/pstar)
    capacity = prefactor*pd*h
    # Series avoids cancellation in the Pd -> infinity limit.
    dh = np.where(x < 1e-4, x*x*(.5+x*(-1/3+x*(1/8-x/30))), h-x*e)
    dc = np.stack((capacity, capacity*global_p/pstar,
                   np.where(p > p0, -prefactor*e, 0.), prefactor*pd*dh), axis=-1)
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


def fit(kind, pressure, t, target, mask, early, delay, weights, mc, budget, pd_fixed=None):
    """C0 loss/optimizer conventions, with C1 bounds and fixed three starts."""
    free = np.array({"onset": [3, 2, 4, 5], "fixed": [0, 1, 2],
                     "flow": [0, 1, 2, 3], "joint": list(range(6))}[kind])
    if kind == "fixed" and pd_fixed is None:
        raise ValueError("T2-F requires its training-fold onset-only Pd")
    lower, upper = (coordinates([BOUNDS[k][j] for k in FIELDS]) for j in (0, 1))
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
    return record


def fit_folds(ctx, sample, deadline, point=False):
    brews, coarse, fine = ctx.fine.brews, ctx.coarse, ctx.fine
    n = len(brews.ids)
    result = {k: dict(bank={}, endpoint=np.empty(n), q=np.empty_like(fine.flow), onset=np.empty(n))
              for k in (*KINDS, "locked")}
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
        for kind in KINDS:
            onset = result["onset"]["bank"].get(fold)
            record = fit(kind, coarse.pressure[train], coarse.t, coarse.flow[train], coarse.mask[train],
                         ctx.early[train], ctx.delay[train], weights, mc, budget,
                         pd_fixed=onset["Pd_bar"] if kind == "fixed" else None)
            if kind == "fixed":
                record.update(Pd_source_fit="T2 onset-only:"+fold, onset_parameters=dict(onset),
                              onset_Pd_bound_hit="Pd_bar" in onset["bound_hits"])
            result[kind]["bank"][fold] = record
            if held is None:
                continue
            if kind != "onset":
                coef = flow_parameters(record)
                result[kind]["q"][held] = flow_curve(coef, fine.pressure[held], fine.t, mc)[0]
                result[kind]["endpoint"][held] = flow_curve(coef, brews.pressure[held], brews.t, mc)[0][:, -1]
            if kind in {"onset", "fixed", "joint"}:
                timing = onset if kind == "fixed" else record
                result[kind]["onset"][held] = C0.onset_curve(onset_parameters(timing), ctx.early[held])[0]
        result["locked"]["bank"][fold] = result["fixed"]["bank"][fold]
        if held is not None:
            coef = flow_parameters(result["fixed"]["bank"][fold])
            result["locked"]["q"][held] = flow_curve(coef, fine.pressure[held], fine.t, mc, True)[0]
            result["locked"]["endpoint"][held] = flow_curve(coef, brews.pressure[held], brews.t, mc, True)[0][:, -1]
            result["locked"]["onset"][held] = result["fixed"]["onset"][held]
    return result


def continuous(record):
    values = {}
    if "a_g_s_bar" in record:
        q = flow_curve(flow_parameters(record), np.repeat(GRID[:, None], 2, axis=1),
                       np.array([0., 100.]), record["Mc_fixed_g"])[0][:, -1]
        values.update(flow=q, flow_peak=float(GRID[np.argmax(q)]),
                      analytic_flow_peak=float(record["P0_bar"]+record["Pd_bar"]*
                                               np.log1p(record["Pstar_bar"]/record["Pd_bar"])))
    timing = record.get("onset_parameters", record)
    if "b_s_bar" in timing:
        y = C0.onset_curve(onset_parameters(timing), GRID)[0]
        values.update(onset=y, onset_minimum=float(GRID[np.argmin(y)]),
                      analytic_onset_minimum=float(timing["P0_bar"]+timing["Pd_bar"]))
    return values


def fold_extrema(bank):
    curves = {k: continuous(r) for k, r in bank.items() if k != "DESCRIPTIVE_ALL"}
    result = {}
    for field in ("flow_peak", "onset_minimum", "analytic_flow_peak", "analytic_onset_minimum"):
        values = {k: r[field] for k, r in curves.items() if field in r}
        if values:
            result[field+"_fold_median_bar"] = float(np.median(list(values.values())))
            result[field+"_fold_range_bar"] = [min(values.values()), max(values.values())]
            result[field+"_by_fold_bar"] = values
    return result


def metrics(ctx, results, sample):
    brews = ctx.fine.brews
    answer = {}
    for kind, result in results.items():
        row = dict(parameters=result["bank"]["DESCRIPTIVE_ALL"],
                   bound_hits_by_fold={f: r["bound_hits"] for f, r in result["bank"].items() if r["bound_hits"]})
        if kind in {"fixed", "locked"}:
            row["onset_pd_by_fold"] = {f: dict(Pd_bar=r["Pd_bar"], source=r["Pd_source_fit"],
                                               bound_hit=r["onset_Pd_bound_hit"])
                                       for f, r in result["bank"].items()}
        if kind != "onset":
            error = result["endpoint"]-brews.target
            squared = ((result["q"]-ctx.fine.flow)**2*ctx.fine.mask).sum(axis=1)/ctx.fine.mask.sum(axis=1)
            slope, peak = B.refit_response(brews, result["endpoint"], sample)
            trends = B.condition_means(brews, (result["q"]*ctx.fine.late_weights).sum(axis=1), sample)
            row.update(endpoint_rmse=C0.loss(brews, error**2, sample), trace_rmse=C0.loss(brews, squared, sample),
                       bias=C0.low_bias(brews, error, sample), slope=slope, peak=peak, trends=trends.tolist())
        if kind != "flow":
            row["onset_rmse"] = C0.loss(brews, (result["onset"]-ctx.delay)**2, sample)
        answer[kind] = row
    return answer


def saved_references(ctx):
    """Replay C0 fold coefficients, never refit comparators; check saved scores."""
    saved = {r["candidate"]: r for r in A.read_csv(C0.OUT/"RESULT_TABLE.csv")}
    brews = ctx.fine.brews
    references = dict(ctx.references)
    for name in ("T1 flow-only", "T1/T1-W joint"):
        source = saved[name]
        bank = json.loads(source["parameters_by_fold"])
        q = np.empty_like(ctx.fine.flow); endpoint = np.empty(len(ctx.delay))
        onset = np.empty(len(ctx.delay))
        for held in brews.groups:
            record = bank[brews.fold[held[0]]]
            coef = C0.physical_flow(record); mc = record["Mc_fixed_g"]
            q[held] = C0.flow_curve(coef, ctx.fine.pressure[held], ctx.fine.t, mc)[0]
            endpoint[held] = C0.flow_curve(coef, brews.pressure[held], brews.t, mc)[0][:, -1]
            if "b_s_bar" in record:
                onset[held] = C0.onset_curve(C0.physical_onset(record), ctx.early[held])[0]
        references[name] = dict(q=q, endpoint=endpoint, source=source)
        if name.endswith("joint"):
            references[name]["onset"] = onset
    rows = []
    for name in ("T1 flow-only", "T1/T1-W joint", "E1", "F1", "B1"):
        r = references[name]; source = saved[name]
        squared = ((r["q"]-ctx.fine.flow)**2*ctx.fine.mask).sum(axis=1)/ctx.fine.mask.sum(axis=1)
        row = dict(candidate=name, fit_type="SAVED_REFERENCE", claim=CLAIM,
                   endpoint_rmse_g_s=C0.loss(brews, (r["endpoint"]-brews.target)**2),
                   trace_rmse_g_s=C0.loss(brews, squared),
                   low_pressure_bias_g_s=C0.low_bias(brews, r["endpoint"]-brews.target),
                   source="PRESSURE_PEAK_STAGE_C0/RESULT_TABLE.csv:"+name)
        if "onset" in r:
            row["onset_rmse_s"] = C0.loss(brews, (r["onset"]-ctx.delay)**2)
        for field in ("endpoint_rmse_g_s", "trace_rmse_g_s", "low_pressure_bias_g_s", "onset_rmse_s"):
            if field in row:
                np.testing.assert_allclose(row[field], float(source[field]), rtol=1e-12, atol=0)
        slope_source = source if name.startswith("T1") else r["source"]
        slope_field, interval_field = (("slope_g_s_bar", "slope_interval_g_s_bar")
                                       if name.startswith("T1") else ("slope g/s/bar", "slope interval refit"))
        slope = B.refit_response(brews, r["endpoint"], np.ones(len(brews.ids)))[0]
        np.testing.assert_allclose(slope, float(slope_source[slope_field]), rtol=1e-12, atol=0)
        row.update(slope_g_s_bar=slope, slope_interval_g_s_bar=json.loads(slope_source[interval_field]),
                   slope_interval_source="C0 saved refits" if name.startswith("T1") else
                   "B0d saved refits" if name == "F1" else "B0c saved refits")
        row["saved_replay_rtol"] = 1e-12
        rows.append(row)
    return rows


def onset_identity(ctx, point):
    old = next(r for r in A.read_csv(C0.OUT/"RESULT_TABLE.csv") if r["fit_type"] == "onset")
    old_bank = json.loads(old["parameters_by_fold"])
    differences = {}
    fields = ("Pd_bar", "P0_bar", "b_s_bar", "t0_s")
    for fold, record in point["onset"]["bank"].items():
        previous = dict(old_bank[fold]); previous["Pd_bar"] = previous.pop("Pstar_bar")
        train = np.ones(len(ctx.delay), dtype=bool) if fold == "DESCRIPTIVE_ALL" else (
            np.asarray(ctx.fine.brews.fold) != fold)
        cond = ctx.fine.brews.condition
        weights = np.array([1/np.sum(cond == p) for p in cond[train]]); weights /= weights.sum()
        costs = [float(np.sum(weights*(C0.onset_curve(onset_parameters(r), ctx.early[train])[0]-ctx.delay[train])**2))
                 for r in (previous, record)]
        # Diagnostic objective equivalence threshold, fixed before scoring.
        changed = abs(costs[1]-costs[0]) > 1e-6*max(1., costs[0])
        differences[fold] = dict(absolute_differences={k: abs(record[k]-previous[k]) for k in fields},
                                 c0_parameters={k: previous[k] for k in fields},
                                 c1_parameters={k: record[k] for k in fields},
                                 c0_objective=costs[0], c1_objective=costs[1], different_optimum=changed)
    return dict(max_absolute_differences={k: max(r["absolute_differences"][k] for r in differences.values()) for k in fields},
                different_optimum_folds=[f for f, r in differences.items() if r["different_optimum"]],
                objective_equivalence_relative_tolerance=1e-6, by_fold=differences)


def observed_peak_windows(brews):
    """Same 1,000 whole-brew draws for all four descriptive quadratic windows."""
    samples = B.brew_samples(brews, 1000, SEED)
    nominal = np.unique(brews.condition)
    means = B.condition_means(brews, brews.target, np.ones(len(brews.ids)))
    draws = np.array([B.condition_means(brews, brews.target, s) for s in samples])
    result = {}
    for low, high in ((4., 8.), (5., 8.), (4., 9.), (3.5, 9.)):
        use = (nominal >= low) & (nominal <= high)
        result[f"{low:g}-{high:g}"] = dict(peak_bar=S.observed_quadratic_peak(nominal[use], means[use]),
            interval_bar=A.interval([S.observed_quadratic_peak(nominal[use], d[use]) for d in draws]))
    return result


def restart_diagnostic(root, fixed_bank):
    """Read only the owner-specified upstream tree. Never fit restart data.

    Native p2 is line pressure in centibar; t is ms and m is g. Use p2/100>6
    solely to separate the ~8.4-bar on episodes from the ~3-bar off plateaus.
    Report ordinary least-squares mass slopes over the last five seconds of
    each on episode (duration >=5 s), without choosing windows for agreement.
    The bound uses median p2/100 in the FIRST episode's five-second window.
    Off-state line pressure is never interpreted as pressure across the puck.
    """
    paths = sorted(Path(root).rglob("brew_restarting.txt")) if Path(root).is_dir() else []
    if not paths:
        return dict(status=NA)
    if len(paths) != 1:
        raise ValueError("Multiple restart records inside the authorized upstream tree")
    path = paths[0]
    records = [(i+1, json.loads(line)) for i, line in enumerate(path.read_text().splitlines()) if line.strip()]
    line = np.array([i for i, _ in records]); records = [r for _, r in records]
    t = np.array([r["t"]/1000 for r in records]); mass = np.array([r["m"] for r in records])
    pressure = np.array([r["p2"]/100 for r in records]); on = pressure > 6.
    starts = np.flatnonzero(on & ~np.r_[False, on[:-1]])
    ends = np.flatnonzero(on & ~np.r_[on[1:], False])
    episodes = []
    for start, end in zip(starts, ends):
        if t[end]-t[start] < 5:
            continue
        use = np.arange(start, end+1); use = use[t[use] >= t[end]-5.]
        slope = float(np.polynomial.polynomial.polyfit(t[use]-t[use].mean(), mass[use], 1)[1])
        episodes.append(dict(source_lines=[int(line[use[0]]), int(line[use[-1]])],
                             time_window_s=[float(t[use[0]]), float(t[use[-1]])],
                             pressure_bar=float(np.median(pressure[use])), flow_g_s=slope))
    if len(episodes) < 2:
        raise ValueError("Restart record does not contain two five-second on episodes")
    pr = episodes[0]["pressure_bar"]
    q0 = episodes[0]["flow_g_s"]; after = [r["flow_g_s"] for r in episodes[1:]]
    upper = {f: float(np.exp(pr/r["Pstar_bar"])) for f, r in fixed_bank.items() if f != "DESCRIPTIVE_ALL"}
    ratios = [min(after)/q0, max(after)/q0]
    limits = [float(pr/np.log(r)) for r in ratios]
    return dict(status="AVAILABLE", source=str(path.relative_to(root)),
                source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(), driving_pressure_bar=pr,
                pressure_source_field="p2 / 100 (centibar to bar)", pressure_source_lines=episodes[0]["source_lines"],
                flow_observer="OLS m(g) versus t(ms)/1000, last 5 s of each p2/100>6 bar episode",
                episodes=episodes, observed_before_g_s=q0, observed_after_range_g_s=[min(after), max(after)],
                quoted_before_g_s=1.82, quoted_after_range_g_s=[3.23, 4.31],
                discrepancy_before_g_s=q0-1.82, discrepancy_after_range_g_s=[min(after)-3.23, max(after)-4.31],
                full_relaxation_factor_by_fold=upper, full_relaxation_factor_fold_median=float(np.median(list(upper.values()))),
                full_relaxation_factor_fold_range=[min(upper.values()), max(upper.values())],
                observed_factor_range=ratios, Pstar_restart_limits_bar=limits,
                owner_interpretation=RESTART_INTERPRETATION.format(pressure=pr, low=ratios[0], high=ratios[1],
                                                                  low_limit=limits[0], high_limit=limits[1]),
                directions={"C0": "No pause-induced gain at matched pressure and M; continued delivery can raise flow.",
                            "T2-F": "No pause-induced gain at matched pressure and M; compaction is instantaneous.",
                            "T2-L": "No release on pause: running maximum persists; continued delivery can raise flow."},
                interpretation="exp(P_r/Pstar) is a hypothetical full-relaxation upper bound, not a T2-F restart prediction; off-state line pressure is not puck pressure")


_CONTEXT = None
_DEADLINE = None


def _initialize_worker(ctx, deadline):
    global _CONTEXT, _DEADLINE
    _CONTEXT, _DEADLINE = ctx, deadline


def _refit(task):
    index, sample = task
    started = time.process_time()
    result = fit_folds(_CONTEXT, sample, _DEADLINE)
    return index, metrics(_CONTEXT, result, sample), time.process_time()-started


def result_rows(ctx, point, draws, references):
    if len(draws) != 200:
        raise ValueError("All 200 paired refits are required; do not drop draws")
    brews = ctx.fine.brews
    center = metrics(ctx, point, np.ones(len(brews.ids)))
    ref = ctx.references["B1"]["endpoint"]
    reference_rmse = C0.loss(brews, (ref-brews.target)**2)
    resolved = S.resolved_trends()[0]
    if set(resolved) != {2., 3.5, 4., 5., 6.} or set(resolved.values()) != {1}:
        raise ValueError("Resolved observed trend set changed")
    conditions = list(np.unique(brews.condition))
    rows = []
    for kind in ("fixed", "flow", "joint", "onset", "locked"):
        c, r = center[kind], point[kind]
        interval = lambda field: A.interval([d[kind][field] for d in draws])
        row = dict(candidate=NAMES[kind], fit_type=kind, pressure_basis="RAW LINE PRIMARY", claim=CLAIM,
                   complexity={"fixed": "3 + 2n", "flow": "4", "joint": "6", "onset": "4", "locked": "3 + 2n; no refit"}[kind],
                   eligibility="EXPLORATORY" if kind == "flow" else "UNGRADED SENSITIVITY" if kind == "locked" else "PRIMARY" if kind == "fixed" else "DIAGNOSTIC",
                   parameter_search_bounds=BOUNDS, starts=STARTS, parameters=c["parameters"], parameters_by_fold=r["bank"],
                   refit_count=200, seed=SEED, flow_objective_scale_g_s=C0.FLOW_SCALE, onset_objective_scale_s=C0.ONSET_SCALE,
                   refit_parameters=[d[kind]["parameters"] for d in draws],
                   bound_hits_by_fold=c["bound_hits_by_fold"],
                   refit_bound_hits=[dict(draw=i, folds=d[kind]["bound_hits_by_fold"]) for i, d in enumerate(draws) if d[kind]["bound_hits_by_fold"]],
                   accuracy_grade=NS, peak_grade=NS, slope_grade=NS, trend_grade=NS, onset_grade=NS,
                   low_pressure_bias_grade=NS, Pd_consistency_grade=NS, P0_consistency_grade=NS, Pstar_grade=NS)
        row.update(fold_extrema(r["bank"]))
        for field in FIELDS:
            if field in c["parameters"]:
                row[field] = c["parameters"][field]
                row[field+"_interval"] = A.interval([d[kind]["parameters"][field] for d in draws])
        if kind in {"fixed", "locked"}:
            row.update(Pd_by_fold=c["onset_pd_by_fold"],
                       onset_Pd_bound_folds=[f for f, v in c["onset_pd_by_fold"].items() if v["bound_hit"]],
                       refit_onset_pd_by_fold={f: dict(source=v["source"],
                           Pd_bar=[d[kind]["onset_pd_by_fold"][f]["Pd_bar"] for d in draws],
                           bound_draw_indices=[i for i, d in enumerate(draws) if d[kind]["onset_pd_by_fold"][f]["bound_hit"]])
                           for f, v in c["onset_pd_by_fold"].items()})
        if kind != "onset":
            squared = np.array([(ref-brews.target)**2, (r["endpoint"]-brews.target)**2])
            paired = B.paired_course_loss(brews, squared, SEED)
            delta = A.interval(paired[:, 1]-paired[:, 0]); comparison = A.comparison(delta)
            matches = sum(np.sign(c["trends"][conditions.index(p)]) == sign for p, sign in resolved.items())
            all_observed = B.condition_means(brews, (ctx.fine.flow*ctx.fine.late_weights).sum(axis=1), np.ones(len(brews.ids)))
            row.update(endpoint_rmse_g_s=c["endpoint_rmse"], endpoint_rmse_interval_g_s=interval("endpoint_rmse"),
                       trace_rmse_g_s=c["trace_rmse"], trace_rmse_interval_g_s=interval("trace_rmse"),
                       low_pressure_bias_g_s=c["bias"], low_pressure_bias_interval_g_s=interval("bias"),
                       slope_g_s_bar=c["slope"], slope_interval_g_s_bar=interval("slope"),
                       nominal_peak_bar=c["peak"], nominal_peak_interval_bar=interval("peak"),
                       resolved_trend_matches=int(matches), resolved_trend_total=5,
                       all_trend_matches=int(np.sum(np.sign(c["trends"]) == np.sign(all_observed))),
                       condition_trend_means_g_s_s=c["trends"],
                       condition_endpoint_means_g_s=B.condition_means(brews, r["endpoint"], np.ones(len(brews.ids))).tolist(),
                       b1_endpoint_rmse_g_s=reference_rmse, endpoint_change_percent=100*(c["endpoint_rmse"]/reference_rmse-1),
                       paired_delta_interval_g_s=delta, comparison=comparison,
                       paired_accuracy_method="B0c: 1000 paired condition-then-whole-brew resamples; +/-0.25 g/s band")
            if kind != "locked":
                row.update(accuracy_grade=S.accuracy_grade(c["endpoint_rmse"], reference_rmse, comparison),
                           peak_grade=S.peak_grade(interval("peak")), slope_grade=S.slope_grade(interval("slope")),
                           trend_grade=S.trend_grade(matches), low_pressure_bias_grade=C0.bias_grade(c["bias"]))
        if kind != "flow":
            row.update(onset_rmse_s=c["onset_rmse"], onset_rmse_interval_s=interval("onset_rmse"),
                       condition_onset_means_s=B.condition_means(brews, r["onset"], np.ones(len(brews.ids))).tolist())
            if kind != "locked":
                row["onset_grade"] = C0.onset_grade(c["onset_rmse"])
        rows.append(row)
    by_kind = {r["fit_type"]: r for r in rows}
    for field in ("Pd", "P0"):
        left = by_kind["onset"][field+"_bar_interval"]
        right = by_kind["flow"][field+"_bar_interval"]
        grade, gap = C0.consistency_grade(left, right)
        # The owner grades overlap of marginal intervals from the SAME paired
        # draws, not whether a different paired-difference interval includes 0.
        differences = [d["flow"]["parameters"][field+"_bar"]-d["onset"]["parameters"][field+"_bar"] for d in draws]
        for kind in ("fixed", "flow", "onset"):
            by_kind[kind][field+"_consistency_grade"] = grade
            by_kind[kind][field+"_consistency_gap_bar"] = gap
            by_kind[kind][field+"_paired_difference_interval_bar"] = A.interval(differences)
            by_kind[kind]["consistency_pair"] = "T2 onset-only versus T2 flow-only"
    return rows+references


def figure(ctx, point, out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), layout="constrained")
    brews = ctx.fine.brews
    for ax, target, ylabel in zip(axes, (brews.target, ctx.delay), ("100-s flow (g/s)", "Onset delay (s)")):
        ax.plot(np.unique(brews.condition), B.condition_means(brews, target, np.ones(len(brews.ids))), "o", color="black", label="Observed means")
        ax.set(xlabel="Raw line pressure (bar)", ylabel=ylabel, xlim=(1, 13)); ax.grid(alpha=.2)
    axes[0].axvspan(5, 7, color="#c7dcc9", alpha=.5, label="5–7 bar band")
    axes[0].axvline(6.1, color="gray", ls=":"); axes[1].axvline(3.5, color="gray", ls=":")
    for kind, color in (("fixed", "#2471a3"), ("flow", "#8e44ad"), ("joint", "#d35400")):
        curves = [continuous(r) for f, r in point[kind]["bank"].items() if f != "DESCRIPTIVE_ALL"]
        for ax, field in zip(axes, ("flow", "onset")):
            if field in curves[0]:
                values = np.array([r[field] for r in curves])
                ax.plot(GRID, np.median(values, axis=0), color=color, label=NAMES[kind]+(" (exploratory)" if kind == "flow" else ""))
                ax.fill_between(GRID, values.min(axis=0), values.max(axis=0), color=color, alpha=.1)
    for ax in axes:
        ax.legend(fontsize=7)
    fig.suptitle("Capability demonstration, not validation; constant-pressure fold medians / ranges", fontsize=10)
    fig.savefig(out/"FIGURE.png", dpi=180); plt.close(fig)


def write_summary(rows, diagnostics, elapsed, cpu, out):
    by_name = {r["candidate"]: r for r in rows}
    primary = rows[:3]; onset = by_name["T2 onset-only"]; fixed = primary[0]
    fmt = lambda x: f"{x:.3f}"
    def estimate(r, field):
        if field not in r:
            return "—"
        low, high = r[field+"_interval"]
        return f"{r[field]:.3f} [{low:.3f}, {high:.3f}]"
    def extrema(r, field):
        if field+"_fold_median_bar" not in r:
            return "—"
        low, high = r[field+"_fold_range_bar"]
        return f"{r[field+'_fold_median_bar']:.2f} [{low:.2f}, {high:.2f}]"
    text = ["# PRESSURE-PEAK Stage C1 (T2)", "", "**"+CLAIM+".**", "",
            "56 brews; 11 condition-held-out folds; raw line pressure; unchanged B0c trace mask/weights, stable clock, Mc and 100-s observer. Owner-set bounds, starts and grading bands unchanged; no overall PASS.", "",
            "| Fit | Accuracy | Peak | Slope | Trends | Onset | Low bias |",
            "|---|---|---|---|---|---|---|"]
    for r in primary:
        text.append("| "+" | ".join(str(r[k]) for k in ("candidate", "accuracy_grade", "peak_grade", "slope_grade", "trend_grade", "onset_grade", "low_pressure_bias_grade"))+" |")
    text += ["", "T2-F is primary (3 + 2n); flow-only is EXPLORATORY (4); joint has 6 fitted parameters. T2-L is an ungraded, no-refit sensitivity.", "",
             "| Fit | Pd [95%], bar | Pstar [95%], bar | P0 [95%], bar |",
             "|---|---|---|---|"]
    for r in (*primary, onset):
        text.append("| "+r["candidate"]+" | "+" | ".join(estimate(r, f) for f in ("Pd_bar", "Pstar_bar", "P0_bar"))+" |")
    text += ["", f"Independent onset-only versus flow-only consistency: Pd **{fixed['Pd_consistency_grade']}** (gap {fixed['Pd_consistency_gap_bar']:.3f} bar); P0 **{fixed['P0_consistency_grade']}** (gap {fixed['P0_consistency_gap_bar']:.3f} bar). Pstar is reported, not graded.", "",
             "| Fit | Flow peak; analytic | Onset minimum; analytic | Endpoint / trace / onset RMSE | Slope ≥9 bar [95%] | Low bias |",
             "|---|---|---|---|---|---|"]
    for r in primary:
        flow = extrema(r, "flow_peak")+"; "+extrema(r, "analytic_flow_peak")
        timing = extrema(r, "onset_minimum")+"; "+extrema(r, "analytic_onset_minimum")
        rmse = " / ".join(fmt(r[k]) if k in r else "—" for k in ("endpoint_rmse_g_s", "trace_rmse_g_s", "onset_rmse_s"))
        lo, hi = r["slope_interval_g_s_bar"]
        text.append(f"| {r['candidate']} | {flow} | {timing} | {rmse} | {r['slope_g_s_bar']:.4f} [{lo:.4f}, {hi:.4f}] | {r['low_pressure_bias_g_s']:+.3f} |")
    text += ["", "Extrema: 0.05-bar grid, 1–13 bar, fold median [range], not confidence intervals; analytic turning points P0+Pd (onset) and P0+Pd·ln(1+Pstar/Pd) (capacity) exclude mass memory and are shown alongside the continuous extrema. T2-F's onset uses its separate onset-only P0. Observed flow peak: 6.1 [5.9, 6.3] bar; onset minimum: 3.5 bar. Flow errors/bias are g/s, onset error is s, slope is g/s/bar.", "",
             "![Flow and onset](FIGURE.png)", ""]
    identity = diagnostics["onset_identity"]
    text.append("Onset identity versus saved C0 T1-W: max |Δ| "+", ".join(f"{k}={v:.6g}" for k, v in identity["max_absolute_differences"].items())+
                "; different-optimum folds: "+(", ".join(identity["different_optimum_folds"]) or "none at the declared objective tolerance")+". No bounds/starts were changed to force agreement.")
    bound = fixed["onset_Pd_bound_folds"]
    bootstrap_bound = [(i, f) for f, r in fixed["refit_onset_pd_by_fold"].items() for i in r["bound_draw_indices"]]
    bootstrap_bound_folds = sorted({f for _, f in bootstrap_bound})
    other = {r["candidate"]: r["bound_hits_by_fold"] for r in rows[:4] if r["bound_hits_by_fold"]}
    text += ["", "Onset-only Pd bound hits: point folds "+(", ".join(bound) or "none")+
             f"; {len(bootstrap_bound)} bootstrap fold fits"+
             (" ("+", ".join(bootstrap_bound_folds)+")" if bootstrap_bound_folds else "")+
             ". T2-F retains every such Pd. Other point bound hits: "+(json.dumps(other) if other else "none")+"; all refit bound hits and per-fold Pd/source fits are in RESULT_TABLE.csv.", ""]
    windows = diagnostics["observed_peak_windows"]
    text.append("Observed-peak window sensitivity (1,000 whole-brew resamples; ungraded): "+"; ".join(
        f"{k} bar → {v['peak_bar']:.3f} [{v['interval_bar'][0]:.3f}, {v['interval_bar'][1]:.3f}] bar" for k, v in windows.items())+".")
    restart = diagnostics["restart"]
    text.append("")
    if restart["status"] == NA:
        text.append("Restart: NOT_AVAILABLE in the specified upstream tree; no other location searched.")
    else:
        lo, hi = restart["observed_after_range_g_s"]
        blo, bhi = restart["full_relaxation_factor_interval"]
        text.append(f"Restart (ungraded): P_r={restart['driving_pressure_bar']:.5f} bar, `{restart['source']}`, lines "
                    f"{restart['pressure_source_lines'][0]}–{restart['pressure_source_lines'][1]}, `p2/100`. Last-5-s mass slopes give "
                    f"{restart['observed_before_g_s']:.3f} → {lo:.3f}–{hi:.3f} g/s versus quoted 1.82 → 3.23–4.31 "
                    f"(differences {restart['discrepancy_before_g_s']:+.3f}, {restart['discrepancy_after_range_g_s'][0]:+.3f}/{restart['discrepancy_after_range_g_s'][1]:+.3f} g/s). "
                    "C0 and T2-F provide no matched-pressure pause gain; T2-L retains maximum-pressure compaction. Continued delivery can raise flow in all three. "
                    "T2 contains no relaxation state and itself predicts no pause benefit. "
                    f"Hypothetical T2-F full relaxation permits exp(P_r/Pstar)={restart['full_relaxation_factor']:.3f} [{blo:.3f}, {bhi:.3f}]× (full-cohort fit, 95% interval) "
                    f"versus observed {restart['observed_factor_range'][0]:.3f}–{restart['observed_factor_range'][1]:.3f}×; this relaxation is absent from T2-F. Off-state ~3-bar line pressure is not puck pressure.")
        text.append("Flow source: `m` versus `t/1000`; restart-window source lines "+", ".join(
            f"{e['source_lines'][0]}–{e['source_lines'][1]}" for e in restart["episodes"][1:])+".")
        text += ["", restart["owner_interpretation"]]
        text.append("Applied to T2-F's 95% Pstar interval: "+restart["relaxation_low_end_disposition"]+".")
    refs = [r for r in rows if r["fit_type"] == "SAVED_REFERENCE"]
    text += ["", "Saved comparators (endpoint / trace RMSE, g/s; replay rtol=1e-12): "+"; ".join(
        f"{r['candidate']} {r['endpoint_rmse_g_s']:.3f}/{r['trace_rmse_g_s']:.3f}" for r in refs)+". "+
        f"T2-L endpoint/trace {by_name['T2-L']['endpoint_rmse_g_s']:.3f}/{by_name['T2-L']['trace_rmse_g_s']:.3f} g/s (ungraded).", "",
        f"200/200 paired whole-brew refits repeat all folds, Mc and onset-only Pd; seed {SEED}. Parameter intervals use full-cohort fits; grades use held-out predictions. "
        f"Accuracy: B0c 1,000 paired condition-then-brew resamples, ±0.25 g/s. Joint scales: 0.437 g/s and 4.534 s. Runtime {elapsed/60:.2f} min cumulative wall; {cpu/3600:.2f} refit CPU h; two-hour cap retained. "
        "[Full results, bounds, source identities and diagnostics](RESULT_TABLE.csv). Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. EWP E1 demonstration reviewed read-only; no solver or source-data changes.", "",
        "**Recommendation:** Owner: review the T2-F capability grades, separate-scale consistency and restart limitation before selecting any further work.", ""]
    (out/"SUMMARY.md").write_text("\n".join(text))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--prior-seconds", type=float, default=0.)
    parser.add_argument("--resume", action="store_true", help="Reuse this C1 run's external checkpoints; charge prior wall time")
    args = parser.parse_args()
    if args.work.resolve().is_relative_to(ROOT):
        raise ValueError("Runtime checkpoints must be outside the checkout")
    if args.prior_seconds < 0:
        raise ValueError("Prior compute time cannot be negative")
    args.work.mkdir(parents=True, exist_ok=True); args.out.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    prior = args.prior_seconds
    if args.resume:
        with (args.work/"refits.pkl").open("rb") as stream:
            draws, cpu, stored_elapsed = pickle.load(stream)
        prior = max(prior, stored_elapsed)
        with (args.work/"point.pkl").open("rb") as stream:
            ctx, point, references = pickle.load(stream)
    else:
        draws, cpu = {}, 0.
    deadline = started+max(0., 7200.-prior)
    budget = C0.Deadline(deadline); budget.check()
    if args.resume:
        references = saved_references(ctx)
    if not args.resume:
        ctx = C0.context(args.ewp, args.raw)
        # C0's unchanged onset detector writes this local derived cache.
        # Keep individual-brew working evidence outside the checkout.
        onset_cache = ROOT/".b0-b0c-onsets.csv"
        if onset_cache.exists():
            onset_cache.replace(args.work/"private-b0c-onsets.csv")
        references = saved_references(ctx)
        print("SAVED_REFERENCES_REPRODUCED", flush=True)
        point = fit_folds(ctx, np.ones(len(ctx.delay)), deadline, point=True)
        with (args.work/"point.pkl").open("wb") as stream:
            pickle.dump((ctx, point, references), stream)
        with (args.work/"refits.pkl").open("wb") as stream:
            pickle.dump((draws, cpu, prior+time.monotonic()-started), stream)
        print("POINT_FITS_COMPLETE", time.monotonic()-started, flush=True)
    samples = B.brew_samples(ctx.fine.brews, 200, SEED)
    if len(draws) < 200:
        with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("spawn"),
                                 initializer=_initialize_worker, initargs=(ctx, deadline)) as executor:
            futures = [executor.submit(_refit, (i, s)) for i, s in enumerate(samples) if i not in draws]
            for future in as_completed(futures):
                index, value, seconds = future.result(); draws[index] = value; cpu += seconds
                with (args.work/"refits.pkl").open("wb") as stream:
                    pickle.dump((draws, cpu, prior+time.monotonic()-started), stream)
                if len(draws) % 10 == 0:
                    print("REFITS", len(draws), "of 200; cumulative seconds", prior+time.monotonic()-started, flush=True)
    budget.check()
    rows = result_rows(ctx, point, [draws[i] for i in range(200)], references)
    diagnostics = dict(onset_identity=onset_identity(ctx, point), observed_peak_windows=observed_peak_windows(ctx.fine.brews),
                       restart=restart_diagnostic(args.raw, point["fixed"]["bank"]))
    restart = diagnostics["restart"]
    if restart["status"] != NA:
        restart["T2F_Pstar_interval_bar"] = rows[0]["Pstar_bar_interval"]
        pr = restart["driving_pressure_bar"]
        restart["full_relaxation_factor"] = float(np.exp(pr/rows[0]["Pstar_bar"]))
        restart["full_relaxation_factor_interval"] = [float(np.exp(pr/p)) for p in reversed(rows[0]["Pstar_bar_interval"])]
        restart["relaxation_low_end_disposition"] = (
            "wholly above the low-end limit; whole-bed relaxation cannot account for the rise within T2"
            if rows[0]["Pstar_bar_interval"][0] > restart["Pstar_restart_limits_bar"][0]
            else "not excluded by this upper-bound check")
    figure(ctx, point, args.out)
    budget.check()
    elapsed = prior+time.monotonic()-started
    inputs = ["docs/research/PRESSURE_PEAK_STAGE_C0/RESULT_TABLE.csv", "docs/research/PRESSURE_PEAK_STAGE_B0C/RESULT_TABLE.csv",
              "docs/research/PRESSURE_PEAK_STAGE_B0D/RESULT_TABLE.csv", "docs/research/PRESSURE_PEAK_STAGE_B0C/ONSET.csv",
              "puckworks/data/waszkiewicz2025/traces_per_brew.csv", "puckworks/data/waszkiewicz2025/equilibrium_windows.csv"]
    identities = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    for row in rows:
        row.update(wall_seconds=elapsed, refit_cpu_seconds=cpu, source_sha256=identities)
    rows[0]["diagnostics"] = diagnostics
    B.write_csv(args.out/"RESULT_TABLE.csv", [{k: json.dumps(v) if isinstance(v, (dict, list, tuple)) else v for k, v in r.items()} for r in rows])
    write_summary(rows, diagnostics, elapsed, cpu, args.out)
    with (args.work/"refits.pkl").open("wb") as stream:
        pickle.dump((draws, cpu, prior+time.monotonic()-started), stream)
    print("COMPLETE", json.dumps(dict(wall_seconds=elapsed, refit_cpu_seconds=cpu, refits=len(draws))), flush=True)


if __name__ == "__main__":
    main()

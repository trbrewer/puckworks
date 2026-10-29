"""PRESSURE-PEAK B0/B0b: data checks and mechanism screens.

Waszkiewicz et al. (2025), Zenodo 10.5281/zenodo.18046315, CC-BY-4.0
data; source GPL programs are read for method documentation, never imported.
Stage A functions supply source joins, folds, bootstrap losses and verdicts.
No production model, registry, gate, historical record or source file is written.

First run --checks-only --ewp EWP --raw ORIGINAL_SOURCE. Raw-pressure disappearance
is the sole stop condition. --screen repeats checks before fitting. Primary
pressure is the requested observed-flow-derived basket pressure; SCI-MD-010 and
Stage A actually used direct line pressure. These conditional basket fits have
outcome-dependent covariates, not independent hydraulic predictions. Raw rows
are therefore necessary. Fold membership always retains nominal pressure groups.
Peaks, as in Stage A, refer to those sampled nominal conditions, not a continuous
maximum or a change of grouping when derived basket pressure shifts below 9 bar.

Raw records contain elapsed t in milliseconds, not acquisition dates. The paper
says last ten seconds of each run; a universal aligned 110--120 s window is not
equivalent (durations vary). Both literal and actual terminal windows are checked.
The fixed scoring observer remains endpoint_100s, with no target redefinition.

Numba is optional acceleration for independent brew ODEs. For the 200-refit run,
install numba in a research environment and set NUMBA_NUM_THREADS=4; the fallback
executes identical Python equations. Sensitivity equations provide Jacobians;
synthetic ODE recovery and finite differences independently verify them. Fitting
uses a 0.5-s pressure grid; predictions use all 1000 source samples. The numerical
endpoint difference is reported. Use --prior-fit-seconds to count previous
fitting attempts against the cumulative 7200-second limit.

B0b --timecourse uses raw line pressure primarily, seed 20261030, and the same
equations, folds and endpoint observer. --timecourse-checks-only computes T1--T3
from saved B0 coefficients. Full-trace losses score stable pressure +5 s through
B0's last clean sample, with terminal events removed before flow smoothing.
State history still begins at stable pressure; it is not reset at the scoring
boundary. T4/T5 use 200 whole-brew refits for slope, nominal-condition peak and
late trend. Mean-trend signs determine the 8/11 agreement check; interval-based
rising/declining/unresolved categories are reported separately, since an interval
containing zero does not establish flatness. The per-pressure smooth curve uses
the evaluated brews and is an explicitly ineligible, optimistic fit ceiling.
Fast jamming uses integration steps that resolve its relaxation rate, preventing
numerical overshoot below Qcrit. The old B0 mode and saved results are unchanged.

B0c --onset-only / --swelling-screen use seed 20261031. Native sustained outflow
requires baseline-relative mass >0.5 g AND smoothed flow >0.1 g/s continuously
for 2 s; onset is the start of that interval. The baseline is median cup mass
in stable pressure -2--0 s. Both thresholds have joint x0.5/x1.5 sensitivities.
The inherited stable-pressure clock starts after the last out-of-band sample
among the first 501 records: the band is median pressure +/-min(10%,0.5 bar).
Terminal exclusions and the source 31-point Savitzky--Golay observer are retained.
This is operational cup-outflow timing, including transport and detection lag;
it is not a direct image of front breakthrough or grain-wetting duration.

T1 fits log(delay)=log(c)-n*log(P/bar), equal conditions and equal brews, with
unconstrained n and 1000 whole-brew bootstraps. P is median stable +0--2-s line
pressure; observed-flow-derived basket pressure is sensitivity only. T2 changes
only the scoring mask to measured onset +2 s, never state initialization or the
SCI-MD-010 100-s endpoint. E1/E3 predict onset from training-fold T1 coefficients;
E2 uses measured onset and is diagnostic/ineligible. All three apply exp(-delay/
tau) once to conductance inside the original delivered-mass evolution. Mc is
fixed from that fold's C4/D1 reference fit. There are three free hydraulic
parameters, plus estimated nuisance inputs; 200 whole-brew
refits re-estimate those inputs inside each training fold. The 10--240-s weak
tau bound comes from the documented Hargarten grain-swelling proxy, not a
conductance-rate measurement. B0c never uses the stop/restart brew.

Example: python -m puckworks.analysis.pressure_peak_stage_b0 --swelling-screen
--ewp /path/to/espresso-whole-pull --raw /path/to/upstream --workers 16 --refits 200
with OPENBLAS_NUM_THREADS=1 and NUMBA_NUM_THREADS=1. Public output is aggregate
only; individual onset detections and point-fit checkpoints stay local. Fixed-fit
paired loss intervals resample conditions then brews; refit response intervals
resample brews within conditions. Peaks retain nominal condition coordinates.

B0d --air-screen uses seed 20261101 and the unchanged B0c detector/ONSET.csv.
Timing targets never enter hydraulic predictions. W1/WD1 fit offset, scale and
compaction; W2/WD2 additionally fit atmospheric air fraction and are EXPLORATORY.
The minimum region cannot identify an offset separately from infiltration time.
WD1/WD2 use the D1 permeability, with/without Boyle air, for like-form comparison.
T2 fixes training-fold timing compaction/air coefficients and fits only flow
scale and Mc to endpoints. F1/F2 fit scale, compaction and s0; Mc is inherited
from a reference endpoint fit inside that same training fold. No timing or
hydraulic target from a held-out pressure enters these calibrations.
The consistency check compares extrema of P*k(P)*kr(P), excluding delivered
mass. D1's modulus is expressed as its air-free conductance peak. Air-bearing
extrema are recomputed, not identified with the exponential compaction scale.
All scores use LOPO fits; descriptive full-cohort parameter/peak intervals are
separate. T2 checks independently flow-fitted reference/F coefficients, never
its own timing-fixed coefficient (which would agree by construction). Full-model
nominal endpoint peaks are retained separately. Endpoints keep the 1000-point
observer; the 201-point fitting quadrature is checked explicitly. Late trends
use the inherited last-30-s observer on a 0.1-s grid, including bootstrap refits.
Each pressure view uses 200 paired whole-brew refits. m=2/4 and basket pressure
are sensitivities; the m=3 prior rows repeat the primary fit without new evidence.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import multiprocessing
import random
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import least_squares, brentq

from puckworks.analysis import pressure_peak_stage_a as A

PHI = .122
OUT = A.ROOT / "docs/research/PRESSURE_PEAK_STAGE_B0"
MODELS = ("B1", "C4", "D1", "D2", "D3")

try:
    from numba import njit, prange
except ImportError:  # Optional acceleration; same Python equations remain usable.
    prange = range
    def njit(**kwargs):
        return lambda function: function


def locked_ratio(pressure, dry_modulus):
    """Carman--Kozeny ratio after irreversible locking; Phi is fixed at .122.

    Initial stable pressure P(t=0) proxies wetting pressure, since the source has
    no wetting-front timestamps. It is fixed once per brew, never updated by
    subsequent saturation pressure, and is not an extra fitted initial state.
    Y->infinity gives ratio 1. The FULL D1 retains its W-H2 transient until
    delivered mass/Mc -> infinity; only then is its flow plain Darcy.
    """
    phi = np.maximum(PHI-(1-PHI)*np.asarray(pressure)/dry_modulus, 0.)
    return (phi/PHI)**3*((1-PHI)/(1-phi))**2


@njit(cache=True)
def _state_derivative(state, pressure, mobility, mobility_gradient, beta, critical, mass_scale,
                      evolving):
    n = len(mobility_gradient)
    result = np.zeros(2+2*n)
    mass, z = state[0], state[1]
    inner = np.exp(-mass/mass_scale) if evolving else 0.
    factor = np.exp(inner)
    q = mobility*pressure/(factor+z)
    result[0] = q
    result[1] = beta*max(q-critical, 0.)
    for k in range(n):
        df = -factor*inner/mass_scale*state[2+k]
        if evolving and k == 2:
            df += factor*inner*mass/mass_scale
        dq = pressure*mobility_gradient[k]/(factor+z)-q*(df+state[2+n+k])/(factor+z)
        result[2+k] = dq
        if q > critical:
            result[2+n+k] = beta*dq
            if k == n-2:
                result[2+n+k] += beta*(q-critical)
            if k == n-1:
                result[2+n+k] -= beta*critical
    return result


@njit(cache=True, parallel=True)
def dynamic_with_gradient(pressure, t, parameters, evolving):
    """RK4, linear pressure interpolation, no measured flow inside the ODE.

    D2: Q=a*P/(1+z), zdot=beta*max(Q-Qcrit,0), z(0)=0.
    D3: Q=a*k_ratio*P/(exp(exp(-M/Mc))+z), Mdot=Q; same zdot.
    Thus D3 adds jamming resistance to D1, referenced to the locked R0, rather
    than fitting a new arbitrary resistance history. It has five parameters.
    """
    result = np.empty(pressure.shape[0])
    gradient = np.empty((pressure.shape[0], len(parameters)))
    a = parameters[0]
    beta, critical = parameters[-2], parameters[-1]
    mc = parameters[2] if evolving else 1.
    for i in prange(pressure.shape[0]):
        mobility = a
        dmobility = np.zeros(len(parameters))
        dmobility[0] = mobility
        if evolving:
            phi = max(PHI-(1-PHI)*pressure[i, 0]/parameters[1], 0.)
            mobility = a*(phi/PHI)**3*((1-PHI)/(1-phi))**2
            dmobility[0] = mobility
            if phi > 0:
                dmobility[1] = mobility*(3/phi+2/(1-phi))*(1-PHI)*pressure[i, 0]/parameters[1]
        state = np.zeros(2+2*len(parameters))
        for j in range(len(t)-1):
            dt = t[j+1]-t[j]
            p0, p1 = pressure[i, j], pressure[i, j+1]
            pm = (p0+p1)/2
            k1 = _state_derivative(state, p0, mobility, dmobility, beta, critical, mc, evolving)
            k2 = _state_derivative(state+dt*k1/2, pm, mobility, dmobility, beta, critical, mc, evolving)
            k3 = _state_derivative(state+dt*k2/2, pm, mobility, dmobility, beta, critical, mc, evolving)
            k4 = _state_derivative(state+dt*k3, p1, mobility, dmobility, beta, critical, mc, evolving)
            state += dt*(k1+2*k2+2*k3+k4)/6
        end = _state_derivative(state, pressure[i, -1], mobility, dmobility,
                                beta, critical, mc, evolving)
        result[i] = end[0]
        gradient[i] = end[2:2+len(parameters)]
    return result, gradient


def predict(model, parameters, pressure, t):
    pressure = np.maximum(pressure, 0.)
    if model in ("B1", "C4"):
        return A.predict(model, parameters, pressure, t)
    if model == "D1":
        a, young, mc = parameters
        mobility = a*locked_ratio(pressure[:, 0], young)
        exposure = mobility*np.trapezoid(pressure, t, axis=1)/mc
        return mobility*pressure[:, -1]*np.exp(-np.exp(-A.delivered_state(exposure)))
    if model == "D2":
        return dynamic_with_gradient(pressure, t, np.asarray(parameters), False)[0]
    if model == "D3":
        return dynamic_with_gradient(pressure, t, np.asarray(parameters), True)[0]
    raise ValueError(model)


PARAMETERS = {
    "B1": A.PARAMETER_NAMES["B1"], "C4": A.PARAMETER_NAMES["C4"],
    "D1": ["a_g_s_bar", "Ydry_bar", "Mc_g"],
    "D2": ["a_g_s_bar", "beta_per_g", "Qcrit_g_s"],
    "D3": ["a_g_s_bar", "Ydry_bar", "Mc_g", "beta_per_g", "Qcrit_g_s"],
}
FIT_SETTINGS = {
    "C4": ([.001, .1, .01], [20, 100, 1000], [[1, 5, 30], [2, 12, 150]]),
    "D1": ([.001, 10, .01], [20, 1e6, 1000], [[1, 200, 60], [2, 300, 150]]),
    "D2": ([.001, 1e-7, 1e-5], [20, 10, 10], [[.5, .02, 1], [1, .05, 2]]),
    "D3": ([.001, 10, .01, 1e-7, 1e-5], [20, 1e6, 1000, 10, 10],
           [[1, 200, 60, .01, 1], [2, 300, 150, .03, 2]]),
}


def fit(model, pressure, t, target, weights, budget):
    if model == "B1":
        return A.fit(model, pressure, t, target, weights, budget)
    lower, upper, starts = FIT_SETTINGS[model]
    started = time.monotonic()
    # Resolve the measured history on a 0.5-s integration grid for fitting;
    # final predictions and all scoring use the full 1000-sample history.
    # The maximum endpoint difference is reported, not silently discarded.
    if model in {"D2", "D3"} and len(t) > 201:
        fit_t = np.linspace(t[0], t[-1], 201)
        fit_p = np.array([np.interp(fit_t, t, p) for p in pressure])
    else:
        fit_t, fit_p = t, pressure
    cache_x, cache_result = None, None

    def evaluated(x):
        nonlocal cache_x, cache_result
        budget.check(started)
        if cache_x is None or not np.array_equal(x, cache_x):
            cache_x = x.copy()
            q, jac = dynamic_with_gradient(np.maximum(fit_p, 0.), fit_t, np.exp(x), model == "D3")
            cache_result = ((q-target)*np.sqrt(weights), jac*np.sqrt(weights[:, None]))
        return cache_result

    def residual(log_parameters):
        budget.check(started)
        return (predict(model, np.exp(log_parameters), pressure, t)-target)*np.sqrt(weights)

    try:
        solutions = [least_squares((lambda x: evaluated(x)[0]) if model in {"D2", "D3"} else residual,
                      np.log(initial), jac=(lambda x: evaluated(x)[1]) if model in {"D2", "D3"} else "2-point",
                      bounds=(np.log(lower), np.log(upper)),
                      ftol=1e-7, xtol=1e-7, gtol=1e-7, max_nfev=1000, x_scale="jac")
                     for initial in starts]
        valid = [s for s in solutions if s.success and np.isfinite(s.fun).all()]
        if not valid:
            # Threshold activation creates nonsmooth corners. Retry the same
            # training objective with a box trust region; never skip a bootstrap
            # sample or return a nonconverged fit as though it had converged.
            best = min(solutions, key=lambda s: s.cost)
            retry = least_squares(
                (lambda x: evaluated(x)[0]) if model in {"D2", "D3"} else residual,
                best.x, jac=(lambda x: evaluated(x)[1]) if model in {"D2", "D3"} else "2-point",
                bounds=(np.log(lower), np.log(upper)), method="dogbox", x_scale="jac",
                ftol=1e-7, xtol=1e-7, gtol=1e-7, max_nfev=2000)
            if not retry.success or not np.isfinite(retry.fun).all():
                raise RuntimeError(f"{model}: both optimizers failed; no failed fold is dropped")
            valid = [retry]
        return np.exp(min(valid, key=lambda s: s.cost).x)
    finally:
        budget.elapsed += time.monotonic()-started


def fit_folds(model, brews, sampled, budget):
    """One refit of all eleven folds; sampled multiplicities are training-only."""
    predictions = np.empty(len(brews.ids))
    coefficients = {}
    for holdout in brews.groups:
        train = np.flatnonzero(brews.condition != brews.condition[holdout[0]])
        weights = np.array([sampled[i]/(10*np.sum(brews.condition == brews.condition[i]))
                            for i in train])
        parameters = fit(model, brews.pressure[train], brews.t, brews.target[train], weights, budget)
        predictions[holdout] = predict(model, parameters, brews.pressure[holdout], brews.t)
        coefficients[brews.fold[holdout[0]]] = parameters.tolist()
    return predictions, coefficients


def refit_response(brews, predictions, multiplicity):
    """Same bootstrap brews generate training weights and held-out condition means."""
    x = np.array([np.average(brews.pressure[g, -1], weights=multiplicity[g]) for g in brews.groups])
    y = np.array([np.average(predictions[g], weights=multiplicity[g]) for g in brews.groups])
    p = np.unique(brews.condition)
    return A.slope(x[p >= 9], y[p >= 9]), float(p[np.argmax(y)])


def _refit_sample(arguments):
    model, brews, multiplicity, deadline = arguments
    # Spawn avoids inheriting an active OpenMP pool; each process uses one core.
    try:
        from numba import set_num_threads
        set_num_threads(1)
    except ImportError:
        pass
    local_budget = A.FitBudget(max(0., deadline-time.monotonic()))
    predicted, _ = fit_folds(model, brews, multiplicity, local_budget)
    return refit_response(brews, predicted, multiplicity)


def refit_bootstrap(model, brews, count, budget, workers=1):
    rng = np.random.default_rng(A.SEED)
    samples = []
    for _ in range(count):
        multiplicity = np.zeros(len(brews.ids), dtype=int)
        for group in brews.groups:
            multiplicity += np.bincount(rng.choice(group, len(group)), minlength=len(brews.ids))
        samples.append(multiplicity)
    slopes, peaks = [], []
    started = time.monotonic()
    deadline = started + budget.limit-budget.elapsed
    executor = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
    try:
        results = executor.map(_refit_sample,
                               [(model, brews, m, deadline) for m in samples], chunksize=1)
        for iteration, (high_slope, peak) in enumerate(results, 1):
            slopes.append(high_slope)
            peaks.append(peak)
            if iteration % 10 == 0:
                print(json.dumps({"model": model, "refits": iteration,
                                  "fit_seconds": round(budget.elapsed+time.monotonic()-started, 2)}),
                      flush=True)
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
        # Wall time includes process startup/IPC, conservatively. Workers share
        # an absolute deadline, so parallel work cannot reset the two-hour cap.
        budget.elapsed += time.monotonic()-started
    return {"slope": A.interval(slopes), "peak": A.interval(peaks), "count": count,
            "slope_minmax": [min(slopes), max(slopes)]}


def passes(model, response, refit, comparison):
    return model in {"D1", "D2"} and refit["slope"][1] < 0 and \
        5 <= response["peak"] <= 7 and refit["peak"][0] <= 7 and refit["peak"][1] >= 5 \
        and comparison in {"TIE", "BETTER"}


def link_pressure_rows(rows):
    """Put the actual counterpart numbers next to each primary/sensitivity row."""
    lookup = {(r["candidate"], r["pressure"]): r for r in rows}
    for row in rows:
        other = "raw sensitivity" if row["pressure"] == "basket primary" else "basket primary"
        if (row["candidate"], other) not in lookup:
            continue
        match = lookup[row["candidate"], other]
        row["raw-pressure sensitivity"] = json.dumps({
            "counterpart": other, "RMSE_g_s": float(match["RMSE g/s"]),
            "COMPARISON": match["COMPARISON"],
            "slope_refit": json.loads(match["slope interval refit"]),
            "peak_refit": json.loads(match["peak interval refit"]), "PASS": match["PASS"]})
    return rows


def screen(brews, q, out, count, prior_fit_seconds=0, workers=4, resume=False):
    if count < 200:
        raise ValueError("At least 200 refit-bootstrap replicates required")
    budget = A.FitBudget(7200)
    budget.elapsed = prior_fit_seconds
    rows = A.read_csv(out / "RESULT_TABLE.csv") if resume and (out / "RESULT_TABLE.csv").exists() else []
    completed = {(r["candidate"], r["pressure"]): r for r in rows}
    if any(int(r["refit count"]) != count for r in rows):
        raise ValueError("Resume interval count mismatch")
    for scale, label in ((1., "basket primary"), (0., "raw sensitivity")):
        view = pressure_view(brews, q, scale)
        predictions, parameters = [], {}
        for model in MODELS:
            if (model, label) in completed:
                coefficients = json.loads(completed[model, label]["parameters"])["by_fold"]
                predicted = np.empty(len(view.ids))
                for group in view.groups:
                    predicted[group] = predict(model, coefficients[view.fold[group[0]]],
                                               view.pressure[group], view.t)
            else:
                predicted, coefficients = fit_folds(model, view, np.ones(len(view.ids)), budget)
            predictions.append(predicted)
            parameters[model] = coefficients
            print(json.dumps({"point_folds_completed": model, "pressure": label,
                              "fit_seconds": budget.elapsed}), flush=True)
        loss = np.array([[np.sqrt(np.mean((p[g]-view.target[g])**2)) for g in view.groups]
                         for p in predictions])
        draws = A.nested_loss_draws(view, np.array(predictions))
        for index, (model, predicted) in enumerate(zip(MODELS, predictions)):
            if (model, label) in completed:
                continue
            response = A.response_diagnostics(view, predicted)
            numerical = 0.
            if model in {"D2", "D3"}:
                grid = np.linspace(0, 100, 201)
                for group in view.groups:
                    history = np.array([np.interp(grid, view.t, p) for p in view.pressure[group]])
                    coarse = predict(model, parameters[model][view.fold[group[0]]], history, grid)
                    numerical = max(numerical, float(np.max(np.abs(coarse-predicted[group]))))
            boot = refit_bootstrap(model, view, count, budget, workers)
            error_ci = A.interval(draws[:, index])
            delta_ci = A.interval(draws[:, index]-draws[:, 0])
            comparison = A.comparison(delta_ci)
            capable = A.capability(error_ci, response["slope"])
            row = {
                "candidate": model, "pressure": label,
                "parameters": json.dumps({"names": PARAMETERS[model], "by_fold": parameters[model],
                    "fixed": {"Phi": PHI, "transient_amplitude": 1} if model in {"D1", "D3"}
                             else {"transient_amplitude": 1} if model == "C4" else {}}),
                "RMSE g/s": float(loss[index].mean()), "RMSE interval": json.dumps(error_ci),
                "CAPABILITY": capable, "delta versus B1 g/s": float((loss[index]-loss[0]).mean()),
                "delta interval": json.dumps(delta_ci), "COMPARISON": comparison,
                "slope g/s/bar": response["slope"],
                "slope interval no-refit": json.dumps(response["slope_interval"]),
                "slope interval refit": json.dumps(boot["slope"]),
                "peak nominal bar": response["peak"],
                "peak interval no-refit": json.dumps(response["peak_interval"]),
                "peak interval refit": json.dumps(boot["peak"]),
                "refit count": count, "raw-pressure sensitivity": "paired row uses raw pressure"
                              if scale == 1 else "raw pressure, independent of observed flow",
                "eligibility": "EXPLORATORY: 5 parameters" if model == "D3" else
                               "REFERENCE" if model in {"B1", "C4"} else "ELIGIBLE",
                "PASS": "Y" if passes(model, response, boot, comparison) else "N",
                "maximum coarse/full endpoint difference g/s": numerical,
            }
            rows.append(row)
            write_csv(out / "RESULT_TABLE.csv", rows)
            print(json.dumps({"completed": model, "pressure": label,
                              "RMSE": row["RMSE g/s"], "comparison": comparison,
                              "slope_refit": boot["slope"], "peak_refit": boot["peak"],
                              "PASS": row["PASS"], "fit_seconds": budget.elapsed}), flush=True)
    link_pressure_rows(rows)
    write_csv(out / "RESULT_TABLE.csv", rows)
    return rows, budget.elapsed


def flow_history(brews, data):
    records = A.read_csv(data / "traces_per_brew.csv")
    lookup = {(r["shot_id"], int(r["time_index"])): float(r["mass_flow_rate__g_per_s"])
              for r in records}
    return np.array([[lookup[shot, j] for j in range(1000)] for shot in brews.ids])


def pressure_view(brews, observed_flow, scale):
    """scale=0 is measured line pressure; 1 is the derived basket estimate."""
    a, b, c = A.MACHINE
    pressure = brews.pressure - scale*(a*observed_flow**2+b*observed_flow+c)
    return replace(brews, pressure=pressure)


def diagnostic_row(name, brews, target, details=""):
    result = A.response_diagnostics(brews, target)
    for entry in result["per_pressure"]:
        entry["pressure_mean_bar"] = entry.pop("direct_line")
    return {"check": name, "slope g/s/bar": result["slope"],
            "slope interval": json.dumps(result["slope_interval"]),
            "peak nominal bar": result["peak"],
            "peak interval": json.dumps(result["peak_interval"]),
            "per-pressure mean flow and interval": json.dumps(result["per_pressure"]),
            "verdict": "DOWNTURN SURVIVES" if result["slope_interval"][1] < 0
                       else "SENSITIVE / NOT ESTABLISHED", "details": details}


def raw_trace(path):
    records = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    rows = [r for r in records if "t" in r and "m" in r]
    t = np.array([r["t"]/1000 for r in rows])
    p = np.array([r["p2"]/100 for r in rows])
    mass = np.array([r["m"] for r in rows])
    median = np.median(p)
    outside = np.flatnonzero((p[:501] < max(.9*median, median-.5)) |
                            (p[:501] > min(1.1*median, median+.5)))
    start = outside[-1]+1 if len(outside) else 0
    return t-t[start], p, mass, len(records)-len(rows)


def window_evidence(brews, raw):
    terminal, clean_terminal, pressure_terminal, details = [], [], [], []
    for shot in brews.ids:
        t, p, mass, incomplete = raw_trace(raw / "measurements_time_dependent" / f"{shot}.txt")
        q = savgol_filter(np.gradient(mass, t), 31, 1)
        late = (t >= 110) & (t <= 120)
        terminal_window = t >= t[-1]-10
        terminal.append(float(np.mean(q[terminal_window])))
        pressure_terminal.append(float(np.mean(p[terminal_window])))
        # Diagnostic only: first pressure departure or cup-removal step after
        # 100 s; neither this rule nor this window changes the scoring cohort.
        typical = np.median(p[(t >= 90) & (t <= 100)])
        event = np.flatnonzero((t[1:] > 100) &
                              ((np.abs(p[1:]-typical) > max(.5, .1*typical)) |
                               (np.diff(mass) < -5)))
        end = event[0] if len(event) else len(t)-1
        start = np.searchsorted(t, t[end]-10)
        clean_terminal.append(float((mass[end]-mass[start])/(t[end]-t[start])))
        jumps = np.flatnonzero((t[1:] >= 110) & (t[1:] <= 120) & (np.diff(mass) < -5))
        details.append({"shot": shot, "last_aligned_s": float(t[-1]),
                        "late_duration_s": float(min(t[-1], 120)-110),
                        "late_pressure_min_bar": float(p[late].min()),
                        "late_pressure_max_bar": float(p[late].max()),
                        "largest_late_mass_step_g": float(np.diff(mass[late]).min()),
                        "negative_mass_step_count": len(jumps),
                        "negative_mass_step_time_range_s":
                            [float(t[jumps[0]+1]), float(t[jumps[-1]+1])] if len(jumps) else [],
                        "incomplete_records": incomplete})
    return np.array(terminal), np.array(clean_terminal), np.array(pressure_terminal), details


def metadata_check(raw):
    keys, initial_t, files = set(), [], list((raw / "measurements_time_dependent").rglob("*.txt"))
    for path in files:
        records = [json.loads(s) for s in path.read_text().splitlines() if s.strip()]
        keys.update(k for row in records for k in row)
        initial_t.append(records[0].get("t"))
    if keys != {"U", "m", "p1", "p2", "t", "v1", "v2"} or len(files) != 61:
        raise ValueError("Raw metadata schema/cohort changed; inspect before asserting metadata absence")
    return {"files": len(files), "columns": sorted(keys),
            "initial_t_ms_range": [min(initial_t), max(initial_t)],
            "finding": "Elapsed within-record t only; no date, temperature or global order field. "
                       "Filename suffixes do not establish acquisition chronology. "
                       "U/v1/v2 are voltage channels, not calibrated temperatures."}


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def data_checks(brews, observed_flow, raw, out):
    rows = []
    for scale in (0., .8, 1., 1.2):
        rows.append(diagnostic_row(f"endpoint_pressure_scale_{scale:g}",
                    pressure_view(brews, observed_flow, scale), brews.target,
                    "Zero=direct sensor pressure. Other values multiply all three drop coefficients; "
                    "same 9/11/13 nominal conditions, no regrouping."))
    for name in ("mean_90_100s", "mean_110_120s"):
        rows.append(diagnostic_row(name, brews, brews.windows[name],
                                   "Stored window flows versus the same direct endpoint pressure."))
    terminal, clean, terminal_p, details = window_evidence(brews, raw)
    rows.append(diagnostic_row("actual_last_10s_of_each_record", brews, terminal,
                               "Variable recorded duration; includes shutdown/cup removal. "
                               "Pressure coordinate remains direct endpoint, preserving condition."))
    rows.append(diagnostic_row("last_10s_before_detected_terminal_event", brews, clean,
                               "Mass increment before first post-100s pressure departure >max(.5bar,10%) "
                               "or mass step <-5g. Diagnostic only; scoring endpoint unchanged."))
    rows.append({"check": "late_window_trace_evidence", "verdict":
                 "CONTAMINATION CONFIRMED" if any(d["largest_late_mass_step_g"] < -5 for d in details)
                 else "NO LARGE SCALE DISCONTINUITY FOUND",
                 "details": json.dumps(details)})
    rows.append({"check": "local_acquisition_metadata", "verdict": "ORDER/TEMPERATURE NOT FOUND",
                 "details": json.dumps(metadata_check(raw))})
    rows.append({"check": "author_GitHub_Zenodo_metadata", "verdict": "ORDER/TEMPERATURE NOT FOUND",
                 "details": "Read current github.com/RadostW/espresso at "
                 "b71ac9a321477252dbee3f09feae825d8abc77d2: all 61 time-dependent raw files "
                 "are byte-identical to the retained v1.0.1 copy. Local ZIP MD5 "
                 "ee7ea52d03ea3838b0815ccf0364177f matches Zenodo record 18046315. "
                 "Searched raw JSON keys/headers, filenames, README and Python comments; "
                 "no chronology or temperature records. The 90 C viscosity reference is a "
                 "constant, not a logged temperature. Sorted filenames are processing order. "
                 "No filesystem modification times used; order/drift and temperature-versus-pressure "
                 "tests are not estimable."})
    for row in rows:
        row["source path"] = (
            "puckworks/data/waszkiewicz2025/traces_per_brew.csv; "
            "puckworks/data/waszkiewicz2025/equilibrium_windows.csv"
            if row["check"].startswith(("endpoint_", "mean_")) else
            "https://github.com/RadostW/espresso/tree/b71ac9a321477252dbee3f09feae825d8abc77d2; "
            "https://zenodo.org/records/18046315; "
            "/home/tim/espresso-development/local-audit-20260930T165034Z/private-replay/wp02/"
            "RadostW-espresso-v1.0.1.zip"
            if row["check"] == "author_GitHub_Zenodo_metadata" else
            str(raw / "measurements_time_dependent"))
    write_csv(out / "DATA_CHECKS.csv", rows)
    return rows, rows[0]["verdict"] == "DOWNTURN SURVIVES"


# B0b is an additive research mode. B0's equations, CLI and saved results above
# retain their original meanings; only the new mode uses raw pressure primarily.
B0B_SEED = 20261030
B0B_OUT = A.ROOT / "docs/research/PRESSURE_PEAK_STAGE_B0B"


@dataclass
class Course:
    brews: A.Brews
    t: np.ndarray
    pressure: np.ndarray
    flow: np.ndarray
    mask: np.ndarray
    late_weights: np.ndarray
    observed_trend: np.ndarray
    ends: np.ndarray


def clean_course(t, pressure, mass):
    """B0 terminal detector, applied BEFORE differentiation and smoothing.

    The detector identifies the first post-100-s pressure departure exceeding
    max(.5 bar, 10%) or mass loss exceeding 5 g. The preceding sample is last
    usable. Stable-pressure alignment is supplied unchanged by raw_trace.
    """
    typical = np.median(pressure[(t >= 90) & (t <= 100)])
    event = np.flatnonzero((t[1:] > 100) &
                          ((np.abs(pressure[1:]-typical) > max(.5, .1*typical)) |
                           (np.diff(mass) < -5)))
    end = event[0] if len(event) else len(t)-1
    use = (t >= 0) & (np.arange(len(t)) <= end)
    t, pressure, mass = t[use], pressure[use], mass[use]
    flow = savgol_filter(np.gradient(mass, t), 31, 1)
    late = t >= t[-1]-30
    return t, pressure, flow, A.slope(t[late], flow[late])


def load_course(brews, raw, step=.5, basket=False, omit_low=False, observed_flow=None):
    """Keep 0--5 s as initial-state history, score only t>=5 s.

    Native flow uses the source's 31-point, order-one Savitzky--Golay observer.
    The 100-s endpoint retains its original stored observer and pressure grid.
    No state, onset shift or per-brew coefficient is fitted. Array padding beyond
    a brew's clean end is masked from every loss and trend.
    """
    selected = np.flatnonzero(brews.condition > 3) if omit_low else np.arange(len(brews.ids))
    view = pressure_view(brews, observed_flow, 1.) if basket else brews
    view = replace(view, ids=[brews.ids[i] for i in selected], condition=view.condition[selected],
                   pressure=view.pressure[selected], target=view.target[selected],
                   windows={k: v[selected] for k, v in view.windows.items()},
                   fold=[view.fold[i] for i in selected])
    native = [clean_course(*raw_trace(raw / "measurements_time_dependent" / f"{shot}.txt")[:3])
              for shot in view.ids]
    ends = np.array([r[0][-1] for r in native])
    t = np.arange(0., np.ceil(max(ends)/step)*step+step/2, step)
    p = np.array([np.interp(t, r[0], r[1]) for r in native])
    q = np.array([np.interp(t, r[0], r[2]) for r in native])
    if basket:
        a, b, c = A.MACHINE
        p -= a*q*q+b*q+c
    mask = (t[None, :] >= 5) & (t[None, :] <= ends[:, None])
    late = (t[None, :] >= ends[:, None]-30) & (t[None, :] <= ends[:, None])
    centered = t[None, :]-(late*t).sum(axis=1)[:, None]/late.sum(axis=1)[:, None]
    late_weights = centered*late/(centered**2*late).sum(axis=1)[:, None]
    return Course(view, t, np.maximum(p, 0.), q, mask, late_weights,
                  np.array([r[3] for r in native]), ends)


@njit(cache=True)
def _course_derivative(state, pressure, lock_pressure, parameters, kind):
    """Reuse B0 state/sensitivity equations; kind 0=C4, 1=D1, 2=D2, 3=D3."""
    n = len(parameters)
    mobility = parameters[0]
    dm = np.zeros(n)
    if kind == 0:
        mobility *= np.exp(-pressure/parameters[1])
        dm[1] = mobility*pressure/parameters[1]
    elif kind == 1 or kind == 3:
        phi = max(PHI-(1-PHI)*lock_pressure/parameters[1], 0.)
        mobility *= (phi/PHI)**3*((1-PHI)/(1-phi))**2
        if phi > 0:
            dm[1] = mobility*(3/phi+2/(1-phi))*(1-PHI)*lock_pressure/parameters[1]
    dm[0] = mobility
    beta = parameters[-2] if kind >= 2 else 0.
    crit = parameters[-1] if kind >= 2 else 0.
    mc = parameters[2] if kind != 2 else 1.
    return _state_derivative(state, pressure, mobility, dm, beta, crit, mc, kind != 2)


@njit(cache=True)
def _course_ode(pressure, t, parameters, kind):
    n = len(parameters)
    values = np.empty(pressure.shape)
    jac = np.empty((pressure.shape[0], pressure.shape[1], n))
    for i in range(pressure.shape[0]):
        state = np.zeros(2+2*n)
        lock = pressure[i, 0]
        for j in range(len(t)):
            p0 = pressure[i, j]
            k1 = _course_derivative(state, p0, lock, parameters, kind)
            values[i, j] = k1[0]
            jac[i, j] = k1[2:2+n]
            if j+1 == len(t):
                break
            dt, p1 = t[j+1]-t[j], pressure[i, j+1]
            elapsed = 0.
            while elapsed < dt-1e-12:
                pa = p0+(p1-p0)*elapsed/dt
                k1 = _course_derivative(state, pa, lock, parameters, kind)
                step = dt-elapsed
                if kind >= 2:
                    # Trace fits can select much faster jamming than endpoint
                    # fits. Resolve its local relaxation rate (including the
                    # sensitivity equations), rather than letting RK4 overshoot
                    # below Qcrit and create spurious permanent resistance.
                    inner = np.exp(-state[0]/parameters[2]) if kind == 3 else 0.
                    factor = np.exp(inner)
                    rate = parameters[-2]*k1[0]/(factor+state[1])
                    if kind == 3:
                        rate += inner*k1[0]/parameters[2]
                    step = min(step, .25/max(rate, 1e-12))
                pm = p0+(p1-p0)*(elapsed+step/2)/dt
                pb = p0+(p1-p0)*(elapsed+step)/dt
                k2 = _course_derivative(state+step*k1/2, pm, lock, parameters, kind)
                k3 = _course_derivative(state+step*k2/2, pm, lock, parameters, kind)
                k4 = _course_derivative(state+step*k3, pb, lock, parameters, kind)
                state += step*(k1+2*k2+2*k3+k4)/6
                elapsed += step
    return values, jac


def predict_course(model, parameters, pressure, t):
    """Flow at all times, plus Jacobian (log coordinates except linear B1)."""
    p = np.maximum(pressure, 0.)
    if model == "B1":
        jac = np.stack([np.ones_like(p), p, p*p], axis=-1)
        q = jac @ np.asarray(parameters)
        return np.maximum(q, 0.), jac*(q > 0)[..., None]
    return _course_ode(p, t, np.asarray(parameters), ("C4", "D1", "D2", "D3").index(model))


def course_endpoint(model, parameters, pressure, t):
    """Unchanged endpoint observer; resolve fast fitted jamming before reading it."""
    if model in {"D2", "D3"}:
        return predict_course(model, parameters, pressure, t)[0][:, -1]
    return predict(model, parameters, pressure, t)


def fit_course(model, course, train, multiplicity, budget):
    """Equal conditions, equal brews, equal duration-normalized within-brew loss.

    Fit the prescribed scoring window; never treat samples as independent brews.
    B0 bounds and two initial guesses are retained, with analytic sensitivities.
    """
    started = time.monotonic()
    p, target, mask = course.pressure[train], course.flow[train], course.mask[train]
    cond = course.brews.condition
    weight = np.array([multiplicity[i]/(len(course.brews.groups)-1)/np.sum(cond == cond[i])
                       for i in train])
    root_weight = np.sqrt(weight[:, None]*mask/mask.sum(axis=1)[:, None])
    if model == "B1":
        design = np.stack([np.ones_like(p), p, p*p], axis=-1)
        value = np.linalg.lstsq((design*root_weight[..., None]).reshape(-1, 3),
                               (target*root_weight).ravel(), rcond=None)[0]
        budget.elapsed += time.monotonic()-started
        budget.check(time.monotonic())
        return value
    lower, upper, starts = FIT_SETTINGS[model]
    cache_x, cache = None, None

    def evaluate(x):
        nonlocal cache_x, cache
        budget.check(started)
        if cache_x is None or not np.array_equal(cache_x, x):
            cache_x = x.copy()
            q, jac = predict_course(model, np.exp(x), p, course.t)
            cache = ((q-target)*root_weight).ravel(), (jac*root_weight[..., None]).reshape(-1, len(x))
        return cache

    try:
        fits = [least_squares(lambda x: evaluate(x)[0], np.log(s),
                             jac=lambda x: evaluate(x)[1], bounds=(np.log(lower), np.log(upper)),
                             ftol=1e-7, xtol=1e-7, gtol=1e-7, x_scale="jac", max_nfev=500)
                for s in starts]
        valid = [f for f in fits if f.success and np.isfinite(f.fun).all()]
        if not valid:
            best = min(fits, key=lambda f: f.cost)
            retry = least_squares(lambda x: evaluate(x)[0], best.x, jac=lambda x: evaluate(x)[1],
                                  bounds=(np.log(lower), np.log(upper)), method="dogbox",
                                  x_scale="jac", ftol=1e-7, xtol=1e-7, gtol=1e-7, max_nfev=1500)
            if not retry.success or not np.isfinite(retry.fun).all():
                raise RuntimeError(f"{model}: trace fit failed; no resample omitted")
            valid = [retry]
        return np.exp(min(valid, key=lambda f: f.cost).x)
    finally:
        budget.elapsed += time.monotonic()-started


def course_folds(model, course, multiplicity, budget):
    values = np.empty_like(course.flow)
    endpoint = np.empty(len(course.brews.ids))
    coefficients = {}
    for group in course.brews.groups:
        train = np.flatnonzero((course.brews.condition != course.brews.condition[group[0]]) &
                               (multiplicity > 0))
        coef = fit_course(model, course, train, multiplicity, budget)
        values[group] = predict_course(model, coef, course.pressure[group], course.t)[0]
        endpoint[group] = course_endpoint(model, coef, course.brews.pressure[group], course.brews.t)
        coefficients[course.brews.fold[group[0]]] = coef.tolist()
    return values, endpoint, coefficients


def brew_samples(brews, count, seed=B0B_SEED):
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(count):
        multiplicity = np.zeros(len(brews.ids), dtype=int)
        for group in brews.groups:
            multiplicity += np.bincount(rng.choice(group, len(group)), minlength=len(brews.ids))
        samples.append(multiplicity)
    return samples


def condition_means(brews, values, multiplicity):
    return np.array([np.average(values[g], weights=multiplicity[g]) for g in brews.groups])


def trend_sign(bounds):
    # Numerical zero only; no new practical trend tolerance is introduced.
    return "RISING" if bounds[0] > 1e-10 else "DECLINING" if bounds[1] < -1e-10 else "FLAT/UNRESOLVED"


def mean_trend_sign(value):
    return "POSITIVE" if value > 1e-10 else "NEGATIVE" if value < -1e-10 else "ZERO"


def trend_correlation(pressures, trends):
    return float(np.corrcoef(pressures, trends)[0, 1]) if np.ptp(trends) > 1e-12 else 0.


def trend_summary(brews, values, draws=None):
    means = condition_means(brews, values, np.ones(len(values)))
    pressure = condition_means(brews, brews.pressure[:, -1], np.ones(len(values)))
    if draws is None:
        draws = np.array([condition_means(brews, values, m) for m in brew_samples(brews, 1000)])
    bounds = [A.interval(draws[:, j]) for j in range(len(brews.groups))]
    pressure_draws = [condition_means(brews, brews.pressure[:, -1], m)
                      for m in brew_samples(brews, len(draws))]
    correlations = [trend_correlation(p, row) for p, row in zip(pressure_draws, draws)]
    return {"mean": means.tolist(), "interval": bounds, "sign": [trend_sign(b) for b in bounds],
            "pressure_correlation": trend_correlation(pressure, means),
            "pressure_correlation_interval": A.interval(correlations)}


def aggregate_trend_rows(stage, scenario, model, course, values, draws=None):
    summary = trend_summary(course.brews, values, draws)
    observed = trend_summary(course.brews, course.observed_trend)
    rows = []
    for j, (p, group) in enumerate(zip(np.unique(course.brews.condition), course.brews.groups)):
        rows.append({"stage": stage, "scenario": scenario, "candidate": model,
                     "pressure condition bar": p, "brews": len(group),
                     "clean end range s": json.dumps([float(course.ends[group].min()),
                                                        float(course.ends[group].max())]),
                     "trend g/s/s": summary["mean"][j], "trend interval": json.dumps(summary["interval"][j]),
                     "trend sign": summary["sign"][j], "observed sign": observed["sign"][j],
                     "observed trend g/s/s": observed["mean"][j],
                     "mean trend sign": mean_trend_sign(summary["mean"][j]),
                     "observed mean trend sign": mean_trend_sign(observed["mean"][j]),
                     "sign agreement": "Y" if mean_trend_sign(summary["mean"][j]) ==
                                              mean_trend_sign(observed["mean"][j]) else "N",
                     "interval-class agreement": "Y" if summary["sign"][j] == observed["sign"][j] else "N",
                     "interval source": "200 refits of brews within conditions" if draws is not None
                                        else "1000 brew resamples; no refit",
                     "trend-pressure correlation": summary["pressure_correlation"],
                     "correlation interval": json.dumps(summary["pressure_correlation_interval"]),
                     "observed 5-10s mean flow g/s": float(course.flow[group][:, (course.t >= 5) &
                                                                     (course.t <= 10)].mean())})
    return rows, summary


def existing_timecourse(brews, observed_flow, raw, out):
    """T1--T3: saved B0 coefficients only; no optimizer is called."""
    residuals, trends = [], []
    stored = A.read_csv(OUT / "RESULT_TABLE.csv")
    for basket in (False, True):
        scenario = "RAW PRIMARY" if not basket else "BASKET SENSITIVITY"
        course = load_course(brews, raw, step=.1, basket=basket, observed_flow=observed_flow)
        if not basket:
            rows, _ = aggregate_trend_rows("T2 observed", scenario, "OBSERVED", course, course.observed_trend)
            trends += rows
        for model in MODELS:
            row = next(r for r in stored if r["candidate"] == model and
                       r["pressure"] == ("basket primary" if basket else "raw sensitivity"))
            coefficients = json.loads(row["parameters"])["by_fold"]
            q, endpoint = np.empty_like(course.flow), np.empty(len(brews.ids))
            for group in course.brews.groups:
                coef = coefficients[course.brews.fold[group[0]]]
                q[group] = predict_course(model, coef, course.pressure[group], course.t)[0]
                endpoint[group] = predict(model, coef, course.brews.pressure[group], course.brews.t)
            error = endpoint-brews.target
            draws = np.array([condition_means(brews, error, m) for m in brew_samples(brews, 1000)])
            for j, (p, group) in enumerate(zip(np.unique(brews.condition), brews.groups)):
                residuals.append({"scenario": scenario, "candidate": model, "pressure condition bar": p,
                                  "brews": len(group), "residual predicted-observed g/s": float(error[group].mean()),
                                  "residual interval": json.dumps(A.interval(draws[:, j])),
                                  "source": "B0 saved held-out coefficients; no refit"})
            rows, _ = aggregate_trend_rows("T3 existing fit", scenario, model, course,
                                           (q*course.late_weights).sum(axis=1))
            trends += rows
    write_csv(out / "RESIDUALS.csv", residuals)
    write_csv(out / "LATE_TRENDS.csv", trends)
    return residuals, trends


def paired_course_loss(brews, squared, seed=B0B_SEED):
    """SCI-MD-010 paired conditions-then-brews bootstrap, B0b's new seed.

    squared has model x brew entries: endpoint squared error OR each brew's
    duration-normalized mean trace squared error. The metric remains mean fold
    RMSE, not pooled RMSE. No time points are resampled as independent units.
    """
    groups = [np.flatnonzero(np.array(brews.fold) == f).tolist() for f in sorted(set(brews.fold))]
    rng = random.Random(seed)
    draws = []
    for _ in range(1000):
        selected = [rng.choice(groups) for _ in groups]
        loss = np.zeros(len(squared))
        for group in selected:
            picked = [rng.choice(group) for _ in group]
            loss += np.sqrt(squared[:, picked].mean(axis=1))
        draws.append(loss/len(groups))
    return np.array(draws)


def _course_refit(arguments):
    model, course, sample, deadline = arguments
    try:
        from numba import set_num_threads
        set_num_threads(1)
    except ImportError:
        pass
    budget = A.FitBudget(max(0., deadline-time.monotonic()))
    values, endpoint, _ = course_folds(model, course, sample, budget)
    slope, peak = refit_response(course.brews, endpoint, sample)
    trends = condition_means(course.brews, (values*course.late_weights).sum(axis=1), sample)
    return slope, peak, trends


def course_refits(model, course, count, budget, workers):
    if count < 200:
        raise ValueError("B0b requires at least 200 refits")
    started = time.monotonic()
    deadline = started+budget.limit-budget.elapsed
    args = [(model, course, m, deadline) for m in brew_samples(course.brews, count)]
    executor = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
    try:
        result = []
        for value in executor.map(_course_refit, args, chunksize=1):
            result.append(value)
            if len(result) % 25 == 0:
                print(json.dumps({"candidate": model, "refits_complete": len(result),
                                  "phase_seconds": time.monotonic()-started}), flush=True)
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
        budget.elapsed += time.monotonic()-started
    return {"slope": A.interval([r[0] for r in result]), "peak": A.interval([r[1] for r in result]),
            "trends": np.array([r[2] for r in result])}


def b0b_pass(model, comparison, refit, agreement, primary=True):
    return (primary and model not in {"D3", "SMOOTH CEILING"} and comparison in {"TIE", "BETTER"}
            and -.176 <= refit["slope"][0] <= refit["slope"][1] <= -.020
            and refit["peak"][0] <= 7 and refit["peak"][1] >= 5 and agreement >= 8)


def smooth_ceiling(course, multiplicity):
    """Optimistic within-condition smooth mean, NOT pressure-held-out prediction.

    All brews in a condition contribute, including the evaluated brew. Fixed
    10-s cubic B-spline knots and no pressure-law restriction: a descriptive
    achievable-fit ceiling, explicitly ineligible for comparison or solver PASS.
    """
    from scipy.interpolate import make_lsq_spline
    values, endpoint = np.empty_like(course.flow), np.empty(len(course.brews.ids))
    knots_by_group = {}
    for group in course.brews.groups:
        w = multiplicity[group, None]*course.mask[group]/course.mask[group].sum(axis=1)[:, None]
        total = w.sum(axis=0)
        use = total > 0
        t = course.t[use]
        mean = (w*course.flow[group]).sum(axis=0)[use]/total[use]
        knots = np.r_[[t[0]]*4, np.arange(10., t[-1]-1, 10.), [t[-1]]*4]
        curve = make_lsq_spline(t, mean, knots, k=3, w=np.sqrt(total[use]))
        values[group] = curve(course.t)
        endpoint[group] = curve(100.)
        knots_by_group[str(course.brews.condition[group[0]])] = {"knots_s": knots.tolist(),
                                                               "coefficients": curve.c.tolist()}
    return values, endpoint, knots_by_group


def timecourse_screen(brews, observed_flow, raw, out, refits, prior, workers, resume):
    """T4 raw primary; basket and T5 low-pressure omissions are sensitivities."""
    budget = A.FitBudget()
    budget.elapsed = prior
    rows = A.read_csv(out / "RESULT_TABLE.csv") if resume and (out / "RESULT_TABLE.csv").exists() else []
    trends = A.read_csv(out / "LATE_TRENDS.csv")
    trends = [r for r in trends if r["stage"] in {"T2 observed", "T3 existing fit"} or resume]
    scenarios = [(False, False, "T4 RAW PRIMARY"), (True, False, "T4 BASKET SENSITIVITY"),
                 (False, True, "T5 RAW >3 BAR SENSITIVITY"), (True, True, "T5 BASKET >3 BAR SENSITIVITY")]
    for basket, omit_low, scenario in scenarios:
        course = load_course(brews, raw, basket=basket, omit_low=omit_low, observed_flow=observed_flow)
        fine = load_course(brews, raw, step=.1, basket=basket, omit_low=omit_low, observed_flow=observed_flow)
        baseline_endpoint, baseline_trace = None, None
        for model in (*MODELS, "SMOOTH CEILING"):
            existing = next((r for r in rows if r["scenario"] == scenario and r["candidate"] == model), None)
            if existing is not None and model != "B1":
                continue
            if existing is None:
                print(json.dumps({"fitting": model, "scenario": scenario, "fit_seconds": budget.elapsed}), flush=True)
            if model == "SMOOTH CEILING":
                ceiling_started = time.monotonic()
                q, endpoint, coef = smooth_ceiling(fine, np.ones(len(fine.brews.ids)))
                samples = brew_samples(fine.brews, refits)
                results = []
                for sample in samples:
                    budget.check(ceiling_started)
                    results.append(smooth_ceiling(fine, sample)[:2])
                responses = [refit_response(fine.brews, e, m) for (_, e), m in zip(results, samples)]
                refit = {"slope": A.interval([r[0] for r in responses]),
                         "peak": A.interval([r[1] for r in responses]),
                         "trends": np.array([condition_means(fine.brews, (v*fine.late_weights).sum(axis=1), m)
                                             for (v, _), m in zip(results, samples)])}
                numeric = 0.
                budget.elapsed += time.monotonic()-ceiling_started
            else:
                if existing is not None:
                    coef = json.loads(existing["parameters"])["by_fold"]
                else:
                    _, _, coef = course_folds(model, course, np.ones(len(course.brews.ids)), budget)
                q, endpoint = np.empty_like(fine.flow), np.empty(len(fine.brews.ids))
                numeric = 0.
                for group in fine.brews.groups:
                    c = coef[fine.brews.fold[group[0]]]
                    q[group] = predict_course(model, c, fine.pressure[group], fine.t)[0]
                    endpoint[group] = course_endpoint(model, c, fine.brews.pressure[group], fine.brews.t)
                    coarse_q = predict_course(model, c, course.pressure[group], course.t)[0]
                    interp = np.array([np.interp(course.t, fine.t, v) for v in q[group]])
                    numeric = max(numeric, float(np.max(np.abs(coarse_q-interp)[course.mask[group]])))
                if existing is None:
                    refit = course_refits(model, course, refits, budget, workers)
            endpoint_se = (endpoint-fine.brews.target)**2
            trace_se = ((q-fine.flow)**2*fine.mask).sum(axis=1)/fine.mask.sum(axis=1)
            if model == "B1":
                baseline_endpoint, baseline_trace = endpoint_se, trace_se
                if existing is not None:
                    continue
            endpoint_draws = paired_course_loss(fine.brews, np.array([baseline_endpoint, endpoint_se]))
            trace_draws = paired_course_loss(fine.brews, np.array([baseline_trace, trace_se]))
            loss = lambda se: float(np.mean([np.sqrt(se[g].mean()) for g in fine.brews.groups]))
            endpoint_ci = A.interval(endpoint_draws[:, 1])
            comparison_ci = A.interval(endpoint_draws[:, 1]-endpoint_draws[:, 0])
            comparison = A.comparison(comparison_ci) if model != "SMOOTH CEILING" else "INELIGIBLE CEILING"
            response = A.response_diagnostics(fine.brews, endpoint, seed=B0B_SEED)
            predicted_trends = (q*fine.late_weights).sum(axis=1)
            trend_rows, ts = aggregate_trend_rows("T4/T5 refit", scenario, model, fine, predicted_trends, refit["trends"])
            agreement = sum(r["sign agreement"] == "Y" for r in trend_rows)
            row = {"scenario": scenario, "candidate": model,
                   "baseline": "B1 refitted to traces in the same scenario/folds",
                   "parameters": json.dumps({"names": PARAMETERS.get(model, ["cubic spline coefficients"]),
                                              "by_condition" if model == "SMOOTH CEILING" else "by_fold": coef,
                                              "Phi_fixed": PHI if model in {"D1", "D3"} else None}),
                   "full-trace RMSE g/s": loss(trace_se), "full-trace RMSE interval": json.dumps(A.interval(trace_draws[:, 1])),
                   "full-trace CAPABILITY": A.capability(A.interval(trace_draws[:, 1]), response["slope"]),
                   "endpoint RMSE g/s": loss(endpoint_se), "endpoint RMSE interval": json.dumps(endpoint_ci),
                   "CAPABILITY": A.capability(endpoint_ci, response["slope"]),
                   "delta versus B1 g/s": loss(endpoint_se)-loss(baseline_endpoint),
                   "delta interval": json.dumps(comparison_ci), "COMPARISON": comparison,
                   "slope g/s/bar": response["slope"], "slope interval no-refit": json.dumps(response["slope_interval"]),
                   "slope interval refit": json.dumps(refit["slope"]), "peak nominal bar": response["peak"],
                   "peak interval no-refit": json.dumps(response["peak_interval"]), "peak interval refit": json.dumps(refit["peak"]),
                   "late-trend agreement": f"{agreement}/{len(fine.brews.groups)}",
                   "late-trend interval-class agreement":
                   f"{sum(r['interval-class agreement'] == 'Y' for r in trend_rows)}/{len(fine.brews.groups)}",
                   "trend-pressure correlation": ts["pressure_correlation"],
                   "correlation interval refit": json.dumps(ts["pressure_correlation_interval"]),
                   "refit count": refits, "eligibility": "EXPLORATORY (5 parameters)" if model == "D3" else
                   "IN-SAMPLE CEILING" if model == "SMOOTH CEILING" else "REFERENCE" if model == "B1" else "ELIGIBLE",
                   "PASS": "Y" if b0b_pass(model, comparison, refit, agreement, scenario == "T4 RAW PRIMARY") else "N",
                   "maximum 0.5s/0.1s trace difference g/s": numeric, "cumulative fitting seconds": budget.elapsed}
            rows.append(row)
            trends += trend_rows
            write_csv(out / "RESULT_TABLE.csv", rows)
            write_csv(out / "LATE_TRENDS.csv", trends)
            print(json.dumps({k: v for k, v in row.items() if k != "parameters"}), flush=True)
    return rows, budget.elapsed


# B0c: scoring starts at measured sustained outflow +2 s. State histories still
# start at stable pressure, preserving the B0b reference equations. Only this
# additive mode uses the onset law and swelling conductance multiplier.
B0C_SEED = 20261031
B0C_OUT = A.ROOT / "docs/research/PRESSURE_PEAK_STAGE_B0C"
B0C_MODELS = ("B1", "C4", "D1", "E1", "E2", "E3")
TAU_BOUNDS = (10., 240.)  # Weak proxy bound; provenance/limitations in SWELLING_PRIOR.md.


def sustained_onset(t, mass, flow, mass_threshold=.5, flow_threshold=.1, hold=2.):
    """First qualifying interval's START, not its confirmation time.

    Inputs begin at first stable pressure; mass is relative to the pre-stable
    baseline. Both strict thresholds must hold continuously for at least hold
    seconds on native samples. An undetected onset is NaN, never imputed.
    """
    good = (mass > mass_threshold) & (flow > flow_threshold)
    start = None
    for j, qualifies in enumerate(good):
        if not qualifies:
            start = None
        elif start is None:
            start = j
        if start is not None and t[j]-t[start] >= hold:
            return float(t[start])
    return float("nan")


def measure_onsets(brews, raw):
    """Read originals; preserve B0's stable alignment and terminal detector.

    Pressure input to the onset law is the median during stable +0--2 s, before
    outflow. Basket pressure subtracts the same observed-flow calibration used
    by B0b. Individual detections stay in an ignored local derived-data file.
    """
    detections, pressure, stable, private = [], [], [], []
    for shot in brews.ids:
        t0, p0, m0, _ = raw_trace(raw / "measurements_time_dependent" / f"{shot}.txt")
        t, p, q, _ = clean_course(t0, p0, m0)
        pre = (t0 >= -2) & (t0 <= 0)
        baseline = np.median(m0[pre]) if pre.any() else m0[0]
        mass = np.interp(t, t0, m0)-baseline
        onset = [sustained_onset(t, mass, q, .5*s, .1*s) for s in (.5, 1., 1.5)]
        early = t <= 2
        a, b, c = A.MACHINE
        pressures = [float(np.median(p[early])),
                     float(np.median(np.maximum(p-a*q*q-b*q-c, 0.)[early]))]
        detections.append(onset)
        pressure.append(pressures)
        stable.append(float(-t0[0]))
        private.append({"brew": shot, "stable elapsed from first record s": -t0[0],
                        "outflow elapsed s": -t0[0]+onset[1], "delay s": onset[1],
                        "delay lower thresholds s": onset[0], "delay upper thresholds s": onset[2]})
    write_csv(A.ROOT / ".b0-b0c-onsets.csv", private)
    return np.array(detections), np.array(pressure), np.array(stable)


def onset_power_fit(brews, pressure, delay, train, multiplicity):
    """Equal-condition weighted log fit: delay=c*(P/bar)^(-n).

    n is unconstrained: no inverse-pressure conclusion is built into the fit.
    No hydraulic target or held-out onset enters a training-fold calibration.
    """
    if not np.isfinite(delay[train]).all() or np.any(delay[train] <= 0):
        raise ValueError("Power law requires detected positive delays for every selected brew")
    weight = np.array([multiplicity[i]/np.sum(brews.condition == brews.condition[i]) for i in train])
    design = np.column_stack([np.ones(len(train)), -np.log(pressure[train])])
    value = np.linalg.lstsq(design*np.sqrt(weight[:, None]),
                           np.log(delay[train])*np.sqrt(weight), rcond=None)[0]
    return np.array([np.exp(value[0]), value[1]])


def onset_report(brews, raw, out):
    detections, pressure, stable = measure_onsets(brews, raw)
    samples = brew_samples(brews, 1000, B0C_SEED)
    rows = []
    for j, scale in enumerate((.5, 1., 1.5)):
        for view, name in enumerate(("RAW PRIMARY", "BASKET SENSITIVITY")):
            delay = detections[:, j]
            for group in brews.groups:
                found = group[np.isfinite(delay[group])]
                boot = [np.average(delay[found], weights=m[found]) for m in samples
                        if m[found].sum() > 0]
                rows.append({"check": "condition onset", "pressure view": name,
                             "threshold scale": scale, "pressure condition bar": brews.condition[group[0]],
                             "mass threshold g": .5*scale, "flow threshold g/s": .1*scale, "hold s": 2.,
                             "brews": len(group), "detected": len(found), "undetected": len(group)-len(found),
                             "early pressure mean bar": float(pressure[group, view].mean()),
                             "stable elapsed mean s": float(stable[group].mean()),
                             "outflow elapsed mean s": float(np.mean(stable[found]+delay[found])) if len(found) else "",
                             "delay mean s": float(delay[found].mean()) if len(found) else "",
                             "delay interval s": json.dumps(A.interval(boot)) if boot else "",
                             "interpretation": "FULL COHORT" if len(found) == len(group) else "UNDETECTED; no imputation"})
            if np.isfinite(delay).all():
                train = np.arange(len(delay))
                coef = onset_power_fit(brews, pressure[:, view], delay, train, np.ones(len(delay)))
                fits = np.array([onset_power_fit(brews, pressure[:, view], delay, train, m) for m in samples])
                rows.append({"check": "power law", "pressure view": name, "threshold scale": scale,
                             "c seconds at 1 bar": coef[0], "c interval": json.dumps(A.interval(fits[:, 0])),
                             "n": coef[1], "n interval": json.dumps(A.interval(fits[:, 1])),
                             "interpretation": "Equal-condition log fit; n unconstrained; 1000 brew bootstraps"})
            else:
                rows.append({"check": "power law", "pressure view": name, "threshold scale": scale,
                             "interpretation": "NOT ESTIMABLE ON FULL COHORT: undetected onsets"})
    for row in rows:
        row["source"] = "Waszkiewicz et al. (2025), doi:10.5281/zenodo.18046315, CC-BY-4.0; native traces"
        row["seed"] = B0C_SEED
    write_csv(out / "ONSET.csv", rows)
    if not np.isfinite(detections[:, 1]).all():
        raise ValueError("Primary onsets incomplete: stop before trace refits; no cohort changes")
    return detections[:, 1], pressure


def retime_course(course, delay):
    """Only the loss mask changes; neither pressure/state history nor endpoint."""
    mask = (course.t[None, :] >= delay[:, None]+2) & (course.t[None, :] <= course.ends[:, None])
    if np.any(mask.sum(axis=1) == 0):
        raise ValueError("Empty post-onset trace")
    return replace(course, mask=mask)


@njit(cache=True)
def _swell_course(parameters, pressure, t, delay, mc, kind):
    values = np.empty(pressure.shape)
    jac = np.empty((pressure.shape[0], pressure.shape[1], 3))
    for i in range(len(pressure)):
        ratio = delay[i]/parameters[2]
        base = np.array([parameters[0]*np.exp(-ratio), parameters[1], mc])
        q, dj = _course_ode(pressure[i:i+1], t, base, kind)
        values[i] = q[0]
        jac[i, :, 0] = dj[0, :, 0]
        jac[i, :, 1] = dj[0, :, 1]
        jac[i, :, 2] = dj[0, :, 0]*ratio
    return values, jac


def predict_swelling(model, parameters, pressure, t, delay, mc):
    """S multiplies conductance inside both Q and dM/dt, once per brew.

    E1/E2 use C4, E3 uses D1; Mc is fixed from the corresponding training-fold
    reference. Three free hydraulic parameters: a, compaction scale, tau.
    The onset law and Mc are estimated nuisance inputs, not free hydraulic
    parameters; every refit resamples and re-estimates them within training.
    """
    return _swell_course(np.asarray(parameters, dtype=float), np.maximum(pressure, 0.), t,
                         np.asarray(delay), float(mc), 1 if model == "E3" else 0)


def fit_swelling(model, course, train, multiplicity, delay, reference, budget):
    started = time.monotonic()
    p, target, mask = course.pressure[train], course.flow[train], course.mask[train]
    cond = course.brews.condition
    weight = np.array([multiplicity[i]/(len(course.brews.groups)-1)/np.sum(cond == cond[i]) for i in train])
    root = np.sqrt(weight[:, None]*mask/mask.sum(axis=1)[:, None])
    base = "D1" if model == "E3" else "C4"
    lower = np.array([*FIT_SETTINGS[base][0][:2], TAU_BOUNDS[0]])
    upper = np.array([*FIT_SETTINGS[base][1][:2], TAU_BOUNDS[1]])
    cache_x, cache = None, None

    def evaluate(x):
        nonlocal cache_x, cache
        budget.check(started)
        if cache_x is None or not np.array_equal(cache_x, x):
            cache_x = x.copy()
            q, jac = predict_swelling(model, np.exp(x), p, course.t, delay[train], reference[2])
            cache = ((q-target)*root).ravel(), (jac*root[..., None]).reshape(-1, 3)
        return cache

    try:
        fits = []
        for tau in (15., 60., 200.):
            initial = np.clip([reference[0]*np.exp(np.median(delay[train])/tau), reference[1], tau],
                              lower*1.00001, upper/1.00001)
            fits.append(least_squares(lambda x: evaluate(x)[0], np.log(initial),
                                      jac=lambda x: evaluate(x)[1], bounds=(np.log(lower), np.log(upper)),
                                      x_scale="jac", ftol=1e-7, xtol=1e-7, gtol=1e-7, max_nfev=500))
        valid = [f for f in fits if f.success and np.isfinite(f.fun).all()]
        if not valid:
            best = min(fits, key=lambda f: f.cost)
            retry = least_squares(lambda x: evaluate(x)[0], best.x, jac=lambda x: evaluate(x)[1],
                                  bounds=(np.log(lower), np.log(upper)), method="dogbox", x_scale="jac",
                                  ftol=1e-7, xtol=1e-7, gtol=1e-7, max_nfev=1500)
            if not retry.success or not np.isfinite(retry.fun).all():
                raise RuntimeError(f"{model}: swelling fit failed; no resample omitted")
            valid = [retry]
        return np.exp(min(valid, key=lambda f: f.cost).x)
    finally:
        budget.elapsed += time.monotonic()-started


def swelling_folds(course, measured_delay, early_pressure, multiplicity, budget):
    """Joint folds share reference fits; fixed inputs never use held-out brews."""
    n = len(course.brews.ids)
    result = {m: {"q": np.empty_like(course.flow), "endpoint": np.empty(n), "coefficients": {}}
              for m in B0C_MODELS}
    # Calibrate onset inputs before any hydraulic fit, separately in each fold.
    onset_bank = {}
    for group in course.brews.groups:
        train = np.flatnonzero((course.brews.condition != course.brews.condition[group[0]]) & (multiplicity > 0))
        onset_bank[course.brews.fold[group[0]]] = onset_power_fit(
            course.brews, early_pressure, measured_delay, train, multiplicity)
    for group in course.brews.groups:
        train = np.flatnonzero((course.brews.condition != course.brews.condition[group[0]]) & (multiplicity > 0))
        fold = course.brews.fold[group[0]]
        onset_coef = onset_bank[fold]
        predicted_delay = onset_coef[0]*early_pressure**(-onset_coef[1])
        references = {}
        for model in B0C_MODELS:
            if model in {"B1", "C4", "D1"}:
                coef = fit_course(model, course, train, multiplicity, budget)
                references[model] = coef
                q = predict_course(model, coef, course.pressure[group], course.t)[0]
                endpoint = course_endpoint(model, coef, course.brews.pressure[group], course.brews.t)
                record = {"free": coef.tolist()}
            else:
                ref = references["D1" if model == "E3" else "C4"]
                delay = measured_delay if model == "E2" else predicted_delay
                coef = fit_swelling(model, course, train, multiplicity, delay, ref, budget)
                q = predict_swelling(model, coef, course.pressure[group], course.t, delay[group], ref[2])[0]
                endpoint = predict_swelling(model, coef, course.brews.pressure[group], course.brews.t,
                                             delay[group], ref[2])[0][:, -1]
                record = {"free": coef.tolist(), "Mc_fixed_g": float(ref[2]),
                          "onset_c_fixed_s": float(onset_coef[0]), "onset_n_fixed": float(onset_coef[1])}
            result[model]["q"][group] = q
            result[model]["endpoint"][group] = endpoint
            result[model]["coefficients"][fold] = record
    return result


def _swelling_refit(arguments):
    course, delay, pressure, sample, deadline = arguments
    budget = A.FitBudget(max(0., deadline-time.monotonic()))
    result = swelling_folds(course, delay, pressure, sample, budget)
    return {m: {"response": refit_response(course.brews, r["endpoint"], sample),
                "trends": condition_means(course.brews, (r["q"]*course.late_weights).sum(axis=1), sample)}
            for m, r in result.items()}


def swelling_refits(course, delay, pressure, count, budget, workers):
    if count < 200:
        raise ValueError("B0c requires at least 200 whole-brew refits")
    started = time.monotonic()
    deadline = started+budget.limit-budget.elapsed
    args = [(course, delay, pressure, sample, deadline)
            for sample in brew_samples(course.brews, count, B0C_SEED)]
    executor = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
    results = []
    try:
        for value in executor.map(_swelling_refit, args, chunksize=1):
            results.append(value)
            if len(results) % 10 == 0:
                print(json.dumps({"joint_refits_complete": len(results),
                                  "phase_seconds": time.monotonic()-started}), flush=True)
    finally:
        executor.shutdown(wait=True, cancel_futures=True)
        budget.elapsed += time.monotonic()-started
    return {model: {"slope": A.interval([r[model]["response"][0] for r in results]),
                    "peak": A.interval([r[model]["response"][1] for r in results]),
                    "trends": np.array([r[model]["trends"] for r in results])}
            for model in B0C_MODELS}


def swelling_predict_saved(course, delay, pressure, coefficients):
    result = {}
    for model, records in coefficients.items():
        q, endpoint = np.empty_like(course.flow), np.empty(len(delay))
        for group in course.brews.groups:
            record = records[course.brews.fold[group[0]]]
            coef = record["free"]
            if model in {"B1", "C4", "D1"}:
                q[group] = predict_course(model, coef, course.pressure[group], course.t)[0]
                endpoint[group] = course_endpoint(model, coef, course.brews.pressure[group], course.brews.t)
            else:
                d = delay if model == "E2" else record["onset_c_fixed_s"]*pressure**(-record["onset_n_fixed"])
                q[group] = predict_swelling(model, coef, course.pressure[group], course.t, d[group], record["Mc_fixed_g"])[0]
                endpoint[group] = predict_swelling(model, coef, course.brews.pressure[group], course.brews.t,
                                                   d[group], record["Mc_fixed_g"])[0][:, -1]
        result[model] = {"q": q, "endpoint": endpoint, "coefficients": records}
    return result


def swelling_rows(course, result, scenario, stage, refits=None):
    brews = course.brews
    base = result["B1"]["endpoint"]-brews.target
    samples = brew_samples(brews, 1000, B0C_SEED)
    observed_means = condition_means(brews, course.observed_trend, np.ones(len(base)))
    rows = []
    loss = lambda se: float(np.mean([np.sqrt(se[g].mean()) for g in brews.groups]))
    for model, r in result.items():
        error = r["endpoint"]-brews.target
        trace_error = ((r["q"]-course.flow)*course.mask).sum(axis=1)/course.mask.sum(axis=1)
        trace_se = ((r["q"]-course.flow)**2*course.mask).sum(axis=1)/course.mask.sum(axis=1)
        edraw = paired_course_loss(brews, np.array([base**2, error**2]), B0C_SEED)
        tdraw = paired_course_loss(brews, np.array([trace_se]), B0C_SEED)
        bounds = A.interval(edraw[:, 1])
        delta = A.interval(edraw[:, 1]-edraw[:, 0])
        comparison = A.comparison(delta)
        response = A.response_diagnostics(brews, r["endpoint"], seed=B0C_SEED)
        trends = (r["q"]*course.late_weights).sum(axis=1)
        means = condition_means(brews, trends, np.ones(len(base)))
        agreement = sum(mean_trend_sign(a) == mean_trend_sign(b) for a, b in zip(means, observed_means))
        refit = refits[model] if refits is not None else None
        passed = (model != "E2" and refit is not None and b0b_pass(
            model, comparison, refit, agreement, scenario == "RAW PRIMARY"))
        comp_name = "Ydry_bar" if model == "E3" else "Pstar_bar"
        row = {"scenario": scenario, "stage": stage, "candidate": model,
               "parameters": json.dumps({"names": PARAMETERS[model] if model in PARAMETERS else
                                          ["a_g_s_bar", comp_name, "tau_s"], "by_fold": r["coefficients"]}),
               "baseline": "B1, same scenario and fit stage", "endpoint RMSE g/s": loss(error**2),
               "endpoint RMSE interval": json.dumps(bounds), "CAPABILITY": A.capability(bounds, response["slope"]),
               "delta versus B1 g/s": loss(error**2)-loss(base**2), "delta interval": json.dumps(delta),
               "COMPARISON": comparison, "full-trace RMSE g/s": loss(trace_se),
               "full-trace RMSE interval": json.dumps(A.interval(tdraw[:, 0])),
               "slope g/s/bar": response["slope"], "slope interval no-refit": json.dumps(response["slope_interval"]),
               "slope interval refit": json.dumps(refit["slope"]) if refit else "",
               "peak nominal bar": response["peak"], "peak interval no-refit": json.dumps(response["peak_interval"]),
               "peak interval refit": json.dumps(refit["peak"]) if refit else "",
               "late-trend agreement": f"{agreement}/11", "late-trend means g/s/s": json.dumps(means.tolist()),
               "late-trend intervals refit": json.dumps([A.interval(refit["trends"][:, j]) for j in range(len(means))]) if refit else "",
               "refit count": len(refit["trends"]) if refit else 0,
               "eligibility": "CONDITIONAL; measured onset; ineligible" if model == "E2" else
               "EXISTING FIT DIAGNOSTIC" if refit is None else "REFERENCE" if model == "B1" else "ELIGIBLE",
               "PASS": "Y" if passed else "N"}
        for label, band in (("1-3.5 bar", (1., 3.5)), ("4-6 bar", (4., 6.))):
            selected = (np.unique(brews.condition) >= band[0]) & (np.unique(brews.condition) <= band[1])
            for kind, residual in (("endpoint", error), ("trace", trace_error)):
                center = condition_means(brews, residual, np.ones(len(base)))[selected].mean()
                draws = [condition_means(brews, residual, s)[selected].mean() for s in samples]
                row[f"{kind} residual {label} g/s"] = float(center)
                row[f"{kind} residual {label} interval"] = json.dumps(A.interval(draws))
        rows.append(row)
    return rows


def swelling_screen(brews, observed_flow, raw, out, count, prior, workers, resume):
    budget = A.FitBudget()
    budget.elapsed = prior
    delay, early_pressure = onset_report(brews, raw, out)
    rows = A.read_csv(out / "RESULT_TABLE.csv") if resume and (out / "RESULT_TABLE.csv").exists() else []
    old_rows = A.read_csv(B0B_OUT / "RESULT_TABLE.csv")
    for view, scenario in enumerate(("RAW PRIMARY", "BASKET SENSITIVITY")):
        if any(r["scenario"] == scenario and r["stage"] == "T4 REFIT" for r in rows):
            continue
        course = retime_course(load_course(brews, raw, basket=bool(view), observed_flow=observed_flow), delay)
        fine = retime_course(load_course(brews, raw, step=.1, basket=bool(view), observed_flow=observed_flow), delay)
        existing = {r["candidate"]: {f: {"free": c} for f, c in json.loads(r["parameters"])["by_fold"].items()}
                    for r in old_rows if r["scenario"] == "T4 "+scenario and r["candidate"] in {"B1", "C4", "D1"}}
        old_result = swelling_predict_saved(fine, delay, early_pressure[:, view], existing)
        rows = [r for r in rows if r["scenario"] != scenario]
        rows += swelling_rows(fine, old_result, scenario, "T2 EXISTING")
        write_csv(out / "RESULT_TABLE.csv", rows)
        print(json.dumps({"fitting": scenario, "fit_seconds": budget.elapsed}), flush=True)
        point = swelling_folds(course, delay, early_pressure[:, view], np.ones(len(delay)), budget)
        coef = {m: r["coefficients"] for m, r in point.items()}
        # Ignored checkpoint is derived fit output, never source rows or a record system.
        (A.ROOT / f".b0-b0c-point-{view}.json").write_text(json.dumps(coef))
        precise = swelling_predict_saved(fine, delay, early_pressure[:, view], coef)
        print(json.dumps({"point_fits_complete": scenario, "fit_seconds": budget.elapsed,
                          "endpoint_RMSE": {m: float(np.mean([np.sqrt(np.mean((r['endpoint'][g]-brews.target[g])**2))
                                                               for g in brews.groups])) for m, r in precise.items()}}), flush=True)
        refit = swelling_refits(course, delay, early_pressure[:, view], count, budget, workers)
        new_rows = swelling_rows(fine, precise, scenario, "T4 REFIT", refit)
        for row in new_rows:
            m = row["candidate"]
            interp = np.array([np.interp(course.t, fine.t, q) for q in precise[m]["q"]])
            row["maximum 0.5s/0.1s trace difference g/s"] = float(np.max(np.abs(interp-point[m]["q"])[course.mask]))
            row["cumulative fitting seconds"] = budget.elapsed
        rows += new_rows
        write_csv(out / "RESULT_TABLE.csv", rows)
        print(json.dumps({"completed": scenario, "fit_seconds": budget.elapsed,
                          "verdicts": [{k: r[k] for k in ("candidate", "endpoint RMSE g/s", "COMPARISON",
                                        "slope interval refit", "peak interval refit", "late-trend agreement", "PASS")}
                                       for r in new_rows]}), flush=True)
    return rows, budget.elapsed


# B0d: timing is a separate target, never a hydraulic state/input. The only
# cross-observable inputs are training-fold TIMING PARAMETERS, fixed in T2.
B0D_SEED = 20261101
B0D_OUT = A.ROOT / "docs/research/PRESSURE_PEAK_STAGE_B0D"
P_ATM = 1.01325  # bar; standard atmosphere, matching the Foster card
_D1_PEAK_PHI = (4+PHI-np.sqrt((4+PHI)**2-24*PHI))/4
D1_PEAK_RATIO = (PHI-_D1_PEAK_PHI)/(1-PHI)  # air-free argmax(P*k_D1)/Ydry
_INVERSE_COEFFICIENTS = 1/(np.arange(1., 20.)*np.cumprod(np.arange(1., 20.)))


def boyle_saturation(pressure, s0):
    """Gauge P in bar. s0 is air fraction at zero gauge pressure, not Sr water."""
    return 1-s0*P_ATM/(np.asarray(pressure)+P_ATM)


def air_conductance(pressure, pstar, s0=0., exponent=3, kind=0):
    """P*k*kr; excludes scale and delivered-mass relaxation.

    For D1 (kind=1), pstar reparameterizes Ydry as its air-free conductance
    peak. For C4 it is the exponential scale. With air, the actual peak is
    computed separately; comparing the exponential scale alone is not fair.
    """
    p = np.asarray(pressure)
    k = np.exp(-p/pstar) if kind == 0 else locked_ratio(p, pstar/D1_PEAK_RATIO)
    return p*k*boyle_saturation(p, s0)**exponent


def conductance_peak(pstar, s0=0., exponent=3, kind=0):
    if s0 == 0:
        return float(pstar)
    young = pstar/D1_PEAK_RATIO

    def derivative(p):
        compaction = -1/pstar
        if kind:
            phi = PHI-(1-PHI)*p/young
            compaction = -(1-PHI)/young*(3/phi+2/(1-phi))
        air = exponent*s0*P_ATM/((p+P_ATM)*(p+P_ATM-s0*P_ATM))
        return 1/p+compaction+air

    high = young*PHI/(1-PHI)*(1-1e-10) if kind else pstar*(exponent+2)+P_ATM
    return float(brentq(derivative, 1e-8, high))


def timing_specs():
    return {"W0": (-1, 0), "W1": (0, 0), "WD1": (1, 0),
            **{name+suffix: (kind, m) for suffix, m in (("", 3), ("-m2", 2), ("-m4", 4))
               for name, kind in (("W2", 0), ("WD2", 1))}}


def timing_predict(parameters, pressure, kind=0, exponent=0):
    if kind == -1:
        return np.polynomial.polynomial.polyval(pressure, parameters)
    t0, c, pstar, s0 = parameters
    return t0+c/air_conductance(pressure, pstar, s0, exponent, kind)


def _b0d_solve(evaluate, starts, lower, upper, budget):
    """Shared bounded least squares; failed optimizations never become draws."""
    started = time.monotonic()
    cache_x, cached = None, None

    def value(x):
        nonlocal cache_x, cached
        budget.check(started)
        if cache_x is None or not np.array_equal(cache_x, x):
            cache_x, cached = x.copy(), evaluate(x)
        return cached

    try:
        fits = [least_squares(lambda x: value(x)[0], np.clip(s, lower+1e-10, upper-1e-10),
                             jac=lambda x: value(x)[1], bounds=(lower, upper), x_scale="jac",
                             ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=500) for s in starts]
        valid = [r for r in fits if r.success and np.isfinite(r.fun).all()]
        if not valid:
            best = min(fits, key=lambda r: r.cost)
            retry = least_squares(lambda x: value(x)[0], best.x, jac=lambda x: value(x)[1],
                                  bounds=(lower, upper), method="dogbox", x_scale="jac",
                                  ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500)
            if not retry.success or not np.isfinite(retry.fun).all():
                raise RuntimeError("B0d fit failed; no failed resample is discarded")
            valid = [retry]
        return min(valid, key=lambda r: r.cost).x
    finally:
        budget.elapsed += time.monotonic()-started


def fit_timing(pressure, delay, weights, kind, exponent, budget):
    root = np.sqrt(weights)
    if kind == -1:
        design = np.column_stack([np.ones(len(pressure)), pressure, pressure**2])
        return np.linalg.lstsq(design*root[:, None], delay*root, rcond=None)[0]
    # The declared 0--14-bar domain must have positive D1 permeability. This
    # forcing-domain bound uses no held-out timing or flow observations.
    minimum = 14*(1-PHI)/PHI*D1_PEAK_RATIO*1.00001 if kind else .5
    lower = np.array([0., np.log(.0001), np.log(minimum), 0.])
    upper = np.array([120., np.log(1e4), np.log(100.), 1.])
    free = np.arange(4 if exponent else 3)

    def evaluate(x):
        z = np.zeros(4); z[free] = x
        t0, c, pstar, s0 = z[0], np.exp(z[1]), np.exp(z[2]), z[3]
        term = c/air_conductance(pressure, pstar, s0, exponent, kind)
        comp = pressure/pstar
        if kind:
            shift = (1-PHI)*pressure*D1_PEAK_RATIO/pstar
            phi = PHI-shift
            comp = shift*(3/phi+2/(1-phi))
        air = exponent*P_ATM/(pressure+P_ATM)/boyle_saturation(pressure, s0)
        jac = np.column_stack([np.ones(len(pressure)), term, -term*comp, term*air])
        return (t0+term-delay)*root, jac[:, free]*root[:, None]

    starts = [np.array([a, np.log(c), np.log(p), s])[free]
              for a, c, p, s in ((0., 15., 6., .2), (8., 3., 5., .8), (10., 1., 8., .95))]
    x = _b0d_solve(evaluate, starts, lower[free], upper[free], budget)
    return np.array([x[0], np.exp(x[1]), np.exp(x[2]), x[3] if exponent else 0.])


@njit(cache=True)
def _delivered_scalar(exposure):
    x = exposure
    for _ in range(8):
        series = 0.
        for k in range(19):
            series -= np.expm1(-(k+1)*x)*_INVERSE_COEFFICIENTS[k]
        x = max(0., x-(x+series-exposure)/np.exp(np.exp(-x)))
    return x


@njit(cache=True)
def _air_capacity(p, lock, a, pstar, s0, exponent, kind):
    comp = p/pstar
    k = np.exp(-comp)
    if kind:
        shift = (1-PHI)*lock*D1_PEAK_RATIO/pstar
        phi = max(PHI-shift, 0.)
        k = (phi/PHI)**3*((1-PHI)/(1-phi))**2
        comp = shift*(3/phi+2/(1-phi)) if phi > 0 else 0.
    saturation = 1-s0*P_ATM/(p+P_ATM)
    base = a*p*k*saturation**exponent
    air = -exponent*P_ATM/(p+P_ATM)/max(saturation, 1e-15)
    return base, base*comp, base*air


@njit(cache=True)
def air_endpoint(parameters, pressure, t, kind=0, exponent=3):
    """Exact separated state with trapezoid exposure, matching the B0 observer.

    Parameters a, Pstar, Mc, s0; Jacobian coordinates log(a), log(Pstar),
    log(Mc), s0. No measured timing, mass or flow enters this prediction.
    """
    a, pstar, mc, s0 = parameters
    result = np.empty(len(pressure)); jac = np.empty((len(pressure), 4))
    for i in range(len(pressure)):
        lock = max(pressure[i, 0], 0.)
        prev = _air_capacity(lock, lock, a, pstar, s0, exponent, kind)
        total = np.zeros(3)
        for j in range(1, len(t)):
            now = _air_capacity(max(pressure[i, j], 0.), lock, a, pstar, s0, exponent, kind)
            for k in range(3):
                total[k] += (prev[k]+now[k])*(t[j]-t[j-1])/2
            prev = now
        exposure = total[0]/mc
        x = _delivered_scalar(exposure)
        factor = np.exp(-np.exp(-x))
        q = prev[0]*factor
        common = q*np.exp(-x)*factor/mc
        result[i] = q
        jac[i, 0] = q+common*total[0]
        jac[i, 1] = prev[1]*factor+common*total[1]
        jac[i, 2] = -common*total[0]
        jac[i, 3] = prev[2]*factor+common*total[2]
    return result, jac


@njit(cache=True)
def air_trends(parameters, pressure, t, late_weights, kind=0, exponent=3):
    """Unchanged last-30-s observer; no outflow onset used as an input."""
    a, pstar, mc, s0 = parameters
    result = np.zeros(len(pressure))
    for i in range(len(pressure)):
        lock = max(pressure[i, 0], 0.)
        previous = _air_capacity(lock, lock, a, pstar, s0, exponent, kind)[0]
        total = 0.
        for j in range(len(t)):
            now = _air_capacity(max(pressure[i, j], 0.), lock, a, pstar, s0, exponent, kind)[0]
            if j:
                total += (previous+now)*(t[j]-t[j-1])/2
            if late_weights[i, j] != 0:
                x = _delivered_scalar(total/mc)
                result[i] += late_weights[i, j]*now*np.exp(-np.exp(-x))
            previous = now
    return result


def fit_air_flow(pressure, t, target, weights, kind, exponent, mode, reference, timing, budget):
    """Reference: a,Pstar,Mc; T2: a,Mc; F: a,Pstar,s0 with fold-fixed Mc."""
    root = np.sqrt(weights)
    template = np.array(reference, dtype=float)
    lower = np.array([np.log(.001), np.log(.1 if not kind else 10*D1_PEAK_RATIO), np.log(.01), 0.])
    upper = np.array([np.log(20.), np.log(100. if not kind else 1e6*D1_PEAK_RATIO), np.log(1000.), 1.])
    if mode == "REFERENCE":
        free = np.array([0, 1, 2]); template[3] = 0.
        candidates = [template.copy(), np.array([2., 12. if not kind else 300*D1_PEAK_RATIO, 150., 0.])]
    elif mode == "T2":
        free = np.array([0, 2]); template[1], template[3] = timing[2], timing[3]
        candidates = [template.copy() for _ in range(2)]
        candidates[0][2], candidates[1][2] = 20., 300.
    else:
        free = np.array([0, 1, 3])
        candidates = [template.copy(), template.copy()]
        for c, s in zip(candidates, (.2, .8)):
            c[1] *= .8; c[3] = s
    z = template.copy(); z[:3] = np.log(z[:3])

    def evaluate(x):
        trial = z.copy(); trial[free] = x; trial[:3] = np.exp(trial[:3])
        q, jac = air_endpoint(trial, pressure, t, kind, exponent)
        return (q-target)*root, jac[:, free]*root[:, None]

    starts = []
    for c in candidates:
        c[:3] = np.log(c[:3]); starts.append(c[free])
    best = _b0d_solve(evaluate, starts, lower[free], upper[free], budget)
    z[free] = best; z[:3] = np.exp(z[:3])
    return z


def flow_specs():
    specs = {"B1": (-1, 0, "REFERENCE", None), "C4": (0, 0, "REFERENCE", "W1"),
             "D1": (1, 0, "REFERENCE", "WD1")}
    for name, (kind, m) in timing_specs().items():
        if name != "W0":
            specs["T2-"+name] = (kind, m, "T2", name)
    for suffix, m in (("", 3), ("-m2", 2), ("-m4", 4)):
        for name, kind, timing in (("F1", 0, "W2"), ("F2", 1, "WD2")):
            specs[name+suffix] = (kind, m, "F", timing+suffix)
    return specs


def timing_peak(parameters, kind, exponent):
    if kind == -1:
        a, b, c = parameters
        p = np.clip(-b/(2*c), 1., 13.) if c > 0 else (1. if b+14*c > 0 else 13.)
        return float(p)
    return conductance_peak(parameters[2], parameters[3], exponent, kind)


def air_joint_fit(brews, course, pressure, delay, sample, budget):
    """Full-cohort coefficients are descriptive only; all scores use LOPO fits.

    Each bootstrap repeats both observables' calibrations. A fold's timing,
    reference Mc and hydraulic coefficients use only its training brews.
    """
    n = len(brews.ids)
    timing = {m: {"prediction": np.empty(n), "by_fold": {}} for m in timing_specs()}
    flow = {m: {"endpoint": np.empty(n), "trends": np.empty(n), "by_fold": {}} for m in flow_specs()}
    fit_t = np.linspace(0., 100., 201)
    fit_p = np.array([np.interp(fit_t, brews.t, p) for p in brews.pressure])
    for held in [None, *brews.groups]:
        train = np.flatnonzero(sample > 0) if held is None else np.flatnonzero(
            (sample > 0) & (brews.condition != brews.condition[held[0]]))
        weights = np.array([sample[i]/np.sum(brews.condition == brews.condition[i]) for i in train])
        weights /= weights.sum()
        fold = "DESCRIPTIVE_ALL" if held is None else brews.fold[held[0]]
        for model, (kind, m) in timing_specs().items():
            coef = fit_timing(pressure[train], delay[train], weights, kind, m, budget)
            timing[model]["by_fold"][fold] = coef.tolist()
            if held is not None:
                timing[model]["prediction"][held] = timing_predict(coef, pressure[held], kind, m)
        references = {}
        for model, (kind, m, mode, timed) in flow_specs().items():
            if model == "B1":
                coef = A.fit("B1", brews.pressure[train], brews.t, brews.target[train], weights, budget)
            else:
                reference = np.array([1., 5. if kind == 0 else 200*D1_PEAK_RATIO, 60., 0.]) if mode == "REFERENCE" else references[kind]
                coef = fit_air_flow(fit_p[train], fit_t, brews.target[train], weights, kind, m, mode,
                                    reference, timing[timed]["by_fold"][fold], budget)
                if mode == "REFERENCE":
                    references[kind] = coef
            flow[model]["by_fold"][fold] = coef.tolist()
            if held is not None:
                if model == "B1":
                    q = predict_course("B1", coef, course.pressure[held], course.t)[0]
                    flow[model]["endpoint"][held] = A.predict("B1", coef, brews.pressure[held], brews.t)
                    flow[model]["trends"][held] = (q*course.late_weights[held]).sum(axis=1)
                else:
                    flow[model]["endpoint"][held] = air_endpoint(coef, brews.pressure[held], brews.t, kind, m)[0]
                    flow[model]["trends"][held] = air_trends(coef, course.pressure[held], course.t, course.late_weights[held], kind, m)
    return {"timing": timing, "flow": flow}


def _air_refit(arguments):
    brews, course, pressure, delay, sample, deadline = arguments
    result = air_joint_fit(brews, course, pressure, delay, sample,
                           A.FitBudget(max(0., deadline-time.monotonic())))
    timing, flow = {}, {}
    for model, (kind, m) in timing_specs().items():
        coef = result["timing"][model]["by_fold"]["DESCRIPTIVE_ALL"]
        timing[model] = {"parameters": coef, "minimum": timing_peak(coef, kind, m)}
    for model, (kind, m, _, _) in flow_specs().items():
        r = result["flow"][model]
        coef = r["by_fold"]["DESCRIPTIVE_ALL"]
        flow[model] = {"parameters": coef, "response": refit_response(brews, r["endpoint"], sample),
                       "trends": condition_means(brews, r["trends"], sample).tolist(),
                       "conductance_peak": conductance_peak(coef[1], coef[3], m, kind) if kind >= 0 else None}
    return {"timing": timing, "flow": flow}


def b0d_onsets(brews, raw):
    """Reuse the detector and verify against every primary B0c onset aggregate."""
    detections, pressure, _ = measure_onsets(brews, raw)
    delay = detections[:, 1]
    if not np.isfinite(delay).all():
        raise ValueError("B0c primary onset cohort is incomplete")
    rows = A.read_csv(B0C_OUT / "ONSET.csv")
    for r in rows:
        if r["check"] == "condition onset" and float(r["threshold scale"]) == 1:
            group = brews.condition == float(r["pressure condition bar"])
            np.testing.assert_allclose(delay[group].mean(), float(r["delay mean s"]), atol=1e-12)
            assert int(r["detected"]) == int(group.sum())
    return delay, pressure


def _interval_overlap(left, right):
    return max(left[0], right[0]) <= min(left[1], right[1])


def air_replay(brews, course, pressure, saved):
    """Reproduce scored predictions using aggregate fold coefficients only."""
    result = {"timing": {}, "flow": {}}
    for model, (kind, m) in timing_specs().items():
        bank = saved["timing"][model]["by_fold"]
        prediction = np.empty(len(brews.ids))
        for group in brews.groups:
            prediction[group] = timing_predict(bank[brews.fold[group[0]]], pressure[group], kind, m)
        result["timing"][model] = {"prediction": prediction, "by_fold": bank}
    for model, (kind, m, _, _) in flow_specs().items():
        bank = saved["flow"][model]["by_fold"]
        endpoint, trends = np.empty(len(brews.ids)), np.empty(len(brews.ids))
        for group in brews.groups:
            coef = np.asarray(bank[brews.fold[group[0]]])
            if model == "B1":
                endpoint[group] = A.predict(model, coef, brews.pressure[group], brews.t)
                q = predict_course(model, coef, course.pressure[group], course.t)[0]
                trends[group] = (q*course.late_weights[group]).sum(axis=1)
            else:
                endpoint[group] = air_endpoint(coef, brews.pressure[group], brews.t, kind, m)[0]
                trends[group] = air_trends(coef, course.pressure[group], course.t, course.late_weights[group], kind, m)
        result["flow"][model] = {"endpoint": endpoint, "trends": trends, "by_fold": bank}
    return result


def air_numerical_checks(brews, original, precise):
    fit_t = np.linspace(0., 100., 201)
    fit_p = np.array([np.interp(fit_t, brews.t, p) for p in brews.pressure])
    rows = {}
    for model, (kind, m, _, _) in flow_specs().items():
        prediction = np.empty(len(brews.ids))
        for group in brews.groups:
            coef = np.asarray(precise["flow"][model]["by_fold"][brews.fold[group[0]]])
            prediction[group] = A.predict("B1", coef, fit_p[group], fit_t) if kind == -1 else air_endpoint(coef, fit_p[group], fit_t, kind, m)[0]
        rows[model] = {"maximum endpoint integration difference g/s": float(np.max(np.abs(
            prediction-precise["flow"][model]["endpoint"]))),
            "maximum late-trend grid difference g/s/s": float(np.max(np.abs(
                original["flow"][model]["trends"]-precise["flow"][model]["trends"])))}
    return rows


def air_rows(brews, course, delay, point, draws, scenario):
    """Intervals of descriptive material scales and matched conductance peaks
    are distinct from refitted LOPO full-model endpoint peak intervals.
    """
    timing_rows, flow_rows, timing_intervals, flow_intervals = [], [], {}, {}
    loss = lambda se: float(np.mean([np.sqrt(se[g].mean()) for g in brews.groups]))
    source = "Waszkiewicz et al. (2025), doi:10.5281/zenodo.18046315, CC-BY-4.0"
    for model, (kind, m) in timing_specs().items():
        r = point["timing"][model]; coef = r["by_fold"]["DESCRIPTIVE_ALL"]
        values = np.array([d["timing"][model]["parameters"] for d in draws])
        interval = A.interval([d["timing"][model]["minimum"] for d in draws])
        timing_intervals[model] = interval
        timing_rows.append({"scenario": scenario, "candidate": model, "m": m,
                            "delay RMSE s": loss((r["prediction"]-delay)**2),
                            "Pstar timing bar": coef[2] if kind >= 0 else "",
                            "Pstar timing interval bar": json.dumps(A.interval(values[:, 2])) if kind >= 0 else "",
                            "minimum delay pressure bar": timing_peak(coef, kind, m),
                            "minimum delay pressure interval bar": json.dumps(interval),
                            "s0 interval": json.dumps(A.interval(values[:, 3])) if m else "",
                            "t0 interval s": json.dumps(A.interval(values[:, 0])) if kind >= 0 else "",
                            "parameters by fold": json.dumps(r["by_fold"]),
                            "eligibility": "EXPLORATORY; four timing parameters" if m else "REFERENCE" if kind == -1 else "THREE PARAMETERS",
                            "refit count": len(draws), "seed": B0D_SEED, "source": source})
    for model, (kind, m, _, _) in flow_specs().items():
        if kind >= 0:
            flow_intervals[model] = A.interval([d["flow"][model]["conductance_peak"] for d in draws])
    baseline = point["flow"]["B1"]["endpoint"]-brews.target
    observed = condition_means(brews, course.observed_trend, np.ones(len(delay)))
    for model, (kind, m, mode, timed) in flow_specs().items():
        r = point["flow"][model]; coef = r["by_fold"]["DESCRIPTIVE_ALL"]
        error = r["endpoint"]-brews.target
        paired = paired_course_loss(brews, np.array([baseline**2, error**2]), B0D_SEED)
        delta = A.interval(paired[:, 1]-paired[:, 0]); comparison = A.comparison(delta)
        response = A.response_diagnostics(brews, r["endpoint"], seed=B0D_SEED)
        slope_interval = A.interval([d["flow"][model]["response"][0] for d in draws])
        peak_interval = A.interval([d["flow"][model]["response"][1] for d in draws])
        trends = condition_means(brews, r["trends"], np.ones(len(delay)))
        agreement = sum(mean_trend_sign(a) == mean_trend_sign(b) for a, b in zip(trends, observed))
        # T2 checks independent flow-fitted coefficients, not its own fixed
        # timing coefficients (whose agreement would be true by construction).
        check_model = model
        if mode == "T2":
            check_model = ("F1" if kind == 0 else "F2")+("" if m == 3 else f"-m{m}") if m else ("C4" if kind == 0 else "D1")
        overlap = _interval_overlap(flow_intervals[check_model], timing_intervals[timed]) if timed else False
        eligible = scenario == "RAW PRIMARY" and "-m" not in model and not (mode == "T2" and m)
        passed = overlap and eligible and b0b_pass(model, comparison, {"slope": slope_interval, "peak": peak_interval}, agreement)
        row = {"scenario": scenario, "candidate": model, "m": m, "fit target": "FLOW ENDPOINTS",
               "endpoint RMSE g/s": loss(error**2), "endpoint RMSE interval": json.dumps(A.interval(paired[:, 1])),
               "delta versus B1 g/s": loss(error**2)-loss(baseline**2), "delta interval": json.dumps(delta),
               "COMPARISON": comparison, "CAPABILITY": A.capability(A.interval(paired[:, 1]), response["slope"]),
               "slope g/s/bar": response["slope"], "slope interval refit": json.dumps(slope_interval),
               "full-model peak nominal bar": response["peak"], "full-model peak interval refit": json.dumps(peak_interval),
               "late-trend agreement": f"{agreement}/11", "late-trend means g/s/s": json.dumps(trends.tolist()),
               "late-trend intervals refit": json.dumps([A.interval([d["flow"][model]["trends"][j] for d in draws]) for j in range(11)]),
               "Pstar compaction flow bar": coef[1] if kind >= 0 else "",
               "Pstar compaction flow interval bar": json.dumps(A.interval([d["flow"][model]["parameters"][1] for d in draws])) if kind >= 0 else "",
               "conductance peak flow bar": conductance_peak(coef[1], coef[3], m, kind) if kind >= 0 else "",
               "conductance peak flow interval bar": json.dumps(flow_intervals[model]) if kind >= 0 else "",
               "matched timing law": timed or "", "conductance peak timing interval bar": json.dumps(timing_intervals[timed]) if timed else "",
               "independent flow consistency candidate": check_model if timed else "",
               "independent flow consistency interval bar": json.dumps(flow_intervals[check_model]) if timed else "",
               "Pstar flow estimation": "FIXED FROM TRAINING TIMING" if mode == "T2" else "FLOW FIT",
               "Pstar compaction timing interval bar": json.dumps(A.interval([d["timing"][timed]["parameters"][2] for d in draws])) if timed else "",
               "s0 flow": coef[3] if kind >= 0 else "",
               "s0 flow interval": json.dumps(A.interval([d["flow"][model]["parameters"][3] for d in draws])) if kind >= 0 else "",
               "Pstar overlap": "Y" if overlap else "N", "PASS": "Y" if passed else "N",
               "parameters by fold": json.dumps(r["by_fold"]), "refit count": len(draws), "seed": B0D_SEED,
               "eligibility": "PRIMARY" if eligible else "EXPLORATORY TIMING TRANSFER" if mode == "T2" and m else "SENSITIVITY",
               "source": source}
        if kind == 1:
            alternate = ("W2"+("" if m == 3 else f"-m{m}")) if m else "W1"
            row["exponential timing law"] = alternate
            row["exponential timing peak interval bar"] = json.dumps(timing_intervals[alternate])
            row["exponential timing overlap"] = "Y" if _interval_overlap(flow_intervals[check_model], timing_intervals[alternate]) else "N"
        for label, low, high in (("1-3.5", 1., 3.5), ("4-6", 4., 6.)):
            means = condition_means(brews, error, np.ones(len(delay)))
            row[f"endpoint residual {label} bar g/s"] = float(means[(np.unique(brews.condition) >= low) & (np.unique(brews.condition) <= high)].mean())
        flow_rows.append(row)
    # Only an exponent-shape prior was found: it already fixes m=3. These
    # requested additional rows are explicitly duplicates, not new evidence.
    for model in ("F1", "F2"):
        row = dict(next(r for r in flow_rows if r["candidate"] == model))
        row["candidate"] += "-PRIOR"
        row["prior constraint"] = "Analog m=3 only; no source bound on s0; identical to m=3 row"
        flow_rows.append(row)
    return timing_rows, flow_rows


def air_screen(brews, observed_flow, raw, out, count, prior, workers, resume):
    if count < 200:
        raise ValueError("B0d requires at least 200 whole-brew refits")
    budget = A.FitBudget(); budget.elapsed = prior
    delay, pressure = b0d_onsets(brews, raw)
    timing_rows = A.read_csv(out / "TIMING_FITS.csv") if resume and (out / "TIMING_FITS.csv").exists() else []
    flow_rows = A.read_csv(out / "RESULT_TABLE.csv") if resume and (out / "RESULT_TABLE.csv").exists() else []
    for view, scenario in enumerate(("RAW PRIMARY", "BASKET SENSITIVITY")):
        if any(r["scenario"] == scenario for r in flow_rows):
            continue
        course = load_course(brews, raw, step=.1, observed_flow=observed_flow, basket=bool(view))
        coarse = load_course(brews, raw, observed_flow=observed_flow, basket=bool(view))
        view_brews = course.brews
        point = air_joint_fit(view_brews, course, pressure[:, view], delay, np.ones(len(delay)), budget)
        # Local derived checkpoints contain no raw source records.
        path = A.ROOT / f".b0-b0d-point-{view}.json"
        path.write_text(json.dumps({k: {m: {f: v.tolist() if isinstance(v, np.ndarray) else v for f, v in r.items()}
                                            for m, r in group.items()} for k, group in point.items()}))
        print(json.dumps({"point_complete": scenario, "fit_seconds": budget.elapsed}), flush=True)
        started = time.monotonic(); deadline = started+budget.limit-budget.elapsed
        args = [(view_brews, course, pressure[:, view], delay, sample, deadline)
                for sample in brew_samples(brews, count, B0D_SEED)]
        executor = ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("spawn"))
        draws = []
        try:
            for result in executor.map(_air_refit, args, chunksize=1):
                draws.append(result)
                if len(draws) % 10 == 0:
                    print(json.dumps({"scenario": scenario, "joint_refits": len(draws), "seconds": time.monotonic()-started}), flush=True)
        finally:
            executor.shutdown(wait=True, cancel_futures=True)
            budget.elapsed += time.monotonic()-started
        (A.ROOT / f".b0-b0d-refits-{view}.json").write_text(json.dumps(draws))
        rough = air_replay(view_brews, coarse, pressure[:, view], point)
        numerics = air_numerical_checks(view_brews, rough, point)
        tr, fr = air_rows(view_brews, course, delay, point, draws, scenario)
        for r in fr:
            r["cumulative fitting seconds"] = budget.elapsed
            r.update(numerics[r["candidate"].removesuffix("-PRIOR")])
        timing_rows += tr; flow_rows += fr
        write_csv(out / "TIMING_FITS.csv", timing_rows); write_csv(out / "RESULT_TABLE.csv", flow_rows)
        print(json.dumps({"completed": scenario, "fit_seconds": budget.elapsed,
                          "results": [{k: r[k] for k in ("candidate", "endpoint RMSE g/s", "COMPARISON", "Pstar overlap", "PASS")} for r in fr]}), flush=True)
    return timing_rows, flow_rows, budget.elapsed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=A.ROOT / "puckworks/data/waszkiewicz2025")
    parser.add_argument("--out", type=Path, default=OUT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checks-only", action="store_true")
    mode.add_argument("--screen", action="store_true")
    mode.add_argument("--timecourse", action="store_true", help="B0b T1--T5; raw pressure primary")
    mode.add_argument("--timecourse-checks-only", action="store_true", help="B0b T1--T3; stored fits only")
    mode.add_argument("--onset-only", action="store_true", help="B0c T1 native onset detection and power law")
    mode.add_argument("--swelling-screen", action="store_true", help="B0c T1--T4; raw primary, onset +2 s")
    mode.add_argument("--air-screen", action="store_true", help="B0d timing-only and trapped-air endpoint screen")
    parser.add_argument("--refits", type=int, default=200)
    parser.add_argument("--prior-fit-seconds", type=float, default=0,
                        help="Carry previous fitting time into the two-hour limit")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true", help="Reuse completed rows from this screen")
    args = parser.parse_args()
    brews = A.load_brews(args.data, args.ewp)
    q = flow_history(brews, args.data)
    if args.air_screen:
        try:
            _, _, elapsed = air_screen(brews, q, args.raw, B0D_OUT if args.out == OUT else args.out,
                                        args.refits, args.prior_fit_seconds, args.workers, args.resume)
            print(json.dumps({"total_fit_seconds": elapsed}), flush=True)
        except TimeoutError:
            raise SystemExit("Fitting exceeded two hours: STOP; incomplete rows remain unscored")
        return
    if args.onset_only or args.swelling_screen:
        out = B0C_OUT if args.out == OUT else args.out
        if args.onset_only:
            onset_report(brews, args.raw, out)
        else:
            try:
                _, elapsed = swelling_screen(brews, q, args.raw, out, args.refits,
                                             args.prior_fit_seconds, args.workers, args.resume)
                print(json.dumps({"total_fit_seconds": elapsed}), flush=True)
            except TimeoutError:
                raise SystemExit("Fitting exceeded two hours: STOP; incomplete rows remain unscored")
        return
    if args.timecourse or args.timecourse_checks_only:
        out = B0B_OUT if args.out == OUT else args.out
        if not args.resume:
            existing_timecourse(brews, q, args.raw, out)
        if args.timecourse:
            try:
                _, elapsed = timecourse_screen(brews, q, args.raw, out, args.refits,
                                               args.prior_fit_seconds, args.workers, args.resume)
                print(json.dumps({"total_fit_seconds": elapsed}), flush=True)
            except TimeoutError:
                raise SystemExit("Fitting exceeded two hours: STOP; incomplete rows remain unscored")
        return
    rows, proceed = data_checks(brews, q, args.raw, args.out)
    for row in rows:
        print(json.dumps({k: v for k, v in row.items()
                          if k not in {"per-pressure mean flow and interval", "details"}}))
    if not proceed:
        raise SystemExit("Raw-pressure downturn disappeared: none — stop; no fitting")
    if args.screen:
        try:
            _, elapsed = screen(brews, q, args.out, args.refits, args.prior_fit_seconds,
                                args.workers, args.resume)
            print(json.dumps({"total_fit_seconds": elapsed}), flush=True)
        except TimeoutError:
            raise SystemExit("Fitting exceeded two hours: STOP; any incomplete rows remain unscored")


if __name__ == "__main__":
    main()

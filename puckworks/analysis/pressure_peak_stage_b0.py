"""PRESSURE-PEAK B0: data checks and conditional mechanism screen.

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
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from pathlib import Path

import numpy as np
from scipy.signal import savgol_filter
from scipy.optimize import least_squares

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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--data", type=Path, default=A.ROOT / "puckworks/data/waszkiewicz2025")
    parser.add_argument("--out", type=Path, default=OUT)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--checks-only", action="store_true")
    mode.add_argument("--screen", action="store_true")
    parser.add_argument("--refits", type=int, default=200)
    parser.add_argument("--prior-fit-seconds", type=float, default=0,
                        help="Carry previous fitting time into the two-hour limit")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--resume", action="store_true", help="Reuse completed rows from this screen")
    args = parser.parse_args()
    brews = A.load_brews(args.data, args.ewp)
    q = flow_history(brews, args.data)
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

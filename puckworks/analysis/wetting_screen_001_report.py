"""Report frozen wetting-screen predictions, inherited scores and paired draws.

The resampling and flow bands reproduce EWP e1_demonstration.py at 67bead2;
no optimizer or CFD call occurs here. Intervals condition on all fitted values.
"""
import argparse
import csv
import json
import importlib.metadata
from pathlib import Path
import random
import time

import numpy as np

from . import wetting_screen_001 as W
from . import wetting_screen_001_run as R

CONDITIONAL = "conditional on fitted wetting parameters and transferred form-A tuples"


def package_versions():
    result = {}
    for name in ("numpy", "scipy", "numba", "matplotlib"):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = "not installed"
    return result


def paired_samples(conditions, count=1000, seed=20261103):
    groups = [np.flatnonzero(conditions == p).tolist() for p in W.NOMINAL]
    if any(not group for group in groups):
        raise ValueError("Missing nominal condition; full-cohort score unavailable")
    rng = random.Random(seed)
    samples = []
    for _ in range(count):
        selected = [rng.choice(groups) for _ in groups]
        samples.append([[rng.choice(group) for _ in group] for group in selected])
    return groups, samples


def score_and_draws(squared, groups, samples):
    """Inherited mean of within-condition RMSEs, not pooled RMSE."""
    squared = np.asarray(squared)
    points = np.mean([np.sqrt(squared[:, group].mean(axis=1)) for group in groups], axis=0)
    draws = np.asarray([np.mean([np.sqrt(squared[:, group].mean(axis=1))
                                for group in draw], axis=0) for draw in samples])
    return points, draws


def flow_comparison(interval):
    if interval[1] < 0:
        return "BETTER"
    if interval[0] > 0:
        return "WORSE"
    if interval[0] >= -.25 and interval[1] <= .25:
        return "TIE"
    return "UNRESOLVED"


def onset_grade(value, censored):
    if censored:
        return "MISSES" if value > 4.53 else "NOT_SCORED/unresolved"
    return "MEETS" if value <= 3.51 else "NEAR" if value <= 4.53 else "MISSES"


def quadratic_peak(pressures, flows):
    top = int(np.argmax(flows))
    if top in (0, len(pressures)-1):
        return None
    p = np.asarray(pressures)[top-1:top+2]
    a, b, _ = np.polyfit(p, np.asarray(flows)[top-1:top+2], 2)
    vertex = -b/(2*a) if a < 0 else np.nan
    return float(vertex) if p[0] <= vertex <= p[-1] else None


def response(values, end_pressure, conditions):
    """Inherited nominal peak and 9/11/13 condition-mean regression."""
    rng = np.random.default_rng(R.SEED)
    means, pmeans, draws, pdraws = [], [], [], []
    for pressure in W.NOMINAL:
        group = np.flatnonzero(conditions == pressure)
        picks = rng.choice(group, (R.RESAMPLES, len(group)), replace=True)
        means.append(values[group].mean())
        pmeans.append(end_pressure[group].mean())
        draws.append(values[picks].mean(axis=1))
        pdraws.append(end_pressure[picks].mean(axis=1))
    y, x = np.asarray(means), np.asarray(pmeans)
    yb, xb = np.asarray(draws).T, np.asarray(pdraws).T
    high = W.NOMINAL >= 9
    def slope(p, q):
        return float(np.dot(p-p.mean(), q-q.mean())/np.dot(p-p.mean(), p-p.mean()))
    slopes = np.array([slope(p[high], q[high]) for p, q in zip(xb, yb)])
    peaks = W.NOMINAL[np.argmax(yb, axis=1)]
    pi = np.quantile(peaks, [.025, .975]).tolist()
    si = np.quantile(slopes, [.025, .975]).tolist()
    pg = "MEETS" if pi[0] <= 7 and pi[1] >= 5 else (
        "NEAR" if any(pi[0] <= p <= pi[1] for p in (4, 8)) else "MISSES")
    sg = ("MISSES" if si[1] >= 0 else "MEETS" if si[0] <= -.0403 and si[1] >= -.0880
          else "NEAR" if si[0] >= -.176 and si[1] <= -.020 else "MISSES")
    return dict(slope_g_s_bar=slope(x[high], y[high]), slope_interval=si,
                nominal_peak_bar=float(W.NOMINAL[np.argmax(y)]), nominal_peak_interval=pi,
                nominal_peak_grade=pg, slope_grade=sg, endpoint_condition_means=y.tolist(),
                endpoint_condition_intervals=np.quantile(yb, [.025, .975], axis=0).T.tolist())


def load_frozen(args):
    sources, bank, contexts, native_manifest = R.load_data(args)
    rows = []
    for path in sorted((args.work/"predictions").glob("*.json")):
        row = json.loads(path.read_text())
        if row["identity"]["predictor_sha256"] != R.digest(Path(W.__file__)):
            raise ValueError("Frozen predictor changed")
        if row["identity"]["protocol_sha256"] != R.digest(R.ROOT/"docs/research/WETTING_SCREEN_001/PLAN.md"):
            raise ValueError("Frozen protocol changed")
        if row["identity"]["fit_sha256"]:
            label = "DESCRIPTIVE_ALL" if row["scope"] == "descriptive" else f"HYD-LOCO-{row['pressure_bar']:.1f}"
            if R.digest(args.work/"fits"/(label+"_"+row["arm"]+".json")) != row["identity"]["fit_sha256"]:
                raise ValueError("Frozen fitted parameters changed")
        for label in ("fine", "search"):
            artifact = row[label]["prediction"]
            if R.digest(args.work/"predictions"/artifact["file"]) != artifact["sha256"]:
                raise ValueError("Frozen prediction changed")
        rows.append(row)
    intended = {(scope, arm): 56 if scope == "held_out" else 23
                for scope in ("held_out", "descriptive") for arm in args.arms}
    actual = {key: sum(r["scope"] == key[0] and r["arm"] == key[1] for r in rows) for key in intended}
    R.write_json(args.work/"COVERAGE.json", dict(intended={str(k): v for k, v in intended.items()},
        available={str(k): v for k, v in actual.items()}))
    if actual != intended:
        raise ValueError("Incomplete predictions; coverage written, full-cohort comparison unavailable")
    return sources, bank, contexts, native_manifest, [r for r in rows if r["arm"] in args.arms]


def hydraulic_errors(sources, endpoints, traces):
    target = np.asarray([r["observed_endpoint_g_s"] for r in sources])
    squared = {"endpoint": (np.asarray(endpoints)-target)**2, "primary_trace": [], "companion_trace": []}
    for source, q in zip(sources, traces):
        error = (np.asarray(q)-source["observed_trace_g_s"])**2
        squared["primary_trace"].append(error[np.asarray(source["trace_mask"], dtype=bool)].mean())
        squared["companion_trace"].append(error[np.asarray(source["trace_times_s"]) >= 5.].mean())
    return {k: np.asarray(v) for k, v in squared.items()}


def metrics(sources, rows, arms, numerical="fine"):
    conditions = np.array([r["nominal_pressure_bar"] for r in sources])
    pressure_end = np.array([r["pressure_bar"][-1] for r in sources])
    groups, samples = paired_samples(conditions)
    observed = np.array([r["observed_onset_for_scoring_only_s"] for r in sources])
    all_errors, data, reports = {}, {}, {}
    for arm in arms:
        by_brew = {r["brew"]: r for r in rows if r["arm"] == arm and r["scope"] == "held_out"}
        selected = [by_brew[s["brew"]] for s in sources]
        predictions = [r[numerical] for r in selected]
        observers = [p["observer"] for p in predictions]
        endpoints = np.array([p["endpoint_g_s"] for p in predictions])
        traces = [p["trace_g_s"] for p in predictions]
        errors = hydraulic_errors(sources, endpoints, traces)
        errors["onset"] = np.array([W.squared_onset(o, y) for o, y in zip(observers, observed)])
        all_errors[arm] = errors
        data[arm] = dict(rows=selected, observers=observers, endpoints=endpoints, traces=traces)
        censored = sum(not o["detected"] for o in observers)
        censor_squared = np.array([e if not o["detected"] else 0.
                                   for e, o in zip(errors["onset"], observers)])
        reports[arm] = dict(arm=arm, scope="ordinary held-out; 56/56 available", detected=56-censored,
            role={"W0": "reference", "Z": "zero-delay diagnostic; not a candidate",
                  "W1": "phenomenological constant-delay null", "W2": "primary two-parameter candidate",
                  "W2T": "predeclared three-parameter observation diagnostic"}[arm],
            intended=56, available=56, censored=censored, onset_is_lower_bound=bool(censored),
            censor_contributions_alone_rmse_bound_s=float(np.mean([
                np.sqrt(censor_squared[group].mean()) for group in groups])),
            interval_scope=CONDITIONAL, **response(endpoints, pressure_end, conditions))
        for pressure in (1., 2., 3.5):
            g = conditions == pressure
            reports[arm][f"residual_{pressure:g}_bar_g_s"] = float(np.mean(
                endpoints[g]-np.array([s["observed_endpoint_g_s"] for s in sources])[g]))
    b1 = hydraulic_errors(sources, [s["b1_endpoint_g_s"] for s in sources],
                          [s["b1_trace_g_s"] for s in sources])
    paired = []
    for name in ("onset", "endpoint", "primary_trace", "companion_trace"):
        labels = list(arms) if name == "onset" else [*arms, "B1"]
        errors = np.array([all_errors[a][name] if a != "B1" else b1[name] for a in labels])
        points, draws = score_and_draws(errors, groups, samples)
        for i, arm in enumerate(arms):
            reports[arm][name+"_rmse"] = float(points[i])
            reports[arm][name+"_interval"] = np.quantile(draws[:, i], [.025, .975]).tolist()
        for left, right in [(a, "W0") for a in arms if a != "W0"] + (
                [("W2T", "W2")] if "W2T" in arms else []):
            li, ri = labels.index(left), labels.index(right)
            interval = np.quantile(draws[:, li]-draws[:, ri], [.025, .975]).tolist()
            bound_difference = name == "onset" and (reports[left]["censored"] or reports[right]["censored"])
            paired.append(dict(left=left, right=right, metric=name, scope="ordinary held-out",
                left_score=float(points[li]), right_score=float(points[ri]),
                difference=float(points[li]-points[ri]), lower_95=interval[0], upper_95=interval[1],
                interpretation="difference of computed RMSE bounds; not a bound on their difference" if bound_difference
                    else "paired RMSE difference", interval_scope=CONDITIONAL,
                resampling="1000 identical condition-then-whole-brew draws; seed 20261103"))
        if name != "onset":
            for i, arm in enumerate(arms):
                interval = np.quantile(draws[:, i]-draws[:, -1], [.025, .975]).tolist()
                reports[arm]["b1_"+name+"_rmse"] = float(points[-1])
                reports[arm][name+"_minus_b1_interval"] = interval
                if name == "endpoint":
                    comparison = flow_comparison(interval)
                    reports[arm]["accuracy_comparison_vs_b1"] = comparison
                    reports[arm]["accuracy_grade_vs_b1"] = "MEETS" if comparison in ("BETTER", "TIE") else (
                        "NEAR" if comparison == "UNRESOLVED" and points[i] < points[-1] else "MISSES")
    for arm in arms:
        reports[arm]["onset_grade"] = onset_grade(reports[arm]["onset_rmse"], reports[arm]["censored"])
        if arm == "Z":
            for key in ("onset_grade", "accuracy_grade_vs_b1", "nominal_peak_grade", "slope_grade"):
                reports[arm][key] = "NOT_SCORED/diagnostic"
    return reports, paired, data, samples


def onset_tables(sources, data, arms):
    brew_rows, condition_rows = [], []
    for arm in arms:
        for source, row, observer in zip(sources, data[arm]["rows"], data[arm]["observers"]):
            observed = source["observed_onset_for_scoring_only_s"]
            detected = observer["detected"]
            brew_rows.append(dict(arm=arm, brew=source["brew"], pressure_bar=source["nominal_pressure_bar"],
                observed_onset_s=observed, predicted_onset_s=observer["onset_s"], detected=detected,
                signed_error_s=observer["onset_s"]-observed if detected else None,
                signed_error_lower_bound_s=observer["censor_bound_s"]-observed if not detected else None,
                front_s=row["fine"]["prediction"]["front_s"],
                front_censored_at_100=row["fine"]["prediction"]["front_right_censored"],
                censor_bound_s=observer["censor_bound_s"], samples=observer["samples"],
                last_observation_s=observer["last_timestamp_s"],
                native_qualification_failed=row["native_qualification_failed"],
                squared_loss_s2=W.squared_onset(observer, observed)))
        for pressure in W.NOMINAL:
            group = [r for r in brew_rows if r["arm"] == arm and r["pressure_bar"] == pressure]
            exact, lower = W.median_with_censor([r["predicted_onset_s"] for r in group],
                                               [r["censor_bound_s"] for r in group])
            observed = float(np.median([r["observed_onset_s"] for r in group]))
            front, fbound = W.median_with_censor([r["front_s"] for r in group], [100.]*len(group))
            condition_rows.append(dict(arm=arm, pressure_bar=float(pressure), intended=len(group),
                available=len(group), detected=sum(r["detected"] for r in group),
                observed_median_s=observed, predicted_median_s=exact, median_lower_bound_s=lower,
                signed_median_error_s=exact-observed if exact is not None else None,
                signed_median_error_lower_bound_s=lower-observed if exact is None else None,
                front_median_s=front, front_median_lower_bound_s=fbound,
                censor_bound_min_s=min(r["censor_bound_s"] for r in group),
                censor_bound_max_s=max(r["censor_bound_s"] for r in group)))
    return brew_rows, condition_rows


def extrema(rows, condition_rows, arms):
    sweep, extrema_rows = [], []
    for arm in arms:
        selected = sorted([r for r in rows if r["arm"] == arm and r["scope"] == "descriptive"],
                          key=lambda r: r["pressure_bar"])
        for row in selected:
            p = row["fine"]
            sweep.append(dict(arm=arm, pressure_bar=row["pressure_bar"],
                scope="DESCRIPTIVE_ALL; one common tuple, forcing and 100-s horizon",
                front_s=p["prediction"]["front_s"], front_censored_at_100=p["prediction"]["front_right_censored"],
                detector_onset_s=p["observer"]["onset_s"], detected=p["observer"]["detected"],
                censor_bound_s=p["observer"]["censor_bound_s"], endpoint_scale_liquid_flow_g_s=p["endpoint_g_s"],
                endpoint_unshifted_bed_flow_g_s=p["unshifted_endpoint_g_s"],
                lag_s=row["lag_s"]))
        p = np.array([r["pressure_bar"] for r in selected])
        q = np.array([r["fine"]["endpoint_g_s"] for r in selected])
        detector = [r["fine"]["observer"] for r in selected]
        onset = np.array([o["onset_s"] if o["detected"] else np.inf for o in detector])
        shortest = float(min(onset))
        tied = np.flatnonzero(onset == shortest)
        identifiable = bool(np.isfinite(shortest) and all(o["detected"] or o["censor_bound_s"] > shortest for o in detector))
        held = [r for r in condition_rows if r["arm"] == arm]
        held_min = min((r["predicted_median_s"] for r in held if r["predicted_median_s"] is not None), default=np.inf)
        held_identified = bool(np.isfinite(held_min) and all(r["predicted_median_s"] is not None or
                              r["median_lower_bound_s"] > held_min for r in held))
        extrema_rows.append(dict(arm=arm, descriptive_detector_minimum_s=shortest if identifiable else None,
            descriptive_detector_minimum_pressures_bar=p[tied].tolist() if identifiable else [],
            detector_minimum_status=("unidentified" if not identifiable else
                "boundary minimum at tested sweep edge" if 0 in tied or len(p)-1 in tied else "grid-resolved minimum"),
            held_out_fastest_nominal_conditions_bar=[r["pressure_bar"] for r in held
                if r["predicted_median_s"] == held_min] if held_identified else [],
            held_out_detector_minimum_status="identified at nominal resolution" if held_identified else "unidentified",
            finite_100s_scale_flow_peak_bar=quadratic_peak(p, q),
            finite_100s_scale_flow_nominal_grid_peak_bar=float(p[np.argmax(q)]),
            flow_peak_status="three-point quadratic interpolation of retained 23-pressure sweep; no statistical interval",
            w0_native_reference_bar=6.009,
            capacity_peak_bar=6.00, capacity_peak_refit_interval_bar=[5.77, 6.27],
            capacity_interval_scope="D0 parameter-refit capacity peak; distinct from finite-time/interpolation or conditional resamples"))
    return sweep, extrema_rows


def verification_tables(args):
    verification = json.loads((args.work/"VERIFICATION.json").read_text())
    _, _, contexts, _ = R.load_data(args)
    rows = []
    for row in verification["rows"]:
        flat = {k: v for k, v in row.items() if not isinstance(v, dict)}
        flat.update(native_detector_onset_s=row["native_onset"]["onset_s"],
                    native_detected=row["native_onset"]["detected"],
                    native_censor_bound_s=row["native_onset"]["censor_bound_s"])
        for label in ("native_scheme", "screen_scheme"):
            flat.update({label+"_"+k: v for k, v in row[label].items() if not isinstance(v, dict)})
            flat[label+"_detected"] = row[label]["detector"]["detected"]
            flat[label+"_detector_onset_s"] = row[label]["detector"]["onset_s"]
        if row["arm"] == "A1":
            key = ("held_out_W0_"+row["brew"] if row["brew"] else
                   f"descriptive_W0_constant-{row['pressure_bar']:g}")
            item = json.loads((args.work/"predictions"/(key+".json")).read_text())
            native = args.native/row["run"]/"postProcessing/wholePull/0/traces.csv"
            if R.digest(native) != row["native_trace_sha256"]:
                raise ValueError("Native verification trace changed")
            with native.open() as stream:
                header = next(csv.reader(stream))
            names = ["time_s", "cup_water_mass_kg", "cup_beverage_mass_kg", "outlet_flow_m3_s"]
            a = np.loadtxt(native, delimiter=",", skiprows=1, usecols=[header.index(k) for k in names]).T
            t = np.r_[0., a[0]]
            observation = contexts[row["brew"]] if row["brew"] else t[::20][t[::20] <= 100.]
            observation = observation[observation <= t[-1]]
            with np.load(args.work/"predictions"/item["fine"]["prediction"]["file"]) as prediction:
                if a[0][0] < prediction["time"][0] or a[0][-1] > prediction["time"][-1]:
                    raise ValueError("Fine verification coverage unavailable; no terminal extension")
                detector = W.observe(prediction, observation)
                flat.update(
                    fine_liquid_max_difference_g=float(np.max(np.abs(np.interp(a[0], prediction["time"], prediction["liquid_g"])-1000*a[1]))),
                    fine_beverage_max_difference_g=float(np.max(np.abs(np.interp(a[0], prediction["time"], prediction["beverage_g"])-1000*a[2]))),
                    fine_endpoint_flow_difference_g_s=float(np.interp(a[0][-1], prediction["time"], prediction["bed_flow_g_s"])-965000*a[3][-1]),
                    fine_detected=detector["detected"], fine_detector_onset_s=detector["onset_s"],
                    fine_detection_agrees=detector["detected"] == row["native_onset"]["detected"],
                    fine_onset_difference_s=detector["onset_s"]-row["native_onset"]["onset_s"] if
                        detector["detected"] and row["native_onset"]["detected"] else None,
                    fine_comparison_support="retained native/source common support; full-contract availability separately flagged")
        rows.append(flat)
    R.csv_write(R.OUT/"VERIFICATION.csv", rows)
    return verification


def fit_table(args):
    fits, rows = [], []
    for path in sorted((args.work/"fits").glob("*.json")):
        fit = json.loads(path.read_text())
        fits.append((path, fit))
        p = fit["parameters"]
        names = ["tau0"] if fit["arm"] == "W1" else ["k_w0", "Pw"]+(["t_s"] if fit["arm"] == "W2T" else [])
        rows.append(dict(arm=fit["arm"], fold=fit["fold"],
            frozen_form_a_tuple_a_Pstar_n_Pd_Mc=fit["theta_for_every_training_and_held_brew"],
            tau0_s=p[0] if fit["arm"] == "W1" else None,
            k_w0_m2=p[0] if fit["arm"] != "W1" else None,
            fitted_wetting_pressure_scale_bar=p[1] if fit["arm"] != "W1" else None,
            observation_lag_s=p[2] if fit["arm"] == "W2T" else None,
            loss_s2=fit["loss_s2"], training_brews=len(fit["training_brews"]),
            sampled_exact_minimum_count=fit["sampled_exact_minimum_count"],
            distinct_sampled_exact_minima=len({tuple(r["parameters"]) for r in fit["trials"] if r["loss_s2"] == fit["loss_s2"]}),
            equal_minimum_parameter_ranges=fit["sampled_minimum_parameter_ranges"],
            transformed_coordinate_distance_to_bounds=fit["coordinate_distance_to_bounds"],
            exact_boundary_parameters=[name for name, distance in zip(names, fit["coordinate_distance_to_bounds"]) if distance == 0.],
            parameters_unidentified_within_sampled_equal_minima=[name for name, bounds in
                zip(names, fit["sampled_minimum_parameter_ranges"]) if bounds[0] != bounds[1]],
            minimum_detected_training=min(r["detected_training"] for r in fit["trials"] if r["loss_s2"] == fit["loss_s2"]),
            trials=len(fit["trials"]), column_evaluations=fit["column_evaluations"],
            powell_successful_starts=sum(r["success"] for r in fit["optimizer_results"]),
            powell_start_count=len(fit["optimizer_results"]),
            powell_messages=sorted({r["message"] for r in fit["optimizer_results"]}),
            cpu_hours=fit["cpu_seconds"]/3600., fit_sha256=R.digest(path),
            identifiability=fit["identifiability"]))
    R.csv_write(R.OUT/"FITS.csv", rows)
    return fits


def figures(sources, data, conditions, sweep, arms):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "PW-WETTING-SCREEN-001"
    import matplotlib.pyplot as plt
    palette = dict(W0="#4c566a", Z="#9a6700", W1="#805ad5", W2="#007f5f", W2T="#c2410c")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), layout="constrained")
    for panel in (0, 1):
        keep = lambda r: (r["pressure_bar"] <= 2.) == (panel == 0)
        for arm in arms:
            rows = [r for r in conditions if r["arm"] == arm and keep(r)]
            p = np.array([r["pressure_bar"] for r in rows])
            err = np.array([r["signed_median_error_s"] if r["signed_median_error_s"] is not None else
                            r["signed_median_error_lower_bound_s"] for r in rows])
            axes[panel, 0].plot(p, err, "o-", color=palette[arm], label=arm, markersize=4)
            censored = np.array([r["predicted_median_s"] is None for r in rows])
            axes[panel, 0].scatter(p[censored], err[censored], marker="$↑$", s=170, color=palette[arm])
            constants = [r for r in sweep if r["arm"] == arm and keep(r)]
            q = [r["detector_onset_s"] if r["detected"] else r["censor_bound_s"] for r in constants]
            axes[panel, 1].plot([r["pressure_bar"] for r in constants], q, ".-", color=palette[arm], label=arm)
            for r in constants:
                if not r["detected"]:
                    axes[panel, 1].scatter([r["pressure_bar"]], [r["censor_bound_s"]], marker="$↑$", s=100, color=palette[arm])
        axes[panel, 0].axhline(0, color="black", linewidth=.7)
        axes[panel, 0].set(ylabel="Predicted − observed median (s)")
        axes[panel, 1].set(ylabel="Detector onset (s)")
        ticks = W.NOMINAL[W.NOMINAL <= 2.] if panel == 0 else W.NOMINAL[W.NOMINAL > 2.]
        for ax in axes[panel]:
            ax.set(xlabel="Nominal pressure (bar)", xticks=ticks)
            ax.tick_params(axis="x", labelsize=8)
            ax.grid(alpha=.2)
    axes[0, 0].set_title("Held-out signed detector-median errors")
    axes[0, 1].set_title("Descriptive constant-pressure detector")
    axes[0, 0].legend(ncol=3, fontsize=9)
    fig.suptitle("Beverage-mass B0c observer · all 11 conditions · arrows denote lower bounds", fontsize=12)
    fig.savefig(R.OUT/"ONSET.svg", metadata={"Date": None})
    fig.savefig(R.OUT/"ONSET.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    observed = [np.mean([s["observed_endpoint_g_s"] for s in sources if s["nominal_pressure_bar"] == p]) for p in W.NOMINAL]
    axes[0].plot(W.NOMINAL, observed, "ko", label="Observed beverage flow")
    for arm in arms:
        mean = [np.mean([q for s, q in zip(sources, data[arm]["endpoints"]) if s["nominal_pressure_bar"] == p]) for p in W.NOMINAL]
        axes[0].plot(W.NOMINAL, mean, "o-", color=palette[arm], label=arm, markersize=3)
        constants = [r for r in sweep if r["arm"] == arm]
        axes[1].plot([r["pressure_bar"] for r in constants], [r["endpoint_scale_liquid_flow_g_s"] for r in constants],
                     ".-", color=palette[arm], label=arm)
    axes[0].set(title="Held-out endpoint condition means")
    axes[1].set(title="Descriptive 100-s endpoint sweep")
    for ax in axes:
        ax.set(xlabel="Nominal pressure (bar)", ylabel="Endpoint flow (g/s)")
        ax.grid(alpha=.2)
    axes[0].legend(fontsize=8, ncol=2)
    fig.suptitle("Frozen form A · scored liquid ρQ · W2T includes the observation lag", fontsize=12)
    fig.savefig(R.OUT/"FLOW.svg", metadata={"Date": None})
    fig.savefig(R.OUT/"FLOW.png", dpi=180)
    plt.close(fig)


def report(args):
    start, cpu = time.perf_counter(), time.process_time()
    sources, bank, contexts, native_manifest, rows = load_frozen(args)
    reports, paired, data, samples = metrics(sources, rows, args.arms)
    coarse, _, _, _ = metrics(sources, rows, args.arms, numerical="search")
    brew_rows, conditions = onset_tables(sources, data, args.arms)
    sweep, extremes = extrema(rows, conditions, args.arms)
    R.csv_write(R.OUT/"GRADES.csv", list(reports.values()))
    R.csv_write(R.OUT/"PAIRED_COMPARISONS.csv", paired)
    R.csv_write(R.OUT/"ONSET_BY_BREW.csv", brew_rows)
    R.csv_write(R.OUT/"ONSET_BY_PRESSURE.csv", conditions)
    R.csv_write(R.OUT/"DESCRIPTIVE_SWEEP.csv", sweep)
    R.csv_write(R.OUT/"EXTREMA.csv", extremes)
    R.csv_write(R.OUT/"Z_LOW_PRESSURE.csv", [r for r in brew_rows if r["arm"] == "Z" and r["pressure_bar"] <= 2])
    R.csv_write(R.OUT/"NUMERICAL_CHECKS.csv", [dict(key=r["key"], **r["numerical_comparison"]) for r in rows])
    R.csv_write(R.OUT/"NUMERICAL_SCORES.csv", [dict(arm=arm, metric=metric,
        search_step_score=coarse[arm][metric+"_rmse"], fine_step_score=reports[arm][metric+"_rmse"],
        fine_minus_search=reports[arm][metric+"_rmse"]-coarse[arm][metric+"_rmse"])
        for arm in args.arms for metric in ("onset", "endpoint", "primary_trace", "companion_trace")])
    hydraulic = []
    for arm in args.arms:
        for source, row in zip(sources, data[arm]["rows"]):
            p = row["fine"]
            hydraulic.append(dict(arm=arm, brew=source["brew"], pressure_bar=source["nominal_pressure_bar"],
                predicted_endpoint_g_s=p["endpoint_g_s"], observed_endpoint_g_s=source["observed_endpoint_g_s"],
                endpoint_residual_g_s=p["endpoint_g_s"]-source["observed_endpoint_g_s"],
                unshifted_bed_endpoint_g_s=p["unshifted_endpoint_g_s"],
                endpoint_beverage_minus_liquid_flow_g_s=p["endpoint_beverage_minus_liquid_flow_g_s"],
                scored_basis="scale liquid rhoQ; observed flow is scale-derived beverage flow",
                diagnostic_basis="beverage-minus-liquid is ungraded"))
    R.csv_write(R.OUT/"FLOW_BY_BREW.csv", hydraulic)
    if "W2T" in args.arms:
        unshifted = data["W2T"]["rows"]
        errors = hydraulic_errors(sources, [r["fine"]["unshifted_endpoint_g_s"] for r in unshifted],
                                  [r["fine"]["unshifted_trace_g_s"] for r in unshifted])
        groups, samples = paired_samples(np.array([r["nominal_pressure_bar"] for r in sources]))
        diagnostic = []
        for name, error in errors.items():
            points, draws = score_and_draws([error], groups, samples)
            diagnostic.append(dict(arm="W2T", metric=name, unshifted_bed_rmse=float(points[0]),
                shifted_scored_rmse=reports["W2T"][name+"_rmse"],
                disposition="ungraded unshifted-bed diagnostic; scored prediction uses observation lag"))
        R.csv_write(R.OUT/"W2T_BED_DIAGNOSTIC.csv", diagnostic)
    verification = verification_tables(args)
    fits = fit_table(args)
    if set(args.arms) == set(W.ARMS) and len(fits) != 36:
        raise ValueError("Expected exactly 36 fitted families")
    details = dict(reports=reports, paired=paired, extrema=extremes,
                   verification=verification, conditions=conditions,
                   descriptive_fits={f["arm"]: f["parameters"] for _, f in fits if f["fold"] == "DESCRIPTIVE_ALL"})
    R.write_json(args.work/"REPORT.json", details)
    figures(sources, data, conditions, sweep, args.arms)
    draw_path = args.work/"PAIRED_RESAMPLES.json"
    R.write_json(draw_path, samples)
    manifest = dict(task="PW-WETTING-SCREEN-001", scope="G1 retrospective target-exposed screen; no production component",
        interval_scope=CONDITIONAL, arms=args.arms, intended_brews=56, available_brews=56,
        expected_primary_predictions=395, completed_primary_predictions=len(rows),
        fitted_families=len(fits), prediction_basis="fixed 1D R0; fits at 0.02 s, frozen scoring at 0.005 s; 256 cells",
        r0_engineering_assumptions="0.15/s release, 180 kg/m3 capacity, 1e-9 m2/s diffusivity, 5.6-g extractable inventory",
        observation_support="fixed original timestamps in 0–100 s; no missing-coverage censor shortening or terminal mass extension",
        native_full_contract_roundoff_limitation=[r["run"] for r in verification["rows"] if not r["native_full_contract_comparison_available"]],
        native_verification_support="Original timestamps on retained native support, determined before model evaluation; full-contract limitation separately unavailable",
        source_inputs_sha256=R.digest(args.native/"source_inputs.json"),
        d0_fits_sha256=R.digest(R.ROOT/"docs/research/PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv"),
        native_ewp_commit="67bead2a25bd7e61c16c4fe2c104d885d8d26dd9",
        native_manifest_sha256=R.digest(args.ewp/"docs/demonstrations/FORM_A/RUN_MANIFEST.json"),
        original_sources=[dict(brew=s["brew"], sha256=s["original_sha256"]) for s in sources],
        resamples=1000, seed=20261103, resample_sha256=R.digest(draw_path),
        native_qualification_failed_brews=[r["brew"] for r in native_manifest["runs"] if
                "primary A1" in r["roles"] and r.get("brew") and not r["balances_and_bounds_qualified"]],
        core_hours=dict(fitting=sum(f["cpu_seconds"] for _, f in fits)/3600.,
                        verification=verification["cpu_seconds"]/3600.,
                        frozen_predictions_and_refinement=sum(r["cpu_seconds"] for r in rows)/3600.,
                        reporting=(time.process_time()-cpu)/3600.),
        fits=[dict(file=p.name, sha256=R.digest(p), cpu_seconds=f["cpu_seconds"],
                   column_evaluations=f["column_evaluations"]) for p, f in fits],
        predictions=[dict(key=r["key"], metadata_sha256=R.digest(args.work/"predictions"/(r["key"]+".json")),
                          cpu_seconds=r["cpu_seconds"], fine=r["fine"]["prediction"], search=r["search"]["prediction"])
                     for r in rows],
        code_sha256={p.name: R.digest(p) for p in (R.ROOT/"puckworks/analysis").glob("wetting_screen_001*.py")},
        package_versions=package_versions(),
        external_evidence_directory=str(args.work), no_cfd_executions=True,
        metering_scope="Process CPU seconds for 36 fits, successful native verification, frozen prediction/refinement and reporting; excludes development/QA and unmetered failed setup attempts retained in external logs",
        setup_logs=[dict(file=p.name, sha256=R.digest(p), disposition="retained setup attempt; CPU time not metered")
                    for p in sorted(args.work.glob("pre-verification-*.log"))],
        reporting_wall_seconds=time.perf_counter()-start)
    manifest["core_hours"]["total_recorded"] = sum(manifest["core_hours"].values())
    R.write_json(R.OUT/"RUN_MANIFEST.json", manifest)
    print(json.dumps({k: {name: v[name] for name in ("onset_rmse", "detected", "endpoint_rmse", "primary_trace_rmse")}
                      for k, v in reports.items()}, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp", "native", "raw", "work"):
        parser.add_argument("--"+flag, type=Path, required=True)
    parser.add_argument("--arms", nargs="+", choices=W.ARMS, default=list(W.ARMS))
    parser.add_argument("--output", type=Path, default=R.OUT)
    args = parser.parse_args()
    R.OUT = args.output
    R.OUT.mkdir(parents=True, exist_ok=True)
    report(args)


if __name__ == "__main__":
    main()

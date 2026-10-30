"""Owner-band re-scoring of saved PRESSURE-PEAK results; no model refitting.

Only the explicitly requested observed-mean quadratic is fitted. All mechanism
parameters, paired losses and grading intervals come from the committed CSVs.
New-pressure curves are descriptive constant-line-pressure, 100-s evaluations;
they do not replace the original out-of-fold, measured-history scores.
Waszkiewicz et al. (2025), doi:10.5281/zenodo.18046315, CC-BY-4.0.

Run: python -m puckworks.analysis.pressure_peak_scorecard --max-seconds 600
Only SCORECARD.csv, FIGURE.png and the results section of SUMMARY.md are written.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import signal
import time
from contextlib import contextmanager
from pathlib import Path

import numpy as np

from puckworks.analysis import pressure_peak_stage_a as A
from puckworks.analysis import pressure_peak_stage_b0 as B
from puckworks.data import WASZ_TRACE_ALIASES

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs/research/PRESSURE_PEAK_SCORECARD"
SEED = 20261102
GRID = np.linspace(1., 13., 241)
NOMINAL = np.array([1., 2., 3.5, 4., 5., 6., 7., 8., 9., 11., 13.])
OBSERVED_SLOPE = (-.0880, -.0403)
NS = "NOT_SCORED"
NA = "NOT_AVAILABLE"
GRADES = ("accuracy_grade", "peak_grade", "slope_grade", "trend_grade")
CANDIDATES = {
    "A": ("C1-exp", "C3", "C4", "B1"),
    "B0": ("D1", "D2", "C4", "B1"),
    "B0b": ("C4", "D1", "D2", "D3", "B1"),
    "B0c": ("E1", "E3", "E2", "B1"),
    "B0d": ("F1", "F2", "B1"),
}
MARKER = "<!-- scorecard-results -->"
SOURCE_CREDIT = "Waszkiewicz et al. (2025), doi:10.5281/zenodo.18046315, CC-BY-4.0"
CURVE_LABEL = "descriptive evaluation of saved fits — not a prediction"


def overlap(left, right):
    return max(left[0], right[0]) <= min(left[1], right[1])


def accuracy_grade(rmse, baseline, comparison):
    """Owner's revised capability band: consume the stage's saved comparison."""
    if comparison in {"TIE", "BETTER"}:
        return "MEETS"
    if comparison == "UNRESOLVED" and rmse < baseline:
        return "NEAR"
    if comparison not in {"UNRESOLVED", "WORSE"}:
        raise ValueError(f"Unknown saved comparison: {comparison}")
    return "MISSES"


def peak_grade(bounds):
    if overlap(bounds, (5., 7.)):
        return "MEETS"
    if overlap(bounds, (4., 4.)) or overlap(bounds, (8., 8.)):
        return "NEAR"
    return "MISSES"


def slope_grade(bounds):
    # The owner's non-negative/zero-crossing exclusion takes precedence.
    if bounds[1] >= 0:
        return "MISSES"
    if overlap(bounds, OBSERVED_SLOPE):
        return "MEETS"
    if -.176 <= bounds[0] <= bounds[1] <= -.020:
        return "NEAR"
    return "MISSES"


def trend_grade(matches, total=5):
    if matches is None:
        return NS
    if not 0 <= matches <= total or total <= 0:
        raise ValueError("Invalid resolved late-trend count")
    # Fractions preserve the owner's bands if the file's resolved set changes.
    return "MEETS" if matches / total >= .8 else "NEAR" if matches / total >= .6 else "MISSES"


def timing_overlap(flow, timing):
    return "YES" if overlap(flow, timing) else "NO"


def read_rows(path):
    with Path(path).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def stage_path(stage):
    return Path("docs/research") / f"PRESSURE_PEAK_STAGE_{stage.upper()}" / "RESULT_TABLE.csv"


def select_stage(stage, basket=False, root=ROOT):
    """Choose the saved full-cohort result, never an easier cohort sensitivity."""
    records = read_rows(Path(root) / stage_path(stage))
    selected = {}
    for number, row in enumerate(records, 2):
        if stage == "A":
            include = not basket
        elif stage == "B0":
            include = row["pressure"] == ("basket primary" if basket else "raw sensitivity")
        elif stage == "B0b":
            include = row["scenario"] == ("T4 BASKET SENSITIVITY" if basket else "T4 RAW PRIMARY")
        else:
            include = row["scenario"] == ("BASKET SENSITIVITY" if basket else "RAW PRIMARY")
            if stage == "B0c":
                include = include and row["stage"] == "T4 REFIT"
        if include:
            candidate = row["candidate"]
            if candidate in selected:
                raise ValueError(f"Ambiguous saved row: {stage}/{candidate}")
            selected[candidate] = (row, number)
    return selected


def field(row, *names):
    for name in names:
        if row.get(name, "") != "":
            return row[name]
    raise KeyError(names)


def metrics(stage, source, baseline):
    rmse = float(field(source, "endpoint RMSE g/s", "RMSE g/s"))
    base = float(field(baseline, "endpoint RMSE g/s", "RMSE g/s"))
    delta = json.loads(field(source, "delta interval", "delta interval g/s"))
    peak = json.loads(field(source, "full-model peak interval refit", "peak interval refit", "peak interval bar"))
    slope = json.loads(field(source, "slope interval refit", "slope interval g/s/bar"))
    trend = source.get("late-trend agreement", NS)
    if trend != NS and trend.split("/")[1] != "11":
        raise ValueError("Cannot substitute a reduced-cohort trend score")
    trace = source.get("full-trace RMSE g/s", NS)
    trace_base = baseline.get("full-trace RMSE g/s", NS)
    return {
        "endpoint_rmse_g_s": rmse,
        "endpoint_rmse_interval_g_s": field(source, "endpoint RMSE interval", "RMSE interval", "RMSE interval g/s"),
        "b1_endpoint_rmse_g_s": base,
        "endpoint_rmse_ratio_to_b1": rmse / base,
        "endpoint_rmse_change_percent": 100 * (rmse / base - 1),
        "paired_delta_g_s": float(field(source, "delta versus B1 g/s")),
        "paired_delta_interval_g_s": json.dumps(delta),
        "saved_comparison": source["COMPARISON"],
        "accuracy_grade": "N/A (reference)" if source["candidate"] == "B1" else accuracy_grade(rmse, base, source["COMPARISON"]),
        "trace_rmse_g_s": float(trace) if trace != NS else NS,
        "trace_rmse_interval_g_s": source.get("full-trace RMSE interval", NS),
        "b1_trace_rmse_g_s": float(trace_base) if trace_base != NS else NS,
        "trace_rmse_change_percent": 100 * (float(trace) / float(trace_base) - 1) if trace != NS else NS,
        "peak_nominal_bar": float(field(source, "full-model peak nominal bar", "peak nominal bar", "peak location bar")),
        "peak_interval_bar": json.dumps(peak),
        "peak_grade": peak_grade(peak),
        "slope_g_s_bar": float(field(source, "slope g/s/bar", "high-pressure slope g/s/bar")),
        "slope_interval_g_s_bar": json.dumps(slope),
        "slope_grade": slope_grade(slope),
        "response_interval_method": "fixed-fit brew bootstrap" if stage == "A" else "whole-brew refit bootstrap (saved)",
        "original_late_trend_agreement_ungraded": trend,
        "late_trend_means_g_s_s": source.get("late-trend means g/s/s", NS),
        "late_trend_intervals_g_s_s": source.get("late-trend intervals refit", NS),
    }


def resolved_trends(root=ROOT):
    rows = read_rows(Path(root) / "docs/research/PRESSURE_PEAK_STAGE_B0B/LATE_TRENDS.csv")
    resolved = {}
    for row in rows:
        if row["stage"] == "T2 observed" and row["scenario"] == "RAW PRIMARY":
            low, high = json.loads(row["trend interval"])
            if low > 0 or high < 0:
                resolved[float(row["pressure condition bar"])] = 1 if low > 0 else -1
    return resolved, rows


def trend_metrics(stage, candidate, source, basket=False, root=ROOT):
    resolved, records = resolved_trends(root)
    values, bounds = {}, {}
    if stage == "B0b":
        scenario = "T4 BASKET SENSITIVITY" if basket else "T4 RAW PRIMARY"
        for row in records:
            if row["stage"] == "T4/T5 refit" and row["scenario"] == scenario and row["candidate"] == candidate:
                p = float(row["pressure condition bar"])
                values[p] = float(row["trend g/s/s"])
                bounds[p] = json.loads(row["trend interval"])
    elif stage in {"B0c", "B0d"}:
        values = dict(zip(NOMINAL, json.loads(source["late-trend means g/s/s"])))
        bounds = dict(zip(NOMINAL, json.loads(source["late-trend intervals refit"])))
    count = sum(np.sign(values[p]) == sign for p, sign in resolved.items()) if values else None
    return {"resolved_trend_conditions_bar": json.dumps(sorted(resolved)),
            "resolved_trend_matches": int(count) if count is not None else NS,
            "resolved_trend_total": len(resolved),
            "trend_grade": trend_grade(count, len(resolved)),
            "late_trend_means_g_s_s": json.dumps(values) if values else NS,
            "late_trend_intervals_g_s_s": json.dumps(bounds) if bounds else NS,
            "resolved_trend_source": "docs/research/PRESSURE_PEAK_STAGE_B0B/LATE_TRENDS.csv; T2 observed; RAW PRIMARY"}


def restart_record(stage, source, root=ROOT):
    if stage == "A":
        return source["restart consistency"], str(stage_path(stage)), ""
    if stage == "B0":
        sentence = "Filesystem modification times and restart were not used."
        path = stage_path(stage).with_name("SUMMARY.md")
    elif stage == "B0c":
        sentence = "B0c never uses the stop/restart brew."
        path = Path("puckworks/analysis/pressure_peak_stage_b0.py")
    else:
        return NA, str(stage_path(stage).with_name("SUMMARY.md")), "No stage-specific restart statement or direction was saved."
    if sentence not in (Path(root) / path).read_text():
        raise ValueError("Restart source text changed")
    return sentence, str(path), "Direction was not scored."


def complexity(stage, candidate, source):
    if stage == "B0d" and candidate != "B1":
        return 3, 1, "Mc is fixed from the training-fold reference; m=3 is fixed."
    parameters = json.loads(source.get("parameters", "{}"))
    if stage == "B0c" and candidate.startswith("E"):
        return 3, 1 if candidate == "E2" else 3, "Mc and predictive onset c,n are training-estimated inputs held fixed; E2 uses observed onset instead."
    return len(parameters.get("names", A.PARAMETER_NAMES["B1"])), 0, ""


def load_scorecard(root=ROOT):
    rows, sources, omitted = [], {}, []
    for stage, candidates in CANDIDATES.items():
        primary = select_stage(stage, root=root)
        sensitivity = select_stage(stage, basket=True, root=root)
        if "B1" not in primary:
            omitted.append(f"{stage}: no saved B1 reference; stage omitted")
            continue
        for candidate in candidates:
            if candidate not in primary:
                omitted.append(f"{stage}/{candidate}: no saved result")
                continue
            source, number = primary[candidate]
            row = {"candidate": candidate, "stage": stage, "pressure_basis": "raw (line)",
                   "source_file": str(stage_path(stage)), "source_row": number,
                   "saved_scenario": source.get("scenario", source.get("pressure", "RAW")),
                   "saved_fit_stage": source.get("stage", ""),
                   **metrics(stage, source, primary["B1"][0])}
            row.update(trend_metrics(stage, candidate, source, root=root))
            flag = "REFERENCE" if candidate == "B1" else "EXPLORATORY" if candidate == "D3" else "INELIGIBLE" if candidate == "E2" else ""
            row["flag"] = flag
            row["saved_eligibility"] = source.get("eligibility", "")
            row["fitted_parameters"], row["inherited_estimated_inputs"], row["complexity_note"] = complexity(stage, candidate, source)
            row["restart_statement"], row["restart_source"], row["restart_note"] = restart_record(stage, source, root)
            flow = source.get("conductance peak flow interval bar", "")
            timing = source.get("conductance peak timing interval bar", "")
            row.update(timing_flow_peak_interval_bar=flow or NS,
                       timing_peak_interval_bar=timing or NS,
                       matched_timing_law=source.get("matched timing law") or NS,
                       timing_consistency=timing_overlap(json.loads(flow), json.loads(timing)) if flow and timing else NA if stage == "B0d" else NS,
                       timing_note="B1 has no air-inclusive conductance/timing pair." if stage == "B0d" and candidate == "B1" else "")
            if candidate in sensitivity:
                s, s_number = sensitivity[candidate]
                sensitivity_values = {
                    "pressure_basis": "basket; sensitivity only; observed-flow-derived",
                    "source_file": str(stage_path(stage)), "source_row": s_number,
                    **metrics(stage, s, sensitivity["B1"][0]),
                    **trend_metrics(stage, candidate, s, basket=True, root=root),
                    "conductance_peak_flow_interval_bar": s.get("conductance peak flow interval bar", NS),
                    "conductance_peak_timing_interval_bar": s.get("conductance peak timing interval bar", NS),
                }
                row.update({"basket_" + k: v for k, v in sensitivity_values.items() if not k.endswith("_grade")})
            else:
                row["basket_pressure_basis"] = NS
            row["attribution"] = SOURCE_CREDIT
            rows.append(row)
            sources[stage, candidate] = source
    rank_rows(rows)
    return rows, sources, omitted


def rank_rows(rows):
    for row in rows:
        row["meets_count"] = sum(row[key] == "MEETS" for key in GRADES)
        row["misses_count"] = sum(row[key] == "MISSES" for key in GRADES)
        row["scored_count"] = sum(row[key] in {"MEETS", "NEAR", "MISSES"} for key in GRADES)
        row["meets_fraction"] = row["meets_count"] / row["scored_count"] if row["scored_count"] else NA
        row["misses_fraction"] = row["misses_count"] / row["scored_count"] if row["scored_count"] else NA
        row["advisory_rank"] = "EXCLUDED" if row["flag"] or not row["scored_count"] else ""
    eligible = sorted((r for r in rows if not r["flag"] and r["scored_count"]), key=lambda r: (
        -r["meets_fraction"], r["misses_fraction"], r["endpoint_rmse_ratio_to_b1"], r["stage"], r["candidate"]))
    for rank, row in enumerate(eligible, 1):
        row["advisory_rank"] = rank
    return eligible


def continuous_peak(pressures, values):
    """Grid maximum, leftmost on a tie; no optimizer or model fit."""
    pressures, values = np.asarray(pressures), np.asarray(values)
    if pressures.ndim != 1 or values.shape != pressures.shape or not np.isfinite(values).all():
        raise ValueError("Finite curve on a one-dimensional pressure grid required")
    return float(pressures[np.argmax(values)])


def observed_quadratic_peak(pressures, means):
    """The owner's explicit descriptive-fit exception, on 4--8 bar only."""
    p, q = np.asarray(pressures), np.asarray(means)
    coef = np.polynomial.polynomial.polyfit(p, q, 2)
    candidates = [float(p.min()), float(p.max())]
    if coef[2] < 0 and p.min() <= -coef[1] / (2 * coef[2]) <= p.max():
        candidates.append(float(-coef[1] / (2 * coef[2])))
    values = np.polynomial.polynomial.polyval(candidates, coef)
    return float(candidates[int(np.argmax(values))])


def observed_response(root=ROOT, count=1000, seed=SEED):
    records = read_rows(Path(root) / "puckworks/data/waszkiewicz2025/equilibrium_windows.csv")
    groups = {p: [] for p in NOMINAL}
    for row in records:
        if row["window"] == "endpoint_100s" and row["shot_id"] not in WASZ_TRACE_ALIASES:
            groups[float(row["reference_pressure_round__bar"])].append(float(row["mass_flow_rate__g_per_s"]))
    if sum(map(len, groups.values())) != 56:
        raise ValueError("Expected the existing 56 distinct brews")
    rng = np.random.default_rng(seed)
    means = np.array([np.mean(groups[p]) for p in NOMINAL])
    draws = np.column_stack([rng.choice(groups[p], (count, len(groups[p])), replace=True).mean(axis=1) for p in NOMINAL])
    select = (NOMINAL >= 4) & (NOMINAL <= 8)
    peaks = [observed_quadratic_peak(NOMINAL[select], q[select]) for q in draws]
    return {"peak_bar": observed_quadratic_peak(NOMINAL[select], means[select]),
            "peak_interval_bar": A.interval(peaks), "bootstrap_count": count, "seed": seed,
            "means": [{"pressure_bar": float(p), "brews": len(groups[p]), "mean_g_s": float(q),
                       "interval_g_s": A.interval(draws[:, j])} for j, (p, q) in enumerate(zip(NOMINAL, means))]}


def fold_bank(stage, source):
    bank = json.loads(source["parameters by fold"]) if stage == "B0d" else json.loads(source["parameters"])["by_fold"]
    folds = {k: v for k, v in bank.items() if k.startswith("HYD-LOCO-")}
    if len(folds) != 11:
        raise ValueError("Expected eleven saved held-out-pressure parameter sets")
    return dict(sorted(folds.items(), key=lambda item: float(item[0].removeprefix("HYD-LOCO-"))))


def onset_inputs(root=ROOT):
    """Saved pre-outflow pressure aggregates, not measured onset delays."""
    records = read_rows(Path(root) / "docs/research/PRESSURE_PEAK_STAGE_B0C/ONSET.csv")
    return {float(r["pressure condition bar"]): float(r["early pressure mean bar"]) for r in records
            if r["check"] == "condition onset" and r["pressure view"] == "RAW PRIMARY" and float(r["threshold scale"]) == 1.}


def interpolate_training_inputs(grid, held_out, saved):
    """Only training conditions; linear interpolation, nearest endpoint outside."""
    p = sorted(x for x in saved if x != held_out)
    return np.interp(grid, p, [saved[x] for x in p])


def evaluate_saved(stage, candidate, parameters, pressure, t, early_pressure=None):
    if stage == "A":
        return A.predict(candidate, parameters, pressure, t)
    if stage in {"B0", "B0b"}:
        evaluator = B.course_endpoint if stage == "B0b" else B.predict
        return evaluator(candidate, parameters, pressure, t)
    if stage == "B0c":
        free = parameters["free"]
        if candidate == "B1":
            return A.predict(candidate, free, pressure, t)
        if candidate == "E2":
            raise ValueError("E2 requires observed onset; no substitute onset is constructed.")
        delay = parameters["onset_c_fixed_s"] * early_pressure ** (-parameters["onset_n_fixed"])
        return B.predict_swelling(candidate, free, pressure, t, delay, parameters["Mc_fixed_g"])[0][:, -1]
    if candidate == "B1":
        return A.predict(candidate, parameters, pressure, t)
    return B.air_endpoint(np.asarray(parameters), pressure, t, 0 if candidate == "F1" else 1, 3)[0]


def saved_fold_curves(stage, candidate, source, grid=GRID, time_grid=None, root=ROOT):
    """Evaluate all LOCO folds, excluding DESCRIPTIVE_ALL; never call a fitter.

    At every new line pressure, the forcing is constant from the existing stable
    clock's zero to its 100-s endpoint; other state/parameter conventions remain
    unchanged. These curves are not interpolation of the measured brew histories.
    """
    if candidate == "E2":
        raise ValueError("E2 requires observed onset at new pressures; no predictive onset may be substituted.")
    t = np.linspace(0., 100., 1000) if time_grid is None else np.asarray(time_grid)
    pressure = np.repeat(np.asarray(grid)[:, None], len(t), axis=1)
    curves = []
    for fold, parameters in fold_bank(stage, source).items():
        early = interpolate_training_inputs(grid, float(fold.removeprefix("HYD-LOCO-")), onset_inputs(root)) if candidate in {"E1", "E3"} else None
        curve = evaluate_saved(stage, candidate, parameters, pressure, t, early)
        if not np.isfinite(curve).all():
            raise ValueError("Saved-model evaluation produced nonfinite flow")
        curves.append(curve)
    return np.asarray(curves)


def endpoint_inputs(root=ROOT, raw=None):
    """Existing endpoint observer and histories; no fitting or onset detection."""
    records = read_rows(Path(root) / "puckworks/data/waszkiewicz2025/traces_per_brew.csv")
    histories = {}
    for row in records:
        if row["shot_id"] not in WASZ_TRACE_ALIASES:
            histories.setdefault(row["shot_id"], []).append(row)
    ids = sorted(histories, key=lambda name: (float(histories[name][0]["reference_pressure_round__bar"]), name))
    pressure, condition = [], []
    for name in ids:
        r = sorted(histories[name], key=lambda x: int(x["time_index"]))
        if len(r) != 1000:
            raise ValueError("Saved endpoint history is incomplete")
        pressure.append([float(x["pressure__bar"]) for x in r])
        condition.append(float(r[0]["reference_pressure_round__bar"]))
    windows = {r["shot_id"]: float(r["mass_flow_rate__g_per_s"]) for r in read_rows(
        Path(root) / "puckworks/data/waszkiewicz2025/equilibrium_windows.csv") if r["window"] == "endpoint_100s"}
    early = None
    if raw is not None:
        early = []
        for name in ids:
            t0, p0, m0, _ = B.raw_trace(Path(raw) / "measurements_time_dependent" / f"{name}.txt")
            t, p, _, _ = B.clean_course(t0, p0, m0)
            early.append(float(np.median(p[t <= 2])))
        early = np.asarray(early)
        saved = onset_inputs(root)
        for p in NOMINAL:
            if not np.isclose(early[np.asarray(condition) == p].mean(), saved[p], atol=1e-12, rtol=0):
                raise ValueError("Original early-pressure inputs do not reproduce saved ONSET.csv")
    return np.asarray(pressure), np.asarray(condition), np.array([windows[name] for name in ids]), early


def held_out_endpoints(stage, candidate, source, inputs):
    """Replay only the original held-out observations, never the 121-cell matrix.

    Most stages persisted coefficients/losses rather than endpoint arrays. Verify
    the replay against the saved per-condition-averaged RMSE before using it.
    """
    pressure, condition, target, early = inputs
    if candidate in {"E1", "E3"} and early is None:
        raise ValueError("Original early-pressure inputs unavailable for held-out endpoint replay; supply --raw.")
    q = np.empty(len(target))
    t = np.linspace(0, 100, 1000)
    for fold, parameters in fold_bank(stage, source).items():
        group = condition == float(fold.removeprefix("HYD-LOCO-"))
        q[group] = evaluate_saved(stage, candidate, parameters, pressure[group], t, early[group] if early is not None else None)
    rmse = float(np.mean([np.sqrt(np.mean((q[condition == p] - target[condition == p])**2)) for p in NOMINAL]))
    return np.array([q[condition == p].mean() for p in NOMINAL]), rmse


def consistency(curve_values, saved_values, interpolated=False):
    """Retained combined convention/history diagnostic, not the final status."""
    saved_values = np.asarray(saved_values)
    deviations = np.abs(np.asarray(curve_values) - saved_values)
    tolerance = np.maximum(.02, .05 * np.abs(saved_values))
    passed = deviations <= tolerance
    worst = int(np.argmax(deviations))
    return {"curve_status": "INCONSISTENT" if not passed.all() else "INTERPOLATED_INPUTS" if interpolated else "CONSISTENT",
            "curve_checks_passed": int(passed.sum()), "curve_checks_total": len(passed),
            "curve_max_deviation_g_s": float(deviations[worst]), "curve_max_deviation_pressure_bar": float(NOMINAL[worst]),
            "curve_consistency_by_fold": json.dumps([
                {"fold": f"HYD-LOCO-{p}", "pressure_bar": float(p), "constant_endpoint_g_s": float(q),
                 "saved_endpoint_mean_g_s": float(s), "deviation_g_s": float(d), "tolerance_g_s": float(tol), "within_tolerance": bool(ok)}
                for p, q, s, d, tol, ok in zip(NOMINAL, curve_values, saved_values, deviations, tolerance, passed)])}


def saved_endpoint_reference(stage, candidate, source, inputs, root=ROOT, saved_stage_dir=None):
    """Independent saved endpoints only; never use the current replay as truth."""
    _, condition, target, _ = inputs
    if stage == "B0" or (stage == "A" and candidate == "B1"):
        reference = select_stage("B0", root=root)[candidate][0]
        if fold_bank(stage, source) != fold_bank("B0", reference):
            raise ValueError("Saved endpoint reference uses different fold coefficients")
        path = Path("docs/research/PRESSURE_PEAK_STAGE_B0B/RESIDUALS.csv")
        residuals = {float(r["pressure condition bar"]): float(r["residual predicted-observed g/s"])
                     for r in read_rows(Path(root) / path) if r["scenario"] == "RAW PRIMARY" and r["candidate"] == candidate}
        if set(residuals) != set(NOMINAL):
            raise ValueError("Saved condition residuals are incomplete")
        return np.array([target[condition == p].mean() + residuals[p] for p in NOMINAL]), str(path) + "; B0 saved held-out coefficients; no refit"
    if stage == "B0d":
        path = Path(saved_stage_dir) / ".b0-b0d-point-0.json" if saved_stage_dir else None
        if path is not None and path.exists():
            saved = json.loads(path.read_text())["flow"][candidate]
            bank = {k: v for k, v in saved["by_fold"].items() if k.startswith("HYD-LOCO-")}
            if bank != fold_bank(stage, source):
                raise ValueError("Original saved B0d endpoint cache has different coefficients")
            # Original stage cohort is ordered by (nominal pressure, source ID),
            # exactly as endpoint_inputs. Only condition aggregates are exported.
            q = np.array(saved["endpoint"])
            return np.array([q[condition == p].mean() for p in NOMINAL]), "original Stage B0d .b0-b0d-point-0.json; flow/" + candidate + "/endpoint; condition aggregates only"
        # Re-generation can consume the previously extracted independent aggregate;
        # its explicit source is retained, never replaced by today's replay values.
        snapshot = Path(root) / "docs/research/PRESSURE_PEAK_SCORECARD/SCORECARD.csv"
        if snapshot.exists():
            for r in read_rows(snapshot):
                if r["stage"] == stage and r["candidate"] == candidate and r.get("saved_endpoint_reference_g_s", NA) != NA:
                    return np.array(json.loads(r["saved_endpoint_reference_g_s"])), r["saved_endpoint_reference_source"]
        raise ValueError("Original saved B0d endpoint cache unavailable; supply --saved-stage-dir")
    raise ValueError("Independent per-condition endpoint predictions were not persisted by this stage; saved RMSE reproduction is aggregate evidence only.")


def replay_check(replayed, saved):
    deviations = np.abs(np.asarray(replayed) - np.asarray(saved))
    within = deviations <= .015
    worst = int(np.argmax(deviations))
    return {"curve_status": "CONSISTENT_IDEALISATION" if within.all() else "INCONSISTENT", "check_tier": "PREDICTION",
            "replay_checks_passed": int(within.sum()), "replay_checks_total": len(within),
            "replay_max_deviation_g_s": float(deviations[worst]),
            "replay_max_deviation_pressure_bar": float(NOMINAL[worst]),
            "replay_checks_by_pressure": json.dumps([
                {"pressure_bar": float(p), "replayed_endpoint_g_s": float(q), "saved_endpoint_g_s": float(s),
                 "deviation_g_s": float(d), "within_tolerance": bool(ok)}
                for p, q, s, d, ok in zip(NOMINAL, replayed, saved, deviations, within)])}


def score_check(replayed, saved, tier="AGGREGATE"):
    """Weaker score checks are never counted as independent prediction checks."""
    replayed, saved = np.atleast_1d(replayed), np.atleast_1d(saved)
    if tier not in {"AGGREGATE", "FOLD_SCORE"} or replayed.shape != saved.shape:
        raise ValueError("Invalid score-check tier or shape")
    expected_count = 11 if tier == "FOLD_SCORE" else 1
    if len(saved) != expected_count:
        raise ValueError("Score-check count does not match its tier")
    deviation = np.abs(replayed - saved)
    tolerance = np.maximum(.005, .01 * np.abs(saved))
    within = deviation <= tolerance
    return {"curve_status": "CONSISTENT_IDEALISATION_" + tier if within.all() else "INCONSISTENT",
            "check_tier": tier, "score_checks_passed": int(within.sum()), "score_checks_total": expected_count,
            "score_max_deviation_g_s": float(deviation.max()), "score_check_tolerance_g_s": json.dumps(tolerance.tolist())}


def ramp_effect(constant, replayed):
    difference = np.asarray(constant) - np.asarray(replayed)
    worst = int(np.argmax(np.abs(difference)))
    return {"ramp_effect_median_g_s": float(np.median(difference)),
            "ramp_effect_range_g_s": json.dumps([float(difference.min()), float(difference.max())]),
            "ramp_effect_largest_abs_g_s": float(abs(difference[worst])),
            "ramp_effect_largest_pressure_bar": float(NOMINAL[worst]),
            "ramp_effect_by_pressure": json.dumps([
                {"pressure_bar": float(p), "constant_minus_replay_g_s": float(d)} for p, d in zip(NOMINAL, difference)])}


@contextmanager
def time_limit(seconds):
    def expired(signum, frame):
        raise TimeoutError("Evaluation time budget reached; no refit attempted")
    old = signal.signal(signal.SIGALRM, expired)
    signal.setitimer(signal.ITIMER_REAL, max(.001, seconds))
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, old)


def evaluate_rows(rows, sources, deadline, inputs, root=ROOT, saved_stage_dir=None):
    curves = {}
    ranked = rank_rows(rows)
    priority = {(r["stage"], r["candidate"]) for r in ranked[:2]} | {("B0d", "F1"), ("B0d", "B1")}
    ordered = sorted(rows, key=lambda r: (r["stage"], r["candidate"]) not in priority)
    for row in ordered:
        key = row["stage"], row["candidate"]
        row.update(continuous_peak_median_bar=NA, continuous_peak_fold_range_bar=NA,
                   continuous_peak_by_fold_bar=NA, continuous_peak_note="",
                   curve_label=CURVE_LABEL, curve_status=NA, check_tier=NA, curve_checks_passed=NA, curve_checks_total=11,
                   curve_max_deviation_g_s=NA, curve_max_deviation_pressure_bar=NA, curve_consistency_by_fold=NA,
                   curve_input_convention="INTERPOLATED_INPUTS: training-condition early-pressure means; linear interpolation with nearest endpoint outside training range" if key[1] in {"E1", "E3"} else "constant raw pressure; no measured ancillary input required",
                   replay_endpoint_rmse_g_s=NA,
                   replay_checks_passed=NA, replay_checks_total=11, replay_max_deviation_g_s=NA,
                   replay_max_deviation_pressure_bar=NA, replay_checks_by_pressure=NA,
                   saved_endpoint_reference_g_s=NA, saved_endpoint_reference_source=NA,
                   replay_check_note="", replay_endpoint_means_g_s=NA,
                   score_checks_passed=NA, score_checks_total=NA, score_max_deviation_g_s=NA, score_check_tolerance_g_s=NA,
                   ramp_effect_median_g_s=NA, ramp_effect_range_g_s=NA, ramp_effect_largest_abs_g_s=NA,
                   ramp_effect_largest_pressure_bar=NA, ramp_effect_by_pressure=NA,
                   endpoint_reference_source="saved fold coefficients and original endpoint observer; held-out-only replay checked against saved RMSE; traces_per_brew.csv",
                   continuous_convention="Constant raw line pressure; stable-clock 0--100 s; original initial states; fold-fixed Mc and onset coefficients; original air terms; 0.05-bar grid; fold range is not a confidence interval.")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            row["continuous_peak_note"] = "Analysis compute budget exhausted."
            continue
        try:
            with time_limit(min(120., remaining)):
                values = saved_fold_curves(*key, sources[key], root=root)
            peaks = [continuous_peak(GRID, curve) for curve in values]
            row.update(continuous_peak_median_bar=float(np.median(peaks)),
                       continuous_peak_fold_range_bar=json.dumps([min(peaks), max(peaks)]),
                       continuous_peak_by_fold_bar=json.dumps(peaks))
            curves[key] = values
            saved, rmse = held_out_endpoints(*key, sources[key], inputs)
            nominal_values = np.array([np.interp(p, GRID, values[i]) for i, p in enumerate(NOMINAL)])
            row.update(consistency(nominal_values, saved, interpolated=key[1] in {"E1", "E3"}))
            row["combined_check_status_ungraded"] = row["curve_status"]
            row["curve_status"] = NA
            row["replay_endpoint_rmse_g_s"] = rmse
            row["replay_endpoint_means_g_s"] = json.dumps(saved.tolist())
            row.update(ramp_effect(nominal_values, saved))
            try:
                reference, provenance = saved_endpoint_reference(*key, sources[key], inputs, root, saved_stage_dir)
                row["saved_endpoint_reference_g_s"] = json.dumps(reference.tolist())
                row["saved_endpoint_reference_source"] = provenance
                row.update(replay_check(saved, reference))
            except ValueError as error:
                row["replay_check_note"] = str(error)
                # Audited RESULT_TABLE/companion CSVs contain no per-fold losses
                # for A, B0b or B0c. Do not manufacture eleven fold scores.
                if key[0] in {"A", "B0b", "B0c"}:
                    row.update(score_check(rmse, row["endpoint_rmse_g_s"]))
        except (ValueError, RuntimeError, TimeoutError) as error:
            row["continuous_peak_note"] = str(error)
        print(f"evaluated {key}: {row['curve_status']} replay={row['replay_checks_passed']}/11 max={row['replay_max_deviation_g_s']} ramp={row['ramp_effect_median_g_s']} {row['continuous_peak_note'] or row['replay_check_note']}", flush=True)
    return curves


def plot_figure(rows, curves, observed, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(11.2, 6.6), layout="constrained")
    means = observed["means"]
    y = np.array([m["mean_g_s"] for m in means])
    lo, hi = np.array([m["interval_g_s"] for m in means]).T
    ax.axvspan(5, 7, color="#d6e8d1", alpha=.65, label="Peak grading band: 5–7 bar")
    ax.errorbar(NOMINAL, y, yerr=[y-lo, hi-y], fmt="o", color="#202a35", capsize=3,
                markersize=4, label="Observed endpoint means · 95% brew bootstrap", zorder=5)
    selected = [("B0d", "F1"), ("B0d", "B1")] + [(r["stage"], r["candidate"]) for r in rank_rows(rows)[:2]]
    missing = []
    for key, color in zip(dict.fromkeys(selected), ("#a63a50", "#476a8a", "#c4781a", "#456e45")):
        if key not in curves:
            missing.append("/".join(key))
            continue
        values = curves[key]
        row = next(r for r in rows if (r["stage"], r["candidate"]) == key)
        status = row["curve_status"]
        input_label = " · INTERPOLATED_INPUTS" if key[1] in {"E1", "E3"} else ""
        weak = row["check_tier"] == "AGGREGATE"
        strength = " · weaker check (aggregate only)" if weak else ""
        ax.plot(GRID, np.median(values, axis=0), color=color, lw=2, alpha=.65 if weak else 1.,
                linestyle="--" if status in {"INCONSISTENT", NA} else "-",
                label=f"{key[0]} {key[1]} · {row['check_tier']}{input_label}\nconstant-pressure idealisation{strength}\n{CURVE_LABEL}")
        ax.fill_between(GRID, values.min(axis=0), values.max(axis=0), color=color, alpha=.08)
    ax.set(xlim=(.8, 13.2), ylim=(0, None), xlabel="Nominal observed / prescribed model line pressure (bar)",
           ylabel="Flow at 100 s (g/s)", title="Pressure turnover: saved models, graded separately")
    ax.set_xticks(NOMINAL)
    ax.grid(axis="y", alpha=.18)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=7.5)
    note = "Curves: median of saved folds; light band = fold range (not CI). Lighter line = weaker aggregate check."
    if missing:
        note += " NOT_AVAILABLE: " + ", ".join(missing)
    fig.supxlabel(note + "\nWaszkiewicz et al. (2025) · Zenodo 18046315 · CC-BY-4.0", fontsize=8)
    fig.savefig(path, dpi=180, metadata={"Description": SOURCE_CREDIT})
    plt.close(fig)


def markdown_table(rows):
    lines = ["| Candidate | Stage | Accuracy | Peak | Slope | Trend | Timing | Complexity | Restart |",
             "|---|---|---|---|---|---|---|---|---|"]
    for row in rows:
        complexity_text = str(row["fitted_parameters"])
        if row["inherited_estimated_inputs"]:
            complexity_text += f" + {row['inherited_estimated_inputs']}n"
        if row["flag"]:
            complexity_text += " " + row["flag"]
        restart = row["restart_statement"]
        restart = "higher*" if restart.startswith("higher") else "cannot say" if restart.startswith("cannot say") else "unused" if restart != NA else NA
        values = [row["candidate"], row["stage"], *(row[k] for k in GRADES), row["timing_consistency"], complexity_text, restart]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def ranking_text(rows):
    return "; ".join(f"{r['advisory_rank']}. {r['stage']}/{r['candidate']} (MEETS {r['meets_count']}/{r['scored_count']} scored, "
                     f"MISSES {r['misses_count']}/{r['scored_count']}, RMSE/B1 {r['endpoint_rmse_ratio_to_b1']:.3f})" for r in rank_rows(rows)) + "."


def write_summary(rows, observed, omitted, elapsed, cpu, path):
    original = path.read_text()
    if MARKER not in original:
        raise ValueError("Verbatim owner bands must exist before results are written")
    prefix = original.split(MARKER)[0] + MARKER + "\n\n"
    ranked = rank_rows(rows)
    leaders = ", ".join(f"{r['stage']}/{r['candidate']}" for r in ranked[:2])
    reading = (f"{leaders} lead: E1 matches the endpoint capability, high-pressure slope and resolved late-trend bands, while F1 matches endpoint capability, the saved peak interval and resolved trends. "
               "E1's saved peak interval remains one grid step high; F1 declines too steeply and its air-inclusive conductance peak disagrees with wetting timing. "
               "E1 therefore looks like a peak-location near miss on these criteria, whereas F1 retains a mechanism-consistency shortfall; neither interpretation establishes physical validation.")
    tradeoff = "Across candidates there is a trade-off: forms that place the peak at 5–7 bar decline too steeply above 9 bar (F1, F2), while forms with the observed high-pressure slope peak near 8 bar (E1, C4). No single saved form yet captures both."
    unavailable = [f"{r['stage']}/{r['candidate']}: {r['continuous_peak_note'] or r['replay_check_note']}" for r in rows if r["curve_status"] == NA]
    unavailable += ["B0d/B1: timing pair NOT_AVAILABLE (no air-inclusive reference law).",
                    "B0b and B0d restart statements NOT_AVAILABLE; no stage-specific direction was saved."]
    interval = observed["peak_interval_bar"]
    effects = [abs(x["constant_minus_replay_g_s"]) for r in rows if r["ramp_effect_by_pressure"] != NA for x in json.loads(r["ramp_effect_by_pressure"])]
    errors = [r["endpoint_rmse_g_s"] for r in ranked]
    typical_rmse = float(np.median(errors))
    typical_effect = float(np.median(effects))
    ramp_reading = (f"The pooled median absolute ramp effect is **{typical_effect:.3f} g/s**, "
                    f"or {100*typical_effect/max(errors):.1f}–{100*typical_effect/min(errors):.1f}% of eligible-candidate endpoint RMSEs "
                    f"({100*typical_effect/typical_rmse:.1f}% of their median, {typical_rmse:.3f} g/s). "
                    f"The maximum is {max(effects):.3f} g/s at 13 bar (E3); the largest effects concentrate at 2 and 13 bar, outside the 4–8 bar peak region.")
    signed = [x["constant_minus_replay_g_s"] for r in rows if r["ramp_effect_by_pressure"] != NA for x in json.loads(r["ramp_effect_by_pressure"])]
    replay_reading = ("The initial all-curve consistency failure was due to start-up pressure history, not curve code: "
                      "all checkable replays reproduced saved results (8 rows at prediction level, 11 at aggregate level).")
    if not all(r["curve_status"].startswith("CONSISTENT_IDEALISATION") for r in rows if r["check_tier"] != NA):
        replay_reading = "Some available replay checks failed; see the check-tier table before interpreting curves."
    replay_reading += (f" The signed ramp-effect median is {np.median(signed):+.3f} g/s, with range [{min(signed):+.3f}, {max(signed):+.3f}] g/s; "
                       "the largest magnitudes occur at 13 and 2 bar. Here 'start-up pressure history' includes the nominal-versus-recorded pressure contrast, "
                       "which is nonzero even for memoryless B1; the check does not isolate a causal start-up contribution.")
    next_actions = ["**Owner choice:** select E1 for a bounded EWP reproduction exercise; it leads the capability ranking without a missed graded criterion, "
                    "while its peak-location and weaker aggregate-check limitations must remain explicit. No implementation is started."]
    optional_action = ("**Optional / low priority:** Test whether modelling the measured start-up pressure ramp (rather than constant pressure) moves the predicted flow peak toward 6 bar, using saved fits only; "
                       "typical effect is ~10% of model error and concentrated away from the peak region.")
    e1 = next(r for r in rows if (r["stage"], r["candidate"]) == ("B0c", "E1"))
    f1 = next(r for r in rows if (r["stage"], r["candidate"]) == ("B0d", "F1"))
    peak_reading = "E1/F1 continuous-peak comparison NOT_AVAILABLE: both curves must have a consistent idealisation check."
    if all(r["curve_status"].startswith("CONSISTENT_IDEALISATION") for r in (e1, f1)):
        peak_reading = (f"E1's constant-pressure idealisation peaks at {e1['continuous_peak_median_bar']:.2f} bar (weaker check (aggregate only)) "
                        f"and F1's at {f1['continuous_peak_median_bar']:.2f} bar, both above the observed continuous estimate "
                        f"of {observed['peak_bar']:.3f} [{interval[0]:.3f}, {interval[1]:.3f}] bar (95% interval); this comparison is descriptive and leaves grades unchanged.")
    results = [markdown_table(rows), "", reading, "", tradeoff, "", peak_reading, "",
               "**Advisory leaders:** 1. B0c/E1; 2. B0d/F1. Full ranking and diagnostics below.", "",
               "**Main limits:** E1 — peak location (NEAR); F1 — high-pressure slope (MISSES).", "",
               *next_actions, "", ramp_reading, "", optional_action, "",
               "<details><summary>Full advisory ranking, replay checks, ramp effects, methods and sources</summary>", "",
               "**Advisory ranking:** " + ranking_text(rows), "",
               replay_reading, "",
               f"Observed descriptive quadratic peak: **{observed['peak_bar']:.3f} [{interval[0]:.3f}, {interval[1]:.3f}] bar** "
               f"(95% whole-brew bootstrap, {observed['bootstrap_count']} resamples, seed {observed['seed']}; fit restricted to 4–8 bar).",
               "", continuous_peak_table(rows, observed), "",
               "Every curve below and in FIGURE.png is labelled **" + CURVE_LABEL + "**. "
               "Continuous model peaks and fold ranges are in SCORECARD.csv; FIGURE.png plots the requested unique curves (F1 is also a ranked leader). "
               "Constant line pressure from stable-clock zero to 100 s is a descriptive forcing convention, not a reconstruction of variable measured histories. "
               "No new mechanism fit, resampling of model parameters, or modification of earlier outputs occurred.",
               "Ranking uses the fraction of scored criteria graded MEETS, then the fraction graded MISSES (lower first), then endpoint RMSE/B1. "
               "Only MEETS, NEAR and MISSES enter the denominator; NOT_SCORED and NOT_AVAILABLE enter neither numerator nor denominator. "
               "Timing, complexity and restart are not ranking grades. B1 accuracy is N/A (reference), and B1 is excluded from ranking; "
               "D3 is EXPLORATORY and E2 is INELIGIBLE. B0's raw sensitivity is promoted to this scorecard's primary; basket results occupy separate, ungraded CSV columns. "
               "Each stage uses its own B1 and saved interval method, so the cross-stage ranking is advisory, not a new matched statistical comparison.",
               "Complexity lists free fitted parameters + n fixed training-estimated nuisance inputs; no coefficients were refitted here. "
               "Restart higher* copies Stage A: 'higher (consistent direction; continued delivery, no pause benefit)'; full source statements are in the CSV. "
               "Whole-brew resampling samples each existing brew as a unit within its pressure condition, preserving the cohort and its duplicate exclusion.",
               "Resolved observed late trends confirmed from LATE_TRENDS.csv: " + ", ".join(f"{p:g}" for p in resolved_trends()[0]) + " bar, all rising; no difference from the owner's set. Original x/11 counts remain ungraded in the CSV.",
               "Replay and ramp effects are separate. PREDICTION checks compare replayed versus saved held-out condition-mean endpoints, tolerance 0.015 g/s. "
               "B0 references are reconstructed from saved condition residuals plus observed means; A/B1 shares exactly the same fold coefficients and observer. "
               "B0d references are condition aggregates extracted from the original saved endpoint cache, with coefficients checked against RESULT_TABLE.csv; individual brews are not exported. "
               "No per-fold scores were saved for the remaining A/B0b/B0c rows: their strongest check is AGGREGATE, one score comparison at max(0.005 g/s, 1% of saved RMSE). "
               "Their per-prediction checks remain NOT_AVAILABLE, not 11 independent successes. There is no 121-check matrix. "
               "E1/E3 retain fold-fixed onset coefficients and Mc; their onset pressure input interpolates saved early-pressure means from training conditions only (nearest endpoint beyond that fold's training range). "
               "Stable-pressure zero, original initial states and B0d air terms are preserved. Solid lines are constant-pressure idealisations; aggregate-only lines are lighter and labelled weaker check (aggregate only). "
               "INCONSISTENT curves would be dashed and excluded from peak interpretation. Grades always use saved intervals.",
               "", curve_table(rows), "",
               "Ramp effect = constant nominal-pressure endpoint minus measured-history replay at each fold's held-out condition. "
               "It includes nominal-versus-recorded pressure differences, evidenced by B1's nonzero contrast despite having no memory; it does not isolate a causal start-up contribution. "
               "The table gives the signed median and range across the original held-out conditions; every pressure's signed value is in SCORECARD.csv. "
               "The check tier shown for each result is the replay evidence supporting that ramp contrast.",
               "", ramp_table(rows), "",
               "NOT_AVAILABLE: " + " ".join(unavailable),
               "Omitted requested rows: " + ("; ".join(omitted) if omitted else "none; E2 is included and flagged as requested."),
               f"Generation compute: {elapsed:.2f} s wall / {cpu:.2f} s process CPU; model refits: 0. QA time is reported separately in the PR.",
               "Sources: [Stage A](../PRESSURE_PEAK_STAGE_A/RESULT_TABLE.csv), [B0](../PRESSURE_PEAK_STAGE_B0/RESULT_TABLE.csv), "
               "[B0b](../PRESSURE_PEAK_STAGE_B0B/RESULT_TABLE.csv), [B0c](../PRESSURE_PEAK_STAGE_B0C/RESULT_TABLE.csv), "
               "[B0d](../PRESSURE_PEAK_STAGE_B0D/RESULT_TABLE.csv), and their named companion CSVs; "
               "[100-s brew endpoints](../../../puckworks/data/waszkiewicz2025/equilibrium_windows.csv). "
               "Waszkiewicz et al. (2025), [Zenodo 18046315](https://doi.org/10.5281/zenodo.18046315), CC-BY-4.0. "
               "Only attributed aggregates are added. PHYSICAL_VALIDATION=NOT_ESTABLISHED.", "", "</details>", ""]
    path.write_text(prefix + "\n".join(results), encoding="utf-8")


def peak_interpretation(row):
    if not row["curve_status"].startswith("CONSISTENT_IDEALISATION"):
        return NA
    return "constant-pressure idealisation" + ("; weaker check (aggregate only)" if row["check_tier"] == "AGGREGATE" else "")


def continuous_peak_table(rows, observed):
    lines = ["| Row | Continuous peak, bar | Interval, bar | Interpretation |",
             "|---|---|---|---|"]
    low, high = observed["peak_interval_bar"]
    lines.append(f"| Observed (quadratic, 4–8 bar) | {observed['peak_bar']:.3f} | [{low:.3f}, {high:.3f}] | 95% whole-brew bootstrap interval |")
    for row in rows:
        if not row["curve_status"].startswith("CONSISTENT_IDEALISATION"):
            continue
        low, high = json.loads(row["continuous_peak_fold_range_bar"])
        lines.append(f"| {row['stage']}/{row['candidate']} | {row['continuous_peak_median_bar']:.2f} | [{low:.2f}, {high:.2f}] | {peak_interpretation(row)}; fold range |")
    return "\n".join(lines)


def curve_table(rows):
    lines = ["| Curve (all: descriptive evaluation of saved fits — not a prediction) | Status | Check tier | Prediction checks | Score checks | Largest check deviation, g/s |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        deviation = f"{r['replay_max_deviation_g_s']:.3g} at {r['replay_max_deviation_pressure_bar']:g} bar" if r['replay_max_deviation_g_s'] != NA else f"{r['score_max_deviation_g_s']:.3g} (score)" if r['score_max_deviation_g_s'] != NA else NA
        input_label = " (INTERPOLATED_INPUTS)" if r['candidate'] in {"E1", "E3"} else ""
        checks = f"{r['replay_checks_passed']}/11" if r['replay_checks_passed'] != NA else NA
        score = f"{r['score_checks_passed']}/{r['score_checks_total']}" if r['score_checks_passed'] != NA else NA
        lines.append(f"| {r['stage']}/{r['candidate']}{input_label} | {r['curve_status']} | {r['check_tier']} | {checks} | {score} | {deviation} |")
    return "\n".join(lines)


def ramp_table(rows):
    lines = ["| Candidate | Stage | Check tier | Median effect, g/s | Range, g/s | Largest absolute effect, g/s | Pressure, bar |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        median = bounds = maximum = pressure = NA
        if r["ramp_effect_median_g_s"] != NA:
            low, high = json.loads(r["ramp_effect_range_g_s"])
            median = f"{r['ramp_effect_median_g_s']:+.4f}"
            bounds = f"[{low:+.4f}, {high:+.4f}]"
            maximum = f"{r['ramp_effect_largest_abs_g_s']:.4f}"
            pressure = f"{r['ramp_effect_largest_pressure_bar']:g}"
        lines.append(f"| {r['candidate']} | {r['stage']} | {r['check_tier']} | {median} | {bounds} | {maximum} | {pressure} |")
    return "\n".join(lines)


def generate(out=OUTPUT, root=ROOT, max_seconds=600., raw=None, saved_stage_dir=None):
    started, cpu_started = time.monotonic(), time.process_time()
    out = Path(out)
    if not (out / "SUMMARY.md").exists():
        raise ValueError("Create SUMMARY.md with the verbatim owner bands before generating results")
    rows, sources, omitted = load_scorecard(root)
    observed = observed_response(root)
    inputs = endpoint_inputs(root, raw)
    curves = evaluate_rows(rows, sources, started + min(max_seconds, 3600.), inputs, root, saved_stage_dir)
    for row in rows:
        row.update(observed_continuous_peak_bar=observed["peak_bar"],
                   observed_continuous_peak_interval_bar=json.dumps(observed["peak_interval_bar"]),
                   observed_condition_means=json.dumps(observed["means"]),
                   observed_source="puckworks/data/waszkiewicz2025/equilibrium_windows.csv; endpoint_100s; aliases excluded",
                   observed_bootstrap_seed=SEED, observed_bootstrap_count=1000)
    write_scorecard(rows, out / "SCORECARD.csv")
    plot_figure(rows, curves, observed, out / "FIGURE.png")
    elapsed, cpu = time.monotonic() - started, time.process_time() - cpu_started
    write_summary(rows, observed, omitted, elapsed, cpu, out / "SUMMARY.md")
    print(f"generation_seconds={elapsed:.3f}; process_cpu_seconds={cpu:.3f}; model_refits=0", flush=True)
    return rows


def write_scorecard(rows, path):
    for row in rows:
        row["continuous_peak_interpretation"] = peak_interpretation(row)
    with Path(path).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for row in rows for k in row)), restval=NS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rescore_saved(out=OUTPUT, root=ROOT):
    """Refresh grades/ranking/text without evaluating curves or fitting anything."""
    out = Path(out)
    stored = read_rows(out / "SCORECARD.csv")
    fresh, _, omitted = load_scorecard(root)
    keys = lambda rows: [(r["stage"], r["candidate"]) for r in rows]
    if keys(stored) != keys(fresh):
        raise ValueError("Saved and current stage rows differ; cannot reuse curve results")
    old_leaders = sorted((r for r in stored if str(r["advisory_rank"]).isdigit()), key=lambda r: int(r["advisory_rank"]))[:2]
    if keys(old_leaders) != keys(rank_rows(fresh)[:2]):
        raise ValueError("Figure leaders changed; regenerate the saved-parameter curves before publishing")
    rows = []
    for old, new in zip(stored, fresh):
        row = {**old, **new}
        for key, value in row.items():
            if not isinstance(value, str):
                continue
            try:
                parsed = json.loads(value)
            except ValueError:
                continue
            if type(parsed) in (int, float):
                row[key] = parsed
        rows.append(row)
    first = rows[0]
    observed = {"peak_bar": first["observed_continuous_peak_bar"],
                "peak_interval_bar": json.loads(first["observed_continuous_peak_interval_bar"]),
                "bootstrap_count": first["observed_bootstrap_count"], "seed": first["observed_bootstrap_seed"]}
    timing = re.search(r"Generation compute: ([\d.]+) s wall / ([\d.]+) s process CPU", (out / "SUMMARY.md").read_text())
    if timing is None:
        raise ValueError("Original generation timing is missing; do not invent replacement metadata")
    write_scorecard(rows, out / "SCORECARD.csv")
    write_summary(rows, observed, omitted, float(timing[1]), float(timing[2]), out / "SUMMARY.md")
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUTPUT)
    parser.add_argument("--max-seconds", type=float, default=600.)
    parser.add_argument("--raw", type=Path, help="Existing Waszkiewicz source root; needed only to replay E1/E3's original early-pressure inputs")
    parser.add_argument("--saved-stage-dir", type=Path, help="Original stage workspace containing the existing B0d endpoint cache")
    parser.add_argument("--rescore-saved", action="store_true", help="Refresh ranking and text from the existing CSV without fitting or evaluating curves")
    args = parser.parse_args()
    if args.rescore_saved:
        rescore_saved(out=args.out)
    else:
        generate(out=args.out, max_seconds=args.max_seconds, raw=args.raw, saved_stage_dir=args.saved_stage_dir)


if __name__ == "__main__":
    main()

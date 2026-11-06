"""Frozen Waszkiewicz replay: authenticate, reproduce, then observe; never fit.

Waszkiewicz et al. (2025), Zenodo 18046315, CC-BY-4.0 data. The inherited
JOINT_CLOCK and screen predictors own the dynamics. This module changes only
the reporting observer and writes exclusively to this task's output locations.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import csv
import json
from pathlib import Path
import time

import numpy as np
from scipy.signal import savgol_filter

from . import joint_clock_001 as J
from . import joint_clock_001_evaluate as JE
from . import joint_clock_001_run as JR
from . import pressure_peak_stage_d0 as D0
from . import wasz_turnover_time_001 as O
from . import wetting_screen_001 as W
from . import wetting_screen_001_run as WR

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/TURNOVER_TIME_REPLAY_001"
MODELS = ("A-J1", "D0-R0-diagnostic")
SCOPES = ("LOCO", "DESCRIPTIVE_ALL")
DT = .005
_DATA = None
_ARGS = None


def read_json(path):
    return json.loads(Path(path).read_text())


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def checked_hash(path, expected):
    actual = O.digest(path)
    if actual != expected:
        raise ValueError(f"Frozen input identity mismatch: {Path(path).name}")
    return actual


def load_d0_rows():
    """Read the saved point bank only; no optimizer/refit entry point is called."""
    csv.field_size_limit(100_000_000)
    with (ROOT / "docs/research/PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv").open() as f:
        raw = list(csv.DictReader(f))
    selected = {}
    for row in raw:
        if row["record_type"] != "point_replay" or row["candidate"] != "A":
            continue
        if row["fold"] not in {JR.label(None), *(JR.label(p) for p in W.NOMINAL)}:
            continue
        parsed = {}
        for key, value in row.items():
            if value:
                try:
                    parsed[key] = json.loads(value)
                except (ValueError, TypeError):
                    parsed[key] = value
        selected[row["fold"]] = parsed
    if len(selected) != 12:
        raise ValueError("Incomplete D0 bank")
    return selected


def select_parameters(model, scope, source, data):
    """One matching outer fit AND Mc; held-condition membership is checked in full."""
    held = source["nominal_pressure_bar"] if scope == "LOCO" else None
    fold = JR.label(held)
    intended = [s["brew"] for s in data["sources"]
                if held is None or s["nominal_pressure_bar"] != held]
    if model == "A-J1":
        row = data["joint_fits"][fold]
        if row["fold"] != fold or row["held_condition_bar"] != held or row["model"] != "J1" or row["weight"] != 1:
            raise ValueError("Wrong A-J1 fit")
        parameters, mc = row["parameters"], row["mc_fixed_g"]
    else:
        row = data["d0_rows"][fold]
        parameters = [row["parameters"][k] for k in ("a_g_s_bar", "Pstar_bar", "n", "Pd_bar")]
        mc = row["Mc_fixed_g"]
    if set(row["training_brews"]) != set(intended) or len(row["training_brews"]) != len(intended):
        raise ValueError("Training membership differs from complete held-condition exclusion")
    if mc != data["bank"][fold][4]:
        raise ValueError("Mc does not belong to the matching fold")
    return np.asarray(parameters, dtype=float), float(mc), fold


def load_inputs(args):
    """Authenticate inherited manifests and observations without historical writes."""
    freeze = read_json(OUT / "INPUT_MANIFEST.json")
    for name, expected in freeze["repository_inputs"].items():
        checked_hash(ROOT / name, expected)
    for name, expected in freeze["wasz_inputs"].items():
        checked_hash(args.wasz / "docs/research/WASZ_TURNOVER_TIME_001" / name, expected)
    joint = read_json(ROOT / "docs/research/JOINT_CLOCK_001/RUN_MANIFEST.json")
    screen = read_json(ROOT / "docs/research/WETTING_SCREEN_001/RUN_MANIFEST.json")
    checked_hash(args.native / "source_inputs.json", joint["source_inputs_sha256"])
    checked_hash(args.ewp / "docs/demonstrations/FORM_A/RUN_MANIFEST.json", joint["native_manifest_sha256"])
    for name, expected in joint["source_sha256"].items():
        checked_hash(ROOT / name, expected)
    for name, expected in joint["historical_replay_helpers"].items():
        checked_hash(ROOT / "puckworks/analysis" / name, expected)
    if read_json(args.joint / "EVALUATION_INDEX.json") != joint["predictions"]:
        raise ValueError("Joint prediction index changed")
    data = JR.load_data(args)  # Read-only loader, with original/config/onset authentication.
    data["d0_rows"] = load_d0_rows()
    data["joint_fits"] = {}
    for row in joint["fits"]:
        if row["key"].startswith("J1_lambda-1_"):
            path = args.joint / "fits" / row["file"]
            checked_hash(path, row["sha256"])
            fit = read_json(path)
            if fit["identity"] != JR.identity():
                raise ValueError("Joint fit source identity changed")
            data["joint_fits"][fit["fold"]] = fit
    if len(data["joint_fits"]) != 12:
        raise ValueError("Incomplete joint bank")
    historical = []
    for model, folder, records, marker in (
        (MODELS[0], args.joint / "predictions", joint["predictions"]["records"], "_J1_lambda-1_"),
        (MODELS[1], args.screen / "predictions", screen["predictions"], "_Z_")):
        selected = []
        for entry in records:
            if marker not in entry["key"]:
                continue
            path = folder / (entry["key"] + ".json")
            checked_hash(path, entry["metadata_sha256"])
            row = read_json(path)
            if model == MODELS[0]:
                if row["identity"]["fit_identity"] != JR.identity() or row["identity"]["evaluator_sha256"] not in JE.accepted_evaluator_hashes():
                    raise ValueError("Historical joint evaluator/fit changed")
                fit_path = args.joint / "fits" / (JR.key("J1", 1., None if row["scope"] == "descriptive" else row["pressure_bar"]) + ".json")
                checked_hash(fit_path, row["identity"]["fit_sha256"])
            elif row["identity"]["predictor_sha256"] != O.digest(W.__file__):
                raise ValueError("Historical screen predictor changed")
            for step in ("fine", "search"):
                artifact = row[step]["prediction"]
                checked_hash(folder / artifact["file"], artifact["sha256"])
            selected.append((model, str(folder), row))
        if len(selected) != 79:
            raise ValueError("Incomplete historical 56+23 cases")
        historical.extend(selected)
    data["historical"] = historical
    receipt = read_json(args.wasz / "docs/research/WASZ_TURNOVER_TIME_001/RUN_RECEIPT.json")
    if [s["brew"] for s in data["sources"]] != receipt["brew_order"]:
        raise ValueError("Brew order differs from #423")
    condition = np.array([s["nominal_pressure_bar"] for s in data["sources"]])
    data["draws"] = O.draw_bank(condition)
    if O.bank_digest(data["draws"]) != freeze["draw_bank_sha256"]:
        raise ValueError("Resample identities differ from #423")
    data["condition"] = condition
    with (args.wasz / "docs/research/WASZ_TURNOVER_TIME_001/PER_BREW_BY_TIME.csv").open() as f:
        observed = {(r["brew"], r["clock"], int(r["time_s"])): r for r in csv.DictReader(f)}
    data["observed"] = observed
    data["native"] = {}
    for s in data["sources"]:
        ct, cp, cq, onset, _ = O.native_observation(args.raw / "measurements_time_dependent" / (s["brew"] + ".txt"))
        data["native"][s["brew"]] = (ct, cp, cq, onset)
        for clock, target in O.SNAPSHOTS:
            old = observed[s["brew"], clock, target]
            center = target + (onset if clock == "onset" else 0.)
            p, q, reason = O.paired_window(ct, cp, cq, center)
            if reason != old["reason"] or (reason == "available") != (old["available"] == "True"):
                raise ValueError("Observed availability changed")
            np.testing.assert_allclose([p, q, center - 1, center + 1],
                [float(old[k]) for k in ("pressure_bar", "flow_g_s", "window_start_stable_s", "window_end_stable_s")],
                rtol=1e-12, atol=1e-12)
        for model in MODELS:
            for scope in SCOPES:
                select_parameters(model, scope, s, data)
    return data


def original_d0(data):
    """Original D0 fixture/evaluator replay, distinct from its beverage wrapper."""
    cpu = time.process_time()
    ctx = D0.context_from_fixture(data["fixture"])
    audit = D0.Audit("turnover-original-D0")
    for fold, row in data["d0_rows"].items():
        _, train, held, _ = D0.C.design(ctx.brews.condition, fold)
        actual = D0.E.brew_records(ctx, D0.E.parameters(row["parameters"], "A"), row["Mc_fixed_g"], "A", train, held)
        audit.compare(actual, row["brew_predictions"], fold=fold, field="original_brew_predictions", candidate="A")
    bank = {k: v["parameters"] for k, v in data["d0_rows"].items()}
    values = D0.prediction_arrays(ctx, bank, "A")
    groups = ctx.brews.groups
    scores = dict(endpoint_rmse_g_s=float(np.mean([np.sqrt(np.mean((values["endpoint"][g] - ctx.brews.target[g])**2)) for g in groups])),
                  trace_rmse_g_s=float(np.mean([np.sqrt(values["trace_mse"][g].mean()) for g in groups])))
    audit.compare(scores, read_json(ROOT / "docs/research/JOINT_CLOCK_001/D0_REPLAY.json")["scores"], field="original_scores")
    return dict(model=MODELS[1], case="D0-original-fixture", numerical="original", passed=not audit.mismatches,
                checked_values=audit.checked, mismatch_count=len(audit.mismatches), mismatches=audit.mismatches,
                historical_operator="instantaneous liquid / original clean-end reporting grid",
                cpu_seconds=time.process_time() - cpu, **scores)


def historical_case(job):
    """Evaluate one authenticated historical case at both original steps."""
    model, folder, row = job
    data = _DATA
    if row["scope"] == "held_out":
        source = next(s for s in data["sources"] if s["brew"] == row["brew"])
        observation_times = source["observer_times_s"]
    else:
        p = row["pressure_bar"]
        source = dict(times_s=[0., 100.], pressure_bar=[p, p], predict_times_s=[0., 100.],
                      predict_pressure_bar=[p, p], predict_horizon_s=100.)
        observation_times = np.linspace(0., 100., 1001)
    trace_t = np.array(source.get("trace_times_s", np.linspace(0., 100., 1001)))
    results = []
    for step, dt in (("search", .02), ("fine", .005)):
        cpu = time.process_time()
        maximum = 0.
        error = ""
        try:
            if model == MODELS[0]:
                predictor, lag = J.prepare(source, row["parameters"], "J1", row["mc_fixed_g"], dt)
                prediction = predictor.chemistry(source["predict_horizon_s"])
                observer = predictor.observer(observation_times, lag, accelerate=False)
                q = predictor.scored_flow(trace_t, lag)
                endpoint = float(predictor.scored_flow([100.], lag)[0])
            else:
                prediction = WR.numerical_prediction(source, row["theta"], "Z", [], dt, 256)
                observer = W.observe(prediction, observation_times)
                q = W.scale_prediction(prediction, trace_t)[1]
                endpoint = float(W.scale_prediction(prediction, [100.])[1][0])
            saved = row[step]
            with np.load(Path(folder) / saved["prediction"]["file"], allow_pickle=False) as arrays:
                for name in arrays.files:
                    actual, expected = prediction[name], arrays[name]
                    np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-12)
                    maximum = max(maximum, float(np.max(np.abs(actual - expected))))
            np.testing.assert_allclose(q, saved["trace_g_s"], rtol=1e-12, atol=1e-12)
            np.testing.assert_allclose(endpoint, saved["endpoint_g_s"], rtol=1e-12, atol=1e-12)
            for field in ("detected", "onset_s", "censor_bound_s", "last_timestamp_s", "samples"):
                if observer[field] != saved["observer"][field]:
                    raise ValueError("Historical detector mismatch: " + field)
        except (AssertionError, ValueError, FloatingPointError) as exc:
            error = str(exc)
        results.append(dict(model=model, case=row["key"], numerical=step, passed=not error,
                            maximum_state_absolute_difference=maximum, error=error,
                            historical_operator="instantaneous liquid + separate beverage detector",
                            cpu_seconds=time.process_time() - cpu))
    return results


def reference(args, data):
    """Complete prerequisites; failures block their model, never trigger tuning."""
    results = [original_d0(data)]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for rows in pool.map(historical_case, data["historical"]):
            results.extend(rows)
    status = {m: all(r["passed"] for r in results if r["model"] == m) for m in MODELS}
    driver_cpu = time.process_time() - args.driver_cpu_start
    worker_cpu = sum(r["cpu_seconds"] for r in results if r["case"] != "D0-original-fixture")
    receipt = dict(models=status, records=results, refits=0, input_manifest_sha256=O.digest(OUT / "INPUT_MANIFEST.json"),
                   plan_sha256=O.digest(OUT / "PLAN.md"), code_sha256=O.digest(__file__),
                   driver_cpu_seconds=driver_cpu, worker_cpu_seconds=worker_cpu,
                   cpu_seconds=driver_cpu + worker_cpu)
    previous = args.private / "historical-reproduction.json"
    if previous.exists():
        archive = args.private / "historical-attempts"
        archive.mkdir(exist_ok=True)
        (archive / (O.digest(previous) + ".json")).write_bytes(previous.read_bytes())
    write_json(args.private / "historical-reproduction.json", receipt)
    O.write_csv(args.output / "HISTORICAL_REPRODUCTION.csv", results)
    print(json.dumps(dict(historical_reproduction=status, cases=len(results), core_hours=receipt["cpu_seconds"] / 3600)), flush=True)
    return receipt


def observed_center(onset, clock, offset):
    """Only OBSERVED onset aligns comparison windows; detector results never enter."""
    return float(offset + (onset if clock == "onset" else 0.))


def beverage_observer(prediction, native_t):
    """Sample cumulative beverage mass first, then the inherited derivative/filter."""
    native_t = np.asarray(native_t)
    if native_t[0] < prediction["time"][0] or native_t[-1] > prediction["time"][-1]:
        raise ValueError("Missing native derivative/filter support")
    mass = np.interp(native_t, prediction["time"], prediction["beverage_g"])
    return savgol_filter(np.gradient(mass, native_t), 31, 1)


def measured_replay_case(job):
    """One full-support, pressure-only replay and its fixed native-window observer."""
    model, scope, source = job
    data, args = _DATA, _ARGS
    cpu = time.process_time()
    parameters, mc, fold = select_parameters(model, scope, source, data)
    ct, cp, _, onset = data["native"][source["brew"]]
    theta = np.r_[parameters[:4], mc]
    if source["predict_times_s"][-1] != ct[-1] or source["predict_horizon_s"] != ct[-1]:
        raise ValueError("Forcing must end at genuine clean-course support")
    predictor = J.Prepared(source["predict_times_s"], source["predict_pressure_bar"], theta,
                           "W1" if model == MODELS[0] else "Z", parameters[4:] if model == MODELS[0] else [],
                           DT, 256, float(ct[-1]))
    prediction = predictor.chemistry(float(ct[-1]))
    # The detector keeps its inherited fixed 0–100-s native support. It cannot
    # change any requested observation center or discard an undetected case.
    detector = W.observe(prediction, source["observer_times_s"])
    beverage_flow = beverage_observer(prediction, ct)
    internal = dict(capacity_C_g_s=np.interp(ct, predictor.time, predictor.cap),
                    predicted_liquid_M_g=np.interp(ct, predictor.time, predictor.mass),
                    recovery_R=np.interp(ct, predictor.time, np.exp(-np.exp(-predictor.mass / mc))),
                    instantaneous_liquid_flow_g_s=np.interp(ct, predictor.time, predictor.flow),
                    front_fraction=np.interp(ct, predictor.time, predictor.front))
    rows = []
    for clock, offset in O.SNAPSHOTS:
        center = observed_center(onset, clock, offset)
        old = data["observed"][source["brew"], clock, offset]
        pressure, flow, reason = O.paired_window(ct, cp, beverage_flow, center)
        observed_available = old["available"] == "True"
        if not observed_available:
            flow, reason = np.nan, "observed_" + old["reason"]
        if observed_available:
            np.testing.assert_allclose(pressure, float(old["pressure_bar"]), rtol=1e-12, atol=1e-12)
        row = dict(model=model, scope=scope, brew=source["brew"], nominal_pressure_bar=source["nominal_pressure_bar"],
                   fold=fold, mc_g=mc, clock=clock, time_s=offset, window_start_stable_s=center-1.,
                   window_end_stable_s=center+1., observed_onset_stable_s=onset,
                   observed_available=observed_available, available=reason == "available", reason=reason,
                   achieved_pressure_bar=float(old["pressure_bar"]), observed_flow_g_s=float(old["flow_g_s"]),
                   predicted_beverage_flow_g_s=flow)
        for key, values in internal.items():
            row[key] = O.paired_window(ct, cp, values, center)[1] if row["available"] else np.nan
        rows.append(row)
    artifact = args.private / "predictions" / f"{model}_{scope}_{source['brew']}.npz"
    np.savez_compressed(artifact, **{k: v for k, v in prediction.items() if isinstance(v, np.ndarray)},
                        capacity_C_g_s=predictor.cap, recovery_R=np.exp(-np.exp(-predictor.mass / mc)))
    onset_row = dict(model=model, scope=scope, brew=source["brew"], nominal_pressure_bar=source["nominal_pressure_bar"],
                     fold=fold, mc_g=mc, observed_onset_s=onset, predicted_onset_s=detector["onset_s"],
                     detected=detector["detected"], censor_bound_s=detector["censor_bound_s"],
                     detector_samples=detector["samples"], window_alignment="observed_onset")
    receipt = dict(model=model, scope=scope, brew=source["brew"], parameters=parameters.tolist(), mc_g=mc,
                   artifact=artifact.name, sha256=O.digest(artifact), cpu_seconds=time.process_time() - cpu,
                   dt=DT, cells=256)
    return rows, onset_row, receipt


def unavailable_case(job, reason):
    """Keep every intended window and detector row when a model is unavailable."""
    model, scope, source = job
    rows = []
    for clock, offset in O.SNAPSHOTS:
        old = _DATA["observed"][source["brew"], clock, offset]
        rows.append(dict(model=model, scope=scope, brew=source["brew"], nominal_pressure_bar=source["nominal_pressure_bar"],
                         clock=clock, time_s=offset, observed_available=old["available"] == "True",
                         available=False, reason=reason, achieved_pressure_bar=float(old["pressure_bar"]),
                         observed_flow_g_s=float(old["flow_g_s"]), predicted_beverage_flow_g_s=np.nan))
    onset = dict(model=model, scope=scope, brew=source["brew"], nominal_pressure_bar=source["nominal_pressure_bar"],
                 observed_onset_s=source["observed_onset_for_scoring_only_s"], predicted_onset_s=None,
                 detected=None, prediction_available=False, reason=reason, window_alignment="observed_onset")
    return rows, onset, dict(model=model, scope=scope, brew=source["brew"], artifact=None,
                            sha256=None, cpu_seconds=0., unavailable_reason=reason)


def replay_case(job):
    """Preserve unavailable predictions explicitly, never as zeros/non-detections."""
    cpu = time.process_time()
    try:
        rows, onset, record = measured_replay_case(job)
        onset.update(prediction_available=True, reason="available")
        return rows, onset, record
    except (ValueError, FloatingPointError) as exc:
        rows, onset, record = unavailable_case(job, "prediction_unavailable")
        record.update(cpu_seconds=time.process_time() - cpu, error=str(exc))
        return rows, onset, record


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("phase", choices=("reference", "replay", "report"))
    for name in ("ewp", "raw", "native", "screen", "joint", "wasz", "private"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--output", type=Path, default=OUT)
    p.add_argument("--workers", type=int, default=4)
    return p


def main():
    global _DATA, _ARGS
    args = parser().parse_args()
    args.driver_cpu_start = time.process_time()
    for destination in (args.output.resolve(), args.private.resolve()):
        for protected in (args.ewp, args.raw, args.native, args.screen, args.joint, args.wasz):
            protected = protected.resolve()
            if destination == protected or protected in destination.parents:
                raise ValueError("Output overlaps historical evidence")
    if ROOT == args.private.resolve() or ROOT in args.private.resolve().parents:
        raise ValueError("Private output must stay outside Git")
    args.output.mkdir(parents=True, exist_ok=True)
    args.private.mkdir(parents=True, exist_ok=True)
    _ARGS, _DATA = args, load_inputs(args)
    if args.phase == "reference":
        reference(args, _DATA)
        return
    receipt = read_json(args.private / "historical-reproduction.json")
    if (receipt["input_manifest_sha256"] != O.digest(OUT / "INPUT_MANIFEST.json") or
            receipt["plan_sha256"] != O.digest(OUT / "PLAN.md") or receipt["code_sha256"] != O.digest(__file__)):
        raise ValueError("Historical check belongs to different inputs/plan/code")
    if args.phase == "replay":
        if (args.private / "replay-index.json").exists():
            raise ValueError("Preserve existing replay; use report or a fresh private directory")
        (args.private / "predictions").mkdir(exist_ok=True)
        jobs = [(m, s, b) for m in MODELS if receipt["models"][m] for s in SCOPES for b in _DATA["sources"]]
        rows, onsets, records = [], [], []
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for observations, onset, record in pool.map(replay_case, jobs):
                rows.extend(observations)
                onsets.append(onset)
                records.append(record)
        for model in MODELS:
            if not receipt["models"][model]:
                for scope in SCOPES:
                    for source in _DATA["sources"]:
                        missing, onset, record = unavailable_case((model, scope, source), "historical_reproduction_failed")
                        rows.extend(missing)
                        onsets.append(onset)
                        records.append(record)
        O.write_csv(args.private / "attempted-windows.csv", rows)
        O.write_csv(args.output / "DETECTOR_ONSETS.csv", onsets)
        driver_cpu = time.process_time() - args.driver_cpu_start
        worker_cpu = sum(r["cpu_seconds"] for r in records)
        write_json(args.private / "replay-index.json", dict(records=records, models=receipt["models"],
            cpu_seconds=driver_cpu + worker_cpu, driver_cpu_seconds=driver_cpu, worker_cpu_seconds=worker_cpu, dt=DT, cells=256,
            windows_sha256=O.digest(args.private / "attempted-windows.csv"), code_sha256=O.digest(__file__),
            input_manifest_sha256=O.digest(OUT / "INPUT_MANIFEST.json"), plan_sha256=O.digest(OUT / "PLAN.md")))
        print(json.dumps(dict(replayed=len(records), windows=len(rows), core_hours=sum(r["cpu_seconds"] for r in records)/3600)), flush=True)
    from .turnover_time_replay_001_report import report
    report(args, _DATA)


if __name__ == "__main__":
    main()

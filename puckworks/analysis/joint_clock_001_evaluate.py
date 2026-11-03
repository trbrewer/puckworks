"""Re-evaluate frozen joint fits at both steps; never optimize parameters."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import json
import math
import multiprocessing
from pathlib import Path
import time

import numpy as np

from . import joint_clock_001 as J
from . import joint_clock_001_run as R
from . import wetting_screen_001 as W

_DATA = None
_ARGS = None


def arm_name(model, weight):
    return f"{model}_lambda-{weight:g}"


def evaluate_case(args, data, fit_path, source, scope):
    fit = json.loads(fit_path.read_text())
    if fit["identity"] != R.identity():
        raise ValueError("Frozen fitting code or protocol changed")
    model, weight = fit["model"], fit["weight"]
    arm = arm_name(model, weight)
    name = source.get("brew", f"constant-{source['nominal_pressure_bar']:g}")
    key = scope+"_"+arm+"_"+name
    folder = args.work/"predictions"
    folder.mkdir(exist_ok=True)
    metadata = folder/(key+".json")
    identity = dict(fit_sha256=R.R.digest(fit_path), fit_identity=fit["identity"],
        evaluator_sha256=R.R.digest(Path(__file__)),
        source_input_sha256=R.R.digest(args.native/"source_inputs.json"))
    if metadata.exists():
        row = json.loads(metadata.read_text())
        if row["identity"] != identity:
            raise ValueError("Frozen prediction identity changed")
        for numerical in ("fine", "search"):
            p = row[numerical]["prediction"]
            if R.R.digest(folder/p["file"]) != p["sha256"]:
                raise ValueError("Frozen prediction bytes changed")
        return row
    expected_fold = "DESCRIPTIVE_ALL" if scope == "descriptive" else R.label(source["nominal_pressure_bar"])
    if fit["fold"] != expected_fold or fit["mc_fixed_g"] != data["bank"][expected_fold][4]:
        raise ValueError("Wrong outer-fold fitted vector or Mc")
    if scope == "held_out" and source["brew"] in fit["training_brews"]:
        raise ValueError("Held-out brew appeared in training")
    observations = source.get("observer_times_s", np.linspace(0., 100., 1001))
    trace_times = np.array(source.get("trace_times_s", np.linspace(0., 100., 1001)))
    start, cpu = time.perf_counter(), time.process_time()
    row = dict(key=key, arm=arm, model=model, weight=weight, scope=scope,
        brew=source.get("brew"), pressure_bar=source["nominal_pressure_bar"],
        fold=expected_fold, parameters=fit["parameters"], mc_fixed_g=fit["mc_fixed_g"],
        identity=identity, native_qualification_failed=source.get("native_qualification_failed"))
    predictions = {}
    for numerical, dt in (("search", .02), ("fine", .005)):
        predictor, lag = J.prepare(source, fit["parameters"], model, fit["mc_fixed_g"], dt)
        prediction = predictor.chemistry(source["predict_horizon_s"])
        observer = predictor.observer(observations, lag, accelerate=False)
        artifact = R.R.save_prediction(folder/(key+"_"+numerical+".npz"), prediction, lag)
        artifact["front_on_full_support_s"] = predictor.tb if math.isfinite(predictor.tb) else None
        artifact["front_s"] = predictor.tb if predictor.tb <= 100. else None
        artifact["front_right_censored"] = predictor.tb > 100.
        q = predictor.scored_flow(trace_times, lag)
        endpoint = float(predictor.scored_flow([100.], lag)[0])
        summary = dict(prediction=artifact, observer=observer, endpoint_g_s=endpoint,
            unshifted_endpoint_g_s=float(predictor.scored_flow([100.])[0]),
            trace_g_s=q.tolist(), unshifted_trace_g_s=predictor.scored_flow(trace_times).tolist(),
            endpoint_beverage_g=float(W.scale_prediction(prediction, [100.], lag)[0][0]),
            endpoint_liquid_g=float(np.interp(100.-lag, prediction["time"], prediction["liquid_g"], left=0.)),
            endpoint_beverage_minus_liquid_flow_g_s=float(np.interp(100.-lag, prediction["time"],
                np.gradient(prediction["solute_g"], prediction["time"]), left=0.)))
        if scope == "held_out":
            flow, onset = J.loss_components(predictor.scored_flow(source["fit_times_s"], lag),
                source["fit_flow_g_s"], observer, source["observed_onset_for_scoring_only_s"])
            summary["objective_components"] = dict(flow=flow, onset=onset,
                weighted_onset=weight*onset, joint=flow+weight*onset,
                support="D0 observed-onset+2 through clean end; 0.5-s flow mask, fixed 0–100-s detector")
        row[numerical] = summary
        predictions[numerical] = prediction
    fine, coarse = row["fine"], row["search"]
    of, oc = fine["observer"], coarse["observer"]
    row["numerical_comparison"] = dict(label="Frozen fits; 0.005 minus 0.02 s",
        endpoint_difference_g_s=fine["endpoint_g_s"]-coarse["endpoint_g_s"],
        detector_difference_s=of["onset_s"]-oc["onset_s"] if of["detected"] and oc["detected"] else None,
        detection_agrees=of["detected"] == oc["detected"],
        beverage_max_difference_g=float(np.max(np.abs(predictions["search"]["beverage_g"]-
            np.interp(predictions["search"]["time"], predictions["fine"]["time"], predictions["fine"]["beverage_g"])))) )
    row.update(cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start)
    R.R.write_json(metadata, row)
    return row


def evaluate_fit(path):
    args, data = _ARGS, _DATA
    path = Path(path)
    fit = json.loads(path.read_text())
    held = fit["held_condition_bar"]
    if held is not None:
        selected = [s for s in data["sources"] if s["nominal_pressure_bar"] == held]
        scope = "held_out"
    else:
        pressures = sorted({r["nominal_pressure_bar"] for r in data["manifest"]["runs"]
                            if "primary A0" in r["roles"]})
        if len(pressures) != 23:
            raise ValueError("Descriptive pressure grid changed")
        selected = [dict(nominal_pressure_bar=p, predict_times_s=[0., 100.],
            predict_pressure_bar=[p, p], predict_horizon_s=100.) for p in pressures]
        scope = "descriptive"
    rows = [evaluate_case(args, data, path, s, scope) for s in selected]
    print(json.dumps(dict(evaluated_fit=fit["key"], cases=len(rows))), flush=True)
    return [dict(key=r["key"], cpu_seconds=r["cpu_seconds"],
        metadata_sha256=R.R.digest(args.work/"predictions"/(r["key"]+".json"))) for r in rows]


def main():
    global _DATA, _ARGS
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp", "native", "raw", "screen", "work"):
        parser.add_argument("--"+flag, type=Path, required=True)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--available", action="store_true", help="Evaluate completed frozen fits; report coverage explicitly")
    _ARGS = args = parser.parse_args()
    _DATA = R.load_data(args)
    qualifications = {r["brew"]: not r["balances_and_bounds_qualified"]
        for r in _DATA["manifest"]["runs"] if r.get("brew") and "primary A1" in r["roles"]}
    for s in _DATA["sources"]:
        s["native_qualification_failed"] = qualifications[s["brew"]]
    paths = sorted((args.work/"fits").glob("*.json"))
    if not args.available and len(paths) != 144:
        raise ValueError("Expected all 144 frozen fits before complete reporting")
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("fork")) as pool:
        futures = [pool.submit(evaluate_fit, str(p)) for p in paths]
        rows = [r for f in as_completed(futures) for r in f.result()]
    R.R.write_json(args.work/"EVALUATION_INDEX.json", dict(records=rows, fits_available=len(paths),
        fits_intended=144, cases_available=len(rows), cases_intended=12*(56+23),
        cpu_seconds=sum(r["cpu_seconds"] for r in rows), evaluator_sha256=R.R.digest(Path(__file__))))


if __name__ == "__main__":
    main()

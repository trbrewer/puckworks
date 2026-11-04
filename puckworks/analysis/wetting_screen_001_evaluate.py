"""Freeze predictions before reporting; this module never optimizes parameters."""
import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from . import wetting_screen_001 as W
from . import wetting_screen_001_run as R


def evaluate_case(args, source, theta, contexts, arm, fit, scope, qualification):
    name = source.get("brew", f"constant-{source['nominal_pressure_bar']:g}")
    key = scope+"_"+arm+"_"+name
    folder = args.work/"predictions"
    folder.mkdir(exist_ok=True)
    metadata = folder/(key+".json")
    identity = dict(predictor_sha256=R.digest(Path(W.__file__)),
                    evaluator_sha256=R.digest(Path(__file__)),
                    protocol_sha256=R.digest(R.OUT/"PLAN.md"),
                    fit_sha256=R.digest(fit) if fit else None)
    if metadata.exists():
        result = json.loads(metadata.read_text())
        if result["identity"] != identity:
            raise ValueError("Frozen prediction identity changed")
        for label in ("fine", "search"):
            p = result[label]["prediction"]
            if R.digest(folder/p["file"]) != p["sha256"]:
                raise ValueError("Frozen prediction bytes changed")
        return result
    fitted = json.loads(fit.read_text()) if fit else None
    parameters = fitted["parameters"] if fitted else []
    if fitted and fitted["theta_for_every_training_and_held_brew"] != list(theta):
        raise ValueError("Evaluation does not use the outer fold's tuple")
    dt = fitted["dt"] if fitted else .02
    cells = fitted["cells"] if fitted else 256
    lag = parameters[2] if arm == "W2T" else 0.
    observations = contexts[source["brew"]] if scope == "held_out" else np.linspace(0, 100, 1001)
    trace_times = np.array(source.get("trace_times_s", np.linspace(0, 100, 1001)))
    start, cpu = time.perf_counter(), time.process_time()
    result = dict(key=key, arm=arm, scope=scope, brew=source.get("brew"),
                  pressure_bar=source["nominal_pressure_bar"], theta=list(theta),
                  parameters=parameters, lag_s=lag, identity=identity,
                  native_qualification_failed=qualification,
                  observation_timestamp_sha256=__import__("hashlib").sha256(
                      np.asarray(observations, dtype="<f8").tobytes()).hexdigest())
    predictions = {}
    for label, step in (("search", dt), ("fine", .005)):
        prediction = R.numerical_prediction(source, theta, arm, parameters, step, cells)
        predictions[label] = prediction
        observer = W.observe(prediction, observations, lag)
        _, flow = W.scale_prediction(prediction, trace_times, lag)
        _, endpoint = W.scale_prediction(prediction, [100.], lag)
        result[label] = dict(
            prediction=R.save_prediction(folder/(key+"_"+label+".npz"), prediction, lag),
            observer=observer, endpoint_g_s=float(endpoint[0]),
            unshifted_endpoint_g_s=float(prediction["bed_flow_g_s"][-1]),
            trace_g_s=flow.tolist(),
            unshifted_trace_g_s=np.interp(trace_times, prediction["time"], prediction["bed_flow_g_s"]).tolist(),
            endpoint_beverage_g=float(W.scale_prediction(prediction, [100.], lag)[0][0]),
            endpoint_liquid_g=float(np.interp(100.-lag, prediction["time"], prediction["liquid_g"], left=0.)),
            endpoint_beverage_minus_liquid_flow_g_s=float(np.interp(
                100.-lag, prediction["time"], np.gradient(prediction["solute_g"], prediction["time"]), left=0.)))
    fine, coarse = predictions["fine"], predictions["search"]
    obs1, obs0 = result["fine"]["observer"], result["search"]["observer"]
    result["numerical_comparison"] = dict(
        label="Frozen parameters; 0.005-s minus 0.02-s, same 256-cell R0 discretization",
        beverage_max_difference_g=float(np.max(np.abs(coarse["beverage_g"]-
            np.interp(coarse["time"], fine["time"], fine["beverage_g"])))),
        endpoint_difference_g_s=result["fine"]["endpoint_g_s"]-result["search"]["endpoint_g_s"],
        detector_difference_s=obs1["onset_s"]-obs0["onset_s"] if obs1["detected"] and obs0["detected"] else None,
        detection_agrees=obs1["detected"] == obs0["detected"],
        front_difference_s=(fine["front_s"]-coarse["front_s"] if
            math.isfinite(fine["front_s"]) and math.isfinite(coarse["front_s"]) else None))
    result.update(cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start)
    R.write_json(metadata, result)
    print(json.dumps(dict(evaluated=key, onset=result["fine"]["observer"]["onset_s"],
                          endpoint=result["fine"]["endpoint_g_s"])), flush=True)
    return result


def evaluate(args):
    sources, bank, contexts, manifest = R.load_data(args)
    records = []
    by_brew = {r["brew"]: r for r in manifest["runs"] if "primary A1" in r["roles"] and r.get("brew")}
    pressures = sorted({r["nominal_pressure_bar"] for r in manifest["runs"] if
                        "primary A0" in r["roles"]})
    if len(pressures) != 23:
        raise ValueError("Descriptive sweep differs from the retained 23 pressures")
    for arm in args.arms:
        for source in sources:
            held = source["nominal_pressure_bar"]
            fit = args.work/"fits"/f"HYD-LOCO-{held:.1f}_{arm}.json" if arm in ("W1", "W2", "W2T") else None
            records.append(evaluate_case(args, source, W.freeze_tuple(bank, held), contexts, arm,
                fit, "held_out", not by_brew[source["brew"]]["balances_and_bounds_qualified"]))
        for pressure in pressures:
            source = dict(nominal_pressure_bar=pressure, times_s=[0., 100.], pressure_bar=[pressure]*2)
            fit = args.work/"fits"/f"DESCRIPTIVE_ALL_{arm}.json" if arm in ("W1", "W2", "W2T") else None
            records.append(evaluate_case(args, source, W.freeze_tuple(bank, None), contexts,
                                         arm, fit, "descriptive", None))
    result = dict(records=[dict(key=r["key"], metadata_sha256=R.digest(
                        args.work/"predictions"/(r["key"]+".json"))) for r in records],
                  arms=args.arms, cpu_seconds=sum(r["cpu_seconds"] for r in records),
                  r0=asdict(W.R0()), python=platform.python_version(),
                  numpy=np.__version__, scipy=scipy.__version__,
                  source_sha256=R.digest(args.native/"source_inputs.json"))
    R.write_json(args.work/("PREDICTIONS_"+"_".join(args.arms)+".json"), result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp", "native", "raw", "work"):
        parser.add_argument("--"+flag, type=Path, required=True)
    parser.add_argument("--arms", nargs="+", choices=W.ARMS, default=list(W.ARMS))
    evaluate(parser.parse_args())


if __name__ == "__main__":
    main()

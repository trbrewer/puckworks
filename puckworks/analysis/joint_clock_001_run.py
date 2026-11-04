"""Frozen joint-clock fitting orchestration; predictions and reporting are separate."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
from scipy.optimize import minimize
from scipy.stats import qmc

from . import joint_clock_001 as J
from . import pressure_peak_stage_d0 as D0
from . import wetting_screen_001 as W
from . import wetting_screen_001_run as R

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"docs/research/JOINT_CLOCK_001"
SEED = 20261103
_DATA = None


def label(held):
    return "DESCRIPTIVE_ALL" if held is None else f"HYD-LOCO-{held:.1f}"


def key(model, weight, held):
    return f"{model}_lambda-{weight:g}_{label(held)}"


def identity():
    return {str(p.relative_to(ROOT)): R.digest(p) for p in
            (OUT/"PLAN.md", Path(__file__), Path(J.__file__), Path(W.__file__))}


def load_data(args):
    sources, bank, contexts, manifest = R.load_data(args)
    csv.field_size_limit(100_000_000)
    with (ROOT/"docs/research/PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv").open() as stream:
        raw = next(r for r in csv.DictReader(stream) if r["record_type"] == "inputs")
    fixture = {}
    for k, v in raw.items():
        if v:
            try:
                fixture[k] = json.loads(v)
            except (ValueError, TypeError):
                fixture[k] = v
    if fixture["brew_ids"] != [s["brew"] for s in sources]:
        raise ValueError("D0 and FORM_A cohort order differs")
    for i, s in enumerate(sources):
        original = args.raw/"measurements_time_dependent"/(s["brew"]+".txt")
        ct, cp, _, _ = R.B0.clean_course(*R.B0.raw_trace(original)[:3])
        mask = np.asarray(fixture["fit_mask"][i], dtype=bool)
        s["fit_times_s"] = np.asarray(fixture["fit_times_s"])[mask]
        s["fit_flow_g_s"] = np.asarray(fixture["fit_observed_flow"][i])[mask]
        if not np.array_equal(mask, (np.asarray(fixture["fit_times_s"]) >=
                s["observed_onset_for_scoring_only_s"]+2.) &
                (np.asarray(fixture["fit_times_s"]) <= ct[-1])):
            raise ValueError("Training mask differs from the inherited observed-onset rule")
        # Preserve FORM_A's retained pressure interpolation through 100 s;
        # append original clean-course samples to cover D0's longer fit mask.
        s["predict_times_s"] = np.r_[s["times_s"], ct[ct > 100.]]
        s["predict_pressure_bar"] = np.r_[s["pressure_bar"], cp[ct > 100.]]
        s["predict_horizon_s"] = float(ct[-1])
        s["observer_times_s"] = contexts[s["brew"]]
    timing = {}
    for path in (args.screen/"fits").glob("*.json"):
        row = json.loads(path.read_text())
        timing[(row["fold"], row["arm"])] = row
        if row["theta_for_every_training_and_held_brew"] != bank[row["fold"]]:
            raise ValueError("Timing start belongs to another outer flow tuple")
    if len(timing) != 36:
        raise ValueError("Incomplete historical timing bank")
    return dict(sources=sources, bank=bank, contexts=contexts, manifest=manifest,
                timing=timing, fixture=fixture)


def starts(data, model, held):
    fold = label(held)
    flow = data["bank"][fold][:4]
    if model == "J0":
        saved = [("matching_D0", flow)]
    elif model == "J1":
        tau = data["timing"][(fold, "W1")]["parameters"][0]
        saved = [("matching_D0_W1", [*flow, tau]), ("D0_zero_delay", [*flow, 0.])]
    else:
        w2 = data["timing"][(fold, "W2")]["parameters"]
        w2t = data["timing"][(fold, "W2T")]["parameters"]
        saved = [("matching_D0_W2T", [*flow, *w2t]),
                 ("matching_D0_W2", [*flow, *w2, 0.]),
                 ("matching_D0_W2T_zero_lag", [*flow, *w2t[:2], 0.])]
    lo, hi = J.bounds(model)
    finite_hi = hi.copy()
    finite_hi[2] = 8.
    grid = qmc.scale(qmc.LatinHypercube(len(lo), seed=SEED).random(16), lo, finite_hi)
    return [(name, J.coordinates(p, model).tolist()) for name, p in saved]+[
        (f"space_filling_{i:02d}", z.tolist()) for i, z in enumerate(grid)]


class Objective:
    """Training-only sources; all use the outer fold's fixed Mc and common vector."""
    def __init__(self, data, model, weight, held, accelerate=True):
        self.sources = [s for s in data["sources"] if held is None or s["nominal_pressure_bar"] != held]
        self.mc = data["bank"][label(held)][4]
        self.model, self.weight, self.accelerate = model, weight, accelerate
        self.conditions = sorted({s["nominal_pressure_bar"] for s in self.sources})
        self.groups = [np.array([i for i, s in enumerate(self.sources) if s["nominal_pressure_bar"] == p])
                       for p in self.conditions]
        self.last_key, self.prepared = None, None
        self.trials = []
        self.best = None
        self.column_calls = 0

    def __call__(self, coordinates):
        parameters = J.physical(coordinates, self.model)
        bed_key = tuple(parameters[:-1] if self.model == "J2" else parameters)
        if bed_key != self.last_key:
            self.prepared = [J.prepare(s, parameters, self.model, self.mc)[0] for s in self.sources]
            self.last_key = bed_key
        lag = parameters[-1] if self.model == "J2" else 0.
        parts, detected = [], []
        for source, predictor in zip(self.sources, self.prepared):
            before = predictor.column_calls
            observer = predictor.observer(source["observer_times_s"], lag, self.accelerate)
            self.column_calls += predictor.column_calls-before
            q = predictor.scored_flow(source["fit_times_s"], lag)
            parts.append(J.loss_components(q, source["fit_flow_g_s"], observer,
                                          source["observed_onset_for_scoring_only_s"]))
            detected.append(observer["detected"])
        by_condition = np.array([np.asarray(parts)[g].mean(axis=0) for g in self.groups])
        flow, onset = by_condition.mean(axis=0)
        value = float(flow+self.weight*onset)
        if not math.isfinite(value):
            raise ValueError("Unavailable objective; never convert missing evidence to censoring")
        row = dict(coordinates=list(map(float, coordinates)), parameters=parameters.tolist(),
            objective=value, flow_component=float(flow), onset_component=float(onset),
            weighted_onset_component=float(self.weight*onset), detected=sum(detected),
            condition_components=[dict(pressure_bar=p, flow=float(v[0]), onset=float(v[1]),
                weighted_onset=float(self.weight*v[1]), detected=int(np.sum(np.asarray(detected)[g])),
                brews=len(g)) for p, v, g in zip(self.conditions, by_condition, self.groups)])
        self.trials.append(row)
        if self.best is None or row["objective"] < self.best["objective"]:
            self.best = row
        return value


def run_fit(job):
    model, weight, held, work = job
    data = _DATA
    work = Path(work)
    name = key(model, weight, held)
    path = work/"fits"/(name+".json")
    ident = identity()
    if path.exists():
        saved = json.loads(path.read_text())
        if saved["identity"] != ident:
            raise ValueError("Cannot resume with changed fit source or protocol")
        return dict(key=name, cpu_seconds=saved["cpu_seconds"], resumed=True)
    objective = Objective(data, model, weight, held)
    schedule = starts(data, model, held)
    lo, hi = J.bounds(model)
    start, cpu = time.perf_counter(), time.process_time()
    outcomes = []
    progress = work/"progress"/(name+".json")
    try:
        for number, (origin, z) in enumerate(schedule):
            objective(z)
            result = minimize(objective, z, method="Powell", bounds=list(zip(lo, hi)),
                options=dict(xtol=1e-4, ftol=1e-7, maxiter=np.inf, maxfev=np.inf))
            outcomes.append(dict(start=origin, initial_coordinates=z, success=bool(result.success),
                message=str(result.message), nfev=int(result.nfev), objective=float(result.fun),
                parameters=J.physical(result.x, model).tolist()))
            R.write_json(progress, dict(key=name, completed_starts=number+1, total_starts=len(schedule),
                best=objective.best, evaluations=len(objective.trials),
                cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start))
            print(json.dumps(dict(fit=name, start=number+1, total=len(schedule),
                best=objective.best["objective"], evaluations=len(objective.trials))), flush=True)
        best = objective.best
        ties = [r for r in objective.trials if r["objective"] == best["objective"]]
        vals = np.array([r["parameters"] for r in ties])
        result = dict(key=name, model=model, weight=weight, primary_weight=weight == 1.,
            fold=label(held), held_condition_bar=held, mc_fixed_g=objective.mc,
            training_brews=[s["brew"] for s in objective.sources], **best,
            starts=outcomes, trials=objective.trials, identity=ident,
            equal_minimum_count=len(ties), equal_minimum_ranges=np.c_[vals.min(axis=0), vals.max(axis=0)].tolist(),
            distance_to_bounds=[float(min(z-l, h-z)) for z, l, h in zip(best["coordinates"], lo, hi)],
            column_calls=objective.column_calls, dt=.02, cells=256,
            cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start,
            status="complete", identifiability="Retain competing starts and sampled ties; no uniqueness claim")
        R.write_json(path, result)
    except BaseException as exc:
        R.write_json(work/"failures"/(name+".json"), dict(key=name, identity=ident,
            status="failed", error=repr(exc), starts=outcomes, trials=objective.trials,
            cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start))
        raise
    return dict(key=name, cpu_seconds=result["cpu_seconds"], resumed=False)


def replay(data, work):
    start, cpu = time.perf_counter(), time.process_time()
    ctx = D0.context_from_fixture(data["fixture"])
    bank = {fold: dict(zip(("a_g_s_bar", "Pstar_bar", "n", "Pd_bar", "Mc_fixed_g"), v))
            for fold, v in data["bank"].items()}
    values = D0.prediction_arrays(ctx, bank, "A")
    groups = [np.flatnonzero(ctx.brews.condition == p) for p in W.NOMINAL]
    scores = {"endpoint_rmse_g_s": float(np.mean([np.sqrt(np.mean(
        (values["endpoint"][g]-ctx.brews.target[g])**2)) for g in groups])),
        "trace_rmse_g_s": float(np.mean([np.sqrt(values["trace_mse"][g].mean()) for g in groups]))}
    result = dict(scores=scores, target_historical_endpoint_g_s=.153001,
        target_historical_trace_g_s=.254185, trace_support="D0 own clean-end 0.1-s reporting grid",
        original_fit_support="D0 observed-onset+2 through clean end, 0.5-s duration-normalized flow-only",
        mc_bank=data["bank"], refits=0, predictor="unchanged C3e/D0 helpers and saved original fixture",
        identity=identity(), cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start)
    R.write_json(work/"D0_REPLAY.json", result)
    return result


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("command", choices=["replay", "fit"])
    for flag in ("ewp", "native", "raw", "screen", "work"):
        p.add_argument("--"+flag, type=Path, required=True)
    p.add_argument("--workers", type=int, default=64)
    return p


def main():
    global _DATA
    args = parser().parse_args()
    args.work.mkdir(parents=True, exist_ok=True)
    for name in ("fits", "progress", "failures"):
        (args.work/name).mkdir(exist_ok=True)
    _DATA = load_data(args)
    if args.command == "replay":
        print(json.dumps(replay(_DATA, args.work)), flush=True)
        return
    jobs = [(m, w, h, str(args.work)) for h in [None, *W.NOMINAL.tolist()]
            for w in J.WEIGHTS for m in J.MODELS]
    schedule = dict(identity=identity(), jobs=[key(m,w,h) for m,w,h,_ in jobs],
        starts={key(m,w,h): starts(_DATA,m,h) for m,w,h,_ in jobs},
        weights=list(J.WEIGHTS), primary_weight=1., fit_step=.02, score_step=.005,
        count=144, source_sha256=R.digest(args.native/"source_inputs.json"),
        timing_bank_sha256={p.name:R.digest(p) for p in (args.screen/"fits").glob("*.json")})
    freeze = args.work/"FIT_FREEZE.json"
    if freeze.exists() and json.loads(freeze.read_text()) != schedule:
        raise ValueError("Frozen fit contract changed")
    R.write_json(freeze, schedule)
    import multiprocessing
    with ProcessPoolExecutor(max_workers=args.workers, mp_context=multiprocessing.get_context("fork")) as pool:
        pending = [pool.submit(run_fit, job) for job in jobs]
        results = [f.result() for f in as_completed(pending)]
    R.write_json(args.work/"FIT_EXECUTION.json", dict(results=results,
        cpu_seconds=sum(r["cpu_seconds"] for r in results), python=platform.python_version(),
        workers=args.workers, identity=identity()))


if __name__ == "__main__":
    main()

"""Resume interrupted scheduled starts while enforcing the declared bounds.

Powell's floating-point extrapolation can cross an exact bound by roundoff.
This wrapper projects such coordinates onto the already declared domain. It
does not change any model, objective, start, tolerance or observation support.
The original fit source and all successful/failed attempt records stay intact.
"""
import argparse
import json
from pathlib import Path
import time

import numpy as np
from scipy.optimize import minimize

from . import joint_clock_001 as J
from . import joint_clock_001_run as R


class BoundedObjective(R.Objective):
    def __init__(self, data, model, weight, held, previous):
        super().__init__(data, model, weight, held)
        self.lo, self.hi = J.bounds(model)
        self.trials = previous
        self.best = min(previous, key=lambda r: r["objective"]) if previous else None
        self.cache = {tuple(r["coordinates"]): r["objective"] for r in previous}
        self.cache_hits = 0
        self.projections = []

    def __call__(self, coordinates):
        z = np.asarray(coordinates, dtype=float)
        if not np.isfinite(z).all():
            raise ValueError("Nonfinite optimizer coordinates remain unavailable")
        bounded = np.clip(z, self.lo, self.hi)
        if not np.array_equal(z, bounded):
            self.projections.append(dict(requested=z.tolist(), evaluated=bounded.tolist()))
        key = tuple(bounded)
        if key in self.cache:
            self.cache_hits += 1
            return self.cache[key]
        value = super().__call__(bounded)
        self.cache[key] = value
        return value


def resume_one(data, work, path):
    failed = json.loads(path.read_text())
    if failed["identity"] != R.identity():
        raise ValueError("Original fitting protocol/source changed")
    name = failed["key"]
    target = work/"fits"/(name+".json")
    if target.exists():
        return
    freeze = json.loads((work/"FIT_FREEZE.json").read_text())
    if name not in freeze["jobs"]:
        raise ValueError("Attempt is outside the frozen schedule")
    model, tail = name.split("_lambda-")
    weight_text, fold = tail.split("_", 1)
    weight = float(weight_text)
    held = None if fold == "DESCRIPTIVE_ALL" else float(fold.removeprefix("HYD-LOCO-"))
    schedule = R.starts(data, model, held)
    if [[n, z] for n, z in schedule] != freeze["starts"][name]:
        raise ValueError("Continuation start schedule changed")
    outcomes = failed["starts"].copy()
    for outcome, (origin, z) in zip(outcomes, schedule):
        if outcome["start"] != origin or outcome["initial_coordinates"] != z:
            raise ValueError("Completed start does not match the frozen prefix")
    objective = BoundedObjective(data, model, weight, held, failed["trials"].copy())
    cpu, start = time.process_time(), time.perf_counter()
    try:
        for number in range(len(outcomes), len(schedule)):
            origin, z = schedule[number]
            objective(z)
            result = minimize(objective, z, method="Powell", bounds=list(zip(objective.lo, objective.hi)),
                options=dict(xtol=1e-4, ftol=1e-7, maxiter=np.inf, maxfev=np.inf))
            final = np.clip(result.x, objective.lo, objective.hi)
            outcomes.append(dict(start=origin, initial_coordinates=z, success=bool(result.success),
                message=str(result.message), nfev=int(result.nfev), objective=float(result.fun),
                parameters=J.physical(final, model).tolist()))
            R.R.write_json(work/"progress"/(name+".json"), dict(key=name,
                completed_starts=number+1, total_starts=len(schedule), best=objective.best,
                evaluations=len(objective.trials), cpu_seconds=time.process_time()-cpu,
                wall_seconds=time.perf_counter()-start, continuation=True))
            print(json.dumps(dict(resumed_fit=name, start=number+1, total=len(schedule))), flush=True)
        best = objective.best
        ties = [r for r in objective.trials if r["objective"] == best["objective"]]
        vals = np.array([r["parameters"] for r in ties])
        result = dict(key=name, model=model, weight=weight, primary_weight=weight == 1.,
            fold=fold, held_condition_bar=held, mc_fixed_g=objective.mc,
            training_brews=[s["brew"] for s in objective.sources], **best,
            starts=outcomes, trials=objective.trials, identity=R.identity(),
            equal_minimum_count=len(ties), equal_minimum_ranges=np.c_[vals.min(axis=0), vals.max(axis=0)].tolist(),
            distance_to_bounds=[float(min(z-l, h-z)) for z,l,h in
                                zip(best["coordinates"], objective.lo, objective.hi)],
            column_calls=objective.column_calls, dt=.02, cells=256,
            cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start,
            status="complete", identifiability="Retain competing starts and sampled ties; no uniqueness claim",
            continuation=dict(source_sha256=R.R.digest(Path(__file__)), failed_file=path.name,
                failed_sha256=R.R.digest(path), retained_completed_starts=len(failed["starts"]),
                cached_evaluations=objective.cache_hits, bound_projections=objective.projections,
                cpu_scope="Continuation only; original failed-attempt CPU recorded separately"))
        R.R.write_json(target, result)
    except BaseException as exc:
        folder = work/"continuation_failures"
        folder.mkdir(exist_ok=True)
        R.R.write_json(folder/(name+".json"), dict(key=name, status="failed", error=repr(exc),
            starts=outcomes, trials=objective.trials, projections=objective.projections,
            cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-start))
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp", "native", "raw", "screen", "work"):
        parser.add_argument("--"+flag, type=Path, required=True)
    parser.add_argument("--key", required=True)
    args = parser.parse_args()
    data = R.load_data(args)
    resume_one(data, args.work, args.work/"failures"/(args.key+".json"))


if __name__ == "__main__":
    main()

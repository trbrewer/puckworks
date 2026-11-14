"""Authenticate, replay, and execute exactly 48 LC-J1 fits / 912 starts."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import gzip
import json
import multiprocessing
from pathlib import Path
import platform
import time

import numpy as np
from scipy.optimize import minimize
from scipy.stats import qmc

from . import joint_clock_001 as J
from . import joint_clock_001_run as R
from . import lc_joint_transfer_001 as L

ROOT = R.ROOT
OUT = ROOT/"docs/research/LC_JOINT_TRANSFER_001"
_DATA = None
_ARGS = None


def table(path):
    csv.field_size_limit(100_000_000)
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def identity():
    paths = [OUT/"PLAN.md", Path(__file__), Path(L.__file__),
             Path(J.__file__), Path(R.__file__), Path(R.W.__file__), Path(L.C.__file__)]
    return {str(p.relative_to(ROOT)): R.R.digest(p) for p in paths}


def load_data(args):
    data = R.load_data(args)
    reference = table(ROOT/"docs/research/JOINT_CLOCK_001/FITS.csv")
    reference = {r["key"]: r for r in reference if r["model"] == "J1"}
    if len(reference) != 48:
        raise ValueError("Incomplete J1 comparator")
    data["reference"] = {}
    for key, compact in reference.items():
        path = args.joint/"fits"/(key+".json")
        if R.R.digest(path) != compact["fit_sha256"]:
            raise ValueError("Saved A-J1 bytes changed")
        row = json.loads(path.read_text())
        if row["identity"] != R.identity():
            raise ValueError("Inherited evaluator/protocol changed")
        held = row["held_condition_bar"]
        expected = [s["brew"] for s in data["sources"] if held is None or s["nominal_pressure_bar"] != held]
        if row["training_brews"] != expected or row["fold"] != R.label(held):
            raise ValueError("A-J1 fold isolation mismatch")
        mc = data["bank"][row["fold"]][4]
        if not (mc == row["mc_fixed_g"] == float(compact["Mc_g"])):
            raise ValueError("A-J1 Mc mismatch")
        # Historical trial histories stay external. Retaining them in every
        # fork would multiply gigabytes of unused Python objects across workers.
        keep = ("key", "parameters", "objective", "identity", "weight", "fold",
                "held_condition_bar", "mc_fixed_g", "training_brews")
        data["reference"][(row["weight"], row["fold"])] = {k: row[k] for k in keep}
    # Read the actual C2 T2-F parameters_by_fold, as in C3E/D0.
    c2path = ROOT/"docs/research/PRESSURE_PEAK_STAGE_C2/RESULT_TABLE.csv"
    c2 = next(r for r in table(c2path) if r.get("candidate") == "T2-F" and r.get("parameters_by_fold"))
    bank = json.loads(c2["parameters_by_fold"])
    provenance = []
    for fold, v in data["bank"].items():
        if v[4] != bank[fold]["Mc_fixed_g"]:
            raise ValueError("C2 fixed Mc mismatch")
        provenance.append(dict(fold=fold, Mc_g=v[4], source=str(c2path.relative_to(ROOT)),
            source_sha256=R.R.digest(c2path), candidate="T2-F", field="parameters_by_fold",
            fold_key=fold, matches_all_four_A_J1_weights=True))
    data["mc_provenance"] = provenance
    c3path = ROOT/"docs/research/PRESSURE_PEAK_STAGE_C3E/RESULT_TABLE.csv"
    selected = [r for r in table(c3path) if r["record_type"] == "fit" and
                r["candidate"] == "LC" and r["fold"] in data["bank"]]
    if len(selected) != 12 or len({r["fold"] for r in selected}) != 12:
        raise ValueError("C3E ordinary LC start bank incomplete or duplicated")
    data["lc_seeds"] = {r["fold"]: json.loads(r["parameters"]) for r in selected}
    for fold, p in data["lc_seeds"].items():
        if p["Mc_fixed_g"] != data["bank"][fold][4] or "OMIT" in fold:
            raise ValueError("C3E start provenance mismatch")
    return data


def starts(data, weight, held):
    fold = R.label(held)
    a = data["reference"][(weight, fold)]["parameters"]
    p = data["lc_seeds"][fold]
    lc = [p[k] for k in ("a_g_s_bar", "Pstar_bar", "n", "Pd_bar", "f")]
    saved = [("matching_A_J1_f0", [*a[:4], 0., a[4]]),
             ("matching_C3E_LC_A_J1_tau0", [*lc, a[4]]),
             ("matching_C3E_LC_zero_tau0", [*lc, 0.])]
    lo, hi = L.bounds()
    hi[2] = 8.
    grid = qmc.scale(qmc.LatinHypercube(6, seed=20261103).random(16), lo, hi)
    return [(name, L.coordinates(p).tolist()) for name, p in saved]+[
        (f"space_filling_{i:02d}", z.tolist()) for i, z in enumerate(grid)]


def replay_one(job):
    weight, held = job
    data, args = _DATA, _ARGS
    ref = data["reference"][(weight, R.label(held))]
    start = time.process_time()
    obj = R.Objective(data, "J1", weight, held)
    value = obj(J.coordinates(ref["parameters"], "J1"))
    np.testing.assert_allclose(value, ref["objective"], rtol=1e-12, atol=0)
    embedded = np.r_[ref["parameters"][:4], 0., ref["parameters"][4]]
    nested = L.objective(data, embedded, weight, held)
    np.testing.assert_allclose(nested["objective"], value, rtol=1e-12, atol=0)
    # Full frozen fine/search predictions are recomputed, then compared with
    # saved scalar scores AND complete retained trace arrays and detector state.
    if held is None:
        pressures = sorted({r["nominal_pressure_bar"] for r in data["manifest"]["runs"] if "primary A0" in r["roles"]})
        sources = [dict(nominal_pressure_bar=p, predict_times_s=[0.,100.],
            predict_pressure_bar=[p,p], predict_horizon_s=100.) for p in pressures]
        scope = "descriptive"
    else:
        sources = [s for s in data["sources"] if s["nominal_pressure_bar"] == held]
        scope = "held_out"
    from . import joint_clock_001_evaluate as E
    manifest = json.loads((ROOT/"docs/research/JOINT_CLOCK_001/RUN_MANIFEST.json").read_text())
    expected = {r["key"]: r["metadata_sha256"] for r in manifest["predictions"]["records"]}
    diffs, files = [], []
    for s in sources:
        name = s.get("brew", f"constant-{s['nominal_pressure_bar']:g}")
        key = scope+"_"+E.arm_name("J1",weight)+"_"+name
        path = args.joint/"predictions"/(key+".json")
        if R.R.digest(path) != expected[key]:
            raise ValueError("Saved J1 prediction metadata changed")
        saved = json.loads(path.read_text())
        if saved["identity"]["fit_identity"] != R.identity():
            raise ValueError("Saved J1 prediction fit identity differs")
        if saved["identity"]["fit_sha256"] != R.R.digest(args.joint/"fits"/(ref["key"]+".json")):
            raise ValueError("Prediction uses a different comparator")
        for step, dt in (("fine",.005),("search",.02)):
            target = saved[step]
            artifact = args.joint/"predictions"/target["prediction"]["file"]
            if R.R.digest(artifact) != target["prediction"]["sha256"]:
                raise ValueError("Saved J1 prediction arrays changed")
            predictor, lag = J.prepare(s, ref["parameters"], "J1", ref["mc_fixed_g"], dt)
            prediction = predictor.chemistry(s["predict_horizon_s"])
            observer = predictor.observer(s.get("observer_times_s", np.linspace(0,100,1001)), accelerate=False)
            if observer != target["observer"]:
                raise ValueError("A-J1 observer replay differs")
            q = predictor.scored_flow(s.get("trace_times_s", np.linspace(0,100,1001)))
            np.testing.assert_allclose(q, target["trace_g_s"], rtol=1e-12, atol=0)
            np.testing.assert_allclose(predictor.scored_flow([100.])[0],target["endpoint_g_s"],rtol=1e-12,atol=0)
            with np.load(artifact) as arrays:
                for k in arrays.files:
                    np.testing.assert_allclose(prediction[k], arrays[k], rtol=1e-12, atol=0)
            diffs.append(float(np.max(np.abs(q-np.array(target["trace_g_s"])))))
        files.append(dict(key=key, metadata_sha256=R.R.digest(path)))
    return dict(key=ref["key"], saved_objective=ref["objective"], replay_objective=value,
        embedded_LC_f0_objective=nested["objective"], cases=len(sources),
        maximum_trace_difference_g_s=max(diffs), predictions=files,
        cpu_seconds=time.process_time()-start, exact_tolerance="rtol=1e-12, atol=0")


class Objective:
    def __init__(self, data, weight, held):
        self.data, self.weight, self.held = data, weight, held
        self.lo, self.hi = L.bounds()
        self.trials, self.projections, self.cache = [], [], {}
        self.best = None

    def __call__(self, z):
        z = np.asarray(z, dtype=float)
        if not np.isfinite(z).all():
            raise ValueError("Nonfinite coordinates")
        bounded = np.clip(z, self.lo, self.hi)
        if not np.array_equal(z, bounded):
            self.projections.append(dict(requested=z.tolist(), evaluated=bounded.tolist()))
        key = tuple(bounded)
        if key in self.cache:
            return self.cache[key]
        row = L.objective(self.data, L.physical(bounded), self.weight, self.held)
        row["coordinates"] = bounded.tolist()
        self.trials.append(row)
        self.cache[key] = row["objective"]
        if self.best is None or row["objective"] < self.best["objective"]:
            self.best = row
        return row["objective"]


def run_start(job):
    weight, held, number = job
    data, args = _DATA, _ARGS
    name = R.key("LC-J1", weight, held)
    path = args.work/"starts"/(name+f"_{number:02d}.json")
    if path.exists():
        saved = json.loads(path.read_text())
        if saved["identity"] != identity() or saved["status"] != "complete":
            raise ValueError("Cannot reuse changed or failed start")
        return saved
    origin, z = starts(data, weight, held)[number]
    obj = Objective(data, weight, held)
    cpu, wall = time.process_time(), time.perf_counter()
    record = dict(key=name, number=number, start=origin, initial_coordinates=z, identity=identity())
    try:
        record["initial_objective"] = obj(z)
        result = minimize(obj, z, method="Powell", bounds=list(zip(obj.lo,obj.hi)),
            options=dict(xtol=1e-4, ftol=1e-7, maxiter=np.inf, maxfev=np.inf))
        record.update(status="complete", success=bool(result.success), message=str(result.message),
            nfev=int(result.nfev), returned_objective=float(result.fun),
            returned_parameters=L.physical(np.clip(result.x,obj.lo,obj.hi)).tolist())
    except BaseException as exc:
        record.update(status="failed", success=False, error=repr(exc))
    record.update(best=obj.best, evaluations=len(obj.trials), projections=obj.projections,
        cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-wall)
    trials = args.work/"trials"/(path.stem+".json.gz")
    with gzip.open(trials, "wt") as stream:
        json.dump(obj.trials,stream,allow_nan=False,separators=(",",":"))
    record["trials"] = dict(file=trials.name,sha256=R.R.digest(trials))
    R.R.write_json(path,record)
    print(json.dumps(dict(key=name,start=number+1,status=record["status"],
        objective=obj.best["objective"] if obj.best else None,cpu_seconds=record["cpu_seconds"])),flush=True)
    return record


def collect(data,args):
    fits=[]
    for weight, held in jobs():
        name=R.key("LC-J1",weight,held)
        records=[json.loads((args.work/"starts"/(name+f"_{i:02d}.json")).read_text()) for i in range(19)]
        if any(r["status"]!="complete" or r["identity"]!=identity() for r in records):
            raise ValueError("Unfinished/changed scheduled start")
        winner=min(records,key=lambda r:r["best"]["objective"])
        best=winner["best"]
        if best["objective"]>records[0]["initial_objective"]:
            raise ValueError("Candidate worse than feasible f=0 benchmark")
        ref=data["reference"][(weight,R.label(held))]
        row=dict(key=name,model="LC-J1",weight=weight,fold=R.label(held),held_condition_bar=held,
            mc_fixed_g=data["bank"][R.label(held)][4],training_brews=ref["training_brews"],
            **best,winning_start=winner["number"],starts=[r for r in records],identity=identity(),
            cpu_seconds=sum(r["cpu_seconds"] for r in records),status="complete",dt=.02,cells=256)
        R.R.write_json(args.work/"fits"/(name+".json"),row)
        fits.append(dict(key=name,sha256=R.R.digest(args.work/"fits"/(name+".json")),cpu_seconds=row["cpu_seconds"]))
    R.R.write_json(args.work/"FIT_EXECUTION.json",dict(fits=fits,fit_count=48,start_count=912,
        cpu_seconds=sum(r["cpu_seconds"] for r in fits),python=platform.python_version(),
        workers=args.workers,parallelism="independent starts; fixed order in schedule and collected artifacts"))


def jobs():
    return [(w,h) for h in [None,*R.W.NOMINAL.tolist()] for w in J.WEIGHTS]


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=["replay","fit","collect"])
    for flag in ("ewp","native","raw","screen","joint","work"):
        p.add_argument("--"+flag,type=Path,required=True)
    p.add_argument("--workers",type=int,default=96)
    return p


def main():
    global _DATA,_ARGS
    _ARGS=args=parser().parse_args()
    args.work.mkdir(parents=True,exist_ok=True)
    for folder in ("starts","trials","fits"):
        (args.work/folder).mkdir(exist_ok=True)
    _DATA=data=load_data(args)
    R.R.csv_write(OUT/"MC_PROVENANCE.csv",data["mc_provenance"])
    if args.command=="collect":
        collect(data,args)
        return
    if args.command=="replay":
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context("fork")) as pool:
            rows=list(pool.map(replay_one,jobs()))
        R.R.write_json(args.work/"REFERENCE_REPLAY.json",dict(records=rows,identity=identity(),
            cpu_seconds=sum(r["cpu_seconds"] for r in rows),status="reproduced"))
        return
    replay=json.loads((args.work/"REFERENCE_REPLAY.json").read_text())
    if replay["identity"]!=identity() or replay["status"]!="reproduced":
        raise ValueError("Reference must be reproduced before fitting")
    schedule=dict(identity=identity(),count=48,scheduled_starts=912,
        source_sha256=R.R.digest(args.native/"source_inputs.json"),
        starts={R.key("LC-J1",w,h):starts(data,w,h) for w,h in jobs()},
        reference_replay_sha256=R.R.digest(args.work/"REFERENCE_REPLAY.json"))
    path=args.work/"FIT_FREEZE.json"
    if path.exists() and json.loads(path.read_text())!=schedule:
        raise ValueError("Frozen schedule changed")
    R.R.write_json(path,schedule)
    # Starts have no dependence on other starts. Submission/record order is the
    # declared order; parallel completion changes neither seeds nor selection.
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context("fork")) as pool:
        futures=[pool.submit(run_start,(w,h,i)) for w,h in jobs() for i in range(19)]
        results=[f.result() for f in as_completed(futures)]
    if any(r["status"]!="complete" for r in results):
        raise RuntimeError("Scheduled failures retained; no incomplete fit may be scored")
    collect(data,args)


if __name__=="__main__":
    main()

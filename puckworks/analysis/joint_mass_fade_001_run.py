"""Authenticate and run exactly 24 problems / 456 starts, controls first."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import gzip
import hashlib
import io
import json
import multiprocessing
from pathlib import Path
import subprocess
import time

import numpy as np
from scipy.optimize import minimize

from . import joint_mass_fade_001 as F
from . import joint_clock_001_run as R
from . import wasz_turnover_time_001 as O
from . import turnover_time_replay_001 as T

ROOT = R.ROOT
OUT = ROOT / "docs/research/JOINT_MASS_FADE_001"
ARMS = ("saved_A_J1", "refreshed_A_J1", "A_J1_F")
SCOPES = ("LOCO", "DESCRIPTIVE_ALL")
BASE = "4c5ebab5df79929813949df7113c21290dde40cc"
WASZ = "c4b4a07e110a3ede5013fd876a02a58ee6456eab"
REPLAY = "ec82d1f019da3a5fcd9ff8748c29926c763d7bcc"
LC = "0e1944de72819f0a058b99b6c0b2879e2d4ffde6"
_DATA = _ARGS = None


def table(path):
    csv.field_size_limit(100_000_000)
    with Path(path).open() as f:
        return list(csv.DictReader(f))


def read(path):
    return json.loads(Path(path).read_text())


def identity():
    names = [OUT/"PLAN.md", OUT/"START_BANK.csv", OUT/"SOURCE_FITS.json",
             Path(__file__), Path(F.__file__), Path(F.J.__file__), Path(R.W.__file__), Path(R.__file__)]
    return {str(p.relative_to(ROOT)): R.R.digest(p) for p in names}


def pinned_hash(commit, name):
    return hashlib.sha256(subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)).hexdigest()


def load_data(args):
    data = R.load_data(args)
    manifest = read(ROOT/"docs/research/JOINT_CLOCK_001/RUN_MANIFEST.json")
    T.checked_hash(args.native/"source_inputs.json", manifest["source_inputs_sha256"])
    T.checked_hash(args.ewp/"docs/demonstrations/FORM_A/RUN_MANIFEST.json", manifest["native_manifest_sha256"])
    data["reference"] = {}; data["lc"] = {}
    lc_csv = subprocess.check_output(["git", "show", f"{LC}:docs/research/LC_JOINT_TRANSFER_001/FITS.csv"], cwd=ROOT).decode()
    lc_rows = {r["key"]: r for r in csv.DictReader(io.StringIO(lc_csv))}
    j_rows = {r["key"]: r for r in table(ROOT/"docs/research/JOINT_CLOCK_001/FITS.csv")}
    for r in read(OUT/"SOURCE_FITS.json"):
        assert r["saved_sha256"] == j_rows[r["saved_key"]]["fit_sha256"]
        assert r["lc_sha256"] == lc_rows[r["lc_key"]]["fit_sha256"]
        assert r["lc_frozen_zero_objective"] == float(lc_rows[r["lc_key"]]["frozen_f0_objective"])
        fit = read(args.joint/"fits"/(r["saved_key"]+".json"))
        T.checked_hash(args.joint/"fits"/(r["saved_key"]+".json"), r["saved_sha256"])
        lfit = read(args.lc/"fits"/(r["lc_key"]+".json"))
        T.checked_hash(args.lc/"fits"/(r["lc_key"]+".json"), r["lc_sha256"])
        for name, digest in fit["identity"].items():
            if pinned_hash(BASE, name) != digest:
                raise ValueError("Historical fit code/protocol differs from pinned base")
        fold, held = r["fold"], fit["held_condition_bar"]
        expected = [s["brew"] for s in data["sources"] if held is None or s["nominal_pressure_bar"] != held]
        for item in (fit,lfit):
            if item["fold"] != fold or item["weight"] != 1 or item["training_brews"] != expected or item["mc_fixed_g"] != data["bank"][fold][4]:
                raise ValueError("Fold/weight/Mc/training membership mismatch")
        data["reference"][fold] = {k: fit[k] for k in ("parameters","objective","held_condition_bar","training_brews","mc_fixed_g")}
        data["lc"][fold] = dict(parameters=[*lfit["parameters"][:4],0.,lfit["parameters"][-1]], objective=r["lc_frozen_zero_objective"])
    c2 = next(r for r in table(ROOT/"docs/research/PRESSURE_PEAK_STAGE_C2/RESULT_TABLE.csv") if r.get("candidate")=="T2-F" and r.get("parameters_by_fold"))
    bank = json.loads(c2["parameters_by_fold"])
    assert all(v[4] == bank[k]["Mc_fixed_g"] for k,v in data["bank"].items())
    for item in read(OUT/"IMPORTED_SOURCES.json"):
        T.checked_hash(ROOT/item["path"], item["sha256"])
        assert pinned_hash(item["commit"],item["path"]) == item["sha256"]
    frozen = read(args.replay/"docs/research/TURNOVER_TIME_REPLAY_001/INPUT_MANIFEST.json")
    for name,digest in frozen["repository_inputs"].items():
        assert pinned_hash(REPLAY,name)==digest
    for name,digest in frozen["wasz_inputs"].items():
        T.checked_hash(args.wasz/"docs/research/WASZ_TURNOVER_TIME_001"/name,digest)
        assert pinned_hash(WASZ,"docs/research/WASZ_TURNOVER_TIME_001/"+name)==digest
    receipt = read(args.wasz/"docs/research/WASZ_TURNOVER_TIME_001/RUN_RECEIPT.json")
    assert [s["brew"] for s in data["sources"]] == receipt["brew_order"]
    data["condition"] = np.array([s["nominal_pressure_bar"] for s in data["sources"]])
    data["draws"] = O.draw_bank(data["condition"])
    assert O.bank_digest(data["draws"]) == frozen["draw_bank_sha256"] == "d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6"
    data["observed"] = {(r["brew"],r["clock"],int(r["time_s"])):r for r in table(args.wasz/"docs/research/WASZ_TURNOVER_TIME_001/PER_BREW_BY_TIME.csv")}
    data["native"] = {}
    for s in data["sources"]:
        ct,cp,cq,onset,_ = O.native_observation(args.raw/"measurements_time_dependent"/(s["brew"]+".txt"))
        data["native"][s["brew"]] = ct,cp,cq,onset
        for clock,target in O.SNAPSHOTS:
            row = data["observed"][s["brew"],clock,target]
            p,q,reason = O.paired_window(ct,cp,cq,T.observed_center(onset,clock,target))
            assert reason == row["reason"] and (reason=="available") == (row["available"]=="True")
            np.testing.assert_allclose([p,q],[float(row["pressure_bar"]),float(row["flow_g_s"])],rtol=1e-12,atol=1e-12)
    data["starts"] = table(OUT/"START_BANK.csv")
    return data


def start_bank(data, arm, fold, work):
    rows = [r for r in data["starts"] if r["arm"] == arm and r["fold"] == fold]
    assert len(rows)==19 and [int(r["start"]) for r in rows]==list(range(19))
    if arm=="A_J1_F":
        control = read(work/"fits"/f"refreshed_A_J1_{fold}.json")
        assert control["identity"] == identity() and control["fold"] == fold
    result=[]
    for r in rows:
        p=json.loads(r["parameters"])
        if isinstance(p,str):
            p=list(control["parameters"]);p[4]=float(r["gamma"])
        assert p[4]*float(r["Mc_g"]) == float(r["gamma_Mc"]) or np.isclose(p[4]*float(r["Mc_g"]),float(r["gamma_Mc"]),rtol=1e-15,atol=0)
        assert float(r["Mc_g"]) == data["bank"][fold][4]
        result.append((r["origin"],p))
    return result


class Objective:
    def __init__(self,data,held,control=False):
        self.data,self.held,self.control=data,held,control
        self.lo,self.hi=F.bounds()
        if control:
            self.lo,self.hi=self.lo[[0,1,2,3,5]],self.hi[[0,1,2,3,5]]
        self.trials=[];self.cache={};self.best=None

    def parameters(self,z):
        if self.control:
            z=np.r_[z[:4],0.,z[4]]
        return F.physical(z)

    def __call__(self,z):
        if not np.isfinite(z).all():
            raise ValueError("Nonfinite coordinates")
        z=np.clip(z,self.lo,self.hi)
        key=tuple(z)
        if key in self.cache:
            return self.cache[key]
        row=F.objective(self.data,self.parameters(z),self.held)
        self.trials.append(row);self.cache[key]=row["objective"]
        if self.best is None or row["objective"] < self.best["objective"]:
            self.best=row
        return row["objective"]


def run_start(job):
    arm,fold,number=job;data,args=_DATA,_ARGS
    path=args.work/"starts"/f"{arm}_{fold}_{number:02d}.json"
    if path.exists():
        old=read(path)
        if old["identity"] != identity() or old["status"] != "complete":
            raise ValueError("Changed/failed prior attempt; preserve before retry")
        return old
    origin,p=start_bank(data,arm,fold,args.work)[number]
    held=data["reference"][fold]["held_condition_bar"]
    obj=Objective(data,held,arm=="refreshed_A_J1")
    z=F.coordinates(p)
    if obj.control:
        z=z[[0,1,2,3,5]]
    cpu,wall=time.process_time(),time.perf_counter()
    record=dict(arm=arm,fold=fold,start=number,origin=origin,initial_parameters=p,
                gamma_Mc=p[4]*data["bank"][fold][4],identity=identity())
    try:
        record["initial_objective"]=obj(z)
        result=minimize(obj,z,method="Powell",bounds=list(zip(obj.lo,obj.hi)),
            options=dict(xtol=1e-4,ftol=1e-7,maxiter=np.inf,maxfev=np.inf))
        record.update(status="complete",success=bool(result.success),message=str(result.message),
                      returned_objective=float(result.fun),nfev=int(result.nfev))
    except BaseException as exc:
        record.update(status="failed",success=False,error=repr(exc))
    record.update(best=obj.best,evaluations=len(obj.trials),cpu_seconds=time.process_time()-cpu,
                  wall_seconds=time.perf_counter()-wall)
    trials=args.work/"trials"/(path.stem+".json.gz")
    with gzip.open(trials,"wt") as f:
        json.dump(obj.trials,f,allow_nan=False,separators=(",",":"))
    record["trials_sha256"]=R.R.digest(trials)
    R.R.write_json(path,record)
    print(json.dumps({k:record[k] for k in ("arm","fold","start","status","cpu_seconds")}),flush=True)
    return record


def collect(data,args,arm):
    for fold,ref in data["reference"].items():
        records=[read(args.work/"starts"/f"{arm}_{fold}_{i:02d}.json") for i in range(19)]
        assert all(r["status"]=="complete" and r["identity"]==identity() for r in records)
        winner=min(records,key=lambda r:r["best"]["objective"])
        best=winner["best"]
        if arm=="A_J1_F":
            control=read(args.work/"fits"/f"refreshed_A_J1_{fold}.json")
            np.testing.assert_allclose(records[0]["initial_objective"],control["objective"],rtol=1e-12,atol=0)
            assert best["objective"] <= records[0]["initial_objective"]
        row=dict(arm=arm,fold=fold,mc_fixed_g=data["bank"][fold][4],held_condition_bar=ref["held_condition_bar"],
            training_brews=ref["training_brews"],**best,identity=identity(),winning_start=winner["start"],
            cpu_seconds=sum(r["cpu_seconds"] for r in records),dt=.02,cells=256)
        R.R.write_json(args.work/"fits"/f"{arm}_{fold}.json",row)


def reference_one(fold):
    data,args=_DATA,_ARGS; ref=data["reference"][fold];p=ref["parameters"]
    cpu=time.process_time()
    nested=F.objective(data,[*p[:4],0.,p[-1]],ref["held_condition_bar"])
    np.testing.assert_allclose(nested["objective"],ref["objective"],rtol=1e-12,atol=0)
    zero=F.objective(data,data["lc"][fold]["parameters"],ref["held_condition_bar"])
    np.testing.assert_allclose(zero["objective"],data["lc"][fold]["objective"],rtol=1e-12,atol=0)
    # Authenticate/replay full historical held-out arrays for every brew and
    # the original 23-pressure descriptive sweep at both numerical steps.
    manifest=read(ROOT/"docs/research/JOINT_CLOCK_001/RUN_MANIFEST.json")
    cases=0
    for r in manifest["predictions"]["records"]:
        if "_J1_lambda-1_" not in r["key"]:
            continue
        path=args.joint/"predictions"/(r["key"]+".json")
        T.checked_hash(path,r["metadata_sha256"]); row=read(path)
        rf=R.label(None if row["scope"]=="descriptive" else row["pressure_bar"])
        if rf!=fold:
            continue
        if row["scope"]=="held_out":
            s=next(s for s in data["sources"] if s["brew"]==row["brew"])
        else:
            s=dict(predict_times_s=[0.,100.],predict_pressure_bar=[row["pressure_bar"]]*2,predict_horizon_s=100.)
        for step,dt in (("search",.02),("fine",.005)):
            predictor=F.prepare(s,[*p[:4],0.,p[-1]],ref["mc_fixed_g"],dt)
            pred=predictor.chemistry(s["predict_horizon_s"])
            saved=row[step];ap=args.joint/"predictions"/saved["prediction"]["file"]
            T.checked_hash(ap,saved["prediction"]["sha256"])
            with np.load(ap) as arrays:
                for k in arrays.files:
                    np.testing.assert_allclose(pred[k],arrays[k],rtol=1e-12,atol=0)
            obs=predictor.observer(s.get("observer_times_s",np.linspace(0,100,1001)),accelerate=False)
            for k in ("detected","onset_s","censor_bound_s"):
                assert obs[k]==saved["observer"][k]
        cases+=1
    return dict(fold=fold,objective=nested["objective"],lc_frozen_zero_objective=zero["objective"],cases=cases,
                cpu_seconds=time.process_time()-cpu)


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=["reference","control","fade","collect"])
    for flag in ("ewp","native","raw","screen","joint","lc","wasz","replay","work"):
        p.add_argument("--"+flag,type=Path,required=True)
    p.add_argument("--workers",type=int,default=48)
    return p


def main():
    global _DATA,_ARGS
    _ARGS=args=parser().parse_args()
    for d in ("starts","trials","fits","predictions"):
        (args.work/d).mkdir(parents=True,exist_ok=True)
    _DATA=data=load_data(args)
    if args.command=="reference":
        with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context("fork")) as pool:
            rows=list(pool.map(reference_one,data["reference"]))
        R.R.write_json(args.work/"REFERENCE.json",dict(identity=identity(),records=rows,cpu_seconds=sum(r["cpu_seconds"] for r in rows)))
        return
    if args.command=="collect":
        for arm in ARMS[1:]:
            collect(data,args,arm)
        return
    assert read(args.work/"REFERENCE.json")["identity"]==identity()
    # Plan and bank must already be in Git before the first optimizer call.
    for name in ("PLAN.md","START_BANK.csv"):
        assert pinned_hash("HEAD","docs/research/JOINT_MASS_FADE_001/"+name)==R.R.digest(OUT/name)
    arm="refreshed_A_J1" if args.command=="control" else "A_J1_F"
    frozen=dict(identity=identity(),arm=arm,starts={fold:start_bank(data,arm,fold,args.work) for fold in data["reference"]})
    path=args.work/(args.command+"-FREEZE.json")
    if path.exists():
        assert read(path)==frozen
    R.R.write_json(path,frozen)
    jobs=[(arm,fold,i) for fold in data["reference"] for i in range(19)]
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context("fork")) as pool:
        futures=[pool.submit(run_start,job) for job in jobs]
        for future in as_completed(futures):
            future.result()
    collect(data,args,arm)


if __name__=="__main__":
    main()

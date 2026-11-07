"""Authenticate and run exactly 12 pressure-fade problems / 228 starts; frozen controls."""
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import csv
import gzip
import hashlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import time

import numpy as np
from scipy.optimize import minimize

from . import joint_pressure_fade_001 as F
from . import joint_clock_001_run as R
from . import joint_mass_fade_001_run as MR
from . import wasz_turnover_time_001 as O
from . import turnover_time_replay_001 as T

ROOT = R.ROOT
OUT = ROOT / "docs/research/JOINT_PRESSURE_FADE_001"
ARMS = ("saved_A_J1", "refreshed_A_J1", "A_J1_F", "A_J1_PF")
SCOPES = ("LOCO", "DESCRIPTIVE_ALL")
BASE = "fa0b14003cb0d7c77a902e3adf1e6fd1a38bf120"
FADE_SHA = "ec0dc887ca0f66338fe166cd4ed8e7cbf2994441"
DIAGNOSTIC_SHA = "093b8b5e5a4c86ebf31bc48f46521441069072ec"
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
    names = [OUT/"PLAN.md", OUT/"START_BANK.csv", OUT/"INPUT_MANIFEST.json",
             Path(__file__), Path(F.__file__), Path(F.J.__file__), Path(R.W.__file__), Path(R.__file__)]
    return {str(p.relative_to(ROOT)): R.R.digest(p) for p in names}


def pinned_hash(commit, name):
    return hashlib.sha256(subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=ROOT)).hexdigest()


def load_data(args):
    # Reuse the original authenticated raw observations/folds/windows verbatim.
    data = MR.load_data(args)
    assert O.bank_digest(data['draws']) == 'd599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6'
    manifest = read(OUT/"INPUT_MANIFEST.json")
    for name, digest in manifest["mass_artifacts"].items():
        T.checked_hash(ROOT/name, digest)
        assert pinned_hash(FADE_SHA, name) == digest
    receipt = read(MR.OUT/"RUN_RECEIPT.json")
    for name, digest in receipt["code_sha256"].items():
        assert pinned_hash(FADE_SHA, name) == digest
        if name not in ("puckworks/analysis/joint_clock_001.py", "puckworks/analysis/wetting_screen_001.py"):
            T.checked_hash(ROOT/name, digest)
    diagnostic = "puckworks/analysis/mass_fade_diagnostics_001.py"
    assert R.R.digest(ROOT/diagnostic) == pinned_hash(DIAGNOSTIC_SHA, diagnostic)
    for name, digest in manifest["external_freezes"].items():
        T.checked_hash(args.fade_evidence/name, digest)
    data["reused"] = {}
    for name, digest in manifest["source_fit_sha256"].items():
        T.checked_hash(args.fade_evidence/name, digest)
        fit = read(args.fade_evidence/name)
        for source, value in fit["identity"].items():
            assert pinned_hash(FADE_SHA, source) == value
        ref = data["reference"][fit["fold"]]
        assert fit["mc_fixed_g"] == ref["mc_fixed_g"]
        assert fit["training_brews"] == ref["training_brews"]
        data["reused"][fit["arm"], fit["fold"]] = fit
    assert len(data["reused"]) == 24
    data["starts"] = table(OUT/"START_BANK.csv")
    return data


def start_bank(data, arm, fold, work):
    assert arm == "A_J1_PF"
    rows = [r for r in data["starts"] if r["fold"] == fold and r["arm"] == arm]
    assert len(rows) == 19 and [int(r["start"]) for r in rows] == list(range(19))
    control = data["reused"]["refreshed_A_J1", fold]
    result = []
    for i, r in enumerate(rows):
        p = json.loads(r["parameters"])
        np.testing.assert_array_equal(F.physical(F.coordinates(p)),p)
        assert p[4]*1300 == float(r["gamma_P_1300"])
        assert float(r["Mc_g"]) == data["bank"][fold][4]
        if i < 4:
            assert p[:4]+p[5:] == control["parameters"][:4]+control["parameters"][5:]
        result.append((r["origin"],p))
    assert result[0][1] == control["parameters"]
    return result


class Objective:
    def __init__(self,data,held):
        self.data,self.held=data,held
        self.lo,self.hi=F.bounds()
        self.trials=[];self.cache={};self.best=None

    def parameters(self,z):
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
    obj=Objective(data,held)
    z=F.coordinates(p)
    cpu,wall=time.process_time(),time.perf_counter()
    record=dict(arm=arm,fold=fold,start=number,origin=origin,initial_parameters=p,
                gamma_P_1300=p[4]*1300,identity=identity())
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
        control=data["reused"]["refreshed_A_J1",fold]
        assert records[0]["initial_objective"] == control["objective"]
        assert best["objective"] <= records[0]["initial_objective"]
        row=dict(arm=arm,fold=fold,mc_fixed_g=data["bank"][fold][4],held_condition_bar=ref["held_condition_bar"],
            training_brews=ref["training_brews"],**best,identity=identity(),winning_start=winner["start"],
            cpu_seconds=sum(r["cpu_seconds"] for r in records),dt=.02,cells=256)
        R.R.write_json(args.work/"fits"/f"{arm}_{fold}.json",row)


def reference_one(fold):
    data = _DATA
    control = data["reused"]["refreshed_A_J1",fold]
    cpu = time.process_time()
    actual = F.objective(data, control["parameters"], control["held_condition_bar"])
    for key in ("objective","flow_component","onset_component","detected","intended","available","condition_components"):
        assert actual[key] == control[key], (fold, key)
    return dict(fold=fold, **actual, exact_control_reproduction=True,
                cpu_seconds=time.process_time()-cpu)


def parser():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("command",choices=["reference","fade","collect"])
    for flag in ("ewp","native","raw","screen","joint","lc","wasz","replay","fade-evidence","work"):
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
        collect(data,args,"A_J1_PF")
        return
    assert read(args.work/"REFERENCE.json")["identity"]==identity()
    # Plan and bank must already be in Git before the first optimizer call.
    for name in ("PLAN.md","START_BANK.csv"):
        assert pinned_hash("HEAD","docs/research/JOINT_PRESSURE_FADE_001/"+name)==R.R.digest(OUT/name)
    arm="A_J1_PF"
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

"""Frozen LC-J1 evaluations, f=0 diagnostics and descriptive shape freeze."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
import multiprocessing
from pathlib import Path
import time

import numpy as np

from . import lc_joint_transfer_001 as L
from . import lc_joint_transfer_001_run as R

_DATA = None
_ARGS = None


def evaluate_case(args, data, fit, path, source, scope):
    name=source.get("brew",f"constant-{source['nominal_pressure_bar']:g}")
    arm=f"LC-J1_lambda-{fit['weight']:g}"
    key=scope+"_"+arm+"_"+name
    folder=args.work/"predictions"
    metadata=folder/(key+".json")
    identity=dict(fit_sha256=R.R.R.digest(path),fit_identity=R.identity(),
        evaluator_sha256=R.R.R.digest(Path(__file__)),
        source_input_sha256=R.R.R.digest(args.native/"source_inputs.json"))
    if metadata.exists():
        row=json.loads(metadata.read_text())
        if row["identity"]!=identity:
            raise ValueError("Frozen evaluation identity changed")
        for step in ("fine","search"):
            a=row[step]["prediction"]
            if R.R.R.digest(folder/a["file"])!=a["sha256"]:
                raise ValueError("Frozen array changed")
        return row
    held=None if scope=="descriptive" else source["nominal_pressure_bar"]
    if fit["fold"]!=R.R.label(held) or fit["mc_fixed_g"]!=data["bank"][fit["fold"]][4]:
        raise ValueError("Wrong fold or Mc")
    if scope=="held_out" and source["brew"] in fit["training_brews"]:
        raise ValueError("Held-out brew appears in training")
    start=time.process_time()
    row=dict(key=key,arm=arm,model="LC-J1",weight=fit["weight"],scope=scope,
        brew=source.get("brew"),pressure_bar=source["nominal_pressure_bar"],
        fold=fit["fold"],parameters=fit["parameters"],mc_fixed_g=fit["mc_fixed_g"],identity=identity,
        native_qualification_failed=source.get("native_qualification_failed"))
    for step,dt in (("search",.02),("fine",.005)):
        predictor=L.prepare(source,fit["parameters"],fit["mc_fixed_g"],dt)
        prediction=predictor.chemistry(source["predict_horizon_s"])
        observer=predictor.observer(source.get("observer_times_s",np.linspace(0,100,1001)),accelerate=False)
        artifact=R.R.R.save_prediction(folder/(key+"_"+step+".npz"),prediction)
        artifact.update(front_on_full_support_s=predictor.tb,front_s=predictor.tb if predictor.tb<=100 else None,
                        front_right_censored=bool(predictor.tb>100))
        endpoint=float(predictor.scored_flow([100.])[0])
        q=predictor.scored_flow(source.get("trace_times_s",np.linspace(0,100,1001)))
        value=dict(prediction=artifact,observer=observer,endpoint_g_s=endpoint,
            unshifted_endpoint_g_s=endpoint,trace_g_s=q.tolist(),unshifted_trace_g_s=q.tolist(),
            endpoint_beverage_g=float(np.interp(100.,prediction["time"],prediction["beverage_g"])),
            endpoint_liquid_g=float(np.interp(100.,prediction["time"],prediction["liquid_g"])),
            endpoint_beverage_minus_liquid_flow_g_s=float(np.interp(100.,prediction["time"],
                np.gradient(prediction["solute_g"],prediction["time"]))))
        if scope=="held_out":
            flow,onset=L.J.loss_components(predictor.scored_flow(source["fit_times_s"]),
                source["fit_flow_g_s"],observer,source["observed_onset_for_scoring_only_s"])
            value["objective_components"]=dict(flow=flow,onset=onset,weighted_onset=fit["weight"]*onset,
                                               joint=flow+fit["weight"]*onset)
        row[step]=value
    row["cpu_seconds"]=time.process_time()-start
    R.R.R.write_json(metadata,row)
    return row


def evaluate_fit(job):
    weight,held=job
    args,data=_ARGS,_DATA
    path=args.work/"fits"/(R.R.key("LC-J1",weight,held)+".json")
    fit=json.loads(path.read_text())
    if fit["identity"]!=R.identity():
        raise ValueError("Fitting code changed")
    start=time.process_time()
    p=np.array(fit["parameters"])
    zero=p.copy(); zero[4]=0.
    a=data["reference"][(weight,fit["fold"])]
    ap=np.r_[a["parameters"][:4],0.,a["parameters"][4]]
    diagnostic=dict(key=fit["key"],weight=weight,fold=fit["fold"],f=p[4],
        saved_A_J1_objective=a["objective"],selected_LC_J1_objective=fit["objective"],
        fit_sha256=R.R.R.digest(path),evaluator_sha256=R.R.R.digest(Path(__file__)))
    for name,params in (("LC_J1",p),("frozen_f0",zero),("saved_A_J1",ap)):
        for step,dt in (("search",.02),("fine",.005)):
            diagnostic[name+"_"+step]=L.objective(data,params,weight,held,dt)
    np.testing.assert_allclose(diagnostic["LC_J1_search"]["objective"],fit["objective"],rtol=1e-12,atol=0)
    np.testing.assert_allclose(diagnostic["saved_A_J1_search"]["objective"],a["objective"],rtol=1e-12,atol=0)
    diagnostic["cpu_seconds"]=time.process_time()-start
    R.R.R.write_json(args.work/"diagnostics"/(fit["key"]+".json"),diagnostic)
    if held is None:
        pressures=sorted({r["nominal_pressure_bar"] for r in data["manifest"]["runs"] if "primary A0" in r["roles"]})
        if len(pressures)!=23:
            raise ValueError("Wrong descriptive grid")
        selected=[dict(nominal_pressure_bar=p,predict_times_s=[0.,100.],
            predict_pressure_bar=[p,p],predict_horizon_s=100.) for p in pressures]
        scope="descriptive"
    else:
        selected=[s for s in data["sources"] if s["nominal_pressure_bar"]==held]
        scope="held_out"
    rows=[evaluate_case(args,data,fit,path,s,scope) for s in selected]
    print(json.dumps(dict(evaluated=fit["key"],cases=len(rows))),flush=True)
    return dict(key=fit["key"],diagnostic_cpu_seconds=diagnostic["cpu_seconds"],
        records=[dict(key=r["key"],cpu_seconds=r["cpu_seconds"],
            metadata_sha256=R.R.R.digest(args.work/"predictions"/(r["key"]+".json"))) for r in rows])


def freeze_shapes(args,data):
    shapes=[]
    for weight in L.J.WEIGHTS:
        a=data["reference"][(weight,"DESCRIPTIVE_ALL")]
        lp=args.work/"fits"/(R.R.key("LC-J1",weight,None)+".json")
        lc=json.loads(lp.read_text())
        for model,fit,path in (("A-J1",a,args.joint/"fits"/(a["key"]+".json")),("LC-J1",lc,lp)):
            p=fit["parameters"]
            shapes.append(dict(model=model,weight=weight,n=p[2],Pd_bar=p[3],Pstar_bar=p[1],
                f=0. if model=="A-J1" else p[4],source_fit_sha256=R.R.R.digest(path),fold="DESCRIPTIVE_ALL"))
    record=dict(shapes=shapes,scope="Frozen before any Corrochano calculation; no external shape fitting",
                fit_freeze_sha256=R.R.R.digest(args.work/"FIT_FREEZE.json"))
    path=R.OUT/"FROZEN_EXTERNAL_SHAPES.json"
    if path.exists() and json.loads(path.read_text())!=record:
        raise ValueError("External shapes already frozen with different parameters")
    R.R.R.write_json(path,record)


def main():
    global _DATA,_ARGS
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp","native","raw","screen","joint","work"):
        p.add_argument("--"+flag,type=Path,required=True)
    p.add_argument("--workers",type=int,default=32)
    _ARGS=args=p.parse_args()
    _DATA=data=R.load_data(args)
    qualifications={r["brew"]:not r["balances_and_bounds_qualified"] for r in data["manifest"]["runs"]
                    if r.get("brew") and "primary A1" in r["roles"]}
    for s in data["sources"]:
        s["native_qualification_failed"]=qualifications[s["brew"]]
    for folder in ("predictions","diagnostics"):
        (args.work/folder).mkdir(exist_ok=True)
    freeze_shapes(args,data)
    with ProcessPoolExecutor(max_workers=args.workers,mp_context=multiprocessing.get_context("fork")) as pool:
        rows=list(pool.map(evaluate_fit,R.jobs()))
    R.R.R.write_json(args.work/"EVALUATION_INDEX.json",dict(fits=rows,
        records=[r for f in rows for r in f["records"]],cases_intended=4*(56+23),
        cpu_seconds=sum(f["diagnostic_cpu_seconds"]+sum(r["cpu_seconds"] for r in f["records"]) for f in rows)))


if __name__=="__main__":
    main()

"""Frozen jointly calibrated shapes on the unchanged COR15 reading contract."""
import argparse
import json
from pathlib import Path
import time

import numpy as np
from scipy.stats import qmc

from . import cor15_shape_001 as C
from . import lc_joint_transfer_001 as L
from . import lc_joint_transfer_001_run as R


def shape(p_pa, frozen):
    """Plotted corrected bed Pa -> bar, upstream Q unchanged; h has units bar."""
    return L.capacity([1.,frozen["Pstar_bar"],frozen["n"],frozen["Pd_bar"],frozen["f"],0.],
                      np.asarray(p_pa)/100000.)


def fit(p,q,frozen=None):
    h=np.asarray(p) if frozen is None else shape(p,frozen)
    amplitude,pred,mse=C.amplitude_fit(q,h)
    if not np.isfinite(amplitude) or amplitude<=0:
        raise ValueError("Positive amplitude unavailable")
    return dict(amplitude=amplitude,pred=pred,mse=mse)


def analyze(work):
    cpu=time.process_time()
    frozen_path=R.OUT/"FROZEN_EXTERNAL_SHAPES.json"
    frozen=json.loads(frozen_path.read_text())
    if frozen["fit_freeze_sha256"]!=R.R.R.digest(work/"FIT_FREEZE.json"):
        raise ValueError("Waszkiewicz shape freeze does not match fitting freeze")
    shapes={(r["weight"],r["model"]):r for r in frozen["shapes"]}
    if set(shapes)!={(w,m) for w in L.J.WEIGHTS for m in ("A-J1","LC-J1")}:
        raise ValueError("Incomplete frozen shapes")
    contract,coords=C.read_inputs()
    old=json.loads((C.OUTPUT/"RESULT.json").read_text())
    for path,sha in old["input_sha256"].items():
        if R.R.R.digest(R.ROOT/path)!=sha:
            raise ValueError("Original COR15 inputs changed")
    central=C.realize(contract,coords)
    names=list(dict.fromkeys(r["series"] for r in coords))
    indices={s:np.array([i for i,r in enumerate(coords) if r["series"]==s]) for s in names}
    if len(coords)!=108 or len(names)!=12:
        raise ValueError("Wrong COR15 coverage")
    s2={s:float(np.mean(central[ii,1]**2)) for s,ii in indices.items()}
    models=("LC-J1","A-J1","L0")
    contrasts=(("LC-J1","A-J1"),("LC-J1","L0"),("A-J1","L0"))
    fits,residuals,central_d=[],[],{}
    all_fits={}
    historical=[]
    for s,ii in indices.items():
        p,q=central[ii].T
        d0=C.fit(p,q,"FA")
        l0=C.fit(p,q,"L0")
        np.testing.assert_allclose(d0["pred"],old["central_fits"][s]["FA"]["pred"],rtol=1e-12,atol=0)
        historical.append(dict(series=s,model="D0_FA_historical",rmse_m3_s=d0["rmse"],
            lowest_pressure_bar=float(p.min()/100000),lowest_signed_residual_m3_s=d0["lowest_signed_residual"],
            D_minus_L0=C.matched_contrast(q,d0["pred"],l0["pred"],s2[s])))
        for w in L.J.WEIGHTS:
            fitted={"L0":l0,**{m:fit(p,q,shapes[(w,m)]) for m in ("LC-J1","A-J1")}}
            all_fits[(w,s)]=fitted
            for m,r in fitted.items():
                delta=r["pred"]-q
                fits.append(dict(weight=w,series=s,model=m,n=len(ii),amplitude=r["amplitude"],
                    amplitude_units="m3/(s Pa)" if m=="L0" else "m3/(s bar)",parameters_per_series=1,
                    rmse_m3_s=float(np.sqrt(r["mse"])),mse_m6_s2=r["mse"],
                    mean_signed_residual_m3_s=float(delta.mean()),lowest_signed_residual_m3_s=float(delta[np.argmin(p)]),
                    lowest_pressure_bar=float(p.min()/100000),S2_central_m6_s2=s2[s]))
                for i,pressure,obs,pred in zip(ii,p,q,r["pred"]):
                    residuals.append(dict(weight=w,series=s,model=m,point_id=coords[i]["point_id"],
                        P_Pa=float(pressure),Q_m3_s=float(obs),predicted_Q_m3_s=float(pred),signed_residual_m3_s=float(pred-obs)))
            for a,b in contrasts:
                central_d[(w,s,a,b)]=C.matched_contrast(q,fitted[a]["pred"],fitted[b]["pred"],s2[s])
    design=contract["reading_design"]
    if design["seed"]!=20261104 or design["power"]!=12:
        raise ValueError("Original graphical realization design changed")
    offsets=qmc.Sobol(12+2*len(coords),scramble=True,seed=20261104).random_base2(12)*2-1
    samples=np.empty((4096,4,12,3))
    historical_draws=np.empty((4096,12))
    for draw,u in enumerate(offsets):
        values=C.realize(contract,coords,u)
        for j,(s,ii) in enumerate(indices.items()):
            p,q=values[ii].T
            l0=fit(p,q)
            historical_draws[draw,j]=C.matched_contrast(q,C.fit(p,q,"FA")["pred"],l0["pred"],s2[s])
            for wi,w in enumerate(L.J.WEIGHTS):
                fitted={"L0":l0,**{m:fit(p,q,shapes[(w,m)]) for m in ("LC-J1","A-J1")}}
                for k,(a,b) in enumerate(contrasts):
                    samples[draw,wi,j,k]=C.matched_contrast(q,fitted[a]["pred"],fitted[b]["pred"],s2[s])
    np.testing.assert_allclose(np.mean([r["D_minus_L0"] for r in historical]),old["central_D"],rtol=1e-12,atol=0)
    np.testing.assert_allclose(np.quantile(historical_draws.mean(axis=1),[.025,.975]),old["D_reading_interval"],rtol=1e-12,atol=0)
    paired=[]
    for wi,w in enumerate(L.J.WEIGHTS):
        for k,(a,b) in enumerate(contrasts):
            for j,s in enumerate([*names,"POOLED"]):
                vals=samples[:,wi,:,k].mean(axis=1) if s=="POOLED" else samples[:,wi,j,k]
                value=float(np.mean([central_d[(w,s0,a,b)] for s0 in names])) if s=="POOLED" else central_d[(w,s,a,b)]
                lo,hi=np.quantile(vals,[.025,.975])
                paired.append(dict(weight=w,series=s,left=a,right=b,D=value,reading_lower_95=float(lo),reading_upper_95=float(hi),
                    realizations=4096,interval_scope="graphical readings conditional on frozen Waszkiewicz shape; not population confidence",
                    S2_definition="fixed central mean(Q squared); equal mean over series"))
    path=work/"CORROCHANO_READING_DRAWS.npz"
    np.savez_compressed(path,paired_D=samples,historical_D=historical_draws,offsets=offsets,
                        weights=np.array(L.J.WEIGHTS),series=np.array(names),contrasts=np.array(contrasts))
    for name,rows in (("CORROCHANO_SERIES.csv",fits),("CORROCHANO_RESIDUALS.csv",residuals),
                      ("CORROCHANO_PAIRED.csv",paired),("CORROCHANO_D0_CONTEXT.csv",historical)):
        R.R.R.csv_write(R.OUT/name,rows)
    plot(central,coords,shapes,all_fits,work)
    result=dict(shapes_sha256=R.R.R.digest(frozen_path),input_sha256=old["input_sha256"],
        points=108,series=12,realizations=4096,seed=20261104,contrasts=[r for r in paired if r["series"]=="POOLED"],
        historical_D0_reproduced=True,draws=dict(file=path.name,sha256=R.R.R.digest(path)),
        cpu_seconds=time.process_time()-cpu,source_license="CC-BY-3.0",
        limitations="Upstream-meter Q, corrected bed pressure; constant series recovery absorbed into target-fitted amplitude. A-480 lowest 1.41 bar versus others .23-.42; no common-pressure lowest-point comparison. All points below Waszkiewicz peak; no high-pressure/onset test.")
    R.R.R.write_json(R.OUT/"CORROCHANO_RESULT.json",result)
    return result


def plot(central,coords,shapes,all_fits,preview):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec=VizSpec(id="lc_joint_transfer_001_cor15",title="Jointly calibrated shapes on Corrochano Fig.10",class_=1,
        producer=Producer(module=__name__,function="analyze",result_map={"contrasts":"contrasts"}),
        badge="OBSERVED",evidence_strength="post-fit reconstruction",components=[],
        fidelity_ceiling="Frozen shapes with target-fitted per-series amplitudes; descriptive, not physical validation.",
        render_fn=__name__+":plot",caption="Original axes, primary lambda=1; bars are source three-bed SD, not reading intervals.",
        outputs=["CORROCHANO.svg"],used_in="PW-LC-JOINT-TRANSFER-001")
    if spec.validate():
        raise ValueError(spec.validate())
    readings={r["point_id"]:r for r in R.table(C.OUTPUT/"DIGITIZED.csv")}
    colors={"LC-J1":"#007c91","A-J1":"#be4b35","L0":"#222222"}
    with matplotlib.rc_context({"svg.hashsalt":"PW-LC-JOINT-TRANSFER-001-COR15","font.size":9}):
        fig,axes=plt.subplots(3,4,figsize=(13,10),sharey=True)
        for row,density in enumerate((360,400,480)):
            for col,grind in enumerate("ABCD"):
                s=f"{grind}-{density}"; ax=axes[row,col]
                ii=[i for i,r in enumerate(coords) if r["series"]==s]
                p,q=central[ii].T
                for i in ii:
                    r=readings[coords[i]["point_id"]]
                    xe=np.array([[float(r["Q_SD_minus_m3_s"])],[float(r["Q_SD_plus_m3_s"])]])*1e6 if r["Q_SD_minus_m3_s"] else None
                    ye=np.array([[float(r["P_SD_minus_Pa"])],[float(r["P_SD_plus_Pa"])]])/1e5 if r["P_SD_minus_Pa"] else None
                    ax.errorbar(central[i,1]*1e6,central[i,0]/1e5,xerr=xe,yerr=ye,fmt="o",mfc="white",mec="black",ms=3.5,ecolor=".6",capsize=2,lw=.7)
                grid=np.linspace(p.min(),p.max(),300)
                for m in ("LC-J1","A-J1","L0"):
                    h=grid if m=="L0" else shape(grid,shapes[(1.,m)])
                    ax.plot(all_fits[(1.,s)][m]["amplitude"]*h*1e6,grid/1e5,color=colors[m],label=m+" (1 amplitude)")
                ax.set_title(f"{s} kg/m³ · {len(ii)} means")
                ax.set_ylim(0,4.6); ax.set_xlim(left=0); ax.grid(alpha=.15)
                if row==2: ax.set_xlabel("Upstream-meter Q (10⁻⁶ m³/s)")
                if col==0: ax.set_ylabel("Corrected bed pressure (bar)")
        h,l=axes[0,0].get_legend_handles_labels()
        fig.legend(h,l,ncol=3,loc="upper center",bbox_to_anchor=(.5,.955))
        fig.suptitle("Corrochano 2015: frozen joint shapes, primary λ=1",y=.99)
        fig.text(.02,.027,spec.badge_line()+" · Target-fitted amplitudes; not blind or parameter-free prediction.",fontsize=8)
        fig.text(.02,.01,"A-480 lowest point: 1.41 bar; others: 0.23–0.42 bar. Bars: three-bed SD. Source CC BY 3.0, doi:10.1016/j.jfoodeng.2014.11.006.",fontsize=8)
        fig.tight_layout(rect=(0,.05,1,.93))
        fig.savefig(R.OUT/"CORROCHANO.svg",metadata={"Date":None})
        fig.savefig(preview/"CORROCHANO.png",dpi=140)
        plt.close(fig)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--work",type=Path,required=True)
    args=p.parse_args()
    analyze(args.work)

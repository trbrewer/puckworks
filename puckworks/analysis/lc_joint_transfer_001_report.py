"""Matched frozen Waszkiewicz reporting; no parameter fitting or weight selection."""
import argparse
import gzip
import json
from pathlib import Path
import time

import numpy as np

from . import joint_clock_001_report as Q
from . import lc_joint_transfer_001 as L
from . import lc_joint_transfer_001_run as R
from . import wetting_screen_001_report as P

W=R.R.W
CONDITIONAL="conditional on fitted parameters and fixed Mc; no refit uncertainty"


def load_predictions(args):
    data=R.load_data(args)
    replay=json.loads((args.work/"REFERENCE_REPLAY.json").read_text())
    if replay["status"]!="reproduced" or replay["identity"]!=R.identity():
        raise ValueError("Unreproduced or changed reference")
    index=json.loads((args.work/"EVALUATION_INDEX.json").read_text())
    rows=[]
    refs=[r for f in replay["records"] for r in f["predictions"]]
    for root,entries,model in ((args.joint,refs,"A-J1"),(args.work,index["records"],"LC-J1")):
        for entry in entries:
            path=root/"predictions"/(entry["key"]+".json")
            if R.R.R.digest(path)!=entry["metadata_sha256"]:
                raise ValueError("Frozen prediction metadata changed")
            row=json.loads(path.read_text())
            row["model"]=model
            row["arm"]=f"{model}_lambda-{row['weight']:g}"
            row["artifact_root"]=root/"predictions"
            for step in ("fine","search"):
                artifact=row[step]["prediction"]
                if R.R.R.digest(row["artifact_root"]/artifact["file"])!=artifact["sha256"]:
                    raise ValueError("Frozen trace changed")
            rows.append(row)
    arms=[f"{m}_lambda-{w:g}" for w in L.J.WEIGHTS for m in ("A-J1","LC-J1")]
    for a in arms:
        for scope,n in (("held_out",56),("descriptive",23)):
            selected=[r for r in rows if r["arm"]==a and r["scope"]==scope]
            if len(selected)!=n or len({r["brew"] if scope=="held_out" else r["pressure_bar"] for r in selected})!=n:
                raise ValueError("Incomplete/duplicated prediction cohort")
    return data,rows,arms


def scores(data,rows,arms):
    sources=data["sources"]
    conditions=np.array([s["nominal_pressure_bar"] for s in sources])
    groups,samples=P.paired_samples(conditions)
    reports,selected,errors={},{},{}
    b1=P.hydraulic_errors(sources,[s["b1_endpoint_g_s"] for s in sources],[s["b1_trace_g_s"] for s in sources])
    for arm in arms:
        by_brew={r["brew"]:r for r in rows if r["arm"]==arm and r["scope"]=="held_out"}
        selected[arm]=[by_brew[s["brew"]] for s in sources]
        rr=selected[arm]
        report=dict(arm=arm,model=rr[0]["model"],weight=rr[0]["weight"],intended=56,available=56,
                    interval_scope=CONDITIONAL)
        for step in ("fine","search"):
            preds=[r[step] for r in rr]
            err=P.hydraulic_errors(sources,[r["endpoint_g_s"] for r in preds],[r["trace_g_s"] for r in preds])
            err["onset"]=np.array([W.squared_onset(r["observer"],s["observed_onset_for_scoring_only_s"])
                                   for r,s in zip(preds,sources)])
            errors[(arm,step)]=err
            report[step+"_detected"]=sum(r["observer"]["detected"] for r in preds)
        report["censored"]=56-report["fine_detected"]
        report["onset_is_lower_bound"]=bool(report["censored"])
        report.update(P.response(np.array([r["fine"]["endpoint_g_s"] for r in rr]),
            np.array([s["pressure_bar"][-1] for s in sources]),conditions))
        reports[arm]=report
    paired=[]
    for metric in ("endpoint","primary_trace","companion_trace","onset"):
        square=[errors[(a,"fine")][metric] for a in arms]
        if metric!="onset":
            square.append(b1[metric])
        points,draws=P.score_and_draws(square,groups,samples)
        for i,arm in enumerate(arms):
            r=reports[arm]
            r[metric+"_rmse"]=float(points[i])
            r[metric+"_interval"]=np.quantile(draws[:,i],[.025,.975]).tolist()
            r[metric+"_search_rmse"]=float(np.mean([np.sqrt(errors[(arm,"search")][metric][g].mean()) for g in groups]))
            r[metric+"_fine_minus_search"]=points[i]-r[metric+"_search_rmse"]
            if metric!="onset":
                ci=np.quantile(draws[:,i]-draws[:,-1],[.025,.975]).tolist()
                r[metric+"_minus_b1_interval"]=ci
                r[metric+"_comparison_vs_b1"]=P.flow_comparison(ci)
                if metric=="endpoint":
                    c=r[metric+"_comparison_vs_b1"]
                    r["accuracy_grade_vs_b1"]="MEETS" if c in ("BETTER","TIE") else "NEAR" if c=="UNRESOLVED" and points[i]<points[-1] else "MISSES"
        for w in L.J.WEIGHTS:
            a,b=f"LC-J1_lambda-{w:g}",f"A-J1_lambda-{w:g}"
            i,j=arms.index(a),arms.index(b)
            ci=np.quantile(draws[:,i]-draws[:,j],[.025,.975])
            bound=metric=="onset" and (reports[a]["censored"] or reports[b]["censored"])
            paired.append(dict(weight=w,left=a,right=b,metric=metric,left_score=points[i],right_score=points[j],
                difference=points[i]-points[j],lower_95=ci[0],upper_95=ci[1],
                left_intended=56,right_intended=56,left_available=56,right_available=56,
                left_detected=reports[a]["fine_detected"],right_detected=reports[b]["fine_detected"],
                interpretation="difference of computed bounds; not a bound on true-error difference" if bound else "paired RMSE difference",
                interval_scope=CONDITIONAL))
    for arm,r in reports.items():
        r["onset_grade"]=P.onset_grade(r["onset_rmse"],r["censored"])
    return reports,paired,selected,errors,samples


def flow_tables(data,selected):
    brews,conditions,trends,losses=[],[],[],[]
    sources=data["sources"]
    ft=np.array(data["fixture"]["fine_times_s"])
    for arm,rows in selected.items():
        own=[]
        for i,(s,r) in enumerate(zip(sources,rows)):
            row=dict(arm=arm,model=r["model"],weight=r["weight"],brew=s["brew"],pressure_bar=s["nominal_pressure_bar"],
                endpoint_observed_g_s=s["observed_endpoint_g_s"],endpoint_predicted_g_s=r["fine"]["endpoint_g_s"],
                endpoint_residual_g_s=r["fine"]["endpoint_g_s"]-s["observed_endpoint_g_s"],
                endpoint_beverage_minus_liquid_flow_g_s=r["fine"]["endpoint_beverage_minus_liquid_flow_g_s"],
                native_qualification_failed=r.get("native_qualification_failed"),
                selected_f=r["parameters"][4] if r["model"]=="LC-J1" else 0.)
            q=np.array(r["fine"]["trace_g_s"])
            delta=q-np.array(s["observed_trace_g_s"])
            for kind,mask in (("primary",np.array(s["trace_mask"],dtype=bool)),
                              ("companion",np.array(s["trace_times_s"])>=5.)):
                row[kind+"_mse_g2_s2"]=float(np.mean(delta[mask]**2))
                row[kind+"_signed_error_g_s"]=float(np.mean(delta[mask]))
            weights=np.array(data["fixture"]["late_weights"][i])
            use=weights!=0
            with np.load(r["artifact_root"]/r["fine"]["prediction"]["file"]) as arr:
                if ft[use].max()>arr["time"][-1]:
                    raise ValueError("Missing inherited late-trend support")
                row["late_trend_g_s_s"]=float(np.dot(np.interp(ft[use],arr["time"],arr["bed_flow_g_s"]),weights[use]))
            row["observed_late_trend_g_s_s"]=data["fixture"]["observed_late_trend"][i]
            own.append(row)
        brews.extend(own)
        for p in W.NOMINAL:
            group=[r for r in own if r["pressure_bar"]==p]
            pp=[r for r in rows if r["pressure_bar"]==p]
            condition=dict(arm=arm,model=rows[0]["model"],weight=rows[0]["weight"],pressure_bar=p,
                intended=len(group),available=len(group),detected=sum(r["fine"]["observer"]["detected"] for r in pp),
                selected_f=group[0]["selected_f"],endpoint_observed_g_s=float(np.mean([r["endpoint_observed_g_s"] for r in group])),
                endpoint_predicted_g_s=float(np.mean([r["endpoint_predicted_g_s"] for r in group])),
                endpoint_signed_error_g_s=float(np.mean([r["endpoint_residual_g_s"] for r in group])),
                endpoint_rmse_g_s=float(np.sqrt(np.mean([r["endpoint_residual_g_s"]**2 for r in group]))))
            for k in ("primary","companion"):
                condition[k+"_rmse_g_s"]=float(np.sqrt(np.mean([r[k+"_mse_g2_s2"] for r in group])))
                condition[k+"_signed_error_g_s"]=float(np.mean([r[k+"_signed_error_g_s"] for r in group]))
            conditions.append(condition)
            trend=float(np.mean([r["late_trend_g_s_s"] for r in group]))
            sign=L.C.C.B.mean_trend_sign(trend)
            trends.append(dict(arm=arm,weight=rows[0]["weight"],pressure_bar=p,
                predicted_g_s_s=trend,observed_g_s_s=float(np.mean([r["observed_late_trend_g_s_s"] for r in group])),
                sign=sign,inherited_resolved_rising_condition=bool(p in (2.,3.5,4.,5.,6.)),matches_rising=sign=="POSITIVE"))
            for step,dt in (("fine",.005),("search",.02)):
                components=[r[step]["objective_components"] for r in pp]
                losses.append(dict(arm=arm,weight=rows[0]["weight"],pressure_bar=p,step_s=dt,
                    **{k:float(np.mean([r[k] for r in components])) for k in ("flow","onset","weighted_onset","joint")},
                    intended=len(pp),available=len(pp),detected=sum(r[step]["observer"]["detected"] for r in pp)))
    return brews,conditions,trends,losses


def low_summaries(flow,condition):
    rows=[]
    for arm in dict.fromkeys(r["arm"] for r in flow):
        cc=[r for r in condition if r["arm"]==arm]
        byp={r["pressure_bar"]:r for r in cc}
        bb=[r for r in flow if r["arm"]==arm]
        pred=L.C.within_ratio(bb,"endpoint_predicted_g_s")
        obs=L.C.within_ratio(bb,"endpoint_observed_g_s")
        e=[byp[p]["endpoint_signed_error_g_s"] for p in (1.,2.,3.5)]
        rows.append(dict(arm=arm,weight=cc[0]["weight"],bias12_g_s=float(np.mean(e[:2])),mae12_g_s=float(np.mean(np.abs(e[:2]))),
            bias1_3_5_g_s=float(np.mean(e)),mae1_3_5_g_s=float(np.mean(np.abs(e))),
            within_2bar_ratio=pred["ratio"],within_2bar_denominator=pred["denominator"],observed_ratio=obs["ratio"],
            ratio_absolute_error=abs(pred["ratio"]-obs["ratio"]) if pred["ratio"] is not None else None,
            brew_1_2_residual_g_s=next(r["endpoint_residual_g_s"] for r in bb if r["brew"]=="1-2"),
            held_3_5_residual_g_s=e[2],f_1bar=byp[1.]["selected_f"],f_2bar=byp[2.]["selected_f"],
            f_3_5bar=byp[3.5]["selected_f"]))
    return rows


def pressure_pairs(data,selected,errors,samples):
    """Same 1,000 draws; a pressure absent from a draw has no pressure score."""
    labels=np.array([s["nominal_pressure_bar"] for s in data["sources"]])
    rows=[]
    for w in L.J.WEIGHTS:
        a,b=f"LC-J1_lambda-{w:g}",f"A-J1_lambda-{w:g}"
        for p in W.NOMINAL:
            g=np.flatnonzero(labels==p)
            for metric in ("endpoint","primary_trace","companion_trace","onset"):
                left,right=errors[(a,"fine")][metric],errors[(b,"fine")][metric]
                value=float(np.sqrt(left[g].mean())-np.sqrt(right[g].mean()))
                draws=[]
                for sample in samples:
                    groups=[group for group in sample if labels[group[0]]==p]
                    if groups:
                        draws.append(float(np.mean([np.sqrt(left[x].mean())-np.sqrt(right[x].mean()) for x in groups])))
                lo,hi=np.quantile(draws,[.025,.975])
                counts=[sum(selected[arm][i]["fine"]["observer"]["detected"] for i in g) for arm in (a,b)]
                bound=metric=="onset" and min(counts)<len(g)
                rows.append(dict(weight=w,pressure_bar=p,metric=metric,
                    LC_score=float(np.sqrt(left[g].mean())),A_score=float(np.sqrt(right[g].mean())),difference=value,
                    lower_95=float(lo),upper_95=float(hi),resamples_intended=1000,resamples_with_pressure=len(draws),
                    intended=len(g),available=len(g),LC_detected=counts[0],A_detected=counts[1],
                    f=selected[a][g[0]]["parameters"][4],
                    interpretation="computed bound difference; not a bound on true-error difference" if bound else "paired RMSE difference",
                    interval_scope=CONDITIONAL+"; pressure interval conditional on that pressure appearing in the shared draw"))
    return rows


def descriptive_curves(args,data):
    """Single-curve derivatives and global capacity extrema, distinct from LOCO."""
    rows=[]
    for w in L.J.WEIGHTS:
        a=data["reference"][(w,"DESCRIPTIVE_ALL")]["parameters"]
        lc=json.loads((args.work/"fits"/(R.R.key("LC-J1",w,None)+".json")).read_text())["parameters"]
        for model,p in (("A-J1",[*a[:4],0.,a[4]]),("LC-J1",lc)):
            peak=L.C.D.plain(L.C.global_peak(p[:5],"LC"))
            pp=np.array([9.,11.,13.])
            cap=L.capacity(p,pp)
            slope=float(np.dot(pp-pp.mean(),cap-cap.mean())/np.dot(pp-pp.mean(),pp-pp.mean()))
            rows.append(dict(weight=w,model=model,scope="one DESCRIPTIVE_ALL capacity curve",
                f=p[4],capacity_at_9_11_13_g_s=cap.tolist(),capacity_slope_9_13_g_s_bar=slope,
                global_capacity_maximum=peak,
                qualification="Capacity slope is neither out-of-fold condition-mean slope nor finite-time flow slope"))
    return rows


def numerical_tables(rows,reports):
    cases,scores=[],[]
    for r in rows:
        f,s=r["fine"],r["search"]
        of,os=f["observer"],s["observer"]
        cases.append(dict(arm=r["arm"],weight=r["weight"],scope=r["scope"],brew=r.get("brew"),pressure_bar=r["pressure_bar"],
            fine_detected=of["detected"],search_detected=os["detected"],detection_changed=of["detected"]!=os["detected"],
            fine_onset_s=of["onset_s"],search_onset_s=os["onset_s"],censor_bound_s=of["censor_bound_s"],
            onset_fine_minus_search_s=of["onset_s"]-os["onset_s"] if of["detected"] and os["detected"] else None,
            endpoint_fine_minus_search_g_s=f["endpoint_g_s"]-s["endpoint_g_s"],
            maximum_common_trace_difference_g_s=float(np.max(np.abs(np.array(f["trace_g_s"])-np.array(s["trace_g_s"]))))))
    for arm,r in reports.items():
        for metric in ("endpoint","primary_trace","companion_trace","onset"):
            scores.append(dict(arm=arm,weight=r["weight"],metric=metric,fine_score=r[metric+"_rmse"],
                search_score=r[metric+"_search_rmse"],fine_minus_search=r[metric+"_fine_minus_search"],
                intended=56,available=56,fine_detected=r["fine_detected"],search_detected=r["search_detected"],
                onset_is_lower_bound=r["onset_is_lower_bound"] if metric=="onset" else False))
    return cases,scores


def figure(flow,condition,onset,reports,preview):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec=VizSpec(id="lc_joint_transfer_001",title="Held-out LC-J1 versus saved A-J1",class_=1,
        producer=Producer(module=__name__,function="scores",result_map={"scores":"reports"}),
        badge="OBSERVED",evidence_strength="post-fit reconstruction",components=[],
        fidelity_ceiling="Retrospective held-out comparison on exposed cohort; not physical validation.",
        render_fn=__name__+":figure",caption="Primary lambda=1. Censored detector medians are lower bounds; physical front is separate.",
        outputs=["COMPARISON.svg"],used_in="PW-LC-JOINT-TRANSFER-001")
    if spec.validate():
        raise ValueError(spec.validate())
    colors={"A-J1":"#be4b35","LC-J1":"#007c91"}
    with matplotlib.rc_context({"svg.hashsalt":"PW-LC-JOINT-TRANSFER-001","font.size":10}):
        fig,axes=plt.subplots(1,3,figsize=(15,4.9))
        for m in ("A-J1","LC-J1"):
            arm=m+"_lambda-1"
            bb=[r for r in flow if r["arm"]==arm and r["pressure_bar"]<=3.5]
            offset=-.06 if m=="A-J1" else .06
            for p in (1.,2.,3.5):
                g=[r for r in bb if r["pressure_bar"]==p]
                x=p+offset+np.linspace(-.04,.04,len(g))
                axes[0].scatter(x,[r["endpoint_residual_g_s"] for r in g],color=colors[m],s=20,alpha=.6)
            cc=[r for r in condition if r["arm"]==arm and r["pressure_bar"]<=3.5]
            axes[0].plot([r["pressure_bar"] for r in cc],[r["endpoint_signed_error_g_s"] for r in cc],"o-",color=colors[m],label=m)
            oo=[r for r in onset if r["arm"]==arm]
            known=[r for r in oo if r["predicted_median_s"] is not None]
            axes[1].plot([r["pressure_bar"] for r in known],[r["predicted_median_s"] for r in known],"o-",color=colors[m],label=m+" detector")
            censored=[r for r in oo if r["predicted_median_s"] is None]
            axes[1].scatter([r["pressure_bar"]+offset for r in censored],[r["median_lower_bound_s"] for r in censored],marker="$↑$",s=150,color=colors[m])
            axes[1].plot([r["pressure_bar"] for r in oo],[r["front_median_s"] for r in oo],"--",color=colors[m],alpha=.6,label=m+" front")
            high=[r for r in condition if r["arm"]==arm and r["pressure_bar"]>=9.]
            axes[2].plot([r["pressure_bar"] for r in high],[r["endpoint_predicted_g_s"] for r in high],"o-",color=colors[m],label=m)
        obs=[r for r in onset if r["arm"]=="A-J1_lambda-1"]
        axes[1].plot([r["pressure_bar"] for r in obs],[r["observed_median_s"] for r in obs],"k.-",label="Observed detector")
        high=[r for r in condition if r["arm"]=="A-J1_lambda-1" and r["pressure_bar"]>=9.]
        axes[2].plot([r["pressure_bar"] for r in high],[r["endpoint_observed_g_s"] for r in high],"k.-",label="Observed")
        axes[0].axhline(0,color=".3",lw=.8); axes[0].set_xticks([1.,2.,3.5])
        axes[0].set_ylabel("Endpoint prediction − observation (g/s)")
        axes[1].set_ylabel("Onset / physical arrival (s)")
        axes[2].set_ylabel("Endpoint flow (g/s)"); axes[2].set_xticks([9,11,13])
        for ax,title in zip(axes,("Low pressure · every held-out brew","Cup detector and physical front","High pressure · separate LOCO fits")):
            ax.set_title(title); ax.set_xlabel("Nominal pressure (bar)"); ax.grid(alpha=.15); ax.legend(fontsize=8)
        a,l=reports["A-J1_lambda-1"],reports["LC-J1_lambda-1"]
        fig.suptitle("Primary λ=1 · retained J1 timing, recovery and beverage observer")
        fig.text(.02,.052,f"Detections: A-J1 {a['fine_detected']}/56, LC-J1 {l['fine_detected']}/56; at 1 bar {a['one_bar_detected']}/5 and {l['one_bar_detected']}/5. Arrows denote median lower bounds.",fontsize=9)
        fig.text(.02,.017,spec.badge_line()+" · Waszkiewicz et al., Zenodo 18046315, CC BY 4.0. Lines connect different fold fits.",fontsize=8)
        fig.tight_layout(rect=(0,.09,1,.94))
        fig.savefig(R.OUT/"COMPARISON.svg",metadata={"Date":None})
        fig.savefig(preview/"COMPARISON.png",dpi=140)
        plt.close(fig)


def fit_diagnostics(args):
    fits,starts,curves,near_records=[],[],[],[]
    grid=np.linspace(0.,13.,261)
    for weight,held in R.jobs():
        key=R.R.key("LC-J1",weight,held)
        fit=json.loads((args.work/"fits"/(key+".json")).read_text())
        d=json.loads((args.work/"diagnostics"/(key+".json")).read_text())
        p=np.array(fit["parameters"])
        scale=1e-6*max(1.,fit["objective"])
        row=dict(key=key,weight=weight,fold=fit["fold"],**dict(zip(L.ORDER,p)),Mc_g=fit["mc_fixed_g"],
            saved_A_J1_objective=d["saved_A_J1_search"]["objective"],selected_LC_J1_objective=fit["objective"],
            frozen_f0_objective=d["frozen_f0_search"]["objective"],inherited_objective_disagreement_scale=scale,
            selected_minus_frozen_f0=fit["objective"]-d["frozen_f0_search"]["objective"],
            frozen_f0_minus_saved_A_J1=d["frozen_f0_search"]["objective"]-d["saved_A_J1_search"]["objective"],
            winning_start=fit["winning_start"],starts=len(fit["starts"]),core_hours=fit["cpu_seconds"]/3600,
            fit_sha256=R.R.R.digest(args.work/"fits"/(key+".json")))
        for name in ("saved_A_J1","LC_J1","frozen_f0"):
            change=d[name+"_fine"]["objective"]-d[name+"_search"]["objective"]
            row[name+"_fine_objective"]=d[name+"_fine"]["objective"]
            row[name+"_fine_minus_search"]=change
            row[name+"_training_detected"]=d[name+"_fine"]["detected"]
        improvement=-row["frozen_f0_minus_saved_A_J1"]
        fine_improvement=d["saved_A_J1_fine"]["objective"]-d["frozen_f0_fine"]["objective"]
        row["frozen_f0_improvement_fine_minus_search"]=fine_improvement-improvement
        row["frozen_f0_improves_saved_A_beyond_both_diagnostics"]=bool(
            improvement>scale and fine_improvement>0 and abs(fine_improvement-improvement)<improvement)
        term_gain=-row["selected_minus_frozen_f0"]
        fine_term_gain=d["frozen_f0_fine"]["objective"]-d["LC_J1_fine"]["objective"]
        row["added_term_gain_fine"]=fine_term_gain
        row["added_term_gain_fine_minus_search"]=fine_term_gain-term_gain
        row["added_term_gain_resolved_at_fixed_common_parameters"]=bool(
            term_gain>scale and fine_term_gain>0 and abs(fine_term_gain-term_gain)<term_gain)
        gain=row["saved_A_J1_objective"]-row["selected_LC_J1_objective"]
        fine_gain=d["saved_A_J1_fine"]["objective"]-d["LC_J1_fine"]["objective"]
        row["LC_improvement_over_saved_A_fine_minus_search"]=fine_gain-gain
        row["LC_training_gain_resolved_at_search_step"]=bool(
            gain>scale and fine_gain>0 and abs(fine_gain-gain)<gain)
        redundant=(["n at f=1"] if p[4]==1. else [])+(["f at n=1"] if p[2]==1. else [])
        row["structural_redundancy"]="; ".join(redundant) if redundant else "none established"
        lo,hi=L.bounds()
        row["transformed_bound_distances"]=[float(min(z-l,h-z)) for z,l,h in zip(L.coordinates(p),lo,hi)]
        row["selected_capacity_bounds"]=L.C.bound_record(L.coordinates(p)[:5],"LC")
        row["selected_tau0_fraction_from_bound"]=float(min(p[5],100-p[5])/100)
        row["capacity_peak"]=L.C.D.plain(L.C.global_peak(p[:5],"LC"))
        near=[]
        for r in fit["starts"]:
            starts.append(dict(key=key,weight=weight,fold=fit["fold"],number=r["number"],start=r["start"],
                initial_coordinates=r["initial_coordinates"],initial_objective=r["initial_objective"],
                success=r["success"],message=r.get("message"),nfev=r.get("nfev"),
                returned_objective=r.get("returned_objective"),returned_parameters=r.get("returned_parameters"),
                best_objective=r["best"]["objective"],best_parameters=r["best"]["parameters"],
                objective_above_selected=r["best"]["objective"]-fit["objective"],
                best_capacity_bounds=L.C.bound_record(L.coordinates(r["best"]["parameters"])[:5],"LC"),
                best_tau0_distance_s=min(r["best"]["parameters"][-1],100-r["best"]["parameters"][-1]),
                projected_requests=len(r["projections"]),cpu_seconds=r["cpu_seconds"],trials=r["trials"]))
            path=args.work/"trials"/r["trials"]["file"]
            if R.R.R.digest(path)!=r["trials"]["sha256"]:
                raise ValueError("Trial history changed")
            with gzip.open(path,"rt") as stream:
                trials=json.load(stream)
            coordinates=np.array([t["coordinates"] for t in trials])
            starts[-1]["evaluated_boundary_contacts"]={L.ORDER[k]:dict(
                exact_lower=int(np.sum(coordinates[:,k]==lo[k])),
                exact_upper=int(np.sum(coordinates[:,k]==hi[k])) if np.isfinite(hi[k]) else None,
                near_finite=int(np.sum(np.minimum(coordinates[:,k]-lo[k],hi[k]-coordinates[:,k])/(hi[k]-lo[k])<=1e-6))
                    if np.isfinite(hi[k]) else None) for k in range(6)}
            near.extend(t for t in trials if t["objective"]<=fit["objective"]+scale)
        unique={tuple(t["parameters"]):t for t in near}
        pars=np.array(list(unique))
        caps=np.array([L.capacity(p,grid) for p in pars])
        row["near_objective_unique_vectors"]=len(pars)
        row["near_objective_parameter_ranges"]=np.c_[pars.min(axis=0),pars.max(axis=0)].tolist()
        row["near_objective_max_capacity_spread_g_s"]=float(np.max(np.ptp(caps,axis=0)))
        row["capacity_envelope_scope"]="sampled near-objective vectors on 0–13 bar grid, spacing .05 bar; not a continuum supremum or confidence interval"
        row["start_objective_disagreement"]=bool(np.ptp([r["best"]["objective"] for r in fit["starts"]])>scale)
        near_records.append(dict(key=key,objective_scale=scale,vectors=list(unique.values())))
        for pressure,chosen,cmin,cmax in zip(grid,L.capacity(p,grid),caps.min(axis=0),caps.max(axis=0)):
            curves.append(dict(key=key,weight=weight,fold=fit["fold"],pressure_bar=pressure,
                selected_capacity_g_s=chosen,near_objective_capacity_min_g_s=cmin,near_objective_capacity_max_g_s=cmax))
        fits.append(row)
    path=args.work/"NEAR_OBJECTIVE_VECTORS.json.gz"
    with gzip.open(path,"wt") as stream:
        json.dump(near_records,stream,allow_nan=False,separators=(",",":"))
    return fits,starts,curves,dict(file=path.name,sha256=R.R.R.digest(path))


def fold_isolation(args,data):
    rows=[]
    for w,h in R.jobs():
        path=args.work/"fits"/(R.R.key("LC-J1",w,h)+".json")
        r=json.loads(path.read_text())
        training=[s for s in data["sources"] if h is None or s["nominal_pressure_bar"]!=h]
        held=[s for s in data["sources"] if h is not None and s["nominal_pressure_bar"]==h]
        if r["training_brews"]!=[s["brew"] for s in training]:
            raise ValueError("Selected LC-J1 fit training cohort mismatch")
        if r["mc_fixed_g"]!=data["bank"][R.R.label(h)][4]:
            raise ValueError("Selected LC-J1 fit fixed Mc mismatch")
        rows.append(dict(key=r["key"],weight=w,fold=r["fold"],training_brews=r["training_brews"],
            held_brews=[s["brew"] for s in held],training_conditions=sorted({s["nominal_pressure_bar"] for s in training}),
            held_condition_bar=h,Mc_g=r["mc_fixed_g"],source_fold_key=R.R.label(h),
            historical_LC_seed_source="PRESSURE_PEAK_STAGE_C3E/RESULT_TABLE.csv: record_type=fit, candidate=LC",
            historical_LC_seed_parameters=data["lc_seeds"][r["fold"]],
            saved_A_J1_key=data["reference"][(w,r["fold"])]["key"],
            start_schedule=R.starts(data,w,h),fit_sha256=R.R.R.digest(path)))
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp","native","raw","screen","joint","work"):
        p.add_argument("--"+flag,type=Path,required=True)
    args=p.parse_args()
    cpu=time.process_time()
    data,rows,arms=load_predictions(args)
    reports,paired,selected,errors,samples=scores(data,rows,arms)
    onset_brew,onset_pressure=Q.onset_tables(data["sources"],selected,reports)
    context_path=R.ROOT/"docs/research/JOINT_CLOCK_001/COMPARISON_TABLE.csv"
    historical=R.table(context_path)
    for w in L.J.WEIGHTS:
        saved=next(r for r in historical if r["arm"]==f"J1_lambda-{w:g}")
        replay=reports[f"A-J1_lambda-{w:g}"]
        for field in ("endpoint_rmse","primary_trace_rmse","companion_trace_rmse","onset_rmse"):
            np.testing.assert_allclose(replay[field],float(saved[field]),rtol=1e-12,atol=0)
        if replay["fine_detected"]!=int(saved["fine_detected"]):
            raise ValueError("A-J1 aggregate detection replay differs")
    context=[dict(r,role="historical context; compatible FORM_A masks; no refit",
        source=str(context_path.relative_to(R.ROOT)),source_sha256=R.R.R.digest(context_path))
        for r in historical if r["model"] in ("D0","B1","J0","J1","J2")]
    flow,conditions,trends,losses=flow_tables(data,selected)
    low=low_summaries(flow,conditions)
    sweep,extrema=Q.extrema(rows,onset_pressure,arms)
    for r in extrema:
        own=[s for s in sweep if s["arm"]==r["arm"]]
        yy=np.array([s["endpoint_scale_liquid_flow_g_s"] for s in own])
        r["flow_local_grid_maxima_bar"]=[own[i]["pressure_bar"] for i in range(1,len(own)-1)
            if yy[i]>=yy[i-1] and yy[i]>=yy[i+1] and (yy[i]>yy[i-1] or yy[i]>yy[i+1])]
        r["flow_local_grid_minima_bar"]=[own[i]["pressure_bar"] for i in range(1,len(own)-1)
            if yy[i]<=yy[i-1] and yy[i]<=yy[i+1] and (yy[i]<yy[i-1] or yy[i]<yy[i+1])]
    from . import pressure_peak_scorecard as bands
    from . import pressure_peak_stage_c0 as c0
    for arm,r in reports.items():
        matches=sum(x["matches_rising"] for x in trends if x["arm"]==arm and x["inherited_resolved_rising_condition"])
        r.update(resolved_trend_matches=matches,resolved_trend_total=5,trend_grade=bands.trend_grade(matches))
        bias=next(x["bias1_3_5_g_s"] for x in low if x["arm"]==arm)
        r.update(low_pressure_bias_g_s=bias,low_pressure_bias_grade=c0.bias_grade(bias))
    fits,starts,curves,near=fit_diagnostics(args)
    pressure_paired=pressure_pairs(data,selected,errors,samples)
    capacity=descriptive_curves(args,data)
    numerical_cases,numerical_scores=numerical_tables(rows,reports)
    isolation=fold_isolation(args,data)
    outputs={"SCORES.csv":list(reports.values()),"PAIRED_COMPARISONS.csv":paired,
        "ONSET_BY_BREW.csv":onset_brew,"ONSET_BY_PRESSURE.csv":onset_pressure,
        "FLOW_BY_BREW.csv":flow,"FLOW_BY_PRESSURE.csv":conditions,"LATE_TRENDS.csv":trends,
        "LOSS_BY_PRESSURE.csv":losses,"LOW_PRESSURE.csv":low,"DESCRIPTIVE_SWEEP.csv":sweep,
        "EXTREMA.csv":extrema,"FITS.csv":fits,"OPTIMIZER_STARTS.csv":starts,"CAPACITY_CURVES.csv":curves,
        "PAIRED_PRESSURE.csv":pressure_paired,"DESCRIPTIVE_CAPACITY.csv":capacity,"HISTORICAL_CONTEXT.csv":context,
        "NUMERICAL_BY_CASE.csv":numerical_cases,"NUMERICAL_SCORES.csv":numerical_scores,"FOLD_ISOLATION.csv":isolation}
    for name,values in outputs.items():
        R.R.R.csv_write(R.OUT/name,values)
    R.R.R.write_json(args.work/"PAIRED_RESAMPLES.json",samples)
    figure(flow,conditions,onset_pressure,reports,args.work)
    R.R.R.write_json(args.work/"REPORT.json",dict(scores=reports,paired=paired,low=low,
        resamples_sha256=R.R.R.digest(args.work/"PAIRED_RESAMPLES.json"),near_objective_vectors=near,
        cpu_seconds=time.process_time()-cpu))


if __name__=="__main__":
    main()

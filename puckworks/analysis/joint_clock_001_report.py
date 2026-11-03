"""Report only frozen joint-clock predictions; inherited scores, bands and draws."""
import argparse
import json
from pathlib import Path
import time

import numpy as np

from . import joint_clock_001 as J
from . import joint_clock_001_evaluate as E
from . import joint_clock_001_run as R
from . import wetting_screen_001 as W
from . import wetting_screen_001_report as P

CONDITIONAL = "conditional on fitted parameters and fixed training-derived Mc; no refit bootstrap"


def load_predictions(args):
    data = R.load_data(args)
    rows = []
    index = json.loads((args.work/"EVALUATION_INDEX.json").read_text())
    expected = {r["key"]:r["metadata_sha256"] for r in index["records"]}
    for path in sorted((args.work/"predictions").glob("*.json")):
        if R.R.digest(path) != expected.get(path.stem):
            raise ValueError("Prediction metadata differs from frozen evaluation index")
        row = json.loads(path.read_text())
        if row["identity"]["fit_identity"] != R.identity():
            raise ValueError("Frozen fit identity changed")
        fit = args.work/"fits"/(R.key(row["model"], row["weight"],
                None if row["scope"] == "descriptive" else row["pressure_bar"])+".json")
        if R.R.digest(fit) != row["identity"]["fit_sha256"]:
            raise ValueError("Frozen parameters changed")
        if row["identity"]["evaluator_sha256"] not in E.accepted_evaluator_hashes():
            raise ValueError("Frozen evaluator changed")
        for step in ("fine", "search"):
            artifact = row[step]["prediction"]
            if R.R.digest(args.work/"predictions"/artifact["file"]) != artifact["sha256"]:
                raise ValueError("Frozen arrays changed")
        rows.append(row)
    joint = [E.arm_name(m, w) for w in J.WEIGHTS for m in J.MODELS]
    coverage = [dict(arm=a, scope=s, intended=n,
        available=sum(r["arm"] == a and r["scope"] == s for r in rows))
        for a in joint for s, n in (("held_out", 56), ("descriptive", 23))]
    R.R.csv_write(R.OUT/"COVERAGE.csv", coverage)
    if any(r["available"] != r["intended"] for r in coverage):
        raise ValueError("Incomplete cohort; coverage disclosed, no subset score")
    # These are retained, authenticated 0.005/0.02-s reference predictions.
    # Z is the original D0 liquid clock with the explicit fresh-bed R0 observer.
    reference_hashes = []
    screen_manifest = json.loads((R.ROOT/"docs/research/WETTING_SCREEN_001/RUN_MANIFEST.json").read_text())
    retained = {r["key"]:r["metadata_sha256"] for r in screen_manifest["predictions"]}
    for path in sorted((args.screen/"predictions").glob("*.json")):
        row = json.loads(path.read_text())
        if row["arm"] not in ("W0", "W1", "W2", "W2T", "Z"):
            continue
        if R.R.digest(path) != retained.get(path.stem):
            raise ValueError("Retained reference metadata differs from committed screen manifest")
        if row["identity"]["predictor_sha256"] != R.R.digest(Path(W.__file__)):
            raise ValueError("Retained screen predictor changed")
        for step in ("fine", "search"):
            artifact = row[step]["prediction"]
            if R.R.digest(args.screen/"predictions"/artifact["file"]) != artifact["sha256"]:
                raise ValueError("Retained screen prediction changed")
        reference_hashes.append(dict(file=path.name, sha256=R.R.digest(path),
                                     role="D0 original clock + R0 observer" if row["arm"] == "Z" else row["arm"]))
        if row["arm"] == "Z":
            row["arm"] = "D0"
        row.update(model=row["arm"], weight=None)
        rows.append(row)
    for a in ("D0", "W0", "W1", "W2", "W2T"):
        if sum(r["arm"] == a and r["scope"] == "held_out" for r in rows) != 56:
            raise ValueError("Incomplete retained comparator")
    return data, rows, ["D0", "W0", "W1", "W2", "W2T", *joint], reference_hashes


def scores(sources, rows, arms):
    conditions = np.array([s["nominal_pressure_bar"] for s in sources])
    observed = np.array([s["observed_onset_for_scoring_only_s"] for s in sources])
    groups, samples = P.paired_samples(conditions)
    errors, selected, reports = {}, {}, {}
    for arm in arms:
        by_brew = {r["brew"]:r for r in rows if r["arm"] == arm and r["scope"] == "held_out"}
        selected[arm] = [by_brew[s["brew"]] for s in sources]
        r0 = selected[arm][0]
        reports[arm] = dict(arm=arm, model=r0["model"], weight=r0["weight"],
            primary_weight=r0["weight"] == 1., intended=56, available=56,
            interval_scope=CONDITIONAL, score_step_s=.005, sensitivity_step_s=.02)
        for numerical in ("fine", "search"):
            pred = [r[numerical] for r in selected[arm]]
            obs = [r["observer"] for r in pred]
            squared = P.hydraulic_errors(sources, [r["endpoint_g_s"] for r in pred],
                                         [r["trace_g_s"] for r in pred])
            squared["onset"] = np.array([W.squared_onset(o,y) for o,y in zip(obs,observed)])
            errors[(arm,numerical)] = squared
            reports[arm][numerical+"_detected"] = sum(o["detected"] for o in obs)
        reports[arm]["censored"] = 56-reports[arm]["fine_detected"]
        reports[arm]["onset_is_lower_bound"] = bool(reports[arm]["censored"])
        reports[arm].update(P.response(np.array([r["fine"]["endpoint_g_s"] for r in selected[arm]]),
            np.array([s["pressure_bar"][-1] for s in sources]), conditions))
        for pressure in (1.,2.,3.5):
            g = conditions == pressure
            reports[arm][f"residual_{pressure:g}_bar_g_s"] = float(np.mean(
                [r["fine"]["endpoint_g_s"]-s["observed_endpoint_g_s"]
                 for r,s,yes in zip(selected[arm],sources,g) if yes]))
    b1 = P.hydraulic_errors(sources, [s["b1_endpoint_g_s"] for s in sources],
                           [s["b1_trace_g_s"] for s in sources])
    comparisons = [(E.arm_name(a,w), E.arm_name(b,w)) for w in J.WEIGHTS
                   for a,b in (("J1","J0"),("J2","J0"),("J2","J1"))]
    comparisons += [(E.arm_name(m,w),"D0") for w in J.WEIGHTS for m in J.MODELS]
    paired, b1_scores = [], {}
    for metric in ("endpoint","primary_trace","companion_trace","onset"):
        labels = arms if metric == "onset" else [*arms,"B1"]
        square = [errors[(a,"fine")][metric] if a != "B1" else b1[metric] for a in labels]
        points, draws = P.score_and_draws(square,groups,samples)
        for i,a in enumerate(arms):
            r = reports[a]
            r[metric+"_rmse"] = float(points[i])
            r[metric+"_interval"] = np.quantile(draws[:,i],[.025,.975]).tolist()
            coarse = errors[(a,"search")][metric]
            r[metric+"_search_rmse"] = float(np.mean([np.sqrt(coarse[g].mean()) for g in groups]))
            r[metric+"_fine_minus_search"] = float(points[i]-r[metric+"_search_rmse"])
            if metric != "onset":
                r[metric+"_minus_b1_interval"] = np.quantile(draws[:,i]-draws[:,-1],[.025,.975]).tolist()
                r[metric+"_comparison_vs_b1"] = P.flow_comparison(r[metric+"_minus_b1_interval"])
                b1_scores[metric] = float(points[-1])
        for a,b in comparisons:
            i,j = labels.index(a),labels.index(b)
            ci = np.quantile(draws[:,i]-draws[:,j],[.025,.975])
            bound = metric == "onset" and (reports[a]["censored"] or reports[b]["censored"])
            paired.append(dict(left=a,right=b,metric=metric,left_score=float(points[i]),right_score=float(points[j]),
                difference=float(points[i]-points[j]),lower_95=float(ci[0]),upper_95=float(ci[1]),
                interpretation="difference of computed bounds; not a bound on their difference" if bound else "paired RMSE difference",
                interval_scope=CONDITIONAL))
    for a,r in reports.items():
        r["onset_grade"] = P.onset_grade(r["onset_rmse"],r["censored"])
        comparison = r["endpoint_comparison_vs_b1"]
        r["accuracy_grade_vs_b1"] = ("MEETS" if comparison in ("BETTER","TIE") else
            "NEAR" if comparison == "UNRESOLVED" and r["endpoint_rmse"] < b1_scores["endpoint"] else "MISSES")
        if a == "D0":
            r["onset_grade"] = "NOT_SCORED/added_R0_observer_diagnostic"
    return reports,paired,selected,b1_scores,samples


def onset_tables(sources,selected,reports):
    brews,conditions = [],[]
    for arm,rows in selected.items():
        for source,row in zip(sources,rows):
            o = row["fine"]["observer"]
            y = source["observed_onset_for_scoring_only_s"]
            brews.append(dict(arm=arm,model=row["model"],weight=row["weight"],brew=source["brew"],
                pressure_bar=source["nominal_pressure_bar"],observed_onset_s=y,
                predicted_onset_s=o["onset_s"],detected=o["detected"],censor_bound_s=o["censor_bound_s"],
                signed_error_s=o["onset_s"]-y if o["detected"] else None,
                signed_error_lower_bound_s=o["censor_bound_s"]-y if not o["detected"] else None,
                front_s=row["fine"]["prediction"]["front_s"],front_censored_at_100=row["fine"]["prediction"]["front_right_censored"],
                squared_loss_s2=W.squared_onset(o,y),native_qualification_failed=row.get("native_qualification_failed")))
        for p in W.NOMINAL:
            group = [r for r in brews if r["arm"] == arm and r["pressure_bar"] == p]
            exact,lower = W.median_with_censor([r["predicted_onset_s"] for r in group],[r["censor_bound_s"] for r in group])
            y = float(np.median([r["observed_onset_s"] for r in group]))
            front,fb = W.median_with_censor([r["front_s"] for r in group],[100.]*len(group))
            conditions.append(dict(arm=arm,model=rows[0]["model"],weight=rows[0]["weight"],pressure_bar=float(p),
                intended=len(group),available=len(group),detected=sum(r["detected"] for r in group),
                observed_median_s=y,predicted_median_s=exact,median_lower_bound_s=lower,
                signed_median_error_s=exact-y if exact is not None else None,
                signed_median_error_lower_bound_s=lower-y if exact is None else None,
                front_median_s=front,front_median_lower_bound_s=fb,
                censor_bound_min_s=min(r["censor_bound_s"] for r in group),censor_bound_max_s=max(r["censor_bound_s"] for r in group)))
        high = [r for r in conditions if r["arm"] == arm and r["pressure_bar"] >= 3.5]
        reports[arm]["supplementary_condition_median_rms_s"] = float(np.sqrt(np.mean([
            r["signed_median_error_s"]**2 if r["signed_median_error_s"] is not None else
            max(0.,r["signed_median_error_lower_bound_s"])**2 for r in high])))
        reports[arm]["supplementary_is_bound"] = any(r["predicted_median_s"] is None for r in high)
        reports[arm]["one_bar_detected"] = next(r["detected"] for r in conditions if r["arm"]==arm and r["pressure_bar"]==1.)
        reports[arm]["two_bar_detected"] = next(r["detected"] for r in conditions if r["arm"]==arm and r["pressure_bar"]==2.)
    return brews,conditions


def loss_and_flow_tables(sources,selected,reports):
    losses,flow_rows,bed_rows,numerics = [],[],[],[]
    conditions = np.array([s["nominal_pressure_bar"] for s in sources])
    groups = [np.flatnonzero(conditions==p) for p in W.NOMINAL]
    for arm,rows in selected.items():
        for source,row in zip(sources,rows):
            fine,coarse = row["fine"],row["search"]
            error = P.hydraulic_errors([source],[fine["endpoint_g_s"]],[fine["trace_g_s"]])
            flow_rows.append(dict(arm=arm,model=row["model"],weight=row["weight"],brew=source["brew"],
                pressure_bar=source["nominal_pressure_bar"],endpoint_observed_g_s=source["observed_endpoint_g_s"],
                endpoint_predicted_g_s=fine["endpoint_g_s"],endpoint_residual_g_s=fine["endpoint_g_s"]-source["observed_endpoint_g_s"],
                primary_mse_g2_s2=float(error["primary_trace"][0]),companion_mse_g2_s2=float(error["companion_trace"][0]),
                endpoint_beverage_minus_liquid_flow_g_s=fine["endpoint_beverage_minus_liquid_flow_g_s"]))
            of,oc = fine["observer"],coarse["observer"]
            numerics.append(dict(arm=arm,scope="held_out",brew=source["brew"],pressure_bar=source["nominal_pressure_bar"],
                detector_fine_s=of["onset_s"],detector_search_s=oc["onset_s"],
                fine_detected=of["detected"],search_detected=oc["detected"],detection_changed=of["detected"]!=oc["detected"],
                detector_fine_minus_search_s=of["onset_s"]-oc["onset_s"] if of["detected"] and oc["detected"] else None,
                endpoint_fine_minus_search_g_s=fine["endpoint_g_s"]-coarse["endpoint_g_s"]))
        if rows[0]["model"] in J.MODELS:
            for step in ("fine","search"):
                for p,g in zip(W.NOMINAL,groups):
                    components = [rows[i][step]["objective_components"] for i in g]
                    losses.append(dict(arm=arm,model=rows[0]["model"],weight=rows[0]["weight"],
                        scope="held_out",step_s=.005 if step=="fine" else .02,pressure_bar=float(p),brews=len(g),
                        flow_component=float(np.mean([c["flow"] for c in components])),
                        onset_component=float(np.mean([c["onset"] for c in components])),
                        weighted_onset_component=float(np.mean([c["weighted_onset"] for c in components])),
                        joint_component=float(np.mean([c["joint"] for c in components])),
                        detected=sum(rows[i][step]["observer"]["detected"] for i in g)))
        if rows[0]["model"] == "J2":
            for step in ("fine","search"):
                err = P.hydraulic_errors(sources,[r[step]["unshifted_endpoint_g_s"] for r in rows],
                    [r[step]["unshifted_trace_g_s"] for r in rows])
                for metric,squared in err.items():
                    bed_rows.append(dict(arm=arm,weight=rows[0]["weight"],step_s=.005 if step=="fine" else .02,
                        metric=metric,unshifted_bed_rmse=float(np.mean([np.sqrt(squared[g].mean()) for g in groups])),
                        shifted_scale_rmse=reports[arm][metric+("_rmse" if step=="fine" else "_search_rmse")],
                        disposition="unshifted bed diagnostic; graded flow is scale flow"))
    return losses,flow_rows,bed_rows,numerics


def extrema(rows,conditions,arms):
    sweep,ext = [],[]
    for arm in arms:
        selected = sorted([r for r in rows if r["arm"]==arm and r["scope"]=="descriptive"],key=lambda r:r["pressure_bar"])
        for r in selected:
            p = r["fine"]
            sweep.append(dict(arm=arm,model=r["model"],weight=r["weight"],pressure_bar=r["pressure_bar"],
                front_s=p["prediction"]["front_s"],front_censored_at_100=p["prediction"]["front_right_censored"],
                detector_onset_s=p["observer"]["onset_s"],detected=p["observer"]["detected"],censor_bound_s=p["observer"]["censor_bound_s"],
                endpoint_scale_liquid_flow_g_s=p["endpoint_g_s"],endpoint_bed_liquid_flow_g_s=p["unshifted_endpoint_g_s"]))
        ss = [r for r in sweep if r["arm"]==arm]
        held = [r for r in conditions if r["arm"]==arm]
        known = [r for r in held if r["predicted_median_s"] is not None]
        hm = min((r["predicted_median_s"] for r in known),default=float("inf"))
        unidentified = any(r["predicted_median_s"] is None and r["median_lower_bound_s"]<=hm for r in held)
        record = dict(arm=arm,model=selected[0]["model"],weight=selected[0]["weight"],
            held_out_fastest_detector_nominal_bar=[] if unidentified else [r["pressure_bar"] for r in known if r["predicted_median_s"]==hm],
            held_out_minimum_qualification="unidentified" if unidentified else "nominal grid; folds differ",
            descriptive_forcing="one DESCRIPTIVE_ALL tuple, same 23 constant pressures, 100-s horizon and 0.1-s detector timestamps")
        for name,field,censor in (("front","front_s",100.),("detector","detector_onset_s",98.)):
            known = [r for r in ss if r[field] is not None]
            best = min((r[field] for r in known),default=float("inf"))
            if not known or any(r[field] is None and (r.get("censor_bound_s",censor) if name=="detector" else censor)<=best for r in ss):
                record[name+"_minimum_s"],record[name+"_minimum_pressures_bar"] = None,[]
                record[name+"_qualification"] = "unidentified due to censoring"
            else:
                pp = [r["pressure_bar"] for r in known if r[field]==best]
                record[name+"_minimum_s"],record[name+"_minimum_pressures_bar"] = best,pp
                record[name+"_qualification"] = "flat across grid" if len(pp)==len(ss) else (
                    "boundary minimum" if ss[0]["pressure_bar"] in pp or ss[-1]["pressure_bar"] in pp else "grid minimum/ties")
        pp = [r["pressure_bar"] for r in ss]
        qq = [r["endpoint_scale_liquid_flow_g_s"] for r in ss]
        record["flow_peak_grid_pressures_bar"] = [p for p,q in zip(pp,qq) if q==max(qq)]
        record["flow_peak_interpolated_bar"] = P.quadratic_peak(pp,qq)
        record["flow_peak_qualification"] = "three-point numerical interpolation; no statistical interval" if record["flow_peak_interpolated_bar"] is not None else "boundary or unresolved interpolation"
        record["fitted_front_minimum_Pw_bar"] = selected[0]["parameters"][5] if selected[0]["model"]=="J2" else None
        ext.append(record)
    return sweep,ext


def fit_tables(args):
    fits,starts,training,manifest = [],[],[],[]
    for path in sorted((args.work/"fits").glob("*.json")):
        r = json.loads(path.read_text())
        p = r["parameters"]
        fits.append(dict(key=r["key"],model=r["model"],weight=r["weight"],fold=r["fold"],
            a_g_s_bar=p[0],Pstar_bar=p[1],n=p[2],Pd_bar=p[3],Mc_g=r["mc_fixed_g"],
            tau0_s=p[4] if r["model"]=="J1" else None,k_w0_m2=p[4] if r["model"]=="J2" else None,
            Pw_bar=p[5] if r["model"]=="J2" else None,t_s_s=p[6] if r["model"]=="J2" else None,
            search_training_objective=r["objective"],search_flow_component=r["flow_component"],
            search_onset_component=r["onset_component"],search_detected=r["detected"],
            training_brews=len(r["training_brews"]),equal_minimum_count=r["equal_minimum_count"],
            equal_minimum_ranges=r["equal_minimum_ranges"],transformed_distances_to_bounds=r["distance_to_bounds"],
            starts=len(r["starts"]),successful_starts=sum(s["success"] for s in r["starts"]),
            evaluations=len(r["trials"]),column_calls=r["column_calls"],core_hours=r["cpu_seconds"]/3600,
            fit_sha256=R.R.digest(path),scope="optimizer diagnostics at 0.02 s; final reported held-out scores use 0.005 s"))
        starts.extend(dict(key=r["key"],model=r["model"],weight=r["weight"],fold=r["fold"],
            **s,objective_above_best=s["objective"]-r["objective"]) for s in r["starts"])
        training.extend(dict(key=r["key"],model=r["model"],weight=r["weight"],fold=r["fold"],
            scope="training optimizer diagnostic",step_s=.02,**c) for c in r["condition_components"])
        continuation = r.get("continuation")
        if continuation:
            continuation_source = R.ROOT/"puckworks/analysis/joint_clock_001_resume.py"
            if (continuation["source_sha256"] != R.R.digest(continuation_source) or
                    continuation["failed_sha256"] != R.R.digest(args.work/"failures"/continuation["failed_file"])):
                raise ValueError("Continuation source or retained failed attempt changed")
        manifest.append(dict(key=r["key"],file=path.name,sha256=R.R.digest(path),role="joint fit",
            status=r["status"],core_hours=r["cpu_seconds"]/3600,wall_seconds=r["wall_seconds"],
            continuation=continuation))
    if len(fits)!=144:
        raise ValueError("Incomplete 144-fit cohort")
    return fits,starts,training,manifest


def figures(sources,reports,conditions,losses):
    import matplotlib
    matplotlib.use("Agg")
    matplotlib.rcParams["svg.hashsalt"] = "PW-JOINT-CLOCK-001"
    import matplotlib.pyplot as plt
    colors = dict(J0="#6b4c9a",J1="#007f5f",J2="#c2410c",D0="#6b7280")
    fig,axes = plt.subplots(2,4,figsize=(16,7),layout="constrained")
    for col,weight in enumerate(J.WEIGHTS):
        for panel in (0,1):
            ax = axes[panel,col]
            for model in ("D0",*J.MODELS):
                arm = model if model=="D0" else E.arm_name(model,weight)
                group = [r for r in conditions if r["arm"]==arm and (r["pressure_bar"]<=2.)==(panel==0)]
                xx = [r["pressure_bar"] for r in group]
                yy = [r["signed_median_error_s"] if r["predicted_median_s"] is not None else
                      r["signed_median_error_lower_bound_s"] for r in group]
                ax.plot(xx,yy,"o",color=colors[model],label=model,markersize=3,
                        linestyle="--" if model=="D0" else "-")
                for r,y in zip(group,yy):
                    if r["predicted_median_s"] is None:
                        ax.scatter(r["pressure_bar"],y,marker="$↑$",s=120,color=colors[model])
            ax.axhline(0,color="black",linewidth=.7)
            ax.grid(alpha=.2)
            ax.set(xlabel="Nominal pressure (bar)",xticks=W.NOMINAL[:2] if panel==0 else W.NOMINAL[2:])
            ax.tick_params(labelsize=8)
        axes[0,col].set_title(f"λ={weight:g}"+(" (primary)" if weight==1. else ""))
    axes[0,0].legend(ncol=2,fontsize=8)
    for ax in axes[:,0]:
        ax.set_ylabel("Predicted − observed detector median (s)")
    fig.suptitle("Held-out beverage-mass detector · all 56 brews · arrows denote median bounds")
    for suffix in ("svg","png"):
        fig.savefig(R.OUT/("ONSET."+suffix),dpi=160,metadata={"Date":None} if suffix=="svg" else None)
    plt.close(fig)
    fig,axes = plt.subplots(2,2,figsize=(11,8),layout="constrained")
    observed = [np.mean([s["observed_endpoint_g_s"] for s in sources if s["nominal_pressure_bar"]==p]) for p in W.NOMINAL]
    for ax,weight in zip(axes.flat,J.WEIGHTS):
        ax.plot(W.NOMINAL,observed,"ko",label="Observed beverage flow",markersize=4)
        for model in ("D0",*J.MODELS):
            arm = model if model=="D0" else E.arm_name(model,weight)
            ax.plot(W.NOMINAL,reports[arm]["endpoint_condition_means"],"o-",color=colors[model],label=model,markersize=3)
        ax.set(title=f"λ={weight:g}"+(" (primary)" if weight==1. else ""),xlabel="Nominal pressure (bar)",ylabel="Liquid endpoint flow (g/s)")
        ax.grid(alpha=.2)
    axes[0,0].legend(fontsize=8)
    fig.suptitle("Held-out 100-s endpoints · scale liquid flow · common FORM_A observer")
    for suffix in ("svg","png"):
        fig.savefig(R.OUT/("FLOW."+suffix),dpi=160,metadata={"Date":None} if suffix=="svg" else None)
    plt.close(fig)
    # Every pressure and weight is visible in the SUMMARY's compact numeric panel.
    fig,axes = plt.subplots(3,1,figsize=(13,6.4),layout="constrained")
    for ax,model in zip(axes,J.MODELS):
        matrix = [[next(r for r in losses if r["model"]==model and r["weight"]==w and
                       r["pressure_bar"]==p and r["step_s"]==.005) for p in W.NOMINAL] for w in J.WEIGHTS]
        color = np.log1p([[r["joint_component"] for r in row] for row in matrix])
        ax.imshow(color,aspect="auto",cmap="YlOrBr",vmin=0,vmax=max(float(np.max(color)),1.))
        for i,row in enumerate(matrix):
            for j,r in enumerate(row):
                bound = "≥" if r["detected"]<r["brews"] else "="
                ax.text(j,i,f"F={r['flow_component']:.3g}\nO{bound}{r['onset_component']:.3g}",
                        ha="center",va="center",fontsize=7.5,color="black")
        ax.set(xticks=range(11),xticklabels=[f"{p:g}" for p in W.NOMINAL],
               yticks=range(4),yticklabels=[f"λ={w:g}" for w in J.WEIGHTS],ylabel=model)
        ax.tick_params(labelsize=8)
    axes[-1].set_xlabel("Nominal pressure (bar)")
    fig.suptitle("Held-out normalized loss components by pressure · 0.005 s\nF=flow MSE/0.437²; O=onset loss/4.534²; condition contribution is F+λO",fontsize=10)
    for suffix in ("svg","png"):
        fig.savefig(R.OUT/("PRESSURE_LOSS."+suffix),dpi=180,metadata={"Date":None} if suffix=="svg" else None)
    plt.close(fig)
    fig,ax = plt.subplots(figsize=(8,5),layout="constrained")
    for model in J.MODELS:
        rr = [reports[E.arm_name(model,w)] for w in J.WEIGHTS]
        ax.plot([r["primary_trace_rmse"] for r in rr],[r["onset_rmse"] for r in rr],"o-",color=colors[model],label=model)
        for w,r in zip(J.WEIGHTS,rr):
            ax.annotate(f"λ={w:g}",(r["primary_trace_rmse"],r["onset_rmse"]),xytext=(4,4),textcoords="offset points",fontsize=7)
    for name in ("D0","W0","W1","W2","W2T"):
        r=reports[name]
        ax.scatter(r["primary_trace_rmse"],r["onset_rmse"],color="#6b7280",marker="x")
        ax.annotate(name,(r["primary_trace_rmse"],r["onset_rmse"]),xytext=(4,4),textcoords="offset points",fontsize=8)
    ax.set(xlabel="Primary-trace liquid-flow RMSE (g/s)",ylabel="Onset RMSE or computed lower bound (s)",
           title="Predeclared weights · shared retrospective cohort · lower left is better")
    ax.grid(alpha=.2)
    ax.legend()
    for suffix in ("svg","png"):
        fig.savefig(R.OUT/("TRADEOFF."+suffix),dpi=170,metadata={"Date":None} if suffix=="svg" else None)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("ewp","native","raw","screen","work"):
        parser.add_argument("--"+flag,type=Path,required=True)
    args = parser.parse_args()
    run(args)


def run(args):
    start,cpu = time.perf_counter(),time.process_time()
    data,rows,arms,reference_hashes = load_predictions(args)
    sources = data["sources"]
    report,paired,selected,b1,samples = scores(sources,rows,arms)
    brews,conditions = onset_tables(sources,selected,report)
    losses,flows,bed,numerics = loss_and_flow_tables(sources,selected,report)
    for row in rows:
        if row["model"] not in J.MODELS or row["scope"] != "descriptive":
            continue
        fine,coarse = row["fine"],row["search"]
        of,oc = fine["observer"],coarse["observer"]
        numerics.append(dict(arm=row["arm"],scope="descriptive",brew=None,pressure_bar=row["pressure_bar"],
            detector_fine_s=of["onset_s"],detector_search_s=oc["onset_s"],
            fine_detected=of["detected"],search_detected=oc["detected"],detection_changed=of["detected"]!=oc["detected"],
            detector_fine_minus_search_s=of["onset_s"]-oc["onset_s"] if of["detected"] and oc["detected"] else None,
            endpoint_fine_minus_search_g_s=fine["endpoint_g_s"]-coarse["endpoint_g_s"]))
    sweep,ext = extrema(rows,conditions,arms)
    fits,starts,training,fit_manifest = fit_tables(args)
    numerical_scores = [dict(arm=a,model=r["model"],weight=r["weight"],metric=m,
        score_0_005=r[m+"_rmse"],score_0_02=r[m+"_search_rmse"],
        fine_minus_search=r[m+"_fine_minus_search"],fine_detected=r["fine_detected"],search_detected=r["search_detected"],
        onset_is_bound=r["onset_is_lower_bound"] if m=="onset" else False)
        for a,r in report.items() for m in ("onset","endpoint","primary_trace","companion_trace")]
    comparison = [{k:r[k] for k in ("arm","model","weight","endpoint_rmse","primary_trace_rmse",
        "companion_trace_rmse","onset_rmse","onset_is_lower_bound","fine_detected","one_bar_detected",
        "two_bar_detected","supplementary_condition_median_rms_s","supplementary_is_bound",
        "onset_grade","accuracy_grade_vs_b1","endpoint_comparison_vs_b1")} for r in report.values()]
    comparison.append(dict(arm="B1",model="B1",weight=None,endpoint_rmse=b1["endpoint"],
        primary_trace_rmse=b1["primary_trace"],companion_trace_rmse=b1["companion_trace"],
        onset_grade="NOT_SCORED/no_beverage_predictor"))
    for filename,values in (("GRADES.csv",list(report.values())),("PAIRED_COMPARISONS.csv",paired),
        ("ONSET_BY_BREW.csv",brews),("ONSET_BY_PRESSURE.csv",conditions),("LOSS_BY_PRESSURE.csv",losses),
        ("TRAINING_LOSS_COMPONENTS.csv",training),("FLOW_BY_BREW.csv",flows),("J2_BED_SCALE.csv",bed),
        ("NUMERICAL_CHECKS.csv",numerics),("DESCRIPTIVE_SWEEP.csv",sweep),("EXTREMA.csv",ext),
        ("FITS.csv",fits),("OPTIMIZER_STARTS.csv",starts),("NUMERICAL_SCORES.csv",numerical_scores),
        ("COMPARISON_TABLE.csv",comparison)):
        R.R.csv_write(R.OUT/filename,values)
    replay = json.loads((args.work/"D0_REPLAY.json").read_text())
    R.R.write_json(R.OUT/"D0_REPLAY.json",replay)
    R.R.write_json(args.work/"PAIRED_RESAMPLES.json",samples)
    R.R.write_json(R.OUT/"VIZ_SPEC.json",dict(role="Retrospective coupled-model capability comparisons",
        producer="puckworks.analysis.joint_clock_001_report.figures",
        outputs=[f"{name}.{suffix}" for name in ("ONSET","FLOW","PRESSURE_LOSS","TRADEOFF") for suffix in ("svg","png")],
        dataset_id="waszkiewicz2025/traces_per_brew",source="Waszkiewicz 2025, Zenodo 18046315; authenticated FORM_A histories and D0 support",
        rights="CC-BY-4.0 source; original redraw; raw/native traces external",
        scope="56 held-out brews; all eleven conditions and four predeclared weights; final 0.005-s evaluations",
        encodings=dict(onset="signed condition-median errors; arrows are median lower bounds; 1–2 bar separate from 3.5–13",
            flow="condition-mean liquid scale endpoint against observed scale-derived beverage flow",
            pressure_loss="numeric F and O by pressure/weight/model; color is log(1+F+lambda*O), normalized separately per model; no probability interpretation",
            tradeoff="primary-trace RMSE against onset RMSE/computed bound; lines connect predeclared weights, not additional fits",
            intervals="none drawn; paired intervals in CSV condition on fitted parameters/fixed Mc"),
        ceiling="No physical validation or identified mechanism; fitted scale lag remains observational; retrospective same-cohort capability only"))
    figures(sources,report,conditions,losses)
    evaluation = json.loads((args.work/"EVALUATION_INDEX.json").read_text())
    joint_rows = [r for r in rows if r["model"] in J.MODELS]
    prefix = json.loads((args.work/"PREFIX_VERIFICATION.json").read_text())
    native_verification = R.ROOT/"docs/research/WETTING_SCREEN_001/VERIFICATION.csv"
    source_audit = json.loads((args.work/"SOURCE_AUDIT.json").read_text())
    R.R.write_json(R.OUT/"VERIFICATION.json",dict(D0_replay=replay,prefix_verification=prefix,
        source_audit=source_audit,inherited_native_verification_sha256=R.R.digest(native_verification),
        inherited_native_verification=str(native_verification.relative_to(R.ROOT)),
        note="Existing 102 native checks inherited by identical column hash; qualifications remain in per-brew rows"))
    failures = []
    for path in sorted((args.work/"failures").glob("*.json")):
        failure = json.loads(path.read_text())
        failures.append(dict(file=path.name,sha256=R.R.digest(path),
            **{k:failure[k] for k in ("key","status","error","identity","cpu_seconds","wall_seconds")}))
    boundary_diagnostic = None
    debug_path = args.work/"NUMERICAL_FAILURE_DEBUG.json"
    if debug_path.exists():
        debug = json.loads(debug_path.read_text())
        boundary_diagnostic = dict(file=debug_path.name,sha256=R.R.digest(debug_path),
            **{k:debug[k] for k in ("start","coordinates","parameters","error","cpu_seconds","wall_seconds")},
            role="Exact replay of failing optimizer extrapolation; not another fitted family",
            note="Earlier diagnostic replay failed while serializing NaN; log retained, CPU unmeasured")
    evaluation_recovery = None
    recovery_path = args.work/"EVALUATION_SERIALIZATION_RECOVERY.json"
    if recovery_path.exists():
        evaluation_recovery = json.loads(recovery_path.read_text())
        for record in evaluation_recovery["records"]:
            if R.R.digest(args.work/"interrupted_evaluations"/record["file"]) != record["sha256"]:
                raise ValueError("Retained interrupted evaluation arrays changed")
    manifest = dict(fits=fit_manifest,predictions=evaluation,retained_reference_metadata=reference_hashes,
        fit_freeze_sha256=R.R.digest(args.work/"FIT_FREEZE.json"),source_sha256=R.identity(),
        reporting_sha256=R.R.digest(Path(__file__)),fit_count=144,case_pairs=948,D0_refits=0,
        source_inputs_sha256=R.R.digest(args.native/"source_inputs.json"),
        D0_saved_fits_sha256=R.R.digest(R.ROOT/"docs/research/PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv"),
        native_manifest_sha256=R.R.digest(args.ewp/"docs/demonstrations/FORM_A/RUN_MANIFEST.json"),
        historical_replay_helpers={Path(p).name:R.R.digest(Path(p)) for p in
            (R.D0.__file__,R.D0.E.__file__,R.D0.C.__file__)},
        resamples_sha256=R.R.digest(args.work/"PAIRED_RESAMPLES.json"),
        fit_core_hours=sum(r["core_hours"] for r in fit_manifest),
        evaluation_core_hours=sum(r["cpu_seconds"] for r in joint_rows)/3600,
        replay_core_hours=replay["cpu_seconds"]/3600,reporting_core_hours=(time.process_time()-cpu)/3600,
        prefix_verification_core_hours=sum(r["cpu_seconds"] for r in prefix["records"])/3600,
        failed_attempts=failures,failed_attempt_core_hours=sum(r["cpu_seconds"] for r in failures)/3600,
        numerical_boundary_diagnostic=boundary_diagnostic,
        evaluation_serialization_recovery=evaluation_recovery,
        reporting_wall_seconds=time.perf_counter()-start,
        retained_predecessor_execution="13.22 screen core-hours are historical, not counted again",
        other_work="Structural tests, development and setup are not scientific fit execution; prefix verification separately recorded",
        versions=P.package_versions(),native_evidence="Read-only EWP 67bead2; retained qualification flags propagated",
        external_outputs="Native traces, trial histories and frozen arrays remain outside Git",
        interval_scope=CONDITIONAL)
    manifest["recorded_total_core_hours"] = sum(manifest[k] for k in (
        "fit_core_hours","evaluation_core_hours","replay_core_hours","reporting_core_hours",
        "prefix_verification_core_hours","failed_attempt_core_hours")) + (
            boundary_diagnostic["cpu_seconds"]/3600 if boundary_diagnostic else 0.)
    R.R.write_json(R.OUT/"RUN_MANIFEST.json",manifest)
    R.R.write_json(args.work/"REPORT.json",dict(reports=report,paired=paired,b1=b1,conditions=conditions,
        loss_by_pressure=losses,extrema=ext,bed_scale=bed,manifest=manifest))
    return dict(reports=report,paired=paired,b1=b1,conditions=conditions,losses=losses,
                sweep=sweep,extrema=ext,bed=bed,numerics=numerics,manifest=manifest)


if __name__ == "__main__":
    main()

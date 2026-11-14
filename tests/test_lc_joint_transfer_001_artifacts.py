"""Independent arithmetic and cross-artifact checks; no campaign rerun."""
import csv
from functools import lru_cache
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"docs/research/LC_JOINT_TRANSFER_001"
PRESSURES=(1.,2.,3.5,4.,5.,6.,7.,8.,9.,11.,13.)


@lru_cache(None)
def read(name):
    with (OUT/name).open() as stream:
        return list(csv.DictReader(stream))


def test_complete_frozen_scope_and_whole_condition_isolation():
    fits=read("FITS.csv"); starts=read("OPTIMIZER_STARTS.csv")
    assert len(fits)==48 and len(starts)==912
    assert {float(r["weight"]) for r in fits}=={.05,.5,1.,2.}
    flow=read("FLOW_BY_BREW.csv")
    cohort={r["brew"]:float(r["pressure_bar"]) for r in flow}
    assert len(cohort)==56 and sorted(cohort.values()).count(1.)==5
    assert len(flow)==448 and len(read("ONSET_BY_BREW.csv"))==448
    assert len(read("NUMERICAL_BY_CASE.csv"))==632
    assert len(read("DESCRIPTIVE_SWEEP.csv"))==184
    provenance={r["fold"]:r for r in read("MC_PROVENANCE.csv")}
    for row in read("FOLD_ISOLATION.csv"):
        h=float(row["held_condition_bar"]) if row["held_condition_bar"] else None
        training=json.loads(row["training_brews"])
        held=json.loads(row["held_brews"])
        assert set(training)=={b for b,p in cohort.items() if h is None or p!=h}
        assert set(held)=={b for b,p in cohort.items() if h is not None and p==h}
        assert not set(training)&set(held)
        assert "OMIT" not in row["fold"]
        assert row["fold"]==row["source_fold_key"]
        assert float(row["Mc_g"])==float(provenance[row["fold"]]["Mc_g"])
        schedule=json.loads(row["start_schedule"])
        assert len(schedule)==19
        assert schedule[0][0]=="matching_A_J1_f0" and schedule[0][1][4]==0.
        assert schedule[2][1][-1]==0.
        seed=json.loads(row["historical_LC_seed_parameters"])
        assert schedule[1][1][4]==schedule[2][1][4]==seed["f"]
        own=sorted([s for s in starts if s["key"]==row["key"]],key=lambda s:int(s["number"]))
        assert len(own)==19
        assert [[s["start"],json.loads(s["initial_coordinates"])] for s in own]==schedule
        fit=next(f for f in fits if f["key"]==row["key"])
        selected=float(fit["selected_LC_J1_objective"])
        assert selected==min(float(s["best_objective"]) for s in own)
        assert selected<=float(own[0]["initial_objective"])
        if float(fit["f"])==0.:
            assert selected==float(fit["frozen_f0_objective"])


def test_common_mask_scores_and_censor_counts_reconcile_independently():
    flow=read("FLOW_BY_BREW.csv"); onset=read("ONSET_BY_BREW.csv")
    for score in read("SCORES.csv"):
        arm=score["arm"]
        ff=[r for r in flow if r["arm"]==arm]
        oo=[r for r in onset if r["arm"]==arm]
        assert len(ff)==len(oo)==56
        assert len({r["brew"] for r in ff})==len({r["brew"] for r in oo})==56
        assert sum(r["detected"]=="True" for r in oo)==int(score["fine_detected"])
        for r in oo:
            if r["detected"]=="True":
                expected=(float(r["predicted_onset_s"])-float(r["observed_onset_s"]))**2
            else:
                assert r["predicted_onset_s"]=="" and r["signed_error_s"]==""
                expected=max(0.,float(r["censor_bound_s"])-float(r["observed_onset_s"]))**2
            np.testing.assert_allclose(float(r["squared_loss_s2"]),expected,rtol=1e-12,atol=0)
        for metric,rows,field in (("endpoint",ff,"endpoint_residual_g_s"),
                ("primary_trace",ff,"primary_mse_g2_s2"),("companion_trace",ff,"companion_mse_g2_s2"),
                ("onset",oo,"squared_loss_s2")):
            values=[]
            for p in PRESSURES:
                losses=[float(r[field])**2 if metric=="endpoint" else float(r[field])
                        for r in rows if float(r["pressure_bar"])==p]
                values.append(np.sqrt(sum(losses)/len(losses)))
            np.testing.assert_allclose(float(score[metric+"_rmse"]),sum(values)/11,rtol=1e-12,atol=0)
    for row in read("PAIRED_COMPARISONS.csv"):
        np.testing.assert_allclose(float(row["difference"]),float(row["left_score"])-float(row["right_score"]),rtol=1e-12,atol=0)
        assert int(row["left_available"])==int(row["right_available"])==56
        if row["metric"]=="onset" and min(int(row["left_detected"]),int(row["right_detected"]))<56:
            assert "not a bound" in row["interpretation"]


def test_cor15_units_fixed_shapes_and_equal_series_paired_arithmetic():
    shapes=json.loads((OUT/"FROZEN_EXTERNAL_SHAPES.json").read_text())["shapes"]
    models=read("CORROCHANO_SERIES.csv"); residuals=read("CORROCHANO_RESIDUALS.csv")
    assert len(models)==144 and len(residuals)==1296
    with (ROOT/"docs/research/COR15_SHAPE_001/DIGITIZED.csv").open() as stream:
        original={r["point_id"]:r for r in csv.DictReader(stream)}
    assert len(original)==108
    computed={}
    for row in models:
        w=float(row["weight"]); s=row["series"]; m=row["model"]
        rr=[r for r in residuals if float(r["weight"])==w and r["series"]==s and r["model"]==m]
        assert len(rr)==int(row["n"])
        assert {r["point_id"] for r in rr}=={k for k,v in original.items() if v["series"]==s}
        for r in rr:
            assert float(r["P_Pa"])==float(original[r["point_id"]]["P_Pa"])
            assert float(r["Q_m3_s"])==float(original[r["point_id"]]["Q_m3_s"])
        p=np.array([float(r["P_Pa"]) for r in rr]); q=np.array([float(r["Q_m3_s"]) for r in rr])
        if m=="L0":
            h=p
            assert row["amplitude_units"]=="m3/(s Pa)"
        else:
            f=next(x for x in shapes if x["weight"]==w and x["model"]==m)
            bar=p/100000.
            with np.errstate(over="ignore"):
                h=f["Pd_bar"]*((1-f["f"])*(-np.expm1(-(bar/f["Pd_bar"])**f["n"]))+
                    f["f"]*(-np.expm1(-bar/f["Pd_bar"])))*np.exp(-bar/f["Pstar_bar"])
            assert row["amplitude_units"]=="m3/(s bar)"
        amplitude=np.linalg.lstsq(h[:,None],q,rcond=None)[0][0]
        np.testing.assert_allclose(float(row["amplitude"]),amplitude,rtol=1e-12,atol=0)
        np.testing.assert_allclose([float(r["predicted_Q_m3_s"]) for r in rr],amplitude*h,rtol=1e-12,atol=0)
        delta=np.array([float(r["signed_residual_m3_s"]) for r in rr])
        mse=float(np.mean(delta**2)); s2=float(np.mean(q**2))
        np.testing.assert_allclose(float(row["mse_m6_s2"]),mse,rtol=1e-12,atol=0)
        np.testing.assert_allclose(float(row["S2_central_m6_s2"]),s2,rtol=1e-12,atol=0)
        computed[(w,s,m)]=(mse,s2)
        np.testing.assert_allclose(float(row["lowest_pressure_bar"]),p.min()/100000.,rtol=1e-12,atol=0)
    for row in read("CORROCHANO_PAIRED.csv"):
        w=float(row["weight"]); a,b=row["left"],row["right"]
        series={s for ww,s,m in computed if ww==w} if row["series"]=="POOLED" else {row["series"]}
        value=np.mean([(computed[(w,s,a)][0]-computed[(w,s,b)][0])/computed[(w,s,a)][1] for s in series])
        np.testing.assert_allclose(float(row["D"]),value,rtol=1e-12,atol=0)
        assert int(row["realizations"])==4096
        assert "not population" in row["interval_scope"]

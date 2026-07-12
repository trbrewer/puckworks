"""identifiability.py — the POSITIVE control for the transfer degeneracy (not CI).

Companion to `docs/ANALYSIS_transfer.md`. The angeloni transfer study showed that
a single-grind endpoint fit cannot identify the Sherwood rate scale from the
inventory (the flat valley, ANALYSIS_transfer §3). This module shows the OTHER
half of the claim on the SAME model and the SAME dataset pannusch was fit to
(Schmieder fraction kinetics): information about the kinetic rate lives in the
TEMPORAL SHAPE of the extraction, so scoring against the fraction curve localizes
the rate, while scoring an aggregated endpoint does not.

**Honest scope (review B2/M3).** This is an IN-SAMPLE VERIFICATION on pannusch's
own calibration data, NOT an independent identification of the physical rate. And
the aggregated-endpoint score here is a **sampled-fraction aggregate** — a
duration-weighted mean of the SIX measured windows (fractions 1,2,3,5,7,10), NOT a
true whole cup: the gaps between fractions 3-5, 5-7, 7-10 are omitted.
`sampled_aggregate_vs_actual_cup()` shows the aggregate differs from the actual
brew-ratio-1/3 cup by ~28-38% MAPE, so the aggregate's flatness is partly a
sampling artifact. A defensible full-cup comparison (score full-shot predictions
against the actual BR-1/3 cup, or reconstruct the complete shot) is OWED.

Method (per solute): sweep rate_scale (multiply the Sherwood prefactors A1,A2); at
each rate re-optimize a single global level (the EXACT MAPE weighted-median, review
B3) so the ONLY thing the rate can change is the extraction SHAPE. Score two ways
on the 15 Schmieder experiments:
  - FRACTION: MAPE over all 6 measured time-fractions per shot (temporal shape).
  - SAMPLED-AGGREGATE: MAPE over the duration-weighted mean of those 6 windows.
Report the range ratio = max/min over the swept rates (a DESCRIPTIVE sharpness
proxy, not a decision rule -- it is range-dependent, review B4).

Run:  python -m puckworks.validation.slow.identifiability
"""
import numpy as np

_COL = {"caffeine": "c_caffeine_mg_g", "trigonelline": "c_trigonelline_mg_g",
        "5CQA": "c_5CQA_mg_g"}
_CUP_COMPONENT = {"caffeine": "caffeine", "trigonelline": "trigonelline",
                  "5CQA": "5-CQA"}


def _fit_level_mape(pred, meas):
    """EXACT min MAPE over a single global level L (review B3). The minimiser of
    mean_i (pred_i/meas_i)|L - meas_i/pred_i| is the WEIGHTED MEDIAN of
    x_i = meas_i/pred_i with weights w_i = pred_i/meas_i -- not a grid argmin."""
    pred = np.asarray(pred, float); meas = np.asarray(meas, float)
    x = meas / pred; w = pred / meas
    o = np.argsort(x); x, w = x[o], w[o]
    cw = np.cumsum(w)
    L = float(x[min(int(np.searchsorted(cw, 0.5 * cw[-1])), len(x) - 1)])
    return float(np.mean(np.abs(L * pred - meas) / meas) * 100)


def _sweep_solute(solute, rates):
    from puckworks.models.pannusch2024 import solver as ps
    exps = ps._exp_kinetics(); sp0 = ps._solute_params()[solute]; col = _COL[solute]
    frac_mape, agg_mape = [], []
    for rate in rates:
        sp = dict(sp0); sp["A1"] = sp0["A1"] * rate; sp["A2"] = sp0["A2"] * rate
        fpred, fmeas, apred, ameas = [], [], [], []
        for rows in exps.values():
            rows = sorted(rows, key=lambda r: r["fraction"])
            T = rows[0]["Temp_C"]; flow = rows[0]["flow_mL_s"]
            bounds = sorted({r["t_lower_s"] for r in rows} | {r["t_upper_s"] for r in rows})
            cf = ps.simulate_fractions(T, flow, bounds, sp, 1.0)   # per-unit-level
            idx = {b: i for i, b in enumerate(bounds)}
            pf, mf, dt = [], [], []
            for r in rows:
                i0 = idx[r["t_lower_s"]]; i1 = idx[r["t_upper_s"]]
                pf.append(float(np.mean(cf[i0:i1])) if i1 > i0 else float(cf[i0]))
                mf.append(r[col]); dt.append(r["t_upper_s"] - r["t_lower_s"])
            fpred += pf; fmeas += mf
            dt = np.asarray(dt, float)
            # SAMPLED-FRACTION AGGREGATE (duration-weighted mean of the 6 windows;
            # NOT a whole cup -- the inter-fraction gaps are omitted, review B2)
            apred.append(float(np.sum(np.asarray(pf) * dt) / dt.sum()))
            ameas.append(float(np.sum(np.asarray(mf) * dt) / dt.sum()))
        frac_mape.append(round(_fit_level_mape(fpred, fmeas), 2))
        agg_mape.append(round(_fit_level_mape(apred, ameas), 2))
    return frac_mape, agg_mape


def sampled_aggregate_vs_actual_cup(solutes=("caffeine", "trigonelline", "5CQA")):
    """AUDIT (review B2): the six-window duration-weighted aggregate is NOT the cup.
    Per solute, compare the aggregate of the MEASURED fraction values against the
    actual brew-ratio-1/3 `conc_in_cup` (replicate mean) for the same experiment
    ids. Data-only; no model. Returns per-solute aggregate/cup means, mean ratio,
    and MAPE across the 15 experiments -- large -> the §6 'endpoint' is a sampled
    aggregate, not a full cup, so its flatness is partly a sampling artifact."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks import data as d
    exps = ps._exp_kinetics()
    cup = {}
    for r in d.schmieder_cup_masses():
        if r.get("brew_ratio") != "1/3":
            continue
        cup.setdefault((r.get("component"), r.get("exp")), []).append(r.get("conc_in_cup"))
    out = {}
    for sol in solutes:
        col = _COL[sol]; comp = _CUP_COMPONENT[sol]
        aggs, cups = [], []
        for e, rows in exps.items():
            rows = sorted(rows, key=lambda r: r["fraction"])
            dt = np.array([r["t_upper_s"] - r["t_lower_s"] for r in rows], float)
            agg = float(np.sum(np.array([r[col] for r in rows]) * dt) / dt.sum())
            key = (comp, float(e))
            vals = [v for v in cup.get(key, []) if isinstance(v, (int, float))]
            if not vals:
                continue
            aggs.append(agg); cups.append(float(np.mean(vals)))
        aggs, cups = np.array(aggs), np.array(cups)
        out[sol] = dict(n=len(aggs),
                        mean_sampled_aggregate=round(float(aggs.mean()), 3),
                        mean_actual_cup=round(float(cups.mean()), 3),
                        mean_ratio=round(float((aggs / cups).mean()), 3),
                        mape_vs_actual_cup=round(float(np.mean(np.abs(aggs - cups) / cups) * 100), 1))
    return dict(per_solute=out,
                verdict="the six-window duration-weighted aggregate differs from the "
                        "actual BR-1/3 cup by ~28-38% MAPE (ratio ~1.3) -> it is NOT a "
                        "whole cup; the §6 endpoint score is a SAMPLED-FRACTION "
                        "AGGREGATE. A full-cup comparison (full-shot prediction vs the "
                        "actual cup, or complete-shot reconstruction) is owed.",
                strength="data-only audit")


def identifiability_fractions_vs_cup(solutes=("caffeine", "trigonelline", "5CQA"),
                                     rates=(0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0)):
    """Positive control (IN-SAMPLE VERIFICATION): fraction scoring localizes the
    kinetic rate more sharply than the aggregated endpoint on pannusch's own
    calibration data. Returns per solute the rate grid, fraction/sampled-aggregate
    MAPE sweeps, the min-MAPE rate for each scoring, and the descriptive range
    ratio (max/min over the swept rates -- NOT a decision rule; range-dependent,
    review B4). NOTE: ~3 min of PDE solves (slow; hand-run)."""
    rates = list(rates)
    out = {}
    for sol in solutes:
        fm, am = _sweep_solute(sol, rates)
        fi = int(np.argmin(fm)); ai = int(np.argmin(am))
        out[sol] = dict(rates=rates, fraction_mape=fm, sampled_agg_mape=am,
                        frac_best_rate=rates[fi], sampled_agg_best_rate=rates[ai],
                        frac_range_ratio=round(max(fm) / min(fm), 2),
                        sampled_agg_range_ratio=round(max(am) / min(am), 2))
    return dict(per_solute=out,
                verdict="On pannusch's calibration data, fraction scoring LOCALIZES "
                        "the rate profile more sharply (range ratio ~3-4x, min near "
                        "rate 1 where pannusch was fit) than the SAMPLED-FRACTION "
                        "AGGREGATE endpoint (~1.2-1.4x). This is IN-SAMPLE verification "
                        "of information content, NOT an independent identification of "
                        "the physical rate; the aggregate is not a true cup "
                        "(see sampled_aggregate_vs_actual_cup).",
                strength="verification (in-sample, on pannusch's own fit data); NOT "
                         "independent identification")


def report():
    r = identifiability_fractions_vs_cup()
    print("== identifiability: fraction curve vs sampled-fraction aggregate (Schmieder) ==")
    for sol, x in r["per_solute"].items():
        print(f"\n{sol}  (rate sweep {x['rates'][0]}..{x['rates'][-1]}x)")
        print("  FRACTION MAPE       :", x["fraction_mape"],
              f"-> min at rate {x['frac_best_rate']}x, range ratio {x['frac_range_ratio']}x")
        print("  SAMPLED-AGG MAPE    :", x["sampled_agg_mape"],
              f"-> min at rate {x['sampled_agg_best_rate']}x, range ratio {x['sampled_agg_range_ratio']}x")
    print("\n" + r["verdict"])
    print("\n== audit: sampled aggregate vs ACTUAL BR-1/3 cup (data-only) ==")
    a = sampled_aggregate_vs_actual_cup()
    for sol, x in a["per_solute"].items():
        print(f"  {sol:>13}: aggregate {x['mean_sampled_aggregate']} vs cup "
              f"{x['mean_actual_cup']} (ratio {x['mean_ratio']}); MAPE {x['mape_vs_actual_cup']}%")
    print(" ", a["verdict"])
    return dict(identifiability=r, audit=a)


if __name__ == "__main__":
    report()

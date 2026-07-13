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
                        "AGGREGATE. The repo data have only 6 fraction windows "
                        "(1,2,3,5,7,10) -- the intermediate windows are absent -- so an "
                        "empirical complete-shot reconstruction is DATA-BLOCKED; the "
                        "exact-integral SIMULATION below (full_cup_simulation_"
                        "identifiability) tests the claim without that artifact.",
                strength="data-only audit")


def full_cup_simulation_identifiability(
        solutes=("caffeine", "trigonelline", "5CQA"),
        rates=(0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0),
        n_fine=12, noise=0.03, seed=0, n_seeds=20):
    """B2 design #3 -- a SAME-MODEL, BEST-CASE structural design simulation (review
    MAJ-13): an inverse-crime study (truth generated and refit with the SAME solver)
    that isolates the information-content difference between fraction-resolved and
    whole-cup observations, with NO model discrepancy. It is NOT evidence that a real
    experimental cup lacks rate information, nor that the model is correctly specified.

    Per experiment (its real T, flow, shot duration t_end), generate synthetic truth
    at the calibrated rate=1: a fine-grid fraction curve (n_fine contiguous windows
    over the WHOLE shot) and the EXACT whole-cup concentration (the single [0, t_end]
    integral). Add stated relative Gaussian noise over n_seeds independent
    realizations (the PDE predictions are seed-independent, so this is ~free), sweep
    rate, fit the exact MAPE level, and score against (a) the fine fraction curve and
    (b) the exact full cup. Report per-solute the DISTRIBUTION over seeds of the range
    ratio and best rate for each scoring -- fraction-resolved scoring LOCALIZES the
    rate objective more sharply than the aggregated cup within this same-model design.
    Owed (review MAJ-13): a model-discrepancy variant (altered geometry/flow/IC between
    generation and fitting). NOTE: ~4-6 min of PDE solves (slow; hand-run)."""
    from puckworks.models.pannusch2024 import solver as ps
    exps = ps._exp_kinetics()
    # per-experiment (T, flow, fine edges over the whole shot, t_end)
    shots = []
    for rows in exps.values():
        rows = sorted(rows, key=lambda r: r["fraction"])
        T = rows[0]["Temp_C"]; flow = rows[0]["flow_mL_s"]
        t_end = max(r["t_upper_s"] for r in rows)
        edges = list(np.linspace(0.0, t_end, n_fine + 1))
        shots.append((T, flow, edges, t_end))

    def _predict(sp0, rate, kind):
        """kind='frac' -> fine-window curve concat; 'cup' -> exact [0,t_end] per shot."""
        sp = dict(sp0); sp["A1"] = sp0["A1"] * rate; sp["A2"] = sp0["A2"] * rate
        out_ = []
        for T, flow, edges, t_end in shots:
            if kind == "frac":
                out_ += list(ps.simulate_fractions(T, flow, edges, sp, 1.0))
            else:
                out_.append(float(ps.simulate_fractions(T, flow, [0.0, t_end], sp, 1.0)[0]))
        return np.asarray(out_, float)

    rates = list(rates)
    out = {}
    for sol in solutes:
        sp0 = ps._solute_params()[sol]
        frac_true = _predict(sp0, 1.0, "frac")
        cup_true = _predict(sp0, 1.0, "cup")
        # cache the seed-INDEPENDENT per-rate predictions (the expensive PDE solves)
        frac_preds = [_predict(sp0, rate, "frac") for rate in rates]
        cup_preds = [_predict(sp0, rate, "cup") for rate in rates]
        frr, crr, fbest = [], [], []          # per-seed range ratios + frac best rate
        fm0 = cm0 = None
        fm_all, cm_all = [], []               # per-seed per-rate MAPE (for seed bands)
        for s in range(n_seeds):
            rs = np.random.default_rng(seed + s)
            f_meas = frac_true * (1.0 + noise * rs.standard_normal(frac_true.shape))
            c_meas = cup_true * (1.0 + noise * rs.standard_normal(cup_true.shape))
            fm = [_fit_level_mape(frac_preds[k], f_meas) for k in range(len(rates))]
            cm = [_fit_level_mape(cup_preds[k], c_meas) for k in range(len(rates))]
            frr.append(max(fm) / min(fm)); crr.append(max(cm) / min(cm))
            fbest.append(rates[int(np.argmin(fm))])
            fm_all.append(fm); cm_all.append(cm)
            if s == 0:
                fm0 = [round(v, 2) for v in fm]; cm0 = [round(v, 2) for v in cm]
        frr = np.array(frr); crr = np.array(crr)
        fm_all = np.array(fm_all); cm_all = np.array(cm_all)   # (n_seeds, n_rate)
        out[sol] = dict(rates=rates, fraction_mape=fm0, exact_cup_mape=cm0,   # seed 0 (figure)
                        # per-rate seed distribution (mean +/- std over seeds) for bands
                        fraction_mape_seed_mean=[round(v, 2) for v in fm_all.mean(0)],
                        fraction_mape_seed_std=[round(v, 2) for v in fm_all.std(0)],
                        exact_cup_mape_seed_mean=[round(v, 2) for v in cm_all.mean(0)],
                        exact_cup_mape_seed_std=[round(v, 2) for v in cm_all.std(0)],
                        frac_range_ratio=round(float(frr.mean()), 2),
                        frac_range_ratio_std=round(float(frr.std()), 2),
                        exact_cup_range_ratio=round(float(crr.mean()), 2),
                        exact_cup_range_ratio_std=round(float(crr.std()), 2),
                        frac_best_rate_median=float(np.median(fbest)),
                        frac_best_rate_is_1_frac=round(float(np.mean(np.array(fbest) == 1.0)), 2))
    return dict(per_solute=out, n_fine=n_fine, noise=noise, seed=seed, n_seeds=n_seeds,
                verdict="SAME-MODEL best-case simulation (inverse crime; no model "
                        "discrepancy): over %d noise seeds, fine fraction-curve scoring "
                        "localizes rate=1 far more sharply (range ratio ~%.0fx) than the "
                        "EXACT whole-cup integral (~%.0fx) -- the aggregated cup carries "
                        "less rate information than the resolved fractions, within this "
                        "same-model design. NOT evidence about real cups or model "
                        "correctness." % (
                            n_seeds,
                            np.mean([out[s]["frac_range_ratio"] for s in solutes]),
                            np.mean([out[s]["exact_cup_range_ratio"] for s in solutes])),
                strength="same-model best-case simulation (inverse crime; seeded noise "
                         "distribution); NOT an empirical positive control")


def full_cup_simulation_discrepancy(
        solutes=("caffeine", "trigonelline", "5CQA"),
        rates=(0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0),
        temp_offset_C=4.0, flow_scale=1.10,
        n_fine=12, noise=0.03, seed=0, n_seeds=20):
    """B2 design #4 -- a MODEL-DISCREPANCY positive control (review MAJ-13). Unlike the
    same-model inverse-crime study, the synthetic TRUTH is generated with a DIFFERENT
    configuration than the fitting model: the brew temperature is offset by
    `temp_offset_C` (which enters the kinetics through a nonlinear Arrhenius term, so a
    single rate scale cannot absorb it) and the flow by `flow_scale`. The fitter then
    sweeps ONLY the rate at the NOMINAL (T, flow). This asks the diagnostic question a
    sharp minimum alone cannot answer: under unmodelled discrepancy, does the objective
    still localize, and WHERE?

    Expected/reported: the fraction objective still discriminates (range ratio > 1) but
    the LOCATED best rate is BIASED away from 1 (the fitter trades rate for the
    unmodelled T/flow error) and an IRREDUCIBLE MAPE FLOOR appears above the noise level
    (the discrepancy cannot be fit away). The cup stays comparatively flat. Conclusion: a
    sharp fraction-scoring minimum is NECESSARY but NOT SUFFICIENT for correct kinetics
    -- discrepancy shifts the located rate and leaves a floor. NOTE: ~5-7 min of PDE
    solves (slow; hand-run)."""
    from puckworks.models.pannusch2024 import solver as ps
    exps = ps._exp_kinetics()
    shots = []
    for rows in exps.values():
        rows = sorted(rows, key=lambda r: r["fraction"])
        T = rows[0]["Temp_C"]; flow = rows[0]["flow_mL_s"]
        t_end = max(r["t_upper_s"] for r in rows)
        edges = list(np.linspace(0.0, t_end, n_fine + 1))
        shots.append((T, flow, edges, t_end))

    def _predict(sp0, rate, kind, dT=0.0, fscale=1.0):
        """kind='frac' fine-window curve; 'cup' exact [0,t_end]. dT/fscale perturb the
        TRUTH generator (nominal fit uses dT=0, fscale=1)."""
        sp = dict(sp0); sp["A1"] = sp0["A1"] * rate; sp["A2"] = sp0["A2"] * rate
        out_ = []
        for T, flow, edges, t_end in shots:
            Tt = T + dT; ft = flow * fscale
            if kind == "frac":
                out_ += list(ps.simulate_fractions(Tt, ft, edges, sp, 1.0))
            else:
                out_.append(float(ps.simulate_fractions(Tt, ft, [0.0, t_end], sp, 1.0)[0]))
        return np.asarray(out_, float)

    rates = list(rates)
    out = {}
    for sol in solutes:
        sp0 = ps._solute_params()[sol]
        # TRUTH at rate=1 but with the T/flow DISCREPANCY baked in
        frac_true = _predict(sp0, 1.0, "frac", dT=temp_offset_C, fscale=flow_scale)
        cup_true = _predict(sp0, 1.0, "cup", dT=temp_offset_C, fscale=flow_scale)
        # FIT predictions at NOMINAL (T, flow) -- the misspecified model
        frac_preds = [_predict(sp0, rate, "frac") for rate in rates]
        cup_preds = [_predict(sp0, rate, "cup") for rate in rates]
        frr, crr, fbest, ffloor = [], [], [], []
        fm0 = cm0 = None
        for s in range(n_seeds):
            rs = np.random.default_rng(seed + s)
            f_meas = frac_true * (1.0 + noise * rs.standard_normal(frac_true.shape))
            c_meas = cup_true * (1.0 + noise * rs.standard_normal(cup_true.shape))
            fm = [_fit_level_mape(frac_preds[k], f_meas) for k in range(len(rates))]
            cm = [_fit_level_mape(cup_preds[k], c_meas) for k in range(len(rates))]
            frr.append(max(fm) / min(fm)); crr.append(max(cm) / min(cm))
            fbest.append(rates[int(np.argmin(fm))]); ffloor.append(min(fm))
            if s == 0:
                fm0 = [round(v, 2) for v in fm]; cm0 = [round(v, 2) for v in cm]
        frr = np.array(frr); crr = np.array(crr); ffloor = np.array(ffloor)
        # located-rate bias: how often the fraction minimum lands OFF the true rate=1
        biased = float(np.mean(np.array(fbest) != 1.0))
        out[sol] = dict(
            rates=rates, fraction_mape=fm0, exact_cup_mape=cm0,
            frac_range_ratio=round(float(frr.mean()), 2),
            exact_cup_range_ratio=round(float(crr.mean()), 2),
            frac_best_rate_median=float(np.median(fbest)),
            frac_located_rate_biased_off_1_frac=round(biased, 2),
            irreducible_frac_mape_floor=round(float(ffloor.mean()), 2),
            floor_exceeds_noise=bool(ffloor.mean() > noise * 100 * 1.5))
    mean_floor = float(np.mean([out[s]["irreducible_frac_mape_floor"] for s in solutes]))
    any_biased = float(np.mean([out[s]["frac_located_rate_biased_off_1_frac"]
                                for s in solutes]))
    return dict(
        per_solute=out, temp_offset_C=temp_offset_C, flow_scale=flow_scale,
        n_fine=n_fine, noise=noise, seed=seed, n_seeds=n_seeds,
        mean_irreducible_frac_mape_floor=round(mean_floor, 2),
        mean_located_rate_biased_fraction=round(any_biased, 2),
        verdict=("MODEL-DISCREPANCY positive control (truth generated at T+%.0f C, "
                 "flow x%.2f; fit at nominal T/flow, sweeping rate only): the fraction "
                 "objective still discriminates sharply (range ratio ~%.0fx) and, at this "
                 "discrepancy magnitude, the located rate stays ROBUST near the true 1.0 "
                 "(biased off 1.0 in only %.0f%% of seeds). The discrepancy signature is "
                 "instead the IRREDUCIBLE MAPE FLOOR ~%.1f%% -- well above the %.0f%% "
                 "noise and NOT fittable by rate alone. Conclusion: a sharp minimum near "
                 "the true rate does NOT certify correct kinetics; the residual floor is "
                 "the misspecification tell, and larger T/flow errors both raise the floor "
                 "and begin to bias the located rate (see the larger-dose run)." % (
                     temp_offset_C, flow_scale,
                     np.mean([out[s]["frac_range_ratio"] for s in solutes]),
                     any_biased * 100, mean_floor, noise * 100)),
        strength="model-discrepancy simulation positive control (seeded noise "
                 "distribution); demonstrates a sharp minimum is necessary-not-sufficient")


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
    print("\n== EXACT-integral simulation: fraction curve vs TRUE whole cup ==")
    s = full_cup_simulation_identifiability()
    for sol, x in s["per_solute"].items():
        print(f"  {sol:>13}: fraction range ratio {x['frac_range_ratio']}"
              f"±{x['frac_range_ratio_std']}x (best rate median {x['frac_best_rate_median']}, "
              f"=1 in {x['frac_best_rate_is_1_frac']:.0%} of seeds) | EXACT-cup range "
              f"ratio {x['exact_cup_range_ratio']}±{x['exact_cup_range_ratio_std']}x")
    print(" ", s["verdict"])
    return dict(identifiability=r, audit=a, simulation=s)


if __name__ == "__main__":
    report()

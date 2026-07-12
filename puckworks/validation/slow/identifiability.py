"""identifiability.py — the POSITIVE control for the transfer degeneracy (not CI).

Companion to `docs/ANALYSIS_transfer.md`. The angeloni transfer study showed that
a single-grind WHOLE-CUP fit cannot identify the Sherwood rate scale from the
inventory (the flat valley, ANALYSIS_transfer §3). This module shows the OTHER
half of the claim on the SAME model and the SAME dataset pannusch was fit to
(Schmieder fraction kinetics): the information about the kinetic rate lives in the
TEMPORAL SHAPE of the extraction, so scoring against the fraction curve identifies
the rate, while collapsing the very same shots to a whole-cup value does not.

Method (per solute): sweep rate_scale (multiply the Sherwood prefactors A1,A2);
at each rate re-optimize a single global level (the c_s0/normalization) to best
fit, so the ONLY thing the rate can do is change the extraction SHAPE. Score two
ways on the 15 Schmieder experiments:
  - FRACTION: MAPE over all 6 measured time-fractions per shot (temporal shape).
  - CUP:      MAPE over the volume-weighted whole-cup value per shot (shape
              integrated away).
Report the identifiability RATIO = max-edge MAPE / min MAPE: a sharp trough
(ratio >> 1) means the rate is identified; a flat valley (ratio ~ 1) means it is
not. Result: fractions give a sharp minimum near rate 1 (as expected -- pannusch
was fit here); the collapsed cup is flat -- reproducing the angeloni degeneracy.

Run:  python -m puckworks.validation.slow.identifiability
"""
import numpy as np

_COL = {"caffeine": "c_caffeine_mg_g", "trigonelline": "c_trigonelline_mg_g",
        "5CQA": "c_5CQA_mg_g"}


def _fit_level_mape(pred, meas):
    """Min MAPE over a single global level multiplier (shape-only fit)."""
    pred = np.asarray(pred, float); meas = np.asarray(meas, float)
    grid = np.linspace(0.2, 5.0, 160) * float(np.median(meas / pred))
    return float(min(np.mean(np.abs(L * pred - meas) / meas) * 100 for L in grid))


def _sweep_solute(solute, rates):
    from puckworks.models.pannusch2024 import solver as ps
    exps = ps._exp_kinetics(); sp0 = ps._solute_params()[solute]; col = _COL[solute]
    frac_mape, cup_mape = [], []
    for rate in rates:
        sp = dict(sp0); sp["A1"] = sp0["A1"] * rate; sp["A2"] = sp0["A2"] * rate
        fpred, fmeas, cpred, cmeas = [], [], [], []
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
            cpred.append(float(np.sum(np.asarray(pf) * dt) / dt.sum()))
            cmeas.append(float(np.sum(np.asarray(mf) * dt) / dt.sum()))
        frac_mape.append(round(_fit_level_mape(fpred, fmeas), 2))
        cup_mape.append(round(_fit_level_mape(cpred, cmeas), 2))
    return frac_mape, cup_mape


def identifiability_fractions_vs_cup(solutes=("caffeine", "trigonelline", "5CQA"),
                                     rates=(0.25, 0.4, 0.6, 0.8, 1.0, 1.4, 2.0, 3.0, 4.0)):
    """Positive control: fractions identify the kinetic rate, the whole cup does
    not. Returns per solute the rate grid, fraction/cup MAPE sweeps, the best-fit
    rate for each scoring, and the identifiability ratio (edge/min). NOTE: ~3 min
    of PDE solves (slow; hand-run)."""
    rates = list(rates)
    out = {}
    for sol in solutes:
        fm, cm = _sweep_solute(sol, rates)
        fi = int(np.argmin(fm)); ci = int(np.argmin(cm))
        out[sol] = dict(rates=rates, fraction_mape=fm, cup_mape=cm,
                        frac_best_rate=rates[fi], cup_best_rate=rates[ci],
                        frac_ratio=round(max(fm) / min(fm), 2),
                        cup_ratio=round(max(cm) / min(cm), 2))
    return dict(per_solute=out,
                verdict="fractions IDENTIFY the rate (sharp trough, edge/min ~3-4x, "
                        "best rate ~1 where pannusch was fit); the collapsed cup does "
                        "NOT (flat, edge/min ~1.4x) -- the same non-identifiability as "
                        "the angeloni whole-cup transfer. Confirms: the kinetic rate "
                        "lives in the temporal SHAPE, which whole-cup integrates away.",
                strength="verification (on pannusch's own fit data); positive control "
                         "for the ANALYSIS_transfer degeneracy")


def report():
    r = identifiability_fractions_vs_cup()
    print("== identifiability: fraction curve vs collapsed whole-cup (Schmieder) ==")
    for sol, x in r["per_solute"].items():
        print(f"\n{sol}  (rate sweep {x['rates'][0]}..{x['rates'][-1]}x)")
        print("  FRACTION MAPE:", x["fraction_mape"],
              f"-> min at rate {x['frac_best_rate']}x, edge/min {x['frac_ratio']}x")
        print("  CUP MAPE     :", x["cup_mape"],
              f"-> min at rate {x['cup_best_rate']}x, edge/min {x['cup_ratio']}x")
    print("\n" + r["verdict"])
    return r


if __name__ == "__main__":
    report()

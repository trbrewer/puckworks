#!/usr/bin/env python3
"""Information parity and mechanistic attribution (pivot plan §7).

Two questions, kept apart because they have different evidential standing.

**1. Does the mechanistic model retain an advantage once the empirical arm receives the same
exogenous hydraulic information?** The mechanistic solver's target-grind channel is its matched
endpoint, `t_end = 40 g / flow(p, T, grind)`, so the scalar the empirical arm was missing is the
derived residence time. Adding it is what the plan calls information parity.

This is reported **two ways, which disagree, and the disagreement is the result**:

* `frozen_selection` — the honest held-out score. Candidate families (including the hydraulic ones)
  are selected by leave-one-optimal-condition-out CV **on the calibration conditions only**,
  refitted on all nine, frozen, and only then scored. Nothing about the coarse/fine records can
  reach the predictor.
* `oracle_upper_bound` — what the family could achieve if the *right* hydraulic form were known.
  Each single-covariate form is fitted on calibration data, then the best is picked **by its
  held-out score**. That is selection on the test set. It is NOT a held-out result, cannot be
  quoted as the empirical arm's performance, and is reported only to bound what the family
  contains.

The gap between the two measures something real: whether nine calibration conditions can identify
which hydraulic form to trust when the target grinds are extrapolative.

**2. Where does the apparent cross-grind skill come from?** The M0/M1/M2 ablation:

* **M0** — inherited source rate, fit the level only. Tests whether target-specific rate
  recalibration contributes held-out value at all.
* **M1** — fit rate and level, but apply the **optimal-grind** hydraulic map to coarse and fine.
  Removes the target-grind information channel while keeping everything else.
* **M2** — fit rate and level, target-grind hydraulic map. The canonical published arm.

No parameter is fitted to any coarse or fine concentration in any arm.

Cost: roughly 2,000 PDE solves, ~5 min. Hand-run, never in CI.

CLI::

    python tools/paper_a_information_parity.py --write
    python tools/paper_a_information_parity.py --check
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_INFORMATION_PARITY.json"

VARIETIES = ("Arabica", "Robusta")
SOLUTES = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))
HELD_OUT = ("C", "F")

#: Single-covariate hydraulic forms for the oracle bound. Each is [1, h(tau)] — two parameters, no
#: mechanism, no temperature or pressure. Deliberately the simplest possible responses, so that a
#: win here cannot be attributed to empirical flexibility.
HYDRAULIC_FORMS = {
    "log_residence": lambda tau: np.log(tau),
    "residence": lambda tau: tau,
    "flow": lambda tau: 1.0 / tau,
    "log_flow": lambda tau: np.log(1.0 / tau),
    "sqrt_residence": lambda tau: np.sqrt(tau),
}


def _rows():
    from puckworks import data as D
    return D.angeloni_bioactives()


def _split(rows, variety, grind, on_grid_only=False):
    out = [r for r in rows if r["variety"] == variety and r["granulometry"] == grind]
    return [r for r in out if r["on_grid"] == "True"] if on_grid_only else out


def _tau(rows, grind=None):
    """Residence time at each row's own granulometry, or at a FORCED granulometry if given."""
    from puckworks.validation.slow import angeloni_bracket as AB
    return np.array([40.0 / AB._flow_gran(float(r["p_bar"]), float(r["T_degC"]),
                                          grind or r["granulometry"]) for r in rows], float)


def extrapolation_report(rows) -> dict:
    """How far outside the calibration hydraulic range the target grinds sit.

    The plan (§7.3) requires this be reported, and it turns out to explain the headline: a linear
    empirical response cannot be expected to hold 1.6 calibration-spans beyond its support.
    """
    out = {}
    for variety in VARIETIES:
        cal = _tau(_split(rows, variety, "O", on_grid_only=True))
        span = float(cal.max() - cal.min())
        per_grind = {}
        for grind in HELD_OUT:
            tg = _tau(_split(rows, variety, grind))
            outside = float(((tg < cal.min()) | (tg > cal.max())).mean())
            gap = float(max(cal.min() - tg.min(), tg.max() - cal.max()))
            per_grind[grind] = {
                "residence_s_min": round(float(tg.min()), 3),
                "residence_s_max": round(float(tg.max()), 3),
                "fraction_outside_calibration_range": round(outside, 3),
                "largest_gap_in_calibration_spans": round(gap / span, 3),
            }
        out[variety] = {"calibration_residence_s": [round(float(cal.min()), 3),
                                                    round(float(cal.max()), 3)],
                        "held_out": per_grind}
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1. Information parity
# ─────────────────────────────────────────────────────────────────────────────────────────────


def frozen_selection() -> dict:
    """Honest held-out score with hydraulic families in the candidate set."""
    from puckworks.paper_a import empirical_benchmarks as EB
    p = EB.panel(families=EB.HYDRAULIC_FAMILIES)
    return {
        "candidate_families": list(EB.HYDRAULIC_FAMILIES),
        "selection": ("leave-one-optimal-condition-out CV on the nine calibration conditions only, "
                      "refit on all nine, frozen before any coarse/fine record is scored"),
        "macro_cf_mape": p["empirical"]["macro_cf_mape"],
        "macro_coarse_mape": p["empirical"]["macro_coarse_mape"],
        "macro_fine_mape": p["empirical"]["macro_fine_mape"],
        "groups": [{"group": g["group"], "family": g["family"],
                    "coarse_mape": g["coarse_mape"], "fine_mape": g["fine_mape"]}
                   for g in p["groups"]],
    }


def oracle_upper_bound() -> dict:
    """What the hydraulic family CONTAINS — selected using held-out scores, so not a result."""
    from puckworks.paper_a import empirical_benchmarks as EB
    rows = EB._rows()
    per_form = {}
    for name, h in HYDRAULIC_FORMS.items():
        coarse, fine, allcf = [], [], []
        for variety in VARIETIES:
            for _solute, column in SOLUTES:
                train = [r for r in rows if r.variety == variety and r.is_optimal_grind and r.on_grid]
                _T, _p, yt = EB._cells(train, column)
                tt = EB.residence_times(train)
                beta = EB.fit_mape(np.column_stack([np.ones_like(tt), h(tt)]), yt)

                def score(subset):
                    _Tg, _pg, yg = EB._cells(subset, column)
                    tg = EB.residence_times(subset)
                    return EB.mape(np.column_stack([np.ones_like(tg), h(tg)]) @ beta, yg)

                coarse.append(score([r for r in rows if r.variety == variety
                                     and r.granulometry == "C"]))
                fine.append(score([r for r in rows if r.variety == variety
                                   and r.granulometry == "F"]))
                allcf.append(score([r for r in rows if r.variety == variety
                                    and r.granulometry in HELD_OUT]))
        per_form[name] = {"macro_cf_mape": round(float(np.mean(allcf)), 3),
                          "macro_coarse_mape": round(float(np.mean(coarse)), 3),
                          "macro_fine_mape": round(float(np.mean(fine)), 3)}

    best = min(per_form, key=lambda k: per_form[k]["macro_cf_mape"])
    return {
        "status": ("NOT A HELD-OUT SCORE. The form is chosen by its coarse/fine performance, which "
                   "is selection on the test set. Reported only to bound what a two-parameter, "
                   "mechanism-free hydraulic response can reach."),
        "forms": per_form,
        "best_form": best,
        "best_macro_cf_mape": per_form[best]["macro_cf_mape"],
    }


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2. Mechanistic ablation M0 / M1 / M2
# ─────────────────────────────────────────────────────────────────────────────────────────────


def _frac(AB, ps, species, rate, conds, gran):
    s = dict(species)
    s["A1"] = species["A1"] * rate
    s["A2"] = species["A2"] * rate
    s["c_s0"] = 1.0
    return np.array([float(ps.simulate_fractions(
        T, AB._flow_gran(p, T, gran), AB._matched_bounds(AB._flow_gran(p, T, gran)),
        s, cl1=1.0)[0]) for T, p in conds])


def ablation_panel() -> dict:
    """M0/M1/M2 on the same calibration support and the same held-out corpus."""
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps

    rows = _rows()
    params = ps._solute_params()
    per_group = []

    for variety in VARIETIES:
        train = _split(rows, variety, "O", on_grid_only=True)
        condsO = [(float(r["T_degC"]), float(r["p_bar"])) for r in train]

        for solute, column in SOLUTES:
            mO = np.array([float(r[column]) for r in train])

            # M2 / M1 share the calibration fit: rate and level on the optimal grind.
            best = None
            for rs in AB._RATE_DOMAIN:
                f = _frac(AB, ps, params[solute], float(rs), condsO, "O")
                level, score = AB._mape_level(f, mO)
                if best is None or score < best[2]:
                    best = (float(rs), level, score)
            rate_fit, level_fit, _ = best

            # M0: inherited source rate (multiplier 1.0), level only.
            f0 = _frac(AB, ps, params[solute], 1.0, condsO, "O")
            level_m0 = float(AB._mape_level(f0, mO)[0])

            entry = {"group": "%s:%s" % (variety, solute),
                     "fitted_rate": rate_fit, "m0_rate": 1.0}
            for grind in HELD_OUT:
                rows_g = _split(rows, variety, grind)
                conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in rows_g]
                m = np.array([float(r[column]) for r in rows_g])

                def mape_of(level, rate, hydraulic_grind):
                    f = _frac(AB, ps, params[solute], rate, conds, hydraulic_grind)
                    return float(np.mean(np.abs(level * f - m) / m) * 100.0)

                entry["M0_%s" % grind] = mape_of(level_m0, 1.0, grind)
                entry["M1_%s" % grind] = mape_of(level_fit, rate_fit, "O")   # common map
                entry["M2_%s" % grind] = mape_of(level_fit, rate_fit, grind)  # target map
            per_group.append(entry)

    def macro(arm):
        c = float(np.mean([g["%s_C" % arm] for g in per_group]))
        f = float(np.mean([g["%s_F" % arm] for g in per_group]))
        return {"coarse": round(c, 3), "fine": round(f, 3), "pooled": round((c + f) / 2.0, 3)}

    arms = {a: macro(a) for a in ("M0", "M1", "M2")}
    return {
        "arms": arms,
        "contrasts_pp": {
            "M0_to_M2": round(arms["M0"]["pooled"] - arms["M2"]["pooled"], 3),
            "M1_to_M2": round(arms["M1"]["pooled"] - arms["M2"]["pooled"], 3),
            "M0_to_M1": round(arms["M0"]["pooled"] - arms["M1"]["pooled"], 3),
        },
        "interpretation": {
            "M0_to_M2": "combined value of rate recalibration and target-grind hydraulics",
            "M1_to_M2": "value supplied by the TARGET-GRIND hydraulic map alone",
            "M0_to_M1": "value of fitting the rate under a common hydraulic assumption",
        },
        "per_group": [{k: (round(v, 3) if isinstance(v, float) else v) for k, v in g.items()}
                      for g in per_group],
    }


def run() -> dict:
    rows = _rows()
    frozen = frozen_selection()
    oracle = oracle_upper_bound()
    ablation = ablation_panel()
    model_pooled = ablation["arms"]["M2"]["pooled"]

    return {
        "schema_version": 1,
        "question": ("Does the mechanistic model retain incremental held-out skill once the "
                     "empirical arm receives the same exogenous hydraulic information, and where "
                     "does the cross-grind skill come from? (pivot plan §7)"),
        "status": ("EXPLORATORY. Single campaign, nine calibration conditions, no per-condition "
                   "replicate uncertainty. No equivalence or significance claim is made, and no "
                   "practical margin is manufactured."),
        "mechanistic_reference_pooled_mape": model_pooled,
        "hydraulic_extrapolation": extrapolation_report(rows),
        "information_parity": {
            "frozen_selection": frozen,
            "frozen_minus_model_pp": round(frozen["macro_cf_mape"] - model_pooled, 3),
            "oracle_upper_bound": oracle,
            "oracle_minus_model_pp": round(oracle["best_macro_cf_mape"] - model_pooled, 3),
        },
        "ablation": ablation,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.check:
        if not OUT.exists():
            print("no information-parity archive; run --write", file=sys.stderr)
            return 1
        print("Paper A information-parity archive present.")
        return 0

    print("information parity + M0/M1/M2 ablation (~5 min)...", flush=True)
    result = run()
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("\nwrote %s" % OUT.relative_to(_REPO))

    ip = result["information_parity"]
    print("\nmechanistic (M2) pooled MAPE      : %.3f %%"
          % result["mechanistic_reference_pooled_mape"])
    print("hydraulically-equal, FROZEN       : %.3f %%  (%+.3f pp vs model)"
          % (ip["frozen_selection"]["macro_cf_mape"], ip["frozen_minus_model_pp"]))
    print("  selected families: %s"
          % ", ".join(sorted({g["family"] for g in ip["frozen_selection"]["groups"]})))
    print("hydraulic ORACLE bound (not a score): %.3f %% via %r  (%+.3f pp vs model)"
          % (ip["oracle_upper_bound"]["best_macro_cf_mape"],
             ip["oracle_upper_bound"]["best_form"], ip["oracle_minus_model_pp"]))
    print("\nablation (pooled MAPE):")
    for arm, v in result["ablation"]["arms"].items():
        print("   %-3s coarse %7.3f  fine %7.3f  pooled %7.3f"
              % (arm, v["coarse"], v["fine"], v["pooled"]))
    for k, v in result["ablation"]["contrasts_pp"].items():
        print("   %-10s %+7.3f pp   (%s)" % (k, v, result["ablation"]["interpretation"][k]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Is the M0-vs-M2 estimation-policy contrast stable to the calibration conditions used?

Pivot check 2. The M0/M1/M2 ablation is computed from ONE calibration fit on all nine optimal-grind
conditions. The refit-aware analysis of the earlier headline showed that a fixed-predictor
comparison at this scale can be unstable: the model-minus-constant difference had a median of
-0.058 pp but changed sign in 3 of 9 leave-one-condition-out folds.

M0 - M2 is -0.157 pp under the published rate domain and -0.183 pp once the domain is widened. That
is the same order of magnitude, so the same question has to be asked of it before it can carry a
conclusion.

For each of the nine optimal-grind conditions in turn:

* drop it from the calibration support;
* refit **M2** (rate over the declared grid, level by the exact MAPE-optimal weighted median) on the
  remaining eight;
* refit **M0** (rate FROZEN at the inherited value, level only) on the same eight;
* build **M1** from M2's fitted parameters but with the optimal-grind hydraulic map applied to the
  target grinds;
* score all three on the unchanged complete 132-observation coarse/fine corpus.

The published rate domain is used, not the widened one, so these folds are directly comparable with
the existing refit-aware archive. Check 1 established that the transfer conclusion is the same under
either domain (-0.157 vs -0.183 pp), so the choice is about comparability, not about the answer.

**What this is and is not.** Nine dependent folds. This is an exploratory, descriptive refit-aware
distribution, NOT a calibrated confidence interval, and it must not be relabelled as one.

Cost: roughly 3,000 PDE solves, ~20 min. Hand-run, never in CI.

CLI::

    python tools/paper_a_ablation_refit_stability.py --write
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

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_ABLATION_REFIT_STABILITY.json"

VARIETIES = ("Arabica", "Robusta")
SOLUTES = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))
HELD_OUT = ("C", "F")

#: M0 freezes the rate multiplier at the inherited source value.
INHERITED_RATE = 1.0


def _rows():
    from puckworks import data as D
    return D.angeloni_bioactives()


def _split(rows, variety, grind, on_grid_only=False):
    out = [r for r in rows if r["variety"] == variety and r["granulometry"] == grind]
    return [r for r in out if r["on_grid"] == "True"] if on_grid_only else out


def _conditions(rows):
    seen = []
    for r in _split(rows, "Arabica", "O", on_grid_only=True):
        key = (float(r["T_degC"]), float(r["p_bar"]))
        if key not in seen:
            seen.append(key)
    return seen


def _frac(AB, ps, species, rate, conds, gran):
    s = dict(species)
    s["A1"] = species["A1"] * rate
    s["A2"] = species["A2"] * rate
    s["c_s0"] = 1.0
    return np.array([float(ps.simulate_fractions(
        T, AB._flow_gran(p, T, gran), AB._matched_bounds(AB._flow_gran(p, T, gran)),
        s, cl1=1.0)[0]) for T, p in conds])


def _fit_fold(rows, drop):
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps

    params = ps._solute_params()
    per_group = []

    for variety in VARIETIES:
        train = [r for r in _split(rows, variety, "O", on_grid_only=True)
                 if (float(r["T_degC"]), float(r["p_bar"])) != drop]
        condsO = [(float(r["T_degC"]), float(r["p_bar"])) for r in train]
        held = {g: _split(rows, variety, g) for g in HELD_OUT}

        for solute, column in SOLUTES:
            mO = np.array([float(r[column]) for r in train])

            # ── M2: refit rate and level on the retained conditions ─────────────────────────
            best = None
            for rs in AB._RATE_DOMAIN:
                f = _frac(AB, ps, params[solute], float(rs), condsO, "O")
                level, score = AB._mape_level(f, mO)
                if best is None or score < best[2]:
                    best = (float(rs), level, score)
            rate_fit, level_fit, _ = best

            # ── M0: rate FROZEN, refit the level only on the same retained conditions ───────
            f0 = _frac(AB, ps, params[solute], INHERITED_RATE, condsO, "O")
            level_m0 = float(AB._mape_level(f0, mO)[0])

            entry = {"group": "%s:%s" % (variety, solute), "fitted_rate": rate_fit}
            for grind in HELD_OUT:
                conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in held[grind]]
                m = np.array([float(r[column]) for r in held[grind]])

                def score(level, rate, hydraulic_grind):
                    f = _frac(AB, ps, params[solute], rate, conds, hydraulic_grind)
                    return float(np.mean(np.abs(level * f - m) / m) * 100.0)

                entry["M0_%s" % grind] = score(level_m0, INHERITED_RATE, grind)
                entry["M1_%s" % grind] = score(level_fit, rate_fit, "O")
                entry["M2_%s" % grind] = score(level_fit, rate_fit, grind)
            per_group.append(entry)
    return per_group


def _macro(per_group, key):
    return float(np.mean([g[key] for g in per_group]))


def run() -> dict:
    rows = _rows()
    conditions = _conditions(rows)
    folds = []

    for drop in conditions:
        per_group = _fit_fold(rows, drop)
        fold = {"dropped_condition": {"T_degC": drop[0], "p_bar": drop[1]}}
        for arm in ("M0", "M1", "M2"):
            c = _macro(per_group, "%s_C" % arm)
            f = _macro(per_group, "%s_F" % arm)
            fold["%s_pooled" % arm] = round((c + f) / 2.0, 3)
            fold["%s_coarse" % arm] = round(c, 3)
            fold["%s_fine" % arm] = round(f, 3)
        fold["M0_minus_M2"] = round(fold["M0_pooled"] - fold["M2_pooled"], 3)
        fold["M1_minus_M2"] = round(fold["M1_pooled"] - fold["M2_pooled"], 3)
        fold["n_groups_M0_better"] = sum(
            1 for g in per_group
            if (g["M0_C"] + g["M0_F"]) / 2 < (g["M2_C"] + g["M2_F"]) / 2)
        folds.append(fold)
        print("  dropped (%.1f C, %.0f bar): M0 %.3f  M1 %.3f  M2 %.3f   M0-M2 %+.3f  M1-M2 %+.3f"
              % (drop[0], drop[1], fold["M0_pooled"], fold["M1_pooled"], fold["M2_pooled"],
                 fold["M0_minus_M2"], fold["M1_minus_M2"]), flush=True)

    def spread(key, favours_when_negative=True):
        v = [f[key] for f in folds]
        return {"min": round(min(v), 3), "max": round(max(v), 3),
                "median": round(float(np.median(v)), 3),
                "n_negative": sum(1 for x in v if x < 0),
                "n_positive": sum(1 for x in v if x > 0),
                "sign_stable": bool(all(x < 0 for x in v) or all(x > 0 for x in v))}

    m0 = spread("M0_minus_M2")
    m1 = spread("M1_minus_M2")

    # Disaggregation by target grind. The pooled figure is a mean of the two, and for BOTH
    # contrasts the two halves point in opposite directions -- so a pooled number reported alone
    # would repeat exactly the defect this whole revision was opened to fix.
    def by_grind(arm):
        out = {}
        for grind in ("coarse", "fine"):
            v = [f["%s_%s" % (arm, grind)] - f["M2_%s" % grind] for f in folds]
            out[grind] = {"median": round(float(np.median(v)), 3),
                          "min": round(min(v), 3), "max": round(max(v), 3),
                          "n_negative": sum(1 for x in v if x < 0),
                          "n_positive": sum(1 for x in v if x > 0),
                          "sign_stable": bool(all(x < 0 for x in v) or all(x > 0 for x in v))}
        return out

    disaggregated = {"M0_minus_M2": by_grind("M0"), "M1_minus_M2": by_grind("M1")}

    return {
        "schema_version": 1,
        "question": ("Is the M0-vs-M2 estimation-policy contrast stable to which optimal-grind "
                     "conditions were used for calibration? M0 freezes the mass-transfer-rate "
                     "multiplier at its inherited value and M2 fits it; BOTH re-profile the "
                     "inventory level and BOTH receive the target-grind flow map."),
        "estimand": ("macro pooled MAPE, arm minus M2, in percentage points; NEGATIVE means the arm "
                     "beats the canonical fitted-rate model"),
        "design": {
            "folds": "leave one of the nine optimal-grind conditions out, in turn",
            "refitted_each_fold": ["M2 rate and level", "M0 level only (rate frozen)"],
            "M1": "M2's fitted parameters with the optimal-grind hydraulic map applied to targets",
            "scored_on": "the unchanged complete 132-observation coarse/fine corpus",
            "rate_domain": "the PUBLISHED domain, for comparability with the existing archives",
        },
        "status": ("EXPLORATORY and DESCRIPTIVE: nine dependent folds. This is not a calibrated "
                   "confidence interval and must not be relabelled as one."),
        "n_folds": len(folds),
        "folds": folds,
        "M0_minus_M2": m0,
        "M1_minus_M2": m1,
        "disaggregated_by_target_grind": disaggregated,
        "pooling_warning": (
            "Both pooled contrasts average two opposite results and MUST NOT be reported alone. "
            "M1-M2 is large and positive on coarse but slightly NEGATIVE on fine; M0-M2 is "
            "negative on coarse but mostly POSITIVE on fine."),
        "reading": {
            "M0_minus_M2": ("sign stable across all nine folds" if m0["sign_stable"]
                            else "SIGN CHANGES across folds — the claim must weaken accordingly"),
            "M1_minus_M2": ("sign stable across all nine folds" if m1["sign_stable"]
                            else "SIGN CHANGES across folds — the claim must weaken accordingly"),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    print("leave-one-condition-out refit of M0/M1/M2 (~20 min)...", flush=True)
    result = run()
    if args.write:
        OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("\nwrote %s" % OUT.relative_to(_REPO))

    for key in ("M0_minus_M2", "M1_minus_M2"):
        s = result[key]
        print("\n%-14s median %+.3f pp, range [%+.3f, %+.3f], negative in %d/%d folds, "
              "sign stable: %s"
              % (key, s["median"], s["min"], s["max"], s["n_negative"], result["n_folds"],
                 s["sign_stable"]))
        print("   %s" % result["reading"][key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

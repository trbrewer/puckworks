#!/usr/bin/env python3
"""Leave-one-optimal-condition-out refit of BOTH arms of the headline comparison.

Domain-referee Major finding 2. The published clustered percentile ranges are correctly labelled
fixed-predictor sensitivity ranges: they condition on one fitted mechanistic predictor and one
fitted constant, and resample only the held-out observations. They therefore describe the sampling
sensitivity of a **fixed** comparison, not the stability of the **procedure** that produced the two
predictors from nine optimal-grind conditions.

The referee asked for a refit-aware paired analysis and named a tractable companion:

    "A simpler companion analysis would repeatedly omit one optimal-grind condition, refit both
     arms, and examine the resulting coarse/fine score difference. The folds are dependent, so this
     remains descriptive, but it directly reveals whether the headline depends on a particular
     calibration condition."

That is what this computes. For each of the nine optimal-grind conditions in turn:

* drop it from the training support;
* **refit the mechanistic model** (rate over the declared grid, level by the exact MAPE-optimal
  weighted median) on the remaining eight;
* **refit the level-only constant** on the same eight;
* **refit and re-select the equal-information empirical response** on the same eight;
* score all three on the unchanged complete 132-observation coarse/fine corpus.

Every arm is refitted in every fold. A fold that refitted only one arm would measure that arm's
instability rather than the instability of the comparison.

**What this is and is not.** The nine folds are dependent and there are only nine of them, so this
is an exploratory, descriptive refit-aware distribution. It is **not** a calibrated confidence
interval and must not be relabelled as one — the same distinction the paper already draws for its
percentile ranges. What it answers is narrow and useful: does the sign or the rough size of the
headline difference depend on any single calibration condition?

Cost: roughly 7,800 PDE solves, ~17 minutes. Hand-run, never in CI.

CLI::

    python tools/paper_a_refit_aware_comparison.py --write
    python tools/paper_a_refit_aware_comparison.py --check
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

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_REFIT_AWARE_COMPARISON.json"

VARIETIES = ("Arabica", "Robusta")
SOLUTES = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))
HELD_OUT = ("C", "F")


def _rows():
    from puckworks import data as D
    return D.angeloni_bioactives()


def _split(rows, variety, grind, on_grid_only=False):
    out = [r for r in rows if r["variety"] == variety and r["granulometry"] == grind]
    if on_grid_only:
        out = [r for r in out if r["on_grid"] == "True"]
    return out


def _conditions(rows):
    """The nine optimal-grind (T, p) conditions, in a stable order."""
    seen = []
    for r in _split(rows, "Arabica", "O", on_grid_only=True):
        key = (float(r["T_degC"]), float(r["p_bar"]))
        if key not in seen:
            seen.append(key)
    return seen



def _frac(AB, ps, species, rate, conds, gran):
    """Unit-inventory prediction at the matched endpoint, mirroring the production `frac`.

    The rate multiplier scales A1 and A2 — that is what "refitting the rate" means. An earlier
    draft of this tool omitted it, so `f` was identical for every candidate rate, the level absorbed
    everything, and the mechanistic arm silently became a rate-free model scoring 8.281 % instead of
    the published 8.44 %. It was caught by validating the no-fold-dropped case against the published
    headline, which is why that validation is now a test.
    """
    s = dict(species)
    s["A1"] = species["A1"] * rate
    s["A2"] = species["A2"] * rate
    s["c_s0"] = 1.0
    return np.array([float(ps.simulate_fractions(
        T, AB._flow_gran(p, T, gran), AB._matched_bounds(AB._flow_gran(p, T, gran)),
        s, cl1=1.0)[0]) for T, p in conds])


def _fit_fold(rows, drop, empirical):
    """Refit all three arms on the eight retained conditions; score on the complete C/F corpus."""
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.paper_a import empirical_benchmarks as EB
    from puckworks.paper_a import source_schema as SS

    params = ps._solute_params()
    parsed = {r.sample_id: r for r in SS.parse_rows()}
    per_group = []

    for variety in VARIETIES:
        train = [r for r in _split(rows, variety, "O", on_grid_only=True)
                 if (float(r["T_degC"]), float(r["p_bar"])) != drop]
        condsO = [(float(r["T_degC"]), float(r["p_bar"])) for r in train]
        held = [r for g in HELD_OUT for r in _split(rows, variety, g)]

        for solute, column in SOLUTES:
            mO = np.array([float(r[column]) for r in train])

            # ── mechanistic: refit rate and level on the retained conditions ────────────────
            best = None
            for rs in AB._RATE_DOMAIN:
                f = _frac(AB, ps, params[solute], float(rs), condsO, "O")
                level, score = AB._mape_level(f, mO)
                if best is None or score < best[2]:
                    best = (float(rs), level, score)
            rate, level, _ = best

            # ── level-only constant: refit on the same retained conditions ──────────────────
            constant = float(AB._mape_level(np.ones(len(mO)), mO)[0])

            # ── empirical response: refit AND re-select on the same retained conditions ─────
            fold_rows = [parsed[r["sample"]] for r in train]
            emp = _empirical_on(EB, fold_rows, column)

            # ── score every arm on the UNCHANGED complete C/F corpus ────────────────────────
            group = {"group": "%s:%s" % (variety, solute), "rate": rate}
            for grind in HELD_OUT:
                rows_g = [r for r in held if r["granulometry"] == grind]
                conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in rows_g]
                m = np.array([float(r[column]) for r in rows_g])
                f = _frac(AB, ps, params[solute], rate, conds, grind)
                group["model_%s" % grind] = float(np.mean(np.abs(level * f - m) / m) * 100.0)
                group["const_%s" % grind] = float(np.mean(np.abs(constant - m) / m) * 100.0)
                Tg = np.array([c[0] for c in conds]); pg = np.array([c[1] for c in conds])
                pred = EB._design(emp["family"], Tg, pg) @ emp["beta"]
                group["emp_%s" % grind] = float(np.mean(np.abs(pred - m) / m) * 100.0)
            per_group.append(group)
    return per_group


def _empirical_on(EB, fold_rows, column):
    """Select and fit the empirical family on exactly the fold's retained conditions."""
    T = np.array([float(r.temperature_degC) for r in fold_rows])
    p = np.array([float(r.pressure_bar) for r in fold_rows])
    y = np.array([float(r.raw[column]) for r in fold_rows])
    cv = {}
    for family in EB.FAMILIES:
        errs = []
        for i in range(len(y)):
            keep = np.ones(len(y), bool); keep[i] = False
            if keep.sum() <= EB._design(family, T, p).shape[1]:
                errs = None; break
            beta = EB.fit_mape(EB._design(family, T[keep], p[keep]), y[keep])
            pred = EB._design(family, T[~keep], p[~keep]) @ beta
            errs.append(abs(float(pred[0]) - y[i]) / y[i] * 100.0)
        if errs is not None:
            cv[family] = float(np.mean(errs))
    family = min(EB.FAMILIES, key=lambda f: (cv.get(f, np.inf), EB.FAMILIES.index(f)))
    return {"family": family, "beta": EB.fit_mape(EB._design(family, T, p), y)}


def _macro(per_group, key):
    return float(np.mean([g[key] for g in per_group]))


def run() -> dict:
    rows = _rows()
    conditions = _conditions(rows)
    folds = []
    for drop in conditions:
        per_group = _fit_fold(rows, drop, empirical=True)
        fold = {"dropped_condition": {"T_degC": drop[0], "p_bar": drop[1]}}
        for arm in ("model", "const", "emp"):
            c = _macro(per_group, "%s_C" % arm)
            f = _macro(per_group, "%s_F" % arm)
            fold["%s_coarse" % arm] = round(c, 3)
            fold["%s_fine" % arm] = round(f, 3)
            fold["%s_pooled" % arm] = round((c + f) / 2.0, 3)
        fold["model_minus_const"] = round(fold["model_pooled"] - fold["const_pooled"], 3)
        fold["model_minus_emp"] = round(fold["model_pooled"] - fold["emp_pooled"], 3)
        folds.append(fold)
        print("  dropped (%.1f C, %.0f bar): model %.3f  const %.3f  emp %.3f  "
              "Δconst %+.3f  Δemp %+.3f"
              % (drop[0], drop[1], fold["model_pooled"], fold["const_pooled"],
                 fold["emp_pooled"], fold["model_minus_const"], fold["model_minus_emp"]),
              flush=True)

    def spread(key):
        v = [f[key] for f in folds]
        return {"min": round(min(v), 3), "max": round(max(v), 3),
                "median": round(float(np.median(v)), 3),
                "n_favouring_model": sum(1 for x in v if x < 0),
                "n_favouring_comparator": sum(1 for x in v if x > 0)}

    return {
        "schema_version": 1,
        "question": ("Does the headline model-minus-comparator difference depend on any single "
                     "optimal-grind calibration condition? (domain-referee Major finding 2)"),
        "estimand": "macro pooled MAPE, mechanistic model minus comparator, in percentage points",
        "design": {
            "folds": "leave one of the nine optimal-grind conditions out, in turn",
            "refitted_each_fold": ["mechanistic rate and level", "level-only constant",
                                   "equal-information empirical response (family re-selected)"],
            "scored_on": "the unchanged complete 132-observation coarse/fine corpus",
        },
        "status": ("EXPLORATORY and DESCRIPTIVE: nine dependent folds. This is not a calibrated "
                   "confidence interval and must not be relabelled as one."),
        "n_folds": len(folds),
        "folds": folds,
        "model_minus_const": spread("model_minus_const"),
        "model_minus_emp": spread("model_minus_emp"),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    args = ap.parse_args(argv)

    if args.check:
        if not OUT.exists():
            print("no refit-aware archive; run --write", file=sys.stderr)
            return 1
        print("Paper A refit-aware comparison archive present (%d folds)."
              % json.loads(OUT.read_text())["n_folds"])
        return 0

    print("leave-one-optimal-condition-out refit of both arms (~17 min)...", flush=True)
    result = run()
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("\nwrote %s" % OUT.relative_to(_REPO))
    for key in ("model_minus_const", "model_minus_emp"):
        s = result[key]
        print("  %-18s median %+.3f pp, range [%+.3f, %+.3f], favouring model in %d/%d folds"
              % (key, s["median"], s["min"], s["max"], s["n_favouring_model"], result["n_folds"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

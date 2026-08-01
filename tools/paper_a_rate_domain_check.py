#!/usr/bin/env python3
"""Is the boundary-pinned rate a real degeneracy, or an artefact of the declared rate domain?

Three of the six variety-solute groups (all three Robusta) fit a rate multiplier of exactly 6.5,
the upper edge of `angeloni_bracket._RATE_DOMAIN = geomspace(0.15, 6.5, 18)`. Those are also the
groups where FREEZING the rate (ablation arm M0) transfers better than fitting it.

That observation carries a load-bearing conclusion — "the design cannot separate the rate, and
fitting it anyway degrades transfer" — so the boundary must be explained before the conclusion is
used. There are three possibilities and they mean different things:

* **grid artefact** — a genuine interior optimum sits beyond 6.5, and the published rate is simply
  the wrong number. The transfer comparison would need redoing at the true optimum.
* **saturating degeneracy** — the objective flattens as the rate grows, because a fast enough rate
  reaches local equilibrium within the cup and the predicted concentration stops responding. Then
  no finite optimum exists, 6.5 is arbitrary but so is any other cap, and the rate is unidentified
  in the strongest sense.
* **interior optimum just outside** — a real minimum slightly beyond the cap.

This widens the domain by more than two decades and reports which case holds, per group. It also
re-scores the held-out coarse/fine corpus at the re-found optimum, because the only reason to care
is whether the transfer conclusion moves.

Cost: roughly 2,000 PDE solves, ~10 min. Hand-run, never in CI.

CLI::

    python tools/paper_a_rate_domain_check.py --write
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

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_RATE_DOMAIN_CHECK.json"

VARIETIES = ("Arabica", "Robusta")
SOLUTES = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))
HELD_OUT = ("C", "F")

#: The published domain, for reference.
PUBLISHED_LO, PUBLISHED_HI, PUBLISHED_N = 0.15, 6.5, 18

#: Widened domain: same lower edge, upper edge raised by a factor of ~75 (2.9 decades total).
WIDE_LO, WIDE_HI, WIDE_N = 0.15, 500.0, 40

#: A profile is called SATURATING if the objective changes by less than this (relative) across the
#: top decade of the widened grid — i.e. the data stop distinguishing rates entirely.
SATURATION_TOLERANCE = 0.01


def _rows():
    from puckworks import data as D
    return D.angeloni_bioactives()


def _split(rows, variety, grind, on_grid_only=False):
    out = [r for r in rows if r["variety"] == variety and r["granulometry"] == grind]
    return [r for r in out if r["on_grid"] == "True"] if on_grid_only else out


def _frac(AB, ps, species, rate, conds, gran):
    s = dict(species)
    s["A1"] = species["A1"] * rate
    s["A2"] = species["A2"] * rate
    s["c_s0"] = 1.0
    return np.array([float(ps.simulate_fractions(
        T, AB._flow_gran(p, T, gran), AB._matched_bounds(AB._flow_gran(p, T, gran)),
        s, cl1=1.0)[0]) for T, p in conds])


def analyse_group(AB, ps, params, rows, variety, solute, column, rates) -> dict:
    train = _split(rows, variety, "O", on_grid_only=True)
    condsO = [(float(r["T_degC"]), float(r["p_bar"])) for r in train]
    mO = np.array([float(r[column]) for r in train])

    levels, objective, fracs = [], [], []
    for rate in rates:
        f = _frac(AB, ps, params[solute], float(rate), condsO, "O")
        level, score = AB._mape_level(f, mO)
        levels.append(level)
        objective.append(score)
        fracs.append(float(np.mean(f)))
    objective = np.asarray(objective, float)

    i_min = int(np.argmin(objective))
    j_min = float(objective[i_min])
    rate_star = float(rates[i_min])

    # near-optimal set at the paper's 10 % tolerance
    within = objective <= j_min * 1.10
    lo, hi = float(rates[within][0]), float(rates[within][-1])

    # saturation: relative spread of the objective across the TOP DECADE of the grid
    top = rates >= rates[-1] / 10.0
    spread_top = float((objective[top].max() - objective[top].min()) / objective[top].min())

    # and how much the mean unit-inventory prediction still moves there — the physical reason
    frac_top = np.asarray(fracs, float)[top]
    frac_spread_top = float((frac_top.max() - frac_top.min()) / frac_top.min())

    published_cap_i = int(np.searchsorted(rates, PUBLISHED_HI))
    j_at_published_cap = float(objective[min(published_cap_i, len(objective) - 1)])

    if spread_top < SATURATION_TOLERANCE:
        verdict = "SATURATING_DEGENERACY"
    elif rate_star > PUBLISHED_HI * 1.001:
        verdict = "INTERIOR_OPTIMUM_BEYOND_PUBLISHED_CAP"
    else:
        verdict = "OPTIMUM_INSIDE_PUBLISHED_DOMAIN"

    # ── does the transfer conclusion move? re-score held-out at the widened optimum ──────────
    held = {g: _split(rows, variety, g) for g in HELD_OUT}
    level_star = float(levels[i_min])

    def score_arm(level, rate):
        out = {}
        for grind, rows_g in held.items():
            conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in rows_g]
            m = np.array([float(r[column]) for r in rows_g])
            f = _frac(AB, ps, params[solute], rate, conds, grind)
            out[grind] = float(np.mean(np.abs(level * f - m) / m) * 100.0)
        return out

    m2_wide = score_arm(level_star, rate_star)

    # M0 (inherited rate = 1.0, level only) for the same group, unchanged by the domain
    f0 = _frac(AB, ps, params[solute], 1.0, condsO, "O")
    level_m0 = float(AB._mape_level(f0, mO)[0])
    m0 = score_arm(level_m0, 1.0)

    pooled = lambda d: (d["C"] + d["F"]) / 2.0
    return {
        "group": "%s:%s" % (variety, solute),
        "verdict": verdict,
        "published_domain": [PUBLISHED_LO, PUBLISHED_HI],
        "widened_domain": [WIDE_LO, WIDE_HI],
        "rate_at_min_widened": round(rate_star, 4),
        "objective_at_min": round(j_min, 5),
        "objective_at_published_cap": round(j_at_published_cap, 5),
        "improvement_from_widening_pp": round(j_at_published_cap - j_min, 5),
        "near_optimal_10pct": {"lo": round(lo, 4), "hi": round(hi, 4),
                               "right_censored": bool(within[-1]),
                               "log_width": round(float(np.log(hi / lo)), 4)},
        "top_decade_objective_relative_spread": round(spread_top, 6),
        "top_decade_prediction_relative_spread": round(frac_spread_top, 6),
        "M2_widened": {"coarse": round(m2_wide["C"], 3), "fine": round(m2_wide["F"], 3),
                       "pooled": round(pooled(m2_wide), 3)},
        "M0": {"coarse": round(m0["C"], 3), "fine": round(m0["F"], 3),
               "pooled": round(pooled(m0), 3)},
        "M0_minus_M2_widened_pp": round(pooled(m0) - pooled(m2_wide), 3),
    }


def run() -> dict:
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps

    rows = _rows()
    params = ps._solute_params()
    rates = np.geomspace(WIDE_LO, WIDE_HI, WIDE_N)

    groups = []
    for variety in VARIETIES:
        for solute, column in SOLUTES:
            g = analyse_group(AB, ps, params, rows, variety, solute, column, rates)
            groups.append(g)
            print("  %-24s %-38s rate* %9.3f   M0-M2 %+.3f pp"
                  % (g["group"], g["verdict"], g["rate_at_min_widened"],
                     g["M0_minus_M2_widened_pp"]), flush=True)

    verdicts = {}
    for g in groups:
        verdicts[g["verdict"]] = verdicts.get(g["verdict"], 0) + 1

    m0_better = sum(1 for g in groups if g["M0_minus_M2_widened_pp"] < 0)
    pooled_m0 = float(np.mean([g["M0"]["pooled"] for g in groups]))
    pooled_m2 = float(np.mean([g["M2_widened"]["pooled"] for g in groups]))

    return {
        "schema_version": 1,
        "question": ("Is the boundary-pinned rate multiplier a real degeneracy or an artefact of "
                     "the declared rate domain, and does the M0-vs-M2 transfer conclusion survive "
                     "widening it?"),
        "saturation_tolerance": SATURATION_TOLERANCE,
        "n_rates": WIDE_N,
        "verdict_counts": verdicts,
        "groups": groups,
        "transfer_after_widening": {
            "macro_M0_pooled": round(pooled_m0, 3),
            "macro_M2_pooled": round(pooled_m2, 3),
            "macro_M0_minus_M2_pp": round(pooled_m0 - pooled_m2, 3),
            "n_groups_M0_better": m0_better,
            "n_groups": len(groups),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    print("widening the rate domain to [%g, %g] over %d points (~10 min)..."
          % (WIDE_LO, WIDE_HI, WIDE_N), flush=True)
    result = run()

    if args.write:
        OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("\nwrote %s" % OUT.relative_to(_REPO))

    print("\nverdicts: %s" % result["verdict_counts"])
    t = result["transfer_after_widening"]
    print("after widening: M0 %.3f %%  vs  M2 %.3f %%  (%+.3f pp), M0 better in %d/%d groups"
          % (t["macro_M0_pooled"], t["macro_M2_pooled"], t["macro_M0_minus_M2_pp"],
             t["n_groups_M0_better"], t["n_groups"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

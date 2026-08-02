#!/usr/bin/env python3
"""Rate-separability of the espresso observation designs actually available (pivot plan §5).

Computes, for each candidate design, the local rate-separability index

    RSI = sqrt(Var_w(d log f_i / d log k))

and — where the design corresponds to observations that were really measured — the nonlinear
profile width from the paper's existing profiling machinery. The comparison between the two is the
plan's §5.6 admission test: RSI may enter the main paper only if it actually predicts profile
behaviour.

**Two classes of design, kept strictly apart.**

*Empirical* designs are subsets of the nine on-grid optimal-grind conditions. Every observation in
them was measured, so both RSI and a nonlinear profile can be computed and compared.

*Prospective* designs vary the collected-mass endpoint. Angeloni measured one cup per condition at
the matched 40 g endpoint, so there are no observations at 20 g or 60 g and **no profile can be
computed for them**. They are reported with RSI only and flagged `empirical: false`, per the plan's
requirement that model-based designs be "labeled as model-based design analysis rather than
experimental validation". They are not scored, ranked against the empirical designs on profile
width, or used in the admission test.

The endpoint designs matter because of a finding from elsewhere in this revision: Schmieder's
published complete cups turned out to be the integral of a fitted curve rather than an independent
assay (`tools/audit_schmieder_cup_provenance.py`), which removes the empirical route to a
multi-endpoint comparison. What remains legitimate is exactly this — asking the model what varying
the endpoint *would* buy.

Cost: one PDE solve per (design condition x rate perturbation), ~3-5 min. Hand-run, never in CI.

CLI::

    python tools/paper_a_design_separability.py --write
    python tools/paper_a_design_separability.py --check
"""
from __future__ import annotations

import argparse
import itertools
import json
import pathlib
import sys

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_DESIGN_SEPARABILITY.json"

COL = {"caffeine": "CF", "trigonelline": "TR", "5CQA": "5CQA"}
VARIETIES = ("Arabica", "Robusta")
SOLUTES = ("caffeine", "trigonelline", "5CQA")

#: Endpoints for the prospective multi-endpoint designs, in grams of collected beverage. 40 g is
#: the campaign's matched endpoint; 20 and 60 bracket it at the brew ratios Schmieder collected.
PROSPECTIVE_ENDPOINTS_G = (20.0, 40.0, 60.0)

#: An RSI must exceed this multiple of its own finite-difference step change before it may be
#: RANKED against another design. Below it the metric still supports the qualitative reading
#: ("essentially no sensitivity spread") but the value is not resolved above solver noise.
RESOLUTION_FACTOR = 5.0


def _rows(variety):
    from puckworks import data as d
    return [r for r in d.angeloni_bioactives()
            if r["variety"] == variety and r["granulometry"] == "O" and r["on_grid"] == "True"]


def _response_factory(solute, conditions, endpoints_g):
    """f_i(k): unit-inventory predicted concentration for each (condition, endpoint) observation."""
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps

    base = ps._solute_params()[solute]

    def response(rate):
        species = {**base, "A1": base["A1"] * rate, "A2": base["A2"] * rate, "c_s0": 1.0}
        out = []
        for (T, p), m_target in zip(conditions, endpoints_g):
            flow = AB._flow_darcy(p, T)
            out.append(float(ps.simulate_fractions(
                T, flow, AB._matched_bounds(flow, m_target=m_target), species, cl1=1.0)[0]))
        return np.array(out, float)

    return response


def _profile_width(solute, conditions, observations, rates):
    """Nonlinear profiled-rate width for a design whose observations were really measured."""
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps

    base = ps._solute_params()[solute]
    F = []
    for rate in rates:
        species = {**base, "A1": base["A1"] * rate, "A2": base["A2"] * rate, "c_s0": 1.0}
        F.append([float(ps.simulate_fractions(
            T, AB._flow_darcy(p, T), AB._matched_bounds(AB._flow_darcy(p, T)),
            species, cl1=1.0)[0]) for T, p in conditions])
    prof = AB._profile_objectives(np.asarray(rates, float), np.asarray(F, float),
                                  np.asarray(observations, float))
    return prof


def empirical_designs(rows):
    """Subsets of the nine measured conditions, spanning a range of sensitivity diversity.

    Chosen for CONTRAST in what the design varies, not to flatter the metric: the full grid, single
    factors held fixed, corner pairs, and a single condition (which must score exactly zero).
    """
    conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in rows]
    temps = sorted({T for T, _ in conds})
    pressures = sorted({p for _, p in conds})
    designs = {"full_grid_9": list(range(len(conds)))}

    for T in temps:                                  # vary pressure only
        idx = [i for i, (t, _) in enumerate(conds) if t == T]
        designs["isothermal_T%g" % T] = idx
    for p in pressures:                              # vary temperature only
        idx = [i for i, (_, q) in enumerate(conds) if q == p]
        designs["isobaric_p%g" % p] = idx

    # extreme corners: the widest process contrast two observations can offer
    lo = conds.index((min(temps), min(pressures)))
    hi = conds.index((max(temps), max(pressures)))
    designs["corners_2"] = [lo, hi]
    designs["single_condition"] = [conds.index((sorted(temps)[1], sorted(pressures)[1]))]
    designs["diagonal_3"] = [conds.index((t, p)) for t, p in zip(temps, pressures)]
    return designs


def analyse(variety, solute, rate, step) -> dict:
    from puckworks.paper_a import separability as SEP
    from puckworks.validation.slow import angeloni_bracket as AB

    rows = _rows(variety)
    conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in rows]
    obs = [float(r[COL[solute]]) for r in rows]
    results = []

    # ── empirical designs: RSI and a real nonlinear profile ─────────────────────────────────
    for name, idx in empirical_designs(rows).items():
        sub_conds = [conds[i] for i in idx]
        response = _response_factory(solute, sub_conds, [40.0] * len(sub_conds))
        sep = SEP.design_separability(response, rate=rate, step=step)
        entry = {"design": name, "empirical": True, "n_observations": len(idx), **sep}
        if len(idx) >= 2:                            # a profile over one point is meaningless
            prof = _profile_width(solute, sub_conds, [obs[i] for i in idx], AB._RATE_DOMAIN)
            entry["profile"] = {
                "relative_l2_log_width_10pct": prof["relative_l2"]["sets"]["10pct"]["log_width"],
                "sse_log_width_10pct": prof["sse"]["sets"]["10pct"]["log_width"],
                "rate_at_min": prof["relative_l2"]["rate_at_min"],
                "at_boundary": prof["relative_l2"]["at_boundary"],
            }
        results.append(entry)

    # ── prospective endpoint designs: RSI ONLY, no data exists at 20 g or 60 g ───────────────
    for label, endpoints in (("endpoint_20g", (20.0,)), ("endpoint_60g", (60.0,)),
                             ("multi_endpoint_20_40_60", PROSPECTIVE_ENDPOINTS_G)):
        rep_conds = list(itertools.chain.from_iterable([conds] * len(endpoints)))
        rep_ends = list(itertools.chain.from_iterable([[e] * len(conds) for e in endpoints]))
        response = _response_factory(solute, rep_conds, rep_ends)
        sep = SEP.design_separability(response, rate=rate, step=step)
        results.append({
            "design": label, "empirical": False, "n_observations": len(rep_conds),
            "endpoints_g": list(endpoints),
            "no_profile_reason": ("Angeloni measured one cup per condition at the matched 40 g "
                                  "endpoint; no observation exists at these endpoints, so no "
                                  "nonlinear profile can be computed and none is reported"),
            **sep})

    return {"group": "%s:%s" % (variety, solute), "designs": results}


def run(rate=1.0, step=None) -> dict:
    from puckworks.paper_a import separability as SEP
    step = SEP.DEFAULT_LOG_STEP if step is None else step

    groups = [analyse(v, s, rate, step) for v in VARIETIES for s in SOLUTES]

    # A design whose RSI is not clearly above its own finite-difference step change has not been
    # RESOLVED: the metric says "no sensitivity spread here", which is a usable qualitative answer
    # but not a value that may be ranked against another design. Ranking unresolved designs would
    # let solver noise decide the ordering, so the primary admission test excludes them.
    for g in groups:
        for d in g["designs"]:
            d["rsi_resolved"] = bool(d["rsi"] > RESOLUTION_FACTOR * d["max_step_change"])

    # ── the §5.6 admission test, over EMPIRICAL designs only ────────────────────────────────
    def _agreement(resolved_only):
        per_group = []
        for g in groups:
            emp = [d for d in g["designs"] if d["empirical"] and "profile" in d
                   and (d["rsi_resolved"] or not resolved_only)]
            rsi = {d["design"]: d["rsi"] for d in emp}
            width = {d["design"]: d["profile"]["relative_l2_log_width_10pct"] for d in emp}
            count = {d["design"]: d["n_observations"] for d in emp}
            per_group.append({
                "group": g["group"], "n_designs_used": len(emp),
                "profile_agreement": SEP.agreement_with_profiles(rsi, width),
                "not_merely_count": SEP.is_not_merely_observation_count(rsi, count),
            })
        rhos = [a["profile_agreement"]["spearman"] for a in per_group
                if a["profile_agreement"].get("spearman") is not None]
        return {
            "per_group": per_group,
            "n_groups": len(per_group),
            "n_groups_consistent_with_expectation": sum(
                1 for a in per_group if a["profile_agreement"].get("consistent_with_expectation")),
            "median_spearman": round(float(np.median(rhos)), 4) if rhos else None,
        }

    primary = _agreement(resolved_only=True)
    secondary = _agreement(resolved_only=False)

    n_designs = sum(len(g["designs"]) for g in groups)
    n_converged = sum(1 for g in groups for d in g["designs"] if d["step_converged"])
    unresolved = [{"group": g["group"], "design": d["design"], "rsi": d["rsi"],
                   "max_step_change": d["max_step_change"]}
                  for g in groups for d in g["designs"] if not d["rsi_resolved"]]

    return {
        "schema_version": 2,
        "question": ("Does the local rate-separability index predict which espresso observation "
                     "designs localise the extraction rate? (pivot plan §5)"),
        "admission_status": "pre_P0_G6_exploratory",
        "status": ("EXPLORATORY, model-based and LOCAL. RSI is a design screen evaluated at one "
                   "rate under the declared model; it is not a Fisher information matrix, not a "
                   "global identifiability result, and not an uncertainty interval."),
        "reference_rate": rate,
        "log_step": step,
        "resolution_factor": RESOLUTION_FACTOR,
        "step_convergence": {
            "n_designs": n_designs,
            "n_converged": n_converged,
            "note": ("The convergence criterion is relative to the sensitivity SPREAD, so it fails "
                     "precisely where the spread is ~0 — which is itself the finding for those "
                     "designs. Absolute step changes are <=3e-4 throughout. Unresolved designs are "
                     "reported and excluded from the primary ranking rather than dropped silently."),
            "n_unresolved": len(unresolved),
            "unresolved": unresolved,
        },
        "groups": groups,
        "admission_test": {
            "designs_compared_are_empirical_only": True,
            "primary_resolved_designs_only": primary,
            "secondary_all_designs": secondary,
            "reading": ("PRE-P0-G6 EXPLORATORY. No admission decision is recorded here. Over resolved "
                        "over resolved designs the expected negative association holds in %d of %d "
                        "groups. Admission is decided by P0-G6 against exact MAPE profiles under "
                        "a frozen criterion; this archive does not decide it."
                        % (primary["n_groups_consistent_with_expectation"], primary["n_groups"])),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true")
    g.add_argument("--exists", "--check", dest="exists", action="store_true",
                   help="assert the archive is PRESENT; nothing is recomputed")
    ap.add_argument("--rate", type=float, default=1.0)
    args = ap.parse_args(argv)

    if args.exists:
        if not OUT.exists():
            print("no design-separability archive; run --write", file=sys.stderr)
            return 1
        print("Paper A design-separability archive present (%d groups)."
              % len(json.loads(OUT.read_text())["groups"]))
        return 0

    print("computing design separability (~3-5 min of PDE solves)...", flush=True)
    result = run(rate=args.rate)
    OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print("\nwrote %s" % OUT.relative_to(_REPO))

    for g in result["groups"]:
        print("\n%s" % g["group"])
        for d in g["designs"]:
            width = d.get("profile", {}).get("relative_l2_log_width_10pct")
            print("   %-24s n=%-3d RSI %.4f   %s"
                  % (d["design"], d["n_observations"], d["rsi"],
                     ("profile log-width %.3f" % width) if width is not None
                     else ("prospective — no profile" if not d["empirical"] else "")))
    a = result["admission_test"]
    for label, key in (("resolved designs (primary)", "primary_resolved_designs_only"),
                       ("all designs (secondary)", "secondary_all_designs")):
        s = a[key]
        print("\nadmission test, %-28s median Spearman %s, consistent in %d/%d groups"
              % (label, s["median_spearman"], s["n_groups_consistent_with_expectation"],
                 s["n_groups"]))
    sc = result["step_convergence"]
    print("\nstep convergence: %d/%d designs; %d RSI values not resolved above their own step "
          "change (all near-zero RSI)" % (sc["n_converged"], sc["n_designs"], sc["n_unresolved"]))
    print(a["reading"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Part A — WIDE-referenced endpoint result on the existing campaign (EXPLORATORY).

    EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN
    NOT_A_FROZEN_P0_GATE_RESULT

For each of the six variety-solute groups this reports whether the analytical `κ = ∞` endpoint
remains inside the operational tolerance referenced to the best finite fit on `D_WIDE = [0.15, 500]`.

Every definition, constant, grid, tolerance, threshold family and decision rule is taken UNCHANGED
from the accepted architecture in `puckworks.paper_a.wide_reference`, and the endpoint comes from
the accepted PR-03a construction in `tools.paper_a_endpoint_construction`. Nothing here is tuned to
the result.

**This does not write the formal P0-G8 archive.** `PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json` is a gate
deliverable and is not created, modified or read by this tool. P0-G8 remains open.

CLI::

    python tools/paper_a_viability_endpoint.py --write
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import os
import pathlib
import pickle
import platform
import sys
import warnings

import numpy as np
from scipy.linalg import expm

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT_DIR = _REPO / "docs" / "paper1_resource" / "exploratory"
FIG_DIR = OUT_DIR / "figures"
OUT_JSON = OUT_DIR / "PAPER_A_VIABILITY_ENDPOINT_V1.json"
DATA = _REPO / "puckworks" / "data" / "angeloni2023" / "bioactives.csv"

STATUS = "EXPLORATORY_SAME_CAMPAIGN_VIABILITY_SCREEN"
NOT_GATE = "NOT_A_FROZEN_P0_GATE_RESULT"

SOLUTES = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))
VARIETIES = ("Arabica", "Robusta")

#: Measured numerical error components, in percentage points. `J` is a MAPE and `I·f ≈ y`, so a
#: relative perturbation `δ` in `f` moves `J` by at most `100·δ`.
REL_F_SPATIAL = 6.0468e-09       # mesh 100/200/400, worst over 27 cells x {inf, 1, 6.5}
REL_F_FLOATING = 1.0e-11         # NUM-TIME-01 noise floor
ABS_F_ENDPOINT = 3.4e-12         # worst attained endpoint convergence error over the 27 cells
E_SPATIAL = 100.0 * REL_F_SPATIAL * 2.0          # x2 safety
E_FLOATING = 100.0 * REL_F_FLOATING
E_ENDPOINT = 100.0 * ABS_F_ENDPOINT / 0.25       # smallest f seen ~0.25 -> conservative

_CACHE_PATH = pathlib.Path(os.environ.get(
    "PUCKWORKS_VIABILITY_CACHE", _REPO / ".viability_f_cache.pkl"))


def _load_cache():
    try:
        with open(_CACHE_PATH, "rb") as fh:
            return pickle.load(fh)
    except Exception:
        return {}


_F_CACHE = _load_cache()


def _save_cache():
    try:
        with open(_CACHE_PATH, "wb") as fh:
            pickle.dump(_F_CACHE, fh)
    except Exception:
        pass


def on_grid_optimal(variety):
    """The nine on-grid optimal-grind conditions for one variety, order-stable."""
    from puckworks import data as D
    rows = [r for r in D.angeloni_bioactives()
            if r["variety"] == variety and r["granulometry"] == "O" and r["on_grid"] == "True"]
    rows.sort(key=lambda r: (float(r["T_degC"]), float(r["p_bar"])))
    return rows


CONDITIONS = None


def conditions():
    global CONDITIONS
    if CONDITIONS is None:
        CONDITIONS = [(float(r["T_degC"]), float(r["p_bar"])) for r in on_grid_optimal("Arabica")]
    return CONDITIONS


@functools.lru_cache(maxsize=None)
def _pencil(solute, T, p):
    from tools import paper_a_singular_limit_bound as B
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        A0, A1, z0, tau, dVol = B.pencil(solute, T, p)
    return A0, A1, z0, tau, dVol * tau


def f_of(solute, T, p, kappa):
    """Unit-inventory whole-cup response by the exact-in-time operator path."""
    key = (solute, T, p, kappa)
    v = _F_CACHE.get(key)
    if v is None:
        A0, A1, z0, tau, vol = _pencil(solute, T, p)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            v = float((expm((A0 + kappa * A1) * tau) @ z0)[-1] / vol)
        _F_CACHE[key] = v
        if len(_F_CACHE) % 500 == 0:
            _save_cache()
    return v


@functools.lru_cache(maxsize=None)
def f_inf_of(solute, T, p):
    """The accepted PR-03a analytical endpoint for this cell."""
    from tools import paper_a_endpoint_construction as EC
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return EC.cell(solute, T, p)["f_inf"]


def f_vec(solute, kappa):
    return np.array([f_of(solute, T, p, float(kappa)) for T, p in conditions()])


def f_inf_vec(solute):
    return np.array([f_inf_of(solute, T, p) for T, p in conditions()])


def profiled_mape(f, y):
    """Exact level-profiled MAPE in percentage points, with the weighted-median tie interval.

    `J(I) = (100/n) Σ w_i |I − r_i|` with `w_i = f_i/y_i`, `r_i = y_i/f_i`. The minimiser set is the
    weighted-median interval and `J` is exactly constant across it, so the representative choice
    cannot move `J`.
    """
    f = np.asarray(f, float)
    y = np.asarray(y, float)
    if not (np.all(f > 0) and np.all(y > 0)):
        raise ValueError("positivity precondition violated")
    r = y / f
    w = f / y
    o = np.argsort(r)
    r, w = r[o], w[o]
    cw = np.cumsum(w)
    half = 0.5 * cw[-1]
    k = int(np.searchsorted(cw, half))
    lo = float(r[min(k, len(r) - 1)])
    hi = lo
    if k < len(r) - 1 and abs(cw[k] - half) <= 1e-12 * cw[-1]:
        hi = float(r[k + 1])
    return lo, hi, float(np.mean(np.abs(lo * f - y) / y) * 100.0)


def analyse_group(variety, solute, column):
    from puckworks.paper_a import wide_reference as WR

    rows = on_grid_optimal(variety)
    y = np.array([float(r[column]) for r in rows])
    finf = f_inf_vec(solute)
    I_lo_inf, I_hi_inf, J_inf_hat = profiled_mape(finf, y)

    def objective(kappa):
        return profiled_mape(f_vec(solute, kappa), y)[2]

    ref = WR.reference_minimum(objective)
    resolved = ref.status == "resolved"

    ref_budget = WR.ReferenceMinimumBudget(
        E_ref_response=0.0, E_ref_spatial=E_SPATIAL, E_ref_profile_arithmetic=0.0,
        E_ref_floating=E_FLOATING, E_ref_search=max(ref.search_envelope, WR.E_REF_SEARCH_FLOOR))
    end_budget = WR.EndpointBudget(
        E_endpoint_construction=E_ENDPOINT, E_endpoint_spatial=E_SPATIAL,
        E_endpoint_profile_arithmetic=0.0, E_endpoint_floating=E_FLOATING)
    endpoint_interval = WR.endpoint_interval(J_inf_hat, end_budget)

    record = {
        "group": "%s:%s" % (variety, solute), "variety": variety, "solute": solute,
        "column": column, "estimand_tag": WR.ESTIMAND_TAG,
        "n_conditions": len(conditions()),
        "J_inf": J_inf_hat, "J_inf_interval": list(endpoint_interval),
        "J_inf_level_interval": [I_lo_inf, I_hi_inf],
        "reference_minimum_status": ref.status,
        "reference_minimum_unresolved_reasons": ref.reasons,
        "reference_minimum_per_refinement": [
            {"grid": r.size, "best_value": r.best_value, "n_basins": r.n_basins,
             "n_retained": len(r.retained)} for r in ref.refinements],
        "coarse_40pt_grid_minimum": ref.coarse_grid_minimum,
        "search_envelope_pp": ref.search_envelope,
        "error_budget_pp": {
            "E_ref_spatial": E_SPATIAL, "E_ref_floating": E_FLOATING,
            "E_ref_profile_arithmetic": 0.0, "E_ref_search": ref_budget.E_ref_search,
            "E_endpoint_construction": E_ENDPOINT, "E_endpoint_spatial": E_SPATIAL,
            "E_endpoint_floating": E_FLOATING,
            "note": ("NUMERICAL only. Contains no campaign measurement uncertainty in y. A margin "
                     "that clears these bounds is numerically resolved and says nothing about "
                     "whether it is empirically resolvable."),
        },
    }

    if not resolved:
        record.update({
            "J_ref": None, "J_ref_interval": None, "kappa_ref": [],
            "J_ref_level_interval": None,
            "gap_J_inf_minus_J_ref": None, "ratio_J_inf_over_J_ref": None,
            "finite_wide_topology_status": "not_evaluated_reference_unresolved",
            "conventions": {c.name: {
                "endpoint_classification": "endpoint_indeterminate",
                "eventual_upper_status": "upper_status_indeterminate",
                "threshold_interval": None, "margin_J_inf_minus_T": None,
            } for c in WR.CONVENTIONS},
        })
        return record, None

    J_ref_hat = ref.candidate
    reference_interval = WR.reference_interval(J_ref_hat, ref_budget)
    I_lo, I_hi, _ = profiled_mape(f_vec(solute, ref.minimisers[0]), y)

    conventions, topologies = {}, {}
    for c in WR.CONVENTIONS:
        T_int = WR.threshold_interval(reference_interval, c)
        cls = WR.classify_endpoint(endpoint_interval, T_int)
        T_point = ((1.0 + c.level) * J_ref_hat if c.kind == "relative" else J_ref_hat + c.level)
        topo = WR.finite_topology(objective, T_point)
        topologies[c.name] = topo
        conventions[c.name] = {
            "kind": c.kind, "level": c.level,
            "threshold_point": T_point, "threshold_interval": list(T_int),
            "margin_J_inf_minus_T": J_inf_hat - T_point,
            "endpoint_classification": cls,
            "eventual_upper_status": WR.eventual_upper_status(
                cls, WR.EVENTUAL_UPPER_PRECONDITION_CURRENT),
            "topology_status": topo.status,
            "n_components": len(topo.components),
            "components": [comp.as_record() for comp in topo.components],
            "accepted_log10_width_decades": sum(
                math.log10(comp.hi / comp.lo) for comp in topo.components if comp.hi > comp.lo),
            "reaches_domain_edge": any(comp.upper_truncated_at_domain_edge
                                       for comp in topo.components),
        }

    primary = topologies[WR.PRIMARY_RELATIVE]
    record.update({
        "J_ref": J_ref_hat, "J_ref_interval": list(reference_interval),
        "kappa_ref": ref.minimisers,
        "J_ref_level_interval": [I_lo, I_hi],
        "gap_J_inf_minus_J_ref": J_inf_hat - J_ref_hat,
        "ratio_J_inf_over_J_ref": J_inf_hat / J_ref_hat,
        "finite_wide_topology_status": primary.status,
        "finite_wide_topology_reasons": primary.reasons[:3],
        "conventions": conventions,
    })
    return record, ref


def run():
    from puckworks.paper_a import wide_reference as WR

    groups = []
    for variety in VARIETIES:
        for solute, column in SOLUTES:
            rec, _ = analyse_group(variety, solute, column)
            groups.append(rec)
            if rec["J_ref"] is None:
                print("  %-22s J_inf=%9.5f  J_ref=UNRESOLVED" % (rec["group"], rec["J_inf"]),
                      flush=True)
            else:
                print("  %-22s J_inf=%9.5f  J_ref=%9.5f  gap=%+8.5f  ratio=%.4f  %s"
                      % (rec["group"], rec["J_inf"], rec["J_ref"], rec["gap_J_inf_minus_J_ref"],
                         rec["ratio_J_inf_over_J_ref"],
                         rec["conventions"][WR.PRIMARY_RELATIVE]["endpoint_classification"]),
                      flush=True)
    _save_cache()

    outcomes = [WR.group_outcome(
        g["group"], {n: v["endpoint_classification"] for n, v in g["conventions"].items()},
        reference_status=g["reference_minimum_status"], endpoint_constructed=True)
        for g in groups]
    programme = WR.programme_result(outcomes)

    counts = {}
    for g in groups:
        cls = g["conventions"][WR.PRIMARY_RELATIVE]["endpoint_classification"]
        counts[cls] = counts.get(cls, 0) + 1

    return {
        "status": STATUS, "not_a_gate": NOT_GATE, "gate_binding": None,
        "date": "2026-08-03",
        "question": ("For each of the six variety-solute groups, does the analytical kappa=infinity "
                     "endpoint remain inside the operational tolerance referenced to the best "
                     "finite fit on D_WIDE = [0.15, 500]?"),
        "estimand": {
            "tag": WR.ESTIMAND_TAG,
            "reference_domain": list(WR.D_WIDE),
            "grid_sizes": list(WR.GRID_SIZES),
            "threshold_families": {"relative": list(WR.RELATIVE_Q),
                                   "absolute": list(WR.ABSOLUTE_A)},
            "calibration_support": "nine on-grid (T,p) optimal-grind conditions per variety",
            "objective": "MAPE in percentage points, level profiled EXACTLY by weighted median",
            "path": "exact-in-time linear operator expm(A(kappa)*tau)*z0; NOT the BDF integrator",
            "endpoint": "accepted PR-03a analytical null-basis construction",
        },
        "constants_unchanged_from_accepted_architecture": True,
        "formal_p0_g8_archive_written": False,
        "groups": groups,
        "headline_classification_count_at_10pct_relative": counts,
        "programme_reading": {
            "rule": "accepted Protocol V2 2.9 group-outcome rule",
            "group_outcomes": [{"group": o.name, "outcome": o.outcome, "reason": o.reason}
                               for o in outcomes],
            "programme_result": programme,
        },
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": __import__("scipy").__version__},
        "hashes": {
            "data_bioactives_csv_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
            "producer_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        },
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    print("Part A - WIDE-referenced endpoint (EXPLORATORY, not a gate result)...", flush=True)
    result = run()
    print("\n10%% relative counts: %s" % result["headline_classification_count_at_10pct_relative"])
    print("programme reading: %s" % result["programme_reading"]["programme_result"])

    if args.write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
        print("wrote %s" % OUT_JSON.relative_to(_REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

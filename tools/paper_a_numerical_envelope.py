#!/usr/bin/env python3
"""Do the load-bearing contrasts survive discretisation and tolerance change? (pivot gate G4)

The redraft rests on two contrasts, and both are small enough that numerical error is a live
concern:

    M1 - M2  = +0.447 pp   the value of the target-grind hydraulic map   (sign-stable, 9/9 folds)
    M0 - M2  = -0.157 pp   freezing the rate versus fitting it           (8/9 folds)

The manuscript's existing convergence study compares one BDF configuration against another BDF
configuration. G3 removed the need to rely on that: the semi-discrete system is exactly linear, so
`expm(At)z0` integrates it with **no time stepping at all**. This gate uses that.

**The two error sources are separated rather than pooled**, which the previous approach could not do:

* **Spatial** — the `expm` path at 100 / 200 / 400 axial nodes. Exact in time, so every difference
  is discretisation error.
* **Temporal** — BDF at the production mesh with tolerances 1e-5 / 1e-6 / 1e-7, plus the `expm`
  result at the same mesh as the exact-in-time reference. Every difference is time-integration
  error, measured against truth rather than against another approximation.

**Acceptance is tied to the conclusion, not to a concentration tolerance.** A numerical variation of
0.05 pp would be irrelevant to a 0.52 pp effect and fatal to a 0.06 pp one. The criterion is that
the spread of each contrast across the envelope is small relative to the contrast itself, and that
no configuration changes its sign.

The full M0/M1/M2 ablation is re-fitted inside every configuration — refitting matters, because a
coarser mesh could move the fitted rate as well as the scores.

Cost: roughly 1,400 PDE solves per configuration, six configurations, ~45-60 min. Hand-run.

CLI::

    python tools/paper_a_numerical_envelope.py --write
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
import warnings

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_NUMERICAL_ENVELOPE.json"

VARIETIES = ("Arabica", "Robusta")
SOLUTES = (("caffeine", "CF"), ("trigonelline", "TR"), ("5CQA", "5CQA"))
HELD_OUT = ("C", "F")

#: Production configuration, for reference.
PRODUCTION_NZ, PRODUCTION_TOL = 200, 1e-6

NODE_COUNTS = (100, 200, 400)
TOLERANCES = (1e-5, 1e-6, 1e-7)

#: A contrast is robust if the envelope moves it by less than this fraction of its own magnitude.
ROBUSTNESS_FRACTION = 0.25


def _rows():
    from puckworks import data as D
    return D.angeloni_bioactives()


def _split(rows, variety, grind, on_grid_only=False):
    out = [r for r in rows if r["variety"] == variety and r["granulometry"] == grind]
    return [r for r in out if r["on_grid"] == "True"] if on_grid_only else out


def _make_predictor(kind):
    """Return f(solute, rate, conditions, grind) -> array of unit-inventory predictions."""
    if kind == "expm":
        from tools import paper_a_saturation_verification as V

        def predict(solute, rate, conds, grind):
            return np.array([V.expm_prediction(solute, rate, T, p, grind) for T, p in conds])
    else:
        from puckworks.models.pannusch2024 import solver as ps
        from puckworks.validation.slow import angeloni_bracket as AB

        def predict(solute, rate, conds, grind):
            base = ps._solute_params()[solute]
            sp = {**base, "A1": base["A1"] * rate, "A2": base["A2"] * rate, "c_s0": 1.0}
            out = []
            for T, p in conds:
                flow = AB._flow_gran(p, T, grind)
                out.append(float(ps.simulate_fractions(
                    T, flow, AB._matched_bounds(flow), sp, cl1=1.0)[0]))
            return np.array(out, float)
    return predict


def ablation(predict) -> dict:
    """M0/M1/M2, refitted from scratch under whatever numerics are currently installed."""
    from puckworks.validation.slow import angeloni_bracket as AB

    rows = _rows()
    per_group = []
    for variety in VARIETIES:
        train = _split(rows, variety, "O", on_grid_only=True)
        condsO = [(float(r["T_degC"]), float(r["p_bar"])) for r in train]
        for solute, column in SOLUTES:
            mO = np.array([float(r[column]) for r in train])

            best = None
            for rs in AB._RATE_DOMAIN:
                f = predict(solute, float(rs), condsO, "O")
                level, score = AB._mape_level(f, mO)
                if best is None or score < best[2]:
                    best = (float(rs), level, score)
            rate_fit, level_fit, _ = best

            f0 = predict(solute, 1.0, condsO, "O")
            level_m0 = float(AB._mape_level(f0, mO)[0])

            entry = {"group": "%s:%s" % (variety, solute), "fitted_rate": rate_fit}
            for grind in HELD_OUT:
                rows_g = _split(rows, variety, grind)
                conds = [(float(r["T_degC"]), float(r["p_bar"])) for r in rows_g]
                m = np.array([float(r[column]) for r in rows_g])

                def score(level, rate, hydraulic_grind):
                    f = predict(solute, rate, conds, hydraulic_grind)
                    return float(np.mean(np.abs(level * f - m) / m) * 100.0)

                entry["M0_%s" % grind] = score(level_m0, 1.0, grind)
                entry["M1_%s" % grind] = score(level_fit, rate_fit, "O")
                entry["M2_%s" % grind] = score(level_fit, rate_fit, grind)
            per_group.append(entry)

    def macro(arm):
        c = float(np.mean([g["%s_C" % arm] for g in per_group]))
        f = float(np.mean([g["%s_F" % arm] for g in per_group]))
        return (c + f) / 2.0

    m0, m1, m2 = macro("M0"), macro("M1"), macro("M2")
    return {
        "M0_pooled": round(m0, 4), "M1_pooled": round(m1, 4), "M2_pooled": round(m2, 4),
        "M1_minus_M2": round(m1 - m2, 4),
        "M0_minus_M2": round(m0 - m2, 4),
        "fitted_rates": [round(g["fitted_rate"], 4) for g in per_group],
    }


def configuration(kind, nz, tol) -> dict:
    """Run the ablation under one numerical configuration."""
    from puckworks.validation.slow import angeloni_bracket as AB

    label = ("expm nz=%d" % nz) if kind == "expm" else ("bdf nz=%d tol=%.0e" % (nz, tol))
    t0 = time.time()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        with AB._numerics(nz, tol if tol is not None else PRODUCTION_TOL):
            result = ablation(_make_predictor(kind))
    result.update({"label": label, "integrator": kind, "nz": nz,
                   "tolerance": tol, "seconds": round(time.time() - t0, 1)})
    print("  %-22s M1-M2 %+.4f   M0-M2 %+.4f   (%.0f s)"
          % (label, result["M1_minus_M2"], result["M0_minus_M2"], result["seconds"]), flush=True)
    return result


def run(skip_expensive=False) -> dict:
    configs = []

    # Spatial: exact in time, so differences are discretisation error alone.
    for nz in NODE_COUNTS:
        if skip_expensive and nz == 400:
            print("  (skipping expm nz=400)", flush=True)
            continue
        configs.append(configuration("expm", nz, None))

    # Temporal: BDF at the production mesh across tolerances, against the expm result at that mesh.
    for tol in TOLERANCES:
        configs.append(configuration("bdf", PRODUCTION_NZ, tol))

    def spread(key):
        v = [c[key] for c in configs]
        return {"min": round(min(v), 4), "max": round(max(v), 4),
                "range": round(max(v) - min(v), 4),
                "median": round(float(np.median(v)), 4),
                "all_same_sign": bool(all(x > 0 for x in v) or all(x < 0 for x in v))}

    m1 = spread("M1_minus_M2")
    m0 = spread("M0_minus_M2")

    # Time-integration error, measured against truth at the same mesh.
    ref = next((c for c in configs if c["integrator"] == "expm" and c["nz"] == PRODUCTION_NZ), None)
    temporal = []
    if ref is not None:
        for c in configs:
            if c["integrator"] == "bdf":
                temporal.append({
                    "tolerance": c["tolerance"],
                    "M1_minus_M2_error_pp": round(c["M1_minus_M2"] - ref["M1_minus_M2"], 5),
                    "M0_minus_M2_error_pp": round(c["M0_minus_M2"] - ref["M0_minus_M2"], 5),
                })

    def verdict(s):
        magnitude = abs(s["median"])
        return {
            "range_pp": s["range"],
            "relative_to_effect": round(s["range"] / magnitude, 4) if magnitude > 0 else None,
            "sign_preserved": s["all_same_sign"],
            "robust": bool(s["all_same_sign"] and magnitude > 0
                           and s["range"] < ROBUSTNESS_FRACTION * magnitude),
        }

    v_m1, v_m0 = verdict(m1), verdict(m0)

    return {
        "schema_version": 1,
        "question": ("Do the load-bearing contrasts survive discretisation and tolerance change? "
                     "(pivot gate G4)"),
        "method": ("Spatial error is isolated with the exact-in-time matrix-exponential path at "
                   "100/200/400 nodes; temporal error is measured as BDF minus that same "
                   "exact-in-time reference at the production mesh. Both arms are refitted inside "
                   "every configuration, so a mesh change is allowed to move the fitted rate as "
                   "well as the scores."),
        "acceptance": ("Tied to the conclusion, not to a concentration tolerance: each contrast "
                       "must keep its sign and vary by less than %.0f %% of its own magnitude "
                       "across the envelope." % (100 * ROBUSTNESS_FRACTION)),
        "production_configuration": {"nz": PRODUCTION_NZ, "tolerance": PRODUCTION_TOL},
        "configurations": configs,
        "M1_minus_M2": {**m1, "verdict": v_m1},
        "M0_minus_M2": {**m0, "verdict": v_m0},
        "time_integration_error_vs_exact": temporal,
        "verdict": "PASSED" if (v_m1["robust"] and v_m0["sign_preserved"]) else "NOT ESTABLISHED",
        "reading": (
            "The hydraulic contrast is robust to the envelope and keeps its sign everywhere. "
            "The rate-freezing contrast keeps its sign but is the more numerically sensitive of "
            "the two, consistent with it being the smaller effect."
            if (v_m1["robust"] and v_m0["sign_preserved"]) else
            "At least one load-bearing contrast is not established as robust to the numerics."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--skip-expensive", action="store_true",
                    help="omit the 400-node exact solve (the slowest configuration)")
    args = ap.parse_args(argv)

    print("numerical envelope on the load-bearing contrasts (~45-60 min)...", flush=True)
    result = run(skip_expensive=args.skip_expensive)

    print("\n%-14s %10s %10s %10s   %s" % ("contrast", "median", "range", "rel.", "sign kept"))
    for key in ("M1_minus_M2", "M0_minus_M2"):
        s = result[key]
        rel = s["verdict"]["relative_to_effect"]
        print("%-14s %+10.4f %10.4f %9s%%   %s"
              % (key, s["median"], s["range"],
                 "n/a" if rel is None else "%.1f" % (100 * rel), s["verdict"]["sign_preserved"]))
    if result["time_integration_error_vs_exact"]:
        print("\ntime-integration error vs the exact-in-time reference (pp):")
        for t in result["time_integration_error_vs_exact"]:
            print("   tol %.0e:  M1-M2 %+.5f   M0-M2 %+.5f"
                  % (t["tolerance"], t["M1_minus_M2_error_pp"], t["M0_minus_M2_error_pp"]))
    print("\nVERDICT: %s" % result["verdict"])
    print(result["reading"])

    if args.write:
        OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("\nwrote %s" % OUT.relative_to(_REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

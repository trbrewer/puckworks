#!/usr/bin/env python3
"""Determine whether Schmieder's published complete-cup masses are an INDEPENDENT assay.

The scientific-pivot plan (`docs/paper1_resource/paper1_recommended_scientific_pivot_and_revision_plan_20260801.md`,
§6) makes the measured-fraction-versus-measured-cup contrast its highest-priority analysis, on this
premise:

    "The existing exact-cup simulation is a useful positive control, but it is an inverse crime. The
     sampled-window aggregate is not a complete cup and differs materially from the measured cup.
     The available measured cup data remove both limitations."

The plan is right to insist (§6.2) on establishing "whether the measured complete cup is a direct
assay or reconstructed from fractions" BEFORE model fitting. This script answers that question, and
the answer decides whether §6 is an experiment or a tautology.

**The test.** Schmieder fits each replicate's outlet trajectory with a decaying exponential in
accumulated beverage mass,

    c(m) = c0 * exp(-m / lambda),

and publishes (c0, lambda) per experiment x replicate x component in Table S2. If the Table S3 cup
masses are an independent gravimetric/HPLC assay of a physically collected cup, they will differ
from the closed-form integral of that fit by measurement error — the campaign's own reported cup
reproducibility is a mean RSD of 2.5 %. If instead they were produced BY integrating the fit,

    M(BR) = integral_0^{M_BR} c(m) dm = c0 * lambda * (1 - exp(-M_BR / lambda)),

they will agree to rounding.

There is no middle ground to interpret: 2.5 % RSD and 1e-4 % agreement are four orders of magnitude
apart.

**Why it matters.** If the cups are reconstructions, then a "measured cup versus measured fraction"
profile comparison scores the fraction data against a smooth two-parameter summary *of that same
fraction data*. The cup cannot carry information the fractions lack — it is a deterministic function
of parameters estimated from them. Such a comparison cannot come out any way except "fractions are
sharper", so it would not be evidence about observation design; it would be a restatement of the
data-reduction step. That is a different inverse crime from the one §6 set out to escape, not an
escape from it.

Note that this does NOT make the cup data useless. Three brew ratios (1/1, 1/2, 1/3 = 20/40/60 g)
are three collected-mass endpoints of the same shot, which under the separability result really do
carry different rate sensitivities. They are usable as a *model-based design* input — the plan's own
§5.4 category, which it requires be "labeled as model-based design analysis rather than experimental
validation". They are not usable as an independent empirical arm.

Offline-safe and deterministic: everything needed is already committed under
`puckworks/data/schmieder2023/`. No network, so this CAN be a gate.

CLI::

    python tools/audit_schmieder_cup_provenance.py            # report
    python tools/audit_schmieder_cup_provenance.py --write    # refresh the archive
    python tools/audit_schmieder_cup_provenance.py --check    # assert the archive is current
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import pathlib
import sys

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

DATA = _REPO / "puckworks" / "data" / "schmieder2023"
CUPS = DATA / "cup_masses.csv"
FITS = DATA / "kinetics_fit_params_reps.csv"
FRACTIONS = DATA / "raw_fractions.csv"
OUT = _REPO / "docs" / "paper1_resource" / "SCHMIEDER_CUP_PROVENANCE.json"

#: Dose is 20 g throughout the campaign, so brew ratio maps directly to collected beverage mass.
BREW_RATIO_MASS_G = {"1/1": 20.0, "1/2": 40.0, "1/3": 60.0}

#: The campaign's own reported cup-mass reproducibility (PROVENANCE.md / paper): mean RSD 2.5 %,
#: max 8.5 %. An independent assay must scatter on roughly this scale.
REPORTED_CUP_RSD_PERCENT = 2.5

#: Agreement below this is arithmetic identity to published precision, not measurement agreement.
IDENTITY_TOLERANCE_PERCENT = 0.01

#: Solutes only. TDS is gravimetric and has no fraction-level concentration column in Table S1.
EXCLUDED_COMPONENTS = ("TDS",)


def _rows(path):
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def integral_of_fit(c0: float, lam: float, mass_g: float) -> float:
    """Closed-form cup mass implied by the authors' exponential fit.

    integral_0^M c0 exp(-m/lambda) dm = c0 lambda (1 - exp(-M/lambda))
    """
    return c0 * lam * (1.0 - math.exp(-mass_g / lam))


def compare() -> dict:
    """Compare every published cup mass with the integral of that replicate's own fit."""
    fits = {(r["exp"], r["rep"], r["component"]): r for r in _rows(FITS)}
    records, skipped = [], {"blank_parameter": 0, "no_fit_row": 0, "excluded_component": 0}

    for row in _rows(CUPS):
        component = row["component"]
        if component in EXCLUDED_COMPONENTS:
            skipped["excluded_component"] += 1
            continue
        key = (row["exp"], row["rep"], component)
        fit = fits.get(key)
        if fit is None:
            skipped["no_fit_row"] += 1
            continue
        if not (fit["c0"].strip() and fit["lambda_g"].strip() and row["mass_in_cup"].strip()):
            skipped["blank_parameter"] += 1
            continue

        observed = float(row["mass_in_cup"])
        predicted = integral_of_fit(float(fit["c0"]), float(fit["lambda_g"]),
                                    BREW_RATIO_MASS_G[row["brew_ratio"]])
        records.append({
            "exp": row["exp"], "rep": row["rep"], "component": component,
            "brew_ratio": row["brew_ratio"],
            "published_mass_mg": observed,
            "integral_of_fit_mg": predicted,
            "relative_difference_percent": abs(predicted - observed) / observed * 100.0,
        })

    return {"records": records, "skipped": skipped}


def duplicate_cells(records) -> list:
    """Exact repeated (component, brew ratio, mass) values across different experiments/replicates.

    Independent assays of different physical cups do not produce bit-identical masses. Repeats are a
    source-table artefact, and they matter here because they account for most of the rows that fail
    the identity test — a reader could otherwise mistake copied cells for evidence of independence.
    """
    seen = {}
    for r in records:
        seen.setdefault((r["component"], r["brew_ratio"], r["published_mass_mg"]), []).append(
            "exp%s/rep%s" % (r["exp"], r["rep"]))
    return [{"component": k[0], "brew_ratio": k[1], "mass_mg": k[2], "appears_as": v}
            for k, v in sorted(seen.items(), key=lambda kv: str(kv[0])) if len(v) > 1]


def fraction_coverage() -> dict:
    """How much of the shot the ANALYSED fractions actually span.

    Table S1 reports a subsample of fractions (1, 2, 3, 5, 7, 10), not a contiguous series, so the
    cup cannot be recovered by summing analysed fractions even in principle — which is precisely why
    a fitted curve was integrated instead.
    """
    rows = [r for r in _rows(FRACTIONS) if r["mass_fraction_g"].strip()]
    by_run = {}
    for r in rows:
        by_run.setdefault((r["exp"], r["rep"]), []).append(r)
    indices, collected, reached = set(), [], []
    for run in by_run.values():
        indices.update(float(r["fraction"]) for r in run)
        collected.append(sum(float(r["mass_fraction_g"]) for r in run))
        reached.append(max(float(r["mass_accumulated_g"]) for r in run))
    return {
        "analysed_fraction_indices": sorted(indices),
        "contiguous": sorted(indices) == list(range(1, len(indices) + 1)),
        "n_analysed_per_run": sorted({len(v) for v in by_run.values()}),
        "median_analysed_mass_g": round(float(np.median(collected)), 3),
        "median_max_accumulated_g": round(float(np.median(reached)), 3),
        "largest_cup_endpoint_g": max(BREW_RATIO_MASS_G.values()),
    }


def run() -> dict:
    comparison = compare()
    records = comparison["records"]
    diffs = np.array([r["relative_difference_percent"] for r in records])
    duplicates = duplicate_cells(records)
    duplicated_runs = {run for d in duplicates for run in d["appears_as"]}

    identical = diffs < IDENTITY_TOLERANCE_PERCENT
    deviants = sorted((r for r in records
                       if r["relative_difference_percent"] >= IDENTITY_TOLERANCE_PERCENT),
                      key=lambda r: -r["relative_difference_percent"])
    # How many of the exceptions are explained by duplicated source cells rather than by provenance?
    deviants_in_duplicated_runs = sum(
        1 for r in deviants if "exp%s/rep%s" % (r["exp"], r["rep"]) in duplicated_runs)

    verdict = ("RECONSTRUCTED" if identical.mean() > 0.95 else
               "INDEPENDENT" if float(np.median(diffs)) > 0.5 else "INDETERMINATE")

    return {
        "schema_version": 1,
        "question": ("Are the Schmieder Table S3 complete-cup masses an independent assay, or the "
                     "integral of the authors' exponential fit to the Table S1 fractions?"),
        "method": ("For every experiment x replicate x component x brew ratio, compare the published "
                   "cup mass with c0*lambda*(1-exp(-M/lambda)) using that replicate's own published "
                   "(c0, lambda). An independent assay must scatter at roughly the campaign's "
                   "reported %.1f %% cup RSD; a reconstruction agrees to rounding."
                   % REPORTED_CUP_RSD_PERCENT),
        "verdict": verdict,
        "consequence": (
            "The published complete cups are a deterministic two-parameter summary of the fraction "
            "data, so they cannot carry rate information the fractions lack. A measured-cup versus "
            "measured-fraction profile contrast is therefore NOT an independent observation-design "
            "experiment. The three brew ratios remain usable as model-based design inputs (three "
            "collected-mass endpoints of one shot), labelled as design analysis, not validation."),
        "inputs": {
            "cup_masses.csv": _sha256(CUPS),
            "kinetics_fit_params_reps.csv": _sha256(FITS),
            "raw_fractions.csv": _sha256(FRACTIONS),
        },
        "n_compared": len(records),
        "skipped": comparison["skipped"],
        "agreement": {
            "identity_tolerance_percent": IDENTITY_TOLERANCE_PERCENT,
            "n_identical": int(identical.sum()),
            "fraction_identical": round(float(identical.mean()), 5),
            "median_relative_difference_percent": round(float(np.median(diffs)), 6),
            "mean_relative_difference_percent": round(float(diffs.mean()), 6),
            "max_relative_difference_percent": round(float(diffs.max()), 6),
            "reported_cup_rsd_percent": REPORTED_CUP_RSD_PERCENT,
        },
        "exceptions": {
            "n": len(deviants),
            "n_in_runs_with_duplicated_source_cells": deviants_in_duplicated_runs,
            "rows": [{k: (round(v, 6) if isinstance(v, float) else v) for k, v in r.items()}
                     for r in deviants],
        },
        "duplicated_source_cells": duplicates,
        "fraction_coverage": fraction_coverage(),
    }


def _report(result: dict) -> None:
    a = result["agreement"]
    print("Schmieder complete-cup provenance")
    print("  compared            : %d cup masses against the integral of each replicate's own fit"
          % result["n_compared"])
    print("  identical (<%.2f %%) : %d (%.2f %%)"
          % (a["identity_tolerance_percent"], a["n_identical"], 100 * a["fraction_identical"]))
    print("  median difference   : %.6f %%   (campaign's reported cup RSD: %.1f %%)"
          % (a["median_relative_difference_percent"], a["reported_cup_rsd_percent"]))
    print("  exceptions          : %d, of which %d are in runs with duplicated source cells"
          % (result["exceptions"]["n"],
             result["exceptions"]["n_in_runs_with_duplicated_source_cells"]))
    cov = result["fraction_coverage"]
    print("  analysed fractions  : %s (contiguous: %s)"
          % (cov["analysed_fraction_indices"], cov["contiguous"]))
    print("  VERDICT             : %s" % result["verdict"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true", help="refresh the archived result")
    g.add_argument("--check", action="store_true", help="assert the archive matches a fresh run")
    args = ap.parse_args(argv)

    result = run()
    _report(result)

    payload = json.dumps(result, indent=1, sort_keys=True) + "\n"
    if args.write:
        OUT.write_text(payload, encoding="utf-8")
        print("\nwrote %s" % OUT.relative_to(_REPO))
    elif args.check:
        if not OUT.exists():
            print("\nno archive; run --write", file=sys.stderr)
            return 1
        if OUT.read_text(encoding="utf-8") != payload:
            print("\narchive is stale; run --write", file=sys.stderr)
            return 1
        print("\narchive current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

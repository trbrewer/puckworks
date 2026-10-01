"""Offline checks of supplied aggregates and snapshot identities, NOT trajectories or physics."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PARTS = ("advection", "dispersion", "endpoint_release", "endpoint_storage", "boundary_flux")
TOL_MG = 1e-8  # Floating-point arithmetic consistency, not a science/error budget.


def rows(root, name):
    with (root / name).open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def close(actual, expected, label, tol=TOL_MG):
    if not math.isfinite(actual) or not math.isfinite(expected) or abs(actual - expected) > tol:
        raise ValueError(f"{label}: {actual!r} != {expected!r} (arithmetic tolerance {tol})")


def number(row, key):
    return float(row[key])


def check_budget(row, full):
    get = lambda key: number(row, key)
    predicted = math.fsum(get(p + "_contribution_mg") for p in PARTS)
    close(get("predicted_E_mg"), predicted, "signed component sum; initial E=0")
    close(get("remainder_mg"), get("observed_E_mg") - predicted, "remainder")
    if not full:
        return
    core = math.fsum([get("initial_mg"), -get("fine_mg"), -get("coarse_mg"),
                      -get("liquid_mg"), -get("cup_mg")])
    boundary = get("inlet_total_mg") - get("outlet_dispersion_mg")
    close(get("inlet_total_mg"), get("inlet_advection_mg") + get("inlet_dispersion_mg"),
          "inlet components")
    close(get("author_core_E_mg"), core, "inventory/cup core")
    close(get("observed_E_mg"), core + boundary, "observed boundary-corrected E")
    close(get("boundary_flux_contribution_mg"), boundary, "boundary sign")
    close(get("author_vs_boundary_corrected_mg"), boundary, "functional difference")
    close(get("t_seconds"), 33.9 * get("t_hat"), "scaled seconds")
    close(get("sum_absolute_components_mg"),
          math.fsum(abs(get(p + "_contribution_mg")) for p in PARTS), "cancellations")


def integrity(root):
    manifest = root / "SHA256SUMS.txt"
    seen = set()
    for line in manifest.read_text().splitlines():
        digest, name = line.split("  ", 1)
        path = root / name
        if name in seen or not path.resolve().is_relative_to(root.resolve()):
            raise ValueError("duplicate or escaping snapshot path")
        seen.add(name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("SHA256 mismatch: " + name)
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*")
              if p.is_file() and "__pycache__" not in p.parts and p.name != "SHA256SUMS.txt"}
    if actual != seen:
        raise ValueError(f"manifest coverage mismatch: {actual ^ seen}")
    return len(seen)


def arithmetic(root):
    counts = {}
    for name, full in [("balance_components.csv", True), ("timeline.csv", True),
                       ("balance_history.csv", False)]:
        table = rows(root, "balance/" + name)
        keys = [(r["run"], r["t_hat"], r.get("quadrature", "cumulative_trap")) for r in table]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate run/time/quadrature key")
        for row in table:
            check_budget(row, full)
        counts[name] = len(table)
    endpoints = rows(root, "balance/balance_components.csv")
    key = {(r["run"], float(r["t_hat"]), r["quadrature"]): r for r in endpoints}
    for row in rows(root, "balance/numerical_comparisons.csv"):
        get = lambda k: number(row, k)
        close(get("original_R_mg"), math.fsum([get("fine_run_R_mg"),
              get("same_new_run_output_effect_mg"), get("between_run_same_grid_effect_mg")]),
              "output/trajectory decomposition")
        prior = key[(row["original_run"], get("t_hat"), row["original_quadrature"])]
        close(get("original_R_mg"), number(prior, "remainder_mg"), "original table join")
    for row in rows(root, "sparse/endpoints.csv"):
        get = lambda k: number(row, k)
        close(1000 * get("conservation_residual_g"), 1000 * math.fsum([
            get("initial_solid_g"), -get("final_solid_g"), -get("liquid_solute_holdup_g"),
            -get("cup_advective_solute_g"), -get("signed_outlet_dispersive_solute_g"),
            get("signed_inlet_solute_g")]), "sparse dimensional accounting")
        close(get("author_EY_percent"),
              100 * get("cup_advective_solute_g") / get("conditional_author_denominator_g"),
              "author denominator", 1e-10)
        if any(row[k] for k in ("actual_dry_dose_g", "physical_EY_percent", "water_mass_g",
                                "beverage_mass_g")):
            raise ValueError("unobserved physical quantity must remain blank")
        replay = row["case"].replace("_sparse", "_replay")
        close(1000 * get("cup_advective_solute_g"),
              number(key[(replay, get("t_hat"), "trap")], "cup_mg"), "replay cup join")
    census = rows(root, "review/gate_census.csv")
    categories = Counter(r["audit_primary_class"] for r in census if r["registered"])
    if categories != Counter(CF=15, TR=10, SS=8, SD=21, SC=11):
        raise ValueError("historical census transcription mismatch")
    deliveries = Counter(r["status"] for r in rows(root, "review/directory_census.csv"))
    if deliveries != Counter(READ=10, SOURCE_SCORE_RECOMPUTED=16):
        raise ValueError("historical delivery coverage mismatch")
    for target in json.loads((root / "balance/reporting_target_checks.json").read_text()):
        t = target["t_hat"]
        resolved = key[("tight_early", t, "simpson")]
        close(target["remainder_mg"], number(resolved, "remainder_mg"), "target remainder join")
        if abs(target["remainder_mg"]) >= .01 or target["max_coarse_vs_simpson_term_difference_mg"] >= .01:
            raise ValueError("supplied reporting target not met")
    return counts


def check(root):
    return {"scope": "supplied aggregates and identities only; no trajectories, model execution or physics validation",
            "hashed_files": integrity(root), "arithmetic_rows": arithmetic(root)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    print(json.dumps(check(args.root.resolve()), indent=2))

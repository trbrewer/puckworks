"""Frozen Roman-Corrochano comparison of Wadsworth plus a declared input adapter.

Research only; target-exposed retrospective comparison. No parameter estimation.
The native law and its defaults are imported unchanged. See the frozen protocol.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from decimal import Decimal
import hashlib
import json
import math
from pathlib import Path

from puckworks import data
from puckworks.models.wadsworth2026.permeability import ALPHA, B_PERC, k_percolation

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "docs/analysis/sci_val_tamped_k_001"
INPUT = ROOT / "puckworks/data/romancorrochano2015/sci_val_tamped_k_001_inputs.json"
TARGET = ROOT / "puckworks/data/romancorrochano2015/table2.csv"
KEYS = tuple((g, rho) for g in "ABCD" for rho in (360, 400, 480))
QUALIFIED = "QUALIFIED_DECLARED_ADAPTER_INPUT"


def positive(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("finite positive number required")
    if not math.isfinite(value) or value <= 0:
        raise ValueError("finite positive number required")
    return float(value)


def porosity(value):
    value = positive(value)
    if value >= 1:
        raise ValueError("porosity must be strictly between zero and one")
    return value


def interval(values, validator=positive):
    if len(values) != 3:
        raise ValueError("interval requires low, central, high")
    low, central, high = map(validator, values)
    if not low <= central <= high:
        raise ValueError("unordered interval or central value outside bounds")
    return low, central, high


def complete(rows, key):
    indexed = {}
    for row in rows:
        k = key(row)
        if k not in KEYS or k in indexed:
            raise ValueError(f"duplicate or unknown case key: {k}")
        indexed[k] = row
    if set(indexed) != set(KEYS):
        raise ValueError("missing cases: original denominator is twelve")
    return [indexed[k] for k in KEYS]


def radius_from_um(diameter_um):
    return positive(diameter_um) * 1e-6 / 2


@dataclass(frozen=True)
class CaseInput:
    grind: str
    bulk_density_kgm3: int
    radius_m: tuple[float, float, float]
    consolidated_porosity: tuple[float, float, float]
    initial_porosity: tuple[float, float, float]
    qualification: str = QUALIFIED

    def __post_init__(self):
        interval(self.radius_m)
        interval(self.consolidated_porosity, porosity)
        interval(self.initial_porosity, porosity)
        if self.qualification != QUALIFIED:
            raise ValueError("unsupported or missing case qualification")


def load_inputs(path=INPUT):
    """Load only structural inputs. No target loading or permeability argument."""
    raw = json.loads(Path(path).read_text())
    if (raw["schema_version"] != 1 or raw["original_denominator"] != 12
            or raw["scope"] != "DECLARED_ADAPTER_COMPARISON"
            or raw["units"] != {"d32_um": "um", "bulk_density_kgm3": "kg/m3", "epsilon_ss": "1"}):
        raise ValueError("unsupported input contract or units")
    shared = raw["initial_packing"]
    rho_s = positive(shared["solid_density_kgm3"])
    rho_half = positive(shared["solid_density_rounding_half_kgm3"])
    eps_p = porosity(shared["particle_porosity"])
    eps_half = positive(shared["particle_porosity_rounding_half"])
    particle_rhos = [positive(rs) * (1-porosity(ep))
                    for rs in (rho_s-rho_half, rho_s+rho_half)
                    for ep in (eps_p-eps_half, eps_p+eps_half)]
    cases = []
    for row in raw["cases"]:
        if any(k in row for k in ("permeability_m2", "observed", "target", "k_m2")):
            raise ValueError("targets forbidden in structural inputs")
        rho = positive(row["bulk_density_kgm3"])
        d = positive(row["d32_um"])
        half = positive(row["d32_rounding_half_um"])
        initial = (1-rho/min(particle_rhos), 1-rho/(rho_s*(1-eps_p)),
                   1-rho/max(particle_rhos))
        cases.append(CaseInput(row["grind"], row["bulk_density_kgm3"],
                     tuple(radius_from_um(v) for v in (d-half, d, d+half)),
                     (row["epsilon_ss_low"], row["epsilon_ss"], row["epsilon_ss_high"]),
                     initial, row["qualification"]))
    return complete(cases, lambda c: (c.grind, c.bulk_density_kgm3))


def bounded_prediction(radius_m, phi):
    """Exact closed-form extrema over a rectangular input interval, in SI."""
    rlo, rc, rhi = interval(radius_m)
    plo, pc, phi = interval(phi, porosity)
    radii = [rlo, rhi]
    stationary = 1/ALPHA
    if rlo <= stationary <= rhi:
        radii.append(stationary)
    values = [positive(float(k_percolation(r, p))) for r in radii for p in (plo, phi)]
    return {"low": min(values), "central": positive(float(k_percolation(rc, pc))),
            "high": max(values)}


def predict(cases):
    """Structural inputs -> both frozen arms. Observed permeability is not an input."""
    cases = complete(cases, lambda c: (c.grind, c.bulk_density_kgm3))
    result = []
    for c in cases:
        # Revalidate even if a caller has bypassed the frozen dataclass constructor.
        c.__post_init__()
        result.append({"grind": c.grind, "bulk_density_kgm3": c.bulk_density_kgm3,
                       "qualification": c.qualification,
                       "flags": ["SAUTER_RADIUS_PROXY", "BULK_POROSITY_PROXY",
                                 "READING_BOUNDS_ONLY", "SHARED_INPUT_DEPENDENCE"],
                       "radius_m": list(c.radius_m),
                       "consolidated_porosity": list(c.consolidated_porosity),
                       "initial_porosity": list(c.initial_porosity),
                       "consolidated": bounded_prediction(c.radius_m, c.consolidated_porosity),
                       "initial": bounded_prediction(c.radius_m, c.initial_porosity)})
    return {"task": "SCI-VAL-TAMPED-K-001", "original_denominator": 12,
            "scope": "DECLARED_ADAPTER_COMPARISON", "alpha_per_m": ALPHA,
            "exponent": B_PERC, "units": "SI", "cases": result}


def canonical_bytes(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+"\n").encode()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_targets():
    """Reuse the canonical target loader; recover printed precision from its CSV."""
    rows = complete(data.romancorrochano2015_table2(),
                    lambda r: (r["grind"], r["bulk_density_kgm3"]))
    with TARGET.open(newline="") as stream:
        tokens = complete(csv.DictReader(stream),
                          lambda r: (r["grind"], int(r["bulk_density_kgm3"])))
    targets = []
    for row, token in zip(rows, tokens):
        mean = positive(row["permeability_m2"])
        printed = Decimal(token["permeability_m2"])
        half = Decimal(5).scaleb(printed.as_tuple().exponent-1)
        targets.append({"grind": row["grind"], "bulk_density_kgm3": row["bulk_density_kgm3"],
                        "mean": mean, "sd": positive(row["permeability_sd_m2"]),
                        "low": positive(float(printed-half)),
                        "high": positive(float(printed+half))})
    return targets


def classify(q_low, q_high):
    q_low, q_high = positive(q_low), positive(q_high)
    if q_low > q_high:
        raise ValueError("unordered ratio interval")
    if q_low >= .5 and q_high <= 2:
        return "PASS"
    if q_high < .5 or q_low > 2:
        return "FAIL"
    return "UNRESOLVED_AT_DECLARED_INPUT_PRECISION"


def summaries(rows, arm):
    logs = [r[arm]["signed_log_ratio"] for r in rows]
    return {"n": len(rows), "geometric_mean_ratio": math.exp(sum(logs)/len(logs)),
            "geometric_rms_error_factor": math.exp(math.sqrt(sum(x*x for x in logs)/len(logs))),
            "maximum_multiplicative_error": math.exp(max(abs(x) for x in logs))}


def score(bundle, targets):
    """Join an immutable prediction bundle to targets; also usable with synthetic fixtures."""
    if bundle["original_denominator"] != 12:
        raise ValueError("original denominator changed")
    predictions = complete(bundle["cases"], lambda r: (r["grind"], r["bulk_density_kgm3"]))
    targets = complete(targets, lambda r: (r["grind"], r["bulk_density_kgm3"]))
    rows = []
    for prediction, target in zip(predictions, targets):
        klo, kc, khi = interval((target["low"], target["mean"], target["high"]))
        sd = positive(target["sd"])
        if prediction["qualification"] != QUALIFIED:
            raise ValueError("unsupported case must not be scored")
        row = {k: prediction[k] for k in ("grind", "bulk_density_kgm3", "qualification", "flags")}
        row["observed"] = {"mean_m2": kc, "sd_m2": sd, "rounding_low_m2": klo, "rounding_high_m2": khi}
        for arm in ("consolidated", "initial"):
            p = prediction[arm]
            lo, central, hi = interval((p["low"], p["central"], p["high"]))
            qlo, qc, qhi = lo/khi, central/kc, hi/klo
            row[arm] = {"prediction_m2": central, "prediction_low_m2": lo,
                        "prediction_high_m2": hi, "ratio": qc, "q_low": qlo,
                        "q_high": qhi, "signed_log_ratio": math.log(qc),
                        "classification": classify(qlo, qhi)}
        row["consolidated_over_initial_prediction"] = (
            row["consolidated"]["prediction_m2"]/row["initial"]["prediction_m2"])
        rows.append(row)
    states = [r["consolidated"]["classification"] for r in rows]
    disposition = ("CONSOLIDATED_INPUT_PRIOR_FAILS_DECLARED_SCREEN" if "FAIL" in states else
                   "CONSOLIDATED_INPUT_PRIOR_PASSES_DECLARED_SCREEN" if all(s == "PASS" for s in states) else
                   "UNRESOLVED_AT_DECLARED_INPUT_PRECISION")
    summary = {arm: summaries(rows, arm) for arm in ("consolidated", "initial")}
    per_grind = {g: {arm: summaries([r for r in rows if r["grind"] == g], arm)
                     for arm in summary} for g in "ABCD"}
    result = {"task": bundle["task"], "scientific_adequacy": disposition,
              "scope": "DECLARED_ADAPTER_COMPARISON", "exposure": "TARGET_EXPOSED_RETROSPECTIVE_COMPARISON",
              "coverage": {"intended": 12, "qualified": 12, "scored": 12},
              "criterion": {"new_engineering_screen": True, "ratio_low": .5, "ratio_high": 2., "all_cases_required": 12},
              "counts": {s: states.count(s) for s in ("PASS", "FAIL", "UNRESOLVED_AT_DECLARED_INPUT_PRECISION")},
              "summary": summary, "per_grind": per_grind, "cases": rows,
              "consolidated_over_initial_geometric_mean": math.exp(sum(math.log(r["consolidated_over_initial_prediction"]) for r in rows)/12),
              "physical_validation": "NOT_ESTABLISHED", "successor": "NONE_AUTHORIZED"}
    canonical_bytes(result)  # Reject non-finite output before returning any result.
    return result


def render_report(result):
    """Render retained results only. Does not load inputs/targets or recompute a score."""
    canonical_bytes(result)
    lines = ["# SCI-VAL-TAMPED-K-001 result", "", f"**{result['scientific_adequacy']}**", "",
             "Tested object: unchanged Wadsworth law plus the frozen Sauter-radius / bulk-porosity adapter.",
             "TARGET_EXPOSED_RETROSPECTIVE_COMPARISON; G1; NO_GOVERNING_PHYSICS_CHANGE.", "",
             "Coverage: 12 intended, 12 qualified, 12 scored triplicate summaries from one campaign.",
             "The new permissive mean-level screen requires all twelve ratio intervals within [0.5, 2.0].",
             "Reading/rounding intervals and reported SDs are not confidence intervals.", "",
             f"Case counts: {result['counts']}.", "",
             "| Case | K mean ± SD (m²) | Primary K [reading bounds] (m²) | Ratio [bounds] | ln ratio | Decision |",
             "|---|---|---|---|---|---|"]
    for r in result["cases"]:
        p, o = r["consolidated"], r["observed"]
        lines.append(f"| {r['grind']}-{r['bulk_density_kgm3']} | {o['mean_m2']:.4g} ± {o['sd_m2']:.3g} | "
                     f"{p['prediction_m2']:.5g} [{p['prediction_low_m2']:.5g}, {p['prediction_high_m2']:.5g}] | "
                     f"{p['ratio']:.4f} [{p['q_low']:.4f}, {p['q_high']:.4f}] | {p['signed_log_ratio']:.5f} | {p['classification']} |")
    lines += ["", "Every case is QUALIFIED_DECLARED_ADAPTER_INPUT, with SAUTER_RADIUS_PROXY, BULK_POROSITY_PROXY,",
              "READING_BOUNDS_ONLY and SHARED_INPUT_DEPENDENCE flags. Machine-readable result.json retains both arms,",
              "all per-case bounds and descriptive target SDs.", "",
              "| Arm | Geometric mean ratio | Geometric RMS error factor | Maximum multiplicative error |",
              "|---|---:|---:|---:|"]
    for arm, s in result["summary"].items():
        lines.append(f"| {arm} | {s['geometric_mean_ratio']:.5f} | {s['geometric_rms_error_factor']:.5f} | {s['maximum_multiplicative_error']:.5f} |")
    lines += ["", "| Grind | Primary GM ratio | Primary RMS factor | Primary maximum factor | Initial GM ratio |",
              "|---|---:|---:|---:|---:|"]
    for g, arms in result["per_grind"].items():
        c, i = arms["consolidated"], arms["initial"]
        lines.append(f"| {g} | {c['geometric_mean_ratio']:.5f} | {c['geometric_rms_error_factor']:.5f} | {c['maximum_multiplicative_error']:.5f} | {i['geometric_mean_ratio']:.5f} |")
    lines += ["", f"Consolidated/initial prediction geometric mean: {result['consolidated_over_initial_geometric_mean']:.6f}.",
              "Per-case porosity-substitution effects are retained in result.json; the initial arm is diagnostic only.", ""]
    if result["scientific_adequacy"].endswith("FAILS_DECLARED_SCREEN"):
        lines += ["Reject all-case adequacy of this fixed composite predictor for the tested offline source domain.",
                  "Do not fit a correction in this task; failure does not isolate the native law from its adapter."]
    elif result["scientific_adequacy"].endswith("PASSES_DECLARED_SCREEN"):
        lines += ["Retain only the tested coarse offline source-domain qualification; no production adoption follows."]
    else:
        lines += ["Reading/rounding precision straddles the fixed threshold; retain the named ambiguous cases.",
                  "Finer source readings resolving those ratio intervals are the minimum evidence needed for this screen."]
    lines += ["", "EWP consumer consequence: no compatible production permeability transfer is established; EWP is unchanged.",
              "No fresh-shot hydraulics, H1, equilibrium, extraction kinetics or EWP validation is established.",
              "No structural mechanism is identified, clean-screen question reopened, or successor authorized.", "",
              "BASELINE.json records clean source/software baselines. GATES.json records novelty/source decisions.",
              "FREEZE.json and PRE_SCORE_REVIEW.json bind the approved scientific artifacts; CLOSEOUT.json separates",
              "affected tests, independent review and local-only publication status. No push, PR, merge or auto-merge.", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("predict", "score", "report"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--input", type=Path)
    args = parser.parse_args()
    if args.action == "predict":
        content = canonical_bytes(predict(load_inputs(args.input or INPUT)))
    elif args.action == "score":
        freeze_path = DOC / "FREEZE.json"
        review = json.loads((DOC / "PRE_SCORE_REVIEW.json").read_text())
        if (review["status"] != "APPROVED" or review["independent"] is not True
                or review["freeze_sha256"] != file_hash(freeze_path)):
            raise ValueError("independent exact-freeze approval required")
        freeze = json.loads(freeze_path.read_text())
        for name, expected in freeze["files"].items():
            if file_hash(ROOT/name) != expected:
                raise ValueError(f"frozen artifact changed: {name}")
        predictions = DOC / "predictions.json"
        if args.input is not None and args.input.resolve() != predictions.resolve():
            raise ValueError("only the frozen prediction bundle is authorized")
        if args.output.exists():
            raise FileExistsError("retained score must never be overwritten")
        result = score(json.loads(predictions.read_text()), load_targets())
        result["freeze_sha256"] = file_hash(freeze_path)
        result["review_sha256"] = file_hash(DOC/"PRE_SCORE_REVIEW.json")
        content = canonical_bytes(result)
    else:
        if args.input is None:
            parser.error("report requires --input retained-result.json")
        content = render_report(json.loads(args.input.read_text())).encode()
    # Exclusive creation for predictions and scores; report regeneration is reversible.
    with args.output.open("wb" if args.action == "report" else "xb") as stream:
        stream.write(content)


if __name__ == "__main__":
    main()

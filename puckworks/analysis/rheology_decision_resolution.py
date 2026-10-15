"""Read-only, retained-aggregate RHEOLOGY-010 decision addendum; no native scoring.

The frozen case specification and manifest live in docs/analysis/
val_case_rheology_decision_resolution_001. Historical decisions are case-local;
the accepted policy helper supplies separate sensitivity/claim diagnostics.
"""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal, ROUND_FLOOR, localcontext
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
from typing import Any, cast

from puckworks.validation import decision_resolution as policy

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "docs/analysis/val_case_rheology_decision_resolution_001"
SOURCE = "docs/analysis/sci_md_rheology_010/"
LAWS = ("SW_WATER_ANCHORED_90C", "TR_LINEAR")
METRICS = ("E_Qint", "E_Qpeak", "D_share_mean_pp", "D_share_peak_pp", "E_Spath", "D_TDS_pp")
BUDGETS = dict(zip(METRICS, (0.01, 0.02, 1.0, 2.0, 0.01, 0.1)))
ENDPOINTS = {"UP": "0.015983191", "DOWN": "0.016114389"}
UNKNOWN = ("measurement", "training", "source_model", "parameters", "untested_discretization_continuum")
LIMITS = (
    "Empirical numerical sensitivity only; no certified bound, confidence interval or population interval.",
    "C is a source-conditioned computational reference, not measured physical truth.",
    "No total physical uncertainty, whole-shot fidelity beyond support, arbitrary transfer or production eligibility.",
    "Engineering budgets are not experimentally established taste or consumer tolerances.",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON identity: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    def invalid(value: str) -> None:
        raise ValueError(f"nonfinite JSON number: {value}")
    return json.loads(path.read_text(), object_pairs_hook=_unique, parse_constant=invalid)


def dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"


def pointer(value: Any, locator: str) -> Any:
    for key in locator.split("/")[1:]:
        value = value[key.replace("~1", "/").replace("~0", "~")]
    return value


def expected_ids() -> tuple[str, ...]:
    return tuple(f"{group}/{law}_{history}/{metric}"
                 for group in ("primary", "secondary") for law in LAWS
                 for history in ("DOWN", "UP")
                 for metric in (METRICS if group == "primary" else METRICS[-2:]))


def historical_sum(values: list[float]) -> float:
    """CPython 3.12.3 float sum, explicit for identical results on 3.10–3.13.

    Its Neumaier compensation is part of historical arithmetic, not padding.
    Inputs here are finite nonnegative floats, in original insertion order.
    """
    total, correction = 0.0, 0.0
    for value in values:
        updated = total + value
        correction += ((total - updated) + value if abs(total) >= abs(value)
                       else (value - updated) + total)
        total = updated
    return total + correction if correction and math.isfinite(correction) else total


def finite_nonnegative(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value) and value >= 0


def scalar(question: str, M: Any, u: Any, b: Any, *, complete: bool = True) -> dict[str, Any]:
    """Historical strict two-sided contract, independent of generic comparator."""
    if question not in ("primary", "secondary"):
        raise ValueError("unknown question")
    valid = (complete is True and all(finite_nonnegative(v) for v in (M, u, b))
             and b > 0 and math.isfinite(M + u))
    if not valid:
        return dict(historical_decision="UNRESOLVED", precision_eligible=False,
                    precision_state="UNAVAILABLE", envelope_relation="UNAVAILABLE",
                    L=None, U=None, precision_ceiling=None, precision_headroom=None,
                    below_budget_headroom=None, above_budget_headroom=None)
    lower, upper, ceiling = M - u, M + u, 0.20 * b
    eligible = u <= ceiling
    relation = ("ENTIRELY_BELOW" if upper < b else "ENTIRELY_ABOVE" if lower > b
                else "OVERLAPPING_OR_TOUCHING")
    decision = "UNRESOLVED"
    if eligible and relation == "ENTIRELY_BELOW":
        decision = "PASS" if question == "primary" else "BELOW_DECLARED_MATERIALITY_BUDGET"
    if eligible and relation == "ENTIRELY_ABOVE":
        decision = "FAIL" if question == "primary" else "MATERIAL_MODELED_DELIVERY_CONTRAST"
    return dict(historical_decision=decision, precision_eligible=eligible,
                precision_state="MET" if eligible else "NOT_MET",
                envelope_relation=relation, L=lower, U=upper,
                precision_ceiling=ceiling, precision_headroom=ceiling - u,
                below_budget_headroom=b - upper, above_budget_headroom=lower - b)


def primary_aggregate(flags: list[str]) -> str:
    suffix = ("INSUFFICIENT" if "FAIL" in flags else "SUFFICIENT_FOR_TESTED_OUTPUTS"
              if len(flags) == 24 and all(f == "PASS" for f in flags) else "UNRESOLVED")
    return "E2_CONDUCTANCE_MATCHED_REVERSAL_" + suffix


def term_order(question: str) -> tuple[str, ...]:
    return ("time", "axial", "Cradial" if question == "primary" else "both_C_radial",
            "property", "arithmetic")


def check_terms(question: str, terms: Any, total: Any) -> list[str]:
    names = term_order(question)
    if not isinstance(terms, dict) or set(terms) != set(names):
        return ["missing/incompatible allowance components"]
    if not all(finite_nonnegative(v) for v in terms.values()):
        return ["invalid allowance component"]
    if historical_sum([float(terms[n]) for n in names]) != total:
        return ["retained total differs from historical ordered component sum"]
    return []


def helper_diagnostic(spec: dict[str, Any], result: dict[str, Any], M: float, b: float) -> dict[str, Any]:
    support = "0–30 s, every native interval" if spec["metric"] not in METRICS[-2:] else (
        "0 to B_star=" + ENDPOINTS[spec["history"]] + " kg, zero/first increment included")
    scope = policy.Scope(spec["metric"], spec["units"], support,
                         spec["comparison"] + " retained magnitude", "original frozen metric",
                         "retained aggregate variants and independent arithmetic discrepancies",
                         ((spec["id"], "source-conditioned computational configuration"),),
                         "complete compatible retained aggregate evidence",
                         (("terminal_tail", "deliberately unscored"),)
                         if spec["metric"] in METRICS[-2:] else ())
    requirement = policy.Requirement(
        identity=spec["id"] + "/bound_diagnostic", controlling=False, role="precision",
        scope=scope, operator="<" if spec["group"] == "primary" else ">", threshold=b,
        purpose="Separate mathematical relation from bound resolution; not historical contract",
        threshold_basis="Original declared engineering budget; no experimental practical validation",
        approval="approved", decision_basis="applicable_bound",
        resolution_components=("numerical_continuum",), claim_limits=LIMITS)
    basis = policy.Basis("sensitivity", scope, "Retained additive empirical numerical allowance",
                         ("tested_numerical_sensitivities",),
                         ("Restricted to retained configurations/refinements/support",),
                         term_order(spec["group"]))
    evidence = policy.Evidence(
        "sensitivity", scope, basis, scope.members,
        policy.Quality(True, True, True, True,
                       "Pinned aggregate payload/compatibility checks only; no native re-verification"),
        UNKNOWN, point=M, interval=policy.Interval(result["L"], result["U"]))
    diagnostic = policy.evaluate(requirement, evidence)
    return dict(operator=requirement.operator, decision_basis=requirement.decision_basis,
                evidence_kind=evidence.kind, basis_kind=basis.kind,
                point_relation=diagnostic.point_relation, range_relation=diagnostic.range_relation,
                contractual=diagnostic.contractual, bound_resolution=diagnostic.resolution,
                support_complete=diagnostic.support_complete,
                assessment_complete=diagnostic.assessment_complete,
                reliance_blocked=diagnostic.reliance_blocked,
                interpretation=diagnostic.interpretation, limitations=list(diagnostic.limitations),
                required_bound_components=list(requirement.resolution_components),
                covered_components=list(basis.components), unknown_components=list(UNKNOWN))


def coverage_for(spec: dict[str, Any], coverage: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    rows, errors = {}, []
    delivery = spec["metric"] in METRICS[-2:]
    end = float(ENDPOINTS[spec["history"]])
    for locator in spec["coverage_pointers"]:
        row = coverage.get(locator[1:])
        rows[locator[1:]] = row
        if row is None:
            if delivery:
                errors.append("missing delivery coverage: " + locator)
            continue
        terminal = row.get("terminal_beverage_kg")
        ratio = row.get("scored_fraction_of_terminal")
        if delivery and not (finite_nonnegative(terminal) and terminal > 0
                             and row.get("B_star_kg") == end
                             and row.get("reaches_support") is True and terminal >= end
                             and finite_nonnegative(ratio) and ratio == end / terminal):
            errors.append("invalid/incompatible delivery support: " + locator)
    return rows, errors


def evaluate_row(spec: dict[str, Any], data: dict[str, Any], coverage: dict[str, Any],
                 support_errors: list[str]) -> dict[str, Any]:
    group, case, metric = spec["id"].split("/")
    block = data.get(group, {}).get(case, {})
    original = block.get("decisions", {}).get(metric)
    errors: list[str] = []
    imported = original if isinstance(original, dict) else {}
    M, u, b = (imported.get(k) for k in ("value", "u_total", "budget"))
    terms = imported.get("terms", {})
    if original is None:
        errors.append("missing required decision")
    if imported.get("evidence_complete") is not True:
        errors.append("original evidence incomplete")
    if imported.get("units") != spec["units"] or b != BUDGETS[metric]:
        errors.append("incompatible units or historical budget")
    if not all(finite_nonnegative(v) for v in (M, u, b)):
        errors.append("missing/nonfinite/negative scalar")
    errors.extend(check_terms(group, terms, u))
    variants, arithmetic = {}, {}
    for name, locator in spec["variant_pointers"].items():
        try:
            variants[name] = pointer(data, locator)
            arithmetic[name] = pointer(data, spec["arithmetic_pointers"][name])
        except (KeyError, TypeError):
            errors.append("missing refinement/arithmetic: " + name)
    reconstructed = {}
    if (set(variants) != set(spec["variant_pointers"])
        or set(arithmetic) != set(spec["arithmetic_pointers"])
        or not all(finite_nonnegative(v) for v in [*variants.values(), *arithmetic.values()])):
        errors.append("incomplete/nonfinite/negative refinement evidence")
    elif finite_nonnegative(M):
        if variants["base"] != M:
            errors.append("retained M differs from base variant")
        for term, variant in zip(term_order(group)[:3], ("temporal", "axial", "radial")):
            reconstructed[term] = abs(variants[variant] - M)
        reconstructed["property"] = abs(variants["property"] - M) if "property" in variants else 0.0
        reconstructed["arithmetic"] = max(arithmetic.values())
        if reconstructed != terms:
            errors.append("retained allowance components differ from refinement construction")
    rows, row_errors = coverage_for(spec, coverage)
    errors.extend(row_errors)
    if metric in METRICS[-2:]:
        errors.extend(support_errors)
        for variant in spec["variant_pointers"]:
            if block.get("variants", {}).get(variant, {}).get("delivery_status") != "VALID":
                errors.append("missing/invalid delivery variant: " + variant)
    result = scalar(group, M, u, b, complete=not errors)
    reproduced = result.pop("historical_decision")
    original_label = imported.get("decision")
    return dict(id=spec["id"], group=group, law=spec["law"], history=spec["history"], metric=metric,
                units=spec["units"], comparison=spec["comparison"],
                historical_decision=original_label, reproduced_historical_decision=reproduced,
                decision_discrepancy=original_label != reproduced,
                original_evidence_complete=imported.get("evidence_complete"),
                aggregate_evidence_valid=not errors, issues=errors,
                retained=dict(M=M, u=u, b=b, terms=terms),
                reconstructed_terms=reconstructed,
                reconstructed_total=historical_sum([reconstructed[n] for n in term_order(group)])
                if reconstructed else None,
                variants=variants, arithmetic_discrepancies=arithmetic,
                refinement_construction=dict(
                    time="paired temporal", axial="paired axial",
                    radial="C refined; E2 fixed at base" if group == "primary" else "BOTH C configurations refined",
                    property="paired SW property" if spec["law"].startswith("SW") else "zero for TR",
                    arithmetic="maximum retained 50-digit discrepancy; not recomputed from native traces",
                    sum_order=list(term_order(group))),
                support=dict(B_star_kg=ENDPOINTS[spec["history"]],
                             scored_domain="0 to B_star" if metric in METRICS[-2:] else "all native 0–30 s intervals",
                             coverage=rows, terminal_tails="deliberately unscored for delivery"),
                source_locators=spec,
                helper=helper_diagnostic(spec, result, cast(float, M), cast(float, b)) if not errors else None,
                claim_limits=list(LIMITS), unknown_uncertainty_components=list(UNKNOWN),
                primary_satisfaction_headroom=result["below_budget_headroom"] if group == "primary" else None,
                primary_failure_headroom=result["above_budget_headroom"] if group == "primary" else None,
                secondary_above_budget_headroom=result["above_budget_headroom"] if group == "secondary" else None,
                secondary_below_budget_headroom=result["below_budget_headroom"] if group == "secondary" else None,
                **result)


def evaluate_population(manifest: dict[str, Any], data: dict[str, Any], coverage: dict[str, Any],
                        support_errors: list[str]) -> dict[str, Any]:
    specs = manifest["population"]
    ids = [s["id"] for s in specs]
    if len(ids) != 32 or len(set(ids)) != 32 or set(ids) != set(expected_ids()):
        raise ValueError("manifest must enumerate all 24+8 unique decisions")
    observed = {f"{g}/{c}/{m}" for g in ("primary", "secondary")
                for c, block in data.get(g, {}).items() for m in block.get("decisions", {})}
    if observed - set(ids):
        raise ValueError("undeclared extra decisions: " + str(sorted(observed - set(ids))))
    rows = [evaluate_row(s, data, coverage, support_errors) for s in sorted(specs, key=lambda s: s["id"])]
    summary = {}
    for group in ("primary", "secondary"):
        selected = [r for r in rows if r["group"] == group]
        summary[group] = dict(
            count=len(selected), original=dict(Counter(r["historical_decision"] or "MISSING" for r in selected)),
            reproduced=dict(Counter(r["reproduced_historical_decision"] for r in selected)),
            precision=dict(Counter(r["precision_state"] for r in selected)),
            envelope=dict(Counter(r["envelope_relation"] for r in selected)),
            complete_valid=sum(r["aggregate_evidence_valid"] for r in selected))
    aggregate = primary_aggregate([r["reproduced_historical_decision"] for r in rows if r["group"] == "primary"])
    return dict(cases=rows, summary=summary,
                missing_decisions=sorted(set(ids) - observed),
                discrepancies=[r["id"] for r in rows if r["decision_discrepancy"]],
                original_primary_aggregate=data.get("disposition"), reproduced_primary_aggregate=aggregate,
                primary_aggregate_discrepancy=data.get("disposition") != aggregate)


def verify_support(support: dict[str, Any], coverage: dict[str, Any]) -> list[str]:
    errors = []
    expected_c = {f"{config}_C_{law}_{h}_{v}" for config in ("old", "new") for law in LAWS
                  for h in ("DOWN", "UP") for v in ("base", "temporal", "axial", "radial")
                  + (("property",) if law.startswith("SW") else ())}
    terminals = support.get("C_terminals_kg", {})
    if set(terminals) != expected_c or not all(finite_nonnegative(v) and v > 0 for v in terminals.values()):
        return ["incomplete/invalid 36-C reference support"]
    with localcontext() as ctx:
        ctx.prec = 28  # historical Decimal default, not a new numerical allowance
        for history in ("DOWN", "UP"):
            values = [Decimal(str(v)) for k, v in terminals.items() if f"_{history}_" in k]
            end = str((Decimal(".95") * min(values)).quantize(Decimal("1e-9"), rounding=ROUND_FLOOR))
            if support.get("B_star_kg", {}).get(history) != ENDPOINTS[history] or end != ENDPOINTS[history]:
                errors.append("support endpoint mismatch: " + history)
    for name, terminal in terminals.items():
        if coverage.get(name, {}).get("terminal_beverage_kg") != terminal:
            errors.append("reference terminal mismatch: " + name)
    return errors


def read_inputs(evidence: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Authenticate local repository snapshots without network or source writes."""
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    revision = subprocess.check_output(["git", "-C", str(evidence), "rev-parse", "HEAD"],
                                       text=True, env=env).strip()
    if revision != manifest["evidence"]["commit"]:
        raise ValueError("EWP checkout revision differs from frozen evidence commit")
    for kind, root in (("evidence", evidence), ("policy", ROOT)):
        for source in manifest[kind]["files"]:
            if sha256(root / source["path"]) != source["sha256"]:
                raise ValueError("frozen file hash mismatch: " + source["path"])
    return {name: load_json(evidence / SOURCE / (name + ".json")) for name in
            ("METRICS", "COVERAGE", "SUPPORT", "SUPPORT_RECEIPT", "QUALIFICATION", "REFERENCE_QUALIFICATION")}


def evaluate_checkout(evidence: Path) -> dict[str, Any]:
    manifest = load_json(BUNDLE / "INPUT_MANIFEST.json")
    inputs = read_inputs(evidence, manifest)
    support_errors = verify_support(inputs["SUPPORT"], inputs["COVERAGE"])
    if inputs["SUPPORT_RECEIPT"]["sha256"] != sha256(evidence / SOURCE / "SUPPORT.json"):
        support_errors.append("support receipt mismatch")
    qualification = inputs["QUALIFICATION"]
    reference = inputs["REFERENCE_QUALIFICATION"]
    expected_native = {p[1:] for s in manifest["population"] for p in s["coverage_pointers"]}
    if (set(inputs["COVERAGE"]) != expected_native
        or set(reference) != {n for n in expected_native if "_C_" in n}
        or {"new_" + n for n in qualification} != {n for n in expected_native if "_E2_" in n}):
        raise ValueError("native qualification/coverage identity set differs from frozen population")
    result = evaluate_population(manifest, inputs["METRICS"], inputs["COVERAGE"], support_errors)
    result.update(
                  SCIENTIFIC_RESULT_DISPOSITION={
                      "historical_primary": result["reproduced_primary_aggregate"],
                      "primary_and_secondary": result["summary"],
                      "interpretation": "Historical contracts preserved; empirical envelope relations reported separately"},
                  VALIDATION_FRAMEWORK_DISPOSITION="Case-local aggregate evaluation; tests/reviews/CI are separate evidence in HANDOFF.md",
                  CLAIM_CEILING="Retained numerical sensitivity on declared support only; physical validation not established",
                  task=manifest["task"], classification=["G1", "NO_GOVERNING_PHYSICS_CHANGE",
                  "RESEARCH_ONLY", "RETROSPECTIVE", "TARGET_EXPOSED", "EXPLORATORY"],
                  source_identity=manifest["evidence"], policy_identity=manifest["policy"],
                  input_manifest_sha256=sha256(BUNDLE / "INPUT_MANIFEST.json"),
                  protocol_sha256=sha256(BUNDLE / "PROTOCOL.md"),
                  numerical_representation="binary64; CPython 3.12.3 ordered compensated sum; no tolerance",
                  verification_scope="retained aggregate arithmetic and decisions only; no native/50-digit campaign re-verification",
                  support_issues=support_errors,
                  coverage={k:dict(**v, unscored_terminal_tail_kg=v["terminal_beverage_kg"]-v["B_star_kg"])
                            for k, v in sorted(inputs["COVERAGE"].items())},
                  support_rule=inputs["SUPPORT"]["rule"],
                  controls=dict(PHYSICAL_VALIDATION="NOT_ESTABLISHED", MERGE_AUTHORIZED=False,
                                PRODUCTION_ADOPTION_AUTHORIZED=False, NEW_NATIVE_SIMULATIONS=0,
                                NATIVE_EWP_RUNS=0, NO_AUTOMATIC_SUCCESSOR=True))
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-checkout", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="new JSON file outside evidence checkout")
    args = parser.parse_args()
    evidence, output = args.evidence_checkout.resolve(), args.output.resolve()
    if output == evidence or evidence in output.parents:
        parser.error("output must be outside the read-only EWP checkout")
    if output.exists():
        parser.error("output must be new; compare it with committed RESULTS.json after evaluation")
    result = evaluate_checkout(evidence)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        handle.write(dumps(result))


if __name__ == "__main__":
    main()

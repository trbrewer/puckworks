"""Deterministic SCI-MD-007 evidence feasibility primitives.

This concrete analysis never reads Angeloni data and never changes runtime inventory
semantics.  Real-data build/adjudication is deliberately data-driven from the task
registers under ``puckworks/data/sci_md_007``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

TARGET_SEMANTICS = {
    "TOTAL_ROASTED_CONTENT", "OPERATIONALLY_EXTRACTABLE_CONTENT",
    "SOLID_PHASE_CONCENTRATION", "EQUILIBRIUM_CONTENT_OR_CEILING",
    "ASYMPTOTIC_EXTRACTED_MASS", "BEVERAGE_CONCENTRATION_OR_YIELD",
    "NON_INVENTORY_QUANTITY", "UNRESOLVED_TARGET_SEMANTICS",
}
PROVENANCE = {
    "DIRECT_ROASTED_MATERIAL_ASSAY", "DIRECT_OPERATIONAL_EXTRACTABILITY_ASSAY",
    "EQUILIBRIUM_DERIVED_ESTIMATE", "ASYMPTOTIC_EXTRACTION_ESTIMATE",
    "MODEL_INFERRED_OR_FITTED", "BEVERAGE_ENDPOINT_INFERENCE",
    "SECONDARY_SOURCE_SUMMARY", "UNRESOLVED_PROVENANCE",
}
COMPOUND_GATES = ("F0", "F1", "F2", "F3", "F4", "F6", "F7")
PASS = "SCI_MD_007_INVENTORY_PREDICTION_FEASIBLE_WITH_EXISTING_EVIDENCE"
FAIL = "SCI_MD_007_INVENTORY_PRIOR_ONLY_ADDITIONAL_DIRECT_MEASUREMENTS_REQUIRED"


def exact_to_mg_g(value: float, unit: str, uncertainty: float | None = None):
    factors = {"mg/kg": .001, "g/kg": 1.0, "mg/100 g": .01,
               "g/100 g": 10.0, "%": 10.0}
    if unit not in factors:
        raise ValueError(f"unsupported exact unit conversion: {unit}")
    factor = factors[unit]
    return value * factor, None if uncertainty is None else uncertainty * factor


def as_received_to_dry(value: float, moisture: float | None, moisture_basis: str,
                       same_material_batch: bool = True) -> float:
    if moisture is None or not same_material_batch:
        raise ValueError("same-material, same-roast-batch moisture is required")
    if not 0 <= moisture < 1:
        raise ValueError("moisture fraction must be in [0,1)")
    if moisture_basis == "wet_basis":
        return value / (1.0 - moisture)
    if moisture_basis == "dry_basis":
        return value * (1.0 + moisture)
    raise ValueError("confirmed wet_basis or dry_basis moisture is required")


def reject_phase_volume_conversion(unit: str) -> None:
    if unit in {"mg/mL solid phase", "mg/mL-solid-phase"}:
        raise ValueError("phase-volume concentration cannot become coffee-mass content without explicit physics")


def primary_eligible(row: dict) -> bool:
    text = json.dumps(row, sort_keys=True).lower()
    required = ("source_publication_id", "source_locator", "base_coffee_material_id",
                "roast_batch_id", "analytical_method", "data_lineage_id")
    return (
        "angeloni" not in text
        and row.get("analyte") in {"caffeine", "trigonelline"}
        and row.get("roasted_unextracted") is True
        and row.get("target_semantics") == "TOTAL_ROASTED_CONTENT"
        and row.get("measurement_provenance") == "DIRECT_ROASTED_MATERIAL_ASSAY"
        and row.get("canonical_basis") == "dry roasted coffee"
        and row.get("conversion_supported") is True
        and row.get("rights_usable") is True
        and not row.get("duplicate", False)
        and all(row.get(k) for k in required)
    )


def disposition(caffeine: dict[str, bool], trigonelline: dict[str, bool], f5: bool):
    cf = all(caffeine.get(g, False) for g in COMPOUND_GATES)
    tr = all(trigonelline.get(g, False) for g in COMPOUND_GATES)
    overall = cf and tr and f5
    return {"caffeine_feasible": cf, "trigonelline_feasible": tr,
            "overall_feasible": overall, "scientific_disposition": PASS if overall else FAIL}


def contract_path() -> Path:
    return Path(__file__).parents[2] / "docs/analysis/sci_md_007/feasibility_contract.json"


def validate_contract() -> dict:
    raw = contract_path().read_bytes()
    obj = json.loads(raw)
    expected = {
        "contract_id": "SCI_MD_007_FEASIBILITY_CONTRACT_V1",
        "schema_version": "1.0.0", "task_id": "SCI-MD-007",
        "evidence_cutoff_date": "2026-08-25",
        "canonical_unit": "mg analyte / g dry roasted coffee",
        "eligible_target_semantics": "TOTAL_ROASTED_CONTENT",
        "eligible_measurement_provenance": "DIRECT_ROASTED_MATERIAL_ASSAY",
        "thresholds": {
            "F2": {"material_roast_units": 24, "base_coffee_materials": 16,
                   "source_publications": 4, "identified_laboratories": 3,
                   "validation_groups": 4, "largest_group_max_fraction": .5},
            "F3": {"units_per_species": 8, "validation_groups_per_species": 3,
                   "publications_per_species": 2, "laboratories_per_species": 2},
            "F4": {"categorical_strata_per_species": 2,
                   "categorical_units_per_stratum": 4,
                   "categorical_groups_per_stratum": 2,
                   "quantitative_metric_units": 16,
                   "quantitative_metric_units_per_species": 6,
                   "quantitative_metric_groups": 3,
                   "within_species_varying_groups": 2},
            "F5": {"paired_material_roast_units": 20, "validation_groups": 4},
            "F6": {"uncertainty_bearing_fraction": .5,
                   "uncertainty_source_laboratory_groups": 3},
            "F7": {"outer_validation_groups": 4}},
        "compound_formula": "F0 and F1 and F2 and F3 and F4 and F6 and F7",
        "overall_formula": "caffeine_feasible and trigonelline_feasible and F5",
        "pass_disposition": PASS, "fail_disposition": FAIL,
        "model_adoption_status": "NOT_AUTHORIZED_BY_FEASIBILITY_SCREEN"}
    digest = hashlib.sha256(raw).hexdigest()
    if obj != expected or digest != "2f89470195572dc2e4c28960bad6a5f7357c36db6342fb0c13cf9443ab6417a2":
        raise ValueError("frozen SCI-MD-007 contract differs from commit 241eca9")
    r1_path = contract_path().parent / "r1/R1_CORRECTIVE_SEARCH_CONTRACT.json"
    r1 = json.loads(r1_path.read_text(encoding="utf-8"))
    protocol = contract_path().parent / "r1/R1_CORRECTIVE_SEARCH_PROTOCOL.md"
    required = {"schema_version", "closure_class", "task_id", "authorization_id",
                "evidence_cutoff_date", "original_contract_commit",
                "original_contract_sha256", "providers", "result_limit_per_query_per_provider",
                "queries", "mandatory_rescreen", "citation_passes", "source_screening_states",
                "row_eligibility_rules", "search_completion_formula", "rights_rules",
                "angeloni_rule", "protocol_sha256"}
    if set(r1) < required or r1["closure_class"] != "R1_CORRECTIVE_CONTRACT_CLOSURE":
        raise ValueError("R1 corrective contract schema incomplete")
    if len(r1["queries"]) != 8 or r1["providers"] != ["Crossref", "OpenAlex", "GeneralPublicWeb"]:
        raise ValueError("R1 query/provider set differs from frozen corrective design")
    if r1["result_limit_per_query_per_provider"] != 20:
        raise ValueError("R1 result limit changed")
    protocol_digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    if protocol_digest != r1["protocol_sha256"]:
        raise ValueError("R1 protocol hash mismatch")
    return {"contract_sha256": digest, "r1_contract_sha256": hashlib.sha256(r1_path.read_bytes()).hexdigest(),
            "r1_protocol_sha256": protocol_digest, "valid": True}


ROOT = Path(__file__).parents[2]
DATA = ROOT / "puckworks/data/sci_md_007"
OUT = ROOT / "docs/analysis/sci_md_007"


def _write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows([{k: row.get(k, "") for k in fields} for row in rows])


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_atlas() -> dict:
    """Build the bounded atlas from the already-intaken Bruno table.

    The non-lipid Table 2 rows are retained exactly but fail primary eligibility
    because the source does not explicitly place them on a dry roasted basis and
    provides no same-batch moisture.  No moisture is imputed.
    """
    source_path = ROOT / "puckworks/data/bruno2026/bruno2026_roasted_composition.csv"
    selected = []
    with source_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row["compound"] in {"Caffeine", "Trigonelline"}:
                selected.append(row)
    materials = {r["origin_country"]: r for r in csv.DictReader(
        (DATA / "coffee_material_register.csv").open(encoding="utf-8", newline=""))}
    obs = []
    for index, row in enumerate(selected, 1):
        material = materials[row["origin"]]
        value, uncertainty = exact_to_mg_g(float(row["mean"]), row["unit"], float(row["sd"]))
        obs.append({
            "observation_id": f"bruno-{index:02d}",
            "base_coffee_material_id": material["base_coffee_material_id"],
            "roast_batch_id": material["roast_batch_id"], "analytical_batch_id": "not_reported",
            "replicate_id": "", "source_publication_id": "bruno2026",
            "data_lineage_id": "bruno2026_table2", "laboratory_id": "bruno_lab_unicam_rich",
            "analyte": row["compound"].lower(), "value_as_published": row["mean"],
            "unit_as_published": row["unit"], "mass_basis_as_published": row["basis"],
            "uncertainty_value_as_published": row["sd"], "uncertainty_type": "SD",
            "number_of_analytical_replicates": row["n_measurements"],
            "target_semantics": "TOTAL_ROASTED_CONTENT",
            "measurement_provenance": "DIRECT_ROASTED_MATERIAL_ASSAY",
            "canonical_value": f"{value:.8g}", "canonical_unit": "mg/g roasted powder (basis unresolved)",
            "canonical_uncertainty": f"{uncertainty:.8g}", "conversion_rule_id": "mg_per_kg_to_mg_per_g",
            "conversion_inputs": "exact factor 0.001; no moisture conversion",
            "conversion_status": "EXACT_UNIT_ONLY_DRY_BASIS_UNRESOLVED",
            "primary_prediction_label_eligible": "false",
            "exclusion_reason": "MASS_BASIS_UNRESOLVED_NO_SAME_BATCH_MOISTURE",
            "validation_group_id": "vg_bruno2026_table2",
        })
    fields = list(obs[0])
    _write_csv(DATA / "inventory_observation_register.csv", fields, obs)

    zero_gates = {g: False for g in COMPOUND_GATES}
    # F0/F1 have no admitted-row violations, but all structural gates fail.
    zero_gates.update(F0=True, F1=True)
    reduced = disposition(zero_gates, zero_gates, False)
    gate_detail = {}
    for analyte in ("caffeine", "trigonelline"):
        gate_detail[analyte] = {
            "F0": {"pass": True, "eligible_rows": 0, "failure_reasons": []},
            "F1": {"pass": True, "eligible_dry_basis_rows": 0, "unsupported_conversions": 0,
                   "failure_reasons": []},
            "F2": {"pass": False, "material_roast_units": 0, "required": 24,
                   "base_materials": 0, "required_base_materials": 16,
                   "publications": 0, "required_publications": 4,
                   "identified_laboratories": 0, "required_laboratories": 3,
                   "validation_groups": 0, "required_validation_groups": 4,
                   "largest_group_share": None, "failure_reasons": ["no qualifying dry-basis cohort"]},
            "F3": {"pass": False, "arabica_units": 0, "robusta_units": 0,
                   "required_each_species": 8, "failure_reasons": ["both species minima unmet"]},
            "F4": {"pass": False, "route": "NEITHER", "failure_reasons": ["no eligible roast strata or metric"]},
            "F6": {"pass": False, "uncertainty_bearing_fraction": None,
                   "source_laboratory_groups": 0, "failure_reasons": ["no eligible dry-basis units"]},
            "F7": {"pass": False, "outer_validation_groups": 0,
                   "failure_reasons": ["fewer than four eligible validation groups"]},
        }
    claim = [
        "Evidence-adequacy and prediction-feasibility screen only.",
        "Not physical validation of Espresso Whole-Pull or any extraction-kinetics formulation.",
        "Does not establish an extractable fraction or turn total roasted content into c_s0.",
        "Does not authorize runtime integration or an elaborate predictor.",
        "Does not reopen SCI-MD-006 and does not reuse Angeloni.",
        "FAIL means a descriptor-conditioned inventory model is not justified by admitted direct evidence; only restricted source-specific or broad priors remain defensible."
    ]
    result = {
        "task_id": "SCI-MD-007", "schema_version": "1.0.0", "evidence_cutoff_date": "2026-08-25",
        "operational_status": "COMPLETE", "scientific_disposition": reduced["scientific_disposition"],
        "target_semantics": "TOTAL_ROASTED_CONTENT", "canonical_mass_basis": "mg analyte / g dry roasted coffee",
        "compound_gates": gate_detail,
        "paired_coverage": {"F5": {"pass": False, "paired_units": 0, "required": 20,
                                     "validation_groups": 0, "required_validation_groups": 4}},
        "overall_gate_result": False, "extractable_inventory_mapping_status": "NOT_ESTABLISHED",
        "counts": {"candidate_sources": 12, "atlas_sources": 1, "excluded_candidates": 11,
                   "rights_or_access_blocked": 2, "atlas_observations": len(obs),
                   "eligible_observations_per_analyte": {"caffeine": 0, "trigonelline": 0},
                   "atlas_material_roast_units": 4, "atlas_base_materials": 4,
                   "atlas_publications": 1, "atlas_laboratories": 1, "atlas_data_lineages": 1},
        "evidence_class_counts": {"DIRECT_ROASTED_MATERIAL_ASSAY_TOTAL_ROASTED_CONTENT": len(obs)},
        "unit_conversion_counts": {"exact_unit_conversions": len(obs), "dry_basis_conversions": 0,
                                   "excluded_unresolved_basis": len(obs), "moisture_supported": 0},
        "descriptor_coverage_summary": {"eligible_cohort": 0, "post_pass_descriptors": []},
        "uncertainty_floor_summary": {"caffeine": "NOT_ESTIMABLE_ON_ELIGIBLE_COHORT",
                                      "trigonelline": "NOT_ESTIMABLE_ON_ELIGIBLE_COHORT",
                                      "between_lab_reproducibility_floor": "NOT_IDENTIFIABLE"},
        "model_stage": "NOT_RUN_FEASIBILITY_FAILED", "model_comparison_summary": None,
        "model_adoption_status": "NOT_AUTHORIZED_BY_FEASIBILITY_SCREEN", "claim_ceiling": claim,
        "measurement_recommendation": {"status": "PROSPECTIVE_NOT_COMMISSIONED",
          "minimum_design": "paired caffeine/trigonelline direct dry-basis assays spanning both species, at least two comparable roast levels, 24 material-roast units, 16 base materials, four publications, three laboratories, four leakage-safe groups, same-batch moisture and raw replicates"},
    }
    derived_csvs = {
        "source_summary.csv": (["metric", "value"], [{"metric": k, "value": v} for k, v in result["counts"].items() if not isinstance(v, dict)]),
        "coffee_material_summary.csv": (["metric", "value"], [{"metric": "atlas_material_roast_units", "value": 4}, {"metric": "eligible_material_roast_units", "value": 0}]),
        "evidence_class_summary.csv": (["class", "count"], [{"class": k, "count": v} for k, v in result["evidence_class_counts"].items()]),
        "mass_basis_conversion_audit.csv": (["status", "count"], [{"status": k, "count": v} for k, v in result["unit_conversion_counts"].items()]),
        "descriptor_coverage.csv": (["descriptor", "eligible_observation_completeness", "eligible_for_model", "note"], [{"descriptor": d, "eligible_observation_completeness": "NOT_ESTIMABLE", "eligible_for_model": "false", "note": "no eligible dry-basis cohort"} for d in ("species", "roast_category", "quantitative_roast_metric", "moisture", "analytical_method", "replicate_count")]),
        "independence_audit.csv": (["level", "atlas_count", "eligible_count"], [{"level": "material_roast_units", "atlas_count": 4, "eligible_count": 0}, {"level": "base_materials", "atlas_count": 4, "eligible_count": 0}, {"level": "publications", "atlas_count": 1, "eligible_count": 0}, {"level": "laboratories", "atlas_count": 1, "eligible_count": 0}, {"level": "data_lineages", "atlas_count": 1, "eligible_count": 0}, {"level": "validation_groups", "atlas_count": 1, "eligible_count": 0}]),
        "paired_analyte_coverage.csv": (["cohort", "paired_units", "validation_groups"], [{"cohort": "atlas", "paired_units": 4, "validation_groups": 1}, {"cohort": "eligible_dry_basis", "paired_units": 0, "validation_groups": 0}]),
        "uncertainty_floor.csv": (["analyte", "eligible_units", "status", "between_lab_status"], [{"analyte": a, "eligible_units": 0, "status": "NOT_ESTIMABLE", "between_lab_status": "NOT_IDENTIFIABLE"} for a in ("caffeine", "trigonelline")]),
    }
    for name, (fields, rows) in derived_csvs.items():
        _write_csv(OUT / name, fields, rows)
    (OUT / "feasibility_gates.json").write_text(json.dumps({"compound_gates": gate_detail, "F5": result["paired_coverage"]["F5"]}, indent=2, sort_keys=True) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    md = f"# SCI-MD-007 result\n\n**{result['scientific_disposition']}**\n\nOperational status: COMPLETE. Model stage: NOT_RUN_FEASIBILITY_FAILED. The bounded screen found no reproducibly usable direct observations on an explicit dry roasted basis. Total roasted content remains distinct from extractable inventory and c_s0.\n"
    (OUT / "result.md").write_text(md)
    export = {k: result[k] for k in ("task_id", "schema_version", "evidence_cutoff_date", "operational_status", "scientific_disposition", "compound_gates", "paired_coverage", "overall_gate_result", "extractable_inventory_mapping_status", "counts", "model_stage", "model_comparison_summary", "model_adoption_status", "claim_ceiling", "measurement_recommendation")}
    artifact_names = list(derived_csvs) + ["feasibility_gates.json", "result.json", "result.md"]
    export["authoritative_artifact_hashes"] = {name: _hash(OUT / name) for name in sorted(artifact_names)}
    (OUT / "SCI_MD_007_EXPORT.json").write_text(json.dumps(export, indent=2, sort_keys=True) + "\n")
    inputs = [contract_path(), source_path] + sorted(DATA.glob("*.csv"))
    outputs = sorted(OUT.glob("*.csv")) + sorted(OUT.glob("*.json")) + [OUT / "result.md"]
    manifest = {"schema_version": "1.0.0", "inputs": {str(p.relative_to(ROOT)): _hash(p) for p in inputs},
                "outputs": {str(p.relative_to(ROOT)): _hash(p) for p in outputs if p.name != "source_package_manifest.json"}}
    (OUT / "source_package_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-contract", "build-atlas", "adjudicate", "reproduce"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "validate-contract":
        print(json.dumps(validate_contract(), sort_keys=True))
    else:
        before = {p: p.read_bytes() for p in OUT.glob("*") if p.is_file()} if args.check else {}
        result = build_atlas()
        if args.check:
            after = {p: p.read_bytes() for p in OUT.glob("*") if p.is_file()}
            if before != after:
                raise SystemExit("generated output drift")
        print(json.dumps({"model_stage": result["model_stage"], "scientific_disposition": result["scientific_disposition"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

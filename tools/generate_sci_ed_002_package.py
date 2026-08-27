"""Generate the deterministic SCI-ED-002 prospective design package."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "analysis" / "sci_ed_002"
VERSION = "1.0.0"


def dump_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sampling_rows() -> list[dict]:
    rows = []
    labs = {1: "LAB-A", 2: "LAB-B", 3: "LAB-C", 4: "LAB-D", 5: "LAB-A", 6: "LAB-D"}
    orgs = {1: "ORG-01", 2: "ORG-02", 3: "ORG-03", 4: "ORG-04", 5: "ORG-01", 6: "ORG-02"}
    for g in range(1, 7):
        gid = f"VG{g:02d}"
        paired = {"light": "S1", "medium": "S1", "dark": "S2"} if g % 2 else {"light": "S2", "medium": "S1", "dark": "S1"}
        for species, code in (("Arabica", "A"), ("Robusta", "R")):
            for roast in ("light", "medium", "dark"):
                base = f"{gid}-{code}-{paired[roast]}"
                rows.append({
                    "validation_group_id": gid, "source_study_id": f"STUDY-{gid}",
                    "source_package_id": f"PACKAGE-{gid}", "data_lineage_id": f"LINEAGE-{gid}",
                    "source_organization_id": orgs[g], "laboratory_id": labs[g],
                    "base_material_id": base, "material_roast_unit_id": f"{gid}-{code}-{roast.upper()}",
                    "species": species, "roast_stratum": roast, "roast_batch_id": f"RB-{gid}-{code}-{roast.upper()}",
                    "quantitative_roast_metric_type": "CIE_L_STAR_GROUND_COFFEE",
                    "quantitative_roast_metric_unit": "1", "roast_mass_loss_metric_unit": "percent_dry_basis",
                    "role": "HOLDOUT_PRIMARY" if g == 6 else "OPEN_PRIMARY", "analyte_plan": "caffeine|trigonelline",
                    "moisture_plan": "SAME_BATCH_N3", "uncertainty_plan": "REPLICATE_LEVEL",
                })
    return rows


def schemas() -> dict[str, list[str]]:
    return {
        "study_source_groups": ["source_study_id", "source_package_id", "source_organization_id", "rights_status", "provenance_uri"],
        "validation_groups": ["validation_group_id", "source_study_id", "data_lineage_id", "laboratory_id", "group_role"],
        "laboratories": ["laboratory_id", "candidate_name", "site_country", "method_version", "status"],
        "base_coffee_materials": ["base_material_id", "validation_group_id", "species", "variety_status", "country_status", "region_status", "processing_method", "lot_id", "harvest_id", "role"],
        "material_roast_units": ["material_roast_unit_id", "validation_group_id", "source_study_id", "source_package_id", "data_lineage_id", "source_organization_id", "base_material_id", "species", "variety_status", "country_status", "region_status", "processing_method", "lot_id", "harvest_id", "roast_batch_id", "roast_stratum", "roast_date", "role"],
        "sample_aliquots": ["aliquot_id", "material_roast_unit_id", "lane", "split_order", "minimum_mass_g", "blind_code", "storage_condition", "archive_mass_g"],
        "chain_of_custody": ["custody_event_id", "aliquot_id", "actor_role", "event_type", "event_time_utc", "location_code", "seal_status"],
        "roast_measurements": ["roast_measurement_id", "material_roast_unit_id", "metric_type", "raw_value", "unit", "replicate_id", "standard_uncertainty", "method_version", "calibration_id", "quality_status"],
        "moisture_measurements": ["moisture_measurement_id", "material_roast_unit_id", "aliquot_id", "replicate_id", "wet_mass_g", "dry_mass_g", "moisture_fraction", "standard_uncertainty", "method_version", "quality_status"],
        "analytical_batches": ["analytical_batch_id", "laboratory_id", "method_version", "batch_day_code", "acceptance_status"],
        "total_content_measurements": ["measurement_id", "material_roast_unit_id", "analyte", "estimand", "as_received_result", "moisture_measurement_set_id", "dry_basis_result", "unit", "method_version", "preparation_replicate_id", "analytical_batch_id", "injection_replicate_id", "calibration_id", "qc_set_id", "lod", "loq", "censoring_status", "standard_uncertainty", "expanded_uncertainty", "quality_status"],
        "reference_extraction_runs": ["extraction_run_id", "material_roast_unit_id", "preparation_replicate_id", "analytical_batch_id", "method_version", "maximum_cycles", "stop_status"],
        "reference_extraction_steps": ["extraction_step_id", "extraction_run_id", "step_number", "solvent", "coffee_liquid_ratio", "temperature_c", "contact_time_min", "agitation", "separation", "transfer_loss_g", "fraction_volume_ml", "blank_result", "censoring_status", "cumulative_recovery_mg", "increment_fraction", "stopping_rule_qualifies"],
        "chemistry_measurements": ["chemistry_measurement_id", "parent_record_id", "analyte", "estimand", "raw_result", "corrected_result", "unit", "mass_basis", "method_version", "preparation_replicate_id", "analytical_batch_id", "injection_replicate_id", "lod", "loq", "quantification_status", "standard_uncertainty", "quality_status"],
        "quality_control_measurements": ["qc_measurement_id", "analytical_batch_id", "qc_type", "analyte", "result", "unit", "criterion_id", "quality_status"],
        "uncertainty_components": ["uncertainty_component_id", "estimand_record_id", "component_type", "value", "unit", "distribution", "degrees_of_freedom", "covariance_group_id", "method_version"],
        "bridge_assignments": ["bridge_id", "source_material_roast_unit_id", "laboratory_id", "batch_index", "preparation_replicate_id", "blind_code", "role"],
        "holdout_registry": ["validation_group_id", "domain", "owner_role", "access_control", "sealed_status", "unsealing_trigger", "audit_log_uri", "invalidation_rule"],
        "exclusions_and_reruns": ["event_id", "record_id", "event_type", "frozen_rule_id", "reason_code", "decision_role", "quality_status"],
        "file_manifest": ["file_id", "relative_path", "sha256", "media_type", "raw_or_processed", "rights_status", "provenance_uri"],
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = sampling_rows()
    write_csv(OUT / "SAMPLING_MATRIX.csv", list(rows[0]), rows)
    schema_hashes = {}
    for name, fields in schemas().items():
        schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "$id": f"sci-ed-002/{VERSION}/{name}", "title": name, "type": "object", "additionalProperties": False, "required": fields, "properties": {f: {"type": "string", "minLength": 1} for f in fields}}
        path = OUT / "schemas" / VERSION / f"{name}.schema.json"
        dump_json(path, schema)
        schema_hashes[name] = sha(path)
        write_csv(OUT / "templates" / VERSION / f"{name}.csv", fields, [])

    estimands = {
        "schema_version": VERSION,
        "estimands": {
            "T_total": {"name": "TOTAL_ASSAYABLE_ROASTED_CONTENT", "basis": "mass analyte per mass dry roasted coffee", "method_conditioned": True},
            "I_ref": {"name": "OPERATIONALLY_DEFINED_REFERENCE_EXTRACTABLE_INVENTORY", "basis": "mass analyte per mass dry roasted coffee", "method_conditioned": True},
            "Q_production_solid_initial": {"status": "NOT_ESTABLISHED", "mapping_available": False},
        },
        "ratio": {"name": "f_ref", "formula": "I_ref/T_total", "preserve_covariance": True, "clip": False, "discrepancy_investigation": "required_if_difference_exceeds_combined_expanded_uncertainty"},
        "c_s0_mapping_status": "NOT_ESTABLISHED",
    }
    dump_json(OUT / "ESTIMAND_CONTRACT.json", estimands)
    gates = {"contract": "SCI_ED_002_PROSPECTIVE_ACCEPTANCE_GATES", "schema_version": VERSION, "gates": {f"ED2-G{i}": {"status": "PROJECTED_CAPACITY" if i < 11 else "NOT_ELIGIBLE_NO_COMMISSIONED_MEASUREMENTS"} for i in range(12)}, "canonical_sci_md_007_modified": False}
    dump_json(OUT / "PROSPECTIVE_ACCEPTANCE_GATES.json", gates)
    holdout = {"validation_group_id": "VG06", "domain": "INDEPENDENT_COFFEE_ROAST_FAMILY_AND_SOURCE_GROUP", "sealed": True, "open_core_reducer_access": False, "bridge_use": False, "first_sci_md_007_replay_use": False, "unseal_once_after_separate_authorization": True, "owner_role": "INDEPENDENT_HOLDOUT_CUSTODIAN", "operations_metadata_visibility": "IDENTITY_ONLY_NO_ANALYTE_RESULTS", "emergency_access": "OWNER_AUTHORIZATION_WITH_AUDIT_AND_INVALIDATION_REVIEW"}
    dump_json(OUT / "INDEPENDENCE_AND_HOLDOUT_PLAN.json", holdout)
    bridge = {"bridge_materials": [f"BR-{s}-{r}" for s in ("A", "R") for r in ("LIGHT", "MEDIUM", "DARK")], "laboratories": ["LAB-A", "LAB-B", "LAB-C", "LAB-D"], "batches_per_lab": 2, "preparations_per_batch": 3, "minimum_preparation_records": 144, "primary_count_contribution": 0, "source_groups_minimum": 4, "variance_components": ["material", "laboratory", "laboratory_x_material", "batch_within_laboratory", "preparation", "injection", "residual"], "correction_factors_authorized": False}
    dump_json(OUT / "LABORATORY_BRIDGE_PLAN.json", bridge)
    uncertainty = {"schema_version": VERSION, "hierarchy": ["validation_group", "base_material", "material_roast_unit", "laboratory", "analytical_batch", "preparation", "extraction_step", "injection"], "components": ["material_heterogeneity", "aliquot_selection", "moisture", "mass_volume", "sample_preparation", "extraction_recovery", "sequential_stopping", "dilution", "calibration", "instrument_repeatability", "analytical_batch", "laboratory", "bridge_consensus", "dry_basis_conversion", "ratio_covariance"], "dry_basis": "x_dry=x_as_received/(1-w)", "ratio_covariance": "delta_method_with_joint_preparation_or_adjacent_aliquot_covariance", "report": ["point_estimate", "standard_uncertainty", "degrees_of_freedom_or_method", "coverage_factor", "expanded_uncertainty", "coverage_level", "component_contributions", "method_version", "quality_status"]}
    dump_json(OUT / "UNCERTAINTY_MODEL.json", uncertainty)
    result = {"disposition": "SCI_ED_002_PROTOCOL_FROZEN_COMMISSIONING_NOT_AUTHORIZED", "measurements_collected": False, "commissioning_authorized": False, "laboratories_contacted": False, "formal_quotes_obtained": False, "sci_md_007_reexecuted": False, "predictor_eligible": False, "predictor_developed": False, "c_s0_mapping_status": "NOT_ESTABLISHED", "physical_validation_status": "NOT_ESTABLISHED", "governing_physics_change": False, "synthetic_status": "PROSPECTIVE_DESIGN_CAPACITY_ONLY_NO_MEASUREMENTS"}
    dump_json(OUT / "RESULT.json", result)
    fixture = {"sampling_matrix": "../../SAMPLING_MATRIX.csv", "expected_status": result["synthetic_status"]}
    dump_json(OUT / "fixtures" / "valid" / "design.json", fixture)
    mutations = {
        "shared_base_material_across_groups": "BASE_MATERIAL_CROSSES_VALIDATION_GROUPS",
        "shared_source_package_across_folds": "SOURCE_PACKAGE_OVERLAP_ACROSS_GROUPS",
        "only_three_laboratories": "OPEN_CORE_REQUIRES_FOUR_LABORATORIES",
        "missing_species_roast_cell": "GROUP_SPECIES_ROAST_MATRIX_INCOMPLETE",
        "fewer_than_20_open_base_materials": "OPEN_CORE_REQUIRES_20_BASE_MATERIALS",
        "bridge_rows_counted_as_primary_units": "BRIDGE_RECORD_COUNTED_AS_PRIMARY",
        "unpaired_analyte_plan": "PRIMARY_ANALYTE_PLAN_NOT_PAIRED",
        "missing_moisture": "PRIMARY_MOISTURE_PLAN_MISSING",
        "missing_uncertainty": "PRIMARY_UNCERTAINTY_PLAN_MISSING",
        "vg06_used_by_open_core_reducer": "SEALED_GROUP_ACCESS_BY_OPEN_REDUCER",
        "c_s0_mapping_status_changed": "C_S0_MAPPING_MUST_REMAIN_NOT_ESTABLISHED",
    }
    for name, reason in mutations.items():
        dump_json(OUT / "fixtures" / "invalid" / f"{name}.json", {"base": "../valid/design.json", "mutation": name, "expected_failure": reason})

    source_manifest = {"schema_version": VERSION, "files": []}
    for path in sorted(p for p in OUT.rglob("*") if p.is_file() and p.name not in {"SOURCE_MANIFEST.json", "SCI_ED_002_EXPORT.json"}):
        source_manifest["files"].append({"path": path.relative_to(OUT).as_posix(), "sha256": sha(path)})
    dump_json(OUT / "SOURCE_MANIFEST.json", source_manifest)
    export = {"producer_repository": "https://github.com/trbrewer/puckworks.git", "candidate_commit": "SELF_REFERENTIAL_FINAL_COMMIT_RECORDED_BY_RELEASE_STEP", "candidate_tree": "SELF_REFERENTIAL_FINAL_TREE_RECORDED_BY_RELEASE_STEP", "sci_md_007_authority": {"commit": "31741303fb604ed3e6586a555ea6ef6989c24a62", "tree": "a918072d28f555bf98638fa97da1adb568bf09b8"}, "disposition": result["disposition"], "design_counts": {"open_groups": 5, "sealed_groups": 1, "open_units": 30, "total_units": 36, "open_base_materials": 20, "total_base_materials": 24, "laboratories": 4, "bridge_preparations": 144}, "estimand_statuses": estimands["estimands"], "schema_version": VERSION, "schema_sha256": schema_hashes, "holdout_status": "SEALED_NOT_ACCESSED", "claim_ceiling": result, "espresso_crosswalk_identity": "SCI-ED-002-ESPRESSO-EXTENSION-v1.0.0", "source_manifest_sha256": sha(OUT / "SOURCE_MANIFEST.json")}
    dump_json(OUT / "SCI_ED_002_EXPORT.json", export)


if __name__ == "__main__":
    main()

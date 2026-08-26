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
    "TOTAL_ROASTED_CONTENT",
    "OPERATIONALLY_EXTRACTABLE_CONTENT",
    "SOLID_PHASE_CONCENTRATION",
    "EQUILIBRIUM_CONTENT_OR_CEILING",
    "ASYMPTOTIC_EXTRACTED_MASS",
    "BEVERAGE_CONCENTRATION_OR_YIELD",
    "NON_INVENTORY_QUANTITY",
    "UNRESOLVED_TARGET_SEMANTICS",
}
PROVENANCE = {
    "DIRECT_ROASTED_MATERIAL_ASSAY",
    "DIRECT_OPERATIONAL_EXTRACTABILITY_ASSAY",
    "EQUILIBRIUM_DERIVED_ESTIMATE",
    "ASYMPTOTIC_EXTRACTION_ESTIMATE",
    "MODEL_INFERRED_OR_FITTED",
    "BEVERAGE_ENDPOINT_INFERENCE",
    "SECONDARY_SOURCE_SUMMARY",
    "UNRESOLVED_PROVENANCE",
}
COMPOUND_GATES = ("F0", "F1", "F2", "F3", "F4", "F6", "F7")
PASS = "SCI_MD_007_INVENTORY_PREDICTION_FEASIBLE_WITH_EXISTING_EVIDENCE"
FAIL = "SCI_MD_007_INVENTORY_PRIOR_ONLY_ADDITIONAL_DIRECT_MEASUREMENTS_REQUIRED"


def exact_to_mg_g(value: float, unit: str, uncertainty: float | None = None):
    factors = {"mg/kg": 0.001, "g/kg": 1.0, "mg/100 g": 0.01, "g/100 g": 10.0, "%": 10.0}
    if unit not in factors:
        raise ValueError(f"unsupported exact unit conversion: {unit}")
    factor = factors[unit]
    return value * factor, None if uncertainty is None else uncertainty * factor


def as_received_to_dry(
    value: float, moisture: float | None, moisture_basis: str, same_material_batch: bool = True
) -> float:
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
        raise ValueError(
            "phase-volume concentration cannot become coffee-mass content without explicit physics"
        )


def primary_eligible(row: dict) -> bool:
    text = json.dumps(row, sort_keys=True).lower()
    required = (
        "source_publication_id",
        "source_locator",
        "base_coffee_material_id",
        "roast_batch_id",
        "analytical_method",
        "data_lineage_id",
    )
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
    return {
        "caffeine_feasible": cf,
        "trigonelline_feasible": tr,
        "overall_feasible": overall,
        "scientific_disposition": PASS if overall else FAIL,
    }


def contract_path() -> Path:
    return Path(__file__).parents[2] / "docs/analysis/sci_md_007/feasibility_contract.json"


def validate_contract() -> dict:
    raw = contract_path().read_bytes()
    obj = json.loads(raw)
    expected = {
        "contract_id": "SCI_MD_007_FEASIBILITY_CONTRACT_V1",
        "schema_version": "1.0.0",
        "task_id": "SCI-MD-007",
        "evidence_cutoff_date": "2026-08-25",
        "canonical_unit": "mg analyte / g dry roasted coffee",
        "eligible_target_semantics": "TOTAL_ROASTED_CONTENT",
        "eligible_measurement_provenance": "DIRECT_ROASTED_MATERIAL_ASSAY",
        "thresholds": {
            "F2": {
                "material_roast_units": 24,
                "base_coffee_materials": 16,
                "source_publications": 4,
                "identified_laboratories": 3,
                "validation_groups": 4,
                "largest_group_max_fraction": 0.5,
            },
            "F3": {
                "units_per_species": 8,
                "validation_groups_per_species": 3,
                "publications_per_species": 2,
                "laboratories_per_species": 2,
            },
            "F4": {
                "categorical_strata_per_species": 2,
                "categorical_units_per_stratum": 4,
                "categorical_groups_per_stratum": 2,
                "quantitative_metric_units": 16,
                "quantitative_metric_units_per_species": 6,
                "quantitative_metric_groups": 3,
                "within_species_varying_groups": 2,
            },
            "F5": {"paired_material_roast_units": 20, "validation_groups": 4},
            "F6": {"uncertainty_bearing_fraction": 0.5, "uncertainty_source_laboratory_groups": 3},
            "F7": {"outer_validation_groups": 4},
        },
        "compound_formula": "F0 and F1 and F2 and F3 and F4 and F6 and F7",
        "overall_formula": "caffeine_feasible and trigonelline_feasible and F5",
        "pass_disposition": PASS,
        "fail_disposition": FAIL,
        "model_adoption_status": "NOT_AUTHORIZED_BY_FEASIBILITY_SCREEN",
    }
    digest = hashlib.sha256(raw).hexdigest()
    if (
        obj != expected
        or digest != "2f89470195572dc2e4c28960bad6a5f7357c36db6342fb0c13cf9443ab6417a2"
    ):
        raise ValueError("frozen SCI-MD-007 contract differs from commit 241eca9")
    r1_path = contract_path().parent / "r1/R1_CORRECTIVE_SEARCH_CONTRACT.json"
    r1 = json.loads(r1_path.read_text(encoding="utf-8"))
    protocol = contract_path().parent / "r1/R1_CORRECTIVE_SEARCH_PROTOCOL.md"
    required = {
        "schema_version",
        "closure_class",
        "task_id",
        "authorization_id",
        "evidence_cutoff_date",
        "original_contract_commit",
        "original_contract_sha256",
        "providers",
        "result_limit_per_query_per_provider",
        "queries",
        "mandatory_rescreen",
        "citation_passes",
        "source_screening_states",
        "row_eligibility_rules",
        "search_completion_formula",
        "rights_rules",
        "angeloni_rule",
        "protocol_sha256",
    }
    if set(r1) < required or r1["closure_class"] != "R1_CORRECTIVE_CONTRACT_CLOSURE":
        raise ValueError("R1 corrective contract schema incomplete")
    if len(r1["queries"]) != 8 or r1["providers"] != ["Crossref", "OpenAlex", "GeneralPublicWeb"]:
        raise ValueError("R1 query/provider set differs from frozen corrective design")
    if r1["result_limit_per_query_per_provider"] != 20:
        raise ValueError("R1 result limit changed")
    protocol_digest = hashlib.sha256(protocol.read_bytes()).hexdigest()
    if protocol_digest != r1["protocol_sha256"]:
        raise ValueError("R1 protocol hash mismatch")
    return {
        "contract_sha256": digest,
        "r1_contract_sha256": hashlib.sha256(r1_path.read_bytes()).hexdigest(),
        "r1_protocol_sha256": protocol_digest,
        "valid": True,
    }


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


def build_atlas(check: bool = False) -> dict:
    """Run the R1 data-derived generator; authoritative inputs are read-only."""
    from .sci_md_007_r1 import build

    return build(check=check)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command", choices=("validate-contract", "build-atlas", "adjudicate", "reproduce")
    )
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.command == "validate-contract":
        print(json.dumps(validate_contract(), sort_keys=True))
    else:
        from .sci_md_007_r1 import build

        result = build(check=args.check)
        print(
            json.dumps(
                {
                    "model_stage": result["model_stage"],
                    "scientific_disposition": result["scientific_disposition"],
                },
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

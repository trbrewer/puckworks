"""Deterministic SCI-MD-007 evidence feasibility primitives.

This concrete analysis never reads Angeloni data and never changes runtime inventory
semantics.  Real-data build/adjudication is deliberately data-driven from the task
registers under ``puckworks/data/sci_md_007``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
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
    assert obj["task_id"] == "SCI-MD-007"
    assert obj["thresholds"]["F2"]["material_roast_units"] == 24
    return {"contract_sha256": hashlib.sha256(raw).hexdigest(), "valid": True}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate-contract",))
    args = parser.parse_args(argv)
    if args.command == "validate-contract":
        print(json.dumps(validate_contract(), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

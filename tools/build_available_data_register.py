#!/usr/bin/env python3
"""Build the decision-use data register from the canonical MANIFEST.csv."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "puckworks/data/MANIFEST.csv"
OUTPUT = ROOT / "puckworks/data/AVAILABLE_DATA_REGISTER.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def family_id(dataset_id: str) -> str:
    return dataset_id.split("/", 1)[0].upper().replace("-", "_")


def build() -> dict:
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8", newline="")))
    families: dict[str, dict] = {}
    for row in rows:
        fid = family_id(row["dataset_id"])
        item = families.setdefault(fid, {
            "family_id": fid, "title": row["source_card"],
            "source_cards": [], "manifest_dataset_ids": [],
            "publication_or_repository": row["source_artifact"],
            "source_identifiers": [], "stages": ["UNKNOWN"],
            "observables": ["UNKNOWN"], "measurement_resolution": "UNKNOWN",
            "fraction_resolution": "UNKNOWN", "time_resolution": "UNKNOWN",
            "spatial_resolution": "UNKNOWN", "analytes": ["UNKNOWN"],
            "physical_shot_count_if_known": "UNKNOWN",
            "physical_replicate_structure": "UNKNOWN",
            "coffee_count_if_known": "UNKNOWN", "coffee_lot_count_if_known": "UNKNOWN",
            "roast_batch_count_if_known": "UNKNOWN", "grinder_count_if_known": "UNKNOWN",
            "apparatus_count_if_known": "UNKNOWN", "laboratory_count_if_known": "UNKNOWN",
            "directness": [], "uncertainty_status": [], "validation_strength": [],
            "source_internal_or_external": "UNKNOWN", "target_exposure": "UNKNOWN",
            "historical_task_uses": [], "consumed_comparison_status": "UNKNOWN",
            "raw_access_status": "PACKAGED_IN_REPOSITORY", "external_corpus_id": None,
            "external_source_manifest_hash": None, "rights": [], "eligible_uses": [],
            "conditionally_eligible_uses": [], "blocked_uses": [], "missing_joins": [],
            "last_qualified_task": "PANNUSCH-PRIOR-IMPACT-001",
            "last_qualified_commit": "57f7e74eef92aa9d83ae0995f8b6123663b37548",
            "notes": []
        })
        for key, value in (("source_cards", row["source_card"]),
                           ("manifest_dataset_ids", row["dataset_id"]),
                           ("directness", row["extraction_method"]),
                           ("uncertainty_status", row["uncertainty_retained"]),
                           ("validation_strength", row["validation_strength"]),
                           ("rights", row["license_access"]),
                           ("historical_task_uses", row["gate_use"]),
                           ("notes", row["caveat"])):
            if value not in item[key]:
                item[key].append(value)

    pannusch = families["PANNUSCH2024"]
    pannusch.update({
        "title": "Pannusch 2024 full source repository and qualified reconstructions",
        "publication_or_repository": "Mendeley Data DOI 10.17632/y2tz67f6ry.1",
        "source_identifiers": ["10.17632/y2tz67f6ry.1"],
        "stages": ["extraction"],
        "observables": ["fraction_concentration", "fraction_mass", "TDS", "programmed_flow", "temperature"],
        "measurement_resolution": "PHYSICAL_SHOT_AND_FRACTION_RESOLVED",
        "fraction_resolution": "6 fit/prediction fractions; 12 reference fractions",
        "time_resolution": "fraction boundaries and programmed conditions",
        "analytes": ["caffeine", "trigonelline", "5-CQA", "workbook-defined CQA sum", "TDS"],
        "physical_shot_count_if_known": 69,
        "physical_replicate_structure": "15 fit conditions x3; 8 prediction conditions x3; one n=1 reference preparation",
        "coffee_count_if_known": 1, "apparatus_count_if_known": 1, "laboratory_count_if_known": 1,
        "directness": ["DIRECT_RECOVERED_FRACTION_CHEMISTRY", "N1_OPERATIONAL_REFERENCE_ESTIMATE"],
        "uncertainty_status": ["physical replicates retained; three invalid spills excluded"],
        "validation_strength": ["source-internal; source prediction targets exposed; not independent validation"],
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "consumed_comparison_status": "NOT_INDEPENDENT_EXTERNAL_VALIDATION",
        "raw_access_status": "EXTERNAL_RECOVERED_LOCAL_CORPUS",
        "external_corpus_id": "PANNUSCH2024_MENDELEY_FULL_REPOSITORY",
        "external_source_manifest_hash": "15b9f765d49abe45d6788d7c7891b0695fca185d9c614d122e393993ec06a83c",
        "eligible_uses": ["source reconstruction", "replicate analysis", "source-internal campaign-separated comparison", "programmed-flow contrast", "source-apparatus variance planning"],
        "conditionally_eligible_uses": ["normalized fraction-shape analysis subject to SCI-MD-008 consistency"],
        "blocked_uses": ["independent external validation", "target-blind claim", "total roasted inventory", "production M0", "I_ref-to-M0 bridge", "absolute closure", "hydraulic validation under prescribed flow", "temperature-ramp EWP comparison under current physics", "local home-lab method qualification"],
        "missing_joins": ["production M0", "spent-puck residual", "retained liquid", "same lot", "same roast batch", "independent coffee/apparatus/laboratory"],
        "notes": ["fit_experiments=15; fit_physical_shots=45; fit_fractions=6; prediction_conditions=8; prediction_physical_shots=24; prediction_fractions_per_shot=6; reference_preparations=1; reference_fractions=12; invalid_spills=3", "Raw source files are external and are resolved at runtime; they are not redistributed."]
    })
    return {"schema_version": 1, "manifest_path": "puckworks/data/MANIFEST.csv",
            "manifest_sha256": sha256(MANIFEST), "dataset_count": len(rows),
            "families": [families[k] for k in sorted(families)]}


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

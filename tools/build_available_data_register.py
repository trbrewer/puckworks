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
    families["VISUALIZER"].update({
        "raw_access_status": "PERMISSIONED_LOCAL_API_SNAPSHOT_READY_FOR_INTERNAL_ANALYSIS",
        "external_corpus_id": "VISUALIZER_COFFEE_API_CRAWL_2026_07_15",
        "eligible_uses": ["REAL_WORLD_BOUNDARY_LIBRARY_AND_OPERATING_ENVELOPE", "profile and response variability", "descriptive apparent-resistance analysis"],
        "conditionally_eligible_uses": ["bounded predictive hydraulic study under a new qualified protocol"],
        "blocked_uses": ["population TDS/EY analysis", "laboratory-grade chemistry", "dynamic-resistance production adoption", "device-stratified conclusions without integration identity", "causal mechanism attribution", "raw redistribution", "private-record use"],
        "physical_shot_count_if_known": 23169,
        "last_qualified_task": "ESPRESSO-CORPUS-LEVERAGE-002-C1",
        "notes": ["23,169 unique records; deterministic sample 1,966; time-series-qualified 1,223; resistance-qualified 1,061; plausible nonzero TDS/EY before joint consistency checks 8/9; hydraulics are descriptive motivating evidence, not predictive qualification"],
    })
    families["WASZKIEWICZ2025"].update({
        "physical_shot_count_if_known": 56,
        "physical_replicate_structure": "56 distinct physical brews grouped in 11 controlled conditions; source time samples are not independent observations",
        "measurement_resolution": "PHYSICAL_BREW_AND_PROCESSED_TIME_SERIES",
        "uncertainty_status": ["aggregate SEM; not row-level independent noise"],
        "eligible_uses": ["controlled component-level fixed-versus-evolving effective-resistance comparison"],
        "blocked_uses": ["direct permeability validation", "universal coffee transfer", "independent whole-model validation"],
        "last_qualified_task": "ESPRESSO-CORPUS-LEVERAGE-002-C1",
        "notes": ["56 distinct physical brews grouped in 11 controlled conditions; pressure is a processed basket-node/basket-location quantity; flow and mass are processed or derived according to the source; claim ceiling is source-internal controlled component evidence on one apparatus"],
    })
    families["WADSWORTH2026"].update({
        "eligible_uses": ["SEPARATE_SOURCE_PRIORS_AND_OBSERVATION_OPERATORS"],
        "blocked_uses": ["DIRECT_ROW_LEVEL_FUSION_AS_ONE_COMMON_VALIDATION_SET"],
        "notes": ["22 PSD-related rows; 21 permeability values; permeability range 1.58e-11 to 1.91e-10 m^2"],
        "last_qualified_task": "ESPRESSO-CORPUS-LEVERAGE-002-C1",
    })
    families["VACAGUERRA2023A"].update({
        "eligible_uses": ["SEPARATE_SOURCE_PRIORS_AND_OBSERVATION_OPERATORS"],
        "blocked_uses": ["DIRECT_ROW_LEVEL_FUSION_AS_ONE_COMMON_VALIDATION_SET"],
        "notes": ["50 dry-porosity validation rows; do not equate coffee, apparatus, PSD method, porosity definition, compaction state, permeability method, or geometry with Wadsworth"],
        "last_qualified_task": "ESPRESSO-CORPUS-LEVERAGE-002-C1",
    })
    families["POCKETSCIENCE2024"].update({
        "raw_access_status": "EXTERNAL_WORKBOOK_CONFIGURED_RESOLVER",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "eligible_uses": ["SHEET_SPECIFIC_OPERATIONAL_RECOVERABLE_SOLUTE_CONTRAST"],
        "conditionally_eligible_uses": ["MODEL_TO_ASSAY_MAP_WITH_EXPLICIT_RECOVERY_DRAINAGE_AND_INVENTORY_ASSUMPTIONS"],
        "blocked_uses": ["UNQUALIFIED_RADIAL_SOLID_DEPLETION", "PHYSICAL_VALIDATION", "NEW_SOURCE_AGGREGATE_PUBLICATION_WITHOUT_GRANT_SCOPE"],
        "missing_joins": ["regional initial mass calibration", "post-stop drainage and handling", "recovery efficiencies and model-pool equivalence", "actual expanded publication grant", "exact plotting/MC algorithm"],
        "last_qualified_task": "SCI-MD-RADIAL-OBS-001",
        "last_qualified_commit": "TASK_BRANCH_CONTRACT_HASH_BOUND_NOT_PRODUCTION_AUTHORITY",
    })
    if "GRUDEVA2026" in families:
        families["GRUDEVA2026"].update({
            "source_identifiers": ["10.1017/S095679252500018X"],
            "stages": ["extraction", "infiltration"],
            "observables": ["dimensionless outlet concentration", "spatial liquid profiles", "front positions"],
            "source_internal_or_external": "PUBLISHED_NUMERICAL_REFERENCE",
            "target_exposure": "PUBLIC_COMPARISON_NOT_CALIBRATION",
            "eligible_uses": ["CODE_VERIFICATION", "QUALIFIED_RASTER_COMPARISON"],
            "blocked_uses": ["PHYSICAL_VALIDATION", "EXACT_FIGURE5_REPRODUCTION_WITHOUT_FULL_PROFILES"],
            "last_qualified_task": "MODEL-GRUDEVA2026-REDUCED-001",
            "last_qualified_commit": "TASK_SOURCE_HASH_BOUND_NOT_PRODUCTION_AUTHORITY",
            "physical_shot_count_if_known": 0,
        })
    if "MELROSE2019BED" in families:
        families["MELROSE2019BED"].update({
            "title": "Melrose 2019 Figure 2 partial transient-flow readings",
            "source_identifiers": ["preprint 2019-09-26; SHA256 in melrose2019bed/contract.json"],
            "stages": ["bed_dynamics"],
            "observables": ["published collected-volume interval-average flow rate"],
            "measurement_resolution": "57 visible markers; 14 profile fragments; 10 assigned conditions; partial coverage",
            "time_resolution": "plotted times; exact interval endpoints unknown; campaign 5/10 s HF/LF aliquots",
            "physical_replicate_structure": "UNSPECIFIED_PUBLISHED_AGGREGATE; Figure1 repetition count does not establish Figure2 members/weights",
            "source_internal_or_external": "SOURCE_INTERNAL",
            "target_exposure": "TARGET_EXPOSED",
            "consumed_comparison_status": "RETROSPECTIVE_FIGURE_READING_NOT_PREDICTIVE_VALIDATION",
            "eligible_uses": ["finite within-profile ordinate compatibility under declared reading bounds"],
            "conditionally_eligible_uses": ["opening-only hydraulic implication with qualified pressure, constitutive factors, storage, collection and fixed aggregation"],
            "blocked_uses": ["intrinsic permeability", "cross-pressure reversal", "independent replication", "physical validation", "unqualified individual-run inference"],
            "missing_joins": ["replicate membership and weights", "exact interval endpoints", "pressure-node/value reconciliation", "hydraulic observer and fixed fluid properties", "obscured markers and LF triangle condition identity"],
            "last_qualified_task": "SCI-MD-MELROSE-TRANSIENT-HYDRAULICS-001",
            "last_qualified_commit": "TASK_SOURCE_HASH_BOUND_NOT_PRODUCTION_AUTHORITY",
        })
    # Heterogeneous older Corrochano subsets retain their original aggregate labels.
    # This source observer and its exposure/eligibility apply ONLY to Figure6.23.
    figure_id = "romancorrochano2017/fig6_23_pressure_flow_temperature"
    figure_row = next(row for row in rows if row["dataset_id"] == figure_id)
    families["ROMANCORROCHANO2017"]["dataset_scopes"] = {
        figure_id: {
            "source_card": figure_row["source_card"],
            "observer": "inlet-referenced apparent conductance; upstream meter / reported corrected bed pressure",
            "source_internal_or_external": "SOURCE_INTERNAL",
            "target_exposure": "TARGET_EXPOSED",
            "validation_strength": figure_row["validation_strength"],
            "physical_validation": "NOT_ESTABLISHED",
            "eligible_uses": ["finite figure-reading compatibility and condition-envelope temperature contrasts"],
            "conditionally_eligible_uses": ["scoped hydraulic observer implications", "EQUAL-alpha common-geometry required viscosity ratio"],
            "blocked_uses": ["authenticated individual pairing", "intrinsic permeability", "physical zero flow", "independent campaign replication", "physical validation"],
            "missing_joins": ["run pairing and membership", "meter volume reference and bed-flow mapping", "sensor response/alignment", "actual pressure and calibration reconciliation", "synchronized viscosity/internal geometry"],
            "coverage": "44/48 condition-panel slots; 60s unsupported; one late hot-flow fragment; physical-run counts UNKNOWN",
            "campaign": "existing Corrochano/Melrose lineage; no new independent campaign",
            "last_qualified_task": "SCI-MD-CORROCHANO-PRESSURE-FLOW-001",
        }
    }
    aspect_id = "romancorrochano2017/fig6_9_aspect_ratio"
    aspect_row = next(row for row in rows if row["dataset_id"] == aspect_id)
    families["ROMANCORROCHANO2017"]["dataset_scopes"][aspect_id] = {
        "source_card": aspect_row["source_card"],
        "observer": "four condition-mean Darcy permeabilities; displayed variability and vector-reading bounds separate",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "validation_strength": aspect_row["validation_strength"],
        "physical_validation": "NOT_ESTABLISHED",
        "eligible_uses": ["declared figure-reading ratios", "fixed representative-state consolidation comparison"],
        "conditionally_eligible_uses": ["geometry and conductance accounting with declared lengths, viscosity and qualified Darcy observer"],
        "blocked_uses": ["independent campaign replication", "paired-bed residuals", "causal mechanism identification", "physical validation"],
        "missing_joins": ["bed-level permeability/consolidation identity and covariance", "actual viscosity and extraction state", "wide-cell calibration and correction implementation", "meter volume reference", "temperature-study executed result unavailable"],
        "coverage": "4/4 means and 8/8 displayed endpoints; duplicate graphics removed; no authenticated bed pairs",
        "campaign": "existing thesis/journal/Melrose lineage; narrow bars linked to table aggregates, physical-bed identity unresolved",
        "last_qualified_task": "SCI-MD-CORROCHANO-ASPECT-RATIO-CONSOLIDATION-001",
    }
    hydration_id = "romancorrochano2017/fig6_22_hydration_flow"
    hydration_row = next(row for row in rows if row["dataset_id"] == hydration_id)
    families["ROMANCORROCHANO2017"]["dataset_scopes"][hydration_id] = {
        "source_card": hydration_row["source_card"],
        "observer": "published HR / HR_max; reported corrected bed pressure / inlet-meter flow before unqualified maximum normalization",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "validation_strength": hydration_row["validation_strength"],
        "physical_validation": "NOT_ESTABLISHED",
        "eligible_uses": ["fixed reported-mean-flow rescaling on published clock under graphical-reading contract", "same-clock descriptive condition-envelope comparisons"],
        "conditionally_eligible_uses": [],
        "blocked_uses": ["absolute HR law exclusion", "actual cumulative-volume interpretation", "physical repetition matching", "mechanism identification", "population/statistical rejection", "independent campaign replication", "physical validation"],
        "missing_joins": ["maximum normalization algorithm and window", "mean-flow averaging interval", "common physical clock origin", "instrument-file repetition identity and cross-figure reuse", "instantaneous flow and through-bed observation mapping", "sensor/correction/thermal alignment"],
        "coverage": "6 graphical traces; 15 chunks; 9 bounded joins; 26/30 rescaled and 10/15 same-clock complete envelope requests; all unsupported rows retained",
        "campaign": "existing Corrochano thesis/journal/Melrose lineage; no new independent campaign",
        "last_qualified_task": "SCI-MD-CORROCHANO-HYDRATION-FLOW-RESCALING-001",
    }
    dry_id = "romancorrochano2017/fig6_2_dry_compaction"
    dry_row = next(row for row in rows if row["dataset_id"] == dry_id)
    families["ROMANCORROCHANO2017"]["dataset_scopes"][dry_id] = {
        "source_card": dry_row["source_card"],
        "observer": "published applied axial force and dry coffee mass per bulk bed volume",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "validation_strength": dry_row["validation_strength"],
        "physical_validation": "NOT_ESTABLISHED",
        "eligible_uses": ["fixed-density force and fixed-force density graphical readings", "same-sample force increments and limited additive-force-offset null"],
        "conditionally_eligible_uses": [],
        "blocked_uses": ["population significance", "intrinsic modulus or constitutive law", "wet-bed or hydraulic inference", "exclusion of horizontal density shifts", "independent campaign replication", "physical validation"],
        "missing_joins": ["native force/displacement records", "instrument/sample IDs", "load-cell/displacement calibration and compliance", "force zero and initial state", "individual preparation and loading histories", "journal Figure7 path membership or averaging"],
        "coverage": "12 graphical samples;76 unique chunks painted twice;156 declared sample requests and12 cross-grind comparisons; unsupported/ambiguous requests retained",
        "campaign": "existing Corrochano thesis/journal/Melrose lineage; no new independent campaign",
        "last_qualified_task": "SCI-MD-CORROCHANO-DRY-COMPACTION-001",
    }
    return {"schema_version": 1, "manifest_path": "puckworks/data/MANIFEST.csv",
            "manifest_sha256": sha256(MANIFEST), "dataset_count": len(rows),
            "families": [families[k] for k in sorted(families)]}


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

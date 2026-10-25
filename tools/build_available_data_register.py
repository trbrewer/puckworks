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

    families["MATIAS2023"].update({
        "title": "Matias 2023 aggregate caffeine finite-vial fractions",
        "source_identifiers": ["10.1063/5.0176273", "arXiv:2304.03161v2"],
        "stages": ["extraction", "observables"], "analytes": ["caffeine"],
        "observables": ["finite-vial aggregate concentration mg/L", "reported vertical SE"],
        "measurement_resolution": "10 means; 10 centers, 20 vertical endpoints, 10 horizontal segments recovered",
        "fraction_resolution": "ten sequential nominal 5 mL fractions; endpoints 5,...,50 mL",
        "time_resolution": "UNKNOWN; no volume-to-time mapping",
        "physical_shot_count_if_known": 4,
        "physical_replicate_structure": "four extractions aggregated; forty individual concentrations unavailable in inspected source",
        "coffee_count_if_known": 1, "apparatus_count_if_known": 1,
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "RETROSPECTIVE; TARGET_EXPOSED; NONSCORING",
        "raw_access_status": "PACKAGED_QUALIFIED_GEOMETRY; PUBLIC_PINNED_PDF_ARCHIVE_EXTERNAL",
        "eligible_uses": ["nominal equal-bin finite-fraction observation comparison",
                          "one nonincreasing exponential representation cost",
                          "exact nonincreasing log-convex relaxation; positive-mixture discrepancy lower bound",
                          "graphical recovery sensitivity",
                          "descriptive reported-SE endpoint sensitivity", "adjacent log ratios and curvatures"],
        "conditionally_eligible_uses": ["practical adequacy only with separately authorized tolerance"],
        "blocked_uses": ["independent validation", "physical validation", "individual extraction inference",
                         "particular mechanism or full continuum-model rejection", "production calibration",
                         "exact mixture optimum from relaxed shape cost", "mixture reconstruction from shape compatibility",
                         "unequal-volume robustness", "common 70 mg normalization", "simultaneous-confidence or equivalence claim"],
        "missing_joins": ["individual extraction concentrations", "actual collection boundaries",
                          "horizontal-segment semantics", "common dose/inventory normalization", "controlled extraction temperature"],
        "consumed_comparison_status": "FIXED_POSITIVE_EXPONENTIAL_MIXTURE_EXCLUDED_BY_NECESSARY_SHAPE_ON_DECLARED_N_G_P_OUTER_CONTRACTS",
        "last_qualified_task": "SCI-MD-MATIAS-CAFFEINE-AGGREGATION-001", "last_qualified_commit": None,
        "result": "docs/analysis/sci_md_matias_caffeine_aggregation_001/RESULT.md",
        "accepted_one_rate_result": "docs/analysis/sci_md_matias_caffeine_fraction_shape_001/RESULT.md",
        "PHYSICAL_VALIDATION": "NOT_ESTABLISHED",
    })

    families["KHAMITOVA2020"].update({
        "title": "Khamitova 2020 nominal tamping-force-labelled endpoint chemistry",
        "source_identifiers": ["10.15165/khamitova-gulzhan_phd2020-06-25",
                               "https://pubblicazioni.unicam.it/handle/11581/480144"],
        "stages": ["extraction", "observables"],
        "observables": ["reported amount per reference 40 mL", "related concentration mg/mL",
                        "reported RSD percent; aggregation unresolved", "ground-coffee assay context"],
        "analytes": ["total CQA", "caffeine", "trigonelline", "nicotinic acid"],
        "measurement_resolution": "144 analyte means / 36 configurations; 432 chemistry entries; 8 ground entries",
        "fraction_resolution": "endpoint only; related-unit columns are not separate observations",
        "time_resolution": "nominal 25+/-1 s; no cell-specific clock or transient series",
        "physical_shot_count_if_known": 72,
        "physical_replicate_structure": "36 duplicated configurations; mean/RSD analysis count and pooling UNKNOWN",
        "coffee_count_if_known": 1, "apparatus_count_if_known": 1, "grinder_count_if_known": 1,
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "RETROSPECTIVE; TARGET_EXPOSED; NONSCORING",
        "raw_access_status": "PACKAGED_TRANSCRIPTIONS; OFFICIAL_PDF_AUDITED_NOT_REDISTRIBUTED; RAW_REPLICATES_UNKNOWN",
        "eligible_uses": ["source-specific four-level constant representation cost",
                          "fixed 30-minus-10 kgF contrasts and intermediate-force range",
                          "conditional decimal-rounding sensitivity", "secondary reported-RSD scale diagnostic"],
        "conditionally_eligible_uses": ["future collapse decision with independently justified application error budget and observation basis"],
        "blocked_uses": ["isolated causal tamping effect", "equivalence or practical adequacy claim",
                         "population inference from reported RSD", "extraction yield or inventory recovery",
                         "species-matched 5-CQA comparison", "independent validation or production calibration"],
        "missing_joins": ["shot-to-assay aggregation and RSD basis", "grinder tuning chronology",
                          "measured beverage volume/density", "ground assay dilution/unit reconciliation"],
        "consumed_comparison_status": "DESCRIPTIVE_REPRESENTATION_BENCHMARK; NO_ACCEPTANCE_THRESHOLD",
        "last_qualified_task": "SCI-MD-KHAMITOVA-TAMPING-CHEMISTRY-001",
        "last_qualified_commit": None,
        "result": "docs/analysis/sci_md_khamitova_tamping_chemistry_001/RESULT.md",
        "PHYSICAL_VALIDATION": "NOT_ESTABLISHED",
    })

    radial_id = "foster2025_2/fig8_fig9_radial_front"
    families["FOSTER2025_2"].update({
        "dataset_scopes": {radial_id: {
            "observables": ["published_fitted_infiltration_interface", "published_front_position_extents"],
            "measurement_resolution": "90 canonical shell/scan slots; 30 primary; independent feature support",
            "spatial_resolution": "ten native annuli, r=0.0 to 1.0; equal widths, unequal areas",
            "time_resolution": "printed scans 0-8 s; one-second reconstructions; window convention unknown",
            "physical_replicate_structure": "dependent shells/scans of displayed fine-grind experiment",
            "source_internal_or_external": "SOURCE_INTERNAL",
            "target_exposure": "RETROSPECTIVE; TARGET_EXPOSED; NONSCORING",
            "eligible_uses": ["finite center minimax discrepancy", "outer-minus-inner center contrast",
                              "literal displayed-extent compatibility under graphical reading contract"],
            "blocked_uses": ["physical uniformity or binary saturation", "first liquid/extraction arrival",
                             "measured permeability/porosity/flow", "independent validation", "causal grind effect"],
            "uncertainty_status": "graphical outer enclosures; displayed extents not confidence or physical bounds",
            "result": "docs/analysis/sci_md_foster_radial_front_001/RESULT.md",
            "PHYSICAL_VALIDATION": "NOT_ESTABLISHED",
        }},
        "last_qualified_task": "SCI-MD-FOSTER-RADIAL-FRONT-001 (new radial subset only; prior roles unchanged)",
        "last_qualified_commit": None,
    })

    mo_profile_id = "mo2023/fig14_fig16_segmented_profiles"
    families["MO2023"].update({
        "source_identifiers": ["10.1038/s41598-023-42380-y", "arXiv:2305.03911v2"],
        "dataset_scopes": {mo_profile_id: {
            "observables": ["published_segmented_signal; native epsilon/source porosity metadata"],
            "measurement_resolution": "24 annular-region graphical profiles; 48 dependent contrast requests",
            "physical_replicate_structure": "two capsule histories, medium/delayed and dark/immediate; not 24 extractions",
            "directness": "native vector segments authenticated against final publication renders",
            "source_internal_or_external": "SOURCE_INTERNAL",
            "target_exposure": "TARGET_EXPOSED; RETROSPECTIVE; NONSCORING",
            "eligible_uses": ["descriptive spatial signal band contrasts", "display-coordinate contrast differences"],
            "conditionally_eligible_uses": ["future comparison with a separately qualified observation operator"],
            "blocked_uses": ["intrinsic geometric porosity ordering/change", "measured permeability",
                             "independent replication", "mechanism validation", "unqualified evolving-bed calibration"],
            "uncertainty_status": "graphical outer reading enclosures only; physical variability unquantified",
            "missing_joins": ["wet liquid/solid distinction", "material registration", "physical observation operator"],
            "result": "docs/analysis/sci_md_mo_wet_ct_profiles_001/RESULT.md",
            "PHYSICAL_VALIDATION": "NOT_ESTABLISHED",
        }},
        "last_qualified_task": "SCI-MD-MO-WET-CT-PROFILES-001 (new graphical subset only; prior SPH labels retained)",
        "last_qualified_commit": None,
    })

    families["HARGARTEN2020"].update({
        "title": "Hargarten 2020 swelling and dry/wet particle-size observations",
        "source_identifiers": ["10.1002/jsfa.10440"],
        "stages": ["grind", "bed_dynamics"],
        "observables": ["normalized diffraction-equivalent volume CDF on plotted interval midpoints",
                        "scalar swelling summaries", "microscopy swelling progress"],
        "measurement_resolution": "RETAINED_GRAPHICAL_MARKERS_AND_PUBLISHED_SCALARS",
        "fraction_resolution": "non-sieved medium; prepared medium S/M/L and light S/M",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "eligible_uses": ["bounded graphical-representation exclusion and necessary quantile constraints"],
        "blocked_uses": ["physical-cutoff fractions without bin mapping", "simultaneous compatibility from outer ranges",
                         "mobile-fines mass or erosion rate", "hydraulic closure calibration", "physical validation"],
        "missing_joins": ["instrument bin edges/scaling observation map", "obscured cumulative CI endpoints",
                          "same-particle dry/wet pairing", "PSD-to-hydraulic mapping"],
        "last_qualified_task": "SCI-MD-HARGARTEN-WET-PSD-001",
        "last_qualified_commit": None,
        "notes": ["Figures 2/3b/5b: G dilation excluded for both non-sieved protocols; prepared quantile intersections remain necessary-only outer candidates. P dilation unresolved. Physical-cutoff mapping unresolved; PHYSICAL_VALIDATION=NOT_ESTABLISHED.",
                  "Hot label 90 C cools to about 60 C; washed retained coarse fractions and non-sieved/ultrasound operators differ. Figure5 caption L conflicts with artwork; only light S/M retained.",
                  "Same Hargarten article/reprint campaign; scalar CSVs unchanged. Fine F, density and microscopy figures not newly intaken."]
    })
    families["MAILLE2021"].update({
        "title": "Maille 2021 particle swelling and observed-population effects",
        "source_identifiers": ["10.1016/j.jfoodeng.2020.110420", "ASIC2021 S8-PO-01"],
        "stages": ["grind", "bed_dynamics"],
        "observables": ["reported LD x50 and x90", "LD volume concentration",
                        "same-particle microscopy depictions; qualitative only"],
        "measurement_resolution": "24_GRAPHICAL_MARKERS_IN_8_ALIGNED_TIME_GROUPS",
        "time_resolution": "native poster abscissae; approximately 14-263 s; not a dry baseline",
        "physical_replicate_structure": "UNKNOWN; journal/poster/thesis are one study lineage",
        "source_internal_or_external": "SEPARATE_SOURCE_FROM_HARGARTEN; SOURCE_INTERNAL_REPRESENTATION_TEST",
        "target_exposure": "TARGET_EXPOSED",
        "raw_access_status": "DERIVED_READINGS_PACKAGED; ORIGINALS_NOT_LOCATED_IN_BOUNDED_SEARCH",
        "eligible_uses": ["conditional fixed-population/common-scaling graphical invariant test",
                          "source-grounded qualitative population-sampling evidence"],
        "conditionally_eligible_uses": ["future observation-model assessment with exact source contract"],
        "blocked_uses": ["physical geometric-growth bound", "entrainment fraction or rate fit",
                         "C_M or D_W calibration", "equilibrium or dry-to-wet growth bound",
                         "permeability closure", "physical validation"],
        "missing_joins": ["LD material/protocol and optical/concentration mapping",
                          "experimental uncertainty and replicate identities",
                          "microscopy coffee boundaries and projection uncertainty",
                          "dry baseline and saturation premise"],
        "last_qualified_task": "SCI-MD-MAILLE-SWELLING-EVIDENCE-001",
        "last_qualified_commit": None,
        "notes": ["K=C_V/x50^3 conditionally excluded on retained graphical support; x90/x50 has necessary-only outer overlap. Geometric bound null/NOT_IDENTIFIABLE; PHYSICAL_VALIDATION=NOT_ESTABLISHED.",
                  "Full journal inaccessible; authenticated official poster and attributed thesis reproduction. No extra campaigns from republication; Maille2024 extraction identity/limitations unchanged."]
    })
    families["SMRKE2024"].update({
        "source_identifiers": ["10.1038/s41598-024-55831-x"],
        "stages": ["grind", "observables"],
        "observables": ["Figure3 endpoint EY/time", "S1 derivative of beverage mass, g/s"],
        "measurement_resolution": "S1 native raster ink and qualified graphical reading enclosures",
        "time_resolution": "literal plotted seconds; sampling and derivative processing UNKNOWN",
        "physical_replicate_structure": "S1 nominal3 per12 intended cells; recovered physical shot identity UNKNOWN",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "RETROSPECTIVE / TARGET_EXPOSED / NONSCORING",
        "eligible_uses": ["qualified S1 graphical windows with explicit support and coverage",
                          "unchanged Figure3 S-A qualitative gate"],
        "blocked_uses": ["run_index as shot identity", "legacy S1 values", "S-B quantitative gate",
                         "intrinsic permeability inference", "physical validation"],
        "missing_joins": ["persistent full trajectories and complete condition envelopes",
                          "pump events, clock alignment, measured pressure, balance/derivative response"],
        "last_qualified_task": "SCI-MD-SMRKE-TRANSIENT-HYDRAULICS-001",
        "last_qualified_commit": None,
        "notes": ["Same smrke2024/figures family, corrected S1 subset; no new physical experiment.",
                  "S1 full0-7 g/s scale; nondata legend/text rejected; native coordinates retained.",
                  "Figure3 bytes/ordering and accepted endpoint evidence preserved at historical identities.",
                  "Graphical reading bounds are not replicate or laboratory uncertainty; PHYSICAL_VALIDATION=NOT_ESTABLISHED."]
    })
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
        "eligible_uses": ["fixed-density force and fixed-force density graphical readings", "same-sample force increments and limited additive-force-offset null", "same-force-interval density increments and finite additive-density-offset exclusion under retained graphical-reading contract", "pure positive sample-specific density-scaling exclusion at six retained forces", "finite graphical compatibility with sample-specific constant density baseline and positive amplitude by one 72-reading witness"],
        "conditionally_eligible_uses": ["horizontal density-shift exclusion only under a common single-valued inverse loading branch over tested forces"],
        "blocked_uses": ["population significance", "intrinsic modulus or constitutive law", "wet-bed or hydraulic inference", "exclusion of arbitrary non-injective horizontal-shift curves with sample-dependent branch choices", "exclusion of both force and density offsets simultaneously", "exclusion of general density transformations, relative-initial-state strain or broader preparation explanations beyond the tested pure positive scaling family", "identical actual or continuous normalized material response shapes", "independent campaign replication", "physical validation"],
        "missing_joins": ["native force/displacement records", "instrument/sample IDs", "load-cell/displacement calibration and compliance", "force zero and initial state", "individual preparation and loading histories", "journal Figure7 path membership or averaging"],
        "coverage": "12 graphical samples; 76 unique chunks painted twice; #352 retains 156 sample requests and 12 cross-grind comparisons; density-shift analysis retains 72 readings, 180 increments, 990 sample contrasts, 60 complete envelopes, 90 overlapping grind contrasts; all new rows fully supported with zero ambiguity; primary 5/66 and overall 10/990 sample separations; density normalization: 72 readings, 180 ratios, 990 sample contrasts, 60 complete envelopes, 90 grind comparisons; pure scaling 1/66 primary and 1/990 overall separations, no whole-grind ordering; affine compatibility: one common six-level vector and 72 certified points",
        "campaign": "existing Corrochano thesis/journal/Melrose lineage; no new independent campaign",
        "last_qualified_task": "SCI-MD-CORROCHANO-DENSITY-NORMALIZATION-001",
    }
    # S2 eligibility is dataset-scoped; existing Figure 2/5 evidence is unchanged.
    s2_id = "cameron2020/figS2_pressure_tamp"
    s2_row = next(row for row in rows if row["dataset_id"] == s2_id)
    families["CAMERON2020"].setdefault("dataset_scopes", {})[s2_id] = {
        "source_card": s2_row["source_card"],
        "supplement_card": "docs/cards/cameron2020_si.md",
        "observer": "plotted shot-duration central summaries against native nominal pressure/grind/force groups",
        "source_internal_or_external": "SOURCE_INTERNAL",
        "target_exposure": "TARGET_EXPOSED",
        "validation_strength": s2_row["validation_strength"],
        "physical_validation": "NOT_ESTABLISHED",
        "eligible_uses": ["declared pressure, additive pressure-by-grind and endpoint tamp contrasts under graphical bounds",
                          "descriptive displayed-extent sensitivity where endpoints are recoverable"],
        "blocked_uses": ["automatic minus-one-bar or MachineState conversion", "measured puck pressure-drop law",
                         "permeability or mechanism identification", "replicate/population inference",
                         "Figure 5 repair", "physical validation"],
        "missing_joins": ["exact nominal/applied forces", "pressure node/reference and histories",
                          "S2 per-point replicate count and summary/bar semantics", "shot-clock origin",
                          "four displayed bar extents", "source-specific trajectories and covariance"],
        "coverage": "16 central summaries; 12 bars recovered / 4 missing; 18 contrast IDs per layer; A 18 complete, B 9 complete / 9 incomplete",
        "units": "N; s; native nominal bar; source grinder dial",
        "rights": s2_row["license_access"],
        "result": "docs/analysis/sci_md_cameron_pressure_tamp_001/RESULT.md",
        "last_qualified_task": "SCI-MD-CAMERON-PRESSURE-TAMP-001",
    }
    # Duration eligibility is scoped to the two existing canonical tables. Their
    # historical chemistry/model qualifications and all other datasets stay intact.
    for dataset_id, coverage in [
        ("perticarini2024/ey_tds_cibao", "18 Cibao rows; 12 at 93.4 C and 6 at 90.4 C"),
        ("egidi2024/table2", "12 Modoetia rows; 6 at each temperature; thesis Table 4.3 is the same observations"),
    ]:
        family = family_id(dataset_id)
        families[family].setdefault("dataset_scopes", {})[dataset_id] = {
            "observer": "reported condition duration in seconds; statistic/spread/rounding/clock unspecified",
            "source_internal_or_external": "SOURCE_INTERNAL",
            "target_exposure": "TARGET_EXPOSED",
            "physical_validation": "NOT_ESTABLISHED",
            "eligible_uses": ["retrospective nominal-pressure duration contrasts within coffee-temperature strata",
                              "additive pressure-by-grind contrasts and separate reversal diagnostics",
                              "exact deterministic entrywise perturbation sensitivity; not timing variability"],
            "blocked_uses": ["measured puck pressure-drop or flow calibration", "40/tau as measured flow",
                             "per-shot masses from EY/TDS", "duration n=3 or uncertainty from TDS sigma",
                             "intrinsic permeability/resistance or mechanism inference", "population inference",
                             "independent replication from duplicate publications", "physical validation"],
            "missing_joins": ["duration statistic/spread/rounding/start-stop clock", "duration replicate identities",
                              "actual condition beverage masses", "pressure reference/node/history"],
            "coverage": coverage,
            "campaign": "Perticarini Extraction Procedure 1; egidi2024/table2 is the canonical Modoetia identity",
            "units": "s; degC; native nominal machine bar; ordinal source grind labels",
            "result": "docs/analysis/sci_md_perticarini_pressure_grind_001/RESULT.md",
            "last_qualified_task": "SCI-MD-PERTICARINI-PRESSURE-GRIND-001",
            "prior_use_limit": "EY/TDS qualification and model pressure/temperature prediction strength unchanged",
        }
    return {"schema_version": 1, "manifest_path": "puckworks/data/MANIFEST.csv",
            "manifest_sha256": sha256(MANIFEST), "dataset_count": len(rows),
            "families": [families[k] for k in sorted(families)]}


if __name__ == "__main__":
    OUTPUT.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

"""Target-blind SCI-MD-004 Stage E0 R1 training-bundle producer."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import fmean, stdev

from puckworks.analysis.sci_md_004_target_guard import (
    DENIED_APIS,
    DENIED_RELATIVE_PATHS,
    OPAQUE_METADATA_RELATIVE_PATHS,
    SemanticAccessGuard,
)
from puckworks.models.pannusch2024.closures import TREF_K, diffusion_coeff

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "docs/analysis/sci_md_004_stage_e0"
SCHEMA = "puckworks.sci-md-004-stage-e0-r1-training/v1"
DOSE_G = 20.0
BED_DIAMETER_M = 0.058
BED_HEIGHT_M = 0.015
LIQUID_POROSITY = 0.17
COARSE_INTRAGRANULAR_POROSITY = 0.4
LEGACY_EFFECTIVE_DIFFUSIVITY_M2_S = 1.0e-10

RAW_FRACTIONS = "puckworks/data/schmieder2023/raw_fractions.csv"
AVERAGE_FITS = "puckworks/data/schmieder2023/kinetics_fit_params_avg.csv"
PANNUSCH_PARAMS = "puckworks/data/pannusch2024/table2_fitted_params.csv"
PANNUSCH_GRIND = "puckworks/data/pannusch2024/table2_grind_psi_ds2.csv"
PANNUSCH_RECONSTRUCTION = "puckworks/data/pannusch2024/experimental_kinetics.csv"
MAILLE_TIMES = "puckworks/data/maille2024/Table 6.4 - Model parameter values with 95pct CI R2 and MPE for caffeine and 3-CQA extraction kinetic models.csv"
MAILLE_DIFFUSION = "puckworks/data/maille2024/Table 6.2 - Variable values for estimating Bim and Fom.csv"
SOURCE_PATHS = (
    RAW_FRACTIONS,
    AVERAGE_FITS,
    "puckworks/data/schmieder2023/source/TableS1_ExperimentRawData.xlsx",
    "puckworks/data/schmieder2023/source/foods-12-02871.xml",
    "puckworks/data/schmieder2023/PROVENANCE.md",
    PANNUSCH_PARAMS,
    PANNUSCH_GRIND,
    PANNUSCH_RECONSTRUCTION,
    "puckworks/data/pannusch2024/PROVENANCE.md",
    MAILLE_TIMES,
    MAILLE_DIFFUSION,
    "puckworks/data/maille2024/PROVENANCE.md",
)


def _file(relative: str) -> Path:
    return ROOT / relative


def _hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_csv(relative: str) -> list[dict[str, str]]:
    with _file(relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _csv(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode()


def _json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def build_training_contract() -> dict:
    return {
        "schema_version": SCHEMA,
        "authorization": "SCI-MD-004-STAGE-E0-R1-OWNER-ADJUDICATION-PRESERVE-FAILED-ACCESS-INCIDENT-CLEAN-RESTART-TARGET-ACCESS-TAXONOMY-NO-HOLDOUT-PARAMETERIZATION-CONDITIONAL-CASE-FREEZE-AND-INDEPENDENT-PRE-SCORING-AUDIT-2026-08-24",
        "change_declaration": "NO_GOVERNING_PHYSICS_CHANGE",
        "failed_v1_result_preserved": "SCI_MD_004_STAGE_E0_UNAUTHORIZED_HOLDOUT_ACCESS",
        "primary_training_evidence": "SCHMIEDER_RAW_FRACTIONS",
        "primary_fit_observation": "CONDITION_FRACTION_REPLICATE_MEAN",
        "raw_replicates_role": "SECONDARY_DIAGNOSTIC",
        "inventory_role": "TRAINING_DATA_ESTIMATE_NOT_DIRECT_INITIAL_INVENTORY",
        "pannusch_lineage": "SAME_SCHMIEDER_LINEAGE_NOT_INDEPENDENT",
        "pannusch_reconstruction_role": "ROUND_TRIP_UNIT_AGGREGATION_ONLY_EXCLUDED_FROM_OBJECTIVE",
        "maille_role": "NONADJUDICATIVE_EXTERNAL_PLAUSIBILITY_CHECK",
        "units": {
            "temperature": "K", "flow": "m3/s", "mass": "kg",
            "fraction_concentration": "kg species/kg beverage",
            "inventory": "kg species/kg dry coffee",
        },
        "fraction_coordinate": {
            "source_meaning": "MIDPOINT_PER_SCHMIEDER_EQUATION_1",
            "lower": "midpoint - fraction_mass/2",
            "upper": "midpoint + fraction_mass/2",
            "printed_precision_tolerance_kg": 5e-8,
            "unmeasured_fraction_policy": "PRESERVE_GAPS_NO_INTERPOLATED_OBSERVATIONS",
        },
        "missing_value_policy": "EMPTY_RETAINED_NO_IMPUTATION",
        "rights": {
            "schmieder": "CC-BY DOI 10.3390/foods12152871",
            "pannusch": "CC-BY-NC-3.0 Mendeley 10.17632/y2tz67f6ry.1 / paper CC-BY",
            "maille": "White Rose eTheses table transcription; source PDF not redistributed",
        },
        "sources": [{"path": relative, "sha256": _hash(_file(relative))} for relative in SOURCE_PATHS],
        "claim_ceiling": [
            "TRAINING FIT IS NOT VALIDATION",
            "BLOCKED TRAINING PREDICTION IS NOT AN INDEPENDENT HOLDOUT",
            "ANGELONI REMAINS THE PROTECTED EXTERNAL ENDPOINT HOLDOUT",
        ],
    }


def build_schmieder_fraction_table() -> list[dict]:
    source_hash = _hash(_file(RAW_FRACTIONS))
    cumulative: defaultdict[tuple[int, int, str], float] = defaultdict(float)
    previous: dict[tuple[int, int], tuple[int, float | None]] = {}
    normalized = []
    for source_line, row in enumerate(_read_csv(RAW_FRACTIONS), start=2):
        experiment = int(float(row["exp"]))
        replicate = int(float(row["rep"]))
        fraction = int(float(row["fraction"]))
        mass_g = float(row["mass_fraction_g"]) if row["mass_fraction_g"] else None
        midpoint_g = float(row["mass_accumulated_g"]) if row["mass_accumulated_g"] else None
        lower_g = None if mass_g is None or midpoint_g is None else midpoint_g - mass_g / 2
        upper_g = None if mass_g is None or midpoint_g is None else midpoint_g + mass_g / 2
        trace_key = (experiment, replicate)
        if trace_key not in previous:
            contiguity = "FIRST_MEASURED_FRACTION"
        else:
            prior_fraction, prior_upper = previous[trace_key]
            if fraction != prior_fraction + 1:
                contiguity = "SOURCE_UNMEASURED_FRACTION_GAP"
            elif lower_g is None or prior_upper is None:
                contiguity = "UNVERIFIABLE_SOURCE_MISSING_MASS_COORDINATE"
            elif abs(lower_g - prior_upper) <= 5e-5:
                contiguity = "CONTIGUOUS_WITHIN_PRINTED_PRECISION"
            else:
                contiguity = "SOURCE_CONTIGUITY_ANOMALY"
        previous[trace_key] = (fraction, upper_g)
        for species, column in (
            ("caffeine", "c_caffeine_mg_g"),
            ("trigonelline", "c_trigonelline_mg_g"),
        ):
            concentration = float(row[column]) if row[column] else None
            species_mass = None if mass_g is None or concentration is None else mass_g * concentration * 1e-6
            if species_mass is not None:
                cumulative[(experiment, replicate, species)] += species_mass
            normalized.append({
                "experiment_id": experiment,
                "replicate_id": replicate,
                "fraction_id": fraction,
                "species_id": species,
                "temperature_K": float(row["temp_set_C"]) + 273.15,
                "flow_m3_s": float(row["flow_set_ml_s"]) * 1e-6,
                "grind_source": row["grind_level_set"],
                "fraction_mass_kg": "" if mass_g is None else mass_g * 1e-3,
                "accumulated_mass_coordinate_kg": "" if midpoint_g is None else midpoint_g * 1e-3,
                "fraction_lower_mass_kg": "" if lower_g is None else lower_g * 1e-3,
                "fraction_upper_mass_kg": "" if upper_g is None else upper_g * 1e-3,
                "source_concentration_mg_g": row[column],
                "concentration_kg_per_kg_beverage": "" if concentration is None else concentration * 1e-3,
                "fraction_species_mass_kg": "" if species_mass is None else species_mass,
                "cumulative_measured_fraction_species_mass_kg": "" if species_mass is None else cumulative[(experiment, replicate, species)],
                "coordinate_semantics": "FRACTION_MASS_MIDPOINT",
                "contiguity_status": contiguity,
                "source_file": RAW_FRACTIONS,
                "source_row": source_line,
                "source_hash": source_hash,
                "evidence_status": "PRIMARY_DIRECT_MEASUREMENT",
            })
    return sorted(normalized, key=lambda item: (
        item["experiment_id"], item["replicate_id"], item["fraction_id"], item["species_id"],
    ))


def build_fraction_summary() -> list[dict]:
    grouped: defaultdict[tuple[int, int, str], list[dict]] = defaultdict(list)
    for row in build_schmieder_fraction_table():
        grouped[(row["experiment_id"], row["fraction_id"], row["species_id"])].append(row)
    summary = []
    for (experiment, fraction, species), rows in sorted(grouped.items()):
        values = [float(row["concentration_kg_per_kg_beverage"]) for row in rows if row["concentration_kg_per_kg_beverage"] != ""]
        summary.append({
            "experiment_id": experiment,
            "fraction_id": fraction,
            "species_id": species,
            "replicate_count": len(rows),
            "nonmissing_count": len(values),
            "missing_count": len(rows) - len(values),
            "mean_concentration_kg_per_kg_beverage": "" if not values else fmean(values),
            "sample_sd_concentration_kg_per_kg_beverage": "" if len(values) < 2 else stdev(values),
            "minimum_concentration_kg_per_kg_beverage": "" if not values else min(values),
            "maximum_concentration_kg_per_kg_beverage": "" if not values else max(values),
            "source_row_set": ";".join(str(row["source_row"]) for row in rows),
        })
    return summary


def build_schmieder_inventory_table() -> list[dict]:
    fit_rows = {(int(row["exp"]), row["component"]): row for row in _read_csv(AVERAGE_FITS)}
    first_fractions: defaultdict[tuple[int, str], list[dict]] = defaultdict(list)
    for row in build_schmieder_fraction_table():
        if row["fraction_id"] == 1:
            first_fractions[(row["experiment_id"], row["species_id"])].append(row)
    pannusch = {row["solute"]: row for row in _read_csv(PANNUSCH_PARAMS)}
    solid_phase_volume = math.pi * (BED_DIAMETER_M / 2) ** 2 * BED_HEIGHT_M * (1 - LIQUID_POROSITY)
    result = []
    for key, rows in sorted(first_fractions.items()):
        experiment, species = key
        fit = fit_rows[key]
        c0_mg_g = float(fit["c0"])
        lambda_g = float(fit["lambda_g"])
        first_mass_g = fmean(float(row["fraction_mass_kg"]) * 1e3 for row in rows)
        first_species_mg = fmean(
            float(row["fraction_mass_kg"]) * 1e3 * float(row["source_concentration_mg_g"])
            for row in rows
        )
        tail_species_mg = c0_mg_g * lambda_g * math.exp(-first_mass_g / lambda_g)
        asymptotic_species_mg = first_species_mg + tail_species_mg
        inventory_mg_g = asymptotic_species_mg / DOSE_G
        pannusch_cs0_kg_m3 = float(pannusch[species]["c_s0_mg_mL"])
        pannusch_inventory_mg_g = pannusch_cs0_kg_m3 * solid_phase_volume * 1e6 / DOSE_G
        result.append({
            "experiment_id": experiment,
            "species_id": species,
            "source_quantity": "SCHMIEDER_EQ3_ASYMPTOTIC_EXTRACTABLE_MASS",
            "c0_outlet_concentration_mg_per_g_beverage": c0_mg_g,
            "lambda_beverage_mass_g": lambda_g,
            "mean_first_fraction_species_mass_mg": first_species_mg,
            "fitted_tail_species_mass_mg": tail_species_mg,
            "asymptotic_extractable_species_mass_mg": asymptotic_species_mg,
            "dose_dry_coffee_g": DOSE_G,
            "inventory_mg_species_per_g_dry_coffee": inventory_mg_g,
            "inventory_mass_fraction_kg_per_kg_dry_coffee": inventory_mg_g * 1e-3,
            "status": "TRAINING_DATA_ESTIMATE",
            "direct_initial_inventory_measurement": False,
            "pannusch_initial_solid_concentration_kg_per_m3_solid_phase": pannusch_cs0_kg_m3,
            "pannusch_implied_inventory_mg_per_g_dry_coffee": pannusch_inventory_mg_g,
            "pannusch_to_schmieder_ratio": pannusch_inventory_mg_g / inventory_mg_g,
            "crosscheck": "UNITS_CLOSE_PHASE_DEFINITIONS_EXPLICIT",
        })
    return result


def build_pannusch_scaling_table() -> list[dict]:
    grind = next(row for row in _read_csv(PANNUSCH_GRIND) if float(row["grind"]) == 1.7)
    reference_caffeine_d = float(diffusion_coeff(TREF_K, "caffeine"))
    scale = LEGACY_EFFECTIVE_DIFFUSIVITY_M2_S / reference_caffeine_d
    result = []
    for row in _read_csv(PANNUSCH_PARAMS):
        species = row["solute"]
        if species not in {"caffeine", "trigonelline"}:
            continue
        molecular = float(diffusion_coeff(TREF_K, species))
        result.append({
            "species_id": species,
            "A1": row["A1"], "B1": row["B1"], "A2": row["A2"], "B2": row["B2"],
            "K_ref": row["K_ref"], "gamma_K": row["gamma"], "temperature_reference_K": TREF_K,
            "molecular_diffusivity_reference_m2_s": molecular,
            "effective_diffusivity_scale_a_D": scale,
            "effective_diffusivity_reference_m2_s": scale * molecular,
            "fine_particle_diameter_m": 24e-6,
            "coarse_particle_diameter_m": float(grind["d_s2_um"]) * 1e-6,
            "central_fine_volume_fraction": grind["psi"],
            "coarse_intragranular_porosity": COARSE_INTRAGRANULAR_POROSITY,
            "parameter_status": "SAME_LINEAGE_SCALING_PRIOR_NOT_UNIVERSAL",
            "diffusivity_status": "PROXY_FIXED_NOT_FITTED",
            "reconstructed_kinetics_objective_role": "EXCLUDED_FROM_OBJECTIVE",
        })
    return result


def build_maille_plausibility_table() -> list[dict]:
    diffusion = {row["Variable"]: row for row in _read_csv(MAILLE_DIFFUSION)}
    return [{
        "sample_id": row["Sample ID"],
        "caffeine_lambda_fast_s": row["Caffeine lambda_fast (s)"],
        "caffeine_lambda_slow_s": row["Caffeine lambda_slow (s)"],
        "caffeine_r2": row["Caffeine R2"],
        "caffeine_mpe_pct": row["Caffeine MPE (%)"],
        "maille_effective_diffusivity_m2_s": diffusion["D_eff"]["Value"],
        "status": "NONADJUDICATIVE_EXTERNAL_PLAUSIBILITY_CHECK",
        "limitations": "BATCH_WELL_MIXED_COARSE_GRIND_NOT_ESPRESSO_PRESSURE_OR_FLOW_VALIDATION",
    } for row in _read_csv(MAILLE_TIMES)]


def target_access_policy() -> dict:
    return {
        "schema_version": "puckworks.sci-md-004-stage-e0-r1-target-policy/v1",
        "failed_v1_incident": "EXECUTION_OF_TARGET_TOUCHING_STAGE_A_INTEGRITY_TEST",
        "failed_v1_result": "SCI_MD_004_STAGE_E0_UNAUTHORIZED_HOLDOUT_ACCESS",
        "semantic_target_access": "PROHIBITED",
        "opaque_target_metadata_access": "PERMITTED_FILENAME_HASH_ROW_COUNT_CLASSIFICATION_FLAG_SCHEMA_ONLY",
        "automated_target_integrity_qa_read": "POST_CANDIDATE_FREEZE_SEPARATE_PROCESS_ONLY",
        "protected_scoring_access": "UNAUTHORIZED_IN_STAGE_E0_R1",
        "denied_paths": list(DENIED_RELATIVE_PATHS),
        "denied_apis": list(DENIED_APIS),
        "opaque_metadata_paths": list(OPAQUE_METADATA_RELATIVE_PATHS),
        "integrity_test_marker": "protected_target_integrity",
        "integrity_test_files": [
            "tests/test_data_loaders.py",
            "tests/test_paper_a_model_contract.py",
            "tests/test_paper_a_source_observations.py",
            "tests/test_paper_a_source_schema.py",
            "tests/test_paper_a_transfer_contract.py",
            "tests/test_sci_md_004_stage_a.py",
        ],
    }


def _contract_markdown() -> bytes:
    return b"""# SCI-MD-004 Stage E0 R1 target-blind training contract

Raw Schmieder fraction measurements are the primary measured evidence. Replicate means at each measured condition/fraction are primary fitting observations. The derived asymptotic inventories are same-lineage training estimates, not direct initial-inventory measurements. Pannusch reconstructed kinetics are excluded from the objective. Maill\xc3\xa9 is nonadjudicative plausibility evidence.

TRAINING FIT IS NOT VALIDATION

BLOCKED TRAINING PREDICTION IS NOT AN INDEPENDENT HOLDOUT

ANGELONI REMAINS THE PROTECTED EXTERNAL ENDPOINT HOLDOUT
"""


def write_bundle(destination: str | Path = DEFAULT_OUTPUT) -> dict[str, str]:
    output = Path(destination)
    output.mkdir(parents=True, exist_ok=True)
    with SemanticAccessGuard() as guard:
        artifacts = {
            "STAGE_E0_R1_TRAINING_CONTRACT.md": _contract_markdown(),
            "training_contract.json": _json(build_training_contract()),
            "schmieder_species_fractions_long.csv": _csv(build_schmieder_fraction_table()),
            "schmieder_fraction_summary.csv": _csv(build_fraction_summary()),
            "schmieder_training_inventories.csv": _csv(build_schmieder_inventory_table()),
            "pannusch_scaling_priors.csv": _csv(build_pannusch_scaling_table()),
            "maille_caffeine_plausibility.csv": _csv(build_maille_plausibility_table()),
            "target_access_policy.json": _json(target_access_policy()),
        }
        for name, content in artifacts.items():
            (output / name).write_bytes(content)
        access = guard.manifest()
    access_bytes = _json(access)
    (output / "target_blind_file_access_manifest.json").write_bytes(access_bytes)
    artifacts["target_blind_file_access_manifest.json"] = access_bytes
    hashes = {name: hashlib.sha256(content).hexdigest() for name, content in sorted(artifacts.items())}
    manifest = {
        "schema_version": SCHEMA,
        "deterministic": True,
        "semantic_target_access": False,
        "sources": build_training_contract()["sources"],
        "artifacts": hashes,
    }
    (output / "bundle_manifest.json").write_bytes(_json(manifest))
    return {**hashes, "bundle_manifest.json": _hash(output / "bundle_manifest.json")}


def verify_bundle(destination: str | Path = DEFAULT_OUTPUT) -> bool:
    output = Path(destination)
    manifest = json.loads((output / "bundle_manifest.json").read_text(encoding="utf-8"))
    if manifest["semantic_target_access"] is not False:
        raise ValueError("SEMANTIC_TARGET_ACCESS_FLAG_INVALID")
    for source in manifest["sources"]:
        if _hash(_file(source["path"])) != source["sha256"]:
            raise ValueError("SOURCE_HASH_MISMATCH:" + source["path"])
    for name, expected in manifest["artifacts"].items():
        if _hash(output / name) != expected:
            raise ValueError("BUNDLE_HASH_MISMATCH:" + name)
    names = {path.name.casefold() for path in output.iterdir()}
    if any(Path(path).name.casefold() in names for path in DENIED_RELATIVE_PATHS):
        raise ValueError("PROTECTED_TARGET_IN_TRAINING_BUNDLE")
    return True


if __name__ == "__main__":
    write_bundle()
    verify_bundle()

import json
from pathlib import Path

from tools import build_local_corpus_family_index as builder
from tools import validate_local_corpus_coverage as validator

ROOT = Path(__file__).resolve().parents[1]


def test_generated_index_is_current_and_coverage_valid():
    committed = json.loads((ROOT / "puckworks/data/LOCAL_CORPUS_FAMILY_INDEX.json").read_text())
    assert committed == builder.build()
    assert validator.validate() == []


def test_reviewed_special_authorities_are_narrow_and_explicit():
    index = builder.build()
    families = {item["family_id"]: item for item in index["families"]}
    assert len(families) == 39
    assert set(families["telisromero2001"]["manifest_dataset_ids"]) == {
        "g10_liquor_rheology/telisromero2001_closures",
        "g10_liquor_rheology/telisromero2001_tables",
    }
    assert families["telisromero2001"]["source_registration"].startswith("SOURCE_CARD:")
    assert "DIRECT_ROW_LEVEL_FUSION_AS_ONE_COMMON_VALIDATION_SET" in families["wadsworth2026"]["limits"]
    assert "DIRECT_ROW_LEVEL_FUSION_AS_ONE_COMMON_VALIDATION_SET" in families["vacaguerra2023a"]["limits"]
    wasz = families["waszkiewicz2025"]
    assert any("56" in item and "11" in item for item in wasz["limits"])


def test_visualizer_permission_and_interpretation():
    status = json.loads((ROOT / "puckworks/data/VISUALIZER_API_PERMISSION_STATUS.json").read_text())
    records = {item["corpus_id"]: item for item in status["corpus_records"]}
    assert records["VISUALIZER_COFFEE_API_CRAWL_2026_07_15"]["unique_records"] == 23169
    assert records["VISUALIZER_COFFEE_API_CRAWL_2026_07_15"]["raw_redistribution"] is False
    assert records["VISUALIZER_COFFEE_API_CRAWL_2026_07_15"]["private_data_authority"] is False
    assert records["VISUALIZER_API_REFRESH"]["access_status"].startswith("PERMISSIONED_RATE_LIMITED")
    assert status["tds_ey"]["plausible_nonzero_tds_before_joint_consistency_checks"] == 8
    assert status["tds_ey"]["plausible_nonzero_ey_before_joint_consistency_checks"] == 9
    assert status["tds_ey"]["population_chemistry_ready"] is False
    assert status["hydraulic_evidence"] == "DESCRIPTIVE_APPARENT_RESISTANCE_EVOLUTION_MOTIVATION"

"""Community protocol + submission templates and their validator (Phase 4, #46).

Offline + deterministic. The template bundle + protocol packs exist; the submission validator accepts a
valid (synthetic) package and rejects a missing licence, missing calibration, non-monotonic time, a
duplicate shot id, a checksum mismatch, and a missing chemistry value with no status (never inferred as
zero); the synthetic fixture is clearly labelled and excluded from the data manifest / scientific gates.
"""
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_TPL = _ROOT / "docs" / "data_requests" / "templates"
_FIX = _TPL / "fixtures" / "synthetic"
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra")
import experimental_data_needs as EDN  # noqa: E402


def test_template_bundle_and_protocol_packs_exist():
    for f in ("campaign_metadata.yml", "apparatus.yml", "calibration.csv", "shot_metadata.csv",
              "shot_timeseries.csv", "fraction_metadata.csv", "chemistry_measurements.csv",
              "exclusions.csv", "file_manifest.csv", "README.md"):
        assert (_TPL / f).exists(), f
    protos = _ROOT / "docs" / "data_requests" / "protocols"
    for p in ("EXP-001", "EXP-002", "EXP-005", "EXP-006"):
        assert (protos / f"protocol_{p}.md").exists()
    # EXP-005 indexes the existing kappa(t) protocol rather than rewriting it
    assert "PROTOCOL_kappa_t_discrimination.md" in (protos / "protocol_EXP-005.md").read_text()


def test_valid_synthetic_package_passes():
    assert EDN.validate_submission(_FIX) == []


def _copy(tmp_path) -> Path:
    dst = tmp_path / "sub"
    shutil.copytree(_FIX, dst)
    return dst


def test_missing_license_fails(tmp_path):
    d = _copy(tmp_path)
    meta = (d / "campaign_metadata.yml").read_text().replace("data_license: CC0",
                                                             "data_license: LICENSE_PLACEHOLDER")
    (d / "campaign_metadata.yml").write_text(meta)
    assert any("data_license" in p for p in EDN.validate_submission(d))


def test_missing_calibration_file_fails(tmp_path):
    d = _copy(tmp_path)
    (d / "calibration.csv").unlink()
    assert any("calibration.csv" in p for p in EDN.validate_submission(d))


def test_nonmonotonic_time_fails(tmp_path):
    d = _copy(tmp_path)
    ts = (d / "shot_timeseries.csv").read_text().splitlines()
    ts.append("SHOT1,0.5,7.0,measured,2.0,1.5,scale,93,raw")   # goes back in time for SHOT1
    (d / "shot_timeseries.csv").write_text("\n".join(ts) + "\n")
    assert any("not monotonic" in p for p in EDN.validate_submission(d))


def test_duplicate_shot_id_fails(tmp_path):
    d = _copy(tmp_path)
    sm = (d / "shot_metadata.csv").read_text().splitlines()
    sm.append(sm[1])                                     # duplicate the first data row (SHOT1)
    (d / "shot_metadata.csv").write_text("\n".join(sm) + "\n")
    assert any("duplicate shot_id" in p for p in EDN.validate_submission(d))


def test_checksum_mismatch_fails(tmp_path):
    d = _copy(tmp_path)
    # tamper a manifested file without updating its checksum
    (d / "exclusions.csv").write_text("campaign_id,shot_id,replicate_id,exclusion_reason,recorded_by\n"
                                      "EXP-001,SHOT1,1,tampered,x\n")
    assert any("checksum mismatch" in p for p in EDN.validate_submission(d))


def test_missing_chemistry_value_is_not_inferred_as_zero(tmp_path):
    d = _copy(tmp_path)
    (d / "chemistry_measurements.csv").write_text(
        "campaign_id,shot_id,fraction_id,species,mass_mg,reference_basis,analytical_method,"
        "detection_limit_mg,recovery_pct,measurement_status\n"
        "EXP-001,SHOT1,F1,caffeine,,beverage_volume,HPLC,0.1,95,\n")   # missing mass, no status
    assert any("no measurement_status" in p for p in EDN.validate_submission(d))


def test_raw_processed_distinction_is_required(tmp_path):
    d = _copy(tmp_path)
    sm = (d / "shot_metadata.csv").read_text().replace(",raw_or_processed", ",rawcol")
    (d / "shot_metadata.csv").write_text(sm)
    assert any("raw_or_processed" in p for p in EDN.validate_submission(d))


def test_report_is_deterministic():
    assert EDN.validate_submission(_FIX) == EDN.validate_submission(_FIX)


def test_synthetic_fixture_is_labelled_and_excluded_from_evidence():
    assert (_FIX / "SYNTHETIC_TEST_FIXTURE").exists()
    assert "SYNTHETIC_TEST_FIXTURE" in (_FIX / "campaign_metadata.yml").read_text()
    # the data manifest never references the synthetic fixture
    manifest = (_ROOT / "puckworks" / "data" / "MANIFEST.csv").read_text(encoding="utf-8")
    assert "synthetic" not in manifest.lower() or "fixtures/synthetic" not in manifest

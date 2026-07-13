from __future__ import annotations

import csv
import importlib.util
import math
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


def _load_validator():
    path = REPO / "tools/validate_replicate_uncertainty.py"
    spec = importlib.util.spec_from_file_location("validate_replicate_uncertainty", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_angeloni_recovered_table_is_complete_and_self_consistent() -> None:
    path = (
        REPO
        / "puckworks/data/angeloni2023/angeloni2023_total_solids_lipids_rsd.csv"
    )
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 132
    assert {row["observable"] for row in rows} == {"total_solids", "total_lipids"}
    assert len({row["sample_id"] for row in rows}) == 66
    assert {row["coffee_species"] for row in rows} == {"Arabica", "Robusta"}

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["sample_id"]] = counts.get(row["sample_id"], 0) + 1
        mean = float(row["mean"])
        rsd = float(row["rsd_percent"])
        reconstructed = float(row["sd_reconstructed"])
        assert math.isclose(reconstructed, abs(mean) * rsd / 100.0, rel_tol=1e-10)
        assert row["source_doi"] == "10.3390/app13042688"
    assert set(counts.values()) == {2}


def test_canonical_uncertainty_validator_accepts_consistent_row(tmp_path: Path) -> None:
    validator = _load_validator()
    path = tmp_path / "valid.csv"
    path.write_text(
        "dataset,condition_id,analyte,observable,mean,unit,n,sd,rsd_percent,"
        "uncertainty_source,source_file,source_table,provenance_note\n"
        "demo,c1,caffeine,cup_concentration,10,mg/L,3,1,10,replicates,raw.xlsx,S1,"
        "sample standard deviation\n",
        encoding="utf-8",
    )
    assert validator.validate(path) == 0


def test_canonical_uncertainty_validator_rejects_unqualified_zero(
    tmp_path: Path,
) -> None:
    validator = _load_validator()
    path = tmp_path / "invalid.csv"
    path.write_text(
        "dataset,condition_id,analyte,observable,mean,unit,n,sd,rsd_percent,"
        "uncertainty_source,source_file,source_table,provenance_note\n"
        "demo,c1,caffeine,cup_concentration,10,mg/L,3,0,0,published,table.pdf,S1,"
        "reported exactly\n",
        encoding="utf-8",
    )
    assert validator.validate(path) == 1


def test_recovered_angeloni_canonical_summary_validates() -> None:
    validator = _load_validator()
    path = (
        REPO
        / "puckworks/data/angeloni2023/angeloni2023_uncertainty_summary.csv"
    )
    assert validator.validate(path) == 0

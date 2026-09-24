"""Source-contract checks only: these do not test the predictive hypothesis."""
import csv
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from puckworks import data
from puckworks.analysis import maille_transfer as m


def test_compact_artifact_and_source_identity_replay():
    root = Path(__file__).resolve().parents[1]
    bundle = root / "docs/analysis/sci_md_maille_transfer_001"
    assert json.loads((bundle / "RESULT.json").read_text()) == m.audit()
    audit = json.loads((bundle / "AUDIT.json").read_text())
    assert audit["result_sha256"] == hashlib.sha256((bundle / "RESULT.json").read_bytes()).hexdigest()
    for relative, expected in audit["code_sha256"].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == expected


@pytest.fixture
def source_copy(tmp_path, monkeypatch):
    root = tmp_path / "maille2024"
    shutil.copytree(data.MAILLE, root)
    monkeypatch.setattr(data, "MAILLE", root)
    return root


def edit(root, prefix, transform):
    path = next(root.glob(prefix + " *.csv"))
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        fields, rows = reader.fieldnames, list(reader)
    transform(rows)
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_actual_support_is_empirical_but_not_observer_qualified():
    rows, receipt = m.analysis_view()
    assert len(rows) == 105
    assert len(receipt["reference_summaries"]) == 45
    result = m.audit()
    assert result["observation_kinds"] == {
        "measured_comparative_value_approximate_time": 75,
        "mean_of_three_normalized_replicates": 30,
    }
    assert len(result["curves"]) == 15
    assert all(c["early_n"] == 5 and c["late_n"] == 2 for c in result["curves"])
    assert result["executed_folds"] == result["predictions"] == result["optimizer_attempts"] == 0
    assert result["scientific_verdict"] == "BLOCKED_SOURCE_CONTRACT"
    assert receipt["descriptors"]["Omega_C"]["D43_um"] == 782
    assert receipt["descriptors"]["Omega_A"]["phi"] == 0.356
    assert all(not r["primary_eligible"] and r["replicate_id"] is None for r in rows)


def test_pooled_summaries_do_not_reconstruct_the_source_operator():
    result = m.audit()
    diagnostic = next(r for r in result["pooled_denominator_diagnostic"]
                      if r["material_id"] == "Omega_B" and r["analyte"] == "Quinic Acid")
    assert diagnostic["table510_minus_ratio_of_pooled_means"] == pytest.approx(0.9 - 172 / 181)
    assert abs(diagnostic["table510_minus_ratio_of_pooled_means"]) > 0.05
    example = m.marginal_summary_counterexample()
    assert example["difference"] == pytest.approx(10 / 297)


@pytest.mark.parametrize("prefix", ["Table 5.1", "Table 5.4", "Table 6.3", "Table 5.11"])
def test_missing_material_join_fails(source_copy, prefix):
    edit(source_copy, prefix, lambda rows: rows.pop(0))
    with pytest.raises(m.SourceContractError, match="missing material join"):
        m.analysis_view()


@pytest.mark.parametrize("prefix", ["Table 5.1", "Table 5.4", "Table 6.3", "Table 5.11"])
def test_duplicate_material_join_fails(source_copy, prefix):
    edit(source_copy, prefix, lambda rows: rows.append(rows[0].copy()))
    with pytest.raises(m.SourceContractError, match="duplicate material"):
        m.analysis_view()


def test_no_undocumented_material_alias(source_copy):
    edit(source_copy, "Table 5.1", lambda rows: rows[0].update({"Sample ID": "OmegaA"}))
    with pytest.raises(m.SourceContractError, match="ambiguous material"):
        m.analysis_view()


def test_duplicate_time_lineage_fails(source_copy):
    edit(source_copy, "Table 5.10", lambda rows: rows.append(rows[0].copy()))
    with pytest.raises(m.SourceContractError, match="duplicate observation lineage"):
        m.analysis_view()


def test_ambiguous_file_fails_before_first_match_loader(source_copy):
    shutil.copy(next(source_copy.glob("Table 5.4 *.csv")), source_copy / "Table 5.4 duplicate.csv")
    with pytest.raises(m.SourceContractError, match="exactly one source file"):
        m.analysis_view()


@pytest.mark.parametrize("value", ["nan", "inf", "-0.1", "1.01", "bad"])
def test_impossible_response_fails(source_copy, value):
    edit(source_copy, "Table 5.10", lambda rows: rows[0].update({"Caffeine Omega_A": value}))
    with pytest.raises(m.SourceContractError):
        m.analysis_view()


@pytest.mark.parametrize("prefix,key,value", [
    ("Table 5.4", "D[4,3] Vol Mean (um)", 0),
    ("Table 6.3", "phi", 1.1),
    ("Table 5.11", "Caffeine 600s sd (mg per L)", -1),
])
def test_impossible_descriptors_or_uncertainty_fail(source_copy, prefix, key, value):
    edit(source_copy, prefix, lambda rows: rows[0].update({key: value}))
    with pytest.raises(m.SourceContractError):
        m.analysis_view()


def test_absent_cells_are_reported_not_imputed(source_copy):
    edit(source_copy, "Table 5.10", lambda rows: rows[0].update({"Caffeine Omega_A": "*"}))
    rows, receipt = m.analysis_view()
    assert len(rows) == 104 and len(receipt["missing_cells"]) == 1
    assert m.audit()["observed_cells"] == 104


def test_missing_late_window_is_explicit(source_copy):
    edit(source_copy, "Table 5.10", lambda rows: rows.__delitem__(slice(5, None)))
    result = m.audit()
    assert result["missing_times"] == [60, 180]
    assert not any(c["both_windows_present"] for c in result["curves"])


def test_fitted_kinetics_and_dense_figures_are_never_loaded(monkeypatch):
    def forbidden():
        raise AssertionError("forbidden source reached the primary adapter")
    for name in ("maille_kinetics_caffeine_3cqa", "maille_kinetics_organic_acids",
                 "maille_extraction_curves"):
        monkeypatch.setattr(data, name, forbidden)
    assert m.audit()["observed_cells"] == 105


def test_response_changes_cannot_unlock_scoring(source_copy):
    edit(source_copy, "Table 5.10", lambda rows: rows[0].update({"Caffeine Omega_A": 0.99}))
    assert m.audit()["scientific_verdict"] == m.STATUS
    with pytest.raises(m.SourceContractError, match=m.STATUS):
        m.require_scoring_eligible()
    # No claim of a fitted-parameter leakage test: fitting never became eligible.

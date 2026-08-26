import csv
import hashlib
import json
import shutil
from pathlib import Path

import pytest

from puckworks.analysis import sci_md_007_r2 as r2


def copy_search(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    data.mkdir(parents=True)
    for name in ("search_log.csv", "search_results.csv", "citation_passes.csv"):
        shutil.copyfile(r2.DATA / name, data / name)
    return data


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write(path: Path, values: list[dict[str, str]]) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(values[0]))
        writer.writeheader()
        writer.writerows(values)


def closed(data: Path) -> dict:
    return r2.search_complete(r2.read_csv("sources.csv"), data=data)


def test_current_search_relational_closure_exact_counts():
    result = closed(r2.DATA)
    assert result["pass"]
    assert (result["searches"], result["result_records"]) == (24, 400)
    assert (result["unique_candidates"], result["duplicates"]) == (269, 131)
    assert result["unresolved_candidates"] == 0
    assert len(result["query_provider_audit"]) == 24
    assert len(result["citation_pass_audit"]) == 12


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("provider", "Wrong", "provider/query mismatch"),
        ("query", "wrong query", "provider/query mismatch"),
        ("result_limit", "19", "result limit mismatch"),
        ("result_limit", "word", "nonnegative integer"),
        ("results_returned", "-1", "nonnegative integer"),
        ("results_returned", "21", "returned above limit"),
        ("results_screened", "19", "screened/returned mismatch"),
        ("unique_candidates_added", "19", "unique_candidates_added mismatch"),
        ("duplicates", "1", "duplicates mismatch"),
        ("inaccessible_candidates", "1", "inaccessible_candidates mismatch"),
        ("out_of_scope_candidates", "99", "out_of_scope_candidates mismatch"),
        ("execution_date", "2026-08-26", "invalid execution date"),
    ],
)
def test_search_log_tamper_fails(tmp_path, field, value, reason):
    data = copy_search(tmp_path)
    path = data / "search_log.csv"
    values = rows(path)
    values[0][field] = value
    write(path, values)
    assert reason in " ".join(closed(data)["reasons"])


def test_missing_duplicate_and_unexpected_search_ids_fail(tmp_path):
    for mode in ("missing", "duplicate", "unexpected"):
        data = copy_search(tmp_path / mode)
        path = data / "search_log.csv"
        values = rows(path)
        if mode == "missing":
            values.pop()
        elif mode == "duplicate":
            values.append(dict(values[0]))
        else:
            values[0]["search_id"] = "unexpected"
        write(path, values)
        assert not closed(data)["pass"]


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (lambda values: values.pop(), "result row count mismatch"),
        (lambda values: values[1].update(result_rank="1"), "ranks not unique contiguous"),
        (lambda values: values[0].update(provider="Wrong"), "result provider/query mismatch"),
        (lambda values: values[0].update(query="Wrong"), "result provider/query mismatch"),
        (lambda values: values[0].update(retrieval_date="2026-08-26"), "invalid retrieval date"),
        (lambda values: values[0].update(screening_state=""), "nonterminal screening state"),
        (
            lambda values: values[0].update(screening_state="UNRESOLVED_PENDING_SCREEN"),
            "nonterminal screening state",
        ),
        (lambda values: values[0].update(candidate_id=""), "blank candidate_id"),
        (lambda values: values[0].update(duplicate_of="missing"), "candidate lineage"),
    ],
)
def test_search_result_tamper_fails(tmp_path, mutation, reason):
    data = copy_search(tmp_path)
    path = data / "search_results.csv"
    values = rows(path)
    mutation(values)
    write(path, values)
    assert reason in " ".join(closed(data)["reasons"])


def test_duplicate_only_and_multiple_introduction_lineages_fail(tmp_path):
    for mode in ("duplicate_only", "multiple_introduction"):
        data = copy_search(tmp_path / mode)
        path = data / "search_results.csv"
        values = rows(path)
        candidate = values[0]["candidate_id"]
        occurrence = next(row for row in values if row["candidate_id"] == candidate)
        if mode == "duplicate_only":
            occurrence["duplicate_of"] = candidate
        else:
            duplicate = next(row for row in values if row["duplicate_of"])
            duplicate["duplicate_of"] = ""
        write(path, values)
        assert not closed(data)["pass"]


def test_identity_normalization_and_conflict_detection():
    assert r2.normalize_doi("HTTPS://DOI.ORG/10.1234/ABC.") == "10.1234/abc"
    assert r2.normalize_doi("doi: 10.1234/AbC") == "10.1234/abc"
    assert r2.normalize_text(" A—Coffee:  Study ") == "a coffee study"
    base = {
        "candidate_id": "c1",
        "duplicate_of": "",
        "doi_or_stable_id": "10.1/a",
        "title": "A",
        "year": "2020",
        "authors": "X",
    }
    with pytest.raises(ValueError, match="different identities"):
        r2.resolve_candidate_roots([base, dict(base, duplicate_of="c1", doi_or_stable_id="10.1/b")])


@pytest.mark.parametrize(
    "mutation,reason",
    [
        (
            lambda values: values.__setitem__(
                slice(None),
                [
                    row
                    for row in values
                    if not (
                        row["source_publication_id"] == "bruno2026"
                        and row["direction"] == "BACKWARD"
                    )
                ],
            ),
            "missing BACKWARD pass",
        ),
        (lambda values: values[0].update(rank="21"), "exceeds frozen limit"),
        (lambda values: values[1].update(stable_id=values[0]["stable_id"]), "duplicate citation"),
        (lambda values: values[0].update(screening_state=""), "unterminated citation"),
        (lambda values: values[0].update(retrieval_date="2026-08-26"), "invalid citation"),
    ],
)
def test_citation_pass_tamper_fails(tmp_path, mutation, reason):
    data = copy_search(tmp_path)
    path = data / "citation_passes.csv"
    values = rows(path)
    mutation(values)
    write(path, values)
    assert reason in " ".join(closed(data)["reasons"])


@pytest.mark.parametrize(
    "value,expected",
    [
        ("", False),
        ("unknown", False),
        ("lab_unknown_1", False),
        ("unspecified", False),
        ("lab_a", True),
    ],
)
def test_identified_laboratory_predicate(value, expected):
    assert r2.identified_laboratory(value) is expected


def current_reduction():
    sources = r2.read_csv("sources.csv")
    materials = r2.read_csv("materials.csv")
    observations = r2.read_csv("observations.csv")
    return r2.reduce(sources, materials, observations)


def test_current_independence_and_group_semantics():
    _, edges, gates, _, _, _ = current_reduction()
    for analyte in r2.ANALYTES:
        assert gates[analyte]["F2"]["identified_laboratories"] == 1
        assert gates[analyte]["F2"]["material_roast_units"] == 112
        assert gates[analyte]["F2"]["largest_group_share"] == pytest.approx(67 / 112)
        assert gates[analyte]["F3"]["species"]["Robusta"]["laboratories"] == 1
    assert not any("laboratory_id" in edge["reason"] for edge in edges)
    assert {edge["reason"].split(":")[0] for edge in edges} <= {
        "shared source_publication_id",
        "shared data_lineage_id",
        "shared base_coffee_material_id",
    }


def test_current_f4_executes_every_frozen_primitive():
    _, _, gates, _, _, _ = current_reduction()
    for analyte in r2.ANALYTES:
        gate = gates[analyte]["F4"]
        assert not gate["pass"]
        assert gate["categorical_route"]["species"]["Arabica"]["qualifying_strata_count"] == 0
        assert gate["categorical_route"]["species"]["Robusta"]["qualifying_strata"] == ["medium"]
        quant = gate["quantitative_route"]
        assert quant["material_roast_units"] == 45
        assert quant["validation_groups"] == 2
        assert quant["units_per_species"] == {"Arabica": 3, "Robusta": 33}
        assert quant["within_species_varying_groups"]["Arabica"]["count"] == 1
        assert quant["within_species_varying_groups"]["Robusta"]["count"] == 1
        assert quant["minimum_within_species_varying_groups"] == 1


def test_current_f7_calculates_leakage_and_separates_diagnostics():
    _, _, gates, _, _, _ = current_reduction()
    for analyte in r2.ANALYTES:
        gate = gates[analyte]["F7"]
        assert gate["outer_validation_groups"] == 3
        assert not gate["pass"]
        assert gate["failure_reasons"] == ["outer_validation_groups_below_threshold"]
        assert gate["publication_leakage"] == 0
        assert gate["data_lineage_leakage"] == 0
        assert gate["base_material_leakage"] == 0
        assert gate["species_support_all_folds"] is False
        assert gate["harmonized_roast_category_support_all_folds"] is False
        assert gate["quantitative_metric_type_support_all_folds"] is False


@pytest.mark.parametrize(
    "path,expected",
    [
        (("categorical_route", "pass"), False),
        (("categorical_route", "species", "Arabica", "qualifying_strata_count"), 0),
        (("categorical_route", "species", "Robusta", "qualifying_strata_count"), 1),
        (("quantitative_route", "material_roast_units"), 45),
        (("quantitative_route", "validation_groups"), 2),
        (("quantitative_route", "units_per_species", "Arabica"), 3),
        (("quantitative_route", "units_per_species", "Robusta"), 33),
        (("quantitative_route", "within_species_varying_groups", "Arabica", "count"), 1),
        (("quantitative_route", "within_species_varying_groups", "Robusta", "count"), 1),
        (("quantitative_route", "minimum_within_species_varying_groups"), 1),
    ],
)
def test_f4_current_primitive_regression_is_individually_bound(path, expected):
    _, _, gates, _, _, _ = current_reduction()
    value = gates["caffeine"]["F4"]
    for key in path:
        value = value[key]
    assert value == expected


@pytest.mark.parametrize(
    "field,expected",
    [
        ("outer_validation_groups", 3),
        ("publication_leakage", 0),
        ("data_lineage_leakage", 0),
        ("base_material_leakage", 0),
        ("species_support_all_folds", False),
        ("harmonized_roast_category_support_all_folds", False),
        ("quantitative_metric_type_support_all_folds", False),
    ],
)
def test_f7_current_primitive_regression_is_individually_bound(field, expected):
    _, _, gates, _, _, _ = current_reduction()
    assert gates["trigonelline"]["F7"][field] == expected


def test_generated_artifact_semantic_closure_and_evidence_hashes():
    result = r2.build(check=True)
    assert result["schema_version"] == "1.2.0-R2"
    audit = json.loads((r2.OUT / "r2/R2_CROSS_ARTIFACT_AUDIT.json").read_text())
    assert audit["status"] == "PASS" and all(audit["comparisons"].values())
    independence = rows(r2.OUT / "independence_audit.csv")
    assert {row["laboratories"] for row in independence} == {"1"}
    assert {
        name: hashlib.sha256((r2.DATA / name).read_bytes()).hexdigest()
        for name in ("sources.csv", "materials.csv", "observations.csv")
    } == {
        "sources.csv": "9348b817687a1f3d56d0c1a2841d73d8ed0470530fece7a1acd3c5f2b5a77642",
        "materials.csv": "5864909fc4b8e655ebe82024383e2e9e05fc09786fe746944724ec400f309d1d",
        "observations.csv": "acc14b22cc03f75fb6b1a800d234438bd23ac2f807d99084c47de79cfd5b144f",
    }
    assert result["model_stage"] == "NOT_RUN_FEASIBILITY_FAILED"

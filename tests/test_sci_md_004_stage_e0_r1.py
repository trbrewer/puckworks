import ast
import hashlib
import json
import tempfile
from pathlib import Path

import pytest

from puckworks.analysis import sci_md_004_stage_e0 as stage_e0
from puckworks.analysis import sci_md_004_target_guard as guard


def test_guard_rejects_direct_relative_absolute_traversal_and_case_variants(tmp_path):
    denied = guard.ROOT / guard.DENIED_RELATIVE_PATHS[0]
    attempts = [
        denied,
        guard.DENIED_RELATIVE_PATHS[0],
        guard.ROOT / "docs/analysis/../analysis/sci_md_004/angeloni_targets_long.csv",
        str(denied).upper(),
    ]
    for attempt in attempts:
        with pytest.raises(PermissionError, match=guard.FAILURE):
            guard.assert_semantic_path_allowed(attempt)
    link = tmp_path / "innocent.csv"
    link.symlink_to(denied)
    with pytest.raises(PermissionError, match=guard.FAILURE):
        guard.assert_semantic_path_allowed(link)


def test_guard_rejects_api_configuration_environment_and_subprocess():
    for api in guard.DENIED_APIS:
        with pytest.raises(PermissionError, match=guard.FAILURE):
            guard.assert_api_allowed(api)
    with pytest.raises(PermissionError, match=guard.FAILURE):
        guard.assert_api_allowed("puckworks.analysis.angeloni2023_multispecies")
    target = guard.DENIED_RELATIVE_PATHS[0]
    for value in ({"target_path": target}, {"nested": [target]}, {"TARGET": target}):
        with pytest.raises(PermissionError, match=guard.FAILURE):
            guard.assert_configuration_allowed(value)
    with pytest.raises(PermissionError, match=guard.FAILURE):
        guard.assert_environment_allowed({"STAGE_E0_INPUT": target})
    with pytest.raises(PermissionError, match=guard.FAILURE):
        guard.assert_subprocess_allowed(["python3", "worker.py", target])


def test_guard_allows_input_only_and_opaque_metadata_paths():
    for relative in (*guard.PERMITTED_INPUT_RELATIVE_PATHS, *guard.OPAQUE_METADATA_RELATIVE_PATHS):
        assert guard.assert_semantic_path_allowed(relative) == (guard.ROOT / relative).resolve()


def test_audit_hook_denies_open_and_records_permitted_source():
    allowed = guard.ROOT / stage_e0.RAW_FRACTIONS
    denied = guard.ROOT / guard.DENIED_RELATIVE_PATHS[0]
    with guard.SemanticAccessGuard() as active:
        with allowed.open(encoding="utf-8") as handle:
            assert handle.readline().startswith("exp,")
        with pytest.raises(PermissionError, match=guard.FAILURE):
            denied.open("rb")
    manifest = active.manifest()
    assert manifest["semantic_target_access"] is False
    assert stage_e0.RAW_FRACTIONS in {item["path"] for item in manifest["opened_repository_files"]}


def test_source_counts_missingness_units_bounds_and_replicates():
    assert hashlib.sha256((guard.ROOT / stage_e0.RAW_FRACTIONS).read_bytes()).hexdigest() == "f3511dd46648fb34962c9d774cc901fa65acd7f0caaf130f143e4f04dbb0915f"
    rows = stage_e0.build_schmieder_fraction_table()
    assert len(rows) == 576
    assert len({row["experiment_id"] for row in rows}) == 15
    assert len({(row["experiment_id"], row["replicate_id"]) for row in rows}) == 48
    assert {row["fraction_id"] for row in rows} == {1, 2, 3, 5, 7, 10}
    assert {row["species_id"] for row in rows} == {"caffeine", "trigonelline"}
    assert sum(row["source_concentration_mg_g"] == "" for row in rows) == 4
    assert sum(row["fraction_mass_kg"] == "" for row in rows) == 2
    first = next(row for row in rows if row["experiment_id"] == 1 and row["replicate_id"] == 1 and row["fraction_id"] == 1 and row["species_id"] == "caffeine")
    assert first["fraction_lower_mass_kg"] == pytest.approx(0.0)
    assert first["fraction_upper_mass_kg"] == pytest.approx(0.0058529)
    assert first["concentration_kg_per_kg_beverage"] == pytest.approx(8.79319e-3)
    assert first["fraction_species_mass_kg"] == pytest.approx(5.8529 * 8.79319e-6)
    summary = stage_e0.build_fraction_summary()
    assert len(summary) == 180
    assert any(row["sample_sd_concentration_kg_per_kg_beverage"] != "" for row in summary)


def test_inventory_basis_lineage_diffusivity_and_maille_status():
    inventories = stage_e0.build_schmieder_inventory_table()
    assert len(inventories) == 30
    assert all(row["status"] == "TRAINING_DATA_ESTIMATE" for row in inventories)
    assert all(row["direct_initial_inventory_measurement"] is False for row in inventories)
    assert all(1.0 < row["pannusch_to_schmieder_ratio"] < 2.0 for row in inventories)
    scaling = stage_e0.build_pannusch_scaling_table()
    assert len(scaling) == 2
    assert all(row["diffusivity_status"] == "PROXY_FIXED_NOT_FITTED" for row in scaling)
    assert all(row["reconstructed_kinetics_objective_role"] == "EXCLUDED_FROM_OBJECTIVE" for row in scaling)
    contract = stage_e0.build_training_contract()
    assert contract["pannusch_lineage"] == "SAME_SCHMIEDER_LINEAGE_NOT_INDEPENDENT"
    assert all(row["status"] == "NONADJUDICATIVE_EXTERNAL_PLAUSIBILITY_CHECK" for row in stage_e0.build_maille_plausibility_table())


def test_bundle_is_target_blind_deterministic_and_verifiable():
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        first_hashes = stage_e0.write_bundle(first)
        second_hashes = stage_e0.write_bundle(second)
        assert first_hashes == second_hashes
        assert stage_e0.verify_bundle(first) and stage_e0.verify_bundle(second)
        for name in first_hashes:
            assert (Path(first) / name).read_bytes() == (Path(second) / name).read_bytes()
        policy = json.loads((Path(first) / "target_access_policy.json").read_text())
        assert policy["semantic_target_access"] == "PROHIBITED"
        assert not ({Path(path).name for path in guard.DENIED_RELATIVE_PATHS} & {path.name for path in Path(first).iterdir()})


def test_stage_e0_source_has_no_target_import_or_path_literal():
    source = Path(stage_e0.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names
    } | {
        node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
    }
    assert not any(name.startswith("puckworks.analysis.angeloni2023_multispecies") for name in imported)
    assert not any(name.startswith("puckworks.data.angeloni") for name in imported)
    assert "angeloni_targets_long.csv" not in source


def test_every_target_touching_test_is_marked():
    tests = guard.ROOT / "tests"
    needles = ("build_targets(", "build_contract(", "write_bundle(", "angeloni_targets_long.csv", "angeloni_bioactives")
    offenders = []
    for path in sorted(tests.glob("test_*.py")):
        source = path.read_text(encoding="utf-8")
        if any(needle in source for needle in needles) and "protected_target_integrity" not in source:
            offenders.append(path.name)
    assert offenders == []

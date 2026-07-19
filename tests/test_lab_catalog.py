"""Explicit Guided Pull Laboratory component catalog (PV-19B Phase 3, #70).

Offline + deterministic. CI gate: the committed catalog covers EVERY registered component with an
explicit disposition + adapter capability (never inferred from a stage/kind/role substring); gate ids
resolve; declared runner/adapter ids resolve; rights match the centralized registry; a rights-blocked
component is dispositioned RIGHTS_BLOCKED; and the matrix consumes the catalog rather than a heuristic.
"""
import ast

import pytest

import puckworks
from puckworks.product import lab
from puckworks.product import lab_catalog as C


def test_catalog_covers_every_registered_component_exactly_once():
    entries = C.build_catalog()
    ids = [e.component_id for e in entries]
    assert ids == sorted(ids)
    assert set(ids) == {c.name for c in puckworks.components()}
    assert len(ids) == len(set(ids))


def test_catalog_validation_is_clean():
    assert C.validate_catalog() == []


def test_every_entry_has_explicit_finite_capability():
    for e in C.build_catalog():
        assert e.disposition in lab.DISPOSITIONS
        assert e.adapter_capability in lab.ADAPTER_CAPABILITIES
        assert isinstance(e.gate_ids, tuple)
        # registry-derived fields are present
        assert e.module and e.card_path.startswith("docs/cards/")
        assert e.metadata_review_date == "2026-07-19"


def test_gate_ids_resolve_to_real_gate_functions():
    from puckworks.validation import gates as G
    for e in C.build_catalog():
        for gid in e.gate_ids:
            assert hasattr(G, gid), f"{e.component_id}: unknown gate id {gid}"


def test_declared_runner_and_adapter_ids_resolve():
    from puckworks.product import lab_runners
    for e in C.build_catalog():
        if e.native_runner_id:
            assert lab_runners.has_runner(e.component_id)
        if e.common_scenario_adapter_id:
            assert e.component_id in lab.ADAPTERS


def test_catalog_rights_match_the_centralized_registry():
    from puckworks import rights
    for e in C.build_catalog():
        rec = rights.rights_record(e.component_id)
        assert (e.code_rights_state, e.data_rights_state, e.output_redistribution_state) == (
            rec.code_rights_state, rec.data_rights_state, rec.output_redistribution_state)


def test_rights_blocked_component_is_dispositioned_rights_blocked():
    g = C.catalog_by_id()["grudeva2025.reduced"]
    assert g.disposition == "RIGHTS_BLOCKED" and g.adapter_capability == "RIGHTS_BLOCKED"
    assert g.code_rights_state == "RIGHTS_BLOCKED"
    assert g.public_execution_eligible is False and g.output_publication_eligible is False


def test_cameron_is_the_only_common_scenario_ready_disposition():
    ready = [e.component_id for e in C.build_catalog() if e.disposition == "COMMON_SCENARIO_READY"]
    assert ready == ["cameron2020.extraction_bdf"]


def test_adding_component_without_catalog_entry_fails_validation(monkeypatch):
    # a registered component with no explicit catalog capability is a hard validation failure
    cap = dict(C._CAPABILITY)
    removed = cap.pop("cameron2020.extraction_bdf")
    assert removed
    monkeypatch.setattr(C, "_CAPABILITY", cap)
    problems = C.validate_catalog()
    assert any("cameron2020.extraction_bdf" in p and "no explicit catalog" in p for p in problems)


def test_matrix_consumes_the_catalog_not_a_stage_heuristic():
    # the matrix disposition/adapter capability equal the catalog's for every component
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named"))
    rows = {r["component_id"]: r for r in lab.build_matrix(ex)}
    cat = C.catalog_by_id()
    for cid, e in cat.items():
        row = rows[cid]
        # taichi's disposition may be the env overlay SKIPPED_OPTIONAL_DEPENDENCY; all others equal catalog
        if e.optional_dependency and not lab._optional_dep_available(e.optional_dependency):
            assert row["disposition"] in (e.disposition, "SKIPPED_OPTIONAL_DEPENDENCY")
        else:
            assert row["disposition"] == e.disposition
        assert row["common_scenario_adapter_capability"] == e.adapter_capability


def test_lab_spec_has_no_stage_substring_capability_heuristic():
    # the disposition must not be assigned from a bare stage=="extraction" style comparison in _lab_spec
    src = open(lab.__file__).read()
    tree = ast.parse(src)
    func = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "_lab_spec")
    # no string comparison to a stage/kind literal drives disposition inside _lab_spec
    for node in ast.walk(func):
        if isinstance(node, ast.Compare):
            for c in [node.left, *node.comparators]:
                if isinstance(c, ast.Constant) and c.value in (
                        "extraction", "bed_dynamics", "flow", "infiltration", "machine", "packing",
                        "grind", "synthesis", "reference"):
                    pytest.fail(f"_lab_spec still compares against a stage/kind literal {c.value!r}")

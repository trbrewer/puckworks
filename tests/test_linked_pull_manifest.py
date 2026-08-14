"""Manifest + link-graph contract tests for the Espresso Model Relay (illustrative_linked_pull_v1)."""
from puckworks.product import linked_pull_manifest as M
from puckworks.product.linked_pull_records import LinkKind


def test_manifest_is_clean_against_the_live_registry():
    assert M.verify_linked_pull_manifest() == []


def test_every_registered_component_classified_exactly_once():
    from puckworks import registry
    live = {c.name for c in registry.components()}
    assert set(M.COMPONENT_DISPOSITIONS) == live
    # bound to the LIVE registry: the invariant is exactly-once classification, not a frozen total
    assert len(M.COMPONENT_DISPOSITIONS) == len(live)


def test_manifest_id_is_frozen():
    assert M.MANIFEST_ID == "illustrative_linked_pull_v1"


def test_a_new_registered_component_makes_verification_fail(monkeypatch):
    from puckworks import registry

    class _Fake:
        name = "newcomponent2099.mystery"

    real = registry.components
    monkeypatch.setattr(registry, "components", lambda *a, **k: list(real()) + [_Fake()])
    issues = M.verify_linked_pull_manifest()
    assert any("newcomponent2099.mystery" in s for s in issues)


def test_all_edges_reference_known_components():
    known = set(M.COMPONENT_DISPOSITIONS)
    for e in M.LINK_EDGES:
        assert e.source_component_id is None or e.source_component_id in known
        assert e.target_component_id in known


def test_graph_is_acyclic():
    assert M._acyclicity_errors() == []


def test_grudeva_has_no_edges_for_a_technical_reason_not_a_rights_block():
    from puckworks.product.linked_pull_records import StageStatus
    d = M.COMPONENT_DISPOSITIONS["grudeva2025.reduced"]
    assert d.role_kind != LinkKind.RIGHTS_BLOCKED          # #73 resolved 2026-08-14 by permission
    assert d.intended_status == StageStatus.NOT_SELECTED
    assert "technical limit, not a rights block" in d.role
    for e in M.LINK_EDGES:                                 # the zero-edge topology is unchanged
        assert e.source_component_id != "grudeva2025.reduced"
        assert e.target_component_id != "grudeva2025.reduced"
    assert M.verify_linked_pull_manifest() == []


def test_fast_mode_omits_optional_slow_edges():
    fast = {e.edge_id for e in M.edges_for_mode("fast")}
    ext = {e.edge_id for e in M.edges_for_mode("extended")}
    assert fast < ext
    assert "pack_to_lb" in ext and "pack_to_lb" not in fast


def test_at_least_six_cross_component_handoffs_declared():
    handoffs = [e for e in M.LINK_EDGES if e.kind in (
        LinkKind.DIRECT_MODEL_OUTPUT, LinkKind.DOCUMENTED_ADAPTER, LinkKind.ILLUSTRATIVE_ASSUMPTION,
        LinkKind.OPTIONAL_SLOW_PATH) and e.source_component_id is not None]
    assert len(handoffs) >= 6

"""Manifest + link-graph contract tests for the Espresso Model Relay (illustrative_linked_pull_v1)."""
from puckworks.product import linked_pull_manifest as M
from puckworks.product.linked_pull_records import LinkKind


def test_manifest_is_clean_against_the_live_registry():
    assert M.verify_linked_pull_manifest() == []


def test_every_registered_component_classified_exactly_once():
    from puckworks import registry
    live = {c.name for c in registry.components()}
    assert set(M.COMPONENT_DISPOSITIONS) == live
    assert len(M.COMPONENT_DISPOSITIONS) == len(live) == 25


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


def test_grudeva_is_rights_blocked_with_no_edges():
    d = M.COMPONENT_DISPOSITIONS["grudeva2025.reduced"]
    assert d.role_kind == LinkKind.RIGHTS_BLOCKED
    for e in M.LINK_EDGES:
        assert e.source_component_id != "grudeva2025.reduced"
        assert e.target_component_id != "grudeva2025.reduced"


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

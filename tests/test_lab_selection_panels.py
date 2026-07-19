"""Model selection controls + semantic-safe panels (PV-19B Phase 7, #43 / #70).

Offline + deterministic. Guards component-qualified panel ids (identical trace ids from two components
cannot collide), the semantic-group carried on each panel (same unit is not sufficient to share), the
batch selection inputs (parsed in Python; explicit errors), and the Streamlit selection helpers (a model
is never executed merely because it is available).
"""
import importlib

import pytest

from puckworks.product import lab


@pytest.fixture(scope="module")
def report():
    return lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))


# ── component-qualified, semantically-tagged panels ─────────────────────────────────
def test_panel_ids_are_component_qualified(report):
    for p in lab.render_data(report):
        assert p["panel_id"].startswith(f"{p['component_id']}::")
        assert p["panel_id"].count("::") >= 2          # component::trace::unit
        assert "semantic_group" in p and "reference_basis" in p


def test_identical_trace_ids_from_two_components_would_not_collide(report):
    panels = lab.render_data(report)
    # simulate a second component reusing the same trace_id + unit
    p = dict(panels[0])
    other = dict(p, component_id="other.model",
                 panel_id=f"other.model::{p['trace_id']}::{lab._unit_slug(p['unit'])}",
                 semantic_group=f"grain_volume::{lab._unit_slug(p['unit'])}")
    ids = {p["panel_id"], other["panel_id"]}
    assert len(ids) == 2                               # no collision despite the shared trace_id


def test_assert_semantic_safe_rejects_a_same_id_different_group_collision():
    a = {"panel_id": "x", "semantic_group": "bed_volume::pct", "series": [{"unit": "%"}]}
    b = {"panel_id": "x", "semantic_group": "grain_volume::pct", "series": [{"unit": "%"}]}
    with pytest.raises(ValueError):
        lab.assert_semantic_safe([a, b])
    # same id + same group is fine
    assert lab.assert_semantic_safe([a, dict(a)]) is not None


def test_render_data_panels_are_semantic_safe(report):
    lab.assert_semantic_safe(lab.render_data(report))   # the real panels never collide


# ── batch selection inputs (parsed in Python; explicit) ─────────────────────────────
def test_batch_env_builds_a_selected_lens_request():
    lb = importlib.import_module("tools.lab_batch")
    req = lb._request_from_env(
        {"LAB_LENS_SELECTION_POLICY": "selected", "LAB_LENS_IDS": "cameron2020.extraction_bdf"},
        "pv19_named", {})
    assert req.lens_selection_policy == "selected"
    assert req.requested_lens_ids == ("cameron2020.extraction_bdf",)


def test_batch_env_none_policy_and_reference_selection():
    lb = importlib.import_module("tools.lab_batch")
    req = lb._request_from_env(
        {"LAB_LENS_SELECTION_POLICY": "none", "LAB_REFERENCE_SELECTION_POLICY": "none"},
        "pv19_named", {})
    assert req.lens_selection_policy == "none" and req.reference_selection_policy == "none"


def test_batch_env_unknown_combination_is_an_explicit_error():
    lb = importlib.import_module("tools.lab_batch")
    with pytest.raises(ValueError):        # ids without the selected policy is rejected by the request
        lb._request_from_env(
            {"LAB_LENS_SELECTION_POLICY": "primary", "LAB_LENS_IDS": "cameron2020.extraction_bdf"},
            "pv19_named", {})


# ── Streamlit selection helpers (availability is not selection) ─────────────────────
def test_app_build_request_and_preview():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_app")
    state = {"domain_policy": "warn", "lens_policy": "none", "ref_policy": "none"}
    req = app.build_request("pv19_named", {}, state)
    assert req.lens_selection_policy == "none"
    prev = app.selection_preview(req)
    assert prev["lenses"] == [] and prev["references"] == []      # none selected -> nothing will run


def test_app_preview_shows_readiness_without_executing():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_app")
    state = {"domain_policy": "warn", "lens_policy": "selected",
             "selected_lens_ids": ["mo2023_2.coupled_bed"], "ref_policy": "none"}
    req = app.build_request("pv19_named", {}, state)
    prev = app.selection_preview(req)
    mo = {x["component_id"]: x for x in prev["lenses"]}["mo2023_2.coupled_bed"]
    assert mo["will_execute"] is False and mo["adapter_readiness"] == "NO_ADAPTER"


def test_app_selected_reference_preview_resolves_components():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_app")
    state = {"domain_policy": "warn", "lens_policy": "primary", "ref_policy": "selected",
             "selected_ref_ids": ["waszkiewicz2025.poroelastic"]}
    req = app.build_request("pv19_named", {}, state)
    prev = app.selection_preview(req)
    assert {x["component_id"] for x in prev["references"]} == {"waszkiewicz2025.poroelastic"}

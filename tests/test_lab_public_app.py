"""Public/local Streamlit split + producer-free Explorer app (accessibility mission Phase 4, #43/#70).

Offline + deterministic. Streamlit is a `webapp` extra, so app-import tests skip when it is absent; the
source-contract and pure-logic tests always run. The public app's execution context is fixed in code, its
Model library runs no producer, only affirmatively-cleared selections can run live, a blocked request
carries no science, and downloads carry the rights preflight + provenance.
"""
import importlib
import re
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
PUBLIC = _ROOT / "apps" / "lab_public_app.py"
LOCAL = _ROOT / "apps" / "lab_app.py"
COMMON = _ROOT / "apps" / "lab_ui_common.py"


# ── execution context is fixed in code (never user/query/env selectable) ──────────────
def test_public_entrypoint_is_pinned_to_public_artifact():
    src = PUBLIC.read_text(encoding="utf-8")
    assert 'EXECUTION_CONTEXT = "PUBLIC_ARTIFACT"' in src
    assert 'execution_context=EXECUTION_CONTEXT' in src or 'execution_context="PUBLIC_ARTIFACT"' in src
    # LOCAL_PRIVATE never appears as an execution context in the public app
    assert "LOCAL_PRIVATE" not in src


def test_local_entrypoint_is_pinned_to_local_private():
    src = LOCAL.read_text(encoding="utf-8")
    assert 'EXECUTION_CONTEXT = "LOCAL_PRIVATE"' in src
    assert "PUBLIC_ARTIFACT" not in src


def test_public_context_cannot_be_changed_by_form_query_or_env():
    src = PUBLIC.read_text(encoding="utf-8")
    # the context is a module constant; it is never read from the environment, query string, or a widget
    assert "os.environ" not in src and "getenv" not in src
    assert "query_params" not in src and "experimental_get_query_params" not in src
    # no widget assigns the execution context
    assert not re.search(r"execution_context\s*=\s*st\.", src)


def test_public_app_only_uses_the_service_and_no_forbidden_constructs():
    src = PUBLIC.read_text(encoding="utf-8") + COMMON.read_text(encoding="utf-8")
    assert "lab_service.execute_lab_request" in src
    # no direct scientific stack, no network call, no dynamic exec (a static Colab LINK is allowed)
    for bad in ("import numpy", "import scipy", "requests.", "urllib.request", "os.system",
                "eval(", "exec(", "subprocess"):
        assert bad not in src, f"public surface contains forbidden construct: {bad}"


# ── only affirmatively-cleared selections can run live ────────────────────────────────
def test_only_publicly_cleared_components_are_offered_and_runnable():
    from apps import lab_ui_common as C
    live = C.public_live_ids()
    assert live == ["brewer2026.lb_reference"]              # affirmative rights only
    # an uncleared selection is refused before the service is called
    with pytest.raises(ValueError):
        C.build_public_selfcheck_request(["cameron2020.extraction_bdf"])
    with pytest.raises(ValueError):
        C.build_public_selfcheck_request(["brewer2026.lb_reference", "waszkiewicz2025.poroelastic"])


def test_default_reference_shot_is_not_public_ready_today():
    from apps import lab_ui_common as C
    # Cameron (the recipe-driven reference shot) is NOT_REVIEWED -> the public Run is disabled
    assert C.default_reference_shot_public_ready() is False


def test_public_selfcheck_runs_only_the_cleared_component(monkeypatch):
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_public_app")
    from puckworks.product import lab_runners
    ran = []
    orig = lab_runners.execute_runner
    monkeypatch.setattr(lab_runners, "execute_runner", lambda cid: (ran.append(cid), orig(cid))[1])
    result = app.run_public_selfcheck(["brewer2026.lb_reference"])
    assert result.blocked is False and result.execution_context == "PUBLIC_ARTIFACT"
    assert ran == ["brewer2026.lb_reference"]              # exactly the cleared component
    assert result.report["counts"]["common_scenario_producer_invocations"] == 0


# ── the Model library (Explorer) runs zero producers ──────────────────────────────────
def test_model_library_is_producer_free(monkeypatch):
    import puckworks.product as prod
    from puckworks.product import lab, lab_runners
    called = []
    monkeypatch.setattr(prod, "simulate_pull", lambda *a, **k: called.append("lens"))
    monkeypatch.setattr(lab_runners, "execute_runner", lambda cid: called.append(cid))
    monkeypatch.setattr(lab, "execute_scenario", lambda req: called.append("execute_scenario"))
    from puckworks.product import lab_explorer
    cat = lab_explorer.explorer_catalog()                  # what the Model library view renders
    assert called == [] and cat["producer_free"] is True


# ── a blocked request carries / displays no science; downloads carry preflight + provenance ──
def test_public_artifact_bundle_carries_preflight_and_provenance_and_refuses_blocked():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_public_app")
    result = app.run_public_selfcheck(["brewer2026.lb_reference"])
    bundle = app.public_artifact_bundle(result)
    assert bundle["execution_context"] == "PUBLIC_ARTIFACT"
    assert bundle["rights_preflight"]["blocked"] is False               # rights preflight present
    assert bundle["comparison"]["provenance"]["package_version"]        # provenance present
    # a blocked result yields NO bundle (no scientific output to publish)
    from puckworks.product import lab, lab_service
    blocked = lab_service.execute_lab_request(lab.ScenarioRequest("pv19_named"),
                                              execution_context="PUBLIC_ARTIFACT")
    assert blocked.blocked is True and blocked.report is None
    with pytest.raises(ValueError):
        app.public_artifact_bundle(blocked)


# ── novice presentation: plain labels + chart text-alternatives ───────────────────────
def test_plain_language_labels_present():
    from apps import lab_ui_common as C
    assert C.PLAIN_LABELS["native reference runner"] == "Component self-check"
    assert C.PLAIN_LABELS["common-scenario lens"] == "Model that can use this recipe"
    assert C.PLAIN_LABELS["disposition"] == "Availability"
    assert C.PLAIN_LABELS["warn"] and C.PLAIN_LABELS["strict"]


def test_charts_have_a_text_alternative_table():
    from apps import lab_ui_common as C
    panel = {"x_label": "t (s)", "unit": "bar", "x": [0.0, 1.0],
             "series": [{"label": "pressure", "role": "prescribed", "y": [9.0, 9.0]}]}
    tbl = C.panel_table(panel)
    assert tbl["headers"][0] == "t (s)" and "bar" in tbl["headers"][1]
    assert tbl["rows"] == [(0.0, 9.0), (1.0, 9.0)]


# ── startup smoke (import + producer-free initial state; no server) ────────────────────
def test_public_app_imports_and_main_is_callable():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_public_app")
    assert callable(app.main)
    assert app.EXECUTION_CONTEXT == "PUBLIC_ARTIFACT"


def test_deployment_manifest_is_minimal_and_excludes_heavy_extras():
    # only the actual requirement lines (comments may explain what is deliberately excluded)
    reqs = [ln.strip() for ln in (_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.strip().startswith("#")]
    assert ".[webapp]" in reqs and "pandas" in reqs
    for bad in ("taichi", "pyvista", "vtk", "viz3d", "[lb]"):
        assert not any(bad in r for r in reqs), f"deployment manifest pulls a heavy extra: {bad}"

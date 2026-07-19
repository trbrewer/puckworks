"""Guided Pull Laboratory dynamic-environment tests (#43 / #70): Streamlit UI helpers, batch runner,
devcontainer, and the Actions workflow.

Offline + deterministic. Streamlit is a `webapp` extra (not core / not in the quick lane), so tests that
import the app are skipped when it is absent; the batch/workflow/devcontainer/parity tests always run.
"""
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
APP = _ROOT / "apps" / "lab_app.py"
BATCH = _ROOT / "tools" / "lab_batch.py"
DEVCONTAINER = _ROOT / ".devcontainer" / "devcontainer.json"
WORKFLOW = _ROOT / ".github" / "workflows" / "guided-pull-batch.yml"

if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


# ── core stays free of the web stack ──────────────────────────────────────────────
def test_core_import_does_not_pull_in_streamlit():
    code = "import sys, puckworks; print('streamlit' in sys.modules)"
    out = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
    assert out == "False"


def test_app_and_batch_only_use_public_api():
    src = APP.read_text(encoding="utf-8") + BATCH.read_text(encoding="utf-8")
    assert "puckworks.product" in src and "lab" in src
    assert "import numpy" not in src and "import scipy" not in src
    for bad in ("requests.", "urllib.request", "http://", "https://", "os.system",
                "eval(", "exec("):
        assert bad not in src, f"frontend/runner contains forbidden construct: {bad}"


def test_app_has_no_hidden_scientific_literals():
    text = re.sub(r"#[^\n]*", "", APP.read_text(encoding="utf-8"))
    allowed = {"5.0", "30.0", "10.0", "80.0", "1.0", "12.0", "98.0", "0.5", "1e-9", "0.4"}
    for m in re.findall(r"(?<![\w.])\d+\.\d+", text):
        assert m in allowed, f"unexplained numeric literal in the app: {m}"


# ── Streamlit domain-formatting helper (unit-tested; no server) ────────────────────
class _Finding:
    def __init__(self, status, field="x", plain="p", tech="t"):
        self.status = status
        self.field = field
        self.plain_explanation = plain
        self.technical_reason = tech


class _Enum:
    def __init__(self, v):
        self.value = v


def test_format_finding_levels():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_app")
    assert app.format_finding(_Finding(_Enum("in_domain")))[0] == "success"
    assert app.format_finding(_Finding(_Enum("warning")))[0] == "warning"
    assert app.format_finding(_Finding(_Enum("rejected")))[0] == "error"
    assert app.format_finding(_Finding(_Enum("not_applicable")))[0] == "info"
    # plain_explanation is surfaced in the text; technical_reason in the detail
    lvl, text, detail = app.format_finding(_Finding(_Enum("warning"), field="dose_g", plain="How much"))
    assert "How much" in text and detail == "t"


def test_preset_defaults_come_from_the_selected_preset():
    pytest.importorskip("streamlit")
    app = importlib.import_module("apps.lab_app")
    import puckworks.product as prod
    for pid in prod.available_pull_presets():
        d = app.preset_defaults(pid)
        recipe, _ = prod.load_pull_preset(pid)
        assert d["dose_g"] == recipe.dose_g and d["pressure_bar"] == recipe.pressure_bar


def test_app_module_imports_with_webapp_extra():
    pytest.importorskip("streamlit")
    mod = importlib.import_module("apps.lab_app")
    assert callable(mod.main)


# ── batch runner ──────────────────────────────────────────────────────────────────
def test_batch_runner_bounds_inputs_and_never_clamps():
    lb = importlib.import_module("tools.lab_batch")
    with pytest.raises(SystemExit):
        lb._bounded({"LAB_DOSE_G": "999"})
    assert lb._bounded({"LAB_DOSE_G": "18"}) == {"dose_g": 18.0}


def test_batch_run_matches_package_output_and_writes_manifest(tmp_path):
    pytest.importorskip("matplotlib")     # the batch writes a required scientific figure
    lb = importlib.import_module("tools.lab_batch")
    from puckworks.product import lab
    sha = "c" * 40
    report = lb.run({"LAB_OUT_DIR": str(tmp_path), "LAB_PRESET": "guided_v1",
                     "GITHUB_SHA": sha, "GITHUB_RUN_ID": "7", "LAB_WHEEL_SHA256": "d" * 64})
    # batch output equals package output for the same request + provenance
    ex = lab.execute_scenario(lab.ScenarioRequest("guided_v1"))
    pkg = lab.build_comparison(ex, provenance=lab.BuildProvenance(
        package_version=report["provenance"]["package_version"], source_commit=sha,
        workflow_run_id="7", wheel_sha256="d" * 64))
    assert lab.artifact_sha256(report) == lab.artifact_sha256(pkg)
    # required scientific figure + manifest present
    assert (tmp_path / "guided_pull_lab_trace.png").exists()
    manifest = json.loads((tmp_path / "artifact_manifest.json").read_text())
    assert manifest["requested_preset"] == "guided_v1"
    assert manifest["source_commit"] == sha and manifest["workflow_run_id"] == "7"
    assert manifest["scientific_payload_sha256"] == report["integrity"]["scientific_payload_sha256"]
    # manifest file hashes reproduce
    for name, meta in manifest["files"].items():
        import hashlib
        assert meta["sha256"] == hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()


def test_batch_scenario_identity_not_pv19_for_guided_v1(tmp_path):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    report = lb.run({"LAB_OUT_DIR": str(tmp_path), "LAB_PRESET": "guided_v1", "LAB_DOSE_G": "19"})
    assert report["scenario"]["scenario_id"] == "guided_v1"
    assert report["scenario"]["applied_overrides"]["dose_g"]["effective"] == 19.0


def test_required_scientific_figure_failure_would_fail_the_batch(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    monkeypatch.setattr(lb.lab, "render_data", lambda report: [])   # no plottable panels
    with pytest.raises(RuntimeError):
        lb.run({"LAB_OUT_DIR": str(tmp_path)})


# ── devcontainer + streamlit config ────────────────────────────────────────────────
def test_devcontainer_json_is_valid_and_installs_webapp():
    data = json.loads(DEVCONTAINER.read_text(encoding="utf-8"))
    assert 8501 in data["forwardPorts"]
    assert "webapp" in data["postCreateCommand"]
    assert data["remoteEnv"]["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] == "false"


def test_streamlit_config_disables_telemetry():
    cfg = (_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "gatherUsageStats = false" in cfg


# ── Actions batch workflow security + provenance passing ───────────────────────────
def test_batch_workflow_is_secure_and_passes_provenance():
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"(?m)^permissions:\s*\n\s*contents:\s*read\s*$", wf)
    assert "issues: write" not in wf and "secrets." not in wf
    assert "workflow_dispatch:" in wf
    for use in re.findall(r"uses:\s*(\S+)", wf):
        if "/" in use.split("@")[0]:
            assert re.search(r"@[0-9a-f]{40}$", use), f"action not SHA-pinned: {use}"
    # user inputs never on a run: shell line
    for line in wf.splitlines():
        if re.match(r"\s+run:", line):
            assert "${{ inputs" not in line and "${{ github.event.inputs" not in line
    # wheel SHA is recorded and provenance flows to the runner
    assert "LAB_WHEEL_SHA256" in wf and "tools/lab_batch.py" in wf


def test_codespaces_ci_workflow_is_secure_and_smokes_the_devcontainer():
    wf = (_ROOT / ".github" / "workflows" / "codespaces-ci.yml").read_text(encoding="utf-8")
    assert re.search(r"(?m)^permissions:\s*\n\s*contents:\s*read\s*$", wf)
    assert "issues: write" not in wf and "secrets." not in wf
    for use in re.findall(r"uses:\s*(\S+)", wf):
        if "/" in use.split("@")[0]:
            assert re.search(r"@[0-9a-f]{40}$", use), f"action not SHA-pinned: {use}"
    # it builds the devcontainer and runs a Streamlit health + comparison smoke inside it
    assert "devcontainers/ci@" in wf
    assert "_stcore/health" in wf and "tools/lab_batch.py" in wf

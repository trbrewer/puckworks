"""Guided Pull Laboratory dynamic-environment tests (#43 / #70): Streamlit UI, batch runner,
devcontainer, and the Actions workflow.

Offline + deterministic. Streamlit is a `webapp` extra (not core / not in the quick lane), so tests that
import the app are skipped when it is absent; the batch/workflow/devcontainer/parity tests always run.
"""
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
    # a fresh interpreter importing puckworks must NOT import streamlit
    code = "import sys, puckworks; print('streamlit' in sys.modules)"
    out = subprocess.check_output([sys.executable, "-c", code], text=True).strip()
    assert out == "False", "importing puckworks core pulled in streamlit"


def test_app_and_batch_only_use_public_api():
    src = APP.read_text(encoding="utf-8") + BATCH.read_text(encoding="utf-8")
    # they route through the public product API + the lab comparison API only
    assert "puckworks.product" in src and "lab" in src
    # no re-implemented model math in the frontend/runner
    assert "import numpy" not in src and "import scipy" not in src
    # no external network / shell / eval
    for bad in ("requests.", "urllib.request", "http://", "https://", "subprocess", "os.system",
                "eval(", "exec("):
        assert bad not in src, f"frontend/runner contains forbidden construct: {bad}"


# ── no hidden scientific literals in the frontend ─────────────────────────────────
def test_app_has_no_hidden_scientific_literals():
    text = re.sub(r"#[^\n]*", "", APP.read_text(encoding="utf-8"))
    # only the DECLARED UI bound/step constants (and the "0.4" dev-version label) may appear as decimals
    allowed = {"5.0", "30.0", "18.0", "10.0", "80.0", "36.0", "1.0", "12.0", "9.0", "98.0", "92.0",
               "0.5", "0.4"}
    for m in re.findall(r"(?<![\w.])\d+\.\d+", text):
        assert m in allowed, f"unexplained numeric literal in the app: {m}"


# ── batch runner ──────────────────────────────────────────────────────────────────
def test_batch_runner_bounds_inputs_and_never_clamps(tmp_path):
    import importlib
    lb = importlib.import_module("tools.lab_batch")
    # out-of-range is rejected (SystemExit), not silently clamped
    with pytest.raises(SystemExit):
        lb._bounded({"LAB_DOSE_G": "999"})
    assert lb._bounded({"LAB_DOSE_G": "18"}) == {"dose_g": 18.0}


def test_batch_run_matches_package_output(tmp_path):
    import importlib
    lb = importlib.import_module("tools.lab_batch")
    from puckworks.product import lab
    report = lb.run({"LAB_OUT_DIR": str(tmp_path)})
    # the batch output equals the package comparison for the same scenario
    pkg = lab.build_comparison(lab.run_scenario("pv19_named"))
    assert lab.canonical_json(report) == lab.canonical_json(pkg)
    assert (tmp_path / "guided_pull_lab.json").exists()
    assert (tmp_path / "guided_pull_lab.md").exists()


def test_run_scenario_bounds_route_through_producer():
    from puckworks.product import lab
    run = lab.run_scenario("pv19_named", dose_g=18.0, pressure_bar=9.0)
    assert run["schema_version"] == 1                       # the existing PullRun, not re-implemented


# ── devcontainer ──────────────────────────────────────────────────────────────────
def test_devcontainer_json_is_valid_and_installs_webapp():
    data = json.loads(DEVCONTAINER.read_text(encoding="utf-8"))
    assert 8501 in data["forwardPorts"]
    assert "webapp" in data["postCreateCommand"]
    assert data["remoteEnv"]["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] == "false"


def test_streamlit_config_disables_telemetry():
    cfg = (_ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")
    assert "gatherUsageStats = false" in cfg


# ── Actions batch workflow security ────────────────────────────────────────────────
def test_batch_workflow_is_secure():
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert re.search(r"(?m)^permissions:\s*\n\s*contents:\s*read\s*$", wf)   # read-only default
    assert "issues: write" not in wf and "secrets." not in wf               # no issue write, no secrets
    assert "workflow_dispatch:" in wf
    # every third-party action is SHA-pinned
    for use in re.findall(r"uses:\s*(\S+)", wf):
        if "/" in use.split("@")[0]:
            assert re.search(r"@[0-9a-f]{40}$", use), f"action not SHA-pinned: {use}"
    # user inputs must NEVER be interpolated into a run: shell line (only into env: vars)
    for line in wf.splitlines():
        if re.match(r"\s+run:", line) or (line.strip() and line.startswith(" " * 10) and "run" in wf):
            if re.match(r"\s+run:", line):
                assert "${{ inputs" not in line and "${{ github.event.inputs" not in line


def test_batch_workflow_declared_env_carries_the_inputs():
    wf = WORKFLOW.read_text(encoding="utf-8")
    assert "LAB_DOSE_G: ${{ inputs.dose_g }}" in wf
    assert "tools/lab_batch.py" in wf


# ── app import (skipped when the webapp extra is absent) ───────────────────────────
def test_app_module_imports_with_webapp_extra():
    pytest.importorskip("streamlit")
    import importlib
    mod = importlib.import_module("apps.lab_app")
    assert callable(mod.main)

"""Synthetic, non-Angeloni qualification of the R3 collection and silence controls."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CANARY = "ZXQ_STAGE_E0_R3_CANARY_86420_0.271828182845904"
pytestmark = pytest.mark.slow


def _manifest(path: Path) -> Path:
    manifest = path / "manifest.json"
    manifest.write_text(json.dumps({
        "schema_version": "synthetic/v2",
        "tests": [{
            "static_module_path": "test_canary.py",
            "static_function_name": "test_canary",
            "static_node_id": "test_canary.py::test_canary",
            "opaque_test_id": "PTI-001",
            "permitted_protected_artifact_categories": ["SYNTHETIC_CANARY"],
            "expected_execution_phase": ["setup", "call", "teardown"],
            "marker_name": "protected_target_integrity",
        }],
    }), encoding="utf-8")
    return manifest


def _run(tmp_path: Path, source: str, *, conftest: str = "", collect_only: bool = False):
    target = tmp_path / "protected-synthetic.dat"
    target.write_text(CANARY, encoding="utf-8")
    test = tmp_path / "test_canary.py"
    test.write_text(source, encoding="utf-8")
    if conftest:
        (tmp_path / "conftest.py").write_text(conftest, encoding="utf-8")
    result = tmp_path / "result.json"
    diagnostic = tmp_path / "diagnostic.json"
    junit = tmp_path / "junit.xml"
    env = dict(os.environ)
    env.update({
        "PYTHONPATH": str(ROOT),
        "PYTHONDONTWRITEBYTECODE": "1",
        "SCI_MD_004_SYNTHETIC_PROTECTED_PATH": str(target),
        "SCI_MD_004_CANDIDATE_COMMIT": "SYNTHETIC",
    })
    command = [
        sys.executable, "-m", "tools.protected_target_qa",
        "--protected-test-manifest", str(_manifest(tmp_path)),
        "--protected-qa-result", str(result),
        "--collection-diagnostic", str(diagnostic),
        "--junitxml", str(junit), "-q", "--tb=no",
    ]
    if collect_only:
        command.append("--collect-only")
    command.append(str(test))
    process = subprocess.run(command, cwd=tmp_path, env=env, text=True, capture_output=True, check=False)
    visible = process.stdout + process.stderr
    for artifact in (result, diagnostic, junit):
        if artifact.exists():
            visible += artifact.read_text(encoding="utf-8")
    return process, visible, diagnostic


COLLECTION_CASES = {
    "module_level": "from pathlib import Path\nimport os\nPath(os.environ['SCI_MD_004_SYNTHETIC_PROTECTED_PATH']).read_text()\ndef test_canary(): pass\n",
    "decorator_time": "from pathlib import Path\nimport os, pytest\ndef deco(): Path(os.environ['SCI_MD_004_SYNTHETIC_PROTECTED_PATH']).read_text(); return lambda f:f\n@deco()\ndef test_canary(): pass\n",
    "parametrization_time": "from pathlib import Path\nimport os, pytest\ndef values(): Path(os.environ['SCI_MD_004_SYNTHETIC_PROTECTED_PATH']).read_text(); return [1]\n@pytest.mark.parametrize('x', values())\ndef test_canary(x): pass\n",
    "pytest_generate_tests": "from pathlib import Path\nimport os\ndef pytest_generate_tests(metafunc): Path(os.environ['SCI_MD_004_SYNTHETIC_PROTECTED_PATH']).read_text()\ndef test_canary(): pass\n",
    "static_manifest_generator": "from pathlib import Path\nimport os\ndef generate_manifest(): Path(os.environ['SCI_MD_004_SYNTHETIC_PROTECTED_PATH']).read_text()\ngenerate_manifest()\ndef test_canary(): pass\n",
}


@pytest.mark.parametrize("case", sorted(COLLECTION_CASES))
def test_collection_open_is_blocked_with_opaque_provenance(case, tmp_path):
    process, visible, diagnostic = _run(tmp_path, COLLECTION_CASES[case], collect_only=True)
    assert process.returncode != 0
    assert CANARY not in visible
    payload = json.loads(diagnostic.read_text(encoding="utf-8"))
    assert payload["result"] == "PROTECTED_TARGET_COLLECTION_OPEN_BLOCKED"
    assert payload["event"]["opaque_callsite_id"] == "CPO-001"
    assert payload["target_content_returned"] is False
    assert payload["target_value_recorded"] is False


def test_plugin_collection_hook_open_is_blocked(tmp_path):
    conftest = "from pathlib import Path\nimport os\ndef pytest_collection_modifyitems(items): Path(os.environ['SCI_MD_004_SYNTHETIC_PROTECTED_PATH']).read_text()\n"
    process, visible, diagnostic = _run(tmp_path, "def test_canary(): pass\n", conftest=conftest, collect_only=True)
    assert process.returncode != 0 and CANARY not in visible
    assert json.loads(diagnostic.read_text())["event"]["opaque_callsite_id"] == "CPO-001"


DISCLOSURE_CASES = {
    "stdout": f"print({CANARY!r})",
    "stderr": f"import sys; sys.stderr.write({CANARY!r})",
    "logging": f"import logging; logging.warning({CANARY!r})",
    "warning": f"import warnings; warnings.warn({CANARY!r})",
    "assertion": f"assert False, {CANARY!r}",
    "exception": f"raise RuntimeError({CANARY!r})",
    "dataframe_diff": f"import pandas as pd; from pandas.testing import assert_frame_equal; assert_frame_equal(pd.DataFrame({{'x':[{CANARY!r}]}}), pd.DataFrame({{'x':['x']}}))",
    "temporary_filename": f"raise RuntimeError(str(__import__('pathlib').Path({CANARY!r})))",
    "subprocess_output": f"import subprocess,sys; subprocess.run([sys.executable,'-c',{('print(' + repr(CANARY) + ')')!r}], check=True)",
}


@pytest.mark.parametrize("case", sorted(DISCLOSURE_CASES))
def test_execution_disclosure_is_redacted(case, tmp_path):
    source = "import pytest\npytestmark=pytest.mark.protected_target_integrity\ndef test_canary():\n    " + DISCLOSURE_CASES[case] + "\n"
    process, visible, _diagnostic = _run(tmp_path, source)
    assert process.returncode != 0
    assert CANARY not in visible
    assert "NO_TARGET_VALUE_DISCLOSED" in visible


def test_parameter_id_and_junit_are_redacted(tmp_path):
    source = f"import pytest\npytestmark=pytest.mark.protected_target_integrity\n@pytest.mark.parametrize('x',[1],ids=[{CANARY!r}])\ndef test_canary(x): assert False\n"
    process, visible, _diagnostic = _run(tmp_path, source)
    assert process.returncode != 0 and CANARY not in visible
    assert "PTI-001-001" in visible

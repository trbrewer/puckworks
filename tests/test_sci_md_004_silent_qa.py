"""Synthetic, non-Angeloni qualification of the silent protected-test harness."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from tools.generate_protected_test_manifest import build as build_test_manifest

ROOT = Path(__file__).resolve().parents[1]
CANARY = "ZXQ_STAGE_E0_R2_CANARY_74291_0.314159265358979"


CASES = {
    "stdout": f"print({CANARY!r})",
    "stderr": f"import sys; sys.stderr.write({CANARY!r})",
    "log": f"import logging; logging.warning({CANARY!r})",
    "warning": f"import warnings; warnings.warn({CANARY!r})",
    "assertion": f"assert False, {CANARY!r}",
    "exception": f"raise RuntimeError({CANARY!r})",
    "dataframe": (
        "import pandas as pd; from pandas.testing import assert_frame_equal; "
        f"assert_frame_equal(pd.DataFrame({{'x': [{CANARY!r}]}}), pd.DataFrame({{'x': ['different']}}))"
    ),
    "temp_filename": f"from pathlib import Path; Path({CANARY!r}).write_text('synthetic')",
    "subprocess": (
        "import subprocess, sys; "
        f"subprocess.run([sys.executable, '-c', {(f'print({CANARY!r})')!r}], check=True)"
    ),
}


def _run_child(tmp_path: Path, body: str, *, parametrized: bool = False):
    child = tmp_path / "test_canary.py"
    decorator = (
        f"@pytest.mark.parametrize('value', [1], ids=[{CANARY!r}])\n"
        if parametrized else ""
    )
    parameter = "value" if parametrized else ""
    child.write_text(
        "import pytest\n"
        "pytestmark = pytest.mark.protected_target_integrity\n"
        f"{decorator}def test_canary({parameter}):\n    {body}\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({
        "schema_version": "synthetic/v1",
        "opaque_test_mapping": {"test_canary.py::test_canary": "PTI-001"},
    }), encoding="utf-8")
    junit = tmp_path / "junit.xml"
    result = tmp_path / "result.json"
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(ROOT)
    environment["SCI_MD_004_SYNTHETIC_CANARY"] = CANARY
    process = subprocess.run([
        sys.executable, "-m", "pytest", "-q", "--tb=no", "--rootdir", str(tmp_path),
        "-p", "puckworks.analysis.sci_md_004_silent_qa",
        "--protected-test-manifest", str(manifest),
        "--protected-qa-result", str(result),
        "--junitxml", str(junit), str(child),
    ], cwd=tmp_path, env=environment, text=True, capture_output=True, check=False)
    visible = process.stdout + process.stderr + junit.read_text(encoding="utf-8") + result.read_text(encoding="utf-8")
    return process, visible


@pytest.mark.parametrize("case", sorted(CASES))
def test_silent_harness_redacts_synthetic_canary(case, tmp_path):
    process, visible = _run_child(tmp_path, CASES[case])
    assert process.returncode != 0
    assert CANARY not in visible
    assert "NO_TARGET_VALUE_DISCLOSED" in visible


def test_silent_harness_redacts_parametrized_node_id(tmp_path):
    process, visible = _run_child(tmp_path, "assert True", parametrized=True)
    assert process.returncode != 0
    assert CANARY not in visible
    assert "PTI-001-001" in visible


def test_silent_harness_allows_framework_counts_paths_hashes_and_durations(tmp_path):
    process, visible = _run_child(tmp_path, "assert True")
    assert process.returncode == 0
    assert CANARY not in visible
    assert "1 passed" in visible


def test_synthetic_canary_is_not_present_in_governed_sources():
    matches = []
    for directory in (ROOT / "puckworks/data/schmieder2023", ROOT / "puckworks/data/pannusch2024", ROOT / "puckworks/data/maille2024"):
        for path in directory.rglob("*"):
            if path.is_file() and CANARY.encode() in path.read_bytes():
                matches.append(path)
    assert matches == []


def test_static_protected_test_manifest_is_current():
    committed = json.loads((ROOT / "tests/protected_target_test_manifest.json").read_text())
    assert committed == build_test_manifest()


def test_r1_scientific_subtree_and_bundle_are_immutable():
    import subprocess

    subtree = subprocess.run(
        ["git", "rev-parse", "HEAD:docs/analysis/sci_md_004_stage_e0"],
        cwd=ROOT, text=True, capture_output=True, check=True,
    ).stdout.strip()
    assert subtree == "beee8119613da8fa36da3213ffee30a2c706cbcb"
    bundle = ROOT / "docs/analysis/sci_md_004_stage_e0/bundle_manifest.json"
    assert __import__("hashlib").sha256(bundle.read_bytes()).hexdigest() == "112f8b3b943a5cea3399746fde512048e3898f99c8079433dae86bd142db8709"


@pytest.mark.protected_target_integrity
def test_old_value_scanner_is_not_an_r2_gate():
    plugin = (ROOT / "puckworks/analysis/sci_md_004_silent_qa.py").read_text()
    assert "bioactives.csv" not in plugin
    assert "target cell" not in plugin.casefold()
    assert "NON_PROVENANCE_AWARE_TARGET_STRING_SCAN" not in plugin

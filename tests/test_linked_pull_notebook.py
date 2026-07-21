"""Static contract tests for the Espresso Model Relay Colab notebook (illustrative, one-click, pinned)."""
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NB = REPO / "notebooks" / "illustrative_linked_pull_colab.ipynb"


@pytest.fixture(scope="module")
def nb():
    return json.loads(NB.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def code(nb):
    return "".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")


@pytest.fixture(scope="module")
def markdown(nb):
    return "".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")


def test_notebook_exists_and_valid(nb):
    assert nb["nbformat"] == 4 and nb["cells"]


def test_no_committed_outputs_or_execution_counts(nb):
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            assert not c.get("outputs"), f"cell {i} has outputs"
            assert c.get("execution_count") is None, f"cell {i} has execution_count"


def test_exactly_one_visible_run_cell(nb):
    runs = [c for c in nb["cells"]
            if c["cell_type"] == "code" and "▶ Run the Espresso Model Relay" in "".join(c["source"])]
    assert len(runs) == 1


def test_title_and_permanent_warning_present(markdown):
    assert "THE ESPRESSO MODEL RELAY" in markdown
    assert "illustrative model relay" in markdown.lower()
    assert "validated as one scientific model" in markdown.lower()      # "...has **not** been validated..."
    # the warning is NOT only in a collapsed section — it is a top-level markdown cell
    assert "digital twin" in markdown.lower()


def test_default_mode_is_fast(code):
    m = re.search(r'execution_mode\s*=\s*"([^"]+)"', code)
    assert m and m.group(1).startswith("fast")


def test_calls_the_engine_not_model_equations(code):
    assert "execute_illustrative_linked_pull" in code
    assert 'manifest_id="illustrative_linked_pull_v1"' in code
    assert 'execution_context="LOCAL_PRIVATE"' in code
    # no reimplemented model math in the notebook
    assert "def simulate" not in code and "np.exp(" not in code


def test_form_exposes_only_the_limited_inputs(code):
    for ctrl in ("dose_g", "target_beverage_g", "grind_setting", "target_pressure_bar",
                 "brew_temperature_c", "heterogeneity", "execution_mode"):
        assert ctrl in code
    assert "ipywidgets" not in code


def test_chain_map_and_assumption_ledger_and_dashboard_shown(code):
    assert "chain_map_text" in code
    assert "assumptions" in code and "validation_needed" in code
    assert "cup_dashboard_blocks" in code


def test_technical_metadata_is_collapsible(code):
    assert "<details>" in code and "model_output_hash" in code


def test_downloads_present_but_not_auto_triggered(code):
    assert "illustrative_linked_pull_v1.json" in code and "illustrative_linked_pull_v1.md" in code
    assert "files.upload" not in code


def test_completion_sentinel_present(code):
    assert "LINKED_PULL_RELAY_COMPLETE" in code
    for field in ("manifest=", "context=LOCAL_PRIVATE", "executed=", "model_output_hash="):
        assert field in code


def test_pinned_development_preview_not_mutable_main(code):
    assert "DEVELOPMENT PREVIEW" in code
    assert re.search(r'PIN_COMMIT\s*=\s*"[0-9a-f]{40}"', code)
    assert "@main" not in code and "@latest" not in code
    assert "0.4.0.dev0" in code


def test_no_terminal_instructions_in_novice_markdown(markdown):
    low = markdown.lower()
    for bad in ("pip install", "!pip", "open a terminal", "run this command"):
        assert bad not in low


def test_pinned_commit_contains_every_imported_puckworks_module(code):
    import subprocess
    m = re.search(r'PIN_COMMIT\s*=\s*"([0-9a-f]{40})"', code)
    assert m
    pin = m.group(1)
    mods = set()
    for grp in re.findall(r"from puckworks\.product import ([\w ,]+)", code):
        for part in grp.split(","):
            name = part.strip().split(" as ")[0].strip()
            if name:
                mods.add(name)
    assert "linked_pull" in mods
    if subprocess.run(["git", "cat-file", "-e", f"{pin}^{{commit}}"], cwd=str(REPO),
                      capture_output=True).returncode != 0:
        pytest.skip("pinned commit not present in this checkout")
    for mod in sorted(mods):
        r = subprocess.run(["git", "cat-file", "-e", f"{pin}:puckworks/product/{mod}.py"],
                           cwd=str(REPO), capture_output=True)
        assert r.returncode == 0, f"pinned commit {pin[:12]} lacks puckworks/product/{mod}.py — bump PIN_COMMIT"

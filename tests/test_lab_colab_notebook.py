"""Static contract tests for the form-driven Guided Pull Laboratory Colab notebook (accessibility, #43).

Offline, no execution. A separate hermetic-execution smoke (build a dev wheel, PUCKWORKS_WHEEL, run
outside the checkout, assert GUIDED_PULL_LAB_COMPLETE) runs in the notebook-smoke CI lane. These tests
guard the novice contract: one visible run cell, no terminal instruction, a pinned DEVELOPMENT-PREVIEW
install (never mutable main, never a v0.3.0 claim), the shared rights-safe service under LOCAL_PRIVATE,
the three experience modes mapped to explicit finite requests, and Grudeva never offered.
"""
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NB = REPO / "notebooks" / "guided_pull_laboratory_colab.ipynb"


@pytest.fixture(scope="module")
def nb():
    return json.loads(NB.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def code(nb):
    return "".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code")


@pytest.fixture(scope="module")
def markdown(nb):
    return "".join("".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "markdown")


def test_valid_schema_and_present(nb):
    assert nb["nbformat"] == 4 and nb["cells"]


def test_no_committed_outputs_or_execution_counts(nb):
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            assert not c.get("outputs"), f"cell {i} has committed outputs"
            assert c.get("execution_count") is None, f"cell {i} has execution_count"


def test_exactly_one_visible_run_cell(nb):
    run_cells = [c for c in nb["cells"]
                 if c["cell_type"] == "code" and "#@title ▶ Run the Laboratory" in "".join(c["source"])]
    assert len(run_cells) == 1
    assert run_cells[0]["metadata"].get("cellView") == "form"   # rendered as a form/play button


def test_form_controls_use_native_param_not_ipywidgets(code):
    assert "#@param" in code
    assert "ipywidgets" not in code and "import widgets" not in code
    # the primary novice controls are present
    for ctrl in ("dose_g", "target_beverage_g", "pressure_bar", "experience_mode", "preset"):
        assert ctrl in code


def test_no_terminal_or_shell_instruction_in_the_novice_flow(markdown):
    low = markdown.lower()
    for bad in ("open a terminal", "command line", "run this command", "type the following",
                "in your shell", "pip install", "!pip"):
        assert bad not in low, f"novice markdown instructs {bad!r}"


def test_install_is_a_pinned_development_preview_not_mutable_main(code):
    assert "DEVELOPMENT PREVIEW" in code
    # an immutable full-40-hex commit pin via git+https (option B), never a mutable branch
    assert re.search(r"git\+https://github\.com/trbrewer/puckworks@\{PIN_COMMIT\}", code) or \
        "git+https://github.com/trbrewer/puckworks@" in code
    assert re.search(r'PIN_COMMIT\s*=\s*"[0-9a-f]{40}"', code), "install must pin a full 40-hex commit"
    assert "@main" not in code and "@latest" not in code
    # it must NOT claim to be the v0.3.0 public release, and asserts the dev version
    assert "0.4.0.dev0" in code
    assert "v0.3.0" not in code or "NOT the v0.3.0" in code


def test_uses_the_shared_rights_safe_service_under_local_private(code):
    assert "lab_service.execute_lab_request" in code
    assert 'execution_context="LOCAL_PRIVATE"' in code
    # LOCAL_PRIVATE is explained as a private runtime, not a public-hosting clearance
    assert "does NOT mean" in code and "public hosting" in code.lower()


def test_three_experience_modes_map_to_explicit_finite_requests(code):
    # catalog-only is the producer-free Explorer path (runs nothing)
    assert "lab_explorer.explorer_catalog()" in code
    # guided-only selects no references; guided+self-checks selects the interactive-fast references
    assert 'reference_selection_policy="none"' in code
    assert 'reference_selection_policy="interactive_fast"' in code
    assert 'lens_selection_policy="primary"' in code
    # never "select every future runner" implicitly
    assert "requested_reference_runner_ids" not in code or "grudeva" not in code


def test_grudeva_is_never_offered_and_is_named_as_blocked(nb, code, markdown):
    # grudeva is never a selectable form option
    assert "grudeva" not in code.lower() or "rights-blocked" in code.lower()
    # the rights note names it as blocked
    assert "grudeva2025.reduced is rights-blocked" in code


def test_completion_sentinel_present(code):
    assert "GUIDED_PULL_LAB_COMPLETE" in code
    for field in ("mode=", "context=LOCAL_PRIVATE", "components=", "sci_hash="):
        assert field in code


def test_no_auto_upload_or_credentials(code):
    low = code.lower()
    for bad in ("drive.mount", "password", "token", "secret", "api_key", "requests.post", "urllib.request"):
        assert bad not in low, f"notebook references {bad!r}"
    # a files.download() is a user-initiated DOWNLOAD (allowed); there is no automatic external upload
    assert "files.upload" not in low

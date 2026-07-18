"""Static contract tests for the Guided Espresso Pull Colab notebook (issue #48, Section 4D).

Offline, no execution. A separate hermetic-execution smoke (build a wheel, PUCKWORKS_WHEEL, run
outside the checkout, assert GUIDED_PULL_COMPLETE) runs in the experience CI lane. The quickstart
notebook is intentionally NOT touched by these tests.
"""
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NB_PATH = REPO / "notebooks" / "guided_espresso_pull_colab.ipynb"
QUICKSTART = REPO / "notebooks" / "puckworks_quickstart_colab.ipynb"


@pytest.fixture(scope="module")
def nb():
    return json.loads(NB_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def text():
    return "".join("".join(c["source"]) for c in json.loads(NB_PATH.read_text(encoding="utf-8"))["cells"])


@pytest.fixture(scope="module")
def code_text():
    cells = json.loads(NB_PATH.read_text(encoding="utf-8"))["cells"]
    return "".join("".join(c["source"]) for c in cells if c["cell_type"] == "code")


def test_notebook_is_valid_json_and_present(nb):
    assert nb["nbformat"] == 4 and nb["cells"]


def test_no_committed_outputs(nb):
    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] == "code":
            assert not c.get("outputs"), f"cell {i} has committed outputs"
            assert c.get("execution_count") is None, f"cell {i} has execution_count"


def test_quickstart_notebook_is_unchanged_and_still_present():
    # We must not weaken the v0.2.0 registry quickstart.
    assert QUICKSTART.exists()
    assert "QUICKSTART_COMPLETE" in QUICKSTART.read_text(encoding="utf-8")


def test_no_credentials_or_private_paths(text):
    low = text.lower()
    for bad in ("password", "token", "secret", "api_key", "visualizer/raw", "/raw/", "normalized_v3"):
        assert bad not in low, f"notebook references {bad!r}"


def test_uses_native_param_controls_not_ipywidgets(text):
    assert "#@param" in text
    assert "ipywidgets" not in text and "import widgets" not in text


def test_local_wheel_override_and_no_unpinned_install(code_text):
    assert "PUCKWORKS_WHEEL" in code_text
    # never install the main branch / an unpinned package / a mutable "latest" artifact
    for bad in ("pip install puckworks\n", "pip', 'install', 'puckworks'", "releases/latest",
                "github.com/trbrewer/puckworks/archive", "main.zip"):
        assert bad not in code_text, f"notebook does an unpinned/mutable install: {bad!r}"


def test_release_wheel_url_and_hash_are_pinned_to_v030(code_text):
    # Milestone C: the default path targets the exact immutable v0.3.0 Release asset + SHA-256.
    assert "RELEASED = True" in code_text
    assert "releases/download/v0.3.0/puckworks-0.3.0-py3-none-any.whl" in code_text
    import re
    assert re.search(r"WHEEL_SHA256 = '[0-9a-f]{64}'", code_text), "wheel SHA-256 must be pinned"
    assert "puckworks-0.3.0-py3-none-any.whl" in code_text


def test_hash_verification_precedes_installation(code_text):
    # the SHA-256 machinery and mismatch refusal must appear before the pip install call
    assert "_sha256(" in code_text and "WHEEL_SHA256" in code_text
    i_hash = code_text.index("WHEEL_SHA256")
    i_install = code_text.index("pip', 'install'") if "pip', 'install'" in code_text \
        else code_text.index("pip")
    assert i_hash < i_install, "hash constant/verification must precede the install call"
    assert "SHA-256 mismatch" in code_text


def test_no_broad_exception_swallowing(code_text):
    assert "except Exception" not in code_text and "except:" not in code_text


def test_default_controls_are_in_domain():
    import puckworks.product as p
    r, c = p.load_pull_preset("guided_v1")
    # the notebook's default #@param values equal the in-domain guided_v1 preset
    assert (r.dose_g, r.target_beverage_g, r.pressure_bar, r.grind_setting) == (20.0, 40.0, 9.0, 1.7)
    run = p.simulate_pull(r, c)
    assert run.completion_state == "completed"     # defaults produce a clean, in-domain run


def test_unsupported_controls_are_absent(nb):
    # only #@param declaration lines are controls; forbid unsupported knobs there (the words
    # "flavor"/"taste" still appear in the disclaimers, which is correct).
    param_lines = []
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            for ln in "".join(c["source"]).splitlines():
                if "#@param" in ln:
                    param_lines.append(ln.lower())
    joined = "\n".join(param_lines)
    for bad in ("preinfusion", "basket", "particle_radius", "pressure_profile", "flavor", "taste",
                "lens"):
        assert bad not in joined, f"notebook exposes an unsupported control: {bad!r}"
    # the exposed controls are exactly the honest guided_v1 knobs
    assert "dose_g" in joined and "grind_setting" in joined and "coffee_profile" in joined


def test_honesty_statements_present(text):
    low = text.lower()
    assert "recorded-only" in low or "recorded with the recipe" in low   # temperature
    assert "label only" in low or "descriptive only" in low              # bean_label metadata
    assert "not modeled" in low and "saturated" in low                   # wetting/first drip
    assert "composition" in low and "not" in low                         # composition not flavor


def test_completion_marker_present(code_text):
    assert "GUIDED_PULL_COMPLETE" in code_text

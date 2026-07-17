"""README quality gates for the public homepage (issue #41 / docs/PUBLIC_EXPERIENCE.md).

These are offline, deterministic checks. They protect the newcomer-facing surface from the most
common ways it goes wrong: a false PyPI claim, a stale/removed public-API name, a broken local
image or link, missing alt text, an out-of-date generated pulse block, or hidden control
characters. Network is never touched.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
README = REPO_ROOT / "README.md"
TEXT = README.read_text(encoding="utf-8")

# A documented maximum: the README is a landing page, not the whole doc site.
README_MAX_BYTES = 16_000


def test_readme_exists_and_bounded():
    assert README.exists()
    size = len(TEXT.encode("utf-8"))
    assert size <= README_MAX_BYTES, f"README is {size} bytes (> {README_MAX_BYTES}); keep it focused"


@pytest.mark.parametrize(
    "needle",
    [
        "Evidence-first models for what happens inside an espresso puck",  # mission
        "registry",           # what it is
        "validation gates",   # process
        "public value",       # value section (case-insensitive checked below)
    ],
)
def test_mission_and_value_sections_present(needle):
    assert needle.lower() in TEXT.lower(), f"README missing required content: {needle!r}"


def test_colab_link_targets_the_quickstart_notebook():
    target = ("colab.research.google.com/github/trbrewer/puckworks/blob/main/"
              "notebooks/puckworks_quickstart_colab.ipynb")
    assert target in TEXT, "README must link the CPU quickstart notebook in Colab"
    assert (REPO_ROOT / "notebooks" / "puckworks_quickstart_colab.ipynb").exists()


def test_public_release_link_present():
    assert "releases/latest" in TEXT or "releases/tag/v0.2.0" in TEXT


def test_current_status_link_present():
    assert "docs/planning/STATE_OF_TRUTH.md" in TEXT


def test_api_documentation_link_present():
    assert "docs/API.md" in TEXT


def test_no_false_pypi_install_command():
    # A bare `pip install puckworks` (or `puckworks==x`) would falsely imply a PyPI package.
    # The only allowed forms install a .whl file or a release URL.
    for m in re.finditer(r"pip install\s+([^\s`)]+)", TEXT):
        target = m.group(1)
        if target.startswith("puckworks"):
            assert target.endswith(".whl"), (
                f"README advertises a PyPI-style install {target!r}; puckworks is not on PyPI"
            )


def test_no_rights_blocked_data_described_as_available():
    lowered = TEXT.lower()
    # The Visualizer corpus is gitignored and NOT redistributed; the README must not offer it.
    assert "visualizer" not in lowered, "README must not reference the non-redistributable Visualizer corpus"


def test_no_removed_public_api_name_advertised():
    import puckworks

    allowed = set(puckworks.__all__) | {"__all__"}
    # Inspect the paragraph that advertises the supported public API.
    para = TEXT.split("supported public API", 1)
    assert len(para) == 2, "README must describe the supported public API"
    # Backticked identifiers in the two sentences following the phrase.
    snippet = para[1][:600]
    names = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", snippet))
    unknown = {n for n in names if n not in allowed}
    assert not unknown, f"README advertises non-exported API names: {sorted(unknown)}"


def test_generated_pulse_block_is_current():
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "update_readme_pulse.py"), "--verify"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"README pulse block is stale:\n{r.stdout}\n{r.stderr}"


def _readme_image_tags():
    """Yield (src, alt) for every <img> and markdown image in the README."""
    for m in re.finditer(r"<img\b[^>]*>", TEXT):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag)
        alt = re.search(r'alt="([^"]*)"', tag)
        yield (src.group(1) if src else None), (alt.group(1) if alt else None)
    for m in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", TEXT):
        yield m.group(2), m.group(1)


def test_every_local_image_path_exists():
    # <source srcset=...> too (dark-mode hero).
    srcsets = re.findall(r'srcset="([^"]+)"', TEXT)
    imgs = [src for src, _ in _readme_image_tags() if src]
    for src in imgs + srcsets:
        if src.startswith("http"):
            continue
        assert (REPO_ROOT / src).exists(), f"README references missing local image: {src}"


def test_every_image_has_meaningful_alt_text():
    for src, alt in _readme_image_tags():
        assert alt is not None, f"image {src!r} has no alt attribute"
        assert len(alt.strip()) >= 15, f"image {src!r} has weak alt text: {alt!r}"


def test_relative_markdown_links_resolve():
    for m in re.finditer(r"\]\(([^)]+)\)", TEXT):
        target = m.group(1).strip()
        if target.startswith(("http://", "https://", "#", "mailto:")):
            continue
        path = target.split("#", 1)[0]
        if not path:
            continue
        assert (REPO_ROOT / path).exists(), f"README relative link does not resolve: {target}"


def test_no_hidden_or_bidi_control_characters():
    forbidden = {
        "​", "‌", "‍", "‎", "‏",   # zero-width / LTR-RTL marks
        "‪", "‫", "‬", "‭", "‮",   # bidi embedding/override
        "⁦", "⁧", "⁨", "⁩",             # bidi isolates
        "﻿",                                             # BOM / zero-width no-break space
    }
    present = sorted({hex(ord(c)) for c in TEXT if c in forbidden})
    assert not present, f"README contains hidden/bidi control characters: {present}"


def test_objective_value_process_precede_contributor_detail():
    def idx(anchor):
        i = TEXT.find(anchor)
        assert i != -1, f"README missing section: {anchor}"
        return i

    why = idx("## Why Puckworks exists")
    process = idx("## How evidence moves through the system")
    contribute = idx("## Contribute")
    assert why < contribute and process < contribute, (
        "objective/value/process must appear before deep contributor detail"
    )

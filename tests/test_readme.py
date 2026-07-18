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


def test_hero_uses_the_maintainer_logo():
    # 5C-11: the selected hero path is the maintainer-supplied logo under the canonical asset dir.
    hero = "docs/assets/readme/hero_image_logo.png"
    assert hero in TEXT, "README hero must reference the maintainer logo"
    assert (REPO_ROOT / hero).exists(), "the maintainer hero logo file must exist"


def test_guided_pull_colab_cta_is_live():
    low = TEXT.lower()
    assert "guided espresso pull" in low
    assert "docs/GUIDED_ESPRESSO_PULL.md" in TEXT
    # the guided notebook is now an active one-click Colab CTA
    assert ("colab.research.google.com/github/trbrewer/puckworks/blob/main/"
            "notebooks/guided_espresso_pull_colab.ipynb") in TEXT
    # both distinct paths are offered
    assert "puckworks_quickstart_colab.ipynb" in TEXT
    assert "explore the component registry" in low and "run a guided espresso pull" in low
    # the old upcoming/not-released wording is gone
    assert "not released yet" not in low and "coming in v0.3.0" not in low


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
    # Built via chr() so no literal hidden/bidi character sits in this source file (a control-char
    # scan of the test file itself stays clean).
    forbidden = {chr(c) for c in (
        0x200B, 0x200C, 0x200D, 0x200E, 0x200F,   # zero-width / LTR-RTL marks
        0x202A, 0x202B, 0x202C, 0x202D, 0x202E,   # bidi embedding/override
        0x2066, 0x2067, 0x2068, 0x2069,           # bidi isolates
        0xFEFF,                                   # BOM / zero-width no-break space
    )}
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


# ══════════════════════════════════════════════════════════════════════════════════
# PR #44 finalize: release-record, evidence CTA, gate language, docs, notebook (Phase 8)
# ══════════════════════════════════════════════════════════════════════════════════
import json  # noqa: E402

NOTEBOOK = REPO_ROOT / "notebooks" / "puckworks_quickstart_colab.ipynb"
_NB = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
NB_TEXT = "\n".join("".join(c["source"]) for c in _NB["cells"])
CURRENT_DOCS = [REPO_ROOT / "README.md", REPO_ROOT / "docs" / "ACCESSIBILITY.md",
                REPO_ROOT / "docs" / "PUBLIC_EXPERIENCE.md"]


def _record():
    sys.path.insert(0, str(REPO_ROOT / "tools"))
    import release_record
    return release_record.load_validated(REPO_ROOT / "docs" / "status" / "public_release.json")


def test_evidence_cta_targets_public_readme():
    assert "[🔬 Explore the evidence](docs/public/README.md)" in TEXT
    assert (REPO_ROOT / "docs" / "public" / "README.md").exists()


def test_learn_architecture_is_a_separate_path():
    assert "Learn the architecture" in TEXT and "docs/ONBOARDING.md" in TEXT


def test_pulse_preserves_distinct_gate_counts_not_all_green():
    block = TEXT.split("puckworks-pulse:start")[1].split("puckworks-pulse:end")[0]
    assert "PASS" in block and "ACKNOWLEDGED_EXCEPTION" in block
    assert "all gates green" not in block
    assert "documented gate policy" in block


def test_pulse_release_facts_come_from_the_validated_record():
    rec = _record()
    block = TEXT.split("puckworks-pulse:start")[1].split("puckworks-pulse:end")[0]
    assert rec["tag"] in block and rec["wheel_filename"] in block


def test_no_bare_pypi_install_in_any_current_doc():
    for doc in CURRENT_DOCS:
        text = doc.read_text(encoding="utf-8")
        for m in re.finditer(r"pip install\s+([^\s`)]+)", text):
            target = m.group(1)
            if target.startswith("puckworks"):
                assert target.endswith(".whl"), f"{doc.name}: bare PyPI install {target!r}"


def test_current_md_lists_the_new_authorities():
    cur = (REPO_ROOT / "docs" / "CURRENT.md").read_text(encoding="utf-8")
    assert "docs/PUBLIC_EXPERIENCE.md" in cur
    assert "docs/ACCESSIBILITY.md" in cur
    assert "status/public_release.json" in cur


def test_package_description_is_evidence_first():
    pyproject = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^description\s*=\s*"([^"]+)"', pyproject, re.M)
    assert m, "no package description"
    desc = m.group(1)
    assert desc != "Component registry for espresso process models"
    assert "Evidence-first" in desc and len(desc) <= 200


# ── notebook (Phase 6) ──────────────────────────────────────────────────────────────
def test_notebook_release_link_is_tag_not_download_dir():
    rec = _record()
    assert f"releases/tag/{rec['tag']}" in NB_TEXT
    # no link to the bare (incomplete) download-directory URL
    assert not re.search(rf"releases/download/{re.escape(rec['tag'])}\s*[)\]\s]", NB_TEXT)


def test_notebook_expected_wheel_hash_equals_record():
    rec = _record()
    assert rec["wheel_sha256"] in NB_TEXT, "notebook wheel hash must equal public_release.json"
    assert rec["wheel_filename"] in NB_TEXT


def test_notebook_verifies_hash_before_installing():
    assert "urlretrieve" in NB_TEXT
    assert "sha256" in NB_TEXT.lower()
    assert "refusing to install" in NB_TEXT.lower() or "mismatch" in NB_TEXT.lower()


def test_notebook_does_not_catch_broad_exception():
    assert "except Exception" not in NB_TEXT, "broad except can hide a real notebook bug"
    assert "except ImportError" in NB_TEXT


def test_notebook_uses_only_released_public_apis():
    import puckworks
    referenced = set(re.findall(r"puckworks\.([A-Za-z_][A-Za-z0-9_]*)", NB_TEXT))
    allowed = set(puckworks.__all__) | {"__file__"}
    unknown = referenced - allowed
    assert not unknown, f"notebook references non-public/unreleased API: {sorted(unknown)}"
    assert "puckworks.product" not in NB_TEXT     # product is unreleased (not in v0.2.0)


def test_notebook_has_no_committed_outputs():
    for c in _NB["cells"]:
        if c["cell_type"] == "code":
            assert not c.get("outputs")
            assert c.get("execution_count") in (None,)


def test_notebook_has_completion_marker():
    assert "QUICKSTART_COMPLETE" in NB_TEXT


# ── PR #44 REQUEST-CHANGES corrections: gate + platform wording (3E/3F) ─────────────
def test_readme_gate_sentence_matches_gatestatus_enum():
    import puckworks
    enum_names = {s.value for s in puckworks.GateStatus}   # PASS/FAIL/SKIP/ERROR/ACKNOWLEDGED_EXCEPTION
    # the "What it does" gate bullet must name exactly the real status set (no narrowing)
    para = TEXT.split("Validation gates**", 1)[1][:400]
    named = {w for w in re.findall(r"\b[A-Z][A-Z_]+\b", para)}
    named &= enum_names | {"PASS", "FAIL", "SKIP", "ERROR", "ACKNOWLEDGED_EXCEPTION"}
    assert named == enum_names, f"README gate sentence names {named}, enum is {enum_names}"


def test_readme_distinguishes_os_and_interpreter_coverage():
    # OS smoke is Python 3.12; interpreter coverage names the tested versions separately.
    assert "under Python 3.12" in TEXT
    assert "3.10, 3.12, and 3.13" in TEXT
    # must not claim the full 3.10–3.13 range is smoke-tested across all OSes
    assert "Windows, macOS, and Linux** (Python 3.10" not in TEXT


def test_readme_does_not_overpromise_colab_duration():
    assert "five minutes" not in TEXT


# ── 2F: public-experience reminder scheduled write is opt-in ────────────────────────
def test_public_experience_reminder_scheduled_write_is_opt_in():
    # Text search (no pyyaml — not a public-branch dev dependency).
    wf = (REPO_ROOT / ".github" / "workflows" / "public-experience-review.yml").read_text(encoding="utf-8")
    assert "ENABLE_PUBLIC_EXPERIENCE_REMINDERS == 'true'" in wf
    assert "refs/heads/main" in wf and "workflow_dispatch" in wf


# ── 2E: README public-API wording is a curated subset, not a false-exact list ───────
def test_readme_api_names_subset_of_all_and_not_false_exact():
    import puckworks
    para = TEXT.split("supported public API", 1)[1][:400]
    names = set(re.findall(r"`([A-Za-z_][A-Za-z0-9_]*)`", para))
    names.discard("__all__")
    assert names and names <= set(puckworks.__all__), f"advertised {names - set(puckworks.__all__)} not in __all__"
    # wording must present the list as a selection, not claim the parenthetical IS the whole __all__
    assert "selected commonly-used entry points" in TEXT.lower()


# ── PR#44 Blocker 2: authoritative gate vocabulary must not drift from enum/README ──
def test_public_experience_gate_vocabulary_matches_enum():
    import puckworks
    doc = (REPO_ROOT / "docs" / "PUBLIC_EXPERIENCE.md").read_text(encoding="utf-8")
    enum_names = {s.value for s in puckworks.GateStatus}   # PASS/FAIL/SKIP/ERROR/ACKNOWLEDGED_EXCEPTION
    # the authority doc's gate section must name exactly the full GateStatus set
    section = doc.split("A validation gate reports", 1)
    assert len(section) == 2, "PUBLIC_EXPERIENCE.md must describe gate statuses"
    snippet = section[1][:800]
    named = {w for w in re.findall(r"\b[A-Z][A-Z_]+\b", snippet)} & enum_names
    assert named == enum_names, f"authority doc names {named}, enum is {enum_names}"
    # semantics present: FAIL/ERROR suite-failing, SKIP not a pass, ACK never a pass
    low = snippet.lower()
    assert "suite-failing" in low and "never" in low

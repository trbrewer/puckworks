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

# A documented maximum. The physics-first landing page carries the full stage-by-stage model map,
# the dataset inventory, and the references section inline, so the cap is larger than a bare hero page.
README_MAX_BYTES = 50_000  # grows with the dataset-card bibliography (references-coverage is enforced)


def test_readme_exists_and_bounded():
    assert README.exists()
    size = len(TEXT.encode("utf-8"))
    assert size <= README_MAX_BYTES, f"README is {size} bytes (> {README_MAX_BYTES}); keep it focused"


def test_opening_is_physics_first():
    """The homepage leads with the physical espresso process, not the governance machinery.

    The first screen (before the first '## ' section heading) must name espresso and physics and
    frame the models as separate/testable — and must NOT open by foregrounding the internal
    vocabulary (contract/registry/provenance/validation gate), which the page defines later, in
    plain language, as the *means* of trustworthiness.
    """
    opening = TEXT.split("\n## ", 1)[0].lower()
    assert "espresso" in opening and "physics" in opening, "opening must lead with espresso physics"
    assert "separate" in opening and "testable" in opening, "opening must frame models as separate/testable"
    # governance jargon is introduced later (in 'How Puckworks checks its work'), not up top
    for jargon in ("contract", "registry", "provenance", "validation gate"):
        assert jargon not in opening, f"opening should not foreground {jargon!r} before it is explained"


@pytest.mark.parametrize(
    "needle",
    [
        "the espresso pull, modeled stage by stage",  # physics-first section
        "registry",           # defined in plain language in the checks section
        "validation gates",   # the automated checks
        "references",         # bibliography near the bottom
    ],
)
def test_required_sections_present(needle):
    assert needle.lower() in TEXT.lower(), f"README missing required content: {needle!r}"


def test_physics_first_section_order():
    """Physics → what-you-can-run → data → how-we-check → install → references (bottom)."""
    def idx(anchor):
        i = TEXT.find(anchor)
        assert i != -1, f"README missing section: {anchor}"
        return i

    stages = idx("## The espresso pull, modeled stage by stage")
    run = idx("## What you can run today")
    data = idx("## Data used to check the models")
    checks = idx("## How Puckworks checks its work")
    install = idx("## Install the public release")
    references = idx("## References")
    # physics leads; the model map precedes the trust machinery; references sit near the bottom
    assert stages < run < data < checks, "physics/models/data must precede the how-we-check section"
    assert idx("puckworks-model-map:start") < checks, "the stage-by-stage model map precedes the checks section"
    assert install < references, "references belong near the bottom, after install"
    assert references > TEXT.find("## Current limits"), "references follow the limitations section"


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


def test_flat_valley_pages_cta_is_live():
    # the third public path points at the deployed GitHub Pages interactive
    assert "https://trbrewer.github.io/puckworks/flat-valley/" in TEXT
    assert "cup hides the clock" in TEXT.lower()
    # keeps the two Colab paths
    assert "puckworks_quickstart_colab.ipynb" in TEXT
    assert "guided_espresso_pull_colab.ipynb" in TEXT


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


def test_process_precedes_contributor_detail():
    def idx(anchor):
        i = TEXT.find(anchor)
        assert i != -1, f"README missing section: {anchor}"
        return i

    stages = idx("## The espresso pull, modeled stage by stage")
    process = idx("## How Puckworks checks its work")
    contribute = idx("## Contribute")
    assert stages < contribute and process < contribute, (
        "the physics overview and the how-we-check process must appear before deep contributor detail"
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


def test_relay_warning_is_isolated_from_utility_links():
    """The Espresso Model Relay disclaimer is its OWN blockquote; the general repository utility links
    render as a normal paragraph after a blank line — not lazily continued inside the Relay warning
    quote (which would make repo navigation look like part of the Relay caveat)."""
    lines = TEXT.splitlines()
    warn = next((i for i, ln in enumerate(lines)
                 if ln.startswith("> ") and "Espresso Model Relay" in ln and "assumption-rich" in ln), None)
    assert warn is not None, "the Relay disclaimer blockquote is missing"
    dl = next((i for i, ln in enumerate(lines) if "Download the latest public release" in ln), None)
    assert dl is not None, "the utility links (Download the latest public release) are missing"
    # the utility-link paragraph must NOT be a blockquote line, and must be separated from the warning
    assert not lines[dl].lstrip().startswith(">"), "utility links must render outside the Relay blockquote"
    assert dl > warn and any(lines[j].strip() == "" for j in range(warn + 1, dl)), \
        "a blank line must separate the Relay warning from the utility-link paragraph"
    # the onboarding callout remains its own blockquote
    assert any(ln.startswith("> ") and "New session" in ln for ln in lines), \
        "the onboarding callout must remain its own blockquote"


def test_top_badge_table_offers_all_four_colab_paths():
    for label in ("Full Laboratory Tour", "Espresso Model Relay", "Guided Espresso Pull", "Quickstart"):
        assert label in TEXT, f"the top navigation must offer the {label!r} path"
    for nb in ("guided_pull_laboratory_colab.ipynb", "illustrative_linked_pull_colab.ipynb",
               "guided_espresso_pull_colab.ipynb", "puckworks_quickstart_colab.ipynb"):
        assert f"notebooks/{nb}" in TEXT, f"the top navigation must link {nb}"
        assert (REPO_ROOT / "notebooks" / nb).exists(), f"linked notebook missing: {nb}"


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
    # the gate sentence (in 'How Puckworks checks its work') must name exactly the real status set.
    # Anchor on the plain-language definition, which precedes the pulse table's gate row.
    low = TEXT.lower()
    i = low.find("**validation gates**")
    assert i != -1, "README must define validation gates in the checks section"
    para = TEXT[i:i + 400]
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


# ══════════════════════════════════════════════════════════════════════════════════
# Physics-first rewrite: model-map / data-inventory / references coverage + assets
# ══════════════════════════════════════════════════════════════════════════════════
import csv  # noqa: E402

CARDS = REPO_ROOT / "docs" / "cards"


def _marked_block(name):
    start = f"<!-- puckworks-{name}:start -->"
    end = f"<!-- puckworks-{name}:end -->"
    assert start in TEXT and end in TEXT, f"README missing {name} markers"
    return TEXT.split(start, 1)[1].split(end, 1)[0]


# Registered component id -> the model card that is the source of truth for its physics.
# Project models under puckworks/models/brewer2026/ have no external card and are excluded here.
_COMPONENT_CARD = {
    "cameron2020.extraction_bdf": "cameron2020",
    "pannusch2024.solver": "pannusch2024",
    "pannusch2024.closures": "pannusch2024",
    "waszkiewicz2025.poroelastic": "waszkiewicz2025",
    "grudeva2025.reduced": "grudeva2025",
    "liang2021.desorption": "liang2021",
    "mo2023_2.swelling": "mo2023_2",
    "mo2023_2.coupled_bed": "mo2023_2",
    "moroney2016.surrogate": "moroney2016",
    "romancorrochano2017.extraction": "romancorrochano2017_extraction",
    "fasano2000_partI.fines_migration": "fasano2000_partI",
    "foster2025.infiltration": "foster2025",
    "foster2025.machine_mode": "foster2025_2",
    "wadsworth2026.permeability": "wadsworth2026",
    "wadsworth2026.grindmap": "wadsworth2026_grindmap",
    "wadsworth2026.inertial": "wadsworth2026_inertial",
    "lee2023.feedback": "lee2023",
    "sourcing2026.g10_liquor_rheology": "g10_liquor_rheology",
    "sourcing2026.g1_glassbead_analog": "g1_glassbead_analog",
    "sourcing2026.g3_pump_characteristic": "g3_pump_characteristic",
    "brewer2026.coupled_kappa_t": "brewer2026_coupled_kappa_t",
}

# Rights-restricted source: its raw corpus is not redistributable, so the README must not advertise
# it. Documented exception to reference coverage (see test_no_rights_blocked_data_described_as_available).
_REFERENCE_EXCEPTIONS = {"visualizer_coffee"}


def _registered_components():
    import puckworks
    puckworks.load_builtin_components()
    return sorted(c.name for c in puckworks.components())


def test_model_map_covers_every_registered_component():
    """Every model in the live registry appears in the near-top stage map, with the true count."""
    block = _marked_block("model-map")
    comps = _registered_components()
    missing = [c for c in comps if f"`{c}`" not in block]
    assert not missing, f"model map omits registered components: {missing}"
    # the displayed count is derived from the registry, not hard-coded to a stale number
    m = re.search(r"\*\*(\d+) registered models\*\*", block)
    assert m, "model map must state how many models are registered"
    assert int(m.group(1)) == len(comps), (
        f"model map shows {m.group(1)} models but the registry has {len(comps)}"
    )


def test_model_map_marks_the_guided_pull_chain():
    """Exactly the model the product executes is flagged; the rest are separate lenses."""
    block = _marked_block("model-map")
    assert "Runs in Guided Pull" in block, "the model map must flag the Guided Pull chain"
    # the executed model is Cameron's extraction chain; its row carries the flag
    cam_row = next((ln for ln in block.splitlines() if "`cameron2020.extraction_bdf`" in ln), "")
    assert "Runs in Guided Pull" in cam_row, "cameron2020.extraction_bdf must be flagged as the Guided Pull chain"


def _required_reference_cards():
    """Cards backing a registered component OR an active manifest dataset — the set the References
    section must represent, minus documented rights exceptions."""
    required = set()
    for name in _registered_components():
        stem = _COMPONENT_CARD.get(name)
        if stem and (CARDS / f"{stem}.md").exists():
            required.add(stem)
    with open(REPO_ROOT / "puckworks" / "data" / "MANIFEST.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for tok in re.findall(r"[A-Za-z][A-Za-z0-9_]+", row.get("source_card", "")):
                if (CARDS / f"{tok}.md").exists():
                    required.add(tok)
    return required - _REFERENCE_EXCEPTIONS


def test_references_cover_every_relevant_card():
    block = _marked_block("references")
    linked = set(re.findall(r"docs/cards/([A-Za-z0-9_]+)\.md", block))
    missing = sorted(_required_reference_cards() - linked)
    assert not missing, f"References section omits cards for active components/datasets: {missing}"


def test_reference_links_resolve_and_no_restricted_corpus():
    block = _marked_block("references")
    for stem in re.findall(r"docs/cards/([A-Za-z0-9_]+)\.md", block):
        assert (CARDS / f"{stem}.md").exists(), f"reference links a missing card: {stem}"
    # the rights-restricted corpus is never advertised as a citable source in the bibliography
    assert "visualizer" not in block.lower()


def test_data_inventory_families_and_vocabulary():
    block = _marked_block("data-inventory")
    low = block.lower()
    # the evidence-strength vocabulary a reader needs to weigh each dataset
    for level in ("independent", "post-fit reconstruction", "verification", "reference"):
        assert level in low, f"data inventory must explain the {level!r} evidence level"
    # a representative spread of active source families is named (not a single dump row)
    for family in ("Waszkiewicz", "Wadsworth", "Schmieder", "Pannusch", "Foster", "Liang",
                   "Roman-Corrochano", "Angeloni", "Telis-Romero", "Khomyakov"):
        assert family in block, f"data inventory omits the {family} source family"
    # the non-redistributable corpus is not listed as available data
    assert "visualizer" not in low
    # the inventory points at the row-level manifest
    assert "puckworks/data/MANIFEST.csv" in block


# ── evidence-pipeline SVG: structural + no-overflow-by-construction checks ───────────
import xml.etree.ElementTree as ET  # noqa: E402

SVG_PATH = REPO_ROOT / "docs" / "assets" / "readme" / "evidence-pipeline.svg"
_SVG_NS = "{http://www.w3.org/2000/svg}"


def test_evidence_svg_is_accessible_and_scalable():
    root = ET.parse(SVG_PATH).getroot()
    assert root.get("viewBox"), "SVG must declare a viewBox so it scales at any display width"
    assert root.find(f"{_SVG_NS}title") is not None, "SVG needs a <title> for assistive tech"
    assert root.find(f"{_SVG_NS}desc") is not None, "SVG needs a <desc> for assistive tech"
    labelled = (root.get("aria-labelledby") or "").split()
    assert {"ep-title", "ep-desc"} <= set(labelled), "aria-labelledby must reference title and desc ids"
    # foreignObject text does not render on GitHub; wrapping must use native tspans instead
    assert not any(True for _ in root.iter(f"{_SVG_NS}foreignObject")), "no foreignObject text"


def test_evidence_svg_is_single_column_without_overlap():
    root = ET.parse(SVG_PATH).getroot()
    vb = [float(v) for v in root.get("viewBox").split()]
    boxes = []
    for g in root.findall(f"{_SVG_NS}g"):
        r = g.find(f"{_SVG_NS}rect")
        if r is None:
            continue
        boxes.append(tuple(float(r.get(k)) for k in ("x", "y", "width", "height")))
    assert len(boxes) >= 6, "the pipeline needs its six stage boxes"
    # single column: every box shares the same x and width
    xs = {round(x, 1) for x, _, _, _ in boxes}
    ws = {round(w, 1) for _, _, w, _ in boxes}
    assert len(xs) == 1 and len(ws) == 1, "boxes must form one column (shared x and width)"
    # vertical stacking never overlaps and every box stays inside the viewBox height
    boxes.sort(key=lambda b: b[1])
    for (_, y1, _, h1), (_, y2, _, _) in zip(boxes, boxes[1:]):
        assert y1 + h1 < y2, "stage boxes must not vertically overlap"
    x, y, w, h = boxes[-1]
    assert y + h <= vb[3], "the last box must fit inside the viewBox height (nothing clipped)"


# ── MANIFEST.csv integrity: well-formed rows, stable schema ─────────────────────────
MANIFEST = REPO_ROOT / "puckworks" / "data" / "MANIFEST.csv"
_MANIFEST_COLUMNS = [
    "dataset_id", "source_card", "source_artifact", "extraction_method",
    "units_as_published", "units_in_registry", "uncertainty_retained",
    "license_access", "gate_use", "validation_strength", "caveat",
]


def test_manifest_is_well_formed():
    raw = MANIFEST.read_bytes()
    # CRLF line endings are the committed convention; a lone-LF row signals a mangled edit
    assert b"\r\n" in raw, "MANIFEST.csv uses CRLF line endings"
    text = raw.decode("utf-8")
    rows = list(csv.reader(text.splitlines()))
    assert rows, "MANIFEST.csv is empty"
    header = rows[0]
    assert header == _MANIFEST_COLUMNS, f"MANIFEST schema drift: {header}"
    ncol = len(header)
    for i, row in enumerate(rows[1:], start=2):
        if not any(cell.strip() for cell in row):
            continue
        assert len(row) == ncol, f"MANIFEST row {i} has {len(row)} fields (expected {ncol}): {row[:2]}"
        assert row[0].strip(), f"MANIFEST row {i} has an empty dataset_id"


def test_manifest_source_cards_reference_real_cards_or_registry():
    """Every source_card token that looks like a card names an existing card file."""
    with open(MANIFEST, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cell = row.get("source_card", "")
            for tok in re.findall(r"[a-z][a-z0-9_]{3,}", cell):
                # tokens that match a card filename must resolve; prose words (e.g. 'registry',
                # 'permeability', 'one', 'paper') simply won't match a file and are ignored.
                if tok.endswith(("2000", "2001", "2016", "2017", "2019", "2020", "2021",
                                 "2023", "2024", "2025", "2026")) or tok.startswith(("g1_", "g3_", "g10_")):
                    # exact card, or a split-card family (e.g. romancorrochano2017 -> _extraction/_permeability)
                    resolves = (CARDS / f"{tok}.md").exists() or any(CARDS.glob(f"{tok}_*.md"))
                    assert resolves or tok in {"table1_full"}, (
                        f"source_card token {tok!r} looks like a card but no {tok}[_*].md exists"
                    )

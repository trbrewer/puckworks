"""Round-11 P1-6 and P2-1: what the submission scanner can be shown, and what it must not miss.

P1-6. `_visible_text` described itself as "what a reader sees" and was two regexes: replace
`[text](target)` with `text`, collapse whitespace. It therefore could not see through the most
ordinary markup in the language. Every one of these returned CLEAN at the reviewed commit:

    An earlier **version** was wrong.                       An earlier ver**sion** was wrong.
    An earlier <em>version</em> was wrong.                  An earlier&nbsp;version was wrong.
    The second *review* asked for this.
    See [the internal analysis](docs/internal/review.md) for details.

The first group is round-10 P2-1 one level down: a phrase invisible to the scanner and plainly
visible on the page. The link case is different in kind — discarding TARGETS is right for prose
(the SI's own figure filenames are not leaked identifiers) and wrong for leakage, because the
target ships in the submitted source and surfaces in conversion, accessibility metadata and editor
inspection.

Scope was wrong too: `internal_path` and `internal_narration` applied to the manuscript and
supplement only, while the cover letter, the Highlights file and the standalone captions all go to
the journal.

P2-1. Caption extraction ran from a `### Figure N` heading to the next `###` or end of file. Figure
4 is the last `###` before the supplementary section, so its caption absorbed the horizontal rule
and the `## Supplementary figures` heading, and the renderer emitted a second one. Every freshness
and parity check stayed green, because the upload file exactly equalled the generator's malformed
output — equality to a generator establishes reproducibility, not validity.
"""
from __future__ import annotations

import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import paper_a_consistency as C  # noqa: E402
from tools import paper_a_figure_captions as FC  # noqa: E402

pytestmark = pytest.mark.skipif(
    C._MD is None, reason="markdown-it-py absent; structural scanning reports NOT RUN (tested "
                          "separately by test_a_missing_parser_blocks_rather_than_passing)")

#: Every reproduced bypass, and the string the diagnostic must name.
BYPASSES = [
    ("An earlier **version** was wrong.", "earlier version"),
    ("An earlier <em>version</em> was wrong.", "earlier version"),
    ("An earlier ver**sion** was wrong.", "earlier version"),
    ("An earlier <b>ver</b>sion was wrong.", "earlier version"),
    ("An earlier&nbsp;version was wrong.", "earlier version"),
    ("An earlier _version_ was wrong.", "earlier version"),
    ("The second *review* asked for this.", "review"),
    ("> An earlier **version** was wrong.", "earlier version"),
    ("### An earlier **version** was wrong", "earlier version"),
    ("- The second *review* asked for this.", "review"),
    ("| Note | An earlier **version** was wrong |\n|---|---|\n| a | b |", "earlier version"),
    ("See [the internal analysis](docs/internal/review.md) for details.",
     "docs/internal/review.md"),
    ("See [the internal analysis][internal].\n\n[internal]: docs/internal/review.md",
     "docs/internal/review.md"),
    ('See <a href="docs/internal/review.md">analysis</a>.', "docs/internal/review.md"),
    ("See [analysis](docs%2Finternal%2Freview.md).", "docs/internal/review.md"),
    ("[^1]: See [analysis](docs/internal/review.md).", "docs/internal/review.md"),
    ("`docs/internal/review.md`", "docs/internal/review.md"),
    ("![diagram](docs/internal/review.md)", "docs/internal/review.md"),
]

#: The upload deliverables. All of them: an internal path in the cover letter reaches the editor
#: exactly as surely as one in the manuscript.
UPLOAD_TARGETS = ("CONVERSION", "SUPPLEMENT", "COVER_LETTER", "UPLOAD_CAPTIONS", "HIGHLIGHTS")

_REDIRECTED = ("CONVERSION", "PACKAGE", "HIGHLIGHTS", "COVER_LETTER", "SUPPLEMENT",
               "UPLOAD_CAPTIONS", "CANONICAL", "SUBMISSION_FILES")


@pytest.fixture
def only(tmp_path, monkeypatch):
    """Scan exactly ONE upload file, with the injected text appended.

    The copy keeps its original BASENAME, because rule scope is keyed on it — a fixture that
    renamed the file would scope every rule out and report a serene, meaningless zero.
    """
    def _install(attr, injected):
        src = getattr(C, attr)
        dst = tmp_path / attr / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, dst)
        dst.write_text(dst.read_text(encoding="utf-8") + "\n\n" + injected + "\n",
                       encoding="utf-8")
        for name in _REDIRECTED:
            if name != "SUBMISSION_FILES":
                monkeypatch.setattr(C, name, dst.parent / "absent.md")
        monkeypatch.setattr(C, attr, dst)
        monkeypatch.setattr(C, "SUBMISSION_FILES", (dst,))
        monkeypatch.setattr(C, "CANONICAL", dst.parent / "absent.md")
        return dst
    return _install


# ── 1. every bypass, on every upload deliverable ────────────────────────────────────────────
@pytest.mark.parametrize("target", UPLOAD_TARGETS)
@pytest.mark.parametrize("injected,expect", BYPASSES, ids=[b[0][:34] for b in BYPASSES])
def test_no_markup_or_link_bypass_survives_on_any_upload_file(only, target, injected, expect):
    only(target, injected)
    problems = C._placeholders_and_process_language()
    assert any(expect in p for p in problems), (target, injected, problems[:3])


def test_the_committed_tree_is_clean_under_the_widened_scope():
    assert C._placeholders_and_process_language() == []


# ── 2. the two channels are genuinely separate ──────────────────────────────────────────────
def test_a_link_target_is_still_not_read_as_prose():
    """Discarding targets was right for PROSE semantics, and that must not regress: the SI's own
    figure filenames are the names of files the editor receives, not leaked identifiers."""
    blocks = C._visible_paragraphs("![Supplementary Figure S1](figures/fig3_holdouts.png)\n")
    assert blocks == [(1, "Supplementary Figure S1")]
    assert not any("fig3_holdouts" in text for _ln, text in blocks)


def test_a_submitted_figure_filename_passes_only_through_the_narrow_allowlist(only):
    only("CONVERSION", "![Figure 1](figures/fig1_design.png)")
    assert not any("fig1_design" in p for p in C._placeholders_and_process_language())


def test_a_public_deposit_url_is_allowed_but_a_lookalike_path_is_not(only):
    only("CONVERSION", "Archived at [the deposit](https://doi.org/10.5281/zenodo.1234567).")
    assert C._placeholders_and_process_language() == []


@pytest.mark.parametrize("target", [
    "docs/internal/review.md", "../docs/internal/review.md", "tools/paper_a_transfer_text.py",
    "puckworks/figures_paper_a.py", "tests/test_figure_exports.py",
    "figures/../docs/internal/review.md", "docs%2Finternal%2Freview.md",
])
def test_an_internal_destination_is_caught_however_it_is_written(only, target):
    only("CONVERSION", "See [analysis](%s)." % target)
    assert any("internal_path" in p for p in C._placeholders_and_process_language()), target


@pytest.mark.parametrize("raw,expected", [
    ("docs%2Finternal%2Freview.md", "docs/internal/review.md"),
    ("./docs/internal/review.md", "docs/internal/review.md"),
    ("docs\\internal\\review.md", "docs/internal/review.md"),
    ("  docs/internal/review.md  ", "docs/internal/review.md"),
])
def test_destination_normalisation(raw, expected):
    assert C._normalise_target(raw) == expected


# ── 3. scope is declared, and the exemptions are narrow ─────────────────────────────────────
def test_every_true_upload_deliverable_is_in_path_scope():
    for path in (C.CONVERSION, C.SUPPLEMENT, C.COVER_LETTER, C.HIGHLIGHTS, C.UPLOAD_CAPTIONS):
        assert path.name in C._RULE_SCOPE["internal_path"], path.name
        assert path.name in C._RULE_SCOPE["internal_narration"], path.name


def test_each_exemption_is_named_and_justified():
    """An exemption without a written reason is an exemption nobody can review."""
    assert set(C._PATH_EXEMPT_FILES) == {"PAPER_A_JFE_PACKAGE.md", "PAPER_A_DRAFT.md"}
    for name, why in C._PATH_EXEMPT_FILES.items():
        assert len(why) > 40, name
        assert name not in C._RULE_SCOPE["internal_path"], name


def test_the_broad_section_exemption_is_gone():
    """Fourteen whole sections used to be path-legal, including data availability and figure
    captions — far wider than the unsupplied-metadata placeholders it existed for."""
    assert not hasattr(C, "_PATH_ALLOWED_SECTIONS")


def test_a_path_in_an_availability_statement_is_no_longer_exempt(only):
    only("CONVERSION", "## Data and code availability\n\nSee `docs/reproducibility/notes.md`.")
    assert any("docs/reproducibility/notes.md" in p
               for p in C._placeholders_and_process_language())


def test_the_unsupplied_metadata_placeholder_is_still_allowed(only):
    """The narrow, structural exemption: a block that announces itself as not-yet-supplied may name
    the field and file the missing metadata is tracked in. It is stripped before submission.

    Round-12 P1-8C narrowed this from the whole PARAGRAPH to the placeholder sentence plus ONE exact
    tracking-reference grammar, so the approved wording has to be the approved wording.
    """
    only("CONVERSION",
         "### Funding\n\n*Not yet supplied.* State the funder and grant number. Tracked as "
         "`funding` in `docs/submission/paper_a_front_matter.yaml`; "
         "`tools/paper_a_front_matter.py --check-submission-ready` blocks submission until it is "
         "resolved.")
    assert not any("paper_a_front_matter.yaml" in p
                   for p in C._placeholders_and_process_language())


def test_the_metadata_exemption_stops_at_the_placeholder(only):
    """Round-12 P1-8C: anything else sharing the paragraph is scanned normally."""
    only("CONVERSION", "### Funding\n\n*Not yet supplied.* See `docs/internal/review.md` for the "
                       "scientific analysis.")
    assert any("docs/internal/review.md" in p for p in C._placeholders_and_process_language())


def test_the_highlights_header_no_longer_names_repository_paths():
    """Found by widening the scope: line 2 of an uploaded plain-text deliverable named two."""
    text = C.HIGHLIGHTS.read_text(encoding="utf-8")
    for leaked in ("tools/", "docs/", "puckworks/", ".py", ".yaml"):
        assert leaked not in text, "the uploaded Highlights file carries %r" % leaked
    assert "do not edit" in text.lower(), "the warning the header exists for must survive"


# ── 4. a check that cannot run must not look like a check that ran ──────────────────────────
def test_a_missing_parser_blocks_rather_than_passing(monkeypatch):
    monkeypatch.setattr(C, "_MD", None)
    problems = C._placeholders_and_process_language()
    assert problems and all("SCAN NOT RUN" in p for p in problems)
    assert C.structural_parser_unavailable
    monkeypatch.setattr(C, "_MD", None)
    assert C._visible_paragraphs("An earlier **version** was wrong.") == []


# ── 5. P2-1: caption structure ──────────────────────────────────────────────────────────────
def test_figure_4_ends_at_its_own_caption():
    captions = {n: c for n, _s, c in FC.captions()}
    assert captions["4"].endswith("they should not be pooled as equivalent validation.")
    assert "Supplementary figures" not in captions["4"]
    assert "---" not in captions["4"]


def test_the_rendered_caption_file_has_exactly_one_of_each_heading():
    rendered = FC.render()
    assert rendered.count("## Main figures") == 1
    assert rendered.count("## Supplementary figures") == 1
    assert FC.render_problems(rendered) == []


def test_the_caption_set_invariants_hold():
    found = FC.captions()
    assert FC.caption_set_problems(found) == []
    numbers = [n for n, _s, _c in found]
    assert numbers == list(FC.EXPECTED_MAIN) + list(FC.EXPECTED_SUPPLEMENTARY)
    for number, stem, caption in found:
        assert caption.startswith("**Figure %s." % number)
        assert caption.count("**Figure ") == 1
        assert stem == FC.EXPECTED_STEMS[number]


@pytest.mark.parametrize("mutation,expect", [
    ([("4", "**Figure 4. Text.** --- ## Supplementary figures")], "horizontal rule or heading"),
    ([("4", "**Figure 4. Text.** ## Supplementary figures")], "horizontal rule or heading"),
    ([("4", "Rate-profile comparison.")], "does not begin with"),
    ([("4", "**Figure 4. A.** **Figure 4. B.**")], "figure labels"),
    ([("5", "**Figure 5. Extra.**")], "main figures are"),
], ids=["rule-and-heading", "heading", "no-label", "duplicate-label", "unexpected-figure"])
def test_a_malformed_caption_set_is_rejected(mutation, expect):
    """The defect fixture: before the structural fix this exact shape was the SHIPPED file."""
    found = {n: (s, c) for n, s, c in FC.captions()}
    for number, caption in mutation:
        found[number] = (found.get(number, ("fig_unknown", ""))[0], caption)
    entries = [(n, s, c) for n, (s, c) in sorted(found.items(), key=lambda kv: FC._sort_key(kv[0]))]
    problems = FC.caption_set_problems(entries)
    assert any(expect in p for p in problems), (mutation, problems)


def test_extraction_stops_at_a_section_delimiter(tmp_path, monkeypatch):
    """The reported defect, reproduced against a fixture map rather than asserted about the fix."""
    fixture = tmp_path / "map.md"
    fixture.write_text(
        "### Figure 1 (`a`)\n\n**Figure 1. One.** Body one.\n\n"
        "### Figure 2 (`b`)\n\n**Figure 2. Two.** Body two.\n\n"
        "---\n\n## Supplementary figures\n\n"
        "### Figure S1 (`c`)\n\n**Figure S1. Ess one.** Body three.\n",
        encoding="utf-8")
    monkeypatch.setattr(FC, "INTERNAL_MAP", fixture)
    monkeypatch.setattr(FC, "EXPECTED_MAIN", ("1", "2"))
    monkeypatch.setattr(FC, "EXPECTED_SUPPLEMENTARY", ("S1",))
    monkeypatch.setattr(FC, "EXPECTED_STEMS", {"1": "a", "2": "b", "S1": "c"})
    captions = {n: c for n, _s, c in FC.captions()}
    assert captions["2"] == "**Figure 2. Two.** Body two."
    assert "Supplementary" not in captions["2"]


def test_freshness_and_validity_are_separate_gates():
    """`current == render()` proves the file was generated. It does not prove what was generated is
    a well-formed caption set, which is how the malformed Figure 4 passed for a whole round."""
    assert FC.main(["--check"]) == 0
    assert FC.render_problems("# Figure captions\n\n## Main figures\n\n"
                              "## Supplementary figures\n\n## Supplementary figures\n")


# ── 6. self-check findings, AFTER the round-11 remediation merged ────────────────────────────
#
# Probing our own gates rather than re-running the reviewer's cases found four the remediation had
# not closed. None affected the paper's text — the phrase sweep and `verify` were clean — but each
# was a live hole in a gate, which is the same class of defect the round-11 review was about.

@pytest.mark.parametrize("injected,expect", [
    # A fenced block produced NO visible text at all: only `inline` and `html_block` tokens were
    # handled, so anything inside a fence was invisible to every rule.
    ("```\nSee docs/internal/review.md for details.\n```", "docs/internal/review.md"),
    ("```text\nAn earlier version was wrong.\n```", "earlier version"),
    # Inside a raw HTML block the CommonMark parser does not interpret Markdown, so the emphasis
    # markers survived into the text a rule was matched against.
    ("<div>\nAn earlier **version** was wrong.\n</div>", "earlier version"),
    ("<section>\n<p>The second *review* asked for this.</p>\n</section>", "review"),
])
def test_selfcheck_block_level_bypasses_fail(only, injected, expect):
    only("CONVERSION", injected)
    problems = C._placeholders_and_process_language()
    assert any(expect in p for p in problems), (injected, problems[:3])


@pytest.mark.parametrize("invisible,name", [
    ("​", "zero-width space"), ("‌", "zero-width non-joiner"),
    ("‍", "zero-width joiner"), ("⁠", "word joiner"),
    ("­", "soft hyphen"), ("﻿", "BOM"),
])
def test_selfcheck_an_invisible_character_cannot_split_a_phrase(only, invisible, name):
    """None of these is visible on the page, and each defeated a rule written with plain letters."""
    only("CONVERSION", "An earlier vers%sion was wrong." % invisible)
    assert any("earlier version" in p for p in C._placeholders_and_process_language()), name


def test_selfcheck_a_comment_in_a_verbatim_upload_file_is_scanned_for_paths():
    """A comment is invisible on the page and ships in the source. The manuscript is converted to
    .docx first ("remove editorial notes" is a listed conversion edit), so its stamps never reach an
    editor; the caption file and Highlights are uploaded exactly as they stand."""
    assert set(C._UPLOADED_VERBATIM) == {"PAPER_A_JFE_HIGHLIGHTS.txt",
                                         "PAPER_A_JFE_FIGURE_CAPTIONS.md"}
    text = C.UPLOAD_CAPTIONS.read_text(encoding="utf-8")
    for leaked in ("tools/", "docs/", "puckworks/", "tests/"):
        assert leaked not in text, "the uploaded caption file carries %r" % leaked


def test_selfcheck_a_comment_path_in_the_caption_file_would_fail(only):
    only("UPLOAD_CAPTIONS", "<!-- regenerate with tools/paper_a_figure_captions.py -->")
    assert any("tools/paper_a_figure_captions.py" in p and "HTML comment" in p
               for p in C._placeholders_and_process_language())


def test_selfcheck_the_converted_files_keep_their_generator_stamps(only):
    """Scoping the comment channel to every file would have flagged eleven legitimate stamps and
    forced churn for no reader's benefit. The scope is a judgement, so it is asserted."""
    only("CONVERSION", "<!-- generated by tools/paper_a_front_matter.py -->")
    assert not any("HTML comment" in p for p in C._placeholders_and_process_language())


@pytest.mark.parametrize("identifier", [
    "tools/paper_a_transfer_text.py", "puckworks/figures_paper_a.py",
    "tests/test_figure_exports.py", "docs/submission/paper_a_front_matter.yaml",
])
def test_selfcheck_underscores_survive_emphasis_normalisation(identifier):
    """Stripping emphasis markers must not eat underscores from identifiers.

    Closing the raw-HTML-block bypass by removing `*_`~` globally turned
    `tools/paper_a_transfer_text.py` into `tools/paperatransfertext.py`, and the internal-path rule
    stopped recognising its own target — a fix for one bypass opening another. Only a run at a word
    boundary is an emphasis delimiter.
    """
    blocks = C._visible_paragraphs("The generator lives in `%s` today." % identifier)
    assert any(identifier in text for _ln, text in blocks), blocks


@pytest.mark.parametrize("text,expected", [
    ("An earlier _version_ was wrong.", "An earlier version was wrong."),
    ("An earlier *version* was wrong.", "An earlier version was wrong."),
    ("An earlier **version** was wrong.", "An earlier version was wrong."),
    ("A fig4_transfer producer stem.", "A fig4_transfer producer stem."),
])
def test_selfcheck_emphasis_normalisation_is_exact(text, expected):
    assert C._normalise_visible(text) == expected

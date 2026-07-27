"""One title, one abstract, one keyword list, one set of Highlights — everywhere.

Third review P0-1. The JFE manuscript and the JFE package described different papers:

| item          | manuscript                          | package                                  |
|---------------|-------------------------------------|------------------------------------------|
| title         | Separating Extractable Content...   | Whole-cup measurements can obscure...    |
| abstract      | ~313 words                          | a different, stale 237-word abstract     |
| keywords      | 6                                   | 7                                        |
| Highlights    | 5 repository-facing bullets         | an older set                             |
| status        | analyses complete                   | "final weighted-uncertainty reruns" owed |

The review's instruction was to generate every rendering from one machine-readable source rather
than repair the copies by hand. These tests are the "add a test requiring exact title and abstract
equality across all generated files" half of that instruction.
"""
import pathlib
import re
import subprocess
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from tools import paper_a_front_matter as FM  # noqa: E402

RETIRED_TITLE = "Whole-cup measurements can obscure kinetic parameter localization"


@pytest.fixture(scope="module")
def fm():
    return FM.load()


def test_every_generated_rendering_is_current(fm):
    """The single check that makes the rest of this file non-vacuous: if any rendering drifts from
    the YAML source, this fails and names the file and block."""
    assert FM.check(fm) == []


def test_the_cli_reports_drift_and_exits_nonzero():
    r = subprocess.run([sys.executable, str(_ROOT / "tools" / "paper_a_front_matter.py")],
                       capture_output=True, text=True, cwd=_ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "0 drifted rendering(s)" in r.stdout


# ── the equality the review asked for, checked on the rendered files ──────────────────────────
_TEXT_TARGETS = (
    _ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md",
    _ROOT / "docs" / "submission" / "PAPER_A_JFE_PACKAGE.md",
    _ROOT / "docs" / "PAPER_A_DRAFT.md",
    _ROOT / "docs" / "submission" / "PAPER_A_JFE_COVER_LETTER.md",
)


@pytest.mark.parametrize("path", _TEXT_TARGETS, ids=lambda p: p.name)
def test_one_title_appears_everywhere(path, fm):
    text = path.read_text(encoding="utf-8")
    assert FM._one_line(fm["title"]) in " ".join(text.split()), f"current title absent from {path.name}"
    assert RETIRED_TITLE not in text, f"retired title survives in {path.name}"


def test_the_abstract_is_identical_in_manuscript_and_package(fm):
    man = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md").read_text(encoding="utf-8")
    pkg = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_PACKAGE.md").read_text(encoding="utf-8")
    a_man = FM.block(man, "abstract")
    a_pkg = FM.block(pkg, "abstract").split("\n\n", 1)[1]     # drop the word-count line
    assert a_man == a_pkg == FM._one_line(fm["abstract"])


def test_the_abstract_is_within_the_venue_word_limit(fm):
    n = FM.word_count(fm["abstract"])
    limit = fm["venue"]["abstract_word_limit"]
    assert n <= limit, f"{n} words exceeds the {limit}-word limit"
    # The review asked for 230-240 so that a different word counter in Word or LaTeX cannot push
    # the submitted file over the limit.
    assert 225 <= n <= 240, f"{n} words is outside the 225-240 safety band"


def test_the_keyword_list_is_identical_everywhere_and_within_count(fm):
    kws = fm["keywords"]
    assert len(kws) <= fm["venue"]["keyword_limit"], f"{len(kws)} keywords"
    man = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md").read_text(encoding="utf-8")
    pkg = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_PACKAGE.md").read_text(encoding="utf-8")
    from_man = FM.block(man, "keywords").removeprefix("**Keywords:**").strip()
    from_pkg = FM.block(pkg, "keywords").split("\n\n")[0].strip()
    assert from_man == from_pkg == "; ".join(kws)
    # `profile objective` was repository vocabulary; `porous media`/`model transfer` were
    # package-only. Neither may return.
    for retired in ("profile objective", "porous media", "model transfer", "extraction kinetics"):
        assert retired not in from_man, f"retired keyword `{retired}` is back"


def test_highlights_meet_the_venue_format(fm):
    hi = fm["highlights"]
    lo, high = fm["venue"]["highlight_count"]
    assert lo <= len(hi) <= high, f"{len(hi)} Highlights"
    for h in hi:
        assert len(h) <= fm["venue"]["highlight_char_limit"], f"{len(h)} chars: {h}"
        assert not re.search(r"\b(MAPE|LOCO|OOB|SSE|TDS|CI)\b", h), f"unexplained acronym: {h}"


def test_highlights_are_scientific_findings_not_repository_facts(fm):
    """`All headline values are tied to machine-readable result bundles` is a fact about the
    repository, not a result. Elsevier asks that Highlights be accessible to a general audience."""
    joined = " ".join(fm["highlights"]).lower()
    for banned in ("machine-readable", "result bundle", "repository", "compensation profile",
                   "localize", "benchmark skill"):
        assert banned not in joined, f"repository vocabulary in Highlights: {banned}"


def test_the_highlights_file_is_generated_from_the_same_source(fm):
    text = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_HIGHLIGHTS.txt").read_text(encoding="utf-8")
    assert "do not edit by hand" in text.lower()
    bullets = [ln[2:] for ln in text.splitlines() if ln.startswith("• ")]
    assert bullets == fm["highlights"]


def test_the_package_no_longer_states_completed_analyses_as_outstanding():
    """The package said "final weighted-uncertainty reruns ... remain PI actions" while all six
    objective panels and the bounded refit bootstrap were complete."""
    pkg = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_PACKAGE.md").read_text(encoding="utf-8")
    assert "final weighted-uncertainty reruns, and a clean typeset source remain PI actions" not in pkg
    assert "are **complete**" in " ".join(pkg.split())


def test_unresolved_submission_metadata_is_enumerated_not_scattered(fm):
    """P0-7. The placeholders must be represented once, as explicit nulls, so one check can list
    what still blocks submission."""
    gaps = FM.submission_gaps(fm)
    assert "authors" in gaps and "release_doi" in gaps, (
        "if these are now supplied, update this test and the manuscript's declarations")
    r = subprocess.run([sys.executable, str(_ROOT / "tools" / "paper_a_front_matter.py"),
                        "--check-submission-ready"], capture_output=True, text=True, cwd=_ROOT)
    assert r.returncode == 1, "submission-readiness check must fail while metadata is missing"
    assert "UNRESOLVED: authors" in r.stdout


def test_the_novelty_sentence_stays_hedged_until_the_search_is_archived(fm):
    """The package called the indexed novelty search a PI action while the manuscript said "To our
    knowledge, following the documented search", which reads as final."""
    if fm["novelty_search"]["status"] == "complete":
        pytest.skip("novelty search archived — the hedge may now be removed")
    man = (_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md").read_text(encoding="utf-8")
    assert "following the documented search" not in man, (
        "novelty claim reads as final while novelty_search.status is incomplete")

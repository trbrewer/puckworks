"""Tests for the Paper A cross-reference / scaffolding linter (Paper 1 second review MC8+MC9).

Offline and deterministic. The point of these tests is that the linter is NOT vacuous: an existence
check would pass on the exact bug MC9 describes, because a stale `§4` in the venue conversion still
names a real section. Each fault below is injected into a COPY of the manuscripts and must fail.
"""
import importlib
import shutil
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
X = importlib.import_module("tools.paper_a_xref")


def _sandbox(tmp_path, extra_draft=""):
    """Copy both manuscripts, optionally append text to the draft, and point the linter at them."""
    d, c = tmp_path / "draft.md", tmp_path / "conv.md"
    shutil.copy(X.DRAFT, d)
    shutil.copy(X.CONVERSION, c)
    if extra_draft:
        d.write_text(d.read_text(encoding="utf-8") + extra_draft, encoding="utf-8")
    return d, c


@pytest.fixture
def relinked(monkeypatch):
    def _apply(d, c):
        monkeypatch.setattr(X, "DRAFT", d)
        monkeypatch.setattr(X, "CONVERSION", c)
        monkeypatch.setattr(X, "FILES", (d, c))
    return _apply


def test_current_tree_is_clean():
    assert X.check() == []


def test_both_files_expose_every_labelled_section():
    """A label with no matching heading means the alias table has drifted from the manuscripts,
    which would silently disable the checks that use it."""
    for path in X.FILES:
        found = X._headings(path.read_text(encoding="utf-8"))
        missing = set(X.SECTION_ALIASES) - set(found)
        assert not missing, f"{path.name} has no heading for {sorted(missing)}"


def test_the_two_files_now_share_one_section_architecture():
    """This test previously asserted the OPPOSITE -- that the two files numbered the same sections
    differently, which was the premise of MC9. The section-7 restructure converged them, so the
    root cause is gone and the assertion is inverted rather than deleted: if the structures ever
    diverge again, the stale-reference class returns and this fails.

    The inline labels remain useful even so, because they also catch a renumbering INSIDE one
    file."""
    a = X._headings(X.DRAFT.read_text(encoding="utf-8"))
    b = X._headings(X.CONVERSION.read_text(encoding="utf-8"))
    assert a == b, "the manuscripts have diverged structurally: %s vs %s" % (a, b)


def test_the_shared_architecture_is_the_one_the_review_specified():
    """Guards the restructure itself: results are stated as findings, in the reviewed order."""
    h = X._headings(X.CONVERSION.read_text(encoding="utf-8"))
    assert h["methods"] == "2"
    assert h["wholecup"] == "3"
    assert h["result3"] == "4"
    assert h["temporal"] == "5"
    assert h["discussion"] == "6"
    assert h["limitations"] == "7"


def test_a_stale_number_is_caught_even_though_the_section_exists(tmp_path, relinked):
    """THE MC9 bug: §6 exists in the draft (Limitations), so an existence check passes; but the
    reference means Result 2, which is §4."""
    d, c = _sandbox(tmp_path, "\n\nThe profile analysis (§6<!--sec:result2-->) shows this.\n")
    relinked(d, c)
    probs = X.check()
    assert any("printed number is wrong" in p for p in probs), probs


def test_a_bare_reference_is_caught(tmp_path, relinked):
    d, c = _sandbox(tmp_path, "\n\nAs shown in §5, the null benchmark matters.\n")
    relinked(d, c)
    probs = X.check()
    assert any("bare cross-reference" in p for p in probs), probs


def test_roadmap_references_are_not_policed(tmp_path, relinked):
    """The ROADMAP change log is a different document; its numbering is not ours to check."""
    d, c = _sandbox(tmp_path, "\n\nSee the ROADMAP §7.1 change log.\n")
    relinked(d, c)
    assert not [p for p in X.check() if "bare cross-reference" in p]


@pytest.mark.parametrize("snippet,needle", [
    ("\n\nThis was flagged in review A3-01.\n", "review ID"),
    ("\n\nThe interval is *delivered* in the supplement.\n", "delivered"),
    ("\n\nA measured flow trace is still owed.\n", "owed"),
    ("\n\nThat comparison is deferred.\n", "deferred"),
    ("\n\nUnlike our earlier draft, the residual is small.\n", "earlier draft"),
    ("\n\nThe handoff notes explain the rest.\n", "handoff"),
])
def test_repository_scaffolding_is_caught(tmp_path, relinked, snippet, needle):
    d, c = _sandbox(tmp_path, snippet)
    relinked(d, c)
    probs = X.check()
    assert any(needle in p for p in probs), (needle, probs)


def test_the_working_draft_repository_note_is_exempt():
    """The canonical draft carries an explicitly-marked, strip-before-submission repository note.
    It is scaffolding by design; the venue conversion does not carry it. The exemption must be
    scoped to that block only -- verify it exists and that it does contain a banned word, so the
    exemption is doing real work rather than covering an empty range."""
    text = X.DRAFT.read_text(encoding="utf-8")
    spans = X._exempt_spans(text)
    assert len(spans) == 1
    a, b = spans[0]
    block = text[a:b]
    assert "owed" in block, "the exemption no longer covers any banned text -- re-check its bounds"
    assert b - a < len(text) // 4, "the exemption span is implausibly large"

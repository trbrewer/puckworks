"""Wave-3 guard: `docs/ROADMAP.md` §7.1 scientific history is APPEND-ONLY.

This replaces a guard written earlier in this same branch that asserted `docs/ROADMAP.md` was
byte-unchanged. That assertion was wrong and could not ship: CLAUDE.md **requires** a §7.1
changelog entry for work like this, so "byte-unchanged" asserted something the repository's own
contract forbids. Deleting the test was not an option either — the property it was reaching for is
real, and it is the property that keeps a screen from quietly editing scientific history while
appending to it.

What is actually protected, checked against the frozen scientific base 85f65c0:

  1. every pre-existing §7.1 changelog row is still present, byte-identical, and in its original
     relative order;
  2. base-to-head changes to ROADMAP are confined to the §7.1 changelog region;
  3. only the expected new Wave-3 row was added;
  4. the new row names I-072 and I-090 and records both as RETIRE;
  5. no pre-existing scientific statement outside §7.1 was altered.

None of these depends on the current HEAD SHA, on a raw line count, or on any value that goes
stale merely because legitimate history is appended. BASE is the branch's immutable scientific
base, not a moving head, and the assertions are stated over row CONTENT rather than row position.
"""
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
ROADMAP = "docs/ROADMAP.md"

#: The frozen scientific base this branch is bound to. Immutable by authorization: the Wave-3
#: screens are bound to it, so it is a fixed boundary and not a "current HEAD" that drifts.
BASE = "85f65c0d4b836990152fa4e9bf91c6d292a9e257"

#: The one row this branch is allowed to add, identified by its date cell and its subject.
EXPECTED_NEW_ROW_DATE = "2026-08-07"
EXPECTED_NEW_ROW_MARKER = "Insight Foundry Wave-3 cheap screens"


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _have_base():
    return _git("cat-file", "-e", BASE + "^{commit}").returncode == 0


def _roadmap_at(ref=None):
    if ref is None:
        return (REPO / ROADMAP).read_text(encoding="utf-8")
    return _git("show", "%s:%s" % (ref, ROADMAP)).stdout


def _changelog_rows(text):
    """The §7.1 changelog rows, as a list of raw table lines.

    A row is a table line whose first cell is a date. That is a content test, not a position
    test: rows keep their identity when new ones are prepended above them.
    """
    rows, in_table = [], False
    for line in text.splitlines():
        if line.startswith("| date | change |"):
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                in_table = False
                continue
            first = line.split("|")[1].strip()
            if first.startswith("---") or not first:
                continue
            if first[:4].isdigit() and first.count("-") >= 2:
                rows.append(line)
    return rows


def _changelog_region_bounds(text):
    """(start, end) character offsets of the §7.1 changelog table."""
    start = text.index("| date | change |")
    tail = text[start:]
    lines, off = tail.splitlines(keepends=True), 0
    for i, line in enumerate(lines):
        if i > 1 and not line.startswith("|"):
            break
        off += len(line)
    return start, start + off


pytestmark = pytest.mark.skipif(not _have_base(), reason="scientific base not in this checkout")


# --------------------------------------------------------------------------------------------
# 1. EVERY PRE-EXISTING ROW SURVIVES, BYTE-IDENTICAL, IN ORDER
# --------------------------------------------------------------------------------------------
def test_every_preexisting_changelog_row_survives_byte_identical():
    before = _changelog_rows(_roadmap_at(BASE))
    after = _changelog_rows(_roadmap_at())
    assert before, "no changelog rows parsed at base — the parser, not the history, is wrong"
    missing = [r for r in before if r not in after]
    assert missing == [], (
        "%d pre-existing §7.1 row(s) were edited or removed; scientific history is append-only:\n%s"
        % (len(missing), "\n".join(r[:160] for r in missing[:3])))


def test_preexisting_rows_keep_their_relative_order():
    """Subsequence test: new rows may be interleaved, existing ones may not be reordered."""
    before = _changelog_rows(_roadmap_at(BASE))
    after = _changelog_rows(_roadmap_at())
    it = iter(after)
    assert all(row in it for row in before), (
        "pre-existing §7.1 rows changed relative order")


# --------------------------------------------------------------------------------------------
# 2-3. ONLY THE EXPECTED NEW ROW WAS ADDED
# --------------------------------------------------------------------------------------------
def test_exactly_the_expected_wave3_row_was_added():
    before = _changelog_rows(_roadmap_at(BASE))
    after = _changelog_rows(_roadmap_at())
    added = [r for r in after if r not in before]
    assert len(added) == 1, (
        "expected exactly one new §7.1 row, found %d:\n%s"
        % (len(added), "\n".join(r[:160] for r in added)))
    row = added[0]
    assert row.split("|")[1].strip() == EXPECTED_NEW_ROW_DATE
    assert EXPECTED_NEW_ROW_MARKER in row


def test_the_new_row_names_both_candidates_and_records_both_as_retire():
    before = _changelog_rows(_roadmap_at(BASE))
    row = [r for r in _changelog_rows(_roadmap_at()) if r not in before][0]
    for cid in ("I-072", "I-090"):
        assert cid in row, "the Wave-3 entry does not name %s" % cid
    assert "I-072 RETIRE" in row and "I-090 RETIRE" in row, (
        "the Wave-3 entry must record BOTH dispositions as RETIRE in terms")


# --------------------------------------------------------------------------------------------
# 5. NOTHING OUTSIDE THE CHANGELOG REGION CHANGED
# --------------------------------------------------------------------------------------------
def test_roadmap_changes_are_confined_to_the_changelog_region():
    base_text, head_text = _roadmap_at(BASE), _roadmap_at()
    b0, b1 = _changelog_region_bounds(base_text)
    h0, h1 = _changelog_region_bounds(head_text)
    assert base_text[:b0] == head_text[:h0], (
        "ROADMAP text BEFORE the §7.1 changelog changed — a screen may not edit a live "
        "scientific statement")
    assert base_text[b1:] == head_text[h1:], (
        "ROADMAP text AFTER the §7.1 changelog changed — a screen may not edit a live "
        "scientific statement")


# --------------------------------------------------------------------------------------------
# REGRESSION: the guard must actually catch a rewrite, not merely pass
# --------------------------------------------------------------------------------------------
def test_the_guard_detects_an_edited_historical_row():
    """A guard that has never been shown to fail is not evidence of anything."""
    base_text = _roadmap_at(BASE)
    rows = _changelog_rows(base_text)
    tampered = base_text.replace(rows[-1], rows[-1].replace("RETIRE", "SURVIVE", 1), 1) \
        if "RETIRE" in rows[-1] else base_text.replace(rows[-1], rows[-1] + " EDITED", 1)
    assert tampered != base_text
    surviving = [r for r in _changelog_rows(base_text) if r in _changelog_rows(tampered)]
    assert len(surviving) < len(rows), "the parser cannot see a row edit; the guard is vacuous"


def test_the_guard_detects_a_change_outside_the_changelog():
    head_text = _roadmap_at()
    h0, _ = _changelog_region_bounds(head_text)
    tampered = head_text[:h0].replace("\n", "\nX", 1) + head_text[h0:]
    b0, _ = _changelog_region_bounds(tampered)
    assert tampered[:b0] != head_text[:h0], (
        "a prose edit above the changelog is invisible to the region check")

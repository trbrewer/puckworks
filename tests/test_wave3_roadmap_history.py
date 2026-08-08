"""Wave-3 guard: `docs/ROADMAP.md` §7.1 scientific history is APPEND-ONLY.

Two layers, with two different jobs. Conflating them is what went wrong twice in this branch's
history, so they are kept explicitly apart:

  A. **Immutable historical change-range** — `BASE .. WAVE3_HISTORY_HEAD`. This proves what the
     Wave-3 change ITSELF did: exactly one row added, that row is the 2026-08-07 Wave-3 entry
     naming I-072 and I-090 as RETIRE, every pre-existing row byte-identical and in order, and
     nothing outside the §7.1 region touched. Both endpoints are frozen commits, so these
     assertions can never go stale.

  B. **Live historical persistence** — `WAVE3_HISTORY_HEAD` vs the working tree. This proves only
     that history has not been rewritten SINCE: every row present at `WAVE3_HISTORY_HEAD` is still
     present byte-identically and in order, and the Wave-3 row still appears exactly once and still
     records both dispositions.

**The live layer deliberately permits later legitimate history.** Any number of later §7.1 rows,
later dates, and later authorized ROADMAP changes outside the frozen Wave-3 change range are fine.
This guard is candidate-local; it does not freeze the rest of `docs/ROADMAP.md` forever, and it
does not assert that the total number of rows added since `BASE` remains one.

That last point is the defect this file was rewritten to fix. The previous version compared `BASE`
with the LIVE working tree and required `len(added) == 1`, which passed only until the next
legitimate §7.1 entry was appended — a moving-endpoint assertion of exactly the kind this branch
corrected elsewhere. A regression test below appends a synthetic future row and requires it to be
accepted.
"""
import pathlib
import subprocess

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
ROADMAP = "docs/ROADMAP.md"

#: The frozen scientific base this branch is bound to.
BASE = "85f65c0d4b836990152fa4e9bf91c6d292a9e257"

#: The LAST commit on this branch that changed the Wave-3 §7.1 row itself. Later commits
#: (`d5d7b02` tests, `8ca8fa8` figure caption) do not touch `docs/ROADMAP.md`. Selected from
#: `git log 85f65c0..HEAD -- docs/ROADMAP.md`, not guessed.
WAVE3_HISTORY_HEAD = "e71ac2b2b848dd7a22a826f96c8807718027eb2f"

EXPECTED_NEW_ROW_DATE = "2026-08-07"
EXPECTED_NEW_ROW_MARKER = "Insight Foundry Wave-3 cheap screens"


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _have(ref):
    return _git("cat-file", "-e", ref + "^{commit}").returncode == 0


def roadmap_at(ref=None):
    """ROADMAP text at a commit, or the live working tree when `ref` is None."""
    if ref is None:
        return (REPO / ROADMAP).read_text(encoding="utf-8")
    return _git("show", "%s:%s" % (ref, ROADMAP)).stdout


def changelog_rows(text):
    """The §7.1 changelog rows, as raw table lines.

    A row is a table line whose first cell is a date — a CONTENT test, not a position test, so
    rows keep their identity when new ones are prepended above them.
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


def changelog_region_bounds(text):
    """(start, end) character offsets of the §7.1 changelog table."""
    start = text.index("| date | change |")
    tail = text[start:]
    off = 0
    for i, line in enumerate(tail.splitlines(keepends=True)):
        if i > 1 and not line.startswith("|"):
            break
        off += len(line)
    return start, start + off


# --------------------------------------------------------------------------------------------
# The two assertion helpers. Tests and regressions exercise THESE, not a parallel approximation.
# --------------------------------------------------------------------------------------------

def rows_persist(reference_rows, candidate_text):
    """Problems preventing `candidate_text` from preserving `reference_rows` append-only.

    Empty list == every reference row is present byte-identically AND in its original relative
    order. Extra rows in the candidate are explicitly allowed: that is what append-only means.
    """
    after = changelog_rows(candidate_text)
    problems = []
    missing = [r for r in reference_rows if r not in after]
    if missing:
        problems.append("%d historical row(s) edited or removed: %s"
                        % (len(missing), "; ".join(r[:90] for r in missing[:3])))
    it = iter(after)
    if not all(row in it for row in reference_rows):
        problems.append("historical rows changed relative order")
    return problems


def changes_confined_to_changelog(before_text, after_text):
    """Problems showing a change landed OUTSIDE the §7.1 changelog region."""
    b0, b1 = changelog_region_bounds(before_text)
    a0, a1 = changelog_region_bounds(after_text)
    problems = []
    if before_text[:b0] != after_text[:a0]:
        problems.append("text BEFORE the §7.1 changelog changed")
    if before_text[b1:] != after_text[a1:]:
        problems.append("text AFTER the §7.1 changelog changed")
    return problems


def wave3_rows(rows):
    """Every row that looks like the Wave-3 entry (should be exactly one)."""
    return [r for r in rows
            if r.split("|")[1].strip() == EXPECTED_NEW_ROW_DATE and EXPECTED_NEW_ROW_MARKER in r]


pytestmark = pytest.mark.skipif(
    not (_have(BASE) and _have(WAVE3_HISTORY_HEAD)),
    reason="frozen scientific range not present in this checkout")


# --------------------------------------------------------------------------------------------
# LAYER A — the immutable change range BASE .. WAVE3_HISTORY_HEAD
# --------------------------------------------------------------------------------------------
def test_wave3_range_preserved_every_preexisting_row():
    base_rows = changelog_rows(roadmap_at(BASE))
    assert base_rows, "no rows parsed at BASE — the parser, not the history, is wrong"
    assert rows_persist(base_rows, roadmap_at(WAVE3_HISTORY_HEAD)) == []


def test_wave3_range_added_exactly_one_row():
    before = changelog_rows(roadmap_at(BASE))
    after = changelog_rows(roadmap_at(WAVE3_HISTORY_HEAD))
    added = [r for r in after if r not in before]
    assert len(added) == 1, (
        "the Wave-3 change added %d rows, expected 1:\n%s"
        % (len(added), "\n".join(r[:120] for r in added)))
    assert added[0].split("|")[1].strip() == EXPECTED_NEW_ROW_DATE
    assert EXPECTED_NEW_ROW_MARKER in added[0]


def test_wave3_range_row_names_both_candidates_as_retire():
    row = wave3_rows(changelog_rows(roadmap_at(WAVE3_HISTORY_HEAD)))[0]
    for cid in ("I-072", "I-090"):
        assert cid in row, "the Wave-3 entry does not name %s" % cid
    assert "I-072 RETIRE" in row and "I-090 RETIRE" in row


def test_wave3_range_changes_confined_to_the_changelog_region():
    assert changes_confined_to_changelog(
        roadmap_at(BASE), roadmap_at(WAVE3_HISTORY_HEAD)) == []


# --------------------------------------------------------------------------------------------
# LAYER B — live persistence. Later legitimate history is ALLOWED.
# --------------------------------------------------------------------------------------------
def test_live_preserves_every_row_present_at_wave3_history_head():
    reference = changelog_rows(roadmap_at(WAVE3_HISTORY_HEAD))
    assert rows_persist(reference, roadmap_at()) == []


def test_live_still_carries_the_wave3_row_exactly_once():
    hits = wave3_rows(changelog_rows(roadmap_at()))
    assert len(hits) == 1, "expected exactly one Wave-3 row live, found %d" % len(hits)
    assert "I-072 RETIRE" in hits[0] and "I-090 RETIRE" in hits[0]


def test_live_layer_does_not_bound_how_much_history_was_added_since_base():
    """Explicit: the live layer must not re-impose the moving-endpoint assertion this file was
    rewritten to remove. Appending future rows is legitimate and must stay legitimate."""
    base_rows = changelog_rows(roadmap_at(BASE))
    live_rows = changelog_rows(roadmap_at())
    added_since_base = [r for r in live_rows if r not in base_rows]
    assert len(added_since_base) >= 1
    # no assertion pins this number: growth here is expected, not a defect.


# --------------------------------------------------------------------------------------------
# REGRESSIONS — the guard must accept legitimate growth and reject rewriting
# --------------------------------------------------------------------------------------------
def _live_text_and_reference():
    return roadmap_at(), changelog_rows(roadmap_at(WAVE3_HISTORY_HEAD))


def _insert_rows(text, new_rows):
    """Insert synthetic rows immediately above the newest existing row (newest-first table)."""
    anchor = changelog_rows(text)[0]
    i = text.index(anchor)
    return text[:i] + "".join(r + "\n" for r in new_rows) + text[i:]


FUTURE_ROW = "| 2026-09-01 | **A future authorized entry.** | evidence | items |"
FUTURE_ROW_2 = "| 2026-10-15 | **Another future authorized entry.** | evidence | items |"


def test_regression_one_future_row_is_accepted():
    """THE case the previous guard falsely rejected."""
    live, reference = _live_text_and_reference()
    tampered = _insert_rows(live, [FUTURE_ROW])
    assert rows_persist(reference, tampered) == []
    assert len(wave3_rows(changelog_rows(tampered))) == 1


def test_regression_multiple_future_rows_are_accepted():
    live, reference = _live_text_and_reference()
    tampered = _insert_rows(live, [FUTURE_ROW, FUTURE_ROW_2])
    assert rows_persist(reference, tampered) == []


def test_regression_editing_the_wave3_row_is_rejected():
    live, reference = _live_text_and_reference()
    row = wave3_rows(changelog_rows(live))[0]
    tampered = live.replace(row, row.replace("I-090 RETIRE", "I-090 SURVIVE", 1), 1)
    assert tampered != live
    assert rows_persist(reference, tampered) != []


def test_regression_removing_the_wave3_row_is_rejected():
    live, reference = _live_text_and_reference()
    row = wave3_rows(changelog_rows(live))[0]
    tampered = live.replace(row + "\n", "", 1)
    assert tampered != live
    assert rows_persist(reference, tampered) != []
    assert wave3_rows(changelog_rows(tampered)) == []


def test_regression_editing_a_pre_wave3_row_is_rejected():
    live, reference = _live_text_and_reference()
    base_rows = changelog_rows(roadmap_at(BASE))
    old = base_rows[0]
    tampered = live.replace(old, old.rstrip("|") + " EDITED |", 1)
    assert tampered != live
    assert rows_persist(reference, tampered) != []


def test_regression_reordering_historical_rows_is_rejected():
    live, reference = _live_text_and_reference()
    rows = changelog_rows(live)
    a, b = rows[1], rows[2]
    tampered = live.replace(a + "\n" + b, b + "\n" + a, 1)
    assert tampered != live, "the two rows are not adjacent; pick a different pair"
    problems = rows_persist(reference, tampered)
    assert any("relative order" in p for p in problems), problems


def test_regression_prose_outside_the_changelog_is_rejected_in_the_fixed_range():
    """Layer A's region check must catch an edit outside §7.1 within BASE..WAVE3_HISTORY_HEAD."""
    base_text = roadmap_at(BASE)
    b0, _ = changelog_region_bounds(base_text)
    tampered = base_text[:b0].replace("\n", "\nTAMPERED\n", 1) + base_text[b0:]
    assert tampered != base_text
    problems = changes_confined_to_changelog(base_text, tampered)
    assert any("BEFORE" in p for p in problems), problems

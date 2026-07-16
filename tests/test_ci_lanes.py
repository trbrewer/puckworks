"""WP5 — guard the CI-lane split: the declared SLOW list must stay accurate (no stale
entries), and the quick lane must actually exclude the slow tests. Prevents a heavy test from
silently rejoining quick-pr, or a renamed test leaving a dead entry in the slow list.
"""
from pathlib import Path

import conftest

_TDIR = Path(__file__).parent


def test_slow_list_has_no_stale_entries():
    for entry in conftest.SLOW:
        fname, tname = entry.split("::")
        text = (_TDIR / fname).read_text(encoding="utf-8")
        assert ("def %s(" % tname) in text, "stale slow-list entry (no such test): %s" % entry


def test_slow_list_is_nonempty_and_covers_the_heaviest():
    # the ~35 s quick-gates aggregate is the single heaviest test — it MUST be slow-marked so
    # quick-pr stays fast (the whole point of the split).
    assert conftest.SLOW
    assert "test_gates.py::test_quick_gates" in conftest.SLOW

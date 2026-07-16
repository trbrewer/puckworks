"""WP5 — guard the CI-lane split: the declared SLOW list must stay accurate (no stale
entries), and the quick lane must actually exclude the slow tests. Prevents a heavy test from
silently rejoining quick-pr, or a renamed test leaving a dead entry in the slow list.
"""
import re
import socket
import subprocess
import sys
from pathlib import Path

import pytest

import conftest

_TDIR = Path(__file__).parent
_ROOT = _TDIR.parent


def _collect_count(marker_expr):
    """Number of tests pytest selects for a marker expression (collect-only, no execution)."""
    args = [sys.executable, "-m", "pytest", "--co", "-q", "-p", "no:cacheprovider", "tests/"]
    if marker_expr:
        args += ["-m", marker_expr]
    out = subprocess.run(args, capture_output=True, text=True, cwd=_ROOT).stdout
    m = re.search(r"(\d+)/\d+ tests collected", out) or re.search(r"(\d+) tests collected", out)
    assert m, "could not parse collection count from:\n%s" % out[-500:]
    return int(m.group(1))


def test_offline_lane_blocks_network():
    with pytest.raises(RuntimeError, match="network access blocked"):
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("example.com", 80))


def test_lanes_partition_every_test():
    # every test is in exactly one primary lane: quick == (no slow/live/gpu/external),
    # complement == (slow or live or gpu or external). They must sum to the full suite.
    total = _collect_count("")
    quick = _collect_count("not slow and not live and not gpu and not external_data")
    other = _collect_count("slow or live or gpu or external_data")
    assert quick + other == total, "lanes do not partition: %d + %d != %d" % (quick, other, total)
    assert quick > 0 and other > 0


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

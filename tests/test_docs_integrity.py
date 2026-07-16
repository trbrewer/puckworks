"""R3 — the curated navigation docs must not rot: every internal link in docs/CURRENT.md and
docs/CI_LANES.md must resolve to a real path. (Historical docs under docs/archive/ are exempt.)
"""
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CHECKED = ["docs/CURRENT.md", "docs/CI_LANES.md", "docs/archive/README.md"]
_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_navigation_doc_links_resolve():
    problems = []
    for rel in _CHECKED:
        doc = _ROOT / rel
        for target in _LINK.findall(doc.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            path = target.split("#")[0]
            if not path:
                continue
            if not (doc.parent / path).resolve().exists():
                problems.append("%s -> %s" % (rel, target))
    assert not problems, "broken internal links:\n" + "\n".join(problems)


def test_current_index_exists_and_lists_state_of_truth():
    current = (_ROOT / "docs/CURRENT.md").read_text(encoding="utf-8")
    assert "STATE_OF_TRUTH.md" in current            # the canonical status must be indexed
    assert "no bare" in current.lower()              # the state-vocabulary rule is stated

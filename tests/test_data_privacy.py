"""R8 — private/raw corpus data must NEVER be git-tracked or enter a release/paper bundle
(guardrail: "no private Visualizer data in archives"). The raw shot store (shards, bronze,
crawl dirs) is gitignored; only PII-stripped derived summaries + provenance are tracked.
"""
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]


def _git_tracked():
    try:
        out = subprocess.run(["git", "ls-files"], cwd=_ROOT, capture_output=True, text=True,
                             check=True).stdout
    except Exception:
        pytest.skip("not a git checkout")
    return out.splitlines()


def test_no_raw_corpus_shot_data_is_tracked():
    tracked = _git_tracked()
    bad = [f for f in tracked
           if (Path(f).name.startswith(("shard_", "bronze_")) and f.endswith(".jsonl.gz"))
           or "crawl_v" in f
           or f.endswith("_index.csv") and "visualizer" in f]
    assert not bad, "raw/private corpus shot data is git-tracked: %r" % bad[:10]


def test_paper3_bundle_excludes_raw_corpus():
    from puckworks.paper3 import build
    for f in build.bundle_contents():
        assert not f.endswith(".jsonl.gz"), "raw corpus jsonl in paper3 bundle: %s" % f
        assert "crawl_" not in f, "crawl data in paper3 bundle: %s" % f

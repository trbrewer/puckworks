"""Deterministic source-scope contract for the research-impact report (issue #46, Phase 0).

Offline. The canonical report must be reproducible from a commit and must never silently incorporate a
maintainer's untracked local cards/intake. `committed` scope (the default, used by CI and the standing
issue) examines only git-tracked files and records what it excluded; `working_tree` scope includes
untracked files for local authoring. These tests build a throwaway git repo with tracked and untracked
files so the behaviour is verified directly, not against the live checkout.
"""
import subprocess
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(_ROOT / "tools"))

pytest.importorskip("yaml", reason="pyyaml is a radar/dev extra")


def _run(*args, cwd):
    subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True)


def _make_repo(tmp_path: Path) -> tuple:
    """A tiny git repo with a tracked card + intake and an UNTRACKED card + intake."""
    import research_impact as RI
    repo = tmp_path / "repo"
    (repo / "docs" / "cards").mkdir(parents=True)
    (repo / "docs" / "research" / "intake").mkdir(parents=True)
    # copy the real schema so intake validation is meaningful
    (repo / "docs" / "research" / "intake" / "schema.json").write_text(
        RI.SCHEMA_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    tracked_card = repo / "docs" / "cards" / "tracked_paper.md"
    tracked_card.write_text("# Tracked\n\n**Status:** card-only\n\nDOI 10.1000/tracked\n", encoding="utf-8")
    _run("git", "init", "-q", cwd=repo)
    _run("git", "add", "docs/cards/tracked_paper.md", "docs/research/intake/schema.json", cwd=repo)
    _run("git", "-c", "user.email=t@e", "-c", "user.name=t", "commit", "-qm", "init", cwd=repo)
    # an UNTRACKED card that must NOT enter the committed report
    (repo / "docs" / "cards" / "untracked_paper.md").write_text(
        "# Untracked\n\n**Status:** card-only\n\nDOI 10.1000/untracked\n", encoding="utf-8")
    return repo, tracked_card


def _report(repo: Path, scope: str):
    import research_impact as RI
    return RI.build_report(
        intake_dir=repo / "docs" / "research" / "intake",
        cards_dir=repo / "docs" / "cards",
        components=[], source_scope=scope, repo_root=repo)


def test_committed_scope_excludes_untracked_and_records_them(tmp_path):
    repo, _ = _make_repo(tmp_path)
    r = _report(repo, "committed")
    ss = r["source_scope"]
    assert ss["scope"] == "committed"
    assert ss["tracked_card_count"] == 1
    assert ss["untracked_card_count"] == 1
    assert ss["excluded_untracked_paths"] == ["docs/cards/untracked_paper.md"]
    # the untracked card produced no finding (it was not read at all)
    subjects = {f["subject"] for f in r["findings"]}
    assert "untracked_paper" not in subjects
    assert "tracked_paper" in subjects


def test_working_tree_scope_includes_untracked(tmp_path):
    repo, _ = _make_repo(tmp_path)
    r = _report(repo, "working_tree")
    ss = r["source_scope"]
    assert ss["scope"] == "working_tree"
    assert ss["tracked_card_count"] == 2          # both cards on disk
    assert ss["excluded_untracked_paths"] == []
    subjects = {f["subject"] for f in r["findings"]}
    assert {"tracked_paper", "untracked_paper"} <= subjects


def test_committed_scope_findings_are_stable_when_untracked_files_change(tmp_path):
    repo, _ = _make_repo(tmp_path)
    a = _report(repo, "committed")
    # add MORE untracked noise; the committed FINDINGS + counts must not move (the excluded-paths record
    # honestly reflects on-disk state, but a clean CI checkout has none, so the artifact stays canonical)
    (repo / "docs" / "cards" / "another_untracked.md").write_text(
        "# More\n\n**Status:** proposed\n", encoding="utf-8")
    b = _report(repo, "committed")
    assert a["findings"] == b["findings"]
    assert a["counts"] == b["counts"]
    assert b["source_scope"]["untracked_card_count"] == 2      # the record grows, honestly
    # ...but working_tree scope's findings DO move (it reads the untracked files)
    assert _report(repo, "working_tree")["findings"] != a["findings"]


def test_non_git_directory_degrades_to_working_tree_fallback(tmp_path):
    import research_impact as RI
    plain = tmp_path / "plain"
    (plain / "docs" / "cards").mkdir(parents=True)
    (plain / "docs" / "research" / "intake").mkdir(parents=True)
    (plain / "docs" / "research" / "intake" / "schema.json").write_text(
        RI.SCHEMA_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    (plain / "docs" / "cards" / "x.md").write_text("# X\n\n**Status:** card-only\n", encoding="utf-8")
    r = RI.build_report(intake_dir=plain / "docs" / "research" / "intake",
                        cards_dir=plain / "docs" / "cards", components=[],
                        source_scope="committed", repo_root=plain)
    # no git => cannot scope to committed; recorded honestly, not silently canonicalized as 'committed'
    assert r["source_scope"]["scope"] == "working_tree_fallback"


def test_report_schema_version_and_scope_block_present(tmp_path):
    repo, _ = _make_repo(tmp_path)
    r = _report(repo, "committed")
    assert r["schema_version"] == 2
    assert set(r["source_scope"]) >= {"scope", "requested_scope", "tracked_card_count",
                                      "untracked_card_count", "excluded_untracked_paths"}


def test_invalid_scope_rejected():
    import research_impact as RI
    with pytest.raises(ValueError):
        RI.build_report(source_scope="whatever")


def test_live_committed_report_excludes_the_repo_untracked_cards():
    # against the real repo: committed scope must not incorporate any locally-untracked card
    import research_impact as RI
    r = RI.build_report(source_scope="committed")
    assert r["source_scope"]["scope"] in ("committed", "working_tree_fallback")
    for p in r["source_scope"]["excluded_untracked_paths"]:
        assert p.startswith("docs/")

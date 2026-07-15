"""Paper 3 build/verify tests (WP3.2). The verifier is the CI gate for the Paper 3 lane."""
from puckworks.paper3 import build


def test_verify_passes_on_current_tree():
    rep = build.verify()
    assert rep["ok"] is True, rep["problems"]
    assert rep["problems"] == []
    assert rep["bundle_missing"] == []
    # evidence_strength is now populated card-driven -> no unclassified warnings remain.
    assert not any("unclassified evidence_strength" in w for w in rep["warnings"])


def test_bundle_contents_exist():
    from puckworks.paper3.build import REPO_ROOT
    files = build.bundle_contents()
    assert any("generated/registry_export.json" in f for f in files)
    assert "docs/PAPER_3_PUCKWORKS_DRAFT.md" in files
    for f in files:
        assert (REPO_ROOT / f).exists(), f


def test_verify_detects_stale_generated(tmp_path, monkeypatch):
    # a stale generated artifact must make verify fail. Simulate by pointing the generator's
    # verify at an empty root (nothing on disk == everything stale).
    from puckworks.paper3 import registry_artifacts as gen
    monkeypatch.setattr(build.gen, "verify", lambda root=None: ["registry_export.json"])
    rep = build.verify()
    assert rep["ok"] is False
    assert any("stale_generated_artifacts" in p for p in rep["problems"])

"""R4 — release-manifest logic (fast, no build). The actual wheel/sdist build + twine check +
clean-room install run in release.yml (they need `.[release]` + a fresh venv); this guards the
manifest assembler: required fields, per-artifact checksums, and the dirty-tree refusal.
"""
import hashlib

import pytest

from puckworks import release


def test_manifest_hashes_artifacts_and_refuses_dirty_tree(tmp_path):
    (tmp_path / "puckworks-0.1.0-py3-none-any.whl").write_bytes(b"fake wheel bytes")
    (tmp_path / "puckworks-0.1.0.tar.gz").write_bytes(b"fake sdist bytes")

    m = release.release_manifest(tmp_path, dirty_ok=True)   # rehearsal on a (possibly) dirty tree
    assert set(m) >= {"commit", "python", "platform", "artifacts", "manifest_sha256",
                      "citation_present", "license_present"}
    arts = m["artifacts"]
    assert set(arts) == {"puckworks-0.1.0-py3-none-any.whl", "puckworks-0.1.0.tar.gz"}
    assert arts["puckworks-0.1.0.tar.gz"]["sha256"] == \
        hashlib.sha256(b"fake sdist bytes").hexdigest()
    # manifest hash is deterministic over the same inputs
    assert release.release_manifest(tmp_path, dirty_ok=True)["manifest_sha256"] == m["manifest_sha256"]


def test_manifest_refuses_dirty_when_not_allowed(tmp_path, monkeypatch):
    (tmp_path / "puckworks-0.1.0.tar.gz").write_bytes(b"x")
    monkeypatch.setattr(release, "_git", lambda *a, **k: "M some_file")   # simulate dirty tree
    with pytest.raises(RuntimeError, match="DIRTY"):
        release.release_manifest(tmp_path, dirty_ok=False)

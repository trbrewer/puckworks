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


# ---- PW-REL-001/003/004 hardening ----------------------------------------------------------

def test_rehearsal_manifest_is_marked_non_publishable(tmp_path):
    (tmp_path / "puckworks-0.1.0-py3-none-any.whl").write_bytes(b"w")
    m = release.release_manifest(tmp_path, dirty_ok=True, strict=False)
    assert m["publishable"] is False and m["tag"] is None


def test_pw_rel_004_strict_git_cannot_fail_open(tmp_path, monkeypatch):
    # A short/absent commit must raise in strict mode (never inferred).
    monkeypatch.setattr(release, "_git_strict", lambda *a, **k: "abc123")  # not 40-hex
    with pytest.raises(RuntimeError, match="40-hex"):
        release.release_manifest(tmp_path, strict=True)


def test_pw_rel_004_strict_refuses_dirty_and_checks_tag(tmp_path, monkeypatch):
    calls = {}
    def fake_strict(*a, **k):
        if a[0] == "rev-parse":
            return "0" * 40
        if a[0] == "status":
            return ""            # clean
        if a[0] == "rev-list":
            calls["tag_checked"] = a[-1]
            return "f" * 40       # tag points elsewhere -> mismatch
        return ""
    monkeypatch.setattr(release, "_git_strict", fake_strict)
    with pytest.raises(RuntimeError, match="not HEAD"):
        release.release_manifest(tmp_path, strict=True, tag="v1.2.3")
    assert calls["tag_checked"] == "v1.2.3"


def test_pw_rel_003_build_refuses_stale_artifacts(tmp_path, monkeypatch):
    (tmp_path / "stale-9.9.9-py3-none-any.whl").write_bytes(b"old")
    # build must refuse BEFORE invoking `python -m build`
    monkeypatch.setattr(release.subprocess, "run",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("build ran")))
    with pytest.raises(RuntimeError, match="non-empty"):
        release.build(tmp_path)


def test_pw_rel_001_main_enforces_readiness_before_build(monkeypatch):
    monkeypatch.setattr(release, "rights_release_problems", lambda *a, **k: [])
    monkeypatch.setattr(release, "rights_release_gaps", lambda *a, **k: [])
    monkeypatch.setattr(release, "release_readiness", lambda tag, **k: ["tag != version"])
    monkeypatch.setattr(release, "build",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("built despite not-ready")))
    assert release.main(["build", "--tag", "v9.9.9"]) == 2


def test_artifact_version_parsing():
    assert release._artifact_version("puckworks-0.4.0.dev0-py3-none-any.whl") == "0.4.0.dev0"
    assert release._artifact_version("puckworks-0.4.0.dev0.tar.gz") == "0.4.0.dev0"


def test_pw_rel_006_structured_version_parsing(tmp_path):
    # a reformatted pyproject (comments, extra keys, inline comment) still yields the right version
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "x"\n# a comment\nversion = "9.9.9"  # inline\n')
    assert release._toml_project_version(tmp_path / "pyproject.toml") == "9.9.9"
    # a duplicate __version__ is ambiguous and fails, not silently first-wins
    (tmp_path / "i.py").write_text('__version__ = "1.0"\n__version__ = "2.0"\n')
    with pytest.raises(ValueError, match="multiple __version__"):
        release._py_version(tmp_path / "i.py")
    # the real repo's three sources parse and agree
    ok, v = release.versions_agree()
    assert ok and len(set(v.values())) == 1


def test_pw_ci_005_py_typed_marker_present_and_packaged():
    # PEP 561: the package ships a py.typed marker and declares it in package-data so a downstream
    # type checker can consume puckworks' annotations from an installed wheel.
    import puckworks
    from pathlib import Path
    root = Path(puckworks.__file__).resolve().parent
    assert (root / "py.typed").is_file(), "puckworks/py.typed marker is missing"
    pyproject = (root.parent / "pyproject.toml").read_text()
    assert '"py.typed"' in pyproject, "py.typed is not declared in [tool.setuptools.package-data]"

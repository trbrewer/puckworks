from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile


def _load_module():
    path = Path(__file__).resolve().parents[1] / "tools/prepare_paper_release.py"
    spec = importlib.util.spec_from_file_location("prepare_paper_release", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_assert_manifest_requires_clean_fresh_matching_commit() -> None:
    release = _load_module()
    head = "a" * 40
    manifest = {
        "source_commit": head,
        "bundle_source_commit": head,
        "git_dirty": False,
        "bundle_matches_head": True,
        "release_fresh": True,
        "verified": True,
    }
    release.assert_manifest(manifest, head, "A")


def test_deterministic_tar_gz_is_byte_stable(tmp_path: Path) -> None:
    release = _load_module()
    root = tmp_path / "package"
    root.mkdir()
    (root / "a.txt").write_text("alpha\n", encoding="utf-8")
    (root / "nested").mkdir()
    (root / "nested/b.txt").write_text("beta\n", encoding="utf-8")

    first = tmp_path / "first.tar.gz"
    second = tmp_path / "second.tar.gz"
    release.deterministic_tar_gz(root, first, 1234567890)
    release.deterministic_tar_gz(root, second, 1234567890)
    assert first.read_bytes() == second.read_bytes()


def test_python_env_keeps_detached_worktree_clean(tmp_path: Path) -> None:
    release = _load_module()
    env = release.python_env(tmp_path)
    assert env["PYTHONDONTWRITEBYTECODE"] == "1"
    assert env["PYTHONPATH"].split(release.os.pathsep)[0] == str(tmp_path)

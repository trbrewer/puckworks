"""P0.3 — the deterministic Paper 3 release archive: determinism, verify-without-checkout,
tamper/corruption detection, the privacy/redistributability scan, and fail-closed behaviour.
"""
import gzip
import io
import tarfile

import pytest

from puckworks.paper3 import archive as A


def test_build_twice_is_byte_identical(tmp_path):
    m1 = A.create_archive(tmp_path / "a1.tar.gz")
    m2 = A.create_archive(tmp_path / "a2.tar.gz")
    assert m1["archive_sha256"] == m2["archive_sha256"]         # deterministic
    assert (tmp_path / "a1.tar.gz").read_bytes() == (tmp_path / "a2.tar.gz").read_bytes()


def test_archive_verifies_without_the_source_checkout(tmp_path):
    A.create_archive(tmp_path / "a.tar.gz")
    assert A.verify_archive(tmp_path / "a.tar.gz") == []        # reads only the archive


def test_archive_includes_all_generated_evidence(tmp_path):
    m = A.create_archive(tmp_path / "a.tar.gz")
    gen = [x["path"] for x in m["members"] if x["role"] == "generated_evidence"]
    # the evidence-graph outputs (not only the registry_artifacts subset) must be bundled
    names = {p.rsplit("/", 1)[-1] for p in gen}
    assert {"evidence_graph.json", "evidence_graph_summary.json",
            "paper3_priority_evidence_matrix.md", "component_gate_matrix.csv"} <= names


def test_every_member_is_checksummed_and_classified(tmp_path):
    m = A.create_archive(tmp_path / "a.tar.gz")
    for x in m["members"]:
        assert len(x["sha256"]) == 64
        assert x["role"] and x["redistributable"] is True
        assert x["generator_command"]


def test_altering_any_member_fails_verification(tmp_path):
    A.create_archive(tmp_path / "a.tar.gz")
    raw = io.BytesIO()
    with tarfile.open(tmp_path / "a.tar.gz", "r:gz") as src, tarfile.open(fileobj=raw, mode="w") as dst:
        for mem in src.getmembers():
            data = src.extractfile(mem).read()
            if mem.name.endswith("MANIFEST.csv"):
                data = data + b"TAMPER\n"
                mem.size = len(data)
            dst.addfile(mem, io.BytesIO(data))
    (tmp_path / "t.tar.gz").write_bytes(gzip.compress(raw.getvalue(), mtime=0))
    problems = A.verify_archive(tmp_path / "t.tar.gz")
    assert any("sha256 mismatch" in p or "size mismatch" in p for p in problems)


def test_corrupt_archive_is_handled_gracefully(tmp_path):
    (tmp_path / "c.tar.gz").write_bytes(b"not a gzip file")
    problems = A.verify_archive(tmp_path / "c.tar.gz")
    assert problems and any("unreadable/corrupt" in p for p in problems)


def test_privacy_scan_rejects_private_and_absolute_paths():
    assert A._scan_member("paper3_archive/puckworks/data/visualizer/raw/x.json", b"{}")
    assert A._scan_member("/etc/passwd", b"x")
    assert A._scan_member("paper3_archive/../escape", b"x")
    assert A._scan_member("paper3_archive/k.pem",
                          b"-----BEGIN RSA PRIVATE KEY-----")
    assert A._scan_member("paper3_archive/docs/cards/x.md", b"ok") == []   # clean member


def test_fail_closed_on_unresolvable_commit(tmp_path, monkeypatch):
    monkeypatch.setattr(A, "_git", lambda *a, **k: None)          # commit cannot be determined
    with pytest.raises(RuntimeError, match="cannot determine the git commit"):
        A.create_archive(tmp_path / "a.tar.gz")


def test_inspect_reports_roles_and_commit(tmp_path):
    A.create_archive(tmp_path / "a.tar.gz")
    info = A.inspect_archive(tmp_path / "a.tar.gz")
    assert info["member_count"] > 50 and info["commit"]
    assert "card" in info["roles"] and "generated_evidence" in info["roles"]


def test_list_bundle_nonempty():
    assert A.list_bundle()                                        # the renamed path-list

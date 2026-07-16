"""Deterministic Paper 3 release ARCHIVE (P0.3).

The old `paper3.build bundle` only LISTED expected paths. This builds the immutable archive that
name implies: a byte-deterministic `.tar.gz` with an embedded per-member manifest (path, size,
sha256, role, redistributability, generator command), plus verify/inspect operations that do NOT
use the source checkout.

    python -m puckworks.paper3.archive create-archive --out dist/paper3_archive.tar.gz
    python -m puckworks.paper3.archive verify-archive dist/paper3_archive.tar.gz
    python -m puckworks.paper3.archive inspect-archive dist/paper3_archive.tar.gz
    python -m puckworks.paper3.archive list-bundle          # (renamed from `bundle`)

Determinism: members are lexicographically sorted; tar entries carry fixed mtime (the commit's
committer time or SOURCE_DATE_EPOCH), uid/gid 0, empty owner names, normalized mode; the gzip
wrapper is written with mtime=0. Building twice from the same commit yields the same archive
hash. A release-quality archive additionally includes the wheel + sdist (`--with-dist`).

Fail-closed: refuses to include any private/raw corpus path, any member lacking a
redistributability classification, obvious secrets, or absolute paths.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import subprocess
import tarfile
from pathlib import Path

import puckworks  # for __version__
from puckworks.paper3 import registry_artifacts as gen

SCHEMA_VERSION = 1
REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_ROOT = "paper3_archive"   # top-level dir inside the archive (no absolute paths)

# paths that must NEVER enter a redistributable archive (private / raw corpus, caches, secrets)
_PRIVATE_SUBSTRINGS = ("data/visualizer/raw", "data/visualizer/normalized", "data/visualizer/crawl",
                       "aggregate_stats", "/.git/", "__pycache__", ".env", "id_rsa", "secrets")
_SECRET_MARKERS = ("BEGIN RSA PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY", "AWS_SECRET_ACCESS_KEY")


def _git(*args, root=REPO_ROOT):
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


def _source_date_epoch(root=REPO_ROOT):
    env = os.environ.get("SOURCE_DATE_EPOCH")
    if env and env.isdigit():
        return int(env)
    ct = _git("show", "-s", "--format=%ct", "HEAD", root=root)
    return int(ct) if ct and ct.isdigit() else 0


# ---- membership -------------------------------------------------------------------------
def _static_members(root):
    """(repo_relpath, role, redistributable) for the fixed payload — only files that exist."""
    root = Path(root)
    out = []

    def add(rel, role, redist=True):
        if (root / rel).exists():
            out.append((rel, role, redist))

    for n in ("LICENSE", "LICENSE.txt", "LICENSE.md", "CITATION.cff", "CHANGELOG.md"):
        add(n, "metadata")
    add("docs/PAPER_3_PUCKWORKS_DRAFT.md", "manuscript")
    add("docs/CLAIM_OWNERSHIP.md", "manuscript")
    add("docs/paper3_resource/EVIDENCE_GRAPH.md", "evidence_spec")
    add("puckworks/paper3/EVIDENCE_LINKS.json", "evidence_source")
    add("puckworks/data/MANIFEST.csv", "data_provenance")
    add("puckworks/data/visualizer/PROVENANCE.md", "data_provenance")
    # ALL generated Paper-3 evidence artifacts (registry_artifacts + evidence_graph outputs)
    for p in sorted((root / gen.GENERATED_REL).glob("*")):
        if p.is_file():
            out.append((p.relative_to(root).as_posix(), "generated_evidence", True))
    # model/source cards (physics source of truth used by the paper)
    for p in sorted((root / "docs/cards").glob("*.md")):
        out.append((p.relative_to(root).as_posix(), "card", True))
    return out


def _dist_members(dist_dir, root):
    out = []
    if dist_dir is None:
        return out
    for p in sorted(Path(dist_dir).glob("*")):
        if p.suffix == ".whl":
            out.append((p, "wheel", True))
        elif p.suffixes[-2:] == [".tar", ".gz"] or p.suffix == ".gz":
            out.append((p, "sdist", True))
    return out


def _reproduction_md(commit, sde):
    return (
        "# Paper 3 archive — reproduction\n\n"
        "Source commit: `%s`\nSOURCE_DATE_EPOCH: `%s`\n\n"
        "Rebuild and verify:\n\n"
        "```\n"
        "python -m puckworks.paper3.archive create-archive --out paper3_archive.tar.gz\n"
        "python -m puckworks.paper3.archive verify-archive paper3_archive.tar.gz\n"
        "```\n\n"
        "Regenerate the evidence artifacts (must be byte-identical to those bundled here):\n\n"
        "```\n"
        "python -m puckworks.paper3.registry_artifacts --verify\n"
        "python -m puckworks.paper3.evidence_graph --verify\n"
        "python -m puckworks.paper3.evidence_graph --reconcile --strict --scope all\n"
        "```\n" % (commit, sde))


# ---- scans ------------------------------------------------------------------------------
def _scan_member(arcname, data):
    """Return a list of problems for one member (privacy / secrets / absolute path)."""
    problems = []
    low = arcname.lower()
    if arcname.startswith("/") or ".." in Path(arcname).parts:
        problems.append("absolute/traversal path: %s" % arcname)
    for s in _PRIVATE_SUBSTRINGS:
        if s in low:
            problems.append("private/raw path in archive: %s" % arcname)
            break
    head = data[:65536]
    for marker in _SECRET_MARKERS:
        if marker.encode() in head:
            problems.append("possible secret in %s (%s)" % (arcname, marker))
    return problems


# ---- create -----------------------------------------------------------------------------
def _tarinfo(name, size, sde, mode=0o644):
    ti = tarfile.TarInfo(name)
    ti.size = size
    ti.mtime = sde
    ti.mode = mode
    ti.uid = ti.gid = 0
    ti.uname = ti.gname = ""
    ti.type = tarfile.REGTYPE
    return ti


def create_archive(out_path, root=REPO_ROOT, with_dist=False, dist_dir=None, dirty_ok=True):
    """Build the deterministic archive at `out_path`. Returns the manifest dict. Fail-closed on
    private paths, unclassified members, secrets, a dirty tree (unless dirty_ok), or an
    unresolvable commit."""
    root = Path(root)
    commit = _git("rev-parse", "HEAD", root=root)
    if commit is None:
        raise RuntimeError("cannot determine the git commit — refusing to build an archive")
    if not dirty_ok and _git("status", "--porcelain", root=root):
        raise RuntimeError("refusing to build a release archive on a DIRTY tree")
    # fail closed on stale generated evidence — the archive must match the source
    from puckworks.paper3 import evidence_graph as eg
    stale = gen.verify(root) + eg.verify(root)
    if stale:
        raise RuntimeError("refusing to archive STALE generated evidence: %s" % ",".join(stale))
    sde = _source_date_epoch(root)

    # collect (arcname, bytes, role, redistributable), sorted, with fixed generator command
    members = []
    problems = []
    for rel, role, redist in _static_members(root):
        data = (root / rel).read_bytes()
        arc = "%s/%s" % (ARCHIVE_ROOT, rel)
        problems += _scan_member(arc, data)
        members.append((arc, data, role, redist, "python -m puckworks.paper3.archive create-archive"))
    if with_dist:
        for p, role, redist in _dist_members(dist_dir, root):
            data = Path(p).read_bytes()
            arc = "%s/dist/%s" % (ARCHIVE_ROOT, Path(p).name)
            problems += _scan_member(arc, data)
            members.append((arc, data, role, redist, "python -m puckworks.release build"))
    # synthesized members
    repro = _reproduction_md(commit, sde).encode("utf-8")
    members.append(("%s/REPRODUCTION.md" % ARCHIVE_ROOT, repro, "reproduction", True,
                    "python -m puckworks.paper3.archive create-archive"))

    # fail-closed checks
    for arc, data, role, redist, _cmd in members:
        if redist not in (True, False):
            problems.append("%s: missing redistributability classification" % arc)
        if redist is not True:
            problems.append("%s: not classified redistributable (role=%s)" % (arc, role))
    if problems:
        raise RuntimeError("archive fail-closed:\n  " + "\n  ".join(sorted(set(problems))))

    members.sort(key=lambda m: m[0])
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "archive_root": ARCHIVE_ROOT,
        "commit": commit,
        "source_date_epoch": sde,
        "generator": "python -m puckworks.paper3.archive create-archive",
        "generator_version": getattr(puckworks, "__version__", "unknown"),
        "member_count": len(members),
        "members": [{"path": arc, "bytes": len(data),
                     "sha256": hashlib.sha256(data).hexdigest(), "role": role,
                     "redistributable": redist, "generator_command": cmd}
                    for (arc, data, role, redist, cmd) in members],
    }
    manifest_bytes = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")

    # deterministic tar (uncompressed) in memory, then a gzip wrapper with mtime=0
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as tar:
        for arc, data, _role, _redist, _cmd in members:
            tar.addfile(_tarinfo(arc, len(data), sde), io.BytesIO(data))
        # MANIFEST.json is added LAST and is NOT self-referential (covers the other members)
        tar.addfile(_tarinfo("%s/MANIFEST.json" % ARCHIVE_ROOT, len(manifest_bytes), sde),
                    io.BytesIO(manifest_bytes))
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as fh:
        # filename="" so the gzip FNAME header does NOT embed the output path (determinism)
        with gzip.GzipFile(filename="", fileobj=fh, mode="wb", mtime=0, compresslevel=9) as gz:
            gz.write(raw.getvalue())
    manifest["archive_sha256"] = hashlib.sha256(out.read_bytes()).hexdigest()
    return manifest


# ---- verify / inspect (do NOT use the source checkout) ----------------------------------
def _read_manifest(path):
    with tarfile.open(path, mode="r:gz") as tar:
        name = "%s/MANIFEST.json" % ARCHIVE_ROOT
        member = tar.getmember(name)
        return json.loads(tar.extractfile(member).read().decode("utf-8"))


def verify_archive(path):
    """Verify the archive WITHOUT the source checkout: every declared member is present with the
    recorded sha256, and no undeclared member exists. Returns a list of problems (empty = ok)."""
    problems = []
    try:
        manifest = _read_manifest(path)
    except Exception as e:
        return ["archive is unreadable/corrupt: %s: %s" % (type(e).__name__, e)]
    declared = {m["path"]: m for m in manifest["members"]}
    seen = set()
    with tarfile.open(path, mode="r:gz") as tar:
        for member in tar.getmembers():
            if member.name == "%s/MANIFEST.json" % ARCHIVE_ROOT:
                continue
            seen.add(member.name)
            data = tar.extractfile(member).read()
            d = declared.get(member.name)
            if d is None:
                problems.append("undeclared member in archive: %s" % member.name)
                continue
            got = hashlib.sha256(data).hexdigest()
            if got != d["sha256"]:
                problems.append("sha256 mismatch: %s" % member.name)
            if len(data) != d["bytes"]:
                problems.append("size mismatch: %s" % member.name)
            problems += _scan_member(member.name, data)   # privacy holds at verify time too
    for name in declared:
        if name not in seen:
            problems.append("declared member missing from archive: %s" % name)
    return problems


def inspect_archive(path):
    m = _read_manifest(path)
    return {"commit": m["commit"], "member_count": m["member_count"],
            "generator_version": m.get("generator_version"),
            "roles": _count_roles(m["members"]),
            "members": [(x["path"], x["role"], x["sha256"][:12]) for x in m["members"]]}


def _count_roles(members):
    c = {}
    for m in members:
        c[m["role"]] = c.get(m["role"], 0) + 1
    return dict(sorted(c.items()))


# ---- renamed list-bundle (was `bundle`) -------------------------------------------------
def list_bundle(root=REPO_ROOT):
    from puckworks.paper3.build import bundle_contents
    return bundle_contents()


def main(argv=None):
    p = argparse.ArgumentParser(prog="puckworks.paper3.archive")
    p.add_argument("cmd", choices=["create-archive", "verify-archive", "inspect-archive",
                                   "list-bundle", "bundle"])
    p.add_argument("path", nargs="?")
    p.add_argument("--out", default=str(REPO_ROOT / "dist" / "paper3_archive.tar.gz"))
    p.add_argument("--with-dist", action="store_true")
    p.add_argument("--dist-dir", default=str(REPO_ROOT / "dist"))
    p.add_argument("--no-dirty-ok", action="store_true")
    a = p.parse_args(argv)
    if a.cmd == "create-archive":
        m = create_archive(a.out, with_dist=a.with_dist,
                           dist_dir=a.dist_dir if a.with_dist else None,
                           dirty_ok=not a.no_dirty_ok)
        print("archive -> %s\n  commit %s  members %d  sha256 %s"
              % (a.out, m["commit"], m["member_count"], m["archive_sha256"][:16]))
        return 0
    if a.cmd == "verify-archive":
        problems = verify_archive(a.path or a.out)
        if problems:
            print("ARCHIVE VERIFY FAILED (%d):" % len(problems))
            for pr in problems:
                print("  -", pr)
            return 1
        print("archive verified: every member present with the recorded sha256")
        return 0
    if a.cmd == "inspect-archive":
        print(json.dumps(inspect_archive(a.path or a.out), indent=2))
        return 0
    if a.cmd == "bundle":
        print("NOTE: `bundle` is renamed to `list-bundle` (it lists paths, it does not archive).")
    for f in list_bundle():
        print(f)
    return 0


if __name__ == "__main__":   # pragma: no cover
    raise SystemExit(main())

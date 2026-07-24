"""R4 — a real, clean-room release pipeline (NOT a path list).

`python -m puckworks.release build` produces a wheel + sdist, metadata-checks them, and writes
a release manifest with commit, environment, and SHA-256 checksums. The clean-room INSTALL of
the built wheel outside the repo is done by `release.yml` (needs a fresh venv). This replaces
the old `paper3.build` file-list, which only listed expected paths.

Requires the `[release]` extra (`build`, `twine`).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(*args, root=REPO_ROOT):
    """Lenient git — returns None on any failure. For REHEARSAL only; a release must use _git_strict
    so an unavailable git cannot be read as 'clean tree / no commit' (PW-REL-004)."""
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


def _git_strict(*args, root=REPO_ROOT):
    """Strict git — raises RuntimeError if git is unavailable or the command fails. Used in release
    mode so provenance can never fail open."""
    r = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError("git %s failed (rc=%d): %s"
                           % (" ".join(args), r.returncode, (r.stderr or "").strip()))
    return r.stdout.strip()


def _verify_tag_is_head(tag, head_commit, root=REPO_ROOT):
    """Require the release tag to point at exactly HEAD (annotated or lightweight)."""
    peeled = _git_strict("rev-list", "-n", "1", tag, root=root)
    if peeled != head_commit:
        raise RuntimeError("release tag %r points at %s, not HEAD %s"
                           % (tag, peeled[:12], head_commit[:12]))


def _find(pattern, text):
    import re
    m = re.search(pattern, text, re.MULTILINE)
    return m.group(1) if m else None


def package_versions(root=REPO_ROOT):
    """The version declared in each authoritative source; all MUST agree."""
    root = Path(root)
    return {
        "pyproject": _find(r'^version = "([^"]+)"', (root / "pyproject.toml").read_text()),
        "__version__": _find(r'^__version__ = "([^"]+)"',
                             (root / "puckworks" / "__init__.py").read_text()),
        "citation": _find(r'^version: "([^"]+)"', (root / "CITATION.cff").read_text()),
    }


def versions_agree(root=REPO_ROOT):
    """(ok, {source: version}). ok is True iff all code-declared versions are identical."""
    v = package_versions(root)
    return (None not in v.values() and len(set(v.values())) == 1), v


def release_readiness(tag, root=REPO_ROOT):
    """Release-time cross-checks that need the tag + changelog. Returns a list of problems.
    Verifies tag == package version and the CHANGELOG has a matching version heading."""
    root = Path(root)
    problems = []
    ok, v = versions_agree(root)
    if not ok:
        problems.append("code versions disagree: %r" % v)
    ver = v["pyproject"]
    tag_ver = tag[1:] if tag and tag.startswith("v") else tag
    if tag_ver and ver and tag_ver != ver:
        problems.append("tag %r != package version %r" % (tag, ver))
    changelog = (root / "CHANGELOG.md").read_text()
    if ver and ("## %s" % ver) not in changelog:
        problems.append("CHANGELOG.md has no '## %s' section" % ver)
    return problems


def _module_present(root: Path, component_id: str) -> bool:
    pkg = component_id.split(".")[0]
    return (root / "puckworks/models" / pkg).exists() or any(
        root.glob("puckworks/models/%s/*.py" % pkg))


def rights_release_problems(root=REPO_ROOT):
    """A newly approved release artifact must not include any component whose CODE is not cleared for
    release inclusion (`rights.may_include_code_in_release` -> severity 'blocked'). Returns a problem per
    such component whose module is still present under the package tree. There is NO override flag: an
    authorized removal makes this pass because the blocked module is gone, not by a 'build anyway' bypass.
    NOT_REVIEWED is a reported gap (see rights_release_gaps), not a hard block."""
    root = Path(root)
    try:
        from puckworks import rights
        registered = [c.name for c in __import__("puckworks").components()]
    except Exception as exc:                       # pragma: no cover - import guard
        return ["could not evaluate rights guard: %r" % exc]
    problems = []
    for cid in sorted(registered):
        decision = rights.may_include_code_in_release(cid)
        if decision.severity == "blocked" and _module_present(root, cid):
            rec = rights.rights_record(cid)
            problems.append(
                "code-rights-blocked component %r would enter the release artifact (module under "
                "puckworks/models/%s/); resolve %s before releasing (no override flag exists — an "
                "authorized removal makes this pass)"
                % (cid, cid.split(".")[0], rec.decision_issue or "the rights review"))
    return problems


def rights_release_gaps(root=REPO_ROOT):
    """Components present in the tree whose code rights are a reported GAP (NOT_REVIEWED /
    RIGHTS_REVIEW_REQUIRED) for release inclusion. Not a hard block — surfaced so release readiness
    reports the gap explicitly rather than silently passing."""
    root = Path(root)
    from puckworks import rights
    registered = [c.name for c in __import__("puckworks").components()]
    gaps = []
    for cid in sorted(registered):
        decision = rights.may_include_code_in_release(cid)
        if decision.severity == "gap" and _module_present(root, cid):
            gaps.append("%s (%s)" % (cid, decision.governing_state))
    return gaps


def _artifact_version(path):
    """Version token from a wheel (name-VERSION-...) or sdist (name-VERSION.tar.gz) filename."""
    name = Path(path).name
    if name.endswith(".whl"):
        parts = name[:-len(".whl")].split("-")
        return parts[1] if len(parts) >= 2 else None
    if name.endswith(".tar.gz"):
        stem = name[:-len(".tar.gz")]
        parts = stem.rsplit("-", 1)
        return parts[1] if len(parts) == 2 else None
    return None


def build(outdir, root=REPO_ROOT, clean=False):
    """Build wheel + sdist into a CLEAN `outdir` via `python -m build`. Refuses to build into a
    directory that already holds artifacts (stale wheels/sdists must not enter checks, the manifest,
    or the clean-room install) unless `clean=True` clears them first. Requires exactly one wheel and
    one sdist whose versions match the declared package version. Returns {'wheel', 'sdist'} paths."""
    out = Path(outdir)
    if out.exists():
        stale = [p for p in out.iterdir()
                 if p.name.endswith(".whl") or p.name.endswith(".tar.gz")]
        if stale:
            if not clean:
                raise RuntimeError("refusing to build into non-empty %s (stale artifacts: %s); "
                                   "pass clean=True to clear them first"
                                   % (out, sorted(p.name for p in stale)))
            for p in stale:
                p.unlink()
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "build", "--outdir", str(out), str(root)], check=True)
    wheels, sdists = sorted(out.glob("*.whl")), sorted(out.glob("*.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError("expected exactly one wheel and one sdist, got %d wheel(s) / %d sdist(s) in %s"
                           % (len(wheels), len(sdists), out))
    _, v = versions_agree(root)
    pkg_ver = v["pyproject"]
    wv, sv = _artifact_version(wheels[0]), _artifact_version(sdists[0])
    if pkg_ver and (wv != pkg_ver or sv != pkg_ver):
        raise RuntimeError("artifact versions (wheel %r, sdist %r) != package version %r"
                           % (wv, sv, pkg_ver))
    return {"wheel": wheels[0], "sdist": sdists[0]}


def twine_check(paths):
    """Validate artifact metadata with `twine check` on the EXACT built paths (not a glob)."""
    subprocess.run([sys.executable, "-m", "twine", "check", *(str(p) for p in paths)], check=True)


def release_manifest(outdir, root=REPO_ROOT, dirty_ok=False, strict=False, tag=None, artifacts=None):
    """Assemble the release manifest: exact commit, environment, and per-artifact SHA-256.

    strict=False (REHEARSAL): lenient git; the manifest is marked ``publishable: False``.
    strict=True  (RELEASE):   git must be available and return a full 40-hex commit and a real
    dirty-status (never inferred clean from an error); a supplied ``tag`` must point at HEAD.
    `artifacts` may be an explicit list of built paths; otherwise the *.whl/*.gz in `outdir` are used.
    """
    out = Path(outdir)
    if strict:
        commit = _git_strict("rev-parse", "HEAD", root=root)
        if not _FULL_SHA.match(commit or ""):
            raise RuntimeError("release requires a full 40-hex commit; got %r" % commit)
        dirty = bool(_git_strict("status", "--porcelain", root=root))   # raises if git fails
        if dirty and not dirty_ok:
            raise RuntimeError("refusing to build a RELEASE manifest on a DIRTY tree")
        if tag:
            _verify_tag_is_head(tag, commit, root=root)
        publishable = not dirty
    else:
        dirty = bool(_git("status", "--porcelain", root=root))
        if dirty and not dirty_ok:
            raise RuntimeError("refusing to build a release manifest on a DIRTY tree "
                               "(commit or pass dirty_ok=True for a rehearsal)")
        commit = _git("rev-parse", "HEAD", root=root)
        publishable = False                       # a rehearsal manifest is never publishable
    paths = (list(artifacts) if artifacts is not None
             else [p for p in sorted(out.glob("*")) if p.suffix in (".whl", ".gz")])
    artifacts_meta = {p.name: {"sha256": _sha256(p), "bytes": p.stat().st_size} for p in paths}
    manifest = {
        "commit": commit,
        "dirty": dirty,
        "publishable": publishable,
        "tag": tag,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "citation_present": (Path(root) / "CITATION.cff").exists(),
        "license_present": any((Path(root) / n).exists() for n in ("LICENSE", "LICENSE.txt", "LICENSE.md")),
        "artifacts": artifacts_meta,
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode("utf-8")).hexdigest()
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(prog="puckworks.release")
    p.add_argument("cmd", choices=["build"], nargs="?", default="build")
    p.add_argument("--outdir", default=str(REPO_ROOT / "dist"))
    p.add_argument("--tag", default=None,
                   help="release tag (vX.Y.Z). Enables RELEASE mode: readiness gate + strict git "
                        "provenance + tag==HEAD. Omit for a non-publishable REHEARSAL build.")
    p.add_argument("--clean", action="store_true",
                   help="clear stale artifacts from --outdir before building")
    p.add_argument("--dirty-ok", action="store_true")
    a = p.parse_args(argv)
    release_mode = a.tag is not None
    # Rights guard: hard-block only on code not cleared for release inclusion. There is NO generic
    # bypass flag — an authorized removal makes this pass by removing the blocked module.
    rights_problems = rights_release_problems()
    if rights_problems:
        for prob in rights_problems:
            print("RELEASE BLOCKED (rights): %s" % prob)
        return 2
    for gap in rights_release_gaps():           # reported, not silently passed
        print("RELEASE RIGHTS GAP (not a block; review owed): %s" % gap)
    # PW-REL-001: enforce release readiness (tag == version, changelog) BEFORE building.
    if release_mode:
        problems = release_readiness(a.tag)
        if problems:
            for prob in problems:
                print("RELEASE NOT READY: %s" % prob)
            return 2
    else:
        print("REHEARSAL build (no --tag): the manifest is marked non-publishable")
    arts = build(a.outdir, clean=a.clean)
    paths = [arts["wheel"], arts["sdist"]]
    twine_check(paths)
    manifest = release_manifest(a.outdir, dirty_ok=a.dirty_ok, strict=release_mode,
                                tag=a.tag, artifacts=paths)
    dst = Path(a.outdir) / "release_manifest.json"
    dst.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print("release manifest -> %s" % dst)
    print("  commit %s (dirty=%s, publishable=%s) py %s"
          % (manifest.get("commit"), manifest.get("dirty"),
             manifest.get("publishable"), manifest.get("python")))
    for name, meta in manifest.get("artifacts", {}).items():
        print("  %s  %s" % (meta["sha256"][:16], name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _git(*args, root=REPO_ROOT):
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return None


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


def rights_release_problems(root=REPO_ROOT):
    """A newly approved release artifact must not include any code-rights-BLOCKED component (issue #73).
    Returns a problem per blocked component whose module file is still present under the package tree.
    NOT_REVIEWED is a visible gap, not a block. This surfaces the exact component + decision issue."""
    root = Path(root)
    try:
        from puckworks import rights
        records = rights.all_rights()
    except Exception as exc:                       # pragma: no cover - import guard
        return ["could not evaluate rights guard: %r" % exc]
    problems = []
    for rec in records:
        if not rec.is_code_blocked:
            continue
        mod_path = root / (rec.component_id.split(".")[0] and
                           "puckworks/models/%s" % rec.component_id.split(".")[0])
        present = mod_path.exists() or any(
            root.glob("puckworks/models/%s/*.py" % rec.component_id.split(".")[0]))
        if present:
            problems.append(
                "RIGHTS_BLOCKED component %r would enter the release artifact (module under "
                "puckworks/models/%s/); resolve %s before releasing"
                % (rec.component_id, rec.component_id.split(".")[0], rec.decision_issue or "the rights review"))
    return problems


def build(outdir, root=REPO_ROOT):
    """Build wheel + sdist into `outdir` via `python -m build`. Returns the artifact paths."""
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, "-m", "build", "--outdir", str(out), str(root)], check=True)
    wheels = sorted(out.glob("*.whl"))
    sdists = sorted(out.glob("*.tar.gz"))
    if not wheels or not sdists:
        raise RuntimeError("build did not produce both a wheel and an sdist in %s" % out)
    return {"wheels": wheels, "sdists": sdists}


def twine_check(outdir):
    """Validate artifact metadata with `twine check` (long-description, classifiers, etc.)."""
    subprocess.run([sys.executable, "-m", "twine", "check", *(str(p) for p in Path(outdir).glob("*"))],
                   check=True)


def release_manifest(outdir, root=REPO_ROOT, dirty_ok=False):
    """Assemble the release manifest for the artifacts in `outdir`: exact commit, environment,
    and per-artifact SHA-256. Raises on a dirty tree unless `dirty_ok`."""
    out = Path(outdir)
    dirty = bool(_git("status", "--porcelain", root=root))
    if dirty and not dirty_ok:
        raise RuntimeError("refusing to build a release manifest on a DIRTY tree "
                           "(commit or pass dirty_ok=True for a rehearsal)")
    artifacts = {p.name: {"sha256": _sha256(p), "bytes": p.stat().st_size}
                 for p in sorted(out.glob("*")) if p.suffix in (".whl", ".gz")}
    manifest = {
        "commit": _git("rev-parse", "HEAD", root=root),
        "dirty": dirty,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "citation_present": (Path(root) / "CITATION.cff").exists(),
        "license_present": any((Path(root) / n).exists() for n in ("LICENSE", "LICENSE.txt", "LICENSE.md")),
        "artifacts": artifacts,
    }
    manifest["manifest_sha256"] = hashlib.sha256(
        json.dumps(manifest, sort_keys=True).encode("utf-8")).hexdigest()
    return manifest


def main(argv=None):
    p = argparse.ArgumentParser(prog="puckworks.release")
    p.add_argument("cmd", choices=["build"], nargs="?", default="build")
    p.add_argument("--outdir", default=str(REPO_ROOT / "dist"))
    p.add_argument("--dirty-ok", action="store_true")
    p.add_argument("--allow-rights-blocked", action="store_true",
                   help="build despite a RIGHTS_BLOCKED component (only after an authorized removal)")
    a = p.parse_args(argv)
    rights_problems = rights_release_problems()
    if rights_problems and not a.allow_rights_blocked:
        for prob in rights_problems:
            print("RELEASE BLOCKED (rights): %s" % prob)
        return 2
    build(a.outdir)
    twine_check(a.outdir)
    manifest = release_manifest(a.outdir, dirty_ok=a.dirty_ok)
    dst = Path(a.outdir) / "release_manifest.json"
    dst.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print("release manifest -> %s" % dst)
    print("  commit %s (dirty=%s) py %s" % (manifest["commit"], manifest["dirty"], manifest["python"]))
    for name, meta in manifest["artifacts"].items():
        print("  %s  %s" % (meta["sha256"][:16], name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

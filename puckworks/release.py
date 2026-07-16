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
    a = p.parse_args(argv)
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

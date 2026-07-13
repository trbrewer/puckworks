#!/usr/bin/env python3
"""Build Paper A/B release archives without dirtying the tagged source commit.

The tracked result bundles embed a Git commit.  Recomputing them in-place and then
committing them advances HEAD, so an in-tree "recompute -> commit -> strict verify"
cycle is self-referential.  This tool instead:

1. requires a clean source checkout and records HEAD;
2. creates a detached worktree at exactly that commit;
3. writes all generated bundles, manifests, figures, and source-data exports to an
   *external* staging directory, leaving the worktree clean;
4. runs each paper's existing strict verifier against the staged bundle;
5. overlays the generated files onto `git archive HEAD`; and
6. writes a deterministic tar.gz plus SHA-256 sidecar.

The Git tag remains a source tag.  The release archive is the frozen, generated
submission object whose provenance resolves to that tag's commit.
"""
from __future__ import annotations

import argparse
import contextlib
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_LOCK = REPO_ROOT / "docs/reproducibility/paper_release_environment.json"


def run(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str] | None = None,
    capture: bool = False,
) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )
    return completed.stdout.strip() if capture else ""


def git(*args: str, cwd: Path = REPO_ROOT) -> str:
    return run(["git", *args], cwd=cwd, capture=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256(path)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def ensure_clean_checkout(repo: Path) -> str:
    dirty = git("status", "--porcelain=v1", "--untracked-files=all", cwd=repo)
    if dirty:
        raise RuntimeError(
            "release preparation requires a clean checkout; git status reported:\n"
            + dirty
        )
    return git("rev-parse", "HEAD", cwd=repo)


def check_environment(repo: Path) -> dict[str, Any]:
    checker = repo / "tools/check_release_environment.py"
    output = run(
        [sys.executable, str(checker), "--lock", str(ENV_LOCK), "--json"],
        cwd=repo,
        capture=True,
    )
    payload = json.loads(output)
    if not payload["ok"]:  # defensive: the checker normally exits non-zero first
        raise RuntimeError("release environment mismatch: " + json.dumps(payload))
    return payload["observed"]


def python_env(worktree: Path) -> dict[str, str]:
    env = os.environ.copy()
    prior = env.get("PYTHONPATH")
    env["PYTHONPATH"] = str(worktree) + (os.pathsep + prior if prior else "")
    env.setdefault("PYTHONHASHSEED", "0")
    env.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    env.setdefault("MPLBACKEND", "Agg")
    return env


def build_paper_a(worktree: Path, stage: Path, timestamp: str | None) -> dict[str, Any]:
    bundle = stage / "docs/figures/paper_a/results.json"
    figures = stage / "docs/figures/paper_a"
    manifest = stage / "docs/reproducibility/paper_a_manifest.json"
    script = r'''
import json
from pathlib import Path
from puckworks.figures_paper_a import compute_all, export_source_data, render_all
from puckworks.paper_a.build import verify
bundle = Path(__BUNDLE__)
outdir = Path(__FIGURES__)
manifest_path = Path(__MANIFEST__)
bundle.parent.mkdir(parents=True, exist_ok=True)
manifest_path.parent.mkdir(parents=True, exist_ok=True)
results = compute_all(out_path=str(bundle))
render_all(results=results, outdir=str(outdir))
export_source_data(results=results, outdir=str(outdir))
ok, failures, manifest = verify(
    bundle_path=str(bundle), timestamp=__TIMESTAMP__, write_manifest=False, strict=True
)
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
if not ok:
    raise SystemExit("Paper A strict verification failed:\n" + "\n".join(failures))
print(json.dumps(manifest))
'''
    script = (
        script.replace("__BUNDLE__", repr(str(bundle)))
        .replace("__FIGURES__", repr(str(figures)))
        .replace("__MANIFEST__", repr(str(manifest)))
        .replace("__TIMESTAMP__", repr(timestamp))
    )
    output = run(
        [sys.executable, "-c", script],
        cwd=worktree,
        env=python_env(worktree),
        capture=True,
    )
    return json.loads(output.splitlines()[-1])


def build_paper_b(worktree: Path, stage: Path, timestamp: str | None) -> dict[str, Any]:
    bundle = stage / "docs/figures/paper_b_results.json"
    figures = stage / "docs/figures"
    manifest = stage / "docs/reproducibility/paper_b_manifest.json"
    script = r'''
import json
from pathlib import Path
from puckworks.figures import render_all
from puckworks.paper_b.build import compute, verify
bundle = Path(__BUNDLE__)
outdir = Path(__FIGURES__)
manifest_path = Path(__MANIFEST__)
bundle.parent.mkdir(parents=True, exist_ok=True)
manifest_path.parent.mkdir(parents=True, exist_ok=True)
compute(out_path=str(bundle), include_slow=True)
render_all(outdir=str(outdir))
ok, failures, manifest = verify(
    bundle_path=str(bundle), timestamp=__TIMESTAMP__, write_manifest=False, strict=True
)
manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
if not ok:
    raise SystemExit("Paper B strict verification failed:\n" + "\n".join(failures))
print(json.dumps(manifest))
'''
    script = (
        script.replace("__BUNDLE__", repr(str(bundle)))
        .replace("__FIGURES__", repr(str(figures)))
        .replace("__MANIFEST__", repr(str(manifest)))
        .replace("__TIMESTAMP__", repr(timestamp))
    )
    output = run(
        [sys.executable, "-c", script],
        cwd=worktree,
        env=python_env(worktree),
        capture=True,
    )
    return json.loads(output.splitlines()[-1])


def assert_manifest(manifest: dict[str, Any], head: str, paper: str) -> None:
    failures: list[str] = []
    if manifest.get("source_commit") != head:
        failures.append("manifest.source_commit != HEAD")
    if manifest.get("bundle_source_commit") != head:
        failures.append("manifest.bundle_source_commit != HEAD")
    if manifest.get("git_dirty") is not False:
        failures.append("manifest.git_dirty is not false")
    if manifest.get("bundle_matches_head") is not True:
        failures.append("manifest.bundle_matches_head is not true")
    if manifest.get("release_fresh") is not True:
        failures.append("manifest.release_fresh is not true")
    if manifest.get("verified") is not True:
        failures.append("manifest.verified is not true")
    if failures:
        raise RuntimeError(f"Paper {paper} provenance failed: " + "; ".join(failures))


def extract_git_archive(worktree: Path, head: str, destination: Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(suffix=".tar", delete=False) as handle:
        archive_path = Path(handle.name)
    try:
        with archive_path.open("wb") as handle:
            subprocess.run(
                ["git", "archive", "--format=tar", head],
                cwd=worktree,
                check=True,
                stdout=handle,
            )
        with tarfile.open(archive_path, "r:") as archive:
            archive.extractall(destination, filter="data")
    finally:
        archive_path.unlink(missing_ok=True)


def overlay_tree(source: Path, destination: Path) -> None:
    for path in sorted(source.rglob("*")):
        rel = path.relative_to(source)
        target = destination / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.unlink(missing_ok=True)
            target.symlink_to(os.readlink(path))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, target)


def deterministic_tar_gz(source_dir: Path, output: Path, mtime: int) -> None:
    """Write a sorted gzip-compressed tar with normalized ownership and time."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            with tarfile.open(fileobj=gz, mode="w|") as archive:
                for path in sorted(source_dir.rglob("*"), key=lambda p: p.as_posix()):
                    arcname = path.relative_to(source_dir.parent).as_posix()
                    info = archive.gettarinfo(str(path), arcname=arcname)
                    info.uid = 0
                    info.gid = 0
                    info.uname = "root"
                    info.gname = "root"
                    info.mtime = mtime
                    if info.isfile():
                        with path.open("rb") as handle:
                            archive.addfile(info, handle)
                    else:
                        archive.addfile(info)


def papers_from_arg(value: str) -> Iterable[str]:
    return ("a", "b") if value == "all" else (value,)


def prepare_one(
    paper: str,
    *,
    worktree: Path,
    head: str,
    output_dir: Path,
    timestamp: str | None,
    environment: dict[str, Any],
    source_epoch: int,
) -> Path:
    with tempfile.TemporaryDirectory(prefix=f"puckworks-paper-{paper}-stage-") as tmp:
        stage = Path(tmp) / "generated"
        stage.mkdir(parents=True)
        manifest = (
            build_paper_a(worktree, stage, timestamp)
            if paper == "a"
            else build_paper_b(worktree, stage, timestamp)
        )
        assert_manifest(manifest, head, paper.upper())

        dirty_after = git(
            "status", "--porcelain=v1", "--untracked-files=all", cwd=worktree
        )
        if dirty_after:
            raise RuntimeError(
                "build wrote into the detached source worktree instead of external staging:\n"
                + dirty_after
            )

        generated_hashes = file_hashes(stage)
        provenance = {
            "schema_version": 1,
            "paper": paper.upper(),
            "source_commit": head,
            "suggested_tag": f"paper-{paper}-v1.0.0",
            "source_tree_clean": True,
            "build_outputs_external_to_source_tree": True,
            "strict_manifest_verified": True,
            "timestamp_utc": timestamp,
            "environment": environment,
            "generated_sha256": generated_hashes,
        }
        provenance_path = (
            stage
            / "docs/reproducibility"
            / f"paper_{paper}_release_provenance.json"
        )
        provenance_path.parent.mkdir(parents=True, exist_ok=True)
        provenance_path.write_text(
            json.dumps(provenance, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        package_name = f"puckworks-paper-{paper}-{head[:12]}"
        release_root = Path(tmp) / package_name
        extract_git_archive(worktree, head, release_root)
        overlay_tree(stage, release_root)

        archive_path = output_dir / f"{package_name}.tar.gz"
        deterministic_tar_gz(release_root, archive_path, source_epoch)
        digest = sha256(archive_path)
        archive_path.with_suffix(archive_path.suffix + ".sha256").write_text(
            f"{digest}  {archive_path.name}\n", encoding="utf-8"
        )
        return archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper", choices=("a", "b", "all"), default="all")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "dist")
    parser.add_argument(
        "--timestamp",
        default=None,
        help="UTC timestamp recorded in manifests; pass explicitly for reproducibility",
    )
    args = parser.parse_args(argv)

    head = ensure_clean_checkout(REPO_ROOT)
    environment = check_environment(REPO_ROOT)
    source_epoch = int(git("show", "-s", "--format=%ct", head, cwd=REPO_ROOT))
    args.output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="puckworks-release-worktree-") as tmp:
        worktree = Path(tmp) / "source"
        run(
            ["git", "worktree", "add", "--detach", str(worktree), head],
            cwd=REPO_ROOT,
        )
        try:
            for paper in papers_from_arg(args.paper):
                archive = prepare_one(
                    paper,
                    worktree=worktree,
                    head=head,
                    output_dir=args.output_dir,
                    timestamp=args.timestamp,
                    environment=environment,
                    source_epoch=source_epoch,
                )
                print(archive)
                print(archive.with_suffix(archive.suffix + ".sha256"))
        finally:
            with contextlib.suppress(Exception):
                run(
                    ["git", "worktree", "remove", "--force", str(worktree)],
                    cwd=REPO_ROOT,
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Paper 3 build/verify — extends the existing release model to the registry resource (WP3.2).

`verify` is CI-runnable: it fails when the generated registry artifacts are stale/hand-edited
or the registry schema is invalid, and it lists the Paper 3 bundle contents (checking each
exists). It does NOT tag, deposit to Zenodo, or mint a DOI — those remain explicit human
actions, consistent with the existing release runbook.

`release` is the strict gate: it additionally requires a clean tree and proves FRESHNESS BY
RECOMPUTATION -- every generated artifact regenerates byte-identically and the deterministic
archive builds to the same hash twice. It deliberately does NOT require
`bundle.source_commit == HEAD`.

That choice is scoped, not a claim that commit-equality is impossible. IN-TREE it is
unsatisfiable: committing a bundle advances HEAD, so a committed bundle always reads one commit
stale. OUT-OF-TREE it is achievable, and `tools/prepare_paper_release.py` already achieves it for
Papers 1 and 2 -- detached worktree at HEAD, generated files staged externally, then overlaid onto
`git archive HEAD`, so inside the release archive the source commit and `manifest.source_commit`
agree. Paper 3 is not yet wired into that tool, so this gate asserts the in-tree property
instead: "regenerates identically on a clean tree", which is what a reader of the repository
needs (the same distinction drawn between `generated_from_commit` and
`last_verified_against_commit` in the public claim schema).

CLI:  python -m puckworks.paper3.build verify | list-bundle | release
"""
import json
import sys
from pathlib import Path

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import registry_artifacts as gen

REPO_ROOT = Path(__file__).resolve().parents[2]

# files a Paper 3 resource bundle should include (relative to repo root). Generated artifacts
# are listed via the generator so the two never drift.
_BUNDLE_STATIC = [
    "docs/PAPER_3_PUCKWORKS_DRAFT.md",
    "docs/CLAIM_OWNERSHIP.md",
    "puckworks/data/MANIFEST.csv",
    "puckworks/data/visualizer/PROVENANCE.md",
    "puckworks/data/paper_b_evidence_matrix.csv",
    "puckworks/data/paper_b_evidence_dictionary.csv",
]


def bundle_contents(root=REPO_ROOT):
    """Repo-relative files the Paper 3 bundle should contain.

    Delegates to the ARCHIVE's member list so the two cannot disagree. They previously did: this
    function listed 14 files while the archive shipped 148, and neither figures nor their source
    data appeared in either. `_BUNDLE_STATIC` is retained only as a floor -- every path in it must
    still be present -- so a regression that dropped the manuscript would be caught here even if
    the archive's globbing changed."""
    from puckworks.paper3 import archive as A

    members = {rel for rel, _role, _redist in A._static_members(Path(root))}
    missing_floor = [f for f in _BUNDLE_STATIC if f not in members]
    if missing_floor:
        raise AssertionError("archive no longer includes required bundle files: %s"
                             % missing_floor)
    return sorted(members)


def verify(root=REPO_ROOT):
    """Return a report dict {ok, problems, warnings, bundle_missing}. `ok` is False on any
    hard problem: stale generated artifacts, an invalid registry enum, or a missing bundle
    file. Unclassified evidence_strength is a WARNING (known card-driven debt), not a failure."""
    root = Path(root)
    problems, warnings = [], []

    stale = gen.verify(root)
    if stale:
        problems.append("stale_generated_artifacts:%s" % ",".join(stale))

    for p in R.validate_registry():
        (warnings if "unclassified evidence_strength" in p else problems).append(p)

    bundle_missing = [f for f in bundle_contents() if not (root / f).exists()]
    if bundle_missing:
        problems.append("bundle_missing:%s" % ",".join(bundle_missing))

    return {
        "ok": not problems,
        "n_components": len(R.components()),
        "problems": problems,
        "warnings": warnings,
        "bundle_files": bundle_contents(),
        "bundle_missing": bundle_missing,
    }


def _git(*args, root=REPO_ROOT):
    import subprocess
    try:
        return subprocess.run(["git", *args], cwd=str(root), capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:                                        # noqa: BLE001
        return "UNKNOWN"


def _recomputation_problems(root=REPO_ROOT):
    """Every generated artifact must regenerate byte-identically. This is what freshness MEANS
    here: not that a stored commit equals HEAD, but that nothing in the release was hand-edited
    after it was generated."""
    problems = []

    stale = gen.verify(root)
    if stale:
        problems.append("generated_artifacts_stale:%s" % ",".join(stale))

    from puckworks.paper3 import appendix_b, named_shot_scorecard
    if appendix_b.verify():
        problems.append("appendix_b_stale")
    if named_shot_scorecard.verify():
        problems.append("named_shot_scorecard_stale")

    # figure source data must equal the producers it claims to come from
    try:
        import tempfile

        from puckworks import figures_paper3 as F
        with tempfile.TemporaryDirectory() as tmp:
            fresh = {Path(p).name: Path(p).read_bytes()
                     for p in F.export_source_data(outdir=tmp)}
        committed_dir = Path(root) / "docs/figures/paper3/source_data"
        for name, data in fresh.items():
            path = committed_dir / name
            if not path.exists():
                problems.append("figure_source_data_missing:%s" % name)
            elif path.read_bytes() != data:
                problems.append("figure_source_data_stale:%s" % name)
    except ModuleNotFoundError:
        problems.append("figures_extra_missing: cannot verify figure source data "
                        "(install the [figures] extra)")
    return problems


def release(root=REPO_ROOT, out=None):
    """Strict release gate. Returns a report; `ok` is False on any problem.

    Checks, in order: the standard verify; a CLEAN working tree; freshness by recomputation; and
    that the deterministic archive builds to the SAME hash twice, which is the property that makes
    the archive citable at all."""
    from puckworks.paper3 import archive as A

    root = Path(root)
    rep = verify(root)
    problems = list(rep["problems"])

    # ONE definition of "dirty", shared with the archive (see `archive.RELEASE_MANIFEST`). It was
    # duplicated once, the duplicate was missed, and the second consecutive `release` still died
    # inside create_archive with an unhandled RuntimeError.
    dirty = A.dirty_paths(root)
    if dirty:
        problems.append("tree_dirty:%d_paths" % len(dirty))

    problems += _recomputation_problems(root)

    archive_sha = None
    if not problems:
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a1.tar.gz"
            b = Path(tmp) / "a2.tar.gz"
            try:
                r1 = A.create_archive(a, root=root, dirty_ok=False)
                r2 = A.create_archive(b, root=root, dirty_ok=False)
            except RuntimeError as exc:
                # A gate must REPORT a refusal, not die with a traceback: the caller has asked
                # "is this releasable?" and deserves the answer in the manifest either way.
                problems.append("archive_refused:%s" % exc)
            else:
                if r1["archive_sha256"] != r2["archive_sha256"]:
                    problems.append("archive_not_deterministic")
                archive_sha = r1["archive_sha256"]
                # and it must verify from the tarball alone, without this checkout
                for bad in A.verify_archive(a):
                    problems.append("archive_verify:%s" % bad)

    head = _git("rev-parse", "HEAD", root=root)
    report = dict(
        paper="3", ok=not problems, problems=problems, warnings=rep["warnings"],
        commit=head, tree_clean=not dirty,
        freshness="by recomputation (generated artifacts regenerate identically)",
        archive_sha256=archive_sha, n_components=rep["n_components"],
        n_bundle_files=len(rep["bundle_files"]),
        tag_hint="git tag -a paper-3-v1.0.0-rc.1 -m 'Paper 3 release candidate'",
    )
    if out:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv=None):   # pragma: no cover
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "verify"
    if cmd in ("bundle", "list-bundle"):
        if cmd == "bundle":
            print("NOTE: `bundle` only LISTS paths and is renamed to `list-bundle`. For the real "
                  "immutable archive use `python -m puckworks.paper3.archive create-archive`.",
                  file=sys.stderr)
        print(json.dumps(bundle_contents(), indent=2))
        return 0
    if cmd == "release":
        rep = release(out=str(REPO_ROOT / "docs/reproducibility/paper3_release_manifest.json"))
        print(json.dumps(rep, indent=2))
        return 0 if rep["ok"] else 1
    rep = verify()
    print(json.dumps(rep, indent=2))
    if rep["warnings"]:
        print("WARNINGS: %d unclassified-evidence components (card-driven debt)"
              % len(rep["warnings"]), file=sys.stderr)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())

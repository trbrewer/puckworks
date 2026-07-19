"""P1.4 — inspect built distributions (wheel + sdist) for the file inventory users receive.

    python tools/packaging_check.py dist

Fails (exit 1) if any distribution contains a private/raw corpus path, or is missing a required
package-data file. Importable as a function for the packaging test.
"""
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

# substrings that must NEVER appear in a distribution (private/raw visualizer corpus, logs)
PRIVATE_SUBSTRINGS = ("visualizer/raw", "visualizer/normalized", "visualizer/crawl",
                      "aggregate_stats", ".log")
# package-data that MUST be present for the installed package to work
REQUIRED_SUFFIXES = ("puckworks/data/MANIFEST.csv",
                     "puckworks/data/cameron2020/fig5_grind_deviation.csv",
                     "puckworks/data/visualizer/PROVENANCE.md")

# No product runtime fixture ships in the contract-only PR 1A. Any file under puckworks/data/product/
# would be an unreviewed product-data leak until PR 1B lands an approved fixture and re-adds an
# explicit allowlist.
PRODUCT_DATA_PREFIX = "puckworks/data/product/"
PRODUCT_DATA_ALLOWLIST: set = set()


def _members(path: Path):
    if path.suffix == ".whl" or path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            return z.namelist()
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path) as t:
            return t.getnames()
    return []


def _file_members(path: Path):
    """Only regular-file members (directory entries excluded), for git-tracking comparison."""
    if path.suffix in (".whl", ".zip"):
        with zipfile.ZipFile(path) as z:
            return [i.filename for i in z.infolist() if not i.is_dir()]
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path) as t:
            return [m.name for m in t.getmembers() if m.isfile()]
    return []


# source-tree directories that are NOT part of the installable package and must never ship in a
# distribution: docs (which contain the model cards), the dev-only Streamlit apps, notebooks, and any
# transient staging tree left by the batch runner.
FORBIDDEN_TREE_PREFIXES = ("docs/", "apps/", "notebooks/")
FORBIDDEN_TREE_SUBSTRINGS = ("/cards/", ".staging/", "/out/lab")


def check_distribution(path: Path):
    names = _members(path)
    problems = []
    for n in names:
        low = n.lower()
        if any(s in low for s in PRIVATE_SUBSTRINGS):
            problems.append("%s: PRIVATE path shipped: %s" % (path.name, n))
        norm = _normalize_member(n)
        if any(norm.startswith(p) for p in FORBIDDEN_TREE_PREFIXES) or \
                any(s in norm for s in FORBIDDEN_TREE_SUBSTRINGS):
            problems.append("%s: NON-PACKAGE tree shipped: %s" % (path.name, norm))
    for suf in REQUIRED_SUFFIXES:
        if not any(n.endswith(suf) for n in names):
            problems.append("%s: MISSING required package data: %s" % (path.name, suf))
    # positive allowlist for product data: no unreviewed member may enter puckworks/data/product/
    for n in names:
        idx = n.find(PRODUCT_DATA_PREFIX)
        if idx == -1:
            continue
        rel = n[idx:]
        if rel.endswith("/") or "__pycache__" in rel or rel.rstrip("/") == PRODUCT_DATA_PREFIX.rstrip("/"):
            continue
        if rel not in PRODUCT_DATA_ALLOWLIST:
            problems.append("%s: UNREVIEWED product-data file: %s" % (path.name, rel))
    return problems


def _normalize_member(name):
    """Map a distribution member to its repo-relative path. sdist members are prefixed with
    ``puckworks-<version>/``; wheel members are already repo-relative for the package tree."""
    if name.startswith("puckworks/"):
        return name
    head, _, tail = name.partition("/")
    if head.startswith("puckworks-") and tail:      # sdist container prefix
        return tail
    return name


def git_tracked_paths(repo_root):
    out = subprocess.check_output(["git", "-C", str(repo_root), "ls-files"], text=True)
    return set(out.splitlines())


def check_git_tracked(path, repo_root):
    """Every shipped file under the ``puckworks/`` package tree MUST be git-tracked. This catches a
    local build that swept a gitignored/untracked raw-data file off disk into the distribution (the
    class of leak that the substring blocklist cannot enumerate)."""
    tracked = git_tracked_paths(repo_root)
    problems = []
    for n in _file_members(path):
        norm = _normalize_member(n)
        if not norm.startswith("puckworks/") or norm.endswith("/"):
            continue                                 # only guard the package tree
        if "/__pycache__/" in norm or norm.endswith(".pyc"):
            continue
        if ".egg-info/" in norm or ".dist-info/" in norm:
            continue                                 # packaging-generated metadata
        if norm not in tracked:
            problems.append("%s: UNTRACKED file shipped (not in git): %s" % (path.name, norm))
    return problems


def check_distributions(dist_dir, repo_root=None):
    dist = Path(dist_dir)
    dists = sorted(list(dist.glob("*.whl")) + list(dist.glob("*.tar.gz")))
    if not dists:
        return ["no distributions found in %s" % dist_dir]
    problems = []
    for d in dists:
        problems += check_distribution(d)
        if repo_root is not None:
            problems += check_git_tracked(d, repo_root)
    return problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    dist_dir = argv[0] if argv else "dist"
    # Repo root = the git work tree containing this tool; enables the git-tracked guard.
    try:
        repo_root = subprocess.check_output(
            ["git", "-C", str(Path(__file__).resolve().parent), "rev-parse", "--show-toplevel"],
            text=True).strip()
    except Exception:
        repo_root = None
    problems = check_distributions(dist_dir, repo_root=repo_root)
    if problems:
        print("PACKAGING CHECK FAILED (%d):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("distributions clean: no private paths, no untracked files, all required data present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

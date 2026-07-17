"""P1.4 — inspect built distributions (wheel + sdist) for the file inventory users receive.

    python tools/packaging_check.py dist

Fails (exit 1) if any distribution contains a private/raw corpus path, or is missing a required
package-data file. Importable as a function for the packaging test.
"""
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
                     "puckworks/data/visualizer/PROVENANCE.md",
                     # product fixture + manifest (issue #32 PR 1) — the bundled single-shot
                     "puckworks/data/product/waszkiewicz2025_9bar_single_shot.csv",
                     "puckworks/data/product/waszkiewicz2025_9bar_single_shot.manifest.json")


def _members(path: Path):
    if path.suffix == ".whl" or path.suffix == ".zip":
        with zipfile.ZipFile(path) as z:
            return z.namelist()
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path) as t:
            return t.getnames()
    return []


def check_distribution(path: Path):
    names = _members(path)
    problems = []
    for n in names:
        low = n.lower()
        if any(s in low for s in PRIVATE_SUBSTRINGS):
            problems.append("%s: PRIVATE path shipped: %s" % (path.name, n))
    for suf in REQUIRED_SUFFIXES:
        if not any(n.endswith(suf) for n in names):
            problems.append("%s: MISSING required package data: %s" % (path.name, suf))
    return problems


def check_distributions(dist_dir):
    dist = Path(dist_dir)
    dists = sorted(list(dist.glob("*.whl")) + list(dist.glob("*.tar.gz")))
    if not dists:
        return ["no distributions found in %s" % dist_dir]
    problems = []
    for d in dists:
        problems += check_distribution(d)
    return problems


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    dist_dir = argv[0] if argv else "dist"
    problems = check_distributions(dist_dir)
    if problems:
        print("PACKAGING CHECK FAILED (%d):" % len(problems))
        for p in problems:
            print("  -", p)
        return 1
    print("distributions clean: no private paths, all required data present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

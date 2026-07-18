"""P1.4 — the distribution inventory guard. Fast/offline: exercises the packaging checker logic
and guards the pyproject exclude-config so the private-corpus exclusion cannot silently regress.
The full build + clean-room install runs in the `packaging` CI job.
"""
import sys
import zipfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "tools"))
import packaging_check as P   # noqa: E402


def _fake_dist(tmp_path, names):
    p = tmp_path / "puckworks-0.0.0-py3-none-any.whl"
    with zipfile.ZipFile(p, "w") as z:
        for n in names:
            z.writestr(n, b"x")
    return p


def test_checker_flags_private_paths(tmp_path):
    d = _fake_dist(tmp_path, ["puckworks/__init__.py",
                              "puckworks/data/visualizer/raw/_index.csv"])   # private!
    problems = P.check_distribution(d)
    assert any("PRIVATE path shipped" in x for x in problems)


def test_checker_flags_missing_required_data(tmp_path):
    d = _fake_dist(tmp_path, ["puckworks/__init__.py"])   # no MANIFEST.csv etc.
    problems = P.check_distribution(d)
    assert any("MISSING required package data" in x for x in problems)


def test_checker_passes_clean_distribution(tmp_path):
    names = ["puckworks/__init__.py"] + list(P.REQUIRED_SUFFIXES)
    assert P.check_distribution(_fake_dist(tmp_path, names)) == []


def test_no_distributions_is_a_problem(tmp_path):
    assert P.check_distributions(tmp_path)                 # empty dir -> flagged


def test_pyproject_excludes_the_private_corpus():
    txt = (_ROOT / "pyproject.toml").read_text()
    assert "[tool.setuptools.exclude-package-data]" in txt
    for pat in ("visualizer/raw", "visualizer/crawl", "aggregate_stats"):
        assert pat in txt, "exclude-package-data no longer strips %r from the distribution" % pat
    # space-named pocketscience raw files can't be excluded via package-data; the guard covers them
    assert "pocketscience2024" in txt and "check_git_tracked" in txt, (
        "pyproject must document the git-tracked guard as the backstop for space-named raw data")


def test_git_tracked_guard_is_wired_into_the_checker():
    # the main packaging check must exercise check_git_tracked (not just the substring blocklist)
    assert hasattr(P, "check_git_tracked")
    src = (_ROOT / "tools" / "packaging_check.py").read_text()
    assert "check_git_tracked" in src and "repo_root" in src


def test_git_tracked_guard_flags_an_untracked_data_file(tmp_path):
    # A distribution that shipped a gitignored/untracked data file must be flagged. Use a path that
    # exists in the tree but is gitignored (a pocketscience raw export) so it is genuinely untracked.
    d = _fake_dist(tmp_path, [
        "puckworks/__init__.py",
        "puckworks/data/pocketscience2024/Espresso water flow experiment - LRR.csv",  # gitignored!
    ])
    problems = P.check_git_tracked(d, _ROOT)
    assert any("UNTRACKED file shipped" in x for x in problems)


def test_git_tracked_guard_passes_tracked_only(tmp_path):
    d = _fake_dist(tmp_path, [
        "puckworks/__init__.py",
        "puckworks/data/pocketscience2024/lrr_scalars.csv",   # git-tracked
    ])
    assert P.check_git_tracked(d, _ROOT) == []


def test_git_tracked_guard_normalizes_sdist_prefix(tmp_path):
    # sdist members carry a puckworks-<ver>/ container prefix; the guard must see through it.
    p = tmp_path / "puckworks-0.0.0.tar.gz"
    import tarfile, io
    with tarfile.open(p, "w:gz") as t:
        data = b"x"
        for name in ("puckworks-0.0.0/puckworks/__init__.py",
                     "puckworks-0.0.0/puckworks/data/pocketscience2024/Espresso water flow experiment - VST18.csv"):
            info = tarfile.TarInfo(name); info.size = len(data)
            t.addfile(info, io.BytesIO(data))
    problems = P.check_git_tracked(p, _ROOT)
    assert any("UNTRACKED file shipped" in x and "VST18" in x for x in problems)

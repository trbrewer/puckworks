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


def _clean_names():
    return (["puckworks/__init__.py"] + list(P.REQUIRED_SUFFIXES)
            + ["puckworks-0.0.0.dist-info/licenses/" + b for b in P.REQUIRED_LICENSE_BASENAMES])


def test_checker_passes_clean_distribution(tmp_path):
    assert P.check_distribution(_fake_dist(tmp_path, _clean_names())) == []


def test_checker_flags_a_missing_third_party_notice(tmp_path):
    # #73: some shipped material (Grudeva code + derived data) is NOT under the repo's MIT licence;
    # dropping THIRD_PARTY_NOTICES.md would silently present it as MIT.
    names = [n for n in _clean_names() if not n.endswith("THIRD_PARTY_NOTICES.md")]
    problems = P.check_distribution(_fake_dist(tmp_path, names))
    assert any("MISSING required licence/notice file" in x and "THIRD_PARTY_NOTICES.md" in x
               for x in problems)


def test_checker_flags_a_missing_license(tmp_path):
    names = [n for n in _clean_names() if not n.endswith("/LICENSE")]
    problems = P.check_distribution(_fake_dist(tmp_path, names))
    assert any("MISSING required licence/notice file" in x and "LICENSE" in x for x in problems)


def test_pyproject_ships_the_third_party_notice_in_both_artifacts():
    # the packaging CONFIG, not just the checker: setuptools license-files puts these in the wheel's
    # dist-info/licenses/ and at the sdist root. A regression here is how the notice goes missing.
    txt = (_ROOT / "pyproject.toml").read_text()
    assert "license-files" in txt and "THIRD_PARTY_NOTICES.md" in txt and '"LICENSE"' in txt
    notice = (_ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "Dr. Yoana Grudeva" in notice and "2026-08-14" in notice
    assert "puckworks/models/grudeva2025/reduced.py" in notice
    assert "exp13_per_vial_stats.csv" in notice
    assert "@" not in notice, "the shipped notice must carry no email address"


def test_no_distributions_is_a_problem(tmp_path):
    assert P.check_distributions(tmp_path)                 # empty dir -> flagged


def test_checker_flags_non_package_trees(tmp_path):
    # docs (incl. the model cards), dev apps, notebooks, and any staging tree must never ship
    for leak in ("docs/cards/cameron2020.md", "apps/lab_app.py", "notebooks/x.ipynb",
                 "out/lab.staging/guided_pull_lab.json"):
        d = _fake_dist(tmp_path, ["puckworks/__init__.py", *P.REQUIRED_SUFFIXES, leak])
        problems = P.check_distribution(d)
        assert any("NON-PACKAGE tree shipped" in x for x in problems), leak


def test_checker_flags_non_package_tree_in_sdist_prefix(tmp_path):
    import tarfile
    import io
    p = tmp_path / "puckworks-0.0.0.tar.gz"
    with tarfile.open(p, "w:gz") as t:
        for name in ("puckworks-0.0.0/puckworks/__init__.py",
                     "puckworks-0.0.0/docs/cards/foster2025.md"):   # a card leaked into the sdist
            info = tarfile.TarInfo(name); info.size = 1
            t.addfile(info, io.BytesIO(b"x"))
    assert any("NON-PACKAGE tree shipped" in x and "docs/cards" in x
               for x in P.check_distribution(p))


def test_clean_distribution_with_tests_and_top_level_files_passes(tmp_path):
    # a legitimate dist (package tree + required data + tests + top-level metadata) is NOT flagged
    names = ["puckworks/__init__.py", "tests/test_x.py", "README.md", "pyproject.toml",
             *P.REQUIRED_SUFFIXES, *P.REQUIRED_LICENSE_BASENAMES]
    assert P.check_distribution(_fake_dist(tmp_path, names)) == []


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

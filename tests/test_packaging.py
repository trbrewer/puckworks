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

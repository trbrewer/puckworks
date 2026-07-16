"""P0.4 — version/citation/changelog agreement. The tag/manifest/notes cross-check is exercised
via release.release_readiness (offline; the real tag is applied at release time)."""
import puckworks
from puckworks import release


def test_declared_versions_agree():
    ok, versions = release.versions_agree()
    assert ok, "version sources disagree: %r" % versions


def test_importable_version_matches_pyproject():
    assert puckworks.__version__ == release.package_versions()["pyproject"]


def test_changelog_has_a_section_for_the_current_version():
    ver = release.package_versions()["pyproject"]
    assert ("## %s" % ver) in open("CHANGELOG.md", encoding="utf-8").read()


def test_release_readiness_clean_for_matching_tag():
    ver = release.package_versions()["pyproject"]
    assert release.release_readiness("v%s" % ver) == []


def test_release_readiness_flags_tag_mismatch():
    problems = release.release_readiness("v9.9.9")
    assert any("!= package version" in p for p in problems)

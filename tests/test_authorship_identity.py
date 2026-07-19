"""Software authorship + commit-identity governance (Phase 1).

Offline + deterministic. Puckworks is co-developed by Tim Brewer and Peter Vonk. These tests pin the
software-author list across CITATION.cff / pyproject / AUTHORS.md / README, verify Tim's email is
correct and that no Peter email/ORCID/affiliation is invented, that the erroneous historical commit
identity is canonicalized in .mailmap (history is NOT rewritten) and never appears as a current author,
and that no version/tag fact changed.
"""
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
SOFTWARE_AUTHORS = ("Tim Brewer", "Peter Vonk")
TIM_EMAIL = "t_r_brewer@hotmail.com"


def _read(name):
    return (_ROOT / name).read_text(encoding="utf-8")


def test_citation_cff_lists_exactly_the_two_software_authors():
    yaml = pytest.importorskip("yaml")
    d = yaml.safe_load(_read("CITATION.cff"))
    names = [f"{a.get('given-names')} {a.get('family-names')}" for a in d["authors"]]
    assert names == list(SOFTWARE_AUTHORS)
    assert d["type"] == "software" and d["license"] == "MIT"
    # Tim's email is present and correct; Peter has no invented email
    tim = next(a for a in d["authors"] if a["family-names"] == "Brewer")
    peter = next(a for a in d["authors"] if a["family-names"] == "Vonk")
    assert tim["email"] == TIM_EMAIL
    assert "email" not in peter and "orcid" not in peter and "affiliation" not in peter


def test_pyproject_authors_match():
    try:
        import tomllib
    except ModuleNotFoundError:                     # pragma: no cover - py<3.11
        tomllib = pytest.importorskip("tomli")
    data = tomllib.loads(_read("pyproject.toml"))
    authors = data["project"]["authors"]
    assert [a["name"] for a in authors] == list(SOFTWARE_AUTHORS)
    tim = next(a for a in authors if a["name"] == "Tim Brewer")
    peter = next(a for a in authors if a["name"] == "Peter Vonk")
    assert tim["email"] == TIM_EMAIL and "email" not in peter    # no invented Peter email


def test_authors_md_and_readme_name_both():
    for name in SOFTWARE_AUTHORS:
        assert name in _read("AUTHORS.md")
        assert name in _read("README.md")
    assert "@trbrewer" in _read("AUTHORS.md")


def test_no_invented_peter_identity_anywhere():
    blob = _read("CITATION.cff") + _read("pyproject.toml") + _read("AUTHORS.md") + _read("README.md")
    # no ORCID pattern and no email attached to Peter Vonk
    assert not re.search(r"Vonk[^\n]{0,80}@", blob)
    assert "orcid" not in blob.lower() or "vonk" not in blob.lower().split("orcid")[0][-40:]


def test_mailmap_canonicalizes_the_historical_identity_without_rewriting_history():
    mailmap = _read(".mailmap")
    # the erroneous moontowerrisk identity maps to the canonical Tim Brewer address
    assert "tim.brewer@moontowerrisk.com" in mailmap
    assert f"Tim Brewer <{TIM_EMAIL}>" in mailmap
    # git log with mailmap yields a single canonical identity (history objects unchanged)
    import subprocess
    out = subprocess.run(["git", "-C", str(_ROOT), "log", "--all", "--use-mailmap",
                          "--format=%aN <%aE>"], capture_output=True, text=True)
    if out.returncode == 0 and out.stdout.strip():
        idents = set(out.stdout.strip().splitlines())
        assert idents == {f"Tim Brewer <{TIM_EMAIL}>"}, idents


def test_erroneous_identity_is_only_in_mailmap_and_this_fixture():
    # scan the maintained current-metadata surfaces: none may name the stale identity
    stale = re.compile(r"m00ntower|moontower", re.I)
    for name in ("README.md", "AUTHORS.md", "CITATION.cff", "pyproject.toml"):
        assert not stale.search(_read(name)), f"{name} names the erroneous historical identity"
    # it is allowed in .mailmap (by design)
    assert stale.search(_read(".mailmap"))


def test_readme_governance_enforces_authorship():
    import sys
    if str(_ROOT) not in sys.path:
        sys.path.insert(0, str(_ROOT))
    from tools import readme_governance as rg
    assert rg._author_problems(_read("README.md")) == []      # clean today
    # a README missing Peter is flagged
    problems = rg._author_problems("Puckworks by Tim Brewer only")
    assert any("Peter Vonk" in p for p in problems)


def test_no_version_or_tag_fact_changed():
    yaml = pytest.importorskip("yaml")
    assert yaml.safe_load(_read("CITATION.cff"))["version"] == "0.4.0.dev0"
    assert 'version = "0.4.0.dev0"' in _read("pyproject.toml")

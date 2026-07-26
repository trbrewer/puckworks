"""Software authorship + commit-identity governance (Phase 1).

Offline + deterministic. Puckworks is co-developed by Tim Brewer and Peter Vonk. These tests pin the
software-author list across CITATION.cff / pyproject / AUTHORS.md / README, verify Tim's email is
correct and that no Peter email/ORCID/affiliation is invented, that .mailmap actually canonicalizes
the erroneous historical commit identities (history is NOT rewritten) and that every human author on
the project's own history is the canonical one, and that no version/tag fact changed.

Commit-identity scope (2026-07-25): the mailmap mapping is verified FUNCTIONALLY with
`git check-mailmap` rather than by inspecting mailmapped log output — the erroneous address appears
nowhere in the raw history, so an absence assertion would pass against an empty .mailmap. The
authorship sweep is scoped to `main` (else HEAD), never `--all`, and excludes bots; see
`_project_history_ref` for why.
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


CANONICAL_IDENTITY = f"Tim Brewer <{TIM_EMAIL}>"
# Identities .mailmap must fold into CANONICAL_IDENTITY: the erroneous moontowerrisk address
# (m00ntower account) and the bare-username variant.
STALE_IDENTITIES = (
    "Tim Brewer <tim.brewer@moontowerrisk.com>",
    "trbrewer <t_r_brewer@hotmail.com>",
)


def _git(*args):
    import subprocess
    return subprocess.run(["git", "-C", str(_ROOT), *args], capture_output=True, text=True)


def _is_bot(identity):
    """GitHub bots author as `name[bot] <...>` (dependabot, renovate, github-actions)."""
    return identity.split(" <", 1)[0].endswith("[bot]")


def _project_history_ref():
    """The project's OWN history: `main` when resolvable, else HEAD.

    Deliberately NOT `--all`. `--all` scopes the check to whatever refs the local clone happens
    to hold, which is a property of fetch configuration, not of the project: a shallow CI checkout
    (`actions/checkout` defaults to fetch-depth 1) sees one ref, a developer's full clone sees every
    `origin/*` branch, and a pruned clone sees a third set. That made this guard pass in CI for the
    wrong reason while failing locally on unmerged `origin/dependabot/*` branches -- green exactly
    where it runs, red where it gates nothing. Do not reintroduce `--all`."""
    return "main" if _git("rev-parse", "--verify", "--quiet", "main").returncode == 0 else "HEAD"


def test_mailmap_actually_canonicalizes_every_stale_identity():
    """FUNCTIONAL check of the mapping, via `git check-mailmap` -- independent of whether any commit
    with a stale identity happens to exist.

    This matters: the moontowerrisk address appears NOWHERE in the raw history, so asserting its
    absence from mailmapped output would be vacuous (it would pass against an empty .mailmap). Asking
    git to resolve the identity tests the mechanism instead of relying on a commit to exercise it."""
    mailmap = _read(".mailmap")
    assert "tim.brewer@moontowerrisk.com" in mailmap
    assert CANONICAL_IDENTITY in mailmap
    for stale in STALE_IDENTITIES:
        out = _git("check-mailmap", stale)
        if out.returncode != 0:                     # no git / not a repo -> nothing to verify
            pytest.skip("git check-mailmap unavailable")
        assert out.stdout.strip() == CANONICAL_IDENTITY, (stale, out.stdout)
    # and the mapping is targeted, not a catch-all that rewrites unrelated people
    other = _git("check-mailmap", "Someone Else <nobody@example.com>")
    if other.returncode == 0:
        assert other.stdout.strip() == "Someone Else <nobody@example.com>"


def test_project_history_authors_are_the_canonical_identity():
    """Every HUMAN author on the project's own history resolves to the canonical identity.

    Scope is `main` (else HEAD), not `--all` -- see `_project_history_ref`. Bots are excluded by
    GitHub's `name[bot]` convention: a Dependabot or Actions commit is a CORRECT state of the world,
    not an authorship defect, so the old `== {Tim Brewer}` assertion was a stronger claim than the
    invariant being protected and broke on the first bot branch. Committers are not asserted here:
    GitHub web merges commit as `GitHub <noreply@github.com>` by design."""
    out = _git("log", _project_history_ref(), "--use-mailmap", "--format=%aN <%aE>")
    if out.returncode != 0 or not out.stdout.strip():
        pytest.skip("no git history available")
    humans = {i for i in out.stdout.strip().splitlines() if not _is_bot(i)}
    assert humans == {CANONICAL_IDENTITY}, humans


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

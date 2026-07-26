"""Guards on the three environment-lock artifacts.

Motivated by a real defect: the first transitive lock was compiled with a constraints
file living in a per-session scratch directory, so twelve lines of a *reproducibility* artifact
pointed at an absolute path that exists on exactly one machine. The lock installed fine, which is
precisely why nothing caught it -- a lock can be perfectly valid and still be unreproducible.

These tests assert the three properties that failure violated:
  1. no committed lock may reference a path outside the repository;
  2. the lock's own header must name a *committed* constraints file, so anyone can regenerate it;
  3. the pins must agree with the recorded producing environment (and with each other).
"""
import json
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]

PAPERS_LOCK = _ROOT / "docs/reproducibility/requirements-papers.lock"
PAPERS_CONSTRAINTS = _ROOT / "docs/reproducibility/constraints-papers.txt"
DIRECT_LOCK = _ROOT / "requirements-paper-release.lock"
FREEZE_LOCK = _ROOT / "docs/reproducibility/requirements.lock"
ENVIRONMENT = _ROOT / "docs/reproducibility/paper_release_environment.json"

_PIN = re.compile(r"^([A-Za-z0-9._-]+)==(\S+)\s*$", re.M)

#: Absolute-path shapes that must never appear in a committed lock. `file:///` is excluded here
#: because requirements.lock is a pip freeze that legitimately contains them -- it is handled
#: separately below, where it is asserted to be a record rather than a recipe.
_MACHINE_PATHS = ("/private/tmp/", "/tmp/claude-", "scratchpad", "/Users/", "/home/runner")


def _pins(path: Path) -> dict[str, str]:
    return {k.lower(): v for k, v in _PIN.findall(path.read_text(encoding="utf-8"))}


def test_every_lock_artifact_exists():
    for p in (PAPERS_LOCK, PAPERS_CONSTRAINTS, DIRECT_LOCK, FREEZE_LOCK, ENVIRONMENT):
        assert p.exists(), p


@pytest.mark.parametrize("path", [PAPERS_LOCK, PAPERS_CONSTRAINTS, DIRECT_LOCK],
                         ids=lambda p: p.name)
def test_no_lock_references_a_machine_specific_path(path):
    """THE BUG. A lock that names a scratch directory is not reproducible by anyone else."""
    text = path.read_text(encoding="utf-8")
    for needle in _MACHINE_PATHS:
        assert needle not in text, (
            f"{path.name} references «{needle}» -- a path outside the repository. "
            f"Recompile with the committed constraints file.")


def test_the_lock_names_a_committed_constraints_file():
    """Non-vacuity for the test above: absence of bad paths is not enough. The lock must positively
    point at something a reader actually has, or it is unregenerable in a different way."""
    text = PAPERS_LOCK.read_text(encoding="utf-8")
    assert "docs/reproducibility/constraints-papers.txt" in text, (
        "the lock no longer records which constraints produced it")
    referenced = re.findall(r"-c\s+(\S+)", text)
    assert referenced, "no constraint reference in the lock header"
    for rel in set(referenced):
        assert (_ROOT / rel).exists(), f"lock references {rel}, which is not committed"


def test_the_lock_is_transitive_not_just_direct():
    """The reason this lock exists at all: requirements-paper-release.lock is direct-only."""
    p3, direct = _pins(PAPERS_LOCK), _pins(DIRECT_LOCK)
    assert set(direct) <= set(p3), set(direct) - set(p3)
    assert len(p3) > len(direct) + 5, (
        f"the lock has {len(p3)} pins vs {len(direct)} direct -- it looks direct-only, "
        f"which defeats its purpose")
    for transitive in ("contourpy", "kiwisolver", "fonttools", "pillow"):
        assert transitive in p3, transitive


def test_the_locks_agree_with_the_recorded_producing_environment():
    """Three artifacts state the same versions; a silent disagreement would mean at least one
    describes an environment that never ran."""
    recorded = json.loads(ENVIRONMENT.read_text(encoding="utf-8"))["packages"]
    p3, direct, constraints = _pins(PAPERS_LOCK), _pins(DIRECT_LOCK), _pins(PAPERS_CONSTRAINTS)
    for name, version in recorded.items():
        assert direct.get(name) == version, (name, direct.get(name), version)
        assert p3.get(name) == version, (name, p3.get(name), version)
        assert constraints.get(name) == version, (name, constraints.get(name), version)


def test_the_freeze_lock_is_documented_as_a_record_not_a_recipe():
    """requirements.lock is a conda `pip freeze` full of file:/// build paths. It cannot be
    installed elsewhere, and REPRODUCIBILITY.md must say so rather than listing three locks as
    interchangeable."""
    freeze = FREEZE_LOCK.read_text(encoding="utf-8")
    assert "file:///" in freeze, (
        "requirements.lock no longer looks like a conda freeze -- re-check the guidance in "
        "REPRODUCIBILITY.md, which describes it as not installable")
    guidance = (_ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    assert "Which lock file to use" in guidance
    for name in ("requirements-paper-release.lock", "requirements-papers.lock",
                 "requirements.lock"):
        assert name in guidance, f"{name} is not distinguished in REPRODUCIBILITY.md"
    assert "not installable" in guidance or "**No**" in guidance


#: Every module that PRODUCES a committed manuscript artifact, for any of the three papers.
_PRODUCER_MODULES = (
    "puckworks/figures_paper_a.py",
    "puckworks/paper_a/build.py",
    "puckworks/paper_b2/build.py",
    "puckworks/figures_paper3.py",
    "puckworks/paper3/build.py",
    "puckworks/paper3/archive.py",
)

#: What the single lock actually covers. numpy/scipy are declared dependencies; matplotlib comes
#: from the `figures` extra the lock is compiled with.
_COVERED = {"numpy", "scipy", "matplotlib"}


def _third_party_imports(path: Path) -> set[str]:
    import ast
    import sys
    std = set(sys.stdlib_module_names)
    mods = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Import):
            mods.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods.add(node.module.split(".")[0])
    return {m for m in mods if m not in std and m not in ("puckworks", "tools")}


def test_one_lock_is_enough_because_all_three_papers_share_a_dependency_set():
    """The justification for having ONE lock rather than three identical ones. If any paper's
    producing pipeline grows a dependency the lock does not cover, this fails LOUDLY -- which is
    the whole point, because the alternative is a lock that quietly describes the wrong
    environment for one paper while remaining correct for the others."""
    for rel in _PRODUCER_MODULES:
        path = _ROOT / rel
        assert path.exists(), rel
        extra = _third_party_imports(path) - _COVERED
        assert not extra, (
            f"{rel} imports {sorted(extra)}, which requirements-papers.lock was not compiled to "
            f"cover. Either add it to the lock's extras or give that paper its own lock.")


def test_the_shared_lock_rationale_is_documented():
    """Non-vacuity: the test above only means something if a reader is told why one lock exists."""
    doc = (_ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    assert "Why there is one lock and not three" in doc
    for name in ("figures_paper_a", "paper_b.build", "figures_paper3"):
        assert name in doc, f"{name} is not named in the shared-lock rationale"

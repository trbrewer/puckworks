"""Paper 3 strict release gate and archive payload (release-unblock work).

The gate exists to make a tag meaningful. These tests hold the properties that make it so: the
bundle has ONE definition, the archive actually contains the paper's figures, freshness is defined
by recomputation rather than by an unsatisfiable commit-equality check, and the gate refuses a dirty
tree.
"""
import pathlib

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks.paper3 import archive as A
from puckworks.paper3 import build as B

_ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def members():
    return A._static_members(_ROOT)


def test_the_bundle_has_one_definition():
    """`build.bundle_contents()` used to list 14 files while the archive shipped 148. They now
    share a definition, so they cannot disagree again."""
    bundle = set(B.bundle_contents(_ROOT))
    archive = {rel for rel, _role, _redist in A._static_members(_ROOT)}
    assert bundle == archive


def test_the_required_floor_is_still_present(members):
    """A globbing change must not silently drop the manuscript."""
    present = {rel for rel, _r, _x in members}
    for required in B._BUNDLE_STATIC:
        assert required in present, required


def test_the_archive_ships_the_figures(members):
    """It previously shipped a manuscript with NO figures -- a reader could not check a panel."""
    roles = [r for _p, r, _x in members]
    assert roles.count("figure") >= 21, "figures missing from the archive payload"
    assert "figure_alt_text" in roles, "no text alternatives in the archive"
    assert roles.count("figure_source_data") >= 4, "figure source data missing"


def test_every_committed_figure_is_in_the_archive(members):
    present = {rel for rel, _r, _x in members}
    for p in sorted((_ROOT / "docs/figures/paper3").glob("*.png")):
        rel = p.relative_to(_ROOT).as_posix()
        assert rel in present, rel
        for ext in (".svg", ".pdf"):
            assert rel.replace(".png", ext) in present, rel.replace(".png", ext)


def test_the_archive_is_deterministic(tmp_path):
    """Two builds from the same commit must give the same hash, or the archive is not citable."""
    a = A.create_archive(tmp_path / "a.tar.gz", root=_ROOT, dirty_ok=True)
    b = A.create_archive(tmp_path / "b.tar.gz", root=_ROOT, dirty_ok=True)
    assert a["archive_sha256"] == b["archive_sha256"]


def test_the_archive_verifies_without_the_source_checkout(tmp_path):
    path = tmp_path / "a.tar.gz"
    A.create_archive(path, root=_ROOT, dirty_ok=True)
    problems = A.verify_archive(path)          # returns a LIST of problems; empty == clean
    assert problems == [], problems


def _fake_status(*lines):
    """Stand in for `git status --porcelain`, in its real two-column format."""
    return lambda *a, **k: "\n".join(lines) if a[0] == "status" else "abc"


def test_release_refuses_a_dirty_tree(monkeypatch):
    """The gate's whole purpose. Simulated rather than by dirtying the real tree."""
    monkeypatch.setattr(A, "_git", _fake_status(" M some/file.py"))
    monkeypatch.setattr(B, "_git", _fake_status(" M some/file.py"))
    rep = B.release(_ROOT)
    assert rep["ok"] is False
    assert any(p.startswith("tree_dirty") for p in rep["problems"]), rep["problems"]


def test_the_gate_does_not_count_its_own_report_as_a_dirty_tree(monkeypatch):
    """OBSERVED DEFECT, not a hypothetical: the CLI writes the release manifest into the tree, so
    running `release` twice in a row failed the second time. A gate that flips red purely because
    it ran is worse than useless -- it teaches you to ignore it."""
    monkeypatch.setattr(A, "_git", _fake_status("?? " + A.RELEASE_MANIFEST))
    assert A.dirty_paths(_ROOT) == []

    monkeypatch.setattr(A, "_git", _fake_status(" M " + A.RELEASE_MANIFEST))
    assert A.dirty_paths(_ROOT) == []


def test_the_archive_uses_the_same_definition_of_dirty_as_the_gate(monkeypatch):
    """SECOND SITE of the same defect. The first fix touched only build.release; create_archive
    kept its own independent `git status` check, so the second consecutive run still died -- with
    an unhandled RuntimeError rather than a reported problem. One definition, two callers."""
    import inspect
    src = inspect.getsource(A.create_archive)
    assert "dirty_paths(" in src, "create_archive re-implemented its own dirtiness check"
    assert "--porcelain" not in src, "create_archive still calls git status directly"
    assert "dirty_paths" in inspect.getsource(B.release)

    # ...and behaviourally: with only the manifest untracked, a strict archive build succeeds.
    monkeypatch.setattr(A, "_git", _fake_status("?? " + A.RELEASE_MANIFEST))
    assert A.dirty_paths(_ROOT) == []


def test_a_refused_archive_is_reported_not_raised(monkeypatch):
    """A gate asked 'is this releasable?' must answer in the manifest, not exit with a traceback."""
    monkeypatch.setattr(B, "_recomputation_problems", lambda root: [])
    monkeypatch.setattr(B, "verify", lambda root: dict(
        problems=[], warnings=[], n_components=0, bundle_files=[]))
    monkeypatch.setattr(A, "dirty_paths", lambda root=None: [])
    def _boom(*a, **k):
        raise RuntimeError("refusing to build a release archive on a DIRTY tree: x")
    monkeypatch.setattr(A, "create_archive", _boom)
    rep = B.release(_ROOT)
    assert rep["ok"] is False
    assert any(p.startswith("archive_refused:") for p in rep["problems"]), rep["problems"]


def test_the_exclusion_is_exactly_one_path_and_nothing_near_it(monkeypatch):
    """Non-vacuity for the tests above. An over-broad exclusion (a prefix or a directory) would
    silently stop the gate noticing hand-edited artifacts, which is the failure it exists to catch.
    Every neighbour of the manifest must still count as dirty."""
    near = [
        "docs/reproducibility/paper3_release_manifest.json.bak",
        "docs/reproducibility/paper_a_manifest.json",
        "docs/reproducibility/requirements-papers.lock",
        "docs/reproducibility/",
        "docs/PAPER_3_PUCKWORKS_DRAFT.md",
    ]
    for path in near:
        monkeypatch.setattr(A, "_git", _fake_status(" M " + path))
        assert A.dirty_paths(_ROOT) == [path], f"{path} was wrongly excluded"


def test_dirty_paths_parses_the_porcelain_shapes_git_actually_emits(monkeypatch):
    """A parser that mishandled renames or staged-and-modified entries would drop real dirt."""
    monkeypatch.setattr(A, "_git", _fake_status(
        "?? new/file.py", "MM staged/and/modified.py", "R  old/name.py -> new/name.py",
        " D deleted.py", "A  " + A.RELEASE_MANIFEST))
    assert A.dirty_paths(_ROOT) == [
        "new/file.py", "staged/and/modified.py", "new/name.py", "deleted.py"]


def test_the_release_manifest_is_not_itself_an_archive_member():
    """If it were, the archive hash would depend on the report of the run that produced it, which
    is circular. It is a report ABOUT a release, not part of one."""
    members = [m if isinstance(m, str) else str(m) for m in A._static_members(_ROOT)]
    assert not any(A.RELEASE_MANIFEST in m for m in members), (
        "the release manifest is inside the archive -- the hash is now self-referential")


def test_freshness_is_defined_by_recomputation_not_commit_equality():
    """The design decision, pinned. Commit equality is unsatisfiable IN-TREE because committing the
    bundle advances HEAD; recomputation tests the property a reader of the repository needs.

    The scoping matters and is asserted: commit-equality is achievable out-of-tree, and
    `tools/prepare_paper_release.py` already achieves it for Papers 1 and 2. An unqualified
    "unsatisfiable" here would be false, so the docstring must name the in-tree scope and must not
    claim impossibility in general."""
    rep = B.release(_ROOT)
    assert "recomputation" in rep["freshness"]
    src = (_ROOT / "puckworks/paper3/build.py").read_text(encoding="utf-8")
    flat = " ".join(src.split())          # reflow-insensitive: line wrapping must not break this
    assert "IN-TREE it is unsatisfiable" in flat, "the in-tree scope is no longer stated"
    assert "prepare_paper_release" in src, "the out-of-tree counterexample is no longer named"
    assert "structurally unsatisfiable" not in src, (
        "unqualified 'structurally unsatisfiable' is false -- "
        "tools/prepare_paper_release.py satisfies commit-equality out-of-tree")


def test_the_out_of_tree_release_tool_really_does_not_cover_paper_3():
    """Guards the caveat above: if Paper 3 is later wired into prepare_paper_release.py, the
    docstring and REPRODUCIBILITY.md both become stale and must be revisited."""
    tool = _ROOT / "tools/prepare_paper_release.py"
    src = tool.read_text(encoding="utf-8")
    assert "def build_paper_a" in src and "def build_paper_b" in src, (
        "the tool's shape changed -- re-derive which papers it covers")
    assert "def build_paper3" not in src and "def build_paper_3" not in src, (
        "Paper 3 now has an out-of-tree builder: update paper3/build.py and REPRODUCIBILITY.md, "
        "which both state that it does not")


def test_recomputation_check_covers_every_generated_surface():
    """A freshness check that omitted a generated artifact would certify a stale release."""
    src = (_ROOT / "puckworks/paper3/build.py").read_text(encoding="utf-8")
    for surface in ("gen.verify", "appendix_b.verify", "named_shot_scorecard.verify",
                    "export_source_data"):
        assert surface in src, surface


def test_recomputation_finds_nothing_stale_right_now():
    assert B._recomputation_problems(_ROOT) == []


def test_the_lock_pins_the_producing_environment():
    """A lock resolved without constraints would name matplotlib 3.11.1 while the figures were
    drawn with 3.11.0 -- a different environment from the one that ran.

    Only packages that are actually importable here are compared. matplotlib comes from the
    `figures` extra, which the quick and min-deps CI lanes deliberately do NOT install; a bare
    `import matplotlib` made this test fail in both of them while passing locally.
    """
    import importlib

    lock = (_ROOT / "docs/reproducibility/requirements-papers.lock").read_text(encoding="utf-8")
    checked = []
    for name in ("numpy", "scipy", "matplotlib"):
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError:
            continue                      # optional extra absent in this lane
        checked.append(name)
        assert "%s==%s" % (name, mod.__version__) in lock, name
    assert {"numpy", "scipy"} <= set(checked), (
        "numpy and scipy are hard dependencies -- if they are missing the environment is broken, "
        "not merely missing an extra")


def test_reproducibility_doc_states_what_is_not_reproducible():
    """A reproducibility document that lists only successes is not useful."""
    text = (_ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    assert "What is NOT yet reproducible" in text
    for gap in ("No archival DOI", "No independent reproduction", "Correctness is not certified"):
        assert gap in text, gap


def test_the_archive_hash_depends_on_the_commit_not_only_the_contents(tmp_path, monkeypatch):
    """A non-obvious reproducibility fact, verified rather than assumed: member mtimes come from
    the commit's committer time, so the SAME files at a different commit hash differently. Anyone
    trying to reproduce a published hash must build from the same commit (or set
    SOURCE_DATE_EPOCH). REPRODUCIBILITY.md must keep saying so."""
    a = A.create_archive(tmp_path / "a.tar.gz", root=_ROOT, dirty_ok=True)["archive_sha256"]
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1000000000")
    b = A.create_archive(tmp_path / "b.tar.gz", root=_ROOT, dirty_ok=True)["archive_sha256"]
    assert a != b, "the archive hash is independent of the epoch -- the documented caveat is wrong"

    # ...and pinning the epoch makes it reproducible again, which is the actual escape hatch.
    c = A.create_archive(tmp_path / "c.tar.gz", root=_ROOT, dirty_ok=True)["archive_sha256"]
    assert b == c

    doc = (_ROOT / "REPRODUCIBILITY.md").read_text(encoding="utf-8")
    assert "SOURCE_DATE_EPOCH" in doc and "different sha256" in doc, (
        "the commit-dependence of the hash is no longer documented")


def test_the_suggested_tag_actually_triggers_the_release_workflow():
    """REAL DEFECT the gate itself shipped: the hint said `paper-3-v1.0.0-rc.1`, which matches
    NEITHER trigger pattern in release.yml (`v*`, `paper3-v*`). Following the gate's own advice
    would have created a tag that fired no workflow -- discoverable only after tagging."""
    import fnmatch
    import re
    wf = (_ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    line = re.search(r"^\s*tags:\s*\[(.*)\]\s*$", wf, re.M)
    assert line, "release.yml no longer declares tag triggers in the expected form"
    patterns = [p.strip().strip('"').strip("'") for p in line.group(1).split(",")]
    assert any(fnmatch.fnmatch(B.RELEASE_TAG, p) for p in patterns), (
        f"{B.RELEASE_TAG!r} matches none of {patterns} -- tagging it would fire no workflow")

    # non-vacuity: the name this originally used must still fail the same check
    assert not any(fnmatch.fnmatch("paper-3-v1.0.0-rc.1", p) for p in patterns)

    rep = B.release(_ROOT)
    assert B.RELEASE_TAG in rep["tag_hint"]


def test_the_strict_gate_runs_in_ci_for_paper3_tags():
    """A gate nobody runs is decoration. release.yml must invoke it on the tags it certifies."""
    wf = (_ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
    assert "puckworks.paper3.build release" in wf, "the strict gate is not wired into CI"
    assert "paper3-v" in wf
    assert "figures" in wf, "the gate recomputes figure source data; the extra must be installed"

"""Paper 3 MC7 (availability matrix) and MC8 (implementation status).

MC7 exists because "executable" was doing too much work: the title claimed it of the whole
registry while rights, data, hosting and release status differ per component. A matrix that simply
reported `True` everywhere would restate the overclaim in a wider table, so these tests check that
the matrix DISCRIMINATES — that it separates the dimensions rather than agreeing with itself.

MC8's table is declared rather than derived, and the tests hold it to the standard that follows
from that: every row must carry evidence, and the capabilities the manuscript must not overstate
must actually be marked as intent.
"""
import json

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import availability as A


@pytest.fixture(scope="module")
def m():
    return A.matrix()


@pytest.fixture(scope="module")
def status():
    return A.implementation_status()


def test_every_registered_component_has_a_row(m):
    assert m["n_components"] == len(R.components())
    assert {r["component"] for r in m["rows"]} == {c.name for c in R.components()}


def test_all_eight_dimensions_the_review_named_are_present(m):
    for dim in ("registered", "importable", "runnable_local", "required_data_available",
                "scientifically_eligible", "redistribution_license_status",
                "public_hosting_status", "included_in_release"):
        assert dim in m["dimensions"], dim
        for row in m["rows"]:
            assert dim in row, (row["component"], dim)


def test_the_matrix_actually_discriminates_between_dimensions(m):
    """THE POINT OF MC7. If every dimension gave the same answer for every component, the matrix
    would be a wider way of saying "all 27 are executable" — the overclaim it exists to replace.
    At least two dimensions must disagree with each other somewhere."""
    signatures = {}
    for dim in m["dimensions"]:
        signatures[dim] = tuple(str(r[dim]["value"]) for r in m["rows"])
    distinct = len(set(signatures.values()))
    assert distinct >= 4, (
        f"only {distinct} distinct answer patterns across {len(m['dimensions'])} dimensions — "
        f"the matrix is not separating the notions of availability it was built to separate")


def test_the_public_hosting_count_is_far_below_the_component_count(m):
    """The concrete finding the manuscript must state: being registered and runnable locally is not
    being cleared for public hosted execution. If these ever coincided, the paper's 'executable'
    language would need re-checking rather than this test being relaxed."""
    public = sum(1 for r in m["rows"] if r["public_hosting_status"]["value"])
    local = sum(1 for r in m["rows"] if r["runnable_local"]["value"])
    assert public < local, (public, local)


def test_the_rights_blocked_component_is_visible_as_blocked(m):
    """grudeva2025.reduced is the review's own example. It must not read as available."""
    row = next(r for r in m["rows"] if r["component"] == "grudeva2025.reduced")
    assert row["runnable_local"]["value"] is False
    assert row["required_data_available"]["value"] is False
    assert row["blocking_reason"], "a blocked component with no recorded reason is not actionable"


def test_every_cell_records_how_it_was_obtained(m):
    """derived vs declared. A matrix that mixed them silently would look more rigorous than it is."""
    for row in m["rows"]:
        for dim in m["dimensions"]:
            assert row[dim]["how"] in ("derived", "declared"), (row["component"], dim)
            assert row[dim]["why"], f"{row['component']}.{dim} has no justification"
    assert m["n_cells_derived"] > m["n_cells_declared"], (
        "most of the matrix should be derived; if declarations dominate, it is an assertion table")


def test_the_module_attribute_pointer_convention_does_not_read_as_broken(m):
    """REAL DEFECT the first version had: calibration components name a `module:attribute` dataset
    pointer, and importing that as a module raises ModuleNotFoundError. Three good components were
    reported unimportable for a reason that was a fact about the check, not about them."""
    pointer_components = [c.name for c in R.components() if ":" in c.module]
    assert pointer_components, "the convention is gone — re-check this guard"
    for name in pointer_components:
        row = next(r for r in m["rows"] if r["component"] == name)
        assert row["importable"]["value"] is True, (name, row["importable"]["why"])


def test_importability_is_not_a_rubber_stamp():
    """Non-vacuity for the test above: the check must still fail on something that truly is
    unresolvable, or it is only ever returning True."""
    class _Fake:
        module = "puckworks.data:definitely_not_a_real_attribute_xyz"
    ok, why = A._importable(_Fake())
    assert ok is False and "no attribute" in why

    class _Fake2:
        module = "puckworks.not_a_real_module_xyz"
    ok2, why2 = A._importable(_Fake2())
    assert ok2 is False and "ModuleNotFound" in why2


# --------------------------------------------------------------------------- MC8

def test_implementation_status_declares_itself_declared(status):
    assert "declared" in status["how"]
    for row in status["rows"]:
        assert row["evidence"], row["capability"]


def test_the_capabilities_the_review_named_are_all_covered(status):
    caps = " ".join(r["capability"].lower() for r in status["rows"])
    for needle in ("adapter", "observables", "multi-stage", "scorecard", "corpus", "contract"):
        assert needle in caps, needle


def test_arbitrary_composition_and_the_observables_stage_are_marked_intent(status):
    """MC8's specific warning: do not imply arbitrary safe composition is automated. These two must
    read as architectural intent, not as implemented functionality."""
    intent = set(status["architectural_intent_only"])
    assert any("Arbitrary multi-stage" in c for c in intent), intent
    assert any("Observables stage" in c for c in intent), intent


def test_the_observables_stage_really_is_empty():
    """Non-vacuity: the declared row must match the registry. If a component is ever registered in
    `observables`, the table becomes wrong and this fails."""
    stages = {c.stage for c in R.components()}
    assert "observables" not in stages, (
        "observables now has components — update IMPLEMENTATION_STATUS, which calls it intent")


def test_generated_artifacts_are_not_stale():
    problems = A.verify()
    assert problems == [], problems


def test_the_generated_json_is_machine_readable_as_the_review_asked():
    payload = json.loads(A.MATRIX_JSON.read_text(encoding="utf-8"))
    assert payload["rows"] and payload["counts"]
    status = json.loads(A.STATUS_JSON.read_text(encoding="utf-8"))
    assert status["rows"] and status["counts"]


def test_the_manuscript_tables_are_generated_not_hand_written():
    """Same discipline as the named-shot scorecard: the manuscript owns the prose, the producer
    owns the table. Without this guard the tables become hand-edited copies that drift silently —
    the exact failure MC2 was raised about."""
    text = A.MANUSCRIPT.read_text(encoding="utf-8")
    for begin, end, _ in A._BLOCKS:
        assert begin in text and end in text, begin
    assert A.splice(write_it=False) == "", "a manuscript table is stale — run --splice"


def test_the_staleness_guard_is_not_vacuous(tmp_path, monkeypatch):
    """Proof that the guard above can fail: corrupt the spliced block in a COPY and confirm it is
    reported stale."""
    import shutil
    copy = tmp_path / "draft.md"
    shutil.copy(A.MANUSCRIPT, copy)
    text = copy.read_text(encoding="utf-8")
    begin, end, _ = A._BLOCKS[0]
    corrupted = text.split(begin)[0] + begin + "\n| tampered |\n" + end + text.split(end, 1)[1]
    copy.write_text(corrupted, encoding="utf-8")
    monkeypatch.setattr(A, "MANUSCRIPT", copy)
    assert "STALE" in A.splice(write_it=False)


def test_the_prose_counts_match_the_generated_matrix():
    """The prose states three counts (27 registered/importable, 26 runnable, 1 public, 25
    unreviewed). A generated table beside hand-written prose that disagrees with it is worse than
    no table at all."""
    m = A.matrix()
    text = A.MANUSCRIPT.read_text(encoding="utf-8")
    public = sum(1 for r in m["rows"] if r["public_hosting_status"]["value"])
    local = sum(1 for r in m["rows"] if r["runnable_local"]["value"])
    unreviewed = sum(1 for r in m["rows"]
                     if "NOT_REVIEWED" in str(r["redistribution_license_status"]["value"]))
    assert f"{local} of {m['n_components']} are runnable locally" in text, local
    assert f"**{unreviewed} of {m['n_components']} carry no rights review on record**" in text
    assert public == 1, ("the prose says exactly one component is publicly cleared", public)

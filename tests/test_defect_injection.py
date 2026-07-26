"""Tests for the guardrail defect-injection benchmark (Paper 3 review MC10).

The benchmark's value depends entirely on it being honest, so these tests police the benchmark
itself rather than the guards: the corpus must stay in sync with the tree, it must not quietly
mutate the working files, it must keep its known-miss rows, and its headline numbers must be the
ones the manuscript prints.
"""
import hashlib
import pathlib

import pytest

from puckworks.paper3 import defect_injection as DI

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_TOUCHED = [
    "docs/PAPER_A_DRAFT.md",
    "docs/submission/PAPER_A_JFE_MANUSCRIPT.md",
    "docs/PAPER_3_PUCKWORKS_DRAFT.md",
]


@pytest.fixture(scope="module")
def result():
    return DI.run_benchmark()


def test_every_outcome_matches_its_declared_expectation(result):
    """The corpus declares, per defect, whether the system should catch it. A mismatch means either
    a guard regressed or a gap was closed -- both require a human decision, so fail loudly rather
    than silently re-baselining."""
    bad = [(r["id"], r["name"], r["expected_caught"], r["caught"], r["detail"])
           for r in result["rows"] if not r["as_expected"]]
    assert not bad, "defect outcomes differ from expectation: %s" % bad


def test_the_benchmark_does_not_mutate_the_working_tree(result):
    """Injection must happen on copies. If this ever fails, the benchmark has been corrupting the
    manuscripts it claims to protect."""
    before = {rel: hashlib.sha256((_ROOT / rel).read_bytes()).hexdigest() for rel in _TOUCHED}
    DI.run_benchmark()
    after = {rel: hashlib.sha256((_ROOT / rel).read_bytes()).hexdigest() for rel in _TOUCHED}
    assert before == after


def test_the_corpus_keeps_known_misses(result):
    """A benchmark that reported only its catches would repeat the selected-demonstration problem
    it exists to fix. Removing the undetected rows must not be possible silently."""
    misses = [r for r in result["rows"] if not r["expected_caught"]]
    assert len(misses) >= 5, "the corpus has lost its known-miss rows"
    for r in misses:
        assert r["why_missed"], "%s is a declared miss with no explanation" % r["id"]


def test_the_unit_guard_gap_is_recorded_with_its_cause():
    """The benchmark's own finding: a RANGE check cannot separate units whose scale factor is
    smaller than the quantity's physical spread. Verified directly, not just asserted in prose."""
    from puckworks.contracts import K_SI_MAX, K_SI_MIN, assert_si_permeability

    k = 5e-13                                   # mid espresso bed range, in m^2
    assert K_SI_MIN < k * 1e6 < K_SI_MAX, "mm^2 value should fall INSIDE the declared window"
    assert_si_permeability(k * 1e6)             # must NOT raise -- that is the gap
    assert_si_permeability(k * 1e4)             # cm^2, same cause
    with pytest.raises(ValueError):             # darcy: scale factor exceeds the window
        assert_si_permeability(k / 9.869e-13)


def test_defect_classes_are_declared_and_used(result):
    declared = set(DI.DEFECT_CLASSES)
    used = {r["defect_class"] for r in result["rows"]}
    assert used <= declared, "undeclared defect class: %s" % (used - declared)
    assert used == declared, "declared but unused class: %s" % (declared - used)


def test_ids_are_unique_and_ordered(result):
    ids = [r["id"] for r in result["rows"]]
    assert len(set(ids)) == len(ids), "duplicate defect ids: %s" % ids
    assert ids == sorted(ids)


def test_no_harness_errors(result):
    """A defect whose anchor has gone stale reports as a harness error, which would silently look
    like a miss. Those must be fixed, not tolerated."""
    broken = [(r["id"], r["detail"]) for r in result["rows"] if r["guard"] == "(harness error)"]
    assert not broken, "defect corpus is stale: %s" % broken


def test_manuscript_reports_the_benchmark_numbers(result):
    """The paper must print the benchmark's actual totals, not a remembered pair."""
    text = (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")
    assert "%d defects" % result["n_defects"] in text
    assert "%d were detected" % result["n_detected"] in text
    assert "%d were not" % result["n_undetected"] in text


def test_render_names_every_undetected_defect(result):
    block = DI.render(result)
    for r in result["rows"]:
        if not r["caught"]:
            assert r["id"] in block and r["name"] in block

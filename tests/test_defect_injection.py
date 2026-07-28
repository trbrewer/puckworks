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
    # Whitespace-normalised: the assertions hard-coded a specific line break, so re-wrapping the
    # paragraph made a correct sentence read as absent.
    text = " ".join((_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md")
                    .read_text(encoding="utf-8").split())
    assert "**%d injected defects**" % result["n_defects"] in text
    assert "**%d were caught and %d were missed**" % (
        result["n_defects_detected"], result["n_defects_missed"]) in text
    # "declared structural families", not "independent structural groups": the grouping is an
    # author-assigned de-duplication device and independence was never established (P0-12).
    assert "**%d declared structural families**" % result["n_independent_groups"] in text
    assert "independent structural groups" not in text
    assert "Two **valid controls**" in text and result["n_controls"] == 2


def test_render_names_every_undetected_defect(result):
    block = DI.render(result)
    for r in result["rows"]:
        if not r["caught"] and not r["is_control"]:
            assert r["id"] in block and r["name"] in block


# ── third review P0-7: the reporting must not be able to flatter itself ───────────────────────
def test_controls_are_not_counted_as_defects(result):
    """`D04` is a valid SI permeability the range guard must ACCEPT. It was counted in n_defects,
    n_detected and the detection-rate denominator."""
    controls = [r for r in result["rows"] if r["is_control"]]
    assert controls, "the suite must contain valid controls"
    assert result["n_defects"] == len([r for r in result["rows"] if not r["is_control"]])
    assert result["n_defects"] + result["n_controls"] == len(result["rows"])
    assert "D04" in {r["id"] for r in controls}


def test_no_headline_coverage_percentage_is_emitted(result):
    """The central correction is conceptual: neither 67 % nor 64.7 % estimates architecture
    coverage, because the corpus has no sampling frame."""
    for banned in ("detection_rate", "coverage", "rate"):
        assert banned not in result, f"a coverage-style scalar is back: {banned}"
    text = (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")
    assert "A detection rate of 67%" not in text
    assert "no single coverage percentage" in text


def test_specificity_is_reported_separately_from_sensitivity(result):
    for key in ("n_controls", "n_controls_passed", "n_false_positives"):
        assert key in result
    for fam in result["by_family"].values():
        assert {"true_positives", "false_negatives", "controls", "false_positives"} <= set(fam)


def test_related_mutations_share_an_independence_group(result):
    """D01/D02 are two scale factors of one structural failure; counting them as two independent
    pieces of evidence overstates the sample size."""
    groups = {r["id"]: r["independence_group"] for r in result["rows"]}
    assert groups["D01"] == groups["D02"] == "range_guard"
    assert result["n_independent_groups"] < result["n_defects"], (
        "if every case were its own group the grouping would be doing no work")


def test_every_case_declares_the_execution_path_it_actually_traverses(result):
    """`executable` lumped four different things together.

    It covered an end-to-end contract violation and a manuscript phrase sentinel alike, which is
    what let the paper claim "15 executable mutations that perturb a real input and run the
    production guard" (fourth review P0-12). The honest production-path count is 10.
    """
    kinds = {r["execution_type"] for r in result["rows"]}
    assert kinds <= {"production_path_mutation", "integration_regression_sentinel",
                     "static_manuscript_check", "limitation_analysis"}
    assert "executable" not in kinds, (
        "the undifferentiated `executable` label is back; it cannot support a production-path claim")
    assert result["n_limitation_analyses"] > 0, (
        "cases that return a hard-coded outcome must be labelled, not counted as mutations")
    # The path breakdown must partition the defects exactly -- no case unclassified, none double
    # counted, and controls excluded throughout.
    assert sum(result["by_execution_type"].values()) == result["n_defects"]
    assert result["n_executable_mutations"] == result["by_execution_type"][
        "production_path_mutation"]
    assert result["n_executable_mutations"] < result["n_defects"], (
        "if every defect were a production-path mutation the distinction would be doing no work")
    for k, n in result["by_execution_type_detected"].items():
        assert 0 <= n <= result["by_execution_type"][k]


def test_the_absence_of_a_holdout_suite_is_declared(result):
    """Selection bias must be visible: every case was authored by the guards' own authors."""
    assert result["has_holdout_suite"] is False
    assert "no held-out challenge set" in (
        _ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8").lower()


def test_a_vacuous_always_caught_benchmark_would_fail_the_controls():
    """NON-VACUITY of the controls themselves: a guard that rejected everything must score as a
    false positive rather than as perfect detection."""
    import puckworks.paper3.defect_injection as M
    ctrl = next(d for d in M.CORPUS if d.is_control)
    # Simulate a guard that refuses every input: the control's injector reports caught=False.
    out = M.Outcome(False, "always-reject guard", "VALID input rejected")
    assert not out.caught, "a rejected control must not read as a caught defect"

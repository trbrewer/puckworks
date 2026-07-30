"""Round-10 P0-1/P1-1/P2-1: what the paper may claim, and what a scanner must catch.

Three defects shipped together at the round-10 target commit, and they reinforced each other:

  * the central conclusion — "no resolvable skill" — was a DECISION about absence, asserted from an
    analysis the same paper describes as having no calibrated coverage and supporting no
    distinguishability, non-distinguishability or equivalence claim;
  * the canonical draft and the venue manuscript carried materially different active abstracts while
    CI, on the strength of a curated phrase list, called them content-aligned; and
  * the process-language scanner read physical lines, so a prohibited phrase wrapped across three
    source lines was invisible to it while being plainly visible to a reader.

Every test here is keyed to one of those, and each mutation is one a person could plausibly make.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib
import shutil
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import claim_policy as CP  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402
from tools import paper_a_consistency as C  # noqa: E402

STATUS = TS.TRANSFER_INFERENTIAL_STATUS
ESTIMAND = TS.POOLED_MAPE_ESTIMAND


# ── 1. the prohibited decision language (P0-1) ──────────────────────────────────────────────
@pytest.mark.parametrize("sentence,rule", [
    ("The model showed no resolvable skill beyond a transferred level.", "no_resolvable_skill"),
    ("a mechanistic model can achieve acceptable error while adding no resolvable skill",
     "adds_no_skill"),
    ("Acceptable endpoint accuracy therefore did not supply resolvable skill.",
     "did_not_supply_skill"),
    ("We report the benchmark as unresolved throughout the declared tolerance.",
     "unresolved_throughout"),
    ("Figure 3 states finding 2 — no resolvable gain over the level-only comparator.",
     "no_resolvable_skill"),
    ("The two predictors are statistically indistinguishable.", "non_distinguishable"),
    ("The difference is statistically significant.", "statistical_significance"),
    ("The mechanistic model outperformed the comparator.", "outperforms"),
    ("The arms are practically equivalent.", "is_equivalent"),
    ("There is no meaningful difference between the arms.", "no_meaningful_difference"),
    ("The increment is practically negligible.", "practically_negligible"),
    ("The model is non-inferior to the comparator.", "non_inferior"),
    # Close variants an independent second review asked for: each is a different grammatical route
    # back to the retired verdict, and the first is the one a brevity edit would reach for.
    ("The kinetic structure adds no incremental skill.", "no_incremental_skill"),
    ("The comparison showed no mechanistic advantage.", "no_incremental_skill"),
    ("There is no difference between the two arms.", "no_difference"),
    ("The rate multiplier has no effect on pooled error.", "no_effect"),
    ("The model is at least as good as the comparator.", "at_least_as_good"),
    ("The mechanistic model is no worse than the level-only baseline.", "at_least_as_good"),
    ("The two predictors perform comparably.", "comparable_performance"),
])
def test_every_retired_verdict_is_prohibited_under_the_declared_status(sentence, rule):
    problems = CP.scan(sentence, STATUS)
    assert problems, "FALSE GREEN: %r" % sentence
    assert any("[%s]" % rule in p for p in problems), (rule, problems)


@pytest.mark.parametrize("sentence", [
    # The paper MUST be able to say what it is not claiming. Round 10 praised this sentence.
    "We therefore make **no claim of statistical distinguishability, non-distinguishability or "
    "equivalence** from these ranges.",
    "We claim neither superiority nor equivalence nor absence of incremental skill.",
    "These ranges do not establish whether the advantage is reproducible or practically useful.",
    "Their positions determine neither superiority, non-inferiority, equivalence, nor absence of "
    "skill.",
    "No row here establishes resolvable incremental skill, and none establishes its absence.",
    "Acceptable endpoint accuracy does not by itself establish mechanistic transfer.",
    "This is not a statistical null: no null hypothesis, null distribution or calibrated test is "
    "defined.",
    # The corrected endpoint synthesis says both of these, and both must stay sayable.
    "That applies symmetrically: the wholly negative ranges do not establish an advantage, and the "
    "zero-containing ranges do not establish its absence.",
    "It does not establish that the difference is absent.",
])
def test_explicit_disclaimers_are_permitted(sentence):
    """A scanner that banned these would push authors toward silence about the limits."""
    assert CP.scan(sentence, STATUS) == [], sentence


def test_a_phrase_split_across_lines_or_wrapped_in_emphasis_is_still_caught():
    """Markdown must not be a bypass: bolding and wrapping are how the round-10 leak survived."""
    for text in ("The model added\nno resolvable skill.",
                 "The model added **no resolvable skill**.",
                 "The model added no\n   resolvable\n   skill.",
                 "The model added  no   resolvable    skill."):
        assert CP.scan(text, STATUS), text


def test_the_prohibition_is_derived_from_the_status_not_hard_coded():
    """A future calibrated analysis unlocks the language by DECLARING the decision, not by editing
    a word list. That is the difference between a policy and a ban."""
    verdict = "Under the predeclared margin the two arms are equivalent."
    assert CP.scan(verdict, STATUS)

    earned = dataclasses.replace(
        STATUS, coverage_calibrated=True, confidence_level=0.95,
        confidence_procedure="cluster bootstrap TOST",
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        supports_equivalence_decision=True, practical_margin_pp=0.5,
        permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION)
    assert TS.validate_inferential_status(earned) == []
    assert CP.scan(verdict, earned) == []
    # …but an absence-of-skill verdict is still not licensed by an equivalence decision alone.
    assert CP.scan("The model adds no resolvable skill.", earned)


def test_the_limits_sentence_is_generated_from_the_status():
    text = CP.limits_sentence(STATUS, ESTIMAND)
    for decision in ("superiority", "non-inferiority", "equivalence", "absence of skill"):
        assert decision in text
    assert "does not establish that the difference is absent" in text
    assert CP.scan(text, STATUS) == [], "the generated caveat must satisfy its own policy"


def test_the_limits_sentence_refuses_to_describe_a_calibrated_analysis():
    calibrated = dataclasses.replace(
        STATUS, coverage_calibrated=True, confidence_level=0.95,
        confidence_procedure="cluster bootstrap",
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        supports_superiority_decision=True,
        permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION)
    with pytest.raises(NotImplementedError):
        CP.limits_sentence(calibrated, ESTIMAND)


# ── 2. the accepted claim is actually made, on every surface (P0-1) ─────────────────────────
def test_every_named_surface_carries_the_propositions_it_must():
    assert C._claim_policy() == []


@pytest.mark.parametrize("surface", sorted(CP.SURFACE_ASSERTIONS))
def test_dropping_a_required_proposition_is_caught(surface):
    """An empty surface must fail every requirement — the check cannot be vacuous."""
    missing = CP.missing_assertions("", surface)
    assert len(missing) == len(CP.SURFACE_ASSERTIONS[surface])


def test_a_surface_with_no_declared_requirement_fails_loudly():
    with pytest.raises(KeyError, match="no assertion requirement declared"):
        CP.missing_assertions("anything", "some_new_surface")


def test_the_committed_tree_states_the_observed_advantage_with_its_sign():
    """P0-1's positive half: the point estimate favours the model and the paper must say so."""
    manuscript = (REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md").read_text()
    assert ESTIMAND.direction_clause in " ".join(manuscript.split())
    assert "−0.394" in manuscript


# ── 3. canonical/venue parity (P1-1) ───────────────────────────────────────────────────────
def test_the_two_manuscripts_render_the_same_scientific_blocks():
    assert C._generated_block_parity() == []


@pytest.fixture
def two_manuscripts(tmp_path, monkeypatch):
    """Copies of both manuscripts and the package, with the contract pointed at them."""
    copies = {}
    for attr in ("CANONICAL", "CONVERSION", "PACKAGE"):
        src = getattr(C, attr)
        dst = tmp_path / src.name
        shutil.copy(src, dst)
        monkeypatch.setattr(C, attr, dst)
        copies[attr] = dst
    return copies


@pytest.mark.parametrize("target,mutate,expect", [
    ("CONVERSION", lambda s: s.replace("does not establish whether", "establishes no"),
     "differs between"),
    ("CANONICAL", lambda s: s.replace("−0.394", "+0.394"), "differs between"),
    ("CONVERSION", lambda s: s.replace("<!-- paper-a:transfer-headline:begin -->", ""),
     "must appear exactly once"),
    ("CANONICAL", lambda s: s + "\n<!-- paper-a:transfer-headline:begin -->\nx\n"
                                "<!-- paper-a:transfer-headline:end -->\n",
     "must appear exactly once"),
])
def test_central_claim_drift_between_the_manuscripts_fails(two_manuscripts, target, mutate, expect):
    path = two_manuscripts[target]
    path.write_text(mutate(path.read_text()), encoding="utf-8")
    problems = C._generated_block_parity()
    assert problems, "FALSE GREEN: %s mutation went undetected" % target
    assert any(expect in p for p in problems), problems


def test_an_abstract_that_is_not_the_one_source_fails(two_manuscripts):
    """The round-10 defect exactly: the canonical abstract reporting "incremental skill"."""
    path = two_manuscripts["CANONICAL"]
    path.write_text(path.read_text().replace(
        "The paired difference was −0.394 percentage points",
        "The model showed an incremental skill of ≈4.5 % relative"), encoding="utf-8")
    problems = C._generated_block_parity()
    assert problems, "FALSE GREEN: a canonical abstract that is not the source's abstract"
    assert any("abstract" in p for p in problems), problems


def test_abstract_drift_is_caught_without_a_yaml_parser(two_manuscripts, monkeypatch):
    """pyyaml is an optional extra, and the minimum-dependency lane does not have it.

    The first version of this check returned early there, so the mutation above passed on that lane —
    a check that CANNOT run looking exactly like a check that ran and found nothing. The comparison is
    now in two steps: renderings against each other (no parser needed), then against the source.
    """
    import builtins

    real_import = builtins.__import__

    def no_yaml(name, *args, **kwargs):
        if name == "yaml":
            raise ImportError("No module named 'yaml'")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_yaml)

    assert C._generated_block_parity() == [], "the unmutated tree must still pass without pyyaml"
    assert C.abstract_source_unavailable, (
        "the partial coverage must be RECORDED, not silently treated as a pass")

    path = two_manuscripts["CANONICAL"]
    path.write_text(path.read_text().replace(
        "The paired difference was −0.394 percentage points",
        "The model showed an incremental skill of ≈4.5 % relative"), encoding="utf-8")
    problems = C._generated_block_parity()
    assert any("differs from the" in p and "abstract" in p for p in problems), problems


def test_claim_coverage_audits_both_active_manuscripts_by_default():
    from puckworks.paper_a import claim_coverage as CC

    assert len(CC.ACTIVE_MANUSCRIPTS) == 2
    labels = {label for label, _p in CC.ACTIVE_MANUSCRIPTS}
    assert labels == {"canonical", "venue"}
    assert CC.main([]) == 0
    # And the diagnostic single-file modes must still exist, and still be single.
    assert CC.main(["--canonical-only"]) == 0
    assert CC.main(["--conversion-only"]) == 0


# ── 4. the paragraph-aware scanner (P2-1) ──────────────────────────────────────────────────
def test_the_committed_tree_has_no_process_leakage():
    assert C._placeholders_and_process_language() == []


@pytest.fixture
def scanned(tmp_path, monkeypatch):
    """One scannable copy of the manuscript, with every other prose file removed from the set."""
    dst = tmp_path / C.CONVERSION.name
    shutil.copy(C.CONVERSION, dst)
    monkeypatch.setattr(C, "CONVERSION", dst)
    monkeypatch.setattr(C, "SUBMISSION_FILES", (dst,))
    monkeypatch.setattr(C, "CANONICAL", tmp_path / "absent.md")
    return dst


_WRAPPED = "An earlier version of this paragraph stated that the comparison was unavailable."


@pytest.mark.parametrize("split_at", range(1, len(_WRAPPED.split())))
def test_a_prohibited_phrase_fails_at_every_token_boundary(scanned, split_at):
    """The round-10 leak survived because it was broken across lines at exactly one such boundary.

    Every boundary is tested, not the one that happened to occur: a scanner that handles the reported
    case and not its neighbours has been patched, not fixed.
    """
    words = _WRAPPED.split()
    injected = " ".join(words[:split_at]) + "\n" + " ".join(words[split_at:])
    scanned.write_text(scanned.read_text() + "\n\n" + injected + "\n", encoding="utf-8")
    problems = C._placeholders_and_process_language()
    assert any("earlier version" in p for p in problems), (split_at, problems)


def test_a_prohibited_phrase_split_across_three_lines_fails(scanned):
    scanned.write_text(scanned.read_text() + "\n\nAn\nearlier\nversion of this paragraph said "
                       "otherwise;\nthat\nwas\nwrong.\n", encoding="utf-8")
    problems = C._placeholders_and_process_language()
    assert any("earlier version" in p for p in problems)
    assert any("that was wrong" in p for p in problems)


@pytest.mark.parametrize("injected,expect", [
    ("The second review asked for four to five main figures.", "review"),
    ("Reviewers asked us to move the diagnostics to a supplement.", "review"),
    ("The rendered images previously carried their producer number.", "previously carried"),
    ("This corrects an earlier version of the analysis.", "earlier version"),
    ("See `tests/test_figure_exports.py` for the policy.", "tests/test_figure_exports.py"),
    ("Producer `fig4_transfer` is presentation Figure 3.", "fig4_transfer"),
    ("The generator lives in `tools/paper_a_transfer_text.py`.", "tools/paper_a_transfer_text.py"),
    ("Round-9 P2-1 covered this.", "P2-1"),
    ("Numbers regenerate from puckworks/figures_paper_a.py.", "puckworks/figures_paper_a.py"),
    ("See .github/workflows/ci.yml for the lane.", ".github/workflows/ci.yml"),
])
def test_each_leakage_class_is_caught_in_a_submission_file(scanned, injected, expect):
    scanned.write_text(scanned.read_text() + "\n\n" + injected + "\n", encoding="utf-8")
    problems = C._placeholders_and_process_language()
    assert any(expect in p for p in problems), (injected, problems[:5])


@pytest.mark.parametrize("injected", [
    "AN EARLIER VERSION of this paragraph was different.",
    "An  earlier   version of this paragraph was different.",
    "An\tearlier\tversion of this paragraph was different.",
])
def test_case_and_whitespace_variation_does_not_evade_the_scanner(scanned, injected):
    scanned.write_text(scanned.read_text() + "\n\n" + injected + "\n", encoding="utf-8")
    assert any("earlier version" in p.lower()
               for p in C._placeholders_and_process_language())


def test_an_html_comment_is_not_reader_facing(scanned):
    """Source stamps and rationale comments are assurance devices, not prose a reviewer reads."""
    scanned.write_text(scanned.read_text()
                       + "\n\n<!-- An earlier version of this said something else. -->\n",
                       encoding="utf-8")
    assert not any("earlier version" in p for p in C._placeholders_and_process_language())


def test_stripping_a_comment_preserves_line_numbers():
    """Diagnostics have to name a line a person can open."""
    text = "one\n<!-- two\nthree -->\nAn earlier version of this was wrong.\n"
    stripped = C._strip_html_comments(text)
    assert len(stripped.splitlines()) == len(text.splitlines())
    assert [n for n, _p in C._visible_paragraphs(text)] == [1, 4]


def test_an_image_target_is_not_read_as_a_leaked_identifier():
    """The SI references `figures/fig3_holdouts.png` — the name of a file the editor receives."""
    blocks = C._visible_paragraphs("![Supplementary Figure S1](figures/fig3_holdouts.png)\n")
    assert blocks == [(1, "Supplementary Figure S1")]


def test_the_internal_figure_map_is_not_a_submission_surface():
    """It is ALLOWED to carry producer stems, test paths and review history — that is its job."""
    assert C.FIGURE_MAP_INTERNAL not in C.prose_scanned_files()
    assert C.UPLOAD_CAPTIONS in C.SUBMISSION_FILES
    internal = C.FIGURE_MAP_INTERNAL.read_text(encoding="utf-8")
    assert "fig4_transfer" in internal and "tests/test_figure_exports.py" in internal


def test_the_upload_ready_captions_are_clean_and_generated():
    assert C._upload_captions_are_generated_and_clean() == []
    text = C.UPLOAD_CAPTIONS.read_text(encoding="utf-8")
    for leaked in ("fig4_transfer", "producer", "second review", "tests/", "docs/", "puckworks/"):
        assert leaked not in text, "the uploaded caption file carries %r" % leaked
    assert text.count("<!--") == 1, "only the generation stamp may be a comment"
    assert CP.scan(text, STATUS) == []


def test_the_package_manifest_lists_the_upload_file_and_not_the_internal_map():
    package = (REPO / "docs" / "submission" / "PAPER_A_JFE_PACKAGE.md").read_text()
    assert "PAPER_A_JFE_FIGURE_CAPTIONS.md" in package
    assert "PAPER_A_FIGURE_MAP_INTERNAL.md" not in package


def test_an_internal_path_in_a_data_availability_section_is_allowed(scanned):
    """A narrow, section-scoped allowance: naming the deposit IS the content there."""
    scanned.write_text(scanned.read_text()
                       + "\n\n## Data and code availability\n\nSee `docs/reproducibility/` "
                         "in the archived release.\n", encoding="utf-8")
    problems = [p for p in C._placeholders_and_process_language() if "docs/reproducibility" in p]
    assert problems == []


# ── 5. the inferential status the artefact actually declares ────────────────────────────────
def test_the_committed_artefact_declares_the_status_the_claims_assume():
    ep = json.loads((REPO / "docs" / "paper1_resource"
                     / "PAPER_A_ENDPOINT_PROPAGATION.json").read_text())
    declared = TS.status_from_dict(ep["resampling_design"]["inferential_status"])
    assert declared == STATUS
    assert TS.validate_inferential_status(declared) == []

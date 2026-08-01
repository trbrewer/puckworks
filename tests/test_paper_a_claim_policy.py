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
import re
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


# ── 1b. round-11 P0-1/P1-1: the retired verdict returning by PARAPHRASE ─────────────────────
#
# Round 10 retired "no resolvable skill" and Round 11 found the same decision back on five
# reader-facing surfaces in different words — "adding little", "incremental skill … is small",
# "nearly matched" — with the claim scanner reporting ZERO problems on both manuscripts. Two
# separate defects produced that false green, and both are tested here:
#
#   * the taxonomy had no practical-magnitude or equivalence-adjacent classes at all; and
#   * ANY of `neither`, `without`, `is not`, `are not`, `not a` in the preceding 140 characters
#     suppressed a hit, so a limitations sentence licensed the verdict that followed it.
#
# The exact retired sentences are pinned verbatim: a paraphrase test that does not include the
# wording actually shipped is a test of the fix, not of the defect.
_RETIRED_ROUND_11 = [
    ("while adding little to a baseline that carries no mechanism at all", "adds_little"),
    ("its incremental skill over a level-only comparator is small", "small_incremental_value"),
    ("incremental skill over a level-only baseline is small", "small_incremental_value"),
    ("performance was nearly matched by an O-trained level-only constant", "nearly_matched"),
    ("**incremental skill over a level-only comparator is small**", "small_incremental_value"),
]


@pytest.mark.parametrize("sentence,rule", _RETIRED_ROUND_11 + [
    ("The model adds little to a baseline that carries no mechanism at all.", "adds_little"),
    ("The mechanistic model offers only marginal benefit.", "small_incremental_value"),
    ("The kinetic structure provides little beyond the transferred level.", "adds_little"),
    ("Its incremental skill is minimal.", "small_incremental_value"),
    ("The models are essentially the same.", "essentially_same"),
    ("Performance was effectively matched by the comparator.", "nearly_matched"),
    ("The difference is within noise.", "within_noise"),
    ("There is no practical advantage to the mechanistic model.", "no_practical_advantage"),
    ("The comparator is no worse than the mechanistic model.", "at_least_as_good"),
])
def test_practical_negligibility_paraphrases_are_prohibited(sentence, rule):
    problems = CP.scan(sentence, STATUS)
    assert problems, "FALSE GREEN: %r" % sentence
    assert any("[%s]" % rule in p for p in problems), (rule, problems)


@pytest.mark.parametrize("sentence,rule", _RETIRED_ROUND_11)
def test_the_retired_round_11_sentences_fail_on_every_scanned_surface(scanned, sentence, rule):
    """Not merely in a unit test: injected into an actual upload file, the gate must bite.

    Round 11's finding was precisely that these sentences were IN the shipped manuscript while
    `tools/paper_a_consistency.py verify` printed a clean result.
    """
    scanned.write_text(scanned.read_text() + "\n\n" + sentence + "\n", encoding="utf-8")
    problems = C._claim_policy()
    assert any("[%s]" % rule in p for p in problems), (sentence, problems[:5])


@pytest.mark.parametrize("text", [
    # A nearby disclaimer is not a grammatical negation. Every one of these returned CLEAN at the
    # round-11 commit; the second is internally contradictory and passed anyway.
    "The ranges are not confidence intervals. The model outperforms the comparator.",
    "This is not an inferential result, but the model outperforms the comparator.",
    "Without calibrated coverage, the model outperforms the comparator.",
    "The result is not precise. The model has no incremental skill.",
    "We do not claim equivalence; the model is equivalent to the comparator.",
    "The uncertainty is not small. The model performs comparably.",
    "We make no claim of superiority — the model outperforms the comparator.",
    "No equivalence decision is made. However, the models are essentially the same.",
    "This analysis does not establish superiority, and the model outperforms the comparator.",
])
def test_a_disclaimer_in_another_clause_cannot_license_a_verdict(text):
    assert CP.scan(text, STATUS), "FALSE GREEN: %r" % text


@pytest.mark.parametrize("text", [
    # …while the constructions that genuinely scope the decision term stay legal.
    "This analysis does not establish superiority.",
    "We make no claim of equivalence.",
    "The ranges cannot determine whether the observed difference is absent.",
    "Neither superiority nor equivalence is established by this analysis.",
    "The analysis does not establish that the model outperforms the comparator.",
    "We make no claim that the two arms are equivalent.",
])
def test_a_proposition_scoped_disclaimer_is_still_permitted(text):
    assert CP.scan(text, STATUS) == [], text


@pytest.mark.parametrize("text", [
    # False positives the new magnitude/equivalence rules must NOT produce. Each is ordinary,
    # correct language the paper needs: an interval bound, a sample, the matched-endpoint design
    # the whole estimand rests on, and the true statement that no margin exists.
    "The 40 g upper sensitivity bound was a small positive value.",
    "A small sample was used at each condition.",
    "Records were matched by variety, temperature, and pressure.",
    "Held-out cups were matched by collected mass to the source endpoint.",
    "No practical margin was predeclared.",
    "The endpoint-matched design adds little numerical cost.",
    "Each cluster carries its three co-measured solutes, matched conditions included.",
])
def test_the_magnitude_rules_do_not_fire_on_ordinary_language(text):
    assert CP.scan(text, STATUS) == [], text


def test_clause_splitting_is_explicit_about_its_boundaries():
    """The clause iterator is the load-bearing part of the disclaimer fix, so it is tested directly
    rather than only through `scan`."""
    assert list(CP.iter_decision_clauses("One thing. Another thing.")) == \
        ["One thing.", "Another thing."]
    assert list(CP.iter_decision_clauses("We claim nothing; the model wins.")) == \
        ["We claim nothing", "the model wins."]
    assert list(CP.iter_decision_clauses("Not calibrated, but the model wins.")) == \
        ["Not calibrated", "the model wins."]
    # A coordinated continuation of the SAME subject is one clause; a new subject is not.
    assert len(list(CP.iter_decision_clauses(
        "It does not establish A, and does not establish B."))) == 1
    assert len(list(CP.iter_decision_clauses(
        "It does not establish A, and the model wins."))) == 2
    # Decimals must not be read as sentence ends.
    assert list(CP.iter_decision_clauses("Pooled MAPE was 8.44 % here.")) == \
        ["Pooled MAPE was 8.44 % here."]


def test_the_generic_preceding_window_suppressors_are_gone():
    """The specific tokens the round-11 review named must no longer suppress anything on their own."""
    assert not hasattr(CP, "_DISCLAIMERS")
    assert not hasattr(CP, "_DISCLAIMER_WINDOW")
    for fragment in ("neither", "without", "is not", "are not", "not a", "reserve",
                     "rather than"):
        assert CP.find_non_establishment_spans(fragment) == [], fragment


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


def test_a_coherent_but_unevidenced_status_unlocks_nothing():
    """Round-11 P1-2, reproduced verbatim.

    The reviewer hand-wrote this object. It passed `validate_inferential_status` — it is internally
    coherent, and still is — and it unlocked "the model is equivalent to the comparator", because
    the permission was a boolean somebody could type rather than a result somebody had to earn.
    """
    verdict = "Under the predeclared margin the two arms are equivalent."
    assert CP.scan(verdict, STATUS)

    fabricated = dataclasses.replace(
        STATUS, coverage_calibrated=True, confidence_level=0.95,
        confidence_procedure="invented future procedure",
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        supports_equivalence_decision=True, practical_margin_pp=0.5,
        permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION)
    assert TS.validate_inferential_status(fabricated) == [], \
        "internal coherence is not the thing being tested; it must still hold"
    assert CP.granted(fabricated) == set(), "a DECLARED status grants nothing"
    assert CP.scan(verdict, fabricated), "FALSE GREEN: a fabricated status unlocked equivalence"


def test_the_prohibition_is_derived_from_evidence_not_hard_coded():
    """A future calibrated analysis unlocks the language by PRODUCING EVIDENCE that survives
    verification, not by editing a word list and not by declaring a flag. That is the difference
    between a policy and a ban, and between evidence and assertion."""
    from tests import helpers_inferential_evidence as H

    verdict = "Under the predeclared margin the two arms are equivalent."
    # Round-12 P1-4: through a reference re-verified from production storage, not an object.
    with H.registered_production_evidence() as earned:
        assert CP.scan(verdict, earned) == []
        # …but an absence-of-skill verdict is still not licensed by an equivalence decision alone.
        assert CP.scan("The model adds no resolvable skill.", earned)
        assert CP.scan("The model outperforms the comparator.", earned)


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


# ── 2b. round-11 P1-3: the two STANDALONE upload surfaces ───────────────────────────────────
def test_the_standalone_upload_surfaces_are_governed():
    """Both are uploaded as separate files and read without the manuscript's limitations."""
    for surface in ("highlights", "figure3_caption"):
        assert surface in CP.SURFACE_ASSERTIONS, surface
    # Figure 3's own file header says the captions stand alone, so it carries all four.
    assert set(CP.SURFACE_ASSERTIONS["figure3_caption"]) == {a.id for a in CP.ASSERTIONS}


def _standalone_source(surface: str) -> str:
    from tools import paper_a_consistency as CC

    return CC._read(CC.HIGHLIGHTS) if surface == "highlights" else CC._upload_caption(3)


@pytest.mark.parametrize("surface,proposition", [
    (s, p) for s in ("highlights", "figure3_caption") for p in CP.SURFACE_ASSERTIONS[s]])
def test_deleting_a_required_proposition_from_a_standalone_surface_fails(surface, proposition):
    """Non-vacuity on the REAL generated text, not only on an empty string.

    A proposition may be carried by any of several phrasings — that is what makes it a proposition
    and not a phrase — so the mutation removes EVERY accepted carrier. Deleting one rendering while
    a synonym survives is not a loss of the claim, and a test asserting otherwise would be testing
    the word list rather than the contract.
    """
    source = _standalone_source(surface)
    assert CP.missing_assertions(source, surface) == [], surface

    # Case-insensitively, because `present_in` is: the Highlights bullet opens a sentence with
    # "Uncalibrated ranges" and the carrier is declared in lower case.
    assertion = CP.ASSERTION_BY_ID[proposition]
    stripped = source
    for phrasing in assertion.any_of:
        stripped = re.sub(re.escape(phrasing), "", stripped, flags=re.I)
    assert stripped != source, "no carrier of %r is present in %s" % (proposition, surface)

    missing = CP.missing_assertions(stripped, surface)
    assert any(proposition in m for m in missing), \
        "FALSE GREEN: %s survived losing every carrier of %r" % (surface, proposition)


def test_an_unqualified_gain_fails_the_highlight_assertion():
    """"A process model's gain … was under 0.4 points" — the round-11 wording. Read alone it is an
    established property of the model, and it carries neither the range limit nor the non-decision."""
    retired = ("• A process model's gain over a concentration-only baseline was under 0.4 points\n")
    missing = CP.missing_assertions(retired, "highlights")
    assert {m.split("the ")[1].split(" claim")[0] for m in missing} == \
        set(CP.SURFACE_ASSERTIONS["highlights"]), (
            "the retired one-line highlight must fail EVERY proposition the surface requires")


def test_the_figure3_extractor_cannot_pick_up_figure_s3():
    """A regex over "Figure 3" would match "Figure S3", a different figure in the same file."""
    from tools import paper_a_consistency as CC

    three, s_three = CC._upload_caption(3), CC._upload_caption("S3")
    assert three.startswith("**Figure 3.") and s_three.startswith("**Figure S3.")
    assert three != s_three
    assert "MISSING" in CC._upload_caption(99), "an absent caption must be a NAMED problem"


def test_the_highlights_respect_the_venue_limit():
    """Compact rewriting is the answer to a character limit; deleting the caveat is not."""
    bullets = [ln[2:] for ln in C.HIGHLIGHTS.read_text(encoding="utf-8").splitlines()
               if ln.startswith("• ")]
    assert 3 <= len(bullets) <= 5
    for b in bullets:
        assert len(b) <= 85, (len(b), b)
        assert CP.scan(b, STATUS) == [], b


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


def test_an_internal_path_in_a_data_availability_section_is_no_longer_allowed(scanned):
    """Round-11 P1-6 RETIRED the section-scoped allowance this test used to assert.

    Fourteen whole sections — data availability, reproducibility, figure captions, the declarations —
    were path-legal, on the reasoning that naming the deposit IS the content there. That is far wider
    than the thing it existed for: at the round-11 commit every path in an upload deliverable was
    inside an unsupplied-metadata placeholder, and a genuine leak in an availability statement would
    have been legal. The allowance is now keyed to the PLACEHOLDER, not its neighbourhood, and the
    deposit is named by its public DOI rather than by a repository path.
    """
    scanned.write_text(scanned.read_text()
                       + "\n\n## Data and code availability\n\nSee `docs/reproducibility/` "
                         "in the archived release.\n", encoding="utf-8")
    problems = [p for p in C._placeholders_and_process_language() if "docs/reproducibility" in p]
    assert problems, "FALSE GREEN: a repository path in an availability statement"


# ── 5. the inferential status the artefact actually declares ────────────────────────────────
def test_the_committed_artefact_declares_the_status_the_claims_assume():
    ep = json.loads((REPO / "docs" / "paper1_resource"
                     / "PAPER_A_ENDPOINT_PROPAGATION.json").read_text())
    declared = TS.status_from_dict(ep["resampling_design"]["inferential_status"])
    assert declared == STATUS
    assert TS.validate_inferential_status(declared) == []


# ── 6. self-check finding: how complete is the taxonomy, really? ─────────────────────────────
#
# After the round-11 remediation merged, twenty FRESH paraphrases were tried against the rules —
# none from the review, none from the suite above. SEVENTEEN passed. The classes added since close
# nineteen of the twenty, and the twentieth is left failing on purpose: a keyword taxonomy catches
# what someone thought of, and pinning the measurement is more honest than pretending the list is
# closed. The reviewer brief carries this number.
_FRESH_PARAPHRASES = [
    "The mechanistic model buys us very little.",
    "The gain is not worth having.",
    "The improvement is slight.",
    "The advantage is negligible in practice.",
    "Any advantage is too small to matter.",
    "The model barely improves on the comparator.",
    "The difference is trivial.",
    "The comparator does just as well.",
    "The comparator is every bit as good.",
    "There is little to choose between them.",
    "The mechanistic model is not worth the extra complexity.",
    "For practical purposes the two are interchangeable.",
    "The benefit is vanishingly small.",
    "The model's edge is slim.",
    "Both approaches deliver similar accuracy.",
    "The mechanism contributes almost nothing.",
    "The improvement is marginal at best.",
    "The two arms are on a par.",
    "Skill gains were minor.",
]


@pytest.mark.parametrize("sentence", _FRESH_PARAPHRASES)
def test_fresh_magnitude_paraphrases_are_prohibited(sentence):
    assert CP.scan(sentence, STATUS), "FALSE GREEN: %r" % sentence


def test_the_taxonomy_is_known_to_be_incomplete():
    """Recorded rather than hidden. `much of a muchness` is an ordinary English way to assert
    equivalence and no rule matches it — kept as a standing reminder that the phrase list is a
    backstop, and the load-bearing defence is the positive assertion contract plus generated text."""
    assert CP.scan("The two predictors are much of a muchness.", STATUS) == [], (
        "if this now fails, the taxonomy grew — update the brief's stated coverage rather than "
        "deleting the test")


@pytest.mark.parametrize("sentence", [
    # The new classes must not fire on ordinary language, including the paper's own.
    "The held-out error stays modest under either estimand.",
    "A modest absolute error is reported at the matched endpoint.",
    "Records were matched by variety, temperature, and pressure.",
    "The 40 g upper sensitivity bound was a small positive value.",
    "No practical margin was predeclared.",
    "This analysis does not establish superiority.",
    "The observed pooled-MAPE difference was −0.394 percentage points.",
    "Comparable datasets were used in both campaigns.",
    "The design matched conditions across grinds.",
])
def test_the_new_magnitude_rules_do_not_fire_on_ordinary_language(sentence):
    assert CP.scan(sentence, STATUS) == [], sentence


# ── 7. the falsifiable acceptance criterion (post-round-12 stopping rule) ────────────────────
#
# Rounds 10, 11 and 12 each found the same defect class live in reader-facing text, and each was
# closed by rewriting sentences until no reviewer objected. That acceptance test has no end state:
# "does this wording overclaim?" is a judgement, and the next reader has different judgement. Round
# 11 replaced "small" with "less than half a percentage point"; round 12 objected to that phrase.
#
# This is the replacement. The scientific requirement was always SYMMETRIC — an uncalibrated range
# establishes neither that the advantage is reproducible or useful, nor that it is absent. One-sided
# caution is exactly how "no resolvable skill" survived four rounds: it reads as modesty while
# leaving an absence verdict standing.
#
# A surface either says both or it does not. Finite, checkable, and it found three surfaces
# one-sided the first time it ran — including the ABSTRACT and the editor significance paragraph.

def test_every_load_bearing_surface_states_both_directions():
    """The criterion itself: not 'no reviewer objects', but 'both directions are present'."""
    assert all("symmetric_non_establishment" in props
               for props in CP.SURFACE_ASSERTIONS.values()), \
        "a claim surface that does not require symmetry can drift back to one-sided caution"
    assert C._claim_policy() == []


@pytest.mark.parametrize("one_sided", [
    # Each of these disclaims the ADVANTAGE and says nothing about absence. Each is the shape the
    # abstract, the editor significance paragraph and §8 Conclusions actually had.
    "These are uncalibrated sensitivity ranges with no predeclared margin, so they do not establish "
    "whether the advantage is reproducible or useful.",
    "The ranges do not establish whether that gain is reproducible or practically useful.",
    "Within-campaign holdouts do not by themselves establish useful transfer of the extraction rate.",
    "This analysis does not establish superiority.",
])
def test_one_sided_caution_does_not_satisfy_the_criterion(one_sided):
    assert not CP.ASSERTION_BY_ID["symmetric_non_establishment"].present_in(one_sided), \
        "FALSE GREEN: one-sided non-establishment accepted as symmetric"


@pytest.mark.parametrize("symmetric", [
    "…they establish neither that the advantage is reproducible or useful nor that it is absent.",
    "…they determine neither a comparator decision about the observed difference nor its absence.",
    "Uncalibrated ranges support no superiority, equivalence or absence decision.",
    "…this analysis does not establish whether the difference is reproducible or practically "
    "useful, and it does not establish that the difference is absent.",
])
def test_symmetric_statements_satisfy_the_criterion(symmetric):
    assert CP.ASSERTION_BY_ID["symmetric_non_establishment"].present_in(symmetric)


def test_the_symmetric_form_also_satisfies_no_decision_claimed():
    """It entails it — a surface that upgrades to symmetry must not fail for losing the weaker
    phrasing it replaced."""
    text = ("…they establish neither that the advantage is reproducible or useful nor that it is "
            "absent.")
    assert CP.ASSERTION_BY_ID["no_decision_claimed"].present_in(text)


@pytest.mark.parametrize("surface", sorted(CP.SURFACE_ASSERTIONS))
def test_removing_symmetry_from_any_surface_fails(surface):
    """Non-vacuity on the REAL text of every governed surface."""
    from tools import paper_a_consistency as CC
    from tools import paper_a_front_matter as FMB
    from tools import paper_a_transfer_text as TTX

    fm = FMB.load()
    sources = {
        "abstract": FMB._one_line(fm["abstract"]),
        "editor_significance": FMB._one_line(fm["editor_significance"]),
        "cover_letter": CC._read(CC.COVER_LETTER),
        "highlights": CC._read(CC.HIGHLIGHTS),
        "figure3_caption": CC._upload_caption(3),
        "conclusion": CC._section(CC._read(CC.CONVERSION), "## 8. Conclusions"),
        "results_headline": TTX.extract_block(CC._read(CC.CONVERSION),
                                              "paper-a:transfer-headline"),
        "endpoint_synthesis": TTX.extract_block(CC._read(CC.CONVERSION),
                                                "paper-a:transfer-endpoint-reading"),
        "supplement_reading": TTX.extract_block(CC._read(CC.SUPPLEMENT),
                                                "paper-a:transfer-endpoint-table-supp"),
    }
    text = sources[surface]
    assert CP.missing_assertions(text, surface) == [], surface

    stripped = text
    for carrier in CP.ASSERTION_BY_ID["symmetric_non_establishment"].any_of:
        stripped = re.sub(re.escape(carrier), "", stripped, flags=re.I)
    assert stripped != text, "%s carries no symmetry phrasing at all" % surface
    assert any("symmetric_non_establishment" in m
               for m in CP.missing_assertions(stripped, surface)), \
        "FALSE GREEN: %s survived losing every symmetric carrier" % surface

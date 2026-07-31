"""Round-12 review: every focused adversarial probe, as a permanent regression.

The round-12 reviewer supplied `PAPER_1_ROUND_12_FOCUSED_PROBES.txt` — executable counterexamples
rather than assertions about the code. This module is that file, turned into tests, before any
behaviour was changed. Each one reproduced a false green (or a false red) at commit `4adbe4a`.

The pattern the round-12 review is really about is worth stating once, because it is the fourth
round it has appeared in: **a mechanism that describes more than it does.**

  * the generator's own docstring said the sentence "now says exactly" that usefulness is
    unestablished, and the sentence it emitted was "The observed advantage is therefore small";
  * `_VERIFIED` was documented as making the verified status unforgeable, and it is an ordinary
    module attribute anyone can import;
  * `source_schema` said a float could be converted "through `repr` to recover [the token]
    exactly", which is impossible once two decimal tokens map to one binary float;
  * `Assertion.present_in` was called positive proposition coverage and is a substring test.

Tests are grouped by the probe section they come from, and every expectation is the reviewer's.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import claim_policy as CP  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402

STATUS = TS.TRANSFER_INFERENTIAL_STATUS

MANUSCRIPT = REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
DRAFT = REPO / "docs" / "PAPER_A_DRAFT.md"


def _flat(path: pathlib.Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


# ── [1] and P0-1: the live wording, pinned verbatim ─────────────────────────────────────────
#
# These four were IN the shipped manuscript at the reviewed commit while the scanner reported zero
# problems on all six surfaces. The first is emitted by the authoritative generator itself.
LIVE_ROUND_12_WORDING = [
    "The observed advantage is therefore small.",
    "consistent with the small held-out skill above",
    "only −0.394 percentage points",
    "well under one percentage point",
]


@pytest.mark.parametrize("sentence", LIVE_ROUND_12_WORDING)
def test_the_live_round12_wording_is_prohibited(sentence):
    assert CP.scan(sentence, STATUS), "FALSE GREEN: %r" % sentence


@pytest.mark.parametrize("path", [MANUSCRIPT, DRAFT], ids=["manuscript", "draft"])
@pytest.mark.parametrize("sentence", LIVE_ROUND_12_WORDING)
def test_the_live_round12_wording_is_absent_from_both_manuscripts(path, sentence):
    assert sentence not in _flat(path), "%s still contains %r" % (path.name, sentence)


@pytest.mark.parametrize("sentence", [
    # Realistic copy-edits of the same verdict: adverb insertion, hyphenation, head-noun
    # substitution, voice. The review asks for the policy outcome to be stable across these.
    "The observed advantage is therefore small.",
    "The observed advantage is still small.",
    "The observed advantage is nonetheless small.",
    "The model has a small held-out advantage.",
    "The model has a small held-out skill.",
    "a small cross-grind gain",
    "The difference is small.",
    "The effect is small.",
    "The increment is small.",
    "The contrast is small.",
    "Only −0.394 percentage points separate them.",
    "The gap is well under one percentage point.",
    "The gap is well below one percentage point.",
])
def test_magnitude_verdicts_survive_ordinary_copy_editing(sentence):
    assert CP.scan(sentence, STATUS), "FALSE GREEN: %r" % sentence


# ── [1] and P1-2: ordinary absence/equivalence/magnitude paraphrases ─────────────────────────
@pytest.mark.parametrize("sentence", [
    "The model has no advantage.",
    "There is no advantage.",
    "The model shows no advantage.",
    "The model provides no benefit.",
    "The model is no better than the comparator.",
    "The comparator is just as accurate.",
    "The observed gain is minuscule.",
    "The difference is negligible.",
    "The model has a tiny held-out advantage.",
])
def test_ordinary_paraphrases_are_prohibited(sentence):
    assert CP.scan(sentence, STATUS), "FALSE GREEN: %r" % sentence


# ── [2] and P1-1: clause governance — false negatives ────────────────────────────────────────
#
# A disclaimer in a fronted concessive, a causal continuation, an appositive continuation or a comma
# splice must not license the verdict in the other unit. "Same heuristic clause" is not grammatical
# scope, and every one of these returned clean.
@pytest.mark.parametrize("text", [
    "Although this analysis does not establish superiority, the model outperforms the comparator.",
    "While this analysis does not establish superiority, the model outperforms the comparator.",
    "Whereas this analysis does not establish equivalence, the models are essentially the same.",
    "Though we make no claim of equivalence, the arms are equivalent.",
    "This analysis does not establish superiority because the model outperforms the comparator.",
    "This analysis cannot determine equivalence, meaning the models are essentially the same.",
    "We do not claim equivalence in formal terms, the models are essentially the same in practice.",
])
def test_a_disclaimer_in_another_grammatical_unit_does_not_license_a_verdict(text):
    assert CP.scan(text, STATUS), "FALSE GREEN: %r" % text


# ── [2] and [11] and P1-1: clause governance — false positives ──────────────────────────────
#
# The other half of the same defect. These say exactly what the policy requires and were REJECTED,
# because the epistemic frame was not on the fixed safe-construction list. A gate that punishes
# correct prose teaches authors to write to the scanner.
@pytest.mark.parametrize("text", [
    "Whether the model outperforms the comparator remains unresolved.",
    "Whether the model outperforms the comparator is not established.",
    "The data are insufficient to determine whether the model outperforms the comparator.",
    "It remains unclear whether the model outperforms the comparator.",
    "The analysis leaves unresolved whether the model outperforms the comparator.",
    "The data do not permit us to conclude that the model outperforms the comparator.",
    "We cannot say whether the models are equivalent.",
    "It is an open question whether the model outperforms the comparator.",
])
def test_ordinary_non_establishment_prose_is_permitted(text):
    assert CP.scan(text, STATUS) == [], "FALSE RED: %r" % text


# ── [3]: the active surfaces must be clean, and non-vacuously so ────────────────────────────
def test_every_active_surface_is_clean():
    from tools import paper_a_consistency as C

    assert C._claim_policy() == []


# ── [10] and P1-3: positive coverage must test propositions, not substrings ─────────────────
#
# A surface can DENY the required result, QUOTE it as rejected wording, or MENTION it
# metalinguistically, and `present_in` certifies it as carrying the proposition.
_NEGATED_HIGHLIGHTS = (
    "Observed pooled error was not 0.394 points lower than a level-only comparator\n"
    "These are not uncalibrated ranges\n"
    "The phrase 'support no superiority' is not this paper's conclusion\n")

_QUOTED_CAPTION = (
    "**Figure 3.** This caption must include the strings '−0.394 pp', 'uncalibrated ranges', "
    "'does not establish whether', and 'alone does not establish' before it may be uploaded.")

_CONDITIONAL_ABSTRACT = (
    "If the difference were −0.394 percentage points, and if these were uncalibrated ranges, the "
    "analysis would not establish whether the advantage is reproducible, and endpoint accuracy "
    "alone does not establish transfer — but none of that is what we found.")


@pytest.mark.parametrize("surface,text", [
    ("highlights", _NEGATED_HIGHLIGHTS),
    ("figure3_caption", _QUOTED_CAPTION),
    ("abstract", _CONDITIONAL_ABSTRACT),
], ids=["negated", "quoted", "conditional"])
def test_a_negated_or_quoted_mention_does_not_satisfy_a_proposition(surface, text):
    missing = CP.missing_assertions(text, surface)
    assert missing, "FALSE GREEN: %s certified as carrying its propositions by %s mention" % (
        surface, "negated/quoted/conditional")


def test_the_genuine_surfaces_still_satisfy_their_propositions():
    """The polarity fix must not break the real thing — non-vacuity in the other direction."""
    from tools import paper_a_consistency as C

    assert CP.missing_assertions(C._read(C.HIGHLIGHTS), "highlights") == []
    assert CP.missing_assertions(C._upload_caption(3), "figure3_caption") == []


# ── [4] and P1-4: the construction token is importable ──────────────────────────────────────
def test_importing_the_sentinel_does_not_unlock_decision_language():
    """`_VERIFIED` is an ordinary module attribute. The docstring said direct construction was
    impossible; it is one import away."""
    from puckworks.paper_a import inferential_evidence as IE
    from tests import helpers_inferential_evidence as H

    genuine = H.synthetic_equivalence_status()
    token = getattr(IE, "_VERIFIED", None)
    if token is None:                                     # the sentinel was removed entirely
        return
    try:
        forged = IE.VerifiedInferentialStatus(
            declared=genuine.declared, evidence=genuine.evidence, procedure=genuine.procedure,
            estimand=genuine.estimand, _token=token)
    except Exception:
        return                                            # construction refused: also acceptable
    # Granting nothing may take either shape: an empty set, or a refusal to treat an object as
    # provenance at all. Both mean the sentinel bought the caller no permission.
    try:
        assert CP.granted(forged) == set(), \
            "FALSE GREEN: possession of an importable sentinel unlocked decision language"
    except TypeError:
        # Refusing to treat the object as provenance at all is the stronger outcome, and it must
        # hold at the scan boundary too — the forged status must not be usable as a status.
        with pytest.raises(TypeError):
            CP.scan("The model is equivalent to the comparator.", forged)
        return
    assert CP.scan("The model is equivalent to the comparator.", forged)


# ── [5] and P1-5: evidence semantics and chronology ─────────────────────────────────────────
def test_a_procedure_with_empty_semantics_cannot_register():
    import dataclasses

    from puckworks.paper_a import inferential_evidence as IE
    from tests import helpers_inferential_evidence as H

    for field in ("cluster_unit", "required_estimand_id", "implementation_id"):
        spec = dataclasses.replace(H.procedure(), **{field: ""})
        assert spec.problems(), "FALSE GREEN: empty %s registered" % field
        with pytest.raises(ValueError):
            IE.register({}, spec)


def test_the_decision_interval_must_come_from_the_hashed_result():
    """The probe hashed a result whose interval was [-2.0, 2.0] — which does NOT support
    equivalence — while the evidence record separately claimed (-0.30, 0.20), which does. Both
    digests matched and verification returned no problems."""
    from tests import helpers_inferential_evidence as H

    status, problems = H.verify_detached_result()
    assert status is None, "FALSE GREEN: a decision derived from an interval the result contradicts"
    assert problems


def test_a_margin_protocol_written_after_the_result_is_rejected():
    """A different hash proves identity, not chronology."""
    from tests import helpers_inferential_evidence as H

    status, problems = H.verify_post_result_protocol()
    assert status is None, "FALSE GREEN: a margin protocol created after the result"
    assert problems


# ── [6] and P1-7: raw coordinate identity through the PRODUCTION loader ─────────────────────
@pytest.mark.parametrize("a,b", [
    ("93.4000400000000001", "93.4000400000000002"),
    ("10.0000000000000001", "10.0000000000000002"),
])
def test_distinct_source_tokens_survive_the_production_loader(tmp_path, a, b):
    """`_typed_rows*` calls `float()` on every parseable cell before `source_schema` sees it, so
    `repr()` cannot "recover the source token exactly" — the information is already gone.

    Exercised end-to-end through the production loader, not by calling `parse_coordinate` directly,
    because the direct call is precisely the path that does not reproduce the defect.
    """
    from puckworks import data as D
    from puckworks.paper_a import source_schema as SS

    csv = tmp_path / "coords.csv"
    csv.write_text(
        "sample,variety,T_degC,p_bar,granulometry,on_grid,CF,TR,5CQA\n"
        "X1,Arabica,%s,9,C,False,1.0,1.0,1.0\n"
        "X2,Arabica,%s,9,C,False,1.0,1.0,1.0\n" % (a, b), encoding="utf-8")

    rows = D._typed_rows_hashskip(csv)
    keys = [SS.parse_row(r).condition_key.cluster_id for r in rows]
    assert keys[0] != keys[1], (
        "two distinct source conditions collapsed into one cluster id (%r); a clustered range "
        "depends entirely on which outcomes move together" % keys[0])


# ── [7] and P1-8A: raw HTML destinations ────────────────────────────────────────────────────
@pytest.mark.parametrize("html,target", [
    ('<a href=docs/internal/review.md>the analysis</a>', "docs/internal/review.md"),
    ('<img src=docs/internal/figure.png alt="figure">', "docs/internal/figure.png"),
    ('<a href=docs%2Finternal%2Freview.md>the analysis</a>', "docs/internal/review.md"),
    ('<img srcset="docs/internal/figure.png 1x" alt="figure">', "docs/internal/figure.png"),
    ('<video poster="docs/internal/review.png"></video>', "docs/internal/review.png"),
    ('<a href="docs/internal/review.md">the analysis</a>', "docs/internal/review.md"),
])
def test_every_raw_html_destination_is_extracted(html, target):
    from tools import paper_a_consistency as C

    found = [C._normalise_target(t) for _ln, t in C._link_targets(html)]
    assert any(target in f for f in found), (html, found)


# ── [8] and P1-8B/C: verbatim comments and the metadata exemption ────────────────────────────
@pytest.mark.parametrize("attr,injected,expect", [
    ("HIGHLIGHTS", "<!-- The second review retained a producer identifier. -->", "review"),
    ("HIGHLIGHTS", "<!-- generated from a private producer identifier -->", "producer identifier"),
    ("UPLOAD_CAPTIONS", "<!-- An earlier version was wrong. -->", "earlier version"),
])
def test_all_leakage_classes_apply_to_comments_in_verbatim_uploads(attr, injected, expect):
    """Those files are uploaded as-is, so a comment reaches the editor in the source even though no
    reader sees it rendered. Only the path rule was being applied."""
    from tests.helpers_round12 import scan_one

    problems = scan_one(attr, injected)
    assert any(expect in p for p in problems), (injected, problems[:3])


@pytest.mark.parametrize("injected,expect", [
    ("Funding is not yet supplied. See `docs/internal/review.md` for the scientific analysis.",
     "docs/internal/review.md"),
    ("Funding is not yet supplied. See [the scientific analysis](docs/internal/review.md).",
     "docs/internal/review.md"),
    ('Funding is not yet supplied. <a href=docs/internal/review.md>the analysis</a>',
     "docs/internal/review.md"),
])
def test_the_metadata_exemption_does_not_cover_unrelated_leaks(injected, expect):
    """The exemption is described as keyed narrowly to the placeholder and is implemented per
    paragraph and per source line, so anything sharing a paragraph with it is exempt too."""
    from tests.helpers_round12 import scan_one

    problems = scan_one("CONVERSION", injected)
    assert any(expect in p for p in problems), (injected, problems[:3])


def test_a_genuine_unsupplied_metadata_placeholder_is_still_exempt():
    """Narrowing the exemption must not break the thing it exists for."""
    from tools import paper_a_consistency as C

    assert C._placeholders_and_process_language() == []


# ── [9] and P2-2: caption length ────────────────────────────────────────────────────────────
def test_figure_3_is_an_editor_usable_caption():
    from tools import paper_a_consistency as C

    caption = C._upload_caption(3)
    words = len(caption.split())
    assert words <= 210, "Figure 3 is a %d-word mini-review; the review asks for 150-200" % words
    # …while still carrying everything the review requires it to keep.
    for required in ("44", "132", "8.44", "8.83", "−0.394", "62 of 132"):
        assert required in caption, required


# ── P2-1: producer stems ────────────────────────────────────────────────────────────────────
def test_the_caption_mapping_validates_producer_stems():
    from tools import paper_a_figure_captions as FC

    entries = FC.captions()
    assert all(len(e) == 3 for e in entries), \
        "the heading regex captures the stem and extraction discards it"
    stems = [stem for _n, stem, _c in entries]
    assert len(set(stems)) == len(stems), "producer stems must be unique"


# ── P2-4: the duplicated phrase ─────────────────────────────────────────────────────────────
@pytest.mark.parametrize("path", [MANUSCRIPT, DRAFT], ids=["manuscript", "draft"])
def test_the_comparator_ladder_phrase_is_not_duplicated(path):
    assert "ladder** (in-sample comparator ladder)" not in _flat(path)
    assert "ladder (in-sample comparator ladder)" not in _flat(path)

"""What Paper A is allowed to say, given what its analysis is able to decide.

Round-10 P0-1, the submission blocker. The paper stated, correctly and prominently, that its ranges
are fixed-predictor clustered percentile **sensitivity** ranges with no calibrated coverage, and that
it makes "no claim of statistical distinguishability, non-distinguishability or equivalence" from
them. It then concluded — in the abstract, the editor significance paragraph, the principal Results
headline, the endpoint synthesis, the cover letter and the standalone caption map — that the
mechanistic model supplied **"no resolvable skill"**.

Both cannot be true. The observed contrast at 40 g favours the model by 0.394 pp, every secondary
scheme's range is wholly negative, and the 38 g primary range excludes zero on the favourable side.
An uncalibrated range cannot establish that the model HAS reproducible incremental skill; the same
range cannot establish that it has NONE, and without a predeclared practical margin nothing here can
call the difference negligible. "No resolvable skill" is a property-level negative verdict, and no
declared analysis produces it.

The error is easy to ship because it sounds cautious. A reviewer scanning for overclaiming reads
"no skill" as modesty. So the fix is not a wording pass — the wording would drift back. There are
two mechanisms here:

  1. :func:`scan` — given the analysis's declared :class:`~puckworks.paper_a.transfer_semantics.
     InferentialStatus`, every phrase that presupposes a decision the analysis cannot make is
     prohibited in reader-facing text. If a future analysis genuinely earns one of those decisions,
     it declares it in the status object and the corresponding phrase class unlocks. Explicit
     disclaimers ("we make no claim of equivalence") are recognised and permitted: the paper must be
     able to say what it is not claiming.

  2. :data:`SURFACE_ASSERTIONS` — the propositions the accepted claim is made of, and which surface
     must carry which. This is the positive half. Prohibiting "no skill" is not enough if a surface
     then says nothing about the limits of the evidence, or drops the sign of the difference.

Pure and dependency-free apart from :mod:`transfer_semantics`, so the consistency checker, the text
generator and the tests all reach the same verdicts.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from puckworks.paper_a import transfer_semantics as TS

# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1. Prohibited decision language
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: Which property of the declared status a phrase class presupposes.
ABSENCE = "absence-of-skill"
EQUIVALENCE = "equivalence"
SUPERIORITY = "superiority"
NONINFERIORITY = "non-inferiority"
CALIBRATED = "calibrated coverage"
MARGIN = "a predeclared practical margin"


@dataclass(frozen=True)
class ClaimRule:
    """One phrase class, and the decision it presupposes."""

    id: str
    pattern: re.Pattern
    presupposes: str
    why: str


def _rx(pattern: str) -> re.Pattern:
    return re.compile(pattern, re.I)


#: The rules. Patterns are deliberately ASSERTION-shaped: they match a verdict, not a mention.
#: "non-distinguishability" (the noun, used in the paper's own disclaimer) must not fire the
#: "non-distinguishable" rule, which is why that pattern ends at a word boundary after `-able`.
RULES: tuple[ClaimRule, ...] = (
    ClaimRule(
        "no_resolvable_skill",
        _rx(r"\bno\s+resolvable\s+(?:skill|gain|advantage|benefit|improvement)\b"),
        ABSENCE,
        "a categorical absence verdict; an uncalibrated sensitivity range cannot establish that "
        "incremental skill is absent any more than it can establish that it is present"),
    ClaimRule(
        "adds_no_skill",
        _rx(r"\b(?:add|adds|adding|added|supply|supplies|supplied|supplying|provide|provides|"
            r"provided|offer|offers|offered)\s+no\s+(?:resolvable\s+|meaningful\s+|useful\s+)?"
            r"(?:incremental\s+)?(?:skill|gain|advantage|benefit)\b"),
        ABSENCE,
        "asserts absence of skill as a property of the model rather than a limit of the evidence"),
    ClaimRule(
        "did_not_supply_skill",
        _rx(r"\bdid\s+not\s+(?:supply|provide|add|deliver)\s+(?:any\s+)?(?:resolvable\s+|"
            r"meaningful\s+|useful\s+)?(?:incremental\s+)?(?:skill|gain|advantage)\b"),
        ABSENCE,
        "same verdict in the past tense; what was not established is the SKILL, not the analysis"),
    ClaimRule(
        "no_skill_bare",
        _rx(r"\b(?:has|have|had|shows?|showed|demonstrat\w+)\s+no\s+"
            r"(?:resolvable\s+|incremental\s+)?skill\b"),
        ABSENCE,
        "asserts absence of skill directly"),
    ClaimRule(
        "unresolved_throughout",
        _rx(r"\bunresolved\s+throughout\b"),
        ABSENCE,
        "attaches 'unresolved' to the benchmark as a property rather than to this analysis; say "
        "what THIS analysis does not determine"),
    ClaimRule(
        "is_equivalent",
        _rx(r"\b(?:is|are|was|were|be|being|proved|proven|shown\s+to\s+be)\s+"
            r"(?:statistically\s+|practically\s+)?equivalent\b"),
        EQUIVALENCE,
        "an equivalence verdict requires a predeclared margin and a calibrated procedure"),
    ClaimRule(
        "no_meaningful_difference",
        _rx(r"\bno\s+(?:meaningful|material|real|practical)\s+difference\b"),
        EQUIVALENCE,
        "an equivalence verdict in other words"),
    ClaimRule(
        "non_distinguishable",
        _rx(r"\b(?:statistically\s+)?(?:indistinguishable|non-?distinguishable)\b"),
        CALIBRATED,
        "a distinguishability verdict requires calibrated coverage"),
    ClaimRule(
        "statistical_significance",
        _rx(r"\bstatistically\s+(?:significant|insignificant|non-?significant)\b"),
        CALIBRATED,
        "no calibrated procedure or test is specified anywhere in the transfer analysis"),
    ClaimRule(
        "significantly_better_or_worse",
        _rx(r"\bsignificantly\s+(?:better|worse|outperform\w*|lower|higher)\b"),
        CALIBRATED,
        "'significantly' reads as a test result; the analysis performs none"),
    ClaimRule(
        "practically_negligible",
        _rx(r"\bpractically\s+(?:negligible|irrelevant|meaningless)\b"
            r"|\bno\s+practically\s+useful\s+(?:improvement|gain|advantage)\b"),
        MARGIN,
        "negligibility is a decision against a margin, and no margin is predeclared"),
    ClaimRule(
        "outperforms",
        _rx(r"\b(?:outperform\w*|beats|superior\s+to)\b"),
        SUPERIORITY,
        "a superiority verdict; the observed advantage is small and its reproducibility is not "
        "established"),
    ClaimRule(
        "non_inferior",
        _rx(r"\bnon-?inferior\b"),
        NONINFERIORITY,
        "a non-inferiority verdict requires a predeclared margin"),
    # An independent second review of the same commit asked for the close variants that turn
    # non-establishment back into positive absence. Each of these is a different grammatical route to
    # the retired verdict, and "no incremental skill" is the one most likely to be reached for by
    # someone editing the corrected wording toward brevity.
    ClaimRule(
        "no_incremental_skill",
        _rx(r"\bno\s+(?:incremental|mechanistic|resolvable|measurable|detectable|real)\s+"
            r"(?:skill|advantage|gain|benefit|transfer)\b"),
        ABSENCE,
        "asserts absence as a property; what the analysis lacks is the ability to decide either way"),
    ClaimRule(
        "no_difference",
        _rx(r"\bno\s+difference\b(?!\s+(?:between\s+)?(?:in|is)\s+established)"),
        EQUIVALENCE,
        "the point estimate is not zero and is negative at every endpoint; "
        "\"no difference\" is both an equivalence verdict and factually wrong here"),
    ClaimRule(
        "no_effect",
        _rx(r"\bno\s+(?:effect|signal)\b"),
        ABSENCE,
        "an absence verdict"),
    ClaimRule(
        "at_least_as_good",
        _rx(r"\b(?:at\s+least\s+as\s+good\s+as|no\s+worse\s+than)\b"),
        NONINFERIORITY,
        "a non-inferiority verdict in plain words"),
    ClaimRule(
        "comparable_performance",
        _rx(r"\b(?:performs?|performed|performing)\s+comparably\b|\bcomparable\s+performance\b"),
        EQUIVALENCE,
        "an equivalence verdict in plain words"),
    # ── round-11 P0-1/P1-1 ──────────────────────────────────────────────────────────────────
    # The retired verdict came back by PARAPHRASE. Round 10 removed "no resolvable skill" and the
    # taxonomy above was built around absence, equivalence, distinguishability and superiority — so
    # "adds little", "incremental skill is small" and "nearly matched" walked straight through it,
    # on five reader-facing surfaces, with the scanner reporting zero problems. These are
    # practical-MAGNITUDE verdicts: they say the increment is too small to matter. That is a decision
    # against a margin, and no margin is predeclared.
    ClaimRule(
        "adds_little",
        # Only where "little" is the VALUE contributed: "adds little numerical cost" is a statement
        # about the method's expense, not about the model's worth.
        _rx(r"\b(?:add|adds|adding|added|offer|offers|offering|offered|provide|provides|providing|"
            r"provided|contribute|contributes|contributing|contributed|bring|brings|bringing)\s+"
            r"(?:only\s+)?(?:very\s+)?little\b"
            r"(?=\s*(?:[,.;:)]|$)|\s+(?:to|over|beyond|above|relative|of|more|extra|additional|"
            r"incremental|new|skill|benefit|value|gain|advantage|information|evidence)\b)"),
        MARGIN,
        "a practical-magnitude verdict: how little is 'little' is a decision against a margin, and "
        "no margin is predeclared — state the observed difference instead"),
    ClaimRule(
        "small_incremental_value",
        # Both orders. Attached to a VALUE noun, so "a small positive upper bound" and "a small
        # sample" are untouched — the adjective has to be qualifying the increment itself.
        # Up to two intervening modifiers, because "only a small OBSERVED gain" is the same verdict
        # with one word wedged in, and that is exactly the edit a wording pass makes.
        _rx(r"\b(?:only\s+)?(?:very\s+)?(?:small|minimal|marginal|negligible|slight|meagre|meager|"
            r"trivial|tiny)\s+(?:\w+\s+){0,2}?(?:incremental\s+)?"
            r"(?:skill|gain|benefit|advantage|improvement)\b"
            r"|\b(?:small|minimal|marginal|negligible|slight)\s+(?:\w+\s+){0,2}?"
            r"incremental\s+value\b"
            r"|\b(?:incremental\s+|mechanistic\s+|predictive\s+)?"
            r"(?:skill|gain|benefit|advantage|improvement)\b[^.;:]{0,60}?"
            r"\b(?:is|are|was|were|remains?|remained)\s+"
            r"(?:only\s+)?(?:very\s+)?(?:small|minimal|marginal|negligible|slight|trivial|tiny)\b"),
        MARGIN,
        "'small' is a practical-magnitude decision unless a predeclared margin says what small "
        "means; give the observed number and its sign"),
    ClaimRule(
        "nearly_matched",
        # Not matched RECORDS, matched CONDITIONS or a matched-endpoint design — those are the
        # paper's own methodology, and the estimand is built on them.
        _rx(r"\b(?:nearly|essentially|effectively|virtually|almost|closely|near-?ly)\s+"
            r"match(?:ed|es|ing)?\b"
            r"(?!\s+(?:records?|samples?|pairs?|conditions?|endpoints?|windows?|observations?|"
            r"designs?|cups?|data|grinds?|varieties|filters?))"),
        EQUIVALENCE,
        "an equivalence-adjacent verdict: 'nearly matched' asserts the two arms are close enough "
        "to be treated as the same, which requires a margin and calibrated coverage"),
    ClaimRule(
        "essentially_same",
        _rx(r"\b(?:essentially|effectively|virtually|practically|basically|for\s+all\s+practical\s+"
            r"purposes)\s+(?:the\s+)?(?:same|identical|equal)\b"
            r"|\b(?:is|are|was|were)\s+essentially\s+identical\b"),
        EQUIVALENCE,
        "an equivalence verdict in plain words"),
    ClaimRule(
        "within_noise",
        _rx(r"\bwithin\s+(?:the\s+)?noise\b|\bindistinguishable\s+from\s+noise\b"
            r"|\bwithin\s+(?:the\s+)?margin\s+of\s+error\b|\bin\s+the\s+noise\b"),
        CALIBRATED,
        "'within noise' is a verdict against a noise model this analysis does not define, let alone "
        "calibrate"),
    # A self-check after the round-11 remediation merged tried twenty FRESH paraphrases against the
    # rules above — none of them from the review, none from the test suite. Seventeen passed.
    #
    # That is the honest shape of a keyword taxonomy: it catches what someone thought of. The classes
    # below close the most natural of those, but the result to carry forward is the measurement, not
    # the patch — the taxonomy is a backstop, and the load-bearing defence is the positive assertion
    # contract on each surface plus generated text for the central claims. The reviewer brief now
    # says so with the number attached.
    ClaimRule(
        "worth_little",
        _rx(r"\b(?:buys?|bought|gains?|gained|wins?|won)\s+(?:us\s+|you\s+|the\s+\w+\s+)?"
            r"(?:very\s+)?little\b"
            r"|\bnot\s+worth\s+(?:having|the\s+\w+|it)\b"
            r"|\blittle\s+to\s+choose\s+between\b"
            r"|\b(?:contributes?|adds?|offers?)\s+(?:almost|next\s+to|virtually)\s+nothing\b"
            r"|\btoo\s+small\s+to\s+matter\b"
            r"|\bvanishingly\s+small\b"),
        MARGIN,
        "a practical-worth verdict: whether an increment is 'worth having' is a decision against a "
        "margin, and none is predeclared"),
    ClaimRule(
        "barely_improves",
        _rx(r"\b(?:barely|hardly|scarcely|only\s+just)\s+"
            r"(?:improve\w*|better|beat\w*|outperform\w*|exceed\w*|above)\b"),
        SUPERIORITY,
        "a superiority verdict softened by an adverb is still a superiority verdict"),
    ClaimRule(
        "trivial_difference",
        _rx(r"\bdifference\s+is\s+(?:trivial|immaterial|inconsequential|unimportant)\b"
            r"|\b(?:trivial|immaterial|inconsequential)\s+difference\b"),
        MARGIN,
        "a practical-negligibility verdict about the difference itself"),
    ClaimRule(
        "just_as_good",
        _rx(r"\b(?:does|do|did|performs?|performed)\s+just\s+as\s+(?:well|good)\b"
            r"|\bevery\s+bit\s+as\s+(?:good|accurate|effective)\b"
            r"|\bon\s+a\s+par\s+with\b|\bon\s+a\s+par\b"
            r"|\b(?:are|is|were|was)\s+interchangeable\b"
            r"|\bfor\s+(?:all\s+)?practical\s+purposes\s+(?:the\s+two|they|both)\b"),
        EQUIVALENCE,
        "an equivalence verdict in plain words"),
    ClaimRule(
        "similar_performance",
        _rx(r"\b(?:similar|comparable|equivalent|matching)\s+"
            r"(?:accuracy|performance|error|skill|precision)\b"
            r"|\b(?:deliver|delivers|delivered|achieve|achieves|achieved|give|gives|gave)\s+"
            r"(?:similar|comparable)\s+\w+\b"),
        EQUIVALENCE,
        "an equivalence verdict; 'similar' is a judgement of closeness against an undeclared "
        "threshold"),
    ClaimRule(
        "minor_gain",
        _rx(r"\b(?:minor|slim|thin|modest)\s+(?:incremental\s+)?"
            r"(?:skill|gain|gains|benefit|advantage|edge|improvement|margin)\b"
            r"|\b(?:skill|gain|gains|benefit|advantage|edge)\s+(?:were|was|is|are)\s+"
            r"(?:minor|slim|thin)\b"),
        MARGIN,
        "the same practical-magnitude verdict with a different adjective"),
    ClaimRule(
        "no_practical_advantage",
        # "no practical MARGIN was declared" is a true statement about the protocol and must survive;
        # the noun set is deliberately restricted to the increment itself.
        _rx(r"\bno\s+(?:material|practical|meaningful|real|appreciable|discernible|worthwhile|"
            r"useful)\s+(?:advantage|benefit|gain|improvement|value)\b"),
        MARGIN,
        "a practical-negligibility verdict, which requires the margin the analysis never declared"),
)

#: A paper must be able to name the decision it is not making — "we make no claim of statistical
#: distinguishability, non-distinguishability or equivalence" is the sentence the round-10 review
#: praised, and a scanner that banned it would push authors toward silence about the limits instead
#: of clarity about them.
#:
#: Round-11 P1-1 replaced how that allowance works. It used to be a substring search over the 140
#: characters PRECEDING a hit, against a list that included `neither`, `without`, `is not`, `are
#: not`, `not a` and `reserve`. Those are fragments of ordinary scientific English, not disclaimers,
#: and proximity is not grammar. Every one of these passed:
#:
#:     The ranges are not confidence intervals. The model outperforms the comparator.
#:     We do not claim equivalence; the model is equivalent to the comparator.
#:     Without calibrated coverage, the model outperforms the comparator.
#:
#: The second is self-contradictory and the scanner returned it clean. The shape being rewarded is
#: exactly the one a careful paper produces: a limitations sentence, then an overstrong conclusion.
#:
#: A disclaimer is now recognised only when the non-establishment construction NAMES what is not
#: established and governs the matched term inside the same clause. Each pattern below is a verb
#: phrase; its span runs from the construction to the end of the clause, because that is how far
#: "does not establish …" reaches in English.
_SAFE_CONSTRUCTIONS: tuple[re.Pattern, ...] = tuple(_rx(p) for p in (
    r"\b(?:make|makes|making|made)\s+no\s+claims?\b",
    r"\bno\s+claims?\s+(?:of|to|about|is\s+made|are\s+made)\b",
    r"\b(?:do|does|did|would|can|could|cannot|can\s?not)\s+not\s+claim\b",
    r"\bcannot\s+claim\b",
    r"\b(?:do|does|did|would)\s+not\s+(?:establish|determine|demonstrate|show|resolve|decide|"
    r"support|licence|license|warrant|justify)\b",
    r"\bcannot\s+(?:establish|determine|demonstrate|show|resolve|decide|support|adjudicate|tell|"
    r"distinguish)\b",
    r"\b(?:is|are|was|were)\s+not\s+(?:established|determined|demonstrated|shown|resolved|"
    r"decided|supported)\b",
    r"\b(?:establish|establishes|established|determine|determines|determined|claim|claims|"
    r"claimed|support|supports|supported|decide|decides|decided)\s+neither\b",
    r"\bneither\s+establishes\b",
    r"\bnot\s+(?:by\s+itself|by\s+themselves|,?\s*by\s+itself,?)\s+(?:establish|evidence)\w*\b",
    r"\bwithout\s+(?:establishing|claiming|deciding|determining)\b",
    r"\bnot\s+be\s+read\s+as\b",
    r"\bmust\s+not\s+be\s+(?:read|taken|interpreted)\b",
    r"\bno\s+(?:superiority|non-?inferiority|equivalence|absence|practical-?usefulness|"
    r"usefulness)[^.;:]{0,80}?\bdecision\s+(?:is|was)\s+(?:made|claimed|supported)\b",
    r"\bsupports?\s+no\s+(?:superiority|non-?inferiority|equivalence|absence|practical)\b",
))

#: Where one adjudicable clause ends and the next begins.
#:
#: Round-11 P1-1 again: a disclaimer in a previous sentence, a previous clause, or on the far side of
#: a contrastive conjunction must not reach forward. `but`, `however` and `yet` REVERSE the sentence
#: they join — "the range is not calibrated, **but** the model outperforms the comparator" is an
#: assertion of superiority, and treating the first half as cover for the second inverts the meaning.
#:
#: The comma case is the subtle one. ", and the model outperforms …" opens a new finite clause with
#: its own subject, so an earlier "does not establish" no longer governs it; ", and does not
#: establish equivalence" continues the same subject and does. The determiner/pronoun list is what
#: distinguishes them, and it is deliberately explicit rather than a part-of-speech guess.
_CLAUSE_BOUNDARY = re.compile(
    r"(?<=[.?!])\s+"
    r"|\s*[;:]\s*"
    r"|\s*[—–]+\s*"
    r"|\s+(?:but|however|yet|nevertheless|nonetheless|whereas|although|though|while|despite|"
    r"notwithstanding)\s+"
    r"|\s*,\s+(?:and|or|but|yet|while)\s+(?=(?:the|this|that|these|those|it|they|we|its|their|"
    r"his|her|our|a|an)\b)",
    re.I)

#: Unicode punctuation a source file may carry, normalised so one rule matches both renderings.
_PUNCTUATION = {"‘": "'", "’": "'", "“": '"', "”": '"',
                "‐": "-", "‑": "-", "‒": "-", "­": ""}


def _flatten(text: str) -> str:
    """Collapse whitespace and Markdown emphasis so a phrase survives wrapping and bolding.

    ``**no resolvable skill**`` and a phrase split across two source lines must both be found: the
    round-10 P2-1 finding was a prohibited phrase that survived because the scanner read physical
    lines, and emphasis markers inside a phrase are the same class of bypass.
    """
    for bad, good in _PUNCTUATION.items():
        text = text.replace(bad, good)
    return re.sub(r"[*_`]+", "", " ".join(text.split()))


def iter_decision_clauses(text: str):
    """Split normalised text into the units a decision claim is adjudicated in.

    Deliberately deterministic and small rather than a general parser: its behaviour has to be
    explicable in a review, and every boundary it recognises is covered by a test.
    """
    for clause in _CLAUSE_BOUNDARY.split(_flatten(text)):
        clause = (clause or "").strip()
        if clause:
            yield clause


def find_non_establishment_spans(clause: str) -> list[tuple[int, int]]:
    """The ``(start, end)`` character spans in which a decision term is disclaimed, not asserted.

    A construction governs from where it starts to the end of its clause. Clause boundaries are what
    stop it governing the next assertion, which is the whole point of the round-11 correction.
    """
    return sorted((m.start(), len(clause)) for p in _SAFE_CONSTRUCTIONS
                  for m in p.finditer(clause))


def _governed(match: re.Match, spans) -> bool:
    """True when the match lies wholly inside a disclaimer's reach."""
    return any(start <= match.start() and match.end() <= end for start, end in spans)


def granted(status) -> set[str]:
    """The decision properties this status actually grants.

    Round-11 P1-2. A DECLARED :class:`~puckworks.paper_a.transfer_semantics.InferentialStatus`
    grants nothing, whatever its flags say. The reviewer hand-wrote an internally coherent status
    naming an "invented future procedure", it passed validation, and it unlocked "the model is
    equivalent to the comparator" — because the permission was a boolean somebody could type rather
    than a result somebody had to earn.

    Decision language now comes only from a
    :class:`~puckworks.paper_a.inferential_evidence.VerifiedInferentialStatus`, whose flags are
    computed by re-applying the registered decision rule to the observed interval. That type has no
    settable flag to fabricate.

    This is fail-closed on purpose: for Paper A it changes nothing, because the analysis makes no
    decision and asks for no unlock. It changes what a FUTURE author has to do.
    """
    from puckworks.paper_a.inferential_evidence import VerifiedInferentialStatus

    if not isinstance(status, VerifiedInferentialStatus):
        if isinstance(status, TS.InferentialStatus):
            return set()
        raise TypeError(
            "claim_policy needs an InferentialStatus or a VerifiedInferentialStatus, got %s; a "
            "mapping or a duck-typed stand-in is exactly the shape the round-11 fabrication took"
            % type(status).__name__)

    out = {name for name, ok in status.decision_flags.items() if ok}
    if status.coverage_calibrated:
        out.add(CALIBRATED)
    if status.practical_margin_pp is not None:
        out.add(MARGIN)
    return out


def prohibited_rules(status: TS.InferentialStatus) -> tuple[ClaimRule, ...]:
    """The rules that apply, i.e. those whose presupposition this analysis does not grant."""
    have = granted(status)
    return tuple(r for r in RULES if r.presupposes not in have)


def scan(text: str, status: TS.InferentialStatus, where: str = "") -> list[str]:
    """Return one problem per prohibited decision claim in ``text``. Empty means compliant.

    Adjudication is CLAUSE by clause. A rule fires unless a non-establishment construction in the
    same clause reaches the matched term; a limitations sentence next door does not license a verdict
    (round-11 P1-1).
    """
    label = ("%s: " % where) if where else ""
    rules = prohibited_rules(status)
    problems = []
    for clause in iter_decision_clauses(text):
        spans = find_non_establishment_spans(clause)
        for rule in rules:
            for match in rule.pattern.finditer(clause):
                if _governed(match, spans):
                    continue
                problems.append(
                    "%s[%s] <<%s>> presupposes %s, which this analysis does not support — %s"
                    % (label, rule.id, match.group(0), rule.presupposes, rule.why))
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2. The accepted claim, as propositions
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Assertion:
    """One proposition of the accepted central claim, with the phrasings that carry it."""

    id: str
    what: str
    any_of: tuple[str, ...]

    def present_in(self, text: str) -> bool:
        flat = _flatten(text).lower()
        return any(_flatten(p).lower() in flat for p in self.any_of)


#: The four propositions the accepted P0-1 (Path A) conclusion is made of. A surface may phrase each
#: however its length allows, but it may not drop one: dropping (2) or (3) is how a sentence about a
#: small observed advantage turns back into a verdict, and dropping (4) loses the paper's point.
ASSERTIONS: tuple[Assertion, ...] = (
    Assertion(
        "observed_advantage",
        "the observed pooled difference, with its sign, at the primary endpoint",
        # The last two are the venue-length renderings the Highlights file needs: 85 characters do
        # not fit "−0.394 percentage points" plus its sign convention, but "0.394 points LOWER than"
        # carries the same magnitude AND the same direction, which is what the proposition is for.
        ("−0.394 percentage points", "−0.394 pp", "−0.394 points",
         "0.394 points lower than", "0.394 percentage points lower than")),
    Assertion(
        "ranges_uncalibrated",
        "the reported ranges are uncalibrated sensitivity ranges, not confidence intervals",
        ("not calibrated confidence intervals", "not a calibrated confidence interval",
         "no range here is a calibrated confidence interval",
         "clustered percentile sensitivity range", "fixed-predictor sensitivity",
         "fixed-predictor clustered sensitivity", "without calibrated coverage",
         "uncalibrated sensitivity", "uncalibrated ranges")),
    Assertion(
        "no_decision_claimed",
        "no superiority, equivalence or absence-of-skill decision is made",
        ("do not establish whether", "does not establish whether", "we claim neither",
         "claim neither superiority", "no claim of statistical distinguishability",
         "determine neither", "does not determine whether", "do not determine whether",
         "cannot establish whether", "support no superiority")),
    Assertion(
        "accuracy_is_insufficient",
        "acceptable endpoint accuracy alone does not establish mechanistic transfer",
        ("does not by itself establish", "does not, by itself, establish",
         "do not by themselves establish", "alone does not establish",
         "does not establish useful mechanistic transfer", "necessary but insufficient",
         "not, by itself, evidence")),
)

ASSERTION_BY_ID = {a.id: a for a in ASSERTIONS}

#: Which surface must carry which propositions.
#:
#: The venue abstract and the cover letter carry all four: they are what an editor reads first, and
#: they are where the retired verdict lived. The headline block and endpoint synthesis carry the
#: limits and the lesson but need not restate the point estimate the surrounding table gives. The
#: figure caption map is a pointer document, so it carries the lesson only.
#:
#: Round-11 P1-3 added the two STANDALONE surfaces. Both are uploaded as separate files and read
#: without the paragraphs that supply the limits, and both were governed only by the prohibitive
#: half of the policy — so each could become materially stronger by OMISSION while every
#: prohibited-phrase check stayed green. The Highlights file said "a process model's gain over a
#: concentration-only baseline was under 0.4 points", which alone reads as an established property;
#: Figure 3's caption said its ranges are "not calibrated confidence intervals" and stopped, stating
#: what the ranges are not without stating what they cannot decide.
#:
#: Figure 3 carries all four, because its own file header claims the captions stand alone. The
#: Highlights file carries three: its 85-character bullets cannot also fit the transfer boundary,
#: and the venue limit is a real constraint rather than an excuse — what it may NOT do is drop the
#: evidence boundary to make room, which is why `no_decision_claimed` is required there.
SURFACE_ASSERTIONS: dict[str, tuple[str, ...]] = {
    "abstract": ("observed_advantage", "ranges_uncalibrated", "no_decision_claimed",
                 "accuracy_is_insufficient"),
    "editor_significance": ("no_decision_claimed", "accuracy_is_insufficient"),
    "cover_letter": ("observed_advantage", "ranges_uncalibrated", "no_decision_claimed",
                     "accuracy_is_insufficient"),
    "results_headline": ("observed_advantage", "ranges_uncalibrated",
                         "accuracy_is_insufficient"),
    "endpoint_synthesis": ("ranges_uncalibrated", "no_decision_claimed"),
    "supplement_reading": ("ranges_uncalibrated", "no_decision_claimed"),
    "conclusion": ("accuracy_is_insufficient",),
    "highlights": ("observed_advantage", "ranges_uncalibrated", "no_decision_claimed"),
    "figure3_caption": ("observed_advantage", "ranges_uncalibrated", "no_decision_claimed",
                        "accuracy_is_insufficient"),
}


def missing_assertions(text: str, surface: str) -> list[str]:
    """Which required propositions a surface fails to carry."""
    required = SURFACE_ASSERTIONS.get(surface)
    if required is None:
        raise KeyError("no assertion requirement declared for surface %r; add it to "
                       "SURFACE_ASSERTIONS rather than leaving the surface unchecked" % surface)
    return ["%s: the %s claim is missing (%s)" % (surface, a.id, a.what)
            for a in (ASSERTION_BY_ID[i] for i in required) if not a.present_in(text)]


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3. Generated claim sentences
# ─────────────────────────────────────────────────────────────────────────────────────────────


def limits_sentence(status: TS.InferentialStatus, estimand: TS.EstimandSpec) -> str:
    """The sentence that states what the ranges are and what they therefore cannot decide.

    Generated from the status object, so an analysis that later earns a decision cannot keep
    rendering this caveat, and one that has not earned it cannot lose it.
    """
    if status.coverage_calibrated:                                  # pragma: no cover - future path
        raise NotImplementedError(
            "a calibrated analysis needs its own decision sentence, stating the procedure, the "
            "coverage target and the decision rule; this helper only describes the uncalibrated "
            "case and must not be reused to describe a decision it does not know about")
    undecided = [name for name, ok in status.decision_flags.items() if not ok]
    return ("These are %s ranges, without calibrated coverage and without a predeclared practical "
            "margin, so their positions determine neither %s: this analysis does not establish "
            "whether the observed %s difference is reproducible or practically useful, and it does "
            "not establish that the difference is absent."
            % (status.analysis_kind.prose, _nor_list(undecided), estimand.metric_label))


def _nor_list(items) -> str:
    items = list(items)
    if len(items) <= 1:
        return "".join(items)
    return "%s, nor %s" % (", ".join(items[:-1]), items[-1])

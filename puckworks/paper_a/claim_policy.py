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
)

#: Phrases that mark an EXPLICIT disclaimer. A paper must be able to name the decision it is not
#: making — "we make no claim of statistical distinguishability, non-distinguishability or
#: equivalence" is the sentence the round-10 review praised, and a scanner that banned it would push
#: authors toward silence about the limits instead of clarity about them.
#:
#: Matched in the ~120 characters preceding a hit, on the normalised single-line text.
_DISCLAIMERS = (
    "no claim of", "no claims of", "make no claim", "makes no claim", "making no claim",
    "we do not claim", "do not claim", "does not claim", "cannot claim", "not a claim",
    "does not establish", "do not establish", "cannot establish", "is not established",
    "does not determine", "do not determine", "determine neither", "we claim neither",
    "neither", "rather than", "must not", "should not", "may not", "not be read as",
    "no such", "without", "is not", "are not", "not a", "reserve",
)

#: How far back to look for a disclaimer. Long enough for "we therefore make **no claim of
#: statistical distinguishability, non-distinguishability or equivalence** from these ranges".
_DISCLAIMER_WINDOW = 140


def _flatten(text: str) -> str:
    """Collapse whitespace and Markdown emphasis so a phrase survives wrapping and bolding.

    ``**no resolvable skill**`` and a phrase split across two source lines must both be found: the
    round-10 P2-1 finding was a prohibited phrase that survived because the scanner read physical
    lines, and emphasis markers inside a phrase are the same class of bypass.
    """
    return re.sub(r"[*_`]+", "", " ".join(text.split()))


def granted(status: TS.InferentialStatus) -> set[str]:
    """The decision properties a declared status actually grants."""
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
    """Return one problem per prohibited decision claim in ``text``. Empty means compliant."""
    flat = _flatten(text)
    label = ("%s: " % where) if where else ""
    problems = []
    for rule in prohibited_rules(status):
        for match in rule.pattern.finditer(flat):
            before = flat[max(0, match.start() - _DISCLAIMER_WINDOW):match.start()].lower()
            if any(d in before for d in _DISCLAIMERS):
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
        ("−0.394 percentage points", "−0.394 pp", "−0.394 points")),
    Assertion(
        "ranges_uncalibrated",
        "the reported ranges are uncalibrated sensitivity ranges, not confidence intervals",
        ("not calibrated confidence intervals", "not a calibrated confidence interval",
         "no range here is a calibrated confidence interval",
         "clustered percentile sensitivity range", "fixed-predictor sensitivity",
         "fixed-predictor clustered sensitivity", "without calibrated coverage",
         "uncalibrated sensitivity")),
    Assertion(
        "no_decision_claimed",
        "no superiority, equivalence or absence-of-skill decision is made",
        ("do not establish whether", "does not establish whether", "we claim neither",
         "claim neither superiority", "no claim of statistical distinguishability",
         "determine neither", "does not determine whether", "do not determine whether",
         "cannot establish whether")),
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

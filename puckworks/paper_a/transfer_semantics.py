"""Typed scientific facts about an interval, so no renderer has to infer them.

Round-9 P0-1 and P0-2. The round-8 remediation stopped values being retyped, and immediately
produced a new failure mode: **current numbers rendered into false sentences**. Two examples, both
shipped:

  * the fitting-loss paragraph computed ``same_side = (base.contains_zero == alt.contains_zero)``
    and rendered ``True == True`` as "both lie on the same side of zero". Both intervals *contain*
    zero — they do not lie on a side of it at all. The same code would also have called one wholly
    negative and one wholly positive interval "the same side of zero", because both give
    ``False == False``;
  * Supplementary Table S3 described "the largest advantage any upper bound admits". The estimand
    is ``model loss − comparator loss``, so **negative** values favour the model and the *lower*
    bound is the favourable extreme. The sentence named the wrong end of the interval.

A single boolean cannot safely render four distinct facts. This module separates them:

  1. **containment** — where the interval sits relative to zero (a trinary relation, never a
     boolean, because ``not contains_zero`` conflates "wholly below" with "wholly above");
  2. **exact contact** — whether a bound *is* zero, derived only from full-precision values, never
     because display rounding produced ``0.000``;
  3. **favourability** — which end of the interval is good for the model, which requires knowing
     the estimand's sign convention and cannot be inferred from the interval alone;
  4. **numerical resolution** — how well a bound is pinned down by the resampler, which is a
     property of one audited target and does not generalise (round-9 P1-1);
  5. **inferential status** — which DECISIONS the analysis is able to make at all. An uncalibrated
     sensitivity range cannot establish superiority, and equally cannot establish equivalence or
     absence of skill; without a predeclared practical margin it cannot call a difference
     negligible (round-10 P0-1).

Round-10 P1-2 changed how (3) is obtained. Favourability used to be a second, independently typed
declaration (``EstimandDirection.negative_favours_model``) sitting beside a free-text estimand
sentence in the artefact, with the renderer defaulting to the module-level constant. Two
declarations of one fact agree only by luck: a reversed artefact estimand left the default direction
untouched, the validator and the source oracle stayed green, and the generated prose kept saying
"negative values favour the mechanistic model". Direction is now DERIVED from primitives — which
metric, which way it is preferred, which operands, in which order — and every publication caller
must pass the validated estimand. There is no default.

Pure, dependency-free, and deliberately verbose about the distinction it exists to keep.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1 + 2. Where an interval sits relative to zero
# ─────────────────────────────────────────────────────────────────────────────────────────────


class ZeroRelation(str, Enum):
    """An interval's position relative to zero. Trinary, because a boolean loses the side.

    ``BELOW``/``ABOVE`` both mean "excludes zero"; collapsing them to one negated flag is what let
    the round-8 code call two opposite intervals "the same side of zero".
    """

    BELOW = "below_zero"
    CONTAINS = "contains_zero"
    ABOVE = "above_zero"

    @property
    def excludes_zero(self) -> bool:
        return self is not ZeroRelation.CONTAINS

    @property
    def prose(self) -> str:
        """How the paper says it, in isolation."""
        return {
            ZeroRelation.BELOW: "excludes zero on the negative side",
            ZeroRelation.CONTAINS: "contains zero",
            ZeroRelation.ABOVE: "excludes zero on the positive side",
        }[self]


@dataclass(frozen=True)
class IntervalSemantics:
    """One interval's typed facts, all derived from FULL-PRECISION bounds."""

    lower: float
    upper: float
    relation: ZeroRelation
    touches_zero_at_lower: bool
    touches_zero_at_upper: bool

    @property
    def width(self) -> float:
        return self.upper - self.lower


def require_finite_number(value, what: str) -> float:
    """Return ``value`` as a finite float, or raise. Rejects bool, str, None, NaN and infinities.

    Round-10 P1-3. ``interval_semantics`` used to call ``float()`` on whatever it was handed, so
    ``True``, ``"0.1"`` and ``+inf`` were all accepted and classified: ``interval_semantics(True,
    1.0)`` returned a cheerful ABOVE-zero interval. Every one of those inputs is a defect upstream —
    a boolean where a bound belongs, a JSON string that was never parsed, a division that
    overflowed — and classifying it converts that defect into a plausible sentence.

    ``bool`` is excluded explicitly: it is a subclass of ``int``, so an ``isinstance(value, int)``
    test alone admits ``True`` as the number 1.
    """
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return _reject("%s must be a finite JSON number, got %s %r"
                       % (what, type(value).__name__, value))
    out = float(value)
    if out != out or out in (float("inf"), float("-inf")):
        return _reject("%s must be finite, got %r" % (what, out))
    return out


def _reject(message: str):
    raise ValueError(message)


def interval_semantics(lower, upper) -> IntervalSemantics:
    """Classify ``[lower, upper]`` against zero from full precision.

    Closed-interval convention: a bound of exactly 0.0 means the interval *contains* zero, and the
    corresponding ``touches_zero_at_*`` flag records where. Exact contact is reported separately
    from containment so a renderer can distinguish "reaches zero at its upper bound" (contact) from
    "contains zero" (the bound lies beyond it) — a distinction the round-8 conclusion and cover
    letter got wrong, describing a ``+0.0038 pp`` upper bound as reaching zero.

    Bounds must be finite real numbers. Booleans, numeric strings, ``None``, NaN and infinities are
    rejected before classification rather than coerced (round-10 P1-3).
    """
    lo = require_finite_number(lower, "interval lower bound")
    hi = require_finite_number(upper, "interval upper bound")
    if not lo <= hi:
        raise ValueError("interval lower bound %r exceeds upper bound %r" % (lo, hi))
    if hi < 0.0:
        relation = ZeroRelation.BELOW
    elif lo > 0.0:
        relation = ZeroRelation.ABOVE
    else:
        relation = ZeroRelation.CONTAINS
    return IntervalSemantics(lower=lo, upper=hi, relation=relation,
                             touches_zero_at_lower=(lo == 0.0),
                             touches_zero_at_upper=(hi == 0.0))


def from_interval_record(interval: dict) -> IntervalSemantics:
    """Classify an archived interval record from its full-precision bounds."""
    fp = interval["full_precision_pp"]
    return interval_semantics(fp["lower"], fp["upper"])


def describe_shared_relation(intervals) -> str:
    """Prose for a set of intervals, naming the actual relation rather than a boolean match.

    This is the P0-1 fix. Equality of containment flags does **not** license "the same side of
    zero"; only a shared *excluding* relation does, and then the side must be named.
    """
    sem = list(intervals)
    if not sem:
        raise ValueError("no intervals to describe")
    relations = {s.relation for s in sem}
    if len(relations) > 1:
        return "; ".join(s.relation.prose for s in sem)
    only = relations.pop()
    if only is ZeroRelation.CONTAINS:
        return ("both contain zero" if len(sem) == 2 else "all contain zero")
    side = "negative" if only is ZeroRelation.BELOW else "positive"
    return ("both exclude zero on the %s side" % side if len(sem) == 2
            else "all exclude zero on the %s side" % side)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3. Which end of the interval is good news
# ─────────────────────────────────────────────────────────────────────────────────────────────


class MetricPreference(str, Enum):
    """Which direction of a metric is good. A loss prefers lower; a skill score prefers higher."""

    LOWER_IS_BETTER = "lower_is_better"
    HIGHER_IS_BETTER = "higher_is_better"


class ContrastOperation(str, Enum):
    """Which way round the two arms are subtracted."""

    LEFT_MINUS_RIGHT = "left_minus_right"
    RIGHT_MINUS_LEFT = "right_minus_left"


#: The operand id the paper's claims are ABOUT. Named once so "does a negative value favour the
#: model?" is a lookup against the estimand's operands rather than a second stored boolean.
MODEL_OPERAND = "mechanistic_model"


@dataclass(frozen=True)
class EstimandSpec:
    """A comparative estimand, stated as primitives so its direction can be DERIVED.

    Round-10 P1-2. The predecessor of this type stored ``negative_favours_model`` as a declared
    boolean next to a free-text estimand sentence. Nothing required the two to agree, so a reversed
    contrast could keep every favourability sentence unchanged while the contract stayed green.

    Here the only stored facts are the metric, its preferred direction, the two operands and the
    order of subtraction. Whether a negative value is good news follows mathematically:

        negative favours LEFT  ⟺  (metric prefers lower) == (operation is left − right)

    So reversing ``operation`` reverses every favourability statement, or fails validation. It
    cannot leave the prose untouched.
    """

    id: str
    metric_id: str
    metric_label: str
    metric_preference: MetricPreference
    left_operand: str
    left_label: str
    right_operand: str
    right_label: str
    operation: ContrastOperation
    units: str
    units_label: str

    # ── derived direction ───────────────────────────────────────────────────────────────────
    @property
    def negative_favours(self) -> str:
        """The operand id a negative value of this estimand favours."""
        lower_is_better = self.metric_preference is MetricPreference.LOWER_IS_BETTER
        left_first = self.operation is ContrastOperation.LEFT_MINUS_RIGHT
        return self.left_operand if lower_is_better == left_first else self.right_operand

    @property
    def positive_favours(self) -> str:
        return (self.right_operand if self.negative_favours == self.left_operand
                else self.left_operand)

    @property
    def negative_favours_model(self) -> bool:
        """Convenience for the current paper. Derived, never stored."""
        return self.negative_favours == MODEL_OPERAND

    @property
    def label_of(self) -> dict:
        return {self.left_operand: self.left_label, self.right_operand: self.right_label}

    @property
    def contrast_label(self) -> str:
        """``<metric> for <first> minus <metric> for <second>``, in the declared order."""
        first, second = ((self.left_label, self.right_label)
                         if self.operation is ContrastOperation.LEFT_MINUS_RIGHT
                         else (self.right_label, self.left_label))
        return "%s for the %s minus %s for the %s" % (self.metric_label, first,
                                                      self.metric_label, second)

    @property
    def short_contrast_label(self) -> str:
        """Table-cell form: ``pooled MAPE, mechanistic model − O-trained level-only comparator``.

        Derived from the same primitives as :attr:`contrast_label`, so a reversed operation reverses
        the cell too. Uses U+2212 MINUS SIGN, the paper's convention.
        """
        first, second = ((self.left_label, self.right_label)
                         if self.operation is ContrastOperation.LEFT_MINUS_RIGHT
                         else (self.right_label, self.left_label))
        return "%s, %s − %s" % (self.metric_label, first, second)

    @property
    def direction_clause(self) -> str:
        """The sign convention as a clause that can be embedded mid-sentence.

        Kept separate from :attr:`prose` because ``prose`` carries a semicolon: dropping the whole
        sentence into "Because the estimand is …: the most favourable bound is …" produced a
        sentence with two competing punctuation structures.
        """
        return "negative values favour the %s" % self.label_of[self.negative_favours]

    @property
    def prose(self) -> str:
        """The one sentence every surface uses to define the estimand and its sign."""
        return "%s, in %s; %s" % (self.contrast_label, self.units_label, self.direction_clause)

    @property
    def zero_means(self) -> str:
        return "equal %s under the stated scoring rule" % self.metric_label

    def as_dict(self) -> dict:
        """Serialisation. Derived fields are included for transparency and RE-DERIVED on
        validation, so a hand-edited artefact cannot advertise a direction it does not have."""
        return {
            "id": self.id,
            "metric_id": self.metric_id,
            "metric_label": self.metric_label,
            "metric_preference": self.metric_preference.value,
            "left_operand": self.left_operand,
            "left_label": self.left_label,
            "right_operand": self.right_operand,
            "right_label": self.right_label,
            "operation": self.operation.value,
            "units": self.units,
            "units_label": self.units_label,
            # derived ────────────────────────────────────────────────────────────────────────
            "negative_values_favour": self.negative_favours,
            "positive_values_favour": self.positive_favours,
            "contrast_label": self.contrast_label,
            "short_contrast_label": self.short_contrast_label,
            "direction_clause": self.direction_clause,
            "zero_means": self.zero_means,
            "prose": self.prose,
        }


def estimand_from_dict(obj) -> EstimandSpec:
    """Rebuild an ``EstimandSpec`` from a serialised object, rejecting anything unknown.

    Unknown enum values are REJECTED, never defaulted: falling back to "lower is better" is how a
    misdeclared metric would silently keep the old favourability prose.
    """
    if not isinstance(obj, dict):
        raise ValueError("estimand must be a mapping, got %s" % type(obj).__name__)
    required = ("id", "metric_id", "metric_label", "metric_preference", "left_operand",
                "left_label", "right_operand", "right_label", "operation", "units", "units_label")
    missing = [k for k in required if k not in obj]
    if missing:
        raise ValueError("estimand is missing required field(s) %r" % (missing,))
    for key, enum in (("metric_preference", MetricPreference), ("operation", ContrastOperation)):
        if obj[key] not in {m.value for m in enum}:
            raise ValueError("estimand.%s is %r, which is not one of %r"
                             % (key, obj[key], sorted(m.value for m in enum)))
    if obj["left_operand"] == obj["right_operand"]:
        raise ValueError("estimand contrasts an operand with itself (%r)" % obj["left_operand"])
    return EstimandSpec(
        id=str(obj["id"]), metric_id=str(obj["metric_id"]), metric_label=str(obj["metric_label"]),
        metric_preference=MetricPreference(obj["metric_preference"]),
        left_operand=str(obj["left_operand"]), left_label=str(obj["left_label"]),
        right_operand=str(obj["right_operand"]), right_label=str(obj["right_label"]),
        operation=ContrastOperation(obj["operation"]),
        units=str(obj["units"]), units_label=str(obj["units_label"]))


#: Paper A's comparative estimand. Both arms are scored by MAPE — a LOSS, so lower is better — and
#: the difference is taken model minus comparator, from which "negative favours the mechanistic
#: model" follows. Nothing here states that conclusion directly.
POOLED_MAPE_ESTIMAND = EstimandSpec(
    id="pooled_mape_model_minus_level_only_pp",
    metric_id="pooled_mape",
    metric_label="pooled MAPE",
    metric_preference=MetricPreference.LOWER_IS_BETTER,
    left_operand=MODEL_OPERAND,
    left_label="mechanistic model",
    right_operand="o_trained_level_only_comparator",
    right_label="O-trained level-only comparator",
    operation=ContrastOperation.LEFT_MINUS_RIGHT,
    units="percentage_points",
    units_label="percentage points")


def favourable_extremes(intervals, estimand: EstimandSpec):
    """Return ``(most_favourable, least_favourable)`` bounds across ``intervals``.

    ``estimand`` is REQUIRED. The round-9 remediation left this parameter defaulted, so every
    publication caller silently received the module-level direction regardless of what the artefact
    declared — the P1-2 defect. A missing estimand is now a ``TypeError`` at the call site rather
    than a wrong sentence in the manuscript.

    When negative values favour the model the most favourable value is the smallest LOWER bound and
    the least favourable is the largest UPPER bound. Under the opposite convention the roles swap,
    which is exactly why this is a function of the estimand and not of the interval.
    """
    sem = list(intervals)
    if not sem:
        raise ValueError("no intervals to compare")
    if not isinstance(estimand, EstimandSpec):
        raise TypeError("favourable_extremes requires a validated EstimandSpec, got %s"
                        % type(estimand).__name__)
    lowers = [s.lower for s in sem]
    uppers = [s.upper for s in sem]
    if estimand.negative_favours_model:
        return min(lowers), max(uppers)
    return max(uppers), min(lowers)


def permits_no_advantage(interval: IntervalSemantics, estimand: EstimandSpec) -> bool:
    """True when the interval's least-favourable end concedes the model no advantage at all."""
    if not isinstance(estimand, EstimandSpec):
        raise TypeError("permits_no_advantage requires a validated EstimandSpec, got %s"
                        % type(estimand).__name__)
    if estimand.negative_favours_model:
        return interval.upper >= 0.0
    return interval.lower <= 0.0


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 5. What the analysis is able to DECIDE (round-10 P0-1)
# ─────────────────────────────────────────────────────────────────────────────────────────────


class AnalysisKind(str, Enum):
    """How the reported ranges were produced. Unknown kinds are rejected, never defaulted."""

    FIXED_PREDICTOR_CLUSTERED_SENSITIVITY = "fixed_predictor_clustered_sensitivity"
    CALIBRATED_CLUSTERED_CONFIDENCE = "calibrated_clustered_confidence"

    @property
    def prose(self) -> str:
        """How the paper names the procedure. Derived, so the identifier stays machine-shaped."""
        return {
            AnalysisKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY:
                "fixed-predictor clustered sensitivity",
            AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE:
                "calibrated clustered confidence",
        }[self]


class ClaimClass(str, Enum):
    """The strongest class of claim an analysis of this kind may support."""

    #: Report the observed contrast and the limits of the evidence. No decision is made.
    DESCRIPTIVE_EVIDENCE_LIMITED = "descriptive_evidence_limited"
    #: A calibrated procedure with a predeclared margin decided something.
    CALIBRATED_DECISION = "calibrated_decision"


@dataclass(frozen=True)
class InferentialStatus:
    """What the transfer analysis can and cannot determine, as data rather than as prose.

    Round-10 P0-1. The paper simultaneously stated that its ranges have no calibrated coverage and
    support "no claim of statistical distinguishability, non-distinguishability or equivalence", and
    concluded in the abstract, the significance paragraph, the Results headline, the endpoint
    synthesis, the cover letter and the caption map that the model supplied "no resolvable skill".
    An uncalibrated range cannot establish that a model HAS incremental skill; the same range
    cannot establish that it has NONE. The second error is easy to miss because it sounds cautious.

    So the decisions the analysis is entitled to make are declared, validated for internal
    consistency, and consumed by the claim renderer. A sentence that carries a scientific decision
    cannot then be generated from an analysis that says no such decision was performed.
    """

    analysis_kind: AnalysisKind
    coverage_calibrated: bool
    confidence_level: float | None
    confidence_procedure: str | None
    predictors_refitted_within_draw: bool
    supports_superiority_decision: bool
    supports_noninferiority_decision: bool
    supports_equivalence_decision: bool
    supports_absence_of_skill_decision: bool
    practical_margin_pp: float | None
    permitted_claim_class: ClaimClass

    def as_dict(self) -> dict:
        return {
            "analysis_kind": self.analysis_kind.value,
            "coverage_calibrated": bool(self.coverage_calibrated),
            "confidence_level": self.confidence_level,
            "confidence_procedure": self.confidence_procedure,
            "predictors_refitted_within_draw": bool(self.predictors_refitted_within_draw),
            "supports_superiority_decision": bool(self.supports_superiority_decision),
            "supports_noninferiority_decision": bool(self.supports_noninferiority_decision),
            "supports_equivalence_decision": bool(self.supports_equivalence_decision),
            "supports_absence_of_skill_decision": bool(self.supports_absence_of_skill_decision),
            "practical_margin_pp": self.practical_margin_pp,
            "permitted_claim_class": self.permitted_claim_class.value,
        }

    @property
    def decision_flags(self) -> dict:
        """Decision name (as prose) → whether this analysis is entitled to make it."""
        return {"superiority": self.supports_superiority_decision,
                "non-inferiority": self.supports_noninferiority_decision,
                "equivalence": self.supports_equivalence_decision,
                "absence of skill": self.supports_absence_of_skill_decision}


#: Paper A's transfer analysis, as it actually is. Every flag is False and the margin is None,
#: which is not modesty — it is what a fixed-predictor clustered percentile sensitivity range
#: without a predeclared margin can support.
TRANSFER_INFERENTIAL_STATUS = InferentialStatus(
    analysis_kind=AnalysisKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY,
    coverage_calibrated=False,
    confidence_level=None,
    confidence_procedure=None,
    predictors_refitted_within_draw=False,
    supports_superiority_decision=False,
    supports_noninferiority_decision=False,
    supports_equivalence_decision=False,
    supports_absence_of_skill_decision=False,
    practical_margin_pp=None,
    permitted_claim_class=ClaimClass.DESCRIPTIVE_EVIDENCE_LIMITED)


def status_from_dict(obj) -> InferentialStatus:
    """Rebuild an ``InferentialStatus`` from a serialised object. Rejects unknown enum values."""
    if not isinstance(obj, dict):
        raise ValueError("inferential_status must be a mapping, got %s" % type(obj).__name__)
    required = ("analysis_kind", "coverage_calibrated", "confidence_level",
                "confidence_procedure", "predictors_refitted_within_draw",
                "supports_superiority_decision", "supports_noninferiority_decision",
                "supports_equivalence_decision", "supports_absence_of_skill_decision",
                "practical_margin_pp", "permitted_claim_class")
    missing = [k for k in required if k not in obj]
    if missing:
        raise ValueError("inferential_status is missing required field(s) %r" % (missing,))
    if obj["analysis_kind"] not in {k.value for k in AnalysisKind}:
        raise ValueError("inferential_status.analysis_kind is %r, which is not one of %r"
                         % (obj["analysis_kind"], sorted(k.value for k in AnalysisKind)))
    if obj["permitted_claim_class"] not in {c.value for c in ClaimClass}:
        raise ValueError("inferential_status.permitted_claim_class is %r, which is not one of %r"
                         % (obj["permitted_claim_class"], sorted(c.value for c in ClaimClass)))
    for key in ("coverage_calibrated", "predictors_refitted_within_draw",
                "supports_superiority_decision", "supports_noninferiority_decision",
                "supports_equivalence_decision", "supports_absence_of_skill_decision"):
        if not isinstance(obj[key], bool):
            raise ValueError("inferential_status.%s must be a JSON boolean, got %r"
                             % (key, obj[key]))
    for key in ("confidence_level", "practical_margin_pp"):
        value = obj[key]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise ValueError("inferential_status.%s must be null or a number, got %r"
                             % (key, value))
    return InferentialStatus(
        analysis_kind=AnalysisKind(obj["analysis_kind"]),
        coverage_calibrated=obj["coverage_calibrated"],
        confidence_level=obj["confidence_level"],
        confidence_procedure=(None if obj["confidence_procedure"] is None
                              else str(obj["confidence_procedure"])),
        predictors_refitted_within_draw=obj["predictors_refitted_within_draw"],
        supports_superiority_decision=obj["supports_superiority_decision"],
        supports_noninferiority_decision=obj["supports_noninferiority_decision"],
        supports_equivalence_decision=obj["supports_equivalence_decision"],
        supports_absence_of_skill_decision=obj["supports_absence_of_skill_decision"],
        practical_margin_pp=obj["practical_margin_pp"],
        permitted_claim_class=ClaimClass(obj["permitted_claim_class"]))


def validate_inferential_status(status: InferentialStatus) -> list[str]:
    """Internal consistency of a declared status. Empty means coherent.

    These rules are what stop the object from becoming a rubber stamp. In particular a status cannot
    grant itself a decision it has no procedure for: claiming calibrated coverage without naming a
    procedure, or claiming an equivalence/absence decision without a predeclared margin, fails.
    """
    problems: list[str] = []
    calibrated = bool(status.coverage_calibrated)

    if calibrated:
        if not status.confidence_procedure:
            problems.append("coverage_calibrated is true but no confidence_procedure is named; a "
                            "coverage claim requires an identified procedure, not a flag")
        level = status.confidence_level
        if level is None or isinstance(level, bool) or not isinstance(level, (int, float)) \
                or not 0.0 < float(level) < 1.0:
            problems.append("coverage_calibrated is true but confidence_level is %r; a coverage "
                            "target in (0, 1) is required" % (level,))
        if status.analysis_kind is AnalysisKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY:
            problems.append("analysis_kind is a fixed-predictor sensitivity analysis, which has no "
                            "calibrated coverage; coverage_calibrated must be false")
    else:
        if status.confidence_level is not None:
            problems.append("coverage_calibrated is false but a confidence_level (%r) is declared; "
                            "an uncalibrated range has no coverage target"
                            % (status.confidence_level,))
        if status.confidence_procedure is not None:
            problems.append("coverage_calibrated is false but a confidence_procedure (%r) is "
                            "declared" % (status.confidence_procedure,))
        for name, granted in status.decision_flags.items():
            if granted:
                problems.append("coverage_calibrated is false but the status grants a %s "
                                "decision; an uncalibrated sensitivity range decides nothing, in "
                                "either direction" % name)

    margin = status.practical_margin_pp
    needs_margin = (status.supports_equivalence_decision
                    or status.supports_absence_of_skill_decision
                    or status.supports_noninferiority_decision)
    if needs_margin and (margin is None or isinstance(margin, bool)
                         or not isinstance(margin, (int, float)) or not float(margin) > 0.0):
        problems.append("an equivalence, non-inferiority or absence-of-skill decision requires a "
                        "predeclared practical margin in percentage points; practical_margin_pp is "
                        "%r" % (margin,))
    if margin is not None and not needs_margin:
        problems.append("a practical margin (%r) is declared but no decision uses it; an unused "
                        "margin invites a post hoc negligibility claim" % (margin,))

    decides_something = any(status.decision_flags.values())
    if status.permitted_claim_class is ClaimClass.CALIBRATED_DECISION and not decides_something:
        problems.append("permitted_claim_class is a calibrated decision but the status supports no "
                        "decision")
    if status.permitted_claim_class is ClaimClass.DESCRIPTIVE_EVIDENCE_LIMITED and decides_something:
        problems.append("permitted_claim_class is descriptive/evidence-limited but the status "
                        "grants a decision")
    if status.predictors_refitted_within_draw:
        problems.append("predictors_refitted_within_draw is true; the fixed-predictor contract the "
                        "whole analysis rests on is then violated")
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 4. Numerical resolution, scoped to exactly one audited target (round-9 P1-1)
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AuditKey:
    """The exact target a multi-seed Monte Carlo audit describes.

    Monte Carlo quantile error depends on the resampling distribution and its local tail density.
    An audit of one endpoint/scheme/loss says nothing rigorous about another, so the audit is
    addressed by an exact key and lookup fails rather than falling back.
    """

    endpoint_g: float
    scheme: str
    fitting_loss: str
    bound: str = "both"

    def as_dict(self) -> dict:
        return {"endpoint_g": float(self.endpoint_g), "scheme": self.scheme,
                "fitting_loss": self.fitting_loss, "bound": self.bound}

    @property
    def prose(self) -> str:
        return ("%g g, %s, %s fitting loss"
                % (self.endpoint_g, self.scheme, self.fitting_loss))


#: The one audit Paper A actually retains.
DEFAULT_FITTING_LOSS = "primary"
AUDITED_TARGET = AuditKey(endpoint_g=40.0, scheme="cond_in_variety",
                          fitting_loss=DEFAULT_FITTING_LOSS)


def find_exact_audit(artifact: dict, key: AuditKey) -> dict:
    """Return the single archived audit matching ``key`` exactly.

    Fails on zero matches and on multiple matches; never partial-matches and never falls back to
    a top-level scalar. A renderer that cannot find its audit must say "not separately audited",
    not borrow another target's number.
    """
    audits = artifact.get("stability_audits")
    if not isinstance(audits, list):
        raise KeyError("artefact carries no `stability_audits` list; a single top-level "
                       "`stability_audit` is the round-8 schema and its value must not be "
                       "reused across endpoints, schemes or losses")
    want = key.as_dict()
    matches = [a for a in audits if a.get("target") == want]
    if not matches:
        raise KeyError("no archived Monte Carlo audit for target %r; do not substitute another "
                       "target's value" % (want,))
    if len(matches) > 1:
        raise KeyError("%d archived audits match target %r; the key is not unique"
                       % (len(matches), want))
    return matches[0]


def has_exact_audit(artifact: dict, key: AuditKey) -> bool:
    try:
        find_exact_audit(artifact, key)
    except KeyError:
        return False
    return True

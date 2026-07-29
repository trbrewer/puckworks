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
     property of one audited target and does not generalise (round-9 P1-1).

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


def interval_semantics(lower: float, upper: float) -> IntervalSemantics:
    """Classify ``[lower, upper]`` against zero from full precision.

    Closed-interval convention: a bound of exactly 0.0 means the interval *contains* zero, and the
    corresponding ``touches_zero_at_*`` flag records where. Exact contact is reported separately
    from containment so a renderer can distinguish "reaches zero at its upper bound" (contact) from
    "contains zero" (the bound lies beyond it) — a distinction the round-8 conclusion and cover
    letter got wrong, describing a ``+0.0038 pp`` upper bound as reaching zero.
    """
    lo, hi = float(lower), float(upper)
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


@dataclass(frozen=True)
class EstimandDirection:
    """Which sign of the estimand favours the mechanistic model.

    Cannot be inferred from an interval. The round-8 supplement assumed the upper bound bounded
    the model's "largest advantage"; for a loss *difference* it bounds the largest disadvantage.
    """

    label: str
    negative_favours_model: bool


#: Paper A's comparative estimand. Both arms are scored by MAPE and the difference is taken
#: model-minus-comparator, so a NEGATIVE value means the mechanistic model lost less error.
PAIRED_LOSS_DIFFERENCE = EstimandDirection(
    label="pooled MAPE difference, mechanistic model minus O-trained level-only comparator",
    negative_favours_model=True)


def favourable_extremes(intervals, direction: EstimandDirection = PAIRED_LOSS_DIFFERENCE):
    """Return ``(most_favourable, least_favourable)`` bounds across ``intervals``.

    With ``negative_favours_model``, the most favourable value is the smallest lower bound and the
    least favourable is the largest upper bound. With the opposite convention the roles swap —
    which is exactly why this is a function of the declared direction and not of the interval.
    """
    sem = list(intervals)
    if not sem:
        raise ValueError("no intervals to compare")
    lowers = [s.lower for s in sem]
    uppers = [s.upper for s in sem]
    if direction.negative_favours_model:
        return min(lowers), max(uppers)
    return max(uppers), min(lowers)


def permits_no_advantage(interval: IntervalSemantics,
                         direction: EstimandDirection = PAIRED_LOSS_DIFFERENCE) -> bool:
    """True when the interval's least-favourable end concedes the model no advantage at all."""
    if direction.negative_favours_model:
        return interval.upper >= 0.0
    return interval.lower <= 0.0


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

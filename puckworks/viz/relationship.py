"""Relationship analysis for educational tour figures (#43, ROADMAP §8).

A pure, tested classifier for a 1-D computed curve y(x): monotone increasing / decreasing / approximately
flat / non-monotonic / insufficient. It exists so captions state a relationship the model ACTUALLY
produced (values inserted from `RelationshipSummary`, never hand-typed) and so a one-grid-point wobble is
never mislabelled a physical reversal — a turning point is reported only when the sign change exceeds a
documented tolerance and there are enough points on both sides. No matplotlib, no model — inputs only.
"""
from __future__ import annotations

import dataclasses
import math

CLASSIFICATIONS = ("increasing", "decreasing", "approximately_flat", "non_monotonic", "insufficient")


@dataclasses.dataclass(frozen=True)
class RelationshipSummary:
    classification: str
    direction_before: str | None = None   # for non_monotonic: 'increasing'/'decreasing' before the turn
    direction_after: str | None = None
    turning_x: float | None = None
    turning_index: int | None = None
    x_start: float | None = None
    x_end: float | None = None
    y_start: float | None = None
    y_turning: float | None = None
    y_end: float | None = None
    total_change: float | None = None      # y_end - y_start
    rel_tolerance: float = 0.0
    n_points: int = 0

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _finite_pairs(x, y):
    out = []
    for xi, yi in zip(x, y):
        try:
            xf, yf = float(xi), float(yi)
        except (TypeError, ValueError):
            continue
        if math.isfinite(xf) and math.isfinite(yf):
            out.append((xf, yf))
    out.sort(key=lambda p: p[0])
    return out


def classify_relationship(x, y, *, rel_tol: float = 0.02, min_side_points: int = 2) -> RelationshipSummary:
    """Classify y(x). ``rel_tol`` is the fraction of the total |y|-range a step must exceed to count as a
    real move (below it, a step is 'flat', so noise is not read as a reversal). A non-monotonic verdict
    with a turning point requires >= ``min_side_points`` genuine moves on each side of the turn.

    A caption should insert values from the returned summary rather than typing them by hand.
    """
    pairs = _finite_pairs(x, y)
    n = len(pairs)
    if n < 3:
        return RelationshipSummary("insufficient", n_points=n)
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    yr = max(ys) - min(ys)
    span = max(abs(v) for v in ys) or 1.0
    # a step counts as a real move only if it exceeds rel_tol of the value magnitude (so a small wiggle on
    # a large baseline reads as flat, not a reversal); max(yr, span) keeps it sane near y=0.
    thresh = rel_tol * max(yr, span)
    # directional signs of each step, with |step| below threshold treated as flat (0)
    signs = []
    for i in range(1, n):
        d = ys[i] - ys[i - 1]
        signs.append(0 if abs(d) <= thresh else (1 if d > 0 else -1))
    ups = sum(1 for s in signs if s > 0)
    downs = sum(1 for s in signs if s < 0)
    base = dict(x_start=xs[0], x_end=xs[-1], y_start=ys[0], y_end=ys[-1],
                total_change=ys[-1] - ys[0], rel_tolerance=rel_tol, n_points=n)
    if ups == 0 and downs == 0:
        return RelationshipSummary("approximately_flat", **base)
    if downs == 0:
        return RelationshipSummary("increasing", **base)
    if ups == 0:
        return RelationshipSummary("decreasing", **base)
    # both directions present -> look for a single dominant turning point
    turn = _turning_index(ys, signs, min_side_points)
    if turn is None:
        return RelationshipSummary("non_monotonic", **base)  # wobbly, no single clean turn
    dir_before = "increasing" if ys[turn] - ys[0] > 0 else "decreasing"
    dir_after = "increasing" if ys[-1] - ys[turn] > 0 else "decreasing"
    return RelationshipSummary("non_monotonic", direction_before=dir_before, direction_after=dir_after,
                               turning_x=xs[turn], turning_index=turn, y_turning=ys[turn], **base)


def _turning_index(ys, signs, min_side_points):
    """A single dominant turn: the extremum index whose two sides each carry >= min_side_points genuine
    (non-flat) steps that are predominantly opposite in direction. Returns None for a one-point wobble."""
    n = len(ys)
    # candidate = global max or global min (whichever is interior)
    for cand in (ys.index(max(ys)), ys.index(min(ys))):
        if cand == 0 or cand == n - 1:
            continue
        left = [s for s in signs[:cand] if s != 0]
        right = [s for s in signs[cand:] if s != 0]
        if len(left) < min_side_points or len(right) < min_side_points:
            continue
        left_dir = 1 if sum(left) > 0 else -1
        right_dir = 1 if sum(right) > 0 else -1
        if left_dir != right_dir:                      # genuine reversal across the candidate
            # require the sides to be MOSTLY monotone (>= 60% agree with their side direction)
            if (sum(1 for s in left if s == left_dir) >= 0.6 * len(left)
                    and sum(1 for s in right if s == right_dir) >= 0.6 * len(right)):
                return cand
    return None


def describe(summary: RelationshipSummary, y_label: str, x_label: str, unit: str = "") -> str:
    """A short, value-carrying phrase for a caption (all numbers recomputed from the summary)."""
    u = f" {unit}" if unit else ""
    c = summary.classification
    if c == "insufficient":
        return f"not enough valid points to describe how {y_label} depends on {x_label}"
    if c == "approximately_flat":
        return f"{y_label} stays essentially flat ({summary.y_start:.3g}{u}) as {x_label} changes"
    if c == "increasing":
        return (f"{y_label} rises from {summary.y_start:.3g} to {summary.y_end:.3g}{u} as {x_label} "
                f"increases")
    if c == "decreasing":
        return (f"{y_label} falls from {summary.y_start:.3g} to {summary.y_end:.3g}{u} as {x_label} "
                f"increases")
    if summary.turning_x is not None:
        return (f"{y_label} {summary.direction_before} to {summary.y_turning:.3g}{u} near "
                f"{x_label}={summary.turning_x:.3g}, then {summary.direction_after} to "
                f"{summary.y_end:.3g}{u}")
    return f"{y_label} varies non-monotonically with {x_label}"

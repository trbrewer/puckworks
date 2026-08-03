"""WIDE-referenced reference minimum, finite topology, analytical endpoint, and the H1 rule.

Protocol V2 §2 previously defined the P0-G8 reference quantity as an infimum of `J(kappa)` over a
compactified domain running from 0.15 up to and including an infinite endpoint, while the only
search that was ever specified ended at kappa = 500. Those
two statements cannot both be operative: an infimum over a domain that includes an endpoint the
search never visits is not the quantity any procedure computes, and the gap was being closed by
narrative rather than by arithmetic. The consolidated WIDE-reference pass replaces it with two
separate quantities that each have a procedure:

    D_WIDE = [0.15, 500]
    J_ref  = min over kappa in D_WIDE of J(kappa)      continuously minimised, finite domain
    J_inf  = min over I > 0 of MAPE(y, I * f_inf)      the analytical endpoint, evaluated separately

`J_ref` is the *reference* the operational thresholds are built from. The endpoint is not a member
of the minimisation; it is compared against the resulting threshold and classified. Nothing is
claimed about the open interval `(500, infinity)`: no finite topology is assigned to it and no
finite tail onset is estimated. Those are recorded as `tail_onset_status = unresolved_by_design` and
`intermediate_domain_status = not_characterized_by_design`, which are architectural statements, not
findings.

**This module reads no campaign data.** Every entry point takes a callable objective, so the
architecture can be exercised, and was exercised before the freeze, entirely on synthetic objective
functions. It imports nothing from :mod:`puckworks.data`, computes no `y`, and holds no group
definitions.

Four things are enforced structurally rather than by convention, because each is a defect the
earlier contract permitted:

* **The 40-point grid minimum is never the reported reference.** :func:`reference_minimum` returns a
  candidate produced by bounded scalar minimisation inside identified basins across four nested
  grids; the coarse-grid minimum is retained beside it as a diagnostic and is labelled as one.
* **The error budgets are per quantity, not one pooled sum.** :class:`ReferenceMinimumBudget`,
  :class:`EndpointBudget` and :class:`ShoulderBudget` have disjoint field sets, so a finite-kappa
  remainder, an inventory tie width, a finite-domain search error or a shoulder step error has
  nowhere to go in the endpoint interval. That is the dimensional error Protocol V2 made, and a
  dataclass with four named slots is a stronger guard than a sentence asking nobody to make it.
* **No component adjoining the endpoint is representable.** A connected component is reported only
  within `[0.15, 500]`; :func:`validate_components` rejects a non-finite or out-of-domain bound, so
  an invented `[kappa_c, infinity]` cannot be serialised even by a caller that wants to.
* **The programme result is derived, never declared.** :func:`validate_archive` requires exactly six
  uniquely identified groups and recomputes the label from their records through the frozen rule. A
  correct rule that nothing calls is not a control: for one review cycle this validator checked only
  that `programme_result` was one of three strings, so an archive could carry six excluded groups
  and declare `H1_STRONG`.

The eventual-upper vocabulary is emitted, but it is *conditional*: reading
`wide_referenced_upper_set_unbounded` as a statement about arbitrarily large multipliers requires
the fixed-positive-time limit result, which is a separate deferred derivation. Every archive
therefore declares :data:`EVENTUAL_UPPER_PRECONDITION` and the status of that precondition —
`unresolved`, `assured` or `failed` — so the enumerated value cannot be read as self-supporting. A
`failed` precondition does not merely block the prose: it collapses every `eventual_upper_status` to
`upper_status_indeterminate`, because an inference cannot outlive a refuted premise.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Iterable, Sequence

import numpy as np
from scipy.optimize import brentq, minimize_scalar

# ─────────────────────────────────────────────────────────────────────────────────────────────
# Frozen domain, grids, threshold families
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: Published rate domain, retained for reference only. Not the reference domain.
D_PUB = (0.15, 6.5)

#: The WIDE reference domain. The reference minimum is taken over exactly this interval.
D_WIDE = (0.15, 500.0)

#: Estimand tag for a threshold referenced to `J_ref` with the endpoint evaluated separately.
ESTIMAND_TAG = "FULL-WIDE-ENDPOINT"

#: Retained for finite-domain results that make no endpoint statement.
FINITE_DOMAIN_ESTIMAND_TAG = "FULL-WIDE"

#: Nested log-spaced grid sizes on `D_WIDE`, frozen. Changing these is a protocol deviation.
GRID_SIZES = (40, 80, 160, 320)

#: Relative threshold family: `T_rel(q) = (1 + q) * J_ref`.
RELATIVE_Q = (0.05, 0.10, 0.20)

#: Absolute threshold family: `T_abs(a) = J_ref + a`, in percentage points.
ABSOLUTE_A = (0.10, 0.25)

#: Below this reference upper bound (percentage points) the relative convention is not applicable:
#: a noiseless synthetic control can drive `J_ref` toward zero, where a ratio carries no tolerance.
NEAR_ZERO_PP = 0.05


@dataclass(frozen=True)
class Convention:
    """One member of a threshold family."""

    name: str
    kind: str          # "relative" | "absolute"
    level: float       # q for relative, a (percentage points) for absolute


CONVENTIONS = (
    Convention("rel_q005", "relative", 0.05),
    Convention("rel_q010", "relative", 0.10),
    Convention("rel_q020", "relative", 0.20),
    Convention("abs_a010", "absolute", 0.10),
    Convention("abs_a025", "absolute", 0.25),
)

#: The relative convention the programme rule is stated on.
PRIMARY_RELATIVE = "rel_q010"

#: The absolute conventions the programme rule is stated on.
ABSOLUTE_CONVENTIONS = ("abs_a010", "abs_a025")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Numerical stability tolerances — assigned explicit values here, before the freeze
# ─────────────────────────────────────────────────────────────────────────────────────────────
#
# Every tolerance the implementation needs is named and given a value in this block, so that none
# is chosen while looking at a campaign profile. The coordinate is natural `log kappa` throughout;
# objective tolerances are in percentage points, matching §1.1 of the protocol. All of them are
# fail-closed: violating one returns `unresolved`, never a best guess.

#: Bounded scalar minimisation inside a basin, absolute tolerance in `log kappa`.
MIN_XATOL_LOGKAPPA = 1e-8

#: A basin is retained as tied or near-tied with the best one when its value is within
#: `BASIN_TIE_RTOL * |best| + BASIN_TIE_ATOL`.
BASIN_TIE_RTOL = 1e-3
BASIN_TIE_ATOL = 1e-12

#: Two minimiser locations closer than this in `log kappa` are the same basin.
BASIN_MERGE_DLOG = 1e-6

#: Refinement-to-refinement stability of the best value: `|dJ| <= REF_VALUE_RTOL * |J| +
#: REF_VALUE_ATOL` is required on each of the final two transitions.
REF_VALUE_RTOL = 1e-4
REF_VALUE_ATOL = 1e-9

#: Refinement-to-refinement stability of the retained minimiser set, in `log kappa`, required on
#: the final transition. The whole tied set is compared, not only the argmin, so a genuine tie that
#: swaps which basin holds the argmin does not read as instability.
REF_LOCATION_DLOG = 1e-3

#: Floor for the deterministic search-convergence envelope, in percentage points.
E_REF_SEARCH_FLOOR = 1e-12

#: Bisection tolerance for a threshold root, in `log kappa`.
ROOT_XTOL_LOGKAPPA = 1e-8

#: A local minimum of `J - T` that stays positive but within `TANGENCY_RTOL * T` of zero is a
#: tangency: the sign never changes, so no root is bracketed, yet the component structure is not
#: decided. It is returned unresolved rather than merged away or discarded.
TANGENCY_RTOL = 1e-3

#: Roots on successive grids are matched within this distance in `log kappa`.
ROOT_MATCH_DLOG = 1e-3


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Result vocabulary
# ─────────────────────────────────────────────────────────────────────────────────────────────

REFERENCE_MINIMUM_STATUSES = ("resolved", "unresolved")

FINITE_WIDE_TOPOLOGY_STATUSES = ("resolved", "unresolved")

ENDPOINT_CLASSIFICATIONS = (
    "endpoint_included",
    "endpoint_excluded",
    "endpoint_indeterminate",
    "limit_construction_failed",
)

EVENTUAL_UPPER_STATUSES = (
    "wide_referenced_upper_set_unbounded",
    "wide_referenced_eventually_excluded",
    "upper_status_indeterminate",
)

TAIL_ONSET_STATUSES = (
    "unresolved_by_design",
    "certified_in_separate_analysis",
    "not_applicable",
)

INTERMEDIATE_DOMAIN_STATUSES = ("not_characterized_by_design",)

#: The relative convention returns this instead of a classification when `U_ref` is near zero.
RELATIVE_NOT_APPLICABLE = "relative_threshold_not_applicable_near_zero"

#: Values the current protocol fixes. A producer that writes anything else for these two fields is
#: claiming work this protocol does not do.
PROTOCOL_TAIL_ONSET_STATUS = "unresolved_by_design"
PROTOCOL_INTERMEDIATE_DOMAIN_STATUS = "not_characterized_by_design"

#: The eventual-upper vocabulary is only readable as a statement about arbitrarily large
#: multipliers once the fixed-positive-time limit result exists. Until then the enumerated value
#: records the classification and nothing more, and the archive says so in this field.
EVENTUAL_UPPER_PRECONDITION = "fixed_positive_time_limit"

#: Assurance vocabulary for that precondition, with frozen semantics:
#:
#: * `unresolved` — the conditional machine value may be retained, but it cannot become
#:   reader-facing eventual-upper prose;
#: * `assured` — the fixed-positive-time proposition has passed, so the endpoint-to-eventual-upper
#:   mapping may support scoped reader-facing language;
#: * `failed` — the endpoint classification remains reportable, but every `eventual_upper_status`
#:   is forced to `upper_status_indeterminate`: no eventual inference survives a failed premise.
#:
#: The `failed` state is the one the earlier two-token vocabulary could not express at all. A
#: proposition that is attempted and refuted is not the same as one not yet attempted, and without a
#: token for it the only way to record refutation would have been to leave the field saying "not yet
#: established" — which reads as pending and would have let the mapping survive its own premise.
EVENTUAL_UPPER_PRECONDITION_STATUSES = ("unresolved", "assured", "failed")

#: The current value. Set to `assured` on 2026-08-03 when PR-03a closed on a proof of the
#: fixed-positive-time singular limit, with its assumptions verified at every declared cell — see
#: `PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md`. This is a STATE declaration, not architecture:
#: no vocabulary, formula, threshold, tolerance or rule in this module changes with it.
EVENTUAL_UPPER_PRECONDITION_CURRENT = "assured"

#: Group-level outcomes under the programme rule.
GROUP_OUTCOMES = ("success", "exception", "failure")

PROGRAMME_RESULTS = ("H1_STRONG", "H1_QUALIFIED", "H1_DOES_NOT_LEAD")

#: The six variety-solute groups: {Arabica, Robusta} x {caffeine, trigonelline, 5-CQA}. The archive
#: carries exactly this many, uniquely identified. The count is fixed by the evidence unit, not by
#: how many happened to be produced.
N_GROUPS = 6


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Quantity-specific error budgets
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ReferenceMinimumBudget:
    """Error components of the finite reference minimum, in percentage points.

    `E_ref_profile_arithmetic` is the arithmetic error of the exact weighted-median profiling — the
    floating-point cost of forming the objective at a level that is already the exact minimiser. It
    is **not** the weighted-median tie width: the objective is exactly constant across the tie
    interval, so the tie width is inventory-level identification information in inventory units and
    carries no percentage-point error at all.
    """

    E_ref_response: float
    E_ref_spatial: float
    E_ref_profile_arithmetic: float
    E_ref_floating: float
    E_ref_search: float

    @property
    def evaluation_error(self) -> float:
        """Everything that perturbs a single evaluation, excluding the search envelope."""
        return (self.E_ref_response + self.E_ref_spatial
                + self.E_ref_profile_arithmetic + self.E_ref_floating)


@dataclass(frozen=True)
class EndpointBudget:
    """Error components of the analytical endpoint, in percentage points.

    Four slots and no others. At `kappa = infinity` the asymptotic remainder is zero, so a finite
    `C/kappa` term is not an uncertainty in `J_inf` — it localises where a tail begins, which is a
    different question and is not asked here. The finite-domain search envelope and the response
    shoulder likewise belong to other quantities and have no field in this class.
    """

    E_endpoint_construction: float
    E_endpoint_spatial: float
    E_endpoint_profile_arithmetic: float
    E_endpoint_floating: float

    @property
    def total(self) -> float:
        return (self.E_endpoint_construction + self.E_endpoint_spatial
                + self.E_endpoint_profile_arithmetic + self.E_endpoint_floating)


@dataclass(frozen=True)
class ShoulderBudget:
    """Error components of the response shoulder. It enters no objective and no threshold."""

    E_shoulder_step: float
    E_shoulder_spatial: float
    E_shoulder_floating: float

    @property
    def total(self) -> float:
        return self.E_shoulder_step + self.E_shoulder_spatial + self.E_shoulder_floating


def _clip_interval(lo: float, hi: float) -> tuple[float, float]:
    """Intersect an interval with `[0, infinity)`. Objectives and thresholds are nonnegative."""
    lo, hi = float(lo), float(hi)
    if hi < lo:
        raise ValueError("interval bounds are inverted: [%g, %g]" % (lo, hi))
    return max(0.0, lo), max(0.0, hi)


def reference_interval(candidate: float, budget: ReferenceMinimumBudget) -> tuple[float, float]:
    """Deterministic numerical convergence envelope for `J_ref`.

    This is **not** a mathematically certified global interval. The upper bound is honest — an
    evaluated candidate really does bound the minimum from above, up to its own evaluation error.
    The lower bound subtracts a search-convergence envelope measured from the refinement sequence,
    which is a statement about how the procedure settled, not a proof that no lower basin exists
    off the sampled set.
    """
    e = budget.evaluation_error
    return _clip_interval(candidate - e - budget.E_ref_search, candidate + e)


def endpoint_interval(j_inf_hat: float, budget: EndpointBudget) -> tuple[float, float]:
    """`J_inf` interval from the endpoint budget alone."""
    return _clip_interval(j_inf_hat - budget.total, j_inf_hat + budget.total)


def threshold_interval(reference: tuple[float, float], convention: Convention) -> tuple[float, float]:
    """Propagate the `J_ref` interval through one threshold convention."""
    lo, hi = _clip_interval(*reference)
    if convention.kind == "relative":
        return _clip_interval((1.0 + convention.level) * lo, (1.0 + convention.level) * hi)
    if convention.kind == "absolute":
        return _clip_interval(lo + convention.level, hi + convention.level)
    raise ValueError("unknown convention kind %r" % (convention.kind,))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Finite WIDE minimisation
# ─────────────────────────────────────────────────────────────────────────────────────────────


def nested_grids(domain: tuple[float, float] = D_WIDE,
                 sizes: Sequence[int] = GRID_SIZES) -> tuple[np.ndarray, ...]:
    """The frozen nested log-spaced grids on the domain."""
    lo, hi = domain
    return tuple(np.geomspace(lo, hi, n) for n in sizes)


def _basin_brackets(u: np.ndarray, j: np.ndarray) -> list[tuple[float, float]]:
    """Every sampled local basin, as a bracket in `log kappa`.

    A boundary basin is bracketed by the single adjacent interval, which is why the domain
    endpoints are also evaluated directly: a bounded minimiser will not return the boundary itself.
    """
    out: list[tuple[float, float]] = []
    n = len(u)
    if n < 3:
        return [(float(u[0]), float(u[-1]))]
    if j[0] <= j[1]:
        out.append((float(u[0]), float(u[1])))
    for i in range(1, n - 1):
        if j[i] <= j[i - 1] and j[i] <= j[i + 1]:
            out.append((float(u[i - 1]), float(u[i + 1])))
    if j[-1] <= j[-2]:
        out.append((float(u[-2]), float(u[-1])))
    return out


def _merge_candidates(candidates: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """Collapse minimisers that landed in the same basin, keeping the lower value."""
    kept: list[tuple[float, float]] = []
    for u_star, j_star in sorted(candidates):
        if kept and abs(u_star - kept[-1][0]) <= BASIN_MERGE_DLOG:
            if j_star < kept[-1][1]:
                kept[-1] = (u_star, j_star)
            continue
        kept.append((u_star, j_star))
    return kept


@dataclass
class RefinementRecord:
    """What one grid of the nested sequence produced."""

    size: int
    grid_minimum: float                       # diagnostic only; never reported as J_ref
    grid_argmin: float
    best_value: float                         # after bounded minimisation in every basin
    retained: list[tuple[float, float]]       # (log kappa, J) for the tied / near-tied set
    n_basins: int


@dataclass
class ReferenceMinimum:
    """Outcome of the frozen finite-domain search."""

    status: str                               # resolved | unresolved
    candidate: float | None                   # J_ref point candidate, refined
    minimisers: list[float]                   # kappa locations of the retained tied set
    search_envelope: float                    # E_ref_search
    refinements: list[RefinementRecord]
    reasons: list[str] = field(default_factory=list)

    @property
    def coarse_grid_minimum(self) -> float:
        """The 40-point grid minimum. Kept as a diagnostic; it is never `J_ref`."""
        return self.refinements[0].grid_minimum


def reference_minimum(objective: Callable[[float], float],
                      *,
                      domain: tuple[float, float] = D_WIDE,
                      sizes: Sequence[int] = GRID_SIZES) -> ReferenceMinimum:
    """Continuously minimise `objective` over the finite WIDE domain, fail-closed.

    At every refinement: both domain endpoints are evaluated; every sampled local basin is
    identified; bounded scalar minimisation runs in every basin; tied and near-tied basins are
    retained; the best value and the retained minimiser set are compared against the previous
    refinement; and the search-convergence envelope is calculated from those comparisons. If the
    frozen stability criteria are not met the status is `unresolved` and no candidate is returned.
    """
    if tuple(sizes) != tuple(GRID_SIZES):
        raise ValueError("the nested grid sizes are frozen at %r" % (GRID_SIZES,))

    lo, hi = domain
    log_objective = lambda u: float(objective(math.exp(u)))
    records: list[RefinementRecord] = []

    for grid in nested_grids(domain, sizes):
        u = np.log(grid)
        j = np.asarray([objective(float(k)) for k in grid], float)

        candidates: list[tuple[float, float]] = [
            (float(u[0]), float(objective(lo))),          # step 1: both domain endpoints
            (float(u[-1]), float(objective(hi))),
        ]
        brackets = _basin_brackets(u, j)
        for ulo, uhi in brackets:                          # steps 2-3: minimise in every basin
            res = minimize_scalar(log_objective, bounds=(ulo, uhi), method="bounded",
                                  options={"xatol": MIN_XATOL_LOGKAPPA})
            candidates.append((float(res.x), float(res.fun)))

        candidates = _merge_candidates(candidates)
        best = min(v for _, v in candidates)
        tol = BASIN_TIE_RTOL * abs(best) + BASIN_TIE_ATOL
        retained = [(uu, vv) for uu, vv in candidates if vv <= best + tol]   # step 4

        records.append(RefinementRecord(
            size=len(grid), grid_minimum=float(j.min()), grid_argmin=float(grid[int(j.argmin())]),
            best_value=best, retained=retained, n_basins=len(brackets)))

    # ── step 5: compare across refinements ───────────────────────────────────────────────────
    reasons: list[str] = []
    deltas = [abs(records[i].best_value - records[i - 1].best_value)
              for i in range(1, len(records))]
    for i, d in enumerate(deltas[-2:], start=len(deltas) - 2):
        scale = REF_VALUE_RTOL * abs(records[i + 1].best_value) + REF_VALUE_ATOL
        if d > scale:
            reasons.append("best value moved by %.3e between the %d- and %d-point grids, above the "
                           "frozen %.3e" % (d, records[i].size, records[i + 1].size, scale))

    final, previous = records[-1], records[-2]
    if len(final.retained) != len(previous.retained):
        reasons.append("the retained minimiser set changed size across the final refinement "
                       "(%d -> %d)" % (len(previous.retained), len(final.retained)))
    else:
        for (u_prev, _), (u_now, _) in zip(sorted(previous.retained), sorted(final.retained)):
            if abs(u_prev - u_now) > REF_LOCATION_DLOG:
                reasons.append("a retained minimiser moved by %.3e in log kappa across the final "
                               "refinement, above the frozen %.3e"
                               % (abs(u_prev - u_now), REF_LOCATION_DLOG))

    # ── step 6: the deterministic search-convergence envelope ────────────────────────────────
    envelope = max(max(deltas[-2:]), E_REF_SEARCH_FLOOR)

    if reasons:                                            # step 7: fail closed
        return ReferenceMinimum("unresolved", None, [], envelope, records, reasons)

    minimisers = [math.exp(uu) for uu, _ in sorted(final.retained)]
    return ReferenceMinimum("resolved", final.best_value, minimisers, envelope, records, [])


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Threshold topology on the finite domain
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass
class Component:
    """A connected component of `{kappa in D_WIDE : J(kappa) <= T}`.

    Bounds are always finite and always inside `D_WIDE`. A component reaching the upper edge is
    `upper_truncated_at_domain_edge`: the search stopped there, which is a property of the domain
    and not a property of the objective.
    """

    lo: float
    hi: float
    lower_censored: bool
    upper_truncated_at_domain_edge: bool

    def as_record(self) -> dict:
        return {"lo": self.lo, "hi": self.hi, "lower_censored": self.lower_censored,
                "upper_truncated_at_domain_edge": self.upper_truncated_at_domain_edge}


@dataclass
class Topology:
    """Outcome of the frozen finite-domain component search at one threshold."""

    status: str                                # resolved | unresolved
    components: list[Component]
    roots: list[float]
    tangencies: list[float]
    reasons: list[str] = field(default_factory=list)


def _roots_on_grid(g: Callable[[float], float], u: np.ndarray,
                   values: np.ndarray) -> tuple[list[float], list[str]]:
    """Every bracketed sign change, refined by bisection. Exact grid zeros are roots too."""
    roots: list[float] = []
    notes: list[str] = []
    for i in range(len(u) - 1):
        a, b = float(values[i]), float(values[i + 1])
        if a == 0.0:
            roots.append(float(u[i]))
            continue
        if a * b < 0.0:
            roots.append(float(brentq(g, u[i], u[i + 1], xtol=ROOT_XTOL_LOGKAPPA)))
    if values[-1] == 0.0:
        roots.append(float(u[-1]))
    merged: list[float] = []
    for r in sorted(roots):
        if merged and abs(r - merged[-1]) <= ROOT_MATCH_DLOG:
            continue
        merged.append(r)
    return merged, notes


def _tangencies(g: Callable[[float], float], u: np.ndarray, values: np.ndarray,
                threshold: float) -> tuple[list[float], list[str]]:
    """Interior local minima of `J - T` that sit near zero without changing sign.

    Two things are unresolved here, and both are returned rather than absorbed: a minimum that
    stays positive but within the frozen relative band of zero, and a minimum that is negative
    although the grid showed no sign change — the latter means the grid missed a component, which
    is a statement about the grid, not about the profile.
    """
    found: list[float] = []
    notes: list[str] = []
    band = TANGENCY_RTOL * abs(threshold)
    for i in range(1, len(u) - 1):
        if not (values[i] <= values[i - 1] and values[i] <= values[i + 1]):
            continue
        if values[i] <= 0.0:
            continue      # the grid already sampled inside the accepted set; the component is
                          # bracketed by sign changes on both sides and was refined above
        res = minimize_scalar(g, bounds=(float(u[i - 1]), float(u[i + 1])), method="bounded",
                              options={"xatol": MIN_XATOL_LOGKAPPA})
        if res.fun < 0.0:
            found.append(float(res.x))
            notes.append("a refined local minimum at kappa=%.6g is below the threshold although "
                         "the grid showed no sign change: the grid missed a component"
                         % math.exp(float(res.x)))
        elif res.fun <= band:
            found.append(float(res.x))
            notes.append("a local minimum at kappa=%.6g touches the threshold to within the frozen "
                         "%.1e relative band without changing sign"
                         % (math.exp(float(res.x)), TANGENCY_RTOL))
    return found, notes


def _components(u_lo: float, u_hi: float, roots: Sequence[float],
                sign_at_lo: float) -> list[Component]:
    """Assemble the accepted set from the refined roots and the sign at the lower edge."""
    edges = [u_lo, *roots, u_hi]
    out: list[Component] = []
    inside = sign_at_lo <= 0.0
    for i in range(len(edges) - 1):
        if inside:
            lo, hi = math.exp(edges[i]), math.exp(edges[i + 1])
            out.append(Component(lo=lo, hi=hi,
                                 lower_censored=(i == 0),
                                 upper_truncated_at_domain_edge=(i == len(edges) - 2)))
        inside = not inside
    return out


def finite_topology(objective: Callable[[float], float], threshold: float,
                    *,
                    domain: tuple[float, float] = D_WIDE,
                    sizes: Sequence[int] = GRID_SIZES) -> Topology:
    """Every connected component of the accepted set within `D_WIDE`, fail-closed.

    Sign changes are detected on each nested grid and every detected root is refined; tangency
    checks run explicitly; roots and components are compared across refinements; lower-boundary
    censoring is retained; and components are reported only within the finite domain. If the frozen
    stability criteria fail the status is `unresolved` — never a single interval by default.
    """
    g = lambda u: float(objective(math.exp(u))) - threshold
    per_grid: list[tuple[list[float], list[float], list[str]]] = []

    for grid in nested_grids(domain, sizes):
        u = np.log(grid)
        values = np.asarray([g(float(uu)) for uu in u], float)
        roots, _ = _roots_on_grid(g, u, values)
        tang, notes = _tangencies(g, u, values, threshold)
        per_grid.append((roots, tang, notes))

    reasons: list[str] = []
    roots_final, tang_final, notes_final = per_grid[-1]
    roots_prev = per_grid[-2][0]

    reasons.extend(notes_final)                            # an unresolved tangency is a reason
    if len(roots_final) != len(roots_prev):
        reasons.append("the root count changed across the final refinement (%d -> %d)"
                       % (len(roots_prev), len(roots_final)))
    else:
        for a, b in zip(roots_prev, roots_final):
            if abs(a - b) > ROOT_MATCH_DLOG:
                reasons.append("a root moved by %.3e in log kappa across the final refinement, "
                               "above the frozen %.3e" % (abs(a - b), ROOT_MATCH_DLOG))

    u_lo, u_hi = math.log(domain[0]), math.log(domain[1])
    components = _components(u_lo, u_hi, roots_final, g(u_lo))
    tangencies = [math.exp(t) for t in tang_final]

    status = "unresolved" if reasons else "resolved"
    return Topology(status, components, [math.exp(r) for r in roots_final], tangencies, reasons)


def validate_components(components: Iterable[dict]) -> None:
    """Reject any component that leaves the finite domain.

    Protocol V2 §2.7 used to admit an explicit `[kappa_c, infinity]` component whenever the endpoint
    was included. Under the WIDE reference no finite topology is claimed for `(500, infinity)`, so
    that object does not exist and must not be serialisable.
    """
    lo_d, hi_d = D_WIDE
    for i, c in enumerate(components):
        for key in ("lo", "hi"):
            v = c.get(key)
            if isinstance(v, str) or v is None or not math.isfinite(float(v)):
                raise ValueError("component %d has a non-finite %s (%r); no component adjoining "
                                 "the endpoint exists under this protocol" % (i, key, v))
        lo, hi = float(c["lo"]), float(c["hi"])
        if lo < lo_d - 1e-12 or hi > hi_d + 1e-9 or hi < lo:
            raise ValueError("component %d spans [%g, %g], outside the reported domain [%g, %g]"
                             % (i, lo, hi, lo_d, hi_d))


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Endpoint classification
# ─────────────────────────────────────────────────────────────────────────────────────────────


def classify_endpoint(endpoint: tuple[float, float],
                      threshold: tuple[float, float]) -> str:
    """Interval comparison of `J_inf` against one threshold interval."""
    l_inf, u_inf = _clip_interval(*endpoint)
    l_t, u_t = _clip_interval(*threshold)
    if u_inf < l_t:
        return "endpoint_included"
    if l_inf > u_t:
        return "endpoint_excluded"
    return "endpoint_indeterminate"


def eventual_upper_status(classification: str,
                          precondition_status: str = "unresolved") -> str:
    """Map a classification to the eventual-upper vocabulary, gated by the precondition.

    The conclusion is conditional on the separately required fixed-positive-time limit; see
    :data:`EVENTUAL_UPPER_PRECONDITION`. While the precondition is `unresolved` the enumerated value
    records the endpoint comparison and carries no statement about arbitrarily large multipliers.
    If the precondition has `failed`, the mapping collapses: the endpoint classification is still
    reportable, but no eventual inference survives a refuted premise.
    """
    if precondition_status not in EVENTUAL_UPPER_PRECONDITION_STATUSES:
        raise ValueError("unknown precondition status %r" % (precondition_status,))
    if precondition_status == "failed":
        return "upper_status_indeterminate"
    if classification == "endpoint_included":
        return "wide_referenced_upper_set_unbounded"
    if classification == "endpoint_excluded":
        return "wide_referenced_eventually_excluded"
    if classification in ("endpoint_indeterminate", "limit_construction_failed"):
        return "upper_status_indeterminate"
    raise ValueError("unknown endpoint classification %r" % (classification,))


def classify_group(reference: tuple[float, float] | None,
                   endpoint: tuple[float, float] | None,
                   *,
                   reference_status: str,
                   endpoint_constructed: bool) -> dict[str, str]:
    """Classification under every convention, per group.

    An unresolved reference minimum blocks classification because it changes the threshold. A
    failed limit construction blocks it because there is no endpoint to compare.
    """
    if reference_status not in REFERENCE_MINIMUM_STATUSES:
        raise ValueError("unknown reference minimum status %r" % (reference_status,))
    if not endpoint_constructed:
        return {c.name: "limit_construction_failed" for c in CONVENTIONS}
    if reference_status == "unresolved" or reference is None or endpoint is None:
        return {c.name: "endpoint_indeterminate" for c in CONVENTIONS}

    _, u_ref = _clip_interval(*reference)
    near_zero = u_ref < NEAR_ZERO_PP

    out: dict[str, str] = {}
    for c in CONVENTIONS:
        if c.kind == "relative" and near_zero:
            out[c.name] = RELATIVE_NOT_APPLICABLE
            continue
        out[c.name] = classify_endpoint(endpoint, threshold_interval(reference, c))
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Programme-level H1 rule
# ─────────────────────────────────────────────────────────────────────────────────────────────


@dataclass
class GroupOutcome:
    name: str
    outcome: str                     # success | exception | failure
    reason: str


def group_outcome(name: str,
                  classifications: dict[str, str],
                  *,
                  reference_status: str,
                  endpoint_constructed: bool) -> GroupOutcome:
    """The frozen group-level rule.

    Success and exception are checked in that order, which decides the one case the prose leaves
    ambiguous: a group included under one absolute convention and indeterminate under the other
    **succeeds**, because the success rule asks for inclusion under *at least one* absolute
    convention and exclusion under neither. The exception branch only ever sees groups that already
    failed the success test.
    """
    if reference_status == "unresolved":
        return GroupOutcome(name, "failure", "the reference minimum is unresolved")
    if not endpoint_constructed:
        return GroupOutcome(name, "failure", "the endpoint construction failed")

    primary = classifications[PRIMARY_RELATIVE]
    absolutes = [classifications[a] for a in ABSOLUTE_CONVENTIONS]

    if primary == "endpoint_excluded":
        return GroupOutcome(name, "failure",
                            "excluded under the %s convention" % PRIMARY_RELATIVE)
    excluded_abs = [a for a, v in zip(ABSOLUTE_CONVENTIONS, absolutes)
                    if v == "endpoint_excluded"]
    if excluded_abs:
        return GroupOutcome(name, "failure",
                            "excluded under %s" % ", ".join(excluded_abs))

    if primary == "endpoint_included" and any(v == "endpoint_included" for v in absolutes):
        return GroupOutcome(name, "success",
                            "included under %s and at least one absolute convention, excluded "
                            "under neither" % PRIMARY_RELATIVE)

    if primary == RELATIVE_NOT_APPLICABLE:
        return GroupOutcome(name, "exception",
                            "the relative convention is not applicable near zero")
    return GroupOutcome(name, "exception", "a required convention is indeterminate")


def group_outcome_from_record(record: dict) -> GroupOutcome:
    """Recover the group-level outcome from an archive record.

    This is the join that was missing: :func:`group_outcome` and :func:`programme_result` were
    correct and independently tested, but nothing connected them to the archive, so
    `programme_result` was accepted as free text. An archive could carry six excluded groups and
    declare `H1_STRONG`.

    Two consistency conditions are checked here rather than assumed, because both are ways an
    archive could smuggle a better outcome past the rule:

    * `limit_construction_failed` is a property of the group's endpoint, not of one threshold, so it
      holds under every convention or under none. A record showing it under some conventions only is
      incoherent — it would let the derivation read the group as constructed.
    * an unresolved reference minimum moves the threshold, so it admits `endpoint_indeterminate` and
      nothing else. A record pairing it with `endpoint_included` is claiming a comparison against a
      threshold it does not have.
    """
    classifications = {name: value["endpoint_classification"]
                       for name, value in record["conventions"].items()}

    failed_limit = [v == "limit_construction_failed" for v in classifications.values()]
    if any(failed_limit) and not all(failed_limit):
        raise ValueError("limit_construction_failed must apply to every convention when endpoint "
                         "construction fails; group %r has it under only some"
                         % (record.get("group"),))
    endpoint_constructed = not all(failed_limit)

    if record["reference_minimum_status"] == "unresolved" and endpoint_constructed:
        invalid = {v for v in classifications.values() if v != "endpoint_indeterminate"}
        if invalid:
            raise ValueError("an unresolved reference minimum permits only endpoint_indeterminate "
                             "classifications; group %r carries %r"
                             % (record.get("group"), sorted(invalid)))

    return group_outcome(record["group"], classifications,
                         reference_status=record["reference_minimum_status"],
                         endpoint_constructed=endpoint_constructed)


def programme_result(outcomes: Sequence[GroupOutcome]) -> str:
    """`H1_STRONG` / `H1_QUALIFIED` / `H1_DOES_NOT_LEAD` from the group outcomes."""
    for o in outcomes:
        if o.outcome not in GROUP_OUTCOMES:
            raise ValueError("unknown group outcome %r" % (o.outcome,))
    n = len(outcomes)
    successes = sum(1 for o in outcomes if o.outcome == "success")
    exceptions = sum(1 for o in outcomes if o.outcome == "exception")
    failures = n - successes - exceptions

    if failures:
        return "H1_DOES_NOT_LEAD"
    if successes == n:
        return "H1_STRONG"
    if successes == n - 1 and exceptions == 1:
        return "H1_QUALIFIED"
    return "H1_DOES_NOT_LEAD"


def headline_requires_named_exception(result: str) -> bool:
    """`H1_QUALIFIED` names its exception in the same headline sentence."""
    return result == "H1_QUALIFIED"


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Archive schema
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: Fields every group record carries. Separated deliberately: the reference minimum, the finite
#: topology, the endpoint, the eventual upper status, the tail onset and the intermediate domain
#: are six different questions, and one pooled status field was how they got conflated before.
GROUP_RECORD_FIELDS = (
    "group",
    "estimand_tag",
    "reference_minimum_status",
    "finite_wide_topology_status",
    "tail_onset_status",
    "intermediate_domain_status",
    "conventions",
)

#: Fields every per-convention record carries.
CONVENTION_RECORD_FIELDS = (
    "endpoint_classification",
    "eventual_upper_status",
    "threshold_interval",
    "components",
)

_ENUMS = {
    "reference_minimum_status": REFERENCE_MINIMUM_STATUSES,
    "finite_wide_topology_status": FINITE_WIDE_TOPOLOGY_STATUSES,
    "tail_onset_status": TAIL_ONSET_STATUSES,
    "intermediate_domain_status": INTERMEDIATE_DOMAIN_STATUSES,
}


def validate_group_record(record: dict,
                          precondition_status: str = "unresolved") -> None:
    """Structural contract for one group in the P0-G8 archive."""
    for f in GROUP_RECORD_FIELDS:
        if f not in record:
            raise ValueError("group record is missing %r" % f)

    if record["estimand_tag"] != ESTIMAND_TAG:
        raise ValueError("a WIDE-referenced endpoint result carries %r, not %r"
                         % (ESTIMAND_TAG, record["estimand_tag"]))

    for f, allowed in _ENUMS.items():
        if record[f] not in allowed:
            raise ValueError("%s=%r is not in %r" % (f, record[f], allowed))

    if record["tail_onset_status"] != PROTOCOL_TAIL_ONSET_STATUS:
        raise ValueError("this protocol estimates no finite tail onset; tail_onset_status must be "
                         "%r" % PROTOCOL_TAIL_ONSET_STATUS)
    if record["intermediate_domain_status"] != PROTOCOL_INTERMEDIATE_DOMAIN_STATUS:
        raise ValueError("this protocol characterises no intermediate domain; "
                         "intermediate_domain_status must be %r"
                         % PROTOCOL_INTERMEDIATE_DOMAIN_STATUS)

    conventions = record["conventions"]
    expected = {c.name for c in CONVENTIONS}
    if set(conventions) != expected:
        raise ValueError("every threshold-family result is displayed; expected %r, got %r"
                         % (sorted(expected), sorted(conventions)))

    for name, cr in conventions.items():
        for f in CONVENTION_RECORD_FIELDS:
            if f not in cr:
                raise ValueError("convention %s is missing %r" % (name, f))
        cls = cr["endpoint_classification"]
        if cls not in ENDPOINT_CLASSIFICATIONS and cls != RELATIVE_NOT_APPLICABLE:
            raise ValueError("convention %s has endpoint_classification=%r" % (name, cls))
        if cls == RELATIVE_NOT_APPLICABLE:
            kind = next(c.kind for c in CONVENTIONS if c.name == name)
            if kind != "relative":
                raise ValueError("the near-zero branch is a relative-convention result; %s is %s"
                                 % (name, kind))
            if cr["eventual_upper_status"] != "upper_status_indeterminate":
                raise ValueError("a not-applicable relative convention decides no upper status")
        elif cr["eventual_upper_status"] != eventual_upper_status(cls, precondition_status):
            raise ValueError("convention %s: eventual_upper_status=%r contradicts %r under a "
                             "%s precondition"
                             % (name, cr["eventual_upper_status"], cls, precondition_status))
        validate_components(cr["components"])


def validate_archive(archive: dict) -> None:
    """Structural contract for the P0-G8 result archive.

    Producing this archive is a scientific gate and is not authorised in this pass; the contract
    exists so that the producer, when it is authorised, has a frozen shape to write into.

    The archive contains exactly six uniquely identified variety-solute groups, and
    `programme_result` is recomputed from those records through the frozen group-outcome rule and
    compared against the declared value. It is never accepted as an independent disposition.
    """
    for f in ("protocol_version", "estimand_tag", "reference_domain", "grid_sizes",
              "threshold_families", "eventual_upper_precondition",
              "eventual_upper_precondition_status", "groups", "programme_result"):
        if f not in archive:
            raise ValueError("archive is missing %r" % f)

    if archive["estimand_tag"] != ESTIMAND_TAG:
        raise ValueError("archive estimand tag is %r" % (archive["estimand_tag"],))
    if tuple(archive["reference_domain"]) != D_WIDE:
        raise ValueError("the reference domain is frozen at %r" % (D_WIDE,))
    if tuple(archive["grid_sizes"]) != GRID_SIZES:
        raise ValueError("the nested grid sizes are frozen at %r" % (GRID_SIZES,))
    if archive["eventual_upper_precondition"] != EVENTUAL_UPPER_PRECONDITION:
        raise ValueError("the eventual-upper vocabulary is conditional on %r"
                         % EVENTUAL_UPPER_PRECONDITION)
    if archive["eventual_upper_precondition_status"] not in EVENTUAL_UPPER_PRECONDITION_STATUSES:
        raise ValueError("eventual_upper_precondition_status=%r"
                         % (archive["eventual_upper_precondition_status"],))
    if archive["programme_result"] not in PROGRAMME_RESULTS:
        raise ValueError("programme_result=%r" % (archive["programme_result"],))

    families = archive["threshold_families"]
    if tuple(families.get("relative", ())) != RELATIVE_Q:
        raise ValueError("the relative family is frozen at %r" % (RELATIVE_Q,))
    if tuple(families.get("absolute", ())) != ABSOLUTE_A:
        raise ValueError("the absolute family is frozen at %r" % (ABSOLUTE_A,))

    for record in archive["groups"]:
        validate_group_record(record, archive["eventual_upper_precondition_status"])

    # ── the programme result is derived, never accepted as a free-text disposition ───────────
    if len(archive["groups"]) != N_GROUPS:
        raise ValueError("the P0-G8 archive requires exactly %d groups, got %d"
                         % (N_GROUPS, len(archive["groups"])))

    names = [record["group"] for record in archive["groups"]]
    if any(not isinstance(n, str) or not n.strip() for n in names):
        raise ValueError("every group requires a nonempty string identifier")
    if len(set(names)) != len(names):
        raise ValueError("group identifiers must be unique; got %r" % (sorted(names),))

    expected = programme_result([group_outcome_from_record(r) for r in archive["groups"]])
    if archive["programme_result"] != expected:
        raise ValueError("programme_result=%r contradicts group-derived result %r"
                         % (archive["programme_result"], expected))

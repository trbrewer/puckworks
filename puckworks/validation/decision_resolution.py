"""Opt-in, declarative comparisons; no scoring, inference, or certificate authentication.

See docs/governance/DECISION_RESOLUTION_POLICY.md. Numeric inputs are built-in
int/float or Decimal, preserved without coercion, rounding, or epsilon. Units
must already be canonical and identical; this module performs no conversions.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal
from fractions import Fraction
import json
import math
from typing import Literal, Mapping

Number = int | float | Decimal
Operator = Literal["<=", "<", ">=", ">"]
Verdict = Literal["PASS", "FAIL", "UNRESOLVED", "UNAVAILABLE"]
Relation = Literal["satisfies", "violates", "overlaps"]
Role = Literal["integrity", "precision", "reproduction", "adequacy", "increment", "count", "coverage"]
DecisionBasis = Literal["point", "applicable_bound", "finite_count", "complete_support"]
CountMeaning = Literal["point_contract", "applicable_bound", "tested_sensitivities"]


def _text(value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("nonempty explicit declaration required")


def _choice(value: str, options: tuple[str, ...]) -> None:
    if value not in options:
        raise ValueError(f"unsupported declaration: {value!r}; expected {options}")


def _number(value: Number) -> None:
    if type(value) not in (int, float, Decimal):
        raise TypeError("only built-in int, float and Decimal numeric inputs are supported")
    if isinstance(value, Decimal):
        finite = value.is_finite()
    else:
        finite = type(value) is int or math.isfinite(value)
    if not finite:
        raise ValueError("finite numeric input required")


def _integer(value: int) -> None:
    if type(value) is not int or value < 0:
        raise ValueError("nonnegative integer required (not bool)")


def _names(values: tuple[str, ...]) -> None:
    if type(values) is not tuple or len(set(values)) != len(values):
        raise ValueError("unique identities in an immutable tuple required")
    for value in values:
        _text(value)


def point_relation(value: Number, operator: Operator, threshold: Number) -> Relation:
    """Direct comparison of supplied numbers, independent of their meaning."""
    _number(value)
    _number(threshold)
    _choice(operator, ("<=", "<", ">=", ">"))
    # Exact ratios preserve binary floats and decimal digits without consulting
    # or changing the caller's Decimal context (including FloatOperation traps).
    left, right = Fraction(value), Fraction(threshold)
    satisfied = {"<=": left <= right, "<": left < right,
                 ">=": left >= right, ">": left > right}[operator]
    return "satisfies" if satisfied else "violates"


@dataclass(frozen=True)
class Interval:
    lower: Number
    upper: Number

    def __post_init__(self) -> None:
        _number(self.lower)
        _number(self.upper)
        if Fraction(self.lower) > Fraction(self.upper):
            raise ValueError("inverted interval")


def interval_relation(bounds: Interval, operator: Operator, threshold: Number) -> Relation:
    """Closed-interval relation, with the requirement's exact strictness."""
    lo = point_relation(bounds.lower, operator, threshold)
    hi = point_relation(bounds.upper, operator, threshold)
    return lo if lo == hi else "overlaps"


@dataclass(frozen=True)
class Scope:
    observable: str
    units: str
    domain: str
    estimand: str
    aggregation: str
    information: str
    # (scored member, physical unit); repeated physical units remain explicit.
    support: tuple[tuple[str, str], ...]
    eligibility: str
    exclusions: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        for value in (self.observable, self.units, self.domain, self.estimand,
                      self.aggregation, self.information, self.eligibility):
            _text(value)
        for pairs in (self.support, self.exclusions):
            if type(pairs) is not tuple:
                raise ValueError("immutable support/exclusions required")
            for pair in pairs:
                if type(pair) is not tuple or len(pair) != 2:
                    raise ValueError("identity and physical unit/reason required")
                for value in pair:
                    _text(value)
            _names(tuple(key for key, _ in pairs))
        if not self.support or set(self.members) & {key for key, _ in self.exclusions}:
            raise ValueError("nonempty eligible support disjoint from exclusions required")
        object.__setattr__(self, "support", tuple(sorted(self.support)))
        object.__setattr__(self, "exclusions", tuple(sorted(self.exclusions)))

    @property
    def members(self) -> tuple[str, ...]:
        return tuple(key for key, _ in self.support)


@dataclass(frozen=True)
class Requirement:
    identity: str
    controlling: bool
    role: Role
    scope: Scope
    operator: Operator
    threshold: Number
    purpose: str
    threshold_basis: str
    approval: Literal["approved", "proposed", "undocumented"]
    decision_basis: DecisionBasis
    resolution_components: tuple[str, ...]
    claim_limits: tuple[str, ...]
    comparator: str | None = None
    count_meaning: CountMeaning | None = None

    def __post_init__(self) -> None:
        for value in (self.identity, self.purpose, self.threshold_basis):
            _text(value)
        if type(self.controlling) is not bool:
            raise TypeError("controlling must be bool")
        _choice(self.role, ("integrity", "precision", "reproduction", "adequacy",
                            "increment", "count", "coverage"))
        _choice(self.approval, ("approved", "proposed", "undocumented"))
        _choice(self.decision_basis, ("point", "applicable_bound", "finite_count", "complete_support"))
        if self.role == "count" and self.decision_basis != "finite_count":
            raise ValueError("count role requires explicit finite_count basis and member accounting")
        if self.role == "coverage" and self.decision_basis != "complete_support":
            raise ValueError("coverage role requires explicit complete_support basis")
        point_relation(self.threshold, self.operator, self.threshold)
        _names(self.resolution_components)
        _names(self.claim_limits)
        if not self.claim_limits:
            raise ValueError("explicit claim limits required")
        if self.role == "increment":
            _text(self.comparator)  # type: ignore[arg-type]
        if self.decision_basis in ("finite_count", "complete_support"):
            _integer(self.threshold)  # type: ignore[arg-type]
            if self.operator != ">=" or self.threshold > len(self.scope.members):
                raise ValueError("count/coverage requires >= integer k within fixed support")
        if self.decision_basis == "finite_count":
            if self.role != "count":
                raise ValueError("finite_count requires count role")
            _choice(self.count_meaning, ("point_contract", "applicable_bound", "tested_sensitivities"))  # type: ignore[arg-type]
        elif self.count_meaning is not None:
            raise ValueError("count meaning only applies to finite_count")
        if self.decision_basis == "complete_support" and (
            self.role != "coverage" or self.threshold != len(self.scope.members)
        ):
            raise ValueError("complete_support requires coverage role and k=N")
        if self.decision_basis == "applicable_bound" and not self.resolution_components:
            raise ValueError("bound contract requires explicit uncertainty components")
        object.__setattr__(self, "resolution_components", tuple(sorted(self.resolution_components)))


@dataclass(frozen=True)
class Basis:
    kind: Literal["analytic", "numerical", "allowance", "sensitivity", "descriptive", "unavailable"]
    scope: Scope
    argument: str
    components: tuple[str, ...]
    assumptions: tuple[str, ...]
    tested_sensitivities: tuple[str, ...] = ()
    full_support_justification: str | None = None

    def __post_init__(self) -> None:
        _choice(self.kind, ("analytic", "numerical", "allowance", "sensitivity", "descriptive", "unavailable"))
        _text(self.argument)
        for names in (self.components, self.assumptions, self.tested_sensitivities):
            _names(names)
        if self.kind in ("analytic", "numerical", "allowance") and not self.components:
            raise ValueError("bound basis must identify covered uncertainty components")
        if self.kind == "allowance" and not self.assumptions:
            raise ValueError("allowance requires explicit conditional assumptions")
        if (self.kind == "sensitivity") != bool(self.tested_sensitivities):
            raise ValueError("tested sensitivities belong only to a sensitivity basis")
        if self.full_support_justification is not None:
            _text(self.full_support_justification)
        object.__setattr__(self, "components", tuple(sorted(self.components)))


@dataclass(frozen=True)
class Quality:
    admissible: bool
    source_identity: bool
    payload_integrity: bool
    numerical_integrity: bool
    explanation: str

    def __post_init__(self) -> None:
        if any(type(value) is not bool for value in (
            self.admissible, self.source_identity, self.payload_integrity, self.numerical_integrity
        )):
            raise TypeError("quality declarations must be bool")
        _text(self.explanation)

    @property
    def usable(self) -> bool:
        return all((self.admissible, self.source_identity, self.payload_integrity, self.numerical_integrity))


@dataclass(frozen=True)
class Counts:
    N: int
    D: int
    P: int
    # Every eligible member occurs exactly once, including missing members.
    members: tuple[tuple[str, Literal["definite", "possible", "failure", "missing"]], ...]
    meaning: CountMeaning
    success_definition: str

    def __post_init__(self) -> None:
        for value in (self.N, self.D, self.P):
            _integer(value)
        if not 0 <= self.D <= self.P <= self.N or self.N == 0:
            raise ValueError("count requires 0 <= D <= P <= N and N > 0")
        if type(self.members) is not tuple:
            raise ValueError("immutable member accounting required")
        if any(type(pair) is not tuple or len(pair) != 2 for pair in self.members):
            raise ValueError("immutable two-item member pairs required")
        _names(tuple(key for key, _ in self.members))
        for _, state in self.members:
            _choice(state, ("definite", "possible", "failure", "missing"))
        if (len(self.members) != self.N
            or sum(state == "definite" for _, state in self.members) != self.D
            or sum(state != "failure" for _, state in self.members) != self.P):
            raise ValueError("inconsistent D/P/N/member accounting; P includes missing and D")
        _choice(self.meaning, ("point_contract", "applicable_bound", "tested_sensitivities"))
        _text(self.success_definition)
        object.__setattr__(self, "members", tuple(sorted(self.members)))


@dataclass(frozen=True)
class Evidence:
    kind: Literal["bound", "sensitivity", "point", "unavailable", "count", "coverage"]
    scope: Scope
    basis: Basis
    observed_support: tuple[str, ...]
    quality: Quality
    unknown_components: tuple[str, ...]
    point: Number | None = None
    interval: Interval | None = None
    counts: Counts | None = None

    def __post_init__(self) -> None:
        _choice(self.kind, ("bound", "sensitivity", "point", "unavailable", "count", "coverage"))
        _names(self.observed_support)
        _names(self.unknown_components)
        if not set(self.observed_support) <= set(self.scope.members):
            raise ValueError("observed support outside declared scope")
        if set(self.unknown_components) & set(self.basis.components):
            raise ValueError("a covered uncertainty component cannot also be unknown")
        if self.point is not None:
            _number(self.point)
        if (self.kind in ("bound", "sensitivity")) != (self.interval is not None):
            raise ValueError("only bound/sensitivity evidence carries a supplied interval")
        if self.kind == "bound" and self.basis.kind not in ("analytic", "numerical", "allowance"):
            raise ValueError("bound requires compatible analytical/numerical/allowance basis")
        if self.kind == "sensitivity" and self.basis.kind != "sensitivity":
            raise ValueError("sensitivity basis required")
        if self.kind == "point" and self.point is None:
            raise ValueError("point evidence requires a point")
        if (self.kind == "count") != (self.counts is not None):
            raise ValueError("count evidence requires counts and only counts may carry them")
        if self.kind in ("count", "coverage", "unavailable") and self.point is not None:
            raise ValueError("scalar point not applicable to count/coverage/unavailable")
        if self.counts is not None:
            if {key for key, _ in self.counts.members} != set(self.scope.members):
                raise ValueError("count denominator differs from declared eligible support")
            if {key for key, state in self.counts.members if state != "missing"} != set(self.observed_support):
                raise ValueError("missing member accounting differs from observed support")
            if self.counts.meaning == "applicable_bound" and self.basis.kind not in ("analytic", "numerical", "allowance"):
                raise ValueError("bound-resolved counts require a bound basis")
            if self.counts.meaning == "tested_sensitivities" and self.basis.kind != "sensitivity":
                raise ValueError("sensitivity counts require a sensitivity basis")
        object.__setattr__(self, "observed_support", tuple(sorted(self.observed_support)))
        object.__setattr__(self, "unknown_components", tuple(sorted(self.unknown_components)))


@dataclass(frozen=True)
class Decision:
    requirement: Requirement
    evidence: Evidence | None
    point_relation: Relation | None
    range_relation: Relation | None
    count_relation: Relation | None
    contractual: Verdict
    resolution: Verdict
    interpretation: str
    support_complete: bool
    assessment_complete: bool
    reliance_blocked: bool
    limitations: tuple[str, ...]


def _verdict(relation: Relation) -> Verdict:
    return {"satisfies": "PASS", "violates": "FAIL", "overlaps": "UNRESOLVED"}[relation]  # type: ignore[return-value]


def evaluate(requirement: Requirement, evidence: Evidence | None) -> Decision:
    """Check declared compatibility, never authenticate a certificate or source.

    Raw relations survive incompatibility as diagnostic arithmetic. Contractual
    reliance and supported interpretation are unavailable on affected evidence.
    """
    r, e = requirement, evidence
    limits = list(r.claim_limits)
    if r.approval != "approved":
        limits.append("Threshold basis not approved: contractual comparison only; no practical-value/adoption claim.")
    if e is None:
        return Decision(r, None, None, None, None, "UNAVAILABLE", "UNAVAILABLE", "Required evidence missing.",
                        False, False, False, tuple(limits))
    pr = point_relation(e.point, r.operator, r.threshold) if e.point is not None else None
    ir = interval_relation(e.interval, r.operator, r.threshold) if e.interval is not None else None
    cr: Relation | None = None
    if e.counts is not None and r.decision_basis == "finite_count":
        cr = ("satisfies" if e.counts.D >= r.threshold else
              "violates" if e.counts.P < r.threshold else "overlaps")
    complete = e.observed_support == r.scope.members
    incompatibilities = []
    if r.scope != e.scope or e.basis.scope != e.scope:
        incompatibilities.append("Scope/basis mismatch (including units, estimand, grouping and information).")
    if not e.quality.usable:
        incompatibilities.append("Admissibility/source/payload/numerical integrity blocks scientific reliance.")
    if incompatibilities:
        return Decision(r, e, pr, ir, cr, "UNAVAILABLE", "UNAVAILABLE", "Diagnostic arithmetic only.",
                        complete, False, True, tuple(limits + incompatibilities))
    contract: Verdict = "UNAVAILABLE"
    resolution: Verdict = "UNRESOLVED"
    interpretation = "Point description only; missing uncertainty is not zero uncertainty."
    components_ok = bool(r.resolution_components) and set(r.resolution_components) <= set(e.basis.components)
    if e.kind == "unavailable":
        resolution = "UNAVAILABLE"
        interpretation = "Evidence unavailable or unsupported."
    elif r.decision_basis == "complete_support":
        if e.kind != "coverage":
            raise ValueError("complete_support contract requires coverage evidence")
        contract = resolution = "PASS" if complete else "FAIL"
        interpretation = "Declared support coverage only; no assertion about physical behavior."
    elif r.decision_basis == "finite_count":
        if e.counts is None or e.counts.meaning != r.count_meaning:
            raise ValueError("count contract requires matching explicit success interpretation")
        count = e.counts
        assert cr is not None
        if count.meaning != "applicable_bound" or components_ok:
            contract = _verdict(cr)
        interpretation = f"Finite-cohort count under {count.meaning}; no population reliability."
        if count.meaning == "applicable_bound" and components_ok:
            resolution = contract
        elif count.meaning == "applicable_bound":
            interpretation = "Count basis does not cover required uncertainty components; arithmetic only."
        elif count.meaning == "tested_sensitivities":
            interpretation += " Stability only under named tested sensitivities."
    else:
        if r.decision_basis == "point" and pr is not None and complete:
            contract = _verdict(pr)
        if e.kind == "bound" and components_ok:
            if complete or e.basis.full_support_justification:
                assert ir is not None
                resolution = _verdict(ir)
                interpretation = ("Allowance-conditional" if e.basis.kind == "allowance" else "Declared bound-resolved")
                interpretation += " comparison, only for listed components, scope and assumptions; basis not authenticated."
                if r.decision_basis == "applicable_bound":
                    contract = resolution
            else:
                interpretation = "Incomplete support without full-scope bound justification."
        elif e.kind == "sensitivity" and complete:
            interpretation = f"Tested-sensitivity relation: {ir}; no confidence coverage or continuum bound."
        elif e.kind == "bound":
            interpretation = "Bound does not cover required uncertainty components."
        if not complete:
            limits.append("Incomplete observed support; subset point metrics cannot decide the full requirement.")
    if e.kind in ("count", "bound") and not components_ok:
        limits.append("Required resolution components are not covered by the supplied basis.")
    if e.unknown_components:
        limits.append("Unrepresented uncertainty: " + ", ".join(e.unknown_components) + ".")
    if e.basis.kind == "allowance" and e.kind == "count":
        interpretation += " Allowance-conditional on the stated assumptions."
    return Decision(r, e, pr, ir, cr, contract, resolution, interpretation, complete,
                    complete and contract != "UNAVAILABLE" and resolution != "UNAVAILABLE",
                    False, tuple(limits))


def conjunction(values: tuple[Verdict, ...]) -> Verdict:
    """A sound failure witness survives missing components; empty is unavailable."""
    for value in values:
        _choice(value, ("PASS", "FAIL", "UNRESOLVED", "UNAVAILABLE"))
    if "FAIL" in values:
        return "FAIL"
    if values and all(value == "PASS" for value in values):
        return "PASS"
    return "UNAVAILABLE" if not values or "UNAVAILABLE" in values else "UNRESOLVED"


@dataclass(frozen=True)
class Assessment:
    policy_version: str
    decisions: tuple[Decision, ...]
    contractual: Verdict
    resolution: Verdict
    assessment_complete: bool
    support_complete: bool
    reliance_blocked: bool
    failed_controlling: tuple[str, ...]
    resolved_failure_witnesses: tuple[str, ...]

    def to_json(self) -> str:
        """Stable identities, exact decimal strings, no runtime/environment fields."""
        def decimal(value: object) -> dict[str, str]:
            if isinstance(value, Decimal):
                return {"decimal": str(value)}
            raise TypeError(f"unsupported serialization type: {type(value).__name__}")
        return json.dumps(asdict(self), default=decimal, sort_keys=True, indent=2, allow_nan=False) + "\n"


def assess(requirements: tuple[Requirement, ...], evidence: Mapping[str, Evidence], *,
           policy_version: str, request: str = "comparison") -> Assessment:
    """Evaluate every declared component. Statistical inference/equivalence unsupported."""
    if request != "comparison":
        raise ValueError("unsupported request: statistical inference, equivalence and adoption are not implemented")
    _text(policy_version)
    _names(tuple(r.identity for r in requirements))
    if not requirements or not any(r.controlling for r in requirements):
        raise ValueError("nonempty controlling component set required")
    if set(evidence) - {r.identity for r in requirements}:
        raise ValueError("evidence for undeclared component")
    decisions = tuple(evaluate(r, evidence.get(r.identity)) for r in sorted(requirements, key=lambda r: r.identity))
    controlling = tuple(d for d in decisions if d.requirement.controlling)
    return Assessment(policy_version, decisions,
                      conjunction(tuple(d.contractual for d in controlling)),
                      conjunction(tuple(d.resolution for d in controlling)),
                      all(d.assessment_complete for d in controlling),
                      all(d.support_complete for d in controlling),
                      any(d.reliance_blocked for d in controlling),
                      tuple(d.requirement.identity for d in controlling if d.contractual == "FAIL"),
                      tuple(d.requirement.identity for d in controlling if d.resolution == "FAIL"))

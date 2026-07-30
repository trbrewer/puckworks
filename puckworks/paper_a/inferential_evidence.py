"""Where a decision permission comes from, and what has to be true before one is granted.

Round-11 P1-2. :class:`~puckworks.paper_a.transfer_semantics.InferentialStatus` was doing two jobs
at once, and only one of them safely. As a DESCRIPTION of the present analysis it is correct and
conservative: every decision flag is false, coverage is uncalibrated, no margin is declared. As the
AUTHORITY that unlocks decision language it was self-attestation — ``status_from_dict`` checked
field types and enum membership, ``validate_inferential_status`` checked internal coherence, and
neither asked whether the named procedure exists, ran, achieved its coverage, used its margin
prospectively, or produced the decision claimed. The reviewer wrote this object by hand::

    analysis_kind:           calibrated_clustered_confidence
    coverage_calibrated:     true
    confidence_level:        0.95
    confidence_procedure:    "invented future procedure"
    supports_equivalence_decision: true
    practical_margin_pp:     0.5
    permitted_claim_class:   calibrated_decision

and it validated clean and unlocked "the model is equivalent to the comparator". A JSON *array* in
``confidence_procedure`` also passed, because the parser called ``str()`` on it and got
``"['fake', 'procedure']"``.

That is not a hypothetical about some future author. It is the same structural error as round-10
P1-2 (favourability declared twice, so the declaration and the fact could disagree) one level up:
the permission to make a claim was declared rather than derived. Hashing the artefacts would not
have helped on its own — the defect is that a BOOLEAN was trusted, so the fix has to make the
boolean an output.

The chain here is:

    registered procedure  +  evidence record  +  the artefacts it names
        → verify (every digest recomputed, every semantic re-checked)
        → DERIVE the decision from the observed result and the registered rule
        → VerifiedInferentialStatus, whose decision flags are computed properties

``claim_policy.granted()`` grants nothing to a bare declared status. A future calibrated analysis
unlocks language by producing evidence that survives :func:`verify_inferential_evidence`, not by
editing a flag — and it unlocks only the decision its registered rule actually produced, so
equivalence evidence cannot license superiority prose.

What this is NOT: protection against an adversary who can rewrite the code and the evidence
together. The digests bind an artefact to a claim WITHIN this workflow, which is the failure mode
that has actually occurred here five rounds running — a value or a flag drifting away from the thing
it describes while every checker stayed green.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from puckworks.paper_a import transfer_semantics as TS

SCHEMA_VERSION = 1

# ─────────────────────────────────────────────────────────────────────────────────────────────
# 1. Deterministic serialisation
# ─────────────────────────────────────────────────────────────────────────────────────────────


def canonical_bytes(payload) -> bytes:
    """UTF-8, sorted keys, no whitespace, no NaN/Infinity. The same object always hashes the same.

    ``allow_nan=False`` matters: Python's encoder emits the non-standard tokens ``NaN`` and
    ``Infinity`` by default, which are not JSON, do not round-trip through other readers, and would
    let a non-finite value into a record whose whole purpose is to be reproducible.
    """
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False,
                      separators=(",", ":")).encode("utf-8")


def digest(payload) -> str:
    """The SHA-256 of :func:`canonical_bytes`."""
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 2. Registered procedures
# ─────────────────────────────────────────────────────────────────────────────────────────────

#: The decision names, matching `InferentialStatus.decision_flags`.
SUPERIORITY = "superiority"
NONINFERIORITY = "non-inferiority"
EQUIVALENCE = "equivalence"
ABSENCE = "absence of skill"
DECISIONS = (SUPERIORITY, NONINFERIORITY, EQUIVALENCE, ABSENCE)

#: Decision rules, by id. Each takes the verified interval semantics, the estimand and the margin,
#: and returns True when the rule's condition is MET by the observed result.
#:
#: These are deliberately tiny and total. The point is not that they are sophisticated; it is that
#: the decision is COMPUTED from the result rather than read out of a field somebody typed.


def _rule_superiority(sem: TS.IntervalSemantics, estimand: TS.EstimandSpec, margin) -> bool:
    """The whole interval lies on the side of zero that favours the model."""
    if estimand.negative_favours_model:
        return sem.relation is TS.ZeroRelation.BELOW
    return sem.relation is TS.ZeroRelation.ABOVE


def _rule_equivalence(sem: TS.IntervalSemantics, estimand: TS.EstimandSpec, margin) -> bool:
    """The whole interval lies inside ±margin: neither arm can differ by a relevant amount."""
    if margin is None:
        return False
    return -float(margin) <= sem.lower and sem.upper <= float(margin)


def _rule_noninferiority(sem: TS.IntervalSemantics, estimand: TS.EstimandSpec, margin) -> bool:
    """The UNFAVOURABLE bound is no worse than the margin allows."""
    if margin is None:
        return False
    if estimand.negative_favours_model:
        return sem.upper <= float(margin)
    return sem.lower >= -float(margin)


DECISION_RULES = {
    "calibrated_interval_excludes_zero_on_favoured_side_v1": _rule_superiority,
    "calibrated_interval_within_margin_v1": _rule_equivalence,
    "calibrated_interval_unfavourable_bound_within_margin_v1": _rule_noninferiority,
}


@dataclass(frozen=True)
class ProcedureSpec:
    """One registered inferential procedure, and exactly which decisions it can produce.

    ``decision_rules`` is the load-bearing field: a procedure that can decide equivalence is not
    thereby able to decide superiority, and a generic "calibrated" flag must never unlock all four.

    ``predictors_refitted_within_draw`` is a REQUIREMENT of the procedure, not a free declaration.
    Round-11 P1-2 found the old validator rejecting ``True`` unconditionally — including for the enum
    value that exists to represent a future calibrated procedure, where refitting within the draw is
    exactly what makes the coverage honest — while a fabricated calibrated status with ``False``
    passed. Both halves of that were wrong; here the procedure says which it needs.
    """

    procedure_id: str
    procedure_version: str
    analysis_kind: TS.AnalysisKind
    requires_calibrated_coverage: bool
    predictors_refitted_within_draw: bool
    cluster_unit: str
    required_estimand_id: str
    decision_rules: dict          # decision name → rule id in DECISION_RULES
    decisions_requiring_margin: frozenset
    implementation_id: str

    def as_dict(self) -> dict:
        return {
            "procedure_id": self.procedure_id,
            "procedure_version": self.procedure_version,
            "analysis_kind": self.analysis_kind.value,
            "requires_calibrated_coverage": bool(self.requires_calibrated_coverage),
            "predictors_refitted_within_draw": bool(self.predictors_refitted_within_draw),
            "cluster_unit": self.cluster_unit,
            "required_estimand_id": self.required_estimand_id,
            "decision_rules": dict(sorted(self.decision_rules.items())),
            "decisions_requiring_margin": sorted(self.decisions_requiring_margin),
            "implementation_id": self.implementation_id,
            "schema_version": SCHEMA_VERSION,
        }

    @property
    def sha256(self) -> str:
        return digest(self.as_dict())

    def problems(self) -> list[str]:
        """Registration-time coherence. A procedure that does not specify its semantics fails."""
        out = []
        if not self.procedure_id or not self.procedure_version:
            out.append("a registered procedure needs a stable id AND a version; an id alone can "
                       "silently change meaning between releases")
        for decision, rule_id in sorted(self.decision_rules.items()):
            if decision not in DECISIONS:
                out.append("procedure %r declares an unknown decision %r"
                           % (self.procedure_id, decision))
            if rule_id not in DECISION_RULES:
                out.append("procedure %r maps decision %r to unregistered rule %r"
                           % (self.procedure_id, decision, rule_id))
        for decision in sorted(self.decisions_requiring_margin):
            if decision not in self.decision_rules:
                out.append("procedure %r requires a margin for %r but cannot decide it"
                           % (self.procedure_id, decision))
        if self.requires_calibrated_coverage and \
                self.analysis_kind is TS.AnalysisKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY:
            out.append("procedure %r claims calibrated coverage under a fixed-predictor "
                       "sensitivity analysis_kind, which has none" % self.procedure_id)
        if self.decision_rules and not self.requires_calibrated_coverage:
            out.append("procedure %r produces decisions without calibrated coverage"
                       % self.procedure_id)
        return out


#: The registry. It is EMPTY, and that is the honest state: Paper A runs a fixed-predictor clustered
#: percentile sensitivity analysis, which is not an inferential procedure and produces no decision.
#: There is nothing to register until one is designed, implemented and validated.
#:
#: It is a parameter of every function below rather than a global read directly, so a test can
#: register a synthetic procedure and exercise the positive path without touching the paper's state.
PROCEDURE_REGISTRY: dict = {}


def register(registry: dict, spec: ProcedureSpec) -> None:
    problems = spec.problems()
    if problems:
        raise ValueError("procedure %r cannot be registered: %s"
                         % (spec.procedure_id, "; ".join(problems)))
    key = (spec.procedure_id, spec.procedure_version)
    if key in registry:
        raise ValueError("procedure %r version %r is already registered; bump the version rather "
                         "than redefining one in place" % key)
    registry[key] = spec


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 3. The evidence record
# ─────────────────────────────────────────────────────────────────────────────────────────────

_REQUIRED_EVIDENCE_FIELDS = (
    "schema_version", "procedure_id", "procedure_version", "procedure_spec_sha256",
    "analysis_result_sha256", "source_manifest_sha256", "estimand_contract_sha256",
    "confidence_level", "predictors_refitted_within_draw", "practical_margin_pp",
    "practical_margin_protocol_reference", "practical_margin_protocol_sha256",
    "observed_interval_pp", "decision_rule_ids", "derived_decisions", "created_by",
)


@dataclass(frozen=True)
class EvidenceRecord:
    """What an analysis has to produce before any decision language is available to it.

    Every digest names something OUTSIDE this record — the procedure in the registry, the archived
    result, the source manifest, the estimand contract, the margin protocol. The record never hashes
    itself: a self-referential digest proves only that whoever last edited the file also re-ran the
    hasher, which is the exact non-guarantee round-9 found in the resampling design.
    """

    procedure_id: str
    procedure_version: str
    procedure_spec_sha256: str
    analysis_result_sha256: str
    source_manifest_sha256: str
    estimand_contract_sha256: str
    confidence_level: float
    predictors_refitted_within_draw: bool
    practical_margin_pp: float | None
    practical_margin_protocol_reference: str | None
    practical_margin_protocol_sha256: str | None
    observed_interval_pp: tuple
    decision_rule_ids: dict
    derived_decisions: dict
    created_by: str
    schema_version: int = SCHEMA_VERSION

    def as_dict(self) -> dict:
        return {
            "schema_version": int(self.schema_version),
            "procedure_id": self.procedure_id,
            "procedure_version": self.procedure_version,
            "procedure_spec_sha256": self.procedure_spec_sha256,
            "analysis_result_sha256": self.analysis_result_sha256,
            "source_manifest_sha256": self.source_manifest_sha256,
            "estimand_contract_sha256": self.estimand_contract_sha256,
            "confidence_level": self.confidence_level,
            "predictors_refitted_within_draw": bool(self.predictors_refitted_within_draw),
            "practical_margin_pp": self.practical_margin_pp,
            "practical_margin_protocol_reference": self.practical_margin_protocol_reference,
            "practical_margin_protocol_sha256": self.practical_margin_protocol_sha256,
            "observed_interval_pp": [self.observed_interval_pp[0], self.observed_interval_pp[1]],
            "decision_rule_ids": dict(sorted(self.decision_rule_ids.items())),
            "derived_decisions": {k: bool(v) for k, v in sorted(self.derived_decisions.items())},
            "created_by": self.created_by,
        }


def evidence_from_dict(obj) -> EvidenceRecord:
    """Rebuild an :class:`EvidenceRecord`, rejecting every loose type rather than coercing it.

    No ``str()`` anywhere. Round-11 P1-2's second reproduction was a JSON array in a string field
    that the old parser stringified into ``"['fake', 'procedure']"`` and then accepted.
    """
    if not isinstance(obj, dict):
        raise ValueError("inferential evidence must be a mapping, got %s" % type(obj).__name__)
    missing = [k for k in _REQUIRED_EVIDENCE_FIELDS if k not in obj]
    if missing:
        raise ValueError("inferential evidence is missing required field(s) %r" % (missing,))
    if obj["schema_version"] != SCHEMA_VERSION:
        raise ValueError("inferential evidence schema_version is %r, this code reads %r"
                         % (obj["schema_version"], SCHEMA_VERSION))

    for key in ("procedure_id", "procedure_version", "procedure_spec_sha256",
                "analysis_result_sha256", "source_manifest_sha256", "estimand_contract_sha256",
                "created_by"):
        _require_nonempty_str(obj[key], "evidence.%s" % key)
    for key in ("practical_margin_protocol_reference", "practical_margin_protocol_sha256"):
        if obj[key] is not None:
            _require_nonempty_str(obj[key], "evidence.%s" % key)
    if not isinstance(obj["predictors_refitted_within_draw"], bool):
        raise ValueError("evidence.predictors_refitted_within_draw must be a JSON boolean, got %r"
                         % (obj["predictors_refitted_within_draw"],))
    level = _require_number(obj["confidence_level"], "evidence.confidence_level")
    margin = (None if obj["practical_margin_pp"] is None
              else _require_number(obj["practical_margin_pp"], "evidence.practical_margin_pp"))

    interval = obj["observed_interval_pp"]
    if not isinstance(interval, (list, tuple)) or len(interval) != 2:
        raise ValueError("evidence.observed_interval_pp must be a two-element [lower, upper], got %r"
                         % (interval,))
    lower = _require_number(interval[0], "evidence.observed_interval_pp[0]")
    upper = _require_number(interval[1], "evidence.observed_interval_pp[1]")

    for key in ("decision_rule_ids", "derived_decisions"):
        if not isinstance(obj[key], dict):
            raise ValueError("evidence.%s must be a mapping, got %s" % (key, type(obj[key]).__name__))
    for name, rule_id in obj["decision_rule_ids"].items():
        _require_nonempty_str(rule_id, "evidence.decision_rule_ids[%r]" % name)
    for name, value in obj["derived_decisions"].items():
        if not isinstance(value, bool):
            raise ValueError("evidence.derived_decisions[%r] must be a JSON boolean, got %r"
                             % (name, value))

    return EvidenceRecord(
        procedure_id=obj["procedure_id"], procedure_version=obj["procedure_version"],
        procedure_spec_sha256=obj["procedure_spec_sha256"],
        analysis_result_sha256=obj["analysis_result_sha256"],
        source_manifest_sha256=obj["source_manifest_sha256"],
        estimand_contract_sha256=obj["estimand_contract_sha256"],
        confidence_level=level,
        predictors_refitted_within_draw=obj["predictors_refitted_within_draw"],
        practical_margin_pp=margin,
        practical_margin_protocol_reference=obj["practical_margin_protocol_reference"],
        practical_margin_protocol_sha256=obj["practical_margin_protocol_sha256"],
        observed_interval_pp=(lower, upper),
        decision_rule_ids=dict(obj["decision_rule_ids"]),
        derived_decisions=dict(obj["derived_decisions"]),
        created_by=obj["created_by"])


def _require_nonempty_str(value, what: str) -> str:
    """A string field is a STRING. Lists, mappings, numbers and booleans fail closed.

    This is the direct fix for the reproduced ``confidence_procedure: ["fake", "procedure"]``
    bypass: the old code's ``str(...)`` turned every object into a plausible-looking identifier.
    """
    if isinstance(value, bool) or not isinstance(value, str) or not value.strip():
        raise ValueError("%s must be a non-empty string, got %s %r"
                         % (what, type(value).__name__, value))
    return value


def _require_number(value, what: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("%s must be a JSON number, got %s %r" % (what, type(value).__name__, value))
    try:
        out = float(value)
    except (TypeError, ValueError, OverflowError):
        raise ValueError("%s must be a finite JSON number; conversion overflowed or failed (%r)"
                         % (what, value)) from None
    if out != out or out in (float("inf"), float("-inf")):
        raise ValueError("%s must be finite, got %r" % (what, value))
    return out


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 4. Verification, and the verified status
# ─────────────────────────────────────────────────────────────────────────────────────────────


#: A module-private construction token. Only :func:`verify_inferential_evidence` holds it.
#:
#: Round-11 P1-2 was that a decision permission could be TYPED rather than earned. A self-check
#: after the remediation merged found the same defect one type along: ``VerifiedInferentialStatus``
#: is the thing `claim_policy` trusts, it was an ordinary dataclass, and
#:
#:     VerifiedInferentialStatus(declared=…, evidence=…, procedure=…,
#:                               _decisions={"superiority": True, "equivalence": True, …})
#:
#: granted all four decisions without any verification running. That only one call site constructed
#: it properly was a CONVENTION — precisely the kind of guarantee the original finding rejected.
_VERIFIED = object()


@dataclass(frozen=True)
class VerifiedInferentialStatus:
    """A status whose decision flags are DERIVED, and the evidence they were derived from.

    ``claim_policy.granted()`` unlocks decision language from this type and from nothing else, so
    the type has to be unforgeable rather than merely conventionally constructed. Two things make it
    so:

    * it cannot be instantiated without the module-private token, which only
      :func:`verify_inferential_evidence` has; and
    * ``decision_flags`` **re-applies the registered rule** to the evidence's observed interval on
      every read, rather than returning a stored dict. There is no cached verdict to tamper with,
      and a mismatch between the stored derivation and a fresh one is itself an error.
    """

    declared: TS.InferentialStatus
    evidence: EvidenceRecord
    procedure: ProcedureSpec
    estimand: TS.EstimandSpec
    _token: object = None

    def __post_init__(self):
        if self._token is not _VERIFIED:
            raise TypeError(
                "VerifiedInferentialStatus cannot be constructed directly; it is the object "
                "`claim_policy` trusts, so it may only be produced by verify_inferential_evidence() "
                "from evidence that survived verification")

    # The InferentialStatus surface the claim policy consumes ────────────────────────────────
    @property
    def analysis_kind(self) -> TS.AnalysisKind:
        return self.procedure.analysis_kind

    @property
    def coverage_calibrated(self) -> bool:
        return bool(self.procedure.requires_calibrated_coverage)

    @property
    def practical_margin_pp(self):
        return self.evidence.practical_margin_pp

    @property
    def decision_flags(self) -> dict:
        """Recomputed from the evidence every time. Nothing here is stored."""
        sem = TS.interval_semantics(*self.evidence.observed_interval_pp)
        out = {name: False for name in DECISIONS}
        for decision, rule_id in self.evidence.decision_rule_ids.items():
            registered = self.procedure.decision_rules.get(decision)
            if registered is None or registered != rule_id:
                continue
            out[decision] = bool(DECISION_RULES[registered](
                sem, self.estimand, self.evidence.practical_margin_pp))
        return out

    @property
    def permitted_claim_class(self) -> TS.ClaimClass:
        return (TS.ClaimClass.CALIBRATED_DECISION if any(self.decision_flags.values())
                else TS.ClaimClass.DESCRIPTIVE_EVIDENCE_LIMITED)


def verify_inferential_evidence(declared: TS.InferentialStatus, evidence: EvidenceRecord,
                                estimand: TS.EstimandSpec, artefact_digests: dict,
                                registry: dict = None):
    """Return ``(verified_status_or_None, problems)``.

    ``artefact_digests`` maps ``analysis_result``/``source_manifest``/``estimand_contract``/
    ``practical_margin_protocol`` to the digest the CALLER computed from the actual artefact. The
    evidence record does not get to assert what those artefacts hash to.

    Nothing is trusted:

    * the procedure is looked up by ``(id, version)`` and its spec is re-hashed;
    * every referenced artefact digest is compared against the caller's;
    * the declared semantics (kind, coverage, level, refit policy, estimand) must equal the
      procedure's requirements;
    * a margin must exist, be positive, and be bound to a protocol that is NOT the result — a number
      typed in beside the answer is not a predeclaration; and
    * every decision is RECOMPUTED from the observed interval and the registered rule, then compared
      with what the record and the declared status say.
    """
    registry = PROCEDURE_REGISTRY if registry is None else registry
    problems: list[str] = []

    spec = registry.get((evidence.procedure_id, evidence.procedure_version))
    if spec is None:
        return None, ["no procedure %r version %r is registered; free text cannot select a "
                      "procedure, and an unregistered one has no declared semantics to check "
                      "against" % (evidence.procedure_id, evidence.procedure_version)]
    if spec.sha256 != evidence.procedure_spec_sha256:
        problems.append("the evidence names procedure %r but carries spec digest %s, while the "
                        "registered spec hashes to %s; the procedure's meaning has changed under "
                        "the record" % (evidence.procedure_id,
                                        evidence.procedure_spec_sha256[:12], spec.sha256[:12]))

    for name, field_name in (("analysis_result", "analysis_result_sha256"),
                             ("source_manifest", "source_manifest_sha256"),
                             ("estimand_contract", "estimand_contract_sha256")):
        want = artefact_digests.get(name)
        got = getattr(evidence, field_name)
        if want is None:
            problems.append("no %s digest was supplied to verification, so the evidence's claim "
                            "about it cannot be checked; partial evidence fails closed" % name)
        elif want != got:
            problems.append("evidence.%s is %s but the actual %s hashes to %s"
                            % (field_name, got[:12], name, want[:12]))

    # ── declared semantics against the procedure's requirements ──────────────────────────────
    if declared.analysis_kind is not spec.analysis_kind:
        problems.append("the declared analysis_kind is %r but procedure %r is a %r procedure"
                        % (declared.analysis_kind.value, spec.procedure_id,
                           spec.analysis_kind.value))
    if bool(declared.coverage_calibrated) != bool(spec.requires_calibrated_coverage):
        problems.append("the declared coverage_calibrated=%r contradicts procedure %r"
                        % (declared.coverage_calibrated, spec.procedure_id))
    if bool(declared.predictors_refitted_within_draw) != bool(spec.predictors_refitted_within_draw) \
            or bool(evidence.predictors_refitted_within_draw) != \
            bool(spec.predictors_refitted_within_draw):
        problems.append("procedure %r requires predictors_refitted_within_draw=%r; the status "
                        "declares %r and the evidence records %r"
                        % (spec.procedure_id, spec.predictors_refitted_within_draw,
                           declared.predictors_refitted_within_draw,
                           evidence.predictors_refitted_within_draw))
    if declared.confidence_level is None or \
            float(declared.confidence_level) != float(evidence.confidence_level):
        problems.append("the declared confidence_level %r is not the evidence's %r"
                        % (declared.confidence_level, evidence.confidence_level))
    if not 0.0 < float(evidence.confidence_level) < 1.0:
        problems.append("evidence.confidence_level %r is not a coverage target in (0, 1)"
                        % (evidence.confidence_level,))
    if declared.confidence_procedure != spec.procedure_id:
        problems.append("the declared confidence_procedure %r is not the registered procedure id %r"
                        % (declared.confidence_procedure, spec.procedure_id))
    if estimand.id != spec.required_estimand_id:
        problems.append("procedure %r is registered for estimand %r, not %r; a decision rule's "
                        "sign convention is meaningless against a different contrast"
                        % (spec.procedure_id, spec.required_estimand_id, estimand.id))

    # ── the margin, and whether it was declared BEFORE the result ────────────────────────────
    margin = evidence.practical_margin_pp
    needs_margin = {d for d in evidence.decision_rule_ids if d in spec.decisions_requiring_margin}
    if needs_margin:
        if margin is None or float(margin) <= 0.0:
            problems.append("decisions %r require a predeclared practical margin in percentage "
                            "points; the evidence carries %r" % (sorted(needs_margin), margin))
        if not evidence.practical_margin_protocol_reference \
                or not evidence.practical_margin_protocol_sha256:
            problems.append("a practical margin must be bound to a protocol that predates the "
                            "result; a margin stored beside the answer is not a predeclaration")
        else:
            want = artefact_digests.get("practical_margin_protocol")
            if want is None:
                problems.append("no practical_margin_protocol digest was supplied, so the margin's "
                                "provenance cannot be checked")
            elif want != evidence.practical_margin_protocol_sha256:
                problems.append("evidence.practical_margin_protocol_sha256 is %s but the protocol "
                                "hashes to %s" % (evidence.practical_margin_protocol_sha256[:12],
                                                  want[:12]))
    elif margin is not None:
        problems.append("a practical margin (%r) is recorded but no decision uses it; an unused "
                        "margin invites a post hoc negligibility claim" % (margin,))
    if declared.practical_margin_pp != margin:
        problems.append("the declared practical_margin_pp %r is not the evidence's %r"
                        % (declared.practical_margin_pp, margin))

    # ── DERIVE each decision, rather than reading it ─────────────────────────────────────────
    try:
        sem = TS.interval_semantics(*evidence.observed_interval_pp)
    except (TypeError, ValueError) as exc:
        return None, problems + ["evidence.observed_interval_pp is not a usable interval: %s" % exc]

    derived = {}
    for decision, rule_id in sorted(evidence.decision_rule_ids.items()):
        registered = spec.decision_rules.get(decision)
        if registered is None:
            problems.append("procedure %r cannot decide %r; evidence for one decision class does "
                            "not unlock another" % (spec.procedure_id, decision))
            continue
        if registered != rule_id:
            problems.append("the evidence applies rule %r to %r but procedure %r registers %r"
                            % (rule_id, decision, spec.procedure_id, registered))
            continue
        derived[decision] = bool(DECISION_RULES[registered](sem, estimand, margin))

    for decision in sorted(set(derived) | set(evidence.derived_decisions)):
        recomputed, recorded = derived.get(decision), evidence.derived_decisions.get(decision)
        if recomputed is None or recorded is None or recomputed != recorded:
            problems.append("decision %r: the record says %r, applying the registered rule to the "
                            "observed interval gives %r" % (decision, recorded, recomputed))

    for decision, granted in declared.decision_flags.items():
        if bool(granted) != bool(derived.get(decision, False)):
            problems.append("the declared status %s a %s decision, which the evidence does %s "
                            "produce" % ("grants" if granted else "withholds", decision,
                                         "not" if granted else ""))

    if problems:
        return None, problems
    verified = VerifiedInferentialStatus(declared=declared, evidence=evidence, procedure=spec,
                                         estimand=estimand, _token=_VERIFIED)
    # The status re-derives its flags on every read. Confirm once, here, that a fresh derivation
    # agrees with the one this function just computed — if the two ever disagreed it would mean the
    # rule is not a pure function of (interval, estimand, margin), and every downstream permission
    # would depend on when it was asked.
    if verified.decision_flags != {name: bool(derived.get(name, False)) for name in DECISIONS}:
        return None, ["the derived decisions are not reproducible from the verified status; a "
                      "decision rule must be a pure function of the observed interval, the estimand "
                      "and the margin"]
    return verified, []

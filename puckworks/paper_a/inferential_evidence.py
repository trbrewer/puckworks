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

Round-12 P1-4 and P1-5 rebuilt two parts of that.

**The permission boundary.** Round 11 made ``VerifiedInferentialStatus`` the object
``claim_policy`` trusts and called it unforgeable because construction required a module-private
sentinel. ``_VERIFIED`` is an ordinary module attribute, and one import later the public dataclass
constructor takes it — so the trusted thing had moved from a stored flag to possession of a Python
object, not disappeared. ``granted()`` now takes an evidence IDENTIFIER and re-verifies it from
canonical production storage at the point of use. Passing a pre-verified object grants nothing.

**The evidence itself.** The verifier compared ``analysis_result_sha256`` as an opaque digest and
then took the decisive interval from a separate field in the evidence record, so a hashed result
containing ``[-2.0, 2.0]`` could sit behind a decision derived from ``(-0.30, 0.20)``. And a margin
protocol was proven only to be a *different* artefact, never to have existed first. The interval is
now parsed out of the hashed result, and predeclaration requires a checkable ordering proof.

The word "unforgeable" is retired. In-process Python is not a security boundary against code that
can import the module, and claiming otherwise would be the same "describes more than it does" error
this file exists to fix. What the chain provides is that a permission cannot be obtained without a
matching, self-consistent record in production storage — which is the failure mode that has actually
occurred here, six rounds running: a value or a flag drifting away from the thing it describes while
every checker stayed green.
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
        """Registration-time coherence. A procedure that does not specify its semantics fails.

        Round-12 P1-5: a synthetic procedure with `cluster_unit=""` and `implementation_id=""`
        registered without complaint. A field that is declared but empty is not a declaration; it is
        the absence of one wearing a schema.
        """
        out = []
        for field in ("procedure_id", "procedure_version", "cluster_unit", "required_estimand_id",
                      "implementation_id"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                out.append("procedure %r declares %s=%r; an empty or whitespace-only semantic "
                           "field is the absence of a declaration, not a declaration"
                           % (self.procedure_id, field, value))
        if not self.decision_rules:
            out.append("procedure %r declares no decision rule, so it can produce no decision"
                       % self.procedure_id)
        for decision, rule_id in sorted(self.decision_rules.items()):
            if not isinstance(rule_id, str) or not rule_id.strip():
                out.append("procedure %r maps %r to an empty rule id" % (self.procedure_id, decision))
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


#: Fields the canonical analysis result must carry. The decision is derived from THESE, parsed out
#: of the bytes that were hashed — never from a value the evidence record wrote down beside them.
_REQUIRED_RESULT_FIELDS = (
    "schema_version", "procedure_id", "procedure_version", "estimand_id", "confidence_level",
    "predictors_refitted_within_draw", "observed_interval_pp",
)


def _result_problems(result, evidence: EvidenceRecord, spec: ProcedureSpec,
                     estimand: TS.EstimandSpec) -> tuple:
    """Parse the hashed result and check it means what the evidence says it means.

    Round-12 P1-5. The verifier compared ``analysis_result_sha256`` as an OPAQUE digest and then
    took the decisive interval from ``evidence.observed_interval_pp``, a separate caller-written
    field. The reviewer hashed a result whose interval was ``[-2.0, 2.0]`` — which does not support
    equivalence — while the evidence claimed ``(-0.30, 0.20)``, which does. Both digests matched and
    verification returned no problems.

    So the chain could truthfully say "this decision references this result hash" while deriving the
    decision from a different interval. Identity is not semantics.
    """
    if not isinstance(result, dict):
        return None, ["the analysis result artefact is %s, expected a mapping conforming to the "
                      "canonical result schema" % type(result).__name__]
    missing = [k for k in _REQUIRED_RESULT_FIELDS if k not in result]
    if missing:
        return None, ["the analysis result is missing required field(s) %r; a decision cannot be "
                      "derived from it" % (missing,)]

    problems = []
    if result["procedure_id"] != spec.procedure_id or \
            result["procedure_version"] != spec.procedure_version:
        problems.append("the result was produced by procedure %r/%r, but the evidence names %r/%r"
                        % (result["procedure_id"], result["procedure_version"],
                           spec.procedure_id, spec.procedure_version))
    if result["estimand_id"] != estimand.id:
        problems.append("the result is for estimand %r, not %r" % (result["estimand_id"],
                                                                   estimand.id))
    if bool(result["predictors_refitted_within_draw"]) != bool(spec.predictors_refitted_within_draw):
        problems.append("the result records predictors_refitted_within_draw=%r; procedure %r "
                        "requires %r" % (result["predictors_refitted_within_draw"],
                                         spec.procedure_id, spec.predictors_refitted_within_draw))
    interval = result["observed_interval_pp"]
    if not isinstance(interval, (list, tuple)) or len(interval) != 2:
        return None, problems + ["the result's observed_interval_pp is %r, expected [lower, upper]"
                                 % (interval,)]
    try:
        lower = _require_number(interval[0], "result.observed_interval_pp[0]")
        upper = _require_number(interval[1], "result.observed_interval_pp[1]")
        level = _require_number(result["confidence_level"], "result.confidence_level")
    except ValueError as exc:
        return None, problems + [str(exc)]

    # The transitional duplicate in the evidence record must EQUAL the parsed result, exactly.
    if (float(evidence.observed_interval_pp[0]), float(evidence.observed_interval_pp[1])) != \
            (lower, upper):
        problems.append(
            "the evidence record's observed_interval_pp is %r but the hashed analysis result "
            "contains %r; the decision must be derived from the result, and a record that "
            "disagrees with the artefact it cites is not evidence about it"
            % ((evidence.observed_interval_pp[0], evidence.observed_interval_pp[1]),
               (lower, upper)))
    if float(evidence.confidence_level) != level:
        problems.append("the evidence record's confidence_level is %r but the result records %r"
                        % (evidence.confidence_level, level))
    return (lower, upper), problems


def _chronology_problems(protocol, evidence: EvidenceRecord) -> list[str]:
    """Was the practical margin declared BEFORE the result existed?

    Round-12 P1-5 again: a different hash proves identity, not ordering. The reviewer supplied a
    protocol object explicitly marked ``created_after_result: True`` and it verified.

    The repository-native proof is commit ancestry — the protocol blob committed strictly before the
    commit that produced the result. That requires Git history the verifier may not have, so the
    contract is: an explicit, checkable ordering declaration must be present and must say the
    protocol predates the result. Absent or contradicted, verification FAILS. What is not acceptable
    is silence being read as "fine", which is what the previous version did.
    """
    if not isinstance(protocol, dict):
        return ["the practical-margin protocol artefact is %s, expected a mapping carrying its "
                "chronology proof" % type(protocol).__name__]
    problems = []
    if protocol.get("created_after_result"):
        problems.append("the practical-margin protocol declares created_after_result=True; a "
                        "margin chosen after seeing the result is not a predeclaration, whatever "
                        "its hash")
    ancestry = protocol.get("predates_result")
    if ancestry is not True:
        problems.append(
            "the practical-margin protocol carries no `predates_result: true` proof (protocol "
            "commit a strict ancestor of the result commit); a different hash proves identity, not "
            "chronology, and an unprovable predeclaration must fail closed")
    for field in ("protocol_commit", "result_commit"):
        value = protocol.get(field)
        if not isinstance(value, str) or not value.strip():
            problems.append("the practical-margin protocol does not name %s, so its ordering claim "
                            "cannot be audited" % field)
    if protocol.get("estimand_id") and evidence.decision_rule_ids and \
            protocol.get("units") not in (None, "percentage_points"):
        problems.append("the practical-margin protocol declares units %r; the margin must be in the "
                        "estimand's units" % (protocol.get("units"),))
    return problems


def verify_inferential_evidence(declared: TS.InferentialStatus, evidence: EvidenceRecord,
                                estimand: TS.EstimandSpec, artefact_digests: dict,
                                registry: dict = None, artefacts: dict = None):
    """Return ``(verified_status_or_None, problems)``.

    ``artefact_digests`` maps ``analysis_result``/``source_manifest``/``estimand_contract``/
    ``practical_margin_protocol`` to the digest the CALLER computed from the actual artefact, and
    ``artefacts`` supplies the parsed CONTENT of the result and the margin protocol. Both are
    required: a digest proves which bytes, and the content is what the decision is derived from.

    Nothing is trusted:

    * the procedure is looked up by ``(id, version)`` and its spec is re-hashed;
    * every referenced artefact digest is compared against the caller's;
    * the declared semantics (kind, coverage, level, refit policy, estimand) must equal the
      procedure's requirements;
    * the observed interval is PARSED OUT OF THE HASHED RESULT, and the evidence record's copy must
      equal it exactly (round-12 P1-5);
    * the practical margin must be bound to a protocol carrying a checkable proof that it predates
      the result (round-12 P1-5); and
    * every decision is RECOMPUTED from the parsed interval and the registered rule, then compared
      with what the record and the declared status say.

    **This function is not the production permission boundary.** ``claim_policy.granted()`` does not
    accept its output, because a caller chooses the registry and the artefacts passed here. See
    :func:`verify_registered_production_evidence`.
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
        # …and the protocol's CONTENT has to prove it predates the result.
        protocol = (artefacts or {}).get("practical_margin_protocol")
        if protocol is None:
            problems.append("no practical_margin_protocol content was supplied, so predeclaration "
                            "cannot be proven; a margin whose chronology is unprovable fails closed")
        else:
            problems += _chronology_problems(protocol, evidence)
    elif margin is not None:
        problems.append("a practical margin (%r) is recorded but no decision uses it; an unused "
                        "margin invites a post hoc negligibility claim" % (margin,))
    if declared.practical_margin_pp != margin:
        problems.append("the declared practical_margin_pp %r is not the evidence's %r"
                        % (declared.practical_margin_pp, margin))

    # ── DERIVE each decision from the PARSED RESULT, rather than reading it ──────────────────
    result = (artefacts or {}).get("analysis_result")
    if result is None:
        return None, problems + [
            "no analysis_result content was supplied; the decisive interval must be parsed out of "
            "the bytes that were hashed, not taken from a field beside them"]
    bounds, result_problems = _result_problems(result, evidence, spec, estimand)
    problems += result_problems
    if bounds is None:
        return None, problems
    try:
        sem = TS.interval_semantics(*bounds)
    except (TypeError, ValueError) as exc:
        return None, problems + ["the result's observed interval is not usable: %s" % exc]

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


# ─────────────────────────────────────────────────────────────────────────────────────────────
# 5. The production permission boundary (round-12 P1-4)
# ─────────────────────────────────────────────────────────────────────────────────────────────
#
# Round-11 made `VerifiedInferentialStatus` the thing `claim_policy` trusts and called it
# unforgeable because construction needs `_VERIFIED`. Round-12 pointed out that `_VERIFIED` is an
# ordinary module attribute: `from puckworks.paper_a.inferential_evidence import _VERIFIED` and the
# public dataclass constructor takes it. The trusted boolean had moved again — from a stored flag,
# to possession of an importable sentinel plus caller-chosen evidence and registry objects.
#
# The correction is to stop treating a Python object as provenance at all. In-process Python cannot
# be a security boundary against code that can import the module, and pretending otherwise is the
# same "describes more than it does" error as everything else this file exists to fix. So:
#
#   * production permission takes an evidence IDENTIFIER, not an object;
#   * it is re-verified from CANONICAL PRODUCTION STORAGE at the point of use; and
#   * the registry is not a parameter any production caller can supply.
#
# The wording "unforgeable" is retired. What this provides is that a permission cannot be obtained
# without a matching record in production storage — which is the failure mode that has actually
# occurred here, not an adversary rewriting the package.


@dataclass(frozen=True)
class InferentialEvidenceReference:
    """A pointer to evidence in canonical production storage. Carries no decision of its own."""

    evidence_id: str


#: Canonical production evidence, keyed by id. EMPTY, and that is the honest state: Paper A runs a
#: fixed-predictor clustered percentile sensitivity analysis, which is not an inferential procedure
#: and produces no decision. A future analysis registers here, and nowhere else.
PRODUCTION_EVIDENCE: dict = {}


class EvidenceNotRegistered(LookupError):
    """No canonical production evidence exists for this reference."""


def verify_registered_production_evidence(evidence_id: str):
    """Re-verify production evidence from canonical storage. Returns a verified status.

    Loads the evidence record, the result, the protocol, the estimand and the procedure from
    production locations — never from anything the caller is holding. Raises when the reference is
    unknown, which is what an empty production registry means for every reference.
    """
    entry = PRODUCTION_EVIDENCE.get(evidence_id)
    if entry is None:
        raise EvidenceNotRegistered(
            "no canonical production evidence is registered under %r; a decision permission is "
            "re-earned from production storage at the point of use, so an unregistered reference "
            "grants nothing" % (evidence_id,))
    status, problems = verify_inferential_evidence(
        entry["declared"], entry["evidence"], entry["estimand"], entry["artefact_digests"],
        PROCEDURE_REGISTRY, artefacts=entry["artefacts"])
    if problems:
        raise EvidenceNotRegistered(
            "canonical production evidence %r does not verify: %s" % (evidence_id,
                                                                      "; ".join(problems)))
    return status


def verify_inferential_evidence_for_test(*args, **kwargs):
    """The explicit TEST SEAM.

    Synthetic procedures and caller-supplied registries are available only through this name, so a
    production caller cannot reach them by accident and a reader can see at the call site which one
    is in play. `claim_policy.granted()` does not accept what this returns.
    """
    return verify_inferential_evidence(*args, **kwargs)

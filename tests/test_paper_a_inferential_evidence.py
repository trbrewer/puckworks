"""Round-11 P1-2: a decision permission must be DERIVED from evidence, never declared.

The finding was not that the paper's current status is wrong — it is correct and conservative, every
flag false. It was that the mechanism which would unlock decision language for a future analysis
checked only that the declaration was internally coherent. The reviewer wrote this by hand::

    analysis_kind:                 calibrated_clustered_confidence
    coverage_calibrated:           true
    confidence_level:              0.95
    confidence_procedure:          "invented future procedure"
    supports_equivalence_decision: true
    practical_margin_pp:           0.5
    permitted_claim_class:         calibrated_decision

It validated clean and unlocked "the model is equivalent to the comparator". A JSON array in
`confidence_procedure` also passed, stringified into `"['fake', 'procedure']"`.

Both reproductions are pinned below, then every field of a genuine evidence record is mutated one at
a time, then the positive path is proved to still work — because a fix that merely bans the language
is one an author will delete rather than satisfy.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import claim_policy as CP  # noqa: E402
from puckworks.paper_a import inferential_evidence as IE  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402
from tests import helpers_inferential_evidence as H  # noqa: E402

STATUS = TS.TRANSFER_INFERENTIAL_STATUS


# ── 1. the two reproductions, verbatim ──────────────────────────────────────────────────────
def test_the_reproduced_fabricated_status_unlocks_nothing():
    fabricated = dataclasses.replace(
        STATUS, coverage_calibrated=True, confidence_level=0.95,
        confidence_procedure="invented future procedure",
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        supports_equivalence_decision=True, practical_margin_pp=0.5,
        permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION)
    assert CP.granted(fabricated) == set()
    assert CP.scan("The model is equivalent to the comparator.", fabricated)

    # And it cannot be verified either: no such procedure is registered, and free text must not
    # select one.
    status, problems = H.verify(declared=fabricated,
                                record=H.evidence(procedure_id="invented future procedure"))
    assert status is None
    assert any("no procedure" in p for p in problems), problems


@pytest.mark.parametrize("procedure", [
    ["fake", "procedure"], {"id": "fake"}, 7, 7.5, True, "", "   ",
])
def test_a_non_string_procedure_identifier_fails_closed(procedure):
    """`str(obj["confidence_procedure"])` turned every object into a plausible identifier."""
    obj = dict(STATUS.as_dict(), confidence_procedure=procedure)
    with pytest.raises(ValueError, match="confidence_procedure"):
        TS.status_from_dict(obj)


def test_a_valid_procedure_string_still_parses():
    obj = dict(STATUS.as_dict(), coverage_calibrated=False, confidence_procedure=None)
    assert TS.status_from_dict(obj).confidence_procedure is None


# ── 2. a declared status is not an authority ────────────────────────────────────────────────
def test_a_declared_status_grants_nothing_however_its_flags_read():
    for decision_field in ("supports_superiority_decision", "supports_noninferiority_decision",
                           "supports_equivalence_decision", "supports_absence_of_skill_decision"):
        declared = dataclasses.replace(
            STATUS, coverage_calibrated=True, confidence_level=0.99,
            confidence_procedure="anything", practical_margin_pp=1.0,
            analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
            permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION,
            **{decision_field: True})
        assert CP.granted(declared) == set(), decision_field


def test_a_duck_typed_stand_in_is_rejected_rather_than_trusted():
    class LooksLikeAStatus:
        coverage_calibrated = True
        practical_margin_pp = 0.5
        decision_flags = {"equivalence": True}

    with pytest.raises(TypeError, match="fabrication"):
        CP.granted(LooksLikeAStatus())


def test_the_paper_is_unaffected():
    """The current analysis asks for no unlock, so fail-closed changes nothing it says."""
    assert CP.granted(STATUS) == set()
    assert TS.validate_inferential_status(STATUS) == []
    assert STATUS.permitted_claim_class is TS.ClaimClass.DESCRIPTIVE_EVIDENCE_LIMITED
    assert IE.PROCEDURE_REGISTRY == {}, \
        "the paper registers no inferential procedure, because it performs none"


# ── 3. the positive path ────────────────────────────────────────────────────────────────────
def test_a_genuinely_verified_procedure_unlocks_exactly_its_own_decision():
    verified = H.synthetic_equivalence_status()
    assert CP.granted(verified) == {"equivalence", "calibrated coverage",
                                    "a predeclared practical margin"}
    assert CP.scan("The two arms are equivalent under the predeclared margin.", verified) == []
    # One decision class does not unlock the others.
    assert CP.scan("The model outperforms the comparator.", verified)
    assert CP.scan("The model adds no resolvable skill.", verified)
    assert CP.scan("The model is non-inferior to the comparator.", verified)


def test_the_decision_is_recomputed_not_copied():
    """Move the interval outside the margin and the SAME record stops deciding equivalence."""
    status, problems = H.verify(record=H.evidence(observed_interval_pp=(-0.90, 0.20)))
    assert status is None
    assert any("applying the registered rule" in p for p in problems), problems

    # …and a record that honestly reports the negative result verifies, granting nothing.
    honest = H.evidence(observed_interval_pp=(-0.90, 0.20), derived_decisions={IE.EQUIVALENCE: False})
    status, problems = H.verify(declared=H.replace_declared(
        supports_equivalence_decision=False,
        permitted_claim_class=TS.ClaimClass.DESCRIPTIVE_EVIDENCE_LIMITED), record=honest)
    assert problems == [], problems
    assert status.decision_flags[IE.EQUIVALENCE] is False
    assert CP.scan("The two arms are equivalent.", status)


# ── 4. one-field mutations of a genuine record ──────────────────────────────────────────────
@pytest.mark.parametrize("overrides,expect", [
    ({"procedure_version": "9.9.9"}, "no procedure"),
    ({"procedure_spec_sha256": "0" * 64}, "spec digest"),
    ({"analysis_result_sha256": "0" * 64}, "analysis_result_sha256"),
    ({"source_manifest_sha256": "0" * 64}, "source_manifest_sha256"),
    ({"estimand_contract_sha256": "0" * 64}, "estimand_contract_sha256"),
    ({"confidence_level": 0.90}, "confidence_level"),
    ({"predictors_refitted_within_draw": False}, "predictors_refitted_within_draw"),
    ({"practical_margin_pp": 2.0}, "practical_margin_pp"),
    ({"practical_margin_protocol_sha256": "0" * 64}, "protocol"),
    ({"practical_margin_protocol_reference": None,
      "practical_margin_protocol_sha256": None}, "predates the result"),
    ({"derived_decisions": {IE.EQUIVALENCE: False}}, "the record says"),
    ({"decision_rule_ids": {IE.EQUIVALENCE:
                            "calibrated_interval_excludes_zero_on_favoured_side_v1"}},
     "registers"),
    ({"decision_rule_ids": {IE.SUPERIORITY: "calibrated_interval_within_margin_v1"},
      "derived_decisions": {IE.SUPERIORITY: True}}, "cannot decide"),
])
def test_mutating_one_evidence_field_fails_verification(overrides, expect):
    status, problems = H.verify(record=H.evidence(**overrides))
    assert status is None, "FALSE GREEN: %r verified" % (overrides,)
    assert any(expect in p for p in problems), (overrides, problems)


@pytest.mark.parametrize("overrides,expect", [
    ({"confidence_level": 0.90}, "confidence_level"),
    ({"confidence_procedure": "something else"}, "confidence_procedure"),
    ({"practical_margin_pp": 2.0}, "practical_margin_pp"),
    ({"predictors_refitted_within_draw": False}, "predictors_refitted_within_draw"),
    ({"coverage_calibrated": False}, "coverage_calibrated"),
    ({"analysis_kind": TS.AnalysisKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY}, "analysis_kind"),
    ({"supports_superiority_decision": True}, "grants a superiority"),
    ({"supports_equivalence_decision": False}, "withholds a equivalence"),
])
def test_mutating_the_declared_status_fails_verification(overrides, expect):
    status, problems = H.verify(declared=H.replace_declared(**overrides))
    assert status is None, "FALSE GREEN: %r verified" % (overrides,)
    assert any(expect in p for p in problems), (overrides, problems)


@pytest.mark.parametrize("artefact", sorted(H.ARTEFACT_DIGESTS))
def test_an_artefact_that_does_not_hash_to_its_record_fails(artefact):
    digests = dict(H.ARTEFACT_DIGESTS, **{artefact: "0" * 64})
    status, problems = H.verify(digests=digests)
    assert status is None, artefact
    assert problems


@pytest.mark.parametrize("artefact", sorted(H.ARTEFACT_DIGESTS))
def test_a_missing_artefact_digest_fails_closed(artefact):
    """Partial evidence must not verify. An unsupplied digest is unchecked, not fine."""
    digests = {k: v for k, v in H.ARTEFACT_DIGESTS.items() if k != artefact}
    status, problems = H.verify(digests=digests)
    assert status is None, artefact
    assert any("cannot be checked" in p or "was supplied" in p for p in problems), problems


def test_the_estimand_must_be_the_one_the_procedure_is_registered_for():
    """A decision rule's sign convention is meaningless against a different contrast."""
    reversed_estimand = dataclasses.replace(TS.POOLED_MAPE_ESTIMAND, id="some_other_estimand")
    status, problems = IE.verify_inferential_evidence(
        H.declared_status(), H.evidence(), reversed_estimand, dict(H.ARTEFACT_DIGESTS),
        H.registry())
    assert status is None
    assert any("registered for estimand" in p for p in problems), problems


# ── 5. the record and procedure schemas themselves ──────────────────────────────────────────
@pytest.mark.parametrize("field,bad", [
    ("procedure_id", ["a", "b"]), ("procedure_id", 7), ("procedure_id", ""),
    ("created_by", None), ("analysis_result_sha256", {"x": 1}),
    ("confidence_level", "0.95"), ("confidence_level", True), ("confidence_level", float("nan")),
    ("confidence_level", 10 ** 400),
    ("practical_margin_pp", "0.5"), ("predictors_refitted_within_draw", "true"),
    ("observed_interval_pp", [1.0]), ("observed_interval_pp", "range"),
    ("observed_interval_pp", [float("inf"), 1.0]),
    ("decision_rule_ids", ["equivalence"]), ("derived_decisions", {"equivalence": "yes"}),
])
def test_a_malformed_evidence_field_is_rejected_not_coerced(field, bad):
    obj = H.evidence().as_dict()
    obj[field] = bad
    with pytest.raises(ValueError):
        IE.evidence_from_dict(obj)


def test_a_well_formed_record_round_trips_through_json():
    record = H.evidence()
    assert IE.evidence_from_dict(record.as_dict()) == record
    # Deterministic: the same object always produces the same bytes and therefore the same digest.
    assert IE.canonical_bytes(record.as_dict()) == IE.canonical_bytes(record.as_dict())
    assert IE.digest(record.as_dict()) == IE.digest(dict(reversed(list(
        record.as_dict().items()))))


def test_non_finite_numbers_cannot_be_serialised_into_a_digest():
    with pytest.raises(ValueError):
        IE.canonical_bytes({"x": float("nan")})


@pytest.mark.parametrize("overrides,expect", [
    ({"decision_rules": {"telepathy": "calibrated_interval_within_margin_v1"}}, "unknown decision"),
    ({"decision_rules": {IE.EQUIVALENCE: "no_such_rule"}}, "unregistered rule"),
    ({"decisions_requiring_margin": frozenset({IE.SUPERIORITY})}, "cannot decide"),
    ({"requires_calibrated_coverage": False}, "without calibrated coverage"),
    ({"procedure_version": ""}, "id AND a version"),
    ({"analysis_kind": TS.AnalysisKind.FIXED_PREDICTOR_CLUSTERED_SENSITIVITY}, "has none"),
])
def test_an_incoherent_procedure_cannot_be_registered(overrides, expect):
    spec = dataclasses.replace(H.procedure(), **overrides)
    with pytest.raises(ValueError, match="cannot be registered"):
        IE.register({}, spec)
    assert any(expect in p for p in spec.problems()), spec.problems()


def test_a_procedure_version_cannot_be_redefined_in_place():
    reg = H.registry()
    with pytest.raises(ValueError, match="already registered"):
        IE.register(reg, H.procedure())


# ── 6. the refit policy is the procedure's, not a universal ban ─────────────────────────────
def test_the_refit_rule_is_scoped_to_the_analysis_kind_it_is_about():
    """Round-11 P1-2's second inconsistency: `True` was rejected unconditionally, including for the
    enum value that exists to describe a future calibrated procedure, where refitting within the
    draw is what makes the coverage honest."""
    fixed = dataclasses.replace(STATUS, predictors_refitted_within_draw=True)
    assert any("fixed-predictor contract" in p for p in TS.validate_inferential_status(fixed))

    calibrated = H.declared_status()
    assert calibrated.predictors_refitted_within_draw is True
    assert TS.validate_inferential_status(calibrated) == []
    assert H.verify(declared=calibrated)[1] == []


def test_the_artefact_boundary_refuses_an_unevidenced_decision():
    """The schema has no place for an evidence record yet, so a decision flag in the artefact is
    necessarily an assertion nobody can check. It must not render prose."""
    import copy
    import json

    from tools import paper_a_transfer_text as TT

    ep = json.loads((REPO / "docs" / "paper1_resource"
                     / "PAPER_A_ENDPOINT_PROPAGATION.json").read_text(encoding="utf-8"))
    assert TT.validated_analysis(ep)[1] == STATUS, "the committed artefact must be unaffected"

    mutated = copy.deepcopy(ep)
    declared = mutated["resampling_design"]["inferential_status"]
    declared.update(coverage_calibrated=True, confidence_level=0.95,
                    confidence_procedure="invented future procedure",
                    analysis_kind="calibrated_clustered_confidence",
                    supports_equivalence_decision=True, practical_margin_pp=0.5,
                    permitted_claim_class="calibrated_decision")
    with pytest.raises(ValueError, match="no verifiable evidence record"):
        TT.validated_analysis(mutated)


# ── 7. self-check finding, AFTER the round-11 remediation merged ─────────────────────────────
def test_a_verified_status_cannot_be_constructed_directly():
    """P1-2 was that a decision permission could be TYPED rather than earned. Probing our own fix
    found the same defect one type along: `VerifiedInferentialStatus` is what `claim_policy` trusts,
    it was an ordinary dataclass, and hand-building one with a fabricated decision map granted all
    four decisions with no verification having run. That only one call site built it correctly was a
    CONVENTION — the exact kind of guarantee the original finding rejected."""
    verified = H.synthetic_equivalence_status()
    with pytest.raises(TypeError, match="cannot be constructed directly"):
        IE.VerifiedInferentialStatus(declared=verified.declared, evidence=verified.evidence,
                                     procedure=verified.procedure, estimand=verified.estimand)
    with pytest.raises(TypeError, match="cannot be constructed directly"):
        IE.VerifiedInferentialStatus(declared=STATUS, evidence=verified.evidence,
                                     procedure=verified.procedure,
                                     estimand=TS.POOLED_MAPE_ESTIMAND, _token="guess")


def test_decision_flags_are_recomputed_not_stored():
    """There is no cached verdict to tamper with: the flags re-apply the registered rule to the
    evidence's interval on every read."""
    verified = H.synthetic_equivalence_status()
    assert verified.decision_flags[IE.EQUIVALENCE] is True
    assert not any(f.name == "_decisions" for f in dataclasses.fields(verified)), \
        "a stored decision map is a forgeable field"
    # Same object, evidence swapped for one outside the margin -> the flag follows the evidence.
    outside = dataclasses.replace(verified.evidence, observed_interval_pp=(-0.9, 0.2))
    moved = dataclasses.replace(verified, evidence=outside)
    assert moved.decision_flags[IE.EQUIVALENCE] is False
    assert CP.granted(moved) == {"calibrated coverage", "a predeclared practical margin"}


def test_a_subclass_of_the_declared_status_cannot_smuggle_flags():
    class Sneaky(TS.InferentialStatus):
        @property
        def decision_flags(self):
            return {"equivalence": True, "superiority": True}

    sneaky = Sneaky(**{f.name: getattr(STATUS, f.name) for f in dataclasses.fields(STATUS)})
    assert CP.granted(sneaky) == set()
    assert CP.scan("The arms are equivalent.", sneaky)

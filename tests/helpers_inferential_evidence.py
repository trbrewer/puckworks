"""A synthetic registered procedure, so the POSITIVE evidence path is exercised without inventing
one for the paper.

Round-11 P1-2 asks for two things that pull against each other: proof that a fabricated status
cannot unlock decision language, and proof that a genuine one can — otherwise the fix is
indistinguishable from banning the language outright, and the next author's only route is to delete
the check.

Everything here is test-only and deliberately quarantined in `tests/`. The paper's own registry is
empty, which is the honest state: Paper A runs a fixed-predictor clustered percentile sensitivity
analysis, which is not an inferential procedure and produces no decision. Nothing in this module is
imported by `puckworks/` or `tools/`, and the fixture must never alter the paper's status or prose.
"""
from __future__ import annotations

import dataclasses
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import inferential_evidence as IE  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402

PROCEDURE_ID = "test_only_clustered_bootstrap_tost_v1"
PROCEDURE_VERSION = "1.0.0"

#: Digests of the artefacts the record names. In production these are computed from the real files;
#: here they stand for them, and the tests mutate them to prove the binding is load-bearing.
ARTEFACT_DIGESTS = {
    "analysis_result": IE.digest({"test": "analysis result"}),
    "source_manifest": IE.digest({"test": "source manifest"}),
    "estimand_contract": IE.digest(TS.POOLED_MAPE_ESTIMAND.as_dict()),
    "practical_margin_protocol": IE.digest({"test": "margin protocol", "margin_pp": 0.5}),
}


def procedure() -> IE.ProcedureSpec:
    """A calibrated procedure that can decide EQUIVALENCE and nothing else.

    The single-decision registration is the point: evidence for one decision class must not unlock
    another, so this procedure cannot produce a superiority verdict no matter what its result looks
    like.
    """
    return IE.ProcedureSpec(
        procedure_id=PROCEDURE_ID,
        procedure_version=PROCEDURE_VERSION,
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        requires_calibrated_coverage=True,
        # True, and legitimately: refitting the predictors inside each draw is what makes this
        # procedure's coverage honest. The round-11 review found `True` rejected unconditionally,
        # including for exactly this case.
        predictors_refitted_within_draw=True,
        cluster_unit="cond_in_variety",
        required_estimand_id=TS.POOLED_MAPE_ESTIMAND.id,
        decision_rules={IE.EQUIVALENCE: "calibrated_interval_within_margin_v1"},
        decisions_requiring_margin=frozenset({IE.EQUIVALENCE}),
        implementation_id="tests.helpers_inferential_evidence")


def registry() -> dict:
    reg: dict = {}
    IE.register(reg, procedure())
    return reg


def declared_status() -> TS.InferentialStatus:
    """What the author declares alongside the evidence. Every field is CHECKED against the
    procedure, so this is a statement to be verified, not a permission."""
    return TS.InferentialStatus(
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        coverage_calibrated=True,
        confidence_level=0.95,
        confidence_procedure=PROCEDURE_ID,
        predictors_refitted_within_draw=True,
        supports_superiority_decision=False,
        supports_noninferiority_decision=False,
        supports_equivalence_decision=True,
        supports_absence_of_skill_decision=False,
        practical_margin_pp=0.5,
        permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION)


def evidence(**overrides) -> IE.EvidenceRecord:
    """A record whose observed interval [-0.30, +0.20] lies inside the ±0.5 pp margin, so the
    registered equivalence rule is MET when it is recomputed."""
    spec = procedure()
    base = dict(
        procedure_id=PROCEDURE_ID,
        procedure_version=PROCEDURE_VERSION,
        procedure_spec_sha256=spec.sha256,
        analysis_result_sha256=ARTEFACT_DIGESTS["analysis_result"],
        source_manifest_sha256=ARTEFACT_DIGESTS["source_manifest"],
        estimand_contract_sha256=ARTEFACT_DIGESTS["estimand_contract"],
        confidence_level=0.95,
        predictors_refitted_within_draw=True,
        practical_margin_pp=0.5,
        practical_margin_protocol_reference="tests/margin-protocol.md",
        practical_margin_protocol_sha256=ARTEFACT_DIGESTS["practical_margin_protocol"],
        observed_interval_pp=(-0.30, 0.20),
        decision_rule_ids={IE.EQUIVALENCE: "calibrated_interval_within_margin_v1"},
        derived_decisions={IE.EQUIVALENCE: True},
        created_by="tests.helpers_inferential_evidence/1")
    base.update(overrides)
    return IE.EvidenceRecord(**base)


def verify(declared=None, record=None, digests=None):
    return IE.verify_inferential_evidence(
        declared if declared is not None else declared_status(),
        record if record is not None else evidence(),
        TS.POOLED_MAPE_ESTIMAND,
        dict(ARTEFACT_DIGESTS) if digests is None else digests,
        registry())


def synthetic_equivalence_status() -> IE.VerifiedInferentialStatus:
    status, problems = verify()
    assert problems == [], problems
    assert status.decision_flags == {IE.SUPERIORITY: False, IE.NONINFERIORITY: False,
                                     IE.EQUIVALENCE: True, IE.ABSENCE: False}
    return status


def replace_declared(**kw) -> TS.InferentialStatus:
    return dataclasses.replace(declared_status(), **kw)

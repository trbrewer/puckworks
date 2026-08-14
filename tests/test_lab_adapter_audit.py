"""Second-lens adapter-readiness audit tests (PV-19B Phase 4).

Offline + deterministic. Every extraction-runtime candidate (besides the existing Cameron lens) gets
exactly one finite readiness decision; no adapter is admitted without a tested conversion; grudeva2025
stays rights-blocked; and the audit never invents compatibility or overlays incomparable outputs.
"""
import json

import puckworks
from puckworks.product import lab_adapter_audit as aa


def test_every_extraction_candidate_has_one_finite_decision():
    report = aa.build_audit()
    candidates = {r["component_id"] for r in report["candidates"]}
    expected = {c.name for c in puckworks.components()
                if c.stage == "extraction" and c.execution_role == "runtime"
                and c.name != "cameron2020.extraction_bdf"}
    assert candidates == expected
    for r in report["candidates"]:
        assert r["decision"] in aa.DECISIONS


def test_no_candidate_is_ready_and_no_second_lens_is_invented():
    report = aa.build_audit()
    assert report["ready_for_bounded_adapter"] == []
    assert "No extraction candidate is ready" in report["conclusion"]


def test_grudeva_audit_decision_is_technical_not_a_rights_block():
    report = aa.build_audit()
    g = next(r for r in report["candidates"] if r["component_id"] == "grudeva2025.reduced")
    # rights now come from the centralized registry (no hard-coded "clear"/prose "rights" field)
    assert g["decision"] == "ADAPTER_REQUIRES_TESTED_CONVERSION"
    assert g["code_rights_state"] == "PERMISSION_DOCUMENTED" and g["public_execution_allowed"] is True
    assert "#73" in g["rights_note"] and "permission" in g["rights_note"].lower()
    # the reason must name the technical blocker, not a rights one
    assert "conversion" in g["reason"].lower() and "rights" not in g["decision"].lower()
    # and it is still NOT admissible as a second lens
    assert g["admissible_as_second_lens"] is False


def test_audit_is_deterministic():
    a = aa.canonical_json(aa.build_audit())
    b = aa.canonical_json(aa.build_audit())
    assert a == b


def test_boundaries_present_and_no_overclaim():
    report = aa.build_audit()
    joined = " ".join(report["boundaries"]).lower()
    assert "no universal grinder-dial conversion" in joined
    assert "agreement is not validation" in joined
    blob = json.dumps(report).lower()
    for bad in ("best recipe", "digital twin", "ensemble confidence"):
        assert bad not in blob


def test_evidence_is_carried_not_upgraded():
    reg = {c.name: c.evidence_strength for c in puckworks.components()}
    for r in aa.build_audit()["candidates"]:
        assert r["evidence_strength"] == reg[r["component_id"]]

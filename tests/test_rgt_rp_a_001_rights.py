"""RGT-RP-A-001 rights determinations and fail-closed RP-A profile gate."""
from __future__ import annotations

import json
from pathlib import Path

from puckworks import components
from puckworks import rights


ROOT = Path(__file__).parents[1]
REVIEW = ROOT / "docs/review/rgt_rp_a_001_rights"
TRIO = (
    "cameron2020.extraction_bdf",
    "wadsworth2026.permeability",
    "foster2025.infiltration",
)


def _determinations() -> dict[str, dict]:
    data = json.loads((REVIEW / "COMPONENT_DETERMINATIONS.json").read_text())
    return {row["component_id"]: row for row in data["records"]}


def _evidence_ids() -> set[str]:
    data = json.loads((REVIEW / "EVIDENCE_INVENTORY.json").read_text())
    return {row["evidence_id"] for row in data["records"]}


def test_exact_trio_registered_and_has_one_explicit_record_each():
    registered = {component.name for component in components()}
    assert set(TRIO) <= registered
    assert len(rights._RECORDS) == len(set(rights._RECORDS))
    for component_id in TRIO:
        assert component_id in rights._RECORDS
        assert rights.rights_record(component_id).component_id == component_id
    assert rights.validate_records() == []


def test_canonical_determinations_match_rights_registry_and_resolve_evidence():
    determinations = _determinations()
    evidence = _evidence_ids()
    assert set(determinations) == set(TRIO)
    for component_id, row in determinations.items():
        record = rights.rights_record(component_id)
        assert record.code_rights_state == row["code_state_recommended"]
        assert record.data_rights_state == row["data_state_recommended"]
        assert record.output_redistribution_state == row["output_state_recommended"]
        assert record.source and record.review_date == "2026-08-17"
        assert row["scientific_status_unchanged"] is True
        for field in ("code_evidence_ids", "data_evidence_ids", "output_evidence_ids"):
            assert row[field]
            assert set(row[field]) <= evidence


def test_reviewed_governing_fields_are_not_not_reviewed():
    for component_id in TRIO:
        record = rights.rights_record(component_id)
        assert "NOT_REVIEWED" not in (
            record.code_rights_state,
            record.data_rights_state,
            record.output_redistribution_state,
        )


def test_use_specific_decisions_remain_separate_and_fail_closed():
    cameron, wadsworth, foster = TRIO
    for component_id in TRIO:
        assert rights.may_execute_locally(component_id).allowed
        assert rights.may_execute_in_public_batch(component_id).allowed
        assert rights.may_include_code_in_release(component_id).allowed
    assert not rights.may_publish_outputs(cameron).allowed
    assert not rights.may_publish_outputs(foster).allowed
    assert not rights.may_publish_outputs(wadsworth).allowed
    assert rights.may_include_data_in_release(cameron).allowed
    assert rights.may_include_data_in_release(foster).allowed
    assert rights.may_include_data_in_release(wadsworth).allowed
    assert rights.may_publish_outputs(cameron).governing_field == "output_redistribution_state"


def test_wadsworth_affirmative_scope_and_notice_are_bounded():
    record = rights.rights_record("wadsworth2026.permeability")
    assert "Raw XCT" in record.rights_note
    assert "not relicensed" in record.rights_note
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text()
    assert "Wadsworth 2026 — Table 1 transcriptions" in notice
    assert "Creative Commons Attribution 4.0" in notice
    assert "does not\nrelicense them under Puckworks’ MIT licence" in notice


def test_cameron_and_foster_cross_path_blockers_are_explicit():
    cameron = rights.rights_record("cameron2020.extraction_bdf")
    foster = rights.rights_record("foster2025.infiltration")
    assert "SI Tables S1-S5" in cameron.rights_note
    assert "k_from_kappa()" in foster.rights_note
    assert "synthetic prescribed pressure" in foster.rights_note
    assert "global RightsRecord/output gate" in foster.rights_note


def test_public_review_artifacts_contain_no_private_contact_or_science_results():
    text = "\n".join(path.read_text() for path in REVIEW.glob("*") if path.is_file())
    assert "@" not in text
    assert "/home/" not in text
    assert "response curve values" not in text.lower()
    assert not any(REVIEW.glob("*RESULT*.json"))


def test_evidence_inventory_has_primary_support_for_each_affirmative_state():
    evidence = json.loads((REVIEW / "EVIDENCE_INVENTORY.json").read_text())["records"]
    by_id = {row["evidence_id"]: row for row in evidence}
    for row in _determinations().values():
        for state_field, ids_field in (
            ("code_state_recommended", "code_evidence_ids"),
            ("data_state_recommended", "data_evidence_ids"),
            ("output_state_recommended", "output_evidence_ids"),
        ):
            if row[state_field] in {"CLEAR", "PERMISSION_DOCUMENTED", "INDEPENDENT_REIMPLEMENTATION"}:
                assert any(by_id[evidence_id]["evidence_role"] == "controlling_primary"
                           for evidence_id in row[ids_field])


def test_draft_pr_remote_authority_never_authorizes_science_or_merge():
    remote = json.loads((REVIEW / "REMOTE_AUTHORITY.json").read_text())
    assert remote["draft_pr"]["number"] == 241
    assert remote["draft_pr"]["is_draft"] is True
    assert remote["scientific_execution_authorized"] is False
    assert remote["separate_issue_required_before_ready"] is True
    assert remote["separate_issue_required_before_merge"] is True


def test_rp_a_resume_gate_requires_all_three_and_fails_closed():
    gate = json.loads((REVIEW / "RP_A_001_RESUME_GATE.json").read_text())
    assert gate["decision"] == "RP_A_001_RESUME_NOT_AUTHORIZED"
    assert gate["all_three_required"] is True
    assert gate["automatic_substitution_allowed"] is False
    rows = {row["component_id"]: row for row in gate["component_verdicts"]}
    assert set(rows) == set(TRIO)
    assert rows["wadsworth2026.permeability"]["verdict"] == "NOT_AUTHORIZED_BY_CURRENT_POLICY"
    assert rows["cameron2020.extraction_bdf"]["verdict"] == "NOT_AUTHORIZED"
    assert rows["foster2025.infiltration"]["policy_representation_safe"] is False
    assert gate["scientific_execution_performed"] is False


def test_private_evidence_manifest_contains_no_path_or_contact_data():
    manifest = json.loads((REVIEW / "PRIVATE_EVIDENCE_MANIFEST.json").read_text())
    assert manifest["symbolic_bundle_name"] == "RGT_RP_A_001_PRIVATE_EVIDENCE_BUNDLE"
    assert manifest["file_count"] == len(manifest["evidence_files"])
    assert manifest["absolute_paths_in_public_manifest"] is False
    assert "/home/" not in json.dumps(manifest)

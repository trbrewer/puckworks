"""Producer-free public Explorer catalog (accessibility mission Phase 2, #43/#70).

Offline + deterministic. The Explorer exposes the full component registry in plain language WITHOUT
running any scientific producer, so a public page can browse the catalog with no execution. It reuses the
authoritative catalog + rights registry, keeps code/data/output rights separate, derives public-live
availability from use-specific rights (never NOT_REVIEWED, never code-clearance alone), and emits no
scientific-payload hash.
"""
import puckworks
from puckworks.product import lab_explorer as E


def test_explorer_invokes_zero_producers(monkeypatch):
    import puckworks.product as prod
    from puckworks.product import lab, lab_runners
    called = []
    monkeypatch.setattr(prod, "simulate_pull", lambda *a, **k: called.append("lens"))
    monkeypatch.setattr(lab_runners, "execute_runner", lambda cid: called.append(("native", cid)))
    monkeypatch.setattr(lab, "execute_scenario", lambda req: called.append("execute_scenario"))
    cat = E.explorer_catalog()
    assert called == []                                    # NO producer ran to build the catalog
    assert cat["producer_free"] is True


def test_explorer_enumerates_every_registered_component():
    cat = E.explorer_catalog()
    ids = [r["component_id"] for r in cat["components"]]
    assert set(ids) == {c.name for c in puckworks.components()}
    assert cat["n_components"] == len(ids) == len(set(ids))


def test_explorer_ordering_is_deterministic():
    ids = [r["component_id"] for r in E.explorer_catalog()["components"]]
    assert ids == sorted(ids)


def test_explorer_keeps_code_data_output_rights_separate():
    rows = {r["component_id"]: r for r in E.explorer_catalog()["components"]}
    for r in rows.values():
        assert {"code_rights_state", "data_rights_state", "output_redistribution_state"} <= set(r)
    # the LB component is affirmatively cleared; Cameron now has reviewed code but unresolved outputs
    lb = rows["brewer2026.lb_reference"]
    assert (lb["code_rights_state"], lb["data_rights_state"], lb["output_redistribution_state"]) == (
        "CLEAR", "NOT_APPLICABLE", "CLEAR")
    assert rows["cameron2020.extraction_bdf"]["code_rights_state"] == "INDEPENDENT_REIMPLEMENTATION"


def test_explorer_public_live_is_affirmative_rights_only():
    cat = E.explorer_catalog()
    rows = {r["component_id"]: r for r in cat["components"]}
    # public-live is the conjunction of affirmative public-execution AND output-publication clearance
    assert cat["public_live_component_ids"] == ["brewer2026.lb_reference", "grudeva2025.reduced"]
    assert rows["brewer2026.lb_reference"]["public_live_available"] is True
    g = rows["grudeva2025.reduced"]
    assert g["public_live_available"] is True and g["unavailable_reason"] == ""
    assert g["code_rights_state"] == g["output_redistribution_state"] == "PERMISSION_DOCUMENTED"
    # an affirmative rights state is NOT an execution path: no runner, no common-scenario adapter
    assert g["native_reference_ready"] is False and g["common_scenario_ready"] is False
    # NOT_REVIEWED is never public-live, with a plain reason
    assert rows["cameron2020.extraction_bdf"]["public_live_available"] is False
    assert rows["cameron2020.extraction_bdf"]["unavailable_reason"]
    assert E.public_live_component_ids() == ["brewer2026.lb_reference", "grudeva2025.reduced"]


def test_explorer_reports_a_rights_block_with_a_plain_reason():
    # the GENERIC rights-blocked branch (no component is blocked today) stays exercised
    import unittest.mock as mock

    from puckworks import rights
    cid = "cameron2020.extraction_bdf"
    rec = rights.RightsRecord(cid, "RIGHTS_BLOCKED", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED",
                              rights_note="synthetic block for this test", source="test",
                              decision_issue="#0", review_date="2026-08-14")
    with mock.patch.dict(rights._RECORDS, {cid: rec}):
        rows = {r["component_id"]: r for r in E.explorer_catalog()["components"]}
    assert rows[cid]["public_live_available"] is False
    assert "rights-blocked" in rows[cid]["unavailable_reason"]


def test_explorer_emits_no_scientific_payload_hash():
    cat = E.explorer_catalog()
    blob = str(cat)
    assert "scientific_payload_hash" not in blob and "scientific_payload_sha256" not in blob
    assert "report" in cat and cat["report"] == "puckworks-lab-explorer"


def test_explorer_row_carries_plain_language_and_readiness_fields():
    rows = {r["component_id"]: r for r in E.explorer_catalog()["components"]}
    r = rows["brewer2026.lb_reference"]
    assert r["plain_stage"] and r["plain_role"]             # plain-language phrasing present
    assert r["native_reference_ready"] is True and r["native_runner_id"]
    assert r["common_scenario_ready"] is False              # LB is not a common-scenario lens
    # Cameron is the common-scenario-ready lens
    assert rows["cameron2020.extraction_bdf"]["common_scenario_ready"] is True

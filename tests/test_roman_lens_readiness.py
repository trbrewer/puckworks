"""Roman-Corrochano second-lens readiness — DEFERRED pending affirmative rights review (Phase 6, #70).

Offline + deterministic. Roman-Corrochano is execution-ready on the shared scenario (inputs mappable
without invention; no grinder-dial mapping) and would be a SEPARATE-PANEL relative-trend lens
(NOT_COMPARABLE with Cameron EY/TDS). Its public use requires an affirmative rights review that was not
completed (code/output remain NOT_REVIEWED), so **no adapter is implemented** and its public path is
blocked. These tests pin that honest deferral: no fake adapter, no cross-model arithmetic, no absolute
EY/TDS presentation.
"""
from puckworks.product import lab
from puckworks.product import quantity_semantics as qs


def test_roman_is_execution_ready_but_not_comparable():
    r = qs.roman_corrochano_lens_readiness()
    assert r["execution_readiness"] == "READY_FOR_SHARED_SCENARIO"
    assert r["missing_inputs"] == []
    assert r["output_comparability_vs_cameron_ey"] == "NOT_COMPARABLE"
    assert "separate panel" in r["presentation"] and "relative trend" in r["presentation"]


def test_roman_public_use_is_not_cleared_and_adapter_is_deferred():
    r = qs.roman_corrochano_lens_readiness()
    assert r["code_rights_state"] == "NOT_REVIEWED"
    assert r["public_execution_cleared"] is False and r["output_publication_cleared"] is False
    assert r["adapter_status"] == "DEFERRED_PENDING_RIGHTS_REVIEW"
    assert r["no_adapter_implemented"] is True
    assert r["validation_campaign"] == "EXP-006"


def test_no_roman_adapter_is_registered():
    # the honest deferral: no Roman adapter exists in the Laboratory registry
    assert "romancorrochano2017.extraction" not in lab.ADAPTERS
    # selecting Roman as a lens surfaces it as not-executable, and runs NO producer for it
    ex = lab.execute_scenario(lab.ScenarioRequest(
        "pv19_named", lens_selection_policy="selected",
        requested_lens_ids=("romancorrochano2017.extraction",), reference_selection_policy="none"))
    le = {x["component_id"]: x for x in lab.build_comparison(ex)["lens_execution"]}
    row = le["romancorrochano2017.extraction"]
    assert row["status"] != "executed" and row["producer_invoked"] is False
    assert row["adapter_readiness"] == "NO_ADAPTER"


def test_roman_output_is_never_presented_as_absolute_ey_tds():
    # the readiness record forbids conversion to Cameron EY/TDS and any cross-model arithmetic
    r = qs.roman_corrochano_lens_readiness()
    text = (r["presentation"] + r["output_comparability_vs_cameron_ey"]).lower()
    assert "no difference/ratio/ranking" in r["presentation"]
    assert "not_comparable" in text

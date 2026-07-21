"""Narrative + rights tests for the Espresso Model Relay — structured, computed, no sensory certainty."""
import json

import pytest

from puckworks.product.linked_pull import RelayRequest, execute_illustrative_linked_pull


@pytest.fixture(scope="module")
def result():
    return execute_illustrative_linked_pull(RelayRequest(mode="fast"))


def _executed(result):
    ok = {"EXECUTED", "EXECUTED_WITH_ASSUMPTIONS", "ADAPTED_SCENARIO"}
    return [s for s in result["stages"] if s["status"] in ok and s["component_id"] != "recipe"]


def test_every_executed_station_has_a_full_narrative(result):
    for s in _executed(result):
        n = s["narrative"]
        assert n is not None
        for field in ("question", "what_enters", "what_it_calculates", "what_the_model_shows",
                      "what_is_handed_forward", "possible_cup_implication", "scope"):
            assert n[field], f"{s['component_id']} missing {field}"


def test_assumed_handoffs_are_named_in_the_narrative(result):
    grind = next(s for s in result["stages"] if s["component_id"] == "wadsworth2026.grindmap")
    joined = " ".join(grind["narrative"]["assumptions"])
    assert "A01" in joined


def test_no_prohibited_sensory_certainty_in_narratives(result):
    txt = " ".join(json.dumps(s["narrative"], default=str).lower() for s in result["stages"]
                   if s["narrative"])
    for bad in ("will taste", "tastes ", "best recipe", "grind finer", "guaranteed", "proves channeling",
                "sour", "sweet", "bitter", "balanced espresso", "quality score"):
        assert bad not in txt, bad


def test_relay_never_calls_itself_a_twin_or_validated_model(result):
    txt = json.dumps(result, default=str).lower()
    # the phrases may appear ONLY in negation (the permanent warning), never as an affirmative claim
    for affirmative in ("is a digital twin", "a validated coupled simulation of", "this validated model"):
        assert affirmative not in txt
    assert "not been validated" in txt or "not a validated" in txt      # the disclaimer is present


def test_lower_tds_described_as_less_concentrated_not_worse():
    # a very lean pull -> the dashboard uses concentration language, never "worse"/"bad"
    r = execute_illustrative_linked_pull(RelayRequest(target_beverage_g=56.0, mode="fast"))
    from puckworks.product import linked_pull_display as D
    blocks = " ".join(D.cup_dashboard_blocks(r)).lower()
    assert "concentration" in blocks
    assert "worse" not in blocks and "bad shot" not in blocks


def test_composition_clocks_not_translated_to_taste(result):
    ps = next(s for s in result["stages"] if s["component_id"] == "pannusch2024.solver")
    txt = json.dumps(ps["narrative"], default=str).lower()
    assert "clock" in txt or "release" in txt
    for bad in ("sour", "bitter", "sweet", "flavour score"):
        assert bad not in txt


def test_rights_preflight_precedes_producers_public_context_is_fail_closed():
    # in a public context, non-cleared components are blocked (the relay v1 is LOCAL_PRIVATE-first)
    from puckworks.product import linked_pull as LP

    class _Ctx:
        execution_context = "PUBLIC_ARTIFACT"
    allowed, _ = LP._rights_ok("cameron2020.extraction_bdf", _Ctx())
    blocked, _ = LP._rights_ok("grudeva2025.reduced", _Ctx())
    assert blocked is False                       # grudeva always blocked
    # cameron is NOT_REVIEWED for public batch, so public is fail-closed (blocked) — not silently run
    assert allowed is False


def test_local_private_allows_cameron_but_never_grudeva():
    from puckworks.product import linked_pull as LP

    class _Ctx:
        execution_context = "LOCAL_PRIVATE"
    assert LP._rights_ok("cameron2020.extraction_bdf", _Ctx())[0] is True
    assert LP._rights_ok("grudeva2025.reduced", _Ctx())[0] is False

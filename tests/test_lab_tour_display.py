"""Novice display organization for the Full Laboratory Tour (Phase 5, #43).

Offline. The fast tests drive a SYNTHETIC tour dict (no execution); one @slow test runs a real tour to
prove every registered component is shown in exactly one section. Cards lead with a plain badge/headline,
keep the component id in technical detail, and never overlay incompatible results.
"""
import pytest

from puckworks.product import lab_tour_display as D


def _synthetic_tour():
    def comp(cid, stage, kind, status, outputs=None, sci=None):
        return {"component_id": cid, "stage": stage, "execution_kind": kind, "execution_status": status,
                "input_origin": {"COMMON_SCENARIO": "ENTERED_RECIPE", "NATIVE_REFERENCE":
                                 "COMPONENT_NATIVE_CASE", "SCIENTIFIC_CHECK": "REGISTERED_FIXTURE"}.get(kind, "NONE"),
                "outputs": outputs or [], "message": f"ran {cid}", "fidelity_ceiling": "toy ceiling",
                "rights_decision": {}, "scientific_hash": sci, "comparable_component_ids": [cid]}
    return {
        "manifest_id": "full_laboratory_tour_v1", "execution_context": "LOCAL_PRIVATE",
        "scenario": {"preset_id": "pv19_named"}, "tour_scientific_hash": "abc123",
        "summary": {"registered": 5, "completed": 3, "rights_blocked": 1, "optional_unavailable": 1,
                    "by_kind": {"COMMON_SCENARIO": 1, "NATIVE_REFERENCE": 1, "SCIENTIFIC_CHECK": 1,
                                "OPTIONAL_DEPENDENCY": 1, "RIGHTS_BLOCKED": 1, "NO_EXECUTION_PATH": 0}},
        "components": [
            comp("cam.x", "extraction", "COMMON_SCENARIO", "EXECUTED",
                 [{"name": "ey", "value": 20.0, "unit": "%", "role": "simulated"}], "h1"),
            comp("perm.x", "packing", "NATIVE_REFERENCE", "EXECUTED", [], "h2"),
            comp("chk.x", "flow", "SCIENTIFIC_CHECK", "EXECUTED", [{"gate_id": "g", "status": "PASS"}], "h3"),
            comp("blk.x", "extraction", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED"),
            comp("opt.x", "flow", "OPTIONAL_DEPENDENCY", "OPTIONAL_UNAVAILABLE"),
        ],
    }


def test_section_order_and_membership():
    secs = dict((name, cards) for name, cards in D.tour_display_sections(_synthetic_tour()))
    names = [name for name, _ in D.tour_display_sections(_synthetic_tour())]
    assert names[0] == "Overview" and names[-1] == "Technical provenance"
    assert "Your reference shot" in names and "Calibration and evidence checks" in names
    assert "Components not run" in names
    # the common lens is in Your reference shot; the native ref is in its stage; the check is in Calibration
    assert secs["Your reference shot"][0]["technical"]["component_id"] == "cam.x"
    assert secs["Packing and permeability"][0]["technical"]["component_id"] == "perm.x"
    assert secs["Calibration and evidence checks"][0]["technical"]["component_id"] == "chk.x"
    assert {c["technical"]["component_id"] for c in secs["Components not run"]} == {"blk.x", "opt.x"}


def test_empty_stage_sections_are_omitted():
    names = [name for name, _ in D.tour_display_sections(_synthetic_tour())]
    # no native reference in grind/machine/etc -> those sections are not shown
    assert "Grind and particle representation" not in names
    assert "Machine and boundary conditions" not in names


def test_cards_lead_with_a_badge_not_the_id():
    secs = dict(D.tour_display_sections(_synthetic_tour()))
    card = secs["Your reference shot"][0]
    assert card["badge"] == "USES YOUR SHOT" and card["headline"] and "cam.x" not in card["headline"]
    assert card["technical"]["component_id"] == "cam.x"          # id lives in technical detail
    # every executable card answers: what ran / inputs / comparable / does-not-establish
    for key in ("what_ran", "inputs", "comparable", "does_not_establish"):
        assert card[key]
    assert "never overlays" in card["comparable"]


def test_badges_reflect_status():
    t = _synthetic_tour()
    t["components"][2]["execution_status"] = "CHECK_FAILED"
    secs = dict(D.tour_display_sections(t))
    chk = secs["Calibration and evidence checks"][0]
    assert chk["badge"] == "SCIENTIFIC CHECK — FAILED"
    nr = {c["technical"]["component_id"]: c["badge"] for c in secs["Components not run"]}
    assert nr["blk.x"] == "RIGHTS BLOCKED" and nr["opt.x"] == "OPTIONAL DEPENDENCY UNAVAILABLE"


def test_provenance_section_is_not_a_scientific_claim():
    secs = dict(D.tour_display_sections(_synthetic_tour()))
    prov = secs["Technical provenance"][0]
    assert prov["manifest_id"] == "full_laboratory_tour_v1" and prov["tour_scientific_hash"] == "abc123"
    assert "technical" not in prov                              # it is not a component card


def test_synthetic_coverage_is_exactly_once():
    D.assert_every_component_shown_once(_synthetic_tour())      # no drop, no double-count


@pytest.mark.slow
def test_real_tour_shows_every_registered_component_once():
    from puckworks.product import lab, lab_tour
    t = lab_tour.execute_laboratory_tour(lab.ScenarioRequest("pv19_named"), execution_context="LOCAL_PRIVATE")
    D.assert_every_component_shown_once(t)                      # all 25, each once
    shown = [card["technical"]["component_id"]
             for _, cards in D.tour_display_sections(t) for card in cards if "technical" in card]
    assert len(shown) == 25 == len(set(shown))

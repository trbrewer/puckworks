"""Generated named-shot scorecard (Paper 3 review MC17).

The scorecard was the one asserted result in a provenance paper that the provenance machinery did
not cover: Table 6 was hand-maintained. These tests hold the two properties that made generating it
worthwhile -- statuses are DERIVED rather than authored, and a number with no producer is withdrawn
rather than printed.
"""
import pathlib

import pytest

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import named_shot_scorecard as S

_ROOT = pathlib.Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def card():
    return S.scorecard()


def test_the_manuscript_scorecard_is_generated_and_current():
    assert S.verify() == "", S.verify()


def test_the_hand_written_table_is_gone():
    text = (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")
    assert "Table 6. Draft named-shot scorecard" not in text
    assert "<!-- scorecard:begin -->" in text


def test_every_selected_component_exists_in_the_registry(card):
    ids = {c.name for c in R.components()}
    bad = [r["component"] for r in card["rows"] if r["component"] and r["component"] not in ids]
    assert not bad, f"scorecard selects components that are not registered: {bad}"


def test_status_is_derived_wherever_a_component_is_selected(card):
    """The MC17 fix. An authored status on a stage that has a component would be the old defect."""
    for row in card["rows"]:
        if row["component"]:
            assert row["status_is_derived"], row["label"]
            assert row["evidence"], f"{row['label']}: derived status with no evidence records"
        else:
            assert not row["status_is_derived"], row["label"]
            assert row["status"] in S.NON_COMPONENT_STATUS, (row["label"], row["status"])


def test_derived_statuses_match_the_components_scoped_evidence_vector(card):
    """Recompute independently: the status must be exactly the relations the vector carries."""
    from puckworks.paper3 import evidence_graph as EG
    for row in card["rows"]:
        if not row["component"]:
            continue
        vec = EG.component_evidence_vector(row["component"])
        want = " + ".join(dict.fromkeys(S.RELATION_STATUS[s.relation] for s in vec))
        assert row["status"] == want, (row["label"], row["status"], want)


def test_every_relation_has_a_scorecard_status():
    """A new registry relation must not silently render as nothing."""
    missing = set(R.EVIDENCE_STRENGTHS) - set(S.RELATION_STATUS)
    assert not missing, f"relations with no scorecard status: {missing}"


def test_numbers_are_executed_from_producers_not_transcribed(card):
    """Every number in the table comes from running a producer."""
    found = False
    for row in card["rows"]:
        for name, blk in row["numbers"].items():
            found = True
            assert blk["producer"] in S.NUMBER_PRODUCERS, (name, blk["producer"])
            assert blk["values"], name
    assert found, "no producer-backed numbers at all -- this guard would be vacuous"


def test_the_forchheimer_numbers_match_the_audit_producer(card):
    from puckworks.models.wadsworth2026 import inertial as I
    live = I.de1_fixtureA_audit()
    row = next(r for r in card["rows"] if r["label"] == "Flow law")
    vals = next(iter(row["numbers"].values()))["values"]
    assert vals["Fo_F_max_exp_closure"] == live["Fo_F_max_exp"]
    assert vals["Fo_F_max_zhou_closure"] == live["Fo_F_max_zhou"]
    assert vals["permeability_k_m2"] == live["k_m2"]


def test_the_unbacked_ramp_claim_is_withdrawn_not_printed(card):
    """Regenerating the scorecard exposed a number no producer emits. It must stay withdrawn."""
    assert card["unbacked_claims"], "the withdrawn-claim record has been lost"
    text = (_ROOT / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")
    assert "6.6% shift" not in text and "6.6 % shift" not in text
    assert "WITHDRAWN" in text


def test_the_chain_ends_in_a_measurement_not_a_prediction(card):
    """The paper's own commitment: the scorecard exposes gaps rather than filling them."""
    last = card["rows"][-1]
    assert last["status"] == "open"
    assert "measurement" in last["caveat"].lower() or "capstone" in last["caveat"].lower()
    assert card["n_open_stages"] >= 1


def test_the_dial_is_recorded_as_non_portable(card):
    """Ledger A9/G5: dial spaces are grinder-specific and must never be silently matched."""
    assert card["configuration"]["dial_is_portable"] is False
    named = card["rows"][0]
    assert "portable" in named["caveat"]

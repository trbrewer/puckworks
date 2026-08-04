"""Focused tests for the I-040 cheap screen (Insight Foundry Wave 1).

These guard the SCREEN, not the science: that the enumeration stays complete as the codebase
changes, that the manifest wording is copied byte-identical rather than paraphrased, and that
the decision rule cannot be satisfied by a table that quietly stops covering a consumer.

The screen's own value is that it fails loudly. A new consumer of
`waszkiewicz2025/traces_time_dependent` that the attribution table does not cover must turn the
decision into NEEDS_NEW_DATA, and `test_coverage_is_complete` is what makes that visible at CI
time rather than at read time.
"""
import csv
import json
import pathlib

import pytest

from puckworks.analysis import screen_i040_evidence_halves as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-040"


@pytest.fixture(scope="module")
def audit():
    return S.audit()


def test_manifest_wording_is_byte_identical():
    """The screen may quote the cell; it may never paraphrase it (Foundry standing rule)."""
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    row = rows[S.DATASET_ID]
    assert row["validation_strength"] == S.MANIFEST_VALIDATION_STRENGTH
    assert row["caveat"] == S.MANIFEST_CAVEAT


def test_strength_order_matches_roadmap():
    """ROADMAP §0 vocabulary, strongest first. A reordering here silently inverts every verdict."""
    assert S.STRENGTH_ORDER == ["independent", "post-fit reconstruction", "verification",
                               "qualitative"]


def test_halves_carry_the_manifest_wording():
    assert S.HALVES["A_equilibrium"]["manifest_wording"] in S.MANIFEST_VALIDATION_STRENGTH
    assert S.HALVES["B_post_fit_9bar"]["manifest_wording"] in S.MANIFEST_VALIDATION_STRENGTH
    # the third category is the screen's finding, and must NOT claim to be in the cell
    assert S.HALVES["C_time_base_only"]["in_manifest_cell"] is False


def test_every_consumer_row_is_well_formed():
    for c in S.CONSUMERS:
        assert c["evidence_half"] in S.HALVES, c["consumer"]
        assert c["columns_read"], c["consumer"]
        assert c["attribution_reasoning"], c["consumer"]
        if c["states_strength"] is not None:
            assert c["states_strength"] in S.STRENGTH_ORDER, c["consumer"]


def test_static_enumeration_finds_call_sites():
    sites = S.call_sites()
    assert len(sites) >= 20
    fns = {s["function"] for s in sites}
    assert "gate_waszkiewicz_dynamic_9bar" in fns
    assert "steady_state_curve" in fns


def test_static_reachability_over_approximates_never_misses(audit):
    """The static layer must be a SUPERSET of the dynamically confirmed consumers.

    That direction is the whole point: it may flag a non-consumer, but a miss would make the
    completeness check worthless.
    """
    e = audit["enumeration"]
    static = {g.rsplit(".", 1)[-1] for g in e["static_gates_reaching"]}
    assert set(e["real_gate_consumers"]) <= static


def test_coverage_is_complete(audit):
    """A consumer the attribution table does not cover must be visible, not silent."""
    e = audit["enumeration"]
    assert e["uncovered_call_site_functions"] == []
    assert e["uncovered_gates"] == []
    assert e["complete"] is True


def test_dynamic_trace_ran_every_statically_flagged_gate(audit):
    e = audit["enumeration"]
    assert set(e["dynamic_trace"]) == {g.rsplit(".", 1)[-1]
                                       for g in e["static_gates_reaching"]}
    assert all(v["error"] is None for v in e["dynamic_trace"].values())


def test_adversarial_scan_leaves_no_unresolved_candidate_promotion(audit):
    scan = audit["adversarial_docstring_scan"]
    assert scan["unresolved_candidate_promotions"] == []
    # the scan must actually have fired at least once, or it is not an adversarial check
    assert any(v["candidate_promotion"] for v in scan["per_gate"].values())


def test_decision_is_the_recorded_one(audit):
    assert audit["n_promotions"] == 0
    assert audit["decision"] == "RETIRE"


def test_bundle_is_present_and_agrees_with_a_fresh_run(audit):
    """The committed result must not drift from what the script produces."""
    for rel in ("README.md", "result.json", "decision.md", "figures/primary.png"):
        assert (BUNDLE / rel).exists(), rel
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == audit["decision"]
    assert committed["n_consumers"] == audit["n_consumers"]
    assert committed["n_promotions"] == audit["n_promotions"]
    assert (committed["manifest_validation_strength_verbatim"]
            == S.MANIFEST_VALIDATION_STRENGTH)


def test_bundle_carries_the_required_disposition():
    for rel in ("README.md", "decision.md"):
        text = (BUNDLE / rel).read_text(encoding="utf-8")
        for token in ("CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                      "NOT_A_MODEL_VALIDATION_UPGRADE"):
            assert token in text, (rel, token)
    result = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert result["disposition"] == ["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                                    "NOT_A_MODEL_VALIDATION_UPGRADE"]


def test_decision_records_a_claim_ceiling():
    """Mandatory per docs/insights/screens/README.md — the field that stops over-reading."""
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    assert "## Claim ceiling" in text
    assert "## Adversarial check" in text
    assert "## Strongest alternative explanation" in text


def test_retirement_is_recorded_with_a_reopen_condition():
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    assert "**I-040**" in text
    assert "screens/I-040/" in text

"""Engine tests for the Espresso Model Relay — the default reference pull, rights, determinism, honesty."""
import json

import pytest

from puckworks.product.linked_pull import RelayRequest, execute_illustrative_linked_pull


@pytest.fixture(scope="module")
def result():
    return execute_illustrative_linked_pull(RelayRequest(mode="fast"))


def _executed(result):
    ok = {"EXECUTED", "EXECUTED_WITH_ASSUMPTIONS", "ADAPTED_SCENARIO"}
    return [s for s in result["stages"] if s["status"] in ok and s["component_id"] != "recipe"]


def test_default_run_executes_more_than_ten_components(result):
    assert len(_executed(result)) >= 10


def test_default_run_is_not_just_cameron(result):
    ids = {s["component_id"] for s in _executed(result)}
    assert "cameron2020.extraction_bdf" in ids
    assert len(ids - {"cameron2020.extraction_bdf"}) >= 9      # many non-Cameron models run too


def test_spans_the_espresso_stages(result):
    stations = {s["station_id"] for s in _executed(result)}
    for needed in ("grind", "packing", "machine", "wetting", "flow", "extraction", "puck_change",
                   "heterogeneous", "multisolute"):
        assert needed in stations, needed


def test_at_least_six_cross_component_handoffs_serialized(result):
    handoffs = [link for link in result["links"]
                if link["source_component_id"] and link["kind"] in
                ("DIRECT_MODEL_OUTPUT", "DOCUMENTED_ADAPTER", "ILLUSTRATIVE_ASSUMPTION", "OPTIONAL_SLOW_PATH")]
    assert len(handoffs) >= 6


def test_key_handoffs_present(result):
    edges = {link["edge_id"] for link in result["links"]}
    # machine_to_pannusch is NOT here: the pannusch solver is not run, so no runtime link is fabricated
    for e in ("cameron_radius_to_grindmap", "permeability_to_infiltration", "machine_to_infiltration",
              "cameron_to_waszkiewicz", "cameron_to_streamtube"):
        assert e in edges, e
    assert "machine_to_pannusch" not in edges           # solver not executed -> no runtime hand-off


def test_non_cameron_extraction_branch_runs(result):
    ids = {s["component_id"] for s in _executed(result)}
    # the multi-solute branch executes via the CLOSURES (the solver is honestly not-selected)
    assert "pannusch2024.closures" in ids and "brewer2026.streamtube" in ids


def test_linked_bed_response_branch_runs(result):
    wz = next(s for s in result["stages"] if s["component_id"] == "waszkiewicz2025.poroelastic")
    assert wz["status"] == "EXECUTED_WITH_ASSUMPTIONS"
    assert any(link["edge_id"] == "cameron_to_waszkiewicz" for link in result["links"])


@pytest.mark.slow
def test_deterministic_across_two_runs():
    a = execute_illustrative_linked_pull(RelayRequest(mode="fast"))
    b = execute_illustrative_linked_pull(RelayRequest(mode="fast"))
    assert a["model_output_hash"] == b["model_output_hash"]
    assert a["artifact_hash"] == b["artifact_hash"]


def test_canonical_json_has_no_nan_or_infinity(result):
    txt = json.dumps(result, default=str)
    assert "NaN" not in txt and "Infinity" not in txt


def test_grudeva_receives_zero_calls(result):
    g = next(s for s in result["stages"] if s["component_id"] == "grudeva2025.reduced")
    assert g["status"] == "RIGHTS_BLOCKED"
    assert g["outputs"] == [] and g["inputs"] == []
    # and it is never a link endpoint
    for link in result["links"]:
        assert link["source_component_id"] != "grudeva2025.reduced"
        assert link["target_component_id"] != "grudeva2025.reduced"


def test_no_confidence_or_taste_score(result):
    # forbid ASSERTIVE sensory/score claims (negated safety phrases like "no confidence score" are fine)
    txt = json.dumps(result, default=str).lower()
    for bad in ("quality score", "will taste", "best recipe", "proves channeling", "taste_score",
                "flavour score", "cup quality score", "grind finer", "recommends"):
        assert bad not in txt
    # a confidence/quality SCORE is never produced as a field
    assert "confidence_score" not in txt and "quality_score" not in txt


def test_branch_failure_does_not_erase_other_branches(monkeypatch):
    # force the swelling branch to error; the rest of the relay must still complete
    from puckworks.models.mo2023_2 import swelling as sw
    monkeypatch.setattr(sw, "flow_decay", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    r = execute_illustrative_linked_pull(RelayRequest(mode="fast"))
    sm = next(s for s in r["stages"] if s["component_id"] == "mo2023_2.swelling")
    assert sm["status"] == "EXECUTION_ERROR"                 # reported as an error, not a fake result
    assert len(_executed(r)) >= 10                           # other branches survive


def test_dashboard_does_not_average_incompatible_branches(result):
    from puckworks.product import linked_pull_display as D
    blocks = " ".join(D.cup_dashboard_blocks(result))
    assert "never averaged" in blocks or "not one final number" in blocks
    # each family is labelled separately
    for label in ("Baseline cup", "Heterogeneity branch", "Chemistry clocks"):
        assert label in blocks


def test_cameron_baseline_is_canonical(result):
    cam = next(s for s in result["stages"] if s["component_id"] == "cameron2020.extraction_bdf")
    ey = next(o["value"] for o in cam["outputs"] if o["name"] == "extraction_yield")
    assert 13.0 < ey < 15.5             # pinned C_S0 canonical baseline (~14.1%), not the 17% pollution

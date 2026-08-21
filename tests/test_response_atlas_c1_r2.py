import copy
import hashlib

import pytest

from puckworks.analysis.response_atlas import runner
from puckworks.analysis.response_atlas.decision import (
    ADDITIONAL, APPARATUS, DYNAMIC, SPATIAL, derive_scientific_decision,
)
from puckworks.analysis.response_atlas.governance import (
    apparatus_gate_specs, build_coverage_edges,
    minimum_measurement_sets, validate_measurement_linkage,
)


def eligibility(pair="p", scenario="A", channel="flow", adapter="DIRECT_NATIVE",
                version="1.0.0", state="eligible", left="null", right="other"):
    intervention, basis = "MATCHED", "FLOW_M_S"
    requirement = f"REQ__Q_TEST__{pair}__{scenario}__{intervention}__{basis}"
    contract_hash = hashlib.sha256(f"{adapter}/{version}".encode()).hexdigest()
    return {
        "pair_id": pair, "left_explanation": left, "right_explanation": right,
        "scientific_question": "q", "scenario": scenario, "candidate_observable": channel,
        "common_intervention": intervention, "common_output_basis": basis,
        "comparability_level": 1, "pair_role": "SCIENTIFICALLY_COMPETING",
        "eligibility": state, "reason_code": "TEST", "adapter_id": adapter,
        "adapter_version": version, "uncertainty_available": True,
        "eligibility_id": f"ELIG__{requirement}__{channel}__{adapter}__{version}",
        "requirement_id": requirement, "intervention_id": intervention, "basis_id": basis,
        "support_status": "SUPPORTED", "adapter_contract_hash": "contract",
        "question_id": "Q_TEST", "observation_contract_id": "OBS_TEST",
        "observation_contract_hash": contract_hash,
    }


def measurement(e, identity=None, classification="ROBUSTLY_DISCRIMINATING"):
    option = f"MEASOPT__{e['candidate_observable']}__{e['observation_contract_hash']}"
    return {
        "measurement_record_id": identity or f"MV__{e['requirement_id']}",
        "requirement_id": e["requirement_id"], "eligibility_id": e["eligibility_id"],
        "pair_id": e["pair_id"], "left_explanation": e["left_explanation"],
        "right_explanation": e["right_explanation"], "scenario": e["scenario"],
        "channel": e["candidate_observable"], "measurement_option_id": option,
        "adapter_id": e["adapter_id"], "adapter_version": e["adapter_version"],
        "adapter_contract_hash": "contract", "comparability_level": 1,
        "intervention_id": e["intervention_id"], "basis_id": e["basis_id"],
        "classification": classification,
        "robustly_covers_pair": classification == "ROBUSTLY_DISCRIMINATING",
        "left_support_state": "SUPPORTED", "right_support_state": "SUPPORTED",
        "left_prediction_id": "left", "right_prediction_id": "right",
        "declared_measurement_uncertainty": 0.1,
        "measurement_uncertainty_provenance": "TEST",
        "expanded_left_interval": [0.0, 0.1], "expanded_right_interval": [0.9, 1.0],
        "interval_combination_method": "CONSERVATIVE_ADDITIVE_BOUNDED_HALF_WIDTHS_NO_DISTRIBUTION",
        "reason_code": "TEST", "evidence_label": "TEST", "claim_ceiling": "TEST",
        "evidence_references": [e["eligibility_id"]],
        "observation_contract_id": e["observation_contract_id"],
        "observation_contract_hash": e["observation_contract_hash"],
    }


def requirement(e):
    return {"requirement_id": e["requirement_id"], "pair_id": e["pair_id"],
            "left_explanation": e["left_explanation"], "right_explanation": e["right_explanation"],
            "scenario": e["scenario"], "control_mode": e["common_intervention"],
            "intervention_id": e["intervention_id"], "pressure_node": "NOT_APPLICABLE",
            "pressure_reference": "NOT_APPLICABLE", "basis_id": e["basis_id"],
            "time_basis": "NOT_APPLICABLE", "pair_role": e["pair_role"],
            "scientific_question": "q", "relevant_to_final_decision": True,
            "applicable_candidate_channels": [e["candidate_observable"]],
            "requirement_status": "relevant", "reason_code": "RELEVANT", "provenance": "TEST",
            "question_id": "Q_TEST", "observation_family": e["candidate_observable"],
            "observation_contract_id": e["observation_contract_id"], "spatial_basis": "LUMPED",
            "relevance_status": "RELEVANT"}


def apparatus(status="NOT_EVALUATED", complete=False):
    return {
        "evaluation_id": "APPARATUS_EVALUATION", "apparatus_explanation_ids": ["null"],
        "status": status, "applicable_gate_result_ids": ["gate"] if status != "NOT_EVALUATED" else [],
        "passing_gate_result_ids": ["gate"] if status == "SURVIVES_ALL_APPLICABLE_GATES" else [],
        "failing_gate_result_ids": ["gate"] if status == "RULED_OUT_BY_MATCHED_GATE" else [],
        "unresolved_gate_result_ids": [], "apparatus_gate_coverage_complete": complete,
        "matched_scenario_ids": ["A"] if status != "NOT_EVALUATED" else [],
        "reason_code": "TEST", "contract_version": "rp-a-001-apparatus-gates/v1",
    }


def decide(explanations, es, ms, app, complete=None):
    requirements = [requirement(e) for e in es]
    edges = [r.to_dict() for r in build_coverage_edges(ms, es)]
    minimum = minimum_measurement_sets(requirements, edges)
    if complete is False:
        minimum = {**minimum, "complete": False, "result": "NO_COMPLETE_MEASUREMENT_SET",
                   "all_equally_minimal_sets": [], "minimum_set_ids": [],
                   "uncovered_requirement_ids": [r["requirement_id"] for r in requirements]}
    return derive_scientific_decision(
        explanations=explanations, requirements=requirements, channel_eligibility=es,
        component_reports={}, comparison_records=es, measurement_records=ms,
        coverage_edges=edges, minimum_measurement_sets=minimum,
        apparatus_gate_specs=[r.to_dict() for r in apparatus_gate_specs()],
        apparatus_gate_results=[], apparatus_evaluation=app)


def test_scenarios_are_distinct_requirements_and_both_must_be_covered():
    a, b = eligibility(scenario="A"), eligibility(scenario="B")
    requirements = [requirement(a), requirement(b)]
    edges = [r.to_dict() for r in build_coverage_edges([measurement(a)], [a, b])]
    result = minimum_measurement_sets(requirements, edges)
    assert not result["complete"] and result["uncovered_requirement_ids"] == [b["requirement_id"]]
    edges = [r.to_dict() for r in build_coverage_edges([measurement(a), measurement(b)], [a, b])]
    assert minimum_measurement_sets(requirements, edges)["complete"]


def test_adapter_contracts_are_distinct_and_exact():
    a = eligibility(adapter="A", version="1")
    b = eligibility(adapter="B", version="1")
    assert a["eligibility_id"] != b["eligibility_id"]
    assert measurement(a)["measurement_option_id"] != measurement(b)["measurement_option_id"]
    bad = measurement(a)
    bad["adapter_version"] = "2"
    with pytest.raises(ValueError, match="exact channel eligibility"):
        validate_measurement_linkage(bad, a)


@pytest.mark.parametrize("field", ["left_explanation", "right_explanation", "scenario",
                                   "adapter_id", "adapter_version", "requirement_id",
                                   "intervention_id", "basis_id"])
def test_exact_measurement_eligibility_provenance(field):
    e = eligibility()
    m = measurement(e)
    m[field] = "WRONG"
    with pytest.raises(ValueError, match="exact channel eligibility"):
        validate_measurement_linkage(m, e)


def test_coverage_and_minimum_sets_semantically_recomputed():
    bundle = runner.build_bundle()
    for mutation in (
        lambda b: b["discrimination_requirements"].append(copy.deepcopy(b["discrimination_requirements"][0])),
        lambda b: b["minimum_measurement_sets"].update({"complete": True}),
        lambda b: b["minimum_measurement_sets"].update({"uncovered_requirement_ids": ["fake"]}),
        lambda b: b["coverage_edges"].append({"fake": "edge"}),
    ):
        changed = copy.deepcopy(bundle)
        mutation(changed)
        with pytest.raises(ValueError):
            runner.validate_bundle(changed)


def test_zero_universe_is_non_vacuous_and_real_runner_uses_it():
    bundle = runner.build_bundle()
    assert bundle["summary_counts"]["relevant_requirements"] == 0
    assert not bundle["minimum_measurement_sets"]["complete"]
    assert bundle["minimum_measurement_sets"]["result"] == "NO_COMPLETE_MEASUREMENT_SET"
    assert bundle["decision"]["selected_outcome"] == ADDITIONAL


def test_apparatus_survival_requires_complete_gate_contract():
    ex = [{"explanation_id": "null", "scientific_role": "FIXED_BED_MACHINE_AND_APPARATUS_NULL"},
          {"explanation_id": "other", "scientific_role": "OTHER"}]
    e = eligibility()
    m = measurement(e)
    assert decide(ex, [e], [m], apparatus("SURVIVES_ALL_APPLICABLE_GATES", False)).selected_outcome == ADDITIONAL
    result = decide(ex, [e], [m], apparatus("SURVIVES_ALL_APPLICABLE_GATES", True), complete=False)
    assert result.selected_outcome == APPARATUS and result.global_coverage_complete is False


def test_dynamic_requires_apparatus_ruleout_and_complete_global_coverage():
    ex = [{"explanation_id": "null", "scientific_role": "FIXED_BED_MACHINE_AND_APPARATUS_NULL"},
          {"explanation_id": "dynamic", "scientific_role": "DYNAMIC_BED_EXPLANATION"}]
    e = eligibility(channel="bed_height_or_deformation", right="dynamic")
    m = measurement(e)
    assert decide(ex, [e], [m], apparatus()).selected_outcome == ADDITIONAL
    assert decide(ex, [e], [m], apparatus("RULED_OUT_BY_MATCHED_GATE"), complete=False).selected_outcome == ADDITIONAL
    assert decide(ex, [e], [m], apparatus("RULED_OUT_BY_MATCHED_GATE")).selected_outcome == DYNAMIC


def test_spatial_requires_every_complete_set_to_be_spatial():
    ex = [{"explanation_id": "null", "scientific_role": "FIXED_BED_MACHINE_AND_APPARATUS_NULL"},
          {"explanation_id": "spatial", "scientific_role": "SPATIAL_LOCALIZATION_EXPLANATION"}]
    spatial = eligibility(channel="spatial_flow_variance", right="spatial")
    assert decide(ex, [spatial], [measurement(spatial)],
                  apparatus("RULED_OUT_BY_MATCHED_GATE")).selected_outcome == SPATIAL
    flow = eligibility(channel="flow", right="spatial")
    assert decide(ex, [spatial, flow], [measurement(spatial), measurement(flow)],
                  apparatus("RULED_OUT_BY_MATCHED_GATE")).selected_outcome == ADDITIONAL


def test_manual_decision_and_semantic_mutations_fail():
    bundle = runner.build_bundle()
    changed = copy.deepcopy(bundle)
    changed["decision"]["selected_outcome"] = DYNAMIC
    with pytest.raises(ValueError, match="inconsistent"):
        runner.validate_bundle(changed)
    changed = copy.deepcopy(bundle)
    changed["apparatus_evaluation"]["status"] = "RULED_OUT_BY_MATCHED_GATE"
    with pytest.raises(ValueError, match="apparatus"):
        runner.validate_bundle(changed)

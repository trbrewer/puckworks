import copy
import hashlib

import pytest

from puckworks.analysis.response_atlas import runner
from puckworks.analysis.response_atlas.decision import ADDITIONAL, DYNAMIC
from puckworks.analysis.response_atlas.governance import (
    DIRECT_CONTRACT_HASH, build_coverage_edges, build_requirements,
    canonical_apparatus_gate_specs, evaluate_apparatus, minimum_measurement_sets,
)
from puckworks.analysis.response_atlas.schema import ObservationContractRecord


def test_real_bundle_independent_questions_and_v5_contract():
    bundle = runner.build_bundle()
    assert bundle["schema_version"] == "puckworks.response-atlas-export/v5"
    assert "pair_eligibility" not in bundle
    assert len(bundle["scientific_questions"]) == 4
    assert bundle["summary_counts"]["relevant_questions"] == 0
    assert bundle["apparatus_evaluation"]["status"] == "NOT_EVALUATED"
    assert bundle["decision"]["selected_outcome"] == ADDITIONAL


def test_requirements_are_independent_of_eligibility_and_order():
    bundle = runner.build_bundle()
    questions = bundle["scientific_questions"]
    contracts = bundle["observation_contracts"]
    first = [r.to_dict() for r in build_requirements(questions, contracts)]
    second = [r.to_dict() for r in build_requirements(list(reversed(questions)), list(reversed(contracts)))]
    assert first == second
    with pytest.raises(ValueError, match="never eligibility"):
        build_requirements(bundle["channel_eligibility"], contracts)


def test_relevant_unsupported_requirement_remains_uncovered():
    bundle = runner.build_bundle()
    q = copy.deepcopy(bundle["scientific_questions"][0]); q["relevance_status"] = "RELEVANT"; q["exclusion_reason"] = "NOT_APPLICABLE"
    requirements = [r.to_dict() for r in build_requirements([q], [bundle["observation_contracts"][0]])]
    minimum = runner.minimum_measurement_sets(requirements, [])
    assert minimum["uncovered_requirement_ids"] == [requirements[0]["requirement_id"]]
    assert not minimum["complete"]


@pytest.mark.parametrize("field,value", [("pressure_node", "NOT_PROVIDED"),
    ("pressure_reference", "NOT_PROVIDED"), ("flow_basis", "NOT_PROVIDED")])
def test_incomplete_applicable_observation_contract_rejected(field, value):
    bundle = runner.build_bundle(); data = copy.deepcopy(bundle["observation_contracts"][2])
    data[field] = value; data["channel"] = "pressure" if field.startswith("pressure") else "flow"
    with pytest.raises(ValueError, match="incomplete"):
        ObservationContractRecord.from_dict(data)


def test_direct_native_contract_is_explicit_and_hashed():
    bundle = runner.build_bundle()
    assert all(c["adapter_id"] == "DIRECT_NATIVE" and c["adapter_version"] == "1.0.0" for c in bundle["observation_contracts"])
    assert all(c["adapter_contract_hash"] == DIRECT_CONTRACT_HASH for c in bundle["observation_contracts"])


def _apparatus_fixture(classification="NOT_DISCRIMINATING", missing=False):
    ex = [{"explanation_id":"null","scientific_role":"FIXED_BED_MACHINE_AND_APPARATUS_NULL"},
          {"explanation_id":"other","scientific_role":"OTHER"}]
    req = {"requirement_id":"REQ","left_explanation":"null","right_explanation":"other",
           "scenario":"MACHINE_REF","relevance_status":"RELEVANT","applicable_candidate_channels":["flow"],
           "observation_family":"flow","observation_contract_id":"OBS","pair_id":"PAIR"}
    m = {"requirement_id":"REQ","measurement_record_id":"MV","channel":"flow",
         "classification":"NOT_ADJUDICATED_MISSING_UNCERTAINTY" if missing else classification,
         "comparability_level":1,"left_prediction_id":"L","right_prediction_id":"R"}
    return ex, req, m


def test_real_apparatus_evaluator_pass_fail_unresolved_and_not_applicable():
    specs=[s.to_dict() for s in canonical_apparatus_gate_specs()]
    ex,req,m=_apparatus_fixture()
    with pytest.raises(ValueError,match="closed evidence"):
        evaluate_apparatus(ex,[req],[m],specs)


def test_apparatus_survival_reaches_decision_through_real_evaluator():
    specs=[s.to_dict() for s in canonical_apparatus_gate_specs()]; ex,req,m=_apparatus_fixture()
    with pytest.raises(ValueError,match="closed evidence"):
        evaluate_apparatus(ex,[req],[m],specs)


def _route_pipeline(channel, role, expected):
    ex=[{"explanation_id":"null","scientific_role":"FIXED_BED_MACHINE_AND_APPARATUS_NULL"},
        {"explanation_id":"route","scientific_role":role}]
    specs=[s.to_dict() for s in canonical_apparatus_gate_specs()]
    requirements=[]; eligibility=[]; measurements=[]
    for suffix,ch,family in (("GATE","flow","flow"),("ROUTE",channel,channel)):
        rid=f"REQ_{suffix}"; obs=f"OBS_{suffix}"; oh=hashlib.sha256(obs.encode()).hexdigest()
        requirements.append({"requirement_id":rid,"left_explanation":"null","right_explanation":"route","scenario":"MACHINE_REF","relevance_status":"RELEVANT","relevant_to_final_decision":True,"applicable_candidate_channels":[ch],"observation_family":family,"observation_contract_id":obs,"pair_id":f"PAIR_{suffix}"})
        eid=f"ELIG_{suffix}"; option=f"MEASOPT__{ch}__{oh}"
        eligibility.append({"eligibility_id":eid,"requirement_id":rid,"pair_id":f"PAIR_{suffix}","left_explanation":"null","right_explanation":"route","scenario":"MACHINE_REF","candidate_observable":ch,"adapter_id":"DIRECT_NATIVE","adapter_version":"1.0.0","adapter_contract_hash":DIRECT_CONTRACT_HASH,"comparability_level":1,"intervention_id":"MATCHED","basis_id":"BASIS","observation_contract_id":obs,"observation_contract_hash":oh,"eligibility":"eligible","uncertainty_available":True})
        measurements.append({"measurement_record_id":f"MV_{suffix}","eligibility_id":eid,"requirement_id":rid,"pair_id":f"PAIR_{suffix}","left_explanation":"null","right_explanation":"route","scenario":"MACHINE_REF","channel":ch,"measurement_option_id":option,"adapter_id":"DIRECT_NATIVE","adapter_version":"1.0.0","adapter_contract_hash":DIRECT_CONTRACT_HASH,"comparability_level":1,"intervention_id":"MATCHED","basis_id":"BASIS","observation_contract_id":obs,"observation_contract_hash":oh,"classification":"ROBUSTLY_DISCRIMINATING","left_prediction_id":"L","right_prediction_id":"R"})
    evidence,results,apparatus=evaluate_apparatus(ex,requirements,measurements,specs)
    assert apparatus.status=="RULED_OUT_BY_MATCHED_GATE" and evidence
    edges=[e.to_dict() for e in build_coverage_edges(measurements,eligibility)]
    minimum=minimum_measurement_sets(requirements,edges)
    decision=runner.derive_scientific_decision(explanations=ex,requirements=requirements,channel_eligibility=eligibility,component_reports={},comparison_records=eligibility,measurement_records=measurements,coverage_edges=edges,minimum_measurement_sets=minimum,apparatus_gate_specs=specs,apparatus_gate_results=[r.to_dict() for r in results],apparatus_evaluation=apparatus.to_dict())
    assert decision.selected_outcome==expected


def test_dynamic_and_spatial_outcomes_follow_real_apparatus_ruleout():
    with pytest.raises(ValueError,match="closed evidence"):
        _route_pipeline("bed_height_or_deformation","DYNAMIC_BED_EXPLANATION",DYNAMIC)


@pytest.mark.parametrize("path", ["scientific_questions", "observation_contracts", "channel_eligibility",
    "coverage_matrix", "minimum_measurement_sets", "apparatus_gate_specs", "apparatus_evaluation",
    "decision", "summary_counts"])
def test_semantic_mutations_are_rejected(path):
    bundle=runner.build_bundle(); changed=copy.deepcopy(bundle)
    if isinstance(changed[path], list): changed[path]=list(reversed(changed[path])) if len(changed[path])>1 else changed[path]+[{"bad":True}]
    else: changed[path][next(iter(changed[path]))]="MUTATED"
    with pytest.raises(ValueError): runner.validate_bundle(changed)


def test_contract_window_mutation_changes_hash_identity():
    bundle=runner.build_bundle(); contract=copy.deepcopy(bundle["observation_contracts"][0]); old=contract["contract_sha256"]
    contract["observation_window_end"]="OTHER"
    payload={k:v for k,v in contract.items() if k not in {"observation_contract_id","contract_sha256"}}
    assert hashlib.sha256(__import__("json").dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()!=old

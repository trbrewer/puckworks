import copy
import hashlib

import pytest

from puckworks.analysis.response_atlas import runner
from puckworks.analysis.response_atlas.decision import ADDITIONAL, APPARATUS
from puckworks.analysis.response_atlas.governance import (
    DIRECT_CONTRACT_HASH, build_requirements, canonical_apparatus_gate_specs,
    evaluate_apparatus,
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
    ev,res,app=evaluate_apparatus(ex,[req],[m],specs)
    assert any(r.status=="PASS" for r in res) and any(r.status=="NOT_APPLICABLE" for r in res)
    assert app.status=="SURVIVES_ALL_APPLICABLE_GATES" and ev
    ex,req,m=_apparatus_fixture("ROBUSTLY_DISCRIMINATING")
    _,res,app=evaluate_apparatus(ex,[req],[m],specs)
    assert any(r.status=="FAIL" for r in res) and app.status=="RULED_OUT_BY_MATCHED_GATE"
    ex,req,m=_apparatus_fixture(missing=True)
    _,res,app=evaluate_apparatus(ex,[req],[m],specs)
    assert any(r.status=="UNRESOLVED" for r in res) and app.status=="UNRESOLVED_MISSING_UNCERTAINTY"


def test_apparatus_survival_reaches_decision_through_real_evaluator():
    specs=[s.to_dict() for s in canonical_apparatus_gate_specs()]; ex,req,m=_apparatus_fixture()
    ev,res,app=evaluate_apparatus(ex,[req],[m],specs)
    minimum={"complete":False,"result":"NO_COMPLETE_MEASUREMENT_SET","zero_universe_status":"ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM_PRESENT","all_equally_minimal_sets":[],"minimum_set_ids":[],"uncovered_requirement_ids":["REQ"]}
    decision=runner.derive_scientific_decision(explanations=ex,requirements=[{**req,"relevant_to_final_decision":True}],channel_eligibility=[],component_reports={},comparison_records=[],measurement_records=[{**m,"measurement_option_id":"OPT","left_explanation":"null","right_explanation":"other","pair_id":"PAIR","scenario":"MACHINE_REF"}],coverage_edges=[],minimum_measurement_sets=minimum,apparatus_gate_specs=specs,apparatus_gate_results=[r.to_dict() for r in res],apparatus_evaluation=app.to_dict())
    assert decision.selected_outcome==APPARATUS and ev


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

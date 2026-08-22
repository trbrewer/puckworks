"""C1-R4 evidence-closure regressions for REVIEW-C1R3-001."""
import copy, hashlib, json
import pytest
from puckworks.analysis.response_atlas import governance, runner
from puckworks.analysis.response_atlas.decision import DYNAMIC, SPATIAL, derive_scientific_decision
from puckworks.analysis.response_atlas.governance import (canonical_apparatus_gate_specs,
 evaluate_apparatus, minimum_measurement_sets, build_coverage_edges)
from puckworks.analysis.response_atlas.independent_verifier import reconstruct_apparatus
from puckworks.analysis.response_atlas.measurement_value import build_measurement_record
from puckworks.analysis.response_atlas.schema import (ComparisonEligibilityRecord,
 ObservationContractRecord, PredictionIntervalRecord)

def _hash(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def closed_fixture(classification="pass",channel="flow",role="OTHER",missing=False):
 ex=[{"explanation_id":"null","scientific_role":"FIXED_BED_MACHINE_AND_APPARATUS_NULL"},{"explanation_id":"other","scientific_role":role}]
 q="Q_SYNTH"; pair="PAIR_SYNTH"; scenario="MACHINE_REF"; intervention="MATCHED"; basis="BASIS"
 rid=f"REQ__{q}__{pair}__{scenario}__{intervention}__{basis}"
 body=dict(quantity_name="synthetic_quantity",comparable_observable_group="SYNTHETIC",channel=channel,unit="m/s",value_type="scalar",control_mode="MACHINE_COUPLED",pressure_node="NOT_APPLICABLE",pressure_reference="NOT_APPLICABLE",flow_basis="SUPERFICIAL_BED_AREA_VELOCITY",mass_basis="NOT_APPLICABLE",concentration_basis="NOT_APPLICABLE",deformation_basis="BED_HEIGHT" if channel=="bed_height_or_deformation" else "NOT_APPLICABLE",temperature_basis="NOT_APPLICABLE",time_origin="NOT_APPLICABLE",event_definition="NOT_APPLICABLE",summary_operator="IDENTITY",observation_window_start="NOT_APPLICABLE",observation_window_end="NOT_APPLICABLE",window_reference="NOT_APPLICABLE",spatial_basis="LUMPED_BED_AREA",aggregation_basis=basis,initialization_history_basis="SYNTHETIC_INITIALIZATION",mediation_status="SOURCE_NATIVE",adapter_id="DIRECT_NATIVE",adapter_version="1.0.0",adapter_contract_hash=governance.DIRECT_CONTRACT_HASH,uncertainty_basis="BOUNDED_SYNTHETIC",provenance="C1_R4_SYNTHETIC")
 oh=_hash(body); contract=ObservationContractRecord(f"OBS__{q}__{oh[:16]}",oh,**body).to_dict()
 req={"requirement_id":rid,"pair_id":pair,"left_explanation":"null","right_explanation":"other","scenario":scenario,"control_mode":"MACHINE_COUPLED","intervention_id":intervention,"pressure_node":"NOT_APPLICABLE","pressure_reference":"NOT_APPLICABLE","basis_id":basis,"time_basis":"NOT_APPLICABLE","pair_role":"SCIENTIFICALLY_COMPETING","scientific_question":"synthetic","relevant_to_final_decision":True,"applicable_candidate_channels":[channel],"requirement_status":"relevant","reason_code":"RELEVANT","provenance":"C1_R4_SYNTHETIC","question_id":q,"observation_family":channel,"observation_contract_id":contract["observation_contract_id"],"spatial_basis":"LUMPED_BED_AREA","relevance_status":"RELEVANT"}
 comp=ComparisonEligibilityRecord(pair,"null","other","synthetic",scenario,channel,intervention,basis,1,"SCIENTIFICALLY_COMPETING","eligible","RELEVANT","DIRECT_NATIVE","1.0.0",True,f"ELIG__{rid}__{channel}__DIRECT_NATIVE__1.0.0",rid,intervention,basis,"SUPPORTED",governance.DIRECT_CONTRACT_HASH,q,contract["observation_contract_id"],oh)
 right_value=3.0 if classification=="fail" else 1.05
 flags=["PARAMETER_UNCERTAINTY_NOT_PROVIDED"] if missing else []
 def pred(side,value): return PredictionIntervalRecord(f"PRED__{side}__{scenario}__{channel}",side,scenario,channel,"synthetic","m/s","NOT_APPLICABLE","NOT_APPLICABLE","NOT_APPLICABLE",value,value,value,"BOUNDED","BOUNDED","NOT_APPLICABLE","BOUNDED","SYNTHETIC","C1_R4_SYNTHETIC",flags)
 left,right=pred("null",1.0),pred("other",right_value)
 uncertainty="NOT_PROVIDED" if missing else 0.1
 measurement=build_measurement_record(pair=comp,channel=channel,left_support="SUPPORTED",right_support="SUPPORTED",left=left,right=right,measurement_uncertainty=uncertainty,uncertainty_provenance="C1_R4_SYNTHETIC")
 return ex,req,measurement.to_dict(),[comp.to_dict()],[left.to_dict(),right.to_dict()],[contract]

def evaluate(fixture):
 ex,req,m,comp,pred,contract=fixture; specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
 return evaluate_apparatus(ex,[req],[m],specs,comp,pred,contract)

@pytest.mark.parametrize("classification",["NOT_DISCRIMINATING","ROBUSTLY_DISCRIMINATING"])
def test_review_c1r3_001_empty_evidence_classification_is_rejected(classification):
 ex,req,m,_,_,_=closed_fixture(); m["classification"]=classification; m["robustly_covers_pair"]=classification=="ROBUSTLY_DISCRIMINATING"
 with pytest.raises(ValueError,match="dangling|closed evidence"):
  evaluate_apparatus(ex,[req],[m],[x.to_dict() for x in canonical_apparatus_gate_specs()],[],[],[])

def test_complete_closed_evidence_reaches_pass_fail_and_not_applicable():
 for kind,status in (("pass","SURVIVES_ALL_APPLICABLE_GATES"),("fail","RULED_OUT_BY_MATCHED_GATE")):
  evidence,results,apparatus=evaluate(closed_fixture(kind)); assert evidence and apparatus.status==status
  assert any(x.status==("PASS" if kind=="pass" else "FAIL") for x in results)
  assert any(x.status=="NOT_APPLICABLE" for x in results)

def test_missing_uncertainty_is_legitimate_unresolved():
 assert evaluate(closed_fixture(missing=True))[2].status=="UNRESOLVED_MISSING_UNCERTAINTY"

def test_partial_evidence_is_unresolved_but_dangling_is_invalid():
 ex,req,m,comp,pred,contract=closed_fixture(); specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
 assert evaluate_apparatus(ex,[req],[],specs,comp,pred,contract)[2].status=="UNRESOLVED_MISSING_UNCERTAINTY"
 m["left_prediction_id"]="DANGLING"
 with pytest.raises(ValueError,match="dangling prediction"): evaluate_apparatus(ex,[req],[m],specs,comp,pred,contract)

def test_no_comparator_is_not_evaluated():
 bundle=__import__("puckworks.analysis.response_atlas.runner",fromlist=["build_bundle"]).build_bundle()
 assert bundle["apparatus_evaluation"]["status"]=="NOT_EVALUATED"

@pytest.mark.parametrize("target,key",[("comparison",3),("prediction",4),("contract",5)])
def test_duplicate_id_rejected(target,key):
 fixture=list(closed_fixture()); fixture[key]=fixture[key]+[copy.deepcopy(fixture[key][0])]
 with pytest.raises(ValueError,match="duplicate"): evaluate(tuple(fixture))

def test_stale_classification_and_contract_rejected():
 fixture=list(closed_fixture("fail")); fixture[2]["classification"]="NOT_DISCRIMINATING"; fixture[2]["robustly_covers_pair"]=False
 with pytest.raises(ValueError,match="stale"): evaluate(tuple(fixture))
 fixture=list(closed_fixture()); fixture[5][0]["unit"]="kg/s"
 with pytest.raises(ValueError,match="stale observation contract hash"): evaluate(tuple(fixture))

def test_cross_case_and_wrong_context_rejected():
 fixture=list(closed_fixture()); fixture[4][0]["case_id"]="OTHER_CASE"
 with pytest.raises(ValueError,match="context mismatch"): evaluate(tuple(fixture))

def test_wrong_type_and_noncanonical_gate_records_rejected():
 fixture=list(closed_fixture()); fixture[3]=[fixture[4][0]]
 with pytest.raises((TypeError,ValueError)): evaluate(tuple(fixture))
 fixture=closed_fixture(); specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
 specs[0]["pass_rule"]="CALLER_CONTROLLED"
 with pytest.raises(ValueError,match="noncanonical"): evaluate_apparatus(
  fixture[0],[fixture[1]],[fixture[2]],specs,*fixture[3:])

def test_duplicate_measurement_and_explanation_id_rejected():
 ex,req,m,comp,pred,contract=closed_fixture(); specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
 with pytest.raises(ValueError,match="duplicate measurement"):
  evaluate_apparatus(ex,[req],[m,copy.deepcopy(m)],specs,comp,pred,contract)
 with pytest.raises(ValueError,match="duplicate explanation"):
  evaluate_apparatus(ex+[copy.deepcopy(ex[0])],[req],[m],specs,comp,pred,contract)

@pytest.mark.parametrize("field,value",[("unit","kg/s"),("pressure_node","OTHER_NODE"),
 ("time_origin","OTHER_ORIGIN"),("event_definition","OTHER_EVENT"),
 ("spatial_basis","LOCAL_MASK"),("aggregation_basis","CUP_LEVEL"),
 ("adapter_contract_hash","0"*64),("uncertainty_basis","OTHER_UNCERTAINTY")])
def test_self_consistent_contract_mutation_is_rejected_by_linked_evidence(field,value):
 bundle=runner.build_bundle(); changed=copy.deepcopy(bundle); contract=changed["observation_contracts"][0]
 old_id=contract["observation_contract_id"]; contract[field]=value
 body={k:v for k,v in contract.items() if k not in {"observation_contract_id","contract_sha256"}}
 new_hash=_hash(body); contract["contract_sha256"]=new_hash
 contract["observation_contract_id"]=old_id.rsplit("__",1)[0]+"__"+new_hash[:16]
 for key in ("discrimination_requirements","channel_eligibility","matched_comparisons"):
  for row in changed[key]:
   if row.get("observation_contract_id")==old_id:
    row["observation_contract_id"]=contract["observation_contract_id"]
    if "observation_contract_hash" in row: row["observation_contract_hash"]=new_hash
 with pytest.raises(ValueError,match="observation_contracts|semantically inconsistent"):
  runner.validate_bundle(changed)

def test_self_consistent_terminal_derivative_chain_is_rejected():
 bundle=runner.build_bundle(); changed=copy.deepcopy(bundle)
 changed["apparatus_evaluation"]["status"]="RULED_OUT_BY_MATCHED_GATE"
 changed["apparatus_evaluation"]["reason_code"]="MATCHED_GATE_FAILED"
 changed["decision"]["apparatus_status"]="RULED_OUT_BY_MATCHED_GATE"
 changed["decision"]["selected_outcome"]=DYNAMIC
 changed["summary_counts"]["apparatus_gate_statuses"]={"FAIL":1}
 with pytest.raises(ValueError): runner.validate_bundle(changed)

def test_independent_verifier_is_behaviorally_separate(monkeypatch):
 fixture=closed_fixture("fail"); ex,req,m,comp,pred,contract=fixture; specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
 monkeypatch.setattr(governance,"evaluate_apparatus",lambda *a,**k: (_ for _ in ()).throw(AssertionError("producer called")))
 assert reconstruct_apparatus(ex,[req],[m],specs,comp,pred,contract)[2].status=="RULED_OUT_BY_MATCHED_GATE"

@pytest.mark.parametrize("channel,role,expected",[("bed_height_or_deformation","DYNAMIC_BED_EXPLANATION",DYNAMIC),("spatial_flow_variance","SPATIAL_LOCALIZATION_EXPLANATION",SPATIAL)])
def test_downstream_requires_genuine_closed_ruleout(channel,role,expected):
 ex,req,m,comp,pred,contract=closed_fixture("fail",channel,role); specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
 evidence,results,apparatus=evaluate_apparatus(ex,[req],[m],specs,comp,pred,contract)
 edges=[x.to_dict() for x in build_coverage_edges([m],comp)]; minimum=minimum_measurement_sets([req],edges)
 decision=derive_scientific_decision(explanations=ex,requirements=[req],channel_eligibility=comp,component_reports={},comparison_records=comp,measurement_records=[m],coverage_edges=edges,minimum_measurement_sets=minimum,apparatus_gate_specs=specs,apparatus_gate_results=[x.to_dict() for x in results],apparatus_evaluation=apparatus.to_dict())
 assert evidence and decision.selected_outcome==expected

def test_record_order_is_deterministic():
 fixture=closed_fixture("fail"); first=evaluate(fixture); ex,req,m,comp,pred,contract=fixture
 second=evaluate((ex,req,m,comp,list(reversed(pred)),contract))
 assert [x.to_dict() for x in first[1]]==[x.to_dict() for x in second[1]]

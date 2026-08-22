"""Independent C1-R4 reconstruction from lower-level retained evidence.

This module deliberately does not import producer governance or decision functions.
"""
from __future__ import annotations
import hashlib, json, math
from .measurement_value import discriminate
from .schema import (ApparatusEvaluationRecord, ApparatusGateEvidenceRecord,
 ApparatusGateResult, ApparatusGateSpec, ComparisonEligibilityRecord,
 DiscriminationRequirementRecord, MeasurementValueRecord, ObservationContractRecord,
 PredictionIntervalRecord)

APPARATUS_VERSION="rp-a-001-apparatus-gates/v2"
CANONICAL_GATE_RECORDS_HASH="ca99ef7b9d49dba925602dbdc36aa915919496375e643322e274a9eb2bc5fcf3"
APPARATUS="SCI_MD_003_RP_A_001_APPARATUS_OBSERVATION_EXPLANATION_SURVIVES"
DYNAMIC="SCI_MD_003_RP_A_001_DYNAMIC_BED_SIGNATURE_DISTINGUISHABLE"
SPATIAL="SCI_MD_003_RP_A_001_SPATIAL_LOCALIZATION_ONLY_DISTINGUISHABLE_ROUTE"
ADDITIONAL="SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED"
DYNAMIC_CHANNELS={"bed_height_or_deformation"}
SPATIAL_CHANNELS={"spatial_flow_variance","local_extraction"}

def _hash(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _unique(rows,key,label):
 out={}
 for row in rows:
  identity=row.get(key)
  if not identity or identity in out: raise ValueError(f"invalid or duplicate {label} identity")
  out[identity]=row
 return out

def _classification(measurement,requirement,comparison,predictions,contract):
 MeasurementValueRecord.from_dict(measurement); ObservationContractRecord.from_dict(contract)
 body={k:v for k,v in contract.items() if k not in {"observation_contract_id","contract_sha256"}}
 if _hash(body)!=contract["contract_sha256"]: raise ValueError("independent stale contract hash")
 if comparison["requirement_id"]!=requirement["requirement_id"] or measurement["requirement_id"]!=requirement["requirement_id"]: raise ValueError("independent requirement mismatch")
 if comparison["question_id"]!=requirement["question_id"] or comparison["pair_id"]!=requirement["pair_id"]: raise ValueError("independent question/pair mismatch")
 if any(measurement[k]!=requirement[k] for k in ("pair_id","left_explanation","right_explanation","scenario","intervention_id","basis_id","observation_contract_id")): raise ValueError("independent requirement context mismatch")
 if measurement["eligibility_id"]!=comparison["eligibility_id"] or measurement["scenario"]!=requirement["scenario"]: raise ValueError("independent comparison/case mismatch")
 if measurement["channel"]!=comparison["candidate_observable"] or measurement["observation_contract_id"]!=contract["observation_contract_id"] or measurement["observation_contract_hash"]!=contract["contract_sha256"]: raise ValueError("independent channel/contract mismatch")
 if any(measurement[k]!=contract[k] for k in ("adapter_id","adapter_version","adapter_contract_hash")): raise ValueError("independent adapter mismatch")
 if (contract["control_mode"]!=requirement["control_mode"] or contract["pressure_node"]!=requirement["pressure_node"] or contract["pressure_reference"]!=requirement["pressure_reference"] or contract["time_origin"]!=requirement["time_basis"] or contract["spatial_basis"]!=requirement["spatial_basis"] or contract["aggregation_basis"]!=requirement["basis_id"]): raise ValueError("independent requirement/contract mismatch")
 if measurement["measurement_record_id"]!=f"MV__{measurement['requirement_id']}__{measurement['channel']}__{measurement['adapter_id']}__{measurement['adapter_version']}": raise ValueError("independent measurement identity mismatch")
 if measurement["measurement_option_id"]!=f"MEASOPT__{measurement['channel']}__{measurement['observation_contract_hash']}": raise ValueError("independent measurement option identity mismatch")
 left=predictions.get(measurement["left_prediction_id"]); right=predictions.get(measurement["right_prediction_id"])
 if left is None or right is None: raise ValueError("independent dangling prediction")
 for record,side in ((left,requirement["left_explanation"]),(right,requirement["right_explanation"])):
  PredictionIntervalRecord.from_dict(record)
  if record["prediction_id"]!=f"PRED__{side}__{measurement['scenario']}__{measurement['channel']}": raise ValueError("independent prediction identity mismatch")
  if record["explanation_id"]!=side or record["case_id"]!=measurement["scenario"] or record["channel"]!=measurement["channel"] or record["unit"]!=contract["unit"]: raise ValueError("independent prediction context mismatch")
  if record["pressure_node"]!=contract["pressure_node"] or record["pressure_reference"]!=contract["pressure_reference"] or record["time_basis"]!=contract["time_origin"]: raise ValueError("independent prediction contract mismatch")
 uncertainty=measurement["declared_measurement_uncertainty"]
 if uncertainty!="NOT_PROVIDED" and (not math.isfinite(float(uncertainty)) or float(uncertainty)<0): raise ValueError("independent invalid uncertainty")
 result=discriminate((left["lower_bound"],left["upper_bound"]),(right["lower_bound"],right["upper_bound"]),uncertainty)
 if left["missing_uncertainty_flags"] or right["missing_uncertainty_flags"]: result="NOT_ADJUDICATED_MISSING_UNCERTAINTY"
 if result!=measurement["classification"]: raise ValueError("independent stale classification")
 expanded_left=expanded_right=None
 if uncertainty!="NOT_PROVIDED":
  u=float(uncertainty); expanded_left=[left["lower_bound"]-u,left["upper_bound"]+u]; expanded_right=[right["lower_bound"]-u,right["upper_bound"]+u]
 reasons={"UNSUPPORTED":"RESPONSE_OR_RELATIONSHIP_UNSUPPORTED","NOT_ADJUDICATED_MISSING_UNCERTAINTY":"MEASUREMENT_OR_MODEL_UNCERTAINTY_NOT_PROVIDED","ROBUSTLY_DISCRIMINATING":"CONSERVATIVE_EXPANDED_INTERVALS_DISJOINT","NOMINALLY_DISCRIMINATING_BUT_UNCERTAINTY_OVERLAPS":"NOMINAL_INTERVALS_DISJOINT_EXPANDED_INTERVALS_OVERLAP","NOT_DISCRIMINATING":"PREDICTION_INTERVALS_OVERLAP"}
 if measurement["expanded_left_interval"]!=expanded_left or measurement["expanded_right_interval"]!=expanded_right or measurement["reason_code"]!=reasons[result] or measurement["evidence_references"]!=[measurement["eligibility_id"]]: raise ValueError("independent stale measurement derivatives")
 return result

def reconstruct_apparatus(explanations,requirements,measurements,specs,comparisons,predictions,contracts):
 aids=sorted(x["explanation_id"] for x in explanations if x["scientific_role"]=="FIXED_BED_MACHINE_AND_APPARATUS_NULL")
 matched=[r for r in requirements if r["relevance_status"]=="RELEVANT" and ({r["left_explanation"],r["right_explanation"]}&set(aids))]
 if _hash(specs)!=CANONICAL_GATE_RECORDS_HASH: raise ValueError("independent noncanonical gate specification")
 _unique(explanations,"explanation_id","explanation")
 for requirement in requirements: DiscriminationRequirementRecord.from_dict(requirement)
 for spec in specs: ApparatusGateSpec.from_dict(spec)
 for comparison in comparisons: ComparisonEligibilityRecord.from_dict(comparison)
 for prediction in predictions: PredictionIntervalRecord.from_dict(prediction)
 reqmap=_unique(requirements,"requirement_id","requirement"); specmap=_unique(specs,"gate_id","gate")
 compmap=_unique(comparisons,"eligibility_id","comparison"); predmap=_unique(predictions,"prediction_id","prediction")
 contractmap=_unique(contracts,"observation_contract_id","contract"); _unique(measurements,"measurement_record_id","measurement")
 for contract in contracts:
  ObservationContractRecord.from_dict(contract)
  body={k:v for k,v in contract.items() if k not in {"observation_contract_id","contract_sha256"}}
  if _hash(body)!=contract["contract_sha256"]: raise ValueError("independent stale contract hash")
 for measurement in measurements: MeasurementValueRecord.from_dict(measurement)
 if not matched: return [],[],ApparatusEvaluationRecord("APPARATUS_EVALUATION",aids,"NOT_EVALUATED",[],[],[],[],False,[],"NO_MATCHED_APPARATUS_COMPARATOR",APPARATUS_VERSION,[],[],False,[],[])
 evidence=[]; results=[]
 for req in matched:
  if req["requirement_id"] not in reqmap: raise ValueError("independent dangling requirement")
  apparatus_id=next(iter({req["left_explanation"],req["right_explanation"]}&set(aids))); comparator=req["right_explanation"] if req["left_explanation"]==apparatus_id else req["left_explanation"]
  rows=[m for m in measurements if m["requirement_id"]==req["requirement_id"]]
  for spec in specs:
   if spec["gate_id"] not in specmap: raise ValueError("independent dangling gate")
   exposed=spec["primary"] or spec["gate_name"].lower() in req["applicable_candidate_channels"]
   related=[m for m in rows if m["channel"] in {spec["gate_name"].lower(),req["observation_family"]}]
   if not exposed: uncertainty,status,reason="NOT_REQUIRED","NOT_APPLICABLE","SCENARIO_DOES_NOT_EXPOSE_GATE"
   elif not related: uncertainty,status,reason="MISSING","UNRESOLVED","APPLICABLE_GATE_EVIDENCE_MISSING"
   else:
    classes=[]
    for measurement in related:
     comparison=compmap.get(measurement["eligibility_id"]); contract=contractmap.get(measurement["observation_contract_id"])
     if comparison is None or contract is None: raise ValueError("independent dangling comparison or contract")
     classes.append(_classification(measurement,req,comparison,predmap,contract))
    if "NOT_ADJUDICATED_MISSING_UNCERTAINTY" in classes: uncertainty,status,reason="MISSING","UNRESOLVED","GATE_UNCERTAINTY_MISSING"
    elif any(m["comparability_level"]>2 for m in related) or "UNSUPPORTED" in classes: uncertainty,status,reason="COMPLETE","UNRESOLVED","GATE_EVIDENCE_UNSUPPORTED_OR_NONCOMPARABLE"
    elif "ROBUSTLY_DISCRIMINATING" in classes: uncertainty,status,reason="COMPLETE","FAIL","ROBUST_MATCHED_GATE_DISAGREEMENT"
    else: uncertainty,status,reason="COMPLETE","PASS","MATCHED_GATE_AGREES_WITHIN_UNCERTAINTY"
   evidence_ids=[]; comparison_ids=sorted({m["eligibility_id"] for m in related})
   if related:
    eid=f"APP_EVIDENCE__{spec['gate_name']}__{req['requirement_id']}"; evidence_ids=[eid]
    evidence.append(ApparatusGateEvidenceRecord(eid,spec["gate_id"],apparatus_id,comparator,req["requirement_id"],req["scenario"],req["observation_contract_id"],comparison_ids,[m["measurement_record_id"] for m in related],sorted({x for m in related for x in (m["left_prediction_id"],m["right_prediction_id"]) if x}),uncertainty,"DISAGREES" if status=="FAIL" else "AGREES" if status=="PASS" else "UNRESOLVED",[f"measurement:{m['measurement_record_id']}" for m in related]))
   results.append(ApparatusGateResult(f"APP_RESULT__{spec['gate_name']}__{req['requirement_id']}",spec["gate_id"],apparatus_id,comparator,req["scenario"],"APPLICABLE" if exposed else "NOT_APPLICABLE_BY_PROTOCOL",status,comparison_ids,[m["measurement_record_id"] for m in related],uncertainty,reason,[f"requirement:{req['requirement_id']}"],req["requirement_id"],req["observation_contract_id"],sorted({x for m in related for x in (m["left_prediction_id"],m["right_prediction_id"]) if x}),evidence_ids))
 passing=[x.gate_result_id for x in results if x.status=="PASS"]; failing=[x.gate_result_id for x in results if x.status=="FAIL"]; unresolved=[x.gate_result_id for x in results if x.status=="UNRESOLVED"]; na=[x.gate_result_id for x in results if x.status=="NOT_APPLICABLE"]; applicable=[x.gate_result_id for x in results if x.status!="NOT_APPLICABLE"]
 status="RULED_OUT_BY_MATCHED_GATE" if failing else "UNRESOLVED_MISSING_UNCERTAINTY" if any(x.uncertainty_state=="MISSING" for x in results if x.status=="UNRESOLVED") else "UNRESOLVED_UNSUPPORTED_GATE" if unresolved else "SURVIVES_ALL_APPLICABLE_GATES" if applicable else "NOT_APPLICABLE"
 return evidence,results,ApparatusEvaluationRecord("APPARATUS_EVALUATION",aids,status,applicable,passing,failing,unresolved,bool(applicable and not failing and not unresolved),sorted({x.scenario for x in results}),"MATCHED_GATE_FAILED" if failing else "ALL_APPLICABLE_GATES_PASS" if status=="SURVIVES_ALL_APPLICABLE_GATES" else "APPLICABLE_GATE_UNRESOLVED",APPARATUS_VERSION,na,[x.gate_evidence_id for x in evidence],not any(x.uncertainty_state=="MISSING" for x in results),[z for x in results if x.status=="FAIL" for z in (x.gate_evidence_ids or [])],[z for x in results if x.status=="PASS" for z in (x.gate_evidence_ids or [])])

def independently_select(explanations,measurements,minimum,apparatus):
 ruled=apparatus["status"]=="RULED_OUT_BY_MATCHED_GATE"; complete=bool(minimum["complete"]); sets=minimum["all_equally_minimal_sets"]
 dynamic_ids={x["explanation_id"] for x in explanations if "DYNAMIC_BED" in x["scientific_role"]}; spatial_ids={x["explanation_id"] for x in explanations if "SPATIAL" in x["scientific_role"]}
 robust=[m for m in measurements if m["classification"]=="ROBUSTLY_DISCRIMINATING"]
 dynamic=[m for m in robust if m["channel"] in DYNAMIC_CHANNELS and ({m["left_explanation"],m["right_explanation"]}&dynamic_ids)]; spatial=[m for m in robust if m["channel"] in SPATIAL_CHANNELS and ({m["left_explanation"],m["right_explanation"]}&spatial_ids)]
 dopts={m["measurement_option_id"] for m in dynamic}; sopts={m["measurement_option_id"] for m in spatial}
 if apparatus["status"]=="SURVIVES_ALL_APPLICABLE_GATES" and apparatus["apparatus_gate_coverage_complete"]: return APPARATUS
 if ruled and complete and dynamic and len(dopts)==1 and sets and all(set(s)&dopts for s in sets) and not any(not(set(s)&dopts) for s in sets): return DYNAMIC
 if ruled and complete and spatial and len(sopts)==1 and sets and all(set(s)&sopts for s in sets) and not any(not(set(s)&sopts) for s in sets): return SPATIAL
 return ADDITIONAL

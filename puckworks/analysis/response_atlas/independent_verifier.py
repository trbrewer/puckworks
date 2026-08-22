"""Independent C1-R4 reconstruction from lower-level retained evidence.

This module deliberately does not import producer governance or decision functions.
"""
from __future__ import annotations
import hashlib, json, math
from pathlib import Path
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
ROOT=Path(__file__).resolve().parents[3]

def _hash(value): return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _unique(rows,key,label):
 out={}
 for row in rows:
  identity=row.get(key)
  if not identity or identity in out: raise ValueError(f"invalid or duplicate {label} identity")
  out[identity]=row
 return out

def _file_hash(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def independently_validate_bundle_universe(bundle, authoritative_contracts,
                                           authoritative_comparisons):
 """Independent full-bundle ownership and provenance reconstruction."""
 manifest=bundle["run_manifest"]
 cards={name:_file_hash(ROOT/"docs/cards"/name) for name in (
  "foster2025_2.md","wadsworth2026.md","wadsworth2026_inertial.md",
  "wadsworth2026_grindmap.md","cameron2020.md")}
 selected={"foster2025.machine_mode","wadsworth2026.inertial","cameron2020.extraction_bdf"}
 expected_hashes={
  "component_response_atlas_spec_sha256":_file_hash(ROOT/"docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md"),
  "c1_protocol_sha256":_file_hash(ROOT/"docs/analysis/rp_a_001/c1/correction_protocol.json"),
  "c1_r1_protocol_sha256":_file_hash(ROOT/"docs/analysis/rp_a_001/c1_r1/correction_protocol.json"),
  "c1_r2_protocol_sha256":_file_hash(ROOT/"docs/analysis/rp_a_001/c1_r2/correction_protocol.json"),
  "protocol_sha256":_file_hash(ROOT/"docs/analysis/rp_a_001/c1_r3/correction_protocol.json"),
  "case_matrix_sha256":_file_hash(ROOT/"docs/analysis/rp_a_001/c1/case_matrix.json"),
  "measurement_assumption_sha256":_file_hash(ROOT/"docs/analysis/rp_a_001/c1/measurement_assumptions.json"),
  "registry_snapshot_sha256":_file_hash(ROOT/"puckworks/models/__init__.py")}
 for field,value in expected_hashes.items():
  if manifest.get(field)!=value: raise ValueError(f"independent AUTHORITATIVE_PROVENANCE_MISMATCH: {field}")
 if manifest.get("selected_card_sha256")!=cards or set(manifest.get("selected_components",[]))!=selected:
  raise ValueError("independent UNAUTHORIZED_ROOT: cards or components")
 explanations=_unique(bundle["explanations"],"explanation_id","explanation")
 if {x["component_id"] for x in explanations.values()}!=selected:
  raise ValueError("independent UNAUTHORIZED_ROOT: explanations")
 for explanation in explanations.values():
  if explanation["registry_identity"]!=expected_hashes["registry_snapshot_sha256"] or explanation["card_identity"] not in set(cards.values()):
   raise ValueError("independent AUTHORITATIVE_PROVENANCE_MISMATCH: explanation")
 if bundle["observation_contracts"]!=authoritative_contracts:
  raise ValueError("independent AUTHORITATIVE_PROVENANCE_MISMATCH: contract universe")
 if bundle["matched_comparisons"]!=authoritative_comparisons:
  raise ValueError("independent EXTRANEOUS_MATERIAL_RECORD: comparison universe")
 case_data=json.loads((ROOT/"docs/analysis/rp_a_001/c1/case_matrix.json").read_text())
 cases={row["case_id"] for row in case_data["cases"]}|{"WADSWORTH_WORKED_FO_ENDPOINTS"}
 cell_keys=set()
 for cell in bundle["result_cells"]:
  key=(cell["component_id"],cell["case_id"],cell["observable"])
  if key in cell_keys: raise ValueError("independent DUPLICATE_ID: result cell")
  cell_keys.add(key)
  if cell["component_id"] not in selected or cell["case_id"] not in cases:
   raise ValueError("independent ORPHAN_RECORD: result cell")
 if set(bundle["component_reports"])!=selected:
  raise ValueError("independent ORPHAN_RECORD: component report")
 for row in bundle["quantity_inventory"]:
  if row["component_id"] not in selected:
   raise ValueError("independent ORPHAN_RECORD: quantity inventory")
 requirements={row["requirement_id"] for row in bundle["discrimination_requirements"]}
 measurements={row["measurement_record_id"] for row in bundle["measurement_value_records"]}
 comparisons={row["eligibility_id"] for row in bundle["matched_comparisons"]}
 predictions={row["prediction_id"] for row in bundle["prediction_intervals"]}
 evidence=_unique(bundle["apparatus_gate_evidence"],"gate_evidence_id","gate evidence")
 results=_unique(bundle["apparatus_gate_results"],"gate_result_id","gate result")
 referenced_evidence=set()
 for row in evidence.values():
  if row["requirement_id"] not in requirements or not set(row["comparison_record_ids"])<=comparisons or not set(row["measurement_record_ids"])<=measurements or not set(row["prediction_interval_ids"] or [])<=predictions:
   raise ValueError("independent DANGLING_REFERENCE: gate evidence")
 for row in results.values():
  if row["requirement_id"] not in requirements or not set(row["gate_evidence_ids"] or [])<=set(evidence):
   raise ValueError("independent DANGLING_REFERENCE: gate result")
  referenced_evidence.update(row["gate_evidence_ids"] or [])
 if referenced_evidence!=set(evidence): raise ValueError("independent ORPHAN_RECORD: gate evidence")
 apparatus=bundle["apparatus_evaluation"]
 referenced_results=set(apparatus["applicable_gate_result_ids"]+apparatus["passing_gate_result_ids"]+
                        apparatus["failing_gate_result_ids"]+apparatus["unresolved_gate_result_ids"]+
                        apparatus["not_applicable_gate_result_ids"])
 if referenced_results!=set(results): raise ValueError("independent ORPHAN_RECORD: gate result")
 edge_ids=set()
 for edge in bundle["coverage_edges"]:
  if edge["coverage_edge_id"] in edge_ids: raise ValueError("independent DUPLICATE_ID: coverage edge")
  edge_ids.add(edge["coverage_edge_id"])
  if edge["requirement_id"] not in requirements or edge["measurement_record_id"] not in measurements:
   raise ValueError("independent DANGLING_REFERENCE: coverage edge")
 matrix_edges={identity for row in bundle["coverage_matrix"] for identity in row["coverage_edge_ids"]}
 if matrix_edges!=edge_ids: raise ValueError("independent ORPHAN_RECORD: coverage edge")
 return True

def _independent_global_universe(explanations,requirements,measurements,specs,
                                 comparisons,predictions,contracts,
                                 authoritative_contracts):
 if authoritative_contracts is None:
  raise ValueError("independent UNAUTHORIZED_ROOT: authoritative contracts required")
 explanation_ids=set(_unique(explanations,"explanation_id","explanation"))
 reqmap=_unique(requirements,"requirement_id","requirement")
 specmap=_unique(specs,"gate_id","gate")
 compmap=_unique(comparisons,"eligibility_id","comparison")
 predmap=_unique(predictions,"prediction_id","prediction")
 contractmap=_unique(contracts,"observation_contract_id","contract")
 _unique(measurements,"measurement_record_id","measurement")
 authority=_unique(authoritative_contracts,"observation_contract_id","authoritative contract")
 for requirement in requirements:
  DiscriminationRequirementRecord.from_dict(requirement)
  if requirement["left_explanation"] not in explanation_ids or requirement["right_explanation"] not in explanation_ids:
   raise ValueError("independent DANGLING_REFERENCE: requirement explanation")
  if requirement["observation_contract_id"] not in contractmap:
   raise ValueError("independent DANGLING_REFERENCE: requirement contract")
 for spec in specs: ApparatusGateSpec.from_dict(spec)
 for contract in contracts:
  ObservationContractRecord.from_dict(contract)
  body={k:v for k,v in contract.items() if k not in {"observation_contract_id","contract_sha256"}}
  if _hash(body)!=contract["contract_sha256"] or not contract["observation_contract_id"].endswith(contract["contract_sha256"][:16]):
   raise ValueError("independent CANONICAL_IDENTITY_MISMATCH: contract")
  if authority.get(contract["observation_contract_id"])!=contract:
   raise ValueError("independent AUTHORITATIVE_PROVENANCE_MISMATCH: contract")
 if set(contractmap)!=set(authority):
  raise ValueError("independent ORPHAN_RECORD: contract universe")
 fields=("requirement_id","pair_id","left_explanation","right_explanation","scenario",
         "intervention_id","basis_id","question_id","observation_contract_id")
 for comparison in comparisons:
  ComparisonEligibilityRecord.from_dict(comparison)
  requirement=reqmap.get(comparison["requirement_id"])
  if requirement is None: raise ValueError("independent DANGLING_REFERENCE: comparison requirement")
  if any(comparison[field]!=requirement[field] for field in fields):
   raise ValueError("independent CROSS_CONTEXT_REFERENCE: comparison requirement")
  contract=contractmap.get(comparison["observation_contract_id"])
  if contract is None: raise ValueError("independent DANGLING_REFERENCE: comparison contract")
  if (comparison["candidate_observable"]!=contract["channel"] or
      comparison["observation_contract_hash"]!=contract["contract_sha256"] or
      comparison["adapter_id"]!=contract["adapter_id"] or
      comparison["adapter_version"]!=contract["adapter_version"] or
      comparison["adapter_contract_hash"]!=contract["adapter_contract_hash"]):
   raise ValueError("independent CROSS_CONTEXT_REFERENCE: comparison contract")
 for prediction in predictions:
  PredictionIntervalRecord.from_dict(prediction)
  if prediction["explanation_id"] not in explanation_ids:
   raise ValueError("independent DANGLING_REFERENCE: prediction explanation")
  if prediction["prediction_id"]!=f"PRED__{prediction['explanation_id']}__{prediction['case_id']}__{prediction['channel']}":
   raise ValueError("independent CANONICAL_IDENTITY_MISMATCH: prediction")
  owned=False
  for requirement in requirements:
   contract=contractmap[requirement["observation_contract_id"]]
   if (prediction["explanation_id"] in {requirement["left_explanation"],requirement["right_explanation"]} and
       prediction["case_id"]==requirement["scenario"] and
       prediction["channel"] in set(requirement["applicable_candidate_channels"]+[requirement["observation_family"]]) and
       prediction["channel"]==contract["channel"] and prediction["unit"]==contract["unit"] and
       prediction["pressure_node"]==contract["pressure_node"] and
       prediction["pressure_reference"]==contract["pressure_reference"] and
       prediction["time_basis"]==contract["time_origin"]): owned=True
  if not owned: raise ValueError("independent ORPHAN_RECORD: prediction")
 for measurement in measurements:
  requirement=reqmap.get(measurement.get("requirement_id"))
  comparison=compmap.get(measurement.get("eligibility_id"))
  contract=contractmap.get(measurement.get("observation_contract_id"))
  if requirement is None or comparison is None or contract is None:
   raise ValueError("independent DANGLING_REFERENCE: measurement")
  _classification(measurement,requirement,comparison,predmap,contract)
 return reqmap,specmap,compmap,predmap,contractmap

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

def reconstruct_apparatus(explanations,requirements,measurements,specs,comparisons,predictions,contracts,*,authoritative_contracts=None):
 aids=sorted(x["explanation_id"] for x in explanations if x["scientific_role"]=="FIXED_BED_MACHINE_AND_APPARATUS_NULL")
 matched=[r for r in requirements if r["relevance_status"]=="RELEVANT" and ({r["left_explanation"],r["right_explanation"]}&set(aids))]
 if _hash(specs)!=CANONICAL_GATE_RECORDS_HASH: raise ValueError("independent noncanonical gate specification")
 reqmap,specmap,compmap,predmap,contractmap=_independent_global_universe(
  explanations,requirements,measurements,specs,comparisons,predictions,contracts,
  authoritative_contracts)
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

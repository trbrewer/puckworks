"""Independent questions, observation contracts, coverage, and apparatus gates."""
from __future__ import annotations
from itertools import combinations
import hashlib, json
from .schema import (ApparatusEvaluationRecord, ApparatusGateEvidenceRecord, ApparatusGateResult,
 ApparatusGateSpec, ComparisonEligibilityRecord, CoverageEdgeRecord, DiscriminationRequirementRecord,
 ObservationContractRecord, ScientificQuestionRecord)

COVERAGE_VERSION="rp-a-001-coverage/v3"; APPARATUS_VERSION="rp-a-001-apparatus-gates/v2"
QUESTION_VERSION="rp-a-001-scientific-questions/v1"; REQUIREMENT_VERSION="rp-a-001-requirements/v3"
OBSERVATION_VERSION="rp-a-001-observation-contract/v1"; SEMANTIC_VERSION="rp-a-001-semantic-validation/v2"
DIRECT_CONTRACT_HASH=hashlib.sha256(b"DIRECT_NATIVE/1.0.0").hexdigest()
GATES=(("SIGN",True),("PRESSURE_OR_FLOW_ORDERING",True),("PRESSURE_LAG",False),("TRANSIENT_TIMING",False),("FIRST_DRIP_TIMING",False),("FLOW_MINIMUM",False),("FLOW_RECOVERY",False),("CROSS_CONDITION_TRANSFER",False))

def _hash(x): return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(",",":")).encode()).hexdigest()

def canonical_scientific_questions(explanations):
 roles={e["explanation_id"]:e["scientific_role"] for e in explanations}
 raw=(("Q_FOSTER_CAMERON_MACHINE","PAIR_FOSTER_CAMERON_MACHINE","FOSTER_FIXED_BED_MACHINE_NULL","CAMERON_EXTRACTION_OBSERVER","MACHINE_REF","OBSERVATION_OPERATOR_COMPARISON","EXCLUDED_OBSERVATION_OPERATOR_RELATIONSHIP","observation operator is not a competing hydraulic explanation","MACHINE_COUPLED","MACHINE_PROGRAM","FLOW_TRAJECTORY"),("Q_FOSTER_WADSWORTH_FLOW","PAIR_FOSTER_WADSWORTH_FLOW","FOSTER_FIXED_BED_MACHINE_NULL","WADSWORTH_STATIC_INERTIAL_LENS","MACHINE_REF","NONCOMPETING_COMPONENTS","EXCLUDED_NONCOMPETING_COMPONENTS","machine transient and static response lens answer different questions","MACHINE_COUPLED","MACHINE_PROGRAM","FLOW_TRAJECTORY"),("Q_WADSWORTH_CAMERON_FLOW","PAIR_WADSWORTH_CAMERON_FLOW","WADSWORTH_STATIC_INERTIAL_LENS","CAMERON_EXTRACTION_OBSERVER","P09_REF","OBSERVATION_OPERATOR_COMPARISON","EXCLUDED_OBSERVATION_OPERATOR_RELATIONSHIP","bed-drop lens and downstream observer are not competing explanations","PRESCRIBED_PRESSURE","P09","FLOW_SCALAR"),("Q_WADSWORTH_NESTED_LIMIT","PAIR_WADSWORTH_NESTED_LIMIT","WADSWORTH_STATIC_INERTIAL_LENS","WADSWORTH_STATIC_INERTIAL_LENS","WADSWORTH_WORKED_FO_ENDPOINTS","NESTED_LIMIT","EXCLUDED_NESTED_LIMIT_ONLY","retained for residual closure, not global discrimination","PRESCRIBED_BED_PRESSURE_GRADIENT","SOURCE_REFERENCE","SUPERFICIAL_VELOCITY"))
 return [ScientificQuestionRecord(q,p,l,r,"DIRECTIONAL",role,"bounded common-observable response",s,c,i,b,[roles[l],roles[r]],role=="SCIENTIFICALLY_COMPETING",role=="OBSERVATION_OPERATOR_COMPARISON",role=="NESTED_LIMIT","WITHIN_RETAINED_ROLE_METADATA",rel,reason,"C1_R3_CANONICAL_QUESTION_REGISTRY",QUESTION_VERSION,"flow",["flow"]) for q,p,l,r,s,role,rel,reason,c,i,b in raw]

def canonical_observation_contracts(questions):
 out=[]
 for q in questions:
  static=q["scenario_id"]!="MACHINE_REF"
  d=dict(quantity_name="superficial_darcy_velocity",comparable_observable_group="HYDRAULIC_FLOW",channel="flow",unit="m/s",value_type="scalar" if static else "trajectory",control_mode=q["control_mode"],pressure_node="BED_PRESSURE_DROP" if "WADSWORTH" in q["question_id"] else "NOT_APPLICABLE",pressure_reference="DIFFERENTIAL" if "WADSWORTH" in q["question_id"] else "NOT_APPLICABLE",flow_basis="SUPERFICIAL_BED_AREA_VELOCITY",mass_basis="NOT_APPLICABLE",concentration_basis="NOT_APPLICABLE",deformation_basis="NOT_APPLICABLE",temperature_basis="SOURCE_DECLARED",time_origin="NOT_APPLICABLE" if static else "MACHINE_COMMAND_START",event_definition="NOT_APPLICABLE",summary_operator="IDENTITY" if static else "FULL_TRAJECTORY",observation_window_start="NOT_APPLICABLE" if static else 0.0,observation_window_end="NOT_APPLICABLE" if static else "SOURCE_SHOT_END",window_reference="NOT_APPLICABLE" if static else "MACHINE_COMMAND_START",spatial_basis="LUMPED_BED_AREA",aggregation_basis=q["comparison_basis"],initialization_history_basis="SOURCE_SCENARIO_INITIALIZATION",mediation_status="SOURCE_NATIVE",adapter_id="DIRECT_NATIVE",adapter_version="1.0.0",adapter_contract_hash=DIRECT_CONTRACT_HASH,uncertainty_basis="NOT_PROVIDED",provenance="C1_R3_CANONICAL_OBSERVATION_CONTRACT")
  h=_hash(d); out.append(ObservationContractRecord(f"OBS__{q['question_id']}__{h[:16]}",h,**d))
 return out

def build_requirements(questions,contracts):
 if questions and "eligibility_id" in questions[0]: raise ValueError("requirements must be built from scientific questions, never eligibility")
 cm={c["observation_contract_id"].split("__")[1]:c for c in contracts}; out=[]
 for q in sorted(questions,key=lambda x:x["question_id"]):
  c=cm[q["question_id"]]; rel=q["relevance_status"]=="RELEVANT"; rid=f"REQ__{q['question_id']}__{q['pair_id']}__{q['scenario_id']}__{q['intervention_id']}__{q['comparison_basis']}"
  out.append(DiscriminationRequirementRecord(rid,q["pair_id"],q["left_explanation"],q["right_explanation"],q["scenario_id"],q["control_mode"],q["intervention_id"],c["pressure_node"],c["pressure_reference"],q["comparison_basis"],c["time_origin"],q["pair_role"],q["scientific_purpose"],rel,q["candidate_channel_classes"],"relevant" if rel else "irrelevant",q["relevance_status"],f"scientific_question:{q['question_id']}",q["question_id"],q["observation_family"],c["observation_contract_id"],c["spatial_basis"],q["relevance_status"]))
 return out

def build_channel_eligibility(questions,requirements,contracts):
 qm={q["question_id"]:q for q in questions}; cm={c["observation_contract_id"]:c for c in contracts}; out=[]
 for r in requirements:
  q=qm[r["question_id"]]; c=cm[r["observation_contract_id"]]; level={"NESTED_LIMIT":1,"NONCOMPETING_COMPONENTS":3}.get(q["pair_role"],4); state="unresolved" if q["pair_role"]=="NESTED_LIMIT" else "ineligible"; eid=f"ELIG__{r['requirement_id']}__{c['channel']}__{c['adapter_id']}__{c['adapter_version']}"
  out.append(ComparisonEligibilityRecord(q["pair_id"],q["left_explanation"],q["right_explanation"],q["scientific_purpose"],q["scenario_id"],c["channel"],q["intervention_id"],q["comparison_basis"],level,q["pair_role"],state,q["exclusion_reason"],c["adapter_id"],c["adapter_version"],False,eid,r["requirement_id"],q["intervention_id"],q["comparison_basis"],"NOT_EVALUATED",c["adapter_contract_hash"],q["question_id"],c["observation_contract_id"],c["contract_sha256"]))
 return out

def validate_measurement_linkage(m,e):
 fields=("requirement_id","pair_id","left_explanation","right_explanation","scenario","adapter_id","adapter_version","adapter_contract_hash","comparability_level","intervention_id","basis_id","observation_contract_id","observation_contract_hash")
 if e is None or any(m[f]!=e[f] for f in fields) or e["candidate_observable"]!=m["channel"]: raise ValueError("measurement record lacks exact channel eligibility")
 if m["measurement_option_id"]!=f"MEASOPT__{m['channel']}__{m['observation_contract_hash']}": raise ValueError("measurement option does not bind observation contract")

def build_coverage_edges(ms,es):
 em={e["eligibility_id"]:e for e in es}; out=[]
 for m in ms:
  e=em[m["eligibility_id"]]
  if m["classification"]=="ROBUSTLY_DISCRIMINATING" and m["comparability_level"]<=2 and e["eligibility"]=="eligible" and e["uncertainty_available"]: out.append(CoverageEdgeRecord(f"EDGE__{m['measurement_record_id']}__{m['requirement_id']}",m["requirement_id"],m["measurement_record_id"],m["measurement_option_id"],m["scenario"],m["channel"],m["adapter_id"],m["adapter_version"],m["classification"],True,f"measurement:{m['measurement_record_id']}",m["observation_contract_id"],m["observation_contract_hash"]))
 return sorted(out,key=lambda x:x.coverage_edge_id)

def coverage_matrix(requirements,edges):
 return [{"measurement_option_id":o,"covered_requirement_ids":sorted(e["requirement_id"] for e in edges if e["measurement_option_id"]==o),"coverage_edge_ids":sorted(e["coverage_edge_id"] for e in edges if e["measurement_option_id"]==o)} for o in sorted({e["measurement_option_id"] for e in edges})]

def minimum_measurement_sets(rs,edges):
 u=sorted(r["requirement_id"] for r in rs if r["relevance_status"]=="RELEVANT"); opts={}
 for e in edges: opts.setdefault(e["measurement_option_id"],set()).add(e["requirement_id"])
 unc=sorted(set(u)-set().union(*opts.values())) if opts else u; sets=[]
 if u and not unc:
  for n in range(1,len(opts)+1):
   sets=[list(c) for c in combinations(sorted(opts),n) if set().union(*(opts[x] for x in c))>=set(u)]
   if sets: break
 complete=bool(u and sets and not unc)
 return {"algorithm_version":COVERAGE_VERSION,"universe_requirement_ids":u,"coverage_options":{k:sorted(v) for k,v in sorted(opts.items())},"minimum_set_ids":[f"MINSET__{i+1}" for i in range(len(sets))],"all_equally_minimal_sets":sets,"uncovered_requirement_ids":unc,"complete":complete,"zero_universe_status":"NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM" if not u else "ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM_PRESENT","result":sets if complete else "NO_COMPLETE_MEASUREMENT_SET"}

def canonical_apparatus_gate_specs():
 return [ApparatusGateSpec(f"APP_GATE__{n}",n,p,"MATCHED_MACHINE_SCENARIO" if p else f"SCENARIO_EXPOSES_{n}","MATCHED_LEVEL_1_OR_2_OBSERVATION_CONTRACT",2,True,"AGREES_OR_EQUIVALENT_WITH_COMPLETE_UNCERTAINTY","ROBUST_DISAGREEMENT",APPARATUS_VERSION,"primary" if p else "conditional",f"evaluate {n}",[n],n,["MACHINE_REF"],f"QUERY_{n}","MISSING_OR_NONCOMPARABLE_IS_UNRESOLVED",f"ONLY_WHEN_SCENARIO_DOES_NOT_EXPOSE_{n}",p,QUESTION_VERSION) for n,p in GATES]
apparatus_gate_specs=canonical_apparatus_gate_specs

def evaluate_apparatus(explanations,requirements,measurements,specs,comparisons=None,predictions=None,contracts=None):
 aids=sorted(e["explanation_id"] for e in explanations if e["scientific_role"]=="FIXED_BED_MACHINE_AND_APPARATUS_NULL"); matched=[r for r in requirements if r["relevance_status"]=="RELEVANT" and ({r["left_explanation"],r["right_explanation"]}&set(aids))]
 if not matched: return [],[],ApparatusEvaluationRecord("APPARATUS_EVALUATION",aids,"NOT_EVALUATED",[],[],[],[],False,[],"NO_MATCHED_APPARATUS_COMPARATOR",APPARATUS_VERSION,[],[],False,[],[])
 evs=[]; results=[]
 for r in matched:
  aid=next(iter({r["left_explanation"],r["right_explanation"]}&set(aids))); comp=r["right_explanation"] if r["left_explanation"]==aid else r["left_explanation"]; rows=[m for m in measurements if m["requirement_id"]==r["requirement_id"]]
  for s in specs:
   exposed=s["primary"] or s["gate_name"].lower() in r["applicable_candidate_channels"]; rel=[m for m in rows if m["channel"] in {s["gate_name"].lower(),r["observation_family"]}]
   if not exposed: ust,st,reason="NOT_REQUIRED","NOT_APPLICABLE","SCENARIO_DOES_NOT_EXPOSE_GATE"
   elif not rel: ust,st,reason="MISSING","UNRESOLVED","APPLICABLE_GATE_EVIDENCE_MISSING"
   elif any(m["classification"]=="NOT_ADJUDICATED_MISSING_UNCERTAINTY" for m in rel): ust,st,reason="MISSING","UNRESOLVED","GATE_UNCERTAINTY_MISSING"
   elif any(m["comparability_level"]>2 or m["classification"]=="UNSUPPORTED" for m in rel): ust,st,reason="COMPLETE","UNRESOLVED","GATE_EVIDENCE_UNSUPPORTED_OR_NONCOMPARABLE"
   elif any(m["classification"]=="ROBUSTLY_DISCRIMINATING" for m in rel): ust,st,reason="COMPLETE","FAIL","ROBUST_MATCHED_GATE_DISAGREEMENT"
   else: ust,st,reason="COMPLETE","PASS","MATCHED_GATE_AGREES_WITHIN_UNCERTAINTY"
   evid=[]
   if rel:
    eid=f"APP_EVIDENCE__{s['gate_name']}__{r['requirement_id']}"; evid=[eid]; evs.append(ApparatusGateEvidenceRecord(eid,s["gate_id"],aid,comp,r["requirement_id"],r["scenario"],r["observation_contract_id"],[r["pair_id"]],[m["measurement_record_id"] for m in rel],sorted({x for m in rel for x in (m["left_prediction_id"],m["right_prediction_id"]) if x}),ust,"DISAGREES" if st=="FAIL" else "AGREES" if st=="PASS" else "UNRESOLVED",[f"measurement:{m['measurement_record_id']}" for m in rel]))
   results.append(ApparatusGateResult(f"APP_RESULT__{s['gate_name']}__{r['requirement_id']}",s["gate_id"],aid,comp,r["scenario"],"APPLICABLE" if exposed else "NOT_APPLICABLE_BY_PROTOCOL",st,[r["pair_id"]] if rel else [],[m["measurement_record_id"] for m in rel],ust,reason,[f"requirement:{r['requirement_id']}"],r["requirement_id"],r["observation_contract_id"],sorted({x for m in rel for x in (m["left_prediction_id"],m["right_prediction_id"]) if x}),evid))
 passing=[x.gate_result_id for x in results if x.status=="PASS"]; failing=[x.gate_result_id for x in results if x.status=="FAIL"]; unresolved=[x.gate_result_id for x in results if x.status=="UNRESOLVED"]; na=[x.gate_result_id for x in results if x.status=="NOT_APPLICABLE"]; applicable=[x.gate_result_id for x in results if x.status!="NOT_APPLICABLE"]
 status="RULED_OUT_BY_MATCHED_GATE" if failing else "UNRESOLVED_MISSING_UNCERTAINTY" if any(x.uncertainty_state=="MISSING" for x in results if x.status=="UNRESOLVED") else "UNRESOLVED_UNSUPPORTED_GATE" if unresolved else "SURVIVES_ALL_APPLICABLE_GATES" if applicable else "NOT_APPLICABLE"
 return evs,results,ApparatusEvaluationRecord("APPARATUS_EVALUATION",aids,status,applicable,passing,failing,unresolved,bool(applicable and not failing and not unresolved),sorted({x.scenario for x in results}),"MATCHED_GATE_FAILED" if failing else "ALL_APPLICABLE_GATES_PASS" if status=="SURVIVES_ALL_APPLICABLE_GATES" else "APPLICABLE_GATE_UNRESOLVED",APPARATUS_VERSION,na,[e.gate_evidence_id for e in evs],not any(x.uncertainty_state=="MISSING" for x in results),[z for x in results if x.status=="FAIL" for z in (x.gate_evidence_ids or [])],[z for x in results if x.status=="PASS" for z in (x.gate_evidence_ids or [])])

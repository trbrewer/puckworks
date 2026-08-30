#!/usr/bin/env python3
"""List registered evidence and create/validate scoped data preflights."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "puckworks/data/AVAILABLE_DATA_REGISTER.json"
MANIFEST = ROOT / "puckworks/data/MANIFEST.csv"
ALLOWED = {"EXISTING_DATA_SUFFICIENT_FOR_CURRENT_DECISION", "EXISTING_DATA_PARTIALLY_SUFFICIENT", "SPECIFIC_DATA_GAP_REMAINS", "INDEPENDENT_VALIDATION_DATA_GAP_REMAINS", "EXISTING_DATA_NOT_YET_EXHAUSTED", "NO_RELEVANT_DATA_FOUND_AFTER_REGISTER_CHECK", "NOT_APPLICABLE"}
LAB = {"NONE", "DEFER_EXISTING_DATA_NOT_EXHAUSTED", "REDESIGN_FOR_SPECIFIC_REMAINING_GAP", "PROCEED_TO_BOUNDED_LOCAL_METHOD_QUALIFICATION", "PROCEED_TO_INDEPENDENCE_TIER_AFTER_METHOD_QUALIFICATION", "NOT_APPLICABLE"}

def digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def load_register() -> dict:
    data=json.loads(REGISTER.read_text())
    if data["manifest_sha256"] != digest(MANIFEST): raise ValueError("available-data register is stale")
    return data
def config_path() -> Path: return Path(os.environ.get("XDG_CONFIG_HOME", Path.home()/".config"))/"puckworks/data_sources.json"
def external_status(family: dict) -> str:
    if not family.get("external_corpus_id"): return "PACKAGED_METADATA"
    path=os.environ.get("PUCKWORKS_EXTERNAL_DATA_ROOT")
    if not path and config_path().exists():
        cfg=json.loads(config_path().read_text()); path=cfg.get("sources",{}).get(family["external_corpus_id"],{}).get("path")
    return "AVAILABLE_AND_READABLE" if path and Path(path).is_dir() else "KNOWN_EXTERNAL_CORPUS_NOT_CURRENTLY_MOUNTED"
def matches(f: dict, stage: str|None, observable: str|None) -> bool:
    return (not stage or stage in f["stages"]) and (not observable or observable in f["observables"])
def validate(d: dict, register: dict) -> None:
    required={"schema_version","task_id","scientific_question","decision_to_change","governance_class","model_stage","required_observables","required_independence","puckworks_authority","external_data_check","datasets_reviewed","prior_tasks_reviewed","existing_data_routes_considered","usable_existing_evidence","remaining_scoped_gaps","data_sufficiency_status","data_starvation_scope","home_lab_recommendation","next_action","prepared_by","evidence"}
    missing=sorted(required-set(d));
    if missing: raise ValueError(f"missing required fields: {missing}")
    if d["data_sufficiency_status"] not in ALLOWED: raise ValueError("invalid or unscoped data_sufficiency_status")
    known={x for f in register["families"] for x in f["manifest_dataset_ids"]}
    unknown=sorted(set(d["datasets_reviewed"])-known)
    if unknown: raise ValueError(f"unknown dataset IDs: {unknown}")
    pa=d["puckworks_authority"]
    if not all(pa.get(k) for k in ("commit","tree","manifest_sha256","available_data_register_sha256")): raise ValueError("missing producer authority")
    lab=d["home_lab_recommendation"]
    if lab.get("status") not in LAB: raise ValueError("invalid home-lab status")
    if lab.get("operational_authorization") is not False: raise ValueError("preflight cannot authorize operations")
    if lab["status"] not in {"NONE","NOT_APPLICABLE"}:
        if not d["datasets_reviewed"] or not d["external_data_check"].get("performed") or not lab.get("specific_decision") or not lab.get("why_existing_data_cannot_answer") or not lab.get("minimum_measurement_set") or not lab.get("marginal_information_value") or not d["remaining_scoped_gaps"]: raise ValueError("laboratory recommendation lacks a specific gap and minimum measurement set")

def main() -> None:
    p=argparse.ArgumentParser(); s=p.add_subparsers(dest="cmd",required=True)
    q=s.add_parser("list"); q.add_argument("--stage"); q.add_argument("--observable")
    q=s.add_parser("init"); q.add_argument("--task-id",required=True); q.add_argument("--stage",required=True); q.add_argument("--observable",required=True); q.add_argument("--output",required=True)
    q=s.add_parser("validate"); q.add_argument("path")
    q=s.add_parser("verify-external"); q.add_argument("--family",required=True)
    a=p.parse_args(); r=load_register()
    if a.cmd=="list":
        print(json.dumps([{"family_id":f["family_id"],"datasets":f["manifest_dataset_ids"],"external_status":external_status(f)} for f in r["families"] if matches(f,a.stage,a.observable)],indent=2))
    elif a.cmd=="verify-external":
        f=next((x for x in r["families"] if x.get("external_corpus_id")==a.family or x["family_id"]==a.family),None)
        if not f: raise SystemExit("unknown family")
        print(json.dumps({"family":a.family,"status":external_status(f),"expected_source_manifest_sha256":f.get("external_source_manifest_hash")},indent=2))
    elif a.cmd=="validate":
        validate(json.loads(Path(a.path).read_text()),r); print("VALID")
    else:
        fs=[f for f in r["families"] if matches(f,a.stage,a.observable)]
        d={"schema_version":1,"task_id":a.task_id,"scientific_question":"COMPLETE_ME","decision_to_change":"COMPLETE_ME","governance_class":"G1","model_stage":[a.stage],"required_observables":[a.observable],"required_independence":"COMPLETE_ME","puckworks_authority":{"commit":"COMPLETE_ME","tree":"COMPLETE_ME","manifest_sha256":r["manifest_sha256"],"available_data_register_sha256":digest(REGISTER)},"external_data_check":{"performed":True,"known_corpora":[f["external_corpus_id"] for f in fs if f.get("external_corpus_id")],"mounted_corpora":[],"known_but_unmounted_corpora":[],"source_manifest_hashes":{f["external_corpus_id"]:f["external_source_manifest_hash"] for f in fs if f.get("external_corpus_id")}},"datasets_reviewed":[x for f in fs for x in f["manifest_dataset_ids"]],"prior_tasks_reviewed":[],"existing_data_routes_considered":{k:"COMPLETE_ME" for k in ("direct_observation_comparison","source_reconstruction","source_internal_transfer","normalized_comparison","cross_source_join","adapter_or_observation_operator","parameter_sensitivity","identifiability_or_discrimination","simple_baseline_comparison","bounded_public_data_search")},"usable_existing_evidence":[],"remaining_scoped_gaps":[],"data_sufficiency_status":"EXISTING_DATA_NOT_YET_EXHAUSTED","data_starvation_scope":[],"home_lab_recommendation":{"status":"NONE","specific_decision":"","why_existing_data_cannot_answer":"","minimum_measurement_set":[],"marginal_information_value":"","source_apparatus_evidence_considered":True,"local_method_qualification_required":True,"operational_authorization":False},"next_action":"COMPLETE_ME","prepared_by":"COMPLETE_ME","evidence":[]}
        Path(a.output).write_text(json.dumps(d,indent=2)+"\n")
if __name__=="__main__": main()

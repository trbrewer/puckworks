"""Deterministic SCI-ED-002-R1 method-provenance gates."""
from __future__ import annotations
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs/analysis/sci_ed_002"
R1 = PACK / "r1"
ACCEPTABLE = {"DIRECT_METHOD_REQUIREMENT", "DIRECT_EMPIRICAL_RECOVERY_EVIDENCE", "QUANTITATIVE_DERIVATION_FROM_METHOD_EVIDENCE"}

def validate(mutation=None):
    sources = list(csv.DictReader((R1 / "METHOD_PROVENANCE_AUDIT.csv").open()))
    labs = list(csv.DictReader((R1 / "LABORATORY_IDENTITY_AUDIT.csv").open()))
    rule = json.loads((R1 / "REFERENCE_EXTRACTABILITY_STOPPING_RULE_PROVENANCE.json").read_text())
    if mutation == "unrelated_source": sources[0]["supports_method"] = "false"
    if mutation == "aoac_missing_identity": sources.append({"source_id":"AOAC-X","identity":"","access_date":"2026-08-26","supports_method":"true","supported_claims":"method anchor","unsupported_claims":"","source_class":"AUTHORITATIVE","status":"RETAINED"})
    if mutation == "iso_trigonelline": sources[0]["supported_claims"] += "|trigonelline"
    if mutation == "unsupported_threshold": rule["elements"]["increment_threshold"]["support_class"] = "UNSUPPORTED_DESIGN_CHOICE"
    if mutation == "missing_max_action": rule["elements"]["maximum_cycles"]["action"] = ""
    if mutation == "generic_lab": labs[0]["legal_name"] = "National laboratory"
    if mutation == "three_labs": labs.pop()
    if mutation == "quotation": sources[0]["status"] = "QUOTE_RECEIVED"
    if mutation == "missing_access_date": sources[0]["access_date"] = ""
    for s in sources:
        if not s.get("source_id") or not s.get("identity") or not s.get("access_date"): raise ValueError("SOURCE_IDENTITY_VERSION_ACCESS_DATE_REQUIRED")
        if s["source_id"].startswith("AOAC") and not s["identity"].startswith("AOAC Official Method"): raise ValueError("AOAC_EXACT_APPLICABLE_METHOD_IDENTITY_REQUIRED")
        if s["source_id"] == "ISO20481" and "trigonelline" in s["supported_claims"].lower(): raise ValueError("ISO_20481_CANNOT_SUPPORT_TRIGONELLINE")
        if s.get("supports_method") != "true" and "method anchor" in s.get("supported_claims", ""): raise ValueError("SOURCE_TOPIC_DOES_NOT_SUPPORT_ASSIGNED_METHOD_CLAIM")
        if "QUOTE_RECEIVED" in s.get("status", ""): raise ValueError("COST_ESTIMATE_MUST_NOT_BE_LABELLED_QUOTATION")
    if len(labs) < 4: raise ValueError("FOUR_EXACT_LABORATORY_CANDIDATES_REQUIRED")
    if any(not x["legal_name"] or x["legal_name"].lower() in {"national laboratory", "laboratory candidate"} for x in labs): raise ValueError("GENERIC_UNNAMED_LABORATORY_PROHIBITED")
    if any(x["contact_status"] != "NOT_CONTACTED" for x in labs): raise ValueError("LABORATORY_MUST_REMAIN_NOT_CONTACTED")
    if not rule["elements"]["maximum_cycles"].get("action"): raise ValueError("STOPPING_RULE_MAXIMUM_ACTION_REQUIRED")
    unsupported = [k for k,v in rule["elements"].items() if v.get("critical") and v.get("support_class") not in ACCEPTABLE]
    if unsupported: raise ValueError("STOPPING_RULE_CRITICAL_ELEMENT_UNSUPPORTED:" + ",".join(sorted(unsupported)))
    return {"status":"PASS","laboratories":4}

"""Pure four-way scientific decision derivation for RP-A-001 C1-R1."""
from __future__ import annotations

import hashlib
import json
from .schema import DecisionRecord

RULE_VERSION = "rp-a-001-decision/v1"
APPARATUS = "SCI_MD_003_RP_A_001_APPARATUS_OBSERVATION_EXPLANATION_SURVIVES"
DYNAMIC = "SCI_MD_003_RP_A_001_DYNAMIC_BED_SIGNATURE_DISTINGUISHABLE"
SPATIAL = "SCI_MD_003_RP_A_001_SPATIAL_LOCALIZATION_ONLY_DISTINGUISHABLE_ROUTE"
ADDITIONAL = "SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED"
SPATIAL_CHANNELS = {"spatial_flow_variance", "local_extraction"}
DYNAMIC_CHANNELS = {"bed_height_or_deformation", "bed_state", "deformation"}


def decision_input_hash(*, explanations, pair_eligibility, component_reports,
                        comparison_records, measurement_records, coverage_records,
                        minimum_measurement_sets) -> str:
    payload = {
        "explanations": explanations, "pair_eligibility": pair_eligibility,
        "component_reports": component_reports, "comparison_records": comparison_records,
        "measurement_records": measurement_records, "coverage_records": coverage_records,
        "minimum_measurement_sets": minimum_measurement_sets,
    }
    data = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def derive_scientific_decision(*, explanations, pair_eligibility, component_reports,
                               comparison_records, measurement_records, coverage_records,
                               minimum_measurement_sets) -> DecisionRecord:
    """Apply apparatus → dynamic → spatial → additional-data precedence."""
    eligible = [r for r in pair_eligibility if r["eligibility"] == "eligible"]
    eligible_ids = {r["pair_id"] for r in eligible}
    robust = [r for r in measurement_records if r["robustly_covers_pair"]]
    robust_ids = [r["measurement_record_id"] for r in robust]
    missing = [r["measurement_record_id"] for r in measurement_records
               if r["classification"] == "NOT_ADJUDICATED_MISSING_UNCERTAINTY"]
    unsupported = [r for r in measurement_records if r["classification"] == "UNSUPPORTED"]
    complete = minimum_measurement_sets["result"] != "NO_COMPLETE_MEASUREMENT_SET"
    explanation_by_id = {r["explanation_id"]: r for r in explanations}

    apparatus_ids = {r["explanation_id"] for r in explanations
                     if r["scientific_role"] == "FIXED_BED_MACHINE_AND_APPARATUS_NULL"}
    apparatus_pairs = [p for p in eligible if apparatus_ids & {p["left_explanation"], p["right_explanation"]}]
    apparatus_measurements = [r for r in measurement_records if r["pair_id"] in {p["pair_id"] for p in apparatus_pairs}]
    apparatus_gates = []
    for eid in apparatus_ids:
        cid = explanation_by_id[eid]["component_id"]
        apparatus_gates.extend(component_reports.get(cid, {}).get("decision_gates", []))
    apparatus_ok = bool(apparatus_pairs and apparatus_measurements and apparatus_gates)
    apparatus_ok &= all(g.get("status") == "PASS" for g in apparatus_gates)
    apparatus_ok &= all(r["robustly_covers_pair"] for r in apparatus_measurements)

    dynamic_ids = {r["explanation_id"] for r in explanations if "DYNAMIC_BED" in r["scientific_role"]}
    dynamic_robust = [r for r in robust if r["channel"] in DYNAMIC_CHANNELS and
                      ({r["left_explanation"], r["right_explanation"]} & dynamic_ids)]
    dynamic_covered = {r["pair_id"] for r in dynamic_robust}
    dynamic_routes = {r["channel"] for r in dynamic_robust}
    dynamic_ok = bool(dynamic_ids and eligible_ids and dynamic_covered >= eligible_ids and
                      len(dynamic_routes) == 1 and not apparatus_ok)

    spatial_ids = {r["explanation_id"] for r in explanations if "SPATIAL" in r["scientific_role"]}
    spatial_robust = [r for r in robust if r["channel"] in SPATIAL_CHANNELS and
                      ({r["left_explanation"], r["right_explanation"]} & spatial_ids)]
    spatial_covered = {r["pair_id"] for r in spatial_robust}
    aggregate_covered = {r["pair_id"] for r in robust if r["channel"] not in SPATIAL_CHANNELS}
    spatial_routes = {r["channel"] for r in spatial_robust}
    spatial_ok = bool(spatial_ids and eligible_ids and spatial_covered >= eligible_ids and
                      aggregate_covered < eligible_ids and len(spatial_routes) == 1 and
                      not apparatus_ok and not dynamic_ok)

    if apparatus_ok:
        selected, qualifying = APPARATUS, apparatus_measurements
    elif dynamic_ok:
        selected, qualifying = DYNAMIC, dynamic_robust
    elif spatial_ok:
        selected, qualifying = SPATIAL, spatial_robust
    else:
        selected, qualifying = ADDITIONAL, []

    reasons: dict[str, list[str]] = {}
    if selected != APPARATUS:
        reasons[APPARATUS] = (["NO_MATCHED_APPARATUS_COMPARATOR"] if not apparatus_pairs else
                              ["APPARATUS_GATE_UNSUPPORTED"] if not apparatus_gates else
                              ["APPARATUS_PRIMARY_GATE_FAILED"])
    if selected != DYNAMIC:
        reasons[DYNAMIC] = (["NO_DYNAMIC_BED_EXPLANATION"] if not dynamic_ids else
                            ["NO_SUPPORTED_DEFORMATION_CHANNEL"] if not dynamic_robust else
                            ["DEFORMATION_NOT_UNIQUE"] if len(dynamic_routes) != 1 else
                            ["DEFORMATION_NOT_ROBUST"])
    if selected != SPATIAL:
        reasons[SPATIAL] = (["NO_SPATIAL_EXPLANATION"] if not spatial_ids else
                            ["NO_SUPPORTED_SPATIAL_CHANNEL"] if not spatial_robust else
                            ["SPATIAL_NOT_UNIQUE"] if len(spatial_routes) != 1 else
                            ["SPATIAL_NOT_ROBUST"])
    if selected != ADDITIONAL:
        reasons[ADDITIONAL] = ["HIGHER_PRECEDENCE_OUTCOME_FULLY_QUALIFIED"]

    disqualifying = [r["measurement_record_id"] for r in measurement_records if not r["robustly_covers_pair"]]
    qpair = sorted({r["pair_id"] for r in qualifying})
    qexpl = sorted({x for r in qualifying for x in (r["left_explanation"], r["right_explanation"])})
    qscenario = sorted({r["scenario"] for r in qualifying})
    qchannel = sorted({r["channel"] for r in qualifying})
    if not eligible:
        disqualifying.extend(p["pair_id"] for p in pair_eligibility)
    input_hash = decision_input_hash(
        explanations=explanations, pair_eligibility=pair_eligibility,
        component_reports=component_reports, comparison_records=comparison_records,
        measurement_records=measurement_records, coverage_records=coverage_records,
        minimum_measurement_sets=minimum_measurement_sets)
    return DecisionRecord(
        "PUCKWORKS_COMPONENT_ATLAS_DECISION", selected, RULE_VERSION, input_hash,
        len(eligible), robust_ids, sorted(disqualifying), qpair, qexpl, qscenario,
        qchannel, minimum_measurement_sets["result"], minimum_measurement_sets["zero_pair_status"],
        missing, {"UNSUPPORTED": len(unsupported)}, reasons, "NOT_ESTABLISHED",
        "MODEL_RESPONSE_COMPARISON_ONLY__PHYSICAL_VALIDATION_NOT_ESTABLISHED")

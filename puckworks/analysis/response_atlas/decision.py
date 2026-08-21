"""Pure four-way scientific decision derivation for RP-A-001 C1-R2."""
from __future__ import annotations

import hashlib
import json

from .schema import DecisionRecord

RULE_VERSION = "rp-a-001-decision/v2"
APPARATUS = "SCI_MD_003_RP_A_001_APPARATUS_OBSERVATION_EXPLANATION_SURVIVES"
DYNAMIC = "SCI_MD_003_RP_A_001_DYNAMIC_BED_SIGNATURE_DISTINGUISHABLE"
SPATIAL = "SCI_MD_003_RP_A_001_SPATIAL_LOCALIZATION_ONLY_DISTINGUISHABLE_ROUTE"
ADDITIONAL = "SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED"
SPATIAL_CHANNELS = {"spatial_flow_variance", "local_extraction"}
DYNAMIC_CHANNELS = {"bed_height_or_deformation", "bed_state", "deformation"}


def decision_input_hash(**inputs) -> str:
    data = json.dumps(inputs, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return hashlib.sha256(data).hexdigest()


def derive_scientific_decision(*, explanations, requirements, pair_eligibility,
                               component_reports, comparison_records, measurement_records,
                               coverage_edges, minimum_measurement_sets,
                               apparatus_gate_specs, apparatus_gate_results,
                               apparatus_evaluation) -> DecisionRecord:
    """Apply apparatus survival -> ruled-out dynamic -> ruled-out spatial -> additional."""
    relevant = [r for r in requirements if r["relevant_to_final_decision"]]
    robust = [r for r in measurement_records if r["classification"] == "ROBUSTLY_DISCRIMINATING"]
    robust_ids = sorted(r["measurement_record_id"] for r in robust)
    missing = sorted(r["measurement_record_id"] for r in measurement_records
                     if r["classification"] == "NOT_ADJUDICATED_MISSING_UNCERTAINTY")
    unsupported = [r for r in measurement_records if r["classification"] == "UNSUPPORTED"]
    complete = bool(minimum_measurement_sets["complete"])
    apparatus_status = apparatus_evaluation["status"]
    apparatus_complete = apparatus_evaluation["apparatus_gate_coverage_complete"]

    apparatus_ok = apparatus_status == "SURVIVES_ALL_APPLICABLE_GATES" and apparatus_complete
    apparatus_ruled_out = apparatus_status == "RULED_OUT_BY_MATCHED_GATE"
    dynamic_ids = {r["explanation_id"] for r in explanations if "DYNAMIC_BED" in r["scientific_role"]}
    spatial_ids = {r["explanation_id"] for r in explanations if "SPATIAL" in r["scientific_role"]}
    dynamic_records = [r for r in robust if r["channel"] in DYNAMIC_CHANNELS and
                       ({r["left_explanation"], r["right_explanation"]} & dynamic_ids)]
    spatial_records = [r for r in robust if r["channel"] in SPATIAL_CHANNELS and
                       ({r["left_explanation"], r["right_explanation"]} & spatial_ids)]
    dynamic_options = {r["measurement_option_id"] for r in dynamic_records}
    spatial_options = {r["measurement_option_id"] for r in spatial_records}
    minsets = minimum_measurement_sets["all_equally_minimal_sets"]
    every_set_spatial = bool(minsets and all(set(s) & spatial_options for s in minsets))
    nonspatial_complete = any(not (set(s) & spatial_options) for s in minsets)
    every_set_dynamic = bool(minsets and all(set(s) & dynamic_options for s in minsets))
    nondynamic_complete = any(not (set(s) & dynamic_options) for s in minsets)
    dynamic_ok = bool(apparatus_ruled_out and dynamic_ids and complete and dynamic_records and
                      len(dynamic_options) == 1 and every_set_dynamic and not nondynamic_complete)
    spatial_ok = bool(apparatus_ruled_out and spatial_ids and complete and spatial_records and
                      every_set_spatial and not nonspatial_complete and len(spatial_options) == 1)

    if apparatus_ok:
        selected, qualifying = APPARATUS, []
    elif dynamic_ok:
        selected, qualifying = DYNAMIC, dynamic_records
    elif spatial_ok:
        selected, qualifying = SPATIAL, spatial_records
    else:
        selected, qualifying = ADDITIONAL, []

    reasons: dict[str, list[str]] = {}
    if selected != APPARATUS:
        reasons[APPARATUS] = (["NO_MATCHED_APPARATUS_COMPARATOR"] if apparatus_status == "NOT_EVALUATED" else
                              ["APPARATUS_PRIMARY_GATE_FAILED"] if apparatus_ruled_out else
                              ["APPARATUS_GATE_UNSUPPORTED"])
    if selected != DYNAMIC:
        reasons[DYNAMIC] = (["APPARATUS_NOT_RULED_OUT"] if not apparatus_ruled_out else
                            ["NO_DYNAMIC_BED_EXPLANATION"] if not dynamic_ids else
                            ["NO_COMPLETE_MEASUREMENT_SET"] if not complete else
                            ["DEFORMATION_NOT_UNIQUE"] if len(dynamic_options) != 1 else
                            ["NO_SUPPORTED_DEFORMATION_CHANNEL"])
    if selected != SPATIAL:
        reasons[SPATIAL] = (["APPARATUS_NOT_RULED_OUT"] if not apparatus_ruled_out else
                            ["NO_SPATIAL_EXPLANATION"] if not spatial_ids else
                            ["NO_COMPLETE_MEASUREMENT_SET"] if not complete else
                            ["SPATIAL_NOT_UNIQUE"] if len(spatial_options) != 1 else
                            ["NO_SUPPORTED_SPATIAL_CHANNEL"])
    if selected != ADDITIONAL:
        reasons[ADDITIONAL] = ["HIGHER_PRECEDENCE_OUTCOME_FULLY_QUALIFIED"]

    q_measurements = {r["measurement_record_id"] for r in qualifying}
    inputs = dict(explanations=explanations, requirements=requirements,
                  pair_eligibility=pair_eligibility, component_reports=component_reports,
                  comparison_records=comparison_records, measurement_records=measurement_records,
                  coverage_edges=coverage_edges, minimum_measurement_sets=minimum_measurement_sets,
                  apparatus_gate_specs=apparatus_gate_specs,
                  apparatus_gate_results=apparatus_gate_results,
                  apparatus_evaluation=apparatus_evaluation)
    return DecisionRecord(
        "PUCKWORKS_COMPONENT_ATLAS_DECISION", selected, RULE_VERSION,
        decision_input_hash(**inputs), len(relevant), robust_ids,
        sorted(r["measurement_record_id"] for r in measurement_records
               if r["classification"] != "ROBUSTLY_DISCRIMINATING"),
        sorted({r["pair_id"] for r in qualifying}),
        sorted({x for r in qualifying for x in (r["left_explanation"], r["right_explanation"])}),
        sorted({r["scenario"] for r in qualifying}), sorted({r["channel"] for r in qualifying}),
        minimum_measurement_sets["result"], minimum_measurement_sets["zero_universe_status"],
        missing, {"UNSUPPORTED": len(unsupported)}, reasons, "NOT_ESTABLISHED",
        "MODEL_RESPONSE_COMPARISON_ONLY__PHYSICAL_VALIDATION_NOT_ESTABLISHED",
        apparatus_status, apparatus_complete, complete,
        sorted({r["requirement_id"] for r in qualifying}),
        sorted(e["coverage_edge_id"] for e in coverage_edges if e["measurement_record_id"] in q_measurements),
        minimum_measurement_sets["minimum_set_ids"],
        (apparatus_evaluation["applicable_gate_result_ids"] if selected == APPARATUS else
         apparatus_evaluation["failing_gate_result_ids"] if selected in {DYNAMIC, SPATIAL} else []),
        minimum_measurement_sets["uncovered_requirement_ids"])

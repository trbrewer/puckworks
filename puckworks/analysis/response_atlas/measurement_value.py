from .schema import MeasurementValueRecord, PredictionIntervalRecord


def discriminate(left_interval, right_interval, measurement_uncertainty):
    if left_interval is None or right_interval is None:
        return "UNSUPPORTED"
    if measurement_uncertainty == "NOT_PROVIDED":
        return "NOT_ADJUDICATED_MISSING_UNCERTAINTY"
    u = float(measurement_uncertainty)
    left = (left_interval[0] - u, left_interval[1] + u)
    right = (right_interval[0] - u, right_interval[1] + u)
    separated = left[1] < right[0] or right[1] < left[0]
    if separated:
        return "ROBUSTLY_DISCRIMINATING"
    nominal_separated = left_interval[1] < right_interval[0] or right_interval[1] < left_interval[0]
    return ("NOMINALLY_DISCRIMINATING_BUT_UNCERTAINTY_OVERLAPS" if nominal_separated
            else "NOT_DISCRIMINATING")


def build_measurement_record(*, pair, channel, left_support, right_support,
                             left: PredictionIntervalRecord | None,
                             right: PredictionIntervalRecord | None,
                             measurement_uncertainty, uncertainty_provenance):
    left_interval = None if left is None else (left.lower_bound, left.upper_bound)
    right_interval = None if right is None else (right.lower_bound, right.upper_bound)
    classification = discriminate(left_interval, right_interval, measurement_uncertainty)
    if (classification != "UNSUPPORTED" and
            ((left and left.missing_uncertainty_flags) or (right and right.missing_uncertainty_flags))):
        classification = "NOT_ADJUDICATED_MISSING_UNCERTAINTY"
    if classification == "UNSUPPORTED":
        reason = "RESPONSE_OR_RELATIONSHIP_UNSUPPORTED"
    elif classification == "NOT_ADJUDICATED_MISSING_UNCERTAINTY":
        reason = "MEASUREMENT_OR_MODEL_UNCERTAINTY_NOT_PROVIDED"
    elif classification == "ROBUSTLY_DISCRIMINATING":
        reason = "CONSERVATIVE_EXPANDED_INTERVALS_DISJOINT"
    elif classification == "NOMINALLY_DISCRIMINATING_BUT_UNCERTAINTY_OVERLAPS":
        reason = "NOMINAL_INTERVALS_DISJOINT_EXPANDED_INTERVALS_OVERLAP"
    else:
        reason = "PREDICTION_INTERVALS_OVERLAP"
    expanded_left = expanded_right = None
    if left_interval is not None and right_interval is not None and measurement_uncertainty != "NOT_PROVIDED":
        u = float(measurement_uncertainty)
        expanded_left = [left_interval[0] - u, left_interval[1] + u]
        expanded_right = [right_interval[0] - u, right_interval[1] + u]
    option_id = f"MEASOPT__{channel}__{pair.observation_contract_hash}"
    return MeasurementValueRecord(
        measurement_record_id=f"MV__{pair.requirement_id}__{channel}__{pair.adapter_id}__{pair.adapter_version}", pair_id=pair.pair_id,
        left_explanation=pair.left_explanation, right_explanation=pair.right_explanation,
        scenario=pair.scenario, channel=channel, comparability_level=pair.comparability_level,
        left_support_state=left_support, right_support_state=right_support,
        left_prediction_id=None if left is None else left.prediction_id,
        right_prediction_id=None if right is None else right.prediction_id,
        declared_measurement_uncertainty=measurement_uncertainty,
        measurement_uncertainty_provenance=uncertainty_provenance,
        expanded_left_interval=expanded_left, expanded_right_interval=expanded_right,
        interval_combination_method="CONSERVATIVE_ADDITIVE_BOUNDED_HALF_WIDTHS_NO_DISTRIBUTION",
        classification=classification, reason_code=reason,
        evidence_label="MODEL_RESPONSE_MEASUREMENT_VALUE_NOT_VALIDATION",
        robustly_covers_pair=classification == "ROBUSTLY_DISCRIMINATING",
        claim_ceiling="MODEL_INFORMED_MEASUREMENT_DESIGN_ONLY",
        eligibility_id=pair.eligibility_id, requirement_id=pair.requirement_id,
        measurement_option_id=option_id, adapter_id=pair.adapter_id,
        adapter_version=pair.adapter_version, adapter_contract_hash=pair.adapter_contract_hash,
        intervention_id=pair.intervention_id, basis_id=pair.basis_id,
        evidence_references=[pair.eligibility_id],
        observation_contract_id=pair.observation_contract_id,
        observation_contract_hash=pair.observation_contract_hash)

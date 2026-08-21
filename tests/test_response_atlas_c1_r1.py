import copy

import pytest

from puckworks.analysis.response_atlas import runner
from puckworks.analysis.response_atlas.decision import (
    ADDITIONAL, APPARATUS, DYNAMIC, SPATIAL, derive_scientific_decision,
)
from puckworks.analysis.response_atlas.schema import ComparisonEligibilityRecord


def explanation(identity, role, component=None):
    return {"explanation_id": identity, "scientific_role": role,
            "component_id": component or identity}


def pair(identity="p", left="a", right="b", channel="flow", scenario="s",
         eligibility="eligible", level=1, adapter="NONE"):
    return {"pair_id": identity, "left_explanation": left, "right_explanation": right,
            "scientific_question": "q", "scenario": scenario,
            "candidate_observable": channel, "common_intervention": "matched",
            "common_output_basis": "matched", "comparability_level": level,
            "pair_role": "SCIENTIFICALLY_COMPETING", "eligibility": eligibility,
            "reason_code": "TEST", "adapter_id": adapter,
            "adapter_version": "NONE" if adapter == "NONE" else "1",
            "uncertainty_available": True,
            "eligibility_id": f"ELIG__{identity}__{scenario}__{channel}"}


def measurement(identity="m", pair_id="p", left="a", right="b", channel="flow",
                scenario="s", classification="ROBUSTLY_DISCRIMINATING"):
    return {"measurement_record_id": identity, "pair_id": pair_id,
            "left_explanation": left, "right_explanation": right, "scenario": scenario,
            "channel": channel, "classification": classification,
            "robustly_covers_pair": classification == "ROBUSTLY_DISCRIMINATING"}


def decide(explanations=None, pairs=None, measurements=None, reports=None, complete=False):
    pairs = pairs or []
    measurements = measurements or []
    minimum = {"eligible_pair_ids": [p["pair_id"] for p in pairs if p["eligibility"] == "eligible"],
               "zero_pair_status": "ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM_PRESENT" if any(p["eligibility"] == "eligible" for p in pairs) else "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM",
               "result": [["flow"]] if complete else "NO_COMPLETE_MEASUREMENT_SET"}
    return derive_scientific_decision(
        explanations=explanations or [], pair_eligibility=pairs,
        component_reports=reports or {}, comparison_records=pairs,
        measurement_records=measurements,
        coverage_records=[{"channel": "flow", "robust_measurement_record_ids": [m["measurement_record_id"] for m in measurements if m["robustly_covers_pair"]]}],
        minimum_measurement_sets=minimum)


@pytest.mark.parametrize("classification", [
    "UNSUPPORTED", "NOT_ADJUDICATED_MISSING_UNCERTAINTY", "NOT_DISCRIMINATING",
    "NOMINALLY_DISCRIMINATING_BUT_UNCERTAINTY_OVERLAPS",
])
def test_incomplete_measurement_paths_require_additional_data(classification):
    assert decide(pairs=[pair()], measurements=[measurement(classification=classification)]).selected_outcome == ADDITIONAL


def test_zero_pair_path_is_derived():
    result = decide()
    assert result.selected_outcome == ADDITIONAL
    assert "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM" in result.nonselection_reasons[APPARATUS] or result.zero_pair_status == "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM"


def test_apparatus_path_and_evidence():
    ex = [explanation("null", "FIXED_BED_MACHINE_AND_APPARATUS_NULL", "machine"), explanation("other", "DYNAMIC_BED_EXPLANATION")]
    p = pair(left="null", right="other")
    m = measurement(left="null", right="other")
    result = decide(ex, [p], [m], {"machine": {"decision_gates": [{"gate": "sign", "status": "PASS"}]}}, True)
    assert result.selected_outcome == APPARATUS
    assert result.qualifying_comparison_record_ids == ["p"] and result.robust_measurement_record_ids == ["m"]


def test_apparatus_unsupported_gate_fails():
    ex = [explanation("null", "FIXED_BED_MACHINE_AND_APPARATUS_NULL", "machine"), explanation("other", "OTHER")]
    result = decide(ex, [pair(left="null", right="other")], [measurement(left="null", right="other")],
                    {"machine": {"decision_gates": [{"gate": "timing", "status": "UNSUPPORTED"}]}}, True)
    assert result.selected_outcome == ADDITIONAL


def test_unique_dynamic_path():
    ex = [explanation("a", "DYNAMIC_BED_EXPLANATION"), explanation("b", "OTHER")]
    assert decide(ex, [pair(channel="bed_height_or_deformation")],
                  [measurement(channel="bed_height_or_deformation")], complete=True).selected_outcome == DYNAMIC


def test_dynamic_incomplete_or_nonunique_fails():
    ex = [explanation("a", "DYNAMIC_BED_EXPLANATION"), explanation("b", "OTHER")]
    pairs = [pair("p1", channel="bed_height_or_deformation"), pair("p2", channel="flow")]
    records = [measurement("m1", "p1", channel="bed_height_or_deformation")]
    assert decide(ex, pairs, records).selected_outcome == ADDITIONAL
    records += [measurement("m2", "p2", channel="deformation")]
    assert decide(ex, pairs, records, complete=True).selected_outcome == ADDITIONAL


def test_unique_spatial_only_path_and_aggregate_exclusion():
    ex = [explanation("a", "SPATIAL_LOCALIZATION_EXPLANATION"), explanation("b", "OTHER")]
    p = pair(channel="spatial_flow_variance")
    spatial = measurement(channel="spatial_flow_variance")
    assert decide(ex, [p], [spatial], complete=True).selected_outcome == SPATIAL
    aggregate = measurement("aggregate", channel="flow")
    assert decide(ex, [p], [spatial, aggregate], complete=True).selected_outcome == ADDITIONAL


def test_decision_input_mutation_crosses_boundary():
    ex = [explanation("a", "DYNAMIC_BED_EXPLANATION"), explanation("b", "OTHER")]
    p = pair(channel="bed_height_or_deformation")
    robust = measurement(channel="bed_height_or_deformation")
    assert decide(ex, [p], [robust], complete=True).selected_outcome == DYNAMIC
    robust["classification"] = "NOT_DISCRIMINATING"; robust["robustly_covers_pair"] = False
    assert decide(ex, [p], [robust]).selected_outcome == ADDITIONAL


def test_real_bundle_decision_override_and_bad_reference_fail():
    bundle = runner.build_bundle()
    altered = copy.deepcopy(bundle); altered["decision"]["selected_outcome"] = DYNAMIC
    with pytest.raises(ValueError, match="inconsistent"): runner.validate_bundle(altered)
    altered = copy.deepcopy(bundle); altered["decision"]["robust_measurement_record_ids"] = ["missing"]
    with pytest.raises(ValueError, match="inconsistent|nonexistent"): runner.validate_bundle(altered)


def test_channel_specific_generation_and_isolation():
    bundle = runner.build_bundle()
    assert all(r["eligibility_id"].endswith("__" + r["candidate_observable"]) for r in bundle["pair_eligibility"])
    assert all(r["eligibility_id"] in {e["eligibility_id"] for e in bundle["pair_eligibility"]} for r in bundle["measurement_value_records"])
    with pytest.raises(ValueError):
        ComparisonEligibilityRecord("p", "a", "b", "q", "s", "flow", "same", "m/s", 1,
                                    "SCIENTIFICALLY_COMPETING", "eligible", "TEST", "NONE", "NONE", True,
                                    "ELIG__p__other__flow")


def test_flow_eligibility_generates_only_flow(monkeypatch):
    p = ComparisonEligibilityRecord("p", "a", "b", "q", "s", "flow", "same", "m/s", 1,
                                    "SCIENTIFICALLY_COMPETING", "eligible", "TEST", "NONE", "NONE", True,
                                    "ELIG__p__s__flow")
    explanations = [
        runner.ExplanationRecord("a", "ca", "OTHER", "flow", "q", "p", "c", "r", [], "x", "BED_PRESSURE_DROP", "DIFFERENTIAL", "x", ["flow"], "x", "COMPETING_EXPLANATION", "x"),
        runner.ExplanationRecord("b", "cb", "OTHER", "flow", "q", "p", "c", "r", [], "x", "BED_PRESSURE_DROP", "DIFFERENTIAL", "x", ["flow"], "x", "COMPETING_EXPLANATION", "x")]
    cells = [runner.ResultCell("ca", "s", "darcy_velocity", "SUPPORTED", "m/s", 1, evidence_domain_status="x"), runner.ResultCell("cb", "s", "darcy_velocity", "SUPPORTED", "m/s", 2, evidence_domain_status="x")]
    assumptions = {"channels": [{"channel": c, "assumption_class": "TEST", "measurement_uncertainty": .1} for c in runner.CHANNELS]}
    _, records = runner._derive_measurements([p], cells, assumptions, explanations)
    assert [r.channel for r in records] == ["flow"]
    assert not any(r.channel in {"bed_height_or_deformation", "first_drip_timing", "spatial_flow_variance"} for r in records)


def test_runner_calls_decision_function(monkeypatch):
    called = []
    original = runner.derive_scientific_decision
    def observed(**kwargs):
        called.append(kwargs); return original(**kwargs)
    monkeypatch.setattr(runner, "derive_scientific_decision", observed)
    runner.build_bundle()
    assert called

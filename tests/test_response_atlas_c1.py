import json
import shutil

import pytest

from puckworks.analysis.response_atlas import runner
from puckworks.analysis.response_atlas.compare import minimal_sets
from puckworks.analysis.response_atlas.measurement_value import build_measurement_record
from puckworks.analysis.response_atlas.schema import (
    ComparisonEligibilityRecord, DecisionRecord, ExplanationRecord,
    MeasurementValueRecord, PredictionIntervalRecord, ResidualRecord, ResultCell,
    validate_level_one)


def test_zero_pair_semantics_are_non_vacuous():
    assert minimal_sets(set(), {"flow": set()}) == "NO_COMPLETE_MEASUREMENT_SET"
    with pytest.raises(ValueError):
        DecisionRecord("d", "SCI_MD_003_RP_A_001_ADDITIONAL_DATA_REQUIRED", "v", "bad", 0,
                       [], [], [], [], [], [], [],
                       "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM", [], {}, {},
                       "NOT_ESTABLISHED", "test")


def test_pressure_node_mismatch_rejected_as_level_one():
    left = ResultCell("a", "c", "pressure", "SUPPORTED", "Pa", 1.0,
                      pressure_node="BED_INLET", pressure_reference="GAUGE")
    right = ResultCell("b", "c", "pressure", "SUPPORTED", "Pa", 1.0,
                       pressure_node="PUMP_OUTLET", pressure_reference="GAUGE")
    with pytest.raises(ValueError):
        validate_level_one(left, right)


def test_first_drip_requires_time_contract():
    with pytest.raises(ValueError):
        ResultCell("foster", "case", "first_drip_timing", "SUPPORTED", "s", 6.0)


def test_real_runner_is_response_derived_and_nonaggregate(monkeypatch):
    called = []
    original = runner.minimum_measurement_sets

    def observed(requirements, coverage):
        called.append((requirements, coverage))
        return original(requirements, coverage)

    monkeypatch.setattr(runner, "minimum_measurement_sets", observed)
    bundle = runner.build_bundle()
    assert called
    assert bundle["summary_counts"]["eligible_pairs"] == 0
    assert bundle["minimum_measurement_sets"]["zero_universe_status"] == "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM"
    assert bundle["minimum_measurement_sets"]["result"] == "NO_COMPLETE_MEASUREMENT_SET"
    assert all(r.get("pair_id") != "ALL_REMAINING_EXPLANATIONS" for r in bundle["measurement_value_records"])
    assert bundle["decision"]["zero_pair_status"] == "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM"


def test_real_measurement_path_calls_discrimination(monkeypatch):
    pair = ComparisonEligibilityRecord("pair", "left", "right", "q", "case", "flow",
                                       "same", "m/s", 1, "SCIENTIFICALLY_COMPETING",
                                       "eligible", "TEST", "DIRECT_NATIVE", "1.0.0", True,
                                           "ELIG__REQ__pair__case__same__basis__flow__DIRECT_NATIVE__1.0.0",
                                           "REQ__pair__case__same__basis", "same", "basis", "SUPPORTED", "hash",
                                           "Q_TEST", "OBS_TEST", "a" * 64)
    explanations = [
        ExplanationRecord("left", "a", "test", "flow", "q", "a", "card", "registry", [], "p", "BED_PRESSURE_DROP", "DIFFERENTIAL", "test", ["flow"], "test", "COMPETING_EXPLANATION", "test"),
        ExplanationRecord("right", "b", "test", "flow", "q", "b", "card", "registry", [], "p", "BED_PRESSURE_DROP", "DIFFERENTIAL", "test", ["flow"], "test", "COMPETING_EXPLANATION", "test")]
    cells = [
        ResultCell("a", "case", "darcy_velocity", "SUPPORTED", "m/s", 1.0,
                   reference_basis="superficial", evidence_domain_status="test"),
        ResultCell("b", "case", "darcy_velocity", "SUPPORTED", "m/s", 2.0,
                   reference_basis="superficial", evidence_domain_status="test")]
    assumptions = {"channels": [{"channel": channel, "assumption_class": "REPOSITORY_DECLARED",
                                  "measurement_uncertainty": 0.1} for channel in runner.CHANNELS]}
    calls = []
    import puckworks.analysis.response_atlas.measurement_value as mv
    original = mv.discriminate

    def observed(*args):
        calls.append(args)
        return original(*args)

    monkeypatch.setattr(mv, "discriminate", observed)
    predictions, records = runner._derive_measurements([pair], cells, assumptions, explanations)
    assert calls and len(records) == 1
    assert predictions
    assert next(r for r in records if r.channel == "flow").classification == "NOT_ADJUDICATED_MISSING_UNCERTAINTY"
    assert records[0].channel == "flow"


def test_interval_classifications_and_robust_uncertainty_invariant():
    pair = ComparisonEligibilityRecord("p", "l", "r", "q", "s", "flow", "same", "m/s", 1,
                                       "SCIENTIFICALLY_COMPETING", "eligible", "TEST", "DIRECT_NATIVE", "1.0.0", True,
                                           "ELIG__REQ__p__s__same__basis__flow__DIRECT_NATIVE__1.0.0",
                                           "REQ__p__s__same__basis", "same", "basis", "SUPPORTED", "hash",
                                           "Q_TEST", "OBS_TEST", "a" * 64)
    def pred(identity, value, missing=None):
        return PredictionIntervalRecord(identity, identity, "s", "flow", "q", "m/s",
                                        "NOT_APPLICABLE", "NOT_APPLICABLE", "NOT_APPLICABLE",
                                        value, value, value, 0.0, 0.0, 0.0, 0.0, "test", "test", missing or [])
    robust = build_measurement_record(pair=pair, channel="flow", left_support="SUPPORTED",
                                      right_support="SUPPORTED", left=pred("l", 0), right=pred("r", 2),
                                      measurement_uncertainty=.1, uncertainty_provenance="TEST")
    assert robust.classification == "ROBUSTLY_DISCRIMINATING" and robust.robustly_covers_pair
    nominal = build_measurement_record(pair=pair, channel="flow", left_support="SUPPORTED",
                                       right_support="SUPPORTED", left=pred("l", 0), right=pred("r", .15),
                                       measurement_uncertainty=.1, uncertainty_provenance="TEST")
    assert nominal.classification == "NOMINALLY_DISCRIMINATING_BUT_UNCERTAINTY_OVERLAPS"
    missing = build_measurement_record(pair=pair, channel="flow", left_support="SUPPORTED",
                                       right_support="SUPPORTED", left=pred("l", 0, ["missing"]), right=pred("r", 2),
                                       measurement_uncertainty=.1, uncertainty_provenance="TEST")
    assert missing.classification == "NOT_ADJUDICATED_MISSING_UNCERTAINTY"
    with pytest.raises(ValueError):
        MeasurementValueRecord(**{**robust.to_dict(), "declared_measurement_uncertainty": "NOT_PROVIDED"})


def test_residual_invariants():
    with pytest.raises(ValueError):
        ResidualRecord("x", "a", "b", "q", "m/s", 4, False, 1.0, "none", "semantic", None, None,
                       "NONADDITIVE_ATTRIBUTION", False, None, "test")
    with pytest.raises(ValueError):
        ResidualRecord("x", "a", "b", "q", "m/s", 1, False, None, "none", "semantic", None, None,
                       "NONADDITIVE_ATTRIBUTION", False, .5, "test")


def test_wadsworth_domain_and_grind_are_explicit():
    bundle = runner.build_bundle()
    report = bundle["component_reports"]["wadsworth2026.inertial"]
    assert report["primary_pressure_cases"].startswith("UNSUPPORTED_FOR_CASE")
    assert report["adjudicative_support"] == "EXCLUDED"
    assert "FIXED_POROSITY_RADIUS" in report["grind_direction"]
    wads = [r for r in bundle["quantity_inventory"] if r["component_id"] == "wadsworth2026.inertial"]
    assert wads and all(r["evidence_domain_status"] == "TAMPED_COFFEE_EXTRAPOLATION" for r in wads)


@pytest.fixture
def generated(tmp_path, monkeypatch):
    out = tmp_path / "c1"
    out.mkdir()
    shutil.copy(runner.OUT / "correction_protocol.json", out / "correction_protocol.json")
    monkeypatch.setattr(runner, "OUT", out)
    runner.generate_bundle(execution_commit="1" * 40, execution_tree="2" * 40)
    assert runner.verify_bundle()
    return out


@pytest.mark.parametrize("path,value", [
    (("run_manifest", "execution_code_commit"), "3" * 40),
    (("run_manifest", "execution_code_tree"), "4" * 40),
    (("run_manifest", "protocol_sha256"), "bad"),
    (("run_manifest", "case_matrix_sha256"), "bad"),
    (("run_manifest", "measurement_assumption_sha256"), "bad"),
    (("run_manifest", "registry_snapshot_sha256"), "bad"),
    (("run_manifest", "selected_card_sha256"), {"bad": "bad"}),
    (("run_manifest", "adapter_versions"), {"bad": "0"}),
    (("run_manifest", "environment"), {"python": "bad"}),
    (("run_manifest", "evaluation_count"), 999),
    (("result_cells", 0, "value"), 999.0),
    (("channel_eligibility", 0, "comparability_level"), 5),
    (("channel_eligibility", 0, "candidate_observable"), "temperature"),
    (("channel_eligibility", 0, "scenario"), "OTHER_SCENARIO"),
    (("channel_eligibility", 0, "adapter_version"), "9"),
    (("apparatus_evaluation", "status"), "RULED_OUT_BY_MATCHED_GATE"),
    (("decision", "selected_outcome"), "SCI_MD_003_RP_A_001_DYNAMIC_BED_SIGNATURE_DISTINGUISHABLE"),
    (("decision", "decision_rule_version"), "bad"),
    (("decision", "decision_input_hash"), "0" * 64),
    (("decision", "nonselection_reasons"), {}),
    (("schema_version",), "puckworks.response-atlas-export/v2")])
def test_verifier_detects_protected_payload_mutations(generated, path, value):
    export = generated / "atlas_export.json"
    data = json.loads(export.read_text())
    target = data
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    export.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    with pytest.raises(ValueError):
        runner.verify_bundle()


def test_verifier_detects_hash_mutation(generated):
    (generated / "atlas_export.sha256").write_text("0" * 64 + "  atlas_export.json\n")
    with pytest.raises(ValueError):
        runner.verify_bundle()


def test_superseded_v1_export_rejected_by_c1_validator():
    old = json.loads((runner.BASE / "atlas_export.json").read_text())
    assert old["schema_version"] == "puckworks.response-atlas-export/v1"
    with pytest.raises((KeyError, ValueError)):
        runner.validate_bundle(old)


def test_superseded_v2_export_rejected_by_current_validator():
    old = json.loads((runner.INPUT / "atlas_export.json").read_text())
    assert old["schema_version"] == "puckworks.response-atlas-export/v2"
    with pytest.raises(ValueError, match="schema"):
        runner.validate_bundle(old)

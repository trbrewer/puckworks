"""C1-R5 complete-universe regressions for REVIEW-C1R4-001."""
import copy

import pytest

from puckworks.analysis.response_atlas import governance, runner
from puckworks.analysis.response_atlas.governance import (
    canonical_apparatus_gate_specs,
    evaluate_apparatus,
)
from puckworks.analysis.response_atlas.independent_verifier import reconstruct_apparatus
from puckworks.analysis.response_atlas.schema import PredictionIntervalRecord
from tests.test_response_atlas_c1_r4 import _hash, closed_fixture


def calls(fixture):
    explanations, requirement, measurement, comparisons, predictions, contracts = fixture
    specs = [item.to_dict() for item in canonical_apparatus_gate_specs()]
    arguments = (
        explanations,
        [requirement],
        [measurement],
        specs,
        comparisons,
        predictions,
        contracts,
    )
    authority = copy.deepcopy(contracts)
    return (
        lambda: evaluate_apparatus(
            *arguments, authoritative_contracts=copy.deepcopy(authority)
        ),
        lambda: reconstruct_apparatus(
            *arguments, authoritative_contracts=copy.deepcopy(authority)
        ),
    )


def assert_both_reject(fixture, match):
    for implementation in calls(fixture):
        with pytest.raises(ValueError, match=match):
            implementation()


def test_review_c1r4_001_g1_dangling_comparison_rejected_before_not_evaluated():
    bundle = runner.build_bundle()
    dangling = copy.deepcopy(closed_fixture()[3][0])
    changed = copy.deepcopy(bundle)
    changed["matched_comparisons"] = [dangling]
    with pytest.raises(ValueError, match="DANGLING_REFERENCE|EXTRANEOUS_MATERIAL_RECORD"):
        runner.validate_bundle(changed)
    specs = bundle["apparatus_gate_specs"]
    arguments = (
        bundle["explanations"], bundle["discrimination_requirements"], [], specs,
        [dangling], [], bundle["observation_contracts"],
    )
    for implementation in (evaluate_apparatus, reconstruct_apparatus):
        with pytest.raises(ValueError, match="DANGLING_REFERENCE"):
            implementation(
                *arguments,
                authoritative_contracts=copy.deepcopy(bundle["observation_contracts"]),
            )


def test_review_c1r4_001_g2_orphan_cross_case_prediction_rejected_beside_pass():
    fixture = list(closed_fixture("pass"))
    orphan = copy.deepcopy(fixture[4][0])
    orphan["case_id"] = "UNAUTHORIZED_CASE"
    orphan["prediction_id"] = "PRED__null__UNAUTHORIZED_CASE__flow"
    PredictionIntervalRecord.from_dict(orphan)
    fixture[4].append(orphan)
    assert_both_reject(tuple(fixture), "ORPHAN_RECORD")


def test_review_c1r4_001_g3_self_consistent_provenance_rejected_beside_pass():
    fixture = list(closed_fixture("pass"))
    authority = copy.deepcopy(fixture[5])
    contract = fixture[5][0]
    old_id = contract["observation_contract_id"]
    contract["provenance"] = "CALLER_MUTATED_BUT_SELF_CONSISTENT"
    body = {key: value for key, value in contract.items()
            if key not in {"observation_contract_id", "contract_sha256"}}
    new_hash = _hash(body)
    new_id = old_id.rsplit("__", 1)[0] + "__" + new_hash[:16]
    contract["contract_sha256"] = new_hash
    contract["observation_contract_id"] = new_id
    fixture[1]["observation_contract_id"] = new_id
    fixture[2]["observation_contract_id"] = new_id
    fixture[2]["observation_contract_hash"] = new_hash
    fixture[2]["measurement_option_id"] = f"MEASOPT__flow__{new_hash}"
    fixture[3][0]["observation_contract_id"] = new_id
    fixture[3][0]["observation_contract_hash"] = new_hash
    explanations, requirement, measurement, comparisons, predictions, contracts = fixture
    specs = [item.to_dict() for item in canonical_apparatus_gate_specs()]
    for implementation in (evaluate_apparatus, reconstruct_apparatus):
        with pytest.raises(ValueError, match="AUTHORITATIVE_PROVENANCE_MISMATCH"):
            implementation(
                explanations, [requirement], [measurement], specs,
                comparisons, predictions, contracts,
                authoritative_contracts=copy.deepcopy(authority),
            )


def test_same_case_unauthorized_observable_prediction_is_rejected():
    fixture = list(closed_fixture("pass"))
    orphan = copy.deepcopy(fixture[4][0])
    orphan["channel"] = "unauthorized_observable"
    orphan["prediction_id"] = "PRED__null__MACHINE_REF__unauthorized_observable"
    PredictionIntervalRecord.from_dict(orphan)
    fixture[4].append(orphan)
    assert_both_reject(tuple(fixture), "ORPHAN_RECORD")


def test_orphan_contract_is_rejected_even_when_not_selected():
    fixture = list(closed_fixture("pass"))
    authority = copy.deepcopy(fixture[5])
    orphan = copy.deepcopy(fixture[5][0])
    orphan["provenance"] = "UNAUTHORIZED_ORPHAN"
    body = {key: value for key, value in orphan.items()
            if key not in {"observation_contract_id", "contract_sha256"}}
    orphan["contract_sha256"] = _hash(body)
    orphan["observation_contract_id"] = "OBS__ORPHAN__" + orphan["contract_sha256"][:16]
    fixture[5].append(orphan)
    explanations, requirement, measurement, comparisons, predictions, contracts = fixture
    specs = [item.to_dict() for item in canonical_apparatus_gate_specs()]
    for implementation in (evaluate_apparatus, reconstruct_apparatus):
        with pytest.raises(ValueError, match="AUTHORITATIVE_PROVENANCE_MISMATCH|ORPHAN_RECORD"):
            implementation(
                explanations, [requirement], [measurement], specs,
                comparisons, predictions, contracts,
                authoritative_contracts=copy.deepcopy(authority),
            )


def test_verifier_global_closure_survives_producer_validator_noop(monkeypatch):
    fixture = list(closed_fixture("pass"))
    orphan = copy.deepcopy(fixture[4][0])
    orphan["case_id"] = "UNAUTHORIZED_CASE"
    orphan["prediction_id"] = "PRED__null__UNAUTHORIZED_CASE__flow"
    fixture[4].append(orphan)
    monkeypatch.setattr(
        governance,
        "_validate_global_evidence_universe",
        lambda *args, **kwargs: ({}, {}, {}, {}, {}, {}),
    )
    verifier = calls(tuple(fixture))[1]
    with pytest.raises(ValueError, match="ORPHAN_RECORD"):
        verifier()


def test_valid_universe_is_order_independent_after_global_validation():
    fixture = closed_fixture("fail")
    first = calls(fixture)
    reordered = list(copy.deepcopy(fixture))
    reordered[4].reverse()
    second = calls(tuple(reordered))
    for left, right in zip(first, second):
        assert [item.to_dict() for item in left()[1]] == [item.to_dict() for item in right()[1]]


def test_duplicate_unused_prediction_is_rejected_globally():
    fixture = list(closed_fixture("pass"))
    fixture[4].append(copy.deepcopy(fixture[4][0]))
    assert_both_reject(tuple(fixture), "duplicate|DUPLICATE")


def test_wrong_type_unused_prediction_reference_is_rejected_globally():
    fixture = list(closed_fixture("pass"))
    orphan = copy.deepcopy(fixture[4][0])
    orphan["explanation_id"] = fixture[1]["requirement_id"]
    orphan["prediction_id"] = (
        f"PRED__{orphan['explanation_id']}__{orphan['case_id']}__{orphan['channel']}"
    )
    fixture[4].append(orphan)
    assert_both_reject(tuple(fixture), "DANGLING_REFERENCE")


def test_cross_pair_unused_comparison_is_rejected_globally():
    fixture = list(closed_fixture("pass"))
    fixture[3][0]["pair_id"] = "UNAUTHORIZED_PAIR"
    assert_both_reject(tuple(fixture), "CROSS_CONTEXT_REFERENCE")


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda bundle: bundle["run_manifest"]["selected_card_sha256"].update(
            {"foster2025_2.md": "0" * 64}), "AUTHORITATIVE_PROVENANCE_MISMATCH|UNAUTHORIZED_ROOT"),
        (lambda bundle: bundle["run_manifest"].__setitem__(
            "registry_snapshot_sha256", "0" * 64), "AUTHORITATIVE_PROVENANCE_MISMATCH"),
        (lambda bundle: bundle["result_cells"].append({
            **copy.deepcopy(bundle["result_cells"][0]),
            "component_id": "UNSELECTED_COMPONENT"}), "ORPHAN_RECORD"),
        (lambda bundle: bundle["decision"]["qualifying_requirement_ids"].append(
            "UNAUTHORIZED_REQUIREMENT"), "inconsistent|DANGLING_REFERENCE|ORPHAN_RECORD"),
        (lambda bundle: bundle["apparatus_evaluation"]["gate_evidence_ids"].append(
            "ORPHAN_GATE_EVIDENCE"), "inconsistent|DANGLING_REFERENCE|ORPHAN_RECORD"),
    ],
)
def test_full_bundle_authority_and_orphan_mutations_rejected(mutation, match):
    bundle = runner.build_bundle()
    changed = copy.deepcopy(bundle)
    mutation(changed)
    with pytest.raises(ValueError, match=match):
        runner.validate_bundle(changed)


def test_orphan_gate_evidence_and_result_are_rejected_in_full_bundle():
    fixture = closed_fixture("pass")
    evidence, results, _ = calls(fixture)[0]()
    bundle = runner.build_bundle()
    changed = copy.deepcopy(bundle)
    changed["apparatus_gate_evidence"] = [evidence[0].to_dict()]
    changed["apparatus_gate_results"] = [results[0].to_dict()]
    with pytest.raises(ValueError, match="DANGLING_REFERENCE|ORPHAN_RECORD|inconsistent"):
        runner.validate_bundle(changed)


def test_orphan_measurement_with_dangling_requirement_is_rejected_globally():
    fixture = list(closed_fixture("pass"))
    orphan = copy.deepcopy(fixture[2])
    orphan["measurement_record_id"] += "__ORPHAN"
    orphan["requirement_id"] = "UNAUTHORIZED_REQUIREMENT"
    explanations, requirement, measurement, comparisons, predictions, contracts = fixture
    specs = [item.to_dict() for item in canonical_apparatus_gate_specs()]
    for implementation in (evaluate_apparatus, reconstruct_apparatus):
        with pytest.raises(ValueError, match="DANGLING_REFERENCE"):
            implementation(
                explanations, [requirement], [measurement, orphan], specs,
                comparisons, predictions, contracts,
                authoritative_contracts=copy.deepcopy(contracts),
            )

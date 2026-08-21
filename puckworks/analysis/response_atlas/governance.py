"""Scenario-specific coverage and apparatus governance for RP-A-001 C1-R2."""
from __future__ import annotations

from itertools import combinations

from .schema import (
    ApparatusEvaluationRecord,
    ApparatusGateResult,
    ApparatusGateSpec,
    CoverageEdgeRecord,
    DiscriminationRequirementRecord,
)

COVERAGE_VERSION = "rp-a-001-coverage/v2"
APPARATUS_VERSION = "rp-a-001-apparatus-gates/v1"
GATES = (
    ("SIGN", True),
    ("PRESSURE_OR_FLOW_ORDERING", True),
    ("PRESSURE_LAG", False),
    ("TRANSIENT_TIMING", False),
    ("FIRST_DRIP_TIMING", False),
    ("FLOW_MINIMUM", False),
    ("FLOW_RECOVERY", False),
    ("CROSS_CONDITION_TRANSFER", False),
)


def requirement_from_eligibility(row: dict) -> DiscriminationRequirementRecord:
    relevant = row["eligibility"] == "eligible"
    status = "relevant" if relevant else ("unresolved" if row["eligibility"] == "unresolved" else "irrelevant")
    return DiscriminationRequirementRecord(
        requirement_id=row["requirement_id"], pair_id=row["pair_id"],
        left_explanation=row["left_explanation"], right_explanation=row["right_explanation"],
        scenario=row["scenario"], control_mode=row["common_intervention"],
        intervention_id=row["intervention_id"], pressure_node="NOT_COMMON",
        pressure_reference="NOT_COMMON", basis_id=row["basis_id"], time_basis="NOT_COMMON",
        pair_role=row["pair_role"], scientific_question=row["scientific_question"],
        relevant_to_final_decision=relevant,
        applicable_candidate_channels=[row["candidate_observable"]],
        requirement_status=status, reason_code=row["reason_code"],
        provenance=f"channel_eligibility:{row['eligibility_id']}",
    )


def build_requirements(eligibility: list[dict]) -> list[DiscriminationRequirementRecord]:
    grouped: dict[str, list[dict]] = {}
    for row in eligibility:
        grouped.setdefault(row["requirement_id"], []).append(row)
    by_id = {}
    for requirement_id, rows in grouped.items():
        first = requirement_from_eligibility(rows[0])
        invariant = ("pair_id", "left_explanation", "right_explanation", "scenario",
                     "intervention_id", "basis_id", "pair_role", "scientific_question")
        if any(any(row[field] != rows[0][field] for field in invariant) for row in rows[1:]):
            raise ValueError("inconsistent duplicate discrimination requirement")
        data = first.to_dict()
        data["applicable_candidate_channels"] = sorted({row["candidate_observable"] for row in rows})
        data["provenance"] = ";".join(sorted(f"channel_eligibility:{row['eligibility_id']}" for row in rows))
        by_id[requirement_id] = DiscriminationRequirementRecord.from_dict(data)
    return [by_id[key] for key in sorted(by_id)]


def build_coverage_edges(measurements: list[dict], eligibility: list[dict]) -> list[CoverageEdgeRecord]:
    eligible = {row["eligibility_id"]: row for row in eligibility}
    edges = []
    for row in measurements:
        match = eligible[row["eligibility_id"]]
        if (row["classification"] == "ROBUSTLY_DISCRIMINATING" and
                row["comparability_level"] in (1, 2) and match["eligibility"] == "eligible" and
                match["uncertainty_available"]):
            edges.append(CoverageEdgeRecord(
                coverage_edge_id=f"EDGE__{row['measurement_record_id']}__{row['requirement_id']}",
                requirement_id=row["requirement_id"], measurement_record_id=row["measurement_record_id"],
                measurement_option_id=row["measurement_option_id"], scenario=row["scenario"],
                channel=row["channel"], adapter_id=row["adapter_id"],
                adapter_version=row["adapter_version"], classification=row["classification"],
                robust=True, provenance=f"measurement:{row['measurement_record_id']}",
            ))
    return sorted(edges, key=lambda edge: edge.coverage_edge_id)


def validate_measurement_linkage(record: dict, match: dict | None) -> None:
    fields = ("requirement_id", "pair_id", "left_explanation", "right_explanation",
              "scenario", "adapter_id", "adapter_version", "comparability_level",
              "intervention_id", "basis_id")
    if match is None or any(match[field] != record[field] for field in fields) or match["candidate_observable"] != record["channel"]:
        raise ValueError("measurement record lacks exact channel eligibility")
    expected_option = f"MEASOPT__{record['channel']}__{record['adapter_id']}__{record['adapter_version']}__{record['basis_id']}"
    if record["measurement_option_id"] != expected_option:
        raise ValueError("measurement option does not bind channel and adapter contract")


def minimum_measurement_sets(requirements: list[dict], edges: list[dict]) -> dict:
    universe = sorted(row["requirement_id"] for row in requirements
                      if row["relevant_to_final_decision"])
    options: dict[str, set[str]] = {}
    for edge in edges:
        options.setdefault(edge["measurement_option_id"], set()).add(edge["requirement_id"])
    uncovered = sorted(set(universe) - set().union(*options.values())) if options else universe
    sets: list[list[str]] = []
    if universe and not uncovered:
        names = sorted(options)
        for size in range(1, len(names) + 1):
            for combo in combinations(names, size):
                if set().union(*(options[name] for name in combo)) >= set(universe):
                    sets.append(list(combo))
            if sets:
                break
    complete = bool(universe and sets and not uncovered)
    return {
        "algorithm_version": COVERAGE_VERSION,
        "universe_requirement_ids": universe,
        "coverage_options": {key: sorted(value) for key, value in sorted(options.items())},
        "minimum_set_ids": [f"MINSET__{i + 1}" for i in range(len(sets))],
        "all_equally_minimal_sets": sets,
        "uncovered_requirement_ids": uncovered,
        "complete": complete,
        "zero_universe_status": ("NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM" if not universe
                                 else "ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM_PRESENT"),
        "result": sets if complete else "NO_COMPLETE_MEASUREMENT_SET",
    }


def apparatus_gate_specs() -> list[ApparatusGateSpec]:
    return [ApparatusGateSpec(
        gate_id=f"APP_GATE__{name}", gate_name=name, primary=primary,
        applicability_rule=("APPLICABLE_WHEN_MATCHED_RESPONSE_EXPOSES_GATE" if primary else
                            "CONDITIONAL_WHEN_MATCHED_SCENARIO_PHYSICALLY_EXPOSES_GATE"),
        required_evidence_type="MATCHED_LEVEL_1_OR_2_COMPARISON_WITH_COMPLETE_UNCERTAINTY",
        maximum_comparability_level=2, uncertainty_required=True,
        pass_criterion="MATCHED_GATE_PASSES_WITHIN_DECLARED_UNCERTAINTY",
        fail_criterion="MATCHED_GATE_ROBUSTLY_FAILS_WITH_COMPLETE_UNCERTAINTY",
        contract_version=APPARATUS_VERSION) for name, primary in GATES]


def evaluate_apparatus(explanations: list[dict], requirements: list[dict],
                       measurements: list[dict], specs: list[dict]) -> tuple[list[ApparatusGateResult], ApparatusEvaluationRecord]:
    apparatus_ids = sorted(row["explanation_id"] for row in explanations
                           if row["scientific_role"] == "FIXED_BED_MACHINE_AND_APPARATUS_NULL")
    matched = [row for row in requirements if row["relevant_to_final_decision"] and
               ({row["left_explanation"], row["right_explanation"]} & set(apparatus_ids))]
    if not matched:
        return [], ApparatusEvaluationRecord(
            "APPARATUS_EVALUATION", apparatus_ids, "NOT_EVALUATED", [], [], [], [], False,
            [], "NO_MATCHED_APPARATUS_COMPARATOR", APPARATUS_VERSION)
    # A relevant matched requirement without complete gate evidence is unresolved, never failed.
    results = []
    for requirement in matched:
        related = [m for m in measurements if m["requirement_id"] == requirement["requirement_id"]]
        for spec in specs:
            status = "UNRESOLVED"
            reason = "APPLICABLE_GATE_EVIDENCE_MISSING"
            evidence = [m["measurement_record_id"] for m in related]
            results.append(ApparatusGateResult(
                f"APP_RESULT__{spec['gate_name']}__{requirement['scenario']}", spec["gate_id"],
                next(iter(set(apparatus_ids) & {requirement['left_explanation'], requirement['right_explanation']})),
                requirement["right_explanation"] if requirement["left_explanation"] in apparatus_ids else requirement["left_explanation"],
                requirement["scenario"], "APPLICABLE", status, [requirement["pair_id"]], evidence,
                "COMPLETE" if status != "UNRESOLVED" else "MISSING",
                reason, [f"requirement:{requirement['requirement_id']}"]))
    passing = [r.gate_result_id for r in results if r.status == "PASS"]
    failing = [r.gate_result_id for r in results if r.status == "FAIL"]
    unresolved = [r.gate_result_id for r in results if r.status == "UNRESOLVED"]
    status = ("RULED_OUT_BY_MATCHED_GATE" if failing else
              "SURVIVES_ALL_APPLICABLE_GATES" if results and not unresolved else
              "UNRESOLVED_MISSING_UNCERTAINTY")
    return results, ApparatusEvaluationRecord(
        "APPARATUS_EVALUATION", apparatus_ids, status,
        [r.gate_result_id for r in results], passing, failing, unresolved,
        bool(results and not failing and not unresolved),
        sorted({r.scenario for r in results}),
        "ALL_APPLICABLE_GATES_PASS" if status == "SURVIVES_ALL_APPLICABLE_GATES" else
        "MATCHED_GATE_FAILED" if failing else "APPLICABLE_GATE_UNRESOLVED",
        APPARATUS_VERSION)

from __future__ import annotations

from collections import Counter
import json
import platform
import subprocess
import time
from pathlib import Path

import numpy as np
import scipy

from puckworks.models.cameron2020 import extraction_bdf as cameron
from puckworks.models.foster2025 import machine_mode as foster
from puckworks.models.wadsworth2026 import inertial, permeability
from puckworks.viz.relationship import classify_relationship

from .adapters import ADAPTER_VERSIONS
from .artifacts import canonical_bytes, sha256, write_json
from .decision import RULE_VERSION, derive_scientific_decision
from .governance import (APPARATUS_VERSION, COVERAGE_VERSION, OBSERVATION_VERSION,
                         QUESTION_VERSION, REQUIREMENT_VERSION, SEMANTIC_VERSION,
                         canonical_apparatus_gate_specs, canonical_observation_contracts,
                         canonical_scientific_questions, build_channel_eligibility,
                         build_coverage_edges, build_requirements, coverage_matrix,
                         evaluate_apparatus, minimum_measurement_sets, validate_measurement_linkage)
from .inventory import inventory
from .measurement_value import build_measurement_record, discriminate
from .independent_verifier import independently_select, reconstruct_apparatus
from .schema import (ApparatusEvaluationRecord, ApparatusGateEvidenceRecord, ApparatusGateResult, ApparatusGateSpec,
                     ComparisonEligibilityRecord, CoverageEdgeRecord, DecisionRecord,
                     DiscriminationRequirementRecord, ExplanationRecord, MeasurementValueRecord,
                     ObservationContractRecord, PredictionIntervalRecord, QuantityRow, ResidualRecord,
                     ResultCell, ScientificQuestionRecord)

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/analysis/rp_a_001"
INPUT = BASE / "c1"
R1 = BASE / "c1_r1"
OUT = BASE / "c1_r2"
R2 = BASE / "c1_r2"
OUT = BASE / "c1_r3"
SCHEMA_VERSION = "puckworks.response-atlas-export/v5"
CLAIM = "MODEL_RESPONSE_COMPARISON_ONLY__PHYSICAL_VALIDATION_NOT_ESTABLISHED"
CHANNELS = ["basket_pressure", "separate_upstream_pressure", "flow", "delivered_mass",
            "bed_height_or_deformation", "first_drip_timing", "temperature",
            "turbidity_or_downstream_suspended_solids", "retained_fines_mass",
            "spatial_flow_variance", "local_extraction"]


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate_protocol():
    base = _load(BASE / "protocol.json")
    c1 = _load(INPUT / "correction_protocol.json")
    r1 = _load(R1 / "correction_protocol.json")
    r2 = _load(R2 / "correction_protocol.json")
    r3 = _load(OUT / "correction_protocol.json")
    cases = _load(INPUT / "case_matrix.json")
    if base["programme_protocol_version"] != "sci-md-003-rp-a-001/v1":
        raise ValueError("base protocol changed")
    if c1["programme_protocol_version"] != "sci-md-003-rp-a-001/c1":
        raise ValueError("wrong C1 protocol")
    if c1["schema_version"] != "puckworks.response-atlas-export/v2":
        raise ValueError("wrong preserved C1 export schema")
    if r1["programme_protocol_version"] != "sci-md-003-rp-a-001/c1-r1" or r1["schema_version"] != "puckworks.response-atlas-export/v3":
        raise ValueError("wrong preserved C1-R1 protocol")
    if r2["programme_protocol_version"] != "sci-md-003-rp-a-001/c1-r2" or r2["export_schema"] != "puckworks.response-atlas-export/v4":
        raise ValueError("wrong preserved C1-R2 protocol")
    if r3["programme_protocol_version"] != "sci-md-003-rp-a-001/c1-r3" or r3["export_schema"] != SCHEMA_VERSION:
        raise ValueError("wrong C1-R3 protocol or export schema")
    if sha256(ROOT / "docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md") != c1["component_response_atlas_spec_sha256"]:
        raise ValueError("base specification drift")
    if len(cases["cases"]) != 6 or cases["frozen_status"] != "FROZEN_PRE_CORRECTED_ANALYSIS":
        raise ValueError("C1 case matrix is not frozen")
    return True


def _cell(component, case, observable, status, unit, value=None, **kw):
    return ResultCell(component, case, observable, status, unit, value=value, **kw)


def _cameron_results(cases):
    cells, reports, evaluations = [], [], 0
    for case in cases:
        mapping = case["native_mapping"]["cameron2020.extraction_bdf"]
        if isinstance(mapping, str):
            cells.append(_cell("cameron2020.extraction_bdf", case["case_id"], "transient_flow_history",
                               "UNSUPPORTED_RELATIONSHIP", "m/s", reason=mapping, adjudicative=False))
            continue
        p, gs = mapping["p_bar"], mapping["gs"]
        if not (5.0 <= p <= 11.0 and 1.1 <= gs <= 2.3):
            cells.append(_cell("cameron2020.extraction_bdf", case["case_id"], "extraction_yield",
                               "OUTSIDE_VALID_RANGE", "percent", reason="CAMERON_CARD_RANGE", adjudicative=False))
            continue
        result = cameron.simulate_shot(gs, p, N=16, M=12, n_save=50, rtol=2e-5, atol=2e-7)
        evaluations += 1
        q = cameron.darcy_flux(gs, p, L=cameron.bed_depth(.020), L_ref=cameron.bed_depth(.020))
        values = {
            "darcy_velocity": (q, "m/s", "superficial bed-area basis", "NOT_APPLICABLE"),
            "shot_duration": (result.t_shot, "s", "time to fixed 0.040 kg beverage mass", "SHOT_START_SCALAR_Q"),
            "final_tds": (result.tds, "mass_percent_cup", "accumulated cup beverage mass", "NOT_APPLICABLE"),
            "extraction_yield": (result.EY, "percent", "initial dry-coffee mass", "NOT_APPLICABLE"),
            "accumulated_extracted_mass": (float(result.m_cup[-1]), "kg", "dissolved solids in cup", "NOT_APPLICABLE"),
            "outlet_concentration_final": (float(result.cl_out[-1]), "kg/m^3", "instantaneous bed-outlet liquid", "SHOT_START_SCALAR_Q")}
        for observable, (value, unit, basis, time_basis) in values.items():
            cells.append(_cell("cameron2020.extraction_bdf", case["case_id"], observable,
                               "SUPPORTED", unit, value, reference_basis=basis, time_basis=time_basis,
                               pressure_node="PUMP_OUTLET" if observable == "darcy_velocity" else "NOT_APPLICABLE",
                               pressure_reference="GAUGE" if observable == "darcy_velocity" else "NOT_APPLICABLE",
                               evidence_strength="code_verification", evidence_domain_status="WITHIN_DECLARED_CAMERON_DOMAIN",
                               source_kind="SOURCE_NATIVE_SCALAR_Q"))
        reports.append({"case_id": case["case_id"], "p_bar": p, "gs": gs,
                        "darcy_velocity_m_s": q, "shot_duration_s": result.t_shot,
                        "final_tds_percent": result.tds, "extraction_yield_percent": result.EY})
    pressure = [r for r in reports if r["case_id"] in ("P05_REF", "P09_REF", "P11_REF")]
    curve = classify_relationship([5, 9, 11], [r["extraction_yield_percent"] for r in pressure]).to_dict()
    return cells, {"role": "DOWNSTREAM_EXTRACTION_OBSERVER", "cases": reports,
                   "pressure_ordering_extraction_yield": "STRICT_DECREASING",
                   "curvature": curve, "grind_direction": "CAMERON_EK43_SOURCE_NATIVE_ONLY",
                   "transient_flow_history": "UNSUPPORTED_RELATIONSHIP",
                   "uncertainty": "NOT_PROVIDED", "evidence_ceiling": "code_verification; observation operator only"}, evaluations


def _foster_results():
    result = foster.solve()
    qmin, tmin = foster.flow_minimum(result)
    tp = result["t_p"] + result["p"].t_shift
    ts = result["t_s"] + result["p"].t_shift
    recovery = foster.bed_flow_norm(ts, result) / qmin
    common = dict(evidence_strength="source_curve_reproduction",
                  evidence_domain_status="SOURCE_FINE_GRIND_POST_FIT_MACHINE_CASE",
                  source_kind="SOURCE_NATIVE", time_basis="SOURCE_EXPERIMENT_FRAME_WITH_FITTED_T_SHIFT")
    cells = [
        _cell("foster2025.machine_mode", "MACHINE_REF", "ponding_time", "SUPPORTED", "s", tp, reference_basis="source event definition", **common),
        _cell("foster2025.machine_mode", "MACHINE_REF", "saturation_time", "SUPPORTED", "s", ts, reference_basis="front reaches bed outlet", **common),
        _cell("foster2025.machine_mode", "MACHINE_REF", "minimum_normalized_flow", "SUPPORTED", "1", qmin, reference_basis="Q/Q_m", evidence_strength=common["evidence_strength"], evidence_domain_status=common["evidence_domain_status"]),
        _cell("foster2025.machine_mode", "MACHINE_REF", "time_to_flow_minimum", "SUPPORTED", "s", tmin, reference_basis="source flow-minimum event", **common),
        _cell("foster2025.machine_mode", "MACHINE_REF", "recovery_ratio", "SUPPORTED", "1", recovery, reference_basis="flow at saturation / minimum flow", evidence_strength=common["evidence_strength"], evidence_domain_status=common["evidence_domain_status"]),
        _cell("foster2025.machine_mode", "MACHINE_REF", "first_drip_timing", "UNSUPPORTED_RELATIONSHIP", "s", reason="NO_SATURATION_TO_SCALE_THRESHOLD_OBSERVATION_ADAPTER", adjudicative=False,
              time_basis="SOURCE_EXPERIMENT_FRAME_WITH_FITTED_T_SHIFT", evidence_strength="source_curve_reproduction", evidence_domain_status="NOT_ESTABLISHED_AS_SAME_OBSERVABLE")]
    return cells, {"role": "FIXED_BED_MACHINE_AND_APPARATUS_NULL",
                   "case_id": "MACHINE_REF", "ponding_time_s": tp, "saturation_time_s": ts,
                   "minimum_normalized_flow": qmin, "time_to_flow_minimum_s": tmin,
                   "recovery_ratio": recovery, "first_drip_timing": "UNSUPPORTED_RELATIONSHIP",
                   "first_drip_reason": "Saturation is native; scale-threshold first drip is a distinct measurement comparator.",
                   "pressure_ordering": "NOT_APPLICABLE_MACHINE_GENERATED",
                   "uncertainty": "NOT_PROVIDED", "evidence_ceiling": "source_curve_reproduction; post-fit machine case"}, 1


def _wadsworth_results(cases):
    cells = []
    for case in cases:
        reason = case["native_mapping"]["wadsworth2026.inertial"]
        cells.append(_cell("wadsworth2026.inertial", case["case_id"], "darcy_velocity",
                           "UNSUPPORTED_FOR_CASE", "m/s", reason=str(reason), adjudicative=False,
                           pressure_node="BED_PRESSURE_DROP", pressure_reference="DIFFERENTIAL",
                           reference_basis="superficial bed-area basis", evidence_strength="source_curve_reproduction",
                           evidence_domain_status="PRESSURE_GRADIENT_RANGE_NOT_PROVIDED__TAMPED_INERTIAL_CLOSURE_EXTRAPOLATION"))
    band_zhou = inertial.espresso_fo_band("zhou")
    band_exp = inertial.espresso_fo_band("exp")
    cells.extend([
        _cell("wadsworth2026.inertial", "WADSWORTH_WORKED_FO_ENDPOINTS", "forchheimer_number_min", "SUPPORTED", "1", band_zhou[0], adjudicative=False, reference_basis="card worked endpoint corners", evidence_strength="source_curve_reproduction", evidence_domain_status="MATHEMATICAL_DIAGNOSTIC_CERAMICS_CLOSURE_NOT_TAMPED_COFFEE_VALIDATION"),
        _cell("wadsworth2026.inertial", "WADSWORTH_WORKED_FO_ENDPOINTS", "forchheimer_number_max", "SUPPORTED", "1", band_zhou[1], adjudicative=False, reference_basis="card worked endpoint corners", evidence_strength="source_curve_reproduction", evidence_domain_status="MATHEMATICAL_DIAGNOSTIC_CERAMICS_CLOSURE_NOT_TAMPED_COFFEE_VALIDATION")])
    k = float(permeability.k_percolation(145e-6, .3))
    ki = float(inertial.k_I(k, "zhou"))
    q_parent = 5.36e-4
    gradient = inertial.MU_92C / k * q_parent + inertial.RHO_92C / ki * q_parent ** 2
    q_reconstructed = float(inertial.solve_q(k, ki, gradient))
    q_darcy = float(inertial.solve_q(k, float("inf"), gradient))
    contrast = q_reconstructed - q_darcy
    closure = q_reconstructed - (q_darcy + contrast)
    residual = ResidualRecord("WADSWORTH_SOURCE_REFERENCE_INERTIAL_VS_DARCY",
                              "wadsworth2026.inertial/WADSWORTH_WORKED_FO_ENDPOINTS",
                              "wadsworth2026.inertial/WADSWORTH_DARCY_LIMIT",
                              "darcy_velocity", "m/s", 1, True, contrast, "NOT_PROVIDED",
                              "same producer with inertial contribution disabled", closure, 1e-12,
                              "NESTED_DIFFERENCE", True, None, "MATHEMATICAL_NESTED_LIMIT_NONADJUDICATIVE")
    report = {"role": "STATIC_OR_INERTIAL_HYDRAULIC_RESPONSE_LENS",
              "primary_pressure_cases": "UNSUPPORTED_FOR_CASE_SOURCE_EVIDENCE_DOMAIN",
              "worked_fo_band_zhou": list(band_zhou), "worked_fo_band_exp": list(band_exp),
              "mathematical_domain_status": "EXECUTABLE_STRICT_SI_POSITIVE",
              "declared_valid_range": "Fo_F regime flag; pressure-gradient range NOT_PROVIDED",
              "evidence_domain": "permeability validated on untamped packs; k_I ceramics-fit; tamped-coffee extrapolation",
              "adjudicative_support": "EXCLUDED",
              "grind_direction": "NOT_ADJUDICATED_FIXED_POROSITY_RADIUS_IS_NOT_COMPLETE_GRIND",
              "timing": "UNSUPPORTED_RELATIONSHIP", "evidence_ceiling": "non-adjudicative response lens"}
    return cells, report, residual, 3


def _explanations(registry_hash, cards):
    return [
        ExplanationRecord("FOSTER_FIXED_BED_MACHINE_NULL", "foster2025.machine_mode", "FIXED_BED_MACHINE_AND_APPARATUS_NULL", "machine", "Can apparatus and fixed-bed wetting generate response features?", "puckworks.models.foster2025.machine_mode", cards["foster2025_2.md"], registry_hash, ["fixed bed", "sharp wetting front", "pump and headspace dynamics", "no evolving bed physics"], "MACHINE_COUPLED", "MULTIPLE_SOURCE_NATIVE_NODES", "ABSOLUTE_AND_DIFFERENTIAL", "source fine-grind post-fit case", ["ponding_time", "saturation_time", "flow_minimum", "recovery_ratio"], "SOURCE_FINE_GRIND_POST_FIT", "COMPETING_EXPLANATION", CLAIM),
        ExplanationRecord("WADSWORTH_STATIC_INERTIAL_LENS", "wadsworth2026.inertial", "STATIC_OR_INERTIAL_HYDRAULIC_RESPONSE_LENS", "flow", "How does a static Forchheimer closure depart from Darcy?", "puckworks.models.wadsworth2026.inertial", cards["wadsworth2026_inertial.md"], registry_hash, ["steady single phase", "declared k", "ceramics-fit inertial closure"], "PRESCRIBED_BED_PRESSURE_GRADIENT", "BED_PRESSURE_DROP", "DIFFERENTIAL", "mathematical positive-SI domain; tamped evidence extrapolative", ["darcy_velocity", "forchheimer_number"], "NOT_VALIDATED_FOR_TAMPED_COFFEE_INERTIAL_CLOSURE", "RESPONSE_LENS", CLAIM),
        ExplanationRecord("CAMERON_EXTRACTION_OBSERVER", "cameron2020.extraction_bdf", "DOWNSTREAM_EXTRACTION_OBSERVER", "extraction", "Does a scalar hydraulic contrast remain visible at the cup observer?", "puckworks.models.cameron2020.extraction_bdf", cards["cameron2020.md"], registry_hash, ["scalar Darcy flux", "saturated static bed", "one-way extraction observer"], "PRESCRIBED_PUMP_OVERPRESSURE_OR_SCALAR_Q", "PUMP_OUTLET", "GAUGE", "EK43 1.1-2.3; 5-11 bar pilot", ["outlet_concentration", "tds", "extraction_yield"], "WITHIN_CODE_VERIFICATION_DOMAIN", "OBSERVATION_OPERATOR", CLAIM)]


def _pairs():
    raw = [
        ("PAIR_FOSTER_CAMERON_MACHINE", "FOSTER_FIXED_BED_MACHINE_NULL", "CAMERON_EXTRACTION_OBSERVER", "MACHINE_REF", "flow", 4, "OBSERVATION_OPERATOR_COMPARISON", "ineligible", "CONTROL_MODE_AND_TRANSIENT_HISTORY_NOT_MATCHED"),
        ("PAIR_FOSTER_WADSWORTH_FLOW", "FOSTER_FIXED_BED_MACHINE_NULL", "WADSWORTH_STATIC_INERTIAL_LENS", "MACHINE_REF", "flow", 3, "NONCOMPETING_COMPONENTS", "ineligible", "TIME_RESOLVED_MACHINE_FLOW_VS_STATIC_RESPONSE_LENS"),
        ("PAIR_WADSWORTH_CAMERON_FLOW", "WADSWORTH_STATIC_INERTIAL_LENS", "CAMERON_EXTRACTION_OBSERVER", "P09_REF", "flow", 4, "OBSERVATION_OPERATOR_COMPARISON", "ineligible", "BED_DROP_VS_PUMP_OVERPRESSURE_AND_WADSWORTH_EVIDENCE_EXCLUDED"),
        ("PAIR_WADSWORTH_NESTED_LIMIT", "WADSWORTH_STATIC_INERTIAL_LENS", "WADSWORTH_STATIC_INERTIAL_LENS", "WADSWORTH_WORKED_FO_ENDPOINTS", "flow", 1, "NESTED_LIMIT", "unresolved", "MATHEMATICALLY_NESTED_BUT_NOT_ADJUDICATIVE_IN_TAMPED_COFFEE_DOMAIN")]
    records = []
    for pid, left, right, scenario, channel, level, role, eligibility, reason in raw:
        intervention = "NOT_COMMON" if level > 2 else "SAME_PRODUCER_REFERENCE"
        basis = "NOT_COMMON" if level > 2 else "SUPERFICIAL_VELOCITY_M_S"
        requirement = f"REQ__{pid}__{scenario}__{intervention}__{basis}"
        adapter_id, adapter_version = "DIRECT_NATIVE", "1.0.0"
        records.append(ComparisonEligibilityRecord(
            pid, left, right, "bounded common-observable response", scenario, channel,
            intervention, "NOT_COMMON" if level > 2 else "superficial velocity m/s",
            level, role, eligibility, reason, adapter_id, adapter_version, False,
            f"ELIG__{requirement}__{channel}__{adapter_id}__{adapter_version}",
            requirement, intervention, basis,
            "SUPPORTED" if eligibility == "eligible" else "NOT_EVALUATED",
            "DIRECT_NATIVE_CONTRACT_V1"))
    return records


def _derive_measurements(eligible, cells, assumptions, explanations):
    component = {e.explanation_id: e.component_id for e in explanations}
    assumption = {row["channel"]: row for row in assumptions["channels"]}
    aliases = {"flow": {"darcy_velocity"}, "first_drip_timing": {"first_drip_timing"},
               "delivered_mass": {"delivered_mass"}, "basket_pressure": {"basket_pressure"},
               "separate_upstream_pressure": {"upstream_pressure"},
               "bed_height_or_deformation": {"bed_height", "deformation"},
               "temperature": {"temperature"},
               "turbidity_or_downstream_suspended_solids": {"turbidity", "suspended_solids"},
               "retained_fines_mass": {"retained_fines_mass"},
               "spatial_flow_variance": {"spatial_flow_variance"},
               "local_extraction": {"local_extraction"}}
    by_key = {(c.component_id, c.case_id, c.observable): c for c in cells}
    predictions, records = [], []

    def find(explanation_id, scenario, channel):
        cid = component[explanation_id]
        matches = [cell for (comp, case, obs), cell in by_key.items()
                   if comp == cid and case == scenario and obs in aliases[channel]]
        return matches[0] if matches else None

    def prediction(explanation_id, cell, channel):
        if cell is None or cell.support_status != "SUPPORTED" or not cell.adjudicative:
            return None
        rec = PredictionIntervalRecord(
            f"PRED__{explanation_id}__{cell.case_id}__{channel}", explanation_id,
            cell.case_id, channel, cell.observable, cell.unit, cell.pressure_node,
            cell.pressure_reference, cell.time_basis, float(cell.value), float(cell.value),
            float(cell.value), "NOT_PROVIDED", "BOUNDED_BELOW_NUMERICAL_TOLERANCE",
            "NOT_APPLICABLE", "NOT_PROVIDED", cell.evidence_domain_status,
            f"result_cell:{cell.component_id}/{cell.case_id}/{cell.observable}",
            ["PARAMETER_UNCERTAINTY_NOT_PROVIDED", "INITIALIZATION_HISTORY_UNCERTAINTY_NOT_PROVIDED"])
        predictions.append(rec)
        return rec

    for pair in eligible:
        for channel in [pair.candidate_observable]:
            left_cell = find(pair.left_explanation, pair.scenario, channel)
            right_cell = find(pair.right_explanation, pair.scenario, channel)
            left = prediction(pair.left_explanation, left_cell, channel)
            right = prediction(pair.right_explanation, right_cell, channel)
            left_status = left_cell.support_status if left_cell else "UNSUPPORTED_RELATIONSHIP"
            right_status = right_cell.support_status if right_cell else "UNSUPPORTED_RELATIONSHIP"
            a = assumption[channel]
            uncertainty = a["measurement_uncertainty"]
            if isinstance(uncertainty, dict):
                uncertainty = next(iter(uncertainty.values()))
            records.append(build_measurement_record(
                pair=pair, channel=channel, left_support=left_status, right_support=right_status,
                left=left, right=right, measurement_uncertainty=uncertainty,
                uncertainty_provenance=a["assumption_class"]))
    unique = {p.prediction_id: p for p in predictions}
    return list(unique.values()), records


def validate_bundle(bundle):
    if bundle.get("schema_version") != SCHEMA_VERSION or "pair_eligibility" in bundle:
        raise ValueError("wrong v5 response-atlas schema or redundant eligibility contract")
    typed = (("quantity_inventory", QuantityRow), ("result_cells", ResultCell),
             ("explanations", ExplanationRecord), ("scientific_questions", ScientificQuestionRecord),
             ("observation_contracts", ObservationContractRecord),
             ("discrimination_requirements", DiscriminationRequirementRecord),
             ("channel_eligibility", ComparisonEligibilityRecord),
             ("prediction_intervals", PredictionIntervalRecord),
             ("measurement_value_records", MeasurementValueRecord), ("coverage_edges", CoverageEdgeRecord),
             ("apparatus_gate_specs", ApparatusGateSpec),
             ("apparatus_gate_evidence", ApparatusGateEvidenceRecord),
             ("apparatus_gate_results", ApparatusGateResult), ("residual_records", ResidualRecord))
    for key, cls in typed:
        for row in bundle[key]: cls.from_dict(row)
    ApparatusEvaluationRecord.from_dict(bundle["apparatus_evaluation"])
    decision = DecisionRecord.from_dict(bundle["decision"])
    questions = [x.to_dict() for x in canonical_scientific_questions(bundle["explanations"])]
    contracts = [x.to_dict() for x in canonical_observation_contracts(questions)]
    requirements = [x.to_dict() for x in build_requirements(questions, contracts)]
    eligibility = [x.to_dict() for x in build_channel_eligibility(questions, requirements, contracts)]
    for key, expected in (("scientific_questions", questions), ("observation_contracts", contracts),
                          ("discrimination_requirements", requirements), ("channel_eligibility", eligibility)):
        if bundle[key] != expected: raise ValueError(f"retained {key} is semantically inconsistent")
    emap = {e["eligibility_id"]: e for e in eligibility}
    for m in bundle["measurement_value_records"]: validate_measurement_linkage(m, emap.get(m["eligibility_id"]))
    predictions = {p["prediction_id"]: p for p in bundle["prediction_intervals"]}
    for m in bundle["measurement_value_records"]:
        left=predictions.get(m["left_prediction_id"]); right=predictions.get(m["right_prediction_id"])
        expected=discriminate(None if left is None else (left["lower_bound"],left["upper_bound"]), None if right is None else (right["lower_bound"],right["upper_bound"]), m["declared_measurement_uncertainty"])
        if expected!="UNSUPPORTED" and ((left and left["missing_uncertainty_flags"]) or (right and right["missing_uncertainty_flags"])): expected="NOT_ADJUDICATED_MISSING_UNCERTAINTY"
        if m["classification"] != expected: raise ValueError("retained measurement classification is inconsistent")
    edges=[x.to_dict() for x in build_coverage_edges(bundle["measurement_value_records"],eligibility)]
    matrix=coverage_matrix(requirements,edges); minimum=minimum_measurement_sets(requirements,edges)
    if bundle["coverage_edges"]!=edges or bundle["coverage_matrix"]!=matrix or bundle["minimum_measurement_sets"]!=minimum:
        raise ValueError("retained coverage or minimum sets are semantically inconsistent")
    specs=[x.to_dict() for x in canonical_apparatus_gate_specs()]
    evidence,results,apparatus=evaluate_apparatus(bundle["explanations"],requirements,bundle["measurement_value_records"],specs,bundle["matched_comparisons"],bundle["prediction_intervals"],contracts)
    if bundle["apparatus_gate_specs"]!=specs or bundle["apparatus_gate_evidence"]!=[x.to_dict() for x in evidence] or bundle["apparatus_gate_results"]!=[x.to_dict() for x in results] or bundle["apparatus_evaluation"]!=apparatus.to_dict():
        raise ValueError("retained apparatus artifacts are semantically inconsistent")
    independent_evidence,independent_results,independent_apparatus=reconstruct_apparatus(
        bundle["explanations"],requirements,bundle["measurement_value_records"],specs,
        bundle["matched_comparisons"],bundle["prediction_intervals"],contracts)
    if (bundle["apparatus_gate_evidence"]!=[x.to_dict() for x in independent_evidence] or
        bundle["apparatus_gate_results"]!=[x.to_dict() for x in independent_results] or
        bundle["apparatus_evaluation"]!=independent_apparatus.to_dict()):
        raise ValueError("independent apparatus reconstruction disagrees")
    expected_decision=derive_scientific_decision(explanations=bundle["explanations"],requirements=requirements,channel_eligibility=eligibility,component_reports=bundle["component_reports"],comparison_records=bundle["matched_comparisons"],measurement_records=bundle["measurement_value_records"],coverage_edges=edges,minimum_measurement_sets=minimum,apparatus_gate_specs=specs,apparatus_gate_results=[x.to_dict() for x in results],apparatus_evaluation=apparatus.to_dict())
    if decision != expected_decision: raise ValueError("retained decision is inconsistent with scientific inputs")
    if decision.selected_outcome != independently_select(bundle["explanations"],
            bundle["measurement_value_records"],minimum,independent_apparatus.to_dict()):
        raise ValueError("independent decision reconstruction disagrees")
    expected_counts=_summary_counts(bundle["explanations"],questions,requirements,eligibility,bundle["measurement_value_records"],edges,results,bundle["result_cells"])
    if bundle["summary_counts"] != expected_counts: raise ValueError("retained summary counts are inconsistent")
    return True


def _summary_counts(explanations, questions, requirements, eligibility, measurements, edges, gates, cells):
    return {"explanations":len(explanations), "scientific_questions":len(questions),
            "relevant_questions":sum(q["relevance_status"]=="RELEVANT" for q in questions),
            "excluded_questions":dict(sorted(Counter(q["relevance_status"] for q in questions if q["relevance_status"]!="RELEVANT").items())),
            "discrimination_requirements":len(requirements),
            "relevant_requirements":sum(r["relevance_status"]=="RELEVANT" for r in requirements),
            "channel_eligibility":len(eligibility), "eligible_records":sum(e["eligibility"]=="eligible" for e in eligibility),
            "eligible_pairs":sum(e["eligibility"]=="eligible" for e in eligibility),
            "measurement_records":len(measurements), "coverage_edges":len(edges),
            "covered_requirements":len({e["requirement_id"] for e in edges}),
            "measurement_classifications":dict(sorted(Counter(m["classification"] for m in measurements).items())),
            "apparatus_gate_results":len(gates), "apparatus_gate_statuses":dict(sorted(Counter(g["status"] for g in gates).items())),
            "support_states":dict(sorted(Counter(c["support_status"] for c in cells).items())),
            "result_cells":len(cells), "numerical_failures":sum(c["support_status"]=="NUMERICAL_FAILURE" for c in cells)}


def build_bundle(*, execution_commit=None, execution_tree=None):
    validate_protocol()
    cases = _load(INPUT / "case_matrix.json")["cases"]
    assumptions = _load(INPUT / "measurement_assumptions.json")
    registry_hash = sha256(ROOT / "puckworks/models/__init__.py")
    card_paths = {"foster2025_2.md": ROOT / "docs/cards/foster2025_2.md",
                  "wadsworth2026.md": ROOT / "docs/cards/wadsworth2026.md",
                  "wadsworth2026_inertial.md": ROOT / "docs/cards/wadsworth2026_inertial.md",
                  "wadsworth2026_grindmap.md": ROOT / "docs/cards/wadsworth2026_grindmap.md",
                  "cameron2020.md": ROOT / "docs/cards/cameron2020.md"}
    cards = {name: sha256(path) for name, path in card_paths.items()}
    cam_cells, cam_report, cam_evals = _cameron_results(cases)
    foster_cells, foster_report, foster_evals = _foster_results()
    wads_cells, wads_report, residual, wads_evals = _wadsworth_results(cases)
    cells = sorted(cam_cells + foster_cells + wads_cells,
                   key=lambda x: (x.component_id, x.case_id, x.observable))
    explanations = _explanations(registry_hash, cards)
    question_objs=canonical_scientific_questions([x.to_dict() for x in explanations]); questions=[x.to_dict() for x in question_objs]
    contract_objs=canonical_observation_contracts(questions); contracts=[x.to_dict() for x in contract_objs]
    requirement_objs=build_requirements(questions,contracts); requirements=[x.to_dict() for x in requirement_objs]
    pairs=build_channel_eligibility(questions,requirements,contracts)
    eligible = [p for p in pairs if p.eligibility == "eligible"]
    predictions, measurements = _derive_measurements(eligible, cells, assumptions, explanations)
    pair_dicts = [x.to_dict() for x in pairs]
    measurement_dicts = [x.to_dict() for x in measurements]
    edges = [x.to_dict() for x in build_coverage_edges(measurement_dicts, pair_dicts)]
    coverage = coverage_matrix(requirements,edges)
    minimum = minimum_measurement_sets(requirements, edges)
    component_reports = {"cameron2020.extraction_bdf": cam_report,
                         "foster2025.machine_mode": foster_report,
                         "wadsworth2026.inertial": wads_report}
    gate_specs = [x.to_dict() for x in canonical_apparatus_gate_specs()]
    gate_evidence_obj, gate_results_obj, apparatus_obj = evaluate_apparatus(
        [x.to_dict() for x in explanations], requirements, measurement_dicts, gate_specs,
        pair_dicts, [x.to_dict() for x in predictions], contracts)
    gate_evidence=[x.to_dict() for x in gate_evidence_obj]
    gate_results = [x.to_dict() for x in gate_results_obj]
    apparatus = apparatus_obj.to_dict()
    decision = derive_scientific_decision(
        explanations=[x.to_dict() for x in explanations], requirements=requirements,
        channel_eligibility=pair_dicts,
        component_reports=component_reports, comparison_records=pair_dicts,
        measurement_records=measurement_dicts, coverage_edges=edges,
        minimum_measurement_sets=minimum, apparatus_gate_specs=gate_specs,
        apparatus_gate_results=gate_results, apparatus_evaluation=apparatus)
    execution_commit = execution_commit or _git("rev-parse", "HEAD")
    execution_tree = execution_tree or _git("rev-parse", "HEAD^{tree}")
    evaluation_count = cam_evals + foster_evals + wads_evals
    manifest = {"schema_version": SCHEMA_VERSION, "programme_protocol_version": "sci-md-003-rp-a-001/c1-r3",
                "component_response_atlas_spec_sha256": sha256(ROOT / "docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md"),
                "c1_protocol_sha256": sha256(INPUT / "correction_protocol.json"),
                "c1_r1_protocol_sha256": sha256(R1 / "correction_protocol.json"),
                "c1_r2_protocol_sha256": sha256(R2 / "correction_protocol.json"),
                "protocol_sha256": sha256(OUT / "correction_protocol.json"),
                "case_matrix_sha256": sha256(INPUT / "case_matrix.json"),
                "measurement_assumption_sha256": sha256(INPUT / "measurement_assumptions.json"),
                "execution_code_commit": execution_commit, "execution_code_tree": execution_tree,
                "repository": "https://github.com/trbrewer/puckworks.git", "registry_snapshot_sha256": registry_hash,
                "selected_card_sha256": cards, "adapter_versions": ADAPTER_VERSIONS,
                "selected_components": ["foster2025.machine_mode", "wadsworth2026.inertial", "cameron2020.extraction_bdf"],
                "deterministic_seed": 20260820, "evaluation_count": evaluation_count,
                "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                "decision_rule_version": RULE_VERSION, "coverage_rule_version": COVERAGE_VERSION,
                "scientific_question_registry_version":QUESTION_VERSION,"requirement_rule_version":REQUIREMENT_VERSION,
                "observation_contract_version":OBSERVATION_VERSION,"semantic_validation_version":SEMANTIC_VERSION,
                "apparatus_gate_contract_version": APPARATUS_VERSION,
                "execution_completeness": "COMPLETE_BOUNDED_C1_R3_PILOT", "numerical_failures": 0,
                "support_state_vocabulary": [s.value for s in __import__("puckworks.analysis.response_atlas.schema", fromlist=["SupportStatus"]).SupportStatus],
                "frozen_status": "FROZEN", "claim_ceiling": CLAIM}
    bundle = {"schema_version": SCHEMA_VERSION, "run_manifest": manifest,
              "quantity_inventory": inventory(), "result_cells": [x.to_dict() for x in cells],
              "explanations": [x.to_dict() for x in explanations],
              "component_reports": component_reports,
              "scientific_questions":questions,"observation_contracts":contracts,
              "channel_eligibility": pair_dicts,
              "discrimination_requirements": requirements,
              "matched_comparisons": pair_dicts,
              "prediction_intervals": [x.to_dict() for x in predictions],
              "residual_records": [residual.to_dict()],
              "measurement_value_records": measurement_dicts,
              "coverage_edges": edges,
              "coverage_matrix": coverage,
              "minimum_measurement_sets": minimum,
              "apparatus_gate_specs": gate_specs,
              "apparatus_gate_evidence":gate_evidence,
              "apparatus_gate_results": gate_results,
              "apparatus_evaluation": apparatus,
              "measurement_assumptions": assumptions,
              "summary_counts": _summary_counts([x.to_dict() for x in explanations],questions,requirements,pair_dicts,measurement_dicts,edges,gate_results,[x.to_dict() for x in cells]),
              "decision": decision.to_dict()}
    validate_bundle(_load_bytes(canonical_bytes(bundle)))
    return bundle


def _load_bytes(data):
    return json.loads(data.decode("utf-8"))


def _artifact_map(bundle):
    return {
        "schema.json": {"schema_version": SCHEMA_VERSION,
                        "decision_rule_version": RULE_VERSION,
                        "coverage_rule_version": COVERAGE_VERSION,
                        "apparatus_gate_contract_version": APPARATUS_VERSION,
                        "scientific_question_registry_version":QUESTION_VERSION,
                        "requirement_rule_version":REQUIREMENT_VERSION,
                        "observation_contract_version":OBSERVATION_VERSION,
                        "semantic_validation_version":SEMANTIC_VERSION,
                        "support_states": bundle["run_manifest"]["support_state_vocabulary"],
                        "comparability_levels": [1, 2, 3, 4, 5]},
        "case_matrix.json": _load(INPUT / "case_matrix.json"),
        "measurement_assumptions.json": bundle["measurement_assumptions"],
        "quantity_inventory.json": bundle["quantity_inventory"],
        "explanation_registry.json": bundle["explanations"],
        "scientific_questions.json":bundle["scientific_questions"],
        "observation_contracts.json":bundle["observation_contracts"],
        "channel_eligibility.json": bundle["channel_eligibility"],
        "discrimination_requirements.json": bundle["discrimination_requirements"],
        "run_manifest.json": bundle["run_manifest"],
        "component_reports/index.json": bundle["component_reports"],
        "matched_comparisons.json": bundle["matched_comparisons"],
        "residual_decomposition.json": bundle["residual_records"],
        "measurement_value.json": {"records": bundle["measurement_value_records"], "summary": bundle["summary_counts"]},
        "prediction_intervals.json": bundle["prediction_intervals"],
        "coverage_edges.json": bundle["coverage_edges"],
        "coverage_matrix.json": bundle["coverage_matrix"],
        "minimum_measurement_sets.json": bundle["minimum_measurement_sets"],
        "apparatus_gate_spec.json": bundle["apparatus_gate_specs"],
        "apparatus_gate_evidence.json":bundle["apparatus_gate_evidence"],
        "apparatus_gate_results.json": bundle["apparatus_gate_results"],
        "apparatus_evaluation.json": bundle["apparatus_evaluation"],
        "summary_counts.json":bundle["summary_counts"],
        "DECISION.json": bundle["decision"], "atlas_export.json": bundle}


def generate_bundle(*, execution_commit=None, execution_tree=None):
    started = time.perf_counter()
    bundle = build_bundle(execution_commit=execution_commit, execution_tree=execution_tree)
    for rel, obj in _artifact_map(bundle).items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, obj)
    (OUT / "atlas_export.sha256").write_text(sha256(OUT / "atlas_export.json") + "  atlas_export.json\n", encoding="utf-8")
    write_json(OUT / "runtime.json", {"runtime_schema": "rp-a-001-c1-r3-runtime/v1",
                                      "wall_time_seconds": round(time.perf_counter() - started, 6),
                                      "normalized_for_scientific_verification": ["wall_time_seconds"]})
    return bundle


def verify_bundle():
    retained = _load(OUT / "atlas_export.json")
    validate_bundle(retained)
    manifest = retained["run_manifest"]
    expected = build_bundle(execution_commit=manifest["execution_code_commit"],
                            execution_tree=manifest["execution_code_tree"])
    bad = []
    for rel, obj in _artifact_map(expected).items():
        path = OUT / rel
        if not path.exists() or path.read_bytes() != canonical_bytes(obj):
            bad.append(rel)
    expected_hash = sha256(OUT / "atlas_export.json")
    recorded = (OUT / "atlas_export.sha256").read_text(encoding="utf-8").split()[0]
    if expected_hash != recorded:
        bad.append("atlas_export.sha256")
    if bad:
        raise ValueError("artifact drift: " + ", ".join(bad))
    return True

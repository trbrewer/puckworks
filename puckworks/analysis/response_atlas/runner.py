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
from .compare import minimal_sets
from .decision import RULE_VERSION, derive_scientific_decision
from .inventory import inventory
from .measurement_value import build_measurement_record
from .schema import (ComparisonEligibilityRecord, DecisionRecord, ExplanationRecord,
                     MeasurementValueRecord, PredictionIntervalRecord, QuantityRow,
                     ResidualRecord, ResultCell)

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "docs/analysis/rp_a_001"
INPUT = BASE / "c1"
OUT = BASE / "c1_r1"
SCHEMA_VERSION = "puckworks.response-atlas-export/v3"
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
    r1 = _load(OUT / "correction_protocol.json")
    cases = _load(INPUT / "case_matrix.json")
    if base["programme_protocol_version"] != "sci-md-003-rp-a-001/v1":
        raise ValueError("base protocol changed")
    if c1["programme_protocol_version"] != "sci-md-003-rp-a-001/c1":
        raise ValueError("wrong C1 protocol")
    if c1["schema_version"] != "puckworks.response-atlas-export/v2":
        raise ValueError("wrong preserved C1 export schema")
    if r1["programme_protocol_version"] != "sci-md-003-rp-a-001/c1-r1" or r1["schema_version"] != SCHEMA_VERSION:
        raise ValueError("wrong C1-R1 protocol or export schema")
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
    return [ComparisonEligibilityRecord(pid, left, right, "bounded common-observable response", scenario,
                                        channel, "NOT_COMMON" if level > 2 else "SAME_PRODUCER_REFERENCE",
                                        "NOT_COMMON" if level > 2 else "superficial velocity m/s", level, role,
                                        eligibility, reason, "NONE", "NONE", False,
                                        f"ELIG__{pid}__{scenario}__{channel}")
            for pid, left, right, scenario, channel, level, role, eligibility, reason in raw]


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
    if bundle.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("wrong response-atlas export schema")
    for row in bundle["quantity_inventory"]:
        QuantityRow.from_dict(row)
    for cell in bundle["result_cells"]:
        ResultCell.from_dict(cell)
    for row in bundle["explanations"]:
        ExplanationRecord.from_dict(row)
    for row in bundle["pair_eligibility"]:
        ComparisonEligibilityRecord.from_dict(row)
    for row in bundle["prediction_intervals"]:
        PredictionIntervalRecord.from_dict(row)
    for row in bundle["measurement_value_records"]:
        MeasurementValueRecord.from_dict(row)
    for row in bundle["residual_records"]:
        ResidualRecord.from_dict(row)
    decision = DecisionRecord.from_dict(bundle["decision"])
    eligible = [p for p in bundle["pair_eligibility"] if p["eligibility"] == "eligible"]
    if decision.eligible_pair_count != len(eligible):
        raise ValueError("decision eligible-pair count is inconsistent")
    robust = [r["measurement_record_id"] for r in bundle["measurement_value_records"] if r["robustly_covers_pair"]]
    if decision.robust_measurement_record_ids != robust:
        raise ValueError("decision robust-record inputs are inconsistent")
    eligibility = {p["eligibility_id"]: p for p in bundle["pair_eligibility"]}
    for record in bundle["measurement_value_records"]:
        match = eligibility.get(record["eligibility_id"])
        if match is None or (match["pair_id"], match["scenario"], match["candidate_observable"], match["comparability_level"]) != (record["pair_id"], record["scenario"], record["channel"], record["comparability_level"]):
            raise ValueError("measurement record lacks exact channel eligibility")
    measurement_ids = {r["measurement_record_id"] for r in bundle["measurement_value_records"]}
    pair_ids = {p["pair_id"] for p in bundle["pair_eligibility"]}
    if not set(decision.robust_measurement_record_ids + decision.unresolved_or_missing_uncertainty_record_ids) <= measurement_ids:
        raise ValueError("decision cites nonexistent measurement evidence")
    if not set(decision.qualifying_comparison_record_ids) <= pair_ids:
        raise ValueError("decision cites nonexistent comparison evidence")
    expected = derive_scientific_decision(
        explanations=bundle["explanations"], pair_eligibility=bundle["pair_eligibility"],
        component_reports=bundle["component_reports"], comparison_records=bundle["matched_comparisons"],
        measurement_records=bundle["measurement_value_records"], coverage_records=bundle["coverage_matrix"],
        minimum_measurement_sets=bundle["minimum_measurement_sets"])
    if decision != expected:
        raise ValueError("retained decision is inconsistent with scientific inputs")
    return True


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
    pairs = _pairs()
    eligible = [p for p in pairs if p.eligibility == "eligible"]
    predictions, measurements = _derive_measurements(eligible, cells, assumptions, explanations)
    coverage = [{"channel": ch,
                 "robustly_covered_pair_ids": sorted(r.pair_id for r in measurements if r.channel == ch and r.robustly_covers_pair),
                 "robust_measurement_record_ids": sorted(r.measurement_record_id for r in measurements if r.channel == ch and r.robustly_covers_pair)} for ch in CHANNELS]
    sets = minimal_sets({p.pair_id for p in eligible}, {row["channel"]: set(row["robustly_covered_pair_ids"]) for row in coverage})
    zero_status = "NO_ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM" if not eligible else "ELIGIBLE_PAIRWISE_DISCRIMINATION_PROBLEM_PRESENT"
    minimum = {"eligible_pair_ids": [x.pair_id for x in eligible],
               "zero_pair_status": zero_status, "result": sets}
    component_reports = {"cameron2020.extraction_bdf": cam_report,
                         "foster2025.machine_mode": foster_report,
                         "wadsworth2026.inertial": wads_report}
    pair_dicts = [x.to_dict() for x in pairs]
    measurement_dicts = [x.to_dict() for x in measurements]
    decision = derive_scientific_decision(
        explanations=[x.to_dict() for x in explanations], pair_eligibility=pair_dicts,
        component_reports=component_reports, comparison_records=pair_dicts,
        measurement_records=measurement_dicts, coverage_records=coverage,
        minimum_measurement_sets=minimum)
    execution_commit = execution_commit or _git("rev-parse", "HEAD")
    execution_tree = execution_tree or _git("rev-parse", "HEAD^{tree}")
    evaluation_count = cam_evals + foster_evals + wads_evals
    manifest = {"schema_version": SCHEMA_VERSION, "programme_protocol_version": "sci-md-003-rp-a-001/c1-r1",
                "component_response_atlas_spec_sha256": sha256(ROOT / "docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md"),
                "c1_protocol_sha256": sha256(INPUT / "correction_protocol.json"),
                "protocol_sha256": sha256(OUT / "correction_protocol.json"),
                "case_matrix_sha256": sha256(INPUT / "case_matrix.json"),
                "measurement_assumption_sha256": sha256(INPUT / "measurement_assumptions.json"),
                "execution_code_commit": execution_commit, "execution_code_tree": execution_tree,
                "repository": "https://github.com/trbrewer/puckworks.git", "registry_snapshot_sha256": registry_hash,
                "selected_card_sha256": cards, "adapter_versions": ADAPTER_VERSIONS,
                "selected_components": ["foster2025.machine_mode", "wadsworth2026.inertial", "cameron2020.extraction_bdf"],
                "deterministic_seed": 20260820, "evaluation_count": evaluation_count,
                "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
                "execution_completeness": "COMPLETE_BOUNDED_C1_R1_PILOT", "numerical_failures": 0,
                "support_state_vocabulary": [s.value for s in __import__("puckworks.analysis.response_atlas.schema", fromlist=["SupportStatus"]).SupportStatus],
                "frozen_status": "FROZEN", "claim_ceiling": CLAIM}
    bundle = {"schema_version": SCHEMA_VERSION, "run_manifest": manifest,
              "quantity_inventory": inventory(), "result_cells": [x.to_dict() for x in cells],
              "explanations": [x.to_dict() for x in explanations],
              "component_reports": component_reports,
              "pair_eligibility": pair_dicts,
              "channel_eligibility": pair_dicts,
              "matched_comparisons": pair_dicts,
              "prediction_intervals": [x.to_dict() for x in predictions],
              "residual_records": [residual.to_dict()],
              "measurement_value_records": measurement_dicts,
              "coverage_matrix": coverage,
              "minimum_measurement_sets": minimum,
              "measurement_assumptions": assumptions,
              "summary_counts": {"explanations": len(explanations), "pair_eligibility": len(pairs),
                                 "channel_eligibility": len(pairs),
                                 "eligible_pairs": len(eligible), "measurement_records": len(measurements),
                                 "measurement_classifications": dict(sorted(Counter(x.classification for x in measurements).items())),
                                 "support_states": dict(sorted(Counter(x.support_status for x in cells).items())),
                                 "comparability_levels": dict(sorted(Counter(str(x.comparability_level) for x in pairs).items())),
                                 "result_cells": len(cells)},
              "decision": decision.to_dict()}
    validate_bundle(_load_bytes(canonical_bytes(bundle)))
    return bundle


def _load_bytes(data):
    return json.loads(data.decode("utf-8"))


def _artifact_map(bundle):
    return {
        "schema.json": {"schema_version": SCHEMA_VERSION,
                        "decision_rule_version": RULE_VERSION,
                        "support_states": bundle["run_manifest"]["support_state_vocabulary"],
                        "comparability_levels": [1, 2, 3, 4, 5]},
        "case_matrix.json": _load(INPUT / "case_matrix.json"),
        "measurement_assumptions.json": bundle["measurement_assumptions"],
        "quantity_inventory.json": bundle["quantity_inventory"],
        "explanation_registry.json": bundle["explanations"],
        "pair_eligibility.json": bundle["pair_eligibility"],
        "channel_eligibility.json": bundle["channel_eligibility"],
        "run_manifest.json": bundle["run_manifest"],
        "component_reports/index.json": bundle["component_reports"],
        "matched_comparisons.json": bundle["matched_comparisons"],
        "residual_decomposition.json": bundle["residual_records"],
        "measurement_value.json": {"records": bundle["measurement_value_records"], "summary": bundle["summary_counts"]},
        "coverage_matrix.json": bundle["coverage_matrix"],
        "minimum_measurement_sets.json": bundle["minimum_measurement_sets"],
        "DECISION.json": bundle["decision"], "atlas_export.json": bundle}


def generate_bundle(*, execution_commit=None, execution_tree=None):
    started = time.perf_counter()
    bundle = build_bundle(execution_commit=execution_commit, execution_tree=execution_tree)
    for rel, obj in _artifact_map(bundle).items():
        path = OUT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, obj)
    (OUT / "atlas_export.sha256").write_text(sha256(OUT / "atlas_export.json") + "  atlas_export.json\n", encoding="utf-8")
    write_json(OUT / "runtime.json", {"runtime_schema": "rp-a-001-c1-r1-runtime/v1",
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

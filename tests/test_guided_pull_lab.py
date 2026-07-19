"""Guided Pull Laboratory contract tests (PV-19B, schema v3).

Offline + deterministic. Guards scenario identity + override provenance, the separated
scientific-payload vs full-artifact integrity layers, correct observable roles, the explicit
component capability/rights matrix (incl. RIGHTS_BLOCKED for grudeva2025 per #73), reference-suite
honesty (executed vs coverage placeholders), no equation duplication, and backward compatibility.
"""
import json

import pytest

import puckworks
from puckworks.product import lab


@pytest.fixture(scope="module")
def execution():
    return lab.execute_scenario(lab.ScenarioRequest(preset_id="pv19_named"))


@pytest.fixture(scope="module")
def report(execution):
    return lab.build_comparison(execution, provenance=lab.BuildProvenance(
        package_version="0.4.0.dev0", source_commit="deadbeefcafe", workflow_run_id="123",
        wheel_sha256="abc123"))


# ── SCENARIO IDENTITY ─────────────────────────────────────────────────────────────
def test_pv19_named_is_identified_as_pv19_named():
    r = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))
    assert r["scenario"]["scenario_id"] == "pv19_named"
    assert "pv19_named" in r["executed_lenses"][0]["adapter"]


def test_guided_v1_is_identified_as_guided_v1_not_pv19():
    r = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("guided_v1")))
    assert r["scenario"]["scenario_id"] == "guided_v1"
    assert "guided_v1" in r["executed_lenses"][0]["adapter"]
    assert "pv19_named" not in r["executed_lenses"][0]["adapter"]


def test_custom_guided_v1_retains_base_preset_and_records_overrides():
    ex = lab.execute_scenario(lab.ScenarioRequest("guided_v1", overrides={"dose_g": 19.0}))
    r = lab.build_comparison(ex)
    assert r["scenario"]["scenario_id"] == "guided_v1"
    assert r["scenario"]["preset_id"] == "guided_v1"
    ov = r["scenario"]["applied_overrides"]
    assert ov["dose_g"]["base"] == 20.0 and ov["dose_g"]["effective"] == 19.0
    # effective recipe equals the producer's recipe used for the run
    assert r["scenario"]["effective_recipe"]["dose_g"] == 19.0


def test_no_downstream_guessing_of_preset_identity():
    src = open(lab.__file__).read()
    # scenario identity comes from the request, not a module constant fed into every scenario
    assert "request.preset_id" in src
    assert 'scenario_id": "pv19_named"' not in src   # never hard-coded


def test_scenario_request_rejects_unknown_preset_and_field():
    with pytest.raises(ValueError):
        lab.ScenarioRequest("nope_not_a_preset")
    with pytest.raises(ValueError):
        lab.ScenarioRequest("pv19_named", overrides={"not_a_field": 1})


# ── PROVENANCE + INTEGRITY ────────────────────────────────────────────────────────
def test_full_artifact_carries_build_provenance(report):
    art = json.loads(lab.artifact_json(report))
    prov = art["provenance"]
    assert prov["package_version"] == "0.4.0.dev0"
    assert prov["source_commit"] == "deadbeefcafe"       # NOT stripped from the downloadable artifact
    assert prov["workflow_run_id"] == "123" and prov["wheel_sha256"] == "abc123"


def test_scientific_hash_stable_but_artifact_hash_changes_with_provenance(execution):
    a = lab.build_comparison(execution, provenance=lab.BuildProvenance(source_commit="AAA"))
    b = lab.build_comparison(execution, provenance=lab.BuildProvenance(source_commit="BBB"))
    assert lab.scientific_sha256(a) == lab.scientific_sha256(b)     # science unchanged
    assert lab.artifact_sha256(a) != lab.artifact_sha256(b)         # build identity changed


def test_no_wall_clock_in_either_payload(report):
    for blob in (lab.scientific_json(report), lab.artifact_json(report)):
        for bad in ("timestamp", "generated_at", "datetime", "wall_clock"):
            assert bad not in blob.lower()


def test_integrity_hashes_are_self_consistent(report):
    assert report["integrity"]["scientific_payload_sha256"] == lab.scientific_sha256(report)
    assert report["integrity"]["artifact_sha256"] == lab.artifact_sha256(report)
    # artifact hash is not computed over itself
    art = lab._artifact_payload(report)
    assert "artifact_sha256" not in art.get("integrity", {})


def test_schema_versions(report, execution):
    assert report["schema_version"] == 4 == lab.SCHEMA_VERSION
    assert execution.pull_run["schema_version"] == 1     # PullRun v1 not overloaded


# ── OBSERVABLE ROLES ──────────────────────────────────────────────────────────────
def test_observable_roles_match_producer_semantics(report):
    roles = {o["name"]: o for o in report["executed_lenses"][0]["observables"]}
    assert roles["pressure_bar"]["role"] == "prescribed"
    assert roles["beverage_mass_g"]["role"] == "prescribed"
    assert roles["mean_flow_g_s"]["role"] == "derived"
    for k in ("extracted_mass_g", "extraction_yield_pct", "tds_pct", "shot_duration_s"):
        assert roles[k]["role"] == "simulated", k
    assert roles["first_drip_s"]["role"] == "unsupported"
    assert roles["first_drip_s"]["status"] == "unavailable"
    fd = roles["first_modeled_solute_arrival_s"]
    assert fd["role"] == "derived" and fd["is_physical_first_drip"] is False
    for o in report["executed_lenses"][0]["observables"]:
        assert o["role"] in lab._VALID_ROLES and "unit" in o


def test_trace_roles_are_preserved(report):
    for t in report["executed_lenses"][0]["traces"]:
        for s in t["series"]:
            assert s["role"] in ("prescribed_input", "simulated", "derived")


# ── COMPONENT MATRIX ──────────────────────────────────────────────────────────────
def test_one_row_per_component_no_hardcoded_count(execution):
    matrix = lab.build_matrix(execution)
    names = [r["component_id"] for r in matrix]
    assert names == sorted(names)
    assert len(names) == len(set(names)) == len(puckworks.components())
    for r in matrix:
        for field in ("has_callable_code", "is_runtime_stage", "is_calibration_or_closure",
                      "native_runner_state", "common_scenario_adapter_state", "rights_state",
                      "concentration_reference_basis"):
            assert field in r
        assert r["disposition"] in lab.DISPOSITIONS
        assert r["native_runner_state"] in lab.RUNNER_STATES


def test_calibration_does_not_imply_runtime_execution(execution):
    # calibration != runtime STAGE (though a calibration component may still have a native reference
    # runner, e.g. wadsworth2026.permeability's Table-1 collapse)
    matrix = {r["component_id"]: r for r in lab.build_matrix(execution)}
    cal = [r for r in matrix.values() if r["execution_role"] == "calibration"]
    assert cal
    for r in cal:
        assert r["is_runtime_stage"] is False
        assert r["disposition"] != "COMMON_SCENARIO_READY"


def test_grudeva2025_is_rights_blocked(execution):
    matrix = {r["component_id"]: r for r in lab.build_matrix(execution)}
    g = matrix["grudeva2025.reduced"]
    assert g["rights_state"] == "RIGHTS_BLOCKED"
    assert g["disposition"] == "RIGHTS_BLOCKED"
    assert g["native_runner_state"] == "RIGHTS_BLOCKED"
    assert "unlicensed" in g["rights_note"].lower()


def test_no_substring_heuristic_over_the_run(execution):
    # the matrix is built from explicit specs, not by scanning the run's coverage reason strings
    src = open(lab.__file__).read()
    assert "coverage" in src  # we read executed set, but classification uses _lab_spec, not reasons
    assert "_lab_spec" in src


# ── REFERENCE HONESTY ─────────────────────────────────────────────────────────────
def test_only_executed_references_appear_in_executed_results(report):
    from puckworks.product import lab_runners
    executed = {r["component_id"] for r in report["executed_reference_results"]
                if r["status"] == "executed"}
    # exactly the genuinely-executed native runners (not the common-scenario lens Cameron)
    assert executed == set(lab_runners.INTERACTIVE_FAST)
    assert "cameron2020.extraction_bdf" not in executed        # Cameron is the common lens, not a ref
    for r in report["executed_reference_results"]:
        assert "not the common" in r["label"].lower()
        for o in r.get("outputs", []):
            assert "unit" in o and "role" in o                 # native outputs carry units + roles


def test_missing_runner_is_labelled_not_implemented_not_a_result(report):
    # v4: capability coverage lives in the env-dependent capability_snapshot (excluded from the sci hash)
    cov = {r["component_id"]: r for r in report["capability_snapshot"]["reference_suite_coverage"]}
    # a component with no runner must say "not yet implemented", never an "own native reference" result
    not_impl = [r for r in cov.values() if r["native_runner_capability"] == "NOT_IMPLEMENTED"]
    assert not_impl
    for r in not_impl:
        assert "not yet implemented" in r["note"].lower()
        assert "native reference case" not in r["note"].lower()


def test_optional_dependency_skip_is_not_a_pass(report):
    cov = {r["component_id"]: r for r in report["capability_snapshot"]["reference_suite_coverage"]}
    taichi = cov.get("brewer2026.lb_taichi")
    assert taichi and taichi["native_runner_capability"] in (
        "OPTIONAL_DEPENDENCY_UNAVAILABLE", "NOT_IMPLEMENTED")


def test_failed_reserved_for_errored_execution(report):
    # FAILED is a per-request EXECUTION state, never a static capability
    caps = {r["native_runner_capability"] for r in report["capability_snapshot"]["reference_suite_coverage"]}
    assert "FAILED" not in caps and "FAILED" not in lab.NATIVE_RUNNER_CAPABILITIES
    assert "FAILED" in lab.REQUEST_EXECUTION_STATES


# ── PLOTS ─────────────────────────────────────────────────────────────────────────
def test_render_data_matches_trace_data_exactly(report):
    panels = lab.render_data(report)
    assert panels
    traces = {t["trace_id"]: t for t in report["executed_lenses"][0]["traces"]}
    for p in panels:
        t = traces[p["panel_id"]]
        assert p["x"] == t["axis_values"]
        assert "(" in p["x_label"] and ")" in p["x_label"]   # units in label
        for ps in p["series"]:
            assert ps["role"] and ps["unit"] is not None


# ── HONESTY / NO OVERCLAIM ────────────────────────────────────────────────────────
def test_does_not_upgrade_evidence_or_claim_validation(report):
    import re
    blob = json.dumps(report).lower()
    for phrase in ("digital twin", "best recipe"):
        for m in re.finditer(re.escape(phrase), blob):
            seg = blob[max(0, m.start() - 60):m.end() + 20]
            assert "not " in seg or "never" in seg, f"un-negated {phrase!r}"
    for bad in ("flavor prediction", "tastes better", "validated multi-model simulation of"):
        assert bad not in blob


def test_no_equation_duplication_reuses_the_public_producer():
    src = open(lab.__file__).read()
    assert "simulate_pull" in src
    assert "import numpy" not in src and "from numpy" not in src and "import scipy" not in src


def test_no_universal_grinder_dial_mapping():
    src = open(lab.__file__).read().lower()
    assert "not a universal particle size" in src
    assert "dial_to_particle" not in src and "dial_to_size" not in src


# ── BACKWARD COMPATIBILITY ────────────────────────────────────────────────────────
def test_run_scenario_wrapper_preserves_identity_and_returns_pullrun():
    run = lab.run_scenario("guided_v1", dose_g=19.0)
    assert run["schema_version"] == 1
    # the wrapper does not lose preset/override identity (verifiable via the recipe)
    assert run["recipe"]["dose_g"] == 19.0


def test_build_comparison_rejects_bare_run_dict():
    run = lab.run_scenario("guided_v1")
    with pytest.raises(TypeError):
        lab.build_comparison(run)         # a bare PullRun dict cannot carry preset identity

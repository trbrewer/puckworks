"""Guided Pull Laboratory v4 — request semantics + layered cryptographic integrity (PV-19B, #70).

Offline + deterministic. Verifies the OPERATIONAL domain policy (strict blocks before the producer
runs; the producer is not called), real lens selection (unknown raises; non-executable surfaced, never
dropped; the executed count is derived), unambiguous reference selection (none/interactive_fast/selected;
unknown raises), capability-vs-per-request-execution separation, the three recomputed integrity layers
(scientific hash invariant to build identity AND optional-dependency installation), finite JSON
(NaN/Inf rejected), and tamper detection.
"""
import json

import pytest

import puckworks
from puckworks.product import lab


# ── operational domain policy ───────────────────────────────────────────────────────
def _out_of_range_override():
    # 20 bar is an evidence-range WARNING for pv19_named (not a hard rejection)
    return {"pressure_bar": 20.0}


def test_request_validates_policy_vocabularies():
    with pytest.raises(ValueError):
        lab.ScenarioRequest("pv19_named", domain_policy="loose")
    with pytest.raises(ValueError):
        lab.ScenarioRequest("pv19_named", reference_selection_policy="all")


def test_effective_config_carries_the_request_domain_policy():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", domain_policy="strict"))
    assert ex.effective_config["domain_policy"] == "strict"
    assert ex.effective_domain_policy == "strict"


def test_strict_policy_blocks_before_the_producer_runs(monkeypatch):
    import puckworks.product as prod
    called = {"n": 0}
    real = prod.simulate_pull
    monkeypatch.setattr(prod, "simulate_pull", lambda *a, **k: called.__setitem__("n", called["n"] + 1)
                        or real(*a, **k))
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", overrides=_out_of_range_override(),
                                                  domain_policy="strict"))
    assert ex.domain_blocked is True and ex.pull_run is None
    assert called["n"] == 0            # the scientific producer was NOT invoked when domain-blocked
    assert "out-of-range" in ex.domain_block_reason


def test_warn_policy_runs_the_same_out_of_range_input():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", overrides=_out_of_range_override(),
                                                  domain_policy="warn"))
    assert ex.domain_blocked is False and ex.pull_run is not None


def test_blocked_report_has_no_executed_lens_and_derived_count():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", overrides=_out_of_range_override(),
                                                  domain_policy="strict"))
    r = lab.build_comparison(ex)
    assert r["executed_lenses"] == []
    assert r["counts"]["executed_common_scenario_lenses"] == 0     # derived, not hard-coded to 1
    assert r["domain"]["blocked"] is True and r["domain"]["producer_executed"] is False
    cam = {ls["component_id"]: ls for ls in r["lens_selection"]}["cameron2020.extraction_bdf"]
    assert cam["lens_request_state"] == "REQUESTED_BUT_NOT_EXECUTABLE"     # surfaced, not dropped


# ── lens selection ──────────────────────────────────────────────────────────────────
def test_default_request_executes_the_cameron_common_lens():
    r = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))
    assert r["counts"]["executed_common_scenario_lenses"] == 1
    assert [ls for ls in r["lens_selection"] if ls["lens_request_state"] == "EXECUTED"][0][
        "component_id"] == "cameron2020.extraction_bdf"


def test_unknown_requested_lens_raises_not_silently_dropped():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", requested_lens_ids=("not.a.component",)))
    with pytest.raises(ValueError):
        lab.build_comparison(ex)


def test_requested_but_non_executable_lens_is_surfaced():
    # a real registered component with no common-scenario adapter is REQUESTED_BUT_NOT_EXECUTABLE
    other = next(c.name for c in puckworks.components()
                 if c.name not in ("cameron2020.extraction_bdf",))
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", requested_lens_ids=(other,)))
    r = lab.build_comparison(ex)
    rec = {ls["component_id"]: ls for ls in r["lens_selection"]}[other]
    assert rec["lens_request_state"] == "REQUESTED_BUT_NOT_EXECUTABLE"
    assert r["counts"]["executed_common_scenario_lenses"] == 0


# ── reference selection (unambiguous) ───────────────────────────────────────────────
def test_reference_policy_none_executes_no_references():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", reference_selection_policy="none"))
    r = lab.build_comparison(ex)
    assert r["executed_reference_results"] == [] and r["reference_selection"] == []
    assert r["counts"]["executed_native_references"] == 0


def test_reference_policy_interactive_fast_runs_the_fast_set():
    from puckworks.product import lab_runners
    r = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))
    executed = {x["component_id"] for x in r["executed_reference_results"] if x["status"] == "executed"}
    assert executed == set(lab_runners.INTERACTIVE_FAST)
    for rec in r["reference_selection"]:
        assert rec["native_runner_execution_state"] == "EXECUTED"


def test_selected_policy_requires_ids_and_rejects_unknown():
    with pytest.raises(ValueError):                      # selected but nothing selected
        lab.ScenarioRequest("pv19_named", reference_selection_policy="selected")
    with pytest.raises(ValueError):                      # ids without the selected policy => ambiguous
        lab.ScenarioRequest("pv19_named", requested_reference_runner_ids=("waszkiewicz2025.poroelastic",))
    ex = lab.execute_scenario(lab.ScenarioRequest(
        "pv19_named", reference_selection_policy="selected",
        requested_reference_runner_ids=("not.a.runner",)))
    with pytest.raises(ValueError):                      # unknown id is not silently ignored
        lab.build_comparison(ex)


def test_selected_policy_runs_exactly_the_selected_runner():
    ex = lab.execute_scenario(lab.ScenarioRequest(
        "pv19_named", reference_selection_policy="selected",
        requested_reference_runner_ids=("waszkiewicz2025.poroelastic",)))
    r = lab.build_comparison(ex)
    executed = {x["component_id"] for x in r["executed_reference_results"] if x["status"] == "executed"}
    assert executed == {"waszkiewicz2025.poroelastic"}


# ── capability vs per-request execution state separation ────────────────────────────
def test_matrix_is_capability_only_execution_is_per_request():
    ex = lab.execute_scenario(lab.ScenarioRequest("pv19_named", reference_selection_policy="none"))
    r = lab.build_comparison(ex)
    row = {m["component_id"]: m for m in r["capability_snapshot"]["component_matrix"]}[
        "waszkiewicz2025.poroelastic"]
    assert row["native_runner_capability"] == "AVAILABLE"      # capability: a runner exists
    # ...but with policy=none nothing was executed for THIS request
    assert row["native_runner_capability"] in lab.NATIVE_RUNNER_CAPABILITIES
    assert r["reference_selection"] == []                      # per-request: none executed


# ── three integrity layers ──────────────────────────────────────────────────────────
def _report(**kw):
    return lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named", **kw)))


def test_three_hashes_present_and_self_consistent():
    r = _report()
    integ = r["integrity"]
    for k in ("scientific_payload_sha256", "capability_snapshot_sha256", "artifact_sha256"):
        assert integ[k]
    assert integ["scientific_payload_sha256"] == lab.compute_scientific_result_sha256(r)
    assert integ["capability_snapshot_sha256"] == lab.compute_capability_snapshot_sha256(r)
    assert integ["artifact_sha256"] == lab.compute_artifact_sha256(r)
    assert lab.verify_integrity(r)["ok"] is True


def test_scientific_hash_invariant_to_optional_dependency_installation(monkeypatch):
    # a Cameron-only request's science must not change when Taichi becomes importable (it only changes the
    # env-dependent capability snapshot). Simulate an installed optional dependency.
    base = _report(reference_selection_policy="none")
    monkeypatch.setattr(lab, "_optional_dep_available", lambda dep: True)
    withdep = _report(reference_selection_policy="none")
    assert lab.scientific_sha256(withdep) == lab.scientific_sha256(base)        # science unchanged
    assert lab.capability_snapshot_sha256(withdep) != lab.capability_snapshot_sha256(base)  # cap changed
    assert lab.artifact_sha256(withdep) != lab.artifact_sha256(base)            # artifact changed


def test_tamper_in_science_is_detected():
    r = _report()
    r["scenario"]["effective_recipe"]["dose_g"] = 999.0     # tamper with the science, keep old hash
    v = lab.verify_integrity(r)
    assert v["ok"] is False
    layers = {m["layer"] for m in v["mismatches"]}
    assert "scientific_payload_sha256" in layers and "artifact_sha256" in layers
    with pytest.raises(lab.IntegrityError):
        lab.verify_integrity(r, strict=True)


def test_tamper_in_capability_leaves_science_hash_intact():
    r = _report()
    r["capability_snapshot"]["dispositions"]["INJECTED"] = 1
    v = lab.verify_integrity(r)
    layers = {m["layer"] for m in v["mismatches"]}
    assert "capability_snapshot_sha256" in layers and "artifact_sha256" in layers
    assert "scientific_payload_sha256" not in layers        # the science hash is unaffected


def test_canonical_json_rejects_non_finite():
    r = _report()
    r["scenario"]["nan_field"] = float("nan")
    with pytest.raises(ValueError):
        lab.artifact_json(r)
    r["scenario"]["nan_field"] = float("inf")
    with pytest.raises(ValueError):
        lab.canonical_json(r)


def test_no_wall_clock_or_timestamp_in_any_layer():
    r = _report()
    for blob in (lab.scientific_json(r), lab.artifact_json(r),
                 lab._canonical(lab._capability_payload(r))):
        for bad in ("timestamp", "generated_at", "datetime", "wall_clock"):
            assert bad not in blob.lower()


def test_metadata_incomplete_fallback_does_not_invent_capability():
    class _Bare:
        name = "bogus.incomplete"
        execution_role = ""
        stage = ""
        kind = ""
        module = ""
        gates = ()
        provenance_class = ""
        evidence_strength = ""
        valid_range = None
    spec = lab._lab_spec(_Bare())
    assert spec.metadata_complete is False
    assert spec.disposition == "METADATA_INCOMPLETE"
    assert spec.native_runner_capability == "NOT_APPLICABLE"


def test_build_provenance_absent_fields_are_visible_not_hidden():
    r = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")),
                             provenance=lab.BuildProvenance(package_version="0.4.0.dev0"))
    prov = json.loads(lab.artifact_json(r))["provenance"]
    assert prov["source_commit"] is None and prov["workflow_run_id"] is None  # explicit null, present

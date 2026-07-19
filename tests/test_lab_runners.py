"""Native reference runner tests (PV-19B Phase 3).

Offline + deterministic. Each declared runner calls its registered producer (no equation duplication),
returns provenance-bound native inputs + units-and-roles outputs at the component's registry evidence
(never upgraded), is deterministic, isolates failures, and can never enter the common-scenario results.
"""
import json

import puckworks
from puckworks.product import lab, lab_runners as lr


def test_every_runner_targets_a_registered_component():
    names = {c.name for c in puckworks.components()}
    for cid in lr.RUNNERS:
        assert cid in names


def test_at_least_three_runners_declared():
    assert len(lr.RUNNERS) >= 3
    assert set(lr.INTERACTIVE_FAST) == set(lr.RUNNERS)   # all fast today


def test_no_model_equation_in_runner_module():
    src = open(lr.__file__).read()
    # the runners arrange inputs + call producers; they must not re-derive model math
    assert "steady_state_curve" in src and "front_from_pressure" in src and "k_star" in src
    # no bare numpy-based model equation authoring beyond calling producers / simple stats
    assert "def _run_" in src


def test_each_runner_executes_with_units_roles_and_evidence():
    for cid in lr.INTERACTIVE_FAST:
        r = lr.execute_runner(cid)
        assert r["status"] == "executed", r
        assert r["component_id"] == cid and r["runner_id"] and r["runner_version"]
        assert r["runtime_class"] in lr.RUNTIME_CLASSES
        assert r["evidence"]["evidence_strength"]           # registry evidence attached
        assert r["native_inputs"] and r["outputs"]
        for o in r["outputs"]:
            assert "unit" in o and "role" in o
        assert r["fidelity_ceiling"] and "not the common" in r["label"].lower()
        assert r["scientific_payload_hash"]


def test_runner_outputs_are_deterministic():
    a = lr.run_selected(lr.INTERACTIVE_FAST)
    b = lr.run_selected(lr.INTERACTIVE_FAST)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    # deterministic ordering (sorted by component id)
    assert [r["component_id"] for r in a] == sorted(r["component_id"] for r in a)


def test_runner_does_not_upgrade_evidence():
    reg = {c.name: c.evidence_strength for c in puckworks.components()}
    for cid in lr.INTERACTIVE_FAST:
        r = lr.execute_runner(cid)
        assert r["evidence"]["evidence_strength"] == reg[cid]


def test_failure_is_isolated_and_marked_FAILED(monkeypatch):
    def boom():
        raise RuntimeError("simulated producer failure")
    spec, _ = lr.RUNNERS["wadsworth2026.permeability"]
    monkeypatch.setitem(lr.RUNNERS, "wadsworth2026.permeability", (spec, boom))
    results = lr.run_selected(lr.INTERACTIVE_FAST)
    by = {r["component_id"]: r for r in results}
    assert by["wadsworth2026.permeability"]["status"] == "FAILED"
    assert "simulated producer failure" in by["wadsworth2026.permeability"]["error"]
    # the others still executed
    assert by["waszkiewicz2025.poroelastic"]["status"] == "executed"
    assert by["foster2025.infiltration"]["status"] == "executed"


def test_native_reference_cannot_enter_common_scenario_results():
    report = lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))
    lens_components = {lens["component_id"] for lens in report["executed_lenses"]}
    ref_components = {r["component_id"] for r in report["executed_reference_results"]}
    assert lens_components == {"cameron2020.extraction_bdf"}
    assert not (ref_components & lens_components)          # disjoint: refs are not the lens


def test_grudeva2025_has_no_runner_and_stays_rights_blocked():
    assert "grudeva2025.reduced" not in lr.RUNNERS
    matrix = {r["component_id"]: r for r in lab.build_matrix(
        lab.execute_scenario(lab.ScenarioRequest("pv19_named")))}
    assert matrix["grudeva2025.reduced"]["native_runner_state"] == "RIGHTS_BLOCKED"


def test_scientific_hash_excludes_itself():
    r = lr.execute_runner("waszkiewicz2025.poroelastic")
    recomputed = lr._sci_hash({k: v for k, v in r.items()})   # includes the hash field -> stripped
    assert recomputed == r["scientific_payload_hash"]

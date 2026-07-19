"""Native LB channel code-verification runner tests (#70).

`brewer2026.lb_reference` is the first native reference runner for a first-party SYNTHETIC
code-verification component: it solves the component's canonical plane channel and compares the lattice
permeability to the exact plane-Poiseuille k = h^2/12. The gate (gate_lb_channel) owns the pass/fail band;
the runner surfaces that verdict verbatim. This is code verification, not coffee/espresso validation.
"""
import json
import math

import pytest

import puckworks
from puckworks.models.brewer2026 import lb_reference as lb
from puckworks.product import lab_runners as lr

LB = "brewer2026.lb_reference"


def test_runner_registered_and_discoverable():
    assert lr.has_runner(LB)
    assert LB in lr.available_runners()
    spec, fn = lr.RUNNERS[LB]
    assert spec.component_id == LB and callable(fn)
    assert LB in {c.name for c in puckworks.components()}       # targets a registered component


def test_runtime_classification_is_batch_only_not_interactive_fast():
    # a genuine multi-second LB solve is honestly batch-only, never loosened to look interactive-fast
    assert lr.runtime_class(LB) == "batch-only"
    assert LB not in lr.INTERACTIVE_FAST


def test_valid_named_verification_run_executes():
    r = lr.execute_runner(LB)
    assert r["status"] == "executed" and r["execution_state"] == "EXECUTED"
    assert r["component_id"] == LB and r["runner_id"] == "lb_reference_channel"
    assert r["runtime_class"] == "batch-only"
    assert r["evidence"]["evidence_strength"]                    # registry evidence attached, not upgraded
    # native inputs are the scientifically meaningful, deterministic solver inputs (with units + provenance)
    names = {i["name"] for i in r["native_inputs"]}
    assert {"lattice_dimensions", "body_force_g", "relaxation_tau_plus", "max_iterations",
            "convergence_tolerance"} <= names
    for i in r["native_inputs"]:
        assert i["unit"] and i["provenance"]


def test_outputs_carry_units_and_semantic_roles_and_are_finite():
    r = lr.execute_runner(LB)
    by = {o["name"]: o for o in r["outputs"]}
    assert by["simulated_lattice_permeability"]["role"] == "simulated"
    assert by["analytic_plane_poiseuille_permeability"]["role"] == "analytic_reference"
    assert by["relative_error_pct"]["role"] == "derived"
    for o in r["outputs"]:
        assert o["unit"] and o["role"]
        v = o["value"]
        if isinstance(v, float):
            assert math.isfinite(v)


def test_runner_agrees_with_the_authoritative_gate_and_never_re_derives_the_threshold():
    r = lr.execute_runner(LB)
    gate = r["gate_authority"]
    assert gate["gate"] == "gate_lb_channel"
    verdict = gate["verdict"]
    by = {o["name"]: o for o in r["outputs"]}
    # the runner's reported error, rounded like the gate, equals the gate's err_pct (single source)
    assert round(by["relative_error_pct"]["value"], 3) == verdict["err_pct"]
    # the pass/fail flag is the GATE's, surfaced verbatim (not a duplicated literal in the runner)
    assert by["verification_within_gate_band"]["value"] is bool(verdict["passed"])
    # the acceptance-band COMPARISON lives ONLY in the gate; the runner/producer never execute a
    # threshold comparison of their own (they carry at most an explanatory note pointing back to the gate)
    from puckworks.product import lab_reference_producers as P
    from puckworks.validation import gates as G
    assert 'abs(v["err_pct"]) < 0.5' in open(G.__file__).read()
    for mod in (lr, P):
        code_lines = [ln for ln in open(mod.__file__).read().splitlines()
                      if "#" not in ln and "note=" not in ln]
        assert not any("< 0.5" in ln or "err_pct" in ln and "<" in ln for ln in code_lines)


def test_analytic_reference_matches_the_exact_plane_poiseuille_value():
    v = lb.channel_verification()
    h = float(lb.CHANNEL_VERIFICATION_CASE["Nz"] - 2)
    assert v["k_exact"] == h * h / 12.0                          # analytic reference computed, not canned


def test_deterministic_serialization_and_scientific_hash():
    a = lr.execute_runner(LB)
    b = lr.execute_runner(LB)
    assert a["scientific_payload_hash"] == b["scientific_payload_hash"]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_no_large_raw_array_in_the_normal_artifact():
    # the velocity field must NOT leak into the normal Lab result; outputs are concise scalars/short lists
    r = lr.execute_runner(LB)
    for o in r["outputs"]:
        v = o["value"]
        assert not isinstance(v, dict)
        if isinstance(v, list):
            assert len(v) <= 4
    blob = json.dumps(r)
    assert "\"ux\"" not in blob and len(blob) < 8000            # no dense field serialized


def test_invalid_solver_inputs_are_rejected_not_silently_coerced():
    for kw in (dict(Nz=33.0), dict(N=0), dict(max_steps=-1), dict(check=True),
               dict(tau_plus=0.4), dict(g=float("nan")), dict(g=float("inf")), dict(rtol=0), dict(Nz=2)):
        with pytest.raises(ValueError):
            lb.channel_verification(**kw)


def test_runner_failure_is_isolated_and_marked_FAILED(monkeypatch):
    def boom():
        raise RuntimeError("simulated LB producer failure")
    spec, _ = lr.RUNNERS[LB]
    monkeypatch.setitem(lr.RUNNERS, LB, (spec, boom))
    results = lr.run_selected([LB, "wadsworth2026.permeability"])
    by = {r["component_id"]: r for r in results}
    # a failed runner is a FAILED execution state (an error, never a scientific zero) and does not erase
    # the other runner's real result
    assert by[LB]["status"] == "FAILED" and by[LB]["execution_state"] == "FAILED"
    assert by[LB]["outputs"] == []                              # no fabricated zero output
    assert by["wadsworth2026.permeability"]["status"] == "executed"


def test_runner_does_not_upgrade_registry_evidence():
    reg = {c.name: c.evidence_strength for c in puckworks.components()}
    r = lr.execute_runner(LB)
    assert r["evidence"]["evidence_strength"] == reg[LB]

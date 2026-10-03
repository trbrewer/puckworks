"""Small offline checks of qualification accounting; never launches a full-bed solve."""
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from tools import pannusch_temperature_history_verification as v
from tools import pannusch_temperature_history_reference as ref
from puckworks.models.pannusch2024 import temperature_history as th


def fixture_receipt(tmp_path, method="legacy"):
    c = next(c for c in v.read_json(v.BUNDLE/"CASES.json")["cases"] if c["method"] == method)
    eid = "exec-001"
    np.savez_compressed(tmp_path/(eid+".npz"), fractions=np.ones(7))
    m = {"status": "COMPLETE", "case": c, "case_sha256": v.canonical_hash(c),
         "numerical_identities": v.numerical_identities(c), "arrays_sha256": v.digest(tmp_path/(eid+".npz")),
         "actual_span_s": [0., 30.], "requested_span_s": [0., 30.],
         "integration_complete": True, "segments": [{"status": "COMPLETE", "actual_span_s": [0, 30],
                                                         "requested_span_s": [0, 30]}]}
    v.write_json(tmp_path/(eid+".json"), m)
    e = {"status": "COMPLETE", "case_id": c["id"], "execution_id": eid,
         "numerical_identities": v.numerical_identities(c), "receipt_sha256": v.digest(tmp_path/(eid+".json")),
         "timeout_s": 60., "charged_wall_s": 0.}
    return c, m, [e]


@pytest.mark.parametrize("mutation,reason", [
    (lambda m: m.update(status="FAILED"), "FAILED_OR_MISMATCHED"),
    (lambda m: m.update(actual_span_s=[0., 29.]), "PARTIAL_OR_MISMATCHED"),
    (lambda m: m.update(numerical_identities={}), "NUMERICAL_SOURCE_CHANGED"),
    (lambda m: m.update(case_sha256="0"*64), "FAILED_OR_MISMATCHED"),
])
def test_failed_partial_or_mismatched_evidence_cannot_report_success(tmp_path, mutation, reason):
    c, m, ledger = fixture_receipt(tmp_path)
    mutation(m)
    v.write_json(tmp_path/"exec-001.json", m)
    ledger[0]["receipt_sha256"] = v.digest(tmp_path/"exec-001.json")
    with pytest.raises(ValueError, match=reason):
        v.load_evidence(tmp_path, c, ledger)


def test_receipt_and_array_integrity_and_latest_failure(tmp_path):
    c, m, ledger = fixture_receipt(tmp_path)
    assert v.load_evidence(tmp_path, c, ledger)[1]["fractions"].shape == (7,)
    ledger.append(dict(ledger[0], status="FAILED"))
    with pytest.raises(ValueError, match="LATEST_EXECUTION_FAILED"):
        v.load_evidence(tmp_path, c, ledger)
    ledger.pop()
    (tmp_path/"exec-001.npz").write_bytes(b"changed")
    with pytest.raises(ValueError, match="ARRAY_HASH_MISMATCH"):
        v.load_evidence(tmp_path, c, ledger)


def test_false_complete_bdf_receipt_rejected(tmp_path):
    c, m, ledger = fixture_receipt(tmp_path, "BDF")
    m["integration_complete"] = False
    v.write_json(tmp_path/"exec-001.json", m)
    ledger[0]["receipt_sha256"] = v.digest(tmp_path/"exec-001.json")
    with pytest.raises(ValueError, match="FAILED_INTEGRATION"):
        v.load_evidence(tmp_path, c, ledger)


def test_reserved_slots_and_aggregate_time_are_enforced_before_launch(tmp_path):
    case = v.read_json(v.BUNDLE/"CASES.json")["cases"][0]["id"]
    ledger = [{"execution_id": f"exec-{i:03d}", "case_id": case, "status": "FAILED",
               "timeout_s": 60., "charged_wall_s": 1.} for i in range(1, 29)]
    v.write_json(tmp_path/"executions.json", ledger)
    with patch.object(v.subprocess, "run", side_effect=AssertionError("must not launch")):
        with pytest.raises(RuntimeError, match="ceiling"):
            v.execute(tmp_path, case)
    with patch.object(v.subprocess, "run", return_value=SimpleNamespace(returncode=2)) as launch:
        v.execute(tmp_path, case, correction=True)
    assert launch.call_count == 1
    assert len(v.read_json(tmp_path/"executions.json")) == 29
    ledger = [{"execution_id": "exec-001", "case_id": case, "status": "FAILED",
               "timeout_s": 60., "charged_wall_s": 1800.}]
    v.write_json(tmp_path/"executions.json", ledger)
    with patch.object(v.subprocess, "run", side_effect=AssertionError("must not launch")):
        with pytest.raises(RuntimeError, match="ceiling"):
            v.execute(tmp_path, case, correction=True)
    assert v.used_resources([{"timeout_s": 60., "status": "LAUNCHED"}]) == (1, 60.)


def test_timeout_and_cancel_receipts_persist(tmp_path):
    case = v.read_json(v.BUNDLE/"CASES.json")["cases"][0]["id"]
    with patch.object(v.subprocess, "run", side_effect=subprocess.TimeoutExpired("worker", 60)):
        v.execute(tmp_path, case)
    ledger = v.read_json(tmp_path/"executions.json")
    assert ledger[0]["status"] == "TIMEOUT" and ledger[0]["charged_wall_s"] >= 0
    with patch.object(v.subprocess, "run", side_effect=KeyboardInterrupt):
        with pytest.raises(KeyboardInterrupt):
            v.execute(tmp_path, case)
    assert v.read_json(tmp_path/"executions.json")[-1]["status"] == "CANCELLED"


def test_unreserved_worker_refused_and_report_does_not_integrate(tmp_path):
    v.write_json(tmp_path/"executions.json", [])
    with pytest.raises(ValueError, match="reserved launch"):
        v.worker("A.caffeine.legacy", tmp_path, "exec-001")
    with patch.object(th, "simulate_temperature_history", side_effect=AssertionError("no solve")), \
         patch.object(v, "execute", side_effect=AssertionError("no execute")):
        result = v.report(tmp_path, tmp_path/"report")
    assert result["numerical_disposition"] == "INCOMPLETE"
    assert all(c["reason"] == "UNRUN" for c in result["cases"].values())
    first = (tmp_path/"report/RESULTS.json").read_bytes()
    v.report(tmp_path, tmp_path/"report")
    assert first == (tmp_path/"report/RESULTS.json").read_bytes()


def test_strict_input_json(tmp_path):
    p = tmp_path/"bad.json"; p.write_text('{"bad":NaN}')
    with pytest.raises(ValueError, match="nonfinite"):
        v.read_json(p)


def test_small_ramp_distinct_radau_route_matches_bdf():
    t = np.linspace(0., 2., 9)
    independent, _, checked_t, checked_y = ref.independent_radau(
        [0., 2.], [361.15, 366.15], 2e-6, "caffeine", 1.7, 7, t)
    p = th.simulate_temperature_history(
        th.TemperatureHistory.linear_celsius([0, 2], [88, 93]), flow_m3_s=2e-6,
        t_span_s=(0, 2), solute="caffeine", observation_times_s=t,
        settings=th.TemperatureHistorySettings(nz=7))
    np.testing.assert_allclose(v.reduced(p.observations), independent, rtol=2e-7, atol=1e-9)
    assert checked_t[0] == 0 and checked_t[-1] == 2 and np.isfinite(checked_y).all()


def test_source_assembly_never_calls_production_rhs():
    with patch.object(th._PhysicalSystem, "physical_rhs", side_effect=AssertionError("shared RHS")):
        values, _ = ref.ordered_exponential([0., 1., 2.], [361.15, 366.15], 2e-6,
                                            "caffeine", 1.7, 7, np.array([0., .5, 1., 1.5, 2.]))
    assert values.shape == (5, 21) and np.isfinite(values).all()


def test_no_untracked_or_external_source_dependencies_in_example():
    # The executable demonstration is deliberately a <=12-node smoke, not qualification.
    script = Path(v.ROOT/"examples/pannusch_temperature_history.py")
    result = subprocess.run([__import__('sys').executable, str(script)], check=True, capture_output=True, text=True)
    value = json.loads(result.stdout)
    assert value["settings"]["nz"] == 12 and value["status"] == "COMPLETE"
    assert value["qualification_status"] == "NOT_ASSESSED_FOR_THIS_CALL"

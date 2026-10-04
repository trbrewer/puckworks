"""Small, offline runner/reference checks; no full qualification trajectory is launched."""
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from tools import pannusch_positive_fv_verification as v
from tools import pannusch_positive_fv_reference as ref
from puckworks.models.pannusch2024 import temperature_history_fv as fv


def test_case_counts_observations_and_frozen_defaults():
    c = v.read_json(v.BUNDLE/"CASES.json")
    assert len(c["cases"]) == 28
    assert len({x["id"] for x in c["cases"]}) == 28
    assert [sum(x["family"] == k for x in c["cases"]) for k in "ABCDEF"] == [4, 8, 8, 4, 1, 3]
    assert sum(x["method"] == "Radau" for x in c["cases"]) == 6
    assert fv.FVSettings().cells == c["default_cells"] == 400
    assert fv.FVSettings().h_max_s == c["default_h_max_s"] == .02
    t = v.observations(c)
    assert t[0] == 0 and t[-1] == 30 and np.all(np.diff(t) > 0)
    assert all(x in t for x in (1e-6, 7-1e-8, 7, 7+1e-8, 19, 20, 30))


def test_task_wide_budget_cannot_reset_by_changing_directory(tmp_path):
    with patch.object(v, "authority_path", return_value=tmp_path/"authority.json"):
        with v.locked_authority(tmp_path/"one") as (path, ledger):
            assert ledger["executions"] == []
        with pytest.raises(RuntimeError, match="DIFFERENT_DIRECTORY"):
            with v.locked_authority(tmp_path/"two"):
                pass


def test_execution_correction_reserve_and_auxiliary_wall_accounting():
    row = dict(reserved_wall_s=120., status="FAILED", charged_wall_s=1.)
    ledger = dict(executions=[dict(row) for _ in range(28)], auxiliary=[])
    with pytest.raises(RuntimeError, match="RESERVE"):
        v.reserve(ledger)
    assert v.reserve(ledger, correction=True) == 120
    ledger["executions"].extend(dict(row) for _ in range(4))
    with pytest.raises(RuntimeError, match="RESERVE"):
        v.reserve(ledger, correction=True)
    ledger = dict(executions=[dict(row, charged_wall_s=1700.)], auxiliary=[dict(row, charged_wall_s=95.)])
    assert v.reserve(ledger, auxiliary=True) == 5.
    ledger["auxiliary"].append(dict(reserved_wall_s=5., status="LAUNCHED"))
    with pytest.raises(RuntimeError, match="EXHAUSTED"):
        v.reserve(ledger, auxiliary=True)


def test_execute_resumes_only_unattempted_and_retains_failed_attempts(tmp_path):
    case = v.read_json(v.BUNDLE/"CASES.json")["cases"][0]["id"]
    with patch.object(v, "authority_path", return_value=tmp_path/"authority.json"), \
         patch.object(v.subprocess, "run", return_value=SimpleNamespace(returncode=2)) as launch:
        v.execute(tmp_path/"evidence", case)
        v.execute(tmp_path/"evidence", case)
        assert launch.call_count == 1
        v.execute(tmp_path/"evidence", case, correction=True)
        assert launch.call_count == 2
    entries = v.read_json(tmp_path/"evidence/executions.json")
    assert [e["status"] for e in entries] == ["FAILED", "FAILED"]
    assert entries[0]["execution_id"] != entries[1]["execution_id"]


def test_timeout_and_cancellation_are_retained(tmp_path):
    case = v.read_json(v.BUNDLE/"CASES.json")["cases"][0]["id"]
    with patch.object(v, "authority_path", return_value=tmp_path/"authority.json"):
        with patch.object(v.subprocess, "run", side_effect=subprocess.TimeoutExpired("worker", 120)):
            v.execute(tmp_path/"evidence", case)
        with patch.object(v.subprocess, "run", side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                v.execute(tmp_path/"evidence", case, correction=True)
    assert [e["status"] for e in v.read_json(tmp_path/"evidence/executions.json")] == ["TIMEOUT", "CANCELLED"]


def test_unreserved_worker_refused(tmp_path):
    v.write_json(tmp_path/"executions.json", [])
    with pytest.raises(RuntimeError, match="UNRESERVED"):
        v.worker(tmp_path, "A.caffeine", "exec-001")


def test_report_only_is_deterministic_and_cannot_launch_a_simulation(tmp_path):
    v.write_json(tmp_path/"executions.json", [])
    with patch.object(fv, "simulate_temperature_history_fv", side_effect=AssertionError("no simulation")), \
         patch.object(ref, "radau", side_effect=AssertionError("no reference")), \
         patch.object(fv, "expm_multiply", side_effect=AssertionError("no exponential")):
        result = v.reduce_report(tmp_path, tmp_path/"report")
        assert result["dispositions"]["numerical_qualification"] == "INCOMPLETE"
        before = (tmp_path/"report/RESULTS.json").read_bytes()
        v.reduce_report(tmp_path, tmp_path/"report")
        assert before == (tmp_path/"report/RESULTS.json").read_bytes()


def test_failed_or_unbound_saved_evidence_cannot_qualify(tmp_path):
    case = v.read_json(v.BUNDLE/"CASES.json")["cases"][0]
    with pytest.raises(ValueError, match="UNRUN"):
        v.load_case(tmp_path, case, [])
    entry = dict(case_id=case["id"], execution_id="exec-001", status="FAILED")
    with pytest.raises(ValueError, match="LATEST_ATTEMPT_FAILED"):
        v.load_case(tmp_path, case, [entry])
    entry["status"] = "COMPLETE"
    (tmp_path/"exec-001.json").write_text('{}')
    with pytest.raises(ValueError, match="RECEIPT_HASH_MISMATCH"):
        v.load_case(tmp_path, case, [entry])
    entry["receipt_sha256"] = v.digest(tmp_path/"exec-001.json")
    meta = dict(case=case, case_sha256=v.canonical_hash(case), status="COMPLETE", identities={})
    v.write_json(tmp_path/"exec-001.json", meta); entry["receipt_sha256"] = v.digest(tmp_path/"exec-001.json")
    with pytest.raises(ValueError, match="NUMERICAL_SOURCE_CHANGED"):
        v.load_case(tmp_path, case, [entry])


def test_reference_does_not_call_candidate_generator_and_origin_is_explicit():
    history = fv.TemperatureHistory.linear_celsius((0, .04), (88, 93))
    with patch.object(fv._System, "generator", side_effect=AssertionError("shared builder")):
        whole, _, _, _ = ref.radau(history, 2e-6, "caffeine", 1.7, 5, np.array([0, .02, .04]), t_span_s=(0, .04))
        late, _, _, _ = ref.radau(history, 2e-6, "caffeine", 1.7, 5, np.array([.02, .04]), t_span_s=(0, .04))
    np.testing.assert_array_equal(whole[1:], late)


def test_test_only_passive_path_small_mesh_and_conservative_field_restriction():
    s = v._PassiveSystem(8, 2e-6)
    h = fv.TemperatureHistory.constant_celsius((0, .04), (88,))
    result = fv._evolve(s, h, (0, .04), (0, .02, .04), (), fv.FVSettings(cells=8))
    assert result["numerical_admissibility"] == "PASSED_SAMPLED_CHECKS"
    assert np.all(result["observations"].fine_cell_average_kg_m3 == 0)
    assert np.all(result["observations"].coarse_cell_average_kg_m3 == 0)
    coarse = dict(states=np.ones((2, 3*4+1)), fractions=np.ones(1))
    fine = dict(states=np.ones((2, 3*8+1)), fractions=np.ones(1))
    fine["states"][:, :-1] = np.tile([.5, 1.5], (2, 12))
    meta = dict(case=dict(cells=4), Cstar=1., M0_cont_kg=1., grind=1.7)
    assert v.spatial(coarse, fine, meta)["weighted_field"]["max_abs_normalized"] == 0


def test_example_is_small_offline_and_not_qualified():
    result = subprocess.run([__import__('sys').executable, str(Path(v.ROOT)/"examples/pannusch_temperature_history_fv.py")],
                            check=True, capture_output=True, text=True)
    record = json.loads(result.stdout)
    assert record["settings"]["cells"] == 8 and record["campaign_qualification"] == "NOT_ASSESSED_FOR_THIS_CALL"
    assert record["PHYSICAL_VALIDATION"] == "NOT_ESTABLISHED"


def test_small_worker_saved_evidence_and_accounting_roundtrip(tmp_path):
    contract = v.read_json(v.BUNDLE/'CASES.json')
    case = dict(contract['cases'][0], cells=8, times_s=[0, .04])
    contract['cases'] = [case]
    contract['fraction_bounds_s'] = [0, .02, .04]
    bundle, evidence = tmp_path/'bundle', tmp_path/'evidence'
    bundle.mkdir(); evidence.mkdir()
    v.write_json(bundle/'CASES.json', contract)
    entry = dict(case_id=case['id'], execution_id='exec-001', status='LAUNCHED',
                 reserved_wall_s=120., identities={})
    v.write_json(evidence/'executions.json', [entry])
    with patch.object(v, 'BUNDLE', bundle), patch.object(v, 'identities', return_value={}), \
         patch.object(v, 'observations', return_value=np.array([0, .02, .04])):
        assert v.worker(evidence, case['id'], 'exec-001') == 0
        entry.update(status='COMPLETE', receipt_sha256=v.digest(evidence/'exec-001.json'))
        meta, arrays = v.load_case(evidence, case, [entry])
        result = v.accounting(meta, arrays)
        assert result['positivity_passed'] and result['conservation_passed']
        assert result['quadrature_outlet']['passed']


def test_unavailable_report_clears_failed_case_and_omits_private_path(tmp_path):
    v.write_json(tmp_path/'executions.json', [])
    with patch.object(v, 'load_case', side_effect=OSError('private/local/location')):
        result = v.reduce_report(tmp_path, tmp_path/'report')
    assert result['dispositions']['numerical_qualification'] == 'INCOMPLETE'
    assert 'private/local/location' not in json.dumps(result)
    assert all(c['reason'] == 'OSError' for c in result['cases'].values())

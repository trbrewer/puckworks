"""Small, offline runner/reference checks; no full qualification trajectory is launched."""
import subprocess
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from tools import pannusch_flow_temp_fv_verification as v
from tools import pannusch_flow_temp_fv_reference as ref
from puckworks.models.pannusch2024 import flow_temperature_history_fv as fv


def test_case_counts_and_frozen_observations():
    c=v.read_json(v.BUNDLE/'CASES.json')
    assert len(c['cases'])==32
    assert [sum(x['family']==g for x in c['cases']) for g in 'ABCDEF']==[8,8,8,4,1,3]
    assert c['limits']['executions']==36
    t=v.observations(c)
    assert all(x in t for x in (1e-6,5-1e-8,5,5+1e-8,7,13,19,23,25,30))


def test_task_wide_budget_cannot_reset_by_changing_directory(tmp_path):
    with patch.object(v, "authority_path", return_value=tmp_path/"authority.json"):
        with v.locked_authority(tmp_path/"one") as (path, ledger):
            assert ledger["executions"] == []
        with pytest.raises(RuntimeError, match="DIFFERENT_DIRECTORY"):
            with v.locked_authority(tmp_path/"two"):
                pass


def test_execution_correction_reserve_and_auxiliary_wall_accounting():
    row = dict(reserved_wall_s=120., status="FAILED", charged_wall_s=1.)
    ledger = dict(executions=[dict(row) for _ in range(32)], auxiliary=[])
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
    with patch.object(fv, "simulate_flow_temperature_history_fv", side_effect=AssertionError("no simulation")), \
         patch.object(ref, "reference", side_effect=AssertionError("no reference")), \
         patch.object(fv, "expm_multiply", side_effect=AssertionError("no exponential")):
        result = v.reduce_report(tmp_path, tmp_path/"report")
        assert result["dispositions"]["numerical_qualification"] == "NUMERICAL_QUALIFICATION_INCOMPLETE"
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


@pytest.mark.parametrize('method',['FV','OLD_FV','ORDERED','Radau'])
def test_small_worker_roundtrip_and_independent_flux_inventory_failure(tmp_path,method):
    c=v.read_json(v.BUNDLE/'CASES.json')
    c.update(t_span_s=[0,.08],fraction_bounds_s=[0,.02,.05,.08])
    c['histories']={'T':dict(times_s=[0,.03,.08],values=[353.15,371.15],kind='constant'),
                    'Q':dict(times_s=[0,.02,.08],values=[1e-6,3e-6],kind='constant')}
    if method=='OLD_FV': c['histories']['Q']=dict(times_s=[0,.08],values=[2e-6],kind='constant')
    case=dict(c['cases'][0],cells=4,method=method,temperature='T',flow='Q'); c['cases']=[case]
    bundle,evidence=tmp_path/'bundle',tmp_path/'evidence'; bundle.mkdir();evidence.mkdir()
    v.write_json(bundle/'CASES.json',c)
    entry=dict(case_id=case['id'],execution_id='exec-001',status='LAUNCHED',reserved_wall_s=120.,identities={})
    v.write_json(evidence/'executions.json',[entry])
    with patch.object(v,'BUNDLE',bundle),patch.object(v,'identities',return_value={}), \
         patch.object(v,'observations',return_value=np.array([0,.011,.02,.03,.05,.08])):
        assert v.worker(evidence,case['id'],'exec-001')==0
        entry.update(status='COMPLETE',receipt_sha256=v.digest(evidence/'exec-001.json'))
        meta,a=v.load_case(evidence,case,[entry])
        report=v.accounting(meta,a)
        assert report['conservation_passed'] and report['prescribed_volume']['passed']
        if method in ('FV','OLD_FV'):
            assert report['positivity_passed'] and report['numerical_flux_passed']
            fixed_flux=a['numerical_flux'].copy(); fixed_mout=a['diagnostic_states'][:,-1].copy()
            a['diagnostic_states'][1:,0]+=1.
            broken=v.accounting(meta,a)
            assert not broken['conservation_passed']
            np.testing.assert_array_equal(fixed_flux,a['numerical_flux'])
            np.testing.assert_array_equal(fixed_mout,a['diagnostic_states'][:,-1])
            assert broken['numerical_flux_passed']
            assert broken['fluxes']==report['fluxes']


def test_independent_history_union_and_analytic_volume_inversion():
    T=fv.TemperatureHistory.linear_celsius((0,.03,.08),(80,90,98))
    Q=fv.FlowHistory((0,.02,.08),(1e-6,2e-6,3e-6),'linear')
    assert [s[:2] for s in ref.segments(T,Q,(.01,.07))]==[(.01,.02),(.02,.03),(.03,.07)]
    for t in (.0,.015,.02,.03,.04,.08):
        V=ref.volume(Q,0,t)
        assert ref.time_for_volume(Q,V)==pytest.approx(t,abs=1e-16)
    # Candidate history methods cannot make a reference agree via a shared bug.
    with patch.object(fv.FlowHistory,'value_m3_s',side_effect=AssertionError), \
         patch.object(fv.FlowHistory,'integral',side_effect=AssertionError), \
         patch.object(fv.TemperatureHistory,'value_K',side_effect=AssertionError), \
         patch.object(fv,'_segments',side_effect=AssertionError), \
         patch.object(fv._System,'generator',side_effect=AssertionError):
        z,*_=ref.reference(T,Q,'caffeine',1.7,3,[0,.04,.08],t_span_s=(0,.08))
        assert np.isfinite(z).all()


def test_spatial_paired_restriction_and_private_passive():
    s=v._PassiveSystem(8);T=fv.TemperatureHistory.constant_celsius((0,.04),(88,))
    Q=fv.FlowHistory((0,.04),(1e-6,3e-6),'linear')
    r=fv._evolve(s,T,Q,(0,.04),(0,.02,.04),(),fv.FVSettings(cells=8))
    assert r['numerical_admissibility']=='PASSED_SAMPLED_CHECKS'
    assert np.all(r['observations'].fine_cell_average_kg_m3==0)
    c=dict(states=np.ones((2,13)),fractions=np.ones(1));f=dict(states=np.ones((2,25)),fractions=np.ones(1))
    f['states'][:,:-1]=np.tile([.5,1.5],(2,12))
    meta=dict(case=dict(cells=4),Cstar=1.,M0_cont_kg=1.,grind=1.7)
    assert v.spatial(c,f,meta)['weighted_field']['max_abs_normalized']==0

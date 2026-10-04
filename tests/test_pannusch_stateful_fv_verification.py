"""004 runner/reference tests: N4, 0..0.08 s only; never campaign executions."""
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
import pytest

from tools import pannusch_stateful_fv_verification as v


def test_frozen_matrix_and_plan_identity():
    c = v.read_json(v.BUNDLE/'CASES.json')
    assert len(c['cases']) == 28
    assert [sum(x['family'] == f for x in c['cases']) for f in 'ABCDEF'] == [8,8,2,7,2,1]
    assert len(c['observations_s']) == 86 and len(c['fraction_windows_s']) == 17
    for history in ('S','L'):
        case = next(x for x in c['cases'] if x['history'] == history and x['h_max_s'] == .02)
        plan = v.case_plan(case,c)
        assert plan.primary_times_s[137] == c['checkpoint'][history]['time_s']
        assert plan.identity_sha256 == c['checkpoint'][history]['plan_sha256']


def test_shared_budget_reserve_and_failed_attempts(tmp_path):
    with patch.object(v,'authority_path',return_value=tmp_path/'authority.json'):
        with v.locked_authority(tmp_path/'one'):
            pass
        with pytest.raises(RuntimeError,match='DIFFERENT_DIRECTORY'):
            with v.locked_authority(tmp_path/'two'):
                pass
    ledger = dict(executions=[dict(reserved_wall_s=120.,charged_wall_s=1.) for _ in range(28)], auxiliary=[])
    with pytest.raises(RuntimeError,match='RESERVE'): v.reserve(ledger)
    assert v.reserve(ledger,correction=True) == 120
    ledger['executions'] *= 2
    with pytest.raises(RuntimeError,match='RESERVE'): v.reserve(ledger,correction=True)
    ledger = dict(executions=[dict(reserved_wall_s=120.,charged_wall_s=1795.)],auxiliary=[])
    assert v.reserve(ledger,auxiliary=True) == 5
    ledger['auxiliary'].append(dict(reserved_wall_s=5.))
    with pytest.raises(RuntimeError,match='EXHAUSTED'): v.reserve(ledger)
    case = v.read_json(v.BUNDLE/'CASES.json')['cases'][0]['id']
    with patch.object(v,'authority_path',return_value=tmp_path/'failed-authority.json'), \
         patch.object(v,'identities',return_value={}), \
         patch.object(v.subprocess,'run',return_value=SimpleNamespace(returncode=2)) as launch:
        v.execute(tmp_path/'failed',case)
        v.execute(tmp_path/'failed',case)
        assert launch.call_count == 1
        v.execute(tmp_path/'failed',case,correction=True)
        assert launch.call_count == 2
    assert [r['status'] for r in v.read_json(tmp_path/'failed/executions.json')] == ['FAILED','FAILED']


def test_unreserved_worker_and_report_cannot_integrate(tmp_path):
    v.write_json(tmp_path/'executions.json',[])
    with pytest.raises(RuntimeError,match='UNRESERVED'): v.worker(tmp_path,'bad','bad')
    with patch.object(v.sf,'simulate_stateful_fv',side_effect=AssertionError('no simulation')), \
         patch.object(v.ref,'reference',side_effect=AssertionError('no reference')):
        r = v.reduce_report(tmp_path,tmp_path/'report')
        assert r['dispositions']['numerical_qualification'] == 'IMPLEMENTED_QUALIFICATION_INCOMPLETE'
        saved = (tmp_path/'report/RESULTS.json').read_bytes()
        v.reduce_report(tmp_path,tmp_path/'report')
        assert saved == (tmp_path/'report/RESULTS.json').read_bytes()


def test_small_worker_all_operations_and_independent_accounting(tmp_path):
    c = v.read_json(v.BUNDLE/'CASES.json')
    c.update(t_span_s=[0,.08],observations_s=[0,.011,.02,.03,.05,.08],
             fraction_windows_s=[[0,.02],[.02,.05],[.05,.08],[0,.08]],reference_primary_h_s=[.04,.02,.01])
    c['histories']['S'] = dict(temperature_C=dict(times_s=[0,.03,.08],values=[80,98],kind='constant'),
                             flow=dict(times_s=[0,.02,.08],values=[1e-6,3e-6],kind='constant'))
    c['checkpoint']['S']['time_s'] = .02
    methods = ['BASE_003','EQUILIBRIUM','U','ORDERED','Radau','PREFIX','RESUME','BRANCH','BRANCH_REFERENCE']
    c['cases'] = [dict(c['cases'][0],id=m,method=m,cells=4,checkpoint_index=1,parent='PREFIX' if m in ('RESUME','BRANCH') else 'ORDERED',future_T_C=93.,future_Q_m3_s=2.2e-6) for m in methods]
    bundle = tmp_path/'bundle';bundle.mkdir()
    v.write_json(bundle/'CASES.json',c)
    rows=[]; data={}
    with patch.object(v,'BUNDLE',bundle),patch.object(v,'identities',return_value={}):
        for index,case in enumerate(c['cases']):
            eid=f'exec-{index:03d}'
            row=dict(case_id=case['id'],execution_id=eid,status='LAUNCHED',reserved_wall_s=120.,identities={})
            rows.append(row);v.write_json(tmp_path/'executions.json',rows)
            assert v.worker(tmp_path,case['id'],eid) == 0
            row.update(status='COMPLETE',receipt_sha256=v.digest(tmp_path/(eid+'.json')))
            v.write_json(tmp_path/'executions.json',rows)
            m,a=v.load_case(tmp_path,case);data[case['id']]=(m,a)
            report=v.accounting(m,a,c)
            assert report['passed'],report
            if case['method']=='U':
                q=a['quadrature'].copy();out=a['local_mass'].copy()
                a['primary_fields'][1:,0]+=1
                bad=v.accounting(m,a,c)
                assert not bad['local_inventory']['passed']
                assert bad['numerical_flux']==report['numerical_flux']
                np.testing.assert_array_equal(q,a['quadrature']);np.testing.assert_array_equal(out,a['local_mass'])
                a['primary_fields'][1:,0]-=1
        for left,right,tol in [('BASE_003','EQUILIBRIUM',1e-12),('U','ORDERED',1e-8),('BRANCH','BRANCH_REFERENCE',1e-8)]:
            assert v.compare(*data[left],*data[right],c,tol)['passed']
        for left in ('PREFIX','RESUME'):
            assert v.compare(*data[left],*data['U'],c,1e-12,restart=True)['passed']


def test_reference_does_not_call_candidate_initialization_or_inventory():
    T=v.sf.TemperatureHistory.constant_celsius([0,.03,.08],[80,98])
    Q=v.sf.FlowHistory([0,.02,.08],[1e-6,3e-6],'constant')
    with patch.object(v.sf.fv._System,'generator',side_effect=AssertionError), \
         patch.object(v.sf,'_inventory',side_effect=AssertionError), \
         patch.object(v.sf.FVChemicalState,'from_cell_averages',side_effect=AssertionError), \
         patch.object(v.sf.FlowHistory,'integral',side_effect=AssertionError):
        y,*_=v.ref.reference(T,Q,'caffeine',1.7,4,[0,.04,.08],t_span_s=(0,.08),
                             initial_fields=v.ref.stateful_u_fields('caffeine',4),method='ORDERED')
        assert np.isfinite(y).all()

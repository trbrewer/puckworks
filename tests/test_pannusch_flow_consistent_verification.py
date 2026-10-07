"""Small N4 runner controls; no representative execution slots in CI."""
import json

import numpy as np
import pytest

from tools import pannusch_flow_consistent_verification as v
from tools import pannusch_stateful_fv_verification as old


def test_frozen_matrix_preserves_original_cases_and_one_reference_control():
    c=json.loads((v.BUNDLE/'CASES.json').read_text()); original=json.loads((old.BUNDLE/'CASES.json').read_text())
    for key in ('histories','observations_s','fraction_windows_s','initial_family_U','checkpoint','allowances','settings','radau','reference_primary_h_s'):
        assert c[key]==original[key]
    assert c['cases'][:28]==original['cases'] and len(c['cases'])==29
    assert c['limits']['correction_reserve']==7
    assert c['fraction_windows_s'][2]==[2.737002188183808,2.74]


def test_reservation_counts_failures_auxiliary_and_reserve():
    ledger=dict(executions=[dict(reserved_wall_s=120.,charged_wall_s=1.,status='FAILED') for _ in range(29)],auxiliary=[])
    with pytest.raises(RuntimeError,match='RESERVE'):v.reserve(ledger)
    assert v.reserve(ledger,correction=True)==120.
    ledger['auxiliary'].append(dict(reserved_wall_s=3568.))
    assert v.reserve(ledger,correction=True)==3.
    ledger['auxiliary'].append(dict(reserved_wall_s=3.))
    with pytest.raises(RuntimeError,match='EXHAUSTED'):v.reserve(ledger,auxiliary=True)


def small_contract():
    c=json.loads((v.BUNDLE/'CASES.json').read_text())
    c['t_span_s']=[0,.08];c['observations_s']=[0,.013,.04,.08];c['fraction_windows_s']=[[0,.08],[.013,.04]]
    c['settings']['cells']=4
    for h in c['histories'].values():
        for name in ('flow','temperature_C'):
            h[name]['times_s']=[t*.08/30 for t in h[name]['times_s']]
    return c


def test_small_attached_observer_and_independent_reference(tmp_path):
    c=small_contract()
    case=dict(c['cases'][18],cells=4)
    m,a,_=v.run_case(tmp_path,case,c,120)
    assert m['coverage_complete'],m.get('observer_reason')
    assert m['primary_unchanged'] and a['fractions'].shape==(2,)
    rc=dict(c['cases'][21],cells=4)
    rm,ra,_=v.run_case(tmp_path,rc,c,120)
    assert rm['coverage_complete'] and len(ra['reference_quadrature'])>0
    comparison=old.compare(m,a,rm,ra,c,5e-4)
    assert comparison['passed']
    np.testing.assert_allclose(ra['fractions'],ra['cumulative_difference_fractions'],rtol=1e-10)


def test_small_report_reducers_and_reference_quadrature(tmp_path):
    c=small_contract();case=dict(c['cases'][18],cells=4)
    m,a,_=v.run_case(tmp_path,case,c,120)
    account=v._observer_account(m,a,c)
    assert account['passed'],[(k,x) for k,x in account.items() if isinstance(x,dict) and not x.get('passed',True)]
    assert json.loads(json.dumps(v.sf._json(account),allow_nan=False))['passed'] is True
    rm,ra,_=v.run_case(tmp_path,dict(c['cases'][21],cells=4),c,120)
    account=v._reference_account(rm,ra,c)
    assert account['passed']


def test_repeat_compares_full_saved_quadrature_and_checked_support(tmp_path):
    # Reporting must not lose coverage when its working set discards large arrays.
    a=dict(fields=np.ones((2,12)),observer_quadrature=np.ones((8,12)),exportable=np.ones(2))
    np.savez(tmp_path/'left.npz',**a);np.savez(tmp_path/'right.npz',**a)
    def meta(name):
        return dict(execution_id=name,arrays_sha256=v.digest(tmp_path/(name+'.npz')))
    assert all(v._repeat_arrays(tmp_path,meta('left'),meta('right')).values())
    a['observer_quadrature'][0,6]=2.
    np.savez(tmp_path/'right.npz',**a)
    checks=v._repeat_arrays(tmp_path,meta('left'),meta('right'))
    assert checks['fields'] and not checks['observer_quadrature']
    stale=meta('right');a['exportable'][1]=0.;np.savez(tmp_path/'right.npz',**a)
    with pytest.raises(ValueError,match='HASH_MISMATCH'):
        v._repeat_arrays(tmp_path,meta('left'),stale)

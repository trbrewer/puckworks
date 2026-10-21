"""Offline source-reading arithmetic and finite-order verification (not validation)."""
import csv
import itertools
import json

import numpy as np
import pytest
from scipy.optimize import linprog

from puckworks.analysis.melrose2019bed_transient import (
    DATA, DEFAULT_OUTPUT, affine_enclosure, analyze, compatibility, recover, write,
)


def problem(intervals, edges=None, centers=None):
    pts = [dict(point_id=str(i), lower=a, upper=b,
                central=None if centers is None else centers[i]) for i, (a, b) in enumerate(intervals)]
    if edges is None:
        edges = [(str(i), str(i+1)) for i in range(len(pts)-1)]
    return compatibility(pts, edges)


@pytest.mark.parametrize('intervals,expected', [
    ([(0, 1), (1, 2), (2, 3)], (True, False, False)),
    ([(3, 4), (2, 3), (0, 1)], (False, True, False)),
    ([(1, 3), (2, 4), (2, 2)], (True, True, True)),
    ([(1.9, 2.2), (1.8, 2.1)], (True, True, True)),
    ([(1, 1), (1, 1)], (True, True, True)),
])
def test_known_sequences(intervals, expected):
    r = problem(intervals)
    assert tuple(r[k] for k in ['nondecreasing', 'nonincreasing', 'constant']) == expected


def test_transitive_regression_and_partial_order():
    r = problem([(2, 3), (0, 3), (0, 1)])
    assert not r['nondecreasing'] and r['D_up'] == 1
    assert r['comparable_pairs'] == 3
    assert r['decline_witness']['earlier'] == '0' and r['decline_witness']['later'] == '2'
    r = problem([(2, 3), (0, 3), (0, 1)], [('0', '1')])
    assert r['nondecreasing'] and r['comparable_pairs'] == 1
    assert not r['constant']  # no temporal order needed


@pytest.mark.parametrize('intervals', [[(2, 1)], [(float('nan'), 1)], [(0, float('inf'))]])
def test_invalid_intervals(intervals):
    with pytest.raises(ValueError):
        problem(intervals)


def test_invalid_centers_order_and_duplicate_ids():
    with pytest.raises(ValueError):
        problem([(0, 1)], centers=[2])
    with pytest.raises(ValueError):
        problem([(0, 1)], [('0', 'missing')])
    with pytest.raises(ValueError):
        problem([(0, 1), (0, 1)], [('0', '1'), ('1', '0')])
    with pytest.raises(ValueError):
        compatibility([dict(point_id='a', lower=0, upper=1)]*2, [])


def test_edge_eligibility_and_shared_trough():
    assert problem([])['eligibility'] == 'no_data'
    assert problem([])['constant'] is None
    assert problem([(1, 2)])['eligibility'] == 'single_point'
    r = problem([(1, 2), (3, 4)], [])
    assert r['eligibility'] == 'order_free' and r['comparable_pairs'] == 0
    assert r['nondecreasing'] and not r['constant']
    r = problem([(3, 4), (0, 1), (2, 3)])
    assert r['decline_recovery'] == [dict(earlier='0', trough='1', later='2',
                                        decline_margin=2, recovery_margin=1)]
    # Up then down excludes both monotone hypotheses but has no qualifying trough.
    r = problem([(0, 1), (3, 4), (0, 1)])
    assert not r['nondecreasing'] and not r['nonincreasing'] and not r['decline_recovery']


def lp_expansion(intervals, edges, mode):
    """Independent epigraph LP: variables q_1,...,q_n,delta; minimize delta."""
    n = len(intervals)
    A, b = [], []
    for i, (lo, hi) in enumerate(intervals):
        v = np.zeros(n+1); v[i] = 1; v[-1] = -1
        A.append(v); b.append(hi)
        v = np.zeros(n+1); v[i] = -1; v[-1] = -1
        A.append(v); b.append(-lo)
    for i, j in (edges if mode != 'constant' else [(i, i+1) for i in range(n-1)]):
        v = np.zeros(n+1); v[i] = 1; v[j] = -1
        if mode == 'down':
            v = -v
        A.append(v); b.append(0)
        if mode == 'constant':
            A.append(-v); b.append(0)
    opt = linprog([0]*n+[1], A_ub=A, b_ub=b, bounds=[(None, None)]*n+[(0, None)], method='highs')
    assert opt.success
    return opt.fun


@pytest.mark.parametrize('intervals,edges', [
    ([(2, 3), (0, 3), (0, 1)], [(0, 1), (1, 2)]),
    ([(3, 4), (0, 1), (2, 3)], [(0, 1), (1, 2)]),
    ([(0, 1), (4, 5), (2, 3)], [(0, 2), (1, 2)]),
    ([(1, 2), (4, 5)], []),
])
def test_expansion_against_independent_lp(intervals, edges):
    r = problem(intervals, [(str(i), str(j)) for i, j in edges])
    for mode in ['up', 'down', 'constant']:
        assert r['delta_'+mode] == pytest.approx(lp_expansion(intervals, edges, mode), abs=1e-12)
        delta = r['delta_'+mode]
        w = r['expanded_witness_'+mode]
        q = [w[str(i)] for i in range(len(intervals))] if isinstance(w, dict) else [w]*len(intervals)
        for (lo, hi), value in zip(intervals, q):
            assert lo-delta-1e-12 <= value <= hi+delta+1e-12
        for i, j in edges:
            assert (q[i] <= q[j]+1e-12) if mode == 'up' else (q[i] >= q[j]-1e-12)


def test_deterministic_ties():
    r = problem([(3, 3), (3, 3), (0, 0), (0, 0)])
    assert (r['decline_witness']['earlier'], r['decline_witness']['later']) == ('0', '2')


def test_units_calibration_and_shared_outer_envelope():
    contract, profiles, rows = recover()
    assert contract['pressure']['preprint_Pa']['HF'] == contract['pressure']['preprint_bar']['HF']*1e5
    assert contract['figure']['native_width'] == 957
    assert affine_enclosure((80, 900), [[80, 80], [900, 900]], [0, 100]) == (0, 100)
    assert affine_enclosure((58, 548), [[58, 58], [548, 548]], [6, 0]) == (0, 6)
    for r in rows:
        assert r['lower_m3_s'] == r['lower_ml_s']*1e-6
        assert r['upper_m3_s'] == r['upper_ml_s']*1e-6
        if r['flow_ml_s'] is not None:
            assert r['lower_ml_s'] <= r['flow_ml_s'] <= r['upper_ml_s']
        for a, b in itertools.product([57, 59], [547, 549]):
            for y in [r['y_min']-1, r['y_max']+1]:
                q = 6-(y-a)*6/(b-a)
                assert r['lower_ml_s']-1e-14 <= q <= r['upper_ml_s']+1e-14
    assert len({r['point_id'] for r in rows}) == len(rows)
    assert all(r['profile_id'] in {p['profile_id'] for p in profiles} for r in rows)


def test_rectangular_feasible_does_not_establish_joint_feasible():
    # Shared calibration offset c in [-1,1]: q1=2+c, q2=1+c always decreases.
    r = problem([(1, 3), (0, 2)])
    assert r['nondecreasing'] and r['joint_witness_status'] == 'NOT_TESTED'
    for c in [-1, 0, 1]:
        assert 2+c > 1+c
    # Conversely a rectangular exclusion excludes any contained shared-offset reading.
    assert not problem([(2, 4), (0, 1)])['nondecreasing']


def test_interval_average_unequal_duration_and_weights():
    # Q(t)=t^2; exact integral on disjoint, unequal intervals.
    intervals = [(0, 1), (1, 3), (4, 10)]
    rates = [(b**3-a**3)/(3*(b-a)) for a, b in intervals]
    assert np.all(np.diff(rates) > 0)
    runs = np.array([[0, 1, 2], [10, 11, 12]])
    assert np.all(np.diff(np.array([0.25, 0.75]) @ runs) >= 0)
    assert np.array([0, 1]) @ runs[:, 0] > np.array([1, 0]) @ runs[:, 1]
    # A ratio of summed volumes/durations has varying duration weights.
    durations = np.array([[1, 100], [100, 1]])
    rates = np.array([[1, 2], [10, 11]])
    pooled = (durations*rates).sum(axis=0)/durations.sum(axis=0)
    assert pooled[1] < pooled[0] and np.all(np.diff(rates, axis=1) > 0)


def test_real_expansion_witnesses_and_independent_lp():
    result, rows, _ = analyze()
    for profile in result['profile_results']:
        ps = [r for r in rows if r['profile_id'] == profile['profile_id']]
        intervals = [(r['lower_ml_s'], r['upper_ml_s']) for r in ps]
        edges = [(i, i+1) for i in range(len(ps)-1)]
        for mode in ['up', 'down', 'constant']:
            assert profile['delta_'+mode] == pytest.approx(lp_expansion(intervals, edges, mode), abs=1e-11)
        for triple in profile['decline_recovery']:
            by_id = {p['point_id']: p for p in ps}
            trough = by_id[triple['trough']]
            assert by_id[triple['earlier']]['lower_ml_s'] > trough['upper_ml_s']
            assert by_id[triple['later']]['lower_ml_s'] > trough['upper_ml_s']


def test_complete_ledger_and_deterministic_reproduction(tmp_path):
    result = write(tmp_path)
    for name in ['RESULT.json', 'profile_results.csv', 'condition_results.csv']:
        assert (tmp_path/name).read_bytes() == (DEFAULT_OUTPUT/name).read_bytes()
    assert (tmp_path/'observations.csv').read_bytes() == (DATA/'observations.csv').read_bytes()
    with (DATA/'ambiguous_regions.csv').open() as f:
        assert all(r['observation_count'] == '' for r in csv.DictReader(f))
    ledger = result['condition_coverage']
    assert len(ledger) == 16 and len({r['condition_id'] for r in ledger}) == 16
    assert result['coverage']['obscured_point_count'] is None
    assert result['coverage']['physically_qualified_profiles'] == 0
    expected = json.loads((DATA/'contract.json').read_text())
    assert set(expected['intended_conditions']) == {r['condition_id'] for r in ledger}
    assert sum(r['point_count'] for r in result['profile_results']) == result['coverage']['retained_points']
    assert all(r['physical_validation'] == 'NOT_ESTABLISHED' for r in ledger)


def test_campaign_projection_does_not_double_count(tmp_path, monkeypatch):
    from puckworks.paper3 import corpus
    source = list(csv.DictReader(corpus.MANIFEST_CSV.open()))
    old_rows = [r for r in source if r['dataset_id'] != 'melrose2019bed/fig2_flow_transient']
    manifest = tmp_path/'manifest.csv'
    monkeypatch.setattr(corpus, 'MANIFEST_CSV', manifest)
    def save(rows):
        with manifest.open('w') as f:
            writer = csv.DictWriter(f, fieldnames=list(source[0]))
            writer.writeheader()
            writer.writerows(rows)
    save(old_rows)
    before = corpus.denominators()
    save(source)
    after = corpus.denominators()
    assert after['n_manifest_records'] == before['n_manifest_records']+1
    assert after['n_unique_dataset_sources'] == before['n_unique_dataset_sources']

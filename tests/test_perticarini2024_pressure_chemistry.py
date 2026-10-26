"""Original-condition identity, exact boundaries, chemistry operators and figure extents."""
from collections import Counter
import csv
from decimal import Decimal
from fractions import Fraction as Q
import hashlib
from itertools import product
import json
import random
import socket
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest

from puckworks.analysis import perticarini2024_pressure_chemistry as m


def bundle():
    observations, _ = m.load_observations()
    return observations, m.compute(observations)


def pick(result, coffee, temperature, grind, low='6', high='9'):
    return next(r for r in result['comparisons'] if
                (r['coffee_id'], r['temperature_degC'], r['grind_id'], r['pressure_from_bar'], r['pressure_to_bar'])
                == (coffee, temperature, grind, low, high))


def test_identity_coverage_and_descriptive_sd():
    obs, result = bundle()
    old_obs, inputs = m.duration.load_observations()
    assert tuple(i['file_sha256'] for i in inputs) == m.HASHES
    assert [o['source_condition_id'] for o in obs] == [o['source_condition_id'] for o in old_obs]
    assert [{k: o[k] for k in old} for o, old in zip(obs, old_obs)] == old_obs
    assert Counter(o['dataset_id'] for o in obs) == {'perticarini2024/ey_tds_cibao': 18, 'egidi2024/table2': 12}
    assert len(obs) == len(set(o['source_condition_id'] for o in obs)) == 30
    assert all(o['chemical_sample_n'] == 3 and o['duration_replicate_n'] == 'UNKNOWN' for o in obs)
    assert sum(Q(o['tds_sd_pct']) == 0 for o in obs) == 2
    assert Counter(r['family'] for r in result['comparisons']) == {'primary': 14, 'secondary': 4}
    assert len(result['interactions']) == 6
    assert {(r['coffee_id'], r['grind_id']) for r in result['interactions']} == set(product(m.duration.COFFEES, m.duration.GRINDS[1:4]))
    account = result['condition_accounting']
    assert len(account) == 30 and sum(bool(r['primary_ids']) for r in account) == 28
    assert all(r['primary_ids'] or r['secondary_ids'] for r in account)
    for family in ('primary', 'secondary'):
        rows = [r for r in result['comparisons'] if r['family'] == family]
        for r in rows:
            assert {a['source_condition_id'] for a in account if r['comparison_id'] in a[family+'_ids']} == set(r['coefficients'])
    for r in result['interactions']:
        assert {a['source_condition_id'] for a in account if r['interaction_id'] in a['interaction_ids']} == set(r['coefficients'])
    assert all(o['coffee_id'] == 'cibao' and o['temperature_degC'] == '93.4'
               and o['grind_id'] in ('extra_fine', 'extra_coarse') for o in obs if o['nominal_pressure_bar'] == '12')


def test_key_join_independent_of_both_file_and_observation_order(tmp_path):
    expected, result = bundle()
    for _, filename, _ in m.duration.INPUTS:
        src = m.ROOT / 'puckworks/data' / filename
        with src.open(newline='') as stream:
            rows = list(csv.reader(stream))
        path = tmp_path / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', newline='') as stream:
            csv.writer(stream).writerows([rows[0]] + list(reversed(rows[1:])))
    obs, _ = m.load_observations(tmp_path)
    assert obs == expected
    random.Random(81).shuffle(obs)
    assert m.compute(obs) == result
    for bad in (obs[:-1], obs + [obs[0]]):
        with pytest.raises(ValueError, match='support'):
            m.compute(bad)


def test_independent_decimal_arithmetic_from_original_csvs():
    # Independent field parser and subtraction; no producer coefficients or source lookup.
    raw = {}
    for coffee, filename, fields in [
        ('cibao', 'perticarini2024/ey_tds_cibao.csv', ('T_degC', 'granulometry', 'p_bar', 'tau_s', 'TDS_pct', 'EY_pct')),
        ('modoetia', 'egidi2024/table2_egidi2024_tds_ey.csv', ('T [degC]', 'Granulometry', 'p [bar]', 'tau [s]', 'TDS [%]', 'EY [%]'))]:
        with (m.ROOT / 'puckworks/data' / filename).open() as stream:
            for row in csv.DictReader(stream):
                t, g, p, tau, c, e = [row[k] for k in fields]
                raw[coffee, t, g.lower().replace(' ', '_'), p] = tuple(map(Decimal, (tau, c, e)))
    _, result = bundle()
    for r in result['comparisons']:
        key = (r['coffee_id'], r['temperature_degC'], r['grind_id'])
        lo, hi = [raw[key+(p,)] for p in (r['pressure_from_bar'], r['pressure_to_bar'])]
        got = [r['duration']['nominal']['exact'], r['tds']['nominal']['exact'], r['ey_delta_pp']['exact']]
        assert list(map(Q, got)) == [Q(b-a) for a, b in zip(lo, hi)]
        assert r['tds']['units'] == 'percentage points' and r['duration']['units'] == 's'
    for r in result['interactions']:
        def pressure_delta(t):
            return raw[r['coffee_id'], t, r['grind_id'], '9'][1] - raw[r['coffee_id'], t, r['grind_id'], '6'][1]
        assert Q(r['tds']['nominal']['exact']) == Q(pressure_delta('93.4')-pressure_delta('90.4'))


def test_all_eighteen_accepted_duration_values_and_contract():
    obs, result = bundle()
    accepted = json.loads((m.PREDECESSOR / 'contrasts.json').read_text())
    old = {r['contrast_id']: r for r in accepted['contrasts'] if r['kind'] == 'duration'}
    assert len(old) == len(result['comparisons']) == 18
    values = {o['source_condition_id']: o['tau_s'] for o in obs}
    for r in result['comparisons']:
        a, b = old[r['predecessor_duration_id']], r['duration']
        assert r['coefficients'] == a['terms']
        for k, prior in [('nominal', 'nominal_s'), ('lower', 'lower_s'), ('upper', 'upper_s'), ('critical_allowance', 'critical_h_s')]:
            assert b[k]['exact'] == a[prior]
        assert b['conditional_status'] == a['box_status']
        for h in ('0', '1/3', '0.5', '5'):
            assert m.duration_box(r['coefficients'], values, h)['lower']['exact'] == m.duration.enclosure(a['terms'], values, h)['lower_s']


def test_exposed_independent_checkpoints_and_opposition():
    _, result = bundle()
    hot, cool = [pick(result, 'cibao', t, 'optimal') for t in ('93.4', '90.4')]
    for row, c, e, bounds in [(hot, '-1/5', '-29/50', ('-3/10', '-1/10')),
                               (cool, '3/10', '19/100', ('1/5', '2/5'))]:
        assert row['duration']['nominal']['exact'] == '-6'
        assert (row['duration']['lower']['exact'], row['duration']['upper']['exact']) == ('-7', '-5')
        assert row['tds']['nominal']['exact'] == c and row['ey_delta_pp']['exact'] == e
        assert (row['tds']['lower']['exact'], row['tds']['upper']['exact']) == bounds
    optimal = next(r for r in result['interactions'] if (r['coffee_id'], r['grind_id']) == ('cibao', 'optimal'))
    region = optimal['shorter_with_opposite_tds_region']
    assert not region['empty'] and region['h_C_upper_exclusive']['exact'] == '1/10'
    assert region['h_tau_upper_exclusive']['exact'] == '3'
    fine = next(r for r in result['interactions'] if (r['coffee_id'], r['grind_id']) == ('modoetia', 'fine'))
    assert fine['tds']['nominal']['exact'] == '3/10' and fine['tds']['critical_allowance']['exact'] == '3/40'
    assert fine['tds']['conditional_status'] == 'positive' and fine['conditional_opposition'] == 'unresolved'
    assert fine['opposite_directions_strict_region']['h_C_upper_exclusive']['exact'] == '1/20'
    extra = pick(result, 'cibao', '93.4', 'extra_fine', '9', '12')
    assert extra['tds']['nominal']['exact'] == '1/10' and extra['ey_delta_pp']['exact'] == '-8/25'


def test_exact_zero_touches_printed_ties_and_joint_component_preservation():
    _, result = bundle()
    fine = pick(result, 'modoetia', '93.4', 'fine')
    coarse = pick(result, 'modoetia', '93.4', 'coarse')
    assert (fine['tds']['lower']['exact'], fine['tds']['upper']['exact']) == ('0', '1/5')
    assert (coarse['tds']['lower']['exact'], coarse['tds']['upper']['exact']) == ('-1/5', '0')
    assert coarse['conditional_joint'] == 'SHORTER / TDS SIGN UNRESOLVED'
    assert not coarse['tds']['printed_tie']
    optimal = pick(result, 'modoetia', '93.4', 'optimal')
    assert optimal['conditional_joint'] == 'DURATION SIGN UNRESOLVED / HIGHER TDS'
    assert optimal['duration']['printed_tie'] and optimal['joint_strict_region']['empty']
    for r in result['comparisons']:
        t, c = r['duration'], r['tds']
        region = r['joint_strict_region']
        assert region['empty'] == (t['printed_tie'] or c['printed_tie'])
        assert region['h_tau_upper_exclusive'] == t['critical_allowance']
        assert region['h_C_upper_exclusive'] == c['critical_allowance']
    assert result['counts']['conditional_primary_joint'] == {
        'SHORTER / LOWER TDS': 5, 'SHORTER / HIGHER TDS': 2, 'SHORTER / TDS SIGN UNRESOLVED': 1,
        'DURATION SIGN UNRESOLVED / LOWER TDS': 2, 'DURATION SIGN UNRESOLVED / HIGHER TDS': 1,
        'DURATION SIGN UNRESOLVED / TDS SIGN UNRESOLVED': 3}


def test_exact_box_vertices_and_exclusive_boundaries():
    obs, result = bundle()
    values = {o['source_condition_id']: Q(o['tds_mean_pct']) for o in obs}
    for r in result['comparisons'] + result['interactions']:
        terms = r['coefficients']
        b = r['tds']
        threshold = Q(b['critical_allowance']['exact'])
        assert b['coefficient_l1'] == (4 if 'interaction_id' in r else 2)
        for h in (Q(0), Q('0.05'), threshold):
            vertices = [sum(a*(values[k]+s*h) for (k, a), s in zip(terms.items(), signs))
                        for signs in product((-1, 1), repeat=len(terms))]
            image = m.box(terms, values, h, 'percentage points')
            assert (Q(image['lower']['exact']), Q(image['upper']['exact'])) == (min(vertices), max(vertices))
        assert m.box(terms, values, threshold, 'percentage points')['conditional_status'] == 'unresolved'
        if threshold:
            below = threshold - Q(1, 10**40)
            assert m.box(terms, values, below, 'percentage points')['conditional_status'] == b['nominal_status']
        else:
            assert b['printed_tie'] and m.box(terms, values, 0, 'percentage points')['conditional_status'] == 'unresolved'


def test_shared_original_condition_cancellation_and_structural_zero():
    _, result = bundle()
    for identity in result['arithmetic_identities']:
        assert len(identity['composed_coefficients']) == 2
        assert not identity['residual_coefficients']
        for field, radius in [('tds', '1/10'), ('duration', '1')]:
            residual, composed = identity[field+'_residual'], identity[field+'_composed']
            assert composed['coefficient_l1'] == 2 and composed['radius']['exact'] == radius
            assert residual['coefficient_l1'] == 0 and residual['radius']['exact'] == '0'
            assert residual['critical_allowance'] is None and residual['conditional_status'] == 'structural_zero'
        for h in ('0', '0.05', '1000000'):
            b = m.box({}, {}, h, 'percentage points')
            assert b['lower']['exact'] == b['upper']['exact'] == b['radius']['exact'] == '0'
            assert b['critical_allowance'] is None


@pytest.mark.parametrize('hc,ht', [('-0.1', '0.5'), ('0.05', '-0.1')])
def test_negative_allowances_rejected_before_writing(tmp_path, hc, ht):
    with pytest.raises(ValueError, match='nonnegative'):
        m.write(tmp_path/'output', hc, ht, make_figure=False)
    assert not (tmp_path/'output').exists()
    command = [sys.executable, '-m', m.__name__, '--output', str(tmp_path/'cli'),
               '--tds-allowance-pp', hc, '--duration-allowance-s', ht, '--no-figure']
    p = subprocess.run(command, capture_output=True, text=True)
    assert p.returncode == 2 and 'nonnegative' in p.stderr and not (tmp_path/'cli').exists()


def test_offline_deterministic_numerical_outputs_and_preservation(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError('numerical reproduction must be offline')
    monkeypatch.setattr(socket, 'socket', no_network)
    a = m.write(tmp_path/'a', make_figure=False)
    b = m.write(tmp_path/'b', make_figure=False)
    assert a == b
    for path in (tmp_path/'a').iterdir():
        assert path.read_bytes() == (tmp_path/'b'/path.name).read_bytes() == (m.OUTPUT/path.name).read_bytes()
    for name, expected in a['predecessor_sha256'].items():
        assert hashlib.sha256((m.ROOT/name).read_bytes()).hexdigest() == expected
    for name in ('primary', 'secondary'):
        with (tmp_path/'a'/f'{name}.csv').open() as stream:
            rows = list(csv.DictReader(stream))
        assert len(rows) == (14 if name == 'primary' else 4)
        assert all(r['tds_units'] == 'percentage points' and r['duration_units'] == 's' for r in rows)


def test_committed_figure_exact_data_binding():
    bundle = json.loads((m.OUTPUT/'contrasts.json').read_text())
    root = ET.parse(m.OUTPUT/'COMPARISON.svg').getroot()
    groups = {g.get('id'): g for g in root.iter() if g.get('data-tds-nominal') is not None}
    primary = [r for r in bundle['comparisons'] if r['family'] == 'primary']
    assert set(groups) == {r['comparison_id'] for r in primary}
    for r in primary:
        for field in ('duration', 'tds'):
            for k in ('nominal', 'lower', 'upper'):
                assert groups[r['comparison_id']].get(f'data-{field}-{k}') == r[field][k]['exact']
    texts = ''.join(root.itertext())
    assert '±1 s and ±0.1 pp' in texts and 'Not experimental error bars' in texts


def test_figure_actual_positions_extents_and_repeatability(tmp_path, monkeypatch):
    pytest.importorskip('matplotlib')
    from matplotlib.axes import Axes
    calls = []
    errorbar = Axes.errorbar
    def capture(self, x, y, *args, **kwargs):
        calls.append((x, y, kwargs['xerr'], kwargs['yerr']))
        return errorbar(self, x, y, *args, **kwargs)
    monkeypatch.setattr(Axes, 'errorbar', capture)
    data = m.write(tmp_path/'a')
    m.figure(data, tmp_path/'b.svg')
    assert (tmp_path/'a'/'COMPARISON.svg').read_bytes() == (tmp_path/'b.svg').read_bytes()
    primary = [r for r in data['comparisons'] if r['family'] == 'primary']
    expected = [(float(Q(r['duration']['nominal']['exact'])), float(Q(r['tds']['nominal']['exact'])), 1., .1) for r in primary]
    assert calls == expected + expected

"""Scientific-risk fixtures, independently checked certificates and source reuse."""
from collections import Counter
from copy import deepcopy
from fractions import Fraction as Q
from itertools import product
import json
import math
import subprocess
import sys

import pytest

from puckworks.analysis import khamitova2020_common_scaling as p
from puckworks.analysis import khamitova2020_common_scaling_check as c


@pytest.fixture(scope='module')
def report():
    return p.build_report()


def fixture_certificate(boxes, forces=(0, 1, 2, 3), species=('a', 'b', 'c', 'd')):
    solved = p.solve(boxes, forces, species)
    m = {'cost': p.encode_root(solved['root']),
         'certificate': p.certificate(solved['cycle'], solved['edges'], None, None, forces, species),
         'force_factors': {str(f): p.encode_mono(v) for f, v in solved['g'].items()},
         'analyte_amplitudes_mg_per_reference_40ml': {s: p.encode_mono(v) for s, v in solved['a'].items()},
         'cells': [{'key': [None, None, f, s], 'prediction': p.encode_mono(solved['predictions'][f, s])}
                   for f, s in boxes]}
    c.verify_cycle(m['certificate'], solved['root'], boxes)
    c.verify_brackets(m['cost'])
    assert c.verify_witness(m, boxes, forces, species) == len(boxes)
    assert c.log_lp(boxes, forces, species) == pytest.approx(math.log10(float(solved['root'][0]))/solved['root'][1], abs=1e-9)
    return solved, m


def test_positive_rank_one_gauge_and_analyte_units():
    factors = dict(zip('abcd', (Q(3), Q(5), Q(7), Q(11))))
    boxes = {(f, s): (Q(f+1)*factors[s],)*2 for f, s in product(range(4), 'abcd')}
    solved, m = fixture_certificate(boxes)
    assert solved['root'] == (1, 1) and m['certificate']['kind'] == 'OBJECTIVE_FLOOR'
    # Another positive gauge produces exactly the same products. Renormalize it
    # before checking the declared g_0=1 representation contract.
    scale = Q(17, 3)
    changed_g = {f: p.mul(v, (scale, 0)) for f, v in solved['g'].items()}
    changed_a = {s: p.div(v, (scale, 0)) for s, v in solved['a'].items()}
    for f, s in boxes:
        assert p.mono_compare(p.mul(changed_g[f], changed_a[s]), solved['predictions'][f, s], solved['root']) == 0
    for f in changed_g:
        assert p.mono_compare(p.div(changed_g[f], changed_g[0]), solved['g'][f], solved['root']) == 0
    units = dict(zip('abcd', (Q(1000), Q(1, 40), Q(3, 7), Q(2))))
    scaled = {cell: tuple(v*units[cell[1]] for v in box) for cell, box in boxes.items()}
    result, _ = fixture_certificate(scaled)
    assert result['root'] == (1, 1)


def test_known_four_cell_obstruction_orientation_and_attainment():
    boxes = {(f, s): (Q(1), Q(1)) for f, s in product((0, 1), ('a', 'b'))}
    boxes[0, 'a'] = (Q(4), Q(4))
    solved, _ = fixture_certificate(boxes, (0, 1), ('a', 'b'))
    assert p.root_compare(solved['root'], (Q(4), 4)) == 0
    assert c.four_cell_root(boxes, (0, 1), ('a', 'b')) == (4, 4)
    cycle = solved['cycle']
    reverse = cycle[:1]+tuple(reversed(cycle[1:]))
    assert p.cycle_ratio(cycle, solved['edges']) == 4
    assert p.cycle_ratio(reverse, solved['edges']) == Q(1, 4)
    # Explicit hand solution: g=(1,1/2), a=(2*sqrt(2),sqrt(2)).
    root = solved['root']
    g = {0: (Q(1), 0), 1: (Q(1, 2), 0)}
    a = {'a': (Q(2), 1), 'b': (Q(1), 1)}
    for cell, (lo, hi) in boxes.items():
        y = p.mul(g[cell[0]], a[cell[1]])
        assert p.mono_compare(y, (lo, -1), root) >= 0
        assert p.mono_compare(y, (hi, 1), root) <= 0


def test_six_cycle_invisible_to_every_four_cell_bound():
    boxes = {(f, s): (Q(1, 8), Q(8)) for f, s in product(range(4), 'abcd')}
    for f, s in enumerate('abc'):
        boxes[f, s] = (Q(1), Q(1))
    for cell in [(0, 'b'), (1, 'c'), (2, 'a')]:
        boxes[cell] = (Q(2), Q(8))
    solved, m = fixture_certificate(boxes)
    assert c.four_cell_root(boxes, range(4), 'abcd') == (1, 4)
    assert p.root_compare(solved['root'], (Q(8), 6)) == 0
    assert len(solved['cycle']) == 6
    # Independent explicit attaining witness: every prediction is sqrt(2).
    m['force_factors'] = {str(f): {'coefficient': '1', 'exponent': 0} for f in range(4)}
    m['analyte_amplitudes_mg_per_reference_40ml'] = {s: {'coefficient': '1', 'exponent': 1} for s in 'abcd'}
    for cell in m['cells']:
        cell['prediction'] = {'coefficient': '1', 'exponent': 1}
    assert c.verify_witness(m, boxes, range(4), 'abcd') == 16
    # Invariance for nonzero costs under independent positive unit rescalings.
    units = dict(zip('abcd', (Q(1000), Q(1, 40), Q(3, 7), Q(2))))
    scaled, _ = fixture_certificate({cell: tuple(v*units[cell[1]] for v in box) for cell, box in boxes.items()})
    assert p.root_compare(scaled['root'], solved['root']) == 0


def test_complete_directed_cycle_coverage():
    for ns, expected in [(4, {2: 16, 4: 72, 6: 192, 8: 144}), (3, {2: 12, 4: 36, 6: 48})]:
        cycles = p.cycles(4, ns)
        assert Counter(map(len, cycles)) == expected
        assert len(set(cycles)) == len(cycles)
        for cycle in cycles:
            assert len(set(cycle)) == len(cycle) and cycle[0] == min(cycle)
            assert cycle[:1]+tuple(reversed(cycle[1:])) in cycles
            for u, v in zip(cycle, cycle[1:]+cycle[:1]):
                assert (u < 4) != (v < 4)


@pytest.mark.parametrize('field,value,available', [
    ('rsd', None, (True, True, False)), ('rsd', Q(-1), (True, True, False)),
    ('rsd', Q(100), (True, True, False)), ('rsd_support', 'UNSUPPORTED', (True, True, False)),
    ('rsd_rounding_support', 'UNSUPPORTED', (True, True, False)),
    ('amount_decimal_places', None, (True, False, False)),
    ('amount_decimal_places', True, (True, False, False)),
    ('amount_decimal_places', -1, (True, False, False)),
    ('amount_decimal_places', 2.0, (True, False, False)),
    ('rsd_decimal_places', False, (True, True, False)),
    ('rsd_decimal_places', -1, (True, True, False)),
    ('rsd_decimal_places', '1', (True, True, False)),
    ('amount_rounding_support', 'UNSUPPORTED', (True, False, False)),
    ('amount', Q('0.005'), (True, False, False)),
    ('amount', Q(0), (False, False, False)), ('amount', Q(-1), (False, False, False)),
    ('amount', 'NaN', (False, False, False)), ('amount', True, (False, False, False)),
    ('mean_support', 'UNSUPPORTED', (False, False, False)),
    ('concentration_decimal_places', None, (True, True, True)),
    ('concentration_rounding_support', 'UNSUPPORTED', (True, True, True)),
    ('precision_support', 'UNSUPPORTED', (True, True, True)),
])
def test_layer_specific_support(field, value, available):
    row = deepcopy(p.load_observations()[0])
    row[field] = value
    for layer, supported in zip(p.LAYERS, available):
        box, why = p.layer_bounds(row, layer)
        assert (box is not None) == supported
        assert bool(why) != supported
        assert (box, why) == c.bounds_from_source(row, layer)


def test_per_cell_precision_not_float_rendering():
    row = next(r for r in p.load_observations() if r['amount_string'] == '133.30')
    assert str(float(row['amount'])) == '133.3'
    assert p.half_place(row['amount_decimal_places']) == Q('.005')
    assert p.half_place(row['rsd_decimal_places']) == Q('.05')
    x = row['amount']
    assert p.layer_bounds(row, 'D')[0] == (x-Q('.005'), x+Q('.005'))
    row['amount_decimal_places'] = 3
    assert p.layer_bounds(row, 'D')[0] == (x-Q('.0005'), x+Q('.0005'))


def test_missing_support_retains_all_requests_and_incomplete_verdict():
    rows = p.load_observations()
    rows[0]['rsd'] = None
    report = p.build_report(rows)
    assert len(report['matrices']) == 135
    receipt = c.check(report, observations=rows)
    assert receipt['status'] == 'INCOMPLETE_SUPPORT'
    assert receipt['supported_matrices'] == 131
    for m in report['matrices']:
        assert len(m['cells']) == (16 if m['omitted_analyte'] is None else 12)
    # Missing amount precision leaves nominal work, even if both sensitivity layers fail.
    rows[0]['amount_decimal_places'] = None
    report = p.build_report(rows)
    assert c.check(report, observations=rows)['supported_matrices'] == 127
    incomplete = next(m for m in report['matrices'] if m['status'] == 'UNSUPPORTED')
    incomplete['cells'][0]['L'] = '1'
    with pytest.raises(ValueError, match='Stored interval'):
        c.check(report, observations=rows)


@pytest.mark.parametrize('duplicate', [False, True])
def test_missing_duplicate_source_keys_fail(duplicate):
    rows = p.load_observations()
    rows = rows+[rows[0]] if duplicate else rows[:-1]
    with pytest.raises(ValueError):
        p.build_report(rows)
    with pytest.raises(ValueError):
        c.source_index(rows)


@pytest.mark.parametrize('box', [(0, 1), (-1, 2), (2, 1)])
def test_nonpositive_or_reversed_intervals_rejected(box):
    with pytest.raises(ValueError):
        p.solve({(0, 'a'): tuple(map(Q, box))}, (0,), ('a',))


def test_independent_source_verification_all_135_lp_and_qualifications(report):
    receipt = c.check(report, lp=True)
    assert receipt['status'] == 'COMPLETE_EXACT_OPTIMA_VERIFIED'
    assert receipt['primary_interval_checks'] == 432
    assert receipt['diagnostic_interval_checks'] == 1296
    assert receipt['one_sided_inequalities'] == 3456
    assert len(receipt['secondary_lp']['matrices']) == 135
    assert receipt['secondary_lp']['maximum_absolute_difference_dex'] < 1e-9
    mismatches = [r for r in p.load_observations() if 'SOURCE_UNIT_PAIR_MISMATCH' in r['qualification']]
    assert len(mismatches) == 1
    assert p.key(mismatches[0]) == [88, 7, 10, 'total CQA']
    assert mismatches[0]['amount'] == Q('131.84')
    # Both task-selection examples are recomputed, never fed into the optimizer.
    example = next(m for m in report['matrices'] if (m['temperature_C'], m['pressure_bar'], m['layer'], m['omitted_analyte']) == (98, 9, 'N', None))
    assert c.root_order(c.root_data(example['cost']), (Q(3324118, 2182641), 4)) == 0
    six = next(m for m in report['matrices'] if (m['temperature_C'], m['pressure_bar'], m['layer'], m['omitted_analyte']) == (93, 11, 'N', None))
    assert c.root_order(c.root_data(six['cost']), (Q(9263886589, 8654989675), 6)) == 0
    assert sum(m['longer_cycle_strictly_improves'] for m in report['matrices']) == 12


@pytest.mark.parametrize('attack', ['cycle_direction', 'cycle_product', 'cycle_cell', 'root', 'degree',
    'factor', 'prediction', 'gauge', 'bracket', 'reciprocal', 'missing_matrix', 'duplicate_matrix',
    'missing_cell', 'duplicate_cell', 'interval', 'four_bound', 'ratio', 'gap', 'floor', 'provenance'])
def test_certificate_tampering_is_rejected(report, attack):
    bad = deepcopy(report)
    m = bad['matrices'][0]
    if attack == 'cycle_direction':
        m['certificate']['edges'][0]['from'], m['certificate']['edges'][0]['to'] = m['certificate']['edges'][0]['to'], m['certificate']['edges'][0]['from']
    elif attack == 'cycle_product': m['certificate']['R'] = '2'
    elif attack == 'cycle_cell': m['certificate']['edges'][0]['cell_key'][0] = 93
    elif attack == 'root': m['cost']['radicand'] = '2'
    elif attack == 'degree': m['cost']['degree'] = True
    elif attack == 'factor': m['force_factors']['15']['coefficient'] = '1000'
    elif attack == 'prediction': m['cells'][0]['prediction']['coefficient'] = '1000'
    elif attack == 'gauge': m['force_factors']['10']['coefficient'] = '2'
    elif attack == 'bracket': m['cost']['M_bracket'] = ['1', '1']
    elif attack == 'reciprocal': m['cost']['reciprocal_bracket'] = ['1', '1']
    elif attack == 'missing_matrix': bad['matrices'].pop()
    elif attack == 'duplicate_matrix': bad['matrices'].append(m)
    elif attack == 'missing_cell': m['cells'].pop()
    elif attack == 'duplicate_cell': m['cells'].append(m['cells'][0])
    elif attack == 'interval': m['cells'][0]['L'] = '1'
    elif attack == 'four_bound': m['four_cell_lower_bound'] = p.encode_root((Q(1), 1))
    elif attack == 'ratio': bad['pairwise_analyte_ratios'][0]['ratio_L'] = '1'
    elif attack == 'gap': m['gap_exact_relation'] = 'POSITIVE'
    elif attack == 'floor':
        floor = next(m for m in bad['matrices'] if m['cost']['radicand'] == '1')
        floor['cells'][0]['prediction']['coefficient'] = '0'
    elif attack == 'provenance': bad['input_sha256'][p.PREDECESSOR+'/observations.csv'] = 'bad'
    with pytest.raises(ValueError):
        c.check(bad)


def test_certified_brackets_and_tiny_exact_gap():
    a, b = (Q(1)+Q(1, 10**50), 6), (Q(1), 1)
    assert p.root_compare(a, b) > 0
    assert f'{p.approximation(a)-p.approximation(b):.12f}' == '0.000000000000'
    for root in [a, b, (Q(8), 6), (Q(10**60), 4)]:
        c.verify_brackets(p.encode_root(root))


@pytest.mark.slow
def test_deterministic_cli_twice_and_committed_scientific_artifacts(tmp_path):
    names = ('results.json', 'primary_summary.csv', 'analyte_influence.csv',
             'factors_predictions.csv', 'pairwise_ratios.csv')
    for directory in (tmp_path/'first', tmp_path/'second'):
        subprocess.run([sys.executable, '-m', 'puckworks.analysis.khamitova2020_common_scaling',
                        '--output', str(directory)], cwd=p.ROOT, check=True, capture_output=True)
    for name in names:
        assert (tmp_path/'first'/name).read_bytes() == (tmp_path/'second'/name).read_bytes() == (p.BUNDLE/name).read_bytes()
    subprocess.run([sys.executable, '-m', 'puckworks.analysis.khamitova2020_common_scaling_check',
                    '--results', str(tmp_path/'first/results.json'), '--output', str(tmp_path/'checked.json'), '--lp'],
                    cwd=p.ROOT, check=True, capture_output=True)
    assert json.loads((tmp_path/'checked.json').read_text())['status'] == 'COMPLETE_EXACT_OPTIMA_VERIFIED'


def test_checker_does_not_call_producer_constructors(report, monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError('Independent checker called producer')
    for name in ('solve', 'layer_bounds', 'cycles', 'graph'):
        monkeypatch.setattr(p, name, forbidden)
    assert c.check(report)['status'] == 'COMPLETE_EXACT_OPTIMA_VERIFIED'

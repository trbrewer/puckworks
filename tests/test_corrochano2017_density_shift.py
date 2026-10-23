"""Analytical dependency/decision controls; retained data serve only replay checks."""
import csv
from fractions import Fraction as F
from itertools import combinations, product
import json
import subprocess
import sys

import pytest

from puckworks.analysis import corrochano2017_density_shift as d
from puckworks.analysis import corrochano2017_dry_compaction as g


def axis(anchor=0, trace=0, reverse=False):
    return g.Axis({'values': [0, 100], 'positions_pt': [100, 0] if reverse else [0, 100]},
                  F(anchor), F(trace))


def segments(points):
    points = [tuple(map(F, p)) for p in points]
    return list(zip(points, points[1:]))


def reading(bounds, status='SUPPORTED'):
    return dict(bounds_pt=tuple(map(F, bounds)) if bounds is not None else None,
                status=status, full_support=bounds is not None, reason='analytical fixture')


def test_additive_matrix_invariant_under_common_affine_calibration():
    offsets = [F(-100), F(1, 7), F(23)]
    levels = [F(-3), F(2), F(5, 3), F(12)]  # deliberately nonmonotone
    for alpha, beta in product([F(-1000), F(2, 3), F(900)], [F(1, 5), F(1), F(17)]):
        z = [[c+h for h in levels] for c in offsets]
        rho = [[alpha+beta*x for x in row] for row in z]
        for i, j in combinations(range(3), 2):
            for a, b in combinations(range(4), 2):
                cz = z[i][b]-z[i][a]-z[j][b]+z[j][a]
                cr = rho[i][b]-rho[i][a]-rho[j][b]+rho[j][a]
                assert cr == beta*cz == 0
                assert rho[i][b] == (alpha+beta*offsets[i])+beta*levels[b]
        # An analytical perturbation supplies nonzero positive and negative controls.
        for epsilon in [F(-1, 11), F(1, 13)]:
            assert (beta*epsilon > 0) == (epsilon > 0)
            assert (beta*epsilon < 0) == (epsilon < 0)


def test_shared_scale_can_separate_when_individually_scaled_intervals_overlap():
    a, b = reading([10, 11]), reading([8, 9])
    beta = (F(1), F(2))
    assert d.scale(a['bounds_pt'], beta) == (10, 22)
    assert d.scale(b['bounds_pt'], beta) == (8, 18)
    assert g.subtract(d.scale(a['bounds_pt'], beta), d.scale(b['bounds_pt'], beta)) == (-8, 14)
    contrast = d.compare(a, b, beta)
    assert contrast['bounds_pt'] == (1, 3)
    assert contrast['bounds_kg_m3'] == (1, 6)
    assert contrast['classification'] == 'STRICTLY_SEPARATED'
    assert contrast['difference_orientation'] == 'first_minus_second'


@pytest.mark.parametrize('bounds,expected', [((2, 4), (6, 20)), ((-4, -2), (-20, -6)),
                                           ((-2, 4), (-10, 20)), ((0, 0), (0, 0))])
def test_sign_safe_endpoint_product_rule(bounds, expected):
    assert d.scale(tuple(map(F, bounds)), (F(3), F(5))) == expected


def test_calibration_derived_from_independent_anchors_and_rejects_degeneracy():
    inherited = dict(axes={'density': {'values': [300, 650], 'positions_pt': ['25', '5']}},
                     anchor_guard_pt='1')
    c = d.calibration(inherited)
    assert c['nominal_separation_pt'] == 20
    assert c['beta_kg_m3_per_pt'] == (F(175, 11), F(175, 9))
    inherited['axes']['density']['positions_pt'] = ['7', '5']
    with pytest.raises(ValueError, match='degenerate'):
        d.calibration(inherited)


def test_full_trace_guards_survive_cancellation_and_widening_cannot_create_separation():
    first = segments([(0, 0), (10, -20)])
    second = segments([(0, 0), (10, -10)])
    previous = None
    for guard in [0, 1, 2, 4]:
        increments = []
        for ss in (first, second):
            rr = [d.read_coordinates(ss, f, axis(), axis(trace=guard)) for f in (2, 8)]
            assert all(r['full_support'] for r in rr)
            inc = d.increment(*rr, (F(1), F(1)))
            increments.append(inc)
        assert increments[0]['bounds_pt'] == (12-2*guard, 12+2*guard)
        assert increments[1]['bounds_pt'] == (6-2*guard, 6+2*guard)
        contrast = d.compare(*increments, (F(1), F(1)))
        assert contrast['bounds_pt'] == (6-4*guard, 6+4*guard)
        if previous:
            assert contrast['bounds_pt'][0] <= previous['bounds_pt'][0]
            assert contrast['bounds_pt'][1] >= previous['bounds_pt'][1]
            if previous['sign'] == 0:
                assert contrast['sign'] == 0
        previous = contrast


def test_entire_force_strip_retains_interior_extrema_not_just_nominal_crossing():
    ss = segments([(0, 0), (4, -10), (5, -1), (6, -8), (10, 0)])
    r = d.read_coordinates(ss, 5, axis(trace=1), axis(trace=1))
    nominal = d.read_coordinates(ss, 5, axis(), axis(trace=1))
    assert r['query_pt'] == (4, 6) and r['bounds_pt'] == (0, 11)
    assert nominal['bounds_pt'] == (0, 2)  # nominal-only implementation misses the peak


def test_constant_reverse_multiple_branches_are_retained_and_can_qualify():
    ss = segments([(0, 0), (10, -10), (0, -20), (10, -30)])
    r = d.read_coordinates(ss, 5, axis(), axis())
    assert r['status'] == 'AMBIGUOUS' and r['full_support']
    assert r['components_z_pt'] == [(5, 5), (15, 15), (25, 25)]
    assert r['bounds_pt'] == (5, 25)
    plateau = d.read_coordinates(segments([(0, 0), (5, -5), (5, -15), (10, -20)]),
                                 5, axis(), axis())
    assert plateau['status'] == 'AMBIGUOUS' and plateau['bounds_pt'] == (5, 15)
    assert d.increment(r, plateau, (F(1), F(1)))['status'] == 'AMBIGUOUS'


def test_genuine_gaps_and_endpoint_support_fail_even_with_nominal_crossing():
    ss = segments([(0, 0), (4, -4)]) + segments([(6, -6), (10, -10)])
    r = d.read_coordinates(ss, 4, axis(trace=1), axis())
    assert r['nominal_support'] and not r['full_support']
    assert r['reason'] == 'QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP'
    assert r['bounds_pt'] is None
    r = d.read_coordinates(ss, 1, axis(anchor=1, trace=1), axis())
    assert r['nominal_support'] and not r['full_support']
    assert r['reason'] == 'QUERY_EXCEEDS_RECORDED_ENDPOINT'


def test_force_anchor_corners_and_trace_relaxations_enclose_every_common_choice():
    qa = axis(anchor=1, trace=1)
    beta = (F(2), F(3))
    ss = segments([(-10, 20), (110, -220)])  # z=2*x
    rr = [d.read_coordinates(ss, force, qa, axis(trace=1)) for force in (20, 80)]
    inc = d.increment(*rr, beta)
    for p0, p1, dx0, dx1, dz0, dz1, slope in product(
            [F(-1), F(0), F(1)], [F(99), F(100), F(101)],
            [-1, 0, 1], [-1, 0, 1], [-1, 0, 1], [-1, 0, 1], beta):
        x0 = F(4, 5)*p0+F(1, 5)*p1+dx0
        x1 = F(1, 5)*p0+F(4, 5)*p1+dx1
        value = slope*(2*x1+dz1-2*x0-dz0)
        assert inc['bounds_kg_m3'][0] <= value <= inc['bounds_kg_m3'][1]


def test_subtraction_stays_within_sample_before_grind_aggregation():
    increments = {f'B{k}': d.increment(reading([offset, offset+1]),
                                      reading([offset+10, offset+11]), (F(1), F(1)))
                  for k, offset in enumerate([0, 100, 200], 1)}
    e = d.envelope(increments, ['B1', 'B2', 'B3'], (F(1), F(1)))
    assert e['bounds_pt'] == (9, 11) and e['completeness'] == 'COMPLETE'
    assert g.subtract((10, 211), (0, 201)) == (-191, 211)  # forbidden aggregate-first
    assert d.increment(reading([10, 20]), reading([1, 2]), (F(1), F(1)))['bounds_pt'] == (-19, -8)


def test_sample_witness_excludes_even_when_complete_grind_envelopes_overlap():
    beta = (F(1), F(1))
    rr = {s: reading([0, 20]) for s in ['B1', 'B2', 'B3', 'E1', 'E2', 'E3']}
    rr.update(B1=reading([10, 11]), E1=reading([8, 9]))
    pair = d.compare(rr['B1'], rr['E1'], beta)
    b = d.envelope(rr, ['B1', 'B2', 'B3'], beta)
    e = d.envelope(rr, ['E1', 'E2', 'E3'], beta)
    assert b['completeness'] == e['completeness'] == 'COMPLETE'
    assert d.compare(b, e, beta)['classification'] == 'NOT_EXCLUDED_BY_THIS_COMPARISON'
    assert d.null_disposition([pair], 990) == 'EXCLUDED_BY_SAMPLE_INCREMENT_SEPARATION'


def test_missing_grind_member_blocks_complete_claim_and_preserves_ambiguity():
    beta = (F(1), F(1))
    rr = {'B1': reading([20, 21], 'AMBIGUOUS'), 'B2': reading([22, 23])}
    env = d.envelope(rr, ['B1', 'B2', 'B3'], beta)
    assert env['missing'] == ['B3'] and env['ambiguous_members'] == ['B1']
    assert env['descriptive_only'] and env['bounds_pt'] == (20, 23)
    assert d.compare(env, reading([0, 1]), beta)['classification'] == 'UNSUPPORTED_OR_INCOMPLETE'


def test_exact_contact_and_tiny_gap_decided_before_display_rounding():
    beta = (F(1), F(1))
    assert d.compare(reading([1, 2]), reading([0, 1]), beta)['sign'] == 0
    result = d.compare(reading([1+F(1, 10**9), 2]), reading([0, 1]), beta)
    assert result['classification'] == 'STRICTLY_SEPARATED'
    assert result['display_pt'][0] == '0.000000' and result['bounds_pt'][0] == F(1, 10**9)


def test_null_coverage_and_numerical_failures_remain_distinct():
    beta = (F(1), F(1))
    num = d.numerical_failure(ArithmeticError('fixture'))
    failed = d.increment(reading([0, 1]), num, beta)
    assert failed['status'] == 'NUMERICALLY_UNRESOLVED'
    nc = d.compare(failed, reading([0, 1]), beta)
    assert nc['classification'] == 'NUMERICALLY_UNRESOLVED'
    missing = d.compare(reading(None, 'UNSUPPORTED'), reading([0, 1]), beta)
    overlap = d.compare(reading([0, 2]), reading([0, 1]), beta)
    assert d.null_disposition([overlap]*990, 990) == 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'
    for comparisons in ([overlap]*989, [overlap, missing], [overlap, nc]):
        assert d.null_disposition(comparisons, 990) == 'UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'
    witness = d.compare(reading([2, 3]), reading([0, 1]), beta)
    assert d.null_disposition([witness, missing, nc], 990) == 'EXCLUDED_BY_SAMPLE_INCREMENT_SEPARATION'


@pytest.fixture(scope='module')
def formal_result():
    return d.analyze()


def test_fixed_unique_reporting_set_and_endpoint_references(formal_result):
    assert [len(formal_result[name]) for name in d.TABLES] == [72, 180, 990, 60, 90]
    for name in d.TABLES:
        assert len({r['id'] for r in formal_result[name]}) == len(formal_result[name])
    readings = {r['id']: r for r in formal_result[d.TABLES[0]]}
    for row in formal_result[d.TABLES[1]]:
        a, b = [readings[key] for key in row['endpoints']]
        assert a['trace'] == b['trace'] == row['trace']
        assert row['bounds_pt'] == g.subtract(b['bounds_pt'], a['bounds_pt'])
    pairs = formal_result[d.TABLES[2]]
    assert sum(r['within_grind'] for r in pairs) == 12*15
    for row in pairs + formal_result[d.TABLES[4]]:
        assert row['first'] < row['second'] and row['force_from_N'] < row['force_to_N']
        assert row['difference_orientation'] == 'first_minus_second'
        assert row['bounds_kg_m3'] == d.scale(row['bounds_pt'], formal_result['calibration']['beta_kg_m3_per_pt'])


def test_exact_predecessor_marginal_replay_and_preserved_bytes(formal_result):
    contract = d.authenticate()
    assert formal_result['marginal_replay']['status'] == 'EXACT_MATCH'
    assert formal_result['marginal_replay']['count'] == 72
    assert formal_result['input_hashes'] == contract['inherited_input_hashes']
    # Every protected input, historical output, producer and test is hash checked.
    for name, digest in contract['preserved_file_hashes'].items():
        assert d.sha256(d.ROOT/name) == digest


def test_committed_outputs_and_offline_cli_reproduce(tmp_path, formal_result):
    script = """
import socket, sys
def denied(*args, **kwargs):
    raise AssertionError('network forbidden')
socket.socket = denied
sys.modules['pymupdf'] = None
sys.modules['fitz'] = None
from puckworks.analysis.corrochano2017_density_shift import main
main()
"""
    subprocess.run([sys.executable, '-c', script, '--output', str(tmp_path)], check=True)
    for name in [t+'.csv' for t in d.TABLES] + ['RESULT.json']:
        assert (tmp_path/name).read_bytes() == (d.OUTPUT/name).read_bytes()
    for name in d.TABLES:
        with (tmp_path/(name+'.csv')).open() as stream:
            assert len(list(csv.DictReader(stream))) == len(formal_result[name])
    assert json.loads((tmp_path/'RESULT.json').read_text())['overall_disposition'] == formal_result['overall_disposition']

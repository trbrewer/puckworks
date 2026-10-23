"""Mathematical controls and adversarial certificates; previews are never oracles."""
from copy import deepcopy
from fractions import Fraction as F
import importlib.util
from itertools import combinations, product
import json
import subprocess
import sys

import pytest

from puckworks.analysis import corrochano2017_density_normalization as n
from puckworks.analysis import corrochano2017_density_shift as d
from puckworks.analysis import corrochano2017_dry_compaction as g


def reading(lo, hi=None, status='SUPPORTED'):
    return dict(bounds_pt=(F(lo), F(lo if hi is None else hi)), status=status,
                full_support=True, reason='ANALYTICAL_FIXTURE')


def axis(anchor=0, trace=0):
    return g.Axis(dict(values=[0, 100], positions_pt=[0, 100]), F(anchor), F(trace))


def segments(points):
    points = [tuple(map(F, p)) for p in points]
    return list(zip(points, points[1:]))


def test_synthetic_pure_scaling_with_nonzero_intercept_and_nonzero_first_level():
    # Construct rho=s*h first, then invert ONE nonzero-intercept calibration.
    for tau, beta in product([F(-9), F(0), F(11, 3)], [F(1, 7), F(3)]):
        levels, amplitudes = [F(2), F(7, 3), F(9)], [F(1), F(4), F(13)]
        z = [[s*h/beta-tau for h in levels] for s in amplitudes]
        for i, j in combinations(range(3), 2):
            for a, b in combinations(range(3), 2):
                result = n.density_ratio_contrast(*(reading(z[s][k]) for s, k in
                                      [(i, a), (i, b), (j, a), (j, b)]), (tau, tau))
                assert result['determinant_pt2'] == (0, 0)
                assert result['classification'] == 'NOT_EXCLUDED_BY_THIS_COMPARISON'
                assert n.ratio_bounds((z[i][a],)*2, (z[i][b],)*2, (tau, tau)) == (levels[b]/levels[a],)*2


@pytest.mark.parametrize('value,sign', [(F(2), 0), (F(2)+F(1, 10**10), 1),
                                        (F(2)-F(1, 10**10), -1)])
def test_contact_strict_signs_pair_reversal_and_display_not_used(value, sign):
    r = n.density_ratio_contrast(reading(1), reading(value), reading(1), reading(2), (F(0), F(0)))
    reverse = n.density_ratio_contrast(reading(1), reading(2), reading(1), reading(value), (F(0), F(0)))
    assert r['sign'] == sign and reverse['sign'] == -sign
    assert reverse['determinant_pt2'] == tuple(-x for x in reversed(r['determinant_pt2']))
    assert r['classification'] == ('STRICTLY_SEPARATED' if sign else 'NOT_EXCLUDED_BY_THIS_COMPARISON')


def test_shared_tau_separates_despite_overlapping_marginal_ratios():
    tau = (F(0), F(10))
    a = n.ratio_bounds((F(1),)*2, (F(2),)*2, tau)
    b = n.ratio_bounds((F(10),)*2, (F(21),)*2, tau)
    assert max(a[0], b[0]) < min(a[1], b[1])
    c = n.density_ratio_contrast(reading(1), reading(2), reading(10), reading(21), tau)
    assert c['determinant_pt2'] == (-101, -1)
    assert c['ratio_difference'][1] < 0
    for t in map(F, range(11)):
        direct = (2+t)/(1+t)-(21+t)/(10+t)
        assert c['ratio_difference'][0] <= direct <= c['ratio_difference'][1]


def test_multiaffine_corners_enclose_interior_and_page_origin_invariance():
    boxes = [(F(1), F(2)), (F(3), F(5)), (F(4), F(7)), (F(8), F(11))]
    tau = (F(2), F(9))
    original = n.determinant_bounds(*boxes, tau)
    for a, b, c, d0, t in product(*[[lo, (lo+hi)/2, hi] for lo, hi in boxes+[tau]]):
        determinant = (b+t)*(c+t)-(d0+t)*(a+t)
        assert original[0] <= determinant <= original[1]
    for shift in [F(-1000), F(17, 3), F(10000)]:
        moved = [tuple(v+shift for v in box) for box in boxes]
        moved_tau = tuple(t-shift for t in tau)
        assert n.determinant_bounds(*moved, moved_tau) == original
        assert n.ratio_bounds(*moved[:2], moved_tau) == n.ratio_bounds(*boxes[:2], tau)


def test_physical_intercept_cannot_be_discarded_for_scaling():
    boxes = [(F(v),)*2 for v in (1, 2, 2, 4)]
    assert n.determinant_bounds(*boxes, (F(0),)*2) == (0, 0)
    assert n.determinant_bounds(*boxes, (F(1),)*2) == (-1, -1)
    # At alpha=beta=1, the physical density determinant is -1, not zero.
    assert (1+2)*(1+2)-(1+4)*(1+1) == -1


@pytest.mark.parametrize('numerator,expected', [((2, 4), (F(2, 5), F(4, 3))),
                                               ((-4, -2), (F(-4, 3), F(-2, 5))),
                                               ((-2, 4), (F(-2, 3), F(4, 3))),
                                               ((0, 0), (F(0), F(0)))])
def test_signed_interval_division(numerator, expected):
    assert n.divide_positive(tuple(map(F, numerator)), (F(3), F(5))) == expected


def test_positive_slope_denominator_and_bad_arithmetic_are_visible():
    contract = dict(axes=dict(density=dict(values=[300, 650], positions_pt=['25', '5'])),
                    anchor_guard_pt='1')
    cal = n.calibration(contract)
    assert cal['beta_kg_m3_per_pt'] == (F(175, 11), F(175, 9))
    expected_tau = [(650*(25+e0)-300*(5+e1))/F(350) for e0, e1 in product([-1, 1], repeat=2)]
    assert cal['tau_pt'] == (min(expected_tau), max(expected_tau))
    contract['axes']['density']['positions_pt'] = ['7', '5']
    with pytest.raises(ValueError, match='degenerate'):
        n.calibration(contract)
    with pytest.raises(ValueError, match='denominator'):
        n.divide_positive((F(-1), F(2)), (F(0), F(5)))
    bad = n.density_ratio_contrast(reading(-1), reading(3), reading(2), reading(4), (F(0), F(1)))
    assert bad['classification'] == 'INVALID_POSITIVITY_OR_ENCLOSURE'
    numeric = d.numerical_failure(ArithmeticError('synthetic arithmetic failure'))
    r = n.density_ratio_contrast(numeric, reading(3), reading(2), reading(4), (F(1), F(1)))
    assert r['classification'] == 'NUMERICALLY_UNRESOLVED'
    assert 'synthetic arithmetic failure' in r['reason']


def test_full_strip_components_extrema_both_trace_allowances_and_no_gap_fill():
    ss = segments([(0, 0), (4, -10), (5, -1), (6, -8), (10, 0)])
    r = d.read_coordinates(ss, 5, axis(trace=1), axis(trace=1))
    assert r['query_pt'] == (4, 6) and r['bounds_pt'] == (0, 11)
    no_x = d.read_coordinates(ss, 5, axis(), axis(trace=1))
    no_z = d.read_coordinates(ss, 5, axis(trace=1), axis())
    assert no_x['bounds_pt'] == (0, 2) and no_z['bounds_pt'] == (1, 10)
    gap = segments([(0, 0), (4, -4)])+segments([(6, -6), (10, -10)])
    missing = d.read_coordinates(gap, 4, axis(trace=1), axis())
    assert missing['nominal_support'] and not missing['full_support']
    assert missing['reason'] == 'QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP'
    branches = d.read_coordinates(segments([(0, 0), (10, -10), (0, -20), (10, -30)]),
                                  5, axis(), axis())
    assert branches['status'] == 'AMBIGUOUS'
    assert branches['components_z_pt'] == [(5, 5), (15, 15), (25, 25)]
    assert n.density_ratio(branches, reading(40), (F(100), F(100)))['ambiguous']


def test_constant_reversed_segment_constraints_and_frozen_tie_break():
    assert n.feasible_parameter(((F(4), F(0)), (F(4), F(10))), F(5), F(5), F(1)) == (F(2, 5), F(3, 5))
    assert n.feasible_parameter(((F(10), F(10)), (F(0), F(0))), F(3), F(4), F(1)) == (F(3, 5), F(7, 10))
    assert n.feasible_parameter(((F(4), F(0)), (F(4), F(10))), F(6), F(5), F(1)) is None
    ss = [dict(index=i, endpoints_xz=((F(0), F(0)), (F(10), F(10)))) for i in range(2)]
    c = n.recover(ss, F(4), F(5), F(1))
    assert c['segment']['index'] == 0 and c['t'] == F(9, 20)
    with pytest.raises(ValueError, match='NO_ADMITTED_SOURCE_POINT'):
        n.recover(ss, F(4), F(50), F(1))


def test_sample_exclusion_is_not_complete_grind_order_and_missing_rows_stay_visible():
    ratios = {s: dict(full_support=True, ambiguous=False, bounds_ratio=(F(1), F(3)))
              for s in ['B1', 'B2', 'B3']}
    env = n.envelope(ratios, ['B1', 'B2', 'B3'])
    pair = n.density_ratio_contrast(reading(1), reading(2), reading(1), reading(3), (F(0),)*2)
    pair['id'] = 'synthetic'
    touching = n.density_ratio_contrast(reading(1), reading(2), reading(1), reading(2), (F(0),)*2)
    touching['id'] = 'contact'
    grind = n.grind_comparison(env, env, [pair]+[touching]*8)
    assert grind['sign'] == 0 and grind['marginal_envelope_classification'] == 'OVERLAPPING_OR_CONTACTING'
    assert n.disposition([pair], 990) == 'EXCLUDED_BY_SAMPLE_RATIO_CONTRAST'
    assert n.grind_comparison(env, env, [pair]*9)['sign'] == -1
    assert n.disposition([touching]*990, 990) == 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'
    assert n.disposition([touching]*989, 990) == 'UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'
    partial = n.envelope(ratios, ['B1', 'B2', 'E1'])
    assert partial['missing'] == ['E1'] and partial['descriptive_only']
    assert not n.grind_comparison(partial, env, [pair]*9)['full_support']


@pytest.fixture(scope='module')
def formal():
    return n.analyze()


@pytest.fixture(scope='module')
def source():
    c, p, axes, traces = g.load()
    return n.source_segments(p, traces), axes['force']


def test_exact_replay_accounting_and_protected_predecessor_bytes(formal):
    fixed = n.authenticate()
    assert formal['marginal_replay']['status'] == 'EXACT_MATCH'
    assert formal['marginal_replay']['count'] == 72
    assert [len(formal[t]) for t in n.TABLES] == [72, 180, 990, 60, 90]
    for table in n.TABLES:
        assert len({r['id'] for r in formal[table]}) == len(formal[table])
    assert sum(r['within_grind'] for r in formal[n.TABLES[2]]) == 180
    for path, digest in fixed['preserved_file_hashes'].items():
        assert d.sha256(n.ROOT/path) == digest
    assert formal['input_hashes'] == fixed['inherited_input_hashes']


def test_all_candidate_identities_and_actual_order(formal, source):
    w = formal['affine_witness']
    # Direct mathematical checks, not an assertion of an exposed success flag/number.
    assert len(w['parameters']) == 12 and len(w['certificates']) == 72
    for c in w['certificates']:
        assert c['density_kg_m3'] == w['calibration']['alpha']+w['calibration']['beta']*c['selected_z_pt']
        assert c['density_kg_m3'] == c['b_kg_m3']+c['s_kg_m3']*c['h'] > 0
        assert c['s_kg_m3'] > 0 and abs(c['dx_pt']) <= 1 and abs(c['dz_pt']) <= 1
    assert n.verify_assignment(w, *source)['identities'] == 72


@pytest.mark.parametrize('mutation,reason', [
    ('missing', 'ACCOUNTING'), ('t', 'SEGMENT_MEMBERSHIP'), ('h', 'SHARED_REFERENCE'),
    ('per_force', 'PARAMETER_SUBSTITUTION'), ('displacement', 'SOURCE_OR_DISPLACEMENT'),
    ('hull_gap', 'HULL_GAP'), ('path_order', 'PATH_ORDER')])
def test_producer_rejects_invalid_assignments(formal, source, mutation, reason):
    w, (ss, ax) = deepcopy(formal['affine_witness']), deepcopy(source)
    c = w['certificates'][0]
    if mutation == 'missing':
        w['certificates'].pop()
    elif mutation == 't':
        c['t'] = F(2)
    elif mutation == 'h':
        c['h'] += F(1, 9)
    elif mutation == 'per_force':
        c['a_pt'] += 1
    elif mutation == 'displacement':
        c['dx_pt'] = F(2)
    elif mutation == 'hull_gap':
        r = w['readings'][0]
        z = c['selected_z_pt']
        r['components_z_pt'] = [(z-2, z-1), (z+1, z+2)]  # hull still contains z
    elif mutation == 'path_order':
        # Same exact source points/identities, but a synthetic reversed retained path.
        for s, records in ss.items():
            ss[s] = [dict(r, index=i, endpoints_xz=tuple(reversed(r['endpoints_xz'])))
                     for i, r in enumerate(reversed(records))]
        for c in w['certificates']:
            records = ss[c['trace']]
            index = len(records)-1-c['segment']['index']
            c['segment'] = records[index]
            c['t'] = 1-c['t']
            c['path_position'] = index+c['t']
    with pytest.raises(ValueError, match=reason):
        n.verify_assignment(w, ss, ax)


def reviewer():
    path = n.OUTPUT/'review_check.py'
    spec = importlib.util.spec_from_file_location('normalization_independent_review', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_independent_original_operand_verifier(formal):
    candidate = json.loads(json.dumps(formal['affine_witness'], default=g.serial))
    reviewer().verify_witness(n.ROOT, candidate)


@pytest.mark.parametrize('mutation', ['calibration', 'shared_h', 'parameter', 'source', 't', 'missing'])
def test_independent_checker_rejects_tampered_certificates(formal, mutation):
    candidate = json.loads(json.dumps(formal['affine_witness'], default=g.serial))
    if mutation == 'calibration':
        candidate['calibration']['alpha'] = '0'
    elif mutation == 'shared_h':
        candidate['levels'][1]['h'] = str(F(candidate['levels'][1]['h'])+F(1, 100))
    elif mutation == 'parameter':
        candidate['certificates'][0]['b_kg_m3'] = '1'
    elif mutation == 'source':
        candidate['certificates'][0]['source_x_pt'] = '0'
    elif mutation == 't':
        candidate['certificates'][0]['t'] = '-1'
    else:
        candidate['certificates'].pop()
    with pytest.raises((ValueError, AssertionError)):
        reviewer().verify_witness(n.ROOT, candidate)


def test_offline_reproduction_without_pdf(tmp_path, formal):
    script = """
import socket, sys
socket.socket = lambda *a, **k: (_ for _ in ()).throw(AssertionError('network forbidden'))
sys.modules['fitz'] = sys.modules['pymupdf'] = None
from puckworks.analysis.corrochano2017_density_normalization import main
main()
"""
    subprocess.run([sys.executable, '-c', script, '--output', str(tmp_path)], check=True)
    names = [t+'.csv' for t in n.TABLES]+['affine_'+k+'.csv' for k in
             ('parameters', 'levels', 'intersections', 'readings', 'certificates')]
    names += ['RESULT.json', 'affine_witness.json']
    for name in names:
        assert (tmp_path/name).read_bytes() == (n.OUTPUT/name).read_bytes(), name


@pytest.mark.parametrize('defect,reason', [('support', 'QUERY_EXCEEDS_RECORDED_ENDPOINT'),
    ('amplitude', 'NONPOSITIVE_AMPLITUDE'), ('intersection', 'EMPTY_COMMON_INTERSECTION'),
    ('level_order', 'NONINCREASING_SHARED_LEVELS')])
def test_fixed_construction_negative_outcomes_are_not_affine_exclusions(defect, reason):
    samples = [g0+str(i) for g0 in 'BCDE' for i in range(1, 4)]
    contract = dict(axes=dict(force=dict(values=[0, 300], positions_pt=[0, 300]),
                              density=dict(values=[300, 650], positions_pt=[400, 50])),
                    force_targets_N=[25, 50, 100, 150, 200, 250], trace_guard_pt='1')
    traces, chunks = {}, []
    for sample in samples:
        x = [0, 25, 50, 100, 150, 200, 250, 300]
        z = [F(100+f) for f in x]
        if defect == 'support' and sample == 'B1':
            x, z = x[2:], z[2:]
        if defect == 'amplitude' and sample == 'B1':
            z = [-v for v in z]
        if defect == 'intersection' and sample == 'B1':
            z[4] = F(4000)
        if defect == 'level_order':
            z[2] = F(1000)
        traces[sample] = segments([(f, -v) for f, v in zip(x, z)])
        chunks.append(dict(chunk=sample, vertex_count=len(x)))
    paths = dict(chunks=chunks, joins=[], trace_chunks={s: [s] for s in samples})
    w = n.affine_witness(contract, paths, traces)
    assert w['disposition'] == n.NO_CERTIFICATE and reason in w['failure']['reason']
    assert w['failure']['row'] and not w['failure']['arithmetic_failure']


def test_construction_arithmetic_failure_remains_visible(monkeypatch):
    contract, paths, _, traces = g.load()
    def failed(*args):
        raise ArithmeticError('analytical arithmetic failure')
    monkeypatch.setattr(d, 'read_coordinates', failed)
    w = n.affine_witness(contract, paths, traces)
    assert w['disposition'] == n.NO_CERTIFICATE
    assert w['failure']['arithmetic_failure'] and 'ArithmeticError' in w['failure']['reason']


def test_invalid_component_reference_rejected_explicitly(formal, source):
    w = deepcopy(formal['affine_witness'])
    w['certificates'][0]['component_index'] = 1000
    with pytest.raises(ValueError, match='COMPONENT_REFERENCE'):
        n.verify_assignment(w, *source)

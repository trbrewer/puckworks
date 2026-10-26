"""Bounded scientific contract tests, independent primal/dual and LP checks."""
import copy
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, localcontext
from fractions import Fraction as Q
import json

import pytest

from puckworks.analysis import matias2023_caffeine_aggregation as analysis
from puckworks.analysis.matias2023_aggregation_check import check_exact, check_source, numerical_lp


def solve(x, bands):
    result = analysis.exact_minimax(x, bands)
    check_exact(x, bands, result)
    return result


@pytest.mark.parametrize('logs', [(2, 2, 2, 2), (2, 1, 0, -1), (0,), (1, 0), (-3, -4)])
def test_constant_geometric_and_small_support(logs):
    fit = solve(range(len(logs)), [(v, v) for v in logs])
    assert Q(fit['epsilon']) == 0


def enclosing_log(value):
    """Correctly rounded Decimal log10 with neighboring values encloses exact Q.

    Directed division encloses the rational concentration before monotone log10.
    No rounded log is asserted to equal an exact positive-mixture log.
    """
    with localcontext() as ctx:
        ctx.prec = 70
        ctx.rounding = ROUND_FLOOR
        low = Decimal(value.numerator)/Decimal(value.denominator)
        ctx.rounding = ROUND_CEILING
        high = Decimal(value.numerator)/Decimal(value.denominator)
        return Q(low.log10().next_minus()), Q(high.log10().next_plus())


@pytest.mark.parametrize('components', [[(100, Q(1, 10)), (30, Q(1, 2))],
                                        [(1, Q(1)), (20, Q(1, 3)), (9, Q(1, 5)), (50, Q(4, 5))]])
def test_genuine_positive_mixture_enclosing_logs(components):
    values = [sum(a*q**i for a, q in components) for i in range(10)]
    assert all(a*c >= b*b for a, b, c in zip(values, values[1:], values[2:]))
    assert all(a >= b for a, b in zip(values, values[1:]))
    bands = [enclosing_log(v) for v in values]
    assert Q(solve(range(10), bands)['epsilon']) == 0


def test_positive_log_concave_excursion():
    fit = solve([0, 1, 2], [(0, 0), (0, 0), (-2, -2)])
    assert Q(fit['epsilon']) == Q(1, 2)


def test_local_nonexclusion_is_not_global_feasibility():
    bands = [(0, 0), (Q(-1, 2), Q(-1, 2)), (-3, 0), (-3, -3)]
    assert [bands[i][1]-2*bands[i+1][0]+bands[i+2][1] for i in (0, 1)] == [1, Q(5, 2)]
    fit = solve(range(4), bands)
    assert Q(fit['epsilon']) == Q(1, 4)
    assert list(map(Q, fit['predicted_log'])) == [Q(1, 4), Q(-3, 4), Q(-7, 4), Q(-11, 4)]
    c, = fit['certificates']
    assert (c['index'], c['a'], c['b'], c['alpha'], c['beta']) == (1, 0, 3, '2/3', '1/3')


def test_necessary_shape_compatibility_is_not_mixture_witness():
    logs = [2, 1, 0, 0]
    assert Q(solve(range(4), [(v, v) for v in logs])['epsilon']) == 0
    concentrations = [100, 10, 1, 1]
    assert concentrations[0]*concentrations[2]-concentrations[1]**2 == 0
    # Positive summands a_r*a_s*(q_r-q_s)^2 force all q to agree.
    q = Q(concentrations[1], concentrations[0])
    assert concentrations[0]*q**3 == Q(1, 10) != concentrations[3]


def test_shift_and_widening():
    x, bands = [0, 2, 3, 8], [(2, 2), (1, 1), (-1, 0), (-3, -3)]
    fit = solve(x, bands)
    shift = Q(23, 7)
    shifted = solve(x, [(l+shift, u+shift) for l, u in bands])
    assert fit['epsilon'] == shifted['epsilon']
    assert analysis.multiplicative_enclosure(fit['epsilon']) == analysis.multiplicative_enclosure(shifted['epsilon'])
    widened = solve(x, [(l-Q(1, 10), u+Q(1, 10)) for l, u in bands])
    assert Q(widened['epsilon']) <= Q(fit['epsilon'])


@pytest.mark.parametrize('x,bands', [
    ([0, 1], [(0, 0), (2, 2)]),
    ([0, 1, 3, 7], [(0, 0), (1, 1), (-1, 2), (-3, -3)]),
    ([0, 2, 5, 9], [(0, 0), (-1, 2), (-2, 3), (-3, 4)]),
    ([0, 1, 2, 3], [(0, 0), (-1, -1), (-2, -2), (-3, -3)]),
    ([0, 1, 2, 3], [(0, 0), (1, 1), (1, 1), (0, 0)]),
])
def test_prefix_nonuniform_collinear_ties_and_lp(x, bands):
    fit = solve(x, bands)
    assert numerical_lp(x, bands) == pytest.approx(float(Q(fit['epsilon'])), abs=1e-10)


def test_repeated_prefix_sources_anchor_controls_and_tie_rule():
    fit = solve([0, 1, 2, 3], [(0, 0), (1, 1), (1, 1), (0, 0)])
    assert [r['prefix_source'] for r in fit['provenance']] == [0, 0, 0, 0]
    assert fit['hull_anchors'] == [0, 3]
    assert [c['index'] for c in fit['certificates']] == [1, 2]
    assert all(c['p_a'] == c['p_b'] == 0 for c in fit['certificates'])
    anchor = solve([0, 3], [(0, 0), (2, 2)])['certificates'][0]
    assert anchor['a'] == anchor['b'] == 1 and anchor['alpha'] == '1' and anchor['beta'] == '0'


def test_no_support_has_no_verdict():
    fit = solve([], [])
    assert fit['epsilon'] is None and fit['support_status'] == 'SOURCE_SUPPORT_FAILURE'


@pytest.mark.parametrize('x,bands', [([0, 0], [(0, 1)]*2), ([1, 0], [(0, 1)]*2),
                                      ([0], [(2, 1)]), ([0], [('nan', 1)]),
                                      ([0], [(0, 'inf')]), (['inf'], [(0, 1)]),
                                      ([0], []), ([0.1], [(0, 1)])])
def test_invalid_source_numbers_and_coordinates_rejected(x, bands):
    with pytest.raises(ValueError):
        analysis.exact_minimax(x, bands)


@pytest.mark.parametrize('mutation', ['primal', 'weight', 'coordinate', 'source', 'bound', 'omit_tie'])
def test_independent_checker_rejects_corrupt_certificate_or_witness(mutation):
    x, bands = [0, 1, 2, 3], [(0, 0), (1, 1), (1, 1), (0, 0)]
    fit = solve(x, bands)
    if mutation == 'primal':
        fit['predicted_log'][1] = '3'
    elif mutation == 'omit_tie':
        fit['certificates'].pop()
    else:
        key, value = {'weight': ('alpha', '1/2'), 'coordinate': ('x_a', '-1'),
                      'source': ('p_a', 1), 'bound': ('bound', '0')}[mutation]
        fit['certificates'][0][key] = value
    with pytest.raises(ValueError, match='CHECK_FAILURE'):
        check_exact(x, bands, fit)


def test_source_all_ten_certificates_and_local_global(tmp_path):
    report = analysis.write_report(tmp_path)
    receipt = check_source(tmp_path/'results.json', lp=True)
    expected = {'N': Q(9949, 331638), 'G': Q(474287960807, 16082359097354),
                'P_outer': Q(2571083096567, 168864770522217),
                'P_inner': Q(2742769138607, 168864770522217)}
    for layer, e in expected.items():
        fit = report['layers'][layer]
        assert Q(fit['epsilon']) == e > 0 and fit['support_status'] == 'COMPLETE'
        assert len(fit['predicted_log']) == 10
        c, = fit['certificates']
        assert (c['index'], c['a'], c['b'], c['alpha'], c['beta']) == (1, 0, 3, '2/3', '1/3')
        assert receipt['layers'][layer]['status'] == 'PASS'
    assert [receipt['layers'][k]['local_exclusion_count'] for k in expected] == [5, 5, 0, 1]
    assert len(report['support']) == len(report['witness_residuals']) == 40
    assert len(report['local_curvatures']) == 32
    # G/P center residuals are not the interval objective.
    assert max(abs(Q(w['center_residual_log'])) for w in report['witness_residuals'] if w['layer'] == 'P_outer') > expected['P_outer']
    replay = tmp_path/'replay'
    analysis.write_report(replay)
    assert (tmp_path/'results.json').read_bytes() == (replay/'results.json').read_bytes()


def test_P_endpoint_quantifiers():
    rows = analysis.read_observations()
    report = analysis.build_report(rows)
    outer, inner = (Q(report['layers'][k]['epsilon']) for k in ('P_outer', 'P_inner'))
    # Arbitrary interior endpoint realizations; inclusion proves the universal result.
    for t in (Q(0), Q(1, 3), Q(1)):
        bands = [(Q(r['L_minus'])+t*(Q(r['L_plus'])-Q(r['L_minus'])),
                  Q(r['U_minus'])+(1-t)*(Q(r['U_plus'])-Q(r['U_minus']))) for r in rows]
        cost = Q(solve(range(10), bands)['epsilon'])
        assert outer <= cost <= inner
    assert report['layers']['P_inner']['mixture_discrepancy_lower_bound']['endpoint_quantifier'] == 'INNER_BANDS_ONLY_NOT_UNIVERSAL_EXCLUSION'
    # Inner positivity alone can coexist with an outer relaxed zero.
    assert Q(solve(range(3), [(-2, 2)]*3)['epsilon']) == 0
    assert Q(solve(range(3), [(0, 0), (0, 0), (-2, -2)])['epsilon']) > 0


def test_gapped_support_preserves_slots_and_secants():
    rows = analysis.read_observations()
    rows[2]['center_status'] = 'UNSUPPORTED'
    rows[6]['L_status'] = 'UNSUPPORTED'
    report = analysis.build_report(rows)
    for layer, missing in [('N', 2), ('G', 2), ('P_outer', 6), ('P_inner', 6)]:
        fit = report['layers'][layer]
        assert fit['support_status'] == 'SUBSET_LOWER_BOUND_ONLY' and fit['supported_count'] == 9
        assert list(map(Q, fit['x'])) == [i for i in range(10) if i != missing]
        bands, _, _, _ = analysis.layer_intervals(rows, layer)
        check_exact(fit['x'], [b for b in bands if b is not None], fit)
        witness = [w for w in report['witness_residuals'] if w['layer'] == layer]
        assert len(witness) == 10 and witness[missing]['predicted_log'] is None
        assert sum(d['support_status'] == 'UNSUPPORTED' for d in report['local_curvatures'] if d['layer'] == layer) == 3


def test_empty_inner_invalid_inputs_and_absent_support_are_distinct():
    rows = analysis.read_observations()
    empty = copy.deepcopy(rows)
    empty[0]['L_plus'] = empty[0]['U_plus']
    report = analysis.build_report(empty)
    assert report['layers']['P_inner']['support_status'] == 'INNER_UNAVAILABLE'
    assert report['layers']['P_inner']['epsilon'] is None
    invalid = copy.deepcopy(rows)
    invalid[0]['z'] = 'nan'
    report = analysis.build_report(invalid)
    assert report['layers']['N']['support_status'] == 'SOURCE_INPUT_INVALID'
    assert report['layers']['P_outer']['support_status'] == 'COMPLETE'
    invalid = copy.deepcopy(rows)
    invalid[0]['L_minus'] = 'nan'
    report = analysis.build_report(invalid)
    assert report['layers']['P_outer']['support_status'] == 'SOURCE_INPUT_INVALID'
    assert report['layers']['P_inner']['support_status'] == 'SOURCE_INPUT_INVALID'
    for row in rows:
        row['center_status'] = row['L_status'] = row['U_status'] = 'UNSUPPORTED'
    report = analysis.build_report(rows)
    assert all(v['support_status'] == 'SOURCE_SUPPORT_FAILURE' and v['epsilon'] is None for v in report['layers'].values())
    assert len(report['witness_residuals']) == 40
    rows[2]['x'] = '1'
    with pytest.raises(ValueError):
        analysis.build_report(rows)


def test_zero_subset_never_claims_full_cohort_compatibility():
    rows = analysis.read_observations()
    for row in rows[1:]:
        row['center_status'] = 'UNSUPPORTED'
    report = analysis.build_report(rows)
    assert report['layers']['N']['disposition'] == 'FULL_COHORT_COMPATIBILITY_NOT_ESTABLISHED'


def test_outward_transform_exact_cube_fixture():
    m = analysis.multiplicative_enclosure(Q(1, 3))
    assert Q(m['M_lower'])**3 <= 10 <= Q(m['M_upper'])**3
    assert Q(m['ratio_lower_lower'])**3 <= Q(1, 10) <= Q(m['ratio_lower_upper'])**3


def test_serialized_source_hash_tamper_rejected(tmp_path):
    analysis.write_report(tmp_path)
    path = tmp_path/'results.json'
    report = json.loads(path.read_text())
    report['input_sha256']['observations.csv'] = '0'*64
    path.write_text(json.dumps(report))
    with pytest.raises(ValueError, match='source identity'):
        check_source(path)

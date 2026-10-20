"""Synthetic verification only: no scientific archive reads in quick CI."""
from types import SimpleNamespace
from decimal import Decimal, localcontext

import numpy as np
import pytest

from puckworks.analysis import grudeva2026_baseline_observation_005 as native_p
from puckworks.analysis import grudeva2026_bed_accuracy_004 as native_c
from puckworks.analysis import grudeva2026_publication_reading_bounds_011 as task
from puckworks.analysis.grudeva2026_publication_reading_bounds_011 import decision, residual, witnesses
from puckworks.analysis.grudeva2026_reading_bounds_011_range import (
    Interval as I, Function, Piece, enclose, range_pieces, paired_pieces,
)
from puckworks.analysis.grudeva2026_reading_bounds_011_adapters import (
    quadratic, root_reconstruction, spatial_pieces, Production, Comparator,
)


@pytest.mark.parametrize('co,expected', [([.2], [.2, .2]), ([.2, .3], [.2, .5]),
                                        ([0, 1, -1], [0, .25]), ([1, -2, 1], [0, 1])])
def test_known_ranges(co, expected):
    r = enclose(Function(co), 0., 1.)
    assert r['bounds'][0] <= expected[0]+1e-16
    assert r['bounds'][1] >= expected[1]-1e-16
    assert np.max(np.abs(np.array(r['bounds'])-expected)) < 1e-11


@pytest.mark.parametrize('root', [1e-8, .123456789, 1-1e-8])
def test_stationary_points_including_near_boundary(root):
    f = Function([-I(root)*root, 2*I(root), -1])
    r = enclose(f, 0., 1.)
    assert r['bounds'][1] >= 0
    assert r['bounds'][1] <= 1e-11
    assert r['bounds'][0] <= -max(root*root, (1-root)**2)+1e-16


def test_square_root_stationary_and_singular_endpoint():
    # x+sqrt(1-x): maximum 1.25 at .75, minimum 1 at both ends.
    result = enclose(Function([0, 1], ((1, 1),)), 0., 1.)
    assert result['bounds'][0] <= 1
    assert 1.25 <= result['bounds'][1] <= 1.25+1e-11


def test_outward_arithmetic_and_decimal_conversion():
    third = I(1)/3
    assert third.lo*3 <= 1 <= third.hi*3
    root = I(2).sqrt()
    assert (root*root).lo <= 2 <= (root*root).hi
    assert I(*third.floats()).lo <= third.lo <= third.hi <= I(*third.floats()).hi


def test_production_cell_average_quadratic_and_stencil_limits():
    f = np.array([0., .13, .41, .65, .89, 1.])
    primitive = lambda z: .2*z+.15*z*z+z**3/3
    values = np.diff(primitive(f))/np.diff(f)
    for cell in range(len(values)):
        first = min(max(cell-1, 0), len(values)-3)
        function = quadratic(f, values, first, .8)
        z = (f[cell]+f[cell+1])*.4
        point = function.value(I(z)).floats()
        expected = .2+.3*(z/.8)+(z/.8)**2
        assert abs(np.mean(point)-expected) < 1e-14
    arbitrary = np.array([.1, .2, .8, .25, .1])
    pieces = spatial_pieces(f, arbitrary, 1., 1., .4, .42, 'production')
    left = pieces[0].function.value(I(.41)).floats()
    right = pieces[1].function.value(I(.41)).floats()
    assert abs(np.mean(left)-np.mean(right)) > .01
    result = range_pieces(pieces, .4, .42)['bounds']
    assert result[0] <= min(left[0], right[0])
    assert result[1] >= max(left[1], right[1])
    assert abs(native_p.cell_reconstruction(f, arbitrary, [.41])[0]-np.mean(right)) < 1e-14


@pytest.mark.parametrize('values', [[.2], [.1, .3], [.1, .2, .7, .1]])
def test_comparator_native_special_cases_and_one_sided_stencils(values):
    faces = np.linspace(0., .9, len(values)+1)
    for cell in range(len(values)):
        function = root_reconstruction(faces, values, cell)
        for x in [float((faces[cell]+faces[cell+1])/2), float(np.nextafter(faces[cell+1], faces[cell]))]:
            result = function.value(I(x)).floats()
            assert abs(native_c.point_liquid(x, faces, np.array(values))-np.mean(result)) < 2e-13
    if len(values) > 2:
        x = faces[2]
        left = root_reconstruction(faces, values, 1).value(I(float(x))).floats()
        right = root_reconstruction(faces, values, 2).value(I(float(x))).floats()
        assert abs(np.mean(left)-np.mean(right)) > .01


def fake_production():
    # A BDF linear polynomial valid only to 2.5, underlying step extends to 3.
    meta = {'dense_side': 'right'}
    s = SimpleNamespace(breaks=np.array([0., 1., 2., 2.5]), orders=np.array([1, 1, 1]),
                        shifts=np.array([[0.], [1.], [2.]]), denominators=np.ones((3, 1)),
                        step_bounds=np.array([[0., 1.], [1., 2.], [2., 3.]]), meta=meta,
                        data={f'D_{k}': np.array([[1., .1, .2, .4], [0., .1, .1, .1]]) for k in range(3)})
    return Production(SimpleNamespace(n=3, faces=np.linspace(0, 1, 4), arrival=2.,
                                      horizon=2.5, segments=[s]))


def test_bdf_valid_support_and_physical_event_sides():
    adapter = fake_production()
    with pytest.raises(ValueError, match='valid temporal support'):
        adapter.temporal(2.4, 2.6)
    p = adapter.temporal(.9, 2.5)
    result = range_pieces(p, .9, 2.1)
    assert result['bounds'][0] <= 0 and result['bounds'][1] >= 1
    # Unit plateau and native outlet's right limit remain separate at exit.
    pre = [x for x in result['pieces'] if x['high'] == 2.][0]
    post = [x for x in result['pieces'] if x['low'] == 2.][0]
    assert pre['bounds'] == [1., 1.]
    assert post['bounds'][1] < .6


def comparator_run():
    # front_trace=.2 while physical outlet is zero or one before exit.
    t = [1., 1.5, 2., 2.5, 8.]
    trace = [.2, .2, .2, .4, .1]
    cup = [0., .5, 1., 1.15, 2.525]
    return dict(observations=[{'t': 0.}], accepted_columns=['front_trace', 'cup', 't'],
                accepted=list(map(list, zip(trace, cup, t))), arrival=2., events=[
                    dict(kind='first_drip', t=1., outlet_left=0., outlet_right=1.),
                    dict(kind='desaturation_exit', t=2., outlet_left=1., outlet_right=.2)])


def test_comparator_schema_outlet_knots_events_cup():
    adapter = Comparator(comparator_run())
    assert adapter.native('figure4_concentration', {}, .9) == 0
    assert adapter.native('figure4_concentration', {}, 1.) == 1
    assert adapter.native('figure4_concentration', {}, 1.8) == 1
    assert adapter.native('figure4_concentration', {}, 2.) == .2
    assert adapter.native('figure4_concentration', {}, 2.5) == .4
    assert adapter.cup_consistency < 1e-14
    pieces = adapter.pieces('figure4_concentration', {}, 1.9, 2.1)
    ranges = range_pieces(pieces, 1.9, 2.1)['pieces']
    assert ranges[0]['bounds'] == [1., 1.]
    assert ranges[-1]['bounds'][1] < .25


def test_full_coverage_fails_closed():
    pieces = [Piece(0, .4, Function([0])), Piece(.5, 1, Function([1]))]
    with pytest.raises(ValueError, match='full-interval'):
        range_pieces(pieces, .2, .8)
    with pytest.raises(ValueError, match='full-interval'):
        range_pieces(pieces, -.1, .2)


def test_paired_common_coordinate_cancellation():
    a = [Piece(0, 1, Function([2, 10]))]
    b = [Piece(0, .3, Function([1, 10])), Piece(.3, 1, Function([1, 10]))]
    result = range_pieces(paired_pieces(a, b, 0, 1), 0, 1)
    assert result['bounds'] == [1., 1.]
    # Independently optimized difference would be [-9,11], which is forbidden.
    assert sum(p['low'] < p['high'] for p in result['pieces']) == 2


def test_paired_native_point_override_in_only_one_arm():
    a = [Piece(0, 1, Function([0])), Piece(.5, .5, Function([3]))]
    b = [Piece(0, 1, Function([1]))]
    assert range_pieces(paired_pieces(a, b, 0, 1), 0, 1)['bounds'] == [-1., 2.]


def test_paired_opposite_boundary_ownership():
    a = [Piece(0, .5, Function([0]), low_native=False, high_native=True),
         Piece(.5, 1, Function([2]), low_native=False, high_native=True)]
    b = [Piece(0, .5, Function([0])), Piece(.5, 1, Function([2]))]
    # Same-side differences vanish; actual shared-coordinate difference is -2.
    assert range_pieces(paired_pieces(a, b, 0, 1), 0, 1)['bounds'] == [-2., 0.]


def test_physical_spatial_cut_preserves_exact_product():
    faces = np.array([0., .2, .4, .6, 1.])
    pieces = spatial_pieces(faces, [.1, .2, .4, .6], .7, 1., .1, .5, 'production')
    with localcontext() as ctx:
        ctx.prec = 2200
        cut = Decimal.from_float(.4)*Decimal.from_float(.7)
    assert cut != Decimal.from_float(.4*.7)
    assert pieces[1].high == cut == pieces[2].low


def test_comparator_temporal_failure_does_not_disable_spatial():
    run = comparator_run()
    run['accepted_columns'] = ['wrong']
    run['observations'] = [dict(t=.5, faces=[0., .1, .3], liquid_cells=[.1, .2])]
    adapter = Comparator(run)
    assert np.isfinite(adapter.native('figure3_concentration', {'t': .5}, .15))
    with pytest.raises(ValueError, match='schema'):
        adapter.native('figure4_concentration', {}, 2.1)
    assert np.isfinite(adapter.native('figure3_concentration', {'t': .5}, .15))


def test_nominal_readout_exception_isolated_by_family(monkeypatch):
    rows = [dict(family=f, horizontal_axis='x', original=dict(family=f,
             classification='INCLUDED', model=.2, coordinates={'x': .1}))
            for f in ['bad', 'good']]
    monkeypatch.setattr(task.historical, 'observe', lambda run, row: (.2, None, None, None))
    class Adapter:
        def native(self, family, coord, x):
            if family == 'bad':
                raise ValueError('synthetic operation failure')
            return .2
        def pieces(self, family, coord, low, high):
            return [Piece(0, 1, Function([.2]))]
    failures = task.check_nominals(rows, {}, Adapter())
    assert list(failures) == ['bad']
    assert not rows[0]['nominal_adapter']['passed']
    assert rows[1]['nominal_adapter']['passed']


def test_direct_root_difference_preserves_shared_dependence():
    f = Function([0, 1], ((1, 2),))
    g = Function([1, 1], ((1, 2),))
    assert enclose(f-g, 0., 1.)['bounds'] == [-1., -1.]


def test_bdf_degree_four_range_has_interior_extrema():
    adapter = fake_production()
    segment = adapter.trajectory.segments[0]
    segment.breaks = np.array([2., 2.5])
    segment.orders = np.array([4])
    segment.shifts = np.array([[2., 2., 2., 2.]])
    segment.denominators = np.ones((1, 4))
    # Trace is .4+u-6u^2+8u^3; critical points are (3+-sqrt(3))/12.
    segment.data = {'D_0': np.array([[0., .4, .4, .4], [0., 1., 1., 1.],
                                   [0., -6., -6., -6.], [0., 8., 8., 8.], [0., 0., 0., 0.]])}
    r = range_pieces(adapter.temporal(2., 2.5), 2., 2.5)['bounds']
    critical = [(3-np.sqrt(3))/12, (3+np.sqrt(3))/12]
    expected = [.4+u-6*u*u+8*u**3 for u in [0., .5]+critical]
    assert r[0] <= min(expected)+1e-15 and r[1] >= max(expected)-1e-15
    assert max(abs(r[0]-min(expected)), abs(r[1]-max(expected))) < 1e-11


def test_hull_overlap_is_not_attainable_crossing_or_threshold_sensitivity():
    pieces = [Piece(0, .5, Function([-2])), Piece(.5, 1, Function([2]))]
    r = range_pieces(pieces, 0, 1)
    assert decision(r['bounds'], 1)['zero_exclusion'] == 'UNRESOLVED'
    row = dict(original=dict(publication=0., family='figure3_front', limit=1., coordinates={},
                             extraction_bounds={'z_uncertainty': 0.}),
               horizontal_axis=None, publication_interval=[0., 0.])
    w = witnesses(row, [0., 1.], lambda x: -2 if x < .5 else 2)
    assert not w['demonstrated_threshold_sensitivity']


def test_signed_separation_distinct_from_historical_threshold_and_inclusive_equality():
    assert decision([.01, .02], .015) == dict(signed=[.01, .02], absolute=[.01, .02],
        zero_exclusion='POSITIVE', threshold='UNRESOLVED', extrema_attainability='NOT_INFERRED_FROM_ENCLOSURE')
    assert decision([-.015, .015], .015)['threshold'] == 'WITHIN_THROUGHOUT'
    assert decision([.015, .02], .015)['threshold'] == 'UNRESOLVED'
    assert decision([.016, .02], .015)['threshold'] == 'EXCEEDED_THROUGHOUT'
    assert residual([.1, .2], .15, .01, .015)['zero_exclusion'] == 'UNRESOLVED'

"""Scientific reading/observer regressions and adversarial finite examples."""
import csv
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys

import pytest

from puckworks.analysis import corrochano2017_pressure_flow as c
from puckworks.analysis.melrose2019bed_transient import affine_enclosure, compatibility
from puckworks.data import rc17_fig6_23_pressure_flow


def test_frozen_plan_and_native_calibration():
    contract, rows = c.recover()
    assert hashlib.sha256((c.ROOT / contract['plan']['path']).read_bytes()).hexdigest() == contract['plan']['sha256']
    cal = contract['calibration']
    for x, t in zip(cal['internal_tick_centres_px']['x'], cal['internal_tick_centres_px']['time_s']):
        lo, hi = affine_enclosure([F(x - 1), F(x + 1)], cal['x_anchors_px'], [F(0), F(70)])
        assert lo <= t <= hi
    for panel in ('flow', 'pressure'):
        ticks = cal['internal_tick_centres_px']['flow_m3_s' if panel == 'flow' else 'pressure_Pa']
        for y, value in zip(cal['internal_tick_centres_px']['y'], ticks):
            lo, hi = affine_enclosure([F(y - 1), F(y + 1)], cal['y_anchors_px'], list(map(F, cal['y_values'][panel])))
            assert lo <= F(value) <= hi
    for row in rows:
        assert row['time_lower_s'] <= row['nominal_time_s'] <= row['time_upper_s']
        assert row['central'] is None
    assert {i['width'] for i in contract['source']['panels']} == {512}
    assert {i['height'] for i in contract['source']['panels']} == {384}


def test_bands_enclose_inverse_calibration_and_do_not_extend_endpoint():
    contract, rows = c.recover()
    cal = contract['calibration']
    for r in rows:
        for a, b in itertools.product(*cal['x_anchors_px']):
            x = F(a) + F(r['nominal_time_s'], 70) * (b - a)
            assert F(r['x_min_px']) <= x - 2
            assert F(r['x_max_px']) >= x + 2
        if r['nominal_time_s'] == 60:
            assert r['status'] == 'UNSUPPORTED_ENDPOINT'
            assert r['lower'] is r['upper'] is None
            assert int(r['x_max_px']) > max(cal['trace_endpoint_x_px'])


def test_si_ratio_rectangles_and_nonpositive_denominators():
    assert c.ratio_bounds(('0.000002', '0.000004'), (200000, 400000)) == {
        'status': 'BOUNDED_INDICATION', 'lower': F(1, 200000000000), 'upper': F(1, 50000000000)}
    for p in [(0, 1), (-1, 1), (-2, -1)]:
        r = c.ratio_bounds((0, 1), p)
        assert r['status'] == 'NONPOSITIVE_DENOMINATOR' and r['upper'] is None
    assert c.ratio_bounds(None, (1, 2))['status'] == 'UNSUPPORTED'
    assert c.ratio_bounds((0, 2), (1, 2))['lower'] == 0
    with pytest.raises(ValueError):
        c.ratio_bounds((-1, 2), (1, 2))


def test_calibration_curve_discrepancy_and_actual_observation_support():
    contract, readings = c.recover()
    a = contract['apparatus_calibration']
    aa, b, d = map(F, a['caption_polynomial_SI'])
    q = F(a['check_Q_m3_s'])
    assert aa * q**2 + b * q + d == 25200
    assert a['displayed_curve_reading_Pa'][1] < 25200
    assert c.calibration_support((F('0.000001'), F('0.000002')), a) == 'BELOW'
    assert c.calibration_support((F('0.000004'), F('0.000015')), a) == 'WITHIN'
    assert c.calibration_support((F('0.000018'), F('0.000019')), a) == 'ABOVE'
    assert c.calibration_support((F('0.000002'), F('0.000004')), a) == 'AMBIGUOUS'
    assert next(r for r in readings if r['reading_id'] == 'hot_flow_20')['calibration_support'] == 'BELOW'
    assert not a['correction_reapplied']


def test_floor_missingness_and_loader_do_not_make_physical_zeros():
    rows = rc17_fig6_23_pressure_flow()
    assert len(rows) == 55
    r = next(x for x in rows if x['reading_id'] == 'hot_flow_40')
    assert r['lower'] == 0 and r['upper'] > 0
    assert r['censoring'] == 'FLOOR_INDICATION'
    assert r['physical_flow_eligibility'] == 'NOT_ESTABLISHED'
    r = next(x for x in rows if x['reading_id'] == 'hot_flow_60')
    assert r['lower'] is None and r['central'] is None
    r = c.contrast_bounds((1, 2), (0, 1))
    assert r['ratio'] == [1, None] and r['difference'] == [0, 2]
    assert c.contrast_bounds((1, 2), (0, 0))['ratio'] == [None, None]
    assert c.contrast_bounds(None, (1, 2))['status'] == 'UNSUPPORTED'


def _points(intervals):
    return [dict(point_id=str(i), lower=F(a), upper=F(b), nominal_time_s=10 * i,
                 time_lower_s=F(10 * i), time_upper_s=F(10 * i + 1),
                 complete_envelope=True) for i, (a, b) in enumerate(intervals)]


def test_complete_coverage_cannot_silently_use_a_subset():
    _, rows = c.recover()
    q = next(r for r in rows if r['reading_id'] == 'cold_flow_10')
    p = next(r for r in rows if r['reading_id'] == 'cold_pressure_10')
    assert c.complete_envelope(q, p)
    assert not c.complete_envelope(q, dict(p, coverage='INCOMPLETE'))
    # Dropping the high late trace would manufacture an all-runs decline.
    subset = _points([(10, 10), (1, 1)])
    subset[1]['complete_envelope'] = False
    assert c.temporal_result(subset)['nondecreasing'] is False
    assert c.temporal_result(subset, universal=True)['nondecreasing'] is True
    full = _points([(1, 10), (1, 20)])
    assert c.temporal_result(full, universal=True)['nondecreasing'] is True


def test_transitive_contradiction_touching_and_same_middle():
    edges = [('0', '1'), ('1', '2')]
    result = compatibility(_points([(2, 3), (0, 3), (0, 1)]), edges)
    assert result['decline_witness']['earlier'] == '0'
    assert result['decline_witness']['later'] == '2'
    assert compatibility(_points([(1, 2), (0, 1)]), [('0', '1')])['nondecreasing']
    exact = compatibility(_points([(F(1, 3), F(1, 3)), (F(1, 3), F(1, 3))]), [('0', '1')])
    assert exact['D_up'] == 0
    # One track declines, another recovers; neither has a same-trough witness.
    decline = c.temporal_result(_points([(3, 3), (1, 1), (0, 0)]))
    recovery = c.temporal_result(_points([(0, 0), (1, 1), (3, 3)]))
    assert decline['decline_witness'] and recovery['increase_witness']
    assert not decline['same_trough']['resolved'] and not recovery['same_trough']['resolved']
    good = c.temporal_result(_points([(3, 4), (1, 2), (3, 4)]))
    assert good['same_trough']['resolved'][0]['trough'] == '1'
    # Pairwise possible changes at different middles cannot be fused.
    impossible = c.temporal_result(_points([(0, 0), (1, 2), (3, 3)]))
    assert not impossible['same_trough']['rectangular_possible_triples']


def _fixed_matchings(qs, ps, identity_qualified=True):
    """Test-only independent exhaustive oracle; never enumerate ambiguous identities."""
    if not identity_qualified:
        return None
    out = []
    for perm in itertools.permutations(range(len(ps))):
        runs = []
        for i, j in enumerate(perm):
            values = [F(q) / F(p) for q, p in zip(qs[i], ps[j])]
            runs.append(compatibility(_points([(x, x) for x in values]), [('0', '1')]))
        out.append(runs)
    return out


def test_fixed_pairing_partner_switching_and_quantifiers():
    # Fixed P partners both decline for Q1: 10/1 > 9/2 and 10/10 > 9/11.
    # Switching from high P to low P invents recovery: 10/10 < 9/2.
    qs, ps = [[10, 9], [1, 3]], [[1, 2], [10, 11]]
    results = _fixed_matchings(qs, ps)
    assert all(not matching[0]['nondecreasing'] for matching in results)
    assert F(10, 10) < F(9, 2)
    assert all(any(not run['nondecreasing'] for run in matching) for matching in results)
    assert not all(all(not run['nondecreasing'] for run in matching) for matching in results)
    assert _fixed_matchings(qs, ps, identity_qualified=False) is None
    assert len(_fixed_matchings(qs + [[2, 4]], ps + [[3, 4]])) == 6
    # Union envelopes cannot be used to count individual monotone runs.
    envelope = _points([(F(1, 10), 10), (F(3, 11), F(9, 2))])
    assert c.temporal_result(envelope, universal=True)['nondecreasing']


def test_explicit_alpha_dependent_identity():
    g = [F(2), F(4)]
    assert c.required_viscosity_ratio(g)['bounds'] is None
    assert c.required_viscosity_ratio(g, (1, 1))['bounds'] == [2, 4]
    assert c.required_viscosity_ratio(g, (2, 3))['bounds'] == [4, 12]
    assert c.required_viscosity_ratio([F(2), None], (1, 1))['bounds'] == [2, None]
    # Direct Darcy construction with unequal volume mappings.
    ac, ah, muc, muh, geometry = F(2), F(6), F(5), F(7), F(3)
    gc, gh = ac * geometry / muc, ah * geometry / muh
    assert muh / muc == (ah / ac) * (gc / gh)
    assert muh / muc != gc / gh


def _independent_bounds(row, values):
    # Separate affine expression anchored at the bottom; no producer helper call.
    vals = []
    for y, top, bottom in itertools.product(
            [F(row['y_min_px']) - 2, F(row['y_max_px']) + 2], [28, 30], [341, 343]):
        vals.append((F(bottom) - y) / (bottom - top) * F(values[0]))
    return max(F(0), min(vals)), max(vals)


def test_load_bearing_witness_arithmetic_independent_of_producer_transform():
    with (c.DATA / 'source_coordinates.csv').open() as f:
        rows = {r['reading_id']: r for r in csv.DictReader(x for x in f if not x.startswith('#'))}
    def g(qid, pid):
        ql, qu = _independent_bounds(rows[qid], ['0.000035', '0'])
        pl, pu = _independent_bounds(rows[pid], ['350000', '0'])
        return ql / pu, qu / pl
    a, b = g('cold_flow_10', 'cold_pressure_10'), g('cold_flow_50', 'cold_pressure_50')
    assert a[0] - b[1] == F(611, 152150000000000)
    a, b = g('cold_flow_05', 'cold_pressure_05'), g('cold_flow_55', 'cold_pressure_55')
    assert a[0] - b[1] == F(2891, 82350000000000)
    a, b = g('hot_flow_late_upper_25', 'hot_pressure_25'), g('hot_flow_late_upper_55', 'hot_pressure_55')
    assert b[0] - a[1] == F(1, 3825000000000)


def test_result_quantifiers_and_separate_grids():
    r = c.analyze()
    assert r['counts']['requested_condition_panel_slots'] == 48
    assert r['counts']['recovered_condition_panel_slots'] == 44
    assert r['pairing']['cross_panel_matchings_enumerated'] is None
    for grid in ('PRIMARY', 'SECONDARY'):
        assert not r['temporal'][grid]['cold']['nondecreasing']
        assert r['temporal'][grid]['cold']['nonincreasing']
        assert r['temporal'][grid]['hot']['constant']
        assert not r['temporal'][grid]['hot']['same_trough']['resolved']
    assert r['temporal']['PRIMARY']['hot_flow_late_upper']['constant']
    assert not r['temporal']['SECONDARY']['hot_flow_late_upper']['constant']
    assert all(x['cold_greater_resolved'] for x in r['temperature_contrasts'] if x['nominal_time_s'] != 60)
    assert all(x['physical_viscosity_ratio']['bounds'] is None for x in r['temperature_contrasts'])
    json.dumps(r, allow_nan=False)


def test_outward_serialization_and_deterministic_reproduction(tmp_path):
    a, b = c.analyze(), c.analyze()
    assert a == b
    assert a == json.loads((c.OUTPUT / 'RESULT.json').read_text())
    for r in a['readings'] + a['conductances']:
        if r['lower'] is not None:
            assert F(r['lower']) <= F(r['lower_exact'])
            assert F(r['upper']) >= F(r['upper_exact'])
    subprocess.run([sys.executable, '-m', 'puckworks.analysis.corrochano2017_pressure_flow',
                    '--output', str(tmp_path)], cwd=c.ROOT, check=True, capture_output=True)
    for name, reference in [('RESULT.json', c.OUTPUT), ('conductances.csv', c.OUTPUT), ('readings.csv', c.DATA)]:
        assert (tmp_path / name).read_bytes() == (reference / name).read_bytes()


def test_dataset_scoped_register_and_unchanged_campaign_count():
    spec = importlib.util.spec_from_file_location('available', c.ROOT / 'tools/build_available_data_register.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    register = builder.build()
    family = next(x for x in register['families'] if x['family_id'] == 'ROMANCORROCHANO2017')
    scope = family['dataset_scopes']['romancorrochano2017/fig6_23_pressure_flow_temperature']
    assert scope['source_card'] == 'romancorrochano2017_permeability'
    assert scope['target_exposure'] == 'TARGET_EXPOSED'
    assert family['target_exposure'] == 'UNKNOWN'  # older heterogeneous subsets not overwritten
    assert set(family['dataset_scopes']) == {
        'romancorrochano2017/fig6_23_pressure_flow_temperature',
        'romancorrochano2017/fig6_9_aspect_ratio',
    }
    aspect = family['dataset_scopes']['romancorrochano2017/fig6_9_aspect_ratio']
    assert aspect['target_exposure'] == 'TARGET_EXPOSED'
    assert aspect['physical_validation'] == 'NOT_ESTABLISHED'
    rows = list(csv.DictReader((c.ROOT / 'puckworks/data/MANIFEST.csv').open()))
    alias = {'melrose2019bed': 'romancorrochano2017'}
    def families(rr):
        return {alias.get(x['dataset_id'].split('/')[0], x['dataset_id'].split('/')[0]) for x in rr}
    old = [x for x in rows if x['dataset_id'] != 'romancorrochano2017/fig6_23_pressure_flow_temperature']
    assert families(rows) == families(old)

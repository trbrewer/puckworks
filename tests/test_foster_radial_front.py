"""Focused tests of the source contract and finite representation arithmetic."""
from copy import deepcopy
import csv
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import pytest

from puckworks.analysis import foster2025_radial_front as m

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/'docs/analysis/sci_md_foster_radial_front_001'


def data():
    return json.loads(m.DATA.read_text())


def feature(value):
    if value is None:
        return {'nominal_px': None, 'enclosure_px': None, 'support': 'UNSUPPORTED_READING'}
    lo, hi = value if isinstance(value, tuple) else (value, value)
    return {'nominal_px': (lo+hi)/2, 'enclosure_px': [lo, hi], 'support': 'SUPPORTED'}


def rows():
    return [{'observation_id': f'r{i:02d}', 'shell_id': f'r{i:02d}',
             'shell_midpoint': (2*i+1)/20, 'scan_label_s': 3, 'role': 'primary',
             'eligibility': m.FITTED, 'calibration_id': 'shared', 'duplicate_records': [],
             'center': feature(i), 'lower_endpoint': feature(0), 'upper_endpoint': feature(20)}
            for i in range(10)]


def cals(scale=(F(1), F(1)), offsets=(F(0), F(0))):
    return {'shared': {'alpha': scale, 'nominal': (scale[0], offsets[0]),
                       'vertices': [(a, b) for a in scale for b in offsets]}}


def test_90_unique_slots_and_fixed_30_primary():
    d = data()
    m.validate_cohort(d)
    assert len({r['observation_id'] for r in d['observations']}) == 90
    assert sum(r['role'] == 'primary' for r in d['observations']) == 30
    for mutation in ('duplicate', 'role', 'shell'):
        bad = deepcopy(d)
        if mutation == 'duplicate':
            bad['observations'][-1] = deepcopy(bad['observations'][0])
        elif mutation == 'role':
            bad['observations'][0]['role'] = 'primary'
        else:
            bad['observations'][0]['shell_midpoint'] = .2
        with pytest.raises(ValueError):
            m.validate_cohort(bad)


def test_flat_csv_preserves_nulls_and_statuses():
    flat = list(csv.DictReader(m.DATA.with_suffix('.csv').open()))
    for a, b in zip(data()['observations'], flat):
        assert a['observation_id'] == b['observation_id']
        for k in ('center', 'lower_endpoint', 'upper_endpoint'):
            assert b[k+'_support'] == a[k]['support']
            if a[k]['nominal_px'] is None:
                assert b[k+'_px'] == b[k+'_lo_px'] == b[k+'_hi_px'] == ''
            else:
                assert float(b[k+'_px']) == a[k]['nominal_px']


def test_native_hashes_and_pre_reading_freeze():
    d = data()
    for image in d['images'].values():
        assert hashlib.sha256((ROOT/image['path']).read_bytes()).hexdigest() == image['sha256']
    assert hashlib.sha256((BUNDLE/'PLAN.md').read_bytes()).hexdigest() == d['plan_sha256']
    receipt = json.loads((BUNDLE/'extraction_receipt.json').read_text())
    for k in ('fig8', 'fig9'):
        assert receipt['images'][k]['sha256'] == d['images'][k]['sha256']
        assert receipt['images'][k]['width'] == 1447


def test_exact_witness_calibrations_and_deduplication():
    d = data()
    result = m.analyze(d)
    assert result['feasibility'] == 'NONEMPTY_CHECKED_RATIONAL_WITNESS'
    assert len(result['shared_center_witnesses']) == 3
    assert len(d['observations']) == 90  # neither three nor thirty duplicate records add slots
    for witness in result['shared_center_witnesses']:
        assert F(witness['shared_z']) == F(2,805)*F(witness['fig8_feasible_pixel'])-F(1050,805)
    assert result['calibration_certificates']['fig9_ticks']['alpha_bounds'] == ['1/734', '1/728']
    d['observations'][39]['duplicate_records'][0]['center']['enclosure_px'] = [0, 1]
    assert m.analyze(d)['feasibility'] == m.FAILURE


def test_center_identity_does_not_transfer_endpoints():
    d = data()
    duplicate = d['observations'][39]['duplicate_records'][0]
    duplicate['lower_endpoint'] = feature(0)
    r = m.analyze(d)
    assert r['feasibility'] == m.FAILURE
    assert all(s['G']['status'] == m.FAILURE for s in r['scans'])


def test_rule_zero_and_fit_support_are_not_interchangeable():
    d = data()
    result = m.analyze(d)
    assert [r['fit_eligible_count'] for r in result['scans']] == [0,3,9,10,10,10,10,10,10]
    assert all(result['scans'][i]['E']['status'] == m.UNSUPPORTED for i in (0,1,2))
    r = rows()
    r[4]['eligibility'] = 'UNRESOLVED_FIT_VERSUS_RULE'
    assert m.scan_result(r, cals())['E']['status'] == m.UNSUPPORTED
    assert m.scan_result(r, cals())['D']['status'] == 'QUALIFIED'


def test_inverted_axis_and_outer_minus_inner_sign():
    d = data()
    r = m.analyze(d)['scans'][3]
    assert r['D']['bounds']['exact_lower'] == '-93/728'
    assert r['D']['bounds']['exact_upper'] == '-85/734'
    assert r['D']['direction'] == 'OUTER_SHALLOWER'
    cal = m.calibration(d['calibrations']['fig9_ticks'])
    assert cal['nominal'][0] > 0


def test_independent_center_minimax_is_per_reading_not_robust_fixed_c():
    assert m.independent_e([(F(0),F(10)), (F(5),F(5))]) == (F(0),F(5,2))
    assert m.independent_e([(F(0),F(10))]) == (F(0),F(0))
    # Choosing c=5 before s1 is known costs 5 in the worst case, a different problem.
    assert max(abs(x-5) for x in (0,10)) == 5


def test_touching_intervals_are_compatible():
    r = rows()[:2]
    r[0]['lower_endpoint'], r[0]['upper_endpoint'] = feature(0), feature(1)
    r[1]['lower_endpoint'], r[1]['upper_endpoint'] = feature(1), feature(2)
    assert m.g_enclosure(r, cals()) == (0,0)
    assert m.classify_g((0,0)) == 'COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING'


def test_partial_obstruction_does_not_create_complete_claim():
    r = rows()
    for row in r:
        row['lower_endpoint'], row['upper_endpoint'] = feature(None), feature(None)
    r[0]['lower_endpoint'], r[0]['upper_endpoint'] = feature(0), feature(1)
    r[1]['lower_endpoint'], r[1]['upper_endpoint'] = feature(2), feature(3)
    r[0]['center'], r[1]['center'] = feature(.5), feature(2.5)
    m.check_witness(r, cals())
    result = m.scan_result(r, cals())
    assert result['G']['status'] == m.UNSUPPORTED
    assert result['partial_obstruction']['lower_bound']['exact_lower'] == '1'
    assert result['partial_obstruction']['lower_endpoint_observation'] == 'r01'
    assert result['partial_obstruction']['upper_endpoint_observation'] == 'r00'


def test_shared_offset_cancels_without_asserting_fixed_all_readings_witness():
    r = rows()[:2]
    r[0]['lower_endpoint'], r[0]['upper_endpoint'] = feature(0), feature(2)
    r[1]['lower_endpoint'], r[1]['upper_endpoint'] = feature(1), feature(3)
    cal = cals(offsets=(F(0),F(10)))
    assert m.g_enclosure(r, cal) == (-1,-1)
    # Across all offsets the largest possible lower > smallest possible upper.
    assert max(m.ordinate(x,'lower_endpoint',cal)[1] for x in r) == 11
    assert min(m.ordinate(x,'upper_endpoint',cal)[0] for x in r) == 2


def test_scale_uncertainty_and_mixed_offsets_remain():
    r = rows()
    cal = cals(scale=(F(1),F(2)), offsets=(F(0),F(10)))
    assert m.difference(r[1],'center',r[0],'center',cal) == (1,2)
    cal['other'] = deepcopy(cal['shared'])
    r[1]['calibration_id'] = 'other'
    assert m.difference(r[1],'center',r[0],'center',cal) == (-9,12)


def test_independent_E_D_G_support():
    r = rows()
    r[4]['center'] = feature(None)
    result = m.scan_result(r, cals())
    assert result['E']['status'] == m.UNSUPPORTED
    assert result['D']['status'] == 'QUALIFIED'
    assert result['G']['status'] == 'COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING'
    r[4]['center'] = feature(4)
    r[4]['lower_endpoint'] = feature(None)
    result = m.scan_result(r, cals())
    assert result['E']['status'] == 'QUALIFIED'
    assert result['G']['status'] == m.UNSUPPORTED


@pytest.mark.parametrize('interval,expected', [((1,2),'EXCLUDED_FOR_ALL_ADMISSIBLE_READINGS'),
    ((-2,-1),'COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING'),
    ((-1,0),'COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING'),
    ((0,1),'GRAPHICALLY_UNRESOLVED'), ((-1,1),'GRAPHICALLY_UNRESOLVED')])
def test_strict_and_non_strict_classification(interval, expected):
    assert m.classify_g(interval) == expected
    assert m.classify_g(interval, feasible=False) == m.FAILURE
    assert m.classify_g(interval, supported=False) == m.UNSUPPORTED


def test_infeasible_calibration_or_order_cannot_supply_vacuous_result():
    d = data()
    d['calibrations']['fig9_ticks']['ticks'][0]['z'] = 2
    assert m.analyze(d)['feasibility'] == m.FAILURE
    d = data()
    d['observations'][30]['lower_endpoint'] = feature(900)
    assert m.analyze(d)['feasibility'] == m.FAILURE


def test_outward_reporting_encloses_exact_values():
    for a, b in [(F(1,3),F(2,3)),(F(-2,3),F(-1,3)),(F(0),F(0))]:
        rec = m.bounds_record((a,b))
        assert F(str(rec['lower'])) <= a <= b <= F(str(rec['upper']))


def test_primary_independent_hand_bounds_and_nominal_witnesses():
    r = m.analyze(data())
    # Directly from visible features: t3 extreme center difference 321-232=89 px,
    # each center +/-2 px; scale [1/734,1/728]. One hidden t3 cap blocks complete G.
    s = r['scans'][3]
    assert F(s['E']['bounds']['exact_lower']) == F(85,1468)
    assert F(s['E']['bounds']['exact_upper']) == F(93,1456)
    assert s['G']['status'] == m.UNSUPPORTED
    assert 'bounds' not in s['G']
    # At t4, max lower-cap box is [453,461], min upper-cap box [506,510].
    assert F(r['scans'][4]['G']['bounds']['exact_lower']) == F(-57,728)
    assert F(r['scans'][4]['G']['bounds']['exact_upper']) == F(-45,734)
    for s in r['scans'][3:6]:
        assert s['E']['bounds']['lower'] > 0
        assert s['D']['bounds']['upper'] < 0
        if s['scan_label_s'] in (4,5):
            assert s['G']['status'] == 'COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING'
            assert s['G']['nominal_A'] <= s['G']['nominal_B']
        assert s['partial_obstruction'] is None


def test_deterministic_offline_report_matches_committed_result(tmp_path):
    d = data()
    a, b = tmp_path/'a', tmp_path/'b'
    for output in (a,b):
        m.write_report(d, m.analyze(d), output)
    for name in ('scan_results.json','scan_results.csv','summary.json'):
        assert (a/name).read_bytes() == (b/name).read_bytes() == (BUNDLE/name).read_bytes()


def test_new_intake_does_not_claim_model_calibration_or_physical_measurements():
    from puckworks.insights.corpus_map import build
    corpus = build()
    dataset = 'dataset:foster2025_2/fig8_fig9_radial_front'
    relations = [r for r in corpus['relations'] if r['source'] == dataset or r['target'] == dataset]
    assert any(r['type'] == 'DERIVED_FROM' for r in relations)
    assert not any(r['type'] in {'CALIBRATED_FROM', 'VALIDATED_AGAINST'} for r in relations)
    assert not any(r['target'] in {'observable:porosity','observable:permeability','observable:flow'}
                   for r in relations)

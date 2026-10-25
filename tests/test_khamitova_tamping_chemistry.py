"""Synthetic verification is not source validity; source review is in the bundle."""
import csv
from fractions import Fraction as Q
import hashlib
import json
import subprocess
import sys

import pytest

from puckworks.analysis import khamitova2020_tamping_chemistry as k


def block(y, r=(1, 1, 1, 1), yp=(2, 2, 2, 2), rp=(1, 1, 1, 1)):
    return k.analyze_block(dict(zip(k.FORCES, y)), dict(zip(k.FORCES, r)),
                           dict(zip(k.FORCES, yp)), dict(zip(k.FORCES, rp)))


def test_interior_excursion_minimax_and_ties():
    b = block([10, 16, 12, 10])
    assert [b[x] for x in ('Delta', 'R', 'E', 'c_star', 'E_percent_reference',
                           'endpoint_missed_range')] == [0, 6, 3, 13, 30, 6]
    assert b['minimum_forces'] == [10, 30]
    assert b['maximum_forces'] == b['interior_maximum_forces'] == [15]
    assert b['interior_minimum_forces'] == []
    assert max(abs(y-b['c_star']) for y in b['means']) == b['E']
    # Arithmetic mean (12) is not the minimax midpoint (13).
    assert sum(b['means'])/4 != b['c_star']


def test_range_upper_uses_distinct_observations():
    assert k.range_bounds([(Q(0), Q(100))]+[(Q(50), Q(50))]*3) == (0, 50)
    assert k.range_bounds([(Q(1), Q(2)), (Q(3), Q(4)), (Q(2), Q(3)), (Q(2), Q(2))]) == (1, 3)


def test_hand_rsd_and_units_rescaling():
    b = block([1, 1, 2, 2], [100, 100, 50, 50])
    assert b['reported_rsd_scales'] == [1]*4
    assert b['lambda_star'] == Q(1, 2)
    assert b['lambda_attaining_pairs'] == [[10,20], [10,30], [15,20], [15,30]]
    scaled = block([1000,1000,2000,2000], [100,100,50,50])
    assert scaled['lambda_star'] == b['lambda_star']
    assert scaled['E_percent_reference'] == b['E_percent_reference']
    assert scaled['E'] == 1000*b['E']


@pytest.mark.parametrize('last,status', [('10.02','POSITIVE_UNDER_ROUNDING_CONVENTION'),
 ('9.98','NEGATIVE_UNDER_ROUNDING_CONVENTION'), ('10.01','ROUNDING_UNRESOLVED'),
 ('9.99','ROUNDING_UNRESOLVED'), ('10.00','ROUNDING_UNRESOLVED')])
def test_signed_endpoint_bounds_and_strict_touching(last, status):
    b = block(['10.00','11.00','9.00',last])
    assert b['endpoint_rounding_status'] == status
    assert b['Delta_lower'] == Q(last)-Q(10)-Q('0.01')
    assert b['Delta_upper'] == Q(last)-Q(10)+Q('0.01')
    assert b['Percent_change_lower'] == 100*((Q(last)-Q('.005'))/Q('10.005')-1)
    assert b['Percent_change_upper'] == 100*((Q(last)+Q('.005'))/Q('9.995')-1)


def test_display_rounding_never_controls_decision():
    b = block(['1.000000000000000','1','1','1.000000000000002'], yp=(15,15,15,15))
    assert k.decimal_view(b['Delta_lower']) == '0'
    assert b['endpoint_rounding_status'] == 'POSITIVE_UNDER_ROUNDING_CONVENTION'


@pytest.mark.parametrize('bad', [None, 'NaN', 'Infinity', '-Infinity', 'bad'])
def test_missing_middle_retains_endpoint_and_partial_lower_bound(bad):
    b = block([10,bad,12,11])
    assert b['endpoint_status'] == 'SUPPORTED' and b['Delta'] == 1
    assert b['representation_status'] == 'UNSUPPORTED'
    assert b['R'] is b['E'] is b['c_star'] is None
    assert b['partial_range_lower_bound'] == 2
    assert b['rsd_nominal_status'] == 'UNSUPPORTED'
    assert 'Infinity' not in json.dumps(k.exact(b), allow_nan=False)


def test_missing_endpoint_and_no_means():
    b = block([None,2,3,4])
    assert b['endpoint_status'] == b['representation_status'] == 'UNSUPPORTED'
    assert b['partial_range_lower_bound'] == 2
    assert block([None]*4)['partial_range_lower_bound'] is None


@pytest.mark.parametrize('y10', [0, -1])
def test_invalid_normalizing_denominator_keeps_native_result(y10):
    b = block([y10,1,2,3])
    assert b['endpoint_status'] == b['representation_status'] == 'SUPPORTED'
    assert b['endpoint_normalization_status'] == b['representation_normalization_status'] == 'UNSUPPORTED'
    assert b['Percent_change'] is b['E_percent_reference'] is None
    assert b['rsd_nominal_status'] == 'UNSUPPORTED'
    assert b['endpoint_normalized_rounding_status'] == 'UNSUPPORTED'


def test_rounding_denominator_crosses_zero_nominal_survives():
    b = block(['0.1',1,2,3], yp=(0,2,2,2))
    assert b['Percent_change'] == 2900
    assert b['endpoint_normalized_rounding_status'] == 'UNSUPPORTED'
    assert b['representation_normalized_rounding_status'] == 'UNSUPPORTED'
    assert b['rsd_nominal_status'] == 'FINITE'
    assert b['rsd_rounding_status'] == 'UNSUPPORTED'


def test_missing_precision_is_result_specific():
    b = block([1,2,3,4], yp=(2,None,2,2))
    assert b['endpoint_rounding_status'] == 'POSITIVE_UNDER_ROUNDING_CONVENTION'
    assert b['representation_rounding_status'] == 'UNSUPPORTED'
    assert b['representation_status'] == 'SUPPORTED'
    assert b['rsd_nominal_status'] == 'FINITE' and b['rsd_rounding_status'] == 'UNSUPPORTED'
    b = block([1,2,3,4], rp=(1,None,1,1))
    assert b['rsd_nominal_status'] == 'FINITE' and b['rsd_rounding_status'] == 'UNSUPPORTED'
    assert b['representation_rounding_status'] != 'UNSUPPORTED'


@pytest.mark.parametrize('bad', [None, '-0.01', 'NaN', 'Infinity', 'bad'])
def test_missing_invalid_rsd_never_suppresses_primary(bad):
    b = block([1,2,3,4], [1,bad,1,1])
    assert b['representation_status'] == b['endpoint_status'] == 'SUPPORTED'
    assert b['rsd_nominal_status'] == b['rsd_rounding_status'] == 'UNSUPPORTED'
    assert b['lambda_star'] is None


def test_zero_scales_and_rounded_to_zero():
    b = block([1,2,3,4], [0,0,10,10])
    assert b['rsd_nominal_status'] == 'UNBOUNDED_ZERO_SCALES'
    assert b['lambda_star'] is None and b['lambda_attaining_pairs'] == [[10,15]]
    assert b['rsd_rounding_status'] == 'CONSERVATIVE_UNBOUNDED_UPPER_ENCLOSURE'
    assert b['lambda_upper'] is None and b['lambda_lower'] > 0
    b = block([1,1,2,2], [0,0,50,50])
    assert b['rsd_nominal_status'] == 'FINITE' and b['lambda_star'] == 1
    assert b['lambda_attaining_pairs'] == [[10,20],[10,30],[15,20],[15,30]]
    assert b['rsd_rounding_status'] == 'CONSERVATIVE_UNBOUNDED_UPPER_ENCLOSURE'
    b = block([1]*4, [0]*4)
    assert b['lambda_star'] == 0 and len(b['lambda_attaining_pairs']) == 6
    assert b['lambda_lower'] == 0 and b['lambda_upper'] is None
    json.dumps(k.exact(b), allow_nan=False)


def test_conservative_enclosures_contain_nominal_and_corner_values():
    # Finite corner checks corroborate the interval implementation, not a proof.
    b = block([1,2,3,4], [10,20,30,40])
    assert b['lambda_lower'] <= b['lambda_star'] <= b['lambda_upper']
    assert b['E_percent_reference_lower'] <= b['E_percent_reference'] <= b['E_percent_reference_upper']
    for sign in (-1,1):
        c = block([Q(v)+sign*Q('.005') for v in (1,2,3,4)],
                  [Q(v)-sign*Q('.05') for v in (10,20,30,40)])
        assert b['lambda_lower'] <= c['lambda_star'] <= b['lambda_upper']


def test_zero_not_excluded_and_equal_means():
    b = block([1]*4)
    assert b['R'] == b['E'] == b['endpoint_missed_range'] == 0
    assert b['representation_rounding_status'] == 'ZERO_NOT_EXCLUDED_UNDER_ROUNDING_CONVENTION'
    assert b['minimum_forces'] == b['maximum_forces'] == list(k.FORCES)
    assert b['E_lower'] == 0 and b['E_upper'] == Q('.005')


def test_outward_decimal_serialization():
    for v in (Q(1,3), Q(-1,3), Q(1,10**14), Q(-1,10**14)):
        assert Q(k.decimal_view(v,-1)) <= v <= Q(k.decimal_view(v,1))


def test_complete_cohort_source_precision_mapping_and_unit_audit():
    report = k.build_report()
    assert report['coverage'] == dict(observation_requests=144, observations=144, endpoint_requests=36,
        mean_supported=144, rsd_supported=144,
        mean_rounding_metadata_supported=144, rsd_rounding_metadata_supported=144,
        four_level_requests=36, endpoint_supported=36, four_level_supported=36,
        endpoint_normalization_supported=36, representation_normalization_supported=36,
        endpoint_rounding_supported=36, representation_rounding_supported=36,
        endpoint_normalized_rounding_supported=36, representation_normalized_rounding_supported=36,
        rsd_nominal_finite=36, rsd_rounding_finite=36)
    obs = report['observations']
    assert len({(r['analyte'],r['temperature_C'],r['pressure_bar'],r['tamp_force_kgf']) for r in obs}) == 144
    assert all((r['amount_decimal_places'],r['concentration_decimal_places'],r['rsd_decimal_places']) == (2,2,1) for r in obs)
    assert obs[0]['amount_string'] == '131.84' and obs[0]['concentration_string'] == '3.29'
    bad = [r for r in obs if r['related_unit_status'].startswith('SOURCE_PAIR')]
    assert bad == [obs[0]]
    assert next(r for r in obs if r['analyte']=='total CQA' and r['pressure_bar']==9 and r['temperature_C']==88 and r['tamp_force_kgf']==10)['amount_string'] == '133.30'
    ground = list(csv.DictReader((k.BUNDLE/'ground_audit.csv').open()))
    assert len(ground)==8 and [r['source_string'] for r in ground] == ['37.17','0.1','16.24','7.0','8.55','9.9','0.36','2.6']
    for path, sha in report['input_sha256'].items():
        p = k.ROOT/path if path.startswith('puckworks/') else k.BUNDLE/path
        assert hashlib.sha256(p.read_bytes()).hexdigest() == sha


def test_selected_real_arithmetic():
    b = block(['131.84','144.31','140.67','138.49'], ['2.9','1.9','3.9','5.1'])
    assert (b['R'],b['E'],b['c_star'],b['Delta'],b['endpoint_missed_range']) == tuple(map(Q,['12.47','6.235','138.075','6.65','5.82']))
    assert (b['E_lower'],b['E_upper']) == (Q('6.23'),Q('6.24'))
    assert b['lambda_attaining_pairs'] == [[10,15]]
    assert b['lambda_star'] == Q('12.47')/(Q('131.84')*Q('.029')+Q('144.31')*Q('.019'))


def test_deterministic_offline_export_and_committed_artifacts(tmp_path):
    for directory in (tmp_path/'a', tmp_path/'b'):
        subprocess.run([sys.executable,'-m','puckworks.analysis.khamitova2020_tamping_chemistry',
                        '--output',str(directory)],check=True,capture_output=True,cwd=k.ROOT)
    for filename in ('results.json','observations.csv','representation.csv','endpoints.csv'):
        actual = (tmp_path/'a'/filename).read_bytes()
        assert actual == (tmp_path/'b'/filename).read_bytes() == (k.BUNDLE/filename).read_bytes()
    result=json.loads((tmp_path/'a/results.json').read_text())
    rows=list(csv.DictReader((tmp_path/'a/representation.csv').open()))
    assert len(rows)==36
    for row, b in zip(rows, result['blocks']):
        for key in ('Delta_lower','E_lower','lambda_lower','E_percent_reference_lower'):
            assert Q(row[key]) <= Q(b[key])
        for key in ('Delta_upper','E_upper','lambda_upper','E_percent_reference_upper'):
            assert Q(row[key]) >= Q(b[key])


def write_audit_copy(tmp_path, transform):
    with (k.BUNDLE/'cell_audit.csv').open() as f:
        rows=list(csv.DictReader(f))
    transform(rows)
    with (tmp_path/'cell_audit.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        w.writeheader();w.writerows(rows)


def test_audit_missing_precision_and_rsd_support_remain_separate(tmp_path):
    def change(rows):
        rows[1]['amount_decimal_places']=''
        rows[1]['rsd_support']='UNSUPPORTED'
    write_audit_copy(tmp_path,change)
    observations=k.load_observations(tmp_path)
    row=observations[1]
    assert row['amount']==Q('144.31') and row['mean_support']=='SUPPORTED'
    assert row['amount_rounding_support']==row['precision_support']=='UNSUPPORTED'
    assert row['rsd_support']=='UNSUPPORTED' and row['rsd_rounding_support']=='SUPPORTED'


@pytest.mark.parametrize('change', [
    lambda rows: rows.append(rows[0]),
    lambda rows: rows.pop(),
    lambda rows: rows[0].update(amount_string='131.85'),
    lambda rows: rows[0].update(amount_decimal_places='1'),
    lambda rows: rows[0].update(csv_row_1based='3'),
])
def test_audit_mapping_value_precision_and_cohort_drift_rejected(tmp_path,change):
    write_audit_copy(tmp_path,change)
    with pytest.raises(ValueError):
        k.load_observations(tmp_path)

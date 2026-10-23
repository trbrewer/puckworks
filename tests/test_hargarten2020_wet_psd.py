"""Risk-based checks for midpoint CDF bounds, not physical-bin validation."""
import copy
import csv
from fractions import Fraction as F
import json
import subprocess
import sys

import pytest

from puckworks.analysis import hargarten2020_wet_psd as h


@pytest.fixture
def panel():
    return dict(x_anchors_px=[100,300],x_anchor_um=['10','1000'],x_scale='log10',
                y_anchors_px=[500,0],anchor_allowance_px='1',reading_allowance_px='3')


def marker(name,d,lo,hi=None):
    return dict(point_id=name,diameter_um=[F(d),F(d)],bounds=[F(lo),F(lo if hi is None else hi)])


def rawpoint(x,y,**kw):
    return dict(point_id=str(x),x_px=str(x),y_px=str(y),G_status='SUPPORTED',
                P_status='UNSUPPORTED_ENDPOINTS',ci_top_px='',ci_bottom_px='',**kw)


def test_log_axis_not_linear_and_panel_specific(panel):
    lo,hi=h.diameter_bounds(200,panel)
    assert lo < 100 < hi and hi < 120
    shifted=copy.deepcopy(panel);shifted['x_anchors_px']=[200,400]
    assert h.diameter_bounds(300,shifted)==(lo,hi)
    assert h.diameter_bounds(200,shifted)[1] < lo
    panel['x_scale']='linear'
    with pytest.raises(ValueError):h.diameter_bounds(200,panel)


@pytest.mark.parametrize('exponent,expected',[('0',1),('1',10),('2',100),('-1',F(1,10))])
def test_transcendental_outward_enclosure(exponent,expected):
    lo,hi=h._pow10_enclosure(F(exponent))
    assert lo <= expected <= hi
    assert hi-lo <= F(2,10**6)


def test_y_scale_fraction_and_percentage_points(panel):
    assert h.ordinate_bounds(250,250,panel)==(F(123,250),F(127,250))
    assert h._display_bounds([F(1,100),F(2,100)],100)==['1.000000','2.000000']
    assert h._display_bounds([F(-1,3),F(1,3)])==['-0.333334','0.333334']


def test_tail_not_forced(panel):
    lo,hi=h.ordinate_bounds(0,0,panel)
    assert lo < 1 and hi==1
    lo,hi=h.ordinate_bounds(500,500,panel)
    assert lo==0 and hi > 0


def test_bad_axis_and_reversed_ci_rejected(panel):
    with pytest.raises(ValueError):h.ordinate_bounds(100,50,panel)
    panel['y_anchors_px']=[1,0]
    with pytest.raises(ValueError):h.ordinate_bounds(0,0,panel)


def test_shared_calibration_monotone_witness_not_isotonic_fit(panel):
    pp=[rawpoint(100,450),rawpoint(200,250),rawpoint(300,250)]
    r=h.cdf_feasibility(pp,panel,'G')
    assert r['admissible']
    assert r['witness'][1]['F']==r['witness'][2]['F']
    assert pp[1]['y_px']=='250'
    pp[2]['y_px']='450'
    assert not h.cdf_feasibility(pp,panel,'G')['admissible']
    pp[2]['x_px']='200'
    assert not h.cdf_feasibility(pp,panel,'G')['admissible']


def test_quantile_strict_below_plateau_and_tail():
    pp=[marker('a',10,'.1'),marker('b',20,'.5'),marker('c',30,'.5'),marker('d',40,'.9')]
    q=h.quantile_enclosure(pp,F('.5'))
    assert q['bounds_um']==[10,20] and q['lower_anchor']=='a' and q['upper_anchor']=='b'
    assert h.quantile_enclosure(pp,F('.99'))['bounds_um']==[40,None]
    assert h.quantile_enclosure(pp,F('.05'))['bounds_um']==[None,10]


def test_gaps_and_coordinate_uncertainty_not_interpolation():
    a=marker('a',10,'.1','.2');b=marker('b',30,'.6','.7')
    a['diameter_um']=[F(9),F(11)];b['diameter_um']=[F(29),F(31)]
    assert h.cutoff_enclosure([a,b],20)['bounds']==[F('.1'),F('.7')]
    assert h.cutoff_enclosure([a,b],10)['bounds'] is None
    assert h.quantile_enclosure([a,b],F('.5'))['bounds_um']==[9,31]


def test_known_uniformly_scaled_synthetic_cdf():
    dry=[marker('d'+str(i),d,q) for i,(d,q) in enumerate([(10,'.1'),(20,'.4'),(40,'.7'),(80,'.95')])]
    wet=[dict(p,point_id='w'+p['point_id'],diameter_um=[v*2 for v in p['diameter_um']]) for p in dry]
    rows=[]
    for q in ['.16','.5','.84']:
        d=h.quantile_enclosure(dry,F(q))['bounds_um'];w=h.quantile_enclosure(wet,F(q))['bounds_um']
        bounds=h.ratio_enclosure(d,w);assert bounds[0] <= 2 <= bounds[1]
        rows.append(dict(id=q,bounds=bounds))
    result=h.scale_intersection(rows)
    assert result['bounds'][0] <= 2 <= result['bounds'][1]
    assert result['outcome']=='NONEMPTY_OUTER_CANDIDATE_RANGE'


@pytest.mark.parametrize('lo,hi,outcome',[('0','.2',h.NOT_EXCLUDED),('-.1','.1',h.NOT_EXCLUDED),('0.0000000000000000000000001','.1',h.EXCLUDED)])
def test_strict_positive_excess_and_exact_contact(lo,hi,outcome):
    rows=[dict(id='w',bounds=[F(lo),F(hi)])]
    assert h.cdf_disposition(rows)['outcome']==outcome


def test_positive_witness_precedes_missing_and_no_witness_is_unresolved():
    missing=dict(id='missing',bounds=None)
    assert h.cdf_disposition([dict(id='yes',bounds=[F('.01'),F('.02')]),missing])['outcome']==h.EXCLUDED
    assert h.cdf_disposition([dict(id='zero',bounds=[F(0),F('.02')]),missing])['outcome']==h.UNRESOLVED


def test_intersections_separation_contact_partial_and_no_epsilon():
    assert h.ratio_enclosure([F(0),F(2)],[F(1),F(3)]) is None
    assert h.ratio_enclosure([None,F(2)],[F(1),F(3)]) is None
    assert h.scale_intersection([dict(id='a',bounds=[F('.5'),F('.9')])])['outcome']==h.SCALE_EXCLUDED
    contact=[dict(id='a',bounds=[F('.5'),F(1)])]
    assert h.scale_intersection(contact)['outcome']=='NONEMPTY_OUTER_CANDIDATE_RANGE'
    assert h.scale_intersection(contact+[dict(id='x',bounds=None)])['outcome']=='PARTIAL_OUTER_CANDIDATE_RANGE'
    disjoint=[dict(id='a',bounds=[F(1),F(2)]),dict(id='b',bounds=[F(3),F(4)]),dict(id='missing',bounds=None)]
    r=h.scale_intersection(disjoint)
    assert r['outcome']==h.SCALE_EXCLUDED and r['lower_operand']=='b' and r['upper_operand']=='a'


def test_retained_contract_counts_and_physical_mapping():
    r=h.analyze()
    assert len(r['cdf_readings'])==36 and len(r['contrasts'])==36
    assert len(r['quantile_diameters'])==120 and len(r['multiplier_intervals'])==60
    assert len(r['intersections'])==14
    assert r['physical_cutoff_mapping'].startswith('UNRESOLVED')
    assert all(x['admissible'] for x in r['feasibility'])
    assert all('light_L' not in x['series_id'] for x in r['marker_bounds'])
    assert all(x['bounds'] is None for x in r['marker_bounds'] if x['layer']=='P' and x['series_id']=='non_sieved_dry')


def test_inconsistent_source_never_creates_vacuous_exclusion(tmp_path):
    (tmp_path/'contract.json').write_bytes((h.INPUT/'contract.json').read_bytes())
    pp=list(csv.DictReader((h.INPUT/'coordinates.csv').open()))
    dry=[x for x in pp if x['series_id']=='non_sieved_dry']
    dry[0]['y_px']='20';dry[1]['y_px']='520'
    with (tmp_path/'coordinates.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(pp[0]));w.writeheader();w.writerows(pp)
    r=h.analyze(tmp_path)
    assert all(x['outcome']==h.UNRESOLVED for x in r['conditions'])
    assert not any(x['type']=='CDF_EXCESS' for x in r['witnesses'])


def test_retained_outputs_and_independent_checker():
    produced=json.loads(json.dumps(h.analyze(),default=h._json_default))
    assert produced==json.loads((h.OUTPUT/'RESULT.json').read_text())
    checker=h.OUTPUT/'review_check.py'
    assert checker.is_file()
    subprocess.run([sys.executable,str(checker)],check=True,capture_output=True,text=True)


def test_preserved_accepted_inputs():
    protected=json.loads((h.INPUT/'holdings_checked.json').read_text())['protected_sha256']
    import hashlib
    for name,digest in protected.items():
        assert hashlib.sha256((h.ROOT/name).read_bytes()).hexdigest()==digest

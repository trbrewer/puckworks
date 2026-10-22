"""Meaningful synthetic reading/support controls and authenticated source facts."""
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
import subprocess
import sys

import pytest

from puckworks.analysis import corrochano2017_hydration_flow as h


@pytest.fixture(scope='module')
def result():
    return h.analyze()


def synthetic_cal(guard='0'):
    return h.Calibration(dict(x_20='30',x_80='90',y_0='100',y_1='0',
                              anchor_guard_pt=guard,stroke_guard_pt=guard,
                              reconstruction_guard_pt='0'))


def test_affine_clock_nonzero_intercept_and_exact_reported_decimal_ratios():
    c,_,cal,_=h.load()
    assert cal.x(20)==F(c['calibration']['x_20'])
    assert cal.x(80)==F(c['calibration']['x_80'])
    assert F('0.999')<cal.time(F('186.3758544921875'))<F('1.001')
    assert cal.time(cal.x(0))==0
    for name,expected in [('caption',F(21,122)),('prose',F(209,1220))]:
        r=F(c['flows'][name])/F(c['flows']['high'])
        assert r==expected==F(c['ratios'][name])
        assert r*60<60 and F(c['flows'][name])*60==F(c['flows']['high'])*(r*60)
    # Scaling raw page x instead of calibrated time is wrong for this nonzero intercept.
    assert cal.time(cal.x(60)*F(21,122)) != 60*F(21,122)


def test_full_horizontal_extrema_not_just_center_or_query_endpoints():
    segments=[((F(0),F(0)),(F(1),F(10))),((F(1),F(10)),(F(2),F(0)))]
    assert h.curve_extrema(segments,(F(1,2),F(3,2)))==(5,10)
    assert h.curve_extrema(segments,(F(0),F(2)))==(0,10)
    with pytest.raises(ValueError,match='No represented'):
        h.curve_extrema(segments,(F(3),F(4)))


def test_repeated_x_preserves_vertical_segment():
    segments=[((F(1),F(2)),(F(1),F(9))),((F(1),F(9)),(F(2),F(3)))]
    assert h.curve_extrema(segments,(F(1),F(1)))==(2,9)


def test_endpoint_and_disconnected_gap_support_is_not_truncated():
    cal=synthetic_cal('1')
    trace=dict(segments=[((F(10),F(0)),(F(20),F(10))),((F(22),F(12)),(F(30),F(20)))],
               support_x=[(F(10),F(20)),(F(22),F(30))])
    for t in [0,9,12,20]:
        r=h.read_trace(trace,F(t),cal)
        assert r['nominal_support'] and not r['full_support'] and r['bounds'] is None
    assert h.union(trace['support_x'])==trace['support_x']
    assert h.intersection([(F(0),F(50))],trace['support_x'])==trace['support_x']


def test_horizontal_uncertainty_changes_steep_reading_and_no_ordinate_clipping():
    trace=dict(segments=[((F(0),F(200)),(F(120),F(-40)))],support_x=[(F(0),F(120))])
    exact=h.read_trace(trace,F(40),synthetic_cal())['bounds']
    wide=h.read_trace(trace,F(40),synthetic_cal('1'))['bounds']
    assert exact==(0,0) and wide[0]<0<wide[1]
    assert h.read_trace(trace,F(90),synthetic_cal('1'))['bounds'][1]>1


def test_cartesian_relaxation_contains_shared_axis_readings():
    cal=synthetic_cal('1')
    # Shared anchors are not chosen independently for the two traces in witnesses.
    for t in [F(0),F(30),F(100)]:
        query=cal.query(t)
        for x20,x80 in product([F(29),F(30),F(31)],[F(89),F(90),F(91)]):
            x=x20+(t-20)*(x80-x20)/60
            for dx in [-1,0,1]:
                assert query[0]<=x+dx<=query[1]
        bounds=cal.ordinate((F(20),F(40)))
        for zero,one,p in product([F(99),F(100),F(101)],[F(-1),F(0),F(1)],range(19,42)):
            assert bounds[0]<=(zero-p)/(zero-one)<=bounds[1]


def test_full_support_inverse_exact_at_boundary_and_preserves_positive_lower():
    cal=synthetic_cal('1');support=[(F(30),F(90)),(F(110),F(130))]
    full=cal.time_support(support,True)
    assert len(full)==2 and full[0][0]>20
    for a,b in full:
        assert h.contains(support,cal.query(a)) and h.contains(support,cal.query(b))
        assert not h.contains(support,cal.query(a-F(1,100)))
        assert not h.contains(support,cal.query(b+F(1,100)))


def test_complete_envelope_requires_all_three_ids():
    rr={t:dict(full_support=True,nominal_support=True,bounds=(F(i),F(i+1)))
        for i,t in enumerate(['L1','L2','L3'])}
    assert h.envelope(rr,['L1','L2','L3'])['bounds']==(0,3)
    rr['L3']['full_support']=False
    e=h.envelope(rr,['L1','L2','L3'])
    assert e['completeness']=='INCOMPLETE' and e['missing_ids']==['L3']
    assert e['contributing_ids']==['L1','L2'] and e['nominal_support']
    assert not e['full_support']


@pytest.mark.parametrize('lo,hi,expected',[(('-2','-1'),('1','2'),h.SEPARATED),
                                         (('1','2'),('-2','-1'),h.SEPARATED),
                                         (('0','1'),('1','2'),h.OVERLAP),
                                         (('0','2'),('1','3'),h.OVERLAP)])
def test_signed_interval_subtraction_and_strict_sign(lo,hi,expected):
    a,b=tuple(map(F,lo)),tuple(map(F,hi));d=h.subtract(a,b)
    assert d==(a[0]-b[1],a[1]-b[0]) and h.classify(d)==expected
    assert h.subtract(b,a)==(-d[1],-d[0])


def test_display_rounding_does_not_decide_sign():
    d=(F(-1,10**7),F(-1,10**9))
    assert h.outward(d)==['-0.000001','0.000000']
    assert h.classify(d)==h.SEPARATED
    assert h.classify((F(-1),F(0)))==h.OVERLAP
    assert h.classify(None)==h.UNSUPPORTED
    with pytest.raises(ValueError,match='Invalid'):
        h.classify((F(1),F(-1)))


def test_native_transform_stroke_chunk_legend_and_duplicate_provenance():
    paths=json.loads((h.DATA/'paths.json').read_text())
    curves=[p for p in paths['chunks'] if p['role']=='curve']
    legends=[p for p in paths['chunks'] if p['role']=='legend_excluded']
    assert paths['page_xref']==3193 and paths['content_xrefs']==[3194]
    assert len(curves)==15 and len(legends)==2 and len(paths['trace_chunks'])==6
    assert {p['seqno'] for p in curves}==set(range(30,45))
    assert {p['seqno'] for p in legends}=={50,52}
    assert len({p['raw_path_sha256'] for p in curves})==15
    for p in curves:
        sx,sy=p['graphics_scale'];tx,ty=p['graphics_translation'];ox,oy=p['local_translation']
        assert p['start']==pytest.approx([tx+sx*ox,paths['page_height_pt']-ty-sy*oy],abs=.0002)
        assert p['width_api_pt']==pytest.approx(3*(sx*sy)**.5,abs=.0002)
        assert p['effective_width_upper_pt']<=1.822108
        assert p['effective_width_upper_pt']/2<.92
        assert p['raw_path_offset']>=p['raw_stream_offset']
    assert len(paths['joins'])==9 and not paths['duplicate_curve_chunks']
    for j in paths['joins']:
        assert max(map(abs,j['delta_pt']))<=.001<j['bound_pt']
    _,_,_,traces=h.load()
    assert any(a[0]==b[0] and a[1]!=b[1] for a,b in traces['H2']['segments'])
    assert 'Repeated' in paths['duplicate_artwork']


def test_all_requests_support_decision_logic_and_pair_roles(result):
    assert len(result['envelopes'])==45 and len(result['pairs'])==405
    for family,n,p in [('fixed-rescaling',30,270),('same-clock',15,135)]:
        assert sum(e['family']==family for e in result['envelopes'])==n
        assert sum(e['family']==family for e in result['pairs'])==p
    for s in result['summary']:
        ee=[e for e in result['envelopes'] if all(e[k]==s[k] for k in ['family','grid','interpretation'])]
        assert len(ee)==(8 if s['grid']=='PRIMARY' else 7)
        supported=[e for e in ee if e['classification']!=h.UNSUPPORTED]
        separation=any(e['classification']==h.SEPARATED for e in supported)
        assert (s['disposition']=='SUPPORTED_DISCREPANCY')==separation
        assert s['complete']+s['incomplete']==len(ee)
        for e in supported:
            assert e['difference']==h.subtract(e['low_envelope']['bounds'],e['high_envelope']['bounds'])
            assert len(e['low_envelope']['contributing_ids'])==len(e['high_envelope']['contributing_ids'])==3
    for p in result['pairs']:
        if p['difference'] is not None:
            assert p['reason']=='PAIR_SPECIFIC_ONLY'
    # Independently checked source-support fact, not the motivating separation oracle.
    early=[e for e in result['envelopes'] if e['family']=='fixed-rescaling' and e['low_time_s'] in [10,15]]
    assert len(early)==4 and all(e['classification']==h.UNSUPPORTED for e in early)
    assert all(e['high_envelope']['nominal_support'] for e in early if e['low_time_s']==15)


def test_transformed_support_segment_intersections(result):
    for s in result['pair_support']:
        for kind in ['nominal','full_contract']:
            a=result['trace_support'][s['low_id']][kind]
            b=result['trace_support'][s['high_id']][kind]
            r=s['ratio'];expected=h.intersection(a,[(lo/r,hi/r) for lo,hi in b])
            assert s[kind+'_low_time_s']==expected
            assert all(lo>0 for lo,hi in expected)
            if s['family']=='fixed-rescaling':
                q=F('0.0000021') if s['interpretation']=='caption' else F('0.00000209')
                assert s[kind+'_mean_throughput_proxy_m3']==[(lo*q,hi*q) for lo,hi in expected]


def test_loader_dataset_scoped_evidence_and_campaign():
    from puckworks.data import rc17_fig6_22_hydration_flow
    rows=rc17_fig6_22_hydration_flow()
    assert len(rows)==4222 and {r['trace'] for r in rows}==set(h.IDS['low']+h.IDS['high'])
    register=json.loads((h.ROOT/'puckworks/data/AVAILABLE_DATA_REGISTER.json').read_text())
    family=next(f for f in register['families'] if f['family_id']=='ROMANCORROCHANO2017')
    scope=family['dataset_scopes']['romancorrochano2017/fig6_22_hydration_flow']
    assert scope['target_exposure']=='TARGET_EXPOSED'
    assert scope['physical_validation']=='NOT_ESTABLISHED'
    assert 'no new independent campaign' in scope['campaign']
    assert 'normalization' in ' '.join(scope['missing_joins'])
    assert 'absolute HR law exclusion' in scope['blocked_uses']


def test_deterministic_offline_reproduction_plan_identity(tmp_path,monkeypatch):
    # Any PDF/open/network in the routine producer is unnecessary; subprocess runs
    # using only compact inputs, and the normal module imports no PDF package.
    subprocess.run([sys.executable,'-m','puckworks.analysis.corrochano2017_hydration_flow',
                    '--output',str(tmp_path)],cwd=h.ROOT,check=True)
    for name in ['RESULT.json','envelopes.csv','pairs.csv','readings.csv','pair_support.csv']:
        assert (tmp_path/name).read_bytes()==(h.OUTPUT/name).read_bytes()
    c=json.loads((h.DATA/'contract.json').read_text())
    assert c['plan_sha256']==hashlib.sha256((h.OUTPUT/'PLAN.md').read_bytes()).hexdigest()
    with (tmp_path/'envelopes.csv').open() as f:
        assert len(list(csv.DictReader(f)))==45

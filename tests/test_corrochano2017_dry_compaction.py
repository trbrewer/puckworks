"""Scientific failure modes: synthetic counterexamples, then source/replay consistency."""
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
import subprocess
import sys

import pytest

from puckworks.analysis import corrochano2017_dry_compaction as d
from tools.extract_corrochano2017_dry_compaction import transform


def axis(anchor=0, trace=0, reverse=False):
    return d.Axis({'values': [0, 100], 'positions_pt': [100, 0] if reverse else [0, 100]},
                  F(anchor), F(trace))


def segments(points):
    pp = [tuple(map(F, p)) for p in points]
    return list(zip(pp, pp[1:]))


def reading(bounds, status='SUPPORTED'):
    return {'bounds': tuple(map(F, bounds)) if bounds else None, 'status': status,
            'full_support': bounds is not None, 'reason': 'synthetic'}


def test_composed_transform_and_anisotropic_stroke():
    assert transform('2','3',['2','4'],['10','20'],['5','6'],'200') == (24,144)
    _, paths, _, _ = d.load()
    for c in paths['chunks']:
        assert list(map(F, c['effective_width_xy_pt'])) == [3*F(x) for x in c['scale']]
        assert max(map(F, c['effective_width_xy_pt']))/2 < 1
        assert c['line_caps'] == [0,0,0] and c['line_join'] == 1
    assert max(abs(F(t['residual_pt'])) for t in paths['ticks']) < F('.044')
    assert max(p['transform_check_max_pt'] for p in paths['paintings']) < .0002
    for a in paths['axes']:
        for x,y,op,px,py in a['vertices']:
            assert tuple(map(F, (px,py))) == tuple(map(F, transform(
                x,y,a['scale'],a['translation'],a['local_translation'],paths['page_height_pt'])))
    for t in paths['ticks']:
        a=next(a for a in paths['axes'] if a['drawing_index']==t['drawing_index'])
        assert F(t['coordinate_pt'])==F(a['vertices'][0][3 if t['axis']=='force' else 4])


def test_duplicate_paintings_and_legends_are_not_samples():
    _, paths, _, traces = d.load()
    assert len(traces) == 12
    assert len(paths['paintings']) == 156  # 152 curve paintings + 4 legends
    assert len([c for c in paths['chunks'] if c['role']=='curve']) == 76
    assert len(paths['joins']) == 64
    assert sorted(c for cc in paths['trace_chunks'].values() for c in cc)==[f'C{k:02}' for k in range(76)]
    assert len({p['raw_path_sha256'] for p in paths['paintings'][:76]}) == 76
    assert sum(p['duplicate_of'] is not None for p in paths['paintings']) == 76
    assert all(len([s for s in traces if s[0]==g]) == 3 for g in 'BCDE')
    for i in range(76):
        a,b=paths['paintings'][i],paths['paintings'][i+76]
        assert a['raw_path_sha256']==b['raw_path_sha256'] and b['duplicate_of']==i
    assert all(c['trace'] is None for c in paths['chunks'] if c['role']=='legend_excluded')


def test_inverse_keeps_three_crossings_and_complete_hull():
    ss=segments([(0,0),(10,10),(20,0),(30,10)])
    r=d.read_trace(ss,5,axis(),axis(),1)
    assert r['status']=='AMBIGUOUS' and r['reason']=='MULTIPLE_INTERSECTIONS'
    assert r['nominal_crossings_pt']==[(5,5),(15,15),(25,25)]
    assert r['output_set']==[(5,5),(15,15),(25,25)] and r['bounds']==(5,25)


def test_plateau_is_complete_multivalued_inverse():
    r=d.read_trace(segments([(0,0),(10,5),(20,5),(30,10)]),5,axis(),axis(),1)
    assert r['status']=='AMBIGUOUS' and r['bounds']==(10,20)


def test_full_horizontal_and_vertical_query_support_required():
    ss=segments([(0,0),(10,20)])
    for coordinate,target in [(0,1),(1,1)]:
        r=d.read_trace(ss,target,axis(1,1),axis(),coordinate)
        assert r['nominal_support'] and not r['full_support']
        assert r['bounds'] is None and r['reason']=='QUERY_EXCEEDS_RECORDED_ENDPOINT'
    assert d.read_trace(ss,5,axis(1,1),axis(),0)['full_support']


def test_gaps_and_short_curves_cannot_extrapolate():
    ss=segments([(0,0),(4,4)])+segments([(6,6),(10,10)])
    r=d.read_trace(ss,5,axis(),axis(),0)
    assert r['reason']=='QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP'
    r=d.read_trace(ss,4,axis(1,1),axis(),0)
    assert r['nominal_support'] and not r['full_support']
    assert not d.read_trace(ss,11,axis(),axis(),0)['full_support']
    assert not d.read_trace(segments([(3,3),(4,4)]),F('3.5'),axis(1,1),axis(),0)['full_support']


def test_uncertainty_strip_retains_interior_extrema_and_branches():
    ss=segments([(0,0),(5,10),(10,0)])
    r=d.read_trace(ss,5,axis(0,2),axis(),0)
    assert r['bounds']==(6,10)
    inv=d.read_trace(ss,9,axis(0,1),axis(),1)
    assert inv['bounds']==(4,6)
    # Two strips disconnected in path order stay ambiguous even if output guards merge.
    inv=d.read_trace(ss,5,axis(0,1),axis(0,10),1)
    assert inv['status']=='AMBIGUOUS' and len(inv['output_set'])==1


def test_shared_calibration_cartesian_outer_enclosure():
    a=axis(1,1,True)
    for target in [F(0),F(35),F(100)]:
        q=a.query(target)
        for p0,p1,delta in product([F(99),F(100),F(101)],[F(-1),F(0),F(1)],[-1,0,1]):
            x=(1-target/100)*p0+target/100*p1+delta
            assert q[0]<=x<=q[1]
    lo,hi=a.output((F(30),F(40)))
    for p0,p1,p in product([F(99),F(100),F(101)],[F(-1),F(0),F(1)],range(29,42)):
        assert lo<=100*(p-p0)/(p1-p0)<=hi


def test_within_sample_subtraction_precedes_grind_aggregation():
    before=[reading([0,1]),reading([100,101]),reading([200,201])]
    after=[reading([10,11]),reading([110,111]),reading([210,211])]
    rr={f'B{i+1}':d.increment(a,b) for i,(a,b) in enumerate(zip(before,after))}
    e=d.envelope(rr,['B1','B2','B3'])
    assert e['bounds']==(9,11)
    assert d.subtract((10,211),(0,201))==(-191,211)  # wrong aggregate-first operation


def test_missing_sample_makes_envelope_incomplete_and_cannot_separate():
    rr={'B1':reading([1,2]),'B2':reading([2,3])}
    a=d.envelope(rr,['B1','B2','B3']); b=d.envelope({'E1':reading([100,200])},['E1'])
    assert a['completeness']=='INCOMPLETE' and a['missing']==['B3']
    assert d.compare(a,b)['classification']=='UNSUPPORTED_OR_INCOMPLETE'
    rr['B3']=reading(None,'UNSUPPORTED')
    assert d.envelope(rr,['B1','B2','B3'])['completeness']=='INCOMPLETE'


def test_all_crossing_hull_can_qualify_but_ambiguity_is_retained():
    rr={s:reading([1,3],'AMBIGUOUS') for s in ['B1','B2','B3']}
    e=d.envelope(rr,list(rr))
    assert e['completeness']=='COMPLETE' and e['ambiguous']==list(rr)
    assert d.increment(rr['B1'],reading([2,4]))['status']=='AMBIGUOUS'


def test_interval_subtraction_encloses_every_endpoint_combination_and_keeps_sign():
    before,after=(F(-2),F(5)),(F(1),F(4))
    lo,hi=d.subtract(after,before)
    for a,b in product(range(1,5),range(-2,6)):
        assert lo<=a-b<=hi
    assert (lo,hi)==(-4,6)
    assert d.increment(reading([10,20]),reading([1,2]))['bounds']==(-19,-8)


def test_force_offsets_cancel_in_increments():
    a,b=(F(2),F(3)),(F(10),F(13))
    for shift in [F(-1000),F(0),F(7,3),F(9000)]:
        assert d.subtract(tuple(x+shift for x in b),tuple(x+shift for x in a))==d.subtract(b,a)


def test_exact_classification_precedes_outward_rounding():
    a={'completeness':'COMPLETE','bounds':(F(0),F(1))}
    b={'completeness':'COMPLETE','bounds':(F(1)+F(1,10**9),F(2))}
    c=d.compare(a,b)
    assert c['classification']=='STRICTLY_SEPARATED' and c['sign']==1
    assert c['display'][0]=='0.000000' and c['minimum_gap']==F(1,10**9)
    assert d.outward((F(-1,10**9),F(-1,10**10)))==['-0.000001','0.000000']
    b['bounds']=(F(1),F(2))
    assert d.compare(a,b)['classification']=='NOT_EXCLUDED_BY_THIS_COMPARISON'


def test_null_exclusion_nonexclusion_and_unresolved_are_distinct():
    def r(x):return {'classification':x}
    a,b,c=map(r,['STRICTLY_SEPARATED','NOT_EXCLUDED_BY_THIS_COMPARISON','UNSUPPORTED_OR_INCOMPLETE'])
    assert d.null_disposition([b]*12)=='NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'
    assert d.null_disposition([b])=='UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'
    assert d.null_disposition([b,c])=='UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'
    assert d.null_disposition([a,c])=='EXCLUDED_BY_COMPLETE_INCREMENT_SEPARATION'


@pytest.fixture(scope='module')
def result():
    return d.analyze()


def test_full_request_accounting_and_actual_same_sample_arithmetic(result):
    assert [len(result[n]) for n in d.TABLES]==[60,72,24,8,12,156]
    assert len({r['request_id'] for r in result['support_accounting']})==156
    assert len(result['trace_support'])==12
    rr={r['request_id']:r for r in result['force_at_density']}
    for i in result['sample_force_increments']:
        before,after=[rr[k] for k in i['endpoints']]
        assert before['trace']==after['trace']==i['trace']
        assert i['bounds']==d.increment(before,after)['bounds']
    for c in result['cross_grind_comparisons']:
        if c['classification']=='STRICTLY_SEPARATED':
            assert c['difference'][0]>0 or c['difference'][1]<0
        assert len(c['descriptive_sample_pairs'])==9
    assert result['null_disposition']==d.null_disposition(result['cross_grind_comparisons'])


def test_source_generated_hashes_and_committed_tables_consistent(result):
    contract=json.loads((d.DATA/'contract.json').read_text())
    assert contract['plan_sha256']==hashlib.sha256((d.OUTPUT/'PLAN.md').read_bytes()).hexdigest()
    for name,digest in result['input_hashes'].items():
        assert hashlib.sha256((d.DATA/name).read_bytes()).hexdigest()==digest
    committed=json.loads((d.OUTPUT/'RESULT.json').read_text())
    assert committed['input_hashes']==result['input_hashes']
    assert committed['summary']==result['summary']
    for name in d.TABLES:
        rows=list(csv.DictReader((d.OUTPUT/(name+'.csv')).open()))
        assert len(rows)==len(result[name])
        for expected,actual in zip(result[name],rows):
            if 'status' in expected:assert expected['status']==actual['status']
            if 'bounds' in expected:assert json.dumps(expected['bounds'],default=d.serial,separators=(',',':'))==actual['bounds'] or (expected['bounds'] is None and actual['bounds']=='')


def test_dataset_registration_keeps_dry_observer_and_campaign_scope():
    from puckworks.data import rc17_fig6_2_dry_compaction
    rows=rc17_fig6_2_dry_compaction()
    assert len(rows)==17971 and sum(not r['trace'] for r in rows)==8
    register=json.loads((d.ROOT/'puckworks/data/AVAILABLE_DATA_REGISTER.json').read_text())
    family=next(f for f in register['families'] if f['family_id']=='ROMANCORROCHANO2017')
    scope=family['dataset_scopes']['romancorrochano2017/fig6_2_dry_compaction']
    assert scope['physical_validation']=='NOT_ESTABLISHED'
    assert scope['source_internal_or_external']=='SOURCE_INTERNAL'
    assert 'no new independent campaign' in scope['campaign']


def test_offline_producer_reproduces_all_numerical_artifacts(tmp_path,monkeypatch):
    # Deny network in-process; routine producer needs only compact retained inputs.
    import socket
    def denied(*args,**kwargs):raise AssertionError('Network forbidden')
    monkeypatch.setattr(socket,'socket',denied)
    d.produce(tmp_path)
    for name in [n+'.csv' for n in d.TABLES]+['RESULT.json']:
        assert (tmp_path/name).read_bytes()==(d.OUTPUT/name).read_bytes()


def test_offline_cli_works_without_pdf_reader(tmp_path):
    script="""
import sys
sys.modules['pymupdf']=None
sys.modules['fitz']=None
from puckworks.analysis.corrochano2017_dry_compaction import main
main()
"""
    subprocess.run([sys.executable,'-c',script,'--output',str(tmp_path)],check=True)
    assert (tmp_path/'RESULT.json').read_bytes()==(d.OUTPUT/'RESULT.json').read_bytes()


def test_plot_replay_is_deterministic_and_complete(result,tmp_path):
    pytest.importorskip('matplotlib')
    a,b=tmp_path/'a.svg',tmp_path/'b.svg'
    d.plot(result,a);d.plot(result,b)
    assert a.read_bytes()==b.read_bytes()
    text=a.read_text()
    assert 'PHYSICAL_VALIDATION=NOT_ESTABLISHED' in text
    assert 'All 156 requests' in text and '480→500' in text and '500→520' in text

"""Focused scientific contracts; source graphical compatibility is not validation."""
from fractions import Fraction as Q
import json
import subprocess
import sys

import numpy as np
import pytest

from puckworks.analysis import hargarten2020_swelling_kinetics as k


def point(t, lo, hi=None, tid='a', name=None, width=0):
    t=Q(str(t));lo=Q(str(lo));hi=lo if hi is None else Q(str(hi))
    return dict(t=t,t_lo=t-Q(str(width)),t_hi=t+Q(str(width)),L=lo,U=hi,
                outer_L=lo,outer_U=hi,trace_id=tid,observation_id=name or f'{tid}:{t}')


def trace(tid='a',d=600):
    return dict(trace_id=tid,diameter_um=d)


def test_source_schema_and_ids():
    c,ts,obs=k.read_inputs()
    assert len(ts)==17 and len({t['trace_id'] for t in ts})==17
    assert len({o['observation_id'] for o in obs})==len(obs)
    required={'doi','source_sha256','panel_id','trace_id','marker_id','roast','protocol',
              'diameter_um','x_px','y_px','reading_layer','support_status','notes','units'}
    assert all(required<=o.keys() for o in obs)
    assert all(o['doi']==c['source']['doi'] for o in obs)
    assert any(o['support_status']=='definition_only' for o in obs)


def test_source_times_not_snapped_and_figures_not_replicates():
    _,_,obs=k.read_inputs()
    primary=[o for o in obs if o['figure']==10 and o['support_status']=='supported']
    assert any(o['t'].denominator>1 for o in primary)
    assert next(o for o in primary if o['observation_id']=='f10a-edge-914')['t']<300
    assert all(o['t']<=300 for o in primary)
    assert {o['trace_id'] for o in primary} <= {o['trace_id'] for o in obs if o['figure']==7}
    assert len({o['marker_id'] for o in primary})==len(primary)
    assert any(o['value']>1 for o in primary)


def test_si_radius_conversion():
    assert k.radius_m(608)==Q(304,1_000_000)
    with pytest.raises(ValueError):k.radius_m(0)


def test_negative_decreasing_and_overshoot_not_clipped():
    obs=[point(10,-.2),point(20,1.4),point(30,.4)]
    b=k.baseline(obs)
    assert b['B']==Q('.5')
    assert obs[0]['L']==Q('-.2') and obs[1]['L']==Q('1.4')


def test_exact_baseline_order_endpoints_and_repeated_times():
    obs=[point(10,.8,.9,name='early'),point(20,.2,.3,name='late')]
    b=k.baseline(obs);assert b['B']==Q('.25')
    assert b['decisive']==['early','late']
    assert all(k.distance(w['p'],o['L'],o['U'])<=b['B'] for o,w in zip(obs,b['witness']))
    assert k.baseline([point(0,.3)])['B']==Q('.3')
    assert k.baseline([point(1200,.5)])['B']==Q('.5')
    assert k.baseline([point(10,.8,name='x'),point(10,.2,name='y')])['B']==Q('.3')


def test_baseline_known_lp_optimum():
    import warnings
    from scipy.optimize import OptimizeWarning, linprog
    obs=[point(2,.4,.5),point(7,.1,.2),point(8,1.2,1.3),point(9,.9,1.0)]
    n=len(obs);a=[];b=[]
    for j,o in enumerate(obs):
        r=[0.]*(n+1);r[j]=1;r[-1]=-1;a.append(r);b.append(float(o['U']))
        r=[0.]*(n+1);r[j]=-1;r[-1]=-1;a.append(r);b.append(-float(o['L']))
    for j in range(n-1):
        r=[0.]*(n+1);r[j]=1;r[j+1]=-1;a.append(r);b.append(0.)
    # Match existing LPs: HiGHS retains its scheduler process-wide.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore', message='Unrecognized options detected.*', category=OptimizeWarning)
        sol=linprog([0.]*n+[1.],A_ub=a,b_ub=b,bounds=[(0,1)]*n+[(0,None)],
                    method='highs',options={'threads':1})
    assert sol.success and abs(sol.fun-float(k.baseline(obs)['B']))<1e-10


def test_compatible_finite_reference_denominators():
    trs=[trace('a',400),trace('b',800)];obs=[]
    # H(s)=s/(s+1e10); each denominator is different and never dropped.
    H=lambda s:s/(s+Q(10_000_000_000))
    for tr in trs:
        r=k.radius_m(tr['diameter_um'])
        for t in [10,40,100,300]:
            p=H(Q(t)/r**2)/H(k.T/r**2)
            obs.append(point(t,p,tid=tr['trace_id']))
    fit=k.shared(obs,trs,Q(0));assert fit['epsilon_upper']==0
    # Same scaled time40/a and160/b has different normalized progress.
    r1=k.radius_m(400);r2=k.radius_m(800)
    p1=H(Q(40)/r1**2)/H(k.T/r1**2);p2=H(Q(160)/r2**2)/H(k.T/r2**2)
    assert p1!=p2
    assert k.feasible(k.graph_constraints([point(40,p1,tid='a'),point(160,p2,tid='b')],trs,0))['feasible']


def test_incompatible_positive_certified_margin():
    obs=[point(10,.9,tid='a'),point(10,.1,tid='b')]
    fit=k.shared(obs,[trace('a'),trace('b')],Q(0))
    assert fit['epsilon_lower']>Q('.39')
    assert fit['lower_certificate']['kind']=='positive_cycle'
    assert fit['lower_certificate']['product']>1
    assert fit['delta_lower']>=0


def test_exact_ties_and_near_ties_not_merged():
    obs=[point(10,.5,tid='a'),point(10,.5,tid='b')];trs=[trace('a'),trace('b')]
    g=k.graph_constraints(obs,trs,0)
    assert g['observations']['a:10']==g['observations']['b:10']
    obs[1]=point('10.000000000000000001',.5,tid='b')
    g=k.graph_constraints(obs,trs,0)
    assert len(set(g['observations'].values()))==2


def test_zero_denominator_and_scale_protections():
    # All-zero h would falsely satisfy these contradictory ratios.
    obs=[point(10,.9,tid='a'),point(10,.1,tid='b')];trs=[trace('a'),trace('b')]
    assert not k.feasible(k.graph_constraints(obs,trs,0))['feasible']
    zero=k.feasible(k.graph_constraints([point(10,0)], [trace()],0))
    assert zero['feasible'] and max(zero['h'])>=1
    assert not k.feasible(k.graph_constraints([point(1200,0)], [trace()],0))['feasible']
    assert not k.feasible(k.graph_constraints([point(0,.2)], [trace()],0))['feasible']


def test_uncertain_times_outer_never_joint_proof():
    obs=[point(10,.9,width=5),point(12,.1,width=5)]
    assert k.baseline(obs)['B']==Q('.4')
    assert k.baseline(obs,True)['B']==0
    fit=k.shared(obs,[trace()],Q(0),True)
    assert fit['disposition']=='NONEMPTY_OUTER_FEASIBLE_SET_ONLY'
    assert fit['source_joint_disposition'].startswith('UNRESOLVED')


def test_incomplete_support_honest():
    assert k.baseline([])['B'] is None
    assert k.shared([],[],Q(0))['disposition']=='INSUFFICIENT_SOURCE_SUPPORT'
    assert k.shared([point(10,.2)],[trace(),trace('b')],Q(0))['disposition']=='INSUFFICIENT_SOURCE_SUPPORT'


def test_mo_fixed_parameters_order_repeats_near_zero_reference():
    times=[1200,10,0,10,1e-10,30]
    p,d=k.mo_prediction(608,times,60)
    assert p[0]==1 and p[1]==p[3] and np.isfinite(p).all()
    assert 0<p[2]<=p[4]<p[1]<p[-1]<1
    assert d['D_W']==1.25e-10 and d['C_M']==.1
    assert d['solver']['success'] and d['solver']['rtol']==1e-7
    assert d['endpoint_disposition']=='RAW_FINITE_GRID_INITIAL_ENDPOINT_DEFECT'
    assert d['initial_volume']>1 and d['physical_bound_excess']>0


def test_mo_resolution_and_tolerance():
    a,da=k.mo_prediction(608,[10,30,240],60)
    b,db=k.mo_prediction(608,[10,30,240],120)
    c,dc=k.mo_prediction(608,[10,30,240],240)
    assert np.max(abs(c-b))<np.max(abs(b-a))
    assert dc['initial_progress_pp']<db['initial_progress_pp']<da['initial_progress_pp']
    assert np.max(abs(c-b))*100<.04  # This named particle/time support only.


def test_retained_certificate_deltas_and_tamper(tmp_path):
    bundle=k.DEFAULT_OUTPUT
    if not (bundle/'certificates.json').exists():pytest.skip('derived bundle not yet produced')
    checker=bundle/'review_check.py'
    assert checker.exists()
    subprocess.run([sys.executable,str(checker),'--output',str(bundle)],check=True,capture_output=True)
    import shutil
    for f in bundle.iterdir():
        if f.is_file():
            shutil.copy(f,tmp_path/f.name)
    p=tmp_path/'groups.json';gs=json.loads(p.read_text());gs[0]['delta_lower']='-1';p.write_text(json.dumps(gs))
    bad=subprocess.run([sys.executable,str(checker),'--output',str(tmp_path)],capture_output=True)
    assert bad.returncode!=0
    assert b'group penalty summary' in bad.stderr


def test_shared_witness_satisfies_all_exact_inequalities():
    obs=[point(10,.2,.3,tid='a'),point(30,.4,.5,tid='a'),point(10,.3,.4,tid='b')]
    result=k.shared(obs,[trace('a',500),trace('b',700)],Q(0))
    assert result['disposition']=='CONSTRUCTED_COMPATIBLE_WITNESS'
    g=result['upper_graph'];h=result['upper_witness']['h']
    assert all(h[v]>=a*h[u] for u,v,a,_ in g['edges'])
    assert all(h[i]>=1 for i in g['references'].values())
    assert all(h[i]==0 for i in g['zero_nodes'])


def test_invalid_solver_and_numerical_ambiguity_are_not_exclusion(monkeypatch):
    monkeypatch.setattr(k,'feasible',lambda g:dict(feasible=None))
    assert k.shared([point(10,.2)],[trace()],Q(0))['disposition']=='NUMERICALLY_UNRESOLVED'
    monkeypatch.setattr(k.swelling,'D_W',1e-9)
    with pytest.raises(ValueError,match='frozen'):k.mo_prediction(608,[10])


def test_interpolation_is_explicit_and_no_extrapolation():
    obs=[point(10,.2),point(40,.8)]
    assert k.at_time(obs,Q(30))['status']=='CONDITIONAL_LINEAR_INTERPOLATION_NOT_MEASURED'
    assert k.at_time(obs,Q(240))['status']=='INSUFFICIENT_SOURCE_SUPPORT'
    assert k.at_time(obs,Q(10))['status']=='direct_native'


@pytest.mark.slow
def test_deterministic_offline_regeneration(tmp_path, monkeypatch):
    import socket
    def denied(*a, **kw):
        raise AssertionError('network forbidden during offline reproduction')
    monkeypatch.setattr(socket,'create_connection',denied)
    monkeypatch.setattr(socket.socket,'connect',denied)
    monkeypatch.setitem(sys.modules,'fitz',None)
    monkeypatch.setitem(sys.modules,'pymupdf',None)
    a=tmp_path/'a';b=tmp_path/'b'
    k.produce(a);k.produce(b)
    assert {p.name:p.read_bytes() for p in a.iterdir()}=={p.name:p.read_bytes() for p in b.iterdir()}

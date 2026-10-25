"""Contract tests: exact authority plus independent LP and operator checks."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as Q
import json
import math
from pathlib import Path

import numpy as np
import pytest
from scipy.integrate import quad
from scipy.optimize import linprog

from puckworks.analysis import matias2023_caffeine_fraction_shape as m


def lp(x,bands):
    # Separately stated epigraph LP in alpha,beta,epsilon; no pair elimination.
    A=[];b=[]
    for t,(l,u) in zip(x,bands):
        A.extend([[1,t,-1],[-1,-t,-1]])
        b.extend([float(u),-float(l)])
    r=linprog([0,0,1],A_ub=A,b_ub=b,bounds=[(None,None),(None,0),(0,None)],method='highs')
    assert r.success
    return r.fun


def solve(z):
    return m.exact_minimax(range(len(z)),[(v,v) for v in z])


@pytest.mark.parametrize('z',[[4,3,2,1],[Q(7,3)]*10,[2,1,Q(1,2),0],[0,1,2],[3,2,4,0],[0,0,1]])
def test_independent_lp(z):
    r=solve(z)
    assert float(Q(r['epsilon']))==pytest.approx(lp(range(len(z)),[(v,v) for v in z]),abs=1e-11)


def test_geometric_constant_and_increasing_boundary():
    assert Q(solve([4,3,2,1])['epsilon'])==0
    assert Q(solve([2]*10)['epsilon'])==0
    r=solve([0,1,2]);assert Q(r['epsilon'])==1 and Q(r['beta'])==0
    assert 'NONINCREASING:1,3' in r['attaining_constraints']


def test_independent_lower_bound_and_witness():
    r=solve([3,2,Q(3,2)])
    # Curvature z0-2*z1+z2=1/2; line curvature zero; coefficient L1 norm=4.
    # Hence e>=1/8, independently of the producer's pair formula.
    assert Q(r['epsilon'])==Q(1,8)
    assert r['predicted_log']==['23/8','17/8','11/8']
    assert list(map(Q,r['interval_distance']))==[-Q(1,8),Q(1,8),-Q(1,8)]


def test_full_ordered_cartesian_and_interior_excursion():
    r=solve([3,2,1,0,0,0,0,0,0,0])
    assert r['pair_count']==45 and r['ordered_pair_pair_count']==2025
    r=solve([4,3,4,1,0]);assert Q(r['epsilon'])==1
    assert len(r['attaining_constraints'])>=1


def test_shift_and_widening():
    z=[Q(13,4),Q(7,3),Q(8,5),Q(9,7)]
    r=solve(z);s=solve([v+Q(123,17) for v in z])
    assert r['epsilon']==s['epsilon']
    assert m.multiplicative_enclosure(r['epsilon'])==m.multiplicative_enclosure(s['epsilon'])
    bands=[(v-Q(1,10),v+Q(1,5)) for v in z]
    w=m.exact_minimax(range(4),bands)
    assert Q(w['epsilon'])<=Q(r['epsilon'])
    assert float(Q(w['epsilon']))==pytest.approx(lp(range(4),bands))


def test_zero_certificate_can_be_only_nonnegativity():
    r=m.exact_minimax([0,1,2],[(0,10)]*3)
    assert r['epsilon']=='0' and r['attaining_constraints']==['NONNEGATIVITY']


@pytest.mark.parametrize('x,bounds', [([0,0],[(0,1)]*2),([1,0],[(0,1)]*2),
                                     ([0,1],[(2,1),(0,1)]),([0,1],[(0,1),(0,'nan')]),
                                     ([],[]),([0,1],[(0,1)])])
def test_invalid_contracts(x,bounds):
    with pytest.raises(ValueError):m.exact_minimax(x,bounds)


@pytest.mark.parametrize('value',[0,-1,float('nan'),float('inf')])
def test_no_nonpositive_or_nonfinite_log_clipping(value):
    with pytest.raises(ValueError):m.positive_log(value)


@pytest.mark.parametrize('k',[0,1e-12,.01,.3])
def test_finite_bin_integral(k):
    A=2345.;width=5.
    B=m.finite_bin_mean(A,k,0,width)
    for i in range(10):
        observed=m.finite_bin_mean(A,k,i*width,width)
        integral=quad(lambda v:A*math.exp(-k*v),i*width,(i+1)*width)[0]/width
        assert observed==pytest.approx(integral,rel=2e-14)
        assert observed==pytest.approx(B*math.exp(-k*width*i),rel=2e-14)


def test_aggregation_limitation_without_source_mixture_fit():
    x=np.arange(10)
    c=(100*np.exp(-.1*x)+100*np.exp(-.7*x))/2
    z=np.log10(c)
    assert np.all(np.diff(z)<0) and np.all(np.diff(z,2)>0)
    assert Q(solve([str(v) for v in z])['epsilon'])>0
    # Positive mixtures obey structure; arbitrary curvature is not explained.
    assert np.diff([3,2,0],2)[0]<0


def test_source_support_statuses_and_incomplete_cohort():
    geometry=json.loads((m.DATA/'figure_geometry.json').read_text())
    r=m.build_report(geometry)
    assert r['coverage']==dict(slots=10,centers=10,vertical_lower_endpoints=10,vertical_upper_endpoints=10,horizontal_segments=10)
    assert all(o['L_status']=='COVERED_BUT_RECOVERED' for o in r['observations'][:6])
    assert r['observations'][-1]['center_status']=='CLIPPED_BUT_RECOVERED'
    assert r['observations'][-1]['horizontal_status']=='CLIPPED_BUT_RECOVERED'
    partial=deepcopy(geometry);partial['observations'][4]['marker_rectangle_tokens']=None
    partial['observations'][6]['vertical_tokens']=None
    partial['observations'][9]['horizontal_tokens']=None
    p=m.build_report(partial)
    assert [o['x'] for o in p['observations']]==list(range(10))
    assert p['coverage']['centers']==9 and p['coverage']['horizontal_segments']==9
    assert p['observations'][6]['L_status']=='UNSUPPORTED'
    assert p['layers']['N']['support_status']=='SUBSET_LOWER_BOUND_ONLY'
    assert p['layers']['P_outer']['supported_count']==9
    assert p['observations'][4]['center_reason']=='marker geometry absent'


def test_all_source_witnesses_direct_intersection_and_residuals():
    r=m.build_report()
    for name,c in r['layers'].items():
        a,b,e=map(Q,(c['alpha'],c['beta'],c['epsilon']))
        assert b<=0
        rr=[v for v in r['witness_residuals'] if v['layer']==name]
        lows=[];highs=[];dist=[]
        for i,v in enumerate(rr):
            l,u=map(Q,(v['interval_lower_log'],v['interval_upper_log']))
            y=a+b*i;near=max(l,min(y,u))
            assert str(y)==v['predicted_log'] and str(near)==v['nearest_permitted_log']
            assert str(y-near)==v['interval_distance_log']
            lows.append(l-e-b*i);highs.append(u+e-b*i);dist.append(abs(y-near))
        assert max(lows)<=a<=min(highs) and max(dist)==e
    assert len(r['diagnostics'])==17
    assert Q(r['layers']['G']['epsilon'])<=Q(r['layers']['N']['epsilon'])
    assert 0<Q(r['layers']['P_outer']['epsilon'])<=Q(r['layers']['P_inner']['epsilon'])


def test_endpoint_quantifiers_and_empty_inner():
    g=json.loads((m.DATA/'figure_geometry.json').read_text())
    # Tiny synthetic extents have overlapping endpoint-reading uncertainty.
    g['observations'][0]['vertical_tokens'][1]='26.970'
    g['observations'][0]['vertical_tokens'][3]='26.968'
    r=m.build_report(g)
    assert r['layers']['P_inner']['support_status']=='INNER_UNAVAILABLE'
    assert r['layers']['P_outer']['epsilon'] is not None
    # Distinguish outer compatibility from a universal envelope witness.
    outer=[(-1,1),(-1,1),(-1,1)]
    inner=[(0,0),(1,1),(0,0)]
    assert m.exact_minimax(range(3),outer)['epsilon']=='0'
    assert Q(m.exact_minimax(range(3),inner)['epsilon'])>0


def test_enclosed_transform_against_independent_integer_power():
    # For rational exponent 1/3, enclosure can be checked without logs/exp.
    b=m.multiplicative_enclosure(Q(1,3))
    assert Q(b['M_lower'])**3<10<Q(b['M_upper'])**3
    assert Q(b['ratio_lower_lower'])**3<Q(1,10)<Q(b['ratio_lower_upper'])**3
    assert m.multiplicative_enclosure(0)['ratio_envelope_outer']==['1','1']
    with localcontext() as ctx:
        ctx.prec=100
        for c in m.build_report()['layers'].values():
            e=Q(c['epsilon']); exactish=(Decimal(e.numerator)/Decimal(e.denominator)*Decimal(10).ln()).exp()
            b=c['multiplicative']
            assert Decimal(b['M_lower'])<exactish<Decimal(b['M_upper'])


def test_deterministic_offline_and_committed_outputs(tmp_path):
    a=tmp_path/'a';b=tmp_path/'b';m.write_report(a);m.write_report(b)
    for f in a.iterdir():assert f.read_bytes()==(b/f.name).read_bytes()
    bundle=Path(__file__).resolve().parents[1]/'docs/analysis/sci_md_matias_caffeine_fraction_shape_001'
    if (bundle/'results.json').exists():
        for name in ('results.json','observations.csv','diagnostics.csv','witness_residuals.csv','certificates.csv','RESULT.md'):
            assert (a/name).read_bytes()==(bundle/name).read_bytes()

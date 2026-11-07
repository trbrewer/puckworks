"""Focused bookkeeping checks; mounted frozen-source checks run in the CLI."""
import numpy as np
import pytest
from scipy.stats import spearmanr

from puckworks.analysis import mass_fade_diagnostics_001 as D


def test_fixed_grid_and_adapter():
    assert D.GRID == (0,.0025,.005,.01,.015,.02,.025,.03,.035,.04,.05,.06,.08,.10,.13,.17,.25,.40)
    p = [1.,24.,2.,3.,.00123456789,13.]
    q = D.gamma_vector(p,28.,.13)
    assert q[:4] == p[:4] and q[-1] == p[-1] and q[4] == .13/28
    assert p[4] == .00123456789
    assert D.gamma_vector(p,31.,.13)[4] != q[4]


@pytest.mark.parametrize('mc,x',[(0,.03),(-1,.03),(28,-.01),(1,.4),(28,float('nan'))])
def test_adapter_rejects_invalid(mc,x):
    with pytest.raises(ValueError):
        D.gamma_vector([1,24,2,3,0,13],mc,x)


@pytest.mark.parametrize('y,shape',[
    ([3,2,1,2,3],'interior_minimum'),
    ([1,1,2,3,4],'monotone_toward_smaller_gamma'),
    ([4,3,2,1,1],'monotone_toward_larger_gamma'),
    ([1,1,1,1,1],'flat_exactly'),
    ([2,1,3,1,2],'nonmonotone'),
    ([3,2,2,3,4],'interior_minimum'),
])
def test_shape_and_exact_ties(y,shape):
    r=D.slice_shape(np.arange(5),y)
    assert r['shape']==shape
    assert r['grid_min_products']==np.flatnonzero(np.array(y)==min(y)).tolist()
    assert r['objective_span']==max(y)-min(y)


def test_tiny_nonzero_change_is_not_labeled_flat():
    r=D.slice_shape([0,1,2],[1,1+1e-12,1+2e-12])
    assert r['shape']=='monotone_toward_smaller_gamma'


def test_rank_ties_and_paired_bootstrap():
    x=np.array([[1,1,3,4],[4,2,2,1.]])
    y=np.array([[2,1,4,3],[1,3,2,4.]])
    np.testing.assert_allclose(D.spearman(x,y),[spearmanr(a,b).statistic for a,b in zip(x,y)],rtol=1e-15)
    assert np.isnan(D.spearman(np.ones(11),np.arange(11)))


def test_recorded_mass_baseline_support_and_offset_invariance():
    t=np.array([-3.,-2.,-1.,0.,20.,59.,61.,99.,101.,102.])
    m=np.array([8.,10.,12.,14.,20.,60.,64.,120.,124.,-100.])
    ct=t[3:-1]
    values,baseline,native=D.scale_mass(t,m,ct)
    assert baseline==12
    np.testing.assert_array_equal(values,[50,110])
    np.testing.assert_array_equal(native,m[3:-1]-12)
    shifted,_,_=D.scale_mass(t,m+777,ct)
    np.testing.assert_array_equal(shifted,values)
    with pytest.raises(ValueError,match='outside retained'):
        D.scale_mass(t,m,ct,targets=[102])
    with pytest.raises(ValueError,match='native raw subset'):
        D.scale_mass(t,m,[0.,60.,101.])


def test_mass_baseline_fallback_only_without_baseline_samples():
    values,baseline,_=D.scale_mass([1,60,100],[8,18,28],[1,60,100])
    assert baseline==8
    np.testing.assert_array_equal(values,[10,20])


def test_selected_evaluation_preserves_exact_gamma(monkeypatch):
    from types import SimpleNamespace
    p=[1.,24.,2.,3.,.0012345678912345679,13.]
    fit=dict(arm='A_J1_F',fold='test',parameters=p,mc_fixed_g=28.123,held_condition_bar=None)
    calls=[]
    def objective(data,parameters,held,dt):
        calls.append((parameters,held,dt))
        return dict(objective=1.,parameters=list(parameters))
    monkeypatch.setattr(D,'_R',SimpleNamespace(F=SimpleNamespace(objective=objective)))
    D.evaluate((fit,None,'selected'))
    assert calls[0][0] is p and calls[0][2]==.02
    D.evaluate((fit,.03,'grid'))
    assert calls[1][0][4]==.03/28.123
    assert calls[1][0][:4]==p[:4] and calls[1][0][-1]==p[-1]

"""Leakage, units and multiplicity tests for the research-only pressure observer."""
import copy

import numpy as np
import pytest
from scipy.optimize._numdiff import approx_derivative

from puckworks.analysis import gagne_conditional_pressure as m


def channels():
    t=np.r_[41.,42.1,43.,44.2,46.8,47.1,50.2,57.6,66.,74.9,76.]
    out={}
    for i in range(4):
        q=1.5+.1*np.sin(t/3+i)
        out[str(i)]=dict(espresso_elapsed=t,espresso_flow=q,
            espresso_temperature_basket=92+.2*np.cos(t),
            espresso_pressure=q*(2.5-i*.1)*np.exp(-(t-42)/(65+i)))
    return out


def test_units_native_quadrature_and_volume():
    ch=channels()
    for c in ch.values():
        c['espresso_flow']=np.full(len(c['espresso_elapsed']),2.)
        c['espresso_temperature_basket']=np.full(len(c['espresso_elapsed']),92.)
    s=m.prepare(ch)
    np.testing.assert_allclose(s.temperature,365.15)
    np.testing.assert_allclose(s.volume,2*(s.t-42))
    np.testing.assert_allclose(s.span,66.)
    np.testing.assert_allclose(s.wa.sum(axis=1),1.)
    np.testing.assert_allclose(s.we.sum(axis=1),1.)
    np.testing.assert_allclose(m.response(s,'W',None)[0],1.)
    for drift in [-.2,.2]:
        z=m.prepare(ch,drift)
        np.testing.assert_allclose(z.span,66*(1+drift/2))
        np.testing.assert_allclose(z.volume,2*((s.t-42)+drift*(s.t-42)**2/66))


def test_all_copies_excluded_and_multiplicity_retained():
    s=m.prepare(channels()); counts=np.array([3,0,1,7]);w=m.training_counts(counts,0)
    assert w.tolist()==[0,0,1,7]
    np.testing.assert_array_equal(counts,[3,0,1,7])
    obj=m.Objective(s,w,'V')
    assert obj.shots.ids==('2','3')
    np.testing.assert_allclose(obj.weights,[1/8,7/8])
    u=np.array([.2,.4]); theta=obj.low+(obj.high-obj.low)*u
    expected=m.per_shot_mse(s,m.predict(s,'V',theta)[0])
    assert obj(u)[0]==pytest.approx((expected[2]+7*expected[3])/8)
    with pytest.raises(ValueError,match='Empty'):
        m.training_counts([4,0,0,0],0)


@pytest.mark.parametrize('arm',['V','B'])
def test_analytic_gradient(arm):
    s=m.prepare(channels());o=m.Objective(s,np.array([0,2,1,1]),arm)
    u=np.array([.3,.7]);f,g=o(u)
    np.testing.assert_allclose(g,approx_derivative(lambda x:o(x)[0],u),rtol=1e-6,atol=1e-8)


@pytest.mark.parametrize('arm',m.ARMS)
def test_suffix_pressure_replacement_leaves_held_predictions_unchanged(arm):
    original=channels(); changed=copy.deepcopy(original)
    t=changed['0']['espresso_elapsed']
    changed['0']['espresso_pressure'][t>=47]=1234.+t[t>=47]
    s=m.prepare(original);z=m.prepare(changed);w=m.training_counts([4,2,1,3],0)
    theta=None
    if arm in ['V','B']:
        # The shared optimization sees only selected training objects. The
        # screening loss identity is checked separately below.
        x=m.fit(s,w,arm,[.3,.4]);y=m.fit(z,w,arm,[.3,.4])
        np.testing.assert_array_equal(x['theta'],y['theta'])
        theta=x['theta']
    p=m.predict(s.subset([0]),arm,theta)[0]
    q=m.predict(z.subset([0]),arm,theta)[0]
    np.testing.assert_array_equal(p,q)
    # Selected training scalar objective identical across the entire rectangle.
    if arm in ['V','B']:
        for u in m.STARTS:
            assert m.Objective(s,w,arm)(np.array(u))[0]==m.Objective(z,w,arm)(np.array(u))[0]


def test_anchor_zero_flow_retained_and_secondary_finite():
    ch=channels();ch['0']['espresso_flow'][1:3]=0
    s=m.prepare(ch)
    assert s.na==4 and s.flow[0,0]==0
    p,amp=m.predict(s,'N')
    assert np.isfinite(amp).all()
    assert np.isfinite(m.shot_scores(s,p)['normalized_resistance_rmse']).all()


def test_independent_reduction_is_root_mean_square_not_mean_rmse():
    s=m.prepare(channels()); pred=s.pressure.copy()
    for i in range(4):pred[i,s.na:]+=i
    scores=m.shot_scores(s,pred)
    expected=np.sqrt((0+1+4+9)/4)
    assert m.independent_loss(s,pred)==pytest.approx(expected)
    assert np.sqrt(scores['mse'].mean())==pytest.approx(expected)
    assert scores['rmse'].mean()!=pytest.approx(expected)
    assert scores['bias'].tolist()==pytest.approx([0,1,2,3])


def test_bounds_use_only_training_multiplicity_and_fixed_midpoint():
    s=m.prepare(channels());s.span=np.array([1e10,20.,40.,80.]);w=np.array([0,1,4,1])
    lo,hi=m.bounds_for(s,w)
    np.testing.assert_allclose(np.exp([lo[1],hi[1]]),[4.,400.])
    fit=m.fit(s,w,'B',[0.,0.])
    assert fit['free_dimensions']==0
    np.testing.assert_allclose(fit['theta'],[(m.A_MIN+1)/2,np.log(40.)])
    assert len(fit['starts'])==9 and max(x['nfev'] for x in fit['starts'])<=200


def test_all_nine_classifications_and_zero_intersection():
    for l in [.075,.1,.125]:
        for u in [.1875,.25,.3125]:
            assert m.intersected_bands([-.01,.5],l,u)==['worse','small','moderate','large']
    assert m.intersected_bands([0,.1])==['small','moderate']
    assert m.band(0)=='small'


def test_zero_evaluation_flow_rejected_and_temperature_control_unchanged():
    ch=channels(); ch['0']['espresso_flow'][5]=0.
    with pytest.raises(ValueError,match='Invalid'):
        m.prepare(ch)
    s=m.prepare(channels())
    np.testing.assert_array_equal(m.predict(s,'W',use_temperature=False)[0],m.predict(s,'W')[0])


def test_optional_sobol_base_size_and_training_only_screen():
    pytest.importorskip('jaxgsa')
    s=m.prepare(channels()); screen=m.Screening(s)
    assert screen.design.base_n==512
    assert screen.design.n_expanded==2048
    assert len(screen.samples)==2048
    # Verify cached design losses against the independent training objective.
    weights=m.training_counts([3,2,1,4],0)
    lo,hi=m.bounds_for(s,weights)
    for arm in ['V','B']:
        y=sum(screen.losses(arm,lo,hi,i)*weights[i] for i in np.flatnonzero(weights))/weights.sum()
        obj=m.Objective(s,weights,arm)
        for k in [0,11,1023,2047]:
            assert y[k]==pytest.approx(obj(screen.samples[k])[0],rel=1e-12,abs=1e-12)
    assert all(k[-1]!=0 for k in screen.cache)

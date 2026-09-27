"""Public synthetic fixtures only; no source rows or observations."""
from dataclasses import replace
import json
import math

import pytest
from scipy.special import logit

from puckworks.analysis import conditional_caffeine_delivery as md


def constant(arm='S2', head=.1, tds=.05):
    p = md.parent.synthetic_model('C2')
    p = replace(p, theta=[[float(logit(tds)), 0, 0, 0, 0]]*5)
    m = md.synthetic_model(arm)
    return replace(m, theta=() if arm == 'S0' else [[float(logit(head))]+[0]*len(m.means)]*5,
                   share=head if arm == 'S0' else None,
                   parent_json=None if arm == 'D0' else md.canonical(p.to_dict()))


def state(m):
    return m.condition(md.EarlyInput(m.arm, (.004,.004,.15,.1)[:len(md.feature_names(m.arm))], 'SYNTHETIC'))


@pytest.mark.parametrize('arm', md.ARMS)
def test_units_additivity_zero_and_remaining(arm):
    s = state(constant(arm))
    ps = s.predict_intervals([.008,.02,.008,.03],[.02,.06,.06,.03])
    expected_q = .1 if arm == 'D0' else .005
    assert ps[2].caffeine_kg == pytest.approx(expected_q*.052, abs=1e-17)
    assert ps[2].caffeine_mg == pytest.approx(1e6*expected_q*.052)
    assert ps[2].caffeine_mg_g == pytest.approx(1000*expected_q)
    assert ps[0].caffeine_kg+ps[1].caffeine_kg == pytest.approx(ps[2].caffeine_kg, abs=1e-17)
    assert ps[3].caffeine_kg == ps[3].allowance_kg == 0 and ps[3].caffeine_mg_g is None
    assert s.remaining_caffeine(.06) == ps[2]
    assert all(p.numerical_qualified and p.allowance_kg <= 1e-9 for p in ps)


def test_product_not_product_of_averages_and_parent_immutable():
    m = md.synthetic_model('S1'); before = m.parent_json
    m = replace(m, theta=[[v,0,0] for v in (-4,-3,-2,-1,0)])
    s = state(m); a,b=.008,.06
    p = s.predict_intervals([a],[b])[0]
    head = md.parent.IntervalGeometry([a],[b],m.knot_domain_kg).integrate([s.logits])[0]/(b-a)
    tds = md.parent.predict_intervals(s.parent_state,[a],[b])[0].solute_kg/(b-a)
    assert abs(p.caffeine_kg/(b-a)-head*tds) > 1e-5
    assert before == m.parent_json
    assert 0 <= p.caffeine_kg <= (b-a)*tds
    assert p.difference_64_128_kg <= p.allowance_kg
    assert p.difference_adaptive_kg+p.reference_error_kg <= p.allowance_kg


@pytest.mark.parametrize('arm',md.ARMS)
def test_reload_hash_schema_state_and_order(tmp_path,arm):
    m=md.synthetic_model(arm); path=tmp_path/'m.json';m.save(path)
    r=md.Model.load(path);assert r.sha256==m.sha256
    s=state(r);copy=md.State.from_dict(s.to_dict())
    assert copy.predict_intervals([.008],[.04])==s.predict_intervals([.008],[.04])
    assert s.predict_intervals([.008,.04],[.04,.06])[0]==s.predict_intervals([.008],[.04])[0]
    altered=s.to_dict();altered['logits']=[0]*5
    with pytest.raises(ValueError):md.State.from_dict(altered)
    data=json.loads(path.read_text());data['model']['rights']='tampered';path.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='HASH'):md.Model.load(path)
    d=m.to_dict();d['units']['caffeine']='g'
    with pytest.raises(ValueError):md.Model.from_dict(d)
    d=m.to_dict();d['surprise']=1
    with pytest.raises(ValueError):md.Model.from_dict(d)


@pytest.mark.parametrize('a,b',[(.007,.02),(.02,.01),(.01,.081),(float('nan'),.02),(.01,float('inf'))])
def test_invalid_windows(a,b):
    with pytest.raises(ValueError):state(md.synthetic_model()).predict_intervals([a],[b])


def test_strict_boundary_inputs_unknown_features_and_extrapolation():
    s=state(md.synthetic_model())
    with pytest.raises(ValueError):s.predict_intervals([math.nextafter(.008,0)],[.02])
    for vals in [(0,.004,.1,.1),(.004,-1,.1,.1),(.004,.004,float('inf'),.1)]:
        with pytest.raises(ValueError):md.EarlyInput('S2',vals)
    with pytest.raises(ValueError):md.EarlyInput('S2',(.004,.004,.15,.1),mass_unit='g')
    d=s.inputs.to_dict();d['values']['caffeine']=.01
    with pytest.raises(ValueError):md.EarlyInput.from_dict(d)
    with pytest.raises(ValueError):s.predict_intervals([.008],[.02],mass_unit='g')
    x=s.model.condition(md.EarlyInput('S2',(.004,.009,.15,.1)))
    p=x.predict_intervals([.013],[.03])[0]
    assert 'm2_kg' in p.feature_extrapolation and p.support=='FEATURE_EXTRAPOLATION_DIAGNOSTIC'


def test_D0_has_no_TDS_or_parent_state():
    m=md.synthetic_model('D0');s=state(m)
    assert m.to_dict()['parent'] is None and s.to_dict()['parent_state'] is None
    assert set(s.to_dict()['inputs']['values'])=={'m1_kg','m2_kg'}
    with pytest.raises(ValueError):md.EarlyInput('D0',(.004,.004,.1,.1))
    with pytest.raises(ValueError):replace(m,parent_json=md.canonical(md.parent.synthetic_model().to_dict()))


def test_no_query_time_optimizer(monkeypatch):
    import scipy.optimize
    monkeypatch.setattr(scipy.optimize,'least_squares',lambda *a,**k:pytest.fail('query-time fitting'))
    for arm in md.ARMS:state(md.synthetic_model(arm)).remaining_caffeine(.06)


def test_extreme_hat_products_qualified():
    m=md.synthetic_model('S2')
    m=replace(m,theta=[[x,0,0,0,0] for x in (-20,20,-20,20,-20)])
    ps=state(m).predict_intervals([.008,.02],[.08,.02])
    assert all(p.numerical_qualified for p in ps)

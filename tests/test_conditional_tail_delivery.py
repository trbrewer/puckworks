from dataclasses import FrozenInstanceError, replace
import json

import pytest
from scipy.integrate import quad
from scipy.special import expit

from puckworks.analysis import conditional_tail_delivery as m


def state(logits=(-2., -2., -2., -2., -2.), arm='C2'):
    model = m.synthetic_model(arm)
    model = replace(model, theta=tuple((v,)+(0.,)*len(model.means) for v in logits))
    return model.condition(m.EarlyInput(arm, (.004, .004, .15, .10)[:len(model.means)], 'SYNTHETIC'))


@pytest.mark.parametrize('logit', [-20., -2., 0., 3., 20.])
def test_constant_analytic(logit):
    s = state((logit,)*5)
    p = m.predict_intervals(s, [.008, .023, .08], [.023, .077, .08])
    for v in p:
        assert abs(v.solute_kg-(v.end_kg-v.start_kg)*expit(logit)) <= max(1e-17, v.allowance_kg)
        assert v.numerical_qualified
    assert p[-1].solute_kg == 0 and p[-1].tds_percent is None


@pytest.mark.parametrize('a,b', [(-1000., -999.), (999., 1000.), (-1000., 1000.),
    (-3., -3.+1e-14), (-3., -3.+1e-7), (1e-14, -1e-14), (0., .5), (0., .50000001),
    (19., 20.), (-20., -19.), (-.2, .2), (-20., 20.), (-1e-300, 1e-300)])
def test_divided_difference_against_independent_quad(a, b):
    value = float(m.segment_average(a, b))
    expected = quad(lambda u: expit((1-u)*a+u*b), 0, 1, epsabs=2e-14, epsrel=2e-13,
                    points=[.5], limit=300)[0]
    assert abs(value-expected) < 2e-13
    assert value == float(m.segment_average(b, a))
    assert 0 <= value <= 1


def test_crossings_additivity_order_batch_and_future_independence():
    s = state((-10., 1., -2., 4., -5.))
    starts, ends = [.008, .02, .041, .065], [.02, .041, .065, .08]
    pieces = s.predict_intervals(starts, ends)
    whole = s.remaining_solute(.08)
    assert abs(sum(p.solute_kg for p in pieces)-whole.solute_kg) <= whole.allowance_kg+sum(p.allowance_kg for p in pieces)
    assert pieces == tuple(reversed(s.predict_intervals(starts[::-1], ends[::-1])))
    assert pieces[0] == s.predict_intervals([starts[0]], [ends[0]])[0]
    assert pieces[0] == s.predict_intervals([starts[0], .076], [ends[0], .079])[0]
    assert all(0 <= p.solute_kg <= p.end_kg-p.start_kg and 0 <= p.tds_percent <= 100 for p in pieces)


def test_strict_immutable_serialization(tmp_path):
    s = state()
    with pytest.raises(FrozenInstanceError):
        s.b_anchor = 0
    with pytest.raises(TypeError):
        s.model.theta[0][0] = 7
    with pytest.raises(FrozenInstanceError):
        s.inputs.values = (1, 2)
    original = s.to_dict()
    loaded = m.State.from_dict(json.loads(json.dumps(original)))
    assert loaded == s
    original['model']['theta'][0][0] = 7
    assert s.logits[0] == -2
    with pytest.raises(ValueError):
        m.State.from_dict(original)
    path = tmp_path/'model.json'
    s.model.save(path)
    assert m.Model.load(path) == s.model
    with pytest.raises(FileExistsError):
        s.model.save(path)
    for change in ({'units': {}}, {'feature_order': list(reversed(m.FEATURES))}, {'scales': [1]*4}, {'extra': 1}):
        with pytest.raises(ValueError):
            m.Model.from_dict(s.model.to_dict() | change)
    with pytest.raises(ValueError):
        m.strict_json('{"a":1,"a":2}')
    with pytest.raises(ValueError):
        m.strict_json('{"a":NaN}')


@pytest.mark.parametrize('arm,forbidden', [('C0','q1'),('C0','q2'),('C1','q2')])
def test_ablation_cannot_accept_hidden_chemistry(arm, forbidden):
    values = {'m1_kg': .004, 'm2_kg': .004}
    if arm == 'C1':
        values['q1'] = .1
    m.early_input(arm, **values)
    with pytest.raises(ValueError):
        m.early_input(arm, **(values | {forbidden: .2}))


@pytest.mark.parametrize('a,b', [(.001,.02),(.008,.081),(.02,.01),(.02,float('nan')),
    (None,.02),(-1,.03),(.008,float('inf'))])
def test_invalid_support(a, b):
    with pytest.raises(ValueError):
        state().predict_intervals([a], [b])


def test_units_invalid_early_and_feature_extrapolation():
    with pytest.raises(ValueError):
        state().predict_intervals([.008], [.02], mass_unit='g')
    with pytest.raises(ValueError):
        m.EarlyInput('C2', (.004,.004,11.,10.))
    with pytest.raises(ValueError):
        m.EarlyInput('C0', (True,.004))
    with pytest.raises(ValueError):
        m.EarlyInput('C0', (0.,.004))
    with pytest.raises(ValueError):
        m.EarlyInput('C0', (.004,.004), basis='VOLUME')
    s = state().model.condition(m.EarlyInput('C2', (.004,.004,.3,.4)))
    assert s.feature_extrapolation == ('q1','q2')
    assert s.predict_intervals([.008],[.02])[0].numerical_qualified


def test_model_copies_mutable_coefficient_input():
    old = state().model
    coefficients = [list(row) for row in old.theta]
    new = replace(old, theta=coefficients)
    coefficients[0][0] = 19
    assert new.theta == old.theta

"""Analytic and synthetic verification; these are not experimental observations."""
from dataclasses import replace
import copy
import subprocess
import sys

import numpy as np
import pytest
from scipy.special import logit

from puckworks.analysis import conditional_trigonelline_delivery as m


def synthetic_model(arm='TR-D0', q=.001):
    return m.Model(arm, [[float(logit(q)), 0., 0.]]*5 if arm == 'TR-D0' else (),
                   (.004, .006), (.002, .003), (.009, .01), .08,
                   .01 if arm == 'TR-D0' else None, q if arm == 'TR-K0' else None,
                   m.canonical({'scope': 'SYNTHETIC'}), 'SYNTHETIC_FIRST_PARTY')


def state(model):
    return model.condition(m.EarlyInput(model.arm, (.004, .006), 'SYNTHETIC'))


@pytest.mark.parametrize('arm', m.ARMS)
def test_trigonelline_constant_integral_and_partition_additivity(arm):
    s = state(synthetic_model(arm))
    whole = s.remaining_trigonelline(.079)
    parts = s.predict_intervals([.01, .02, .037, .06], [.02, .037, .06, .079])
    assert whole.trigonelline_kg == pytest.approx(.001*.069, rel=0, abs=1e-18)
    assert whole.trigonelline_mg == pytest.approx(69.)
    assert whole.trigonelline_mg_g == pytest.approx(1.)
    assert abs(sum(p.trigonelline_kg for p in parts)-whole.trigonelline_kg) <= whole.allowance_kg+sum(p.allowance_kg for p in parts)
    assert all(p.numerical_qualified and p.allowance_kg <= 1e-9 for p in parts)


def test_trigonelline_no_target_columns_at_inference():
    inp = m.EarlyInput('TR-D0', (.004, .006), 'SYNTHETIC').to_dict()
    for forbidden in ('q1', 'q2', 'TDS', 'trigonelline', 'caffeine', 'time', 'pressure', 'recipe'):
        bad = copy.deepcopy(inp); bad['values'][forbidden] = 1.
        with pytest.raises(ValueError): m.EarlyInput.from_dict(bad)
    with pytest.raises(ValueError): m.EarlyInput('TR-D0', (.004, .006, .2))
    with pytest.raises(TypeError): state(synthetic_model()).predict_intervals([.01], [.02], TDS=.1)


def test_trigonelline_strict_species_serialization(tmp_path):
    for arm in m.ARMS:
        model = synthetic_model(arm)
        path = tmp_path / (arm+'.json'); model.save(path)
        assert m.Model.load(path) == model
        original = model.to_dict()
        for key, value in [('species', 'caffeine'), ('version', 'conditional-caffeine-delivery/1'),
                           ('units', dict(original['units'], concentration='mg/g')), ('extra', True)]:
            bad = copy.deepcopy(original); bad[key] = value
            with pytest.raises(ValueError): m.Model.from_dict(bad)
        s = state(model); saved = s.to_dict()
        assert m.State.from_dict(saved) == s
        saved['b_anchor'] = .011
        with pytest.raises(ValueError): m.State.from_dict(saved)
        with pytest.raises(FileExistsError): model.save(path)


def test_trigonelline_domain_and_zero_width_contract():
    s = state(synthetic_model())
    zero, = s.predict_intervals([.02], [.02])
    assert zero.trigonelline_kg == 0 and zero.trigonelline_mg_g is None
    for a, b in [([np.nextafter(.01, 0.)], [.02]), ([.02], [.01]), ([.02], [.081]),
                 ([float('nan')], [.03]), ([.02], []), ([.02], [float('inf')])]:
        with pytest.raises(ValueError): s.predict_intervals(a, b)
    with pytest.raises(ValueError): s.predict_intervals([.02], [.03], mass_unit='g')
    with pytest.raises(ValueError): m.EarlyInput('TR-D0', (True, .005))


def test_extreme_trigonelline_knots_have_independent_numerical_qualification():
    model = replace(synthetic_model(), theta=[[v, 0, 0] for v in (-20, 20, -20, 20, -20)])
    whole = state(model).remaining_trigonelline(.08)
    assert whole.numerical_qualified and whole.allowance_kg <= 1e-9
    assert whole.difference_adaptive_kg <= whole.allowance_kg


def test_trigonelline_saved_model_inference_without_optimizer(tmp_path):
    path = tmp_path / 'synthetic.json'; synthetic_model().save(path)
    code = """
import scipy.optimize
def forbidden(*args, **kwargs):
    raise RuntimeError('optimizer must never run during saved-model inference')
scipy.optimize.least_squares = forbidden
scipy.optimize.minimize = forbidden
from puckworks.analysis.conditional_trigonelline_delivery import Model, EarlyInput
import sys
model = Model.load(sys.argv[1])
result = model.condition(EarlyInput('TR-D0', (.004,.006), 'SYNTHETIC')).remaining_trigonelline(.07)
assert result.numerical_qualified
assert 'puckworks.analysis.conditional_trigonelline_training' not in sys.modules
"""
    subprocess.run([sys.executable, '-c', code, str(path)], check=True)

"""Analytic and synthetic verification; these are not experimental observations."""
from dataclasses import replace
import copy
import subprocess
import sys

import numpy as np
import pytest
from scipy.special import logit

from puckworks.analysis import conditional_5cqa_delivery as m


def synthetic_model(arm='D0', q=.001):
    return m.Model(arm, [[float(logit(q)), 0., 0.]]*5 if arm == 'D0' else (),
                   (.004, .006), (.002, .003), (.009, .01), .08,
                   .01 if arm == 'D0' else None, q if arm == 'E0' else None,
                   .03 if arm == 'E0' else None,
                   m.canonical({'scope': 'SYNTHETIC'}), 'SYNTHETIC_FIRST_PARTY')


def state(model):
    return model.condition(m.EarlyInput(model.arm, (.004, .006), 'SYNTHETIC'))


def test_five_cqa_constant_d0_integral_and_partition_additivity():
    s = state(synthetic_model('D0'))
    whole = s.remaining_5cqa(.079)
    parts = s.predict_intervals([.01, .02, .037, .06], [.02, .037, .06, .079])
    assert whole.five_cqa_kg == pytest.approx(.001*.069, rel=0, abs=1e-18)
    assert whole.five_cqa_mg == pytest.approx(69.)
    assert whole.five_cqa_mg_g == pytest.approx(1.)
    assert abs(sum(p.five_cqa_kg for p in parts)-whole.five_cqa_kg) <= whole.allowance_kg+sum(p.allowance_kg for p in parts)
    assert all(p.numerical_qualified and p.allowance_kg <= 1e-9 for p in parts)


def test_five_cqa_no_target_columns_at_inference():
    inp = m.EarlyInput('D0', (.004, .006), 'SYNTHETIC').to_dict()
    for forbidden in ('q1', 'q2', 'TDS', 'five_cqa', 'caffeine', 'time', 'pressure', 'recipe'):
        bad = copy.deepcopy(inp); bad['values'][forbidden] = 1.
        with pytest.raises(ValueError): m.EarlyInput.from_dict(bad)
    with pytest.raises(ValueError): m.EarlyInput('D0', (.004, .006, .2))
    with pytest.raises(TypeError): state(synthetic_model()).predict_intervals([.01], [.02], TDS=.1)


def test_five_cqa_strict_species_serialization(tmp_path):
    for arm in m.ARMS:
        model = synthetic_model(arm)
        path = tmp_path / (arm+'.json'); model.save(path)
        assert m.Model.load(path) == model
        original = model.to_dict()
        for key, value in [('species', 'caffeine'), ('species', 'CQA_sum'), ('species', '3CQA'),
                           ('species', 'trigonelline'), ('version', 'conditional-caffeine-delivery/1'),
                           ('units', dict(original['units'], concentration='mg/g')), ('extra', True)]:
            bad = copy.deepcopy(original); bad[key] = value
            with pytest.raises(ValueError): m.Model.from_dict(bad)
        s = state(model); saved = s.to_dict()
        assert m.State.from_dict(saved) == s
        saved['b_anchor'] = .011
        with pytest.raises(ValueError): m.State.from_dict(saved)
        with pytest.raises(FileExistsError): model.save(path)


def test_five_cqa_domain_and_zero_width_contract():
    s = state(synthetic_model())
    zero, = s.predict_intervals([.02], [.02])
    assert zero.five_cqa_kg == 0 and zero.five_cqa_mg_g is None
    for a, b in [([np.nextafter(.01, 0.)], [.02]), ([.02], [.01]), ([.02], [.081]),
                 ([float('nan')], [.03]), ([.02], []), ([.02], [float('inf')])]:
        with pytest.raises(ValueError): s.predict_intervals(a, b)
    with pytest.raises(ValueError): s.predict_intervals([.02], [.03], mass_unit='g')
    with pytest.raises(ValueError): m.EarlyInput('D0', (True, .005))


def test_extreme_five_cqa_knots_have_independent_numerical_qualification():
    model = replace(synthetic_model(), theta=[[v, 0, 0] for v in (-20, 20, -20, 20, -20)])
    whole = state(model).remaining_5cqa(.08)
    assert whole.numerical_qualified and whole.allowance_kg <= 1e-9
    assert whole.difference_adaptive_kg <= whole.allowance_kg


def test_five_cqa_saved_model_inference_without_optimizer(tmp_path):
    path = tmp_path / 'synthetic.json'; synthetic_model().save(path)
    code = """
import importlib.abc, sys
import scipy.optimize
def forbidden(*args, **kwargs):
    raise RuntimeError('optimizer called during inference')
scipy.optimize.least_squares = forbidden
scipy.optimize.minimize = forbidden
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, *args):
        if 'training' in fullname or fullname.startswith('openpyxl'):
            raise RuntimeError('forbidden inference dependency: '+fullname)
sys.meta_path.insert(0, Block())
from puckworks.analysis.conditional_5cqa_delivery import Model, EarlyInput
import sys
model = Model.load(sys.argv[1])
result = model.condition(EarlyInput('D0', (.004,.006), 'SYNTHETIC')).remaining_5cqa(.07)
assert result.numerical_qualified
assert 'puckworks.analysis.conditional_5cqa_training' not in sys.modules
"""
    subprocess.run([sys.executable, '-c', code, str(path)], check=True)
    # SciPy initializes optimization utilities transitively with its integration
    # namespace; the research runtime itself imports no optimizer or training API.
    import ast
    from pathlib import Path
    tree = ast.parse(Path(m.__file__).read_text())
    assert not any(isinstance(n, ast.ImportFrom) and n.module and
                   ('training' in n.module or 'optimize' in n.module) for n in ast.walk(tree))


@pytest.mark.parametrize('amplitude,length', [(0., .001), (1., 1.), (.007, .023)])
def test_exponential_exact_integral_stability_additivity_and_units(amplitude, length):
    from decimal import Decimal, localcontext
    model = replace(synthetic_model('E0'), amplitude=amplitude, decay_kg=length)
    s = state(model)
    a, b = .025, np.nextafter(.025, 1.)
    p, = s.predict_intervals([a], [b])
    with localcontext() as ctx:
        ctx.prec = 75
        A, L, lo, hi = map(Decimal.from_float, (amplitude, length, a, b))
        expected = float(A*L*((-lo/L).exp()-(-hi/L).exp()))
    assert p.five_cqa_kg == pytest.approx(expected, rel=2e-14, abs=1e-35)
    whole = s.remaining_5cqa(.075)
    parts = s.predict_intervals([.01,.027,.05], [.027,.05,.075])
    assert abs(sum(x.five_cqa_kg for x in parts)-whole.five_cqa_kg) <= whole.allowance_kg+sum(x.allowance_kg for x in parts)
    assert whole.five_cqa_mg == 1e6*whole.five_cqa_kg
    assert whole.five_cqa_mg_g == 1000*whole.five_cqa_kg/(.075-.01)
    assert whole.species == '5CQA' and whole.model_sha256 == model.sha256
    assert dict(whole.units)['concentration'] == 'kg/kg'
    assert all(x.numerical_qualified and 0 <= x.five_cqa_kg <= x.end_kg-x.start_kg for x in parts)
    # Neither early mass changes the global curve at a common permissible interval.
    other = model.condition(m.EarlyInput('E0', (.002, .003), 'SYNTHETIC'))
    assert s.predict_intervals([.02],[.04])[0].five_cqa_kg == other.predict_intervals([.02],[.04])[0].five_cqa_kg


def test_models_and_states_are_immutable_and_exponential_bounds_strict():
    from dataclasses import FrozenInstanceError
    model = synthetic_model('E0')
    with pytest.raises(FrozenInstanceError): model.amplitude = .1
    with pytest.raises(FrozenInstanceError): state(model).b_anchor = 0.
    for changes in ({'amplitude':1.1}, {'amplitude':-.1}, {'decay_kg':.0009},
                    {'decay_kg':1.1}, {'decay_kg':float('nan')}, {'species':'CQA_sum'}):
        with pytest.raises(ValueError): replace(model, **changes)


def test_d0_extreme_allowed_feature_slopes_are_qualified_or_explicitly_rejected():
    for theta in (np.full((5,3),20.), np.full((5,3),-20.),
                  np.asarray([[20*(-1)**j, 20, -20] for j in range(5)])):
        s = state(replace(synthetic_model(), theta=theta))
        p = s.remaining_5cqa(.08)
        assert np.isfinite(p.five_cqa_kg) and 0 <= p.five_cqa_kg <= .07
        assert p.numerical_qualified and p.allowance_kg <= 1e-9
    model = replace(synthetic_model(), theta=[[20*(-1)**j, -20*(-1)**j, 20*(-1)**j] for j in range(5)])
    extrapolated = model.condition(m.EarlyInput('D0', (.0001, .0199), 'SYNTHETIC'))
    assert extrapolated.feature_extrapolation == ('m1_kg', 'm2_kg')
    p, = extrapolated.predict_intervals([.0213], [.0771])
    # Allowed coefficients plus extrapolated features can be too steep for the
    # fixed quadrature. Retain the failed numerical gate; never expand its budget.
    assert not p.numerical_qualified and p.allowance_kg > 1e-9
    assert p.difference_adaptive_kg <= p.allowance_kg

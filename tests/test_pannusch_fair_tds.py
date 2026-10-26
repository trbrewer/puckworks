"""Synthetic conservation/observation/weight tests; no external target reads."""
import numpy as np
import pytest

from puckworks.analysis import pannusch_fair_tds as m
from puckworks.analysis import pannusch_equilibrium_limit as eq
from puckworks.models.pannusch2024 import solver as ps


def shot(name, condition, windows, masses):
    return dict(shot=name, condition=condition, windows=windows, masses_g=masses,
                temperature_C=89., flow_label=2., start_s=0., grind=1.7)


def test_density_front_and_inventory():
    p = ps._solute_params()['tds']
    s = m.Scenario(89., 2., p)
    front = s.constants()['front_s']
    windows = [[0, front/2], [front/2, front*1.5], [front*1.5, front*2]]
    values, _ = m.predict('E', p, [shot('a', 'c', windows, [1, 2, 1])])
    plateau = 100*s.constants()['K']*p['c_s0']/980
    assert values[0] == pytest.approx([plateau, plateau/2, 0])
    assert np.dot(values[0]*980/100, np.diff(windows).ravel())*s.Q == pytest.approx(s.system(1).M0(s.T))


def test_union_trajectory_keeps_individual_windows_and_gaps():
    p = ps._solute_params()['tds']
    shots = [shot('a', 'c', [[0, 3], [4, 7], [10, 14]], [3, 2, 4]),
             shot('b', 'c', [[0, 2], [3, 6], [9, 15]], [1, 4, 3])]
    joined, diagnostics = m.predict('F', p, shots, cells=16)
    for i, q in enumerate(shots):
        single, _ = m.predict('F', p, [q], cells=16)
        assert joined[i] == pytest.approx(single[0], abs=1e-10)
    assert len(diagnostics) == 1
    assert diagnostics[0]['mass_balance_relative'] < 1e-9
    assert diagnostics[0]['minimum_phase_kg_m3'] >= 0
    scaled, _ = m.predict('F', dict(p, c_s0=p['c_s0']*2), shots, cells=16)
    assert scaled == pytest.approx(joined*2, abs=1e-10)


def test_profiled_amplitude_and_group_balance():
    shots = [shot('a', 'c', [[0, 1], [2, 3]], [1, 3]),
             shot('b', 'c', [[0, 1], [2, 3]], [2, 2]),
             shot('d', 'e', [[0, 1], [2, 3]], [3, 1])]
    w = m.weights(shots)
    assert w.sum(axis=1) == pytest.approx([.25, .25, .5])
    u = np.array([[1., 2], [3, 4], [5, 6]])
    observed = u*7 + np.array([[1, -1], [2, -2], [3, -3]])
    a = m.amplitude(u, observed, w, [0, 10])
    loss = lambda v: np.sum(w*(u*v-observed)**2)
    assert loss(a) < loss(a-.01) and loss(a) < loss(a+.01)


def test_bias_is_absolute_before_aggregation_and_deletion_rebalances():
    first = m.shot_metrics([2., 4.], np.array([1., 1.]), [3., 1.])
    second = m.shot_metrics([0., 0.], np.array([1., 3.]), [3., 1.])
    rows = [dict(condition='a', **first), dict(condition='b', **second)]
    out = m.aggregate(rows)
    assert out['B'] == pytest.approx(0)
    assert out['A'] == pytest.approx(1.5)
    assert out['R'] == pytest.approx(np.sqrt(3))
    assert m.aggregate(rows[:1]) == first


def test_original_source_kernel_is_reused():
    s = m.Scenario(89., 2., ps._solute_params()['tds'])
    windows = [[0., 4.], [7., 12.]]
    expected, _ = eq.finite_averages(s, windows, cells=12)
    actual, _ = m.predict('F', s.parameters, [shot('a', 'c', windows, [3, 4])], cells=12)
    assert actual[0] == pytest.approx(100*expected/980, abs=1e-10)


def test_band_boundaries():
    assert [m.band(x) for x in [-.01, 0, .0999, .1, .2499, .25]] == [
        'worse', 'small', 'small', 'moderate', 'moderate', 'large']
    assert m.interval_bands(-.1, .3) == ['large', 'moderate', 'small', 'worse']

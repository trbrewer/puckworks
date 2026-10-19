"""Analytical, algebraic and small synthetic checks; no experimental targets."""
import numpy as np
import pytest
from scipy.integrate import quad
from scipy.special import gammaincc

from puckworks.analysis import pannusch_equilibrium_limit as m


@pytest.mark.parametrize('species', m.SPECIES)
def test_phase_capacity_front_and_exact_inventory(species):
    s = m.Scenario(species, 86., 2., start_s=7.)
    p, system = s.constants(), s.system(4)
    assert p['S'] == pytest.approx(.83*(.23+.4*.77))
    assert p['H'] == pytest.approx(.17+p['S']/p['K'])
    assert system.initial(s.T)[:4].min() > 0  # clean inlet does not delete liquid
    assert system.initial(s.T).sum() == pytest.approx(p['initial_total_kg'])
    w = [[7., p['front_s']+3]]
    c = m.equilibrium_averages(s, w)[0]
    assert s.Q*(w[0][1]-7)*c == pytest.approx(p['initial_total_kg'])
    assert p['initial_liquid_kg']+p['initial_fine_kg']+p['initial_coarse_kg'] == pytest.approx(p['initial_total_kg'])


def test_front_crossing_gaps_and_boundary_integrals():
    s = m.Scenario('caffeine', 90., 2.)
    p = s.constants()
    f, amplitude = p['front_s'], p['K']*p['c_s0']
    w = [[0., .2*f], [.3*f, .5*f], [.8*f, f], [f, 1.1*f], [1.2*f, 1.3*f], [1.4*f, 2*f]]
    np.testing.assert_allclose(m.equilibrium_averages(s, w), [amplitude]*3+[0.]*3)
    assert m.equilibrium_averages(s, [[.8*f, 1.2*f]])[0] == pytest.approx(amplitude/2)
    # An independent quadrature of the discontinuous outlet, split at its front.
    assert quad(lambda t: amplitude if t < f else 0., .8*f, 1.2*f, points=[f])[0] == pytest.approx(.2*f*amplitude)


def test_same_source_flow_convention():
    s = m.Scenario('caffeine', 90., 1.96)
    assert s.Q == pytest.approx(2e-6)
    assert s.Q != 1.96e-6


def test_normalized_scale_and_density_units():
    c, mass = np.arange(1, 7.), np.arange(2, 8.)*.001
    p, _, quantity = m.normalize(c, mass)
    np.testing.assert_allclose(quantity, mass/980*c)
    for scale in (.001, 10.):
        np.testing.assert_allclose(m.normalize(c*scale, mass)[0], p)
        np.testing.assert_allclose(m.normalize(c, mass*scale)[0], p)


def test_normalization_allowance_encloses_extreme_perturbations():
    import itertools
    c, mass, e = np.arange(1, 7.), np.arange(2, 8.)*.001, np.full(6, .03)
    p, d, _ = m.normalize(c, mass, errors=e)
    for signs in itertools.product((-1., 1.), repeat=6):
        perturbed = m.normalize(c+e*np.array(signs), mass)[0]
        assert np.all(abs(perturbed-p) <= d)
        target = np.array([.5, .2, .1, .1, .05, .05])
        assert abs(m.rmse(perturbed-target)-m.rmse(p-target)) <= m.rmse(d)


@pytest.mark.parametrize('c', [np.zeros(6), np.array([-1.,1,1,1,1,1]), np.full(6,np.nan)])
def test_unavailable_normalizations_are_rejected(c):
    with pytest.raises(ValueError):
        m.normalize(c, np.ones(6))


def test_unresolved_within_allowance_and_tail_zero():
    with pytest.raises(ValueError):
        m.normalize(np.ones(6), np.ones(6), errors=np.ones(6))
    p, _, _ = m.normalize([1.,1,1,0,0,0], np.ones(6))
    assert np.array_equal(p[-3:], [0.,0,0])


def test_finite_generator_mass_positivity_scale_and_semigroup():
    s = m.Scenario('trigonelline', 90., 2.)
    windows = [[0., .2], [.2, .4], [.6, .8], [1., 1.2], [1.4, 1.6], [2., 2.5]]
    a, ledger = m.finite_averages(s, windows, cells=4)
    b, _ = m.finite_averages(s, windows, cells=4, halves=True, scale=.03)
    np.testing.assert_allclose(b/.03, a, rtol=1e-12)
    assert ledger['mass_balance_relative'] < 1e-12
    assert ledger['remaining_kg']+ledger['total_outlet_kg'] == pytest.approx(ledger['initial_inventory_kg'])
    assert ledger['minimum_phase_kg_m3'] >= 0
    B = s.system(4).generator(s.T)
    np.testing.assert_allclose(np.asarray(B.sum(axis=0)), 0., atol=1e-14)
    off = B.toarray()
    np.fill_diagonal(off,0)
    assert off.min() >= 0


def test_finite_grid_equilibrium_is_not_continuum_front():
    s = m.Scenario('caffeine', 90., 2.)
    p = s.constants()
    f, n = p['front_s'], 4
    w = [[0., .5*f], [.8*f, 1.2*f], [1.2*f, 2*f]]
    reference = np.array([quad(lambda t: p['K']*p['c_s0']*gammaincc(n,n*t/f),a,b)[0]/(b-a) for a,b in w])
    np.testing.assert_allclose(m.grid_equilibrium_averages(s,w,n),reference,rtol=1e-12)
    assert reference[-1] > 0 == m.equilibrium_averages(s,w)[-1]


def test_rebalancing_after_omission_is_not_flat_profile_average():
    rows = [dict(condition=c,shot=f'{c}{j}',analyte=a,value=v)
            for c,v,count in [('A',1.,2),('B',3.,3)] for j in range(count) for a in m.SPECIES]
    assert m.balanced(rows,'value') == 2.
    assert np.mean([r['value'] for r in rows]) != 2.


@pytest.mark.parametrize('windows', [[[1,1]], [[-1,2]], [[1,3],[2,4]], [[0,np.nan]]])
def test_invalid_window_support(windows):
    with pytest.raises(ValueError):
        m.equilibrium_averages(m.Scenario('caffeine',90.,2.),windows)

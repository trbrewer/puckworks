"""Small actual-update regressions, not hidden full-horizon qualification runs."""
import ast
from pathlib import Path

import numpy as np
import pytest
from scipy.linalg import expm

from puckworks.analysis import grudeva2026_conservative_003 as ref


def test_old_nodal_counterexample_is_retained_with_its_actual_scope():
    row = ref.old_counterexample()
    assert row['count'] == 1
    assert row['mapped_source_integral'] == pytest.approx(.00016, abs=1e-18)
    assert row['old_nodal_observed_donation'] == pytest.approx(.00008, abs=1e-18)
    amount = .8*.002*.05  # exact cell average of the SAME prescribed triangle
    receiver = np.array([0., .0003, .0014, .002])
    assert sum(ref.transfer_amounts(np.array([amount]), receiver, np.array([0., .002]))) == pytest.approx(.00008, abs=1e-18)


@pytest.mark.parametrize('initial,liquid', [(1.388, .2), (.2, .9), (.7, .7)])
def test_actual_nonmatching_exchange_signed_and_equilibrium(initial, liquid):
    radial = ref.Radial(24)
    d = np.array([0., .013, .07, .19, .2])
    r = np.array([0., .02, .045, .1, .15, .2])
    old = initial*np.ones((24, len(d)-1))*np.diff(d)
    c0 = np.full(len(r)-1, liquid)
    c, j, audit = ref.coupled_exchange(radial, old, c0, d, r, .004)
    dl = np.diff(r) @ (c-c0)
    df = ref.BETA*dl
    db = ref.DELTA*np.sum(radial.means(j-old))
    allowance = ref.ALGEBRA_RTOL*audit['scale']+audit['linear_residual']
    assert abs(dl+df+db) <= allowance
    assert audit['amount_residual'] <= allowance
    if initial != liquid:
        assert np.sign(dl) == np.sign(initial-liquid)
    else:
        assert c == pytest.approx(c0, abs=2e-14)
    o = ref.overlap(r, d)
    p = o.multiply((1/np.diff(r))[:, None])
    assert np.diff(r) @ p == pytest.approx(np.diff(d), abs=2e-17)


def test_nonuniform_nonconstant_signed_amounts_no_endpoint_extension():
    d = np.array([0., .002, .007, .012])
    r = np.array([0., .001, .005, .01, .012])
    amounts = np.array([.00008, -.00003, .00011])
    mapped = ref.transfer_amounts(amounts, r, d)
    assert sum(mapped) == pytest.approx(sum(amounts), abs=1e-19)
    with pytest.raises(ValueError, match='supports'):
        ref.transfer_amounts(amounts, np.array([0., .02]), d)
    radial = ref.Radial(24)
    c0 = np.array([.2, .6, .4, .8])
    old = np.ones((24, 3))*np.diff(d)*np.array([1.388, .1, 1.1])
    c1, j1, audit = ref.coupled_exchange(radial, old, c0, d, r, .001)
    losses = radial.means(old-j1)
    assert min(losses) < 0 < max(losses)
    balance = ref.CAPACITY*np.diff(r) @ (c1-c0)-ref.DELTA*sum(losses)
    assert abs(balance) <= ref.ALGEBRA_RTOL*audit['scale']+audit['linear_residual']


def test_continuous_admission_matches_independent_shell_cohort_quadrature():
    radial = ref.Radial(8)
    h, speed, boundary = .013, .17, .2
    old = np.zeros((8, 1))
    actual = radial.advance(old, np.array([boundary]), np.array([boundary]),
                            np.zeros(1), np.array([speed*h]), h)
    _, lower, diagonal, upper, _, _ = radial.op
    matrix = np.diag(diagonal)+np.diag(lower, -1)+np.diag(upper, 1)
    nodes, weights = np.polynomial.legendre.leggauss(32)
    ages = h*(nodes+1)/2
    independent = sum(weight*(boundary+expm(matrix*age) @ np.full(8, ref.INITIAL-boundary))
                      for age, weight in zip(ages, weights))*h*speed/2
    assert radial.shells(actual)[:, 0] == pytest.approx(independent, abs=3e-17)
    # Splitting admission into different ages preserves all existing memory.
    first = radial.advance(old, np.array([boundary]), np.array([boundary]),
                           np.zeros(1), np.array([speed*h/3]), h/3)
    split = radial.advance(first, np.array([boundary]), np.array([boundary]),
                           np.array([speed*h/3]), np.array([speed*2*h/3]), 2*h/3)
    assert split == pytest.approx(actual, abs=4e-17)


def test_actual_positive_diffusion_moving_step_has_paired_inventory():
    radial = ref.Radial(32)
    faces = np.array([0., .02, .09, .095])
    c0 = np.array([.02, .12, .2])
    j0 = np.full((32, 3), ref.INITIAL)*np.diff(faces)
    c1, j1, new_faces, audit = ref.step(radial, c0, j0, faces, .001)
    ds = new_faces[-1]-faces[-1]
    # The optimized path executed by run() is the same shell integrator that
    # receives the positive-age analytic qualification, including admission.
    independently_advanced = radial.advance(j0, c0, c1, np.diff(faces),
                                             np.diff(new_faces)-np.diff(faces), .001)
    assert j1 == pytest.approx(independently_advanced, abs=2e-17)
    before = ref.CAPACITY*np.diff(faces) @ c0+ref.DELTA*sum(radial.means(j0))
    after = ref.CAPACITY*np.diff(new_faces) @ c1+ref.DELTA*sum(radial.means(j1))
    expected = ref.DELTA*ref.INITIAL*ds-audit['face_amount'][-1]
    assert after-before == pytest.approx(expected, abs=5e-16)
    assert abs(audit['front_residual']) < 2e-18
    assert audit['transfer_residual'] <= ref.ALGEBRA_RTOL*audit['algebra_scale']+audit['linear_residual']


def test_manufactured_transport_geometry_and_fixed_domain():
    old = np.array([0., .03, .09, .2])
    for speed in (0., .08):
        h, slope = .003, .2
        new = old.copy(); new[-1] += speed*h
        c0 = slope*(old[:-1]+old[1:])/2
        # C=k*z is stationary, G=k; exact space-time source volume integral.
        source = h*slope*(np.diff(old)+np.diff(new))/2
        c1, _, _, err = ref.transport_solve(c0, old, new, h, source, np.zeros(3))
        assert c1 == pytest.approx(slope*(new[:-1]+new[1:])/2, abs=2e-17)
        assert err < 1e-17
        uniform, _, _, _ = ref.transport_solve(np.full(3, .3), old, new, h,
                                               np.zeros(3), np.zeros(3), inlet=.3)
        assert uniform == pytest.approx(.3, abs=1e-16)


def test_empty_initial_support_and_exact_zero_diffusion_front_step():
    radial = ref.Radial(8, 0.)
    c, j, f, d = ref.step(radial, np.zeros(1), np.zeros((8, 1)), np.zeros(2), .01)
    assert f[-1] == pytest.approx(.01/5.4416, rel=1e-12)
    assert c == pytest.approx(0., abs=1e-15)
    assert j == pytest.approx(ref.INITIAL*f[-1], abs=1e-17)
    assert abs(d['front_residual']) <= 1e-17


def test_no_production_helpers_and_no_import_execution():
    tree = ast.parse(Path(ref.__file__).read_text())
    names = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    assert not any(n and 'models' in n for n in names)
    assert ref.observation_support(8.)[0][-1] == 8.
    for invalid in ({'bed': True}, {'dt': 0.}, {'horizon': 9.}, {'diffusivity': -1.}):
        with pytest.raises(ValueError):
            ref.Controls(**invalid)


def test_observer_return_seam_restores_and_forbids_extrapolation():
    from types import SimpleNamespace
    from puckworks.analysis.grudeva2026_conservative_003_observer import capture_returns, evaluate
    result = SimpleNamespace(t=np.array([0., 1.]), sol=lambda t: np.array([t]))
    original = lambda *a, **kw: result
    module = SimpleNamespace(solve_ivp=original)
    with capture_returns(module) as segments:
        returned = module.solve_ivp(None, (0., 1.), None, events=None)
        assert returned is result
    assert module.solve_ivp is original
    assert evaluate(segments, 1.)[0][0] == 1.
    with pytest.raises(ValueError, match='outside'):
        evaluate(segments, 1.0001)
    with pytest.raises(RuntimeError):
        with capture_returns(module):
            raise RuntimeError('synthetic interruption')
    assert module.solve_ivp is original


def test_report_norm_missing_and_empty_support_cannot_pass():
    from puckworks.analysis.grudeva2026_conservative_003_report import norm
    missing = norm(np.array([0., 1.e6]), np.array([True, True]), np.array([True, False]), .001)
    assert not missing['passed'] and missing['max_absolute'] == 0
    assert missing['included'] == missing['unavailable'] == 1
    empty = norm(np.zeros(2), np.zeros(2, bool), np.ones(2, bool), .001)
    assert not empty['passed'] and empty['max_absolute'] is None

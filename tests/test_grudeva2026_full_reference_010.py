"""Independent mathematical controls; only bounded fixtures, no horizon-8 case."""
from dataclasses import replace
import json

import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

from puckworks.analysis.grudeva2026_full_reference_010 import (
    Case, Model, Settings, Sphere, geometric_rhs, integrate, liquid_flux,
)
from puckworks.analysis.grudeva2026_full_reference_010_io import (
    boundary_quadrature, capture, fv_weights, independent_inventories,
    load_archive, observe, radial_weights, save_archive,
)


def robin_reference(faces, times, D, Q, k, initial, liquid, modes=800):
    """Continuum sphere eigenfunctions, independent of the FV spatial matrix."""
    Bi = Q*k/D
    roots = np.array([brentq(lambda x: x/np.tan(x)-(1-Bi),
                            n*np.pi+1e-9, (n+1)*np.pi-1e-9)
                      for n in range(modes)])
    a, b = faces[:-1, None], faces[1:, None]
    def primitive(r):
        u = r*roots
        return (np.sin(u)-u*np.cos(u))/roots**3
    shell = 3*(primitive(b)-primitive(a))/(b**3-a**3)
    A = 2*(np.sin(roots)-roots*np.cos(roots))/(roots*(1-np.sin(2*roots)/(2*roots)))
    coefficients = (initial-liquid)*np.exp(-np.outer(times, D*roots**2))*A
    means = 3*(np.sin(roots)-roots*np.cos(roots))/roots**3
    return (liquid+coefficients@shell.T, liquid+coefficients@means,
            liquid+coefficients@(np.sin(roots)/roots))


def saturated_reference(times, D, J, initial, modes=800):
    roots = np.array([brentq(lambda x: np.tan(x)-x,
                            n*np.pi+1e-9, (n+.5)*np.pi-1e-9)
                      for n in range(1, modes+1)])
    times = np.asarray(times)
    means = initial-3*J*times
    surface = means-J/(5*D)+(2*J/D)*(np.exp(-np.outer(times, D*roots**2))/roots**2).sum(axis=1)
    return means, surface


def test_declared_parameter_derivation():
    c = Case()
    c.check()
    assert c.M0 == pytest.approx(5.552, abs=1e-15)
    np.testing.assert_allclose(c.Q, [5/48, 5/12], atol=1e-15)
    with pytest.raises(ValueError):
        replace(c, epsilon=.02).check()


@pytest.mark.parametrize('initial,liquid', [(.8, .2), (.2, .8)])
def test_independent_robin_sphere(initial, liquid):
    times = np.array([1e-5, 1e-4, .001, .01, .1])
    errors = []
    for n in (16, 32, 64):
        sphere = Sphere(n, .7, .4, 2.5)
        ref, mean, surface = robin_reference(sphere.faces, times, .7, .4, 2.5, initial, liquid)
        if n == 64:
            check = robin_reference(sphere.faces, times, .7, .4, 2.5, initial, liquid, 1600)
            np.testing.assert_allclose(ref, check[0], atol=2e-12, rtol=0)
        result = solve_ivp(lambda t, y: sphere.rhs(y, sphere.transfer(y, liquid)[0]),
                           (0, .1), np.full(n, initial), method='BDF', t_eval=times,
                           rtol=1e-10, atol=1e-12)
        assert result.success
        transfer, cs = sphere.transfer(result.y.T, liquid)
        metrics = {'n': n, 'profile': float(np.max(abs(result.y.T-ref))),
                   'mean': float(np.max(abs(sphere.mean(result.y.T)-mean))),
                   'surface': float(np.max(abs(cs-surface))),
                   'flux': float(np.max(abs(transfer-2.5*(surface-liquid))))}
        errors.append(metrics)
    print('ROBIN', initial, liquid, json.dumps(errors))
    assert errors[-1]['profile'] < 2e-3
    assert errors[-1]['mean'] < 2e-4
    assert errors[-1]['flux'] < 5e-3
    assert errors[-1]['profile'] < errors[-2]['profile'] < errors[-3]['profile']


def test_saturated_surface_short_age_and_zero_transfer():
    sphere = Sphere(64, 1., .25, 4.)
    times = np.array([1e-5, 1e-4, .001, .01])
    initial, liquid = 1.4, .2
    result = solve_ivp(lambda t, y: sphere.rhs(y, sphere.transfer(y, liquid)[0]),
                       (0, .01), np.full(64, initial), method='BDF', t_eval=times,
                       rtol=1e-10, atol=1e-12)
    mean, cs = saturated_reference(times, 1., .8, initial)
    G, actual_cs = sphere.transfer(result.y.T, liquid)
    print('SATURATED', {'surface_error': float(max(abs(actual_cs-cs))),
                        'mean_error': float(max(abs(sphere.mean(result.y.T)-mean)))})
    np.testing.assert_allclose(sphere.mean(result.y.T), mean, atol=2e-9, rtol=0)
    np.testing.assert_allclose(actual_cs, cs, atol=2e-4, rtol=0)
    assert np.all(G > 0)
    for grain, liquid in [(.6, .6), (1.4, 1.)]:
        g, surface = sphere.transfer(np.full(64, grain), liquid)
        assert g == 0.
        np.testing.assert_array_equal(sphere.rhs(np.full(64, grain), g), 0.)


def test_surface_transition_is_signed_and_continuous():
    sphere = Sphere(16, 1., .4, 3.)
    for liquid in (.2, 1.2):
        threshold = 1+sphere.Q*sphere.k*(1-liquid)/sphere.h
        states = np.full((3, 16), threshold)
        states[:, -1] += [-1e-10, 0, 1e-10]
        G, surface = sphere.transfer(states, liquid)
        np.testing.assert_allclose(G, sphere.k*(np.minimum(surface, 1)-liquid), atol=1e-14)
        assert max(abs(np.diff(G))) < 1e-8
        assert np.all(G < 0) if liquid > 1 else np.all(G > 0)


@pytest.mark.parametrize('initial,liquid,expected_l', [(.8, .2, .68), (1.4, .2, 1.)])
def test_closed_paired_transfer(initial, liquid, expected_l):
    c = Case()
    spheres = [Sphere(12, D, Q, k) for D, Q, k in zip([100., 1.], c.Q, c.k)]
    def rhs(t, y):
        L, rates, total = y[0], [], 0.
        for i, sphere in enumerate(spheres):
            grains = y[1+i*12:1+(i+1)*12]
            G, surface = sphere.transfer(grains, L)
            total += G
            rates.extend(sphere.rhs(grains, G))
        return np.r_[total, rates]
    y0 = np.r_[liquid, np.full(24, initial)]
    result = solve_ivp(rhs, (0, 4), y0, method='BDF', rtol=1e-9, atol=1e-11)
    y = result.y[:, -1]
    M = y[0]+sum(w*s.mean(y[1+i*12:1+(i+1)*12]) for i, (w,s) in enumerate(zip(c.weights,spheres)))
    assert M == pytest.approx(liquid+4*initial, abs=2e-8)
    assert y[0] == pytest.approx(expected_l, abs=2e-7)
    if initial > 1:
        assert np.min(y[1:]) > 1-1e-7
        weighted_grain = sum(w*s.mean(y[1+i*12:1+(i+1)*12])
                             for i, (w,s) in enumerate(zip(c.weights, spheres)))/4
        assert weighted_grain == pytest.approx(1.2, abs=2e-7)
    else:
        np.testing.assert_allclose(y, expected_l, atol=3e-7, rtol=0)
    probe = np.r_[.7, np.linspace(.2, 1.5, 24)]
    derivative = rhs(0, probe)
    total = derivative[0]+sum(w*s.mean(derivative[1+i*12:1+(i+1)*12])
                              for i, (w,s) in enumerate(zip(c.weights,spheres)))
    assert abs(total) < 1e-10


@pytest.mark.parametrize('moving,t', [(False, 1.5), (True, .3)])
def test_liquid_manufactured_actual_operator(moving, t):
    # c=(.2+.1*t)*(2*z/s-(z/s)^2), zero inlet, zero right gradient.
    s = t if moving else 1.
    errors = []
    for n in (16, 32, 64):
        faces = s*np.linspace(0, 1, n+1)
        a, b = faces[:-1]/s, faces[1:]/s
        C = (.2+.1*t)*(a+b-(a*a+a*b+b*b)/3)
        flux, out = liquid_flux(C, s, moving)
        x = faces/s
        exact = ((1-moving*x)*(.2+.1*t)*(2*x-x*x)
                 -.01*(.2+.1*t)*(2-2*x)/s)
        # This is the actual conservative divergence contribution to the RHS.
        errors.append(float(np.mean(abs(n*np.diff(flux-exact)/s))))
    print('LIQUID_RHS', moving, errors)
    assert errors[-1] < errors[-2]/1.5 < errors[-3]/1.5**2
    assert errors[-1] < 1e-3
    n = 64
    faces = s*np.linspace(0, 1, n+1)
    a, b = faces[:-1]/s, faces[1:]/s
    C = (.2+.1*t)*(a+b-(a*a+a*b+b*b)/3)
    flux, out = liquid_flux(C, s, moving)
    x = faces/s
    exact = ((1-moving*x)*(.2+.1*t)*(2*x-x*x)
             -.01*(.2+.1*t)*(2-2*x)/s)
    # Centered internal advection of exact quadratic averages has a known O(h²) error.
    assert max(abs(flux-exact)) < 3e-5
    assert flux[0] == pytest.approx(-.02*(.2+.1*t)/s, abs=1e-14)
    assert flux[0] < 0
    assert out == pytest.approx(.2+.1*t, abs=1e-14)


def test_geometry_memory_and_admission():
    n, t = 64, .4
    faces = np.linspace(0, 1, n+1)
    xi = (faces[:-1]+faces[1:])/2
    uniform = np.full((n, 4), 1.388)
    np.testing.assert_allclose(geometric_rhs(uniform, t, faces, 1.388), 0, atol=4e-14)
    # Manufactured fixed-z history c=c0-A*(t-z), radial forcing R=-A.
    A = np.array([.1, .2, .3, .4])
    grain = 1.388-t*(1-xi[:, None])*A
    actual = geometric_rhs(grain, t, faces, 1.388)-A
    np.testing.assert_allclose(actual, -(1-xi[:, None])*A, atol=1e-13)
    # Integral geometric admission uses exact initial boundary, independent of interior.
    expected = (1.388-grain.mean(axis=0))/t
    np.testing.assert_allclose(geometric_rhs(grain, t, faces, 1.388).mean(axis=0), expected,
                               atol=1e-14)


def test_startup_and_independent_inventory_quadrature():
    for tau in (1e-5, 1e-6, 1e-7):
        model = Model(Settings(axial=16, fines=16, boulders=32, startup=tau))
        y = model.startup(tau)
        phases = model.inventories(tau, y)
        np.testing.assert_allclose(phases, independent_inventories(model, tau, y), atol=1e-13)
        residual = sum(phases)+y[-1]-y[-2]-model.case.M0
        assert residual == pytest.approx(200*tau**3/.03, abs=5e-13)
        state = model.split(y,tau)
        for sphere, sl in zip(model.spheres, model.slices):
            G, surface = sphere.transfer(state[:, sl], state[:, 0])
            assert min(surface) > 1
    print('STARTUP', {'last_residual': residual, 'scales': [1e-5, 1e-6, 1e-7]})


def test_observation_reconstruction_exact_polynomials():
    faces = np.linspace(0, 1, 33)
    a, b = faces[:-1], faces[1:]
    C = a+b-(a*a+a*b+b*b)/3
    z = np.linspace(0, 1, 101)
    np.testing.assert_allclose(fv_weights(faces, z, True, True)@C, 2*z-z*z, atol=1e-13)
    sphere = Sphere(32, 1, .4, 2.)
    a, b = sphere.faces[:-1], sphere.faces[1:]
    # Integrate c=0.2+0.3*r²+0.1*r⁴ independently with Gaussian quadrature.
    x, w = np.polynomial.legendre.leggauss(6)
    r = (a+b)[:, None]/2+(b-a)[:, None]*x/2
    mean = (((.2+.3*r*r+.1*r**4)*r*r*w).sum(axis=1)*(b-a)/2/sphere.volume)
    obs = np.linspace(0, 1, 41)
    np.testing.assert_allclose(radial_weights(sphere, obs)@mean, .2+.3*obs**2+.1*obs**4,
                               atol=1e-11, rtol=0)


@pytest.mark.slow
def test_capture_transition_availability_and_safe_archive(tmp_path):
    settings = Settings(axial=12, fines=6, boulders=8, rtol=1e-6, atol=1e-12, max_step=.05)
    model, results = integrate(settings, horizon=1.01)
    trajectory = capture(model, results)
    np.testing.assert_array_equal(results[0][1].y[:, -1], results[1][1].y[:, 0])
    assert results[0][1].y[-1].max() == 0
    support = {'times': [0., 1e-7, .1, .5, .9999, 1., 1.0001, 1.01],
               'z': [0., .05, .1, .5, .9, 1.], 'r': [0., .5, 1.]}
    observations = observe(trajectory, support)
    assert np.all(np.isnan(observations['liquid'][0]))
    assert np.all(np.isnan(observations['outlet'][:5]))
    assert np.isfinite(observations['outlet'][5:]).all()
    path = tmp_path/'archive'
    save_archive(path, trajectory, {'role': 'bounded software fixture; not campaign'})
    restored, manifest = load_archive(path)
    for seg, original in zip(restored.segments, results):
        np.testing.assert_array_equal(seg['y'], original[1].y)
        for t in (seg['t'][:-1]+seg['t'][1:])/2:
            np.testing.assert_allclose(restored.state(t), original[1].sol(t), atol=2e-13, rtol=0)
    control_model, control = integrate(settings, capture=False, horizon=1.01)
    for (_, result), (_, plain) in zip(results, control):
        np.testing.assert_array_equal(result.t, plain.t)
        np.testing.assert_array_equal(result.y, plain.y)
    t3, integral3 = boundary_quadrature(restored, 3)
    t5, integral5 = boundary_quadrature(restored, 5)
    np.testing.assert_allclose(integral3, integral5, atol=2e-7, rtol=0)
    actual = np.array([restored.state(t)[-2:] for t in t5])
    np.testing.assert_allclose(integral5, actual, atol=2e-6, rtol=0)
    with pytest.raises(FileExistsError):
        save_archive(path, trajectory, {})
    segment = path/'segment-0.npz'
    with segment.open('ab') as stream:
        stream.write(b'corrupt')
    with pytest.raises(ValueError, match='identity'):
        load_archive(path)


def test_independent_saturation_transition_evolution():
    """Constant-flux continuum until c_surface=1, then continuum Robin modes."""
    D, Q, k, initial, liquid = 1., .25, 4., 1.1, .2
    J = Q*k*(1-liquid)
    roots_n = np.array([brentq(lambda x: np.tan(x)-x, n*np.pi+1e-9,
                               (n+.5)*np.pi-1e-9) for n in range(1, 161)])
    def saturated_surface(t):
        return initial-3*J*t-J/(5*D)+2*J/D*np.sum(np.exp(-D*roots_n**2*t)/roots_n**2)
    switch = brentq(lambda t: saturated_surface(t)-1, 1e-4, .1)
    roots_r = np.array([brentq(lambda x: x/np.tan(x)-(1-Q*k/D), n*np.pi+1e-9,
                               (n+1)*np.pi-1e-9) for n in range(160)])
    x, w = np.polynomial.legendre.leggauss(360)
    r, w = (x+1)/2, w/2
    phi_n = np.sinc(np.outer(r, roots_n)/np.pi)
    transition = (initial-3*J*switch+J/D*(.3-r*r/2)
                  +2*J/D*phi_n@(np.exp(-D*roots_n**2*switch)/(roots_n**2*np.cos(roots_n))))
    phi_r = np.sinc(np.outer(r, roots_r)/np.pi)
    norm = (1-np.sin(2*roots_r)/(2*roots_r))/(2*roots_r**2)
    coefficients = ((transition-liquid)*r*r*w)@phi_r/norm
    times = np.array([switch+.002, switch+.01, .05, .1])
    ref_surface = liquid+(np.exp(-np.outer(times-switch,D*roots_r**2))*coefficients)@(np.sin(roots_r)/roots_r)
    errors = []
    for n in (16,32,64):
        sphere = Sphere(n,D,Q,k)
        sol = solve_ivp(lambda t,y:sphere.rhs(y,sphere.transfer(y,liquid)[0]),
                        (0,.1),np.full(n,initial),method='BDF',t_eval=times,
                        rtol=1e-10,atol=1e-12)
        G,surface = sphere.transfer(sol.y.T,liquid)
        errors.append(float(max(abs(surface-ref_surface))))
        assert np.all(surface<1)
        assert np.all(G>0)
    print('SATURATION_TRANSITION', {'t_continuum_switch':switch,'surface_errors':errors})
    assert errors[-1]<errors[-2]<errors[-3]
    assert errors[-1]<3e-4


def test_temporal_controls_meaningful_on_actual_grain_operator():
    from scipy.linalg import expm
    sphere = Sphere(12,.7,.4,2.5)
    liquid=.2
    # Same spatial matrix is appropriate ONLY as a temporal oracle; independent
    # continuum controls above separately verify that spatial operator.
    matrix=np.column_stack([sphere.rhs(np.eye(12)[j],sphere.transfer(np.eye(12)[j],0.)[0])
                            for j in range(12)])
    times=np.array([.0001,.003,.017,.061,.1])
    exact=np.array([liquid+expm(matrix*t)@np.full(12,.6) for t in times])
    errors=[];work=[]
    for rtol in (1e-5,1e-7,1e-9):
        sol=solve_ivp(lambda t,y:sphere.rhs(y,sphere.transfer(y,liquid)[0]),
                      (0,.1),np.full(12,.8),method='BDF',t_eval=times,
                      rtol=rtol,atol=rtol/100)
        errors.append(float(np.max(abs(sol.y.T-exact))))
        work.append(sol.nfev)
    print('TEMPORAL', {'errors':errors,'nfev':work})
    assert errors[-1]<errors[-2]<errors[-3]
    assert work[0]<work[-1]

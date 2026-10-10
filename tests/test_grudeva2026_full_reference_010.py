"""Independent mathematical controls; only bounded fixtures, no horizon-8 case."""
from dataclasses import asdict, replace
import hashlib
import json

from puckworks.analysis import grudeva2026_full_reference_010_io as archive_io

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
    from tools.run_grudeva2026_full_reference_010 import fresh_read, provisional_summary
    checkpoints = tmp_path/'checkpoints'
    archive_io.save_checkpoints(checkpoints, model, results, {'role': 'bounded fixture'})
    fresh_read(checkpoints, 'checkpoint')
    accepted, _ = archive_io.load_checkpoints(checkpoints)
    trajectory = capture(model, results, checkpoints=accepted)
    np.testing.assert_array_equal(results[0][1].y[:, -1], results[1][1].y[:, 0])
    assert results[0][1].y[-1].max() == 0
    support = {'times': [0., 1e-7, .1, .5, .9999, 1., 1.0001, 1.01],
               'z': [0., .05, .1, .5, .9, 1.], 'r': [0., .5, 1.]}
    observations = observe(trajectory, support)
    assert np.all(np.isnan(observations['liquid'][0]))
    assert np.all(np.isnan(observations['outlet'][:5]))
    assert np.isfinite(observations['outlet'][5:]).all()
    path = tmp_path/'archive'
    save_archive(path, trajectory, {'role': 'bounded software fixture; not campaign'},
                 checkpoint_directory=checkpoints)
    fresh_read(path, 'archive')
    restored, manifest = load_archive(path)
    assert (path/'segment-0-y.npy').stat().st_ino == (checkpoints/'segment-0-y.npy').stat().st_ino
    assert provisional_summary(restored) == json.loads((checkpoints/'PROVISIONAL.json').read_text())
    for seg, original in zip(restored.segments, results):
        np.testing.assert_array_equal(seg['y'], original[1].y)
        for t in (seg['t'][:-1]+seg['t'][1:])/2:
            np.testing.assert_allclose(restored.state(t), original[1].sol(t), atol=2e-13, rtol=0)
    # Continuation end-to-end audit consumes independently reloaded states.
    from tools.run_grudeva2026_full_reference_010 import audit
    restored_observations = observe(restored, support)
    for key in observations:
        np.testing.assert_array_equal(observations[key], restored_observations[key])
    stats, diagnostic_arrays = audit(restored, restored_observations)
    assert np.isfinite(stats['balance_independent_max'])
    assert np.isfinite(diagnostic_arrays['native_inventories']).all()
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
    segment = path/'segment-0-y.npy'
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


# Solver-free continuation integrity controls. No new full-case rows in pytest.
@pytest.mark.parametrize('layout', ['C', 'F', 'transpose', 'stride', 'reverse', 'scalar', 'empty'])
def test_chunked_identity_independent_reference(layout, monkeypatch):
    a = np.arange(7*11, dtype=np.float64).reshape(7, 11)
    a[0, 0] = -0.
    a = {'C': a, 'F': np.asfortranarray(a), 'transpose': a.T, 'stride': a[::2, ::3],
         'reverse': a[::-1, ::-1], 'scalar': np.array(-0.), 'empty': a[:0]}[layout]
    monkeypatch.setattr(archive_io, 'CHUNK_BYTES', 32)
    identity = archive_io.array_identity(a)
    assert identity == {'dtype': a.dtype.str, 'shape': list(a.shape),
                        'sha256': hashlib.sha256(a.tobytes(order='C')).hexdigest()}
    assert archive_io.array_identity(np.array([-0.])) != archive_io.array_identity(np.array([0.]))


@pytest.mark.parametrize('layout', ['C', 'transpose', 'stride'])
def test_numeric_roundtrip_layout(tmp_path, layout):
    a = np.arange(99., dtype=np.float64).reshape(9, 11)
    a[0, 0] = -0.
    a = {'C': a, 'transpose': a.T, 'stride': a[::2, ::2]}[layout]
    expected = {'shape': list(a.shape), 'dtype': a.dtype.str,
                'sha256': hashlib.sha256(a.tobytes(order='C')).hexdigest()}
    record = archive_io.write_numeric(tmp_path/'a.npy', a, expected)
    loaded = np.load(tmp_path/'a.npy', allow_pickle=False)
    assert loaded.tobytes(order='C') == a.tobytes(order='C')
    assert archive_io.payload_identity(tmp_path/'a.npy') == expected
    assert record['independently_loaded_payload'] == 'PASS'


def test_source_mutation_during_serialization(tmp_path, monkeypatch):
    a = archive_io.stable_copy(np.arange(20.))
    expected = archive_io.array_identity(a)
    original = np.save
    def mutate(file, array, **kwargs):
        original(file, array, **kwargs)
        array.flags.writeable = True
        array.view(np.uint64)[3] ^= np.uint64(1 << 29)
    monkeypatch.setattr(np, 'save', mutate)
    with pytest.raises(archive_io.CaptureMismatch, match='post_write_source') as caught:
        archive_io.write_numeric(tmp_path/'a.npy', a, expected)
    assert caught.value.record['checks']['source']['identity'] == 'FAIL'
    assert caught.value.record['checks']['source']['finiteness'] == 'PASS'


@pytest.mark.parametrize('condition', ['identity', 'nonfinite', 'both', 'secondary'])
def test_numeric_member_failure_persists_actual_conditions(tmp_path, monkeypatch, condition):
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    value = np.arange(12.).reshape(3, 4)
    expected = archive_io.array_identity(value)
    value[1, 2] = .25 if condition == 'identity' else np.nan
    if condition == 'nonfinite':
        expected = archive_io.array_identity(value)
    path = tmp_path/'segment-1-D.npy'
    if condition == 'secondary':
        def unavailable(*args):
            assert (tmp_path/'failure.json').exists()
            assert (tmp_path/'capture-quarantine/FAILURE.json').exists()
            raise OSError('injected optional scan failure')
        monkeypatch.setattr(archive_io, 'nonfinite_detail', unavailable)
    with pytest.raises(archive_io.CaptureMismatch) as caught:
        archive_io.write_numeric(path, value, expected, {'archive_group': 'segment-1', 'component': 'D'})
    preserve_run_failure(tmp_path, caught.value, {'message': str(caught.value)})
    primary = json.loads((tmp_path/'failure.json').read_text())['numeric_failure']
    saved = json.loads((tmp_path/'capture-quarantine/FAILURE.json').read_text())
    assert primary == saved
    assert saved['path'] == str(path) and saved['member'] == path.name
    assert saved['archive_group'] == 'segment-1' and saved['component'] == 'D'
    source = saved['checks']['source']
    assert source['expected'] == expected
    assert source['observed'] == archive_io.array_identity(value)
    assert source['identity'] == ('PASS' if condition == 'nonfinite' else 'FAIL')
    assert source['finiteness'] == ('PASS' if condition == 'identity' else 'FAIL')
    assert set(saved['failed_conditions']) == {
        'source.'+key for key in ('identity', 'finiteness') if source[key] == 'FAIL'}
    assert not path.exists()
    if condition == 'secondary':
        receipt = json.loads((tmp_path/'capture-quarantine/PRESERVATION.json').read_text())
        assert receipt['status'] == 'PARTIAL_EVIDENCE_WRITE_FAILURE'
        assert 'injected optional scan failure' in receipt['errors'][0]
    else:
        detail = json.loads((tmp_path/'capture-quarantine/numeric-detail-0.json').read_text())
        assert detail['nonfinite_count'] == (0 if condition == 'identity' else 1)
        if condition != 'identity':
            assert detail['first_index'] == [1, 2]
            assert bytes.fromhex(detail['window']['bytes_hex']) == value.tobytes()


@pytest.mark.parametrize('unavailable', ['identity', 'finiteness'])
def test_numeric_primary_check_error_does_not_hide_other_failure(tmp_path, monkeypatch, unavailable):
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    value = np.arange(4.)
    expected = archive_io.array_identity(value)
    value[2] = np.inf
    def fail(*args):
        raise OSError('injected primary check error')
    monkeypatch.setattr(archive_io, 'array_identity' if unavailable == 'identity' else 'finite', fail)
    with pytest.raises(archive_io.CaptureMismatch) as caught:
        archive_io.write_numeric(tmp_path/'segment-1-D.npy', value, expected, {'archive_group': 'segment-1'})
    preserve_run_failure(tmp_path, caught.value, {'message': str(caught.value)})
    saved = json.loads((tmp_path/'failure.json').read_text())['numeric_failure']['checks']['source']
    assert saved[unavailable] == 'ERROR'
    assert saved['finiteness' if unavailable == 'identity' else 'identity'] == 'FAIL'
    assert saved[unavailable+'_error'] == 'OSError: injected primary check error'


def test_numeric_caller_preserves_primary_if_preservation_raises(tmp_path, monkeypatch):
    from tools import run_grudeva2026_full_reference_010 as runner
    value = np.ones(2)
    expected = archive_io.array_identity(value)
    value[0] = np.nan
    def fail(*args):
        assert (tmp_path/'failure.json').exists()
        raise OSError('injected preservation failure')
    monkeypatch.setattr(runner, 'persist_capture_failure', fail)
    with pytest.raises(archive_io.CaptureMismatch) as caught:
        try:
            archive_io.write_numeric(tmp_path/'segment-1-D.npy', value, expected, {'archive_group': 'segment-1'})
        except archive_io.CaptureMismatch as exc:
            runner.preserve_run_failure(tmp_path, exc, {'message': str(exc)})
            raise
    saved = json.loads((tmp_path/'failure.json').read_text())['numeric_failure']
    assert saved == caught.value.record
    assert saved['failed_conditions'] == ['source.identity', 'source.finiteness']
    assert 'injected preservation failure' in (tmp_path/'diagnostic-preservation-error.json').read_text()


def test_numeric_saved_payload_failure_retains_actual_byte_witness(tmp_path, monkeypatch):
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    path = tmp_path/'segment-1-D.npy'
    value = np.arange(12.).reshape(3, 4)
    expected = archive_io.array_identity(value)
    save = np.save
    def damaged_payload(stream, array, **kwargs):
        if stream.name == str(path):
            array = array.copy()
            array[1, 2] = np.nan
        return save(stream, array, **kwargs)
    monkeypatch.setattr(np, 'save', damaged_payload)
    with pytest.raises(archive_io.CaptureMismatch) as caught:
        archive_io.write_numeric(path, value, expected, {'archive_group': 'segment-1'})
    preserve_run_failure(tmp_path, caught.value, {'message': str(caught.value)})
    saved = json.loads((tmp_path/'failure.json').read_text())['numeric_failure']
    assert saved['stage'] == 'saved_payload'
    assert saved['checks']['serialized_payload']['identity'] == 'FAIL'
    assert saved['checks']['loaded_payload']['identity'] == 'FAIL'
    assert saved['checks']['loaded_payload']['finiteness'] == 'FAIL'
    q = tmp_path/'capture-quarantine'
    witness = json.loads((q/'witness-0.json').read_text())
    assert witness['first_index'] == [1, 2]
    retained = np.load(q/'witness-0-target.npy', allow_pickle=False)
    assert retained.dtype == np.uint8
    assert retained.tobytes() == np.load(path, allow_pickle=False).tobytes()
    assert json.loads((q/'PRESERVATION.json').read_text())['status'] == 'PRESERVED'


def test_archive_writer_supplies_exact_member_context(tmp_path, monkeypatch):
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure
    original = archive_io.write_numeric
    def reject(path, value, expected, context=None):
        if path.name == 'segment-0-D.npy':
            value = value.copy()
            value.flat[0] = np.nan
        return original(path, value, expected, context)
    monkeypatch.setattr(archive_io, 'write_numeric', reject)
    with pytest.raises(archive_io.CaptureMismatch) as caught:
        _synthetic_archive(tmp_path)
    preserve_run_failure(tmp_path, caught.value, {'message': str(caught.value)})
    saved = json.loads((tmp_path/'failure.json').read_text())['numeric_failure']
    assert saved['member'] == 'segment-0-D.npy' and saved['archive_group'] == 'segment-0'
    assert saved['archive_role'] == 'trajectory' and saved['component'] == 'D'
    assert not (tmp_path/'archive/manifest.json').exists()


@pytest.mark.parametrize('bad', [np.array([object()], dtype=object), np.array([np.nan]), np.array([np.inf])])
def test_unsafe_or_nonfinite_source_rejected(tmp_path, bad):
    with pytest.raises(ValueError):
        archive_io.write_numeric(tmp_path/'a.npy', bad, archive_io.array_identity(bad))


def _synthetic_archive(tmp_path):
    """Construct state-layout fixture, not a PDE solution or numerical case."""
    from types import SimpleNamespace
    model = Model(Settings(axial=3, fines=3, boulders=3))
    n = model.n*model.width+2
    t = np.array([1., 1.1, 1.2])
    y = np.arange(n*3, dtype=np.float64).reshape(n, 3)/100
    y[0, 0] = -0.
    parts = [SimpleNamespace(order=1, D=np.array([y[:,j+1], np.zeros(n)]),
                             t_shift=np.array([t[j+1]]), denom=np.array([.1])) for j in range(2)]
    result = SimpleNamespace(t=t, y=y, sol=SimpleNamespace(interpolants=parts),
                             success=True, message='synthetic layout only', nfev=0, njev=0, nlu=0)
    trajectory = archive_io.capture(model, [(False, result)])
    path = tmp_path/'archive'
    archive_io.save_archive(path, trajectory, {'role':'solver-free layout fixture'})
    return path, trajectory, result


def test_owned_capture_and_archive_roundtrip(tmp_path):
    path, trajectory, original = _synthetic_archive(tmp_path)
    assert not np.shares_memory(trajectory.segments[0]['y'], original.y)
    assert trajectory.segments[0]['y'].flags.owndata
    assert not trajectory.segments[0]['y'].flags.writeable
    restored, _ = archive_io.load_archive(path)
    assert restored.segments[0]['y'].tobytes() == original.y.tobytes()
    original.y[0, 0] = 9.
    assert trajectory.segments[0]['y'][0, 0] == 0.
    assert np.signbit(trajectory.segments[0]['y'][0, 0])


@pytest.mark.parametrize('failure', ['bit', 'dtype', 'shape', 'order', 'missing', 'incomplete', 'truncated', 'redundant', 'accumulator'])
def test_archive_negative_boundaries(tmp_path, failure):
    path, _, _ = _synthetic_archive(tmp_path)
    manifest = json.loads((path/'manifest.json').read_text())
    key = {'redundant':'concentrations', 'accumulator':'boundary_accumulators'}.get(failure, 'y')
    record = manifest['segments'][0]['arrays'][key]
    target = path/record['file']
    if failure == 'incomplete':
        (path/'manifest.json').unlink()
    elif failure == 'missing':
        target.unlink()
    else:
        a = np.load(target, allow_pickle=False)
        if failure in ('bit', 'redundant', 'accumulator'):
            a.reshape(-1).view(np.uint64)[4] ^= np.uint64(1 << 29)
        elif failure == 'dtype':
            a = a.astype(np.float32)
        elif failure == 'shape':
            a = a.reshape(-1)
        elif failure == 'order':
            a = np.asfortranarray(a)
        np.save(target, a, allow_pickle=False)
        if failure == 'truncated':
            with target.open('r+b') as f: f.truncate(target.stat().st_size-1)
        # Deliberately match the whole-file hash: stale prospective identity must
        # still reject it, independently of byte-level file corruption checking.
        record['sha256'] = archive_io.sha256(target)
        if failure in ('redundant', 'accumulator'):
            # Even a self-consistent payload identity cannot waive relationship checks.
            commitments = json.loads((path/'SOURCE_COMMITMENT.json').read_text())
            record['array'] = commitments['segment-0'][key] = archive_io.array_identity(a)
            (path/'SOURCE_COMMITMENT.json').write_text(json.dumps(commitments))
            manifest['source_commitment_sha256'] = archive_io.sha256(path/'SOURCE_COMMITMENT.json')
        (path/'manifest.json').write_text(json.dumps(manifest))
    with pytest.raises((ValueError, FileNotFoundError)):
        archive_io.load_archive(path)


def test_interrupted_write_has_no_success_manifest(tmp_path, monkeypatch):
    original = archive_io.write_numeric
    calls = []
    def fail(path, a, expected, context=None):
        calls.append(path)
        if len(calls) == 3:
            raise OSError('injected interrupted write')
        return original(path, a, expected, context)
    monkeypatch.setattr(archive_io, 'write_numeric', fail)
    with pytest.raises(OSError, match='interrupted'):
        _synthetic_archive(tmp_path)
    assert (tmp_path/'archive/SOURCE_COMMITMENT.json').exists()
    assert not (tmp_path/'archive/manifest.json').exists()
    with pytest.raises(FileNotFoundError):
        archive_io.load_archive(tmp_path/'archive')


def test_legacy_stale_array_identity_rejected(tmp_path):
    # v1 producer's exact old schema: matching ZIP hash must not mask stale y digest.
    model = Model(Settings(axial=3, fines=3, boulders=3))
    path = tmp_path/'legacy'; path.mkdir()
    a = np.arange(20.)
    expected = archive_io.array_identity(a)
    a.view(np.uint64)[5] ^= np.uint64(1)
    np.savez_compressed(path/'geometry.npz', y=a)
    archive_io.write_json(path/'manifest.json', {
        'schema':'grudeva-full-010-v1', 'case': __import__('dataclasses').asdict(model.case),
        'settings':__import__('dataclasses').asdict(model.settings), 'segments':[],
        'geometry': {'file':'geometry.npz', 'sha256':archive_io.sha256(path/'geometry.npz'),
                     'arrays':{'y':expected}}})
    with pytest.raises(ValueError, match='state identity'):
        archive_io.load_archive(path)


def test_capture_copy_detects_source_mutation(monkeypatch):
    source = np.arange(10.)
    original = np.array
    def mutate(a, *args, **kwargs):
        result = original(a, *args, **kwargs)
        if a is source:
            source[4] += 1.
        return result
    monkeypatch.setattr(np, 'array', mutate)
    with pytest.raises(ValueError, match='Snapshot commitment mismatch'):
        archive_io.stable_copy(source)


def test_no_continuation_means_original_hashes_still_required():
    from tools.run_grudeva2026_full_reference_010 import load_matrix
    with pytest.raises(ValueError, match='Frozen implementation changed'):
        load_matrix()


def test_continuation_cannot_change_solver_or_matrix(tmp_path, monkeypatch):
    from tools import run_grudeva2026_full_reference_010 as runner
    matrix = json.loads((runner.DOC/'MATRIX.json').read_text())
    (tmp_path/'MATRIX.json').write_bytes((runner.DOC/'MATRIX.json').read_bytes())
    binding = {'original_matrix_sha256':runner.ORIGINAL_MATRIX_SHA256,
               'original_implementation':matrix['implementation'],
               'implementation':dict(matrix['implementation']), 'changed_files':list(runner.CONTINUATION_FILES)}
    binding['implementation']['puckworks/analysis/grudeva2026_full_reference_010.py']='0'*64
    (tmp_path/'CONTINUATION.json').write_text(json.dumps(binding))
    monkeypatch.setattr(runner, 'DOC', tmp_path)
    with pytest.raises(ValueError, match='Unapproved continuation file delta'):
        runner.continuation_binding(matrix)
    (tmp_path/'MATRIX.json').write_text('{}')
    with pytest.raises(ValueError, match='Original continuation matrix'):
        runner.continuation_binding(matrix)


def test_saved_row_cannot_trust_completion_label(tmp_path):
    from tools.run_grudeva2026_full_reference_010 import validate_saved_row
    archive_io.write_json(tmp_path/'results.json', {'gates':{'claimed':True}})
    archive_io.write_json(tmp_path/'end.json', {'status':'COMPLETE','results_sha256':'0'*64})
    with pytest.raises(ValueError, match='result/continuation identity'):
        validate_saved_row(tmp_path, {}, None)


def test_later_copy_cannot_mutate_earlier_dense_capture(tmp_path, monkeypatch):
    original_zeros = np.zeros
    original_commit = archive_io._dense_part_commitment
    target = {}
    def track(shape, *args, **kwargs):
        a = original_zeros(shape, *args, **kwargs)
        if isinstance(shape, tuple) and len(shape) == 3:
            target['D'] = a
        return a
    calls = 0
    def mutate(*args):
        nonlocal calls
        calls += 1
        if calls == 2:
            target['D'][0, 0, 4] += .125
        return original_commit(*args)
    monkeypatch.setattr(np, 'zeros', track)
    monkeypatch.setattr(archive_io, '_dense_part_commitment', mutate)
    with pytest.raises(ValueError, match='Dense final commitment mismatch'):
        _synthetic_archive(tmp_path)


@pytest.mark.parametrize('steps', [0, 1])
def test_returned_partial_solver_states_retained_without_success(tmp_path, steps):
    from types import SimpleNamespace
    model = Model(Settings(axial=3, fines=3, boulders=3))
    n = model.n*model.width+2
    t = np.array([1., 1.1])[:steps+1]
    y = np.ones((n, len(t)))
    dense = [SimpleNamespace(order=1, D=np.array([y[:,1], np.zeros(n)]),
                             t_shift=np.array([1.1]), denom=np.array([.1]))] if steps else []
    result = SimpleNamespace(t=t, y=y, sol=SimpleNamespace(interpolants=dense),
                             success=False, message='injected solver failure', nfev=3, njev=1, nlu=1)
    trajectory = capture(model, [(False, result)])
    path = tmp_path/'partial'
    manifest = save_archive(path, trajectory, {'role':'injected partial solver'}, complete=False)
    assert manifest['status'] == 'INCOMPLETE_SOLVER_TRAJECTORY_NOT_QUALIFIED'
    assert (path/'INCOMPLETE_MANIFEST.json').exists()
    assert np.load(path/'segment-0-y.npy', allow_pickle=False).tobytes() == y.tobytes()
    assert not (path/'manifest.json').exists()
    with pytest.raises(FileNotFoundError):
        load_archive(path)


def test_saved_row_rejects_other_valid_row_archive(tmp_path):
    from tools.run_grudeva2026_full_reference_010 import validate_saved_row, ORIGINAL_MATRIX_SHA256
    path, _, _ = _synthetic_archive(tmp_path)
    row = tmp_path/'anchor'; row.mkdir()
    path.rename(row/'trajectory')
    manifest_path = row/'trajectory/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    matrix = {'case':manifest['case'], 'rows':{'anchor':manifest['settings']}, 'implementation':{}}
    manifest['metadata'] = {'row':'fines_coarse', 'implementation':{},
                            'matrix_sha256':ORIGINAL_MATRIX_SHA256, 'continuation_sha256':None}
    manifest_path.write_text(json.dumps(manifest))
    np.savez_compressed(row/'observations.npz', a=np.ones(2))
    np.savez_compressed(row/'diagnostics.npz', a=np.ones(2))
    digest = archive_io.sha256(manifest_path)
    stats = {'continuation_sha256':None,'settings':manifest['settings'],
             'archive':{'manifest_sha256':digest,'observations_sha256':archive_io.sha256(row/'observations.npz'),
                        'diagnostics_sha256':archive_io.sha256(row/'diagnostics.npz')}}
    archive_io.write_json(row/'results.json', stats)
    archive_io.write_json(row/'end.json', {'status':'COMPLETE','continuation_sha256':None,
                    'results_sha256':archive_io.sha256(row/'results.json'), 'archive_manifest_sha256':digest})
    with pytest.raises(ValueError, match='row/case/settings/implementation'):
        validate_saved_row(row, matrix, None, full_archive=False)


@pytest.mark.parametrize('failure', [None, 'source', 'stale', 'bool_bit', 'nan_bit'])
def test_observation_bundle_prospective_identity(tmp_path, monkeypatch, failure):
    from tools import run_grudeva2026_full_reference_010 as runner
    a = np.array([0., -0., np.nan, 1.])
    values = {'values':a, 'available':np.array([True, True, False, True])}
    path = tmp_path/'observations.npz'
    if failure == 'source':
        original = np.savez_compressed
        def mutate(file, **arrays):
            original(file, **arrays)
            a[1] = .125
        monkeypatch.setattr(np, 'savez_compressed', mutate)
        with pytest.raises(ValueError, match='source mutation during serialization'):
            runner.save_bundle(path, values)
        assert path.with_suffix('.source.json').exists()
        return
    record = runner.save_bundle(path, values)
    # Independent reference bytes include NaN payload and signed zero.
    import hashlib
    for key, value in values.items():
        assert record['arrays'][key]['sha256'] == hashlib.sha256(value.tobytes()).hexdigest()
    if failure:
        if failure == 'bool_bit':
            values['available'][0] = False
        else:
            a.view(np.uint64)[2 if failure == 'nan_bit' else 3] ^= np.uint64(1)
        np.savez_compressed(path, **values)
        record['sha256'] = archive_io.sha256(path)
        with pytest.raises(ValueError, match='serialized payload identity'):
            runner.validate_bundle(path, record)
    else:
        runner.validate_bundle(path, record)


def test_checkpoint_rejects_changed_payload_in_fresh_reader(tmp_path):
    import subprocess
    from tools.run_grudeva2026_full_reference_010 import fresh_read
    _, trajectory, result = _synthetic_archive(tmp_path)
    path = tmp_path/'checkpoints'
    archive_io.save_checkpoints(path, trajectory.model, [(False, result)], {})
    with (path/'segment-0-y.npy').open('r+b') as stream:
        stream.seek(-1, 2)
        original = stream.read(1)
        stream.seek(-1, 2)
        stream.write(bytes([original[0] ^ 1]))
    with pytest.raises(subprocess.CalledProcessError):
        fresh_read(path, 'checkpoint')
    assert not (path/'checkpoint-fresh-read.json').exists()


def test_checkpoint_survives_dense_failure(tmp_path, monkeypatch):
    from tools.run_grudeva2026_full_reference_010 import preserve_run_failure, fresh_read
    _, trajectory, result = _synthetic_archive(tmp_path)
    path = tmp_path/'checkpoints'
    archive_io.save_checkpoints(path, trajectory.model, [(False, result)], {})
    fresh_read(path, 'checkpoint')
    accepted, _ = archive_io.load_checkpoints(path)
    def fail(*args, **kwargs):
        raise archive_io.CaptureMismatch('injected dense failure', {'stage': 'dense'}, [])
    monkeypatch.setattr(archive_io, 'capture_dense', fail)
    with pytest.raises(archive_io.CaptureMismatch) as error:
        capture(trajectory.model, [(False, result)], checkpoints=accepted)
    preserve_run_failure(tmp_path, error.value, {'message': str(error.value)})
    assert json.loads((tmp_path/'failure.json').read_text())['message'] == 'injected dense failure'
    assert (path/'PROVISIONAL.json').exists()
    retained, _ = archive_io.load_checkpoints(path)
    assert archive_io.array_identity(retained.segments[0]['y']) == archive_io.array_identity(result.y)
    assert not (path/'manifest.json').exists()


def test_checkpoint_detects_source_change_before_capture(tmp_path):
    _, trajectory, result = _synthetic_archive(tmp_path)
    path = tmp_path/'checkpoints'
    archive_io.save_checkpoints(path, trajectory.model, [(False, result)], {})
    accepted, _ = archive_io.load_checkpoints(path)
    result.y[1, 0] += 1.
    with pytest.raises(archive_io.CaptureMismatch, match='Checkpoint/source'):
        capture(trajectory.model, [(False, result)], checkpoints=accepted)


def test_provisional_evaluation_allowance_separate_from_exact_bytes():
    from tools.run_grudeva2026_full_reference_010 import reconcile_provisional
    assert reconcile_provisional({'mass': 1.}, {'mass': np.nextafter(1., 2.)}) < 1
    with pytest.raises(ValueError, match='numerical summary'):
        reconcile_provisional({'mass': 1.}, {'mass': 1.0001})
    assert archive_io.array_identity(np.array([1.])) != archive_io.array_identity(np.array([np.nextafter(1., 2.)]))


def test_rerun_checkpoints_precede_failed_solver_dense_capture(tmp_path, monkeypatch):
    import tools.run_grudeva2026_full_reference_010 as runner
    _, trajectory, result = _synthetic_archive(tmp_path)
    result.success = False
    matrix = {'rows': {'anchor': asdict(trajectory.model.settings)}}
    monkeypatch.setattr(runner, 'load_matrix', lambda *a: matrix)
    monkeypatch.setattr(runner, 'rerun_binding', lambda *a: {})
    monkeypatch.setattr(runner, 'admit_rerun_row', lambda *a: None)
    monkeypatch.setattr(runner, 'integrate', lambda *a: (trajectory.model, [(False, result)]))
    monkeypatch.setattr(runner, 'resources', lambda: {'available_bytes': 200*1024**3})
    output = tmp_path/'campaign'/'anchor'
    def fail(*args, **kwargs):
        assert (output/'checkpoints/PROVISIONAL.json').exists()
        assert (output/'checkpoints/checkpoint-fresh-read.json').exists()
        raise archive_io.CaptureMismatch('injected failed-solver capture', {'stage': 'dense'}, [])
    monkeypatch.setattr(runner, 'capture', fail)
    with pytest.raises(archive_io.CaptureMismatch):
        runner.run_row(tmp_path/'campaign', 'anchor', rerun=True)
    assert json.loads((output/'solver-end.json').read_text())['status'] == 'FAILED'
    assert (output/'failure.json').exists()
    archive_io.load_checkpoints(output/'checkpoints')


def test_rerun_binding_rejects_order_and_scientific_change(tmp_path, monkeypatch):
    import tools.run_grudeva2026_full_reference_010 as runner
    matrix_path = runner.DOC/'MATRIX.json'
    matrix = json.loads(matrix_path.read_text())
    (tmp_path/'MATRIX.json').write_bytes(matrix_path.read_bytes())
    monkeypatch.setattr(runner, 'DOC', tmp_path)
    binding = {'authorization': 'OWNER AUTHORIZATION — CONTROLLED SCIENTIFIC RERUN / MODEL-GRUDEVA2026-FULL-REFERENCE-010',
               'original_matrix_sha256': runner.ORIGINAL_MATRIX_SHA256,
               'original_implementation': matrix['implementation'],
               'implementation': {p: archive_io.sha256(runner.ROOT/p) for p in runner.FILES},
               'changed_files': sorted(runner.CONTINUATION_FILES), 'row_order': matrix['row_order']}
    (tmp_path/'RERUN.json').write_text(json.dumps(binding))
    with pytest.raises(ValueError, match='execution order'):
        runner.rerun_binding(matrix)
    binding['implementation'][runner.FILES[1]] = 'changed'
    (tmp_path/'RERUN.json').write_text(json.dumps(binding))
    with pytest.raises(ValueError, match='source scope'):
        runner.rerun_binding(matrix)

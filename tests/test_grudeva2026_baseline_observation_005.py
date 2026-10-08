"""Independent compact fixtures; no full production trajectory is executed."""
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.integrate._ivp.bdf import BdfDenseOutput
from scipy.integrate._ivp.common import OdeSolution

from puckworks.analysis import grudeva2026_baseline_observation_005 as obs


def test_seam_arguments_multiple_segments_identity_failure_and_restoration():
    calls, returned = [], [object(), object()]
    args = (object(), (0., 1.), np.array([1., 2.]))
    kwargs = dict(method='BDF', events=(object(),), rtol=2e-8, dense_output=True)
    def original(*a, **k):
        calls.append((a, k))
        return returned[len(calls)-1]
    module = SimpleNamespace(solve_ivp=original)
    with obs.capture_returns(module) as captured:
        for expected in returned:
            assert module.solve_ivp(*args, **kwargs) is expected
    assert module.solve_ivp is original
    assert len(calls) == len(captured) == 2
    for a, k in calls:
        assert all(x is y for x, y in zip(a, args))
        assert k.keys() == kwargs.keys()
        assert all(k[key] is kwargs[key] for key in k)
    assert [x['solution'] for x in captured] == returned
    error = RuntimeError('original exception')
    def failed(*a, **k):
        raise error
    module.solve_ivp = failed
    with pytest.raises(RuntimeError) as caught:
        with obs.capture_returns(module) as captured:
            module.solve_ivp(*args, **kwargs)
    assert caught.value is error and module.solve_ivp is failed
    assert captured[0]['solution'] is None
    with pytest.raises(KeyError):
        with obs.capture_returns(module):
            raise KeyError('outside solver')
    assert module.solve_ivp is failed


@pytest.mark.parametrize('s', [.0001, .13, 1.])
@pytest.mark.parametrize('degree', [0, 1, 2])
def test_cell_averages_are_not_points_and_quadratic_integral_constraints(s, degree):
    faces = s*(1-(1-np.arange(9)/8)**2)
    left, right = faces[:-1], faces[1:]
    averages = (right**(degree+1)-left**(degree+1))/((degree+1)*(right-left))
    z = np.r_[0., (left+right)/2, s]
    actual = obs.cell_reconstruction(faces, averages, z)
    assert np.max(abs(actual-z**degree)) < obs.ALGEBRA*4
    # Independent Gauss integration on each cell recovers its supplied average.
    q = 1/np.sqrt(3)
    values = obs.cell_reconstruction(faces, averages, np.ravel(
        np.column_stack(((left+right)/2-q*(right-left)/2, (left+right)/2+q*(right-left)/2))))
    assert np.max(abs(values.reshape(-1, 2).mean(axis=1)-averages)) < obs.ALGEBRA*4
    if degree == 2:
        assert np.max(abs(averages-((left+right)/2)**2)) > s*s*1e-4


def finite_mode(age, rates, initial=1.388, b0=.07, a=.1, b=.02):
    age = np.asarray(age)
    rate = rates[:, None]
    A = initial-b0+a/rate-2*b/rate**2
    B = b0-a/rate+2*b/rate**2
    C = a-2*b/rate
    return A*np.exp(-rate*age)+B+C*age+b*age**2


def finite_primitive(age, rates, initial=1.388, b0=.07, a=.1, b=.02):
    rate = rates[:, None]
    A = initial-b0+a/rate-2*b/rate**2
    B = b0-a/rate+2*b/rate**2
    C = a-2*b/rate
    return -A/rate*np.exp(-rate*age)+B*age+C*age**2/2+b*age**3/3


def test_fixed_position_time_varying_modal_field_activation_endpoints_and_negative_control():
    rates = np.array([1., 3., 8.])
    weights = np.array([.5, .3, .2])
    xi = 1-(1-np.arange(129)/128)**2
    worst, wrong = 0., 0.
    for t in [.01, .1, .4, 2., 4.9, 5., 5.02, 6., 8.]:
        s, speed = min(.2*t, 1.), .2
        faces = s*xi
        age0, age1 = t-faces[:-1]/speed, t-faces[1:]/speed
        averages = speed*(finite_primitive(age0, rates)-finite_primitive(age1, rates))/np.diff(faces)
        # Fixed positions, plus inlet and near the newly activated front.
        z = np.unique(np.r_[0., np.asarray(obs.HISTORY_Z)[np.asarray(obs.HISTORY_Z) <= s], s, .999*s])
        observed = obs.cell_reconstruction(faces, averages, z)
        expected = finite_mode(t-z/speed, rates)
        worst = max(worst, float(np.max(abs(weights @ (observed-expected)))))
        if s >= .25:
            correct = float(weights @ finite_mode([t-.25/speed], rates)[:, 0])
            wrong = max(wrong, abs(float(weights @ averages[:, 32])-correct))
        assert np.allclose(finite_mode([0.], rates), 1.388, atol=2e-14, rtol=0)
    assert worst < 2e-5, worst
    assert wrong > .01  # following a moving cell index is observably wrong
    # C(0,t)=0 inlet oracle, independently integrated finite relaxation equation.
    for t in [.01, .1, .4]:
        expected = 1.388*np.exp(-rates*t)
        assert np.max(abs(finite_mode([t], rates, b0=0., a=0., b=0.)[:, 0]-expected)) == 0


def test_inventory_modal_axis_tail_and_no_complement_or_empty_volume():
    n, m = 8, 3
    faces = 1-(1-np.arange(n+1)/n)**2
    weights = np.array([.6, .3, .1])
    liquid = np.arange(n)/10
    modal = np.arange(m*n).reshape(m, n)/30
    y = np.r_[.4, liquid, modal.ravel(), 123.]  # cup cannot influence any phase
    phase, audit = obs.inventory(.8, y, n, weights, faces)
    ic = sum(.4*(faces[j+1]-faces[j])*liquid[j] for j in range(n))
    ib = sum(.4*(faces[j+1]-faces[j])*sum(weights[k]*modal[k, j] for k in range(m)) for j in range(n))
    assert phase == pytest.approx([ic+.4, 3.2*(ic+1.388*.6), .8*(ib+1.388*.6)], abs=1e-14)
    assert audit['sum_error'] <= audit['sum_allowance']
    assert audit['modal_inventory_contributions'][-1] > 0
    y[0] = 0
    phase, _ = obs.inventory(0., y, n, weights, faces)
    assert phase == pytest.approx([0., 3.2*1.388, .8*1.388])
    cp, bp, modes = obs.profiles(0., y, n, weights, faces, np.array([0., .1, 1.]), None)
    assert cp.tolist() == [0., 0., 0.]
    assert bp == pytest.approx([1.388]*3)
    assert np.all(modes == 1.388)


@pytest.mark.parametrize('modes', [32, 64])
def test_actual_tail_and_positive_age_analytical_spherical_response(modes):
    from puckworks.models.grudeva2026.kernel import modal_spectrum, spherical_history
    from puckworks.analysis.grudeva2026_reference_002 import analytic_sphere
    w, rates = modal_spectrum(.7, modes)
    audit = obs.spectrum_audit(w, rates, .7)
    assert audit['weight_error'] <= audit['allowance']
    assert audit['rate_relative_error'] <= audit['allowance']
    ages = np.array([0., .002, .02, .1, .3, .7])
    for initial, boundary, slope in [(1.6, .2, 0.), (1.6, .2, .3), (.2, .2, .5), (1.4, 1.4, 0.)]:
        a = spherical_history(ages+4.3, boundary+slope*ages, initial, diffusivity=.7, q_b=.4, modes=modes)
        b = spherical_history(ages+15.3, boundary+slope*ages, initial, diffusivity=.7, q_b=.4, modes=modes)
        for j, age in enumerate(ages[1:], 1):
            flux, mean = analytic_sphere(age, initial, boundary, slope, diffusivity=.7, q_b=.4)
            assert abs(a['mean'][j]-mean) <= 2e-5
            assert abs(a['flux'][j]-flux) <= 2e-4
            assert abs(a['mean'][j]-b['mean'][j]) < 1e-12
        if initial == boundary and slope > 0:
            assert a['flux'][-1] < 0


def dense_fixture():
    ts = np.array([0., .4, .8])
    polynomials = []
    for a, b in [(0., .4), (.4, 1.)]:  # underlying final polynomial extends beyond event
        h = b-a
        D = np.array([[b*b, 2*b*b], [2*b*h-h*h, 2*(2*b*h-h*h)], [2*h*h, 4*h*h]])
        polynomials.append(BdfDenseOutput(a, b, h, 2, D))
    sol = OdeSolution(ts, polynomials, alt_segment=True)
    return SimpleNamespace(t=ts, y=np.array([ts**2, 2*ts**2]), sol=sol, success=True,
                           status=1, message='terminal event', nfev=0, njev=0, nlu=0,
                           t_events=[np.array([.8])], y_events=[np.array([[.64, 1.28]])])


def test_dense_serialization_replay_interiors_accepted_event_limits_and_censoring(tmp_path):
    live = dense_fixture()
    meta = obs.save_segment(tmp_path, 'segment.npz', dict(solution=live,
                            requested_interval=[0., 1.], fixed=False, dripping=False), 2)
    segment = obs.Segment(tmp_path, meta, 2)
    assert meta['live_replay']['allowance_fraction'] <= 1
    for t in [0., .13, .4, .6, np.nextafter(.8, 0.), .8]:
        assert segment.evaluate(t) == pytest.approx([t*t, 2*t*t], abs=1e-14)
    with pytest.raises(ValueError, match='outside'):
        segment.evaluate(np.nextafter(.8, 1.))
    segment.close()
    (tmp_path/'segment.npz').write_bytes(b'corrupt')
    with pytest.raises(ValueError, match='identity'):
        obs.Segment(tmp_path, meta, 2)


def test_piecewise_event_split_cup_integrals_use_actual_trace():
    faces = np.linspace(0., 1., 9)
    class Fixture:
        horizon = 4.
        arrival = 2.
        n = 8
        segments = [SimpleNamespace(breaks=np.array([0., .7, 1.])),
                    SimpleNamespace(breaks=np.array([1., 1.8, 2.])),
                    SimpleNamespace(breaks=np.array([2., 2.7, 4.]))]
        def evaluate(self, t):
            # Spatially constant, time-curved trace with exact primitive.
            return np.r_[1., np.full(8, (t-2)**2), np.zeros(8), 0.], {}
    f = Fixture()
    f.faces = faces
    times = np.array([0., .8, 1., 1.5, 2., 2.3, 4.])
    expected = [0., 0., 0., .5, 1., 1.+.3**3/3, 1.+8/3]
    assert obs.cup_integral(f, times, 4) == pytest.approx(expected, abs=2e-14)
    assert obs.cup_integral(f, times, 8) == pytest.approx(expected, abs=2e-14)
    with pytest.raises(ValueError):
        obs.cup_integral(f, [4.1], 4)


@pytest.mark.parametrize('content', ['{"x":NaN}', '{"x":1e999}'])
def test_nonfinite_json_rejected(tmp_path, content):
    path = tmp_path/'invalid.json'
    path.write_text(content)
    with pytest.raises(ValueError):
        obs.read_json(path)


def test_event_provenance_remains_distinct_at_identical_times():
    trajectory = obs.Trajectory.__new__(obs.Trajectory)
    trajectory.segments = [SimpleNamespace(t=[0., 1.], meta={'fixed': False}, evaluate=lambda t: np.array([t])),
                           SimpleNamespace(t=[1., 2.], meta={'fixed': True}, evaluate=lambda t: np.array([t]))]
    assert not trajectory.evaluate(1., side='left')[1]['fixed']
    assert trajectory.evaluate(1., side='right')[1]['fixed']
    with pytest.raises(ValueError, match='outside'):
        trajectory.evaluate(2.01)
    with pytest.raises(ValueError, match='left/right'):
        trajectory.evaluate(1., side='nearest')


def test_requested_time_cannot_manufacture_missing_physical_split():
    fixture = SimpleNamespace(horizon=2., arrival=None, segments=[SimpleNamespace(breaks=np.array([0., 2.]))])
    with pytest.raises(ValueError, match='first-drip'):
        obs.cup_integral(fixture, [0., 1., 2.], 4)


def test_returned_verification_failure_keeps_complete_result(tmp_path, monkeypatch):
    from puckworks.models.grudeva2026 import reduced
    from dataclasses import asdict
    result = reduced.Result('NUMERICAL_VERIFICATION_FAILED', asdict(reduced.Parameters()), obs.controls('normal'),
                            diagnostics={'synthetic': 'returned diagnostics retained'},
                            unavailable_reasons={'conservation': 'synthetic exceeded allowance'})
    monkeypatch.setattr(reduced, 'simulate', lambda **kwargs: result)
    path = tmp_path/'failed.json'
    payload = obs.execute(path)
    assert payload['public_result'] == result.to_dict()
    assert payload['public_result']['status'] == 'NUMERICAL_VERIFICATION_FAILED'
    assert payload['restored']
    with pytest.raises((KeyError, ValueError)):
        obs.Trajectory(path)  # empty synthetic support cannot qualify


def qualification_evidence():
    """Retain actual/independent expected numbers for failure-first offline reduction."""
    from puckworks.models.grudeva2026.kernel import spherical_history
    from puckworks.analysis.grudeva2026_reference_002 import analytic_sphere
    import tempfile
    from pathlib import Path
    fixtures = {}
    actual, expected = [], []
    for s in [.0001, .13, 1.]:
        f = s*(1-(1-np.arange(9)/8)**2)
        z = np.r_[0., (f[1:]+f[:-1])/2, s]
        for d in range(3):
            averages = (f[1:]**(d+1)-f[:-1]**(d+1))/((d+1)*np.diff(f))
            actual.extend(obs.cell_reconstruction(f, averages, z).tolist())
            expected.extend((z**d).tolist())
    fixtures['polynomial'] = dict(actual=actual, expected=expected)
    actual, expected, wrong = [], [], 0.
    rates, w = np.array([1., 3., 8.]), np.array([.5, .3, .2])
    for t in [.01, .1, .4, 2., 4.9, 5., 5.02, 6., 8.]:
        s = min(.2*t, 1.)
        f = s*(1-(1-np.arange(129)/128)**2)
        means = .2*(finite_primitive(t-f[:-1]/.2, rates)-finite_primitive(t-f[1:]/.2, rates))/np.diff(f)
        z = np.unique(np.r_[0., np.asarray(obs.HISTORY_Z)[np.asarray(obs.HISTORY_Z) <= s], s, .999*s])
        actual.extend((w @ obs.cell_reconstruction(f, means, z)).tolist())
        expected.extend((w @ finite_mode(t-z/.2, rates)).tolist())
        if s >= .25:
            wrong = max(wrong, abs(float(w @ means[:, 32])-float(w @ finite_mode([t-.25/.2], rates)[:, 0])))
    fixtures['history'] = dict(actual=actual, expected=expected)
    ages = np.array([0., .002, .02, .1, .3, .7])
    for modes in [32, 64]:
        mean, flux, expected_mean, expected_flux = [], [], [], []
        for initial, boundary, slope in [(1.6, .2, 0.), (1.6, .2, .3), (.2, .2, .5), (1.4, 1.4, 0.)]:
            r = spherical_history(ages+4.3, boundary+slope*ages, initial, diffusivity=.7, q_b=.4, modes=modes)
            mean.extend(r['mean'][1:]); flux.extend(r['flux'][1:])
            for age in ages[1:]:
                ef, em = analytic_sphere(age, initial, boundary, slope, diffusivity=.7, q_b=.4)
                expected_mean.append(em); expected_flux.append(ef)
        fixtures[f'kernel_mean_{modes}'] = dict(actual=mean, expected=expected_mean)
        fixtures[f'kernel_flux_{modes}'] = dict(actual=flux, expected=expected_flux)
    with tempfile.TemporaryDirectory() as directory:
        meta = obs.save_segment(Path(directory), 'fixture.npz', dict(solution=dense_fixture(),
                                requested_interval=[0., 1.], fixed=False, dripping=False), 2)
        segment = obs.Segment(directory, meta, 2)
        actual, expected = [], []
        for t in [0., .13, .4, .6, np.nextafter(.8, 0.), .8]:
            actual.extend(segment.evaluate(t).tolist()); expected.extend([t*t, 2*t*t])
        segment.close()
    fixtures['dense'] = dict(actual=actual, expected=expected)
    class Cup:
        horizon, arrival, n = 4., 2., 8
        faces = np.linspace(0., 1., 9)
        segments = [SimpleNamespace(breaks=np.array([0., .7, 1.])),
                    SimpleNamespace(breaks=np.array([1., 1.8, 2.])),
                    SimpleNamespace(breaks=np.array([2., 2.7, 4.]))]
        def evaluate(self, t):
            return np.r_[1., np.full(8, (t-2)**2), np.zeros(8), 0.], {}
    times = [0., .8, 1., 1.5, 2., 2.3, 4.]
    fixtures['cup'] = dict(actual=np.r_[obs.cup_integral(Cup(), times, 4), obs.cup_integral(Cup(), times, 8)].tolist(),
                           expected=[0., 0., 0., .5, 1., 1.+.3**3/3, 1.+8/3]*2)
    return dict(sources=obs.sources(), fixture_source_sha256=obs.sha(__file__), fixtures=fixtures,
                negative_control_error=wrong, physical_validation='NOT_ESTABLISHED')


@pytest.mark.parametrize('damage', ['nonfinite', 'shape', 'monotonicity'])
def test_dense_payload_validation_beyond_file_hash(tmp_path, damage):
    live = dense_fixture()
    meta = obs.save_segment(tmp_path, 'bad.npz', dict(solution=live, requested_interval=[0., 1.],
                            fixed=False, dripping=False), 2)
    path = tmp_path/'bad.npz'
    with np.load(path, allow_pickle=False) as data:
        arrays = {k: data[k] for k in data.files}
    if damage == 'nonfinite':
        arrays['D_0'][0, 0] = np.nan
    elif damage == 'shape':
        arrays['accepted_y'] = arrays['accepted_y'][:1]
    else:
        arrays['breaks'][1] = arrays['breaks'][0]
    np.savez(path, **arrays)
    meta['sha256'] = obs.sha(path)
    with pytest.raises(ValueError):
        obs.Segment(tmp_path, meta, 2)


def test_missing_dense_output_retains_failed_solver_states_and_diagnostics(tmp_path):
    live = dense_fixture()
    live.sol, live.success, live.status, live.message = None, False, -1, 'synthetic solver failure'
    meta = obs.save_segment(tmp_path, 'failed.npz', dict(solution=live, requested_interval=[0., 1.],
                            fixed=False, dripping=False), 2)
    assert not meta['success'] and meta['message'] == 'synthetic solver failure'
    assert 'no dense output' in meta['unavailable_reason']
    with np.load(tmp_path/'failed.npz', allow_pickle=False) as raw:
        assert np.array_equal(raw['accepted_y'], live.y)
        assert np.array_equal(raw['event_y_0'], live.y_events[0])

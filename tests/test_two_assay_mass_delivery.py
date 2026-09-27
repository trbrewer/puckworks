"""Deterministic synthetic verification; no private corpus required."""
from dataclasses import asdict, replace
import copy

import numpy as np
import pytest
from scipy.integrate import quad

from puckworks.analysis import two_assay_mass_delivery as md


def base(empirical=False, p=.8327267294693588):
    return md.FrozenBase.from_model(md.kernel.Model('synthetic',
        'BOUNDARY_AWARE_EMPIRICAL' if empirical else 'MASS',
        (.3, .12, .15, .03) if empirical else (.24, 70., p), (0., .06),
        {'kind': 'SYNTHETIC_NO_SOURCE_DATA'}, 'first-party synthetic fixture',
        knots_kg=(0., .012, .025, .06) if empirical else ()))


def pair(q1, q2):
    p = md.synthetic_pair()
    return md.ObservationPair(replace(p.first, tds_percent=q1*100),
                              replace(p.second, tds_percent=q2*100))


@pytest.mark.parametrize('p,arm', [(.8327267294693588, md.ARMS[0]), (1., md.ARMS[1])])
@pytest.mark.parametrize('A,k', [(.2, 60.), (.8, 4.), (.3, 800.), (.02, .001)])
def test_exact_interval_recovery_and_independent_future(p, arm, A, k):
    state = md.FittedState(base(p=p), md.synthetic_pair(p, A, k), arm)
    d = state.diagnostics
    assert d['A'] == pytest.approx(A, rel=2e-10)
    assert d['k'] == pytest.approx(k, rel=2e-7)
    assert d['A_bounds'][0] <= A <= d['A_bounds'][1]
    assert d['k_bounds'][0] <= k <= d['k_bounds'][1]
    assert len(d['attempts']) == 2
    pred = state.predict_intervals((md.IntervalQuery(.009, .037),))[0]
    independent, _ = quad(lambda b: A*np.exp(-(k*b)**p), .009, .037, epsabs=1e-14)
    assert abs(pred.solute_kg-independent) <= pred.numerical_allowance_kg
    assert pred.numerical_allowance_kg <= 1e-9


def test_origin_and_interval_fit_not_midpoint():
    p, A, k = .8327267294693588, .3, 80.
    original = md.synthetic_pair(p, A, k)
    observations = []
    for o, a, b in ((original.first, .002, .007), (original.second, .009, .02)):
        value = 100*A*md.shape_average(a, b, (k*.01)**p, p, 'reference')
        observations.append(replace(o, start_kg=a, end_kg=b, tds_percent=value))
    state = md.FittedState(base(), md.ObservationPair(*observations))
    assert state.diagnostics['k'] == pytest.approx(k, rel=1e-10)
    mid = A*np.exp(-(k*(.009+.02)/2)**p)
    assert abs(mid-observations[1].q) > .001


def test_monotonicity_and_log_derivative():
    pair = md.synthetic_pair()
    for p in (.8327267294693588, 1.):
        values = [md.ratio(pair, x, p) for x in (0., .1, 1., 10., 40.)]
        assert all(a > b for a, b in zip(values, values[1:]))
        lam, step = .6, 1e-5
        means = [-md.shape_derivative(o.start_kg, o.end_kg, lam, p)/
                 md.shape_average(o.start_kg, o.end_kg, lam, p) for o in (pair.first, pair.second)]
        fd = (np.log(md.ratio(pair, lam+step, p))-np.log(md.ratio(pair, lam-step, p)))/(2*step)
        assert fd == pytest.approx(means[0]-means[1], rel=1e-8)


@pytest.mark.parametrize('q1,q2', [(0., .1), (.1, .2), (.1, 0.)])
def test_incompatible_pairs(q1, q2):
    with pytest.raises(md.FitFailure, match='SCIENTIFICALLY_INCOMPATIBLE'):
        md.FittedState(base(), pair(q1, q2))


def test_constant_zero_and_unit_limits():
    for q in (0., .12, 1.):
        state = md.FittedState(base(), pair(q, q))
        pred = state.remaining_solute(.03)
        assert pred.solute_kg == pytest.approx(q*(.03-.008), abs=1e-18)
        assert state.diagnostics['k'] == (None if q == 0 else 0.)
        assert pred.tds_sensitivity_pp_per_pp is None if q == 0 else pred.tds_sensitivity_pp_per_pp is not None
    assert 'SINGULAR' in md.FittedState(base(), pair(0., 0.)).diagnostics['jacobian_status']
    assert 'NONREGULAR' in md.FittedState(base(), pair(.1, .1)).diagnostics['jacobian_status']


def test_no_finite_bracket_and_amplitude_bound():
    with pytest.raises(md.FitFailure, match='RATE_CEILING') as fail:
        md.FittedState(base(), pair(.1, 1e-200))
    assert len(fail.value.attempts) == 1
    assert fail.value.attempts[0]['initial_bracket_lambda'][1] == (10000*.01)**.8327267294693588
    with pytest.raises(md.FitFailure, match='A_EXCEEDS_ONE'):
        md.FittedState(base(), pair(.99, .01))


def test_near_equality_is_not_assay_tolerance():
    state = md.FittedState(base(), pair(.1, .1-1e-8))
    assert state.diagnostics['k'] > 0
    assert state.diagnostics['status'] == 'QUALIFIED'


@pytest.mark.parametrize('arm', md.ARMS)
def test_sensitivities_finite_difference_and_immutable_roundtrip(arm):
    b = base(empirical=arm in md.ARMS[3:])
    obs = md.synthetic_pair(p=1. if arm == md.ARMS[1] else .8327267294693588)
    state = md.FittedState(b, obs, arm)
    query = (md.IntervalQuery(.015, .029),)
    pred = state.predict_intervals(query)[0]
    for j in range(2):
        values = []
        for sign in (-1, 1):
            entries = [obs.first, obs.second]
            entries[j] = replace(entries[j], tds_percent=entries[j].tds_percent+sign*1e-4)
            other = md.FittedState(b, md.ObservationPair(*entries), arm)
            values.append(other.predict_intervals(query)[0].tds_percent)
        assert (values[1]-values[0])/2e-4 == pytest.approx(pred.tds_sensitivity_pp_per_pp[j], rel=2e-6, abs=1e-9)
    serialized = state.to_dict()
    assert md.FittedState.from_dict(serialized).to_dict() == serialized
    changed = copy.deepcopy(serialized)
    changed['diagnostics']['status'] = 'FORGED'
    with pytest.raises(ValueError, match='DERIVED_FIELDS'):
        md.FittedState.from_dict(changed)
    changed = copy.deepcopy(serialized)
    changed['producer_modules']['mass_delivery.py'] = '0'*64
    with pytest.raises(ValueError, match='PRODUCER_IDENTITY'):
        md.FittedState.from_dict(changed)
    changed = copy.deepcopy(serialized)
    changed['base']['sha256'] = '0'*64
    with pytest.raises(ValueError):
        md.FittedState.from_dict(changed)


def test_two_parameter_jacobian():
    state = md.FittedState(base(), md.synthetic_pair())
    d = state.diagnostics
    j = np.array(d['jacobian_q_by_A_lambda'])
    jk = np.array(d['jacobian_q_by_A_k'])
    for row, o in enumerate((state.observations.first, state.observations.second)):
        delta = 1e-5
        fn = lambda x: d['A']*md.shape_average(o.start_kg,o.end_kg,x,d['p'])
        assert j[row, 1] == pytest.approx((fn(d['lambda']+delta)-fn(d['lambda']-delta))/(2*delta), rel=1e-8)
        assert jk[row, 1] == pytest.approx(j[row, 1]*d['p']*.01*(d['k']*.01)**(d['p']-1))


def test_fixed_shape_formula_and_exact_legacy_parity():
    obs = md.synthetic_pair()
    b = base(True)
    g = [md.legacy.integral(b.curve(), o.start_kg, o.end_kg)[0]/o.width for o in (obs.first,obs.second)]
    state = md.FittedState(b, obs, md.ARMS[3])
    expected = sum(o.width*x*o.q for o,x in zip((obs.first,obs.second),g))/sum(o.width*x*x for o,x in zip((obs.first,obs.second),g))
    assert state.diagnostics['alpha'] == expected
    second = md.FittedState(b, obs, md.ARMS[4])
    assert second.diagnostics['alpha'] == pytest.approx(obs.second.q/g[1], abs=1e-15)
    first = md.FittedState(b, obs, md.ARMS[5])
    legacy = md.legacy_state(b,obs)
    q = (md.IntervalQuery(.012,.04),)
    x,y = first.predict_intervals(q)[0],legacy.predict_intervals(q)[0]
    assert (x.solute_kg,x.numerical_allowance_kg,x.tds_percent)==(y.solute_kg,y.numerical_allowance_kg,y.tds_percent)


@pytest.mark.parametrize('field,value', [('tds_percent',True),('tds_percent',float('nan')),
    ('start_kg',False),('end_kg',float('inf')),('tds_unit','kg/kg'),('tds_basis','VOLUME'),
    ('mass_basis','g'),('input_class','SCORING_ONLY'),('rights',''),('fraction_id',True),('fraction_id',3)])
def test_invalid_observation(field,value):
    with pytest.raises(ValueError):
        replace(md.synthetic_pair().first, **{field:value})


def test_pair_identity_queries_and_strict_json():
    p=md.synthetic_pair()
    for other in (p.first,replace(p.second,source_id='wrong'),replace(p.second,shot_id='wrong'),
                  replace(p.second,start_kg=.001),replace(p.second,rights='wrong')):
        with pytest.raises(ValueError): md.ObservationPair(p.first,other)
    with pytest.raises(ValueError): md.ObservationPair(p.second,p.first)
    with pytest.raises(ValueError): md.ObservationPair.from_dict({**asdict(p),'later_tds':3})
    state=md.FittedState(base(),p)
    for query in (md.IntervalQuery(0,.004),md.IntervalQuery(.06,.061),{'start_kg':.01,'end_kg':.02}):
        with pytest.raises(ValueError): state.predict_intervals((query,))
    assert state.predict_intervals((md.IntervalQuery(.01,.01),))[0].tds_percent is None
    for text in ('{"x":1,"x":2}','{"x":NaN}'):
        with pytest.raises(ValueError): md.strict_json(text)
    with pytest.raises(ValueError,match='SOURCE_FRACTION_ONE'):
        md.legacy.AnchorInput(**{**asdict(p.second),'input_class':'SYNTHETIC_ANCHOR_INPUT'})


def test_numerical_failure_is_not_fit_rescue(monkeypatch):
    original=md.qualified_average
    monkeypatch.setattr(md,'qualified_average',lambda *a:(original(*a)[0],.1))
    with pytest.raises(md.FitFailure,match='NUMERICALLY_UNRESOLVED') as fail:
        md.FittedState(base(),md.synthetic_pair())
    assert len(fail.value.attempts)==2


def test_propagated_error_includes_inversion_interval():
    state=md.FittedState(base(),md.synthetic_pair())
    pred=state.remaining_solute(.06)
    d=state.diagnostics
    integral_error=md.qualified_average(.008,.06,d['lambda'],d['p'])[1]*d['A']*.052
    assert pred.numerical_allowance_kg>integral_error
    assert d['A_bounds'][1]>d['A_bounds'][0]


def test_ill_conditioned_pair_can_terminate_but_not_qualify_forecast():
    original=md.synthetic_pair()
    observations=[]
    for o,a,b in ((original.first,.03,.030000000001),
                  (original.second,.030000000001,.030000000002)):
        observations.append(replace(o,start_kg=a,end_kg=b,
            tds_percent=20*md.shape_average(a,b,.6**.8327267294693588,.8327267294693588,'reference')))
    state=md.FittedState(base(),md.ObservationPair(*observations))
    assert state.diagnostics['jacobian_condition_number']>1e10
    assert all(a['status']=='CONVERGED' for a in state.diagnostics['attempts'])
    with pytest.raises(ValueError,match='PROPAGATED_PREDICTION'):
        state.remaining_solute(.06)


def test_exact_rate_ceiling_retains_numerical_boundary_status():
    obs=md.synthetic_pair(p=1.,A=.2,k=md.K_MAX)
    try:
        state=md.FittedState(base(p=1.),obs,md.ARMS[1])
        assert state.diagnostics['k']<=md.K_MAX
    except md.FitFailure as exc:
        assert exc.status.startswith('NUMERICALLY_UNRESOLVED')
        assert exc.attempts

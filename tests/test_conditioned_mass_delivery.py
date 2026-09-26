"""Offline synthetic checks: no restricted source or target chemistry in tests."""
from dataclasses import replace
import json
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.integrate import quad

from puckworks.analysis import conditioned_mass_delivery as md
from puckworks.analysis import mass_delivery as old_kernel
from puckworks.analysis import pannusch_conditioned_mass_delivery as study


RECIPE = {'temperature_K': 362.15, 'source_flow_setting_code': 2.}


def empirical():
    return md.Model('synthetic-empirical', 'SETTING_AWARE_EMPIRICAL',
        tuple(tuple(np.linspace(.25+.02*i, .01+.005*i, 5)) for i in range(5)),
        (0., .06), {'kind': 'SYNTHETIC'}, 'synthetic fixture', knots_kg=tuple(np.linspace(0, .06, 5)))


def records():
    result = []
    model = md.synthetic_model()
    for condition in study.SITE_CONDITIONS:
        temp, flow = study.EXPECTED[condition]
        for replicate in (1, 2, 3):
            masses = np.full(10, 4.+.1*replicate)
            run = SimpleNamespace(mE=masses, mE_cum=np.cumsum(masses), tE=np.arange(1, 11)*3.)
            for r in study.old.mass_coordinates(run):
                recipe = {'temperature_K': temp+273.15, 'source_flow_setting_code': flow}
                q = float(model.predict(r['b0'], r['b1'], **recipe).average_q)
                result.append(dict(r, **recipe, setting_kind='CONSTANT', campaign='FIT_2021_12',
                    condition=condition, shot=condition.replace('-C', '-E')+f'-R{replicate}',
                    source_id='SYNTHETIC', eligible=True, q=q, solute_kg=r['mass_kg']*q,
                    source_rounding_allowance_kg=0.))
    return result


@pytest.mark.parametrize('theta', [(0., 0., .25), (1., 0., 4.), (.2827944898059652, 68.0383392716077, .8327267294693588), (.3, 10000., .25)])
def test_zero_slopes_exact_original_mass(theta):
    model = replace(md.synthetic_model(), coefficients=theta+(0.,)*4)
    for t, f in [(353.15, 2.), (362.15, 3.), (365.15, 2.)]:
        a, b = np.array([0., .01, .03]), np.array([.001, .02, .06])
        np.testing.assert_array_equal(model.predict(a, b, temperature_K=t, source_flow_setting_code=f).solute_kg,
                                      old_kernel.compact_delivery(a, b, theta))
        assert md.recipe_coefficients(model.coefficients, (t-362.15)/9, f-2) == theta


@pytest.mark.parametrize('z', [0., 1., .5, 1e-16, 1-1e-16])
def test_odds_exact_endpoints_identity_and_stability(z):
    assert md.odds_shift(z, 0) == z
    for h in [-1e300, -1000., -3., 3., 1000., 1e300]:
        q = md.odds_shift(z, h)
        assert 0 <= q <= 1
        if z in (0., 1.):
            assert q == z


@pytest.mark.parametrize('concentration', [0., .3, 1.])
def test_zero_rate_and_concentration(concentration):
    m = replace(md.synthetic_model(), coefficients=(concentration, 0., .25, 0., 0., 3., -3.))
    assert m.cumulative_solute(.06, temperature_K=353.15, source_flow_setting_code=2.) == concentration*.06
    z = replace(m, coefficients=(0., 10000., 4., 3., 3., 3., 3.))
    assert z.cumulative_solute(.06, **RECIPE) == 0


@pytest.mark.parametrize('model', [md.synthetic_model(), empirical()])
def test_additivity_partition_bounds_zero_and_quadrature(model):
    rng = np.random.default_rng(59)
    partition = np.r_[0., np.sort(rng.uniform(0, .06, 30)), .06]
    recipe = {'temperature_K': 359.15, 'source_flow_setting_code': 2.3}
    d = model.predict(partition[:-1], partition[1:], **recipe)
    assert np.all(d.solute_kg >= 0)
    assert np.all(d.solute_kg <= np.diff(partition))
    assert sum(d.solute_kg) == pytest.approx(model.cumulative_solute(.06, **recipe), abs=1e-12)
    zero = model.predict(.02, .02, **recipe)
    assert zero.solute_kg == 0 and np.isnan(zero.tds_percent)
    assert md.integration_allowance(model, 0., .06, **recipe) <= 1e-9
    t, f = md.features(**recipe)
    if model.family == 'MTF':
        c, k, p = md.recipe_coefficients(model.coefficients, t, f)
        integral = quad(lambda b: c*np.exp(-(k*b)**p), 0, .06, epsabs=1e-14)[0]
    else:
        q = md.setting_weights(t, f) @ np.array(model.coefficients)
        integral = quad(lambda b: np.interp(b, model.knots_kg, q), 0, .06, points=model.knots_kg, epsabs=1e-14)[0]
    assert model.cumulative_solute(.06, **recipe) == pytest.approx(integral, abs=1e-11)


@pytest.mark.parametrize('a,b,changes', [(-.1, 0., {}), (.02, .01, {}), (0., np.inf, {}),
    (0., .07, {}), (0., .01, {'temperature_K': np.nan}), (0., .01, {'source_flow_setting_code': np.inf}),
    (0., .01, {'temperature_unit': 'degC'}), (0., .01, {'mass_unit': 'g'}),
    (0., .01, {'flow_unit': 'mL/s'}), (0., .01, {'temperature_K': 371.15, 'source_flow_setting_code': 3.}),
    (0., .01, {'setting_kind': 'RAMP'})])
def test_invalid_and_unsupported_rejected(a, b, changes):
    with pytest.raises(ValueError):
        md.synthetic_model().predict(a, b, **(RECIPE | changes))


def test_explicit_unsupported_masks():
    m = md.synthetic_model()
    d = m.predict([0., 0., 0.], [.01, .07, .01], temperature_K=[362.15, 362.15, 371.15], source_flow_setting_code=[2., 2., 3.], strict=False)
    assert d.in_domain.tolist() == [True, False, False]
    assert d.unsupported_reason.tolist() == ['', 'OUTSIDE_FIT_MASS_DOMAIN', 'OUTSIDE_SETTING_DESIGN_HULL']
    assert np.isnan(d.solute_kg[1:]).all()
    r = m.predict(0., .01, **RECIPE, setting_kind='VARIABLE', strict=False)
    assert str(r.unsupported_reason) == 'NOT_ADJUDICATED_VARIABLE_SETTING_INPUT'


def test_temperature_and_flow_semantics():
    assert md.temperature_to_kelvin(89, 'degC') == 362.15
    assert md.features(362.15, 2.) == (0., 0.)
    assert md.features(371.15, 2.) == (1., 0.)
    with pytest.raises(ValueError):
        md.temperature_to_kelvin(89, 'Celsius')
    assert md.synthetic_model().source_code_semantics == md.SEMANTICS


def test_diamond_sites_continuity_and_weights():
    m = empirical()
    sites = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)]
    for j, (t, f) in enumerate(sites):
        np.testing.assert_array_equal(md.setting_weights(t, f), np.eye(5)[j])
        got = m.predict(0, .06, temperature_K=362.15+9*t, source_flow_setting_code=2+f).solute_kg
        expected = old_kernel.linear_basis_integral(0., .06, m.knots_kg) @ m.coefficients[j]
        assert got == expected
    for t, f in [(.5, .5), (-.5, -.5), (.25, -.75)]:
        assert sum(md.setting_weights(t, f)) == 1
    for epsilon in [-1e-10, 1e-10]:
        left = m.predict(0, .04, temperature_K=362.15+9*epsilon, source_flow_setting_code=2.5).solute_kg
        center = m.predict(0, .04, temperature_K=362.15, source_flow_setting_code=2.5).solute_kg
        assert abs(left-center) < 1e-10


@pytest.mark.parametrize('model', [md.synthetic_model(), empirical()])
def test_round_trip_and_malformed_artifacts(tmp_path, model):
    path = tmp_path/'model.json'
    model.save(path)
    loaded = md.Model.load(path)
    assert loaded.to_dict() == model.to_dict()
    for field, value in [('version', 'mass-delivery/1'), ('units', {}), ('parameter_bounds', {}),
                         ('feature_definitions', {}), ('setting_hull', {}), ('source_code_semantics', 'measured flow'),
                         ('fit_identity', {}), ('rights', ''), ('claims', []), ('coefficients', [float('nan')])]:
        bad = model.to_dict() | {field: value}
        with pytest.raises(ValueError):
            md.Model.from_dict(bad)
    with pytest.raises(ValueError):
        md.Model.from_dict(model.to_dict() | {'extra': 1})
    path.write_text('{"family":"MTF","family":"MT"}')
    with pytest.raises(ValueError):
        md.Model.load(path)


def test_ablations_and_bounded_parameters():
    for family, index in [('MT', 4), ('MF', 3), ('M0', 5)]:
        theta = [.2, 40, 1, 0, 0, 0, 0]
        theta[index] = .1
        with pytest.raises(ValueError):
            replace(md.synthetic_model(), family=family, coefficients=tuple(theta))
    with pytest.raises(ValueError):
        replace(md.synthetic_model(), coefficients=(.2, 10001, 1, 0, 0, 0, 0))


def test_full_mass_prefix_chemistry_gaps_and_shot_folds():
    rr = records()
    first = [r for r in rr if r['shot'] == 'FIT-E09-R1']
    assert [r['fraction'] for r in first] == [1, 2, 3, 5, 7, 10]
    assert first[3]['b0'] > first[2]['b1']
    assert first[-1]['b1'] == pytest.approx(.041)
    for name, train, held in study.folds(rr):
        assert {r['shot'] for r in train}.isdisjoint(r['shot'] for r in held)
        assert len(train) == 60 and len(held) == 30
        assert all(r['shot'].endswith(name) for r in held)
    projection = study.project(rr)
    assert all('q' not in r and 'solute_kg' not in r for r in projection)
    with pytest.raises(ValueError):
        study.predict(md.synthetic_model(), [projection[0] | {'q': .2}])


def test_fit_rejects_march_and_balanced_weights():
    rr = records()
    good, weights = study.old.training_weights(rr)
    assert sum(weights**2) == pytest.approx(1)
    for c in study.SITE_CONDITIONS:
        assert sum(w*w for r, w in zip(good, weights) if r['condition'] == c) == pytest.approx(.2)
    rr[0]['campaign'] = 'PREDICTION_2022_03'
    with pytest.raises(ValueError):
        list(study.folds(rr))
    with pytest.raises(ValueError):
        study.fit_empirical(rr, 5, .001)
    with pytest.raises(ValueError):
        study.fit_compact(rr, 'MTF', np.zeros((16, 7)), study.Budget(), 'synthetic')


def test_empirical_order_invariance_rank_and_training_domain():
    rr = records()
    model, trace = study.fit_empirical(rr, 5, .001)
    shuffled = [rr[i] for i in np.random.default_rng(7).permutation(len(rr))]
    other, _ = study.fit_empirical(shuffled, 5, .001)
    assert model.to_dict() == other.to_dict()
    assert trace['bounded_linear_solves'] == 5
    assert model.domain_kg[1] == max(r['b1'] for r in rr)
    narrow = [r for r in rr if r['fraction'] in (1, 2)]
    unavailable, diagnosis = study.fit_empirical(narrow, 9, 0.)
    assert unavailable is None
    assert any(s['status'] == 'EXCLUDED_RANK_DEFICIENT_UNPENALIZED' for s in diagnosis['sites'])
    for _, train, held in study.folds(rr):
        m, _ = study.fit_empirical(train, 5, .001)
        assert m.domain_kg[1] == max(r['b1'] for r in train)
        assert m.domain_kg[1] <= max(r['b1'] for r in rr)


def test_frozen_starts_and_persistent_budget(tmp_path):
    starts = json.loads((study.DOC/'STARTS.json').read_text())['starts']
    assert np.array(starts).shape == (16, 7)
    assert np.all(np.array(starts)[:8, 3:] == 0)
    path = tmp_path/'budget.jsonl'
    budget = study.Budget(path)
    budget.start('synthetic', [1, 2, 3])
    assert study.Budget(path).count == 1
    budget.count = 500
    with pytest.raises(RuntimeError):
        budget.start('over-cap', [])


def test_no_self_review_or_drift_scoring(tmp_path):
    study.write_json(tmp_path/'freeze.json', {'producer_commit': 'c', 'producer_tree': 't'})
    review = tmp_path/'review.json'
    study.write_json(review, {'status': 'APPROVED', 'independent': False})
    with pytest.raises(ValueError):
        study.verify_before_score(tmp_path, review)


def test_numerical_threshold_intervals():
    assert study.old.threshold(1., 1e-8, 1.) == 'NUMERICALLY_UNRESOLVED'
    assert study.old.threshold(.9, 1e-8, 1.) == 'PASS'
    assert study.old.threshold(1.1, 1e-8, 1.) == 'FAIL'


def test_nonzero_synthetic_slopes_change_outputs():
    m = md.synthetic_model()
    a = m.cumulative_solute(.04, temperature_K=353.15, source_flow_setting_code=2.)
    b = m.cumulative_solute(.04, temperature_K=371.15, source_flow_setting_code=2.)
    assert abs(a-b) > 1e-4


def test_compact_recovers_synthetic_recipe_dependent_intervals():
    training = records()
    starts = json.loads((study.DOC/'STARTS.json').read_text())['starts']
    model, trace = study.fit_compact(training, 'MTF', starts, study.Budget(), 'SYNTHETIC_TEST_ONLY')
    assert trace['status'] == 'CONVERGED'
    assert len(trace['attempts']) == 16
    assert all(a['actual_residual_evaluations'] <= 2000 for a in trace['attempts'])
    assert all(a['actual_residual_evaluations'] > a['optimizer_nfev'] for a in trace['attempts'] if a['success'])
    prediction = study.predict(model, study.project(training))
    assert max(abs(r['predicted_solute_kg']-o['solute_kg']) for r, o in zip(prediction, training)) < 1e-9

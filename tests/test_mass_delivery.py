"""Synthetic tests only; ordinary CI never reads external Pannusch chemistry."""
from dataclasses import replace
from types import SimpleNamespace
import json

import numpy as np
import pytest

from puckworks.analysis import mass_delivery as md
from puckworks.analysis import pannusch_mass_delivery as study


def model(**changes):
    return replace(md.Model('synthetic', 'MASS', (.15, 40., .8), (0., .06),
                            {'kind': 'SYNTHETIC'}, 'synthetic fixture'), **changes)


def records():
    out = []
    for c in range(1, 4):
        for s in range(1, 3):
            run = SimpleNamespace(mE=np.full(10, 5.), mE_cum=np.arange(1, 11)*5.,
                                  tE=np.arange(1, 11)*3.)
            for r in study.mass_coordinates(run):
                q = float(model().predict(r['b0'], r['b1']).average_q)
                out.append(dict(r, campaign='FIT_2021_12', condition=f'C{c}', shot=f'C{c}-R{s}',
                                source_id='SYNTHETIC', eligible=True, q=q,
                                solute_kg=r['mass_kg']*q, source_rounding_allowance_kg=0.))
    return out


def test_units_and_source_mass_basis():
    assert md.mass_to_kg([1, 2], 'g').tolist() == [.001, .002]
    assert md.mass_to_kg(1, 'mg') == 1e-6
    assert md.mass_to_kg(1, 'kg') == 1
    assert md.concentration_to_fraction(5, 'percent') == .05
    assert md.concentration_to_fraction(.05, 'kg/kg') == .05
    for args in [(5, 'mg/L', 'MASS'), (5, 'percent', 'VOLUME'), (101, 'percent', 'MASS')]:
        with pytest.raises(ValueError): md.concentration_to_fraction(*args)
    for value, unit in [(-1, 'kg'), (1, 'ml'), (np.nan, 'g')]:
        with pytest.raises(ValueError): md.mass_to_kg(value, unit)


@pytest.mark.parametrize('p', [.25, .8, 1., 4.])
def test_predecessor_mass_operator_synthetic_only(p):
    from puckworks.analysis.grudeva_clock import deliver
    rr = [dict(shot=1, vial=i+1, mass_g=m, b_start_g=b, t_start_s=i, t_end_s=i+1)
          for i, (m, b) in enumerate([(1e-8, 0.), (5., 0.), (10., 5.), (5., 35.)])]
    old = deliver(rr, (.2, 0., .04, p))*.001
    new = md.compact_delivery([r['b_start_g']*.001 for r in rr],
                             [(r['b_start_g']+r['mass_g'])*.001 for r in rr], (.2, 40., p))
    np.testing.assert_allclose(new, old, atol=1e-15, rtol=1e-13)


@pytest.mark.parametrize('c0', [0., .1, 1.])
def test_constant_and_zero_rate(c0):
    m = model(coefficients=(c0, 0., .25))
    np.testing.assert_allclose(m.predict([0, .01], [.01, .03]).solute_kg, c0*np.array([.01,.02]), atol=1e-15)
    assert m.cumulative_solute(.04) == pytest.approx(c0*.04)
    assert float(m.cumulative_solute(.06)) == c0*.06


def test_bounded_additive_delivery_and_disjoint_support():
    m = model()
    split = m.predict([0, .01, .02], [.01, .02, .04]).solute_kg
    assert np.all(split >= 0) and np.all(split <= [.01,.01,.02])
    assert sum(split) == pytest.approx(m.cumulative_solute(.04), abs=1e-13)
    assert split[0]+split[2] < m.cumulative_solute(.04)  # missing middle assay is not zero
    assert m.average_tds(.01, .02) == pytest.approx(100*split[1]/.01)


def test_zero_width_is_explicit_and_domain_flags():
    r = model().predict([.01, .06], [.01, .07], strict=False)
    assert r.solute_kg[0] == 0 and np.isnan(r.average_q[0])
    assert not r.positive_width[0] and not r.in_domain[1]
    assert np.isnan(r.solute_kg[1])
    with pytest.raises(ValueError, match='domain'): model().cumulative_solute(.07)


@pytest.mark.parametrize('bounds', [(-.01,.01),(.02,.01),(0.,float('inf')),(np.nan,.1)])
def test_bad_intervals(bounds):
    with pytest.raises(ValueError): model().predict(*bounds)


@pytest.mark.parametrize('theta', [(-.1,2,1),(1.1,2,1),(.1,-1,1),(.1,10001,1),(.1,2,.2),(.1,2,5),(.1,np.nan,1)])
def test_invalid_parameters(theta):
    with pytest.raises(ValueError): model(coefficients=theta)


def test_serialization_and_schema(tmp_path):
    m = model(); path = tmp_path/'model.json'; m.save(path)
    other = md.Model.load(path)
    assert m.to_dict() == other.to_dict()
    assert other.cumulative_solute(.04) == m.cumulative_solute(.04)
    for field, value in [('version','future'),('units',{'mass':'g'}),('family','UNKNOWN'),('claims',[])]:
        data = json.loads(path.read_text()); data[field] = value
        with pytest.raises(ValueError): md.Model.from_dict(data)
    d = m.to_dict(); d['extra'] = 1
    with pytest.raises(ValueError): md.Model.from_dict(d)


def test_no_future_observations_for_stop_query():
    # The public API receives only a requested stop; no final shot mass or chemistry.
    assert float(model().cumulative_solute(.035)) > 0
    assert model().cumulative_solute(.035) < model().cumulative_solute(.04)


@pytest.mark.parametrize('p', [.25, .5, 4.])
def test_independent_integration_origin_and_refinement(p):
    m = model(coefficients=(.8, 500., p))
    for a, b in [(0,1e-12),(0,.001),(.001,.005),(.05,.06)]:
        assert md.integration_allowance(m, a, b) < 1e-9


def test_time_integrates_against_mass_and_sensitivities():
    m = model(family='TIME', coefficients=(.2,.03,.8), time_domain_s=(0.,60.))
    for timing in ['linear','u2','sqrt']:
        mm = replace(m,timing=timing)
        a = float(mm.predict(0.,.01,time_bounds=(0.,10.)).solute_kg)
        b = float(mm.predict(0.,.02,time_bounds=(0.,10.)).solute_kg)
        assert b == pytest.approx(2*a)
        assert md.integration_allowance(mm,0,.01,(0,10)) < 1e-9
    with pytest.raises(ValueError): m.predict(0,.01)
    with pytest.raises(ValueError): m.cumulative_solute(.01)
    assert not m.predict(0,.01,time_bounds=(60.,65.),strict=False).in_domain


def test_complete_mass_sequence_independent_of_chemistry():
    r = SimpleNamespace(mE=np.ones(11), mE_cum=np.arange(1,12), tE=np.arange(1,12), TdS=np.arange(6))
    a = study.mass_coordinates(r)
    r.TdS = np.zeros(6); assert study.mass_coordinates(r) == a
    r.TdS = np.arange(6)[::-1]; assert study.mass_coordinates(r) == a
    assert a[3]['b0'] == .004 and a[-1]['b1'] == .010
    assert a[-1]['collection_mass_kg'] == .011
    assert sum(x['mass_kg'] for x in a) == .006
    r.mE_cum[-1] = 99
    with pytest.raises(ValueError, match='prefix'): study.mass_coordinates(r)


def test_missing_chemistry_advances_mass_and_does_not_fit_zero():
    rr = records(); old = study.project(rr)
    rr[1].update(eligible=False,q=None,solute_kg=None)
    assert study.project(rr) == old
    good, weights = study.training_weights(rr)
    assert len(good) == len(rr)-1 and np.sum(weights**2) == pytest.approx(1.)
    assert old[3]['b0'] > old[2]['b1']


def test_duplicate_analytical_rows_and_identity():
    row = dict(shot='a',fraction=2,analyte='TDS',q=.1)
    assert study.deduplicate([row,dict(row)], ('shot','fraction','analyte')) == [row]
    with pytest.raises(ValueError,match='duplicate'):
        study.deduplicate([row,dict(row,q=.2)],('shot','fraction','analyte'))


def test_grouped_split_and_training_information_boundary():
    rr = records()
    for c, train, held in study.loco(rr):
        assert all(r['condition'] != c for r in train)
        assert not {r['shot'] for r in train}&{r['shot'] for r in held}
    rr[0]['campaign'] = 'PREDICTION_2022_03'
    with pytest.raises(ValueError,match='held campaign'): study.training_weights(rr)
    with pytest.raises(ValueError,match='role'): study.attach_chemistry(rr,allow_campaign='FIT_2021_12')
    with pytest.raises(ValueError,match='coordinate-only'): study.predict(model(),records())
    coords = study.project(records())
    assert all('q' not in r and 'solute_kg' not in r and 'collection_mass_kg' not in r for r in coords)


def test_boundary_aware_exact_integration_and_training_basis():
    rr = records()
    fitted, _ = study.fit_empirical(rr,5,.001)
    assert fitted.knots_kg == pytest.approx(np.linspace(0,.05,5))
    m = replace(fitted, coefficients=(.1,.3,.2,.05,.1))
    whole = m.predict(0,.05).solute_kg
    assert whole == pytest.approx(np.trapezoid(m.coefficients,m.knots_kg),abs=1e-15)
    assert sum(m.predict([0,.013],[.013,.05]).solute_kg) == pytest.approx(whole,abs=1e-15)
    assert md.integration_allowance(m, .002,.041) < 1e-9
    # Held values, boundaries and totals cannot reach the baseline fitting signature.
    changed = [dict(r,q=.99,solute_kg=.1) for r in rr if r['condition']=='C3']
    train = [r for r in rr if r['condition']!='C3']
    a,_ = study.fit_empirical(train,5,.001)
    changed.reverse()
    b,_ = study.fit_empirical(train,5,.001)
    assert a.to_dict() == b.to_dict()


def test_equal_condition_shot_mass_weights():
    rr = records(); good,w = study.training_weights(rr)
    assert sum(w*w) == pytest.approx(1.)
    for c in ['C1','C2','C3']:
        assert sum(x*x for r,x in zip(good,w) if r['condition']==c) == pytest.approx(1/3)


def test_metrics_numerical_bounds_and_no_denominator_reduction():
    rr = records(); pred = study.predict(model(),study.project(rr))
    shots = study.shot_metrics(rr,pred)
    assert all(s['metrics']['R_pp'] < 1e-12 for s in shots)
    assert all(s['chemistry_mass_coverage'] == pytest.approx(.6) for s in shots)
    assert all(c['adequacy']=='PASS' for c in study.condition_metrics(shots))
    pred[0].update(in_domain=False,predicted_solute_kg=None)
    shots = study.shot_metrics(rr,pred)
    assert shots[0]['metrics'] is None and shots[0]['supported_only_diagnostic'] is not None
    assert study.condition_metrics(shots)[0]['adequacy']=='UNSUPPORTED_OR_UNQUALIFIED'
    assert study.threshold(1.,1e-8,1.) == 'NUMERICALLY_UNRESOLVED'
    assert study.threshold(.9,1e-8,1.) == 'PASS'
    assert study.threshold(1.1,1e-8,1.) == 'FAIL'


def test_score_requires_independent_exact_freeze_review(tmp_path):
    p=tmp_path/'review.json'; p.write_text(json.dumps({'status':'PENDING'}))
    with pytest.raises(ValueError,match='approval'): study.score(tmp_path,p)


def test_frozen_target_register_drift_is_rejected_before_target_access(tmp_path):
    p = tmp_path/'synthetic_register.csv'; p.write_text('synthetic,target\n1,2\n')
    manifest = {'registers': {p.name: study.digest(p)}}
    study.verify_registers(manifest,tmp_path)
    p.write_text('synthetic,target\n1,3\n')
    with pytest.raises(ValueError,match='register drift'):
        study.verify_registers(manifest,tmp_path)


def test_competitive_decision_keeps_numerical_uncertainty_explicit():
    conditions = {}
    for name, R, status in [('MASS',1.,'NUMERICALLY_UNRESOLVED'),('TIME',1.05,'FAIL')]:
        conditions[name] = [{'condition': c, 'adequacy':status,
                            'metrics':{'R_pp':R,'R_allowance_pp':1e-8,'abs_B_pp':.1,'B_allowance_pp':1e-8}}
                           for c in study.PRIMARY]
    a = study.aggregate(conditions['MASS'],study.PRIMARY)
    assert a['adequacy_status'] == 'NUMERICALLY_UNRESOLVED'
    result = study.comparison(conditions,b='TIME')
    assert result['competitive_status'] == 'NUMERICALLY_UNRESOLVED'
    assert not result['competitive']


def test_near_zero_positive_rate_at_unit_concentration():
    for k in (1e-20,1e-16,1e-12,1e-9):
        m = model(coefficients=(1.,k,1.))
        value = float(m.cumulative_solute(.06))
        assert 0 <= value <= .06
        assert value == pytest.approx(.06,abs=1e-11)

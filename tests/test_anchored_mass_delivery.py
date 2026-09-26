"""Synthetic numerical and information-flow tests; no private source rows."""
from dataclasses import FrozenInstanceError, replace
import json
from types import SimpleNamespace

import numpy as np
import pytest
from scipy.integrate import quad

from puckworks.analysis import anchored_mass_delivery as md
from puckworks.analysis import mass_delivery as kernel
from puckworks.analysis import conditioned_mass_delivery as conditioned
from puckworks.analysis import pannusch_anchored_mass_delivery as study


def base(family='MASS'):
    if family == 'MASS':
        model = kernel.Model('synthetic/MASS', family, (.2, 50., .8), (0., .06),
            {'kind': 'SYNTHETIC'}, 'first-party synthetic')
    else:
        model = kernel.Model('synthetic/EMPIRICAL', 'BOUNDARY_AWARE_EMPIRICAL',
            (.2, .1, .16, .03, .05), (0., .06), {'kind': 'SYNTHETIC'},
            'first-party synthetic', knots_kg=(0., .015, .03, .045, .06))
    return md.FrozenBase.from_model(model)


def setting_base():
    profile = (.2, .1, .16, .03, .05)
    return md.FrozenBase.from_model(conditioned.Model('synthetic/SETTING',
        'SETTING_AWARE_EMPIRICAL', (profile,)*5, (0., .06), {'kind': 'SYNTHETIC'},
        'first-party synthetic', knots_kg=(0., .015, .03, .045, .06)))


def observation(b, scale=1., setting=None):
    q = float(b.curve(setting).predict(0., .004).tds_percent)*scale
    return replace(md.synthetic_observation(), tds_percent=q)


@pytest.mark.parametrize('family', ['MASS', 'EMPIRICAL'])
@pytest.mark.parametrize('scale', [0., .7, 1., 1.8])
def test_scalar_recovery_identity_additivity_and_remaining(family, scale):
    b = base(family)
    before = b.artifact_json
    s = md.anchor(b, observation(b, scale))
    edges = (.004, .007, .015, .03, .045, .059)
    queries = tuple(md.IntervalQuery(u, v) for u, v in zip(edges[:-1], edges[1:]))
    pp = s.predict_intervals(queries)
    assert s.alpha == pytest.approx(scale, abs=1e-15)
    for q, p in zip(queries, pp):
        assert p.solute_kg == pytest.approx(scale*float(b.curve().predict(q.start_kg, q.end_kg).solute_kg), abs=2e-15)
        assert p.tds_percent == pytest.approx(100*p.solute_kg/(q.end_kg-q.start_kg))
    total = s.remaining_solute(edges[-1])
    assert sum(p.solute_kg for p in pp) == pytest.approx(total.solute_kg, abs=1e-13)
    assert b.artifact_json == before
    with pytest.raises(FrozenInstanceError):
        s.alpha = .5
    with pytest.raises(FrozenInstanceError):
        s.observation.tds_percent = 10


@pytest.mark.parametrize('family', ['MASS', 'EMPIRICAL'])
def test_independent_integral_and_analytical_sensitivity(family):
    b = base(family)
    a = observation(b, .8)
    s = md.anchor(b, a)
    curve = b.curve()
    if family == 'MASS':
        c, k, p = curve.coefficients
        fn = lambda x: c*np.exp(-(k*x)**p)
        points = None
    else:
        fn = lambda x: np.interp(x, curve.knots_kg, curve.coefficients)
        points = curve.knots_kg
    d = quad(fn, 0, .004, epsabs=1e-15)[0]
    i = quad(fn, .004, .059, points=points, epsabs=1e-15)[0]
    p = s.remaining_solute(.059)
    expected = .004*a.tds_percent/100*i/d
    assert abs(p.solute_kg-expected) <= p.numerical_allowance_kg
    assert p.anchor_error_amplification == pytest.approx(.004*i/(.055*d), abs=1e-12)
    plus = md.anchor(b, replace(a, tds_percent=a.tds_percent+.001)).remaining_solute(.059)
    assert (plus.tds_percent-p.tds_percent)/.001 == pytest.approx(p.anchor_error_amplification, rel=1e-10)


def test_ratio_product_allowance_encloses_corners(monkeypatch):
    b = base()
    d, de, v, ve = 1e-4, 5e-11, 5e-5, 4e-10
    monkeypatch.setattr(md, 'integral', lambda curve, u, w: (d, de) if u == 0 else (v, ve))
    a = replace(md.synthetic_observation(), tds_percent=2.5)
    s = md.anchor(b, a)
    p = s.remaining_solute(.02)
    for denominator in (d-de, d+de):
        for future in (v-ve, v+ve):
            ref = .004*.025/denominator*future
            assert abs(ref-p.solute_kg) <= p.numerical_allowance_kg
    monkeypatch.setattr(md, 'integral', lambda curve, u, w: (d, de) if u == 0 else (v, 2e-9))
    with pytest.raises(ValueError, match='NUMERICALLY_UNRESOLVED_FUTURE'):
        s.remaining_solute(.02)


@pytest.mark.parametrize('coefficients', [(0., 50., .8), (1e-14, 50., .8), (.2, 10000., 4.)])
def test_zero_or_unresolved_denominator(coefficients):
    m = replace(base().curve(), coefficients=coefficients)
    a = md.synthetic_observation()
    if coefficients[1] == 10000:
        a = replace(a, start_kg=.02, end_kg=.024)
    with pytest.raises(ValueError, match='NUMERICALLY_UNRESOLVED_ANCHOR_DENOMINATOR'):
        md.anchor(md.FrozenBase.from_model(m), a)


@pytest.mark.parametrize('tds', [-1., 100.1, float('nan'), float('inf'), True])
def test_invalid_anchor_values(tds):
    with pytest.raises(ValueError):
        replace(md.synthetic_observation(), tds_percent=tds)


@pytest.mark.parametrize('delta', [{'end_kg': 0.}, {'start_kg': -.01}, {'tds_basis': 'VOLUME'},
    {'tds_unit': 'kg/kg'}, {'mass_basis': 'NOMINAL_VOLUME'}, {'fraction_id': 2}, {'fraction_id': True}])
def test_invalid_anchor_basis_and_interval(delta):
    with pytest.raises(ValueError):
        replace(md.synthetic_observation(), **delta)


def test_supported_anchor_and_nonmonotone_bound():
    b = base('EMPIRICAL')
    with pytest.raises(ValueError, match='UNSUPPORTED_ANCHOR_INTERVAL'):
        md.anchor(b, replace(md.synthetic_observation(), end_kg=.07))
    # Peak at a knot must be detected even though anchor concentration is low.
    m = replace(b.curve(), coefficients=(.05, .05, .9, .05, .05))
    with pytest.raises(ValueError, match='CONCENTRATION_EXCEEDS_ONE'):
        md.anchor(md.FrozenBase.from_model(m), replace(md.synthetic_observation(), tds_percent=10.))
    s = md.anchor(b, observation(b))
    assert s.maximum_anchored_concentration == pytest.approx(.2)


def test_zero_anchor_and_query_edges():
    s = md.anchor(base(), replace(md.synthetic_observation(), tds_percent=0.))
    p = s.remaining_solute(.04)
    assert p.solute_kg == p.tds_percent == p.numerical_allowance_kg == 0
    assert p.anchor_error_amplification > 0
    z = s.remaining_solute(.004)
    assert z.solute_kg == 0 and z.tds_percent is None and z.anchor_error_amplification is None
    for args, reason in [((.003, .005), 'BEFORE_ANCHOR'), ((.01, .061), 'OUTSIDE_FROZEN')]:
        with pytest.raises(ValueError, match=reason):
            s.predict_intervals((md.IntervalQuery(*args),))
    for args in [(.02, .01), (-1, .01), (0, float('inf'))]:
        with pytest.raises(ValueError):
            md.IntervalQuery(*args)


def test_serialization_strict_and_no_base_mutation(tmp_path):
    b = base()
    m = b.curve()
    m.fit_identity['kind'] = 'MUTATED_TEMPORARY_COPY'
    assert b.curve().fit_identity['kind'] == 'SYNTHETIC'
    s = md.anchor(b, observation(b))
    p = tmp_path/'synthetic.json'
    s.save(p)
    assert md.AnchoredState.load(p) == s
    for key, value in [('alpha', .1), ('units', {}), ('future_domain_kg', [0, 1]), ('claims', []), ('extra', 1)]:
        d = s.to_dict()
        d[key] = value
        with pytest.raises(ValueError):
            md.AnchoredState.from_dict(d)
    d = s.to_dict(); d['base']['sha256'] = '0'*64
    with pytest.raises(ValueError):
        md.AnchoredState.from_dict(d)
    with pytest.raises(ValueError, match='DUPLICATE'):
        md.strict_json('{"a":1,"a":2}')


def test_shared_anchor_parity_and_setting_semantics():
    b, sb = base('EMPIRICAL'), setting_base()
    a = observation(b, .8)
    s1 = md.anchor(b, a)
    s2 = md.anchor(sb, a, setting=md.NominalSetting(362.15, 2.))
    assert s1.alpha == s2.alpha
    assert s1.remaining_solute(.05) == s2.remaining_solute(.05)
    with pytest.raises(ValueError, match='TYPED_NOMINAL_SETTING'):
        md.anchor(sb, a)
    with pytest.raises(ValueError):
        md.NominalSetting(380., 2.)
    with pytest.raises(ValueError):
        md.NominalSetting(362.15, 2., 'VARIABLE')


def synthetic_cohort():
    coords, rows = [], []
    for shot in study.SHOTS:
        condition = shot[:8].replace('-E', '-C')
        # Genuine source identity labels with entirely synthetic values.
        run = SimpleNamespace(mE=np.full(11, 4.), mE_cum=np.arange(1, 12)*4., tE=np.arange(1, 12)*3.)
        for r in study.old.mass_coordinates(run):
            c = dict(r, campaign=study.CAMPAIGN, condition=condition, shot=shot,
                     source_id='SYNTHETIC', temperature_K=362.15, source_flow_setting_code=2.)
            coords.append(c)
            q = float(base().curve().predict(c['b0'], c['b1']).average_q)*.8
            rows.append({'campaign_id': study.CAMPAIGN, 'condition_id': condition, 'shot_id': shot,
                'fraction_id': str(r['fraction']), 'analyte': 'TDS', 'source_id': 'SYNTHETIC',
                'concentration_unit': 'percent', 'fraction_liquid_g_or_ml': '4',
                'measured_concentration': str(100*q), 'validity': 'VALID',
                'derived_analyte_mass_mg': str(4000*q)})
    return coords, rows


def test_later_chemistry_change_delete_permute_cannot_change_prediction():
    coords, rows = synthetic_cohort()
    bases = {'MASS': base(), 'EMPIRICAL': base('EMPIRICAL'), 'SETTING_EMPIRICAL': setting_base()}
    anchors, _ = study.extract_anchors(rows, coords)
    expected = study.predict_bundle(bases, anchors, study.project_queries(coords))
    changed = [dict(r, measured_concentration='99', derived_analyte_mass_mg='9999')
               if r['fraction_id'] != '1' else r for r in rows]
    for data in (changed, list(reversed(changed)), [r for r in rows if r['fraction_id'] == '1']):
        actual, _ = study.extract_anchors(data, coords)
        assert actual == anchors
        assert study.predict_bundle(bases, actual, study.project_queries(coords)) == expected


def test_cross_shot_and_endpoint_independence_and_query_leakage():
    coords, rows = synthetic_cohort()
    bases = {'MASS': base(), 'EMPIRICAL': base('EMPIRICAL'), 'SETTING_EMPIRICAL': setting_base()}
    anchors, _ = study.extract_anchors(rows, coords)
    queries = study.project_queries(coords)
    before, _ = study.predict_bundle(bases, anchors, queries)
    anchors[study.SHOTS[-1]] = replace(anchors[study.SHOTS[-1]], tds_percent=1.)
    after, _ = study.predict_bundle(bases, anchors, queries)
    for arm in study.ARMS:
        assert before[arm][:5] == after[arm][:5]
    state = md.anchor(base(), observation(base()))
    original = state.to_dict()
    early = state.predict_intervals((md.IntervalQuery(.004, .01),))[0]
    state.remaining_solute(.03); state.remaining_solute(.06)
    assert state.to_dict() == original
    assert state.predict_intervals((md.IntervalQuery(.004, .01),))[0] == early
    bad = dict(queries[0], tds_percent=30.)
    with pytest.raises(ValueError, match='COORDINATE_ONLY'):
        study.predict_bundle(bases, anchors, [bad])
    with pytest.raises(ValueError, match='COORDINATE_ONLY'):
        state.predict_intervals([{'start_kg': .004, 'end_kg': .01, 'tds_percent': 30.}])


def test_scorer_excludes_anchor_and_preserves_missing_shot_denominators():
    coords, rows = synthetic_cohort()
    bases = {'MASS': base(), 'EMPIRICAL': base('EMPIRICAL'), 'SETTING_EMPIRICAL': setting_base()}
    anchors, _ = study.extract_anchors(rows, coords)
    anchors[study.SHOTS[0]] = None
    predictions, _ = study.predict_bundle(bases, anchors, study.project_queries(coords))
    observed = study.selected_assays(rows, [r for r in coords if r['fraction'] in study.SUFFIX], study.SUFFIX)
    result, shots = study.evaluate(observed, predictions)
    first = shots['ANCHORED_MASS'][0]
    assert first['expected_assays'] == 5 and first['supported_assays'] == 0
    assert len(shots['ANCHORED_MASS']) == 12
    assert result['axes']['A'] != 'PASS' and result['axes']['D'] != 'PASS'
    with pytest.raises(ValueError, match='COMPLETE_SUFFIX'):
        study.evaluate(observed[5:], predictions)
    with pytest.raises(ValueError, match='COMPLETE_SUFFIX'):
        study.evaluate([dict(observed[0], fraction=1)]+observed[1:], predictions)
    with pytest.raises(ValueError, match='ASSAY_ROLE'):
        study.selected_assays(rows, coords, study.SUFFIX)


def test_missing_fraction_one_never_falls_back():
    coords, rows = synthetic_cohort()
    rows = [r for r in rows if not (r['shot_id'] == study.SHOTS[0] and r['fraction_id'] == '1')]
    anchors, support = study.extract_anchors(rows, coords)
    assert anchors[study.SHOTS[0]] is None
    assert support[0]['reason'] == 'MISSING_ASSAY'


def test_threshold_crossing_is_numerically_unresolved():
    assert study.old.threshold(.9999999, 1e-6, 1.) == 'NUMERICALLY_UNRESOLVED'
    assert study.conjunction(['PASS', 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS']) != 'PASS'


def test_perfect_comparator_does_not_divide_by_zero_or_earn_material_gain():
    m = {'R_pp': 0., 'abs_B_pp': 0., 'B_pp': 0., 'R_allowance_pp': 0., 'B_allowance_pp': 0.}
    cc = [{'condition': c, 'metrics': m, 'adequacy': 'PASS'} for c in study.old.PRIMARY]
    result = study.compare({'ANCHORED_MASS': cc, 'ANCHOR_PERSISTENCE': cc}, 'ANCHOR_PERSISTENCE')
    assert result['relative_R_reduction'] is None
    assert result['material_gain'] == 'FAIL'


def test_state_rejects_boolean_derived_numbers():
    s = md.anchor(base(), observation(base()))
    d = s.to_dict(); d['alpha'] = True
    with pytest.raises(ValueError, match='FINITE_SCALAR'):
        md.AnchoredState.from_dict(d)


def test_review_gate_rejects_authorless_or_wrong_freeze_before_outcomes(tmp_path):
    review = tmp_path/'review.json'
    freeze = tmp_path/'freeze.json'
    freeze.write_text(json.dumps({'producer_commit': 'synthetic', 'producer_tree': 'synthetic'}))
    review.write_text(json.dumps({'status': 'APPROVED', 'independent': False}))
    with pytest.raises(ValueError, match='independent exact-freeze'):
        study.verify_before_score(tmp_path, review)


def test_synthetic_cli(capsys, monkeypatch):
    monkeypatch.setattr('sys.argv', ['anchored_mass_delivery'])
    md.main()
    result = json.loads(capsys.readouterr().out)
    assert result['input_class'] == 'SYNTHETIC_ANCHOR_INPUT'
    assert result['remaining']['numerical_allowance_kg'] <= 1e-9

"""Synthetic public tests only; no source-derived values or private locators."""
from dataclasses import replace
import json

import numpy as np
import pytest
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled
from puckworks.analysis import pocketscience_cross_basket_tds as basket
from puckworks.analysis import pocketscience_affine_tds as model
from tools import pocketscience_affine_tds as runner


def fixture():
    return [parent.Shot('synthetic', 10*g+i, ('synthetic', str(g)), style,
        .02, .035+.002*g+.001*i, 7+.3*g+.1*i, 7.5+.2*g+.05*i)
        for g, style in enumerate(['traditional', 'turbo']*3) for i in range(3)]


def full_fixture():
    shots = []
    for sheet in ('Sworks High Flow', 'VST18'):
        for grinder, style in parent.STYLE_MAP.items():
            for prep in ('N', 'Y'):
                for dispersion in (('Brass', 'Teflon') if sheet == 'Sworks High Flow' else ('Teflon',)):
                    for i in range(5):
                        index = sum(s.sheet == sheet for s in shots)+1
                        # Synthetic identities assign one traditional and two turbo exclusions.
                        row = {9: 25, 25: 9}.get(index, index) if sheet == 'Sworks High Flow' else index
                        shots.append(parent.Shot(sheet, row, (sheet, grinder, prep, dispersion), style,
                            .019+.0001*i, .035+.0004*index, 7+.03*index, 7.2+.02*index,
                            sheet == 'Sworks High Flow' and row in (7, 9, 23)))
    return shots


def test_full_cohort_restoration_and_explicit_fold_order():
    all60 = full_fixture()
    primary, complete = runner.cohorts(all60)
    assert len(primary) == 57 and complete == all60
    assert [sum(s.style == v for s in primary) for v in parent.STYLES] == [29, 28]
    for rows in (primary, complete):
        record = runner.fold_record(rows)
        assert record['original_order'] == [s.identity for s in rows]
        assert record['global_condition_indices'] == parent.arrays(rows)[3].tolist()
        assert len(record['folds']) == 12 and record['coverage_per_shot'] == 1
        held = []
        for f in record['folds']:
            assert set(f['training']).isdisjoint(f['held'])
            assert set(f['training']) | set(f['held']) == {s.identity for s in rows}
            assert all(s.condition == f['condition'] for s in rows if s.identity in f['held'])
            held += f['held']
        assert sorted(held) == sorted(s.identity for s in rows)
    assert {s.identity for s in complete if s not in primary} == {('Sworks High Flow', v) for v in (7, 9, 23)}
    with pytest.raises(ValueError, match='full 57/60'):
        runner.cohorts(all60[:40])
    with pytest.raises(ValueError, match='duplicate'):
        runner.cohorts(all60+[all60[0]])


def test_held_targets_leave_that_folds_coefficients_and_predictions_unchanged():
    x, y, style, group = parent.arrays(fixture())
    pred, fits = model.cross_predict(x, y, style, group)
    for g in np.unique(group):
        changed = y.copy(); changed[group == g] += 23
        other, other_fits = model.cross_predict(x, changed, style, group)
        np.testing.assert_array_equal(pred[group == g], other[group == g])
        assert fits[g] == other_fits[g]


@pytest.mark.parametrize('intercept,slope,expected_slope', [(-5, 20, 20), (2, 160, 100), (20, -10, 0)])
def test_signed_intercept_and_bounded_slope_exact_optima(intercept, slope, expected_slope):
    x = np.array([.3, .35, .4, .45, .5, .55])
    style = np.array([0, 1, 0, 1, 0, 1]); y = intercept+slope*x
    w = np.array([1, 2, 0, 3, 1, 2])
    fit = model.fit_source(x, y, style, w)
    a, b = fit['parameters']['A']['coefficients']
    assert b == pytest.approx(expected_slope)
    assert a == pytest.approx(np.average(y, weights=w)-b*np.average(x, weights=w))
    if slope == 20: assert a < 0
    z = np.column_stack((np.ones(len(x)), x))*np.sqrt(w[:, None])
    independent = lsq_linear(z, y*np.sqrt(w), bounds=([-np.inf, 0], [np.inf, 100]), method='bvls', tol=1e-14)
    held_x = np.array([.01, .7, 2.])
    np.testing.assert_allclose(model.predict(fit, held_x, np.array([0, 1, 1]))[:, 0],
                               independent.x[0]+independent.x[1]*held_x, rtol=0, atol=1e-10)
    for v in fit['nesting_checks'].values(): assert v['sse_difference'] <= v['allowance']
    diagnostic = fit['parameters']['A']
    assert diagnostic['rank'] == 2 and len(diagnostic['singular_values']) == 2
    assert diagnostic['column_normalized_condition_number'] >= 1


def test_literal_resampling_matches_weighted_folds_fits_and_scores():
    x, y, style, group = parent.arrays(fixture())
    for seed in range(3):
        w = parent.bootstrap_weights(group, np.random.default_rng(seed))
        pred, fits = model.cross_predict(x, y, style, group, w)
        ids = np.repeat(np.arange(len(x)), w)
        literal, literal_fits = model.cross_predict(x[ids], y[ids], style[ids], group[ids])
        np.testing.assert_allclose(pred[ids], literal, rtol=0, atol=1e-10)
        weighted = model.scores(y, pred, group, w)
        expanded = model.scores(y[ids], literal, group[ids])
        for arm in model.ARMS:
            assert weighted[arm] == pytest.approx(expanded[arm])
            for f, g in zip(fits, literal_fits, strict=True):
                np.testing.assert_allclose(f['parameters'][arm]['coefficients'], g['parameters'][arm]['coefficients'], rtol=0, atol=1e-10)


def test_rank_weights_solver_and_oracle_failures(monkeypatch):
    x, y, style, group = parent.arrays(fixture())
    for weights in (np.zeros(len(x)), -np.ones(len(x)), np.full(len(x), np.nan)):
        with pytest.raises(ValueError): model.fit_source(x, y, style, weights)
    with pytest.raises(ValueError, match='Sxx|rank'): model.fit_source(np.ones(len(x)), y, style)
    with pytest.raises(ValueError, match='rank'): model.fit_source(x, y, style, (style == 0).astype(int))
    with pytest.raises(ValueError, match='rank'): model.cross_predict(x, y, style, style)
    original = model.lsq_linear
    def failed(*args, **kwargs):
        r = original(*args, **kwargs); r.success = False; return r
    monkeypatch.setattr(model, 'lsq_linear', failed)
    with pytest.raises(ValueError, match='solver failed'): model.fit_source(x, y, style)
    monkeypatch.setattr(model, 'lsq_linear', original)
    fit = model.fit_source(x, y, style)
    fit['independent_coefficients']['A'][0] += 1e-6
    with pytest.raises(ValueError, match='prediction failure'): model.oracle_error(fit, x, style)


def test_out_of_domain_raw_predictions_are_scored_and_retained():
    shots = fixture()
    shots = [replace(s, filtered_tds_pp=-4+25*s.dose_kg/s.beverage_kg) for s in shots]
    held = shots[0].condition
    shots = [replace(s, beverage_kg=20, filtered_tds_pp=3) if s.condition == held else s for s in shots]
    r = model.evaluate(shots, draws=2)
    rows = [p for p in r['predictions'] if p['condition'] == held]
    assert all(p['predictions']['A'] < 0 and p['out_of_domain']['A'] for p in rows)
    expected = np.sqrt(np.mean([p['errors']['A']**2 for p in r['predictions']]))
    assert r['scores']['A']['rmse'] == pytest.approx(expected)
    assert r['point_domain']['A']['physical_predictions'] >= len(rows)
    assert r['coverage_per_arm'] == len(shots)


def test_zero_references_decisions_and_nine_boundaries():
    r = model.evaluate([replace(s, filtered_tds_pp=0) for s in fixture()], draws=3)
    assert r['decision']['primary'] == 'AFFINE_MATCHED_COMPARISON_UNRESOLVED'
    assert r['decision']['selection'] == 'AFFINE_NOT_SELECTED_RETAIN_PRIOR_P_QUALIFICATION'
    for c in r['contrasts'].values():
        assert c['gain'] is None and c['gain_ci95'] is None and c['gain_undefined_draws'] == 3
        assert c['difference_ci95'] == [0, 0] and len(c['boundary_check']) == 9
    for a in model.ARMS: assert r['scores'][a]['rmse_ci95'] == [0, 0]
    comparisons = {k: {'difference_ci95': [-2, -1]} for k in ('A/M', 'A/P', 'A/N')}
    assert model.decisions(comparisons)['selection'] == 'AFFINE_CONDITIONAL_ADDED_VALUE_OVER_M_P_N'
    comparisons['A/P']['difference_ci95'] = [-1, 0]
    assert model.decisions(comparisons)['primary'] == 'AFFINE_LOWER_THAN_MATCHED_M'
    assert model.decisions(comparisons)['selection'].startswith('AFFINE_NOT_SELECTED')
    comparisons['A/M']['difference_ci95'] = [0, 1]
    assert model.decisions(comparisons)['primary'] == 'AFFINE_MATCHED_COMPARISON_UNRESOLVED'
    comparisons['A/M']['difference_ci95'] = [1, 2]
    assert model.decisions(comparisons)['primary'] == 'M_LOWER_THAN_AFFINE'


def test_failed_draw_preserves_attempt_and_suppresses_success_only_cis(monkeypatch):
    original = model.cross_predict; calls = 0
    def fail(*args, **kwargs):
        nonlocal calls
        calls += 1
        if calls == 3: raise ValueError('synthetic second draw failure')
        return original(*args, **kwargs)
    monkeypatch.setattr(model, 'cross_predict', fail)
    r = model.evaluate(fixture(), draws=4)
    assert (r['bootstrap']['completed'], r['bootstrap']['failed'], r['bootstrap']['not_run']) == (1, 1, 2)
    assert len(r['bootstrap']['failures'][0]['multiplicities']) == len(fixture())
    assert r['decision']['selection'] == r['decision']['primary'] == 'INCOMPLETE_BOOTSTRAP'
    assert all(v['difference_ci95'] is None for v in r['contrasts'].values())
    assert all(v['rmse_ci95'] is None for v in r['scores'].values())


def test_condition_deletion_reruns_remaining_loco_and_predecessor_is_unchanged():
    shots = fixture(); old = pooled.evaluate(shots, draws=3)
    before = json.dumps(old, sort_keys=True)
    r = model.evaluate(shots, draws=3, reference=old, reference_draws=old['bootstrap_samples'])
    assert r['reference_reproduction']['point_max_difference_pp'] <= 1e-10
    assert r['reference_reproduction']['draw_max_difference_pp'] <= 1e-10
    assert r['reference_reproduction']['multiplicities_verified'] == 3
    assert json.dumps(old, sort_keys=True) == before
    assert parent.ARMS == ('M', 'C', 'N') and pooled.ARMS == basket.ARMS == ('M', 'C', 'N', 'P')
    d = model.deletion_influence(shots, r)
    assert len(d['deletions']) == 6
    for row in d['deletions']:
        subset = [s for s in shots if s.condition != row['deleted']]
        x, y, style, group = parent.arrays(subset)
        p, fits = model.cross_predict(x, y, style, group)
        assert len(row['folds']) == row['conditions'] == 5 and row['n'] == len(subset)
        assert row['folds'] == fits and row['scores'] == model.scores(y, p, group)
    old['predictions'][0]['predictions']['P'] += 1e-4
    with pytest.raises(ValueError, match='point reference drift'):
        model.evaluate(shots, draws=3, reference=old)

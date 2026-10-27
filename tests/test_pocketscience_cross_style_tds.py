"""Synthetic-only style-transfer tests; no source-derived numeric fixtures."""
from dataclasses import replace

import numpy as np
import pytest
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled
from puckworks.analysis import pocketscience_cross_basket_tds as basket
from puckworks.analysis import pocketscience_cross_style_tds as model
from tools import pocketscience_cross_style_tds as runner


def fixture():
    shots = []
    for sheet in (basket.SOURCE, basket.TARGET):
        for grinder, style in parent.STYLE_MAP.items():
            for material in (('Brass', 'Teflon') if sheet == basket.SOURCE else ('Teflon',)):
                for screen in ('Y', 'N'):
                    g = len(shots)//5
                    for i in range(5):
                        shots.append(parent.Shot(sheet, 100+len(shots), (sheet, grinder, screen, material),
                            style, .017+.0001*i, .035+.001*g+.0003*i,
                            6+.2*g+.1*i, 7+.2*g+.05*i))
    # Synthetic exclusions on both styles; allocation must come from style, not basket.
    return [replace(s, source_excluded=True) if i in (0, 21, 26) else s for i, s in enumerate(shots)]


def test_targets_cannot_change_source_fits_or_predictions():
    shots = [s for s in fixture() if not s.source_excluded]
    changed = [replace(s, filtered_tds_pp=99, unfiltered_tds_pp=98)
               if s.style == 'turbo' else s for s in shots]
    for observation in ('filtered', 'unfiltered'):
        a, b = [model.evaluate(s, observation, draws=4) for s in (shots, changed)]
        assert a['source_fit'] == b['source_fit']
        assert [p['predictions'] for p in a['predictions']] == [p['predictions'] for p in b['predictions']]
        for u, v in zip(a['bootstrap_samples'], b['bootstrap_samples'], strict=True):
            assert u['multiplicities'] == v['multiplicities'] and u['fit'] == v['fit']
        assert a['scores'] != b['scores']


def test_weighted_fits_and_scores_match_literal_rows_and_bounded_solver():
    shots = fixture()
    source, target = model.split(shots)
    x, y, _, g = parent.arrays(shots)
    for _ in range(5):
        w = parent.bootstrap_weights(g, np.random.default_rng(63+_))
        assert all(w[g == k].sum() == (g == k).sum() for k in np.unique(g))
        f = model.fit_source(x[source], y[source], w[source], oracle=True)
        copies = np.repeat(np.flatnonzero(source), w[source])
        literal = model.fit_source(x[copies], y[copies])
        p = model.predict(f['coefficients'], x[target])
        np.testing.assert_allclose(p, model.predict(literal['coefficients'], x[target]), atol=1e-10, rtol=0)
        for j, arm in enumerate(model.ARMS):
            z = x[copies] if arm == 'P' else np.ones(len(copies))
            solved = lsq_linear(z[:, None], y[copies], bounds=(0, 100), method='bvls', tol=1e-14)
            assert solved.success
            expected = solved.x[0]*(x[target] if arm == 'P' else np.ones(target.sum()))
            np.testing.assert_allclose(p[:, j], expected, atol=1e-10, rtol=0)
        repeated = np.repeat(np.flatnonzero(target), w[target])
        weighted = model.scores(y[target], p, g[target], w[target])
        expanded = model.scores(y[repeated], model.predict(f['coefficients'], x[repeated]), g[repeated])
        for arm in model.ARMS:
            assert weighted[arm] == pytest.approx(expanded[arm])


def test_style_partition_order_coverage_and_all60_additions():
    shots = fixture()
    r = runner.style_splits(shots)
    primary = [s for s in shots if not s.source_excluded]
    source, target = model.split(primary)
    assert not (source & target).any() and (source | target).all()
    assert set(r['primary']['source']).isdisjoint(r['primary']['target'])
    assert r['primary']['original_order'] == [s.identity for s in primary]
    assert [len(r['primary'][k]) for k in ('source_conditions', 'target_conditions')] == [6, 6]
    assert [len(r['all60'][k]) for k in ('source', 'target')] == [30, 30]
    for a in r['additions']:
        shot = next(s for s in shots if s.identity == a['identity'])
        assert a['side'] == ('source' if shot.style == 'traditional' else 'target')
        assert shot.identity in r['all60'][a['side']] and shot.identity not in r['primary'][a['side']]
    evaluated = model.evaluate(primary, draws=2)
    assert evaluated['coverage_per_arm'] == target.sum()
    assert [(p['sheet'], p['row']) for p in evaluated['predictions']] == r['primary']['target']
    assert len(evaluated['condition_errors']) == 6 and len(evaluated['basket_errors']) == 2
    with pytest.raises(ValueError, match='duplicate'):
        model.split(primary+[primary[0]])
    with pytest.raises(ValueError, match='partition'):
        model.split([s for s in shots if s.style == 'traditional'])


def test_deleting_target_preserves_source_fit_and_source_deletion_keeps_all_targets():
    shots = [s for s in fixture() if not s.source_excluded]
    point = model.evaluate(shots, draws=2)
    r = model.deletion_influence(shots, point)
    assert len(r['deletions']) == 12
    for d in r['deletions']:
        if d['side'] == 'target':
            assert d['source_fit'] is point['source_fit']
            assert d['training_n'] == point['training_n']
        else:
            assert d['evaluation_n'] == point['evaluation_n']
            assert d['training_n'] < point['training_n']


@pytest.mark.parametrize('bad', [np.nan, np.inf, -1., 0.])
def test_invalid_predictors(bad):
    with pytest.raises(ValueError):
        model.fit_source([bad], [5])


@pytest.mark.parametrize('weights', [[0, 0], [-1, 2], [np.nan, 1], [1]])
def test_invalid_training_weights(weights):
    with pytest.raises(ValueError):
        model.fit_source([.2, .4], [3, 6], weights)


def test_active_bounds_and_nonfinite_observations():
    for y, expected in [([-4, -2], 0), ([150, 200], 100)]:
        fit = model.fit_source([.2, .3], y, oracle=True)
        assert fit['coefficients'] == dict(P=expected, N=expected)
        assert all(fit['active_bounds'].values())
        assert model.oracle_error(fit, [.1, .5]) <= 1e-10
    with pytest.raises(ValueError):
        model.fit_source([.2], [np.nan])
    with pytest.raises(ValueError):
        model.scores([1], [[np.nan, 1]], [0])
    with pytest.raises(ValueError):
        model.scores([1], [[1, 1]], [0], [0])


def test_zero_reference_and_zero_endpoints_preserve_absolute_contrasts():
    result = model.evaluate([replace(s, filtered_tds_pp=0) for s in fixture()], draws=4)
    c = result['contrasts']['P/N']
    assert c['gain'] is None and c['gain_ci95'] is None and c['gain_undefined_draws'] == 4
    assert c['difference_ci95'] == [0, 0] and len(c['boundary_check']) == 9
    assert result['decision'] == 'CROSS_STYLE_COMPARISON_UNRESOLVED'
    for ci, expected in [([-2, -1], 'P_CROSS_STYLE_ADDED_VALUE_OVER_N'),
                         ([1, 2], 'N_LOWER_CROSS_STYLE_LOSS'),
                         ([-1, 0], 'CROSS_STYLE_COMPARISON_UNRESOLVED'),
                         ([0, 1], 'CROSS_STYLE_COMPARISON_UNRESOLVED')]:
        assert model.decision({'P/N': {'difference_ci95': ci}}) == expected
    c = model.contrasts({'P': {'rmse': 1}, 'N': {'rmse': 0}})['P/N']
    assert c == {'difference': 1, 'gain': None}


def test_failed_draw_preserves_multiplicities_and_blocks_inference(monkeypatch):
    original = model.fit_source
    def fail(x, y, weights=None, **kwargs):
        if weights is not None:
            raise ValueError('synthetic failed draw')
        return original(x, y, **kwargs)
    monkeypatch.setattr(model, 'fit_source', fail)
    r = model.evaluate(fixture(), draws=3)
    assert r['bootstrap']['requested'] == 3
    assert r['bootstrap']['failed'] == 1 and r['bootstrap']['not_run'] == 2
    assert r['bootstrap']['completed'] == 0
    assert len(r['bootstrap']['failures'][0]['multiplicities']) == 60
    assert r['decision'] == 'INCOMPLETE_BOOTSTRAP'
    assert r['contrasts']['P/N']['difference_ci95'] is None


def test_support_reports_missing_strata_and_retains_extrapolations():
    shots = fixture()
    # Remove one traditional preparation only; no matching support may be invented.
    remove = shots[0].condition
    shots = [replace(s, beverage_kg=.01) if s.style == 'turbo' else s
             for s in shots if s.condition != remove]
    r = model.evaluate(shots, draws=2)
    assert r['support']['overall']['target_extrapolation_count'] == r['evaluation_n']
    assert any(s['missing_training_support'] for s in r['support']['by_preparation'])
    assert any(p['extrapolation']['preparation'] is None for p in r['predictions'])
    assert r['coverage_per_arm'] == r['evaluation_n']


def test_predecessor_globals_and_both_style_rank_guards_unchanged():
    shots = [s for s in fixture() if s.style == 'traditional']
    x, y, style, group = parent.arrays(shots)
    assert parent.ARMS == ('M', 'C', 'N') and pooled.ARMS == basket.ARMS == ('M', 'C', 'N', 'P')
    with pytest.raises(ValueError, match='missing training style'):
        basket.split(shots)
    with pytest.raises(ValueError, match='rank'):
        basket.fit_source(x, y, style)
    with pytest.raises(ValueError, match='rank'):
        pooled.joint_predict(x, y, style, group)

"""Synthetic transfer tests; no private data or source-derived numeric fixtures."""
from dataclasses import replace

import numpy as np
import pytest
from scipy.optimize import lsq_linear

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled
from puckworks.analysis import pocketscience_cross_basket_tds as model


def fixture():
    return [parent.Shot(sheet, 10*g+i, (sheet, str(g)), style,
                        .02, .03+.002*g+.001*i, 7+.3*g+.1*i, 8+.2*g+.1*i)
            for sheet in (model.SOURCE, model.TARGET)
            for g, style in enumerate(['traditional', 'turbo']*2) for i in range(3)]


def test_target_changes_cannot_change_fits_or_predictions():
    shots = fixture()
    changed = [replace(s, filtered_tds_pp=99) if s.sheet == model.TARGET else s for s in shots]
    a, b = [model.evaluate(s, draws=4) for s in (shots, changed)]
    assert a['source_fit'] == b['source_fit']
    assert [p['predictions'] for p in a['predictions']] == [p['predictions'] for p in b['predictions']]
    for u, v in zip(a['bootstrap_samples'], b['bootstrap_samples'], strict=True):
        assert u['multiplicities'] == v['multiplicities'] and u['fit'] == v['fit']
    assert a['scores'] != b['scores']
    assert parent.ARMS == ('M', 'C', 'N') and pooled.ARMS == ('M', 'C', 'N', 'P')


def test_source_weighting_matches_literal_copies_and_independent_solver():
    shots = fixture()
    source, target = model.split(shots)
    x, y, s, g = parent.arrays(shots)
    rng = np.random.default_rng(20261026)
    for _ in range(6):
        w = parent.bootstrap_weights(g, rng)
        assert all(w[g == k].sum() == (g == k).sum() for k in np.unique(g))
        fit = model.fit_source(x[source], y[source], s[source], w[source], oracle=True)
        copies = np.repeat(np.flatnonzero(source), w[source])
        expanded = model.fit_source(x[copies], y[copies], s[copies])
        p = model.predict(fit, x[target], s[target])
        np.testing.assert_allclose(p, model.predict(expanded, x[target], s[target]), atol=1e-10, rtol=0)
        for j, arm in enumerate(model.ARMS):
            a = model.design(x[copies], s[copies], arm)
            solved = lsq_linear(a, y[copies], bounds=(0,100), method='bvls', tol=1e-14)
            assert solved.success
            np.testing.assert_allclose(p[:, j], model.design(x[target], s[target], arm)@solved.x,
                                       atol=1e-10, rtol=0)
        targets = np.repeat(np.flatnonzero(target), w[target])
        weighted = pooled.scores(y[target], p, g[target], w[target])
        literal = pooled.scores(y[targets], model.predict(fit, x[targets], s[targets]), g[targets])
        for arm in model.ARMS:
            assert weighted[arm] == pytest.approx(literal[arm])
        assert fit['training_sse']['M'] <= fit['training_sse']['P']+fit['nesting_roundoff_allowance']


def test_split_identity_coverage_and_condition_deletions():
    shots = fixture()
    source, target = model.split(shots)
    assert not (source & target).any() and (source | target).all()
    assert {s.identity for s in shots if s.sheet == model.SOURCE}.isdisjoint(
        s.identity for s in shots if s.sheet == model.TARGET)
    result = model.evaluate(shots, draws=3)
    assert result['coverage_per_arm'] == 12
    assert [(p['sheet'], p['row']) for p in result['predictions']] == [
        s.identity for s in shots if s.sheet == model.TARGET]
    deletion = model.deletion_influence(shots, result)
    assert len(deletion['deletions']) == 8
    for row in deletion['deletions']:
        if row['side'] == 'target':
            assert row['source_fit'] is result['source_fit']
        else:
            assert row['evaluation_n'] == result['evaluation_n']
    with pytest.raises(ValueError, match='duplicate'):
        model.split(shots+[shots[0]])


def test_missing_styles_rank_invalid_values_and_bounds():
    shots = fixture()
    with pytest.raises(ValueError, match='missing training style'):
        model.split([s for s in shots if s.sheet == model.TARGET or s.style == 'turbo'])
    x, y, s, _ = parent.arrays(shots)
    with pytest.raises(ValueError, match='rank'):
        model.fit_source(x, y, s, (s == 0).astype(int))
    with pytest.raises(ValueError, match='rank'):
        model.fit_source(x*0, y, s)
    for bad in (np.full(len(x), np.nan), -np.ones(len(x)), np.zeros(len(x))):
        with pytest.raises(ValueError):
            model.fit_source(x, y, s, bad)
    fit = model.fit_source(x*.001, y, s, oracle=True)
    assert fit['parameters']['P']['active_bounds'] == [True]
    assert model.oracle_error(fit, x*.001, s) <= 1e-10


def test_zero_reference_decision_boundaries_and_undefined_counts():
    result = model.evaluate([replace(s, filtered_tds_pp=0) for s in fixture()], draws=4)
    c = result['contrasts']['P/N']
    assert c['gain'] is None and c['gain_ci95'] is None and c['gain_undefined_draws'] == 4
    assert c['difference_ci95'] == [0., 0.] and len(c['boundary_check']) == 9
    assert result['decision'] == 'TRANSFER_COMPARISON_UNRESOLVED'
    for ci, expected in [([-2,-1], 'P_TRANSFER_ADDED_VALUE_OVER_N'),
                         ([1,2], 'N_LOWER_TRANSFER_LOSS'),
                         ([-1,0], 'TRANSFER_COMPARISON_UNRESOLVED'),
                         ([0,1], 'TRANSFER_COMPARISON_UNRESOLVED')]:
        assert model.decision({'P/N': {'difference_ci95': ci}}) == expected


def test_failed_draws_block_decision_and_intervals(monkeypatch):
    original = model.fit_source
    def fail(*args, **kwargs):
        if len(args) > 3:
            raise ValueError('synthetic failed draw')
        return original(*args, **kwargs)
    monkeypatch.setattr(model, 'fit_source', fail)
    result = model.evaluate(fixture(), draws=3)
    assert result['bootstrap']['requested'] == result['bootstrap']['failed'] == 3
    assert result['bootstrap']['completed'] == 0
    assert result['decision'] == 'INCOMPLETE_BOOTSTRAP'
    assert all(c['difference_ci95'] is None for c in result['contrasts'].values())

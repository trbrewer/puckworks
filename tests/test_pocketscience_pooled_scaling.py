"""Synthetic public tests; no source values, identifiers or private files."""
from dataclasses import replace
import numpy as np
import pytest
from scipy.optimize import minimize_scalar

from puckworks.analysis import pocketscience_cup_tds as parent
from puckworks.analysis import pocketscience_pooled_scaling as pooled


def fixture():
    return [parent.Shot('synthetic', 1+10*g+i, ('synthetic', str(g)), style,
                        .02, .035+.003*g+.001*i, 8+.4*g+.1*i, 8.1+.4*g+.1*i)
            for g, style in enumerate(['traditional', 'turbo']*3) for i in range(3)]


def test_nesting_and_independently_solved_p():
    x, y, style, group = parent.arrays(fixture())
    p, fits, checks = pooled.joint_predict(x, y, style, group, oracle=True)
    for f, check in zip(fits, checks):
        train = group != f['condition_index']
        solved = minimize_scalar(lambda alpha: np.sum((alpha*x[train]-y[train])**2),
                                 bounds=(0,100), method='bounded')
        assert f['parameters']['P']['coefficients'][0] == pytest.approx(solved.x, abs=1e-10)
        assert check['sse_M'] <= check['sse_P']+check['roundoff_allowance']
        assert check['oracle_max_difference_pp'] <= 1e-10


def test_held_targets_and_predecessor_unchanged():
    x, y, style, group = parent.arrays(fixture())
    legacy, fits = parent.cross_predict(x, y, style, group)
    p, _, _ = pooled.joint_predict(x, y, style, group)
    np.testing.assert_array_equal(p[:, :3], legacy)
    assert parent.ARMS == ('M','C','N')
    for g in np.unique(group):
        altered = y.copy()
        altered[group == g] += 20
        q, _, _ = pooled.joint_predict(x, altered, style, group)
        np.testing.assert_array_equal(p[group == g], q[group == g])


def test_one_global_multiplicity_equals_literal_copies():
    x, y, style, group = parent.arrays(fixture())
    rng = np.random.default_rng(20261026)
    for _ in range(8):
        w = parent.bootstrap_weights(group, rng)
        p, _, checks = pooled.joint_predict(x, y, style, group, w, oracle=True)
        idx = np.repeat(np.arange(len(y)), w)
        q, _, _ = pooled.joint_predict(x[idx], y[idx], style[idx], group[idx])
        np.testing.assert_allclose(p[idx], q, atol=1e-10, rtol=0)
        for a in pooled.ARMS:
            assert pooled.scores(y, p, group, w)[a] == pytest.approx(pooled.scores(y[idx], q, group[idx])[a])
        assert all(c['sse_M'] <= c['sse_P']+c['roundoff_allowance'] for c in checks)


def test_bootstrap_parent_reproduction_and_drift_detection():
    shots = fixture()
    old = parent.evaluate(shots, draws=13)
    new = pooled.evaluate(shots, draws=13)
    assert pooled.verify_predecessor(new, old, old['bootstrap_samples'])['max_absolute_difference_pp'] == 0
    old['predictions'][0]['predictions']['M'] += 1e-5
    with pytest.raises(ValueError, match='numerical drift'):
        pooled.verify_predecessor(new, old, old['bootstrap_samples'])


def test_bounds_zero_reference_and_rank():
    shots = [replace(s, filtered_tds_pp=0) for s in fixture()]
    result = pooled.evaluate(shots, draws=3)
    assert result['contrasts']['P/N']['gain'] is None
    assert result['contrasts']['M/P']['gain_ci95'] is None
    x,y,s,g = parent.arrays(fixture())
    _, fits, _ = pooled.joint_predict(x*.001, y, s, g, oracle=True)
    assert all(f['parameters']['P']['active_bounds'] == [True] for f in fits)
    with pytest.raises(ValueError, match='rank'):
        pooled.joint_predict(x, y, s, s)


def test_frozen_decision_and_failed_draws(monkeypatch):
    def decision(mp,pn,failed=0):
        return pooled.decision({'M/P':{'gain_ci95':mp},'P/N':{'gain_ci95':pn}}, failed)
    assert decision([.01,.2],[.1,.3])['status'].startswith('STRATIFICATION_EARNS')
    assert decision([-.2,-.01],[.1,.3])['status'] == 'POOLED_SCALING_CONDITIONALLY_BETTER'
    assert decision([-.1,.1],[.1,.3]) == {'status':'M/P_UNRESOLVED', 'supported_parsimonious_alternative':True, 'historical_M_qualification':'PRESERVED_NOT_REVISED'}
    assert decision([-.2,-.01],[-.1,.3])['status'].startswith('UNRESOLVED_RETAIN')
    original = pooled.joint_predict
    def fail_draw(*args, **kwargs):
        if len(args) >= 5:
            raise ValueError('synthetic bootstrap failure')
        return original(*args, **kwargs)
    monkeypatch.setattr(pooled, 'joint_predict', fail_draw)
    result = pooled.evaluate(fixture(), draws=2)
    assert result['bootstrap']['failed'] == 2 and result['bootstrap']['completed'] == 0
    assert result['decision']['status'] == 'INCOMPLETE_BOOTSTRAP'
    assert result['contrasts']['M/P']['gain_ci95'] is None

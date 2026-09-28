"""Synthetic-only tests of the fixed training architecture and budget receipts."""
from dataclasses import replace

import numpy as np
import pytest

from puckworks.analysis import conditional_5cqa_delivery as m
from puckworks.analysis import conditional_5cqa_training as t


def synthetic_shots(arm='D0'):
    result = []
    for design in (1, 2, 3):
        for rep in (1, 2, 3):
            masses = (.003+design*.0001, .004+rep*.0001)
            windows = (t.Window(3, sum(masses), .014, .001+design*.0001, .014-sum(masses)),
                       t.Window(5, .025, .03, .0005+rep*.0001, .005))
            result.append(t.Shot(f'FIT-E{design:02d}-R{rep}', f'FIT-C{design:02d}',
                                 m.EarlyInput(arm, masses, 'SYNTHETIC'), windows))
    return tuple(result)


def test_five_cqa_whole_design_fold_exclusion():
    shots = synthetic_shots()
    training, held = t.split_design(shots, 'FIT-C02')
    assert len(held) == 3 and len(training) == 6
    assert all(s.group == 'FIT-C02' for s in held)
    assert not {s.shot for s in training} & {s.shot for s in held}
    changed = tuple(replace(s, windows=tuple(replace(w, q=100*w.q) for w in s.windows),
                            inputs=m.EarlyInput('D0', (.001, .002), 'SYNTHETIC')) if s.group == 'FIT-C02' else s for s in shots)
    retained, _ = t.split_design(changed, 'FIT-C02')
    p, q = t.FitProblem(training, .01, scope='SYNTHETIC'), t.FitProblem(retained, .01, scope='SYNTHETIC')
    assert training == retained and p.domain == q.domain
    np.testing.assert_array_equal(p.means, q.means)
    np.testing.assert_array_equal(p.starts, q.starts)
    np.testing.assert_array_equal(p.residual(p.starts[0]), q.residual(q.starts[0]))


def test_exponential_and_d0_share_condition_shot_measured_window_weights():
    d0, k0 = synthetic_shots(), synthetic_shots('E0')
    # An intentionally unequal number of physical shots tests the hierarchy.
    d0, k0 = d0[:-1], k0[:-1]
    np.testing.assert_array_equal(t.weights(d0), t.weights(k0))
    for group in ('FIT-C01', 'FIT-C02', 'FIT-C03'):
        assert sum(w for s, w in zip(d0, t.shot_weights(d0)) if s.group == group) == pytest.approx(1/3)
    problem = t.FitProblem(k0, None, scope='SYNTHETIC')
    assert t.EXPONENTIAL_STARTS_KG == (.01,.03,.10)
    for initial, length in zip(problem.starts, t.EXPONENTIAL_STARTS_KG):
        kernel = m.exponential_integrals([w.start_kg for w in problem.windows],
            [w.end_kg for w in problem.windows], 1., length)/problem.widths
        assert initial[0] == pytest.approx(np.sum(problem.weights*kernel*problem.q)/np.sum(problem.weights*kernel**2))
        assert np.exp(initial[1]) == pytest.approx(length)


def test_inherited_d0_settings_and_task_scale():
    p = t.FitProblem(synthetic_shots(), .01, scope='SYNTHETIC')
    assert t.LAMBDAS == (.0001, .01, 1., 100.) and t.START_ORDER == (-1, 0, 1)
    theta = np.asarray(p.starts[1]).reshape(5, 3)
    expected = 1000/.25*(float(p.weights @ p.q)-p.q)*np.sqrt(p.weights)
    np.testing.assert_allclose(p.residual(theta.ravel())[:len(p.q)], expected, atol=1e-14, rtol=0)
    assert np.all(theta[:, 1:] == 0)
    assert t.select_lambda([{'lambda': .0001, 'status': 'SELECTABLE', 'balanced_R_mg_g': .1},
                            {'lambda': 100., 'status': 'SELECTABLE', 'balanced_R_mg_g': .1000005}]) == 100.


def test_actual_numerical_jacobian_calls_are_counted(tmp_path):
    budget = t.Budget(tmp_path/'starts', synthetic=True)
    model, audit = t.fit(synthetic_shots(), 1., budget, 'D0.synthetic', 'SYNTHETIC',
                         'SYNTHETIC_FIRST_PARTY', scope='SYNTHETIC')
    assert model is not None and len(audit['starts']) == 3
    for start in audit['starts']:
        assert 0 < start['numerical_jacobian_residual_calls'] < start['actual_residual_calls'] <= 8000
        assert start['actual_residual_calls'] > start['nfev']


def test_budget_cannot_reset_or_repair_incomplete_attempt(tmp_path):
    directory = tmp_path/'starts'
    budget = t.Budget(directory, synthetic=True)
    stamp = budget.clock['started_unix']
    budget.start('D0.synthetic.incomplete', 0, np.zeros(15))
    budget.worker_lock.close()
    with pytest.raises(t.BudgetReached, match='INCOMPLETE_ATTEMPT'):
        t.Budget(directory, synthetic=True)
    assert m.strict_json((directory/'clock.json').read_text())['started_unix'] == stamp


def test_synthetic_exponential_parameter_recovery_from_interval_averages(tmp_path):
    amplitude, length = .007, .027
    shots = synthetic_shots('E0')
    shots = tuple(replace(s, windows=tuple(replace(w, q=float(m.exponential_integrals(
        [w.start_kg], [w.end_kg], amplitude, length)[0]/(w.end_kg-w.start_kg))) for w in s.windows)) for s in shots)
    budget = t.Budget(tmp_path/'starts', synthetic=True)
    model, audit = t.fit(shots, None, budget, 'E0.synthetic', 'SYNTHETIC', 'SYNTHETIC_FIRST_PARTY', scope='SYNTHETIC')
    assert model.amplitude == pytest.approx(amplitude, rel=1e-8)
    assert model.decay_kg == pytest.approx(length, rel=1e-8)
    assert len(audit['starts']) == 3
    assert all(r['actual_residual_calls'] == r['nfev']+r['numerical_jacobian_residual_calls'] for r in audit['starts'])


def test_exception_keeps_start_and_failure_call_accounting(tmp_path, monkeypatch):
    budget = t.Budget(tmp_path/'starts', synthetic=True)
    def broken(*args): raise FloatingPointError('synthetic material defect')
    monkeypatch.setattr(t.FitProblem, 'residual', broken)
    with pytest.raises(FloatingPointError):
        t.fit(synthetic_shots('E0'), None, budget, 'E0.failure', 'SYNTHETIC', 'SYNTHETIC', scope='SYNTHETIC')
    end, = (tmp_path/'starts').glob('*.end.json')
    record = m.strict_json(end.read_text())
    assert record['status']=='FAILED' and record['actual_residual_calls']==1
    assert len(list((tmp_path/'starts').glob('*.start.json')))==1

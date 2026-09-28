"""Synthetic-only tests of the fixed training architecture and budget receipts."""
from dataclasses import replace

import numpy as np
import pytest

from puckworks.analysis import conditional_trigonelline_delivery as m
from puckworks.analysis import conditional_trigonelline_training as t


def synthetic_shots(arm='TR-D0'):
    result = []
    for design in (1, 2, 3):
        for rep in (1, 2, 3):
            masses = (.003+design*.0001, .004+rep*.0001)
            windows = (t.Window(3, sum(masses), .014, .001+design*.0001, .014-sum(masses)),
                       t.Window(5, .025, .03, .0005+rep*.0001, .005))
            result.append(t.Shot(f'FIT-E{design:02d}-R{rep}', f'FIT-C{design:02d}',
                                 m.EarlyInput(arm, masses, 'SYNTHETIC'), windows))
    return tuple(result)


def test_trigonelline_whole_design_fold_exclusion():
    shots = synthetic_shots()
    training, held = t.split_design(shots, 'FIT-C02')
    assert len(held) == 3 and len(training) == 6
    assert all(s.group == 'FIT-C02' for s in held)
    assert not {s.shot for s in training} & {s.shot for s in held}
    changed = tuple(replace(s, windows=tuple(replace(w, q=100*w.q) for w in s.windows),
                            inputs=m.EarlyInput('TR-D0', (.001, .002), 'SYNTHETIC')) if s.group == 'FIT-C02' else s for s in shots)
    retained, _ = t.split_design(changed, 'FIT-C02')
    p, q = t.FitProblem(training, .01, scope='SYNTHETIC'), t.FitProblem(retained, .01, scope='SYNTHETIC')
    assert training == retained and p.domain == q.domain
    np.testing.assert_array_equal(p.means, q.means)
    np.testing.assert_array_equal(p.starts, q.starts)
    np.testing.assert_array_equal(p.residual(p.starts[0]), q.residual(q.starts[0]))


def test_constant_and_d0_share_condition_shot_measured_window_weights(tmp_path):
    d0, k0 = synthetic_shots(), synthetic_shots('TR-K0')
    # An intentionally unequal number of physical shots tests the hierarchy.
    d0, k0 = d0[:-1], k0[:-1]
    np.testing.assert_array_equal(t.weights(d0), t.weights(k0))
    for group in ('FIT-C01', 'FIT-C02', 'FIT-C03'):
        assert sum(w for s, w in zip(d0, t.shot_weights(d0)) if s.group == group) == pytest.approx(1/3)
    budget = t.Budget(tmp_path/'starts', synthetic=True)
    model, _ = t.fit_constant(k0, budget, 'synthetic', 'SYNTHETIC', 'SYNTHETIC_FIRST_PARTY', scope='SYNTHETIC')
    expected = float(t.weights(k0) @ np.asarray([w.q for s in k0 for w in s.windows]))
    assert model.constant_q == expected
    assert not list((tmp_path/'starts').glob('*.start.json'))


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
    model, audit = t.fit(synthetic_shots(), 1., budget, 'synthetic.D0', 'SYNTHETIC',
                         'SYNTHETIC_FIRST_PARTY', scope='SYNTHETIC')
    assert model is not None and len(audit['starts']) == 3
    for start in audit['starts']:
        assert 0 < start['numerical_jacobian_residual_calls'] < start['actual_residual_calls'] <= 8000
        assert start['actual_residual_calls'] > start['nfev']


def test_budget_cannot_reset_or_repair_incomplete_attempt(tmp_path):
    directory = tmp_path/'starts'
    budget = t.Budget(directory, synthetic=True)
    stamp = budget.clock['started_unix']
    budget.start('synthetic.incomplete', 0, np.zeros(15))
    budget.worker_lock.close()
    with pytest.raises(t.BudgetReached, match='INCOMPLETE_ATTEMPT'):
        t.Budget(directory, synthetic=True)
    assert m.strict_json((directory/'clock.json').read_text())['started_unix'] == stamp

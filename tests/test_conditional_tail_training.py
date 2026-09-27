from dataclasses import replace

import numpy as np
import pytest

from puckworks.analysis import conditional_tail_training as t
from puckworks.analysis import conditional_tail_delivery as m


def fixture():
    return tuple(t.TrainingShot(f'FIT-E{i:02d}-R{j}', f'FIT-C{i:02d}',
        m.EarlyInput('C2', (.003+i*.0001, .003+j*.0001, .15+i*.01, .08+j*.01)),
        (t.Window(3,.01,.02,.07+i*.001),t.Window(5,.03,.04+i*.001,.03)))
        for i in (1,2,3) for j in (1,2,3))


def test_balanced_objective_and_exact_penalty():
    shots = fixture()
    problem = t.FitProblem(shots, .01)
    theta = np.linspace(-.2, .2, problem.size).reshape(problem.shape)
    r = problem.residual(theta.ravel())
    pred = problem.geometry.integrate((problem.features @ theta.T)[problem.row_shots])/problem.masses
    manual = np.sum(problem.weights*(100*(pred-problem.q))**2)+.01*(
        np.mean(theta[:,1:]**2)+np.mean((np.diff(theta,n=2,axis=0)/(.25**2))**2))
    assert r @ r == pytest.approx(manual, rel=1e-14)
    assert problem.weights.sum() == pytest.approx(1.)
    for i, shot in enumerate(shots):
        assert problem.weights[problem.row_shots == i].sum() == pytest.approx(1/9)
    for index, sign in enumerate((-1,0,1)):
        a = problem.starts[index].reshape(problem.shape)
        assert np.all(a[:,1:] == 0)
        assert a[-1,0]-a[0,0] == pytest.approx(2*sign)


def test_fold_isolation_including_center_domain_and_initialization():
    original = fixture()
    group, train, held, domain, support = t.folds(original)[0]
    changed = tuple(replace(s, inputs=m.EarlyInput('C2',(.01,.01,.7,.8)),
        windows=(t.Window(3,.04,.09,.8),)) if s.group == group else s for s in original)
    _, other_train, _, other_domain, _ = t.folds(changed)[0]
    p, q = t.FitProblem(train,.01), t.FitProblem(other_train,.01)
    assert train == other_train
    assert domain == other_domain
    assert np.array_equal(p.means,q.means)
    assert all(np.array_equal(a,b) for a,b in zip(p.starts,q.starts))
    assert not {s.shot for s in train} & {s.shot for s in held}
    assert len({s.group for s in held}) == 1
    assert all(s.startswith('FIT-') for s,f in support)


def test_lambda_tie_nonselectable_and_failure_rules():
    entries = [{'lambda':l,'balanced_R_pp':1.+i*1e-7,'status':'SELECTABLE'} for i,l in enumerate(t.LAMBDAS)]
    assert t.select_lambda(entries) == 100
    entries[-1]['status'] = 'NONSELECTABLE'
    entries[-1]['balanced_R_pp'] = 0
    assert t.select_lambda(entries) == 1
    with pytest.raises(ValueError):
        t.select_lambda([dict(e,status='NONSELECTABLE') for e in entries])


def test_fit_rejects_pred_and_conditioning_response():
    with pytest.raises(ValueError):
        replace(fixture()[0], campaign='PREDICTION_2022_03')
    with pytest.raises(ValueError):
        replace(fixture()[0], shot='PRED-E01-R1')
    with pytest.raises(ValueError):
        t.Window(2,.003,.006,.1)


def test_arm_projection_removes_forbidden_assays():
    records = [{'shot': s.shot, 'group':s.group, 'early_values':s.inputs.values,
                'windows':[{'fraction':w.fraction,'start_kg':w.start_kg,'end_kg':w.end_kg,'q':w.q} for w in s.windows]} for s in fixture()]
    zero = t.project_arm(records,'C0')
    one = t.project_arm(records,'C1')
    for r in records:
        r['early_values'] = (*r['early_values'][:2],.99,.98)
    assert zero == t.project_arm(records,'C0')
    assert one != t.project_arm(records,'C1')
    for r,s in zip(records,fixture()):
        r['early_values'] = (*s.inputs.values[:3],.99)
    assert one == t.project_arm(records,'C1')


def test_recorded_failure_does_not_retry_or_delete_start(tmp_path, monkeypatch):
    def failure(fun, initial, **kwargs):
        fun(initial)
        raise ValueError('SYNTHETIC_SOLVER_FAILURE')
    monkeypatch.setattr(t, 'least_squares', failure)
    budget = t.Budget(tmp_path/'starts', apply_memory_limit=False)
    model, audit = t.fit(fixture(),.01,budget,'synthetic','SYNTHETIC','SYNTHETIC')
    assert model is None and len(audit['starts']) == 3
    assert sum(s['actual_residual_calls'] for s in audit['starts']) == 3
    assert len(list((tmp_path/'starts').glob('*.start.json'))) == 3
    with pytest.raises(FileExistsError):
        t.fit(fixture(),.01,budget,'synthetic','SYNTHETIC','SYNTHETIC')

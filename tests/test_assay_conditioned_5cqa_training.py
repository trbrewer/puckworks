"""Synthetic-only grouped fitting, D0 objective nesting, and durable accounting."""
from dataclasses import replace

import numpy as np
import pytest

from puckworks.analysis import assay_conditioned_5cqa_delivery as m
from puckworks.analysis import assay_conditioned_5cqa_training as t
from puckworks.analysis import conditional_5cqa_delivery as old_m
from puckworks.analysis import conditional_5cqa_training as old_t


def synthetic_shots():
    result=[]
    for design in (1,2,3):
        for rep in (1,2,3):
            inputs=m.EarlyInput(.003+design*.0001,.004+rep*.0001,.002+design*.0001,'SYNTHETIC')
            anchor=sum(inputs.values[:2])
            windows=(t.Window(3,anchor,.014,.001+design*.0001,.014-anchor),
                     t.Window(5,.025,.03,.0005+rep*.0001,.005))
            result.append(t.Shot(f'FIT-E{design:02d}-R{rep}',f'FIT-C{design:02d}',inputs,windows))
    return tuple(result)


def test_whole_design_training_only_transforms_domain_and_starts():
    shots=synthetic_shots()
    retained,held=t.split_design(shots,'FIT-C02')
    assert len(retained)==6 and len(held)==3
    assert not {s.shot for s in retained}&{s.shot for s in held}
    changed=tuple(replace(s,inputs=m.EarlyInput(.001,.002,.9),
                          windows=(t.Window(10,.06,.068,.1,.008),))
                  if s.group=='FIT-C02' else s for s in shots)
    safe,_=t.split_design(changed,'FIT-C02')
    a,b=t.FitProblem(retained,.01),t.FitProblem(safe,.01)
    assert retained==safe and a.domain==b.domain==.03
    np.testing.assert_array_equal(a.means,b.means)
    np.testing.assert_array_equal(a.minima,b.minima)
    np.testing.assert_array_equal(a.maxima,b.maxima)
    np.testing.assert_array_equal(a.starts,b.starts)
    np.testing.assert_array_equal(a.residual(a.starts[0]),b.residual(b.starts[0]))
    assert a.features.shape==(6,4) and a.shape==(5,4)
    assert t.LAMBDAS==(.0001,.01,1.,100.) and t.START_ORDER==(-1,0,1)
    assert m.SCALES==(.01,.01,.01)
    for start in a.starts:
        assert np.all(start.reshape(5,4)[:,1:]==0)


def test_preserved_d0_fixed_lambda_objective_and_separate_assay_penalties():
    shots=synthetic_shots()[:-1]
    previous=tuple(old_t.Shot(s.shot,s.group,old_m.EarlyInput('D0',s.inputs.values[:2]),
        tuple(old_t.Window(w.fraction,w.start_kg,w.end_kg,w.q,w.mass_kg) for w in s.windows)) for s in shots)
    new,old=t.FitProblem(shots,.01),old_t.FitProblem(previous,.01)
    theta=np.array([[-6-j*.25,.1*j,-.2*j] for j in range(5)])
    expanded=np.c_[theta,np.zeros(5)]
    nr,orr=new.residual(expanded.ravel()),old.residual(theta.ravel())
    np.testing.assert_allclose(nr[:len(orr)],orr,rtol=0,atol=1e-14)
    np.testing.assert_array_equal(nr[len(orr):],np.zeros(8))
    assert nr@nr==pytest.approx(orr@orr,rel=2e-15)
    expanded[:,3]=[.1,.3,.8,.6,-.1]
    r=new.residual(expanded.ravel())
    np.testing.assert_array_equal(r[len(new.q):len(new.q)+19],orr[len(old.q):])
    np.testing.assert_allclose(r[-8:-3],expanded[:,3]*np.sqrt(.01/5),atol=0)
    np.testing.assert_allclose(r[-3:],np.diff(expanded[:,3],n=2)/.25**2*np.sqrt(.01/3),atol=0)
    for group in {s.group for s in shots}:
        assert sum(w for s,w in zip(shots,t.shot_weights(shots)) if s.group==group)==pytest.approx(1/3)
    assert t.weights(shots).sum()==pytest.approx(1)


def test_only_l1_and_intact_fit_shots_can_train():
    shots=synthetic_shots()
    with pytest.raises(ValueError): t.validate(shots+(shots[0],))
    with pytest.raises(ValueError): replace(shots[0],campaign='PREDICTION_2022_03')
    with pytest.raises(ValueError): replace(shots[0],windows=(shots[0].windows[0],)*2)
    for arm in ('E0','D0','A1','S2'):
        with pytest.raises(ValueError,match='ONLY_L1'): t.project_arm([],arm)
    with pytest.raises(ValueError): t.FitProblem(shots,.001)
    with pytest.raises(ValueError): t.Window(2,.01,.02,.001,.01)
    with pytest.raises(ValueError): t.Window(3,.01,.02,1.01,.01)


def test_lambda_selection_largest_tie_and_numerical_ambiguity():
    def candidate(lam,value,allowance=0.,status='SELECTABLE'):
        return dict(lambda_=lam,balanced_R_mg_g=value,R_allowance_mg_g=allowance,status=status)|{'lambda':lam}
    assert t.select_lambda([candidate(.0001,.1),candidate(100.,.1000005)])==100.
    with pytest.raises(ValueError,match='UNRESOLVED'):
        t.select_lambda([candidate(.0001,.1,1e-7),candidate(100.,.100001,1e-7)])
    with pytest.raises(ValueError,match='NO_SELECTABLE'):
        t.select_lambda([candidate(1.,None,status='NONSELECTABLE')])


def test_synthetic_fit_actual_jacobian_calls_and_replay(tmp_path):
    b=t.Budget(tmp_path/'starts',synthetic=True)
    model,audit=t.fit(synthetic_shots(),1.,b,'L1.synthetic','SYNTHETIC','SYNTHETIC_FIRST_PARTY',scope='SYNTHETIC')
    assert model is not None and len(audit['starts'])==3 and np.asarray(model.theta).shape==(5,4)
    for start in audit['starts']:
        assert start['actual_residual_calls']==start['nfev']+start['numerical_jacobian_residual_calls']
        assert 0<start['numerical_jacobian_residual_calls']<start['actual_residual_calls']<=8000
    support={(s.shot,w.fraction) for s in synthetic_shots() for w in s.windows}
    metric=t.held_metrics(model,synthetic_shots(),support)
    assert metric['R_allowance_mg_g']>=0 and metric['max_allowance_kg']<=1e-9
    b.worker_lock.close()


def test_budget_lock_persistence_deadline_and_non_l1_rejection(tmp_path,monkeypatch):
    b=t.Budget(tmp_path/'starts',synthetic=True)
    with pytest.raises(t.BudgetReached,match='ONE_WORKER'): t.Budget(tmp_path/'starts',synthetic=True)
    with pytest.raises(ValueError,match='ONLY_L1'): b.start('A1.forbidden',0,np.zeros(20))
    stamp=b.clock['started_unix'];b.start('L1.incomplete',0,np.zeros(20));b.worker_lock.close()
    with pytest.raises(t.BudgetReached,match='INCOMPLETE'): t.Budget(tmp_path/'starts',synthetic=True)
    assert m.strict_json((tmp_path/'starts/clock.json').read_text())['started_unix']==stamp
    assert t.LIMITS['max_starts']==183 and t.LIMITS['max_wall_seconds']==3600
    from datetime import datetime
    assert t.TASK_DEADLINE==datetime.fromisoformat('2026-09-29T18:22:32+00:00').timestamp()


def test_failed_attempt_retained_and_8000_actual_call_ceiling(tmp_path,monkeypatch):
    b=t.Budget(tmp_path/'starts',synthetic=True)
    def consume(fun,x,**kwargs):
        for _ in range(8001): fun(x)
    monkeypatch.setattr(t,'least_squares',consume)
    monkeypatch.setattr(t.FitProblem,'residual',lambda self,x:np.zeros(1))
    with pytest.raises(t.BudgetReached,match='EIGHT_THOUSAND'):
        t.fit(synthetic_shots(),1.,b,'L1.synthetic','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    end,=(tmp_path/'starts').glob('*.end.json')
    record=m.strict_json(end.read_text())
    assert record['status']=='FAILED' and record['actual_residual_calls']==8000
    assert len(list((tmp_path/'starts').glob('*.start.json')))==1
    b.worker_lock.close()

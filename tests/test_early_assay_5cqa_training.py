"""Synthetic matched cohorts, nested objectives and durable bounded attempts."""
from dataclasses import replace
from datetime import datetime

import numpy as np
import pytest

from puckworks.analysis import early_assay_5cqa_delivery as m
from puckworks.analysis import early_assay_5cqa_training as t
from puckworks.analysis import assay_conditioned_5cqa_delivery as old_m
from puckworks.analysis import assay_conditioned_5cqa_training as old_t


def records():
    result=[]
    for design in (1,2,3):
        for rep in (1,2,3):
            early=[.003+design*.0001,.004+rep*.0001,.002+design*.0001,.001+rep*.0001]
            anchor=sum(early[:2])
            result.append(dict(shot=f'FIT-E{design:02d}-R{rep}',group=f'FIT-C{design:02d}',early_values=early,
                windows=[dict(fraction=3,start_kg=anchor,end_kg=.014,q=.001+design*.0001,mass_kg=.014-anchor),
                         dict(fraction=5,start_kg=.025,end_kg=.03,q=.0005+rep*.0001,mass_kg=.005)]))
    return result


def synthetic_shots(arm='L1M'):
    return t.project_arm(records(),arm)


@pytest.mark.parametrize('arm',m.ARMS)
def test_whole_design_fold_local_transforms_domain_and_initialization(arm):
    shots=synthetic_shots(arm);retained,held=t.split_design(shots,'FIT-C02')
    assert len(retained)==6 and len(held)==3
    assert not {s.shot for s in retained}&{s.shot for s in held}
    changed=tuple(replace(s,inputs=replace(s.inputs,m1_kg=.001,m2_kg=.002),
                         windows=(t.Window(10,.06,.068,.1,.008),)) if s.group=='FIT-C02' else s for s in shots)
    safe,_=t.split_design(changed,'FIT-C02');a,b=t.FitProblem(retained,.01),t.FitProblem(safe,.01)
    assert retained==safe and a.domain==b.domain==.03
    for name in ('means','minima','maxima','starts','features','weights'):
        np.testing.assert_array_equal(getattr(a,name),getattr(b,name))
    np.testing.assert_array_equal(a.residual(a.starts[0]),b.residual(b.starts[0]))
    assert a.shape==(5,5 if arm=='L12' else 4)
    assert t.LAMBDAS==(.0001,.01,1.,100.) and t.START_ORDER==(-1,0,1)
    assert m.scales(arm)==(.01,)*len(m.feature_names(arm))
    for start in a.starts: assert np.all(start.reshape(a.shape)[:,1:]==0)


@pytest.mark.parametrize('arm,poison_index',[('L1M',3),('L2M',2)])
def test_forbidden_assay_poison_invariance(arm,poison_index):
    class Poison:
        def __float__(self): raise AssertionError('forbidden chemical covariate')
    raw=records();a=t.project_arm(raw,arm)
    for row in raw: row['early_values'][poison_index]=Poison()
    b=t.project_arm(raw,arm)
    assert a==b
    p,q=t.FitProblem(a,.01),t.FitProblem(b,.01)
    np.testing.assert_array_equal(p.starts,q.starts)
    np.testing.assert_array_equal(p.residual(p.starts[0]),q.residual(q.starts[0]))
    assert t.provenance(p,'synthetic','SYNTHETIC')==t.provenance(q,'synthetic','SYNTHETIC')


@pytest.mark.parametrize('lam',t.LAMBDAS)
def test_fixed_lambda_nesting_shared_transforms_and_separate_chemical_penalties(lam):
    raw=records()[:-1]
    problems={arm:t.FitProblem(t.project_arm(raw,arm),lam) for arm in m.ARMS}
    p12=problems['L12'];theta=np.array([[-6-j*.25,.1*j,-.2*j,.12*j] for j in range(5)])
    for arm,indices in [('L1M',[0,1,2,3]),('L2M',[0,1,2,4])]:
        p=problems[arm];expanded=np.zeros((5,5));expanded[:,indices]=theta
        np.testing.assert_array_equal(p.means,p12.means[[i-1 for i in indices[1:]]])
        np.testing.assert_array_equal(p.features,p12.features[:,indices])
        a,b=p.residual(theta.ravel()),p12.residual(expanded.ravel())
        np.testing.assert_allclose(a[:len(p.q)+19],b[:len(p.q)+19],rtol=0,atol=1e-14)
        np.testing.assert_array_equal(a[-8:],b[-16:-8] if arm=='L1M' else b[-8:])
        np.testing.assert_array_equal(b[-8:] if arm=='L1M' else b[-16:-8],np.zeros(8))
        assert a@a==pytest.approx(b@b,rel=2e-15)
        mm=p.model(theta,{'species':'5CQA'},'SYNTHETIC');nn=p12.model(expanded,{'species':'5CQA'},'SYNTHETIC')
        x=mm.condition(p.shots[0].inputs).remaining_5cqa(.03)
        y=nn.condition(p12.shots[0].inputs).remaining_5cqa(.03)
        assert abs(x.five_cqa_kg-y.five_cqa_kg)<=x.allowance_kg+y.allowance_kg
    shots=problems['L1M'].shots
    oldshots=tuple(old_t.Shot(s.shot,s.group,old_m.EarlyInput(*s.inputs.values),
        tuple(old_t.Window(w.fraction,w.start_kg,w.end_kg,w.q,w.mass_kg) for w in s.windows)) for s in shots)
    old=old_t.FitProblem(oldshots,lam)
    np.testing.assert_allclose(problems['L1M'].residual(theta.ravel()),old.residual(theta.ravel()),atol=1e-14,rtol=0)
    for group in {s.group for s in shots}:
        assert sum(w for s,w in zip(shots,t.shot_weights(shots)) if s.group==group)==pytest.approx(1/3)
    assert t.weights(shots).sum()==pytest.approx(1)


def test_invalid_training_records_and_lambda_ambiguity():
    shots=synthetic_shots()
    with pytest.raises(ValueError): t.validate(shots+(shots[0],))
    with pytest.raises(ValueError): t.validate(shots+synthetic_shots('L2M'))
    with pytest.raises(ValueError): replace(shots[0],campaign='PREDICTION_2022_03')
    with pytest.raises(ValueError): replace(shots[0],windows=(shots[0].windows[0],)*2)
    for arm in ('E0','D0','A1','L1','S2'):
        with pytest.raises(ValueError): t.project_arm([],arm)
    with pytest.raises(ValueError): t.FitProblem(shots,.001)
    with pytest.raises(ValueError): t.Window(2,.01,.02,.001,.01)
    def c(lam,value,allowance=0.,status='SELECTABLE'):
        return {'lambda':lam,'balanced_R_mg_g':value,'R_allowance_mg_g':allowance,'status':status}
    assert t.select_lambda([c(.0001,.1),c(100.,.1000005)])==100.
    with pytest.raises(ValueError,match='UNRESOLVED'): t.select_lambda([c(.0001,.1,1e-7),c(100.,.100001,1e-7)])
    with pytest.raises(ValueError,match='NO_SELECTABLE'): t.select_lambda([c(1.,None,status='NONSELECTABLE')])


@pytest.mark.parametrize('arm',m.ARMS)
def test_synthetic_fit_actual_jacobian_calls_and_numerical_allowances(tmp_path,arm):
    b=t.Budget(tmp_path/'starts',synthetic=True)
    try:
        shots=synthetic_shots(arm)
        model,audit=t.fit(shots,1.,b,arm+'.synthetic','SYNTHETIC','SYNTHETIC_FIRST_PARTY',scope='SYNTHETIC')
        assert model is not None and len(audit['starts'])==3
        for start in audit['starts']:
            assert start['actual_residual_calls']==start['nfev']+start['numerical_jacobian_residual_calls']
            assert 0<start['numerical_jacobian_residual_calls']<start['actual_residual_calls']<=8000
        support={(s.shot,w.fraction) for s in shots for w in s.windows}
        metric=t.held_metrics(model,shots,support)
        assert metric['R_allowance_mg_g']>=0 and metric['max_allowance_kg']<=1e-9
    finally: b.worker_lock.close()


def test_budget_lock_persistence_deadline_and_arm_limits(tmp_path):
    b=t.Budget(tmp_path/'starts',synthetic=True)
    with pytest.raises(t.BudgetReached,match='ONE_WORKER'): t.Budget(tmp_path/'starts',synthetic=True)
    with pytest.raises(ValueError,match='ONLY_DECLARED'): b.start('A1.forbidden',0,np.zeros(20))
    stamp=b.clock['started_unix'];b.start('L1M.incomplete',0,np.zeros(20));b.worker_lock.close()
    with pytest.raises(t.BudgetReached,match='INCOMPLETE'): t.Budget(tmp_path/'starts',synthetic=True)
    assert m.strict_json((tmp_path/'starts/clock.json').read_text())['started_unix']==stamp
    assert t.LIMITS['max_starts']==549 and t.LIMITS['max_wall_seconds']==3600
    assert t.TASK_DEADLINE==datetime.fromisoformat('2026-09-29T22:34:51+00:00').timestamp()
    b=t.Budget(tmp_path/'full_arm',synthetic=True)
    for i in range(183): (b.directory/f'L1M.retained.{i}.start.json').write_text('{}')
    with pytest.raises(t.BudgetReached,match='183'): b.start('L1M.extra',0,np.zeros(20))
    for i in range(366): (b.directory/f'L2M.retained.{i}.start.json').write_text('{}')
    with pytest.raises(t.BudgetReached,match='FIVE_HUNDRED'): b.start('L12.extra',0,np.zeros(25))
    b.worker_lock.close()


def test_failed_attempt_retained_and_actual_call_ceiling(tmp_path,monkeypatch):
    b=t.Budget(tmp_path/'starts',synthetic=True)
    def consume(fun,x,**kwargs):
        for _ in range(8001): fun(x)
    monkeypatch.setattr(t,'least_squares',consume)
    monkeypatch.setattr(t.FitProblem,'residual',lambda self,x:np.zeros(1))
    with pytest.raises(t.BudgetReached,match='EIGHT_THOUSAND'):
        t.fit(synthetic_shots(),1.,b,'L1M.synthetic','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    end,=(tmp_path/'starts').glob('*.end.json');record=m.strict_json(end.read_text())
    assert record['status']=='FAILED' and record['actual_residual_calls']==8000
    assert len(list((tmp_path/'starts').glob('*.start.json')))==1
    b.worker_lock.close()

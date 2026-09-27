"""Synthetic FIT-only loss, grouping, budget and recovery tests."""
from dataclasses import replace
import json

import numpy as np
import pytest
from scipy.special import logit

from puckworks.analysis import conditional_caffeine_delivery as md
from puckworks.analysis import conditional_caffeine_training as tr


def fixture(arm='S2',q=.005):
    p=md.parent.synthetic_model('C2');p=replace(p,theta=[[float(logit(.05)),0,0,0,0]]*5)
    shots=tuple(tr.Shot(f'FIT-E{g:02}-R{r}',f'FIT-C{g:02}',
        md.EarlyInput(arm,(.004,.004,.15,.1)[:len(md.feature_names(arm))],'SYNTHETIC'),
        (tr.Window(3,.008,.02,q),tr.Window(5,.02,.06,q))) for g in (1,2) for r in (1,2,3))
    return shots,p


def test_weight_and_exact_loss_normalization():
    shots,p=fixture('S1');problem=tr.FitProblem(shots,.01,p,scope='SYNTHETIC')
    w=tr.weights(shots)
    assert sum(w)==pytest.approx(1)
    assert w[0]/w[1]==pytest.approx(.012/.04)
    theta=np.zeros(problem.shape);theta[:,0]=logit(.1)
    residual=problem.residual(theta.ravel())
    assert residual@residual < 1e-25
    theta[0,1]=.2;theta[2,0]+=.1
    residual=problem.residual(theta.ravel())
    data=residual[:len(w)]
    expected=data@data+.01*(np.mean(theta[:,1:]**2)+np.mean((np.diff(theta,n=2,axis=0)/.25**2)**2))
    assert residual@residual==pytest.approx(expected)
    assert len(problem.starts)==3
    for start in problem.starts:assert not np.asarray(start).reshape(problem.shape)[:,1:].any()


@pytest.mark.parametrize('arm',['D0','S1','S2'])
def test_recoverable_constant_three_starts(tmp_path,arm):
    shots,p=fixture(arm)
    budget=tr.Budget(tmp_path/'starts',apply_memory_limit=False)
    model,audit=tr.fit(shots,.0001,p,budget,'synthetic', 'SYNTHETIC', 'SYNTHETIC',scope='SYNTHETIC')
    assert model is not None and audit['status']=='CONVERGED'
    assert len(audit['starts'])==3 and len(list((tmp_path/'starts').glob('*.start.json')))==3
    result=model.condition(shots[0].inputs).predict_intervals([.008],[.06])[0]
    assert result.caffeine_mg_g==pytest.approx(5.,abs=1e-5)
    assert all(r['actual_residual_calls'] <= 8000 for r in audit['starts'])
    with pytest.raises(FileExistsError):tr.fit(shots,.0001,p,budget,'synthetic','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')


def test_scalar_weighted_LS_and_misspecification_boundary(tmp_path):
    shots,p=fixture('S0')
    budget=tr.Budget(tmp_path/'starts',apply_memory_limit=False)
    m,a=tr.fit_scalar(shots,p,budget,'recover','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    assert m.share==pytest.approx(.1) and not a['boundary_solution']
    bad,p=fixture('S0',q=.06)
    m,a=tr.fit_scalar(bad,p,budget,'misspecified','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    assert m.share==1 and a['boundary_solution'] and a['unconstrained_share']>1
    assert m.condition(bad[0].inputs).remaining_caffeine(.06).caffeine_mg_g==pytest.approx(50)
    assert bad[0].windows[0].q==.06  # observation remains unchanged


def test_design_grouping_and_full_parent_exclusion(tmp_path):
    shots,p=fixture()
    p=replace(p,training_identity_json=md.canonical({'scope':'FIT_ONLY','groups':['FIT-C01','FIT-C02'],
            'shots':[s.shot for s in shots]}))
    records=[{'shot':s.shot,'group':s.group,'early_values':s.inputs.values,'windows':[tr.asdict(w) for w in s.windows]} for s in shots]
    dest=tmp_path/'dev';dest.mkdir()
    with pytest.raises(ValueError,match='PARENT_LEAKAGE'):
        tr.develop(records,[{'group':'FIT-C01'}],{'FIT-C01':p},dest,
                   tr.Budget(tmp_path/'starts',apply_memory_limit=False),'synthetic','synthetic')
    assert not list((tmp_path/'starts').glob('*.start.json'))
    with pytest.raises(ValueError):replace(shots[0],campaign='PREDICTION_2022_03')
    with pytest.raises(ValueError):tr.Window(1,.008,.02,.01)


def test_tie_and_failed_candidate_not_selected():
    cs=[{'lambda':.0001,'balanced_R_mg_g':1.,'status':'SELECTABLE'},
        {'lambda':100.,'balanced_R_mg_g':1.0000009,'status':'SELECTABLE'},
        {'lambda':.01,'balanced_R_mg_g':0.,'status':'NONSELECTABLE'}]
    assert tr.select_lambda(cs)==100


def test_budget_durable_start_ceiling(tmp_path):
    b=tr.Budget(tmp_path/'starts',apply_memory_limit=False)
    clock=json.loads(b.clock_path.read_text());clock['max_starts']=1;b.clock_path.write_text(json.dumps(clock))
    b=tr.Budget(tmp_path/'starts',apply_memory_limit=False);b.start('one',0,[0])
    with pytest.raises(tr.BudgetReached):tr.Budget(tmp_path/'starts',apply_memory_limit=False).start('two',0,[0])

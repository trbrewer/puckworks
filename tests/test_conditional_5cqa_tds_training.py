"""Synthetic tests for the fixed 5-CQA head development rules."""
from dataclasses import asdict, replace
import numpy as np
import pytest
from scipy.special import logit
from puckworks.analysis import conditional_5cqa_tds_delivery as md
from puckworks.analysis import conditional_5cqa_tds_training as tr


def fixture(arm='S2',q=.005):
    p=md.parent.synthetic_model('C2');p=replace(p,theta=[[float(logit(.05)),0,0,0,0]]*5)
    shots=tuple(tr.Shot(f'FIT-E{g:02}-R{r}',f'FIT-C{g:02}',
        md.EarlyInput(arm,(.004,.004,.15,.1),'SYNTHETIC'),
        (tr.Window(3,.008,.02,q,.012),tr.Window(5,.02,.06,q,.04))) for g in (1,2) for r in (1,2,3))
    return shots,p


def test_exact_penalty_scale_starts_and_hierarchical_weights():
    shots,p=fixture('S1');problem=tr.FitProblem(shots,.01,p,scope='SYNTHETIC')
    w=tr.weights(shots); assert sum(w)==pytest.approx(1)
    assert w[0]/w[1]==pytest.approx(.012/.04)
    theta=np.zeros(problem.shape);theta[:,0]=logit(.1)
    residual=problem.residual(theta.ravel());assert residual@residual < 1e-25
    theta[0,1]=.2;theta[2,0]+=.1
    residual=problem.residual(theta.ravel())
    predictions=problem.geometry.integrate((problem.features@theta.T)[problem.row_shots],problem.parent_values)/problem.widths
    data=(1000/.25)*(predictions-problem.q)*np.sqrt(w)
    assert residual[:len(w)]==pytest.approx(data)
    expected=data@data+.01*(np.mean(theta[:,1:]**2)+np.mean((np.diff(theta,n=2,axis=0)/.25**2)**2))
    assert residual@residual==pytest.approx(expected)
    for ramp,start in zip((-1,0,1),problem.starts):
        t=start.reshape(problem.shape)
        assert not t[:,1:].any()
        assert t[:,0]==pytest.approx(logit(.1)+ramp*np.linspace(-1,1,5))
    unequal=shots[:2]+shots[3:]
    weights=tr.weights(unequal)
    assert sum(weights[:4])==pytest.approx(.5)
    assert sum(weights[4:])==pytest.approx(.5)


@pytest.mark.parametrize('q,expected,boundary',[(0.,0.,True),(.005,.1,False),(.06,1.,True)])
def test_scalar_closed_form_and_boundaries(tmp_path,q,expected,boundary):
    shots,p=fixture('S0',q)
    b=tr.Budget(tmp_path/'starts',synthetic=True)
    try:m,a=tr.fit_scalar(shots,p,b,'S0.fixture','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    finally:b.worker_lock.close()
    assert m.share==pytest.approx(expected) and a['boundary_solution']==boundary
    assert a['denominator']==pytest.approx(.05**2)
    assert a['unconstrained_share']==pytest.approx(q/.05)
    assert not list((tmp_path/'starts').glob('*.start.json'))
    assert all(w.q==q for s in shots for w in s.windows)


def test_scalar_invalid_denominator_and_independent_formula():
    x=np.array([.01,.03,.02]);y=np.array([.002,.001,.003]);w=np.array([.2,.3,.5])
    r=tr.bounded_scalar(x,y,w)
    assert r['share']==pytest.approx(sum(w*x*y)/sum(w*x*x))
    for x in [[0,0],[float('nan'),.1]]:
        with pytest.raises(ValueError):tr.bounded_scalar(x,[.1,.1],[.5,.5])


@pytest.mark.parametrize('arm',['S1','S2'])
def test_three_start_constant_recovery(tmp_path,arm):
    shots,p=fixture(arm);b=tr.Budget(tmp_path/'starts',synthetic=True)
    try:m,a=tr.fit(shots,.0001,p,b,arm+'.fixture','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    finally:b.worker_lock.close()
    assert m and a['status']=='CONVERGED' and len(a['starts'])==3
    assert m.condition(shots[0].inputs).remaining_5cqa(.06).five_cqa_mg_g==pytest.approx(5.,abs=1e-5)
    assert all(r['actual_residual_calls']<=8000 for r in a['starts'])


def test_synthetic_s2_distinguishable_tds_head_at_fixed_masses(tmp_path):
    base,p=fixture('S2'); truth=replace(md.synthetic_model('S2'),
        theta=[[-3,0,0,1.8,-.6]]*5,parent_json=md.canonical(p.to_dict()))
    shots=[]
    for i,(q1,q2) in enumerate([(.06,.05),(.10,.07),(.14,.06),(.18,.14),(.22,.10),(.26,.18)]):
        inputs=md.EarlyInput('S2',(.004,.004,q1,q2),'SYNTHETIC')
        s=truth.condition(inputs)
        ps=s.predict_intervals([.008,.02],[.02,.06])
        ws=tuple(tr.Window(f,a,b,v.five_cqa_mg_g/1000,b-a) for f,a,b,v in zip((3,5),(.008,.02),(.02,.06),ps))
        shots.append(tr.Shot(f'FIT-E{i+1:02}-R1',f'FIT-C{i+1:02}',inputs,ws))
    b=tr.Budget(tmp_path/'starts',synthetic=True)
    try:m,a=tr.fit(tuple(shots),.0001,p,b,'S2.dependence','SYNTHETIC','SYNTHETIC',scope='SYNTHETIC')
    finally:b.worker_lock.close()
    lo=m.condition(shots[0].inputs).remaining_5cqa(.06).five_cqa_mg_g
    hi=m.condition(shots[-1].inputs).remaining_5cqa(.06).five_cqa_mg_g
    assert hi-lo>.5
    assert a['status']=='CONVERGED'  # No demand for unique coefficient recovery.


def test_numerical_bounds_can_block_lambda_tie():
    cs=[{'lambda':.0001,'balanced_R_mg_g':1.,'R_allowance_mg_g':1e-12,'status':'SELECTABLE'},
        {'lambda':100.,'balanced_R_mg_g':1.0000009,'R_allowance_mg_g':1e-12,'status':'SELECTABLE'}]
    assert tr.select_lambda(cs)==100
    cs[1]['R_allowance_mg_g']=2e-7
    with pytest.raises(ValueError,match='NUMERICALLY_UNRESOLVED'):tr.select_lambda(cs)
    cs[1]['status']='NONSELECTABLE';assert tr.select_lambda(cs)==.0001


def test_parent_matrix_missing_and_held_leakage():
    shots,p=fixture();records=[{'shot':s.shot,'group':s.group} for s in shots]
    with pytest.raises(ValueError,match='FIFTEEN'):tr.validate_parent_matrix(records,[],{})
    records=[{'shot':f'FIT-E{g:02}-R{r}','group':f'FIT-C{g:02}'} for g in range(1,16) for r in (1,2,3)]
    p=replace(p,training_identity_json=md.canonical({'scope':'FIT_ONLY','groups':sorted({r['group'] for r in records}),'shots':[r['shot'] for r in records]}))
    specs=[{'group':f'FIT-C{g:02}'} for g in range(1,16)]
    with pytest.raises(ValueError,match='PARENT_LEAKAGE'):
        tr.validate_parent_matrix(records,specs,{s['group']:p for s in specs})
    with pytest.raises(ValueError):replace(shots[0],campaign='PREDICTION_2022_03')
    with pytest.raises(ValueError):tr.Window(1,.008,.02,.01,.012)


def test_budget_preserves_incomplete_and_one_worker(tmp_path):
    b=tr.Budget(tmp_path/'starts',synthetic=True)
    with pytest.raises(tr.BudgetReached,match='ONE_WORKER'):tr.Budget(tmp_path/'starts',synthetic=True)
    b.start('S1.one',0,[0]);b.worker_lock.close()
    with pytest.raises(tr.BudgetReached,match='INCOMPLETE'):tr.Budget(tmp_path/'starts',synthetic=True)


def test_future_fields_rejected_from_training_projection():
    shots,_=fixture();r={'shot':shots[0].shot,'group':shots[0].group,'early_values':shots[0].inputs.values,
                       'windows':[asdict(w) for w in shots[0].windows],'future_TDS':.2}
    with pytest.raises(ValueError,match='STRICT'):tr.project_arm([r],'S2')

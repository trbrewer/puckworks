"""Analytical conservation/observer/limiting verification, not physical validation."""
from dataclasses import replace
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from scipy.special import gammaincc
from puckworks.analysis import moroney_transfer as mt


def test_observation_units_and_pot_delivery():
    p=mt.observation(np.array([0.,10.,100.]), np.array([mt.RHO*.1]*3),[0,.001,.002])
    assert np.allclose(p['exit_mg_g'],100)
    assert np.allclose(p['pot_mg_g'][1:],[100,20])
    assert np.isnan(p['pot_mg_g'][0])
    assert np.allclose(mt.pot_delivery([10,100],[100,20]),[1,2])


@pytest.mark.parametrize('basis',['dose','hydraulic'])
@pytest.mark.parametrize('profile',['uniform','linear'])
def test_startup_and_full_budget(basis,profile):
    for c in [mt.DEEP,mt.SHALLOW]:
        y,_,_,_=mt.system(c,12,.1833,.0447,.77,.9,profile,basis)
        assert y.sum()==pytest.approx(mt.Y_MAX*c.dry_g/1000)
        p=mt.solve(c,n=12,basis=basis,profile=profile)
        total=p['delivered_g']+p['retained_mobile_g']+p['retained_internal_g']+p['remaining_surface_g']
        assert np.allclose(total,p['initial_inventory_g'],rtol=1e-6)
        assert p['balance_relative']<1e-6


def test_zero_transfer_pure_advection_analytic_chain():
    n=8; m=np.linspace(0,120,121)
    p=mt.solve(n=n,mass_g=m,alpha=0,beta=0,amplitude=.5)
    tau=mt.volumes()['mobile_m3']/mt.Q
    expected=mt.CSAT*.5*gammaincc(n,n*m/mt.DEEP.mass_flow_g_s/tau)*1000/mt.RHO
    assert np.allclose(p['exit_mg_g'],expected,atol=2e-4)


def test_zero_initial_dissolved_and_zero_transfer():
    p=mt.solve(n=5,split=1,amplitude=0,alpha=0,beta=0)
    assert np.all(p['exit_mg_g']==0)
    assert np.all(p['delivered_g']==0)


def test_closed_well_mixed_exchange_matches_batch_rhs():
    c=replace(mt.DEEP,flow_m3_s=0)
    y,rhs,_,v=mt.system(c,1,.1833,.0447,.77,0,'uniform','dose')
    dy=rhs(0,y)
    assert abs(dy.sum())<1e-17
    ch=y[0]/v['mobile_m3']; phi=v['phi_dry']+(y.sum()-y[2])/(mt.CS*v['grain_m3'])
    cv=y[1]/(phi*v['grain_m3'])
    av=.1833*phi**(4/3)*2.2e-9*6/(322.49e-6*282e-6)
    # Existing batch's corrected v->h sign and grain/mobile volume factor.
    assert dy[1]==pytest.approx(-v['grain_m3']*av*(cv-ch))
    sol=solve_ivp(rhs,[0,1000],y,method='BDF',rtol=1e-9,atol=1e-13)
    assert np.max(abs(sol.y.sum(axis=0)-y.sum()))<1e-10


def test_empirical_finite_inventory_and_derivative():
    pars=[.30,.6,20,200]; m=np.linspace(1,500,10000)
    for mode in ['N_M','N_T']:
        p=mt.empirical(m,pars,mt.SHALLOW,mode)
        assert np.all(p['delivered_g']<=mt.SHALLOW.dry_g*mt.Y_MAX)
        assert np.allclose(np.gradient(p['delivered_g'],m)[1:-1]*1000,p['exit_mg_g'][1:-1],rtol=3e-5)
    # With equal flow N_T preserves width; N_M preserves concentration vs M/dose.
    deep=mt.empirical(m,pars)
    shallow=mt.empirical(m*12.5/60,pars,mt.SHALLOW)
    assert np.allclose(deep['exit_mg_g'],shallow['exit_mg_g'])


def test_invalid_rejected_not_clipped():
    with pytest.raises(ValueError): mt.solve(split=.01,amplitude=1)
    with pytest.raises(ValueError): mt.solve(alpha=-1)
    with pytest.raises(ValueError): mt.empirical([1],[.9,.5,2,1])


def test_target_leakage_values_cannot_change_calibration_or_transfer(monkeypatch):
    from puckworks.analysis import moroney_transfer_run as run
    m=np.array([5.,20.,60.,200.,600.])
    pars=[.3,.75,20.,170.]
    truth=mt.empirical(m,pars)
    tr={'exit_mass':m,'exit_obs':truth['exit_mg_g'],'pot_mass':m,'pot_obs':truth['pot_mg_g']}
    cfg={'empirical_starts':[[.3,.75,np.log(20),np.log(150)]],
         'empirical_bounds':[[0,0,np.log(.5),np.log(.01)],[mt.Y_MAX,1,np.log(500),np.log(2000)]],
         'max_nfev':5,'pot_objective_weight':.25}
    original=run.rows
    def changed(name):
        rr=original(name)
        if name==run.F11:
            for r in rr: r['concentration_mg_per_g']='987654321'
        return rr
    a=run.calibrate(tr,cfg)
    monkeypatch.setattr(run,'rows',changed)
    assert all(r['concentration_mg_per_g']=='987654321' for r in run.rows(run.F11))
    b=run.calibrate(tr,cfg)
    assert a['records']==b['records']
    assert a['selected']==b['selected']
    for scaling in ['N_M','N_T']:
        p=mt.empirical(m,a['records'][0]['parameters'],mt.SHALLOW,scaling)
        q=mt.empirical(m,b['records'][0]['parameters'],mt.SHALLOW,scaling)
        assert np.array_equal(p['exit_mg_g'],q['exit_mg_g'])
    # Mechanistic solver accepts no target concentration and preserves exact trajectories.
    p=mt.solve(mt.SHALLOW,m,n=8); q=mt.solve(mt.SHALLOW,m,n=8)
    assert np.array_equal(p['exit_mg_g'],q['exit_mg_g'])


def test_published_control_is_separate_and_conservative():
    p=mt.solve(n=10,amplitude=1,published_control=True)
    assert p['balance_relative']<1e-6
    assert p['volumes']['phi_h']==.2
    # Historical Table2 inventory does not silently become the dose-bound prediction inventory.
    assert not np.isclose(p['initial_inventory_g'],mt.Y_MAX*mt.DEEP.dry_g,rtol=1e-4)
    with pytest.raises(ValueError): mt.solve(mt.SHALLOW,published_control=True)


def test_mechanistic_calibration_is_target_independent(monkeypatch):
    from puckworks.analysis import moroney_transfer_run as run
    m=np.array([10.,30.,100.,400.]); family=dict(profile='linear',amplitude=.5,basis='dose')
    truth=mt.solve(mass_g=m,n=8,**family)
    tr={'exit_mass':m,'exit_obs':truth['exit_mg_g'],'pot_mass':m,'pot_obs':truth['pot_mg_g']}
    cfg={'mechanistic_starts':[[np.log(.1833),np.log(.0447),.11/.143435]],
         'mechanistic_bounds':[[np.log(.01),np.log(.001),.65],[np.log(2),np.log(.5),.95]],
         'max_nfev':8,'pot_objective_weight':.25,'fit_cells':8}
    a=run.calibrate(tr,cfg,family)
    # Any source read from fitting would now fail, including a hidden target read.
    monkeypatch.setattr(run,'rows',lambda name: (_ for _ in ()).throw(AssertionError('source read in fit')))
    b=run.calibrate(tr,cfg,family)
    assert a['selected'] is not None
    assert a['records']==b['records']
    x,y=a['records'][0]['parameters'],b['records'][0]['parameters']
    p=mt.solve(mt.SHALLOW,m,n=8,alpha=x[0],beta=x[1],split=x[2],**family)
    q=mt.solve(mt.SHALLOW,m,n=8,alpha=y[0],beta=y[1],split=y[2],**family)
    assert np.array_equal(p['exit_mg_g'],q['exit_mg_g'])


def test_review_gate_fails_closed_before_source_confirmation(tmp_path,monkeypatch):
    from puckworks.analysis import moroney_transfer_run as run
    run.write_json(tmp_path/'freeze.json',{'files':{},'source_ready':False})
    monkeypatch.setattr(run,'DOC',tmp_path)
    with pytest.raises(ValueError,match='figure-object'):
        run.require_review(tmp_path/'nonexistent.json')


def test_bounds_mass_coordinate_and_monotonic_delivery():
    for basis in ['dose','hydraulic']:
        for c in [mt.DEEP,mt.SHALLOW]:
            for profile,amp in [('uniform',0),('uniform',1),('linear',1)]:
                for split in [.65,.95]:
                    y,_=mt.initial_state(c,5,split,amp,profile,basis)
                    assert y.min()>=0
    assert mt.DEEP.mass_flow_g_s==pytest.approx(4.02208333333)
    p=mt.solve(n=8)
    assert np.all(np.diff(p['delivered_g'])>=-1e-10)
    assert p['delivered_g'][-1] <= p['initial_inventory_g']


def test_closed_exchange_analytic_exponential():
    c=replace(mt.DEEP,flow_m3_s=0)
    y,rhs,_,v=mt.system(c,1,.1833,0,.77,0,'uniform','dose')
    phi=v['phi_dry']+(y.sum()-y[2])/(mt.CS*v['grain_m3'])
    capacity_h=v['mobile_m3']; capacity_v=phi*v['grain_m3']
    exchange=v['grain_m3']*.1833*phi**(4/3)*2.2e-9*6/(322.49e-6*282e-6)
    rate=exchange*(1/capacity_h+1/capacity_v)
    equilibrium=(y[0]+y[1])/(capacity_h+capacity_v)
    t=np.linspace(0,200,21)
    sol=solve_ivp(rhs,[0,200],y,t_eval=t,method='BDF',rtol=1e-10,atol=1e-14)
    exact=equilibrium*(1-np.exp(-rate*t))
    assert np.allclose(sol.y[0]/capacity_h,exact,rtol=1e-7,atol=1e-7)


def test_source_ready_requires_both_original_figure_audits(tmp_path,monkeypatch):
    from puckworks.analysis import moroney_transfer_run as run
    monkeypatch.setattr(run,'DOC',tmp_path)
    d={'pdf_sha256':'a'*64,'confirmed_legend_rows':['example'],'audits':{}}
    run.write_json(tmp_path/'source_objects.json',d)
    assert not run.source_ready([])
    for figure,page in [('fig11',233),('fig3',219)]:
        d['audits'][figure]={'printed_page':page,'panels':['a','b'],'visual_confirmation':True,
            'axis_coordinates':[1,2],'marker_objects':[3],'classification_evidence':'synthetic fixture'}
        run.write_json(tmp_path/'source_objects.json',d)
    assert run.source_ready([])


def test_no_silent_prediction_support_extrapolation():
    p={'mass_g':[1,2],'exit_mg_g':[10,5],'delivered_g':[.01,.015]}
    with pytest.raises(ValueError,match='outside'):
        mt.metrics(p,np.array([1,3]),np.array([10,5]),np.array([1,2]),np.array([10,5]),12)


def test_synthetic_pipeline_scores_and_renders_once(tmp_path,monkeypatch):
    import json
    from pathlib import Path
    from puckworks.analysis import moroney_transfer_run as run
    pytest.importorskip('matplotlib')
    doc=tmp_path/'doc';doc.mkdir()
    monkeypatch.setattr(run,'DOC',doc)
    config=json.loads((Path(run.ROOT)/'docs/analysis/sci_md_moroney_transfer_001/protocol.json').read_text())
    config['families']=config['families'][:1];config['resolutions']=[4,8,16]
    run.write_json(doc/'protocol.json',config)
    # High-readout DEEP endpoint exceeds every target coordinate: prior regression trigger.
    run.write_json(doc/'target_support.json',{'exit_mass':[4,20,80],'pot_mass':[4,20,80]})
    synthetic={}
    for name,c in [('deep',mt.DEEP),('shallow',mt.SHALLOW)]:
        m=np.array([5.,25.,100.]) if name=='deep' else np.array([4.,20.,80.])
        p=mt.empirical(m,[.3,.7,20,170],c)
        synthetic[name]={'exit_mass':m,'exit_obs':p['exit_mg_g'],'pot_mass':m,'pot_obs':p['pot_mg_g']}
    monkeypatch.setattr(run,'observations',lambda name:synthetic[name])
    monkeypatch.setattr(run,'rows',lambda name:[])  # no real source/model lines
    marker=tmp_path/'frozen-source';marker.write_text('synthetic')
    monkeypatch.setattr(run,'ROOT',tmp_path)
    run.write_json(doc/'freeze.json',{'files':{'frozen-source':run.digest(marker)},
        'source_ready':True,'runtime':run.runtime_identity()})
    review=tmp_path/'review.json'
    run.write_json(review,{'decision':'APPROVED_FOR_SCORING','reviewer':'SYNTHETIC_TEST_FIXTURE_NOT_REAL_APPROVAL',
        'thresholds_accepted':True,'freeze_sha256':run.digest(doc/'freeze.json')})
    def fake_fit(training,cfg,family):
        return {'selected':0,'admitted':[0],'records':[{'start':0,'parameters':[.3,.7,20,170] if family is None else [.1833,.0447,.77],'success':True}]}
    monkeypatch.setattr(run,'calibrate',fake_fit)
    out=tmp_path/'out';run.predict(review,out)
    assert json.loads((out/'prediction_freeze.json').read_text())['target_concentrations_attached'] is False
    predictions=json.loads((out/'predictions.json').read_text())
    for p in predictions.values(): assert 100.2 in p['mass_g']
    # Source/code mutation fails before target attachment despite an unchanged manifest.
    marker.write_text('changed')
    with pytest.raises(ValueError,match='frozen input changed'): run.score(out)
    marker.write_text('synthetic')
    run.score(out)
    assert all((out/f'figure{i}.png').exists() for i in [1,2,3])
    assert (out/'decisions.json').exists()
    with pytest.raises(ValueError,match='already scored'): run.score(out)


def test_decisions_reject_missing_baselines_and_diagnose_parameter_variation(tmp_path,monkeypatch):
    from puckworks.analysis import moroney_transfer_run as run
    monkeypatch.setattr(run,'DOC',tmp_path)
    cfg={'source_perturbations':[{'id':'central'},{'id':'low'}],
         'families':[{'id':'f','basis':'dose'}]}
    run.write_json(tmp_path/'protocol.json',cfg)
    fits={};scores={};num={}
    for perturb in ['central','low']:
        fits[perturb+'/f']={'selected':0,'admitted':[0,1]}
        fits[perturb+'/empirical']={'selected':None,'admitted':[]} if perturb=='low' else {'selected':0,'admitted':[0]}
        for start in [0,1]:
            for cond in ['deep','shallow']:
                k=f'{perturb}/f/{start}/{cond}'
                scores[k]={'outlet_rmse_mg_g':2.,'cumulative_max_ey_pp':.5}
                num[k]={'balance_relative':1e-12,'refinement':[{'outlet_rmse_mg_g':0.,'delivery_max_ey_pp':0.}]*3}
        if perturb=='central':
            for mode in ['N_M','N_T']:
                for cond in ['deep','shallow']:
                    scores[f'{perturb}/empirical/0/{mode}/{cond}']={'outlet_rmse_mg_g':4.,'cumulative_max_ey_pp':.5}
    run.write_json(tmp_path/'calibration.json',fits);run.write_json(tmp_path/'numerics.json',num)
    run.decide(tmp_path,scores)
    import json
    d=json.loads((tmp_path/'decisions.json').read_text())
    assert d['overall']=='UNRESOLVED'
    assert d['baselines']['N_M']['coverage']=='INCOMPLETE'
    # Complete comparators, two deep-adequate solutions with opposite target adequacy.
    fits['low/empirical']={'selected':0,'admitted':[0]}
    for k in list(scores):
        if '/empirical/' in k: scores[k.replace('central/','low/')]=scores[k]
        if '/f/1/shallow' in k: scores[k]['outlet_rmse_mg_g']=10
    run.write_json(tmp_path/'calibration.json',fits)
    run.decide(tmp_path,scores)
    d=json.loads((tmp_path/'decisions.json').read_text())
    assert d['overall']=='INITIALIZATION_OR_PARAMETER_LIMITED'
    assert d['families']['f']['parameter_decision_varies']

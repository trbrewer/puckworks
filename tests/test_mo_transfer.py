"""Focused conservation/source/fold tests; no real response calibration."""
import json
from pathlib import Path
import numpy as np
import pytest
from scipy.integrate import solve_ivp
from puckworks.analysis.mo_transfer import (Bed, simulate, populations, particle_derivative,
                                           radial_geometry, interpolate_supported)
from puckworks.analysis.mo_transfer_run import (grouped_folds, fit_predict, axis_decision,
    adequate, simpler_comparator, require_authority, freeze_predictions, score_once)

BED = Bed(.015,.029,.0135,.17,1000,.5)
ROOT = Path(__file__).resolve().parents[1]


def run(model='S2', inventory=.3, kinetic=.05, weights=(.2,.8), radii=(15e-6,180e-6), **kw):
    return simulate(model,BED,weights,radii,3e-6,inventory,kinetic,.8,
                    np.array([.005,.02,.08]),nz=6,nr=6,**kw)


@pytest.mark.parametrize('model,kinetic',[('S0',.05),('S2',.05),('D2',1e-11)])
def test_conservation_delivery_water_and_scaling(model,kinetic):
    a=run(model,kinetic=kinetic)
    b=run(model,inventory=.6,kinetic=kinetic)
    assert a['solute_balance_relative'] <= 1e-6
    assert a['water_balance_relative'] <= 1e-8
    assert a['min_state_inventory_fraction'] >= -a['positivity_tolerance_inventory_fraction']
    dry=a['trajectory_cup_m3']==0
    assert np.all(a['trajectory_delivered_kg'][dry]==0)
    assert np.all(np.diff(a['trajectory_delivered_kg'])>=-1e-12)
    np.testing.assert_allclose(b['ey_pct'],2*a['ey_pct'],rtol=1e-10)
    np.testing.assert_allclose(b['strength_pct'],2*a['strength_pct'],rtol=1e-10)
    np.testing.assert_allclose(a['ey_pct'], a['strength_pct']*a['masses_kg']/(BED.dose_kg*.5))
    np.testing.assert_allclose(a['particle_kg']+a['liquid_solute_kg']+a['delivered_whole_kg'],.0045,atol=1e-10)
    np.testing.assert_allclose(a['trajectory_cup_m3'][-1]*1000*.5,.08)


@pytest.mark.parametrize('model',['S0','S2','D2'])
def test_zero_inventory_and_release(model):
    zero=run(model,inventory=0,kinetic=1e-11 if model=='D2' else .05)
    stopped=run(model,kinetic=0)
    assert np.all(zero['ey_pct']==0)
    assert np.all(stopped['ey_pct']==0)
    np.testing.assert_allclose(stopped['particle_kg'],.0045)
    assert np.all(stopped['liquid_solute_kg']==0)


def test_interface_flux_is_identical_and_extraction_only():
    v=np.array([[.3,.7]])
    s=v[...,None]*np.ones((1,2,5))/5
    ds,gain=particle_derivative(s,v,np.array([1.,2.]),np.array([0.]),.1,.5,'D2')
    assert abs(ds.sum()+gain.sum())<1e-14
    ds,gain=particle_derivative(s,v,np.array([1.,2.]),np.array([100.]),.1,.5,'D2')
    assert gain[0]==0
    assert abs(ds.sum())<1e-14


@pytest.mark.parametrize('model,kinetic',[('S2',.05),('D2',1e-11)])
def test_single_and_identical_populations(model,kinetic):
    a=run(model,kinetic=kinetic,weights=(1,0),radii=(100e-6,100e-6))
    b=run(model,kinetic=kinetic,weights=(.2,.8),radii=(100e-6,100e-6))
    np.testing.assert_allclose(a['ey_pct'],b['ey_pct'],atol=1e-5)
    if model=='S2':
        np.testing.assert_allclose(a['ey_pct'],run('S0',kinetic=kinetic)['ey_pct'],atol=1e-8)


def test_radial_diffusion_against_analytic_perfect_sink():
    errors=[]
    t=np.array([.01,.03,.1,.3])
    n=np.arange(1,500)
    exact=6/np.pi**2*np.sum(np.exp(-np.pi**2*t[:,None]*n*n)/(n*n),axis=1)
    for nr in (24,48,96):
        w,_,_=radial_geometry(nr)
        def rhs(t,s):
            ds,_=particle_derivative(s.reshape(1,1,nr),np.ones((1,1)),np.ones(1),
                                     np.zeros(1),1,1,'D2')
            return ds.ravel()
        r=solve_ivp(rhs,(0,t[-1]),w,t_eval=t,method='BDF',rtol=1e-9,atol=1e-12)
        errors.append(float(np.max(abs(r.y.sum(axis=0)-exact))))
    assert errors[2]<errors[1]<errors[0]
    assert errors[-1]<.0003


def test_support_determinism_and_conversion():
    for target in ([-1],[3],[np.nan]):
        with pytest.raises(ValueError): interpolate_supported([0,2],[0,1],target)
    np.testing.assert_array_equal(run()['ey_pct'],run()['ey_pct'])
    w,r=populations(dict(theta_f=.2,theta_c=.8,**{'2R_f_um':30,'2R_c_um':360}))
    np.testing.assert_allclose(r,[15e-6,180e-6],rtol=1e-15)
    assert w.sum()==1


def test_fold_projection_and_source_gate():
    rows=[dict(row_id=f'{p}{q}',condition_id=f'{p}{q}',powder=p,flow_m3_s=q,
               mass_kg=.02,ey_pct=123,strength_pct=567) for p in 'EMF' for q in (2,3,4)]
    for axis in ('flow','powder'):
        folds=list(grouped_folds(rows,axis))
        assert len(folds)==3
        for _,train,held in folds:
            assert len(train)==6 and len(held)==3
            assert all('ey_pct' not in r and 'strength_pct' not in r for r in held)
            assert {r['condition_id'] for r in train}.isdisjoint(r['condition_id'] for r in held)
    with pytest.raises(ValueError,match='withheld'):
        fit_predict(rows,rows,'S0',{},0)
    contract=json.loads((ROOT/'docs/analysis/sci_md_mo_transfer_001/contract.json').read_text())
    with pytest.raises(RuntimeError,match='BLOCKED_SOURCE_CONTRACT'):
        require_authority(contract,{},'unused')
    with pytest.raises(RuntimeError,match='BLOCKED_SOURCE_CONTRACT'):
        fit_predict(rows,[],'S0',contract,0)


def test_decision_arithmetic_and_once_only_score(tmp_path):
    a={str(i):.4 for i in range(9)}
    b={str(i):.9 for i in range(9)}
    assert axis_decision(a,b,.1,.1,[True]*3,[True]*3)['verdict']=='MATERIAL_TRANSFER_GAIN'
    assert axis_decision(a,b,.1,.1,[False]*3,[True]*3)['verdict']=='CALIBRATION_INADEQUATE'
    assert not adequate({'a':.95},.1)
    assert simpler_comparator({'S0':1,'S2':.85},.1)=='S0'
    a['0']=1.6
    assert axis_decision(a,b,.1,.1,[True]*3,[True]*3)['verdict']=='NO_EARNED_MATERIAL_GAIN'
    with pytest.raises(ValueError): axis_decision({},b,.1,.1,[True]*3,[True]*3)
    p=tmp_path/'predictions.json'; marker=tmp_path/'score.json'
    h=freeze_predictions(p,{'row_ids':['synthetic-row'],'predictions':[.4]})
    score_once(p,h,marker,[dict(row_id='synthetic-row',condition_id='synthetic',ey_pct=.5)],[.4])
    with pytest.raises(FileExistsError): score_once(p,h,marker,[dict(row_id='synthetic-row',condition_id='synthetic',ey_pct=.5)],[.4])

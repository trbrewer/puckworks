"""Verification of pressure exposure, exact embedding and frozen contracts."""
import json

import numpy as np
import pytest
from scipy.special import expi
from scipy.stats import qmc

from puckworks.analysis import joint_clock_001 as J
from puckworks.analysis import joint_mass_fade_001 as M
from puckworks.analysis import joint_pressure_fade_001 as F
from puckworks.analysis import joint_pressure_fade_001_run as R


def source(pressure=9.):
    return dict(predict_times_s=np.array([0.,100.]),
                predict_pressure_bar=np.array([pressure,pressure]),predict_horizon_s=100.)


def test_adapter_fixed_mc_tau_last():
    p=np.array([.8,24.,2.,3.6,.0002,13.173])
    np.testing.assert_allclose(F.physical(F.coordinates(p)),p,rtol=1e-14,atol=0)
    assert F.coordinates(p)[4]==.0002 and F.coordinates(p)[5]==13.173/100
    pred=F.prepare(source(),p,29.,dt=.1,cells=16)
    assert pred.mc==29. and pred.gamma_p==.0002 and pred.gamma==0. and pred.tb==13.173
    for bad in (-.001,.006,np.nan):
        with pytest.raises(ValueError):
            F.prepare(source(),[*p[:4],bad,p[-1]],29.)
    with pytest.raises(ValueError):
        J.Prepared([0.,100.],[9.,9.],[*p[:4],29.],'W1',[0.],gamma=.001,gamma_p=.0001)


@pytest.mark.parametrize('tau',[0.,13.173,100.])
def test_zero_nests_inherited_both_paths(tau):
    s=source();s['predict_times_s']=np.array([0.,10.,60.,100.])
    s['predict_pressure_bar']=np.array([-1.,5.,13.,8.])
    p=[.8,24.,2.,3.6,0.,tau]
    a=F.prepare(s,p,29.,dt=.1,cells=16)
    b=M.prepare(s,p,29.,dt=.1,cells=16)
    np.testing.assert_allclose(a.mass,b.mass,rtol=1e-12,atol=0)
    np.testing.assert_allclose(a.flow,b.flow,rtol=1e-12,atol=0)
    full=a.chemistry(100.);old=b.chemistry(100.)
    for k,v in full.items():
        np.testing.assert_allclose(v,old[k],rtol=1e-12,atol=0)


@pytest.mark.parametrize('gamma_p',[.0001,.001,.005])
@pytest.mark.parametrize('tau',[0.,13.173])
def test_constant_pressure_exposure_and_independent_mass_integral(gamma_p,tau):
    p=[.8,24.,2.,3.6,gamma_p,tau]
    a=F.prepare(source(),p,29.,dt=.01,cells=16);full=a.chemistry(100.)
    expected=9.*np.maximum(a.time-tau,0.)
    np.testing.assert_allclose(a.exposure,expected,rtol=1e-12,atol=0)
    np.testing.assert_allclose(full['pressure_exposure_bar_s'],expected,rtol=1e-12,atol=0)
    np.testing.assert_allclose(a.mass,full['liquid_g'],rtol=1e-12,atol=0)
    np.testing.assert_allclose(a.flow,full['bed_flow_g_s'],rtol=1e-12,atol=0)
    # Separable ODE: integral_0^M exp(exp(-m/Mc)) dm = C*(1-exp(-k*t))/k.
    left=-a.mc*(expi(np.exp(-a.mass/a.mc))-expi(1.))
    right=a.cap[0]*(-np.expm1(-gamma_p*expected))/(gamma_p*9.)
    np.testing.assert_allclose(left,right,rtol=1e-7,atol=2e-8)
    use=a.time>tau
    exact=a.cap*np.exp(-np.exp(-a.mass/a.mc))*np.exp(-gamma_p*expected)
    np.testing.assert_allclose(a.flow[use],exact[use],rtol=1e-12,atol=0)
    zero=F.prepare(source(),[*p[:4],0.,tau],29.,dt=.01,cells=16).chemistry(100.)
    assert full['liquid_g'][-1]<zero['liquid_g'][-1]
    assert full['solute_g'][-1]!=zero['solute_g'][-1]
    assert full['max_balance_error_g']<1e-9


def test_variable_pressure_clipping_breakthrough_and_quadrature():
    s=source();s['predict_times_s']=np.array([0.,20.,40.,100.])
    s['predict_pressure_bar']=np.array([-3.,2.,13.,4.])
    p=[.8,24.,2.,3.6,.002,13.173]
    a=F.prepare(s,p,29.,dt=.1,cells=16);full=a.chemistry(100.)
    expected=np.r_[0.,np.cumsum(np.diff(a.time)*.5*(a.pressure[:-1]+a.pressure[1:])*(a.front[:-1]>=1))]
    np.testing.assert_array_equal(a.exposure,expected)
    np.testing.assert_array_equal(full['pressure_exposure_bar_s'],expected)
    assert np.all(a.exposure[a.time<=a.tb]==0.)
    np.testing.assert_allclose(a.mass,full['liquid_g'],rtol=1e-12,atol=0)
    np.testing.assert_allclose(a.flow,full['bed_flow_g_s'],rtol=1e-12,atol=0)
    # Explicit independent step at a varying-pressure interior point.
    j=np.searchsorted(a.time,55.);dt=a.time[j]-a.time[j-1]
    r=np.exp(-np.exp(-a.mass[j-1]/29.))*np.exp(-p[4]*expected[j-1])
    mid=a.mass[j-1]+.25*dt*(a.cap[j-1]+a.cap[j])*r
    add=.5*dt*(a.cap[j-1]+a.cap[j])*np.exp(-np.exp(-mid/29.))*np.exp(-p[4]*(expected[j-1]+expected[j])/2)
    assert a.mass[j]==pytest.approx(a.mass[j-1]+add,rel=1e-14)


@pytest.mark.parametrize('pressure,gamma_p,tau',[(13.,.005,0.),(9.,.003,13.173),(1.,.005,90.),(1.,.005,0.)])
def test_exact_prefix_declines_and_nondetections(pressure,gamma_p,tau):
    p=[.8,24.,2.,3.6,gamma_p,tau];times=np.linspace(.013,99.913,1001)
    fast=F.prepare(source(pressure),p,29.,dt=.1,cells=16)
    slow=F.prepare(source(pressure),p,29.,dt=.1,cells=16)
    a=fast.observer(times);b=slow.observer(times,accelerate=False)
    for k in ('detected','onset_s','censor_bound_s','last_timestamp_s','samples'):
        assert a[k]==b[k]
    full=slow.chemistry(100.);literal=J.W.observe(full,times)
    for k in ('detected','onset_s','censor_bound_s'):
        assert a[k]==literal[k]
    if pressure>=9:
        assert slow.flow[-1]<slow.flow[len(slow.flow)//2]
    if tau==90:
        assert not a['detected']


def test_frozen_bank_common_coordinates_and_exact_embedding():
    rows=R.table(R.OUT/'START_BANK.csv');old=R.table(R.MR.OUT/'START_BANK.csv')
    fits=R.table(R.MR.OUT/'FITS.csv')
    assert len(rows)==228
    products=qmc.LatinHypercube(1,seed=20261107).random(15)[:,0]*.6
    for fold in sorted({r['fold'] for r in rows}):
        own=[r for r in rows if r['fold']==fold]
        assert len(own)==19
        control=next(r for r in fits if r['fold']==fold and r['arm']=='refreshed_A_J1')
        common=[float(control[k]) for k in ('a','Pstar','n','Pd','tau0')]
        for r in own:
            p=json.loads(r['parameters'])
            np.testing.assert_array_equal(F.physical(F.coordinates(p)),p)
            assert float(r['Mc_g'])==float(control['Mc_g'])
        for r,product in zip(own[:4],(0.,.05,.15,.30)):
            p=json.loads(r['parameters'])
            assert p[:4]+p[5:]==common and p[4]==product/1300
        for r,product in zip(own[4:],products):
            p=json.loads(r['parameters'])
            original=next(o for o in old if o['fold']==fold and o['arm']=='refreshed_A_J1' and o['origin']==r['origin'])
            q=json.loads(original['parameters'])
            assert p[:4]+p[5:]==q[:4]+q[5:] and p[4]==product/1300


def test_source_contract_hashes():
    for item in R.read(R.MR.OUT/'IMPORTED_SOURCES.json'):
        R.T.checked_hash(R.ROOT/item['path'],item['sha256'])
    # The inherited observation test verifies the bank from its actual arrays.
    from tests.test_joint_mass_fade_001 import test_frozen_trajectory_code_and_shared_resample_identity
    test_frozen_trajectory_code_and_shared_resample_identity()


def test_primary_contrast_uses_pressure_fade_inside_shared_draws():
    from puckworks.analysis import joint_pressure_fade_001_report as P
    points=np.array([1.,2.,9.,4.])
    draws=np.array([[1.,2.,3.],[2.,4.,6.],[90.,80.,70.],[5.,7.,8.]])
    value=P.difference_fields('contrast',points,draws)
    expected=R.O.uncertainty('contrast',2.,np.array([3.,3.,2.]))
    assert value==expected
    row=P.comparison(3.,np.array([2.,3.,4.]),points,draws)
    assert row['pressure_fade_minus_refreshed']==2.
    assert row['pressure_fade_minus_refreshed_absolute_error']==0.


def test_mass_and_pressure_parameter_labels_stay_separate():
    from puckworks.analysis import joint_pressure_fade_001_report as P
    p=[.8,24.,2.,3.6,.0002,13.]
    mass=P.parameter_fields('A_J1_F',p,29.)
    pressure=P.parameter_fields('A_J1_PF',p,29.)
    assert mass['gamma']==.0002 and mass['gamma_P']==0.
    assert pressure['gamma']==0. and pressure['gamma_P']==.0002
    assert pressure['gamma_P_1300']==.26 and mass['gamma_Mc']==.0002*29.


def test_slice_grid_is_fixed_and_peak_convention_is_inherited():
    from puckworks.analysis import joint_pressure_fade_001_evaluate as E
    from puckworks.analysis import joint_mass_fade_001_evaluate as ME
    assert E.SLICE_GRID==(0.,.0125,.025,.05,.075,.1,.15,.2,.3,.45,.6)
    for flow in ([1.,2.,3.],[3.,2.,1.],[1.,3.,1.],[1.,1.,1.]):
        assert E.peak([0.,1.,2.],flow)==ME.peak([0.,1.,2.],flow)

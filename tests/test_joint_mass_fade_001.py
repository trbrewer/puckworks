"""Focused verification for the bounded mass-fade campaign."""
import hashlib
import json
import subprocess

import numpy as np
import pytest

from puckworks.analysis import joint_clock_001 as J
from puckworks.analysis import joint_mass_fade_001 as F
from puckworks.analysis import joint_mass_fade_001_run as R
from puckworks.analysis import turnover_time_replay_001 as T
from puckworks.analysis import wasz_turnover_time_001 as O


def source(p=9.):
    return dict(predict_times_s=np.array([0.,100.]),predict_pressure_bar=np.array([p,p]),predict_horizon_s=100.)


def test_adapter_mc_gamma_tau_last():
    p=np.array([.8,24.,2.,3.6,.007,13.])
    np.testing.assert_allclose(F.physical(F.coordinates(p)),p,rtol=1e-14,atol=0)
    assert F.coordinates(p)[4]==.007 and F.coordinates(p)[5]==.13
    a=F.prepare(source(),p,29.)
    assert a.mc==29 and a.gamma==.007 and a.tb==13
    b=J.Prepared([0.,100.],[9.,9.],[*p[:4],29.],"W1",[13.],gamma=.007)
    np.testing.assert_array_equal(a.mass,b.mass)
    with pytest.raises(ValueError):
        F.coordinates(p[:5])


@pytest.mark.parametrize('gamma',[.003,.02,.05])
@pytest.mark.parametrize('tau',[0.,13.173])
def test_two_paths_match_and_chemistry_responds(gamma,tau):
    p=[.8,24.,2.,3.6,gamma,tau]
    a=F.prepare(source(),p,29.)
    full=a.chemistry(100.)
    np.testing.assert_allclose(a.mass,full['liquid_g'],rtol=1e-12,atol=0)
    np.testing.assert_allclose(a.flow,full['bed_flow_g_s'],rtol=1e-12,atol=0)
    zero=F.prepare(source(),[*p[:4],0.,tau],29.).chemistry(100.)
    assert full['liquid_g'][-1]<zero['liquid_g'][-1]
    assert full['solute_g'][-1]!=zero['solute_g'][-1]
    assert full['max_balance_error_g']<1e-9


@pytest.mark.parametrize('p,gamma,tau',[(9.,.03,13.),(9.,.1,0.),(1.,.2,90.),(1.,.2,0.)])
def test_positive_prefix_full_decline_nondetection(p,gamma,tau):
    pars=[.8,24.,2.,3.6,gamma,tau]
    times=np.linspace(.013,99.913,1001)
    fast=F.prepare(source(p),pars,29.)
    slow=F.prepare(source(p),pars,29.)
    x=fast.observer(times); y=slow.observer(times,accelerate=False)
    for k in ('onset_s','detected','censor_bound_s','last_timestamp_s','samples'):
        assert x[k]==y[k]
    z=J.W.observe(slow.chemistry(100.),times)
    assert x['detected']==z['detected'] and x['onset_s']==z['onset_s']
    if p==1 and tau==90:
        assert not x['detected']


@pytest.mark.parametrize('product',[0.,.13,1.,1.3])
def test_analytic_constant_pressure_regimes(product):
    mc=29.;g=product/mc
    t=np.linspace(0.,300.,60001);cap=np.full(len(t),3.);front=np.ones(len(t))
    mass,flow=J.liquid_only(t,cap,front,mc,g)
    exact=cap*np.exp(-np.exp(-mass/mc))*np.exp(-g*mass)
    np.testing.assert_allclose(flow,exact,rtol=1e-12,atol=0)
    reg=F.regime(g,mc)
    if product==0:
        assert np.all(np.diff(flow)>=0) and reg['Mstar_g'] is None
    elif product<1:
        peak=np.argmax(flow)
        assert 0<peak<len(flow)-1
        assert abs(mass[peak]-reg['Mstar_g'])<.02
        assert np.all(np.diff(flow[:peak+1])>=0) and np.all(np.diff(flow[peak:])<=0)
    else:
        assert np.argmax(flow)==0 and np.all(np.diff(flow)<=0)
        assert reg['regime']=='declines_from_breakthrough'


def test_zero_nesting_original_equations():
    # Independent literal original update, including event insertion.
    a=F.prepare(source(),[.8,24.,2.,3.6,0.,13.173],29.)
    mass=np.zeros(len(a.time));flow=np.zeros(len(a.time))
    import math
    for j in range(1,len(mass)):
        mass[j]=mass[j-1]
        if a.front[j-1]>=1:
            dt=a.time[j]-a.time[j-1]
            r=math.exp(-math.exp(-mass[j-1]/a.mc))
            mid=mass[j-1]+.25*dt*(a.cap[j-1]+a.cap[j])*r
            mass[j]+=.5*dt*(a.cap[j-1]+a.cap[j])*math.exp(-math.exp(-mid/a.mc))
            flow[j]=a.cap[j]*math.exp(-math.exp(-mass[j]/a.mc))
    np.testing.assert_allclose(a.mass,mass,rtol=1e-12,atol=0)
    np.testing.assert_allclose(a.flow,flow,rtol=1e-12,atol=0)
    b=J.prepare(source(),[.8,24.,2.,3.6,13.173],'J1',29.)[0]
    for k,v in a.chemistry(100.).items():
        if isinstance(v,np.ndarray):
            np.testing.assert_allclose(v,b.chemistry(100.)[k],rtol=1e-12,atol=0)


def test_start_bank_fold_matching():
    rows=R.table(R.OUT/'START_BANK.csv')
    refs=R.read(R.OUT/'SOURCE_FITS.json')
    assert len(rows)==456 and len(refs)==12
    for ref in refs:
        fold=ref['fold'];mc=ref['Mc_g']
        control=[r for r in rows if r['fold']==fold and r['arm']=='refreshed_A_J1']
        fade=[r for r in rows if r['fold']==fold and r['arm']=='A_J1_F']
        assert len(control)==len(fade)==19
        assert all(float(r['Mc_g'])==mc for r in control+fade)
        lhs={r['origin']:json.loads(r['parameters']) for r in control if r['origin'].startswith('LHS')}
        for r in fade[4:]:
            p=json.loads(r['parameters']); base=lhs[r['origin']]
            assert p[:4]+p[5:]==base[:4]+base[5:]
            assert 0<=p[4]*mc<=.4
        assert [float(r['gamma_Mc']) for r in fade[:4]]==[0.,.03,.13,.25]
        assert ref['zero_seed_included']==(fold in ('HYD-LOCO-9.0','HYD-LOCO-11.0'))


def test_frozen_trajectory_code_and_shared_resample_identity():
    for entry in R.read(R.OUT/'IMPORTED_SOURCES.json'):
        assert hashlib.sha256((R.ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
    # Frozen cohort ordering/counts from #423; no dependency on mounted data.
    condition=np.repeat(J.W.NOMINAL,[5,4,3,10,5,6,4,4,5,4,6])
    assert O.bank_digest(O.draw_bank(condition))=='d599d80c854fd5a3cf9b9ca5d6fe1c617b222125bd1adcb36ad9edecd96801b6'
    assert T.observed_center(12.,'onset',10)==22.
    assert T.observed_center(12.,'stable_pressure',10)==10.


def test_zero_column_against_pinned_original(tmp_path):
    # Read original source only when a Git checkout is present. Historical full
    # arrays are also replayed by the mandatory authenticated reference command.
    if not (R.ROOT/'.git').exists():
        pytest.skip('Git source unavailable in distribution')
    exists=subprocess.run(['git','cat-file','-e',R.BASE],cwd=R.ROOT,capture_output=True)
    if exists.returncode:
        pytest.skip('Pinned original source absent in shallow CI checkout; locally verified')
    code=subprocess.check_output(['git','show',f'{R.BASE}:puckworks/analysis/wetting_screen_001.py'],cwd=R.ROOT).decode()
    start=code.index('def _column(');end=code.index('\n\ndef predict(',start)
    namespace={'np':np,'math':__import__('math')}
    exec(code[start:end],namespace)
    a=F.prepare(source(),[.8,24.,2.,3.6,0.,13.],29.,dt=.2,cells=8)
    r=a.r0
    old=namespace['_column'](a.time,a.cap,a.front,a.mc,8,r.phi,r.rho,r.length,r.area,r.inventory_kg,r.rate,r.capacity,r.diffusivity,r.length/r.native_cells,False)
    new=J.W._column(a.time,a.cap,a.front,a.mc,8,r.phi,r.rho,r.length,r.area,r.inventory_kg,r.rate,r.capacity,r.diffusivity,r.length/r.native_cells,False,0.)
    for x,y in zip(old,new):
        np.testing.assert_allclose(x,y,rtol=1e-12,atol=0)


def test_peak_horizon_boundary_and_decline():
    from puckworks.analysis.joint_mass_fade_001_evaluate import peak
    time=np.arange(5.)
    assert peak(time,[0,2,1,3,4])['peak_status']=='no interior peak within horizon'
    assert peak(time,[4,3,2,1,0])['boundary_left']
    assert peak(time,[0,2,4,2,1])['maximum_times_s']==[2.]
    assert peak(time,[0,0,0,0,0])['peak_status']=='flat; no unique peak'


def test_paired_contrast_is_inside_shared_draws():
    from puckworks.analysis.joint_mass_fade_001_report import comparison
    observed=2.;ob=np.array([1.,2.,3.])
    points=np.array([3.,3.,2.5]);draws=np.array([[2.,3.,4.],[2.,3.,4.],[1.5,2.5,3.5]])
    row=comparison(observed,ob,points,draws)
    assert row['fade_minus_refreshed']==-.5
    assert row['fade_minus_refreshed_lo']==row['fade_minus_refreshed_hi']==-.5
    assert row['fade_minus_refreshed_absolute_error']==-.5

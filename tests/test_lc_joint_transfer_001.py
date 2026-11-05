"""Focused checks for the declared capacity-only substitution; no fitted campaign."""
import numpy as np
import pytest

from puckworks.analysis import joint_clock_001 as J
from puckworks.analysis import lc_joint_transfer_001 as L
from puckworks.analysis import lc_joint_transfer_001_run as R


def source(pressure=2.):
    return dict(predict_times_s=[0., 50., 100.],
                predict_pressure_bar=[pressure, pressure+.2, pressure], predict_horizon_s=100.)


def test_coordinate_order_and_domains():
    p=np.array([1.2,24.,3.7,4.,.37,23.])
    z=L.coordinates(p)
    np.testing.assert_array_equal(z[[2,4,5]],[3.7,.37,.23])
    np.testing.assert_array_equal(z[[0,1,3]],np.log(p[[0,1,3]]))
    np.testing.assert_allclose(L.physical(z),p,rtol=1e-12,atol=0)
    lo,hi=L.bounds()
    assert hi[2]==np.inf
    np.testing.assert_array_equal(lo[[2,4,5]],[1.,0.,0.])
    np.testing.assert_array_equal(hi[[4,5]],[1.,1.])
    for function in (L.coordinates,L.physical):
        with pytest.raises(ValueError):
            function([1.]*5)


@pytest.mark.parametrize("n,f",[(1.,0.),(1.,.4),(1.,1.),(3.,1.),(1e8,1.)])
def test_exact_linear_capacity_limits(n,f):
    p=np.array([1.2,24.,n,4.,f,13.])
    pressures=np.array([-1.,0.,.01,1.,2.,3.5,9.,13.,100.])
    expected=L.capacity([1.2,24.,1.,4.,0.,13.],pressures)
    np.testing.assert_allclose(L.capacity(p,pressures),expected,rtol=1e-12,atol=0)


@pytest.mark.parametrize("tau",[0.,13.137])
def test_exact_f0_predictor_nesting_and_zero_front(tau):
    p=[1.2,24.,2.3,4.,0.,tau]
    lc=L.prepare(source(),p,28.7,dt=.2,cells=8)
    a,_=J.prepare(source(),p[:4]+[tau],"J1",28.7,dt=.2,cells=8)
    np.testing.assert_allclose(lc.cap,a.cap,rtol=1e-12,atol=0)
    for name in ("time","front","mass","flow"):
        np.testing.assert_allclose(getattr(lc,name),getattr(a,name),rtol=1e-12,atol=0)
    x,y=lc.chemistry(100.),a.chemistry(100.)
    for k in x:
        np.testing.assert_allclose(x[k],y[k],rtol=1e-12,atol=0)
    if tau==0.:
        fully_wet,_=J.prepare(source(),p[:4],"J0",28.7,dt=.2,cells=8)
        np.testing.assert_allclose(x["beverage_g"],fully_wet.chemistry(100.)["beverage_g"],rtol=1e-12,atol=0)
    else:
        assert np.all(lc.mass[lc.time<=tau]==0.)
        assert np.all(lc.flow[lc.time<=tau]==0.)
        np.testing.assert_array_equal(np.exp(-np.exp(-lc.mass[lc.time<=tau]/28.7)),
                                      np.full(np.sum(lc.time<=tau),np.exp(-1.)))


@pytest.mark.parametrize("pressure,tau",[(1.,13.),(6.,13.),(0.,0.),(1.,100.)])
def test_inherited_observer_prefix_and_censor_contract(pressure,tau):
    p=[.8,24.,3.,4.,.3,tau]
    lc=L.prepare(source(pressure),p,28.7,dt=.2,cells=8)
    times=np.linspace(0.,99.93,1000)
    prefix=lc.observer(times)
    full=lc.observer(times,accelerate=False)
    for k in ("onset_s","detected","censor_bound_s","last_timestamp_s","samples"):
        assert prefix[k]==full[k]
    assert full["censor_bound_s"]==times[times[-1]-times>=2.][-1]
    if tau==100.:
        assert not full["detected"]
    assert L.Prepared.observer is J.Prepared.observer
    assert L.Prepared.chemistry is J.Prepared.chemistry


def test_fold_matching_starts_and_f_last_time_last():
    data=dict(reference={},lc_seeds={})
    for h in (None,1.,3.5):
        fold=R.R.label(h)
        data["lc_seeds"][fold]=dict(a_g_s_bar=1.,Pstar_bar=20.,n=3.,Pd_bar=4.,f=.4)
        for w in J.WEIGHTS:
            data["reference"][(w,fold)]=dict(parameters=[1.,20.,2.,4.,10.+w])
    for h in (None,1.,3.5):
        for w in J.WEIGHTS:
            schedule=R.starts(data,w,h)
            assert len(schedule)==19
            first=L.physical(schedule[0][1])
            assert first[4]==0. and first[5]==10.+w
            second=L.physical(schedule[1][1])
            assert second[4]==.4 and second[5]==10.+w
            third=L.physical(schedule[2][1])
            assert third[4]==.4 and third[5]==0.
            assert schedule[3:]==R.starts(data,.05,None)[3:]


def test_reference_and_seed_filters_have_exact_scope():
    # Repository tables are compact inputs, not a campaign replay.
    joint=R.table(R.ROOT/"docs/research/JOINT_CLOCK_001/FITS.csv")
    a=[r for r in joint if r["model"]=="J1"]
    assert len(a)==48
    folds={r["fold"] for r in a}
    c3=R.table(R.ROOT/"docs/research/PRESSURE_PEAK_STAGE_C3E/RESULT_TABLE.csv")
    lc=[r for r in c3 if r["record_type"]=="fit" and r["candidate"]=="LC" and r["fold"] in folds]
    assert len(lc)==12 and not any("OMIT" in r["fold"] for r in lc)


def test_lc_global_capacity_checks_multiple_stationary_candidates():
    p=np.array([1.,1.,8.,6.,.1,13.])
    peak=L.C.global_peak(p[:5],"LC")
    assert len(peak["stationary_pressures_bar"])>=3
    assert peak["infinite_pressure_capacity_g_s"]==0.
    assert peak["candidate_pressures_bar"][0]==0.
    assert peak["capacity_g_s"]>=L.capacity(p,np.linspace(0.,30.,30001)).max()


def test_external_units_amplitude_and_matched_contrast():
    # Synthetic only: no Corrochano evaluation before the shape freeze.
    from puckworks.analysis import lc_joint_transfer_001_cor15 as X
    p=np.array([25000.,50000.,125000.,250000.,450000.])
    frozen=dict(n=2.7,Pd_bar=3.8,Pstar_bar=24.,f=.3)
    h=X.shape(p,frozen)
    direct=3.8*((1-.3)*(-np.expm1(-(p/1e5/3.8)**2.7))+.3*(-np.expm1(-p/1e5/3.8)))*np.exp(-p/1e5/24.)
    np.testing.assert_allclose(h,direct,rtol=1e-12,atol=0)
    q=2e-6*h+np.array([1,-1,1,-1,1])*1e-8
    a=X.fit(p,q,frozen); b=X.fit(p,q)
    independent=np.linalg.lstsq(h[:,None],q,rcond=None)[0][0]
    np.testing.assert_allclose(a["amplitude"],independent,rtol=1e-12,atol=0)
    fixed_s2=float(np.mean(q**2))
    for factor in (1.,.9,1.1):
        y=q*factor
        aa=X.fit(p,y,frozen); bb=X.fit(p,y)
        expected=(aa["mse"]-bb["mse"])/fixed_s2
        np.testing.assert_allclose(X.C.matched_contrast(y,aa["pred"],bb["pred"],fixed_s2),expected,rtol=1e-12,atol=0)
    assert b["amplitude"]>0 and a["amplitude"]>0


def test_unavailable_pressure_support_is_not_censoring():
    s=source(); s["predict_times_s"]=[1.,50.,99.]
    with pytest.raises(ValueError,match="support"):
        L.prepare(s,[1.,20.,3.,4.,.4,13.],28.7)

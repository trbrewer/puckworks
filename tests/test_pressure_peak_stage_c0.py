"""C0 equation recovery, independent Jacobians, bands and saved reference identity."""
from types import SimpleNamespace
import time

import numpy as np
import pytest

from puckworks.analysis import pressure_peak_stage_c0 as C


def test_threshold_flow_recovers_a_pstar_p0_without_observed_onset():
    t = np.linspace(0., 100., 41)
    pressure = np.repeat(np.array([1., 2., 3.5, 5., 7., 9., 13.])[:, None], len(t), axis=1)
    expected = np.array([1.7, 6.4, .55])
    target = C.flow_curve(expected, pressure, t, 29.)[0]
    mask = np.broadcast_to(t >= 20., target.shape)
    result = C.fit("flow", pressure, t, target, mask, pressure[:, 0],
                   np.full(len(pressure), np.nan), np.full(len(pressure), 1/len(pressure)),
                   29., C.Deadline(time.monotonic()+60))
    np.testing.assert_allclose(C.physical_flow(result), expected, rtol=1e-6, atol=1e-8)


def test_threshold_zero_reduces_to_c4_and_flow_jacobian():
    t = np.linspace(0., 100., 101)
    pressure = np.array([3.+.1*np.sin(t/10), 11.+.2*np.cos(t/20)])
    q = C.flow_curve(np.array([1.3, 7., 0.]), pressure, t, 30.)[0]
    expected = C.B.air_endpoint(np.array([1.3, 7., 30., 0.]), pressure, t)[0]
    np.testing.assert_allclose(q[:, -1], expected, rtol=1e-12, atol=0)
    x = np.array([np.log(1.3), np.log(7.), .6])
    physical = lambda v: np.array([np.exp(v[0]), np.exp(v[1]), v[2]])
    _, jac = C.flow_curve(physical(x), pressure, t, 30.)
    for k in range(3):
        d = np.zeros(3); d[k] = 1e-5
        numeric = (C.flow_curve(physical(x+d), pressure, t, 30.)[0]
                   -C.flow_curve(physical(x-d), pressure, t, 30.)[0])/2e-5
        np.testing.assert_allclose(jac[:, :, k], numeric, rtol=1e-5, atol=1e-8)


def test_onset_epsilon_and_jacobian():
    pressure = np.array([.5, 1., 4., 9., 13.])
    x = np.array([np.log(6.), .6, np.log(3.), 8.])
    physical = lambda v: [np.exp(v[0]), v[1], np.exp(v[2]), v[3]]
    q, jac = C.onset_curve(physical(x), pressure)
    assert q[0] == pytest.approx(8.+3*np.exp(.5/6)/.01)
    for k in range(4):
        d = np.zeros(4); d[k] = 1e-5
        numeric = (C.onset_curve(physical(x+d), pressure)[0]
                   -C.onset_curve(physical(x-d), pressure)[0])/2e-5
        np.testing.assert_allclose(jac[:, k], numeric, rtol=1e-5, atol=1e-8)


@pytest.mark.parametrize("value,grade", [(3.51,"MEETS"),(3.51001,"NEAR"),(4.53,"NEAR"),(4.53001,"MISSES")])
def test_onset_band_edges(value, grade):
    assert C.onset_grade(value) == grade


@pytest.mark.parametrize("value,grade", [(.1,"MEETS"),(-.1,"MEETS"),(.10001,"NEAR"),(-.2,"NEAR"),(.20001,"MISSES")])
def test_bias_band_edges(value, grade):
    assert C.bias_grade(value) == grade


@pytest.mark.parametrize("left,right,grade", [([1,2],[2,3],"MEETS"),([-1,1],[0,2],"MEETS"),
                                            ([1,2],[3,4],"NEAR"),([1,2],[3.001,4],"MISSES")])
def test_consistency_band_edges(left, right, grade):
    assert C.consistency_grade(left, right)[0] == grade


def test_inherited_flow_grade_bands():
    assert C.S.accuracy_grade(.2,.3,"TIE") == "MEETS"
    assert C.S.accuracy_grade(.2,.3,"UNRESOLVED") == "NEAR"
    assert C.S.accuracy_grade(.4,.3,"UNRESOLVED") == "MISSES"
    assert [C.S.peak_grade(x) for x in ([5,7],[8,8],[9,9])] == ["MEETS","NEAR","MISSES"]
    assert [C.S.slope_grade(x) for x in ([-.09,-.06],[-.03,-.02],[-.07,0])] == ["MEETS","NEAR","MISSES"]
    assert [C.S.trend_grade(x) for x in (4,3,2)] == ["MEETS","NEAR","MISSES"]


def test_saved_b1_all_eleven_folds_reproduce_source_score():
    pressure, condition, target, _ = C.S.endpoint_inputs()
    groups = [np.flatnonzero(condition == p) for p in C.S.NOMINAL]
    brews = SimpleNamespace(ids=list(range(len(target))), pressure=pressure, condition=condition,
                            target=target, t=np.linspace(0.,100.,1000), groups=groups,
                            fold=[next(k for k in C.S.fold_bank("B0c", C.S.select_stage("B0c")["B1"][0])
                                       if float(k.removeprefix("HYD-LOCO-")) == p) for p in condition])
    prediction, bank = C.saved_b1(brews)
    assert len(bank) == 11
    for fold, record in bank.items():
        use = condition == float(fold.removeprefix("HYD-LOCO-"))
        expected = np.maximum(np.polynomial.polynomial.polyval(pressure[use,-1], record["free"]), 0.)
        np.testing.assert_allclose(prediction[use], expected, rtol=1e-12, atol=0)


def test_constant_flow_peak_and_onset_minimum_share_pstar_plus_p0():
    grid = np.arange(1.,13.0001,.05)
    pstar,p0 = 5.5,.5
    t = np.array([0.,100.]);pressure=np.repeat(grid[:,None],2,axis=1)
    flow = C.flow_curve(np.array([1.5,pstar,p0]),pressure,t,30.)[0][:,-1]
    onset = C.onset_curve([pstar,p0,3.,8.],grid)[0]
    assert grid[np.argmax(flow)] == pytest.approx(6.)
    assert grid[np.argmin(onset)] == pytest.approx(6.)


def test_saved_fold_extrema_exclude_full_cohort_fit_and_report_range():
    bank = {name: dict(a_g_s_bar=1.5, Pstar_bar=ps, P0_bar=.5, Mc_fixed_g=30., b_s_bar=3., t0_s=8.)
            for name, ps in (("first", 5.5), ("second", 6.5), ("third", 7.5), ("DESCRIPTIVE_ALL", 11.5))}
    result = C.fold_extrema(bank)
    for key in ("flow_peak", "onset_minimum"):
        assert result["continuous_"+key+"_fold_median_bar"] == pytest.approx(7.)
        np.testing.assert_allclose(result["continuous_"+key+"_fold_range_bar"], [6., 8.], rtol=1e-12, atol=0)
        assert set(result["continuous_"+key+"_by_fold_bar"]) == {"first", "second", "third"}


def test_compute_deadline_is_not_silently_extended():
    with pytest.raises(TimeoutError, match="two-hour"):
        C.Deadline(time.monotonic()-1).check()


def test_accuracy_keeps_b0c_between_condition_uncertainty():
    brews=SimpleNamespace(ids=list(range(4)),target=np.zeros(4),
                         groups=[np.array([0,1]),np.array([2,3])],fold=["low","low","high","high"])
    reference=np.full(4,1.)
    candidate=np.array([.5,.5,1.5,1.5])
    # Fixed-condition brew-only resampling would spuriously give [0,0].
    bounds=C.paired_accuracy(brews,candidate,reference)
    np.testing.assert_allclose(bounds,[-.5,.5],rtol=1e-12,atol=0)
    assert C.A.comparison(bounds)=="UNRESOLVED"

"""T2 limits, independent derivatives, recovery and fold-local nuisance inputs."""
from types import SimpleNamespace
import time

import numpy as np
import pytest

from puckworks.analysis import pressure_peak_stage_c1 as C


def test_infinite_pd_recovers_c0_t1_flow():
    t = np.linspace(0., 100., 101)
    pressure = np.array([.4+.1*np.sin(t/10), 3.+.4*np.sin(t/15), 11.+.2*np.cos(t/20)])
    expected = C.C0.flow_curve([1.3, 7., .6], pressure, t, 30.)[0]
    actual = C.flow_curve([1.3, 7., .6, 1e12], pressure, t, 30.)[0]
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=0)


@pytest.mark.parametrize("locked", [False, True])
def test_flow_jacobian_against_central_differences(locked):
    t = np.linspace(0., 100., 51)
    pressure = np.array([.3+.05*np.sin(t), 3.+.8*np.sin(t/10), 11.+np.cos(t/20)])
    x = C.coordinates([1.6, 16., .55, 3., 3., 8.])
    q, jac = C.flow_curve(C.physical(x)[:4], pressure, t, 29., locked)
    np.testing.assert_allclose(q[0], 0., atol=0)
    for k in range(4):
        d = np.zeros(6); d[k] = 1e-5
        numeric = (C.flow_curve(C.physical(x+d)[:4], pressure, t, 29., locked)[0]
                   -C.flow_curve(C.physical(x-d)[:4], pressure, t, 29., locked)[0])/2e-5
        np.testing.assert_allclose(jac[:, :, k], numeric, rtol=2e-5, atol=1e-9)


def test_onset_jacobian_mapping_and_floor():
    pressure = np.array([.2, 1., 4., 9., 13.])
    x = C.coordinates([1.6, 16., .55, 3., 3., 8.])
    y, jac = C.C0.onset_curve(C.physical(x)[[3, 2, 4, 5]], pressure)
    np.testing.assert_allclose(y[0], 8.+3*np.exp(.2/3)/.01, rtol=1e-12)
    for j, k in enumerate([3, 2, 4, 5]):
        d = np.zeros(6); d[k] = 1e-5
        numeric = (C.C0.onset_curve(C.physical(x+d)[[3, 2, 4, 5]], pressure)[0]
                   -C.C0.onset_curve(C.physical(x-d)[[3, 2, 4, 5]], pressure)[0])/2e-5
        np.testing.assert_allclose(jac[:, j], numeric, rtol=2e-5, atol=1e-8)


@pytest.mark.parametrize("kind", ["fixed", "flow", "joint", "onset"])
def test_synthetic_parameter_recovery(kind):
    t = np.linspace(0., 100., 31)
    nominal = np.array([.8, 1.3, 2., 3.5, 5., 7., 9., 13.])
    pressure = nominal[:, None]*(1+.02*np.sin(t/12))[None, :]
    expected = np.array([1.6, 16., .55, 3.2, 3., 8.])
    target = C.flow_curve(expected[:4], pressure, t, 29.)[0]
    delay = C.C0.onset_curve(expected[[3, 2, 4, 5]], nominal)[0]
    result = C.fit(kind, pressure, t, target, np.broadcast_to(t >= 20., target.shape), nominal,
                   delay, np.full(len(nominal), 1/len(nominal)), 29.,
                   C.C0.Deadline(time.monotonic()+60), pd_fixed=expected[3] if kind == "fixed" else None)
    indices = {"fixed": [0, 1, 2, 3], "flow": [0, 1, 2, 3], "joint": list(range(6)), "onset": [3, 2, 4, 5]}[kind]
    np.testing.assert_allclose([result[C.FIELDS[i]] for i in indices], expected[indices], rtol=2e-5, atol=1e-7)


def test_locked_equals_t2_under_constant_pressure_and_keeps_early_maximum():
    t = np.linspace(0., 100., 51)
    pressure = np.repeat(np.array([.2, 2., 5., 9., 13.])[:, None], len(t), axis=1)
    args = ([1.6, 16., .55, 3.2], pressure, t, 29.)
    for actual, expected in zip(C.flow_curve(*args, locked=True), C.flow_curve(*args)):
        np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=0)
    pressure = np.array([[12., 4., 4.]])
    # At t=0 M=0, and the global term at later times must retain the first 12 bar.
    q = C.flow_curve(args[0], pressure, np.array([0., 1e-10, 2e-10]), 29., True)[0]
    expected = 1.6*3.2*(-np.expm1(-(4.-.55)/3.2))*np.exp(-12/16)/np.e
    np.testing.assert_allclose(q[0, -1], expected, rtol=1e-9, atol=0)


def test_turning_point_formulas_and_distinct_fixed_onset_threshold():
    p0, pd, ps = .55, 3.2, 16.
    peak = p0+pd*np.log1p(ps/pd)
    onset_min = p0+pd
    h = 1e-4
    pressure = np.repeat(np.array([peak-h, peak, peak+h])[:, None], 2, axis=1)
    q = C.flow_curve([1.6, ps, p0, pd], pressure, np.array([0., 100.]), 29.)[0][:, -1]
    np.testing.assert_allclose((q[2]-q[0])/(2*h), 0., atol=1e-8)
    assert q[1] > q[0] and q[1] > q[2]
    y = C.C0.onset_curve([pd, p0, 3., 8.], np.array([onset_min-h, onset_min, onset_min+h]))[0]
    np.testing.assert_allclose((y[2]-y[0])/(2*h), 0., atol=1e-8)
    assert y[1] < y[0] and y[1] < y[2]
    record = dict(a_g_s_bar=1.6, Pstar_bar=ps, P0_bar=p0, Pd_bar=pd, Mc_fixed_g=29.,
                  onset_parameters=dict(Pd_bar=pd, P0_bar=.2, b_s_bar=3., t0_s=8.))
    result = C.continuous(record)
    np.testing.assert_allclose(result["analytic_flow_peak"], peak, rtol=1e-12)
    np.testing.assert_allclose(result["analytic_onset_minimum"], 3.4, rtol=1e-12)
    assert abs(result["flow_peak"]-peak) <= .025
    np.testing.assert_allclose(result["onset_minimum"], 3.4, rtol=1e-12)


def test_same_resample_fold_mc_and_bound_pd_provenance(monkeypatch):
    t = np.array([0., 50., 100.]); condition = np.repeat([2., 5., 9.], 2)
    pressure = np.repeat(condition[:, None], len(t), axis=1)
    groups = [np.flatnonzero(condition == p) for p in [2., 5., 9.]]
    brews = SimpleNamespace(ids=list(range(6)), condition=condition, pressure=pressure, t=t,
                            groups=groups, fold=[f"HYD-LOCO-{p}" for p in condition])
    course = SimpleNamespace(brews=brews, pressure=pressure, t=t, flow=np.ones_like(pressure), mask=np.ones_like(pressure, dtype=bool))
    ctx = SimpleNamespace(coarse=course, fine=course, early=condition, delay=np.full(6, 15.))
    sample = np.array([2., 0., 1., 1., 0., 2.]); calls = []
    def mc_fit(model, course, train, multiplicity, budget):
        np.testing.assert_allclose(multiplicity, sample, rtol=0, atol=0)
        assert all(sample[train] > 0)
        return np.array([1., 7., 29.])
    def fake_fit(kind, pressure, t, target, mask, early, delay, weights, mc, budget, pd_fixed=None):
        calls.append((kind, early.copy(), weights.copy(), mc))
        r = dict(zip(C.FIELDS, [1.6, 16., .55, .1, 3., 8.]))
        r.update(Mc_fixed_g=mc, bound_hits=["Pd_bar"] if kind == "onset" else [])
        if kind == "fixed":
            np.testing.assert_allclose(pd_fixed, .1, rtol=0, atol=0)
        return r
    monkeypatch.setattr(C.B, "fit_course", mc_fit); monkeypatch.setattr(C, "fit", fake_fit)
    result = C.fit_folds(ctx, sample, time.monotonic()+60)
    for i in range(0, len(calls), 4):
        assert [r[0] for r in calls[i:i+4]] == list(C.KINDS)
        for other in calls[i+1:i+4]:
            for j in (1, 2, 3):
                np.testing.assert_allclose(other[j], calls[i][j], rtol=0, atol=0)
    for fold, r in result["fixed"]["bank"].items():
        assert r["onset_Pd_bound_hit"]
        assert r["Pd_source_fit"] == "T2 onset-only:"+fold
        np.testing.assert_allclose(r["Pd_bar"], r["onset_parameters"]["Pd_bar"], rtol=0, atol=0)
    np.testing.assert_allclose(result["fixed"]["onset"], result["onset"]["onset"], rtol=1e-12)


def test_two_hour_deadline_and_missing_restart(tmp_path):
    with pytest.raises(TimeoutError, match="two-hour"):
        C.C0.Deadline(time.monotonic()-1).check()
    assert C.restart_diagnostic(tmp_path, {}) == {"status": "NOT_AVAILABLE"}

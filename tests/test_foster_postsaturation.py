"""Ordinary interface/regression QA, separate from the bounded qualification run."""
from dataclasses import replace
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.models.foster2025 import machine_mode as fm


@pytest.fixture(scope="module")
def result():
    return fm.solve()


def test_three_stages_and_independent_water_fields(result):
    assert result["success"], result["message"]
    p = result["p"]
    assert result["actual_support_s"] == [0, 30]
    ts = result["t_s"]
    assert 0 < result["t_p"] < ts < 30
    assert result["sol"].y.shape[0] == 2
    assert result["post_sol"].y.shape[0] == 1
    before, at, after = [fm.observe(t, result) for t in (ts-1e-7, ts, ts+1e-7)]
    assert before["Q_out_m3_s"] == 0
    assert at["Q_out_m3_s"] == at["Q_bed_in_m3_s"] > 0
    assert at["s_m"] == after["s_m"] == p.L
    for key, scale in [("H_m", p.H0), ("headspace_pressure_absolute_Pa", p.p_m),
                       ("Q_pump_m3_s", p.Q_m), ("Q_bed_in_m3_s", p.Q_m),
                       ("V_pump_m3", p.A*p.H0), ("V_out_m3", p.A*p.H0)]:
        assert abs(before[key]-after[key])/scale < 1e-6
    zero = fm.observe(0, result)
    assert zero["V_pump_m3"] == zero["V_out_m3"] == zero["V_storage_m3"] == 0
    end = fm.observe(30, result)
    assert end["H_m"] > at["H_m"]
    assert end["V_pump_m3"] > end["V_out_m3"] > 0
    assert json.loads(json.dumps(end, allow_nan=False))["PHYSICAL_VALIDATION"] == "NOT_ESTABLISHED"


def test_observer_and_clock_boundaries(result):
    shift = result["p"].t_shift
    for t in [-1e-12, 30+1e-12, np.nan, np.inf]:
        with pytest.raises(fm.UnavailableObservation):
            fm.observe(t, result)
        for observer in [fm.front_headspace_mm, fm.bed_flow_norm]:
            with pytest.raises(fm.UnavailableObservation):
                observer(t + shift, result)
    for t in [0, result["t_p"], result["t_s"], 30]:
        o = fm.observe(t, result)
        assert np.allclose(fm.front_headspace_mm(t+shift, result), [o["s_m"]*1e3, o["H_m"]*1e3])
        assert fm.bed_flow_norm(t+shift, result) == pytest.approx(o["Q_bed_in_m3_s"]/result["p"].Q_m)


@pytest.mark.parametrize("which", ["zero", "before_ponding", "at_ponding", "before_saturation"])
def test_successful_early_horizons(which):
    p = fm.FosterParams()
    tp = fm.ponding(p)[1]
    horizon = {"zero": 0, "before_ponding": tp/2, "at_ponding": tp, "before_saturation": 1.0}[which]
    r = fm.solve(horizon_s=horizon)
    assert r["success"] and r["t_s"] is None
    assert r["actual_support_s"] == [0, horizon]
    assert fm.observe(horizon, r)["Q_out_m3_s"] == 0
    assert fm.metadata(r)["event_status"]["ponding"] == ("REACHED" if horizon >= tp else "UNREACHED")
    with pytest.raises(fm.UnavailableObservation):
        fm.flow_minimum(r)
    with pytest.raises(fm.UnavailableObservation):
        fm.observe(np.nextafter(horizon, np.inf), r)


def test_horizon_at_saturation_does_not_extend_or_index_empty_events(result):
    horizon = result["t_s"]
    r = fm.solve(horizon_s=horizon)
    assert r["success"]
    assert r["actual_support_s"][1] <= horizon
    o = fm.observe(r["actual_support_s"][1], r)
    # A re-localized event can differ by roundoff at an exact endpoint. Report
    # REACHED only when localized within support, otherwise explicitly UNREACHED.
    if r["t_s"] is None:
        assert o["Q_out_m3_s"] == 0 and o["event_status"]["saturation"] == "UNREACHED"
        assert abs(o["s_m"]-r["p"].L)/r["p"].L < 1e-8
    else:
        assert o["s_m"] == r["p"].L
    json.dumps(fm.metadata(r), allow_nan=False)


@pytest.mark.parametrize("field,value", [("L", 0), ("H0", -1), ("A", 0), ("mu", 0),
    ("k", -1), ("phi_T", 0), ("phi_T", 1), ("p_m", 1e5), ("R_f", -1),
    ("beta", 0.5), ("beta", 20), ("p_c", -1), ("t_shift", np.nan), ("Q_m", np.inf)])
def test_invalid_parameters(field, value):
    with pytest.raises(fm.UnsupportedRegime):
        fm.solve(replace(fm.FosterParams(), **{field: value}))


def test_degenerate_ordering_and_real_but_negative_pump_root():
    p = fm.FosterParams()
    with pytest.raises(fm.UnsupportedRegime):
        fm.solve(replace(p, beta=1, p_c=0))
    with pytest.raises(fm.UnsupportedRegime):
        fm.solve(replace(p, L=1e-7))
    # Large R_f admits a real discriminant above shutoff, but its root is negative.
    p = replace(p, R_f=1e13)
    hstop = p.H0*(1-p.beta*p.p_a/p.p_m)
    h = hstop + 1e-8
    disc = p.R_f**2 + 4*(p.p_m-p.p_a)/p.Q_m**2*(p.p_m-fm.p_h(h,p))
    assert disc > 0 and h < p.H0
    with pytest.raises(fm.UnsupportedRegime, match="shutoff"):
        fm.Q_pump(h, p)
    with pytest.raises(fm.UnsupportedRegime, match="range"):
        fm.Q_pump(0, replace(fm.FosterParams(), beta=0.5))


@pytest.mark.parametrize("horizon", [-1, np.inf, np.nan])
def test_invalid_horizon(horizon):
    with pytest.raises(ValueError):
        fm.solve(horizon_s=horizon)


@pytest.mark.parametrize("which", ["rtol", "atol_scale", "max_step"])
def test_invalid_solver_settings(which):
    with pytest.raises(ValueError):
        fm.solve(**{which: 0})


@pytest.mark.parametrize("fail_call", [1, 2])
def test_failed_integration_never_yields_successful_observations(monkeypatch, fail_call):
    original = fm.solve_ivp
    calls = []

    def fail(*args, **kwargs):
        calls.append(1)
        if len(calls) == fail_call:
            return SimpleNamespace(success=False, message="injected numerical failure", t=np.array([args[1][0]]))
        return original(*args, **kwargs)

    monkeypatch.setattr(fm, "solve_ivp", fail)
    r = fm.solve()
    assert not r["success"] and r["status"] == "NUMERICAL_FAILURE"
    json.dumps(fm.metadata(r), allow_nan=False)
    for observer, t in [(fm._sH, 0), (fm.observe, 0), (fm.front_headspace_mm, r["p"].t_shift),
                        (fm.bed_flow_norm, r["p"].t_shift)]:
        with pytest.raises(fm.UnavailableObservation, match="NUMERICAL_FAILURE"):
            observer(t, r)
    with pytest.raises(fm.UnavailableObservation):
        fm.flow_minimum(r)


def test_internal_invalid_state_fails_explicitly(monkeypatch):
    def invalid(rhs, *args, **kwargs):
        rhs(1, [0.001, fm.FosterParams().H0])
    monkeypatch.setattr(fm, "solve_ivp", invalid)
    r = fm.solve()
    assert not r["success"] and r["status"] == "UNSUPPORTED_DOMAIN"
    with pytest.raises(fm.UnavailableObservation):
        fm.observe(0, r)


def test_inputs_are_copied(result):
    p = fm.FosterParams()
    r = fm.solve(p, horizon_s=0)
    p.Q_m *= 2
    assert r["p"].Q_m == result["p"].Q_m


def test_actual_entry_rhs_and_observation_determinism(result):
    p = result["p"]
    H = result["sol"].y_events[0][0][1]
    pressure = p.p_a*p.beta/(1-H/p.H0)
    a = (p.p_m-p.p_a)/p.Q_m**2
    qp = 2*(p.p_m-pressure)/(p.R_f+np.sqrt(p.R_f**2+4*a*(p.p_m-pressure)))
    f = p.k/(p.mu*p.L)*(pressure-p.p_a+p.p_c+p.rho*p.g*(H+p.L))
    expected = qp/p.A-f
    assert abs(result["post_entry_derivative_m_s"]-expected) < 1e-16
    times = [0, result["t_p"], result["t_s"], 8, 30]
    first = json.dumps([fm.observe(t,result) for t in times],sort_keys=True,allow_nan=False)
    second = json.dumps([fm.observe(t,result) for t in times],sort_keys=True,allow_nan=False)
    assert first == second


def test_gate_and_atlas_consumers_propagate_failure(result, monkeypatch):
    from puckworks.validation import gates
    from puckworks.analysis.response_atlas import runner
    failed = dict(result,success=False,status="NUMERICAL_FAILURE",message="injected")
    for gate in (gates.gate_foster_ct_trajectory, gates.gate_foster_fig15_flowmin,
                 gates.foster_fig15_windows):
        report = gate(failed)
        assert report["passed"] is False
        assert report["numerical_status"] == "NUMERICAL_FAILURE"
        json.dumps(report,allow_nan=False)
    monkeypatch.setattr(fm,"solve",lambda: failed)
    with pytest.raises(fm.UnavailableObservation):
        runner._foster_results()

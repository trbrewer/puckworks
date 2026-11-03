"""Structural checks of clocks, exact prefix evaluation and outer-fold isolation."""
import math
from unittest.mock import patch

import numpy as np
import pytest

from puckworks.analysis import joint_clock_001 as J
from puckworks.analysis import joint_clock_001_run as R
from puckworks.analysis import wetting_screen_001 as W

THETA = [.77, 24., 2.47, 3.56, 28.7]


@pytest.mark.parametrize("model,p", [("J0", THETA[:4]),
    ("J1", [*THETA[:4], 13.]), ("J2", [*THETA[:4], 1e-14, 4., 9.])])
def test_coordinates_and_fixed_mc(model, p):
    np.testing.assert_allclose(J.physical(J.coordinates(p, model), model), p)
    theta, _, _, lag = J.decode(p, model, 31.)
    assert theta[-1] == 31.
    assert lag == (9. if model == "J2" else 0.)


@pytest.mark.parametrize("arm,wet", [("Z", []), ("W1", [13.]), ("W2T", [1e-14, 4.])])
def test_extended_predictor_preserves_screen_and_hydraulic_column_identity(arm, wet):
    p = J.Prepared([0., 30., 100.], [2., 6., 11.], THETA, arm, wet, dt=.1, cells=16)
    full = p.chemistry(100.)
    old = W.predict([0., 30., 100.], [2., 6., 11.], THETA, arm, wet, dt=.1, cells=16)
    np.testing.assert_array_equal(p.mass, full["liquid_g"])
    np.testing.assert_array_equal(p.flow, full["bed_flow_g_s"])
    for field in ("liquid_g", "beverage_g", "remaining_g", "stored_solute_g"):
        np.testing.assert_allclose(full[field], old[field], rtol=1e-12, atol=1e-12)


@pytest.mark.parametrize("pressure,lag", [(1., 0.), (2., 0.), (6., 0.), (13., 9.5),
                                          (6., 80.), (6., 100.)])
def test_prefix_onset_matches_full_observer_and_keeps_original_censor_bound(pressure, lag):
    times = np.arange(.037, 100., .101)
    p = J.Prepared([0., 100.], [pressure]*2, THETA, "W1", [13.], dt=.02, cells=16)
    accelerated = p.observer(times, lag)
    full = W.observe(p.chemistry(100.), times, lag)
    for field in ("onset_s", "detected", "censor_bound_s", "last_timestamp_s", "samples"):
        assert accelerated[field] == full[field]
    if pressure == 6. and lag == 0.:
        assert accelerated["chemistry_until_s"] < 100.
    assert accelerated["censor_bound_s"] == times[times[-1]-times >= 2.][-1]


def test_front_does_not_shift_pressure_and_inventory_crosses_breakthrough():
    p = J.Prepared([0., 30., 130.], [2., 6., 11.], THETA, "W1", [13.], dt=.1, cells=16, horizon=130.)
    full = p.chemistry(130.)
    j = np.flatnonzero(p.time == 13.)[0]
    assert full["stored_solute_g"][j] > 0.
    assert full["remaining_g"][j] < full["remaining_g"][0]
    assert full["liquid_g"][j] == 0.
    np.testing.assert_allclose(p.scored_flow([50., 125.], 9.), np.interp([41., 116.], p.time, p.flow))
    with pytest.raises(ValueError, match="support"):
        p.scored_flow([140.])


def test_joint_objective_has_one_outer_mc_and_no_held_condition_target():
    data = dict(bank={"HYD-LOCO-2.0": THETA}, sources=[dict(brew=str(p), nominal_pressure_bar=p,
        observer_times_s=[0., 100.], fit_times_s=np.array([10., 20.]),
        fit_flow_g_s=np.array([1., 1.]), observed_onset_for_scoring_only_s=math.nan if p == 2. else 12.)
        for p in W.NOMINAL])
    seen = []
    class Fake:
        column_calls = 0
        def observer(self, times, lag, accelerate):
            return dict(onset_s=10., detected=True, censor_bound_s=98.)
        def scored_flow(self, times, lag):
            return np.array([.5, .5])
    def prepare(source, parameters, model, mc):
        seen.append((source["brew"], mc))
        return Fake(), 0.
    objective = R.Objective(data, "J0", .05, 2.)
    with patch.object(J, "prepare", prepare):
        value = objective(J.coordinates(THETA[:4], "J0"))
    assert len(seen) == 10 and ("2.0", THETA[-1]) not in seen
    assert all(mc == THETA[-1] for _, mc in seen)
    assert value == pytest.approx(.25/.437**2+.05*4/4.534**2)


def test_missing_support_is_unavailable_not_a_smaller_censor_bound():
    with pytest.raises(ValueError, match="support"):
        J.Prepared([0., 90.], [6., 6.], THETA, "Z", [])
    p = J.Prepared([0., 100.], [1., 1.], THETA, "Z", [], cells=16)
    with pytest.raises(ValueError, match="support"):
        p.observer(np.arange(101.1))


def test_predeclared_weight_count_and_start_isolation():
    assert J.WEIGHTS == (.05, .5, 1., 2.)
    assert len(J.MODELS)*len(J.WEIGHTS)*12 == 144
    data = dict(bank={"HYD-LOCO-2.0": THETA}, timing={
        ("HYD-LOCO-2.0", "W1"): dict(parameters=[13.]),
        ("HYD-LOCO-2.0", "W2"): dict(parameters=[1e-14, 5.]),
        ("HYD-LOCO-2.0", "W2T"): dict(parameters=[1e-14, 3.5, 10.])})
    for model, count in (("J0", 17), ("J1", 18), ("J2", 19)):
        starts = R.starts(data, model, 2.)
        assert len(starts) == count
        lo, hi = J.bounds(model)
        for _, z in starts:
            assert np.all(np.asarray(z) >= lo) and np.all(np.asarray(z) <= hi)


def test_final_scores_use_fine_step_and_paired_identical_draws():
    from puckworks.analysis import joint_clock_001_evaluate as E
    from puckworks.analysis import joint_clock_001_report as P
    sources=[]
    for i,p in enumerate(np.r_[np.repeat(W.NOMINAL,5),13.]):
        sources.append(dict(brew=str(i),nominal_pressure_bar=float(p),pressure_bar=[float(p)]*2,
            observed_endpoint_g_s=.5,observed_trace_g_s=[.5]*3,trace_times_s=[0.,10.,100.],
            trace_mask=[False,True,True],observed_onset_for_scoring_only_s=10.,
            b1_endpoint_g_s=.8,b1_trace_g_s=[.8]*3))
    arms=["D0", "W0", "W1", "W2", "W2T", *[E.arm_name(m,w) for w in J.WEIGHTS for m in J.MODELS]]
    rows=[]
    for arm in arms:
        for s in sources:
            row=dict(arm=arm,model=arm.split("_lambda")[0],weight=float(arm.split("-")[-1]) if "lambda" in arm else None,
                     scope="held_out",brew=s["brew"])
            for numerical,q,onset in (("fine",.6,12.),("search",.61,12.1)):
                row[numerical]=dict(endpoint_g_s=q,trace_g_s=[q]*3,
                    observer=dict(detected=True,onset_s=onset,censor_bound_s=98.))
            rows.append(row)
    reports,paired,_,_,_=P.scores(sources,rows,arms)
    r=reports["J2_lambda-1"]
    assert r["endpoint_rmse"]==pytest.approx(.1)
    assert r["endpoint_search_rmse"]==pytest.approx(.11)
    assert r["onset_rmse"]==2.
    assert r["onset_search_rmse"]==pytest.approx(2.1)
    assert r["onset_grade"]=="MEETS"
    assert r["accuracy_grade_vs_b1"]=="MEETS"
    assert len(paired)==96
    assert all(p["difference"]==p["lower_95"]==p["upper_95"]==0. for p in paired)

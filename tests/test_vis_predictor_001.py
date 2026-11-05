"""Synthetic contract checks; no private Visualizer records required."""
from dataclasses import replace
import json
from pathlib import Path

import numpy as np
import pytest
from numpy.testing import assert_allclose
from scipy.optimize._numdiff import approx_derivative

from puckworks.empirical.visualizer import (
    Design, Shot, capacity, capacity_maximum, encode, extract_windows,
    fitted_model, grouped_folds, load_model, predict, pressure_quadrature, save_model,
    solve_amplitude, start_schedule,
)
from puckworks.analysis.vis_predictor_001 import check_private, release_ok


def example(rate=1, user="u", key="s"):
    t = np.arange(0, 30.01, .25)
    w = np.maximum(t - 5, 0) * rate / 1000
    p = (5 + 2 * np.sin(t / 8)) * 1e5
    windows, flags, reason = extract_windows(t, p, w)
    assert reason == "retained"
    return Shot(key, user, windows, flags)


def test_increment_onset_window_and_mass():
    s = example()
    first = s.windows[0]
    assert first.start_s == 0
    assert first.mass_g == 1.25  # first native sample strictly above 1g, after pump start
    assert first.end_s == 2
    assert first.flow_g_s == pytest.approx(1)
    assert [w.start_s for w in s.windows if w.role == "calibration"] == [0, 2, 4]
    assert [w.start_s for w in s.windows if w.role == "guard"] == [6]
    assert min(w.start_s for w in s.windows if w.role == "score") == 8
    assert all(w.end_s - w.start_s == 2 for w in s.windows)
    assert s.windows[1].mass_g == pytest.approx(3.25)


def test_observation_ignores_supplied_flow_and_preserves_negative_increment():
    t = np.arange(0, 30.01, .25)
    weight = (t + 2) / 1000
    weight[(t >= 10) & (t <= 12)] -= .009
    windows, flags, reason = extract_windows(t, np.full(len(t), 5e5), weight,
                                            np.full(len(t), .999))
    assert reason == "retained"
    assert flags["negative_increment"] and flags["reset_like"]
    assert any(w.flow_g_s < 0 for w in windows)
    assert windows[0].flow_g_s == pytest.approx(1)
    assert flags["supplied_agreement"] == "disagree"


def test_gaps_never_bridged_and_missing_calibration_rejected():
    t = np.r_[np.arange(0, 11, .25), np.arange(14, 30, .25)]
    windows, flags, reason = extract_windows(t, np.full(len(t), 5e5), (t + 2) / 1000)
    assert reason == "retained" and flags["gap"]
    assert not any(w.start_s < 14 and w.end_s > 10.75 for w in windows)
    t = np.r_[np.arange(0, 2, .25), np.arange(5, 30, .25)]
    assert extract_windows(t, np.full(len(t), 5e5), (t + 2) / 1000)[2] == "calibration_support"


def test_timestamps_and_insufficient_support():
    assert extract_windows([0, 1, 1], [1e5] * 3, [0, .002, .003])[2] == "timestamps"
    t = np.arange(0, 8, .25)
    assert extract_windows(t, t * 1e5, t / 1000)[2] == "later_support"
    assert extract_windows(t, t * 1e5, np.zeros(len(t)))[2] == "no_delivery_onset"


def test_mean_of_response_not_response_of_mean():
    p, weights = pressure_quadrature(np.array([0, 2]), np.array([0, 4]), 0, 2)
    assert_allclose(p @ weights, 2)
    assert_allclose((p ** 2) @ weights, 16 / 3)
    assert not np.isclose((p ** 2) @ weights, (p @ weights) ** 2)
    assert_allclose(weights.sum(), 1)


@pytest.mark.parametrize("n", [1, 2.5, 20])
def test_exact_nesting(n):
    d = Design([example()])
    par = dict(n=n, Pd=3.5, Mc=20, kappa=0)
    assert np.array_equal(d.basis("AR", encode("AR", par)), d.basis("M0R", encode("M0R", par)))
    assert np.array_equal(d.basis("A", encode("A", par)), d.basis("M0", encode("M0", par)))
    assert_allclose(capacity([0, 1, 10], n, 3, 0), capacity([0, 1, 10], n, 3))


def test_start_mass_and_start_time_only():
    s = example()
    d = Design([s])
    assert_allclose(d.basis("R0", [np.log(10)]), np.exp(-np.exp(-d.mass / 10)))
    assert_allclose(d.basis("T0", [np.log(10)]), np.exp(-np.exp(-d.time / 10)))


def test_user_folds_no_leakage_and_order_invariant():
    users = [f"user{i}" for i in range(75)] * 3
    mapping = grouped_folds(users)
    assert mapping == grouped_folds(users[::-1])
    for fold in range(5):
        train = {u for u in users if mapping[u] != fold}
        test = {u for u in users if mapping[u] == fold}
        assert not train & test
        assert len(test) == 15
    with pytest.raises(ValueError):
        grouped_folds([""])


def test_amplitude_and_equal_user_weighting():
    assert solve_amplitude([2, 4], [1, 2]) == 2
    assert solve_amplitude([-2, -4], [1, 2]) == -2
    assert solve_amplitude([2, 4], [0, 0]) == 0
    d = Design([example(user="a"), example(user="a"), example(user="b")])
    assert_allclose(d.shot_weight, [.25, .25, .5])
    basis = d.basis("C0", [])
    assert_allclose(d.amplitudes(basis), [1, 1, 1])


@pytest.mark.parametrize("model", ["T0", "R0", "L0R", "M0R", "AR", "M0", "A"])
def test_profiled_gradient(model):
    d = Design([example(1), example(1.7, user="v")])
    theta = encode(model, dict(Tc=11, Mc=19, Pd=4, n=2.3, kappa=.13))
    value, derivative = d.objective(model, theta)
    numerical = approx_derivative(lambda x: d.objective(model, x)[0], theta).ravel()
    assert np.isfinite(value)
    assert_allclose(derivative, numerical, rtol=2e-5, atol=1e-7)


def test_saved_predictor_roundtrip_target_blindness_and_guard(tmp_path):
    model = fitted_model("AR", dict(n=2.5, Pd=3.5, Mc=20, kappa=.05))
    path = tmp_path / "model.json"
    save_model(path, model)
    restored = load_model(path)
    s = example()
    early = [w for w in s.windows if w.role == "calibration"]
    later = [w for w in s.windows if w.role == "score"]
    expected, a = predict(model, early, later)
    actual, b = predict(restored, early, [replace(w, flow_g_s=float("nan")) for w in later])
    assert_allclose(actual, expected)
    assert a == b
    with pytest.raises(ValueError, match="guard"):
        predict(model, early, [replace(later[0], start_s=6)])
    path.write_text("{}")
    with pytest.raises(ValueError, match="hash"):
        load_model(path)


def test_capacity_global_maximum_and_nesting_limit():
    params = dict(n=2.5, Pd=3.5, kappa=.05)
    result = capacity_maximum(params, [0, 20])
    peak = result["peak_bar"]
    assert result["stationary_points"] == 1 and result["inside_training_range"]
    grid = np.geomspace(.0001, 1e4, 10000)
    assert result["peak_capacity"] >= capacity(grid, **params).max()
    assert capacity(peak, **params) > capacity(peak * .999, **params)
    assert capacity_maximum({**params, "kappa": 0}, [0, 20])["peak_bar"] is None


def test_starts_nested_exact_and_n_unbounded():
    from puckworks.empirical.visualizer import coordinates
    historical = [dict(n=2, Pd=4, kappa=.1)]
    nested = fitted_model("M0R", dict(n=2.5, Pd=3, Mc=20))
    starts = start_schedule("AR", historical, nested)
    assert len(starts) == 18
    assert starts[0][2] == 0
    assert coordinates("AR")[1][0] == (1, None)
    assert_allclose(starts, start_schedule("AR", historical, nested))


def test_release_rules_and_private_path(tmp_path):
    shots = [Shot(str(i), str(i // 2), [], {}) for i in range(60)]
    assert release_ok(list(range(20)), shots, range(60))
    assert not release_ok(list(range(19)), shots, range(60))
    assert not release_ok(list(range(50)), shots, range(60))
    assert check_private(tmp_path) == tmp_path
    with pytest.raises(ValueError):
        check_private(Path(__file__).resolve().parents[1] / "private")


def test_committed_outputs_release_surface():
    out = Path(__file__).resolve().parents[1] / "docs/research/VIS_PREDICTOR_001"
    import csv
    for filename in ("SCORES.csv", "CONTRASTS.csv", "BREAKDOWNS.csv", "AGGREGATED_EXAMPLE.csv",
                     "FOLD_MANIFEST.csv", "FUNNEL.csv"):
        if not (out / filename).exists():
            continue  # pre-score test run; no scores are required for freezing the plan
        for row in csv.DictReader((out / filename).open()):
            assert not {"key", "user", "hashed_user", "id", "content_sha256"} & row.keys()
            if row.get("shots"):
                assert int(row["shots"]) >= 20 and int(row["users"]) >= 10
    for path in (out / "models").glob("*/*.json"):
        model = load_model(path)
        assert "amplitude" not in model
        assert not {"user", "key", "hashed_user", "id"} & model.keys()
    if (out / "FROZEN_MANIFEST.json").exists():
        assert json.loads((out / "FROZEN_MANIFEST.json").read_text())["seed"] == 20261105


def test_tiny_basis_matches_direct_solve():
    d = Design([example()])
    b = np.full(len(d.windows), 1e-160)
    assert_allclose(d.predictions(b), np.ones(len(b)))
    assert_allclose(d.amplitudes(b), [solve_amplitude(d.q[d.cal], b[d.cal])])


def test_quadrature_audit_blocks_sharp_unresolved_shapes():
    from puckworks.empirical.visualizer import Settings, Window, audit_quadrature
    p, wt = pressure_quadrature(np.array([0, 2]), np.array([0, 2]), 0, 2, order=16)
    window = Window(0, 2, 1, 999, p, wt, 2, "calibration")
    shot = Shot("x", "u", [window], {})
    model = fitted_model("M0", dict(n=1000, Pd=.9))
    assert not audit_quadrature([shot], model)["passed"]
    model = fitted_model("M0", dict(n=1, Pd=.9))
    assert audit_quadrature([shot], model)["passed"]
    assert Settings().quadrature_order == 16


def test_sparse_operator_preserves_native_window_quadrature():
    s = example()
    d = Design([s])
    params = dict(n=2.8, Pd=3.7, kappa=.12)
    expected = [w.quadrature_weight @ capacity(w.pressure_bar, **params) for w in s.windows]
    assert_allclose(d.basis("A", encode("A", params)), expected, rtol=1e-14, atol=1e-14)


def test_quadrature_gate_scales_full_recovery_basis():
    from puckworks.empirical.visualizer import Window, audit_quadrature
    p, wt = pressure_quadrature(np.array([0, 2]), np.array([10, 10]), 0, 2, order=16)
    early = [Window(i, i+2, 1.1, 0, p, wt, 0, "calibration") for i in (0, 2, 4)]
    p, wt = pressure_quadrature(np.array([0, 2]), np.array([0, 9.671]), 0, 2, order=16)
    later = Window(8, 10, 100, 0, p, wt, 9.671, "score")
    model = fitted_model("M0R", dict(n=1000., Pd=10., Mc=10.))
    result = audit_quadrature([Shot("x", "u", early + [later], {})], model)
    assert not result["passed"]
    assert result["maximum_relative_error"] > 1e-5

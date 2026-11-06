"""Focused no-fit controls for frozen replay and disclosure-safe coverage."""
import csv
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import turnover_time_replay_001 as T
from puckworks.analysis import turnover_time_replay_001_coverage as V
from puckworks.analysis import turnover_time_replay_001_report as R


def test_held_condition_parameters_and_mc_are_matched():
    sources = [dict(brew=f"{p}-{i}", nominal_pressure_bar=p) for p in (9., 11., 13.) for i in range(2)]
    row = dict(fold="HYD-LOCO-11.0", held_condition_bar=11., model="J1", weight=1.,
               parameters=[1., 20., 2., 3., 10.], mc_fixed_g=25.,
               training_brews=[s["brew"] for s in sources if s["nominal_pressure_bar"] != 11.])
    data = dict(sources=sources, joint_fits={row["fold"]: row}, bank={row["fold"]: [1, 20, 2, 3, 25.]})
    parameters, mc, fold = T.select_parameters("A-J1", "LOCO", sources[2], data)
    assert mc == 25. and fold == row["fold"] and parameters[-1] == 10.
    row["mc_fixed_g"] = 30.
    with pytest.raises(ValueError, match="Mc"):
        T.select_parameters("A-J1", "LOCO", sources[2], data)
    row["mc_fixed_g"] = 25.
    row["training_brews"].append(sources[3]["brew"])
    with pytest.raises(ValueError, match="membership"):
        T.select_parameters("A-J1", "LOCO", sources[2], data)


def test_observed_onset_controls_windows_independently_of_detector():
    for detector in (dict(detected=False, onset_s=None), dict(detected=True, onset_s=80.)):
        # Neither detection status nor predicted onset is a window argument.
        assert T.observed_center(12., "onset", 10.) == 22.
        assert T.observed_center(12., "stable_pressure", 10.) == 10.
        assert detector["onset_s"] != 12.


def test_nondetection_remains_a_prediction(monkeypatch):
    def synthetic(job):
        return [dict(available=True, predicted_beverage_flow_g_s=0.)], dict(detected=False, onset_s=None), dict(cpu_seconds=0.)
    monkeypatch.setattr(T, "measured_replay_case", synthetic)
    rows, onset, _ = T.replay_case(None)
    assert onset["prediction_available"] and not onset["detected"]
    assert len(rows) == 1 and rows[0]["predicted_beverage_flow_g_s"] == 0.


def test_measured_replay_retains_observed_windows_when_detector_fails(monkeypatch, tmp_path):
    native = np.arange(0., 121., .1)
    source = dict(brew="synthetic", nominal_pressure_bar=13., predict_times_s=native,
                  predict_pressure_bar=np.full(len(native), 13.), predict_horizon_s=native[-1],
                  observer_times_s=native[native <= 100.])
    observed = {}
    for clock, offset in T.O.SNAPSHOTS:
        observed[source["brew"], clock, offset] = dict(available="True", reason="available",
                                                     pressure_bar="13.0", flow_g_s="2.0")
    monkeypatch.setattr(T, "_DATA", dict(native={"synthetic": (native, np.full(len(native), 13.),
                                                               np.full(len(native), 2.), 7.)},
                                        observed=observed))
    (tmp_path / "predictions").mkdir()
    monkeypatch.setattr(T, "_ARGS", SimpleNamespace(private=tmp_path))
    monkeypatch.setattr(T, "select_parameters", lambda *args: (np.array([1., 2., 3., 4., 5.]), 25., "fold"))

    class Predictor:
        def __init__(self, *args):
            self.time = native
            self.cap = self.flow = self.front = np.ones(len(native))
            self.mass = 2*native

        def chemistry(self, horizon):
            assert horizon == native[-1]
            return dict(time=native, beverage_g=2*native)

    monkeypatch.setattr(T.J, "Prepared", Predictor)
    monkeypatch.setattr(T.W, "observe", lambda *args: dict(onset_s=None, detected=False,
                                                         censor_bound_s=100., samples=1001))
    rows, onset, receipt = T.replay_case(("A-J1", "LOCO", source))
    assert len(rows) == len(T.O.SNAPSHOTS) == 10
    assert onset["prediction_available"] and not onset["detected"]
    assert receipt["artifact"] is not None
    for row in rows:
        expected = row["time_s"] + (7. if row["clock"] == "onset" else 0.)
        assert row["window_start_stable_s"] == expected-1.
        assert row["window_end_stable_s"] == expected+1.
        assert row["available"]
        assert row["predicted_beverage_flow_g_s"] == pytest.approx(2.)
        assert row["achieved_pressure_bar"] == 13.


def test_missing_prediction_cannot_silently_reduce_condition():
    observed = np.array([[1., 2., 3., 4.], [2., 3., 4., 5.]])
    predicted = observed.copy()
    predicted[0, 0] = np.nan
    result = R.complete_observed_conditions(predicted, observed, np.array([9., 9., 13., 13.]))
    assert np.isnan(result[0, :2]).all()
    np.testing.assert_array_equal(result[0, 2:], observed[0, 2:])
    np.testing.assert_array_equal(result[1], observed[1])


def test_paired_change_uses_shared_draw_indices_not_interval_endpoints():
    draws = np.arange(1000.)
    actual = R.paired_difference("delta", 7., 3., draws + 7, draws + 3)
    assert actual["delta"] == actual["delta_lo"] == actual["delta_hi"] == 4.
    condition = np.repeat([9., 11., 13.], 3)
    bank = T.O.draw_bank(condition)
    original_hash = T.O.bank_digest(bank)
    base = np.arange(9.) + 1
    q = np.stack([base + k for k in range(10)])
    _, _, bp, bq, _ = T.O.condition_statistics(q*2, q, condition, bank)
    np.testing.assert_allclose(bp, 2*bq)
    np.testing.assert_allclose(bq[9]-bq[0], 9.)
    assert T.O.bank_digest(bank) == original_hash


def test_native_beverage_mass_derivative_then_fixed_window_and_pressure():
    fine = np.arange(0., 110.005, .005)
    native = np.arange(0., 108., .093)
    prediction = dict(time=fine, beverage_g=2*fine + .01*fine**2,
                      bed_flow_g_s=np.full(len(fine), 123.))
    observed = T.beverage_observer(prediction, native)
    p, q, reason = T.O.paired_window(native, 9 + .01*native, observed, 100.)
    assert reason == "available"
    assert p == pytest.approx(10.)
    assert q == pytest.approx(4., abs=2e-8)
    assert q != 123.  # Instantaneous liquid output is not the beverage observer.
    with pytest.raises(ValueError, match="support"):
        T.beverage_observer(dict(time=fine[fine <= 100], beverage_g=2*fine[fine <= 100]), native)


@pytest.mark.parametrize("pressure,index", [(8.99, 0), (9., 1), (10., 1), (np.nextafter(10., np.inf), 2),
    (11., 2), (np.nextafter(11., np.inf), 3), (12., 3), (13., 4), (np.nextafter(13., np.inf), 5)])
def test_visualizer_exact_pressure_bin_boundaries(pressure, index):
    assert V.pressure_bin(pressure) == index


def shot(user, p, times=(8., 10., 12.)):
    windows = [SimpleNamespace(role="score", mean_pressure_bar=p, start_s=t, end_s=t+2) for t in times]
    windows += [SimpleNamespace(role=role, mean_pressure_bar=99., start_s=0., end_s=2.)
                for role in ("calibration", "guard")]
    return SimpleNamespace(user=user, windows=windows)


def test_score_roles_actual_denominator_and_window_weighted_midpoints():
    shots = [shot(str(i % 10), p) for p in (8., 9.5, 10.5, 11.5, 12.5, 14.) for i in range(20)]
    rows, audit = V.census(shots)
    assert audit["partition_releasable"]
    assert audit["retained_windows"] == 600
    assert rows[0]["scored_windows"] == 360
    assert sum(r["scored_windows"] for r in rows[1:]) == 360
    for row in rows[1:]:
        assert row["scored_windows"] == 60 and row["distinct_shots"] == 20 and row["distinct_users"] == 10
        assert row["midpoint_median_s"] == 11.
        assert row["percent_all_scored"] == pytest.approx(100/6)
    # One shot can appear in several bins; distinct-shot totals are never summed.
    shots[0].windows.append(SimpleNamespace(role="score", mean_pressure_bar=10.5, start_s=98., end_s=100.))
    _, audit = V.census(shots)
    assert audit["scored_windows"] == 361


def test_unsafe_cell_withholds_entire_partition_and_derived_values():
    shots = [shot(str(i % 10), 8.) for i in range(40)] + [shot("private-user", 14.)]
    rows, audit = V.census(shots)
    assert not audit["partition_releasable"]
    assert rows[0]["scored_windows"] == 123  # Safe standalone all-score denominator.
    for row in rows[1:]:
        assert row["release"] == "whole_partition_withheld"
        assert all(v is None for k, v in row.items() if k not in ("pressure_bin", "release"))
    serialized = json.dumps(rows)
    assert "private-user" not in serialized
    assert "midpoint_median_s\": 99" not in serialized


def test_complement_and_actual_user_linkage_are_protected():
    shots = [shot(str(i % 10), 8.) for i in range(120)]
    shots[110].user = "rare-transition"
    universe = set(range(120))
    groups = [set(range(100)), set(range(20, 120))]
    assert all(V.cell_safe(ids, shots, universe) for ids in groups)
    assert not V.partition_safe(groups, shots, universe)
    assert not V.cell_safe(set(range(105)), shots, universe)  # 15-shot complement.


def test_safe_empty_cell_is_distinct_from_withheld():
    rows, audit = V.census([shot(str(i % 10), 8.) for i in range(40)])
    assert audit["partition_releasable"]
    assert rows[-1]["scored_windows"] == 0
    assert rows[-1]["midpoint_median_s"] is None
    assert rows[-1]["release"] == "released"


def test_passive_snapshot_adapter_preserves_mean_pressure():
    w = V.SnapshotWindow()
    w.pressure_bar = np.array([9., 11., 13.])
    w.quadrature_weight = np.array([.2, .5, .3])
    assert w.mean_pressure_bar == pytest.approx(11.2)


def test_committed_historical_reproduction_is_complete():
    with (T.OUT / "HISTORICAL_REPRODUCTION.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 317
    assert all(r["passed"] == "True" for r in rows)
    assert sum(r["numerical"] == "fine" for r in rows) == 158
    assert sum(r["numerical"] == "search" for r in rows) == 158
    assert sum(r["case"] == "D0-original-fixture" for r in rows) == 1


def test_committed_source_and_resample_bank_identities():
    receipt = T.read_json(T.OUT / "RUN_RECEIPT.json")
    for path, expected in receipt["code_sha256"].items():
        assert T.O.digest(T.ROOT / path) == expected
    assert T.O.digest(T.OUT / "PLAN.md") == receipt["plan_sha256"]
    assert T.O.digest(T.OUT / "PARAMETER_BANK.json") == receipt["parameter_bank_sha256"]
    with (T.OUT / "DETECTOR_ONSETS.csv").open() as f:
        onsets = list(csv.DictReader(f))
    condition_by_brew = {r["brew"]: float(r["nominal_pressure_bar"]) for r in onsets}
    assert set(condition_by_brew) == set(receipt["brew_order"])
    condition = np.array([condition_by_brew[b] for b in receipt["brew_order"]])
    assert T.O.bank_digest(T.O.draw_bank(condition)) == receipt["draw_bank_sha256"]
    assert receipt["draw_bank_sha256"] == T.read_json(T.OUT / "INPUT_MANIFEST.json")["draw_bank_sha256"]


def test_committed_phase_changes_match_their_trajectory_endpoints():
    with (T.OUT / "TRAJECTORIES_9_11_13.csv").open() as f:
        rows = list(csv.DictReader(f))
    snapshots = {(r["model"], r["scope"], r["clock"], int(r["time_s"]), float(r["nominal_pressure_bar"])): r
                 for r in rows if r["record_type"] == "snapshot"}
    for row in rows:
        if row["record_type"] not in ("phase", "adjacent"):
            continue
        identity = row["model"], row["scope"], row["clock"]
        a, b = int(row["start_time_s"]), int(row["end_time_s"])
        for signal in ("observed", "predicted"):
            def increment(c):
                key = signal + "_beverage_flow_g_s"
                return float(snapshots[(*identity, b, c)][key]) - float(snapshots[(*identity, a, c)][key])
            expected = (increment(9.)-increment(13.) if row["trajectory"] == "9_minus_13"
                        else increment(float(row["trajectory"])))
            assert float(row[signal + "_increment_g_s"]) == pytest.approx(expected, abs=1e-12)
        assert float(row["observed_minus_predicted_increment_g_s"]) == pytest.approx(
            float(row["observed_increment_g_s"])-float(row["predicted_increment_g_s"]), abs=1e-12)


def test_committed_visualizer_partition_exposes_no_suppressed_derivatives():
    with (T.OUT / "VIS_HIGH_PRESSURE_COVERAGE.csv").open() as f:
        rows = list(csv.DictReader(f))
    assert rows[0]["pressure_bin"] == "ALL_SCORED"
    assert int(rows[0]["scored_windows"]) == 118542
    assert len(rows) == 7
    for row in rows[1:]:
        assert row["release"] == "whole_partition_withheld"
        assert all(value == "" for key, value in row.items() if key not in ("pressure_bin", "release"))

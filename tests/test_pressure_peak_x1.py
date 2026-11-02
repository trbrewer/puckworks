"""Synthetic selection checks and offline plug-in arithmetic; no private shots."""

import csv
import json

import numpy as np
import pytest
from numpy.testing import assert_allclose

from puckworks import data
from puckworks.analysis import pressure_peak_x1 as x1


def test_projection_does_not_decode_weight_or_flow(monkeypatch):
    class Guard:
        def raw_decode(self, text, i):
            assert not text[i:].startswith("[987654")
            return json.JSONDecoder().raw_decode(text, i)

    monkeypatch.setattr(x1, "DECODER", Guard())
    text = '{"other":{"escaped":"a\\"b"},"hydraulic":{"time__s":[0,1],"pressure__Pa":[900000,500000],"weight__kg":[987654,987654],"flow":[987654,987654]}}'
    rec, end = x1.project(
        text, {"hydraulic": {"time__s": True, "pressure__Pa": True, "weight__kg": "LENGTH"}}
    )
    assert end == len(text)
    assert rec["hydraulic"]["weight__kg"] == 2
    assert "flow" not in rec["hydraulic"]


def test_support_and_resolution():
    t = np.array([0, 1, 1, 2, 3, 4.0])
    p = np.array([9, 8, 7, np.nan, 6, 5.0]) * 1e5
    blocks = x1.support_blocks(t, p)
    assert blocks == [(0, 2), (2, 3), (4, 6)]
    assert_allclose(x1.resolution(p, blocks), 1e5, rtol=1e-12, atol=0)
    assert x1.resolution(np.ones(3), [(0, 3)]) is None


def test_sweep_primary_secondary_and_full_excursion():
    p = np.array([9.2, 9, 8, 8.1, 7, 6, 5, 4.9]) * 1e5
    t = np.arange(len(p), dtype=float)
    assert not x1.sweep_runs(t, p, [(0, len(p))], 0)
    selected = x1.sweep_runs(t, p, [(0, len(p))], 10000)
    assert len(selected) == 1
    assert_allclose([selected[0]["t0"], selected[0]["t1"]], [1, 6], rtol=1e-12, atol=0)
    p = np.array([9, 8, 8.1, 8.2, 5]) * 1e5
    assert not x1.sweep_runs(np.arange(5.0), p, [(0, 5)], 10000)


def test_flat_maximal_intervals_against_exhaustive_definition():
    rng = np.random.default_rng(20261101)
    for _ in range(30):
        p = 800000 + 1000 * rng.integers(-2, 3, 30)
        t = np.arange(30.0)
        all_valid = [
            (s, e)
            for s in range(30)
            for e in range(s + 11, 31)
            if np.max(np.abs(p[s:e] - np.median(p[s:e]))) <= 1000
        ]
        maximal = [
            (s, e)
            for s, e in all_valid
            if not any(a <= s and e <= b and (a, b) != (s, e) for a, b in all_valid)
        ]
        actual = x1.flat_runs(t, p, [(0, 30)], 1000)
        assert [(r["start"], r["end"]) for r in actual] == maximal


def test_labels_and_explicit_states():
    assert x1.machine_label("Decent DE1") == "DE1/Decent"
    assert x1.machine_label("GaggiMate") == "Gaggiuino/GaggiMate"
    assert x1.machine_label("Decent", "Meticulous") == "other/unknown"
    assert x1.phase([4, 4], 0, 2) == "state_unknown"
    assert x1.phase(["espresso", "venting"], 0, 2) == "explicit_non_brewing"


@pytest.mark.parametrize("t", [294.0, 365.01, 369.15])
def test_table_outside_domain_never_calls_clamping_loader(monkeypatch, t):
    def forbidden(*args):
        raise AssertionError("Clamping loader called outside table")

    monkeypatch.setattr(data, "telisromero_eta_measured", forbidden)
    assert x1.table_root(t, 2.7)[0] is None


def test_property_inverse_and_geometry():
    for r in x1.property_rows():
        assert_allclose(r["bed_volume_ml"], np.pi * 29**2 * 14 / 1000, rtol=1e-12, atol=0)
        assert_allclose(
            r["Mc_pore_volumes_times_porosity"]
            * r["water_density_kg_m3"]
            * r["bed_volume_ml"]
            * 1e-6,
            x1.MC / 1000,
            rtol=1e-12,
            atol=0,
        )
        if r["water_percent"] is not None:
            fn = (
                data.telisromero_viscosity_pas
                if r["method"] == "Eq10"
                else data.telisromero_eta_measured
            )
            assert_allclose(
                fn(r["temperature_K"], r["water_percent"]),
                r["target_viscosity_Pa_s"],
                rtol=1e-12,
                atol=0,
            )


def synthetic_segment(t, w):
    t, w = np.asarray(t, dtype=float), np.asarray(w, dtype=float)
    record = dict(
        id="synthetic", label="DE1/Decent", t=t.tolist(), p=(np.ones(len(t)) * 8e5).tolist()
    )
    window = dict(start=0, end=len(t), t0=t[0], t1=t[-1], phase="state_unknown")
    return x1.segment_flow(record, (w / 1000).tolist(), window)


def test_final_quarter_normalization_and_negative_readings():
    s = synthetic_segment([0, 2, 4, 8, 12], [0, 2, 1, 5, 13])
    assert s["usable"] and s["negative_increments"]
    assert_allclose(s["normalizer_g_s"], 2.0, rtol=1e-12, atol=0)
    assert_allclose(s["mean_flow_g_s"], 13 / 12, rtol=1e-12, atol=0)
    assert_allclose(x1.mass_value(s, 1.5)[0], 1.0, rtol=1e-12, atol=0)
    assert x1.mass_value(s, 1.5)[1] == 2
    assert np.isnan(x1.mass_value(s, 14)[0])


def test_support_intersection_and_population_spread():
    a = synthetic_segment([0, 5, 10], [0, 5, 15])
    b = synthetic_segment([0, 5, 10], [0, 10, 30])
    summary, points = x1.collapse([a, b], [(0, 0), (5, 7.5), (10, 20)])
    assert [p["contributors"] for p in points] == [2, 2, 1]
    # At the middle paired index, mass samples normalized flows 1 and 0.5;
    # time samples both 1. Only the first two indices support a variance.
    assert_allclose(points[1]["mass_variance"], 0.0625, rtol=1e-12, atol=0)
    assert_allclose(summary["mass_spread"], np.sqrt(0.0625 / 2), rtol=1e-12, atol=0)
    assert_allclose(summary["time_spread"], 0.0, rtol=1e-12, atol=0)


def test_flow_tercile_ties_preserved_and_zero_normalizer_kept():
    segments = [synthetic_segment([0, 10], [0, q * 10]) for q in (0, 1, 1, 1, 2, 3)]
    rows = x1.flow_bins(segments)
    own = [r for r in rows if r["stratum"] == "DE1/Decent"]
    assert [r["segments"] for r in own] == [6, 4, 0, 2]
    assert sum(r["segments"] for r in own[1:]) == len(segments)
    summary, points = x1.collapse(segments, [(0, 0)])
    assert summary["segments"] == 6 and points[0]["contributors"] == 5


def test_committed_rheology_replay():
    saved = list(csv.DictReader((x1.OUT / "VISCOSITY_BOUND.csv").open()))
    for expected, actual in zip(saved, x1.property_rows(), strict=True):
        for key, value in actual.items():
            if isinstance(value, (int, float)):
                assert_allclose(float(expected[key]), value, rtol=1e-12, atol=0)
            else:
                assert expected[key] == ("" if value is None else value)


def test_committed_collapse_from_aggregate_variances():
    points = list(csv.DictReader((x1.OUT / "COLLAPSE_GRID.csv").open()))
    rows = list(csv.DictReader((x1.OUT / "COLLAPSE.csv").open()))
    for r in rows:
        chosen = [
            p for p in points if all(p[k] == r[k] for k in ("stratum", "tercile", "grid_view"))
        ]
        assert [int(p["j"]) for p in chosen] == list(range(21))
        supported = [p for p in chosen if int(p["contributors"]) >= 2]
        assert len(supported) == int(r["supported_indices"])
        if not supported:
            assert r["direction"] == "unavailable" and not r["mass_spread"]
            continue
        values = [
            np.sqrt(np.mean([float(p[axis + "_variance"]) for p in supported]))
            for axis in ("mass", "time")
        ]
        assert_allclose(
            [float(r["mass_spread"]), float(r["time_spread"])], values, rtol=1e-12, atol=0
        )
        assert_allclose(float(r["mass_minus_time"]), values[0] - values[1], rtol=1e-12, atol=0)
        expected = "mass" if values[0] < values[1] else "time" if values[1] < values[0] else "tie"
        assert r["direction"] == expected
        assert (r["role"] == "PRIMARY_CLOCK_COMPARISON") == (
            r["tercile"] == "all" and r["grid_view"] == "primary_median_matched"
        )


def test_committed_bins_and_median_matched_grid():
    bins = list(csv.DictReader((x1.OUT / "MEAN_FLOW_BINS.csv").open()))
    grids = list(csv.DictReader((x1.OUT / "CLOCK_GRIDS.csv").open()))
    for label in (*x1.LABELS, x1.POOLED):
        rows = [r for r in bins if r["stratum"] == label]
        assert int(rows[0]["segments"]) == sum(int(r["segments"]) for r in rows[1:])
    for r in grids:
        assert_allclose(float(r["time_s"]), int(r["j"]) / 2, rtol=1e-12, atol=0)
        if r["qbar_med_g_s"]:
            assert_allclose(
                float(r["primary_mass_g"]),
                float(r["qbar_med_g_s"]) * float(r["time_s"]),
                rtol=1e-12,
                atol=0,
            )
        assert r["credit"] == x1.CREDIT


def test_sweep_signs_keep_one_sided_support_and_plateaus():
    s = dict(t=[0, 1, 2, 3, 4, 5], p=[9e5, 8e5, 7e5, 6e5, 6e5, 5e5], q=[1, 2, 3, 4, 5])
    r = x1.sweep_signs(s)
    assert r["above6_negative"] == 3
    assert r["below6_negative"] == 1
    assert r["above6_whole_side_negative"] == 1
    assert r["below6_whole_side_negative"] == 1

"""Contract-shape matrix (WP0.6): synthetic fixtures modeling the live Visualizer response
SHAPES, asserting each normalizes to the expected structural outcome. This is the one place
the shape contract is documented + guarded, so a serializer change surfaces as a failing test
rather than silent data corruption. Fixtures are clearly-fake (SHAPE-* / FAKE-* ids)."""
import json
from pathlib import Path

import pytest

from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig

SHAPES = Path(__file__).resolve().parent / "fixtures" / "visualizer" / "shapes"


def _load(name):
    with open(SHAPES / name, encoding="utf-8") as fh:
        return json.load(fh)


def _cfg():
    return HarvestConfig(salt="shape-test")


def test_chart_data_toplevel():
    t = normalize_shot(_load("chart_data_toplevel.json"), _cfg())
    assert t["n_samples"] == 3
    hy = t["hydraulic"]
    assert hy["pressure__Pa"][1] == pytest.approx(9.0e5)
    assert hy["pressure_goal__Pa"][0] == pytest.approx(9.0e5)
    assert hy["mass_flow_from_scale__kg_per_s"][2] == pytest.approx(1.9e-3)
    assert t["machine"] == "decent"


def test_legacy_nested_timeframe():
    t = normalize_shot(_load("legacy_nested_timeframe.json"), _cfg())
    assert t["n_samples"] == 2                       # nested data.timeframe fallback still works
    assert "missing:timeframe" not in t["flags"]


def test_brewdata_only_has_no_normalized_telemetry():
    # documents the P0-06 limitation: a brewdata-only shape yields no hydraulic trace today.
    t = normalize_shot(_load("brewdata_only.json"), _cfg())
    assert t["n_samples"] == 0
    assert "missing:timeframe" in t["flags"]
    assert t["machine"] == "gaggiuino"               # source still inferred


def test_zero_sensory_kept():
    t = normalize_shot(_load("zero_sensory.json"), _cfg())
    sens = t["outcomes"]["sensory"]
    assert sens["espresso_enjoyment"] == 0           # a real 0 is kept (0..100 scale)
    assert sens["flavor"] == 7


def test_ambiguous_flow_native_and_missing_goal():
    t = normalize_shot(_load("ambiguous_flow_missing_goal.json"), _cfg())
    hy = t["hydraulic"]
    assert hy["flow_reported__native"] == [0.0, 2.0]  # NATIVE, not kg/s
    assert t["units"]["hydraulic"]["flow_reported__native"]["si"] is None
    assert "flow__kg_per_s" not in hy
    assert any(f.startswith("unit_ambiguous:espresso_flow") for f in t["flags"])
    assert "missing:espresso_pressure_goal" in t["flags"]


def test_mixed_samples_aligned_and_flagged():
    t = normalize_shot(_load("mixed_samples.json"), _cfg())
    p = t["hydraulic"]["pressure__Pa"]
    assert len(p) == 4                                # alignment preserved
    assert p[0] == pytest.approx(6.0e5) and p[3] == pytest.approx(9.0e5)
    assert p[1] is None and p[2] is None              # bool + non-numeric dropped in place
    assert any(f.startswith("bad_samples:espresso_pressure=") for f in t["flags"])

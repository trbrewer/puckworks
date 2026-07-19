"""Unit-safe scientific visualization tests (PV-19B Phase 3, #43 / #70).

Offline + deterministic. Guards the single hard rule that a scientific figure must never overlay
incompatible units (bar / g/s / g / % / kg/m^3 / kg / m^3) on one ordinary y-axis: the shared plotting
layer splits every trace into one panel per unit, a mixed-unit panel is rejected by an explicit
validator, and the batch emits a figure + a CSV text-alternative per panel with a required-figure gate.
"""
import importlib

import pytest

from puckworks.product import lab

_FORBIDDEN_ON_ONE_AXIS = {"bar", "g/s", "g", "%", "kg/m^3", "kg", "m^3", "s"}


@pytest.fixture(scope="module")
def report():
    return lab.build_comparison(lab.execute_scenario(lab.ScenarioRequest("pv19_named")))


# ── the shared plotting layer is unit-safe by construction ──────────────────────────
def test_every_panel_carries_exactly_one_unit(report):
    panels = lab.render_data(report)
    assert panels
    for p in panels:
        units = {s["unit"] for s in p["series"]}
        assert len(units) == 1, f"panel {p['panel_id']} mixes units {units}"
        assert p["unit"] in units
        # the y-axis label names the unit (accessibility + no ambiguity)
        assert str(p["unit"]) in p["y_label"]


def test_the_mixed_unit_source_trace_is_actually_split(report):
    # the machine-flow trace legitimately holds bar + g/s + g; it MUST become >= 2 unit panels, never one
    panels = lab.render_data(report)
    flow_panels = [p for p in panels if p["trace_id"] == "machine_flow_time"]
    assert len(flow_panels) >= 2
    assert {p["unit"] for p in flow_panels} >= {"bar", "g/s"}


def test_no_two_incompatible_units_ever_share_a_panel(report):
    for p in lab.render_data(report):
        units = {str(s["unit"]) for s in p["series"]}
        assert len(units & _FORBIDDEN_ON_ONE_AXIS) <= 1 or len(units) == 1


def test_assert_unit_safe_rejects_a_mixed_unit_panel():
    bad = {"panel_id": "x", "series": [{"unit": "bar", "y": [1]}, {"unit": "g/s", "y": [2]}]}
    with pytest.raises(ValueError):
        lab.assert_unit_safe(bad)
    ok = {"panel_id": "y", "series": [{"unit": "kg/m^3", "y": [1]}, {"unit": "kg/m^3", "y": [2]}]}
    assert lab.assert_unit_safe(ok) is ok


def test_panel_inventory_reports_units_and_counts(report):
    inv = lab.panel_inventory(report)
    assert inv and all("unit" in row and row["n_series"] >= 1 for row in inv)
    assert len(inv) == len(lab.render_data(report))


# ── the batch renders one figure + one CSV per unit panel (required-figure gate) ─────
def test_batch_writes_one_unit_safe_figure_and_csv_per_panel(tmp_path):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    import json
    report = lb.run({"LAB_OUT_DIR": str(tmp_path), "LAB_PRESET": "guided_v1"})
    manifest = json.loads((tmp_path / "artifact_manifest.json").read_text())
    inv = manifest["panel_inventory"]
    panels = lab.render_data(report)
    assert len(inv) == len(panels) >= 2
    # every panel has both a figure and a CSV text-alternative present and hash-listed
    for row in inv:
        assert (tmp_path / row["figure"]).exists() and (tmp_path / row["csv"]).exists()
        assert row["figure"] in manifest["files"] and row["csv"] in manifest["files"]
        # the CSV header carries the panel's single unit (text alternative to the figure)
        header = (tmp_path / row["csv"]).read_text(encoding="utf-8").splitlines()[0]
        assert str(row["unit"]) in header
    # the back-compat required figure is still emitted
    assert (tmp_path / "guided_pull_lab_trace.png").exists()


def test_required_figure_gate_fails_when_nothing_plottable(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    monkeypatch.setattr(lb.lab, "render_data", lambda report: [])
    with pytest.raises(RuntimeError):
        lb.run({"LAB_OUT_DIR": str(tmp_path)})


def test_panel_figure_refuses_a_mixed_unit_panel(tmp_path):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    bad = {"panel_id": "x", "x": [0, 1], "x_label": "t (s)", "y_label": "mixed", "title": "bad",
           "series": [{"label": "p", "role": "prescribed_input", "unit": "bar", "y": [1, 2]},
                      {"label": "q", "role": "simulated", "unit": "g/s", "y": [3, 4]}]}
    with pytest.raises(ValueError):
        lb._panel_figure(tmp_path / "bad.png", bad)

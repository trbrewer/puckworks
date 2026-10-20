"""R-05/T06: descriptive public source tables, not a solver/theorem test."""
import csv
import json
from pathlib import Path

import numpy as np
import pytest

from puckworks import data
from puckworks.validation.gates import gate_fasano_cor82_nonmonotone as gate

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = "fasano2000_partI.fines_migration"
GATE = "gate_fasano_cor82_nonmonotone"


@pytest.mark.parametrize("series,pressure,flow,segment,midpoint,q_gap,final", [
    ("beta1", 0.310, 0.235, (0.32, 0.33), 0.325, 0.090, 0.173),
    ("beta2", 0.210, 0.153, (0.22, 0.23), 0.225, 0.072, 0.121),
])
def test_retained_coordinate_diagnostics(series, pressure, flow, segment, midpoint, q_gap, final):
    # Independent reduction of CSV bytes, not the gate's reported diagnostics.
    folder = ROOT / "puckworks/data/fasano2000_partI"
    with (folder / "fig8_6_asymptotic_q_vs_p0.csv").open() as f:
        response = np.array([(float(r["p0"]), float(r["q"])) for r in csv.DictReader(f)
                             if r["series"] == series])
    with (folder / "fig8_7_thresholds.csv").open() as f:
        threshold = np.array([(float(r["q"]), float(r["beta"])) for r in csv.DictReader(f)
                              if r["series"] == series])
    peak = response[np.argmax(response[:, 1])]
    index = np.argmin(np.diff(threshold[:, 1]) / np.diff(threshold[:, 0]))
    bounds = threshold[index:index + 2, 0]
    assert len(response) == 16
    assert peak == pytest.approx((pressure, flow))
    assert bounds == pytest.approx(segment)
    assert bounds.mean() == pytest.approx(midpoint)
    assert abs(peak[0] - bounds.mean()) == pytest.approx(0.015)
    # Nominal CSV-coordinate arithmetic only; cross-figure normalization is unestablished.
    assert abs(peak[1] - bounds.mean()) == pytest.approx(q_gap)
    assert response[-1, 1] == final
    result = gate()[series]
    assert result["peak_p0"] == pressure
    assert result["peak_q"] == flow
    assert result["steepest_segment_q"] == segment
    assert result["steepest_segment_q_midpoint"] == pytest.approx(midpoint)


def test_retained_turnover_allows_beta2_tail_rebound_without_solver(monkeypatch):
    from puckworks.models.fasano2000_partI import fines_migration

    def no_solver(*args, **kwargs):
        pytest.fail("Source-figure gate must not execute the solver")

    monkeypatch.setattr(fines_migration, "simulate", no_solver)
    tail = [(r["p0"], r["q"]) for r in data.fasano_fig8_6()
            if r["series"] == "beta2" and r["p0"] >= 0.45]
    assert tail == [(0.45, 0.114), (0.50, 0.116), (0.55, 0.119), (0.60, 0.121)]
    result = gate()
    assert result["passed"] and result["beta2_peaks_below_beta1"]
    assert result["endpoint_drop_screen"] == 0.005
    for series in ("beta1", "beta2"):
        assert result[series]["sampled_turnover"]
        assert result[series]["threshold_nonincreasing"]
        assert result[series]["threshold_net_drop"]
        assert result[series]["n_samples"] == 16


@pytest.mark.parametrize("flows", [
    [0.1, 0.2, 0.3, 0.4],  # increasing: maximum at right endpoint
    [0.4, 0.3, 0.2, 0.1],  # decreasing: maximum at left endpoint
    [0.2, 0.2, 0.2, 0.2],  # constant: neither rise nor endpoint drop
])
def test_no_interior_turnover(monkeypatch, flows):
    rows = [dict(series=s, p0=p, q=q)
            for s in ("beta1", "beta2")
            for p, q in zip([0.0, 0.1, 0.2, 0.3], flows)]
    monkeypatch.setattr(data, "fasano_fig8_6", lambda: rows)
    result = gate()
    assert not result["passed"]
    assert all(not result[s]["sampled_turnover"] for s in ("beta1", "beta2"))


def test_pressure_axis_representation_invariance_exposes_old_predicate(monkeypatch):
    # An axis-representation test, not a new physical pressure scenario.
    original = gate()
    rows = [dict(r, p0=2 * r["p0"]) for r in data.fasano_fig8_6()]
    monkeypatch.setattr(data, "fasano_fig8_6", lambda: rows)
    scaled = gate()
    assert scaled["passed"] == original["passed"] is True
    assert scaled["beta2_peaks_below_beta1"] == original["beta2_peaks_below_beta1"] is True
    for series in ("beta1", "beta2"):
        before, after = original[series], scaled[series]
        assert after["peak_p0"] == 2 * before["peak_p0"]
        assert after["sampled_turnover"] == before["sampled_turnover"] is True
        assert after["peak_q"] == before["peak_q"]
        assert after["steepest_segment_q"] == before["steepest_segment_q"]
        midpoint = before["steepest_segment_q_midpoint"]
        assert abs(before["peak_p0"] - midpoint) < 0.05
        assert not abs(after["peak_p0"] - midpoint) < 0.05


def test_accidental_cross_observable_proximity_cannot_rescue_response(monkeypatch):
    rows = [dict(series=s, p0=start + i * 0.1, q=0.4 - i * 0.1)
            for s, start in (("beta1", 0.325), ("beta2", 0.225)) for i in range(4)]
    monkeypatch.setattr(data, "fasano_fig8_6", lambda: rows)
    result = gate()
    assert result["beta2_peaks_below_beta1"]
    assert not result["passed"]
    assert result["cross_figure_relation"] == "unassessed"
    for s in ("beta1", "beta2"):
        assert result[s]["peak_p0"] == pytest.approx(result[s]["steepest_segment_q_midpoint"])
        assert not result[s]["sampled_turnover"]
        assert "tracks" not in result[s]


@pytest.mark.parametrize("drop,passed", [(0.004, False), (0.006, True)])
def test_inherited_endpoint_drop_screen(monkeypatch, drop, passed):
    rows = data.fasano_fig8_6()
    for row in rows:
        if row["series"] == "beta1" and row["p0"] == 0.6:
            row["q"] = 0.235 - drop
    monkeypatch.setattr(data, "fasano_fig8_6", lambda: rows)
    assert gate()["passed"] is passed


def test_threshold_nonincrease_checks_every_interval(monkeypatch):
    rows = data.fasano_fig8_7()
    for row in rows:
        if row["series"] == "beta1" and row["q"] == 0.10:
            row["beta"] = 0.99  # interior rise; endpoints still decrease
    monkeypatch.setattr(data, "fasano_fig8_7", lambda: rows)
    result = gate()
    assert result["beta1"]["threshold_net_drop"]
    assert not result["beta1"]["threshold_nonincreasing"]
    assert not result["passed"]


def test_peak_pressure_ordering_is_executable(monkeypatch):
    rows = [dict(r, p0=2 * r["p0"] if r["series"] == "beta2" else r["p0"])
            for r in data.fasano_fig8_6()]
    monkeypatch.setattr(data, "fasano_fig8_6", lambda: rows)
    result = gate()
    assert all(result[s]["sampled_turnover"] for s in ("beta1", "beta2"))
    assert not result["beta2_peaks_below_beta1"]
    assert not result["passed"]


def test_current_result_and_evidence_keep_the_descriptive_ceiling():
    from puckworks.paper3 import evidence_graph as eg

    result = gate()
    assert result["cross_figure_relation"] == "unassessed"
    assert "descriptive source-figure check" in result["strength"]
    assert "does not verify Corollary 8.2" in result["note"]
    assert all("tracks" not in result[s] for s in ("beta1", "beta2"))
    link = next(x for x in eg.load_links() if x["gate"] == GATE)
    assert link["support_status"] == "context_only"
    assert link["reality_facing"] is False
    assert link["relationship"] == "not_empirical"
    assert link["evidence_strength"] == "sign_or_compatibility"
    assert link["component_evidence_strength"] == "qualitative_capacity"
    assert link["sources"][0]["evidence_role"] == "context"
    assert link["sources"][0]["dataset_manifest_ids"] == [
        "fasano2000_partI/fig8_6_model_q_inf", "fasano2000_partI/fig8_7_thresholds"]
    assert "sampled maximum strictly inside" in link["claim"]
    assert "nonincreasing on every interval" in link["claim"]
    assert "does not verify Corollary 8.2" in link["claim_not_supported"]
    assert "without simulating reversal" in eg.CONSERVATIVE_SUMMARIES[COMPONENT]
    generated = json.loads((ROOT / "docs/paper3_resource/generated/evidence_graph.json").read_text())
    current = next(x for x in generated["links"] if x["gate"] == GATE)
    for field in ("claim", "observable", "caveat", "claim_not_supported", "relationship"):
        assert current[field] == link[field]
    with (ROOT / "docs/figures/paper3/source_data/fig2_evidence_vectors.csv").open() as f:
        vector = next(x for x in csv.DictReader(f) if x["gate"] == GATE)
    assert vector["scope"] == link["observable"]
    # Targeted checks of the demonstrated erroneous claims, not an all-gates phrase policy.
    for path, old in [
        ("puckworks/models/__init__.py", "peak-tracks-beta-knee"),
        ("puckworks/data/MANIFEST.csv", "peak tracks the Fig 8.7 beta knee"),
        ("puckworks/data/fasano2000_partI/PROVENANCE.md", "verifies exactly that cross-figure"),
        ("docs/cards/fasano2000_partI.md", "usable as a verification twin"),
    ]:
        assert old not in (ROOT / path).read_text()

"""The actual registered gate must detect the historical area interpolation fault."""
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks import registry
from puckworks.gate_runner import GateStatus, evaluate_gate
from puckworks.models.cameron2020 import extraction_bdf as cam
from puckworks.validation.gates import _cameron_solid_inventory

COMPONENT = "cameron2020.extraction_bdf"
GATE = "gate_cameron_conservation"
PANEL = [(1.9, 40, 24), (1.1, 20, 12), (2.1, 20, 12)]


def registered_gate():
    registry.load_builtin_components()
    matches = [gate for gate in registry.get(COMPONENT).gates
               if (getattr(gate, "gate_id", None) or gate.__name__) == GATE]
    assert len(matches) == 1
    return matches[0]


@pytest.fixture
def historical_interpolation():
    """Original area interpolation (713c3c22), reinstated in the current solver."""
    def microstructure(gs):
        phi1 = np.interp(gs, cam.GS_GRID, cam.PHI_S1_GRID)
        phi2 = np.interp(gs, cam.GS_GRID, cam.PHI_S2_GRID)
        a2 = np.interp(gs, cam.GS_GRID, cam.A2_GRID)
        bet1 = np.interp(gs, cam.GS_GRID, cam.BET1_GRID)
        bet2 = np.interp(gs, cam.GS_GRID, cam.BET2_GRID)
        return phi1, phi2, a2, bet1, bet2
    return microstructure


def registered_gate_roundtrip(monkeypatch, historical_interpolation):
    """Return actual typed receipts, also used to generate the compact result."""
    gate = registered_gate()
    original = cam.grind_microstructure

    def evaluate():
        result = evaluate_gate(COMPONENT, gate)
        payload = result.to_dict(include_runtime=False)
        assert json.loads(json.dumps(payload, allow_nan=False)) == payload
        assert result.component_id == COMPONENT
        assert result.gate_id == GATE
        assert [(c["GS"], c["N"], c["M"]) for c in result.metrics["cases"]] == PANEL
        for case in result.metrics["cases"]:
            assert type(case["passed"]) is bool
            assert all(type(value) is bool for value in case["checks"].values())
            assert case["passed"] is all(case["checks"].values())
        return result, payload

    corrected, corrected_payload = evaluate()
    assert corrected.status is GateStatus.PASS
    assert all(all(c["checks"].values()) for c in corrected.metrics["cases"])
    assert corrected.metrics["EY"] == round(corrected.metrics["cases"][0]["EY"], 2)
    assert corrected.metrics["EY_solid"] == round(corrected.metrics["cases"][0]["EY_solid"], 2)
    assert corrected.metrics["inventory_ceiling"] == round(
        corrected.metrics["cases"][0]["inventory_ceiling"], 1)

    with monkeypatch.context() as patch:
        patch.setattr(cam, "grind_microstructure", historical_interpolation)
        faulty, faulty_payload = evaluate()
        assert faulty.status is GateStatus.FAIL  # normal numerical FAIL, never ERROR
        control, *affected = faulty.metrics["cases"]
        assert control["passed"] is True
        for case in affected:
            assert case["checks"]["mass_budget"] is False
            assert case["abs_mass_residual_kg"] > case["mass_tolerance_kg"]
            assert case["mass_residual_kg"] < 0
            # Old EY screen would admit these, independently of its case-selection flaw.
            assert case["abs_ey_discrepancy_pp"] < 0.5
            assert case["checks"]["finite"] is True
        for case in faulty.metrics["cases"]:
            # Reviewable raw inventories, not a converted EY_solid discrepancy.
            assert case["mass_residual_kg"] == (
                case["initial_solute_mass_kg"] - case["final_solid_solute_mass_kg"]
                - case["retained_liquid_solute_mass_kg"] - case["cup_solute_mass_kg"])
    assert cam.grind_microstructure is original
    assert registered_gate() is gate
    restored, restored_payload = evaluate()
    assert restored.status is GateStatus.PASS
    assert all(all(c["checks"].values()) for c in restored.metrics["cases"])
    assert restored_payload == corrected_payload
    return dict(corrected=corrected_payload, historical_fault=faulty_payload,
                restored=restored_payload)


def test_registered_gate_positive_historical_fault_and_restoration(
        monkeypatch, historical_interpolation):
    registered_gate_roundtrip(monkeypatch, historical_interpolation)


@pytest.mark.parametrize("radius", [2.0, 5.0])
def test_independent_solid_reducer_unequal_shells(radius):
    # Three nodes: faces at 0, a/4, 3a/4, a. Shell fractions 1,26,37 / 64.
    # Axial mean field is (2,4,6); mean concentration is 328/64 = 5.125.
    field = np.array([[1., 2., 4.], [3., 6., 8.]])
    assert _cameron_solid_inventory(field, radius, 0.25, 8.0) == 10.25


def synthetic_state(gs, **kwargs):
    """Finite, exactly budgeted half-depleted state for predicate boundary tests."""
    n, m = kwargs["N"], kwargs["M"]
    initial = np.pi * cam.R0**2 * cam.bed_depth(kwargs["m_in"]) * cam.PHI_S * kwargs["c_s0"]
    cup = initial / 2
    ey = 100 * cup / kwargs["m_in"]
    return SimpleNamespace(
        cs1_final=np.full((n, m), kwargs["c_s0"] / 2),
        cs2_final=np.full((n, m), kwargs["c_s0"] / 2),
        cl_final=np.zeros(n), m_cup=np.array([cup]), EY=ey, EY_solid=ey, t_shot=30.0)


@pytest.mark.parametrize("diagnostic,tolerance,scale,expected", [
    ("mass", 2e-11, 0.999, True), ("mass", 2e-11, 1.001, False),
    ("ey", 1e-7, 0.999, True), ("ey", 1e-7, 1.001, False),
])
def test_absolute_budgets_without_relative_allowance(
        monkeypatch, diagnostic, tolerance, scale, expected):
    # Synthetic boundary controls are distinct from the actual-solver historical regression.
    def simulate(gs, **kwargs):
        state = synthetic_state(gs, **kwargs)
        if diagnostic == "mass":
            state.m_cup[-1] += tolerance * scale
        else:
            state.EY_solid -= tolerance * scale
        return state
    monkeypatch.setattr(cam, "simulate_shot", simulate)
    result = registered_gate()()
    assert result["passed"] is expected
    assert len(result["cases"]) == 3  # retain later cases even on failure
    check = "mass_budget" if diagnostic == "mass" else "ey_agreement"
    assert all(case["checks"][check] is expected for case in result["cases"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("field", ["cs1_final", "cs2_final", "cl_final"])
def test_final_concentration_checks(monkeypatch, field):
    def simulate(gs, **kwargs):
        state = synthetic_state(gs, **kwargs)
        getattr(state, field).flat[0] = -1.001e-8
        return state
    monkeypatch.setattr(cam, "simulate_shot", simulate)
    result = registered_gate()()
    assert result["passed"] is False
    assert all(c["checks"][field + "_nonnegative"] is False for c in result["cases"])


@pytest.mark.parametrize("boundary", ["zero", "ceiling"])
def test_strict_inventory_bounds(monkeypatch, boundary):
    def simulate(gs, **kwargs):
        state = synthetic_state(gs, **kwargs)
        state.EY = 0.0 if boundary == "zero" else 2 * state.EY
        state.EY_solid = state.EY
        return state
    monkeypatch.setattr(cam, "simulate_shot", simulate)
    result = registered_gate()()
    check = "ey_positive" if boundary == "zero" else "below_inventory_ceiling"
    assert result["passed"] is False
    assert all(c["checks"][check] is False for c in result["cases"])


@pytest.mark.parametrize("fault", ["nan", "inf", "shape"])
def test_invalid_state_uses_serializable_runner_error(monkeypatch, fault):
    def simulate(gs, **kwargs):
        state = synthetic_state(gs, **kwargs)
        if fault == "shape":
            state.cs1_final = state.cs1_final[0]
        else:
            state.cs1_final[0, 0] = float(fault)
        return state
    monkeypatch.setattr(cam, "simulate_shot", simulate)
    result = evaluate_gate(COMPONENT, registered_gate())
    assert result.status is GateStatus.ERROR
    assert result.exception_type == "ValueError"
    json.dumps(result.to_dict(), allow_nan=False)


def test_fig2_evidence_vector_projection_matches_live_producer():
    """Check the affected CSV without invoking unrelated figure calculations."""
    import csv
    from pathlib import Path
    from puckworks.paper3.evidence_graph import evidence_vectors

    path = (Path(__file__).resolve().parents[1] /
            "docs/figures/paper3/source_data/fig2_evidence_vectors.csv")
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.reader(stream))
    assert rows[0] == ["component", "relation", "scope", "gate", "outcome"]
    assert rows[1:] == [[name, item.relation, item.scope, item.gate, item.outcome]
                        for name, vector in sorted(evidence_vectors().items())
                        for item in vector]

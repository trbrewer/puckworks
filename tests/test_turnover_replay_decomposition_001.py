"""No-simulation controls for frozen linear observation decomposition."""
import ast
import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import turnover_replay_decomposition_001 as D


def test_observation_function_and_helper_source_are_unchanged():
    freeze = D.read_json(D.OUT / "INPUT_MANIFEST.json")
    assert D.observer_source_hash(D.__file__) == freeze["beverage_observer_source_sha256"]
    for path, expected in freeze["repository_inputs"].items():
        D.checked_hash(D.ROOT / path, expected)


def test_authentication_rejects_modified_bytes_before_loading(tmp_path):
    path = tmp_path / "retained.npz"
    np.savez(path, time=np.arange(50.), liquid_g=np.arange(50.), solute_g=np.arange(50.), beverage_g=2*np.arange(50.))
    digest = D.O.digest(path)
    assert D.load_arrays(path, digest)["time"].shape == (50,)
    with path.open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="authentication"):
        D.load_arrays(path, digest)


def test_missing_separate_component_stops_without_subtraction_or_simulation(tmp_path):
    path = tmp_path / "missing.npz"
    np.savez(path, time=np.arange(50.), liquid_g=np.arange(50.), beverage_g=2*np.arange(50.))
    with pytest.raises(ValueError, match="Missing retained signals.*solute_g"):
        D.load_arrays(path, D.O.digest(path))


def test_mass_observer_is_linear_on_fixed_native_support():
    fine = np.arange(0., 111., .005)
    native = np.arange(0., 109., .093)
    liquid, solute = 2*fine + .01*fine**2, .1*fine - .0003*fine**2
    flows = D.component_flows(dict(time=fine, liquid_g=liquid, solute_g=solute, beverage_g=liquid+solute), native)
    for center in (10., 20., 40., 60., 100.):
        values = {key: D.O.paired_window(native, np.full(len(native), 13.), q, center)[1] for key, q in flows.items()}
        # The quadratic is linearly interpolated between non-aligned fine/native nodes.
        assert values["liquid"] == pytest.approx(2+.02*center, abs=2e-8)
        assert values["solute"] == pytest.approx(.1-.0006*center, abs=2e-8)
        D.close(values["liquid"]+values["solute"], values["total"], "synthetic windows")
    # The late solute *flow change* is negative despite increasing cumulative mass.
    assert .1-.0006*100 < .1-.0006*60


def test_full_filter_support_required_and_masks_not_observations():
    with pytest.raises(ValueError, match="support"):
        D.beverage_observer(dict(time=np.arange(101.), beverage_g=np.arange(101.)), np.arange(110.))
    native = np.arange(110.)
    valid = np.ones(110, dtype=bool)
    valid[101] = False
    assert D.O.paired_window(native, native, native, 100., valid=valid)[2] == "masked_or_nonfinite_support"


def test_reconstruction_failure_stops_instead_of_accepting_a_mismatch():
    with pytest.raises(AssertionError):
        D.close(1.01, 1., "bad reconstruction")
    with pytest.raises(ValueError, match="nonfinite"):
        D.close(np.nan, 1., "missing reconstruction")


def test_shared_bank_identity_and_paired_late_changes():
    freeze = D.read_json(D.OUT / "INPUT_MANIFEST.json")
    # Nominal membership is frozen by the inherited source cohort, not inferred from model outputs.
    nominal_by_prefix = {"1": 1., "2": 2., "3-5": 3.5, "4": 4., "5": 5., "6": 6.,
                         "7": 7., "8": 8., "9": 9., "10": 11., "12": 13.}
    condition = np.array([nominal_by_prefix["3-5" if b.startswith("3-5-") else b.split("-")[0]]
                          for b in freeze["brew_order"]])
    bank = D.O.draw_bank(condition)
    assert D.O.bank_digest(bank) == freeze["draw_bank_sha256"]
    before = np.arange(56.)/10
    q = np.stack([before, before+.123])
    p = np.tile(condition, (2, 1))
    _, means, _, draws, _ = D.O.condition_statistics(p, q, condition, bank)
    np.testing.assert_allclose(means[1]-means[0], .123, atol=1e-14)
    np.testing.assert_allclose(draws[1]-draws[0], .123, atol=1e-14)
    interval = D.O.interval(draws[1, :, -1]-draws[0, :, -1])
    np.testing.assert_allclose(interval, [.123, .123])


def test_decompose_uses_observed_centers_and_checks_every_window(tmp_path):
    native = np.arange(0., 121., .1)
    arrays = dict(time=native, liquid_g=2*native, solute_g=.1*native, beverage_g=2.1*native)
    (tmp_path / "predictions").mkdir()
    path = tmp_path / "predictions/saved.npz"
    np.savez(path, **arrays)
    record = dict(model="A-J1", scope="LOCO", brew="synthetic", artifact=path.name, sha256=D.O.digest(path))
    observed, windows = {}, {}
    for clock, target in D.O.SNAPSHOTS:
        center = target + (7. if clock == "onset" else 0.)
        obs = dict(available="True", reason="available", pressure_bar="13", flow_g_s="3",
                   window_start_stable_s=str(center-1), window_end_stable_s=str(center+1), onset_stable_s="7")
        observed["synthetic", clock, target] = obs
        windows["A-J1", "LOCO", "synthetic", clock, target] = dict(obs, observed_onset_stable_s="7",
            achieved_pressure_bar="13", nominal_pressure_bar="13", predicted_beverage_flow_g_s="2.1")
    data = dict(records=[record], native={"synthetic": (native, np.full(len(native), 13.), np.full(len(native), 3.), 7., 0.)},
                observed=observed, windows=windows)
    rows, audit = D.decompose(SimpleNamespace(retained=tmp_path), data)
    assert len(rows) == audit["windows"] == 10
    assert [r["window_start_stable_s"] for r in rows if r["clock"] == "onset"] == [16., 26., 36., 46.]
    windows["A-J1", "LOCO", "synthetic", "stable_pressure", 100]["predicted_beverage_flow_g_s"] = "2.2"
    with pytest.raises(AssertionError, match="component window sum"):
        D.decompose(SimpleNamespace(retained=tmp_path), data)


def test_runner_has_no_simulation_or_fitting_imports():
    tree = ast.parse(Path(D.__file__).read_text())
    imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    forbidden = ("joint_clock", "wetting_screen", "turnover_time_replay_001", "optimize")
    for node in imports:
        names = [getattr(node, "module", "") or "", *(a.name for a in node.names)]
        assert not any(part in name for name in names for part in forbidden)


def test_frozen_bank_has_every_model_scope_brew_once():
    freeze = json.loads((D.OUT / "INPUT_MANIFEST.json").read_text())
    keys = [(r["model"], r["scope"], r["brew"]) for r in freeze["arrays"]]
    assert len(keys) == len(set(keys)) == 224
    assert set(keys) == {(m, s, b) for m in D.MODELS for s in D.SCOPES for b in freeze["brew_order"]}


def test_committed_reconstruction_receipt_and_outputs():
    receipt = D.read_json(D.OUT / "RUN_RECEIPT.json")
    assert receipt["arrays"] == 224 and receipt["windows"] == 2240
    assert receipt["fits"] == receipt["simulations"] == 0
    D.checked_hash(D.__file__, receipt["code_sha256"])
    D.checked_hash(D.O.__file__, receipt["observer_sha256"])
    for name, expected in receipt["outputs"].items():
        D.checked_hash(D.OUT / name, expected)
    for filename, suffix, expected_rows in (("CONTRIBUTIONS_BY_TIME.csv", "flow_g_s", 440),
        ("PHASE_CONTRIBUTIONS.csv", "change_g_s", 36), ("SLOPE_CONTRIBUTIONS.csv", "slope_g_s_bar", 40)):
        rows = D.read_csv(D.OUT / filename)
        assert len(rows) == expected_rows
        for row in rows:
            D.close(float(row["liquid_"+suffix])+float(row["solute_"+suffix]), float(row["total_"+suffix]), filename)
            if filename == "PHASE_CONTRIBUTIONS.csv" and row["end_time_s"] == "100":
                assert all(int(row[name+"_change_g_s_finite_draws"]) == 1000 for name in (*D.COMPONENTS, "observed"))

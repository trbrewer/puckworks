"""Synthetic exclusion/provenance tests; private source records are never required."""
from dataclasses import replace
import csv
import json
import pickle
import sys

import numpy as np
import pytest

from puckworks.analysis import vis_predictor_001 as shared
from puckworks.analysis import vis_predictor_002 as rerun
from puckworks.empirical.visualizer import Shot, extract_windows, fitted_model, load_model


def shot(key, user, fold, reset=False):
    t = np.arange(0, 25.01, .25)
    windows, flags, reason = extract_windows(t, np.full(len(t), 5e5), (t+2)/1000)
    assert reason == "retained"
    flags["reset_like"] = reset
    return Shot(key, user, windows, flags, fold)


def test_filter_preserves_objects_original_folds_and_other_flags(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Fold generator called")
    monkeypatch.setattr(shared, "grouped_folds", forbidden)
    original = [shot("a", "u1", 4), shot("b", "u2", 2, True), shot("c", "u3", 0)]
    original[0].flags["negative_increment"] = True
    original[0].flags["clipping_like"] = True
    before = rerun.shot_bytes_digest([original[0], original[2]])
    retained = rerun.unflagged_shots(original)
    assert retained[0] is original[0] and retained[1] is original[2]
    assert [s.fold for s in retained] == [4, 0]
    assert rerun.shot_bytes_digest(retained) == before
    assert retained[0].flags["negative_increment"] and retained[0].flags["clipping_like"]


@pytest.mark.parametrize("phase", ["check-c0", "fit", "deploy", "audit", "audit-deployment", "score", "report"])
def test_flagged_shot_stops_every_consuming_phase(tmp_path, monkeypatch, phase):
    output, private, parent = (tmp_path / n for n in ("output", "private", "parent"))
    private.mkdir()
    bad = [shot("flagged", "u", 0, True)]
    (private / "windows.pkl").write_bytes(pickle.dumps(bad, protocol=5))
    manifest = dict(task_id=rerun.TASK, base_sha=rerun.BASE,
                    survivor_object_sha256=rerun.shot_bytes_digest(bad))
    monkeypatch.setattr(rerun, "verify_parent", lambda *a: None)
    monkeypatch.setattr(shared, "verify_freeze", lambda *a: manifest)
    def forbidden(*args, **kwargs):
        raise AssertionError("Flagged shot reached fitting/calibration/scoring")
    monkeypatch.setattr(shared, "fit_models", forbidden)
    monkeypatch.setattr(shared, "score", forbidden)
    monkeypatch.setattr(shared, "report", forbidden)
    monkeypatch.setattr(rerun, "check_c0", forbidden)
    monkeypatch.setattr(sys, "argv", ["runner", phase, "--private", str(private),
                                     "--parent-private", str(parent), "--output", str(output)])
    with pytest.raises(RuntimeError, match="only stored unflagged"):
        rerun.main()


def test_public_and_private_parent_paths_are_read_only(tmp_path):
    parent = tmp_path / "001-private"
    private = tmp_path / "002-private"
    for output, destination in ((rerun.PARENT, private), (rerun.PARENT / "child", private),
                                (rerun.OUT, parent), (rerun.OUT, parent / "child")):
        with pytest.raises(ValueError, match="overlaps read-only"):
            rerun.validate_locations(output, destination, parent)
    link = tmp_path / "parent-link"
    parent.mkdir()
    link.symlink_to(parent, target_is_directory=True)
    with pytest.raises(ValueError, match="overlaps read-only"):
        rerun.validate_locations(rerun.OUT, link, parent)
    assert rerun.validate_locations(rerun.OUT, private, parent)[0] == rerun.OUT


def test_001_model_cannot_satisfy_002_skip_check(tmp_path):
    parent = load_model(rerun.PARENT / "models/fold_0/T0.json")
    (tmp_path / "PLAN.md").write_text("002 post-hoc correction")
    (tmp_path / "STARTS.json").write_bytes((rerun.PARENT / "STARTS.json").read_bytes())
    manifest = dict(task_id=rerun.TASK, corpus_fold_sha256="002-cohort", windows_sha256="002-windows")
    contract = shared.resume_contract(manifest, "0", tmp_path)
    assert not shared.resume_matches(parent, "T0", contract)
    assert not shared.resume_matches(None, "T0", contract)
    model = fitted_model("T0", {"Tc": 2}, {"resume_contract": contract})
    assert shared.resume_matches(model, "T0", contract)
    for key in ("task_id", "fold", "corpus_fold_sha256", "windows_sha256", "plan_sha256",
                "starts_sha256", "evaluator_sha256", "settings", "integration", "runtime"):
        changed = dict(contract, **{key: "foreign"})
        assert not shared.resume_matches(model, "T0", changed)


def test_c0_reproduction_uses_early_only_and_parent_lookup(monkeypatch):
    s = shot("survivor", "u", 4)
    windows = s.windows[:3] + [w for w in s.windows if w.role == "score"][:3]
    s.windows = [replace(w, flow_g_s=q) for w, q in zip(windows, [1, 2, 3, 5, 2, 1])]
    excluded = shot("excluded", "v", 1, True)
    parent = [excluded, s]
    cache = dict(prediction={"C0": [np.full(len(excluded.windows), 999), np.full(6, 2.)]})
    expected_rmse = np.sqrt(10/3)
    expected_nrmse = expected_rmse / np.sqrt(14/3)
    monkeypatch.setattr(rerun, "C0_REFERENCE", dict(rmse_g_s=expected_rmse, nrmse=expected_nrmse))
    result = rerun.c0_reproduction([s], parent, cache)
    assert result["passed"] and result["maximum_parent_prediction_difference"] == 0
    cache["prediction"]["C0"][1] += .1
    assert not rerun.c0_reproduction([s], parent, cache)["passed"]


def test_committed_c0_reference_and_release_cells():
    with (rerun.PARENT / "BREAKDOWNS.csv").open() as f:
        original = next(r for r in csv.DictReader(f) if r["diagnostic"] == "reset_like"
                        and r["group"] == "False" and r["model"] == "C0")
    for metric, expected in rerun.C0_REFERENCE.items():
        assert abs(float(original[metric])-expected) <= rerun.C0_ATOL
    receipt = rerun.OUT / "C0_REPRODUCTION.json"
    if receipt.exists():
        result = json.loads(receipt.read_text())
        assert result["passed"]
        for metric, expected in rerun.C0_REFERENCE.items():
            assert abs(result[metric]-expected) <= rerun.C0_ATOL
    for path in rerun.OUT.glob("*.csv"):
        for row in csv.DictReader(path.open()):
            assert not {"key", "user", "hashed_user", "id", "content_sha256"} & row.keys()
            if row.get("shots"):
                assert int(row["shots"]) >= 20 and int(row["users"]) >= 10
    for path in (rerun.OUT / "models").glob("*/*.json"):
        model = load_model(path)
        assert model["metadata"]["resume_contract"]["task_id"] == rerun.TASK


def test_report_rejects_parent_or_stale_prediction_cache(tmp_path, monkeypatch):
    output, private = tmp_path / "out", tmp_path / "private"
    output.mkdir()
    private.mkdir()
    (output / "FROZEN_MANIFEST.json").write_text(json.dumps(dict(task_id=rerun.TASK)))
    (private / "windows.pkl").write_bytes(pickle.dumps([shot("s", "u", 0)]))
    monkeypatch.setattr(shared, "prediction_provenance", lambda out: {"cohort": "002"})
    for cache in ({"prediction": {}}, {"provenance": {"cohort": "001"}}):
        (private / "predictions.pkl").write_bytes(pickle.dumps(cache))
        with pytest.raises(RuntimeError, match="Foreign/stale 002 prediction cache"):
            shared.report(private, output, rerun.CONTRASTS)
    assert not (output / "SCORES.csv").exists()


def test_empty_audit_cannot_authorize_scoring(tmp_path):
    (tmp_path / "quadrature.json").write_text(json.dumps(dict(passed=True, rows=[])))
    with pytest.raises(RuntimeError, match="Incomplete/foreign"):
        rerun.require_audit(tmp_path, tmp_path, {})

"""Legacy resume compatibility, using copies of committed models and synthetic shots."""
import json
import pickle
import shutil
import sys

import numpy as np
import pytest

from puckworks.analysis import vis_predictor_001 as runner
from puckworks.empirical.visualizer import Shot, extract_windows, load_model, save_model


@pytest.fixture
def legacy_artifacts(tmp_path, monkeypatch):
    output, private = tmp_path / "VIS_PREDICTOR_001", tmp_path / "private"
    output.mkdir()
    private.mkdir()
    for name in ("PLAN.md", "STARTS.json", "FROZEN_MANIFEST.json"):
        shutil.copy2(runner.OUT / name, output / name)
    shutil.copytree(runner.OUT / "models", output / "models")
    t = np.arange(0, 25.01, .25)
    windows, flags, reason = extract_windows(t, np.full(len(t), 5e5), (t+2)/1000)
    assert reason == "retained"
    shots = [Shot(str(f), str(f), windows, flags, f) for f in range(5)]
    (private / "windows.pkl").write_bytes(pickle.dumps(shots, protocol=5))
    manifest = json.loads((output / "FROZEN_MANIFEST.json").read_text())
    # Substitute only the private corpus/freeze; authenticate real model bytes.
    monkeypatch.setattr(runner, "verify_freeze", lambda *args: manifest)
    monkeypatch.setattr(runner, "_FIT_DESIGN", None)

    def forbidden(*args, **kwargs):
        raise AssertionError("Legacy resume attempted optimization or a model write")

    monkeypatch.setattr(runner, "ProcessPoolExecutor", forbidden)
    monkeypatch.setattr(runner, "fit_start", forbidden)
    monkeypatch.setattr(runner, "save_model", forbidden)
    return output, private


def test_001_fit_and_deployment_resume_preserve_all_committed_model_hashes(legacy_artifacts, monkeypatch):
    output, private = legacy_artifacts
    models = output / "models"
    before = {p.relative_to(models): runner.sha(p) for p in models.rglob("*") if p.is_file()}
    expected_models = set(models.glob("*/*.json"))
    assert len(expected_models) == 48 and len(before) == 96
    authenticated = set()

    def authenticate(path):
        saved = load_model(path)
        assert "resume_contract" not in saved["metadata"]
        authenticated.add(path)
        return saved

    monkeypatch.setattr(runner, "load_model", authenticate)
    for fold in [*range(5), "all"]:
        args = ["runner", "deploy" if fold == "all" else "fit",
                "--private", str(private), "--output", str(output)]
        if fold != "all":
            args += ["--fold", str(fold)]
        monkeypatch.setattr(sys, "argv", args)
        runner.main()
    assert authenticated == expected_models  # Includes all six analytical C0 files.
    after = {p.relative_to(models): runner.sha(p) for p in models.rglob("*") if p.is_file()}
    assert after == before


@pytest.mark.parametrize("model", ["C0", "M0R"])
def test_001_resume_still_rejects_unauthenticated_artifacts(legacy_artifacts, model):
    output, private = legacy_artifacts
    path = output / "models/fold_0" / (model + ".json")
    path.write_bytes(path.read_bytes() + b"\n")  # Detached hash deliberately unchanged.
    with pytest.raises(ValueError, match="Model hash mismatch"):
        runner.fit_models(private, "0", 1, output)


def test_001_resume_preserves_pinned_pressure_integration_guard(legacy_artifacts):
    output, private = legacy_artifacts
    path = output / "models/fold_0/M0R.json"
    saved = load_model(path)
    saved["integration"]["max_pressure_step_bar"] = .2
    save_model(path, saved)  # Authenticated but incompatible copy; no fitting.
    with pytest.raises(RuntimeError, match="Cached pressure model uses different integration"):
        runner.fit_models(private, "0", 1, output)

"""Recomputed hash API + artifact replay verification (PV-19B Phase 6, #70).

Offline + deterministic. Guards that the public hash functions ALWAYS recompute (never return the
embedded claim under a computing name), that BuildProvenance is format-validated, that verify_artifact
keeps self-consistency (integrity) separate from producer reproduction (replay) and reports build
identity as 'not_verified' rather than guessing, and that the batch publishes atomically.
"""
import importlib
import json

import pytest

from puckworks.product import lab


@pytest.fixture(scope="module")
def report():
    ex = lab.execute_scenario(lab.ScenarioRequest("guided_v1", overrides={"dose_g": 19.0}))
    return lab.build_comparison(ex, provenance=lab.BuildProvenance(
        package_version="0.4.0.dev0", source_commit="a" * 40, workflow_run_id="7", wheel_sha256="b" * 64))


# ── recomputed hash API ─────────────────────────────────────────────────────────────
def test_public_hashes_always_recompute(report):
    tampered = json.loads(lab.artifact_json(report))
    tampered["integrity"]["scientific_payload_sha256"] = "0" * 64   # a bogus embedded claim
    # the public function ignores the embedded claim and recomputes from content
    assert lab.scientific_sha256(tampered) == lab.compute_scientific_result_sha256(tampered)
    assert lab.scientific_sha256(tampered) != "0" * 64
    # the embedded accessor returns the (bogus) stored claim, clearly separate
    assert lab.embedded_scientific_sha256(tampered) == "0" * 64


def test_embedded_accessors_read_the_stored_claim(report):
    assert lab.embedded_scientific_sha256(report) == report["integrity"]["scientific_payload_sha256"]
    assert lab.embedded_capability_sha256(report) == report["integrity"]["capability_snapshot_sha256"]
    assert lab.embedded_artifact_sha256(report) == report["integrity"]["artifact_sha256"]


# ── BuildProvenance validation ──────────────────────────────────────────────────────
def test_build_provenance_validates_formats():
    with pytest.raises(ValueError):
        lab.BuildProvenance(source_commit="xyz")             # not hex/too short
    with pytest.raises(ValueError):
        lab.BuildProvenance(wheel_sha256="abc123")           # not 64 hex
    with pytest.raises(ValueError):
        lab.BuildProvenance(workflow_run_id="not-a-number")
    # None is a visible gap, not an error
    p = lab.BuildProvenance()
    assert p.source_commit is None and p.wheel_sha256 is None
    ok = lab.BuildProvenance(source_commit="deadbeef", wheel_sha256="c" * 64, workflow_run_id="42",
                             package_version="0.4.0.dev0")
    assert ok.source_commit == "deadbeef"


# ── verify_artifact: four independent levels ────────────────────────────────────────
def test_clean_artifact_verifies_at_all_levels(report):
    r = json.loads(lab.artifact_json(report))
    v = lab.verify_artifact(r, replay=True, installed_version="0.4.0.dev0", wheel_sha256="b" * 64)
    assert v["ok"] is True
    assert v["schema"]["ok"] and v["integrity"]["ok"]
    assert v["producer_replay"]["performed"] and v["producer_replay"]["reproduced"] is True
    assert v["build_identity"]["package_version"] == "match"
    assert v["build_identity"]["wheel_sha256"] == "match"


def test_build_identity_is_not_verified_without_inputs(report):
    v = lab.verify_artifact(json.loads(lab.artifact_json(report)))
    assert v["build_identity"]["package_version"] == "not_verified"
    assert v["build_identity"]["wheel_sha256"] == "not_verified"
    assert v["producer_replay"]["performed"] is False       # replay is opt-in


def test_integrity_and_replay_are_independent_axes(report):
    # tamper the DISPLAY echo (scenario) but not the stored hash: integrity fails, producer still repros
    r = json.loads(lab.artifact_json(report))
    r["scenario"]["title"] = "TAMPERED"
    v = lab.verify_artifact(r, replay=True)
    assert v["integrity"]["ok"] is False                    # self-consistency broken
    assert v["ok"] is False
    # a self-consistent artifact is not automatically producer-reproduced, and vice versa — separate keys
    assert "integrity" in v and "producer_replay" in v


def test_replay_detects_a_scientific_mismatch_with_a_diff_path(report):
    r = json.loads(lab.artifact_json(report))
    # change the applied override so the reconstructed request reruns a DIFFERENT science
    r["scenario"]["applied_overrides"]["dose_g"]["effective"] = 21.0
    r["request"] = dict(r["request"])
    v = lab.verify_artifact(r, replay=True)
    assert v["producer_replay"]["reproduced"] is False
    assert v["producer_replay"]["first_diff"]               # a concrete differing path is reported


def test_reconstruct_request_roundtrips(report):
    req = lab.reconstruct_request(json.loads(lab.artifact_json(report)))
    assert req.preset_id == "guided_v1" and req.overrides["dose_g"] == 19.0


# ── atomic batch output ─────────────────────────────────────────────────────────────
def test_batch_publishes_atomically_and_records_the_full_manifest(tmp_path):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    final = tmp_path / "out"
    lb.run({"LAB_OUT_DIR": str(final), "LAB_PRESET": "guided_v1",
            "GITHUB_SHA": "e" * 40, "GITHUB_RUN_ID": "9", "LAB_WHEEL_SHA256": "f" * 64})
    assert final.exists() and not (tmp_path / "out.staging").exists()   # staging renamed away
    manifest = json.loads((final / "artifact_manifest.json").read_text())
    for k in ("scientific_payload_sha256", "capability_snapshot_sha256", "artifact_sha256",
              "domain_policy", "lens_selection_policy", "reference_selection_policy",
              "replay_verification"):
        assert k in manifest
    assert manifest["replay_verification"]["schema_ok"] and manifest["replay_verification"]["integrity_ok"]


def test_batch_leaves_no_partial_final_dir_on_failure(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    lb = importlib.import_module("tools.lab_batch")
    monkeypatch.setattr(lb.lab, "render_data", lambda report: [])    # forces the required-figure failure
    final = tmp_path / "out"
    with pytest.raises(RuntimeError):
        lb.run({"LAB_OUT_DIR": str(final)})
    assert not final.exists()                                # no partially valid final directory

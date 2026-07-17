"""Sanctioned-export publication-readiness: strict manifest profiles + fail-closed freeze gate.

Synthetic only — no live API request occurs here or in CI.
"""
from __future__ import annotations

import json

import pytest

from puckworks.data import corpus_freeze
from puckworks.data.corpus_export import (
    ExportManifestError,
    import_sanctioned_export,
    synthetic_export,
    validate_export_manifest,
)


def _pub_manifest():
    _, man = synthetic_export()
    return man


# ---- validator profiles -----------------------------------------------------

def test_rehearsal_profile_minimal():
    out = validate_export_manifest({"export_cutoff": 1000}, profile="rehearsal")
    assert out["publication_qualified"] is False and out["classification"] == "rehearsal-source"


def test_publication_profile_complete():
    out = validate_export_manifest(_pub_manifest(), profile="publication")
    assert out["publication_qualified"] is True


@pytest.mark.parametrize("mutate", [
    lambda m: m.pop("rights_basis"),
    lambda m: m.pop("aggregate_publication_status"),
    lambda m: m.pop("archive_or_export_sha256"),
    lambda m: m.update(archive_or_export_sha256="notahash"),
    lambda m: m.update(export_cutoff=None),
    lambda m: m.update(aggregate_publication_status="prohibited"),
    lambda m: m.update(raw_redistribution_status="whatever"),
    lambda m: m.pop("user_linkage_semantics"),
    lambda m: m.pop("retention_policy"),
    lambda m: m.pop("contact_record"),
])
def test_publication_profile_fails_closed(mutate):
    m = _pub_manifest()
    mutate(m)
    with pytest.raises(ExportManifestError):
        validate_export_manifest(m, profile="publication")


def test_record_count_consistency():
    m = _pub_manifest()
    m["record_count"] = 999
    with pytest.raises(ExportManifestError):
        validate_export_manifest(m, profile="publication", n_records=9)


def test_raw_prohibited_but_aggregate_permitted_is_valid():
    m = _pub_manifest()
    m["raw_redistribution_status"] = "prohibited"
    m["aggregate_publication_status"] = "permitted"
    assert validate_export_manifest(m, profile="publication")["publication_qualified"]


# ---- import + adversarial (synthetic) ---------------------------------------

def test_synthetic_import_handles_adversarial(tmp_path):
    recs, man = synthetic_export(cutoff=1000)
    summary = import_sanctioned_export(recs, man, tmp_path / "store", salt="t")
    assert summary["n_excluded_after_cutoff"] >= 1   # post-cutoff dropped
    assert summary["n_quarantined"] >= 1             # un-normalizable quarantined
    assert summary["export_cutoff"] == 1000
    assert (tmp_path / "store" / "source_export_manifest.json").exists()


def test_import_refuses_non_empty_destination(tmp_path):
    dst = tmp_path / "store"
    dst.mkdir()
    (dst / "x").write_text("occupied")
    recs, man = synthetic_export()
    with pytest.raises(FileExistsError):
        import_sanctioned_export(recs, man, dst)


def test_deterministic_repeated_import(tmp_path):
    recs, man = synthetic_export()
    a = import_sanctioned_export(recs, man, tmp_path / "a", salt="t")
    b = import_sanctioned_export(recs, man, tmp_path / "b", salt="t")
    assert a == b


# ---- freeze gate fails closed on an incomplete manifest ---------------------

def _store(d, cutoff, complete):
    from puckworks.lib import visualizer_harvest as vh
    d.mkdir(parents=True, exist_ok=True)
    cfg = vh.HarvestConfig(out_dir=str(d), salt="t")
    recs = [vh.normalize_shot({"id": "A", "user_id": "u", "updated_at": 100, "timeframe": [0.0, 1.0],
                               "data": {"espresso_pressure": [6.0, 9.0]}}, cfg)]
    vh._write_shard(cfg, 0, recs)
    vh._append_index(cfg, [vh._index_row(r) for r in recs])
    man = _pub_manifest() if complete else {"export_cutoff": cutoff, "source": "min"}
    man["export_cutoff"] = cutoff
    man["record_count"] = 1
    (d / "source_export_manifest.json").write_text(json.dumps(man))


def test_freeze_not_publication_ready_with_incomplete_manifest(tmp_path):
    _store(tmp_path / "src", 1000, complete=False)
    cand = corpus_freeze.freeze_rehearse(tmp_path / "src")
    assert cand.has_export_cutoff is True
    assert cand.ready_for_publication is False
    assert any("publication profile" in b for b in cand.blockers)


def test_freeze_publication_ready_with_complete_manifest(tmp_path):
    _store(tmp_path / "src", 1000, complete=True)
    cand = corpus_freeze.freeze_rehearse(tmp_path / "src")
    assert cand.ready_for_publication is True

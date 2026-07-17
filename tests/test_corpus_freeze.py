"""WP1 / PR2 — the verified publication-freeze lifecycle (rehearse / materialize / verify).

No network: small synthetic stores. Proves the publication gate cannot be forced by a label,
the moving public window is rejected, materialization is immutable + non-overwriting, and
verification catches source or materialized-file mutation.
"""
import json

import pytest

from puckworks.lib import visualizer_harvest as vh
from puckworks.data import corpus_freeze as cf
from puckworks.data import visualizer_store as vs
from puckworks.analysis import corpus_bundle


def _rec(cfg, sid, u, p):
    return vh.normalize_shot({"id": sid, "user_id": "u", "updated_at": u,
                              "timeframe": [0.0, 1.0], "data": {"espresso_pressure": p}}, cfg)


def _store(d, versions, export_cutoff=None, shard=0):
    d.mkdir(parents=True, exist_ok=True)
    cfg = vh.HarvestConfig(out_dir=str(d), salt="t")
    recs = [_rec(cfg, sid, u, p) for (sid, u, p) in versions]
    vh._write_shard(cfg, shard, recs)
    vh._append_index(cfg, [vh._index_row(r) for r in recs])
    if export_cutoff is not None:
        # a publication-ready source carries a validated publication-profile governance manifest.
        # Mechanics-only real-export mock (not a real rights grant).
        from puckworks.data.corpus_export import _governance_record
        man = _governance_record(len(versions), export_cutoff, source_kind="real_export")
        man["source"] = "sanctioned-export-fixture"
        (d / "source_export_manifest.json").write_text(json.dumps(man))
    return cfg


def test_rehearse_rejects_moving_window(tmp_path):
    _store(tmp_path, [("A", 100, [6.0, 9.0])])          # no export manifest = moving feed
    cand = cf.freeze_rehearse(tmp_path)
    assert cand.has_export_cutoff is False
    assert cand.ready_for_publication is False
    assert any("export cutoff" in b for b in cand.blockers)


def test_rehearse_ready_on_coherent_export(tmp_path):
    _store(tmp_path, [("A", 100, [6.0, 9.0]), ("B", 50, [6.0, 6.0])], export_cutoff=1000)
    cand = cf.freeze_rehearse(tmp_path)
    assert cand.reconcile_ok is True and cand.has_export_cutoff is True
    assert cand.ready_for_publication is True, cand.blockers


def test_materialize_publication_refused_on_moving_window(tmp_path):
    _store(tmp_path, [("A", 100, [6.0, 9.0])])
    with pytest.raises(RuntimeError, match="NOT publication-ready"):
        cf.freeze_materialize(tmp_path, tmp_path / "snap", classification="publication-freeze")


def test_materialize_refuses_overwrite(tmp_path):
    src = tmp_path / "src"
    _store(src, [("A", 100, [6.0, 9.0])])
    dst = tmp_path / "snap"
    cf.freeze_materialize(src, dst, classification="current-state")
    with pytest.raises(FileExistsError):
        cf.freeze_materialize(src, dst, classification="current-state")


def test_full_publication_path_unlocks_bundle(tmp_path):
    src = tmp_path / "src"
    _store(src, [("A", 100, [6.0, 9.0, 9.0]), ("B", 50, [6.0, 6.0])], export_cutoff=1000)
    dst = tmp_path / "snap"
    man = cf.freeze_materialize(src, dst, classification="publication-freeze", name="pub")
    assert (dst / "canonical_records.jsonl.gz").exists()
    assert man["n_canonical_records"] == 2 and man["snapshot_id"]
    assert "EXPLORATORY" not in (dst / "DATA_CARD.md").read_text()

    receipt = cf.freeze_verify(dst, source_dir=src)
    assert receipt.verified is True and receipt.qualifies_for_publication is True

    # the VERIFIED receipt (not a label) unlocks a publication bundle
    snap = vs.CorpusSnapshot(src, name="pub", classification="current-state")
    bundle = corpus_bundle.build_bundle(snap, require_freeze=True, receipt=receipt)
    assert bundle["exploratory"] is False
    assert bundle["publication_receipt_sha256"] == receipt.receipt_sha256


def test_current_state_materialization_is_marked_exploratory(tmp_path):
    src = tmp_path / "src"
    _store(src, [("A", 100, [6.0, 9.0])])               # moving feed
    dst = tmp_path / "snap"
    cf.freeze_materialize(src, dst, classification="current-state")
    assert "EXPLORATORY — NOT A PUBLICATION SNAPSHOT" in (dst / "DATA_CARD.md").read_text()
    receipt = cf.freeze_verify(dst)
    assert receipt.verified is True                      # it IS a valid current-state snapshot
    assert receipt.qualifies_for_publication is False    # ...but NOT publication-qualified


def test_verify_detects_materialized_mutation(tmp_path):
    src = tmp_path / "src"
    _store(src, [("A", 100, [6.0, 9.0])], export_cutoff=1000)
    dst = tmp_path / "snap"
    cf.freeze_materialize(src, dst, classification="publication-freeze")
    (dst / "canonical_records.jsonl.gz").write_bytes(b"tampered")     # corrupt a frozen file
    receipt = cf.freeze_verify(dst)
    assert receipt.verified is False and receipt.qualifies_for_publication is False
    assert any("mutated" in p for p in receipt.problems)


def test_verify_detects_source_mutation(tmp_path):
    src = tmp_path / "src"
    _store(src, [("A", 100, [6.0, 9.0])], export_cutoff=1000)
    dst = tmp_path / "snap"
    cf.freeze_materialize(src, dst, classification="publication-freeze")
    _store(src, [("C", 200, [7.0, 7.0])], shard=1)                    # source mutates after freeze
    receipt = cf.freeze_verify(dst, source_dir=src)
    assert receipt.verified is False
    assert any("source has mutated" in p for p in receipt.problems)

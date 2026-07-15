"""Tests for the canonical visualizer corpus snapshot interface (WP0/PR1).

Builds small on-disk stores from synthetic normalized records (no network) and exercises
the deduplicated latest view, integrity diagnostics, deterministic manifest, the measurement
dictionary, and the ambiguous-flow pooling guard.
"""
import json

import pytest

from puckworks.lib import visualizer_harvest as vh
from puckworks.data import visualizer_store as vs


def _rec(cfg, sid, updated_at, pressure):
    return vh.normalize_shot({"id": sid, "user_id": "u", "updated_at": updated_at,
                              "timeframe": [0.0, 1.0],
                              "data": {"espresso_pressure": pressure}}, cfg)


def _build_store(tmp_path, records):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), salt="t")
    vh._write_shard(cfg, 0, records)
    vh._append_index(cfg, [vh._index_row(r) for r in records])
    return cfg


def test_measurement_dictionary_first_tranche_and_pooling_guard():
    d = vs.measurement_dictionary()
    for ch in ("time__s", "pressure__Pa", "pressure_goal__Pa",
               "mass_flow_from_scale__kg_per_s", "flow_reported__native",
               "flow_goal_reported__native", "weight__kg", "state_change"):
        assert ch in d
        assert d[ch]["quantity_kind"] and "commanded" in d[ch] and d[ch]["eligibility"]
    # commanded/achieved split is explicit
    assert d["pressure_goal__Pa"]["commanded"] is True
    assert d["pressure__Pa"]["commanded"] is False
    # ambiguous flow is NOT pooling-safe; resolved SI channels are
    assert vs.is_pooling_safe("pressure__Pa") is True
    assert vs.is_pooling_safe("mass_flow_from_scale__kg_per_s") is True
    assert vs.is_pooling_safe("flow_reported__native") is False       # P0.4 guardrail
    assert d["flow_reported__native"]["canonical_unit"] is None


def test_snapshot_latest_dedups_and_prefers_last_written_on_tie(tmp_path):
    cfg = tmp_path / "store"
    r1 = None
    c = vh.HarvestConfig(out_dir=str(cfg), salt="t")
    a1 = _rec(c, "A", 100, [1.0, 1.0])
    a2 = _rec(c, "A", 100, [9.0, 9.0])          # same timestamp, changed content
    b = _rec(c, "B", 50, [6.0, 6.0])
    _build_store(cfg, [a1, a2, b])
    snap = vs.CorpusSnapshot(cfg, name="t", classification="current-state")
    latest = {r["id"]: r for r in snap.latest()}
    assert set(latest) == {"A", "B"}                                  # one per id
    assert latest["A"]["hydraulic"]["pressure__Pa"][0] == pytest.approx(9.0e5)  # last-written
    # version history is still available separately
    assert sum(1 for _ in snap.iter_versions()) == 3


def test_snapshot_integrity_stats(tmp_path):
    cfg = tmp_path / "store"
    c = vh.HarvestConfig(out_dir=str(cfg), salt="t")
    recs = [_rec(c, "A", 100, [1.0, 1.0]),
            _rec(c, "A", 100, [9.0, 9.0]),      # same-second conflict (different content)
            _rec(c, "A", 200, [9.0, 9.0]),      # a later revision
            _rec(c, "B", 50, [6.0, 6.0])]
    _build_store(cfg, recs)
    st = vs.CorpusSnapshot(cfg).integrity_stats()
    assert st["n_logical_records"] == 2 and st["n_stored_versions"] == 4
    assert st["n_revisions"] == 1                 # only A has >1 distinct version
    assert st["n_same_timestamp_conflicts"] == 1  # A@100 has two distinct hashes
    assert st["n_missing_updated_at"] == 0


def test_snapshot_as_of_cutoff(tmp_path):
    cfg = tmp_path / "store"
    c = vh.HarvestConfig(out_dir=str(cfg), salt="t")
    _build_store(cfg, [_rec(c, "A", 100, [1.0, 1.0]), _rec(c, "A", 200, [9.0, 9.0])])
    # as_of before the edit -> the earlier version wins
    snap = vs.CorpusSnapshot(cfg, as_of=150)
    latest = {r["id"]: r for r in snap.latest()}
    assert latest["A"]["hydraulic"]["pressure__Pa"][0] == pytest.approx(1.0e5)
    assert snap.integrity_stats()["n_stored_versions"] == 1           # only the <=150 version


def test_snapshot_manifest_is_deterministic_and_complete(tmp_path):
    cfg = tmp_path / "store"
    c = vh.HarvestConfig(out_dir=str(cfg), salt="t")
    _build_store(cfg, [_rec(c, "A", 100, [1.0, 1.0]), _rec(c, "B", 50, [6.0, 6.0])])
    snap = vs.CorpusSnapshot(cfg, name="pilot", classification="exploratory-window")
    m1 = snap.manifest()
    m2 = snap.manifest()
    assert m1 == m2                                                   # deterministic
    assert m1["classification"] == "exploratory-window"
    assert m1["integrity"]["n_logical_records"] == 2
    assert m1["reconcile_ok"] is True and m1["manifest_sha256"]
    assert m1["shards"] and all(s["sha256"] for s in m1["shards"])
    assert m1["measurement_dictionary_channels"] == sorted(vs.MEASUREMENT_DICTIONARY)
    # freeze writes the same deterministic manifest to disk
    dst = tmp_path / "snap.json"
    frozen = vs.freeze_snapshot(cfg, "pilot", dst, classification="publication-freeze")
    on_disk = json.load(open(dst))
    assert on_disk == frozen and frozen["classification"] == "publication-freeze"


def test_qc_table_flat_columns(tmp_path):
    cfg = tmp_path / "store"
    c = vh.HarvestConfig(out_dir=str(cfg), salt="t")
    good = vh.normalize_shot({"id": "A", "user_id": "u", "updated_at": 1,
                              "timeframe": [0.0, 1.0, 2.0], "drink_tds": 9.0,
                              "data": {"espresso_pressure": [6.0, 9.0, 9.0],
                                       "espresso_pressure_goal": [6.0, 9.0, 9.0]}}, c)
    _build_store(cfg, [good])
    rows = list(vs.CorpusSnapshot(cfg).qc_table())
    assert len(rows) == 1
    row = rows[0]
    assert set(row) == set(vs.QC_COLUMNS)                 # exactly the declared columns
    assert row["id"] == "A" and row["n_samples"] == 3
    assert row["has_pressure"] is True and row["has_pressure_goal"] is True
    assert row["has_mass_flow"] is False and row["has_tds"] is True
    assert row["time_monotonic"] is True and row["n_impossible_flags"] == 0


def test_bad_classification_rejected(tmp_path):
    with pytest.raises(ValueError):
        vs.CorpusSnapshot(tmp_path, classification="totally-frozen")

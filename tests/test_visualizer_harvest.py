"""Offline tests for the visualizer.coffee harvester (ROADMAP 0.13).

NO network: everything runs against the committed synthetic fixtures in
tests/fixtures/visualizer/ (clearly fake ids). This module is NOT wired into
run_all_gates — the harvester is tooling, not a physics gate.
"""
import json
from pathlib import Path

import pytest

from puckworks.lib import visualizer_harvest as vh

FIX = Path(__file__).resolve().parent / "fixtures" / "visualizer"


def _load(name):
    with open(FIX / name, encoding="utf-8") as fh:
        return json.load(fh)


def _cfg(tmp_path=None):
    # a fixed salt keeps the hashes deterministic in tests (no DEV-salt warning)
    return vh.HarvestConfig(out_dir=(tmp_path or FIX), salt="unit-test-salt")


def test_normalize_splits_three_tiers_with_si_units():
    tidy = vh.normalize_shot(_load("decent_full.json"), _cfg())
    assert set(("hydraulic", "outcomes", "context")) <= set(tidy)
    hy, oc, ctx = tidy["hydraulic"], tidy["outcomes"], tidy["context"]
    # hydraulic converted to SI: 9 bar -> 9e5 Pa, 1.9 g/s -> 1.9e-3 kg/s,
    # 6 g -> 6e-3 kg, 90 degC -> 363.15 K
    assert hy["pressure__Pa"][2] == pytest.approx(9.0e5)
    assert hy["flow_weight__kg_per_s"][2] == pytest.approx(1.9e-3)
    assert hy["weight__kg"][4] == pytest.approx(6.0e-3)
    assert hy["temperature_basket__K"][0] == pytest.approx(363.15)
    # outcomes tier kept SEPARATE, percent -> fraction
    assert oc["tds__fraction"] == pytest.approx(0.094)
    assert oc["ey__fraction"] == pytest.approx(0.213)
    assert oc["sensory"]["flavor"] == 7
    # context tier: dose g -> kg
    assert ctx["dose__kg"] == pytest.approx(0.018)
    assert ctx["machine"] == "decent"
    # the units block records raw + si for every stored channel (rule 7)
    assert tidy["units"]["hydraulic"]["pressure__Pa"] == {"raw": "bar", "si": "Pa"}


def test_privacy_drop_removes_user_and_free_text():
    raw = _load("decent_full.json")
    tidy = vh.normalize_shot(raw, _cfg())
    blob = json.dumps(tidy)
    # none of the PII / free-text values survive anywhere in the record
    for banned in ("Not A Real Person", "Not A Real Barista", "FAKE-user-aaa",
                   "avatar", "SYNTHETIC"):
        assert banned not in blob
    for banned_key in vh._PRIVACY_DROP:
        assert banned_key not in tidy
    # only a salted one-way hash of the user id is kept
    assert tidy["hashed_user"] and len(tidy["hashed_user"]) == 16
    assert tidy["hashed_user"] != raw["user_id"]
    assert tidy["hashed_user"] == vh.hash_user(_cfg(), "FAKE-user-aaa")


def test_missing_outcomes_yield_nulls_and_flags_not_errors():
    tidy = vh.normalize_shot(_load("minimal_missing.json"), _cfg())  # must not raise
    assert tidy["outcomes"]["tds__fraction"] is None
    assert tidy["outcomes"]["ey__fraction"] is None
    assert tidy["machine"] is None
    assert tidy["n_samples"] == 0
    assert "missing:timeframe" in tidy["flags"]
    assert "missing:machine_source" in tidy["flags"]
    # no invented fields: hydraulic carries no series when data is empty
    assert "pressure__Pa" not in tidy["hydraulic"]


def test_machine_inference_from_brewdata():
    assert vh.normalize_shot(_load("decent_full.json"), _cfg())["machine"] == "decent"
    assert vh.normalize_shot(_load("meticulous_partial.json"), _cfg())["machine"] == "meticulous"


def test_flow_unit_ambiguity_is_flagged_not_coerced_silently():
    tidy = vh.normalize_shot(_load("decent_full.json"), _cfg())
    assert any(f.startswith("unit_ambiguous:espresso_flow") for f in tidy["flags"])


def test_zero_ey_is_treated_missing():
    # drink_ey == 0 in the meticulous fixture -> a missing outcome, not 0.0
    tidy = vh.normalize_shot(_load("meticulous_partial.json"), _cfg())
    assert tidy["outcomes"]["ey__fraction"] is None
    assert tidy["outcomes"]["tds__fraction"] == pytest.approx(0.081)


def test_store_roundtrip_index_and_stats(tmp_path):
    cfg = _cfg(tmp_path)
    recs = [vh.normalize_shot(_load(n), cfg) for n in
            ("decent_full.json", "meticulous_partial.json", "minimal_missing.json")]
    vh._write_shard(cfg, 0, recs)
    vh._append_index(cfg, [vh._index_row(r) for r in recs])
    # generator never loads all into memory; yields each stored record
    got = list(vh.iter_store(cfg))
    assert len(got) == 3
    ids = {r["id"] for r in got}
    assert "FAKE-decent-0001" in ids
    stats = vh.compute_stats(cfg)
    assert stats["total_shots"] == 3
    assert stats["machine_mix"].get("decent") == 1
    assert stats["pct_with_tds"] == pytest.approx(100 * 2 / 3, abs=0.1)  # decent+meticulous
    # the DERIVED aggregate CSV writes (metric,key,value) with no per-shot rows
    path = vh.write_aggregate_csv(cfg, stats)
    text = path.read_text()
    assert "total_shots" in text and "FAKE-decent-0001" not in text


def test_index_ids_dedup_helper(tmp_path):
    cfg = _cfg(tmp_path)
    recs = [vh.normalize_shot(_load("decent_full.json"), cfg)]
    vh._append_index(cfg, [vh._index_row(r) for r in recs])
    assert vh._read_index_ids(cfg) == {"FAKE-decent-0001"}


def test_default_dev_salt_warns():
    import warnings
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        vh.HarvestConfig(out_dir=FIX)  # no salt, no env -> DEV salt + loud warning
        assert any("PUCKWORKS_VIS_SALT" in str(x.message) for x in w)


# --- data-module two-tier loaders (part C): degrade cleanly + assert units ---
from puckworks import data as pwdata


def test_loader_index_absent_returns_present_false(tmp_path, monkeypatch):
    monkeypatch.setattr(pwdata, "VIS_RAW", tmp_path / "does_not_exist")
    assert pwdata.visualizer_index() == {"present": False}


def test_loader_iter_absent_raises_run_the_harvester(tmp_path, monkeypatch):
    monkeypatch.setattr(pwdata, "VIS_RAW", tmp_path / "does_not_exist")
    with pytest.raises(RuntimeError, match="visualizer_harvest full"):
        list(pwdata.visualizer_iter_shots())


def test_loader_iter_and_accessors_on_populated_store(tmp_path, monkeypatch):
    # build a real shard from the fixtures, point the loader at it
    cfg = _cfg(tmp_path)
    recs = [vh.normalize_shot(_load(n), cfg) for n in
            ("decent_full.json", "meticulous_partial.json")]
    vh._write_shard(cfg, 0, recs)
    vh._append_index(cfg, [vh._index_row(r) for r in recs])
    monkeypatch.setattr(pwdata, "VIS_RAW", tmp_path)

    idx = pwdata.visualizer_index()
    assert idx["present"] and idx["n_shots"] == 2

    shots = list(pwdata.visualizer_iter_shots(filter=lambda s: s["machine"] == "decent"))
    assert len(shots) == 1 and shots[0]["id"] == "FAKE-decent-0001"

    import numpy as np
    hy = pwdata.visualizer_hydraulic(shots[0])
    assert isinstance(hy["pressure__Pa"], np.ndarray)
    assert hy["pressure__Pa"][2] == pytest.approx(9.0e5)   # SI, asserted units
    oc = pwdata.visualizer_outcomes(shots[0])
    assert oc["tds__fraction"] == pytest.approx(0.094)
    assert oc["sensory"]["flavor"] == 7


def test_accessor_unit_assertion_catches_off_si(tmp_path):
    # a corrupted stored unit must trip the rule-7 assertion, not pass silently
    tidy = vh.normalize_shot(_load("decent_full.json"), _cfg(tmp_path))
    tidy["units"]["hydraulic"]["pressure__Pa"]["si"] = "bar"  # wrong
    with pytest.raises(AssertionError, match="rule 7"):
        pwdata.visualizer_hydraulic(tidy)


def test_intake_tracked_artifacts_present():
    """The two-tier MANIFEST rows, the data-only card, PROVENANCE and the DERIVED
    aggregate CSV are the tracked intake artifacts (ROADMAP 0.13)."""
    import csv
    root = Path(__file__).resolve().parent.parent
    man = list(csv.DictReader(
        open(root / "puckworks/data/MANIFEST.csv", encoding="utf-8-sig")))
    by_id = {r["dataset_id"]: r for r in man}
    assert "visualizer/hydraulic_timeseries" in by_id
    assert "visualizer/user_outcomes" in by_id
    # tiers kept separate: hydraulic is reference-strength population, outcomes not groundtruth
    assert "reference-strength population" in by_id["visualizer/hydraulic_timeseries"]["validation_strength"]
    assert "NONE as groundtruth" in by_id["visualizer/user_outcomes"]["gate_use"]
    assert by_id["visualizer/hydraulic_timeseries"]["units_in_registry"] == "Pa; kg/s; kg; K; s"
    assert (root / "docs/cards/visualizer_coffee.md").exists()
    assert (root / "puckworks/data/visualizer/PROVENANCE.md").exists()
    agg = (root / "puckworks/data/visualizer/aggregate_stats.csv").read_text()
    assert agg.startswith("metric,key,value") and "total_shots" in agg


def test_num_tolerates_dirty_user_fields():
    """Harvest crash-safety: user-entered numeric fields are free text ('18g', '8.5%',
    'n/a'). `_num` must parse the leading number + flag dirtiness, or return None --
    never raise (a raw '18g' crashed the live crawl)."""
    from puckworks.lib.visualizer_harvest import _num
    assert _num("18g") == (18.0, True)
    assert _num("8.5%") == (8.5, True)
    assert _num("n/a") == (None, True)
    assert _num("") == (None, False) and _num(None) == (None, False)
    assert _num(18) == (18.0, False) and _num(19.5) == (19.5, False)


def test_normalize_shot_survives_dirty_dose():
    """A shot with a unit-suffixed bean_weight ('18g') must normalize (dose parsed +
    flagged), not raise -- guards the live-crawl crash."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig()
    raw = {"id": "x", "user_id": "u", "updated_at": 1, "bean_weight": "18g",
           "drink_weight": 40, "data": {}}
    tidy = normalize_shot(raw, cfg)
    assert abs(tidy["context"]["dose__kg"] - 0.018) < 1e-12
    assert any("dirty_value:bean_weight" in f for f in tidy["flags"])


def test_full_crawl_page_resume(tmp_path, monkeypatch):
    """A reaped full crawl must RESUME listing near where it stopped (not re-list the
    whole newest-first prefix) and still collect every shot via id-dedup. Fakes a
    550-shot / 6-page API; run 1 is bounded, run 2 resumes and completes."""
    from puckworks.lib import visualizer_harvest as vh
    import types

    def fake_get(cfg, session, limiter, path, params=None):
        if path == "/shots":
            start = (params["page"] - 1) * 100
            if start >= 550:
                return {"data": []}
            return {"data": [{"id": f"id{start+i}", "clock": 10000 - (start + i),
                              "updated_at": start + i} for i in range(min(100, 550 - start))]}
        return {"id": path.split("/")[-1], "user_id": "u", "updated_at": 1, "data": {}}

    monkeypatch.setattr(vh, "_get", fake_get)
    monkeypatch.setattr(vh, "_requests",
                        lambda: types.SimpleNamespace(Session=lambda: None,
                                                      RequestException=Exception))
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    cfg.max_requests = 120
    r1 = vh.harvest_all(cfg)
    assert r1["completed"] is False and r1["last_page"] >= 2
    cfg.max_requests = None
    r2 = vh.harvest_all(cfg)
    assert r2["completed"] is True
    assert r2["resumed_from_page"] <= r1["last_page"]           # resumed near, not page 1+prefix
    import csv
    ids = [row["id"] for row in csv.DictReader(open(tmp_path / "_index.csv"))]
    assert len(ids) == len(set(ids)) == 550                     # all shots, no dupes/misses


def test_timeframe_read_from_top_level_and_legacy(monkeypatch):
    """review §8.1 (P0): the live API puts `timeframe` at the TOP LEVEL of a shot detail,
    alongside `data` (value channels only). The normalizer must read it there (with a
    nested `data.timeframe` fallback for legacy fixtures) -- else every live trace loses
    its time base (n_samples=0, missing:timeframe) despite having values."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    # LIVE layout: timeframe top-level, values under data
    live = {"id": "a", "user_id": "u", "updated_at": 1,
            "timeframe": [0.0, 0.5, 1.0],
            "data": {"espresso_pressure": [0.0, 6.0, 9.0], "espresso_flow": [0.0, 1.0, 2.0]}}
    t = normalize_shot(live, cfg)
    assert t["n_samples"] == 3
    assert t["hydraulic"]["time__s"] == [0.0, 0.5, 1.0]
    assert not any("timeframe" in f for f in t["flags"])
    assert len(t["hydraulic"]["pressure__Pa"]) == 3
    # LEGACY nested layout still works (fallback)
    legacy = {"id": "b", "user_id": "u", "updated_at": 1,
              "data": {"timeframe": [0.0, 0.5], "espresso_pressure": [1.0, 2.0]}}
    assert normalize_shot(legacy, cfg)["n_samples"] == 2


def test_sensory_zero_is_kept(monkeypatch):
    """review §8.6 (P1): sensory scores are validated 0..15, so a real 0 must be kept, not
    erased to None by truthiness; booleans are excluded; out-of-range is flagged."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    raw = {"id": "c", "user_id": "u", "updated_at": 1, "timeframe": [0.0],
           "data": {}, "espresso_enjoyment": 0}
    t = normalize_shot(raw, cfg)
    assert t["outcomes"]["sensory"]["espresso_enjoyment"] == 0     # kept, not None

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
    # §8: scale-derived flow is CONFIRMED mass flow -> SI kg/s
    assert hy["mass_flow_from_scale__kg_per_s"][2] == pytest.approx(1.9e-3)
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


def test_ambiguous_flow_kept_native_not_labelled_kg_per_s():
    """§8: pump/model-estimated flow must NOT be stored as kg/s. It is kept native under
    flow_reported__native with units.si=None + a semantic tag, and there is NO flow__kg_per_s
    field asserting mass flow. The SI accessor excludes it."""
    from puckworks import data as pwdata
    cfg = _cfg()
    raw = {"id": "f", "user_id": "u", "updated_at": 1, "timeframe": [0.0, 1.0, 2.0],
           "data": {"espresso_pressure": [0.0, 6.0, 9.0],
                    "espresso_flow": [0.0, 1.5, 2.2],           # ambiguous pump estimate
                    "espresso_flow_weight": [0.0, 1.0, 1.9]}}   # scale-derived mass flow
    t = vh.normalize_shot(raw, cfg)
    hy, u = t["hydraulic"], t["units"]["hydraulic"]
    # ambiguous flow: native value, NOT converted, NOT kg/s
    assert hy["flow_reported__native"] == [0.0, 1.5, 2.2]
    assert u["flow_reported__native"]["si"] is None
    assert u["flow_reported__native"]["semantic"] == "reported_pump_or_model_estimate"
    assert "flow__kg_per_s" not in hy                 # the old mislabelled field is gone
    # scale-derived flow: confirmed SI mass flow
    assert hy["mass_flow_from_scale__kg_per_s"][2] == pytest.approx(1.9e-3)
    # the SI hydraulic accessor surfaces mass flow but NOT the native reported flow
    si = pwdata.visualizer_hydraulic(t)
    assert "mass_flow_from_scale__kg_per_s" in si
    assert "flow_reported__native" not in si


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
        sid = path.split("/")[-1]
        # detail carries the SAME updated_at as the listing (id"idN" -> updated_at N), as the
        # real API does; version-aware dedup relies on that agreement to skip on resume.
        return {"id": sid, "user_id": "u", "updated_at": int(sid[2:]), "data": {}}

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


def test_enjoyment_uses_0_100_scale_not_0_15():
    """SERIALIZER_REVIEW §6: espresso_enjoyment is a 0..100 preference score, NOT a 0..15
    tasting dimension. Validating it against 0..15 nulled every real value >15 (e.g. 82).
    Tasting dimensions must still be validated on 0..15."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    base = {"id": "e", "user_id": "u", "updated_at": 1, "timeframe": [0.0], "data": {}}
    # enjoyment 82 is VALID on the 0..100 scale -> kept, not nulled, not flagged
    t = normalize_shot({**base, "espresso_enjoyment": 82}, cfg)
    assert t["outcomes"]["sensory"]["espresso_enjoyment"] == 82
    assert not any("espresso_enjoyment" in f for f in t["flags"])
    # enjoyment 100 valid; 101 out of range
    assert normalize_shot({**base, "espresso_enjoyment": 100}, cfg)[
        "outcomes"]["sensory"]["espresso_enjoyment"] == 100
    over = normalize_shot({**base, "espresso_enjoyment": 101}, cfg)
    assert over["outcomes"]["sensory"]["espresso_enjoyment"] is None
    assert "out_of_range:espresso_enjoyment" in over["flags"]
    # a tasting dimension is STILL 0..15: 16 is out of range
    dim = normalize_shot({**base, "flavor": 16}, cfg)
    assert dim["outcomes"]["sensory"]["flavor"] is None
    assert "out_of_range:flavor" in dim["flags"]
    assert normalize_shot({**base, "flavor": 15}, cfg)[
        "outcomes"]["sensory"]["flavor"] == 15


def test_crawl_creates_missing_output_dir(tmp_path, monkeypatch):
    """SERIALIZER_REVIEW §2: a fresh harvest must not FileNotFoundError. The per-100 disk
    guard fires on the first iteration, so _crawl must create out_dir before it. Point at a
    not-yet-existent nested path and confirm the crawl runs and writes records."""
    from puckworks.lib import visualizer_harvest as vh
    import types, csv

    def fake_get(cfg, session, limiter, path, params=None):
        if path == "/shots":
            if params["page"] > 1:
                return {"data": []}
            return {"data": [{"id": f"id{i}", "clock": 100 - i, "updated_at": i}
                             for i in range(3)]}
        return {"id": path.split("/")[-1], "user_id": "u", "updated_at": 1,
                "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [6.0, 9.0]}}

    monkeypatch.setattr(vh, "_get", fake_get)
    monkeypatch.setattr(vh, "_requests",
                        lambda: types.SimpleNamespace(Session=lambda: None,
                                                      RequestException=Exception))
    fresh = tmp_path / "does" / "not" / "exist" / "yet"
    assert not fresh.exists()
    cfg = vh.HarvestConfig(out_dir=str(fresh), max_req_per_min=10 ** 9, salt="t")
    r = vh.harvest_all(cfg)                      # must NOT raise FileNotFoundError
    assert r["completed"] is True
    ids = [row["id"] for row in csv.DictReader(open(fresh / "_index.csv"))]
    assert len(ids) == 3


def _crawl_with_pii(tmp_path, monkeypatch):
    """Run a small full crawl whose detail responses carry PII + a real trace, so we can
    inspect the Bronze store. Returns the HarvestConfig used."""
    from puckworks.lib import visualizer_harvest as vh
    import types

    def fake_get(cfg, session, limiter, path, params=None):
        if path == "/shots":
            if params["page"] > 1:
                return {"data": []}
            return {"data": [{"id": f"id{i}", "clock": 100 - i, "updated_at": 1000 + i}
                             for i in range(2)]}
        sid = path.split("/")[-1]
        return {"id": sid, "updated_at": 1000,
                "user_id": "SECRET-user-42", "user_name": "Not A Real Person",
                "barista": "Not A Real Barista", "espresso_notes": "secret tasting note",
                "timeframe": [0.0, 0.5, 1.0],
                "data": {"espresso_pressure": [0.0, 6.0, 9.0]},
                "espresso_enjoyment": 82}

    monkeypatch.setattr(vh, "_get", fake_get)
    monkeypatch.setattr(vh, "_requests",
                        lambda: types.SimpleNamespace(Session=lambda: None,
                                                      RequestException=Exception))
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "store"), max_req_per_min=10 ** 9,
                           salt="bronze-salt")
    vh.harvest_all(cfg)
    return cfg


def test_bronze_stores_pii_stripped_raw_with_content_hash(tmp_path, monkeypatch):
    """SERIALIZER_REVIEW §5: Bronze keeps the raw payload MINUS PII, plus a content hash and
    the salted user hash, so a later normalizer fix can re-normalize offline."""
    from puckworks.lib import visualizer_harvest as vh
    import hashlib, json
    cfg = _crawl_with_pii(tmp_path, monkeypatch)
    bronze = list(vh.iter_bronze(cfg))
    assert len(bronze) == 2
    rec = bronze[0]
    # PII is gone -- no direct identifiers or free text anywhere in the stored record
    blob = json.dumps(rec)
    for banned in ("SECRET-user-42", "Not A Real Person", "Not A Real Barista",
                   "secret tasting note"):
        assert banned not in blob
    for banned_key in vh._PRIVACY_DROP:
        assert banned_key not in rec["payload"]
    # but the raw trace payload IS retained for re-normalization
    assert rec["payload"]["timeframe"] == [0.0, 0.5, 1.0]
    assert rec["payload"]["data"]["espresso_pressure"] == [0.0, 6.0, 9.0]
    assert rec["payload"]["espresso_enjoyment"] == 82
    # salted user hash is kept (not the id); content hash matches the stored payload
    assert rec["hashed_user"] == vh.hash_user(cfg, "SECRET-user-42")
    expect = hashlib.sha256(
        json.dumps(rec["payload"], sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    assert rec["content_sha256"] == expect


def test_renormalize_from_bronze_reproduces_records_offline(tmp_path, monkeypatch):
    """The payoff: re-run the normalizer over Bronze with NO network and reproduce the
    normalized store -- identities preserved via the stored hash despite user_id being
    stripped. Network access during re-normalization would be a bug."""
    from puckworks.lib import visualizer_harvest as vh
    import csv
    cfg = _crawl_with_pii(tmp_path, monkeypatch)
    orig = {r["id"]: r for r in csv.DictReader(open(cfg.out_dir / "_index.csv"))}

    # break the network so re-normalization proves it is fully offline
    def boom(*a, **k):
        raise AssertionError("re-normalization must not hit the network")
    monkeypatch.setattr(vh, "_get", boom)

    dst = tmp_path / "renorm"
    summary = vh.renormalize_from_bronze(cfg, dst)
    assert summary["n_records"] == 2
    redone = {r["id"]: r for r in csv.DictReader(open(dst / "_index.csv"))}
    assert set(redone) == set(orig)
    for sid, row in redone.items():
        assert row["hashed_user"] == orig[sid]["hashed_user"]   # identity preserved
        assert row["hashed_user"]                                # and non-empty
        assert row["n_samples"] == orig[sid]["n_samples"]        # trace reproduced


def _fake_transport(monkeypatch, listing, details):
    """Wire vh._get to a scripted API: `listing` is a dict page->[(id, updated_at), ...];
    `details` is a dict id->detail-response. Missing pages return empty."""
    from puckworks.lib import visualizer_harvest as vh
    import types

    def fake_get(cfg, session, limiter, path, params=None):
        if path == "/shots":
            items = listing.get(params["page"], [])
            return {"data": [{"id": i, "clock": 10 ** 9 - u, "updated_at": u}
                             for (i, u) in items]}
        sid = path.split("/")[-1]
        return details[sid]
    monkeypatch.setattr(vh, "_get", fake_get)
    monkeypatch.setattr(vh, "_requests",
                        lambda: types.SimpleNamespace(Session=lambda: None,
                                                      RequestException=Exception))


def test_version_dedup_reruns_add_nothing_and_capture_edits(tmp_path, monkeypatch):
    """§3/§4: re-listing the moving window must NOT re-fetch or duplicate unchanged shots,
    but MUST capture an edited shot (newer updated_at) as a new version, with the latest
    view collapsing to one current record per id."""
    from puckworks.lib import visualizer_harvest as vh

    def detail(sid, upd, press):
        return {"id": sid, "updated_at": upd, "user_id": f"u-{sid}",
                "timeframe": [0.0, 1.0], "data": {"espresso_pressure": press}}

    # run 1: two shots
    listing = {1: [("a", 100), ("b", 101)]}
    details = {"a": detail("a", 100, [6.0, 9.0]), "b": detail("b", 101, [5.0, 8.0])}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "s"), max_req_per_min=10 ** 9, salt="t")
    r1 = vh.harvest_all(cfg)
    assert r1["n_new"] == 2 and r1["n_fetched"] == 2

    # run 2: SAME window, nothing changed -> zero fetches, zero new, no duplicate rows
    r2 = vh.harvest_all(cfg)
    assert r2["n_fetched"] == 0 and r2["n_new"] == 0 and r2["n_updated"] == 0

    # run 3: shot "a" edited (updated_at bumped, pressure changed) -> fetched as a new version
    details["a"] = detail("a", 200, [6.0, 9.5])
    listing[1] = [("a", 200), ("b", 101)]
    r3 = vh.harvest_all(cfg)
    assert r3["n_fetched"] == 1 and r3["n_new"] == 0 and r3["n_updated"] == 1

    # store now holds 3 VERSIONS but the latest view is 2 shots, with a's newest kept
    assert sum(1 for _ in vh.iter_store(cfg)) == 3
    latest = {s["id"]: s for s in vh.iter_store_latest(cfg)}
    assert set(latest) == {"a", "b"}
    assert latest["a"]["updated_at"] == 200
    assert latest["a"]["hydraulic"]["pressure__Pa"][1] == pytest.approx(9.5e5)  # edited value
    idx = vh.latest_index_rows(cfg)
    assert len(idx) == 2 and vh._as_int(idx["a"]["updated_at"]) == 200


def test_trace_parsing_tolerates_bad_samples_without_dropping_shot():
    """§9: booleans, non-numeric strings, null, and NaN in a trace must become None IN PLACE
    (alignment kept) and be flagged — never a false measurement and never dropping the shot."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    import math
    cfg = HarvestConfig(salt="t")
    raw = {"id": "z", "user_id": "u", "updated_at": 1,
           "timeframe": [0.0, 0.5, 1.0, 1.5, 2.0],
           "data": {"espresso_pressure": [6.0, True, "bad", None, float("nan")]}}
    t = normalize_shot(raw, cfg)                       # must NOT raise
    p = t["hydraulic"]["pressure__Pa"]
    assert len(p) == 5                                 # alignment preserved
    assert p[0] == pytest.approx(6.0e5)                # good sample kept + converted
    assert p[1] is None and p[2] is None and p[4] is None   # bool / non-numeric / NaN dropped
    assert p[3] is None                                # explicit null stays null
    assert any(f.startswith("bad_samples:espresso_pressure=") for f in t["flags"])
    # and the whole record serializes with NaN rejection (no NaN leaked into the trace)
    import json
    json.dumps(t, allow_nan=False)


def test_malformed_record_is_quarantined_not_silently_skipped(tmp_path, monkeypatch):
    """§9: a shot the normalizer cannot handle is written to the quarantine ledger (with a
    reason + content hash), not silently counted-and-dropped, and the crawl continues."""
    from puckworks.lib import visualizer_harvest as vh
    listing = {1: [("ok", 10), ("bad", 11)]}
    details = {
        "ok": {"id": "ok", "updated_at": 10, "user_id": "u",
               "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [6.0, 9.0]}},
        # `data` is a string, not a dict -> normalize_shot raises -> quarantine
        "bad": {"id": "bad", "updated_at": 11, "user_id": "u", "data": "not-a-dict"},
    }
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "s"), max_req_per_min=10 ** 9, salt="t")
    r = vh.harvest_all(cfg)
    assert r["completed"] is True
    assert r["n_new"] == 1 and r["n_quarantined"] == 1     # good stored, bad quarantined
    q = list(vh.iter_quarantine(cfg))
    assert len(q) == 1
    assert q[0]["id"] == "bad" and q[0]["failure_stage"] == "normalize"
    assert q[0]["content_sha256"] and q[0]["run_id"] == r["run_id"]
    # the good shot is in the store; the bad one is NOT
    stored = {s["id"] for s in vh.iter_store_latest(cfg)}
    assert stored == {"ok"}


def test_run_manifest_written_with_provenance_and_salt_fingerprint(tmp_path, monkeypatch):
    """§10: every crawl writes a per-run manifest (counts, timestamps, schema versions,
    mode) with a salt FINGERPRINT — never the salt itself."""
    from puckworks.lib import visualizer_harvest as vh
    import json, hashlib
    listing = {1: [("a", 10), ("b", 11)]}
    details = {sid: {"id": sid, "updated_at": u, "user_id": "u",
                     "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [6.0, 9.0]}}
               for sid, u in (("a", 10), ("b", 11))}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "s"), max_req_per_min=10 ** 9,
                           salt="secret-salt")
    r = vh.harvest_all(cfg)
    mans = list(vh.iter_run_manifests(cfg))
    assert len(mans) == 1
    m = mans[0]
    assert m["run_id"] == r["run_id"] and m["completed"] is True
    assert m["n_new"] == 2 and m["mode"] == "full"
    assert m["normalizer_schema_version"] == vh._NORMALIZE_SCHEMA_VERSION
    assert m["started_at"] <= m["completed_at"]
    # the salt never appears; only a fingerprint of it
    assert "secret-salt" not in json.dumps(m)
    assert m["salt_fingerprint"] == hashlib.sha256(b"secret-salt").hexdigest()[:12]


def test_integration_source_explicit_inferred_unknown():
    """§7: the data-origin app/parser is recorded SEPARATELY from machine, with provenance:
    explicit (stable field) > inferred (brewdata) > unknown (flagged, never guessed)."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    base = {"user_id": "u", "updated_at": 1, "timeframe": [0.0], "data": {}}
    # explicit stable field wins
    ex = normalize_shot({**base, "id": "1", "integration_source": "Decent_TCL"}, cfg)
    assert ex["context"]["integration_source"] == "decent_tcl"
    assert ex["context"]["integration_source_provenance"] == "explicit"
    assert "missing:integration_source" not in ex["flags"]
    # inferred from brewdata when no explicit field
    inf = normalize_shot({**base, "id": "2", "brewdata": {"gaggiuino": {}}}, cfg)
    assert inf["context"]["integration_source"] == "gaggiuino"
    assert inf["context"]["integration_source_provenance"] == "inferred"
    # unknown -> None + flag (never guessed)
    unk = normalize_shot({**base, "id": "3"}, cfg)
    assert unk["context"]["integration_source"] is None
    assert unk["context"]["integration_source_provenance"] == "unknown"
    assert "missing:integration_source" in unk["flags"]


def test_shard_writes_are_atomic_no_tmp_leftover(tmp_path, monkeypatch):
    """Atomicity: shard/bronze writes go via a temp file + fsync + os.replace, leaving no
    .tmp files behind and producing readable gzip shards."""
    from puckworks.lib import visualizer_harvest as vh
    import gzip
    listing = {1: [("a", 10), ("b", 11)]}
    details = {sid: {"id": sid, "updated_at": u, "user_id": "u",
                     "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [6.0, 9.0]}}
               for sid, u in (("a", 10), ("b", 11))}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "s"), max_req_per_min=10 ** 9, salt="t")
    vh.harvest_all(cfg)
    out = cfg.out_dir
    assert not list(out.glob("*.tmp"))                       # no torn temp files left
    shard = sorted(out.glob("shard_*.jsonl.gz"))[0]
    with gzip.open(shard, "rt") as fh:                        # fully readable gzip
        assert sum(1 for _ in fh) == 2


def test_reconcile_and_rebuild_index(tmp_path, monkeypatch):
    """Reconciliation reports a clean store; the index is rebuildable derived metadata --
    deleting it and rebuilding from shards reproduces the same ids, and reconcile stays ok."""
    from puckworks.lib import visualizer_harvest as vh
    listing = {1: [("a", 10), ("b", 11), ("c", 12)]}
    details = {sid: {"id": sid, "updated_at": u, "user_id": "u",
                     "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [6.0, 9.0]}}
               for sid, u in (("a", 10), ("b", 11), ("c", 12))}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "s"), max_req_per_min=10 ** 9, salt="t")
    vh.harvest_all(cfg)

    r = vh.reconcile_store(cfg)
    assert r["ok"] and r["problems"] == []
    assert r["n_unique_ids"] == 3 and r["n_latest"] == 3 and r["n_index_rows"] == 3

    # index is rebuildable from the shards
    vh._index_path(cfg).unlink()
    n = vh.rebuild_index(cfg)
    assert n == 3
    assert {row["id"] for row in vh.iter_index_rows(cfg)} == {"a", "b", "c"}
    assert vh.reconcile_store(cfg)["ok"]


def test_timeseries_qc_metrics():
    """QC metrics: a clean trace reports monotonic time + sane dt; a non-monotonic /
    duplicate-timestamp / flatline trace is measured and flagged, not silently accepted."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    # clean, evenly-sampled trace
    ok = normalize_shot({"id": "1", "user_id": "u", "updated_at": 1,
                         "timeframe": [0.0, 0.5, 1.0, 1.5],
                         "data": {"espresso_pressure": [1.0, 2.0, 3.0, 4.0]}}, cfg)
    q = ok["qc"]
    assert q["time_monotonic"] is True and q["time_duplicate_stamps"] == 0
    assert q["dt_median_s"] == pytest.approx(0.5)
    assert q["channels"]["pressure__Pa"]["flatline"] is False
    assert q["channels"]["pressure__Pa"]["len_matches_time"] is True
    assert "qc:time_not_monotonic" not in ok["flags"]

    # non-monotonic time with a duplicate stamp + a flatline channel
    bad = normalize_shot({"id": "2", "user_id": "u", "updated_at": 1,
                          "timeframe": [0.0, 1.0, 1.0, 0.5],           # dup + goes backwards
                          "data": {"espresso_pressure": [5.0, 5.0, 5.0, 5.0]}}, cfg)
    q2 = bad["qc"]
    assert q2["time_monotonic"] is False
    assert q2["time_duplicate_stamps"] == 1
    assert q2["time_nonincreasing_steps"] == 2                         # the dup + the reversal
    assert q2["channels"]["pressure__Pa"]["flatline"] is True
    assert "qc:time_not_monotonic" in bad["flags"]
    assert "qc:duplicate_timestamps" in bad["flags"]


def test_latest_returns_last_written_on_timestamp_tie(tmp_path):
    """P0-3: two versions of one shot share an integer-second updated_at with different
    content. The latest view must return the index's last-wins winner (by content hash),
    not the first physical record sharing that timestamp."""
    from puckworks.lib import visualizer_harvest as vh
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), salt="t")
    r1 = vh.normalize_shot({"id": "A", "user_id": "u", "updated_at": 100,
                            "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [1.0, 1.0]}}, cfg)
    r2 = vh.normalize_shot({"id": "A", "user_id": "u", "updated_at": 100,
                            "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [9.0, 9.0]}}, cfg)
    assert r1["content_sha256"] != r2["content_sha256"]       # distinct versions
    vh._write_shard(cfg, 0, [r1, r2])
    vh._append_index(cfg, [vh._index_row(r1), vh._index_row(r2)])
    latest = {s["id"]: s for s in vh.iter_store_latest(cfg)}
    assert latest["A"]["hydraulic"]["pressure__Pa"][0] == pytest.approx(9.0e5)  # last-written


def test_reconcile_detects_version_missing_from_index(tmp_path):
    """P1-1: a stored version absent from the index must be a reconcile FAILURE, not `ok`."""
    from puckworks.lib import visualizer_harvest as vh
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), salt="t")
    a100 = vh.normalize_shot({"id": "A", "user_id": "u", "updated_at": 100,
                              "timeframe": [0.0], "data": {}}, cfg)
    a101 = vh.normalize_shot({"id": "A", "user_id": "u", "updated_at": 101,
                              "timeframe": [0.0], "data": {}}, cfg)
    vh._write_shard(cfg, 0, [a100, a101])
    vh._append_index(cfg, [vh._index_row(a101)])              # only the 101 version indexed
    rep = vh.reconcile_store(cfg)
    assert rep["ok"] is False
    assert any("versions_in_shards_not_index" in p for p in rep["problems"])


def test_incremental_cursor_not_advanced_on_incomplete_run(tmp_path, monkeypatch):
    """P0-2: an interrupted descending incremental run must NOT advance its durable cursor
    past a record it never fetched, else that record is skipped forever. A@200 fetched, run
    stops; a second run must still capture B@199."""
    from puckworks.lib import visualizer_harvest as vh
    listing = {1: [("A", 200), ("B", 199)]}                  # newest-first
    details = {sid: {"id": sid, "updated_at": u, "user_id": "u",
                     "timeframe": [0.0], "data": {}} for sid, u in (("A", 200), ("B", 199))}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    vh._save_cursor(cfg, 100)                                 # prior committed cursor

    cfg.max_requests = 1
    r1 = vh.harvest_incremental(cfg)
    assert r1["completed"] is False
    assert vh._load_cursor(cfg)["last_updated_at"] == 100     # NOT advanced to 200

    cfg.max_requests = None
    vh.harvest_incremental(cfg)
    assert {s["id"] for s in vh.iter_store_latest(cfg)} == {"A", "B"}   # B not lost


def test_run_id_is_unique_across_runs(tmp_path, monkeypatch):
    """P1-8: run ids must not collide (the old seconds+pid scheme could)."""
    from puckworks.lib import visualizer_harvest as vh
    _fake_transport(monkeypatch, {1: []}, {})
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    ids = {vh.harvest_all(cfg)["run_id"] for _ in range(5)}
    assert len(ids) == 5


def test_strip_pii_is_recursive_and_drops_free_text():
    """P1-3: PII must be dropped at ANY nesting depth, and free-text profile/tags too."""
    from puckworks.lib import visualizer_harvest as vh
    import json
    raw = {"id": "x", "user_id": "SECRET", "espresso_pressure": [1, 2],
           "metadata": {"user_name": "Klaus", "email": "k@example.com",
                        "notes": "a private note", "keep": "ok"},
           "profile_title": "2021.12_klaus_1mls_80C", "tags": ["klaus", "home"]}
    stripped = vh._strip_pii(raw)
    blob = json.dumps(stripped)
    for banned in ("SECRET", "Klaus", "k@example.com", "a private note",
                   "2021.12_klaus_1mls_80C", "klaus"):
        assert banned not in blob
    assert stripped["metadata"] == {"keep": "ok"}         # nested PII gone, benign kept
    assert "profile_title" not in stripped and "tags" not in stripped
    assert stripped["espresso_pressure"] == [1, 2]        # telemetry preserved
    # and the normalized context keeps only privacy-safe presence signals
    cfg = vh.HarvestConfig(salt="t")
    ctx = vh.normalize_shot(raw, cfg)["context"]
    assert ctx["profile_present"] is True and ctx["n_tags"] == 2
    assert "profile_title" not in ctx and "tags" not in ctx


def test_quarantine_retains_payload_for_offline_repair(tmp_path, monkeypatch):
    """P1-2: a quarantined record keeps its PII-stripped payload so a future normalizer fix
    can re-normalize it offline (previously only a hash + reason were stored)."""
    from puckworks.lib import visualizer_harvest as vh
    listing = {1: [("bad", 11)]}
    details = {"bad": {"id": "bad", "updated_at": 11, "user_id": "u",
                       "data": "not-a-dict", "espresso_pressure": [6.0, 9.0]}}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    vh.harvest_all(cfg)
    q = list(vh.iter_quarantine(cfg))
    assert len(q) == 1 and q[0]["payload"]                 # payload retained, not just hash
    assert "user_id" not in q[0]["payload"]                # PII still stripped
    assert q[0]["payload"]["espresso_pressure"] == [6.0, 9.0]


def test_fetch_404_is_quarantined_and_crawl_continues(tmp_path, monkeypatch):
    """P0-05: a 404 (shot deleted/private between list and detail) must record a lifecycle
    event and CONTINUE, not stop the whole crawl. The valid sibling is still stored."""
    from puckworks.lib import visualizer_harvest as vh
    import types

    class _Resp:
        status_code = 404

    def fake_get(cfg, session, limiter, path, params=None):
        if path == "/shots":
            if params["page"] > 1:
                return {"data": []}
            return {"data": [{"id": "gone", "clock": 2, "updated_at": 10},
                             {"id": "ok", "clock": 1, "updated_at": 11}]}
        if path.endswith("/gone"):
            err = RuntimeError("404 Not Found")
            err.response = _Resp()
            raise err
        return {"id": "ok", "updated_at": 11, "user_id": "u",
                "timeframe": [0.0, 1.0], "data": {"espresso_pressure": [6.0, 9.0]}}

    monkeypatch.setattr(vh, "_get", fake_get)
    monkeypatch.setattr(vh, "_requests",
                        lambda: types.SimpleNamespace(Session=lambda: None,
                                                      RequestException=Exception))
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    r = vh.harvest_all(cfg)
    assert r["completed"] is True and r["n_quarantined"] == 1
    assert {s["id"] for s in vh.iter_store_latest(cfg)} == {"ok"}     # sibling not lost
    assert list(vh.iter_quarantine(cfg))[0]["failure_stage"] == "fetch_404"


def test_list_detail_id_mismatch_is_quarantined(tmp_path, monkeypatch):
    """P1-02: if the detail response's id != the listed id, it must be quarantined, never
    stored under the wrong id."""
    from puckworks.lib import visualizer_harvest as vh
    listing = {1: [("A", 10)]}
    details = {"A": {"id": "B", "updated_at": 10, "user_id": "u",     # WRONG id
                     "timeframe": [0.0], "data": {}}}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    r = vh.harvest_all(cfg)
    assert r["n_quarantined"] == 1 and r["n_new"] == 0
    assert list(vh.iter_store_latest(cfg)) == []                      # nothing stored
    assert list(vh.iter_quarantine(cfg))[0]["failure_stage"] == "list_detail_id_mismatch"


def test_renormalize_refuses_nonempty_destination(tmp_path, monkeypatch):
    """P1-01: re-normalizing into a non-empty destination must raise, not append duplicate
    index rows; replace_dst=True is idempotent."""
    from puckworks.lib import visualizer_harvest as vh
    cfg = _crawl_with_pii(tmp_path, monkeypatch)
    dst = tmp_path / "renorm"
    vh.renormalize_from_bronze(cfg, dst)
    with pytest.raises(RuntimeError, match="not empty"):
        vh.renormalize_from_bronze(cfg, dst)                          # second run refused
    s = vh.renormalize_from_bronze(cfg, dst, replace_dst=True)        # explicit replace ok
    import csv
    rows = list(csv.DictReader(open(dst / "_index.csv")))
    assert len(rows) == s["n_records"]                               # no duplicate rows


def test_git_commit_uses_repo_root_not_cwd(tmp_path, monkeypatch):
    """P1-04: _git_commit resolves the Puckworks repo, not the process cwd (which reported an
    unrelated repo's HEAD). Running from an unrelated dir must not change the answer."""
    from puckworks.lib import visualizer_harvest as vh
    import os
    here = vh._git_commit()
    old = os.getcwd()
    try:
        os.chdir(tmp_path)
        assert vh._git_commit() == here      # unaffected by cwd
    finally:
        os.chdir(old)


def test_sensory_noninteger_is_flagged_not_truncated():
    """P2-02: a non-integer sensory value (7.9) must be flagged and dropped, not silently
    truncated to 7. An integer-valued float (7.0) is accepted."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    base = {"id": "s", "user_id": "u", "updated_at": 1, "timeframe": [0.0], "data": {}}
    bad = normalize_shot({**base, "flavor": 7.9}, cfg)
    assert bad["outcomes"]["sensory"]["flavor"] is None
    assert "noninteger_sensory:flavor" in bad["flags"]
    ok = normalize_shot({**base, "flavor": 7.0}, cfg)
    assert ok["outcomes"]["sensory"]["flavor"] == 7          # integer-valued float accepted


def test_physical_impossibility_is_flagged(monkeypatch):
    """P1-07: impossible values are flagged (retained in Bronze, but must not silently enter
    modeling cohorts): fractions outside 0..1, nonpositive dose/duration, out-of-window
    pressure/temperature."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    t = normalize_shot({"id": "p", "user_id": "u", "updated_at": 1,
                        "drink_tds": 250.0,            # -> 2.5 fraction, impossible
                        "bean_weight": "-18", "duration": "-30",
                        "timeframe": [0.0, 1.0],
                        "data": {"espresso_pressure": [-5.0, 9.0],   # -5 bar -> -5e5 Pa
                                 "espresso_temperature_basket": [20.0, 1000.0]}}, cfg)
    f = t["flags"]
    assert "impossible:tds__fraction" in f
    assert "impossible:dose__kg_nonpositive" in f
    assert "impossible:duration__s_nonpositive" in f
    assert "impossible:pressure__Pa" in f
    assert "impossible:temperature_basket__K" in f
    # a clean shot has none of these
    ok = normalize_shot({"id": "q", "user_id": "u", "updated_at": 1, "timeframe": [0.0, 1.0],
                         "data": {"espresso_pressure": [6.0, 9.0]}}, cfg)
    assert not any(fl.startswith("impossible:") for fl in ok["flags"])


def test_state_channel_qc_flags_alignment_and_bad_values():
    """P2-01: the state channel must not bypass QC — length mismatch and non-code values
    (booleans, free text) are flagged."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    t = normalize_shot({"id": "st", "user_id": "u", "updated_at": 1,
                        "timeframe": [0.0, 1.0, 2.0],
                        "data": {"espresso_state_change": [0, True, "manual-note"]}}, cfg)
    assert "length_mismatch:espresso_state_change" not in t["flags"]   # same length (3)
    assert any(f.startswith("invalid_state_values:") for f in t["flags"])
    short = normalize_shot({"id": "st2", "user_id": "u", "updated_at": 1,
                            "timeframe": [0.0, 1.0, 2.0],
                            "data": {"espresso_state_change": [0, 1]}}, cfg)  # too short
    assert "length_mismatch:espresso_state_change" in short["flags"]


def test_strip_pii_drops_urls_and_case_variants():
    """P1-03: the privacy filter is case-insensitive and drops relinking URLs and unknown
    free-text key variants (emailAddress, Owner, profile_url, image_url)."""
    from puckworks.lib import visualizer_harvest as vh
    import json
    raw = {"id": "x", "espresso_pressure": [1, 2],
           "emailAddress": "alice@example.test", "profile_url": "https://x/p",
           "image_url": "https://x/i.jpg",
           "metadata": {"Owner": "Alice", "comment": "Alice home", "location": "123 St",
                        "keep": "ok"}}
    stripped = vh._strip_pii(raw)
    blob = json.dumps(stripped)
    for banned in ("alice@example.test", "https://x/p", "https://x/i.jpg", "Alice",
                   "Alice home", "123 St"):
        assert banned not in blob
    assert stripped["metadata"] == {"keep": "ok"}
    assert stripped["espresso_pressure"] == [1, 2]        # telemetry preserved


def test_reconcile_bronze_parity_optin(tmp_path, monkeypatch):
    """P1-05: reconcile reports normalized versions lacking Bronze, and fails only when
    require_bronze=True (so a legitimately mixed store still passes by default)."""
    from puckworks.lib import visualizer_harvest as vh
    cfg = _crawl_with_pii(tmp_path, monkeypatch)   # store WITH bronze
    r = vh.reconcile_store(cfg)
    assert r["ok"] and r["n_norm_without_bronze"] == 0
    # a normalized-only shot (no bronze) is reported but ok by default, fails when required
    extra = vh.normalize_shot({"id": "nb", "user_id": "u", "updated_at": 9,
                               "timeframe": [0.0], "data": {}}, cfg)
    vh._write_shard(cfg, 999, [extra])             # write normalized WITHOUT bronze
    vh._append_index(cfg, [vh._index_row(extra)])
    r2 = vh.reconcile_store(cfg)
    assert r2["n_norm_without_bronze"] == 1 and r2["ok"] is True
    assert vh.reconcile_store(cfg, require_bronze=True)["ok"] is False


def test_state_files_written_atomically_no_tmp(tmp_path, monkeypatch):
    """P2-07: cursor / list-page / manifest writes leave no .tmp files and are valid JSON."""
    from puckworks.lib import visualizer_harvest as vh
    import json
    listing = {1: [("a", 10)]}
    details = {"a": {"id": "a", "updated_at": 10, "user_id": "u",
                     "timeframe": [0.0], "data": {}}}
    _fake_transport(monkeypatch, listing, details)
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), max_req_per_min=10 ** 9, salt="t")
    vh.harvest_all(cfg)
    assert not list(cfg.out_dir.glob("*.tmp"))
    assert not list((cfg.out_dir / "_runs").glob("*.tmp"))
    json.load(open(cfg.out_dir / "_list_page.json"))          # valid, complete JSON
    for m in (cfg.out_dir / "_runs").glob("*.json"):
        json.load(open(m))


def test_num_rejects_booleans_and_non_finite():
    """P1-4: scalar parsing must reject booleans (True != 1.0 dose) and NaN/Inf (they would
    later be mis-attributed to serialization), returning (None, dirty=True)."""
    from puckworks.lib.visualizer_harvest import _num
    assert _num(True) == (None, True)
    assert _num(False) == (None, True)
    assert _num(float("nan")) == (None, True)
    assert _num(float("inf")) == (None, True)
    assert _num("nan") == (None, True)
    assert _num("inf") == (None, True)
    assert _num(18.0) == (18.0, False)                     # a real number still passes
    assert _num("18g") == (18.0, True)                     # dirty-suffix still parsed+flagged


def test_start_time_retained_and_duration_dirty_flagged():
    """P1-5: brew start_time is retained (distinct from updated_at). P1-4: a dirty duration
    surfaces a flag instead of silently dropping it."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    t = normalize_shot({"id": "s", "user_id": "u", "updated_at": 1784, "start_time": 1700,
                        "duration": "30 s", "timeframe": [0.0], "data": {}}, cfg)
    assert t["context"]["start_time"] == 1700
    assert t["context"]["duration__s"] == 30.0
    assert "dirty_value:duration" in t["flags"]


def test_qc_gap_awareness_missing_timestamp():
    """Review #2: a missing timestamp inside a series must be COUNTED, not silently bridged
    into one large interval, and must not let an under-determined trace read as monotonic."""
    from puckworks.lib.visualizer_harvest import normalize_shot, HarvestConfig
    cfg = HarvestConfig(salt="t")
    t = normalize_shot({"id": "g", "user_id": "u", "updated_at": 1,
                        "timeframe": [0.0, None, 2.0],
                        "data": {"espresso_pressure": [1.0, 2.0, 3.0]}}, cfg)
    q = t["qc"]
    assert q["time_missing"] == 1
    assert q.get("dt_max_s") is None or q["dt_max_s"] < 2.0   # no bridged 2 s step
    assert q["time_monotonic"] is None                       # not enough adjacency to judge
    assert "qc:missing_timestamps" in t["flags"]

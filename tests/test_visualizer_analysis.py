"""Tests for the corpus-analysis harness (WP1): eligibility engine, P0 census, pressure atlas.

Synthetic stores only (no network). Verifies eligibility flow, census counts + one-shot-per-
user sensitivity, pressure tracking metrics/aggregation, the EXPLORATORY marker, and the
guard that ambiguous flow cannot enter the pressure atlas.
"""
import pytest

from puckworks.lib import visualizer_harvest as vh
from puckworks.data import visualizer_store as vs
from puckworks.analysis import visualizer_eligibility as elig
from puckworks.analysis import visualizer_census as census
from puckworks.analysis import controller_atlas as atlas


def _shot(cfg, sid, user, data, updated_at=100, extra=None):
    raw = {"id": sid, "user_id": user, "updated_at": updated_at,
           "timeframe": [0.0, 1.0, 2.0, 3.0], "data": data}
    raw.update(extra or {})
    return vh.normalize_shot(raw, cfg)


def _store(tmp_path, records):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path), salt="t")
    vh._write_shard(cfg, 0, records)
    vh._append_index(cfg, [vh._index_row(r) for r in records])
    return vs.CorpusSnapshot(tmp_path, name="t", classification="exploratory-window")


def test_eligibility_profiles_and_flow(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    tracked = _shot(cfg, "A", "u1",
                    {"espresso_pressure": [6.0, 9.0, 9.0, 9.0],
                     "espresso_pressure_goal": [6.0, 9.0, 9.0, 9.0]})
    no_goal = _shot(cfg, "B", "u2", {"espresso_pressure": [6.0, 9.0, 9.0, 9.0]})
    empty = _shot(cfg, "C", "u3", {})
    snap = _store(tmp_path, [tracked, no_goal, empty])
    rep = elig.eligibility_report(snap, "pressure_tracking_valid")
    assert rep["n_included"] == 1
    assert rep["exclusion_reasons"].get("no_pressure_goal") == 1
    assert rep["exclusion_reasons"].get("no_hydraulic_channel") == 1
    # census_all includes everything
    assert elig.eligibility_report(snap, "census_all")["n_included"] == 3


def test_census_counts_and_one_shot_per_user(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    # one prolific user (3 shots) + one other user (1 shot)
    recs = [_shot(cfg, f"P{i}", "prolific", {"espresso_pressure": [6.0, 9.0, 9.0, 9.0]},
                  updated_at=100 + i) for i in range(3)]
    recs.append(_shot(cfg, "Q", "other", {"espresso_pressure": [6.0, 9.0, 9.0, 9.0]},
                      extra={"drink_tds": 9.0}))
    snap = _store(tmp_path, recs)
    prod = census.corpus_census(snap)
    assert prod["exploratory"] is True and prod["product"] == "corpus_census"
    allc = prod["results"]["all_shots"]
    assert allc["n_shots"] == 4 and allc["max_shots_per_user"] == 3
    assert allc["channel_availability"]["pressure__Pa"] == 4
    assert allc["outcome_coverage"].get("tds") == 1        # kept separate from hydraulics
    # one-shot-per-user collapses the prolific user to a single shot
    assert prod["results"]["one_shot_per_user"]["n_shots"] == 2


def test_pressure_atlas_metrics_and_aggregation(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    # achieved lags/deviates from a stepped goal
    a = _shot(cfg, "A", "u1",
              {"espresso_pressure": [3.0, 8.0, 9.0, 9.0],
               "espresso_pressure_goal": [3.0, 9.0, 9.0, 9.0]},
              extra={"brewdata": {"decent": {}}})
    snap = _store(tmp_path, [a])
    m = atlas.pressure_tracking_metrics(snap.latest().__next__())
    assert m["active_time_s"] == pytest.approx(3.0)        # time-weighted active interval
    assert m["n_goal_transitions"] == 1                    # 3->9 bar
    assert m["tw_rmse_bar"] > 0 and m["tw_signed_bias_bar"] < 0   # achieved below goal on avg
    assert 0.0 <= m["frac_time_within_1bar"] <= 1.0        # a fraction of active time
    prod = atlas.pressure_atlas(snap)
    assert prod["results"]["overall"]["n_shots"] == 1
    assert "decent" in prod["results"]["by_source_family"]
    assert prod["exploratory"] is True


def test_pressure_atlas_excludes_shots_without_goal(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    no_goal = _shot(cfg, "A", "u", {"espresso_pressure": [6.0, 9.0, 9.0, 9.0]})
    snap = _store(tmp_path, [no_goal])
    assert atlas.pressure_atlas(snap)["results"]["overall"]["n_shots"] == 0


def test_pressure_atlas_never_pools_ambiguous_flow():
    # the guardrail: the atlas channels are pooling-safe, proxy flow is not
    assert vs.is_pooling_safe(atlas._ACHIEVED) and vs.is_pooling_safe(atlas._GOAL)
    assert vs.is_pooling_safe("flow_reported__native") is False


def test_corpus_bundle_products_and_freeze_guard(tmp_path):
    from puckworks.lib import visualizer_harvest as vh
    from puckworks.data import visualizer_store as vs
    from puckworks.analysis import corpus_bundle
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    a = _shot(cfg, "A", "u1",
              {"espresso_pressure": [3.0, 9.0, 9.0, 9.0],
               "espresso_pressure_goal": [3.0, 9.0, 9.0, 9.0]}, extra={"drink_tds": 9.0})
    snap = _store(tmp_path, [a])                     # classification=exploratory-window
    bundle = corpus_bundle.build_bundle(snap, dst_dir=tmp_path / "bundle")
    assert bundle["exploratory"] is True and bundle["bundle_sha256"]
    prods = bundle["products"]
    assert set(prods) == {"census", "pressure_atlas", "eligibility", "claim_bundle"}
    assert prods["claim_bundle"]["corpus"]["n_shots"] == 1
    assert "latent puck" in prods["claim_bundle"]["evidence_ceiling"]     # ecological ceiling
    assert (tmp_path / "bundle" / "bundle.json").exists()
    # deterministic
    assert corpus_bundle.build_bundle(snap)["bundle_sha256"] == bundle["bundle_sha256"]
    # WP1.2: a publication bundle needs a VERIFIED receipt, not a classification label.
    import pytest as _pt
    with _pt.raises(RuntimeError, match="VERIFIED publication receipt"):
        corpus_bundle.build_bundle(snap, require_freeze=True)
    # assigning the 'publication-freeze' label to a snapshot CANNOT unlock it (the old bug)
    labelled = vs.CorpusSnapshot(tmp_path, name="f", classification="publication-freeze")
    with _pt.raises(RuntimeError, match="VERIFIED publication receipt"):
        corpus_bundle.build_bundle(labelled, require_freeze=True)
    # a forged receipt (not qualifying) is also refused
    class _Fake:
        qualifies_for_publication = False
        receipt_sha256 = "x"
    with _pt.raises(RuntimeError, match="VERIFIED publication receipt"):
        corpus_bundle.build_bundle(snap, require_freeze=True, receipt=_Fake())

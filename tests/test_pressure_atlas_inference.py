"""PR5 / WP2.7-2.9 — hierarchical inference for the pressure atlas: contributor concentration,
inclusion/exclusion flow, a SEEDED (store-order-independent) one-shot-per-user sensitivity, and
user-clustered bootstrap CIs. Deterministic; no network.
"""
from puckworks.lib import visualizer_harvest as vh
from puckworks.data import visualizer_store as vs
from puckworks.analysis import controller_atlas as atlas


def _shot(cfg, sid, user, pbar, gbar=(6.0, 9.0, 9.0, 9.0)):
    return vh.normalize_shot(
        {"id": sid, "user_id": user, "updated_at": 100, "timeframe": [0.0, 1.0, 2.0, 3.0],
         "data": {"espresso_pressure": list(pbar), "espresso_pressure_goal": list(gbar)}}, cfg)


def _fleet(cfg):
    # u1 x3, u2 x2, u3 x1 = 6 eligible shots over 3 users (concentrated)
    spec = [("u1", [6, 9, 9, 9]), ("u1", [6, 8, 9, 9]), ("u1", [6, 9, 8, 9]),
            ("u2", [6, 9, 9, 9]), ("u2", [6, 7, 9, 9]), ("u3", [6, 9, 9, 9])]
    return [_shot(cfg, "S%d" % i, u, p) for i, (u, p) in enumerate(spec)]


def _store(d, records):
    cfg = vh.HarvestConfig(out_dir=str(d), salt="t")
    vh._write_shard(cfg, 0, records)
    vh._append_index(cfg, [vh._index_row(r) for r in records])
    return vs.CorpusSnapshot(d, name="t", classification="current-state")


def test_concentration_exclusion_and_bootstrap(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    recs = _fleet(cfg)
    recs.append(vh.normalize_shot(                          # an excluded shot (no goal channel)
        {"id": "NG", "user_id": "u4", "updated_at": 100, "timeframe": [0.0, 1.0, 2.0, 3.0],
         "data": {"espresso_pressure": [6.0, 9.0, 9.0, 9.0]}}, cfg))
    r = atlas.pressure_atlas(_store(tmp_path / "s", recs), n_boot=200)["results"]

    conc = r["concentration"]
    assert conc["n_shots"] == 6 and conc["n_users"] == 3 and conc["max_shots_per_user"] == 3
    assert 2.0 < conc["effective_users"] < 3.0            # concentrated (u1 dominates)
    assert r["exclusion_flow"]["n_excluded"] >= 1         # the no-goal shot
    assert r["one_shot_per_user"]["n_shots"] == 3         # exactly one per user
    bs = r["user_cluster_bootstrap"]["tw_mae_bar"]
    assert bs["n_users"] == 3 and bs["ci95_lo"] <= bs["point_median"] <= bs["ci95_hi"]


def test_atlas_is_store_order_independent(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    recs = _fleet(cfg)
    a = atlas.pressure_atlas(_store(tmp_path / "a", list(recs)), n_boot=200)["results"]
    b = atlas.pressure_atlas(_store(tmp_path / "b", list(reversed(recs))), n_boot=200)["results"]
    assert a["bootstrap_seed"] == b["bootstrap_seed"]     # seed from SORTED users, not order
    assert a["one_shot_per_user"] == b["one_shot_per_user"]
    assert a["user_cluster_bootstrap"] == b["user_cluster_bootstrap"]
    assert a["concentration"] == b["concentration"]


def test_bootstrap_is_deterministic(tmp_path):
    cfg = vh.HarvestConfig(out_dir=str(tmp_path / "x"), salt="t")
    snap = _store(tmp_path / "s", _fleet(cfg))
    a = atlas.pressure_atlas(snap, n_boot=200)["results"]["user_cluster_bootstrap"]
    b = atlas.pressure_atlas(snap, n_boot=200)["results"]["user_cluster_bootstrap"]
    assert a == b                                          # same seed -> identical CIs

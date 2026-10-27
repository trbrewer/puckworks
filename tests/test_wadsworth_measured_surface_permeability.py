"""Synthetic fitting/selection tests; actual observations are only authenticated."""
import csv
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import wadsworth_measured_surface_permeability as m

ROOT = Path(__file__).resolve().parents[1]


def test_parent_manifest_identity_is_bound_before_contents(tmp_path):
    (tmp_path/"ARTIFACTS.json").write_text("{}\n")
    with pytest.raises(m.p.QualificationError, match="manifest identity"):
        m.authenticate_parent(tmp_path, ROOT, [])


@pytest.fixture
def records():
    rng = np.random.default_rng(331)
    rows = []
    for coffee in m.COFFEES:
        for g in range(1, 12):
            if (coffee, g) == ("Guayacan", 2):
                continue
            radius = (.2+.05*g)*m.p.R0
            phi, surface = float(rng.uniform(.3, .7)), float(rng.uniform(1e4, 5e4))
            z = 2-1.4*np.log(surface/m.S0)+1.2*np.log(phi)+rng.normal(0, .1)
            rows.append(m.Record(coffee, g, radius, phi, float(m.p.K0*np.exp(z)), 0, surface))
    return rows


def test_authenticated_column_units_join_and_observation_order():
    base = m.p.load_table(ROOT/m.p.SOURCE)
    rows = m.load_table(ROOT/m.p.SOURCE)
    assert len(rows) == 21 and rows[0].s == 33588.43 and rows[0].s != 40384.06
    assert rows[0].R == .000211 and rows[0].phi == .4792
    assert [{k: v for k, v in asdict(r).items() if k != "s"} for r in rows] == [asdict(r) for r in base]
    assert m.p.sha(m.p.canonical([r.identity for r in rows])) == m.PARENT_MEMBERSHIP
    raw = list(csv.DictReader((ROOT/m.p.SOURCE).read_text().splitlines()))
    assert m.join_surface(base, raw[::-1]) == rows  # Keyed join preserves parent order.
    for bad in (raw+raw[:1], raw[:-1]):
        with pytest.raises(m.p.QualificationError):
            m.join_surface(base, bad)
    bad = [dict(r) for r in raw]
    bad[1]["s_p_connected_per_m"] = "20000"
    with pytest.raises(m.p.QualificationError, match="missingness"):
        m.join_surface(base, bad)
    for value in ("0", "nan", "-1"):
        bad = [dict(r) for r in raw]
        bad[0]["s_p_connected_per_m"] = value
        with pytest.raises(m.p.QualificationError, match="surface"):
            m.join_surface(base, bad)


def test_four_arm_oof_keyed_diagnostics_and_outcome_separation(records):
    point = m.evaluate(records)
    changed = m.evaluate([replace(r, k=r.k*9) if r.coffee == "Tumba" else r for r in records])
    assert point["diagnostics"]["Guayacan"] == changed["diagnostics"]["Guayacan"]
    for coffee in m.COFFEES:
        assert set(point["diagnostics"][coffee]) == set(m.ARMS)
        for arm, diag in point["diagnostics"][coffee].items():
            assert diag["source"] == coffee and diag["arm"] == arm
    for arm in m.ARMS:
        assert len(point["predictions"][arm]) == 21
        assert np.all(np.isfinite(point["predictions"][arm]))
    ids = [tuple(i) for f in point["folds"] for i in f["evaluation"]]
    assert len(ids) == len(set(ids)) == 21
    assert m.p.ARMS == ("W3", "E3", "N")


def test_surface_does_not_enter_retained_arms(records):
    first = m.evaluate(records)
    changed = m.evaluate([replace(r, s=r.s*(1+r.G*.05)) for r in records])
    for arm in m.COMPARATORS:
        assert first["predictions"][arm] == changed["predictions"][arm]
        for c in m.COFFEES:
            assert first["diagnostics"][c][arm] == changed["diagnostics"][c][arm]
    assert first["predictions"]["S3"] != changed["predictions"]["S3"]


def test_surface_reference_changes_only_intercept(records):
    train, held = records[:10], records[10:]
    pred, first = m.fit_s3(train, held, np.ones(10))
    other, second = m.fit_s3(train, held, np.ones(10), s0=2e4)
    np.testing.assert_allclose(pred, other, rtol=0, atol=1e-12)
    a, b = first["coefficients"], second["coefficients"]
    assert a["sSlope"] == pytest.approx(b["sSlope"])
    assert a["sPhi"] == pytest.approx(b["sPhi"])
    assert b["sIntercept"] == pytest.approx(a["sIntercept"]+a["sSlope"]*np.log(2))


@pytest.mark.parametrize("arm", m.ARMS)
def test_weighted_replication_qr_and_nesting(records, arm):
    train, held = records[:10], records[10:]
    weights = np.array([0, 2, 1, 3, 1, 0, 2, 1, 2, 1])
    def fit(rows, w):
        return m.fit_s3(rows, held, w) if arm == "S3" else m.p.fit(rows, held, arm, w)
    pred, diag = fit(train, weights)
    replicas = [r for r, w in zip(train, weights) for _ in range(w)]
    repeated, other = fit(replicas, np.ones(len(replicas)))
    np.testing.assert_allclose(pred, repeated, atol=1e-12, rtol=1e-12)
    assert diag["qr_max_log_difference"] < 1e-10
    assert diag["training_sse"] == pytest.approx(other["training_sse"], abs=1e-12)
    if arm in ("S3", "E3"):
        _, naive = m.p.fit(train, held, "N", weights)
        assert diag["training_sse"] <= naive["training_sse"]+1e-12


def test_paired_vectors_and_reproduction_guard(records):
    boot = m.p.bootstrap(records, n=3, evaluator=m.evaluate)
    assert boot["counts"]["completed"] == 3
    for draw in boot["draws"]:
        for c in m.COFFEES:
            train = next(f for f in draw["result"]["folds"] if f["source"] == c)
            held = next(f for f in draw["result"]["folds"] if f["target"] == c)
            assert train["training_weights"] == held["evaluation_weights"] == draw["weights"][c]
        current = draw["result"]
        assert m.reproduce(current, current, draw["weights"], draw["weights"])["status"] == "PASS"
        wrong = {c: list(w) for c, w in draw["weights"].items()}
        wrong["Guayacan"][0] += 1
        with pytest.raises(m.p.QualificationError, match="multiplicity"):
            m.reproduce(current, current, wrong, draw["weights"])
    broken = {**current, "predictions": {**current["predictions"], "E3": [x+1e-8 for x in current["predictions"]["E3"]]}}
    with pytest.raises(m.p.QualificationError, match="reproduction"):
        m.reproduce(broken, current)


def test_deletions_remove_both_roles(records):
    result = m.deletion_analysis(records, m.evaluate(records))
    assert len(result["results"]) == 32
    for deletion in result["results"]:
        for fold in deletion["result"]["folds"]:
            for identity in fold["training"]+fold["evaluation"]:
                assert (identity != deletion["deleted"] if deletion["kind"] == "record"
                        else identity[1] != deletion["deleted"])
        assert all(len(x) == len(deletion["retained"]) for x in deletion["result"]["predictions"].values())


def test_raw_extrapolation_and_feature_specific_support(records):
    train = records[:10]
    x = m.surface_features(train)
    z = 1+x @ [-2, 1.3]
    train = [replace(r, k=float(k)) for r, k in zip(train, m.p.checked_k(z))]
    held = [replace(records[10], s=1e2, phi=.8)]
    pred, _ = m.fit_s3(train, held, np.ones(10))
    assert pred[0] == pytest.approx(1+float(m.surface_features(held)[0] @ [-2, 1.3]))
    assert pred[0] > max(z)
    point = m.evaluate(records)
    rows = m.prediction_rows(records, point)
    for row in rows:
        expected = {"s", "phi"} if row["arm"] == "S3" else {"R", "phi"} if row["arm"] != "N" else set()
        assert set(row["source_feature_ranges"]) == set(row["marginal_extrapolation_flags"]) == expected


def test_rank_zero_weights_and_failed_draw_counts(records):
    with pytest.raises(m.p.QualificationError, match="rank"):
        m.fit_s3(records[:10], records[10:], np.r_[1., 1., np.zeros(8)])
    with pytest.raises(m.p.QualificationError, match="weights"):
        m.fit_s3(records[:10], records[10:], np.zeros(10))
    with pytest.raises(m.p.QualificationError, match="scale"):
        m.fit_s3([replace(r, s=m.S0) for r in records[:10]], records[10:], np.ones(10))
    saved = []
    def fail(rows, weights):
        raise m.p.QualificationError("required S3 failure")
    result = m.p.bootstrap(records, evaluator=fail, sink=saved.append)
    assert result["counts"] == dict(requested=2000, completed=0, failed=1, unattempted=1999)
    assert saved[0]["weights"] == result["failure"]["weights"]
    assert m.p.contrast(1, 0)["gain"] is None
    for z in ([np.nan], [np.inf], [1e5], [-1e5]):
        with pytest.raises(m.p.QualificationError):
            m.p.checked_k(z)


def test_preference_requires_all_comparators_and_both_directions():
    point = dict(scores={arm: {c: {"log_rmse": .5 if arm == "S3" else 1.} for c in m.COFFEES} for arm in m.ARMS})
    intervals = {b: [-.8, -.1] for b in m.COMPARATORS}
    assert m.preference(point, intervals)["qualification"] == "S3_CONDITIONAL_PREFERENCE"
    intervals["N"] = [-.5, .1]
    assert m.preference(point, intervals)["qualification"] == "SURFACE_REPRESENTATION_PREFERENCE_UNRESOLVED"
    intervals["W3"] = [.1, .3]
    assert m.preference(point, intervals)["resolved_better_comparators"] == ["W3"]
    assert m.preference(point, intervals)["qualification"] == "SURFACE_REPRESENTATION_NOT_SELECTED"
    assert m.preference(point, intervals, complete=False)["qualification"] == "INCOMPLETE"
    intervals = {b: [-.8, -.1] for b in m.COMPARATORS}
    point["scores"]["S3"]["Guayacan"]["log_rmse"] = 2.
    assert m.preference(point, intervals)["direction_dependence"]
    assert m.preference(point, intervals)["qualification"] == "SURFACE_REPRESENTATION_PREFERENCE_UNRESOLVED"
    assert m.decision([-.1, 0]) == m.decision([0, .1]) == "SURFACE_RADIUS_COMPARISON_UNRESOLVED"
    assert m.decision([-.2, -.1]) == "S3_LOWER_CONDITIONAL_LOG_LOSS_THAN_E3"

"""Synthetic numerical, pairing, authority and decision risks; no real fitting."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import wadsworth_percolation_kc_transfer as m


@pytest.fixture
def records():
    rng = np.random.default_rng(719)
    rows = []
    for coffee in m.COFFEES:
        for g in range(1, 12):
            if (coffee, g) == ("Guayacan", 2):
                continue
            phi, surface = float(rng.uniform(.25, .75)), float(rng.uniform(1e4, 5e4))
            z = 1-2*np.log(surface/m.S0)+3*np.log(phi)+rng.normal(0, .2)
            rows.append(m.s.Record(coffee, g, .0002+g*.00001, phi, float(m.K0*np.exp(z)), 0, surface))
    return rows


def test_source_connected_columns_missingness_and_pins():
    root = Path(__file__).resolve().parents[1]
    rows = m.s.load_table(root/m.p.SOURCE)
    assert len(rows) == 21 and rows[0].s == 33588.43 and rows[0].phi == .4792
    assert rows[0].s != 40384.06
    assert [r.identity for r in rows].count(["Guayacan", 2]) == 0
    assert m.p.sha(m.p.canonical([r.identity for r in rows])) == m.s.PARENT_MEMBERSHIP
    assert m.p.sha(m.p.canonical([m.asdict(r) for r in rows])) == m.OBSERVATIONS


def test_pinned_authority_precedes_manifest(tmp_path):
    (tmp_path/"FREEZE.json").write_text("{}")
    (tmp_path/"RESULT.json").write_text("{}")
    with pytest.raises(m.p.QualificationError, match="FREEZE identity"):
        m.authenticate_pr382(tmp_path, tmp_path, [])


@pytest.mark.parametrize("arm", m.ARMS)
def test_weights_replication_freedom_qr(records, arm):
    weights = np.array([0, 2, 1, 3, 1, 0, 2, 1, 2, 1])
    first, diag = m.fit(records[:10], records[10:], arm, weights)
    literal = [r for r, n in zip(records[:10], weights) for _ in range(n)]
    second, repeated = m.fit(literal, records[10:], arm, np.ones(len(literal)))
    np.testing.assert_allclose(first, second, rtol=0, atol=1e-12)
    assert diag["coefficient_count"] == (3 if arm == "S3" else 1)
    assert diag["training_sse"] == pytest.approx(repeated["training_sse"], abs=1e-12)
    assert diag["qr_max_log_difference"] < 1e-10


def test_shape_identity_normalization_and_response_cancellation(records):
    train, held = records[:10], records[10:]
    weights = np.arange(10)
    predictions = {}
    for arm in ("PER1", "KC1"):
        predictions[arm], _ = m.fit(train, held, arm, weights)
        shifted, _ = m.fit(train, held, arm, weights, normalization_shift=7.)
        np.testing.assert_allclose(shifted, predictions[arm], atol=1e-12, rtol=0)
    expected = m.phi_difference(held)-np.average(m.phi_difference(train), weights=weights)
    np.testing.assert_allclose(predictions["PER1"]-predictions["KC1"], expected, atol=1e-12, rtol=0)
    changed = [replace(r, k=r.k*(1+r.G), s=r.s*(1+.1*r.G)) for r in records]
    delta = m.fit(changed[:10], changed[10:], "PER1", weights)[0]-m.fit(changed[:10], changed[10:], "KC1", weights)[0]
    np.testing.assert_allclose(delta, expected, atol=1e-12, rtol=0)


def test_training_only_transforms_and_nesting(records):
    point = m.evaluate(records)
    changed = m.evaluate([replace(r, k=r.k*9) if r.coffee == "Tumba" else r for r in records])
    assert point["diagnostics"]["Guayacan"] == changed["diagnostics"]["Guayacan"]
    for coffee in m.COFFEES:
        d = point["diagnostics"][coffee]
        for other in ("KC1", "N"):
            assert d["S3"]["training_sse"] <= d[other]["training_sse"]+1e-12
    assert m.p.ARMS == ("W3", "E3", "N") and m.s.ARMS == ("S3", "E3", "W3", "N")
    assert all(len(v) == 21 for v in point["predictions"].values())


def test_zero_weights_rank_finite_failures(records):
    for arm in m.ARMS:
        for w in (np.zeros(10), np.full(10, np.nan), np.full(10, -1)):
            with pytest.raises(m.p.QualificationError):
                m.fit(records[:10], records[10:], arm, w)
    with pytest.raises(m.p.QualificationError, match="rank"):
        m.fit(records[:10], records[10:], "S3", np.r_[1., 1., np.zeros(8)])
    with pytest.raises(m.p.QualificationError):
        m.fit([replace(r, k=np.inf) for r in records[:10]], records[10:], "N", np.ones(10))
    for z in ([np.nan], [1e6], [-1e6]):
        with pytest.raises(m.p.QualificationError):
            m.p.checked_k(z)


def test_pairing_zero_weight_predictions_and_failure_accounting(records):
    boot = m.p.bootstrap(records, n=3, evaluator=m.evaluate)
    assert boot["counts"] == dict(requested=3, completed=3, failed=0, unattempted=0)
    for draw in boot["draws"]:
        for c in m.COFFEES:
            source = next(x for x in draw["result"]["folds"] if x["source"] == c)
            target = next(x for x in draw["result"]["folds"] if x["target"] == c)
            assert source["training_weights"] == target["evaluation_weights"] == draw["weights"][c]
        assert all(len(x) == 21 for x in draw["result"]["predictions"].values())
    saved = []
    def failure(rows, weights):
        raise m.p.QualificationError("required failure")
    failed = m.p.bootstrap(records, evaluator=failure, sink=saved.append)
    assert failed["counts"] == dict(requested=2000, completed=0, failed=1, unattempted=1999)
    assert failed["failure"] == saved[0]


def test_reproduction_local_retained_arms(records):
    point = m.evaluate(records)
    assert m.reproduce_point(point, point)["status"] == "PASS"
    changed = {**point, "predictions": {**point["predictions"], "S3": [v+1e-8 for v in point["predictions"]["S3"]]}}
    with pytest.raises(m.p.QualificationError, match="prediction reproduction"):
        m.reproduce_point(changed, point)
    boot = m.p.bootstrap(records, n=3, evaluator=m.evaluate)
    scores, context = m.summarize(point, boot["draws"], context=True)
    parent = dict(scores=scores, contrasts=context)
    assert m.reproduce_summaries(scores, context, parent)["status"] == "PASS"


def test_metrics_reverse_orientation_grades_boundaries(records):
    point = m.evaluate(records)
    boot = m.p.bootstrap(records, n=3, evaluator=m.evaluate)
    for arm in m.ARMS:
        x = point["scores"][arm]
        assert x["aggregate"]["log_rmse"] == pytest.approx(np.sqrt(sum(x[c]["log_rmse"]**2 for c in m.COFFEES)/2))
    forward = m.oriented_contrast(point, boot["draws"], "PER1", "KC1", "log_rmse")
    reverse = m.oriented_contrast(point, boot["draws"], "KC1", "PER1", "log_rmse")
    np.testing.assert_allclose(reverse["delta_ci"], [-forward["delta_ci"][1], -forward["delta_ci"][0]])
    assert reverse["point"]["gain"] == pytest.approx(-forward["point"]["gain"]/(1-forward["point"]["gain"]))
    _, rows = m.summarize(point, boot["draws"])
    assert all(len(x["boundary_sensitivity"]) == 9 for x in rows if x["kind"] == "gain")
    assert m.p.grade_interval([-.1,.1]) == ["worse", "small", "moderate"]
    assert m.p.interval([.1, None, .2]) is None
    assert m.p.contrast(1., 0.)["gain"] is None


def test_refuse_preference_for_primary_only():
    scores = {a: {c: {"log_rmse": v} for c in (*m.COFFEES, "aggregate")}
              for a, v in zip(m.ARMS, (.8, 1., .7, .6))}
    point = dict(scores=scores)
    decision = m.decisions(point, [dict(result=point)]*3)
    assert decision["primary"] == "PER1_LOWER_CONDITIONAL_LOG_LOSS_THAN_KC1"
    assert decision["preference"] == "NO_PUBLISHED_SHAPE_CONDITIONAL_PREFERENCE"
    assert decision["shapes"]["PER1"]["resolved_adverse_comparators"] == ["N", "S3"]
    assert m.decisions(point, [], complete=False)["preference"] == "INCOMPLETE"


def test_deletions_remove_both_roles(records):
    result = m.deletion_analysis(records, m.evaluate(records))
    assert len(result["results"]) == 32
    for item in result["results"]:
        for fold in item["result"]["folds"]:
            for identity in fold["training"]+fold["evaluation"]:
                assert identity != item["deleted"] if item["kind"] == "record" else identity[1] != item["deleted"]

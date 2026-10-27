"""Synthetic numerical checks; real table is read only for cohort qualification."""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from puckworks.analysis import wadsworth_held_coffee_permeability as m

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def records():
    rng = np.random.default_rng(141)
    rows = []
    for c in m.COFFEES:
        for g in range(1, 12):
            if c == "Guayacan" and g == 2:
                continue
            radius = (0.2 + g * 0.05) * m.R0
            phi = float(rng.uniform(.3, .7))
            z = .5 - .8 * np.log(radius/m.R0) + 1.1*np.log(phi) + rng.normal(0, .1)
            rows.append(m.Record(c, g, radius, phi, float(m.K0*np.exp(z)), 0.0))
    return rows


def test_exact_bytes_cohort_missingness_and_units(tmp_path):
    rows = m.load_table(ROOT/m.SOURCE)
    assert len(rows) == 21
    assert [sum(r.coffee == c for r in rows) for c in m.COFFEES] == [10, 11]
    assert [r.identity for r in rows] == [[c, g] for c in m.COFFEES for g in range(1, 12)
                                          if (c, g) != ("Guayacan", 2)]
    assert rows[0].R == .000211  # Radius, not diameter.
    assert rows[0].phi == .4792  # Connected, not total .5014.
    assert min(r.k for r in rows) == 1.58e-11
    assert max(r.k for r in rows) == 1.91e-10
    altered = tmp_path/"normalized.csv"
    altered.write_bytes((ROOT/m.SOURCE).read_bytes().replace(b"\r\n", b"\n"))
    with pytest.raises(m.QualificationError, match="byte/hash"):
        m.load_table(altered)


def test_oof_coverage_and_held_out_response_independence(records):
    original = m.evaluate(records)
    changed = [replace(r, k=r.k*12, k_err=1e6) if r.coffee == "Tumba" else r for r in records]
    perturbed = m.evaluate(changed)
    for arm in m.ARMS:
        assert len(original["predictions"][arm]) == 21
        assert np.all(np.isfinite(original["predictions"][arm]))
    for d, e in zip(original["diagnostics"][:3], perturbed["diagnostics"][:3]):
        assert d == e  # Target outcome/error cannot enter the Guayacan-trained fit.
    targets = [x for fold in original["folds"] for x in fold["evaluation"]]
    assert len(targets) == len({tuple(x) for x in targets}) == 21


def test_equal_coffee_not_pooled_or_mean_rmse(records):
    truth = np.log([r.k/m.K0 for r in records])
    errors = np.array([1 if r.coffee == "Guayacan" else 3 for r in records])
    weights = {"Guayacan": np.ones(10), "Tumba": np.ones(11)}
    result = m.score(records, truth+errors, weights)
    assert result["aggregate"]["log_rmse"] == pytest.approx(np.sqrt(5))
    assert result["aggregate"]["log_rmse"] != pytest.approx(np.sqrt(np.mean(errors**2)))
    assert result["aggregate"]["log_rmse"] != pytest.approx(2)
    assert result["aggregate"]["log_bias"] == pytest.approx(2)


@pytest.mark.parametrize("arm", m.ARMS)
def test_weighted_replicated_rows_and_independent_solvers(records, arm):
    train, target = records[:10], records[10:]
    w = np.array([0, 2, 1, 3, 1, 0, 2, 1, 2, 1])
    pred, d = m.fit(train, target, arm, w)
    replicated = [r for r, count in zip(train, w) for _ in range(count)]
    other, e = m.fit(replicated, target, arm, np.ones(len(replicated)))
    np.testing.assert_allclose(pred, other, atol=1e-12, rtol=1e-12)
    assert d["training_sse"] == pytest.approx(e["training_sse"], abs=1e-12)
    assert d["qr_max_log_difference"] < 1e-10


def test_one_vector_for_both_roles_and_stable_streams(records):
    boot = m.bootstrap(records, n=4)
    streams = [np.random.default_rng(s) for s in np.random.SeedSequence(20261027).spawn(2)]
    for draw in boot["draws"]:
        for coffee, size, stream in zip(m.COFFEES, (10, 11), streams):
            expected = np.bincount(stream.integers(0, size, size=size), minlength=size).tolist()
            assert draw["weights"][coffee] == expected
            training = next(f for f in draw["result"]["folds"] if f["source"] == coffee)
            held = next(f for f in draw["result"]["folds"] if f["target"] == coffee)
            assert training["training_weights"] == held["evaluation_weights"] == expected
    assert boot["counts"] == dict(requested=4, completed=4, failed=0, unattempted=0)


def test_both_role_deletions(records):
    point = m.evaluate(records)
    deleted = m.deletion_analysis(records, point)
    assert len(deleted["results"]) == 32
    for d in deleted["results"]:
        assert len(d["retained"]) == (20 if d["kind"] == "record" or d["deleted"] == 2 else 19)
        for fold in d["result"]["folds"]:
            for identity in fold["training"] + fold["evaluation"]:
                assert (identity != d["deleted"] if d["kind"] == "record" else identity[1] != d["deleted"])


def test_rank_failure_and_failed_draw_accounting(records):
    weights = np.r_[1., 1., np.zeros(8)]
    with pytest.raises(m.QualificationError, match="rank") as caught:
        m.fit(records[:10], records[10:], "E3", weights)
    assert caught.value.diagnostics["rank"] == 2
    assert len(caught.value.diagnostics["singular_values"]) == 2
    seen = []

    def fail_second(rows, weights):
        if len(seen) == 1:
            raise m.QualificationError("rank fixture")
        return m.evaluate(rows, weights)

    boot = m.bootstrap(records, n=2000, evaluator=fail_second, sink=seen.append)
    assert boot["counts"] == dict(requested=2000, completed=1, failed=1, unattempted=1998)
    assert boot["failure"]["reason"] == "rank fixture"
    assert boot["failure"]["weights"] == seen[1]["weights"]
    assert len(seen) == 2


def test_raw_extrapolation_and_nonphysical_coefficients(records):
    train = records[:10]
    x, offset = m.predictors(train, "W3")
    z = offset + np.column_stack((np.ones(10), x)) @ np.array([-3., -2., -1.])
    train = [replace(r, k=float(k)) for r, k in zip(train, m.checked_k(z))]
    target = [replace(records[10], R=.002, phi=.8)]
    pred, d = m.fit(train, target, "W3", np.ones(10))
    tx, to = m.predictors(target, "W3")
    assert pred[0] == pytest.approx(float(to[0] - 3 + tx[0] @ [-2., -1.]))
    assert d["a_negative"] and d["b_nonpositive"]
    assert pred[0] > max(z)  # No clipping at the training range.


@pytest.mark.parametrize("z", [[np.nan], [np.inf], [1e5], [-1e5]])
def test_nonfinite_or_unrepresentable_predictions(z):
    with pytest.raises(m.QualificationError):
        m.checked_k(z)


def test_zero_reference_boundaries_and_percentiles():
    assert m.contrast(1, 0) == dict(delta=1, gain=None)
    assert m.interval([None, 1]) is None
    assert m.grade(None) == "undefined"
    assert m.grade_interval([0, .1]) == ["small", "moderate"]
    assert m.grade_interval([-.1, 0]) == ["worse", "small"]
    assert m.decision([-1, 0]) == m.decision([0, 1]) == "HELD_COFFEE_COMPARISON_UNRESOLVED"
    assert m.decision(None) == "INCOMPLETE"
    assert m.interval(list(range(100))) == pytest.approx([2.475, 96.525])


def test_invalid_weights_and_scale(records):
    for w in (np.zeros(10), -np.ones(10), np.full(10, np.nan)):
        with pytest.raises(m.QualificationError, match="weight"):
            m.fit(records[:10], records[10:], "E3", w)
    constant = [replace(r, R=.0005) for r in records[:10]]
    with pytest.raises(m.QualificationError, match="scale"):
        m.fit(constant, records[10:], "E3", np.ones(10))


def test_missing_input_preserves_not_attempted_counts(tmp_path):
    result = m.run(tmp_path/"missing_checkout", tmp_path/"private")
    assert result["status"] == "INCOMPLETE"
    assert result["decision"] == "INCOMPLETE"
    assert result["counts"] == dict(requested=2000, completed=0, failed=0, unattempted=2000)
    assert (tmp_path/"private"/"RESULT.json").exists()

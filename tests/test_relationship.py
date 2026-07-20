"""Relationship analyzer for educational tour figures (#43).

Offline. Classifies a 1-D computed curve so captions state the relationship the model ACTUALLY produced
and a one-grid-point wobble is never mislabelled a physical reversal.
"""
from puckworks.viz.relationship import classify_relationship as C
from puckworks.viz.relationship import describe


def test_increasing():
    r = C([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    assert r.classification == "increasing" and r.total_change == 4


def test_decreasing():
    assert C([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]).classification == "decreasing"


def test_approximately_flat():
    # small wiggles on a large baseline are flat, not a reversal
    assert C([1, 2, 3, 4, 5], [3.0, 3.01, 2.99, 3.0, 3.02]).classification == "approximately_flat"


def test_noisy_but_monotonic():
    assert C([1, 2, 3, 4, 5, 6], [1, 1.05, 1.9, 2.0, 2.95, 4.0]).classification == "increasing"


def test_genuine_turning_point():
    r = C([1, 2, 3, 4, 5, 6, 7], [1, 3, 5, 6, 5, 3, 1])
    assert r.classification == "non_monotonic"
    assert r.direction_before == "increasing" and r.direction_after == "decreasing"
    assert r.turning_x == 4.0 and r.y_turning == 6


def test_spurious_one_point_wobble_is_not_a_turning_point():
    # a single tiny down-step in an otherwise-rising curve must NOT become a physical reversal
    r = C([1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 3.02, 5, 6, 7])
    assert r.classification == "increasing" and r.turning_x is None


def test_invalid_or_insufficient_data():
    assert C([1, 2, float("nan")], [1, float("nan"), 3]).classification == "insufficient"
    assert C([1], [1]).classification == "insufficient"
    assert C([1, 2], [1, 2]).classification == "insufficient"


def test_describe_inserts_recomputed_values():
    r = C([5, 7, 9, 11], [15.59, 14.76, 14.11, 13.57])
    assert r.classification == "decreasing"
    text = describe(r, "extraction yield", "pressure", "%")
    assert "15.6" in text and "13.6" in text and "falls" in text


def test_tolerance_controls_flatness():
    # a 1% trend reads as flat under a 2% tolerance but as a trend under a tight tolerance
    y = [100.0, 100.4, 100.8, 101.2]
    assert C([1, 2, 3, 4], y, rel_tol=0.02).classification == "approximately_flat"
    assert C([1, 2, 3, 4], y, rel_tol=0.001).classification == "increasing"

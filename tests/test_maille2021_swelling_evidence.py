"""Analytical controls for a restricted graphical invariant test, not science validation."""
from fractions import Fraction as F

import pytest

from puckworks.analysis.maille2021_swelling_evidence import (
    EXCLUDED, INSUFFICIENT, NOT_EXCLUDED, intersection, invariant_bounds, linear_bounds,
)


def test_common_scaling_preserves_both_invariants():
    # Fixed number, common shape-preserving scale: every volume scales cubically.
    rows_r, rows_k = [], []
    for scale in (F(1), F(3, 2), F(2)):
        median, upper, concentration = 2*scale, 5*scale, F(1, 100)*scale**3
        rows_r.append((str(scale), invariant_bounds((upper, upper), (median, median))))
        rows_k.append((str(scale), invariant_bounds(
            (concentration, concentration), (median, median), 3)))
    assert intersection(rows_r)["intersection"] == (F(5, 2), F(5, 2))
    assert intersection(rows_k)["intersection"] == (F(1, 800), F(1, 800))


def test_linear_concentration_change_does_not_obey_cubic_scaling():
    rows = [("early", invariant_bounds((1, 1), (1, 1), 3)),
            ("late", invariant_bounds((2, 2), (2, 2), 3))]
    result = intersection(rows)
    assert result["status"] == EXCLUDED
    assert result["certificate"]["strict_gap"] == F(3, 4)


def test_contact_is_not_exclusion_and_missing_support_is_visible():
    assert intersection([("a", (F(1), F(2))), ("b", (F(2), F(3)))])["status"] == NOT_EXCLUDED
    result = intersection([("a", (F(1), F(2))), ("missing", None)])
    assert result["status"] == INSUFFICIENT
    assert (result["supported"], result["required"]) == (1, 2)
    for invalid in ((0, 1), (-1, 1), (2, 1)):
        assert invariant_bounds((1, 2), invalid, 3) is None


def test_shared_calibration_outer_bounds_include_interior_realizations():
    axis = {"pixels": [100, 0], "values": [0, 1]}
    lo, hi = linear_bounds(50, axis, 4, 1)
    assert (lo, hi) == (F(45, 100), F(55, 100))
    # One calibration, two markers: dependence is allowed, not sampled as lab noise.
    for a, b in ((F(199, 2), F(1, 2)), (F(201, 2), F(-1, 2))):
        for pixel in (F(93, 2), F(100, 2), F(107, 2)):
            assert lo <= (pixel-a)/(b-a) <= hi
    with pytest.raises(ValueError, match="crossing"):
        linear_bounds(1, {"pixels": [0, 1], "values": [0, 1]}, 1, 1)


def test_distribution_shape_change_can_fail_ratio_without_concentration_test():
    rows = [("a", invariant_bounds((2, 2), (1, 1))),
            ("b", invariant_bounds((3, 3), (1, 1)))]
    assert intersection(rows)["status"] == EXCLUDED

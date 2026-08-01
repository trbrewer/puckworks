"""The local inventory–rate separability result (scientific-pivot plan §5).

The whole value of this module is that the criterion is EXACT for the declared factorisation, so
the tests check the algebra against independent constructions rather than against remembered
numbers. A separability index that merely counted observations, or that could not detect a
perfectly collinear design, would be worse than no diagnostic at all.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import separability as SEP  # noqa: E402


# ── 1. the exact identity ────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("seed", range(8))
def test_det_gram_equals_total_weight_times_weighted_scatter(seed):
    """det(G) = (sum w) * sum w (s - sbar)^2, checked against a direct determinant."""
    rng = np.random.default_rng(seed)
    n = int(rng.integers(2, 30))
    s = rng.normal(0.0, rng.uniform(0.1, 3.0), n)
    w = rng.uniform(0.05, 5.0, n)

    out = SEP.separability(s, w)
    assert out["det_gram"] == pytest.approx(out["det_from_variance_identity"], rel=1e-9, abs=1e-12)

    # ...and against the (sum w)^2 * Var_w(s) form the plan states.
    sbar = float(np.sum(w * s) / np.sum(w))
    var_w = float(np.sum(w * (s - sbar) ** 2) / np.sum(w))
    assert out["det_gram"] == pytest.approx(np.sum(w) ** 2 * var_w, rel=1e-9)


def test_rsi_is_the_weighted_standard_deviation_of_the_sensitivities():
    s = np.array([0.1, 0.4, 0.9, 1.6])
    out = SEP.separability(s)
    assert out["rsi"] == pytest.approx(float(np.std(s)), rel=1e-12)
    assert out["rsi_total"] == pytest.approx(float(np.std(s)) * np.sqrt(len(s)), rel=1e-12)


def test_uniform_sensitivities_are_exactly_inseparable():
    """The central claim: identical proportional response => the rate is locally unidentifiable,
    no matter how many observations are collected.

    The tolerance on the direct determinant is scaled by the matrix magnitude because
    ``np.linalg.det`` cancels two large products here: at n=1000 with s=0.7 the entries are ~1000
    and ~490, and the residual is ~3e-9 in absolute terms. The variance identity stays at ~1e-26 —
    see the companion test below, which is why the identity form is what the module reports.
    """
    for n in (2, 10, 1000):
        out = SEP.separability(np.full(n, 0.7))
        assert out["rsi"] == pytest.approx(0.0, abs=1e-12)
        assert abs(out["det_from_variance_identity"]) <= 1e-20 * n ** 2
        assert abs(out["det_gram"]) <= 1e-11 * n ** 2
        assert out["column_cosine"] == pytest.approx(1.0, rel=1e-12)
        assert out["smallest_singular_value"] == pytest.approx(0.0, abs=1e-9 * n)


def test_the_variance_identity_is_better_conditioned_than_the_direct_determinant():
    """Not a style preference: on a collinear design the direct determinant loses all its digits.

    det(G) subtracts (sum w s)^2 from (sum w)(sum w s^2) — two quantities that agree to full
    precision when the design is degenerate, which is exactly the case the diagnostic exists to
    detect. The variance form never forms that difference.
    """
    out = SEP.separability(np.full(4000, 0.7))
    assert abs(out["det_gram"]) > 0.0, (
        "if this ever becomes exactly zero the numerical argument above is stale, not wrong — "
        "re-check before deleting the identity form")
    # ~17 orders of magnitude, not a marginal preference.
    assert abs(out["det_from_variance_identity"]) < 1e-12 * abs(out["det_gram"])


def test_a_single_observation_can_never_separate_the_two_parameters():
    """Two unknowns, one observation — the diagnostic must say so rather than divide by zero."""
    out = SEP.separability(np.array([1.3]))
    assert out["rsi"] == pytest.approx(0.0, abs=1e-12)
    assert out["det_gram"] == pytest.approx(0.0, abs=1e-12)


def test_separability_is_invariant_to_a_common_shift_in_sensitivity():
    """Only the SPREAD carries information; a shift is absorbed by the level.

    This is the formal content of "the level competes with the rate", and it is why the paper can
    say more observations of the same kind do not help.
    """
    s = np.array([0.2, 0.5, 1.1])
    base = SEP.separability(s)["rsi"]
    for shift in (-5.0, 0.3, 12.0):
        assert SEP.separability(s + shift)["rsi"] == pytest.approx(base, rel=1e-12)


def test_replicating_a_design_leaves_rsi_alone_but_raises_total_rsi():
    """The two indices must answer different questions, or reporting both is noise."""
    s = np.array([0.2, 0.9, 1.4])
    one, three = SEP.separability(s), SEP.separability(np.tile(s, 3))
    assert three["rsi"] == pytest.approx(one["rsi"], rel=1e-12)
    assert three["rsi_total"] == pytest.approx(one["rsi_total"] * np.sqrt(3), rel=1e-12)


def test_zero_weights_drop_observations_exactly():
    s = np.array([0.1, 0.5, 9.9])
    w = np.array([1.0, 1.0, 0.0])
    assert SEP.separability(s, w)["rsi"] == pytest.approx(SEP.separability(s[:2])["rsi"], rel=1e-12)


def test_negative_weights_are_rejected():
    with pytest.raises(ValueError):
        SEP.separability(np.array([0.1, 0.2]), np.array([1.0, -1.0]))


# ── 2. sensitivities from a response, with step convergence ──────────────────────────────────
def test_a_pure_power_law_response_has_exactly_known_sensitivities():
    """f_i(k) = k^p_i  =>  d log f / d log k = p_i, to finite-difference accuracy."""
    p = np.array([0.25, 0.5, 1.0, 2.0])
    got = SEP.log_rate_sensitivities(lambda k: k ** p, rate=1.7)
    assert np.allclose(got.s, p, atol=1e-6)
    assert got.converged


def test_a_rate_independent_response_reports_zero_separability():
    """The degenerate case the paper warns about, reached through the response path."""
    out = SEP.design_separability(lambda k: np.array([2.0, 3.0, 4.0]), rate=1.0)
    assert np.allclose(out["sensitivities"], 0.0, atol=1e-9)
    assert out["rsi"] == pytest.approx(0.0, abs=1e-9)


def test_step_convergence_is_reported_and_can_fail():
    """A response with structure far below the step must NOT be silently reported as converged."""
    smooth = SEP.log_rate_sensitivities(lambda k: k ** np.array([0.3, 1.2]), rate=1.0)
    assert smooth.converged

    def wiggly(k):
        return k ** np.array([0.3, 1.2]) * (1.0 + 0.5 * np.sin(400.0 * np.log(k)))

    assert not SEP.log_rate_sensitivities(wiggly, rate=1.0).converged


def test_non_positive_response_is_rejected_rather_than_producing_nan():
    with pytest.raises(ValueError):
        SEP.log_rate_sensitivities(lambda k: np.array([1.0, -1.0]), rate=1.0)


def test_sensitivities_are_recorded_at_every_step_for_audit():
    got = SEP.log_rate_sensitivities(lambda k: k ** np.array([0.4, 0.9]), rate=1.0)
    assert len(got.per_step) == len(SEP.STEP_MULTIPLIERS)


# ── 3. the admission tests the plan requires before RSI may enter the main paper ─────────────
def test_profile_agreement_detects_the_expected_sign():
    """Higher separability with narrower profiles => negative rank correlation."""
    rsi = {"a": 0.1, "b": 0.4, "c": 0.9, "d": 1.5}
    width = {"a": 3.0, "b": 2.0, "c": 1.0, "d": 0.4}          # monotonically narrowing
    out = SEP.agreement_with_profiles(rsi, width)
    assert out["spearman"] == pytest.approx(-1.0, abs=1e-9)
    assert out["consistent_with_expectation"]


def test_profile_agreement_reports_disagreement_rather_than_hiding_it():
    """If local geometry fails to predict the nonlinear profile, that must surface as a result."""
    rsi = {"a": 0.1, "b": 0.4, "c": 0.9, "d": 1.5}
    width = {"a": 0.4, "b": 1.0, "c": 2.0, "d": 3.0}          # wrong way round
    out = SEP.agreement_with_profiles(rsi, width)
    assert out["spearman"] > 0
    assert not out["consistent_with_expectation"]


def test_profile_agreement_refuses_to_report_on_too_few_designs():
    out = SEP.agreement_with_profiles({"a": 1.0, "b": 2.0}, {"a": 1.0, "b": 2.0})
    assert out["spearman"] is None


def test_rsi_is_not_a_restatement_of_observation_count():
    """Designs with MORE observations but redundant sensitivities must score LOWER."""
    many_redundant = np.full(50, 0.8) + np.array([1e-9] * 50)
    few_diverse = np.array([0.1, 1.9])
    assert SEP.separability(few_diverse)["rsi"] > SEP.separability(many_redundant)["rsi"]

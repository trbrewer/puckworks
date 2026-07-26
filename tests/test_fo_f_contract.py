"""Forchheimer-number contract: the manuscript-facing formula IS the registered implementation.

Paper 3 review P0-1. The manuscript printed `Fo_F = k_I*rho*|u|/mu`, which omits the Darcy
permeability `k` and inverts `k_I`. That was a manuscript-only transcription error -- the registered
component always computed the form implied by its own momentum law -- but nothing pinned the two
together, so the paper and the code could disagree silently about a quantity the flow-regime argument
rests on. These tests close that gap by rederiving the diagnostic from the momentum law and by
recording the exact inputs behind the reported named-shot range.
"""
import numpy as np
import pytest

from puckworks.models.wadsworth2026 import inertial as W

# The equation as printed in the manuscript (§4.4), transcribed here INDEPENDENTLY of the module so
# the comparison is a real cross-check and not a restatement of the implementation.
MANUSCRIPT_FORMULA = "Fo_F = rho * k * |q| / (mu * k_I)"


def _manuscript_fo_f(rho, k, q, mu, k_I):
    return rho * k * abs(q) / (mu * k_I)


def test_fo_f_manuscript_formula_matches_the_implementation():
    """THE contract. Independently written manuscript formula == registered producer, across a
    grid spanning the espresso range, not one lucky fixture."""
    for k in (1e-15, 7.4e-15, 5e-14):
        for q in (2e-4, 5.36e-4, 1.54e-3):
            for closure in ("zhou", "exp"):
                kI = W.k_I(k, closure)
                got = float(W.forchheimer_number(k, q, kI))
                want = _manuscript_fo_f(W.RHO_92C, k, q, W.MU_92C, kI)
                assert got == pytest.approx(want, rel=1e-12), (k, q, closure, got, want)


def test_fo_f_is_the_inertial_over_viscous_drag_ratio_of_the_momentum_law():
    """Derive the diagnostic from `grad_p = -(mu/k) q - (rho/k_I) |q| q` rather than asserting the
    algebra: the ratio of the two drag terms must equal Fo_F. This is what makes the OLD manuscript
    form detectably wrong (it omitted k and inverted k_I) rather than merely different."""
    k, q, kI = 7.4e-15, 1.54e-3, W.k_I(7.4e-15, "exp")
    viscous = (W.MU_92C / k) * q
    inertial = (W.RHO_92C / kI) * abs(q) * q
    assert inertial / viscous == pytest.approx(float(W.forchheimer_number(k, q, kI)), rel=1e-12)


def test_the_retired_manuscript_form_is_genuinely_different():
    """Guard against 'it was only a rearrangement'. The retired form disagrees by orders of
    magnitude AND moves the wrong way with k_I, which is why it could not be left uncorrected."""
    k, q = 7.4e-15, 1.54e-3
    kI_lo, kI_hi = W.k_I(k, "exp"), W.k_I(k, "exp") * 10.0
    correct_lo = float(W.forchheimer_number(k, q, kI_lo))
    correct_hi = float(W.forchheimer_number(k, q, kI_hi))
    retired = lambda kI: kI * W.RHO_92C * q / W.MU_92C          # the printed (wrong) form
    # correct: raising k_I REDUCES the inertial ratio; retired: raising k_I RAISES it -> reversed
    assert correct_hi < correct_lo
    assert retired(kI_hi) > retired(kI_lo)
    # and the magnitudes are not close: the retired form is ~1e6 times smaller here, so the two
    # could never be mistaken for a rearrangement of one another
    assert correct_lo / retired(kI_lo) > 1e3


def test_named_shot_range_inputs_are_recorded_and_reproduce_the_reported_band():
    """Review P0-1 item 4: the reported ~0.86-5.7 band must be reproducible from recorded inputs
    with a declared velocity convention, not quoted from memory."""
    r = W.de1_fixtureA_audit()
    # velocity convention: SUPERFICIAL (Darcy) q = Q/A -- pinned, since the number depends on it
    assert r["q_peak_m_s"] == pytest.approx(1.53996e-3, rel=1e-3)
    assert r["k_m2"] == pytest.approx(7.41946e-15, rel=1e-3)
    assert W.RHO_92C == 960.0 and W.MU_92C == 3.0e-4
    assert r["Fo_F_max_exp"] == pytest.approx(0.857, rel=1e-2)
    assert r["Fo_F_max_zhou"] == pytest.approx(5.721, rel=1e-2)
    # and the band is reconstructable from those inputs alone
    for closure, reported in (("exp", r["Fo_F_max_exp"]), ("zhou", r["Fo_F_max_zhou"])):
        want = _manuscript_fo_f(W.RHO_92C, r["k_m2"], r["q_peak_m_s"], W.MU_92C,
                                W.k_I(r["k_m2"], closure))
        assert reported == pytest.approx(want, rel=1e-6)


def test_manuscript_prints_the_corrected_equation_and_the_velocity_convention():
    """Prose guard: the retired form must not reappear, and the velocity convention must be stated
    (the number is convention-dependent, so an unstated convention is not reproducible)."""
    import pathlib
    md = (pathlib.Path(__file__).resolve().parents[1]
          / "docs/PAPER_3_PUCKWORKS_DRAFT.md").read_text(encoding="utf-8")
    assert r"Fo_F = \rho\,k\,|q| / (\mu\,k_I)" in md
    assert "superficial (Darcy) velocity" in md
    # the retired form may appear ONLY inside the errata parenthetical that explains it
    assert md.count(r"k_I\rho|u|/\mu") <= 1

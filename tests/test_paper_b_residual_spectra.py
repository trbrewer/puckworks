"""Paper 2 review item 4.7 — residual diagnostics as a first-class result.

Lag-1 autocorrelation says the residuals are dependent. It cannot say whether they DRIFT or
OSCILLATE, and those mean different things about model adequacy: a slow excursion and a fast
wobble can produce similar lag-1 values. 4.7 asks for the ACF across lags and the spectra, which is
what distinguishes them.

These tests pin the finding and, more importantly, check the diagnostics could have come out the
other way — a spectrum estimator that reported "drift" for any input would be worthless here.
"""
import numpy as np
import pytest

from puckworks.analysis import waszkiewicz_shot_level as W


@pytest.fixture(scope="module")
def rd():
    return W.residual_diagnostics(resolution_s=1.0)


def test_every_branch_reports_acf_across_lags_and_a_spectrum(rd):
    for name, b in rd["branches"].items():
        assert len(b["acf_by_lag"]) >= 10, (name, len(b["acf_by_lag"]))
        assert b["spectrum"]["period_s"], name
        assert b["spectrum"]["dominant_period_s"] is not None, name


def test_residual_structure_is_drift_not_oscillation(rd):
    """The §5.2b finding. Every branch keeps most of its residual power at the slowest end."""
    for name, b in rd["branches"].items():
        share = b["spectrum"]["power_in_slowest_quarter"]
        assert share > 0.9, (name, share)


def test_the_temporal_branches_shed_the_slowest_component(rd):
    """The part the scalars do not show: static branches peak at the full window (a single
    unreversed drift); the temporal branches peak at half of it, so what they leave reverses
    within the shot."""
    br = rd["branches"]
    assert br["rung1_const"]["spectrum"]["dominant_period_s"] == pytest.approx(80.0, abs=0.1)
    assert br["rung3_static"]["spectrum"]["dominant_period_s"] == pytest.approx(80.0, abs=0.1)
    assert br["rung4_phi_of_t"]["spectrum"]["dominant_period_s"] == pytest.approx(40.0, abs=0.1)
    assert (br["rung4_phi_of_t"]["spectrum"]["dominant_period_s"]
            < br["rung1_const"]["spectrum"]["dominant_period_s"])


def test_the_spectrum_can_distinguish_oscillation_from_drift():
    """NON-VACUITY. If `_periodogram` reported "drift" for everything, the finding above would be
    an artefact of the estimator. A pure fast oscillation must NOT land in the slowest quarter."""
    n, dt = 80, 1.0
    t = np.arange(n) * dt

    drift = t - t.mean()                                  # monotone ramp
    fast = np.sin(2 * np.pi * t / 4.0)                    # 4 s period
    fast = fast - fast.mean()

    s_drift = W._periodogram(drift, dt)
    s_fast = W._periodogram(fast, dt)

    assert s_drift["power_in_slowest_quarter"] > 0.9, s_drift
    assert s_fast["power_in_slowest_quarter"] < 0.1, s_fast
    assert s_fast["dominant_period_s"] == pytest.approx(4.0, abs=0.5)


def test_the_acf_estimator_is_not_vacuous():
    """White noise must not look autocorrelated, and a ramp must."""
    rng = np.random.default_rng(0)
    noise = rng.normal(size=400)
    noise -= noise.mean()
    ramp = np.arange(400, dtype=float)
    ramp -= ramp.mean()

    assert abs(W._acf_by_lag(noise, 5)[0]) < 0.2
    assert W._acf_by_lag(ramp, 5)[0] > 0.9
    assert W._acf_by_lag(noise, 0) == []


def test_degenerate_inputs_do_not_raise():
    """A constant residual has no structure to report; it must return empty, not divide by zero."""
    flat = np.zeros(40)
    assert W._periodogram(flat, 1.0)["period_s"] == []
    assert W._acf_by_lag(flat, 5) == []
    assert W._periodogram(np.zeros(3), 1.0)["dominant_period_s"] is None


def test_the_manuscript_states_the_finding_with_the_computed_numbers(rd):
    import pathlib
    text = pathlib.Path("docs/PAPER_B2_TEMPORAL_DRAFT.md").read_text(encoding="utf-8")
    assert "5.2b Residual structure is drift, not oscillation" in text
    for value in ("0.957", "0.990", "0.954", "80 s", "40 s"):
        assert value in text, value
    assert "not yet built" in text, (
        "the manuscript must still say the residual figure is not drawn")

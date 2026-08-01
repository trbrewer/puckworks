"""The Schmieder complete cups are a reconstruction, and Stage 1 of the pivot plan depends on it.

The scientific-pivot plan makes "measured fractions versus measured complete cups" its highest-value
empirical analysis, on the premise that the published cups are an independent observation of the
same shots. They are not: they are the closed-form integral of the authors' exponential fit to the
fraction data.

These tests pin that finding, because it is the kind of result that quietly decays. If someone later
re-derives the cup column, or a future intake replaces Table S3, the premise could silently become
true or false again and a whole analysis arm would rest on it either way.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from tools import audit_schmieder_cup_provenance as A  # noqa: E402


@pytest.fixture(scope="module")
def result():
    return A.run()


def test_the_published_cups_are_the_integral_of_the_published_fit(result):
    """The headline finding, stated as an assertion rather than a paragraph."""
    assert result["verdict"] == "RECONSTRUCTED"
    assert result["n_compared"] == 432
    assert result["agreement"]["fraction_identical"] > 0.98


def test_agreement_is_orders_of_magnitude_tighter_than_the_reported_measurement_scatter(result):
    """This is the whole argument: an independent assay cannot agree this well.

    The campaign reports a mean cup reproducibility RSD of 2.5 %. The observed median difference is
    ~3e-5 %. Nothing that was separately weighed and assayed lands five orders of magnitude inside
    its own reproducibility.
    """
    median = result["agreement"]["median_relative_difference_percent"]
    assert median < 1e-3
    assert median < A.REPORTED_CUP_RSD_PERCENT / 1000.0


def test_every_exception_is_explained_by_a_duplicated_source_cell(result):
    """Otherwise the exceptions might be the genuinely-independent rows, and the verdict is mixed."""
    exceptions = result["exceptions"]
    assert exceptions["n"] == exceptions["n_in_runs_with_duplicated_source_cells"], (
        "an exception NOT attributable to source duplication would need explaining before the "
        "reconstruction verdict could be stated without qualification")


def test_duplicated_source_cells_are_reported_not_silently_tolerated(result):
    """Bit-identical masses across different physical cups are a source defect worth surfacing."""
    dups = result["duplicated_source_cells"]
    assert dups, "the audit must keep reporting these while they are present in the source"
    for d in dups:
        assert len(d["appears_as"]) > 1


def test_the_analysed_fractions_are_a_subsample_so_summation_could_not_have_produced_the_cup(result):
    """Explains WHY a fitted curve was integrated: fractions 4, 6, 8, 9 were never analysed."""
    cov = result["fraction_coverage"]
    assert cov["contiguous"] is False
    assert cov["analysed_fraction_indices"] == [1.0, 2.0, 3.0, 5.0, 7.0, 10.0]
    assert cov["median_analysed_mass_g"] < cov["largest_cup_endpoint_g"], (
        "the analysed fractions collect less mass than the largest cup endpoint, so the 1/3 brew "
        "ratio is an extrapolation of the fit rather than an aggregate of measurements")


def test_the_closed_form_matches_numerical_integration():
    """Guard the algebra itself, independently of the data."""
    from scipy.integrate import quad

    for c0, lam, M in ((7.52657, 14.5824, 20.0), (10.37012, 20.09653, 60.0), (1.0, 3.0, 1.0)):
        numeric = quad(lambda m: c0 * np.exp(-m / lam), 0.0, M)[0]
        assert A.integral_of_fit(c0, lam, M) == pytest.approx(numeric, rel=1e-10)


def test_a_genuinely_independent_column_would_be_detected():
    """The test must be able to return INDEPENDENT, or it is not a test.

    Perturb the published masses by the campaign's own reported RSD and confirm the verdict flips.
    Without this, `verdict == "RECONSTRUCTED"` could just mean the audit always says that.
    """
    records = A.compare()["records"]
    rng = np.random.default_rng(0)
    noisy = rng.normal(1.0, A.REPORTED_CUP_RSD_PERCENT / 100.0, len(records))
    diffs = np.array([abs(r["integral_of_fit_mg"] - r["published_mass_mg"] * n)
                      / (r["published_mass_mg"] * n) * 100.0
                      for r, n in zip(records, noisy)])
    assert (diffs < A.IDENTITY_TOLERANCE_PERCENT).mean() < 0.05, (
        "assay-scale noise must not look like arithmetic identity")
    assert float(np.median(diffs)) > 0.5


def test_the_archive_is_current():
    """The JSON other documents cite must match a fresh run."""
    assert A.main(["--check"]) == 0

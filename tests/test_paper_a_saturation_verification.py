"""Gate G3: the rate saturation is physical, not a solver floor.

H1 — that a whole cup at a matched endpoint cannot see the kinetics — rests entirely on the
predicted concentration going flat in the rate. A BDF solver that had quietly converged to a floor
would produce the same flat numbers, and two configurations of the same numerical path can agree
while both are wrong. So the finding is re-derived on an integrator that shares no time-stepping
machinery with BDF: the semi-discrete system is linear, so `expm(At)z0` is exact.

These tests pin the verification, not just its conclusion, because "we checked once" decays.
"""
from __future__ import annotations

import json
import pathlib
import sys

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ARCHIVE = REPO / "docs" / "paper1_resource" / "PAPER_A_SATURATION_VERIFICATION.json"


@pytest.fixture(scope="module")
def archive():
    if not ARCHIVE.exists():
        pytest.skip("run tools/paper_a_saturation_verification.py --write")
    return json.loads(ARCHIVE.read_text(encoding="utf-8"))


# ── 1. the approach is only valid if the system really is linear ─────────────────────────────
def test_the_production_rhs_is_exactly_linear(archive):
    """If `_rhs` were nonlinear, the matrix-exponential path would be solving a different model."""
    lin = archive["linearity_check"]
    assert lin["is_linear"] is True
    assert lin["max_relative_superposition_error"] < 1e-12


def test_the_rhs_is_linear_when_recomputed_live():
    """Re-derived rather than read from the archive, so a solver change cannot slip past."""
    from tools import paper_a_saturation_verification as V

    p, _c0, _t, _cl1, nz = V._params("caffeine", 1.0)
    assert V.check_linearity(p, nz)["is_linear"] is True


def test_the_operator_reproduces_the_rhs_state_by_state(archive):
    """Including at rate 500, where the operator is extremely stiff."""
    for key in ("operator_check_rate_1", "operator_check_rate_500"):
        assert archive[key]["matches_rhs"] is True, key
        assert archive[key]["max_relative_operator_error"] < 1e-12, key


# ── 2. the decisive check: two independent integrators ───────────────────────────────────────
def test_bdf_and_the_matrix_exponential_agree(archive):
    """The core of G3. No adaptive stepping, no numerical Jacobian, no overflow warnings.

    Agreement to ~1e-6 relative across the whole rate range means the BDF result is not an artefact
    of its own error control.
    """
    assert archive["bdf_vs_expm"]["worst_relative_difference_percent"] < 0.01


def test_the_two_integrators_agree_in_the_SATURATED_regime_specifically(archive):
    """Agreement at rate 1 would prove nothing about a floor reached at rate 500."""
    deep = [r for r in archive["bdf_vs_expm"]["rows"] if r["rate"] >= 50.0]
    assert len(deep) >= 6
    for row in deep:
        assert row["relative_difference_percent"] < 0.01, (row["solute"], row["rate"])


# ── 3. the saturation itself, on the independent path ────────────────────────────────────────
def test_the_saturation_reproduces_without_bdf(archive):
    """A tenfold rate change still moves the prediction by <0.1 %, computed by matrix exponential."""
    assert archive["saturation_on_independent_path"]["worst_decade_spread_percent"] < 0.1


def test_the_prediction_converges_to_a_rate_independent_limit(archive):
    """The physical signature. A solver floor has no reason to produce a convergent sequence."""
    s = archive["saturation_on_independent_path"]
    assert s["all_converged"] is True
    for row in s["per_solute"]:
        assert row["converged"] is True, row["solute"]
        assert row["increments_shrink_above_floor"] is True, row["solute"]
        assert row["reached_noise_floor"] is True, row["solute"]


def test_the_increments_fall_by_many_orders_of_magnitude(archive):
    """Convergence must be decisive, not marginal: >6 decades of collapse in the increment."""
    s = archive["saturation_on_independent_path"]
    assert s["least_orders_of_magnitude_fallen"] > 6.0


def test_the_noise_floor_is_stated_and_sits_between_machine_error_and_physics(archive):
    """The convergence verdict must rest on a declared threshold, not on inspection.

    The floor has to be well above double-precision `expm` error (~1e-11) and far below any change
    that would matter physically, or it is doing the deciding rather than the data.
    """
    floor = archive["saturation_on_independent_path"]["noise_floor_relative"]
    assert 1e-10 < floor < 1e-6
    assert archive["saturation_on_independent_path"]["worst_final_increment_relative"] <= floor


# ── 4. the verdict ───────────────────────────────────────────────────────────────────────────
def test_the_verdict_is_physical(archive):
    assert archive["verdict"] == "PHYSICAL"


def test_the_verdict_is_derived_not_asserted(archive):
    """Every component of the conjunction must be present and true, so the verdict cannot be
    written by hand into the archive while a check underneath it fails."""
    assert archive["linearity_check"]["is_linear"]
    assert archive["operator_check_rate_1"]["matches_rhs"]
    assert archive["operator_check_rate_500"]["matches_rhs"]
    assert archive["bdf_vs_expm"]["worst_relative_difference_percent"] < 0.01
    assert archive["saturation_on_independent_path"]["all_converged"]


def test_a_nonflat_response_would_still_be_detected():
    """The sweep must be able to report a LARGE spread, or 'flat' is a constant not a measurement.

    At a rate multiplier of 0.1 the model is far from equilibrium and the response to rate is
    strong; the same code path must show that.
    """
    from tools import paper_a_saturation_verification as V

    lo = V.expm_prediction("caffeine", 0.1)
    hi = V.expm_prediction("caffeine", 1.0)
    spread = abs(hi - lo) / abs(lo) * 100.0
    assert spread > 10.0, (
        "a decade of rate in the UNSATURATED regime must move the prediction substantially, "
        "otherwise the flatness reported at high rate is a property of the code, not the physics")

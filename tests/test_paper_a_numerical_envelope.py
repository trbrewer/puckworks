"""Gate G4: the load-bearing contrasts survive the numerical envelope.

The redraft rests on two small contrasts (+0.447 pp and -0.157 pp), so "the numerics do not matter"
has to be demonstrated rather than assumed. The envelope reports that both are essentially
unmoved — which is a strong claim, and therefore one that needs a control: a check that can only
pass if changing the mesh really does change the computed answer.

Without that control, an envelope in which the node-count patch silently failed would report perfect
stability and look like the best possible result.
"""
from __future__ import annotations

import json
import pathlib
import sys
import warnings

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ARCHIVE = REPO / "docs" / "paper1_resource" / "PAPER_A_NUMERICAL_ENVELOPE.json"


@pytest.fixture(scope="module")
def archive():
    if not ARCHIVE.exists():
        pytest.skip("run tools/paper_a_numerical_envelope.py --write")
    return json.loads(ARCHIVE.read_text(encoding="utf-8"))


# ── 1. the control: the envelope must be capable of showing an effect ────────────────────────
def test_the_node_count_patch_actually_reaches_the_exact_path():
    """If `ps.NZ` did not change, every configuration would solve the same problem.

    This is the control that makes the whole gate meaningful. It asserts both that the patch takes
    effect and that the computed prediction genuinely responds to it.
    """
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps
    from tools import paper_a_saturation_verification as V

    seen = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for nz in (100, 400):
            with AB._numerics(nz, 1e-6):
                assert ps.NZ == nz, "the node-count patch did not take effect"
                seen[nz] = V.expm_prediction("caffeine", 1.0)

    assert seen[100] != seen[400], (
        "the mesh must change the computed prediction, or the envelope is vacuous and its "
        "stability result means nothing")


def test_the_solver_tolerance_patch_measurably_changes_the_bdf_answer():
    """Same control for the temporal axis: loosening the tolerance must degrade the answer."""
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks.models.pannusch2024 import solver as ps
    from tools import paper_a_saturation_verification as V

    exact = None
    got = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for tol in (1e-5, 1e-7):
            with AB._numerics(200, tol):
                sp = dict(ps._solute_params()["caffeine"])
                sp["c_s0"] = 1.0
                flow = AB._flow_gran(9.0, 93.4, "O")
                got[tol] = float(ps.simulate_fractions(
                    93.4, flow, AB._matched_bounds(flow), sp, cl1=1.0)[0])
        with AB._numerics(200, 1e-6):
            exact = V.expm_prediction("caffeine", 1.0)

    assert got[1e-5] != got[1e-7], "the tolerance patch did not change the BDF result"
    # ...and the tighter tolerance must be the closer one to the exact-in-time answer.
    assert abs(got[1e-7] - exact) < abs(got[1e-5] - exact), (
        "tightening the tolerance must move BDF TOWARD the exact solution; if it does not, the "
        "exact reference and the BDF path are not solving the same problem")


# ── 2. the envelope was actually swept ───────────────────────────────────────────────────────
def test_both_error_sources_were_separated(archive):
    """Spatial via the exact-in-time path, temporal against that same reference."""
    kinds = {c["integrator"] for c in archive["configurations"]}
    assert kinds == {"expm", "bdf"}
    meshes = {c["nz"] for c in archive["configurations"] if c["integrator"] == "expm"}
    assert meshes == {100, 200, 400}
    tols = {c["tolerance"] for c in archive["configurations"] if c["integrator"] == "bdf"}
    assert tols == {1e-5, 1e-6, 1e-7}


def test_every_configuration_refitted_rather_than_reusing_parameters(archive):
    """A mesh change must be allowed to move the fitted rate, not only the scores."""
    assert "refitted inside every configuration" in archive["method"]
    for c in archive["configurations"]:
        assert len(c["fitted_rates"]) == 6


# ── 3. the result ────────────────────────────────────────────────────────────────────────────
def test_the_hydraulic_contrast_is_numerically_robust(archive):
    s = archive["M1_minus_M2"]
    assert s["verdict"]["robust"] is True
    assert s["verdict"]["sign_preserved"] is True
    assert s["range"] < 0.01, "must be far below the +0.52 pp effect it supports"


def test_the_rate_freezing_contrast_keeps_its_sign_everywhere(archive):
    s = archive["M0_minus_M2"]
    assert s["verdict"]["sign_preserved"] is True
    assert s["max"] < 0.0, "every configuration must still favour freezing the rate"
    assert s["range"] < 0.01


def test_numerical_variation_is_orders_below_both_effects(archive):
    """The acceptance criterion, stated as a comparison rather than a tolerance."""
    for key, effect in (("M1_minus_M2", 0.447), ("M0_minus_M2", 0.157)):
        assert archive[key]["range"] < 0.05 * effect, key


def test_time_integration_error_is_negligible_at_production_tolerance(archive):
    """Measured against truth, not against another BDF run."""
    rows = {t["tolerance"]: t for t in archive["time_integration_error_vs_exact"]}
    assert 1e-6 in rows
    for key in ("M1_minus_M2_error_pp", "M0_minus_M2_error_pp"):
        assert abs(rows[1e-6][key]) < 1e-3, key


def test_the_verdict_is_passed(archive):
    assert archive["verdict"] == "PASSED"


def test_acceptance_is_tied_to_the_conclusion_not_a_concentration_tolerance(archive):
    """The referee's original framing, preserved so it cannot drift back to an absolute threshold."""
    assert "Tied to the conclusion" in archive["acceptance"]
    assert "its own magnitude" in archive["acceptance"]

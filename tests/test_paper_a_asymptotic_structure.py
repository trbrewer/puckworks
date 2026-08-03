"""Structural premises of the large-multiplier limit (R0a: PR-02, PR-03).

Protocol V2 §2.4 constructs the `κ → ∞` limit from a singular perturbation of the operator pencil
`A(κ) = A₀ + κ·A₁`, taking the fast subspace to the local-equilibrium manifold `ker(A₁)`. Two
premises underwrite that construction, and both were recorded OPEN by the pre-freeze premise audit
before these tests existed:

* **PR-02** — the operator really is *affine* in the multiplier. If it were not, the pencil, the
  reduced operator and the remainder bound would all be invalid.
* **PR-03** — `A₁` has a spectral gap on the fast subspace, so the fast modes decay uniformly and
  the remainder is `O(1/(κ·gap))`.

These are **structural properties of the model operator**. They inspect no profiled objective, no
tolerance boundary and no shoulder, so they are permitted before the P0-G0 freeze — the adjudication
explicitly authorises deriving the asymptotic operator and error bounds without evaluating campaign
outcomes.

PR-03 is only *partially* closed here. The gap is measured; a remainder bound with explicit
constants is still owed before P0-G8 may run.
"""
from __future__ import annotations

import pathlib
import sys
import warnings

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _operator(kappa, solute="caffeine"):
    from tools import paper_a_saturation_verification as V

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p, _c0, _t, _cl1, nz = V._params(solute, kappa)
        A, _idx = V.build_operator(p, nz)
    return A


@pytest.fixture(scope="module")
def pencil():
    """(A1, A_at_1) — the multiplier-linear part and a reference point."""
    a1, a2 = _operator(1.0), _operator(2.0)
    return a2 - a1, a1


# ── PR-02 ────────────────────────────────────────────────────────────────────────────────────
def test_the_operator_is_affine_in_the_multiplier(pencil):
    """A(κ) = A₀ + κ·A₁ exactly, so the pencil in protocol V2 §2.4 is well posed."""
    A1, A_at_1 = pencil
    for kappa in (3.0, 10.0, 100.0):
        implied = (_operator(kappa) - A_at_1) / (kappa - 1.0)
        residual = np.abs(implied - A1).max() / max(np.abs(A1).max(), 1e-30)
        assert residual < 1e-10, ("A(κ) is not affine at κ=%g (residual %.2e); the limit "
                                  "construction has no basis" % (kappa, residual))


def test_the_fast_slow_split_matches_the_physics(pencil):
    """`ker(A₁)` must be the slow manifold: liquid cells plus accumulated mass.

    With `nz` axial nodes the reduced state is [c_l, c_s1, c_s2, m_cum] of size 3·nz+1. Interphase
    transfer acts on the 2·nz grain rows, so rank(A₁) = 2·nz and nullity = nz+1. A different split
    would mean the limit is not the local-equilibrium manifold the derivation assumes.
    """
    from puckworks.models.pannusch2024 import solver as ps

    A1, _ = pencil
    nz = ps.NZ
    assert A1.shape == (3 * nz + 1, 3 * nz + 1)
    rank = np.linalg.matrix_rank(A1, tol=1e-9)
    assert rank == 2 * nz, (rank, 2 * nz)
    assert A1.shape[0] - rank == nz + 1


# ── PR-03 ────────────────────────────────────────────────────────────────────────────────────
def test_the_fast_subspace_has_a_spectral_gap(pencil):
    """All fast modes decay, uniformly and away from zero, so the κ→∞ limit exists.

    A gap is necessary for a `O(1/(κ·gap))` remainder. It is not sufficient for the BOUND, which
    needs explicit constants — recorded as still owed in the R0a audit rather than assumed here.
    """
    A1, _ = pencil
    eigenvalues = np.linalg.eigvals(A1)
    fast = eigenvalues[np.abs(eigenvalues) > 1e-8]

    assert fast.size > 0
    assert fast.real.max() < 0, "a non-decaying fast mode would prevent any limit"
    gap = np.abs(fast.real).min()
    assert gap > 1e-2, "spectral gap %.3e is too small to bound the remainder usefully" % gap


def test_the_gap_is_a_property_of_the_operator_not_of_one_solute(pencil):
    """If the split held only for caffeine, the derivation could not cover every group."""
    from puckworks.models.pannusch2024 import solver as ps

    nz = ps.NZ
    for solute in ("trigonelline", "5CQA"):
        A1 = _operator(2.0, solute) - _operator(1.0, solute)
        assert np.linalg.matrix_rank(A1, tol=1e-9) == 2 * nz, solute
        fast = np.linalg.eigvals(A1)
        fast = fast[np.abs(fast) > 1e-8]
        assert fast.real.max() < 0, solute


def test_the_remainder_bound_is_recorded_as_still_owed():
    """PR-03 must not silently become 'assured' because a gap was measured.

    Measuring a gap and deriving a bound with constants are different things, and P0-G8's error
    budget needs the second. This test fails if the audit is upgraded without the derivation.
    """
    import json

    audit = json.loads((REPO / "docs" / "paper1_resource"
                        / "PAPER_A_PRE_FREEZE_PREMISE_AUDIT_R0A.json").read_text(encoding="utf-8"))
    ids = {p["premise_id"]: p for p in audit["premises"]}
    assert ids["PR-03a"]["disposition"] == "assured", (
        "the stable null-basis endpoint converges at every declared cell")
    assert ids["PR-03b"]["disposition"] == "NOT-PURSUED-CURRENT-PROTOCOL", (
        "the WIDE-referenced architecture removes the need for a sharp finite-tail bound; "
        "tail_onset_status is unresolved_by_design")
    assert ids["PR-03b"]["blocks_before"] == [], (
        "a missing tail onset must not block P0-G0 once PR-03a is assured")

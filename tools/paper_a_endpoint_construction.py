#!/usr/bin/env python3
"""PR-03a — the fixed-positive-time singular limit, its assumptions, and the endpoint construction.

The proposition, its assumptions and its proof live in
`docs/paper1_resource/PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md`. This producer **verifies
the assumptions of that proposition at every declared cell** and constructs the endpoint. It does
not, and cannot, prove the proposition: a finite sample of trajectories is not a theorem.

The adjudication separates two questions an earlier draft had fused:

* **PR-03a** — does `f(κ)` converge to a trustworthy analytical endpoint `f_inf`? This decides the
  P0-G8 *endpoint classification* and is a pre-freeze blocker.
* **PR-03b** — how large must `κ` be before the profile has entered its accepted tail? This only
  localises the onset, and an unresolved onset does not invalidate an endpoint result.

At `κ = ∞` the asymptotic remainder is **zero**, so a finite-κ `C/κ` term is not an uncertainty
contribution to `J_inf`. Adding one, as the previous protocol did, was a category error.

**Five statuses, not one.** The previous single verdict could not distinguish a failed algebraic
assumption from a degraded numerical diagnostic, so a `method_limited` sequence and a genuinely
broken cell reported identically:

    algebraic_limit_status         assured | not_assured
    endpoint_construction_status   verified | failed
    finite_kappa_validation_status consistent | method_limited | inconsistent
    coverage_status                complete | incomplete
    overall_PR03a_status           assured | not_assured

`overall_PR03a_status` is `assured` only when the algebraic assumptions hold, the construction is
verified, coverage is complete, and the finite-κ diagnostic is not `inconsistent`. A
`method_limited` diagnostic does **not** block: it is a statement about `expm`, not about the limit.

**Stable construction.** The endpoint is built from rank-revealing null bases, never from inverting
the full eigenvector matrix (whose condition number here is ~5e10):

    N   = orthonormal basis of ker(A₁)            (SVD right null space)
    L   = basis of ker(A₁ᵀ), normalised so LᵀN = I
    A_s = Lᵀ A₀ N                                 (reduced slow operator)
    z_inf(T) = N · exp(A_s·T) · Lᵀ z₀

with `P = N Lᵀ` verified idempotent and annihilating `A₁` on both sides.

**Model-only.** No `y`, `J`, `J_ref`, `J_inf`, threshold, profile component, tail classification or
shoulder is read or computed. Permitted before the P0-G0 freeze on that basis.

CLI::

    python tools/paper_a_endpoint_construction.py --write
    python tools/paper_a_endpoint_construction.py --check
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import platform
import sys
import warnings

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_ENDPOINT_CONSTRUCTION.json"
PROOF = _REPO / "docs" / "paper1_resource" / "PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md"

SOLUTES = ("caffeine", "trigonelline", "5CQA")
VARIETIES = ("Arabica", "Robusta")

#: Finite-κ DIAGNOSTIC sequence. Protocol V2 declared {1e2 … 1e6}. It is retained in full and is
#: **not** a proof of the limit — see the proposition artefact §8. The observed error is U-shaped:
#: it falls to a minimum near κ≈1e3 and then rises. The rise is read as degradation of the
#: MEASUREMENT (‖A(κ)T‖ grows linearly in κ, so `expm` conditioning degrades) rather than of the
#: limit. That reading is a **diagnostic interpretation, not a proved error law**, and no universal
#: O(κ·eps) claim is made anywhere in this producer or its archive.
VERIFY_KAPPA = (1e2, 1e3, 1e4, 1e5, 1e6)

#: The diagnostic must attain at least this error somewhere in the sequence.
CONVERGENCE_TOL = 1e-9

#: A post-minimum rise beyond this absolute cap is `inconsistent` rather than `method_limited`.
#: A ratio window was tried first and was the wrong instrument: it flagged a flat tail (ratio 1.002,
#: plainly not divergence) and a ratio of 49 against an arbitrary cap of 50. What the check must
#: exclude is DIVERGENCE, so an absolute cap three orders below any quantity of interest is the right
#: test. Neither this cap nor any ratio rule determines the theorem.
TAIL_ABS_CAP = 1e-6

#: Projector residuals above this fail the construction. Chosen from double precision on operators
#: of this size, not from observed values.
IDENTITY_TOL = 1e-10

#: Relative rank tolerance family, recorded for transparency. It is NOT what decides the rank —
#: see `_separated_rank`. A threshold scaled to `s.max()*n*eps` sits *inside* the noise floor of an
#: exactly singular operator, so a numerically-zero singular value can straddle it and the verdict
#: then reports the tolerance rather than the operator.
RANK_TOL_FAMILY = (0.1, 1.0, 10.0)

#: Minimum retained/discarded separation required AT THE DECLARED CUT. It verifies a structurally
#: derived rank; it never discovers one.
#:
#: The previous edition chose the rank from the globally LARGEST singular-value gap and asserted that
#: a defective zero produces no such gap. That assertion is false, and the review supplied the
#: counterexample: for `block_diag(Jordan2(0), [-1e9])` the singular values are `[1e9, 1, 0]` and
#: `[1e18, 0, 0]`, so the largest gap sits between the fast block and the Jordan singular value
#: rather than at the true nonzero/zero cut, and the rule returned rank 1 for both — reporting a
#: DEFECTIVE zero as semisimple. The crossover is governed by this very constant, so the claim that
#: it sat "far above anything a defective operator produces" was self-refuting.
RANK_GAP_MIN = 1e6

#: An eigenvalue of A₁ counts as fast when |λ| exceeds this multiple of the spectral radius.
SPECTRAL_TOL_REL = 1e-8

#: An endpoint output must be real to this absolute tolerance and strictly positive.
IMAG_TOL = 1e-12

#: Fields excluded from `--check` comparison, because they legitimately differ between machines
#: without indicating archive drift.
CHECK_EXCLUDED_TOP_LEVEL = ("environment",)

#: Relative tolerance for float comparison in `--check`. Declared, not discovered.
CHECK_RTOL = 1e-9


def _sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _rel(path: pathlib.Path) -> str:
    """Repo-relative when possible. `relative_to` raises for a path outside the repo, which used to
    crash the missing-archive branch of `--check` instead of reporting it."""
    try:
        return str(path.relative_to(_REPO))
    except ValueError:
        return str(path)


def null_bases(A1):
    """Rank-revealing right/left null bases with Lᵀ N = I, and the induced spectral projector."""
    n = A1.shape[0]
    U, s, Vt = np.linalg.svd(A1)
    tol = s.max() * n * np.finfo(float).eps
    rank = int((s > tol).sum())

    N = Vt[rank:].T.conj()
    Lraw = U[:, rank:]
    gram = Lraw.conj().T @ N
    L = Lraw @ np.linalg.inv(gram).conj().T
    P = (N @ L.conj().T).real

    diagnostics = {
        "rank": rank, "nullity": n - rank,
        "svd_rank_tolerance": float(tol),
        "residual_A1_N": float(np.linalg.norm(A1 @ N, 2)),
        "residual_Lt_A1": float(np.linalg.norm(L.conj().T @ A1, 2)),
        "residual_Lt_N_minus_I": float(np.linalg.norm(L.conj().T @ N - np.eye(n - rank), 2)),
        "residual_P_squared_minus_P": float(np.linalg.norm(P @ P - P, 2)),
        "residual_A1_P": float(np.linalg.norm(A1 @ P, 2)),
        "residual_P_A1": float(np.linalg.norm(P @ A1, 2)),
        # cond(N)=1 is automatic for an orthonormal SVD basis and is NOT evidence of operator
        # conditioning; the informative quantities are cond(L) and the pre-normalisation Gram.
        "cond_N": float(np.linalg.cond(N)), "cond_L": float(np.linalg.cond(L)),
        # Ratio of the smallest RETAINED singular value to the largest DISCARDED one. This is a
        # rank-separation diagnostic for the SVD cut; it is NOT the fast spectral decay gap, and the
        # earlier name "singular_gap" invited exactly that confusion.
        "svd_rank_separation_ratio": (float(s[rank - 1] / s[rank])
                                      if rank < len(s) and s[rank] > 0.0 else float("inf")),
        "cond_Lt_N_before_normalisation": float(np.linalg.cond(gram)),
    }
    return N, L, P, diagnostics


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Assumption verification — proposition §2, tested per cell
# ─────────────────────────────────────────────────────────────────────────────────────────────


def structural_rank(nz=None):
    """The model-derived rank of A₁, declared rather than discovered.

    The reduced state is `[c_l, c_s1, c_s2, m_cum]` of dimension `3·nz + 1`. The interphase-transfer
    terms that carry the multiplier act on the `2·nz` grain rows only; advection and the accumulation
    row are annihilated by `A₁`. Hence

        rank(A₁) = 2·nz          nullity(A₁) = nz + 1

    the kernel being the `nz` liquid cells plus the accumulated-mass coordinate. This is the same
    split independently asserted by `tests/test_paper_a_asymptotic_structure.py`.
    """
    if nz is None:
        from puckworks.models.pannusch2024 import solver as ps
        nz = ps.NZ
    return {
        "nz": int(nz),
        "state_dimension": int(3 * nz + 1),
        "expected_fast_rank": int(2 * nz),
        "expected_slow_nullity": int(nz + 1),
        "derivation": ("A1 carries the interphase-transfer terms, which act on the 2*nz grain rows; "
                       "the nz liquid cells and the accumulated-mass row are annihilated. rank = "
                       "2*nz, nullity = nz+1."),
    }


def _largest_gap_rank(s):
    """DIAGNOSTIC ONLY — the rank the superseded largest-gap rule would have reported.

    Retained solely so the archive records what the withdrawn rule said. It must never decide a
    verdict: for `block_diag(Jordan2(0), [-1e9])` it returns rank 1 for both `A₁` and `A₁²` and
    thereby calls a defective zero semisimple.
    """
    s = np.asarray(s, float)
    if s.size == 0:
        return 0, float("inf")
    floor = s.max() * np.finfo(float).eps
    ratios = s[:-1] / np.maximum(s[1:], floor)
    i = int(np.argmax(ratios))
    return i + 1, float(ratios[i])


def _separation_at(s, r):
    """Retained/discarded separation at the DECLARED cut `r`.

    Returns `(ratio, separated, decidable)`. Two independent things can go wrong and they are
    reported separately rather than collapsed into one `False`:

    * **not decidable** — the last RETAINED value sits at or below `eps·max(s)`, so it is not
      numerically distinguishable from zero and the rank at this cut cannot be determined at all.
      This is what happens to `A₁²` for an operator with a very large internal scale ratio: squaring
      doubles the dynamic range, and beyond ~1e16 a legitimately retained singular value falls under
      the noise level of its own computation.
    * **not separated** — the retained and discarded blocks are decidable but too close, so the cut
      is not clean.

    The scaled-Jordan counterexample `block_diag(Jordan2(0), [-1e9])` fails as *not decidable* on
    `A₁²`, where the true cut needs a retained value that is exactly zero.

    Either failure is fail-closed. Neither is ever reported as semisimple.
    """
    s = np.asarray(s, float)
    if not 0 < r <= s.size:
        return 0.0, False, False
    floor = s.max() * np.finfo(float).eps if s.size else 0.0
    last_retained = float(s[r - 1])
    decidable = last_retained > floor
    if not decidable:
        return 0.0, False, False
    if r == s.size:
        return float("inf"), True, True
    ratio = last_retained / max(float(s[r]), floor)
    return float(ratio), bool(ratio >= RANK_GAP_MIN), True


def _semisimplicity_failure_reason(ok1, ok2, dec1, dec2, last1, last2):
    """Why the declared cut failed — a defective kernel and an undecidable rank are not the same.

    If the last value the cut needs to RETAIN in `A₁²` is itself zero, the kernel has grown under
    squaring: that is the definition of a defective zero. If it is merely small relative to
    `eps·max(s)`, double precision cannot decide the rank there. Both fail closed; conflating them
    would hide which one occurred.
    """
    if ok1 and ok2:
        return None
    for label, last, dec in (("A1", last1, dec1), ("A1^2", last2, dec2)):
        if last is not None and last == 0.0:
            return ("kernel grows under squaring: %s has an exactly zero singular value where the "
                    "declared cut requires a retained one, so zero is DEFECTIVE" % label)
    if not (dec1 and dec2):
        return ("rank at the declared cut is not numerically decidable: a retained singular value "
                "falls below eps*max(s), which happens when the operator's internal scale ratio "
                "exceeds what double precision resolves after squaring")
    return "retained and discarded blocks are not cleanly separated at the declared cut"


def semisimplicity(A1, expected_rank):
    """(A2): zero is a semisimple eigenvalue of A₁ — VERIFIED at a declared structural cut.

    A defective zero would mean `ker(A₁)` and `ran(A₁)` intersect, no normalised `L` exists, and the
    whole construction is meaningless.

    The rank is **not discovered**. `expected_rank` comes from the model structure and this function
    verifies that both `A₁` and `A₁²` separate cleanly at exactly that cut. Discovering the rank from
    the largest gap is unsound: a fast block whose scale exceeds the gap floor creates a larger gap
    before the Jordan singular value than at the true nonzero/zero cut, so
    `block_diag(Jordan2(0), [-1e9])` was reported semisimple. Verifying at the declared cut rejects
    it, because at the true rank `A₁²` has a zero where a retained value is required.

    The threshold family is still recorded, because it shows why a bare threshold cannot be trusted
    either: at a 10x TIGHTER tolerance a numerically-zero singular value of `A₁` crosses back above
    the cut in some real cells, reporting the noise floor rather than the operator.
    """
    n = A1.shape[0]
    s1 = np.linalg.svd(A1, compute_uv=False)
    s2 = np.linalg.svd(A1 @ A1, compute_uv=False)
    base1 = s1.max() * n * np.finfo(float).eps
    base2 = s2.max() * n * np.finfo(float).eps

    family = {}
    for f in RANK_TOL_FAMILY:
        family["x%g" % f] = {"rank_A1": int((s1 > f * base1).sum()),
                             "rank_A1_squared": int((s2 > f * base2).sum())}

    sep1, ok1, dec1 = _separation_at(s1, expected_rank)
    sep2, ok2, dec2 = _separation_at(s2, expected_rank)
    last1 = float(s1[expected_rank - 1]) if 0 < expected_rank <= s1.size else None
    last2 = float(s2[expected_rank - 1]) if 0 < expected_rank <= s2.size else None
    gap_rank1, gap_ratio1 = _largest_gap_rank(s1)
    gap_rank2, gap_ratio2 = _largest_gap_rank(s2)

    return {
        "test": ("rank(A1) == rank(A1^2) == expected structural rank, VERIFIED at the declared cut; "
                 "the cut is never discovered from the largest gap"),
        "expected_rank": int(expected_rank),
        "nullity": int(n - expected_rank),
        "separation_at_expected_cut_A1": sep1,
        "separation_at_expected_cut_A1_squared": sep2,
        "separates_cleanly_A1": bool(ok1),
        "separates_cleanly_A1_squared": bool(ok2),
        "rank_decidable_A1": bool(dec1),
        "rank_decidable_A1_squared": bool(dec2),
        "last_retained_singular_value_A1": last1,
        "last_retained_singular_value_A1_squared": last2,
        "failure_reason": _semisimplicity_failure_reason(ok1, ok2, dec1, dec2, last1, last2),
        "minimum_gap_ratio_required": RANK_GAP_MIN,
        "threshold_rank_tolerance": float(base1),
        "threshold_rank_tolerance_A1_squared": float(base2),
        "rank_tolerance_family": list(RANK_TOL_FAMILY),
        "rank_under_tolerance_family": family,
        "threshold_family_note": ("recorded for transparency only; a threshold near the noise floor "
                                  "of an exactly singular operator is straddled by numerically-zero "
                                  "singular values and reports the tolerance, not the operator"),
        "withdrawn_largest_gap_rule": {
            "role": "DIAGNOSTIC ONLY - decides nothing",
            "rank_A1": gap_rank1, "gap_ratio_A1": gap_ratio1,
            "rank_A1_squared": gap_rank2, "gap_ratio_A1_squared": gap_ratio2,
            "agrees_with_expected": bool(gap_rank1 == expected_rank == gap_rank2),
            "why_withdrawn": ("it selects the globally largest gap, which for a scale-separated "
                              "defective operator such as block_diag(Jordan2(0), [-1e9]) lands "
                              "before the Jordan singular value rather than at the nonzero/zero "
                              "cut, reporting a defective zero as semisimple"),
        },
        "semisimple": bool(ok1 and ok2),
    }


def fast_spectrum(A1):
    """(A3): every nonzero eigenvalue of A₁ lies strictly in the open left half-plane.

    Computed by ordered real Schur, which reduces by orthogonal similarity and never forms or
    inverts an eigenvector matrix. The fast invariant subspace comes back as an orthonormal basis,
    which is also what makes the Lemma-3 constants well conditioned.
    """
    from scipy.linalg import schur

    radius = float(np.abs(np.linalg.eigvals(A1)).max())
    cut = SPECTRAL_TOL_REL * radius

    Tq, Z, k = schur(A1, output="real", sort=lambda a, b: (a * a + b * b) > cut * cut)
    k = int(k)
    fast_block = Tq[:k, :k]
    fast_eigs = np.linalg.eigvals(fast_block) if k else np.array([])

    return {
        "spectral_method": "ordered real Schur (scipy.linalg.schur, nonzero modes sorted first)",
        "spectral_tolerance": float(cut),
        "spectral_tolerance_rule": "|lambda| > %g * spectral_radius" % SPECTRAL_TOL_REL,
        "spectral_radius": radius,
        "fast_mode_count": k,
        "slow_mode_count": int(A1.shape[0] - k),
        "max_real_fast_eigenvalue": float(fast_eigs.real.max()) if k else float("-inf"),
        "min_abs_fast_eigenvalue": float(np.abs(fast_eigs).min()) if k else float("inf"),
        "all_fast_modes_strictly_stable": bool(k > 0 and fast_eigs.real.max() < 0.0),
    }, Z[:, :k], fast_block


def lemma3_constants(fast_block, A_ff):
    """Derived constants of proposition Lemma 3: X, M, gamma, kappa_0.

    Every one is derived from the operator. None is fitted to an observed trajectory or to an output
    error — that distinction is the whole point of separating the theorem from the diagnostic.
    """
    from scipy.linalg import solve_continuous_lyapunov

    if fast_block.size == 0:
        return {"applicable": False, "why": "no fast modes"}
    X = solve_continuous_lyapunov(fast_block.conj().T, -np.eye(fast_block.shape[0]))
    Xs = (X + X.conj().T).real / 2.0
    ev = np.linalg.eigvalsh(Xs)
    lmin, lmax = float(ev[0]), float(ev[-1])
    if not lmin > 0:
        return {"applicable": False, "why": "Lyapunov solution is not positive definite",
                "lambda_min_X": lmin, "lambda_max_X": lmax}
    S = A_ff.conj().T @ Xs + Xs @ A_ff
    return {
        "applicable": True,
        "lyapunov_equation": "F^T X + X F = -I on the fast block",
        "lambda_min_X": lmin, "lambda_max_X": lmax,
        "M_decay_constant": float(np.sqrt(lmax / lmin)),
        "gamma_decay_rate": float(1.0 / (4.0 * lmax)),
        "kappa_0_threshold": float(2.0 * np.linalg.norm(S, 2)),
        "bound": "||exp((kappa F + A_ff) t)|| <= M exp(-gamma kappa t) for kappa >= kappa_0",
        "derived_not_fitted": True,
    }


def endpoint_verdict(f_complex):
    """Required properties of a declared endpoint output: finite, real within tolerance, positive."""
    re, im = float(np.real(f_complex)), float(np.imag(f_complex))
    return {
        "f_inf": re,
        "imag_part_magnitude": abs(im),
        "imag_tolerance": IMAG_TOL,
        "finite": bool(np.isfinite(re) and np.isfinite(im)),
        "real_within_tolerance": bool(abs(im) <= IMAG_TOL),
        "strictly_positive": bool(re > 0.0),
    }


def rank_agreement(expected_rank, null_basis_rank, schur_fast_count, semisimple_ok,
                   slow_pairing_conditioned):
    """Every independent rank source must agree with the declared structural rank.

    Four routines compute the same integer by different means — the model structure, the SVD null
    basis, the ordered Schur fast count, and the semisimplicity separation. A single one of them
    deciding alone is how the largest-gap rule got to call a defective zero semisimple. Any
    disagreement fails closed.
    """
    sources = {"expected_structural_rank": int(expected_rank),
               "null_basis_rank": int(null_basis_rank),
               "schur_fast_mode_count": int(schur_fast_count)}
    agree = len(set(sources.values())) == 1
    return {
        "sources": sources,
        "all_sources_agree": bool(agree),
        "semisimplicity_verified_at_expected_cut": bool(semisimple_ok),
        "slow_pairing_nonsingular_and_conditioned": bool(slow_pairing_conditioned),
        "agreement_ok": bool(agree and semisimple_ok and slow_pairing_conditioned),
    }


def coverage_verdict(n_cells, n_conditions, n_solutes, n_varieties):
    """`complete` only when every operator-distinct cell exists and covers every declared cell."""
    expected_cells = n_conditions * n_solutes
    declared = n_conditions * n_varieties * n_solutes
    return ("complete" if (n_cells == expected_cells and declared == n_cells * n_varieties)
            else "incomplete")


def overall_status(algebraic, construction, finite_kappa, coverage):
    """The frozen closure rule. `method_limited` does not block; `inconsistent` does."""
    return ("assured" if (algebraic == "assured" and construction == "verified"
                          and coverage == "complete" and finite_kappa != "inconsistent")
            else "not_assured")


def _finite_kappa_disposition(errors):
    """`consistent` | `method_limited` | `inconsistent` — a diagnostic disposition, never a proof."""
    best = int(np.argmin(errors))
    attained = errors[best] <= CONVERGENCE_TOL
    tail = errors[best:]
    rose = len(tail) > 1 and tail[-1] > tail[0]
    bounded = all(e <= TAIL_ABS_CAP for e in tail)
    if not attained or not bounded:
        return "inconsistent", best
    return ("method_limited" if rose else "consistent"), best


def cell(solute, T_degC, p_bar) -> dict:
    from scipy.linalg import expm
    from tools import paper_a_singular_limit_bound as B

    captured = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        A0, A1, z0, horizon, dVol = B.pencil(solute, T_degC, p_bar)
        N, L, P, diag = null_bases(A1)
        volume = dVol * horizon

        structure = structural_rank()
        semis = semisimplicity(A1, structure["expected_fast_rank"])
        spec, W, fast_block = fast_spectrum(A1)

        # dual basis of [N W]; Lemma 2. L recovered this way must agree with the SVD L, since
        # L^T N = I and L^T A1 = 0 determine it uniquely — recorded as a cross-check.
        V = np.hstack([N, W])
        Vinv = np.linalg.inv(V)
        m = N.shape[1]
        L_dual = Vinv[:m, :].conj().T
        Mt = Vinv[m:, :]
        A_ff = (Mt @ A0 @ W).real
        lemma3 = lemma3_constants(fast_block, A_ff)
        dual_agreement = float(np.linalg.norm(L_dual - L, 2))

        A_s = (L.conj().T @ A0 @ N).real
        z_inf = (N @ expm(A_s * horizon) @ (L.conj().T @ z0)).real
        f_inf_complex = complex((N @ expm(A_s * horizon) @ (L.conj().T @ z0))[-1] / volume)
        f_inf = float(z_inf[-1] / volume)

        # the declared output reads the accumulated-mass coordinate. The proposition remark asserts
        # that the output COVECTOR annihilates the fast subspace, equivalently e_out Q = 0 (it lies
        # in ker(A1^T), not in ker(A1) — a linear output row is a covector, not a state vector).
        # Verified, not assumed.
        e_out = np.zeros(A1.shape[0]); e_out[-1] = 1.0
        output_is_slow = float(np.linalg.norm(e_out @ (np.eye(A1.shape[0]) - P), 2))
        endpoint = endpoint_verdict(f_inf_complex)

        seq = []
        for k in VERIFY_KAPPA:
            f_k = float((expm((A0 + k * A1) * horizon) @ z0)[-1] / volume)
            seq.append({"kappa": k, "f": f_k, "abs_error": abs(f_k - f_inf)})
        captured = ["%s: %s" % (w.category.__name__, str(w.message)[:200]) for w in caught]

    errors = [s["abs_error"] for s in seq]
    disposition, best = _finite_kappa_disposition(errors)

    agreement = rank_agreement(structure["expected_fast_rank"], diag["rank"],
                               spec["fast_mode_count"], semis["semisimple"],
                               diag["cond_Lt_N_before_normalisation"] < 1e6)
    identities_ok = all(diag[k] < IDENTITY_TOL for k in
                        ("residual_A1_N", "residual_Lt_A1", "residual_Lt_N_minus_I",
                         "residual_P_squared_minus_P", "residual_A1_P", "residual_P_A1"))
    well_conditioned = diag["cond_L"] < 1e3 and diag["cond_Lt_N_before_normalisation"] < 1e6
    finite = endpoint["finite"]
    real_within_tol = endpoint["real_within_tolerance"]
    positive = endpoint["strictly_positive"]

    algebraic_ok = bool(agreement["agreement_ok"] and spec["all_fast_modes_strictly_stable"]
                        and lemma3.get("applicable", False))
    construction_ok = bool(identities_ok and well_conditioned and finite and real_within_tol
                           and positive)

    return {
        "solute": solute, "T_degC": T_degC, "p_bar": p_bar, "horizon_tc": horizon,
        "applies_to_varieties": list(VARIETIES),
        "assumptions": {
            "structural_rank": structure,
            "A2_semisimple_zero": semis,
            "rank_source_agreement": agreement,
            "A3_stable_fast_spectrum": spec,
            "A4_A5_bases_and_normalisation": {
                **diag,
                "identities_within_tolerance": identities_ok,
                "identity_tolerance": IDENTITY_TOL,
                "well_conditioned_bases": well_conditioned,
                "dual_basis_agreement_norm": dual_agreement,
            },
            "lemma3_derived_constants": lemma3,
        },
        "endpoint": {
            **endpoint,
            "output_functional": "accumulated-mass coordinate divided by dVol*T",
            "output_covector_fast_component_norm": output_is_slow,
            "output_covector_annihilates_fast_subspace": bool(output_is_slow < 1e-9),
            "output_covector_note": ("e_out Q = 0, equivalently the output covector lies in "
                                     "ker(A1^T). A linear output row is a covector, not a state "
                                     "vector, so it does not 'lie in ker(A1)'."),
        },
        "finite_kappa_diagnostic": {
            "role": "DIAGNOSTIC ONLY - it does not prove the proposition",
            "sequence": seq,
            "best_kappa": VERIFY_KAPPA[best],
            "min_abs_error": errors[best],
            "final_abs_error": errors[-1],
            "convergence_tolerance": CONVERGENCE_TOL,
            "tail_absolute_cap": TAIL_ABS_CAP,
            "disposition": disposition,
        },
        "warnings": captured,
        "algebraic_limit_ok": algebraic_ok,
        "endpoint_construction_ok": construction_ok,
        # retained for continuity with the previous archive consumers
        "f_inf": f_inf,
        "status": "pass" if (algebraic_ok and construction_ok
                             and disposition != "inconsistent") else "fail",
    }


def run() -> dict:
    import scipy
    from tools import paper_a_singular_limit_bound as B

    conditions = B._conditions()
    cells = [cell(s, T, p) for T, p in conditions for s in SOLUTES]
    declared = len(conditions) * len(VARIETIES) * len(SOLUTES)

    algebraic = "assured" if all(c["algebraic_limit_ok"] for c in cells) else "not_assured"
    construction = "verified" if all(c["endpoint_construction_ok"] for c in cells) else "failed"
    dispositions = [c["finite_kappa_diagnostic"]["disposition"] for c in cells]
    if "inconsistent" in dispositions:
        finite_kappa = "inconsistent"
    elif "method_limited" in dispositions:
        finite_kappa = "method_limited"
    else:
        finite_kappa = "consistent"
    coverage = coverage_verdict(len(cells), len(conditions), len(SOLUTES), len(VARIETIES))
    overall = overall_status(algebraic, construction, finite_kappa, coverage)

    return {
        "schema_version": 2,
        "premise": "PR-03a",
        "question": ("Does f(kappa) converge to a trustworthy analytical endpoint f_inf, computed "
                     "by a stable construction whose assumptions are verified at every declared "
                     "cell? This decides the P0-G8 ENDPOINT classification; it does not localise "
                     "the finite tail onset, which is PR-03b."),
        "scope_note": ("MODEL-ONLY. No y, J, J_ref, J_inf, threshold, profile component, tail "
                       "classification or shoulder is read or computed."),
        "proposition": {
            "artefact": "docs/paper1_resource/PAPER_A_FIXED_TIME_SINGULAR_LIMIT_PROPOSITION.md",
            "sha256": _sha256(PROOF),
            "statement": ("For fixed T > 0, exp((A0 + kappa A1) T) -> N exp((L^T A0 N) T) L^T, "
                          "under a semisimple zero eigenvalue of A1 and a strictly stable nonzero "
                          "spectrum."),
            "qualification": ("Convergence is NOT uniform at t = 0 for off-manifold initial data: "
                              "z_kappa(0) - P z0 = Q z0, independent of kappa. No uniform O(1/kappa) "
                              "state bound on [0, T] is claimed. Permitted formulations are fixed "
                              "positive T, or uniformity on [delta, T] for every delta > 0."),
            "proved_here": False,
            "role_of_this_producer": ("verifies the proposition's ASSUMPTIONS at every declared "
                                      "cell and constructs the endpoint; it does not prove the "
                                      "proposition"),
        },
        "construction": {
            "method": "rank-revealing SVD null bases; N spans ker(A1), L spans ker(A1^T), L^T N = I",
            "reduced_operator": "A_s = L^T A0 N",
            "endpoint": "z_inf(T) = N exp(A_s T) L^T z0",
            "why_not_eigensystem": ("cond(full eigenvector matrix) ~5e10; the eigen-projector "
                                    "endpoint differs from the independent high-kappa limit by "
                                    "4.3e-9, whereas this construction agrees to ~1e-12. The "
                                    "discrepancy previously read as a convergence floor was the "
                                    "construction's own conditioning error."),
        },
        "endpoint_remainder_note": ("At kappa = infinity the asymptotic remainder is ZERO. A "
                                    "finite-kappa C/kappa term is therefore NOT an uncertainty "
                                    "contribution to J_inf and must not enter the endpoint budget; "
                                    "it controls only the finite tail onset (PR-03b)."),
        "finite_kappa_diagnostic_note": (
            "The high-kappa sequence is a DIAGNOSTIC and is not an independent proof. Its U-shaped "
            "error is read as degradation of the measurement rather than of the limit; that reading "
            "is a diagnostic interpretation, NOT a proved error law, and no universal O(kappa*eps) "
            "claim is made. method_limited does not block assurance; inconsistent does."),
        "verification_sequence": list(VERIFY_KAPPA),
        "tolerances": {
            "convergence_tolerance": CONVERGENCE_TOL, "tail_absolute_cap": TAIL_ABS_CAP,
            "identity_tolerance": IDENTITY_TOL, "imag_tolerance": IMAG_TOL,
            "spectral_tolerance_relative": SPECTRAL_TOL_REL,
            "rank_tolerance_family": list(RANK_TOL_FAMILY),
            "check_relative_tolerance": CHECK_RTOL,
        },
        "coverage": {
            "conditions": len(conditions), "declared_cells": declared,
            "operator_distinct_cells": len(cells),
            "deduplication_proof": ("the pencil depends on (T, p, solute) only; variety enters "
                                    "solely through y, never read here. Each cell covers both "
                                    "varieties; declared coverage is complete."),
            "cells_passing": sum(1 for c in cells if c["status"] == "pass"),
            "cells_failing": sum(1 for c in cells if c["status"] != "pass"),
        },
        "cells": cells,
        "algebraic_limit_status": algebraic,
        "endpoint_construction_status": construction,
        "finite_kappa_validation_status": finite_kappa,
        "coverage_status": coverage,
        "overall_PR03a_status": overall,
        "closure_rule": ("overall_PR03a_status = assured iff algebraic_limit_status = assured and "
                         "endpoint_construction_status = verified and coverage_status = complete "
                         "and finite_kappa_validation_status != inconsistent"),
        "environment": {"python": platform.python_version(), "numpy": np.__version__,
                        "scipy": scipy.__version__, "platform": platform.platform()},
        "provenance": {
            "producer": "tools/paper_a_endpoint_construction.py",
            "producer_sha256": _sha256(pathlib.Path(__file__)),
            "command": "python tools/paper_a_endpoint_construction.py --write",
            "verification_command": "python tools/paper_a_endpoint_construction.py --check",
            "inputs": {rel: _sha256(_REPO / rel) for rel in (
                "tools/paper_a_singular_limit_bound.py",
                "tools/paper_a_saturation_verification.py",
                "puckworks/models/pannusch2024/solver.py",
                "puckworks/models/pannusch2024/closures.py",
            )},
            "manual_verdict_editing": "PROHIBITED; the archive is generated",
        },
    }


def canonical(obj) -> str:
    """The declared canonical serialisation. Used for writing and for `--check`."""
    return json.dumps(obj, indent=1, sort_keys=True, allow_nan=False) + "\n"


def semantic_diff(a, b, path="", rtol=CHECK_RTOL, out=None):
    """Structural equality, with floats compared to a declared relative tolerance."""
    out = [] if out is None else out
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append("%s/%s: present in only one archive" % (path, k))
            else:
                semantic_diff(a[k], b[k], "%s/%s" % (path, k), rtol, out)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append("%s: length %d vs %d" % (path, len(a), len(b)))
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                semantic_diff(x, y, "%s[%d]" % (path, i), rtol, out)
    elif isinstance(a, bool) or isinstance(b, bool) or a is None or b is None:
        if a != b:
            out.append("%s: %r vs %r" % (path, a, b))
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        if not (a == b or abs(a - b) <= rtol * max(abs(a), abs(b))):
            out.append("%s: %r vs %r (rtol %g)" % (path, a, b, rtol))
    elif a != b:
        out.append("%s: %r vs %r" % (path, a, b))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="regenerate and compare against the committed archive; nonzero on drift "
                         "or on overall_PR03a_status != assured")
    args = ap.parse_args(argv)

    print("verifying the proposition's assumptions and constructing the endpoint "
          "(model-only)...", flush=True)
    result = run()
    cov = result["coverage"]
    print("\ncells: %d computed covering %d declared; passing %d, failing %d"
          % (cov["operator_distinct_cells"], cov["declared_cells"],
             cov["cells_passing"], cov["cells_failing"]))
    worst = max(result["cells"], key=lambda c: c["finite_kappa_diagnostic"]["min_abs_error"])
    print("worst MINIMUM |f(k) - f_inf| = %.3e at k=%g  (%s, T=%.1f, p=%.0f)"
          % (worst["finite_kappa_diagnostic"]["min_abs_error"],
             worst["finite_kappa_diagnostic"]["best_kappa"], worst["solute"],
             worst["T_degC"], worst["p_bar"]))
    print("worst cond(L) = %.3f"
          % max(c["assumptions"]["A4_A5_bases_and_normalisation"]["cond_L"]
                for c in result["cells"]))
    print("worst max Re(fast eigenvalue) = %.3e"
          % max(c["assumptions"]["A3_stable_fast_spectrum"]["max_real_fast_eigenvalue"]
                for c in result["cells"]))
    for f in ("algebraic_limit_status", "endpoint_construction_status",
              "finite_kappa_validation_status", "coverage_status", "overall_PR03a_status"):
        print("  %-32s %s" % (f, result[f]))

    assured = result["overall_PR03a_status"] == "assured"

    if args.check:
        if not OUT.exists():
            print("CHECK FAILED: %s does not exist" % _rel(OUT))
            return 1
        stored = json.loads(OUT.read_text(encoding="utf-8"))
        a = {k: v for k, v in stored.items() if k not in CHECK_EXCLUDED_TOP_LEVEL}
        b = {k: v for k, v in result.items() if k not in CHECK_EXCLUDED_TOP_LEVEL}
        diffs = semantic_diff(a, b)
        if diffs:
            print("CHECK FAILED: %d difference(s) against the committed archive" % len(diffs))
            for d in diffs[:20]:
                print("   %s" % d)
            return 1
        print("CHECK OK: archive matches a fresh run (excluding %s; floats at rtol %g)"
              % (", ".join(CHECK_EXCLUDED_TOP_LEVEL), CHECK_RTOL))
        if not assured:
            print("CHECK FAILED: overall_PR03a_status = %s" % result["overall_PR03a_status"])
            return 1
        return 0

    if args.write:
        OUT.write_text(canonical(result), encoding="utf-8")
        print("wrote %s" % _rel(OUT))

    # Exact equality, not endswith: the previous verdict "PR03A_LIMIT_CONVERGENCE_NOT_ASSURED" also
    # ended in "ASSURED", so the suffix test exited 0 on failure. Every NOT_ASSURED run before that
    # fix reported success.
    return 0 if assured else 1


if __name__ == "__main__":
    raise SystemExit(main())

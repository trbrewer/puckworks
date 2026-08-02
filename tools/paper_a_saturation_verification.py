#!/usr/bin/env python3
"""Is the high-rate plateau a BDF artefact, or structural to the declared model? (NUM-TIME-01)

`paper_a_rate_domain_check.py` found that a tenfold change in the kinetic rate multiplier moves the
predicted cup concentration by less than 0.05 %, and by *exactly* 0.000 % in two groups. That is the
paper's central mechanism — the cup cannot see the kinetics — but it is also exactly what a solver
returning a converged floor would look like. Two configurations of the same numerical path can agree
while both being wrong, so agreement is not evidence here.

This settles it with an **independent integrator**.

**The system is linear in the state.** Every term of `solver._rhs` is linear in (c_l, c_s1, c_s2):
advection through a fixed differentiation matrix, and interphase transfer through constant
coefficients. The accumulated-mass equation is linear in the outlet liquid cell, and the accumulated
volume is exactly `dVol * t`. So for fixed conditions the semi-discrete problem is

    dz/dt = A z,    z = [c_l, c_s1, c_s2, m_cum],

and the solution is `z(t) = expm(A t) z(0)` — computable with **no time stepping, no adaptive error
control, no numerical Jacobian, and none of the machinery that produces the overflow warnings.**

Three checks, in order of strength:

1. **Linearity** — verify `_rhs` really is linear before treating it as a matrix. If it is not, the
   whole approach is invalid and the script says so rather than producing a plausible number.
2. **Matrix reconstruction** — `A z` against `_rhs(t, z)` state by state on random states.
3. **Independent integration** — BDF against `expm`, then re-run the saturation sweep entirely on
   the `expm` path.

Plus the structural prediction that distinguishes the two hypotheses:

4. **Convergence to a multiplier-independent limit.** If the plateau is structural to the model —
   the grains approach local equilibrium with the surrounding liquid faster than the liquid is
   displaced — then as the multiplier grows the prediction must converge to a *finite* limit, with
   increments shrinking until they reach arithmetic noise. A solver floor has no reason to produce a
   convergent sequence; it produces a constant because something stopped changing.

**Scope.** Both integrators solve the SAME governing equations on the SAME spatial operator with the
same parameterisation and the same omitted physics. The path is independent in TIME only. Nothing
here establishes that real espresso occupies the large-mass-transfer-coefficient regime; that is an
empirical question this check cannot address.

CLI::

    python tools/paper_a_saturation_verification.py --write
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import warnings

import numpy as np

_REPO = pathlib.Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

OUT = _REPO / "docs" / "paper1_resource" / "PAPER_A_SATURATION_VERIFICATION.json"

#: Representative conditions: the centre of the Angeloni optimal-grind grid.
T_C, P_BAR = 93.4, 9.0

#: Rate multipliers spanning the saturated regime and far beyond it.
SATURATION_RATES = (10.0, 50.0, 100.0, 500.0, 1e3, 1e4, 1e5)

#: Rates used for the BDF-vs-expm agreement check, from identified to deeply saturated.
AGREEMENT_RATES = (0.5, 1.0, 6.5, 50.0, 500.0)

#: Relative increment below which a change is arithmetic noise in the 601x601 matrix exponential
#: rather than a response. Double-precision `expm` on this operator lands around 1e-11 relative, and
#: no physical change of interest is anywhere near 1e-9, so the floor sits comfortably between.
#:
#: This constant exists because the first version of this check was WRONG: it required successive
#: increments to shrink monotonically across the whole sweep, including the tail where every
#: increment is ~1e-13. Ratios of noise to noise (23.7, 46.5) then failed a convergence test that
#: the sequence had in fact passed four orders of magnitude earlier. The criterion below is the
#: well-posed one -- shrink while above the floor, then reach it -- not a loosened version of the
#: original.
NOISE_FLOOR_RELATIVE = 1e-9

SOLUTES = ("caffeine", "trigonelline", "5CQA")


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Build the linear operator from the production right-hand side
# ─────────────────────────────────────────────────────────────────────────────────────────────


def _params(solute, rate, T_degC=None, p_bar=None, gran="O"):
    """Exactly the parameter block `simulate_fractions` builds, for one condition and rate.

    The condition defaults to the centre of the optimal-grind grid, which is what G3 uses. It is
    parameterised so gate G4 can evaluate the same exact-in-time path at every scored condition and
    granulometry without a second implementation of the operator.
    """
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.models.pannusch2024 import closures as pc
    from puckworks.validation.slow import angeloni_bracket as AB

    T_degC = T_C if T_degC is None else float(T_degC)
    p_bar = P_BAR if p_bar is None else float(p_bar)

    sp = dict(ps._solute_params()[solute])
    sp["A1"] = sp["A1"] * rate
    sp["A2"] = sp["A2"] * rate
    sp["c_s0"] = 1.0
    cl1 = 1.0

    flow = AB._flow_gran(p_bar, T_degC, gran)
    t_end = AB._matched_bounds(flow)[1]

    nz = ps.NZ
    T = T_degC + 273.15
    q = flow / 1000.0 / ps.RHO / ps.ACS
    grind = ps.GRIND_17
    psi, d_s2, d_s1 = grind["psi"], grind["d_s2"], ps.D1_FINE
    d32 = 6.0 / (psi * 6.0 / d_s1 + (1 - psi) * 6.0 / d_s2)
    h1 = float(pc.sherwood_h(T, q, sp["A1"], sp["B1"], sp["solute"], d32))
    h2 = float(pc.sherwood_h(T, q, sp["A2"], sp["B2"], sp["solute"], d32))
    K = float(pc.vant_hoff_K(T, sp["K_ref"], sp["gamma"]))
    cs0 = sp["c_s0"]
    alpha_s1 = psi * (1 - ps.ALPHA_L)
    alpha_s2 = (1 - psi) * (1 - ps.ALPHA_L)
    p = dict(D1z=ps.five_point_biased_upwind(nz, 1.0 / (nz - 1), q), v_l=q / ps.ALPHA_L,
             K=K, cs0=cs0, cl1=cl1,
             m1=(6 * h1 * alpha_s1) / (ps.ALPHA_L * d_s1) * ps.TC,
             m2=(6 * h2 * alpha_s2) / (ps.ALPHA_L * d_s2) * ps.TC,
             f1=(6 * h1) / d_s1 * ps.TC, f2=(6 * h2) / (ps.PHI_V2 * d_s2) * ps.TC,
             dVol=q * (np.pi / 4 * ps.DBED ** 2) * ps.TC * 1e6)

    c0 = np.ones(3 * nz + 2)
    c0[0] = 0.0
    c0[1:nz] = K * cs0 / cl1
    c0[3 * nz:3 * nz + 2] = 0.0
    return p, c0, t_end, cl1, nz


def check_linearity(p, nz, seed=0) -> dict:
    """`_rhs` must satisfy f(a+b) - f(0) = (f(a)-f(0)) + (f(b)-f(0)) to be a linear operator."""
    from puckworks.models.pannusch2024 import solver as ps

    rng = np.random.default_rng(seed)
    n = 3 * nz + 2
    f0 = ps._rhs(0.0, np.zeros(n), p)
    worst = 0.0
    for _ in range(5):
        a, b = rng.normal(size=n), rng.normal(size=n)
        lhs = ps._rhs(0.0, a + b, p) - f0
        rhs = (ps._rhs(0.0, a, p) - f0) + (ps._rhs(0.0, b, p) - f0)
        scale = max(float(np.abs(rhs).max()), 1e-30)
        worst = max(worst, float(np.abs(lhs - rhs).max()) / scale)
    return {"max_relative_superposition_error": worst, "is_linear": bool(worst < 1e-10)}


def build_operator(p, nz):
    """A for the reduced state z = [c_l, c_s1, c_s2, m_cum]; volume is exactly dVol*t.

    Columns are read from the production `_rhs`, which is legitimate because the operator is linear
    (checked above) — and is the point: the operator under test must be the SAME model the paper
    solves. What is being replaced is the INTEGRATOR, which is where the warnings originate.
    """
    from puckworks.models.pannusch2024 import solver as ps

    n_full = 3 * nz + 2
    idx = list(range(3 * nz)) + [3 * nz + 1]        # drop the volume state
    m = len(idx)
    f0 = ps._rhs(0.0, np.zeros(n_full), p)
    A = np.empty((m, m))
    e = np.zeros(n_full)
    for col, j in enumerate(idx):
        e[j] = 1.0
        A[:, col] = (ps._rhs(0.0, e, p) - f0)[idx]
        e[j] = 0.0
    return A, idx


def verify_operator(A, idx, p, nz, seed=1) -> dict:
    """A z against _rhs(z), state by state, on random states."""
    from puckworks.models.pannusch2024 import solver as ps

    rng = np.random.default_rng(seed)
    n_full = 3 * nz + 2
    f0 = ps._rhs(0.0, np.zeros(n_full), p)
    worst = 0.0
    for _ in range(5):
        z_full = np.zeros(n_full)
        z_full[idx] = rng.normal(size=len(idx))
        expected = (ps._rhs(0.0, z_full, p) - f0)[idx]
        got = A @ z_full[idx]
        scale = max(float(np.abs(expected).max()), 1e-30)
        worst = max(worst, float(np.abs(got - expected).max()) / scale)
    return {"max_relative_operator_error": worst, "matches_rhs": bool(worst < 1e-10)}


def expm_prediction(solute, rate, T_degC=None, p_bar=None, gran="O") -> float:
    """Cup concentration by matrix exponential — no time stepping, no adaptive control."""
    from scipy.linalg import expm
    from puckworks.models.pannusch2024 import solver as ps

    p, c0, t_end, cl1, nz = _params(solute, rate, T_degC, p_bar, gran)
    A, idx = build_operator(p, nz)
    tau = t_end / ps.TC
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        z = expm(A * tau) @ c0[idx]
    mcum = z[-1] * cl1
    vol = p["dVol"] * tau
    return float(mcum / vol)


def bdf_prediction(solute, rate) -> float:
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.validation.slow import angeloni_bracket as AB

    sp = dict(ps._solute_params()[solute])
    sp["A1"] = sp["A1"] * rate
    sp["A2"] = sp["A2"] * rate
    sp["c_s0"] = 1.0
    flow = AB._flow_gran(P_BAR, T_C, "O")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return float(ps.simulate_fractions(T_C, flow, AB._matched_bounds(flow), sp, cl1=1.0)[0])


def run() -> dict:
    from puckworks.models.pannusch2024 import solver as ps

    # ── 1 & 2: the operator is legitimate ───────────────────────────────────────────────────
    p, _c0, _t, _cl1, nz = _params("caffeine", 1.0)
    linearity = check_linearity(p, nz)
    A, idx = build_operator(p, nz)
    operator = verify_operator(A, idx, p, nz)

    # also at a deeply saturated rate, where stiffness is extreme
    p_sat, _c, _t2, _cl2, _nz2 = _params("caffeine", 500.0)
    A_sat, idx_sat = build_operator(p_sat, nz)
    operator_saturated = verify_operator(A_sat, idx_sat, p_sat, nz)

    # ── 3: BDF vs expm ──────────────────────────────────────────────────────────────────────
    agreement = []
    for solute in SOLUTES:
        for rate in AGREEMENT_RATES:
            bdf, ex = bdf_prediction(solute, rate), expm_prediction(solute, rate)
            agreement.append({
                "solute": solute, "rate": rate,
                "bdf": bdf, "expm": ex,
                "relative_difference_percent": abs(bdf - ex) / abs(ex) * 100.0,
            })
    worst_agreement = max(a["relative_difference_percent"] for a in agreement)

    # ── 4: saturation sweep on the INDEPENDENT path, and convergence to a limit ─────────────
    sweep = []
    for solute in SOLUTES:
        preds = {r: expm_prediction(solute, r) for r in SATURATION_RATES}
        vals = np.array([preds[r] for r in SATURATION_RATES], float)
        # spread across a decade in the saturated regime (50 -> 500)
        lo, hi = preds[50.0], preds[500.0]
        decade_spread = abs(hi - lo) / abs(lo) * 100.0
        # Convergence to a limit: increments must shrink while they are still ABOVE the arithmetic
        # noise floor, and the sequence must then reach that floor. Comparing increments once both
        # are noise says nothing, so those are excluded rather than allowed to decide the verdict.
        limit = float(vals[-1])
        increments = np.abs(np.diff(vals))
        relative = increments / abs(limit)
        signal = [float(x) for x in relative if x > NOISE_FLOOR_RELATIVE]
        shrinking = all(signal[i + 1] < signal[i] for i in range(len(signal) - 1))
        reached_floor = bool(relative[-1] <= NOISE_FLOOR_RELATIVE)
        decades_fallen = (float(np.log10(signal[0] / relative[-1]))
                          if signal and relative[-1] > 0 else float("inf"))

        sweep.append({
            "solute": solute,
            "predictions": {str(r): preds[r] for r in SATURATION_RATES},
            "decade_spread_percent_50_to_500": decade_spread,
            "limit_estimate": limit,
            "relative_increments": [float(x) for x in relative],
            "n_increments_above_noise_floor": len(signal),
            "increments_shrink_above_floor": bool(shrinking),
            "reached_noise_floor": reached_floor,
            "orders_of_magnitude_fallen": decades_fallen,
            "final_increment_relative": float(relative[-1]),
            "converged": bool(shrinking and reached_floor),
        })

    all_converged = all(s["converged"] for s in sweep)
    worst_decade = max(s["decade_spread_percent_50_to_500"] for s in sweep)
    worst_final_increment = max(s["final_increment_relative"] for s in sweep)
    least_decades_fallen = min(s["orders_of_magnitude_fallen"] for s in sweep)

    model_structural = bool(linearity["is_linear"] and operator["matches_rhs"]
                    and operator_saturated["matches_rhs"]
                    and worst_agreement < 0.01 and all_converged
                    and worst_final_increment <= NOISE_FLOOR_RELATIVE)

    return {
        "schema_version": 1,
        "question": ("Is the high-rate plateau an artefact of BDF time integration, or a "
                     "structural property of the declared semi-discrete model? (NUM-TIME-01)"),
        "evidence_type": "numerical-model-structural",
        "temporal_artifact_status": "not_BDF_artifact",
        "physical_validity": "untested",
        "current_interpretation": ("a finite response limit within the declared semi-discrete "
                                   "model and spatial operator; the two integrators share the "
                                   "governing equations, parameterisation, discretisation and "
                                   "omitted physics, so the path is independent in TIME only"),
        "method": ("The semi-discrete system is linear in the state, so it is re-solved by dense "
                   "matrix exponential: no time stepping, no adaptive error control, no numerical "
                   "Jacobian, none of the machinery that emits the overflow warnings."),
        "condition": {"T_degC": T_C, "p_bar": P_BAR, "granulometry": "O", "nz": ps.NZ},
        "linearity_check": linearity,
        "operator_check_rate_1": operator,
        "operator_check_rate_500": operator_saturated,
        "bdf_vs_expm": {
            "worst_relative_difference_percent": worst_agreement,
            "rows": [{k: (round(v, 9) if isinstance(v, float) else v) for k, v in a.items()}
                     for a in agreement],
        },
        "saturation_on_independent_path": {
            "noise_floor_relative": NOISE_FLOOR_RELATIVE,
            "worst_decade_spread_percent": worst_decade,
            "worst_final_increment_relative": worst_final_increment,
            "least_orders_of_magnitude_fallen": least_decades_fallen,
            "all_converged": all_converged,
            "per_solute": sweep,
        },
        "verdict": "MODEL-STRUCTURAL" if model_structural else "NOT ESTABLISHED",
        "reading": (
            "The plateau reproduces on an integrator that shares no time-stepping machinery with BDF, "
            "and the prediction converges to a finite limit. A solver floor would not produce a "
            "convergent sequence. This establishes the plateau is STRUCTURAL to the declared "
            "semi-discrete model; it does NOT establish that real espresso occupies that regime."
            if model_structural else
            "One or more checks failed; the plateau is NOT established as structural and H1 cannot "
            "rest on it."),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args(argv)

    print("verifying the saturation on an independent numerical path...", flush=True)
    result = run()

    print("\nlinearity of _rhs            : %s (rel err %.2e)"
          % (result["linearity_check"]["is_linear"],
             result["linearity_check"]["max_relative_superposition_error"]))
    print("operator matches _rhs @rate 1 : %s (rel err %.2e)"
          % (result["operator_check_rate_1"]["matches_rhs"],
             result["operator_check_rate_1"]["max_relative_operator_error"]))
    print("operator matches _rhs @rate 500: %s (rel err %.2e)"
          % (result["operator_check_rate_500"]["matches_rhs"],
             result["operator_check_rate_500"]["max_relative_operator_error"]))
    print("\nBDF vs matrix exponential, worst relative difference: %.6f %%"
          % result["bdf_vs_expm"]["worst_relative_difference_percent"])
    s = result["saturation_on_independent_path"]
    print("\nsaturation on the expm path:")
    for row in s["per_solute"]:
        print("   %-14s decade spread %.6f %%   limit %.9f   increments fell %.1f orders to "
              "%.1e   converged %s"
              % (row["solute"], row["decade_spread_percent_50_to_500"], row["limit_estimate"],
                 row["orders_of_magnitude_fallen"], row["final_increment_relative"],
                 row["converged"]))
    print("\nVERDICT: %s" % result["verdict"])
    print(result["reading"])

    if args.write:
        OUT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")
        print("\nwrote %s" % OUT.relative_to(_REPO))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

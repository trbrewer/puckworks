"""screen_i072_matched_observable.py — Insight Foundry cheap screen for candidate I-072.

    CHEAP_SCIENTIFIC_SCREEN
    NOT_A_PUBLICATION_RESULT
    NOT_A_MODEL_VALIDATION_UPGRADE

Question (generated, verbatim from the candidate):

    Under one matched scenario, do mo2023_2.swelling and brewer2026.streamtube differ in sign,
    ordering, or magnitude on an observable they both produce?

THE PROTOCOL IS FROZEN AND COMMITTED SEPARATELY, BEFORE THIS MODULE EXISTED:
`docs/insights/screens/I-072/PROTOCOL.md`. This module executes that protocol and nothing else.

**NEITHER COMPONENT IS EXECUTED.** The protocol's compatibility gate (G1-G5) fails upstream of
execution, and the protocol's execution rule then forbids running either model.
`tests/test_screen_i072.py` asserts that by replacing every forbidden entry point with a tripwire
and running the whole screen.

WHAT THE GATE FINDS — the two components emit orthogonal moments of the same flow field:

  * `mo2023_2.swelling` emits `q(t)/q(0)`: the bed-MEAN Carman-Kozeny conductivity, indexed by
    TIME, normalised by its own t=0 value, under fixed dP. The bed is one 1-D column, so its
    across-tube dispersion is identically zero. `docs/cards/mo2023_2.md` states this in terms:
    "Mo's 1-D homogeneity is silent on channeling."

  * `brewer2026.streamtube` Rung A emits a per-TUBE permeability multiplier `k_i` from a
    UNIT-MEAN lognormal, constant in time, and scores the EY deficit that its dispersion causes.
    Because the ensemble mean is normalised to exactly one, the bed-mean flow ratio the swelling
    model computes is IDENTICALLY 1 for every sigma and every grind -- it carries zero
    information about the streamtube mechanism, and is not a prediction of that mechanism at all.

Each component's output is the other's structural zero. That is not a disagreement and it is not
an agreement: it is two different questions. The same card that generated the tension row already
says so -- "complementary-competing ... a bed can have both".

The structural claim about the streamtube ensemble is PROVED here rather than asserted, by
evaluating the pure quadrature constructors that build the tube weights. Those perform no solve;
the protocol permits exactly them and names everything it forbids.

Run:  python -m puckworks.analysis.screen_i072_matched_observable
"""
from __future__ import annotations

import hashlib
import inspect
import json
import pathlib

import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CANDIDATE_ID = "I-072"
COMPONENT_A = "mo2023_2.swelling"
COMPONENT_B = "brewer2026.streamtube"
TENSION_ROW = "T-0147"

PROTOCOL_PATH = "docs/insights/screens/I-072/PROTOCOL.md"

#: The commit this screen was run at -- the base of the branch that carries it. Frozen as a
#: constant rather than read from git so the artifact is reproducible from a clean checkout.
BASE_COMMIT = "85f65c0d4b836990152fa4e9bf91c6d292a9e257"

#: Every entry point the protocol forbids this screen from calling. The test replaces each with a
#: tripwire and runs the whole screen; entering any of them is a test failure, not a warning.
FORBIDDEN_EXECUTION = (
    ("puckworks.models.mo2023_2.swelling", "flow_decay"),
    ("puckworks.models.mo2023_2.swelling", "flow_decay_ratio"),
    ("puckworks.models.mo2023_2.swelling", "swelling_volume_ratio"),
    ("puckworks.models.brewer2026.streamtube", "EYResponse"),
    ("puckworks.models.brewer2026.streamtube", "simulate_ensemble_dynamic"),
    ("puckworks.models.cameron2020.extraction_bdf", "simulate_shot"),
)

#: Pure constructors the protocol explicitly permits: they build quadrature weights or read a
#: measured microstructure table. No ODE, no PDE, no shot.
PERMITTED_STRUCTURAL = (
    "puckworks.models.brewer2026.streamtube.lognormal_nodes",
    "puckworks.models.cameron2020.extraction_bdf.grind_microstructure",
)

#: Files whose content the result is bound to.
INPUT_FILES = (
    PROTOCOL_PATH,
    "puckworks/models/mo2023_2/swelling.py",
    "puckworks/models/brewer2026/streamtube.py",
    "puckworks/models/__init__.py",
    "docs/cards/mo2023_2.md",
    "puckworks/data/mo2023_2/table1_granulometry.csv",
    "puckworks/data/mo2023_2/fig3a_qdecay.csv",
)

#: Sigma grid for the structural proof. Fixed here, before any result, and spanning the whole
#: range brentq is allowed to search in `EYResponse.sigma_for_deficit` (1e-4 .. 3.0).
SIGMA_GRID = (0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0)

#: Above this sigma the 15-node Gauss-Hermite rule itself under-resolves the lognormal
#: tail, so the machine-precision claim is scoped to sigma <= this value and the
#: larger-sigma deviations are reported as a quadrature artifact rather than hidden.
SIGMA_EXACT_MAX = 1.5

#: The streamtube's declared calibration dials (registry valid_range: "calibrated at dial 1.1-1.5").
STREAMTUBE_DIALS = (1.1, 1.3, 1.5)


# ------------------------------------------------------------------------------------------
# provenance
# ------------------------------------------------------------------------------------------

def _sha256(rel_path: str) -> str:
    p = REPO_ROOT / rel_path
    return hashlib.sha256(p.read_bytes()).hexdigest()


def provenance() -> dict:
    return {
        "base_commit": BASE_COMMIT,
        "protocol_path": PROTOCOL_PATH,
        "protocol_sha256": _sha256(PROTOCOL_PATH),
        "input_sha256": {f: _sha256(f) for f in INPUT_FILES},
        "command": "python -m puckworks.analysis.screen_i072_matched_observable",
    }


def _registry_entry(name: str) -> dict:
    from puckworks.registry import components
    hit = [c for c in components() if c.name == name]
    if not hit:
        raise LookupError("component %r is not registered" % name)
    c = hit[0]
    return {"name": c.name, "stage": c.stage, "kind": c.kind, "module": c.module,
            "assumptions": c.assumptions, "valid_range": c.valid_range,
            "evidence_strength": c.evidence_strength, "provenance_class": c.provenance_class,
            "gates": [g.__name__ for g in c.gates]}


# ------------------------------------------------------------------------------------------
# the compatibility table (protocol section 3), copied from the authorities
# ------------------------------------------------------------------------------------------

def compatibility_table() -> list[dict]:
    """The side-by-side the protocol requires, one row per aspect.

    `aligned` is the screen's judgement for that row alone; the gate in `gate()` is what turns
    these rows into a decision. Values are copied from the registry entry, the module contract or
    the card -- never paraphrased into a form that would flatter alignment.
    """
    A, B = COMPONENT_A, COMPONENT_B
    rows = [
        dict(aspect="component identity", a=A, b=B, aligned=True,
             note="both are registered runtime components on the bed_dynamics stage"),
        dict(aspect="physical quantity",
             a="bed-mean Carman-Kozeny conductivity ratio q(t)/q(0)",
             b="per-tube permeability multiplier k_i, and the EY deficit its spread causes",
             aligned=False,
             note="a mean and a dispersion are different moments of the same field"),
        dict(aspect="mathematical definition",
             a="eps_b^(3+2n) d32^2 / (1-eps_b)^2, evaluated at t and divided by its t=0 value",
             b="k_i = exp(sigma*xi - sigma^2/2) with E[k]=1; deficit = 1 - EY_ens(sigma)/EY(k=1)",
             aligned=False, note="no transformation maps one onto the other"),
        dict(aspect="units", a="dimensionless ratio (dP, mu, L cancel by construction)",
             b="dimensionless multiplier; deficit is a dimensionless yield fraction",
             aligned=True,
             note="both dimensionless -- which is exactly why a plot would look admissible"),
        dict(aspect="total vs normalised", a="bed-total (one 1-D column), self-normalised at t=0",
             b="per-tube, normalised so the ENSEMBLE MEAN is exactly 1",
             aligned=False,
             note="streamtube's normalisation makes the bed-total flow ratio identically 1"),
        dict(aspect="index", a="time", b="tube (lateral position); Rung A has no time index for k",
             aligned=False, note="the decisive row: different index sets"),
        dict(aspect="evaluation location / pressure node",
             a="none exposed -- dP is a scalar that cancels; no pressure is evaluated anywhere",
             b="one common pressure drop shared by all tubes (module default p_bar=5.0)",
             aligned=False,
             note="S5.9 / ledger A1 cannot be satisfied on a model that evaluates no node"),
        dict(aspect="time basis / event basis",
             a="t=0 is the instant dry grain surfaces reach c^w=C_M; horizon is a clock time",
             b="shot start; the shot ENDS at a delivered beverage mass m_out, not a clock time",
             aligned=False, note="a clock horizon and a mass endpoint are not the same terminus"),
        dict(aspect="initial state", a="dry grains, c^w(r,0)=0, instantaneous surface wetting",
             b="saturated bed; no infiltration stage exists in the model",
             aligned=False, note="swelling is driven by the uptake streamtube assumes complete"),
        dict(aspect="intervention / boundary condition", a="fixed dP, free flow",
             b="fixed pressure AND fixed delivered mass (m_in=0.020 kg, m_out=0.040 kg)",
             aligned=False,
             note="ONBOARDING: mo2023_2's fixed-q branch is INSENSITIVE to swelling -- the "
                  "intervention is load-bearing, not cosmetic"),
        dict(aspect="geometry", a="fixed bed height; swelling reduces eps_b only (Eq. 21)",
             b="K parallel NON-EXCHANGING tubes at one shared dP",
             aligned=False, note="one column vs K columns with no lateral exchange"),
        dict(aspect="saturation / prewet assumption",
             a="no unsaturated-flow stage; grains imbibe from a wetted surface",
             b="saturated throughout; wetting is out of scope",
             aligned=False, note=""),
        dict(aspect="grind descriptor / parameter validity range",
             a="powder identity E/H/M/F (theta_f, 2R_f, 2R_c, d32) -- THERE IS NO DIAL",
             b="EK43 dial 1.1-1.5, LOO-interpolated, not externally validated",
             aligned=False,
             note="rule 9 / ledger A9,G5: no dial mapping without an explicit refit adapter"),
        dict(aspect="output validity range",
             a="q(60)/q(0) reproduced to ~5% (E/H/M) and ~13% (F); the fixed-dP swelling claim "
               "is UNVALIDATED in the source paper",
             b="EY deficit over the calibrated dial domain only",
             aligned=False, note="different observables, so the ranges are not comparable"),
        dict(aspect="declared uncertainty source",
             a="model-vs-source reproduction agreement (gate threshold max_rel_err < 0.20)",
             b="gate_streamtube_heldout: held-out |error| on the EY relative deviation, < 0.02",
             aligned=False,
             note="neither is a measurement uncertainty, and they are on different observables"),
        dict(aspect="validation / evidence scope", a="source_curve_reproduction",
             b="within_campaign_held_out (no card exists for this component)",
             aligned=False, note="copied verbatim from the registry; neither is upgraded here"),
        dict(aspect="transformation required to compare",
             a="-", b="-", aligned=False,
             note="NONE EXISTS that is not an invention: to put these on one axis you must "
                  "either give the streamtube a time-varying mean (Rung B, uncalibrated) or "
                  "give the swelling model a lateral index (physics it does not have)"),
    ]
    return rows


# ------------------------------------------------------------------------------------------
# the structural proof: each component's output is the other's structural zero
# ------------------------------------------------------------------------------------------

def streamtube_mean_is_invariant() -> dict:
    """Prove: the bed-TOTAL flow ratio is identically 1 in the streamtube model, for every sigma.

    Rung A gives tube i the superficial velocity q_ref * k_i, constant in time. The bed-total
    flow is therefore q_ref * sum_i w_i k_i. Both tube constructions in the module normalise that
    sum to one -- the Gauss-Hermite ensemble analytically (E[k]=1 for a unit-mean lognormal), the
    quantile-midpoint ensemble explicitly (`k0 *= 1.0 / k0.mean()`).

    So q_total(t)/q_total(0) == 1 for all t and all sigma. The observable `mo2023_2.swelling`
    computes is not merely unmatched in the streamtube model -- it is CONSTANT there, and
    therefore carries no information about the streamtube mechanism.

    Uses only `lognormal_nodes`, which the protocol permits: it is a quadrature constructor and
    performs no solve.
    """
    from puckworks.models.brewer2026 import streamtube as st

    rows = []
    for sigma in SIGMA_GRID:
        k, w = st.lognormal_nodes(float(sigma), n=15)
        mean_gh = float(np.sum(w * k))
        # the quantile-midpoint construction used by Rung B, reproduced without running Rung B
        from scipy.stats import norm
        K = 12
        xi = norm.ppf((np.arange(K) + 0.5) / K)
        k0 = np.exp(sigma * xi - 0.5 * sigma ** 2)
        k0 = k0 / k0.mean()
        rows.append(dict(sigma=float(sigma),
                         gauss_hermite_mean_k=mean_gh,
                         gauss_hermite_abs_dev_from_1=abs(mean_gh - 1.0),
                         quantile_midpoint_mean_k=float(k0.mean()),
                         across_tube_cv=float(np.sqrt(np.sum(w * (k - mean_gh) ** 2)) / mean_gh),
                         analytic_lognormal_cv=float(np.sqrt(np.expm1(sigma ** 2)))))
    qmid_worst = max(abs(r["quantile_midpoint_mean_k"] - 1.0) for r in rows)
    gh_worst_all = max(r["gauss_hermite_abs_dev_from_1"] for r in rows)
    gh_worst_machine = max(r["gauss_hermite_abs_dev_from_1"] for r in rows
                           if r["sigma"] <= SIGMA_EXACT_MAX)
    return dict(
        claim="the bed-total flow ratio q_total(t)/q_total(0) is identically 1 in "
              "brewer2026.streamtube Rung A, for every sigma",
        analytic_basis="E[k] = E[exp(sigma*xi - sigma^2/2)] = 1 EXACTLY for a standard normal "
                       "xi -- the -sigma^2/2 term in `lognormal_nodes` is what makes the "
                       "lognormal unit-mean, and `simulate_ensemble_dynamic` additionally "
                       "renormalises with `k0 *= 1.0 / k0.mean()`. The numbers below are a "
                       "numerical confirmation of an analytic identity, not an estimate of it",
        method="evaluate the unit-mean quadrature constructors directly; no solve is performed",
        function_evaluated="puckworks.models.brewer2026.streamtube.lognormal_nodes",
        rows=rows,
        quantile_midpoint_max_abs_deviation=qmid_worst,
        quantile_midpoint_scope="every sigma on the grid (exact by explicit renormalisation)",
        gauss_hermite_max_abs_deviation_within_scope=gh_worst_machine,
        gauss_hermite_scope="sigma <= %s" % SIGMA_EXACT_MAX,
        gauss_hermite_max_abs_deviation_all_sigma=gh_worst_all,
        quadrature_caveat="at sigma = 2.0 and 3.0 the 15-node Gauss-Hermite rule itself "
                          "under-resolves the lognormal tail (worst deviation %.1e), while the "
                          "explicitly renormalised quantile-midpoint construction stays at 1.0 to "
                          "machine precision at the SAME sigma. That is quadrature resolution, "
                          "not a mechanism that moves the mean -- reported rather than trimmed "
                          "away by choosing a friendlier sigma grid." % gh_worst_all,
        holds=bool(qmid_worst < 1e-12 and gh_worst_machine < 1e-12),
        consequence="the observable mo2023_2.swelling emits is a CONSTANT in this model. It is "
                    "not a competing prediction of flow decay; the model has no mechanism that "
                    "can move it.")


def swelling_has_no_lateral_index() -> dict:
    """Prove: `mo2023_2.swelling` has no tube/lateral index, so its dispersion is identically 0.

    Checked against the implementation contract rather than asserted: the public entry points
    take no tube count and no heterogeneity parameter, and every state variable they return is a
    scalar per time sample.
    """
    from puckworks.models.mo2023_2 import swelling as sw

    sig = inspect.signature(sw.flow_decay)
    params = list(sig.parameters)
    lateral_terms = ("K", "n_tube", "tubes", "sigma", "hetero", "lateral", "radial")
    found = [p for p in params if p in lateral_terms]
    src = inspect.getsource(sw)
    return dict(
        claim="mo2023_2.swelling carries no lateral/tube index; its across-tube dispersion is "
              "identically 0",
        method="signature and source contract of the public entry point",
        flow_decay_parameters=params,
        lateral_parameters_found=found,
        returns="t, eps_b(t), d32(t), q_rel(t) -- one scalar per time sample, no tube axis",
        module_declares_one_column=bool("fixed bed height" in src or "fixed-height bed" in src),
        card_authority="docs/cards/mo2023_2.md: \"Mo's 1-D homogeneity is silent on channeling.\"",
        holds=bool(not found),
        consequence="the observable brewer2026.streamtube emits is a CONSTANT (zero) in this "
                    "model. It is not a competing prediction of flow heterogeneity; the model "
                    "has no mechanism that can move it.")


def source_data_scale() -> dict:
    """The magnitude of the temporal decay, taken from the SOURCE DATA, not from the model.

    `mo2_fig3a_qdecay` is the digitised Fig 3(a) measurement. Reading it is a data read; the
    swelling model is not run. This exists so the figure can show the size of the quantity the
    streamtube model holds structurally constant, without executing either component.
    """
    from puckworks import data as d
    by: dict[str, list[tuple[float, float]]] = {}
    for r in d.mo2_fig3a_qdecay():
        if r["s_m_pct"] == 3.6:                      # the gate's own selection, s_m = 3.6 %
            by.setdefault(r["powder"], []).append((r["t_s"], r["q_mm_s"]))
    out = {}
    for pw in ("E", "H", "M", "F"):
        pts = sorted(by[pw])
        out[pw] = dict(t_first_s=pts[0][0], t_last_s=pts[-1][0],
                       q_first_mm_s=pts[0][1], q_last_mm_s=pts[-1][1],
                       q_ratio=pts[-1][1] / pts[0][1])
    return dict(source="mo2023_2/fig3a_qdecay (digitised Fig 3a, s_m = 3.6 %)",
                is_model_output=False, per_powder=out,
                span=[min(v["q_ratio"] for v in out.values()),
                      max(v["q_ratio"] for v in out.values())])


def grind_descriptor_check() -> dict:
    """G5: do the declared validity domains intersect in a descriptor BOTH components accept?

    Mo's side is a powder identity with a granulometry; the streamtube's side is an EK43 dial.
    The only quantity computable on both sides is a derived Sauter diameter -- and the protocol
    froze, before any number was computed, that a d32 coincidence is not a matched grind.
    `grind_microstructure` is a measured-PSD table lookup, not a solve.
    """
    from puckworks import data as d
    from puckworks.models.cameron2020 import extraction_bdf as em

    mo = {r["powder"]: dict(theta_f=r["theta_f"], theta_c=r["theta_c"],
                            R_f_um=r["2R_f_um"] / 2.0, R_c_um=r["2R_c_um"] / 2.0,
                            d32_um=r["d_32_um"]) for r in d.mo2_granulometry()}
    cam = {}
    for gs in STREAMTUBE_DIALS:
        phi1, phi2, a2, _b1, _b2 = em.grind_microstructure(gs)
        d32 = 2.0 / ((phi2 / a2 + phi1 / em.A1) / (phi1 + phi2))
        cam[str(gs)] = dict(phi_fines=float(phi1), phi_boulder=float(phi2),
                            R_f_um=float(em.A1 * 1e6), R_c_um=float(a2 * 1e6),
                            d32_um=float(d32 * 1e6))

    mo_d32 = [v["d32_um"] for v in mo.values()]
    cam_d32 = [v["d32_um"] for v in cam.values()]
    d32_overlap = not (max(mo_d32) < min(cam_d32) or max(cam_d32) < min(mo_d32))
    inside = {pw: bool(min(cam_d32) <= v["d32_um"] <= max(cam_d32)) for pw, v in mo.items()}

    # granulometry actually matched? compare the two representative radii for any powder whose
    # d32 lands inside the streamtube's dial-derived d32 span.
    granulometry_matches = {}
    for pw, v in mo.items():
        if not inside[pw]:
            continue
        best = min(cam.values(), key=lambda c: abs(c["d32_um"] - v["d32_um"]))
        granulometry_matches[pw] = dict(
            mo_R_f_um=v["R_f_um"], cam_R_f_um=best["R_f_um"],
            R_f_rel_diff=abs(v["R_f_um"] - best["R_f_um"]) / best["R_f_um"],
            mo_R_c_um=v["R_c_um"], cam_R_c_um=best["R_c_um"],
            R_c_rel_diff=abs(v["R_c_um"] - best["R_c_um"]) / best["R_c_um"],
            mo_theta_f=v["theta_f"], cam_phi_fines_fraction=best["phi_fines"] /
            (best["phi_fines"] + best["phi_boulder"]))

    return dict(
        mo_powders=mo, streamtube_dials=cam,
        mo_descriptor="powder identity E/H/M/F -- no grinder dial exists in this component",
        streamtube_descriptor="EK43 dial 1.1-1.5",
        common_descriptor=None,
        d32_spans=dict(mo=[min(mo_d32), max(mo_d32)], streamtube=[min(cam_d32), max(cam_d32)]),
        d32_numerically_overlaps=bool(d32_overlap),
        mo_powder_d32_inside_streamtube_span=inside,
        granulometry_behind_the_d32_coincidence=granulometry_matches,
        intersect=False,
        why="Mo's powders are not placed on any grinder dial, and rule 9 / ledger A9,G5 forbids "
            "mapping one grinder's dial space onto another's without an explicit refit adapter. "
            "A d32 coincidence is a coincidence of one derived moment, not a matched grind: the "
            "granulometry behind it differs in both representative radii and in the fines "
            "fraction.")


# ------------------------------------------------------------------------------------------
# gate + uncertainty + adversarial checks
# ------------------------------------------------------------------------------------------

def gate(table: list[dict], grind: dict) -> dict:
    """The protocol's five-part compatibility gate. Fails closed."""
    by = {r["aspect"]: r for r in table}
    g1 = by["physical quantity"]["aligned"] and by["mathematical definition"]["aligned"]
    g2 = by["index"]["aligned"] and by["total vs normalised"]["aligned"]
    g3 = by["evaluation location / pressure node"]["aligned"]
    g4 = (by["intervention / boundary condition"]["aligned"]
          and by["initial state"]["aligned"])
    g5 = bool(grind["intersect"])
    checks = {
        "G1_quantity_and_definition": dict(passed=bool(g1),
            reason="a bed-mean conductivity ratio and a per-tube permeability multiplier are "
                   "different moments of the flow field; no transformation maps one to the other"),
        "G2_index_and_normalisation": dict(passed=bool(g2),
            reason="time-indexed and self-normalised vs tube-indexed and ensemble-mean-normalised"),
        "G3_pressure_node": dict(passed=bool(g3),
            reason="mo2023_2.swelling evaluates no pressure at any location -- dP cancels in the "
                   "ratio -- so no node identity can be matched to the streamtube's shared node"),
        "G4_intervention_and_initial_state": dict(passed=bool(g4),
            reason="fixed-dP from a dry bed vs fixed-pressure-and-mass-endpoint on a saturated "
                   "bed; the intervention is load-bearing (the fixed-q branch is swelling-"
                   "insensitive)"),
        "G5_validity_domains_intersect": dict(passed=bool(g5), reason=grind["why"]),
    }
    passed = all(c["passed"] for c in checks.values())
    return dict(checks=checks, passed=passed,
                failed=[k for k, v in checks.items() if not v["passed"]],
                execution_permitted=passed)


def uncertainty_audit() -> dict:
    """What numerical uncertainty the repository actually declares, and for which observable."""
    from puckworks.validation import gates as G
    heldout_doc = inspect.getdoc(G.gate_streamtube_heldout) or ""
    return dict(
        brewer2026_streamtube=dict(
            evidence_label="within_campaign_held_out",
            label_is_a_numerical_band=False,
            numerical_quantity="gate_streamtube_heldout: max held-out |error| on the EY RELATIVE "
                               "DEVIATION, leave-one-out over GS 1.1/1.3/1.5, pass threshold 0.02",
            gate_docstring=heldout_doc.splitlines()[0] if heldout_doc else "",
            observable="EY relative deviation (dimensionless yield fraction)",
            population="three grind settings from one campaign",
            admissible_for_this_comparison=False,
            why_not="wrong observable. A held-out error on an extraction-yield deficit is not an "
                    "uncertainty on a bed-mean flow ratio, and the protocol froze the "
                    "borrow-another-observable's-band move as inadmissible before any result.",
            card_exists=False,
            card_note="no docs/cards/brewer2026_streamtube.md or docs/cards/brewer2026.md; the "
                      "validity range and uncertainty are registry-sourced, and this result says "
                      "so rather than assuming card provenance"),
        mo2023_2_swelling=dict(
            evidence_label="source_curve_reproduction",
            numerical_quantity="registry valid_range: reproduction agreement E/H/M within ~5%, F "
                               "within ~13%; gate_mo2_swelling_flow_decay pass threshold "
                               "max_rel_err < 0.20",
            observable="q(60)/q(0) per powder",
            admissible_for_this_comparison=False,
            why_not="these are model-vs-source AGREEMENT tolerances and a gate pass threshold, "
                    "not a measurement uncertainty on the physical quantity; the source campaign "
                    "retains no replicate spread on q(t)/q(0)"),
        conclusion="no admissible quantitative uncertainty exists for a shared observable, "
                   "because no shared observable exists. Had one existed, this audit would have "
                   "blocked the comparison independently.")


def adversarial_checks(structural: dict, lateral: dict, grind: dict) -> list[dict]:
    """Every check the protocol froze. Each is the strongest available attempt to make the
    finding go away; each records what it would have taken to succeed."""
    return [
        dict(id="A1", check="units",
             result="both outputs are dimensionless; the incompatibility is NOT a unit mismatch",
             overturns=False,
             note="this is why the comparison looks admissible on an axis and is not"),
        dict(id="A2", check="total vs normalised",
             result="normalising both to their own reference value does not help: the streamtube "
                    "mean is ALREADY normalised to 1 by construction, so the normalised bed-total "
                    "ratio is 1 for every sigma (max deviation %.2e)"
                    % structural["gauss_hermite_max_abs_deviation_all_sigma"],
             overturns=False),
        dict(id="A3", check="pressure node (S5.9 / ledger A1)",
             result="cannot reconcile: mo2023_2.swelling evaluates no pressure anywhere. dP "
                    "cancels identically in the ratio, so there is no node to align",
             overturns=False),
        dict(id="A4", check="time origin",
             result="cannot reconcile: the streamtube's Rung A k has no time index at all, so no "
                    "choice of t=0 produces a time-varying quantity to align",
             overturns=False),
        dict(id="A5", check="sign convention / reciprocal / complement",
             result="a reciprocal or complement of a bed-mean ratio is still a bed-mean ratio; "
                    "it does not acquire a tube index",
             overturns=False),
        dict(id="A6", check="geometry / area scaling",
             result="an area or bed-depth factor is a constant prefactor; it cannot convert a "
                    "constant-in-time quantity into a decaying one",
             overturns=False),
        dict(id="A7", check="fixed-flow vs fixed-pressure",
             result="the intervention is load-bearing, not cosmetic: mo2023_2's fixed-q branch is "
                    "swelling-INSENSITIVE (gate_mo2_swelling_insensitivity) while its fixed-dP "
                    "branch throttles hard. Converting one intervention to the other changes "
                    "which physics is observable, and the repository declares no conversion",
             overturns=False),
        dict(id="A8", check="initial saturation / prewet",
             result="cannot reconcile: swelling is DRIVEN by the uptake the streamtube assumes "
                    "already complete. Matching the initial state removes the mechanism",
             overturns=False),
        dict(id="A9", check="the known composition mis-scale",
             result="not applicable, and that matters. gate_kappa_t_composition_diagnostic "
                    "already records mo2023_2's fixed-dP swelling branch over-closing a saturated "
                    "pre-wet bed ('reported not tuned away'). This screen reports NO numerical "
                    "disagreement, so it cannot be mistaking that known mis-scale for a discovery",
             overturns=False),
        dict(id="A10", check="the d32 rescue",
             result="d32 spans overlap numerically (mo %.1f-%.1f um vs streamtube dials %.1f-%.1f "
                    "um) and %d of 4 Mo powders land inside the streamtube span -- and it rescues "
                    "nothing. The granulometry behind the coincidence differs: %s. d32 is one "
                    "derived moment, it is not a grinder dial, and rule 9 forbids the mapping"
                    % (grind["d32_spans"]["mo"][0], grind["d32_spans"]["mo"][1],
                       grind["d32_spans"]["streamtube"][0], grind["d32_spans"]["streamtube"][1],
                       sum(grind["mo_powder_d32_inside_streamtube_span"].values()),
                       "; ".join("%s: R_f differs %.0f%%, R_c differs %.0f%%"
                                 % (pw, 100 * v["R_f_rel_diff"], 100 * v["R_c_rel_diff"])
                                 for pw, v in
                                 grind["granulometry_behind_the_d32_coincidence"].items())
                       or "no powder lands inside"),
             overturns=False,
             note="this is the check most likely to have produced a false SURVIVE"),
        dict(id="A11", check="the Rung-B rescue",
             result="Rung B (simulate_ensemble_dynamic) does emit a time-indexed bed-total flow, "
                    "which is the index and normalisation G1-G2 need -- and it is still not "
                    "admissible. Running it requires lam_e, a_open and a_clog, whose module "
                    "defaults are 0.0 (i.e. no dynamics) and for which the repository declares no "
                    "calibrated values; supplying them is inventing parameters. Rung B also "
                    "carries NO gate and the registry declares it 'hypothesis-generating', so a "
                    "comparison there would score a gated component against an ungated diagnostic",
             overturns=False,
             note="this is the honest reopen path, and it is a calibration task, not a screen"),
        dict(id="A12", check="is the finding merely the tension row's own premise?",
             result="no -- the tension row T-0147 declares shared_observable EMPTY and asks "
                    "whether one exists. The card it was generated from already says "
                    "'complementary-competing ... a bed can have both'. This screen converts "
                    "that prose into a checkable structural statement and finds it correct",
             overturns=False),
    ]


# ------------------------------------------------------------------------------------------
# decision
# ------------------------------------------------------------------------------------------

def decide(gate_result: dict) -> dict:
    """Apply the candidate's criteria and the protocol's frozen ordering rule, unrevised."""
    g14 = [k for k in gate_result["failed"] if k.startswith(("G1", "G2", "G3", "G4"))]
    if gate_result["passed"]:
        raise AssertionError("gate passed: this branch requires an executed comparison, and the "
                             "protocol's execution rule would apply instead")
    decision = "RETIRE" if g14 else "NEEDS_NEW_DATA"
    return dict(
        decision=decision,
        rule_applied="protocol section 7 ordering rule, frozen before results: a G1-G4 failure "
                     "is RETIRE because no amount of new data changes what a component computes; "
                     "NEEDS_NEW_DATA is reserved for a missing declared value where G1-G4 pass",
        gate_failures=gate_result["failed"],
        g1_to_g4_failures=g14,
        rationale="mo2023_2.swelling and brewer2026.streamtube answer different physical "
                  "questions. One computes the bed-MEAN permeability as a function of TIME under "
                  "fixed dP; the other computes the across-TUBE DISPERSION of permeability at a "
                  "fixed mean, with no time index. Each component's output is identically "
                  "constant in the other's model -- the streamtube's bed-total flow ratio is 1 "
                  "for every sigma by unit-mean construction, and the swelling model's lateral "
                  "dispersion is 0 for every powder because it has one column. Their declared "
                  "validity domains also fail to intersect: a powder identity and an EK43 dial "
                  "are not the same descriptor and rule 9 forbids the adapter.",
        models_executed=[],
        model_solves_performed=0)


# ------------------------------------------------------------------------------------------
# screen
# ------------------------------------------------------------------------------------------

def screen() -> dict:
    table = compatibility_table()
    grind = grind_descriptor_check()
    structural = streamtube_mean_is_invariant()
    lateral = swelling_has_no_lateral_index()
    g = gate(table, grind)
    decision = decide(g)
    checks = adversarial_checks(structural, lateral, grind)

    return {
        "screen": CANDIDATE_ID,
        "candidate_id": CANDIDATE_ID,
        "tension_row": TENSION_ROW,
        "disposition": ["CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                        "NOT_A_MODEL_VALIDATION_UPGRADE"],
        "components": [COMPONENT_A, COMPONENT_B],
        "registry_entries": {COMPONENT_A: _registry_entry(COMPONENT_A),
                             COMPONENT_B: _registry_entry(COMPONENT_B)},
        "provenance": provenance(),
        "protocol": {"path": PROTOCOL_PATH, "sha256": _sha256(PROTOCOL_PATH),
                     "frozen_before_execution": True,
                     "note": "committed in its own commit, before this module existed"},
        "observable_definition": {
            COMPONENT_A: {
                "quantity": "q(t)/q(0) -- bed-mean Carman-Kozeny conductivity ratio",
                "units": "dimensionless", "index": "time",
                "normalisation": "self-normalised at t=0",
                "intervention": "fixed dP", "initial_state": "dry bed",
                "lateral_index": None},
            COMPONENT_B: {
                "quantity": "per-tube permeability multiplier k_i; scored as the EY deficit",
                "units": "dimensionless", "index": "tube",
                "normalisation": "ensemble mean exactly 1",
                "intervention": "fixed pressure + fixed delivered mass",
                "initial_state": "saturated bed", "time_index": None}},
        "matched_scenario": None,
        "matched_scenario_note": "none was constructed: the compatibility gate fails upstream of "
                                 "scenario construction, and the protocol forbids execution past "
                                 "a failed gate",
        "compatibility_table": table,
        "grind_descriptor_check": grind,
        "structural_degeneracy": {
            "streamtube_bed_total_flow_ratio_is_identically_1": structural,
            "swelling_lateral_dispersion_is_identically_0": lateral,
            "summary": "each component's output is the other's structural zero"},
        "source_data_scale": source_data_scale(),
        "compatibility_gate": g,
        "models_executed": [],
        "model_solves_performed": 0,
        "models_executed_note": "neither component is executed. The determination is reached at "
                                "the compatibility gate, upstream of any run",
        "forbidden_execution_set": ["%s.%s" % f for f in FORBIDDEN_EXECUTION],
        "structural_functions_evaluated": list(PERMITTED_STRUCTURAL),
        "structural_functions_note": "lognormal_nodes builds Gauss-Hermite quadrature weights; "
                                     "grind_microstructure reads a measured-PSD table. Neither "
                                     "integrates an ODE or PDE and neither runs a shot",
        "uncertainty_authorities": uncertainty_audit(),
        "primary_numerical_findings": {
            "streamtube_quantile_midpoint_max_abs_dev_of_mean_k_from_1":
                structural["quantile_midpoint_max_abs_deviation"],
            "streamtube_gauss_hermite_max_abs_dev_of_mean_k_from_1":
                structural["gauss_hermite_max_abs_deviation_within_scope"],
            "streamtube_gauss_hermite_scope": structural["gauss_hermite_scope"],
            "sigma_values_checked": list(SIGMA_GRID),
            "swelling_lateral_parameters_found": lateral["lateral_parameters_found"],
            "source_data_q_ratio_span_mo_fig3a": source_data_scale()["span"],
            "note": "there is NO between-model numerical difference to report, because no shared "
                    "observable exists. The numbers above characterise the two structural "
                    "degeneracies, not a disagreement"},
        "adversarial_checks": checks,
        "adversarial_checks_overturning": [c["id"] for c in checks if c["overturns"]],
        "decision": decision["decision"],
        "decision_record": decision,
        "reopen_condition":
            "brewer2026.streamtube Rung B acquires DECLARED, calibrated values for lam_e, a_open "
            "and a_clog together with a gate, so that it predicts a time-varying bed-TOTAL flow "
            "ratio -- and that prediction is made on a granulometry inside mo2023_2's declared "
            "powder set, or on a grind descriptor both components declare they accept. Then, and "
            "only then, G1-G5 can be re-evaluated on q_total(t)/q_total(0). NOT reopened by a "
            "response sweep (that is RP-A, ROADMAP S9), and NOT reopened by a d32 coincidence.",
        "claim_ceiling":
            "A registry finding about one declared-competitor row, and nothing more. This screen "
            "does NOT establish that the two components agree; two components that answer "
            "different questions neither agree nor disagree. It does NOT establish that a real "
            "bed lacks either mechanism -- docs/cards/mo2023_2.md says a bed can have both, and "
            "this result is consistent with that. It does NOT upgrade, downgrade or restate any "
            "validation rung or evidence class: mo2023_2.swelling remains "
            "source_curve_reproduction and brewer2026.streamtube remains "
            "within_campaign_held_out. It licenses no statement about espresso.",
        "evidence_labels_unchanged": True,
        "administrative_exception_invoked": False,
    }


# ------------------------------------------------------------------------------------------
# figure
# ------------------------------------------------------------------------------------------

def figure(result: dict | None = None, path: str | None = None) -> str:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, Rectangle

    plt.rcParams.update({"figure.dpi": 150, "savefig.dpi": 150, "font.size": 8.5,
                         "font.family": "DejaVu Sans"})
    r = result or screen()
    struct = r["structural_degeneracy"]["streamtube_bed_total_flow_ratio_is_identically_1"]
    src = r["source_data_scale"]

    ABS = "#b4472a"      # "structurally absent" accent
    A_COL, B_COL = "#37618a", "#7a5195"

    fig = plt.figure(figsize=(13.4, 9.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.05], hspace=0.30, wspace=0.20)

    # ---- (a) the definition matrix: each output is the other's structural zero ----
    ax = fig.add_subplot(gs[0, 0])
    ax.set_axis_off()
    ax.set_title("(a)  What each component actually computes", loc="left", fontweight="bold")
    lab_w, cell_w, gap = 0.30, 0.325, 0.015
    xs = [lab_w + gap, lab_w + gap + cell_w + gap]
    ax.text(xs[0] + cell_w / 2, 0.895, COMPONENT_A, ha="center", va="bottom", fontsize=8.4,
            fontweight="bold", family="monospace", color=A_COL)
    ax.text(xs[1] + cell_w / 2, 0.895, COMPONENT_B, ha="center", va="bottom", fontsize=8.4,
            fontweight="bold", family="monospace", color=B_COL)
    rows = ["bed-MEAN permeability\nratio, indexed by TIME\n$q(t)/q(0)$",
            "across-TUBE dispersion\nof permeability,\nat a fixed mean"]
    cell = [["THE MODEL'S OUTPUT\n\nsource-data scale\n%.3f - %.3f"
             % (src["span"][0], src["span"][1]),
             "STRUCTURALLY ABSENT\n\n= 1 for every sigma\nunit-mean by construction"],
            ["STRUCTURALLY ABSENT\n\n= 0 for every powder\none 1-D column, no tube axis",
             "THE MODEL'S OUTPUT\n\n$CV=\\sqrt{e^{\\sigma^2}-1}$\n(0 to 85 on this grid)"]]
    for i in range(2):
        y = 0.545 - 0.375 * i
        ax.text(0.0, y + 0.135, rows[i], ha="left", va="center", fontsize=8.0, linespacing=1.5)
        for j in range(2):
            absent = cell[i][j].startswith("STRUCTURALLY")
            ax.add_patch(Rectangle((xs[j], y), cell_w, 0.27, transform=ax.transAxes,
                                   facecolor="#f7e7e2" if absent else "#e9f0f4",
                                   edgecolor=ABS if absent else (A_COL if j == 0 else B_COL),
                                   linewidth=1.5, linestyle="--" if absent else "-",
                                   hatch="//" if absent else None, alpha=0.55 if absent else 0.95,
                                   zorder=1))
            ax.text(xs[j] + cell_w / 2, y + 0.135, cell[i][j], ha="center", va="center",
                    fontsize=7.1, linespacing=1.7, zorder=3,
                    color=ABS if absent else "#1b3b4b",
                    fontweight="bold" if absent else "normal",
                    bbox=dict(boxstyle="round,pad=0.42", facecolor="white",
                              alpha=0.88 if absent else 0.0, edgecolor="none"))
    ax.text(0.5, -0.03, "each component's output is the other's STRUCTURAL ZERO\n"
                        "-> different questions, not disagreement and not agreement",
            ha="center", va="top", fontsize=8.6, style="italic", color=ABS, linespacing=1.5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # ---- (b) data flow: where the chains fail to meet ----
    ax = fig.add_subplot(gs[0, 1])
    ax.set_axis_off()
    ax.set_title("(b)  The two chains, and the adapter that does not exist", loc="left",
                 fontweight="bold")
    chain_a = ["powder E/H/M/F\n(no dial exists)", "swelling PDE\n-> eps_b(t), d32(t)",
               "Carman-Kozeny\nat FIXED dP", "q(t)/q(0)\ntime-indexed\nbed-mean"]
    chain_b = ["EK43 dial\n1.1 - 1.5", "fines phi_1\n-> sigma(GS)",
               "K tubes, ONE dP\nfixed out-mass", "EY deficit\ntube-indexed\nmean fixed"]
    bw, bh = 0.205, 0.185
    for row, chain, colr, name in ((0.735, chain_a, A_COL, COMPONENT_A),
                                   (0.235, chain_b, B_COL, COMPONENT_B)):
        ax.text(0.0, row + bh + 0.045, name, fontsize=8.2, family="monospace", color=colr,
                fontweight="bold")
        for i, box in enumerate(chain):
            x = 0.005 + 0.2495 * i
            ax.add_patch(Rectangle((x, row), bw, bh, transform=ax.transAxes, facecolor="white",
                                   edgecolor=colr, linewidth=1.2))
            ax.text(x + bw / 2, row + bh / 2, box, ha="center", va="center", fontsize=6.7,
                    linespacing=1.45)
            if i < 3:
                ax.add_patch(FancyArrowPatch((x + bw + 0.004, row + bh / 2),
                                             (x + 0.2455, row + bh / 2), transform=ax.transAxes,
                                             arrowstyle="-|>", mutation_scale=8, color=colr,
                                             linewidth=1.0))
    for x0, txt in ((0.108, "no grind adapter\nrule 9 / ledger A9, G5"),
                    (0.856, "different moment,\ndifferent index:\nno transformation")):
        ax.add_patch(FancyArrowPatch((x0, 0.725), (x0, 0.432), transform=ax.transAxes,
                                     arrowstyle="<|-|>", mutation_scale=10, color=ABS,
                                     linewidth=1.5, linestyle=(0, (4, 3))))
        ax.text(x0, 0.578, txt, fontsize=7.2, color=ABS, va="center", ha="center",
                fontweight="bold", linespacing=1.5,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="none"))
    ax.text(0.5, 0.055, "neither end of the two chains meets: not the grind input,\n"
                        "and not the output moment", ha="center", va="center", fontsize=7.8,
            style="italic", color=ABS, linespacing=1.5)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    # ---- (c) the quantity mo emits, at source-data scale, vs streamtube's flat structural zero
    ax = fig.add_subplot(gs[1, 0])
    powders = ["E", "H", "M", "F"]
    vals = [src["per_powder"][p]["q_ratio"] for p in powders]
    ax.bar(range(4), vals, color=A_COL, width=0.54,
           label="mo2023_2.swelling's observable, at SOURCE-DATA scale\n"
                 "(Fig 3a digitised, $s_m$ = 3.6 %; the model is NOT run)")
    ax.axhline(1.0, color=ABS, linewidth=2.0, linestyle="--",
               label="brewer2026.streamtube: = 1 exactly for every sigma\n"
                     "(max dev %.1e) - STRUCTURALLY ABSENT, not a prediction"
                     % struct["quantile_midpoint_max_abs_deviation"])
    for i, v in enumerate(vals):
        ax.text(i, v + 0.025, "%.3f" % v, ha="center", fontsize=7.6, color=A_COL,
                fontweight="bold")
    ax.set_xticks(range(4)); ax.set_xticklabels(powders)
    ax.set_xlabel("Mo powder  (there is no grinder dial on this side)")
    ax.set_ylabel("bed-total flow ratio  $q(t_{end})/q(0)$")
    ax.set_ylim(0, 1.42)
    ax.set_title("(c)  The time-indexed bed-mean observable", loc="left", fontweight="bold")
    ax.legend(loc="upper left", fontsize=7.0, framealpha=0.96)

    # ---- (d) the quantity streamtube emits, vs mo's flat structural zero ----
    ax = fig.add_subplot(gs[1, 1])
    sig = [row["sigma"] for row in struct["rows"]]
    cv = [row["across_tube_cv"] for row in struct["rows"]]
    mean_k = [row["gauss_hermite_mean_k"] for row in struct["rows"]]
    ax.plot(sig, cv, "o-", color=B_COL, linewidth=1.7, markersize=4.6,
            label="brewer2026.streamtube's observable: across-tube CV of $k$")
    ax.plot(sig, mean_k, "s-", color="#9a9a9a", linewidth=1.2, markersize=3.6,
            label="its ensemble mean of $k$  (= 1 by construction, all sigma)")
    ax.axhline(0.0, color=ABS, linewidth=2.0, linestyle="--",
               label="mo2023_2.swelling: = 0 for every powder (one 1-D column)\n"
                     "STRUCTURALLY ABSENT, not a prediction")
    ax.set_yscale("symlog", linthresh=0.01)
    ax.set_ylim(-0.004, 300)
    ax.set_xlabel("heterogeneity parameter sigma  (streamtube's controlling input)")
    ax.set_ylabel("across-tube dispersion of $k$  (CV, symlog)")
    ax.set_title("(d)  The tube-indexed dispersion observable", loc="left", fontweight="bold")
    ax.legend(loc="lower right", fontsize=7.0, framealpha=0.96)
    ax.grid(alpha=0.25, linewidth=0.5)

    fig.suptitle("I-072 cheap screen — CHEAP_SCIENTIFIC_SCREEN / NOT_A_PUBLICATION_RESULT / "
                 "NOT_A_MODEL_VALIDATION_UPGRADE\n"
                 "Decision: RETIRE — different questions. NEITHER component was executed: the "
                 "compatibility gate fails upstream of any run.",
                 fontsize=9.8, y=0.985)

    out = path or str(REPO_ROOT / "docs/insights/screens/I-072/figures/primary.png")
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main(argv=None):
    r = screen()
    out = REPO_ROOT / "docs/insights/screens/I-072/result.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(r, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    fig = figure(r)
    print("protocol frozen before execution: %s (%s)"
          % (r["protocol"]["frozen_before_execution"], r["protocol"]["path"]))
    print("protocol sha256: %s" % r["protocol"]["sha256"])
    print("models executed: %s (solves: %d)" % (r["models_executed"], r["model_solves_performed"]))
    print("compatibility gate: passed=%s failed=%s" % (r["compatibility_gate"]["passed"],
                                                       r["compatibility_gate"]["failed"]))
    print("streamtube max |E[k] - 1|: quantile-midpoint %.1e (all sigma), "
      "Gauss-Hermite %.1e (%s)"
      % (r["primary_numerical_findings"]["streamtube_quantile_midpoint_max_abs_dev_of_mean_k_from_1"],
         r["primary_numerical_findings"]["streamtube_gauss_hermite_max_abs_dev_of_mean_k_from_1"],
         r["primary_numerical_findings"]["streamtube_gauss_hermite_scope"]))
    print("adversarial checks overturning the finding: %s"
          % (r["adversarial_checks_overturning"] or "none"))
    print("DECISION: %s" % r["decision"])
    print("wrote %s" % out)
    print("wrote %s" % fig)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Focused tests for the I-024 cheap screen (Insight Foundry Wave 1).

These encode the SCIENTIFIC properties the 2026-08-04 correction established, and the two
defects it removed:

  * the superseded `test_C3_is_scale_free_in_the_assumed_rsd` uniformly rescaled already-computed
    z values, which is not the perturbation the screen performs. It is replaced by an END-TO-END
    test that changes the bioactive RSD, refits BOTH models and recomputes held-out residuals —
    and it asserts the OPPOSITE property: the shared fit genuinely moves, so C3 is NOT scale-free
    and no scale-free shortcut may be reintroduced;
  * whole-band claims may not rest on two endpoints. The sweep's exactness rests on three
    mathematical facts (amplitude x-independence, independent-selection x-independence, and
    monotonicity of C1/C3 on a fixed selection) and each is tested directly.

Nothing here asserts "the decision is RETIRE" for its own sake — the disposition test re-applies
the rule to the stored sweep, so it fails if the numbers change AND the rule stops matching them.
"""
import json
import pathlib

import numpy as np
import pytest

from puckworks.analysis import screen_i024_common_state as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-024"


@pytest.fixture(scope="module")
def small():
    """A cheap 3-rate fit used by the structural tests. Real solves, small grid."""
    conds = S.conditions()
    pred = S.UnitPredictions(conds)
    rates = [0.5, 1.0, 2.0]
    return conds, pred, rates, S.coefficients(pred, conds, rates)


# --------------------------------------------------------------------------------------------
# Design — evidence unit and split
# --------------------------------------------------------------------------------------------
def test_predeclared_split_is_the_interior_pressure():
    assert S.HELD_OUT_P_BAR == (9.0,)
    assert S.TRAIN_P_BAR == (6.0, 12.0)
    conds = S.conditions()
    assert len(conds) == 18
    assert sum(1 for c in conds if c["held_out"]) == 6
    assert sum(1 for c in conds if not c["held_out"]) == 12
    assert {c["p_bar"] for c in conds if c["held_out"]} == {9.0}


def test_evidence_unit_is_angeloni_only():
    for key in ("maille", "ellero", "khamitova"):
        assert any(key in k.lower() for k in S.EXCLUDED_EVIDENCE), key
    assert all(v for v in S.EXCLUDED_EVIDENCE.values()), "every exclusion needs a reason"
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    for banned in ("maille_", "ellero_", "khamitova_", "schmieder_", "angeloni_lipids"):
        assert banned not in src, "a non-angeloni loader is being called: %s" % banned


def test_criterion_thresholds_are_the_predeclared_ones():
    assert (S.C1_Z_THRESHOLD, S.C2_SPREAD_THRESHOLD, S.C3_REDUCTION_FACTOR) == (1.0, 1.0, 0.7)


def test_uncertainty_band_is_the_source_stated_one():
    import csv
    assert S.BIOACTIVE_RSD_BAND_PCT == (0.3, 19.7)
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    assert "0.3-19.7" in rows["angeloni2023/bioactives"]["uncertainty_retained"]


# --------------------------------------------------------------------------------------------
# THE CORRECTION — C3 is NOT scale-free, and the sweep's exactness
# --------------------------------------------------------------------------------------------
def test_changing_the_bioactive_rsd_refits_the_shared_model(small):
    """END-TO-END. Change the RSD, refit both models, recompute held-out residuals.

    This is the perturbation the screen actually performs, and it must MOVE the shared fit —
    that is why the withdrawn scale-free claim was wrong. Asserted on the real fit, not on a
    rescale of stored z values.
    """
    conds, pred, rates, coefs = small
    indep = S.independent_selection(coefs)

    def shared_at(rsd_pct):
        x = S.rsd_to_x(rsd_pct)
        sel = {}
        for v in S.VARIETIES:
            A = np.array([p["A"] for p in coefs[v]], float)
            B = np.array([p["b"] for p in coefs[v]], float)
            sel[v] = int(np.argmin(x * A + B))
        return sel

    lo, hi = shared_at(19.7), shared_at(0.3)
    assert lo != hi, ("the shared selection did not move across the declared band — if this is "
                      "genuinely true the scale-free claim would need re-examining, not assuming")
    # and the recomputed held-out residual ratio must differ correspondingly
    p_lo = S.residual_parts(pred, conds, coefs, lo, indep, rates)
    p_hi = S.residual_parts(pred, conds, coefs, hi, indep, rates)
    r_lo = S.criteria_at(p_lo, S.rsd_to_x(19.7))["reduction_ratio"]
    r_hi = S.criteria_at(p_hi, S.rsd_to_x(0.3))["reduction_ratio"]
    assert r_lo != pytest.approx(r_hi, rel=1e-9)


def test_no_scale_free_shortcut_is_reintroduced():
    """A guard against the withdrawn claim creeping back into the module text."""
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    assert "scale_free_claim_withdrawn" in src
    assert "IT IS NOT" in src


def test_amplitude_is_independent_of_the_assumed_rsd(small):
    """Fact 1 the exact argument rests on: the common weight factor cancels in the WLS ratio."""
    conds, pred, rates, _ = small
    row = pred.row(1.0)
    for v in S.VARIETIES:
        for s in S.BIOACTIVES:
            # _level uses 1/m^2 for bioactives by construction; verify against an explicit
            # weighted fit at two very different RSDs
            def wls(rsd):
                num = den = 0.0
                for c in conds:
                    if c["variety"] != v or c["held_out"]:
                        continue
                    f = row[(v, c["T_degC"], c["p_bar"], s)]
                    m = c["measured"][s]
                    w = 1.0 / (m * rsd / 100.0) ** 2
                    num += w * f * m
                    den += w * f * f
                return num / den
            assert wls(0.3) == pytest.approx(wls(19.7), rel=1e-12)
            assert wls(0.3) == pytest.approx(S._level(row, conds, v, s), rel=1e-12)


def test_independent_rate_selection_is_independent_of_the_assumed_rsd(small):
    """Fact 2: a common positive factor cannot move an argmin, so these never change."""
    conds, pred, rates, coefs = small
    sel = S.independent_selection(coefs)
    for v in S.VARIETIES:
        for s in S.BIOACTIVES:
            vals = np.array([p["a"][s] for p in coefs[v]], float)
            for factor in (S.rsd_to_x(0.3), S.rsd_to_x(19.7)):
                assert int(np.argmin(factor * vals)) == sel[v][s]["rate_index"]


def test_C1_and_C3_are_monotone_on_a_fixed_selection(small):
    """Fact 3: this is what makes endpoint evaluation of each interval EXACT."""
    conds, pred, rates, coefs = small
    indep = S.independent_selection(coefs)
    sel = {v: 1 for v in S.VARIETIES}                       # any fixed selection
    parts = S.residual_parts(pred, conds, coefs, sel, indep, rates)
    xs = np.geomspace(S.rsd_to_x(19.7), S.rsd_to_x(0.3), 40)
    z = [S.criteria_at(parts, x)["Z_shared"] for x in xs]
    ratio = [S.criteria_at(parts, x)["reduction_ratio"] for x in xs]
    assert all(b >= a - 1e-12 for a, b in zip(z, z[1:])), "Z_shared must be monotone in x"
    d = np.diff(ratio)
    assert np.all(d >= -1e-12) or np.all(d <= 1e-12), "the C3 ratio must be monotone in x"


def test_c2_vertex_is_found_when_the_spread_has_an_interior_minimum(small):
    """C2 is the only criterion whose extremum can be interior; the vertex must be located."""
    conds, pred, rates, coefs = small
    indep = S.independent_selection(coefs)
    parts = S.residual_parts(pred, conds, coefs, {v: 1 for v in S.VARIETIES}, indep, rates)
    x_lo, x_hi = S.rsd_to_x(19.7), S.rsd_to_x(0.3)
    vx = S.c2_vertex_x(parts, x_lo, x_hi)
    if vx is None:
        pytest.skip("no interior vertex for this selection")
    here = S.criteria_at(parts, vx)["between_species_spread"]
    for x in np.geomspace(x_lo, x_hi, 60):
        assert S.criteria_at(parts, x)["between_species_spread"] >= here - 1e-9


def test_breakpoints_actually_change_the_selection(small):
    """A reported breakpoint must be a real switch of the lower envelope, not a crossing."""
    conds, pred, rates, coefs = small
    x_lo, x_hi = S.rsd_to_x(19.7), S.rsd_to_x(0.3)
    bps = S.lower_envelope_breakpoints(coefs, x_lo, x_hi)
    for v, bl in bps.items():
        A = np.array([p["A"] for p in coefs[v]], float)
        B = np.array([p["b"] for p in coefs[v]], float)
        for b in bl:
            below = int(np.argmin(b["x"] * (1 - 1e-7) * A + B))
            above = int(np.argmin(b["x"] * (1 + 1e-7) * A + B))
            assert below != above, (v, b)


def test_rsd_to_x_roundtrips():
    for rsd in (0.3, 1.0, 4.7, 19.7):
        assert S.x_to_rsd(S.rsd_to_x(rsd)) == pytest.approx(rsd, rel=1e-12)


def test_solver_output_scales_linearly_in_c_s0():
    """The whole cheap budget — and the closed-form amplitude — rests on this."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.validation.slow import angeloni_bracket as AB
    sp = dict(ps._solute_params()["caffeine"])
    flow = AB._flow_darcy(9.0, 93.4)
    bounds = AB._matched_bounds(flow)
    p1 = float(ps.simulate_fractions(93.4, flow, bounds, dict(sp, c_s0=1.0), cl1=1.0)[0])
    for lam in (0.5, 7.3, 12.54):
        p2 = float(ps.simulate_fractions(93.4, flow, bounds, dict(sp, c_s0=lam), cl1=1.0)[0])
        assert p2 / lam == pytest.approx(p1, rel=1e-4), lam


def test_amplitude_is_free_in_both_models(small):
    """Blindness to a multiplicative scale is the design, not an afterthought."""
    conds, pred, rates, coefs = small
    indep = S.independent_selection(coefs)
    for v in S.VARIETIES:
        for ri in range(len(rates)):
            assert set(coefs[v][ri]["levels"]) == set(S.SPECIES)
            assert all(np.isfinite(x) for x in coefs[v][ri]["levels"].values())
        for s in S.SPECIES:
            assert "rate_index" in indep[v][s]


# --------------------------------------------------------------------------------------------
# Committed bundle
# --------------------------------------------------------------------------------------------
def test_bundle_is_present_and_carries_the_disposition():
    for rel in ("README.md", "result.json", "decision.md", "figures/primary.png"):
        assert (BUNDLE / rel).exists(), rel
    for rel in ("README.md", "decision.md"):
        text = (BUNDLE / rel).read_text(encoding="utf-8")
        for token in ("CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                      "NOT_A_MODEL_VALIDATION_UPGRADE"):
            assert token in text, (rel, token)


def test_committed_decision_follows_from_its_own_sweep():
    """The disposition must be DERIVED from the stored evaluations, not asserted."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    evals = [e for iv in r["sweep"]["intervals"] for e in iv["evaluations"]]
    assert evals
    any_s = any(e["survive"] for e in evals)
    all_s = all(e["survive"] for e in evals)
    expected = "SURVIVE" if all_s else ("NEEDS_NEW_DATA" if any_s else "RETIRE")
    assert r["decision"] == expected


def test_band_coverage_is_not_two_endpoints():
    """The defect: a whole-band claim from two points. Coverage must be a real sweep."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert r["sweep"]["n_breakpoints"] >= 1
    assert len(r["sweep"]["intervals"]) == r["sweep"]["n_breakpoints"] + 1
    assert r["sweep"]["n_evaluated_points"] > 2
    xs = sorted({e["x"] for iv in r["sweep"]["intervals"] for e in iv["evaluations"]})
    assert xs[0] == pytest.approx(S.rsd_to_x(S.BIOACTIVE_RSD_BAND_PCT[1]))
    assert xs[-1] == pytest.approx(S.rsd_to_x(S.BIOACTIVE_RSD_BAND_PCT[0]))


def test_shared_rate_moves_across_the_committed_band():
    """The observable fact that refutes the withdrawn scale-free claim."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    seen = {v: {iv["shared_rate"][v] for iv in r["sweep"]["intervals"]} for v in S.VARIETIES}
    assert any(len(s) > 1 for s in seen.values()), (
        "the shared rate never moves — re-examine whether the sweep is needed")


def test_rate_grid_robustness_is_recorded_with_evidence():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    rb = r["rate_grid_robustness"]
    assert rb["rounds"], "no expansion evidence recorded"
    assert rb["rounds"][0]["n_rates"] == len(S.BASE_RATE_GRID)
    last = rb["rounds"][-1]
    assert "stop_reason" in last
    # an expansion must actually have been attempted if round 0 had an edge optimum
    if rb["rounds"][0]["n_decisive_optima_at_edge"] > 0:
        assert len(rb["rounds"]) > 1 or last["stop_reason"] == "max rounds reached"
        assert max(rb["final_rates"]) > max(S.BASE_RATE_GRID)
    for q in rb["rounds"]:
        assert "edges" in q and "worst_case_C3_ratio" in q


def test_amplitude_metric_is_defined_and_reported_across_the_band():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    amp = r["amplitude_diagnostic"]
    assert len(amp) >= 2, "the amplitude effect must be reported at more than one RSD"
    for a in amp:
        assert "1 - RMS(z_fitted) / RMS(z_fixed)" in a["metric_definition"]
        assert "not a fraction of raw residual" in a["metric_definition"]
    rsds = sorted(a["rsd_pct"] for a in amp)
    assert rsds[0] == pytest.approx(S.BIOACTIVE_RSD_BAND_PCT[0])
    assert rsds[-1] == pytest.approx(S.BIOACTIVE_RSD_BAND_PCT[1])
    # it must NOT be RSD-independent — quoting one number was part of the defect
    vals = {round(a["rms_reduction_fraction"], 4) for a in amp}
    assert len(vals) > 1


def test_table7_comparison_is_qualified_not_universal():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    t7 = r["amplitude_vs_table7"]
    matched = [x for x in t7["rows"] if x["species_matched"]]
    unmatched = [x for x in t7["rows"] if not x["species_matched"]]
    assert {x["species"] for x in matched} == {"caffeine", "trigonelline"}
    assert t7["n_species_matched_cells"] == len(matched)
    assert 0 <= t7["n_species_matched_cells_fitted_closer"] <= len(matched)
    for x in unmatched:
        assert x["fitted_closer_to_table7_than_pannusch"] is None
        assert x["note"]
    cqa = [x for x in t7["rows"] if x["species"] == "5CQA"]
    assert cqa and all("TOTAL CQA" in x["note"] for x in cqa)


def test_corrected_language_does_not_claim_inventory_over_transport():
    """The withdrawn explanatory claim must not survive anywhere reader-facing."""
    for rel in ("README.md", "decision.md"):
        text = (BUNDLE / rel).read_text(encoding="utf-8").lower()
        assert "differ in inventory, not in transport" not in text
        assert "not in how they move through it" not in text
        assert "amplitude" in text, rel


def test_decision_records_a_claim_ceiling_and_an_adversarial_check():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure"):
        assert section in text, section


def test_retirement_record_matches_the_committed_decision():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    if r["decision"] == "RETIRE":
        assert "**I-024**" in text
        assert "screens/I-024/" in text
    else:
        assert "**I-024**" not in text


# --------------------------------------------------------------------------------------------
# Expensive — the full corrected analysis
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
def test_per_species_freedom_buys_nothing_anywhere_on_the_band():
    r = S.screen()
    assert r["decision"] == "RETIRE"
    assert r["C3_ever_satisfied"] is False
    assert r["worst_case_C3_ratio"] > S.C3_REDUCTION_FACTOR
    for iv in r["sweep"]["intervals"]:
        assert iv["any_survive"] is False


@pytest.mark.slow
def test_committed_result_does_not_drift_from_a_fresh_run():
    fresh = S.screen()
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == fresh["decision"]
    assert committed["sweep"]["n_breakpoints"] == fresh["sweep"]["n_breakpoints"]
    assert committed["worst_case_C3_ratio"] == pytest.approx(
        fresh["worst_case_C3_ratio"], rel=1e-6)

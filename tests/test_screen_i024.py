"""Focused tests for the I-024 cheap screen (Insight Foundry Wave 1).

These guard the screen's DESIGN, which is where its verdict actually comes from:

  * the evidence unit really is angeloni-only (the excluded campaigns must stay excluded);
  * the c_s0 linearity the whole cheap budget rests on still holds;
  * a per-species inventory level is free in BOTH models, so the comparison stays blind to
    inventory and assay scaling;
  * C3 is scale-free, which is what lets the screen decide despite the missing solute-specific
    replicate RSD;
  * the held-out split is the predeclared one and is never silently widened.

If any of those stop being true, the RETIRE is no longer earned, whatever the numbers say.
"""
import json
import pathlib

import numpy as np
import pytest

from puckworks.analysis import screen_i024_common_state as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-024"


# --------------------------------------------------------------------------------------------
# Design — cheap, always run
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
    """The excluded campaigns must be declared, with a reason, and never scored."""
    for key in ("maille", "ellero", "khamitova"):
        assert any(key in k.lower() for k in S.EXCLUDED_EVIDENCE), key
    assert all(v for v in S.EXCLUDED_EVIDENCE.values()), "every exclusion needs a reason"
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    for banned in ("maille_", "ellero_", "khamitova_", "schmieder_"):
        assert banned not in src, "a non-angeloni loader is being called: %s" % banned


def test_solver_is_linear_in_c_s0():
    """The closed-form level fit — and the whole cheap budget — depends on this."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.validation.slow import angeloni_bracket as AB
    sp = dict(ps._solute_params()["caffeine"])
    flow = AB._flow_darcy(9.0, 93.4)
    bounds = AB._matched_bounds(flow)
    unit = dict(sp, c_s0=1.0)
    p1 = float(ps.simulate_fractions(93.4, flow, bounds, unit, cl1=1.0)[0])
    for lam in (0.5, 7.3, 12.54):
        p2 = float(ps.simulate_fractions(93.4, flow, bounds, dict(sp, c_s0=lam), cl1=1.0)[0])
        assert p2 / lam == pytest.approx(p1, rel=1e-4), lam


def test_a_level_is_free_in_both_models():
    """Blindness to inventory / assay scaling is the design, not an afterthought."""
    conds = S.conditions()
    F = {0: {(c["variety"], c["T_degC"], c["p_bar"], s): 1.0 + 0.1 * i
             for i, c in enumerate(conds) for s in S.SPECIES}}
    shared, indep = S.fit(F, conds, 5.0, rate_grid=np.array([1.0]))
    for v in S.VARIETIES:
        assert set(shared[v]["levels"]) == set(S.SPECIES)          # shared: per-species level
        for s in S.SPECIES:
            assert "level" in indep[v][s]                          # independent: same
            assert np.isfinite(indep[v][s]["level"])


def test_C3_is_scale_free_in_the_assumed_rsd():
    """The arm that lets the screen decide despite the missing solute-specific RSD.

    C3 compares two RMS standardised residuals computed under the SAME sigma, so a common
    rescale of sigma cancels. Asserted directly rather than trusted.
    """
    rows = [dict(z_shared=2.0, z_independent=1.0, species="caffeine"),
            dict(z_shared=4.0, z_independent=2.0, species="tds"),
            dict(z_shared=1.0, z_independent=0.5, species="5CQA"),
            dict(z_shared=3.0, z_independent=1.5, species="trigonelline")]
    scaled = [dict(r, z_shared=r["z_shared"] * 7.0, z_independent=r["z_independent"] * 7.0)
              for r in rows]
    a, b = S.evaluate(rows), S.evaluate(scaled)
    assert a["reduction_ratio"] == pytest.approx(b["reduction_ratio"])
    assert a["C3_reduced_by_species_fits"] == b["C3_reduced_by_species_fits"]


def test_criterion_thresholds_are_the_predeclared_ones():
    assert (S.C1_Z_THRESHOLD, S.C2_SPREAD_THRESHOLD, S.C3_REDUCTION_FACTOR) == (1.0, 1.0, 0.7)
    assert "Predeclared before any fit was computed" in S.CRITERION_STATEMENT


def test_uncertainty_band_is_the_source_stated_one():
    """The band must come from the MANIFEST cell, not from a convenient guess."""
    import csv
    assert S.BIOACTIVE_RSD_BAND_PCT == (0.3, 19.7)
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    assert "0.3-19.7" in rows["angeloni2023/bioactives"]["uncertainty_retained"]


def test_tds_uses_measured_per_condition_rsd():
    conds = S.conditions()
    sig = S.sigma_of(conds[0], "tds", bioactive_rsd_pct=5.0)
    expected = abs(conds[0]["measured"]["tds"]) * conds[0]["tds_rsd_pct"] / 100.0
    assert sig == pytest.approx(expected)
    # a bioactive must NOT use the tds column
    sig_b = S.sigma_of(conds[0], "caffeine", bioactive_rsd_pct=5.0)
    assert sig_b == pytest.approx(abs(conds[0]["measured"]["caffeine"]) * 0.05)


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


def test_committed_result_is_internally_consistent():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert r["decision"] == "RETIRE"
    assert r["decision_invariant_across_band"] is True
    assert r["evidence_unit"]["n_train"] == 12 and r["evidence_unit"]["n_held_out"] == 6
    assert r["uncertainty"]["solute_specific_rsd_recovered"] is False
    # C3 must fail at BOTH ends — that is what makes the verdict scale-free
    assert r["C3_by_band"] == {"low": False, "high": False}
    for tag in ("low", "high"):
        assert r["band"][tag]["evaluation"]["survive"] is False
    # the inventory/assay alternative must have been quantified, not asserted
    la = r["band"]["low"]["level_absorption"]
    assert la["absorbed_fraction"] > 0.5
    assert la["Z_level_fixed_at_pannusch_table2"] > la["Z_level_fitted"]


def test_flat_valley_diagnostics_are_surfaced():
    """A boundary optimum must be visible in the record, never silently accepted."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    edges = [d["rate_at_grid_edge"]
             for tag in ("low", "high") for v in S.VARIETIES
             for d in r["band"][tag]["independent"][v].values()]
    assert any(edges), "the record should surface at least one right-censored rate optimum"


def test_decision_records_a_claim_ceiling_and_an_adversarial_check():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure"):
        assert section in text, section


def test_retirement_is_recorded_with_a_reopen_condition():
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    assert "**I-024**" in text
    assert "screens/I-024/" in text


# --------------------------------------------------------------------------------------------
# Expensive — the numbers themselves
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
def test_per_species_fits_buy_nothing_held_out():
    r = S.screen()
    assert r["decision"] == "RETIRE"
    assert r["decision_invariant_across_band"] is True
    for tag in ("low", "high"):
        e = r["band"][tag]["evaluation"]
        assert e["C3_reduced_by_species_fits"] is False
        assert e["reduction_ratio"] > S.C3_REDUCTION_FACTOR


@pytest.mark.slow
def test_committed_result_does_not_drift_from_a_fresh_run():
    fresh = S.screen()
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == fresh["decision"]
    for tag in ("low", "high"):
        f = fresh["band"][tag]["evaluation"]
        c = committed["band"][tag]["evaluation"]
        assert f["Z_shared"] == pytest.approx(c["Z_shared"], rel=1e-6)
        assert f["Z_independent"] == pytest.approx(c["Z_independent"], rel=1e-6)

"""Focused tests for the I-010 cheap screen (Insight Foundry Wave 1).

These guard the SCREEN'S DISCIPLINE, not its numbers: that the producer->consumer path claim
stays true against the actual source, that the materiality criterion stays derived from retained
uncertainty rather than drifting to a round number, that the flow map really is frozen at the
baseline viscosity, and that an inadmissible substitution cannot leak into the decision.

The expensive sweeps are marked slow. The cheap structural checks run in the quick lane, which is
where a silent regression would otherwise hide.
"""
import json
import pathlib

import pytest

from puckworks.analysis import screen_i010_closure_portability as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-010"


# --------------------------------------------------------------------------------------------
# Structural — cheap, always run
# --------------------------------------------------------------------------------------------
def test_the_import_path_claim_is_true_in_source():
    """The screen's whole step 1 rests on this line existing. If it moves, the claim is stale."""
    src = (REPO / "puckworks/models/pannusch2024/solver.py").read_text(encoding="utf-8")
    assert "from puckworks.models.pannusch2024 import closures as pc" in src
    assert "pc.sherwood_h(" in src
    assert "pc.vant_hoff_K(" in src


def test_transitive_closures_reach_the_consumer_only_via_sherwood():
    """diffusion_coeff / water_viscosity / water_density must NOT be called by the solver."""
    src = (REPO / "puckworks/models/pannusch2024/solver.py").read_text(encoding="utf-8")
    for name in ("diffusion_coeff", "water_viscosity", "water_density"):
        assert "pc.%s(" % name not in src, name
    closures = (REPO / "puckworks/models/pannusch2024/closures.py").read_text(encoding="utf-8")
    assert "diffusion_coeff(T_K, solute)" in closures       # called inside sherwood_h


def test_declared_valid_range_matches_the_registry_verbatim():
    from puckworks.registry import components
    entry = {c.name: c for c in components()}["pannusch2024.closures"]
    assert entry.valid_range == S.DECLARED_VALID_RANGE


def test_materiality_is_derived_from_retained_uncertainty():
    """U must be sqrt(obs^2 + num^2) — not a round percentage someone typed in."""
    import numpy as np
    assert S.MATERIALITY_U_PCT == pytest.approx(
        float(np.hypot(S.OBS_RSD_PCT, S.NUM_REL_PCT)), rel=1e-12)
    assert "Predeclared before any substitution was computed" in S.MATERIALITY_STATEMENT


def test_observational_uncertainty_matches_the_campaign():
    """obs is the median measured per-condition TS RSD; it may not drift from the data."""
    import statistics

    from puckworks import data as d
    rsd = [r["RSD_pct"] for r in d.angeloni_total_solids() if r["RSD_pct"] is not None]
    assert S.OBS_RSD_PCT == pytest.approx(statistics.median(rsd), abs=0.005)


def test_held_out_unit_is_the_independent_campaign():
    shots = S._held_out_shots()
    assert len(shots) == 18
    assert {r["granulometry"] for r in shots} == {"O"}
    assert {r["on_grid"] for r in shots} == {"True"}
    assert {r["variety"] for r in shots} == {"Arabica", "Robusta"}


def test_inadmissible_substitutions_are_declared_and_reasoned():
    subs = {s["closure"]: s for s in S.substitutions()}
    assert subs["water_viscosity"]["admissible"] is False
    assert "outside ITS OWN range" in subs["water_viscosity"]["admissibility_note"]
    assert subs["sherwood_h"]["admissible"] is False
    assert subs["sherwood_h"]["patch"] is None
    # the three that count must be admissible
    for name in ("vant_hoff_K", "diffusion_coeff", "water_density"):
        assert subs[name]["admissible"] is True, name


def test_the_two_K_closures_still_disagree_on_the_sign_of_dK_dT():
    """The K(T) swap is only a meaningful test while this disagreement is live (G4 record)."""
    from puckworks.models.pannusch2024 import closures as pc
    from puckworks.models.romancorrochano2017 import extraction as rx
    from puckworks import data as d
    t2 = {r["solute"]: r for r in d.pannusch_table2()}
    p = t2["caffeine"]
    pann = (float(pc.vant_hoff_K(371.15, p["K_ref"], p["gamma"]))
            - float(pc.vant_hoff_K(361.15, p["K_ref"], p["gamma"])))
    roman = rx.K_of_T(98.0) - rx.K_of_T(88.0)
    assert pann < 0 < roman, "the sign disagreement this swap probes has gone away"


def test_flow_map_is_frozen_at_the_baseline_viscosity():
    """A viscosity swap must NOT move the boundary condition — the predeclared freeze."""
    from puckworks.validation.slow import angeloni_bracket as AB
    shots = S._held_out_shots()[:1]
    baseline_flow = float(AB._flow_darcy(shots[0]["p_bar"], shots[0]["T_degC"]))
    subs = {s["closure"]: s for s in S.substitutions()}
    captured = []
    real = AB._matched_bounds

    def spy(flow_source, *a, **k):
        captured.append(float(flow_source))
        return real(flow_source, *a, **k)

    AB._matched_bounds = spy
    try:
        S._predict(shots, subs["water_viscosity"]["patch"])
    finally:
        AB._matched_bounds = real
    assert captured, "the observation operator was never called"
    assert all(f == pytest.approx(baseline_flow) for f in captured)


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
    assert r["path"]["established"] is True
    assert r["held_out_unit"]["n_points"] == 72
    assert r["validity_range"]["consumed_outside_declared_range"] is False
    assert r["recalibration"] is None, "branch must not run without a material no-refit effect"
    assert r["uncertainty"]["combined_U_pct"] == pytest.approx(S.MATERIALITY_U_PCT)
    ran = [s for s in r["substitutions"] if s["ran"]]
    counted = [s for s in ran if s["counts_toward_decision"]]
    assert len(counted) == 3
    assert all(not s["material"] for s in counted)
    # the excluded viscosity bound IS material — that is the point of reporting it
    mu = [s for s in ran if s["closure"] == "water_viscosity"][0]
    assert mu["material"] is True and mu["counts_toward_decision"] is False


def test_decision_records_a_claim_ceiling_and_an_adversarial_check():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure"):
        assert section in text, section


def test_retirement_is_recorded_with_a_reopen_condition():
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    assert "**I-010**" in text
    assert "screens/I-010/" in text


# --------------------------------------------------------------------------------------------
# Expensive — the numbers themselves
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
def test_no_admissible_swap_is_material():
    r = S.screen()
    assert r["decision"] == "RETIRE"
    counted = [s for s in r["substitutions"]
               if s.get("ran") and s.get("counts_toward_decision")]
    assert len(counted) == 3
    for s in counted:
        assert s["median_rel_change_pct"] < S.MATERIALITY_U_PCT, s["closure"]


@pytest.mark.slow
def test_committed_result_does_not_drift_from_a_fresh_run():
    fresh = S.screen()
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == fresh["decision"]
    fm = {s["closure"]: s.get("median_rel_change_pct") for s in fresh["substitutions"]}
    cm = {s["closure"]: s.get("median_rel_change_pct") for s in committed["substitutions"]}
    assert fm.keys() == cm.keys()
    for k in fm:
        if fm[k] is None:
            assert cm[k] is None
        else:
            assert fm[k] == pytest.approx(cm[k], rel=1e-6)

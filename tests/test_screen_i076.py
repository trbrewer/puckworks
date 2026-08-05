"""Focused tests for the I-076 cheap screen (Insight Foundry Wave 2).

These establish the properties the verdict rests on, not the verdict:

  * NO MODEL IS EXECUTED — asserted by instrumenting both solvers and running the whole screen;
  * the protocol commit PRECEDES every result-producing commit, checked against git history;
  * both blockers are real, checked against the live signatures and card text rather than
    against prose in the module;
  * the scenario was chosen by the SOURCE's own DoE role, not by a range midpoint;
  * uncertainty authorities stay unpooled and are never borrowed across components;
  * `cameron2020.paper_mode` is never imported or invoked.
"""
import json
import pathlib
import subprocess

import pytest

from puckworks.analysis import screen_i076_matched_models as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-076"


@pytest.fixture(scope="module")
def result():
    return S.screen()


# --------------------------------------------------------------------------------------------
# THE PROTOCOL-FIRST REQUIREMENT
# --------------------------------------------------------------------------------------------
def test_protocol_document_exists_and_freezes_all_sixteen_items():
    p = BUNDLE / "PROTOCOL.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for n in range(1, 17):
        assert ("\n## %d." % n) in text, "protocol item %d is missing" % n


def test_protocol_commit_precedes_every_result_producing_commit():
    """Git history must show the protocol landing first. This is the whole point of item 0."""
    def commits_touching(path):
        out = subprocess.run(["git", "log", "--format=%H", "--", path],
                             cwd=REPO, capture_output=True, text=True).stdout.split()
        return out                       # newest first
    proto = commits_touching("docs/insights/screens/I-076/PROTOCOL.md")
    if not proto:
        pytest.skip("protocol not yet committed (working-tree run)")
    results = []
    for rel in ("docs/insights/screens/I-076/result.json",
                "puckworks/analysis/screen_i076_matched_models.py",
                "docs/insights/screens/I-076/decision.md"):
        results += commits_touching(rel)
    if not results:
        pytest.skip("no result-producing commit yet")
    order = subprocess.run(["git", "log", "--format=%H"], cwd=REPO,
                           capture_output=True, text=True).stdout.split()
    pos = {h: i for i, h in enumerate(order)}          # 0 = newest
    first_protocol = max(pos[h] for h in proto if h in pos)          # oldest protocol commit
    first_result = max(pos[h] for h in results if h in pos)          # oldest result commit
    assert first_protocol > first_result, (
        "the protocol commit must be OLDER than the first result-producing commit")


def test_screen_declares_the_protocol_and_that_it_was_frozen_first(result):
    assert result["protocol"]["path"] == "docs/insights/screens/I-076/PROTOCOL.md"
    assert result["protocol"]["frozen_before_execution"] is True


# --------------------------------------------------------------------------------------------
# NO MODEL EXECUTION
# --------------------------------------------------------------------------------------------
def test_no_model_is_executed_anywhere_in_the_screen():
    """Instrument both solvers and run the entire screen. Neither may be called."""
    from puckworks.models.cameron2020 import extraction_bdf as C
    from puckworks.models.pannusch2024 import solver as P
    calls = []
    real_c, real_p, real_pq = C.simulate_shot, P.simulate_fractions, P.simulate_fractions_qt

    def spy(name, fn):
        def _w(*a, **k):
            calls.append(name)
            return fn(*a, **k)
        return _w

    C.simulate_shot = spy("cameron.simulate_shot", real_c)
    P.simulate_fractions = spy("pannusch.simulate_fractions", real_p)
    P.simulate_fractions_qt = spy("pannusch.simulate_fractions_qt", real_pq)
    try:
        r = S.screen()
        S.figure(path=REPO / "docs/insights/screens/I-076/figures/_test_tmp.png", result=r)
    finally:
        C.simulate_shot, P.simulate_fractions, P.simulate_fractions_qt = real_c, real_p, real_pq
        tmp = REPO / "docs/insights/screens/I-076/figures/_test_tmp.png"
        if tmp.exists():
            tmp.unlink()
    assert calls == [], "a model was executed: %s" % calls
    assert r["models_executed"] is False


def test_quarantined_component_is_never_invoked():
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    assert "paper_mode" in src, "the quarantine must be declared"
    # declared only as a string, never imported or called
    assert "import paper_mode" not in src
    assert "paper_mode." not in src.replace('QUARANTINED = "cameron2020.paper_mode"', "")
    assert S.QUARANTINED == "cameron2020.paper_mode"


# --------------------------------------------------------------------------------------------
# BLOCKER A — grind, checked against the cards
# --------------------------------------------------------------------------------------------
def test_the_two_components_name_different_grinders_in_their_cards():
    schmieder = (REPO / "docs/cards/schmieder2023.md").read_text(encoding="utf-8")
    cameron = (REPO / "docs/cards/cameron2020.md").read_text(encoding="utf-8")
    assert "E65S" in schmieder, "pannusch's campaign card must name its grinder"
    assert "EK43" in cameron, "cameron's card must name its dial"
    assert "EK43" not in schmieder.split("## Assumptions")[1][:600], (
        "the campaign card must not also claim an EK43 in its apparatus paragraph")


def test_grind_blocker_is_derived_not_asserted(result):
    g = result["blockers"]["grind"]
    assert g["e65s_named_in_campaign_card"] is True
    assert g["ek43_named_in_cameron_card"] is True
    assert g["same_dial_space"] is False
    assert g["declared_adapter_exists"] is False
    assert g["blocks"] is True


def test_the_existing_uncalibrated_maps_contradict_each_other(result):
    """Evidence that the forbidden mapping is not merely unproven but inconsistent in-repo."""
    g = result["blockers"]["grind"]
    assert g["existing_maps_contradict_each_other"] is True
    assigns = g["granulometry_O_assignments"]
    assert len({v for v in assigns.values() if v is not None}) > 1, assigns
    src = (REPO / "puckworks/validation/slow/angeloni_bracket.py").read_text(encoding="utf-8")
    assert "UNCALIBRATED" in src, "the in-repo map must still declare itself uncalibrated"


def test_grind_is_load_bearing_for_cameron_beyond_the_flux():
    """Supplying q does not remove the grind dependence — microstructure still needs gs."""
    import inspect
    from puckworks.models.cameron2020 import extraction_bdf as C
    body = inspect.getsource(C.simulate_shot)
    assert "grind_microstructure(gs)" in body
    i_q = body.index("if q is None")
    i_micro = body.index("grind_microstructure(gs)")
    assert i_micro > i_q, "microstructure must be computed regardless of an explicit q"


# --------------------------------------------------------------------------------------------
# BLOCKER B — temperature, checked against the live signatures
# --------------------------------------------------------------------------------------------
def test_cameron_has_no_temperature_parameter():
    import inspect
    from puckworks.models.cameron2020 import extraction_bdf as C
    params = list(inspect.signature(C.simulate_shot).parameters)
    assert not any("temp" in p.lower() or p == "T_C" for p in params), params


def test_pannusch_requires_a_temperature():
    import inspect
    from puckworks.models.pannusch2024 import solver as P
    params = list(inspect.signature(P.simulate_fractions).parameters)
    assert "T_C" in params


def test_temperature_blocker_is_derived(result):
    t = result["blockers"]["temperature"]
    assert t["component_a_accepts_temperature"] is True
    assert t["component_b_accepts_temperature"] is False
    assert t["component_b_is_isothermal"] is True
    assert t["blocks"] is True


# --------------------------------------------------------------------------------------------
# Scenario provenance
# --------------------------------------------------------------------------------------------
def test_scenario_is_the_sources_own_centre_point_not_a_chosen_midpoint(result):
    scn = result["scenario"]
    assert scn["doe_role"] == "DoE Central Point"
    assert "midpoint" in scn["selection_reason"].lower()
    assert scn["n_replicates"] >= 3, "a measured uncertainty needs replicates"


def test_scenario_values_come_from_the_source(result):
    from puckworks import data as d
    reps = [x for x in d.schmieder_cup_masses()
            if x["component"] == "TDS" and x["brew_ratio"] == "1/2" and x["exp"] == 7.0]
    scn = result["scenario"]
    assert len(reps) == scn["n_replicates"]
    assert scn["measured_flow_mL_s"]["mean"] == pytest.approx(
        sum(x["scale_flow_ml_s"] for x in reps) / len(reps), abs=1e-4)
    assert scn["dose_g"] == 20.00
    assert scn["beverage_g"] == 40.0


def test_dose_provenance_is_the_card_not_an_inference(result):
    card = (REPO / "docs/cards/schmieder2023.md").read_text(encoding="utf-8")
    assert "20.00" in card, "the dose must be stated in the card, not inferred from the ratio"
    assert "schmieder2023.md" in result["scenario"]["dose_provenance"]


# --------------------------------------------------------------------------------------------
# Uncertainty discipline
# --------------------------------------------------------------------------------------------
def test_uncertainty_authorities_are_separate_and_unpooled(result):
    u = result["uncertainty_authorities"]
    for k in ("measured_replicate", "fitted_source_residual", "numerical_convergence",
              "parameter", "model_form"):
        assert k in u, k
    assert "NOT pooled" in u["pooling_policy"]
    assert "MAY NOT be used as cameron" in u["fitted_source_residual"]["prohibition"]
    assert "MAY NOT be treated as experimental" in u["numerical_convergence"]["prohibition"]


def test_measured_replicate_rsd_comes_from_the_manifest(result):
    import csv
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    caveat = rows["schmieder2023/cup_masses"]["caveat"]
    u = result["uncertainty_authorities"]["measured_replicate"]
    assert str(u["campaign_mean_rsd_pct"]) in caveat
    assert caveat in u["source"]


# --------------------------------------------------------------------------------------------
# Comparability and decision
# --------------------------------------------------------------------------------------------
def test_comparability_uses_the_five_levels_without_building_machinery(result):
    c = result["comparability"]
    assert c["primary"]["level"] in S.COMPARABILITY_LEVELS
    assert set(S.COMPARABILITY_LEVELS) == {1, 2, 3, 4, 5}
    assert "No comparability schema" in c["note"]
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    for banned in ("class ComparabilitySchema", "AdapterRegistry", "response_atlas", "sweep("):
        assert banned not in src, banned


def test_decision_follows_from_the_blockers(result):
    blocking = [b for b in (result["blockers"]["grind"], result["blockers"]["temperature"])
                if b["blocks"]]
    expected = "NEEDS_NEW_DATA" if blocking else "PENDING_EXECUTION"
    assert result["decision"] == expected
    assert result["blockers"]["n_blocking"] == len(blocking)


def test_missing_evidence_is_named_and_neither_item_is_sufficient_alone(result):
    ue = result["unblocking_evidence"]
    assert len(ue) == 2
    for u in ue:
        assert u["precisely"] and u["resolves"]
        assert u["sufficient_alone"] is False


# --------------------------------------------------------------------------------------------
# Committed bundle
# --------------------------------------------------------------------------------------------
def test_bundle_is_present_and_carries_the_disposition():
    for rel in ("README.md", "result.json", "decision.md", "figures/primary.png",
                "PROTOCOL.md"):
        assert (BUNDLE / rel).exists(), rel
    for rel in ("README.md", "decision.md", "PROTOCOL.md"):
        text = (BUNDLE / rel).read_text(encoding="utf-8")
        for token in ("CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                      "NOT_A_MODEL_VALIDATION_UPGRADE"):
            assert token in text, (rel, token)


def test_committed_result_does_not_drift_from_a_fresh_run(result):
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == result["decision"]
    assert committed["models_executed"] is False
    assert (committed["comparability"]["primary"]["level"]
            == result["comparability"]["primary"]["level"])
    assert (committed["scenario"]["measured_tds_mass_fraction"]["mean_pct"]
            == pytest.approx(result["scenario"]["measured_tds_mass_fraction"]["mean_pct"]))


def test_decision_records_a_claim_ceiling_and_names_the_missing_evidence():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure",
                    "## Named missing evidence"):
        assert section in text, section


def test_needs_new_data_is_not_recorded_as_a_retirement():
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    if committed["decision"] == "RETIRE":
        assert "**I-076**" in text
    else:
        assert "**I-076**" not in text, (
            "I-076 is in RETIRED_CANDIDATES.md but its screen did not return RETIRE")

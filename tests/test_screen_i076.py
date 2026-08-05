"""Focused tests for the I-076 cheap screen (Insight Foundry Wave 2).

These establish the properties the verdict rests on, not the verdict:

  * NO MODEL IS EXECUTED — asserted by instrumenting both solvers and running the whole screen;
  * the protocol commit PRECEDES every result-producing commit, checked against git history;
  * the ONE decisive cross-grinder blocker is real, checked against the live signatures, card
    text and manifest rather than against prose in the module — while the absence of an exposed
    temperature argument is NOT independently blocking, because cameron carries a fixed ~90 C
    water-property basis inside pannusch's declared window;
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


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _history_is_truncated():
    """CI checks out at depth 1, so per-path `git log` cannot show commit ORDER.

    A shallow (or single-commit) checkout is an environment limit, not a protocol violation —
    the ordering assertion is meaningful only where the history is actually present.
    """
    if _git("rev-parse", "--is-shallow-repository").stdout.strip() == "true":
        return True
    return len(_git("log", "--format=%H").stdout.split()) < 2


def _has_matplotlib():
    try:
        import matplotlib                                    # noqa: F401
    except ImportError:
        return False
    return True


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
    if _history_is_truncated():
        pytest.skip("shallow/truncated checkout: per-path commit order is not observable here")

    def commits_touching(path):
        return _git("log", "--format=%H", "--", path).stdout.split()   # newest first
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
    order = _git("log", "--format=%H").stdout.split()
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
        if _has_matplotlib():
            # the figure is rendered from `r` and must not reach a solver either; matplotlib is
            # absent in the min-deps lane, where screen() alone still proves the property
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


def test_grind_mapping_is_absent_and_remains_decisive(result):
    g = result["blockers"]["grind"]
    assert g["e65s_named_in_campaign_card"] is True
    assert g["ek43_named_in_cameron_card"] is True
    assert g["same_dial_space"] is False
    assert g["declared_adapter_exists"] is False
    assert g["blocks"] is True
    # decisive: it alone produces the disposition
    assert result["decisive_blocker_count"] == 1
    assert result["decision"] == "NEEDS_NEW_DATA"
    # and no source in the repository supplies the mapping
    import csv
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    e65s_psd = [r for r in rows if "E65S" in (r["source_artifact"] + r["caveat"])
                and "psd" in r["dataset_id"].lower()]
    assert not e65s_psd, "an E65S PSD now exists — the decisive blocker may be resolvable"


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
# TEMPERATURE — a NON-BLOCKING caveat, not an independent blocker
# --------------------------------------------------------------------------------------------
def test_absence_of_a_temperature_argument_does_not_set_a_blocker(result):
    """The correction: a missing ARGUMENT is not evidence of a different intervention."""
    t = result["temperature"]
    assert t["parameterized"] is False, "cameron still exposes no temperature argument"
    assert t["independently_blocking"] is False, (
        "a fixed or implicit temperature basis is not automatically a different intervention")
    assert t["basis"] == "fixed_or_implicit"
    assert result["decisive_blocker_count"] == 1
    assert result["decisive_blocker"] == "cross_grinder_microstructure_mapping"


def test_cameron_carries_a_fixed_water_property_basis_near_90C(result):
    """Provenance for treating temperature as fixed rather than absent."""
    src = (REPO / "puckworks/models/cameron2020/extraction_bdf.py").read_text(encoding="utf-8")
    assert "viscosity of water at ~90 C" in src
    ev = result["temperature"]["detail"]["fixed_basis_evidence"]
    assert ev["constant"] == "MU"
    assert ev["documented_temperature_C"] == pytest.approx(90.0)
    assert ev["value"] == pytest.approx(3.15e-4)
    # and it sits inside pannusch's declared window
    rng = result["temperature"]["detail"]["component_a_declared_range"]
    assert "80-98" in rng.replace("–", "-")


def test_temperature_remains_a_recorded_non_blocking_caveat(result):
    caveats = result["non_blocking_caveats"]
    assert any("temperature" in c["caveat"].lower() for c in caveats)
    for c in caveats:
        assert c["why_not_blocking"]
    t = result["temperature"]["detail"]
    assert t["residual_caveat"]
    assert "NON-BLOCKING" in t["residual_caveat"]
    assert "withdrawn" in t["superseded_note"]


def test_pannusch_still_requires_a_temperature():
    import inspect
    from puckworks.models.pannusch2024 import solver as P
    assert "T_C" in list(inspect.signature(P.simulate_fractions).parameters)


# --------------------------------------------------------------------------------------------
# The pannusch metadata conflict — internal, not card-versus-registry
# --------------------------------------------------------------------------------------------
def test_pannusch_metadata_conflict_is_internal_and_unresolved(result):
    """Both statements live in the component's OWN card; the screen records, never resolves."""
    conf = result["blockers"]["grind"]["evidence"][S.COMPONENT_A]["metadata_conflict"]
    assert "INTERNAL" in conf["kind"]
    assert "NOT a card-versus-registry" in conf["kind"]
    assert conf["corrected_in_this_pr"] is False
    card = (REPO / "docs/cards/pannusch2024.md").read_text(encoding="utf-8")
    assert "Schmieder-2023 apparatus" in card, "the lineage statement must be in the card"
    assert "EK43-type grind" in card, "the validity statement must be in the SAME card"


def test_neither_registry_nor_source_card_was_modified():
    base = "14c3753c6e8dab2995332dbe1c3d1e04c4348051"
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("branch base %s not present in this checkout" % base[:7])
    for path in ("puckworks/models/__init__.py", "docs/cards/pannusch2024.md",
                 "docs/cards/cameron2020.md", "docs/cards/schmieder2023.md"):
        r = _git("diff", "--numstat", base, "HEAD", "--", path)
        assert r.returncode == 0, r.stderr
        assert r.stdout.strip() == "", "%s was modified: %s" % (path, r.stdout.strip())


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
    assert "Temperature is NOT" in c["primary"]["rationale"]
    assert set(S.COMPARABILITY_LEVELS) == {1, 2, 3, 4, 5}
    assert "No comparability schema" in c["note"]
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    for banned in ("class ComparabilitySchema", "AdapterRegistry", "response_atlas", "sweep("):
        assert banned not in src, banned


def test_decision_follows_from_the_grind_blocker_alone(result):
    blocking = [result["blockers"]["grind"]] if result["blockers"]["grind"]["blocks"] else []
    expected = "NEEDS_NEW_DATA" if blocking else "PENDING_EXECUTION"
    assert result["decision"] == expected
    assert result["blockers"]["n_blocking"] == len(blocking) == result["decisive_blocker_count"]
    assert result["temperature"]["independently_blocking"] is False


def test_exactly_one_item_appears_in_the_decisive_missing_evidence_list(result):
    ue = result["unblocking_evidence"]
    assert len(ue) == 1, "the missing-evidence list must name ONE item, not two"
    u = ue[0]
    assert u["precisely"] and u["resolves"]
    assert u["sufficient_alone"] is True
    assert "grind" in u["need"].lower()
    assert "temperature" not in u["need"].lower(), (
        "temperature must not appear as jointly-required missing evidence")


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

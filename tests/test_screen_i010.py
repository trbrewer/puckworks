"""Focused tests for the I-010 cheap screen (Insight Foundry Wave 1).

These guard the SCREEN'S SCIENTIFIC DISCIPLINE, not its numbers or its disposition. In
particular they encode the defect the 2026-08-04 correction fixed: the screen must never judge
an output against an uncertainty that is not that output's own.

Every test here is a property that would still have to hold if the numbers moved. Nothing asserts
"the decision is NEEDS_NEW_DATA" for its own sake — the one test that touches the disposition
derives it from the classification inputs, so it fails if the numbers change AND the rule stops
matching them.
"""
import json
import pathlib
import statistics

import pytest

from puckworks.analysis import screen_i010_closure_portability as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-010"


# --------------------------------------------------------------------------------------------
# Structural — the path claim
# --------------------------------------------------------------------------------------------
def test_the_import_path_claim_is_true_in_source():
    """The screen's whole step 1 rests on this line existing. If it moves, the claim is stale."""
    src = (REPO / "puckworks/models/pannusch2024/solver.py").read_text(encoding="utf-8")
    assert "from puckworks.models.pannusch2024 import closures as pc" in src
    assert "pc.sherwood_h(" in src
    assert "pc.vant_hoff_K(" in src


def test_transitive_closures_reach_the_consumer_only_via_sherwood():
    src = (REPO / "puckworks/models/pannusch2024/solver.py").read_text(encoding="utf-8")
    for name in ("diffusion_coeff", "water_viscosity", "water_density"):
        assert "pc.%s(" % name not in src, name
    closures = (REPO / "puckworks/models/pannusch2024/closures.py").read_text(encoding="utf-8")
    assert "diffusion_coeff(T_K, solute)" in closures       # called inside sherwood_h


def test_declared_valid_range_matches_the_registry_verbatim():
    from puckworks.registry import components
    entry = {c.name: c for c in components()}["pannusch2024.closures"]
    assert entry.valid_range == S.DECLARED_VALID_RANGE


# --------------------------------------------------------------------------------------------
# THE CORRECTION — uncertainty authority
# --------------------------------------------------------------------------------------------
def test_every_output_has_a_declared_uncertainty_authority():
    assert set(S.UNCERTAINTY_AUTHORITY) == set(S.FROZEN["species"])
    assert S.UNCERTAINTY_AUTHORITY["tds"]["kind"] == "measured_per_condition"
    for sp in ("caffeine", "trigonelline", "5CQA"):
        auth = S.UNCERTAINTY_AUTHORITY[sp]
        assert auth["kind"] == "declared_range"
        assert tuple(auth["range_pct"]) == S.BIOACTIVE_RSD_BAND_PCT


def test_bioactive_band_is_the_manifest_cell_not_an_invention():
    """The band must come from the MANIFEST, and the campaign must NOT retain a per-cell value."""
    import csv
    with open(REPO / "puckworks/data/MANIFEST.csv", newline="", encoding="utf-8") as fh:
        rows = {r["dataset_id"]: r for r in csv.DictReader(fh)}
    assert "0.3-19.7" in rows["angeloni2023/bioactives"]["uncertainty_retained"]
    assert "not per-cell" in rows["angeloni2023/bioactives"]["uncertainty_retained"]
    assert S.BIOACTIVE_RSD_BAND_PCT == (0.3, 19.7)


def test_total_solids_authority_is_the_measured_per_condition_column():
    from puckworks import data as d
    shots = S._held_out_shots()
    by_cond = S._tds_rsd_by_condition(shots)
    src = {(r["variety"], r["T_degC"], r["p_bar"]): float(r["RSD_pct"])
           for r in d.angeloni_total_solids()}
    assert len(by_cond) == 18
    for k, v in by_cond.items():
        assert v == src[k]


def test_classification_never_reads_the_campaign_proxy():
    """The defect being corrected: 4.70 % must not be able to decide anything.

    Perturbing PROXY_U_PCT to an absurd value must leave every classification unchanged.
    """
    shots = S._held_out_shots()
    tds_rsd = list(S._tds_rsd_by_condition(shots).values())
    effects = [3.0] * 18
    before = {sp: S._classify(sp, effects, tds_rsd)["status"] for sp in S.FROZEN["species"]}
    orig = S.PROXY_U_PCT
    try:
        S.PROXY_U_PCT = 999.0
        after = {sp: S._classify(sp, effects, tds_rsd)["status"] for sp in S.FROZEN["species"]}
    finally:
        S.PROXY_U_PCT = orig
    assert before == after


def test_bioactive_classification_is_three_way_and_uses_both_ends():
    """A median effect inside the declared band must be CHANGES, not silently resolved."""
    shots = S._held_out_shots()
    tds_rsd = list(S._tds_rsd_by_condition(shots).values())
    lo, hi = S.BIOACTIVE_RSD_BAND_PCT
    below = S._classify("caffeine", [lo * 0.5] * 18, tds_rsd)
    inside = S._classify("caffeine", [(lo + hi) / 2] * 18, tds_rsd)
    above = S._classify("caffeine", [hi * 2] * 18, tds_rsd)
    assert below["status"] == S.STATUS_IMMATERIAL
    assert inside["status"] == S.STATUS_CHANGES
    assert above["status"] == S.STATUS_MATERIAL
    assert inside["material_at_low_rsd"] is True
    assert inside["material_at_high_rsd"] is False
    assert inside["threshold_pct"] is None, "a band must not collapse to a single threshold"


def test_total_solids_status_is_named_for_the_median_criterion():
    """The status must not be readable as a condition-level claim.

    This is the defect the 2026-08-04 claim-alignment correction fixed: the decision statistic is
    the MEDIAN effect vs the MEDIAN measured RSD, and individual conditions may still exceed
    their own RSD. The label and its scope have to say so.
    """
    shots = S._held_out_shots()
    tds_rsd = list(S._tds_rsd_by_condition(shots).values())
    med = statistics.median(tds_rsd)
    rec = S._classify("tds", [med * 0.1] * 18, tds_rsd)
    assert rec["status"] == S.STATUS_TDS_IMMATERIAL == "IMMATERIAL_BY_MEDIAN_CRITERION"
    assert "MEDIAN" in rec["status_scope"]
    assert "does NOT assert" in rec["status_scope"]
    hot = S._classify("tds", [med * 10] * 18, tds_rsd)
    assert hot["status"] == S.STATUS_TDS_MATERIAL == "MATERIAL_BY_MEDIAN_CRITERION"


def test_median_immaterial_does_not_imply_zero_condition_exceedances():
    """A constructed case: median below the median RSD while some conditions still exceed.

    If this ever became impossible the 0/18 shorthand would be safe — it is not, and the screen's
    own committed numbers are an instance of it.
    """
    tds_rsd = [1.0] * 9 + [9.0] * 9          # median 5.0
    effects = [2.0] * 9 + [2.0] * 9          # median 2.0 < 5.0, but exceeds 1.0 nine times
    rec = S._classify("tds", effects, tds_rsd)
    assert rec["status"] == S.STATUS_TDS_IMMATERIAL
    assert rec["n_conditions_effect_exceeds_own_rsd"] == 9


def test_committed_total_solids_exceedance_counts_are_the_recorded_ones():
    """Locks the corrected counts against the committed result. NOT zero for two of three."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    got = {s["closure"]: s["per_output"]["tds"]["n_conditions_effect_exceeds_own_rsd"]
           for s in r["substitutions"] if s.get("ran")}
    assert got["vant_hoff_K"] == 2
    assert got["diffusion_coeff"] == 1
    assert got["water_density"] == 0
    for s in r["substitutions"]:
        if not s.get("ran"):
            continue
        assert s["per_output"]["tds"]["n_conditions"] == 18


def test_reader_facing_text_does_not_revert_to_the_false_zero_of_eighteen_claim():
    """The exact regression: 'X of 18' for total solids must match the committed counts.

    Guards the decision record, the README, the candidate card and the ROADMAP entry against a
    blanket 0-of-18 statement covering every admissible swap.
    """
    import re
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    counts = {s["closure"]: s["per_output"]["tds"]["n_conditions_effect_exceeds_own_rsd"]
              for s in r["substitutions"] if s.get("ran")}
    admissible_counts = sorted(counts[c] for c in
                               ("vant_hoff_K", "diffusion_coeff", "water_density"))
    targets = [BUNDLE / "decision.md", BUNDLE / "README.md",
               REPO / "docs/ROADMAP.md",
               *(REPO / "docs/insights/candidates").glob("I-010_*.md")]
    banned = re.compile(r"0 of 18[^.\n]*(every|all|each)[^.\n]*(admissible|swap)", re.I)
    banned2 = re.compile(r"(every|all|each)[^.\n]*(admissible|swap)[^.\n]*0 of 18", re.I)
    for t in targets:
        text = t.read_text(encoding="utf-8")
        assert not banned.search(text), "false blanket 0-of-18 claim in %s" % t.name
        assert not banned2.search(text), "false blanket 0-of-18 claim in %s" % t.name
    # and the true counts must appear in the decision record
    dec = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for n in admissible_counts:
        assert ("%d of 18" % n) in dec, "count %d of 18 missing from decision.md" % n


def test_resolution_rule_is_vector_valued_per_solute():
    """The missing evidence is THREE solute-specific authorities, not one common RSD.

    Added by the 2026-08-05 correction. The earlier shorthand ("above ~3.2 % retires, below
    ~0.7 % survives") collapsed three separate authorities into one scalar and invented a
    survival boundary that is not one. Each solute's threshold is its own LARGEST admissible
    median effect, and the candidate-level rule is an AND over retirement / an OR over survival.
    """
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    adm = [x for x in r["substitutions"] if x.get("ran") and x.get("counts_toward_decision")]
    assert adm, "no admissible substitutions in the committed result"

    # derive, do not hardcode: a solute's threshold is the largest admissible median effect on it
    thresholds = {sp: max(x["per_output"][sp]["median_effect_pct"] for x in adm)
                  for sp in ("caffeine", "trigonelline", "5CQA")}
    assert thresholds["caffeine"] == pytest.approx(3.1707, abs=5e-5)
    assert thresholds["trigonelline"] == pytest.approx(3.0608, abs=5e-5)
    assert thresholds["5CQA"] == pytest.approx(3.1382, abs=5e-5)

    # they are genuinely distinct — that is why a single scalar cannot express the rule
    assert len({round(v, 4) for v in thresholds.values()}) == 3

    def all_immaterial(rsd):
        """Replay the screen's own classifier at a per-solute RSD vector."""
        tds_rsd = list(S._tds_rsd_by_condition(S._held_out_shots()).values())
        for x in adm:
            for sp, thr in thresholds.items():
                effects = [x["per_output"][sp]["median_effect_pct"]] * 18
                orig = S.UNCERTAINTY_AUTHORITY[sp]["range_pct"]
                try:
                    S.UNCERTAINTY_AUTHORITY[sp]["range_pct"] = [rsd[sp], rsd[sp]]
                    st = S._classify(sp, effects, tds_rsd)["status"]
                finally:
                    S.UNCERTAINTY_AUTHORITY[sp]["range_pct"] = orig
                if st != S.STATUS_IMMATERIAL:
                    return False
        return True

    eps = 1e-6
    at_or_above = {sp: thresholds[sp] for sp in thresholds}
    assert all_immaterial(at_or_above), "RETIRE arm: >= its own threshold must be immaterial"

    # OR semantics: ONE solute below its own threshold is enough to keep a material swap alive
    for sp in thresholds:
        v = dict(at_or_above)
        v[sp] = thresholds[sp] - eps
        assert not all_immaterial(v), (
            "a single solute below its own threshold must leave a material swap: %s" % sp)


def test_obsolete_scalar_resolution_shorthand_is_gone():
    """The ~3.2 %/~0.7 % candidate-boundary wording must not return anywhere reader-facing."""
    import re
    targets = [BUNDLE / "decision.md", BUNDLE / "README.md", REPO / "docs/ROADMAP.md",
               *(REPO / "docs/insights/candidates").glob("I-010_*.md")]
    # a scalar retire/survive boundary stated as a single number
    banned = [
        re.compile(r"above\s*~?\s*3\.2\s*%[^.\n]{0,60}retire", re.I),
        re.compile(r"below\s*~?\s*0\.7\s*%[^.\n]{0,60}surviv", re.I),
        re.compile(r"retires the candidate[^.\n]{0,40}below\s*~?\s*0\.7", re.I),
        re.compile(r"splits by substitution", re.I),
    ]
    for t in targets:
        text = t.read_text(encoding="utf-8")
        # the ROADMAP records the WITHDRAWAL of the shorthand; allow it only there, quoted
        for pat in banned:
            for m in pat.finditer(text):
                ctx = text[max(0, m.start() - 260):m.end() + 120]
                assert "withdrawn" in ctx.lower(), (
                    "obsolete scalar resolution shorthand in %s: %r" % (t.name, m.group(0)))


def test_claim_ceiling_is_not_a_conditionwise_total_solids_claim():
    """The ceiling may state a median result; it may not say every condition is below its RSD."""
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    lo = text.index("## Claim ceiling")
    hi = text.index("## Next action")
    ceiling = text[lo:hi]
    assert "at every one of the 18 conditions" not in ceiling
    assert "median" in ceiling.lower(), "the ceiling must name the decision statistic"
    assert "not at every individual condition" in ceiling or "2 of 18" in ceiling


def test_total_solids_classification_is_two_way_against_a_measured_threshold():
    shots = S._held_out_shots()
    tds_rsd = list(S._tds_rsd_by_condition(shots).values())
    med = statistics.median(tds_rsd)
    assert S._classify("tds", [med * 0.1] * 18, tds_rsd)["status"] == S.STATUS_TDS_IMMATERIAL
    assert S._classify("tds", [med * 10] * 18, tds_rsd)["status"] == S.STATUS_TDS_MATERIAL
    rec = S._classify("tds", [med * 10] * 18, tds_rsd)
    assert rec["n_conditions_effect_exceeds_own_rsd"] == 18


def test_outputs_are_not_pooled_into_one_decisive_statistic():
    """Per-output records must exist and the pooled figures must be labelled non-decisive."""
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    assert "per_output" in src
    assert "decides nothing" in src
    # the decision function must consult per-output statuses, never a pooled median
    import inspect
    body = inspect.getsource(S.screen)
    assert "per_output" in body
    assert "pooled_median" not in body


# --------------------------------------------------------------------------------------------
# Substitution admissibility and the frozen flow map
# --------------------------------------------------------------------------------------------
def test_inadmissible_substitutions_are_declared_and_reasoned():
    subs = {s["closure"]: s for s in S.substitutions()}
    assert subs["water_viscosity"]["admissible"] is False
    assert "outside ITS OWN range" in subs["water_viscosity"]["admissibility_note"]
    assert subs["sherwood_h"]["admissible"] is False
    assert subs["sherwood_h"]["patch"] is None
    for name in ("vant_hoff_K", "diffusion_coeff", "water_density"):
        assert subs[name]["admissible"] is True, name


def test_the_two_K_closures_still_disagree_on_the_sign_of_dK_dT():
    """The K(T) swap is only a meaningful probe while this disagreement is live (G4 record)."""
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


def test_solver_output_scales_linearly_in_c_s0():
    """Not used by I-010's arithmetic, but it is why a level swap is NOT a closure swap."""
    from puckworks.models.pannusch2024 import solver as ps
    from puckworks.validation.slow import angeloni_bracket as AB
    sp = dict(ps._solute_params()["caffeine"])
    flow = AB._flow_darcy(9.0, 93.4)
    bounds = AB._matched_bounds(flow)
    p1 = float(ps.simulate_fractions(93.4, flow, bounds, dict(sp, c_s0=1.0), cl1=1.0)[0])
    p2 = float(ps.simulate_fractions(93.4, flow, bounds, dict(sp, c_s0=7.3), cl1=1.0)[0])
    assert p2 / 7.3 == pytest.approx(p1, rel=1e-4)


def test_held_out_unit_is_the_independent_campaign():
    shots = S._held_out_shots()
    assert len(shots) == 18
    assert {r["granulometry"] for r in shots} == {"O"}
    assert {r["on_grid"] for r in shots} == {"True"}
    assert {r["variety"] for r in shots} == {"Arabica", "Robusta"}


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


def test_committed_decision_follows_from_its_own_classification_inputs():
    """The disposition must be DERIVED, not asserted. Re-apply the rule to the stored cells."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    adm = [s for s in r["substitutions"] if s.get("ran") and s.get("counts_toward_decision")]
    material = [(s["closure"], sp) for s in adm
                for sp, v in s["per_output"].items() if v["status"] == S.STATUS_MATERIAL]
    changing = [(s["closure"], sp) for s in adm
                for sp, v in s["per_output"].items() if v["status"] == S.STATUS_CHANGES]
    outside = r["validity_range"]["consumed_outside_declared_range"]
    if outside or material:
        expected = "SURVIVE"
    elif changing:
        expected = "NEEDS_NEW_DATA"
    else:
        expected = "RETIRE"
    assert r["decision"] == expected


def test_inadmissible_substitutions_are_excluded_from_the_decision():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    excluded = [s for s in r["substitutions"] if s.get("ran")
                and not s["counts_toward_decision"]]
    assert excluded, "the viscosity bound should be present and excluded"
    named = {c for c, _ in map(tuple, r["material_cells"] + r["changing_cells"])}
    for s in excluded:
        assert s["closure"] not in named, s["closure"]


def test_every_changing_cell_is_a_bioactive_with_no_retained_rsd():
    """A CHANGES cell can only arise where the authority is a range, never where it is measured."""
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    for _closure, sp in map(tuple, r["changing_cells"]):
        assert S.UNCERTAINTY_AUTHORITY[sp]["kind"] == "declared_range", sp


def test_missing_evidence_is_named_when_the_decision_is_needs_new_data():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    if r["decision"] != "NEEDS_NEW_DATA":
        pytest.skip("only applies to a NEEDS_NEW_DATA disposition")
    why = r["decision_reasoning"].lower()
    assert "solute-specific" in why and "rsd" in why
    assert r["uncertainty"]["solute_specific_rsd_recovered"] is False
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    assert "solute-specific replicate RSD" in text


def test_proxy_is_recorded_as_a_proxy():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert r["uncertainty"]["proxy_U_pct"] == pytest.approx(4.70)
    assert "decision authority" in r["uncertainty"]["proxy_U_role"]
    assert "tds_median_rsd_this_screen_pct" in r["uncertainty"]


def test_decision_records_a_claim_ceiling_and_an_adversarial_check():
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for section in ("## Claim ceiling", "## Adversarial check",
                    "## Strongest alternative explanation", "## Primary figure"):
        assert section in text, section


def test_no_retirement_is_recorded_unless_the_screen_retired():
    r = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    text = (REPO / "docs/insights/RETIRED_CANDIDATES.md").read_text(encoding="utf-8")
    if r["decision"] == "RETIRE":
        assert "**I-010**" in text
    else:
        assert "**I-010**" not in text, (
            "I-010 is in RETIRED_CANDIDATES.md but its screen did not return RETIRE")


def test_claim_ceiling_does_not_generalise_beyond_total_solids():
    """The corrected ceiling must not say the consumer is insensitive full stop."""
    text = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    lo = text.index("## Claim ceiling")
    hi = text.index("## Next action")
    ceiling = text[lo:hi]
    assert "total-solids" in ceiling or "total solids" in ceiling
    assert "0.3–19.7" in ceiling or "0.3-19.7" in ceiling


# --------------------------------------------------------------------------------------------
# Expensive — the numbers themselves
# --------------------------------------------------------------------------------------------
@pytest.mark.slow
def test_total_solids_has_a_real_answer():
    """The one output with retained uncertainty must be resolved either way, never CHANGES."""
    r = S.screen()
    for s in r["substitutions"]:
        if not (s.get("ran") and s.get("counts_toward_decision")):
            continue
        assert s["per_output"]["tds"]["status"] in (S.STATUS_TDS_MATERIAL,
                                                    S.STATUS_TDS_IMMATERIAL)


@pytest.mark.slow
def test_committed_result_does_not_drift_from_a_fresh_run():
    fresh = S.screen()
    committed = json.loads((BUNDLE / "result.json").read_text(encoding="utf-8"))
    assert committed["decision"] == fresh["decision"]
    for cs, fs in zip(committed["substitutions"], fresh["substitutions"]):
        assert cs["closure"] == fs["closure"]
        if not fs["ran"]:
            continue
        for sp in S.FROZEN["species"]:
            assert (cs["per_output"][sp]["median_effect_pct"]
                    == pytest.approx(fs["per_output"][sp]["median_effect_pct"], rel=1e-6)), sp
            assert cs["per_output"][sp]["status"] == fs["per_output"][sp]["status"], sp


@pytest.mark.slow
def test_swap_effects_are_larger_on_the_named_solutes_than_on_the_aggregate():
    """Why the total-solids answer cannot be generalised: the closures are per-solute.

    The K(T) swap carries solute-specific K_ref/gamma, so it must move the named solutes more
    than the aggregate proxy. If that stopped being true, generalising tds would become
    defensible and this test should fail loudly rather than silently permit it.
    """
    r = S.screen()
    k = [s for s in r["substitutions"] if s["closure"] == "vant_hoff_K"][0]
    tds = k["per_output"]["tds"]["median_effect_pct"]
    for sp in ("caffeine", "trigonelline", "5CQA"):
        assert k["per_output"][sp]["median_effect_pct"] > tds, sp

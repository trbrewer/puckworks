"""Focused tests for the I-090 cheap screen (Insight Foundry Wave 3).

These establish the properties the verdict rests on, not the verdict:

  * the protocol commit PRECEDES every result-producing commit, and the result is bound to the
    protocol by SHA-256;
  * the frozen event definitions are the ones the authorities declare, and the three events are
    checked to be distinct rather than assumed so;
  * the pair is a PRODUCER/CONSUMER pair, established three independent ways, and the shared
    front law is demonstrated numerically with a grid-refinement check that distinguishes
    quadrature error from a physical difference;
  * exactly one bounded execution runs, inside machine_mode's own declared configuration, and
    machine_mode is NEVER run against de1_fixtureA;
  * the evidence audit reports one independent extraction and refuses every prohibited
    uncertainty substitute — in particular cadence is never used as a spread;
  * the decision mapping is the protocol's frozen ordering rule, exercised on inputs other than
    the live one;
  * the recorded correction target is named and its files are BYTE-UNCHANGED by this branch.
"""
import copy
import json
import math
import pathlib
import subprocess

import numpy as np
import pytest

from puckworks.analysis import screen_i090_first_drip as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-090"



# --------------------------------------------------------------------------------------------
# CROSS-ENVIRONMENT NUMERICAL EQUIVALENCE
#
# Committed-artifact comparison used to require exact equality. That held only in the
# environment that generated the file: six CI lanes of run 31263251957 (CPython 3.10-3.13,
# `quality`, `min-deps`) reproduce last-ULP disagreement in NumPy/SciPy/BLAS arithmetic.
#
# Observed across those six lanes for I-090 (66 differing float leaves, and NOTHING
# else -- no string, bool, int, null, key, list length, list order, hash, decision or
# provenance field differed anywhere):
#     max |delta|   = 1.243e-14   (execution.window_s, magnitude ~5.9)
#     max relative  = 1.487e-08   (rmse_mm, magnitude ~7.0e-08)
# Large-magnitude leaves need the RELATIVE branch; near-zero leaves need the ABSOLUTE branch.
#
# THESE ARE SOFTWARE PORTABILITY TOLERANCES. They bound how far two builds of the same
# libraries disagree on the same arithmetic. They are NOT model uncertainty, measurement
# uncertainty, parameter uncertainty or evidence uncertainty, and they may never be used to
# round away a scientific discrepancy.
FLOAT_PATH = "execution.rmse_mm"

RESULT_REL_TOL = 1e-12   # 472x the largest relative delta needing it; ceiling 1e-10
RESULT_ABS_TOL = 1e-13   # 19x the largest absolute delta needing it; ceiling 1e-10, and ~1e11
                         # below the 0.01 mm identity threshold


def _assert_result_equivalent(expected, actual, path="$"):
    """Strict recursive comparison: structure and non-floating content EXACT, floats within
    the frozen portability tolerance. Reports the full JSON path of any difference."""
    # bool first: bool is an int subclass in Python
    if isinstance(expected, bool) or isinstance(actual, bool):
        assert isinstance(expected, bool) and isinstance(actual, bool), (
            "%s: bool/non-bool mismatch (%r vs %r)" % (path, expected, actual))
        assert expected == actual, "%s: %r != %r" % (path, expected, actual)
    elif expected is None or actual is None:
        assert expected is None and actual is None, "%s: %r != %r" % (path, expected, actual)
    elif isinstance(expected, dict):
        assert isinstance(actual, dict), "%s: dict vs %s" % (path, type(actual).__name__)
        missing, extra = set(expected) - set(actual), set(actual) - set(expected)
        assert not missing and not extra, (
            "%s: key set differs (missing=%s extra=%s)" % (path, sorted(missing), sorted(extra)))
        for k in expected:
            _assert_result_equivalent(expected[k], actual[k], "%s.%s" % (path, k))
    elif isinstance(expected, list):
        assert isinstance(actual, list), "%s: list vs %s" % (path, type(actual).__name__)
        assert len(expected) == len(actual), (
            "%s: length %d != %d" % (path, len(expected), len(actual)))
        for i, (e, a) in enumerate(zip(expected, actual)):
            _assert_result_equivalent(e, a, "%s[%d]" % (path, i))
    elif isinstance(expected, str):
        assert isinstance(actual, str) and expected == actual, (
            "%s: %r != %r" % (path, expected, actual))
    elif isinstance(expected, int) and isinstance(actual, int):
        assert expected == actual, "%s: int %r != %r" % (path, expected, actual)
    elif isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        assert math.isfinite(expected) and math.isfinite(actual), (
            "%s: non-finite value (%r vs %r)" % (path, expected, actual))
        if not math.isclose(expected, actual,
                            rel_tol=RESULT_REL_TOL, abs_tol=RESULT_ABS_TOL):
            delta = abs(expected - actual)
            scale = max(abs(expected), abs(actual))
            raise AssertionError(
                "%s: outside the portability tolerance\n"
                "  committed = %r\n  fresh     = %r\n"
                "  |delta|   = %.6e\n  relative  = %s\n"
                "  permitted = rel_tol %.0e / abs_tol %.0e"
                % (path, expected, actual, delta,
                   ("%.6e" % (delta / scale)) if scale else "n/a",
                   RESULT_REL_TOL, RESULT_ABS_TOL))
    else:
        raise AssertionError("%s: unrecognised type pair %s / %s"
                             % (path, type(expected).__name__, type(actual).__name__))

@pytest.fixture(scope="module")
def result():
    return S.screen()


def _git(*args):
    return subprocess.run(("git",) + args, cwd=REPO, capture_output=True, text=True)


def _history_is_truncated():
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
# PROTOCOL FIRST, AND BOUND BY HASH
# --------------------------------------------------------------------------------------------
def test_protocol_document_exists_and_freezes_all_twelve_items():
    p = BUNDLE / "PROTOCOL.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for n in range(1, 13):
        assert ("\n## %d." % n) in text, "protocol item %d is missing" % n
    assert "Ordering rule, frozen now" in text
    assert "MECHANISM_IDENTITY_CHECK" in text
    assert "Uncertainty may not be manufactured" in text


def test_identity_thresholds_are_the_ones_the_protocol_froze():
    text = (BUNDLE / "PROTOCOL.md").read_text(encoding="utf-8")
    assert "RMSE < 0.01 mm" in text and "max |Δs| < 0.02 mm" in text
    assert S.IDENTITY_RMSE_MAX_MM == 0.01
    assert S.IDENTITY_MAXABS_MAX_MM == 0.02


def test_protocol_commit_precedes_every_result_producing_commit():
    if _history_is_truncated():
        pytest.skip("shallow/truncated checkout: per-path commit order is not observable here")

    def commits_touching(path):
        return _git("log", "--format=%H", "--", path).stdout.split()
    proto = commits_touching("docs/insights/screens/I-090/PROTOCOL.md")
    if not proto:
        pytest.skip("protocol not yet committed (working-tree run)")
    results = []
    for rel in ("docs/insights/screens/I-090/result.json",
                "puckworks/analysis/screen_i090_first_drip.py",
                "docs/insights/screens/I-090/decision.md"):
        results += commits_touching(rel)
    if not results:
        pytest.skip("no result-producing commit yet")
    order = _git("log", "--format=%H").stdout.split()
    pos = {h: i for i, h in enumerate(order)}
    assert max(pos[h] for h in proto if h in pos) > max(pos[h] for h in results if h in pos), (
        "the protocol commit must be OLDER than the first result-producing commit")


def test_result_is_hash_bound_to_the_live_protocol_and_inputs(result):
    live = S._sha256(S.PROTOCOL_PATH)
    assert result["protocol"]["sha256"] == live
    assert result["provenance"]["protocol_sha256"] == live
    assert result["provenance"]["base_commit"] == S.BASE_COMMIT
    for rel, digest in result["provenance"]["input_sha256"].items():
        assert digest == S._sha256(rel), "input hash drifted for %s" % rel
    assert len(result["provenance"]["input_sha256"]) == len(S.INPUT_FILES)


def test_committed_result_is_cross_platform_numerically_equivalent(result):
    """Structure and non-floating content EXACT; computed floats within the frozen portability
    tolerance. Byte identity across numerical environments was never achievable and is not the
    property this artifact needs."""
    path = BUNDLE / "result.json"
    if not path.exists():
        pytest.skip("result not yet written")
    _assert_result_equivalent(json.loads(path.read_text(encoding="utf-8")), result)


def test_screen_is_deterministic():
    assert json.dumps(S.screen(), sort_keys=True) == json.dumps(S.screen(), sort_keys=True)


# --------------------------------------------------------------------------------------------
# THE OBSERVABLE-DEFINITION GATE
# --------------------------------------------------------------------------------------------
def test_three_events_are_distinct_and_each_is_fully_specified(result):
    defs = result["observable_definition"]["three_distinct_events"]
    assert len(defs) == 3
    for d in defs:
        for field in ("event", "authority", "physical_event", "detection_threshold",
                      "time_origin", "pressure_history", "known_delay", "rig"):
            assert d.get(field), "%s is missing %s" % (d["event"], field)
    # distinct on the fields that decide the gate
    assert len({d["time_origin"] for d in defs}) == 3
    assert result["observable_definition"]["one_common_definition_exists"] is False
    assert result["observable_definition"]["units"] == "s"


def test_the_measured_event_is_declared_not_a_model_output():
    card = (REPO / "docs/cards/foster2025.md").read_text(encoding="utf-8")
    flat = " ".join(card.split())
    assert "the measurement-side comparator (first crossing of a 0.5 g scale threshold), NOT a " \
           "model output" in flat


def test_machine_mode_reported_time_carries_a_fitted_shift(result):
    from puckworks.models.foster2025.machine_mode import FosterParams
    assert FosterParams().t_shift == 0.796
    b = result["observable_definition"]["three_distinct_events"][1]
    assert "FITTED start-time alignment" in b["time_origin"]


def test_event_gate_fails_on_all_three_checks(result):
    g = result["event_definition_gate"]
    assert g["passed"] is False
    assert set(g["failed"]) == {"E1_same_event_across_the_two_components",
                                "E2_model_event_equals_measured_event",
                                "E3_the_components_are_rivals"}


# --------------------------------------------------------------------------------------------
# E3 — CO-LOCATION IS NOT A RELATIONSHIP
# --------------------------------------------------------------------------------------------
def test_both_components_bind_to_one_card_and_the_card_says_outputs_serve_both(result):
    rel = result["relationship_check"]
    assert rel["both_components_share_one_card"] is True
    assert set(rel["card_binding"].values()) == {"docs/cards/foster2025.md"}
    assert rel["card_declares_outputs_attributed_to_both"] is True
    assert rel["are_rivals"] is False
    assert rel["relationship"] == "PRODUCER_CONSUMER"


def test_the_two_components_sit_on_different_pipeline_stages(result):
    rel = result["relationship_check"]
    assert rel["stages_differ"] is True
    assert rel["registry_stages"][S.COMPONENT_A] == "infiltration"
    assert rel["registry_stages"][S.COMPONENT_B] == "machine"


def test_each_module_names_the_other_as_its_counterpart(result):
    rel = result["relationship_check"]
    assert rel["infiltration_doc_names_machine_mode"] is True
    assert rel["machine_mode_doc_names_complement"] is True


def test_the_tension_row_edge_comes_from_one_outputs_clause():
    """The generated row's premise, checked at its source rather than argued about."""
    import csv
    rows = {}
    with open(REPO / "docs/insights/generated/observable_index.csv", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row["model"] in (S.COMPONENT_A, S.COMPONENT_B):
                rows[row["model"]] = row["first_drip_time"]
    assert rows == {S.COMPONENT_A: "predicts", S.COMPONENT_B: "predicts"}
    # ... and both of those edges are sourced from the SAME card's Outputs clause
    corpus = json.loads((REPO / "docs/insights/generated/corpus_map.json").read_text())
    cards = {e["id"]: e["attrs"].get("card_path") for e in corpus.get("entities", [])
             if e.get("id", "").startswith("model:foster2025.")}
    assert len(set(cards.values())) == 1


# --------------------------------------------------------------------------------------------
# THE ONE PERMITTED EXECUTION
# --------------------------------------------------------------------------------------------
def test_exactly_one_bounded_execution_class_is_declared(result):
    e = result["execution"]
    assert e["execution_class"] == "MECHANISM_IDENTITY_CHECK"
    assert e["is_a_discrimination_run"] is False
    assert e["model_solves_performed"] == 1 + len(S.IDENTITY_GRIDS)
    assert set(result["models_executed"]) == {S.COMPONENT_A, S.COMPONENT_B}


def test_machine_mode_is_never_run_against_the_de1_fixture():
    """The fixture must not reach machine_mode. Instrument the loader and the solver together."""
    from puckworks.models.foster2025 import machine_mode as fm
    seen = []
    real_solve, real_fixture = fm.solve, S._fixture

    def spy_solve(p=None):
        seen.append(("solve", p))
        return real_solve(p)
    fm.solve = spy_solve
    try:
        S.screen()
    finally:
        fm.solve = real_solve
    assert len(seen) == 1, "machine_mode was solved %d times, expected exactly 1" % len(seen)
    assert seen[0][1] is None, "machine_mode was solved with a NON-DEFAULT parameter set"
    # and the module offers no way to feed it a recorded trace in the first place
    import inspect
    assert set(inspect.signature(real_solve).parameters) == {"p"}


def test_machine_mode_cannot_consume_a_recorded_pressure_history(result):
    vr = result["validity_range_check"]
    assert vr["machine_mode_can_consume_a_recorded_trace"] is False
    assert vr["de1_inside_machine_mode_range"] is False
    assert "refitting the pump characteristic" in vr["machine_mode_consumption_note"]


def test_the_identity_check_ran_in_the_components_own_declared_configuration(result):
    from puckworks.models.foster2025.machine_mode import FosterParams
    p = FosterParams()
    cfg = result["execution"]["configuration"]
    assert "Table I" in cfg
    assert ("%.3f" % (p.phi_T)) in cfg or ("%.3f" % p.phi_T) in cfg
    assert result["execution"]["bed_depth_mm"] == pytest.approx(p.L * 1e3)


def test_the_shared_front_law_identity_holds_within_the_frozen_thresholds(result):
    e = result["execution"]
    assert e["identity_holds"] is True
    assert e["rmse_mm"] < S.IDENTITY_RMSE_MAX_MM
    assert e["max_abs_mm"] < S.IDENTITY_MAXABS_MAX_MM


def test_the_residual_is_quadrature_error_not_a_physical_difference(result):
    """A residual that does not fall under grid refinement would mean the two implementations
    genuinely differ. Requiring the fall is what separates 'same law' from 'close enough'."""
    e = result["execution"]
    assert e["residual_falls_with_grid_refinement"] is True
    rm = [x["rmse_mm"] for x in e["refinement"]]
    assert rm == sorted(rm, reverse=True)
    assert rm[0] / rm[-1] > 50, "the residual barely moves; it may not be quadrature error"
    assert [x["n_grid"] for x in e["refinement"]] == list(S.IDENTITY_GRIDS)


def test_the_identity_disclaims_any_claim_about_correctness(result):
    assert "not about the physics being right" in \
        result["execution"]["what_this_does_not_show"].replace("\n", " ")


# --------------------------------------------------------------------------------------------
# EVIDENCE AND REPLICATE AUDIT
# --------------------------------------------------------------------------------------------
def test_evidence_is_one_independent_extraction_with_no_spread(result):
    ev = result["evidence_audit"]
    assert ev["independent_extractions"] == 1
    assert ev["rows_are_samples_not_replicates"] is True
    assert ev["replicate_spread_available"] is False
    assert ev["experimental_spread_value"] is None
    assert ev["n_samples"] > 1


def test_cadence_is_recorded_as_resolution_and_never_used_as_a_spread(result):
    ev = result["evidence_audit"]
    assert "NOT a population variance" in ev["event_resolution_note"]
    unc = result["uncertainty_authorities"]
    assert unc["measurement"]["replicate_spread"] is None
    assert unc[S.COMPONENT_A]["numerical_band_on_first_drip"] is None
    assert unc[S.COMPONENT_B]["numerical_band_on_first_drip"] is None
    b2 = [c for c in result["adversarial_checks"] if c["id"] == "B2"][0]
    assert b2["overturns"] is False and "no." in b2["result"]


def test_every_prohibited_uncertainty_substitute_is_declared_unused(result):
    ev = result["evidence_audit"]
    prohibited = set(ev["prohibited_uncertainty_substitutes_not_used"])
    for item in ("between-model separation", "an assumed coefficient of variation",
                 "a qualitative evidence-strength label", "solver convergence"):
        assert item in prohibited
    # and no between-model separation is reported anywhere to be misused
    assert "separation" not in json.dumps(result["primary_numerical_findings"]).lower() or \
        "no between-model separation" in result["primary_numerical_findings"]["note"]


def test_observed_first_drip_matches_the_repositorys_single_authoritative_constant(result):
    from puckworks.models.foster2025 import infiltration as inf
    fx = S._fixture()
    t = np.asarray(fx["elapsed_s"], float); w = np.asarray(fx["weight_g"], float)
    assert result["evidence_audit"]["observed_first_drip_s"] == inf.observed_first_drip_s(t, w)
    assert result["evidence_audit"]["detection_threshold_g"] == inf.FIRST_DRIP_THRESHOLD_G


def test_threshold_sensitivity_is_measured_and_exceeds_the_model_bracket(result):
    """B1. If a convention moves the measured event by more than the model spread it is checked
    against, the convention is load-bearing and must be stated, not assumed away."""
    b1 = [c for c in result["adversarial_checks"] if c["id"] == "B1"][0]
    assert "sampling intervals" in b1["result"]
    assert "WIDER than the 1.4 s model bracket" in b1["note"]
    from puckworks.models.foster2025 import infiltration as inf
    fx = S._fixture()
    t = np.asarray(fx["elapsed_s"], float); w = np.asarray(fx["weight_g"], float)
    vals = [inf.observed_first_drip_s(t, w, threshold_g=g) for g in (0.05, 2.0)]
    assert (max(vals) - min(vals)) > 1.4, "the stated span must be reproducible from the fixture"


def test_configuration_is_not_fully_specified_and_says_why(result):
    ev = result["evidence_audit"]
    assert ev["matched_operating_configuration_fully_specified"] is False
    assert "ASSUMED" in ev["grind_setting"]
    assert "FITTED to this same shot" in ev["kappa"]


# --------------------------------------------------------------------------------------------
# DECISION MAPPING
# --------------------------------------------------------------------------------------------
def test_live_decision_is_retire_on_structural_grounds(result):
    assert result["decision"] == "RETIRE"
    assert result["decision_record"]["structural_failures"]
    assert result["decision_record"]["would_replicates_have_rescued_it"] is False


def test_a_non_structural_failure_would_map_to_needs_new_data(result):
    """The ordering rule is a mapping, so exercise the other branch. If the pair were genuine
    rivals with one common event definition, single-replicate evidence would be NEEDS_NEW_DATA."""
    fake = copy.deepcopy(result["event_definition_gate"])
    for key in fake["checks"]:
        fake["checks"][key]["passed"] = True
    fake["passed"] = False                    # a non-E obstacle, e.g. missing uncertainty
    fake["failed"] = ["U1_no_declared_discrimination_uncertainty"]
    assert S.decide(fake, result["evidence_audit"])["decision"] == "NEEDS_NEW_DATA"


def test_a_passing_gate_refuses_to_produce_a_decision_here(result):
    fake = copy.deepcopy(result["event_definition_gate"])
    for key in fake["checks"]:
        fake["checks"][key]["passed"] = True
    fake["passed"] = True
    fake["failed"] = []
    with pytest.raises(AssertionError):
        S.decide(fake, result["evidence_audit"])


def test_retirement_states_plainly_that_replicates_would_not_rescue_it(result):
    b7 = [c for c in result["adversarial_checks"] if c["id"] == "B7"][0]
    assert b7["result"].startswith("NO.")
    assert "waste the experiment" in b7["result"]
    assert "Replicates ALONE do not reopen this candidate" in result["reopen_condition"]


def test_the_screen_does_not_declare_the_observable_worthless(result):
    """B8. Bounding one pair is not the same as retiring an observable, and the difference has
    to be stated or the next session will read the retirement too broadly."""
    b8 = [c for c in result["adversarial_checks"] if c["id"] == "B8"][0]
    assert "no, and this screen does not claim that" in b8["result"]
    assert "mo2023_2" in b8["result"]


def test_every_adversarial_check_ran_and_none_overturned(result):
    ids = [c["id"] for c in result["adversarial_checks"]]
    assert ids == ["B%d" % i for i in range(1, 9)]
    assert result["adversarial_checks_overturning"] == []


# --------------------------------------------------------------------------------------------
# THE RECORDED-BUT-NOT-APPLIED CORRECTION TARGET
# --------------------------------------------------------------------------------------------
def test_the_recorded_finding_quotes_both_live_authorities_verbatim(result):
    f = result["recorded_findings"][0]
    row = S._manifest_row("de1_fixtureA")
    assert f["current_value"] == row["validation_strength"]
    assert f["current_value"] == "independent (parameter-free triangle)"
    roadmap = (REPO / "docs/ROADMAP.md").read_text(encoding="utf-8")
    assert f["contradicting_quote"] in " ".join(roadmap.split()).replace("`", "`")
    assert f["applied"] is False


def test_named_correction_targets_are_byte_unchanged_by_this_branch():
    """A screen records a correction target; it does not apply one. CLAUDE.md: the Foundry 'may
    not change, promote or restate any label, badge or validation rung'.

    The property differs per surface, and conflating them would make the guard wrong rather than
    strict. The manifest and the card must be byte-identical. `docs/ROADMAP.md` must NOT be, and
    could not be: its §7.1 changelog is append-only and CLAUDE.md REQUIRES an entry for work like
    this, so asserting it unchanged would assert something the repository's own contract forbids.
    The ROADMAP property — pre-existing §7.1 rows byte-identical and in order, changes confined to
    the changelog region — is enforced by `tests/test_wave3_roadmap_history.py`, which states it
    over row content rather than over a line count.
    """
    base = S.BASE_COMMIT
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("base commit not present in this checkout")

    for path in S.CORRECTION_TARGET_FILES:
        r = _git("diff", "--numstat", base, "HEAD", "--", path)
        assert r.stdout.strip() == "", "%s was edited; a screen may not apply a correction" % path

    assert S.CORRECTION_TARGET_APPEND_ONLY == ("docs/ROADMAP.md",)
    assert (REPO / "tests/test_wave3_roadmap_history.py").exists(), (
        "the append-only ROADMAP property must be enforced somewhere")


def test_the_over_claim_wording_still_stands_verbatim():
    """The direct test of 'recorded, not applied': if the screen had corrected the cell, this
    wording would be gone. Its continued presence is the evidence that it did not."""
    for rel, wording in S.UNCORRECTED_WORDING.items():
        text = (REPO / rel).read_text(encoding="utf-8")
        assert wording in text, (
            "%r is no longer present in %s — the correction appears to have been APPLIED, which "
            "a screen may not do" % (wording, rel))
    # and the manifest cell itself is still the uncorrected value the finding names
    assert S._manifest_row("de1_fixtureA")["validation_strength"] == \
        "independent (parameter-free triangle)"


def test_no_evidence_label_or_rung_is_changed(result):
    assert result["evidence_labels_unchanged"] is True
    assert result["administrative_exception_invoked"] is False
    assert result["registry_entries"][S.COMPONENT_A]["evidence_strength"] == \
        "sign_or_compatibility"
    assert result["registry_entries"][S.COMPONENT_B]["evidence_strength"] == \
        "source_curve_reproduction"


def test_the_finding_is_distinct_from_the_i045_selection(result):
    """I-045 adjudicated three manifest rows and its own test asserts de1_fixtureA is foreign to
    that selection. This finding must not be a rediscovery of that one."""
    f = result["recorded_findings"][0]
    assert f["distinct_from_I045"] is True
    i045 = (REPO / "tests/test_screen_i045.py").read_text(encoding="utf-8")
    assert "de1_fixtureA" in i045 and "foreign" in i045


def test_claim_ceiling_refuses_the_correctness_reading(result):
    c = result["claim_ceiling"]
    assert "does NOT establish that the shared front law is CORRECT" in c
    assert "sign_or_compatibility" in c and "source_curve_reproduction" in c
    assert "does NOT validate the unresolved de1_fixtureA provenance condition" in c


def test_bundle_is_present_and_carries_the_disposition():
    for name in ("PROTOCOL.md", "result.json", "decision.md", "README.md"):
        assert (BUNDLE / name).exists(), "%s is missing from the bundle" % name
    dec = (BUNDLE / "decision.md").read_text(encoding="utf-8")
    for tag in ("CHEAP_SCIENTIFIC_SCREEN", "NOT_A_PUBLICATION_RESULT",
                "NOT_A_MODEL_VALIDATION_UPGRADE"):
        assert tag in dec
    for heading in ("## Decision", "## Claim ceiling", "## Adversarial check", "## Reproduction"):
        assert heading in dec


# --------------------------------------------------------------------------------------------
# THE PORTABILITY TOLERANCE MUST NOT BE VACUOUS
#
# A tolerance that accepts a real change is worse than no tolerance at all. Every mutation below
# is applied to a deep copy of the in-memory result; the committed artifact is never rewritten.
# --------------------------------------------------------------------------------------------
def _at(obj, path):
    """Fetch/lset by a simple dotted/indexed path used only by these regressions."""
    cur = obj
    for part in path.split("."):
        if part.endswith("]"):
            name, idx = part[:-1].split("[")
            cur = cur[name][int(idx)] if name else cur[int(idx)]
        else:
            cur = cur[part]
    return cur


def _set(obj, path, value):
    parts = path.split(".")
    parent = _at(obj, ".".join(parts[:-1])) if len(parts) > 1 else obj
    last = parts[-1]
    if last.endswith("]"):
        name, idx = last[:-1].split("[")
        (parent[name] if name else parent)[int(idx)] = value
    else:
        parent[last] = value


def _rejects(expected, actual):
    with pytest.raises(AssertionError):
        _assert_result_equivalent(expected, actual)


def test_tolerance_accepts_a_last_ulp_perturbation(result):
    """The exact defect six CI lanes reported."""
    fresh = copy.deepcopy(result)
    _set(fresh, FLOAT_PATH, math.nextafter(_at(result, FLOAT_PATH), math.inf))
    assert _at(fresh, FLOAT_PATH) != _at(result, FLOAT_PATH)
    _assert_result_equivalent(result, fresh)                      # must NOT raise


def test_tolerance_accepts_a_perturbation_just_inside_it(result):
    fresh = copy.deepcopy(result)
    base = _at(result, FLOAT_PATH)
    _set(fresh, FLOAT_PATH, base + 0.5 * max(RESULT_REL_TOL * abs(base), RESULT_ABS_TOL))
    _assert_result_equivalent(result, fresh)                      # must NOT raise


def test_tolerance_rejects_a_perturbation_beyond_it(result):
    fresh = copy.deepcopy(result)
    base = _at(result, FLOAT_PATH)
    _set(fresh, FLOAT_PATH, base + 1e3 * max(RESULT_REL_TOL * abs(base), RESULT_ABS_TOL))
    _rejects(result, fresh)


def test_removing_a_key_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh.pop("decision")
    _rejects(result, fresh)


def test_adding_a_key_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh["an_unexpected_key"] = 1
    _rejects(result, fresh)


def test_changing_a_list_length_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh["adversarial_checks"] = fresh["adversarial_checks"][:-1]
    _rejects(result, fresh)


def test_reordering_a_list_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh["adversarial_checks"][0], fresh["adversarial_checks"][1] = (
        fresh["adversarial_checks"][1], fresh["adversarial_checks"][0])
    _rejects(result, fresh)


def test_changing_the_decision_is_rejected(result):
    fresh = copy.deepcopy(result)
    assert fresh["decision"] == "RETIRE"
    fresh["decision"] = "SURVIVE"
    _rejects(result, fresh)


def test_changing_a_boolean_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh["evidence_labels_unchanged"] = not fresh["evidence_labels_unchanged"]
    _rejects(result, fresh)


def test_changing_an_integer_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh["model_solves_performed"] = fresh["model_solves_performed"] + 1
    _rejects(result, fresh)


def test_changing_a_sha256_is_rejected(result):
    fresh = copy.deepcopy(result)
    fresh["protocol"]["sha256"] = "0" * 64
    _rejects(result, fresh)
    fresh = copy.deepcopy(result)
    key = sorted(fresh["provenance"]["input_sha256"])[0]
    fresh["provenance"]["input_sha256"][key] = "0" * 64
    _rejects(result, fresh)


def test_nan_and_infinity_are_rejected(result):
    for bad in (float("nan"), float("inf")):
        fresh = copy.deepcopy(result)
        _set(fresh, FLOAT_PATH, bad)
        _rejects(result, fresh)


def test_a_bool_substituted_for_a_number_is_rejected(result):
    fresh = copy.deepcopy(result)
    _set(fresh, FLOAT_PATH, True)
    _rejects(result, fresh)


def test_a_threshold_crossing_identity_residual_is_rejected(result):
    """I-090's identity rests on RMSE < 0.01 mm and max < 0.02 mm. Mutations across those frozen
    thresholds must be rejected, not absorbed by the portability tolerance."""
    for path, limit in (("execution.rmse_mm", S.IDENTITY_RMSE_MAX_MM),
                        ("execution.max_abs_mm", S.IDENTITY_MAXABS_MAX_MM)):
        assert _at(result, path) < limit
        fresh = copy.deepcopy(result)
        _set(fresh, path, limit * 10.0)
        _rejects(result, fresh)
        assert not (_at(fresh, path) < limit)

"""Focused tests for the I-072 cheap screen (Insight Foundry Wave 3).

These establish the properties the verdict rests on, not the verdict:

  * the protocol commit PRECEDES every result-producing commit, checked against git history,
    and the committed result is bound to the protocol by SHA-256;
  * NEITHER COMPONENT IS EXECUTED — asserted by replacing every forbidden entry point with a
    tripwire and running the whole screen, including the figure;
  * the frozen observable definitions (quantity, units, index, normalisation, intervention,
    initial state) are the ones the registry and the module contracts actually declare;
  * the two structural degeneracies are real: the streamtube ensemble mean is exactly one, and
    the swelling model carries no lateral index;
  * validity-range enforcement — the d32 coincidence is COMPUTED and then explicitly refused as
    a matched grind, so the check cannot silently become a bridge;
  * uncertainty provenance is explicit and nothing is borrowed across observables;
  * the decision mapping is the protocol's frozen ordering rule, and it is exercised on inputs
    other than the live one so the mapping is tested rather than the outcome restated;
  * no evidence label, rung or registry field is changed by the screen.
"""
import copy
import json
import math
import pathlib
import subprocess

import pytest

from puckworks.analysis import screen_i072_matched_observable as S

REPO = pathlib.Path(__file__).resolve().parents[1]
BUNDLE = REPO / "docs/insights/screens/I-072"



# --------------------------------------------------------------------------------------------
# CROSS-ENVIRONMENT NUMERICAL EQUIVALENCE
#
# Committed-artifact comparison used to require exact equality. That held only in the
# environment that generated the file: six CI lanes of run 31263251957 (CPython 3.10-3.13,
# `quality`, `min-deps`) reproduce last-ULP disagreement in NumPy/SciPy/BLAS arithmetic.
#
# Observed across those six lanes for I-072 (156 differing float leaves, and NOTHING
# else -- no string, bool, int, null, key, list length, list order, hash, decision or
# provenance field differed anywhere):
#     max |delta|   = 1.279e-13   (across_tube_cv, magnitude ~85)
#     max relative  = 5.0e-01   (gauss_hermite_abs_dev_from_1, magnitude ~1e-16)
# Large-magnitude leaves need the RELATIVE branch; near-zero leaves need the ABSOLUTE branch.
#
# THESE ARE SOFTWARE PORTABILITY TOLERANCES. They bound how far two builds of the same
# libraries disagree on the same arithmetic. They are NOT model uncertainty, measurement
# uncertainty, parameter uncertainty or evidence uncertainty, and they may never be used to
# round away a scientific discrepancy.
FLOAT_PATH = ("structural_degeneracy.streamtube_bed_total_flow_ratio_is_identically_1"
              ".rows[0].analytic_lognormal_cv")

RESULT_REL_TOL = 1e-13   # 66x the largest relative delta needing it; ceiling 1e-12
RESULT_ABS_TOL = 1e-14   # 18x the largest absolute delta needing it; = ceiling, and 100x below
                         # the 1e-12 structural decision threshold


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
def test_protocol_document_exists_and_freezes_all_ten_items():
    p = BUNDLE / "PROTOCOL.md"
    assert p.exists()
    text = p.read_text(encoding="utf-8")
    for n in range(1, 11):
        assert ("\n## %d." % n) in text, "protocol item %d is missing" % n
    # the two commitments that stop a post-result choice
    assert "Ordering rule, frozen now" in text
    assert "**Inadmissible**" in text


def test_protocol_commit_precedes_every_result_producing_commit():
    if _history_is_truncated():
        pytest.skip("shallow/truncated checkout: per-path commit order is not observable here")

    def commits_touching(path):
        return _git("log", "--format=%H", "--", path).stdout.split()   # newest first
    proto = commits_touching("docs/insights/screens/I-072/PROTOCOL.md")
    if not proto:
        pytest.skip("protocol not yet committed (working-tree run)")
    results = []
    for rel in ("docs/insights/screens/I-072/result.json",
                "puckworks/analysis/screen_i072_matched_observable.py",
                "docs/insights/screens/I-072/decision.md"):
        results += commits_touching(rel)
    if not results:
        pytest.skip("no result-producing commit yet")
    order = _git("log", "--format=%H").stdout.split()
    pos = {h: i for i, h in enumerate(order)}          # 0 = newest
    first_protocol = max(pos[h] for h in proto if h in pos)
    first_result = max(pos[h] for h in results if h in pos)
    assert first_protocol > first_result, (
        "the protocol commit must be OLDER than the first result-producing commit")


def test_result_is_hash_bound_to_the_live_protocol_and_inputs(result):
    live = S._sha256(S.PROTOCOL_PATH)
    assert result["protocol"]["sha256"] == live
    assert result["provenance"]["protocol_sha256"] == live
    assert result["protocol"]["frozen_before_execution"] is True
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
# NO MODEL EXECUTION AFTER A FAILED SEMANTIC GATE
# --------------------------------------------------------------------------------------------
def test_neither_component_is_executed_anywhere_in_the_screen():
    """Replace every forbidden entry point with a tripwire and run the whole screen.

    This is the protocol's execution rule made enforceable: a failed compatibility gate must
    stop execution, and 'we did not run it' must be a checked property, not a claim in prose.
    """
    import importlib
    tripped, restore = [], []
    for mod_name, attr in S.FORBIDDEN_EXECUTION:
        mod = importlib.import_module(mod_name)
        real = getattr(mod, attr)
        restore.append((mod, attr, real))

        def _trip(*a, _n="%s.%s" % (mod_name, attr), **k):
            tripped.append(_n)
            raise AssertionError("forbidden execution: %s" % _n)
        setattr(mod, attr, _trip)
    tmp = BUNDLE / "figures/_test_tmp.png"
    try:
        r = S.screen()
        if _has_matplotlib():
            S.figure(result=r, path=str(tmp))
    finally:
        for mod, attr, real in restore:
            setattr(mod, attr, real)
        if tmp.exists():
            tmp.unlink()
    assert tripped == [], "a forbidden entry point was called: %s" % tripped
    assert r["models_executed"] == []
    assert r["model_solves_performed"] == 0


def test_forbidden_set_covers_both_components_public_solvers():
    forbidden = {"%s.%s" % f for f in S.FORBIDDEN_EXECUTION}
    assert any("mo2023_2.swelling.flow_decay" in f for f in forbidden)
    assert any("streamtube.EYResponse" in f for f in forbidden)
    assert any("streamtube.simulate_ensemble_dynamic" in f for f in forbidden)
    # the streamtube's Rung A runs Cameron shots, so Cameron is the real execution surface
    assert any("extraction_bdf.simulate_shot" in f for f in forbidden)


def test_permitted_structural_functions_perform_no_solve():
    """The two permitted helpers must be pure constructors, not entry points into a solver."""
    import inspect
    from puckworks.models.brewer2026 import streamtube as st
    from puckworks.models.cameron2020 import extraction_bdf as em
    for fn in (st.lognormal_nodes, em.grind_microstructure):
        src = inspect.getsource(fn)
        for banned in ("solve_ivp", "simulate_shot", "EYResponse(", "odeint"):
            assert banned not in src, "%s reaches a solver via %s" % (fn.__name__, banned)


# --------------------------------------------------------------------------------------------
# THE FROZEN OBSERVABLE DEFINITIONS ARE THE ONES THE AUTHORITIES DECLARE
# --------------------------------------------------------------------------------------------
def test_observable_definitions_carry_quantity_units_index_and_intervention(result):
    for comp in (S.COMPONENT_A, S.COMPONENT_B):
        d = result["observable_definition"][comp]
        for field in ("quantity", "units", "index", "normalisation", "intervention",
                      "initial_state"):
            assert d.get(field), "%s is missing %s" % (comp, field)
        assert d["units"] == "dimensionless"
    a = result["observable_definition"][S.COMPONENT_A]
    b = result["observable_definition"][S.COMPONENT_B]
    assert a["index"] == "time" and a["lateral_index"] is None
    assert b["index"] == "tube" and b["time_index"] is None
    assert "fixed dP" in a["intervention"]
    assert "fixed delivered mass" in b["intervention"]


def test_registry_fields_are_copied_live_not_restated(result):
    from puckworks.registry import components
    live = {c.name: c for c in components()}
    for comp in (S.COMPONENT_A, S.COMPONENT_B):
        rec = result["registry_entries"][comp]
        assert rec["valid_range"] == live[comp].valid_range
        assert rec["assumptions"] == live[comp].assumptions
        assert rec["evidence_strength"] == live[comp].evidence_strength


def test_streamtube_card_absence_is_declared_not_assumed(result):
    """The candidate's readiness note: this component has no card, and the result must say so."""
    assert not (REPO / "docs/cards/brewer2026_streamtube.md").exists()
    assert not (REPO / "docs/cards/brewer2026.md").exists()
    u = result["uncertainty_authorities"]["brewer2026_streamtube"]
    assert u["card_exists"] is False
    assert "registry" in u["card_note"]


# --------------------------------------------------------------------------------------------
# THE TWO STRUCTURAL DEGENERACIES
# --------------------------------------------------------------------------------------------
def test_streamtube_ensemble_mean_is_exactly_one(result):
    s = result["structural_degeneracy"]["streamtube_bed_total_flow_ratio_is_identically_1"]
    assert s["holds"] is True
    assert s["quantile_midpoint_max_abs_deviation"] < 1e-12
    assert s["gauss_hermite_max_abs_deviation_within_scope"] < 1e-12
    assert s["gauss_hermite_scope"] == "sigma <= %s" % S.SIGMA_EXACT_MAX
    assert len(s["rows"]) == len(S.SIGMA_GRID)


def test_large_sigma_quadrature_error_is_reported_not_hidden(result):
    """The 15-node rule loses accuracy at sigma >= 2. That is a quadrature artifact and it is
    disclosed; the machine-precision claim is scoped rather than quietly extended over it."""
    s = result["structural_degeneracy"]["streamtube_bed_total_flow_ratio_is_identically_1"]
    assert s["gauss_hermite_max_abs_deviation_all_sigma"] > \
        s["gauss_hermite_max_abs_deviation_within_scope"]
    assert "quadrature" in s["quadrature_caveat"]
    big = [r for r in s["rows"] if r["sigma"] > S.SIGMA_EXACT_MAX]
    assert big, "the sigma grid must extend past the machine-precision scope"
    for r in big:
        # the explicitly renormalised construction stays exact at the SAME sigma, which is what
        # shows the deviation is the quadrature and not the mechanism
        assert abs(r["quantile_midpoint_mean_k"] - 1.0) < 1e-12


def test_swelling_carries_no_lateral_index(result):
    lat = result["structural_degeneracy"]["swelling_lateral_dispersion_is_identically_0"]
    assert lat["holds"] is True
    assert lat["lateral_parameters_found"] == []
    from puckworks.models.mo2023_2 import swelling as sw
    import inspect
    params = set(inspect.signature(sw.flow_decay).parameters)
    assert not (params & {"K", "n_tube", "tubes", "sigma", "hetero", "lateral", "radial"})


def test_the_card_itself_states_the_complementarity():
    card = (REPO / "docs/cards/mo2023_2.md").read_text(encoding="utf-8")
    assert "brewer2026.streamtube" in card
    assert "1-D homogeneity is silent on channeling" in card


# --------------------------------------------------------------------------------------------
# VALIDITY-RANGE ENFORCEMENT — THE d32 COINCIDENCE IS REFUSED, NOT USED
# --------------------------------------------------------------------------------------------
def test_validity_domains_do_not_intersect(result):
    g = result["grind_descriptor_check"]
    assert g["intersect"] is False
    assert g["common_descriptor"] is None
    assert "rule 9" in g["why"]
    assert result["compatibility_gate"]["checks"]["G5_validity_domains_intersect"]["passed"] \
        is False


def test_d32_coincidence_is_computed_and_then_refused(result):
    """The strongest available rescue is the one most likely to produce a false SURVIVE, so the
    screen must compute it, find it, and still refuse it on the granulometry behind it."""
    g = result["grind_descriptor_check"]
    assert g["d32_numerically_overlaps"] is True, "the coincidence must be real to be refused"
    inside = [p for p, v in g["mo_powder_d32_inside_streamtube_span"].items() if v]
    assert inside, "at least one powder must land inside, or the refusal is untested"
    for pw in inside:
        m = g["granulometry_behind_the_d32_coincidence"][pw]
        assert m["R_f_rel_diff"] > 0.10 and m["R_c_rel_diff"] > 0.10, (
            "the refusal rests on the granulometry differing; it does not here")
    a10 = [c for c in result["adversarial_checks"] if c["id"] == "A10"][0]
    assert a10["overturns"] is False
    assert "rescues nothing" in a10["result"]


def test_matched_scenario_was_never_constructed(result):
    assert result["matched_scenario"] is None
    assert "upstream" in result["matched_scenario_note"]


# --------------------------------------------------------------------------------------------
# UNCERTAINTY PROVENANCE
# --------------------------------------------------------------------------------------------
def test_no_uncertainty_is_borrowed_across_observables(result):
    u = result["uncertainty_authorities"]
    st = u["brewer2026_streamtube"]
    assert st["label_is_a_numerical_band"] is False
    assert st["admissible_for_this_comparison"] is False
    assert "EY" in st["observable"]
    assert u["mo2023_2_swelling"]["admissible_for_this_comparison"] is False
    # and nothing numeric was carried into the findings as a band
    findings = json.dumps(result["primary_numerical_findings"])
    assert "uncertainty" not in findings.lower()
    assert "NO between-model numerical difference" in result["primary_numerical_findings"]["note"]


def test_the_heldout_gate_is_named_as_the_only_numeric_authority(result):
    st = result["uncertainty_authorities"]["brewer2026_streamtube"]
    assert "gate_streamtube_heldout" in st["numerical_quantity"]
    from puckworks.validation import gates as G
    assert callable(G.gate_streamtube_heldout)


# --------------------------------------------------------------------------------------------
# DECISION MAPPING — exercised, not restated
# --------------------------------------------------------------------------------------------
def test_live_decision_is_retire_on_a_g1_to_g4_failure(result):
    assert result["decision"] == "RETIRE"
    assert result["decision_record"]["g1_to_g4_failures"], (
        "a RETIRE must rest on a G1-G4 failure, not on G5 alone")
    assert result["compatibility_gate"]["passed"] is False
    assert result["compatibility_gate"]["execution_permitted"] is False


def test_a_g5_only_failure_would_map_to_needs_new_data(result):
    """The ordering rule is a mapping, so test the mapping: if only the validity domains failed,
    the honest answer would be NEEDS_NEW_DATA. That branch must exist and be reachable."""
    fake = copy.deepcopy(result["compatibility_gate"])
    for key in list(fake["checks"]):
        fake["checks"][key]["passed"] = not key.startswith("G5")
    fake["passed"] = False
    fake["failed"] = [k for k, v in fake["checks"].items() if not v["passed"]]
    assert S.decide(fake)["decision"] == "NEEDS_NEW_DATA"


def test_a_passing_gate_refuses_to_produce_a_decision_here(result):
    fake = copy.deepcopy(result["compatibility_gate"])
    for key in fake["checks"]:
        fake["checks"][key]["passed"] = True
    fake["passed"] = True
    fake["failed"] = []
    with pytest.raises(AssertionError):
        S.decide(fake)


def test_decision_criteria_match_the_candidate_card_verbatim_terms():
    card = next(p for p in (REPO / "docs/insights/candidates").glob("I-072_*.md"))
    text = card.read_text(encoding="utf-8")
    for term in ("SURVIVE", "RETIRE", "NEEDS_NEW_DATA"):
        assert term in text
    assert "no shared observable definition exists" in text


def test_every_adversarial_check_ran_and_none_overturned(result):
    ids = [c["id"] for c in result["adversarial_checks"]]
    assert ids == ["A%d" % i for i in range(1, 13)]
    assert result["adversarial_checks_overturning"] == []
    for c in result["adversarial_checks"]:
        assert c["result"], "check %s produced no result" % c["id"]


# --------------------------------------------------------------------------------------------
# NOTHING WAS UPGRADED, AND NOTHING ADMINISTRATIVE WAS TOUCHED
# --------------------------------------------------------------------------------------------
def test_no_evidence_label_or_rung_is_changed(result):
    assert result["evidence_labels_unchanged"] is True
    assert result["administrative_exception_invoked"] is False
    assert result["registry_entries"][S.COMPONENT_A]["evidence_strength"] == \
        "source_curve_reproduction"
    assert result["registry_entries"][S.COMPONENT_B]["evidence_strength"] == \
        "within_campaign_held_out"


def test_registry_manifest_and_cards_are_unmodified_by_this_branch():
    base = S.BASE_COMMIT
    if _git("cat-file", "-e", base + "^{commit}").returncode != 0:
        pytest.skip("base commit not present in this checkout")
    for path in ("puckworks/models/__init__.py", "puckworks/data/MANIFEST.csv",
                 "docs/cards/mo2023_2.md", "puckworks/validation/gates.py"):
        r = _git("diff", "--numstat", base, "HEAD", "--", path)
        assert r.stdout.strip() == "", "%s was modified by this screen branch" % path


def test_claim_ceiling_is_present_and_refuses_the_agreement_reading(result):
    ceiling = result["claim_ceiling"]
    assert "does NOT establish that the two components agree" in ceiling
    assert "source_curve_reproduction" in ceiling and "within_campaign_held_out" in ceiling
    assert result["reopen_condition"]
    assert "RP-A" in result["reopen_condition"]


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


def test_a_threshold_crossing_structural_deviation_is_rejected(result):
    """I-072's decision rests on the deviation being < 1e-12. A mutation across that threshold
    must be rejected by the equivalence contract, not absorbed by the portability tolerance."""
    fresh = copy.deepcopy(result)
    path = ("structural_degeneracy.streamtube_bed_total_flow_ratio_is_identically_1"
            ".gauss_hermite_max_abs_deviation_within_scope")
    assert _at(result, path) < 1e-12
    _set(fresh, path, 1e-9)                                   # violates the frozen threshold
    _rejects(result, fresh)
    # and the scientific assertion that consumes it would fail too
    assert not (_at(fresh, path) < 1e-12)

"""Round-9 contracts: interval geometry, estimand direction, audit scope, and fail-closed rows.

Every test here corresponds to a defect that shipped. The round-8 remediation removed retyped
values and replaced them with generated sentences, which promptly produced *current numbers in
false claims*:

  * two intervals that both contain zero were described as lying "on the same side of zero",
    because the generator compared two `contains_zero` booleans for equality;
  * an interval with a ``+0.0038 pp`` upper bound was said to "reach zero at its upper bound";
  * the "largest advantage" was attributed to an upper bound, though negative model-minus-comparator
    values favour the model and the *lower* bound is the favourable extreme;
  * one target's Monte Carlo standard error was printed as though it described every endpoint;
  * the endpoint contract returned a clean bill of health when the result rows were deleted;
  * a resampling partition with two observations swapped between clusters validated cleanly.

These are parameterised over the geometries that actually occur, so a renderer cannot be correct at
40 g and false at 38 g.
"""
from __future__ import annotations

import copy
import dataclasses
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from puckworks.paper_a import source_resampling_oracle as ORACLE  # noqa: E402
from puckworks.paper_a import transfer_contract as TC  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402

ENDPOINT_JSON = REPO / "docs" / "paper1_resource" / "PAPER_A_ENDPOINT_PROPAGATION.json"


def _endpoint():
    return json.loads(ENDPOINT_JSON.read_text())


# ── 1. trinary zero relation, from full precision ───────────────────────────────────────────
@pytest.mark.parametrize("lower,upper,expect", [
    (-0.884, -0.042, TS.ZeroRelation.BELOW),        # 38 g primary
    (-0.829, +0.0038, TS.ZeroRelation.CONTAINS),    # 40 g primary
    (-0.891, +0.0058, TS.ZeroRelation.CONTAINS),    # 42 g primary
    (+0.0004, +0.825, TS.ZeroRelation.ABOVE),
    (-0.5, 0.0, TS.ZeroRelation.CONTAINS),          # closed-interval convention
    (0.0, +0.5, TS.ZeroRelation.CONTAINS),
])
def test_zero_relation_is_trinary_and_full_precision(lower, upper, expect):
    assert TS.interval_semantics(lower, upper).relation is expect


def test_a_boolean_cannot_distinguish_the_two_excluding_sides():
    """The exact type error behind P0-1: `not contains_zero` loses the side."""
    below = TS.interval_semantics(-0.8, -0.1)
    above = TS.interval_semantics(+0.1, +0.8)
    assert below.relation.excludes_zero and above.relation.excludes_zero
    assert below.relation is not above.relation
    # A renderer keyed on containment-equality would call these "the same side of zero".
    assert TS.describe_shared_relation([below, above]) != \
        TS.describe_shared_relation([below, below])


@pytest.mark.parametrize("a,b,expect_fragment", [
    ((-0.829, +0.0038), (-0.826, +0.0043), "both contain zero"),
    ((-0.884, -0.042), (-0.880, -0.030), "both exclude zero on the negative side"),
    ((+0.042, +0.884), (+0.030, +0.880), "both exclude zero on the positive side"),
])
def test_shared_relation_names_the_relation(a, b, expect_fragment):
    sem = [TS.interval_semantics(*a), TS.interval_semantics(*b)]
    assert TS.describe_shared_relation(sem) == expect_fragment


def test_mixed_relations_are_described_separately_not_collapsed():
    sem = [TS.interval_semantics(-0.884, -0.042), TS.interval_semantics(-0.829, +0.0038)]
    text = TS.describe_shared_relation(sem)
    assert "excludes zero on the negative side" in text and "contains zero" in text


def test_exact_contact_is_recorded_separately_from_containment():
    """"reaches zero at its upper bound" must be false when the bound is beyond zero."""
    touching = TS.interval_semantics(-0.829, 0.0)
    beyond = TS.interval_semantics(-0.829, +0.0038)
    assert touching.relation is beyond.relation is TS.ZeroRelation.CONTAINS
    assert touching.touches_zero_at_upper is True
    assert beyond.touches_zero_at_upper is False, (
        "an interval whose upper bound lies beyond zero does not reach zero AT that bound")


def test_reversed_bounds_are_rejected():
    with pytest.raises(ValueError):
        TS.interval_semantics(+0.1, -0.1)


# ── 1b. what is NOT an interval bound (round-10 P1-3) ───────────────────────────────────────
@pytest.mark.parametrize("lower,upper", [
    (True, 1.0),                     # bool is an int subclass: `float(True)` is 1.0
    (False, 1.0),
    (-0.5, True),
    ("-0.5", 0.1),                   # a JSON string that was never parsed
    (-0.5, "0.1"),
    (None, 0.1),
    (-0.5, None),
    ([0.0], 0.1),
    ({"lower": -0.5}, 0.1),
    (float("nan"), 0.1),
    (-0.5, float("nan")),
    (float("-inf"), 0.1),
    (-0.5, float("inf")),
])
def test_non_numeric_and_non_finite_bounds_are_rejected_before_classification(lower, upper):
    """`interval_semantics(True, 1.0)` used to return a cheerful ABOVE-zero interval.

    Every input here is an upstream defect — a boolean where a bound belongs, an unparsed JSON
    string, an overflowed division. Classifying it turns that defect into a plausible sentence about
    where a bound sits relative to zero.
    """
    with pytest.raises(ValueError, match="finite"):
        TS.interval_semantics(lower, upper)


@pytest.mark.parametrize("value", [True, False, "0.1", None, [], float("nan"), float("inf")])
def test_require_finite_number_names_the_field_it_rejected(value):
    with pytest.raises(ValueError, match="my bound"):
        TS.require_finite_number(value, "my bound")


@pytest.mark.parametrize("lower,upper", [(-0.5, 0.1), (-1, 2), (0.0, 0.0), (-0.0, 0.0)])
def test_ordinary_finite_bounds_including_negative_zero_are_accepted(lower, upper):
    sem = TS.interval_semantics(lower, upper)
    assert sem.relation is TS.ZeroRelation.CONTAINS


# ── 2. estimand direction and favourability ─────────────────────────────────────────────────
#
# Round-10 P1-2 replaced the stored `EstimandDirection.negative_favours_model` boolean with a
# derivation from primitives. Everything below therefore asserts the DERIVATION, not a recorded
# answer: the point is that no one can write the answer down and have it disagree with the metric
# and the subtraction order.

ESTIMAND = TS.POOLED_MAPE_ESTIMAND


def test_negative_favours_the_model_for_a_loss_difference():
    assert ESTIMAND.metric_preference is TS.MetricPreference.LOWER_IS_BETTER
    assert ESTIMAND.operation is TS.ContrastOperation.LEFT_MINUS_RIGHT
    assert ESTIMAND.negative_favours == TS.MODEL_OPERAND
    assert ESTIMAND.negative_favours_model is True
    assert "minus" in ESTIMAND.contrast_label


@pytest.mark.parametrize("preference,operation,expect_model", [
    (TS.MetricPreference.LOWER_IS_BETTER, TS.ContrastOperation.LEFT_MINUS_RIGHT, True),
    (TS.MetricPreference.LOWER_IS_BETTER, TS.ContrastOperation.RIGHT_MINUS_LEFT, False),
    (TS.MetricPreference.HIGHER_IS_BETTER, TS.ContrastOperation.LEFT_MINUS_RIGHT, False),
    (TS.MetricPreference.HIGHER_IS_BETTER, TS.ContrastOperation.RIGHT_MINUS_LEFT, True),
])
def test_direction_is_derived_from_metric_preference_and_operand_order(preference, operation,
                                                                      expect_model):
    """All four combinations, because only a derivation gets all four right for free."""
    spec = dataclasses.replace(ESTIMAND, metric_preference=preference, operation=operation)
    assert spec.negative_favours_model is expect_model
    assert (spec.negative_favours == TS.MODEL_OPERAND) is expect_model
    assert spec.positive_favours != spec.negative_favours


def test_reversing_the_operation_reverses_the_prose_and_the_table_label():
    """The P1-2 requirement: a reversed contrast cannot leave the rendered sentence unchanged."""
    reversed_spec = dataclasses.replace(ESTIMAND, operation=TS.ContrastOperation.RIGHT_MINUS_LEFT)
    assert reversed_spec.prose != ESTIMAND.prose
    assert reversed_spec.short_contrast_label != ESTIMAND.short_contrast_label
    assert "favour the mechanistic model" in ESTIMAND.prose
    assert "favour the O-trained level-only comparator" in reversed_spec.prose


def test_most_favourable_bound_is_the_lowest_lower_not_any_upper():
    """P0-1: the supplement attributed the "largest advantage" to an upper bound."""
    sem = [TS.interval_semantics(-0.884, -0.042),
           TS.interval_semantics(-0.829, +0.0038),
           TS.interval_semantics(-0.891, +0.0058)]
    best, worst = TS.favourable_extremes(sem, ESTIMAND)
    assert best == pytest.approx(-0.891)      # most favourable: smallest lower bound
    assert worst == pytest.approx(+0.0058)    # least favourable: largest upper bound
    assert best < worst


def test_favourability_flips_with_the_declared_direction():
    sem = [TS.interval_semantics(-0.5, +0.2)]
    positive_good = dataclasses.replace(ESTIMAND,
                                        metric_preference=TS.MetricPreference.HIGHER_IS_BETTER)
    assert TS.favourable_extremes(sem, ESTIMAND) == (-0.5, +0.2)
    assert TS.favourable_extremes(sem, positive_good) == (+0.2, -0.5)


@pytest.mark.parametrize("call", [
    lambda: TS.favourable_extremes([TS.interval_semantics(-0.5, +0.2)]),
    lambda: TS.permits_no_advantage(TS.interval_semantics(-0.5, +0.2)),
])
def test_favourability_helpers_have_no_default_direction(call):
    """A publication renderer must not be able to omit the estimand and get an assumed one."""
    with pytest.raises(TypeError):
        call()


@pytest.mark.parametrize("bad", [None, {}, "model minus comparator", 1.0,
                                 TS.POOLED_MAPE_ESTIMAND.as_dict()])
def test_favourability_helpers_reject_anything_but_a_validated_spec(bad):
    """Including the SERIALISED estimand: a renderer must rebuild it through the validator."""
    with pytest.raises(TypeError):
        TS.favourable_extremes([TS.interval_semantics(-0.5, +0.2)], bad)


def test_the_defaulted_direction_constant_is_gone():
    """The round-9 API is removed, not deprecated: a default here is the P1-2 defect."""
    for retired in ("PAIRED_LOSS_DIFFERENCE", "EstimandDirection"):
        assert not hasattr(TS, retired), (
            "%r still exists; a module-level default direction is exactly what let a reversed "
            "artefact estimand leave every favourability sentence unchanged" % retired)


@pytest.mark.parametrize("upper,concedes", [(-0.042, False), (0.0, True), (+0.0038, True)])
def test_permits_no_advantage_tracks_the_unfavourable_end(upper, concedes):
    assert TS.permits_no_advantage(TS.interval_semantics(-0.8, upper), ESTIMAND) is concedes


def test_estimand_serialisation_round_trips_and_rederives_its_own_direction():
    payload = ESTIMAND.as_dict()
    assert TS.estimand_from_dict(payload) == ESTIMAND
    assert payload["negative_values_favour"] == TS.MODEL_OPERAND


@pytest.mark.parametrize("mutate,expect", [
    (lambda d: d.__setitem__("operation", "left_minus_middle"), "not one of"),
    (lambda d: d.__setitem__("metric_preference", "whatever"), "not one of"),
    (lambda d: d.pop("left_operand"), "missing required field"),
    (lambda d: d.__setitem__("right_operand", d["left_operand"]), "operand with itself"),
])
def test_a_malformed_estimand_is_rejected_not_defaulted(mutate, expect):
    payload = ESTIMAND.as_dict()
    mutate(payload)
    with pytest.raises(ValueError, match=expect):
        TS.estimand_from_dict(payload)


# ── 2b. what the analysis may DECIDE (round-10 P0-1) ────────────────────────────────────────
def test_the_declared_status_supports_no_decision_at_all():
    st = TS.TRANSFER_INFERENTIAL_STATUS
    assert st.coverage_calibrated is False
    assert st.practical_margin_pp is None
    assert not any(st.decision_flags.values())
    assert st.permitted_claim_class is TS.ClaimClass.DESCRIPTIVE_EVIDENCE_LIMITED
    assert TS.validate_inferential_status(st) == []


@pytest.mark.parametrize("field", ["supports_superiority_decision",
                                   "supports_noninferiority_decision",
                                   "supports_equivalence_decision",
                                   "supports_absence_of_skill_decision"])
def test_an_uncalibrated_status_cannot_grant_itself_a_decision(field):
    """Absence of skill is a DECISION. An uncalibrated range cannot make it either way."""
    st = dataclasses.replace(TS.TRANSFER_INFERENTIAL_STATUS, **{field: True})
    problems = TS.validate_inferential_status(st)
    assert problems, "FALSE GREEN: %s granted without calibrated coverage" % field
    assert any("decides nothing" in p for p in problems)


def test_claiming_calibrated_coverage_needs_a_procedure_and_a_level():
    st = dataclasses.replace(TS.TRANSFER_INFERENTIAL_STATUS, coverage_calibrated=True)
    problems = TS.validate_inferential_status(st)
    assert any("no confidence_procedure is named" in p for p in problems)
    assert any("confidence_level" in p for p in problems)
    assert any("fixed-predictor sensitivity analysis" in p for p in problems)


def test_an_equivalence_decision_needs_a_predeclared_margin():
    st = dataclasses.replace(
        TS.TRANSFER_INFERENTIAL_STATUS, coverage_calibrated=True, confidence_level=0.95,
        confidence_procedure="cluster bootstrap TOST",
        analysis_kind=TS.AnalysisKind.CALIBRATED_CLUSTERED_CONFIDENCE,
        supports_equivalence_decision=True,
        permitted_claim_class=TS.ClaimClass.CALIBRATED_DECISION)
    assert any("predeclared practical margin" in p for p in TS.validate_inferential_status(st))
    with_margin = dataclasses.replace(st, practical_margin_pp=0.5)
    assert TS.validate_inferential_status(with_margin) == []


def test_an_unused_margin_is_rejected():
    """A margin nobody decides with is an invitation to a post hoc negligibility claim."""
    st = dataclasses.replace(TS.TRANSFER_INFERENTIAL_STATUS, practical_margin_pp=0.5)
    assert any("no decision uses it" in p for p in TS.validate_inferential_status(st))


@pytest.mark.parametrize("mutate,expect", [
    (lambda d: d.__setitem__("analysis_kind", "vibes"), "not one of"),
    (lambda d: d.__setitem__("permitted_claim_class", "strong"), "not one of"),
    (lambda d: d.__setitem__("coverage_calibrated", "false"), "must be a JSON boolean"),
    (lambda d: d.__setitem__("practical_margin_pp", "0.5"), "must be null or a number"),
    (lambda d: d.pop("supports_equivalence_decision"), "missing required field"),
])
def test_a_malformed_status_is_rejected(mutate, expect):
    payload = TS.TRANSFER_INFERENTIAL_STATUS.as_dict()
    mutate(payload)
    with pytest.raises(ValueError, match=expect):
        TS.status_from_dict(payload)


# ── 3. Monte Carlo audit scope (P1-1) ───────────────────────────────────────────────────────
def test_the_declared_audit_target_is_exactly_one_endpoint_scheme_and_loss():
    k = TS.AUDITED_TARGET
    assert (k.endpoint_g, k.scheme, k.fitting_loss) == (40.0, "cond_in_variety", "primary")


def test_audit_lookup_requires_an_exact_target():
    art = {"stability_audits": [{"target": TS.AUDITED_TARGET.as_dict(), "n_runs": 20}]}
    assert TS.find_exact_audit(art, TS.AUDITED_TARGET)["n_runs"] == 20
    for wrong in (TS.AuditKey(38.0, "cond_in_variety", "primary"),
                  TS.AuditKey(40.0, "group", "primary"),
                  TS.AuditKey(40.0, "cond_in_variety", "alternative")):
        with pytest.raises(KeyError, match="no archived Monte Carlo audit"):
            TS.find_exact_audit(art, wrong)


def test_audit_lookup_never_falls_back_to_a_top_level_scalar():
    """The round-8 shape must not satisfy a keyed lookup."""
    legacy = {"stability_audit": {"upper_monte_carlo_se_at_canonical_B_pp": 0.0005}}
    with pytest.raises(KeyError, match="stability_audits"):
        TS.find_exact_audit(legacy, TS.AUDITED_TARGET)


def test_ambiguous_audit_keys_are_rejected():
    dup = {"stability_audits": [{"target": TS.AUDITED_TARGET.as_dict()},
                                {"target": TS.AUDITED_TARGET.as_dict()}]}
    with pytest.raises(KeyError, match="not unique"):
        TS.find_exact_audit(dup, TS.AUDITED_TARGET)


def test_the_committed_artifact_carries_the_declared_audit():
    assert TS.has_exact_audit(_endpoint(), TS.AUDITED_TARGET)


def test_no_audit_is_archived_for_the_unaudited_targets():
    """Guards against quietly inventing precision for targets that were never audited."""
    ep = _endpoint()
    for wrong in (TS.AuditKey(38.0, "cond_in_variety", "primary"),
                  TS.AuditKey(42.0, "cond_in_variety", "primary"),
                  TS.AuditKey(40.0, "sample_in_variety_grind", "primary")):
        assert not TS.has_exact_audit(ep, wrong)


# ── 4. endpoint rows fail closed (P1-2) ─────────────────────────────────────────────────────
def _valid_endpoint_artifact():
    return {"endpoint": TC.endpoint_object(),
            "rows": [{"m_target_g": v} for v in TC.ENDPOINT_TARGETS]}


@pytest.mark.parametrize("name,mutate", [
    ("rows_deleted", lambda a: a.pop("rows")),
    ("rows_empty", lambda a: a.__setitem__("rows", [])),
    ("rows_not_a_list", lambda a: a.__setitem__("rows", {})),
    ("all_row_keys_deleted", lambda a: [r.pop("m_target_g") for r in a["rows"]]),
    ("first_row_key_deleted", lambda a: a["rows"][0].pop("m_target_g")),
    ("middle_row_key_deleted", lambda a: a["rows"][1].pop("m_target_g")),
    ("last_row_key_deleted", lambda a: a["rows"][2].pop("m_target_g")),
    ("one_row_missing", lambda a: a["rows"].pop()),
    ("duplicate_row", lambda a: a["rows"].append(dict(a["rows"][0]))),
    ("extra_target", lambda a: a["rows"].append({"m_target_g": 44.0})),
    ("row_not_a_mapping", lambda a: a["rows"].__setitem__(1, "nope")),
    ("non_finite_target", lambda a: a["rows"][1].__setitem__("m_target_g", float("nan"))),
    ("non_numeric_target", lambda a: a["rows"][1].__setitem__("m_target_g", "forty")),
    ("retired_key_in_last_row", lambda a: a["rows"][2].__setitem__("v_target_ml", 42.0)),
])
def test_endpoint_row_mutations_all_fail(name, mutate):
    art = _valid_endpoint_artifact()
    mutate(art)
    assert TC.validate_endpoint_contract(art), f"{name} produced a FALSE GREEN"


def test_a_well_formed_endpoint_artifact_passes():
    assert TC.validate_endpoint_contract(_valid_endpoint_artifact()) == []


def test_rows_are_optional_only_where_they_are_not_endpoint_indexed():
    """The comparator-loss artefact keys its rows by fitting loss, at one endpoint."""
    art = {"endpoint": TC.endpoint_object(), "rows": [{"fitting_loss": "primary"}]}
    assert TC.validate_endpoint_contract(art, require_rows=False) == []
    assert TC.validate_endpoint_contract(art, require_rows=True)


# ── 5. resampling membership is source-bound (P1-3) ─────────────────────────────────────────
def test_the_oracle_reproduces_the_documented_census_from_the_csv_alone():
    exp = ORACLE.expected_design()
    for name, census in ORACLE.EXPECTED_CENSUS.items():
        assert exp[name]["n_clusters"] == census["n_clusters"], name
        assert exp[name]["cluster_size_distribution"] == census["sizes"], name
        assert exp[name]["n_strata"] == census["n_strata"], name
        assert exp[name]["n_observations"] == 132, name


def test_the_oracle_shares_no_grouping_code_with_production():
    """If the oracle called the production grouper, a shared bug could certify itself.

    Checked on the parsed AST rather than the raw text: the module docstring names the forbidden
    functions in order to explain why it avoids them, and a substring scan cannot tell an
    explanation from a call.
    """
    import ast

    tree = ast.parse((REPO / "puckworks" / "paper_a"
                      / "source_resampling_oracle.py").read_text())

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
            imported.update("%s.%s" % (node.module or "", a.name) for a in node.names)
    assert not any("transfer_contract" in m for m in imported), (
        "the oracle must not import the production contract module: %r" % sorted(imported))

    called = {n.func.id for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    called |= {n.func.attr for n in ast.walk(tree)
               if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    for forbidden in ("cluster_key_of", "stratum_key_of", "cluster_membership",
                      "scheme_design", "resampling_design"):
        assert forbidden not in called, f"the oracle must not call production {forbidden!r}"


def test_the_committed_design_matches_the_source_partition_exactly():
    assert ORACLE.compare_design(_endpoint()["resampling_design"]) == []


def _refresh_hash(design, scheme):
    design["schemes"][scheme]["membership_sha256"] = \
        TC.sha256_of(design["schemes"][scheme]["membership"])


@pytest.mark.parametrize("scheme,mutate_desc", [
    ("sample_in_variety_grind", "swap one solute between two sample records"),
    ("cond_in_variety", "move one observation to the wrong condition cluster"),
])
def test_count_preserving_membership_swaps_are_caught(scheme, mutate_desc):
    """Both of these passed every round-8 check with a refreshed self-hash."""
    design = copy.deepcopy(_endpoint()["resampling_design"])
    mem = design["schemes"][scheme]["membership"]
    a, b = mem[0], mem[1]
    a_obs, b_obs = sorted(a["observation_ids"]), sorted(b["observation_ids"])
    a["observation_ids"] = a_obs[:-1] + [b_obs[-1]]
    b["observation_ids"] = b_obs[:-1] + [a_obs[-1]]
    _refresh_hash(design, scheme)

    # The mutation is invisible to counts, sizes and the self-hash …
    assert TC.validate_resampling_design(design, 132) == [], (
        "this test is only meaningful while the internal validator still misses the swap")
    # … and caught by the independent source oracle.
    problems = ORACLE.compare_design(design)
    assert problems, f"FALSE GREEN: {mutate_desc}"
    assert any(scheme in p and "membership differs from the source" in p for p in problems)


def test_a_dropped_cluster_is_caught():
    design = copy.deepcopy(_endpoint()["resampling_design"])
    design["schemes"]["group"]["membership"].pop()
    _refresh_hash(design, "group")
    assert any("missing cluster" in p or "clusters" in p
               for p in ORACLE.compare_design(design))


def test_a_renamed_cluster_is_caught():
    design = copy.deepcopy(_endpoint()["resampling_design"])
    design["schemes"]["cond_in_variety"]["membership"][0]["cluster_id"] = "Arabica|999|999"
    _refresh_hash(design, "cond_in_variety")
    problems = ORACLE.compare_design(design)
    assert any("undeclared cluster" in p for p in problems)


def test_a_wrong_stratum_is_caught():
    design = copy.deepcopy(_endpoint()["resampling_design"])
    design["schemes"]["sample_in_variety_grind"]["membership"][0]["stratum"] = "Robusta|F"
    _refresh_hash(design, "sample_in_variety_grind")
    assert any("stratum" in p for p in ORACLE.compare_design(design))


def test_wrong_archived_grinds_are_caught_even_with_a_refreshed_hash():
    """Round-10 P1-2's twelfth reproduced false green.

    A cluster's grind composition is what the Methods census and Table S6 report ("18 contain both a
    coarse and a fine sample record"). The round-9 oracle compared observation ids, strata and sample
    ids and stopped, so this passed with the self-hash refreshed.
    """
    design = copy.deepcopy(_endpoint()["resampling_design"])
    cluster = next(c for c in design["schemes"]["cond_in_variety"]["membership"]
                   if c["grinds"] == ["C"])
    cluster["grinds"] = ["C", "F"]
    _refresh_hash(design, "cond_in_variety")
    problems = ORACLE.compare_design(design)
    assert problems, "FALSE GREEN: wrong archived grinds"
    assert any("grinds are" in p for p in problems)


def test_a_declared_census_that_contradicts_the_source_is_caught():
    """`n_strata` and the size distribution are published; the oracle must own them too."""
    for field, wrong in (("n_strata", 99), ("n_clusters", 99),
                         ("cluster_size_distribution", {"3": 26})):
        design = copy.deepcopy(_endpoint()["resampling_design"])
        design["schemes"]["cond_in_variety"][field] = wrong
        problems = ORACLE.compare_design(design)
        assert problems, "FALSE GREEN: artefact declares %s=%r" % (field, wrong)


# ── 6. the DECLARED design, pinned against the contract (round-10 P1-2) ─────────────────────
#
# The twelve mutations below all keep the observation membership exactly as the source implies, so
# the source oracle is silent by design — nothing about the DATA changed. They change what the
# artefact SAYS, which is what the Methods paragraph, Table 5 and Supplementary Table S6 are
# generated from. Every one of them returned an empty problem list before this remediation.

def _committed_design():
    return copy.deepcopy(_endpoint()["resampling_design"])


@pytest.mark.parametrize("name,mutate,expect", [
    ("estimand_reversed",
     lambda d: d["estimand"].__setitem__("operation", "right_minus_left"),
     "estimand.operation"),
    ("estimand_derived_direction_flipped",
     lambda d: d["estimand"].__setitem__("negative_values_favour",
                                         "o_trained_level_only_comparator"),
     "its own primitives imply"),
    ("estimand_prose_rewritten",
     lambda d: d["estimand"].__setitem__("prose", "negative values favour the comparator"),
     "its own primitives imply"),
    ("estimand_unknown_operation",
     lambda d: d["estimand"].__setitem__("operation", "left_over_right"),
     "not one of"),
    ("interval_kind_calibrated_CI",
     lambda d: d.__setitem__("interval_kind", "calibrated 95% confidence interval"),
     "interval_kind"),
    ("nested_schema_version_999",
     lambda d: d.__setitem__("schema_version", 999),
     "schema_version"),
    ("scheme_order_reversed",
     lambda d: d.__setitem__("scheme_order", list(reversed(d["scheme_order"]))),
     "scheme_order"),
    ("scheme_role_wrong",
     lambda d: d["schemes"]["group"].__setitem__("role", "primary_conservative_sensitivity"),
     "declares role"),
    ("scheme_label_wrong",
     lambda d: d["schemes"]["group"].__setitem__("label", "whole variety group"),
     "declares label"),
    ("scheme_strata_wrong",
     lambda d: d["schemes"]["cond_in_variety"].__setitem__("strata", ["variety", "solute"]),
     "declares strata"),
    ("scheme_cluster_key_wrong",
     lambda d: d["schemes"]["cond_in_variety"].__setitem__("cluster_key", ["sample_id"]),
     "declares cluster_key"),
    ("scheme_rationale_wrong",
     lambda d: d["schemes"]["group"].__setitem__("rationale", "the most informative construction"),
     "declares rationale"),
    ("scheme_n_strata_wrong",
     lambda d: d["schemes"]["cond_in_variety"].__setitem__("n_strata", 7),
     "n_strata"),
    ("scheme_n_clusters_wrong",
     lambda d: d["schemes"]["cond_in_variety"].__setitem__("n_clusters", 27),
     "n_clusters"),
    ("scheme_size_distribution_wrong",
     lambda d: d["schemes"]["cond_in_variety"].__setitem__("cluster_size_distribution",
                                                           {"3": 9, "6": 17}),
     "cluster_size_distribution"),
    ("predictors_refit_true",
     lambda d: d.__setitem__("predictors_refit_inside_resampling", True),
     "predictors_refit_inside_resampling"),
    ("predictors_refit_truthy_string",
     lambda d: d.__setitem__("predictors_refit_inside_resampling", "false"),
     "predictors_refit_inside_resampling"),
    ("primary_scheme_changed",
     lambda d: d.__setitem__("primary_scheme", "group"),
     "primary_scheme"),
    ("status_grants_absence_of_skill",
     lambda d: d["inferential_status"].__setitem__("supports_absence_of_skill_decision", True),
     "inferential_status"),
    ("status_claims_calibrated_coverage",
     lambda d: d["inferential_status"].__setitem__("coverage_calibrated", True),
     "inferential_status"),
    ("status_invents_a_margin",
     lambda d: d["inferential_status"].__setitem__("practical_margin_pp", 0.5),
     "inferential_status"),
    ("status_deleted",
     lambda d: d.pop("inferential_status"),
     "inferential_status"),
    ("estimand_support_rewritten",
     lambda d: d.__setitem__("estimand_support", "mean over the matched on-grid subset"),
     "estimand_support"),
    ("unknown_extra_scheme",
     lambda d: d["schemes"].__setitem__("cond_in_solute", dict(d["schemes"]["group"])),
     "undeclared scheme"),
    ("required_scheme_removed",
     lambda d: d["schemes"].pop("cond_in_group"),
     "omits scheme"),
    ("unexpected_top_level_field",
     lambda d: d.__setitem__("coverage", "95%"),
     "unexpected field"),
    ("unexpected_scheme_field",
     lambda d: d["schemes"]["group"].__setitem__("p_value", 0.04),
     "unexpected field"),
    ("cluster_n_observations_wrong",
     lambda d: d["schemes"]["group"]["membership"][0].__setitem__("n_observations", 99),
     "n_observations"),
])
def test_declared_design_mutations_all_fail(name, mutate, expect):
    design = _committed_design()
    mutate(design)
    problems = TC.validate_resampling_design(design, 132)
    assert problems, "FALSE GREEN: %s" % name
    assert any(expect in p for p in problems), (name, expect, problems)


def test_the_committed_declared_design_passes():
    assert TC.validate_resampling_design(_committed_design(), 132) == []


# ── 7. the renderer takes its direction FROM the artefact (round-10 P1-2) ────────────────────
def _artefacts():
    from tools import paper_a_transfer_text as TT

    return (json.loads(TT.ENDPOINT_JSON.read_text(encoding="utf-8")),
            json.loads(TT.CORPUS_JSON.read_text(encoding="utf-8")),
            json.loads(TT.LOSS_JSON.read_text(encoding="utf-8")))


def _reverse_the_estimand(ep):
    """Reverse the contrast in the artefact, re-deriving what the primitives now imply."""
    design = ep["resampling_design"]
    spec = dataclasses.replace(TS.estimand_from_dict(design["estimand"]),
                              operation=TS.ContrastOperation.RIGHT_MINUS_LEFT)
    design["estimand"] = spec.as_dict()
    return ep


@pytest.mark.parametrize("block", ["block_endpoint_reading", "block_transfer_results",
                                   "block_endpoint_table", "block_table5",
                                   "block_supplement_endpoint_table"])
def test_reversing_the_artefact_estimand_changes_every_favourability_block(block):
    """The exact P1-2 failure mode: correct numbers rendered with inverted scientific meaning.

    Before this remediation the renderer imported its sign convention from a module-level default and
    hard-coded the sentence beside it, so this mutation changed nothing at all in the output.
    """
    from tools import paper_a_transfer_text as TT

    ep, corpus, loss = _artefacts()
    render = getattr(TT, block)
    before = render(copy.deepcopy(ep), corpus, loss)
    after = render(_reverse_the_estimand(copy.deepcopy(ep)), corpus, loss)
    assert after != before, (
        "%s renders identically after the estimand is reversed, so its favourability statements do "
        "not come from the artefact" % block)


def test_rewriting_only_the_estimand_prose_fails_validation_instead():
    """The other half of the requirement: hand-edited prose must not silently win, either."""
    design = _committed_design()
    design["estimand"]["prose"] = ("pooled MAPE for the comparator minus pooled MAPE for the "
                                   "model; positive values favour the mechanistic model")
    problems = TC.validate_resampling_design(design, 132)
    assert any("its own primitives imply" in p for p in problems)


def test_the_renderer_refuses_an_artefact_with_no_declared_estimand():
    from tools import paper_a_transfer_text as TT

    ep, _corpus, _loss = _artefacts()
    ep["resampling_design"].pop("estimand")
    with pytest.raises(ValueError, match="estimand"):
        TT.validated_analysis(ep)
    ep.pop("resampling_design")
    with pytest.raises(KeyError, match="refusing to assume"):
        TT.validated_analysis(ep)


def test_the_renderer_refuses_an_incoherent_inferential_status():
    from tools import paper_a_transfer_text as TT

    ep, _corpus, _loss = _artefacts()
    ep["resampling_design"]["inferential_status"]["supports_absence_of_skill_decision"] = True
    with pytest.raises(ValueError, match="not internally consistent"):
        TT.validated_analysis(ep)

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


# ── 2. estimand direction and favourability ─────────────────────────────────────────────────
def test_negative_favours_the_model_for_a_loss_difference():
    assert TS.PAIRED_LOSS_DIFFERENCE.negative_favours_model is True
    assert "minus" in TS.PAIRED_LOSS_DIFFERENCE.label


def test_most_favourable_bound_is_the_lowest_lower_not_any_upper():
    """P0-1: the supplement attributed the "largest advantage" to an upper bound."""
    sem = [TS.interval_semantics(-0.884, -0.042),
           TS.interval_semantics(-0.829, +0.0038),
           TS.interval_semantics(-0.891, +0.0058)]
    best, worst = TS.favourable_extremes(sem)
    assert best == pytest.approx(-0.891)      # most favourable: smallest lower bound
    assert worst == pytest.approx(+0.0058)    # least favourable: largest upper bound
    assert best < worst


def test_favourability_flips_with_the_declared_direction():
    sem = [TS.interval_semantics(-0.5, +0.2)]
    positive_good = TS.EstimandDirection(label="skill score", negative_favours_model=False)
    assert TS.favourable_extremes(sem) == (-0.5, +0.2)
    assert TS.favourable_extremes(sem, positive_good) == (+0.2, -0.5)


@pytest.mark.parametrize("upper,concedes", [(-0.042, False), (0.0, True), (+0.0038, True)])
def test_permits_no_advantage_tracks_the_unfavourable_end(upper, concedes):
    assert TS.permits_no_advantage(TS.interval_semantics(-0.8, upper)) is concedes


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

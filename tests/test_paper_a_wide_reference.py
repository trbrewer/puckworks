"""Synthetic architecture tests for the WIDE-referenced P0-G8 contract.

Authorization §7.4: no campaign data may be used. Every objective here is a closed-form function of
the multiplier, chosen so that the *right answer is known before the procedure runs* — an interior
minimum, a minimum at each boundary, exact and near ties, several accepted components, a tangency,
and a profile the frozen grids genuinely cannot resolve. Tests that check the classification, the
near-zero branch and the programme rule are pure interval arithmetic and need no objective at all.

These tests exercise pure functions. They construct no P0-G8 result archive and read no campaign
`y`, so running them is not the scientific gate.
"""
from __future__ import annotations

import math
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from puckworks.paper_a import wide_reference as WR   # noqa: E402


# ── synthetic objectives, in u = log kappa ───────────────────────────────────────────────────
U_LO, U_HI = math.log(WR.D_WIDE[0]), math.log(WR.D_WIDE[1])


def _interior(kappa):
    """Single interior minimum: J = 1 at kappa = e."""
    return 1.0 + (math.log(kappa) - 1.0) ** 2


def _lower_boundary(kappa):
    """Monotone increasing: the minimum sits exactly on kappa = 0.15."""
    return 1.0 + (math.log(kappa) - U_LO) ** 2


def _upper_boundary(kappa):
    """Monotone decreasing: the minimum sits exactly on kappa = 500."""
    return 1.0 + (math.log(kappa) - U_HI) ** 2


def _two_wells(kappa):
    """Exact tie: J = 1 at u = 0 and u = 4, with a hump of 1.16 between them."""
    u = math.log(kappa)
    return 1.0 + 0.01 * (u ** 2) * ((u - 4.0) ** 2)


def _two_wells_near_tied(kappa):
    """The same pair tilted by 1e-5 per unit u — a near tie, well inside the retention band."""
    u = math.log(kappa)
    return 1.0 + 0.01 * (u ** 2) * ((u - 4.0) ** 2) + 1e-5 * u


def _unresolvable(kappa):
    """A profile the frozen grids cannot resolve: ~900 exactly tied minima in the domain.

    The oscillation period is 0.0090 in log kappa and the finest grid spacing is 0.0254, so every
    grid aliases it. The correct outcome is `unresolved` — reporting one minimiser here would be
    the procedure inventing a result the sampling cannot support.
    """
    return 1.0 + 0.05 * math.sin(700.0 * math.log(kappa))


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 1. Finite WIDE minimisation
# ═════════════════════════════════════════════════════════════════════════════════════════════


def test_an_interior_minimum_is_found_and_the_coarse_grid_minimum_is_not_the_result():
    """The 40-point grid minimum is a diagnostic. It is never `J_ref`."""
    r = WR.reference_minimum(_interior)
    assert r.status == "resolved", r.reasons
    assert r.candidate == pytest.approx(1.0, abs=1e-9)
    assert r.minimisers == pytest.approx([math.e], rel=1e-6)

    coarse = r.coarse_grid_minimum
    assert coarse > r.candidate, (
        "the coarse grid cannot land on the true minimiser here, so a procedure that reported the "
        "grid minimum would report %.9f instead of %.9f" % (coarse, r.candidate))
    assert [rec.size for rec in r.refinements] == list(WR.GRID_SIZES)


def test_a_minimum_on_the_lower_boundary_is_found():
    r = WR.reference_minimum(_lower_boundary)
    assert r.status == "resolved", r.reasons
    assert r.candidate == pytest.approx(1.0, abs=1e-9)
    assert r.minimisers[0] == pytest.approx(WR.D_WIDE[0], rel=1e-9)


def test_a_minimum_on_the_upper_boundary_is_found():
    """Both domain endpoints are evaluated directly; a bounded minimiser never returns one."""
    r = WR.reference_minimum(_upper_boundary)
    assert r.status == "resolved", r.reasons
    assert r.candidate == pytest.approx(1.0, abs=1e-9)
    assert r.minimisers[-1] == pytest.approx(WR.D_WIDE[1], rel=1e-9)


def test_exactly_tied_minima_are_both_retained():
    r = WR.reference_minimum(_two_wells)
    assert r.status == "resolved", r.reasons
    assert r.candidate == pytest.approx(1.0, abs=1e-9)
    assert len(r.minimisers) == 2, r.minimisers
    assert [math.log(k) for k in r.minimisers] == pytest.approx([0.0, 4.0], abs=1e-4)


def test_near_tied_minima_are_both_retained():
    """A tilt of 1e-5 separates the wells by far less than the 1e-3 relative retention band."""
    r = WR.reference_minimum(_two_wells_near_tied)
    assert r.status == "resolved", r.reasons
    assert len(r.minimisers) == 2, r.minimisers
    lo, hi = sorted(r.minimisers)
    assert math.log(lo) == pytest.approx(0.0, abs=1e-2)
    assert math.log(hi) == pytest.approx(4.0, abs=1e-2)


def test_an_unresolved_refinement_sequence_fails_closed():
    r = WR.reference_minimum(_unresolvable)
    assert r.status == "unresolved"
    assert r.candidate is None, "an unresolved search returns no candidate at all"
    assert r.minimisers == []
    assert r.reasons


def test_the_nested_grid_sizes_are_frozen():
    with pytest.raises(ValueError, match="frozen"):
        WR.reference_minimum(_interior, sizes=(40, 80, 160))


def test_the_search_envelope_is_positive_and_deterministic():
    a = WR.reference_minimum(_interior)
    b = WR.reference_minimum(_interior)
    assert a.search_envelope > 0.0
    assert a.search_envelope == b.search_envelope
    assert a.candidate == b.candidate


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 2. Finite topology
# ═════════════════════════════════════════════════════════════════════════════════════════════


def test_a_single_interior_component_is_reported_within_the_domain():
    t = WR.finite_topology(_interior, 1.10)
    assert t.status == "resolved", t.reasons
    assert len(t.components) == 1
    c = t.components[0]
    assert not c.lower_censored and not c.upper_truncated_at_domain_edge
    assert math.log(c.lo) == pytest.approx(1.0 - math.sqrt(0.10), abs=1e-6)
    assert math.log(c.hi) == pytest.approx(1.0 + math.sqrt(0.10), abs=1e-6)


def test_multiple_accepted_components_are_all_reported():
    """The two-well profile at the 10 % relative threshold accepts two separated bands."""
    t = WR.finite_topology(_two_wells, 1.10)
    assert t.status == "resolved", t.reasons
    assert len(t.components) == 2, [c.as_record() for c in t.components]
    assert len(t.roots) == 4
    for c in t.components:
        assert not c.lower_censored and not c.upper_truncated_at_domain_edge
        assert WR.D_WIDE[0] <= c.lo <= c.hi <= WR.D_WIDE[1]


def test_a_component_reaching_the_lower_edge_is_censored_not_extended():
    t = WR.finite_topology(_lower_boundary, 1.50)
    assert t.status == "resolved", t.reasons
    assert len(t.components) == 1
    assert t.components[0].lower_censored
    assert t.components[0].lo == pytest.approx(WR.D_WIDE[0])


def test_a_component_reaching_the_upper_edge_is_truncated_not_called_unlimited():
    """The upper edge is a property of the domain. The record says truncated, and stops there."""
    t = WR.finite_topology(_upper_boundary, 1.50)
    assert t.status == "resolved", t.reasons
    c = t.components[-1]
    assert c.upper_truncated_at_domain_edge
    assert c.hi == pytest.approx(WR.D_WIDE[1])
    assert math.isfinite(c.hi)


def test_a_threshold_tangency_returns_unresolved():
    """T just below the two tied well bottoms: the profile touches without crossing."""
    t = WR.finite_topology(_two_wells, 1.0 * (1.0 - 5e-4))
    assert t.status == "unresolved"
    assert t.tangencies, "a tangency must be reported, not merged away or discarded"
    assert t.roots == []
    assert any("touches the threshold" in r for r in t.reasons)


def test_no_component_may_adjoin_the_endpoint():
    WR.validate_components([{"lo": 1.0, "hi": 500.0}])
    for bad in ({"lo": 1.0, "hi": float("inf")}, {"lo": 1.0, "hi": "inf"},
                {"lo": 1.0, "hi": 501.0}, {"lo": 0.01, "hi": 2.0}):
        with pytest.raises(ValueError):
            WR.validate_components([bad])


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 3. Thresholds, intervals and endpoint classification
# ═════════════════════════════════════════════════════════════════════════════════════════════


def test_threshold_intervals_propagate_the_reference_interval():
    ref = (2.0, 2.5)
    rel = WR.threshold_interval(ref, WR.Convention("x", "relative", 0.10))
    abs_ = WR.threshold_interval(ref, WR.Convention("y", "absolute", 0.25))
    assert rel == pytest.approx((2.2, 2.75))
    assert abs_ == pytest.approx((2.25, 2.75))


def test_every_interval_is_intersected_with_the_nonnegative_axis():
    budget = WR.ReferenceMinimumBudget(0.1, 0.1, 0.0, 0.0, 0.5)
    lo, hi = WR.reference_interval(0.2, budget)
    assert lo == 0.0 and hi == pytest.approx(0.4)


def test_endpoint_included_excluded_and_indeterminate():
    threshold = (1.0, 1.2)
    assert WR.classify_endpoint((0.5, 0.9), threshold) == "endpoint_included"
    assert WR.classify_endpoint((1.3, 1.5), threshold) == "endpoint_excluded"
    assert WR.classify_endpoint((0.9, 1.1), threshold) == "endpoint_indeterminate"
    assert WR.classify_endpoint((1.2, 1.2), threshold) == "endpoint_indeterminate"


def test_eventual_upper_status_is_a_function_of_the_classification():
    assert WR.eventual_upper_status("endpoint_included") == "wide_referenced_upper_set_unbounded"
    assert WR.eventual_upper_status("endpoint_excluded") == "wide_referenced_eventually_excluded"
    assert WR.eventual_upper_status("endpoint_indeterminate") == "upper_status_indeterminate"
    assert WR.eventual_upper_status("limit_construction_failed") == "upper_status_indeterminate"


def test_an_unresolved_reference_blocks_every_classification():
    """An unresolved `J_ref` moves the threshold, so no comparison against it means anything."""
    got = WR.classify_group(None, (0.1, 0.2), reference_status="unresolved",
                            endpoint_constructed=True)
    assert set(got.values()) == {"endpoint_indeterminate"}


def test_a_failed_limit_construction_is_recorded_as_such_everywhere():
    got = WR.classify_group((1.0, 1.1), None, reference_status="resolved",
                            endpoint_constructed=False)
    assert set(got.values()) == {"limit_construction_failed"}


def test_the_near_zero_branch_disables_the_relative_convention_only():
    """U_ref below 0.05 pp: a ratio carries no tolerance, and the absolutes still decide."""
    got = WR.classify_group((0.0, 0.02), (0.001, 0.01), reference_status="resolved",
                            endpoint_constructed=True)
    for c in WR.CONVENTIONS:
        if c.kind == "relative":
            assert got[c.name] == WR.RELATIVE_NOT_APPLICABLE
        else:
            assert got[c.name] == "endpoint_included"


def test_the_relative_convention_is_not_silently_replaced_by_an_absolute_one():
    """The near-zero branch must not quietly promote an absolute result into the relative slot."""
    got = WR.classify_group((0.0, 0.02), (0.001, 0.01), reference_status="resolved",
                            endpoint_constructed=True)
    assert got[WR.PRIMARY_RELATIVE] not in WR.ENDPOINT_CLASSIFICATIONS


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 4. Group and programme rules
# ═════════════════════════════════════════════════════════════════════════════════════════════


def _classifications(primary, a010, a025, other_rel="endpoint_included"):
    return {"rel_q005": other_rel, "rel_q010": primary, "rel_q020": other_rel,
            "abs_a010": a010, "abs_a025": a025}


def _outcome(name, primary, a010, a025, *, reference_status="resolved", constructed=True):
    return WR.group_outcome(name, _classifications(primary, a010, a025),
                            reference_status=reference_status, endpoint_constructed=constructed)


INCL, EXCL, IND = "endpoint_included", "endpoint_excluded", "endpoint_indeterminate"


def test_group_success_requires_the_primary_relative_and_one_absolute():
    assert _outcome("g", INCL, INCL, INCL).outcome == "success"
    assert _outcome("g", INCL, INCL, IND).outcome == "success"


def test_an_absolute_exclusion_is_a_failure_even_with_the_relative_included():
    assert _outcome("g", INCL, INCL, EXCL).outcome == "failure"
    assert _outcome("g", INCL, EXCL, INCL).outcome == "failure"


def test_an_indeterminate_required_convention_is_an_exception_not_a_failure():
    assert _outcome("g", IND, INCL, INCL).outcome == "exception"
    assert _outcome("g", INCL, IND, IND).outcome == "exception"


def test_the_near_zero_relative_branch_is_an_exception():
    o = _outcome("g", WR.RELATIVE_NOT_APPLICABLE, INCL, INCL)
    assert o.outcome == "exception"
    assert "near zero" in o.reason


def test_an_unresolved_reference_or_failed_construction_is_a_group_failure():
    assert _outcome("g", INCL, INCL, INCL, reference_status="unresolved").outcome == "failure"
    assert _outcome("g", INCL, INCL, INCL, constructed=False).outcome == "failure"


def test_h1_strong_requires_six_of_six():
    outcomes = [_outcome("g%d" % i, INCL, INCL, INCL) for i in range(6)]
    assert WR.programme_result(outcomes) == "H1_STRONG"
    assert not WR.headline_requires_named_exception("H1_STRONG")


def test_h1_qualified_is_exactly_five_successes_and_one_named_exception():
    outcomes = [_outcome("g%d" % i, INCL, INCL, INCL) for i in range(5)]
    outcomes.append(_outcome("g5", IND, INCL, INCL))
    assert WR.programme_result(outcomes) == "H1_QUALIFIED"
    assert WR.headline_requires_named_exception("H1_QUALIFIED")
    assert outcomes[-1].name == "g5"


def test_h1_does_not_lead_on_a_failure_or_on_two_exceptions():
    fail = [_outcome("g%d" % i, INCL, INCL, INCL) for i in range(5)]
    fail.append(_outcome("g5", EXCL, INCL, INCL))
    assert WR.programme_result(fail) == "H1_DOES_NOT_LEAD"

    two = [_outcome("g%d" % i, INCL, INCL, INCL) for i in range(4)]
    two += [_outcome("g4", IND, INCL, INCL), _outcome("g5", IND, INCL, INCL)]
    assert WR.programme_result(two) == "H1_DOES_NOT_LEAD"


def test_unresolved_finite_topology_does_not_by_itself_change_the_programme_result():
    """§7.3: secondary topology ambiguity is reported prominently but erases no classification."""
    outcomes = [_outcome("g%d" % i, INCL, INCL, INCL) for i in range(6)]
    assert WR.programme_result(outcomes) == "H1_STRONG"
    record = _group_record("Arabica:caffeine", finite_wide_topology_status="unresolved")
    WR.validate_group_record(record)          # accepted, and still visible in the record


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 5. Error budgets stay in their own quantities
# ═════════════════════════════════════════════════════════════════════════════════════════════


def test_the_endpoint_budget_has_no_slot_for_a_finite_domain_or_shoulder_error():
    fields = set(WR.EndpointBudget.__dataclass_fields__)
    assert fields == {"E_endpoint_construction", "E_endpoint_spatial",
                      "E_endpoint_profile_arithmetic", "E_endpoint_floating"}
    for forbidden in ("E_ref_search", "E_shoulder_step", "remainder", "tie_width"):
        assert forbidden not in fields
    with pytest.raises(TypeError):
        WR.EndpointBudget(1.0, 1.0, 1.0, 1.0, 1.0)         # no fifth slot exists


def test_the_shoulder_budget_enters_no_objective_and_no_threshold():
    shoulder = WR.ShoulderBudget(0.5, 0.5, 0.5)
    ref = WR.ReferenceMinimumBudget(0.01, 0.01, 0.0, 0.0, 0.02)
    end = WR.EndpointBudget(0.01, 0.01, 0.0, 0.0)
    before = (WR.reference_interval(2.0, ref), WR.endpoint_interval(2.0, end))
    assert shoulder.total == pytest.approx(1.5)
    assert before == (WR.reference_interval(2.0, ref), WR.endpoint_interval(2.0, end))


def test_the_reference_envelope_is_asymmetric_by_construction():
    """An evaluated candidate bounds the minimum from above; only the lower side owes the search."""
    b = WR.ReferenceMinimumBudget(0.01, 0.0, 0.0, 0.0, 0.30)
    lo, hi = WR.reference_interval(2.0, b)
    assert hi == pytest.approx(2.01)
    assert lo == pytest.approx(1.69)


# ═════════════════════════════════════════════════════════════════════════════════════════════
# 6. Archive schema
# ═════════════════════════════════════════════════════════════════════════════════════════════


def _convention_record(cls, precondition="unresolved"):
    upper = ("upper_status_indeterminate" if cls == WR.RELATIVE_NOT_APPLICABLE
             else WR.eventual_upper_status(cls, precondition))
    return {"endpoint_classification": cls, "eventual_upper_status": upper,
            "threshold_interval": [1.0, 1.2],
            "components": [{"lo": 0.15, "hi": 12.0, "lower_censored": True,
                            "upper_truncated_at_domain_edge": False}]}


def _group_record(name, **overrides):
    record = {
        "group": name,
        "estimand_tag": WR.ESTIMAND_TAG,
        "reference_minimum_status": "resolved",
        "finite_wide_topology_status": "resolved",
        "tail_onset_status": WR.PROTOCOL_TAIL_ONSET_STATUS,
        "intermediate_domain_status": WR.PROTOCOL_INTERMEDIATE_DOMAIN_STATUS,
        "conventions": {c.name: _convention_record("endpoint_included") for c in WR.CONVENTIONS},
    }
    record.update(overrides)
    return record


def _archive(**overrides):
    a = {
        "protocol_version": "V2",
        "estimand_tag": WR.ESTIMAND_TAG,
        "reference_domain": list(WR.D_WIDE),
        "grid_sizes": list(WR.GRID_SIZES),
        "threshold_families": {"relative": list(WR.RELATIVE_Q), "absolute": list(WR.ABSOLUTE_A)},
        "eventual_upper_precondition": WR.EVENTUAL_UPPER_PRECONDITION,
        "eventual_upper_precondition_status": WR.EVENTUAL_UPPER_PRECONDITION_CURRENT,
        "groups": [_group_record("g%d" % i) for i in range(6)],
        "programme_result": "H1_STRONG",
    }
    a.update(overrides)
    return a


def test_a_well_formed_archive_validates():
    WR.validate_archive(_archive())


def test_the_six_status_fields_are_separate_and_all_required():
    for missing in ("reference_minimum_status", "finite_wide_topology_status",
                    "tail_onset_status", "intermediate_domain_status", "conventions"):
        record = _group_record("g")
        record.pop(missing)
        with pytest.raises(ValueError, match=missing):
            WR.validate_group_record(record)


def test_this_protocol_may_not_claim_a_tail_onset_or_an_intermediate_characterisation():
    with pytest.raises(ValueError, match="tail onset"):
        WR.validate_group_record(_group_record("g", tail_onset_status="not_applicable"))
    with pytest.raises(ValueError, match="intermediate"):
        WR.validate_group_record(
            _group_record("g", intermediate_domain_status="characterized"))


def test_every_threshold_family_result_is_displayed():
    record = _group_record("g")
    record["conventions"].pop("rel_q005")
    with pytest.raises(ValueError, match="displayed"):
        WR.validate_group_record(record)


def test_an_eventual_upper_status_contradicting_its_classification_is_rejected():
    record = _group_record("g")
    record["conventions"]["abs_a010"]["eventual_upper_status"] = \
        "wide_referenced_eventually_excluded"
    with pytest.raises(ValueError, match="contradicts"):
        WR.validate_group_record(record)


def test_the_near_zero_branch_decides_no_upper_status():
    record = _group_record("g")
    record["conventions"]["rel_q010"] = _convention_record(WR.RELATIVE_NOT_APPLICABLE)
    WR.validate_group_record(record)
    record["conventions"]["rel_q010"]["eventual_upper_status"] = \
        "wide_referenced_upper_set_unbounded"
    with pytest.raises(ValueError, match="decides no upper status"):
        WR.validate_group_record(record)


def test_the_near_zero_branch_cannot_appear_on_an_absolute_convention():
    record = _group_record("g")
    record["conventions"]["abs_a010"] = _convention_record(WR.RELATIVE_NOT_APPLICABLE)
    with pytest.raises(ValueError, match="relative-convention result"):
        WR.validate_group_record(record)


def test_the_finite_domain_tag_is_not_the_endpoint_tag():
    assert WR.FINITE_DOMAIN_ESTIMAND_TAG != WR.ESTIMAND_TAG
    with pytest.raises(ValueError, match="FULL-WIDE-ENDPOINT"):
        WR.validate_group_record(
            _group_record("g", estimand_tag=WR.FINITE_DOMAIN_ESTIMAND_TAG))


def test_the_archive_pins_the_domain_the_grids_and_both_threshold_families():
    for bad in ({"reference_domain": [0.15, 1000.0]},
                {"grid_sizes": [40, 80, 160]},
                {"threshold_families": {"relative": [0.10], "absolute": list(WR.ABSOLUTE_A)}},
                {"threshold_families": {"relative": list(WR.RELATIVE_Q), "absolute": [0.10]}}):
        with pytest.raises(ValueError, match="frozen"):
            WR.validate_archive(_archive(**bad))


def test_the_archive_declares_the_precondition_of_the_eventual_upper_vocabulary():
    """`wide_referenced_upper_set_unbounded` is not self-supporting: it needs the fixed-time limit."""
    with pytest.raises(ValueError, match="conditional on"):
        WR.validate_archive(_archive(eventual_upper_precondition="none"))
    with pytest.raises(ValueError, match="eventual_upper_precondition_status"):
        WR.validate_archive(_archive(eventual_upper_precondition_status="proved"))


def test_the_precondition_vocabulary_is_the_three_state_assurance_vocabulary():
    assert WR.EVENTUAL_UPPER_PRECONDITION_STATUSES == ("unresolved", "assured", "failed")


def test_the_current_precondition_state_agrees_with_its_evidence():
    """`assured` since 2026-08-03, when PR-03a closed on a proof.

    The state is pinned to the generated evidence rather than asserted on its own, so the module
    constant and the PR-03a archive cannot drift apart. The VOCABULARY is architecture and is
    frozen; this value is state.
    """
    import json

    assert WR.EVENTUAL_UPPER_PRECONDITION_CURRENT in WR.EVENTUAL_UPPER_PRECONDITION_STATUSES
    assert WR.EVENTUAL_UPPER_PRECONDITION_CURRENT == "assured"
    archive = json.loads((_ROOT / "docs" / "paper1_resource"
                          / "PAPER_A_ENDPOINT_CONSTRUCTION.json").read_text(encoding="utf-8"))
    assert archive["overall_PR03a_status"] == "assured", (
        "the precondition may only read 'assured' while PR-03a is assured")


def test_unresolved_retains_the_conditional_machine_value():
    """The mapping still runs; what it may not do is become prose. That is a text rule, not a code
    one, so the archive keeps the field and the protocol carries the prohibition."""
    assert WR.eventual_upper_status("endpoint_included", "unresolved") == \
        "wide_referenced_upper_set_unbounded"
    WR.validate_archive(_archive(eventual_upper_precondition_status="unresolved"))


def test_assured_leaves_the_mapping_unchanged():
    for cls in ("endpoint_included", "endpoint_excluded", "endpoint_indeterminate"):
        assert WR.eventual_upper_status(cls, "assured") == WR.eventual_upper_status(cls,
                                                                                   "unresolved")
    a = _archive(eventual_upper_precondition_status="assured")
    WR.validate_archive(a)


def test_failed_collapses_every_eventual_upper_status_and_fails_closed():
    """An inference cannot outlive a refuted premise.

    The endpoint classification is still reportable — it is a numerical comparison and the refuted
    proposition is about time, not about the interval. What does not survive is the eventual reading.
    """
    for cls in WR.ENDPOINT_CLASSIFICATIONS:
        assert WR.eventual_upper_status(cls, "failed") == "upper_status_indeterminate"

    collapsed = _archive(
        eventual_upper_precondition_status="failed",
        groups=[{**_group_record("g%d" % i),
                 "conventions": {c.name: _convention_record("endpoint_included", "failed")
                                 for c in WR.CONVENTIONS}} for i in range(6)])
    WR.validate_archive(collapsed)
    for group in collapsed["groups"]:
        for cr in group["conventions"].values():
            assert cr["endpoint_classification"] == "endpoint_included"
            assert cr["eventual_upper_status"] == "upper_status_indeterminate"

    surviving = _archive(eventual_upper_precondition_status="failed")   # built for "unresolved"
    with pytest.raises(ValueError, match="under a failed precondition"):
        WR.validate_archive(surviving)


def test_a_failed_precondition_does_not_change_the_programme_rule():
    """The rule reads endpoint classifications, not eventual status, so it is untouched."""
    outcomes = [_outcome("g%d" % i, INCL, INCL, INCL) for i in range(6)]
    assert WR.programme_result(outcomes) == "H1_STRONG"


def test_an_unknown_precondition_status_is_rejected_at_the_mapping():
    with pytest.raises(ValueError, match="unknown precondition status"):
        WR.eventual_upper_status("endpoint_included", "deferred")


# ── 6b. the programme result is derived from the records, not declared ───────────────────────


def _conventions(primary, a010, a025, other_rel="endpoint_included", precondition="unresolved"):
    return {"rel_q005": _convention_record(other_rel, precondition),
            "rel_q010": _convention_record(primary, precondition),
            "rel_q020": _convention_record(other_rel, precondition),
            "abs_a010": _convention_record(a010, precondition),
            "abs_a025": _convention_record(a025, precondition)}


def _group(name, primary=INCL, a010=INCL, a025=INCL, **overrides):
    return _group_record(name, conventions=_conventions(primary, a010, a025), **overrides)


def _successes(n, start=0):
    return [_group("g%d" % i) for i in range(start, start + n)]


def test_a_declared_programme_result_must_match_the_group_derived_one():
    """The defect this closes: the validator checked only that the label was one of three strings.

    `group_outcome` and `programme_result` were correct and independently tested, but nothing
    connected them to the archive, so an archive could carry six excluded groups and declare
    `H1_STRONG`. A rule nothing calls is not a control.
    """
    excluded = [_group("g%d" % i, primary=EXCL) for i in range(6)]
    with pytest.raises(ValueError, match="contradicts group-derived result"):
        WR.validate_archive(_archive(groups=excluded, programme_result="H1_STRONG"))

    qualified = _successes(5) + [_group("g5", primary=IND)]
    with pytest.raises(ValueError, match="contradicts group-derived result"):
        WR.validate_archive(_archive(groups=qualified, programme_result="H1_STRONG"))


def test_the_archive_requires_exactly_six_groups():
    for n in (0, 5, 7):
        with pytest.raises(ValueError, match="exactly 6 groups"):
            WR.validate_archive(_archive(groups=_successes(n), programme_result="H1_STRONG"))


def test_group_identifiers_must_be_unique_and_nonempty():
    dupes = _successes(5) + [_group("g0")]
    with pytest.raises(ValueError, match="unique"):
        WR.validate_archive(_archive(groups=dupes, programme_result="H1_STRONG"))

    for blank in ("", "   "):
        blanks = _successes(5) + [_group(blank)]
        with pytest.raises(ValueError, match="nonempty string identifier"):
            WR.validate_archive(_archive(groups=blanks, programme_result="H1_STRONG"))


def test_a_failed_limit_construction_holds_under_every_convention_or_none():
    """It is a property of the group's endpoint, not of one threshold.

    Showing it under some conventions only would let the derivation read the group as constructed.
    """
    mixed = _successes(5) + [_group("g5", a010="limit_construction_failed")]
    with pytest.raises(ValueError, match="must apply to every convention"):
        WR.validate_archive(_archive(groups=mixed, programme_result="H1_DOES_NOT_LEAD"))


def test_an_unresolved_reference_minimum_cannot_carry_an_inclusion():
    """It moves the threshold, so a comparison against that threshold does not exist."""
    bad = _successes(5) + [_group("g5", reference_minimum_status="unresolved")]
    with pytest.raises(ValueError, match="only endpoint_indeterminate"):
        WR.validate_archive(_archive(groups=bad, programme_result="H1_DOES_NOT_LEAD"))


def test_the_three_programme_labels_are_accepted_when_the_records_derive_them():
    WR.validate_archive(_archive(groups=_successes(6), programme_result="H1_STRONG"))

    qualified = _successes(5) + [_group("g5", primary=IND)]
    WR.validate_archive(_archive(groups=qualified, programme_result="H1_QUALIFIED"))

    failing = _successes(5) + [_group("g5", primary=EXCL)]
    WR.validate_archive(_archive(groups=failing, programme_result="H1_DOES_NOT_LEAD"))


def test_a_group_whose_endpoint_construction_failed_derives_a_failure():
    collapsed = {c.name: _convention_record("limit_construction_failed") for c in WR.CONVENTIONS}
    groups = _successes(5) + [_group_record("g5", conventions=collapsed)]
    WR.validate_archive(_archive(groups=groups, programme_result="H1_DOES_NOT_LEAD"))
    with pytest.raises(ValueError, match="contradicts group-derived result"):
        WR.validate_archive(_archive(groups=groups, programme_result="H1_QUALIFIED"))


def test_a_failed_precondition_collapses_eventual_status_without_moving_the_label():
    """The premise is about time; the classification is an interval comparison. Only one collapses."""
    groups = [_group_record("g%d" % i,
                            conventions=_conventions(INCL, INCL, INCL, precondition="failed"))
              for i in range(6)]
    archive = _archive(groups=groups, programme_result="H1_STRONG",
                       eventual_upper_precondition_status="failed")
    WR.validate_archive(archive)
    for group in archive["groups"]:
        for cr in group["conventions"].values():
            assert cr["eventual_upper_status"] == "upper_status_indeterminate"
            assert cr["endpoint_classification"] == "endpoint_included"


def test_no_p0_g8_result_archive_exists_in_the_tree():
    """This pass builds the contract. Producing the archive is the scientific gate, not authorised."""
    assert not (_ROOT / "docs" / "paper1_resource"
                / "PAPER_A_ASYMPTOTIC_PROFILE_LIMITS.json").exists()


def test_the_module_reads_no_campaign_data():
    """Checked on the parsed imports, not on the prose — a docstring may name what it excludes."""
    import ast

    tree = ast.parse((_ROOT / "puckworks" / "paper_a" / "wide_reference.py")
                     .read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert imported == {"__future__", "math", "dataclasses", "typing", "numpy",
                        "scipy.optimize"}, sorted(imported)

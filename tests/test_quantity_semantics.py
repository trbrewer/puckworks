"""Orthogonal quantity semantics + separated readiness axes (PV-19B Phase 5, #70).

Offline + deterministic. Guards the orthogonal QuantityDefinition axes (per-species / flow-trend /
profile are NOT denominators), the plot compatibility signature (same unit is necessary but not
sufficient), and the SEPARATION of shared-scenario execution readiness from output comparability (a model
may execute on the shared scenario and show native outputs in a separate panel without converting to
Cameron EY/TDS).
"""
import pytest

from puckworks.product import quantity_semantics as qs


# ── orthogonal axes ─────────────────────────────────────────────────────────────────
def test_reference_bases_are_true_denominators_only():
    for bad in ("per_species", "flow_trend", "liquid_phase_profile"):
        assert bad not in qs.REFERENCE_BASES
    for good in ("packed_bed_volume", "grain_total_volume", "dry_coffee_mass", "dimensionless"):
        assert good in qs.REFERENCE_BASES


def test_quantity_definition_validates_every_axis():
    with pytest.raises(ValueError):
        qs.QuantityDefinition("x", "n", "not_a_basis", "solid", "single_soluble_pool", "global",
                              "final", "absolute", "%", "simulated", "obs")
    with pytest.raises(ValueError):
        qs.QuantityDefinition("x", "n", "dry_coffee_mass", "solid", "single_soluble_pool", "global",
                              "final", "not_an_aggregation", "%", "simulated", "obs")


# ── plot compatibility signature ────────────────────────────────────────────────────
def _q(**kw):
    base = dict(quantity_id="q", numerator="c", reference_basis="mobile_liquid_volume",
               phase="mobile_liquid", species_scope="total_solute", spatial_support="outlet",
               temporal_support="cumulative", aggregation="absolute", unit="kg/m^3",
               semantic_role="simulated", observable_definition="o")
    base.update(kw)
    return qs.QuantityDefinition(**base)


def test_same_unit_different_basis_cannot_share_an_axis():
    a = _q(reference_basis="mobile_liquid_volume")
    b = _q(reference_basis="grain_total_volume")     # same unit, different denominator
    assert a.unit == b.unit and not qs.may_share_axis(a, b)


def test_same_unit_different_species_scope_cannot_share_an_axis():
    a = _q(species_scope="total_solute")
    b = _q(species_scope="named_species")            # same unit, different species scope
    assert not qs.may_share_axis(a, b)


def test_identical_signature_may_share():
    assert qs.may_share_axis(_q(), _q())


def test_relative_trend_is_never_overlaid_with_absolute():
    trend = _q(aggregation="relative_trend", unit="-")
    absolute = _q(aggregation="absolute", unit="-")
    assert not qs.may_share_axis(trend, absolute)
    assert qs.output_comparability(absolute, trend) == "NOT_COMPARABLE"


def test_incompatible_absolute_pair_is_faceted_not_overlaid():
    a = _q(reference_basis="mobile_liquid_volume")
    b = _q(reference_basis="grain_total_volume")
    assert qs.output_comparability(a, b) == "FACETED_SEPARATELY"
    assert qs.output_comparability(a, b, validated_conversion_registered=True) == \
        "COMPARED_AFTER_VALIDATED_CONVERSION"


# ── the two readiness decisions are independent ─────────────────────────────────────
def test_execution_ready_does_not_imply_comparable():
    # Roman-Corrochano can run on the shared scenario (as a trend panel) yet is NOT comparable to EY
    exe = qs.shared_scenario_execution_readiness("romancorrochano2017.extraction")
    assert exe["execution_readiness"] == "READY_FOR_SHARED_SCENARIO"
    assert qs.candidate_comparability("romancorrochano2017.extraction") == "NOT_COMPARABLE"


def test_pannusch_and_mo_need_an_input_adapter_and_are_faceted():
    for cid in ("pannusch2024.solver", "mo2023_2.coupled_bed"):
        exe = qs.shared_scenario_execution_readiness(cid)
        assert exe["execution_readiness"] == "INPUT_ADAPTER_REQUIRED"
        assert exe["missing_inputs"]
        assert qs.candidate_comparability(cid) == "FACETED_SEPARATELY"


def test_grudeva_execution_blocker_is_technical_not_rights():
    # #73 resolved 2026-08-14 by documented permission. The shared scenario still cannot honestly drive
    # it: no fines radius, no shared flow prescription, and an untested basis conversion.
    exe = qs.shared_scenario_execution_readiness("grudeva2025.reduced")
    assert exe["execution_readiness"] == "INPUT_ADAPTER_REQUIRED"
    assert exe["missing_inputs"]
    assert "rights" not in exe["reason"].lower().split("(")[0] or "not a rights" in exe["reason"].lower()


def test_a_rights_blocked_component_short_circuits_execution_readiness():
    # the GENERIC short-circuit (no component is blocked today) stays exercised
    import unittest.mock as mock

    from puckworks import rights
    cid = "mo2023_2.coupled_bed"
    rec = rights.RightsRecord(cid, "RIGHTS_BLOCKED", "RIGHTS_BLOCKED", "RIGHTS_BLOCKED",
                              rights_note="synthetic block for this test", source="test",
                              decision_issue="#0", review_date="2026-08-14")
    with mock.patch.dict(rights._RECORDS, {cid: rec}):
        exe = qs.shared_scenario_execution_readiness(cid)
    assert exe["execution_readiness"] == "RIGHTS_BLOCKED"


def test_no_candidate_is_directly_comparable_to_cameron_ey():
    r = qs.build_report()
    assert r["directly_comparable_to_cameron_ey"] == []
    assert "EXECUTION and output COMPARABILITY are separate" in r["conclusion"]
    assert "shared-scenario execution does not imply output comparability" in r["boundaries"]


def test_measurement_agenda_turns_blockers_into_actions():
    agenda = qs.measurement_agenda()
    assert agenda and all(
        {"blocker_id", "component", "missing_quantity", "acceptance", "enables_test"} <= set(a)
        for a in agenda)
    # a READY candidate contributes no agenda items; a candidate with input blockers does
    comps = {a["component"] for a in agenda}
    assert "romancorrochano2017.extraction" not in comps
    # grudeva joined the agenda on 2026-08-14: with the rights block gone (#73), its blockers are
    # genuine missing INPUTS, which is exactly what this agenda exists to record.
    assert "grudeva2025.reduced" in comps


def test_report_covers_every_extraction_runtime_candidate():
    import puckworks
    r = qs.build_report()
    covered = {row["component_id"] for row in r["candidates"]}
    expected = {c.name for c in puckworks.components()
                if c.stage == "extraction" and c.execution_role == "runtime"
                and c.name != "cameron2020.extraction_bdf"}
    assert covered == expected

"""Reference-basis ontology + fail-closed inventory-adapter tests (PV-19B Phase 5, #70).

Offline + deterministic. Guards the finite quantity-basis vocabulary, that inventory conversion is
fail-closed (only the identity is registered; every cross-basis request raises), that the conservation
primitive rejects a non-conserving transform, and that NO extraction candidate is admissible as a second
common-scenario lens (different basis + no validated conversion, or rights-blocked, or a trend).
"""
import pytest

import puckworks
from puckworks.product import lab_adapter_audit as audit
from puckworks.product import reference_basis as rb


# ── vocabulary + typed basis ────────────────────────────────────────────────────────
def test_quantity_basis_vocabulary_is_finite_and_bases_are_typed():
    assert rb.COMMON_LENS_BASIS in rb.QUANTITY_BASES
    for spec in rb.all_bases():
        assert spec.quantity_basis in rb.QUANTITY_BASES
    with pytest.raises(ValueError):
        rb.BasisSpec("x", "not_a_basis", "obs")


def test_unrecorded_component_is_unspecified_not_guessed():
    assert rb.basis_of("brewer2026.lb_taichi").quantity_basis == "unspecified"
    assert rb.basis_of("cameron2020.extraction_bdf").quantity_basis == "bed_volume"


# ── conservation primitive ──────────────────────────────────────────────────────────
def test_total_inventory_and_identity_conserves():
    c = [2.0, 4.0, 6.0]
    v = [1.0, 0.5, 0.25]
    total = rb.total_inventory(c, v)
    assert total == pytest.approx(2 * 1 + 4 * 0.5 + 6 * 0.25)
    rb.assert_inventory_conserved(total, total)          # identical -> conserves


def test_conservation_check_rejects_a_non_conserving_transform():
    before = rb.total_inventory([1.0, 1.0], [1.0, 1.0])          # 2.0
    after = rb.total_inventory([1.0, 2.0], [1.0, 1.0])           # 3.0 -> not conserved
    with pytest.raises(rb.InventoryNotConserved):
        rb.assert_inventory_conserved(before, after)


def test_conservation_check_accepts_a_conserving_rescale():
    # move inventory between cells but keep the total (a legitimate conserving redistribution)
    before = rb.total_inventory([2.0, 0.0], [1.0, 1.0])          # 2.0
    after = rb.total_inventory([1.0, 1.0], [1.0, 1.0])           # 2.0
    rb.assert_inventory_conserved(before, after)


# ── conversion is fail-closed ───────────────────────────────────────────────────────
def test_identity_conversion_is_registered_and_exact():
    assert rb.conversion_rule("bed_volume", "bed_volume").validated
    assert rb.convert_inventory([1.0, 2.0, 3.0], "bed_volume", "bed_volume") == [1.0, 2.0, 3.0]


@pytest.mark.parametrize("frm,to", [
    ("grain_volume", "bed_volume"), ("per_bed_cell", "bed_volume"),
    ("per_species", "bed_volume"), ("bed_volume", "grain_volume"),
])
def test_every_cross_basis_conversion_fails_closed(frm, to):
    assert rb.conversion_rule(frm, to) is None
    with pytest.raises(rb.UnsupportedConversion):
        rb.convert_inventory([1.0, 2.0], frm, to)


def test_no_cross_basis_rule_is_registered_today():
    cross = [k for k, v in rb._RULES.items() if k[0] != k[1] and v.validated]
    assert cross == []                                   # only identity rules are registered


# ── second-lens admissibility (mechanical) ──────────────────────────────────────────
def test_grudeva_is_rights_blocked_from_second_lens():
    r = rb.adapter_readiness("grudeva2025.reduced")
    assert r["code_rights_blocked"] is True
    assert r["admissible_as_second_lens"] is False and "rights" in r["blocker"].lower()


@pytest.mark.parametrize("cid", ["mo2023_2.coupled_bed", "pannusch2024.solver",
                                 "romancorrochano2017.extraction"])
def test_no_candidate_is_admissible_without_a_validated_conversion(cid):
    r = rb.adapter_readiness(cid)
    assert r["admissible_as_second_lens"] is False
    assert r["has_validated_conversion"] is False
    assert r["quantity_basis"] != rb.COMMON_LENS_BASIS


def test_report_admits_no_second_lens_and_lists_only_identity_conversions():
    rep = rb.build_basis_report()
    assert rep["admissible_as_second_lens"] == []
    assert "NO second lens is added" in rep["conclusion"]
    assert all("->" in c and c.split("->")[0] == c.split("->")[1]
               for c in rep["registered_conversions"])   # identity-only


def test_typed_basis_is_consistent_with_the_prose_audit():
    # a candidate whose typed basis differs from Cameron's (no validated conversion) must NOT be READY in
    # the independent prose audit — the two views cannot disagree.
    a = {r["component_id"]: r for r in audit.build_audit()["candidates"]}
    for cid, arow in a.items():
        rr = rb.adapter_readiness(cid)
        if not rr["admissible_as_second_lens"]:
            assert arow["decision"] != "READY_FOR_BOUNDED_ADAPTER", cid


def test_report_covers_every_extraction_runtime_candidate():
    rep = rb.build_basis_report()
    covered = {r["component_id"] for r in rep["candidates"]}
    expected = {c.name for c in puckworks.components()
                if c.stage == "extraction" and c.execution_role == "runtime"
                and c.name != "cameron2020.extraction_bdf"}
    assert covered == expected

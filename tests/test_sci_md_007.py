import pytest

from puckworks.analysis import sci_md_007 as s


@pytest.mark.parametrize("unit,value,expected", [
    ("mg/kg", 1000, 1), ("g/kg", 1, 1), ("mg/100 g", 100, 1),
    ("g/100 g", .1, 1), ("%", .1, 1),
])
def test_exact_conversions(unit, value, expected):
    actual, uncertainty = s.exact_to_mg_g(value, unit, value / 10)
    assert actual == expected
    assert uncertainty == expected / 10


def test_moisture_conversion_and_rejections():
    assert s.as_received_to_dry(9, .1, "wet_basis") == 10
    assert s.as_received_to_dry(10, .1, "dry_basis") == 11
    with pytest.raises(ValueError):
        s.as_received_to_dry(9, None, "wet_basis")
    with pytest.raises(ValueError):
        s.as_received_to_dry(9, .1, "wet_basis", same_material_batch=False)
    with pytest.raises(ValueError):
        s.reject_phase_volume_conversion("mg/mL solid phase")


def eligible_row(**updates):
    row = dict(analyte="caffeine", roasted_unextracted=True,
               target_semantics="TOTAL_ROASTED_CONTENT",
               measurement_provenance="DIRECT_ROASTED_MATERIAL_ASSAY",
               canonical_basis="dry roasted coffee", conversion_supported=True,
               rights_usable=True, duplicate=False, source_publication_id="s1",
               source_locator="Table 2", base_coffee_material_id="m1",
               roast_batch_id="r1", analytical_method="HPLC", data_lineage_id="d1")
    row.update(updates)
    return row


def test_primary_eligibility_is_semantic_and_provenance_strict():
    assert s.primary_eligible(eligible_row())
    assert not s.primary_eligible(eligible_row(measurement_provenance="ASYMPTOTIC_EXTRACTION_ESTIMATE"))
    assert not s.primary_eligible(eligible_row(target_semantics="SOLID_PHASE_CONCENTRATION",
                                               measurement_provenance="MODEL_INFERRED_OR_FITTED"))
    assert not s.primary_eligible(eligible_row(source_publication_id="angeloni2023"))


def test_exact_boolean_reducer_and_compound_preservation():
    passed = {g: True for g in s.COMPOUND_GATES}
    failed = dict(passed, F3=False)
    result = s.disposition(passed, failed, True)
    assert result["caffeine_feasible"] is True
    assert result["trigonelline_feasible"] is False
    assert result["scientific_disposition"] == s.FAIL
    assert s.disposition(passed, passed, False)["scientific_disposition"] == s.FAIL
    assert s.disposition(passed, passed, True)["scientific_disposition"] == s.PASS


def test_contract_is_frozen_and_valid():
    assert s.validate_contract()["valid"]

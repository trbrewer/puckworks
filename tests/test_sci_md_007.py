import pytest

from puckworks.analysis import sci_md_007 as s
from puckworks.analysis import sci_md_007_r1 as r1


@pytest.mark.parametrize(
    "unit,value,expected",
    [
        ("mg/kg", 1000, 1),
        ("g/kg", 1, 1),
        ("mg/100 g", 100, 1),
        ("g/100 g", 0.1, 1),
        ("%", 0.1, 1),
    ],
)
def test_exact_conversions(unit, value, expected):
    actual, uncertainty = s.exact_to_mg_g(value, unit, value / 10)
    assert actual == expected
    assert uncertainty == expected / 10


def test_moisture_conversion_and_rejections():
    assert s.as_received_to_dry(9, 0.1, "wet_basis") == 10
    assert s.as_received_to_dry(10, 0.1, "dry_basis") == 11
    with pytest.raises(ValueError):
        s.as_received_to_dry(9, None, "wet_basis")
    with pytest.raises(ValueError):
        s.as_received_to_dry(9, 0.1, "wet_basis", same_material_batch=False)
    with pytest.raises(ValueError):
        s.reject_phase_volume_conversion("mg/mL solid phase")


def eligible_row(**updates):
    row = dict(
        analyte="caffeine",
        roasted_unextracted=True,
        target_semantics="TOTAL_ROASTED_CONTENT",
        measurement_provenance="DIRECT_ROASTED_MATERIAL_ASSAY",
        canonical_basis="dry roasted coffee",
        conversion_supported=True,
        rights_usable=True,
        duplicate=False,
        source_publication_id="s1",
        source_locator="Table 2",
        base_coffee_material_id="m1",
        roast_batch_id="r1",
        analytical_method="HPLC",
        data_lineage_id="d1",
    )
    row.update(updates)
    return row


def test_primary_eligibility_is_semantic_and_provenance_strict():
    assert s.primary_eligible(eligible_row())
    assert not s.primary_eligible(
        eligible_row(measurement_provenance="ASYMPTOTIC_EXTRACTION_ESTIMATE")
    )
    assert not s.primary_eligible(
        eligible_row(
            target_semantics="SOLID_PHASE_CONCENTRATION",
            measurement_provenance="MODEL_INFERRED_OR_FITTED",
        )
    )
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


@pytest.mark.parametrize(
    "semantics,provenance",
    [
        ("SOLID_PHASE_CONCENTRATION", "MODEL_INFERRED_OR_FITTED"),
        ("ASYMPTOTIC_EXTRACTED_MASS", "ASYMPTOTIC_EXTRACTION_ESTIMATE"),
        ("BEVERAGE_CONCENTRATION_OR_YIELD", "BEVERAGE_ENDPOINT_INFERENCE"),
    ],
)
def test_non_total_evidence_is_ineligible(semantics, provenance):
    assert not s.primary_eligible(
        eligible_row(target_semantics=semantics, measurement_provenance=provenance)
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("canonical_basis", ""),
        ("conversion_supported", False),
        ("rights_usable", False),
        ("duplicate", True),
        ("roasted_unextracted", False),
        ("source_locator", ""),
        ("analytical_method", ""),
        ("roast_batch_id", ""),
        ("data_lineage_id", ""),
    ],
)
def test_each_row_eligibility_primitive_is_required(field, value):
    assert not s.primary_eligible(eligible_row(**{field: value}))


def test_registers_validate_and_eligibility_is_data_derived():
    sources = r1.read_csv("sources.csv")
    materials = r1.read_csv("materials.csv")
    observations = r1.read_csv("observations.csv")
    r1.validate_registers(sources, materials, observations)
    mapping, _ = r1.groups(materials, observations)
    qualified = r1.qualify(observations, mapping)
    direct = next(x for x in qualified if x["observation_id"].startswith("acre-caf"))
    fitted = next(x for x in qualified if x["observation_id"] == "pannusch-caffeine")
    assert direct["primary_prediction_label_eligible"] is True
    assert fitted["primary_prediction_label_eligible"] is False
    changed = [dict(x) for x in observations]
    row = next(x for x in changed if x["observation_id"].startswith("acre-caf"))
    row["canonical_unit"] = ""
    row["conversion_status"] = "UNRESOLVED"
    assert not next(
        x for x in r1.qualify(changed, mapping) if x["observation_id"] == row["observation_id"]
    )["primary_prediction_label_eligible"]


@pytest.mark.parametrize(
    "mutation,match",
    [
        (lambda s, m, o: o.append(dict(o[0])), "invalid/duplicate observation_id"),
        (lambda s, m, o: o[0].update(analyte="invalid"), "invalid observation enum"),
        (
            lambda s, m, o: o[0].update(source_publication_id="missing"),
            "observation source FK failure",
        ),
        (
            lambda s, m, o: o[0].update(base_coffee_material_id="missing"),
            "observation material FK failure",
        ),
        (lambda s, m, o: o[0].update(uncertainty_value_as_published="-1"), "invalid uncertainty"),
        (
            lambda s, m, o: o[0].update(number_of_analytical_replicates="-1"),
            "invalid replicate count",
        ),
        (lambda s, m, o: o[0].update(rights_usable="FALSE"), "must be true or false"),
        (lambda s, m, o: o[0].update(data_lineage_id="angeloni2023"), "prohibited lineage"),
    ],
)
def test_register_validator_fails_closed(mutation, match):
    sources = r1.read_csv("sources.csv")
    materials = r1.read_csv("materials.csv")
    observations = r1.read_csv("observations.csv")
    mutation(sources, materials, observations)
    with pytest.raises(ValueError, match=match):
        r1.validate_registers(sources, materials, observations)


def test_connected_groups_join_publications_and_roasts():
    materials = r1.read_csv("materials.csv")
    observations = r1.read_csv("observations.csv")
    mapping, edges = r1.groups(materials, observations)
    dias = {
        mapping[(m["base_coffee_material_id"], m["roast_batch_id"])]
        for m in materials
        if m["source_publication_id"] == "dias2015"
    }
    assert len(dias) == 1
    assert any("shared source_publication_id" in x["reason"] for x in edges)


def test_real_reducer_is_register_derived_and_blocks_model():
    sources = r1.read_csv("sources.csv")
    materials = r1.read_csv("materials.csv")
    observations = r1.read_csv("observations.csv")
    rows, edges, gates, f5, feasible, overall = r1.reduce(sources, materials, observations)
    assert len(rows) == len(observations) == 228 and edges
    assert gates["caffeine"]["F2"]["material_roast_units"] == 112
    assert gates["caffeine"]["F2"]["publications"] == 3
    assert gates["caffeine"]["F2"]["identified_laboratories"] == 1
    assert gates["caffeine"]["F7"]["outer_validation_groups"] == 3
    assert f5["paired_material_roast_units"] == 112 and not f5["pass"]
    assert feasible == {"caffeine": False, "trigonelline": False} and not overall


def test_fitted_and_asymptotic_classes_are_present_without_inflation():
    observations = r1.read_csv("observations.csv")
    assert sum(x["measurement_provenance"] == "MODEL_INFERRED_OR_FITTED" for x in observations) == 2
    assert (
        sum(x["measurement_provenance"] == "ASYMPTOTIC_EXTRACTION_ESTIMATE" for x in observations)
        == 2
    )
    assert (
        len(
            {
                x["base_coffee_material_id"]
                for x in observations
                if x["source_publication_id"] == "schmieder2023"
            }
        )
        == 1
    )


def test_search_is_numeric_terminal_and_citation_complete():
    sources = r1.read_csv("sources.csv")
    result = r1.search_complete(sources)
    assert result["pass"] and result["searches"] == 24 and result["result_records"] == 400
    assert result["citation_records"] >= 12


def test_synthetic_pass_path_runs_all_models_without_group_leakage():
    records = []
    for group in range(4):
        for species in ("Arabica", "Robusta"):
            for roast_i, roast in enumerate(("light", "dark")):
                records.append(
                    {
                        "validation_group_id": f"g{group}",
                        "species": species,
                        "roast": roast,
                        "metric": roast_i,
                        "target": 10 + group + (species == "Robusta") * 4 - roast_i,
                    }
                )
    result = r1.run_simple_models(records)
    assert set(result["models"]) == {"M0", "M1", "M2", "M3"}
    assert result["outer_groups"] == ["g0", "g1", "g2", "g3"]
    assert all(x["prediction_count"] == len(records) for x in result["models"].values())
    assert result == r1.run_simple_models(records)


def test_generated_artifacts_are_byte_identical():
    result = r1.build(check=True)
    assert result["operational_status"] == "COMPLETE"
    assert result["model_stage"] == "NOT_RUN_FEASIBILITY_FAILED"


def test_claim_ceiling_and_extractable_status_are_independent():
    result = __import__("json").loads((r1.OUT / "result.json").read_text())
    assert result["extractable_inventory_mapping_status"] == "NOT_ESTABLISHED"
    assert any("Physical validation remains NOT_ESTABLISHED" in x for x in result["claim_ceiling"])
    assert result["model_adoption_status"] == "NOT_AUTHORIZED_BY_FEASIBILITY_SCREEN"

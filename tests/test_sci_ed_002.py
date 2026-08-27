import json
from pathlib import Path

import pytest

from tools import validate_sci_ed_002 as ed2


PACK = Path(__file__).parents[1] / "docs" / "analysis" / "sci_ed_002"


def test_valid_design_is_capacity_not_evidence():
    result = ed2.validate()
    assert result["status"] == "PROSPECTIVE_DESIGN_CAPACITY_ONLY_NO_MEASUREMENTS"
    assert result["projected_gates"] == {"open_primary_units": 30, "total_primary_units": 36, "open_base_materials": 20, "total_base_materials": 24, "open_laboratories": 4, "sealed_groups_excluded": 1, "bridge_primary_count": 0}


@pytest.mark.parametrize("fixture", sorted((PACK / "fixtures" / "invalid").glob("*.json")), ids=lambda p: p.stem)
def test_each_negative_fixture_has_exact_reason(fixture):
    record = json.loads(fixture.read_text())
    with pytest.raises(ValueError, match=f"^{record['expected_failure']}$"):
        ed2.validate(record["mutation"])


def test_claim_ceiling_and_estimands():
    result = json.loads((PACK / "RESULT.json").read_text())
    contract = json.loads((PACK / "ESTIMAND_CONTRACT.json").read_text())
    assert not result["measurements_collected"] and not result["predictor_eligible"]
    assert contract["estimands"]["Q_production_solid_initial"]["status"] == "NOT_ESTABLISHED"
    assert contract["ratio"]["clip"] is False

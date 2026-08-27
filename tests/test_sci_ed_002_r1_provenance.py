import pytest
from tools.validate_sci_ed_002_provenance import validate

@pytest.mark.parametrize("mutation,reason", [
 ("unrelated_source","SOURCE_TOPIC_DOES_NOT_SUPPORT_ASSIGNED_METHOD_CLAIM"),
 ("aoac_missing_identity","AOAC_EXACT_APPLICABLE_METHOD_IDENTITY_REQUIRED"),
 ("iso_trigonelline","ISO_20481_CANNOT_SUPPORT_TRIGONELLINE"),
 ("unsupported_threshold","STOPPING_RULE_CRITICAL_ELEMENT_UNSUPPORTED"),
 ("missing_max_action","STOPPING_RULE_MAXIMUM_ACTION_REQUIRED"),
 ("generic_lab","GENERIC_UNNAMED_LABORATORY_PROHIBITED"),
 ("three_labs","FOUR_EXACT_LABORATORY_CANDIDATES_REQUIRED"),
 ("quotation","COST_ESTIMATE_MUST_NOT_BE_LABELLED_QUOTATION"),
 ("missing_access_date","SOURCE_IDENTITY_VERSION_ACCESS_DATE_REQUIRED"),
])
def test_exact_negative_controls(mutation, reason):
    with pytest.raises(ValueError, match=reason): validate(mutation)

def test_current_rule_remains_fail_closed():
    with pytest.raises(ValueError, match="STOPPING_RULE_CRITICAL_ELEMENT_UNSUPPORTED"):
        validate()

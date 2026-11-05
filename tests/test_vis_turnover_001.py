"""Synthetic checks for the Step 0 stop, without real corpus or outcomes."""

import json
from pathlib import Path

import pytest

from puckworks.analysis import vis_turnover_001 as v


@pytest.mark.parametrize("goal", [None, 0, -1, 4.0])
def test_goal_presence_is_not_a_control_classifier(goal):
    # A generic goal container carries no source-specific controller semantics.
    flags = v.field_presence({"hydraulic": {"flow_goal_reported__native": [goal]}}, {})
    assert flags["flow_goal_channel"]
    assert not flags["native_control_mode"]
    assert not flags["native_stage"]


def test_generic_channel_names_and_parser_do_not_establish_lineage_or_hardware():
    payload = {"brewdata": {"parser": "Parsers::Beanconqueror"}}
    flags = v.field_presence({"hydraulic": {
        "mass_flow_from_scale__kg_per_s": [0.001], "weight__kg": [0.020],
    }}, payload)
    assert v.format_family(payload) == "VISUALIZER_BEANCONQUEROR"
    assert flags["flow_weight_channel"] and flags["weight_channel"]
    assert not flags["native_scale"] and not flags["reported_machine"]
    assert v.format_family({"brewdata": {"samples": [1, 2]}}) == "UNRESOLVED"
    with pytest.raises(ValueError, match="differs"):
        v.format_family({"brewdata": {"parser": "Parsers::Gaggimate"}})


def test_presence_does_not_drop_zero_or_inspect_array_values():
    assert v.present(0) and v.present(-1) and v.present(False)
    assert v.present([None])
    assert not v.present(None) and not v.present([])


def test_disclosure_checks_both_cells_and_user_linkage():
    all_users = set(range(30))
    assert v.publishable_count(0, set(), 100, all_users)
    assert v.publishable_count(100, all_users, 100, all_users)
    assert v.publishable_count(50, set(range(15)), 100, all_users)
    assert not v.publishable_count(19, set(range(15)), 100, all_users)
    assert not v.publishable_count(50, set(range(9)), 100, all_users)
    assert not v.publishable_count(81, set(range(15)), 100, all_users)
    assert not v.publishable_count(50, set(range(25)), 100, all_users)
    assert not v.publishable_count(100, set(), 100, set())


def test_metadata_audit_aligns_one_canonical_record_without_outcomes(monkeypatch):
    class Forbidden(dict):
        def get(self, *args):
            raise AssertionError("Outcomes must not be accessed")

    rows = [dict(id=str(i), updated_at=1, hashed_user=str(i), machine=None,
                 outcomes=Forbidden()) for i in range(30)]

    class Snapshot:
        def latest(self):
            return iter(rows)

    receipt = {"integrity": dict(n_revisions=0, n_same_timestamp_conflicts=0,
                                 n_logical_records=30)}
    monkeypatch.setattr(v, "authenticate", lambda *args: (Snapshot(), receipt))
    bronze = [dict(id=r["id"], updated_at=1, payload={}) for r in rows]
    monkeypatch.setattr(v, "iter_bronze", lambda cfg: iter(bronze))
    result = v.audit(Path("unused"), Path("unused"))
    assert not result["turnover_calculated"]
    assert all(r["present_records"] == 0 for r in result["coverage"]
               if r["field"] == "reported_machine")
    assert "hashed_user" not in json.dumps(result)
    bronze.append(bronze[0])
    with pytest.raises(ValueError, match="Duplicate"):
        v.audit(Path("unused"), Path("unused"))

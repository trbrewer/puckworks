"""Offline sampling, request-boundary and privacy checks; no live API."""

import json
from types import SimpleNamespace

import pytest

from puckworks.analysis import vis_metadata_probe_001 as p
from puckworks.analysis import vis_metadata_probe_001_report as report


def test_draw_fixed_balanced_unique_and_order_independent():
    groups = {g: [f"synthetic-{g}-{i}" for i in range(400)] for g in p.GROUPS}
    selected = p.draw(groups)
    assert selected == p.draw({g: list(reversed(v)) for g, v in groups.items()})
    assert len(selected) == len(set(selected)) == 300
    assert [sum(g == group for g, _ in selected) for group in p.GROUPS] == [150, 150]


class FakeSession:
    def __init__(self, status=200):
        self.calls = 0
        self.status = status

    def get(self, url, **kwargs):
        assert kwargs["allow_redirects"] is False
        self.calls += 1
        return SimpleNamespace(status_code=self.status, headers={})


@pytest.mark.parametrize("status", [401, 403, 429, 302, 500])
def test_refusal_stops_without_recording_url_or_body(tmp_path, status):
    fake = FakeSession(status)
    bounded = p.BoundedSession(fake, tmp_path)
    with pytest.raises(p.ProbeStopped):
        bounded.get("https://visualizer.coffee/api/shots/synthetic-sensitive-id")
    ledger = (tmp_path / "REQUESTS.jsonl").read_text()
    assert "sensitive" not in ledger and json.loads(ledger)["status"] == status
    assert fake.calls == 1


def test_cap_pages_and_profile_scope_enforced_before_network(tmp_path):
    fake = FakeSession()
    bounded = p.BoundedSession(fake, tmp_path)
    with pytest.raises(p.ListingComplete):
        bounded.get("https://visualizer.coffee/api/shots",
                    params=dict(page=4, items=100, sort="start_time"))
    with pytest.raises(p.ProbeStopped):
        bounded.get("https://visualizer.coffee/api/shots/synthetic/profile", params={"format": "csv"})
    bounded.count = p.MAX_REQUESTS
    with pytest.raises(p.ProbeStopped, match="ceiling"):
        bounded.get("https://visualizer.coffee/api/shots/synthetic")
    assert fake.calls == 0


def test_only_field_paths_types_and_salted_linkage_persist():
    raw = dict(id="SENSITIVE_SHOT", user_id="SENSITIVE_USER", profile_title="SENSITIVE_TITLE",
               metadata={"unknown personal key": "SENSITIVE_TEXT"},
               brewdata={"parser": "Parsers::Gaggimate"},
               data={"espresso_flow_weight": [123.456], "espresso_weight": [789.123]},
               profile_url="https://visualizer.coffee/api/shots/SENSITIVE_SHOT/profile")
    cfg = p.vh.HarvestConfig(salt="synthetic-test-salt")
    summary = p.summarize(raw, cfg)
    text = json.dumps(summary)
    assert not any(value in text for value in ("SENSITIVE", "123.456", "789.123", "personal"))
    assert summary["format"] == "VISUALIZER_GAGGIMATE"
    assert summary["machine"] == "UNKNOWN"
    assert summary["full_qualification"] == "UNKNOWN_NOT_EVALUATED"
    assert "profile_title" in summary["fields"]
    assert "profile_title" not in summary["after_privacy_fields"]


def test_profile_control_fields_do_not_certify_active_control():
    fields = p.field_types({"steps": [{"pump": "pressure", "limiter": {"flow": None}},
                                     {"pump": "flow", "flow": -1}, {"flow": 0}]})
    assert fields["steps[].pump"] == ["str"]
    assert fields["steps[].limiter.flow"] == ["null"]
    assert fields["steps[].flow"] == ["int"]


def test_report_suppresses_small_fields_and_complements():
    rows = [dict(status="AVAILABLE", user_token=str(i), fields={}) for i in range(40)]
    assert report.releasable(rows, [])
    assert report.releasable(rows, rows)
    assert report.releasable(rows, rows[:20])
    assert not report.releasable(rows, rows[:19])
    assert not report.releasable(rows, rows[:21])
    assert not report.releasable([dict(user_token="one") for _ in range(40)], [])


def test_profile_not_requested_is_not_absent_at_source():
    rows = [dict(status="AVAILABLE", user_token=str(i), fields={}) for i in range(40)]
    result = report.availability(rows, "B", "ALL", "ALL")
    steps = next(r for r in result if r["native_field"] == "PROFILE.steps")
    assert steps["absent_at_current_source"] == 0
    assert steps["profile_not_returned_or_not_requested"] == 40


def test_current_privacy_drop_is_not_automatically_historical_loss():
    rows = [dict(status="AVAILABLE", user_token=str(i), fields={"profile_title": ["str"]},
                 after_privacy_fields={}, old_fields={}) for i in range(40)]
    result = report.availability(rows, "A", "ALL", "ALL")
    title = next(r for r in result if r["native_field"] == "profile_title")
    assert title["privacy_dropped_now"] == 40
    assert title["historically_confirmed_drop"] == 0
    assert title["new_at_source_or_historical_loss_unknown"] == 40
    for row in rows:
        row["old_profile_present"] = True
    title = next(r for r in report.availability(rows, "A", "ALL", "ALL")
                 if r["native_field"] == "profile_title")
    assert title["historically_confirmed_drop"] == 40
    assert title["new_at_source_or_historical_loss_unknown"] == 0


def test_nested_counts_cannot_reveal_one_shot_by_subtraction():
    rows = [dict(status="AVAILABLE", user_token=str(i), fields={}) for i in range(100)]
    for row in rows[:80]:
        row["fields"]["data"] = ["dict"]
    for row in rows[:79]:
        row["fields"]["data.espresso_weight"] = ["list"]
    output = report.availability(rows, "B", "ALL", "ALL")
    for path in ("data", "data.espresso_weight"):
        assert next(r for r in output if r["native_field"] == path)["present"] == "SUPPRESSED"


def test_omitted_sentinels_and_limiter_fields_are_unknown_not_absent():
    rows = [dict(status="AVAILABLE", user_token=str(i), fields={}) for i in range(40)]
    output = report.availability(rows, "B", "ALL", "ALL")
    for path in report.NOT_CAPTURED_PATHS:
        item = next(r for r in output if r["native_field"] == path)
        assert item["absent_at_current_source"] == "NOT_CAPTURED"
        assert item["present"] == "NOT_CAPTURED"

"""Offline sampling, request-boundary and privacy checks; no live API."""

import json
from types import SimpleNamespace

import pytest

from puckworks.analysis import vis_metadata_probe_001 as p


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

"""Guard the reconciled present-state truth (PV-05 Section 1) against regressing to superseded wording.

These checks target only PRESENT-STATE summaries and the machine status source — never archival sprint
records or historical review notes. They fail if the planning docs slide back to "nothing is built",
PV-03 not-started, a stale Guided-Pull milestone, or the bundled-shot fixture lane shown as unblocked.
"""
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]


def _items():
    d = json.loads((_ROOT / "docs" / "status" / "current.json").read_text(encoding="utf-8"))
    return {it["id"]: it for it in d["items"]}


def test_current_json_reflects_shipped_public_value():
    items = _items()
    # PV-03 shipped -> complete, not active/not-started
    assert items["pv03-flat-valley-interactive"]["state"] == "complete"
    # PV-05 is the active public-value lane; PV-04 is queued next
    assert items["pv05-model-composition"]["state"] == "active"
    assert items["pv04-analysis-autopsy"]["state"] in ("proposed", "active")
    # Guided Pull is released and awaiting signed-out human acceptance (still active, not milestone-B)
    gp = items["guided-espresso-pull"]
    assert gp["state"] == "active"
    assert "v0.3.0" in gp["title"] or "v0.3.0" in (gp["acceptance_evidence"] or "")
    assert "milestone b" not in (gp["title"] + (gp["acceptance_evidence"] or "")).lower()


def test_bundled_shot_fixture_lane_stays_blocked():
    # the evidence-aware bundled-shot explanation lane (issue #32) must NOT be shown as unblocked
    ebe = _items()["evidence-aware-explanation-bundle"]
    assert ebe["state"] == "blocked"
    assert ebe["issue_or_pr"] == "#32"
    assert ebe["resume_trigger"], "a blocked lane must name what would unblock it"


def test_sprints_present_state_not_all_unbuilt():
    txt = (_ROOT / "docs" / "SPRINTS.md").read_text(encoding="utf-8")
    # the retired blanket present-state claim must be gone
    assert "Nothing here is built yet" not in txt
    # the present-state summary now records the shipped items
    assert "PV-00" in txt and "complete" in txt
    assert "live" in txt.lower()


def test_public_value_exec_summary_uses_matched_endpoint_reading():
    txt = (_ROOT / "docs" / "PUBLIC_VALUE.md").read_text(encoding="utf-8")
    # the superseded transfer-failure framing is retired from the executive summary
    assert "fails badly at other grinds" not in txt
    assert "25-49%" not in txt and "25–49%" not in txt
    # the corrected reading + delivery status are present
    assert "practically non-identifiable" in txt
    assert "live" in txt.lower() and "PV-05" in txt


def test_changelog_next_feature_is_pv05():
    txt = (_ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    dev = txt.split("## 0.4.0.dev0", 1)[1].split("## 0.3.0", 1)[0]
    assert 'first up: the PV-03' not in dev
    assert "PV-05" in dev and "live" in dev.lower()

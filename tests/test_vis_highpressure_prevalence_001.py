"""Synthetic-only boundaries, access caps and release tests for the bounded probe."""
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import vis_highpressure_prevalence_001 as probe
from puckworks.analysis import vis_highpressure_prevalence_001_report as report


def trace(end=70, pressure=11., onset=0):
    t = np.arange(end + 1, dtype=float)
    p = np.full(len(t), pressure * 1e5)
    w = np.where(t < onset, 0., (t - onset + 2) / 1000)
    return t, p, w


@pytest.mark.parametrize("p,expected", [(10, False), (10.01, True), (11, True), (12, True)])
def test_strict_threshold(p, expected):
    r = probe.measure(*trace(10, p))
    assert r["events"]["gt10_late0"] == expected
    assert r["events"]["gt11_late0"] == (p > 11)
    assert not r["events"]["gt12_late0"]


@pytest.mark.parametrize("end,late40,late60", [(40, False, False), (41, True, False),
                                             (60, True, False), (61, True, True)])
def test_late_strict_boundary(end, late40, late60):
    r = probe.measure(*trace(end))
    assert r["events"]["gt10_late40"] == late40
    assert r["events"]["gt10_late60"] == late60


def test_ten_seconds_and_onset_relative():
    r = probe.measure(*trace(60, onset=50))
    assert r["events"]["gt10_late0"]
    assert not r["events"]["gt10_late40"]
    assert probe.measure(*trace(59, onset=50))["status"] == "short_support"
    t, p, w = trace(60, onset=50)
    w[49] = .001  # equality is not onset
    assert probe.measure(t, p, w)["events"] == r["events"]


def test_crossings_and_irregular_time_not_sample_count():
    t = np.r_[0., 2., np.arange(3., 13.), 14.]
    p = np.r_[9., 11., np.full(10, 11.), 9.] * 1e5
    w = (t + 2) / 1000
    assert probe.measure(t, p, w)["events"]["gt10_late0"]  # crossing 1 to 13
    p[2:-2] = 10.1e5
    assert probe.measure(t, p, w)["events"]["gt10_late0"]
    t = t * .6
    assert not probe.measure(t, p, w)["events"]["gt10_late0"]


def test_equal_threshold_splits_and_spikes_do_not_count():
    t, p, w = trace(18)
    p[9] = 10e5
    assert not probe.measure(t, p, w)["events"]["gt10_late0"]
    p[:] = 9e5
    p[8:10] = 13e5
    assert not any(probe.measure(t, p, w)["events"].values())


@pytest.mark.parametrize("last,expected", [(12., True), (11.98, False)])
def test_interpolated_run_length_at_ten_seconds(last, expected):
    t = np.r_[np.arange(0., 12., 2.), last]
    p = np.r_[9., np.full(5, 11.), 9.] * 1e5
    w = (t + 2) / 1000
    assert probe.measure(t, p, w)["events"]["gt10_late0"] == expected


def test_late_stretch_need_not_start_after_late_boundary():
    t, p, w = trace(45, 9)
    p[30:] = 11e5
    r = probe.measure(t, p, w)
    assert r["events"]["gt10_late40"]
    assert not r["events"]["gt10_late60"]


@pytest.mark.parametrize("defect", ["gap", "nan_p", "nan_w", "negative_p"])
def test_invalid_support_is_never_bridged(defect):
    t, p, w = trace(18)
    if defect == "gap":
        t[9:] += 3
    elif defect == "nan_p":
        p[9] = np.nan
    elif defect == "nan_w":
        w[9] = np.nan
    else:
        p[9] = -1
    r = probe.measure(t, p, w)
    assert r["status"] == "short_support"
    assert not any(r["events"].values())


def test_reset_flag_does_not_repair_or_erase_inclusive_indicator():
    t, p, w = trace(70)
    w[30:] -= .0061
    r = probe.measure(t, p, w)
    assert r["reset_like"]
    assert r["events"]["gt10_late60"]
    w = np.full(len(t), .02)
    w[30:] = .015
    assert not probe.measure(t, p, w)["reset_like"]


def test_invalid_timestamps_and_missing_channels():
    t, p, w = trace()
    assert probe.measure(t, p[:-1], w)["status"] == "channel_lengths"
    t[4] = t[3]
    assert probe.measure(t, p, w)["status"] == "timestamps"
    assert probe.measure(*trace(10),)["onset_left_censored"]
    t, p, w = trace()
    w[:] = .001
    assert probe.measure(t, p, w)["status"] == "no_delivery_onset"


def test_sample_dedup_and_snapshot_exclusion():
    seen = set()
    selected, counts = probe.select_rows([{"id": s} for s in ("old", "a", "a", None)],
                                         {"old"}, seen)
    assert selected == ["a"]
    assert counts == dict(duplicates=1, snapshot_overlap=1, missing_id=1)
    selected, counts = probe.select_rows([{"id": s} for s in ("a", "b", "old")],
                                         {"old"}, seen)
    assert selected == ["b"] and counts["duplicates"] == 2


class FakeHTTP:
    def __init__(self, status=200):
        self.status = status
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        return SimpleNamespace(status_code=self.status, headers={"Retry-After": "5"})


def test_request_allowlist_and_caps(tmp_path):
    http = FakeHTTP()
    session = probe.BoundedSession(http, tmp_path)
    url = "https://visualizer.coffee/api/shots"
    for p in range(1, 21):
        session.get(url, params=dict(page=p, items=100, sort="start_time"))
    with pytest.raises(probe.ProbeStopped):
        session.get(url, params=dict(page=21, items=100, sort="start_time"))
    session.allowed = {"fixture"}
    session.get(url + "/fixture")
    with pytest.raises(probe.ProbeStopped):
        session.get(url + "/fixture")
    with pytest.raises(probe.ProbeStopped):
        session.get(url + "/not-selected")
    session.count = 2020
    with pytest.raises(probe.ProbeStopped):
        session.get(url)
    assert http.calls == 21
    text = (tmp_path / "REQUESTS.jsonl").read_text()
    assert "fixture" not in text and "https" not in text
    with pytest.raises(FileExistsError):
        probe.BoundedSession(http, tmp_path)


@pytest.mark.parametrize("status", [301, 401, 403, 429, 500])
def test_refusal_stops_without_retry(tmp_path, status):
    http = FakeHTTP(status)
    session = probe.BoundedSession(http, tmp_path)
    with pytest.raises(probe.ProbeStopped):
        session.get("https://visualizer.coffee/api/shots",
                    params=dict(page=1, items=100, sort="start_time"))
    assert http.calls == 1
    assert json.loads((tmp_path / "REQUESTS.jsonl").read_text())["status"] == status


def synthetic_rows(n=200):
    return [dict(shot_token=f"synthetic-{i}", user_token=f"synthetic-user-{i}",
                 status="evaluable", reset_like=False, onset_left_censored=False,
                 gap=False, incomplete_support=False, profile_title="Fixture profile",
                 events={f"gt{p}_late{t}": False for p in (10, 11, 12) for t in (0, 40, 60)})
            for i in range(n)]


def test_clopper_pearson_endpoints_and_known_interval():
    assert report.exact_interval(0, 100)[0] == 0
    assert report.exact_interval(100, 100)[1] == 1
    assert report.exact_interval(0, 100)[1] == pytest.approx(1 - .025 ** .01)
    assert report.exact_interval(50, 100) == pytest.approx((.3983211295, .6016788705))


def test_linked_subtraction_hides_safe_marginal_with_rare_difference():
    rows = synthetic_rows()
    d = report.Disclosure(rows)
    assert d.consider("late", range(40))
    assert not d.consider("any", range(41))
    assert d.consider("any_safe_difference", range(60))


def test_higher_order_intersection_and_user_overlap_are_checked():
    rows = synthetic_rows(80)
    d = report.Disclosure(rows)
    assert d.consider("a", range(40))
    assert d.consider("b", range(20, 60))
    # Marginal c and each pairwise difference are safe; the joint remainder is one.
    assert not d.consider("c", set(range(1, 20)) | set(range(40, 60)))
    rows = synthetic_rows(100)
    for i in range(50):
        rows[i]["user_token"] = f"synthetic-user-{i % 10}"
    for i in range(50, 100):
        rows[i]["user_token"] = f"synthetic-user-{i % 11}"
    assert not report.partition_safe(rows, [set(range(50))])  # one exclusive user


def test_suppressed_estimates_and_profile_labels_stay_withheld():
    rows = synthetic_rows()
    for r in rows[:5]:
        r["events"]["gt10_late0"] = True
        r["profile_title"] = "rare-title@example.test"
    prevalence, profiles, _ = report.release_tables(rows)
    chosen = next(r for r in prevalence if r.get("threshold_bar") == "10"
                  and r.get("late_s") == "0" and r["analysis"] == "primary")
    assert chosen["events"] == report.WITHHELD
    for field in ("ci95_lower", "ci95_upper", "prevalence", "qualifying_users",
                  "projected_shots_per_10000", "projected_users_per_10000"):
        assert chosen[field] == report.WITHHELD
    assert "rare-title" not in json.dumps(profiles)
    assert profiles[0]["shots"] == report.WITHHELD


def test_safe_counts_projections_and_explicit_title_approval():
    rows = synthetic_rows()
    for r in rows[:40]:
        r["events"]["gt10_late0"] = r["events"]["gt10_late40"] = True
    prevalence, profiles, d = report.release_tables(rows, ["Fixture profile"])
    r = next(r for r in prevalence if r.get("threshold_bar") == "10"
             and r.get("late_s") == "40" and r["analysis"] == "primary"
             and r["denominator"] == "all_selected")
    assert r["events"] == r["qualifying_users"] == 40
    assert r["projected_shots_per_10000"] == r["projected_users_per_10000"] == 2000
    conditional = next(r for r in prevalence if r.get("threshold_bar") == "10"
                       and r.get("late_s") == "40" and r["analysis"] == "primary"
                       and r["denominator"] == "primary_evaluable")
    assert conditional["projected_shots_per_10000"] == "NA"
    assert profiles == [dict(profile_title="Fixture profile", shots=40, distinct_users=40,
                             release_status="RELEASED")]
    assert report.partition_safe(rows, d.memberships)


def test_commanded_pressure_cannot_enter_measurement():
    cfg = probe.vh.HarvestConfig(out_dir="unused", salt="synthetic")
    t, p, w = trace(70, 9)
    raw = dict(timeframe=t.tolist(), data=dict(espresso_pressure=(p / 1e5).tolist(),
               espresso_weight=(w * 1000).tolist(), espresso_pressure_goal=[15] * len(t)))
    h = probe.vh.normalize_shot(raw, cfg)["hydraulic"]
    r = probe.measure(h["time__s"], h["pressure__Pa"], h["weight__kg"])
    assert not any(r["events"].values())


def test_request_audit_handles_network_stop_and_checks_frozen_order(tmp_path):
    ledger = [dict(kind="listing", status=200, started_utc="2026-01-01T00:00:00+00:00",
                   ended_utc="2026-01-01T00:00:01+00:00", retry_after=None),
              dict(kind="detail", status="network_error", started_utc="2026-01-01T00:00:04+00:00",
                   ended_utc="2026-01-01T00:00:05+00:00")]
    (tmp_path / "REQUESTS.jsonl").write_text("\n".join(json.dumps(r) for r in ledger) + "\n")
    run = dict(snapshot_unchanged=True, api_attempts=2)
    sample = dict(selected=["synthetic-a", "synthetic-b"], snapshot_overlap_after_exclusion=0,
                  frozen_utc="2026-01-01T00:00:02+00:00")
    result = report.audit_requests(tmp_path, run, sample, [])
    assert result["statuses"] == {"200": 1, "network_error": 1}
    assert result["retry_after_responses"] == 0
    with pytest.raises(AssertionError):
        report.audit_requests(tmp_path, run, sample, [dict(shot_token="synthetic-b")])

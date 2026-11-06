"""Synthetic-only boundaries, access caps and release tests for the bounded probe."""
import json
from types import SimpleNamespace

import numpy as np
import pytest

from puckworks.analysis import vis_highpressure_prevalence_001 as probe


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

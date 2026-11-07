"""One bounded descriptive probe. No model imports, fitting, or scoring."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace

import numpy as np

from puckworks.data.corpus_freeze import _source_state
from puckworks.lib import visualizer_harvest as vh

PLAN = "docs/research/VIS_HIGHPRESSURE_PREVALENCE_001/PLAN.md"
SNAPSHOT_SHA = "6769656c8555d940bf79a2243a784c38b63066d3fe231227628667d251ba4d5b"
MAX_PAGES, MAX_SHOTS, MAX_REQUESTS = 20, 2000, 2020
THRESHOLDS = (10, 11, 12)
LATE = (0, 40, 60)


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def token(salt, value):
    return hashlib.sha256((salt + "|probe-shot|" + str(value)).encode()).hexdigest()[:32]


def measure(time_s, pressure_pa, weight_kg):
    """Mirror empirical onset/support/reset rules; scan linear achieved pressure.

    Prediction-specific calibration/score eligibility is deliberately absent.
    A boundary exactly at threshold splits strict-above connected intervals.
    """
    arrays = []
    for values in (time_s, pressure_pa, weight_kg):
        arrays.append(np.array([np.nan if x is None else x for x in values], dtype=float))
    t, p, w = arrays
    empty = {f"gt{q}_late{s}": False for q in THRESHOLDS for s in LATE}
    out = dict(status="channel_lengths", reset_like=None, onset_left_censored=None,
               gap=None, incomplete_support=None, events=empty)
    if len(t) < 2 or len(p) != len(t) or len(w) != len(t):
        return out
    if not np.isfinite(t).all() or np.any(np.diff(t) <= 0):
        return dict(out, status="timestamps")
    wg = w * 1000
    onset_indices = np.flatnonzero(np.isfinite(wg) & (wg > 1.0))
    if not len(onset_indices):
        return dict(out, status="no_delivery_onset")
    onset = t[onset_indices[0]]
    valid = np.isfinite(w) & np.isfinite(p) & (p >= 0)
    out.update(reset_like=bool(np.any(np.diff(wg) < -5)),
               onset_left_censored=bool(onset_indices[0] == 0),
               gap=bool(np.any(np.diff(t) > 2)),
               incomplete_support=bool(not valid.all() or np.any(np.diff(t) > 2)))
    edges = np.flatnonzero(~valid[:-1] | ~valid[1:] | (np.diff(t) > 2)) + 1
    bounds = sorted({0, len(t), *edges.tolist()})
    supported = False
    for a, b in zip(bounds[:-1], bounds[1:]):
        if b - a < 2 or not valid[a:b].all():
            continue
        start = max(float(t[a]), float(onset))
        if t[b - 1] - start < 10 - 1e-9:
            continue
        supported = True
        tt = np.r_[start, t[a:b][t[a:b] > start]]
        pp = np.interp(tt, t[a:b], p[a:b]) / 1e5
        for threshold in THRESHOLDS:
            runs = []
            run = None
            for i in range(len(tt) - 1):
                x, y, px, py = tt[i], tt[i + 1], pp[i], pp[i + 1]
                if px <= threshold and py <= threshold:
                    if run is not None:
                        runs.append(run)
                        run = None
                    continue
                left, right = x, y
                if px <= threshold:
                    left = x + (threshold - px) * (y - x) / (py - px)
                if py <= threshold:
                    right = x + (threshold - px) * (y - x) / (py - px)
                if run is not None and px > threshold and abs(run[1] - left) < 1e-9:
                    run[1] = right
                else:
                    if run is not None:
                        runs.append(run)
                    run = [left, right]
                if py <= threshold:
                    runs.append(run)
                    run = None
            if run is not None:
                runs.append(run)
            for left, right in runs:
                if right - left >= 10 - 1e-9:
                    for late in LATE:
                        if late == 0 or right - onset > late:
                            out["events"][f"gt{threshold}_late{late}"] = True
    return dict(out, status="evaluable" if supported else "short_support")


def select_rows(rows, existing, seen):
    """Deduplicate listing IDs before snapshot exclusion, never replenish."""
    selected = []
    counts = dict(duplicates=0, snapshot_overlap=0, missing_id=0)
    for row in rows:
        shot = row.get("id")
        if not isinstance(shot, str) or not shot:
            counts["missing_id"] += 1
        elif shot in seen:
            counts["duplicates"] += 1
        else:
            seen.add(shot)
            if shot in existing:
                counts["snapshot_overlap"] += 1
            else:
                selected.append(shot)
    return selected, counts


class ProbeStopped(RuntimeError):
    """Only controlled reasons; never include response bodies or private URLs."""


class ShotUnavailable(RuntimeError):
    pass


class BoundedSession:
    def __init__(self, session, private):
        self.session = session
        self.ledger = private / "REQUESTS.jsonl"
        self.ledger.touch(exist_ok=False)
        self.count = 0
        self.pages = set()
        self.allowed = set()
        self.fetched = set()

    def _bounded_prevalence_get(self, url, params=None, timeout=None):
        if self.count >= MAX_REQUESTS:
            raise ProbeStopped("API attempt ceiling")
        prefix = "https://visualizer.coffee/api/shots"
        if url == prefix:
            page = (params or {}).get("page")
            if (page not in range(1, MAX_PAGES + 1) or page in self.pages
                    or params != dict(page=page, items=100, sort="start_time")):
                raise ProbeStopped("Listing outside frozen scope")
            self.pages.add(page)
            kind = "listing"
        elif url.startswith(prefix + "/") and params is None:
            shot = url[len(prefix) + 1:]
            if shot not in self.allowed or shot in self.fetched or len(self.fetched) >= MAX_SHOTS:
                raise ProbeStopped("Detail outside frozen sample")
            self.fetched.add(shot)
            kind = "detail"
        else:
            raise ProbeStopped("Endpoint outside scope")
        self.count += 1
        event = dict(attempt=self.count, kind=kind, started_utc=utc())
        try:
            response = self.session.get(url, params=params, timeout=timeout, allow_redirects=False)
        except vh._requests().RequestException:
            event.update(status="network_error", ended_utc=utc())
            with self.ledger.open("a") as stream:
                stream.write(json.dumps(event) + "\n")
            raise ProbeStopped("Network failure; no retry") from None
        event.update(status=response.status_code, ended_utc=utc(),
                     retry_after=response.headers.get("Retry-After"))
        with self.ledger.open("a") as stream:
            stream.write(json.dumps(event) + "\n")
        if kind == "detail" and response.status_code in (404, 410):
            raise ShotUnavailable(f"HTTP {response.status_code}")
        if response.status_code != 200:
            raise ProbeStopped(f"API stop: HTTP {response.status_code}")
        return response

    get = _bounded_prevalence_get


def verify_snapshot(root):
    state = _source_state(root)
    if state["aggregate_sha256"] != SNAPSHOT_SHA or len(state["files"]) != 465:
        raise ProbeStopped("Snapshot identity differs")
    existing = vh.latest_index_rows(SimpleNamespace(out_dir=root))
    if len(existing) != 23169:
        raise ProbeStopped("Snapshot logical count differs")
    return set(existing), dict(aggregate_sha256=SNAPSHOT_SHA, files=465, logical_records=23169)


def probe(root, private):
    repo = Path(__file__).resolve().parents[2]
    if private.resolve().is_relative_to(repo):
        raise ValueError("Private evidence must be outside Git")
    committed = subprocess.check_output(["git", "show", "HEAD:" + PLAN], cwd=repo)
    if committed != (repo / PLAN).read_bytes():
        raise ProbeStopped("PLAN must be committed before requests")
    existing, receipt = verify_snapshot(root)
    salt = (root.parent / ".harvest_salt").read_text().strip()
    if not salt:
        raise ProbeStopped("Missing production salt")
    private.mkdir(mode=0o700, parents=True, exist_ok=True)
    cfg = vh.HarvestConfig(out_dir=private, salt=salt, max_req_per_min=18)
    http = vh._requests().Session()
    http.trust_env = False  # No ambient netrc credentials or authentication.
    http.headers.update({"Accept": "application/json",
                         "User-Agent": "Puckworks-prevalence-probe/1.0 (permissioned research)"})
    session = BoundedSession(http, private)
    limiter = vh._RateLimiter(18)
    report = dict(started_utc=utc(), status="RUNNING", snapshot=receipt,
                  plan_sha256=sha(repo / PLAN), code_sha256=sha(__file__),
                  code_commit=subprocess.check_output(["git", "rev-parse", "HEAD"],
                                                      cwd=repo, text=True).strip(),
                  listing_entries=0, duplicates=0, snapshot_overlap=0, missing_id=0,
                  selected=0, processed=0)
    selected, seen = [], set()
    try:
        for page in range(1, MAX_PAGES + 1):
            data = vh._get(cfg, session, limiter, "/shots",
                           params=dict(page=page, items=100, sort="start_time"))
            rows = data.get("data", data) if isinstance(data, dict) else data
            if not isinstance(rows, list) or len(rows) > 100 or not all(
                    isinstance(r, dict) for r in rows):
                raise ProbeStopped("Unexpected listing shape")
            report["listing_entries"] += len(rows)
            if report["listing_entries"] > MAX_SHOTS:
                raise ProbeStopped("Listing sample cap")
            new, counts = select_rows(rows, existing, seen)
            selected.extend(new)
            for key, value in counts.items():
                report[key] += value
            del data, rows
            # The recorded page size alone determines end of listing.
            if len(new) + sum(counts.values()) == 0:
                break
        if len(selected) > MAX_SHOTS or set(selected) & existing:
            raise ProbeStopped("Sample cap or snapshot dedup failed")
        session.allowed = set(selected)
        report["selected"] = len(selected)
        manifest = dict(frozen_utc=utc(), selected=[token(salt, s) for s in selected],
                        snapshot_overlap_after_exclusion=0)
        (private / "SAMPLE.json").write_text(json.dumps(manifest, indent=2) + "\n")
        for shot in selected:
            record = dict(shot_token=token(salt, shot))
            try:
                raw = vh.fetch_shot(cfg, shot, _session=session, _limiter=limiter)
                if not isinstance(raw, dict) or raw.get("id") != shot:
                    raise ProbeStopped("Unexpected detail identity/shape")
                # Read only the needed categories, then use the shared SI normalizer
                # on an allowlist; never persist raw responses or unrelated free text.
                title = raw.get("profile_title")
                record.update(user_token=vh.hash_user(cfg, raw.get("user_id")),
                              profile_title=title if isinstance(title, str) and title else None)
                data = raw.get("data") or {}
                if not isinstance(data, dict):
                    data = {}
                narrow = dict(timeframe=raw.get("timeframe"), data={k: data[k] for k in (
                    "timeframe", "espresso_pressure", "espresso_weight") if k in data})
                norm = vh.normalize_shot(narrow, cfg,
                                         hashed_user_override=record["user_token"])
                h = norm["hydraulic"]
                record.update(measure(h.get("time__s", []), h.get("pressure__Pa", []),
                                      h.get("weight__kg", [])))
                del raw, data, narrow, norm, h
            except ShotUnavailable as exc:
                record.update(status="unavailable", reason=str(exc), user_token=None,
                              profile_title=None, events={})
            with (private / "MEASURES.jsonl").open("a") as stream:
                stream.write(json.dumps(record, allow_nan=False) + "\n")
            report["processed"] += 1
            if report["processed"] % 100 == 0:
                print(json.dumps(dict(processed=report["processed"],
                                      api_attempts=session.count)), flush=True)
        report["status"] = "COMPLETED"
    except ProbeStopped as exc:
        report.update(status="STOPPED", reason=str(exc))
    except Exception:
        report.update(status="STOPPED", reason="Unexpected processing failure; inspect offline")
        raise ProbeStopped(report["reason"]) from None
    finally:
        report.update(ended_utc=utc(), api_attempts=session.count,
                      rate_wait_seconds=limiter.total_wait_s)
        _, after = verify_snapshot(root)
        report["snapshot_unchanged"] = after == receipt
        (private / "RUN.json").write_text(json.dumps(report, indent=2) + "\n")
        http.close()
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    probe(args.root, args.private)


if __name__ == "__main__":
    main()

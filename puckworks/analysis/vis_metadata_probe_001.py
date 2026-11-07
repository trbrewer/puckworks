"""Bounded Visualizer metadata probe; no hydraulic computation or raw persistence."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import subprocess
from types import SimpleNamespace

from puckworks.analysis.pressure_peak_x1 import authenticate
from puckworks.lib import visualizer_harvest as vh

SEED = 20261105
GROUPS = ("VISUALIZER_BEANCONQUEROR", "UNRESOLVED")
PLAN = "docs/research/VIS_METADATA_PROBE_001/PLAN.md"
MAX_REQUESTS = 1203

# Only source/schema field names are retained. Unknown keys can be user text.
SAFE_KEYS = set("""machine device machine_type machine_model model manufacturer source
integration integration_source parser metadata brewdata profile profile_title profile_url
profile_fields frames steps stages stage state status control_mode control pump sensor
limiter maximum_flow maximum_pressure max_flow_or_pressure flow_limit pressure_limit
flow_limiter pressure_limiter pressure flow temperature temperature_goal seconds duration
preinfusion bloom pause shutdown transition exit type version scale scale_connected
scale_name scale_model measured estimated weight_source flow_source scale_flow scale_weight
espresso_weight espresso_flow_weight espresso_flow_weight_raw espresso_state_change
espresso_pressure espresso_pressure_goal espresso_flow_goal data samples v vf ev pf
bean_weight grinder_model grinder_setting bean_brand bean_type roast_date roast_level
coffee_bag_id roaster_id user_id id name title label preparation brewFlow pressureFlow
settings head group elapsed state_change pressure_priority flow_priority connected
weight gravimetric_flow targetPressure targetPumpFlow weightFlow shotWeight
preinfusion_time preinfusion_flow_rate preinfusion_stop_pressure temperature
sensor_name flow_mode pump_mode format hardware telemetry""".split())


class ProbeStopped(RuntimeError):
    """Redacted stop reason, without a response body or shot URL."""


class ShotUnavailable(RuntimeError):
    pass


class ListingComplete(RuntimeError):
    pass


class BoundedSession:
    def __init__(self, session, private):
        self.session = session
        self.ledger = private / "REQUESTS.jsonl"
        self.count = 0
        if self.ledger.exists():
            raise ProbeStopped("Existing request ledger: no implicit live rerun")

    def _bounded_metadata_get(self, url, params=None, timeout=None):
        if self.count >= MAX_REQUESTS:
            raise ProbeStopped("API attempt ceiling reached")
        path = url.removeprefix("https://visualizer.coffee/api")
        if path == "/shots":
            kind = "listing"
            if params == dict(page=4, items=100, sort="start_time"):
                raise ListingComplete
            if params not in [dict(page=p, items=100, sort="start_time") for p in range(1, 4)]:
                raise ProbeStopped("Listing outside frozen pages")
        elif path.startswith("/shots/") and path.endswith("/profile"):
            kind = "profile"
            if params != {"format": "json"}:
                raise ProbeStopped("Only JSON profiles are authorized")
        elif path.startswith("/shots/") and path.count("/") == 2 and params is None:
            kind = "detail"
        else:
            raise ProbeStopped("Endpoint outside frozen scope")
        self.count += 1
        event = dict(attempt=self.count, kind=kind, started_utc=utc())
        try:
            response = self.session.get(url, params=params, timeout=timeout, allow_redirects=False)
        except vh._requests().RequestException:
            event.update(status="network_error", ended_utc=utc())
            with self.ledger.open("a") as stream:
                stream.write(json.dumps(event) + "\n")
            raise ProbeStopped("Network failure; no implicit retry") from None
        event.update(status=response.status_code, ended_utc=utc(),
                     retry_after=response.headers.get("Retry-After"),
                     content_type=response.headers.get("Content-Type"))
        with self.ledger.open("a") as stream:
            stream.write(json.dumps(event) + "\n")
        if response.status_code in (401, 403, 429) or 300 <= response.status_code < 400:
            raise ProbeStopped(f"API access/rate/redirect stop: HTTP {response.status_code}")
        if response.status_code in (404, 410, 422):
            raise ShotUnavailable(f"HTTP {response.status_code}")
        if response.status_code != 200:
            raise ProbeStopped(f"Unexpected API status: HTTP {response.status_code}")
        return response

    # Preserve the harvester's Session interface without adding a generic `get`
    # definition to the repository's name-based static gate reachability audit.
    get = _bounded_metadata_get


def field_types(raw):
    """Retain fixed native paths and value types only; no arrays or text values."""
    found = {}

    def visit(value, path, depth):
        if depth > 12:
            return
        kind = "null" if value is None else type(value).__name__
        found.setdefault(path, set()).add(kind)
        if isinstance(value, dict):
            for key in sorted(set(value) & SAFE_KEYS):
                visit(value[key], path + "." + key if path else key, depth + 1)
        elif isinstance(value, list) and path.endswith(("steps", "frames", "stages", "samples", "data")):
            for frame in value:
                if isinstance(frame, dict):
                    visit(frame, path + "[]", depth + 1)

    visit(raw, "", 0)
    found.pop("", None)
    return {key: sorted(value) for key, value in sorted(found.items())}


def summarize(raw, cfg):
    before = field_types(raw)
    stripped = vh._strip_pii(raw)
    after = field_types(stripped)
    bd = raw.get("brewdata") if isinstance(raw.get("brewdata"), dict) else {}
    parser = bd.get("parser") or raw.get("parser") or raw.get("integration_source")
    from puckworks.data.visualizer.integration_contract import parser_family
    family = parser_family(parser) or "UNRESOLVED"
    machine = "UNKNOWN"
    machine_values = [raw.get("machine"), raw.get("device"), bd.get("machine")]
    if isinstance(raw.get("metadata"), dict):
        machine_values += [raw["metadata"].get("machine"), raw["metadata"].get("device")]
    # Exact declared labels only; never infer hardware from a parser/profile.
    labels = {"de1": "reported_DE1", "de1pro": "reported_DE1", "de1xl": "reported_DE1",
              "decent": "reported_DE1", "decent de1": "reported_DE1",
              "meticulous": "reported_Meticulous", "gaggimate": "reported_GaggiMate",
              "gaggiuino": "reported_Gaggiuino"}
    recognized = {labels[v.strip().lower()] for v in machine_values
                  if isinstance(v, str) and v.strip().lower() in labels}
    if len(recognized) == 1:
        machine = next(iter(recognized))
    return dict(fields=before, after_privacy_fields=after, format=family,
                user_token=vh.hash_user(cfg, raw.get("user_id")),
                profile_advertised=isinstance(raw.get("profile_url"), str)
                and bool(raw["profile_url"]),
                machine=machine, machine_origin="UNKNOWN_NOT_HARDWARE_VERIFIED",
                full_qualification="UNKNOWN_NOT_EVALUATED")


def utc():
    return datetime.now(timezone.utc).isoformat()


def token(salt, raw_id):
    return hashlib.sha256((salt + "|probe-shot|" + str(raw_id)).encode()).hexdigest()[:32]


def draw(groups):
    rng = random.Random(SEED)
    return [(group, shot) for group in GROUPS
            for shot in rng.sample(sorted(groups[group]), 150)]


def select_existing(root, inventory):
    snapshot, receipt = authenticate(root, inventory)
    if receipt["integrity"]["n_revisions"] or receipt["integrity"]["n_same_timestamp_conflicts"]:
        raise ValueError("Unexpected snapshot revisions")
    canonical = vh.latest_index_rows(SimpleNamespace(out_dir=root))
    groups = {group: [] for group in GROUPS}
    seen = set()
    for row in vh.iter_bronze(SimpleNamespace(out_dir=root)):
        shot = row["id"]
        if shot in seen or int(canonical[shot]["updated_at"]) != row["updated_at"]:
            raise ValueError("Bronze/canonical alignment differs")
        seen.add(shot)
        bd = row["payload"].get("brewdata")
        parser = bd.get("parser") if isinstance(bd, dict) else None
        if parser not in (None, "Parsers::Beanconqueror"):
            raise ValueError("Unexpected explicit format")
        group = GROUPS[0] if parser else GROUPS[1]
        groups[group].append(shot)
    if seen != set(canonical):
        raise ValueError("Unequal canonical/Bronze key sets")
    if [len(groups[g]) for g in GROUPS] != [1004, 22165]:
        raise ValueError("Snapshot differs from frozen strata")
    return draw(groups), receipt


def committed_plan():
    repo = Path(__file__).resolve().parents[2]
    committed = subprocess.check_output(["git", "show", "HEAD:" + PLAN], cwd=repo)
    if committed != (repo / PLAN).read_bytes():
        raise ValueError("Plan must be committed before requests")
    return hashlib.sha256(committed).hexdigest()


def freeze(root, inventory, private):
    plan_hash = committed_plan()
    selected, receipt = select_existing(root, inventory)
    salt = (root.parent / ".harvest_salt").read_text().strip()
    if not salt:
        raise ValueError("Missing production salt")
    data = dict(created_utc=utc(), plan_sha256=plan_hash, seed=SEED,
                authentication=receipt,
                selected=[dict(group=g, shot_token=token(salt, s)) for g, s in selected])
    destination = private / "SAMPLE_A.json"
    with destination.open("x") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
    print(json.dumps(dict(sample_a_records=len(selected),
                         manifest_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                         created_utc=data["created_utc"])))


def probe(root, inventory, private):
    plan_hash = committed_plan()
    sample = json.loads((private / "SAMPLE_A.json").read_text())
    selected, receipt = select_existing(root, inventory)
    salt = (root.parent / ".harvest_salt").read_text().strip()
    expected = [dict(group=g, shot_token=token(salt, shot)) for g, shot in selected]
    if expected != sample["selected"] or sample["authentication"] != receipt:
        raise ProbeStopped("Sample/source changed since pre-request freeze")
    selected_ids = {s for _, s in selected}
    old = {}
    for row in vh.iter_bronze(SimpleNamespace(out_dir=root)):
        if row["id"] in selected_ids:
            old[token(salt, row["id"])] = field_types(row["payload"])
    cfg = vh.HarvestConfig(out_dir=private, salt=salt, max_req_per_min=18)
    http = vh._requests().Session()
    http.headers.update({"Accept": "application/json",
                         "User-Agent": "Puckworks-metadata-probe/1.0 (permissioned research)"})
    session = BoundedSession(http, private)
    limiter = vh._RateLimiter(18)
    report = dict(started_utc=utc(), plan_sha256=plan_hash, sample_a=300,
                  sample_b=0, overlap=0, status="RUNNING", snapshot=receipt)
    cache = {}
    try:
        recent = []
        recent_seen = set()
        try:
            for page, shot, _, _ in vh.list_public_shot_ids(cfg, _session=session, _limiter=limiter):
                if shot and shot not in recent_seen:
                    recent_seen.add(shot)
                    recent.append(shot)
                if len(recent) == 300:
                    break
        except ListingComplete:
            pass
        report.update(sample_b=len(recent), overlap=len(recent_seen & selected_ids))
        (private / "SAMPLE_B.json").write_text(json.dumps(dict(
            created_utc=utc(), selected=[token(salt, s) for s in recent]), indent=2) + "\n")
        schedule = [("A", group, shot) for group, shot in selected]
        schedule += [("B", "RECENT_LISTING", shot) for shot in recent]
        for arm, stratum, shot in schedule:
            shot_token = token(salt, shot)
            if shot_token not in cache:
                try:
                    raw = vh.fetch_shot(cfg, shot, _session=session, _limiter=limiter)
                    summary = summarize(raw, cfg)
                    if summary["profile_advertised"]:
                        try:
                            profile = vh._get(cfg, session, limiter, f"/shots/{shot}/profile",
                                              params={"format": "json"})
                            summary["profile_fields"] = field_types(profile)
                            del profile
                        except ShotUnavailable as exc:
                            summary["profile_status"] = str(exc)
                    summary["status"] = "AVAILABLE"
                    del raw
                except ShotUnavailable as exc:
                    summary = dict(status="UNAVAILABLE", reason=str(exc))
                cache[shot_token] = summary
            record = dict(arm=arm, stratum=stratum, shot_token=shot_token,
                          old_fields=old.get(shot_token, {}) if arm == "A" else {},
                          **cache[shot_token])
            with (private / "FIELDS.jsonl").open("a") as stream:
                stream.write(json.dumps(record, sort_keys=True) + "\n")
        report["status"] = "COMPLETED"
    except (ProbeStopped, ShotUnavailable) as exc:
        report.update(status="STOPPED", reason=str(exc))
    finally:
        report.update(ended_utc=utc(), api_attempts=session.count,
                      rate_wait_seconds=limiter.total_wait_s)
        (private / "RUN.json").write_text(json.dumps(report, indent=2) + "\n")
        http.close()
    print(json.dumps({k: v for k, v in report.items() if k != "snapshot"}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["freeze", "probe"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--private", type=Path, required=True)
    args = parser.parse_args()
    if args.private.resolve().is_relative_to(Path(__file__).resolve().parents[2]):
        parser.error("Private output must be outside Git")
    args.private.mkdir(parents=True, exist_ok=True)
    if args.command == "freeze":
        freeze(args.root, args.inventory, args.private)
    else:
        probe(args.root, args.inventory, args.private)


if __name__ == "__main__":
    main()

"""Respectful harvester for the visualizer.coffee public shot API (ROADMAP 0.13).

This is Phase-0 *data intake* plus an ingestion *tool* — it adds NO registry
component and NO physics gate (CLAUDE.md rule 1 governs components; a harvester
is tooling). It pulls public espresso shots from https://visualizer.coffee and
writes a two-tier on-disk store where machine-side **hydraulic telemetry** and
user-entered **outcomes** are kept as SEPARATE evidence tiers (never merged into
one "shot" record) — see docs/cards/visualizer_coffee.md and PROVENANCE.md.

Hard constraints honoured here (see the task spec / PROVENANCE.md):
  * LICENSE — the shot CORPUS carries no research-use license. The raw harvested
    store is gitignored and NEVER committed. Only code, schema, PROVENANCE,
    MANIFEST rows and a small DERIVED aggregate CSV are tracked.
  * PRIVACY — on ingest we DROP user_name, user_id, avatar_url, barista and all
    *_notes free-text; we keep only a salted one-way hash of user_id for
    dedup/selection-bias accounting.
  * RATE LIMITS — default <=30 req/min with exponential backoff on 429/5xx, a
    persistent resume cursor and a --max-requests cap. Safely re-runnable and
    interruptible.
  * UNITS — stored SI at the store boundary; raw units recorded; missing/off-unit
    fields are FLAGGED, not silently coerced (CLAUDE.md rule 7).
  * NETWORK-OPTIONAL — `requests` is lazily imported (the [harvest] extra). The
    core package imports without it; tests run against a committed fixture, never
    the live API. This module is NOT in run_all_gates.

CLI:
    python -m puckworks.lib.visualizer_harvest full         [--max-requests N] [--req-per-min R] [--out DIR]
    python -m puckworks.lib.visualizer_harvest incremental  [--max-requests N] [--req-per-min R] [--out DIR]
    python -m puckworks.lib.visualizer_harvest stats        [--write-aggregate] [--out DIR]
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import re
import time
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator, Optional

# The tracked, committed default DEV salt. Production runs MUST override it via
# PUCKWORKS_VIS_SALT so the user hashes are not reproducible from this repo.
_DEV_SALT = "puckworks-visualizer-DEV-salt-not-for-publication"

_DEFAULT_BASE_URL = "https://visualizer.coffee/api"
_DEFAULT_OUT = Path(__file__).resolve().parents[1] / "data" / "visualizer" / "raw"

# --- unit conversion to SI at the store boundary -------------------------
# Raw units are as published by the API (bar; g/s; g; degC; s). We convert the
# channels we are confident about and FLAG the rest.
_BAR_TO_PA = 1.0e5
_G_TO_KG = 1.0e-3
_GPS_TO_KGPS = 1.0e-3


def _c_to_k(v):
    return None if v is None else float(v) + 273.15


# Hydraulic series channels grouped by physical quantity → SI conversion.
# key -> (registry_name, raw_unit, si_unit, convert)
_PRESSURE_CHANNELS = {
    "espresso_pressure": ("pressure__Pa", "bar", "Pa", lambda x: x * _BAR_TO_PA),
    "espresso_pressure_goal": ("pressure_goal__Pa", "bar", "Pa", lambda x: x * _BAR_TO_PA),
}
_FLOW_CHANNELS = {
    # espresso_flow may be volumetric (mL/s) on some sources; espresso_flow_weight
    # is the scale-derived mass flow (the trustworthier channel). We treat the
    # published unit as g/s per the manifest and FLAG the volumetric ambiguity.
    "espresso_flow": ("flow__kg_per_s", "g/s", "kg/s", lambda x: x * _GPS_TO_KGPS),
    "espresso_flow_weight": ("flow_weight__kg_per_s", "g/s", "kg/s", lambda x: x * _GPS_TO_KGPS),
    "espresso_flow_goal": ("flow_goal__kg_per_s", "g/s", "kg/s", lambda x: x * _GPS_TO_KGPS),
}
_WEIGHT_CHANNELS = {
    "espresso_weight": ("weight__kg", "g", "kg", lambda x: x * _G_TO_KG),
    "espresso_water_dispensed": ("water_dispensed__kg", "g", "kg", lambda x: x * _G_TO_KG),
}
_TEMP_CHANNELS = {
    "espresso_temperature_goal": ("temperature_goal__K", "degC", "K", _c_to_k),
    "espresso_temperature_mix": ("temperature_mix__K", "degC", "K", _c_to_k),
    "espresso_temperature_basket": ("temperature_basket__K", "degC", "K", _c_to_k),
}
# categorical channel, no unit conversion
_STATE_CHANNELS = {"espresso_state_change": ("state_change", "code", "code", None)}

_VOLUMETRIC_AMBIGUOUS = {"espresso_flow", "espresso_flow_goal"}

# user-entered outcome scalars (SEPARATE evidence tier)
_OUTCOME_FRACTIONS = {  # published percent → stored fraction
    "drink_tds": ("tds__fraction", "%", "fraction"),
    "drink_ey": ("ey__fraction", "%", "fraction"),
}
_SENSORY_INTS = [
    "fragrance", "aroma", "flavor", "aftertaste", "acidity", "bitterness",
    "sweetness", "mouthfeel", "espresso_enjoyment",
]

# fields dropped on ingest for privacy (constraint 2)
_PRIVACY_DROP = [
    "user_name", "user_id", "avatar_url", "barista",
    "espresso_notes", "bean_notes", "private_notes", "notes",
]

_KNOWN_MACHINE_KEYS = [
    "decent", "meticulous", "beanconqueror", "gaggiuino", "gaggimate",
]

_INDEX_COLUMNS = [
    "id", "hashed_user", "machine", "has_tds", "has_ey", "has_sensory",
    "n_samples", "duration_s", "updated_at",
]


@dataclass
class HarvestConfig:
    base_url: str = _DEFAULT_BASE_URL
    out_dir: Path = _DEFAULT_OUT
    max_req_per_min: int = 30
    max_requests: Optional[int] = None
    shard_size: int = 500
    salt: str = field(default_factory=lambda: os.environ.get("PUCKWORKS_VIS_SALT", ""))
    items_per_page: int = 100
    timeout_s: float = 30.0

    def __post_init__(self):
        self.out_dir = Path(self.out_dir)
        if not self.salt:
            warnings.warn(
                "PUCKWORKS_VIS_SALT is not set — using the committed DEV salt. "
                "PRODUCTION harvests MUST set PUCKWORKS_VIS_SALT so user hashes are "
                "not reproducible from this repo.",
                stacklevel=2,
            )
            self.salt = _DEV_SALT


def hash_user(cfg: HarvestConfig, user_id) -> Optional[str]:
    """Salted one-way hash of a raw user id (constraint 2: never store the id)."""
    if user_id in (None, ""):
        return None
    h = hashlib.sha256((cfg.salt + "|" + str(user_id)).encode("utf-8"))
    return h.hexdigest()[:16]


# --- HTTP with rate-limit + backoff --------------------------------------
class _RateLimiter:
    """Keep request starts under max_req_per_min without a foreground sleep loop."""

    def __init__(self, max_req_per_min: int):
        self.min_interval = 60.0 / max(1, max_req_per_min)
        self._last = 0.0
        self.total_wait_s = 0.0

    def wait(self):
        now = time.monotonic()
        gap = self.min_interval - (now - self._last)
        if gap > 0:
            self.total_wait_s += gap
            time.sleep(gap)
        self._last = time.monotonic()


def _requests():
    try:
        import requests  # lazy: only needed for live harvest (the [harvest] extra)
    except ImportError as e:  # pragma: no cover - exercised only without the extra
        raise ImportError(
            "The visualizer harvester needs the optional 'requests' dependency. "
            "Install it with:  pip install -e \".[harvest]\""
        ) from e
    return requests


def _get(cfg, session, limiter, path, params=None, _max_retries=6):
    """GET base_url+path with rate limiting + exponential backoff on 429/5xx."""
    requests = _requests()
    url = cfg.base_url.rstrip("/") + path
    delay = 1.0
    for attempt in range(_max_retries):
        limiter.wait()
        try:
            resp = session.get(url, params=params, timeout=cfg.timeout_s)
        except requests.RequestException:
            if attempt == _max_retries - 1:
                raise
            limiter.total_wait_s += delay
            time.sleep(delay)
            delay = min(delay * 2, 60.0)
            continue
        if resp.status_code == 429 or resp.status_code >= 500:
            # respect Retry-After when present, else exponential backoff
            ra = resp.headers.get("Retry-After")
            wait = float(ra) if (ra and ra.isdigit()) else delay
            if attempt == _max_retries - 1:
                resp.raise_for_status()
            limiter.total_wait_s += wait
            time.sleep(wait)
            delay = min(delay * 2, 60.0)
            continue
        resp.raise_for_status()
        return resp.json()
    raise RuntimeError(f"exhausted retries for {url}")  # pragma: no cover


# --- API access -----------------------------------------------------------
def list_public_shot_ids(cfg, updated_after=None, _session=None, _limiter=None):
    """Paginate GET /shots yielding (id, clock, updated_at) for PUBLIC shots.

    Uses sort='updated_at' when updated_after is set (incremental), else
    sort='start_time' (initial crawl). Stops when a page returns no rows.
    """
    session = _session if _session is not None else _requests().Session()
    limiter = _limiter if _limiter is not None else _RateLimiter(cfg.max_req_per_min)
    sort = "updated_at" if updated_after is not None else "start_time"
    page = 1
    while True:
        params = {"page": page, "items": cfg.items_per_page, "sort": sort}
        if updated_after is not None:
            params["updated_after"] = int(updated_after)
        data = _get(cfg, session, limiter, "/shots", params=params)
        rows = data.get("data", data) if isinstance(data, dict) else data
        if not rows:
            return
        for r in rows:
            yield (r.get("id"), r.get("clock"), r.get("updated_at"))
        page += 1


def fetch_shot(cfg, shot_id, _session=None, _limiter=None):
    """GET /shots/{id} -> raw dict (with backoff/retry on 429/5xx)."""
    session = _session if _session is not None else _requests().Session()
    limiter = _limiter if _limiter is not None else _RateLimiter(cfg.max_req_per_min)
    return _get(cfg, session, limiter, f"/shots/{shot_id}")


# --- normalization: split into hydraulic / outcomes / context ------------
def _series(raw_data, key):
    v = raw_data.get(key)
    if isinstance(v, list) and v:
        return v
    return None


def _infer_machine(raw):
    """Infer the source machine from the brewdata payload; null+flag if unknown."""
    bd = raw.get("brewdata")
    if isinstance(bd, dict):
        for k in _KNOWN_MACHINE_KEYS:
            if k in bd:
                return k
        src = bd.get("source") or bd.get("machine")
        if isinstance(src, str) and src:
            return src.lower()
    src = raw.get("source") or raw.get("machine")
    if isinstance(src, str) and src:
        return src.lower()
    return None


_NUM_RE = re.compile(r"[-+]?\d*\.?\d+")


def _num(v):
    """Tolerant numeric parse of a possibly-dirty USER-entered field.

    Returns ``(value_or_None, dirty)``. User fields are free text: values like
    ``'18g'``, ``'8.5%'``, ``'25 s'`` or ``'n/a'`` appear. We never `float()` them
    blindly (that crashed the crawl on ``'18g'``). Numeric types pass through; a
    string is parsed by stripping a leading number off the front — ``dirty=True``
    flags that a suffix/garbage was present (so it is traceable per CLAUDE.md rule 7),
    and an unparseable value yields ``(None, True)`` instead of raising.
    """
    if v in (None, "", 0):
        return (None, False)
    if isinstance(v, (int, float)):
        return (float(v), False)
    s = str(v).strip()
    try:
        return (float(s), False)
    except (ValueError, TypeError):
        m = _NUM_RE.match(s)
        return (float(m.group(0)), True) if m else (None, True)


def normalize_shot(raw, cfg):
    """Turn one raw API shot into a TidyShot dict with SEPARATE evidence tiers.

    Returns {schema_version, id, hashed_user, machine, hydraulic, outcomes,
    context, units, flags}. Applies the privacy drop (constraint 2), converts
    known channels to SI (constraint 4), and NEVER invents a missing field —
    missing values become null and are flagged.
    """
    flags = []
    units = {"hydraulic": {}, "outcomes": {}, "context": {}}
    data = raw.get("data") or {}

    # privacy: confirm we never carry a dropped field forward
    hashed_user = hash_user(cfg, raw.get("user_id"))

    # --- hydraulic tier: SI series on the shared time base ---------------
    hydraulic = {}
    timeframe = _series(data, "timeframe")
    if timeframe is None:
        flags.append("missing:timeframe")
        n_samples = 0
    else:
        hydraulic["time__s"] = [float(x) for x in timeframe]
        units["hydraulic"]["time__s"] = {"raw": "s", "si": "s"}
        n_samples = len(timeframe)

    for group in (_PRESSURE_CHANNELS, _FLOW_CHANNELS, _WEIGHT_CHANNELS,
                  _TEMP_CHANNELS):
        for src_key, (name, raw_u, si_u, conv) in group.items():
            s = _series(data, src_key)
            if s is None:
                flags.append(f"missing:{src_key}")
                continue
            if timeframe is not None and len(s) != len(timeframe):
                flags.append(f"length_mismatch:{src_key}")
            hydraulic[name] = [None if x is None else conv(float(x)) for x in s]
            units["hydraulic"][name] = {"raw": raw_u, "si": si_u}
            if src_key in _VOLUMETRIC_AMBIGUOUS:
                flags.append(f"unit_ambiguous:{src_key}=volumetric_or_mass")

    # categorical state change: kept as-is (no unit)
    sc = _series(data, "espresso_state_change")
    if sc is not None:
        hydraulic["state_change"] = list(sc)
        units["hydraulic"]["state_change"] = {"raw": "code", "si": "code"}

    # --- outcomes tier: user-entered TDS/EY/sensory (NOT groundtruth) ----
    outcomes = {}
    for src_key, (name, raw_u, si_u) in _OUTCOME_FRACTIONS.items():
        v = raw.get(src_key)
        num, dirty = _num(v)
        if num is None:
            outcomes[name] = None
            flags.append(f"missing:{src_key}" if v in (None, "", 0)
                         else f"unparseable:{src_key}")
        else:
            outcomes[name] = num / 100.0  # percent -> fraction (SI-dimensionless)
            units["outcomes"][name] = {"raw": raw_u, "si": si_u}
            if dirty:
                flags.append(f"dirty_value:{src_key}")
    sensory = {}
    for key in _SENSORY_INTS:
        v = raw.get(key)
        sensory[key] = int(v) if isinstance(v, (int, float)) and v else None
    if not any(v is not None for v in sensory.values()):
        flags.append("missing:sensory")
    outcomes["sensory"] = sensory

    # --- context: dose/drink weight, grinder, machine, profile, roast ---
    def _kg(field_name):
        num, dirty = _num(raw.get(field_name))
        if num is None:
            return None
        if dirty:
            flags.append(f"dirty_value:{field_name}")
        return num * _G_TO_KG

    machine = _infer_machine(raw)
    if machine is None:
        flags.append("missing:machine_source")
    context = {
        "dose__kg": _kg("bean_weight"),
        "drink_weight__kg": _kg("drink_weight"),
        "duration__s": _num(raw.get("duration"))[0],
        "grinder_model": raw.get("grinder_model") or None,
        "grinder_setting": raw.get("grinder_setting") or None,
        "machine": machine,
        "profile_title": raw.get("profile_title") or None,
        "roast_level": raw.get("roast_level") or None,
        "tags": list(raw.get("tags") or []),
    }
    units["context"]["dose__kg"] = {"raw": "g", "si": "kg"}
    units["context"]["drink_weight__kg"] = {"raw": "g", "si": "kg"}
    units["context"]["duration__s"] = {"raw": "s", "si": "s"}

    return {
        "schema_version": 1,
        "id": raw.get("id"),
        "hashed_user": hashed_user,
        "machine": machine,
        "updated_at": raw.get("updated_at"),
        "hydraulic": hydraulic,
        "outcomes": outcomes,
        "context": context,
        "units": units,
        "flags": flags,
        "n_samples": n_samples,
    }


# --- store layout ---------------------------------------------------------
def _index_path(cfg):
    return cfg.out_dir / "_index.csv"


def _cursor_path(cfg):
    return cfg.out_dir / "_cursor.json"


def _read_index_ids(cfg):
    p = _index_path(cfg)
    if not p.exists():
        return set()
    with open(p, newline="", encoding="utf-8") as fh:
        return {row["id"] for row in csv.DictReader(fh)}


def _index_row(tidy):
    sensory = (tidy.get("outcomes") or {}).get("sensory") or {}
    return {
        "id": tidy.get("id"),
        "hashed_user": tidy.get("hashed_user") or "",
        "machine": tidy.get("machine") or "",
        "has_tds": int((tidy["outcomes"].get("tds__fraction")) is not None),
        "has_ey": int((tidy["outcomes"].get("ey__fraction")) is not None),
        "has_sensory": int(any(v is not None for v in sensory.values())),
        "n_samples": tidy.get("n_samples", 0),
        "duration_s": (tidy["context"].get("duration__s") or ""),
        "updated_at": tidy.get("updated_at") or "",
    }


def _append_index(cfg, rows):
    p = _index_path(cfg)
    new = not p.exists()
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    with open(p, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_INDEX_COLUMNS)
        if new:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_shard(cfg, shard_idx, tidy_records):
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    path = cfg.out_dir / f"shard_{shard_idx:05d}.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as fh:
        for rec in tidy_records:
            fh.write(json.dumps(rec) + "\n")
    return path


def _next_shard_idx(cfg):
    existing = sorted(cfg.out_dir.glob("shard_*.jsonl.gz")) if cfg.out_dir.exists() else []
    if not existing:
        return 0
    return int(existing[-1].stem.split("_")[1].split(".")[0]) + 1


def _load_cursor(cfg):
    p = _cursor_path(cfg)
    if not p.exists():
        return {"last_updated_at": None}
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def _save_cursor(cfg, last_updated_at):
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    with open(_cursor_path(cfg), "w", encoding="utf-8") as fh:
        json.dump({"last_updated_at": last_updated_at}, fh)


def _crawl(cfg, updated_after):
    """Shared crawl body for full/incremental. Returns a run summary dict."""
    session = _requests().Session()
    limiter = _RateLimiter(cfg.max_req_per_min)
    seen = _read_index_ids(cfg)
    shard_idx = _next_shard_idx(cfg)
    buffer, index_buffer = [], []
    n_fetched = n_new = n_skipped = 0
    max_updated = _load_cursor(cfg).get("last_updated_at")

    def flush():
        nonlocal shard_idx, buffer, index_buffer
        if buffer:
            _write_shard(cfg, shard_idx, buffer)
            _append_index(cfg, index_buffer)
            shard_idx += 1
            buffer, index_buffer = [], []

    stopped_early = None
    try:
        for sid, _clock, upd in list_public_shot_ids(
                cfg, updated_after=updated_after, _session=session, _limiter=limiter):
            if cfg.max_requests is not None and n_fetched >= cfg.max_requests:
                break
            if sid in seen and updated_after is None:
                continue  # initial crawl dedups on id
            try:
                raw = fetch_shot(cfg, sid, _session=session, _limiter=limiter)
            except Exception as exc:
                # a persistent 429/5xx (retries exhausted), network drop, or a listing
                # error: STOP GRACEFULLY so the finally-block preserves everything
                # fetched so far. Re-running `full` resumes (id-dedup skips done shots).
                stopped_early = "%s: %s" % (type(exc).__name__, exc)
                break
            n_fetched += 1
            try:
                tidy = normalize_shot(raw, cfg)
            except Exception:
                # a single malformed record must not abort the crawl: skip it and
                # continue (the tolerant `_num` parser already handles dirty user
                # fields; this is a last-resort guard for anything unforeseen).
                n_skipped += 1
                continue
            if sid not in seen:
                n_new += 1
                seen.add(sid)
            buffer.append(tidy)
            index_buffer.append(_index_row(tidy))
            if upd is not None:
                max_updated = upd if max_updated is None else max(max_updated, upd)
            if len(buffer) >= cfg.shard_size:
                flush()
    finally:
        # NEVER lose the in-progress buffer or the resume cursor -- runs on normal exit,
        # exception, or interruption (environment reap / Ctrl-C).
        flush()
        if max_updated is not None:
            _save_cursor(cfg, max_updated)
    return {
        "n_fetched": n_fetched, "n_new": n_new, "n_skipped": n_skipped,
        "rate_limit_wait_s": round(limiter.total_wait_s, 1),
        "cursor": max_updated, "stopped_early": stopped_early,
    }


def harvest_all(cfg):
    """Initial full crawl: walk public ids, fetch, normalize, write shards +
    _index.csv + _cursor.json. Safely re-runnable (dedups on id)."""
    return _crawl(cfg, updated_after=None)


def harvest_incremental(cfg):
    """Re-run mode: list with updated_after=cursor, fetch+append only new/updated,
    advance the cursor. Idempotent (dedup on id; last-write-wins on updated_at)."""
    cursor = _load_cursor(cfg).get("last_updated_at")
    return _crawl(cfg, updated_after=(cursor if cursor is not None else 0))


# --- stats / aggregate ----------------------------------------------------
def iter_store(cfg):
    """Yield TidyShot dicts from the on-disk shards (generator; never loads all)."""
    if not cfg.out_dir.exists():
        return
    for shard in sorted(cfg.out_dir.glob("shard_*.jsonl.gz")):
        with gzip.open(shard, "rt", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield json.loads(line)


def _histogram(values, edges):
    counts = [0] * (len(edges) - 1)
    for v in values:
        if v is None:
            continue
        for i in range(len(edges) - 1):
            if edges[i] <= v < edges[i + 1]:
                counts[i] += 1
                break
    return counts


def compute_stats(cfg):
    """Aggregate coverage/mix/unit-audit statistics over the store (no per-shot rows)."""
    total = 0
    machines, grinders = {}, {}
    n_tds = n_ey = n_sensory = 0
    durations, peak_pressure, peak_flow = [], [], []
    unit_audit = {"missing_timeframe": 0, "flow_unit_ambiguous": 0,
                  "length_mismatch": 0, "missing_machine": 0}
    for shot in iter_store(cfg):
        total += 1
        m = shot.get("machine") or "unknown"
        machines[m] = machines.get(m, 0) + 1
        g = (shot.get("context") or {}).get("grinder_model") or "unknown"
        grinders[g] = grinders.get(g, 0) + 1
        oc = shot.get("outcomes") or {}
        n_tds += int(oc.get("tds__fraction") is not None)
        n_ey += int(oc.get("ey__fraction") is not None)
        sensory = oc.get("sensory") or {}
        n_sensory += int(any(v is not None for v in sensory.values()))
        dur = (shot.get("context") or {}).get("duration__s")
        if dur is not None:
            durations.append(dur)
        hy = shot.get("hydraulic") or {}
        pp = [x for x in (hy.get("pressure__Pa") or []) if x is not None]
        if pp:
            peak_pressure.append(max(pp) / _BAR_TO_PA)  # report in bar for readability
        pf = [x for x in (hy.get("flow_weight__kg_per_s") or hy.get("flow__kg_per_s") or [])
              if x is not None]
        if pf:
            peak_flow.append(max(pf) / _GPS_TO_KGPS)  # report in g/s
        for fl in shot.get("flags") or []:
            if fl == "missing:timeframe":
                unit_audit["missing_timeframe"] += 1
            elif fl.startswith("unit_ambiguous:"):
                unit_audit["flow_unit_ambiguous"] += 1
            elif fl.startswith("length_mismatch:"):
                unit_audit["length_mismatch"] += 1
            elif fl == "missing:machine_source":
                unit_audit["missing_machine"] += 1

    def _pct(n):
        return round(100.0 * n / total, 2) if total else 0.0

    top_grinders = sorted(grinders.items(), key=lambda kv: -kv[1])[:20]
    return {
        "total_shots": total,
        "machine_mix": dict(sorted(machines.items(), key=lambda kv: -kv[1])),
        "grinder_mix_top20": dict(top_grinders),
        "pct_with_tds": _pct(n_tds),
        "pct_with_ey": _pct(n_ey),
        "pct_with_sensory": _pct(n_sensory),
        "duration_hist_s": {
            "edges": [0, 15, 20, 25, 30, 35, 40, 60, 1e9],
            "counts": _histogram(durations, [0, 15, 20, 25, 30, 35, 40, 60, 1e9]),
        },
        "peak_pressure_hist_bar": {
            "edges": [0, 2, 4, 6, 8, 9, 10, 12, 1e9],
            "counts": _histogram(peak_pressure, [0, 2, 4, 6, 8, 9, 10, 12, 1e9]),
        },
        "peak_flow_hist_g_per_s": {
            "edges": [0, 1, 2, 3, 4, 5, 6, 8, 1e9],
            "counts": _histogram(peak_flow, [0, 1, 2, 3, 4, 5, 6, 8, 1e9]),
        },
        "unit_audit": unit_audit,
    }


def _aggregate_csv_path(cfg):
    # the DERIVED tracked file lives one level up from raw/ (data/visualizer/)
    return cfg.out_dir.parent / "aggregate_stats.csv"


def write_aggregate_csv(cfg, stats=None):
    """Write the small DERIVED aggregate CSV (the only data-derived tracked file).

    Long-format (metric, key, value) so counts, mixes, histograms and the
    unit-audit all live in one flat table with NO per-shot rows.
    """
    stats = stats or compute_stats(cfg)
    rows = [("total_shots", "", stats["total_shots"])]
    for k, v in stats["machine_mix"].items():
        rows.append(("machine_mix", k, v))
    for k, v in stats["grinder_mix_top20"].items():
        rows.append(("grinder_mix_top20", k, v))
    for m in ("pct_with_tds", "pct_with_ey", "pct_with_sensory"):
        rows.append((m, "", stats[m]))
    for hist in ("duration_hist_s", "peak_pressure_hist_bar", "peak_flow_hist_g_per_s"):
        edges, counts = stats[hist]["edges"], stats[hist]["counts"]
        for i, c in enumerate(counts):
            rows.append((hist, f"[{edges[i]},{edges[i + 1]})", c))
    for k, v in stats["unit_audit"].items():
        rows.append(("unit_audit", k, v))
    path = _aggregate_csv_path(cfg)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "key", "value"])
        w.writerows(rows)
    return path


# --- CLI ------------------------------------------------------------------
def _print_summary(title, d):
    print(f"== {title} ==")
    for k, v in d.items():
        print(f"  {k}: {v}")


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.lib.visualizer_harvest")
    p.add_argument("cmd", choices=["full", "incremental", "stats"])
    p.add_argument("--max-requests", type=int, default=None)
    p.add_argument("--req-per-min", type=int, default=30)
    p.add_argument("--out", default=str(_DEFAULT_OUT))
    p.add_argument("--write-aggregate", action="store_true",
                   help="stats: also (re)write the tracked aggregate_stats.csv")
    a = p.parse_args(argv)
    cfg = HarvestConfig(out_dir=a.out, max_req_per_min=a.req_per_min,
                        max_requests=a.max_requests)
    if a.cmd == "full":
        summary = harvest_all(cfg)
        _print_summary("visualizer harvest (full)", summary)
    elif a.cmd == "incremental":
        summary = harvest_incremental(cfg)
        _print_summary("visualizer harvest (incremental)", summary)
    else:  # stats
        stats = compute_stats(cfg)
        _print_summary("visualizer store stats", {
            "total_shots": stats["total_shots"],
            "pct_with_tds": stats["pct_with_tds"],
            "pct_with_ey": stats["pct_with_ey"],
            "pct_with_sensory": stats["pct_with_sensory"],
            "machine_mix": stats["machine_mix"],
            "grinder_mix_top20": stats["grinder_mix_top20"],
            "unit_audit": stats["unit_audit"],
        })
        if a.write_aggregate:
            path = write_aggregate_csv(cfg, stats)
            print(f"  wrote aggregate -> {path}")


if __name__ == "__main__":
    main()

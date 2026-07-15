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
  * RATE LIMITS (published API docs) — 50 requests/min AND **200 requests / 10 min**
    per client IP; 429 on exceed. The 10-minute window is the BINDING sustained cap
    (=20 req/min average), so a long crawl must average <=20/min regardless of the
    50/min burst allowance. Default is a safe 18/min (180 per 10-min window); the
    evenly-spaced limiter therefore respects the 10-min window inherently. Exponential
    backoff on 429/5xx, a persistent resume cursor and a --max-requests cap keep it
    safely re-runnable and interruptible.
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
import math
import os
import re
import shutil
import subprocess
import time
import warnings
from collections import Counter
from dataclasses import dataclass, field, replace
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
    # SERIALIZER_REVIEW §8: only the SCALE-DERIVED channel is confirmed mass flow, so only it
    # is converted to SI kg/s. Pump/model-estimated `espresso_flow` (which may be volumetric
    # mL/s, mass g/s, or a machine proxy) is NOT labelled kg/s -- see _AMBIGUOUS_FLOW_CHANNELS.
    "espresso_flow_weight": ("mass_flow_from_scale__kg_per_s", "g/s", "kg/s",
                             lambda x: x * _GPS_TO_KGPS),
}
# Reported/estimated flow with UNKNOWN quantity kind: stored NATIVE (no unit conversion, no
# kg/s label) with an explicit semantic tag. A warning flag alone did not make a kg_per_s
# column scientifically safe; downstream must opt in knowing the value is not SI mass flow.
_AMBIGUOUS_FLOW_CHANNELS = {
    "espresso_flow": ("flow_reported__native", "reported_pump_or_model_estimate"),
    "espresso_flow_goal": ("flow_goal_reported__native", "goal_reported_estimate"),
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

# user-entered outcome scalars (SEPARATE evidence tier)
_OUTCOME_FRACTIONS = {  # published percent → stored fraction
    "drink_tds": ("tds__fraction", "%", "fraction"),
    "drink_ey": ("ey__fraction", "%", "fraction"),
}
# Tasting dimensions are scored 0..15; `espresso_enjoyment` is a SEPARATE 0..100
# preference score (Visualizer shot model). Validating enjoyment against 0..15
# nulled every real value >15 (SERIALIZER_REVIEW §6 — a fixture value of 82 became
# None). Keep a per-field ceiling so each dimension is validated on its own scale.
_SENSORY_MAX = {
    "fragrance": 15, "aroma": 15, "flavor": 15, "aftertaste": 15,
    "acidity": 15, "bitterness": 15, "sweetness": 15, "mouthfeel": 15,
    "espresso_enjoyment": 100,
}
_SENSORY_INTS = list(_SENSORY_MAX)  # preserve stored key set + order

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
    "n_samples", "duration_s", "updated_at", "content_sha256",
]


@dataclass
class HarvestConfig:
    base_url: str = _DEFAULT_BASE_URL
    out_dir: Path = _DEFAULT_OUT
    max_req_per_min: int = 18   # safe under the binding 200-req/10-min IP limit (=20/min)
    max_requests: Optional[int] = None
    shard_size: int = 100   # small so progress checkpoints often (survives short reaps)
    salt: str = field(default_factory=lambda: os.environ.get("PUCKWORKS_VIS_SALT", ""))
    items_per_page: int = 100
    timeout_s: float = 30.0
    min_free_gb: float = 1.0   # stop gracefully if the drive drops below this many GB free
    store_bronze: bool = True   # keep a PII-stripped raw payload so a later normalizer fix
                                # can re-normalize OFFLINE (SERIALIZER_REVIEW §5). Essential
                                # for the ephemeral recent-updated window: once a shot ages
                                # out of the API it can never be re-fetched.

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
def list_public_shot_ids(cfg, updated_after=None, start_page=1,
                         _session=None, _limiter=None):
    """Paginate GET /shots yielding (page, id, clock, updated_at) for PUBLIC shots.

    Uses sort='updated_at' when updated_after is set (incremental), else
    sort='start_time' (initial crawl). Stops when a page returns no rows. `start_page`
    lets a resumed full crawl skip re-listing the already-fetched prefix (the API sorts
    newest-first and caps pages at 100 rows, so re-listing from page 1 is the dominant
    resume cost once the store is large).
    """
    session = _session if _session is not None else _requests().Session()
    limiter = _limiter if _limiter is not None else _RateLimiter(cfg.max_req_per_min)
    sort = "updated_at" if updated_after is not None else "start_time"
    page = max(1, int(start_page))
    while True:
        params = {"page": page, "items": cfg.items_per_page, "sort": sort}
        if updated_after is not None:
            params["updated_after"] = int(updated_after)
        data = _get(cfg, session, limiter, "/shots", params=params)
        rows = data.get("data", data) if isinstance(data, dict) else data
        if not rows:
            return
        for r in rows:
            yield (page, r.get("id"), r.get("clock"), r.get("updated_at"))
        page += 1


def _list_page_path(cfg):
    return cfg.out_dir / "_list_page.json"


def _load_list_page(cfg):
    p = _list_page_path(cfg)
    if p.exists():
        try:
            return max(1, int(json.load(open(p)).get("next_page", 1)))
        except Exception:
            return 1
    return 1


def _save_list_page(cfg, page):
    p = _list_page_path(cfg)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump({"next_page": max(1, int(page))}, fh)


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


def _finite_float(x):
    """Parse one trace element to a FINITE float, else None (SERIALIZER_REVIEW §9).
    A Python bool is NOT a measurement (it would become 1.0/0.0 -- a false sample); NaN
    and infinity are rejected; a non-numeric string yields None. This keeps a single bad
    sample from either faking a value or dropping the whole shot via a raised exception."""
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return float(x) if math.isfinite(x) else None
    if isinstance(x, str):
        try:
            f = float(x)
        except ValueError:
            return None
        return f if math.isfinite(f) else None
    return None


def _parse_series(seq):
    """Parse a raw trace to aligned floats: bad/non-finite/boolean elements become None in
    place (array alignment preserved). Returns (values, n_bad) where n_bad counts positions
    that held a non-null value we could not use as a finite number."""
    values, n_bad = [], 0
    for x in seq:
        f = _finite_float(x)
        if f is None:
            values.append(None)
            if x is not None:      # an explicit null is 'missing', not 'bad'
                n_bad += 1
        else:
            values.append(f)
    return values, n_bad


def _timeseries_qc(hydraulic, n_samples):
    """First-class time-series QC metrics (SERIALIZER_REVIEW §9): timestamp monotonicity,
    duplicate stamps, sampling-interval median + jitter (IQR), and per-channel valid /
    flatline / length-vs-time. These feed declared eligibility rules downstream rather than
    hiding inside a single opaque flag. Computed from the already-parsed hydraulic arrays."""
    t = hydraulic.get("time__s")
    qc = {"n_samples": n_samples, "time_present": bool(t)}
    if t:
        tv = [x for x in t if x is not None]
        qc["time_valid"] = len(tv)
        steps = [b - a for a, b in zip(tv, tv[1:])]
        qc["time_nonincreasing_steps"] = sum(1 for s in steps if s <= 0)
        qc["time_duplicate_stamps"] = sum(1 for s in steps if s == 0)
        qc["time_monotonic"] = all(s > 0 for s in steps) if steps else True
        if steps:
            ss = sorted(steps)
            n = len(ss)
            qc["dt_median_s"] = ss[n // 2] if n % 2 else (ss[n // 2 - 1] + ss[n // 2]) / 2
            qc["dt_min_s"] = ss[0]
            qc["dt_max_s"] = ss[-1]
            qc["dt_iqr_s"] = ss[min(n - 1, (3 * n) // 4)] - ss[n // 4]   # sampling jitter
    channels = {}
    for name, series in hydraulic.items():
        if name in ("time__s", "state_change"):
            continue
        vals = [x for x in series if x is not None]
        channels[name] = {
            "length": len(series),
            "valid": len(vals),
            "missing": len(series) - len(vals),
            "len_matches_time": (t is None or len(series) == len(t)),
            "flatline": (len(set(vals)) == 1) if len(vals) > 1 else False,
        }
    qc["channels"] = channels
    return qc


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


def _integration_source(raw):
    """Best-effort ``(source, provenance)`` for the data ORIGIN app/parser, kept SEPARATE
    from machine make/model (SERIALIZER_REVIEW §7). Different integrations (Decent,
    Meticulous, Beanconqueror, Gaggiuino, GaggiMate, SEP, Pressensor, …) differ in channel
    definitions, units, cadence, and flow estimation, so an unknown source is unexplained
    modeling heterogeneity. `provenance` is 'explicit' if Visualizer emits a stable field,
    else 'inferred' from brewdata, else 'unknown' — source is never guessed from a machine."""
    for key in ("integration_source", "integration", "parser"):
        v = raw.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip().lower(), "explicit"
    m = _infer_machine(raw)
    if m is not None:
        return m, "inferred"
    return None, "unknown"


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


_NORMALIZE_SCHEMA_VERSION = 5   # v2 §7; v3 §8; v4 §9 qc; v5 content_sha256 + start_time + privacy


def normalize_shot(raw, cfg, hashed_user_override=None):
    """Turn one raw API shot into a TidyShot dict with SEPARATE evidence tiers.

    Returns {schema_version, id, hashed_user, machine, hydraulic, outcomes,
    context, units, flags}. Applies the privacy drop (constraint 2), converts
    known channels to SI (constraint 4), and NEVER invents a missing field —
    missing values become null and are flagged.

    `hashed_user_override` lets re-normalization from Bronze reproduce the salted
    user hash when the raw `user_id` has already been stripped from the payload.
    """
    flags = []
    units = {"hydraulic": {}, "outcomes": {}, "context": {}}
    data = raw.get("data") or {}

    # privacy: confirm we never carry a dropped field forward
    hashed_user = (hashed_user_override if hashed_user_override is not None
                   else hash_user(cfg, raw.get("user_id")))

    # --- hydraulic tier: SI series on the shared time base ---------------
    # review §8.1 (P0): the live Visualizer schema/serializer put `timeframe` at the
    # TOP LEVEL of the shot-detail response, alongside `data` (which holds only the value
    # channels). The old code read `data.timeframe`, which is absent -> every live trace
    # was wrongly flagged missing:timeframe with n_samples=0 (values present, NO time
    # base). Read top-level first, fall back to the nested layout for legacy fixtures.
    hydraulic = {}
    timeframe = _series(raw, "timeframe")
    if timeframe is None:
        timeframe = _series(data, "timeframe")
    if timeframe is None:
        flags.append("missing:timeframe")
        n_samples = 0
    else:
        tvals, t_bad = _parse_series(timeframe)   # §9: tolerant, keeps alignment
        hydraulic["time__s"] = tvals
        units["hydraulic"]["time__s"] = {"raw": "s", "si": "s"}
        n_samples = len(timeframe)
        if t_bad:
            flags.append(f"bad_samples:timeframe={t_bad}")

    for group in (_PRESSURE_CHANNELS, _FLOW_CHANNELS, _WEIGHT_CHANNELS,
                  _TEMP_CHANNELS):
        for src_key, (name, raw_u, si_u, conv) in group.items():
            s = _series(data, src_key)
            if s is None:
                flags.append(f"missing:{src_key}")
                continue
            if timeframe is not None and len(s) != len(timeframe):
                flags.append(f"length_mismatch:{src_key}")
            vals, n_bad = _parse_series(s)   # §9: bool/non-finite/non-numeric -> None in place
            hydraulic[name] = [None if v is None else conv(v) for v in vals]
            units["hydraulic"][name] = {"raw": raw_u, "si": si_u}
            if n_bad:
                flags.append(f"bad_samples:{src_key}={n_bad}")

    # §8 ambiguous flow: kept NATIVE (no conversion, no kg/s label), with an explicit
    # semantic tag and units.si=None so it is excluded from the SI hydraulic accessor.
    for src_key, (name, semantic) in _AMBIGUOUS_FLOW_CHANNELS.items():
        s = _series(data, src_key)
        if s is None:
            flags.append(f"missing:{src_key}")
            continue
        if timeframe is not None and len(s) != len(timeframe):
            flags.append(f"length_mismatch:{src_key}")
        vals, n_bad = _parse_series(s)
        hydraulic[name] = vals   # native value as reported -- NOT SI mass flow
        units["hydraulic"][name] = {"raw": "g/s_or_mL/s", "si": None, "semantic": semantic}
        if n_bad:
            flags.append(f"bad_samples:{src_key}={n_bad}")
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
        hi = _SENSORY_MAX[key]  # 0..15 tasting dims, 0..100 enjoyment (SERIALIZER_REVIEW §6)
        # review §8.6 (P1): a real 0 must be KEPT (the old `and v` truthiness turned a valid
        # 0 into None, distorting missingness and within-user distributions). Booleans are
        # excluded (bool is an int subclass).
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            sensory[key] = int(v) if 0 <= v <= hi else None
            if not (0 <= v <= hi):
                flags.append(f"out_of_range:{key}")
        else:
            sensory[key] = None
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
    integ_source, integ_prov = _integration_source(raw)   # §7: origin app/parser
    if integ_prov == "unknown":
        flags.append("missing:integration_source")
    context = {
        "dose__kg": _kg("bean_weight"),
        "drink_weight__kg": _kg("drink_weight"),
        "duration__s": _num(raw.get("duration"))[0],
        "grinder_model": raw.get("grinder_model") or None,
        "grinder_setting": raw.get("grinder_setting") or None,
        "machine": machine,
        "integration_source": integ_source,
        "integration_source_provenance": integ_prov,
        "profile_title": raw.get("profile_title") or None,
        "roast_level": raw.get("roast_level") or None,
        "tags": list(raw.get("tags") or []),
    }
    units["context"]["dose__kg"] = {"raw": "g", "si": "kg"}
    units["context"]["drink_weight__kg"] = {"raw": "g", "si": "kg"}
    units["context"]["duration__s"] = {"raw": "s", "si": "s"}

    qc = _timeseries_qc(hydraulic, n_samples)   # §9 first-class time-series QC
    if qc.get("time_monotonic") is False:
        flags.append("qc:time_not_monotonic")
    if qc.get("time_duplicate_stamps"):
        flags.append("qc:duplicate_timestamps")

    rec = {
        "schema_version": _NORMALIZE_SCHEMA_VERSION,
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
        "qc": qc,
    }
    # content hash for version identity (id, updated_at, content_sha256): distinguishes two
    # edits that share an integer-second updated_at, and lets the latest view + reconciliation
    # address the exact stored version rather than any record sharing a timestamp (P0-3/P1-1).
    rec["content_sha256"] = _record_content_hash(rec)
    return rec


def _record_content_hash(rec):
    """Stable SHA-256 over a normalized record's content (excluding the hash field itself)."""
    core = {k: v for k, v in rec.items() if k != "content_sha256"}
    return hashlib.sha256(json.dumps(core, sort_keys=True, ensure_ascii=False,
                                     default=str).encode("utf-8")).hexdigest()


# --- store layout ---------------------------------------------------------
def _index_path(cfg):
    return cfg.out_dir / "_index.csv"


def _cursor_path(cfg):
    return cfg.out_dir / "_cursor.json"


def _as_int(x, default=None):
    """Tolerant int parse for index fields (updated_at may be '' or a string)."""
    try:
        return int(x)
    except (TypeError, ValueError):
        return default


def _read_index_ids(cfg):
    p = _index_path(cfg)
    if not p.exists():
        return set()
    with open(p, newline="", encoding="utf-8") as fh:
        return {row["id"] for row in csv.DictReader(fh)}


def iter_index_rows(cfg):
    """Yield every row of the append-only _index.csv (one per stored VERSION)."""
    p = _index_path(cfg)
    if not p.exists():
        return
    with open(p, newline="", encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            yield row


def latest_index_rows(cfg):
    """§3 latest-version view: collapse the append-only index to ONE row per shot id —
    the latest by `updated_at` (ties resolved to the last-written row). This is the
    default analytic view; the full version history stays in the shards + index."""
    latest = {}
    for row in iter_index_rows(cfg):
        sid = row.get("id")
        if sid is None:
            continue
        u = _as_int(row.get("updated_at"), default=-1)
        prev = latest.get(sid)
        if prev is None or u >= _as_int(prev.get("updated_at"), default=-1):
            latest[sid] = row
    return latest


def latest_index_map(cfg):
    """§4 dedup key: {shot_id -> latest stored updated_at (int, -1 if missing)}. Used both
    to crawl only new/changed shots and to select latest versions when reading the store."""
    return {sid: _as_int(r.get("updated_at"), default=-1)
            for sid, r in latest_index_rows(cfg).items()}


def iter_store_latest(cfg):
    """§3: yield exactly one record per shot id — the latest version. The winner is the
    index's latest row (max `updated_at`, ties → last-written); it is matched by
    `(updated_at, content_sha256)` and, on a same-timestamp tie, the LAST physical record
    that matches is chosen (P0-3) — not the first record sharing the timestamp."""
    winners = {sid: (_as_int(r.get("updated_at"), default=-1), r.get("content_sha256") or "")
               for sid, r in latest_index_rows(cfg).items()}
    chosen = {}
    for rec in iter_store(cfg):
        sid = rec.get("id")
        w = winners.get(sid)
        if w is None:
            continue
        key = (_as_int(rec.get("updated_at"), default=-1), rec.get("content_sha256") or "")
        if key == w:
            chosen[sid] = rec      # keep the LAST match = index last-wins tie policy
    for rec in chosen.values():
        yield rec


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
        # explicit None checks: a real 0 (duration/updated_at) must NOT collapse to "" via
        # truthiness -- that would read back as missing and defeat §4 version dedup.
        "duration_s": (d if (d := tidy["context"].get("duration__s")) is not None else ""),
        "updated_at": (u if (u := tidy.get("updated_at")) is not None else ""),
        "content_sha256": tidy.get("content_sha256") or "",
    }


def _rewrite_index(cfg, rows):
    """Atomically write the whole _index.csv with the current columns (fills any missing
    field with ''). Used to self-heal a header that drifted after a column was added."""
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    dst = _index_path(cfg)
    tmp = dst.with_name(dst.name + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_INDEX_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in _INDEX_COLUMNS})
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, dst)


def _append_index(cfg, rows):
    p = _index_path(cfg)
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    if p.exists():
        with open(p, newline="", encoding="utf-8") as fh:
            header = next(csv.reader(fh), None)
        if header != _INDEX_COLUMNS:
            # a column was added since this file was written: migrate the whole file to the
            # current columns (index is derived metadata) rather than append ragged rows.
            _rewrite_index(cfg, list(iter_index_rows(cfg)) + list(rows))
            return
    new = not p.exists()
    with open(p, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_INDEX_COLUMNS, extrasaction="ignore")
        if new:
            w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in _INDEX_COLUMNS})


# --- quarantine ledger: a malformed record is RECORDED, never silently skipped (§9) ---
def _quarantine_path(cfg):
    return cfg.out_dir / "_quarantine.jsonl"


def _quarantine_record(run_id, sid, updated_at, raw, stage, exc):
    """One record we could not normalize or serialize, captured with enough context to
    re-examine it later: run, id, stage, exception, and a content hash of the PII-stripped
    raw payload. A single bad shot must never abort the crawl or vanish without a trace."""
    payload = _strip_pii(raw or {})
    try:
        blob = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    except Exception:
        blob = repr(payload)
    return {
        "run_id": run_id, "id": sid, "updated_at": updated_at,
        "failure_stage": stage,
        "exception_type": type(exc).__name__,
        "reason": str(exc)[:500],
        "content_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
    }


def _append_quarantine(cfg, records):
    if not records:
        return
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    with open(_quarantine_path(cfg), "a", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def iter_quarantine(cfg):
    """Yield quarantine records (malformed shots recorded, not silently dropped)."""
    p = _quarantine_path(cfg)
    if not p.exists():
        return
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _atomic_write_jsonl_gz(path, records, ensure_ascii=True):
    """Write gz-compressed JSONL ATOMICALLY (temp file -> fsync -> os.replace), so a crash
    or reap mid-write never leaves a torn shard that still reads as valid
    (SERIALIZER_REVIEW atomicity). `mtime=0` keeps the gzip byte-for-byte reproducible so
    checksums are stable. Returns the final path."""
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", mtime=0) as gz:
            for rec in records:
                gz.write((json.dumps(rec, ensure_ascii=ensure_ascii) + "\n").encode("utf-8"))
        raw.flush()
        os.fsync(raw.fileno())   # durable before the atomic rename
    os.replace(tmp, path)        # atomic on POSIX
    return path


def _write_shard(cfg, shard_idx, tidy_records):
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    return _atomic_write_jsonl_gz(cfg.out_dir / f"shard_{shard_idx:05d}.jsonl.gz",
                                  tidy_records, ensure_ascii=True)


# --- Bronze: PII-stripped immutable raw layer (SERIALIZER_REVIEW §5) ------
# Keep the raw API payload (minus PII) beside the normalized record so a later
# normalizer fix re-normalizes OFFLINE instead of losing data to the API's
# ephemeral recent-updated window. Never committed (gitignored with the store).
_BRONZE_SCHEMA_VERSION = 1


def _strip_pii(raw):
    """Drop every direct-identifier / free-text field before the payload is stored.
    Only a salted one-way user hash is retained, in the Bronze wrapper (not here)."""
    return {k: v for k, v in raw.items() if k not in _PRIVACY_DROP}


def _bronze_record(cfg, raw, tidy):
    """Wrap one PII-stripped raw payload with the metadata needed to re-normalize it
    later: id, updated_at, the salted user hash, and a content hash of the payload."""
    payload = _strip_pii(raw)
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return {
        "bronze_schema_version": _BRONZE_SCHEMA_VERSION,
        "id": tidy.get("id"),
        "updated_at": tidy.get("updated_at"),
        "hashed_user": tidy.get("hashed_user"),
        "content_sha256": hashlib.sha256(blob.encode("utf-8")).hexdigest(),
        "payload": payload,
    }


def _write_bronze_shard(cfg, shard_idx, bronze_records):
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    return _atomic_write_jsonl_gz(cfg.out_dir / f"bronze_{shard_idx:05d}.jsonl.gz",
                                  bronze_records, ensure_ascii=False)


def iter_bronze(cfg):
    """Yield every stored Bronze record (PII-stripped raw payload + wrapper)."""
    for shard in sorted(cfg.out_dir.glob("bronze_*.jsonl.gz")):
        with gzip.open(shard, "rt", encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    yield json.loads(line)


def renormalize_from_bronze(cfg, dst_dir):
    """Re-run the CURRENT normalizer over stored Bronze payloads, OFFLINE (no network),
    writing a fresh normalized store (shards + index) into `dst_dir`. This is the payoff
    of Bronze: a normalizer fix (e.g. the enjoyment-scale or flow-semantics corrections)
    can be applied to shots already harvested, even after they age out of the API window.
    The stored salted user hash is re-injected so identities are preserved without the raw
    user_id ever being retained. Returns a summary dict."""
    dst = replace(cfg, out_dir=Path(dst_dir))
    dst.out_dir.mkdir(parents=True, exist_ok=True)
    buf, idx_buf, shard_idx, n = [], [], 0, 0
    for b in iter_bronze(cfg):
        tidy = normalize_shot(b.get("payload") or {}, dst,
                              hashed_user_override=b.get("hashed_user"))
        buf.append(tidy)
        idx_buf.append(_index_row(tidy))
        n += 1
        if len(buf) >= dst.shard_size:
            _write_shard(dst, shard_idx, buf)
            _append_index(dst, idx_buf)
            shard_idx += 1
            buf, idx_buf = [], []
    if buf:
        _write_shard(dst, shard_idx, buf)
        _append_index(dst, idx_buf)
        shard_idx += 1
    return {"n_records": n, "n_shards": shard_idx}


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


# --- run manifest: per-crawl provenance so a paper can name its exact corpus state (§10) --
_HARVEST_VERSION = 1        # bump when the store layout / crawl contract changes


def _git_commit():
    """Best-effort current git commit for provenance; None if git is unavailable."""
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"],
                             capture_output=True, text=True, timeout=5)
        return out.stdout.strip() if out.returncode == 0 and out.stdout.strip() else None
    except Exception:
        return None


def _runs_dir(cfg):
    return cfg.out_dir / "_runs"


def _write_run_manifest(cfg, manifest):
    d = _runs_dir(cfg)
    d.mkdir(parents=True, exist_ok=True)
    path = d / ("%s.json" % manifest["run_id"])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, sort_keys=True)
    return path


def iter_run_manifests(cfg):
    """Yield the per-run manifests written by past crawls (provenance ledger)."""
    d = _runs_dir(cfg)
    if not d.exists():
        return
    for p in sorted(d.glob("*.json")):
        with open(p, encoding="utf-8") as fh:
            yield json.load(fh)


def _crawl(cfg, updated_after):
    """Shared crawl body for full/incremental. Returns a run summary dict."""
    # Ensure the destination exists BEFORE the first disk-space check (SERIALIZER_REVIEW
    # §2): the per-100 disk guard fires on the first iteration (n_fetched==0), which on a
    # fresh out_dir would raise FileNotFoundError before any shard write creates it.
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    session = _requests().Session()
    limiter = _RateLimiter(cfg.max_req_per_min)
    # §4 version-aware dedup: id -> latest stored updated_at. We fetch a listed shot only
    # when it is new OR its updated_at is newer than what we hold (an edit); an already-held
    # version is skipped WITHOUT a fetch. This captures edits (as new versions) instead of
    # the old "skip if id seen" which silently missed every edit on a periodic re-list.
    seen_versions = latest_index_map(cfg)
    shard_idx = _next_shard_idx(cfg)
    buffer, index_buffer, bronze_buffer = [], [], []
    n_fetched = n_new = n_updated = n_quarantined = 0
    started_at = time.time()
    # Unique per run: time_ns + random suffix. `run_%d_%d % (seconds, pid)` collided for two
    # runs started in the same second under one process, overwriting a manifest (P1-8).
    run_id = "run_%d_%s" % (time.time_ns(), os.urandom(4).hex())
    max_updated = _load_cursor(cfg).get("last_updated_at")

    def flush():
        nonlocal shard_idx, buffer, index_buffer, bronze_buffer
        if buffer:
            _write_shard(cfg, shard_idx, buffer)
            if cfg.store_bronze and bronze_buffer:
                _write_bronze_shard(cfg, shard_idx, bronze_buffer)  # 1:1 with the shard idx
            _append_index(cfg, index_buffer)
            shard_idx += 1
            buffer, index_buffer, bronze_buffer = [], [], []

    # LISTING-PAGE RESUME (full crawl only): the API lists newest-first, 100/page, with
    # no start-time filter, so reaching un-fetched OLDER shots means paging past the ones
    # we already have. Persist the page reached; on resume, rewind a few pages (new shots
    # shift boundaries) and let id-dedup absorb the overlap -- turns a ~N/100-page re-list
    # into a handful of pages. Incremental crawls use the updated_after cursor instead.
    use_page_resume = updated_after is None
    _REWIND = 3
    start_page = max(1, _load_list_page(cfg) - _REWIND) if use_page_resume else 1
    cur_page = start_page
    completed = False
    stopped_early = None
    try:
        for page, sid, _clock, upd in list_public_shot_ids(
                cfg, updated_after=updated_after, start_page=start_page,
                _session=session, _limiter=limiter):
            cur_page = page
            if cfg.max_requests is not None and n_fetched >= cfg.max_requests:
                break
            upd_i = _as_int(upd, default=None)
            have = seen_versions.get(sid)
            if have is not None and upd_i is not None and upd_i <= have:
                continue  # §4: already hold this version (or newer) -- no fetch
            # DISK GUARD: never fill the drive -- stop gracefully (finally-flush saves)
            # if free space drops below the floor. Checked every 100 fetched shots (cheap).
            if n_fetched % 100 == 0:
                free_gb = shutil.disk_usage(cfg.out_dir).free / (1024 ** 3)
                if free_gb < cfg.min_free_gb:
                    stopped_early = "low_disk: %.2f GB free < %.2f GB floor" % (
                        free_gb, cfg.min_free_gb)
                    break
            try:
                raw = fetch_shot(cfg, sid, _session=session, _limiter=limiter)
            except Exception as exc:
                # a persistent 429/5xx (retries exhausted), network drop, or a listing
                # error: STOP GRACEFULLY so the finally-block preserves everything
                # fetched so far. Re-running `full` resumes (id-dedup skips done shots).
                stopped_early = "%s: %s" % (type(exc).__name__, exc)
                break
            n_fetched += 1
            # §9: a single malformed record must not abort the crawl AND must not vanish
            # silently -- it is written to the quarantine ledger with a reason + content hash.
            try:
                tidy = normalize_shot(raw, cfg)
            except Exception as exc:
                n_quarantined += 1
                _append_quarantine(cfg, [_quarantine_record(
                    run_id, sid, upd, raw, "normalize", exc)])
                continue
            try:
                json.dumps(tidy, allow_nan=False)  # §9: NaN/Inf must never enter a shard
            except Exception as exc:
                n_quarantined += 1
                _append_quarantine(cfg, [_quarantine_record(
                    run_id, sid, upd, raw, "serialize", exc)])
                continue
            if sid not in seen_versions:
                n_new += 1        # a shot id we had never stored before
            elif upd_i is not None and have is not None and upd_i > have:
                n_updated += 1    # a newer version of a shot we already held (an edit)
            # record/refresh the latest version we now hold (from the record, fallback list)
            stored_upd = _as_int(tidy.get("updated_at"), default=upd_i)
            if stored_upd is not None:
                seen_versions[sid] = (stored_upd if have is None
                                      else max(have, stored_upd))
            elif sid not in seen_versions:
                seen_versions[sid] = -1
            buffer.append(tidy)
            index_buffer.append(_index_row(tidy))
            if cfg.store_bronze:
                # store the PII-stripped raw BEFORE it is lost -- kept 1:1 with `buffer`
                bronze_buffer.append(_bronze_record(cfg, raw, tidy))
            if upd is not None:
                max_updated = upd if max_updated is None else max(max_updated, upd)
            if len(buffer) >= cfg.shard_size:
                flush()
                if use_page_resume:
                    _save_list_page(cfg, cur_page)   # checkpoint the listing position
        else:
            completed = True   # loop exhausted naturally = full crawl reached the oldest
    finally:
        # NEVER lose the in-progress buffer or the resume cursor -- runs on normal exit,
        # exception, or interruption (environment reap / Ctrl-C).
        flush()
        # P0-2: only advance the durable incremental cursor when the run COMPLETED. The
        # source lists newest-first, so on an interrupted run max(updated_at seen) is past
        # records not yet fetched; committing it would make the next `updated_after` query
        # skip them permanently. On an incomplete run keep the prior cursor (re-listing
        # re-sees already-stored versions, which version-aware dedup skips cheaply).
        if completed and max_updated is not None:
            _save_cursor(cfg, max_updated)
        if use_page_resume:
            # completed -> reset to page 1 so the next run re-scans newest for new shots;
            # interrupted -> save the page reached so the next run resumes near it.
            _save_list_page(cfg, 1 if completed else cur_page)
    summary = {
        "run_id": run_id,
        "n_fetched": n_fetched, "n_new": n_new, "n_updated": n_updated,
        "n_quarantined": n_quarantined,
        "rate_limit_wait_s": round(limiter.total_wait_s, 1),
        "cursor": max_updated, "stopped_early": stopped_early,
        "resumed_from_page": start_page, "last_page": cur_page, "completed": completed,
    }
    # §10 per-run provenance manifest: which corpus state a paper/model was built on.
    manifest = dict(summary)
    manifest.update({
        "mode": "full" if updated_after is None else "incremental",
        "harvest_version": _HARVEST_VERSION,
        "normalizer_schema_version": _NORMALIZE_SCHEMA_VERSION,
        "bronze_schema_version": _BRONZE_SCHEMA_VERSION,
        "puckworks_commit": _git_commit(),
        "started_at": started_at,
        "completed_at": time.time(),
        "store_bronze": cfg.store_bronze,
        "salt_fingerprint": hashlib.sha256(cfg.salt.encode("utf-8")).hexdigest()[:12],
        "config": {"base_url": cfg.base_url, "max_req_per_min": cfg.max_req_per_min,
                   "shard_size": cfg.shard_size, "min_free_gb": cfg.min_free_gb},
    })
    try:
        _write_run_manifest(cfg, manifest)
    except Exception:
        pass   # a manifest write failure must never sink an otherwise-successful crawl
    return summary


def harvest_all(cfg):
    """Initial full crawl: walk public ids, fetch, normalize, write shards +
    _index.csv + _cursor.json. Safely re-runnable (dedups on id)."""
    return _crawl(cfg, updated_after=None)


def harvest_incremental(cfg):
    """Periodic top-up: re-list the public window and fetch only shots that are new or
    have a newer `updated_at` than the version we already hold (§4 version-aware dedup).
    Edits are appended as new versions; the latest-view reader (`iter_store_latest`,
    `latest_index_rows`) collapses to one current record per shot (§3). Safe to re-run:
    an unchanged shot is skipped without a fetch, so no duplicate accumulation."""
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


def rebuild_index(cfg):
    """Regenerate `_index.csv` from the shards -- the index is DERIVED metadata, not the
    source of record identity (SERIALIZER_REVIEW: index is rebuildable). Atomic replace.
    Returns the number of rows written."""
    rows = [_index_row(rec) for rec in iter_store(cfg)]
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    dst = _index_path(cfg)
    tmp = dst.with_name(dst.name + ".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=_INDEX_COLUMNS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, dst)
    return len(rows)


def _version_key(d):
    """Content-addressed version identity (P0-3/P1-1): (id, updated_at, content_sha256)."""
    return (d.get("id"), _as_int(d.get("updated_at"), default=-1),
            d.get("content_sha256") or "")


def reconcile_store(cfg):
    """Verify store integrity (SERIALIZER_REVIEW reconciliation). Non-destructive; returns a
    report dict: `ok` plus any problems. Compares the exact MULTISET of content-addressed
    version keys `(id, updated_at, content_sha256)` between shards and index (not just id
    sets, which missed a stored version absent from the index — P1-1), flags duplicate
    version keys and unreadable shards, and checks the latest view is one-per-id."""
    problems = []
    shard_keys, n_records = Counter(), 0
    for shard in sorted(cfg.out_dir.glob("shard_*.jsonl.gz")):
        try:
            with gzip.open(shard, "rt", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    n_records += 1
                    shard_keys[_version_key(rec)] += 1
        except Exception as exc:                       # torn / corrupt shard
            problems.append("unreadable_shard:%s:%s" % (shard.name, exc))
    index_keys, n_index = Counter(), 0
    for row in iter_index_rows(cfg):
        n_index += 1
        index_keys[_version_key(row)] += 1
    in_shards_not_index = shard_keys - index_keys
    in_index_not_shards = index_keys - shard_keys
    n_dup_versions = sum(c - 1 for c in shard_keys.values() if c > 1)
    if in_shards_not_index:
        problems.append("versions_in_shards_not_index:%d" % sum(in_shards_not_index.values()))
    if in_index_not_shards:
        problems.append("index_versions_not_in_shards:%d" % sum(in_index_not_shards.values()))
    if n_dup_versions:
        problems.append("duplicate_version_keys:%d" % n_dup_versions)
    shard_ids = {k[0] for k in shard_keys}
    n_latest = len(latest_index_rows(cfg))
    if shard_ids and n_latest != len(shard_ids):
        problems.append("latest_view_not_one_per_id:%d!=%d" % (n_latest, len(shard_ids)))
    return {
        "ok": not problems,
        "n_shard_records": n_records,
        "n_index_rows": n_index,
        "n_unique_ids": len(shard_ids),
        "n_latest": n_latest,
        "n_versions_extra": n_records - len(shard_ids),   # edits stored beyond one-per-id
        "n_bronze": sum(1 for _ in iter_bronze(cfg)),
        "n_quarantined": sum(1 for _ in iter_quarantine(cfg)),
        "problems": problems,
    }


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
    """Aggregate coverage/mix/unit-audit statistics over the store (no per-shot rows).
    Uses the §3 latest-version view so re-listed/edited shots are counted once."""
    total = 0
    machines, grinders = {}, {}
    n_tds = n_ey = n_sensory = 0
    durations, peak_pressure, peak_flow = [], [], []
    unit_audit = {"missing_timeframe": 0, "flow_unit_ambiguous": 0,
                  "length_mismatch": 0, "missing_machine": 0}
    for shot in iter_store_latest(cfg):
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
        # §8: only the CONFIRMED scale-derived mass flow is a kg/s quantity; the ambiguous
        # reported flow is native and must not enter a mass-flow histogram.
        pf = [x for x in (hy.get("mass_flow_from_scale__kg_per_s") or []) if x is not None]
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
    p.add_argument("cmd", choices=["full", "incremental", "stats", "reconcile",
                                   "rebuild-index"])
    p.add_argument("--max-requests", type=int, default=None)
    p.add_argument("--req-per-min", type=int, default=18)  # under 200/10min IP limit
    p.add_argument("--out", default=str(_DEFAULT_OUT))
    p.add_argument("--min-free-gb", type=float, default=1.0,
                   help="stop gracefully if the drive drops below this many GB free")
    p.add_argument("--write-aggregate", action="store_true",
                   help="stats: also (re)write the tracked aggregate_stats.csv")
    a = p.parse_args(argv)
    cfg = HarvestConfig(out_dir=a.out, max_req_per_min=a.req_per_min,
                        max_requests=a.max_requests, min_free_gb=a.min_free_gb)
    if a.cmd == "full":
        summary = harvest_all(cfg)
        _print_summary("visualizer harvest (full)", summary)
    elif a.cmd == "incremental":
        summary = harvest_incremental(cfg)
        _print_summary("visualizer harvest (incremental)", summary)
    elif a.cmd == "reconcile":
        _print_summary("visualizer store reconcile", reconcile_store(cfg))
    elif a.cmd == "rebuild-index":
        n = rebuild_index(cfg)
        print("  rebuilt _index.csv from shards: %d rows" % n)
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

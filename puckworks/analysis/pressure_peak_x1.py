"""X1 plug-in rheology and staged, read-only Visualizer scoping. No model fits."""

from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

from puckworks import data
from puckworks.data.corpus_freeze import _source_state
from puckworks.data.visualizer_store import CorpusSnapshot
from puckworks.lib.visualizer_harvest import latest_index_rows
from puckworks.models.pannusch2024.closures import water_density, water_viscosity

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_X1"
MC = 28.709461834955388
LABELS = ("DE1/Decent", "Meticulous", "Gaggiuino/GaggiMate", "other/unknown")
POOLED = "reported labels pooled"
CREDIT = "Data source: Visualizer; thanks to the contributing users who made their shots public."
TOKEN = re.compile(r'"(?:[^"\\]|\\.)*"|[{}\[\]]')
STRING = re.compile(r'"(?:[^"\\]|\\.)*"')
DECODER = json.JSONDecoder()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open("w", newline="") as f:
        writer = csv.DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(rows)


def table_root(t, ratio):
    """Invert measured, piecewise-linear concentration dependence only in-domain."""
    if not 295 <= t <= 365:
        return None, None, None, "TEMPERATURE_OUTSIDE_TABLE"
    xs = sorted({float(r["Xw_pct"]) for r in data.telisromero_table1_eta()})
    ys = [data.telisromero_eta_measured(t, x) for x in xs]
    muw = float(water_viscosity(t))
    target = ratio * muw
    for x0, x1, y0, y1 in zip(xs, xs[1:], ys, ys[1:]):
        if y1 <= target <= y0:
            x = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
            return x, ys[-1] / muw, ys[0] / muw, "IN_DOMAIN_INTERPOLATION"
    return None, ys[-1] / muw, ys[0] / muw, "TARGET_NOT_BRACKETED"


def property_rows():
    coef = data.telisromero_rheology_closures()["eq10_newtonian"]
    volume = math.pi * (0.058 / 2) ** 2 * 0.014
    rows = []
    for t in (363.15, 369.15, 365.0):
        muw = float(water_viscosity(t))
        rho = float(water_density(t))
        for ratio in (2.7, math.e):
            for method in ("Eq10", "Table1"):
                if method == "Eq10":
                    pre = float(coef["pre_factor"]) * math.exp(float(coef["Ea_or_A"]) / (8.314 * t))
                    x = (ratio * muw / pre) ** (1 / float(coef["Xw_exponent"]))
                    domain = "IN_DOMAIN" if 295 <= t <= 365 and 76 <= x <= 90 else "EXTRAPOLATED"
                    low = high = None
                else:
                    x, low, high, domain = table_root(t, ratio)
                rows.append(
                    dict(
                        method=method,
                        temperature_C=t - 273.15,
                        temperature_K=t,
                        temperature_role="TABLE_EDGE_ONLY"
                        if t == 365
                        else "SOURCE_WINDOW_SENSITIVITY",
                        target_ratio=ratio,
                        water_viscosity_Pa_s=muw,
                        target_viscosity_Pa_s=ratio * muw,
                        water_percent=x,
                        solids_mass_fraction=None if x is None else 1 - x / 100,
                        solids_wt_percent=None if x is None else 100 - x,
                        domain=domain,
                        table_min_ratio=low,
                        table_max_ratio=high,
                        water_density_kg_m3=rho,
                        bed_volume_ml=volume * 1e6,
                        Mc_g=MC,
                        Mc_pore_volumes_times_porosity=MC / 1000 / (rho * volume),
                    )
                )
    return rows


def _skip(text, i):
    """Find a JSON value's end without decoding its scalar/array values."""
    if text[i] == '"':
        return STRING.match(text, i).end()
    if text[i] in "[{":
        depth = 0
        for match in TOKEN.finditer(text, i):
            token = match.group()
            if token[0] == '"':
                continue
            depth += 1 if token in "[{" else -1
            if depth == 0:
                return match.end()
        raise ValueError("Unclosed JSON container")
    match = re.match(r"[^,}\]\s]+", text[i:])
    return i + match.end()


def project(text, wanted, i=0):
    """Decode only named fields; LENGTH inspects scalar-array structure, not values."""
    i += len(text[i:]) - len(text[i:].lstrip())
    if text[i] != "{":
        return {}, _skip(text, i)
    result = {}
    i += 1
    while True:
        while text[i].isspace() or text[i] == ",":
            i += 1
        if text[i] == "}":
            return result, i + 1
        key, i = DECODER.raw_decode(text, i)
        while text[i].isspace() or text[i] == ":":
            i += 1
        spec = wanted.get(key, False)
        if isinstance(spec, dict):
            result[key], i = project(text, spec, i)
        elif spec is True:
            result[key], i = DECODER.raw_decode(text, i)
        else:
            end = _skip(text, i)
            if spec == "LENGTH":
                body = text[i:end]
                result[key] = (
                    (body.count(",") + 1 if body[1:-1].strip() else 0)
                    if body.startswith("[")
                    else None
                )
            i = end


def machine_label(*values):
    found = set()
    for value in values:
        text = str(value or "").lower()
        if re.search(r"\bde1(?:\+|pro|xl|xxl)?\b|\bdecent\b", text):
            found.add(LABELS[0])
        if "meticulous" in text:
            found.add(LABELS[1])
        if "gaggiuino" in text or "gaggimate" in text:
            found.add(LABELS[2])
    return next(iter(found)) if len(found) == 1 else LABELS[3]


def numeric(values):
    return np.array(
        [
            float(x) if isinstance(x, (int, float)) and not isinstance(x, bool) else np.nan
            for x in values
        ],
        dtype=float,
    )


def support_blocks(t, p):
    blocks, start = [], None
    for i in range(len(t)):
        valid = np.isfinite(t[i]) and np.isfinite(p[i])
        if start is not None and (not valid or t[i] <= t[i - 1]):
            blocks.append((start, i))
            start = None
        if valid and start is None:
            start = i
    if start is not None:
        blocks.append((start, len(t)))
    return blocks


def resolution(p, blocks):
    diffs = [
        abs(float(p[i + 1] - p[i])) for a, b in blocks for i in range(a, b - 1) if p[i + 1] != p[i]
    ]
    return min(diffs) if diffs else None


def phase(states, start, end):
    """No inference from firmware codes; only explicit named states are interpreted."""
    values = {str(s).lower().strip() for s in states[start:end] if s is not None}
    if values & {"idle", "off", "pump-off", "venting", "steam", "hotwater"}:
        return "explicit_non_brewing"
    return "active_brew" if values and values <= {"espresso", "brewing"} else "state_unknown"


def sweep_runs(t, p, blocks, tolerance):
    candidates = []
    if tolerance is None:
        return candidates
    for a, b in blocks:
        start, low = a, p[a]
        runs = []
        for i in range(a + 1, b):
            # A reversal's full upward excursion is bounded, not each accumulating step.
            if p[i] - low > tolerance:
                runs.append((start, i))
                start, low = i, p[i]
            low = min(low, p[i])
        runs.append((start, b))
        for s, e in runs:
            if p[s] < 9e5 or min(p[s:e]) > 5e5:
                continue
            times = []
            for level in (9e5, 5e5):
                k = s + next(k for k, x in enumerate(p[s:e]) if x <= level)
                times.append(
                    float(
                        t[k]
                        if k == s
                        else t[k - 1] + (level - p[k - 1]) * (t[k] - t[k - 1]) / (p[k] - p[k - 1])
                    )
                )
            if times[1] > times[0]:
                candidates.append(dict(start=s, end=e, t0=times[0], t1=times[1]))
    return candidates


def flat_runs(t, p, blocks, delta):
    candidates = []
    if delta is None:
        return candidates
    for a, b in blocks:
        for start in range(a, b):
            ordered, last = [], None
            for end in range(start, b):
                bisect.insort(ordered, p[end])
                if ordered[-1] - ordered[0] > 2 * delta:
                    break
                if t[end] - t[start] < 10:
                    continue
                n = len(ordered)
                med = (ordered[(n - 1) // 2] + ordered[n // 2]) / 2
                if 6e5 <= med <= 10e5 and max(med - ordered[0], ordered[-1] - med) <= delta:
                    last = dict(
                        start=start,
                        end=end + 1,
                        t0=float(t[start]),
                        t1=float(t[end]),
                        median_pressure_Pa=float(med),
                    )
            if last is not None:
                candidates.append(last)
    maximal, furthest = [], -1
    for c in candidates:
        if c["end"] > furthest:
            maximal.append(c)
            furthest = c["end"]
    return maximal


def authenticate(root, inventory):
    manifest = json.loads(Path(inventory).read_text())
    expected = {
        Path(r["relative_path"]).name: r["sha256"]
        for r in manifest["entries"]
        if r["relative_path"].startswith("visualizer/crawl_v6_20260715/")
        and (
            Path(r["relative_path"]).name.startswith(("shard_", "bronze_"))
            or Path(r["relative_path"]).name == "_index.csv"
        )
    }
    state = _source_state(Path(root))
    if not expected or state["files"] != expected:
        raise RuntimeError("Visualizer files differ from the owner inventory; stop")
    snapshot = CorpusSnapshot(root, classification="current-state")
    return snapshot, dict(
        source_aggregate_sha256=state["aggregate_sha256"],
        inventory_identity=manifest["content_identity"],
        files_verified=len(expected),
        integrity=snapshot.integrity_stats(),
    )


def selected_candidates(candidates, states):
    eligible = []
    for c in candidates:
        c["phase"] = phase(states, c["start"], c["end"])
        if c["phase"] != "explicit_non_brewing":
            eligible.append(c)
    return eligible


def select_pressure(root, inventory, private):
    snapshot, audit = authenticate(root, inventory)
    winners = latest_index_rows(snapshot._cfg)
    wanted = {
        "id": True,
        "updated_at": True,
        "content_sha256": True,
        "machine": True,
        "context": {"machine": True},
        "hydraulic": {
            "time__s": True,
            "pressure__Pa": True,
            "weight__kg": "LENGTH",
            "state_change": True,
        },
    }
    counts = {label: Counter() for label in LABELS}
    selected, seen = {}, set()
    for shard in sorted(Path(root).glob("shard_*.jsonl.gz")):
        with gzip.open(shard, "rt") as f:
            for line in f:
                rec, _ = project(line, wanted)
                sid = rec["id"]
                winner = winners.get(sid)
                if (
                    not winner
                    or sid in seen
                    or str(rec.get("updated_at")) != winner["updated_at"]
                    or rec.get("content_sha256") != winner["content_sha256"]
                ):
                    continue
                seen.add(sid)
                label = machine_label(rec.get("machine"), rec.get("context", {}).get("machine"))
                count = counts[label]
                count["canonical_records"] += 1
                hy = rec.get("hydraulic", {})
                times, pressures = hy.get("time__s"), hy.get("pressure__Pa")
                if (
                    not isinstance(times, list)
                    or not isinstance(pressures, list)
                    or len(times) < 2
                    or len(times) != len(pressures)
                    or hy.get("weight__kg") != len(times)
                ):
                    continue
                count["pressure_weight_common_time"] += 1
                t, p = numeric(times), numeric(pressures)
                blocks = support_blocks(t, p)
                delta = resolution(p, blocks)
                count["defined_resolution"] += delta is not None
                count["pressure_spanning_candidates"] += any(
                    max(p[a:b]) >= 9e5 and min(p[a:b]) <= 5e5 for a, b in blocks
                )
                states = hy.get("state_change") or []
                record = dict(id=sid, label=label, t=times, p=pressures, delta_Pa=delta)
                for view, tol in (("strict", 0.0), ("secondary", delta)):
                    candidates = sweep_runs(t, p, blocks, tol)
                    count[view + "_runs_before_state"] += bool(candidates)
                    good = selected_candidates(candidates, states)
                    count[view + "_selected"] += bool(good)
                    count[view + "_multiple"] += len(good) > 1
                    if good:
                        record[view] = good[0]
                        count[view + "_" + good[0]["phase"]] += 1
                flats = selected_candidates(flat_runs(t, p, blocks, delta), states)
                count["flat_selected"] += bool(flats)
                count["flat_multiple"] += len(flats) > 1
                if flats:
                    record["flat"] = flats[0]
                    count["flat_" + flats[0]["phase"]] += 1
                if any(k in record for k in ("flat", "strict", "secondary")):
                    selected[sid] = record
    if len(seen) != len(winners):
        raise RuntimeError("Canonical index/shard join incomplete")
    audit.update(
        plan_sha256=sha(OUT / "PLAN.md"), weight_values_decoded=False, flow_values_decoded=False
    )
    result = dict(audit=audit, counts={k: dict(v) for k, v in counts.items()}, selected=selected)
    Path(private).mkdir(parents=True, exist_ok=True)
    path = Path(private) / "selection.json"
    path.write_text(json.dumps(result, allow_nan=False))
    return audit, counts, sha(path)


def interval_value(t, values, at):
    """Right interval at internal knots, last interval at the support end."""
    if at < t[0] or at > t[-1]:
        return float("nan")
    return float(values[min(np.searchsorted(t, at, side="right") - 1, len(values) - 1)])


def segment_flow(record, weights, window):
    s, e = window["start"], window["end"]
    t = numeric(record["t"])[s:e]
    p = numeric(record["p"])[s:e]
    w = numeric(weights)[s:e] * 1000  # normalized kg to grams
    t0, t1 = window["t0"], window["t1"]
    # Crossings may be between samples. Insert only the two window boundaries.
    inside = (t > t0) & (t < t1)
    tw = np.r_[t0, t[inside], t1]
    ww = np.interp(tw, t, w)
    pp = np.interp(tw, t, p)
    q = np.diff(ww) / np.diff(tw)
    duration = t1 - t0
    mean = (ww[-1] - ww[0]) / duration
    normalizer = (ww[-1] - np.interp(t1 - duration / 4, tw, ww)) / (duration / 4)
    return dict(
        id=record["id"],
        label=record["label"],
        phase=window["phase"],
        t=(tw - t0).tolist(),
        p=pp.tolist(),
        w=ww.tolist(),
        q=q.tolist(),
        duration_s=duration,
        mean_flow_g_s=float(mean),
        normalizer_g_s=float(normalizer),
        usable=bool(np.isfinite(mean) and np.isfinite(q).any()),
        negative_increments=bool(np.any(np.diff(ww) < 0)),
        missing_weight=bool(not np.isfinite(ww).all()),
    )


def group_segments(segments, label):
    return [s for s in segments if s["usable"] and (label == POOLED or s["label"] == label)]


def flow_bins(segments):
    rows = []
    for label in (*LABELS, POOLED):
        group = group_segments(segments, label)
        means = np.array([s["mean_flow_g_s"] for s in group])
        b1, b2 = np.quantile(means, [1 / 3, 2 / 3], method="linear") if group else (None, None)
        for tercile in ("all", 1, 2, 3):
            chosen = (
                group
                if tercile == "all"
                else [
                    s
                    for s in group
                    if 1 + int(s["mean_flow_g_s"] > b1) + int(s["mean_flow_g_s"] > b2) == tercile
                ]
            )
            rows.append(
                dict(
                    stratum=label,
                    tercile=tercile,
                    b1_g_s=b1,
                    b2_g_s=b2,
                    segments=len(chosen),
                    mean_flow_min_g_s=min((s["mean_flow_g_s"] for s in chosen), default=None),
                    mean_flow_max_g_s=max((s["mean_flow_g_s"] for s in chosen), default=None),
                    median_duration_s=float(np.median([s["duration_s"] for s in chosen]))
                    if chosen
                    else None,
                    label_composition=json.dumps(
                        dict(Counter(s["label"] for s in chosen)), sort_keys=True
                    ),
                    credit=CREDIT,
                )
            )
    return rows


def clean_json(value):
    """Private JSON uses null for absent numeric support, never invented values."""
    if isinstance(value, dict):
        return {k: clean_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [clean_json(v) for v in value]
    return None if isinstance(value, float) and not math.isfinite(value) else value


def prepare_flow(root, inventory, private):
    private = Path(private)
    selection = json.loads((private / "selection.json").read_text())
    if selection["audit"]["plan_sha256"] != sha(OUT / "PLAN.md"):
        raise RuntimeError("Plan changed after pressure selection; stop")
    snapshot, audit = authenticate(root, inventory)
    winners = latest_index_rows(snapshot._cfg)
    selected = selection["selected"]
    segments, sweeps, seen = [], [], set()
    for shard in sorted(Path(root).glob("shard_*.jsonl.gz")):
        with gzip.open(shard, "rt") as f:
            for line in f:
                meta, _ = project(line, {"id": True, "updated_at": True, "content_sha256": True})
                sid = meta["id"]
                winner = winners.get(sid)
                if (
                    sid not in selected
                    or sid in seen
                    or str(meta.get("updated_at")) != winner["updated_at"]
                    or meta.get("content_sha256") != winner["content_sha256"]
                ):
                    continue
                seen.add(sid)
                rec, _ = project(line, {"hydraulic": {"weight__kg": True}})
                weights = rec["hydraulic"]["weight__kg"]
                record = selected[sid]
                for view in ("flat", "strict", "secondary"):
                    if view not in record:
                        continue
                    segment = segment_flow(record, weights, record[view])
                    segment["view"] = view
                    (segments if view == "flat" else sweeps).append(segment)
    if seen != set(selected):
        raise RuntimeError("Selected weight join incomplete; stop")
    # Persist bins first. No collapse function is invoked by this phase.
    bins = flow_bins(segments)
    write_csv(OUT / "MEAN_FLOW_BINS.csv", bins)
    grids = []
    for label in (*LABELS, POOLED):
        group = group_segments(segments, label)
        median = float(np.median([s["mean_flow_g_s"] for s in group])) if group else None
        for j in range(21):
            grids.append(
                dict(
                    stratum=label,
                    segments=len(group),
                    qbar_med_g_s=median,
                    j=j,
                    time_s=j / 2,
                    primary_mass_g=None if median is None else median * j / 2,
                    secondary_mass_g=MC * j / 20,
                    credit=CREDIT,
                )
            )
    write_csv(OUT / "CLOCK_GRIDS.csv", grids)
    payload = clean_json(
        dict(
            segments=segments,
            sweeps=sweeps,
            selection_sha256=sha(private / "selection.json"),
            plan_sha256=sha(OUT / "PLAN.md"),
            bins_sha256=sha(OUT / "MEAN_FLOW_BINS.csv"),
            grids_sha256=sha(OUT / "CLOCK_GRIDS.csv"),
        )
    )
    (private / "flow-prepared.json").write_text(json.dumps(payload, allow_nan=False))
    return bins, [g for g in grids if g["j"] == 0]


def mass_value(segment, target):
    q = numeric(segment["q"])
    w = numeric(segment["w"]) - segment["w"][0]
    if target == 0:
        return float(q[0]), 0
    crossings = np.flatnonzero((w[:-1] < target) & (target <= w[1:]) & (np.diff(w) > 0))
    return (float(q[crossings[0]]), len(crossings)) if len(crossings) else (float("nan"), 0)


def collapse(group, grid):
    points = []
    for j, (time, mass) in enumerate(grid):
        pairs, repeated = [], 0
        if mass is not None:
            for s in group:
                normalizer = s["normalizer_g_s"]
                if normalizer is None or normalizer == 0:
                    continue
                qm, n = mass_value(s, mass)
                qt = interval_value(numeric(s["t"]), numeric(s["q"]), time)
                if np.isfinite(qm) and np.isfinite(qt):
                    pairs.append((qm / normalizer, qt / normalizer))
                    repeated += n > 1
        pairs = np.asarray(pairs)
        points.append(
            dict(
                j=j,
                time_s=time,
                mass_g=mass,
                contributors=len(pairs),
                repeated_crossing_segments=repeated,
                mass_variance=float(np.var(pairs[:, 0], ddof=0)) if len(pairs) >= 2 else None,
                time_variance=float(np.var(pairs[:, 1], ddof=0)) if len(pairs) >= 2 else None,
            )
        )
    supported = [p for p in points if p["mass_variance"] is not None]
    ms = math.sqrt(np.mean([p["mass_variance"] for p in supported])) if supported else None
    ts = math.sqrt(np.mean([p["time_variance"] for p in supported])) if supported else None
    summary = dict(
        segments=len(group),
        supported_indices=len(supported),
        j_min=min((p["j"] for p in supported), default=None),
        j_max=max((p["j"] for p in supported), default=None),
        mass_spread=ms,
        time_spread=ts,
        mass_minus_time=None if ms is None else ms - ts,
        direction="unavailable"
        if ms is None
        else "mass"
        if ms < ts
        else "time"
        if ts < ms
        else "tie",
    )
    return summary, points


def calculate_collapse(private):
    private = Path(private)
    payload = json.loads((private / "flow-prepared.json").read_text())
    for key, path in (
        ("plan_sha256", OUT / "PLAN.md"),
        ("bins_sha256", OUT / "MEAN_FLOW_BINS.csv"),
        ("grids_sha256", OUT / "CLOCK_GRIDS.csv"),
        ("selection_sha256", private / "selection.json"),
    ):
        if payload[key] != sha(path):
            raise RuntimeError(f"Pre-metric input changed: {key}; stop")
    bins = list(csv.DictReader((OUT / "MEAN_FLOW_BINS.csv").open()))
    grids = list(csv.DictReader((OUT / "CLOCK_GRIDS.csv").open()))
    summaries, points = [], []
    for binrow in bins:
        label, tercile = binrow["stratum"], binrow["tercile"]
        group = group_segments(payload["segments"], label)
        if tercile != "all" and group:
            b1, b2 = float(binrow["b1_g_s"]), float(binrow["b2_g_s"])
            group = [
                s
                for s in group
                if 1 + int(s["mean_flow_g_s"] > b1) + int(s["mean_flow_g_s"] > b2) == int(tercile)
            ]
        for view, col in (
            ("primary_median_matched", "primary_mass_g"),
            ("secondary_Mc_later_sampling_bias", "secondary_mass_g"),
        ):
            grid = [
                (float(g["time_s"]), float(g[col]) if g[col] else None)
                for g in grids
                if g["stratum"] == label
            ]
            summary, pts = collapse(group, grid)
            prefix = dict(
                stratum=label,
                tercile=tercile,
                grid_view=view,
                role="PRIMARY_CLOCK_COMPARISON"
                if tercile == "all" and view.startswith("primary")
                else "DESCRIPTIVE_ONLY",
            )
            summaries.append(dict(**prefix, **summary, credit=CREDIT))
            points.extend(dict(**prefix, **p, credit=CREDIT) for p in pts)
    write_csv(OUT / "COLLAPSE.csv", summaries)
    write_csv(OUT / "COLLAPSE_GRID.csv", points)
    return [r for r in summaries if r["tercile"] == "all"]


def distribution(values, prefix):
    values = [v for v in values if np.isfinite(v)]
    quantiles = np.quantile(values, [0, 0.25, 0.5, 0.75, 1]) if values else [None] * 5
    return {prefix + "_" + k: v for k, v in zip(("min", "q25", "median", "q75", "max"), quantiles)}


def sweep_signs(segment):
    """Interval-flow samples at pressure midpoints; no smoothing or lag repair."""
    p = numeric(segment["p"]) / 1e5
    t = numeric(segment["t"])
    q = numeric(segment["q"])
    mid = (p[:-1] + p[1:]) / 2
    dp, dq = np.diff(mid), np.diff(q)
    finite = np.isfinite(dq) & np.isfinite(dp)
    result = {}
    for name, side in (
        ("above6", (mid[:-1] >= 6) & (mid[1:] >= 6)),
        ("below6", (mid[:-1] <= 6) & (mid[1:] <= 6)),
    ):
        valid = finite & side & (dp != 0)
        slopes = dq[valid] / dp[valid]
        result[name + "_positive"] = int(np.sum(slopes > 0))
        result[name + "_negative"] = int(np.sum(slopes < 0))
        result[name + "_zero"] = int(np.sum(slopes == 0))
        result[name + "_plateau"] = int(np.sum(finite & side & (dp == 0)))
        if len(slopes) == 0:
            pattern = "sparse"
        elif np.all(slopes > 0):
            pattern = "positive_only"
        elif np.all(slopes < 0):
            pattern = "negative_only"
        elif np.all(slopes == 0):
            pattern = "flat_only"
        else:
            pattern = "mixed_or_flat"
        result[name + "_pattern_" + pattern] = 1
        pairs = np.flatnonzero(valid)
        result[name + "_support_min_bar"] = (
            float(min(mid[pairs].min(), mid[pairs + 1].min())) if len(pairs) else None
        )
        result[name + "_support_max_bar"] = (
            float(max(mid[pairs].max(), mid[pairs + 1].max())) if len(pairs) else None
        )
    result["crosses6_unassigned"] = int(
        np.sum(finite & ~(((mid[:-1] >= 6) & (mid[1:] >= 6)) | ((mid[:-1] <= 6) & (mid[1:] <= 6))))
    )
    # Native first downward 6-bar crossing, supported inside the frozen 9-to-5 window.
    ks = np.flatnonzero((p[:-1] >= 6) & (p[1:] <= 6) & (p[:-1] > p[1:]))
    if len(ks):
        k = ks[0]
        tc = t[k] + (6 - p[k]) * (t[k + 1] - t[k]) / (p[k + 1] - p[k])
        q6 = interval_value(t, q, tc)
        for name, value in (("above6", (q6 - q[0]) / -3), ("below6", (q[-1] - q6) / -1)):
            if np.isfinite(value):
                result[
                    name
                    + "_whole_side_"
                    + ("positive" if value > 0 else "negative" if value < 0 else "zero")
                ] = 1
                result[name + "_whole_side_slope_g_s_bar"] = float(value)
    return result


def aggregate_visualizer(private):
    private = Path(private)
    selection = json.loads((private / "selection.json").read_text())
    flow = json.loads((private / "flow-prepared.json").read_text())
    funnels = [
        dict(
            funnel="authenticated_DE1",
            stratum="authenticated_DE1",
            view=view,
            canonical_records=selection["audit"]["integrity"]["n_logical_records"],
            authenticated_DE1=0,
            status="STOPPED_AT_DEVICE_AUTHENTICATION",
            credit=CREDIT,
        )
        for view in ("strict", "secondary")
    ]
    quality, signrows = [], []
    for label in LABELS:
        count = selection["counts"][label]
        for view in ("strict", "secondary", "flat"):
            records = [
                s
                for s in (flow["segments"] if view == "flat" else flow["sweeps"])
                if s["label"] == label and s["view"] == view
            ]
            funnels.append(
                dict(
                    funnel="reported_labels",
                    stratum=label,
                    view=view,
                    canonical_records=count.get("canonical_records", 0),
                    pressure_weight_common_time=count.get("pressure_weight_common_time", 0),
                    defined_resolution=count.get("defined_resolution", 0),
                    pressure_spanning_candidates=count.get("pressure_spanning_candidates", 0)
                    if view != "flat"
                    else None,
                    runs_before_state=count.get(
                        view + "_runs_before_state", count.get("flat_selected", 0)
                    ),
                    pressure_selected=count.get(view + "_selected", 0),
                    multiple_candidates=count.get(view + "_multiple", 0),
                    active_brew=count.get(view + "_active_brew", 0),
                    state_unknown=count.get(view + "_state_unknown", 0),
                    usable_scale_flow=sum(s["usable"] for s in records),
                    status="REPORTED_LABELS_UNVERIFIED",
                    credit=CREDIT,
                )
            )
            for state in ("active_brew", "state_unknown"):
                group = [s for s in records if s["phase"] == state]
                native_steps = []
                maxgaps = []
                for s in group:
                    original = selection["selected"][s["id"]]
                    win = original[view]
                    t = numeric(original["t"])[win["start"] : win["end"]]
                    dt = np.diff(t)[(t[:-1] < win["t1"]) & (t[1:] > win["t0"])]
                    native_steps.extend(dt.tolist())
                    maxgaps.append(float(max(dt)))
                quality.append(
                    dict(
                        stratum=label,
                        view=view,
                        phase=state,
                        selected=len(group),
                        usable_scale_flow=sum(s["usable"] for s in group),
                        missing_weight_segments=sum(s["missing_weight"] for s in group),
                        negative_increment_segments=sum(s["negative_increments"] for s in group),
                        zero_normalizer_segments=sum(s["normalizer_g_s"] == 0 for s in group),
                        negative_normalizer_segments=sum(
                            s["normalizer_g_s"] is not None and s["normalizer_g_s"] < 0
                            for s in group
                        ),
                        unavailable_normalizer_segments=sum(
                            s["normalizer_g_s"] is None for s in group
                        ),
                        **distribution([s["duration_s"] for s in group], "duration_s"),
                        **distribution(native_steps, "native_cadence_s"),
                        **distribution(maxgaps, "largest_native_gap_s"),
                        credit=CREDIT,
                    )
                )
                if view == "flat":
                    continue
                signs = [sweep_signs(s) for s in group if s["usable"]]
                summed = Counter()
                for s in signs:
                    summed.update(
                        {
                            k: v
                            for k, v in s.items()
                            if not any(x in k for x in ("support_", "slope_g"))
                        }
                    )
                for side in ("above6", "below6"):
                    support = [
                        s[side + "_support_min_bar"]
                        for s in signs
                        if s[side + "_support_min_bar"] is not None
                    ]
                    upper = [
                        s[side + "_support_max_bar"]
                        for s in signs
                        if s[side + "_support_max_bar"] is not None
                    ]
                    row = dict(
                        stratum=label,
                        view=view,
                        phase=state,
                        side=side,
                        selected=len(group),
                        usable_scale_flow=len(signs),
                        support_min_bar=min(support, default=None),
                        support_max_bar=max(upper, default=None),
                    )
                    for suffix in (
                        "positive",
                        "negative",
                        "zero",
                        "plateau",
                        "pattern_positive_only",
                        "pattern_negative_only",
                        "pattern_flat_only",
                        "pattern_mixed_or_flat",
                        "pattern_sparse",
                        "whole_side_positive",
                        "whole_side_negative",
                        "whole_side_zero",
                    ):
                        row[suffix] = summed[side + "_" + suffix]
                    row.update(
                        distribution(
                            [
                                s[side + "_whole_side_slope_g_s_bar"]
                                for s in signs
                                if side + "_whole_side_slope_g_s_bar" in s
                            ],
                            "whole_side_slope_g_s_bar",
                        )
                    )
                    row.update(crosses6_unassigned=summed["crosses6_unassigned"], credit=CREDIT)
                    signrows.append(row)
    write_csv(OUT / "VISUALIZER_FUNNELS.csv", funnels)
    write_csv(OUT / "VISUALIZER_QUALITY.csv", quality)
    write_csv(OUT / "SWEEP_SIGNS.csv", signrows)
    return funnels


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase", choices=("properties", "select", "prepare", "collapse", "aggregate")
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--private", type=Path)
    args = parser.parse_args()
    if args.phase == "properties":
        write_csv(OUT / "VISCOSITY_BOUND.csv", property_rows())
        print("Wrote VISCOSITY_BOUND.csv; plug-in only, no fits")
    elif args.phase == "select":
        audit, counts, digest = select_pressure(args.root, args.inventory, args.private)
        print(json.dumps(dict(audit=audit, counts=counts, selection_sha256=digest), indent=2))
    elif args.phase == "prepare":
        bins, grids = prepare_flow(args.root, args.inventory, args.private)
        print(json.dumps(dict(bins=bins, grids=grids), indent=2))
    elif args.phase == "collapse":
        print(json.dumps(calculate_collapse(args.private), indent=2))
    else:
        print(json.dumps(aggregate_visualizer(args.private), indent=2))


if __name__ == "__main__":
    main()

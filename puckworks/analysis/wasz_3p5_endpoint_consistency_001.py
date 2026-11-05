"""No-fit Waszkiewicz record audit; inherited observations remain unchanged.

Waszkiewicz et al. (2025), Zenodo 18046315 v1.0.1, CC-BY-4.0 data.
No upstream GPL program is copied or imported. No model is evaluated.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import time

import numpy as np

from puckworks import data as D
from puckworks.analysis import pressure_peak_stage_b0 as B

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/WASZ_3P5_ENDPOINT_CONSISTENCY_001"
BASE = "4c5ebab5df79929813949df7113c21290dde40cc"
LC_PIN = "0e1944de72819f0a058b99b6c0b2879e2d4ffde6"
EWP_PIN = "67bead2a25bd7e61c16c4fe2c104d885d8d26dd9"
SUPPORT_CONDITIONS = (1., 2., 3.5, 4., 5.)


def sha(value):
    return hashlib.sha256(value).hexdigest()


def table(value):
    return list(csv.DictReader(io.StringIO(value.decode())))


def git_bytes(repo, commit, path):
    return subprocess.check_output(["git", "-C", str(repo), "show", f"{commit}:{path}"])


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        w.writerows({k: json.dumps(v, sort_keys=True, allow_nan=False)
                    if isinstance(v, (dict, list)) else v for k, v in row.items()}
                   for row in rows)


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def audit_raw(text):
    """Inspect original line positions; never drop/sort/deduplicate records.

    A missing timestamp prevents *both* adjacent intervals: it is never bridged.
    Sorting the diagnostic list of largest gaps does not reorder input records.
    """
    records, malformed, blank, nondict = [], 0, 0, 0
    for line in text.splitlines():
        if not line.strip():
            blank += 1
            records.append(None)
            continue
        try:
            r = json.loads(line)
        except (ValueError, TypeError):
            malformed += 1
            records.append(None)
            continue
        if not isinstance(r, dict):
            nondict += 1
            r = None
        records.append(r)
    objects = [r for r in records if r is not None]
    fields = sorted({"t", "p2", "m"}.union(*(set(r) for r in objects)))
    missing = {k: sum(k not in r for r in objects) for k in fields}
    null = {k: sum(k in r and r[k] is None for r in objects) for k in fields}
    nonfinite = {k: sum(isinstance(r.get(k), (int, float)) and not finite(r[k])
                        for r in objects) for k in fields}
    invalid_numeric = {k: sum(k in r and r[k] is not None and not finite(r[k])
                             for r in objects) for k in ("t", "p2", "m")}
    ts = [r.get("t")/1000 if r and finite(r.get("t")) else None for r in records]
    valid = [t for t in ts if t is not None]
    gaps = [(i+1, i+2, b-a) for i, (a, b) in enumerate(zip(ts, ts[1:]))
            if a is not None and b is not None]
    dt = np.array([g[2] for g in gaps])
    top = sorted((g for g in gaps if g[2] > 0), key=lambda g: (-g[2], g[0]))[:5]
    result = dict(raw_lines=len(records), json_objects=len(objects), blank_lines=blank,
        malformed_lines=malformed, nonobject_lines=nondict, raw_fields=fields,
        missing_fields=missing, null_fields=null, nonfinite_fields=nonfinite,
        invalid_numeric_fields=invalid_numeric, missing_t=missing["t"],
        missing_p2=missing["p2"], missing_m=missing["m"],
        repeated_timestamp_records=len(valid)-len(set(valid)),
        adjacent_equal_timestamps=sum(g[2] == 0 for g in gaps),
        adjacent_decreasing_timestamps=sum(g[2] < 0 for g in gaps),
        adjacent_nonincreasing_timestamps=sum(g[2] <= 0 for g in gaps),
        adjacent_timestamp_pairs=len(gaps),
        raw_first_record_timestamp_s=ts[0] if ts else None,
        raw_end_timestamp_s=ts[-1] if ts else None,
        first_finite_timestamp_s=valid[0] if valid else None,
        last_finite_timestamp_s=valid[-1] if valid else None,
        largest_gaps=[dict(from_line=a, to_line=b, dt_s=c) for a, b, c in top])
    for name, function in (("min", np.min), ("median", np.median), ("mean", np.mean),
                           ("sd", np.std), ("max", np.max),
                           ("p05", lambda a: np.quantile(a, .05)),
                           ("p95", lambda a: np.quantile(a, .95))):
        result[f"raw_adjacent_dt_{name}_s"] = float(function(dt)) if len(dt) else None
    return result, records


def endpoint_pressure(times, pressure, endpoint_s=100.):
    """Match a supported time, not a row number or final available raw sample."""
    t, p = np.asarray(times, float), np.asarray(pressure, float)
    if (t.ndim != 1 or p.shape != t.shape or len(t) < 2 or
            not np.isfinite(t).all() or not np.isfinite(p).all() or
            np.any(np.diff(t) <= 0) or not t[0] <= endpoint_s <= t[-1]):
        raise ValueError("Unsupported or unordered endpoint-pressure pairing")
    return float(np.interp(endpoint_s, t, p))


def excursions(t, p, lower, upper):
    """Left-held interval durations on the supplied named support only."""
    t, p = np.asarray(t), np.asarray(p)
    if not len(t) or np.any(np.diff(t) <= 0):
        raise ValueError("Empty or unordered excursion support")
    dt = np.diff(t)
    below, above = p[:-1] < lower, p[:-1] > upper
    longest, current = 0., 0.
    for duration, is_below in zip(dt, below):
        current = current+duration if is_below else 0.
        longest = max(longest, current)

    def intervals(mask):
        edges = np.diff(np.r_[False, mask, False].astype(int))
        return [[float(t[a]), float(t[b])] for a, b in
                zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1))]

    return dict(start_s=float(t[0]), end_s=float(t[-1]), samples=len(t),
        pressure_min_bar=float(p.min()), pressure_max_bar=float(p.max()),
        overshoot_above_upper_band_bar=float(max(0., p.max()-upper)),
        below_band_duration_s=float(dt[below].sum()),
        above_band_duration_s=float(dt[above].sum()),
        longest_below_band_duration_s=float(longest),
        below_band_intervals_s=intervals(below), above_band_intervals_s=intervals(above))


def adjacent_steps(pairs):
    rows = []
    for low, high in ((2., 3.5), (3.5, 4.)):
        a = [r for r in pairs if r["nominal_pressure_bar"] == low]
        b = [r for r in pairs if r["nominal_pressure_bar"] == high]
        qa, qb = [float(np.mean([r["endpoint_flow_g_s"] for r in g])) for g in (a, b)]
        for view in ("nominal", "matched_endpoint_100s"):
            field = "nominal_pressure_bar" if view == "nominal" else "endpoint_line_pressure_bar"
            pa, pb = [float(np.mean([r[field] for r in g])) for g in (a, b)]
            rows.append(dict(step=f"{low:g}->{high:g}", pressure_view=view,
                low_brews=len(a), high_brews=len(b), low_mean_flow_g_s=qa,
                high_mean_flow_g_s=qb, delta_flow_g_s=qb-qa, low_mean_pressure_bar=pa,
                high_mean_pressure_bar=pb, delta_pressure_bar=pb-pa,
                change_g_s_per_bar=(qb-qa)/(pb-pa) if pb != pa else None))
    return rows


def observed_map(rows, field, ids):
    result = {}
    for brew in ids:
        values = {float(r[field]) for r in rows if r["brew"] == brew}
        if len(values) != 1:
            raise ValueError(f"Missing or inconsistent saved observation: {brew}/{field}")
        result[brew] = values.pop()
    if {r["brew"] for r in rows} != set(ids):
        raise ValueError("Saved observed cohort differs")
    return result


def figure(pairs, out, preview=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"svg.hashsalt": "WASZ_3P5_ENDPOINT_CONSISTENCY_001",
                         "font.size": 10})
    fig, ax = plt.subplots(figsize=(9, 5.4), layout="constrained")
    for special, color, label in ((False, "#63778b", "Other nominal conditions (53 brews)"),
                                   (True, "#c64b24", "Nominal 3.5 bar (3 brews)")):
        rows = [r for r in pairs if (r["nominal_pressure_bar"] == 3.5) == special]
        ax.scatter([r["endpoint_line_pressure_bar"] for r in rows],
                   [r["endpoint_flow_g_s"] for r in rows], color=color,
                   s=48 if special else 26, alpha=1 if special else .75,
                   label=label, zorder=3 if special else 2)
        if special:
            for i, r in enumerate(rows):
                ax.annotate(r["brew"], (r["endpoint_line_pressure_bar"], r["endpoint_flow_g_s"]),
                            xytext=(10, (8, 0, -14)[i]), textcoords="offset points", color=color)
    ax.set(xlabel="Matched line pressure at the inherited 100-s endpoint (bar)",
           ylabel="Stored endpoint_100s flow (g/s)",
           title="Waszkiewicz: all 56 brews, unchanged endpoint observations")
    ax.grid(alpha=.18)
    ax.legend(loc="lower right", frameon=False)
    fig.suptitle("Descriptive record check · no model curve · no brew exclusions", fontsize=10)
    path = out / "ENDPOINT_PRESSURE.svg"
    fig.savefig(path, metadata={"Date": None})
    path.write_text("\n".join(line.rstrip() for line in path.read_text().splitlines())+"\n")
    if preview is not None:
        fig.savefig(preview, dpi=140)
    plt.close(fig)


def run(args):
    started = time.process_time()
    args.out.mkdir(parents=True, exist_ok=True)
    hashes = {}

    def read(path, label, expected=None):
        value = path.read_bytes()
        digest = sha(value)
        if expected is not None and digest != expected:
            raise ValueError(f"Input authentication failed: {label}")
        hashes[label] = digest
        return value

    def pinned(repo, commit, path, label):
        value = git_bytes(repo, commit, path)
        hashes[label] = sha(value)
        return value

    manifest_path = "docs/demonstrations/FORM_A/RUN_MANIFEST.json"
    manifest = json.loads(pinned(args.ewp, EWP_PIN, manifest_path, "EWP:"+manifest_path))
    sources = json.loads(read(args.source_inputs, "FORM_A:source_inputs.json",
                             manifest["input_sha256"]["source_inputs"]))
    read(Path(B.__file__), "PW:puckworks/analysis/pressure_peak_stage_b0.py",
         manifest["input_sha256"]["B0_observer_source"])
    ids = [r["brew"] for r in sources]
    if len(ids) != 56 or len(set(ids)) != 56:
        raise ValueError("Wrong inherited cohort")

    # This entire pass precedes every preprocessing/observation helper call.
    audits, originals = [], {}
    for source in sources:
        name = source["brew"]
        path = args.raw / "measurements_time_dependent" / (name+".txt")
        value = read(path, "Zenodo:measurements_time_dependent/"+path.name,
                     source["original_sha256"])
        audit, records = audit_raw(value.decode())
        audits.append(dict(brew=name, nominal_pressure_bar=source["nominal_pressure_bar"],
                           source_sha256=sha(value), **audit))
        originals[name] = records
    write_csv(args.out / "RAW_INTEGRITY.csv", audits)
    for audit in audits:
        if (audit["malformed_lines"] or audit["nonobject_lines"] or
                audit["adjacent_nonincreasing_timestamps"] or
                any(audit["invalid_numeric_fields"].values()) or
                any(audit["null_fields"].get(k, 0) for k in ("t", "p2", "m"))):
            raise ValueError("Raw evidence needs explicit availability assessment; audit preserved")

    regpath = "docs/analysis/sci_md_010/INPUT_ARTIFACT_REGISTER.json"
    register = json.loads(pinned(args.ewp, EWP_PIN, regpath, "EWP:"+regpath))
    for record in register["artifacts"]:
        if record["artifact_id"] in ("WASZ_EQUILIBRIUM", "WASZ_LINE_PRESSURE"):
            read(ROOT / record["path"], "PW:"+record["path"], record["sha256"])
    traces = D.waszkiewicz_traces_per_brew(include_aliases=False)
    by_brew = {name: (pressure, r) for pressure, group in traces.items() for name, r in group.items()}
    if set(by_brew) != set(ids) or len(traces) != 11 or set(ids) & set(D.WASZ_TRACE_ALIASES):
        raise ValueError("Brew set/alias exclusion changed")
    windows = {r["shot_id"]: r for r in D.waszkiewicz_equilibrium_windows()
               if r["window"] == "endpoint_100s" and r["shot_id"] in ids}
    histpath = "docs/analysis/sci_md_010/BREW_RESULTS.csv"
    historical = table(pinned(args.ewp, EWP_PIN, histpath, "EWP:"+histpath))
    historical = {r["physical_unit_id"].removeprefix("WASZ-BREW-"): r for r in historical
                  if r["model_id"] == "HYD_B1_PRESSURE_QUADRATIC"}
    if set(historical) != set(ids):
        raise ValueError("SCI-MD-010 cohort differs")
    saved = {}
    for study, commit in (("JOINT_CLOCK_001", BASE), ("LC_JOINT_TRANSFER_001", LC_PIN)):
        for kind, field in (("FLOW", "endpoint_observed_g_s"), ("ONSET", "observed_onset_s")):
            path = f"docs/research/{study}/{kind}_BY_BREW.csv"
            rows = table(pinned(ROOT, commit, path, f"PW@{commit}:{path}"))
            saved[study, kind] = observed_map(rows, field, ids)

    pairs, supporting = [], []
    for source, audit in zip(sources, audits):
        name = source["brew"]
        nominal, trace = by_brew[name]
        q = float(windows[name]["mass_flow_rate__g_per_s"])
        p = endpoint_pressure(trace["time__s"], trace["pressure__bar"])
        np.testing.assert_array_equal(trace["pressure__bar"], source["pressure_bar"])
        if q != source["observed_endpoint_g_s"] or nominal != source["nominal_pressure_bar"]:
            raise ValueError("FORM_A endpoint or grouping differs")
        for study in ("JOINT_CLOCK_001", "LC_JOINT_TRANSFER_001"):
            if q != saved[study, "FLOW"][name]:
                raise ValueError("Saved observed endpoint differs")
        h = historical[name]
        pairs.append(dict(brew=name, nominal_pressure_bar=nominal,
            endpoint_time_s=100., endpoint_line_pressure_bar=p, endpoint_flow_g_s=q,
            sci_md_010_line_pressure_bar=float(h["line_pressure_bar"]),
            sci_md_010_flow_g_s=float(h["observed_flow_g_s"]),
            pressure_difference_bar=p-float(h["line_pressure_bar"]),
            flow_difference_g_s=q-float(h["observed_flow_g_s"]),
            form_a_flow_difference_g_s=q-source["observed_endpoint_g_s"],
            joint_clock_flow_difference_g_s=q-saved["JOINT_CLOCK_001", "FLOW"][name],
            lc_joint_flow_difference_g_s=q-saved["LC_JOINT_TRANSFER_001", "FLOW"][name],
            support="stored endpoint_100s; pressure time_index=999; stable-pressure zero"))

        path = args.raw / "measurements_time_dependent" / (name+".txt")
        t, pressure, mass, removed = B.raw_trace(path)
        ct, cp, flow, trend = B.clean_course(t, pressure, mass)
        retained = [r for r in originals[name] if r is not None and "t" in r and "m" in r]
        raw_t = np.asarray([r["t"]/1000 for r in retained])
        if np.any(np.diff(raw_t) <= 0):
            raise ValueError("Inherited retained chronology is non-increasing")
        origin = float(raw_t[np.flatnonzero(t == 0)[0]])
        pre = (t >= -2.) & (t <= 0.)
        baseline = float(np.median(mass[pre]) if pre.any() else mass[0])
        onset = B.sustained_onset(ct, np.interp(ct, t, mass)-baseline, flow)
        if not np.isfinite(onset) or onset != source["observed_onset_for_scoring_only_s"]:
            raise ValueError("Inherited observed onset changed")
        for study in ("JOINT_CLOCK_001", "LC_JOINT_TRANSFER_001"):
            if onset != saved[study, "ONSET"][name]:
                raise ValueError("Saved observed onset differs")
        rt = np.asarray(source["trace_times_s"])
        mask = np.asarray(source["trace_mask"], bool)
        np.testing.assert_array_equal(mask, (rt >= onset+2.) & (rt <= ct[-1]))
        np.testing.assert_array_equal(np.interp(rt, ct, flow), source["observed_trace_g_s"])
        report_pressure = np.interp(rt, source["times_s"], source["pressure_bar"])[mask]
        audit.update(retained_incomplete_rows_removed=removed, retained_first_timestamp_s=float(raw_t[0]),
            retained_end_timestamp_s=float(raw_t[-1]), stable_origin_timestamp_s=origin,
            raw_end_aligned_s=(audit["raw_end_timestamp_s"]-origin
                               if audit["raw_end_timestamp_s"] is not None else None),
            clean_end_aligned_s=float(ct[-1]), clean_end_timestamp_s=origin+float(ct[-1]),
            raw_end_minus_clean_end_s=(audit["raw_end_timestamp_s"]-origin-float(ct[-1])
                                     if audit["raw_end_timestamp_s"] is not None else None))
        if nominal not in SUPPORT_CONDITIONS:
            continue
        med = float(np.median(pressure))
        lo, hi = max(.9*med, med-.5), min(1.1*med, med+.5)
        row = dict(record_type="brew", brew=name, nominal_pressure_bar=nominal, brew_count=1,
            primary_reporting_start_s=float(rt[mask][0]), primary_reporting_end_s=float(rt[mask][-1]),
            primary_reporting_samples=int(mask.sum()), primary_pressure_mean_bar=float(report_pressure.mean()),
            primary_pressure_sd_bar=float(report_pressure.std()), stable_median_pressure_bar=med,
            stable_lower_band_bar=lo, stable_upper_band_bar=hi,
            stable_elapsed_from_first_raw_record_s=(origin-audit["raw_first_record_timestamp_s"]
                if audit["raw_first_record_timestamp_s"] is not None else None),
            stable_elapsed_from_first_retained_s=float(-t[0]),
            observed_onset_s=onset, clean_end_s=float(ct[-1]),
            final_clean_30s_start_s=float(ct[ct >= ct[-1]-30][0]),
            final_clean_30s_samples=int(np.sum(ct >= ct[-1]-30)),
            final_clean_30s_flow_trend_g_s2=float(trend),
            baseline_mass_g=baseline, baseline_samples=int(pre.sum()),
            beverage_mass_100s_g=endpoint_pressure(t, mass)-baseline,
            beverage_mass_clean_end_g=endpoint_pressure(t, mass, ct[-1])-baseline,
            joint_observed_onset_difference_s=onset-saved["JOINT_CLOCK_001", "ONSET"][name],
            lc_observed_onset_difference_s=onset-saved["LC_JOINT_TRANSFER_001", "ONSET"][name])
        for prefix, tt, pp in (("prestable", t[t <= 0], pressure[t <= 0]),
                               ("stable_to_clean_end", ct, cp)):
            row.update({prefix+"_"+k: v for k, v in excursions(tt, pp, lo, hi).items()})
        supporting.append(row)
    for nominal in SUPPORT_CONDITIONS:
        group = [r for r in supporting if r["record_type"] == "brew" and r["nominal_pressure_bar"] == nominal]
        row = dict(record_type="equal_brew_mean", brew="", nominal_pressure_bar=nominal,
                   brew_count=len(group))
        for field in group[0]:
            if field not in row:
                vals = [r[field] for r in group]
                row[field] = float(np.mean(vals)) if all(finite(v) for v in vals) else None
        supporting.append(row)
    steps = adjacent_steps(pairs)
    for filename, rows in (("RAW_INTEGRITY.csv", audits), ("ENDPOINT_PAIRS.csv", pairs),
                           ("STEP_COMPARISON.csv", steps), ("SUPPORTING_SUMMARIES.csv", supporting)):
        write_csv(args.out / filename, rows)
    figure(pairs, args.out)
    for path in (ROOT / "puckworks/data/waszkiewicz2025/PROVENANCE.md", Path(__file__),
                 Path(D.__file__), Path(B.A.__file__), OUT / "PLAN.md"):
        read(path, "PW:"+str(path.relative_to(ROOT)))
    write_json(args.out / "INPUT_HASHES.json", hashes)
    write_json(args.out / "VERIFICATION.json", dict(base=BASE, lc_pin=LC_PIN, ewp_pin=EWP_PIN,
        raw_audit_completed_before_preprocessing=True, brews=56, conditions=11,
        alias_exclusion=D.WASZ_TRACE_ALIASES, endpoint_pairs=len(pairs),
        endpoint_target_unchanged=True, saved_observed_flows_onsets_identical=True,
        primary_reporting_trace_and_mask_identical=True,
        max_sci_md_010_pressure_difference_bar=max(abs(r["pressure_difference_bar"]) for r in pairs),
        max_sci_md_010_flow_difference_g_s=max(abs(r["flow_difference_g_s"]) for r in pairs),
        raw_fields=sorted({k for r in audits for k in r["raw_fields"]}),
        model_fits=0, model_evaluations=0, model_scores=0,
        process_cpu_seconds_inside_run=time.process_time()-started,
        source_attribution="Waszkiewicz et al. (2025), Zenodo 18046315 v1.0.1, CC-BY-4.0",
        scope="Same campaign; no causal or physical-validation claim"))
    print(json.dumps(dict(brews=len(pairs), supporting_rows=len(supporting), steps=steps), indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--source-inputs", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    run(parser.parse_args())


if __name__ == "__main__":
    main()

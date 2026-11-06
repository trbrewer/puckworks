"""Linear observation decomposition of retained #424 arrays; no fits/simulations.

Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Only saved cumulative masses
are observed. The runner has no call to a model, optimizer or simulation CLI.
"""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.signal import savgol_filter

from . import wasz_turnover_time_001 as O

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/TURNOVER_REPLAY_DECOMPOSITION_001"
MODELS = ("A-J1", "D0-R0-diagnostic")
SCOPES = ("LOCO", "DESCRIPTIVE_ALL")
COMPONENTS = ("liquid", "solute", "total")
RTOL = ATOL = 1e-12


def beverage_observer(prediction, native_t):
    """Sample cumulative beverage mass first, then the inherited derivative/filter."""
    native_t = np.asarray(native_t)
    if native_t[0] < prediction["time"][0] or native_t[-1] > prediction["time"][-1]:
        raise ValueError("Missing native derivative/filter support")
    mass = np.interp(native_t, prediction["time"], prediction["beverage_g"])
    return savgol_filter(np.gradient(mass, native_t), 31, 1)


def read_json(path):
    return json.loads(Path(path).read_text())


def read_csv(path):
    with Path(path).open() as stream:
        return list(csv.DictReader(stream))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def checked_hash(path, expected):
    """Fail before consuming a changed or missing retained input."""
    if O.digest(path) != expected:
        raise ValueError(f"Input authentication failed: {Path(path).name}")


def observer_source_hash(path):
    """Exact function source, independent of Python-version AST field changes."""
    text = Path(path).read_text()
    node = next(n for n in ast.parse(text).body
                if isinstance(n, ast.FunctionDef) and n.name == "beverage_observer")
    return hashlib.sha256(ast.get_source_segment(text, node).encode()).hexdigest()


def close(actual, expected, label):
    """Inherited numerical tolerance; a failure stops before interpretation."""
    if not np.isfinite(actual).all() or not np.isfinite(expected).all():
        raise ValueError("Missing/nonfinite reconstruction: " + label)
    np.testing.assert_allclose(actual, expected, rtol=RTOL, atol=ATOL, err_msg=label)
    return float(np.max(np.abs(np.asarray(actual)-expected)))


def load_arrays(path, expected_hash):
    """Read separately retained masses only; missing components are never inferred."""
    checked_hash(path, expected_hash)
    required = ("time", "liquid_g", "solute_g", "beverage_g")
    with np.load(path, allow_pickle=False) as saved:
        missing = set(required) - set(saved.files)
        if missing:
            raise ValueError(f"Missing retained signals in {Path(path).name}: {sorted(missing)}")
        arrays = {key: saved[key] for key in required}
    t = arrays["time"]
    if t.ndim != 1 or len(t) < 2 or not np.isfinite(t).all() or not (np.diff(t) > 0).all():
        raise ValueError("Invalid retained timestamps")
    if any(a.shape != t.shape or not np.isfinite(a).all() for a in arrays.values()):
        raise ValueError("Invalid retained mass support")
    return arrays


def component_flows(arrays, native_t):
    """Apply the exact frozen mass observer separately to all three saved signals."""
    return {name: beverage_observer(dict(time=arrays["time"], beverage_g=arrays[key]), native_t)
            for name, key in zip(COMPONENTS, ("liquid_g", "solute_g", "beverage_g"))}


def authenticate(args):
    """Bind retained arrays, index, observed support and draw identities to #424."""
    freeze = read_json(OUT / "INPUT_MANIFEST.json")
    for folder, key in ((ROOT, "repository_inputs"), (args.replay, "replay_files"), (args.wasz, "wasz_files")):
        for path, expected in freeze[key].items():
            checked_hash(folder / path, expected)
    old_out = args.replay / "docs/research/TURNOVER_TIME_REPLAY_001"
    wasz_out = args.wasz / "docs/research/WASZ_TURNOVER_TIME_001"
    for path in (Path(__file__), args.replay / "puckworks/analysis/turnover_time_replay_001.py"):
        if observer_source_hash(path) != freeze["beverage_observer_source_sha256"]:
            raise ValueError("The frozen observation operator changed")
    checked_hash(args.retained / "replay-index.json", freeze["replay_index_sha256"])
    checked_hash(args.retained / "attempted-windows.csv", freeze["retained_windows_sha256"])
    index = read_json(args.retained / "replay-index.json")
    old = read_json(old_out / "RUN_RECEIPT.json")
    for key, expected in (
        ("code_sha256", old["code_sha256"]["puckworks/analysis/turnover_time_replay_001.py"]),
        ("plan_sha256", old["plan_sha256"]), ("input_manifest_sha256", old["input_manifest_sha256"]),
        ("windows_sha256", old["private_windows_sha256"])):
        if index[key] != expected:
            raise ValueError("Retained replay index differs from #424: " + key)
    records = [{k: row[k] for k in ("model", "scope", "brew", "artifact", "sha256")}
               for row in index["records"]]
    if records != freeze["arrays"]:
        raise ValueError("Retained array bank changed")
    brews = freeze["brew_order"]
    identities = {(r["model"], r["scope"], r["brew"]) for r in records}
    if len(records) != 224 or identities != {(m, s, b) for m in MODELS for s in SCOPES for b in brews}:
        raise ValueError("Incomplete or duplicated replay bank")
    if brews != old["brew_order"] or brews != read_json(wasz_out / "RUN_RECEIPT.json")["brew_order"]:
        raise ValueError("Brew order changed")
    raw_manifest = read_json(wasz_out / "INPUT_MANIFEST.json")
    by_brew = {r["brew"]: r for r in raw_manifest["brews"]}
    native = {}
    for brew in brews:
        path = args.raw / "measurements_time_dependent" / (brew + ".txt")
        checked_hash(path, by_brew[brew]["original_sha256"])
        native[brew] = O.native_observation(path)
    condition = np.array([by_brew[b]["nominal_pressure_bar"] for b in brews])
    draws = O.draw_bank(condition)
    if O.bank_digest(draws) != freeze["draw_bank_sha256"] or O.bank_digest(draws) != old["draw_bank_sha256"]:
        raise ValueError("Whole-brew resample identities changed")
    observed = {(r["brew"], r["clock"], int(r["time_s"])): r
                for r in read_csv(wasz_out / "PER_BREW_BY_TIME.csv")}
    windows = read_csv(args.retained / "attempted-windows.csv")
    lookup = {(r["model"], r["scope"], r["brew"], r["clock"], int(r["time_s"])): r for r in windows}
    expected_windows = {(m, s, b, c, t) for m, s, b in identities for c, t in O.SNAPSHOTS}
    if len(windows) != len(lookup) or set(lookup) != expected_windows:
        raise ValueError("Saved window membership changed")
    # All hashes/signals are checked before any component outcome is reported.
    for row in records:
        load_arrays(args.retained / "predictions" / row["artifact"], row["sha256"])
    return dict(freeze=freeze, records=records, brews=brews, condition=condition,
                native=native, observed=observed, windows=lookup, draws=draws, old_out=old_out)


def decompose(args, data):
    """Every #424 window must reconstruct; never shrink or shift the cohort."""
    rows = []
    audit = dict(arrays=0, windows=0, max_mass_residual_g=0., max_window_sum_residual_g_s=0.,
                 max_saved_total_residual_g_s=0., max_native_observed_residual=0.)
    for record in data["records"]:
        model, scope, brew = (record[k] for k in ("model", "scope", "brew"))
        arrays = load_arrays(args.retained / "predictions" / record["artifact"], record["sha256"])
        audit["max_mass_residual_g"] = max(audit["max_mass_residual_g"],
            close(arrays["liquid_g"]+arrays["solute_g"], arrays["beverage_g"], "saved mass sum"))
        ct, cp, cq, onset, _ = data["native"][brew]
        flows = component_flows(arrays, ct)
        for clock, target in O.SNAPSHOTS:
            old = data["windows"][model, scope, brew, clock, target]
            obs = data["observed"][brew, clock, target]
            if old["available"] != "True" or obs["available"] != "True":
                raise ValueError("A retained comparison window is unavailable; no cohort reduction allowed")
            center = target + (onset if clock == "onset" else 0.)
            p, q, reason = O.paired_window(ct, cp, cq, center)
            if reason != obs["reason"] or reason != "available":
                raise ValueError("Observed support changed")
            residual = close([p, q, center-1, center+1, onset],
                [float(obs[k]) for k in ("pressure_bar", "flow_g_s", "window_start_stable_s",
                                         "window_end_stable_s", "onset_stable_s")], "#423 observation")
            close([center-1, center+1, onset, p], [float(old[k]) for k in
                ("window_start_stable_s", "window_end_stable_s", "observed_onset_stable_s", "achieved_pressure_bar")],
                "#424 alignment/pressure")
            audit["max_native_observed_residual"] = max(audit["max_native_observed_residual"], residual)
            values = {}
            for name, flow in flows.items():
                _, values[name], status = O.paired_window(ct, cp, flow, center)
                if status != "available":
                    raise ValueError("Missing genuine component window support")
            audit["max_window_sum_residual_g_s"] = max(audit["max_window_sum_residual_g_s"],
                close(values["liquid"]+values["solute"], float(old["predicted_beverage_flow_g_s"]), "component window sum"))
            audit["max_saved_total_residual_g_s"] = max(audit["max_saved_total_residual_g_s"],
                close(values["total"], float(old["predicted_beverage_flow_g_s"]), "saved beverage observer"))
            rows.append(dict(model=model, scope=scope, brew=brew, clock=clock, time_s=target,
                nominal_pressure_bar=float(old["nominal_pressure_bar"]), achieved_pressure_bar=float(obs["pressure_bar"]),
                observed_flow_g_s=float(obs["flow_g_s"]), **{name+"_flow_g_s": v for name, v in values.items()},
                window_start_stable_s=center-1, window_end_stable_s=center+1, available=True))
            audit["windows"] += 1
        audit["arrays"] += 1
    return rows, audit


def tables(data, rows):
    """Same condition means, achieved-pressure slopes and paired whole-brew draws."""
    lookup = {(r["model"], r["scope"], r["brew"], r["clock"], r["time_s"]): r for r in rows}
    nominal = np.array(list(data["draws"]))
    by_time, phases, slopes = [], [], []
    historical_means = {(r["model"], r["scope"], r["clock"], int(r["time_s"]), float(r["nominal_pressure_bar"])): r
                        for r in read_csv(data["old_out"] / "PREDICTED_BY_TIME.csv")}
    historical_slopes = {(r["model"], r["scope"], r["clock"], int(r["time_s"])): r
                         for r in read_csv(data["old_out"] / "SLOPE_COMPARISON.csv")}
    residuals = dict(max_condition_sum_residual_g_s=0., max_slope_sum_residual_g_s_bar=0.,
                     max_bootstrap_sum_residual_g_s=0.)
    for model in MODELS:
        for scope in SCOPES:
            ordered = [[lookup[model, scope, b, c, t] for b in data["brews"]] for c, t in O.SNAPSHOTS]
            p = np.array([[r["achieved_pressure_bar"] for r in group] for group in ordered])
            means, draws, hs = {}, {}, {}
            for name in (*COMPONENTS, "observed"):
                q = np.array([[r[name+"_flow_g_s"] for r in group] for group in ordered])
                mp, means[name], bp, draws[name], count = O.condition_statistics(p, q, data["condition"], data["draws"])
                hs[name] = O.high_slope(mp, means[name], nominal)
            residuals["max_bootstrap_sum_residual_g_s"] = max(residuals["max_bootstrap_sum_residual_g_s"],
                close(draws["liquid"]+draws["solute"], draws["total"], "paired draw reconstruction"))
            for j, (clock, target) in enumerate(O.SNAPSHOTS):
                common = dict(model=model, scope=scope, clock=clock, time_s=target)
                old_slope = historical_slopes[model, scope, clock, target]
                residuals["max_slope_sum_residual_g_s_bar"] = max(residuals["max_slope_sum_residual_g_s_bar"],
                    close(hs["liquid"][j]+hs["solute"][j], float(old_slope["predicted_slope_g_s_bar"]), "#424 slope sum"))
                close(hs["total"][j], float(old_slope["predicted_slope_g_s_bar"]), "#424 total slope")
                slopes.append(dict(common, **{name+"_slope_g_s_bar": hs[name][j] for name in hs}))
                for k, c in enumerate(nominal):
                    old_mean = historical_means[model, scope, clock, target, c]
                    residuals["max_condition_sum_residual_g_s"] = max(residuals["max_condition_sum_residual_g_s"],
                        close(means["liquid"][j, k]+means["solute"][j, k], float(old_mean["predicted_beverage_flow_g_s"]), "#424 condition sum"))
                    close(means["total"][j, k], float(old_mean["predicted_beverage_flow_g_s"]), "#424 total condition mean")
                    by_time.append(dict(common, nominal_pressure_bar=c, brews=int(count[j, k]),
                        achieved_pressure_bar=mp[j, k], **{name+"_flow_g_s": means[name][j, k] for name in means}))
            for a, b in ((10, 40), (40, 60), (60, 100)):
                ia, ib = O.SNAPSHOTS.index(("stable_pressure", a)), O.SNAPSHOTS.index(("stable_pressure", b))
                for c in (9., 11., 13.):
                    k = list(nominal).index(c)
                    row = dict(model=model, scope=scope, clock="stable_pressure", start_time_s=a, end_time_s=b,
                               nominal_pressure_bar=c, brews=int(count[ia, k]), intervals="paired pointwise 95%" if b == 100 else "not requested")
                    for name in means:
                        point = means[name][ib, k]-means[name][ia, k]
                        change = draws[name][ib, :, k]-draws[name][ia, :, k]
                        if b == 100:
                            row.update(O.uncertainty(name+"_change_g_s", point, change))
                        else:
                            row[name+"_change_g_s"] = float(point)
                    phases.append(row)
    return by_time, phases, slopes, residuals


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("replay", "wasz", "retained", "raw", "private"):
        parser.add_argument("--"+name, type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    for target in (args.private.resolve(), args.output.resolve()):
        for protected in (args.replay, args.wasz, args.retained, args.raw):
            if target == protected.resolve() or protected.resolve() in target.parents:
                raise ValueError("Output overlaps a read-only input")
    if ROOT == args.private.resolve() or ROOT in args.private.resolve().parents:
        raise ValueError("Private window details must remain outside Git")
    args.private.mkdir(parents=True, exist_ok=True)
    if (args.private / "RUN_RECEIPT.json").exists():
        raise ValueError("Preserve the previous decomposition; use a fresh private output")
    cpu, wall = time.process_time(), time.perf_counter()
    data = authenticate(args)
    try:
        rows, audit = decompose(args, data)
        by_time, phases, slopes, residuals = tables(data, rows)
    except (ValueError, AssertionError) as exc:
        write_json(args.private / "RECONSTRUCTION_FAILURE.json", dict(error=str(exc),
            code_sha256=O.digest(__file__), cpu_seconds=time.process_time()-cpu))
        raise  # No interpretation/aggregate output after reconstruction failure.
    args.output.mkdir(parents=True, exist_ok=True)
    O.write_csv(args.private / "WINDOW_CONTRIBUTIONS.csv", rows)
    for name, values in (("CONTRIBUTIONS_BY_TIME", by_time), ("PHASE_CONTRIBUTIONS", phases), ("SLOPE_CONTRIBUTIONS", slopes)):
        O.write_csv(args.output / (name+".csv"), values)
    from .turnover_replay_decomposition_001_figure import figure
    figure(by_time, args.output)
    receipt = dict(**audit, **residuals, code_sha256=O.digest(__file__),
        figure_code_sha256=O.digest(ROOT / "puckworks/analysis/turnover_replay_decomposition_001_figure.py"),
        input_manifest_sha256=O.digest(OUT / "INPUT_MANIFEST.json"), plan_sha256=O.digest(OUT / "PLAN.md"),
        observer_sha256=O.digest(O.__file__), draw_bank_sha256=O.bank_digest(data["draws"]),
        brew_order=data["brews"], rtol=RTOL, atol=ATOL, fits=0, simulations=0,
        private_windows_sha256=O.digest(args.private / "WINDOW_CONTRIBUTIONS.csv"),
        outputs={p.name: O.digest(p) for p in sorted(args.output.iterdir()) if p.suffix in (".csv", ".svg")},
        cpu_seconds=time.process_time()-cpu, wall_seconds=time.perf_counter()-wall)
    receipt["core_hours"] = receipt["cpu_seconds"]/3600
    write_json(args.private / "RUN_RECEIPT.json", receipt)
    write_json(args.output / "RUN_RECEIPT.json", receipt)
    print(json.dumps({k: receipt[k] for k in (*audit, *residuals, "core_hours")}))


if __name__ == "__main__":
    main()

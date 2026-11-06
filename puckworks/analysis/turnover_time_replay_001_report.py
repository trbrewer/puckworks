"""Paired descriptive tables from frozen replay windows; no simulations or fits."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import time

import numpy as np

from . import wasz_turnover_time_001 as O
from . import turnover_time_replay_001 as T

STATES = ("capacity_C_g_s", "predicted_liquid_M_g", "recovery_R",
          "instantaneous_liquid_flow_g_s", "front_fraction")


def number(value):
    return float(value) if value not in (None, "") else np.nan


def paired_difference(name, left, right, left_draws, right_draws):
    """Subtract identically indexed whole-brew draws, never interval endpoints."""
    return O.uncertainty(name, left - right, left_draws - right_draws)


def complete_observed_conditions(values, observed, condition):
    """An incomplete prediction cannot silently shrink an observed condition."""
    values = np.asarray(values).copy()
    values[~np.isfinite(observed)] = np.nan
    for c in np.unique(condition):
        ids = np.flatnonzero(condition == c)
        for j in range(len(values)):
            eligible = np.isfinite(observed[j, ids])
            if not np.isfinite(values[j, ids[eligible]]).all():
                values[j, ids] = np.nan
    return values


def summaries(data, windows):
    """Condition means, shared-draw slopes, trajectories and availability."""
    sources, bank, condition = data["sources"], data["draws"], data["condition"]
    nominal = np.array(list(bank))
    shape = (len(O.SNAPSHOTS), len(sources))
    pressure, observed = np.full(shape, np.nan), np.full(shape, np.nan)
    for i, s in enumerate(sources):
        for j, (clock, target) in enumerate(O.SNAPSHOTS):
            row = data["observed"][s["brew"], clock, target]
            if row["available"] == "True":
                pressure[j, i], observed[j, i] = number(row["pressure_bar"]), number(row["flow_g_s"])
    mp, mq, bp, bq, counts = O.condition_statistics(pressure, observed, condition, bank)
    os, obs = O.high_slope(mp, mq, nominal), O.high_slope(bp, bq, nominal)
    conditions, slopes, trajectories, availability = [], [], [], []
    lookup = {(r["model"], r["scope"], r["brew"], r["clock"], int(r["time_s"])): r for r in windows}
    if len(lookup) != 4*shape[0]*shape[1]:
        raise ValueError("Not every intended model/scope/brew/window is retained")
    for model in T.MODELS:
        for scope in T.SCOPES:
            values = np.full(shape, np.nan)
            states = {key: np.full(shape, np.nan) for key in STATES}
            for i, source in enumerate(sources):
                for j, (clock, target) in enumerate(O.SNAPSHOTS):
                    row = lookup[model, scope, source["brew"], clock, target]
                    if row["available"] in (True, "True"):
                        if number(row["achieved_pressure_bar"]) != pressure[j, i]:
                            raise ValueError("Predicted slope did not retain frozen observed pressure")
                        values[j, i] = number(row["predicted_beverage_flow_g_s"])
                        for key in STATES:
                            states[key][j, i] = number(row.get(key))
            intended_values = values.copy()
            values = complete_observed_conditions(values, observed, condition)
            _, pq, _, pbq, _ = O.condition_statistics(pressure, values, condition, bank)
            ps, pbs = O.high_slope(mp, pq, nominal), O.high_slope(bp, pbq, nominal)
            state_means = {}
            for key, value in states.items():
                value[~np.isfinite(values)] = np.nan
                state_means[key] = O.condition_statistics(pressure, value, condition, bank)[1]
            identity = dict(model=model, scope=scope,
                            scope_definition="pooled different held-condition fits" if scope == "LOCO" else "one common in-sample parameter set")
            for j, (clock, target) in enumerate(O.SNAPSHOTS):
                common = dict(identity, clock=clock, time_s=target)
                previous = j - 1 if j and O.SNAPSHOTS[j-1][0] == clock else None
                best, edge, ratio, missing = O.maximum(pq[j], nominal)
                maxima = [O.maximum(q, nominal) for q in pbq[j]]
                row = {**common,
                       **O.uncertainty("observed_slope_g_s_bar", os[j], obs[j]),
                       **O.uncertainty("predicted_slope_g_s_bar", ps[j], pbs[j]),
                       **paired_difference("observed_minus_predicted_slope_g_s_bar", os[j], ps[j], obs[j], pbs[j]),
                       **paired_difference("observed_stable100_minus_current_g_s_bar", os[O.REFERENCE], os[j], obs[O.REFERENCE], obs[j]),
                       **paired_difference("predicted_stable100_minus_current_g_s_bar", ps[O.REFERENCE], ps[j], pbs[O.REFERENCE], pbs[j]),
                       **O.uncertainty("observed_minus_predicted_reference_change_g_s_bar",
                                       (os[O.REFERENCE]-os[j])-(ps[O.REFERENCE]-ps[j]),
                                       (obs[O.REFERENCE]-obs[j])-(pbs[O.REFERENCE]-pbs[j])),
                       "reference_clock": "stable_pressure", "reference_time_s": 100,
                       "previous_time_s": O.SNAPSHOTS[previous][1] if previous is not None else None,
                       "maximum_nominal_bar": best, "maximum_at_available_edge": edge,
                       "missing_nominal_conditions": missing,
                       **O.uncertainty("ratio_13_to_max", ratio, [v[2] for v in maxima]),
                       "maximum_selection_fractions": {str(c): sum(c in v[0] for v in maxima)/len(maxima) for c in nominal},
                       "maximum_tied_draws": sum(len(v[0]) > 1 for v in maxima)}
                if previous is not None:
                    row.update(paired_difference("observed_current_minus_previous_g_s_bar", os[j], os[previous], obs[j], obs[previous]))
                    row.update(paired_difference("predicted_current_minus_previous_g_s_bar", ps[j], ps[previous], pbs[j], pbs[previous]))
                    row.update(O.uncertainty("observed_minus_predicted_adjacent_change_g_s_bar",
                        (os[j]-os[previous])-(ps[j]-ps[previous]), (obs[j]-obs[previous])-(pbs[j]-pbs[previous])))
                slopes.append(row)
                for k, c in enumerate(nominal):
                    ids = np.flatnonzero(condition == c)
                    detail = [lookup[model, scope, sources[i]["brew"], clock, target] for i in ids]
                    n_available = int(np.isfinite(intended_values[j, ids]).sum())
                    complete = np.isfinite(pq[j, k])
                    reason = "complete" if complete else "incomplete_observed_condition"
                    availability.append(dict(common, nominal_pressure_bar=c, intended_brews=len(ids),
                                             observed_available=int(counts[j, k]), predicted_available=n_available,
                                             aggregate_available=bool(complete), status=reason,
                                             unavailable_reasons={r["reason"]: sum(x["reason"] == r["reason"] for x in detail)
                                                                  for r in detail if r["available"] not in (True, "True")}))
                    condition_row = {**common, "nominal_pressure_bar": c, "observed_brews": int(counts[j, k]),
                                     "predicted_brews": n_available, "aggregate_status": reason,
                                     "achieved_pressure_bar": mp[j, k],
                                     **O.uncertainty("observed_beverage_flow_g_s", mq[j, k], bq[j, :, k]),
                                     **O.uncertainty("predicted_beverage_flow_g_s", pq[j, k], pbq[j, :, k]),
                                     **paired_difference("observed_minus_predicted_flow_g_s", mq[j, k], pq[j, k], bq[j, :, k], pbq[j, :, k]),
                                     **{key: state_means[key][j, k] for key in STATES},
                                     "state_sampling": "native-node window time average, then equal-brew condition mean"}
                    conditions.append(condition_row)
                    if c in (9., 11., 13.):
                        trajectories.append(dict(condition_row, record_type="snapshot"))
            changes = [("phase", "stable_pressure", a, b) for a, b in ((10, 40), (40, 60), (60, 100))]
            for clock in ("stable_pressure", "onset"):
                times = [t for c, t in O.SNAPSHOTS if c == clock]
                changes += [("adjacent", clock, a, b) for a, b in zip(times[:-1], times[1:])]
            for kind, clock, start, end in changes:
                a, b = O.SNAPSHOTS.index((clock, start)), O.SNAPSHOTS.index((clock, end))
                od, pd = mq[b]-mq[a], pq[b]-pq[a]
                obd, pbd = bq[b]-bq[a], pbq[b]-pbq[a]
                for c in (9., 11., 13., "9_minus_13"):
                    if c == "9_minus_13":
                        i, k = list(nominal).index(9.), list(nominal).index(13.)
                        ov, pv, obv, pbv = od[i]-od[k], pd[i]-pd[k], obd[:, i]-obd[:, k], pbd[:, i]-pbd[:, k]
                    else:
                        k = list(nominal).index(c)
                        ov, pv, obv, pbv = od[k], pd[k], obd[:, k], pbd[:, k]
                    trajectories.append({**identity, "record_type": kind, "clock": clock,
                                         "start_time_s": start, "end_time_s": end, "trajectory": c,
                                         **O.uncertainty("observed_increment_g_s", ov, obv),
                                         **O.uncertainty("predicted_increment_g_s", pv, pbv),
                                         **paired_difference("observed_minus_predicted_increment_g_s", ov, pv, obv, pbv)})
    return conditions, slopes, trajectories, availability


def figure(rows, out):
    """Observed and frozen-model slopes; scope is encoded separately from model."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "TURNOVER_TIME_REPLAY_001"})
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)
    colors = {T.MODELS[0]: "#007f73", T.MODELS[1]: "#c45b14"}
    for ax, clock in zip(axes, ("stable_pressure", "onset")):
        baseline = [r for r in rows if r["clock"] == clock and r["model"] == T.MODELS[0] and r["scope"] == "LOCO"]
        times = [r["time_s"] for r in baseline]
        ax.fill_between(times, [r["observed_slope_g_s_bar_lo"] for r in baseline],
                        [r["observed_slope_g_s_bar_hi"] for r in baseline], color="0.5", alpha=.18)
        ax.plot(times, [r["observed_slope_g_s_bar"] for r in baseline], "ko-", lw=2.2, label="Observed beverage flow")
        for model in T.MODELS:
            for scope in T.SCOPES:
                chosen = [r for r in rows if r["clock"] == clock and r["model"] == model and r["scope"] == scope]
                label = model + (" · LOCO (pooled fits)" if scope == "LOCO" else " · all-condition (in-sample)")
                ax.plot([r["time_s"] for r in chosen], [r["predicted_slope_g_s_bar"] for r in chosen],
                        color=colors[model], linestyle="-" if scope == "LOCO" else "--",
                        marker="o" if scope == "LOCO" else "s", ms=3.5, lw=1.4, label=label)
        ax.axhline(0, color="0.4", lw=.7)
        ax.set(title="Since stable pressure" if clock == "stable_pressure" else "Since observed onset",
               xlabel="Window center (s)", xticks=times)
        ax.grid(alpha=.15)
    axes[0].set_ylabel("9/11/13-bar condition-mean slope (g/s/bar)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", bbox_to_anchor=(.5, .045), ncol=2, frameon=False)
    fig.suptitle("Waszkiewicz: observed and frozen-model pressure slopes", fontsize=14)
    fig.text(.5, .012, "2-s beverage-flow windows · shared observed alignment/pressure · shaded: pointwise observed 95% interval", ha="center", fontsize=9)
    fig.subplots_adjust(left=.08, right=.98, bottom=.30, top=.86, wspace=.13)
    fig.savefig(out / "SLOPE_REPLAY.svg", metadata={"Date": None})
    plt.close(fig)


def report(args, data):
    cpu = time.process_time()
    index = T.read_json(args.private / "replay-index.json")
    if index["code_sha256"] != O.digest(T.__file__) or index["plan_sha256"] != O.digest(T.OUT / "PLAN.md"):
        raise ValueError("Replay belongs to another code/plan")
    T.checked_hash(args.private / "attempted-windows.csv", index["windows_sha256"])
    for row in index["records"]:
        if row["artifact"] is not None:
            T.checked_hash(args.private / "predictions" / row["artifact"], row["sha256"])
    with (args.private / "attempted-windows.csv").open() as f:
        windows = list(csv.DictReader(f))
    conditions, slopes, trajectories, availability = summaries(data, windows)
    for name, rows in (("PREDICTED_BY_TIME", conditions), ("SLOPE_COMPARISON", slopes),
                       ("TRAJECTORIES_9_11_13", trajectories), ("AVAILABILITY", availability)):
        O.write_csv(args.output / (name + ".csv"), rows)
    figure(slopes, args.output)
    historical = T.read_json(args.private / "historical-reproduction.json")
    prior = [T.read_json(p) for p in sorted((args.private / "historical-attempts").glob("*.json"))]
    parameters = []
    for model in T.MODELS:
        for scope in T.SCOPES:
            for source in data["sources"]:
                p, mc, fold = T.select_parameters(model, scope, source, data)
                row = dict(model=model, scope=scope, fold=fold, parameters=p.tolist(), mc_g=mc)
                if row not in parameters:
                    parameters.append(row)
    T.write_json(args.output / "PARAMETER_BANK.json", parameters)
    receipt = dict(plan_sha256=O.digest(T.OUT / "PLAN.md"), input_manifest_sha256=O.digest(T.OUT / "INPUT_MANIFEST.json"),
                   code_sha256={str(Path(p).relative_to(T.ROOT)): O.digest(p) for p in (T.__file__, __file__, O.__file__)},
                   parameter_bank_sha256=O.digest(args.output / "PARAMETER_BANK.json"),
                   draw_bank_sha256=O.bank_digest(data["draws"]), brew_order=[s["brew"] for s in data["sources"]],
                   historical_models_passed=historical["models"], historical_cases=len(historical["records"]),
                   historical_reference_sha256=O.digest(args.private / "historical-reproduction.json"),
                   prior_historical_attempts=[dict(code_sha256=r["code_sha256"], cpu_seconds=r["cpu_seconds"]) for r in prior],
                   historical_cpu_seconds=historical["cpu_seconds"], replay_cpu_seconds=index["cpu_seconds"],
                   reporting_cpu_seconds=time.process_time() - cpu, intended_replay_cases=224,
                   available_replay_cases=sum(r["artifact"] is not None for r in index["records"]),
                   intended_windows=len(windows), available_windows=sum(r["available"] == "True" for r in windows),
                   private_windows_sha256=index["windows_sha256"], refits=0, dt_s=T.DT, cells=256)
    receipt["recorded_part_a_core_hours"] = (receipt["historical_cpu_seconds"] + receipt["replay_cpu_seconds"] +
        receipt["reporting_cpu_seconds"] + sum(r["cpu_seconds"] for r in prior))/3600
    T.write_json(args.output / "RUN_RECEIPT.json", receipt)
    print(json.dumps({k: receipt[k] for k in ("available_replay_cases", "intended_windows", "available_windows", "recorded_part_a_core_hours")}))

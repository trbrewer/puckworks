"""No-fit Waszkiewicz time snapshots with paired native pressure and flow.

Data: Waszkiewicz et al. (2025), Zenodo 18046315, CC-BY-4.0.
Only observation helpers are reused from Stage A/B0. No model is evaluated or
fitted. EWP and original data are read-only inputs; all writes target this task.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import time

import numpy as np
import scipy

from . import pressure_peak_stage_a as A
from . import pressure_peak_stage_b0 as B0

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/WASZ_TURNOVER_TIME_001"
SNAPSHOTS = [("stable_pressure", t) for t in (10, 20, 30, 40, 60, 100)] + [
    ("onset", t) for t in (10, 20, 30, 40)]
SEED = 20261106
N_BOOT = 1000
REFERENCE = SNAPSHOTS.index(("stable_pressure", 100))


def digest(path):
    """SHA-256 of file bytes, without modifying the source."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, rows):
    """Write deterministic, lossless numeric CSV; unavailable values are blank."""
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: json.dumps(v, separators=(",", ":"))
                             if isinstance(v, (list, dict)) else
                             "" if isinstance(v, (float, np.floating)) and not np.isfinite(v)
                             else v for k, v in row.items()})


def authenticate(ewp, raw, native):
    """Check every frozen input before any new observation is computed."""
    manifest = json.loads((OUT / "INPUT_MANIFEST.json").read_text())
    for base, name in ((ROOT, "puckworks_files"), (ewp, "ewp_files")):
        for path, expected in manifest[name].items():
            if digest(base / path) != expected:
                raise ValueError(f"Frozen input changed: {path}")
    if digest(native / "source_inputs.json") != manifest["source_inputs_sha256"]:
        raise ValueError("FORM_A source-input identity changed")
    sources = json.loads((native / "source_inputs.json").read_text())
    by_id = {s["brew"]: s for s in sources}
    if len(by_id) != 56 or set(by_id) != {s["brew"] for s in manifest["brews"]}:
        raise ValueError("Frozen 56-brew cohort changed")
    for row in manifest["brews"]:
        source = by_id[row["brew"]]
        if source["nominal_pressure_bar"] != row["nominal_pressure_bar"]:
            raise ValueError("Nominal condition changed")
        if digest(raw / "measurements_time_dependent" / (row["brew"] + ".txt")) != row["original_sha256"]:
            raise ValueError("Original trace changed")
    return by_id


def stage_a_reference(ewp):
    """Reproduce Stage A's exact endpoint observer; raise before time-series work.

    The original response_diagnostics is correct ONLY for this endpoint check.
    Its bootstrap seed is historical (20261029), separate from the time series.
    """
    brews = A.load_brews(ROOT / "puckworks/data/waszkiewicz2025", ewp)
    response = A.response_diagnostics(brews, brews.target)
    with (ROOT / "docs/research/PRESSURE_PEAK_STAGE_A/RESULT_TABLE.csv").open() as stream:
        historical = next(r for r in csv.DictReader(stream) if r["candidate"] == "B1")
    means = json.loads(historical["observed per-pressure flow g/s"])
    original = json.loads((ewp / "docs/analysis/sci_md_010/PRESSURE_RESPONSE_DIAGNOSTICS.json").read_text())[
        "HYD_B1_PRESSURE_QUADRATIC"]
    close = lambda x, y: np.testing.assert_allclose(x, y, rtol=0, atol=1e-10)
    rows = []
    for now, old, ewp_row in zip(response["per_pressure"], means, original["condition_means"], strict=True):
        close([now["pressure"], now["n"], now["mean"], now["direct_line"], *now["interval"]],
              [old["pressure"], old["n"], old["mean"], old["direct_line"], *old["interval"]])
        close([now["mean"], now["direct_line"]],
              [ewp_row["observed_flow_g_s"], ewp_row["line_pressure_bar"]])
        rows.append(dict(record_type="condition", nominal_pressure_bar=now["pressure"],
                         n=now["n"], flow_g_s=now["mean"], pressure_bar=now["direct_line"],
                         flow_lo=now["interval"][0], flow_hi=now["interval"][1],
                         historical_flow_g_s=old["mean"], historical_pressure_bar=old["direct_line"]))
    close(response["slope"], original["observed_high_slope"])
    assert original["observed_peak_conditions"] == [f"WASZ-COND-{response['peak']:.1f}"]
    # Stage A published the observed slope interval at four decimal places.
    assert [round(v, 4) for v in response["slope_interval"]] == [-.0880, -.0403]
    assert response["peak_interval"] == [5., 6.]
    rows.append(dict(record_type="response", slope_g_s_bar=response["slope"],
                     historical_slope_g_s_bar=original["observed_high_slope"],
                     slope_lo=response["slope_interval"][0], slope_hi=response["slope_interval"][1],
                     maximum_nominal_bar=response["peak"], maximum_lo=5., maximum_hi=6.,
                     bootstrap_seed=A.SEED, bootstrap_draws=A.N_BOOT))
    rows.extend(dict(record_type="brew", brew=brew, nominal_pressure_bar=float(p),
                     flow_g_s=float(q), pressure_bar=float(line))
                for brew, p, q, line in zip(brews.ids, brews.condition, brews.target, brews.pressure[:, -1]))
    return brews, rows


def paired_window(t, pressure, flow, center, *, valid=None, support_end=None):
    """Exact piecewise-linear means over [center-1, center+1], or missing reason.

    Both signals require the SAME genuine bracketing samples. Explicit masks,
    nonfinite values and a recorded support end prevent padding from entering.
    This function never clamps a boundary to the available support.
    """
    t = np.asarray(t, dtype=float)
    p = np.ma.asarray(pressure, dtype=float).filled(np.nan)
    q = np.ma.asarray(flow, dtype=float).filled(np.nan)
    if t.ndim != 1 or len(t) < 2 or p.shape != t.shape or q.shape != t.shape:
        raise ValueError("Expected equal-length native vectors")
    if not np.isfinite(t).all() or not np.all(np.diff(t) > 0):
        raise ValueError("Native timestamps must be finite and strictly increasing")
    if not np.isfinite(center):
        return np.nan, np.nan, "onset_undetected"
    start, end = center - 1., center + 1.
    last = t[-1] if support_end is None else min(t[-1], support_end)
    if start < t[0] or end > last:
        return np.nan, np.nan, "outside_recorded_support"
    left = np.searchsorted(t, start, side="right") - 1
    right = np.searchsorted(t, end, side="left")
    good = np.isfinite(p) & np.isfinite(q)
    if valid is not None:
        good &= np.asarray(valid, dtype=bool)
    if not good[left:right + 1].all():
        return np.nan, np.nan, "masked_or_nonfinite_support"
    nodes = np.r_[start, t[(t > start) & (t < end)], end]
    integrate = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
    return (float(integrate(np.interp(nodes, t, p), nodes) / 2.),
            float(integrate(np.interp(nodes, t, q), nodes) / 2.), "available")


def native_observation(path):
    """Inherited stable clock, terminal handling, derivative and onset operator."""
    t, p, mass, _ = B0.raw_trace(path)
    ct, cp, cq, _ = B0.clean_course(t, p, mass)
    pre = (t >= -2) & (t <= 0)
    baseline = np.median(mass[pre]) if pre.any() else mass[0]
    onset = B0.sustained_onset(ct, np.interp(ct, t, mass) - baseline, cq)
    return ct, cp, cq, onset, float(-t[0])


def observations(brews, sources, raw):
    """All 560 attempted windows; stable windows have no onset fitting mask."""
    p = np.full((len(SNAPSHOTS), len(brews.ids)), np.nan)
    q = p.copy()
    rows = []
    for i, brew in enumerate(brews.ids):
        ct, cp, cq, onset, offset = native_observation(raw / "measurements_time_dependent" / (brew + ".txt"))
        np.testing.assert_allclose(onset, sources[brew]["observed_onset_for_scoring_only_s"],
                                   rtol=0, atol=0, equal_nan=True)
        for j, (clock, target) in enumerate(SNAPSHOTS):
            center = target + (onset if clock == "onset" else 0.)
            p[j, i], q[j, i], reason = paired_window(ct, cp, cq, center)
            rows.append(dict(brew=brew, nominal_pressure_bar=float(brews.condition[i]),
                             clock=clock, time_s=target, window_start_stable_s=center - 1,
                             window_end_stable_s=center + 1, onset_stable_s=onset,
                             stable_offset_from_first_record_s=offset,
                             recorded_start_stable_s=float(ct[0]), recorded_end_stable_s=float(ct[-1]),
                             available=reason == "available", reason=reason,
                             pressure_bar=p[j, i], flow_g_s=q[j, i]))
    return p, q, rows


def draw_bank(condition, *, n_boot=N_BOOT, seed=SEED):
    """One immutable bank of whole-brew indices for every time and both clocks."""
    rng = np.random.default_rng(seed)
    bank = {float(c): rng.choice(np.flatnonzero(condition == c),
                                (n_boot, np.count_nonzero(condition == c)), replace=True)
            for c in np.unique(condition)}
    for draws in bank.values():
        draws.flags.writeable = False
    return bank


def bank_digest(bank):
    """Hash ordered, little-endian int64 brew indices (identity order in receipt)."""
    return hashlib.sha256(b"".join(a.astype("<i8").tobytes() for a in bank.values())).hexdigest()


def condition_statistics(p, q, condition, bank):
    """Paired available-brew means, with no replacement/redraw for missingness."""
    means_p, means_q, boot_p, boot_q, counts = [], [], [], [], []
    for c, draws in bank.items():
        group = np.flatnonzero(condition == c)
        valid = np.isfinite(p) & np.isfinite(q)
        def mean(values, indices):
            ok = valid[:, indices]
            n = ok.sum(axis=-1)
            total = np.where(ok, values[:, indices], 0.).sum(axis=-1)
            return np.divide(total, n, out=np.full(total.shape, np.nan), where=n > 0)
        means_p.append(mean(p, group))
        means_q.append(mean(q, group))
        boot_p.append(mean(p, draws))
        boot_q.append(mean(q, draws))
        counts.append(valid[:, group].sum(axis=-1))
    return tuple(np.stack(v, axis=-1) for v in (means_p, means_q, boot_p, boot_q, counts))


def high_slope(p, q, nominal):
    """Unweighted three-condition slope, using matched achieved window pressure."""
    high = np.isin(nominal, [9., 11., 13.])
    if high.sum() != 3:
        raise ValueError("Need nominal 9, 11 and 13 bar conditions")
    x, y = p[..., high], q[..., high]
    x = x - x.mean(axis=-1, keepdims=True)
    y = y - y.mean(axis=-1, keepdims=True)
    den = (x * x).sum(axis=-1)
    return np.divide((x * y).sum(axis=-1), den,
                     out=np.full(den.shape, np.nan), where=den > 0)


def maximum(q, nominal):
    """Available-condition maximum (exact ties), edge status and 13/max ratio."""
    ok = np.isfinite(q)
    missing = nominal[~ok].tolist()
    if not ok.any():
        return [], False, np.nan, missing
    best = np.max(q[ok])
    selected = nominal[ok & (q == best)].tolist()
    edges = nominal[ok][[0, -1]]
    ratio = q[np.flatnonzero(nominal == 13)[0]] / best if best > 0 else np.nan
    return selected, any(p in edges for p in selected), float(ratio), missing


def interval(values):
    """Stage A nearest-rank interval on finite, identically indexed draws."""
    values = np.asarray(values)
    finite = values[np.isfinite(values)]
    return A.interval(finite) if len(finite) else [np.nan, np.nan]


def uncertainty(name, point, draws):
    lo, hi = interval(draws)
    return {name: float(point), name + "_lo": lo, name + "_hi": hi,
            name + "_finite_draws": int(np.isfinite(draws).sum())}


def tables(p, q, condition, per_brew, bank):
    """Summarize frozen observations; all paired differences share draw indices."""
    nominal = np.array(list(bank))
    mp, mq, bp, bq, counts = condition_statistics(p, q, condition, bank)
    slopes, bs = high_slope(mp, mq, nominal), high_slope(bp, bq, nominal)
    condition_rows, slope_rows, availability = [], [], []
    for j, (clock, target) in enumerate(SNAPSHOTS):
        previous = j - 1 if j and SNAPSHOTS[j - 1][0] == clock else None
        common = dict(clock=clock, time_s=target)
        selected, edge, ratio, missing = maximum(mq[j], nominal)
        maxima = [maximum(row, nominal) for row in bq[j]]
        row = {**common, **uncertainty("slope_g_s_bar", slopes[j], bs[j]),
               **uncertainty("stable100_minus_current_g_s_bar", slopes[REFERENCE] - slopes[j], bs[REFERENCE] - bs[j]),
               "previous_time_s": SNAPSHOTS[previous][1] if previous is not None else "",
               **uncertainty("current_minus_previous_g_s_bar", slopes[j] - slopes[previous] if previous is not None else np.nan,
                             bs[j] - bs[previous] if previous is not None else np.full(N_BOOT, np.nan)),
               "maximum_nominal_bar": selected, "maximum_at_available_edge": edge,
               "missing_nominal_conditions": missing,
               **uncertainty("ratio_13_to_max", ratio, [r[2] for r in maxima]),
               "maximum_selection_fractions": {str(c): sum(c in r[0] for r in maxima) / len(maxima) for c in nominal},
               "maximum_tied_draws": sum(len(r[0]) > 1 for r in maxima),
               "maximum_missing_condition_draws": sum(bool(r[3]) for r in maxima),
               "maximum_unavailable_draws": sum(not r[0] for r in maxima)}
        slope_rows.append(row)
        for k, c in enumerate(nominal):
            condition_rows.append({**common, "nominal_pressure_bar": c, "n_available": int(counts[j, k]),
                                   **uncertainty("flow_g_s", mq[j, k], bq[j, :, k]),
                                   **uncertainty("pressure_bar", mp[j, k], bp[j, :, k]),
                                   **uncertainty("stable100_minus_current_flow_g_s", mq[REFERENCE, k] - mq[j, k], bq[REFERENCE, :, k] - bq[j, :, k]),
                                   **uncertainty("current_minus_previous_flow_g_s", mq[j, k] - mq[previous, k] if previous is not None else np.nan,
                                                 bq[j, :, k] - bq[previous, :, k] if previous is not None else np.full(N_BOOT, np.nan))})
            cells = [r for r in per_brew if r["clock"] == clock and r["time_s"] == target and r["nominal_pressure_bar"] == c]
            availability.append({**common, "nominal_pressure_bar": c, "n_total": len(cells),
                                 "n_available": sum(r["available"] for r in cells),
                                 "n_window_starts_before_onset": sum(r["available"] and r["window_start_stable_s"] < r["onset_stable_s"] for r in cells),
                                 "unavailable_reasons": {reason: sum(r["reason"] == reason for r in cells) for reason in sorted({r["reason"] for r in cells if not r["available"]})}})
    return condition_rows, slope_rows, availability


def figure(rows, out):
    """One two-panel descriptive figure; connecting lines are not fitted curves."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({"font.size": 10, "svg.hashsalt": "WASZ_TURNOVER_TIME_001"})
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharex=True, sharey=True)
    colors = {10: "#440154", 20: "#414487", 30: "#2a788e", 40: "#22a884", 60: "#7ad151", 100: "#111111"}
    for ax, clock, title in zip(axes, ("stable_pressure", "onset"), ("Since stable pressure", "Since detected onset")):
        for c, target in SNAPSHOTS:
            if c != clock:
                continue
            subset = [r for r in rows if r["clock"] == c and r["time_s"] == target]
            ax.plot([r["pressure_bar"] for r in subset], [r["flow_g_s"] for r in subset],
                    "o-", color=colors[target], lw=2.5 if target == 100 else 1.4,
                    ms=5 if target == 100 else 3.5, label=f"{target} s")
        ax.set(title=title, xlabel="Mean achieved line pressure (bar)", xlim=(0, 14))
        ax.axhline(0, color="0.8", lw=.7)
        ax.grid(alpha=.15)
        ax.legend(frameon=False, ncol=3, title="Window center",
                  loc="upper center", bbox_to_anchor=(.5, -.16))
    axes[0].set_ylabel("Mean beverage-mass-derived flow (g/s)")
    fig.suptitle("Waszkiewicz: pressure–flow snapshots during brewing", fontsize=14)
    fig.text(.5, .015, "2-s centered windows · points are nominal-condition means · lines connect observations, not fits", ha="center", fontsize=9)
    fig.subplots_adjust(left=.075, right=.98, top=.85, bottom=.29, wspace=.09)
    fig.savefig(out / "FLOW_BY_PRESSURE.svg", metadata={"Date": None})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=OUT)
    parser.add_argument("--reference-only", action="store_true")
    args = parser.parse_args()
    started, cpu = time.perf_counter(), time.process_time()
    sources = authenticate(args.ewp, args.raw, args.native)
    brews, reference = stage_a_reference(args.ewp)  # STOP on mismatch, before snapshots.
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "STAGE_A_REFERENCE.csv", reference)
    print("Exact Stage A endpoint reproduction: PASS", flush=True)
    if args.reference_only:
        return
    p, q, per_brew = observations(brews, sources, args.raw)
    bank = draw_bank(brews.condition)
    conditions, slopes, availability = tables(p, q, brews.condition, per_brew, bank)
    for name, rows in (("PER_BREW_BY_TIME", per_brew), ("CONDITION_MEANS_BY_TIME", conditions),
                       ("TIME_SLOPES", slopes), ("AVAILABILITY", availability)):
        write_csv(args.output / (name + ".csv"), rows)
    figure(conditions, args.output)
    receipt = dict(plan_sha256=digest(OUT / "PLAN.md"), input_manifest_sha256=digest(OUT / "INPUT_MANIFEST.json"),
                   code_sha256={str(Path(__file__).relative_to(ROOT)): digest(__file__)},
                   bootstrap_seed=SEED, bootstrap_draws=N_BOOT, draw_bank_sha256=bank_digest(bank),
                   brew_order=brews.ids, stage_a_reference="PASS", n_brews=len(brews.ids),
                   attempted_windows=len(per_brew), available_windows=int(np.isfinite(q).sum()),
                   runtime=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                   wall_seconds=time.perf_counter() - started, cpu_seconds=time.process_time() - cpu)
    receipt["core_hours"] = receipt["cpu_seconds"] / 3600
    (args.output / "RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({k: v for k, v in receipt.items() if k not in ("brew_order", "code_sha256")}, indent=2))


if __name__ == "__main__":
    main()

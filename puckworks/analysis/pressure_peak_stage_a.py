"""PRESSURE-PEAK Stage A: isolated, retrospective Python mechanism screen.

No registry imports or writes; external sources are opened read-only. Data are
Waszkiewicz et al. (2025), Zenodo 10.5281/zenodo.18046315, CC-BY-4.0. No source
GPL code is imported/copied. See the dataset PROVENANCE.md for the reduction.

Run the data-only check FIRST:
  python -m puckworks.analysis.pressure_peak_stage_a --ewp EWP --raw SOURCE --audit-only
After inspecting confounders, run with --screen. Output is aggregate CSV and
stdout diagnostics, never new scientific authority/receipt records.

P is direct line pressure (bar), q is g/s, t seconds, delivered mass grams.
C1-C4 are conditional whole-system laws, not identified intrinsic permeability.
They never use the basket pressure derived from the observed flow. W-H0A retains
its fixed machine calibration, with its two coefficients refitted to the endpoint
target (the historical dynamic-mass score is not reused). Endpoints, canonical brew identities, fitting
weights and folds match SCI-MD-010. The reported dimensional loss is the equal
mean of held-out-condition RMSEs; its normalized counterpart is also reported.
The user requests g/s, hence the primary displayed loss omits SCI-MD-010's
outer-training flow-range division. It does not pool all 56 squared errors.

C1-exp: a P exp(-P/Pstar), 2 parameters.
C1-power: a P (1+P/Pc)^(-n), 3 parameters, optimized as
    (a, inverse_Pc, n_over_Pc), including inverse_Pc=0's exponential limit.
C2-m1/m2: q=P/R, Rdot=beta q**m R0; m fixed, R(0)=R0, 2 parameters.
C3: q=a P exp(-S/Pstar); S jumps up to new P maxima and relaxes toward
    current P with tau during pressure decreases, S(0)=P(0), 3 parameters.
C4: q=a P exp(-P/Pstar) exp(-exp(-M/Mc)), Mdot=q, M(0)=0,
    3 parameters. This is W-H2's delivered-mass exponential log resistance,
    with transient amplitude fixed at 1, combined with C1-exp. No stored fitted
    parameter is borrowed; W-H2 was selected solely by its stored LOCO loss.

Time zero is the stored pressure-aligned trace start; no unobserved prehistory
or per-brew initial-state parameter is inferred. Slopes and peaks are computed
from out-of-fold condition means, not a separate all-data fitted curve. All
prediction intervals condition on the fitted coefficients. Author exclusions
and unknown acquisition chronology/batch metadata preclude causal attribution.

The first numerical search for C1-power reached Pc=100 bar in all training
folds. The final parameterization removes that arbitrary ceiling by including
the exponential limit; it changes neither the family nor its parameter budget.

Local quasi-static compaction q proportional to integral_0^P k(sigma) ds,
k>=0, has dq/dP>=0 and is excluded analytically. None of C1-C4 reduces to
that form. C2 nevertheless cannot peak at a common time under constant P:
R**(m+1)=R0**(m+1)+(m+1)*beta*R0*P**m*t, so dlog(q)/dlog(P)>0.

Restart diagnostic compares flow at matched applied pressure, without resetting
states. C1 and B1/W-H0A have no restart response; C2 keeps added resistance and
predicts lower flow; C3 instantly recompacts on reapplication and cannot explain
a persistent increase at the same pressure. C4 predicts higher later flow from
continued delivery, but no separate benefit of stopping. The actual restart
record's off-state line pressure (~3 bar with closed valves) is NOT a driving
puck pressure; forcing it through these flow laws would be erroneous.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

SEED = 20261029
N_BOOT = 1000
TOLERANCE = 0.25
MODELS = ("B1", "W-H0A", "C1-exp", "C1-power", "C2-m1", "C2-m2", "C3", "C4")
PARAMETER_NAMES = {
    "B1": ["intercept_g_s", "linear_g_s_bar", "quadratic_g_s_bar2"],
    "W-H0A": ["log_resistance_intercept", "log_pressure_coefficient"],
    "C1-exp": ["a_g_s_bar", "Pstar_bar"],
    "C1-power": ["a_g_s_bar", "inverse_Pc_per_bar", "n_over_Pc_per_bar"],
    "C2-m1": ["R0_bar_s_g", "beta_per_g"],
    "C2-m2": ["R0_bar_s_g", "beta_s_g2"],
    "C3": ["a_g_s_bar", "Pstar_bar", "tau_s"],
    "C4": ["a_g_s_bar", "Pstar_bar", "Mc_g"],
}
ROOT = Path(__file__).resolve().parents[2]
MACHINE = (0.017184292098914252, 0.03670858658698296, 0.2831597837775055)


def read_csv(path):
    with Path(path).open(newline="") as stream:
        return list(csv.DictReader(stream))


def interval(values):
    """SCI-MD-010 nearest-rank 95% interval, not interpolated quantiles."""
    values = np.sort(values)
    return [float(values[math.ceil(p * len(values)) - 1]) for p in (0.025, 0.975)]


def slope(x, y):
    x, y = np.asarray(x), np.asarray(y)
    return float(np.sum((x-x.mean())*(y-y.mean())) / np.sum((x-x.mean())**2))


@dataclass
class Brews:
    ids: list[str]
    condition: np.ndarray
    pressure: np.ndarray
    target: np.ndarray
    t: np.ndarray
    windows: dict[str, np.ndarray]
    fold: list[str]
    aggregate_max_difference: float

    @property
    def groups(self):
        return [np.flatnonzero(self.condition == p) for p in np.unique(self.condition)]


def load_brews(data: Path, ewp: Path) -> Brews:
    """Join by source IDs and validate against historical rows/fold membership."""
    rows = read_csv(data / "traces_per_brew.csv")
    traces = {}
    for row in rows:
        traces.setdefault(row["shot_id"], []).append(row)
    for trace in traces.values():
        trace.sort(key=lambda row: int(row["time_index"]))
        if [int(row["time_index"]) for row in trace] != list(range(1000)):
            raise ValueError("Incomplete trace")
    windows = read_csv(data / "equilibrium_windows.csv")
    window_lookup = {(r["shot_id"], r["window"]): float(r["mass_flow_rate__g_per_s"])
                     for r in windows}
    historical = [r for r in read_csv(ewp / "docs/analysis/sci_md_010/BREW_RESULTS.csv")
                  if r["model_id"] == "HYD_B1_PRESSURE_QUADRATIC"]
    historical.sort(key=lambda r: (float(r["condition_id"].split("-")[-1]),
                                   r["physical_unit_id"]))
    ids = [r["physical_unit_id"].removeprefix("WASZ-BREW-") for r in historical]
    if len(ids) != 56 or len(set(ids)) != 56 or any("_alt" in i for i in ids):
        raise ValueError("Canonical SCI-MD-010 cohort changed")
    folds = read_csv(ewp / "docs/analysis/sci_md_010/FOLD_ASSIGNMENTS.csv")
    for fold in folds:
        actual = {r["physical_unit_id"] for r in historical
                  if r["outer_fold"] == fold["outer_fold"]}
        if actual != set(fold["evaluation_physical_units"].split(";")):
            raise ValueError("SCI-MD-010 fold mismatch")
    pressure = np.array([[float(r["pressure__bar"]) for r in traces[i]] for i in ids])
    target = np.array([window_lookup[i, "endpoint_100s"] for i in ids])
    np.testing.assert_allclose(pressure[:, -1], [float(r["line_pressure_bar"])
                                               for r in historical], atol=1e-10, rtol=0)
    np.testing.assert_allclose(target, [float(r["observed_flow_g_s"])
                                       for r in historical], atol=1e-10, rtol=0)
    # Reproduce the published means WITH their duplicate, then score WITHOUT it.
    published = read_csv(data / "traces_time_dependent.csv")
    aggregates = {}
    for row in rows:
        key = (float(row["reference_pressure_round__bar"]), int(row["time_index"]))
        aggregates.setdefault(key, []).append(float(row["mass_flow_rate__g_per_s"]))
    differences = [abs(np.mean(aggregates[float(r["reference_pressure_round__bar"]),
                                         round(float(r["time__s"]) * 999 / 100)])
                       - float(r["mass_flow_rate__g_per_s"])) for r in published]
    # Per-brew export has five decimal places; the published means have six.
    if max(differences) > 1e-5:
        raise ValueError("Per-brew traces do not reproduce published means")
    return Brews(ids, np.array([float(traces[i][0]["reference_pressure_round__bar"])
                               for i in ids]), pressure, target, np.linspace(0, 100, 1000),
                 {w: np.array([window_lookup[i, w] for i in ids])
                  for w in ("endpoint_100s", "mean_90_100s", "mean_110_120s")},
                 [r["outer_fold"] for r in historical], float(max(differences)))


def response_diagnostics(brews, values, seed=SEED):
    """Conditional brew bootstrap: preserve every pressure for slope/peak."""
    rng = np.random.default_rng(seed)
    groups = brews.groups
    pressures = np.unique(brews.condition)
    x = np.array([brews.pressure[g, -1].mean() for g in groups])
    y = np.array([values[g].mean() for g in groups])
    xb, yb = [], []
    for g in groups:
        draws = rng.choice(g, (N_BOOT, len(g)), replace=True)
        xb.append(brews.pressure[draws, -1].mean(axis=1))
        yb.append(values[draws].mean(axis=1))
    xb, yb = np.array(xb).T, np.array(yb).T
    high = pressures >= 9  # Same conditions as SCI-MD-010 direct-line >=8.5.
    slopes = [slope(a[high], b[high]) for a, b in zip(xb, yb)]
    peaks = pressures[np.argmax(yb, axis=1)]
    return {
        "slope": slope(x[high], y[high]), "slope_interval": interval(slopes),
        "peak": float(pressures[np.argmax(y)]), "peak_interval": interval(peaks),
        "per_pressure": [{"pressure": float(p), "n": len(g), "mean": float(y[j]),
                          "interval": interval(yb[:, j]), "direct_line": float(x[j])}
                         for j, (p, g) in enumerate(zip(pressures, groups))],
    }


def raw_window_check(brews, raw):
    """Mass-increment control on ORIGINAL clock; never refits any model."""
    control, details = [], []
    for shot in brews.ids:
        records = [json.loads(line) for line in
                   (raw / "measurements_time_dependent" / f"{shot}.txt").read_text().splitlines()
                   if line.strip()]
        complete = [r for r in records if "t" in r and "m" in r]
        t = np.array([r["t"] / 1000 for r in complete])
        mass = np.array([r["m"] for r in complete])
        pressure = np.array([r["p2"] / 100 for r in complete])
        median = np.median(pressure)
        bad = np.flatnonzero((pressure[:501] < max(.9*median, median-.5)) |
                             (pressure[:501] > min(1.1*median, median+.5)))
        start = int(bad[-1]+1) if len(bad) else 0
        window = (t >= 90) & (t <= 100)
        q = (mass[window][-1]-mass[window][0]) / (t[window][-1]-t[window][0])
        control.append(q)
        aligned = (t-t[start] >= 90) & (t-t[start] <= 100)
        details.append({"offset": float(t[start]), "end": float(t[-1]-t[start]),
                        "min_mass_step": float(np.diff(mass[aligned]).min()),
                        "incomplete": len(records)-len(complete)})
    return {"original_clock_90_100": response_diagnostics(brews, np.array(control)),
            "minimum_aligned_end_s": min(d["end"] for d in details),
            "minimum_90_100_mass_step_g": min(d["min_mass_step"] for d in details),
            "incomplete_terminal_records": sum(d["incomplete"] for d in details),
            "alignment_offset_range_by_pressure": {
                str(p): [min(details[i]["offset"] for i in g),
                         max(details[i]["offset"] for i in g)]
                for p, g in zip(np.unique(brews.condition), brews.groups)}}


def data_check(brews, raw):
    result = response_diagnostics(brews, brews.target)
    loo_slopes, loo_peaks = [], []
    for omitted in range(len(brews.ids)):
        groups = [g[g != omitted] for g in brews.groups]
        x = np.array([brews.pressure[g, -1].mean() for g in groups])
        y = np.array([brews.target[g].mean() for g in groups])
        high = np.unique(brews.condition) >= 9
        loo_slopes.append(slope(x[high], y[high]))
        loo_peaks.append(np.unique(brews.condition)[np.argmax(y)])
    result.update(loo_slope_range=[min(loo_slopes), max(loo_slopes)],
                  loo_peak_range=[float(min(loo_peaks)), float(max(loo_peaks))],
                  windows={w: response_diagnostics(brews, q)
                           for w, q in brews.windows.items()},
                  published_mean_max_difference=brews.aggregate_max_difference,
                  raw=raw_window_check(brews, raw))
    result["robust_numeric_peak"] = bool(result["slope_interval"][1] < 0 and
                                         max(loo_slopes) < 0 and
                                         result["raw"]["original_clock_90_100"]["slope_interval"][1] < 0)
    return result


def local_compaction_flow(pressure, scale=3.0):
    """Example k=exp(-sigma/scale): integral remains monotone despite compaction."""
    return -scale * np.expm1(-np.asarray(pressure) / scale)


def relaxation_state(pressure, t, tau):
    """Piecewise-linear pressure; exact relaxed update, clamped to new maximum."""
    state = pressure[:, 0].copy()
    for j, dt in enumerate(np.diff(t), 1):
        decay = np.exp(-dt / tau)
        change = (pressure[:, j]-pressure[:, j-1]) / dt
        relaxed = pressure[:, j] - change*tau + (
            state-pressure[:, j-1]+change*tau)*decay
        state = np.maximum(pressure[:, j], relaxed)
    return state


def delivered_state(exposure):
    """Invert integral_0^x exp(exp(-u)) du; stable even for large delivered mass.

    C4 separates in the operational time integral(a P exp(-P/Pstar) dt)/Mc.
    The convergent series avoids Ei(exp(-x)) underflow/cancellation. Newton is
    solving only a numerical state, not adding any fitted parameter.
    """
    x = np.asarray(exposure).copy()
    for _ in range(8):
        series = np.zeros_like(x)
        for k in range(1, 20):
            series -= np.expm1(-k*x) / (k*math.factorial(k))
        x = np.maximum(0, x - (x+series-exposure) / np.exp(np.exp(-x)))
    return x


def predict(model, parameters, pressure, t):
    pressure = np.maximum(np.asarray(pressure), 0)
    end = pressure[:, -1]
    if model == "B1":
        return np.maximum(0, parameters[0]+parameters[1]*end+parameters[2]*end**2)
    if model == "W-H0A":
        r = np.exp(parameters[0]+parameters[1]*np.log(np.maximum(end, .4)))
        a, b, c = MACHINE
        d = np.maximum(end-c, 0)
        return 2*d / (b+r+np.sqrt((b+r)**2+4*a*d))
    if model == "C1-power":
        a, inverse_pc, n_over_pc = parameters
        exponent = end if inverse_pc == 0 else np.log1p(end*inverse_pc)/inverse_pc
        return a*end*np.exp(-n_over_pc*exponent)
    if model.startswith("C2"):
        r0, beta = parameters
        m = int(model[-1])
        left, right = pressure[:, :-1], pressure[:, 1:]
        # Exact integral of P**m on each linearly interpolated history segment.
        power_mean = (left+right)/2 if m == 1 else (left**2+left*right+right**2)/3
        exposure = np.sum(power_mean*np.diff(t), axis=1)
        r = (r0**(m+1)+(m+1)*beta*r0*exposure)**(1/(m+1))
        return end/r
    a, pstar = parameters[:2]
    if model == "C3":
        return a*end*np.exp(-relaxation_state(pressure, t, parameters[2])/pstar)
    base = a*pressure*np.exp(-pressure/pstar)
    if model == "C4":
        exposure = np.sum((base[:, :-1]+base[:, 1:])/2*np.diff(t), axis=1)
        x = delivered_state(exposure/parameters[2])
        return base[:, -1]*np.exp(-np.exp(-x))
    if model == "C1-exp":
        return base[:, -1]
    raise ValueError(model)


# Broad numerical search bounds, not physical authority. Positive parameters
# fitted in log coordinates. W-H0A uses its two log-resistance coefficients.
BOUNDS_STARTS = {
    "W-H0A": ([-10, -3], [10, 5], [[1, .5], [0, 1.5]]),
    "C1-exp": ([.001, .1], [20, 100], [[1, 5], [.5, 12]]),
    "C1-power": ([.001, 0, 1e-5], [100, 20, 20],
                 [[2, 1/3, 2/3], [1, 1/12, 3/12], [1, 1e-5, .15]]),
    "C2-m1": ([.01, 1e-8], [100, 10], [[2, .01], [4, .0001]]),
    "C2-m2": ([.01, 1e-8], [100, 10], [[2, .01], [4, .0001]]),
    "C3": ([.001, .1, .05], [20, 100, 1000], [[1, 5, 1], [1, 5, 30], [1, 5, 300]]),
    "C4": ([.001, .1, .01], [20, 100, 1000], [[1, 5, 30], [2, 5, 150], [2, 12, 500]]),
}


class FitBudget:
    def __init__(self, limit=7200):
        self.elapsed = 0.0
        self.limit = limit

    def check(self, started):
        if self.elapsed + time.monotonic()-started > self.limit:
            raise TimeoutError("Two-hour total fitting budget exhausted; STOP")


def fit(model, pressure, t, target, weights, budget=None):
    budget = budget or FitBudget()
    started = time.monotonic()
    try:
        if model == "B1":
            p = pressure[:, -1]
            design = np.column_stack([np.ones(len(p)), p, p*p])
            return np.linalg.lstsq(design*np.sqrt(weights[:, None]),
                                   target*np.sqrt(weights), rcond=None)[0]
        lower, upper, starts = BOUNDS_STARTS[model]
        def transform(x):
            if model == "W-H0A":
                return x
            if model == "C1-power":
                return np.array([np.log(x[0]), x[1], np.log(x[2])])
            return np.log(x)

        def inverse(x):
            if model == "W-H0A":
                return x
            if model == "C1-power":
                return np.array([np.exp(x[0]), x[1], np.exp(x[2])])
            return np.exp(x)

        def residual(x):
            budget.check(started)
            return (predict(model, inverse(x), pressure, t)-target)*np.sqrt(weights)

        fits = [least_squares(residual, transform(np.array(initial, dtype=float)),
                              bounds=(transform(np.array(lower)), transform(np.array(upper))),
                              ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=500)
                for initial in starts]
        successful = [f for f in fits if f.success and np.all(np.isfinite(f.fun))]
        if not successful:
            raise RuntimeError(f"No converged fit: {model}")
        best = min(successful, key=lambda f: f.cost)
        return inverse(best.x)
    finally:
        budget.elapsed += time.monotonic()-started


def nested_loss_draws(brews, predictions):
    """Exact SCI-MD-010 resampling units: conditions, then paired brews; no refit."""
    rng = random.Random(SEED)
    groups = [np.flatnonzero(np.array(brews.fold) == f).tolist() for f in sorted(set(brews.fold))]
    squared = (predictions-brews.target[None, :])**2
    draws = []
    for _ in range(N_BOOT):
        selected = [rng.choice(groups) for _ in groups]
        loss = np.zeros(len(predictions))
        for group in selected:
            picked = [rng.choice(group) for _ in group]
            loss += np.sqrt(squared[:, picked].mean(axis=1))
        draws.append(loss/len(groups))
    return np.array(draws)


def capability(bounds, high_slope):
    if high_slope >= 0 or bounds[0] > TOLERANCE:
        return "NOT CAPABLE"
    return "CAPABLE" if bounds[1] <= TOLERANCE else "UNRESOLVED"


def comparison(bounds):
    if bounds[1] < 0:
        return "BETTER"
    if bounds[0] > 0:
        return "WORSE"
    if bounds[0] >= -TOLERANCE and bounds[1] <= TOLERANCE:
        return "TIE"
    return "UNRESOLVED"


def screen(brews, ewp, out):
    """Only called after data check and human inspection of source metadata."""
    budget = FitBudget()
    predictions, coefficients, scales, numerical_changes = [], {}, [], {}
    for g in brews.groups:
        training = [h for h in brews.groups if h[0] not in g]
        scales.append(float(np.ptp([brews.target[h].mean() for h in training])))
    for model in MODELS:
        q = np.zeros(len(brews.ids))
        coefficients[model] = {}
        numeric_max = 0.0
        for g in brews.groups:
            train = np.flatnonzero(brews.condition != brews.condition[g[0]])
            weights = np.array([1/(10*np.sum(brews.condition[train] == brews.condition[i]))
                                for i in train])
            parameters = fit(model, brews.pressure[train], brews.t, brews.target[train],
                             weights, budget)
            q[g] = predict(model, parameters, brews.pressure[g], brews.t)
            coefficients[model][brews.fold[g[0]]] = parameters.tolist()
            if model in {"C3", "C4"}:
                fine_t = np.linspace(0, 100, 1999)
                fine_p = np.array([np.interp(fine_t, brews.t, p) for p in brews.pressure[g]])
                fine_q = predict(model, parameters, fine_p, fine_t)
                numeric_max = max(numeric_max, float(np.max(np.abs(fine_q-q[g]))))
        if not np.all(np.isfinite(q)):
            raise ValueError(f"Nonfinite held-out prediction: {model}")
        predictions.append(q)
        numerical_changes[model] = numeric_max
        print(json.dumps({"completed": model, "fit_seconds": budget.elapsed}), flush=True)
    predictions = np.array(predictions)
    # Recover the stored baseline to machine precision, not merely its score.
    stored = {r["physical_unit_id"].removeprefix("WASZ-BREW-"): float(r["predicted_flow_g_s"])
              for r in read_csv(ewp / "docs/analysis/sci_md_010/BREW_RESULTS.csv")
              if r["model_id"] == "HYD_B1_PRESSURE_QUADRATIC"}
    np.testing.assert_allclose(predictions[0], [stored[i] for i in brews.ids], atol=1e-9, rtol=0)
    losses = np.array([[np.sqrt(np.mean((q[g]-brews.target[g])**2))
                       for g in brews.groups] for q in predictions])
    draws = nested_loss_draws(brews, predictions)
    rows = []
    for j, (model, q) in enumerate(zip(MODELS, predictions)):
        response = response_diagnostics(brews, q)
        ci, delta_ci = interval(draws[:, j]), interval(draws[:, j]-draws[:, 0])
        verdict = comparison(delta_ci)
        restart = ("lower (inconsistent)" if model.startswith("C2") else
                   "higher (consistent direction; continued delivery, no pause benefit)"
                   if model == "C4" else "cannot say (no persistent matched-pressure increase)")
        row = {
            "candidate": model, "parameters": parameter_description(model, coefficients[model]),
            "RMSE g/s": float(losses[j].mean()), "RMSE interval g/s": json.dumps(ci),
            "CAPABILITY": capability(ci, response["slope"]),
            "delta versus B1 g/s": float((losses[j]-losses[0]).mean()),
            "delta interval g/s": json.dumps(delta_ci), "COMPARISON": verdict,
            "high-pressure slope g/s/bar": response["slope"],
            "slope interval g/s/bar": json.dumps(response["slope_interval"]),
            "peak location bar": response["peak"],
            "peak interval bar": json.dumps(response["peak_interval"]),
            "restart consistency": restart,
            "PASS": "Y" if model.startswith("C") and response["slope"] < 0
                    and verdict in {"BETTER", "TIE"} else "N",
            "SCI-MD-010 normalized RMSE": float(np.mean(losses[j]/scales)),
            "maximum refined-grid change g/s": numerical_changes[model],
            "observed per-pressure flow g/s": json.dumps(
                response_diagnostics(brews, brews.target)["per_pressure"], separators=(",", ":"))
                if model == "B1" else "",
        }
        rows.append(row)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "RESULT_TABLE.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return {"fit_seconds": budget.elapsed, "results": rows}


def parameter_description(model, by_fold):
    fixed = {"m": int(model[-1])} if model.startswith("C2") else (
        {"log_resistance_transient_amplitude": 1} if model == "C4" else {})
    return json.dumps({"names": PARAMETER_NAMES[model], "fixed": fixed,
                       "by_fold": by_fold}, separators=(",", ":"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "puckworks/data/waszkiewicz2025")
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audit-only", action="store_true")
    mode.add_argument("--screen", action="store_true")
    parser.add_argument("--out", type=Path, default=ROOT / "docs/research/PRESSURE_PEAK_STAGE_A")
    args = parser.parse_args()
    brews = load_brews(args.data, args.ewp)
    checked = data_check(brews, args.raw)
    print(json.dumps({"step0": checked}, indent=2), flush=True)
    if args.screen:
        if not checked["robust_numeric_peak"]:
            raise SystemExit("Peak not robust: none — stop; no fitting performed")
        print(json.dumps(screen(brews, args.ewp, args.out), indent=2))


if __name__ == "__main__":
    main()

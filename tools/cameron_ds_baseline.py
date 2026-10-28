#!/usr/bin/env python3
"""Exposed Cameron Figure 5 reconstruction; process-isolated D_S overrides.

No production parameters are changed on disk. Each numerical group gets a new
interpreter; only that child's D_S is assigned after import. All seven grinds
remain together. `score` reuses retained executions without new integrations.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BUNDLE = ROOT / "docs/analysis/sci_md_cameron_ds_baseline_001"
MODEL = ROOT / "puckworks/models/cameron2020/extraction_bdf.py"
GRINDS = [1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, data):
    Path(path).write_text(json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + "\n")


def csv_write(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def targets():
    with (BUNDLE / "TARGETS.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    if [float(r["gs"]) for r in rows] != GRINDS:
        raise ValueError("The seven authenticated grinds must be retained in source order")
    return rows


def worker(args):
    """One fresh process per group; no reuse of workers across diffusivities."""
    import numpy as np
    from puckworks.models.cameron2020 import extraction_bdf as model

    request = read(args.request)
    method = request["method"]
    original_ds = model.D_S
    if request["override"]:
        model.D_S = request["D_S_m2_s"]
    elif request["D_S_m2_s"] != original_ds:
        raise ValueError("Ordinary baseline cannot override D_S")
    if model.K_RATE != 6e-7 or model.C_S0 != 118 or model.PHI_S != .8272:
        raise ValueError("Frozen physical defaults changed")
    rows = []
    for gs in GRINDS:
        started = time.monotonic()
        row = dict(gs=gs, D_S_m2_s=model.D_S, status="STARTED")
        rows.append(row)
        write(args.output, rows)  # Includes attempted integrations if a child fails.
        try:
            result = model.simulate_shot(gs, p_bar=5., m_in=.020, m_out=.040,
                                         N=method["N"], M=method["M"], n_save=120,
                                         rtol=method["rtol"], atol=method["atol"], c_s0=118.)
            phi1, phi2, a2, _, _ = model.grind_microstructure(gs)
            volume = np.pi * model.R0**2 * model.bed_depth(.020)
            # Independent shell-volume reduction, not SphereGrid or EY_solid.
            def solid_mass(field, radius, phase):
                nodes = np.linspace(0., radius, field.shape[1])
                faces = np.r_[0., (nodes[:-1] + nodes[1:]) / 2, radius]
                weights = np.diff(faces**3) / radius**3
                return float(volume * phase * np.mean(field @ weights))
            initial = volume * (phi1 + phi2) * 118.
            final = solid_mass(result.cs1_final, model.A1, phi1) + solid_mass(
                result.cs2_final, a2, phi2)
            liquid = volume * (1 - model.PHI_S) * float(np.mean(result.cl_final))
            cup = float(result.m_cup[-1])
            balance = initial - final - liquid - cup
            fields_min = min(float(np.min(x)) for x in
                             (result.cs1_final, result.cs2_final, result.cl_final))
            if (not np.isfinite(result.EY) or abs(balance) > 2e-11
                    or abs(result.EY - 100 * cup / .020) > 1e-10
                    or abs(result.EY - result.EY_solid) > 1e-7
                    or fields_min < -1e-8 or not 0 < cup < initial):
                raise ValueError("Numerical mass/finite-state contract failed")
            np.savez(args.output.parent / f"{args.output.stem}-gs{gs:.1f}.npz",
                     t=result.t, m_cup=result.m_cup, cl_out=result.cl_out,
                     cl_final=result.cl_final, cs1_final=result.cs1_final,
                     cs2_final=result.cs2_final)
            row.update(status="SUCCESS", EY_pp=float(result.EY), cup_solute_kg=cup,
                       initial_solute_kg=float(initial), final_solid_solute_kg=final,
                       liquid_solute_kg=liquid, balance_residual_kg=float(balance),
                       EY_minus_solid_pp=float(result.EY - result.EY_solid),
                       minimum_final_concentration_kg_m3=fields_min,
                       endpoint_s=float(result.t_shot),
                       Ds1_dimensionless=float(model.D_S * result.t_shot / model.A1**2),
                       Ds2_dimensionless=float(model.D_S * result.t_shot / a2**2))
        except Exception as error:
            row.update(status="FAILED", error_type=type(error).__name__,
                       message=str(error).replace(str(ROOT), "[checkout]"))
        row["elapsed_s"] = time.monotonic() - started
        write(args.output, rows)
        if row["status"] != "SUCCESS":
            return 1
    return 0


def run(private):
    import numpy as np
    from scipy.optimize import minimize_scalar

    if private.resolve().is_relative_to(ROOT):
        raise ValueError("Execution receipts must remain outside Git")
    private.mkdir(parents=True, exist_ok=True, mode=0o700)
    state_path = private / "run_state.json"
    if state_path.exists():
        raise ValueError("Retained execution exists; use score, not another fit")
    config = read(BUNDLE / "RESULTS.json")
    if config["runner_sha256"] != sha(__file__) or config["model_sha256"] != sha(MODEL):
        raise ValueError("Code differs from the frozen analysis")
    if config["targets_sha256"] != sha(BUNDLE / "TARGETS.csv"):
        raise ValueError("Targets differ from the frozen analysis")
    method = config["methods"]
    y = np.array([float(r["theory_EY_pp"]) for r in targets()])
    state = dict(config_sha256=sha(BUNDLE / "RESULTS.json"), methods=method,
                 groups=[], evaluations=[], status="RUNNING", integrations=0)
    write(private / "frozen_inputs.json", config)
    start = time.monotonic()

    def group(label, ds, resolution, override=True):
        remaining = method["model_elapsed_limit_s"] - (time.monotonic() - start)
        if remaining <= 0 or state["integrations"] + 7 > 126:
            raise RuntimeError("Frozen model budget exhausted")
        request = dict(D_S_m2_s=float(ds), method=resolution, override=override)
        req = private / f"{label}-request.json"
        out = private / f"{label}.json"
        write(req, request)
        receipt = dict(label=label, request=request, status="STARTED")
        state["groups"].append(receipt)
        write(state_path, state)
        with (private / f"{label}.log").open("w") as log:
            try:
                proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "worker",
                                       "--request", str(req), "--output", str(out)],
                                      stdout=log, stderr=subprocess.STDOUT,
                                      timeout=remaining,
                                      env=dict(os.environ, PYTHONPATH=str(ROOT),
                                               OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1"))
                receipt["returncode"] = proc.returncode
            except subprocess.TimeoutExpired:
                receipt["returncode"] = None
                receipt["timeout"] = True
        rows = read(out) if out.exists() else []
        state["integrations"] += len(rows)
        receipt.update(rows=rows, output_sha256=sha(out) if out.exists() else None,
                       status="SUCCESS" if len(rows) == 7 and all(
                           r["status"] == "SUCCESS" for r in rows) else "FAILED")
        write(state_path, state)
        if receipt["returncode"] != 0 or receipt["status"] != "SUCCESS":
            raise RuntimeError("Incomplete seven-grind group; no retry or target exclusions")
        return np.array([r["EY_pp"] for r in rows])

    try:
        ds0 = method["printed_D_S_m2_s"]
        # All seven ordinary calls are completed and retained before any fitting.
        baseline = group("A-ordinary", ds0, method["base"], override=False)
        state["baseline_frozen_sha256"] = sha(private / "A-ordinary.json")
        historical = np.array(config["retained_baseline_EY_pp"])
        state["historical_parity_max_pp"] = float(np.max(abs(baseline - historical)))
        if state["historical_parity_max_pp"] > 1e-7:
            raise RuntimeError("Ordinary baseline does not reproduce the retained source contract")
        write(state_path, state)

        def objective(log_factor):
            if len(state["evaluations"]) >= 15:
                raise RuntimeError("Objective evaluation limit exhausted")
            number = len(state["evaluations"]) + 1
            ds = ds0 * 10.**float(log_factor)
            prediction = group(f"D-eval-{number:02}", ds, method["base"])
            loss = float(np.sum((prediction - y)**2))
            state["evaluations"].append(dict(evaluation=number, log10_factor=float(log_factor),
                D_S_m2_s=ds, objective_SSE_pp2=loss, RMSE_pp=float(np.sqrt(loss / 7)),
                predictions_EY_pp=prediction.tolist()))
            write(state_path, state)
            return loss

        objective(0.)
        state["override_parity_max_pp"] = float(np.max(abs(
            np.array(state["evaluations"][0]["predictions_EY_pp"]) - baseline)))
        if state["override_parity_max_pp"] > 1e-10:
            raise RuntimeError("Isolated printed-D_S override fails ordinary-call parity")
        objective(-1.)
        objective(1.)
        optimum = minimize_scalar(objective, bounds=(-1., 1.), method="bounded",
            options={"maxiter": 12, "xatol": method["log10_factor_xatol"]})
        state["optimizer"] = dict(method="scipy.optimize.minimize_scalar/bounded",
            success=bool(optimum.success), message=str(optimum.message), nfev=int(optimum.nfev),
            x=float(optimum.x), fun=float(optimum.fun))
        best = min(state["evaluations"], key=lambda r: r["objective_SSE_pp2"])
        state["selected"] = best
        state["boundary_selected"] = abs(best["log10_factor"]) == 1.
        write(state_path, state)
        group("A-refinement", ds0, method["refinement"])
        group("D-refinement", best["D_S_m2_s"], method["refinement"])
        state["status"] = "COMPLETED"
    except Exception as error:
        state.update(status="BLOCKED", blocker=type(error).__name__ + ": " + str(error))
        raise
    finally:
        state["elapsed_model_s"] = time.monotonic() - start
        write(state_path, state)
    print(json.dumps({k: state[k] for k in
                      ("status", "integrations", "elapsed_model_s", "boundary_selected")}))


def metrics(prediction, target):
    import numpy as np
    residual = np.asarray(prediction) - target
    return dict(MAE_pp=float(np.mean(abs(residual))),
                RMSE_pp=float(np.sqrt(np.mean(residual**2))),
                max_absolute_error_pp=float(np.max(abs(residual))),
                signed_residuals_pp=residual.tolist())


def band(g, low=.10, high=.25):
    return "worse" if g < 0 else "small" if g < low else "moderate" if g < high else "large"


def bands(interval, low, high):
    lo, hi = interval
    return [b for b in ("worse", "small", "moderate", "large") if b in {
        band(x, low, high) for x in (lo, hi, 0., low, high) if lo <= x <= hi}]


def score(private, output):
    """Deterministic reductions of frozen executions; no model or refit calls."""
    import numpy as np
    state = read(private / "run_state.json")
    if state["status"] != "COMPLETED":
        raise ValueError("No valid complete comparison to score")
    config = read(private / "frozen_inputs.json")
    if sha(MODEL) != config["model_sha256"] or sha(__file__) != config["runner_sha256"]:
        raise ValueError("Model/runner identity changed")
    if sha(BUNDLE / "TARGETS.csv") != config["targets_sha256"]:
        raise ValueError("Target identity changed")
    groups = {r["label"]: r for r in state["groups"]}
    for label, group in groups.items():
        if sha(private / f"{label}.json") != group["output_sha256"]:
            raise ValueError("Retained execution identity changed")
    def prediction(label):
        return np.array([r["EY_pp"] for r in groups[label]["rows"]])
    records = targets()
    y = np.array([float(r["theory_EY_pp"]) for r in records])
    exp = np.array([float(r["experiment_mean_EY_pp"]) for r in records])
    y_other = np.array([float(r["retained_second_reader_theory_EY_pp"]) for r in records])
    allowance = np.array([float(r["reading_allowance_pp"]) for r in records])
    ceiling = config["inventory"]["ceiling_EY_pp"]
    flat = float(np.clip(np.mean(y), 0., ceiling))
    pred = {"A": prediction("A-ordinary"),
            "D": np.array(state["selected"]["predictions_EY_pp"]),
            "B": np.full(7, flat)}
    refined = {"A": prediction("A-refinement"), "D": prediction("D-refinement"),
               "B": pred["B"]}
    delta = {arm: abs(refined[arm] - pred[arm]) for arm in pred}

    def loss_interval(arm, reading, numerical):
        # Simultaneous outer envelope; no probability or independence assumption.
        magnitude = abs(pred[arm] - y)
        radius = (allowance if reading else 0.) + (delta[arm] if numerical else 0.)
        return [float(np.sqrt(np.mean(np.maximum(magnitude - radius, 0.)**2))),
                float(np.sqrt(np.mean((magnitude + radius)**2)))]

    primary, secondary = {}, {}
    for arm in pred:
        primary[arm] = dict(metrics(pred[arm], y), fitted_parameters=0 if arm == "A" else 1,
            graphical_RMSE_outer_pp=loss_interval(arm, True, False),
            numerical_RMSE_outer_pp=loss_interval(arm, False, True),
            combined_RMSE_outer_pp=loss_interval(arm, True, True),
            common_reading_offset_RMSE_pp={str(s): metrics(pred[arm], y + s)["RMSE_pp"]
                                         for s in (-.03, 0., .03)},
            retained_second_reader=metrics(pred[arm], y_other),
            refined=metrics(refined[arm], y),
            numerical_delta_EY_pp=delta[arm].tolist(),
            max_numerical_delta_pp=float(max(delta[arm])),
            numerical_target_compliant=bool(max(delta[arm]) <= .05),
            statistical_CI="NOT_APPLICABLE_FIXED_THEORETICAL_CURVE")
        secondary[arm] = dict(metrics(pred[arm], exp), CI="NOT_ESTIMABLE",
            by_regime={regime: metrics(pred[arm][mask], exp[mask]) for regime, mask in
                       [("partially_clogged", np.array(GRINDS) < 1.7),
                        ("standard_flow", np.array(GRINDS) >= 1.7)]})
    gains, classifications = {}, []
    for reference in ("A", "B"):
        name = "D_vs_" + reference
        value = 1 - primary["D"]["RMSE_pp"] / primary[reference]["RMSE_pp"]
        gain = {"g": value, "absolute_RMSE_reduction_pp":
                primary[reference]["RMSE_pp"] - primary["D"]["RMSE_pp"]}
        for kind in ("graphical", "numerical", "combined"):
            d = primary["D"][kind + "_RMSE_outer_pp"]
            r = primary[reference][kind + "_RMSE_outer_pp"]
            gain[kind + "_outer_g"] = [1 - d[1] / r[0], 1 - d[0] / r[1]]
        gain["coherent_refinement_g"] = 1 - primary["D"]["refined"]["RMSE_pp"] / primary[
            reference]["refined"]["RMSE_pp"]
        gain["coherent_common_reading_g"] = {str(s): 1 - primary["D"][
            "common_reading_offset_RMSE_pp"][str(s)] / primary[reference][
            "common_reading_offset_RMSE_pp"][str(s)] for s in (-.03, 0., .03)}
        gain["examined_sensitivity_preserves_advantage"] = gain["combined_outer_g"][0] > 0
        gains[name] = gain
        for f1, f2 in itertools.product((.75, 1., 1.25), repeat=2):
            low, high = .10 * f1, .25 * f2
            classifications.append(dict(comparison=name, lower_boundary=low, upper_boundary=high,
                point_band=band(value, low, high), graphical_bands=bands(
                    gain["graphical_outer_g"], low, high), numerical_bands=bands(
                    gain["numerical_outer_g"], low, high), combined_bands=bands(
                    gain["combined_outer_g"], low, high)))
    point_rows = []
    for i, row in enumerate(records):
        record = dict(row)
        record.update(inventory_ceiling_EY_pp=ceiling,
                      target_interval_wholly_above_ceiling=bool(y[i] - allowance[i] > ceiling),
                      theory_reading_lower_EY_pp=float(y[i] - allowance[i]),
                      theory_reading_upper_EY_pp=float(y[i] + allowance[i]),
                      experimental_mean_reading_lower_EY_pp=float(exp[i] - allowance[i]),
                      experimental_mean_reading_upper_EY_pp=float(exp[i] + allowance[i]),
                      experimental_SD_lower_extent_EY_pp=(float(exp[i]) - float(row["sd_lower_pp"])
                          if row["sd_lower_pp"] else None),
                      experimental_SD_upper_extent_EY_pp=(float(exp[i]) + float(row["sd_upper_pp"])
                          if row["sd_upper_pp"] else None))
        for arm in pred:
            record.update({arm + "_EY_pp": float(pred[arm][i]),
                           arm + "_theory_signed_residual_pp": float(pred[arm][i] - y[i]),
                           arm + "_experimental_signed_residual_pp": float(pred[arm][i] - exp[i]),
                           arm + "_numerical_delta_pp": float(delta[arm][i])})
        point_rows.append(record)
    config.update(status="SCORED_EXPOSED_IN_SAMPLE_RECONSTRUCTION", primary=primary,
        secondary=secondary, gains=gains, band_sensitivity=classifications,
        constant_control=dict(constrained_EY_pp=flat, unrestricted_target_mean_EY_pp=float(np.mean(y)),
            bound_active=flat != float(np.mean(y)),
            unrestricted_diagnostic=metrics(np.full(7, np.mean(y)), y)),
        reporting_diagnostic=dict(factor=1 / .8272**2,
            definition="A physical EY multiplied algebraically by phi_s^-2; unchanged cup output; not a physical prediction or fitted correction",
            predictions_EY_pp=(pred["A"] / .8272**2).tolist(),
            scores=metrics(pred["A"] / .8272**2, y)),
        execution=state,
        intervals_wholly_above_inventory=[GRINDS[i] for i in range(7)
                                          if y[i] - allowance[i] > ceiling])
    output.mkdir(parents=True, exist_ok=True)
    write(output / "RESULTS.json", config)
    csv_write(output / "PREDICTIONS.csv", point_rows)
    csv_write(output / "SCORES.csv", [dict(target=target, arm=arm,
        fitted_parameters=0 if arm == "A" else 1,
        **{k: results[arm][k] for k in ("MAE_pp", "RMSE_pp", "max_absolute_error_pp")})
        for target, results in (("theoretical_curve", primary), ("experimental_means", secondary))
        for arm in pred])
    csv_write(output / "FIT_EVALUATIONS.csv", [{k: v for k, v in r.items()
        if k != "predictions_EY_pp"} for r in state["evaluations"]])
    print(json.dumps(dict(scores={a: primary[a]["RMSE_pp"] for a in pred}, gains=gains)))


def figure(output):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from puckworks.viz.spec import Producer, VizSpec

    data = read(output / "RESULTS.json")
    rows = targets()
    x = np.array(GRINDS)
    y = np.array([float(r["theory_EY_pp"]) for r in rows])
    exp = np.array([float(r["experiment_mean_EY_pp"]) for r in rows])
    spec = VizSpec(id="sci-md-cameron-ds-baseline-001", title="Cameron Figure 5 reconstruction",
        class_=1, producer=Producer("tools.cameron_ds_baseline", "frozen_reconstruction", {}),
        badge="PREDICTED", evidence_strength="post-fit reconstruction",
        fidelity_ceiling="Exposed in-sample published-curve reconstruction; author generating configuration unresolved; not physical validation.",
        render_fn="tools.cameron_ds_baseline:figure", components=[],
        caption="Published curve and experimental means are different targets. Reading allowances are not experimental CIs.",
        outputs=["comparison.png"])
    errors = spec.validate()
    if errors:
        raise ValueError(str(errors))
    fig, axes = plt.subplots(2, 1, figsize=(9, 7), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})
    ax, residual = axes
    ax.plot(x, y, "ko-", label="Published homogeneous curve")
    ax.fill_between(x, y - .03, y + .03, color="black", alpha=.15)
    for arm, color, label in [("A", "#ba392c", "A: conserved baseline"),
                              ("D", "#007a78", "D: one fitted diffusivity"),
                              ("B", "#686868", "B: one fitted constant")]:
        e = np.array(data["primary"][arm]["signed_residuals_pp"])
        ax.plot(x, y + e, marker="s", color=color, label=label)
        residual.plot(x, e, marker="s", color=color, label=arm)
    for mask, color, label in [(x < 1.7, "#d17c22", "Experimental mean: partially clogged"),
                               (x >= 1.7, "#4477aa", "Experimental mean: standard flow")]:
        ax.scatter(x[mask], exp[mask], facecolors="white", edgecolors=color, marker="D",
                   zorder=5, label=label)
    for i, row in enumerate(rows):
        for key, sign in (("sd_lower_pp", -1), ("sd_upper_pp", 1)):
            if row[key]:
                end = exp[i] + sign * float(row[key])
                ax.plot([x[i], x[i]], [exp[i], end], color="#556677", lw=1)
                ax.plot([x[i] - .012, x[i] + .012], [end, end], color="#556677", lw=1)
    ax.axhline(data["inventory"]["ceiling_EY_pp"], color="#999999", linestyle=":",
               label="Fixed initial-inventory ceiling")
    residual.plot(x, data["reporting_diagnostic"]["scores"]["signed_residuals_pp"],
                  "--", color="#9966aa", label="A × phi_s^-2: reporting diagnostic only")
    residual.axhline(0, color="black", lw=.7)
    residual.legend(fontsize=8, ncol=2, loc="lower right")
    ax.legend(fontsize=8, ncol=2, loc="lower left")
    ax.set_ylabel("EY (% of declared dry dose)")
    residual.set_ylabel("Error vs curve (EY pp)")
    residual.set_xlabel("Source grinder setting")
    residual.set_xticks(x)
    ax.set_title("Exposed, in-sample Figure 5 reconstruction")
    fig.text(.5, .012, "Curve reading allowance ±0.03 pp; visible experimental bars are SD, not CIs.\n"
             "Obscured SD extents remain unknown. No physical validation or author-configuration claim.",
             ha="center", fontsize=8)
    fig.tight_layout(rect=(0, .065, 1, 1))
    fig.savefig(output / "comparison.png", dpi=160)
    plt.close(fig)
    data["figure"] = spec.to_dict()
    write(output / "RESULTS.json", data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "worker", "score", "figure"))
    parser.add_argument("--private", type=Path,
        default=Path.home() / ".local/share/puckworks/sci-md-cameron-ds-baseline-001/model")
    parser.add_argument("--request", type=Path)
    parser.add_argument("--output", type=Path, default=BUNDLE)
    args = parser.parse_args()
    if args.command == "worker":
        return worker(args)
    if args.command == "run":
        run(args.private)
    elif args.command == "figure":
        figure(args.output)
    else:
        score(args.private, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

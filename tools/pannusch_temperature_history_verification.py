"""Bounded synthetic qualification; separate execution and saved-evidence reporting.

Run as `python -m tools.pannusch_temperature_history_verification --help`.
Full arrays/logs remain external. Source-derived reports retain Pannusch et al.
attribution and CC-BY-NC-3.0 treatment; they are not physical validation.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.integrate import cumulative_simpson

from puckworks.models.pannusch2024 import solver as ps, closures as pc
from puckworks.models.pannusch2024 import temperature_history as th
from tools import pannusch_temperature_history_reference as ref

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/"docs/analysis/model_pannusch2024_temp_history_001"
RIGHTS = "Pannusch et al.; DOI 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived report; software licensing separate"


def read_json(path):
    def invalid(value):
        raise ValueError("nonfinite JSON constant: "+value)
    return json.loads(Path(path).read_text(), parse_constant=invalid)


def write_json(path, obj):
    path = Path(path)
    tmp = path.with_suffix(path.suffix+".tmp")
    tmp.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+"\n")
    os.replace(tmp, path)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, allow_nan=False).encode()).hexdigest()


def observations():
    return np.unique(np.r_[np.arange(2401)*.0125, 7-1e-8, 7+1e-8, 19-1e-8, 19+1e-8])


def numerical_identities(case):
    names = ["puckworks/models/pannusch2024/solver.py", "puckworks/models/pannusch2024/closures.py",
             "puckworks/data/pannusch2024/table2_fitted_params.csv",
             "puckworks/data/pannusch2024/table2_grind_psi_ds2.csv"]
    if case["method"] == "BDF":
        names.append("puckworks/models/pannusch2024/temperature_history.py")
    if case["method"] in ("expm", "Radau"):
        names.append("tools/pannusch_temperature_history_reference.py")
    names.extend(["docs/analysis/model_pannusch2024_temp_history_001/CASES.json",
                  "docs/analysis/model_pannusch2024_temp_history_001/CONTRACT.md"])
    return {name: digest(ROOT/name) for name in names}


def reduced(trajectory):
    return np.column_stack((trajectory.liquid_kg_m3[:, 1:], trajectory.fine_kg_m3,
                            trajectory.coarse_kg_m3, trajectory.outlet_solute_kg))


def worker(case_id, directory, execution_id):
    """One species/history/grid/settings/method; hard wall timer is process-local."""
    ledger = read_json(Path(directory)/"executions.json")
    entry = next((e for e in ledger if e["execution_id"] == execution_id), None)
    if entry is None or entry["status"] != "LAUNCHED" or entry["case_id"] != case_id:
        raise ValueError("worker requires its reserved launch receipt")
    with (Path(directory)/(execution_id+".claim")).open("x") as claim:
        claim.write(case_id+"\n")
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall ceiling")))
    signal.setitimer(signal.ITIMER_REAL, 58.)
    contract = read_json(BUNDLE/"CASES.json")
    case = next(c for c in contract["cases"] if c["id"] == case_id)
    if entry["numerical_identities"] != numerical_identities(case):
        raise ValueError("numerical source changed after launch reservation")
    Q, tspan, grind, solute, n = contract["Q_m3_s"], contract["span_s"], contract["grind"], case["solute"], case["nz"]
    times, bounds = observations(), np.asarray(contract["fraction_bounds_s"])
    meta = {"case": case, "case_sha256": canonical_hash(case),
            "numerical_identities": numerical_identities(case),
            "execution_id": execution_id, "source_commit": subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "runner_sha256": digest(__file__), "requested_span_s": tspan,
            "flow_m3_s": Q, "grind": grind, "fraction_bounds_s": bounds.tolist(),
            "observation_sha256": hashlib.sha256(times.tobytes()).hexdigest(),
            "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
            "rights": RIGHTS, "PHYSICAL_VALIDATION": "NOT_ESTABLISHED"}
    arrays = {}
    start = time.monotonic()
    method = case["method"]
    if method == "legacy":
        sp = ps._solute_params()[solute]
        legacy_argument = 1.96
        assert legacy_argument/1000.0/980.0 == Q
        fractions = ps.simulate_fractions(88., legacy_argument, bounds, sp, sp["c_s0"], ps.GRINDS[grind])
        arrays["fractions"] = fractions
        complete = len(fractions) == len(bounds)-1 and np.isfinite(fractions).all() and bool(ps.LAST_SOLVE.get("success"))
        # Legacy API diagnostics concern its output times, not accepted internal steps.
        meta.update(status="COMPLETE" if complete else "FAILED", actual_span_s=tspan if complete else None,
                    legacy_argument=legacy_argument, legacy_cl1=sp["c_s0"],
                    legacy_output_time_diagnostics=dict(ps.LAST_SOLVE), segment_count=1,
                    physical_trajectory="UNAVAILABLE_FROM_UNCHANGED_LEGACY_API")
    elif method == "BDF":
        rtol, atol, step = contract["levels"][case["level"]]
        history = th.TemperatureHistory(case["times_s"], tuple(t+273.15 for t in case["temperatures_C"]), case["history_kind"])
        result = th.simulate_temperature_history(
            history, flow_m3_s=Q, t_span_s=tspan, solute=solute, grind=grind,
            observation_times_s=times, fraction_bounds_s=bounds,
            settings=th.TemperatureHistorySettings(nz=n, rtol=rtol, normalized_atol=atol,
                                                  max_step_s=step, wall_time_limit_s=55.))
        meta.update(json.loads(result.to_json(include_trajectories=False)))
        meta["segment_count"] = len(result.segments)
        arrays.update(times=result.observations.times_s, states=reduced(result.observations),
                      volume=result.observations.hydraulic_volume_m3,
                      diagnostic_times=result.checked_trajectory.times_s,
                      diagnostic_states=reduced(result.checked_trajectory))
        if all(f.concentration_kg_m3 is not None for f in result.fractions):
            arrays["fractions"] = np.array([f.concentration_kg_m3 for f in result.fractions])
        complete = result.status == "COMPLETE"
    else:
        temperatures = np.array(case["temperatures_C"])+273.15
        if method == "expm":
            states, diagnostics = ref.ordered_exponential(case["times_s"], temperatures, Q, solute, grind, n, times)
            checked_t, checked_y = times, states
        else:
            rtol, atol, step = contract["levels"]["radau"]
            states, diagnostics, checked_t, checked_y = ref.independent_radau(
                case["times_s"], temperatures, Q, solute, grind, n, times, rtol, atol, step)
        at_bounds = states[np.searchsorted(times, bounds), -1]
        fractions = np.diff(at_bounds)/(Q*np.diff(bounds))
        arrays.update(times=times, states=states, volume=Q*(times-tspan[0]), fractions=fractions,
                      diagnostic_times=checked_t, diagnostic_states=checked_y)
        complete = bool(all(np.isfinite(a).all() for a in arrays.values()))
        meta.update(status="COMPLETE" if complete else "FAILED", actual_span_s=tspan,
                    segment_count=len(diagnostics), segments=diagnostics,
                    reference_shared_machinery="unchanged closures, parameter table, geometry, verified source stencil")
    meta["numerical_wall_s"] = time.monotonic()-start
    target = Path(directory)/execution_id
    np.savez_compressed(str(target)+".npz", **arrays)
    meta["arrays_sha256"] = digest(str(target)+".npz")
    write_json(str(target)+".json", meta)
    signal.setitimer(signal.ITIMER_REAL, 0.)
    return 0 if complete else 2


def used_resources(ledger):
    # An interrupted launch cannot disappear or regain its allocation.
    return len(ledger), sum(e.get("charged_wall_s", e["timeout_s"]) for e in ledger)


def execute(directory, case_id=None, correction=False):
    directory = Path(directory).resolve()
    if directory == ROOT or ROOT in directory.parents:
        raise ValueError("full evidence must be outside the repository")
    directory.mkdir(parents=True, exist_ok=True)
    contract = read_json(BUNDLE/"CASES.json")
    with (directory/"execution.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        ledger_path = directory/"executions.json"
        ledger = read_json(ledger_path) if ledger_path.exists() else []
        if case_id and case_id not in {c["id"] for c in contract["cases"]}:
            raise ValueError("unknown frozen case")
        if correction and not case_id:
            raise ValueError("a correction must name one affected case")
        selected = [c for c in contract["cases"] if not case_id or c["id"] == case_id]
        if not case_id:
            attempted = {e["case_id"] for e in ledger}
            selected = [c for c in selected if c["id"] not in attempted]
        for case in selected:
            count, elapsed = used_resources(ledger)
            ceiling = 32 if correction else 28
            if count >= ceiling or elapsed >= 1800:
                raise RuntimeError("execution/time ceiling reached; retain INCOMPLETE qualification")
            if count == 27 and not case_id:
                raise RuntimeError("slot 28 requires an explicit named review replay")
            limit = min(60., 1800-elapsed-.5)
            if limit < .1:
                raise RuntimeError("insufficient remaining numerical wall budget")
            eid = f"exec-{count+1:03d}"
            entry = {"execution_id": eid, "case_id": case["id"], "status": "LAUNCHED",
                     "timeout_s": limit, "allocation": "CORRECTION" if correction else "PLANNED_OR_NAMED_REPLAY",
                     "numerical_identities": numerical_identities(case)}
            ledger.append(entry)
            write_json(ledger_path, ledger)  # durable before launch
            began = time.monotonic()
            try:
                env = dict(os.environ, OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
                with (directory/(eid+".log")).open("w") as log:
                    proc = subprocess.run([sys.executable, "-m", "tools.pannusch_temperature_history_verification",
                                           "worker", "--case-id", case["id"], "--evidence-dir", str(directory),
                                           "--execution-id", eid], cwd=ROOT, env=env, stdout=log,
                                          stderr=subprocess.STDOUT, timeout=limit, check=False)
                entry["status"] = "COMPLETE" if proc.returncode == 0 else "FAILED"
                entry["returncode"] = proc.returncode
            except subprocess.TimeoutExpired:
                entry["status"] = "TIMEOUT"
            except BaseException:
                entry["status"] = "CANCELLED"
                raise
            finally:
                entry["charged_wall_s"] = time.monotonic()-began
                receipt = directory/(eid+".json")
                if receipt.exists():
                    entry["receipt_sha256"] = digest(receipt)
                    entry["segment_count"] = read_json(receipt).get("segment_count", 0)
                write_json(ledger_path, ledger)
                print(eid, case["id"], entry["status"], round(entry["charged_wall_s"], 3), "s", flush=True)


def compatible_numerical_identities(saved, current):
    """One hash-bound input-rejection correction; never a general stale-source waiver."""
    if saved == current:
        return True
    proof = read_json(BUNDLE/"VALIDATION_CORRECTION.json")
    name = proof["module"]
    if saved.get(name) != proof["original_sha256"] or current.get(name) != proof["corrected_sha256"]:
        return False
    corrected = dict(saved)
    corrected[name] = proof["corrected_sha256"]
    return corrected == current


def load_evidence(directory, case, ledger):
    entries = [e for e in ledger if e["case_id"] == case["id"]]
    if not entries:
        raise ValueError("UNRUN")
    entry = entries[-1]
    if entry["status"] != "COMPLETE":
        raise ValueError("LATEST_EXECUTION_"+entry["status"])
    base = Path(directory)/entry["execution_id"]
    path = Path(str(base)+".json")
    if digest(path) != entry.get("receipt_sha256"):
        raise ValueError("RECEIPT_HASH_MISMATCH")
    meta = read_json(path)
    if meta["status"] != "COMPLETE" or meta["case"] != case or meta["case_sha256"] != canonical_hash(case):
        raise ValueError("FAILED_OR_MISMATCHED_RECEIPT")
    if not all(compatible_numerical_identities(saved, numerical_identities(case))
               for saved in (meta["numerical_identities"], entry["numerical_identities"])):
        raise ValueError("NUMERICAL_SOURCE_CHANGED")
    archive = Path(str(base)+".npz")
    if digest(archive) != meta["arrays_sha256"]:
        raise ValueError("ARRAY_HASH_MISMATCH")
    with np.load(archive, allow_pickle=False) as data:
        arrays = {k: data[k] for k in data.files}
    if not all(np.isfinite(a).all() for a in arrays.values()):
        raise ValueError("NONFINITE_EVIDENCE")
    if meta["actual_span_s"] != [0., 30.] or meta["requested_span_s"] != [0., 30.]:
        raise ValueError("PARTIAL_OR_MISMATCHED_SUPPORT")
    if arrays.get("fractions", np.array([])).shape != (7,):
        raise ValueError("INCOMPLETE_FRACTIONS")
    if case["method"] == "BDF":
        if meta.get("integration_complete") is not True:
            raise ValueError("FAILED_INTEGRATION_DESPITE_RECEIPT_STATUS")
        segments = meta["segments"]
        if len(segments) != len(case["times_s"])-1 or any(
                s["status"] != "COMPLETE" or s["actual_span_s"] != s["requested_span_s"] for s in segments):
            raise ValueError("INCOMPLETE_SEGMENT_RECEIPT")
        if any(a["end_state_sha256"] != b["start_state_sha256"] for a, b in zip(segments, segments[1:])):
            raise ValueError("STATE_NOT_CARRIED_AT_KNOT")
    if case["method"] != "legacy":
        times, y = arrays["times"], arrays["states"]
        if not np.array_equal(times, observations()) or y.shape != (len(times), 3*case["nz"]):
            raise ValueError("INCOMPLETE_OR_MISMATCHED_OBSERVATIONS")
        expected = ref.reference_initial(case["temperatures_C"][0]+273.15, case["solute"], case["nz"])
        if not np.allclose(y[0], expected, rtol=0., atol=1e-14):
            raise ValueError("MISMATCHED_INITIAL_STATE")
        dt, dy = arrays["diagnostic_times"], arrays["diagnostic_states"]
        if dt.ndim != 1 or dy.shape != (len(dt), 3*case["nz"]) or dt[0] != 0 or dt[-1] != 30 or np.any(np.diff(dt) <= 0):
            raise ValueError("INVALID_DIAGNOSTIC_SUPPORT")
        if arrays["volume"].shape != times.shape:
            raise ValueError("INVALID_VOLUME_SHAPE")
    return meta, arrays


def budget_metric(values, scale, allowance):
    a = np.asarray(values, dtype=float)/scale
    return {"max_abs_normalized": float(np.max(np.abs(a))),
            "signed_min_normalized": float(np.min(a)), "signed_max_normalized": float(np.max(a)),
            "signed_final_normalized": float(a[-1]), "allowance": allowance,
            "passed": bool(np.max(np.abs(a)) <= allowance)}


def accounting(case, arrays):
    """Independent spatial inventory, temporal flux, and discrete weighted budget."""
    n, Q, grind = case["nz"], 2e-6, 1.7
    solute = case["solute"]
    sp = ps._solute_params()[solute]
    C = sp["c_s0"]
    M = ref.continuum_M0(case["temperatures_C"][0]+273.15, solute, grind)
    psi, d2 = ps.GRINDS[grind]["psi"], ps.GRINDS[grind]["d_s2"]
    a1, a2 = psi*(1-ps.ALPHA_L), (1-psi)*(1-ps.ALPHA_L)
    w = np.full(n, ps.L/(n-1)); w[[0, -1]] *= .5

    def inventory(y):
        cl = np.column_stack((np.zeros(len(y)), y[:, :n-1]))
        return ps.ACS*((ps.ALPHA_L*cl+a1*y[:, n-1:2*n-1]
                        +ps.PHI_V2*a2*y[:, 2*n-1:-1])@w)

    y, diagnostic = arrays["states"], arrays["diagnostic_states"]
    M0h = float(inventory(y[:1])[0])
    inc = inventory(diagnostic)+diagnostic[:, -1]-M0h
    cont = inc+M0h-M
    regular = np.arange(2401)*.0125
    idx = np.searchsorted(arrays["times"], regular)
    g = y[idx]
    cl = np.column_stack((np.zeros(len(g)), g[:, :n-1]))
    flux = Q*cl[:, -1]
    temporal = cumulative_simpson(flux, x=regular, initial=0.)
    coarse_temporal = cumulative_simpson(flux[::2], x=regular[::2], initial=0.)
    volume_quad = cumulative_simpson(np.full(len(regular), Q), x=regular, initial=0.)
    d32 = 6/(psi*6/ps.D1_FINE+(1-psi)*6/d2)
    D = ps.five_point_biased_upwind(n, ps.L/(n-1), Q/ps.ACS)
    transport_rate = Q*(cl[:, -1]-cl@(w[1:]@D[1:, :]))
    transport_cum = cumulative_simpson(transport_rate, x=regular, initial=0.)
    inlet_cum = np.zeros(len(regular))
    # Integrate each coefficient segment with its own endpoint temperature.
    for segment_index, (a, b) in enumerate(zip(case["times_s"][:-1], case["times_s"][1:])):
        ii = np.flatnonzero((regular >= a) & (regular <= b))
        temp = np.full(len(ii), case["temperatures_C"][segment_index]+273.15)
        if case["history_kind"] == "linear":
            temp += (case["temperatures_C"][segment_index+1]-case["temperatures_C"][segment_index])*(regular[ii]-a)/(b-a)
        K = pc.vant_hoff_K(temp, sp["K_ref"], sp["gamma"])
        h1 = pc.sherwood_h(temp, Q/ps.ACS, sp["A1"], sp["B1"], solute, d32)
        h2 = pc.sherwood_h(temp, Q/ps.ACS, sp["A2"], sp["B2"], solute, d32)
        inlet_rate = -ps.ACS*w[0]*K*(a1*6*h1/ps.D1_FINE*g[ii, n-1]
                                      +a2*6*h2/d2*g[ii, 2*n-1])
        inlet_cum[ii] = inlet_cum[ii[0]]+cumulative_simpson(inlet_rate, x=regular[ii], initial=0.)
    expected_inc = transport_cum+inlet_cum
    actual_inc = inventory(g)+g[:, -1]-M0h
    minima = {name: float(np.min(diagnostic[:, lo:hi]))/C for name, lo, hi in (
        ("liquid_interior", 0, n-1), ("fine", n-1, 2*n-1), ("coarse", 2*n-1, 3*n-1))}
    refined = {"dt_0_025_minimum_normalized": float(np.min(g[::2, :-1]))/C,
               "dt_0_0125_minimum_normalized": float(np.min(g[:, :-1]))/C}
    record = {
        "scales": {"C_kg_m3": C, "M_kg": M, "V_m3": Q*30},
        "M0_cont_kg": M, "M0_h_kg": M0h, "initial_quadrature_offset_kg": M0h-M,
        "continuum_residual": budget_metric(cont, M, 5e-3),
        "incremental_discrete_residual": budget_metric(inc, M, 5e-3),
        "independent_flux_quadrature": budget_metric(temporal-g[:, -1], M, 1e-6),
        "flux_quadrature_refinement": budget_metric(coarse_temporal-temporal[::2], M, 1e-6),
        "discrete_budget_quadrature": budget_metric(actual_inc-expected_inc, M, 1e-6),
        "transport_stencil_final_kg": float(transport_cum[-1]),
        "pinned_inlet_exchange_final_kg": float(inlet_cum[-1]),
        "independent_volume_quadrature": budget_metric(volume_quad-arrays["volume"][idx], Q*30, 1e-6),
        "exact_volume_error": budget_metric(arrays["volume"]-Q*(arrays["times"]-0.), Q*30, 1e-6),
        "sampled_minima_normalized": minima, "minimum_sampling_refinement": refined,
        "positivity_allowance": 1e-6, "sampled_positivity_passed": bool(min(minima.values()) >= -1e-6),
        "diagnostic_sample_count": len(diagnostic),
        "diagnostic_support_s": [float(arrays["diagnostic_times"][0]), float(arrays["diagnostic_times"][-1])],
        "min_outlet_mass_increment_kg": float(np.min(np.diff(diagnostic[:, -1]))),
        "sampled_maximum_concentration_normalized": float(np.max(diagnostic[:, :-1]))/C,
    }
    record["passed"] = all(record[k]["passed"] for k in (
        "continuum_residual", "independent_flux_quadrature", "flux_quadrature_refinement",
        "discrete_budget_quadrature", "exact_volume_error", "independent_volume_quadrature")) and record["sampled_positivity_passed"]
    return record


def agreement(a, b, solute, T0_C, allowance=1e-6):
    n = (a["states"].shape[1])//3
    C = ps._solute_params()[solute]["c_s0"]
    M = ref.continuum_M0(T0_C+273.15, solute, 1.7)
    out = {}
    for key, lo, hi in (("liquid", 0, n-1), ("fine", n-1, 2*n-1), ("coarse", 2*n-1, 3*n-1)):
        error = float(np.max(np.abs(a["states"][:, lo:hi]-b["states"][:, lo:hi])))/C
        out[key] = {"max_normalized_error": error, "passed": error <= allowance}
    for key, v1, v2, scale in (("solute", a["states"][:, -1], b["states"][:, -1], M),
                               ("volume", a["volume"], b["volume"], 2e-6*30),
                               ("fraction", a["fractions"], b["fractions"], C)):
        error = float(np.max(np.abs(v1-v2)))/scale
        out[key] = {"max_normalized_error": error, "passed": error <= allowance}
    return {"channels": out, "allowance": allowance,
            "passed": all(v["passed"] for v in out.values())}


def report(directory, output):
    """Read saved arrays only. No solve, retry, extrapolation or silent cache hit."""
    contract = read_json(BUNDLE/"CASES.json")
    directory, output = Path(directory), Path(output)
    ledger = read_json(directory/"executions.json")
    out = {"task": contract["task"], "contract_sha256": digest(BUNDLE/"CONTRACT.md"),
           "cases_sha256": digest(BUNDLE/"CASES.json"), "reporter_sha256": digest(__file__),
           "rights": RIGHTS, "PHYSICAL_VALIDATION": "NOT_ESTABLISHED",
           "cases": {}, "comparisons": {}, "limits": list(th.LIMITATIONS),
           "execution_resources": {"count": used_resources(ledger)[0],
                                   "charged_wall_s": used_resources(ledger)[1],
                                   "remaining_slots": 32-len(ledger),
                                   "remaining_wall_s": 1800-used_resources(ledger)[1],
                                   "segment_integrations": sum(e.get("segment_count", 0) for e in ledger)},
           "execution_ledger": ledger}
    data, metadata = {}, {}
    for case in contract["cases"]:
        key = case["id"]
        try:
            meta, arrays = load_evidence(directory, case, ledger)
            metadata[key], data[key] = meta, arrays
            row = {"status": "COMPLETE", "case": case, "execution_id": meta["execution_id"],
                   "arrays_sha256": meta["arrays_sha256"], "numerical_identities": meta["numerical_identities"],
                   "actual_span_s": meta["actual_span_s"], "segment_count": meta["segment_count"],
                   "versions": meta["versions"], "source_commit": meta["source_commit"],
                   "fraction_concentration_kg_m3": arrays["fractions"].tolist()}
            if case["method"] != "legacy":
                row["accounting"] = accounting(case, arrays)
            if case["method"] == "BDF":
                row["segment_diagnostics"] = meta["segments"]
            if case["method"] == "legacy":
                row["legacy_arithmetic"] = "1.96 / 1000.0 / 980.0 == 2e-6; arithmetic only"
                row["legacy_cl1"] = meta["legacy_cl1"]
            out["cases"][key] = row
        except (ValueError, OSError, KeyError) as exc:
            out["cases"][key] = {"status": "INCOMPLETE", "reason": str(exc), "case": case}
    comparisons = out["comparisons"]
    for s in contract["species"]:
        keys = [f"A.{s}.BDF", f"A.{s}.legacy"]
        if all(k in data for k in keys):
            error = float(np.max(np.abs(data[keys[0]]["fractions"]-data[keys[1]]["fractions"])))/ps._solute_params()[s]["c_s0"]
            comparisons[f"A.{s}.legacy"] = {"max_normalized_fraction_error": error,
                                              "allowance": 1e-4, "passed": error <= 1e-4}
        keys = [f"B.{s}.BDF", f"B.{s}.expm"]
        if all(k in data for k in keys):
            comparisons[f"B.{s}.independent"] = agreement(data[keys[0]], data[keys[1]], s, 88.)
    for direction, T0 in (("rise", 88.), ("fall", 93.)):
        for other in ("coarse", "finer", "radau"):
            ka, kb = f"C.{direction}.fine", f"C.{direction}.{other}"
            if ka in data and kb in data:
                v = agreement(data[ka], data[kb], "caffeine", T0)
                v["gated"] = other != "coarse"
                comparisons[f"C.{direction}.{other}"] = v
    for a, b, label in (("D.rise.100", "C.rise.fine", "100_to_200"),
                         ("C.rise.fine", "D.rise.400", "200_to_400")):
        if a in data and b in data:
            error = float(np.max(np.abs(data[a]["fractions"]-data[b]["fractions"])))/ps._solute_params()["caffeine"]["c_s0"]
            comparisons["D."+label] = {"max_normalized_fraction_error": error, "allowance": 5e-3,
                                        "passed": error <= 5e-3, "gated": label == "200_to_400"}
    ka, kb = "C.rise.fine", "E.repeat.rise.fine"
    if ka in data and kb in data:
        comparisons["E.repeat"] = {"passed": all(np.array_equal(data[ka][k], data[kb][k]) for k in data[ka]),
                                    "comparison": "all retained numerical arrays byte-equivalent"}
    # Derived observers require no additional solve. Their support includes the unobserved prefix.
    delayed = {}
    for key, a in data.items():
        if "times" not in a:
            continue
        t, y = a["times"], a["states"]
        def mass(at):
            j = int(np.searchsorted(t, at))
            if j >= len(t) or t[j] != at:
                raise ValueError("observer lacks exact retained support")
            return float(y[j, -1])
        c2030 = (mass(30)-mass(20))/(2e-6*10)
        whole = (mass(30)-mass(0))/(2e-6*30)
        partition = float(np.sum(a["fractions"]*np.diff(contract["fraction_bounds_s"]))/30)
        error = abs(whole-partition)/ps._solute_params()[out["cases"][key]["case"]["solute"]]["c_s0"]
        delayed[key] = {"model_initial_time_s": 0., "delayed_window_s": [20., 30.],
                        "delayed_fraction_kg_m3": c2030, "mass_at_20_s_kg": mass(20),
                        "knot_window_7_19_kg_m3": (mass(19)-mass(7))/(2e-6*12),
                        "partition_error_normalized": error, "passed": error <= 1e-12 and mass(20) > 0}
    out["derived_observers"] = delayed
    expected_comparisons = 17  # 4 A + 4 B + 6 C (2 diagnostic only) + 2 D + 1 E
    complete = all(r["status"] == "COMPLETE" for r in out["cases"].values())
    account_pass = complete and all(r.get("accounting", {"passed": True})["passed"] for r in out["cases"].values())
    comparison_pass = len(comparisons) == expected_comparisons and all(
        v["passed"] for v in comparisons.values() if v.get("gated", True))
    out["resource_ceiling_passed"] = len(ledger) <= 32 and used_resources(ledger)[1] <= 1800
    out["units_and_bases"] = dict(th.BASES)
    out["numerical_disposition"] = "VERIFIED" if out["resource_ceiling_passed"] and complete and account_pass and comparison_pass and all(
        v["passed"] for v in delayed.values()) else "INCOMPLETE"
    out["capability_qualification"] = ("INCOMPLETE_NUMERICAL_GATES_FAILED_OR_UNRUN"
                                        if out["numerical_disposition"] == "INCOMPLETE"
                                        else "INCOMPLETE_PENDING_SOFTWARE_QA_HOSTED_CI_AND_INDEPENDENT_REVIEW")
    out["separate_dispositions"] = {
        "constant_compatibility": "PASS" if all(comparisons.get(f"A.{s}.legacy", {}).get("passed", False) for s in contract["species"]) else "INCOMPLETE",
        "temporal_and_independent": "PASS" if all(comparisons.get(k, {}).get("passed", False) for k in (
            [f"B.{s}.independent" for s in contract["species"]]+[f"C.{d}.{m}" for d in ("rise", "fall") for m in ("finer", "radau")])) else "INCOMPLETE",
        "spatial_accounting_positivity": "PASS" if account_pass and comparisons.get("D.200_to_400", {}).get("passed", False) else "INCOMPLETE",
        "software_qa_hosted_ci_independent_review": "SEPARATE_HANDOFF_RECEIPTS_REQUIRED"}
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/"RESULTS.json", out)
    print(out["numerical_disposition"], "saved-evidence report;", len(ledger), "executions")
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for name in ("execute", "worker", "report"):
        sub = subs.add_parser(name)
        sub.add_argument("--evidence-dir", type=Path, required=True)
        if name != "report":
            sub.add_argument("--case-id", required=name == "worker")
        if name == "execute":
            sub.add_argument("--correction", action="store_true")
        if name == "worker":
            sub.add_argument("--execution-id", required=True)
        if name == "report":
            sub.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.command == "worker":
        return worker(args.case_id, args.evidence_dir, args.execution_id)
    if args.command == "execute":
        execute(args.evidence_dir, args.case_id, args.correction)
    else:
        report(args.evidence_dir, args.output_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

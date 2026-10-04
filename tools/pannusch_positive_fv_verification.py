"""002 bounded qualification. Execute once/resume; report only reduces saved evidence.

Large arrays/logs and the task-wide resource authority remain outside Git.
Source-derived reports: Pannusch et al., DOI 10.17632/y2tz67f6ry.1, CC-BY-NC-3.0.
"""
from __future__ import annotations

import os
# One numerical worker and one BLAS thread, including report reductions.
for _thread_variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import inspect
import json
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

import numpy as np
import scipy
from puckworks.models.pannusch2024 import temperature_history_fv as fv, solver as ps
from tools import pannusch_positive_fv_reference as ref
from tools.pannusch_temperature_history_verification import read_json, write_json, digest, canonical_hash

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/"docs/analysis/model_pannusch2024_positive_fv_002"
TASK = "MODEL-PANNUSCH2024-POSITIVE-FV-002"
PARENT = "c7310ea1ac6c41ec2cb8f918584ab41cb485fa60"
RIGHTS = "Pannusch et al., DOI 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived outputs; first-party software licensing separate"


def observations(contract):
    return np.unique(np.r_[np.arange(2401)*.0125, 7-1e-8, 7+1e-8, 19-1e-8, 19+1e-8,
                           contract["early_times_s"]])


def identities():
    paths = ["puckworks/models/pannusch2024/temperature_history_fv.py",
             "puckworks/models/pannusch2024/temperature_history.py",
             "puckworks/models/pannusch2024/solver.py", "puckworks/models/pannusch2024/closures.py",
             "puckworks/data/pannusch2024/table2_fitted_params.csv", "puckworks/data/pannusch2024/table2_grind_psi_ds2.csv",
             "tools/pannusch_positive_fv_reference.py",
             "docs/analysis/model_pannusch2024_positive_fv_002/CONTRACT.md",
             "docs/analysis/model_pannusch2024_positive_fv_002/CASES.json"]
    result = {p: digest(ROOT/p) for p in paths}
    blocks = (observations, _fields, _PassiveSystem, case_inputs, worker, execute, reserve, charged, used)
    result["numerical_worker_and_resource_blocks"] = hashlib.sha256(
        "\n".join(inspect.getsource(f) for f in blocks).encode()).hexdigest()
    return result


def authority_path():
    common = Path(subprocess.check_output(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, text=True).strip())
    if not common.is_absolute():
        common = ROOT/common
    return common/"qualification-budgets"/(TASK+".json")


def charged(entry):
    return float(entry.get("charged_wall_s", entry["reserved_wall_s"]))


def used(ledger):
    return sum(charged(e) for e in ledger["executions"]+ledger["auxiliary"])


@contextmanager
def locked_authority(directory):
    directory = Path(directory).resolve()
    path = authority_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix(".lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            ledger = read_json(path)
            if ledger["evidence_directory"] != str(directory):
                raise RuntimeError("TASK_BUDGET_ALREADY_BOUND_TO_DIFFERENT_DIRECTORY")
        else:
            ledger = dict(task=TASK, evidence_directory=str(directory), executions=[], auxiliary=[])
            directory.mkdir(parents=True, exist_ok=True)
            write_json(path, ledger)
        yield path, ledger


def reserve(ledger, *, auxiliary=False, correction=False):
    count = len(ledger["executions"])
    if not auxiliary and count >= (32 if correction else 28):
        raise RuntimeError("EXECUTION_CEILING_OR_FOUR_SLOT_RESERVE")
    remaining = 1800.-used(ledger)
    if remaining <= 0.1:
        raise RuntimeError("AGGREGATE_NUMERICAL_TIME_EXHAUSTED")
    return min(120., remaining)


def _fields(trajectory):
    return np.column_stack((trajectory.liquid_cell_average_kg_m3,
                            trajectory.fine_cell_average_kg_m3,
                            trajectory.coarse_cell_average_kg_m3, trajectory.outlet_solute_kg))


class _PassiveSystem(fv._System):
    """Test-only initial condition/rates; never a public alternate-physics mode."""
    def __init__(self, n, Q):
        super().__init__("caffeine", 1.7, Q, n)
        self.Cstar = 1.

    def generator(self, T):
        return fv._mass_generator(self.n, self.Q/(self.W*ps.ALPHA_L), 0., 0., 0., 0.)

    def initial(self, T):
        avg, _, _ = ref.passive_exact(self.n, [0], self.Q, self.Cstar)
        return np.r_[self.capacities[:self.n]*avg[0], np.zeros(2*self.n+1)]

    def M0(self, T):
        return ps.ACS*ps.ALPHA_L*self.Cstar*ps.L/2


def case_inputs(case, contract):
    passive = case["method"] == "PASSIVE"
    span = case["times_s"][::len(case["times_s"])-1]
    history = fv.TemperatureHistory(case["times_s"], tuple(t+273.15 for t in case["temperatures_C"]), case["history_kind"])
    times = (np.array(contract["passive"]["times_over_residence"])*contract["passive"]["residence_time_s"]
             if passive else observations(contract))
    bounds = np.array([] if passive else contract["fraction_bounds_s"])
    return passive, span, history, times, bounds


def worker(directory, case_id, execution_id):
    directory = Path(directory)
    ledger = read_json(directory/"executions.json")
    entry = next((e for e in ledger if e["execution_id"] == execution_id), None)
    if entry is None or entry["status"] != "LAUNCHED" or entry["case_id"] != case_id:
        raise RuntimeError("UNRESERVED_WORKER")
    with (directory/(execution_id+".claim")).open("x") as claim:
        claim.write(case_id+"\n")
    if entry["identities"] != identities():
        raise RuntimeError("SOURCE_CHANGED_AFTER_RESERVATION")
    limit = max(.01, entry["reserved_wall_s"]-1.)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("NUMERICAL_WALL_CEILING")))
    signal.setitimer(signal.ITIMER_REAL, limit)
    contract = read_json(BUNDLE/"CASES.json")
    case = next(c for c in contract["cases"] if c["id"] == case_id)
    passive, span, history, times, bounds = case_inputs(case, contract)
    Q, n, solute, grind = contract["Q_m3_s"], case["cells"], case["solute"], contract["grind"]
    meta = dict(task=TASK, case=case, case_sha256=canonical_hash(case), execution_id=execution_id,
                source_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                identities=identities(), runner_file_sha256=digest(__file__), requested_span_s=span, Q_m3_s=Q, grind=grind,
                history=fv.th._json_value(history), fraction_bounds_s=bounds.tolist(),
                versions=dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__),
                observation_sha256=hashlib.sha256(times.tobytes()).hexdigest(), rights=RIGHTS,
                PHYSICAL_VALIDATION="NOT_ESTABLISHED")
    start = time.monotonic()
    arrays = {}
    try:
        if case["method"] in ("FV", "PASSIVE"):
            settings = fv.FVSettings(cells=n, h_max_s=case["h_max_s"], wall_time_limit_s=max(.001, limit-10))
            if passive:
                system = _PassiveSystem(n, Q)
                result = fv._evolve(system, history, span, tuple(times), (), settings)
                meta.update({k: v for k, v in result.items() if k not in ("observations", "checked_trajectory", "trace", "quadrature", "fractions")})
                tr, checked, trace, quad = [result[k] for k in ("observations", "checked_trajectory", "trace", "quadrature")]
                meta.update(Cstar=1., capacities=system.capacities.reshape(3, n)[:, 0].tolist(), settings=fv.th._json_value(settings), test_only=True)
                fractions = np.array([])
            else:
                result = fv.simulate_temperature_history_fv(history, flow_m3_s=Q, t_span_s=span,
                    solute=solute, grind=grind, observation_times_s=times, fraction_bounds_s=bounds, settings=settings)
                meta.update(json.loads(result.to_json(include_trajectories=False)))
                tr, checked, trace, quad = result.observations, result.checked_trajectory, result.trace, result.quadrature
                meta.update(Cstar=ps._solute_params()[solute]["c_s0"], capacities=result.phase_capacities_m3.tolist())
                raw = [f.raw_diagnostic_concentration_kg_m3 for f in result.fractions]
                fractions = np.array(raw, dtype=float) if all(v is not None for v in raw) else np.array([])
            arrays.update(times=tr.times_s, states=_fields(tr), volume=tr.hydraulic_volume_m3,
                          diagnostic_times=checked.times_s, diagnostic_states=_fields(checked),
                          trace_times=trace.times_s, trace_masses=trace.masses_kg,
                          frozen_temperature=trace.frozen_temperature_K, fractions=fractions,
                          quadrature_times=quad.times_s, quadrature_weights=quad.weights_s,
                          quadrature_order=quad.order, quadrature_flux=quad.outlet_flux_kg_s,
                          quadrature_Mout=quad.outlet_solute_kg, quadrature_inventory=quad.total_from_physical_fields_kg,
                          quadrature_phase_minima=quad.phase_minima_kg_m3)
            meta["segment_count"] = len(meta["segments"])
            complete = bool(meta["integration_complete"]) and list(meta["actual_span_s"]) == span
        else:
            values, checked_t, checked_y, records = ref.radau(history, Q, solute, grind, n, times, t_span_s=span)
            _, M0 = ref.initial_and_inventory(history.value_K(span[0]), solute, grind, n)
            frac = np.diff(values[np.searchsorted(times, bounds), -1])/(Q*np.diff(bounds))
            arrays.update(times=times, states=values, diagnostic_times=checked_t, diagnostic_states=checked_y,
                          volume=Q*(times-span[0]), fractions=frac)
            meta.update(status="COMPLETE", integration_complete=True, actual_span_s=span,
                        M0_cont_kg=M0, Cstar=ps._solute_params()[solute]["c_s0"], segments=records,
                        segment_count=len(records), shared_machinery="unchanged closures, source parameters/geometry, history value object; no candidate generator")
            complete = True
        if not all(np.isfinite(a).all() for a in arrays.values()):
            complete = False
            meta["reason"] = "NONFINITE_SAVED_ARRAY"
        meta["status"] = "COMPLETE" if complete else "PARTIAL_OR_FAILED"
    except Exception as exc:
        meta.update(status="FAILED", integration_complete=False, actual_span_s=None,
                    reason="WORKER_EXCEPTION:"+type(exc).__name__)
        complete = False
    meta["numerical_wall_s"] = time.monotonic()-start
    np.savez_compressed(directory/(execution_id+".npz"), **arrays)
    meta["arrays_sha256"] = digest(directory/(execution_id+".npz"))
    write_json(directory/(execution_id+".json"), meta)
    signal.setitimer(signal.ITIMER_REAL, 0.)
    return 0 if complete else 2


def execute(directory, case_id=None, correction=False):
    directory = Path(directory).resolve()
    with locked_authority(directory) as (authority, ledger):
        cases = read_json(BUNDLE/"CASES.json")["cases"]
        if correction and case_id is None:
            raise ValueError("correction requires a named affected case")
        if case_id is not None and case_id not in {c["id"] for c in cases}:
            raise ValueError("unknown case")
        selected = [c for c in cases if case_id is None or c["id"] == case_id]
        attempted = {e["case_id"] for e in ledger["executions"]}
        selected = [c for c in selected if correction or c["id"] not in attempted]
        for case in selected:
            limit = reserve(ledger, correction=correction)
            eid = f"exec-{len(ledger['executions'])+1:03d}"
            entry = dict(execution_id=eid, case_id=case["id"], status="LAUNCHED", reserved_wall_s=limit,
                         identities=identities(), correction=correction)
            ledger["executions"].append(entry)
            write_json(authority, ledger); write_json(directory/"executions.json", ledger["executions"])
            started = time.monotonic()
            try:
                with (directory/(eid+".log")).open("w") as log:
                    process = subprocess.run([sys.executable, "-m", "tools.pannusch_positive_fv_verification", "worker",
                                              "--evidence-dir", str(directory), "--case-id", case["id"], "--execution-id", eid],
                                             cwd=ROOT, env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT, timeout=limit)
                entry.update(status="COMPLETE" if process.returncode == 0 else "FAILED", returncode=process.returncode)
            except subprocess.TimeoutExpired:
                entry["status"] = "TIMEOUT"
            except BaseException:
                entry["status"] = "CANCELLED"
                raise
            finally:
                entry["charged_wall_s"] = time.monotonic()-started
                path = directory/(eid+".json")
                if path.exists():
                    entry["receipt_sha256"] = digest(path)
                    receipt = read_json(path)
                    entry["segment_count"] = receipt.get("segment_count", 0)
                    entry["exponential_applications"] = receipt.get("exponential_applications", 0)
                    entry["propagations"] = receipt.get("propagations", 0)
                    entry["diagnostic_evaluations"] = receipt.get("diagnostic_evaluations", 0)
                write_json(authority, ledger); write_json(directory/"executions.json", ledger["executions"])
                print(eid, case["id"], entry["status"], round(entry["charged_wall_s"], 3), "s; aggregate", round(used(ledger), 3), flush=True)


def load_case(directory, case, ledger):
    matches = [e for e in ledger if e["case_id"] == case["id"]]
    if not matches:
        raise ValueError("UNRUN")
    e = matches[-1]
    if e["status"] != "COMPLETE":
        raise ValueError("LATEST_ATTEMPT_"+e["status"])
    path = Path(directory)/(e["execution_id"]+".json")
    if digest(path) != e.get("receipt_sha256"):
        raise ValueError("RECEIPT_HASH_MISMATCH")
    meta = read_json(path)
    if meta["case"] != case or meta["case_sha256"] != canonical_hash(case) or meta["status"] != "COMPLETE":
        raise ValueError("INCOMPLETE_OR_WRONG_CASE")
    if meta["identities"] != identities() or e["identities"] != identities():
        raise ValueError("NUMERICAL_SOURCE_CHANGED")
    path = path.with_suffix(".npz")
    if digest(path) != meta["arrays_sha256"]:
        raise ValueError("ARRAY_HASH_MISMATCH")
    with np.load(path, allow_pickle=False) as archive:
        arrays = {k: archive[k] for k in archive.files}
    contract = read_json(BUNDLE/"CASES.json")
    passive, span, history, times, bounds = case_inputs(case, contract)
    n = case["cells"]
    if not meta["integration_complete"] or meta["actual_span_s"] != span:
        raise ValueError("PARTIAL_SUPPORT")
    if not all(np.isfinite(a).all() for a in arrays.values()):
        raise ValueError("NONFINITE_ARRAY")
    if not np.array_equal(arrays["times"], times) or arrays["states"].shape != (len(times), 3*n+1):
        raise ValueError("WRONG_OBSERVATION_SUPPORT")
    if arrays["fractions"].shape != (max(0, len(bounds)-1),) or arrays["volume"].shape != times.shape:
        raise ValueError("INCOMPLETE_OBSERVERS")
    dt, dy = arrays["diagnostic_times"], arrays["diagnostic_states"]
    if dt.ndim != 1 or dy.shape != (len(dt), 3*n+1) or dt[0] != span[0] or dt[-1] != span[1] or np.any(np.diff(dt) <= 0):
        raise ValueError("INVALID_DIAGNOSTIC_SUPPORT")
    if case["method"] != "Radau":
        st, sx = arrays["trace_times"], arrays["trace_masses"]
        steps = sum(int(np.ceil((b-a)/case["h_max_s"])) for a, b in zip(case["times_s"], case["times_s"][1:]))
        if st.shape != (steps+1,) or sx.shape != (steps+1, 3*n+1) or st[0] != span[0] or st[-1] != span[-1]:
            raise ValueError("INCOMPLETE_PRIMARY_STEPS")
        if len(arrays["quadrature_times"]) != 12*steps or arrays["quadrature_phase_minima"].shape != (12*steps, 3):
            raise ValueError("INCOMPLETE_QUADRATURE")
        records = [dict(s) if isinstance(s, list) else s for s in meta["segments"]]
        if len(records) != len(case["times_s"])-1 or any(s["status"] != "COMPLETE" for s in records):
            raise ValueError("INCOMPLETE_SEGMENTS")
        if any(a["end_state_sha256"] != b["start_state_sha256"] for a, b in zip(records, records[1:])):
            raise ValueError("STATE_RESET_AT_KNOT")
    if passive:
        initial, _, _ = ref.passive_exact(n, [0], meta["Q_m3_s"])
        expected = np.r_[initial[0], np.zeros(2*n+1)]
    else:
        expected, _ = ref.initial_and_inventory(history.value_K(span[0]), case["solute"], contract["grind"], n)
    if not np.allclose(arrays["states"][0], expected, rtol=2e-15, atol=1e-15):
        raise ValueError("INITIAL_STATE_CHANGED")
    return meta, arrays


def metric(values, scale, allowance):
    z = np.asarray(values)/scale
    return dict(max_abs_normalized=float(np.max(np.abs(z), initial=0.)),
                signed_min_normalized=float(np.min(z, initial=0.)), signed_max_normalized=float(np.max(z, initial=0.)),
                signed_final_normalized=float(z.reshape(-1)[-1]) if z.size else 0.,
                allowance=allowance, passed=bool(np.max(np.abs(z), initial=0.) <= allowance))


def accounting(meta, a):
    n, C, M = meta["case"]["cells"], meta["Cstar"], meta["M0_cont_kg"]
    Q = meta["Q_m3_s"]
    psi = ps.GRINDS[meta["grind"]]["psi"]
    weights = ps.ACS*ps.L/n*np.array([ps.ALPHA_L, psi*(1-ps.ALPHA_L), ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L)])
    fields = a["diagnostic_states"][:, :-1].reshape(-1, 3, n)
    remaining = np.sum(fields*weights[None, :, None], axis=(1, 2))
    mout = a["diagnostic_states"][:, -1]
    residual = remaining+mout-M
    minima = np.min(fields, axis=(0, 2))/C
    candidate = meta["case"]["method"] != "Radau"
    result = dict(M0_cont_kg=M, M0_independent_cell_sum_kg=float(remaining[0]+mout[0]),
                  initial_offset_kg=float(remaining[0]+mout[0]-M),
                  inventory=metric(residual, M, 1e-8), checked_samples=len(fields), actual_span_s=meta["actual_span_s"],
                  hydraulic_volume=metric(a["volume"]-Q*(a["times"]-a["times"][0]), Q*(a["times"][-1]-a["times"][0]), 1e-6))
    if candidate:
        minima = np.minimum(minima, np.min(a["quadrature_phase_minima"], axis=0)/C)
        times = np.r_[a["diagnostic_times"], a["quadrature_times"]]
        all_mout = np.r_[mout, a["quadrature_Mout"]]
        sorted_mout = all_mout[np.argsort(times, kind="stable")]
        min_increment = float(np.min(np.diff(sorted_mout), initial=0.)/M)
        qweights, qflux = a["quadrature_weights"].reshape(-1, 12), a["quadrature_flux"].reshape(-1, 12)
        q4 = np.cumsum(np.sum(qweights[:, :4]*qflux[:, :4], axis=1))
        q8 = np.cumsum(np.sum(qweights[:, 4:]*qflux[:, 4:], axis=1))
        result.update(quadrature_outlet=metric(q8-a["trace_masses"][1:, -1], M, 1e-6),
                      quadrature_refinement=metric(q8-q4, M, 1e-6),
                      quadrature_inventory=metric(a["quadrature_inventory"]-M, M, 1e-8),
                      quadrature_evaluations=len(a["quadrature_times"]),
                      minimum_Mout_increment_over_Mstar=min_increment,
                      minimum_Mout_over_Mstar=float(np.min(all_mout)/M))
        result["positivity_passed"] = bool(minima.min() >= -1e-10 and min_increment >= -1e-10 and all_mout.min()/M >= -1e-10)
    result["phase_minima_over_Cstar"] = dict(zip(("liquid", "fine", "coarse"), map(float, minima)))
    result["conservation_passed"] = all(v["passed"] for k, v in result.items() if isinstance(v, dict) and "passed" in v)
    return result


def agreement(a, b, meta):
    n, C, M = meta["case"]["cells"], meta["Cstar"], meta["M0_cont_kg"]
    V = meta["Q_m3_s"]*(meta["actual_span_s"][1]-meta["actual_span_s"][0])
    out = {name: metric(a["states"][:, i*n:(i+1)*n]-b["states"][:, i*n:(i+1)*n], C, 1e-6)
           for i, name in enumerate(("liquid", "fine", "coarse"))}
    out.update(Mout=metric(a["states"][:, -1]-b["states"][:, -1], M, 1e-6),
               volume=metric(a["volume"]-b["volume"], V, 1e-6),
               fractions=metric(a["fractions"]-b["fractions"], C, 1e-6))
    out["passed"] = all(v["passed"] for v in out.values())
    return out


def spatial(coarse, fine, meta):
    n, C, M = meta["case"]["cells"], meta["Cstar"], meta["M0_cont_kg"]
    c = coarse["states"][:, :-1].reshape(-1, 3, n)
    f = fine["states"][:, :-1].reshape(-1, 3, n, 2).mean(axis=-1)
    psi = ps.GRINDS[meta["grind"]]["psi"]
    capacities = np.array([ps.ALPHA_L, psi*(1-ps.ALPHA_L), ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L)])
    weighted = ps.ACS*ps.L/n*np.sum(np.abs(c-f)*capacities[None, :, None], axis=(1, 2))
    out = dict(fractions=metric(coarse["fractions"]-fine["fractions"], C, .005),
               Mout=metric(coarse["states"][:, -1]-fine["states"][:, -1], M, .005),
               weighted_field=metric(weighted, M, .005))
    out["passed"] = all(v["passed"] for v in out.values())
    return out


def reduce_report(directory, output, parent_evidence=None):
    """Pure saved-array reduction: no candidate, reference, or exponential invocation."""
    contract = read_json(BUNDLE/"CASES.json")
    ledger = read_json(Path(directory)/"executions.json")
    report = dict(task=TASK, parent_head=PARENT, contract_sha256=digest(BUNDLE/"CONTRACT.md"),
                  cases_sha256=digest(BUNDLE/"CASES.json"), reporter_sha256=digest(__file__),
                  rights=RIGHTS, PHYSICAL_VALIDATION="NOT_ESTABLISHED", cases={}, temporal={}, spatial={},
                  manufactured={}, observers={}, optional_nodal_diagnostics={}, execution_receipts=ledger,
                  resources=dict(executions=len(ledger), execution_wall_s=sum(charged(e) for e in ledger),
                                 remaining_slots=32-len(ledger), reserved_correction_slots=4,
                                 auxiliary_accounting="Task authority and HANDOFF; separately charged so repeated numerical reports remain deterministic"))
    data, metadata = {}, {}
    for case in contract["cases"]:
        key = case["id"]
        try:
            meta, arrays = load_case(directory, case, ledger)
            data[key], metadata[key] = arrays, meta
            report["cases"][key] = dict(case=case, status="COMPLETE", execution_id=meta["execution_id"],
                source_commit=meta["source_commit"], identities=meta["identities"], arrays_sha256=meta["arrays_sha256"],
                versions=meta["versions"], actual_span_s=meta["actual_span_s"], segment_count=meta["segment_count"],
                propagations=meta.get("propagations"), exponential_applications=meta.get("exponential_applications"),
                diagnostic_evaluations=meta.get("diagnostic_evaluations"), accounting=accounting(meta, arrays))
            if case["family"] != "F":
                times, mass = arrays["times"], arrays["states"][:, -1]
                def m(t):
                    at = np.flatnonzero(times == t)
                    if len(at) != 1:
                        raise ValueError("MISSING_EXACT_OBSERVER")
                    return float(mass[at[0]])
                whole = (m(30)-m(0))/(30*contract["Q_m3_s"])
                part = np.dot(arrays["fractions"], np.diff(contract["fraction_bounds_s"]))/30
                report["observers"][key] = dict(delayed_20_30_kg_m3=(m(30)-m(20))/(10*contract["Q_m3_s"]),
                    cross_knot_7_19_kg_m3=(m(19)-m(7))/(12*contract["Q_m3_s"]),
                    additivity_error_over_Cstar=abs(whole-part)/meta["Cstar"], passed=bool(abs(whole-part)/meta["Cstar"] <= 1e-12))
        except (ValueError, KeyError, OSError) as exc:
            data.pop(key, None); metadata.pop(key, None)
            report["cases"][key] = dict(case=case, status="UNAVAILABLE_OR_FAILED",
                                         reason=type(exc).__name__ if isinstance(exc, OSError) else str(exc))
    for solute in fv.th.SPECIES:
        a, b = "B."+solute+".FV", "B."+solute+".Radau"
        if a in data and b in data:
            report["temporal"]["steps."+solute] = agreement(data[a], data[b], metadata[a])
    for direction in ("rise", "fall"):
        a = "C."+direction+".default"
        for other in ("coarse", "finer", "Radau"):
            b = "C."+direction+"."+other
            if a in data and b in data:
                v = agreement(data[a], data[b], metadata[a]); v["gated"] = other != "coarse"
                report["temporal"][direction+"."+other] = v
    for history, nominal in (("rise", "C.rise.default"), ("trigonelline", "B.trigonelline.FV")):
        keys = ["D."+history+".200", nominal, "D."+history+".800"]
        values = []
        for a, b, label in zip(keys, keys[1:], ("200_to_400", "400_to_800")):
            if a in data and b in data:
                v = spatial(data[a], data[b], metadata[a]); v["gated"] = label == "400_to_800"
                report["spatial"][history+"."+label] = v; values.append(v)
        if len(values) == 2:
            ratios = {}
            for channel in ("fractions", "Mout", "weighted_field"):
                x, y = (v[channel]["max_abs_normalized"] for v in values)
                ratios[channel] = dict(difference_ratio=x/y if min(x, y) > 1e-12 else None,
                                       status="RESOLVED_DIFFERENCE_RATIO_NOT_ORDER_PROOF" if min(x, y) > 1e-12 else "ROUNDING_LIMIT_RATIO_UNRESOLVED")
            report["spatial"][history+".refinement_diagnostics"] = ratios
    for n in (32, 64, 128):
        key = "F.passive."+str(n)
        if key not in data:
            continue
        a = data[key]; exact, exact_out, M = ref.passive_exact(n, a["times"], contract["Q_m3_s"])
        values = np.mean(np.abs(a["states"][:, :n]-exact), axis=1)
        remaining = ps.ACS*ps.ALPHA_L*ps.L/n*np.sum(a["states"][:, :n], axis=1)
        report["manufactured"][str(n)] = dict(times_s=a["times"].tolist(), L1_liquid_error_over_C0=values.tolist(),
            outlet_error_over_M0=((a["states"][:, -1]-exact_out)/M).tolist(),
            postexit_remaining_plus_outlet_error=float((remaining[-1]+abs(a["states"][-1, -1]-M))/M))
    if all(str(n) in report["manufactured"] for n in (32, 64, 128)):
        orders = [np.log2(np.array(report["manufactured"][str(n)]["L1_liquid_error_over_C0"])[1:4]/
                          np.array(report["manufactured"][str(2*n)]["L1_liquid_error_over_C0"])[1:4]).tolist() for n in (32, 64)]
        finest = report["manufactured"]["128"]
        report["manufactured"]["orders"] = orders
        report["manufactured"]["passed"] = bool(np.min(orders) >= .8 and max(finest["L1_liquid_error_over_C0"][1:4]) <= .05
                                                    and finest["postexit_remaining_plus_outlet_error"] <= .05)
    ka, kb = "C.rise.default", "E.repeat.rise"
    report["repeatability"] = dict(passed=ka in data and kb in data and all(np.array_equal(data[ka][k], data[kb][k]) for k in data[ka]))
    if parent_evidence is not None:
        parent_ledger = read_json(Path(parent_evidence)/"executions.json")
        for solute in fv.th.SPECIES:
            key = "A."+solute
            try:
                e = next(e for e in parent_ledger if e["case_id"] == "A."+solute+".BDF")
                p = Path(parent_evidence)/(e["execution_id"]+".json")
                if digest(p) != e["receipt_sha256"]:
                    raise ValueError("PARENT_RECEIPT_HASH_MISMATCH")
                m = read_json(p)
                if m["source_commit"] != "a8c94caf35bff300519af9bcffb7d4771c5e9553" or m["status"] != "COMPLETE" or digest(p.with_suffix('.npz')) != m["arrays_sha256"]:
                    raise ValueError("PARENT_IDENTITY_MISMATCH")
                with np.load(p.with_suffix('.npz'), allow_pickle=False) as a:
                    difference = data[key]["fractions"]-a["fractions"]
                report["optional_nodal_diagnostics"][solute] = dict(parent_execution=e["execution_id"], parent_array_sha256=m["arrays_sha256"],
                    max_fraction_difference_over_Cstar=float(np.max(np.abs(difference))/metadata[key]["Cstar"]),
                    interpretation="CROSS_DISCRETIZATION_DIAGNOSTIC_NOT_ERROR_AGAINST_TRUTH_NOT_GATED")
            except (OSError, KeyError, ValueError, StopIteration) as exc:
                report["optional_nodal_diagnostics"][solute] = dict(status="UNAVAILABLE_OPTIONAL_DIAGNOSTIC", reason=type(exc).__name__)
    else:
        report["optional_nodal_diagnostics"] = dict(status="NOT_REQUESTED_NO_PARENT_RERUN")
    candidates = [c for c in contract["cases"] if c["method"] != "Radau"]
    complete = all(c["id"] in data for c in contract["cases"])
    candidate_complete = all(c["id"] in data for c in candidates)
    positivity = candidate_complete and all(report["cases"][c["id"]]["accounting"]["positivity_passed"] for c in candidates)
    conservation = candidate_complete and all(report["cases"][c["id"]]["accounting"]["conservation_passed"] for c in candidates)
    temporal = len(report["temporal"]) == 10 and all(v["passed"] for v in report["temporal"].values() if v.get("gated", True))
    spatial_ok = all(report["spatial"].get(h+".400_to_800", {}).get("passed", False) for h in ("rise", "trigonelline")) and report["manufactured"].get("passed", False)
    observers = len(report["observers"]) == 25 and all(v["passed"] for v in report["observers"].values())
    numeric = complete and positivity and conservation and temporal and spatial_ok and observers and report["repeatability"]["passed"]
    report["dispositions"] = dict(positivity="VERIFIED" if positivity else "INCOMPLETE", conservation="VERIFIED" if conservation else "INCOMPLETE",
        temporal_accuracy="VERIFIED" if temporal else "INCOMPLETE", spatial_accuracy="VERIFIED" if spatial_ok else "INCOMPLETE",
        retained_observers="VERIFIED" if observers else "INCOMPLETE", numerical_qualification="VERIFIED" if numeric else
            "POSITIVITY_AND_CONSERVATION_VERIFIED_ACCURACY_INCOMPLETE" if positivity and conservation else "INCOMPLETE",
        mathematical_structure="ALGEBRAIC_PROOF_AND_SEPARATE_SMALL_MESH_QA", software_QA="SEPARATE_RECEIPT", hosted_CI="SEPARATE_RECEIPT", independent_review="SEPARATE_EXACT_HEAD_RECEIPT")
    report["scope"] = "Only declared cases/settings; no full-domain, empirical, native-MATLAB or physical qualification; 001 unchanged"
    Path(output).mkdir(parents=True, exist_ok=True)
    write_json(Path(output)/"RESULTS.json", report)
    return report


def report(directory, output, parent_evidence=None):
    """Charge saved-evidence numerical reduction without launching any trajectory."""
    with locked_authority(directory) as (authority, ledger):
        limit = reserve(ledger, auxiliary=True)
        e = dict(kind="REPORT_ONLY", status="LAUNCHED", reserved_wall_s=limit)
        ledger["auxiliary"].append(e); write_json(authority, ledger)
        started = time.monotonic()
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("REPORT_WALL_CEILING")))
        signal.setitimer(signal.ITIMER_REAL, limit)
        try:
            value = reduce_report(directory, output, parent_evidence)
            e["status"] = "COMPLETE"
            return value
        except BaseException:
            e["status"] = "FAILED_OR_CANCELLED"
            raise
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0.)
            e["charged_wall_s"] = time.monotonic()-started
            write_json(authority, ledger)
            write_json(Path(directory)/"auxiliary.json", ledger["auxiliary"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("execute", "worker", "report"))
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--parent-evidence-dir", type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--execution-id")
    parser.add_argument("--correction", action="store_true")
    args = parser.parse_args()
    if args.mode == "execute":
        execute(args.evidence_dir, args.case_id, args.correction)
    elif args.mode == "worker":
        return worker(args.evidence_dir, args.case_id, args.execution_id)
    else:
        if args.output_dir is None:
            parser.error("report requires --output-dir")
        print(json.dumps(report(args.evidence_dir, args.output_dir, args.parent_evidence_dir)["dispositions"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

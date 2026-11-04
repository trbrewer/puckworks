"""Execution/reports for the approved wetting screen; native evidence is read-only."""
import argparse
from collections import OrderedDict
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
from scipy.optimize import minimize

from . import pressure_peak_stage_b0 as B0
from . import wetting_screen_001 as W

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/"docs/research/WETTING_SCREEN_001"
SEED = 20261103
RESAMPLES = 1000


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(2**20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n")


def csv_write(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows({k: json.dumps(v) if isinstance(v, (list, dict)) else v
                         for k, v in row.items()} for row in rows)


def verify_r0_config(config, theta):
    """Authenticate the fixed geometry, chemistry, pressure and initial state."""
    r = W.R0()
    expected = {
        ("geometry", "basket_radius_m"): r.radius,
        ("geometry", "axial_cells"): r.native_cells,
        ("coffee_bed", "initial_porosity"): r.phi,
        ("coffee_bed", "bed_depth_m"): r.length,
        ("liquid", "density_kg_m3"): r.rho,
        ("liquid", "dynamic_viscosity_Pa_s"): r.mu,
        ("liquid", "effective_solute_diffusivity_m2_s"): r.diffusivity,
        ("hydraulics", "wetting_permeability_m2"): r.wetting_k,
        ("hydraulics", "outlet_pressure_gauge_Pa"): 0.,
        ("hydraulics", "front_pressure_gauge_Pa"): 0.,
        ("wetting", "initial_saturation"): 0.,
        ("wetting", "initial_wet_front_m"): 0.,
        ("wetting", "front_smoothing_cells"): 1.,
        ("extraction", "rate_constant_1_s"): r.rate,
        ("extraction", "saturation_concentration_kg_m3"): r.capacity,
    }
    if any(config[section][key] != value for (section, key), value in expected.items()):
        raise ValueError("Retained R0 configuration differs from the fixed column")
    bed = config["coffee_bed"]
    if bed["dry_dose_kg"]*bed["initial_extractable_fraction_dry_basis"] != r.inventory_kg:
        raise ValueError("Retained R0 inventory differs")
    closure = config["form_a_whole_bed_closure"]
    if [closure[k] for k in ("aGPerSBar", "pstarBar", "n", "pdBar", "mcG")] != list(theta):
        raise ValueError("Retained closure differs from its frozen fold")


def load_data(args):
    native_manifest = json.loads((args.ewp/"docs/demonstrations/FORM_A/RUN_MANIFEST.json").read_text())
    path = args.native/"source_inputs.json"
    if digest(path) != native_manifest["input_sha256"]["source_inputs"]:
        raise ValueError("Source-input identity changed")
    sources = json.loads(path.read_text())
    table = ROOT/"docs/research/PRESSURE_PEAK_STAGE_D0/RESULT_TABLE.csv"
    if digest(table) != native_manifest["input_sha256"]["D0_saved_fits"]:
        raise ValueError("Frozen D0 bank changed")
    csv.field_size_limit(100_000_000)
    bank = {}
    expected = {"DESCRIPTIVE_ALL", *(f"HYD-LOCO-{p:.1f}" for p in W.NOMINAL)}
    with table.open() as stream:
        for row in csv.DictReader(stream):
            if row["record_type"] == "point_replay" and row["candidate"] == "A":
                if row["fold"] in expected:
                    p = json.loads(row["parameters"])
                    bank[row["fold"]] = [p[k] for k in ("a_g_s_bar", "Pstar_bar", "n", "Pd_bar", "Mc_fixed_g")]
    if set(bank) != expected or len(sources) != 56:
        raise ValueError("Wrong fold bank or cohort")
    for record in native_manifest["runs"]:
        if not set(record["roles"]) & {"primary A0", "primary A1"}:
            continue
        config_path = args.native/(record["run"]+".json")
        if digest(config_path) != record["config_sha256"]:
            raise ValueError("Retained configuration identity changed")
        held = record["nominal_pressure_bar"] if record.get("brew") else None
        verify_r0_config(json.loads(config_path.read_text()), W.freeze_tuple(bank, held))
    contexts = {}
    for row in sources:
        original = args.raw/"measurements_time_dependent"/(row["brew"]+".txt")
        if digest(original) != row["original_sha256"]:
            raise ValueError("Original source changed")
        t, p, mass, _ = B0.raw_trace(original)
        ct, _, q, _ = B0.clean_course(t, p, mass)
        pre = (t >= -2) & (t <= 0)
        baseline = np.median(mass[pre]) if pre.any() else mass[0]
        onset = B0.sustained_onset(ct, np.interp(ct, t, mass)-baseline, q)
        if onset != row["observed_onset_for_scoring_only_s"]:
            raise ValueError("Original B0c operator replay changed")
        # This contract is fixed BEFORE prediction. Missing prediction is unavailable.
        usable = t[(t >= 0.) & (t <= 100.)]
        contexts[row["brew"]] = usable
    return sources, bank, contexts, native_manifest


def numerical_prediction(source, theta, arm, parameters, dt, cells, native=False):
    return W.predict(np.asarray(source["times_s"]), np.asarray(source["pressure_bar"]),
                     theta, arm, parameters, dt=dt, cells=cells, native_time_scheme=native)


def save_prediction(path, prediction, lag=0.):
    arrays = {k: v for k, v in prediction.items() if isinstance(v, np.ndarray)}
    np.savez_compressed(path, **arrays)
    return dict(file=Path(path).name, sha256=digest(path), lag_s=lag,
                front_s=None if not math.isfinite(prediction["front_s"]) else prediction["front_s"],
                front_right_censored=not math.isfinite(prediction["front_s"]),
                max_balance_error_g=prediction["max_balance_error_g"],
                max_concentration=prediction["max_concentration"],
                min_concentration=prediction["min_concentration"],
                dt=prediction["dt"], cells=prediction["cells"])


def verify(args):
    sources, bank, contexts, manifest = load_data(args)
    by_brew = {r["brew"]: r for r in sources}
    records = [r for r in manifest["runs"] if set(r["roles"]) & {"primary A0", "primary A1"}]
    work = args.work/"verification"
    work.mkdir(parents=True, exist_ok=True)
    rows = []
    start, cpu = time.perf_counter(), time.process_time()
    for number, record in enumerate(records):
        path = args.native/record["run"]/"postProcessing/wholePull/0/traces.csv"
        if digest(path) != record["trace_sha256"]:
            raise ValueError("Native trace changed")
        history = bool(record.get("brew"))
        source = by_brew[record["brew"]] if history else dict(times_s=[0., 100.],
                    pressure_bar=[record["nominal_pressure_bar"]]*2)
        theta = W.freeze_tuple(bank, record["nominal_pressure_bar"] if history else None)
        arm = "A0" if record["arm"] == "A0" else "W0"
        with path.open() as stream:
            header = next(csv.reader(stream))
        names = ["time_s", "cup_water_mass_kg", "cup_beverage_mass_kg", "outlet_flow_m3_s"]
        a = np.loadtxt(path, delimiter=",", skiprows=1, usecols=[header.index(k) for k in names]).T
        nt = np.r_[0., a[0]]
        nm, nb, nq = (np.r_[0., a[k]*f] for k, f in ((1, 1000.), (2, 1000.), (3, 965000.)))
        # Verification constants have no original scale timestamps. Use the
        # retained native timestamps every 20 steps (~0.1 s), including initial
        # zero, rather than extending a terminal timestamp rounded below 100.
        # Histories always use the fixed ORIGINAL observation timestamps.
        contract = contexts[record["brew"]] if history else nt[::20][nt[::20] <= 100.]
        native_has_contract = bool(contract[-1] <= nt[-1])
        # Native verification additionally replays EWP's retained common
        # support. This is evidence-only: the primary predictor/fitting
        # contract above stays unchanged and missing coverage is unavailable.
        tobs = contract[contract <= nt[-1]]
        native_pred = dict(time=nt, beverage_g=nb, bed_flow_g_s=nq)
        native_onset = W.observe(native_pred, tobs)
        row = dict(run=record["run"], arm=record["arm"], brew=record.get("brew"),
                   pressure_bar=record["nominal_pressure_bar"],
                   native_qualification_failed=not record["balances_and_bounds_qualified"],
                   native_trace_sha256=record["trace_sha256"],
                   native_front_s=record["first_drip_s"] if record["first_drip_s"] >= 0 else None,
                   native_onset=native_onset,
                   primary_contract_last_s=float(contract[-1]),
                   native_last_s=float(nt[-1]),
                   native_full_contract_comparison_available=native_has_contract,
                   verification_support="Retained native/source common support, fixed before column prediction")
        for label, dt, cells, native in (("native_scheme", .005, 256, True),
                                        ("screen_scheme", args.dt, args.cells, False)):
            prediction = numerical_prediction(source, theta, arm, (), dt, cells, native)
            observer = W.observe(prediction, tobs)
            full_observer = W.observe(prediction, contract)
            if label == "screen_scheme":
                item = save_prediction(work/(record["run"]+".npz"), prediction)
                row["prediction"] = item
            row[label] = dict(front_s=prediction["front_s"] if math.isfinite(prediction["front_s"]) else None,
                liquid_max_difference_g=float(np.max(np.abs(np.interp(nt, prediction["time"], prediction["liquid_g"])-nm))),
                beverage_max_difference_g=float(np.max(np.abs(np.interp(nt, prediction["time"], prediction["beverage_g"])-nb))),
                endpoint_flow_difference_g_s=float(prediction["bed_flow_g_s"][-1]-nq[-1]),
                detector=observer, primary_contract_detector=full_observer,
                detection_agrees=observer["detected"] == native_onset["detected"],
                onset_difference_s=(observer["onset_s"]-native_onset["onset_s"]
                    if observer["detected"] and native_onset["detected"] else None),
                max_balance_error_g=prediction["max_balance_error_g"],
                max_concentration_kg_m3=prediction["max_concentration"])
        rows.append(row)
        print(json.dumps(dict(verification=number+1, total=len(records), run=record["run"],
            beverage_error_g=row["native_scheme"]["beverage_max_difference_g"],
            onset_delta=row["screen_scheme"]["onset_difference_s"])), flush=True)
    result = dict(rows=rows, wall_seconds=time.perf_counter()-start,
                  cpu_seconds=time.process_time()-cpu, dt=args.dt, cells=args.cells,
                  source_sha256={str(p.relative_to(ROOT)): digest(p) for p in
                      [ROOT/"puckworks/analysis/wetting_screen_001.py", Path(__file__)]},
                  native_manifest_sha256=digest(args.ewp/"docs/demonstrations/FORM_A/RUN_MANIFEST.json"))
    write_json(args.work/"VERIFICATION.json", result)
    return result


def train_indices(sources, held):
    return [i for i, r in enumerate(sources) if held is None or r["nominal_pressure_bar"] != held]


def coordinates(arm, physical):
    if arm == "W1":
        return np.array([physical[0]/100.])
    return np.r_[np.log(physical[:2]), physical[2]/100.] if arm == "W2T" else np.log(physical[:2])


def physical_parameters(arm, z):
    if arm == "W1":
        return [float(z[0]*100)]
    return [*np.exp(z[:2]).tolist(), float(z[2]*100)] if arm == "W2T" else np.exp(z[:2]).tolist()


def search_axes(arm):
    k = np.linspace(math.log(1e-16), math.log(1e-12), 9)
    pw = np.linspace(math.log(.5), math.log(30), 9)
    delay = np.linspace(0., 1., 21)
    return [delay] if arm == "W1" else [k, pw, delay] if arm == "W2T" else [k, pw]


class FoldObjective:
    """Training selection and frozen theta are fixed at construction, never per brew."""
    def __init__(self, sources, bank, contexts, held, arm, dt, cells):
        self.theta = W.freeze_tuple(bank, held)
        self.fold = "DESCRIPTIVE_ALL" if held is None else f"HYD-LOCO-{held:.1f}"
        self.indices = train_indices(sources, held)
        self.sources = [sources[i] for i in self.indices]
        self.contexts = contexts
        self.arm, self.dt, self.cells = arm, dt, cells
        self.conditions = sorted({r["nominal_pressure_bar"] for r in self.sources})
        self.groups = [np.array([i for i, r in enumerate(self.sources)
                        if r["nominal_pressure_bar"] == p]) for p in self.conditions]
        self.cache = OrderedDict()
        self.trials = []
        self.column_evaluations = 0

    def __call__(self, z):
        parameters = physical_parameters(self.arm, z)
        wet = parameters[:2] if self.arm == "W2T" else parameters
        key = tuple(wet)
        if key not in self.cache:
            predictions = []
            for source in self.sources:
                p = numerical_prediction(source, self.theta, self.arm, parameters, self.dt, self.cells)
                # Cache only quantities needed by the observer; internal states stay in
                # final/fine verification artifacts, not this short-lived search cache.
                predictions.append({k: p[k] for k in ("time", "beverage_g", "bed_flow_g_s")})
                self.column_evaluations += 1
            self.cache[key] = predictions
            if len(self.cache) > 3:
                self.cache.popitem(last=False)
        else:
            self.cache.move_to_end(key)
        lag = parameters[2] if self.arm == "W2T" else 0.
        squared = []
        detections = 0
        for source, prediction in zip(self.sources, self.cache[key]):
            result = W.observe(prediction, self.contexts[source["brew"]], lag)
            squared.append(W.squared_onset(result, source["observed_onset_for_scoring_only_s"]))
            detections += int(result["detected"])
        squared = np.asarray(squared)
        value = float(np.mean([squared[g].mean() for g in self.groups]))
        self.trials.append(dict(coordinates=list(map(float, z)), parameters=parameters,
                               loss_s2=value, detected_training=detections))
        return value


def fit_family(sources, bank, contexts, held, arm, args):
    label = "DESCRIPTIVE_ALL" if held is None else f"HYD-LOCO-{held:.1f}"
    path = args.work/"fits"/(label+"_"+arm+".json")
    if path.exists():
        saved = json.loads(path.read_text())
        if (saved["protocol_sha256"] != digest(OUT/"PLAN.md") or
            saved["source_sha256"] != digest(Path(__file__)) or
            saved["predictor_sha256"] != digest(ROOT/"puckworks/analysis/wetting_screen_001.py") or
            saved["dt"] != args.dt or saved["cells"] != args.cells):
            raise ValueError("Resume protocol, source or numerical settings changed")
        return saved
    path.parent.mkdir(exist_ok=True, parents=True)
    objective = FoldObjective(sources, bank, contexts, held, arm, args.dt, args.cells)
    axes = search_axes(arm)
    start, cpu = time.perf_counter(), time.process_time()
    for point in itertools.product(*axes):
        objective(point)
    seeds = sorted(objective.trials, key=lambda r: (r["loss_s2"], r["coordinates"]))[:5]
    optimizers = []
    for seed in seeds:
        result = minimize(objective, seed["coordinates"], method="Powell",
                          bounds=[(x[0], x[-1]) for x in axes],
                          options=dict(xtol=1e-5, ftol=1e-8))
        optimizers.append(dict(success=bool(result.success), message=str(result.message),
                               nfev=int(result.nfev), loss_s2=float(result.fun),
                               parameters=physical_parameters(arm, result.x)))
    best = min(objective.trials, key=lambda r: (r["loss_s2"], r["coordinates"]))
    ties = [r for r in objective.trials if r["loss_s2"] == best["loss_s2"]]
    values = np.asarray([r["parameters"] for r in ties])
    result = dict(arm=arm, fold=label, held_condition_bar=held,
        parameters=best["parameters"], loss_s2=best["loss_s2"],
        training_brews=[r["brew"] for r in objective.sources],
        theta_for_every_training_and_held_brew=objective.theta.tolist(),
        sampled_exact_minimum_count=len(ties),
        sampled_minimum_parameter_ranges=np.column_stack([values.min(axis=0), values.max(axis=0)]).tolist(),
        coordinate_distance_to_bounds=[min(z-x[0], x[-1]-z) for z, x in zip(best["coordinates"], axes)],
        optimizer_results=optimizers, trials=objective.trials,
        column_evaluations=objective.column_evaluations, dt=args.dt, cells=args.cells,
        wall_seconds=time.perf_counter()-start, cpu_seconds=time.process_time()-cpu,
        protocol_sha256=digest(OUT/"PLAN.md"), source_sha256=digest(Path(__file__)),
        predictor_sha256=digest(ROOT/"puckworks/analysis/wetting_screen_001.py"),
        numerical_scope="Fixed R0 column in search; no DESCRIPTIVE_ALL chemistry lookup",
        identifiability="Ranges of sampled equal minima, not confidence intervals or proof of uniqueness")
    write_json(path, result)
    print(json.dumps(dict(fit=label, arm=arm, loss_s2=result["loss_s2"],
                         parameters=result["parameters"], cpu_seconds=result["cpu_seconds"])), flush=True)
    return result


def fit_fold(args, held):
    sources, bank, contexts, _ = load_data(args)
    results = []
    for arm in ("W1", "W2", "W2T"):
        results.append(fit_family(sources, bank, contexts, held, arm, args))
    return [dict(arm=r["arm"], fold=r["fold"], cpu_seconds=r["cpu_seconds"]) for r in results]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["verify", "fit"])
    parser.add_argument("--ewp", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--dt", type=float, default=.02)
    parser.add_argument("--cells", type=int, default=256)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    args.work.mkdir(exist_ok=True, parents=True)
    if args.command == "verify":
        verify(args)
    else:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            jobs = [executor.submit(fit_fold, args, held) for held in [None, *W.NOMINAL.tolist()]]
            results = [job.result() for job in jobs]
        write_json(args.work/"FIT_EXECUTION.json", dict(folds=results,
            cpu_seconds=sum(r["cpu_seconds"] for group in results for r in group),
            python=platform.python_version(), workers=args.workers))


if __name__ == "__main__":
    main()


"""D0: capability demonstration, not validation; TARGET_EXPOSED.

PHYSICAL_VALIDATION=NOT_ESTABLISHED. Approved immutable plan at 2510091f.
Only this entry point orchestrates D0. Earlier helpers remain unchanged.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from contextlib import contextmanager
import hashlib
import json
import math
import multiprocessing
import os
from pathlib import Path
import pickle
import resource
import subprocess
import sys
import time
from types import SimpleNamespace

import numpy as np
from scipy.optimize import least_squares

from . import pressure_peak_stage_c3e as E

C, D, C2 = E.C, E.D, E.C.C2
C1, C0, A, B, S = C2.C1, C2.C0, C2.A, C2.B, C2.S
ROOT = E.ROOT
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_D0"
PLAN_SHA256 = "a364be4550ab0144d20e2dfb48beb82acd6cce20d2afffa986b5777cd04dc942"
WORK = Path("/home/tim/pressure-peak-d0-work")
RAW = Path("/home/tim/wasz-terminal-mass-evidence/upstream")
CACHE = Path("/home/tim/pressure-peak-stage-a/.b0-b0c-onsets.csv")
FORMS = ("A", "LC")
FOLDS = C.STANDARD
SEED = C2.SEED
CLAIM = D.CLAIM
INHERITED = "INHERITED: C2 capped onset-only law (onset RMSE 3.522 s, NEAR, fixed by C2)"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_plan(path=OUT / "PLAN.md"):
    if digest(path) != PLAN_SHA256:
        raise RuntimeError("Approved D0 PLAN.md changed; execution refused")


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(D.plain(value), separators=(",", ":"), allow_nan=False)+"\n")
    temporary.replace(path)


def log_event(work, **event):
    value = dict(plan_sha256=PLAN_SHA256, unix_time=time.time(), pid=os.getpid(), **event)
    data = (json.dumps(value, allow_nan=False)+"\n").encode()
    fd = os.open(Path(work)/"runtime.jsonl", os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


@contextmanager
def measured(work, name, role="phase", **details):
    wall, cpu = time.monotonic(), time.process_time()
    status = "interrupted"
    log_event(work, event="start", role=role, name=name, **details)
    try:
        yield
        status = "complete"
    finally:
        log_event(work, event="finish", role=role, name=name, status=status,
                  wall_seconds=time.monotonic()-wall, cpu_seconds=time.process_time()-cpu, **details)


class Audit:
    """Collect every differing field in a batch before stopping dependent work."""
    def __init__(self, name):
        self.name, self.checked, self.mismatches = name, 0, []

    def compare(self, actual, saved, draw="POINT", fold="DESCRIPTIVE_ALL", field="", candidate="", exact=False):
        if isinstance(saved, dict):
            for key, value in saved.items():
                self.compare(actual.get(key), value, draw, fold, field+"."+key, candidate, exact)
            return
        if isinstance(saved, (list, tuple, np.ndarray)):
            if actual is None or len(actual) != len(saved):
                self.checked += 1
                self.mismatches.append(dict(draw=draw, fold=fold, field=field, candidate=candidate,
                                            actual_length=None if actual is None else len(actual), saved_length=len(saved)))
                return
            try:
                expected, observed = np.asarray(saved), np.asarray(actual)
            except ValueError:
                expected = np.array([], dtype=object)
            if expected.dtype.kind in "biuf" and observed.shape == expected.shape:
                self.checked += expected.size
                tolerance = 0 if exact or expected.dtype.kind in "bi" else 1e-12
                try:
                    np.testing.assert_allclose(observed, expected, rtol=tolerance, atol=0)
                except AssertionError:
                    for index in zip(*np.where(~np.isclose(observed, expected, rtol=tolerance, atol=0))):
                        location = "".join(f"[{i}]" for i in index)
                        self.compare(observed[index].item(), expected[index].item(), draw, fold,
                                     field+location, candidate, exact)
                return
            for index, (x, y) in enumerate(zip(actual, saved)):
                self.compare(x, y, draw, fold, f"{field}[{index}]", candidate, exact)
            return
        self.checked += 1
        numeric = isinstance(saved, (int, float, np.number)) and not isinstance(saved, (bool, np.bool_))
        if numeric and actual is not None:
            try:
                np.testing.assert_allclose(actual, saved, rtol=0 if exact else 1e-12, atol=0)
                return
            except AssertionError:
                absolute = abs(float(actual)-float(saved))
                relative = absolute/abs(float(saved)) if saved else (0. if not absolute else "infinity")
                self.mismatches.append(dict(draw=draw, fold=fold, field=field, candidate=candidate,
                    actual=D.plain(actual), saved=D.plain(saved), absolute_difference=D.plain(absolute),
                    relative_difference=D.plain(relative)))
        elif actual != saved:
            self.mismatches.append(dict(draw=draw, fold=fold, field=field, candidate=candidate,
                                       actual=D.plain(actual), saved=D.plain(saved)))

    def finish(self, work):
        record = dict(name=self.name, checked_fields=self.checked, mismatch_count=len(self.mismatches),
                      mismatches=self.mismatches, plan_sha256=PLAN_SHA256)
        write_json(Path(work)/f"audit-{self.name}.json", record)
        if self.mismatches:
            print("ASSERTION_FAILURE", json.dumps(record), flush=True)
            raise RuntimeError(f"{self.name}: {len(self.mismatches)} mismatches; owner review required")
        print("ASSERTIONS_OK", self.name, self.checked, flush=True)
        return record


def training(ctx, sample, fold):
    conditions = ctx.brews.condition
    held = None if fold == "DESCRIPTIVE_ALL" else np.flatnonzero(np.asarray(ctx.brews.fold) == fold)
    train = np.flatnonzero(sample > 0) if held is None else np.flatnonzero(
        (sample > 0) & (conditions != conditions[held[0]]))
    weights = np.array([sample[i]/np.sum(conditions == conditions[i]) for i in train])
    weights /= weights.sum()
    return train, held, weights


class DrawEvaluator:
    """C3e residual/Jacobian with explicitly supplied sampled weights and Mc."""
    def __init__(self, pressure, t, target, mask, weights, mc, form, budget):
        self.pressure, self.t, self.target, self.mask = pressure, t, target, mask
        self.mc, self.arm, self.budget = mc, form, budget
        self.weight = np.sqrt(weights[:, None]*mask/mask.sum(axis=1)[:, None])
        self.last_z, self.last = None, None

    def __call__(self, z):
        self.budget.check()
        lo, hi = E.bounds(self.arm)
        if not np.isfinite(z).all() or np.any(z < lo) or np.any(z > hi):
            raise ValueError("Evaluation outside declared domain")
        if self.last_z is None or not np.array_equal(z, self.last_z):
            q, jac = E.flow(E.physical(z, self.arm), self.pressure, self.t, self.mc, self.arm)
            value = (((q-self.target)*self.weight).ravel(),
                     (jac*self.weight[..., None]).reshape(-1, len(z)))
            if not all(np.isfinite(v).all() for v in value):
                raise FloatingPointError("Nonfinite D0 residual/Jacobian; owner review required")
            self.last_z, self.last = z.copy(), value
        return self.last


def evaluator(ctx, sample, fold, mc, form):
    train, held, weights = training(ctx, sample, fold)
    g = ctx.coarse
    return DrawEvaluator(g.pressure[train], g.t, g.flow[train], g.mask[train], weights,
                         mc, form, C0.Deadline(math.inf)), train, held, weights


def context_from_fixture(row):
    """Self-contained CSV twin; no source-data files or historical tables needed."""
    ids, conditions = row["brew_ids"], np.array(row["conditions_bar"])
    folds = [f"HYD-LOCO-{p}" for p in conditions]
    brews = A.Brews(ids, conditions, np.array(row["endpoint_pressure"]),
        np.array(row["endpoint_observed_g_s"]), np.array(row["endpoint_times_s"]), {}, folds, 0.)
    grids = {}
    for name, prefix in (("coarse", "fit"), ("fine", "fine")):
        grids[name] = SimpleNamespace(brews=brews, t=np.array(row[prefix+"_times_s"]),
            pressure=np.array(row[prefix+"_pressure"]), flow=np.array(row[prefix+"_observed_flow"]),
            mask=np.array(row[prefix+"_mask"], dtype=bool))
    grids["fine"].late_weights = np.array(row["late_weights"])
    grids["fine"].observed_trend = np.array(row["observed_late_trend"])
    return SimpleNamespace(brews=brews, **grids, early=np.array(row["early_pressure_bar"]),
                           delay=np.array(row["observed_onsets_s"]), saved=row["saved_parameters_by_fold"])


def point_replays(ctx, rows, work):
    audit = Audit("point-replays")
    fits = [r for r in rows if r["record_type"] == "fit" and r["candidate"] in FORMS]
    for row in fits:
        form, fold = row["candidate"], row["fold"]
        _, train, held, _ = C.design(ctx.brews.condition, fold)
        p, mc = E.parameters(row["parameters"], form), row["Mc_fixed_g"]
        audit.compare(E.parameter_record(p, form, mc), row["parameters"], fold=fold, field="parameters", candidate=form)
        for grid, name in ((ctx.coarse, "objective"), (ctx.fine, "fine_objective")):
            q = E.flow(p, grid.pressure[train], grid.t, mc, form, False)[0]
            actual = C.objective_parts(ctx.brews.condition[train], C.trace_mse(q, grid.flow[train], grid.mask[train]))
            audit.compare(D.plain(actual), row[name], fold=fold, field=name, candidate=form)
        audit.compare(E.brew_records(ctx, p, mc, form, train, held), row["brew_predictions"],
                      fold=fold, field="predictions", candidate=form)
        audit.compare(E.global_peak(p, form), row["capacity_peak"], fold=fold, field="capacity_peak", candidate=form)
        lo, hi = E.bounds(form)
        ev = E.Evaluator(ctx.coarse.pressure[train], ctx.coarse.t, ctx.coarse.flow[train],
            ctx.coarse.mask[train], ctx.brews.condition[train], mc, form, C0.Deadline(math.inf))
        checks = [(row["starts"][row["selected_start"]]["final_coordinates"], row["jacobian_check"])]
        checks += [(s["initial_coordinates"], s["initial_jacobian_check"]) for s in row["starts"] if "initial_jacobian_check" in s]
        for z, saved in checks:
            actual = E.S.jacobian_diagnostic(ev, np.array(z), lo, hi)
            for key in ("analytic_norm", "full_branch_switches", "half_branch_switches", "half_step_error_decreases"):
                audit.compare(actual[key], saved[key], fold=fold, candidate=form, field="jacobian."+key)
            for rel, absolute in (("full_relative_error", "full_absolute_error"), ("half_relative_error", "half_absolute_error"),
                                  ("half_step_relative_change", "half_step_absolute_change")):
                audit.compare(saved[absolute]/saved["analytic_norm"] if saved["analytic_norm"] else None,
                              saved[rel], fold=fold, candidate=form, field="jacobian."+rel)
        if fold in FOLDS:
            ev, _, _, _ = evaluator(ctx, np.ones(len(ctx.brews.ids)), fold, mc, form)
            residual = ev(E.coordinates(p, form))[0]
            audit.compare(float(residual@residual), row["objective"]["objective"], fold=fold,
                          candidate=form, field="D0_unit_weight_objective")
        print("POINT_REPLAY", form, fold, flush=True)
    audit.compare(len(fits), 28, field="point_fit_count", exact=True)
    audit.finish(work)
    return fits


def prepare(raw, cache, work):
    verify_plan()
    rows = E.read_table()
    inputs = next(r for r in rows if r["record_type"] == "inputs")
    with measured(work, "1-authentication"):
        sources = E.source_hashes(raw, cache, inputs["brew_ids"])
        historical = next(r for r in rows if r["record_type"] == "provenance")["source_sha256"]
        audit = Audit("authentication")
        audit.compare(sources, historical, field="source_sha256", exact=True)
        audit.finish(work)
        ctx = D.load_context(raw, cache)
        ctx.delay = ctx.delays[:, 1]
        audit = Audit("raw-input-twin")
        audit.compare(dict(claim=CLAIM, **C.input_fixture(ctx)), inputs, field="inputs")
        audit.finish(work)
    with measured(work, "2-T2F-objective"):
        saved = ctx.saved["DESCRIPTIVE_ALL"]
        q = C1.flow_curve(C1.flow_parameters(saved), ctx.coarse.pressure, ctx.coarse.t, saved["Mc_fixed_g"])[0]
        objective = C.objective_parts(ctx.brews.condition, C.trace_mse(q, ctx.coarse.flow, ctx.coarse.mask))["objective"]
        audit = Audit("T2F-point-objective")
        audit.compare(objective, .0719361259858887, field="objective_sum_squares", candidate="T2-F")
        audit.finish(work)
    with measured(work, "3-point-replays"):
        # C2's point convention re-derives only DESCRIPTIVE_ALL Mc.
        sample = np.ones(len(ctx.brews.ids))
        mc = B.fit_course("C4", ctx.coarse, np.arange(len(sample)), sample, C0.Deadline(math.inf))[2]
        audit = Audit("point-Mc")
        audit.compare(mc, ctx.saved["DESCRIPTIVE_ALL"]["Mc_fixed_g"], field="Mc_fixed_g")
        audit.finish(work)
        points = point_replays(ctx, rows, work)
    with measured(work, "4-paired-draws-and-weight-test"):
        indices, samples = C2.paired_samples(ctx.brews)
        saved_c2 = {r["candidate"]: r for r in D.read_table(C2.OUT/"RESULT_TABLE.csv")}
        audit = Audit("draws-and-weights")
        pairing = saved_c2["T2-F"]["diagnostics"]["pairing"]
        audit.compare(indices, pairing["draw_indices"], field="draw_indices", exact=True)
        audit.compare(samples, pairing["multiplicities"], field="multiplicities", exact=True)
        for fold in FOLDS:
            train, held, weights = training(ctx, samples[0], fold)
            expected_train = np.flatnonzero(samples[0] > 0) if held is None else np.flatnonzero(
                (samples[0] > 0) & (ctx.brews.condition != ctx.brews.condition[held[0]]))
            expected = np.array([samples[0,i]/np.sum(ctx.brews.condition == ctx.brews.condition[i]) for i in expected_train])
            expected /= expected.sum()
            audit.compare(train, expected_train, draw=0, fold=fold, field="training", exact=True)
            audit.compare(weights, expected, draw=0, fold=fold, field="sampled_weights")
        audit.finish(work)
    state = dict(plan_sha256=PLAN_SHA256, ctx=ctx, inputs=inputs, points=points,
                 sources=sources, indices=indices, samples=samples, saved=saved_c2)
    path = work/"prepared.pkl"
    with path.open("wb") as stream:
        pickle.dump(state, stream)
    print("PREPARED", flush=True)
    return state


def bound_flags(record):
    return [key for key, item in record.items() if item["active"] or item["near_finite_bound"]]


def fit_problem(ctx, sample, fold, mc, onset_pd, form, work, draw):
    ev, train, held, weights = evaluator(ctx, sample, fold, mc, form)
    lo, hi = E.bounds(form)
    starts = E.start_values(form, {"Pd_bar": onset_pd})
    path = work/f"starts-{draw:03d}-{form}-{fold}.json"
    records = []
    g = ctx.coarse
    ids = [ctx.brews.ids[i] for i in train]
    def counts(p):
        return E.zero_counts(p, form, g.pressure[train], g.mask[train], ctx.brews.condition[train], ids)
    def attempt(z, group, fallback=False, original=None):
        started = time.monotonic()
        initial = ev(z)[0]
        record = dict(seed_group=group, original_coordinates=original, initial_coordinates=z.copy(),
            initial_objective=float(initial@initial), initial_bounds=E.bound_record(z, form),
            initial_counts=counts(E.physical(z, form)), fallback=fallback)
        records.append(record)
        try:
            fit = least_squares(lambda x: ev(x)[0], z, jac=lambda x: ev(x)[1], bounds=(lo, hi),
                method="dogbox" if fallback else "trf", x_scale="jac", ftol=1e-8, xtol=1e-8,
                gtol=1e-8, max_nfev=1500 if fallback else 500)
            if not np.isfinite(fit.fun).all() or not np.isfinite(fit.x).all():
                raise FloatingPointError("Nonfinite optimizer result")
            record.update(objective=float(2*fit.cost), success=bool(fit.success), nfev=fit.nfev,
                final_coordinates=fit.x, final_parameters=E.parameter_record(E.physical(fit.x, form), form, mc),
                final_bounds=E.bound_record(fit.x, form, fit.active_mask), final_counts=counts(E.physical(fit.x, form)),
                message=fit.message)
            return fit
        finally:
            record["wall_seconds"] = time.monotonic()-started
            write_json(path, dict(draw=draw, fold=fold, candidate=form, plan_sha256=PLAN_SHA256, starts=records))
    fits = []
    for group, physical in starts:
        original = E.coordinates(physical, form)
        fits.append(attempt(np.clip(original, lo+1e-10, hi-1e-10), group, original=original))
    valid = [(i,f) for i,f in enumerate(fits) if f.success and np.isfinite(f.fun).all()]
    if not valid:
        best = min(fits, key=lambda f: f.cost)
        fit = attempt(best.x, "fallback", True)
        if not fit.success:
            raise RuntimeError(f"Unresolved fit: draw={draw}, fold={fold}, form={form}")
        valid = [(len(fits),fit)]
    selected, fit = min(valid, key=lambda v: v[1].cost)
    objectives = [r["objective"] for r in records]
    p = E.physical(fit.x, form)
    q = E.flow(p, g.pressure[train], g.t, mc, form, False)[0]
    mse = C.trace_mse(q, g.flow[train], g.mask[train])
    np.testing.assert_allclose(float(weights@mse), 2*fit.cost, rtol=1e-12, atol=0)
    return dict(fold=fold, candidate=form, parameters=E.parameter_record(p, form, mc),
        objective=float(2*fit.cost), selected_start=selected, starts=records, weights=weights,
        training_indices=train, training_mse=mse, onset_seed_Pd_bar=onset_pd,
        start_disagreement=max(objectives)-min(objectives) > 1e-6*max(1.,2*fit.cost),
        selected_bound_flags=bound_flags(records[selected]["final_bounds"]), fallback=len(records)>len(starts),
        capacity_peak=E.global_peak(p, form), full_start_path=str(path), full_start_sha256=digest(path))


_STATE = _WORK = None


def initialize_worker(state, work):
    global _STATE, _WORK
    _STATE, _WORK = state, Path(work)
    verify_plan()


def prerequisites(draw):
    ctx, sample = _STATE["ctx"], _STATE["samples"][draw]
    path = _WORK/f"prerequisites-{draw:03d}.json"
    if path.exists():
        saved = json.loads(path.read_text())
        if saved["plan_sha256"] != PLAN_SHA256 or saved["draw"] != draw:
            raise RuntimeError("Prerequisite checkpoint identity mismatch")
        return saved
    with measured(_WORK, "Mc-onset", role="worker", draw=draw):
        audit = Audit(f"Mc-onset-{draw:03d}")
        bank = {}
        for fold in FOLDS:
            train, held, weights = training(ctx, sample, fold)
            budget = C0.Deadline(math.inf)
            mc = B.fit_course("C4", ctx.coarse, train, sample, budget)[2]
            onset = C2.fit_t2("onset", ctx.coarse.pressure[train], ctx.coarse.t, ctx.coarse.flow[train],
                ctx.coarse.mask[train], ctx.early[train], ctx.delay[train], weights, mc, budget)
            expected_mc = _STATE["saved"]["T2-F"]["refit_parameters_by_fold"][draw][fold]["Mc_fixed_g"]
            expected_onset = _STATE["saved"]["T2 onset-only (capped)"]["refit_parameters_by_fold"][draw][fold]
            audit.compare(mc, expected_mc, draw, fold, "Mc_fixed_g", "C4")
            audit.compare(onset, expected_onset, draw, fold, "onset", "T2 onset-only (capped)")
            margin = C2.margin_audit(onset, ctx, train, held)
            bank[fold] = dict(mc=float(mc), expected_mc=expected_mc, onset=onset, expected_onset=expected_onset,
                              margin=margin, training_indices=train, weights=weights)
        audit.finish(_WORK)
        result = dict(draw=draw, plan_sha256=PLAN_SHA256, bank=bank)
        write_json(path, result)
        return result


def fit_draw(draw):
    path = _WORK/f"draw-{draw:03d}.json"
    if path.exists():
        value = json.loads(path.read_text())
        if value["plan_sha256"] != PLAN_SHA256 or value["draw"] != draw:
            raise RuntimeError("Draw checkpoint identity mismatch")
        return draw
    with measured(_WORK, "flow-refit", role="worker", draw=draw):
        prereq = prerequisites(draw)
        ctx, sample = _STATE["ctx"], _STATE["samples"][draw]
        fits = {form: {} for form in FORMS}
        for fold in FOLDS:
            fixed = prereq["bank"][fold]
            for form in FORMS:
                fits[form][fold] = fit_problem(ctx, sample, fold, fixed["mc"], fixed["onset"]["Pd_bar"], form, _WORK, draw)
        result = dict(draw=draw, plan_sha256=PLAN_SHA256, prerequisites=prereq, fits=fits)
        write_json(path, result)
        print("DRAW_COMPLETE", draw, flush=True)
        return draw


def pool_map(state, work, function, indices):
    with ProcessPoolExecutor(max_workers=32, mp_context=multiprocessing.get_context("spawn"),
                             initializer=initialize_worker, initargs=(state, work)) as pool:
        futures = {pool.submit(function, i): i for i in indices}
        try:
            for future in as_completed(futures):
                future.result()
                print("TASK_COMPLETE", function.__name__, futures[future], flush=True)
        except BaseException:
            for future in futures:
                future.cancel()
            raise


def run_refits(state, work):
    completed = []
    for index in range(200):
        path = work/f"draw-{index:03d}.json"
        if path.exists():
            value = json.loads(path.read_text())
            if value["plan_sha256"] != PLAN_SHA256 or value["draw"] != index:
                raise RuntimeError("Draw checkpoint identity mismatch")
            completed.append(index)
    log_event(work, event="resume", role="information", draws=completed)
    if not (work/"pilot.json").exists():
        started = time.monotonic()
        pool_map(state, work, fit_draw, [i for i in (0,1) if i not in completed])
        wall = time.monotonic()-started
        events = [json.loads(line) for line in (work/"runtime.jsonl").read_text().splitlines()]
        # flow-refit encloses prerequisites for pilot draws; avoid CPU double counting.
        cpu = sum(r["cpu_seconds"] for r in events if r.get("name")=="flow-refit" and r.get("event")=="finish" and r.get("draw") in (0,1))
        record = dict(plan_sha256=PLAN_SHA256, draws=[0,1], wall_seconds=wall, worker_cpu_seconds=cpu,
            projected_total_worker_cpu_seconds=cpu*100, projected_32_worker_wall_seconds=cpu*100/32,
            parallelism_assumption="Two draw workers in pilot; projection assumes 32 occupied workers and similar draw costs. Startup, checks, comparator replays and reporting are additional.",
            projection_is_informational=True)
        write_json(work/"pilot.json", record)
        print("PILOT", json.dumps(record), flush=True)
    pool_map(state, work, prerequisites, [i for i in range(200) if not (work/f"prerequisites-{i:03d}.json").exists()])
    pool_map(state, work, fit_draw, [i for i in range(200) if not (work/f"draw-{i:03d}.json").exists()])


def prediction_arrays(ctx, bank, form):
    endpoint, mse, trends = (np.empty(len(ctx.brews.ids)) for _ in range(3))
    for held in ctx.brews.groups:
        record = bank[ctx.brews.fold[held[0]]]
        if "parameters" in record:
            record = record["parameters"]
        mc = record["Mc_fixed_g"]
        if form in FORMS:
            p = E.parameters(record, form)
            fine = E.flow(p, ctx.fine.pressure[held], ctx.fine.t, mc, form, False)[0]
            endpoint[held] = E.flow(p, ctx.brews.pressure[held], ctx.brews.t, mc, form, False)[0][:,-1]
        else:
            c0 = form.startswith("C0")
            p = C0.physical_flow(record) if c0 else C1.flow_parameters(record)
            flow = C0.flow_curve if c0 else C1.flow_curve
            fine = flow(p, ctx.fine.pressure[held], ctx.fine.t, mc)[0]
            endpoint[held] = flow(p, ctx.brews.pressure[held], ctx.brews.t, mc)[0][:,-1]
        mse[held] = C.trace_mse(fine, ctx.fine.flow[held], ctx.fine.mask[held])
        trends[held] = (fine*ctx.fine.late_weights[held]).sum(axis=1)
    if not all(np.isfinite(v).all() for v in (endpoint,mse,trends)):
        raise FloatingPointError("Nonfinite held-out prediction")
    return dict(endpoint=endpoint, trace_mse=mse, trends=trends)


def ratio(ctx, endpoints):
    ids = ctx.brews.ids
    numerator = float(np.mean([endpoints[ids.index(i)] for i in ("2-2","2-4")]))
    denominator = float(np.mean([endpoints[ids.index(i)] for i in ("2-3","2-5")]))
    return numerator/denominator if denominator else None


def metric_values(ctx, arrays, sample):
    endpoint, mse, trends = (np.asarray(arrays[k]) for k in ("endpoint","trace_mse","trends"))
    residual = endpoint-ctx.brews.target
    condition_residual = B.condition_means(ctx.brews, residual, sample)
    condition_trends = B.condition_means(ctx.brews, trends, sample)
    slope, peak = B.refit_response(ctx.brews, endpoint, sample)
    low = condition_residual[:3]
    resolved = [list(C.CONDITIONS).index(p) for p in (2.,3.5,4.,5.,6.)]
    return dict(endpoint_rmse_g_s=C0.loss(ctx.brews,residual**2,sample),
        trace_rmse_g_s=C0.loss(ctx.brews,mse,sample), low_pressure_bias_g_s=float(np.mean(low)),
        low_mae_g_s=float(np.mean(np.abs(low))), condition_residuals_g_s=condition_residual,
        condition_trends_g_s_s=condition_trends, trend_matches=int(sum(np.sign(condition_trends[resolved])==1)),
        slope_g_s_bar=slope, nominal_peak_bar=peak,
        brew_1_2_residual_g_s=float(residual[ctx.brews.ids.index("1-2")]),
        residual_1_g_s=float(low[0]), residual_2_g_s=float(low[1]), residual_3_5_g_s=float(low[2]),
        bias12_g_s=float(np.mean(low[:2])), mae12_g_s=float(np.mean(np.abs(low[:2]))),
        within_2bar_ratio=ratio(ctx,endpoint))


def replay_objectives(draw):
    path = _WORK/f"T2F-objectives-{draw:03d}.json"
    if path.exists():
        value = json.loads(path.read_text())
        if value["plan_sha256"] != PLAN_SHA256 or value["draw"] != draw:
            raise RuntimeError("Comparator checkpoint identity mismatch")
        return
    with measured(_WORK,"T2F-objectives",role="worker",draw=draw):
        ctx, sample = _STATE["ctx"], _STATE["samples"][draw]
        bank = _STATE["saved"]["T2-F"]["refit_parameters_by_fold"][draw]
        audit = Audit(f"T2F-objectives-{draw:03d}")
        result = {}
        for fold, record in bank.items():
            train, _, weights = training(ctx,sample,fold)
            q = C1.flow_curve(C1.flow_parameters(record),ctx.coarse.pressure[train],ctx.coarse.t,record["Mc_fixed_g"])[0]
            mse = C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train])
            objective = float(weights@mse)
            audit.compare(objective,record["objective_sum_squares"],draw,fold,"objective_sum_squares","T2-F")
            result[fold] = dict(parameters=record, training_indices=train, weights=weights,
                                training_mse=mse, objective=objective, saved_objective=record["objective_sum_squares"])
        audit.finish(_WORK)
        write_json(path,dict(draw=draw,plan_sha256=PLAN_SHA256,folds=result))


def evaluate_draw(draw):
    path = _WORK/f"metrics-{draw:03d}.json"
    if path.exists():
        value = json.loads(path.read_text())
        if value["plan_sha256"] != PLAN_SHA256 or value["draw"] != draw:
            raise RuntimeError("Metric checkpoint identity mismatch")
        return
    with measured(_WORK,"held-out-metrics",role="worker",draw=draw):
        ctx,sample = _STATE["ctx"],_STATE["samples"][draw]
        fitted = json.loads((_WORK/f"draw-{draw:03d}.json").read_text())
        result = {}
        banks = {form:fitted["fits"][form] for form in FORMS}
        banks["T2-F"] = _STATE["saved"]["T2-F"]["refit_parameters_by_fold"][draw]
        for form,bank in banks.items():
            arrays = prediction_arrays(ctx,bank,form)
            values = metric_values(ctx,arrays,sample)
            if form in FORMS:
                peak = bank["DESCRIPTIVE_ALL"]["capacity_peak"]
                values.update(continuous_peak_bar=peak["pressure_bar"], continuous_peak_capacity_g_s=peak["capacity_g_s"],
                    ordinary_peak_median_bar=float(np.median([bank[f]["capacity_peak"]["pressure_bar"] for f in FOLDS[1:]])))
            result[form] = dict(arrays=arrays,metrics=values)
        onset = np.empty(len(ctx.brews.ids))
        for held in ctx.brews.groups:
            record = fitted["prerequisites"]["bank"][ctx.brews.fold[held[0]]]["onset"]
            onset[held] = C0.onset_curve(C1.onset_parameters(record),ctx.early[held])[0]
        result["onset"] = dict(predictions=onset,rmse_s=C0.loss(ctx.brews,(onset-ctx.delay)**2,sample))
        write_json(path,dict(draw=draw,plan_sha256=PLAN_SHA256,values=result))


def saved_comparators(state, work):
    """Frozen point predictions only; no historical fitting or context CLI."""
    ctx, saved = state["ctx"], state["saved"]
    banks = {name:saved[name]["parameters_by_fold"] for name in
             ("T2-F","T2 joint (capped)","C0 joint (capped)","C1 T2-F","C0 T1 flow-only","C0 T1/T1-W joint")}
    values = {name:prediction_arrays(ctx,bank,name) for name,bank in banks.items()}
    selected = {m:S.select_stage("B0c")[m][0] for m in ("B1","E1")}
    replay = B.swelling_predict_saved(ctx.fine,ctx.delay,ctx.early,{m:S.fold_bank("B0c",r) for m,r in selected.items()})
    for name,record in replay.items():
        values[name] = dict(endpoint=record["endpoint"],
            trace_mse=C.trace_mse(record["q"],ctx.fine.flow,ctx.fine.mask),
            trends=(record["q"]*ctx.fine.late_weights).sum(axis=1))
    f1 = S.select_stage("B0d")["F1"][0]
    q,endpoint = np.empty_like(ctx.fine.flow),np.empty(len(ctx.delay))
    for fold,parameters in S.fold_bank("B0d",f1).items():
        held = np.asarray(ctx.brews.fold)==fold
        coef = np.array(parameters)
        endpoint[held] = B.air_endpoint(coef,ctx.brews.pressure[held],ctx.brews.t)[0]
        for j in range(len(ctx.fine.t)):
            q[held,j] = B.air_endpoint(coef,ctx.fine.pressure[held,:j+1],ctx.fine.t[:j+1])[0]
    values["F1"] = dict(endpoint=endpoint,trace_mse=C.trace_mse(q,ctx.fine.flow,ctx.fine.mask),
                        trends=(q*ctx.fine.late_weights).sum(axis=1))
    audit, rows = Audit("saved-point-comparators"), []
    for name,arrays in values.items():
        source = saved[name if name not in ("B1","E1","F1") else "C0 "+name]
        metrics = metric_values(ctx,arrays,np.ones(len(ctx.brews.ids)))
        for key in ("endpoint_rmse_g_s","trace_rmse_g_s","low_pressure_bias_g_s","slope_g_s_bar"):
            audit.compare(metrics[key],source[key],field=key,candidate=name)
        rows.append(dict(record_type="saved_comparator",candidate=name,metrics=metrics,arrays=arrays,
                         saved_metrics={k:source[k] for k in ("endpoint_rmse_g_s","trace_rmse_g_s","low_pressure_bias_g_s","slope_g_s_bar")},
                         source="C2 RESULT_TABLE saved row: "+source["candidate"],historical_refits=0))
    audit.finish(work)
    return rows


METRICS = ("endpoint_rmse_g_s","trace_rmse_g_s","low_pressure_bias_g_s","residual_1_g_s",
           "residual_2_g_s","residual_3_5_g_s","brew_1_2_residual_g_s","within_2bar_ratio","slope_g_s_bar")


def distribution(values):
    """All-draw intervals, with explicit unavailable ratios and no filtering."""
    missing = sum(v is None for v in values)
    if missing:
        return dict(median=None,interval=None,undefined_count=missing,total=len(values))
    return dict(median=float(np.median(values)),interval=A.interval(values),undefined_count=0,total=len(values))


def scale_comparison(flow, onset, graded):
    left,right = A.interval(flow),A.interval(onset)
    grade,gap = C0.consistency_grade(left,right)
    difference = np.asarray(flow)-np.asarray(onset)
    return dict(grade=grade if graded else "EXPLORATORY, NOT_GRADED",flow_interval_bar=left,onset_interval_bar=right,
        flow_width_bar=left[1]-left[0],onset_width_bar=right[1]-right[0],gap_bar=gap,
        paired_difference=distribution(difference),flow_percentiles=np.percentile(flow,[2.5,25,50,75,97.5]),
        onset_percentiles=np.percentile(onset,[2.5,25,50,75,97.5]),percentile_levels=[2.5,25,50,75,97.5],
        weak_interval_width_consistency=bool(graded and grade=="MEETS" and not (A.interval(difference)[0]<=0<=A.interval(difference)[1])),
        P0_consistency="NOT_APPLICABLE",Pstar_grade="NOT_GRADED")


def runtime_summary(work):
    events = [json.loads(line) for line in (work/"runtime.jsonl").read_text().splitlines()]
    finished = [r for r in events if r["event"]=="finish"]
    intervals = sorted((r["unix_time"]-r["wall_seconds"],r["unix_time"]) for r in finished if r["role"] in ("driver","check"))
    merged = []
    for start,end in intervals:
        if merged and start<=merged[-1][1]:
            merged[-1][1] = max(end,merged[-1][1])
        else:
            merged.append([start,end])
    workers = [r for r in finished if r["role"]=="worker"]
    outer = [r for r in workers if not any(o is not r and o["pid"]==r["pid"]
        and o["unix_time"]>=r["unix_time"] and o["unix_time"]-o["wall_seconds"]<=r["unix_time"]-r["wall_seconds"] for o in workers)]
    return dict(wall_seconds=sum(end-start for start,end in merged),
        worker_cpu_seconds=sum(r["cpu_seconds"] for r in outer)+sum(r.get("worker_cpu_seconds",0.) for r in finished if r["role"]=="check"),
        driver_cpu_seconds=sum(r["cpu_seconds"] for r in finished if r["role"] in ("driver","check")),
        resumed_draws=sorted({i for r in events if r["event"]=="resume" for i in r["draws"]}),
        attempts=[r for r in finished if r["role"] in ("driver","check")],
        accounting="Union of measured driver/check wall intervals; nested worker events counted once. Every completed/failed/interrupted logged attempt retained.")


def compact_fit(record):
    result = {k:v for k,v in record.items() if k!="starts"}
    columns = ["initial_objective","objective","success","nfev","initial_bound_flags","final_bound_flags",
               "initial_structural","initial_numerical","final_structural","final_numerical","final_coordinates"]
    result["start_columns"] = columns
    result["starts_compact"] = [[r["initial_objective"],r["objective"],r["success"],r["nfev"],
        bound_flags(r["initial_bounds"]),bound_flags(r["final_bounds"]),r["initial_counts"]["structural"],
        r["initial_counts"]["numerical"],r["final_counts"]["structural"],r["final_counts"]["numerical"],r["final_coordinates"]] for r in record["starts"]]
    result["seed_group_best_objectives"] = {group:min(r["objective"] for r in record["starts"] if r["seed_group"]==group)
                                            for group in {r["seed_group"] for r in record["starts"]}}
    keys = ("a_g_s_bar","Pstar_bar","n","Pd_bar")+(("f",) if record["candidate"]=="LC" else ())
    result["parameter_ranges"] = {key:[min(r["final_parameters"][key] for r in record["starts"]),
                                      max(r["final_parameters"][key] for r in record["starts"])] for key in keys}
    result["selected_bound_flags"] = bound_flags(record["starts"][record["selected_start"]]["final_bounds"])
    return result


def build_readings(state, draws, metrics, comparators):
    ctx = state["ctx"]
    ones = np.ones(len(ctx.brews.ids))
    reference = next(r for r in comparators if r["candidate"]=="B1")
    onset_pd = [d["prerequisites"]["bank"]["DESCRIPTIVE_ALL"]["onset"]["Pd_bar"] for d in draws]
    readings = []
    for form in FORMS:
        point_bank = {r["fold"]:r for r in state["points"] if r["candidate"]==form and r["fold"] in FOLDS}
        arrays = prediction_arrays(ctx,point_bank,form)
        center = metric_values(ctx,arrays,ones)
        peak = point_bank["DESCRIPTIVE_ALL"]["capacity_peak"]
        center.update(continuous_peak_bar=peak["pressure_bar"],continuous_peak_capacity_g_s=peak["capacity_g_s"],
                      ordinary_peak_median_bar=float(np.median([point_bank[f]["capacity_peak"]["pressure_bar"] for f in FOLDS[1:]])))
        values = [m["values"][form]["metrics"] for m in metrics]
        fields = [k for k,v in center.items() if not isinstance(v,np.ndarray)]
        distributions = {key:distribution([v[key] for v in values]) for key in fields}
        condition_intervals = [A.interval([v["condition_residuals_g_s"][i] for v in values]) for i in range(11)]
        trend_intervals = [A.interval([v["condition_trends_g_s_s"][i] for v in values]) for i in range(11)]
        sampled = B.paired_course_loss(ctx.brews,np.array([(np.asarray(reference["arrays"]["endpoint"])-ctx.brews.target)**2,
                                                          (arrays["endpoint"]-ctx.brews.target)**2]),SEED)
        delta = A.interval(sampled[:,1]-sampled[:,0])
        comparison = A.comparison(delta)
        grades = dict(accuracy=S.accuracy_grade(center["endpoint_rmse_g_s"],reference["metrics"]["endpoint_rmse_g_s"],comparison),
            peak=S.peak_grade(distributions["nominal_peak_bar"]["interval"]),
            slope=S.slope_grade(distributions["slope_g_s_bar"]["interval"]),trends=S.trend_grade(center["trend_matches"]),
            onset="NOT_SCORED",low_pressure_bias=C0.bias_grade(center["low_pressure_bias_g_s"]))
        parameters = {k:distribution([d["fits"][form]["DESCRIPTIVE_ALL"]["parameters"][k] for d in draws])
                      for k in ("a_g_s_bar","Pstar_bar","n","Pd_bar")+(("f",) if form=="LC" else ())}
        scale = scale_comparison([d["fits"][form]["DESCRIPTIVE_ALL"]["parameters"]["Pd_bar"] for d in draws],onset_pd,form=="A")
        grades["scale_consistency"] = scale["grade"]
        flags = dict(start_disagreement=[],bound_hits=[],fallbacks=[],censored_training=[],seed_dependence=[])
        bound_details, start_totals = [], dict(scheduled=0,unsuccessful=0,initial_structural=0,initial_numerical=0,final_structural=0,final_numerical=0)
        for draw in draws:
            for fold,fit in draw["fits"][form].items():
                selected = fit["starts"][fit["selected_start"]]
                # Use inherited active flags for unbounded n; no invented proximity band.
                bound = bound_flags(selected["final_bounds"])
                loc = dict(draw=draw["draw"],fold=fold)
                if fit["start_disagreement"]:
                    flags["start_disagreement"].append(loc)
                if bound:
                    flags["bound_hits"].append(loc)
                    bound_details.append(dict(**loc,fields=bound,parameters=fit["parameters"],bounds=selected["final_bounds"]))
                if fit["fallback"]:
                    flags["fallbacks"].append(loc)
                if selected["final_counts"]["total"]:
                    flags["censored_training"].append(loc)
                best = fit["objective"]
                groups = {g:min(r["objective"] for r in fit["starts"] if r["seed_group"]==g)
                          for g in ("saved_onset_Pd","4.0_bar")}
                if groups["saved_onset_Pd"]-best <= 1e-6*max(1,best) < groups["4.0_bar"]-best:
                    flags["seed_dependence"].append(loc)
                for attempt in fit["starts"]:
                    start_totals["scheduled"] += not attempt["fallback"]
                    start_totals["unsuccessful"] += not attempt["success"]
                    for phase in ("initial","final"):
                        for kind in ("structural","numerical"):
                            start_totals[phase+"_"+kind] += attempt[phase+"_counts"][kind]
        flagged = {r["draw"] for group in flags.values() for r in group}
        endpoints = {}
        for field,dist in distributions.items():
            if dist["interval"] is not None:
                endpoints[field] = [dict(draw=i,value=v[field]) for i,v in enumerate(values)
                                    if i in flagged and v[field] in dist["interval"]]
        for field,dist in parameters.items():
            endpoints[field] = [dict(draw=d["draw"],value=d["fits"][form]["DESCRIPTIVE_ALL"]["parameters"][field])
                for d in draws if d["draw"] in flagged and d["fits"][form]["DESCRIPTIVE_ALL"]["parameters"][field] in dist["interval"]]
        readings.append(dict(record_type="reading",candidate=form,eligibility="PRIMARY" if form=="A" else "EXPLORATORY",
            parameter_count=4 if form=="A" else 5,center=center,distributions=distributions,grades=grades,
            parameters=point_bank["DESCRIPTIVE_ALL"]["parameters"],parameter_distributions=parameters,scale_consistency=scale,
            condition_residual_intervals_g_s=condition_intervals,condition_trend_intervals_g_s_s=trend_intervals,
            b1_endpoint_rmse_g_s=reference["metrics"]["endpoint_rmse_g_s"],b1_trace_rmse_g_s=reference["metrics"]["trace_rmse_g_s"],
            accuracy_delta_interval_g_s=delta,accuracy_comparison=comparison,accuracy_resample_deltas=(sampled[:,1]-sampled[:,0]).tolist(),
            flags=flags,flagged_draw_counts={k:len({r["draw"] for r in v}) for k,v in flags.items()},
            flagged_fit_counts={k:len(v) for k,v in flags.items()},bound_details=bound_details,start_totals=start_totals,
            flagged_interval_endpoints=endpoints,point_arrays=arrays))
    paired = []
    for left,right in (("A","T2-F"),("LC","A")):
        for key in METRICS:
            differences = [None if None in (m["values"][left]["metrics"][key],m["values"][right]["metrics"][key]) else
                m["values"][left]["metrics"][key]-m["values"][right]["metrics"][key] for m in metrics]
            paired.append(dict(record_type="paired",candidate=left+" - "+right,metric=key,
                               distribution=distribution(differences),differences=differences,
                               comparator_label="replay of saved C2 refits" if right=="T2-F" else "paired D0 refits"))
    return readings,paired


CALL_PATH = {
    "checked_pattern":"TimeoutError|Deadline|Budget|timed_attempt|7200|time.monotonic",
    "active_path":["D0.evaluator -> C0.Deadline(math.inf) -> DrawEvaluator -> C3e.flow/capacity -> C3d/C3c/C3a numerical helpers",
        "D0.prepare/prerequisites -> B.fit_course(..., C0.Deadline(math.inf)) -> predict_course/_course_ode",
        "D0.prerequisites -> C2.fit_t2(..., C0.Deadline(math.inf)) -> C0.onset_curve",
        "Point-only E.Evaluator receives C0.Deadline(math.inf); point Jacobian checks never enter refits"],
    "findings":["C0.Deadline.check contains a monotonic >= end TimeoutError; end=math.inf disables it.",
        "B.fit_course and C2.fit_t2 only call their supplied budget; no independent wall-time stop.",
        "C3a.Budget/timed_attempt and earlier CLI mains hardcode 7200; none is called by D0.",
        "A.FitBudget has a default 7200-second limit; D0 never constructs it.",
        "Scorecard time_limit/evaluate_rows use SIGALRM and deadline comparisons; D0 calls neither.",
        "C3e.fit_fold and training_evaluator are not used for refits.",
        "D0 time.monotonic calls measure durations only. No subprocess/future timeout is set."],
    "wall_clock_cap":None,"workers":32,"blas_threads_per_worker":1,
}


def report_results(state,work):
    verify_plan()
    if not all((work/f"draw-{i:03d}.json").exists() for i in range(200)):
        raise RuntimeError("All 200 completed draws required; no partial-draw grade")
    pool_map(state,work,replay_objectives,list(range(200)))
    pool_map(state,work,evaluate_draw,list(range(200)))
    comparators = saved_comparators(state,work)
    draws = [json.loads((work/f"draw-{i:03d}.json").read_text()) for i in range(200)]
    metrics = [json.loads((work/f"metrics-{i:03d}.json").read_text()) for i in range(200)]
    readings,paired = build_readings(state,draws,metrics,comparators)
    rows = [dict(state["inputs"],record_type="inputs"),
        dict(record_type="pairing",seed=SEED,draw_indices=state["indices"],multiplicities=state["samples"],
             brew_ids=state["ctx"].brews.ids)]
    historical = next(r for r in E.read_table() if r["record_type"]=="provenance")["source_sha256"]
    rows.append(dict(record_type="source_authentication",actual_sha256=state["sources"],expected_sha256=historical))
    rows.extend(dict(r,record_type="point_replay") for r in state["points"])
    external = []
    for draw in draws:
        index = draw["draw"]
        rows.append(dict(record_type="onset_Mc_assertions",draw=index,bank=draw["prerequisites"]["bank"]))
        for form in FORMS:
            for fold,record in draw["fits"][form].items():
                rows.append(dict(record_type="refit",draw=index,**compact_fit(record)))
                external.append(dict(path=record["full_start_path"],sha256=record["full_start_sha256"]))
        objective = json.loads((work/f"T2F-objectives-{index:03d}.json").read_text())
        rows.append(dict(record_type="T2F_refit_replay",draw=index,folds=objective["folds"],label="replay of saved C2 refits"))
        rows.append(dict(record_type="draw_metrics",draw=index,values=metrics[index]["values"]))
    rows.extend(comparators)
    rows.extend(readings)
    rows.extend(paired)
    source_onset = state["saved"]["T2 onset-only (capped)"]
    onset_rmse = [m["values"]["onset"]["rmse_s"] for m in metrics]
    audit = Audit("inherited-onset-interval")
    audit.compare(A.interval(onset_rmse),source_onset["onset_rmse_interval_s"],field="onset_rmse_interval_s")
    audit.finish(work)
    rows.append(dict(record_type="inherited_onset",candidate=INHERITED,onset_grade=source_onset["onset_grade"],
        onset_rmse_s=source_onset["onset_rmse_s"],onset_rmse_interval_s=A.interval(onset_rmse),
        point_parameters_by_fold=source_onset["parameters_by_fold"],refit_rmse_s=onset_rmse))
    sources = dict(state["sources"])
    for path in (OUT/"PLAN.md",Path(__file__),ROOT/"tests/test_pressure_peak_stage_d0.py",E.OUT/"RESULT_TABLE.csv"):
        sources[str(path.relative_to(ROOT))] = digest(path)
    rows.append(dict(record_type="provenance",plan_sha256=PLAN_SHA256,source_sha256=sources,
        external_start_records=external,call_path=CALL_PATH,pilot=json.loads((work/"pilot.json").read_text()),
        runtime=runtime_summary(work),observed_within_2bar_ratio=ratio(state["ctx"],state["ctx"].brews.target),
        refit_count=200,fit_count=4800,scheduled_start_count=43200,point_replay_count=28,source_base_commit="2510091f7f40f2fe10ab9f6efb52c3605e9c8772"))
    rows = finalize_reporting(rows,work,state)
    rows = [{k:v for k,v in row.items() if k!="claim"} for row in rows]
    D.write_table(rows,OUT/"RESULT_TABLE.csv")
    write_summary(rows,OUT/"SUMMARY.md")
    print("REPORT_COMPLETE",digest(OUT/"RESULT_TABLE.csv"),flush=True)


def write_summary(rows,path):
    readings = [r for r in rows if r["record_type"]=="reading"]
    paired = [r for r in rows if r["record_type"]=="paired"]
    provenance = next(r for r in rows if r["record_type"]=="provenance")
    onset = next(r for r in rows if r["record_type"]=="inherited_onset")
    def interval(bounds):
        return "unavailable" if bounds is None else f"[{bounds[0]:.6g}, {bounds[1]:.6g}]"
    def metric(r,key):
        return f"{r['center'][key]:.6g} {interval(r['distributions'][key]['interval'])}"
    text = ["# PRESSURE-PEAK D0: A and exploratory LC", "", "**"+CLAIM+".**", "",
        "A is primary (four parameters); LC is EXPLORATORY (five). Grades use ordinary held-out predictions on this retrospective cohort. No overall PASS. DESCRIPTIVE_ALL parameter intervals are in-sample.","",
        "| Form | Accuracy | Peak | Slope | Trends | Onset | Low bias | Scale |",
        "|---|---|---|---|---|---|---|---|"]
    for r in readings:
        text.append("| "+r["candidate"]+(" (EXPLORATORY)" if r["candidate"]=="LC" else "")+" | "+" | ".join(r["grades"][k] for k in
            ("accuracy","peak","slope","trends","onset","low_pressure_bias","scale_consistency"))+" |")
    text += ["","| Separate onset law | Held-out onset RMSE [95%], s | Grade |","|---|---|---|",
        f"| {INHERITED} | {onset['onset_rmse_s']:.9g} {interval(onset['onset_rmse_interval_s'])} | NEAR, fixed by C2 |",
        "","This onset grade belongs only to the inherited law.","",
        "| Form | Endpoint RMSE [95%], g/s | Trace RMSE [95%], g/s | Slope >=9 bar [95%], g/s/bar | Nominal peak [95%], bar |",
        "|---|---|---|---|---|"]
    for r in readings:
        text.append("| "+r["candidate"]+" | "+" | ".join(metric(r,k) for k in
            ("endpoint_rmse_g_s","trace_rmse_g_s","slope_g_s_bar","nominal_peak_bar"))+" |")
    text += ["",f"B1 endpoint/trace RMSE: {readings[0]['b1_endpoint_rmse_g_s']:.9g}/{readings[0]['b1_trace_rmse_g_s']:.9g} g/s. RMSE is mean condition RMSE. Accuracy uses the separate B0c 1,000 paired condition-then-brew resamples, +/-0.25 g/s.","",
        "| Form | Accuracy delta [95%], g/s | Continuous global capacity peak [95%], bar | Capacity at peak [95%], g/s | Ordinary-fold peak median [95%], bar |",
        "|---|---|---|---|---|"]
    for r in readings:
        text.append(f"| {r['candidate']} | {r['accuracy_comparison']} {interval(r['accuracy_delta_interval_g_s'])} | "+" | ".join(metric(r,k) for k in
            ("continuous_peak_bar","continuous_peak_capacity_g_s","ordinary_peak_median_bar"))+" |")
    for r in readings:
        peaks = [p["capacity_peak"]["pressure_bar"] for p in rows if p["record_type"]=="point_replay"
                 and p["candidate"]==r["candidate"] and p["fold"] in FOLDS[1:]]
        text += ["",f"{r['candidate']} ordinary point-fold continuous peak range: [{min(peaks):.6g}, {max(peaks):.6g}] bar (range, not a confidence interval)."]
    text += ["", "Continuous peaks are DESCRIPTIVE_ALL parameter-derived global maxima, checking all stationary candidates and endpoint limits, including competing LC maxima. The nominal peak grade is lenient; fold ranges are not confidence intervals.","",
        "| Form | Flow Pd [95%]; width, bar | Onset Pd [95%]; width, bar | Paired flow-minus-onset Pd median [95%], bar | Grade |",
        "|---|---|---|---|---|"]
    for r in readings:
        s=r["scale_consistency"]
        text.append(f"| {r['candidate']} | {interval(s['flow_interval_bar'])}; {s['flow_width_bar']:.6g} | {interval(s['onset_interval_bar'])}; {s['onset_width_bar']:.6g} | {s['paired_difference']['median']:.6g} {interval(s['paired_difference']['interval'])} | {s['grade']} |")
    for r in readings:
        s=r["scale_consistency"]
        text += ["",f"{r['candidate']} scale interval gap {s['gap_bar']:.6g} bar; flow/onset descriptive percentiles (2.5/25/50/75/97.5): "+
            "/".join(f"{v:.6g}" for v in s["flow_percentiles"])+" / "+"/".join(f"{v:.6g}" for v in s["onset_percentiles"])+" bar. "+
            ("MEETS comes from interval width while the paired interval excludes zero; this is weak consistency, not a shared scale. " if s["weak_interval_width_consistency"] else "")+
            f"P0 consistency NOT_APPLICABLE. Pstar {r['parameters']['Pstar_bar']:.6g} {interval(r['parameter_distributions']['Pstar_bar']['interval'])} bar, NOT_GRADED."]
    text += ["", "| Form | 1 / 2 / 3.5-bar signed residuals, g/s | Signed low bias [95%], g/s | Low-condition MAE [95%], g/s | bias12 / mae12, g/s |",
        "|---|---|---|---|---|"]
    for r in readings:
        c=r["center"]
        text.append(f"| {r['candidate']} | "+" / ".join(f"{v:+.6g}" for v in c["condition_residuals_g_s"][:3])+f" | {metric(r,'low_pressure_bias_g_s')} | {metric(r,'low_mae_g_s')} | {c['bias12_g_s']:.6g} / {c['mae12_g_s']:.6g} |")
    text += ["", "| Form / nominal bar | Held-out residual [95%], g/s | Late trend [95%], g/s/s (resolved conditions only) |",
        "|---|---|---|"]
    for r in readings:
        for i,p in enumerate(C.CONDITIONS):
            trend = f"{r['center']['condition_trends_g_s_s'][i]:.6g} {interval(r['condition_trend_intervals_g_s_s'][i])}" if p in (2.,3.5,4.,5.,6.) else "not scored"
            text.append(f"| {r['candidate']} / {p:g} | {r['center']['condition_residuals_g_s'][i]:+.6g} {interval(r['condition_residual_intervals_g_s'][i])} | {trend} |")
    for r in readings:
        text += ["",f"{r['candidate']} resolved rising-trend matches: {r['center']['trend_matches']}/5, refit count interval {interval(r['distributions']['trend_matches']['interval'])}.",""]
    for contrast in ("A - T2-F","LC - A"):
        text += ["",contrast+" paired differences; identical whole-brew draws. T2-F is a replay of saved C2 refits.","",
                 "| Metric | Median difference | 95% interval |","|---|---:|---|"]
        for r in paired:
            if r["candidate"]==contrast:
                d=r["distribution"]
                text.append(f"| {r['metric']} | {d['median']:.6g} | {interval(d['interval'])} |" if d["median"] is not None else f"| {r['metric']} | undefined | unavailable |")
    draw_rows = [r for r in rows if r["record_type"]=="draw_metrics"]
    text += ["", "| Form | Brew 1-2 residual median [95%], g/s | 3.5-bar residual median [95%], g/s | Within-2-bar ratio median [95%] |",
             "|---|---|---|---|"]
    for form in (*FORMS,"T2-F"):
        cells=[]
        for field in ("brew_1_2_residual_g_s","residual_3_5_g_s","within_2bar_ratio"):
            d=distribution([r["values"][form]["metrics"][field] for r in draw_rows])
            cells.append(f"{d['median']:.6g} {interval(d['interval'])}" if d["median"] is not None else f"unavailable ({d['undefined_count']} undefined)")
        text.append("| "+form+" | "+" | ".join(cells)+" |")
    text += ["",f"Observed within-2-bar ratio, recomputed from authenticated endpoints: {provenance['observed_within_2bar_ratio']:.12g}. Zero denominators are undefined, never floored. The 3.5-bar condition has three brews and only 10 distinct within-condition resampling multisets, so its interval is coarse.","",
        "| Form | Start disagreement draws / fits | Bound draws / fits | Fallback draws / fits | Censored selected-training draws / fits |",
        "|---|---|---|---|---|"]
    for r in readings:
        text.append("| "+r["candidate"]+" | "+" | ".join(f"{r['flagged_draw_counts'][k]} / {r['flagged_fit_counts'][k]}" for k in
            ("start_disagreement","bound_hits","fallbacks","censored_training"))+" |")
    left,right = readings[1]["center"],readings[0]["center"]
    observed_ratio = provenance["observed_within_2bar_ratio"]
    text += ["",f"LC minus A point changes in absolute error: within-2-bar ratio {abs(left['within_2bar_ratio']-observed_ratio)-abs(right['within_2bar_ratio']-observed_ratio):+.9g}; "+
        f"brew 1-2 {abs(left['brew_1_2_residual_g_s'])-abs(right['brew_1_2_residual_g_s']):+.9g} g/s; "+
        f"3.5-bar condition {abs(left['residual_3_5_g_s'])-abs(right['residual_3_5_g_s']):+.9g} g/s. Negative reduces absolute error. Read these magnitudes as a tradeoff, not a veto."]
    for r in readings:
        text += ["",f"{r['candidate']} start totals: {json.dumps(r['start_totals'])}. Onset-seed dependence: {r['flagged_draw_counts']['seed_dependence']} draws. "+
            f"Bound fields: {json.dumps({k:sum(k in b['fields'] for b in r['bound_details']) for k in ('log_a','log_Pstar','log_Pd','n','f')})}. "+
            "Flagged interval endpoint contributors: "+json.dumps({k:v for k,v in r["flagged_interval_endpoints"].items() if v})+".",""]
        if "seed_group_totals" in r:
            text += [f"{r['candidate']} seed-group start totals: {json.dumps(r['seed_group_totals'])}. "+
                f"Largest within-fit parameter spans across starts: {json.dumps(r['maximum_start_parameter_spans'])}. "+
                f"Selected boundary draw counts: {json.dumps(r['degenerate_boundary_draw_counts'])}.",""]
    pilot, runtime = provenance["pilot"], provenance["runtime"]
    text += ["All starts, failures and boundary/censoring qualifications are retained. No Jacobian checks ran in refits. Point checks replayed C3e. Omission twins are replayed context only; 3.5-bar information remains in Mc.","",
        "Runtime and source details", "",
        f"Pilot draws 0 and 1: {pilot['wall_seconds']:.3f} s wall, {pilot['worker_cpu_seconds']:.3f} s worker CPU. "+
        f"Projection: {pilot['projected_32_worker_wall_seconds']:.3f} s at 32 workers, {pilot['projected_total_worker_cpu_seconds']:.3f} s worker CPU. "+
        pilot['parallelism_assumption']+" Informational only; no time cap. Pilot draws are included in the 200.","",
        "Pilot per-start wall seconds (count/min/median/max/sum): "+json.dumps(pilot.get("start_timings",{}))+".","",
        f"Cumulative measured wall {runtime['wall_seconds']:.3f} s; worker/check CPU {runtime['worker_cpu_seconds']:.3f} s; "+
        f"driver CPU {runtime['driver_cpu_seconds']:.3f} s. Resumed draws: {runtime['resumed_draws'] or 'none'}. "+
        runtime['accounting']+" Per-attempt records are retained in RESULT_TABLE.csv and the work-directory runtime log.","",
        "Call-path inspection: "+" ".join(CALL_PATH["findings"]),"",
        "Source hashes, selected fits, compact per-start records, assertion twins and paired draw values are in RESULT_TABLE.csv. Full start records remain outside Git at the recorded paths and SHA-256 values. Waszkiewicz et al., Zenodo 18046315, CC-BY-4.0. Earlier stages and source data are unchanged.","",
        "Interpretation rules, verbatim",""]
    for line in (OUT/"PLAN.md").read_text().splitlines():
        if len(line)>2 and line[0]=="R" and line[1].isdigit() and line[2]==".":
            text += [line, ""]
    text += ["","D0 results await owner review. No merge or successor is authorized.",""]
    result="\n".join(text)
    if "\u2014" in result:
        raise ValueError("Summary must not contain em dashes")
    path.write_text(result)


def final_replay_details(state, rows, work):
    """Complete the saved grid/nesting and comparator reporting checks, without refits."""
    if any(r["record_type"]=="point_reference" for r in rows):
        return
    audit = Audit("final-saved-details")
    ctx = state["ctx"]
    points = {(r["candidate"],r["fold"]):r for r in rows if r["record_type"]=="point_replay"}
    refs = {r["fold"]:r for r in E.read_table() if r["record_type"]=="reference"}
    for (form,fold),point in points.items():
        ref = refs[fold] if form=="A" else points["A",fold]
        coarse = ref["objective"]["objective"]-point["objective"]["objective"]
        fine = ref["fine_objective"]["objective"]-point["fine_objective"]["objective"]
        audit.compare(coarse,point["coarse_gain"],fold=fold,candidate=form,field="coarse_gain")
        audit.compare(fine,point["fine_gain"],fold=fold,candidate=form,field="fine_gain")
        audit.compare(coarse>0 and (fine<=0 or abs(coarse-fine)>=coarse),point["grid_gain_unresolved"],fold=fold,candidate=form,field="grid_gain_unresolved")
        if form=="LC":
            train = np.array(point["training_indices"])
            p = np.r_[E.parameters(ref["parameters"],"A"),0.]
            q = E.flow(p,ctx.coarse.pressure[train],ctx.coarse.t,point["Mc_fixed_g"],form,False)[0]
            objective = C.objective_parts(ctx.brews.condition[train],C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train]))["objective"]
            audit.compare(objective,point["nested_benchmark"]["A_embedded_objective"],fold=fold,candidate=form,field="nested_objective")
            audit.compare(point["objective"]["objective"]-objective,point["nested_benchmark"]["returned_minus_A"],fold=fold,candidate=form,field="returned_minus_A")
    for fold,ref in refs.items():
        rows.append(dict(record_type="point_reference",fold=fold,**{k:ref[k] for k in
            ("candidate","parameters","training_indices","objective","fine_objective")}))
    for row in (r for r in rows if r["record_type"]=="saved_comparator"):
        name = row["candidate"]
        source = state["saved"][name if name not in ("E1","F1","B1") else "C0 "+name]
        if "parameters_by_fold" in source:
            row["parameters_by_fold"] = source["parameters_by_fold"]
        if "onset_rmse_s" in source:
            prediction = np.empty(len(ctx.brews.ids))
            for held in ctx.brews.groups:
                p = source["parameters_by_fold"][ctx.brews.fold[held[0]]]
                p = p.get("onset_parameters",p)
                physical = C0.physical_onset(p) if name.startswith("C0") else C1.onset_parameters(p)
                prediction[held] = C0.onset_curve(physical,ctx.early[held])[0]
            actual = C0.loss(ctx.brews,(prediction-ctx.delay)**2)
            audit.compare(actual,source["onset_rmse_s"],candidate=name,field="onset_rmse_s")
            row["arrays"]["onset"] = prediction
            row["metrics"]["onset_rmse_s"] = actual
            row["saved_metrics"]["onset_rmse_s"] = source["onset_rmse_s"]
        objectives = {}
        for fold,p in source.get("parameters_by_fold",{}).items():
            if "objective_sum_squares" not in p:
                continue
            train,_,weights = training(ctx,np.ones(len(ctx.brews.ids)),fold)
            q = C1.flow_curve(C1.flow_parameters(p),ctx.coarse.pressure[train],ctx.coarse.t,p["Mc_fixed_g"])[0]
            mse = C.trace_mse(q,ctx.coarse.flow[train],ctx.coarse.mask[train])
            objective = float(weights@mse)
            if "joint" in name:
                onset = C0.onset_curve(C1.onset_parameters(p),ctx.early[train])[0]
                objective = objective/C0.FLOW_SCALE**2+float(weights@(onset-ctx.delay[train])**2)/C0.ONSET_SCALE**2
            audit.compare(objective,p["objective_sum_squares"],fold=fold,candidate=name,field="objective_sum_squares")
            objectives[fold] = dict(actual=objective,saved=p["objective_sum_squares"])
        row["objective_replays"] = objectives
    source = state["saved"]["T2-F"]
    metrics = [r for r in rows if r["record_type"]=="draw_metrics"]
    comparisons = {}
    for field,saved_field in (("endpoint_rmse_g_s","endpoint_rmse_interval_g_s"),("trace_rmse_g_s","trace_rmse_interval_g_s"),
        ("low_pressure_bias_g_s","low_pressure_bias_interval_g_s"),("slope_g_s_bar","slope_interval_g_s_bar")):
        actual = A.interval([r["values"]["T2-F"]["metrics"][field] for r in metrics])
        audit.compare(actual,source[saved_field],candidate="T2-F",field=saved_field)
        comparisons[field] = dict(actual=actual,saved=source[saved_field])
    rows.append(dict(record_type="T2F_interval_replay",comparisons=comparisons))
    audit.finish(work)


def finalize_reporting(rows, work, state):
    """Summarize recorded diagnostics and timings without any fitting."""
    final_replay_details(state,rows,work)
    provenance = next(r for r in rows if r["record_type"]=="provenance")
    provenance["call_path"] = CALL_PATH
    pilot = json.loads((work/"pilot.json").read_text())
    if "start_timings" not in pilot:
        timings = {f:[] for f in FORMS}
        for index in (0,1):
            draw = json.loads((work/f"draw-{index:03d}.json").read_text())
            for form in FORMS:
                timings[form].extend(s["wall_seconds"] for fit in draw["fits"][form].values() for s in fit["starts"])
        pilot["start_timings"] = {f:dict(count=len(v),minimum=min(v),median=float(np.median(v)),maximum=max(v),sum=sum(v))
                                  for f,v in timings.items()}
        write_json(work/"pilot.json",pilot)
    provenance["pilot"] = pilot
    for reading in (r for r in rows if r["record_type"]=="reading"):
        fits = [r for r in rows if r["record_type"]=="refit" and r["candidate"]==reading["candidate"]]
        groups = {g:dict(starts=0,initial_structural=0,initial_numerical=0,final_structural=0,final_numerical=0)
                  for g in ("saved_onset_Pd","4.0_bar")}
        for fit in fits:
            seeds = E.start_values(reading["candidate"],{"Pd_bar":fit["onset_seed_Pd_bar"]})
            for (group,_),record in zip(seeds,fit["starts_compact"]):
                values = dict(zip(fit["start_columns"],record))
                groups[group]["starts"] += 1
                for key in groups[group]:
                    if key!="starts":
                        groups[group][key] += values[key]
        reading["seed_group_totals"] = groups
        reading["maximum_start_parameter_spans"] = {key:max(r["parameter_ranges"][key][1]-r["parameter_ranges"][key][0] for r in fits)
                                                     for key in fits[0]["parameter_ranges"]}
        reading["degenerate_boundary_draw_counts"] = {label:len({r["draw"] for r in fits
            if key in r["selected_bound_flags"] and (r["parameters"][key]<=.5 if value==0 else r["parameters"][key]>=.5)})
            for label,key,value in (("f=0","f",0),("f=1","f",1))} if reading["candidate"]=="LC" else {}
        reading["degenerate_boundary_draw_counts"]["n=1"] = len({r["draw"] for r in fits if "n" in r["selected_bound_flags"]})
    manifest = work/"external-start-records.sha256"
    if not manifest.exists():
        audit = Audit("external-start-record-hashes")
        for record in provenance["external_start_records"]:
            audit.compare(digest(record["path"]),record["sha256"],field=record["path"],exact=True)
        audit.finish(work)
        manifest.write_text("".join(r["sha256"]+"  "+r["path"]+"\n" for r in provenance["external_start_records"]))
    provenance["external_start_manifest"] = dict(path=str(manifest),sha256=digest(manifest),count=4800)
    provenance["call_path_grep"] = dict(path=str(work/"call-path-grep.txt"),sha256=digest(work/"call-path-grep.txt"))
    provenance["source_sha256"]["puckworks/analysis/pressure_peak_stage_d0.py"] = digest(__file__)
    provenance["source_sha256"]["tests/test_pressure_peak_stage_d0.py"] = digest(ROOT/"tests/test_pressure_peak_stage_d0.py")
    return rows


def run_check(work, command):
    """Timed independent checks; subprocess timeout deliberately absent."""
    wall, cpu = time.monotonic(), time.process_time()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    status = "interrupted"
    log_event(work, event="start", role="check", name=" ".join(command))
    try:
        result = subprocess.run(command, check=False)
        status = "complete" if result.returncode == 0 else "failed"
        return result.returncode
    finally:
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        log_event(work, event="finish", role="check", name=" ".join(command), status=status,
            wall_seconds=time.monotonic()-wall, cpu_seconds=time.process_time()-cpu,
            worker_cpu_seconds=after.ru_utime+after.ru_stime-before.ru_utime-before.ru_stime)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=("prepare", "run", "report", "finalize"), default="run")
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--onset-cache", type=Path, default=CACHE)
    parser.add_argument("--work", type=Path, default=WORK)
    parser.add_argument("--check", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    verify_plan()
    if args.work.resolve().is_relative_to(ROOT):
        raise ValueError("Checkpoints must remain outside Git")
    for name in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
        if os.environ.get(name) != "1":
            raise RuntimeError(f"Set {name}=1 before imports")
    args.work.mkdir(parents=True, exist_ok=True)
    if args.check:
        sys.exit(run_check(args.work, args.check))
    with measured(args.work, args.phase, role="driver"):
        path = args.work/"prepared.pkl"
        if path.exists():
            with path.open("rb") as stream:
                state = pickle.load(stream)
            if state["plan_sha256"] != PLAN_SHA256:
                raise RuntimeError("Preparation checkpoint identity mismatch")
        else:
            state = prepare(args.raw, args.onset_cache, args.work)
        if args.phase == "run":
            run_refits(state, args.work)
            print("REFITS_COMPLETE", flush=True)
        if args.phase in ("run","report"):
            report_results(state,args.work)
        if args.phase == "finalize":
            rows = finalize_reporting(D.read_table(OUT/"RESULT_TABLE.csv"),args.work,state)
            provenance = next(r for r in rows if r["record_type"]=="provenance")
            provenance["runtime"] = runtime_summary(args.work)
            provenance["source_sha256"]["puckworks/analysis/pressure_peak_stage_d0.py"] = digest(__file__)
            provenance["source_sha256"]["tests/test_pressure_peak_stage_d0.py"] = digest(ROOT/"tests/test_pressure_peak_stage_d0.py")
            rows = [{k:v for k,v in r.items() if k!="claim"} for r in rows]
            D.write_table(rows,OUT/"RESULT_TABLE.csv")
            write_summary(rows,OUT/"SUMMARY.md")
    if args.phase in ("run","report","finalize") and (OUT/"RESULT_TABLE.csv").exists():
        # Include the just-finished report/check accounting without another refit.
        rows = D.read_table(OUT/"RESULT_TABLE.csv")
        next(r for r in rows if r["record_type"]=="provenance")["runtime"] = runtime_summary(args.work)
        rows = [{k:v for k,v in r.items() if k!="claim"} for r in rows]
        D.write_table(rows,OUT/"RESULT_TABLE.csv")
        write_summary(rows,OUT/"SUMMARY.md")


if __name__ == "__main__":
    main()

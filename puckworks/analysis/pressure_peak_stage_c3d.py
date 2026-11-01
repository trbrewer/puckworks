"""C3d Pd-transfer screen; capability demonstration, not validation.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED. Implementation was
separately authorized after approval of the unchanged C3d plan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import least_squares

from . import pressure_peak_stage_c3c as C

D, C1 = C.D, C.C1
ROOT = C.ROOT
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C3D"
PLAN_SHA256 = "8086b1e741487b0967bf8e94de69a1e9385a9aff4280a61c78247e5ee1b142a9"
FIXED_PD = 3.9844972419062152
HELD = ("HYD-LOCO-1.0", "HYD-LOCO-2.0", *C.OMITTED)
FOLDS = ("DESCRIPTIVE_ALL", *HELD)
SCHEDULE = tuple((arm, fold) for arm in ("A", "B-W3", "B-W4")
                 for fold in (FOLDS if arm == "A" else HELD))


def read_table(path=OUT / "RESULT_TABLE.csv"):
    return D.read_table(path)


def coordinates(p, arm):
    z = C.coordinates(p)
    if arm == "A":
        z[3] = np.log(z[3])
    return z


def physical(z, arm):
    p = C.physical(z)
    if arm == "A":
        p[3] = np.exp(p[3])
    return p


def bounds(arm):
    if arm != "A":
        return C.bounds(arm.removeprefix("B-"))
    lo, hi = C.bounds("W4")
    lo[3], hi[3] = np.log(.1), np.log(100.)
    return lo, hi


def start_values(arm, saved):
    if arm == "A":
        return [(group, [*s, pd]) for s in C.STARTS for group, pd in
                (("saved_onset_Pd", saved["Pd_bar"]), ("4.0_bar", 4.))]
    return [("C3c", s) for s in C.start_values(arm.removeprefix("B-"), saved)]


def split(p, arm):
    return (p[:3], p[3]) if arm == "A" else (p, FIXED_PD)


def parameter_record(p, arm, mc):
    shape, pd = split(p, arm)
    return C.parameter_record(shape, pd, mc)


def parameters(record, arm):
    keys = ("a_g_s_bar", "Pstar_bar", "n")
    keys += ("Pd_bar",) if arm == "A" else ("P0_bar",) if arm == "B-W4" else ()
    return np.array([record[k] for k in keys])


def capacity(p, pressure, arm):
    shape, pd = split(p, arm)
    c, dc = C.capacity(shape, pressure, pd)
    if arm != "A":
        return c, dc
    pressure = np.maximum(np.asarray(pressure, dtype=float), 0.)
    x = pressure/pd
    h = C.opening(x, p[2])[0]
    ue = np.zeros_like(x)
    positive = x > 0
    with np.errstate(over="ignore"):
        logu = p[2]*np.log(x[positive])
    finite = logu < C.LOG_MAX
    values = np.zeros_like(logu)
    values[finite] = np.exp(logu[finite]-np.exp(logu[finite]))
    ue[positive] = values
    dh = h-p[2]*ue
    # Match C1's cancellation-safe n=1 limit at very small positive x.
    if p[2] == 1.:
        dh = np.where(x < 1e-4, x*x*(.5+x*(-1/3+x*(1/8-x/30))), dh)
    dpd = p[0]*pd*np.exp(-pressure/p[1])*dh
    return c, np.concatenate((dc, dpd[..., None]), axis=-1)


def flow(p, pressure, t, mc, arm, jacobian=True):
    c, dc = capacity(p, pressure, arm)
    q, mass = D.mass_flow(c, t, mc)
    if not jacobian:
        return q, mass, c
    integral = np.zeros_like(dc)
    integral[..., 1:, :] = np.cumsum(
        (dc[..., :-1, :]+dc[..., 1:, :])*np.diff(t)[:, None]/2, axis=-2)
    inner = np.exp(-mass/mc)
    factor = np.exp(-inner)
    jac = dc*factor[..., None]+(q*inner*factor/mc)[..., None]*integral
    return q, jac


class Evaluator:
    """Only training arrays enter optimization; no onset vector is accepted."""
    def __init__(self, pressure, t, target, mask, conditions, mc, arm, budget):
        self.pressure, self.t, self.target, self.mask = pressure, t, target, mask
        self.mc, self.arm, self.budget = mc, arm, budget
        self.weight = np.sqrt(D.condition_weights(conditions)[:, None]*mask/mask.sum(axis=1)[:, None])
        self.last_z, self.last = None, None

    def __call__(self, z):
        self.budget.check()
        if self.last_z is None or not np.array_equal(self.last_z, z):
            q, jac = flow(physical(z, self.arm), self.pressure, self.t, self.mc, self.arm)
            result = (((q-self.target)*self.weight).ravel(),
                      (jac*self.weight[..., None]).reshape(-1, len(z)))
            if not all(np.isfinite(v).all() for v in result):
                raise FloatingPointError("Nonfinite evaluation: stop for owner review")
            self.last_z, self.last = z.copy(), result
        return self.last


def training_evaluator(ctx, arm, fold, budget):
    source, train, _, _ = C.design(ctx.brews.condition, fold)
    g = ctx.coarse
    return Evaluator(g.pressure[train], g.t, g.flow[train], g.mask[train],
                     ctx.brews.condition[train], ctx.saved[source]["Mc_fixed_g"], arm, budget)


def finite_difference(evaluate, z, lo, hi, multiplier=1.):
    residual = evaluate(z)[0]
    jac = np.empty((len(residual), len(z)))
    threshold = z[3] if evaluate.arm == "B-W4" else 0.
    branches = evaluate.pressure > threshold
    switches = np.zeros_like(branches, dtype=bool)
    for k in range(len(z)):
        step = multiplier*1e-4*max(1., abs(z[k]))
        left, right = z.copy(), z.copy()
        if z[k]-step < lo[k]:
            right[k] = min(z[k]+step, hi[k])
        elif z[k]+step > hi[k]:
            left[k] -= step
        else:
            left[k] -= step
            right[k] += step
        jac[:, k] = (evaluate(right)[0]-evaluate(left)[0])/(right[k]-left[k])
        if evaluate.arm == "B-W4":
            switches |= (evaluate.pressure > left[3]) != branches
            switches |= (evaluate.pressure > right[3]) != branches
    return jac, int((switches & evaluate.mask).sum())


def jacobian_diagnostic(evaluate, z, lo, hi):
    analytic = evaluate(z)[1]
    full, switches = finite_difference(evaluate, z, lo, hi)
    half, half_switches = finite_difference(evaluate, z, lo, hi, .5)
    norm = float(np.linalg.norm(analytic))
    ef, eh, change = (float(np.linalg.norm(v)) for v in
                       (full-analytic, half-analytic, full-half))
    return dict(analytic_norm=norm, full_absolute_error=ef, half_absolute_error=eh,
        full_relative_error=ef/norm if norm else None, half_relative_error=eh/norm if norm else None,
        half_step_absolute_change=change, half_step_relative_change=change/norm if norm else None,
        full_branch_switches=switches, half_branch_switches=half_switches,
        half_step_error_decreases=eh < ef)


def bound_record(z, arm, active=None):
    lo, hi = bounds(arm)
    names = ("log_a", "log_Pstar", "n", "log_Pd" if arm == "A" else "P0")[:len(z)]
    result = {}
    for k, name in enumerate(names):
        finite = np.isfinite(hi[k])
        distance = min(z[k]-lo[k], hi[k]-z[k])/(hi[k]-lo[k]) if finite else None
        result[name] = dict(lower_distance=float(z[k]-lo[k]),
            upper_distance=float(hi[k]-z[k]) if finite else None,
            fraction_of_range=float(distance) if finite else None,
            near_finite_bound=bool(distance <= 1e-6) if finite else None,
            active=int(active[k]) if active is not None else None)
    return result


def seed_groups(attempts, selected):
    best = attempts[selected]["objective"]
    tolerance = 1e-6*max(1., best)
    groups = {}
    for group in ("saved_onset_Pd", "4.0_bar"):
        all_group = [r for r in attempts if r["seed_group"] == group]
        good = [r for r in all_group if r.get("success")]
        objectives = [r["objective"] for r in good]
        groups[group] = dict(converged_objectives=objectives,
            best_objective=min(objectives) if objectives else None,
            reaches_selected=bool(objectives and min(objectives)-best <= tolerance),
            failed_labels=[r["label"] for r in all_group if not r.get("success")],
            Pd_values_bar=[r["final_parameters"]["Pd_bar"] for r in good],
            n_values=[r["final_parameters"]["n"] for r in good],
            **{key+"_range": [min(r["final_parameters"][key] for r in good),
                              max(r["final_parameters"][key] for r in good)] if good else None
               for key in ("Pd_bar", "n")})
    dependence = (groups["saved_onset_Pd"]["reaches_selected"] and
                  not groups["4.0_bar"]["reaches_selected"])
    return dict(groups=groups, selected_group=attempts[selected]["seed_group"],
                objective_tolerance=tolerance, rule4_start_dependence=dependence)


def endpoint_records(ctx, p, mc, arm, train, held):
    """Measured pressure histories only; no held-out onset input or prediction."""
    q, mass, cap = flow(p, ctx.brews.pressure, ctx.brews.t, mc, arm, False)
    if not all(np.isfinite(v).all() for v in (q, mass, cap)):
        raise FloatingPointError("Nonfinite endpoint evaluation")
    return [dict(brew=brew, condition_bar=float(ctx.brews.condition[i]),
        role="training" if i in train else "held_out" if i in held else "omitted",
        endpoint_pressure_bar=float(ctx.brews.pressure[i, -1]),
        endpoint_observed_g_s=float(ctx.brews.target[i]), endpoint_prediction_g_s=float(q[i, -1]),
        endpoint_residual_g_s=float(q[i, -1]-ctx.brews.target[i]),
        capacity_100_g_s=float(cap[i, -1]), hydraulic_mass_100_g=float(mass[i, -1]),
        memory_multiplier_100=float(np.exp(-np.exp(-mass[i, -1]/mc))))
        for i, brew in enumerate(ctx.brews.ids)]


def condition_records(records):
    return [dict(condition_bar=c, role=group[0]["role"], n=len(group),
        residual_g_s=float(np.mean([r["endpoint_residual_g_s"] for r in group])),
        prediction_g_s=float(np.mean([r["endpoint_prediction_g_s"] for r in group])),
        observed_g_s=float(np.mean([r["endpoint_observed_g_s"] for r in group])),
        zero_endpoints=sum(r["endpoint_prediction_g_s"] == 0 for r in group))
        for c in sorted({r["condition_bar"] for r in records})
        for group in [[r for r in records if r["condition_bar"] == c]]]


def reference_folds(ctx):
    """Three saved objectives replay first; omitted evaluations are plug-ins."""
    historical = C.read_table()
    rows = []
    for fold in FOLDS:
        source, train, held, omitted = C.design(ctx.brews.condition, fold)
        saved = ctx.saved[source]
        coef, mc = C1.flow_parameters(saved), saved["Mc_fixed_g"]
        parts = []
        for grid in (ctx.coarse, ctx.fine):
            q = C1.flow_curve(coef, grid.pressure[train], grid.t, mc)[0]
            parts.append(C.objective_parts(ctx.brews.condition[train],
                C.trace_mse(q, grid.flow[train], grid.mask[train])))
        replay = fold not in C.OMITTED
        if replay:
            np.testing.assert_allclose(parts[0]["objective"], saved["objective_sum_squares"],
                                       rtol=1e-12, atol=0)
        if fold == "DESCRIPTIVE_ALL":
            np.testing.assert_allclose(parts[0]["objective"], .0719361259858887,
                                       rtol=1e-12, atol=0)
        print("T2F_REFERENCE", fold, parts[0]["objective"], "replay" if replay else "plug-in", flush=True)
        prior = next(r for r in historical if r["record_type"] == "reference" and r["fold"] == fold)
        rows.append(dict(record_type="reference", candidate="T2-F", fold=fold, source_fold=source,
            reference_kind="replay" if replay else "reduced-training plug-in; not refitted",
            saved_objective=saved["objective_sum_squares"] if replay else None,
            parameters=saved, training_indices=train, held_out_indices=held, omitted_indices=omitted,
            objective=parts[0], fine_objective=parts[1], brew_predictions=prior["brew_predictions"],
            condition_predictions=condition_records(prior["brew_predictions"]),
            onset_label="Historical C2/C3c predictions only; no C3d onset prediction"))
    return D.plain(rows)


def comparators():
    return [dict(record_type="comparator", candidate=r["candidate"], fold=r["fold"],
        parameters=r["parameters"], brew_predictions=r["brew_predictions"],
        condition_predictions=condition_records(r["brew_predictions"]),
        source="Committed C3c; no refit") for r in C.read_table()
        if r["record_type"] == "fit" and r["fold"] in FOLDS]


class UnresolvedFit(RuntimeError):
    def __init__(self, row):
        super().__init__(f"Stopped: {row['candidate']} {row['fold']}; owner review required")
        self.row = D.plain(row)


def fit_fold(ctx, arm, fold, reference, budget, work):
    source, train, held, omitted = C.design(ctx.brews.condition, fold)
    saved, g = ctx.saved[source], ctx.coarse
    mc = saved["Mc_fixed_g"]
    lo, hi = bounds(arm)
    evaluate = training_evaluator(ctx, arm, fold, budget)
    ids = [ctx.brews.ids[i] for i in train]
    row = dict(record_type="fit", candidate=arm, fold=fold, source_fold=source,
        parameter_count=len(lo), eligibility="EXPLORATORY" if arm != "B-W3" else "DIAGNOSTIC ONLY",
        exposure="TARGET_EXPOSED retrospective sequence" if arm == "A" else
                 "TARGET_EXPOSED: full-cohort onset Pd used held-out onset times; diagnostic only",
        Pd_provenance="free flow parameter" if arm == "A" else "DESCRIPTIVE_ALL onset fit",
        onset_seed_Pd_bar=saved["Pd_bar"], Mc_fixed_g=mc,
        training_indices=train, held_out_indices=held, omitted_indices=omitted, training_brews=ids,
        starts=[], fallback=None, status="running")
    attempt_path = work / f"{arm}-{fold}-attempts.json"

    def save():
        attempt_path.write_text(json.dumps(D.plain(row), allow_nan=False)+"\n")

    def counts(p):
        shape, pd = split(p, arm)
        return C.zero_capacity(shape, g.pressure[train], g.mask[train], pd, ctx.brews.condition[train], ids)

    def kinks(p):
        return C.kink_counts(split(p, arm)[0], g.pressure[train], g.mask[train], ids)

    def attempt(start, label, group, fallback=False):
        original = np.array(start, copy=True) if fallback else coordinates(start, arm)
        z = original.copy() if fallback else np.clip(original, lo+1e-10, hi-1e-10)
        p = physical(z, arm)
        record = dict(label=label, seed_group=group, original_start_coordinates=original,
            initial_coordinates=z, initial_parameters=parameter_record(p, arm, mc),
            initial_bounds=bound_record(z, arm), initial_training_counts=counts(p),
            initial_kink_counts=kinks(p))
        if fallback:
            row["fallback"] = record
        else:
            row["starts"].append(record)
        save()
        started = time.monotonic()
        try:
            initial = evaluate(z)[0]
            record["initial_objective"] = float(initial@initial)
            if arm == "B-W4" and (fallback or start[2] == 1.):
                record["initial_jacobian_check"] = jacobian_diagnostic(evaluate, z, lo, hi)
            if arm == "B-W4" and label == "start-2" and record["initial_training_counts"]["structural"]:
                raise RuntimeError("P0=0,n=2 safeguard unexpectedly structurally censored")
            fit = least_squares(lambda v: evaluate(v)[0], z, jac=lambda v: evaluate(v)[1],
                bounds=(lo, hi), method="dogbox" if fallback else "trf", x_scale="jac",
                ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500 if fallback else 500)
            if not np.isfinite(fit.cost) or not np.isfinite(fit.x).all():
                raise FloatingPointError("Nonfinite optimizer result")
            final = physical(fit.x, arm)
            record.update(final_coordinates=fit.x, final_parameters=parameter_record(final, arm, mc),
                objective=float(2*fit.cost), success=bool(fit.success), message=fit.message,
                nfev=fit.nfev, njev=fit.njev, active_mask=fit.active_mask,
                final_bounds=bound_record(fit.x, arm, fit.active_mask),
                final_training_counts=counts(final), final_kink_counts=kinks(final))
        except Exception as exc:
            record.update(success=False, error=f"{type(exc).__name__}: {exc}")
            row["status"] = "unresolved"
            raise UnresolvedFit(row) from exc
        finally:
            record["wall_seconds"] = time.monotonic()-started
            save()
        return fit

    fits = []
    for i, (group, start) in enumerate(start_values(arm, saved)):
        fit = attempt(start, f"start-{i+1}", group)
        fits.append(fit)
        print("START", arm, fold, i+1, group, fit.success, 2*fit.cost, flush=True)
    valid = [(i, r) for i, r in enumerate(fits) if r.success]
    if not valid:
        seed = min(range(len(fits)), key=lambda i: fits[i].cost)
        retry = attempt(fits[seed].x, "dogbox fallback", row["starts"][seed]["seed_group"], True)
        row["fallback"]["source_start"] = seed
        if retry.success:
            valid = [(len(fits), retry)]
        else:
            row["status"] = "unresolved"
            save()
            raise UnresolvedFit(row)
    selected, best = min(valid, key=lambda pair: pair[1].cost)
    p = physical(best.x, arm)
    try:
        parts = []
        for grid in (ctx.coarse, ctx.fine):
            q = flow(p, grid.pressure[train], grid.t, mc, arm, False)[0]
            if not np.isfinite(q).all():
                raise FloatingPointError("Nonfinite grid evaluation")
            parts.append(C.objective_parts(ctx.brews.condition[train],
                C.trace_mse(q, grid.flow[train], grid.mask[train])))
        np.testing.assert_allclose(parts[0]["objective"], 2*best.cost, rtol=1e-12, atol=0)
        records = endpoint_records(ctx, p, mc, arm, train, held)
        diagnostic = jacobian_diagnostic(evaluate, best.x, lo, hi)
    except Exception as exc:
        row.update(status="unresolved", error=f"{type(exc).__name__}: {exc}")
        save()
        raise UnresolvedFit(row) from exc
    attempts = row["starts"]+([row["fallback"]] if row["fallback"] else [])
    objectives = [r["objective"] for r in attempts]
    gain = reference["objective"]["objective"]-parts[0]["objective"]
    fine_gain = reference["fine_objective"]["objective"]-parts[1]["objective"]
    row.update(status="complete", parameters=parameter_record(p, arm, mc), selected_start=selected,
        objective=parts[0], fine_objective=parts[1], brew_predictions=records,
        condition_predictions=condition_records(records), jacobian_check=diagnostic,
        selected_bounds=bound_record(best.x, arm, best.active_mask),
        selected_training_counts=counts(p), selected_kink_counts=kinks(p),
        start_disagreement=max(objectives)-min(objectives) > 1e-6*max(1., 2*best.cost),
        parameter_ranges={k: [min(r["final_parameters"][k] for r in attempts),
                              max(r["final_parameters"][k] for r in attempts)]
                          for k in ("a_g_s_bar", "Pstar_bar", "n", "P0_bar", "Pd_bar")},
        coarse_gain_vs_T2F=gain, fine_gain_vs_T2F=fine_gain,
        grid_gain_unresolved=bool(gain > 0 and (fine_gain <= 0 or abs(gain-fine_gain) >= gain)),
        plateau_label="possible flat-gradient dependence" if counts(p)["total"] else "none")
    if arm == "A":
        row["seed_audit"] = seed_groups(attempts, selected)
        row["Pd_comparisons"] = {name: dict(reference_Pd_bar=ref, difference_bar=p[3]-ref, ratio=p[3]/ref)
                                for name, ref in (("matching_onset", saved["Pd_bar"]),
                                                  ("full_cohort_onset", FIXED_PD))}
    save()
    return D.plain(row)


def helps(residual, t2f, c3c):
    return dict(helps=bool(abs(residual) < abs(t2f) and abs(residual) < abs(c3c)),
                reduction_vs_T2F_g_s=abs(t2f)-abs(residual),
                reduction_vs_C3c_g_s=abs(c3c)-abs(residual))


def held_residual(row):
    return next(r["residual_g_s"] for r in row["condition_predictions"] if r["role"] == "held_out")


def reading(fits, references, prior):
    rows, flags = [], {}
    for arm in ("A", "B-W3", "B-W4"):
        form = "W4" if arm == "B-W4" else "W3"
        checks = []
        for fold in HELD[:2]:
            fit = next(r for r in fits if r["candidate"] == arm and r["fold"] == fold)
            twin = next(r for r in fits if r["candidate"] == arm and r["fold"] == fold+"-OMIT-3.5")
            ref = next(r for r in references if r["fold"] == fold)
            old = next(r for r in prior if r["candidate"] == form and r["fold"] == fold)
            old_twin = next(r for r in prior if r["candidate"] == form and r["fold"] == twin["fold"])
            new, base, former = map(held_residual, (fit, ref, old))
            check = helps(new, base, former)
            checks.append(check["helps"])
            rows.append(dict(record_type="held_out_comparison", candidate=arm, fold=fold,
                residual_g_s=new, T2F_residual_g_s=base, C3c_residual_g_s=former, **check,
                omitted_residual_g_s=held_residual(twin),
                omission_change_g_s=held_residual(twin)-new,
                C3c_omitted_residual_g_s=held_residual(old_twin),
                grid_gain_unresolved=fit["grid_gain_unresolved"],
                start_disagreement=fit["start_disagreement"],
                rule4_start_dependence=fit.get("seed_audit", {}).get("rule4_start_dependence")))
        flags[arm] = all(checks)
    b_forms = [arm for arm in ("B-W3", "B-W4") if flags[arm]]
    if flags["A"] and b_forms:
        interpretation = "A and "+", ".join(b_forms)+" fix both: mainly Pd transfer within this screen."
    elif b_forms:
        interpretation = "Only "+", ".join(b_forms)+" fix both: held-out onset information helps; weaker diagnostic result."
    elif flags["A"]:
        interpretation = "Only A fixes both: freeing flow Pd helps; the specified full-cohort fixed value does not."
    elif any(r["helps"] for r in rows):
        interpretation = "Partial improvements only; no arm/form fixes both. Rule 1 does not resolve a unique cause."
    else:
        interpretation = "Neither arm helps: the tested flow family is the limit within this screen."
    rows.append(dict(record_type="interpretation", fixes_by_arm=flags, B_fixing_forms=b_forms,
        rule1_reading=interpretation,
        qualifications="Fixed Mc, objective and prescribed starts; not proof of a unique physical cause. "
        "Arm B is target-exposed and cannot count as held-out capability."))
    return rows


def numerical_fixtures(budget):
    t = np.array([0., .5, 1., 2., 5., 20., 100.])
    pressure = np.array([[0., .5, 1., 1.1, 1.4, 2., 2.5], [2., 3., 4., 5., 7., 9., 13.]])
    for pd in (.1, 4., 100.):
        p = np.array([1.2, 12.2, 1., pd])
        q, jac = flow(p, pressure, t, 28.7, "A")
        ref, rjac = C1.flow_curve([p[0], p[1], 0., pd], pressure, t, 28.7)
        np.testing.assert_allclose(q, ref, rtol=1e-12, atol=0)
        np.testing.assert_allclose(jac[..., [0, 1, 3]], rjac[..., [0, 1, 3]], rtol=1e-12, atol=0)
        for n in (1., 2., 4.):
            p[2] = n
            q, jac = flow(p, pressure, t, 28.7, "A")
            ref, rjac = C.flow(p[:3], pressure, t, pd, 28.7)
            np.testing.assert_allclose(q, ref, rtol=1e-12, atol=0)
            np.testing.assert_allclose(jac[..., :3], rjac, rtol=1e-12, atol=0)
    p = np.array([1.2, 12.2, 2.3, 4.])
    evaluate = Evaluator(pressure, t, np.zeros_like(pressure), np.ones_like(pressure, dtype=bool),
                         np.array([1., 2.]), 28.7, "A", budget)
    check = jacobian_diagnostic(evaluate, coordinates(p, "A"), *bounds("A"))
    if not check["half_step_error_decreases"]:
        raise RuntimeError("Smooth synthetic Jacobian halving needs investigation before fits")
    c, dc = capacity([1., 12., 1e200, 4.], np.array([0., 2., 4., 8., 1e200]), "A")
    if not np.isfinite(np.r_[c, dc.ravel()]).all():
        raise FloatingPointError("Nonfinite synthetic large-power limit")
    np.testing.assert_allclose(dc[0], 0., rtol=1e-12, atol=0)
    return dict(record_type="numerical_fixtures", nested_replays=True, smooth_jacobian=check,
                large_power_capacity=c, large_power_jacobian=dc)


def source_hashes(raw, cache, ids):
    sources = C.source_hashes(raw, cache, ids)
    for path in (Path(__file__), OUT / "PLAN.md", C.OUT / "RESULT_TABLE.csv"):
        sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if sources[str((OUT / "PLAN.md").relative_to(ROOT))] != PLAN_SHA256:
        raise RuntimeError("Approved plan changed")
    return sources


def write_summary(rows, path):
    comparisons = [r for r in rows if r["record_type"] == "held_out_comparison"]
    fits = [r for r in rows if r["record_type"] == "fit"]
    interpretation = next(r for r in rows if r["record_type"] == "interpretation")
    provenance = next(r for r in rows if r["record_type"] == "provenance")
    lines = ["# PRESSURE-PEAK C3d: Pd transfer", "",
        "**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.**",
        "Ungraded Python screen. Arm B uses held-out onset times through its fixed full-cohort Pd; it is diagnostic only.",
        "Arm A uses no fixed onset Pd or onset loss. Training onsets enter its masks and saved-Pd starts, never held-out onset times.", "",
        interpretation["rule1_reading"], interpretation["qualifications"], "",
        "## Held-out endpoint flow", "",
        "Signed residuals are prediction minus observation, g/s. Strict helps flags use both references; twins are separate sensitivity tests.", "",
        "| Arm | Held bar | T2-F | C3c same form | C3d | Helps | 3.5 omitted | Omission change | C3c omitted |",
        "|---|---:|---:|---:|---:|---|---:|---:|---:|"]
    for r in comparisons:
        h = float(r["fold"].removeprefix("HYD-LOCO-"))
        lines.append(f"| {r['candidate']} | {h:g} | {r['T2F_residual_g_s']:+.9f} | "
            f"{r['C3c_residual_g_s']:+.9f} | {r['residual_g_s']:+.9f} | {r['helps']} | "
            f"{r['omitted_residual_g_s']:+.9f} | {r['omission_change_g_s']:+.9f} | {r['C3c_omitted_residual_g_s']:+.9f} |")
    lines += ["", "Fixes both ordinary held-out conditions: "+", ".join(
        f"{a}={v}" for a, v in interpretation["fixes_by_arm"].items())+".", "",
        "Unrounded reductions in absolute error (T2-F, C3c), with numerical qualifications:"]
    for r in comparisons:
        lines.append(f"- {r['candidate']} {r['fold']}: ({r['reduction_vs_T2F_g_s']!r}, "
            f"{r['reduction_vs_C3c_g_s']!r}); grid gain unresolved={r['grid_gain_unresolved']}; "
            f"start disagreement={r['start_disagreement']}; rule-4 start dependence={r['rule4_start_dependence']}.")
    lines += ["", "## Free Pd and the seed groups", "",
        "Ranges below cover converged starts, not confidence intervals. All parameters, bounds, failures and every initial/final start are in RESULT_TABLE.csv.", "",
        "| A fit | Selected Pd | n | Pd minus / divided by onset Pd | Selected group | Saved-onset seed Pd range | 4.0-bar seed Pd range | Rule-4 dependence |",
        "|---|---:|---:|---|---|---|---|---|"]
    for r in fits:
        if r["candidate"] != "A":
            continue
        audit, p = r["seed_audit"], r["parameters"]
        groups = audit["groups"]
        delta = r["Pd_comparisons"]["matching_onset"]
        ranges = [groups[g]["Pd_bar_range"] for g in ("saved_onset_Pd", "4.0_bar")]
        lines.append(f"| {r['fold']} | {p['Pd_bar']:.9f} | {p['n']:.9f} | "
            f"{delta['difference_bar']:+.9f} / {delta['ratio']:.9f} | {audit['selected_group']} | "
            f"{ranges[0]} | {ranges[1]} | {audit['rule4_start_dependence']} |")
    for r in fits:
        if r["candidate"] == "A":
            parts = []
            for group, v in r["seed_audit"]["groups"].items():
                parts.append(f"{group}: Pd={v['Pd_values_bar']}, n={v['n_values']}, "
                    f"J={v['converged_objectives']}, best J={v['best_objective']!r}, "
                    f"reaches selected={v['reaches_selected']}, failed={v['failed_labels']}")
            full = r["Pd_comparisons"]["full_cohort_onset"]
            lines += ["", f"{r['fold']}: "+"; ".join(parts)+".",
                f"Selected Pd minus / divided by 3.9844972419062152: {full['difference_bar']!r} / {full['ratio']!r}."]
    lines += ["", "## Numerical qualifications", "",
        "A bound or disagreement across starts prevents identifying Pd as a scale. Equal objectives do not erase parameter spread.",
        "Censoring counts mean zero capacity throughout a masked training trace. Structural zeros and numerical underflow are separate in the table.", "",
        "| Arm / fit | Start disagreement | Selected near bounds | Training zeros | FD relative error h / h/2 | Branch switches h / h/2 | Grid gain unresolved |",
        "|---|---|---|---:|---|---|---|"]
    for r in fits:
        j = r["jacobian_check"]
        near = [k for k, v in r["selected_bounds"].items() if v["near_finite_bound"] or v["active"]]
        lines.append(f"| {r['candidate']} / {r['fold']} | {r['start_disagreement']} | {near} | "
            f"{r['selected_training_counts']['total']} | {j['full_relative_error']:.6g} / {j['half_relative_error']:.6g} | "
            f"{j['full_branch_switches']} / {j['half_branch_switches']} | {r['grid_gain_unresolved']} |")
    full = next(r for r in fits if r["fold"] == "DESCRIPTIVE_ALL")
    lines += ["", "DESCRIPTIVE_ALL A is in-sample. Its 1/2/3.5-bar residuals are "+
        "/".join(f"{r['residual_g_s']:+.9f}" for r in full["condition_predictions"] if r["condition_bar"] in (1., 2., 3.5))+
        " g/s. These describe the fitted cohort; they do not show held-out prediction.",
        "Condition loss components and shares beside T2-F are in the table. Absolute-flow loss gives low-flow conditions little weight; it was not reweighted.",
        "No new onset prediction, high-pressure held-out result or scale-consistency claim is made.", "",
        "## Execution and evidence", "",
        "T2-F DESCRIPTIVE_ALL and both ordinary held-out objectives replayed first with assert_allclose(rtol=1e-12, atol=0). "
        "The full-cohort objective is 0.0719361259858887. Reduced-support references are plug-ins.",
        f"{provenance['fit_count']} fits / {provenance['start_count']} prescribed starts; "
        f"{provenance['fallback_count']} inherited fallbacks. Cumulative execution and check time at report generation: "
        f"{provenance['cumulative_wall_seconds']:.3f} s of 7200 s. Serial, one BLAS thread.",
        "Source hashes, exact training indices, inherited Mc, endpoint records and reproduction inputs are in RESULT_TABLE.csv. "
        "Earlier stage modules and source data are unchanged. The approved PLAN.md is unchanged.", ""]
    path.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--onset-cache", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    with D.timed_attempt(args.work) as budget:
        ctx = D.load_context(args.raw, args.onset_cache)
        sources = source_hashes(args.raw, args.onset_cache, ctx.brews.ids)
        references = reference_folds(ctx)
        fixtures, prior = numerical_fixtures(budget), comparators()
        rows = [*references, C.input_fixture(ctx), D.plain(fixtures), *prior]
        checkpoint, identity = args.work / "completed-fits.json", args.work / "fit-sources.json"
        if args.report_only:
            if json.loads(identity.read_text()) != sources:
                raise RuntimeError("Fit sources changed; cannot report a different calculation")
            fits = json.loads(checkpoint.read_text())
            if [(r["candidate"], r["fold"]) for r in fits] != list(SCHEDULE):
                raise RuntimeError("Incomplete fit schedule; owner review required")
            if any(r["status"] != "complete" for r in fits):
                raise RuntimeError("Unresolved fit; owner review required")
        else:
            if checkpoint.exists() or identity.exists():
                raise RuntimeError("Existing fit attempt: no automatic repetition; owner review required")
            identity.write_text(json.dumps(sources, indent=2)+"\n")
            fits = []
            for arm, fold in SCHEDULE:
                reference = next(r for r in references if r["fold"] == fold)
                try:
                    fit = fit_fold(ctx, arm, fold, reference, budget, args.work)
                except UnresolvedFit as exc:
                    D.write_table([*rows, *fits, exc.row], args.out / "RESULT_TABLE.csv")
                    (args.out / "SUMMARY.md").write_text("# C3d stopped\n\n"+D.CLAIM+
                        ". Ungraded.\n\n"+str(exc)+". No later fits or retuning.\n")
                    raise
                fits.append(fit)
                checkpoint.write_text(json.dumps(fits, allow_nan=False)+"\n")
                print("FIT_COMPLETE", arm, fold, fit["parameters"], flush=True)
        rows += [*fits, *reading(fits, references, prior)]
        if sources != source_hashes(args.raw, args.onset_cache, ctx.brews.ids):
            raise RuntimeError("Sources changed during execution")
        rows.append(dict(record_type="provenance", source_sha256=sources,
            source_base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            plan_sha256=PLAN_SHA256, python=sys.version, cumulative_wall_seconds=budget.cumulative,
            prior_attempt_seconds=budget.prior, cap_seconds=7200, execution="serial; one BLAS thread",
            fit_count=len(fits), start_count=sum(len(r["starts"]) for r in fits),
            fallback_count=sum(r["fallback"] is not None for r in fits),
            bootstrap_count=0, onset_refits=0, report_only=args.report_only))
        budget.check()
        D.write_table(rows, args.out / "RESULT_TABLE.csv")
        write_summary(D.plain(rows), args.out / "SUMMARY.md")
        print("COMPLETE", budget.cumulative, "cumulative seconds", flush=True)


if __name__ == "__main__":
    main()

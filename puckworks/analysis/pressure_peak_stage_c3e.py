"""C3e retrospective screen: capability demonstration, not validation.

PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED. The owner approved
PLAN.md at c5597403. Earlier helpers and the scientific plan stay unchanged.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.optimize import brentq, least_squares

from . import pressure_peak_stage_c3d as S

C, D = S.C, S.D
ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs/research/PRESSURE_PEAK_STAGE_C3E"
PLAN_SHA256 = "4dd98413d5187459bf0b8d6df2659309468a8efd7fc3c58df4a468a32e1108bc"
FORMS = ("A", "M1", "M2", "LC")
FOLDS = (*C.STANDARD, *C.OMITTED)
SCHEDULE = tuple((form, fold) for form in FORMS for fold in FOLDS)
SERIES = np.array([1/(k*math.factorial(k)) for k in range(1, 20)])


def read_table(path=OUT / "RESULT_TABLE.csv"):
    return D.read_table(path)


def coordinates(p, form):
    z = np.asarray(p, dtype=float).copy()
    z[[0, 1, 3]] = np.log(z[[0, 1, 3]])
    return z


def physical(z, form):
    p = np.asarray(z, dtype=float).copy()
    p[[0, 1, 3]] = np.exp(p[[0, 1, 3]])
    return p


def bounds(form):
    lo, hi = S.bounds("A")
    if form in ("M2", "LC"):
        lo, hi = np.r_[lo, 0.], np.r_[hi, 10. if form == "M2" else 1.]
    return lo, hi


def start_values(form, saved):
    starts = S.start_values("A", saved)
    if form in ("M2", "LC"):
        starts = [(group, [*p, extra]) for group, p in starts
                  for extra in (0., .3 if form == "M2" else .1)]
    return starts


def parameter_record(p, form, mc):
    result = S.parameter_record(p[:4], "A", mc)
    if form in ("M2", "LC"):
        result["v_g_s" if form == "M2" else "f"] = float(p[4])
    if form == "M2":
        result["Mc_over_v_s"] = float(mc/p[4]) if p[4] else "infinity"
    return result


def parameters(record, form):
    p = S.parameters(record, "A")
    if form in ("M2", "LC"):
        p = np.r_[p, record["v_g_s" if form == "M2" else "f"]]
    return p


def capacity(p, pressure, form):
    c, dc = S.capacity(p[:4], pressure, "A")
    if form == "M2":
        dc = np.concatenate((dc, np.zeros_like(c)[..., None]), axis=-1)
    if form == "LC":
        linear = np.array(p[:4], copy=True)
        linear[2] = 1.
        c1, d1 = S.capacity(linear, pressure, "A")
        d1[..., 2] = 0.
        dc = np.concatenate(((1-p[4])*dc+p[4]*d1, (c1-c)[..., None]), axis=-1)
        c = (1-p[4])*c+p[4]*c1
    return c, dc


@C.B.njit(cache=True)
def _primitive(x):
    result = x
    for k in range(1, 20):
        result -= np.expm1(-k*x)*SERIES[k-1]
    return result


@C.B.njit(cache=True)
def _inverse(exposure):
    # Same series and eight Newton steps as stage A's delivered_state.
    x = exposure
    for _ in range(8):
        x = max(0., x-(_primitive(x)-exposure)/np.exp(np.exp(-x)))
    return x


@C.B.njit(cache=True)
def _clock_state(cap, dc, t, mc, v):
    """Symmetric clock/exposure splitting, with analytic discrete sensitivities.

    Each full step uses the inherited trapezoid capacity exposure. Clock
    half-steps advance X; the exact exposure map advances X and M together.
    No scoring mask is accepted, so censoring cannot pause the state.
    """
    nb, nt = cap.shape
    mass, state = np.zeros_like(cap), np.zeros_like(cap)
    sensitivity = np.zeros_like(dc)
    for i in range(nb):
        x, m = 0., 0.
        dx = np.zeros(5)
        for j in range(1, nt):
            dt = t[j]-t[j-1]
            before = x+v*dt/(2*mc)
            dx[4] += dt/(2*mc)
            exposure = (cap[i, j-1]+cap[i, j])*dt/(2*mc)
            after = before if exposure == 0. else _inverse(_primitive(before)+exposure)
            r0, r1 = np.exp(-np.exp(-before)), np.exp(-np.exp(-after))
            for k in range(5):
                di = (dc[i, j-1, k]+dc[i, j, k])*dt/(2*mc)
                dx[k] = r1*(dx[k]/r0+di)
            m += mc*(after-before)
            x = after+v*dt/(2*mc)
            dx[4] += dt/(2*mc)
            mass[i, j], state[i, j] = m, x
            sensitivity[i, j] = dx
    return mass, state, sensitivity


def flow(p, pressure, t, mc, form, jacobian=True):
    p, t = np.asarray(p, dtype=float), np.asarray(t, dtype=float)
    c, dc = capacity(p, pressure, form)
    if form == "A":
        return S.flow(p, pressure, t, mc, "A", jacobian)
    integral = np.zeros_like(dc)
    integral[..., 1:, :] = np.cumsum((dc[..., :-1, :]+dc[..., 1:, :])*np.diff(t)[:, None]/2,
                                    axis=-2)
    if form == "M2":
        mass, state, ds = _clock_state(c, dc, t, mc, p[4])
        r = np.exp(-np.exp(-state))
        q = c*r
        jac = dc*r[..., None]+(q*np.exp(-state))[..., None]*ds
        if p[4] == 0.:
            # Preserve the inherited arithmetic at the exact nested boundary.
            q, mass, _ = S.flow(p[:4], pressure, t, mc, "A", False)
            jac[..., :4] = S.flow(p[:4], pressure, t, mc, "A")[1]
    elif form == "M1":
        exposure = np.zeros_like(c)
        exposure[..., 1:] = np.cumsum((c[..., :-1]+c[..., 1:])*np.diff(t)/2, axis=-1)/mc
        # exp(M/Mc) = (1-e^-1) + exp(exposure-1), evaluated without overflow.
        state = np.empty_like(exposure)
        finite_exp = exposure < np.log(np.finfo(float).max)
        state[finite_exp] = np.log1p(np.expm1(exposure[finite_exp])/np.e)
        state[~finite_exp] = exposure[~finite_exp]-1.+np.log1p((np.e-1)*np.exp(-exposure[~finite_exp]))
        mass = mc*state
        r = 1-(1-np.exp(-1.))*np.exp(-state)
        q = c*r
        jac = dc*r[..., None]+(q*(1-r)/mc)[..., None]*integral
    else:
        q, mass = D.mass_flow(c, t, mc)
        inner = np.exp(-mass/mc)
        r = np.exp(-inner)
        jac = dc*r[..., None]+(q*inner*r/mc)[..., None]*integral
    if not all(np.isfinite(v).all() for v in (q, mass, c, jac)):
        raise FloatingPointError("Nonfinite flow/state/Jacobian evaluation")
    return (q, jac) if jacobian else (q, mass, c)


class Evaluator(S.Evaluator):
    def __call__(self, z):
        self.budget.check()
        lo, hi = bounds(self.arm)
        if not np.isfinite(z).all() or np.any(z < lo) or np.any(z > hi):
            raise ValueError("Evaluation outside declared domain")
        if self.last_z is None or not np.array_equal(self.last_z, z):
            q, jac = flow(physical(z, self.arm), self.pressure, self.t, self.mc, self.arm)
            value = (((q-self.target)*self.weight).ravel(),
                     (jac*self.weight[..., None]).reshape(-1, len(z)))
            if not all(np.isfinite(v).all() for v in value):
                raise FloatingPointError("Nonfinite evaluation: stop for owner review")
            self.last_z, self.last = z.copy(), value
        return self.last


def training_evaluator(ctx, form, fold, budget):
    source, train, _, _ = C.design(ctx.brews.condition, fold)
    g = ctx.coarse
    return Evaluator(g.pressure[train], g.t, g.flow[train], g.mask[train],
                     ctx.brews.condition[train], ctx.saved[source]["Mc_fixed_g"], form, budget)


def source_hashes(raw, cache, ids):
    sources = S.source_hashes(raw, cache, ids)
    historical = next(r for r in S.read_table() if r["record_type"] == "provenance")["source_sha256"]
    for key, expected in historical.items():
        if sources.get(key) != expected:
            raise RuntimeError(f"C3d source authentication failed: {key}")
    for path in (Path(__file__), OUT/"PLAN.md", S.OUT/"RESULT_TABLE.csv"):
        sources[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    if sources[str((OUT/"PLAN.md").relative_to(ROOT))] != PLAN_SHA256:
        raise RuntimeError("Approved C3e plan changed")
    return sources


def replay_c3d(ctx):
    records = []
    for row in S.read_table():
        if row["record_type"] != "fit" or row["candidate"] != "A":
            continue
        _, train, _, _ = C.design(ctx.brews.condition, row["fold"])
        p, mc = parameters(row["parameters"], "A"), row["Mc_fixed_g"]
        q = flow(p, ctx.coarse.pressure[train], ctx.coarse.t, mc, "A", False)[0]
        obj = C.objective_parts(ctx.brews.condition[train],
                               C.trace_mse(q, ctx.coarse.flow[train], ctx.coarse.mask[train]))
        np.testing.assert_allclose(obj["objective"], row["objective"]["objective"], rtol=1e-12, atol=0)
        endpoint = flow(p, ctx.brews.pressure, ctx.brews.t, mc, "A", False)[0][:, -1]
        np.testing.assert_allclose(endpoint, [b["endpoint_prediction_g_s"] for b in row["brew_predictions"]],
                                   rtol=1e-12, atol=0)
        records.append(dict(fold=row["fold"], parameters=row["parameters"], objective=obj["objective"],
                            endpoint_predictions_g_s=endpoint))
        print("C3D_A_REPLAY", row["fold"], obj["objective"], flush=True)
    if len(records) != 5:
        raise RuntimeError("C3d replay coverage differs")
    return D.plain(dict(record_type="c3d_replay", fits=records))


def numerical_fixtures(budget):
    t = np.linspace(0., 100., 201)
    pressure = np.array([1+np.sin(t/20)/5, 4+np.sin(t/10)])
    checks = {}
    for n in (1., 2., 4.):
        p = np.array([1.2, 12.2, n, 4.])
        for form in ("M2", "LC"):
            base = flow(p, pressure, t, 28.7, "A")
            nested = flow(np.r_[p, 0.], pressure, t, 28.7, form)
            np.testing.assert_allclose(nested[0], base[0], rtol=1e-12, atol=0)
            np.testing.assert_allclose(nested[1][..., :4], base[1], rtol=1e-12, atol=0)
    for form in FORMS:
        p = [1.2, 12.2, 2.3, 4.]+([.3] if form == "M2" else [.1] if form == "LC" else [])
        e = Evaluator(pressure, t, np.zeros_like(pressure), np.ones_like(pressure, dtype=bool),
                      np.array([1., 2.]), 28.7, form, budget)
        checks[form] = S.jacobian_diagnostic(e, coordinates(p, form), *bounds(form))
        if not checks[form]["half_step_error_decreases"]:
            raise RuntimeError(f"{form} smooth synthetic Jacobian halving needs investigation")
    # Exact pure clock and LC degeneracies, including zero pressure.
    zero = np.zeros((1, len(t)))
    p = np.array([1.2, 12.2, 2., 4., .3])
    q, m, _ = flow(p, zero, t, 28.7, "M2", False)
    np.testing.assert_allclose(q, 0., rtol=1e-12, atol=0)
    # Zero capacity must deliver exactly zero mass, including internal steps.
    np.testing.assert_allclose(m, 0., rtol=1e-12, atol=0)
    for n, f in ((1., .2), (1., 1.), (3., 1.)):
        p = [1.2, 12.2, n, 4., f]
        linear = flow([1.2, 12.2, 1., 4.], pressure, t, 28.7, "A")[0]
        np.testing.assert_allclose(flow(p, pressure, t, 28.7, "LC")[0], linear, rtol=1e-12, atol=0)
    for form in FORMS:
        p = [1., 12., 1e200, 4.]+([10.] if form == "M2" else [1.] if form == "LC" else [])
        c, dc = capacity(p, np.array([0., 2., 4., 8., 1e200]), form)
        if not np.isfinite(np.r_[c, dc.ravel()]).all():
            raise FloatingPointError(f"{form} nonfinite large-power limit")
    return D.plain(dict(record_type="numerical_fixtures", nested_identities=True,
                        smooth_jacobians=checks, exact_zero_clock=True))


def bound_record(z, form, active=None):
    result = S.bound_record(z[:4], "A", None if active is None else active[:4])
    if len(z) == 5:
        upper = 10. if form == "M2" else 1.
        fraction = min(z[4], upper-z[4])/upper
        result["v" if form == "M2" else "f"] = dict(lower_distance=float(z[4]),
            upper_distance=float(upper-z[4]), fraction_of_range=float(fraction),
            near_finite_bound=bool(fraction <= 1e-6), active=int(active[4]) if active is not None else None)
    return result


def zero_counts(p, form, pressure, mask, conditions, ids):
    c = capacity(p, pressure, form)[0]
    zero = np.all((c == 0) | ~mask, axis=1)
    structural = np.all((pressure <= 0) | ~mask, axis=1)
    numerical = zero & ~structural
    return dict(total=int(sum(zero)), structural=int(sum(structural)), numerical=int(sum(numerical)),
        brew_ids=[b for b, flag in zip(ids, zero) if flag],
        by_condition={str(float(c)): dict(total=int(sum(zero[conditions == c])),
            structural=int(sum(structural[conditions == c])), numerical=int(sum(numerical[conditions == c])))
            for c in np.unique(conditions)})


def global_peak(p, form):
    """Isolate every LC stationary point using bounds on its derivative.

    h_n' - h_n/Pstar is unimodal: its derivative changes sign when
    n-1-n*(P/Pd)**n-P/Pstar=0. The linear term decreases throughout.
    Their exact interval ranges bound the mixture derivative and allow
    root exclusion. All mixture stationary points lie between the two
    component peaks. The inherited root-location tolerance is 1e-12 bar.
    """
    p = np.asarray(p)
    a, star, n, pd = p[:4]
    upper = pd
    while C.log_slope(p[:3], upper, pd) > 0:
        upper *= 2
    pn = brentq(lambda x: C.log_slope(p[:3], x, pd), np.nextafter(0., 1.), upper, xtol=1e-12)
    pl = pd*np.log1p(star/pd)
    f = p[4] if form == "LC" else 0.
    if f == 0 or n == 1 or f == 1:
        roots = [pl if f == 1 or n == 1 else pn]
    else:
        turn = brentq(lambda x: n-1-n*(x/pd)**n-x/star, 0., pd, xtol=1e-12)

        def components(x):
            h, _, hx = C.opening(np.array([x/pd]), n)
            gn = hx[0]/pd-h[0]/star
            g1 = np.exp(-x/pd)/pd+np.expm1(-x/pd)/star
            return gn, g1

        def derivative(x):
            gn, g1 = components(x)
            return (1-f)*gn+f*g1

        pending, roots = [(min(pl, pn), max(pl, pn))], []
        while pending:
            left, right = pending.pop()
            nl, ll = components(left)
            nr, lr = components(right)
            high_n = components(turn)[0] if left < turn < right else max(nl, nr)
            lower = (1-f)*min(nl, nr)+f*lr
            higher = (1-f)*high_n+f*ll
            if lower > 0 or higher < 0:
                continue
            mid = (left+right)/2
            if right-left <= 1e-12 or mid in (left, right):
                dl, dr = derivative(left), derivative(right)
                roots.append(brentq(derivative, left, right, xtol=1e-12)
                             if dl*dr <= 0 else mid)
            else:
                pending.extend(((left, mid), (mid, right)))
        roots.sort()
        roots = [r for i, r in enumerate(roots) if i == 0 or r-roots[i-1] > 1e-12]
    candidates = [0., *roots]
    capacities = capacity(p, np.array(candidates), form)[0]
    j = int(np.argmax(capacities))
    return dict(pressure_bar=float(candidates[j]), capacity_g_s=float(capacities[j]),
                stationary_pressures_bar=roots, candidate_pressures_bar=candidates,
                candidate_capacities_g_s=capacities, infinite_pressure_capacity_g_s=0.,
                domain="P>=0; global capacity maximum")


def brew_records(ctx, p, mc, form, train, held):
    q, mass, cap = flow(p, ctx.brews.pressure, ctx.brews.t, mc, form, False)
    fine = flow(p, ctx.fine.pressure, ctx.fine.t, mc, form, False)[0]
    mse = C.trace_mse(fine, ctx.fine.flow, ctx.fine.mask)
    trends = (fine*ctx.fine.late_weights).sum(axis=1)
    records = []
    for i, brew in enumerate(ctx.brews.ids):
        x = mass[i, -1]+(p[4]*ctx.brews.t[-1] if form == "M2" else 0.)
        memory = (1-(1-np.exp(-1.))*np.exp(-x/mc) if form == "M1"
                  else np.exp(-np.exp(-x/mc)))
        records.append(dict(brew=brew, condition_bar=float(ctx.brews.condition[i]),
            role="training" if i in train else "held_out" if i in held else "omitted",
            endpoint_pressure_bar=float(ctx.brews.pressure[i, -1]),
            endpoint_observed_g_s=float(ctx.brews.target[i]), endpoint_prediction_g_s=float(q[i, -1]),
            endpoint_residual_g_s=float(q[i, -1]-ctx.brews.target[i]),
            capacity_100_g_s=float(cap[i, -1]), hydraulic_mass_100_g=float(mass[i, -1]),
            conditioning_X_100_g=float(x), clock_contribution_100_g=float(x-mass[i, -1]),
            memory_multiplier_100=float(memory), trace_mse=float(mse[i]),
            predicted_late_trend_g_s_s=float(trends[i]),
            observed_late_trend_g_s_s=float(ctx.fine.observed_trend[i])))
    return records


def metrics(records):
    cond = S.condition_records(records)
    high = [c for c in cond if c["condition_bar"] >= 9]
    group = {c["condition_bar"]: [r for r in records if r["condition_bar"] == c["condition_bar"]] for c in cond}
    pressure = [np.mean([r["endpoint_pressure_bar"] for r in group[c["condition_bar"]]]) for c in high]
    low = [c["residual_g_s"] for c in cond if c["condition_bar"] <= 3.5]
    return dict(condition_predictions=cond,
        endpoint_rmse_g_s=D.grouped_rmse(np.array([r["condition_bar"] for r in records]),
                                        np.array([r["endpoint_residual_g_s"] for r in records])),
        trace_rmse_g_s=float(np.mean([np.sqrt(np.mean([r["trace_mse"] for r in g])) for g in group.values()])),
        low_bias_g_s=float(np.mean(low)) if low else None,
        low_mae_g_s=float(np.mean(np.abs(low))) if low else None,
        slope_g_s_bar=C.A.slope(np.array(pressure), np.array([c["prediction_g_s"] for c in high])) if len(high) == 3 else None,
        slope_pressures_bar=pressure, slope_predictions_g_s=[c["prediction_g_s"] for c in high],
        resolved_trends=[dict(condition_bar=c, predicted=float(np.mean([r["predicted_late_trend_g_s_s"] for r in g])),
            observed=float(np.mean([r["observed_late_trend_g_s_s"] for r in g])),
            matches_rising=C.B.mean_trend_sign(np.mean([r["predicted_late_trend_g_s_s"] for r in g])) == "POSITIVE")
            for c, g in group.items() if c in (2., 3.5, 4., 5., 6.)])


def fit_fold(ctx, form, fold, reference, base, deadline, work):
    budget = C.C0.Deadline(deadline)
    source, train, held, omitted = C.design(ctx.brews.condition, fold)
    saved, g = ctx.saved[source], ctx.coarse
    mc = saved["Mc_fixed_g"]
    lo, hi = bounds(form)
    evaluate = training_evaluator(ctx, form, fold, budget)
    ids = [ctx.brews.ids[i] for i in train]
    row = dict(record_type="fit", candidate=form, fold=fold, source_fold=source,
        parameter_count=len(lo), eligibility="EXPLORATORY" if form in ("M2", "LC") else "base" if form == "A" else "control",
        exposure="TARGET_EXPOSED retrospective sequence; no held-out onset input to fitting",
        Mc_fixed_g=mc, Mc_source="C2 T2-F parameters_by_fold; inherited C3c/C3d bank",
        Mc_bank_training_indices=C.design(ctx.brews.condition, source)[1],
        omission_caveat="3.5-bar information remains in ordinary-fold Mc" if fold in C.OMITTED else None,
        onset_seed_Pd_bar=saved["Pd_bar"], training_indices=train, held_out_indices=held,
        omitted_indices=omitted, training_brews=ids, starts=[], fallback=None, status="running")
    path = work/f"{form}-{fold}-attempts.json"

    def save():
        path.write_text(json.dumps(D.plain(row), allow_nan=False)+"\n")

    def counts(p):
        return zero_counts(p, form, g.pressure[train], g.mask[train], ctx.brews.condition[train], ids)

    def attempt(start, label, group, fallback=False):
        original = np.array(start, copy=True) if fallback else coordinates(start, form)
        z = original.copy() if fallback else np.clip(original, lo+1e-10, hi-1e-10)
        p = physical(z, form)
        record = dict(label=label, seed_group=group, original_start_coordinates=original,
            initial_coordinates=z, initial_parameters=parameter_record(p, form, mc),
            initial_bounds=bound_record(z, form), initial_training_counts=counts(p))
        if fallback:
            row["fallback"] = record
        else:
            row["starts"].append(record)
        save()
        started = time.monotonic()
        try:
            initial = evaluate(z)[0]
            record["initial_objective"] = float(initial@initial)
            # Retain initial checks at the n=1 boundary and new nested boundaries.
            if fallback or start[2] == 1. or (len(start) == 5 and start[4] == 0.):
                record["initial_jacobian_check"] = S.jacobian_diagnostic(evaluate, z, lo, hi)
            fit = least_squares(lambda z: evaluate(z)[0], z, jac=lambda z: evaluate(z)[1],
                bounds=(lo, hi), method="dogbox" if fallback else "trf", x_scale="jac",
                ftol=1e-8, xtol=1e-8, gtol=1e-8, max_nfev=1500 if fallback else 500)
            if not np.isfinite(fit.cost) or not np.isfinite(fit.x).all():
                raise FloatingPointError("Nonfinite optimizer result")
            final = physical(fit.x, form)
            record.update(final_coordinates=fit.x, final_parameters=parameter_record(final, form, mc),
                objective=float(2*fit.cost), success=bool(fit.success), message=fit.message,
                nfev=fit.nfev, njev=fit.njev, active_mask=fit.active_mask,
                final_bounds=bound_record(fit.x, form, fit.active_mask), final_training_counts=counts(final))
        except Exception as exc:
            record.update(success=False, error=f"{type(exc).__name__}: {exc}")
            row["status"] = "unresolved"
            raise
        finally:
            record["wall_seconds"] = time.monotonic()-started
            save()
        return fit

    try:
        fits = []
        for i, (group, start) in enumerate(start_values(form, saved)):
            fit = attempt(start, f"start-{i+1}", group)
            fits.append(fit)
            print("START", form, fold, i+1, fit.success, 2*fit.cost, flush=True)
        valid = [(i, fit) for i, fit in enumerate(fits) if fit.success]
        if not valid:
            seed = min(range(len(fits)), key=lambda i: fits[i].cost)
            retry = attempt(fits[seed].x, "dogbox fallback", row["starts"][seed]["seed_group"], True)
            row["fallback"]["source_start"] = seed
            if not retry.success:
                raise RuntimeError("Unresolved fit after inherited fallback")
            valid = [(len(fits), retry)]
        selected, best = min(valid, key=lambda pair: pair[1].cost)
        p = physical(best.x, form)
        parts = []
        for grid in (ctx.coarse, ctx.fine):
            q = flow(p, grid.pressure[train], grid.t, mc, form, False)[0]
            parts.append(C.objective_parts(ctx.brews.condition[train], C.trace_mse(q, grid.flow[train], grid.mask[train])))
        np.testing.assert_allclose(parts[0]["objective"], 2*best.cost, rtol=1e-12, atol=0)
        attempts = row["starts"]+([row["fallback"]] if row["fallback"] else [])
        objectives = [r["objective"] for r in attempts]
        records = brew_records(ctx, p, mc, form, train, held)
        comparison = reference if base is None else base
        gain = comparison["objective"]["objective"]-parts[0]["objective"]
        fine_gain = comparison["fine_objective"]["objective"]-parts[1]["objective"]
        nesting = None
        if form in ("M2", "LC"):
            embedded = np.r_[parameters(base["parameters"], "A"), 0.]
            q = flow(embedded, g.pressure[train], g.t, mc, form, False)[0]
            objective = C.objective_parts(ctx.brews.condition[train], C.trace_mse(q, g.flow[train], g.mask[train]))["objective"]
            np.testing.assert_allclose(objective, base["objective"]["objective"], rtol=1e-12, atol=0)
            nesting = dict(A_embedded_objective=objective, returned_minus_A=parts[0]["objective"]-objective,
                materially_worse=parts[0]["objective"]-objective > 1e-6*max(1., objective),
                benchmark_only_not_added_start=True)
        numeric_keys = ("a_g_s_bar", "Pstar_bar", "n", "Pd_bar")+(("v_g_s",) if form == "M2" else ("f",) if form == "LC" else ())
        row.update(status="complete", parameters=parameter_record(p, form, mc), selected_start=selected,
            objective=parts[0], fine_objective=parts[1], brew_predictions=records,
            condition_predictions=S.condition_records(records), descriptive_metrics=metrics(records),
            capacity_peak=global_peak(p, form), jacobian_check=S.jacobian_diagnostic(evaluate, best.x, lo, hi),
            selected_bounds=bound_record(best.x, form, best.active_mask), selected_training_counts=counts(p),
            start_disagreement=max(objectives)-min(objectives) > 1e-6*max(1., 2*best.cost),
            parameter_ranges={k: [min(r["final_parameters"][k] for r in attempts),
                                  max(r["final_parameters"][k] for r in attempts)] for k in numeric_keys},
            seed_audit=S.seed_groups(attempts, selected), comparison_candidate=comparison["candidate"],
            coarse_gain=gain, fine_gain=fine_gain,
            grid_gain_unresolved=bool(gain > 0 and (fine_gain <= 0 or abs(gain-fine_gain) >= gain)),
            nested_benchmark=nesting)
        if nesting and nesting["materially_worse"]:
            raise RuntimeError("Nested training objective materially worse than feasible A; unresolved optimization")
        save()
        return D.plain(row)
    except Exception as exc:
        row.update(status="unresolved", error=f"{type(exc).__name__}: {exc}")
        save()
        raise RuntimeError(f"{form}/{fold}: {exc}; owner review required") from exc


def within_ratio(records, field):
    by_id = {r["brew"]: r for r in records}
    numerator = np.mean([by_id[b][field] for b in ("2-2", "2-4")])
    denominator = np.mean([by_id[b][field] for b in ("2-3", "2-5")])
    return dict(numerator=float(numerator), denominator=float(denominator),
                ratio=float(numerator/denominator) if denominator else None)


def readings(fits, references):
    result = []
    sources = {form: [r for r in fits if r["candidate"] == form] for form in FORMS}
    sources["T2-F"] = references
    for form, rows in sources.items():
        ordinary = [r for r in rows if r["fold"] in C.STANDARD and r["fold"] != "DESCRIPTIVE_ALL"]
        records = [b for r in ordinary for b in r["brew_predictions"] if b["role"] == "held_out"]
        measured = metrics(records)
        cond = {r["condition_bar"]: r["residual_g_s"] for r in measured["condition_predictions"]}
        e1, e2 = cond[1.], cond[2.]
        all_fit = next(r for r in rows if r["fold"] == "DESCRIPTIVE_ALL")
        record = dict(record_type="reading", candidate=form, ordinary_metrics=measured,
            bias12_g_s=(e1+e2)/2, mae12_g_s=(abs(e1)+abs(e2))/2,
            within_2bar_prediction=within_ratio(records, "endpoint_prediction_g_s"),
            within_2bar_observed=within_ratio(records, "endpoint_observed_g_s"),
            brew_1_2_residual_g_s=next(b["endpoint_residual_g_s"] for b in records if b["brew"] == "1-2"),
            held_3_5_residual_g_s=cond[3.5], low_pressure_brew_predictions=[b for b in records if b["condition_bar"] in (1., 2.)],
            descriptive_all_slope_g_s_bar=metrics(all_fit["brew_predictions"])["slope_g_s_bar"],
            out_of_fold_slope_g_s_bar=measured["slope_g_s_bar"],
            slope_label="ordinary out-of-fold 9/11/13 means across three models; not one curve derivative",
            omission_twins=[dict(fold=r["fold"], Mc_fixed_g=r.get("Mc_fixed_g", r["parameters"]["Mc_fixed_g"]),
                residual_g_s=next(c["residual_g_s"] for c in S.condition_records(r["brew_predictions"]) if c["role"] == "held_out"),
                ordinary_residual_g_s=cond[float(r["source_fold"].removeprefix("HYD-LOCO-"))],
                caveat="3.5-bar information remains in Mc; flow-training sensitivity only")
                for r in rows if r["fold"] in C.OMITTED])
        for twin in record["omission_twins"]:
            twin["signed_omission_change_g_s"] = twin["residual_g_s"]-twin["ordinary_residual_g_s"]
        if form != "T2-F":
            peaks = [r["capacity_peak"]["pressure_bar"] for r in ordinary]
            record.update(ordinary_capacity_peak_median_bar=float(np.median(peaks)),
                ordinary_capacity_peak_range_bar=[min(peaks), max(peaks)], peak_range_is_confidence_interval=False,
                descriptive_all_peak=all_fit["capacity_peak"],
                twin_peaks={r["fold"]: r["capacity_peak"] for r in rows if r["fold"] in C.OMITTED},
                parameters_by_fold={r["fold"]: r["parameters"] for r in rows})
        result.append(record)
    base = result[0]
    base_cond = {r["condition_bar"]: r["residual_g_s"] for r in base["ordinary_metrics"]["condition_predictions"]}
    for row in result:
        means = {r["condition_bar"]: r["residual_g_s"] for r in row["ordinary_metrics"]["condition_predictions"]}
        gains = [abs(base_cond[h])-abs(means[h]) for h in (1., 2.)]
        pred, observed = row["within_2bar_prediction"]["ratio"], row["within_2bar_observed"]["ratio"]
        ref = base["within_2bar_prediction"]["ratio"]
        row.update(absolute_error_reductions_vs_A_g_s=gains, improves_both_vs_A=all(g > 0 for g in gains),
            ratio_absolute_error=abs(pred-observed) if pred is not None and observed is not None else None,
            ratio_absolute_error_reduction_vs_A=abs(ref-observed)-abs(pred-observed) if None not in (pred, observed, ref) else None,
            brew_1_2_absolute_error_reduction_vs_A=abs(base["brew_1_2_residual_g_s"])-abs(row["brew_1_2_residual_g_s"]),
            held_3_5_absolute_error_reduction_vs_A=abs(base["held_3_5_residual_g_s"])-abs(row["held_3_5_residual_g_s"]))
    return D.plain(result)


def write_summary(rows, path):
    reads = {r["candidate"]: r for r in rows if r["record_type"] == "reading"}
    fits = [r for r in rows if r["record_type"] == "fit"]
    provenance = next(r for r in rows if r["record_type"] == "provenance")
    def residual(form, condition):
        return next(c["residual_g_s"] for c in reads[form]["ordinary_metrics"]["condition_predictions"] if c["condition_bar"] == condition)
    winners = [f for f in FORMS[1:] if reads[f]["improves_both_vs_A"]]
    lines = ["# PRESSURE-PEAK C3e: free-Pd base and low-pressure forms", "",
        "**capability demonstration, not validation; PHYSICAL_VALIDATION=NOT_ESTABLISHED; TARGET_EXPOSED.** Ungraded Python screen.", "",
        ("Forms improving absolute held-out condition-mean errors at both 1 and 2 bar versus A: "+", ".join(winners)+"."
         if winners else "No added form improves absolute held-out condition-mean errors at both 1 and 2 bar versus A."),
        "This is the declared low-pressure screen, not overall model preference or physical validation. DESCRIPTIVE_ALL is in-sample only.", "",
        "## Ordinary held-out predictions", "",
        "Residuals are prediction minus observation, g/s. T2-F is the accepted historical reference, with matched observers and no refit.", "",
        "| Form | 1 bar | 2 bar | bias12 | mae12 | Within-2-bar ratio | Brew 1-2 residual | 3.5-bar residual |",
        "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for f in (*FORMS, "T2-F"):
        r = reads[f]
        lines.append(f"| {f} | {residual(f,1):+.6f} | {residual(f,2):+.6f} | {r['bias12_g_s']:+.6f} | {r['mae12_g_s']:.6f} | {r['within_2bar_prediction']['ratio']:.6f} | {r['brew_1_2_residual_g_s']:+.6f} | {r['held_3_5_residual_g_s']:+.6f} |")
    lines += ["", f"Recomputed observed within-2-bar ratio: **{reads['A']['within_2bar_observed']['ratio']:.9f}**, a ratio of pair means from authenticated 100-s endpoint observations.", "",
        "| Form | Ratio absolute-error reduction vs A | Brew 1-2 absolute-error reduction | 3.5-bar absolute-error reduction |",
        "|---|---:|---:|---:|"]
    for f in FORMS[1:]:
        r = reads[f]
        lines.append(f"| {f} | {r['ratio_absolute_error_reduction_vs_A']:+.6f} | {r['brew_1_2_absolute_error_reduction_vs_A']:+.6f} | {r['held_3_5_absolute_error_reduction_vs_A']:+.6f} |")
    lines += ["", "Positive reductions improve the named metric; negative reductions are tradeoffs. A ratio gain alone does not fix the law, and a small worsening or brew 1-2 alone is not an automatic veto.", "",
        "## All conditions and downstream behavior", "",
        "| Form | 1 | 2 | 3.5 | 4 | 5 | 6 | 7 | 8 | 9 | 11 | 13 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for f in (*FORMS, "T2-F"):
        lines.append("| "+f+" | "+" | ".join(f"{residual(f,h):+.4f}" for h in C.CONDITIONS)+" |")
    lines += ["", "| Form | Endpoint / trace RMSE, g/s | 1-3.5 bias / MAE, g/s | Rising resolved trends | Capacity peak median [range], bar | >=9 slope: in-sample / out-of-fold, g/s/bar |",
        "|---|---|---|---:|---|---|"]
    for f in (*FORMS, "T2-F"):
        r, m = reads[f], reads[f]["ordinary_metrics"]
        peak = (f"{r['ordinary_capacity_peak_median_bar']:.5f} [{r['ordinary_capacity_peak_range_bar'][0]:.5f}, {r['ordinary_capacity_peak_range_bar'][1]:.5f}]" if f != "T2-F" else "historical C2")
        lines.append(f"| {f} | {m['endpoint_rmse_g_s']:.5f} / {m['trace_rmse_g_s']:.5f} | {m['low_bias_g_s']:+.5f} / {m['low_mae_g_s']:.5f} | {sum(t['matches_rising'] for t in m['resolved_trends'])}/5 | {peak} | {r['descriptive_all_slope_g_s_bar']:+.6f} / {r['out_of_fold_slope_g_s_bar']:+.6f} |")
    lines += ["", "Peaks are global capacity maxima; ordinary-fold ranges are not confidence intervals. The out-of-fold slope combines the 9/11/13-bar held-out predictions from three models and is not a curve derivative. Both slopes use actual mean endpoint pressures.", "",
        "## Fixed-bank omission tests and fitted additions", "",
        "Twins omit 3.5 bar from flow fitting only. **3.5-bar information remains in Mc**; its effect has not been measured. These are conditional sensitivity tests, not robustness to removing 3.5 bar from the whole calibration pipeline.", "",
        "| Form | Held bar | Ordinary residual | Omission-twin residual | Signed change |",
        "|---|---:|---:|---:|---:|"]
    for f in FORMS:
        for r in reads[f]["omission_twins"]:
            lines.append(f"| {f} | {r['fold'].split('-')[2]} | {r['ordinary_residual_g_s']:+.6f} | {r['residual_g_s']:+.6f} | {r['signed_omission_change_g_s']:+.6f} |")
    lines += ["", "| Fit | M2 v, g/s | Mc/v, s | LC f |",
        "|---|---:|---:|---:|"]
    for fold in FOLDS:
        m2, lc = (reads[f]["parameters_by_fold"][fold] for f in ("M2", "LC"))
        ratio = m2["Mc_over_v_s"]
        lines.append(f"| {fold} | {m2['v_g_s']:.9g} | {ratio if isinstance(ratio,str) else format(ratio,'.9g')} | {lc['f']:.9g} |")
    lines += ["", "All fitted parameters, nine individual low-pressure predictions, condition objective shares, descriptive and twin peaks, and all start diagnostics are in RESULT_TABLE.csv.", "",
        "## Numerical and interpretive limits", ""]
    for f in FORMS:
        own = [r for r in fits if r["candidate"] == f]
        disagreements = [r["fold"] for r in own if r["start_disagreement"]]
        bounds_hit = [(r["fold"], k) for r in own for k,v in r["selected_bounds"].items() if v.get("near_finite_bound") or v.get("active")]
        lines.append(f"{f}: start-objective disagreement in {disagreements or 'none'}; selected bound flags {bounds_hit or 'none'}; unresolved grid gains in {[r['fold'] for r in own if r['grid_gain_unresolved']] or 'none'}.")
        lines.append("")
    lines += ["Boundary estimates and weak parameter agreement limit identification. A stable nested-boundary optimum can support retaining A. LC loses n at f=1 and f at n=1. An upper-v-bound estimate leaves bound sensitivity unresolved. Equal objectives do not establish uniquely identified parameters.", "",
        "M1 changes recovery speed as well as shape. M2 uses symmetric clock/exposure integration on the inherited grid, with the exact v=0 identity preserved. Masks never pause or reset its state. The B0c objective scores observed onset + 2 s through clean support; the pre-onset stretch is unscored. Large v values can be indistinguishable at the endpoint; diagnostic agreement alone cannot identify v. No restart claim is made.", "",
        "The Jacobian checks retain halving direction and branch counts. CI replays analytic norms and saved error-ratio arithmetic, not roundoff-dominated finite-difference cancellation remainders. A synthetic extreme-pressure LC check reaches an unused overflow branch in the unchanged parent n=1 Taylor expression; returned capacity and derivatives are finite.", "",
        "Run order and dates are unavailable. Per-condition batch effects can also produce conductance steps with near-proportional within-condition flow; this screen cannot exclude them. No bootstrap, profiling, onset refit or grading was performed.", "",
        "## Execution", "",
        "Source authentication, T2-F objective replays (including 0.0719361259858887), all five C3d A prediction/objective replays, and exact v=0 / f=0 identities completed before fitting with rtol=1e-12, atol=0.", "",
        f"{provenance['fit_count']} fit problems / {provenance['start_count']} scheduled starts; {provenance['fallback_count']} inherited fallbacks. Cumulative execution and checks: {provenance['cumulative_wall_seconds']:.3f} s of 7200 s. {provenance.get('test_results','Focused checks pending.')}", "",
        "The status item remains active with verified_commit=null. The C3e screen awaits owner review; no successor is authorized."]
    path.write_text("\n".join(lines)+"\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", type=Path, required=True)
    parser.add_argument("--onset-cache", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    with D.timed_attempt(args.work) as budget:
        checkpoint = args.work/"fits.json"
        identity = args.work/"fit-source-identity.json"
        if checkpoint.exists() or identity.exists():
            raise RuntimeError("Existing attempt; no automatic fit repetition")
        ids = next(r for r in S.read_table() if r["record_type"] == "inputs")["brew_ids"]
        sources = source_hashes(args.raw, args.onset_cache, ids)
        print("SOURCE_AUTHENTICATION_COMPLETE", len(sources), flush=True)
        ctx = D.load_context(args.raw, args.onset_cache)
        references = C.reference_folds(ctx)
        replay = replay_c3d(ctx)
        numerical = numerical_fixtures(budget)
        # Confirm the accepted reference metric definitions before candidates.
        ref_read = dict(ordinary_metrics=metrics([b for r in references
            if r["fold"] in C.STANDARD and r["fold"] != "DESCRIPTIVE_ALL"
            for b in r["brew_predictions"] if b["role"] == "held_out"]))
        accepted = next(r for r in C.C2.read_results() if r["candidate"] == "T2-F")
        for key in ("endpoint_rmse_g_s", "trace_rmse_g_s", "slope_g_s_bar"):
            np.testing.assert_allclose(ref_read["ordinary_metrics"][key], float(accepted[key]), rtol=1e-12, atol=0)
        print("REFERENCE_METRIC_COMPATIBILITY_COMPLETE", flush=True)
        identity.write_text(json.dumps(sources, indent=2)+"\n")
        fits = []
        try:
            for forms in (("A",), ("M1", "M2", "LC")):
                pool = ProcessPoolExecutor(max_workers=args.workers)
                futures = {}
                try:
                    for form in forms:
                        for fold in FOLDS:
                            reference = next(r for r in references if r["fold"] == fold)
                            base = next((r for r in fits if r["candidate"] == "A" and r["fold"] == fold), None)
                            future = pool.submit(fit_fold, ctx, form, fold, reference, base, budget.end, args.work)
                            futures[future] = (form, fold)
                    for future in as_completed(futures):
                        budget.check()
                        row = future.result()
                        fits.append(row)
                        checkpoint.write_text(json.dumps(fits, allow_nan=False)+"\n")
                        print("FIT_COMPLETE", row["candidate"], row["fold"], row["parameters"], flush=True)
                except BaseException:
                    for future in futures:
                        future.cancel()
                    for process in list(pool._processes.values()):
                        process.terminate()
                    pool.shutdown(wait=True, cancel_futures=True)
                    raise
                else:
                    pool.shutdown(wait=True)
        except BaseException as exc:
            (args.work/"STOP.txt").write_text(f"{type(exc).__name__}: {exc}\n")
            raise
        fits.sort(key=lambda r: SCHEDULE.index((r["candidate"], r["fold"])))
        if sources != source_hashes(args.raw, args.onset_cache, ids):
            raise RuntimeError("Sources changed during execution")
        rows = [C.input_fixture(ctx), replay, numerical, *references, *fits, *readings(fits, references)]
        rows.append(dict(record_type="provenance", source_sha256=sources, plan_sha256=PLAN_SHA256,
            source_base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            python=sys.version, cumulative_wall_seconds=budget.cumulative, cap_seconds=7200,
            execution=f"{args.workers} workers; one BLAS thread per worker", fit_count=len(fits),
            start_count=sum(len(r["starts"]) for r in fits), fallback_count=sum(r["fallback"] is not None for r in fits),
            bootstrap_count=0, onset_refits=0, profiling_count=0))
        budget.check()
        D.write_table(rows, OUT/"RESULT_TABLE.csv")
        write_summary(D.plain(rows), OUT/"SUMMARY.md")
        print("COMPLETE", budget.cumulative, flush=True)


if __name__ == "__main__":
    main()

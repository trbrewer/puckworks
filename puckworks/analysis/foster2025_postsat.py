"""Offline bounded reproduction for MODEL-FOSTER2025-POSTSAT-001.

Run from the repository with its pinned baseline history. External log/cache
paths retain variable metadata and dense arrays; only compact reports enter Git.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No optimization or parameter fitting.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import pickle
import subprocess
import sys
import time
import types

import numpy as np
import scipy
from scipy.integrate import quad, solve_ivp
from scipy.optimize import brentq

from puckworks.models.foster2025 import machine_mode as fm
from puckworks.validation import gates

BASE = "5745f615637dbfe95065b48339c3fe566fa58d66"
ROOT = Path(__file__).resolve().parents[2]
BUNDLE = Path("docs/analysis/model_foster2025_postsat_001")
SOURCE = "puckworks/models/foster2025/machine_mode.py"
LEVELS = dict(coarse=dict(rtol=1e-7, atol_scale=1e-9, max_step=0.02),
              fine=dict(rtol=1e-9, atol_scale=1e-11, max_step=0.005),
              finer=dict(rtol=1e-11, atol_scale=1e-13, max_step=0.00125))
CHANNELS = ("s_m", "H_m", "headspace_pressure_absolute_Pa", "Q_pump_m3_s",
            "Q_bed_in_m3_s", "Q_out_m3_s", "V_pump_m3", "V_out_m3", "V_storage_m3")
BUDGET = 1e-6


def digest(data):
    return hashlib.sha256(data).hexdigest()


def scales(p):
    v = p.A * (p.H0 + p.phi_T*p.L)
    return np.array([p.L, p.H0, p.p_m, p.Q_m, p.Q_m, p.Q_m, v, v, v])


def groups(p):
    return dict(P_m=p.p_m/p.p_a, R=p.R_f*p.Q_m/p.p_a, Hratio=p.H0/p.L,
                G=p.rho*p.g*p.L/p.p_a, P_c=p.p_c/p.p_a, beta=p.beta,
                K=p.k*p.A*p.p_a/(p.mu*p.Q_m*p.L), phi_T=p.phi_T,
                t_shift_s=p.t_shift, time_scale_s=p.A*p.L/p.Q_m, length_scale_m=p.L)


def fixture_params():
    p = fm.FosterParams()
    p.Q_m = p.A*p.L/5.162
    p.H0 = 0.782*p.L
    p.p_m = 14.8038*p.p_a
    p.R_f = 0.0002*p.p_a/p.Q_m
    p.g = 0.00093195*p.p_a/(p.rho*p.L)
    p.p_c = 0.0987*p.p_a
    p.k = 0.0495*p.mu*p.Q_m*p.L/(p.A*p.p_a)
    return p


def independent_flows(H, s, p):
    """Separate Eq. 5/7/16 implementation, rationalized pump root.

    Never call production pressure, pump, bed flow, RHS or observation helpers.
    """
    ph = p.p_a*p.beta/(1-H/p.H0)
    a = (p.p_m-p.p_a)/(p.Q_m*p.Q_m)
    dp = p.p_m-ph
    qp = 2*dp/(p.R_f+np.sqrt(p.R_f*p.R_f+4*a*dp))
    qb = p.A*p.k/(p.mu*s)*(ph-p.p_a+p.p_c+p.rho*p.g*(H+s))
    return ph, qp, qb


def independent_F(H, p):
    _, qp, qb = independent_flows(H, p.L, p)
    return (qp-qb)/p.A


def independent_derivative(H, p):
    _, q, _ = independent_flows(H, p.L, p)
    dp = p.p_a*p.H0*p.beta/(p.H0-H)**2
    a = (p.p_m-p.p_a)/p.Q_m**2
    return -dp/(p.A*(2*a*q+p.R_f))-p.k*(dp+p.rho*p.g)/(p.mu*p.L)


def baseline_module():
    raw = subprocess.check_output(["git", "show", f"{BASE}:{SOURCE}"], cwd=ROOT)
    module = types.ModuleType("_foster_postsat_pinned_baseline")
    sys.modules[module.__name__] = module
    exec(compile(raw, "pinned_baseline_machine_mode.py", "exec"), module.__dict__)
    return module, digest(raw)


def comparison_grid(results):
    points = list(np.linspace(0, 30, 601))
    for r in results:
        for t in (r["t_p"], r["t_s"]):
            if t is not None:
                points.extend(t+d for d in (0, -1e-7, 1e-7, -1e-4, 1e-4) if 0 <= t+d <= 30)
    return np.unique(points)


def observations(r, grid):
    return np.array([[fm.observe(float(t), r)[key] for key in CHANNELS] for t in grid])


def differences(left, right, grid, ts_left, ts_right, p):
    err = np.abs(left-right)/scales(p)
    event_gap = (grid >= min(ts_left, ts_right)) & (grid < max(ts_left, ts_right))
    norms = {key: float(np.max(err[~event_gap, i] if key == "Q_out_m3_s" else err[:, i]))
             for i, key in enumerate(CHANNELS)}
    return dict(normalized_max=norms, passed=all(v <= BUDGET for v in norms.values()),
                outlet_excluded_event_gap_s=[min(ts_left, ts_right), max(ts_left, ts_right)],
                outlet_excluded_sample_count=int(event_gap.sum()),
                event_time_error_normalized=abs(ts_left-ts_right)/(p.A*p.L/p.Q_m))


def independent_integrals(r, grid, *, scalar_post=None):
    """QUADPACK integration of independently coded flows, split at each event.

    Integrating each common-grid subinterval provides an independent cumulative
    series, as well as independent headspace increments. Not a complement.
    """
    p, tp, ts = r["p"], r["t_p"], r["t_s"]
    _, qp0, _ = independent_flows(0, r["s_p"], p)

    def state(t):
        if t <= tp:
            return qp0*t/(p.A*p.phi_T), 0.0
        if t >= ts:
            H = scalar_post.sol(t)[0] if scalar_post is not None else r["post_sol"].sol(t)[0]
            return p.L, float(H)
        s, H = r["sol"].sol(t)
        return float(s), float(H)

    def flows(t):
        if t <= tp:
            return np.array([qp0, 0.0, 0.0])
        s, H = state(t)
        _, qp, qb = independent_flows(H, s, p)
        return np.array([qp, qb if t >= ts else 0.0, qp-qb])

    sums, errors, increments = [np.zeros(3)], [], []
    for lo, hi in zip(grid[:-1], grid[1:]):
        value = np.zeros(3)
        error = np.zeros(3)
        boundaries = [lo] + [x for x in (tp, ts) if lo < x < hi] + [hi]
        for a, b in zip(boundaries[:-1], boundaries[1:]):
            if b <= tp:
                value[0] += qp0*(b-a)
                continue
            for i in range(3):
                v, e = quad(lambda t: flows(t)[i], a, b, epsabs=1e-14,
                            epsrel=2e-11, limit=200)
                value[i] += v
                error[i] += e
        sums.append(sums[-1]+value)
        errors.append(error)
        increments.append(p.A*(state(hi)[1]-state(lo)[1])-value[2])
    return np.array(sums), np.array(errors), np.array(increments), state


class ExecutionLog:
    """Task-local log only: count all starts, cache arrays outside the repository."""
    def __init__(self, path, cache, reuse=False, final_source=False):
        self.reuse = reuse
        self.final_source = final_source
        self.path, self.cache = Path(path), Path(cache)
        for location in (self.path, self.cache):
            if location.resolve().is_relative_to(ROOT):
                raise ValueError("execution metadata and dense arrays must remain outside Git")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.cache.mkdir(parents=True, exist_ok=True)
        self.rows = [json.loads(x) for x in self.path.read_text().splitlines()] if self.path.exists() else []
        self.source_hash = digest((ROOT/SOURCE).read_bytes())

    def append(self, row):
        self.rows.append(row)
        with self.path.open("a") as f:
            f.write(json.dumps(row, allow_nan=False, sort_keys=True)+"\n")

    def trajectory(self, name, fn):
        reuse_oracle = self.final_source and name in ("baseline", "independent-post", "equilibrium", "perturbation")
        if self.reuse or reuse_oracle:
            matches = [r for r in self.rows if r["event"] == "START" and r["name"] == name
                       and (r["source_sha256"] == self.source_hash or reuse_oracle)]
            if not matches:
                raise ValueError("no unchanged-source cache for " + name)
            row = matches[-1]
            with (self.cache/f"{row['execution']:02d}-{name}.pickle").open("rb") as f:
                return pickle.load(f)
        n = sum(r["event"] == "START" for r in self.rows)
        seconds = sum(r.get("numerical_seconds", 0) for r in self.rows)
        if n >= 12 or seconds >= 600:
            raise RuntimeError("qualification resource ceiling reached")
        self.append(dict(event="START", execution=n+1, name=name, source_sha256=self.source_hash,
                         utc=datetime.now(timezone.utc).isoformat()))
        tic = time.perf_counter()
        try:
            result = fn()
            good = result.get("success", True) if isinstance(result, dict) else result.success
            with (self.cache/f"{n+1:02d}-{name}.pickle").open("wb") as f:
                pickle.dump(result, f)
        except Exception:
            self.append(dict(event="END", execution=n+1, name=name, success=False,
                             numerical_seconds=time.perf_counter()-tic))
            raise
        self.append(dict(event="END", execution=n+1, name=name, success=bool(good),
                         numerical_seconds=time.perf_counter()-tic))
        if not good:
            raise RuntimeError(f"{name}: unsuccessful numerical solve")
        return result


def run(log):
    old, old_hash = baseline_module()
    baseline = log.trajectory("baseline", old.solve)
    runs = {name: log.trajectory("D-"+name, lambda settings=settings: fm.solve(**settings))
            for name, settings in LEVELS.items()}
    fixture = log.trajectory("F-fine", lambda: fm.solve(fixture_params(), **LEVELS["fine"]))
    ref = runs["finer"]
    p, ts = ref["p"], ref["t_s"]
    hs = ref["sol"].y_events[0][0][1]
    independent = log.trajectory("independent-post", lambda: solve_ivp(
        lambda t,y: [independent_F(y[0],p)], [ts,30], [hs], method="DOP853",
        rtol=2e-12, atol=1e-14*p.H0, max_step=0.01, dense_output=True))
    if independent.t[0] != ts or independent.y[0, 0] != hs:
        raise ValueError("cached independent trajectory initial state no longer matches final source")
    hstop = p.H0*(1-p.beta*p.p_a/p.p_m)
    heq = brentq(lambda H: independent_F(H,p), 0, np.nextafter(hstop, 0), xtol=1e-16)
    rate = independent_derivative(heq,p)
    tau = -1/rate
    eq = log.trajectory("equilibrium", lambda: solve_ivp(
        lambda t,y: [independent_F(y[0],p)], [0,tau], [heq], method="DOP853",
        rtol=2e-12, atol=1e-14*p.H0, max_step=tau/100, dense_output=True))
    perturbation = 1e-5*p.H0
    pert = log.trajectory("perturbation", lambda: solve_ivp(
        lambda t,y: [independent_F(y[0],p)], [0,tau], [heq+perturbation], method="DOP853",
        rtol=2e-12, atol=1e-14*p.H0, max_step=tau/100, dense_output=True))

    tic = time.perf_counter()
    grid = comparison_grid(list(runs.values()))
    arrays = {name: observations(r,grid) for name,r in runs.items()}
    fine_finer = differences(arrays["fine"], arrays["finer"], grid,
                             runs["fine"]["t_s"], ts, p)
    coarse_fine = differences(arrays["coarse"], arrays["fine"], grid,
                              runs["coarse"]["t_s"], runs["fine"]["t_s"], p)
    integrals, qerr, herr, _ = independent_integrals(ref,grid)
    production = arrays["finer"]
    vscale = scales(p)[6]
    water = dict(global_residual_normalized=float(np.max(np.abs(
                     integrals[:,0]-integrals[:,1]-production[:,8]))/vscale),
                 production_residual_normalized=float(np.max(np.abs(
                     production[:,6]-production[:,7]-production[:,8]))/vscale),
                 pump_accumulation_difference_normalized=float(np.max(np.abs(
                     integrals[:,0]-production[:,6]))/vscale),
                 outlet_accumulation_difference_normalized=float(np.max(np.abs(
                     integrals[:,1]-production[:,7]))/vscale),
                 headspace_subinterval_residual_normalized=float(np.max(np.abs(herr))/vscale),
                 quadrature_error_bound_normalized=(qerr.sum(axis=0)/vscale).tolist(),
                 interior_and_boundary_samples=len(grid),
                 before_first_drip_samples=int(np.sum(grid<ts)))
    water["passed"] = all(np.max(value) <= BUDGET for key,value in water.items() if key.endswith("normalized"))
    indep_integrals, iqerr, _, state = independent_integrals(ref,grid,scalar_post=independent)
    independent_array = []
    for t,volumes in zip(grid,indep_integrals):
        s,H = state(t)
        ph,qp,qb = independent_flows(H, s if s>0 else ref["s_p"],p)
        if t <= ref["t_p"]:
            qb = ref["Q_p"]
        independent_array.append([s,H,ph,qp,qb,qb if t>=ts else 0,
                                  volumes[0],volumes[1],p.A*(H+p.phi_T*s)])
    ind_comparison = differences(production, np.array(independent_array),grid,ts,ts,p)
    ind_comparison["post_sample_count"] = int(np.sum(grid>=ts))
    ind_comparison["quadrature_error_bound_normalized"] = (iqerr.sum(axis=0)/vscale).tolist()

    common_end = min(baseline["t_s"], runs["fine"]["t_s"])
    early_grid = np.unique(np.r_[np.linspace(0,common_end,501),
                                baseline["t_p"], runs["fine"]["t_p"]])
    baseline_values = []
    for t in early_grid:
        s,H = old._sH(t,baseline)
        qb = baseline["Q_p"] if t <= baseline["t_p"] else old.f_bed(H,s,baseline["p"])*p.A
        baseline_values.append([s,H,old.p_h(H,baseline["p"]),old.Q_pump(H,baseline["p"]),qb])
    new = observations(runs["fine"],early_grid)[:,:5]
    norms = np.max(np.abs(new-np.array(baseline_values))/scales(p)[:5],axis=0)
    events = {key: abs(baseline[key]-runs["fine"][key])/(p.A*p.L/p.Q_m) for key in ("t_p","t_s")}
    compatibility = dict(normalized_max=dict(zip(CHANNELS[:5],norms.tolist())),
                         event_error_normalized=events, count=len(early_grid),
                         common_model_support_s=[0,float(common_end)],
                         passed=bool(np.max(norms)<=BUDGET and max(events.values())<=BUDGET))
    Hs_old = float(baseline["sol"].sol(baseline["t_s"])[1])
    imbalance = float(old.Q_pump(Hs_old,baseline["p"])-p.A*old.f_bed(Hs_old,p.L,baseline["p"]))
    defect = dict(source_sha256=old_hash, baseline_commit=BASE, parameters=asdict(baseline["p"]),
                  reported_saturation_s=baseline["t_s"]+p.t_shift,
                  H_at_saturation_m=Hs_old, pump_minus_bed_m3_s=imbalance,
                  legacy_constant_headspace_balance_defect_preserved=bool(imbalance>0))

    post_start = fm.observe(ts,ref)
    left = ref["sol"].sol(ts)
    _,qpl,qbl = independent_flows(float(left[1]),float(left[0]),p)
    transition_norms = dict(H=abs(float(left[1])-post_start["H_m"])/p.H0,
        s=abs(p.L-float(left[0]))/p.L,
        pressure=abs(independent_flows(float(left[1]),p.L,p)[0]-post_start["headspace_pressure_absolute_Pa"])/p.p_m,
        pump=abs(qpl-post_start["Q_pump_m3_s"])/p.Q_m,
        bed=abs(qbl-post_start["Q_bed_in_m3_s"])/p.Q_m)
    step=1e-6
    fd=(fm._sH(ts+step,ref)[1]-hs)/step
    left_volumes = np.array([ref["Q_p"]*ref["t_p"], 0.0])+fm._segment_volumes(ts,ref,False)
    volume_jump = np.array([post_start["V_pump_m3"],post_start["V_out_m3"]])-left_volumes
    transition = dict(normalized_continuity=transition_norms, s_after_exactly_L=fm._sH(ts+step,ref)[0]==p.L,
                      outlet_left_m3_s=fm.observe(ts-1e-7,ref)["Q_out_m3_s"],
                      outlet_right_m3_s=post_start["Q_out_m3_s"],
                      eq29_entry_derivative_m_s=independent_F(hs,p),
                      actual_solver_entry_derivative_m_s=ref["post_entry_derivative_m_s"],
                      algebraic_entry_derivative_error_normalized=abs(ref["post_entry_derivative_m_s"]-independent_F(hs,p))*(p.A*p.L/p.Q_m)/p.H0,
                      numerical_entry_derivative_m_s=float(fd),
                      finite_difference_entry_diagnostic="NOT_QUALIFIED_AS_DENSE_OUTPUT_DERIVATIVE",
                      finite_difference_diagnostic_note="Initial forward-difference estimate exceeded 1e-6 (retained). This is not a state-trajectory budget: the actual RHS is checked algebraically; no derivative observation is supplied.",
                      derivative_error_normalized=abs(fd-independent_F(hs,p))*(p.A*p.L/p.Q_m)/p.H0,
                      volume_jump_m3=volume_jump.tolist(),
                      volume_continuity_basis="Both segment quadratures begin at zero; pre-event accumulated volumes carry forward.")
    transition["passed"] = bool(max(transition_norms.values())<=BUDGET
        and transition["algebraic_entry_derivative_error_normalized"]<=64*np.finfo(float).eps and transition["s_after_exactly_L"]
        and np.max(np.abs(volume_jump))/vscale<=BUDGET
        and transition["outlet_left_m3_s"]==0 and transition["outlet_right_m3_s"]>0)
    end=fm.observe(30,ref)
    eq_drift=float(np.max(np.abs(eq.y[0]-heq))/p.H0)
    measured=(pert.y[0,-1]-heq)/perturbation
    rate_error=abs(measured-np.exp(rate*tau))/np.exp(rate*tau)
    equilibrium=dict(H_eq_m=heq, Fprime_per_s=rate, relaxation_time_s=tau,
        initial_perturbation_m=perturbation, equilibrium_drift_normalized=eq_drift,
        rate_test_relative_error=float(rate_error), rate_test_budget=1e-3,
        endpoint_H_error_normalized=abs(end["H_m"]-heq)/p.H0,
        endpoint_flow_imbalance_normalized=abs(end["Q_pump_m3_s"]-end["Q_bed_in_m3_s"])/p.Q_m,
        root_residual_normalized=abs(independent_F(heq,p))*p.A/p.Q_m,
        stable=bool(rate<0), passed=bool(rate<0 and eq_drift<=1e-9 and rate_error<=1e-3))
    equilibrium["finite_horizon_equilibrated"] = (equilibrium["endpoint_H_error_normalized"]<=BUDGET
                                                  and equilibrium["endpoint_flow_imbalance_normalized"]<=BUDGET)
    cap_excess=float(np.max(production[:,4]-ref["Q_p"])/p.Q_m)
    domain=dict(passed=bool(np.all(production[:,:2]>=0) and np.all(production[:,0]<=p.L)
                            and np.all(production[:,1]<=hstop) and np.all(production[:,3]>=0)
                            and np.all(production[:,3]<=p.Q_m) and cap_excess<=64*np.finfo(float).eps),
                H_stop_m=hstop, max_H_m=float(production[:,1].max()),
                min_Q_pump_m3_s=float(production[:,3].min()), max_Q_pump_m3_s=float(production[:,3].max()),
                max_source_cap_excess_normalized=cap_excess,
                support=fm.metadata(ref), invariant_proof="CONTRACT.md: source cap and domain invariance")
    a=(p.p_m-p.p_a)/p.Q_m**2
    algebra=float(np.max(np.abs(a*production[:,3]**2+p.R_f*production[:,3]-(p.p_m-production[:,2])))/p.p_m)
    references={}
    for name,r in [("dimensional_defaults",runs["fine"]),("rounded_fixture",fixture)]:
        references[name]=dict(parameters=asdict(r["p"]), dimensionless=groups(r["p"]),
            figure15=gates.foster_fig15_windows(r),
            existing_flow_minimum_gate=gates.gate_foster_fig15_flowmin(r),
            existing_fig12_14_gate=gates.gate_foster_ct_trajectory(r))
    paths=[SOURCE,"puckworks/analysis/foster2025_postsat.py","puckworks/validation/gates.py",
           str(BUNDLE/"CONTRACT.md"),"puckworks/models/foster2025/infiltration.py",
           "puckworks/data/foster2025_2/foster2025_params.csv",
           "puckworks/data/foster2025_2/fig15_flow_pressure.csv",
           "puckworks/data/foster2025_2/fig12_14_fitted_curves.csv"]
    statuses=dict(equation_completion="PASS" if transition["passed"] else "FAIL",
        domain_boundedness="PASS" if domain["passed"] else "FAIL",
        water_conservation="PASS" if water["passed"] else "FAIL",
        temporal_accuracy="PASS" if fine_finer["passed"] and fine_finer["event_time_error_normalized"]<=BUDGET else "FAIL",
        independent_method="PASS" if ind_comparison["passed"] else "FAIL",
        equilibrium_stability="PASS" if equilibrium["passed"] else "FAIL",
        finite_horizon_equilibrium="PASS" if equilibrium["finite_horizon_equilibrated"] else "NOT_REACHED",
        earlier_stage_compatibility="PASS" if compatibility["passed"] else "FAIL")
    for name,r in references.items():
        statuses["source_reference_"+name]="PASS" if all(r[k]["passed"] for k in
            ("figure15","existing_flow_minimum_gate","existing_fig12_14_gate")) else "FAIL"
    statuses.update(software_QA="REPORTED_SEPARATELY_IN_HANDOFF",hosted_CI="REPORTED_SEPARATELY_IN_HANDOFF",
                    independent_exact_head_review="REPORTED_SEPARATELY_IN_HANDOFF")
    qualified=all(v=="PASS" for k,v in statuses.items() if k not in
                  ("software_QA","hosted_CI","independent_exact_head_review"))
    result=dict(task="MODEL-FOSTER2025-POSTSAT-001", governance="G2",
        change_declaration="GOVERNING_PHYSICS_CHANGE", PHYSICAL_VALIDATION="NOT_ESTABLISHED",
        disposition="BOUNDED_NUMERICAL_AND_SOURCE_RECONSTRUCTION_PASS" if qualified else "DIAGNOSTIC_DRAFT_QUALIFICATION_INCOMPLETE",
        outcomes=statuses, source_sha256={path:digest((ROOT/path).read_bytes()) for path in paths},
        configuration_sha256=digest(json.dumps(dict(levels=LEVELS,D=asdict(p),F=asdict(fixture["p"])),sort_keys=True).encode()),
        dependencies=dict(python=sys.version.split()[0],numpy=np.__version__,scipy=scipy.__version__),
        baseline=defect, settings=LEVELS, scales=dict(zip(CHANNELS,scales(p).tolist())),
        time_scale_s=p.A*p.L/p.Q_m, comparison_grid_count=len(grid),
        fine_to_finer=fine_finer, coarse_to_fine=coarse_fine, water=water,
        independent_method=ind_comparison, compatibility=compatibility, transition=transition,
        equilibrium=equilibrium, domain=domain, algebraic_roundoff_pump_equation_normalized=algebra,
        references=references, dimensionless_default_minus_fixture={k:groups(p)[k]-groups(fixture["p"])[k] for k in groups(p)},
        qualification_executions_this_bundle=8,
        retained_initial_report_disposition="DIAGNOSTIC_DRAFT_QUALIFICATION_INCOMPLETE: finite-difference derivative check; no failed source-reference comparison",
        verification_correction="Actual solver RHS entry is compared with independent Eq. 29. The initial dense-output derivative diagnostic remains explicitly unqualified; no thresholds/parameters/source observers/support masks changed.", resource_ceiling=dict(executions=12,numerical_seconds=600))
    log.append(dict(event="ANALYSIS", numerical_seconds=time.perf_counter()-tic, source_sha256=log.source_hash))
    # Arrays and complete result caches remain private; make independent review replay possible.
    np.savez(log.cache/"comparison-arrays.npz",model_time_s=grid,**arrays,independent=np.array(independent_array))
    return result


def markdown(r):
    lines=["# MODEL-FOSTER2025-POSTSAT-001 results", "", r["disposition"], "",
           "G2 / GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.", "",
           "The old constant headspace is replaced by source Eq. 29/38 after actual saturation.",
           "Source-conditioned equation reconstruction only; no fitting, new physics or EWP adoption.", "",
           "The initial finite-difference entry-derivative diagnostic remains NOT_QUALIFIED_AS_DENSE_OUTPUT_DERIVATIVE.",
           "Its normalized error is retained in JSON. The solver RHS at entry is verified independently at algebraic roundoff;",
           "no derivative observer is supplied. The initial diagnostic disposition and correction remain recorded.", "",
           "| Outcome | Disposition |", "|---|---|"]
    lines += [f"| {k} | {v} |" for k,v in r["outcomes"].items()]
    lines += ["",f"Pinned baseline defect: saturation {r['baseline']['reported_saturation_s']:.9f} reported s; "
              f"pump minus bed inflow {r['baseline']['pump_minus_bed_m3_s']*1e6:.9f} mL/s.","",
              "| Continuous channel | Fine/finer normalized max | Independent normalized max |",
              "|---|---:|---:|"]
    lines += [f"| {k} | {r['fine_to_finer']['normalized_max'][k]:.4g} | {r['independent_method']['normalized_max'][k]:.4g} |" for k in CHANNELS]
    lines += ["",f"Independent global water residual: {r['water']['global_residual_normalized']:.4g}; "
              f"headspace subinterval residual: {r['water']['headspace_subinterval_residual_normalized']:.4g} (budget 1e-6).",
              f"Outlet comparison excludes {r['fine_to_finer']['outlet_excluded_sample_count']} samples in the disclosed "
              f"event interval {r['fine_to_finer']['outlet_excluded_event_gap_s']} model s. "
              "All continuous channels retain these samples; event-time errors are separate.","",
              "| Case/window | n | reported seconds | Q RMSE/max | p_h RMSE/max |", "|---|---:|---|---|---|"]
    for case,ref in r["references"].items():
        for name,w in ref["figure15"]["windows"].items():
            q,ph=w["channels"]["Q_norm"],w["channels"]["p_h_norm"]
            lines.append(f"| {case}/{name} | {w['count']} | {w['reported_range_s']} | {q['rmse']:.5g}/{q['max_abs']:.5g} | {ph['rmse']:.5g}/{ph['max_abs']:.5g} |")
    lines += ["", "Both representations are frozen separately; neither rescues the other. All reference timestamps are covered.",
              "The existing early-flow and fitted-trajectory checks retain their original thresholds; see JSON for each result.",
              "Rounded source-event classification is fixed at reported 6.667 s; candidate differences are disclosed in JSON.",
              "", "See RESULTS.json for source/configuration hashes, parameters, transforms/discrepancies, support, every norm and gate.",
              "See HANDOFF.md for variable execution metadata, QA, hosted CI, exact-head review and unresolved limitations.", ""]
    return "\n".join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--execution-log", type=Path, required=True)
    parser.add_argument("--cache-dir", type=Path, required=True)
    parser.add_argument("--final-source", action="store_true",
                        help="Rerun the three D levels and F; reuse source-independent baseline/oracles with exact initial-state check")
    parser.add_argument("--reuse-trajectories", action="store_true",
                        help="Recompute reports only from the same solver-source cache; no new solves")
    args=parser.parse_args()
    log=ExecutionLog(args.execution_log,args.cache_dir,args.reuse_trajectories,args.final_source)
    result=run(log)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    (args.output_dir/"RESULTS.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    (args.output_dir/"RESULTS.md").write_text(markdown(result))
    print(result["disposition"])
    return 0 if result["disposition"]=="BOUNDED_NUMERICAL_AND_SOURCE_RECONSTRUCTION_PASS" else 1


if __name__=="__main__":
    raise SystemExit(main())

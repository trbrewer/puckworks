"""Bounded 001 observer qualification. Representative runs are outside CI.

Pannusch/Schmieder source-derived output CC-BY-NC-3.0; software license separate.
Uses the existing Git-common-directory reservation/receipt pattern.
"""
from __future__ import annotations

import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'

import argparse
import ast
from contextlib import contextmanager
import fcntl
import hashlib
import inspect
import math
from pathlib import Path
import platform
import resource
import signal
import subprocess
import sys
import time

import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.sparse.linalg import expm_multiply
from puckworks.models.pannusch2024 import stateful_fv as sf
from puckworks.models.pannusch2024 import flow_consistent_observer as ob
from tools import pannusch_flow_temp_fv_reference as ref
from tools import pannusch_stateful_fv_verification as old
from tools.pannusch_temperature_history_verification import read_json, write_json, digest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/'docs/analysis/model_pannusch2024_flow_consistent_observation_001'
TASK = 'MODEL-PANNUSCH2024-FLOW-CONSISTENT-OBSERVATION-001'
BASE = 'b9ad38c6ebfe96d90462254dfb664dd789036b31'
RIGHTS = old.RIGHTS


def authority_path():
    p = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], cwd=ROOT, text=True).strip())
    return (p if p.is_absolute() else ROOT/p)/'qualification-budgets'/(TASK+'.json')


@contextmanager
def locked_authority(directory):
    directory = Path(directory).resolve()
    path = authority_path(); path.parent.mkdir(parents=True, exist_ok=True)
    with path.with_suffix('.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if path.exists():
            ledger = read_json(path)
            if ledger['evidence_directory'] != str(directory):
                raise RuntimeError('TASK_BUDGET_ALREADY_BOUND_TO_DIFFERENT_DIRECTORY')
        else:
            ledger = dict(task=TASK, evidence_directory=str(directory), executions=[], auxiliary=[])
            directory.mkdir(parents=True, exist_ok=True)
            write_json(path, ledger)
        yield path, ledger


def reserve(ledger, *, correction=False, auxiliary=False):
    if not auxiliary and len(ledger['executions']) >= (36 if correction else 29):
        raise RuntimeError('EXECUTION_CEILING_OR_SEVEN_SLOT_RESERVE')
    remaining = 3600.-old.used(ledger)
    if remaining <= .1:
        raise RuntimeError('AGGREGATE_NUMERICAL_TIME_EXHAUSTED')
    return min(120., remaining)


def identities():
    paths = [ROOT/'puckworks/models/pannusch2024'/x for x in (
        'flow_consistent_observer.py', 'stateful_fv.py', 'flow_temperature_history_fv.py',
        'temperature_history_fv.py', 'temperature_history.py', 'flow_history.py', 'solver.py', 'closures.py')]
    paths += [ROOT/'puckworks/data/pannusch2024'/x for x in ('table2_fitted_params.csv', 'table2_grind_psi_ds2.csv')]
    paths += [Path(__file__), Path(old.__file__), Path(ref.__file__), BUNDLE/'CASES.json', BUNDLE/'CONTRACT.md']
    out = {str(p.relative_to(ROOT)): digest(p) for p in paths}
    out['numerical_runner_blocks'] = hashlib.sha256('\n'.join(inspect.getsource(f) for f in (
        authority_path, locked_authority, reserve, identities, load_case, _trajectory,
        _reference, run_case, worker, execute)).encode()).hexdigest()
    return out



def _guard_only_reuse(meta):
    """Narrow proof for the one independently reviewed validation correction.

    Original observations retain their producer/identity. No result is rebuilt
    or restamped. Legacy upstream/checkpoint sources must remain byte-identical.
    """
    producer='780fbda0edb27ffcd2bae85bc10650a41612df17'
    observer='puckworks/models/pannusch2024/flow_consistent_observer.py'
    runner='tools/pannusch_flow_consistent_verification.py'
    if meta['source_commit']!=producer:raise ValueError('UNSUPPORTED_REUSE_PRODUCER')
    original={p:subprocess.check_output(['git','show',producer+':'+p],cwd=ROOT).decode() for p in (observer,runner)}
    for path,source in original.items():
        if hashlib.sha256(source.encode()).hexdigest()!=meta['identities'][path]:
            raise ValueError('REUSE_PRODUCING_SOURCE_MISMATCH')
    old_tree=ast.parse(original[observer]);new_tree=ast.parse((ROOT/observer).read_text())
    guards=[f for f in new_tree.body if isinstance(f,ast.FunctionDef) and f.name=='_check_prior_accounting']
    if len(guards)!=1:raise ValueError('REUSE_GUARD_MISSING')
    new_tree.body.remove(guards[0])
    prefix=next(f for f in new_tree.body if isinstance(f,ast.FunctionDef) and f.name=='_checked_prefix')
    calls=[x for x in prefix.body if isinstance(x,ast.Expr) and isinstance(x.value,ast.Call)
           and isinstance(x.value.func,ast.Name) and x.value.func.id=='_check_prior_accounting']
    if len(calls)!=1:raise ValueError('REUSE_GUARD_CALL_MISMATCH')
    prefix.body.remove(calls[0])
    if ast.dump(old_tree)!=ast.dump(new_tree):raise ValueError('OBSERVER_NUMERICS_CHANGED')
    names=('authority_path','locked_authority','reserve','identities','load_case','_trajectory',
           '_reference','run_case','worker','execute')
    before={f.name:f for f in ast.parse(original[runner]).body if isinstance(f,ast.FunctionDef)}
    after={f.name:f for f in ast.parse(Path(__file__).read_text()).body if isinstance(f,ast.FunctionDef)}
    lines=original[runner].splitlines(keepends=True)
    def source(f):
        first=min([f.lineno,*[d.lineno for d in f.decorator_list]])
        return ''.join(lines[first-1:f.end_lineno])
    frozen=hashlib.sha256('\n'.join(source(before[n]) for n in names).encode()).hexdigest()
    if frozen!=meta['identities']['numerical_runner_blocks']:raise ValueError('REUSE_RUNNER_IDENTITY')
    if any(ast.dump(before[n])!=ast.dump(after[n]) for n in names if n!='load_case'):
        raise ValueError('REUSE_NUMERICAL_RUNNER_CHANGED')
    # Apply the new read-only guard to actual retained receipt inputs, without
    # manufacturing a StatefulFVResult or any current observer identity.
    if 'observer_result_sha256' in meta:
        plan=meta['plan'];times=plan['primary_times_s']
        start=int(np.searchsorted(times,meta['actual_span_s'][0]))
        flow=sf.FlowHistory(**plan['flow_history'])
        root=meta['root_state']
        inventory=sf._inventory(*(np.asarray(root[k]) for k in ('liquid_cell_average_kg_m3',
            'fine_cell_average_kg_m3','coarse_cell_average_kg_m3')),root['grind'])
        ob._check_prior_accounting(inventory,meta['mode'],start,
            meta['prior_mass_terms'],meta['prior_volume_terms'],flow,times)
    return dict(producer=producer,observer_ast_equal_without_added_guard=True,
        numerical_runner_ast_equal_except_checked_loader=True,new_guard_passed_on_receipt_inputs=True,
        checkpoint_policy='UPSTREAM_SOURCES_BYTE_IDENTICAL; CURRENT_CHECKPOINT_NOT_MIGRATED',
        original_observer_identity_preserved=meta.get('observer_result_sha256'))


def load_case(directory, case_id):
    rows = [r for r in read_json(Path(directory)/'executions.json') if r['case_id'] == case_id]
    if not rows or rows[-1]['status'] != 'COMPLETE':
        raise ValueError('MISSING_OR_FAILED_EXECUTION:'+case_id)
    row = rows[-1]; path = Path(directory)/(row['execution_id']+'.json')
    if digest(path) != row['receipt_sha256']:
        raise ValueError('RECEIPT_HASH_MISMATCH')
    m = read_json(path)
    if m['identities'] != row['identities'] or not m['coverage_complete']:
        raise ValueError('IDENTITY_OR_COVERAGE_MISMATCH')
    # Exact producing source remains authoritative even after report-only edits.
    observer='puckworks/models/pannusch2024/flow_consistent_observer.py'
    guard_reuse=m['identities'][observer]!=digest(ROOT/observer)
    if guard_reuse:_guard_only_reuse(m)
    for name, sha in m['identities'].items():
        if guard_reuse and name in (observer,'numerical_runner_blocks'):continue
        if name == 'numerical_runner_blocks':
            if identities()[name] != sha:raise ValueError('NUMERICAL_RUNNER_CHANGED')
            continue
        if name != str(Path(__file__).relative_to(ROOT)) and digest(ROOT/name) != sha:
            raise ValueError('NUMERICAL_DEPENDENCY_CHANGED:'+name)
    if digest(path.with_suffix('.npz')) != m['arrays_sha256']:
        raise ValueError('ARRAY_HASH_MISMATCH')
    with np.load(path.with_suffix('.npz'), allow_pickle=False) as z:
        arrays = {k:z[k] for k in z.files}
    if not all(np.isfinite(v).all() for v in arrays.values()):
        raise ValueError('NONFINITE_ARRAY')
    return m, arrays


def _trajectory(tr):
    return dict(times=tr.times_s, fields=old.fields_array(tr), local_mass=tr.segment_outlet_solute_kg,
        origin_mass=tr.origin_outlet_solute_kg, local_volume=tr.segment_volume_m3, origin_volume=tr.origin_volume_m3)


def _reference(case, c, p, observations, windows, initial, prior_m, prior_v):
    """New counted reference execution; independent physical-time concentrations.

    Keeps all original endpoint/phase samples. Dense output is sampled in chunks
    during its producing solve; only scalar quadrature output is retained.
    No candidate generator, clock, initialization or inventory routine is used.
    """
    n = case['cells']; start, stop = p.t_span_s
    endpoints = np.unique(np.concatenate([ref.primary_times(p.temperature_history, p.flow_history,
        (start, stop), h) for h in c['reference_primary_h_s']]))
    queries = np.unique(np.r_[observations, endpoints])
    values = np.empty((len(queries), 3*n+1))
    y = np.r_[initial.ravel(), 0.]
    values[queries == start] = y
    M = math.fsum((initial*old.capacities(n, c['grind'])[:, None]).ravel())
    C = float(np.max(initial))
    settings = c['reference_control'] if case.get('control') else c['radau']
    atol = np.r_[np.full(3*n, settings['scaled_atol']*C), settings['scaled_atol']*M]
    assemble = ref.operator_factory(case['solute'], c['grind'], n)
    diagnostic_t, diagnostic_y, records, quadrature = [start], [y.copy()], [], []
    rules = {order:np.polynomial.legendre.leggauss(order) for order in (4, 8)}
    ordered = case['method'] in ('ORDERED', 'BRANCH_REFERENCE')
    for a, b, ti, qi in ref.segments(p.temperature_history, p.flow_history, (start, stop)):
        def operator(t):
            return assemble(ref.value(p.temperature_history, t, interval=ti), ref.value(p.flow_history, t, interval=qi))
        ix = np.flatnonzero((queries > a) & (queries <= b))
        specs = []
        base = ref.primary_times(p.temperature_history, p.flow_history, (a,b), .02)
        for wi, (l,r) in enumerate(windows):
            lo, hi = max(a,l), min(b,r)
            if hi <= lo: continue
            edges = np.unique(np.r_[lo, base[(base>lo)&(base<hi)], hi])
            for left,right in zip(edges,edges[1:]):
                for order in (4,8):
                    nodes, weights = rules[order]
                    for node,weight in zip(nodes,weights):
                        specs.append((float(left+(right-left)*(node+1)/2),wi,order,float((right-left)*weight/2)))
        def record_quad(spec,z):
            t,wi,order,w = spec
            phases=z[:-1].reshape(3,n)
            bed=math.fsum((phases*old.capacities(n,c['grind'])[:,None]).ravel())
            quadrature.append((wi,order,t,w,ref.value(p.flow_history,t,interval=qi)*z[n-1],bed,z[-1],*np.min(phases,axis=1)))
        if ordered:
            A=operator(a); previous=a
            by_time={}
            for spec in specs:by_time.setdefault(spec[0],[]).append(spec)
            query_index={float(queries[j]):j for j in ix}
            # One independently assembled physical-time trajectory through a
            # sorted union; discard quadrature fields immediately after reduction.
            for t in sorted({b,*query_index,*by_time}):
                y=expm_multiply(A*(t-previous),y,traceA=float(A.diagonal().sum())*(t-previous))
                if t in query_index:
                    values[query_index[t]]=y
                    diagnostic_t.append(t);diagnostic_y.append(y.copy())
                for spec in by_time.get(t,()):record_quad(spec,y)
                previous=t
            records.append(dict(span_s=[a,b],method='independent ordered concentration exponentials'))
        else:
            sol=solve_ivp(lambda t,x:operator(t)@x,(a,b),y,method='Radau',
                jac=lambda t,x:operator(t),atol=atol,rtol=settings['rtol'],
                max_step=settings['max_step_s'],dense_output=True)
            if not sol.success or sol.t[-1]!=b:raise RuntimeError('REFERENCE_INCOMPLETE')
            values[ix]=sol.sol(queries[ix]).T;y=sol.y[:,-1].copy()
            dt=np.unique(np.r_[sol.t[1:],queries[ix]])
            diagnostic_t.extend(dt);diagnostic_y.extend(sol.sol(dt).T)
            records.append(dict(span_s=[a,b],accepted_steps=len(sol.t)-1,nfev=sol.nfev,nlu=sol.nlu))
            for j in range(0,len(specs),8):
                batch=specs[j:j+8]
                for spec,z in zip(batch,sol.sol([v[0] for v in batch]).T):record_quad(spec,z)
    observed, primary = values[np.searchsorted(queries, observations)], values[np.searchsorted(queries,endpoints)]
    vols = np.array([ref.volume(p.flow_history,start,t) for t in observations])
    q = np.asarray(quadrature).reshape(-1,10)
    delivered = np.array([math.fsum(q[(q[:,0]==i)&(q[:,1]==8),3]*q[(q[:,0]==i)&(q[:,1]==8),4]) for i in range(len(windows))])
    fraction_v = np.array([ref.volume(p.flow_history,*w) for w in windows])
    dc = np.asarray(diagnostic_y)
    arrays = dict(times=observations, fields=observed[:,:-1], local_mass=observed[:,-1], origin_mass=observed[:,-1]+prior_m,
        local_volume=vols, origin_volume=vols+prior_v, primary_times=endpoints, primary_fields=primary[:,:-1],
        primary_local_mass=primary[:,-1], primary_origin_mass=primary[:,-1]+prior_m,
        diagnostic_times=np.asarray(diagnostic_t), diagnostic_fields=dc[:,:-1], diagnostic_local_mass=dc[:,-1],
        reference_quadrature=q, fractions=delivered/fraction_v, fraction_mass=delivered, fraction_volume=fraction_v,
        # Historical cumulative-difference operator retained only as a comparator.
        cumulative_difference_fractions=np.array([(values[np.searchsorted(queries,r),-1]-values[np.searchsorted(queries,l),-1])/
                                                  ref.volume(p.flow_history,l,r) for l,r in windows]))
    return arrays, records


def run_case(directory, case, c, limit):
    started = time.monotonic(); p = old.case_plan(case,c); method = case['method']
    n = case['cells']; start, stop = p.t_span_s; cp = None; prior_m = prior_v = 0.
    if method in ('RESUME', 'BRANCH'):
        parent,_ = load_case(directory,case['parent'])
        path = Path(directory)/(parent['execution_id']+'.checkpoint.json')
        if digest(path) != parent['checkpoint_sha256']: raise ValueError('PARENT_CHECKPOINT_HASH')
        cp = sf.FVCheckpoint.from_json(path.read_text()); start = cp.time_s
        if method == 'RESUME':
            if cp.plan.identity_sha256 != p.identity_sha256: raise ValueError('PARENT_PLAN')
            p = cp.plan
    if method == 'PREFIX': stop = float(p.primary_times_s[case['checkpoint_index']])
    if method == 'BRANCH_REFERENCE': start = c['checkpoint']['S']['time_s']
    if method in ('BRANCH', 'BRANCH_REFERENCE'):
        p = sf.FVPlan(sf.TemperatureHistory.constant_celsius((start,stop),(case['future_T_C'],)),
            sf.FlowHistory((start,stop),(case['future_Q_m3_s'],),'constant'),(start,stop),p.settings)
    obs = np.asarray(c['observations_s']); obs = obs[(obs>=start)&(obs<=stop)]
    windows = np.asarray(c['fraction_windows_s']); windows = windows[(windows[:,0]>=start)&(windows[:,1]<=stop)]
    meta = dict(case=case, requested_span_s=[start,stop], root_time_s=0., windows=windows.tolist(),
        temperature_history=ref.raw_history(p.temperature_history),flow_history=ref.raw_history(p.flow_history),
        plan_sha256=p.identity_sha256,mode=method)
    exported = None
    if method in ('ORDERED','Radau','BRANCH_REFERENCE'):
        initial = ref.stateful_u_fields(case['solute'],n)
        if method == 'BRANCH_REFERENCE':
            parent,a = load_case(directory,case['parent']); i = np.flatnonzero(a['times']==start)
            if len(i)!=1: raise ValueError('INDEPENDENT_PARENT_ABSENT')
            initial = a['fields'][i[0]].reshape(3,n)
            prior_m, prior_v = float(a['origin_mass'][i[0]]), float(a['origin_volume'][i[0]])
        arrays, records = _reference(case,c,p,obs,windows,initial,prior_m,prior_v)
        meta.update(reference_records=records,status='COMPLETE',integration_complete=True,actual_span_s=[start,stop])
    elif method == 'BASE_003':
        r = sf.fv.simulate_flow_temperature_history_fv(p.temperature_history,flow_history=p.flow_history,
            t_span_s=(start,stop),solute=case['solute'],grind=c['grind'],observation_times_s=obs,
            fraction_bounds_s=np.unique(windows),settings=p.settings)
        tr = r.observations
        arrays=dict(times=tr.times_s,fields=old.fields_array(tr),local_mass=tr.outlet_solute_kg,origin_mass=tr.outlet_solute_kg,
            local_volume=tr.hydraulic_volume_m3,origin_volume=tr.hydraulic_volume_m3,primary_times=r.trace.times_s,
            primary_fields=r.trace.masses_kg[:,:-1]/np.repeat(r.phase_capacities_m3,n),primary_local_mass=r.trace.masses_kg[:,-1],
            primary_origin_mass=r.trace.masses_kg[:,-1],frozen_T=r.trace.frozen_temperature_K,frozen_Q=r.trace.frozen_flow_m3_s,
            fractions=np.array([(tr.outlet_solute_kg[np.searchsorted(obs,b)]-tr.outlet_solute_kg[np.searchsorted(obs,a)])/ref.volume(p.flow_history,a,b) for a,b in windows]))
        meta.update(status=r.status,integration_complete=r.integration_complete,actual_span_s=list(r.actual_span_s))
    else:
        kw=dict(plan=p,observation_times_s=obs,fraction_windows_s=windows,stop_time_s=stop)
        r=(sf.branch_stateful_fv(cp,**kw) if method=='BRANCH' else sf.simulate_stateful_fv(checkpoint=cp,**kw)) if cp else sf.simulate_stateful_fv(initial_state=old.candidate_state(case,p,c),**kw)
        remaining = max(.01, limit-(time.monotonic()-started)-3)
        remaining_actions=p.settings.max_exponential_applications-r.exponential_applications
        if remaining_actions < 1:raise RuntimeError('ATTACHED_EXPONENTIAL_APPLICATION_LIMIT')
        resources=sf.FVSettings(**{**sf.fv.th._json_value(p.settings),'wall_time_limit_s':min(120.,remaining),
                                   'max_exponential_applications':remaining_actions})
        z=ob.observe_flow_consistent_fv(r,observation_times_s=obs,fraction_windows_s=windows,resource_settings=resources)
        arrays=_trajectory(z.observations)
        for key,value in _trajectory(r.observations).items(): arrays['old_'+key]=value
        primary=r.primary
        arrays.update(primary_times=primary.times_s,primary_fields=old.fields_array(primary),primary_local_mass=primary.segment_outlet_solute_kg,
            primary_origin_mass=primary.origin_outlet_solute_kg,primary_local_volume=primary.segment_volume_m3,primary_origin_volume=primary.origin_volume_m3,
            raw_primary=r.raw_primary_masses_kg,step_mass=r.step_outlet_solute_kg,step_volume=r.step_volume_m3,exportable=r.exportable_primary,
            frozen_T=p.primary_steps[r.start_index:r.start_index+len(r.step_outlet_solute_kg),2],frozen_Q=p.primary_steps[r.start_index:r.start_index+len(r.step_outlet_solute_kg),3],
            fractions=np.array([f.concentration_kg_m3 for f in z.fractions],dtype=float),fraction_mass=np.array([f.solute_kg for f in z.fractions],dtype=float),
            fraction_volume=np.array([f.volume_m3 for f in z.fractions],dtype=float),old_fractions=np.array([f.concentration_kg_m3 for f in r.fractions],dtype=float),
            old_quadrature=r.raw_quadrature,old_diagnostic_times=r.raw_diagnostic_times_s,old_raw_diagnostic=r.raw_diagnostic_masses_kg,
            observer_checks=z.checks,clock_residuals=z.clock_residuals,observer_quadrature=z.quadrature,
            panels=np.array([[getattr(panel,f.name) for f in __import__('dataclasses').fields(panel)] for panel in z.panels],dtype=float))
        # Saved raw observation accumulators permit direct local restart reduction.
        times, idx=np.unique(np.r_[primary.times_s,z.observations.times_s],return_index=True)
        arrays.update(diagnostic_times=times,raw_diagnostic=np.vstack((r.raw_primary_masses_kg,z.raw_observation_masses_kg))[idx])
        shared,oi,pi=np.intersect1d(z.observations.times_s,r.primary.times_s,return_indices=True)
        endpoint_identity=bool(np.array_equal(old.fields_array(z.observations)[oi],old.fields_array(r.primary)[pi])
            and np.array_equal(z.observations.segment_outlet_solute_kg[oi],r.primary.segment_outlet_solute_kg[pi])
            and np.array_equal(z.observations.origin_outlet_solute_kg[oi],r.primary.origin_outlet_solute_kg[pi]))
        whole_identity=all(panel.solute_kg==r.step_outlet_solute_kg[panel.owner_index] for panel in z.panels
            if panel.start_s==r.primary.times_s[panel.owner_index] and panel.end_s==r.primary.times_s[panel.owner_index+1])
        meta.update(status=r.status,integration_complete=r.integration_complete,actual_span_s=[start,r.actual_end_s],mode=r.mode,
            parent_identity=r.parent_identity,upstream_result_sha256=r.identity_sha256,observer_result_sha256=z.identity_sha256,
            model_identity=r.root_state.model_identity,root_state=sf._json(r.root_state),plan=sf._json(p),
            prior_mass_terms=list(r.prior_outlet_terms_kg),prior_volume_terms=list(r.prior_volume_terms_m3),
            observer_support=z.request_support,observer_reason=z.reason,observer_admissibility=z.numerical_admissibility,
            fraction_status=[f.status for f in z.fractions],fraction_reason=[f.reason for f in z.fractions],
            propagations=r.propagations,exponential_applications=r.exponential_applications+z.exponential_applications,
            primary_unchanged=sf._hash(r)==r.identity_sha256 and endpoint_identity and whole_identity,
            observed_primary_endpoint_count=len(shared),observed_primary_identity=endpoint_identity,whole_step_identity=whole_identity,legacy_diagnostics=sf._json(r.diagnostics))
        if method=='PREFIX' and r.integration_complete:
            exported=r.checkpoint(stop).to_json()
            meta['checkpoint_identity']=r.checkpoint(stop).identity_sha256
    meta['coverage_complete']=bool(meta['integration_complete'] and meta['actual_span_s']==[start,stop]
        and np.array_equal(arrays['times'],obs) and all(np.isfinite(v).all() for v in arrays.values())
        and meta.get('observer_support','COMPLETE')=='COMPLETE')
    return meta,arrays,exported


def worker(directory,case_id,eid):
    directory=Path(directory); rows=read_json(directory/'executions.json')
    row=next(e for e in rows if e['execution_id']==eid)
    if row['status']!='LAUNCHED' or row['case_id']!=case_id or row['identities']!=identities(): raise RuntimeError('UNRESERVED_OR_CHANGED_WORKER')
    with (directory/(eid+'.claim')).open('x') as f:f.write(case_id+'\n')
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    limit=max(.01,row['reserved_wall_s']-1)
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NUMERICAL_WALL_CEILING')))
    signal.setitimer(signal.ITIMER_REAL,limit)
    c=read_json(BUNDLE/'CASES.json');case=next(x for x in c['cases'] if x['id']==case_id)
    started=time.monotonic();arrays={}; complete=False
    meta=dict(task=TASK,execution_id=eid,case=case,identities=identities(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        source_tree=subprocess.check_output(['git','rev-parse','HEAD^{tree}'],cwd=ROOT,text=True).strip(),
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),rights=RIGHTS,
        scope='RESEARCH_ONLY',PHYSICAL_VALIDATION='NOT_ESTABLISHED')
    try:
        info,arrays,cp=run_case(directory,case,c,limit);meta.update(info)
        if cp is not None:
            path=directory/(eid+'.checkpoint.json');path.write_text(cp);meta['checkpoint_sha256']=digest(path)
        complete=meta['coverage_complete']
    except Exception as exc:
        import traceback
        traceback.print_exc();meta.update(status='FAILED',reason=type(exc).__name__+':'+str(exc),coverage_complete=False)
    np.savez_compressed(directory/(eid+'.npz'),**arrays)
    meta.update(arrays_sha256=digest(directory/(eid+'.npz')),numerical_wall_s=time.monotonic()-started,
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    write_json(directory/(eid+'.json'),meta);signal.setitimer(signal.ITIMER_REAL,0)
    return 0 if complete else 2


def execute(directory,case_id=None,correction=False):
    directory=Path(directory).resolve()
    with locked_authority(directory) as (path,ledger):
        cases=read_json(BUNDLE/'CASES.json')['cases']
        if correction and case_id is None: raise ValueError('NAMED_CORRECTION_REQUIRED')
        if case_id is not None and case_id not in {x['id'] for x in cases}: raise ValueError('UNKNOWN_CASE')
        for case in cases:
            if case_id is not None and case['id']!=case_id:continue
            if not correction and any(e['case_id']==case['id'] for e in ledger['executions']):continue
            limit=reserve(ledger,correction=correction);eid=f"exec-{len(ledger['executions'])+1:03d}"
            row=dict(execution_id=eid,case_id=case['id'],status='LAUNCHED',reserved_wall_s=limit,identities=identities(),correction=correction)
            ledger['executions'].append(row);write_json(path,ledger);write_json(directory/'executions.json',ledger['executions'])
            started=time.monotonic()
            try:
                with (directory/(eid+'.log')).open('w') as log:
                    done=subprocess.run([sys.executable,'-m','tools.pannusch_flow_consistent_verification','worker',
                        '--evidence-dir',str(directory),'--case-id',case['id'],'--execution-id',eid],cwd=ROOT,
                        env=os.environ.copy(),stdout=log,stderr=subprocess.STDOUT,timeout=limit)
                row.update(status='COMPLETE' if done.returncode==0 else 'FAILED',returncode=done.returncode)
            except subprocess.TimeoutExpired:row['status']='TIMEOUT'
            except BaseException:row['status']='CANCELLED';raise
            finally:
                row['charged_wall_s']=time.monotonic()-started
                if (directory/(eid+'.json')).exists():row['receipt_sha256']=digest(directory/(eid+'.json'))
                write_json(path,ledger);write_json(directory/'executions.json',ledger['executions'])
                print(eid,case['id'],row['status'],round(row['charged_wall_s'],3),'s; aggregate',round(old.used(ledger),3),flush=True)
            if row['status']!='COMPLETE':break  # No automatic retry or cascading failed parents.


def auxiliary(directory,kind,operation):
    resource.setrlimit(resource.RLIMIT_AS,(2*1024**3,2*1024**3))
    with locked_authority(directory) as (path,ledger):
        limit=reserve(ledger,auxiliary=True)
        row=dict(kind=kind,status='LAUNCHED',reserved_wall_s=limit);ledger['auxiliary'].append(row);write_json(path,ledger)
        start=time.monotonic()
        signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('AUXILIARY_WALL_LIMIT')))
        signal.setitimer(signal.ITIMER_REAL,limit)
        try:
            result=operation();row['status']='COMPLETE';return result
        except BaseException:row['status']='FAILED';raise
        finally:
            signal.setitimer(signal.ITIMER_REAL,0);row['charged_wall_s']=time.monotonic()-start;write_json(path,ledger)
            public={k:v for k,v in ledger.items() if k!='evidence_directory'}
            public['charged_total_wall_s']=old.used(ledger)
            write_json(BUNDLE/'RESOURCES.json',public)


def audit_reuse(directory):
    """Verify original evidence, never load it as a current result/checkpoint."""
    proof=read_json(old.BUNDLE/'EVIDENCE_REUSE.json')
    previous=read_json(old.authority_path())
    archived=Path(previous['evidence_directory'])
    verified=[]
    for item in proof['original_artifacts']:
        eid=item['execution_id']; receipt=archived/(eid+'.json')
        if digest(receipt)!=item['receipt_sha256'] or digest(receipt.with_suffix('.npz'))!=item['arrays_sha256']:
            raise ValueError('ORIGINAL_ARCHIVE_HASH_MISMATCH')
        m=read_json(receipt)
        if m['source_commit']!=proof['original_producer_commit'] or m['identities']!=proof['original_producer_identities']:
            raise ValueError('ORIGINAL_PRODUCER_MISMATCH')
        if not m['coverage_complete']:raise ValueError('ORIGINAL_UNCHECKED_SUPPORT')
        case=next(x for x in read_json(old.BUNDLE/'CASES.json')['cases'] if x['id']==item['case_id'])
        if m['case']!=case or m['plan_sha256']!=old.case_plan(case,read_json(old.BUNDLE/'CASES.json')).identity_sha256:
            # Branch plans intentionally replace future forcing.
            if case['method'] not in ('BRANCH','BRANCH_REFERENCE'):raise ValueError('ORIGINAL_INPUT_PLAN_MISMATCH')
        with np.load(receipt.with_suffix('.npz'),allow_pickle=False) as z:
            if not all(np.isfinite(z[k]).all() for k in z.files):raise ValueError('ORIGINAL_NONFINITE_ARRAY')
            if 'exportable' in z and not np.all(z['exportable']):raise ValueError('ORIGINAL_INADMISSIBLE_SUPPORT')
            if z['primary_times'][-1]!=m['actual_span_s'][1]:raise ValueError('ORIGINAL_CHECKED_END_MISMATCH')
        if 'checkpoint_sha256' in m and digest(archived/(eid+'.checkpoint.json'))!=m['checkpoint_sha256']:
            raise ValueError('ORIGINAL_CHECKPOINT_ARTIFACT_MISMATCH')
        verified.append(dict(case_id=item['case_id'],receipt_sha256=item['receipt_sha256'],arrays_sha256=item['arrays_sha256'],producer=m['source_commit']))
    # Dependency bytes must be the exact constructor-corrected pair, no broad waiver.
    for path,sha in proof['corrected_producer_identities'].items():
        if path not in ('pinned_base','worker_and_reservation_blocks') and digest(ROOT/path)!=sha:
            raise ValueError('CORRECTED_DEPENDENCY_MISMATCH:'+path)
    intake=read_json(old.BUNDLE/'INTAKE.json')
    reused_sources={}
    for path,sha in intake['source_reuse_hashes'].items():
        if '/model_pannusch' in path or '/pannusch2024/' in path:
            if digest(ROOT/path)!=sha:raise ValueError('SOURCE_REUSE_MISMATCH')
            reused_sources[path]=sha
    record=dict(task=TASK,all_original_artifacts_verified=verified,source_reuse=reused_sources,
        prior_original_inspections_reused=intake['prior_original_inspections_reused'],original_files_inspected_this_task=[],
        historical_producer=proof['original_producer_commit'],evidence_reuse_sha256=digest(old.BUNDLE/'EVIDENCE_REUSE.json'),
        diagnostic_sha256=digest(old.BUNDLE/'DIAGNOSTIC.json'),mapping={f:'NEW_EXECUTION; original settings and reducers retained' for f in 'ABCDEF'},
        checkpoint_policy='HISTORICAL_ARTIFACT_ONLY; NO_MIGRATION; new current-source prefix/suffix',
        PHYSICAL_VALIDATION='NOT_ESTABLISHED',rights=RIGHTS)
    write_json(BUNDLE/'EVIDENCE_REUSE.json',record)
    return record



def audit_guard_reuse(directory):
    """Charged source/input/array audit before three affected correction runs."""
    proof=read_json(BUNDLE/'EVIDENCE_REUSE.json');rows=[]
    for case in read_json(BUNDLE/'CASES.json')['cases']:
        meta,arrays=load_case(directory,case['id'])
        entry=_guard_only_reuse(meta)
        entry.update(case_id=case['id'],arrays_sha256=meta['arrays_sha256'],
            source_identities=meta['identities'],upstream_result_sha256=meta.get('upstream_result_sha256'),
            plan_sha256=meta['plan_sha256'])
        if 'checkpoint_sha256' in meta:
            path=Path(directory)/(meta['execution_id']+'.checkpoint.json')
            if digest(path)!=meta['checkpoint_sha256']:raise ValueError('REUSE_CURRENT_CHECKPOINT_BYTES')
            cp=sf.FVCheckpoint.from_json(path.read_text())
            if cp.identity_sha256!=meta['checkpoint_identity']:raise ValueError('REUSE_CURRENT_CHECKPOINT_IDENTITY')
            entry['unchanged_current_source_checkpoint_validated']=cp.identity_sha256
        rows.append(entry);del arrays
    proof['independent_review_guard_correction']=dict(
        finding='Prior signed delivery and same-schedule volume-tail checkpoint invariants missing',
        observer_source_sha256=digest(Path(ob.__file__)),runner_source_sha256=digest(Path(__file__)),
        frozen_contract_unchanged=True,original_records_retained=rows,
        correction_cases=['C.caffeine.RESUME','D.caffeine.RESUME','E.caffeine.BRANCH'],
        scope='Validation-only reuse, no altered numerical expression or old result/current identity fabrication')
    write_json(BUNDLE/'EVIDENCE_REUSE.json',proof)
    return proof


def _old_arrays(a):
    legacy=dict(a)
    for name in ('times','fields','local_mass','origin_mass','local_volume','origin_volume','fractions','quadrature','diagnostic_times','raw_diagnostic'):
        if 'old_'+name in a:legacy[name]=a['old_'+name]
    return legacy


def _observer_account(meta,a,c):
    n=meta['case']['cells'];scales=old.fixed_scales(meta,a,c)
    C,M,LC,LM=(scales[k] for k in ('Cstar','Mstar','local_Cstar','local_Mstar'))
    z=a['observer_checks'];panels=a['panels'];q=a['observer_quadrature']
    base=old.accounting(meta,a,c)
    interval_inventory=old.inventory(a['primary_fields'],n,c['grind'])[z[:,8].astype(int)]
    base['new_interval_inventory']=old.metric(z[:,1]/interval_inventory,1.,1e-8)
    base['new_interval_inventory']['signed_absolute_kg']=dict(initial=float(z[0,1]),final=float(z[-1,1]),minimum=float(min(z[:,1])),maximum=float(max(z[:,1])))
    cumulative=[math.fsum((*a['step_mass'][:int(row[8])],float(row[7]))) for row in z]
    indices=np.argsort(z[:,0],kind='stable')
    base['new_chronological_delivery']=old.metric(np.minimum(np.diff(np.asarray(cumulative)[indices]),0.),LM,1e-10)
    base['new_local_inventory']=old.metric(z[:,2],LM,1e-8)
    base['new_root_inventory']=old.metric(z[:,3],M,1e-8)
    base['new_phase_positivity']=old.metric(np.minimum(z[:,4:7],0),LC,1e-10)
    base['new_delivery_positivity']=old.metric(np.minimum(z[:,7],0),LM,1e-10)
    base['clock_volume']=old.metric(a['clock_residuals'][:,2],1.,ob.CLOCK_RTOL)
    base['clock_endpoint']=old.metric(a['clock_residuals'][:,3],1.,ob.CLOCK_RTOL)
    # Reconstruct actual Q independently of runtime FlowHistory and volume clock.
    actual_q=np.array([ref.value(meta['flow_history'],float(t),interval=min(
        int(np.searchsorted(meta['flow_history']['times_s'],float(a['primary_times'][int(owner)]),side='right'))-1,
        len(meta['flow_history']['times_s'])-2)) for owner,t in zip(q[:,0],q[:,4])])
    rows=[]
    full_g8=[];full_g4=[];full_dm=[]
    for panel in panels:
        owner,l,h,dm,dv=panel[:5]
        values={}
        for order in (4,8):
            select=(q[:,0]==owner)&(q[:,1]==l)&(q[:,2]==h)&(q[:,3]==order)
            if np.count_nonzero(select)!=order:raise ValueError('NEW_QUADRATURE_COVERAGE')
            values[order]=math.fsum(q[select,5]*q[select,6]*actual_q[select])
        expected_v=ref.volume(meta['flow_history'],l,h)
        err=values[8]-dm;control=values[8]-values[4]
        tolerance=max(ob.LOCAL_FLUX_CSCALE*C*expected_v,ob.COMPOSITION_RTOL*abs(dm))
        rows.append(dict(window=[float(l),float(h)],owner=int(owner),mass_kg=float(dm),volume_m3=float(dv),
            actual_Q_GL8_kg=values[8],actual_Q_GL4_kg=values[4],frozen_Q_GL8_kg=float(panel[7]),
            residual_kg=err,residual_concentration_over_Cstar=err/expected_v/C,GL8_GL4_kg=control,
            local_allowance_kg=tolerance,passed=abs(err)<=tolerance and abs(control)<=tolerance,
            volume_relative=(dv-expected_v)/expected_v,composition_residual_kg=float(panel[9])))
        i=int(owner)
        if l==a['primary_times'][i] and h==a['primary_times'][i+1]:
            full_g8.append(values[8]);full_g4.append(values[4]);full_dm.append(dm)
    # Original root/local scale flux criterion, plus stringent local panel tests.
    base['actual_Q_flux']=old.metric(np.cumsum(np.asarray(full_g8)-full_dm),M,1e-6)
    base['actual_Q_GL8_GL4']=old.metric(np.cumsum(np.asarray(full_g8)-full_g4),M,1e-6)
    base['all_local_actual_Q_closure']=dict(passed=all(x['passed'] for x in rows),operator='NEW_ACTUAL_Q_VOLUME_CLOCK',
        maximum_absolute_kg=max(abs(x['residual_kg']) for x in rows),
        maximum_concentration_scaled=max(abs(x['residual_concentration_over_Cstar']) for x in rows))
    base['analytic_local_volume']=old.metric([x['volume_relative'] for x in rows],1.,1e-12)
    base['primary_endpoint_whole_step_identity']=dict(passed=meta['primary_unchanged'])
    fraction_rows=[]
    for (l,h),mass,volume in zip(meta['windows'],a['fraction_mass'],a['fraction_volume']):
        parts=[x for x in rows if l<=x['window'][0]<x['window'][1]<=h and
               x['window']==[max(l,float(a['primary_times'][x['owner']])),min(h,float(a['primary_times'][x['owner']+1]))]]
        total=math.fsum(x['actual_Q_GL8_kg'] for x in parts)
        control=math.fsum(x['GL8_GL4_kg'] for x in parts)
        tol=max(ob.LOCAL_FLUX_CSCALE*C*volume,ob.COMPOSITION_RTOL*abs(mass))
        fraction_rows.append(dict(window=[l,h],direct_mass_kg=float(mass),volume_m3=float(volume),actual_Q_GL8_kg=total,
            closure_kg=total-mass,closure_concentration_over_Cstar=(total-mass)/volume/C,GL8_GL4_kg=control,
            allowance_kg=tol,passed=abs(total-mass)<=tol and abs(control)<=tol))
    base['all_fraction_actual_Q_closure']=dict(passed=all(x['passed'] for x in fraction_rows),fractions=fraction_rows)
    base['passed']=all(v.get('passed',True) for v in base.values() if isinstance(v,dict))
    return base


def _reference_account(meta,a,c):
    base=old.accounting(meta,a,c);s=old.fixed_scales(meta,a,c)
    q=a['reference_quadrature'];M=s['Mstar'];LM=s['local_Mstar'];C=s['Cstar']
    prior=a['origin_mass'][0]
    base['actual_Q_quadrature_inventory']=old.metric(q[:,5]+q[:,6]-LM,LM,1e-8)
    base['actual_Q_quadrature_origin_inventory']=old.metric(q[:,5]+q[:,6]+prior-M,M,1e-8)
    base['quadrature_phase_positivity']=old.metric(np.minimum(q[:,7:10],0),C,1e-10)
    controls=[]
    for i in range(len(meta['windows'])):
        vals=[math.fsum(q[(q[:,0]==i)&(q[:,1]==order),3]*q[(q[:,0]==i)&(q[:,1]==order),4]) for order in (4,8)]
        controls.append(vals[1]-vals[0])
    base['reference_GL8_GL4']=old.metric(controls,M,1e-6)
    base['reference_local_GL8_GL4']=old.metric(np.array(controls)/a['fraction_volume'],C,2e-11)
    base['reference_flux_vs_integrated_outlet']=old.metric(a['fractions']-a['cumulative_difference_fractions'],C,1e-8)
    base['passed']=all(v.get('passed',True) for v in base.values() if isinstance(v,dict))
    return base



def _repeat_arrays(directory, left, right):
    """Compare every saved numerical array, streaming one pair at a time.

    Caller has verified producer, receipt, source and array identities. Check
    artifact bytes again here; runtime metadata is deliberately separate.
    """
    paths=[Path(directory)/(m['execution_id']+'.npz') for m in (left,right)]
    for path,meta in zip(paths,(left,right)):
        if digest(path)!=meta['arrays_sha256']:raise ValueError('REPEAT_ARRAY_HASH_MISMATCH')
    with np.load(paths[0],allow_pickle=False) as a, np.load(paths[1],allow_pickle=False) as b:
        checks={'same_array_keys':set(a.files)==set(b.files)}
        checks.update({key:bool(key in b.files and np.array_equal(a[key],b[key])) for key in a.files})
    return checks


def reduce_report(directory):
    c=read_json(BUNDLE/'CASES.json');data={};missing={}
    checks={};comparisons={};old_comparisons={};accounts={};old_accounts={}
    for case in c['cases']:
        name=case['id']
        try:m,a=load_case(directory,name)
        except (OSError,ValueError,KeyError) as exc:
            missing[name]=str(exc);continue
        accounts[name]=(_observer_account(m,a,c) if 'observer_checks' in a else
                        _reference_account(m,a,c) if 'reference_quadrature' in a else old.accounting(m,a,c))
        if 'old_fields' in a:
            legacy=_old_arrays(a);legacy.pop('quadrature',None)
            old_accounts[name]=old.accounting(m,legacy,c)
            q=a['old_quadrature'];full=q[:,5].astype(bool)
            old_accounts[name]['frozen_Q_full_flux_diagnostic_kg']=float(math.fsum(q[full&(q[:,2]==8),1]*q[full&(q[:,2]==8),6])-math.fsum(a['step_mass']))
            old_accounts[name]['actual_Q_full_flux_diagnostic_kg']=float(math.fsum(q[full&(q[:,2]==8),1]*q[full&(q[:,2]==8),7])-math.fsum(a['step_mass']))
            keep=np.isin(a['old_diagnostic_times'],np.r_[a['times'],a['primary_times']])
            a['old_diagnostic_times']=a['old_diagnostic_times'][keep]
            a['old_raw_diagnostic']=a['old_raw_diagnostic'][keep]
            del legacy,q
        # Discard full sampling evidence only after reduction. Arrays and hashes
        # remain in the external producer artifact, not fabricated/interpolated.
        for key in ('observer_quadrature','observer_checks','panels','old_quadrature',
                    'reference_quadrature','diagnostic_fields','diagnostic_local_mass'):
            a.pop(key,None)
        # Only restart comparisons need local raw accumulators. Preserve their
        # exact samples; other cases retain phase/endpoint fields for all gates.
        if name not in ('B.caffeine.U','C.caffeine.PREFIX','C.caffeine.RESUME',
                        'D.default','D.caffeine.PREFIX','D.caffeine.RESUME'):
            for key in ('raw_primary','raw_diagnostic','old_raw_diagnostic',
                        'diagnostic_times','old_diagnostic_times'):
                a.pop(key,None)
        data[name]=(m,a)
    def pair(name,left,right,tol,**kwargs):
        if left not in data or right not in data:
            comparisons[name]=dict(passed=False,reason='MISSING_REQUIRED_EXECUTION');checks[name]=False;return
        ma,a=data[left];mb,b=data[right]
        comparisons[name]=old.compare(ma,a,mb,b,c,tol,**kwargs)
        old_comparisons[name]=old.compare(ma,_old_arrays(a),mb,_old_arrays(b),c,tol,**kwargs)
        checks[name]=comparisons[name]['passed']
    for sp in sf.fv.th.SPECIES:
        pair('equilibrium.'+sp,'A.'+sp+'.BASE_003','A.'+sp+'.EQUILIBRIUM',1e-12)
        pair('supplied_reference.'+sp,'B.'+sp+'.U','B.'+sp+'.ORDERED',1e-8)
    for hist,pre,res,full in [('S','C.caffeine.PREFIX','C.caffeine.RESUME','B.caffeine.U'),('L','D.caffeine.PREFIX','D.caffeine.RESUME','D.default')]:
        pair(hist+'.prefix',pre,full,1e-12,restart=True);pair(hist+'.resume',res,full,1e-12,restart=True)
        if all(x in data for x in (pre,res,full)):
            pm,pa=data[pre];sm,sa=data[res]
            lineage=sm['parent_identity']==pm['checkpoint_identity'] and pm['root_state']==sm['root_state']
            comparisons[hist+'.recombination']=old.recombination(data[pre],data[res],data[full],c['checkpoint'][hist]['time_s'])
            comparisons[hist+'.recombination']['lineage_checked']=lineage
            checks[hist+'.recombination']=comparisons[hist+'.recombination']['passed'] and lineage
        else:checks[hist+'.recombination']=False
    pair('branch_reference','E.caffeine.BRANCH','E.caffeine.BRANCH_REFERENCE',1e-8)
    pair('default_finer','D.default','D.fine',5e-4)
    for level in ('coarse','default','fine'):pair('Radau.'+level,'D.'+level,'D.caffeine.Radau',5e-4)
    checks.pop('Radau.coarse',None)
    pair('reference_resolution','D.caffeine.Radau','D.caffeine.Radau.control',1e-8)
    uncertainty=comparisons.get('reference_resolution',{}).get('aggregate_scaled_error')
    errors=[comparisons.get('Radau.'+k,{}).get('aggregate_scaled_error') for k in ('coarse','default','fine')]
    raw_decrease=all(x is not None for x in errors) and all(x<=1e-10 or y<x for x,y in zip(errors,errors[1:]))
    resolved=uncertainty is not None and uncertainty<=min(1e-8,.01*5e-4)
    ordering=raw_decrease and resolved and all(x<=1e-10 or y+2*uncertainty<x-2*uncertainty for x,y in zip(errors,errors[1:]))
    checks['resolved_temporal_decrease']=bool(ordering)
    comparisons['reference_ordering_control']=dict(errors=errors,control_difference=uncertainty,raw_decrease=raw_decrease,
        status='PASS' if ordering else 'UNRESOLVED' if raw_decrease else 'FAIL',rigorous_error_certificate=False)
    if all(k in data for k in ('D.default','D.N800')):
        comparisons['mesh']=old.spatial(*data['D.default'],*data['D.N800'],c);checks['mesh']=comparisons['mesh']['passed']
    else:checks['mesh']=False
    if all(k in data for k in ('D.default','F.repeat')):
        comparisons['repeat']=_repeat_arrays(directory,data['D.default'][0],data['F.repeat'][0])
        checks['deterministic_repeat']=all(comparisons['repeat'].values())
    else:checks['deterministic_repeat']=False
    checks['all_independent_accounting']=len(accounts)==29 and all(v['passed'] for v in accounts.values())
    checks['full_coverage']=len(data)==29 and not missing
    # All old/new/reference fraction values and errors, including the controlling
    # short window. Complete phase arrays remain externally hash-bound.
    fractions={};channel_samples={}
    for level in ('coarse','default','fine'):
        name='D.'+level
        if name not in data or 'D.caffeine.Radau' not in data:continue
        m,a=data[name];rm,b=data['D.caffeine.Radau'];scales=old.fixed_scales(m,a,c);C=scales['Cstar']
        fractions[level]=[dict(window=w,old=float(o),new=float(n),reference=float(r),old_error_over_Cstar=float((o-r)/C),new_error_over_Cstar=float((n-r)/C))
            for w,o,n,r in zip(m['windows'],a['old_fractions'],a['fractions'],b['fractions'])]
        channel_samples[level]=[]
        for i,t in enumerate(a['times']):
            j=int(np.searchsorted(b['times'],t));n=m['case']['cells']
            item=dict(time_s=float(t),outlet=dict(old=float(a['old_fields'][i,n-1]),new=float(a['fields'][i,n-1]),reference=float(b['fields'][j,n-1])),
                origin_mass=dict(old=float(a['old_origin_mass'][i]),new=float(a['origin_mass'][i]),reference=float(b['origin_mass'][j])),
                volume=dict(old=float(a['old_origin_volume'][i]),new=float(a['origin_volume'][i]),reference=float(b['origin_volume'][j])))
            for phase,k in [('liquid',0),('fine',1),('coarse',2)]:
                item[phase]=dict(old_max_error_over_Cstar=float(np.max(abs(a['old_fields'][i,k*n:(k+1)*n]-b['fields'][j,k*n:(k+1)*n]))/C),
                    new_max_error_over_Cstar=float(np.max(abs(a['fields'][i,k*n:(k+1)*n]-b['fields'][j,k*n:(k+1)*n]))/C))
            channel_samples[level].append(item)
    success=all(checks.values())
    dispositions=dict(implementation='IMPLEMENTED',numerical_qualification='VERIFIED_ON_DECLARED_CASES' if success else 'IMPLEMENTED_QUALIFICATION_INCOMPLETE',
        conservation='PASS' if checks['all_independent_accounting'] else 'INCOMPLETE_OR_FAILED',
        actual_flow_consistency='PASS' if accounts and all(v.get('all_fraction_actual_Q_closure',{'passed':True})['passed'] for v in accounts.values()) and checks['full_coverage'] else 'INCOMPLETE_OR_FAILED',
        temporal='PASS' if all(checks.get(k,False) for k in ('default_finer','Radau.default','Radau.fine','resolved_temporal_decrease','reference_resolution')) else 'INCOMPLETE_OR_FAILED',
        mesh_sensitivity='PASS' if checks['mesh'] else 'INCOMPLETE_OR_FAILED',
        continuation='PASS' if all(checks.get(h+'.'+x,False) for h in ('S','L') for x in ('prefix','resume','recombination')) else 'INCOMPLETE_OR_FAILED',
        branching='PASS' if checks.get('branch_reference') else 'INCOMPLETE_OR_FAILED',software_QA='SEPARATE_QA_RECEIPT',hosted_CI='PENDING',independent_review='PENDING_EXACT_HEAD')
    record=dict(task=TASK,method=ob.METHOD,dispositions=dispositions,gates=checks,comparisons=comparisons,old_comparisons=old_comparisons,
        accounting=accounts,old_accounting=old_accounts,each_fraction=fractions,channel_samples=channel_samples,missing=missing,
        producers={k:dict(commit=m['source_commit'],tree=m['source_tree'],upstream=m.get('upstream_result_sha256'),observer=m.get('observer_result_sha256'),
            arrays_sha256=m['arrays_sha256'],execution_id=m['execution_id']) for k,(m,a) in data.items()},
        runtime_accuracy='NOT_ASSESSED',PHYSICAL_VALIDATION='NOT_ESTABLISHED',scope='RESEARCH_ONLY',rights=RIGHTS)
    record=sf._json(record)  # Preserve finite values; normalize NumPy scalar booleans.
    write_json(BUNDLE/'RESULTS.json',record)
    lines=['# Flow-consistent observer results','', '**'+dispositions['numerical_qualification']+'**; '+ob.METHOD+'.',
        'G2 / NUMERICAL_METHOD_CHANGE / RESEARCH_ONLY. Runtime accuracy NOT_ASSESSED.',
        'PHYSICAL_VALIDATION=NOT_ESTABLISHED. Historical 004 remains failed.','', '| Check | Disposition |','|---|---|']
    lines += [f"| {k} | {'PASS' if v else 'FAIL / INCOMPLETE / UNRESOLVED'} |" for k,v in checks.items()]
    lines += ['', '| Comparison | Liquid | Fine | Coarse | Outlet | Root mass | Fractions |','|---|---:|---:|---:|---:|---:|---:|']
    for key,r in comparisons.items():
        if 'aggregate_scaled_error' in r:lines.append('| '+key+' | '+' | '.join(f"{r[k]['maximum_scaled']:.9g}" for k in ('liquid','fine','coarse','outlet','origin_mass','fractions'))+' |')
    lines += ['', 'Errors above use original fixed C*/M* scales and reducers. All 86 observation channels, original primary endpoint comparisons,',
        'all 17 old/new/reference fractions at all three levels, signed accounting and all gates are in RESULTS.json.',
        'Hash-bound full phase arrays and logs are external. New reference fractions use physical-time actual-Q quadrature;',
        'cumulative-difference reference fractions are separately retained as a diagnostic.','',
        '| h (s) | Old controlling fraction | New | Reference | Old signed error / C* | New signed error / C* |',
        '|---|---:|---:|---:|---:|---:|']
    for level,h in [('coarse',.04),('default',.02),('fine',.01)]:
        if level in fractions:
            f=fractions[level][2];lines.append(f"| {h} | {f['old']:.12g} | {f['new']:.12g} | {f['reference']:.12g} | {f['old_error_over_Cstar']:.9g} | {f['new_error_over_Cstar']:.9g} |")
    lines += ['', 'N400/N800 is bounded mesh sensitivity, not continuum or physical validation.',
        'Software QA, hosted checks and one independent nonhuman exact-head review are separately reported.',
        'No merge, adoption, EWP/default/lock change, envelope extension, fit, score or successor.', '', RIGHTS+'.','']
    (BUNDLE/'RESULTS.md').write_text('\n'.join(lines))
    return record


def main():
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['execute','worker','audit','audit-guard','report'])
    parser.add_argument('--evidence-dir',type=Path,required=True);parser.add_argument('--case-id');parser.add_argument('--execution-id')
    parser.add_argument('--correction',action='store_true');args=parser.parse_args()
    if args.command=='execute':execute(args.evidence_dir,args.case_id,args.correction)
    elif args.command=='worker':return worker(args.evidence_dir,args.case_id,args.execution_id)
    elif args.command=='audit':auxiliary(args.evidence_dir,'VERIFIED_ARCHIVE_REUSE',lambda:audit_reuse(args.evidence_dir))
    elif args.command=='audit-guard':auxiliary(args.evidence_dir,'GUARD_ONLY_EVIDENCE_REUSE',lambda:audit_guard_reuse(args.evidence_dir))
    else:auxiliary(args.evidence_dir,'REPORT_ONLY',lambda:reduce_report(args.evidence_dir))
    return 0


if __name__=='__main__':raise SystemExit(main())

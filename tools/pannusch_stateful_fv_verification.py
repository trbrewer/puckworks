"""004 bounded campaign; full qualification is never an ordinary CI test.

Uses the existing Git-common-directory budget/receipt pattern. Numerical data
remain outside Git. Pannusch source-derived output: CC-BY-NC-3.0.
"""
from __future__ import annotations

import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS'):
    os.environ[_name] = '1'

import argparse
from contextlib import contextmanager
import fcntl
import hashlib
import importlib.util
import inspect
import json
import math
from pathlib import Path
import platform
import signal
import subprocess
import sys
import time

import numpy as np
import scipy
from puckworks.models.pannusch2024 import stateful_fv as sf
from tools import pannusch_flow_temp_fv_reference as ref
from tools.pannusch_temperature_history_verification import read_json, write_json, digest

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/'docs/analysis/model_pannusch2024_stateful_fv_004'
TASK = 'MODEL-PANNUSCH2024-STATEFUL-FV-004'
BASE = '58b6cd2f29af3fa4372119ba59f8a6a1446369cc'
RIGHTS = 'Pannusch et al., 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived output; first-party software licensing separate'


def authority_path():
    p = Path(subprocess.check_output(['git', 'rev-parse', '--git-common-dir'], cwd=ROOT, text=True).strip())
    return (p if p.is_absolute() else ROOT/p)/'qualification-budgets'/(TASK+'.json')


def used(ledger):
    return sum(float(e.get('charged_wall_s', e['reserved_wall_s'])) for e in ledger['executions']+ledger['auxiliary'])


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
    if not auxiliary and len(ledger['executions']) >= (32 if correction else 28):
        raise RuntimeError('EXECUTION_CEILING_OR_FOUR_SLOT_RESERVE')
    remaining = 1800.-used(ledger)
    if remaining <= .1:
        raise RuntimeError('AGGREGATE_NUMERICAL_TIME_EXHAUSTED')
    return min(120., remaining)


def identities():
    paths = ['puckworks/models/pannusch2024/'+f for f in (
        'stateful_fv.py', 'flow_temperature_history_fv.py', 'flow_history.py',
        'temperature_history_fv.py', 'temperature_history.py', 'solver.py', 'closures.py')]
    paths += ['puckworks/data/pannusch2024/'+f for f in ('table2_fitted_params.csv', 'table2_grind_psi_ds2.csv')]
    paths += ['tools/pannusch_flow_temp_fv_reference.py', 'tools/pannusch_temperature_history_verification.py',
              str((BUNDLE/'CONTRACT.md').relative_to(ROOT)), str((BUNDLE/'CASES.json').relative_to(ROOT))]
    out = {p: digest(ROOT/p) for p in paths}
    out['worker_and_reservation_blocks'] = hashlib.sha256('\n'.join(inspect.getsource(f) for f in (
        authority_path, used, locked_authority, reserve, execute, case_plan, candidate_state,
        baseline_module, parent_case, fields_array, run_case, worker, load_case)).encode()).hexdigest()
    out['pinned_base'] = BASE
    return out


def execute(directory, case_id=None, *, correction=False):
    directory = Path(directory).resolve()
    with locked_authority(directory) as (path, ledger):
        cases = read_json(BUNDLE/'CASES.json')['cases']
        if correction and case_id is None:
            raise ValueError('CORRECTION_REQUIRES_NAMED_AFFECTED_CASE')
        if case_id is not None and case_id not in {c['id'] for c in cases}:
            raise ValueError('UNKNOWN_CASE')
        for case in cases:
            if case_id is not None and case['id'] != case_id:
                continue
            if not correction and any(e['case_id'] == case['id'] for e in ledger['executions']):
                continue
            limit = reserve(ledger, correction=correction)
            eid = f"exec-{len(ledger['executions'])+1:03d}"
            row = dict(execution_id=eid, case_id=case['id'], status='LAUNCHED',
                       reserved_wall_s=limit, identities=identities(), correction=correction)
            ledger['executions'].append(row)
            write_json(path, ledger); write_json(directory/'executions.json', ledger['executions'])
            started = time.monotonic()
            try:
                with (directory/(eid+'.log')).open('w') as log:
                    r = subprocess.run([sys.executable, '-m', 'tools.pannusch_stateful_fv_verification', 'worker',
                        '--evidence-dir', str(directory), '--case-id', case['id'], '--execution-id', eid],
                        cwd=ROOT, env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT, timeout=limit)
                row.update(status='COMPLETE' if r.returncode == 0 else 'FAILED', returncode=r.returncode)
            except subprocess.TimeoutExpired:
                row['status'] = 'TIMEOUT'
            except BaseException:
                row['status'] = 'CANCELLED'
                raise
            finally:
                row['charged_wall_s'] = time.monotonic()-started
                if (directory/(eid+'.json')).exists():
                    row['receipt_sha256'] = digest(directory/(eid+'.json'))
                write_json(path, ledger); write_json(directory/'executions.json', ledger['executions'])
                print(eid, case['id'], row['status'], round(row['charged_wall_s'], 3),
                      's; aggregate', round(used(ledger), 3), flush=True)


def case_plan(case, contract):
    h = contract['histories'][case['history']]
    t, q = h['temperature_C'], h['flow']
    T = (sf.TemperatureHistory.constant_celsius if t['kind'] == 'constant' else sf.TemperatureHistory.linear_celsius)(t['times_s'], t['values'])
    Q = sf.FlowHistory(q['times_s'], q['values'], q['kind'])
    s = sf.FVSettings(**{**contract['settings'], 'cells': case['cells'], 'h_max_s': case['h_max_s']})
    return sf.FVPlan(T, Q, tuple(contract['t_span_s']), s)


def candidate_state(case, plan, contract):
    if case['method'] == 'EQUILIBRIUM':
        return sf.FVChemicalState.source_equilibrium(plan.temperature_history,
            time_s=plan.t_span_s[0], solute=case['solute'], grind=contract['grind'], cells=case['cells'])
    n = case['cells']; x = np.linspace(0., 1., n+1)
    # Exact integrals of the polynomials divided by cell widths. Independent
    # reference construction uses sums/products of the cell edges instead.
    width = np.diff(x)
    liquid = np.diff(.15*x+.125*x*x)/width
    fine = np.diff(.85*x-.275*x*x)/width
    coarse = np.diff(.10*x+.15*x*x*x)/width
    C0 = sf.fv.ps._solute_params()[case['solute']]['c_s0']
    return sf.FVChemicalState.from_cell_averages(solute=case['solute'], grind=contract['grind'],
        time_s=plan.t_span_s[0], edges_m=np.linspace(0, sf.fv.ps.L, n+1),
        liquid_kg_m3=C0*liquid, fine_kg_m3=C0*fine, coarse_kg_m3=C0*coarse)


def baseline_module(directory):
    target = directory/'pinned-003-runtime'; target.mkdir(exist_ok=True)
    for name in ('flow_temperature_history_fv.py', 'flow_history.py'):
        raw = subprocess.check_output(['git', 'show', BASE+':puckworks/models/pannusch2024/'+name], cwd=ROOT)
        p = target/name
        if p.exists() and p.read_bytes() != raw:
            raise RuntimeError('PINNED_BASE_SOURCE_CHANGED')
        p.write_bytes(raw)
    name = 'puckworks.models.pannusch2024._004_pinned_003'
    spec = importlib.util.spec_from_file_location(name, target/'flow_temperature_history_fv.py')
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod; spec.loader.exec_module(mod)
    return mod


def parent_case(directory, case_id):
    c = next(c for c in read_json(BUNDLE/'CASES.json')['cases'] if c['id'] == case_id)
    return load_case(directory, c)


def fields_array(tr):
    return np.column_stack((tr.liquid_cell_average_kg_m3, tr.fine_cell_average_kg_m3,
                            tr.coarse_cell_average_kg_m3))


def run_case(directory, case, contract, limit):
    p = case_plan(case, contract); method = case['method']; n = case['cells']
    obs = np.asarray(contract['observations_s']); windows = np.asarray(contract['fraction_windows_s'])
    start, stop = p.t_span_s
    cp = None
    if method in ('RESUME', 'BRANCH'):
        parent, _ = parent_case(directory, case['parent'])
        cp_path = directory/(parent['execution_id']+'.checkpoint.json')
        if digest(cp_path) != parent['checkpoint_sha256']:
            raise ValueError('PARENT_CHECKPOINT_HASH_MISMATCH')
        cp = sf.FVCheckpoint.from_json(cp_path.read_text())
        start = cp.time_s
        if method == 'RESUME':
            if p.identity_sha256 != cp.plan.identity_sha256:
                raise ValueError('RESUME_PLAN_MISMATCH')
            p = cp.plan
        else:
            p = sf.FVPlan(sf.TemperatureHistory.constant_celsius((start, stop), (case['future_T_C'],)),
                sf.FlowHistory((start, stop), (case['future_Q_m3_s'],), 'constant'), (start, stop), p.settings)
    if method == 'PREFIX':
        stop = float(p.primary_times_s[case['checkpoint_index']])
    if method == 'BRANCH_REFERENCE':
        start = contract['checkpoint']['S']['time_s']
        p = sf.FVPlan(sf.TemperatureHistory.constant_celsius((start, stop), (case['future_T_C'],)),
            sf.FlowHistory((start, stop), (case['future_Q_m3_s'],), 'constant'), (start, stop), p.settings)
    obs = obs[(obs >= start) & (obs <= stop)]
    windows = windows[(windows[:, 0] >= start) & (windows[:, 1] <= stop)]
    meta = dict(case=case, requested_span_s=[start, stop], root_time_s=0.,
                temperature_history=ref.raw_history(p.temperature_history), flow_history=ref.raw_history(p.flow_history),
                windows=windows.tolist(), plan_sha256=p.identity_sha256, mode=method)
    arrays = {}; exported = None
    if method == 'BASE_003':
        old = baseline_module(directory)
        bounds = np.unique(windows)
        r = old.simulate_flow_temperature_history_fv(p.temperature_history, flow_history=p.flow_history,
            t_span_s=(start, stop), solute=case['solute'], grind=contract['grind'], observation_times_s=obs,
            fraction_bounds_s=bounds, settings=p.settings)
        tr = r.observations
        arrays.update(times=tr.times_s, fields=fields_array(tr), local_mass=tr.outlet_solute_kg,
                      origin_mass=tr.outlet_solute_kg, local_volume=tr.hydraulic_volume_m3, origin_volume=tr.hydraulic_volume_m3,
                      primary_times=r.trace.times_s, primary_fields=r.trace.masses_kg[:, :-1]/np.repeat(r.phase_capacities_m3, n),
                      primary_local_mass=r.trace.masses_kg[:, -1], primary_origin_mass=r.trace.masses_kg[:, -1],
                      frozen_T=r.trace.frozen_temperature_K, frozen_Q=r.trace.frozen_flow_m3_s)
        # All window endpoints are common observations; mass differences are the
        # historical 003 output operator retained as the baseline comparator.
        arrays['fractions'] = np.array([(tr.outlet_solute_kg[np.searchsorted(obs,b)]-tr.outlet_solute_kg[np.searchsorted(obs,a)])/ref.volume(p.flow_history,a,b) for a,b in windows])
        meta.update(status=r.status, integration_complete=r.integration_complete,
                    sampled_admissibility=r.numerical_admissibility, actual_span_s=list(r.actual_span_s),
                    pinned_engine_sha256=digest(Path(old.__file__)), legacy_M0_cont_kg=r.M0_cont_kg)
    elif method in ('ORDERED', 'Radau', 'BRANCH_REFERENCE'):
        initial = ref.stateful_u_fields(case['solute'], n)
        if method == 'BRANCH_REFERENCE':
            parent, a = parent_case(directory, case['parent'])
            i = np.flatnonzero(a['times'] == start)
            if len(i) != 1: raise ValueError('INDEPENDENT_PARENT_TIME_ABSENT')
            initial = a['fields'][i[0]].reshape(3,n)
            prior_m = float(a['origin_mass'][i[0]])
            prior_v = float(a['origin_volume'][i[0]])
        else:
            prior_m = prior_v = 0.
        endpoints = np.unique(np.concatenate([ref.primary_times(p.temperature_history,p.flow_history,(start,stop),h)
            for h in contract['reference_primary_h_s']]))
        queries = np.unique(np.r_[obs, endpoints])
        values, checked_t, checked_y, records = ref.reference(p.temperature_history, p.flow_history,
            case['solute'], contract['grind'], n, queries, t_span_s=(start,stop),
            method='Radau' if method == 'Radau' else 'ORDERED', initial_fields=initial, **contract['radau'])
        observed = values[np.searchsorted(queries, obs)]; primary = values[np.searchsorted(queries, endpoints)]
        v = np.array([ref.volume(p.flow_history,start,t) for t in obs])
        arrays.update(times=obs, fields=observed[:,:-1], local_mass=observed[:,-1], origin_mass=observed[:,-1]+prior_m,
                      local_volume=v, origin_volume=v+prior_v, primary_times=endpoints, primary_fields=primary[:,:-1],
                      primary_local_mass=primary[:,-1], primary_origin_mass=primary[:,-1]+prior_m,
                      diagnostic_times=checked_t, diagnostic_fields=checked_y[:,:-1], diagnostic_local_mass=checked_y[:,-1])
        arrays['fractions'] = np.array([(values[np.searchsorted(queries,b),-1]-values[np.searchsorted(queries,a),-1])/ref.volume(p.flow_history,a,b) for a,b in windows])
        meta.update(status='COMPLETE', integration_complete=True, actual_span_s=[start,stop], reference_records=records)
    else:
        kw = dict(plan=p, observation_times_s=obs, fraction_windows_s=windows,
                  stop_time_s=stop, resource_settings=sf.FVSettings(**{**sf.fv.th._json_value(p.settings), 'wall_time_limit_s':max(.01,limit-15)}))
        if cp is not None:
            r = (sf.branch_stateful_fv(cp, **kw) if method == 'BRANCH' else sf.simulate_stateful_fv(checkpoint=cp, **kw))
        else:
            r = sf.simulate_stateful_fv(initial_state=candidate_state(case,p,contract), **kw)
        tr, primary = r.observations, r.primary
        arrays.update(times=tr.times_s, fields=fields_array(tr), local_mass=tr.segment_outlet_solute_kg,
            origin_mass=tr.origin_outlet_solute_kg, local_volume=tr.segment_volume_m3, origin_volume=tr.origin_volume_m3,
            primary_times=primary.times_s, primary_fields=fields_array(primary),
            primary_local_mass=primary.segment_outlet_solute_kg, primary_origin_mass=primary.origin_outlet_solute_kg,
            primary_local_volume=primary.segment_volume_m3, primary_origin_volume=primary.origin_volume_m3,
            raw_primary=r.raw_primary_masses_kg, quadrature=r.raw_quadrature,
            diagnostic_times=r.raw_diagnostic_times_s, raw_diagnostic=r.raw_diagnostic_masses_kg,
            step_mass=r.step_outlet_solute_kg, step_volume=r.step_volume_m3,
            exportable=r.exportable_primary, frozen_T=p.primary_steps[r.start_index:r.start_index+len(r.step_outlet_solute_kg),2],
            frozen_Q=p.primary_steps[r.start_index:r.start_index+len(r.step_outlet_solute_kg),3],
            fractions=np.array([f.concentration_kg_m3 for f in r.fractions], dtype=float))
        meta.update(status=r.status, integration_complete=r.integration_complete, actual_span_s=[start,r.actual_end_s],
            mode=r.mode, parent_identity=r.parent_identity, request_report_identity=r.identity_sha256,
            model_identity=r.root_state.model_identity, diagnostics=sf._json(r.diagnostics),
            fraction_status=[f.status for f in r.fractions], fraction_reason=[f.reason for f in r.fractions],
            propagations=r.propagations, exponential_applications=r.exponential_applications,
            diagnostic_evaluations=r.diagnostic_evaluations,
            prior_mass_terms=list(r.prior_outlet_terms_kg), prior_volume_terms=list(r.prior_volume_terms_m3))
        if method == 'PREFIX' and r.integration_complete:
            exported = r.checkpoint(stop).to_json()
    complete = meta['integration_complete'] and meta['actual_span_s'] == [start, stop]
    complete &= np.array_equal(arrays['times'], obs) and all(np.isfinite(a).all() for a in arrays.values())
    meta['coverage_complete'] = bool(complete)
    return meta, arrays, exported


def worker(directory, case_id, execution_id):
    directory = Path(directory)
    row = next((e for e in read_json(directory/'executions.json') if e['execution_id']==execution_id), None)
    if row is None or row['status'] != 'LAUNCHED' or row['case_id'] != case_id:
        raise RuntimeError('UNRESERVED_WORKER')
    with (directory/(execution_id+'.claim')).open('x') as f: f.write(case_id+'\n')
    if row['identities'] != identities(): raise RuntimeError('SOURCE_CHANGED_AFTER_RESERVATION')
    limit = max(.01, row['reserved_wall_s']-1)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('NUMERICAL_WALL_CEILING')))
    signal.setitimer(signal.ITIMER_REAL, limit)
    c = read_json(BUNDLE/'CASES.json'); case = next(x for x in c['cases'] if x['id'] == case_id)
    started = time.monotonic(); arrays = {}
    meta = dict(task=TASK, execution_id=execution_id, case=case, identities=identities(),
                source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
                versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
                rights=RIGHTS, scope='RESEARCH_ONLY', PHYSICAL_VALIDATION='NOT_ESTABLISHED')
    try:
        info, arrays, checkpoint = run_case(directory, case, c, limit)
        meta.update(info)
        if checkpoint is not None:
            path = directory/(execution_id+'.checkpoint.json'); path.write_text(checkpoint)
            meta['checkpoint_sha256'] = digest(path)
        complete = meta['coverage_complete']
    except Exception as exc:
        import traceback
        traceback.print_exc()
        meta.update(status='FAILED', reason=type(exc).__name__+':'+str(exc), coverage_complete=False)
        complete = False
    np.savez_compressed(directory/(execution_id+'.npz'), **arrays)
    meta['arrays_sha256'] = digest(directory/(execution_id+'.npz'))
    meta['numerical_wall_s'] = time.monotonic()-started
    write_json(directory/(execution_id+'.json'), meta)
    signal.setitimer(signal.ITIMER_REAL, 0)
    return 0 if complete else 2


def matching_producer_identities(produced, current):
    """Only exact reviewed input-boundary reuse; never a general hash waiver."""
    if produced == current:
        return True
    path = BUNDLE/'EVIDENCE_REUSE.json'
    if not path.exists():
        return False
    proof = read_json(path)
    return (produced == proof.get('original_producer_identities')
            and current == proof.get('corrected_producer_identities'))


def load_case(directory, case):
    directory = Path(directory)
    matches = [e for e in read_json(directory/'executions.json') if e['case_id']==case['id']]
    if not matches: raise ValueError('UNRUN')
    row = matches[-1]
    if row['status'] != 'COMPLETE': raise ValueError('LATEST_ATTEMPT_'+row['status'])
    path = directory/(row['execution_id']+'.json')
    if digest(path) != row.get('receipt_sha256'): raise ValueError('RECEIPT_HASH_MISMATCH')
    m = read_json(path)
    if not matching_producer_identities(m['identities'], identities()) or not matching_producer_identities(row['identities'], identities()): raise ValueError('NUMERICAL_SOURCE_CHANGED')
    if m['case'] != case or not m['coverage_complete']: raise ValueError('CASE_OR_COVERAGE_MISMATCH')
    if digest(path.with_suffix('.npz')) != m['arrays_sha256']: raise ValueError('ARRAY_HASH_MISMATCH')
    with np.load(path.with_suffix('.npz'), allow_pickle=False) as z:
        arrays = {k:z[k] for k in z.files}
    if not all(np.isfinite(a).all() for a in arrays.values()): raise ValueError('NONFINITE_ARRAYS')
    return m, arrays


def capacities(n, grind):
    ps = ref.ps
    psi = ps.GRINDS[grind]['psi']
    return ps.ACS*(ps.L/n)*np.array([ps.ALPHA_L, psi*(1-ps.ALPHA_L), ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L)])


def inventory(fields, n, grind):
    return np.sum(np.asarray(fields).reshape(-1,3,n)*capacities(n,grind)[None,:,None], axis=(1,2))


def fixed_scales(meta, arrays, contract):
    c = meta['case']; n = c['cells']; sp = ref.ps._solute_params()[c['solute']]
    if c['method'] in ('BASE_003','EQUILIBRIUM'):
        K = float(ref.pc.vant_hoff_K(353.15,sp['K_ref'],sp['gamma']))
        initial = np.repeat([K*sp['c_s0'],sp['c_s0'],sp['c_s0']],n)
    else:
        initial = ref.stateful_u_fields(c['solute'],n).ravel()
    local = arrays['primary_fields'][0]
    return dict(Cstar=float(np.max(initial)), Mstar=float(inventory(initial,n,contract['grind'])[0]),
                local_Cstar=float(np.max(np.abs(local))), local_Mstar=float(inventory(local,n,contract['grind'])[0]),
                legacy_Cstar=sp['c_s0'])


def metric(errors, scale, allowance):
    scale = float(scale)
    e = np.asarray(errors, dtype=float)
    maximum = float(np.max(np.abs(e),initial=0.))
    normalized = maximum/scale if scale > 0 else (0. if maximum == 0 else None)
    return dict(maximum_absolute=maximum, fixed_scale=float(scale), maximum_scaled=normalized,
                signed_initial=float(e.ravel()[0]) if e.size else 0.,
                signed_final=float(e.ravel()[-1]) if e.size else 0.,
                signed_min=float(np.min(e)) if e.size else 0.,
                signed_max=float(np.max(e)) if e.size else 0., allowance=allowance,
                passed=normalized is not None and math.isfinite(normalized) and normalized <= allowance)


def local_mass_at(a, start, queries):
    if 'step_mass' not in a:
        i = np.searchsorted(a['times'],start)
        if i == len(a['times']) or a['times'][i] != start:
            raise ValueError('REFERENCE_LOCAL_ORIGIN_ABSENT')
        return a['local_mass'][np.searchsorted(a['times'],queries)]-a['local_mass'][i]
    ts = a['primary_times']; first = int(np.searchsorted(ts,start))
    if ts[first] != start: raise ValueError('LOCAL_ORIGIN_NOT_PRIMARY')
    out=[]
    for t in queries:
        j = int(np.searchsorted(ts,t))
        if j < len(ts) and ts[j] == t:
            terms = a['step_mass'][first:j]
        else:
            k = int(np.searchsorted(a['diagnostic_times'],t))
            if a['diagnostic_times'][k] != t: raise ValueError('LOCAL_OBSERVATION_ABSENT')
            terms = (*a['step_mass'][first:j-1],float(a['raw_diagnostic'][k,-1]))
        out.append(math.fsum(terms))
    return np.asarray(out)


def accounting(meta, a, contract):
    n, grind = meta['case']['cells'], contract['grind']
    scales = fixed_scales(meta,a,contract)
    M, C = scales['Mstar'], scales['Cstar']
    L, CL = scales['local_Mstar'], scales['local_Cstar']
    bed = inventory(a['primary_fields'],n,grind)
    result = dict(scales=scales, initial_inventory_kg=float(bed[0]))
    result['local_inventory'] = metric(bed+a['primary_local_mass']-L,L,1e-8)
    result['origin_inventory'] = metric(bed+a['primary_origin_mass']-M,M,1e-8)
    fresh = meta['requested_span_s'][0] == 0
    result['initial_inventory'] = metric([bed[0]-M],M,1e-8) if fresh else dict(passed=True, reason='CHECKPOINT_LOCAL_INVENTORY_INDEPENDENTLY_RECOMPUTED_FROM_FIELDS')
    result['input_fields'] = metric(a['primary_fields'][0]-ref.stateful_u_fields(meta['case']['solute'],n).ravel(),C,1e-12) if fresh and meta['case']['method'] not in ('BASE_003','EQUILIBRIUM') else dict(passed=True, reason='EQUILIBRIUM_OR_CHECKPOINT_COMPARED_SEPARATELY')
    start, end = meta['requested_span_s']
    expected_v = np.array([ref.volume(meta['flow_history'],start,t) for t in a['times']])
    Vlocal = ref.volume(meta['flow_history'],start,end)
    # Branch prior flow belongs to S; resumed histories retain their original support.
    original = case_plan({**meta['case'], 'method':'U'},contract)
    expected_prior = ref.volume(original.flow_history,0.,start)
    Vroot = expected_prior+Vlocal
    result['local_volume'] = metric(a['local_volume']-expected_v,Vlocal,1e-12)
    result['origin_volume'] = metric(a['origin_volume']-expected_prior-expected_v,Vroot,1e-12)
    phase_minima = np.minimum(np.min(a['primary_fields'].reshape(-1,3,n),axis=(0,2)),
                              np.min(a['fields'].reshape(-1,3,n),axis=(0,2)))
    if 'raw_diagnostic' in a:
        dc = a['raw_diagnostic'][:,:-1]/np.repeat(capacities(n,grind),n)
        dm = local_mass_at(a,start,a['diagnostic_times'])
        d_bed = inventory(dc,n,grind)
        result['diagnostic_local_inventory'] = metric(d_bed+dm-L,L,1e-8)
        result['diagnostic_origin_inventory'] = metric(d_bed+dm+math.fsum(meta['prior_mass_terms'])-M,M,1e-8)
        phase_minima = np.minimum(phase_minima,np.min(dc.reshape(-1,3,n),axis=(0,2)))
    elif 'diagnostic_fields' in a:
        dc = a['diagnostic_fields']; dm = a['diagnostic_local_mass']
        d_bed = inventory(dc,n,grind)
        result['diagnostic_local_inventory'] = metric(d_bed+dm-L,L,1e-8)
        result['diagnostic_origin_inventory'] = metric(d_bed+dm+a['origin_mass'][0]-M,M,1e-8)
        phase_minima = np.minimum(phase_minima,np.min(dc.reshape(-1,3,n),axis=(0,2)))
    if 'quadrature' in a:
        q = a['quadrature']; steps = len(a['step_mass'])
        qmass = np.array([math.fsum((*a['step_mass'][:int(row[3])],float(row[8]))) for row in q])
        result['quadrature_local_inventory'] = metric(q[:,9]+qmass-L,L,1e-8)
        result['quadrature_origin_inventory'] = metric(q[:,9]+qmass+math.fsum(meta['prior_mass_terms'])-M,M,1e-8)
        phase_minima = np.minimum(phase_minima,np.min(q[:,10:13],axis=0))
        full = q[:,5].astype(bool)
        panel = {}
        for order in (4,8):
            for flux, col in [('numerical',6),('prescribed',7)]:
                full_parts = [float(np.sum(q[(q[:,3]==i)&full&(q[:,2]==order),1]*q[(q[:,3]==i)&full&(q[:,2]==order),col])) for i in range(steps)]
                out=[]; ends=[]
                for owner, end_t in sorted(set((int(row[3]),float(row[4])) for row in q)):
                    select=(q[:,3]==owner)&(q[:,4]==end_t)&(q[:,2]==order)
                    out.append(math.fsum((*full_parts[:owner],float(np.sum(q[select,1]*q[select,col])))))
                    ends.append(end_t)
                panel[(order,flux)]=np.asarray(out)
                if order == 8:
                    expected = local_mass_at(a,start,np.asarray(ends))
                    allowance = 5e-4 if flux == 'prescribed' and meta['case']['history']=='L' else 1e-6
                    result[flux+'_flux'] = metric(panel[(order,flux)]-expected,L,allowance)
            # Panel support itself is a gate, not inferred from a finite integral.
            result['quadrature_coverage'] = dict(passed=bool(np.count_nonzero(full&(q[:,2]==order)) == order*steps))
        for flux in ('numerical','prescribed'):
            result[flux+'_GL8_GL4'] = metric(panel[(8,flux)]-panel[(4,flux)],L,1e-6)
        chronological = sorted([*(zip(a['diagnostic_times'],local_mass_at(a,start,a['diagnostic_times']))),*(zip(q[:,0],qmass))])
        increments = np.diff([v for _,v in chronological])
        result['outlet_monotonicity'] = metric(np.minimum(increments,0.),L,1e-10)
        result['checkpoint_export_support'] = dict(passed=bool(np.all(a['exportable'])))
    else:
        result['outlet_monotonicity'] = metric(np.minimum(np.diff(a['primary_local_mass']),0.),L,1e-10)
    result['positivity_root'] = metric(np.minimum(phase_minima,0.),C,1e-10)
    result['positivity_local'] = metric(np.minimum(phase_minima,0.),CL,1e-10)
    result['phase_minima_kg_m3'] = phase_minima.tolist()
    result['passed'] = all(v.get('passed',True) for v in result.values() if isinstance(v,dict))
    return result


def compare(ma,a,mb,b,contract,allowance,*,restart=False):
    scales = fixed_scales(ma,a,contract)
    C = scales['legacy_Cstar'] if ma['case']['method'] in ('BASE_003','EQUILIBRIUM') else scales['Cstar']
    M = scales['Mstar']; result={}; maxima=[]
    common, ia, ib = np.intersect1d(a['times'],b['times'],return_indices=True)
    primary, pa, pb = np.intersect1d(a['primary_times'],b['primary_times'],return_indices=True)
    if len(common)==0 or len(primary)==0:
        return dict(passed=False,reason='NO_COMMON_SUPPORT')
    n=ma['case']['cells']
    for phase,i in [('liquid',0),('fine',1),('coarse',2)]:
        err=np.r_[(a['fields'][ia,i*n:(i+1)*n]-b['fields'][ib,i*n:(i+1)*n]).ravel(),
                  (a['primary_fields'][pa,i*n:(i+1)*n]-b['primary_fields'][pb,i*n:(i+1)*n]).ravel()]
        result[phase]=metric(err,C,allowance);maxima.append(result[phase]['maximum_scaled'])
        if restart: result[phase+'_local_scale']=metric(err,scales['local_Cstar'],allowance)
    err=np.r_[a['fields'][ia,n-1]-b['fields'][ib,n-1],a['primary_fields'][pa,n-1]-b['primary_fields'][pb,n-1]]
    result['outlet']=metric(err,C,allowance);maxima.append(result['outlet']['maximum_scaled'])
    if restart: result['outlet_local_scale']=metric(err,scales['local_Cstar'],allowance)
    err=np.r_[a['origin_mass'][ia]-b['origin_mass'][ib],a['primary_origin_mass'][pa]-b['primary_origin_mass'][pb]]
    result['origin_mass']=metric(err,M,allowance);maxima.append(result['origin_mass']['maximum_scaled'])
    start=max(ma['requested_span_s'][0],mb['requested_span_s'][0])
    if ma['requested_span_s'][0] == mb['requested_span_s'][0]:
        result['segment_mass']=metric(np.r_[a['local_mass'][ia]-b['local_mass'][ib],a['primary_local_mass'][pa]-b['primary_local_mass'][pb]],scales['local_Mstar'],allowance)
    if restart:
        queries=np.unique(np.r_[common,primary])
        err=local_mass_at(a,start,queries)-local_mass_at(b,start,queries)
        result['local_mass']=metric(err,scales['local_Mstar'],allowance)
        result['origin_mass_local_scale']=metric(np.r_[a['origin_mass'][ia]-b['origin_mass'][ib],a['primary_origin_mass'][pa]-b['primary_origin_mass'][pb]],scales['local_Mstar'],allowance)
        # The resumed primary plan must be the exact subset of the uninterrupted plan.
        j=np.searchsorted(b['primary_times'],a['primary_times'][0])
        result['exact_schedule']=dict(passed=bool(np.array_equal(a['primary_times'],b['primary_times'][j:j+len(a['primary_times'])])
            and np.array_equal(a['frozen_T'],b['frozen_T'][j:j+len(a['frozen_T'])])
            and np.array_equal(a['frozen_Q'],b['frozen_Q'][j:j+len(a['frozen_Q'])])))
        result['raw_state_bitwise_equal']=bool(np.array_equal(a['raw_primary'],b['raw_primary'][j:j+len(a['raw_primary'])]))
    V=ref.volume(ma['flow_history'],start,ma['requested_span_s'][1])
    result['volume']=metric(a['origin_volume'][ia]-b['origin_volume'][ib],V,1e-12)
    if restart:
        # Local prescribed volumes are independently reconstructed, no offset subtraction.
        va=np.array([ref.volume(ma['flow_history'],start,t) for t in common])
        vb=np.array([ref.volume(mb['flow_history'],start,t) for t in common])
        result['local_volume']=metric(va-vb,V,1e-12)
    wa=list(map(tuple,ma['windows']));wb=list(map(tuple,mb['windows']))
    both=[w for w in wa if w in wb]
    err=np.array([a['fractions'][wa.index(w)]-b['fractions'][wb.index(w)] for w in both])
    result['fractions']=metric(err,C,allowance);maxima.append(result['fractions']['maximum_scaled'])
    result['each_fraction_error_scaled']=(np.abs(err)/C).tolist();result['fraction_windows']=both
    if restart:result['fractions_local_scale']=metric(err,scales['local_Cstar'],allowance)
    result['aggregate_scaled_error']=max(maxima)
    result['common_observations']=len(common);result['common_primary_endpoints']=len(primary)
    result['passed']=all(v['passed'] for v in result.values() if isinstance(v,dict) and 'passed' in v)
    return result


def spatial(ma,a,mb,b,contract):
    n=ma['case']['cells']; s=fixed_scales(ma,a,contract)
    if mb['case']['cells']!=2*n or not np.array_equal(a['times'],b['times']):
        return dict(passed=False,reason='MESH_OR_OBSERVATION_MISMATCH')
    coarse=a['fields'].reshape(-1,3,n)
    fine=b['fields'].reshape(-1,3,n,2).mean(axis=-1)
    weighted=np.sum(abs(coarse-fine)*capacities(n,contract['grind'])[None,:,None],axis=(1,2))
    r=dict(weighted_field=metric(weighted,s['Mstar'],.005),
           outlet_mass=metric(a['origin_mass']-b['origin_mass'],s['Mstar'],.005),
           fractions=metric(a['fractions']-b['fractions'],s['Cstar'],.005))
    r['passed']=all(x['passed'] for x in r.values())
    return r


def recombination(prefix, suffix, full, tc):
    mp,a=prefix;ms,b=suffix;mf,c=full
    def amount(m,z,w):
        i=list(map(tuple,m['windows'])).index(w)
        volume=ref.volume(m['flow_history'],*w)
        return z['fractions'][i]*volume,volume
    m1,v1=amount(mp,a,(1.,tc));m2,v2=amount(ms,b,(tc,5.));m,v=amount(mf,c,(1.,5.))
    r=dict(mass=metric([math.fsum((m1,m2))-m],m,1e-12),volume=metric([math.fsum((v1,v2))-v],v,1e-12),
           concentration=metric([(m1+m2)/(v1+v2)-m/v],m/v,1e-12))
    r['passed']=all(x['passed'] for x in r.values());return r


def reduce_report(directory, output):
    directory,output=Path(directory),Path(output);c=read_json(BUNDLE/'CASES.json'); data={}; failures={}
    for case in c['cases']:
        try:data[case['id']]=load_case(directory,case)
        except (ValueError,OSError,KeyError) as exc:failures[case['id']]=str(exc)
    accounts={k:accounting(m,a,c) for k,(m,a) in data.items()}
    checks={};comparisons={}
    def pair(name,left,right,tolerance,**kw):
        if left not in data or right not in data:
            checks[name]=False;comparisons[name]=dict(passed=False,reason='MISSING_REQUIRED_EXECUTION');return
        result=compare(*data[left],*data[right],c,tolerance,**kw)
        comparisons[name]=result;checks[name]=result['passed']
    for sp in sf.fv.th.SPECIES:
        pair('equilibrium.'+sp,'A.'+sp+'.BASE_003','A.'+sp+'.EQUILIBRIUM',1e-12)
        pair('supplied_reference.'+sp,'B.'+sp+'.U','B.'+sp+'.ORDERED',1e-8)
    pair('S.prefix','C.caffeine.PREFIX','B.caffeine.U',1e-12,restart=True)
    pair('S.resume','C.caffeine.RESUME','B.caffeine.U',1e-12,restart=True)
    pair('L.prefix','D.caffeine.PREFIX','D.default',1e-12,restart=True)
    pair('L.resume','D.caffeine.RESUME','D.default',1e-12,restart=True)
    pair('branch_reference','E.caffeine.BRANCH','E.caffeine.BRANCH_REFERENCE',1e-8)
    pair('default_finer','D.default','D.fine',5e-4)
    for level in ('coarse','default','fine'):
        pair('Radau.'+level,'D.'+level,'D.caffeine.Radau',5e-4)
    # Coarse error is reported for the decrease test; its size is not an extra gate.
    checks.pop('Radau.coarse')
    errors=[comparisons.get('Radau.'+x,{}).get('aggregate_scaled_error') for x in ('coarse','default','fine')]
    checks['resolved_temporal_decrease']=all(x is not None for x in errors) and all(a<=1e-10 or b<a for a,b in zip(errors,errors[1:]))
    if all(k in data for k in ('D.default','D.N800')):
        comparisons['mesh']=spatial(*data['D.default'],*data['D.N800'],c);checks['mesh']=comparisons['mesh']['passed']
    else:checks['mesh']=False
    for hist,ids in [('S',('C.caffeine.PREFIX','C.caffeine.RESUME','B.caffeine.U')),
                     ('L',('D.caffeine.PREFIX','D.caffeine.RESUME','D.default'))]:
        if all(k in data for k in ids):
            comparisons[hist+'.recombination']=recombination(*(data[k] for k in ids),c['checkpoint'][hist]['time_s'])
            checks[hist+'.recombination']=comparisons[hist+'.recombination']['passed']
        else:checks[hist+'.recombination']=False
    if 'D.default' in data and 'F.repeat' in data:
        a,b=data['D.default'][1],data['F.repeat'][1]
        comparisons['repeat']={k:bool(np.array_equal(v,b.get(k))) for k,v in a.items()}
        checks['deterministic_repeat']=all(comparisons['repeat'].values())
    else:checks['deterministic_repeat']=False
    checks['full_coverage']=len(data)==28 and not failures
    checks['all_independent_accounting']=bool(accounts) and all(v['passed'] for v in accounts.values())
    checks['all_input_states']=checks['full_coverage'] and all(v['input_fields']['passed'] for v in accounts.values())
    passed=all(checks.values())
    ledger=read_json(directory/'executions.json') if (directory/'executions.json').exists() else []
    record=dict(task=TASK,governance='G2',change='NUMERICAL_METHOD_CHANGE',scope='RESEARCH_ONLY',
                PHYSICAL_VALIDATION='NOT_ESTABLISHED',runtime_accuracy='NOT_ASSESSED',
                dispositions=dict(implementation='IMPLEMENTED',numerical_qualification='VERIFIED_ON_DECLARED_CASES' if passed else 'IMPLEMENTED_QUALIFICATION_INCOMPLETE',
                    input_state_verification='PASS' if checks['all_input_states'] else 'INCOMPLETE_OR_FAILED',
                    same_schedule_continuation='PASS' if all(checks[x] for x in ('S.prefix','S.resume','L.prefix','L.resume','S.recombination','L.recombination')) else 'INCOMPLETE_OR_FAILED',
                    branching='PASS' if checks['branch_reference'] else 'INCOMPLETE_OR_FAILED',
                    temporal='PASS' if all(checks[x] for x in ('default_finer','Radau.default','Radau.fine','resolved_temporal_decrease')) else 'INCOMPLETE_OR_FAILED',
                    mesh='PASS' if checks['mesh'] else 'INCOMPLETE_OR_FAILED',software_QA='SEPARATE_QA_RECEIPT',hosted_CI='PENDING',independent_review='PENDING_EXACT_HEAD'),
                gates=checks,comparisons=comparisons,accounting=accounts,failed_or_unavailable=failures,
                resources=dict(executions=len(ledger),charged_execution_wall_s=sum(e.get('charged_wall_s',e['reserved_wall_s']) for e in ledger),
                               auxiliary='TASK_WIDE_AUTHORITY_RECEIPT',limits=c['limits']),
                identities=identities(),
                identity_meaning='Current reporting source; original integration identities are retained_producers, never restamped.',
                reporter_sha256=digest(Path(__file__)),
                retained_producers={m['source_commit']:m['identities'] for m,_ in data.values()},
                evidence_reuse_sha256=digest(BUNDLE/'EVIDENCE_REUSE.json') if (BUNDLE/'EVIDENCE_REUSE.json').exists() else None,
                rights=RIGHTS)
    output.mkdir(parents=True,exist_ok=True);write_json(output/'RESULTS.json',record)
    lines=['# MODEL-PANNUSCH2024-STATEFUL-FV-004 results','', '**'+record['dispositions']['numerical_qualification']+'**. G2 / NUMERICAL_METHOD_CHANGE.',
           'RESEARCH_ONLY; PHYSICAL_VALIDATION=NOT_ESTABLISHED; runtime accuracy NOT_ASSESSED.','',
           'Software QA, hosted CI and independent exact-head review are separate dispositions.','',
           '| Frozen gate | Result |','|---|---|']
    lines += [f"| {k} | {'PASS' if v else 'FAIL / INCOMPLETE'} |" for k,v in checks.items()]
    lines += ['',f"Integrations: {len(ledger)}; charged execution wall time: {record['resources']['charged_execution_wall_s']:.6f} s.",
              'Hard ceilings: 32 integrations, 1800 aggregate numerical seconds, 120 seconds per invocation.',
              'Every launched attempt is retained; report-only work is separately charged.','',
              '| Comparison | Liquid / C* | Fine / C* | Coarse / C* | Outlet / C* | Origin mass / M* | Fractions / C* |',
              '|---|---:|---:|---:|---:|---:|---:|']
    for key,r in comparisons.items():
        if 'aggregate_scaled_error' in r:
            lines.append('| '+key+' | '+' | '.join(f"{r[k]['maximum_scaled']:.9g}" for k in ('liquid','fine','coarse','outlet','origin_mass','fractions'))+' |')
    lines += ['', 'N400/N800 is a bounded mesh-sensitivity comparison, not asymptotic convergence or physical validation.',
              'Step/reference and branch/reference comparisons independently assemble concentration balances and source capacities.',
              'S and L prefixes actually stopped before suffix calls. Same-schedule comparisons include raw states and exact saved forcing.',
              'Fraction checks include every frozen window and mass/volume recombination across the checkpoint.',
              'Absolute and signed initial/final/worst inventory residuals, flux checks, scales, per-fraction errors and failures are in RESULTS.json.',
              '', 'Failed or unavailable executions: '+(json.dumps(failures,sort_keys=True) if failures else 'none')+'.',
              '', RIGHTS+'.','']
    (output/'RESULTS.md').write_text('\n'.join(lines))
    return record


def report(directory,output):
    with locked_authority(directory) as (path,ledger):
        limit=reserve(ledger,auxiliary=True)
        row=dict(status='LAUNCHED',reserved_wall_s=limit,kind='REPORT_ONLY')
        ledger['auxiliary'].append(row);write_json(path,ledger)
        started=time.monotonic()
        try:
            signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('REPORT_WALL_LIMIT')))
            signal.setitimer(signal.ITIMER_REAL,limit)
            result=reduce_report(directory,output)
            row['status']='COMPLETE'
            print(result['dispositions']['numerical_qualification'])
        except BaseException:
            row['status']='FAILED';raise
        finally:
            signal.setitimer(signal.ITIMER_REAL,0)
            row['charged_wall_s']=time.monotonic()-started
            write_json(path,ledger)
            write_json(Path(output)/'RESOURCES.json',dict(task=TASK,executions=ledger['executions'],auxiliary=ledger['auxiliary'],
                charged_total_wall_s=used(ledger),limits=read_json(BUNDLE/'CASES.json')['limits']))


def main():
    p=argparse.ArgumentParser();p.add_argument('command',choices=['execute','worker','report'])
    p.add_argument('--evidence-dir',type=Path,required=True);p.add_argument('--output-dir',type=Path)
    p.add_argument('--case-id');p.add_argument('--execution-id');p.add_argument('--correction',action='store_true')
    a=p.parse_args()
    if a.command=='execute':execute(a.evidence_dir,a.case_id,correction=a.correction)
    elif a.command=='worker':return worker(a.evidence_dir,a.case_id,a.execution_id)
    else:report(a.evidence_dir,a.output_dir or BUNDLE)
    return 0


if __name__=='__main__':raise SystemExit(main())

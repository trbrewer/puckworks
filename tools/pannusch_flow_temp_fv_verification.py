"""003 bounded qualification. Execute once/resume; report only reduces saved evidence.

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
from puckworks.models.pannusch2024 import flow_temperature_history_fv as fv, solver as ps
from tools import pannusch_flow_temp_fv_reference as ref
from tools.pannusch_temperature_history_verification import read_json, write_json, digest, canonical_hash

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT/"docs/analysis/model_pannusch2024_flow_temp_fv_003"
TASK = "MODEL-PANNUSCH2024-FLOW-TEMP-FV-003"
PARENT = "1d780b7fb57df4693e22e564010c891602df119d"
RIGHTS = "Pannusch et al., DOI 10.17632/y2tz67f6ry.1; CC-BY-NC-3.0 source-derived outputs; first-party software licensing separate"


def observations(contract):
    o = contract['observations']
    grid = np.arange(round((o['grid_end_s']-o['grid_start_s'])/o['grid_step_s'])+1)*o['grid_step_s']+o['grid_start_s']
    probes = [t+d for t in o['interior_knots_s'] for d in o['knot_probes_s']]
    return np.unique(np.r_[grid, probes, contract['early_times_s'], contract['fraction_bounds_s'],
                           np.asarray(contract['derived_windows_s']).ravel()])


def identities():
    paths = ["puckworks/models/pannusch2024/flow_temperature_history_fv.py",
             "puckworks/models/pannusch2024/flow_history.py",
             "puckworks/models/pannusch2024/temperature_history_fv.py",
             "puckworks/models/pannusch2024/temperature_history.py",
             "puckworks/models/pannusch2024/solver.py", "puckworks/models/pannusch2024/closures.py",
             "puckworks/data/pannusch2024/table2_fitted_params.csv", "puckworks/data/pannusch2024/table2_grind_psi_ds2.csv",
             "tools/pannusch_flow_temp_fv_reference.py",
             "tools/pannusch_temperature_history_verification.py",
             "docs/analysis/model_pannusch2024_flow_temp_fv_003/CONTRACT.md",
             "docs/analysis/model_pannusch2024_flow_temp_fv_003/CASES.json"]
    result = {p: digest(ROOT/p) for p in paths}
    blocks = (observations, _fields, _PassiveSystem, case_inputs, worker, execute, reserve, charged, used, _save_candidate)
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
    if not auxiliary and count >= (36 if correction else 32):
        raise RuntimeError("EXECUTION_CEILING_OR_FOUR_SLOT_RESERVE")
    remaining = 1800.-used(ledger)
    if remaining <= 0.1:
        raise RuntimeError("AGGREGATE_NUMERICAL_TIME_EXHAUSTED")
    return min(120., remaining)


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
                    process = subprocess.run([sys.executable, "-m", "tools.pannusch_flow_temp_fv_verification", "worker",
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


def _fields(trajectory):
    return np.column_stack((trajectory.liquid_cell_average_kg_m3,
        trajectory.fine_cell_average_kg_m3,trajectory.coarse_cell_average_kg_m3,trajectory.outlet_solute_kg))


class _PassiveSystem(fv._System):
    """Private manufactured seam; no source parameter modification."""
    def __init__(self,n):
        super().__init__('caffeine',1.7,n)
        self.Cstar=1.

    def generator(self,T,Q):
        return fv._mass_generator(self.n,Q/(self.W*ps.ALPHA_L),0,0,0,0)

    def initial(self,T):
        edges=self.edges
        primitive=edges/2-ps.L*np.sin(2*np.pi*edges/ps.L)/(4*np.pi)
        avg=np.diff(primitive)/(ps.L/self.n)
        return np.r_[self.capacities[:self.n]*avg,np.zeros(2*self.n+1)]

    def M0(self,T):
        return ps.ACS*ps.ALPHA_L*ps.L/2


def case_inputs(case,contract):
    passive=case['method']=='PASSIVE'
    t,q=(contract['histories'][case[k]] for k in ('temperature','flow'))
    history=fv.TemperatureHistory(t['times_s'],t['values'],t['kind'])
    flow=fv.FlowHistory(q['times_s'],q['values'],q['kind'])
    if passive:
        times=np.array([ref.time_for_volume(q,x*ps.ACS*ps.ALPHA_L*ps.L)
                        for x in contract['passive']['displacements_over_L']])
        span=[0.,float(times[-1])]; bounds=np.array([])
    else:
        span=contract['t_span_s']; times=observations(contract); bounds=np.array(contract['fraction_bounds_s'])
    return passive,span,history,flow,times,bounds


def _save_candidate(arrays,tr,checked,trace,quad,fractions,Q=None):
    old=Q is not None
    count=len(trace.times_s)-1
    arrays.update(times=tr.times_s,states=_fields(tr),volume=tr.hydraulic_volume_m3,
        diagnostic_times=checked.times_s,diagnostic_states=_fields(checked),
        trace_times=trace.times_s,trace_masses=trace.masses_kg,
        frozen_temperature=trace.frozen_temperature_K,
        frozen_flow=np.full(count,Q) if old else trace.frozen_flow_m3_s,
        fractions=fractions,quadrature_times=quad.times_s,quadrature_weights=quad.weights_s,
        quadrature_order=quad.order,quadrature_step=np.repeat(np.arange(count),12) if old else quad.primary_step_index,
        quadrature_end=np.repeat(trace.times_s[1:],12) if old else quad.panel_end_s,
        quadrature_full=np.ones(len(quad.times_s)) if old else quad.full_interval,
        numerical_flux=quad.outlet_flux_kg_s if old else quad.numerical_frozen_step_flux_kg_s,
        prescribed_flux=quad.outlet_flux_kg_s if old else quad.prescribed_flow_diagnostic_flux_kg_s,
        quadrature_Mout=quad.outlet_solute_kg,quadrature_inventory=quad.total_from_physical_fields_kg,
        quadrature_phase_minima=quad.phase_minima_kg_m3)


def worker(directory,case_id,execution_id):
    directory=Path(directory)
    entry=next((e for e in read_json(directory/'executions.json') if e['execution_id']==execution_id),None)
    if entry is None or entry['status']!='LAUNCHED' or entry['case_id']!=case_id:
        raise RuntimeError('UNRESERVED_WORKER')
    with (directory/(execution_id+'.claim')).open('x') as claim: claim.write(case_id+'\n')
    if entry['identities']!=identities(): raise RuntimeError('SOURCE_CHANGED_AFTER_RESERVATION')
    limit=max(.01,entry['reserved_wall_s']-1.)
    signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('NUMERICAL_WALL_CEILING')))
    signal.setitimer(signal.ITIMER_REAL,limit)
    contract=read_json(BUNDLE/'CASES.json'); case=next(c for c in contract['cases'] if c['id']==case_id)
    passive,span,history,flow,times,bounds=case_inputs(case,contract)
    n,solute,grind=case['cells'],case['solute'],contract['grind']
    meta=dict(task=TASK,case=case,case_sha256=canonical_hash(case),execution_id=execution_id,
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        identities=identities(),runner_file_sha256=digest(__file__),requested_span_s=span,grind=grind,
        temperature_history=ref.raw_history(history),flow_history=ref.raw_history(flow),fraction_bounds_s=bounds.tolist(),
        versions=dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__),
        observation_sha256=hashlib.sha256(times.tobytes()).hexdigest(),rights=RIGHTS,PHYSICAL_VALIDATION='NOT_ESTABLISHED')
    start=time.monotonic(); arrays={}
    try:
        if case['method'] in ('FV','PASSIVE','OLD_FV'):
            settings=fv.FVSettings(cells=n,h_max_s=case['h_max_s'],diagnostic_step_s=contract['diagnostic_step_s'],
                wall_time_limit_s=max(.001,limit-10),**case.get('resource_overrides',{}))
            if passive:
                system=_PassiveSystem(n)
                result=fv._evolve(system,history,flow,span,tuple(times),(),settings)
                meta.update({k:v for k,v in result.items() if k not in ('observations','checked_trajectory','trace','quadrature','fractions')})
                tr,checked,trace,quad=[result[k] for k in ('observations','checked_trajectory','trace','quadrature')]
                meta.update(Cstar=1.,capacities=system.capacities.reshape(3,n)[:,0].tolist(),settings=fv.th._json_value(settings),test_only=True)
                fractions=np.array([])
            else:
                args=dict(t_span_s=span,solute=solute,grind=grind,observation_times_s=times,fraction_bounds_s=bounds,settings=settings)
                result=(fv.fixed.simulate_temperature_history_fv(history,flow_m3_s=2e-6,**args) if case['method']=='OLD_FV'
                        else fv.simulate_flow_temperature_history_fv(history,flow_history=flow,**args))
                # History metadata stays in a common raw schema for independent reduction.
                info=json.loads(result.to_json(include_trajectories=False))
                info.pop('temperature_history',None); info.pop('flow_history',None)
                meta.update(info)
                tr,checked,trace,quad=result.observations,result.checked_trajectory,result.trace,result.quadrature
                meta.update(Cstar=ps._solute_params()[solute]['c_s0'],capacities=result.phase_capacities_m3.tolist())
                raw=[f.raw_diagnostic_concentration_kg_m3 for f in result.fractions]
                fractions=np.array(raw,dtype=float) if all(v is not None for v in raw) else np.array([])
            _save_candidate(arrays,tr,checked,trace,quad,fractions,2e-6 if case['method']=='OLD_FV' else None)
            arrays['primary_states']=np.column_stack((trace.masses_kg[:,:-1]/np.repeat(meta['capacities'],n),trace.masses_kg[:,-1]))
            meta['segment_count']=len(meta['segments'])
            complete=bool(meta['integration_complete']) and list(meta['actual_span_s'])==span
        else:
            endpoints=np.unique(np.concatenate([ref.primary_times(history,flow,span,h) for h in contract['reference_endpoint_h_s']]))
            reference_times=np.unique(np.r_[times,endpoints])
            values,checked_t,checked_y,records=ref.reference(history,flow,solute,grind,n,reference_times,
                t_span_s=span,method=case['method'],**{k:v for k,v in contract['radau'].items()})
            _,M0=ref.initial_and_inventory(ref.value(history,span[0]),solute,grind,n)
            observed=values[np.searchsorted(reference_times,times)]
            frac=np.diff(values[np.searchsorted(reference_times,bounds),-1])/np.array([ref.volume(flow,a,b) for a,b in zip(bounds,bounds[1:])])
            arrays.update(times=times,states=observed,diagnostic_times=checked_t,diagnostic_states=checked_y,
                volume=np.array([ref.volume(flow,span[0],t) for t in times]),fractions=frac,
                trace_times=endpoints,primary_states=values[np.searchsorted(reference_times,endpoints)])
            meta.update(status='COMPLETE',integration_complete=True,actual_span_s=span,M0_cont_kg=M0,
                Cstar=ps._solute_params()[solute]['c_s0'],segments=records,segment_count=len(records),
                shared_machinery='Only unchanged source parameters/geometry/closures; independent history clocks, union, volume and concentration operator')
            complete=True
        if not all(np.isfinite(a).all() for a in arrays.values()):
            complete=False; meta['reason']='NONFINITE_SAVED_ARRAY'
        meta['status']='COMPLETE' if complete else 'PARTIAL_OR_FAILED'
    except Exception as exc:
        meta.update(status='FAILED',integration_complete=False,actual_span_s=None,reason='WORKER_EXCEPTION:'+type(exc).__name__)
        import traceback
        traceback.print_exc()
        complete=False
    meta['numerical_wall_s']=time.monotonic()-start
    np.savez_compressed(directory/(execution_id+'.npz'),**arrays)
    meta['arrays_sha256']=digest(directory/(execution_id+'.npz'))
    write_json(directory/(execution_id+'.json'),meta)
    signal.setitimer(signal.ITIMER_REAL,0.)
    return 0 if complete else 2

def load_case(directory,case,ledger):
    matches=[e for e in ledger if e['case_id']==case['id']]
    if not matches: raise ValueError('UNRUN')
    e=matches[-1]
    if e['status']!='COMPLETE': raise ValueError('LATEST_ATTEMPT_'+e['status'])
    path=Path(directory)/(e['execution_id']+'.json')
    if digest(path)!=e.get('receipt_sha256'): raise ValueError('RECEIPT_HASH_MISMATCH')
    meta=read_json(path)
    if meta['case']!=case or meta['case_sha256']!=canonical_hash(case) or meta['status']!='COMPLETE':
        raise ValueError('INCOMPLETE_OR_WRONG_CASE')
    if meta['identities']!=identities() or e['identities']!=identities(): raise ValueError('NUMERICAL_SOURCE_CHANGED')
    if digest(path.with_suffix('.npz'))!=meta['arrays_sha256']: raise ValueError('ARRAY_HASH_MISMATCH')
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as saved: a={k:saved[k] for k in saved.files}
    contract=read_json(BUNDLE/'CASES.json')
    passive,span,T,Q,times,bounds=case_inputs(case,contract); n=case['cells']
    if not meta['integration_complete'] or meta['actual_span_s']!=span: raise ValueError('PARTIAL_SUPPORT')
    if not all(np.isfinite(v).all() for v in a.values()): raise ValueError('NONFINITE_ARRAY')
    if not np.array_equal(a['times'],times) or a['states'].shape!=(len(times),3*n+1): raise ValueError('WRONG_OBSERVATION_SUPPORT')
    if a['fractions'].shape!=(max(0,len(bounds)-1),) or a['volume'].shape!=times.shape: raise ValueError('INCOMPLETE_OBSERVERS')
    dt,dy=a['diagnostic_times'],a['diagnostic_states']
    if dy.shape!=(len(dt),3*n+1) or dt[0]!=span[0] or dt[-1]!=span[-1] or np.any(np.diff(dt)<=0):
        raise ValueError('INVALID_DIAGNOSTIC_SUPPORT')
    if case['method'] in ('FV','PASSIVE','OLD_FV'):
        expected=ref.primary_times(T,Q,span,case['h_max_s'])
        if not np.array_equal(a['trace_times'],expected): raise ValueError('WRONG_PRIMARY_UNION_PARTITION')
        steps=len(expected)-1
        full=a['quadrature_full'].astype(bool)
        if np.count_nonzero(full)!=12*steps or len(full)%12: raise ValueError('INCOMPLETE_QUADRATURE')
        order=a['quadrature_order'].reshape(-1,12)
        if not np.all(order==np.r_[np.full(4,4),np.full(8,8)]): raise ValueError('WRONG_QUADRATURE_ORDERS')
        if a['trace_masses'].shape!=(steps+1,3*n+1): raise ValueError('INCOMPLETE_PRIMARY_STATES')
        records=[dict(s) for s in meta['segments']]
        if len(records)!=len(ref.segments(T,Q,span)) or any(s['status']!='COMPLETE' for s in records):
            raise ValueError('INCOMPLETE_SEGMENTS')
        if any(l['end_state_sha256']!=r['start_state_sha256'] for l,r in zip(records,records[1:])):
            raise ValueError('STATE_RESET_AT_KNOT')
    if passive:
        initial,_,_=ref.passive_exact(n,[0],Q); expected=np.r_[initial[0],np.zeros(2*n+1)]
    else: expected,_=ref.initial_and_inventory(ref.value(T,span[0]),case['solute'],contract['grind'],n)
    if not np.allclose(a['states'][0],expected,rtol=3e-15,atol=1e-15): raise ValueError('INITIAL_STATE_CHANGED')
    return meta,a


def metric(values,scale,allowance):
    z=np.asarray(values)/scale
    return dict(max_abs_normalized=float(np.max(np.abs(z),initial=0)),
        signed_min_normalized=float(np.min(z,initial=0)),signed_max_normalized=float(np.max(z,initial=0)),
        signed_final_normalized=float(z.ravel()[-1]) if z.size else 0.,allowance=allowance,
        passed=bool(np.max(abs(z),initial=0)<=allowance))


def _indices(times,query):
    """Match rounding-equivalent clocks, never interpolate a concentration."""
    i=np.searchsorted(times,query); i=np.minimum(i,len(times)-1)
    previous=np.maximum(0,i-1)
    i=np.where(abs(times[previous]-query)<abs(times[i]-query),previous,i)
    if np.max(abs(times[i]-query),initial=0)>1e-12: raise ValueError('MISSING_COMPARISON_ENDPOINT')
    return i


def flux_diagnostics(a,M):
    w=a['quadrature_weights'].reshape(-1,12)
    step=a['quadrature_step'].reshape(-1,12)[:,0].astype(int)
    ends=a['quadrature_end'].reshape(-1,12)[:,0]
    full=a['quadrature_full'].reshape(-1,12)[:,0].astype(bool)
    observed=a['diagnostic_states'][_indices(a['diagnostic_times'],ends),-1]
    result={}
    for key,flux in (('numerical_frozen_step','numerical_flux'),('prescribed_flow_diagnostic','prescribed_flux')):
        f=a[flux].reshape(-1,12)
        panels4=np.sum(w[:,:4]*f[:,:4],axis=1); panels8=np.sum(w[:,4:]*f[:,4:],axis=1)
        prefix4=np.r_[0,np.cumsum(panels4[full])]; prefix8=np.r_[0,np.cumsum(panels8[full])]
        total4=prefix4[step]+panels4; total8=prefix8[step]+panels8
        result[key]=dict(GL8_minus_Mout=metric(total8-observed,M,1e-6 if key=='numerical_frozen_step' else 5e-4),
                        GL8_minus_GL4=metric(total8-total4,M,1e-6))
    result.update(full_panels=int(full.sum()),partial_panels=int((~full).sum()))
    return result


def accounting(meta,a):
    n,C,M=meta['case']['cells'],meta['Cstar'],meta['M0_cont_kg']
    flow=meta['flow_history']; t0,tf=meta['actual_span_s']
    V=ref.volume(flow,t0,tf)
    psi=ps.GRINDS[meta['grind']]['psi']
    weights=ps.ACS*ps.L/n*np.array([ps.ALPHA_L,psi*(1-ps.ALPHA_L),ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L)])
    fields=a['diagnostic_states'][:,:-1].reshape(-1,3,n)
    remaining=np.sum(fields*weights[None,:,None],axis=(1,2)); mout=a['diagnostic_states'][:,-1]
    residual=remaining+mout-M; minima=np.min(fields,axis=(0,2))/C
    result=dict(M0_cont_kg=M,M0_independent_cell_sum_kg=float(remaining[0]+mout[0]),
        initial_offset_kg=float(remaining[0]+mout[0]-M),inventory=metric(residual,M,1e-8),
        checked_samples=len(fields),actual_span_s=[t0,tf],
        prescribed_volume=metric(a['volume']-np.array([ref.volume(flow,t0,t) for t in a['times']]),V,1e-12))
    if meta.get('fractions'):
        result['fraction_volumes'] = metric([
            f['volume_m3']-ref.volume(flow,f['start_s'],f['end_s'])
            for f in meta['fractions']], V, 1e-12)
    if 'quadrature_times' in a:
        minima=np.minimum(minima,np.min(a['quadrature_phase_minima'],axis=0)/C)
        times=np.r_[a['diagnostic_times'],a['quadrature_times']]
        all_m=np.r_[mout,a['quadrature_Mout']]
        inc=float(np.min(np.diff(all_m[np.argsort(times,kind='stable')]),initial=0)/M)
        result.update(fluxes=flux_diagnostics(a,M),quadrature_inventory=metric(a['quadrature_inventory']-M,M,1e-8),
            quadrature_evaluations=len(a['quadrature_times']),minimum_Mout_increment_over_Mstar=inc,
            minimum_Mout_over_Mstar=float(all_m.min()/M))
        result['positivity_passed']=bool(minima.min()>=-1e-10 and inc>=-1e-10 and all_m.min()/M>=-1e-10)
        flux=result['fluxes']
        result['numerical_flux_passed']=all(v['passed'] for v in flux['numerical_frozen_step'].values())
        result['prescribed_flux_passed']=all(v['passed'] for v in flux['prescribed_flow_diagnostic'].values())
    result['phase_minima_over_Cstar']=dict(zip(('liquid','fine','coarse'),map(float,minima)))
    result['conservation_passed']=result['inventory']['passed'] and result.get('quadrature_inventory',{'passed':True})['passed']
    return result


def agreement(a,b,meta,allowance):
    n,C,M=meta['case']['cells'],meta['Cstar'],meta['M0_cont_kg']
    V=ref.volume(meta['flow_history'],*meta['actual_span_s'])
    difference=a['states']-b['states']
    # Each primary endpoint is also compared against a reference or the finer trace.
    ai=_indices(b['trace_times'],a['trace_times'])
    endpoint=a['primary_states']-b['primary_states'][ai]
    out={name:metric(np.r_[difference[:,i*n:(i+1)*n].ravel(),endpoint[:,i*n:(i+1)*n].ravel()],C,allowance)
         for i,name in enumerate(('liquid','fine','coarse'))}
    out.update(outlet=metric(np.r_[difference[:,n-1],endpoint[:,n-1]],C,allowance),
        Mout=metric(np.r_[difference[:,-1],endpoint[:,-1]],M,allowance),
        volume=metric(a['volume']-b['volume'],V,allowance),fractions=metric(a['fractions']-b['fractions'],C,allowance),
        each_fraction_abs_over_Cstar=(abs(a['fractions']-b['fractions'])/C).tolist())
    out['aggregate_error']=max(out[k]['max_abs_normalized'] for k in ('liquid','fine','coarse','outlet','Mout','fractions'))
    out['passed']=all(v['passed'] for v in out.values() if isinstance(v,dict) and 'passed' in v)
    return out


def spatial(coarse,fine,meta):
    n,C,M=meta['case']['cells'],meta['Cstar'],meta['M0_cont_kg']
    c=coarse['states'][:,:-1].reshape(-1,3,n); f=fine['states'][:,:-1].reshape(-1,3,n,2).mean(axis=-1)
    psi=ps.GRINDS[meta['grind']]['psi']
    capacities=np.array([ps.ALPHA_L,psi*(1-ps.ALPHA_L),ps.PHI_V2*(1-psi)*(1-ps.ALPHA_L)])
    weighted=ps.ACS*ps.L/n*np.sum(abs(c-f)*capacities[None,:,None],axis=(1,2))
    out=dict(fractions=metric(coarse['fractions']-fine['fractions'],C,.005),
        Mout=metric(coarse['states'][:,-1]-fine['states'][:,-1],M,.005),weighted_field=metric(weighted,M,.005))
    out['passed']=all(v['passed'] for v in out.values())
    return out


def reduce_report(directory,output):
    """Saved-evidence reduction only. No candidate/reference/exponential calls."""
    contract=read_json(BUNDLE/'CASES.json'); ledger=read_json(Path(directory)/'executions.json')
    result=dict(task=TASK,base=PARENT,contract_sha256=digest(BUNDLE/'CONTRACT.md'),cases_sha256=digest(BUNDLE/'CASES.json'),
        reporter_sha256=digest(__file__),rights=RIGHTS,PHYSICAL_VALIDATION='NOT_ESTABLISHED',
        cases={},compatibility={},joint_steps={},temporal={},convergence={},spatial={},manufactured={},observers={},
        execution_receipts=ledger,resources=dict(executions=len(ledger),execution_wall_s=sum(charged(e) for e in ledger),
        remaining_slots=36-len(ledger),per_group={g:dict(executions=sum(e['case_id'].startswith(g+'.') for e in ledger),
        wall_s=sum(charged(e) for e in ledger if e['case_id'].startswith(g+'.'))) for g in 'ABCDEF'}))
    data={}; metadata={}
    for case in contract['cases']:
        key=case['id']
        try:
            meta,a=load_case(directory,case,ledger); data[key]=a; metadata[key]=meta
            result['cases'][key]=dict(case=case,status='COMPLETE',execution_id=meta['execution_id'],source_commit=meta['source_commit'],
                identities=meta['identities'],arrays_sha256=meta['arrays_sha256'],versions=meta['versions'],accounting=accounting(meta,a))
            if case['family']!='F':
                flow=meta['flow_history']; bounds=contract['fraction_bounds_s']
                volumes=np.array([ref.volume(flow,l,r) for l,r in zip(bounds,bounds[1:])])
                mass=a['states'][:,-1]
                def dm(l,r): return float(mass[_indices(a['times'],np.array([r]))[0]]-mass[_indices(a['times'],np.array([l]))[0]])
                whole=dm(0,30)/ref.volume(flow,0,30); recombined=np.dot(volumes,a['fractions'])/volumes.sum()
                windows={str(w):dm(*w)/ref.volume(flow,*w) for w in contract['derived_windows_s']}
                result['observers'][key]=dict(derived_window_kg_m3=windows,volume_weighted_recombination=metric(whole-recombined,meta['Cstar'],1e-12))
        except (ValueError,KeyError,OSError) as exc:
            data.pop(key,None); metadata.pop(key,None)
            result['cases'][key]=dict(case=case,status='UNAVAILABLE_OR_FAILED',reason=type(exc).__name__ if isinstance(exc,OSError) else str(exc))
    for solute in fv.th.SPECIES:
        for group,method,budget,target in [('A','OLD_FV',1e-12,'compatibility'),('B','ORDERED',1e-8,'joint_steps')]:
            a,b=f'{group}.{solute}.FV',f'{group}.{solute}.{method}'
            if a in data and b in data: result[target][solute]=agreement(data[a],data[b],metadata[a],budget)
    for direction in ('up','down'):
        default=f'C.{direction}.default'; reference=f'C.{direction}.Radau'
        for other in ('finer','Radau'):
            b=f'C.{direction}.{other}'
            if default in data and b in data: result['temporal'][direction+'.'+other]=agreement(data[default],data[b],metadata[default],5e-4)
        errors=[]; fluxes=[]
        for level in ('coarse','default','finer'):
            a=f'C.{direction}.{level}'
            if a in data and reference in data:
                comparison=agreement(data[a],data[reference],metadata[a],5e-4)
                errors.append(comparison['aggregate_error'])
                flux=result['cases'][a]['accounting']['fluxes']['prescribed_flow_diagnostic']['GL8_minus_Mout']['max_abs_normalized']
                fluxes.append(flux)
                result['convergence'][direction+'.'+level]=dict(h_max_s=metadata[a]['case']['h_max_s'],reference_errors=comparison,prescribed_flux_discrepancy=flux)
        def decreasing(values):
            return len(values)==3 and all(y<x or max(x,y)<=1e-10 for x,y in zip(values,values[1:]))
        result['convergence'][direction+'.trend']=dict(aggregate_errors=errors,prescribed_flux_discrepancies=fluxes,
            resolution_floor=1e-10,error_decreases=decreasing(errors),flux_decreases=decreasing(fluxes),
            passed=decreasing(errors) and decreasing(fluxes),order='NOT_CLAIMED')
    for history,nominal in [('up','C.up.default'),('trigonelline','B.trigonelline.FV')]:
        keys=[f'D.{history}.200',nominal,f'D.{history}.800']; vals=[]
        for a,b,label in zip(keys,keys[1:],('200_to_400','400_to_800')):
            if a in data and b in data:
                v=spatial(data[a],data[b],metadata[a]); result['spatial'][history+'.'+label]=v; vals.append(v)
        if len(vals)==2:
            result['spatial'][history+'.ratios']={k:(vals[0][k]['max_abs_normalized']/vals[1][k]['max_abs_normalized']
                if min(v[k]['max_abs_normalized'] for v in vals)>1e-10 else None) for k in ('fractions','Mout','weighted_field')}
    for n in (32,64,128):
        key=f'F.passive.{n}'
        if key in data:
            a=data[key]; exact,mout,M=ref.passive_exact(n,a['times'],metadata[key]['flow_history'])
            error=np.mean(abs(a['states'][:,:n]-exact),axis=1)
            remaining=ps.ACS*ps.ALPHA_L*ps.L/n*np.sum(a['states'][:,:n],axis=1)
            result['manufactured'][str(n)]=dict(times_s=a['times'].tolist(),L1_over_C0=error.tolist(),
                signed_outlet_error_over_M0=((a['states'][:,-1]-mout)/M).tolist(),
                postexit_remaining_plus_outlet_error=float((remaining[-1]+abs(a['states'][-1,-1]-M))/M))
    if all(str(n) in result['manufactured'] for n in (32,64,128)):
        orders=[np.log2(np.array(result['manufactured'][str(n)]['L1_over_C0'])[1:4]/np.array(result['manufactured'][str(n*2)]['L1_over_C0'])[1:4]).tolist() for n in (32,64)]
        finest=result['manufactured']['128']; result['manufactured']['orders']=orders
        result['manufactured']['passed']=bool(np.min(orders)>=.8 and max(finest['L1_over_C0'][1:4])<=.05 and finest['postexit_remaining_plus_outlet_error']<=.05)
    a,b='C.up.default','E.repeat.up'
    result['repeatability']=dict(passed=a in data and b in data and set(data[a])==set(data[b]) and all(np.array_equal(data[a][k],data[b][k]) for k in data[a]))
    candidates=[c['id'] for c in contract['cases'] if c['method'] in ('FV','PASSIVE')]
    candidate_complete=all(k in data for k in candidates)
    def candidate_gate(name): return candidate_complete and all(result['cases'][k]['accounting'][name] for k in candidates)
    positivity=candidate_gate('positivity_passed'); conservation=candidate_gate('conservation_passed')
    def group_pass(name,count): return len(result[name])==count and all(v['passed'] for v in result[name].values())
    temporal=group_pass('temporal',4) and all(result['convergence'].get(d+'.trend',{}).get('passed',False) for d in ('up','down'))
    spatial_ok=all(result['spatial'].get(d+'.400_to_800',{}).get('passed',False) for d in ('up','trigonelline')) and result['manufactured'].get('passed',False)
    observers=len(result['observers'])==29 and all(v['volume_weighted_recombination']['passed'] for v in result['observers'].values())
    volume=all(k in data and result['cases'][k]['accounting']['prescribed_volume']['passed'] and result['cases'][k]['accounting'].get('fraction_volumes',{'passed':True})['passed'] for k in (c['id'] for c in contract['cases']))
    gates=dict(full_coverage=len(data)==32,positivity=positivity,conservation=conservation,
        numerical_flux=candidate_gate('numerical_flux_passed'),prescribed_flux=candidate_gate('prescribed_flux_passed'),
        volume=volume,compatibility=group_pass('compatibility',4),joint_steps=group_pass('joint_steps',4),
        temporal_accuracy=temporal,spatial_accuracy=spatial_ok,observers=observers,repeatability=result['repeatability']['passed'])
    numeric=all(gates.values())
    result['gates']=gates
    result['dispositions']=dict(numerical_qualification='VERIFIED_ON_DECLARED_CASES' if numeric else
        'POSITIVITY_AND_CONSERVATION_VERIFIED_ACCURACY_INCOMPLETE' if positivity and conservation else 'NUMERICAL_QUALIFICATION_INCOMPLETE',
        software_QA='SEPARATE_RECEIPT',hosted_CI='SEPARATE_RECEIPT',independent_review='SEPARATE_EXACT_HEAD_RECEIPT')
    result['scope']='RESEARCH_ONLY; runtime accuracy NOT_ASSESSED; new 5e-4 joint-linear engineering budget does not amend 002 temperature-only 1e-6; 001/002 preserved'
    Path(output).mkdir(parents=True,exist_ok=True); write_json(Path(output)/'RESULTS.json',result)
    return result

def report(directory, output):
    """Charge saved-evidence numerical reduction without launching any trajectory."""
    with locked_authority(directory) as (authority, ledger):
        limit = reserve(ledger, auxiliary=True)
        e = dict(kind="REPORT_ONLY", status="LAUNCHED", reserved_wall_s=limit)
        ledger["auxiliary"].append(e); write_json(authority, ledger)
        started = time.monotonic()
        signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("REPORT_WALL_CEILING")))
        signal.setitimer(signal.ITIMER_REAL, limit)
        try:
            value = reduce_report(directory, output)
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
        print(json.dumps(report(args.evidence_dir, args.output_dir)["dispositions"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

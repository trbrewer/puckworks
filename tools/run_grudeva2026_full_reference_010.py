#!/usr/bin/env python3
"""Explicit 010 campaign; ordinary pytest never executes these scientific rows."""
from __future__ import annotations

import argparse
from dataclasses import asdict
import datetime as dt
import fcntl
import json
from importlib.metadata import distribution
import resource
import os
from pathlib import Path
import platform
import shutil
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import scipy  # noqa: E402
from scipy.integrate._ivp import bdf  # noqa: E402

from puckworks.analysis.grudeva2026_full_reference_010 import (  # noqa: E402
    Case, Settings, integrate, liquid_flux,
)
from puckworks.analysis.grudeva2026_full_reference_010_io import (  # noqa: E402
    boundary_quadrature, capture, independent_inventories,
    load_archive, observe, save_archive, sha256, write_json,
)

DOC = ROOT/'docs/analysis/model_grudeva2026_full_reference_010'
FILES = ['tests/test_grudeva2026_full_reference_010.py', 'puckworks/analysis/grudeva2026_full_reference_010.py',
         'puckworks/analysis/grudeva2026_full_reference_010_io.py',
         'tools/run_grudeva2026_full_reference_010.py',
         'docs/analysis/model_grudeva2026_full_reference_010/CONTRACT.md',
         'docs/analysis/model_grudeva2026_full_reference_010/SOURCE.json']
LIMITS = {'liquid': 1e-3, 'outlet': 1e-3, 'grain_means': 2.3e-4,
          'grain_radial': 2.3e-4, 'M_l': 5e-5, 'M_f': 5e-5,
          'M_b': 5e-5, 'M_dry': 5e-5, 'J_in': 5e-5, 'J_out': 5e-5}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def environment():
    return {'distribution_records':{name:sha256(next(p.locate() for p in distribution(name).files if str(p).endswith('.dist-info/RECORD'))) for name in ['numpy','scipy']},'python': sys.version, 'numpy': np.__version__, 'scipy': scipy.__version__,
            'platform': platform.platform(), 'bdf_sha256': sha256(bdf.__file__),
            'threads': {k: os.environ.get(k) for k in
                        ['OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS']}}


def resources():
    meminfo=Path('/proc/meminfo').read_text()
    available=int(next(line.split()[1] for line in meminfo.splitlines() if line.startswith('MemAvailable:')))*1024
    path=Path('/sys/fs/cgroup')/Path('/proc/self/cgroup').read_text().split('::')[1].strip().lstrip('/')
    groups=[]
    while str(path).startswith('/sys/fs/cgroup'):
        values={n:(path/n).read_text().strip() if (path/n).exists() else 'NOT_EXPOSED'
                for n in ['memory.current','memory.max','memory.high']}
        groups.append(values)
        if values['memory.current'].isdigit():
            for limit in ['memory.max','memory.high']:
                if values[limit].isdigit():
                    available=min(available,int(values[limit])-int(values['memory.current']))
        path=path.parent
    return {'meminfo':meminfo,'cgroup_memory':groups,'available_bytes':available,
            'limits':Path('/proc/self/limits').read_text()}


def freeze():
    integration = json.loads((DOC/'INTEGRATION.json').read_text())
    if integration['status'] != 'PASS':
        raise ValueError('Current selected base integration is incomplete')
    development = json.loads((DOC/'DEVELOPMENT.json').read_text())
    if development['disposition'] != 'PASS':
        raise ValueError('Focused controls have not passed')
    anchor = asdict(Settings(axial=256, fines=32, boulders=64, rtol=1e-9,
                             atol=1e-14, max_step=.02, startup=1e-7))
    rows = {'anchor': anchor}
    for axis, field, levels in [('axial', 'axial', [64,128]), ('fines','fines',[8,16]),
                                ('boulders','boulders',[16,32]),
                                ('startup','startup',[1e-5,1e-6])]:
        for label, value in zip(['coarse','medium'], levels):
            rows[f'{axis}_{label}'] = {**anchor, field:value}
    rows['time_coarse'] = {**anchor, 'rtol':1e-5, 'atol':1e-10, 'max_step':.08}
    rows['time_medium'] = {**anchor, 'rtol':1e-7, 'atol':1e-12, 'max_step':.04}
    rows['combined_coarse'] = asdict(Settings(64,8,16,1e-5,1e-10,.08,1e-5))
    rows['combined_medium'] = asdict(Settings(128,16,32,1e-7,1e-12,.04,1e-6))
    rows['repeat'] = anchor.copy()
    positions = [0., .001, .01, .05, .1, .25, .5, .75, 1.]
    times = [0.,1e-7,1e-6,1e-5,1e-4,1e-3,.01,.025,.99,.9999,.999999,1.,1.000001,1.0001,1.01]
    times += list(np.linspace(.05, 8, 160))
    for z in positions:
        times += [z]+[z+age for age in [1e-6,1e-5,1e-4,.001,.01]]
    support = {'times': sorted(set(times)),
               'z': sorted(set(positions+[1e-8,5e-8,1e-7,5e-7,1e-6,5e-6,1e-5,1e-4]+list(np.linspace(0,1,201)))),
               'r': [0.,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95,.99,.999,1.],
               'history_positions': positions,
               'boundary_flux_columns':['signed_inlet','discharge','physical_front_or_outlet','ALE_relative_front_or_outlet'],
               'event_convention': 't=z grain initial; t=1 outlet right limit, Jout=0; dry liquid absent',
               'availability': {'liquid': 't>0 and 0<=z<=min(t,1)',
                                'outlet': 't>=1 (right limit at first drip)',
                                'grain_means': 'all z,t; dry and birth states initial',
                                'grain_radial': 'all z,t; dry and birth states initial',
                                'inventories': 'all t; wet-volume phases zero at t=0',
                                'integrals': 'all t; startup analytic then BDF states'}}
    matrix = {'task':'MODEL-GRUDEVA2026-FULL-REFERENCE-010','frozen_at':now(),
              'case':asdict(Case()),'rows':rows,'row_order':list(rows),
              'axes':['time','axial','fines','boulders','startup','combined'],
              'required_pair':'medium versus anchor on each axis including combined',
              'support':support,'limits':LIMITS,
              'combined_budget':'combined pair AND sum of five isolated fine differences <= limit',
              'trend':'decreasing when d_medium_fine < d_coarse_medium and both exceed floor; otherwise unestablished or resolved stability',
              'floor':'max(256*epsilon*max(1,observable absolute scale), repeat difference, time medium/fine difference for spatial axes)',
              'temporal_effectiveness':'distinct accepted-state/work patterns and at least one required nonconstant observable with decreasing changes above 10 times repeat/arithmetic floor',
              'uncertainty':'Conditional Richardson estimates only when ratio>1; not rigorous bounds; report none otherwise',
              'implementation':{p:sha256(ROOT/p) for p in FILES},
              'environment':environment(),'integration_sha256':sha256(DOC/'INTEGRATION.json'),
              'controls_sha256':sha256(DOC/'DEVELOPMENT.json')}
    write_json(DOC/'MATRIX.json',matrix)
    print('Frozen',len(rows),'rows; matrix',sha256(DOC/'MATRIX.json'),flush=True)


def load_matrix():
    matrix = json.loads((DOC/'MATRIX.json').read_text())
    for p, digest in matrix['implementation'].items():
        if sha256(ROOT/p) != digest:
            raise ValueError(f'Frozen implementation changed: {p}')
    if environment() != matrix['environment']:
        raise ValueError('Execution environment differs from freeze')
    review = json.loads((DOC/'PRE_CAMPAIGN_REVIEW.json').read_text())
    if review['disposition'] != 'PASS' or review['matrix_sha256'] != sha256(DOC/'MATRIX.json'):
        raise ValueError('Required independent pre-campaign review unavailable')
    return matrix


def extrema(values, coordinates):
    finite = np.isfinite(values)
    if not finite.any():
        return {'minimum':None,'maximum':None,'available':0,'requested':int(values.size)}
    result = {'requested':int(values.size),'available':int(finite.sum()),
              'unavailable':int((~finite).sum())}
    for label, which in [('minimum', np.nanargmin),('maximum', np.nanargmax)]:
        ids = np.unravel_index(which(values), values.shape)
        result[label] = float(values[ids])
        result[label+'_location'] = {k:(np.asarray(v)[idx].item())
                                    for (k,v),idx in zip(coordinates.items(),ids)}
    return result


def audit(trajectory, observations):
    model = trajectory.model
    native_times, inventories, accumulators, bounds = [], [], [], []
    residuals, independent_errors = [], []
    native_witnesses = {}
    def witness(label, value, t, z, r=None, population=None, kind='state'):
        better = label not in native_witnesses or (value < native_witnesses[label]['value'] if label.endswith('min') else value > native_witnesses[label]['value'])
        if better:
            native_witnesses[label] = {'value':float(value),'t':float(t),'z':float(z),
                                       'r':None if r is None else float(r),
                                       'population':population,'kind':kind}
    for seg in trajectory.segments:
        for t, y in zip(seg['t'], seg['y'].T):
            state = model.split(y,t)
            phases = model.inventories(float(t), y)
            check = independent_inventories(model,float(t),y)
            j=int(np.argmin(phases))
            witness('inventory_min',phases[j],t,0.,kind=['M_l','M_f','M_b','M_dry'][j])
            native_times.append(t); inventories.append(phases); accumulators.append(y[-2:])
            residuals.append(sum(check)+y[-1]-y[-2]-model.case.M0)
            independent_errors.append(max(abs(phases-check)))
            _, cout = liquid_flux(state[:,0],min(t,1.),seg['moving'],model.case.D_l)
            surfaces = [sphere.transfer(state[:,sl],state[:,0])[1]
                        for sphere,sl in zip(model.spheres,model.slices)]
            s=min(float(t),1.)
            for label, arg in [('aqueous_min',np.argmin),('aqueous_max',np.argmax)]:
                j=int(arg(state[:,0]));witness(label,state[j,0],t,s*model.xi[j])
                witness(label,0.,t,0.,kind='inlet');witness(label,cout,t,s,kind='front_or_outlet')
            for pop,(sphere,sl,surface) in enumerate(zip(model.spheres,model.slices,surfaces)):
                for label,arg in [('grain_min',np.argmin),('grain_max',np.argmax)]:
                    j,k=np.unravel_index(arg(state[:,sl]),state[:,sl].shape)
                    witness(label,state[:,sl][j,k],t,s*model.xi[j],sphere.r[k],pop)
                    j=int(arg(surface));witness(label,surface[j],t,s*model.xi[j],1.,pop,'surface')
            bounds.append([min(0.,state[:,0].min(),cout), max(state[:,0].max(),cout),
                           min(state[:,1:].min(),min(v.min() for v in surfaces)),
                           max(state[:,1:].max(),max(v.max() for v in surfaces)), min(phases)])
    ts, phases, acc, bounds = map(np.asarray,(native_times,inventories,accumulators,bounds))
    qtimes, q3 = boundary_quadrature(trajectory,3)
    _, q5 = boundary_quadrature(trajectory,5)
    evolved = np.array([trajectory.state(float(t))[-2:] for t in qtimes])
    actualphases = np.array([independent_inventories(model,float(t),trajectory.state(float(t))) for t in qtimes])
    balance = actualphases.sum(axis=1)+q5[:,1]-q5[:,0]-model.case.M0
    ix = int(np.argmax(abs(balance)))
    common_balance = observations['inventories'].sum(axis=1)+observations['integrals'][:,1]-observations['integrals'][:,0]-model.case.M0
    common = {}
    coords = {'t': observations['times'],'z': observations['z'],'population': [0,1],'r':observations['r']}
    for key in ('liquid','grain_means','grain_radial','outlet','inventories','integrals'):
        selected=dict(list(coords.items())[:observations[key].ndim])
        if key=='inventories':selected={'t':observations['times'],'phase':['M_l','M_f','M_b','M_dry']}
        if key=='integrals':selected={'t':observations['times'],'boundary':['J_in','J_out']}
        common[key] = extrema(observations[key],selected)
    stats = {'native_witnesses':native_witnesses,'native_states':len(ts),'native_extrema': {
                 'aqueous_min':float(bounds[:,0].min()),'aqueous_max':float(bounds[:,1].max()),
                 'grain_min':float(bounds[:,2].min()),'grain_max':float(bounds[:,3].max()),
                 'inventory_min':float(bounds[:,4].min())},
             'native_extrema_times':[float(ts[np.argmin(bounds[:,0])]),float(ts[np.argmax(bounds[:,1])]),
                                     float(ts[np.argmin(bounds[:,2])]),float(ts[np.argmax(bounds[:,3])])],
             'balance_independent_max':float(max(abs(balance))),
             'balance_independent_location':{'t':float(qtimes[ix]),'residual':float(balance[ix])},
             'balance_relative_to_M0':float(max(abs(balance))/model.case.M0),
             'balance_accumulator_max':float(max(abs(np.asarray(residuals)))),
             'balance_common_max':float(max(abs(common_balance))),
             'inventory_quadrature_max':float(max(independent_errors)),
             'boundary_quadrature_3_vs_5':np.max(abs(q3-q5),axis=0).tolist(),
             'boundary_quadrature_vs_evolved':np.max(abs(q5-evolved),axis=0).tolist(),
             'common_extrema':common,
             'terminal_inventories':phases[-1].tolist(),'terminal_Jin_Jout':acc[-1].tolist(),
             'complete':all(seg['success'] for seg in trajectory.segments) and ts[-1]==8.,
             'availability_reasons':{'liquid_unavailable':'dry support or zero wetted volume',
                                      'outlet_unavailable':'no discharge before t=1'},
             'work':[{k:seg[k] for k in ['nfev','njev','nlu']} for seg in trajectory.segments]}
    required_finite = (np.isfinite(observations['liquid'])[observations['wet']].all()
                       and all(np.isfinite(observations[k]).all() for k in
                               ['grain_means','grain_radial','inventories','integrals'])
                       and np.isfinite(observations['outlet'][observations['times']>=1]).all())
    n = stats['native_extrema']; c = common
    gates = {'complete':stats['complete'],'required_support':bool(required_finite),
             'conservation':max(stats['balance_independent_max'],stats['balance_common_max'])<=1e-6,
             'aqueous_bounds':min(n['aqueous_min'],c['liquid']['minimum'],c['outlet']['minimum'])>=-1e-8
                               and max(n['aqueous_max'],c['liquid']['maximum'],c['outlet']['maximum'])<=1+1e-8,
             'grain_bounds':min(n['grain_min'],c['grain_means']['minimum'],c['grain_radial']['minimum'])>=-1e-8,
             'phase_bounds':min(n['inventory_min'],c['inventories']['minimum'])>=-1e-8,
             'inventory_quadrature':stats['inventory_quadrature_max']<=1e-11*max(1,model.case.M0),
             'boundary_quadrature':max(stats['boundary_quadrature_3_vs_5'])<=2e-7,
             'boundary_accumulator':max(stats['boundary_quadrature_vs_evolved'])<=2e-7,
             'zero_predrip_cup':bool(np.all(observations['integrals'][observations['times']<=1,1]==0)),
             'transition_continuity':bool(np.array_equal(trajectory.segments[0]['y'][:,-1],trajectory.segments[1]['y'][:,0]))}
    stats['gates'] = {k:bool(v) for k,v in gates.items()}
    arrays = {'native_times':ts,'native_inventories':phases,'native_integrals':acc,
              'native_bounds':bounds,'independent_flux_times':qtimes,'independent_flux_integrals':q5,
              'independent_balance':balance,'independent_inventories':actualphases}
    return stats, arrays


def run_row(root, row):
    matrix = load_matrix()
    if row not in matrix['rows']:
        raise ValueError('Row outside frozen matrix')
    root.mkdir(parents=True,exist_ok=True)
    with (root/'execution.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        output = root/row
        output.mkdir(exist_ok=False)
        start = time.monotonic()
        write_json(output/'start.json',{'row':row,'started':now(),'pid':os.getpid(),
                                       'matrix_sha256':sha256(DOC/'MATRIX.json'),
                                       'environment':environment(),
                                       'free_disk_bytes':shutil.disk_usage(root).free,
                                       'host_meminfo':Path('/proc/meminfo').read_text(),
                                       'resources':resources()})
        try:
            if shutil.disk_usage(root).free < 8*1024**3:
                raise OSError('Insufficient safe archive disk headroom')
            if resources()['available_bytes']<2*1024**3:
                raise OSError('Insufficient memory headroom under existing OS/host limits')
            print('START',row,now(),flush=True)
            model, results = integrate(Settings(**matrix['rows'][row]))
            trajectory = capture(model,results)
            manifest = save_archive(output/'trajectory',trajectory,
                                    {'row':row,'matrix_sha256':sha256(DOC/'MATRIX.json'),
                                     'environment':matrix['environment'],
                                     'implementation':matrix['implementation']})
            for moving, result in results:
                if not result.success:
                    raise RuntimeError(result.message)
            # Exact arrays are verified by hashes; interpolant arithmetic gets its own audit.
            restored, _ = load_archive(output/'trajectory')
            max_error, max_scaled = 0., 0.
            for seg, (_, original) in zip(restored.segments, results):
                for t in (seg['t'][:-1]+seg['t'][1:])/2:
                    want, got = original.sol(t), restored.state(float(t))
                    error = float(max(abs(want-got)))
                    max_error=max(max_error,error)
                    max_scaled=max(max_scaled,error/(256*np.finfo(float).eps*max(1,float(max(abs(want))))))
            del restored
            observations = observe(trajectory,matrix['support'])
            stats, arrays = audit(trajectory,observations)
            np.savez_compressed(output/'observations.npz',**observations)
            np.savez_compressed(output/'diagnostics.npz',**arrays)
            stats['archive'] = {'manifest_sha256':sha256(output/'trajectory/manifest.json'),
                                'observations_sha256':sha256(output/'observations.npz'),
                                'diagnostics_sha256':sha256(output/'diagnostics.npz'),
                                'state_byte_identity':'PASS','evaluation_max':max_error,
                                'evaluation_allowance_fraction':max_scaled}
            stats['gates']['archive_evaluation'] = max_scaled<=1
            stats['elapsed_seconds'] = time.monotonic()-start
            stats['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            stats['settings']=matrix['rows'][row]
            write_json(output/'results.json',stats)
            write_json(output/'end.json',{'row':row,'ended':now(),'status':'COMPLETE',
                                         'seconds':time.monotonic()-start,'all_gates_passed':all(stats['gates'].values())})
            print('END',row,stats['elapsed_seconds'],stats['gates'],flush=True)
        except BaseException as exc:
            write_json(output/'failure.json',{'row':row,'ended':now(),'seconds':time.monotonic()-start,
                                             'exception':type(exc).__name__,'message':str(exc),
                                             'traceback':traceback.format_exc()})
            raise


def family_arrays(data):
    result={k:data[k] for k in ['liquid','outlet','grain_means','grain_radial']}
    for j,k in enumerate(['M_l','M_f','M_b','M_dry']): result[k]=data['inventories'][:,j]
    result.update(J_in=data['integrals'][:,0],J_out=data['integrals'][:,1])
    return result


def compare(a,b,support):
    left,right = family_arrays(a),family_arrays(b)
    metrics={}
    for key, value in left.items():
        diff=value-right[key]
        valid=np.isfinite(diff)
        ids=np.unravel_index(np.nanargmax(abs(diff)),diff.shape)
        coords={'t':support['times'][ids[0]]}
        for i,name in enumerate(['z','population','r'],1):
            if len(ids)>i: coords[name]=([0,1] if name=='population' else support[name])[ids[i]]
        maximum=float(abs(diff[ids]));scale=max(1.,float(np.nanmax(abs(value))))
        metrics[key]={'max_change':maximum,'signed_change':float(diff[ids]),'location':coords,
                      'left':float(value[ids]),'right':float(right[key][ids]),
                      'requested':int(value.size),'available':int(valid.sum()),
                      'unavailable':int((~valid).sum()),'limit':LIMITS[key],
                      'passed':maximum<=LIMITS[key],'roundoff_floor':256*np.finfo(float).eps*scale}
    return metrics


def report(root):
    matrix=load_matrix()
    rows={}
    for row in matrix['rows']:
        path=root/row/'results.json'
        rows[row]=json.loads(path.read_text()) if path.exists() else {'disposition':'INCOMPLETE'}
    if any('gates' not in row for row in rows.values()):
        partial={'task':matrix['task'],'disposition':'FULL_REFERENCE_QUALIFICATION_INCOMPLETE',
                 'physical_validation':'NOT_ESTABLISHED','rows':rows,'matrix_sha256':sha256(DOC/'MATRIX.json'),
                 'executed_rows':sum('gates' in row for row in rows.values()),'declared_rows':len(rows),
                 'reason':'Missing full rows; accepted partial trajectories and failures remain external; no reference qualification'}
        write_json(root/'RESULTS.json',partial)
        print(partial['disposition'],flush=True)
        return
    with np.load(root/'anchor/observations.npz',allow_pickle=False) as f: anchor={k:f[k] for k in f.files}
    pairs={}
    with np.load(root/'repeat/observations.npz',allow_pickle=False) as f:
        repeat={k:f[k] for k in f.files}
    pairs['repeat']=compare(repeat,anchor,matrix['support'])
    for axis in matrix['axes']:
        data=[]
        for level in ['coarse','medium']:
            with np.load(root/f'{axis}_{level}/observations.npz',allow_pickle=False) as f:
                data.append({k:f[k] for k in f.files})
        pairs[axis+'_coarse_medium']=compare(data[0],data[1],matrix['support'])
        pairs[axis+'_medium_fine']=compare(data[1],anchor,matrix['support'])
    trends={}
    budgets={}
    for key in LIMITS:
        summed=sum(pairs[axis+'_medium_fine'][key]['max_change'] for axis in matrix['axes'] if axis!='combined')
        combined=pairs['combined_medium_fine'][key]['max_change']
        budgets[key]={'sum_isolated_changes':summed,'combined_change':combined,'limit':LIMITS[key],
                      'passed':max(summed,combined)<=LIMITS[key]}
        for axis in matrix['axes']:
            d1=pairs[axis+'_coarse_medium'][key]['max_change'];d2=pairs[axis+'_medium_fine'][key]['max_change']
            floor=max(pairs['repeat'][key]['max_change'],pairs['repeat'][key]['roundoff_floor'])
            if axis not in ('time','startup'): floor=max(floor,pairs['time_medium_fine'][key]['max_change'])
            status='DECREASING' if d1>d2>floor else ('RESOLVED_STABILITY' if max(d1,d2)<=floor else 'TREND_UNESTABLISHED')
            ratio=d1/d2 if d2>floor else None
            trends[f'{axis}/{key}']={'coarse_medium':d1,'medium_fine':d2,'floor':floor,'status':status,
                                    'conditional_estimated_fine_error':d2/(ratio-1) if ratio is not None and ratio>1 else None,
                                    'interpretation':'Richardson-type estimate assumes the measured ratio persists; not a continuum certificate'}
    repeat_state=True
    for j in [0,1]:
        a=json.loads((root/'anchor/trajectory/manifest.json').read_text())['segments'][j]['arrays']
        b=json.loads((root/'repeat/trajectory/manifest.json').read_text())['segments'][j]['arrays']
        repeat_state &= a==b
    temporal_effective=(rows['time_coarse']['native_states']!=rows['anchor']['native_states']
        and any(pairs['time_coarse_medium'][key]['max_change']>pairs['time_medium_fine'][key]['max_change']>
                10*max(pairs['repeat'][key]['roundoff_floor'],pairs['repeat'][key]['max_change'])
                for key in ['liquid','outlet','grain_means','grain_radial','J_out']))
    passed=temporal_effective and all(all(row.get('gates',{'missing':False}).values()) for row in rows.values()) and all(x['passed'] for x in budgets.values()) and repeat_state
    result={'task':matrix['task'],'disposition':'FULL_REFERENCE_NUMERICALLY_QUALIFIED_ON_DECLARED_SYNTHETIC_CASE' if passed else 'FULL_REFERENCE_QUALIFICATION_INCOMPLETE',
            'physical_validation':'NOT_ESTABLISHED','matrix_sha256':sha256(DOC/'MATRIX.json'),
            'executed_rows':sum('gates' in row for row in rows.values()),'declared_rows':len(rows),
            'reused_full_model_runs':0,'rows':rows,'refinement':pairs,'combined_budgets':budgets,
            'trends':trends,'repeat_native_state_identity':repeat_state,'temporal_effectiveness':temporal_effective,
            'limitations':['Not physical validation','Not a rigorous continuum-error bound','No reduced-model comparison','Not Figure 5 reproduction']}
    write_json(root/'RESULTS.json',result)
    print(result['disposition'],flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['freeze','run','report'])
    p.add_argument('--archive-root',type=Path)
    p.add_argument('--row')
    a=p.parse_args()
    if a.operation=='freeze': freeze()
    elif a.archive_root is None: p.error('--archive-root required')
    elif a.operation=='run': run_row(a.archive_root,a.row)
    else: report(a.archive_root)


if __name__=='__main__':
    main()

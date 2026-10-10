#!/usr/bin/env python3
"""Explicit 010 campaign; ordinary pytest never executes these scientific rows."""
from __future__ import annotations

import argparse
import base64
import gc
import hashlib
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
import subprocess
import sys
import time
import traceback
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import scipy  # noqa: E402
from scipy.integrate._ivp import bdf  # noqa: E402

from puckworks.analysis.grudeva2026_full_reference_010 import (  # noqa: E402
    Case, Settings, integrate, liquid_flux,
)
from puckworks.analysis.grudeva2026_full_reference_010_io import (  # noqa: E402
    array_identity, boundary_quadrature, capture, independent_inventories,
    load_archive, observe, save_archive, sha256, write_json,
    CaptureMismatch, persist_capture_failure,
    save_checkpoints, load_checkpoints, sync_directory,
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


ORIGINAL_MATRIX_SHA256 = '092269b20b88d413abbfb1350240d32ab869e985cf1825ef1f28f73462e667d3'
CONTINUATION_FILES = {FILES[0], FILES[2], FILES[3]}


def continuation_binding(matrix):
    """Explicit reviewed hash transition; no arbitrary changed-source bypass."""
    path = DOC/'CONTINUATION.json'
    binding = json.loads(path.read_text())
    if (sha256(DOC/'MATRIX.json') != ORIGINAL_MATRIX_SHA256
            or binding['original_matrix_sha256'] != ORIGINAL_MATRIX_SHA256
            or binding['original_implementation'] != matrix['implementation']):
        raise ValueError('Original continuation matrix/implementation identity mismatch')
    if set(binding['implementation']) != set(matrix['implementation']):
        raise ValueError('Continuation implementation scope mismatch')
    changed = {p for p in matrix['implementation']
               if binding['implementation'][p] != matrix['implementation'][p]}
    if changed != CONTINUATION_FILES or set(binding['changed_files']) != changed:
        raise ValueError('Unapproved continuation file delta')
    for p, digest in binding['implementation'].items():
        if sha256(ROOT/p) != digest:
            raise ValueError(f'Continuation implementation changed: {p}')
    if binding['environment'] != matrix['environment'] or environment() != binding['environment']:
        raise ValueError('Continuation environment changed')
    if binding['archive_schema'] != 'grudeva-full-010-v2' or binding['row_order'] != matrix['row_order']:
        raise ValueError('Continuation archive semantics or row order changed')
    for name, digest in binding['control_documents'].items():
        if Path(name).name != name or sha256(DOC/name) != digest:
            raise ValueError('Continuation control/plan identity mismatch')
    controls = json.loads((DOC/'CONTINUATION_CONTROLS.json').read_text())
    review = json.loads((DOC/'CONTINUATION_PRE_REVIEW.json').read_text())
    if (controls['disposition'] != 'PASS' or review['disposition'] != 'PASS'
            or review['continuation_sha256'] != sha256(path)):
        raise ValueError('Required continuation controls/review unavailable')
    return binding


def executable_identity():
    """Check actual installed bytes against RECORD, not version strings alone."""
    records = {}
    for name in ('numpy', 'scipy'):
        entries = {}
        for entry in distribution(name).files:
            if entry.hash is None:
                continue
            if entry.hash.mode != 'sha256':
                raise ValueError('Unsupported installed-file hash')
            digest = sha256(entry.locate())
            expected = base64.urlsafe_b64decode(entry.hash.value+'='*((-len(entry.hash.value)) % 4)).hex()
            if digest != expected:
                raise ValueError(f'Installed scientific input identity mismatch: {name}/{entry}')
            entries[str(entry)] = digest
        records[name] = {'files': len(entries), 'sha256': hashlib.sha256(
            json.dumps(entries, sort_keys=True).encode()).hexdigest()}
    return {'python_sha256': sha256(sys.executable), 'installed_files': records}


def rerun_binding(matrix, root=None):
    """Specific owner-authorized rerun; historical binding paths stay strict."""
    binding = json.loads((DOC/'RERUN.json').read_text())
    if (binding['authorization'] != 'OWNER AUTHORIZATION — CONTROLLED SCIENTIFIC RERUN / MODEL-GRUDEVA2026-FULL-REFERENCE-010'
            or sha256(DOC/'MATRIX.json') != ORIGINAL_MATRIX_SHA256
            or binding['original_matrix_sha256'] != ORIGINAL_MATRIX_SHA256
            or binding['original_implementation'] != matrix['implementation']):
        raise ValueError('Rerun matrix/authorization identity mismatch')
    changed = {p for p in matrix['implementation'] if binding['implementation'][p] != matrix['implementation'][p]}
    if (set(binding['implementation']) != set(matrix['implementation'])
            or changed != CONTINUATION_FILES or set(binding['changed_files']) != changed):
        raise ValueError('Unapproved rerun source scope')
    for path, digest in binding['implementation'].items():
        if sha256(ROOT/path) != digest:
            raise ValueError(f'Rerun source identity mismatch: {path}')
    order = ['anchor', 'repeat']+[r for r in matrix['row_order'] if r not in ('anchor', 'repeat')]
    if binding['row_order'] != order or len(set(order)) != 14:
        raise ValueError('Rerun execution order mismatch')
    if (binding['environment'] != environment() or binding['executable'] != executable_identity()
            or any(v != '1' for v in binding['environment']['threads'].values())):
        raise ValueError('Rerun executable/environment mismatch')
    for name, digest in binding['reused_documents'].items():
        if Path(name).name != name or sha256(DOC/name) != digest:
            raise ValueError('Reused evidence identity mismatch')
    if root is not None and hashlib.sha256(str(root.resolve()).encode()).hexdigest() != binding['evidence_directory_identity']:
        raise ValueError('Rerun requires its exclusive bound evidence directory')
    return binding


def binding_digest(binding):
    return sha256(DOC/('RERUN.json' if binding and 'authorization' in binding else 'CONTINUATION.json')) if binding else None


def load_matrix(continuation=False, rerun=False):
    matrix = json.loads((DOC/'MATRIX.json').read_text())
    if rerun:
        rerun_binding(matrix)
    elif continuation:
        continuation_binding(matrix)
    else:
        for p, digest in matrix['implementation'].items():
            if sha256(ROOT/p) != digest:
                raise ValueError(f'Frozen implementation changed: {p}')
    if not rerun and environment() != matrix['environment']:
        raise ValueError('Execution environment differs from freeze')
    review = json.loads((DOC/'PRE_CAMPAIGN_REVIEW.json').read_text())
    if review['disposition'] != 'PASS' or review['matrix_sha256'] != sha256(DOC/'MATRIX.json'):
        raise ValueError('Required independent pre-campaign review unavailable')
    return matrix


def provisional_summary(trajectory):
    """Compact accepted-state diagnostics, with no independent flux claim."""
    model = trajectory.model
    extrema = np.array([np.inf, -np.inf, np.inf, -np.inf, np.inf])
    balance_max, count, samples = 0., 0, []
    for segment in trajectory.segments:
        selected = set(np.linspace(0, len(segment['t'])-1, 41, dtype=int))
        for index, (t, y) in enumerate(zip(segment['t'], segment['y'].T)):
            state = model.split(y, t)
            phases = model.inventories(float(t), y)
            _, outlet = liquid_flux(state[:, 0], min(t, 1.), segment['moving'], model.case.D_l)
            surfaces = [sphere.transfer(state[:, sl], state[:, 0])[1]
                        for sphere, sl in zip(model.spheres, model.slices)]
            values = [min(0., state[:, 0].min(), outlet), max(state[:, 0].max(), outlet),
                      min(state[:, 1:].min(), min(v.min() for v in surfaces)),
                      max(state[:, 1:].max(), max(v.max() for v in surfaces)), min(phases)]
            extrema[[0, 2, 4]] = np.minimum(extrema[[0, 2, 4]], np.asarray(values)[[0, 2, 4]])
            extrema[[1, 3]] = np.maximum(extrema[[1, 3]], np.asarray(values)[[1, 3]])
            residual = float(sum(phases)+y[-1]-y[-2]-model.case.M0)
            if not np.isfinite([*values, *phases, residual]).all():
                raise ValueError('Nonfinite accepted numerical summary')
            balance_max = max(balance_max, abs(residual)); count += 1
            if index in selected:
                samples.append({'t': float(t), 'moving': segment['moving'],
                                'outlet': None if segment['moving'] else float(outlet),
                                'inventories': phases.tolist(), 'Jin_Jout': y[-2:].tolist(),
                                'accumulator_balance': residual})
    return {'label': 'PROVISIONAL — NOT FULL_REFERENCE_QUALIFICATION',
            'balance_kind': 'model inventory plus evolved boundary accumulators; independent final flux/quadrature audit pending',
            'native_states': count, 'balance_accumulator_max': balance_max,
            'native_extrema': dict(zip(('aqueous_min', 'aqueous_max', 'grain_min', 'grain_max', 'inventory_min'), extrema.tolist())),
            'evolution': samples}


def fresh_read(directory, kind):
    """No solver in reader; its receipt binds verified metadata identities."""
    subprocess.run([sys.executable, str(Path(__file__).resolve()), 'readback',
                    '--archive-root', str(directory), '--row', kind], check=True)


def reconcile_provisional(early, final):
    """Byte identities are exact; reevaluated floating-point summaries are not."""
    errors = []
    def check(a, b):
        if isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys():
            for key in a:
                check(a[key], b[key])
        elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
            for x, y in zip(a, b):
                check(x, y)
        elif isinstance(a, float) and isinstance(b, float):
            allowance = 256*np.finfo(float).eps*max(1., abs(a), abs(b))
            errors.append(abs(a-b)/allowance)
            if not np.isfinite([a, b]).all() or abs(a-b) > allowance:
                raise ValueError('Provisional/validated numerical summary mismatch')
        elif a != b:
            raise ValueError('Provisional/validated summary structure mismatch')
    check(early, final)
    return max(errors, default=0.)


def readback(directory, kind):
    if kind == 'checkpoint':
        trajectory, _ = load_checkpoints(directory)
        write_json(directory/'PROVISIONAL.json', provisional_summary(trajectory))
        identity = {'checkpoint_sha256': sha256(directory/'checkpoint.json'),
                    'summary_sha256': sha256(directory/'PROVISIONAL.json')}
    elif kind == 'archive':
        trajectory, _ = load_archive(directory)
        identity = {'manifest_sha256': sha256(directory/'manifest.json')}
    elif kind == 'bundles':
        stats = json.loads((directory/'results.json').read_text())
        for name in ('observations', 'diagnostics'):
            validate_bundle(directory/(name+'.npz'), stats['archive'][
                'observation_bundle' if name == 'observations' else 'diagnostic_bundle'])
        identity = {'results_sha256': sha256(directory/'results.json')}
    else:
        raise ValueError('Unknown readback kind')
    write_json(directory/f'{kind}-fresh-read.json', {'status': 'PASS', 'pid': os.getpid(), **identity})
    sync_directory(directory)


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


def bundle_identity(value):
    """Exact observation bytes; NaN availability and bool masks are retained."""
    a = np.asarray(value)
    if a.dtype.kind not in 'fiub':
        raise ValueError('Unsafe observation dtype')
    identity = array_identity(a.view(np.uint8) if a.dtype.kind == 'b' else a)
    return {**identity, 'dtype': a.dtype.str, 'shape': list(a.shape)}


def validate_bundle(path, record):
    commitment = path.with_suffix('.source.json')
    if sha256(path) != record['sha256'] or sha256(commitment) != record['source_sha256']:
        raise ValueError('Observation bundle file/commitment identity mismatch')
    expected = json.loads(commitment.read_text())
    if expected != record['arrays']:
        raise ValueError('Observation prospective commitment mismatch')
    with zipfile.ZipFile(path) as archive:
        if sorted(archive.namelist()) != sorted(k+'.npy' for k in expected):
            raise ValueError('Observation bundle array set mismatch')
        for key, identity in expected.items():
            with archive.open(key+'.npy') as stream:
                version = np.lib.format.read_magic(stream)
                reader = {(1, 0):np.lib.format.read_array_header_1_0,
                          (2, 0):np.lib.format.read_array_header_2_0}.get(version)
                if reader is None:
                    raise ValueError('Unsupported observation header')
                shape, fortran, dtype = reader(stream)
                if dtype.kind not in 'fiub' or fortran:
                    raise ValueError('Unsafe observation dtype/order')
                h, count = hashlib.sha256(), 0
                for block in iter(lambda: stream.read(4*1024**2), b''):
                    h.update(block); count += len(block)
                if (count != int(np.prod(shape, dtype=object))*dtype.itemsize
                        or {'shape':list(shape), 'dtype':dtype.str, 'sha256':h.hexdigest()} != identity):
                    raise ValueError('Observation serialized payload identity mismatch')
    with np.load(path, allow_pickle=False) as loaded:
        for key, identity in expected.items():
            if bundle_identity(loaded[key]) != identity:
                raise ValueError('Observation loaded payload identity mismatch')


def save_bundle(path, values):
    expected = {key:bundle_identity(value) for key,value in values.items()}
    snapshots = {key:np.array(value, copy=True, order='C') for key,value in values.items()}
    for key, a in snapshots.items():
        if bundle_identity(a) != expected[key] or bundle_identity(values[key]) != expected[key]:
            raise ValueError('Observation source mutation during capture')
        a.flags.writeable = False
    write_json(path.with_suffix('.source.json'), expected)
    with path.open('xb') as stream:
        np.savez_compressed(stream, **snapshots)
        stream.flush(); os.fsync(stream.fileno())
    for key, a in snapshots.items():
        if bundle_identity(a) != expected[key] or bundle_identity(values[key]) != expected[key]:
            raise ValueError('Observation source mutation during serialization')
    record = {'sha256':sha256(path), 'source_sha256':sha256(path.with_suffix('.source.json')),
              'arrays':expected, 'order':'C'}
    validate_bundle(path, record)
    return record


def preserve_run_failure(output, exc, record):
    """Retain the original failure even if secondary diagnostic writes fail."""
    if isinstance(exc, CaptureMismatch):
        if exc.record.get('kind') == 'NUMERIC_MEMBER_REJECTED':
            record['numeric_failure'] = exc.record
        record['capture_comparisons'] = exc.record.get('comparisons')
        record['capture_location'] = {k: exc.record.get(k) for k in
                                      ('segment', 'moving', 'interval', 'component')}
    try:
        write_json(output/'failure.json', record)
    except BaseException as error:
        print('Original failure:', json.dumps(record), file=sys.stderr, flush=True)
        print('Secondary failure-record write error:', repr(error), file=sys.stderr, flush=True)
    if isinstance(exc, CaptureMismatch):
        try:
            receipt = persist_capture_failure(output/'capture-quarantine', exc)
            if receipt['errors']:
                print('Secondary capture diagnostic errors:', receipt['errors'], file=sys.stderr, flush=True)
        except BaseException as error:
            secondary = {'error': f'{type(error).__name__}: {error}',
                         'primary_failure': 'failure.json already attempted; original exception remains primary'}
            print('Secondary capture diagnostic error:', secondary, file=sys.stderr, flush=True)
            try:
                write_json(output/'diagnostic-preservation-error.json', secondary)
            except BaseException as write_error:
                print('Secondary diagnostic receipt error:', repr(write_error), file=sys.stderr, flush=True)


def run_row(root, row, continuation=False, rerun=False):
    matrix = load_matrix(continuation, rerun)
    binding = rerun_binding(matrix, root) if rerun else (continuation_binding(matrix) if continuation else None)
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
                                       'continuation_sha256':binding_digest(binding),
                                       'free_disk_bytes':shutil.disk_usage(root).free,
                                       'host_meminfo':Path('/proc/meminfo').read_text(),
                                       'resources':resources()})
        stage = 'ADMISSION'
        try:
            if rerun:
                admit_rerun_row(root, row, matrix, binding)
            if binding and row != 'anchor':
                # Other rows do not consume anchor values; report() independently
                # revalidates every archive before any reference comparison.
                validate_saved_row(root/'anchor', matrix, binding, full_archive=False)
            if shutil.disk_usage(root).free < (60 if binding else 8)*1024**3:
                raise OSError('Insufficient safe archive disk headroom')
            if resources()['available_bytes']<(160 if binding else 2)*1024**3:
                raise OSError('Insufficient memory headroom under existing OS/host limits')
            print('START',row,now(),flush=True)
            stage = 'INTEGRATING'
            write_json(output/'solver-start.json', {'row':row,'started':now(),'settings':matrix['rows'][row]})
            model, results = integrate(Settings(**matrix['rows'][row]))
            solver_complete = all(r.success for _, r in results) and results[-1][1].t[-1] == 8.
            write_json(output/'solver-end.json', {'row':row,'ended':now(),'status':'COMPLETE' if solver_complete else 'FAILED',
                       'segments':[{'moving':moving,'success':bool(r.success),'accepted_entries':len(r.t),
                                    'start':float(r.t[0]),'end':float(r.t[-1]),'message':r.message} for moving,r in results]})
            checkpoints = None
            if rerun:
                stage = 'CHECKPOINTING'
                save_checkpoints(output/'checkpoints', model, results,
                                 {'row': row, 'binding_sha256': binding_digest(binding)})
                stage = 'CHECKPOINT_FRESH_READ_AND_PROVISIONAL'
                fresh_read(output/'checkpoints', 'checkpoint')
                checkpoints, _ = load_checkpoints(output/'checkpoints')
            if not solver_complete:
                stage = 'RETAINING_PARTIAL_SOLVER_STATES'
                partial = capture(model, results, {'run': row, 'diagnostic': 'capture-integrity'})
                save_archive(output/'partial-trajectory', partial,
                             {'row':row,'role':'returned accepted states, incomplete solver; not qualified',
                              'matrix_sha256':sha256(DOC/'MATRIX.json')}, complete=False)
                raise RuntimeError('Integrator did not complete the declared horizon; returned states retained')
            if rerun:
                rerun_binding(matrix, root)
            stage = 'CAPTURING'
            trajectory = capture(model,results, {'run': row, 'diagnostic': 'capture-integrity'}, checkpoints=checkpoints)
            stage = 'WRITING_ARCHIVE'
            manifest = save_archive(output/'trajectory',trajectory,
                                    {'row':row,'matrix_sha256':sha256(DOC/'MATRIX.json'),
                                     'environment':environment(),
                                     'implementation':binding['implementation'] if binding else matrix['implementation'],
                                     'continuation_sha256':binding_digest(binding)},
                                    checkpoint_directory=output/'checkpoints' if rerun else None)
            if rerun:
                sync_directory(output/'trajectory')
                stage = 'ARCHIVE_FRESH_READ'
                fresh_read(output/'trajectory', 'archive')
            for moving, result in results:
                if not result.success:
                    raise RuntimeError(result.message)
            # Exact arrays are verified by hashes; interpolant arithmetic gets its own audit.
            stage = 'RELOADING_ARCHIVE'
            restored, _ = load_archive(output/'trajectory')
            stage = 'INTERPOLANT_FIDELITY'
            max_error, max_scaled = 0., 0.
            for seg, (_, original) in zip(restored.segments, results):
                for t in (seg['t'][:-1]+seg['t'][1:])/2:
                    want, got = original.sol(t), restored.state(float(t))
                    error = float(max(abs(want-got)))
                    max_error=max(max_error,error)
                    max_scaled=max(max_scaled,error/(256*np.finfo(float).eps*max(1,float(max(abs(want))))))
            # All observations/audits consume the independently validated archive.
            # Release original dense solver and capture buffers before auditing.
            trajectory = restored
            del results, original, result
            gc.collect()
            if rerun:
                stage = 'PROVISIONAL_RECONCILIATION'
                early = json.loads((output/'checkpoints/PROVISIONAL.json').read_text())
                final = provisional_summary(trajectory)
                summary_fraction = reconcile_provisional(early, final)
                write_json(output/'provisional-reconciliation.json',
                           {'status': 'PASS', 'accepted_state_bytes': 'EXACT',
                            'summary_evaluation_allowance_fraction': summary_fraction,
                            'independent_flux_audit': 'SEPARATE_REQUIRED_AUDIT'})
            stage = 'OBSERVING'
            observations = observe(trajectory,matrix['support'])
            stage = 'AUDITING'
            stats, arrays = audit(trajectory,observations)
            stage = 'SAVING_AUDITS'
            observation_record = save_bundle(output/'observations.npz', observations)
            diagnostic_record = save_bundle(output/'diagnostics.npz', arrays)
            stats['archive'] = {'observation_bundle':observation_record,
                                'diagnostic_bundle':diagnostic_record,
                                'manifest_sha256':sha256(output/'trajectory/manifest.json'),
                                'observations_sha256':sha256(output/'observations.npz'),
                                'diagnostics_sha256':sha256(output/'diagnostics.npz'),
                                'state_byte_identity':'PASS','evaluation_max':max_error,
                                'evaluation_allowance_fraction':max_scaled}
            stats['gates']['archive_evaluation'] = max_scaled<=1
            stats['elapsed_seconds'] = time.monotonic()-start
            stats['peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            stats['settings']=matrix['rows'][row]
            stats['continuation_sha256']=binding_digest(binding)
            stats['observation_source']='independently validated archive payloads'
            write_json(output/'results.json',stats)
            if rerun:
                stage = 'BUNDLE_FRESH_READ'
                fresh_read(output, 'bundles')
                rerun_binding(matrix, root)
                if not stats['gates']['required_support'] or not stats['gates']['archive_evaluation']:
                    raise ValueError('Required observation support or interpolant fidelity failed')
            write_json(output/'end.json',{'row':row,'ended':now(),'status':'COMPLETE',
                                         'seconds':time.monotonic()-start,'all_gates_passed':all(stats['gates'].values()),
                                         'solver_status':'COMPLETE','archive_status':'PASS','observation_status':'COMPLETE',
                                         'results_sha256':sha256(output/'results.json'),
                                         'archive_manifest_sha256':sha256(output/'trajectory/manifest.json'),
                                         'continuation_sha256':binding_digest(binding)})
            print('END',row,stats['elapsed_seconds'],stats['gates'],flush=True)
        except BaseException as exc:
            preserve_run_failure(output, exc, {'row':row,'ended':now(),'seconds':time.monotonic()-start,
                                             'stage':stage,'archive_manifest_published':(output/'trajectory/manifest.json').exists(),
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


def validate_saved_row(path, matrix, binding, full_archive=True):
    """Revalidate content identities; presence/completion labels are insufficient."""
    end = json.loads((path/'end.json').read_text())
    stats = json.loads((path/'results.json').read_text())
    expected_binding = binding_digest(binding)
    if (end['status'] != 'COMPLETE' or end['results_sha256'] != sha256(path/'results.json')
            or end['continuation_sha256'] != expected_binding
            or stats['continuation_sha256'] != expected_binding):
        raise ValueError('Saved row result/continuation identity mismatch')
    if (stats['settings'] != matrix['rows'][path.name]
            or end['archive_manifest_sha256'] != sha256(path/'trajectory/manifest.json')
            or stats['archive']['manifest_sha256'] != end['archive_manifest_sha256']):
        raise ValueError('Saved row settings/archive identity mismatch')
    for key, file in [('observations_sha256', 'observations.npz'), ('diagnostics_sha256', 'diagnostics.npz')]:
        if stats['archive'][key] != sha256(path/file):
            raise ValueError('Saved observation/diagnostic identity mismatch')
    manifest = json.loads((path/'trajectory/manifest.json').read_text())
    if (manifest['case'] != matrix['case'] or manifest['settings'] != matrix['rows'][path.name]
            or manifest['metadata']['row'] != path.name
            or manifest['metadata']['implementation'] != (binding['implementation'] if binding else matrix['implementation'])
            or manifest['metadata']['matrix_sha256'] != ORIGINAL_MATRIX_SHA256
            or manifest['metadata']['continuation_sha256'] != expected_binding):
        raise ValueError('Saved archive row/case/settings/implementation mismatch')
    if binding:
        validate_bundle(path/'observations.npz', stats['archive']['observation_bundle'])
        validate_bundle(path/'diagnostics.npz', stats['archive']['diagnostic_bundle'])
    if full_archive:
        trajectory, manifest = load_archive(path/'trajectory')
        if (manifest['metadata']['matrix_sha256'] != ORIGINAL_MATRIX_SHA256
                or manifest['metadata']['continuation_sha256'] != expected_binding):
            raise ValueError('Saved archive lineage mismatch')
        del trajectory
    return stats


def repeat_check(root, matrix, binding):
    """Fresh process revalidates both archives; compare science, not timestamps."""
    stats = {row: validate_saved_row(root/row, matrix, binding) for row in ('anchor', 'repeat')}
    if not all(v['gates']['required_support'] and v['gates']['archive_evaluation'] for v in stats.values()):
        raise ValueError('Missing required repeat support/fidelity')
    manifests = [json.loads((root/row/'trajectory/manifest.json').read_text()) for row in ('anchor', 'repeat')]
    identities = [[{key: rec['array'] for key, rec in segment['arrays'].items()}
                   for segment in manifest['segments']] for manifest in manifests]
    observations = []
    for row in ('anchor', 'repeat'):
        with np.load(root/row/'observations.npz', allow_pickle=False) as values:
            observations.append({key: values[key] for key in values.files})
    metrics = compare(observations[1], observations[0], matrix['support'])
    exact_observations = all(bundle_identity(observations[0][k]) == bundle_identity(observations[1][k])
                             for k in observations[0])
    passed = identities[0] == identities[1] and exact_observations
    write_json(root/'REPEAT.json', {'status': 'PASS' if passed else 'FAIL',
               'binding_sha256': binding_digest(binding),
               'manifest_sha256': [sha256(root/row/'trajectory/manifest.json') for row in ('anchor', 'repeat')],
               'scientific_array_identity': identities[0] == identities[1],
               'exact_observations': exact_observations, 'metrics': metrics})
    if not passed:
        raise ValueError('Unresolved independent repeatability failure')


def admit_rerun_row(root, row, matrix, binding):
    order = binding['row_order']
    # Current row directory already exists; every earlier row must be complete.
    for previous in order[:order.index(row)]:
        stats = validate_saved_row(root/previous, matrix, binding, full_archive=False)
        if not all(stats['gates'][key] for key in ('complete', 'required_support', 'archive_evaluation')):
            raise ValueError('Earlier row lacks required integrity/integration/support')
    if any((root/later).exists() for later in order[order.index(row)+1:]):
        raise ValueError('Rerun order violation')
    if row not in ('anchor', 'repeat'):
        repeat = json.loads((root/'REPEAT.json').read_text())
        if (repeat['status'] != 'PASS' or repeat['binding_sha256'] != binding_digest(binding)
                or repeat['manifest_sha256'] != [sha256(root/r/'trajectory/manifest.json') for r in ('anchor', 'repeat')]):
            raise ValueError('Repeatability admission missing or stale')


def report(root, continuation=False, rerun=False):
    matrix=load_matrix(continuation, rerun)
    binding=rerun_binding(matrix, root) if rerun else (continuation_binding(matrix) if continuation else None)
    rows={}
    for row in matrix['row_order']:
        path=root/row/'results.json'
        rows[row]=(validate_saved_row(root/row, matrix, binding) if binding else json.loads(path.read_text())) if path.exists() and (not rerun or (root/row/'end.json').exists()) else {'disposition':'INCOMPLETE'}
    if any('gates' not in row for row in rows.values()):
        partial={'task':matrix['task'],'disposition':'FULL_REFERENCE_QUALIFICATION_INCOMPLETE',
                 'physical_validation':'NOT_ESTABLISHED','rows':rows,'matrix_sha256':sha256(DOC/'MATRIX.json'),
                 'audited_rows':sum('gates' in row for row in rows.values()),'declared_rows':len(rows),
                 'solver_started_rows':sum((root/name/'solver-start.json').exists() for name in matrix['row_order']),
                 'solver_complete_rows':sum((root/name/'solver-end.json').exists() and json.loads((root/name/'solver-end.json').read_text())['status']=='COMPLETE' for name in matrix['row_order']),
                 'original_failed_solver_complete_rows':2 if rerun else (1 if binding else 0),
                 'continuation_sha256':binding_digest(binding),
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
        repeat_state &= {k:v['array'] for k,v in a.items()} == {k:v['array'] for k,v in b.items()}
    temporal_effective=(rows['time_coarse']['native_states']!=rows['anchor']['native_states']
        and any(pairs['time_coarse_medium'][key]['max_change']>pairs['time_medium_fine'][key]['max_change']>
                10*max(pairs['repeat'][key]['roundoff_floor'],pairs['repeat'][key]['max_change'])
                for key in ['liquid','outlet','grain_means','grain_radial','J_out']))
    passed=temporal_effective and all(all(row.get('gates',{'missing':False}).values()) for row in rows.values()) and all(x['passed'] for x in budgets.values()) and repeat_state
    result={'task':matrix['task'],'disposition':'FULL_REFERENCE_NUMERICALLY_QUALIFIED_ON_DECLARED_SYNTHETIC_CASE' if passed else 'FULL_REFERENCE_QUALIFICATION_INCOMPLETE',
            'physical_validation':'NOT_ESTABLISHED','matrix_sha256':sha256(DOC/'MATRIX.json'),
            'audited_rows':sum('gates' in row for row in rows.values()),'declared_rows':len(rows),
                 'solver_started_rows':sum((root/name/'solver-start.json').exists() for name in matrix['row_order']),
                 'solver_complete_rows':sum((root/name/'solver-end.json').exists() and json.loads((root/name/'solver-end.json').read_text())['status']=='COMPLETE' for name in matrix['row_order']),
                 'original_failed_solver_complete_rows':2 if rerun else (1 if binding else 0),
                 'continuation_sha256':binding_digest(binding),
            'reused_full_model_runs':0,'rows':rows,'refinement':pairs,'combined_budgets':budgets,
            'trends':trends,'repeat_native_state_identity':repeat_state,'temporal_effectiveness':temporal_effective,
            'limitations':['Not physical validation','Not a rigorous continuum-error bound','No reduced-model comparison','Not Figure 5 reproduction']}
    write_json(root/'RESULTS.json',result)
    print(result['disposition'],flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation',choices=['freeze','run','report','readback','repeat-check'])
    p.add_argument('--archive-root',type=Path)
    p.add_argument('--row')
    p.add_argument('--continuation', action='store_true', help='Validate the reviewed 010 continuation binding; never ignore hashes')
    p.add_argument('--rerun', action='store_true', help='Validate the specific controlled rerun binding')
    a=p.parse_args()
    if a.rerun and a.continuation: p.error('Select exactly one binding')
    if a.operation=='freeze': freeze()
    elif a.archive_root is None: p.error('--archive-root required')
    elif a.operation=='readback': readback(a.archive_root, a.row)
    elif a.operation=='repeat-check':
        matrix=load_matrix(rerun=True)
        repeat_check(a.archive_root, matrix, rerun_binding(matrix, a.archive_root))
    elif a.operation=='run': run_row(a.archive_root,a.row,a.continuation,a.rerun)
    else: report(a.archive_root,a.continuation,a.rerun)


if __name__=='__main__':
    main()

"""010 observations and exact numeric archives; no pickle/source execution.

v1 remains readable and strict. v2 commits source bytes before serialization,
checks mutation boundaries, and independently verifies payload and loaded bytes.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path

import numpy as np

from .grudeva2026_full_reference_010 import Case, Model, Settings, liquid_flux

CHUNK_BYTES = 4 * 1024**2
SCHEMA = 'grudeva-full-010-v2'


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(CHUNK_BYTES), b''):
            h.update(block)
    return h.hexdigest()


def numeric_chunks(value):
    """Bounded C-order stream, including transposes/strides; no full byte copy."""
    a = np.asarray(value)
    if a.dtype.kind not in 'fiu':
        raise ValueError('Only numeric float/integer arrays are supported')
    if a.flags.c_contiguous:
        if a.size:
            raw = memoryview(a.reshape(-1)).cast('B')
            for start in range(0, len(raw), CHUNK_BYTES):
                yield raw[start:start+CHUNK_BYTES]
    else:
        with np.nditer(a, flags=['external_loop', 'buffered', 'zerosize_ok'],
                       op_flags=['readonly'], order='C',
                       buffersize=max(1, CHUNK_BYTES//a.itemsize)) as iterator:
            for block in iterator:
                yield memoryview(np.ascontiguousarray(block)).cast('B')


def array_identity(value):
    a = np.asarray(value)
    h = hashlib.sha256()
    for block in numeric_chunks(a):
        h.update(block)
    return {'shape': list(a.shape), 'dtype': a.dtype.str, 'sha256': h.hexdigest()}


def finite(value):
    a = np.asarray(value)
    for block in numeric_chunks(a):
        if not np.isfinite(np.frombuffer(block, dtype=a.dtype)).all():
            return False
    return True


def stable_copy(value):
    """Commit before copy; ownership/contiguity alone never proves identity."""
    before = array_identity(value)
    snapshot = np.array(value, copy=True, order='C')
    if array_identity(snapshot) != before or array_identity(value) != before:
        raise ValueError('Source mutation during snapshot capture')
    snapshot.flags.writeable = False
    return snapshot


def write_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


class Trajectory:
    def __init__(self, model, segments):
        self.model, self.segments = model, segments

    def state(self, t):
        if t < 0 or t > self.segments[-1]['t'][-1]:
            raise ValueError('Time outside captured support')
        if t <= self.model.settings.startup:
            return self.model.startup(t)
        segment = self.segments[0] if t <= 1 else self.segments[-1]
        times = segment['t']
        if t < times[0] or t > times[-1]:
            raise ValueError('Missing required segment')
        k = np.searchsorted(times, t, side='left')
        if k < len(times) and times[k] == t:
            return segment['y'][:, k].copy()
        k = max(0, k-1)
        order = int(segment['order'][k])
        p = np.cumprod((t-segment['shift'][k, :order]) / segment['denom'][k, :order])
        return segment['D'][k, 0] + p @ segment['D'][k, 1:order+1]


def _dense_part_commitment(order, D, shift, denom):
    return json.dumps({'order': int(order), 'D': array_identity(D),
                       'shift': array_identity(shift), 'denom': array_identity(denom)},
                      sort_keys=True).encode()


def dense_chain(arrays):
    """Prospective source-piece commitments must match the completed target."""
    chain = hashlib.sha256()
    for j, order in enumerate(arrays['order']):
        order = int(order)
        if order < 1 or order > 5:
            raise ValueError('Invalid dense order')
        chain.update(_dense_part_commitment(order, arrays['D'][j, :order+1],
                                           arrays['shift'][j, :order], arrays['denom'][j, :order]))
        if (not _same_bits(arrays['D'][j, order+1:], np.zeros_like(arrays['D'][j, order+1:]))
                or not _same_bits(arrays['shift'][j, order:], np.ones_like(arrays['shift'][j, order:]))
                or not _same_bits(arrays['denom'][j, order:], np.ones_like(arrays['denom'][j, order:]))):
            raise ValueError('Dense padding changed from declared initialization')
    return chain.hexdigest()


def capture(model, results):
    segments = []
    for moving, result in results:
        # The solver still owns result arrays. Keep independent, checked snapshots.
        t, y = stable_copy(result.t), stable_copy(result.y)
        dense = result.sol.interpolants
        ns, nvar = len(dense), len(y)
        D = np.zeros((ns, 6, nvar))
        shift, denom = np.ones((ns, 5)), np.ones((ns, 5))
        order = np.empty(ns, dtype=np.int8)
        source_chain = hashlib.sha256()
        for j, part in enumerate(dense):
            order[j] = part.order
            source_chain.update(_dense_part_commitment(part.order, part.D, part.t_shift, part.denom))
            for source, target in [(part.D, D[j, :part.order+1]),
                                   (part.t_shift, shift[j, :part.order]),
                                   (part.denom, denom[j, :part.order])]:
                expected = array_identity(source)
                target[...] = source
                if array_identity(source) != expected or array_identity(target) != expected:
                    raise ValueError('Dense source mutation during capture')
        arrays = {'t': t, 'y': y, 'D': D, 'shift': shift, 'denom': denom, 'order': order}
        source_after = hashlib.sha256()
        for part in dense:
            source_after.update(_dense_part_commitment(part.order, part.D, part.t_shift, part.denom))
        if source_after.hexdigest() != source_chain.hexdigest() or dense_chain(arrays) != source_chain.hexdigest():
            raise ValueError('Dense source/target mutation after an earlier capture copy')
        identities = {k: array_identity(v) for k, v in arrays.items()}
        if identities['t'] != array_identity(result.t) or identities['y'] != array_identity(result.y):
            raise ValueError('Solver source mutated during dense capture')
        for value in arrays.values():
            value.flags.writeable = False
        segments.append({**arrays, 'moving': moving,
                         'capture_commitment': identities,
                         'dense_source_chain_sha256': source_chain.hexdigest(),
                         'success': bool(result.success), 'message': result.message,
                         'nfev': result.nfev, 'njev': result.njev, 'nlu': result.nlu})
    return Trajectory(model, segments)


def payload_identity(path):
    """Read NPY header and raw serialized bytes independently of NumPy loading."""
    with Path(path).open('rb') as stream:
        version = np.lib.format.read_magic(stream)
        if version == (1, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_1_0(stream)
        elif version == (2, 0):
            shape, fortran, dtype = np.lib.format.read_array_header_2_0(stream)
        else:
            raise ValueError('Unsupported numeric NPY header')
        if dtype.kind not in 'fiu' or fortran:
            raise ValueError('Unsafe dtype or non-C payload ordering')
        remaining = int(np.prod(shape, dtype=object))*dtype.itemsize
        h = hashlib.sha256()
        while remaining:
            block = stream.read(min(CHUNK_BYTES, remaining))
            if not block:
                raise ValueError('Incomplete numeric payload')
            h.update(block)
            remaining -= len(block)
        if stream.read(1):
            raise ValueError('Unexpected trailing payload')
    return {'shape': list(shape), 'dtype': dtype.str, 'sha256': h.hexdigest()}


def write_numeric(path, value, expected):
    """Serialize against a prospective source commitment, never a file-derived one."""
    if array_identity(value) != expected or not finite(value):
        raise ValueError('Source commitment mismatch or nonfinite source')
    # Capture snapshots already own read-only C buffers. Other callers get an
    # independent checked snapshot; ascontiguousarray alone would not suffice.
    a = value if (value.flags.owndata and value.flags.c_contiguous
                  and not value.flags.writeable) else stable_copy(value)
    with Path(path).open('xb') as stream:
        np.save(stream, a, allow_pickle=False)
        stream.flush()
        os.fsync(stream.fileno())
    if array_identity(value) != expected or array_identity(a) != expected:
        raise ValueError('Source mutation during serialization')
    raw = payload_identity(path)
    if raw != expected:
        raise ValueError('Serialized payload differs from source commitment')
    loaded = np.load(path, allow_pickle=False, mmap_mode='r')
    if array_identity(loaded) != expected or not finite(loaded):
        raise ValueError('Loaded payload differs from source commitment')
    return {'file': Path(path).name, 'sha256': sha256(path), 'array': expected,
            'order': 'C', 'pre_write_source': 'PASS', 'post_write_source': 'PASS',
            'serialized_payload': 'PASS', 'independently_loaded_payload': 'PASS'}


def _same_bits(a, b):
    return a.dtype == b.dtype and a.shape == b.shape and array_identity(a) == array_identity(b)


def _segment_shape_check(model, arrays):
    nt = len(arrays['t'])
    nv = model.n*model.width+2
    shapes = {'t': (nt,), 'y': (nv, nt), 'D': (nt-1, 6, nv),
              'shift': (nt-1, 5), 'denom': (nt-1, 5), 'order': (nt-1,),
              'concentrations': (nt, nv-2), 'boundary_accumulators': (nt, 2),
              'physical_z_faces': (nt, model.n+1), 'physical_z_centers': (nt, model.n)}
    if set(arrays) != set(shapes):
        raise ValueError('Archive array set mismatch')
    for key, shape in shapes.items():
        if arrays[key].shape != shape or arrays[key].dtype != np.dtype('i1' if key == 'order' else 'f8'):
            raise ValueError('Archive dtype or shape mismatch')
    if nt < 1 or not np.all(np.diff(arrays['t']) > 0) or not np.all((arrays['order'] >= 1) & (arrays['order'] <= 5)):
        raise ValueError('Invalid accepted-time or dense-order support')
    if np.any(arrays['denom'] <= 0):
        raise ValueError('Invalid dense denominators')


def _redundancy(model, arrays):
    _segment_shape_check(model, arrays)
    # Bounded, separately evaluated relationship checks. Includes sign of zero.
    for start in range(0, len(arrays['t']), 64):
        stop = start+64
        scale = np.minimum(arrays['t'][start:stop, None], 1.)
        want = arrays['y'][:-2, start:stop].T/scale
        if not _same_bits(want, arrays['concentrations'][start:stop]):
            raise ValueError('Redundant concentration disagreement')
        if not _same_bits(arrays['y'][-2:, start:stop].T, arrays['boundary_accumulators'][start:stop]):
            raise ValueError('Boundary accumulator disagreement')
        for key, coordinates in [('physical_z_faces', model.faces), ('physical_z_centers', model.xi)]:
            if not _same_bits(scale*coordinates, arrays[key][start:stop]):
                raise ValueError('Physical geometry disagreement')


def save_archive(directory, trajectory, metadata, complete=True):
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    model = trajectory.model
    write_json(directory/'WRITE_START.json', {'schema': SCHEMA, 'metadata': metadata})
    manifest = {'schema': SCHEMA, 'case': asdict(model.case),
                'settings': asdict(model.settings), 'metadata': metadata, 'segments': [],
                'geometry': {}, 'activation': 't_wet(z)=z; dry inactive; initial=1.388',
                'state_layout': 'y[:-2]=cell-major U=s*C amounts; last2=Jin,Jout; concentrations and accumulators stored separately',
                'transition': 't=1; identical end/start state; motion ends, discharge begins'}
    geometry = {'xi_faces': model.faces, 'xi': model.xi}
    for label, sphere in zip(('fines', 'boulders'), model.spheres):
        geometry.update({f'{label}_faces': sphere.faces, f'{label}_centers': sphere.r,
                         f'{label}_volumes': sphere.volume})
    groups = [('geometry', {}, {k: stable_copy(v) for k, v in geometry.items()})]
    for j, segment in enumerate(trajectory.segments):
        arrays = {k: v for k, v in segment.items() if isinstance(v, np.ndarray)}
        if dense_chain(arrays) != segment['dense_source_chain_sha256']:
            raise ValueError('Dense captured source chain mismatch')
        source = {k: array_identity(v) for k, v in arrays.items()}
        if source != segment.get('capture_commitment'):
            raise ValueError('Captured source commitment mismatch')
        nt, nv = len(segment['t']), len(segment['y'])
        concentrations = np.empty((nt, nv-2))
        for start in range(0, nt, 64):
            concentrations[start:start+64] = segment['y'][:-2, start:start+64].T/np.minimum(segment['t'][start:start+64, None], 1.)
        arrays.update(concentrations=concentrations,
                      boundary_accumulators=stable_copy(segment['y'][-2:].T),
                      physical_z_faces=np.minimum(segment['t'][:, None], 1.)*model.faces,
                      physical_z_centers=np.minimum(segment['t'][:, None], 1.)*model.xi)
        if source != {k: array_identity(arrays[k]) for k in source}:
            raise ValueError('Source mutation during derived-array construction')
        _redundancy(model, arrays)
        for a in arrays.values():
            a.flags.writeable = False
        groups.append((f'segment-{j}', {k: v for k, v in segment.items() if not isinstance(v, np.ndarray)}, arrays))
    for name, info, arrays in groups[1:]:
        if info['capture_commitment'] != {key: array_identity(arrays[key]) for key in info['capture_commitment']}:
            raise ValueError('Captured source changed before prospective write commitment')
    prospective = {name: {key: array_identity(a) for key, a in arrays.items()}
                   for name, _, arrays in groups}
    write_json(directory/'SOURCE_COMMITMENT.json', prospective)
    for name, info, arrays in groups:
        records = {key: write_numeric(directory/f'{name}-{key}.npy', a, prospective[name][key])
                   for key, a in arrays.items()}
        if prospective[name] != {key: array_identity(a) for key, a in arrays.items()}:
            raise ValueError('Source mutation across archive serialization')
        if name != 'geometry':
            _redundancy(model, arrays)
            # Reloaded relationships, not just the source-side construction.
            loaded = {key: np.load(directory/rec['file'], mmap_mode='r', allow_pickle=False)
                      for key, rec in records.items()}
            _redundancy(model, loaded)
            if dense_chain(loaded) != info['dense_source_chain_sha256']:
                raise ValueError('Serialized dense capture chain mismatch')
            manifest['segments'].append({**info, 'arrays': records})
        else:
            manifest['geometry'] = {'arrays': records}
    manifest['source_commitment_sha256'] = sha256(directory/'SOURCE_COMMITMENT.json')
    if complete:
        if any(not seg['success'] or len(seg['t']) < 2 for seg in trajectory.segments):
            raise ValueError('Incomplete solver trajectory cannot publish success')
        write_json(directory/'validated-manifest.pending.json', manifest)
        os.link(directory/'validated-manifest.pending.json', directory/'manifest.json')
    else:
        manifest['status'] = 'INCOMPLETE_SOLVER_TRAJECTORY_NOT_QUALIFIED'
        write_json(directory/'INCOMPLETE_MANIFEST.json', manifest)
    return manifest


def _load_v1(directory, manifest):
    model = Model(Settings(**manifest['settings']), Case(**manifest['case']))
    segments = []
    for record in [manifest['geometry'], *manifest['segments']]:
        name = record['file']
        if Path(name).name != name:
            raise ValueError('Unsafe archive path')
        path = directory/name
        if sha256(path) != record['sha256']:
            raise ValueError('Archive byte identity mismatch')
        with np.load(path, allow_pickle=False) as data:
            if set(data.files) != set(record['arrays']):
                raise ValueError('Archive array set mismatch')
            arrays = {}
            for key in data.files:
                a = data[key]
                if a.dtype.kind not in 'fiu' or array_identity(a) != record['arrays'][key]:
                    raise ValueError('Archive state identity mismatch')
                if not finite(a):
                    raise ValueError('Nonfinite archive state')
                arrays[key] = a
        if record is not manifest['geometry']:
            segments.append({**{k: v for k, v in record.items()
                                if k not in ('file', 'sha256', 'arrays')}, **arrays})
    return Trajectory(model, segments), manifest


def load_archive(directory):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['schema'] == 'grudeva-full-010-v1':
        return _load_v1(directory, manifest)
    if manifest['schema'] != SCHEMA:
        raise ValueError('Unknown archive schema')
    if sha256(directory/'SOURCE_COMMITMENT.json') != manifest['source_commitment_sha256']:
        raise ValueError('Source commitment identity mismatch')
    commitments = json.loads((directory/'SOURCE_COMMITMENT.json').read_text())
    model = Model(Settings(**manifest['settings']), Case(**manifest['case']))
    segments = []
    for j, record in enumerate([manifest['geometry'], *manifest['segments']]):
        name = 'geometry' if j == 0 else f'segment-{j-1}'
        arrays = {}
        if set(record['arrays']) != set(commitments[name]):
            raise ValueError('Archive array set mismatch')
        for key, rec in record['arrays'].items():
            if Path(rec['file']).name != rec['file']:
                raise ValueError('Unsafe archive path')
            path = directory/rec['file']
            expected = commitments[name][key]
            if rec['array'] != expected or rec['order'] != 'C' or sha256(path) != rec['sha256']:
                raise ValueError('Archive source/file identity mismatch')
            if payload_identity(path) != expected:
                raise ValueError('Archive payload identity mismatch')
            a = np.load(path, allow_pickle=False, mmap_mode='r')
            if array_identity(a) != expected or not finite(a):
                raise ValueError('Archive loaded state identity mismatch')
            arrays[key] = a
        if j:
            if not record['success'] or len(arrays['t']) < 2:
                raise ValueError('Incomplete solver archive')
            if dense_chain(arrays) != record['dense_source_chain_sha256']:
                raise ValueError('Loaded dense capture chain mismatch')
            if record['capture_commitment'] != {key: commitments[name][key] for key in record['capture_commitment']}:
                raise ValueError('Captured/source commitment chain mismatch')
            _redundancy(model, arrays)
            segments.append({**{k: v for k, v in record.items() if k != 'arrays'}, **arrays})
        else:
            expected_geometry = {'xi_faces': model.faces, 'xi': model.xi}
            for label, sphere in zip(('fines', 'boulders'), model.spheres):
                expected_geometry.update({f'{label}_faces': sphere.faces, f'{label}_centers': sphere.r,
                                          f'{label}_volumes': sphere.volume})
            if set(arrays) != set(expected_geometry) or any(not _same_bits(arrays[k], v) for k, v in expected_geometry.items()):
                raise ValueError('Archive radial/axial geometry mismatch')
    return Trajectory(model, segments), manifest


def fv_weights(faces, points, left_zero=False, right_neumann=False):
    """Quadratic exact cell-average reconstruction on the physical support."""
    faces, points = np.asarray(faces), np.asarray(points)
    n = len(faces)-1
    weights = np.zeros((len(points), n))
    for i, x in enumerate(points):
        cell = min(n-1, max(0, np.searchsorted(faces, x)-1))
        center = (faces[cell]+faces[cell+1])/2
        scale = faces[cell+1]-faces[cell]
        if left_zero and cell == 0:
            indices = np.array([0, 1])
            a, b = (faces[indices]-faces[0])/scale, (faces[indices+1]-faces[0])/scale
            mat = np.array([(a+b)/2, (a*a+a*b+b*b)/3]).T
            u = (x-faces[0])/scale
            weights[i, indices] = np.linalg.solve(mat.T, [u, u*u])
        elif right_neumann and cell == n-1:
            indices = np.array([n-2, n-1])
            a, b = (faces[indices]-faces[-1])/scale, (faces[indices+1]-faces[-1])/scale
            mat = np.array([np.ones(2), (a*a+a*b+b*b)/3]).T
            u = (x-faces[-1])/scale
            weights[i, indices] = np.linalg.solve(mat.T, [1., u*u])
        else:
            indices = np.arange(max(0, min(n-3, cell-1)), max(0, min(n-3, cell-1))+3)
            a, b = (faces[indices]-center)/scale, (faces[indices+1]-center)/scale
            mat = np.array([np.ones(3), (a+b)/2, (a*a+a*b+b*b)/3]).T
            u = (x-center)/scale
            weights[i, indices] = np.linalg.solve(mat.T, [1., u, u*u])
    return weights


def radial_weights(sphere, points):
    """Quadratic in r², fitted to exact spherical shell averages."""
    faces, centers = sphere.faces, sphere.r
    weights = np.zeros((len(points), len(centers)))
    for j, r in enumerate(points):
        cell = np.searchsorted(centers, r)
        ids = np.arange(max(0, min(len(centers)-3, cell-1)),
                        max(0, min(len(centers)-3, cell-1))+3)
        a, b = faces[ids], faces[ids+1]
        # Center the r² basis to avoid cancellation near r=1 on graded meshes.
        origin, scale = centers[ids[1]]**2, b[-1]**2-a[0]**2
        nodes, gw = np.polynomial.legendre.leggauss(4)
        qr = ((a+b)[:, None]+(b-a)[:, None]*nodes)/2
        measure = (b-a)[:, None]/2 * gw * qr**2 / sphere.volume[ids, None]
        ucell = (qr**2-origin)/scale
        mat = np.array([np.ones(3), np.sum(measure*ucell, axis=1),
                        np.sum(measure*ucell**2, axis=1)]).T
        u = (r*r-origin)/scale
        weights[j, ids] = np.linalg.solve(mat.T, [1., u, u*u])
    return weights


def observe(trajectory, support):
    model = trajectory.model
    times, z, r = map(np.asarray, (support['times'], support['z'], support['r']))
    liquid = np.full((len(times), len(z)), np.nan)
    means = np.empty((len(times), len(z), 2))
    radial = np.empty((len(times), len(z), 2, len(r)))
    inventory, integrals, boundary = [], [], []
    wet = np.zeros_like(liquid, dtype=bool)
    outlet = np.full(len(times), np.nan)
    rw = [radial_weights(sphere, r) for sphere in model.spheres]
    for it, t in enumerate(times):
        y = trajectory.state(float(t))
        s=min(t,1.)
        state=model.split(y,t) if t>0 else None
        available = (z <= s) & (t > 0)
        wet[it] = available
        means[it] = model.case.initial
        radial[it] = model.case.initial
        if s > 0:
            wl = fv_weights(s*model.faces, z[available], True, True)
            wg = fv_weights(s*model.faces, z[available])
            liquid[it, available] = wl @ state[:, 0]
            flux, cout = liquid_flux(state[:, 0], s, t < 1, model.case.D_l)
            if t >= 1:
                outlet[it] = cout  # right-hand discharge limit at t=1
            boundary.append([flux[0], cout if t >= 1 else 0., cout, flux[-1]])
            for i, (sphere, sl) in enumerate(zip(model.spheres, model.slices)):
                grains = wg @ state[:, sl]
                means[it, available, i] = sphere.mean(grains)
                radial[it, available, i] = grains @ rw[i].T
                _, surface = sphere.transfer(grains, liquid[it, available])
                radial[it, :, i, -1][available] = surface
            # Exact newly wetted grain trace, distinct from every positive age.
            born = available & (z == t) & (t <= 1)
            means[it, born] = model.case.initial
            radial[it, born] = model.case.initial
        else:
            boundary.append([0., 0., 0., 0.])
        inventory.append(model.inventories(float(t), y))
        integrals.append(y[-2:])
    return {'times': times, 'z': z, 'r': r, 'liquid': liquid, 'wet': wet,
            'grain_means': means, 'grain_radial': radial, 'outlet': outlet,
            'inventories': np.array(inventory), 'integrals': np.array(integrals),
            'boundary_flux': np.array(boundary)}


def independent_inventories(model, t, y):
    """Independent Gaussian quadrature of actual piecewise-constant FV states."""
    if t==0:
        return np.array([0.,0.,0.,model.case.M0])
    state, s = model.split(y,t), min(t, 1.)
    x, w = np.polynomial.legendre.leggauss(2)
    axial_weight = np.diff(s * model.faces)
    amounts = [float(np.sum(axial_weight.astype(np.longdouble)*state[:, 0]))]
    for weight, sphere, sl in zip(model.case.weights, model.spheres, model.slices):
        a, b = sphere.faces[:-1], sphere.faces[1:]
        radii = ((a+b)[:, None]+(b-a)[:, None]*x)/2
        radial_weight = np.sum((b-a)[:, None]/2*w*radii**2, axis=1)*3
        total = np.sum(axial_weight.astype(np.longdouble)[:, None] *
                       state[:, sl] * radial_weight[None, :])
        amounts.append(float(weight * total))
    return np.r_[amounts, (1-s)*model.case.M0]


def boundary_quadrature(trajectory, order):
    x, w = np.polynomial.legendre.leggauss(order)
    model = trajectory.model
    tau=model.settings.startup
    initial=np.zeros(2)
    for point,weight in zip(tau*(x+1)/2,w):
        state=model.split(model.startup(point),point)
        initial[0]+=tau*weight/2*liquid_flux(state[:,0],point,True,model.case.D_l)[0][0]
    values = [initial.copy()]
    times = [model.settings.startup]
    total = initial.copy()
    for seg in trajectory.segments:
        for a, b in zip(seg['t'][:-1], seg['t'][1:]):
            value = np.zeros(2)
            for point, weight in zip((a+b)/2+(b-a)*x/2, w):
                state = model.split(trajectory.state(float(point)),point)
                s = point if seg['moving'] else 1.
                flux, cout = liquid_flux(state[:, 0], s, seg['moving'], model.case.D_l)
                value += weight * np.array([flux[0], 0 if seg['moving'] else cout])
            total += (b-a)/2*value
            values.append(total.copy())
            times.append(b)
    return np.array(times), np.array(values)

"""Non-invasive observations and safe, integrity-checked 010 trajectory archives.

Only NumPy numeric arrays and JSON are loaded. No Python/pickle deserialization.
BDF dense coefficients preserve solver state; evaluation has a scale-aware budget.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np

from .grudeva2026_full_reference_010 import Case, Model, Settings, liquid_flux


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def array_identity(value):
    a = np.ascontiguousarray(value)
    return {'shape': list(a.shape), 'dtype': a.dtype.str,
            'sha256': hashlib.sha256(a.tobytes()).hexdigest()}


def write_json(path, value):
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')


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


def capture(model, results):
    segments = []
    for moving, result in results:
        dense = result.sol.interpolants
        ns, nvar = len(dense), len(result.y)
        D = np.zeros((ns, 6, nvar))
        shift, denom = np.ones((ns, 5)), np.ones((ns, 5))
        order = np.empty(ns, dtype=np.int8)
        for j, part in enumerate(dense):
            order[j] = part.order
            D[j, :part.order+1] = part.D
            shift[j, :part.order] = part.t_shift
            denom[j, :part.order] = part.denom
        segments.append({'moving': moving, 't': result.t.copy(), 'y': result.y.copy(),
                         'D': D, 'shift': shift, 'denom': denom, 'order': order,
                         'success': bool(result.success), 'message': result.message,
                         'nfev': result.nfev, 'njev': result.njev, 'nlu': result.nlu})
    return Trajectory(model, segments)


def save_archive(directory, trajectory, metadata):
    directory = Path(directory)
    directory.mkdir(exist_ok=False)
    model = trajectory.model
    manifest = {'schema': 'grudeva-full-010-v1', 'case': asdict(model.case),
                'settings': asdict(model.settings), 'metadata': metadata, 'segments': [],
                'geometry': {}, 'activation': 't_wet(z)=z; dry inactive; initial=1.388',
                'state_layout': 'y[:-2]=cell-major U=s*C amounts; last2=Jin,Jout; concentrations stored separately',
                'transition': 't=1; identical end/start state; motion ends, discharge begins'}
    geometry = {'xi_faces': model.faces, 'xi': model.xi}
    for label, sphere in zip(('fines', 'boulders'), model.spheres):
        geometry[f'{label}_faces'] = sphere.faces
        geometry[f'{label}_centers'] = sphere.r
        geometry[f'{label}_volumes'] = sphere.volume
    np.savez_compressed(directory/'geometry.npz', **geometry)
    manifest['geometry'] = {'file': 'geometry.npz', 'sha256': sha256(directory/'geometry.npz'),
                            'arrays': {k: array_identity(v) for k, v in geometry.items()}}
    for j, segment in enumerate(trajectory.segments):
        arrays = {k: v for k, v in segment.items() if isinstance(v, np.ndarray)}
        arrays['concentrations'] = segment['y'][:-2].T/np.minimum(segment['t'][:,None],1.)
        arrays['physical_z_faces'] = np.minimum(segment['t'][:, None], 1.) * model.faces
        arrays['physical_z_centers'] = np.minimum(segment['t'][:, None], 1.) * model.xi
        name = f'segment-{j}.npz'
        np.savez_compressed(directory/name, **arrays)
        record = {k: v for k, v in segment.items() if not isinstance(v, np.ndarray)}
        record.update(file=name, sha256=sha256(directory/name),
                      arrays={k: array_identity(v) for k, v in arrays.items()})
        manifest['segments'].append(record)
    write_json(directory/'manifest.json', manifest)
    return manifest


def load_archive(directory):
    directory = Path(directory)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest['schema'] != 'grudeva-full-010-v1':
        raise ValueError('Unknown archive schema')
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
                if not np.all(np.isfinite(a)):
                    raise ValueError('Nonfinite archive state')
                arrays[key] = a
        if record is not manifest['geometry']:
            segments.append({**{k: v for k, v in record.items()
                                if k not in ('file', 'sha256', 'arrays')}, **arrays})
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

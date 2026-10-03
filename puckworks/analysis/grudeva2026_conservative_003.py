"""Analysis-only conservative successor to Grudeva reference 002.

The radial shell operator retains Yoana Grudeva's permissioned reference-port
lineage; see docs/permissions/grudeva2025.md and THIRD_PARTY_NOTICES.md.
This modified computation is not an untouched author run. Article mathematics:
Grudeva, Moroney & Foster, DOI 10.1017/S095679252500018X (CC-BY-4.0).
No production numerical helper is used. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from scipy.linalg import eigh_tridiagonal, solve_banded
from scipy.optimize import brentq
from scipy.sparse import coo_matrix

from .grudeva2026_reference_002 import shell_operator

INITIAL, BETA, DELTA, CAPACITY = 1.388, 3.2, .8, 4.2
JUMP = 1+BETA*INITIAL
M0 = (BETA+DELTA)*INITIAL
EPS = np.finfo(float).eps
ALGEBRA_RTOL = 256*EPS


@dataclass(frozen=True)
class Controls:
    bed: int = 128
    shells: int = 3200
    dt: float = .001
    horizon: float = .4
    diffusivity: float = 1.

    def __post_init__(self):
        for v in (self.bed, self.shells):
            if isinstance(v, bool) or not isinstance(v, int) or v < 4:
                raise ValueError('bed/shells must be integers >=4')
        if not all(np.isfinite(v) for v in (self.dt, self.horizon, self.diffusivity)):
            raise ValueError('finite controls required')
        if min(self.dt, self.horizon) <= 0 or self.horizon > 8 or self.diffusivity < 0:
            raise ValueError('positive time, horizon<=8 and nonnegative D required')


def overlap(receiver, donor):
    """Physical overlap lengths; uncovered, reversed or empty support is rejected."""
    r, d = np.asarray(receiver, float), np.asarray(donor, float)
    for f in (r, d):
        if f.ndim != 1 or len(f) < 2 or not np.all(np.isfinite(f)) or np.any(np.diff(f) <= 0):
            raise ValueError('strictly increasing finite faces required')
    if r[0] != d[0] or r[-1] != d[-1]:
        raise ValueError('supports must coincide; no endpoint extension')
    rows, cols, values = [], [], []
    i = j = 0
    while i < len(r)-1 and j < len(d)-1:
        length = min(r[i+1], d[j+1])-max(r[i], d[j])
        if length > 0:
            rows.append(i); cols.append(j); values.append(length)
        right_r, right_d = r[i+1], d[j+1]
        i += right_r <= right_d
        j += right_d <= right_r
    return coo_matrix((values, (rows, cols)), shape=(len(r)-1, len(d)-1)).tocsr()


def amount_map(receiver, donor):
    """Map paired AMOUNTS, T=O diag(v_d)^-1; no global normalization."""
    return overlap(receiver, donor).multiply(1/np.diff(donor)).tocsr()


def transfer_amounts(amounts, receiver, donor):
    return np.asarray(amount_map(receiver, donor) @ amounts)


def cut_transfer(amounts, faces):
    """Coincident support, allowing the zero-volume endpoint of a front bracket."""
    positive = np.diff(faces) > 0
    if not np.all(positive):
        if np.any(np.asarray(amounts)[~positive] != 0):
            raise ValueError('a zero-volume cell cannot transfer an amount')
        result = np.zeros_like(amounts)
        if np.any(positive):
            physical_faces = faces[:sum(positive)+1]
            result[positive] = transfer_amounts(np.asarray(amounts)[positive], physical_faces, physical_faces)
        return result
    return transfer_amounts(amounts, faces, faces)


def old_counterexample():
    z = np.linspace(0., 1., 128)
    s, h, delta, qb = .002, .001, .8, 1/2.4
    count = int(np.searchsorted(z, s, side='right'))
    mapped = np.interp(z*s, z[:count], np.array([.1])/(3*qb*h))
    return {'count': count, 'mapped_source_integral': float(h*s*np.trapezoid(mapped, z)),
            'old_nodal_observed_donation': float(delta*np.trapezoid([.1, 0.], [0., s])),
            'scope': 'algebra only; not actual liquid-state change or canonical trajectory'}


class Radial:
    """Exact interval integration of ALL degrees of the radial FV shell matrix.

    j contains physical-z INTEGRALS of transformed shell states. The transform
    is a numerical eigendecomposition, not the production spherical series.
    """
    def __init__(self, shells, diffusivity=1.):
        self.op = shell_operator(shells, diffusivity)
        w, lower, diag, upper, _, _ = self.op
        self.w = w
        if diffusivity == 0:
            self.rates = np.zeros(shells)
            self.q = np.eye(shells)
            self.p = np.sqrt(w)
        else:
            eig, self.q = eigh_tridiagonal(-diag, -np.sqrt(lower*upper))
            if np.min(eig) <= 0:
                raise ArithmeticError('nonpositive radial diffusion rate')
            self.rates = eig
            self.p = self.q.T @ np.sqrt(w)
        self.weights = self.p**2
        self.weight_defect = float(abs(sum(self.weights)-1))
        if self.weight_defect > ALGEBRA_RTOL*shells:
            raise ArithmeticError('radial transform does not preserve constant inventory')

    def factors(self, h):
        if not np.isfinite(h) or h <= 0:
            raise ValueError('positive interval required')
        x = h*self.rates
        e = np.exp(-x)
        f1, f2 = np.empty_like(x), np.empty_like(x)
        small = abs(x) < .01
        y = x[small]
        f1[small] = 1-y/2+y*y/6-y**3/24+y**4/120-y**5/720+y**6/5040
        f2[small] = .5-y/6+y*y/24-y**3/120+y**4/720-y**5/5040+y**6/40320
        f1[~small] = -np.expm1(-x[~small])/x[~small]
        f2[~small] = (1-f1[~small])/x[~small]
        return e, f1, f2

    def affine(self, j0, c0, v0, dv, h):
        """Return base, coefficient so actual j1=base+coefficient*C1."""
        e, f1, f2 = self.factors(h)
        base = (e[:, None]*j0 + (f1-e)[:, None]*(v0*c0)
                + (INITIAL*f1)[:, None]*dv + (2*f2-f1)[:, None]*(dv*c0))
        coefficient = (1-f1)[:, None]*v0+(1-2*f2)[:, None]*dv
        return base, coefficient

    def advance(self, j0, c0, c1, v0, dv, h):
        base, coefficient = self.affine(j0, c0, v0, dv, h)
        return base+coefficient*c1

    def shells(self, j):
        return (self.q @ (self.p[:, None]*np.atleast_2d(j).reshape(len(self.w), -1)))/np.sqrt(self.w)[:, None]

    def means(self, j):
        return self.weights @ j

    def flux(self, j, boundary, qb=1/2.4):
        # Equality to surface conductance verified independently in shell coordinates.
        return (self.weights*self.rates) @ (j-np.asarray(boundary))/(3*qb)


def coupled_exchange(radial, grains, liquid, donor_faces, receiver_faces, h):
    """Actual implicit paired update on fixed support, including nonmatching grids.

    The moving solver uses the same affine radial response and amount transfer;
    coincident cut cells make this coupling diagonal there.
    """
    vd, vr = np.diff(donor_faces), np.diff(receiver_faces)
    o = overlap(receiver_faces, donor_faces)
    q = o.T.multiply((1/vd)[:, None]).tocsr()
    t = amount_map(receiver_faces, donor_faces)
    c0 = np.asarray(q @ liquid)
    base, coeff = radial.affine(grains, c0, vd, np.zeros_like(vd), h)
    loss0 = DELTA*radial.means(grains-base)
    response = DELTA*radial.means(coeff)
    matrix = np.diag(CAPACITY*vr)+(t.multiply(response) @ q).toarray()
    rhs = CAPACITY*vr*liquid + t @ loss0
    c1 = np.linalg.solve(matrix, rhs)
    j1 = base+coeff*np.asarray(q @ c1)
    gain = transfer_amounts(DELTA*radial.means(grains-j1), receiver_faces, donor_faces)
    residual = CAPACITY*vr*(c1-liquid)-gain
    return c1, j1, {'amount_residual': float(max(abs(residual))),
                    'linear_residual': float(max(abs(matrix @ c1-rhs))),
                    'scale': float(np.sum(abs(CAPACITY*vr*liquid))+np.sum(abs(gain)))}


def face_coefficients(faces):
    """Linear upwind cell-average trace; first cell uses the zero inlet."""
    v = np.diff(faces)
    center = (faces[:-1]+faces[1:])/2
    alpha = np.ones(len(v))
    alpha[0] = 2.
    if len(v) > 1:
        alpha[1:] += .5*v[1:]/np.diff(center)
    return alpha, 1-alpha


def face_values(c, faces, inlet=0.):
    alpha, beta = face_coefficients(faces)
    return np.r_[inlet, alpha*c+beta*np.r_[inlet, c[:-1]]]


def transport_solve(c0, old_faces, new_faces, h, loss0, response, *, inlet=0.):
    """Reynolds balance with paired grain AMOUNTS and common face traces."""
    v0, v1 = np.diff(old_faces), np.diff(new_faces)
    a, b = face_coefficients(new_faces)
    old_trace = face_values(c0, old_faces, inlet)
    if v0[-1] == 0:  # zero-volume newly cut cell carries the preceding front trace
        old_trace[-1] = c0[-1]
    factor = h-CAPACITY*(new_faces-old_faces)
    diagonal = CAPACITY*v1+response+.5*factor[1:]*a
    low1 = .5*(factor[2:]*b[1:]-factor[1:-1]*a[:-1])
    low2 = -.5*factor[2:-1]*b[1:-1]
    band = np.zeros((3, len(c0)))
    band[0] = diagonal
    band[1, :-1] = low1
    band[2, :-2] = low2
    rhs = CAPACITY*v0*c0+loss0-.5*np.diff(factor*old_trace)
    boundary_part = np.zeros(len(c0)+1)
    boundary_part[0], boundary_part[1] = inlet, b[0]*inlet
    rhs -= .5*np.diff(factor*boundary_part)
    c1 = solve_banded((2, 0), band, rhs, check_finite=False)
    new_trace = face_values(c1, new_faces, inlet)
    face_amount = factor*(old_trace+new_trace)/2
    solve_error = CAPACITY*(v1*c1-v0*c0)+np.diff(face_amount)-loss0+response*c1
    return c1, face_amount, .5*(old_trace[-1]+new_trace[-1]), float(max(abs(solve_error)))


def step(radial, c0, j0, old_faces, h, *, fixed=False, displacement=None, materialize=True):
    """One ACTUAL coupled step; front and transport share the same trace/time rule."""
    v0 = np.diff(old_faces)
    zeros = np.zeros(len(v0))
    e, f1, f2 = radial.factors(h)
    birth = INITIAL*f1+(2*f2-f1)*c0[-1]
    birth_coefficient = 1-2*f2
    old_b = radial.means(j0)
    base_mean = (radial.weights*e) @ j0 + float(radial.weights @ (f1-e))*(v0*c0)
    coeff_mean = float(radial.weights @ (1-f1))*v0
    birth_mean = float(radial.weights @ birth)
    birth_response = float(radial.weights @ birth_coefficient)

    def solve(ds):
        faces = old_faces.copy()
        faces[-1] += ds
        loss = DELTA*(old_b-base_mean)
        response = DELTA*coeff_mean.copy()
        loss[-1] += DELTA*ds*(INITIAL-birth_mean)
        response[-1] += DELTA*ds*birth_response
        # Coincident physical supports: the same paired amount map as the
        # nonmatching exchange fixture, used in the actual linear RHS.
        loss = cut_transfer(loss, faces)
        response = cut_transfer(response, faces)
        c1, flux, cf, linear = transport_solve(c0, old_faces, faces, h, loss, response)
        return c1, flux, cf, linear

    if fixed:
        ds = 0.
    elif displacement is not None:
        ds = displacement
    else:
        # At zero volume the ds=0 endpoint is only a root bracket. Its limit
        # has no exchange or stored liquid, Cf=0, so jump residual is h.
        def equation(ds):
            if old_faces[-1] == 0 and ds == 0:
                return h
            cf = solve(ds)[2]
            return h*(1-cf)-ds*(JUMP-CAPACITY*cf)
        # At ds=h/a the jump residual is h*(1-JUMP/a)<0, independently
        # of Cf. Unlike h/JUMP this remains a strict bracket for roundoff-
        # sized negative C in the exact D=0 limit. No concentration projection.
        ds = brentq(equation, 0., h/CAPACITY, xtol=np.nextafter(0., 1.), rtol=4*EPS)
    c1, flux, cf, linear = solve(ds)
    jump = 0. if fixed else h*(1-cf)-ds*(JUMP-CAPACITY*cf)
    if not materialize:
        return None, None, None, {'front_residual': float(jump)}
    j1 = e[:, None]*j0
    j1 += (f1-e)[:, None]*(v0*c0)
    j1 += (1-f1)[:, None]*(v0*c1)
    j1[:, -1] += ds*(birth+birth_coefficient*c1[-1])
    faces = old_faces.copy(); faces[-1] += ds
    donated = DELTA*(old_b+INITIAL*np.r_[zeros[:-1], ds]-radial.means(j1))
    gain = transfer_amounts(donated, faces, faces)
    balance = CAPACITY*(np.diff(faces)*c1-v0*c0)+np.diff(flux)-gain
    scale = float(np.sum(abs(CAPACITY*v0*c0))+np.sum(abs(CAPACITY*np.diff(faces)*c1))
                  +np.sum(abs(flux))+np.sum(abs(gain))
                  +DELTA*(sum(abs(old_b))+INITIAL*abs(ds)+sum(abs(radial.means(j1)))))
    return c1, j1, faces, {'front_trace': cf, 'front_residual': float(jump),
                          'linear_residual': linear, 'transfer_residual': float(max(abs(balance))),
                          'algebra_scale': scale, 'face_amount': flux.tolist()}


def observation_support(horizon):
    fixture = json.loads((Path(__file__).parents[1]/'data/grudeva2026/publication_reference.json').read_text())
    times = {0., .01, .05, .1, .2, .4, .8, 1., 1.01, 2., 3.2, 4.8, 6.4, 8., horizon}
    times.update(row['t'] for row in fixture['figure4'])
    times.update(np.round(np.arange(0., horizon, .025), 12))
    times.update(np.round(np.arange(6.3, 6.7001, .005), 12))
    z = set(np.round(np.arange(0., 1.0001, .005), 12))
    z.update(row['z'] for row in fixture['figure3'])
    return np.array(sorted(t for t in times if t <= horizon)), np.array(sorted(z))


def phase_integrals(t, s, faces, liquid, grain_integrals):
    ic = float(np.diff(faces) @ liquid)
    ib = float(sum(grain_integrals))
    return np.array([ic+min(t, 1.)-s, BETA*(ic+INITIAL*(1-s)),
                     DELTA*(ib+INITIAL*(1-s))])


def point_liquid(point, faces, values):
    """Cell-local linear reconstruction at a supported physical coordinate."""
    if not faces[0] <= point <= faces[-1] or faces[-1] == faces[0]:
        raise ValueError('point outside positive active support')
    k = min(int(np.searchsorted(faces, point, side='right')-1), len(values)-1)
    center = (faces[:-1]+faces[1:])/2
    slope = values[0]/center[0] if k == 0 else (values[k]-values[k-1])/(center[k]-center[k-1])
    return float(values[k]+slope*(point-center[k]))


def run(ctrl=Controls()):
    """Execute this one backend; a single execution never claims qualification."""
    started = time.perf_counter()
    radial = Radial(ctrl.shells, ctrl.diffusivity)
    grid = np.linspace(0., 1., ctrl.bed+1)
    times, z = observation_support(ctrl.horizon)
    history_z = np.array([.025, .1, .25, .5, .75, .9, 1.])
    activation = np.full(len(z), np.nan)
    activation[z == 0] = 0.
    history_activation = np.full(len(history_z), np.nan)
    histories = np.full((ctrl.shells, len(history_z)), INITIAL)
    faces = np.array([0., 0.])
    c = np.zeros(1)
    j = np.zeros((ctrl.shells, 1))
    t = cup = 0.
    arrival = None
    sample = 1
    records, observations, accepted, events = [], [], [], []
    max_global = max_transfer = max_jump = max_linear = 0.
    min_c = max_c = 0.
    min_grain = INITIAL
    shell_integral_error = 0.
    status, reason = 'EXECUTED_UNQUALIFIED', None

    def save(event=None):
        nonlocal shell_integral_error
        s = faces[-1]
        means = radial.means(j)
        phases = phase_integrals(t, s, faces, c, means)
        trace = face_values(c, faces)[-1] if s > 0 else 0.
        outlet = 0. if t < 1 else (1. if arrival is None else trace)
        records.append([t, s, outlet, cup, *phases, (sum(phases)+cup-M0)/M0])
        # Independent radial integral from reconstructed shell states, with
        # independent spatial sum performed BEFORE the radial transform.
        reconstructed = radial.shells(np.sum(j, axis=1)[:, None])[:, 0]
        error = abs(float(radial.w @ reconstructed)-float(sum(means)))
        shell_integral_error = max(shell_integral_error, error)
        centers = .5*(faces[:-1]+faces[1:])
        liquid = np.where(z <= min(t, 1.), 1., 0.)
        b = np.full(len(z), INITIAL)
        active = z < s
        if s > 0:
            liquid[active] = np.interp(z[active], np.r_[0., centers, s], np.r_[0., c, trace])
            b0 = INITIAL*float(radial.weights @ np.exp(-radial.rates*t))
            bfront = INITIAL if arrival is None else float(radial.means(histories)[-1])
            b[active] = np.interp(z[active], np.r_[0., centers, s],
                                   np.r_[b0, means/np.diff(faces), bfront])
        liquid[z == 0] = 0.
        if arrival is not None:
            liquid[z == 1] = trace
            b[z == 1] = radial.means(histories)[-1]
        observations.append({'t': t, 'event': event, 'faces': faces.tolist(),
                             'liquid_cells': c.tolist(), 'grain_integrals': means.tolist(),
                             'liquid_profile': liquid.tolist(), 'grain_profile': b.tolist(),
                             'grain_history': radial.means(histories).tolist()})

    save('initial')
    while sample < len(times):
        if time.perf_counter()-started > 895:
            status, reason = 'RESOURCE_LIMIT', 'per-run time ceiling'; break
        target = float(times[sample])
        h = min(ctrl.dt, target-t)
        if t < 1 < t+h:
            h = 1-t
        old_s = faces[-1]
        old_c = c.copy()
        old_faces = faces.copy()
        crossing = False
        try:
            next_state = step(radial, c, j, faces, h, fixed=arrival is not None)
            if arrival is None and next_state[2][-1] >= grid[len(c)]:
                distance = grid[len(c)]-old_s
                def event_equation(duration):
                    trial = step(radial, c, j, faces, duration, displacement=distance, materialize=False)
                    return trial[3]['front_residual']
                h = brentq(event_equation, max(distance*JUMP*.5, np.nextafter(0., 1.)), h,
                           xtol=np.nextafter(0., 1.), rtol=4*EPS)
                next_state = step(radial, c, j, faces, h, displacement=distance)
                crossing = True
            c, j, faces, diagnostic = next_state
        except (ValueError, ArithmeticError, np.linalg.LinAlgError) as exc:
            status, reason = 'NUMERICAL_FAILURE', str(exc); break
        new_t = target if t+h >= target else t+h
        new_s = faces[-1]
        ds = new_s-old_s
        if new_s > min(new_t, 1.)+1e-10:
            status, reason = 'UNSUPPORTED_REGIME', 'desaturation overtook wetting'; break
        active = (z > old_s) & (z <= new_s)
        if ds > 0:
            activation[active] = t+h*(z[active]-old_s)/ds
        # Point observers retain their own fixed-z activation and history.
        for k, point in enumerate(history_z):
            if point > new_s:
                continue
            age = h
            fraction = 0.
            if np.isnan(history_activation[k]):
                fraction = (point-old_s)/ds if ds > 0 else 0.
                history_activation[k] = t+h*fraction
                age = h*(1-fraction)
            if age > 0:
                boundary1 = point_liquid(point, faces, c)
                if fraction > 0 or point > old_s:
                    old_front = face_values(old_c, old_faces)[-1] if old_s > 0 else 0.
                    new_front = face_values(c, faces)[-1]
                    boundary0 = old_front+fraction*(new_front-old_front)
                else:
                    boundary0 = point_liquid(point, old_faces, old_c)
                histories[:, k:k+1] = radial.advance(histories[:, k:k+1], np.array([boundary0]),
                    np.array([boundary1]), np.ones(1), np.zeros(1), age)
        if t >= 1:
            cup += h if arrival is None else diagnostic['face_amount'][-1]
        t = new_t
        if crossing and len(c) == ctrl.bed:
            arrival = t
            events.append({'t': t, 'kind': 'desaturation_exit', 'outlet_left': 1.,
                           'outlet_right': float(face_values(c, faces)[-1]),
                           'phase_state_continuity': 'same actual state on both sides'})
        if t == 1:
            events.append({'t': t, 'kind': 'first_drip', 'outlet_left': 0., 'outlet_right': 1.,
                           'phase_state_continuity': 'same actual state on both sides'})
        phases = phase_integrals(t, new_s, faces, c, radial.means(j))
        residual = float((sum(phases)+cup-M0)/M0)
        max_global = max(max_global, abs(residual))
        max_transfer = max(max_transfer, diagnostic['transfer_residual'])
        max_jump = max(max_jump, abs(diagnostic['front_residual']))
        max_linear = max(max_linear, diagnostic['linear_residual'])
        min_c = min(min_c, float(min(c)), float(face_values(c, faces).min()))
        max_c = max(max_c, float(max(c)), float(face_values(c, faces).max()))
        min_grain = min(min_grain, float(np.min(radial.means(j)/np.diff(faces))))
        accepted.append([t, new_s, cup, *phases, residual, diagnostic['transfer_residual'],
                         diagnostic['front_residual'], diagnostic['linear_residual'], diagnostic['algebra_scale'],
                         float(face_values(c, faces)[-1])])
        reached = t == target
        if reached or crossing:
            save('exit' if arrival == t else ('cell_crossing' if crossing else ('first_drip' if t == 1 else None)))
        if reached:
            sample += 1
        if min_c < -1e-8 or max_c > 1+1e-8 or min_grain < -1e-8 or min(phases) < -1e-8:
            status, reason = 'NUMERICAL_BOUNDS_FAILED', 'accepted state or trace outside budget'; break
        if crossing and arrival is None:
            front_c = face_values(c, faces)[-1]
            faces = np.r_[faces, faces[-1]]
            c = np.r_[c, front_c]
            j = np.c_[j, np.zeros(ctrl.shells)]
    return {'controls': asdict(ctrl), 'status': status, 'reason': reason,
            'arrival': arrival, 'records': records, 'observations': observations, 'accepted': accepted, 'events': events,
            'record_columns': ['t', 's', 'outlet', 'cup', 'liquid', 'fines', 'boulders', 'residual'],
            'accepted_columns': ['t', 's', 'cup', 'liquid', 'fines', 'boulders', 'residual',
                                 'transfer_residual', 'front_residual', 'linear_residual', 'algebra_scale', 'front_trace'],
            'z': z.tolist(), 'grain_history_z': history_z.tolist(),
            'activation': [None if np.isnan(x) else float(x) for x in activation],
            'grain_history_activation': [None if np.isnan(x) else float(x) for x in history_activation],
            'max_normalized_conservation_residual': max_global,
            'max_transfer_residual': max_transfer, 'max_front_residual': max_jump,
            'max_linear_residual': max_linear, 'aqueous_min': min_c, 'aqueous_max': max_c,
            'grain_mean_min': min_grain, 'radial_weight_defect': radial.weight_defect,
            'independent_shell_integral_error': shell_integral_error,
            'seconds': time.perf_counter()-started, 'qualified': False,
            'physical_validation': 'NOT_ESTABLISHED'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, required=True)
    for name, value in asdict(Controls()).items():
        ap.add_argument('--'+name, type=type(value), default=value)
    args = ap.parse_args(argv)
    result = run(Controls(**{k: getattr(args, k) for k in asdict(Controls())}))
    result['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['radial_source_sha256'] = hashlib.sha256(Path(__file__).with_name('grudeva2026_reference_002.py').read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, allow_nan=False, separators=(',', ':'))+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'reason', 'arrival', 'seconds',
                                            'max_normalized_conservation_residual')}))
    return 2  # execution is never numerical qualification


if __name__ == '__main__':
    raise SystemExit(main())

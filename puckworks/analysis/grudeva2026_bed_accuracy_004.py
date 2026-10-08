"""Analysis-only 004: conservative square-root bed reconstruction.

Reuses unchanged 003 radial, signed-amount and inventory helpers and the 002
permission-attributed Grudeva radial operator. See THIRD_PARTY_NOTICES.md.
Modified reference lineage, not an untouched author execution. Mathematics:
Grudeva, Moroney & Foster, DOI 10.1017/S095679252500018X (CC-BY-4.0).
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No production numerical internals.
"""
from __future__ import annotations
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from scipy.linalg import solve_banded
from scipy.optimize import brentq
from .grudeva2026_conservative_003 import (
    Controls, Radial, INITIAL, DELTA, CAPACITY, JUMP, M0, EPS,
    cut_transfer, transfer_amounts, observation_support,
    phase_integrals,
)


def root_means(faces, anchor):
    """Exact mean of sqrt(anchor-z), including zero-volume limit."""
    if not np.isfinite(anchor) or anchor < faces[-1]:
        raise ValueError('reconstruction anchor outside physical support')
    u=np.sqrt(np.maximum(anchor-faces[:-1], 0.))
    v=np.sqrt(np.maximum(anchor-faces[1:], 0.))
    return np.divide(2*(u*u+u*v+v*v),3*(u+v),out=np.zeros_like(u),where=u+v>0)


def weights(x, p, target, value):
    """Three integral constraints, expressed in divided differences."""
    ratio=(x[0]-x[2])/(x[1]-x[2])
    w0=((value-p[2])-(p[1]-p[2])*(target-x[2])/(x[1]-x[2]))/(p[0]-p[2]-(p[1]-p[2])*ratio)
    w1=(target-x[2]-w0*(x[0]-x[2]))/(x[1]-x[2])
    return np.array([w0,w1,1-w0-w1])


def reconstruction(faces, anchor=None):
    """Rows for right face traces, columns current/previous/twice previous.

    Inlet supplies a point constraint for the two-cell closure. One active cell
    uses its exact inlet and linear mean. No state limiter or concentration cap.
    """
    if anchor is None: anchor=faces[-1]
    x=(faces[:-1]+faces[1:])/2
    p=root_means(faces,anchor)
    n=len(x);co=np.zeros((3,n));boundary=np.zeros(n);first_upper=0.
    co[0,0]=2.;boundary[0]=-1.
    if n>1:
        first=weights(np.array([0.,x[0],x[1]]),np.array([np.sqrt(anchor),p[0],p[1]]),faces[1],np.sqrt(max(anchor-faces[1],0.)))
        boundary[0],co[0,0],first_upper=first
        w=weights(np.array([0.,x[0],x[1]]),np.array([np.sqrt(anchor),p[0],p[1]]),faces[2],np.sqrt(max(anchor-faces[2],0.)))
        boundary[1],co[1,1],co[0,1]=w
    if n>2:
        w=weights(np.array([x[:-2],x[1:-1],x[2:]]),np.array([p[:-2],p[1:-1],p[2:]]),faces[3:],np.sqrt(np.maximum(anchor-faces[3:],0.)))
        co[:,2:]=w[::-1]
    return co,boundary,first_upper


def face_values(c, faces, inlet=0., anchor=None):
    co,boundary,first_upper=reconstruction(faces,anchor)
    trace=co[0]*c+boundary*inlet
    trace[1:]+=co[1,1:]*c[:-1]
    trace[2:]+=co[2,2:]*c[:-2]
    if len(c)>1: trace[0]+=first_upper*c[1]
    return np.r_[inlet,trace]


def point_liquid(point, faces, values, anchor=None, inlet=0.):
    """Evaluate the same integral reconstruction used by face evolution."""
    if not faces[0]<=point<=faces[-1] or faces[-1]==faces[0]:
        raise ValueError('point outside positive active support')
    if point==0: return float(inlet)
    if anchor is None: anchor=faces[-1]
    i=min(int(np.searchsorted(faces,point,side='right')-1),len(values)-1)
    x=(faces[:-1]+faces[1:])/2
    if len(values)==1: return float(inlet+(values[0]-inlet)*point/x[0])
    p=root_means(faces,anchor)
    if i<=1:
        w=weights(np.array([0.,x[0],x[1]]),np.array([np.sqrt(anchor),p[0],p[1]]),point,np.sqrt(max(anchor-point,0.)))
        return float(w@np.r_[inlet,values[:2]])
    w=weights(x[i-2:i+1],p[i-2:i+1],point,np.sqrt(max(anchor-point,0.)))
    return float(w@values[i-2:i+1])


def transport_solve(c0,old_faces,new_faces,h,loss0,response,*,inlet=0.,anchor0=None,anchor1=None):
    """Unchanged Reynolds amounts; enriched spatial face constraints."""
    v0,v1=np.diff(old_faces),np.diff(new_faces)
    if len(c0)>1 and v1[-1]==0:
        # Root-bracket limit at the instant a new cell is admitted. Two
        # coincident faces enclose no equation or stored amount. Solve only
        # positive physical support, then attach its identical front trace.
        if v0[-1]!=0 or loss0[-1]!=0 or response[-1]!=0:
            raise ValueError('zero-volume cell carries a nonzero amount')
        c,flux,cf,error=transport_solve(c0[:-1],old_faces[:-1],new_faces[:-1],h,
                                       loss0[:-1],response[:-1],inlet=inlet,
                                       anchor0=anchor0,anchor1=anchor1)
        trace=face_values(c,new_faces[:-1],inlet,anchor1)[-1]
        return np.r_[c,trace],np.r_[flux,flux[-1]],cf,error
    co,boundary,first_upper=reconstruction(new_faces,anchor1)
    trace0=face_values(c0,old_faces,inlet,anchor0)
    if v0[-1]==0: trace0[-1]=c0[-1]
    factor=h-CAPACITY*(new_faces-old_faces)
    n=len(c0);band=np.zeros((4,n))
    band[0]=CAPACITY*v1+response+.5*factor[1:]*co[0]
    if n>1: band[1,:-1]=.5*(factor[2:]*co[1,1:]-factor[1:-1]*co[0,:-1])
    if n>2: band[2,:-2]=.5*(factor[3:]*co[2,2:]-factor[2:-1]*co[1,1:-1])
    if n>3: band[3,:-3]=-.5*factor[3:-1]*co[2,2:-1]
    rhs=CAPACITY*v0*c0+loss0-.5*np.diff(factor*trace0)
    rhs-=.5*np.diff(factor*np.r_[inlet,boundary*inlet])
    if n==1:
        c1=rhs/band[0]
    else:
        # Only the inlet closure uses one downstream average. Its face amount
        # enters BOTH adjacent equations with opposite signs.
        band[0,1]-=.5*factor[1]*first_upper
        upper=np.zeros((1,n));upper[0,1]=.5*factor[1]*first_upper
        c1=solve_banded((3,1),np.vstack((upper,band)),rhs,check_finite=False)
    trace1=face_values(c1,new_faces,inlet,anchor1)
    flux=factor*(trace0+trace1)/2
    err=CAPACITY*(v1*c1-v0*c0)+np.diff(flux)-loss0+response*c1
    return c1,flux,.5*(trace0[-1]+trace1[-1]),float(max(abs(err)))

def step(radial, c0, j0, old_faces, h, *, fixed=False, displacement=None, materialize=True, offset=0., exit_speed=0.):
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
        c1, flux, cf, linear = transport_solve(c0, old_faces, faces, h, loss, response,
                                                   anchor0=old_faces[-1]+offset,
                                                   anchor1=faces[-1]+offset+h*exit_speed)
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
    exit_speed = 0.
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
        anchor = s+exit_speed*(t-arrival) if arrival is not None else s
        trace = face_values(c, faces, anchor=anchor)[-1] if s > 0 else 0.
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
            liquid[active] = [point_liquid(p, faces, c, anchor) for p in z[active]]
            b0 = INITIAL*float(radial.weights @ np.exp(-radial.rates*t))
            bfront = INITIAL if arrival is None else float(radial.means(histories)[-1])
            b[active] = [point_liquid(p, faces, means/np.diff(faces), anchor, b0) for p in z[active]]
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
            offset = exit_speed*(t-arrival) if arrival is not None else 0.
            next_state = step(radial, c, j, faces, h, fixed=arrival is not None, offset=offset, exit_speed=exit_speed)
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
                boundary1 = point_liquid(point, faces, c, new_s+offset+h*exit_speed)
                if fraction > 0 or point > old_s:
                    old_front = face_values(old_c, old_faces, anchor=old_s+offset)[-1] if old_s > 0 else 0.
                    new_front = face_values(c, faces, anchor=new_s+offset+(0. if crossing else h*exit_speed))[-1]
                    boundary0 = old_front+fraction*(new_front-old_front)
                else:
                    boundary0 = point_liquid(point, old_faces, old_c, old_s+offset)
                histories[:, k:k+1] = radial.advance(histories[:, k:k+1], np.array([boundary0]),
                    np.array([boundary1]), np.ones(1), np.zeros(1), age)
        if t >= 1:
            cup += h if arrival is None else diagnostic['face_amount'][-1]
        t = new_t
        if crossing and len(c) == ctrl.bed:
            arrival = t
            cf_exit = face_values(c, faces)[-1]
            exit_speed = (1-cf_exit)/(JUMP-CAPACITY*cf_exit)
            events.append({'t': t, 'kind': 'desaturation_exit', 'outlet_left': 1.,
                           'outlet_right': float(face_values(c, faces, anchor=new_s+offset+(0. if crossing else h*exit_speed))[-1]),
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
        min_c = min(min_c, float(min(c)), float(face_values(c, faces, anchor=new_s+offset+(0. if crossing else h*exit_speed)).min()))
        max_c = max(max_c, float(max(c)), float(face_values(c, faces, anchor=new_s+offset+(0. if crossing else h*exit_speed)).max()))
        min_grain = min(min_grain, float(np.min(radial.means(j)/np.diff(faces))))
        accepted.append([t, new_s, cup, *phases, residual, diagnostic['transfer_residual'],
                         diagnostic['front_residual'], diagnostic['linear_residual'], diagnostic['algebra_scale'],
                         float(face_values(c, faces, anchor=new_s+offset+(0. if crossing else h*exit_speed))[-1])])
        reached = t == target
        if reached or crossing:
            save('exit' if arrival == t else ('cell_crossing' if crossing else ('first_drip' if t == 1 else None)))
        if reached:
            sample += 1
        if min_c < -1e-8 or max_c > 1+1e-8 or min_grain < -1e-8 or min(phases) < -1e-8:
            status, reason = 'NUMERICAL_BOUNDS_FAILED', 'accepted state or trace outside budget'; break
        if crossing and arrival is None:
            front_c = face_values(c, faces, anchor=new_s+offset+(0. if crossing else h*exit_speed))[-1]
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
    result['configuration_sha256'] = hashlib.sha256(json.dumps(result['controls'], sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    result['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['inherited_source_sha256'] = hashlib.sha256(Path(__file__).with_name('grudeva2026_conservative_003.py').read_bytes()).hexdigest()
    result['radial_source_sha256'] = hashlib.sha256(Path(__file__).with_name('grudeva2026_reference_002.py').read_bytes()).hexdigest()
    args.output.write_text(json.dumps(result, allow_nan=False, separators=(',', ':'))+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'reason', 'arrival', 'seconds',
                                            'max_normalized_conservation_residual')}))
    return 2  # execution is never numerical qualification


if __name__ == '__main__':
    raise SystemExit(main())

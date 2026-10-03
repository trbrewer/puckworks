"""Bounded offline diagnostic, MODEL-GRUDEVA2026-REFERENCE-002, route A.

Adapted from the permissioned grudeva2025.reduced port of Yoana Grudeva's
espresso-model, with implicit conservative radial shells and the changes in
CONTRACT.md. This modified reference lineage is NOT an untouched author run.
Direct written permission (2026-08-14), NOT MIT/CC-BY/OSI for the derived
reference algorithm; see docs/permissions/grudeva2025.md and THIRD_PARTY_NOTICES.
Article mathematics: Grudeva, Moroney & Foster, DOI 10.1017/S095679252500018X.
No production grudeva2026 numerical helper is imported. No network on import.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.linalg import solve_banded
from scipy.sparse import diags

INITIAL = 1.388
BETA, DELTA, CAPACITY = 3.2, .8, 4.2
QB = 1 / 2.4


@dataclass(frozen=True)
class Controls:
    bed: int = 64
    shells: int = 32
    dt: float = .002
    horizon: float = .4
    diffusivity: float = 1.

    def __post_init__(self):
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 4
               for v in (self.bed, self.shells)):
            raise ValueError('bed and shells must be integers >=4')
        if not all(np.isfinite(v) for v in (self.dt, self.horizon, self.diffusivity)):
            raise ValueError('finite controls required')
        if min(self.dt, self.horizon) <= 0 or self.diffusivity < 0:
            raise ValueError('positive time controls, nonnegative diffusivity required')


def jump_speed(c):
    """Independent storage-jump / advective-jump calculation, gamma=1."""
    if not np.isfinite(c) or not 0 <= c <= 1:
        raise ValueError('unsupported front concentration')
    storage_jump = (1-c) + BETA*(INITIAL-c)
    return (1-c) / storage_jump


def normalization_audit():
    # The two radii affect bare symbols but cancel in the effective coefficients.
    af, ab, phi_t = 3.65e-6, 228.69e-6, .2
    area_f, area_b = 3*.64/af, 3*.16/ab
    b0 = (area_f+area_b)/2
    bf, bb = area_f/b0, area_b/b0
    qf, qb = phi_t/(af*b0), phi_t/(ab*b0)
    return {'legacy_bf': bf, 'legacy_bb': bb, 'legacy_Qf': qf, 'legacy_Qb': qb,
            'effective_fines': bf/(3*qf), 'effective_boulder_flux': bb/qb,
            'canonical_beta': BETA, 'canonical_inverse_Qb': 1/QB,
            'passed': bool(abs(bf/(3*qf)-BETA) < 1e-14 and abs(bb/qb-1/QB) < 1e-14),
            'table1_ratio': 310/224, 'table2_initial': INITIAL,
            'legacy_explicit_D1_dt_over_dr2': (32/5)/(3000-1)*29**2}


def shell_operator(n, diffusivity):
    """Finite volumes of r^2 dc/dt = D (r^2 dc/dr)_r; weights sum to one."""
    faces = np.linspace(0., 1., n+1)
    centers = (faces[:-1]+faces[1:])/2
    weights = np.diff(faces**3)
    conductance = 3*diffusivity*faces[1:-1]**2/np.diff(centers)
    surface = 3*diffusivity/(1-centers[-1])
    lower, upper = conductance/weights[1:], conductance/weights[:-1]
    diagonal = -np.r_[conductance, surface]/weights
    diagonal[1:] -= conductance/weights[1:]
    forcing = np.zeros(n)
    forcing[-1] = surface/weights[-1]
    return weights, lower, diagonal, upper, forcing, surface


def shell_step(grains, boundary, dt, operator):
    """Backward Euler, all columns at fixed physical z, no state projection."""
    weights, lower, diagonal, upper, forcing, _ = operator
    band = np.zeros((3, len(weights)))
    band[0, 1:] = -dt*upper
    band[1] = 1-dt*diagonal
    band[2, :-1] = -dt*lower
    return solve_banded((1, 1), band, grains+dt*forcing[:, None]*boundary,
                        check_finite=False)


def liquid_step(liquid, source, eta, snew, speed, dt):
    """E27 implicit upwind; tested with exact C=k*z, G=k on a moving grid."""
    adv = (1/CAPACITY-eta[1:]*speed)/snew
    k = dt*adv/(eta[1]-eta[0])
    band = np.zeros((2, len(eta)-1))
    band[0] = 1+k
    band[1, :-1] = -k[1:]
    return np.r_[0., solve_banded((1, 0), band, liquid[1:]+dt*source[1:]/CAPACITY,
                                  check_finite=False)]


def reached_sample(t, dt, target):
    """Exact floating endpoint, including addition rounding up to the target."""
    return t+dt >= target


def grain_history(times, boundary0, slope, initial, *, shells=3200, diffusivity=.7,
                  q_b=.4, rtol=2e-11):
    """Radial FV/BDF analytical qualification; linear boundary from activation."""
    ts = np.asarray(times, float)
    if ts.ndim != 1 or len(ts) < 2 or np.any(np.diff(ts) <= 0):
        raise ValueError('strictly increasing times required')
    op = shell_operator(shells, diffusivity)
    w, lower, diagonal, upper, forcing, surface = op
    matrix = diags([lower, diagonal, upper], [-1, 0, 1], format='csc')
    ages = ts-ts[0]
    start = time.perf_counter()
    result = solve_ivp(lambda age, c: matrix@c+forcing*(boundary0+slope*age),
                       (0., ages[-1]), np.full(shells, initial), method='BDF',
                       jac=matrix, rtol=rtol, atol=rtol/100, t_eval=ages)
    if not result.success:
        raise RuntimeError(result.message)
    means = w@result.y
    flux = surface*(result.y[-1]-(boundary0+slope*ages))/(3*q_b)
    # Age-zero flux of a jump is unavailable, not the finite grid's regularization.
    return {'mean': means.tolist(), 'flux': [None]+flux[1:].tolist(),
            'seconds': time.perf_counter()-start, 'shells': shells}


def analytic_sphere(age, initial, boundary0, slope, diffusivity=.7, q_b=.4):
    """Infinite-series scalar oracle, independently derived; not either backend."""
    k = np.arange(1., 10001.)
    rate = (np.pi*k)**2*diffusivity
    decay = np.exp(-rate*age)
    mean = boundary0+slope*age+6/np.pi**2*(
        (initial-boundary0)*np.sum(decay/k**2)
        - slope*(np.pi**2/(90*diffusivity)-np.sum(decay/(rate*k**2))))
    flux = 2*diffusivity/q_b*((initial-boundary0)*sum(decay)
                           - slope*(1/(6*diffusivity)-sum(decay/rate)))
    return float(flux), float(mean)


def analytical_qualification():
    ages = np.array([0., .002, .02, .1, .3, .7])
    rows = []
    for n in (800, 1600, 3200):
        for initial, boundary, slope in ((1.6, .2, .3), (.2, .2, .5)):
            r = grain_history(4.3+ages, boundary, slope, initial, shells=n)
            expected = [analytic_sphere(age, initial, boundary, slope) for age in ages[1:]]
            rows.append({'shells': n, 'initial': initial, 'slope': slope,
                         'mean_error': float(np.max(np.abs(np.array(r['mean'][1:])-
                                                          np.array(expected)[:, 1]))),
                         'flux_error': float(np.max(np.abs(np.array(r['flux'][1:])-
                                                          np.array(expected)[:, 0]))),
                         'seconds': r['seconds']})
    a = grain_history(4.3+ages, .2, .3, 1.6)
    b = grain_history(15.3+ages, .2, .3, 1.6)
    eq = grain_history(4.3+ages, 1.4, 0., 1.4, shells=64)
    front = max(abs(jump_speed(c)*(1+BETA*(INITIAL-c)/(1-c))-1)
                for c in (0., .2, .6, .95))
    shifted = max(abs(np.array(a['flux'][1:])-b['flux'][1:]))
    equilibrium = max(abs(np.array(eq['mean'])-1.4))
    final = [r for r in rows if r['shells'] == 3200]
    return {'front_relative_error': front, 'radial_refinement': rows,
            'time_translation_flux_error': float(shifted),
            'equilibrium_mean_error': float(equilibrium), 'history_solve_count': 9,
            'passed': bool(front <= 1e-12 and shifted <= 1e-8 and equilibrium <= 2e-12
                           and all(r['mean_error'] <= 2e-5 and r['flux_error'] <= 2e-4 for r in final))}


def observe(t, s, liquid, grains, z, eta, weights, cup, arrival):
    """Actual state integrals, independent of the solver's discharge accumulator."""
    ic = s*np.trapezoid(liquid, eta)
    means = weights@grains
    active = z < s
    # At zero age the grain interior is untouched; the surface has zero volume.
    gz = np.r_[z[active], s]
    gb = np.r_[means[active], means[-1] if arrival is not None else INITIAL]
    ib = float(np.trapezoid(gb, gz)) if len(gz) > 1 else 0.
    phases = np.array([ic+min(t, 1.)-s, BETA*(ic+INITIAL*(1-s)),
                       DELTA*(ib+INITIAL*(1-s))])
    outlet = 0. if t < 1 else (1. if arrival is None else float(liquid[-1]))
    return phases, outlet, means


def run(ctrl=Controls()):
    """Modified reference route. Returned arrays are unqualified diagnostics."""
    started = time.perf_counter()
    eta = np.linspace(0., 1., ctrl.bed)
    z = eta.copy()  # fixed PHYSICAL coordinates for the grains
    op = shell_operator(ctrl.shells, ctrl.diffusivity)
    w = op[0]
    grain = np.full((ctrl.shells, ctrl.bed), INITIAL)
    liquid = np.zeros(ctrl.bed)
    activation = np.full(ctrl.bed, np.nan)
    activation[0] = 0.
    t, s, cup, quadrature, arrival = 0., 0., 0., 0., None
    records, profiles, histories, mean_profiles = [], [], [], []
    source_integral, grain_loss = 0., np.zeros(ctrl.bed)
    exchange_balance = 0.
    status, reason = 'EXECUTED_UNQUALIFIED', None
    history_z = np.array([.025, .1, .25, .5, .75, .9, 1.])
    diagnostics = {0., .01, .05, .1, .2, .4, .8, 1., 1.01, 2., 3.2, 4.8, 6.4, 8.}
    fixture = json.loads((Path(__file__).parents[1]/'data/grudeva2026/publication_reference.json').read_text())
    diagnostics.update(row['t'] for row in fixture['figure4'])
    diagnostics.update(np.round(np.arange(0., ctrl.horizon, .025), 12))
    diagnostics.update(np.round(np.arange(6.3, min(6.7, ctrl.horizon), .005), 12))
    samples = sorted(x for x in diagnostics if 0 <= x < ctrl.horizon)+[ctrl.horizon]
    sample_idx = 1
    def save():
        phases, outlet, means = observe(t, s, liquid, grain, z, eta, w, cup, arrival)
        records.append([t, s, outlet, cup, quadrature, *phases,
                        (sum(phases)+cup-4*INITIAL)/(4*INITIAL), source_integral])
        profiles.append(liquid.copy())
        histories.append(np.interp(history_z, z, means))
        mean_profiles.append(means)
    save()
    while sample_idx < len(samples):
        if time.perf_counter()-started > 900:
            status, reason = 'RESOURCE_LIMIT', '900 second run ceiling'
            break
        try:
            speed = jump_speed(float(liquid[-1])) if arrival is None else 0.
        except ValueError as exc:
            status, reason = 'UNSUPPORTED_OR_NUMERICAL_BOUNDS', str(exc)
            break
        target = samples[sample_idx]
        h = min(ctrl.dt, target-t)
        if t < 1 < t+h:
            h = 1-t
        hits_exit = arrival is None and speed > 0 and s+speed*h >= 1
        if hits_exit:
            h = (1-s)/speed
        hits_sample = reached_sample(t, h, target)
        snew = s+speed*h
        if snew > min(t+h, 1.)+1e-10:
            status, reason = 'UNSUPPORTED_REGIME', 'desaturation overtook wetting'
            break
        count = int(np.searchsorted(z, snew, side='right'))
        boundary = np.interp(z[:count], s*eta, liquid) if s > 0 else np.zeros(count)
        old = grain[:, :count].copy()
        existing = int(np.searchsorted(z, s, side='right'))
        if existing:
            grain[:, :existing] = shell_step(old[:, :existing], boundary[:existing], h, op)
        for j in range(existing, count):
            activation[j] = t+(z[j]-s)/speed
            age = t+h-activation[j]
            if age > 0:
                grain[:, j:j+1] = shell_step(old[:, j:j+1], boundary[j:j+1], age, op)
        loss = w@(old-grain[:, :count])
        grain_loss[:count] += loss
        # Interval-mean phase exchange includes the partial first activation step.
        source = loss/(3*QB*h)
        surface_loss = np.zeros(count)
        if existing:
            surface_loss[:existing] = h*op[-1]*(grain[-1, :existing]-boundary[:existing])
        for j in range(existing, count):
            surface_loss[j] = (t+h-activation[j])*op[-1]*(grain[-1, j]-boundary[j])
        exchange_balance = max(exchange_balance, float(np.max(abs(loss-surface_loss))))
        mapped = np.interp(eta*snew, z[:count], source)
        previous_exit = liquid[-1]
        liquid = liquid_step(liquid, mapped, eta, snew, speed, h)
        if t >= 1-1e-13:
            if arrival is None:
                cup += h
                quadrature += h
            else:
                cup += h*liquid[-1]
                quadrature += h*(previous_exit+liquid[-1])/2
        source_integral += h*snew*np.trapezoid(mapped, eta)
        t, s = target if hits_sample else t+h, snew
        if hits_exit:
            arrival = t  # localized step, no projection or overshoot/clamp
        if hits_sample or hits_exit:
            save()
            if hits_sample:
                sample_idx += 1
        if np.min(liquid) < -1e-8 or np.max(liquid) > 1+1e-8 or np.min(grain) < -1e-8:
            status, reason = 'NUMERICAL_BOUNDS_FAILED', 'accepted state out of bounds; no clipping'
            break
    data = np.asarray(records)
    max_residual = float(np.max(abs(data[:, 8])))
    return {'controls': asdict(ctrl), 'status': status, 'reason': reason,
            'arrival': arrival, 'records': data.tolist(),
            'record_columns': ['t', 's', 'outlet', 'cup_right', 'cup_trapezoid_split',
                               'liquid', 'fines', 'boulders', 'residual', 'mapped_source_integral'],
            'eta': eta.tolist(), 'liquid_profiles': np.asarray(profiles).tolist(),
            'physical_grain_z': z.tolist(), 'boulder_mean_profiles': np.asarray(mean_profiles).tolist(),
            'grain_history_z': history_z.tolist(), 'grain_means': np.asarray(histories).tolist(),
            'activation': [None if np.isnan(x) else float(x) for x in activation],
            'terminal_grain_means': (w@grain).tolist(),
            'grain_transfer_balance_max': exchange_balance,
            'grain_integrated_loss_check': float(np.max(abs(grain_loss-(INITIAL-w@grain)))),
            'max_normalized_conservation_residual': max_residual,
            'cup_quadrature_difference': float(np.max(abs(data[:, 3]-data[:, 4]))),
            'seconds': time.perf_counter()-started,
            'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'qualified': False, 'physical_validation': 'NOT_ESTABLISHED'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--mode', choices=['analytic', 'run'], required=True)
    ap.add_argument('--output', type=Path, required=True)
    for key, default, kind in [('bed', 64, int), ('shells', 32, int), ('dt', .002, float),
                               ('horizon', .4, float), ('diffusivity', 1., float)]:
        ap.add_argument('--'+key, type=kind, default=default)
    args = ap.parse_args(argv)
    result = (analytical_qualification() if args.mode == 'analytic' else
              run(Controls(**{k: getattr(args, k) for k in asdict(Controls())})))
    result['source_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('status', 'passed', 'arrival',
                     'max_normalized_conservation_residual', 'seconds') if k in result}))
    return 0 if args.mode == 'analytic' and result['passed'] else (2 if args.mode == 'run' else 1)


if __name__ == '__main__':
    raise SystemExit(main())

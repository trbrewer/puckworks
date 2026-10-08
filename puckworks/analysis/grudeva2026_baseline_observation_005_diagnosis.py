"""One frozen, archive-only 005 diagnosis; never evolves or qualifies a solver.

The independent polynomial uses two-node Gauss moments about the stencil center.
The existing observer remains the observed operator, not the expected-value oracle.
"""
from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

import numpy as np
from scipy.integrate import quad

from . import grudeva2026_baseline_observation_005 as obs


def stencil(faces, z):
    n = len(faces)-1
    cell = min(max(int(np.searchsorted(faces, z, side='right'))-1, 0), n-1)
    first = min(max(cell-1, 0), n-3)
    return cell, np.arange(first, first+3)


def moment_polynomial(faces, averages, z):
    """Independent exact quadratic cell integrals via Gauss nodes, not centers."""
    faces, averages = np.asarray(faces), np.asarray(averages)
    cell, indices = stencil(faces, z)
    local = faces[indices[0]:indices[-1]+2]
    origin, scale = (local[0]+local[-1])/2, local[-1]-local[0]
    left, right = (local[:-1]-origin)/scale, (local[1:]-origin)/scale
    mid, half = (left+right)/2, (right-left)/2
    nodes = mid[:, None]+half[:, None]*np.array([-1., 1.])/np.sqrt(3.)
    moments = np.stack([np.mean(nodes**k, axis=1) for k in range(3)], axis=1)
    coefficients = np.linalg.solve(moments, averages[..., indices].T).T
    u = (z-origin)/scale
    point = np.array([1., u, u*u])
    weights = np.linalg.solve(moments.T, point)
    return dict(cell=cell, indices=indices, origin=origin, scale=scale,
                moments=moments, coefficients=coefficients, weights=weights,
                value=coefficients @ point, condition=float(np.linalg.cond(moments)))


def polynomial_integral(poly, left, right):
    a, b = (left-poly['origin'])/poly['scale'], (right-poly['origin'])/poly['scale']
    factors = np.array([(b**(k+1)-a**(k+1))/(k+1) for k in range(3)])
    return poly['scale']*(poly['coefficients'] @ factors)


def reaverage(faces, means, left, right):
    """Integrate the piecewise fine reconstruction over actual overlap cells."""
    if not faces[0] <= left < right <= faces[-1]:
        raise ValueError('coarse cell outside fine physical domain')
    boundaries = np.r_[left, faces[(faces > left) & (faces < right)], right]
    pieces = []
    for a, b in zip(boundaries[:-1], boundaries[1:]):
        poly = moment_polynomial(faces, means, (a+b)/2)
        integral = float(polynomial_integral(poly, a, b))
        pieces.append(dict(left=float(a), right=float(b), fine_cell=poly['cell'], integral=integral))
    return math.fsum(p['integral'] for p in pieces)/(right-left), pieces


def finite_point(age, rates, forcing):
    """Exact local-age relaxation response to b0+a*age+b*age**2."""
    r = np.asarray(rates)[:, None]
    age = np.atleast_1d(age)[None, :]
    b0, a, b = forcing
    amplitude = obs.INITIAL-b0+a/r-2*b/r**2
    return (amplitude*np.exp(-r*age) + b0-a/r+2*b/r**2
            + (a-2*b/r)*age + b*age**2)


def finite_averages(faces, t, rates, forcing, speed=.2):
    """Closed-form age integral; expm1 avoids subtracting close exponentials."""
    r = np.asarray(rates)[:, None]
    low, high = t-faces[1:]/speed, t-faces[:-1]/speed
    span = np.diff(faces)/speed
    if np.min(low) < -64*np.finfo(float).eps*max(1., t):
        raise ValueError('fixture cells precede prescribed activation')
    b0, a, b = forcing
    exponential = np.exp(-r*low)*(-np.expm1(-r*span))/(r*span)
    return ((obs.INITIAL-b0+a/r-2*b/r**2)*exponential
            + b0-a/r+2*b/r**2+(a-2*b/r)*(low+high)/2
            + b*(low*low+low*high+high*high)/3)


def array_json(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {k: array_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [array_json(v) for v in value]
    return value


def checkpoint(path, result):
    """One exclusive output, then same-file flushed partial stages; no retries."""
    with path.open('w') as stream:
        stream.write(obs.canonical(array_json(result))+'\n')
        stream.flush()
        os.fsync(stream.fileno())


def point_record(tr, t, z):
    y, segment = tr.evaluate(t)
    front, _, modal = obs.state_fields(y, tr.n, tr.m)
    faces = front*tr.faces
    _, mean, modes = obs.profiles(t, y, tr.n, tr.weights, tr.faces, np.array([z]), tr.arrival)
    poly = moment_polynomial(faces, modal, z)
    normalized = moment_polynomial(tr.faces, modal, z/front)
    cell_means = tr.weights @ modal
    mean_poly = moment_polynomial(faces, cell_means, z)
    indices = poly['indices']
    reconstructed_then_weighted = float(tr.weights @ poly['value'])
    residual = poly['coefficients'] @ poly['moments'].T-modal[:, indices]
    scale = max(1., float(np.sum(abs(tr.weights[:, None]*modal[:, indices]))),
                float(np.sum(abs(tr.weights*poly['value']))))
    allowance = obs.ALGEBRA*scale*max(poly['condition'], normalized['condition'])
    activation = tr.activation(z)
    # Center values of the fitted polynomial are not the input cell averages.
    centers = (faces[indices]+faces[indices+1])/2
    u = (centers-poly['origin'])/poly['scale']
    center_values = poly['coefficients'] @ np.stack([np.ones(3), u, u*u])
    details = dict(t=t, z=z, front=front, activation=activation, grain_age=t-activation,
        segment_valid_interval=segment['valid_interval'], containing_cell=poly['cell'],
        stencil=indices, physical_faces=faces[indices[0]:indices[-1]+2],
        physical_widths=np.diff(faces)[indices], normalized_faces=tr.faces[indices[0]:indices[-1]+2],
        reconstruction_weights=poly['weights'], moment_matrix=poly['moments'],
        moment_condition=poly['condition'], polynomial_coefficients=poly['coefficients'],
        integral_moment_residual=residual, modal_axis=0, weights=tr.weights, rates=tr.rates,
        modal_cell_averages=modal[:, indices], modal_point=modes[:, 0],
        modal_contributions=tr.weights*modes[:, 0], grain_mean=float(mean[0]),
        grain_cell_averages=cell_means[indices], independent_modal_point=poly['value'],
        independent_grain_mean=reconstructed_then_weighted,
        analytic_inlet=float(obs.INITIAL*np.sum(tr.weights*np.exp(-tr.rates*t))) if z == 0 else None,
        integral_moment_residual_max=float(np.max(abs(residual))),
        integral_residual_max=float(np.max(abs(residual*np.diff(faces)[indices]))),
        cell_center_minus_average=center_values-modal[:, indices],
        physical_minus_normalized=poly['value']-normalized['value'],
        independent_minus_observer=poly['value']-modes[:, 0],
        reconstruct_then_weight_minus_weight_then_reconstruct=reconstructed_then_weighted-float(mean_poly['value']),
        arithmetic_allowance=allowance,
        arithmetic_max=float(max(np.max(abs(residual)), np.max(abs(poly['value']-normalized['value'])),
            np.max(abs(poly['value']-modes[:, 0])),
            abs(reconstructed_then_weighted-float(mean_poly['value'])))))
    details['implementation_agrees'] = details['arithmetic_max'] <= allowance
    return details, faces, cell_means


def archived_point(a, b, specification):
    t, z = specification['t'], specification['z']
    ra, fa, ba = point_record(a, t, z)
    rb, fb, bb = point_record(b, t, z)
    lo, hi = min(ra['front'], rb['front']), max(ra['front'], rb['front'])
    spatial = ((z < lo-.008 or z > hi+.008) or t >= max(a.arrival, b.arrival))
    spatial = spatial and (t >= 1. or abs(z-min(t, 1.)) > .008)
    aged = min(ra['grain_age'], rb['grain_age']) >= .02
    total = ra['grain_mean']-rb['grain_mean']
    result = dict(name=specification['name'], normal=ra, combined=rb,
        normal_minus_combined=total, original_allowance=specification['allowance'],
        original_max_absolute=specification['original_max_absolute'],
        mask=dict(grain_profile=bool(spatial and aged), grain_history=bool(aged),
                  inlet_gate=True if z == 0 else None, spatial=bool(spatial), aged=bool(aged)))
    if z == 0:
        result['normal_minus_analytic_inlet'] = ra['grain_mean']-ra['analytic_inlet']
        result['combined_minus_analytic_inlet'] = rb['grain_mean']-rb['analytic_inlet']
    p = moment_polynomial(fa, ba, z)
    ids = p['indices']
    if fa[ids[0]] < fb[0] or fa[ids[-1]+1] > fb[-1]:
        result['decomposition'] = dict(supported=False, reason='entire normal stencil lacks common physical support')
    else:
        averages, pieces = zip(*(reaverage(fb, bb, fa[j], fa[j+1]) for j in ids))
        averages = np.array(averages)
        fine = float(moment_polynomial(fb, bb, z)['value'])
        coarse = float(p['value'])
        stored = float((ba[ids]-averages) @ p['weights'])
        reconstruction = float(averages @ p['weights']-fine)
        result['decomposition'] = dict(supported=True, reference='COMBINED_REPRESENTATION_NOT_CONTINUUM',
            total=coarse-fine, original_observer_total=total,
            original_minus_mean_first=total-(coarse-fine),
            stored_field=stored, reaveraging_reconstruction=reconstruction,
            closure=(coarse-fine)-stored-reconstruction,
            coarse_means=ba[ids], fine_averaged_on_coarse=averages,
            stored_mean_differences=ba[ids]-averages, overlap_pieces=pieces)
    resolved = a.m-1
    assert np.array_equal(a.weights[:-1], b.weights[:resolved])
    assert np.array_equal(a.rates[:-1], b.rates[:resolved])
    ac, bc = ra['modal_contributions'], rb['modal_contributions']
    matched = ac[:resolved]-bc[:resolved]
    tail = float(ac[-1]-np.sum(bc[resolved:]))
    result['spectrum_split'] = dict(shared_resolved_modes=resolved,
        shared_per_mode_difference=matched, shared_sum=float(np.sum(matched)),
        normal_tail=float(ac[-1]), combined_additional_resolved=float(np.sum(bc[resolved:-1])),
        combined_tail=float(bc[-1]), tail_vs_additional_and_tail=tail,
        closure=total-float(np.sum(matched))-tail)
    return array_json(result)


def fixture_case(tr, case, forcing):
    t, z = case['t'], np.array(case['z'])
    front, speed = min(.2*t, 1.), .2
    faces = front*tr.faces
    averages = finite_averages(faces, t, tr.rates, forcing)
    actual = tr.weights @ obs.cell_reconstruction(tr.faces, averages, z/front)
    exact = tr.weights @ finite_point(t-z/speed, tr.rates, forcing)
    age = t-z/speed
    return dict(t=t, z=z, age=age, actual=actual, exact=exact, signed_error=actual-exact,
                positive_age_mask=age >= .02), averages, faces


def fixture_diagnosis(tr, plan):
    output = dict(spectrum_weights=tr.weights.tolist(), spectrum_rates=tr.rates.tolist(),
                  cells=tr.n, modes_including_tail=tr.m, families={})
    for name, forcing in plan['forcing'].items():
        cases, numerical_checks = [], []
        for case_index, case in enumerate(plan['cases']):
            values, averages, faces = fixture_case(tr, case, forcing)
            cases.append(array_json(values))
            for selected in plan['independent_average_subset']:
                if selected['case_index'] != case_index:
                    continue
                j = selected['cell'] if selected['cell'] >= 0 else tr.n+selected['cell']
                for k in sorted(set([0, 31, tr.m-2, tr.m-1])):
                    low, high = case['t']-faces[j+1]/.2, case['t']-faces[j]/.2
                    rate = tr.rates[k]
                    knots = [low+x/rate for x in (1., 4., 16., 64.) if low < low+x/rate < high]
                    integral, error = quad(lambda u: float(finite_point(u, [rate], forcing)[0, 0]),
                        low, high, points=knots, epsabs=1e-13*(high-low), epsrel=1e-12, limit=100)
                    numerical_checks.append(dict(t=case['t'], cell=j, mode=k,
                        exact_average=float(averages[k, j]), independent_average=integral/(high-low),
                        signed_difference=float(averages[k, j]-integral/(high-low)),
                        quadrature_estimated_error=error/(high-low)))
        rows = [dict(t=c['t'], z=z, age=age, signed_error=e, eligible=eligible)
                for c in cases for z, age, e, eligible in zip(c['z'], c['age'], c['signed_error'], c['positive_age_mask'])]
        eligible = [r for r in rows if r['eligible']]
        output['families'][name] = dict(cases=cases, requested=len(rows), included=len(eligible),
            excluded=len(rows)-len(eligible), unavailable=0,
            maximum_all=max(rows, key=lambda r: abs(r['signed_error'])),
            maximum_age_eligible=max(eligible, key=lambda r: abs(r['signed_error'])),
            allowance=plan['grain_allowance'],
            failures_all=sum(abs(r['signed_error']) > plan['grain_allowance'] for r in rows),
            failures_age_eligible=sum(abs(r['signed_error']) > plan['grain_allowance'] for r in eligible),
            independent_average_checks=numerical_checks)
    return output


def run(folder, plan, result, save):
    root = Path(obs.__file__).parents[2]
    for name, expected in plan['frozen_sources'].items():
        if obs.sha(root/name) != expected:
            raise ValueError('frozen source mismatch: '+name)
    if obs.sha(__file__) != plan['diagnostic_source_sha256']:
        raise ValueError('diagnostic source mismatch')
    trajectories = {}
    try:
        for row in ('normal', 'combined'):
            binding = plan['captures'][row]
            path = folder/binding['file']
            if obs.sha(path) != binding['sha256']:
                raise ValueError('successful capture metadata mismatch')
            meta = obs.read_json(path)
            for s in meta['segments']:
                if obs.sha(folder/s['receipt_file']) != s['receipt_sha256']:
                    raise ValueError('successful segment receipt mismatch')
            # Full safe validation also verifies the original expected file/array identities.
            trajectories[row] = obs.Trajectory(path)
            result['archive_checks'][row] = dict(metadata_sha256=binding['sha256'],
                segments=[dict(file=s['file'], sha256=s['sha256'], receipt_sha256=s['receipt_sha256'])
                          for s in meta['segments']], validated=True)
            save()
        for point in plan['failure_points']:
            result['archived_points'].append(archived_point(trajectories['normal'], trajectories['combined'], point))
            save()
        for row, tr in trajectories.items():
            result['manufactured'][row] = fixture_diagnosis(tr, plan['fixture'])
            save()
        result['execution'] = 'DIAGNOSIS_COMPLETE_NOT_QUALIFICATION'
    finally:
        for tr in trajectories.values():
            tr.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-directory', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--allocation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    plan, allocation = obs.read_json(args.plan), obs.read_json(args.allocation)
    if (allocation['diagnostic_plan_sha256'] != obs.sha(args.plan)
            or allocation['diagnostic_source_sha256'] != obs.sha(__file__)
            or allocation['attempt'] != plan['attempt']):
        raise ValueError('diagnostic allocation identity mismatch')
    with args.output.open('x'):
        pass
    result = dict(task=obs.TASK, physical_validation='NOT_ESTABLISHED',
        scientific_outcome='OBSERVER_QUALIFICATION_INCOMPLETE',
        execution='INCOMPLETE', source_sha256=obs.sha(__file__), plan_sha256=obs.sha(args.plan),
        allocation_sha256=obs.sha(args.allocation), archive_checks={}, archived_points=[], manufactured={})
    def save():
        checkpoint(args.output, result)
    save()
    try:
        run(args.runs_directory, plan, result, save)
    except BaseException as exc:
        result['failure'] = dict(type=type(exc).__name__, message=str(exc))
        save()
        raise
    save()
    print(obs.canonical(dict(execution=result['execution'], artifact_sha256=obs.sha(args.output))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

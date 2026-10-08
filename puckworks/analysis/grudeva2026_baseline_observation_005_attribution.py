"""Frozen single-axis diagnostic reduction; no solver calls or qualification override."""
from __future__ import annotations

import argparse
import math
import os
from pathlib import Path

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_baseline_observation_005_diagnosis as diagnostic
from . import grudeva2026_baseline_observation_005_report as report

AXES = ('bed_fine', 'modes_fine', 'time_fine', 'combined')


def run_check(path, meta, observed, plan, matrix_hash):
    """Charged per-run safety/support check; retained accuracy failures may continue."""
    path = Path(path)
    reasons = report.check_run(meta, obs.controls(meta['row']), matrix_hash)
    binding = plan['attribution']['normal_binding']
    normal_path = path.parent/binding['file']
    if obs.sha(normal_path) != binding['sha256']:
        reasons.append('original normal identity mismatch')
    normal = obs.read_json(normal_path)
    same_environment = meta['environment'] == normal['environment']
    if not same_environment:
        reasons.append('original normal environment mismatch')
    result = dict(artifact_sha256=obs.sha(path), row=meta['row'], same_environment=same_environment,
                  qualification_override=False, reasons=reasons)
    if meta['row'] == 'control':
        equal = obs.canonical(meta['public_result']) == obs.canonical(normal['public_result'])
        result['neutrality'] = dict(exact_complete_result_equal=equal, same_environment=same_environment,
            observed_sha256=normal['public_result_sha256'], unobserved_sha256=meta['public_result_sha256'],
            passed=equal and same_environment)
        if meta['observed'] or not equal:
            reasons.append('unexplained normal/control neutrality mismatch')
    elif observed is None:
        reasons.append('complete observation unavailable')
    else:
        gates = report.numeric_gates(observed, meta)
        result.update(gates=gates, audits=observed['audits'])
        required = ('complete_status', 'solver_segments', 'horizon', 'events', 'activation_support',
            'required_times', 'independent_inventory_sums', 'public_inventory_algebra',
            'public_profile_reconstruction', 'public_cup_outlet_reconstruction', 'tail_weights_rates', 'cup_quadrature')
        reasons.extend('untrustworthy support/algebra: '+key for key in required if not gates[key])
        result['retained_accuracy_failures'] = [k for k, v in gates.items() if not v and k not in required]
        # observe_saved has safely validated every retained accepted/event/coefficient array.
        for segment in meta['segments']:
            if obs.sha(path.parent/segment['receipt_file']) != segment['receipt_sha256']:
                reasons.append('capture receipt identity mismatch')
        result['observation_sha256'] = obs.sha(path.with_name(path.stem+'-observations.json'))
    result['safe_to_continue'] = not reasons
    return result


def project_cell(faces, means, left, right):
    """Same piecewise polynomial: exact whole-cell amounts, integrated partial cells."""
    if not faces[0] <= left < right <= faces[-1]:
        raise ValueError('normal cell has no complete common physical support')
    boundaries = np.r_[left, faces[(faces > left) & (faces < right)], right]
    pieces = []
    for a, b in zip(boundaries[:-1], boundaries[1:]):
        j, _ = diagnostic.stencil(faces, (a+b)/2)
        whole = a == faces[j] and b == faces[j+1]
        if whole:
            amount = means[j]*(b-a)
        else:
            poly = diagnostic.moment_polynomial(faces, means, (a+b)/2)
            amount = diagnostic.polynomial_integral(poly, a, b)
        pieces.append(dict(left=float(a), right=float(b), cell=j, whole_cell=bool(whole), amount=float(amount)))
    return math.fsum(p['amount'] for p in pieces)/(right-left), pieces


def signed_interactions(changes):
    """Same point and representation only; no maximum subtraction."""
    return changes['combined']-sum(changes[k] for k in AXES[:3])


def point(tr, t, z):
    y, segment = tr.evaluate(t)
    front, _, modal = obs.state_fields(y, tr.n, tr.m)
    if front > 0 and z <= front:
        details, faces, means = diagnostic.point_record(tr, t, z)
        details['point_reconstruction_supported'] = True
        return details, faces, means
    _, grain, modes = obs.profiles(t, y, tr.n, tr.weights, tr.faces, np.array([z]), tr.arrival)
    activation = tr.activation(z)
    return (dict(t=t, z=z, front=front, grain_mean=float(grain[0]), activation=activation,
                 grain_age=None if activation is None else t-activation,
                 modal_contributions=tr.weights*modes[:, 0], point_reconstruction_supported=False),
            front*tr.faces, tr.weights @ modal)


def point_attribution(trajectories, t, z, origins):
    records = {name: point(tr, t, z) for name, tr in trajectories.items()}
    normal, normal_faces, normal_means = records['normal']
    normal_poly = (diagnostic.moment_polynomial(normal_faces, normal_means, z)
                   if normal['point_reconstruction_supported'] else None)
    result = dict(t=t, z=z, origins=origins, normal=normal, rows={}, direct_changes={}, common_changes={})
    for name in AXES:
        row, faces, means = records[name]
        direct = row['grain_mean']-normal['grain_mean']
        result['direct_changes'][name] = direct
        age = (normal['grain_age'] is not None and row['grain_age'] is not None
               and min(normal['grain_age'], row['grain_age']) >= .02)
        low, high = sorted((normal['front'], row['front']))
        exited = t >= max(trajectories['normal'].arrival, trajectories[name].arrival)
        spatial = (z < low-.008 or z > high+.008 or exited) and (t >= 1 or abs(z-min(t, 1)) > .008)
        entry = dict(point=row, delta_direct=direct,
                     original_masks=dict(grain_profile=bool(spatial and age), grain_history=bool(age)))
        if normal_poly is None:
            entry['common'] = dict(supported=False, reason='normal point has no active polynomial stencil')
        else:
            ids = normal_poly['indices']
            if not row['point_reconstruction_supported'] or normal_faces[ids[0]] < faces[0] or normal_faces[ids[-1]+1] > faces[-1]:
                entry['common'] = dict(supported=False, reason='entire normal stencil lacks common physical support')
            else:
                averages, pieces = zip(*(project_cell(faces, means, normal_faces[j], normal_faces[j+1]) for j in ids))
                averages = np.array(averages)
                common_value = float(averages @ normal_poly['weights'])
                normal_value = float(normal_poly['value'])
                reference_value = float(diagnostic.moment_polynomial(faces, means, z)['value'])
                common_delta = common_value-normal_value
                readout = reference_value-common_value
                result['common_changes'][name] = common_delta
                entry['common'] = dict(supported=True, reference='NORMAL_PHYSICAL_STENCIL_NOT_EXACT_TRUTH',
                    normal_cells=ids, normal_averages=normal_means[ids], projected_averages=averages,
                    average_changes=averages-normal_means[ids], delta_common=common_delta,
                    delta_reconstruction=readout, mean_first_direct=reference_value-normal_value,
                    closure=(reference_value-normal_value)-common_delta-readout,
                    point_grouping_residual=direct-(reference_value-normal_value), overlap_pieces=pieces)
        shared = trajectories['normal'].m-1
        assert np.array_equal(trajectories['normal'].weights[:shared], trajectories[name].weights[:shared])
        assert np.array_equal(trajectories['normal'].rates[:shared], trajectories[name].rates[:shared])
        base, other = normal['modal_contributions'], row['modal_contributions']
        resolved = other[:shared]-base[:shared]
        tail_delta = float(np.sum(other[shared:])-base[-1])
        entry['modes'] = dict(shared_resolved=shared, shared_changes=resolved,
            shared_sum=float(np.sum(resolved)), normal_tail=float(base[-1]),
            reference_additional_resolved=float(np.sum(other[shared:-1])), reference_tail=float(other[-1]),
            additional_and_tail_change=tail_delta, closure=direct-float(np.sum(resolved))-tail_delta)
        result['rows'][name] = entry
    result['nonadditivity_direct'] = signed_interactions(result['direct_changes'])
    if len(result['common_changes']) == len(AXES):
        result['nonadditivity_common'] = signed_interactions(result['common_changes'])
        vectors = {k:result['rows'][k]['common']['average_changes'] for k in AXES}
        result['nonadditivity_cell_averages'] = signed_interactions(vectors)
    else:
        result['nonadditivity_common'] = None
        result['common_unavailable_reason'] = 'one or more rows lacks full common physical stencil support'
    return diagnostic.array_json(result)


def checkpoint(path, result):
    # Partial stages are durable; JSON serialization precedes replacement.
    payload = obs.canonical(result)+'\n'
    temporary = path.with_suffix('.partial')
    with temporary.open('w') as f:
        f.write(payload); f.flush(); os.fsync(f.fileno())
    temporary.replace(path)


def reduce(folder, matrix, output):
    plan = obs.read_json(matrix)
    result = dict(task=obs.TASK, diagnostic_completion='INCOMPLETE', physical_validation='NOT_ESTABLISHED',
        matrix_sha256=obs.sha(matrix), source_sha256=obs.sha(__file__), qualification=None, points=[])
    checkpoint(output, result)
    result['qualification'] = report.report(folder, matrix)
    checkpoint(output, result)
    trajectories = {}
    try:
        for name in ('normal', *AXES):
            spec = plan['runs'][name]
            if result['qualification']['runs'][name]['reasons']:
                raise ValueError('untrustworthy row in reduction: '+name)
            trajectories[name] = obs.Trajectory(folder/spec['file'])
        locations = {(p['t'], p['z']): [p['name']] for p in plan['attribution']['points']}
        for name in AXES[:3]:
            for observable in ('grain_profiles', 'grain_histories'):
                metric = result['qualification']['refinements'][name][observable]
                if metric['max_absolute'] is None or metric['unavailable']:
                    raise ValueError('required full-support grain comparison unavailable')
                at = metric['location']
                locations.setdefault((at['t'], at['z']), []).append(name+'/'+observable+'/maximum')
        for (t, z), origins in locations.items():
            result['points'].append(point_attribution(trajectories, t, z, origins))
            checkpoint(output, result)
        result['diagnostic_completion'] = 'SINGLE_AXIS_ATTRIBUTION_EXECUTED_NOT_QUALIFICATION'
        result['historical_diagnosis_sha256'] = plan['attribution']['historical_diagnosis_sha256']
    finally:
        for tr in trajectories.values():
            tr.close()
    checkpoint(output, result)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-directory', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--allocation', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    spec = obs.read_json(args.allocation)
    if (spec['attempt'] != 'attribution-reduction' or spec['role'] != 'single_axis_reduction'
            or spec['matrix_sha256'] != obs.sha(args.matrix) or spec['source_sha256'] != obs.sha(__file__)
            or spec['output'] != args.output.name or os.environ.get('GRUDEVA005_ATTEMPT') != spec['attempt']):
        raise ValueError('frozen reduction allocation mismatch')
    with args.output.open('x'):
        pass
    try:
        result = reduce(args.runs_directory, args.matrix, args.output)
    except BaseException as exc:
        result = obs.read_json(args.output)
        result['failure'] = dict(type=type(exc).__name__, message=str(exc))
        checkpoint(args.output, result)
        raise
    print(result['diagnostic_completion'], result['qualification']['disposition'])
    return 0  # Completed diagnostic; the retained scientific report remains incomplete.


if __name__ == '__main__':
    raise SystemExit(main())

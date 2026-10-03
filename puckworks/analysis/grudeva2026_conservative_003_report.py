"""Deterministic offline 003 verification and saved-run reduction.

Only --local executes bounded elementary fixtures. Saved-run reduction does
not execute solvers; incomplete qualification returns non-success.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from . import grudeva2026_conservative_003 as core
from .grudeva2026_reference_002 import analytic_sphere, normalization_audit


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def local_qualification():
    ages = [.002, .02, .1, .3, .7]
    rows = []
    selected = None
    shifted = []
    for n in (800, 1600, 3200, 6400):
        radial = core.Radial(n, .7)
        for initial, boundary, slope in ((1.6, .2, 0.), (1.6, .2, .3), (.2, .2, .5), (1.4, 1.4, 0.)):
            actual, expected = [], []
            shell_flux_errors = []
            for age in ages:
                j = radial.advance(np.full((n, 1), initial), np.array([boundary]),
                                   np.array([boundary+slope*age]), np.ones(1), np.zeros(1), age)
                flux = float(radial.flux(j[:, 0], boundary+slope*age, .4))
                mean = float(radial.means(j)[0])
                actual.append([flux, mean])
                expected.append(analytic_sphere(age, initial, boundary, slope, diffusivity=.7, q_b=.4))
                shells = radial.shells(j)[:, 0]
                shell_flux = radial.op[-1]*(shells[-1]-boundary-slope*age)/(3*.4)
                shell_flux_errors.append(abs(flux-shell_flux))
            errors = np.max(abs(np.array(actual)-np.array(expected)), axis=0)
            rows.append({'shells': n, 'initial': initial, 'boundary': boundary, 'slope': slope,
                         'flux_error': float(errors[0]), 'mean_error': float(errors[1]),
                         'shell_surface_flux_reconstruction_error': float(max(shell_flux_errors)),
                         'weight_defect': radial.weight_defect,
                         'passed': bool(errors[0] <= 2e-4 and errors[1] <= 2e-5)})
        if all(row['passed'] for row in rows[-4:]) and selected is None:
            selected = n
        if n == 3200:
            for activation in (4.3, 15.3):
                history, previous = np.full((n, 1), 1.6), activation
                values = []
                for age in ages:
                    absolute = activation+age
                    history = radial.advance(history, np.array([.2+.3*(previous-activation)]),
                        np.array([.2+.3*age]), np.ones(1), np.zeros(1), absolute-previous)
                    values.append([float(radial.flux(history[:, 0], .2+.3*age, .4)), float(radial.means(history)[0])])
                    previous = absolute
                shifted.append(values)
    front_error = max(abs(((1-c)/(core.JUMP-core.CAPACITY*c))
                          *((core.JUMP-core.CAPACITY*c)/(1-c))-1) for c in (0., .2, .6, .95))
    # Actual coupled release/uptake on nonmatching physical volumes.
    radial = core.Radial(48)
    d, r = np.array([0., .013, .07, .19, .2]), np.array([0., .02, .045, .1, .15, .2])
    exchanges = []
    for initial, concentration in ((1.388, .2), (.2, .9), (.7, .7)):
        old = np.full((48, 4), initial)*np.diff(d)
        c0 = np.full(5, concentration)
        c1, j1, audit = core.coupled_exchange(radial, old, c0, d, r, .004)
        change_l = float(np.diff(r) @ (c1-c0))
        change_b = float(core.DELTA*sum(radial.means(j1-old)))
        residual = change_l*(1+core.BETA)+change_b
        allowance = core.ALGEBRA_RTOL*audit['scale']+audit['linear_residual']
        exchanges.append({'initial': initial, 'boundary': concentration, 'liquid_change': change_l,
                          'fines_change': core.BETA*change_l, 'boulder_change': change_b,
                          'residual': residual, 'allowance': allowance, **audit,
                          'passed': bool(abs(residual) <= allowance and audit['amount_residual'] <= allowance)})
    shift_error = float(np.max(abs(np.array(shifted[0])-np.array(shifted[1]))))
    return {'kind': 'LOCAL_NUMERICAL_QUALIFICATION', 'old_counterexample': core.old_counterexample(),
            'radial': rows, 'first_passing_shell_count': selected, 'front_relative_error': front_error,
            'actual_signed_exchange': exchanges, 'legacy_normalization': normalization_audit(),
            'shifted_activation_error': shift_error,
            'passed': bool(selected is not None and front_error <= 1e-12 and shift_error <= 1e-8
                           and all(r['passed'] for r in exchanges)),
            'core_sha256': sha(core.__file__), 'reporter_sha256': sha(__file__),
            'physical_validation': 'NOT_ESTABLISHED'}


def norm(values, include, available, budget):
    values, include, available = np.asarray(values), np.asarray(include), np.asarray(available)
    selected = include & available
    maximum = float(np.max(abs(values[selected]))) if np.any(selected) else None
    return {'max_absolute': maximum, 'budget': budget, 'included': int(np.sum(selected)),
            'excluded': int(np.sum(available & ~include)), 'unavailable': int(np.sum(~available)),
            'passed': bool(maximum is not None and maximum <= budget and np.all(available))}


def samples(run, requested):
    ts = np.array([x['t'] for x in run['observations']])
    indices = np.array([int(np.argmin(abs(ts-t))) for t in requested])
    available = abs(ts[indices]-requested) <= 2e-13
    return indices, available


def refinement(a, b):
    """No interpolation across events and no endpoint extension of missing times."""
    requested, z = core.observation_support(8.)
    ia, aa = samples(a, requested); ib, ab = samples(b, requested)
    available = aa & ab
    ar, br = np.asarray(a['records'])[ia], np.asarray(b['records'])[ib]
    no_events = a['arrival'] is None or b['arrival'] is None
    lo, hi = (0., 8.) if no_events else sorted([a['arrival'], b['arrival']])
    smooth = ((requested < lo-.025) | (requested > hi+.025)) & (abs(requested-1) > .025)
    out = {'outlet': norm(ar[:, 2]-br[:, 2], smooth, available & (not no_events), .001),
           'front': norm(ar[:, 1]-br[:, 1], np.ones(len(requested), bool), available, .001),
           'arrival': {'max_absolute': None if no_events else abs(a['arrival']-b['arrival']),
                       'included': 0 if no_events else 1, 'excluded': 0,
                       'unavailable': int(no_events), 'budget': .001,
                       'passed': bool(not no_events and abs(a['arrival']-b['arrival']) <= .001)}}
    az = np.asarray(a['z']); bz = np.asarray(b['z'])
    if not np.array_equal(az, z) or not np.array_equal(bz, z):
        raise ValueError('physical observation grid differs from frozen support')
    cp_a = np.asarray([a['observations'][k]['liquid_profile'] for k in ia])
    cp_b = np.asarray([b['observations'][k]['liquid_profile'] for k in ib])
    bp_a = np.asarray([a['observations'][k]['grain_profile'] for k in ia])
    bp_b = np.asarray([b['observations'][k]['grain_profile'] for k in ib])
    low = np.minimum(ar[:, 1], br[:, 1])[:, None]-.008
    high = np.maximum(ar[:, 1], br[:, 1])[:, None]+.008
    spatial = (z[None, :] < low) | (z[None, :] > high)
    # Once both fronts have exited there is no spatial desaturation jump to
    # mask at z=1. The outlet and endpoint grain history remain real support.
    if not no_events:
        spatial |= (requested >= hi)[:, None]
    # Wetting has an independent liquid/no-liquid jump, at identical location.
    spatial &= ((requested >= 1.)[:, None]
                | (abs(z[None, :]-np.minimum(requested, 1.)[:, None]) > .008))
    available_grid = np.broadcast_to(available[:, None], spatial.shape)
    liquid_support = spatial.copy()
    # The endpoint liquid sample is the outlet trace: removing the vanished
    # spatial front mask must not bypass its temporal event exclusion.
    liquid_support[:, z == 1.] &= smooth[:, None]
    out['liquid_profiles'] = norm(cp_a-cp_b, liquid_support, available_grid, .001)
    activation_a = np.array([np.nan if x is None else x for x in a['activation']])
    activation_b = np.array([np.nan if x is None else x for x in b['activation']])
    activation_available = np.isfinite(activation_a) & np.isfinite(activation_b)
    out['activation'] = norm(activation_a-activation_b, np.ones(len(z), bool), activation_available, .001)
    aged = requested[:, None]-np.maximum(activation_a, activation_b)[None, :] >= .02
    # Per-method empirical grain allowance, keeping 2e-5 analytical allocation
    # for each method out of the inherited total 5e-4 budget.
    out['grain_profiles'] = norm(bp_a-bp_b, spatial & aged,
                                 available_grid & activation_available[None, :], .00023)
    if 'grain_history' in a['observations'][0] and 'grain_history' in b['observations'][0]:
        ha = np.asarray([a['observations'][k]['grain_history'] for k in ia])
        hb = np.asarray([b['observations'][k]['grain_history'] for k in ib])
        ta = np.array([np.nan if x is None else x for x in a['grain_history_activation']])
        tb = np.array([np.nan if x is None else x for x in b['grain_history_activation']])
        history_available = available[:, None] & np.isfinite(ta+tb)[None, :]
        age_mask = requested[:, None]-np.maximum(ta, tb)[None, :] >= .02
        out['grain_histories'] = norm(ha-hb, age_mask, history_available, .00023)
    else:
        out['grain_histories'] = {'passed': False, 'reason': 'history observer unavailable',
                                  'included': 0, 'excluded': 0, 'unavailable': len(requested)*7,
                                  'max_absolute': None, 'budget': .00023}
    for k, name in ((3, 'cup'), (4, 'liquid_inventory'), (5, 'fines_inventory'), (6, 'boulder_inventory')):
        out[name] = norm(ar[:, k]-br[:, k], np.ones(len(requested), bool), available, 5e-5)
    out['passed'] = all(row['passed'] for row in out.values())
    out['allowance_kind'] = 'EMPIRICAL_REFINEMENT_DIFFERENCES_NOT_RIGOROUS_CONTINUUM_BOUNDS'
    return out


def audit_run(path):
    r = json.loads(path.read_text())
    records, accepted = np.asarray(r['records']), np.asarray(r['accepted'])
    if len(records) == 0 or len(accepted) == 0:
        return {'passed': False, 'reason': 'empty observations/evolution'}
    independent = []
    cell_quadrature = []
    for o in r['observations']:
        faces, c, grain = np.array(o['faces']), np.array(o['liquid_cells']), np.array(o['grain_integrals'])
        # Recompute each exact state integral independently of core phase helper.
        ic = sum((right-left)*value for left, right, value in zip(faces[:-1], faces[1:], c))
        ib = sum(grain)
        t, s = o['t'], faces[-1]
        independent.append([ic+min(t, 1)-s, 3.2*(ic+1.388*(1-s)), .8*(ib+1.388*(1-s))])
        # Two-point Gauss quadrature of the cell-average reconstruction. This
        # verifies discrete integration only, never continuum profile accuracy.
        gauss = sum((right-left)*(.5*value+.5*value) for left, right, value in zip(faces[:-1], faces[1:], c))
        cell_quadrature.append(abs(gauss-ic))
    recomputed = np.array(independent)
    residual = (recomputed.sum(axis=1)+records[:, 3]-5.552)/5.552
    allowance = core.ALGEBRA_RTOL*accepted[:, 10]+accepted[:, 9]
    scaled = np.divide(abs(accepted[:, 7]), allowance, out=np.zeros(len(allowance)), where=allowance > 0)
    linear_allowance = core.ALGEBRA_RTOL*accepted[:, 10]
    linear_scaled = np.divide(abs(accepted[:, 9]), linear_allowance,
                              out=np.zeros(len(allowance)), where=linear_allowance > 0)
    cup_quad = 0.
    previous_t, previous_trace = 0., 0.
    max_cup_error = 0.
    for row in accepted:
        t, trace = row[0], row[11]
        if previous_t >= 1:
            if r['arrival'] is None or previous_t < r['arrival']:
                cup_quad += t-previous_t
            else:
                # Independent two-point Gaussian quadrature of the accepted
                # piecewise linear outlet, split at first drip and front exit.
                node = 1/np.sqrt(3)
                values = [(previous_trace+trace)/2+(trace-previous_trace)*x/2 for x in (-node, node)]
                cup_quad += (t-previous_t)*sum(values)/2
        max_cup_error = max(max_cup_error, abs(cup_quad-row[2]))
        previous_t, previous_trace = t, trace
    source_matches = r.get('source_sha256') == sha(core.__file__)
    radial_matches = r.get('radial_source_sha256') == sha(Path(core.__file__).with_name('grudeva2026_reference_002.py'))
    terminal = float(records[-1, 0]) == r['controls']['horizon'] == 8.
    bounds = r['aqueous_min'] >= -1e-8 and r['aqueous_max'] <= 1+1e-8 and r['grain_mean_min'] >= -1e-8
    passed = (r['status'] == 'EXECUTED_UNQUALIFIED' and source_matches and radial_matches and terminal and bounds
              and max(abs(accepted[:, 6])) <= 1e-6 and max(abs(residual)) <= 1e-6
              and max(scaled) <= 1 and max(linear_scaled) <= 1
              and np.max(abs(recomputed-records[:, 4:7])) <= 5e-13
              and np.max(accepted[:, 1]-np.minimum(accepted[:, 0], 1.)) <= 1e-10)
    return {'controls': r['controls'], 'artifact_sha256': sha(path), 'core_sha256': r.get('source_sha256'),
            'current_core_matches': source_matches, 'radial_source_matches': radial_matches,
            'status': r['status'], 'reason': r['reason'], 'arrival': r['arrival'],
            'terminal_available': terminal, 'last_observed_time': float(records[-1, 0]),
            'accepted_steps': len(accepted), 'saved_states': len(records), 'bounds_passed': bool(bounds),
            'aqueous_min': r['aqueous_min'], 'aqueous_max': r['aqueous_max'], 'grain_mean_min': r['grain_mean_min'],
            'max_global_normalized_residual': float(max(abs(accepted[:, 6]))),
            'independent_observation_residual': float(max(abs(residual))),
            'phase_reconstruction_error': float(np.max(abs(recomputed-records[:, 4:7]))),
            'algebra_allowance_max_fraction': float(max(scaled)), 'max_transfer_amount_residual': float(max(abs(accepted[:, 7]))),
            'linear_solve_roundoff_max_fraction': float(max(linear_scaled)),
            'max_front_amount_residual': float(max(abs(accepted[:, 8]))),
            'independent_shell_integral_error': r['independent_shell_integral_error'],
            'independent_cell_quadrature_error': float(max(cell_quadrature)),
            'independent_split_cup_quadrature_error': max_cup_error,
            'quadrature_scope': 'exact discrete reconstruction; continuum allowance comes from refinement',
            'terminal_phase_states': records[-1, 4:7].tolist(), 'terminal_cup': float(records[-1, 3]),
            'passed': bool(passed)}


def reduce_saved(folder, matrix_path, baseline_dir):
    from .grudeva2026_reference_002_report import reuse_baseline
    plan = json.loads(matrix_path.read_text())
    raw, audits = {}, {}
    for name, row in plan['runs'].items():
        path = folder/row['file']
        if not path.exists():
            audits[name] = {'passed': False, 'reason': 'run artifact unavailable'}
            continue
        raw[name] = json.loads(path.read_text())
        if raw[name]['controls'] != row['controls']:
            raise ValueError('frozen controls mismatch: '+name)
        audits[name] = audit_run(path)
    refinements = {name: refinement(raw['normal'], raw[name])
                   for name in ('bed_fine', 'radial_fine', 'time_fine', 'combined') if name in raw and 'normal' in raw}
    local_path, limit_path = folder/plan['local'], folder/plan['limit']
    local = json.loads(local_path.read_text())
    limit = json.loads(limit_path.read_text())
    limit_audit = audit_run(limit_path)
    limit_records = np.asarray(limit['records'])
    limit_error = None if limit['arrival'] is None else abs(limit['arrival']/5.4416-1)
    limit_audit['front_relative_error'] = limit_error
    limit_liquid = max(max(abs(np.array(o['liquid_cells']))) for o in limit['observations'])
    limit_grain = max(max(abs(np.array(o['grain_integrals'])/np.diff(o['faces'])-1.388))
                      for o in limit['observations'] if o['faces'][-1] > 0)
    limit_audit.update({'liquid_max_absolute': float(limit_liquid), 'grain_mean_error': float(limit_grain)})
    limit_audit['passed'] = bool(limit_audit['passed'] and limit_error is not None and limit_error <= 1e-12
                             and abs(limit_records[-1, 3]-4.4416) <= 1e-12
                             and limit_liquid <= 1e-12 and limit_grain <= 1e-12
                             and max(abs(limit_records[:, 1]-np.minimum(limit_records[:, 0]/5.4416, 1.))) <= 1e-12)
    local_ok = local['passed'] and local['core_sha256'] == sha(core.__file__)
    qualified_shells = {r['shells'] for r in local['radial']
                        if all(q['passed'] for q in local['radial'] if q['shells'] == r['shells'])}
    local_ok &= all(row['controls']['shells'] in qualified_shells for row in plan['runs'].values())
    qualified = (local_ok and limit_audit['passed'] and len(audits) == 5 and len(refinements) == 4
                 and all(row['passed'] for row in audits.values()) and all(row['passed'] for row in refinements.values()))
    ledger = [json.loads(line) for line in (folder/'invocations.jsonl').read_text().splitlines()]
    starts = {row['name']: row for row in ledger if row['event'] == 'start'}
    attempts = []
    for end in [row for row in ledger if row['event'] == 'end']:
        start = starts[end['name']]
        output_path = Path(start['command'][start['command'].index('--output')+1])
        executed = json.loads(output_path.read_text()) if output_path.exists() else {}
        result_status = executed.get('status', 'LOCAL_PASS' if executed.get('passed') else 'FAILED_OR_UNAVAILABLE')
        attempts.append({k: start[k] for k in ('name', 'kind', 'phase', 'source_hashes')} |
                        {'start_utc': start['utc'], 'end_utc': end['utc'], 'seconds': end['seconds'],
                         'exit_code': end['exit_code'], 'log_sha256': end['log_sha256'],
                         'result_status': result_status, 'reason': executed.get('reason'),
                         'controls': executed.get('controls'),
                         'artifact_file': output_path.name,
                         'artifact_sha256': sha(output_path) if output_path.exists() else None,
                         'last_observed_time': executed['records'][-1][0] if executed.get('records') else None,
                         'command': ['python']+[('$GRUDEVA_EVIDENCE/'+Path(token).name
                                                 if str(folder) in token else token)
                                                for token in start['command'][1:]]})
    spent = sum(row['seconds'] for row in attempts)
    full = sum(row['kind'] == 'full' for row in attempts)
    root = Path(__file__).parents[2]
    baseline = reuse_baseline(root, baseline_dir)
    return {'task': 'MODEL-GRUDEVA2026-CONSERVATIVE-003', 'governance': 'G2',
            'change_declaration': 'NUMERICAL_METHOD_CHANGE',
            'disposition': 'ALTERNATIVE_QUALIFIED_COMPARISON_PENDING' if qualified else 'LOCAL_REPAIR_COUPLED_QUALIFICATION_INCOMPLETE',
            'transfer_consistency': 'PASS' if local_ok and all(row.get('algebra_allowance_max_fraction', 2) <= 1 for row in audits.values()) else 'INCOMPLETE',
            'coupled_qualification': 'PASS' if qualified else 'INCOMPLETE',
            'alternative_qualified': bool(qualified), 'local_qualification': local,
            'runs': audits, 'refinements': refinements, 'zero_diffusion_limit': limit_audit,
            'baseline_raw_state_qualification': 'UNAVAILABLE_NOT_EXECUTED',
            'baseline_observer': 'PREPARED_SYNTHETIC_RETURN_SEAM_TEST_ONLY',
            'inter_method_agreement': {'status': 'UNAVAILABLE', 'reason': 'Both coupled and raw observation qualifications required',
                                     'included': 0, 'excluded': 0, 'unavailable': 'ENTIRE_REQUIRED_SUPPORT'},
            'earliest_qualified_inter_method_divergence': 'UNAVAILABLE',
            'baseline_preservation': baseline,
            'figures': {'figure3': 'BASELINE_HISTORICAL_FAIL_UNCHANGED_ALTERNATIVE_NOT_SCORED',
                        'figure4': 'BASELINE_HISTORICAL_FAIL_UNCHANGED_ALTERNATIVE_NOT_SCORED',
                        'figure5': 'FIG5_REFERENCE_INCOMPLETE'},
            'attempts': attempts, 'resources': {'full_horizon_invocations': full, 'short_invocations': len(attempts)-full,
                         'aggregate_numerical_seconds': spent, 'unresolved_starts': len(starts)-len(attempts),
                         'failed_full_invocations': sum(r['kind'] == 'full' and r['result_status'] != 'EXECUTED_UNQUALIFIED' for r in attempts),
                         'full_limit': 24, 'aggregate_limit_seconds': 3600, 'per_run_limit_seconds': 900,
                         'memory_limit_bytes': 2*1024**3, 'within_total_limits': full <= 24 and spent <= 3600},
            'resource_enforcement': {'controller_sha256': sha(folder/'invoke.py'),
                                     'method': 'parent subprocess timeout and child RLIMIT_AS=2 GiB; ledger fsynced before invocation',
                                     'measured_peak_rss': 'NOT_RECORDED; address-space ceiling enforced for every numerical process'},
            'environment': json.loads((folder/'environment.json').read_text()),
            'source_hashes': {str(path.relative_to(root)): sha(path) for path in sorted((root/'puckworks/analysis').glob('grudeva2026_*003*.py'))},
            'plan_sha256': sha(matrix_path), 'physical_validation': 'NOT_ESTABLISHED',
            'independent_review': 'PENDING_EXACT_HEAD', 'hosted_ci': 'PENDING', 'software_qa': 'REPORTED_SEPARATELY',
            'automatic_successor': 'NONE'}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--local', action='store_true')
    ap.add_argument('--runs-directory', type=Path)
    ap.add_argument('--matrix', type=Path)
    ap.add_argument('--baseline-directory', type=Path)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args(argv)
    if args.local:
        result = local_qualification()
    else:
        if not all((args.runs_directory, args.matrix, args.baseline_directory)):
            ap.error('saved reduction requires runs-directory, matrix and baseline-directory')
        result = reduce_saved(args.runs_directory, args.matrix, args.baseline_directory)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2, allow_nan=False)+'\n')
    print(json.dumps({k: result[k] for k in ('passed', 'first_passing_shell_count', 'disposition') if k in result}))
    return (0 if result['passed'] else 2) if args.local else 2


if __name__ == '__main__':
    raise SystemExit(main())

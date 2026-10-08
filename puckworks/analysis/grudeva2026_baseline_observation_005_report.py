"""Failure-first offline 005 qualification. This module never launches a solver."""
from __future__ import annotations

import argparse
import json
import zipfile
from pathlib import Path

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_conservative_003_report as inherited

QUALIFIED = 'BASELINE_RAW_OBSERVATION_NUMERICALLY_QUALIFIED_ON_DECLARED_CASES'
BASELINE_INCOMPLETE = 'BASELINE_QUALIFICATION_INCOMPLETE'
OBSERVER_INCOMPLETE = 'OBSERVER_QUALIFICATION_INCOMPLETE'
RESOURCE_POLICY = '005-owner-8gib-20261008'
OLD_CONTROLLER_SHA256 = '6de6f55611ceaea5be65dd4f2027c4aefaff92cd9e22f78f1aa7f1576aa37341'
MEMORY_8GIB = 8*1024**3

BUDGETS = dict(outlet=.001, liquid_profiles=.001, front=.001, arrival=.001,
               activation=.001, grain_profiles=.00023, grain_histories=.00023,
               cup=5e-5, liquid_inventory=5e-5, fines_inventory=5e-5, boulder_inventory=5e-5)


def metric(values, include, available, allowance, times=None, z=None):
    values = np.asarray(values, float)
    include = np.broadcast_to(include, values.shape)
    available = np.broadcast_to(available, values.shape) & np.isfinite(values)
    result = inherited.norm(values, include, available, allowance)
    result['requested'] = int(values.size)
    result['location'] = None
    selected = include & available
    if np.any(selected):
        k = np.unravel_index(np.argmax(np.where(selected, abs(values), -1)), values.shape)
        result['location'] = {'index': [int(i) for i in k]}
        if times is not None:
            result['location']['t'] = float(times[k[0]])
        if z is not None:
            result['location']['z'] = float(z[k[-1]])
    return result


def refinement(a, b):
    """Unchanged inherited acceptance; add counts and locations, checking parity."""
    expected = inherited.refinement(a, b)
    t, z = obs.observation_support(8.)
    ia, aa = inherited.samples(a, t)
    ib, ab = inherited.samples(b, t)
    available = aa & ab
    ar, br = np.asarray(a['records'])[ia], np.asarray(b['records'])[ib]
    lo, hi = sorted([a['arrival'], b['arrival']])
    smooth = ((t < lo-.025) | (t > hi+.025)) & (abs(t-1) > .025)
    spatial = ((z[None, :] < np.minimum(ar[:, 1], br[:, 1])[:, None]-.008) |
               (z[None, :] > np.maximum(ar[:, 1], br[:, 1])[:, None]+.008))
    spatial |= (t >= hi)[:, None]
    spatial &= ((t >= 1)[:, None] | (abs(z[None, :]-np.minimum(t, 1)[:, None]) > .008))
    liquid = spatial.copy()
    liquid[:, z == 1] &= smooth[:, None]
    act_a, act_b = np.asarray(a['activation'], float), np.asarray(b['activation'], float)
    age = t[:, None]-np.maximum(act_a, act_b)[None, :] >= .02
    rows = {}
    rows['outlet'] = metric(ar[:, 2]-br[:, 2], smooth, available, .001, t)
    rows['front'] = metric(ar[:, 1]-br[:, 1], True, available, .001, t)
    rows['arrival'] = metric(np.array([a['arrival']-b['arrival']]), True, True, .001)
    rows['arrival']['location'] = {'normal_t': a['arrival'], 'refined_t': b['arrival'], 'z': 1.}
    for key, field, mask, budget in [('liquid_profiles', 'liquid_profile', liquid, .001),
                                     ('grain_profiles', 'grain_profile', spatial & age, .00023)]:
        x = np.array([a['observations'][k][field] for k in ia])
        y = np.array([b['observations'][k][field] for k in ib])
        rows[key] = metric(x-y, mask, available[:, None], budget, t, z)
    rows['activation'] = metric(act_a-act_b, True, np.isfinite(act_a+act_b), .001, z=z)
    ha, hb = np.array(a['grain_history_activation']), np.array(b['grain_history_activation'])
    aged = t[:, None]-np.maximum(ha, hb)[None, :] >= .02
    x = np.array([a['observations'][k]['grain_history'] for k in ia])
    y = np.array([b['observations'][k]['grain_history'] for k in ib])
    rows['grain_histories'] = metric(x-y, aged, available[:, None] & np.isfinite(ha+hb)[None, :], .00023, t, obs.HISTORY_Z)
    for k, name in [(3, 'cup'), (4, 'liquid_inventory'), (5, 'fines_inventory'), (6, 'boulder_inventory')]:
        rows[name] = metric(ar[:, k]-br[:, k], True, available, 5e-5, t)
    for name, row in rows.items():
        for key in ('max_absolute', 'budget', 'included', 'excluded', 'unavailable', 'passed'):
            if row[key] != expected[name][key]:
                raise ValueError('inherited mask/refinement disagreement: '+name+'/'+key)
    return rows


def unavailable_metrics(reason):
    sizes = dict(outlet=395, liquid_profiles=395*220, front=395, arrival=1, activation=220,
                 grain_profiles=395*220, grain_histories=395*7, cup=395,
                 liquid_inventory=395, fines_inventory=395, boulder_inventory=395)
    return {k: dict(requested=sizes[k], included=0, excluded=0, unavailable=sizes[k],
                    max_absolute=None, location=None, budget=v, passed=False, reason=reason)
            for k, v in BUDGETS.items()}


def resource_audit(folder):
    reasons = []
    path = folder/'invocations.jsonl'
    if not path.exists():
        return dict(passed=False, reasons=['attempt ledger unavailable'], full=0, short=0, seconds=0.)
    try:
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        obs.canonical(rows)
        if any(not isinstance(r, dict) for r in rows):
            raise ValueError('attempt must be an object')
    except (ValueError, TypeError) as exc:
        return dict(passed=False, reasons=['malformed attempt ledger: '+str(exc)], full=0, short=0, seconds=0.)
    amendment = None
    persistence = None
    prior_persistence_names = set()
    historical_names = set()
    if (folder/'resource-amendment.json').exists():
        try:
            amendment = obs.read_json(folder/'resource-amendment.json')
            historical = folder/'invocations-before-8gib.jsonl'
            previous = obs.read_json(folder/'MATRIX-2gib-reviewed.json')
            historical_rows = [json.loads(v) for v in historical.read_text().splitlines()]
            historical_names = {v['name'] for v in historical_rows if v['event'] == 'start'}
            controller_source = Path(obs.__file__).parents[2]/'tools/grudeva2026_baseline_observation_005_invoke.py'
            current_controller = amendment['controller_sha256']
            if (folder/'persistence-amendment.json').exists():
                persistence = obs.read_json(folder/'persistence-amendment.json')
                prefix = folder/'invocations-before-persistence-controller.jsonl'
                prior_persistence_names = {r['name'] for r in map(json.loads, prefix.read_text().splitlines())
                                           if r['event'] == 'start'}
                if (persistence['previous_controller_sha256'] != current_controller
                        or obs.sha(folder/'invoke-before-persistence.py') != current_controller
                        or persistence['resource_amendment_sha256'] != obs.sha(folder/'resource-amendment.json')
                        or persistence['historical_ledger_sha256'] != obs.sha(prefix)
                        or not path.read_bytes().startswith(prefix.read_bytes())):
                    reasons.append('persistence controller/history identity mismatch')
                current_controller = persistence['controller_sha256']
            if (amendment['policy'] != RESOURCE_POLICY or amendment['memory_bytes'] != MEMORY_8GIB
                    or amendment['old_controller_sha256'] != OLD_CONTROLLER_SHA256
                    or obs.sha(folder/'invoke-2gib.py') != OLD_CONTROLLER_SHA256
                    or obs.sha(historical) != amendment['historical_ledger_sha256']
                    or not path.read_bytes().startswith(historical.read_bytes())
                    or obs.sha(folder/'invoke.py') != current_controller
                    or obs.sha(controller_source) != current_controller
                    or previous['controller_sha256'] != OLD_CONTROLLER_SHA256
                    or obs.sha(folder/'MATRIX-2gib-reviewed.json') != amendment['historical_matrix_sha256']
                    or obs.sha(folder/'RESULTS-2gib-reviewed.json') != amendment['historical_result_sha256']):
                reasons.append('resource policy/controller/history identity mismatch')
        except (KeyError, ValueError, TypeError, OSError) as exc:
            reasons.append('resource amendment unavailable/malformed: '+str(exc))
    starts, ends = {}, {}
    for row in rows:
        group = starts if row.get('event') == 'start' else ends if row.get('event') == 'end' else None
        if group is None or not isinstance(row.get('name'), str) or row['name'] in group:
            reasons.append('malformed/duplicate attempt event')
            continue
        if group is ends and row['name'] not in starts:
            reasons.append('end without prior start: '+row['name'])
        if group is starts and starts.keys() != ends.keys():
            reasons.append('overlapping or unresolved earlier start: '+row['name'])
        group[row['name']] = row
    if starts.keys() != ends.keys():
        reasons.append('unresolved attempt starts/ends')
    for name, start in starts.items():
        new = amendment is not None and name not in historical_names
        memory = MEMORY_8GIB if new else 2*1024**3
        try:
            if (not 0 < start.get('time_ceiling', 301) <= 300 or start.get('memory_bytes') != memory
                    or start.get('phase') not in ('development', 'final', 'correction')):
                reasons.append('invocation limits/phase unverified: '+name)
            if new:
                expected_controller = (persistence['controller_sha256']
                    if persistence and name not in prior_persistence_names else amendment['controller_sha256'])
                if (start.get('resource_policy') != RESOURCE_POLICY
                        or start.get('controller_sha256') != expected_controller
                        or start.get('resource_amendment_sha256') != obs.sha(folder/'resource-amendment.json')):
                    reasons.append('attempt policy/controller identity mismatch: '+name)
                end = ends.get(name, {})
                if end and end.get('enforced_rlimit_as') != [MEMORY_8GIB, MEMORY_8GIB]:
                    reasons.append('actual child address-space enforcement unverified: '+name)
                allocation = folder/start.get('allocation_file', '')
                if not allocation.is_file() or obs.sha(allocation) != start.get('allocation_sha256'):
                    reasons.append('attempt allocation identity mismatch: '+name)
                elif persistence and name not in prior_persistence_names:
                    spec = obs.read_json(allocation)
                    if (spec.get('controller_sha256') != expected_controller
                            or spec.get('persistence_amendment_sha256') != obs.sha(folder/'persistence-amendment.json')):
                        reasons.append('persistence attempt/controller binding mismatch: '+name)
                    if start.get('phase') == 'correction' and (name != 'combined-persistence-recapture'
                            or start.get('kind') != 'full' or spec.get('role') != 'combined_persistence_recapture'):
                        reasons.append('unauthorized corrective recapture: '+name)
            elif any(k in start for k in ('resource_policy', 'resource_amendment_sha256')):
                reasons.append('historical attempt retroactively relabeled: '+name)
            if ends.get(name, {}).get('peak_rss_bytes', 0) > memory:
                reasons.append('attempt memory ceiling exceeded: '+name)
        except (ValueError, TypeError, OSError) as exc:
            reasons.append('malformed attempt limits: '+name+': '+str(exc))
    for name, end in ends.items():
        if any(not isinstance(end.get(k), (int, float)) or isinstance(end.get(k), bool)
               for k in ('seconds', 'peak_rss_bytes')):
            return dict(passed=False, reasons=reasons+['malformed resource measurement: '+name],
                        full=sum(r.get('kind') == 'full' for r in starts.values()),
                        short=sum(r.get('kind') == 'short' for r in starts.values()), seconds=0.,
                        starts=starts, ends=ends)
    primary = [name for name, start in starts.items() if start.get('phase') != 'correction']
    if (sum(starts[name].get('kind') == 'full' for name in primary) > 7
            or sum(ends.get(name, {}).get('seconds', 0) for name in primary) > 900):
        reasons.append('three-slot/300-second correction reserve violated')
    full = sum(r.get('kind') == 'full' for r in starts.values())
    short = sum(r.get('kind') == 'short' for r in starts.values())
    if full+short != len(starts):
        reasons.append('unrecognized invocation kind')
    seconds = sum(r.get('seconds', -1) for r in ends.values())
    peak = max([r.get('peak_rss_bytes', 0) for r in ends.values()] or [0])
    maximum = max([r.get('seconds', 0) for r in ends.values()] or [0])
    if full > 10 or short > 20 or seconds > 1200 or maximum > 300:
        reasons.append('resource ceiling exceeded')
    for name, end in ends.items():
        if end.get('seconds', -1) < 0 or end.get('peak_rss_bytes', -1) < 0:
            reasons.append('missing resource measurement: '+name)
        log = folder/(name+'.log')
        if not log.exists() or obs.sha(log) != end.get('log_sha256'):
            reasons.append('attempt log identity mismatch: '+name)
    return dict(passed=not reasons, reasons=reasons, full=full, short=short, seconds=seconds,
                maximum_seconds=maximum, peak_rss_bytes=peak,
                starts=starts, ends=ends, remaining_full=10-full, remaining_short=20-short,
                remaining_seconds=1200-seconds)


def captured_matrix_hash(folder, plan, specification, current_hash):
    """Permit a changed allocation receipt only with identical scientific fields."""
    binding = specification.get('captured_matrix')
    if binding is None:
        return current_hash
    name = binding['file']
    if Path(name).name != name:
        raise ValueError('invalid captured matrix filename')
    path = folder/name
    if obs.sha(path) != binding['sha256']:
        raise ValueError('captured matrix identity mismatch')
    previous = obs.read_json(path)
    for key in ('sources', 'canonical_parameters', 'request_hashes', 'budgets', 'numerical_allocations'):
        if key not in previous or previous[key] != plan.get(key):
            raise ValueError('captured matrix scientific identity changed: '+key)
    for name in [*obs.ROWS, 'repeat', 'control']:
        for key in ('controls', 'horizon', 'observed'):
            if previous['runs'][name][key] != plan['runs'][name][key]:
                raise ValueError('captured matrix scientific row changed')
    if previous.get('resource_amendment', {}).get('binding_sha256') != plan.get('resource_amendment', {}).get('binding_sha256'):
        raise ValueError('captured matrix resource amendment changed')
    return binding['sha256']


def check_run(meta, expected, matrix_hash):
    reasons = []
    if meta.get('sources') != obs.sources():
        reasons.append('source identity mismatch')
    if meta.get('controls') != expected:
        reasons.append('configuration mismatch')
    from puckworks.models.grudeva2026.reduced import Parameters
    from dataclasses import asdict
    if meta.get('parameters') != asdict(Parameters()):
        reasons.append('canonical parameter mismatch')
    request = obs.requests()
    if meta.get('requests') != request or meta.get('request_hashes') != {k: obs.digest(v) for k, v in request.items()}:
        reasons.append('public/diagnostic support identity mismatch')
    if meta.get('matrix_sha256') != matrix_hash:
        reasons.append('matrix identity mismatch')
    public = meta.get('public_result', {})
    if obs.digest(public) != meta.get('public_result_sha256'):
        reasons.append('public Result identity mismatch')
    if public.get('controls') != expected or public.get('parameters') != meta.get('parameters'):
        reasons.append('public Result configuration mismatch')
    if meta.get('observed'):
        if not meta.get('restored') or not meta.get('public_result_unchanged_after_capture'):
            reasons.append('capture restoration/Result immutability unresolved')
        if not meta.get('solve_invocations') or meta.get('solve_invocations') != meta.get('returned'):
            reasons.append('not every original solver invocation returned')
        for s in meta.get('segments', []):
            if 'unavailable_reason' in s:
                reasons.append('segment unavailable: '+s['unavailable_reason'])
            if s.get('persistence_schema') != '005.segment-persistence.v2' or any(
                    s.get(k) != 'PASS' for k in ('capture_outcome', 'artifact_integrity', 'array_fidelity', 'numerical_replay')):
                reasons.append('segment persistence/fidelity/replay incomplete')
            replay = s.get('live_replay', {})
            if replay.get('allowance_fraction', 2) > 1:
                reasons.append('live dense replay failed or unavailable')
            if max(replay.get('accepted_state_error', 1), replay.get('event_state_error', 1)) > obs.ALGEBRA*8:
                reasons.append('dense replay accepted/event agreement failed or unavailable')
    return reasons


def numeric_gates(run, meta):
    a = run['audits']
    public = meta['public_result']
    gates = {
        'complete_status': public['status'] == 'COMPLETED',
        'solver_segments': all(s.get('success') for s in meta['segments']),
        'horizon': a['horizon'] == 8.,
        'events': len(run['events']) == 2 and run['arrival'] is not None,
        'activation_support': all(t is not None for t in run['activation']+run['grain_history_activation']),
        'required_times': not run['unavailable_times'],
        'conservation': a['max_normalized_conservation'] <= 1e-6,
        'aqueous_bounds': a['aqueous_min'] >= -1e-8 and a['aqueous_max'] <= 1+1e-8,
        'grain_bounds': a['grain_mean_min'] >= -1e-8,
        'phase_bounds': a['phase_min'] >= -1e-8,
        'front_support': a['front_wet_excess'] <= 1e-10 and a['front_decrease'] <= 1e-10,
        'cup_quadrature': a['cup_quadrature_refinement_max'] <= 1e-10,
        'cup_state_integral': a['cup_state_integral_max'] + a['cup_quadrature_refinement_max'] <= 5e-5,
        'independent_inventory_sums': a['independent_sum_allowance_fraction'] <= 1,
        'public_inventory_algebra': a['public_inventory_allowance_fraction'] <= 1,
        'public_profile_reconstruction': a['public_profile_reconstruction_error'] <= obs.ALGEBRA*4,
        'public_cup_outlet_reconstruction': max(a['public_cup_error'], a['public_outlet_error']) <= obs.ALGEBRA*4,
        'diagnostic_inlet': a['diagnostic_inlet_mean_error'] <= 2e-5,
        'tail_weights_rates': max(a['spectrum']['weight_error'], a['spectrum']['rate_relative_error']) <= obs.ALGEBRA,
    }
    for field in ('liquid_profile', 'grain_profile', 'grain_history'):
        bound = a.get('diagnostic_bounds', {}).get(field, {})
        gates['diagnostic_'+field+'_bounds'] = (bound.get('included', 0) > 0
            and bound.get('minimum') is not None and bound['minimum'] >= -1e-8
            and (field != 'liquid_profile' or bound.get('maximum', float('inf')) <= 1+1e-8))
    return {k: bool(v) for k, v in gates.items()}


def fixture_audit(folder, plan):
    binding = plan.get('fixtures', {})
    path = folder/binding.get('file', 'fixtures.json')
    reasons, gates = [], {}
    if not path.exists():
        return dict(passed=False, reasons=['independent numerical fixtures unavailable'], gates={})
    r = obs.read_json(path)
    if obs.sha(path) != binding.get('sha256') or r.get('sources') != obs.sources():
        reasons.append('fixture artifact/source identity mismatch')
    required = {'polynomial': (90, obs.ALGEBRA*4), 'history': (61, 2e-5),
                'kernel_mean_32': (20, 2e-5), 'kernel_flux_32': (20, 2e-4),
                'kernel_mean_64': (20, 2e-5), 'kernel_flux_64': (20, 2e-4),
                'dense': (12, obs.ALGEBRA*4), 'cup': (14, 1e-10)}
    for key, (count, allowance) in required.items():
        try:
            row = r['fixtures'][key]
            actual, expected = np.asarray(row['actual'], float), np.asarray(row['expected'], float)
            if actual.ndim != 1 or actual.shape != expected.shape or not len(actual) or (count is not None and len(actual) != count):
                raise ValueError('fixture shape/support mismatch')
            gates[key] = metric(actual-expected, True, np.isfinite(actual+expected), allowance)
            if not gates[key]['passed']:
                reasons.append('independent fixture failed: '+key)
        except (KeyError, ValueError, TypeError) as exc:
            reasons.append(key+': '+str(exc))
    test_source = Path(obs.__file__).parents[2]/'tests/test_grudeva2026_baseline_observation_005.py'
    if r.get('fixture_source_sha256') != obs.sha(test_source):
        reasons.append('independent fixture implementation identity mismatch')
    if r.get('negative_control_error', 0) <= .01:
        reasons.append('moving-index negative control did not discriminate')
    return dict(passed=not reasons, reasons=reasons, gates=gates)


def report(folder, matrix):
    folder, matrix = Path(folder), Path(matrix)
    plan = obs.read_json(matrix)
    matrix_hash = obs.sha(matrix)
    reasons, blocks = [], []
    if plan.get('sources') != obs.sources() or plan.get('reporter_sha256') != obs.sha(__file__):
        blocks.append('SOURCE_IDENTITY_BLOCKED')
        reasons.append('matrix source/reporter identities do not match current implementation')
    controller = folder/'invoke.py'
    if not controller.exists() or obs.sha(controller) != plan.get('controller_sha256'):
        blocks.append('CONTROLLER_IDENTITY_BLOCKED')
        reasons.append('external controller identity unavailable or mismatched')
    if plan.get('request_hashes') != {k: obs.digest(v) for k, v in obs.requests().items()}:
        blocks.append('SUPPORT_IDENTITY_BLOCKED')
        reasons.append('matrix request identities differ')
    resources = resource_audit(folder)
    if not resources['passed']:
        blocks.append('RESOURCE_ACCOUNTING_BLOCKED')
        reasons.extend(resources['reasons'])
    feasibility = plan.get('feasibility', {})
    if feasibility.get('disposition') != 'FEASIBLE':
        blocks.append('RESOURCE_FEASIBILITY_BLOCKED')
    if feasibility.get('execution_block') in ('OBSERVER_CAPTURE_IDENTITY_BLOCKED', 'OBSERVER_DIAGNOSTIC_INLET_BLOCKED'):
        blocks.append(feasibility['execution_block'])
    fixtures = fixture_audit(folder, plan)
    reasons.extend(fixtures['reasons'])
    raw, observed, runs = {}, {}, {}
    for name in [*obs.ROWS, 'repeat', 'control']:
        specification = plan.get('runs', {}).get(name, {})
        path = folder/specification.get('file', name+'.json')
        failures = []
        if specification.get('controls') != obs.controls(name):
            failures.append('matrix row controls differ from declared row')
        if not path.exists():
            failures.append('mandatory run artifact unavailable')
        else:
            try:
                r = obs.read_json(path)
                raw[name] = r
                failures.extend(check_run(r, obs.controls(name), captured_matrix_hash(folder, plan, specification, matrix_hash)))
                if r.get('observed'):
                    for segment in r.get('segments', []):
                        receipt = segment.get('receipt_file', '')
                        if (not receipt or Path(receipt).name != receipt or not (folder/receipt).is_file()
                                or obs.sha(folder/receipt) != segment.get('receipt_sha256')):
                            failures.append('segment persistence receipt unavailable or mismatched')
                attempt = specification.get('attempt', name)
                end = resources.get('ends', {}).get(attempt, {})
                start = resources.get('starts', {}).get(attempt, {})
                if end.get('artifact_sha256') != obs.sha(path) or start.get('kind') != 'full':
                    failures.append('run artifact/attempt binding mismatch')
                if end.get('exit_code') not in (0, 2):
                    failures.append('run attempt failed or terminated')
                if name != 'control' and not failures:
                    observed[name] = obs.observe_saved(path)
                    gates = numeric_gates(observed[name], r)
                    reasons.extend(name+': failed gate: '+key for key, passed in gates.items() if not passed)
                    runs[name] = dict(artifact_sha256=obs.sha(path), public_status=r['public_result']['status'],
                                      audits=observed[name]['audits'], gates=gates,
                                      numerical_passed=all(gates.values()))
            except (ValueError, KeyError, TypeError, OSError, IndexError, zipfile.BadZipFile, EOFError) as exc:
                failures.append('malformed/incomplete evidence: '+str(exc))
        runs.setdefault(name, {})['reasons'] = failures
        reasons.extend(name+': '+v for v in failures)
    neutrality = dict(passed=False, reason='same-environment normal/control evidence unavailable')
    if all(k in raw and not runs[k]['reasons'] for k in ('normal', 'control')):
        a, b = raw['normal'], raw['control']
        equality = obs.canonical(a['public_result']) == obs.canonical(b['public_result'])
        same_env = a['environment'] == b['environment']
        neutrality = dict(passed=equality and same_env, exact_complete_result_equal=equality,
                          same_environment=same_env, observed_sha256=a['public_result_sha256'],
                          unobserved_sha256=b['public_result_sha256'])
    repeat = dict(passed=False, reason='observed repeat evidence unavailable')
    if all(k in observed for k in ('normal', 'repeat')):
        repeat = dict(passed=obs.canonical(observed['normal']) == obs.canonical(observed['repeat']) and
                      raw['normal']['public_result_sha256'] == raw['repeat']['public_result_sha256'],
                      scope='complete recomputed observations and complete public Result')
    refinements = {}
    for name in list(obs.ROWS)[1:]:
        if all(k in observed and all(v is not None for v in observed[k]['activation'])
               and observed[k]['arrival'] is not None for k in ('normal', name)):
            try:
                refinements[name] = refinement(observed['normal'], observed[name])
            except (ValueError, KeyError, TypeError, IndexError) as exc:
                refinements[name] = unavailable_metrics(str(exc))
                reasons.append(name+': '+str(exc))
        else:
            refinements[name] = unavailable_metrics('mandatory physical-coordinate trajectory unavailable')
    observer_ok = fixtures['passed'] and neutrality['passed'] and not blocks
    for name in obs.ROWS:
        if name not in observed:
            observer_ok = False
        elif any(not runs[name]['gates'][k] for k in ('independent_inventory_sums', 'public_inventory_algebra',
                 'public_profile_reconstruction', 'public_cup_outlet_reconstruction', 'tail_weights_rates', 'cup_quadrature',
                 'diagnostic_inlet', 'diagnostic_liquid_profile_bounds', 'diagnostic_grain_profile_bounds',
                 'diagnostic_grain_history_bounds')):
            observer_ok = False
    numeric_ok = all(runs.get(k, {}).get('numerical_passed', False) for k in [*obs.ROWS, 'repeat'])
    numeric_ok &= repeat['passed'] and all(v['passed'] for pair in refinements.values() for v in pair.values())
    disposition = QUALIFIED if observer_ok and numeric_ok else BASELINE_INCOMPLETE if observer_ok else OBSERVER_INCOMPLETE
    public_resources = {k: v for k, v in resources.items() if k not in ('starts', 'ends')}
    public_resources['attempts'] = []
    for name, start in resources.get('starts', {}).items():
        end = resources.get('ends', {}).get(name, {})
        public_resources['attempts'].append({
            'name': name, 'kind': start.get('kind'), 'phase': start.get('phase'),
            'start_utc': start.get('utc'), 'end_utc': end.get('utc'),
            'seconds': end.get('seconds'), 'exit_code': end.get('exit_code'),
            'peak_rss_bytes': end.get('peak_rss_bytes'), 'log_sha256': end.get('log_sha256'),
            'artifact_sha256': end.get('artifact_sha256'), 'source_hashes': start.get('source_hashes'),
            'memory_bytes': start.get('memory_bytes'), 'resource_policy': start.get('resource_policy', 'original-2gib'),
            'controller_sha256': start.get('controller_sha256', OLD_CONTROLLER_SHA256),
            'enforced_rlimit_as': end.get('enforced_rlimit_as'), 'telemetry': end.get('telemetry'),
            'allocation_sha256': start.get('allocation_sha256'), 'evidence_bytes': end.get('evidence_bytes')})
    return dict(task=obs.TASK, governance='G1', change_declaration='NO_GOVERNING_PHYSICS_CHANGE',
                disposition=disposition, physical_validation='NOT_ESTABLISHED',
                matrix_sha256=matrix_hash, blocks=blocks, reasons=reasons,
                observer_qualified=observer_ok, production_numerics='PASS' if numeric_ok else
                ('INCOMPLETE' if resources.get('full', 0) or raw else 'NOT_EXECUTED'), numerical_support='COMPLETE' if numeric_ok else 'INCOMPLETE',
                fixtures=fixtures, neutrality=neutrality, deterministic_repeat=repeat,
                runs=runs, refinements=refinements, resources=public_resources, feasibility=feasibility,
                software_qa='SEPARATE_RECEIPT', hosted_ci='SEPARATE_EXACT_HEAD_RECEIPT',
                independent_review='SEPARATE_EXACT_HEAD_RECEIPT')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs-directory', type=Path, required=True)
    parser.add_argument('--matrix', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        result = report(args.runs_directory, args.matrix)
    except (ValueError, KeyError, TypeError, OSError, IndexError) as exc:
        result = dict(disposition=OBSERVER_INCOMPLETE, blocks=['MALFORMED_OR_MISSING_EVIDENCE'],
                      reasons=[str(exc)], physical_validation='NOT_ESTABLISHED')
    args.output.write_text(obs.canonical(result)+'\n')
    print(result['disposition'])
    return 0 if result['disposition'] == QUALIFIED else 2


if __name__ == '__main__':
    raise SystemExit(main())

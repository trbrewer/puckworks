"""005 serial runner and adapter for the existing external resource controller."""
from __future__ import annotations

import argparse
import json
import os
import runpy
from pathlib import Path

from puckworks.analysis import grudeva2026_baseline_observation_005 as obs

ROOT = Path(__file__).resolve().parents[1]


def initialize(folder):
    folder.mkdir(parents=True, exist_ok=True)
    target = folder/'invoke.py'
    if target.exists():
        raise FileExistsError('controller exists; never reset an attempt ledger')
    source = (ROOT/'tools/grudeva2026_bed_accuracy_004_invoke.py').read_text()
    substitutions = {
        "assert used<3600 and (kind!='full' or full<24)":
        "short=sum(r['kind']=='short' for r in starts.values())\nassert used<1200 and (kind!='full' or full<10) and (kind!='short' or short<20)",
        '# Protect 8 slots / 1800 seconds. Final allocation may reserve more.':
        '# 005: protect three full slots and 300 seconds for one observer correction.',
        "cap={'development':1800.,'final':2100.,'correction':3600.}[phase]":
        "cap={'development':900.,'final':900.,'correction':1200.}[phase]",
        "assert used<cap and (phase!='development' or kind!='full' or full<16)":
        "assert used<cap and (phase=='correction' or kind!='full' or full<7)",
        'ceiling=min(900.,cap-used)': 'ceiling=min(300.,cap-used)',
        "PYTHONHASHSEED='0')": "PYTHONHASHSEED='0',GRUDEVA005_ATTEMPT=name)",
    }
    for old, new in substitutions.items():
        if source.count(old) != 1:
            raise ValueError('inherited controller text differs: '+old)
        source = source.replace(old, new)
    target.write_text(source)
    (folder/'controller-binding.json').write_text(obs.canonical({
        'inherited_sha256': obs.sha(ROOT/'tools/grudeva2026_bed_accuracy_004_invoke.py'),
        'controller_sha256': obs.sha(target), 'limits': {'full': 10, 'short': 20,
        'aggregate_seconds': 1200, 'primary_seconds': 900, 'per_invocation_seconds': 300,
        'memory_bytes': 2*1024**3, 'reserve_slots': 3, 'reserve_seconds': 300}})+'\n')



def amend_resources(folder):
    """Install the owner's exact 8 GiB amendment without replacing the ledger."""
    import fcntl
    from puckworks.analysis import grudeva2026_baseline_observation_005_report as report
    folder = folder.resolve()
    with (folder/'controller.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if (folder/'resource-amendment.json').exists():
            raise FileExistsError('resource amendment already installed')
        audit = report.resource_audit(folder)
        if not audit['passed']:
            raise ValueError(audit['reasons'])
        if obs.sha(folder/'invoke.py') != report.OLD_CONTROLLER_SHA256:
            raise ValueError('wrong original 005 controller')
        snapshots = [('invoke.py', 'invoke-2gib.py'), ('controller-binding.json', 'controller-binding-2gib.json'),
                     ('invocations.jsonl', 'invocations-before-8gib.jsonl')]
        for source, target in snapshots:
            data = (folder/source).read_bytes()
            if (folder/target).exists() and (folder/target).read_bytes() != data:
                raise ValueError('historical snapshot differs: '+target)
            (folder/target).write_bytes(data)
        for name in ('MATRIX', 'RESULTS'):
            source = ROOT/f'docs/analysis/model_grudeva2026_baseline_observation_005/{name}.json'
            target = folder/f'{name}-2gib-reviewed.json'
            if target.exists() and target.read_bytes() != source.read_bytes():
                raise ValueError('historical reviewed snapshot differs')
            target.write_bytes(source.read_bytes())
        source = ROOT/'tools/grudeva2026_baseline_observation_005_invoke.py'
        binding = dict(policy=report.RESOURCE_POLICY, memory_bytes=report.MEMORY_8GIB,
                       old_controller_sha256=report.OLD_CONTROLLER_SHA256, controller_sha256=obs.sha(source),
                       historical_ledger_sha256=obs.sha(folder/'invocations-before-8gib.jsonl'),
                       historical_matrix_sha256=obs.sha(folder/'MATRIX-2gib-reviewed.json'),
                       historical_result_sha256=obs.sha(folder/'RESULTS-2gib-reviewed.json'),
                       starting_full=audit['full'], starting_short=audit['short'], starting_seconds=audit['seconds'])
        (folder/'resource-amendment.json').write_text(obs.canonical(binding)+'\n')
        temporary = folder/'invoke-amended.tmp'
        temporary.write_bytes(source.read_bytes())
        temporary.replace(folder/'invoke.py')
        (folder/'controller-binding.json').write_text(obs.canonical(binding)+'\n')
    return binding


def allocation_gate(args):
    from puckworks.analysis import grudeva2026_baseline_observation_005_report as report
    if args.allocation is None:
        raise ValueError('owner continuation requires a bound allocation')
    spec = obs.read_json(args.allocation)
    folder = args.allocation.resolve().parent
    expected_kind = 'short' if args.pilot else 'full'
    checks = (spec.get('attempt') == os.environ.get('GRUDEVA005_ATTEMPT'),
              spec.get('kind') == expected_kind, spec.get('row') == args.row,
              spec.get('output') == args.output.name,
              spec.get('sources') == obs.sources(), spec.get('controls') == obs.controls(args.row),
              spec.get('runner_sha256') == obs.sha(__file__),
              spec.get('request_hashes') == {k: obs.digest(v) for k, v in obs.requests(.4 if args.pilot else 8.).items()},
              spec.get('resource_amendment_sha256') == obs.sha(folder/'resource-amendment.json'),
              spec.get('controller_sha256') == obs.sha(folder/'invoke.py'),
              spec.get('matrix_sha256') == obs.sha(args.matrix) if args.matrix else False,
              os.environ.get('GRUDEVA005_RESOURCE_POLICY') == report.RESOURCE_POLICY)
    if not all(checks):
        raise ValueError('allocation source/request/resource identity mismatch')
    role = spec.get('role')
    if role == 'replacement_pilot':
        if not (args.pilot and args.row == 'combined' and spec['attempt'] == 'pilot-combined-8gib'):
            raise ValueError('only one exact combined replacement pilot authorized')
    elif role == 'combined_feasibility_probe':
        if args.pilot or args.row != 'combined' or spec['attempt'] != 'combined-feasibility-8gib':
            raise ValueError('only the exact combined full probe is authorized')
        prerequisite = spec.get('pilot_prerequisite', {})
        path = folder/prerequisite.get('file', '')
        if not path.is_file() or obs.sha(path) != prerequisite.get('sha256'):
            raise ValueError('successful short pilot prerequisite unavailable')
        pilot = obs.read_json(path)
        if not pilot.get('applicable_pilot_checks_passed') or not spec.get('measured_full_probe_basis'):
            raise ValueError('full probe has no qualified pilot/headroom/budget basis')
    elif role == 'remaining_panel':
        if args.pilot or obs.read_json(args.matrix).get('feasibility', {}).get('disposition') != 'FEASIBLE':
            raise ValueError('remaining panel allocation is not feasible')
    elif role == 'combined_persistence_recapture':
        if args.pilot or args.row != 'combined' or spec['attempt'] != 'combined-persistence-recapture':
            raise ValueError('only the exact corrective combined recapture is authorized')
        if spec.get('persistence_amendment_sha256') != obs.sha(folder/'persistence-amendment.json'):
            raise ValueError('persistence amendment identity mismatch')
        for binding in spec.get('persistence_tests', []):
            path = folder/binding['file']
            if obs.sha(path) != binding['sha256'] or obs.read_json(path).get('exit_code') != 0:
                raise ValueError('persistence qualification unavailable')
            if obs.read_json(path).get('sources') != obs.sources():
                raise ValueError('persistence tests source mismatch')
        if len(spec.get('persistence_tests', [])) != 2 or not spec.get('remaining_panel_estimate'):
            raise ValueError('recapture requires qualified tests and complete cost estimate')
    else:
        raise ValueError('unauthorized allocation role')
    return spec

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('directory', type=Path)
    amend = sub.add_parser('amend-resources')
    amend.add_argument('directory', type=Path)
    fixtures = sub.add_parser('fixtures')
    fixtures.add_argument('--output', type=Path, required=True)
    run = sub.add_parser('run')
    run.add_argument('--row', choices=[*obs.ROWS, 'repeat', 'control'], default='normal')
    run.add_argument('--pilot', action='store_true')
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--matrix', type=Path)
    run.add_argument('--allocation', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'init':
        initialize(args.directory)
        return 0
    if args.command == 'amend-resources':
        amend_resources(args.directory)
        return 0
    if not os.environ.get('GRUDEVA005_ATTEMPT'):
        parser.error('scientific execution requires the external invoke.py controller')
    if args.command == 'fixtures':
        module = runpy.run_path(str(ROOT/'tests/test_grudeva2026_baseline_observation_005.py'))
        result = module['qualification_evidence']()
        args.output.write_text(obs.canonical(result)+'\n')
        print('Independent numerical fixture arrays retained')
        return 0
    amended = bool(os.environ.get('GRUDEVA005_RESOURCE_POLICY'))
    if amended:
        try:
            allocation_gate(args)
        except (ValueError, KeyError, OSError, TypeError) as exc:
            parser.error(str(exc))
    if not args.pilot:
        if args.matrix is None:
            parser.error('full runs require the frozen matrix')
        plan = obs.read_json(args.matrix)
        if not amended and plan.get('feasibility', {}).get('disposition') != 'FEASIBLE':
            parser.error('RESOURCE_FEASIBILITY_BLOCKED: no full allocation')
        if (plan.get('sources') != obs.sources() or
                plan.get('request_hashes') != {k: obs.digest(v) for k, v in obs.requests().items()} or
                plan.get('runs', {}).get(args.row, {}).get('controls') != obs.controls(args.row)):
            parser.error('frozen source/configuration/support identity mismatch')
    matrix_hash = obs.sha(args.matrix) if args.matrix else None
    def stage(value, **details):
        args.output.with_name(args.output.stem+'-execution.json').write_text(
            obs.canonical(dict(stage=value, **details))+'\n')
    stage('production_and_capture')
    try:
        r = obs.execute(args.output, row=args.row, pilot=args.pilot,
                        observed=args.row != 'control', matrix_sha256=matrix_hash)
        stage('capture_returned', production_status=r['public_result']['status'], returned=r.get('returned'))
        if args.row != 'control' and r.get('segments'):
            stage('replay_and_observation', production_status=r['public_result']['status'], returned=r.get('returned'))
            observed = obs.observe_saved(args.output)
            # Full observation arrays are external; compact run metadata remain separate.
            output = args.output.with_name(args.output.stem+'-observations.json')
            output.write_text(obs.canonical(observed)+'\n')
            import numpy as np
            dense_count = accepted_count = 0
            for segment in r['segments']:
                with np.load(args.output.parent/segment['file'], allow_pickle=False) as data:
                    dense_count += len(data['orders'])
                    accepted_count += len(data['accepted_t'])
            stage('completed_observation', production_status=r['public_result']['status'], returned=r.get('returned'),
                  accepted_states=accepted_count, dense_intervals=dense_count,
                  retained_numerical_bytes=r['retained_numerical_bytes'],
                  live_replay=[s.get('live_replay') for s in r['segments']], observation_sha256=obs.sha(output))
            print(json.dumps({'status': r['status'], 'production_status': r['public_result']['status'],
                              'retained_numerical_bytes': r['retained_numerical_bytes'],
                              'accepted_states': observed['audits']['accepted_states'],
                              'dense_intervals': dense_count,
                              'live_replay_points': sum(s['live_replay']['points'] for s in r['segments']),
                              'horizon': observed['audits']['horizon'],
                              'observation_sha256': obs.sha(output)}, sort_keys=True))
        else:
            print(json.dumps({'status': r['status'], 'production_status': r['public_result']['status']}))
    except BaseException as exc:
        import traceback
        frames = traceback.extract_tb(exc.__traceback__)
        functions = [f.name for f in frames]
        phase = ('observation' if 'observe_saved' in functions else
                 'persistence_or_replay' if 'save_segment' in functions else
                 'solve_or_result_assembly')
        stage('failed', failure_stage=phase, exception_type=type(exc).__name__,
              exception_message=str(exc), traceback_functions=functions)
        raise
    return 2  # single execution cannot qualify a matrix


if __name__ == '__main__':
    raise SystemExit(main())

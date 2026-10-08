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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    init = sub.add_parser('init')
    init.add_argument('directory', type=Path)
    fixtures = sub.add_parser('fixtures')
    fixtures.add_argument('--output', type=Path, required=True)
    run = sub.add_parser('run')
    run.add_argument('--row', choices=[*obs.ROWS, 'repeat', 'control'], default='normal')
    run.add_argument('--pilot', action='store_true')
    run.add_argument('--output', type=Path, required=True)
    run.add_argument('--matrix', type=Path)
    args = parser.parse_args(argv)
    if args.command == 'init':
        initialize(args.directory)
        return 0
    if not os.environ.get('GRUDEVA005_ATTEMPT'):
        parser.error('scientific execution requires the external invoke.py controller')
    if args.command == 'fixtures':
        module = runpy.run_path(str(ROOT/'tests/test_grudeva2026_baseline_observation_005.py'))
        result = module['qualification_evidence']()
        args.output.write_text(obs.canonical(result)+'\n')
        print('Independent numerical fixture arrays retained')
        return 0
    if not args.pilot:
        if args.matrix is None:
            parser.error('full runs require the frozen matrix')
        plan = obs.read_json(args.matrix)
        if plan.get('feasibility', {}).get('disposition') != 'FEASIBLE':
            parser.error('RESOURCE_FEASIBILITY_BLOCKED: no full allocation')
        if (plan.get('sources') != obs.sources() or
                plan.get('request_hashes') != {k: obs.digest(v) for k, v in obs.requests().items()} or
                plan.get('runs', {}).get(args.row, {}).get('controls') != obs.controls(args.row)):
            parser.error('frozen source/configuration/support identity mismatch')
    matrix_hash = obs.sha(args.matrix) if args.matrix else None
    r = obs.execute(args.output, row=args.row, pilot=args.pilot,
                    observed=args.row != 'control', matrix_sha256=matrix_hash)
    if args.row != 'control' and r.get('segments'):
        observed = obs.observe_saved(args.output)
        # Full observation arrays are external; compact run metadata remain separate.
        output = args.output.with_name(args.output.stem+'-observations.json')
        output.write_text(obs.canonical(observed)+'\n')
        print(json.dumps({'status': r['status'], 'production_status': r['public_result']['status'],
                          'retained_numerical_bytes': r['retained_numerical_bytes'],
                          'accepted_states': observed['audits']['accepted_states'],
                          'dense_intervals': sum(s['live_replay']['points'] for s in r['segments']),
                          'horizon': observed['audits']['horizon'],
                          'observation_sha256': obs.sha(output)}, sort_keys=True))
    else:
        print(json.dumps({'status': r['status'], 'production_status': r['public_result']['status']}))
    return 2  # single execution cannot qualify a matrix


if __name__ == '__main__':
    raise SystemExit(main())

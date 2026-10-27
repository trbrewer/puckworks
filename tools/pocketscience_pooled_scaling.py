#!/usr/bin/env python3
"""Frozen private pooled-scaling comparison; never prints source paths or values."""
import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from tools import pocketscience_cup_tds as previous  # noqa: E402
from puckworks.analysis import pocketscience_cup_tds as parent  # noqa: E402
from puckworks.analysis import pocketscience_pooled_scaling as model  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-POOLED-SCALING-001'
PARENT = '2f93c216f02700e28801418a3069684fff0ba9ea'
MAIN = previous.BASE
EWP = previous.EWP
MEMBERSHIP = '1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196'
PARENT_HASHES = {'FREEZE.json': '48bfd9e5de9659486e754fad72860b3f77cedb5324901ae3097ab6e49749d5f6',
                 'RESULT.json': '1b548e74f24e7e576c6bf1b831109ae7fce9d6bf27575d7d73986a2f0b3253d5'}
FILES = ['puckworks/analysis/pocketscience_pooled_scaling.py',
         'tools/pocketscience_pooled_scaling.py', 'tests/test_pocketscience_pooled_scaling.py',
         'docs/analysis/sci_md_pocketscience_pooled_scaling_001/METHODS.md']
digest, write_json = previous.digest, previous.write_json


def locations(output=None):
    source, predecessor = previous.locations()
    out = output.resolve() if output else predecessor.parent/TASK
    if out.is_relative_to(REPO) or out.is_relative_to(source.parent.parent) or out == predecessor:
        raise ValueError('new evidence must be external and separate from predecessor/source')
    return source, predecessor, out


def freeze(source, old, out):
    if (out/'FREEZE.json').exists():
        raise ValueError('freeze exists; use a fresh output directory')
    for name, expected in PARENT_HASHES.items():
        if digest(old/name) != expected:
            raise ValueError('predecessor '+name+' hash mismatch')
    frozen = json.loads((old/'FREEZE.json').read_text())
    for name, expected in frozen['code_sha256'].items():
        if digest(REPO/name) != expected:
            raise ValueError('predecessor scientific code changed')
    for name, expected in frozen['private_input_sha256'].items():
        if digest(old/name) != expected:
            raise ValueError('predecessor input '+name+' changed')
    artifacts = json.loads((old/'ARTIFACTS.json').read_text())
    for name in ('primary_bootstrap.json', 'unfiltered_bootstrap.json', 'include_rejected_bootstrap.json'):
        if digest(old/name) != artifacts[name]:
            raise ValueError('predecessor bootstrap artifact mismatch')
    shots, failed = parent.read_source(source)
    observed = json.loads(json.dumps([asdict(s) for s in shots]))
    if failed or len(shots) != 60 or observed != json.loads((old/'SHOTS.json').read_text()):
        raise ValueError('predecessor observation/order drift')
    primary = [s for s in shots if not s.source_excluded]
    if parent.membership_hash(primary) != MEMBERSHIP:
        raise ValueError('primary membership drift')
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    (out/'SHOTS.json').write_bytes((old/'SHOTS.json').read_bytes())
    (out/'METHODS.md').write_bytes((REPO/FILES[-1]).read_bytes())
    record = {'task': TASK, 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'pw_main': MAIN, 'pw_parent_and_branch_base': PARENT, 'ewp_sha': EWP,
              'source_sha256': digest(source), 'membership_sha256': MEMBERSHIP,
              'exposure': parent.EXPOSURE, 'primary_n': 57, 'conditions': 12,
              'qualified_all_n': 60, 'flush_n': 10, 'sessions': 'UNKNOWN',
              'inspection': 'Hash-bound source/parent receipt check; unchanged observer compared all '
                            '60 raw cup rows and metadata against exact parent order. No census or '
                            'source acquisition. Parent full-precision result inspected; P NOT_RUN.',
              'parent_receipts': {p.name: digest(p) for p in old.iterdir() if p.is_file()},
              'code_sha256': {p: digest(REPO/p) for p in FILES+list(frozen['code_sha256'])},
              'private_input_sha256': {p: digest(out/p) for p in ('SHOTS.json', 'METHODS.md')},
              'seed': 20261026, 'draws': 2000, 'bounds': [0, 100], 'loss_status': 'P_NOT_RUN',
              'model_specification': 'METHODS.md, including comparisons, decision and sensitivities'}
    write_json(out/'FREEZE.json', record)
    print(json.dumps({'status': 'FROZEN_P_NOT_RUN', 'freeze_sha256': digest(out/'FREEZE.json')}))


def report(result):
    primary = result['primary']
    lines = [f'# {TASK}', '',
             'This comparison asks whether a second style/grinder coefficient improves conditional '
             'cup-TDS prediction beyond one pooled dose/beverage coefficient. The primary evaluation '
             'uses 57 physical shots (37 Sworks, 20 VST) in 12 existing conditions. '
             f"Result: {primary['decision']['status']}. "
             'These are retrospective, exposed measurements conditional on measured final beverage '
             'mass, not blind validation or a forecast of beverage mass. No practical adequacy, '
             'causal style/grinder interpretation or production adoption follows.', '',
             'Pocket Science Coffee (2024). '+parent.EXPOSURE+'. All 60 cup rows were checked '
             'against the authenticated parent inputs/order; raw B including B54, D/E converted to kg; '
             'C is a separate observation. TDS pp means nominal refractometer-equivalent solute per '
             'solution mass. Historical Y54 is unchanged. Ten flush measurements are excluded; '
             'sessions remain UNKNOWN. Used means and their shots remain exposed.', '',
             '| Arm | RMSE pp | MAE pp | Bias pp | Condition-balanced RMSE pp |',
             '|---|---:|---:|---:|---:|']
    for arm in ('P', 'M', 'C', 'N'):
        s = primary['scores'][arm]
        lines.append(f"| {arm} | {s['rmse']:.6f} | {s['mae']:.6f} | {s['bias']:.6f} | {s['condition_balanced_rmse']:.6f} |")
    lines += ['', '| Contrast | Difference pp [95% CI] | Gain [95% CI] | Point; CI grades |',
              '|---|---|---|---|']
    for key in ('M/P', 'P/N', 'M/C', 'M/N'):
        c = primary['contrasts'][key]
        def interval(quantity):
            ci = c[quantity+'_ci95']
            value = c[quantity]
            return 'undefined' if value is None else f'{value:.6f} '+(
                'CI unavailable' if ci is None else f'[{ci[0]:.6f}, {ci[1]:.6f}]')
        lines.append(f"| {key} | {interval('difference')} | {interval('gain')} | {c['grade']}; {', '.join(c['ci_grades'])} |")
    lines += ['', 'Differences are L_A−L_B (negative favors A); gains are 1−L_A/L_B '
              '(positive favors A). P/N fit one coefficient each; M/C two each. Independent '
              'training fits, [0,100] bounds, identical physical-shot squared-TDS objective; '
              'alpha/theta are operational coefficients. Every shot receives one prediction '
              'per arm; complete fold, condition, adverse/worst-case results are private.', '']
    for name in ('primary', 'unfiltered', 'include_rejected'):
        r = result[name]
        b = r['bootstrap']
        text = f"{name}: n={r['n']}; draws requested/completed/failed={b['requested']}/{b['completed']}/{b['failed']}; "
        text += f"decision {r['decision']['status']}. "
        for key in ('M/P', 'P/N'):
            c = r['contrasts'][key]
            text += f"{key} gain {c['gain']:.6f}, CI {c['gain_ci95']}; " if c['gain'] is not None else f'{key} gain undefined; '
        lines.append(text.rstrip('; ')+'.')
    lines += ['', 'Seed 20261026; one global within-condition physical-shot multiplicity vector '
              'per draw, used for every refit and held score. Percentile intervals assume '
              'exchangeability within these fixed conditions; they omit unknown sessions, '
              'calibration and shared systematic error and are not simultaneous.', '']
    for key in ('M/P', 'P/N'):
        c = primary['contrasts'][key]
        lines.append(f"Nine ±25% boundary combinations, {key}: point grades "
                     +', '.join(sorted({v['point'] for v in c['boundary_check']}))+'; CI grade sets '
                     +' / '.join(sorted({','.join(v['ci_grades']) for v in c['boundary_check']}))+'.')
    lines += ['', 'Bands are descriptive, not adequacy margins or sensor-uncertainty tests. '
              'Condition-deletion gain ranges (not CIs): '+ '; '.join(
                  f"{k} {result['deletion']['influence_ranges_not_ci'][k]['gain']}" for k in ('M/P', 'P/N'))+'.', '',
              'Arithmetic checks: bounded least squares for P and nested training SSE pass; '
              'full-precision predecessor point predictions/scores and all 2,000 bootstrap '
              'draws reproduce to 1e-10. Active bounds and numerical discrepancies are recorded '
              'in RESULT.json. This is not measurement accuracy. PR374 artifacts remain unchanged. '
              'A pooled formula establishes no transfer to new grinders, baskets, coffees or campaigns. '
              'P1 blind-TDS=OPEN.', '',
              'Reproduce: `python tools/pocketscience_pooled_scaling.py freeze`; focused tests; '
              '`python tools/pocketscience_pooled_scaling.py run`. Use `--output` for a fresh private '
              'directory. Source/input/code/method hashes: FREEZE.json; full artifact hashes: ARTIFACTS.json.']
    return '\n'.join(lines)+'\n'


def export_csv(out, label, result):
    fields = ['sheet', 'row', 'condition', 'style', 'target_pp', 'x']+[a+'_prediction_pp' for a in model.ARMS]
    with (out/(label+'_predictions.csv')).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for row in result['predictions']:
            record = {k: row[k] for k in fields[:6]}
            record['condition'] = json.dumps(record['condition'])
            record.update({a+'_prediction_pp': row['predictions'][a] for a in model.ARMS})
            writer.writerow(record)


def run(source, old, out):
    if (out/'RESULT.json').exists():
        raise ValueError('result exists; use a fresh output directory')
    frozen = json.loads((out/'FREEZE.json').read_text())
    if digest(source) != frozen['source_sha256']:
        raise ValueError('original hash changed')
    for directory, key in ((REPO, 'code_sha256'), (out, 'private_input_sha256'), (old, 'parent_receipts')):
        for name, expected in frozen[key].items():
            if digest(directory/name) != expected:
                raise ValueError('frozen '+key+' drift: '+name)
    shots = [parent.Shot(**dict(s, condition=tuple(s['condition'])))
             for s in json.loads((out/'SHOTS.json').read_text())]
    primary = [s for s in shots if not s.source_excluded]
    if parent.membership_hash(primary) != MEMBERSHIP:
        raise ValueError('primary membership changed')
    old_result = json.loads((old/'RESULT.json').read_text())
    result = {'task': TASK, 'pw_main': MAIN, 'pw_parent': PARENT, 'ewp_sha': EWP,
              'exposure': parent.EXPOSURE, 'freeze_sha256': digest(out/'FREEZE.json')}
    start = time.monotonic()
    for name, cohort, observation in (('primary', primary, 'filtered'),
                                      ('unfiltered', primary, 'unfiltered'),
                                      ('include_rejected', shots, 'filtered')):
        r = model.evaluate(cohort, observation, deadline=start+1800)
        result[name] = r
        if r['bootstrap']['failed']:
            write_json(out/'INCOMPLETE.json', result)
            raise ValueError('failed paired bootstrap draws; no unconditional decision')
        r['predecessor_reproduction'] = model.verify_predecessor(
            r, old_result[name], json.loads((old/(name+'_bootstrap.json')).read_text()))
        write_json(out/(name+'_bootstrap.json'), r.pop('bootstrap_samples'))
        export_csv(out, name, r)
    result['deletion'] = model.deletion_influence(primary)
    result['scientific_computation_seconds'] = time.monotonic()-start
    if result['scientific_computation_seconds'] > 1800:
        raise ValueError('scientific computation budget exceeded')
    write_json(out/'RESULT.json', result)
    (out/'RESULT.md').write_text(report(result))
    write_json(out/'ARTIFACTS.json', {p.name: digest(p) for p in sorted(out.iterdir())
                                   if p.is_file() and p.name != 'ARTIFACTS.json'})
    print(json.dumps({'status': 'COMPLETED_PRIVATE', 'result_sha256': digest(out/'RESULT.json')}))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('freeze', 'run'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        source, old, out = locations(args.output)
        (freeze if args.command == 'freeze' else run)(source, old, out)
    except (OSError, ValueError, KeyError) as exc:
        reason = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(json.dumps({'status': 'NOT_RUN_OR_INCOMPLETE', 'blocker': reason}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

#!/usr/bin/env python3
"""Private source-internal analysis; stdout contains safe status/hashes only."""
import argparse
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from puckworks.analysis.pocketscience_cup_tds import (  # noqa: E402
    EXPOSURE, SOURCE_SHA256, STYLE_MAP, Shot, read_source, membership_hash,
    evaluate, deletion_influence,
)
from tools.inventory_local_corpus import config_path  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-CUP-TDS-001'
BASE = '21669a427145194e1f4003e3cf1b97dedefe2679'
EWP = 'f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516'
FILES = ['puckworks/analysis/pocketscience_cup_tds.py', 'tools/pocketscience_cup_tds.py',
         'tests/test_pocketscience_cup_tds.py', 'puckworks/analysis/pocketscience2024_assay.py',
         'docs/analysis/sci_md_pocketscience_cup_tds_001/METHODS.md']


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def locations():
    config = json.loads(config_path().read_text())
    root = Path(os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or config['inventory']['root'])
    evidence = Path(config['inventory']['manifest']).resolve().parent / TASK
    source = root/'pocketscience2024'/'Espresso water flow experiment.xlsx'
    if evidence.resolve().is_relative_to(REPO) or evidence.resolve().is_relative_to(root.resolve()):
        raise ValueError('private evidence must be outside checkout and source collection')
    return source, evidence


def freeze(source, evidence):
    if (evidence/'FREEZE.json').exists():
        raise ValueError('freeze already exists; do not overwrite')
    shots, failed = read_source(source)
    primary = [s for s in shots if not s.source_excluded]
    evidence.mkdir(parents=True, exist_ok=True, mode=0o700)
    write_json(evidence/'SHOTS.json', [asdict(s) for s in shots])
    inspection = {
        'source_sha256': SOURCE_SHA256, 'original_inspected': True,
        'scope': 'All 60 experimental rows: raw B/C/D/E and A/F/I/J, repeated headers, '
                 'source exclusion notes; formula/cache views opened by qualified reader. '
                 'No figure reading, new census, external acquisition or physical experiments.',
        'raw_basis': {'B': 'filtered numeric TDS percent', 'C': 'unfiltered numeric TDS percent',
                      'D': 'initial dry dose g', 'E': 'final beverage mass g'},
        'basis_authority': 'Hash-qualified original plus existing MEASUREMENT_MAP.md and source card',
        'nominal_tds_basis': 'refractometer-equivalent solute per solution mass',
        'physical_identity': 'sheet + row, not repeated shot number',
        'style_map': STYLE_MAP, 'condition': ['sheet', 'grinder', 'screen/paper', 'dispersion'],
        'primary': 57, 'primary_sworks': 37, 'primary_vst': 20, 'conditions': 12,
        'experimental_total': 60, 'distinct_flush_measurements': 10,
        'flush_count_authority': 'Prior qualified reconstruction, excluded from cup comparison',
        'rejected_cup_qualified': sum(s.source_excluded for s in shots),
        'rejected_cup_failed': failed, 'session_count': 'UNKNOWN',
        'B54': 'direct raw B read and qualified; historical Y54 remains unchanged',
        'formula_assurance': 'Prior 1672-formula replay with maximum display error below 5e-9 '
                             'reused by unchanged original/reader hashes; not measurement uncertainty',
        'exposure': EXPOSURE, 'prior_use': 'Used means and their replicates remain exposed',
        'historical_PR373': 'zero admitted target shots; NOT_RUN transfer losses/CIs, no predictor evidence',
        'rights': 'Expanded redistribution grant absent; all numerical artifacts private',
    }
    write_json(evidence/'INSPECTION.json', inspection)
    methods = REPO/FILES[-1]
    (evidence/'METHODS.md').write_bytes(methods.read_bytes())
    frozen = {'task': TASK, 'timestamp_utc': datetime.now(timezone.utc).isoformat(),
              'pw_base': BASE, 'ewp_sha': EWP, 'source_sha256': digest(source),
              'membership_sha256': membership_hash(primary), 'exposure': EXPOSURE,
              'governance': 'G1 / NO_GOVERNING_PHYSICS_CHANGE / retrospective exposed comparison',
              'code_sha256': {p: digest(REPO/p) for p in FILES},
              'private_input_sha256': {p: digest(evidence/p) for p in ['SHOTS.json', 'INSPECTION.json', 'METHODS.md']},
              'draws': 2000, 'seed': 20261026, 'loss_status': 'NOT_RUN',
              'fit_bounds': [0, 100], 'gain_boundaries': [0, .10, .25],
              'grade_check_lower': [.075, .10, .125], 'grade_check_upper': [.1875, .25, .3125],
              'decision_authority': 'METHODS.md frozen before scoring'}
    write_json(evidence/'FREEZE.json', frozen)
    print(json.dumps({'status': 'FROZEN_NOT_SCORED', 'membership_sha256': frozen['membership_sha256'],
                      'freeze_sha256': digest(evidence/'FREEZE.json')}))


def report(result):
    p = result['primary']
    lines = [f'# {TASK}', '',
             'Objective: test whether measured dose/beverage scaling improves held-condition '
             'absolute cup TDS over a style-specific constant. The primary cohort has 57 shots '
             '(37 Sworks, 20 VST), 12 conditions; the cup-qualified inclusion sensitivity has 60. '
             f"Decision: {p['decision']['selected']}. "
             'This is a retrospective source-internal comparison conditional on measured final '
             'beverage mass, with exposed targets. It supports only conditional research use; '
             'no blind validation, practical adequacy, production adoption or causal interpretation follows.', '',
             f'Exposure: {EXPOSURE}. Pocket Science Coffee (2024). Sessions UNKNOWN; '
             'style/grinder confounded. All 60 raw cup rows and metadata inspected; exact original '
             'hash verified. Direct B (including B54), C sensitivity, D/E grams converted to kg. '
             'TDS pp is nominal refractometer-equivalent solute per solution mass. Used means and '
             'replicates remain exposed. Ten separate flush measurements are not cup shots.', '',
             '| Arm | RMSE pp | MAE pp | Bias pp | Condition-balanced RMSE pp |',
             '|---|---:|---:|---:|---:|']
    for arm, s in p['scores'].items():
        lines.append(f"| {arm} | {s['rmse']:.6f} | {s['mae']:.6f} | {s['bias']:.6f} | {s['condition_balanced_rmse']:.6f} |")
    lines += ['', '| Contrast | RMSE difference pp [95% CI] | Gain [95% CI] | Grade; CI grades |',
              '|---|---|---|---|']
    for key, c in p['contrasts'].items():
        d, g = c['difference_ci95'], c['gain_ci95']
        gain = 'undefined' if g is None else f"{c['gain']:.6f} [{g[0]:.6f}, {g[1]:.6f}]"
        lines.append(f"| {key} | {c['difference']:.6f} [{d[0]:.6f}, {d[1]:.6f}] | {gain} | {c['grade']}; {', '.join(c['ci_grades'])} |")
    lines += ['', 'Differences are L_A−L_B (negative favors A); gains 1−L_A/L_B (positive favors A). '
              'M/C each fit two independent style coefficients; N one. C uses fewer measured inputs. '
              'Theta is operational fitted EY, not an extraction mechanism. Twelve held-condition folds; '
              'all 57 shots receive exactly one prediction per arm. Squared absolute-TDS objective; '
              'training rank checks pass. Bounds [0,100]; active bound details in RESULT.json.', '']
    for name in ['primary', 'unfiltered', 'include_rejected']:
        r = result[name]
        b = r['bootstrap']
        lines.append(f"{name}: n={r['n']}; bootstrap requested/completed/failed "
                     f"{b['requested']}/{b['completed']}/{b['failed']}; active-bound draws {b['active_bound_draws']}. "
                     f"RMSE M/C/N={r['scores']['M']['rmse']:.6f}/{r['scores']['C']['rmse']:.6f}/{r['scores']['N']['rmse']:.6f}; "
                     f"decision {r['decision']['selected']}.")
    lines += ['', 'Seed 20261026; one global within-condition multiplicity set per draw, full refitting '
              'and paired scoring. Percentile intervals assume exchangeable shots in these fixed '
              'conditions, omit unknown session dependence/calibration/shared systematic errors, and '
              'are not simultaneous. Historical 0.01-pp/0.1-g assumptions are not calibrated uncertainty.', '']
    for key, c in p['contrasts'].items():
        points = sorted({z['point'] for z in c['boundary_check']})
        cis = sorted({','.join(z['ci_grades']) for z in c['boundary_check']})
        lines.append(f"Nine ±25% boundary combinations, {key}: point grades {', '.join(points)}; CI grade sets {' / '.join(cis)}.")
    lines += ['', 'These are reporting bands, not practical adequacy thresholds; boundary checks do '
              'not test measurement-error robustness. Deleting each condition and refitting remaining CV '
              'gives gain influence ranges (not CIs): '+ '; '.join(
                  f"{k} [{v['gain'][0]:.6f}, {v['gain'][1]:.6f}]" for k, v in result['deletion']['influence_ranges_not_ci'].items())+'.', '',
              'Independent least-squares cross-check maximum prediction discrepancy: '
              f"{p['least_squares_max_difference_pp']:.3g} pp (<1e-10); arithmetic assurance only. "
              'No separate grinder/style, hydraulic or radial-depletion effect is identified. '
              'Full predictions, fold coefficients, adverse/worst cases, condition errors, sensitivities '
              'and bootstrap draws are private companion JSON artifacts. P1 blind-TDS=OPEN.', '',
              'Reproduce: `python tools/pocketscience_cup_tds.py freeze`, then focused tests, then '
              '`python tools/pocketscience_cup_tds.py run` (fresh private evidence directory; frozen '
              'outputs are never overwritten). Authority and source/code/input hashes: FREEZE.json; '
              'all artifact hashes: ARTIFACTS.json.']
    return '\n'.join(lines)+'\n'


def run(source, evidence):
    if (evidence/'RESULT.json').exists():
        raise ValueError('result already exists; do not overwrite')
    frozen = json.loads((evidence/'FREEZE.json').read_text())
    if digest(source) != frozen['source_sha256']:
        raise ValueError('source changed after freeze')
    for p, h in frozen['code_sha256'].items():
        if digest(REPO/p) != h:
            raise ValueError('code changed after freeze')
    for p, h in frozen['private_input_sha256'].items():
        if digest(evidence/p) != h:
            raise ValueError('private input changed after freeze')
    shots = [Shot(**dict(s, condition=tuple(s['condition'])))
             for s in json.loads((evidence/'SHOTS.json').read_text())]
    primary = [s for s in shots if not s.source_excluded]
    if membership_hash(primary) != frozen['membership_sha256']:
        raise ValueError('primary membership changed')
    start = time.monotonic()
    result = {'task': TASK, 'pw_base': BASE, 'ewp_sha': EWP, 'exposure': EXPOSURE,
              'freeze_sha256': digest(evidence/'FREEZE.json'),
              'pw_head_at_execution': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip(),
              'primary': evaluate(primary), 'unfiltered': evaluate(primary, 'unfiltered'),
              'include_rejected': evaluate(shots), 'deletion': deletion_influence(primary)}
    result['scientific_computation_seconds'] = time.monotonic()-start
    if result['scientific_computation_seconds'] > 1800:
        raise ValueError('scientific computation budget exceeded')
    for name in ['primary', 'unfiltered', 'include_rejected']:
        write_json(evidence/(name+'_bootstrap.json'), result[name].pop('bootstrap_samples'))
    write_json(evidence/'RESULT.json', result)
    (evidence/'RESULT.md').write_text(report(result))
    write_json(evidence/'ARTIFACTS.json', {p.name: digest(p) for p in sorted(evidence.iterdir()) if p.is_file()})
    print(json.dumps({'status': 'COMPLETED_PRIVATE', 'result_sha256': digest(evidence/'RESULT.json'),
                      'scientific_computation_seconds': result['scientific_computation_seconds']}))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['freeze', 'run'])
    args = parser.parse_args()
    try:
        source, evidence = locations()
        (freeze if args.command == 'freeze' else run)(source, evidence)
    except (OSError, ValueError, KeyError) as exc:
        # Avoid leaking owner paths through exception messages or tracebacks.
        print(json.dumps({'status': 'NOT_RUN_OR_INCOMPLETE', 'error_type': type(exc).__name__}), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

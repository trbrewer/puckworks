#!/usr/bin/env python3
"""Bounded private style transfer; CLI emits safe status/hash summaries only."""
import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import sys
import time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
import numpy as np  # noqa: E402
import scipy  # noqa: E402
import openpyxl  # noqa: E402
from tools import pocketscience_cross_basket_tds as previous  # noqa: E402
from puckworks.analysis import pocketscience_cup_tds as parent  # noqa: E402
from puckworks.analysis import pocketscience_cross_basket_tds as basket  # noqa: E402
from puckworks.analysis import pocketscience_pooled_scaling as pooled  # noqa: E402
from puckworks.analysis import pocketscience_cross_style_tds as model  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-CROSS-STYLE-TDS-001'
PARENT = 'e21a98db63a1912a0f8baa2ef1c7cdc562293c18'
MAIN, EWP = previous.MAIN, previous.EWP
PARENT_HASHES = {
    'FREEZE.json': '22a50d10197d1fda389210fdc0fd672906e7b2a65134d8a7dc934e3429476f30',
    'RESULT.json': 'ef32f88905be021395d5bd87b8f3afe2a4e7bd964ef6712d7380295894a7d317',
    'SPLIT.json': 'fcf4e6f2f57df234b283d651d19c192097451d531c9f87d1480d13ece2077c68'}
FILES = ['puckworks/analysis/pocketscience_cross_style_tds.py',
         'tools/pocketscience_cross_style_tds.py', 'tests/test_pocketscience_cross_style_tds.py',
         'docs/analysis/sci_md_pocketscience_cross_style_tds_001/METHODS.md']
digest, write_json = previous.digest, previous.write_json


def locations(output=None, predecessor=None):
    source, ancestor, old, default = previous.locations()
    recent = (predecessor or default).resolve()
    out = output.resolve() if output else old.parent/TASK
    if (out.is_relative_to(REPO) or out.is_relative_to(source.parent.parent)
            or any(out.is_relative_to(p) or p.is_relative_to(out) for p in (ancestor, old, recent))):
        raise ValueError('evidence must be external and separate from originals/predecessors')
    return source, ancestor, old, recent, out


def split_record(shots):
    source, target = model.split(shots)
    _, _, _, group = parent.arrays(shots)
    return dict(conditions=sorted({s.condition for s in shots}),
                global_condition_indices=group.tolist(), original_order=[s.identity for s in shots],
                source=[s.identity for s, keep in zip(shots, source) if keep],
                target=[s.identity for s, keep in zip(shots, target) if keep],
                source_conditions=sorted(set(group[source].tolist())),
                target_conditions=sorted(set(group[target].tolist())),
                source_baskets=sorted({s.sheet for s, keep in zip(shots, source) if keep}),
                target_baskets=sorted({s.sheet for s, keep in zip(shots, target) if keep}),
                disjoint=True, complete=True)


def style_splits(shots):
    primary = [s for s in shots if not s.source_excluded]
    splits = {name: split_record(rows) for name, rows in [('primary', primary), ('all60', shots)]}
    for name, n in [('primary', 57), ('all60', 60)]:
        r = splits[name]
        if (len(r['source'])+len(r['target']) != n or len(r['conditions']) != 12
                or len(r['source_conditions']) != 6 or len(r['target_conditions']) != 6
                or r['source_baskets'] != sorted((basket.SOURCE, basket.TARGET))
                or r['target_baskets'] != r['source_baskets']):
            raise ValueError('unresolved style split identity/counts')
    if (len(splits['all60']['source']), len(splits['all60']['target'])) != (30, 30):
        raise ValueError('complete design style counts drift')
    if any(len(s.condition) != 4 or s.condition[0] != s.sheet
           or parent.STYLE_MAP.get(s.condition[1]) != s.style for s in shots):
        raise ValueError('qualified condition/style mapping drift')
    additions = [dict(identity=s.identity, style=s.style,
                      side='source' if s.style == 'traditional' else 'target',
                      provenance='original source sectioning exclusion; cup-qualified')
                 for s in shots if s.source_excluded]
    return dict(**splits, additions=additions)


def authenticate(source, ancestor, old, recent):
    # One original-file pass, unchanged reader; no historical bootstrap refits.
    shots, receipts, _ = previous.authenticate(source, ancestor, old)
    for name, expected in PARENT_HASHES.items():
        if digest(recent/name) != expected:
            raise ValueError('PR376 pinned artifact mismatch')
    frozen = json.loads((recent/'FREEZE.json').read_text())
    for directory, key in ((REPO, 'code_sha256'), (recent, 'private_input_sha256')):
        for name, expected in frozen[key].items():
            if digest(directory/name) != expected:
                raise ValueError('PR376 frozen code/input drift')
    artifacts = json.loads((recent/'ARTIFACTS.json').read_text())
    if any(digest(recent/name) != value for name, value in artifacts.items()):
        raise ValueError('PR376 artifact receipt drift')
    receipts['PR376'] = dict(artifacts, **{'ARTIFACTS.json': digest(recent/'ARTIFACTS.json')})
    for label, directory in [('PR374', ancestor), ('PR375', old)]:
        for name, expected in frozen['parent_receipts'][label].items():
            if digest(directory/name) != expected:
                raise ValueError('PR376-bound ancestor artifact drift')
    if json.loads(json.dumps([asdict(s) for s in shots])) != json.loads((recent/'SHOTS.json').read_text()):
        raise ValueError('PR376 observations/order drift')
    historical = json.loads((recent/'RESULT.json').read_text())
    if historical['freeze_sha256'] != PARENT_HASHES['FREEZE.json']:
        raise ValueError('PR376 freeze/result linkage drift')
    for name in ('primary', 'unfiltered', 'include_rejected'):
        r = historical[name]
        b = r['bootstrap']
        saved = json.loads((recent/(name+'_bootstrap.json')).read_text())
        if (b['requested'], b['completed'], b['failed'], len(saved)) != (2000, 2000, 0, 2000):
            raise ValueError('PR376 bootstrap completion drift')
        if any(b['active_bound_draws'].values()):
            raise ValueError('PR376 active bounds context drift')
        rows = [s for s in shots if name == 'include_rejected' or not s.source_excluded]
        _, _, _, group = parent.arrays(rows)
        for draw in saved:
            w = np.asarray(draw['multiplicities'])
            if (w.shape != group.shape or np.any(w < 0) or np.any(w != np.floor(w))
                    or any(w[group == g].sum() != (group == g).sum() for g in np.unique(group))):
                raise ValueError('PR376 saved multiplicity receipt invalid')
        for key, c in r['contrasts'].items():
            for q in ('difference', 'gain'):
                values = [d['contrasts'][key][q] for d in saved]
                if (None in values or c[q+'_undefined_draws'] != 0 or
                        not np.allclose(np.percentile(values, [2.5, 97.5]), c[q+'_ci95'], atol=1e-10, rtol=0)):
                    raise ValueError('PR376 saved-draw interval drift')
    return shots, receipts, historical


def inspect(source, ancestor, old, recent, out):
    if out.exists():
        raise ValueError('output exists; use a fresh private evidence directory')
    start = time.monotonic()
    shots, receipts, historical = authenticate(source, ancestor, old, recent)
    splits = style_splits(shots)
    out.mkdir(mode=0o700, parents=True)
    write_json(out/'SHOTS.json', [asdict(s) for s in shots])
    write_json(out/'SPLIT.json', splits)
    write_json(out/'SUPPORT.json', {name: model.support(rows) for name, rows in [
        ('primary', [s for s in shots if not s.source_excluded]), ('all60', shots)]})
    write_json(out/'PREDECESSOR_CONTEXT.json', historical)
    write_json(out/'DISCOVERY.json', dict(source=str(source), predecessors={
        'PR374': str(ancestor), 'PR375': str(old), 'PR376': str(recent)}, output=str(out),
        authority='configured resolver, authenticated receipts; no basename authority', receipts=receipts))
    write_json(out/'INSPECTION.json', dict(original_workbook=True,
        scope='Unchanged observer opened formula/cache views; raw B/C/D/E, metadata A/F/I/J, '
        'repeated headers and exclusion notes for all 60 cup-qualified rows. Exact observations, '
        'identities and order compared to authenticated PR374/375/376 SHOTS.json.',
        private_inspected='Predecessor freeze/results/input/code/artifact receipts; PR375/376 saved '
        'draw intervals checked without refits; PR376 saved global multiplicities checked.',
        inherited_context='Existing card, source provenance, measurement map, manifest and available-data register.',
        inspection_limits='No new PDF/posts/CSV/figure reading, acquisition, corpus audit, or EWP execution.',
        sessions='UNKNOWN', shared_calibration_uncertainty='UNKNOWN', systematic_measurement_uncertainty='UNKNOWN',
        exposure_both_sides=parent.EXPOSURE, metadata_computation_seconds=time.monotonic()-start))
    write_json(out/'INSPECTED.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
        source_sha256=digest(source), parent_receipts=receipts,
        private_input_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(dict(status='INSPECTED_STYLE_SPLIT_NOT_FITTED', split_sha256=digest(out/'SPLIT.json'),
                          support_sha256=digest(out/'SUPPORT.json'))))


def check_inputs(source, ancestor, old, recent, out, frozen):
    if digest(source) != frozen['source_sha256']:
        raise ValueError('original hash drift')
    for name, value in frozen['private_input_sha256'].items():
        if digest(out/name) != value:
            raise ValueError('private frozen input drift')
    for label, directory in [('PR374', ancestor), ('PR375', old), ('PR376', recent)]:
        for name, value in frozen['parent_receipts'][label].items():
            if digest(directory/name) != value:
                raise ValueError('predecessor artifact drift')


def freeze(source, ancestor, old, recent, out):
    if (out/'FREEZE.json').exists():
        raise ValueError('freeze exists; never overwrite')
    inspected = json.loads((out/'INSPECTED.json').read_text())
    check_inputs(source, ancestor, old, recent, out, inspected)
    old_freeze = json.loads((recent/'FREEZE.json').read_text())
    (out/'METHODS.md').write_bytes((REPO/FILES[-1]).read_bytes())
    write_json(out/'ENVIRONMENT.json', dict(python=platform.python_version(), numpy=np.__version__,
                                          scipy=scipy.__version__, openpyxl=openpyxl.__version__))
    record = dict(task=TASK, timestamp_utc=datetime.now(timezone.utc).isoformat(), pw_main=MAIN,
                  pw_parent_and_branch_base=PARENT, pr375_ancestor=previous.PARENT,
                  pr374_ancestor=previous.previous.PARENT, ewp_read_only_sha=EWP,
                  source_sha256=digest(source), membership_sha256=previous.previous.MEMBERSHIP,
                  split_sha256=digest(out/'SPLIT.json'), support_sha256=digest(out/'SUPPORT.json'),
                  parent_receipts=inspected['parent_receipts'], exposure_both_sides=parent.EXPOSURE,
                  code_sha256={p: digest(REPO/p) for p in FILES+list(old_freeze['code_sha256'])},
                  private_input_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()},
                  seed=20261026, draws=2000, bounds=[0, 100], transfer_status='NOT_RUN',
                  conditions=[6, 6], flush_measurements_excluded=10,
                  decision_authority='METHODS.md; P/N absolute RMSE difference CI against zero',
                  sensitivities=['unfiltered', 'all60', 'source/target condition deletion'])
    write_json(out/'FREEZE.json', record)
    print(json.dumps(dict(status='FROZEN_TRANSFER_NOT_RUN', freeze_sha256=digest(out/'FREEZE.json'),
                          split_sha256=record['split_sha256'])))


def reproduce_primary(shots, recent):
    primary = [s for s in shots if not s.source_excluded]
    source, target = basket.split(primary)
    x, y, style, group = parent.arrays(primary)
    f = basket.fit_source(x[source], y[source], style[source], oracle=True)
    pred = basket.predict(f, x[target], style[target])
    metric = pooled.scores(y[target], pred, group[target])
    saved = json.loads((recent/'RESULT.json').read_text())['primary']
    identities = [s.identity for s, keep in zip(primary, target) if keep]
    if identities != [(p['sheet'], p['row']) for p in saved['predictions']]:
        raise ValueError('PR376 point evaluation identity drift')
    errors = [abs(metric[a][k]-v) for a in basket.ARMS for k, v in saved['scores'][a].items()]
    errors += [abs(pred[i, j]-p['predictions'][a]) for i, p in enumerate(saved['predictions'])
               for j, a in enumerate(basket.ARMS)]
    maximum = float(max(errors))
    if maximum > 1e-10:
        raise ValueError('necessary PR376 primary point reproduction failed')
    return dict(status='PASS', max_absolute_difference_pp=maximum, point_reproductions=1,
                historical_bootstrap_reruns=0)


def report(result):
    p = result['primary']
    interval = previous.interval
    lines = [f"# {p['decision']}", '',
             f"Unfiltered: {result['unfiltered']['decision']}; all-60: {result['include_rejected']['decision']}. "
             +result['sensitivity_qualification'], '',
             f"Pocket Science Coffee (2024). Traditional/Niche Zero {p['training_n']} shots/6 conditions "
             f"train → turbo/Superjolly MP64 {p['evaluation_n']} shots/6 conditions evaluate, both baskets. "
             'All-60: 30→30; ten separate flushes excluded. Original sectioning rejects added by actual style: '
             +'; '.join(f"Sworks row {a['identity'][1]} → {a['side']} ({a['style']})"
                        for a in result['split']['additions'])+'.', '',
             'x=measured dose/final beverage (raw D/E g→kg); filtered raw B including B54; '
             'unfiltered sensitivity fits/evaluates C separately. Nominal refractometer-equivalent '
             'solute/solution mass; absolute TDS percentage points, no density conversion. EY, '
             'regional assays and historical Y54 are not inputs.', '',
             '| Analysis | P RMSE | N RMSE | Delta pp [95% CI] | Gain % [95% CI] | Point / CI grades |',
             '|---|---:|---:|---|---|---|']
    for name in ('primary', 'unfiltered', 'include_rejected'):
        r = result[name]
        c = r['contrasts']['P/N']
        lines.append(f"| {name} | {r['scores']['P']['rmse']:.6f} | {r['scores']['N']['rmse']:.6f} | "
                     f"{interval(c, 'difference')} | {interval(c, 'gain', 100)} | "
                     f"{c['grade']} / {','.join(c['ci_grades'])} |")
    lines += ['', '| Primary | MAE | Bias (prediction−observation) | Condition-balanced RMSE |',
              '|---|---:|---:|---:|']
    for a in model.ARMS:
        lines.append('| '+a+' | '+' | '.join(f"{p['scores'][a][k]:.6f}" for k in
                                           ('mae', 'bias', 'condition_balanced_rmse'))+' |')
    lines += ['', 'Negative delta favors P; positive gain favors P. Both independently fit one scalar '
              'on traditional physical-shot SSE, bounds [0,100]. M/C are unavailable from traditional-only '
              'training and remain unfitted. No nested-model assertion or adequacy margin.', '',
              'Influence ranges (not CIs):']
    for side, r in result['deletion']['influence_ranges_not_ci'].items():
        lines.append(f"{side}: delta {r['difference']}; gain {r['gain']}; "
                     f"sign reversals {r['sign_reversals']}, ties {r['ties']}.")
    lines += ['', '| Lower / upper boundary | Primary point / CI | Unfiltered point / CI | All-60 point / CI |',
              '|---|---|---|---|']
    for i, b in enumerate(p['contrasts']['P/N']['boundary_check']):
        row = [f"{b['lower']}/{b['upper']}"]
        for name in ('primary', 'unfiltered', 'include_rejected'):
            z = result[name]['contrasts']['P/N']['boundary_check'][i]
            row.append(z['point']+' / '+','.join(z['ci_grades']))
        lines.append('| '+' | '.join(row)+' |')
    support = p['support']['overall']
    lines += ['', 'Nine boundary checks reclassify unchanged gains; descriptive only, not sensor-error '
              'robustness or practical acceptance. Primary x support: traditional '+str(support['source_range'])+
              '; turbo '+str(support['target_range'])+f"; {support['target_extrapolation_count']} extrapolations retained. "
              'Basket/preparation support, missing-support flags, all predictions, adverse cases and '
              'condition/basket errors are in JSON.', '',
              parent.EXPOSURE+' on BOTH sides. Used means expose their underlying shots; training exclusion '
              'does not restore blindness. Style, grinder, recipe and duration are confounded. This tests '
              'conditional reuse within one observed campaign/direction; basket and LOCO conclusions remain unchanged.', '',
              'Original workbook formula/cache views inspected; all 60 cup rows/order matched authenticated '
              'PR374–376 SHOTS. Freeze/results/artifact receipts and saved PR375/376 intervals authenticated '
              'without historical bootstrap reruns; one PR376 point replay passed. No new post/PDF/export/figure '
              'inspection or acquisition. Sessions, shared calibration and systematic uncertainty UNKNOWN.', '',
              'Paired campaigns (requested/completed/failed/undefined delta/undefined gain; active bounds P,N): '
              +'; '.join(f"{n} {r['bootstrap']['requested']}/{r['bootstrap']['completed']}/"
                  f"{r['bootstrap']['failed']}/{r['contrasts']['P/N']['difference_undefined_draws']}/"
                  f"{r['contrasts']['P/N']['gain_undefined_draws']}; "
                  f"{r['bootstrap']['active_bound_draws']['P']},{r['bootstrap']['active_bound_draws']['N']}"
                  for n, r in result.items() if n in ('primary', 'unfiltered', 'include_rejected'))+
              '. Seed 20261026; point active bounds '+str(p['source_fit']['active_bounds'])+
              '. Common global condition multiplicities refit source and score target. '
              'Percentile intervals condition on six source/six target conditions, within-condition exchangeability '
              'and the selected family. They include fit/sampling variation, omit unknown sessions, shared systematic '
              'error and previous selection uncertainty; not simultaneous or new-campaign validation.', '',
              'SciPy bounded least-squares agreement ≤1e-10 pp checks arithmetic, not measurement precision '
              'or independent human review. One implementation/review cycle; freeze precedes fits; full private '
              'JSON/CSVs/draws and ARTIFACTS hashes support reproduction. P1 blind-TDS=OPEN. Next candidate only: '
              'SCI-MD-POCKETSCIENCE-CROSS-DISPERSION-TDS-001; not executed. Reassess if genuinely unexposed '
              'existing data become executable.']
    return '\n'.join(lines)+'\n'


def exports(out, result):
    names = ('primary', 'unfiltered', 'include_rejected')
    for name in names:
        fields = ['sheet', 'row', 'condition', 'style', 'target_pp', 'x', 'P_prediction_pp', 'N_prediction_pp']
        with (out/(name+'_predictions.csv')).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for row in result[name]['predictions']:
                r = {k: row[k] for k in fields[:6]}
                r['condition'] = json.dumps(r['condition'])
                r.update({a+'_prediction_pp': row['predictions'][a] for a in model.ARMS})
                writer.writerow(r)
    for filename, key in [('SCORES.csv', 'scores'), ('CONTRASTS.csv', 'contrasts')]:
        rows = [dict(analysis=n, arm_or_contrast=k, **v) for n in names for k, v in result[n][key].items()]
        with (out/filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in r.items()}
                             for r in rows)


def run(source, ancestor, old, recent, out):
    if any((out/n).exists() for n in ('RESULT.json', 'INCOMPLETE.json', 'ATTEMPT.json')):
        raise ValueError('attempt exists; never overwrite or silently rerun')
    frozen = json.loads((out/'FREEZE.json').read_text())
    check_inputs(source, ancestor, old, recent, out, frozen)
    for name, value in frozen['code_sha256'].items():
        if digest(REPO/name) != value:
            raise ValueError('frozen scientific code/method drift')
    shots = [parent.Shot(**dict(s, condition=tuple(s['condition'])))
             for s in json.loads((out/'SHOTS.json').read_text())]
    primary = [s for s in shots if not s.source_excluded]
    if parent.membership_hash(primary) != frozen['membership_sha256']:
        raise ValueError('primary membership drift')
    if json.loads(json.dumps(style_splits(shots))) != json.loads((out/'SPLIT.json').read_text()):
        raise ValueError('style split drift')
    start = time.monotonic()
    metadata_seconds = json.loads((out/'INSPECTION.json').read_text())['metadata_computation_seconds']
    deadline = start+1800-metadata_seconds
    write_json(out/'ATTEMPT.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), status='STARTED'))
    result = dict(task=TASK, pw_main=MAIN, pw_parent=PARENT, ewp_sha=EWP,
                  freeze_sha256=digest(out/'FREEZE.json'), exposure_both_sides=parent.EXPOSURE,
                  split=json.loads((out/'SPLIT.json').read_text()), sessions='UNKNOWN',
                  shared_calibration_uncertainty='UNKNOWN', systematic_measurement_uncertainty='UNKNOWN')
    try:
        result['predecessor_point_reproduction'] = reproduce_primary(shots, recent)
        for name, cohort, observation in [('primary', primary, 'filtered'),
                                          ('unfiltered', primary, 'unfiltered'),
                                          ('include_rejected', shots, 'filtered')]:
            r = model.evaluate(cohort, observation, deadline=deadline)
            result[name] = r
            write_json(out/(name+'_bootstrap.json'), r.pop('bootstrap_samples'))
            if r['bootstrap']['failed'] or r['bootstrap']['not_run']:
                raise ValueError('paired inference INCOMPLETE; failed or unattempted draws')
        result['deletion'] = model.deletion_influence(primary, result['primary'])
        changed = [name for name in ('unfiltered', 'include_rejected')
                   if result[name]['decision'] != result['primary']['decision']]
        reversals = sum(r['sign_reversals'] for r in result['deletion']['influence_ranges_not_ci'].values())
        result['sensitivity_qualification'] = ('Decision changes: '+', '.join(changed)+'. ' if changed else
            'Observation and cohort sensitivities preserve the primary decision. ')+(
            f'{reversals} condition-deletion sign reversals; influence diagnostics do not replace the primary CI.')
        result['scientific_computation_seconds'] = time.monotonic()-start+metadata_seconds
        if time.monotonic() > deadline:
            raise ValueError('scientific computation cap exhausted')
        result['status'] = 'COMPLETED_PRIVATE'
        write_json(out/'RESULT.json', result)
        (out/'RESULT.md').write_text(report(result))
        p = result['primary']
        summary = (f"{p['decision']}. A dose-to-beverage scaling coefficient learned from "
                   f"{p['training_n']} traditional shots was compared with an independently learned constant "
                   f"on {p['evaluation_n']} turbo shots. "+result['sensitivity_qualification']+
                   ' Both baskets are represented. All targets were historically exposed, and predictions '
                   'require measured final beverage mass. Style, grinder, recipe and duration are confounded. '
                   'This is one retrospective campaign, not blind or causal validation. Unknown session '
                   'dependence and shared measurement uncertainty are omitted. Earlier basket and LOCO '
                   'results remain unchanged. Pocket Science Coffee (2024). P1 blind-TDS remains OPEN.')
        (out/'SUMMARY.md').write_text(summary+'\n')
        exports(out, result)
    except (ValueError, OSError, np.linalg.LinAlgError) as exc:
        result.update(status='INCOMPLETE', blocker=str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
        write_json(out/'INCOMPLETE.json', result)
        raise
    finally:
        write_json(out/'ARTIFACTS.json', {p.name: digest(p) for p in sorted(out.iterdir())
                                        if p.is_file() and p.name != 'ARTIFACTS.json'})
    print(json.dumps(dict(status='COMPLETED_PRIVATE', result_sha256=digest(out/'RESULT.json'))))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('inspect', 'freeze', 'run'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--predecessor', type=Path, help='Narrow explicit private PR376 bundle locator')
    args = parser.parse_args()
    try:
        locations_resolved = locations(args.output, args.predecessor)
        {'inspect': inspect, 'freeze': freeze, 'run': run}[args.command](*locations_resolved)
    except (OSError, ValueError, KeyError) as exc:
        # Exception paths/configuration are never emitted; detailed evidence stays private.
        reason = str(exc) if isinstance(exc, ValueError) else type(exc).__name__
        print(json.dumps(dict(status='BLOCKED_NOT_RUN_OR_INCOMPLETE', blocker=reason)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

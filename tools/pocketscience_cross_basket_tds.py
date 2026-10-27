#!/usr/bin/env python3
"""Frozen private transfer runner; stdout contains safe hashes/status only."""
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
from tools import pocketscience_pooled_scaling as previous  # noqa: E402
from puckworks.analysis import pocketscience_cup_tds as parent  # noqa: E402
from puckworks.analysis import pocketscience_pooled_scaling as pooled  # noqa: E402
from puckworks.analysis import pocketscience_cross_basket_tds as model  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-CROSS-BASKET-TDS-001'
PARENT = '9f8c6c7cf894872908f3ea212c69209db13c602a'
MAIN, EWP = previous.MAIN, previous.EWP
PARENT_HASHES = {
    'FREEZE.json': 'cdad2b189075198368efdcd5b46953df4ef0d38a20a662ff4e24ebb160c595e5',
    'RESULT.json': 'fdf422e40b9ccd7598c3d99be10a211a6a41b342c89943a9a87232845811d868'}
FILES = ['puckworks/analysis/pocketscience_cross_basket_tds.py',
         'tools/pocketscience_cross_basket_tds.py', 'tests/test_pocketscience_cross_basket_tds.py',
         'docs/analysis/sci_md_pocketscience_cross_basket_tds_001/METHODS.md']
digest, write_json = previous.digest, previous.write_json


def locations(output=None):
    source, ancestor, old = previous.locations()
    out = output.resolve() if output else old.parent/TASK
    source, ancestor, old = source.resolve(), ancestor.resolve(), old.resolve()
    if (out.is_relative_to(REPO) or out.is_relative_to(source.parent.parent)
            or any(out.is_relative_to(p) or p.is_relative_to(out) for p in (ancestor, old))):
        raise ValueError('new evidence must be external and separate from predecessors/source')
    return source, ancestor, old, out


def authenticate(source, ancestor, old):
    receipts = {}
    for label, directory, expected in [('PR374', ancestor, previous.PARENT_HASHES),
                                        ('PR375', old, PARENT_HASHES)]:
        for name, value in expected.items():
            if digest(directory/name) != value:
                raise ValueError(label+' '+name+' hash mismatch')
        frozen = json.loads((directory/'FREEZE.json').read_text())
        for name, value in frozen['code_sha256'].items():
            if digest(REPO/name) != value:
                raise ValueError(label+' scientific code drift')
        for name, value in frozen['private_input_sha256'].items():
            if digest(directory/name) != value:
                raise ValueError(label+' private input drift')
        artifacts = json.loads((directory/'ARTIFACTS.json').read_text())
        receipts[label] = {name: digest(directory/name) for name in artifacts}
        if receipts[label] != artifacts:
            raise ValueError(label+' artifact receipt drift')
    old_freeze = json.loads((old/'FREEZE.json').read_text())
    for name, expected in old_freeze['parent_receipts'].items():
        if digest(ancestor/name) != expected:
            raise ValueError('PR375-bound PR374 receipt drift')
    shots, failed = parent.read_source(source)
    observed = json.loads(json.dumps([asdict(s) for s in shots]))
    if failed or len(shots) != 60 or any(observed != json.loads((d/'SHOTS.json').read_text())
                                       for d in (ancestor, old)):
        raise ValueError('authenticated observation/order drift')
    primary = [s for s in shots if not s.source_excluded]
    if parent.membership_hash(primary) != previous.MEMBERSHIP:
        raise ValueError('57-shot membership drift')
    if {(s.sheet, s.row) for s in shots if s.source_excluded} != {
            (model.SOURCE, r) for r in (7, 9, 23)}:
        raise ValueError('source rejection provenance drift')
    historical = json.loads((old/'RESULT.json').read_text())
    if historical['freeze_sha256'] != PARENT_HASHES['FREEZE.json']:
        raise ValueError('historical result/freeze linkage mismatch')
    for name in ('primary', 'unfiltered', 'include_rejected'):
        r = historical[name]
        b = r['bootstrap']
        draws = json.loads((old/(name+'_bootstrap.json')).read_text())
        if (b['requested'], b['completed'], b['failed'], len(draws)) != (2000,2000,0,2000):
            raise ValueError('historical bootstrap completion mismatch')
        if any(b['active_bound_draws'].values()):
            raise ValueError('historical active bounds context mismatch')
        for key, c in r['contrasts'].items():
            for q in ('difference', 'gain'):
                values = [d['contrasts'][key][q] for d in draws]
                if None in values or not np.allclose(np.percentile(values, [2.5,97.5]),
                                                     c[q+'_ci95'], atol=1e-10, rtol=0):
                    raise ValueError('historical saved-draw interval mismatch')
    return shots, receipts, historical


def split_record(shots):
    source, target = model.split(shots)
    _, _, _, group = parent.arrays(shots)
    conditions = sorted({s.condition for s in shots})
    return dict(conditions=conditions, global_condition_indices=group.tolist(),
                original_order=[s.identity for s in shots],
                source=[s.identity for i,s in enumerate(shots) if source[i]],
                target=[s.identity for i,s in enumerate(shots) if target[i]],
                source_conditions=sorted(set(group[source].tolist())),
                target_conditions=sorted(set(group[target].tolist())), disjoint=True)


def freeze(source, ancestor, old, out):
    if out.exists():
        raise ValueError('output exists; use a fresh evidence directory')
    shots, receipts, historical = authenticate(source, ancestor, old)
    primary = [s for s in shots if not s.source_excluded]
    splits = {name: split_record(cohort) for name, cohort in [('primary', primary), ('all60', shots)]}
    for name, counts in [('primary',(37,20,8,4)), ('all60',(40,20,8,4))]:
        r = splits[name]
        if tuple(len(r[k]) for k in ('source','target','source_conditions','target_conditions')) != counts:
            raise ValueError('frozen split counts drift')
    if splits['primary']['target'] != splits['all60']['target']:
        raise ValueError('sensitivity evaluation identity drift')
    out.mkdir(mode=0o700, parents=True)
    write_json(out/'SHOTS.json', [asdict(s) for s in shots])
    write_json(out/'SPLIT.json', splits)
    write_json(out/'SUPPORT.json', {name:model.support(cohort) for name,cohort in
                                  [('primary',primary), ('all60',shots)]})
    (out/'METHODS.md').write_bytes((REPO/FILES[-1]).read_bytes())
    write_json(out/'INSPECTION.json', dict(
        original_workbook=True, scope='All 60 cup rows raw B/C/D/E and A/F/I/J, repeated '
        'headers and source exclusion notes; formula/cache views opened by unchanged reader. '
        'Exact identity/order/observations compared to authenticated PR374 and PR375 SHOTS.json.',
        private_inspected=['PR374/375 FREEZE.json, RESULT.json, SHOTS.json, ARTIFACTS.json',
                           'PR375 three saved bootstrap JSONs; percentile intervals recomputed without refits'],
        other_originals_inspected=[], new_source_acquisition=False, figure_reading=False,
        inherited_context='Existing card, measurement map, provenance, manifest and available-data record; '
        'no new reading of source PDFs/posts/CSV exports or expanded grant.',
        sessions='UNKNOWN', shared_calibration_uncertainty='UNKNOWN', exposure_both_sides=parent.EXPOSURE))
    # Retain full-precision historical context explicitly separate from transfer outcomes.
    write_json(out/'PREDECESSOR_CONTEXT.json', {name: historical[name] for name in
                                             ('primary','unfiltered','include_rejected','deletion')})
    write_json(out/'ENVIRONMENT.json', dict(python=platform.python_version(), numpy=np.__version__,
                                          scipy=scipy.__version__, openpyxl=openpyxl.__version__))
    old_freeze = json.loads((old/'FREEZE.json').read_text())
    record = dict(task=TASK, timestamp_utc=datetime.now(timezone.utc).isoformat(),
                  pw_main=MAIN, pw_parent_and_branch_base=PARENT, pr374_ancestor=previous.PARENT,
                  ewp_read_only_sha=EWP, source_sha256=digest(source),
                  membership_sha256=previous.MEMBERSHIP, exposure_both_sides=parent.EXPOSURE,
                  split_sha256=digest(out/'SPLIT.json'), parent_receipts=receipts,
                  code_sha256={p:digest(REPO/p) for p in FILES+list(old_freeze['code_sha256'])},
                  private_input_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},
                  seed=20261026, draws=2000, bounds=[0,100], transfer_status='NOT_RUN',
                  source_counts=[37,8], evaluation_counts=[20,4], all60_source_counts=[40,8],
                  flush_measurements_excluded=10, model_and_decision_authority='METHODS.md')
    write_json(out/'FREEZE.json', record)
    print(json.dumps(dict(status='FROZEN_TRANSFER_NOT_RUN', freeze_sha256=digest(out/'FREEZE.json'),
                          split_sha256=record['split_sha256'])))


def reproduce_primary(shots, old):
    x,y,s,g = parent.arrays([v for v in shots if not v.source_excluded])
    pred, _, _ = pooled.joint_predict(x,y,s,g,oracle=True)
    saved = json.loads((old/'RESULT.json').read_text())['primary']
    metrics = pooled.scores(y,pred,g)
    errors = [abs(metrics[a][k]-v) for a in model.ARMS for k,v in saved['scores'][a].items()]
    for i, p in enumerate(saved['predictions']):
        errors.extend(abs(pred[i,j]-p['predictions'][a]) for j,a in enumerate(model.ARMS))
    maximum = float(max(errors))
    if maximum > 1e-10:
        raise ValueError('necessary predecessor point reproduction failed')
    return dict(status='PASS', max_absolute_difference_pp=maximum, loco_bootstrap_reruns=0)


def interval(c, q, scale=1):
    v, ci = c[q], c[q+'_ci95']
    if v is None:
        return 'undefined'
    return f'{v*scale:.6f} '+(f'[{ci[0]*scale:.6f}, {ci[1]*scale:.6f}]' if ci else '[unavailable]')


def report(result):
    p = result['primary']
    lines = [f"# {p['decision']}", '',
             f"Filtered primary; unfiltered: {result['unfiltered']['decision']}; all-60: "
             f"{result['include_rejected']['decision']}. Condition deletions are influence diagnostics "
             '(ranges/reversals below), not confidence intervals.', '',
             'Pocket Science Coffee (2024). 37 Sworks shots/8 conditions train; 20 VST shots/4 conditions '
             'evaluate; one campaign, 57 physical shots. Ten flushes excluded. All-60 adds three '
             'cup-qualified Sworks sectioning rejects (rows 7,9,23), giving 40→20. Raw B including B54; '
             'D/E grams→kg; x=dose/final beverage. Nominal refractometer-equivalent solute/solution mass; '
             'TDS percentage points, no density conversion. Unfiltered refits/evaluates raw C.', '',
             parent.EXPOSURE+' on BOTH sides. Earlier means, selection and LOCO exposed targets; '
             'procedural exclusion does not restore blindness. Brass/teflon Sworks versus teflon VST; '
             'styles confounded with grinders. No isolated basket effect, unseen-campaign generalization, '
             'causality, practical adequacy or production readiness.', '',
             'Inspected original workbook formula/cache views and all 60 cup rows against authenticated '
             'PR374/375 inputs/order; private freeze/results/artifact receipts and saved PR375 draws. '
             'No new PDF/post/figure/export reading. Sessions and shared calibration uncertainty UNKNOWN.', '',
             '| Arm | RMSE | MAE | Bias | Balanced RMSE |', '|---|---:|---:|---:|---:|']
    for a in ('P','M','C','N'):
        s = p['scores'][a]
        lines.append('| '+a+' | '+' | '.join(f'{s[k]:.6f}' for k in
                                           ('rmse','mae','bias','condition_balanced_rmse'))+' |')
    lines += ['', '| Contrast | Difference pp [95% CI] | Gain % [95% CI] | Point / CI grades |',
              '|---|---|---|---|']
    for key,c in p['contrasts'].items():
        lines.append(f"| {key} | {interval(c,'difference')} | {interval(c,'gain',100)} | "
                     f"{c['grade']} / {','.join(c['ci_grades'])} |")
    lines += ['', 'Negative difference favors numerator; positive gain favors numerator. P/N one '
              'coefficient each; M/C two each; M/P tests extra fitting freedom. All source-only bounded '
              '[0,100] physical-shot SSE fits. Coefficients are operational. Primary uses P−N absolute '
              'RMSE CI against zero; secondary contrasts never replace it. Unresolved is not equivalence '
              'or noninferiority. Favorable P/N does not establish P best among four.', '']
    for name in ('unfiltered','include_rejected'):
        c = result[name]['contrasts']['P/N']
        lines.append(f"{name} P/N: difference {interval(c,'difference')} pp; gain {interval(c,'gain',100)}%.")
    for side, values in result['deletion']['influence_ranges_not_ci'].items():
        lines.append(side+' deletion gain ranges/reversals: '+ '; '.join(
            f"{k} {v['gain'][0]*100:.2f}…{v['gain'][1]*100:.2f}%/{v['sign_reversals']}"
            for k,v in values.items())+'.')
    lines += ['', 'Nine boundary checks (lower/upper; entries point:CI; W=worse,S=small,M=moderate,L=large):',
              '', '| Boundaries | P/N | M/P | M/C | C/N |', '|---|---|---|---|---|']
    codes = dict(worse='W',small='S',moderate='M',large='L',undefined='U')
    for i,b in enumerate(p['contrasts']['P/N']['boundary_check']):
        row = [f"{b['lower']}/{b['upper']}"]
        for c in p['contrasts'].values():
            z = c['boundary_check'][i]
            row.append(codes[z['point']]+':'+''.join(codes[v] for v in z['ci_grades']))
        lines.append('| '+' | '.join(row)+' |')
    lines += ['', 'Descriptive boundaries only, not measurement robustness/adequacy. Every analysis uses '
              '2,000 paired fixed-condition draws, seed 20261026; shared physical-shot multiplicities '
              'refit source and score target. Completion/failed/active counts: '+ '; '.join(
                  f"{n} {r['bootstrap']['completed']}/{r['bootstrap']['failed']}/"
                  f"{sum(r['bootstrap']['active_bound_draws'].values())}" for n,r in result.items()
                  if n in ('primary','unfiltered','include_rejected'))+'. '
              'Undefined counts, source coefficients, coverage, support/extrapolation, condition errors, '
              'adverse cases and draws are in JSON/CSV. Intervals condition on fixed conditions, selected '
              'family and within-condition exchangeability; include source-fit/target-sampling variation, '
              'omit unknown sessions, systematic measurement and previous-selection uncertainty; '
              'not simultaneous or new-campaign validation.', '',
              'Independent bounded numerical solvers and nesting checks pass; primary historical '
              'point replay agrees within 1e-10, no historical bootstrap rerun. One author implementation/review '
              'cycle, no independent human review. Freeze/support precede transfer fitting. Reproduce with '
              '`tools/pocketscience_cross_basket_tds.py freeze` then `run`; hashes in FREEZE/ARTIFACTS. '
              'P1 blind-TDS=OPEN. Next candidate only: SCI-MD-POCKETSCIENCE-CROSS-STYLE-TDS-001; '
              'not executed; reprioritize if genuinely unexposed existing data become executable.']
    return '\n'.join(lines)+'\n'


def exports(out, result):
    for name in ('primary','unfiltered','include_rejected'):
        previous.export_csv(out,name,result[name])
    for filename, key in [('SCORES.csv','scores'),('CONTRASTS.csv','contrasts')]:
        rows = [dict(analysis=n, arm_or_contrast=k, **v) for n in
                ('primary','unfiltered','include_rejected') for k,v in result[n][key].items()]
        with (out/filename).open('w',newline='') as stream:
            writer = csv.DictWriter(stream,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()}
                             for r in rows)


def run(source, ancestor, old, out):
    if (out/'RESULT.json').exists() or (out/'INCOMPLETE.json').exists():
        raise ValueError('result/attempt exists; do not overwrite')
    frozen = json.loads((out/'FREEZE.json').read_text())
    if digest(source) != frozen['source_sha256']:
        raise ValueError('source hash drift')
    for directory,key in ((REPO,'code_sha256'),(out,'private_input_sha256')):
        for name,expected in frozen[key].items():
            if digest(directory/name) != expected:
                raise ValueError('frozen '+key+' drift')
    for label,directory in [('PR374',ancestor),('PR375',old)]:
        for name,expected in frozen['parent_receipts'][label].items():
            if digest(directory/name) != expected:
                raise ValueError('predecessor artifact changed')
    shots = [parent.Shot(**dict(s,condition=tuple(s['condition'])))
             for s in json.loads((out/'SHOTS.json').read_text())]
    primary = [s for s in shots if not s.source_excluded]
    if parent.membership_hash(primary) != previous.MEMBERSHIP:
        raise ValueError('membership drift')
    start = time.monotonic()
    result = dict(task=TASK,pw_main=MAIN,pw_parent=PARENT,ewp_sha=EWP,exposure=parent.EXPOSURE,
                  freeze_sha256=digest(out/'FREEZE.json'),sessions='UNKNOWN',
                  shared_calibration_uncertainty='UNKNOWN')
    try:
        result['predecessor_point_reproduction'] = reproduce_primary(shots,old)
        for name,cohort,observation in [('primary',primary,'filtered'),
                                         ('unfiltered',primary,'unfiltered'),
                                         ('include_rejected',shots,'filtered')]:
            r = model.evaluate(cohort,observation,deadline=start+1800)
            result[name] = r
            write_json(out/(name+'_bootstrap.json'),r.pop('bootstrap_samples'))
            if r['bootstrap']['failed']:
                raise ValueError('failed paired bootstrap draws; inferential decision incomplete')
        result['deletion'] = model.deletion_influence(primary,result['primary'])
        result['scientific_computation_seconds'] = time.monotonic()-start
        if result['scientific_computation_seconds'] > 1800:
            raise ValueError('scientific computation budget exceeded')
        write_json(out/'RESULT.json',result)
        (out/'RESULT.md').write_text(report(result))
        summary = (f"{result['primary']['decision']}. In this retrospective comparison, four models "
                   'were fitted only to 37 Sworks shots and evaluated on 20 VST shots. '
                   f"Unfiltered sensitivity: {result['unfiltered']['decision']}; including three "
                   f"additional cup-qualified source shots: {result['include_rejected']['decision']}. "
                   'Condition-influence ranges are reported separately. These targets were already '
                   'exposed; predictions depend on measured final beverage mass. Basket, dispersion '
                   'and style/grinder differences remain confounded. This does not establish blind '
                   'validation, practical adequacy or production readiness. Pocket Science Coffee (2024).')
        (out/'SUMMARY.md').write_text(summary+'\n')
        exports(out,result)
        write_json(out/'ARTIFACTS.json',{p.name:digest(p) for p in sorted(out.iterdir())
                                       if p.is_file() and p.name!='ARTIFACTS.json'})
    except (ValueError, OSError, np.linalg.LinAlgError) as exc:
        result.update(status='INCOMPLETE',blocker=str(exc) if isinstance(exc,ValueError) else type(exc).__name__)
        write_json(out/'INCOMPLETE.json',result)
        raise
    print(json.dumps(dict(status='COMPLETED_PRIVATE',result_sha256=digest(out/'RESULT.json'))))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('freeze','run'))
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    try:
        (freeze if args.command=='freeze' else run)(*locations(args.output))
    except (OSError,ValueError,KeyError) as exc:
        reason = str(exc) if isinstance(exc,ValueError) else type(exc).__name__
        print(json.dumps(dict(status='NOT_RUN_OR_INCOMPLETE',blocker=reason)),file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

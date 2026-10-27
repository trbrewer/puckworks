#!/usr/bin/env python3
"""Frozen private Sworks dispersion transfer; emit safe status/hashes only."""
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
from tools import pocketscience_cross_style_tds as previous  # noqa: E402
from puckworks.analysis import pocketscience_cup_tds as parent  # noqa: E402
from puckworks.analysis import pocketscience_cross_style_tds as historical_style  # noqa: E402
from puckworks.analysis import pocketscience_cross_dispersion_tds as model  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-CROSS-DISPERSION-TDS-001'
PARENT = '499930653969f473136b2c5303b00d09b8945c68'
IMPLEMENTATION_PARENT = '561abeae2dde5d9df4f180195640b13cd802a5e3'
MAIN, EWP = previous.MAIN, previous.EWP
ANCESTOR_MEMBERSHIP = '1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196'
PARENT_HASHES = {
    'FREEZE.json': 'a456a657230267bc936a1137cf3535ae617b6a35136617d1a0db5c85fb4b523b',
    'RESULT.json': 'a3260b74acbf890c1328c5d41e8e129a6419ad51484d3b1c1e87ebdff91bc428',
    'SPLIT.json': '4b190297c13dbc66a9c520893d2b471c8c17e195ac7f1db990faa6a79e4dda46'}
FILES = ['puckworks/analysis/pocketscience_cross_dispersion_tds.py',
         'tools/pocketscience_cross_dispersion_tds.py', 'tests/test_pocketscience_cross_dispersion_tds.py',
         'docs/analysis/sci_md_pocketscience_cross_dispersion_tds_001/METHODS.md']
ANALYSES = ('primary', 'unfiltered', 'ALL40_SWORKS')
digest, write_json = previous.digest, previous.write_json


def locations(output=None, predecessor=None):
    source, a, b, c, default = previous.locations()
    recent = (predecessor or default).resolve()
    directories = dict(PR374=a, PR375=b, PR376=c, PR377=recent)
    out = output.resolve() if output else recent.parent/TASK
    if (out.is_relative_to(REPO) or out.is_relative_to(source.parent.parent)
            or any(out.is_relative_to(p) or p.is_relative_to(out) for p in directories.values())):
        raise ValueError('fresh private evidence must be separate from source/checkout/predecessors')
    return source, directories, out


def cohorts(shots):
    sworks = [s for s in shots if s.sheet == model.BASKET]
    primary = [s for s in sworks if not s.source_excluded]
    if len(sworks) != 40 or len(primary) != 37:
        raise ValueError('Sworks subset membership/count drift')
    if {(s.sheet, s.row) for s in sworks if s.source_excluded} != {
            (model.BASKET, r) for r in (7, 9, 23)}:
        raise ValueError('original source exclusion provenance drift')
    return primary, sworks


def split_record(shots):
    source, target = model.split(shots)
    _, _, _, group = parent.arrays(shots)
    return dict(conditions=sorted({s.condition for s in shots}),
                global_condition_indices=group.tolist(), original_order=[s.identity for s in shots],
                source=[s.identity for s, keep in zip(shots, source) if keep],
                target=[s.identity for s, keep in zip(shots, target) if keep],
                training_conditions=sorted(set(group[source].tolist())),
                evaluation_conditions=sorted(set(group[target].tolist())),
                disjoint=True, complete=True, vst_scientific_n=0)


def dispersion_splits(shots):
    primary, all40 = cohorts(shots)
    records = {name: split_record(rows) for name, rows in [('primary', primary), ('ALL40_SWORKS', all40)]}
    for name, n in [('primary', 37), ('ALL40_SWORKS', 40)]:
        r = records[name]
        if (len(r['source'])+len(r['target']) != n or len(r['conditions']) != 8
                or len(r['training_conditions']) != 4 or len(r['evaluation_conditions']) != 4):
            raise ValueError('dispersion split identity/count drift')
    if (len(records['ALL40_SWORKS']['source']), len(records['ALL40_SWORKS']['target'])) != (20, 20):
        raise ValueError('all40 complete dispersion design drift')
    records['additions'] = [dict(identity=s.identity, literal_dispersion=s.condition[3],
        dispersion=model.DISPERSION[s.condition[3]],
        side='source' if model.DISPERSION[s.condition[3]] == 'brass' else 'target',
        provenance='original sectioning exclusion; cup-qualified') for s in all40 if s.source_excluded]
    return records


def authenticate(source, directories):
    # Exactly one original observer pass; ancestors' saved receipts/intervals, no refits.
    shots, receipts, _ = previous.authenticate(source, *(directories[k] for k in ('PR374', 'PR375', 'PR376')))
    recent = directories['PR377']
    for name, expected in PARENT_HASHES.items():
        if not (recent/name).is_file() or digest(recent/name) != expected:
            raise ValueError('PR377 '+name+' unavailable or hash mismatch')
    frozen = json.loads((recent/'FREEZE.json').read_text())
    for directory, key in ((REPO, 'code_sha256'), (recent, 'private_input_sha256')):
        for name, expected in frozen[key].items():
            if digest(directory/name) != expected:
                raise ValueError('PR377 frozen code/input drift')
    for label, values in frozen['parent_receipts'].items():
        for name, expected in values.items():
            if digest(directories[label]/name) != expected:
                raise ValueError('PR377-bound ancestor receipt drift')
    artifacts = json.loads((recent/'ARTIFACTS.json').read_text())
    if any(digest(recent/name) != expected for name, expected in artifacts.items()):
        raise ValueError('PR377 saved artifact receipt drift')
    receipts['PR377'] = dict(artifacts, **{'ARTIFACTS.json': digest(recent/'ARTIFACTS.json')})
    if json.loads(json.dumps([asdict(s) for s in shots])) != json.loads((recent/'SHOTS.json').read_text()):
        raise ValueError('PR377 observation/physical identity/order drift')
    if parent.membership_hash([s for s in shots if not s.source_excluded]) != ANCESTOR_MEMBERSHIP:
        raise ValueError('ancestor 57-shot membership drift')
    if json.loads(json.dumps(previous.style_splits(shots))) != json.loads((recent/'SPLIT.json').read_text()):
        raise ValueError('historical style split drift')
    historical = json.loads((recent/'RESULT.json').read_text())
    if historical['freeze_sha256'] != PARENT_HASHES['FREEZE.json']:
        raise ValueError('PR377 result/freeze linkage drift')
    for name in ('primary', 'unfiltered', 'include_rejected'):
        r = historical[name]
        b = r['bootstrap']
        saved = json.loads((recent/(name+'_bootstrap.json')).read_text())
        if (b['requested'], b['completed'], b['failed'], b['not_run'], len(saved)) != (2000, 2000, 0, 0, 2000):
            raise ValueError('PR377 bootstrap completion drift')
        if any(b['active_bound_draws'].values()):
            raise ValueError('PR377 active-bound context drift')
        rows = [s for s in shots if name == 'include_rejected' or not s.source_excluded]
        _, _, _, group = parent.arrays(rows)
        for d in saved:
            w = np.asarray(d['multiplicities'])
            if (w.shape != group.shape or np.any(w < 0) or np.any(w != np.floor(w))
                    or any(w[group == g].sum() != (group == g).sum() for g in np.unique(group))):
                raise ValueError('PR377 historical multiplicity receipt invalid')
        for c in r['contrasts'].values():
            for q in ('difference', 'gain'):
                values = [d['contrasts']['P/N'][q] for d in saved]
                if (None in values or c[q+'_undefined_draws'] != 0 or
                        not np.allclose(np.percentile(values, [2.5, 97.5]), c[q+'_ci95'], atol=1e-10, rtol=0)):
                    raise ValueError('PR377 saved-draw interval mismatch')
    return shots, receipts, historical


def inspect(source, directories, out):
    if out.exists():
        raise ValueError('output exists; use fresh private evidence')
    out.mkdir(mode=0o700, parents=True)
    start = time.monotonic()
    try:
        shots, receipts, historical = authenticate(source, directories)
        primary, all40 = cohorts(shots)
        # These strings come from raw J through observe_sheet, checked against pinned SHOTS.
        literal_values = sorted({s.condition[3] for s in all40})
        if set(literal_values) != set(model.DISPERSION):
            raise ValueError('unresolved original literal dispersion labels')
        splits = dispersion_splits(shots)
        write_json(out/'SOURCE_SHOTS.json', [asdict(s) for s in shots])
        write_json(out/'SHOTS.json', [asdict(s) for s in all40])
        write_json(out/'DISPERSION_MAP.json', dict(raw_column='J', tuple_index=3,
            literal_values=literal_values, exact_mapping=model.DISPERSION,
            authority='Authenticated original raw J, unchanged observer, exact predecessor SHOTS match; no aliases'))
        write_json(out/'SPLIT.json', splits)
        for name in ('primary', 'ALL40_SWORKS'):
            write_json(out/(name+'_SPLIT.json'), splits[name])
        write_json(out/'SUBSET.json', dict(primary_membership_sha256=parent.membership_hash(primary),
            ALL40_SWORKS_membership_sha256=parent.membership_hash(all40),
            primary_order=[s.identity for s in primary], ALL40_SWORKS_order=[s.identity for s in all40],
            vst_excluded_from_science=20, separate_flushes_excluded=10))
        write_json(out/'SUPPORT.json', {name: model.support(rows) for name, rows in
                                      [('primary', primary), ('ALL40_SWORKS', all40)]})
        write_json(out/'HISTORICAL_STYLE_CONTEXT.json', historical)
        write_json(out/'DISCOVERY.json', dict(source=str(source), predecessors={k: str(v) for k, v in directories.items()},
                                             authority='configured resolver and authenticated receipts; no directory discovery'))
        write_json(out/'INSPECTION.json', dict(original_workbook=True,
            scope='Unchanged reader opened formula/cache views once; all 60 cup rows raw B/C/D/E, '
            'A/F/I/J metadata, repeated headers/exclusions matched authenticated PR374–377 SHOTS in order. '
            'Raw J literal values verified; scientific subset/groups are Sworks only.',
            private_inspected='Predecessor frozen code/input/result/artifact receipts; saved bootstrap '
            'intervals and multiplicities authenticated without historical bootstrap refits.',
            limits='No new source acquisition, figures, PDF/post/export reading, native EWP execution or broad discovery.',
            context='Existing card, measurement map, source provenance, manifest and available-data records.',
            sessions='UNKNOWN', installation_order='UNKNOWN', shared_calibration_and_systematic_error='UNKNOWN',
            exposure_both_sides=parent.EXPOSURE, metadata_seconds=time.monotonic()-start))
        write_json(out/'INSPECTED.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
            source_sha256=digest(source), parent_receipts=receipts,
            private_input_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()}))
    except (OSError, ValueError, KeyError) as exc:
        write_json(out/'BLOCKED.json', dict(status='BLOCKED', transfer='NOT_RUN',
            blocker=str(exc) if isinstance(exc, ValueError) else type(exc).__name__))
        raise
    print(json.dumps(dict(status='AUTHENTICATED_DISPERSION_METADATA_NOT_FITTED',
        subset_sha256=digest(out/'SUBSET.json'), split_sha256=digest(out/'SPLIT.json'),
        literal_mapping_sha256=digest(out/'DISPERSION_MAP.json'))))


def check_inputs(source, directories, out, record):
    if digest(source) != record['source_sha256']:
        raise ValueError('original source hash drift')
    for name, expected in record['private_input_sha256'].items():
        if digest(out/name) != expected:
            raise ValueError('frozen private input drift')
    for label, receipts in record['parent_receipts'].items():
        for name, expected in receipts.items():
            if digest(directories[label]/name) != expected:
                raise ValueError('predecessor artifact drift')


def freeze(source, directories, out):
    if (out/'FREEZE.json').exists() or (out/'BLOCKED.json').exists():
        raise ValueError('freeze/blocker exists; never overwrite')
    inspected = json.loads((out/'INSPECTED.json').read_text())
    check_inputs(source, directories, out, inspected)
    predecessor = json.loads((directories['PR377']/'FREEZE.json').read_text())
    (out/'METHODS.md').write_bytes((REPO/FILES[-1]).read_bytes())
    write_json(out/'ENVIRONMENT.json', dict(python=platform.python_version(), numpy=np.__version__,
                                           scipy=scipy.__version__, openpyxl=openpyxl.__version__))
    subset = json.loads((out/'SUBSET.json').read_text())
    record = dict(task=TASK, timestamp_utc=datetime.now(timezone.utc).isoformat(), pw_main=MAIN,
        pw_branch_base_and_scientific_parent=PARENT, pr377_implementation=IMPLEMENTATION_PARENT,
        pr376_ancestor=previous.PARENT, pr375_ancestor=previous.previous.PARENT,
        pr374_ancestor=previous.previous.previous.PARENT, ewp_read_only_sha=EWP,
        source_sha256=digest(source), ancestor_membership_sha256=ANCESTOR_MEMBERSHIP,
        subset_membership_sha256=subset['primary_membership_sha256'],
        ALL40_SWORKS_membership_sha256=subset['ALL40_SWORKS_membership_sha256'],
        split_sha256=digest(out/'SPLIT.json'),
        split_record_sha256={n: digest(out/(n+'_SPLIT.json')) for n in ('primary', 'ALL40_SWORKS')},
        literal_mapping_sha256=digest(out/'DISPERSION_MAP.json'),
        parent_receipts=inspected['parent_receipts'], exposure_both_sides=parent.EXPOSURE,
        code_sha256={p: digest(REPO/p) for p in FILES+list(predecessor['code_sha256'])},
        private_input_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()},
        seed=20261026, draws=2000, bounds=[0, 100], transfer_status='NOT_RUN',
        comparison_roles={'P/N': 'primary', 'M/C': 'key secondary', 'M/P': 'secondary', 'C/N': 'secondary'},
        conditions=[4, 4], vst_scientific_n=0, decision_authority='METHODS.md',
        sensitivities=['unfiltered', 'ALL40_SWORKS', 'source/target condition influence'])
    write_json(out/'FREEZE.json', record)
    print(json.dumps(dict(status='FROZEN_DISPERSION_NOT_RUN', freeze_sha256=digest(out/'FREEZE.json'),
                          subset_membership_sha256=record['subset_membership_sha256'], split_sha256=record['split_sha256'])))


def historical_point_replay(all_source_shots, recent):
    """One historical style check only; never enters new Sworks fits/groups/scores."""
    shots = [s for s in all_source_shots if not s.source_excluded]
    source, target = historical_style.split(shots)
    x, y, _, group = parent.arrays(shots)
    fit = historical_style.fit_source(x[source], y[source], oracle=True)
    pred = historical_style.predict(fit['coefficients'], x[target])
    metric = historical_style.scores(y[target], pred, group[target])
    saved = json.loads((recent/'RESULT.json').read_text())['primary']
    if [s.identity for s, keep in zip(shots, target) if keep] != [(v['sheet'], v['row']) for v in saved['predictions']]:
        raise ValueError('historical point identity drift')
    errors = [abs(metric[a][k]-v) for a in historical_style.ARMS for k, v in saved['scores'][a].items()]
    errors += [abs(pred[i, j]-v['predictions'][a]) for i, v in enumerate(saved['predictions'])
               for j, a in enumerate(historical_style.ARMS)]
    maximum = float(max(errors))
    if maximum > 1e-10:
        raise ValueError('necessary historical PR377 point replay failed')
    return dict(status='PASS', purpose='HISTORICAL_VERIFICATION_ONLY_NOT_DISPERSION_ANALYSIS',
                max_absolute_difference_pp=maximum, point_replays=1, historical_bootstrap_reruns=0)


def qualification(result):
    p = result['primary']
    changes = {name: {k: dict(primary=v, sensitivity=result[name]['contrast_conclusions'][k])
                     for k, v in p['contrast_conclusions'].items() if result[name]['contrast_conclusions'][k] != v}
               for name in ('unfiltered', 'ALL40_SWORKS')}
    return dict(contrast_conclusion_changes=changes,
                influence_ranges_not_ci=result['deletion']['influence_ranges_not_ci'],
                historical_basket_style_loco_conclusions='UNCHANGED')


def report(result):
    p = result['primary']
    interval = previous.previous.interval
    lines = [f"# {p['decision']}", '', 'M/C: '+p['mc_interpretation']+'. '+
             '; '.join(n+': '+result[n]['decision']+', M/C '+result[n]['mc_interpretation']
                       for n in ('unfiltered', 'ALL40_SWORKS'))+'.', '',
             f"Pocket Science Coffee (2024). {p['training_n']} brass shots → {p['evaluation_n']} teflon shots; "
             'four conditions per side, both styles/preparations, Sworks only. ALL40_SWORKS confirms 20→20. '
             'All 20 VST shots and ten flush measurements are outside new science. Sectioning exclusions added: '
             +'; '.join(f"row {a['identity'][1]}→{a['side']}" for a in result['split']['additions'])+'. '
             'Preparation N means paper on top.', '',
             'x=measured dose/final beverage (D/E g→kg); filtered y=raw B including B54, '
             'separate unfiltered C→C refit. TDS pp: nominal refractometer-equivalent solute/solution mass; '
             'no density conversion, derived EY, regional targets or Y54 substitution.', '',
             '| Primary arm | RMSE | MAE | Bias | Balanced RMSE |', '|---|---:|---:|---:|---:|']
    for a in ('P', 'M', 'C', 'N'):
        lines.append('| '+a+' | '+' | '.join(f"{p['scores'][a][k]:.6f}" for k in
                                          ('rmse', 'mae', 'bias', 'condition_balanced_rmse'))+' |')
    lines += ['', '| Primary contrast | Delta pp [95% CI] | Gain % [95% CI] | Point/CI grades |', '|---|---|---|---|']
    for key, c in p['contrasts'].items():
        lines.append(f"| {key} | {interval(c,'difference')} | {interval(c,'gain',100)} | "
                     f"{c['grade']}/{','.join(c['ci_grades'])} |")
    lines += ['', 'Negative delta/positive gain favor the first arm. P/N fit one scalar each, M/C two; '
              'M/P tests an added coefficient. Source-only bounded [0,100] TDS-SSE fits. '
              'Favorable P/N alone cannot establish scaling beyond style constants or P best among four. '
              'An unresolved M/C leaves incremental scaling unestablished, not absent; no causal attribution.', '',
              '| Sensitivity | RMSE P/M/C/N | P/N delta CI; gain CI | M/C delta CI; gain CI |', '|---|---|---|---|']
    for name in ('unfiltered', 'ALL40_SWORKS'):
        r = result[name]
        values = '/'.join(f"{r['scores'][a]['rmse']:.4f}" for a in ('P','M','C','N'))
        cells = [f"{interval(r['contrasts'][k],'difference')}; {interval(r['contrasts'][k],'gain',100)}%" for k in ('P/N','M/C')]
        lines.append('| '+name+' | '+values+' | '+' | '.join(cells)+' |')
    lines += ['', 'Changed CI conclusions: '+'; '.join(n+': '+(', '.join(k+' '+v['primary']+'→'+v['sensitivity'] for k,v in changes.items()) or 'none') for n,changes in result['sensitivity_qualification']['contrast_conclusion_changes'].items())+'.',
              'Condition influence: point delta ranges, reversals/ties (not CIs):']
    for side, contrasts in result['deletion']['influence_ranges_not_ci'].items():
        lines.append(side+': '+'; '.join(f"{k} [{v['difference'][0]:.4f},{v['difference'][1]:.4f}] "
                     f"{v['sign_reversals']}/{v['ties']}" for k,v in contrasts.items())+'.')
    lines += ['', '| Lower/upper | P/N | M/C | M/P | C/N |', '|---|---|---|---|---|']
    codes = dict(worse='W', small='S', moderate='M', large='L', undefined='U')
    for i, b in enumerate(p['contrasts']['P/N']['boundary_check']):
        cells = [f"{b['lower']}/{b['upper']}"]
        for c in p['contrasts'].values():
            z = c['boundary_check'][i]
            cells.append(codes[z['point']]+':'+''.join(codes[v] for v in z['ci_grades']))
        lines.append('| '+' | '.join(cells)+' |')
    lines += ['', 'Nine unchanged-result boundary checks: point:CI; W/S/M/L=worse/small/moderate/large. '
              'Descriptive boundaries, not sensor robustness or adequacy. Sensitivity grades/all boundary '
              'checks, gain influence ranges, support/flags, predictions, adverse cases and condition/style errors: JSON/CSV.', '',
              parent.EXPOSURE+' on BOTH sides. Earlier means/selection exposed shots; exclusion does not '
              'restore blindness. Fixed basket does not isolate dispersion; installation order, sessions, '
              'shared calibration/systematic differences remain UNKNOWN. No practical adequacy/production claim.', '',
              'Inspected original formula/cache workbook once; all 60 rows/order and literal raw-J mapping '
              'matched authenticated PR374–377 inputs. Private code/input/result/artifact and saved-draw '
              'receipts checked. One separate historical PR377 point replay; zero historical bootstrap reruns. '
              'No new PDFs/posts/exports/figures/acquisition/native EWP runs.', '',
              'Draws requested/completed/failed/not-run; total undefined contrasts; active-bound draws: '+
              '; '.join(f"{n} {r['bootstrap']['requested']}/{r['bootstrap']['completed']}/"
                  f"{r['bootstrap']['failed']}/{r['bootstrap']['not_run']}; "
                  f"{sum(c[q+'_undefined_draws'] for c in r['contrasts'].values() for q in ('difference','gain'))}; "
                  f"{sum(r['bootstrap']['active_bound_draws'].values())}" for n,r in result.items() if n in ANALYSES)+'. '
              'Seed 20261026; common eight-condition shot multiplicities refit brass and score teflon. '
              'Percentile intervals include fit/sampling variability conditional on four/four fixed conditions, '
              'within-condition exchangeability and selected family; omit sessions, shared systematic error '
              'and selection uncertainty. Not simultaneous/new-campaign intervals.', '',
              'Bounded least-squares ≤1e-10 pp and training M/P nesting verify arithmetic, not measurement '
              'precision or independent human review. Freeze/ARTIFACTS bind reproduction. Prior basket/style/LOCO '
              'results unchanged. P1 blind-TDS=OPEN. Next candidate only: SCI-MD-POCKETSCIENCE-AFFINE-TDS-001; '
              'not executed; reprioritize if genuinely unexposed existing data become executable.']
    return '\n'.join(lines)+'\n'


def exports(out, result):
    for name in ANALYSES:
        fields = ['sheet','row','condition','style','target_pp','x']+[a+'_prediction_pp' for a in model.ARMS]
        with (out/(name+'_predictions.csv')).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields); writer.writeheader()
            for p in result[name]['predictions']:
                row = {k:p[k] for k in fields[:6]}; row['condition']=json.dumps(row['condition'])
                row.update({a+'_prediction_pp':p['predictions'][a] for a in model.ARMS}); writer.writerow(row)
    for filename, key in [('SCORES.csv','scores'), ('CONTRASTS.csv','contrasts')]:
        rows = [dict(analysis=n, arm_or_contrast=k, **v) for n in ANALYSES for k,v in result[n][key].items()]
        with (out/filename).open('w', newline='') as stream:
            writer=csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader()
            writer.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in row.items()} for row in rows)


def run(source, directories, out):
    if any((out/n).exists() for n in ('ATTEMPT.json','RESULT.json','INCOMPLETE.json','BLOCKED.json')):
        raise ValueError('attempt/result/blocker exists; never silently rerun')
    frozen=json.loads((out/'FREEZE.json').read_text()); check_inputs(source,directories,out,frozen)
    for name,expected in frozen['code_sha256'].items():
        if digest(REPO/name)!=expected: raise ValueError('frozen scientific code/test/method drift')
    def load_shots(name):
        return [parent.Shot(**dict(s,condition=tuple(s['condition']))) for s in json.loads((out/name).read_text())]
    all40=load_shots('SHOTS.json'); primary,all40=cohorts(all40)
    if parent.membership_hash(primary)!=frozen['subset_membership_sha256']:
        raise ValueError('Sworks primary membership drift')
    if json.loads(json.dumps(dispersion_splits(all40)))!=json.loads((out/'SPLIT.json').read_text()):
        raise ValueError('dispersion partition drift')
    start=time.monotonic(); metadata=json.loads((out/'INSPECTION.json').read_text())['metadata_seconds']
    deadline=start+1800-metadata
    write_json(out/'ATTEMPT.json',dict(status='STARTED',timestamp_utc=datetime.now(timezone.utc).isoformat()))
    result=dict(task=TASK,pw_main=MAIN,pw_parent=PARENT,ewp_sha=EWP,freeze_sha256=digest(out/'FREEZE.json'),
                exposure_both_sides=parent.EXPOSURE,split=json.loads((out/'SPLIT.json').read_text()),
                sessions='UNKNOWN',installation_order='UNKNOWN',shared_calibration_and_systematic_error='UNKNOWN')
    try:
        result['historical_verification']=historical_point_replay(load_shots('SOURCE_SHOTS.json'),directories['PR377'])
        for name,rows,observation in [('primary',primary,'filtered'),('unfiltered',primary,'unfiltered'),('ALL40_SWORKS',all40,'filtered')]:
            r=model.evaluate(rows,observation,deadline=deadline);result[name]=r
            write_json(out/(name+'_bootstrap.json'),r.pop('bootstrap_samples'))
            if r['bootstrap']['failed'] or r['bootstrap']['not_run']:
                raise ValueError('paired inference INCOMPLETE; failed/unattempted draws preserved')
        result['deletion']=model.deletion_influence(primary,result['primary'])
        result['sensitivity_qualification']=qualification(result)
        result['scientific_computation_seconds']=time.monotonic()-start+metadata
        if time.monotonic()>deadline: raise ValueError('scientific computation budget exhausted')
        result['status']='COMPLETED_PRIVATE';write_json(out/'RESULT.json',result)
        (out/'RESULT.md').write_text(report(result));exports(out,result)
        p=result['primary']
        primary_words = {'P_CROSS_DISPERSION_ADDED_VALUE_OVER_N':'Pooled scaling lowered filtered error versus a constant',
            'N_LOWER_CROSS_DISPERSION_LOSS':'The constant lowered filtered error versus pooled scaling',
            'CROSS_DISPERSION_COMPARISON_UNRESOLVED':'The filtered pooled-scaling comparison remains unresolved'}
        mc_words = {'SCALING_ADDED_VALUE_BEYOND_STYLE_CONSTANTS':'Scaling also added value beyond style constants.',
            'STYLE_CONSTANTS_LOWER_LOSS':'Style constants outperformed style-specific scaling.',
            'INCREMENTAL_SCALING_CLAIM_UNESTABLISHED':'Added scaling value beyond style constants remains unestablished.'}
        changed = [n for n in ('unfiltered','ALL40_SWORKS') if result[n]['decision'] != p['decision']]
        reversals=sum(v['P/N']['sign_reversals'] for v in result['deletion']['influence_ranges_not_ci'].values())
        summary=(primary_words[p['decision']]+f" using {p['training_n']} brass training and {p['evaluation_n']} teflon evaluation shots. "
            +mc_words[p['mc_interpretation']]+' Primary decision changes under: '+(', '.join(changed) if changed else 'neither sensitivity')
            +f". {reversals} condition-deletion point reversals occurred. Both styles/preparations used Sworks only. "
            'Targets were already exposed; prediction requires measured beverage mass. Unknown installation order, '
            'sessions and shared measurement effects prevent a causal dispersion claim. Earlier results are unchanged. '
            'Pocket Science Coffee (2024). P1 blind-TDS remains OPEN.')
        (out/'SUMMARY.md').write_text(summary+'\n')
    except (ValueError,OSError,np.linalg.LinAlgError) as exc:
        result.update(status='INCOMPLETE',blocker=str(exc) if isinstance(exc,ValueError) else type(exc).__name__)
        write_json(out/'INCOMPLETE.json',result);raise
    finally:
        write_json(out/'ARTIFACTS.json',{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='ARTIFACTS.json'})
    print(json.dumps(dict(status='COMPLETED_PRIVATE',result_sha256=digest(out/'RESULT.json'))))


def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('inspect','freeze','run'))
    parser.add_argument('--output',type=Path)
    parser.add_argument('--predecessor',type=Path,help='Explicit private PR377 locator; pinned receipts required')
    args=parser.parse_args()
    try:
        {'inspect':inspect,'freeze':freeze,'run':run}[args.command](*locations(args.output,args.predecessor))
    except (OSError,ValueError,KeyError) as exc:
        reason=str(exc) if isinstance(exc,ValueError) else type(exc).__name__
        print(json.dumps(dict(status='BLOCKED_NOT_RUN_OR_INCOMPLETE',blocker=reason)),file=sys.stderr);return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())

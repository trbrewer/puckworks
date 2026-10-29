#!/usr/bin/env python3
"""Frozen private affine LOCO comparison; CLI emits safe status and hashes only."""
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
from tools import pocketscience_cross_dispersion_tds as previous  # noqa: E402
from puckworks.analysis import pocketscience_cup_tds as parent  # noqa: E402
from puckworks.analysis import pocketscience_affine_tds as model  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-AFFINE-TDS-001'
PARENT = '2425223a872e104345a787984ee5874671258368'
PARENT_GIT_PARENT = '499930653969f473136b2c5303b00d09b8945c68'
LOCO_REFERENCE = '9f8c6c7cf894872908f3ea212c69209db13c602a'
MAIN, EWP = previous.MAIN, previous.EWP
MEMBERSHIP = previous.ANCESTOR_MEMBERSHIP
PINS = {'PR375': {
    'FREEZE.json': 'cdad2b189075198368efdcd5b46953df4ef0d38a20a662ff4e24ebb160c595e5',
    'RESULT.json': 'fdf422e40b9ccd7598c3d99be10a211a6a41b342c89943a9a87232845811d868'},
    'PR378': {
    'FREEZE.json': '88d0d110185b1ddb3e2bf1a3abfcd0d01abd927c04655edc2d62ad288883a4ef',
    'RESULT.json': '17e1af2636e697bf9ba9455eab5dc3a658fe01ab0ce560b793224f09a2fa820c'}}
FILES = ['puckworks/analysis/pocketscience_affine_tds.py', 'tools/pocketscience_affine_tds.py',
         'tests/test_pocketscience_affine_tds.py', 'docs/analysis/sci_md_pocketscience_affine_tds_001/METHODS.md']
CONTEXT = ['docs/cards/pocketscience2024.md', 'puckworks/data/pocketscience2024/PROVENANCE.md',
           'docs/data/ESPRESSO_DATA_GUIDE.md', 'docs/data/AVAILABLE_DATA_FIRST_POLICY.md',
           'puckworks/data/MANIFEST.csv', 'puckworks/data/AVAILABLE_DATA_REGISTER.json',
           'docs/analysis/sci_md_radial_obs_001/MEASUREMENT_MAP.md']
ANALYSES = ('primary', 'unfiltered', 'ALL60')
digest, write_json = previous.digest, previous.write_json


def locations(output=None, predecessor=None):
    source, directories, candidate = previous.locations()
    recent = predecessor.resolve() if predecessor else candidate
    # A locator proposes a candidate; these pinned bytes alone establish authority.
    for name, expected in PINS['PR378'].items():
        if not (recent/name).is_file() or digest(recent/name) != expected:
            raise ValueError('actual PR378 bundle unavailable or unauthenticated; explicit predecessor locator required')
    directories = dict(directories, PR378=recent)
    out = output.resolve() if output else recent.parent/TASK
    if (out.is_relative_to(REPO) or out.is_relative_to(source.parent.parent)
            or any(out.is_relative_to(p) or p.is_relative_to(out) for p in directories.values())):
        raise ValueError('fresh evidence must be separate from source, checkout and predecessors')
    return source, directories, out


def cohorts(shots):
    parent.arrays(shots)
    primary = [s for s in shots if not s.source_excluded]
    if len(shots) != 60 or len(primary) != 57:
        raise ValueError('full 57/60 cohort restoration required; not ALL40_SWORKS')
    if {(s.sheet, s.row) for s in shots if s.source_excluded} != {('Sworks High Flow', r) for r in (7, 9, 23)}:
        raise ValueError('original sectioning-exclusion drift')
    for rows, expected in ((primary, (37, 20, 29, 28)), (shots, (40, 20, 30, 30))):
        counts = tuple(sum(s.sheet == v for s in rows) for v in ('Sworks High Flow', 'VST18'))
        counts += tuple(sum(s.style == v for s in rows) for v in parent.STYLES)
        if counts != expected or len({s.condition for s in rows}) != 12:
            raise ValueError('full cohort basket/style/condition drift')
        if any(len(s.condition) != 4 or s.condition[0] != s.sheet
               or parent.STYLE_MAP.get(s.condition[1]) != s.style or s.condition[2] not in ('Y', 'N') for s in rows):
            raise ValueError('unresolved condition identity')
    return primary, shots


def fold_record(shots):
    x, _, style, group = parent.arrays(shots)
    conditions = sorted({s.condition for s in shots})
    records = []
    for g, condition in enumerate(conditions):
        train, held = group != g, group == g
        train_ids = [s.identity for s, keep in zip(shots, train) if keep]
        held_ids = [s.identity for s, keep in zip(shots, held) if keep]
        if set(train_ids) & set(held_ids) or len(train_ids)+len(held_ids) != len(shots):
            raise ValueError('invalid fold separation')
        records.append(dict(condition_index=g, condition=condition, training=train_ids, held=held_ids,
                            training_n=len(train_ids), held_n=len(held_ids),
                            support=model.support_record(x, style, train, held)))
    if sum(len(f['held']) for f in records) != len(shots):
        raise ValueError('incomplete fold coverage')
    return dict(n=len(shots), conditions=conditions, global_condition_indices=group.tolist(),
                original_order=[s.identity for s in shots], folds=records, coverage_per_shot=1)


def authenticate(source, directories):
    shots, receipts, _ = previous.authenticate(source, directories)  # One unchanged original observer pass.
    observed = json.loads(json.dumps([asdict(s) for s in shots]))
    for label in ('PR375', 'PR378'):
        directory = directories[label]
        for name, expected in PINS[label].items():
            if digest(directory/name) != expected:
                raise ValueError(label+' pinned hash drift')
        frozen = json.loads((directory/'FREEZE.json').read_text())
        for root, key in ((REPO, 'code_sha256'), (directory, 'private_input_sha256')):
            for name, expected in frozen[key].items():
                if digest(root/name) != expected:
                    raise ValueError(label+' frozen code/input drift')
        result = json.loads((directory/'RESULT.json').read_text())
        if result['freeze_sha256'] != PINS[label]['FREEZE.json']:
            raise ValueError(label+' result/freeze linkage drift')
        artifacts = json.loads((directory/'ARTIFACTS.json').read_text())
        if any(digest(directory/name) != expected for name, expected in artifacts.items()):
            raise ValueError(label+' saved artifact drift')
        receipts[label] = dict(artifacts, **{'ARTIFACTS.json': digest(directory/'ARTIFACTS.json')})
        source_name = 'SOURCE_SHOTS.json' if label == 'PR378' else 'SHOTS.json'
        if observed != json.loads((directory/source_name).read_text()):
            raise ValueError(label+' full-cohort observation/identity/order drift')
    recent = json.loads((directories['PR378']/'FREEZE.json').read_text())
    for label, bound in recent['parent_receipts'].items():
        if any(digest(directories[label]/name) != expected for name, expected in bound.items()):
            raise ValueError('PR378-bound ancestor receipt drift')
    subset = json.loads((directories['PR378']/'SHOTS.json').read_text())
    if subset != [s for s in observed if s['sheet'] == 'Sworks High Flow'] or len(subset) != 40:
        raise ValueError('PR378 SOURCE_SHOTS/SHOTS distinction drift')
    primary, all60 = cohorts(shots)
    if parent.membership_hash(primary) != MEMBERSHIP:
        raise ValueError('ancestor57 membership drift')
    sequence_receipts = {}
    old = json.loads((directories['PR375']/'RESULT.json').read_text())
    for name, rows in (('primary', primary), ('unfiltered', primary), ('include_rejected', all60)):
        saved = json.loads((directories['PR375']/(name+'_bootstrap.json')).read_text())
        if len(saved) != 2000 or old[name]['bootstrap']['failed'] or old[name]['bootstrap']['completed'] != 2000:
            raise ValueError('PR375 saved campaign incomplete')
        group = parent.arrays(rows)[3]
        rng = np.random.default_rng(20261026)
        for i, draw in enumerate(saved):
            if draw['draw'] != i or draw['multiplicities'] != parent.bootstrap_weights(group, rng).tolist():
                raise ValueError('PR375 saved deterministic multiplicities invalid')
        for key, value in old[name]['contrasts'].items():
            for q in ('difference', 'gain'):
                values = [d['contrasts'][key][q] for d in saved]
                if None in values or not np.allclose(np.percentile(values, [2.5, 97.5]), value[q+'_ci95'], atol=1e-10, rtol=0):
                    raise ValueError('PR375 saved contrast interval drift')
        sequence_receipts[name] = dict(draws=2000, sequence='EXACT', bootstrap_sha256=digest(directories['PR375']/(name+'_bootstrap.json')))
    return shots, receipts, sequence_receipts


def inspect(source, directories, out):
    if out.exists():
        raise ValueError('output exists; use fresh private evidence')
    out.mkdir(parents=True, mode=0o700)
    try:
        shots, receipts, sequence = authenticate(source, directories)
        primary, all60 = cohorts(shots)
        write_json(out/'SHOTS.json', [asdict(s) for s in shots])
        for name, rows in (('primary', primary), ('ALL60', all60)):
            write_json(out/(name+'_FOLDS.json'), fold_record(rows))
        write_json(out/'COHORT.json', dict(primary_membership_sha256=parent.membership_hash(primary),
            ALL60_membership_sha256=parent.membership_hash(all60), primary_n=57, ALL60_n=60,
            primary_basket_counts=[37, 20], ALL60_basket_counts=[40, 20], primary_style_counts=[29, 28],
            ALL60_style_counts=[30, 30], conditions=12, flush_excluded=10,
            additions=[dict(identity=s.identity, condition=s.condition, style=s.style,
                            provenance='original sectioning exclusion; cup-qualified') for s in shots if s.source_excluded]))
        write_json(out/'DISCOVERY.json', dict(source=str(source), predecessors={k: str(v) for k, v in directories.items()},
            authority='Configured candidates authenticated by pinned receipts; no unrelated discovery or basename authority'))
        write_json(out/'INSPECTION.json', dict(original_observer_passes=1,
            scope='Original formula/cache workbook views, all60 raw cup observations/metadata/order compared with '
                  'authenticated PR374–377 full SHOTS and PR378 SOURCE_SHOTS; PR378 SHOTS40 excluded as cohort authority.',
            private_inspected='Input/code/result/freeze/artifact receipts; PR375 exact saved multiplicity sequence '
                              'and interval arithmetic; full-precision PR375 and PR378 results, no historical fit reruns.',
            context_sha256={p: digest(REPO/p) for p in CONTEXT}, sequence_receipts=sequence,
            limits='No new acquisition, figure/post/PDF reading, broad discovery or native EWP execution.',
            sessions='UNKNOWN', installation_order='UNKNOWN', shared_calibration_and_systematic_error='UNKNOWN',
            exposure=parent.EXPOSURE))
        write_json(out/'HISTORICAL_CONTEXT.json', {label: json.loads((directories[label]/'RESULT.json').read_text())
                                                for label in ('PR375', 'PR378')})
        write_json(out/'INSPECTED.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
            source_sha256=digest(source), parent_receipts=receipts,
            private_input_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()}))
    except (ValueError, OSError, KeyError) as exc:
        write_json(out/'BLOCKED.json', dict(status='BLOCKED_NOT_RUN', blocker=str(exc) if isinstance(exc, ValueError) else type(exc).__name__))
        raise
    print(json.dumps(dict(status='AUTHENTICATED_AFFINE_NOT_RUN', membership_sha256=MEMBERSHIP,
                         fold_sha256={n: digest(out/(n+'_FOLDS.json')) for n in ('primary', 'ALL60')})))


def freeze(source, directories, out):
    if (out/'FREEZE.json').exists() or (out/'BLOCKED.json').exists():
        raise ValueError('freeze/blocker exists; never overwrite')
    inspected = json.loads((out/'INSPECTED.json').read_text())
    previous.check_inputs(source, directories, out, inspected)
    ancestor = json.loads((directories['PR378']/'FREEZE.json').read_text())
    (out/'METHODS.md').write_bytes((REPO/FILES[-1]).read_bytes())
    write_json(out/'ENVIRONMENT.json', dict(python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, openpyxl=openpyxl.__version__))
    record = dict(task=TASK, timestamp_utc=datetime.now(timezone.utc).isoformat(), pw_main=MAIN,
        pw_branch_base_and_scientific_parent=PARENT, bases_git_parent=PARENT_GIT_PARENT,
        pr375_loco_reference=LOCO_REFERENCE, pr374_ancestor='2f93c216f02700e28801418a3069684fff0ba9ea', ewp_read_only_sha=EWP,
        source_sha256=digest(source), membership_sha256=MEMBERSHIP, exposure=parent.EXPOSURE,
        fold_sha256={n: digest(out/(n+'_FOLDS.json')) for n in ('primary', 'ALL60')},
        parent_receipts=inspected['parent_receipts'],
        code_sha256={p: digest(REPO/p) for p in FILES+list(ancestor['code_sha256'])},
        private_input_sha256={p.name: digest(p) for p in out.iterdir() if p.is_file()},
        arms=list(model.ARMS), seed=20261026, draws=2000,
        bounds={'A': {'intercept': 'unbounded signed', 'slope': [0, 100]}, 'M_P_N': [0, 100]},
        prediction_policy='RAW_UNCLIPPED', rank_tolerance='max(n,p)*machine_epsilon*largest_singular_value',
        oracle=dict(method='bvls', solver_tol=1e-14, absolute_prediction_tolerance_pp=1e-10),
        comparison_roles={'A/M': 'primary', 'A/P': 'key incremental value', 'A/N': 'naive reference'},
        decision_authority='METHODS.md', sensitivities=['unfiltered', 'ALL60', 'delete each condition then rerun 11-fold LOCO'],
        scoring_status='NOT_RUN')
    write_json(out/'FREEZE.json', record)
    print(json.dumps(dict(status='FROZEN_AFFINE_NOT_RUN', freeze_sha256=digest(out/'FREEZE.json'), fold_sha256=record['fold_sha256'])))


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


def write_tables(out, result):
    for filename, collection, fields in (
        ('SCORES.csv', 'scores', ['analysis', 'arm', 'rmse', 'rmse_ci95', 'mae', 'bias', 'condition_balanced_rmse']),
        ('CONTRASTS.csv', 'contrasts', ['analysis', 'contrast', 'difference', 'difference_ci95', 'gain', 'gain_ci95', 'grade', 'ci_grades', 'boundary_check'])):
        with (out/filename).open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            for name in ANALYSES:
                for key, value in result[name][collection].items():
                    row = dict(analysis=name, **{fields[1]: key}, **{k: value[k] for k in fields[2:]})
                    writer.writerow({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()})


def report(result):
    p = result['primary']
    lines = [f'# {TASK}', '', f"Primary: **{p['decision']['primary']}**. Selection: **{p['decision']['selection']}**.",
        'Sensitivity interval/selection changes: '+result['sensitivity_summary']+'.', '',
        'Pocket Science Coffee (2024). Primary: 57 physical shots (37 Sworks/20 VST; 29 traditional/28 turbo), '
        '12 LOCO folds. ALL60: 40/20 basket counts, 30/30 styles; original excluded Sworks rows 7,9,23 restored. '
        'Ten flush measurements excluded. Every shot receives one raw prediction per arm.', '',
        'Direct filtered B, including B54, is numeric TDS pp; separate C is unfiltered. D/E grams become kg; '
        'x=dose/final beverage mass. Nominal refractometer-equivalent solute/solution mass; no density conversion. '
        'No derived EY or regional target substitution.', '',
        '| Arm | RMSE [95% CI] pp | MAE | Bias | Balanced RMSE |', '|---|---|---:|---:|---:|']
    def interval(v, ci, scale=1):
        return 'undefined' if v is None else f'{v*scale:.6f} ['+', '.join(f'{z*scale:.6f}' for z in ci)+']' if ci is not None else f'{v*scale:.6f} [unavailable]'
    for a in model.ARMS:
        s = p['scores'][a]
        lines.append(f"|{a}|{interval(s['rmse'], s['rmse_ci95'])}|{s['mae']:.6f}|{s['bias']:.6f}|{s['condition_balanced_rmse']:.6f}|")
    lines += ['', '| Analysis/contrast | Delta pp [95% CI] | Gain % [95% CI] | Point/CI grades |', '|---|---|---|---|']
    for name in ANALYSES:
        for key, c in result[name]['contrasts'].items():
            lines.append(f"|{name}/{key}|{interval(c['difference'], c['difference_ci95'])}|{interval(c['gain'], c['gain_ci95'],100)}|{c['grade']}/{'/'.join(c['ci_grades'])}|")
    lines += ['', 'Negative delta/positive gain favors A. A/M match two parameters, observations and SSE optimization, '
        'but differ in parameter meanings and constraint geometry. A has signed empirical intercept and slope[0,100]; '
        'M/P/N retain[0,100]. Raw predictions are scored without clipping. A/M are not nested.', '',
        '| Lower/upper bands | A/M point:CI | A/P point:CI | A/N point:CI |', '|---|---|---|---|']
    short = {'worse': 'W', 'small': 'S', 'moderate': 'M', 'large': 'L', 'undefined': 'U'}
    for i in range(9):
        c = p['contrasts']['A/M']['boundary_check'][i]
        cells = []
        for key in ('A/M', 'A/P', 'A/N'):
            v = p['contrasts'][key]['boundary_check'][i]
            cells.append(short[v['point']]+':'+''.join(short[z] for z in v['ci_grades']))
        lines.append(f"|{c['lower']}/{c['upper']}|"+'|'.join(cells)+'|')
    lines += ['', 'W/S/M/L=worse/small/moderate/large. Nine combinations for every sensitivity are in JSON/CSV; '
        'these are reporting boundaries, not adequacy or measurement-error checks. Influence delta ranges/reversals/ties '
        '(not CIs): '+ '; '.join(f"{k} {v['difference']}; {v['sign_reversals']}/{v['ties']}" for k,v in result['deletion']['influence_ranges_not_ci'].items())+'.', '',
        'Each campaign: 2,000 paired within-condition draws, seed20261026, every arm/fold refitted. '
        'Requested/completed/failed/unattempted, undefined gains, active/interior fits, domain flags and all numerical '
        'checks are recorded. '+result['numerical_summary']+'.', '',
        parent.EXPOSURE+'. Used means expose underlying shots; procedural folds/new A do not restore blindness. '
        'Original workbook inspected once; all60 observations/order matched full-cohort predecessors and PR378 SOURCE_SHOTS, '
        'not its SHOTS40 subset. PR375 input/code/result/draw receipts and deterministic multiplicities authenticated; '
        'joint M/P/N point/draw results reproduce within1e-10. No separate historical campaign or PR378 replay.', '',
        'Intervals condition on these fixed conditions and within-condition exchangeability; unknown sessions, installation/order, '
        'shared calibration/systematic measurement error and previous selection uncertainty are omitted. Not simultaneous, '
        'blind, causal, practical-adequacy, new-campaign or production evidence. Numerical checks are not independent human review. '
        'Earlier conclusions remain unchanged. P1 blind-TDS=OPEN. Candidate status: '+result['next_candidate']['status']+'. '
        'Reproduction: METHODS.md, FREEZE.json and ARTIFACTS.json.']
    return '\n'.join(lines)+'\n'


def run(source, directories, out):
    if any((out/name).exists() for name in ('ATTEMPT.json', 'RESULT.json', 'INCOMPLETE.json', 'BLOCKED.json')):
        raise ValueError('attempt/result/blocker exists; no repeated campaign')
    frozen = json.loads((out/'FREEZE.json').read_text())
    previous.check_inputs(source, directories, out, frozen)
    for name, expected in frozen['code_sha256'].items():
        if digest(REPO/name) != expected:
            raise ValueError('frozen scientific code/method drift')
    shots = [parent.Shot(**dict(s, condition=tuple(s['condition']))) for s in json.loads((out/'SHOTS.json').read_text())]
    primary, all60 = cohorts(shots)
    if parent.membership_hash(primary) != MEMBERSHIP:
        raise ValueError('primary membership drift')
    for name, rows in (('primary', primary), ('ALL60', all60)):
        if json.loads(json.dumps(fold_record(rows))) != json.loads((out/(name+'_FOLDS.json')).read_text()):
            raise ValueError('frozen fold/order/support drift')
    old = json.loads((directories['PR375']/'RESULT.json').read_text())
    write_json(out/'ATTEMPT.json', dict(timestamp_utc=datetime.now(timezone.utc).isoformat(), freeze_sha256=digest(out/'FREEZE.json')))
    start = time.monotonic()
    result = dict(task=TASK, status='INCOMPLETE', pw_main=MAIN, pw_parent=PARENT, ewp_sha=EWP,
                  exposure=parent.EXPOSURE, freeze_sha256=digest(out/'FREEZE.json'),
                  campaign_status={n: 'NOT_RUN' for n in ANALYSES}, condition_influence_status='NOT_RUN')
    try:
        for name, rows, observation, old_name in (('primary', primary, 'filtered', 'primary'),
                ('unfiltered', primary, 'unfiltered', 'unfiltered'), ('ALL60', all60, 'filtered', 'include_rejected')):
            saved = json.loads((directories['PR375']/(old_name+'_bootstrap.json')).read_text())
            result['campaign_status'][name] = 'INCOMPLETE'
            r = model.evaluate(rows, observation, deadline=start+1800, reference=old[old_name], reference_draws=saved)
            result[name] = r
            write_json(out/(name+'_bootstrap.json'), r.pop('bootstrap_samples'))
            export_csv(out, name, r)
            if r['bootstrap']['failed']:
                raise ValueError('invalid required paired inference: '+r['bootstrap']['failures'][0]['reason'])
            result['campaign_status'][name] = 'COMPLETED'
            write_json(out/'PROGRESS.json', dict(completed_analyses=[n for n in ANALYSES if n in result], elapsed_seconds=time.monotonic()-start))
        result['condition_influence_status'] = 'INCOMPLETE'
        result['deletion'] = model.deletion_influence(primary, result['primary'], deadline=start+1800)
        result['condition_influence_status'] = 'COMPLETED'
        changes = {}
        for name in ('unfiltered', 'ALL60'):
            changes[name] = {k: dict(primary=v, sensitivity=result[name]['decision'][k])
                for k, v in result['primary']['decision'].items() if k != 'contrasts' and result[name]['decision'][k] != v}
            changes[name]['contrasts'] = {k: dict(primary=v, sensitivity=result[name]['decision']['contrasts'][k])
                for k, v in result['primary']['decision']['contrasts'].items() if result[name]['decision']['contrasts'][k] != v}
        result['sensitivity_changes'] = changes
        words = {'FIRST_ARM_LOWER_LOSS': 'favors affine', 'REFERENCE_LOWER_LOSS': 'favors reference', 'UNRESOLVED': 'unresolved'}
        result['sensitivity_summary'] = '; '.join(name+': '+(', '.join(k+' '+words[v['sensitivity']] for k,v in change['contrasts'].items())
            if change['contrasts'] else 'no contrast changes')+('; selection changes' if 'selection' in change else '; selection unchanged')
            for name,change in changes.items())
        justified = result['primary']['decision']['selection'] == 'AFFINE_CONDITIONAL_ADDED_VALUE_OVER_M_P_N'
        result['next_candidate'] = dict(task='SCI-MD-POCKETSCIENCE-AFFINE-CROSS-BASKET-TDS-001',
            status='JUSTIFIED_CANDIDATE_NOT_EXECUTED' if justified else 'NOT_JUSTIFIED',
            policy='Same frozen A/M/P/N; 37 Sworks to20 VST only if present incremental value earned; reassess if genuinely unexposed existing data executable')
        active = sum(r['bootstrap']['fit_counts'][a]['active_fits']+r['point_fit_counts'][a]['active_fits'] for r in (result[n] for n in ANALYSES) for a in model.ARMS)
        active += sum(v['active_fits'] for v in result['deletion']['fit_counts'].values())
        domain = sum(r['bootstrap']['out_of_domain_draws'][a]+int(r['point_domain'][a]['physical_predictions']>0) for r in (result[n] for n in ANALYSES) for a in model.ARMS)
        undefined = sum(c['gain_undefined_draws'] for n in ANALYSES for c in result[n]['contrasts'].values())
        deletion_domain = sum(result['deletion']['out_of_domain_deletions'].values())
        result['numerical_summary'] = f'Zero failed/unattempted draws; undefined gains={undefined}; active fits including deletions={active}; point/draw arm-domain events={domain}; deletion-domain events={deletion_domain}'
        result['scientific_computation_seconds'] = time.monotonic()-start
        if result['scientific_computation_seconds'] > 1800:
            raise ValueError('scientific computation cap exceeded')
        result['status'] = 'COMPLETED_PRIVATE'
        write_json(out/'RESULT.json', result)
        write_tables(out, result)
        (out/'RESULT.md').write_text(report(result))
        p = result['primary']['decision']
        primary_words = {'AFFINE_LOWER_THAN_MATCHED_M': 'Affine has lower held-condition error than M.',
            'M_LOWER_THAN_AFFINE': 'M has lower held-condition error than affine.',
            'AFFINE_MATCHED_COMPARISON_UNRESOLVED': 'The affine comparison with M remains unresolved.'}
        selection_words = 'Affine earns added value over M, P and N.' if justified else 'Affine is not selected; retain the prior P qualification.'
        (out/'SUMMARY.md').write_text(primary_words[p['primary']]+' '+selection_words+' '+result['sensitivity_summary']+'. '
            'The primary comparison uses57 physical shots and12 held-condition folds. Prediction requires measured '
            'final beverage mass; all targets were previously exposed. Unknown sessions, installation order and '
            'shared measurement error limit interpretation. No causal, practical-adequacy or production claim follows. '
            f"Next candidate: {result['next_candidate']['status']}; not executed. Pocket Science Coffee (2024). P1 blind-TDS=OPEN.\n")
    except (ValueError, OSError, KeyError, np.linalg.LinAlgError) as exc:
        result.update(status='INCOMPLETE', blocker=str(exc) if isinstance(exc, ValueError) else type(exc).__name__)
        write_json(out/'INCOMPLETE.json', result)
        raise
    finally:
        write_json(out/'ARTIFACTS.json', {p.name: digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name != 'ARTIFACTS.json'})
    print(json.dumps(dict(status='COMPLETED_PRIVATE', result_sha256=digest(out/'RESULT.json'))))


def main():
    os.umask(0o077)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('inspect', 'freeze', 'run'))
    parser.add_argument('--output', type=Path)
    parser.add_argument('--predecessor', type=Path, help='Narrow explicit PR378 candidate; pinned receipts required')
    args = parser.parse_args()
    try:
        {'inspect': inspect, 'freeze': freeze, 'run': run}[args.command](*locations(args.output, args.predecessor))
    except (ValueError, OSError, KeyError, np.linalg.LinAlgError) as exc:
        print(json.dumps(dict(status='BLOCKED_NOT_RUN_OR_INCOMPLETE', blocker=str(exc) if isinstance(exc, ValueError) else type(exc).__name__)), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

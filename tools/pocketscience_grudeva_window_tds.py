#!/usr/bin/env python3
"""Freeze/run the qualified private window transfer; emit safe status/hashes only."""
import argparse
import csv
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
from tools import pocketscience_affine_tds as previous  # noqa: E402
from puckworks.analysis import pocketscience_cup_tds as source_model  # noqa: E402
from puckworks.analysis import grudeva_clock as clock  # noqa: E402
from puckworks.analysis import pocketscience_grudeva_window_tds as model  # noqa: E402

TASK = 'SCI-MD-POCKETSCIENCE-GRUDEVA-WINDOW-TDS-001'
PARENT = 'cc6e3d66eb5192e08e0949373548bb3a04ee69fd'
MAIN, EWP = previous.MAIN, previous.EWP
PINS = {'FREEZE.json': '223028d54749d8f847ca051b92ace472f7f64b898c2a461302446fe765b4e226',
        'RESULT.json': '62653cb4127cfc89c8b4c0417a83810852f96eab88e240c4a94c26254f916011'}
WORKBOOK_SHA = '9e9063baea1e8f67d905b1e2d03a61a4227e26ed2964ae118426be09bced01cc'
DOSE_RECEIPT_SHA = 'a6482a485aeb32af52c9fe5d3da6842592a7e3da4d468a23c4518c5942d949fc'
FILES = ['puckworks/analysis/pocketscience_grudeva_window_tds.py',
         'tools/pocketscience_grudeva_window_tds.py', 'tests/test_pocketscience_grudeva_window_tds.py',
         'docs/analysis/sci_md_pocketscience_grudeva_window_tds_001/METHODS.md']
ANALYSES = ('primary', 'source_observation', 'target_literal_zero')
digest, write_json = previous.digest, previous.write_json


def locations(output=None, predecessor=None):
    workbook, ancestors, candidate = previous.locations()
    recent = predecessor.resolve() if predecessor else candidate
    for name, expected in PINS.items():
        if digest(recent/name) != expected:
            raise ValueError('PR379 pinned artifact mismatch')
    out = output.resolve() if output else recent.parent/(TASK+'-qualified')
    if (out.is_relative_to(REPO) or out.is_relative_to(workbook.parent.parent)
            or out.is_relative_to(recent) or recent.is_relative_to(out)):
        raise ValueError('private evidence must be separate from originals and predecessor')
    return workbook, ancestors, recent, out


def inputs(workbook, ancestors, recent, out):
    if digest(workbook) != WORKBOOK_SHA:
        raise ValueError('workbook hash drift')
    frozen = json.loads((recent/'FREEZE.json').read_text())
    previous.previous.check_inputs(workbook, ancestors, recent, frozen)
    for name, expected in frozen['code_sha256'].items():
        if digest(REPO/name) != expected:
            raise ValueError('predecessor code drift')
    if json.loads((recent/'RESULT.json').read_text())['freeze_sha256'] != PINS['FREEZE.json']:
        raise ValueError('PR379 result/freeze linkage drift')
    manifest = json.loads((recent/'ARTIFACTS.json').read_text())
    if any(digest(recent/name) != h for name,h in manifest.items()):
        raise ValueError('PR379 saved artifact drift')
    # Reuse the task's authenticated once-only workbook observer output.
    raw = json.loads((out/'SOURCE_SHOTS.json').read_text())
    reference = json.loads((recent/'SHOTS.json').read_text())
    shots = [source_model.Shot(**dict(r, condition=tuple(r['condition']))) for r in raw]
    reference_shots = [source_model.Shot(**dict(r, condition=tuple(r['condition']))) for r in reference]
    primary = model.source_cohort(shots, reference_shots)
    locators = json.loads((out/'LOCATORS.json').read_text())
    pins = {'exp13.csv': clock.SOURCE_SHA, 'PlotData.ipynb': clock.NOTEBOOK_SHA, 'thesis.pdf': model.THESIS_SHA}
    for name, sha in pins.items():
        if digest(Path(locators['grudeva'][name])) != sha:
            raise ValueError('Grudeva original hash drift')
    if digest(out/'NOMINAL_DOSE_AUTHORITY.json') != DOSE_RECEIPT_SHA:
        raise ValueError('authenticated dose passage receipt drift')
    authority = json.loads((out/'NOMINAL_DOSE_AUTHORITY.json').read_text())
    records = json.loads((out/'AUTHENTICATED_GRUDEVA_RECORDS.json').read_text())
    if records != clock.parse_source(Path(locators['grudeva']['exp13.csv'])):
        raise ValueError('Grudeva original observation/order drift')
    return primary, records, authority, frozen


def freeze(workbook, ancestors, recent, out):
    if any((out/p).exists() for p in ('FREEZE.json','ATTEMPT.json','RESULT.json','INCOMPLETE.json')):
        raise ValueError('freeze/attempt already exists')
    shots, records, authority, parent_freeze = inputs(workbook, ancestors, recent, out)
    targets = {name: model.aggregate(records, authority, literal_zero=name == 'target_literal_zero')
               for name in ('primary','target_literal_zero')}
    x, _, _, groups = source_model.arrays(shots)
    write_json(out/'SOURCE_MEMBERSHIP_NEW.json',dict(dataset='pocketscience2024/workbook_assay_reconstruction',
        physical_n=len(shots), conditions=sorted({s.condition for s in shots}),
        original_order=[s.identity for s in shots], global_condition_indices=groups.tolist(),
        primary_membership_sha256=source_model.membership_hash(shots)))
    for name, record in targets.items():
        write_json(out/(name+'_TARGET.json'),record)
    write_json(out/'SUPPORT.json',{name:model.support(x,v['endpoints']) for name,v in targets.items()})
    write_json(out/'INSPECTION.json',dict(original_source_observer_passes_across_task=1,
        source='All60 observations and order match authenticated PR379 full-cohort SHOTS; original workbook inspected in preserved initial qualification',
        grudeva='Pinned original CSV and static notebook inspected; authenticated thesis methods sections 2.1–2.2, printed pages27–30 inspected as text; no figures or notebook execution',
        dose_authority_sha256=DOSE_RECEIPT_SHA, sessions='UNKNOWN', shared_calibration='UNKNOWN',
        systematic_measurement_error='UNKNOWN', historic_replays=0, new_acquisition=False,
        prior_blocked_evidence_preserved=True, exposure_both_datasets='TARGET_EXPOSED / RETROSPECTIVE'))
    (out/'METHODS.md').write_bytes((REPO/FILES[-1]).read_bytes())
    write_json(out/'ENVIRONMENT.json',dict(python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__))
    code = dict(parent_freeze['code_sha256'])
    code.update({p:digest(REPO/p) for p in FILES+['puckworks/analysis/grudeva_clock.py']})
    contract=dict(task=TASK, timestamp_utc=datetime.now(timezone.utc).isoformat(), pw_main=MAIN,
        pw_base_scientific_parent=PARENT, bases_git_parent=previous.PARENT, ewp_read_only_sha=EWP,
        upstream_grudeva=clock.SOURCE_COMMIT, parent_pins=PINS, workbook_sha256=WORKBOOK_SHA,
        source_membership_sha256=digest(out/'SOURCE_MEMBERSHIP_NEW.json'),
        target_membership_sha256={n:digest(out/(n+'_TARGET.json')) for n in targets},
        nominal_dose_receipt_sha256=DOSE_RECEIPT_SHA, support_sha256=digest(out/'SUPPORT.json'),
        code_sha256=code, private_input_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},
        source_n=57, source_conditions=12, target_n=11, literal_zero_target_n=13,
        arms=list(model.ARMS), bounds=[0,100], seed=model.SEED, draws=2000,
        resampling='SeedSequence.spawn(2); source within condition; independent whole target shots; same initialization each analysis',
        primary_comparison='P/N; absolute RMSE delta CI against zero', prediction_policy='RAW_UNCLIPPED',
        oracle={'method':'bvls','solver_tolerance':1e-14,'prediction_tolerance_pp':1e-10},
        sensitivities=['source raw C','literal positive-mass zeros, 13 whole targets','12 source-condition and 11 target-shot deletions'],
        gain_boundaries={'lower':[.075,.10,.125],'upper':[.1875,.25,.3125]},
        scoring_status='NOT_RUN', scientific_computation_cap_seconds=1800)
    write_json(out/'FREEZE.json',contract)
    print(json.dumps({'status':'FROZEN_NOT_RUN','freeze_sha256':digest(out/'FREEZE.json'),
                      'source_membership_sha256':contract['source_membership_sha256'],
                      'target_membership_sha256':contract['target_membership_sha256']}))


def interval(c, key, scale=1):
    v, ci = c[key], c[key+'_ci95']
    if v is None:
        return 'undefined'
    return f'{v*scale:.6f} ['+(', '.join(f'{x*scale:.6f}' for x in ci) if ci else 'undefined')+']'


def report(result):
    p=result['primary']
    lines=[f"# {p['decision']}",'',result['sensitivity_summary'],'',
        'Pocket Science Coffee (2024) supplies57 physical source shots/12 conditions (37Sworks+20VST;29traditional+28turbo). '
        'Grudeva supplies11 complete-chemistry physical 0–32s windows; literal-zero sensitivity uses13. '
        'Whole shots with chemistry gaps are excluded from primary; extra block/terminal vials and source flushes are excluded.', '',
        'Source x=measured dose/final beverage; primary y=filtered rawB, includingB54. Source-observation sensitivity refits rawC '
        'and retains Grudeva’s single recorded channel. Target x=nominal0.0185kg/sum16 recorded net masses; '
        'y=100×pooled solute/beverage. Thesis§2.1 printedpp28–29 explicitly links18.5g to13 experiments; '
        'dose is nominal, not individually measured. Structural zeros contribute zero; no shortened denominator, '
        'density conversion or derived-EY substitution. Basis: refractometer-equivalent solute/solution mass; TDSpp.', '',
        '| Analysis | P RMSE [95% CI] | N RMSE [95% CI] | Delta [95% CI] | Gain% [95% CI] | Grade / CI grades |',
        '|---|---|---|---|---|---|']
    for name in ANALYSES:
        a=result[name];c=a['contrasts']['P/N']
        lines.append('| '+name+' | '+ ' | '.join([interval(a['scores'][k],'rmse') for k in model.ARMS]+
            [interval(c,'difference'),interval(c,'gain',100),c['grade']+'/'+','.join(c['ci_grades'])])+' |')
    lines += ['', '| Primary | MAE | Bias |','|---|---:|---:|']
    for arm in model.ARMS:
        lines.append(f"|{arm}|{p['scores'][arm]['mae']:.6f}|{p['scores'][arm]['bias']:.6f}|")
    lines += ['', '| Lower/upper | Primary | Source C | Literal zero |','|---|---|---|---|']
    for i,b in enumerate(p['contrasts']['P/N']['boundary_check']):
        fields=[f"{b['lower']}/{b['upper']}"]
        for name in ANALYSES:
            z=result[name]['contrasts']['P/N']['boundary_check'][i];fields.append(z['point']+'/'+','.join(z['ci_grades']))
        lines.append('| '+' | '.join(fields)+' |')
    lines += ['', 'All nine boundary combinations reclassify unchanged gains; reporting conventions, not adequacy or sensor-error tests.',
        f"Source x range{p['support']['source_range']}; target{p['support']['target_range']}; "
        f"{p['support']['extrapolation_count']} extrapolated targets retained. Coverage11/11 per arm. "
        f"Primary domain flags{p['out_of_domain_predictions']}; point active bounds{p['source_fit']['active_bounds']}. "
        'Per-shot errors, adverse/worst cases, coefficients and flags are in JSON.', '',
        'Influence point ranges (not CIs):']
    for side,v in result['influence']['ranges_not_ci'].items():
        lines.append(f"{side}: delta{v['difference']}; gain{v['gain']}; reversals{v['sign_reversals']}; ties{v['ties']}.")
    lines += ['', 'Campaign requested/completed/failed/unattempted/undefined gains; active-bound draws(P,N): '+
        '; '.join(f"{n}:{r['bootstrap']['requested']}/{r['bootstrap']['completed']}/{r['bootstrap']['failed']}/"
                  f"{r['bootstrap']['unattempted']}/{r['contrasts']['P/N']['gain_undefined_draws']};"
                  f"{r['bootstrap']['active_bound_draws']['P']},{r['bootstrap']['active_bound_draws']['N']}"
                  for n,r in result.items() if n in ANALYSES)+'.', '',
        'Both arms independently fit one scalar on the same source SSE, bounds[0,100]. '
        'SeedSequence20261027 spawns independent source/target streams; shared P/N multiplicities refit source every draw. '
        'Percentile intervals include source-fit/target-sampling variability under within-source-condition and whole-target-shot '
        'exchangeability. They omit unknown settings/sessions/order, nominal-dose error, calibration/dilution/systematic error, '
        'cross-campaign observer differences and prior selection; not simultaneous intervals.', '',
        'Both datasets are TARGET_EXPOSED/RETROSPECTIVE. Used means and prior clock/MASS analyses preclude blindness. '
        'Original Pocket workbook inspected once; all60/order matched authenticated PR379. Grudeva CSV/notebook authenticated; '
        'notebook read statically, thesis methods text inspected, no figures or model replays. Numerical BVLS checks≤1e-10pp '
        'verify arithmetic, not measurement precision or independent human review.', '',
        'Conditional on measured collected beverage mass and authenticated nominal dose. Whole-cup versus window endpoints '
        'and campaign effects remain confounded. No complete-cup transfer, blind validation, adequacy, causality or production claim. '
        'Prior Pocket Science conclusions unchanged. P1 blind-TDS=OPEN. Next candidate only: '
        'SCI-MD-WADSWORTH-HELD-COFFEE-PERMEABILITY-001; not executed.']
    return '\n'.join(lines)+'\n'


def exports(out,result):
    for filename,key,label in [('SCORES.csv','scores','arm'),('CONTRASTS.csv','contrasts','contrast')]:
        rows=[dict(analysis=n,**{label:a},**v) for n in ANALYSES for a,v in result[n][key].items()]
        with (out/filename).open('w',newline='') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
            w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)
    for name in ANALYSES:
        with (out/(name+'_predictions.csv')).open('w',newline='') as f:
            rows=result[name]['predictions'];w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader()
            w.writerows({k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)


def run(workbook,ancestors,recent,out):
    if any((out/p).exists() for p in ('ATTEMPT.json','RESULT.json','INCOMPLETE.json')):
        raise ValueError('attempt already exists; do not silently rerun')
    frozen=json.loads((out/'FREEZE.json').read_text())
    for root,key in ((REPO,'code_sha256'),(out,'private_input_sha256')):
        for name,sha in frozen[key].items():
            if digest(root/name)!=sha:raise ValueError('frozen code/input/method drift')
    shots,records,authority,_=inputs(workbook,ancestors,recent,out)
    targets={n:json.loads((out/(n+'_TARGET.json')).read_text()) for n in ('primary','target_literal_zero')}
    for n,v in targets.items():
        if v!=model.aggregate(records,authority,literal_zero=n=='target_literal_zero'):
            raise ValueError('target membership/observation drift')
    start=time.monotonic();deadline=start+1800
    write_json(out/'ATTEMPT.json',dict(started_utc=datetime.now(timezone.utc).isoformat(),status='STARTED'))
    result=dict(task=TASK,freeze_sha256=digest(out/'FREEZE.json'),pw_main=MAIN,pw_base=PARENT,
                ewp_read_only_sha=EWP,exposure='Both datasets TARGET_EXPOSED / RETROSPECTIVE',
                nominal_dose_authority_sha256=DOSE_RECEIPT_SHA,membership=frozen['target_membership_sha256'])
    try:
        for name,observation,cohort in [('primary','filtered','primary'),('source_observation','unfiltered','primary'),
                                       ('target_literal_zero','filtered','target_literal_zero')]:
            a=model.evaluate(shots,targets[cohort]['endpoints'],observation,deadline=deadline)
            result[name]=a;write_json(out/(name+'_bootstrap.json'),a.pop('bootstrap_samples'))
            if a['bootstrap']['failed'] or a['bootstrap']['unattempted']:
                raise ValueError('paired inference incomplete; failed campaign retained')
        result['influence']=model.influence(shots,targets['primary']['endpoints'],result['primary'],deadline)
        changes=[n for n in ANALYSES[1:] if result[n]['decision']!=result['primary']['decision']]
        result['sensitivity_summary']=('Decision changes: '+', '.join(changes)+'. ' if changes else
            'Source-observation and target-zero assumptions preserve the primary interval decision. ')+\
            '; '.join(f"{side} deletions: {v['sign_reversals']} point reversals, {v['ties']} ties"
                      for side,v in result['influence']['ranges_not_ci'].items())+'. Influence is not interval inference.'
        result['scientific_computation_seconds']=time.monotonic()-start
        if time.monotonic()>deadline:raise ValueError('scientific computation cap exhausted')
        result['status']='COMPLETED_PRIVATE';write_json(out/'RESULT.json',result)
        text=report(result)
        if len(text.split())>750:raise ValueError('private result word budget exceeded')
        (out/'RESULT.md').write_text(text)
        summary=(result['primary']['decision']+'. '+result['sensitivity_summary']+
            ' The two predictors learned only from57 Pocket Science shots and were tested on11 Grudeva collection windows. '
            'Predictions require measured collected mass and the authenticated nominal18.5g dose. Both datasets were historically exposed. '
            'This compares regular windows, not complete cups, and cannot establish blindness, adequacy or causation. '
            'Unknown sessions, nominal-dose error and shared systematic uncertainty are omitted. Prior Pocket Science conclusions remain unchanged. '
            'P1 blind-TDS remains OPEN.')
        if len(summary.split())>120:raise ValueError('plain summary word budget exceeded')
        (out/'SUMMARY.md').write_text(summary+'\n');exports(out,result)
    except (ValueError,OSError,np.linalg.LinAlgError) as exc:
        result.update(status='INCOMPLETE',blocker=str(exc) if isinstance(exc,ValueError) else type(exc).__name__)
        write_json(out/'INCOMPLETE.json',result);raise
    finally:
        write_json(out/'ARTIFACTS.json',{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='ARTIFACTS.json'})
    print(json.dumps({'status':'COMPLETED_PRIVATE','result_sha256':digest(out/'RESULT.json')}))


def main():
    os.umask(0o077)
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('freeze','run'))
    parser.add_argument('--output',type=Path,help='Existing qualified private input bundle; fresh for a scoring attempt')
    parser.add_argument('--predecessor',type=Path,help='Explicit PR379 bundle locator, authenticated by pinned bytes')
    args=parser.parse_args()
    try:
        {'freeze':freeze,'run':run}[args.command](*locations(args.output,args.predecessor))
    except (ValueError,OSError,KeyError) as exc:
        print(json.dumps({'status':'BLOCKED_NOT_RUN_OR_INCOMPLETE','error_type':type(exc).__name__}),file=sys.stderr)
        return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())

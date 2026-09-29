"""Bounded matched early-assay 5-CQA research; originals and rows stay private."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
import os
import platform
import subprocess
import time

import numpy as np
import scipy

from . import early_assay_5cqa_delivery as md
from . import pannusch_conditional_5cqa_delivery as legacy
from . import pannusch_assay_conditioned_5cqa_delivery as previous
from . import pannusch_conditional_tail_delivery as source_geometry
from . import pannusch_mass_delivery as source

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_5cqa_assay_002'
TASK = 'SCI-MD-5CQA-ASSAY-002'
SPECIES = md.SPECIES
ARMS = md.ARMS
SUFFIX, PANELS = legacy.SUFFIX, legacy.PANELS
read, write, digest = legacy.read, legacy.write, legacy.digest
canonical, identity, private_directory = md.canonical, md.identity, legacy.private_directory
TASK_DEADLINE = datetime.fromisoformat('2026-09-29T22:34:51+00:00').timestamp()
INCOMPLETE, UNRESOLVED = legacy.INCOMPLETE, legacy.UNRESOLVED


def check_task_clock():
    if time.time() >= TASK_DEADLINE:
        raise RuntimeError('SIX_HOUR_TASK_DEADLINE')


def git(expression):
    return subprocess.check_output(['git', 'rev-parse', expression], cwd=ROOT, text=True).strip()


def contract():
    value = read(DOC/'INFORMATION_CONTRACT.json')
    if value['task'] != TASK or value['arms'] != list(ARMS) or value['new_heads'] != list(md.ARMS):
        raise ValueError('WRONG_EARLY_ASSAY_FIVE_CQA_CONTRACT')
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', value['contract_commit'], 'HEAD'], cwd=ROOT)
    for relative, sha in value['files'].items():
        committed = subprocess.check_output(['git', 'show', value['contract_commit']+':'+relative], cwd=ROOT)
        if digest(ROOT/relative) != sha or source.hashlib.sha256(committed).hexdigest() != sha:
            raise ValueError('PROTOCOL_MUST_BE_COMMITTED_AND_IMMUTABLE_BEFORE_FITTING')
    return value


def qualified_sources():
    paths, history = legacy.qualified_sources()
    if history != read(DOC/'SOURCE_IDENTITIES.json'):
        raise ValueError('EXACT_EIGHT_ORIGINAL_TEN_REGISTER_BINDING_REQUIRED')
    for relative, sha in read(DOC/'DEPENDENCIES.json')['files'].items():
        if digest(ROOT/relative) != sha:
            raise ValueError('IMMUTABLE_PREDECESSOR_CHANGED:'+relative)
    return paths, history


source_contract_error = previous.source_contract_error
checked_source_row = previous.checked_source_row
formula_cell, source_books = previous.formula_cell, previous.source_books
pred_queries, suffix_formula_check = previous.pred_queries, previous.suffix_formula_check
EXCLUDED_SHOTS = ('FIT-E03-R1', 'FIT-E11-R3', 'FIT-E14-R3')
EVIDENCE_RELATIVE = '5cqa-assay-002-evidence-20260929T163451Z'


def early_projection(coords, rows, exclusions):
    """Exact source roles; invalid spills remain exclusions, never valid zeros."""
    early, projected = previous.first_projection(coords, rows)
    excluded = {r['shot_id'] for r in exclusions if r['campaign_id'] == 'FIT_2021_12'
                and r['fraction_id'] == '2' and r['analyte_or_measurement'] == 'ALL_HPLC_ANALYTES'
                and r['normalized_status'] == 'INVALID_SPILL'}
    if excluded != set(EXCLUDED_SHOTS):
        source_contract_error('EXCLUSION_REGISTER_CHANGED')
    selected = [r for r in rows if r.get('analyte') == SPECIES and r.get('fraction_id') == '2']
    index = {r['shot_id']: r for r in selected}
    if len(index) != len(selected) or set(index) != set(early):
        source_contract_error('EXACT_SECOND_ASSAY_IDENTITY_MATRIX_REQUIRED')
    second = []
    for shot, values in early.items():
        row = index[shot]
        campaign = 'FIT_2021_12' if shot.startswith('FIT-') else 'PREDICTION_2022_03'
        checked_source_row(dict(row, validity='VALID', exclusion_reason=''), campaign, shot, 2)
        if shot in excluded:
            if row['validity'] != 'INVALID' or row['exclusion_reason'] != 'INVALID_SPILL':
                source_contract_error('SPILL_MUST_NOT_BECOME_VALID_ZERO', shot, 2)
            early[shot] = values+[None]
            continue
        checked_source_row(row, campaign, shot, 2)
        field = 'concentration_value' if campaign == 'FIT_2021_12' else 'measured_concentration'
        q = md.assay_from_mg_g(float(row[field]))
        mass = md.number(float(row['fraction_liquid_g_or_ml']))/1000
        if abs(mass-values[1]) > 5.001e-12:
            source_contract_error('SECOND_VIAL_MASS_EXPORT_MISMATCH', shot, 2)
        early[shot] = values+[q]
        second.append({'campaign': campaign, 'shot': shot, 'fraction': 2,
                       'species': SPECIES, 'source_id': row['source_id'], 'mass_kg': values[1], 'q': q})
    return early, projected, second


def original_early_assays(paths, early, first, second):
    original, audit = previous.original_first_assays(paths, early, first)
    objects, books, counts = {}, {}, Counter()
    for row in second:
        shot = row['shot']; label, exp, rep = shot.split('-')
        if row['fraction'] != 2 or row['species'] != SPECIES or shot in EXCLUDED_SHOTS:
            source_contract_error('VALID_SECOND_ASSAY_ROLE_REQUIRED', shot, 2)
        if label not in objects:
            objects[label] = source.mat(paths['P24-MAT-'+label])['ExperimentalData']
            books[label] = source_books(paths['P24-HPLC-'+label])
        e, j = int(exp[1:]), int(rep[1:])
        run = objects[label][e-1].run[j-1]
        concentration = md.number(float(run.cAlcaloids[1, 2]))
        mass_g = md.number(float(run.mE[1]))
        mass_mg = formula_cell(*books[label], label, e, j, 2)
        q = md.assay_from_mg_g(concentration)
        if (mass_g <= 0 or abs(concentration-1000*row['q']) > 5.001e-9
                or abs(mass_g/1000-row['mass_kg']) > 5.001e-12
                or abs(mass_mg/mass_g-concentration) > 1e-12):
            source_contract_error('ORIGINAL_SECOND_ASSAY_RECONCILIATION', shot, 2)
        original[shot].append(q)
        counts[label] += 1
    for shot in EXCLUDED_SHOTS:
        original[shot].append(None)
    if dict(counts) != {'FIT': 42, 'PRED': 24}:
        source_contract_error('ALL_SIXTY_SIX_VALID_SECOND_ASSAYS_REQUIRED')
    audit.pop('fraction_2_assays_projected')
    audit.update(second_fraction_reconciliations=dict(counts), second_fraction_HPLC_formulas=dict(counts),
                 fraction_2_invalid_spills=3)
    return original, audit


def build_projections(coords, rows, groups, exclusions, *, early=None):
    projected, _, _ = early_projection(coords, rows, exclusions)
    if early is None:
        early = projected
    if set(early) != set(projected) or any(early[s][:2] != projected[s][:2] for s in early):
        source_contract_error('EXACT_EARLY_MASS_JOIN_REQUIRED')
    result = previous.build_projections(coords, rows, groups, early={s: v[:3] for s, v in early.items()})
    training = [dict(r, early_values=early[r['shot']]) for r in result['training'] if r['shot'] not in EXCLUDED_SHOTS]
    for r in result['fit_slots']:
        r['eligible_shot'] = r['shot'] not in EXCLUDED_SHOTS
        if not r['eligible_shot']:
            r.update(supported=False, reason='MATCHED_COHORT_INVALID_Q2_SPILL')
    domain = max(w['end_kg'] for s in training for w in s['windows'])
    if domain > md.HARD_UPPER_KG:
        source_contract_error('TRAINING_DOMAIN_EXCEEDS_HARD_CEILING')
    for q in result['queries']:
        reason = q['source_reason'] or (q['coordinate_status'] if q['coordinate_status'] != 'QUALIFIED' else
                 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN' if q['b1'] > domain else '')
        q.update(supported=not reason, reason=reason)
    originals = sorted({s['group'] for s in training})
    eligible = [r for r in result['fit_slots'] if r['eligible_shot']]
    if (len(training), len(originals), len(eligible), sum(r['supported'] for r in eligible)) != (42, 15, 168, 165):
        source_contract_error('MATCHED_COHORT_OR_SOURCE_SUPPORT_DISCREPANCY')
    folds = []
    for group in originals:
        retained = [s for s in training if s['group'] != group]
        held = [s for s in training if s['group'] == group]
        bound = max(w['end_kg'] for s in retained for w in s['windows'])
        support = [(s['shot'], w['fraction']) for s in held for w in s['windows'] if w['end_kg'] <= bound]
        held_ids = {s['shot'] for s in held}
        folds.append({'group': group, 'domain_kg': bound, 'training_shots': [s['shot'] for s in retained],
                      'held_shots': [s['shot'] for s in held], 'support': support,
                      'slots': [{'shot': s['shot'], 'fraction': s['fraction'],
                                 'supported': (s['shot'], s['fraction']) in support,
                                 'reason': s['reason'] or ('OUTSIDE_FOLD_DOMAIN' if (s['shot'], s['fraction']) not in support else '')}
                                for s in eligible if s['shot'] in held_ids]})
    counts = {'fit_original_physical_shots': 45, 'fit_original_suffix_slots': 180,
              'fit_eligible_physical_shots': len(training), 'fit_original_designs': len(originals),
              'fit_eligible_intended_slots': len(eligible), 'fit_supported_slots': sum(s['supported'] for s in eligible),
              'fit_reasons': dict(Counter(s['reason'] for s in result['fit_slots'] if s['reason'])),
              'common_domain_kg': [0., domain], 'PRED_suffix_values_projected': 0,
              'PRED_first_assay_values_projected': 24, 'PRED_second_assay_values_projected': 24,
              'panels': {p: {'original_shots': 3*len(cs), 'intended_slots': 12*len(cs),
                             'supported_slots': sum(q['supported'] for q in result['queries'] if q['condition'] in cs)}
                         for p, cs in PANELS.items()}}
    result.update(training=training, development_support=folds, source_counts=counts,
                  early_inputs={k: v for k, v in early.items() if k.startswith('PRED-')},
                  excluded_shots=[r for r in exclusions if r['shot_id'] in EXCLUDED_SHOTS])
    return result


def historical_reference():
    """Retained #299 predictions and scores only; never fit, regenerate or rescore."""
    root = Path(os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or read(source.config_path())['sources'][
                'PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path'])
    retained = root/'5cqa-assay-001-evidence-20260929T122232Z/run-001'
    frozen = read(previous.DOC/'FREEZE.json')
    if (digest(retained/'freeze.json') != '401b3a58fe6ca275b1482c1eb4a8146bdad8952bcbabf8bf4a1c7e96f3ed5b68'
            or frozen['producer_commit'] != '35fe284b386f0bec468956c4be9508dcb06ddf43'):
        raise ValueError('HISTORICAL_FREEZE_IDENTITY_DRIFT')
    for name in ('predictions.json', 'models/E0.json', 'models/D0.json', 'models/A1.json', 'models/L1.json'):
        if digest(retained/name) != frozen['artifacts'][name]:
            raise ValueError('RETAINED_HISTORICAL_ARTIFACT_DRIFT:'+name)
    if digest(retained/'scores.json') != digest(previous.DOC/'RESULTS.json'):
        raise ValueError('RETAINED_HISTORICAL_RESULTS_DRIFT')
    return {'publication_head': 'c2bea543f21d9d43ad71dc23a44ea5f8216e8c9b',
            'producer_commit': frozen['producer_commit'], 'producer_tree': frozen['producer_tree'],
            'freeze_sha256': digest(retained/'freeze.json'),
            'predictions_sha256': digest(retained/'predictions.json'),
            'results_sha256': digest(retained/'scores.json'),
            'status': 'EXACT_RETAINED_REFERENCE_ONLY_NO_NEW_HISTORICAL_SCORE',
            'fit_calls': 0, 'prediction_generation_calls': 0, 'score_calls': 0,
            'results': read(retained/'scores.json')}


def task_run(out):
    root = Path(os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT') or read(source.config_path())['sources'][
                'PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path'])
    expected = (root/EVIDENCE_RELATIVE/'run-001').resolve()
    if Path(out).resolve() != expected:
        raise ValueError('ONE_REGISTERED_TASK_RUN_NO_BUDGET_RESET')
    clock = read(expected.parent/'task_clock.json')
    if (clock['task'] != TASK or clock['started_utc'] != '2026-09-29T16:34:51Z'
            or clock['deadline_utc'] != '2026-09-29T22:34:51Z'):
        raise ValueError('PERSISTENT_TASK_CLOCK_IDENTITY_MISMATCH')
    if sum(p.stat().st_size for p in expected.parent.rglob('*') if p.is_file()) >= 5*1024**3:
        raise ValueError('FIVE_GIB_TASK_EVIDENCE_CEILING')
    return expected


def prepare(out):
    check_task_clock()
    out = task_run(out)
    authority = contract()
    paths, history = qualified_sources()
    out = private_directory(out, create=True); out.chmod(0o700)
    coords, rows = source_geometry.coordinates(paths), source_geometry.all_rows()
    exclusions = source.rows(source.DATA/'exclusion_register.csv')
    early, first, second = early_projection(coords, rows, exclusions)
    early, first_audit = original_early_assays(paths, early, first, second)
    fit_rows = [r for r in rows if r['campaign_id'] == 'FIT_2021_12']
    for r in fit_rows:
        if r['analyte'] == SPECIES and int(r['fraction_id']) in SUFFIX:
            checked_source_row(r, r['campaign_id'], r['shot_id'], int(r['fraction_id']))
    qualified_fit = legacy.original_rows(paths, fit_rows, 'FIT_2021_12')
    projections = build_projections(coords,
        qualified_fit+[r for r in rows if r['campaign_id'] == 'PREDICTION_2022_03'],
        source_geometry.condition_groups(), exclusions, early=early)
    counts = projections['source_counts']
    expected = read(DOC/'DATA_AVAILABILITY_PREFLIGHT.json')['counts']
    if counts != expected:
        source_contract_error('QUALIFIED_SOURCE_COHORT_OR_SUPPORT_CHANGED')
    reconciled = legacy.original_reconciliation(paths, projections['fit_slots'], fit_rows)
    if reconciled != 180:
        source_contract_error('ALL_FIT_SUFFIX_ORIGINALS_REQUIRED')
    counts.update(first_audit, FIT_suffix_original_checks=reconciled,
                  FIT_suffix_formulas=suffix_formula_check(paths, 'FIT'))
    projections.update(source=dict(history, rights=source.RIGHTS), information_contract=authority,
                       historical_reference=historical_reference())
    for name, value in projections.items():
        write(out/(name+'.json'), value)
    write(out/'prepared_hashes.json', {str(p.relative_to(out)): digest(p) for p in out.rglob('*.json')})
    write(out/'preparation_runtime.json', source_geometry.imported_files())
    print(canonical(counts))


def develop(out):
    from . import early_assay_5cqa_training as train
    check_task_clock(); out = prepared(task_run(out))
    if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
        raise ValueError('ONE_BLAS_THREAD_REQUIRED')
    dest = out/'development'; dest.mkdir()
    budget = train.Budget(out/'starts', evidence_root=out.parent)
    try:
        records, source_id = read(out/'training.json'), source_identity(out)
        specs = read(out/'development_support.json')
        summary = {'task': TASK, 'scope': 'FIT_ONLY_MODEL_SELECTION_NOT_EXTERNAL_VALIDATION', 'arms': {}}
        model_dir = out/'models'; model_dir.mkdir()
        for arm in ARMS:
            shots = train.project_arm(records, arm)
            candidates = []
            for lam in train.LAMBDAS:
                candidate = {'lambda': lam, 'status': 'SELECTABLE', 'folds': []}
                for spec in specs:
                    group = spec['group']
                    training, held = train.split_design(shots, group)
                    support = set(map(tuple, spec['support']))
                    expected = {(s.shot, w.fraction) for s in held for w in s.windows if w.end_kg <= spec['domain_kg']}
                    if ([s.shot for s in training] != spec['training_shots']
                            or [s.shot for s in held] != spec['held_shots'] or support != expected
                            or max(w.end_kg for s in training for w in s.windows) != spec['domain_kg']):
                        raise ValueError('WHOLE_ORIGINAL_DESIGN_FOLD_OR_SUPPORT_DRIFT')
                    name = f'{arm}.{lam}.{group}'
                    model, audit = train.fit(training, lam, budget, name, source_id, source.RIGHTS)
                    write(dest/(name+'.audit.json'), audit)
                    fold = {'group': group, 'fit_status': audit['status'],
                            'domain_kg': spec['domain_kg'], 'training_shots': spec['training_shots'],
                            'held_shots': spec['held_shots'], 'support': spec['support']}
                    try:
                        if model is None:
                            raise ValueError('FIT_NOT_QUALIFIED:'+audit['status'])
                        model.save(dest/(name+'.model.json'))
                        fold.update(train.held_metrics(model, held, support), model_sha256=model.sha256)
                    except ValueError as exc:
                        candidate['status'] = 'NONSELECTABLE'; fold['failure'] = str(exc)
                    candidate['folds'].append(fold)
                    write(dest/(name+'.fold.json'), fold)
                    print(name, fold['fit_status'], flush=True)
                for target, key in [('balanced_R_mg_g', 'R_mg_g'), ('R_allowance_mg_g', 'R_allowance_mg_g')]:
                    candidate[target] = float(np.mean([f[key] for f in candidate['folds']])) if candidate['status'] == 'SELECTABLE' else None
                candidates.append(candidate)
                write(dest/f'{arm}.{lam}.candidate.json', candidate)
            lam = train.select_lambda(candidates)
            summary['arms'][arm] = {'candidates': candidates, 'selected_lambda': lam}
            write(dest/(arm+'.selection.json'), summary['arms'][arm])
            model, audit = train.fit(shots, lam, budget, arm+'.final', source_id, source.RIGHTS, scope='FINAL_FIT')
            write(model_dir/(arm+'.audit.json'), audit)
            if model is None:
                raise ValueError('NUMERICAL_OR_DECISION_UNRESOLVED:FINAL_FIT:'+arm)
            model.save(model_dir/(arm+'.json'))
            support = {(s.shot, w.fraction) for s in shots for w in s.windows}
            write(model_dir/(arm+'.qualification.json'), train.held_metrics(model, shots, support))
        write(dest/'development.json', summary)
        write(out/'fitting_completion.json', {'status': 'COMPLETE',
              'fitting_stage_wall_seconds': time.time()-budget.clock['started_unix']})
    finally:
        budget.worker_lock.close()


def decide(adequacy, comparisons, complete, *, support_complete=True, numerical_qualified=True):
    adequate = [a for a in ARMS if adequacy[a] == 'PASS']
    single = [a for a in ('L1M', 'L2M') if a in adequate]
    earned = adequacy['L12'] == 'PASS' and all(comparisons[k]['status'] == 'PASS'
                                             for k in ('L12_vs_L1M', 'L12_vs_L2M'))
    blocker = None
    if all(adequacy[a] == 'FAIL' for a in ARMS):
        label = 'TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE'
    elif not numerical_qualified:
        label, blocker = 'NUMERICAL_OR_DECISION_UNRESOLVED', 'PRIMARY_NUMERICAL_QUALIFICATION_INCOMPLETE'
    elif not support_complete:
        label, blocker = 'SOURCE_SUPPORT_INCOMPLETE', 'PRIMARY_SOURCE_SUPPORT_INCOMPLETE'
    elif (not complete or any(adequacy[a] not in ('PASS', 'FAIL') for a in ARMS)
          or any(c['status'] not in ('PASS', 'FAIL') for c in comparisons.values())):
        label, blocker = 'NUMERICAL_OR_DECISION_UNRESOLVED', 'REQUIRED_DECISION_THRESHOLD_OVERLAP'
    elif earned:
        label = 'TWO_ASSAY_MAPPING_EARNED'
    elif single:
        label = 'SINGLE_ASSAY_ADEQUATE_NO_EARNED_TWO_ASSAY_COMPLEXITY'
    elif adequate:
        label = 'ADEQUATE_INCREMENT_NOT_ESTABLISHED'
    else:
        label, blocker = 'NUMERICAL_OR_DECISION_UNRESOLVED', 'ADEQUACY_UNRESOLVED'
    return {'disposition': label, 'blocker': blocker, 'adequate_arms': adequate,
            'adequate_single_assay_contracts': single, 'two_assay_route_earned': earned,
            'single_assay_placement_earned': comparisons['L2M_vs_L1M']['status'] == 'PASS',
            'minimum_tested_assay_count': 1 if single else 2 if adequate else None,
            'primary_complete_qualified_support': complete}


def prepared(out):
    out = private_directory(out)
    contract(); qualified_sources()
    if any((out/n).exists() for n in ('freeze.json', 'score_receipt.json')):
        raise ValueError('FROZEN_RUN_IMMUTABLE')
    for relative, sha in read(out/'prepared_hashes.json').items():
        if digest(out/relative) != sha:
            raise ValueError('PREPARED_PROJECTION_DRIFT')
    for relative, sha in read(out/'preparation_runtime.json').items():
        if digest(ROOT/relative) != sha:
            raise ValueError('PREPARATION_RUNTIME_DRIFT')
    return out


def source_identity(out):
    value = read(out/'source.json')
    return identity({'source_files': {k: v for k, v in value['source_files'].items() if k.endswith('-FIT')},
                     'fit_register': value['registers']['fit_fraction_replicates.csv']})


def load_models(out):
    return {a: md.Model.load(out/'models'/(a+'.json')) for a in ARMS}


def predict_records(models, early, queries):
    if set(models) != set(ARMS):
        raise ValueError('COMPLETE_THREE_ARM_MATRIX_REQUIRED')
    predictions, states = {}, {}
    for query in queries:
        md.exact_keys(query, legacy.QUERY_KEYS)
        if query['analyte'] != SPECIES or query['campaign'] != 'PREDICTION_2022_03':
            raise ValueError('COORDINATE_ONLY_PRED_FIVE_CQA_QUERY_REQUIRED')
    for arm in md.ARMS:
        results = []
        for q in queries:
            result = dict(q, prediction_status=q['reason'] or 'NOT_PREDICTED', numerical_qualified=False,
                          five_cqa_kg=None, five_cqa_mg=None, five_cqa_mg_g=None,
                          allowance_kg=None, feature_extrapolation=[])
            if q['supported']:
                try:
                    values = early[q['shot']]
                    schema = {'L1M': md.L1MInput, 'L2M': md.L2MInput, 'L12': md.L12Input}[arm]
                    inputs = schema(**{n: values[md.FEATURES.index(n)] for n in md.feature_names(arm)},
                                    input_class='SOURCE_EARLY_INPUT')
                    state = models[arm].condition(inputs)
                    start, coord_allowance = source_geometry.source_query_start(q, state)
                    p = state.predict_intervals([start], [q['b1']])[0]
                    allowance = p.allowance_kg+coord_allowance
                    result.update(asdict(p), integration_start_kg=start, coordinate_allowance_kg=coord_allowance,
                                  allowance_kg=allowance, numerical_qualified=p.numerical_qualified and allowance <= 1e-9,
                                  prediction_status='QUALIFIED' if p.numerical_qualified and allowance <= 1e-9 else 'NUMERICALLY_UNQUALIFIED')
                    states[arm+':'+q['shot']] = state.to_dict()
                except (ValueError, FloatingPointError) as exc:
                    result['prediction_status'] = 'PREDICTION_FAILED:'+str(exc)
            results.append(result)
        predictions[arm] = results
    return predictions, states


def execution_account(out):
    starts = list((out/'starts').glob('*.start.json'))
    logs = [read(p) for p in (out/'starts').glob('*.end.json')]
    return {'task': TASK, 'iterative_starts': len(starts), 'completed_starts': len(logs),
            'starts_by_arm': {a: len(list((out/'starts').glob(a+'.*.start.json'))) for a in ARMS},
            'historical_reference_fits': 0,
            'parent_fits': 0, 'E0_D0_fits': 0,
            'fitting_stage_wall_seconds': read(out/'fitting_completion.json')['fitting_stage_wall_seconds'],
            'actual_residual_calls': sum(r['actual_residual_calls'] for r in logs),
            'numerical_jacobian_residual_calls': sum(r['numerical_jacobian_residual_calls'] for r in logs),
            'max_calls_per_start': max((r['actual_residual_calls'] for r in logs), default=0),
            'optimizer_wall_seconds': sum(r['elapsed_seconds'] for r in logs),
            'failed_starts': sum(r['status'] != 'CONVERGED' for r in logs),
            'boundary_starts': sum(bool(r['boundary_indices']) for r in logs),
            'peak_rss_kib': max((r['peak_rss_kib'] for r in logs), default=0),
            'workers': 1, 'blas_threads': 1, 'native_ewp_runs': 0, 'scientific_score_passes': 0,
            'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
            'imported_first_party_modules': source_geometry.imported_files()}


def freeze(out):
    check_task_clock(); out = prepared(task_run(out))
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('COMMITTED_CLEAN_PRODUCER_REQUIRED')
    execution = execution_account(out)
    if (execution['iterative_starts'] != 549 or execution['completed_starts'] != 549
            or execution['starts_by_arm'] != {a: 183 for a in ARMS}
            or execution['max_calls_per_start'] > 8000 or execution['fitting_stage_wall_seconds'] >= 3600):
        raise ValueError('EXECUTION_ACCOUNTING_NOT_QUALIFIED')
    predictions, states = predict_records(load_models(out), read(out/'early_inputs.json'), read(out/'queries.json'))
    write(out/'predictions.json', predictions); write(out/'states.json', states)
    for ps in predictions.values():
        primary = [p for p in ps if p['condition'] in PANELS['primary']]
        if len(ps) != 96 or len(primary) != 48 or not all(p['supported'] and p['numerical_qualified'] for p in primary):
            raise ValueError('ALL_ORIGINAL_QUALIFIED_PRIMARY_WINDOWS_REQUIRED')
        if any(not p['numerical_qualified'] for p in ps if p['supported']):
            raise ValueError('NUMERICALLY_UNQUALIFIED_SUPPORTED_PREDICTION')
    execution.update(max_allowance_kg=max(p['allowance_kg'] for ps in predictions.values() for p in ps if p['allowance_kg'] is not None),
                     prediction_slots=288, historical_reference='EXACT_RETAINED_RECORDS_NO_REFIT_OR_RESCORE')
    write(out/'execution.json', execution)
    files = set(execution['imported_first_party_modules']) | set(read(out/'preparation_runtime.json'))
    files |= set(read(DOC/'DEPENDENCIES.json')['files'])
    files |= {str(p.relative_to(ROOT)) for p in DOC.rglob('*') if p.is_file()}
    files |= {str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('test_*early_assay*5cqa*.py')}
    files |= {'puckworks/analysis/early_assay_5cqa_training.py'}
    write(out/'freeze.json', {'task': TASK, 'producer_commit': git('HEAD'), 'producer_tree': git('HEAD^{tree}'),
        'code_and_protocol': {p: digest(ROOT/p) for p in sorted(files)},
        'artifacts': {str(p.relative_to(out)): digest(p) for p in sorted(out.rglob('*.json'))},
        'arms': list(ARMS), 'panels': PANELS, 'outcomes_attached': False,
        'review_status': 'READY_FOR_INDEPENDENT_REVIEW', 'scoring_policy': 'ONE_INDEPENDENTLY_APPROVED_SCORE_NO_RETUNING'})
    print('READY_FOR_INDEPENDENT_REVIEW', digest(out/'freeze.json'))


def verify_frozen(out):
    frozen = read(out / 'freeze.json')
    if frozen['task'] != TASK or frozen['arms'] != list(ARMS) or frozen['outcomes_attached'] is not False:
        raise ValueError('WRONG_FROZEN_EXPERIMENT')
    for relative, sha in frozen['code_and_protocol'].items():
        if digest(ROOT / relative) != sha:
            raise ValueError('FROZEN_CODE_OR_PROTOCOL_DRIFT:' + relative)
        committed = subprocess.check_output(['git', 'show', frozen['producer_commit']+':'+relative], cwd=ROOT)
        if source.hashlib.sha256(committed).hexdigest() != sha:
            raise ValueError('FROZEN_PRODUCER_COMMIT_BINDING_MISMATCH')
    if git(frozen['producer_commit']+'^{tree}') != frozen['producer_tree']:
        raise ValueError('FROZEN_PRODUCER_TREE_MISMATCH')
    for relative, sha in frozen['artifacts'].items():
        if digest(out / relative) != sha:
            raise ValueError('FROZEN_ARTIFACT_DRIFT:' + relative)
    source.verify_registers(read(out / 'source.json'))
    return frozen


def verify(out):
    out = private_directory(out)
    frozen = verify_frozen(out)
    models = load_models(out)
    predictions, states = predict_records(models, read(out / 'early_inputs.json'), read(out / 'queries.json'))
    if canonical(predictions) != canonical(read(out / 'predictions.json')) or canonical(states) != canonical(read(out / 'states.json')):
        raise ValueError('SAVED_MODEL_INFERENCE_NOT_DETERMINISTIC')
    result = {'task': TASK, 'status': 'PASS', 'reviewed_producer': frozen['producer_commit'],
              'prediction_slots': sum(map(len, predictions.values())), 'prediction_max_difference': 0.,
              'optimizer_calls': 0, 'outcome_joins': 0, 'score_calls': 0, 'writes': 0}
    print(canonical(result))
    return result


def score_guard(out):
    if any((out / n).exists() for n in ('score_receipt.json', 'scores.json', 'score_completion.json',
                                      'observed_suffix.json', 'shot_results.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')


def verify_before_score(out, review):
    from . import pannusch_conditioned_mass_delivery as receipt
    score_guard(out)
    frozen = receipt.verify_before_score(out, review)
    approved = read(review)
    if (frozen['task'] != TASK or approved.get('task') != TASK or not approved.get('reviewer')
            or approved.get('unresolved_blocking_findings') != []
            or approved.get('future_chemistry_attached') is not False
            or approved.get('approval_scope') != 'ONE_PREDECLARED_FROZEN_PRED_SCORE_ONLY_NO_RETUNING'):
        raise ValueError('GENUINE_INDEPENDENT_EXACT_FREEZE_REVIEW_REQUIRED')
    verify_frozen(out)
    qualified_sources()
    return frozen


def score(out, review):
    check_task_clock()
    out = private_directory(out)
    score_guard(out)
    task_run(out)
    verify_before_score(out, review)
    write(out / 'score_receipt.json', {'task': TASK, 'status': 'STARTED',
          'freeze_sha256': digest(out / 'freeze.json'), 'review_sha256': digest(Path(review)),
          'predictions_sha256': digest(out / 'predictions.json')})
    # Sole outcome join, after the independent approval and exclusive receipt.
    observed = read(out / 'queries.json')
    rows = source_geometry.all_rows()
    paths, _ = qualified_sources()
    index = legacy.analyte_index(legacy.original_rows(paths, rows, 'PREDICTION_2022_03'), 'PREDICTION_2022_03')
    for r in observed:
        original = index[r['shot'], r['fraction']]
        if not r['analyte_eligible'] or original['validity'] != 'VALID':
            raise ValueError('SOURCE_VALID_PRED_TARGET_REQUIRED')
        r['q'] = legacy.source_value(original, 'PREDICTION_2022_03')
    if legacy.original_reconciliation(paths, observed, rows) != 96:
        raise ValueError('ALL_PRED_FIVE_CQA_ORIGINALS_REQUIRED')
    suffix_formula_check(paths, 'PRED')
    result, private = evaluate(observed, read(out / 'predictions.json'))
    result['historical_reference'] = read(out/'historical_reference.json')
    write(out / 'observed_suffix.json', observed)
    write(out / 'shot_results.json', private)
    write(out / 'scores.json', result)
    write(out / 'score_completion.json', {'task': TASK, 'status': 'COMPLETE', 'scientific_score_passes': 1,
          'files': {n: digest(out / n) for n in ('scores.json', 'shot_results.json', 'observed_suffix.json', 'score_receipt.json')},
          'freeze_sha256': digest(out / 'freeze.json'), 'review_sha256': digest(Path(review))})
    print(result['disposition'])


def report(out):
    out = private_directory(out)
    verify_frozen(out)
    completion = read(out / 'score_completion.json')
    if completion['task'] != TASK or completion['status'] != 'COMPLETE' or completion['scientific_score_passes'] != 1:
        raise ValueError('RETAINED_COMPLETED_SCORE_REQUIRED')
    if completion['freeze_sha256'] != digest(out / 'freeze.json'):
        raise ValueError('RETAINED_SCORE_FREEZE_MISMATCH')
    if set(completion['files']) != {'scores.json', 'shot_results.json', 'observed_suffix.json', 'score_receipt.json'}:
        raise ValueError('COMPLETE_RETAINED_SCORE_BINDING_REQUIRED')
    receipt = read(out / 'score_receipt.json')
    if (receipt['task'] != TASK or receipt['freeze_sha256'] != completion['freeze_sha256']
            or receipt['review_sha256'] != completion['review_sha256']
            or receipt['predictions_sha256'] != digest(out / 'predictions.json')):
        raise ValueError('RETAINED_SCORE_RECEIPT_BINDING_MISMATCH')
    for relative, sha in completion['files'].items():
        if digest(out / relative) != sha:
            raise ValueError('RETAINED_SCORE_ARTIFACT_DRIFT')
    result = read(out / 'scores.json')
    print(canonical(result))
    return result


def evaluate(observed, predictions):
    expected = {(r['shot'], r['fraction']) for r in observed}
    if len(observed) != 96 or len(expected) != 96 or set(predictions) != set(ARMS):
        raise ValueError('ALL_ORIGINAL_PRED_SLOTS_AND_THREE_ARMS_REQUIRED')
    supports = []
    for ps in predictions.values():
        if len(ps) != 96 or {(p['shot'], p['fraction']) for p in ps} != expected:
            raise ValueError('MISSING_PREDICTIONS_CANNOT_DROP_DENOMINATORS')
        supports.append({(p['shot'], p['fraction']): (p['supported'], p['reason']) for p in ps})
    if any(s != supports[0] for s in supports[1:]):
        raise ValueError('IDENTICAL_COMPARISON_SUPPORT_REQUIRED')
    panels, private = {}, {}
    for panel, conditions in PANELS.items():
        panels[panel], private[panel] = {}, {}
        for arm in ARMS:
            panels[panel][arm], private[panel][arm] = legacy.panel_metrics(observed, predictions[arm], conditions)
    primary = panels['primary']
    adequacy = {a: primary[a]['adequacy'] for a in ARMS}
    comparisons = {}
    for a, b in [('L2M', 'L1M'), ('L12', 'L1M'), ('L12', 'L2M')]:
        gain = legacy.material_gain(primary[a], primary[b])
        gain['gain_status'] = gain['status']
        gain['candidate_adequacy'] = adequacy[a]
        gain['status'] = legacy.conjunction([gain['status'], adequacy[a]])
        comparisons[a+'_vs_'+b] = gain
    primary_records = [p for ps in predictions.values() for p in ps if p['condition'] in PANELS['primary']]
    decision = decide(adequacy, comparisons, all(v['complete_scope'] for v in primary.values()),
                      support_complete=all(p['supported'] for p in primary_records),
                      numerical_qualified=all(p['numerical_qualified'] for p in primary_records if p['supported']))
    failures = {a: dict(Counter(p['prediction_status'] for p in ps if not p['numerical_qualified']))
                for a, ps in predictions.items()}
    extrapolation = {a: {panel: {'shots': len({p['shot'] for p in ps if p['condition'] in cs and p['feature_extrapolation']}),
                                 'features': sorted({f for p in ps if p['condition'] in cs for f in p['feature_extrapolation']})}
                          for panel, cs in PANELS.items()} for a, ps in predictions.items()}
    return {'task': TASK, **decision, 'adequacy_by_arm': adequacy, 'pairwise_complexity': comparisons,
            'panels': panels, 'prediction_failures_and_unsupported': failures, 'feature_extrapolation': extrapolation,
            'claims': list(md.CLAIMS), 'rights': source.RIGHTS, 'physical_validation': 'NOT_ESTABLISHED',
            'analytical_uncertainty': 'NOT_ESTABLISHED', 'scientific_score_passes': 1, 'outcome_joins': 1,
            'native_ewp_runs': 0, 'merge_authorized': False, 'production_adoption_authorized': False,
            'successor_authorized': False}, private


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    sub = parser.add_subparsers(dest='stage', required=True)
    for name in ('prepare', 'develop', 'freeze', 'score', 'verify', 'report'):
        stage = sub.add_parser(name, allow_abbrev=False)
        stage.add_argument('--out', type=Path, required=True)
        if name == 'score': stage.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    if args.stage in ('prepare', 'develop', 'freeze', 'score'):
        import resource
        soft, hard = resource.getrlimit(resource.RLIMIT_AS)
        cap = 12*1024**3
        resource.setrlimit(resource.RLIMIT_AS, (min(cap, soft) if soft > 0 else cap, hard))
    if args.stage == 'score': score(args.out, args.review)
    else: globals()[args.stage](args.out)


if __name__ == '__main__':
    main()

"""Bounded early-TDS-conditioned 5-CQA research; originals and rows stay private."""
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

from . import conditional_5cqa_tds_delivery as md
from . import pannusch_conditional_5cqa_delivery as legacy
from . import pannusch_conditional_caffeine_delivery as inherited
from . import pannusch_conditional_tail_delivery as source_geometry
from . import pannusch_mass_delivery as source

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_5cqa_tds_001'
TASK = 'SCI-MD-5CQA-TDS-001'
SPECIES = md.SPECIES
ARMS = ('E0', 'D0', 'S0', 'S1', 'S2')
SUFFIX, PANELS = legacy.SUFFIX, legacy.PANELS
read, write, digest = legacy.read, legacy.write, legacy.digest
canonical, identity, private_directory = md.canonical, md.identity, legacy.private_directory
TASK_DEADLINE = datetime.fromisoformat('2026-09-29T07:09:49+00:00').timestamp()
INCOMPLETE, UNRESOLVED = legacy.INCOMPLETE, legacy.UNRESOLVED


def check_task_clock():
    if time.time() >= TASK_DEADLINE:
        raise RuntimeError('SIX_HOUR_TASK_DEADLINE')


def git(expression):
    return subprocess.check_output(['git', 'rev-parse', expression], cwd=ROOT, text=True).strip()


def contract():
    value = read(DOC/'INFORMATION_CONTRACT.json')
    if value['task'] != TASK or value['arms'] != list(ARMS) or value['new_heads'] != list(md.ARMS):
        raise ValueError('WRONG_FIVE_CQA_TDS_CONTRACT')
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


def retained_parents(directory):
    try:
        parents, final, records = inherited.retained_parents(directory)
    except (OSError, ValueError, KeyError) as exc:
        raise ValueError('BLOCKED_DEPENDENCY: RETAINED_006_PARENT_ARCHIVE') from exc
    expected = read(DOC/'PARENT_FOLDS.json')['folds']
    if len(records) != 15 or [{k: r[k] for k in e} for r, e in zip(records, expected)] != expected:
        raise ValueError('BLOCKED_DEPENDENCY: EXACT_COMPLETE_PARENT_MATRIX')
    # Rehydrate the unchanged semantic model into this runtime's verified namespace.
    return ({k: md.parent.Model.from_dict(v.to_dict()) for k, v in parents.items()},
            md.parent.Model.from_dict(final.to_dict()), records)


def original_early(paths, early, projected):
    count = source_geometry.verify_original_assays(paths, projected)
    objects = {k: source.mat(paths['P24-MAT-'+k])['ExperimentalData'] for k in ('FIT', 'PRED')}
    result = {}
    for shot, values in early.items():
        label, exp, rep = shot.split('-')
        run = objects[label][int(exp[1:])-1].run[int(rep[1:])-1]
        original = [md.number(float(run.TdS[k]))/100 for k in (0, 1)]
        if any(abs(a-b) > 5.001e-11 for a, b in zip(original, values[2:])):
            raise ValueError('ORIGINAL_EARLY_TDS_ROUNDING_MISMATCH')
        result[shot] = values[:2]+original
    return result, count


def build_projections(coords, rows, groups, parents, final, *, early=None):
    result = legacy.build_projections(coords, rows, groups)
    projected_early, _ = inherited.early_projection(coords, rows)
    if early is None:
        early = projected_early
    if set(early) != set(projected_early) or any(early[s][:2] != projected_early[s][:2] for s in early):
        raise ValueError('EXACT_EARLY_SHOT_MASS_JOIN_REQUIRED')
    for s in result['training']:
        s['early_values'] = list(early[s['shot']])
    result['early_inputs'] = {k: list(v) for k, v in early.items() if k.startswith('PRED-')}
    bound = min(final.domain_kg, result['source_counts']['common_domain_kg'][1])
    if bound > .06971540000000001:
        raise ValueError('NO_FINAL_DOMAIN_EXTENSION')
    result['source_counts']['common_domain_kg'] = [0., bound]
    for q in result['queries']:
        if q['supported'] and q['b1'] > bound:
            q.update(supported=False, reason='OUTSIDE_COMMON_TRAINING_MASS_DOMAIN')
    for spec in result['development_support']:
        if spec['group'] not in parents:
            raise ValueError('COMPLETE_PARENT_MATRIX_REQUIRED')
        parent = parents[spec['group']]
        spec['domain_kg'] = min(spec['domain_kg'], parent.domain_kg)
        spec['parent_sha256'] = parent.sha256
        held = [s for s in result['training'] if s['group'] == spec['group']]
        spec['support'] = [(s['shot'], w['fraction']) for s in held for w in s['windows'] if w['end_kg'] <= spec['domain_kg']]
        keys = set(spec['support'])
        for slot in spec['slots']:
            if slot['supported'] and (slot['shot'], slot['fraction']) not in keys:
                slot.update(supported=False, reason='OUTSIDE_FOLD_DOMAIN')
    for panel, conditions in PANELS.items():
        result['source_counts']['panels'][panel]['supported_slots'] = sum(q['supported'] for q in result['queries'] if q['condition'] in conditions)
    from .conditional_5cqa_tds_training import validate_parent_matrix
    validate_parent_matrix(result['training'], result['development_support'], parents)
    return result


def prepare(out, parent_evidence):
    check_task_clock()
    authority = contract()
    paths, history = qualified_sources()
    parents, final, records = retained_parents(parent_evidence)
    out = private_directory(out, create=True); out.chmod(0o700)
    coords, rows = source_geometry.coordinates(paths), source_geometry.all_rows()
    early, projected = inherited.early_projection(coords, rows)
    early, count = original_early(paths, early, projected)
    projections = build_projections(coords, legacy.original_rows(paths, rows, 'FIT_2021_12'),
                                    source_geometry.condition_groups(), parents, final, early=early)
    counts = projections['source_counts']
    expected = read(DOC/'DATA_AVAILABILITY_PREFLIGHT.json')['counts']
    if counts != expected:
        raise ValueError('QUALIFIED_SOURCE_COHORT_OR_SUPPORT_CHANGED')
    counts['early_original_TDS_checks'] = count
    counts['original_5CQA_checks'] = legacy.original_reconciliation(paths, projections['fit_slots']+projections['queries'], rows)
    counts['HPLC_formula_check'] = legacy.hplc_formula_check(paths)
    if count != 138 or counts['original_5CQA_checks'] != 276:
        raise ValueError('COMPLETE_ORIGINAL_RECONCILIATION_REQUIRED')
    projections.update(source=dict(history, rights=source.RIGHTS), information_contract=authority,
                       parent_verification=records)
    for name, value in projections.items():
        write(out/(name+'.json'), value)
    (out/'parents').mkdir()
    for group, parent in parents.items():
        parent.save(out/'parents'/(group+'.json'))
    write(out/'prepared_hashes.json', {str(p.relative_to(out)): digest(p) for p in out.rglob('*.json')})
    write(out/'preparation_runtime.json', source_geometry.imported_files())
    print(canonical(counts))


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


def develop(out):
    from . import conditional_5cqa_tds_training as train
    check_task_clock(); out = prepared(out)
    if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
        raise ValueError('ONE_BLAS_THREAD_REQUIRED')
    dest = out/'development'; dest.mkdir()
    budget = train.Budget(out/'starts', evidence_root=out.parent)
    try:
        parents = {p.stem: md.parent.Model.load(p) for p in (out/'parents').glob('*.json')}
        records, source_id = read(out/'training.json'), source_identity(out)
        summary = train.develop(records, read(out/'development_support.json'), parents, dest,
                                budget, source_id, source.RIGHTS)
        model_dir = out/'models'; model_dir.mkdir()
        final = md.parent.Model.load(ROOT/'docs/analysis/sci_md_mass_delivery_006/models/C2.json')
        for arm in md.ARMS:
            shots = train.project_arm(records, arm)
            lam = summary['arms'][arm]['selected_lambda']
            name = arm+'.FINAL'
            model, audit = (train.fit_scalar(shots, final, budget, name, source_id, source.RIGHTS, scope='FINAL_FIT')
                if arm == 'S0' else train.fit(shots, lam, final, budget, name, source_id, source.RIGHTS, scope='FINAL_FIT'))
            write(model_dir/(arm+'.audit.json'), audit)
            if model is None:
                raise ValueError('NOT_ADJUDICATED_FINAL_FIT_FAILURE:'+arm)
            model.save(model_dir/(arm+'.json'))
            support = {(s.shot, w.fraction) for s in shots for w in s.windows}
            write(model_dir/(arm+'.qualification.json'), train.held_metrics(model, shots, support))
        for arm in legacy.ARMS:
            src = ROOT/'docs/analysis/sci_md_5cqa_delivery_001/models'/f'{arm}.json'
            with (model_dir/(arm+'.json')).open('xb') as stream:
                stream.write(src.read_bytes())
        write(out/'fitting_completion.json', {'status': 'COMPLETE',
              'fitting_stage_wall_seconds': time.time()-budget.clock['started_unix']})
    finally:
        budget.worker_lock.close()


def load_models(out):
    return {a: (legacy.md.Model if a in legacy.ARMS else md.Model).load(out/'models'/(a+'.json')) for a in ARMS}


def predict_records(models, early, queries):
    if set(models) != set(ARMS):
        raise ValueError('COMPLETE_FIVE_ARM_MATRIX_REQUIRED')
    predictions, states = legacy.predict_records({a: models[a] for a in legacy.ARMS},
                                                  {k: v[:2] for k, v in early.items()}, queries)
    for arm in md.ARMS:
        results = []
        for q in queries:
            # The legacy operator above already checked exact query keys/species.
            result = dict(q, prediction_status=q['reason'] or 'NOT_PREDICTED', numerical_qualified=False,
                          five_cqa_kg=None, five_cqa_mg=None, five_cqa_mg_g=None,
                          allowance_kg=None, feature_extrapolation=[])
            if q['supported']:
                try:
                    state = models[arm].condition(md.EarlyInput(arm, early[q['shot']], 'SOURCE_EARLY_INPUT'))
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
    scalar = list((out/'scalar_fits').glob('*.start.json'))
    return {'task': TASK, 'iterative_starts': len(starts), 'completed_starts': len(logs),
            'starts_by_arm': {a: len(list((out/'starts').glob(a+'.*.start.json'))) for a in ('S1', 'S2')},
            'scalar_fits': len(scalar), 'completed_scalar_fits': len(list((out/'scalar_fits').glob('*.end.json'))),
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
    check_task_clock(); out = prepared(out)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('COMMITTED_CLEAN_PRODUCER_REQUIRED')
    execution = execution_account(out)
    if (execution['iterative_starts'] != 366 or execution['completed_starts'] != 366
            or execution['starts_by_arm'] != {'S1': 183, 'S2': 183}
            or execution['scalar_fits'] != 16 or execution['completed_scalar_fits'] != 16
            or execution['max_calls_per_start'] > 8000 or execution['fitting_stage_wall_seconds'] >= 3600):
        raise ValueError('EXECUTION_ACCOUNTING_NOT_QUALIFIED')
    predictions, states = predict_records(load_models(out), read(out/'early_inputs.json'), read(out/'queries.json'))
    write(out/'predictions.json', predictions); write(out/'states.json', states)
    write(out/'legacy_predictions.json', {a: predictions[a] for a in legacy.ARMS})
    expected = read(ROOT/'docs/analysis/sci_md_5cqa_delivery_001/FREEZE.json')['artifacts']['predictions.json']
    if digest(out/'legacy_predictions.json') != expected:
        raise ValueError('FROZEN_E0_D0_REPLAY_MISMATCH')
    for ps in predictions.values():
        primary = [p for p in ps if p['condition'] in PANELS['primary']]
        if len(ps) != 96 or len(primary) != 48 or not all(p['supported'] and p['numerical_qualified'] for p in primary):
            raise ValueError('ALL_ORIGINAL_QUALIFIED_PRIMARY_WINDOWS_REQUIRED')
        if any(not p['numerical_qualified'] for p in ps if p['supported']):
            raise ValueError('NUMERICALLY_UNQUALIFIED_SUPPORTED_PREDICTION')
    execution.update(max_allowance_kg=max(p['allowance_kg'] for ps in predictions.values() for p in ps if p['allowance_kg'] is not None),
                     prediction_slots=480, legacy_prediction_sha256=expected, legacy_replay='EXACT_RETAINED_BYTES')
    write(out/'execution.json', execution)
    files = set(execution['imported_first_party_modules']) | set(read(out/'preparation_runtime.json'))
    files |= set(read(DOC/'DEPENDENCIES.json')['files'])
    files |= {str(p.relative_to(ROOT)) for p in DOC.rglob('*') if p.is_file()}
    files |= {str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('test_*5cqa_tds*.py')}
    files |= {'puckworks/analysis/conditional_5cqa_tds_training.py'}
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
    result, private = evaluate(observed, read(out / 'predictions.json'))
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



def decide(adequacy, comparisons, complete):
    adequate = [a for a in md.ARMS if adequacy[a] == 'PASS']
    least = adequate[0] if adequate else None
    earned = []
    if comparisons['S1_vs_S0']['status'] == 'PASS':
        earned.append('S1')
    if all(comparisons[k]['status'] == 'PASS' for k in ('S2_vs_S1', 'S2_vs_S0')):
        earned.append('S2')
    replacement = earned[-1] if earned else None
    if not complete:
        label = 'NOT_ADJUDICATED_PRIMARY_SUPPORT_OR_NUMERICAL_FAILURE'
    elif any(adequacy[a] not in ('PASS', 'FAIL') for a in md.ARMS):
        label = 'NOT_ADJUDICATED_PRIMARY_THRESHOLD_OVERLAP'
    elif adequate and any(c['status'] not in ('PASS', 'FAIL') for c in comparisons.values()):
        label = 'NOT_ADJUDICATED_COMPLEXITY_THRESHOLD_OVERLAP'
    elif replacement == 'S2':
        label = 'TDS_CONDITIONED_SHARE_INCREMENT_EARNED'
    elif replacement == 'S1':
        label = 'MASS_CONDITIONED_SHARE_INCREMENT_EARNED'
    elif least == 'S0':
        label = 'CONSTANT_SHARE_FIVE_CQA_ADEQUATE'
    elif least:
        label = 'ADEQUATE_INCREMENT_NOT_ESTABLISHED'
    else:
        label = 'TESTED_TDS_CONDITIONED_FIVE_CQA_FAMILIES_INADEQUATE'
    return {'disposition': label, 'least_complex_adequate_new_arm': least,
            'adequate_new_arms': adequate, 'earned_replacement_arm': replacement,
            'more_complex_adequate_arm_earned_replacement': replacement is not None,
            'adequacy_disposition_by_new_arm': {a: ('ADEQUATE_INCREMENT_NOT_ESTABLISHED'
                if a in adequate and a not in earned and a != 'S0' else
                'CONSTANT_SHARE_FIVE_CQA_ADEQUATE' if a == 'S0' and a in adequate else adequacy[a]) for a in md.ARMS}}


def evaluate(observed, predictions):
    expected = {(r['shot'], r['fraction']) for r in observed}
    if len(observed) != 96 or len(expected) != 96 or set(predictions) != set(ARMS):
        raise ValueError('ALL_ORIGINAL_PRED_SLOTS_AND_FIVE_ARMS_REQUIRED')
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
    for a, b in [('S1', 'S0'), ('S2', 'S1'), ('S2', 'S0')]:
        gain = legacy.material_gain(primary[a], primary[b])
        gain['gain_status'] = gain['status']
        gain['candidate_adequacy'] = adequacy[a]
        gain['status'] = legacy.conjunction([gain['status'], adequacy[a]])
        comparisons[a+'_vs_'+b] = gain
    decision = decide(adequacy, comparisons, all(v['complete_scope'] for v in primary.values()))
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
        if name == 'prepare': stage.add_argument('--parent-evidence', type=Path, required=True)
        if name == 'score': stage.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    if args.stage == 'prepare': prepare(args.out, args.parent_evidence)
    elif args.stage == 'score': score(args.out, args.review)
    else: globals()[args.stage](args.out)


if __name__ == '__main__':
    main()

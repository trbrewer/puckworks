"""Bounded source projection, retained-parent verification and caffeine freeze.

Only the separate scorer projects PRED caffeine outcomes. Raw rows stay private.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
from pathlib import Path
import os
import platform
import subprocess
import time

import numpy as np
import scipy

from . import conditional_caffeine_delivery as md
from . import conditional_caffeine_training as train
from . import pannusch_conditional_tail_delivery as old
from . import conditional_tail_training as old_train
from . import pannusch_mass_delivery as source

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_caffeine_delivery_001'
TASK = 'SCI-MD-CAFFEINE-DELIVERY-001'
SUFFIX = (3, 5, 7, 10)
PANELS = old.PANELS
read, write, digest = old.read, train.write_new, source.digest
private_directory = old.private_directory
PARENT_FREEZE = '54d5afb2a5dc938f9d9efce88bc6a511f8984837ebd583eae9eea9c4db96a7b3'


def git(expression):
    return subprocess.check_output(['git', 'rev-parse', expression], cwd=ROOT, text=True).strip()


def contract():
    c = read(DOC/'INFORMATION_CONTRACT.json')
    if c['task'] != TASK or c['arms'] != list(md.ARMS) or c['primary'] != 'S2':
        raise ValueError('WRONG_CONTRACT')
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', c['contract_commit'], 'HEAD'], cwd=ROOT)
    for path, sha in c['files'].items():
        committed = subprocess.check_output(['git', 'show', c['contract_commit']+':'+path], cwd=ROOT)
        if digest(ROOT/path) != sha or source.hashlib.sha256(committed).hexdigest() != sha:
            raise ValueError('CONTRACT_NOT_IMMUTABLE_AND_COMMITTED_BEFORE_FIT')
    return c


def qualified_sources():
    history = read(DOC/'SOURCE_IDENTITIES.json')
    source.verify_registers(history)
    paths = source.source_paths()
    if {k: digest(v) for k, v in paths.items()} != history['source_files']:
        raise ValueError('QUALIFIED_SOURCE_HASH_MISMATCH')
    dep = read(DOC/'DEPENDENCIES.json')['parent']
    for path, sha in dep['producer_files'].items():
        if digest(ROOT/path) != sha:
            raise ValueError('IMMUTABLE_006_DEPENDENCY_CHANGED')
    retained = read(ROOT/'docs/analysis/sci_md_mass_delivery_006/RESULT_BINDING.json')
    for path, sha in retained['frozen_code_and_protocol'].items():
        if path.endswith('.py') and digest(ROOT/path) != sha:
            raise ValueError('QUALIFIED_006_SOURCE_OR_TRAINING_CODE_CHANGED')
    return paths, history


def retained_parents(directory):
    """Verify retained fold models without any parent optimizer invocation."""
    directory = Path(directory)
    if digest(directory/'freeze.json') != PARENT_FREEZE:
        raise ValueError('CROSS_FIT_PARENT_NOT_AVAILABLE: FREEZE_HASH')
    f = read(directory/'freeze.json')
    for path in ('training.json', 'development_support.json'):
        if digest(directory/path) != f['artifacts'][path]:
            raise ValueError('CROSS_FIT_PARENT_NOT_AVAILABLE: TRAINING_PROVENANCE')
    shots = old_train.project_arm(read(directory/'training.json'), 'C2')
    parents, records = {}, []
    for group, training, held, domain, support in old_train.folds(shots):
        relative = f'development/C2.0.0001.{group}.model.json'
        path = directory/relative
        if not path.is_file() or digest(path) != f['artifacts'].get(relative):
            raise ValueError('CROSS_FIT_PARENT_NOT_AVAILABLE:'+group)
        p = md.parent.Model.load(path)
        info = md.strict_json(p.training_identity_json)
        # FitProblem construction derives only transforms/geometry, never fits.
        expected = old_train.FitProblem(training, .0001)
        if (p.arm != 'C2' or p.regularization != .0001 or p.domain_kg != domain
                or info['shots'] != [s.shot for s in training]
                or info['groups'] != sorted({s.group for s in training})
                or any(s.shot in info['shots'] for s in held)
                or info['training_projection_sha256'] != md.identity([asdict(s) for s in training])
                or not np.allclose(p.means, expected.means, rtol=0, atol=16*np.finfo(float).eps)
                or tuple(p.minima) != tuple(expected.minima) or tuple(p.maxima) != tuple(expected.maxima)):
            raise ValueError('CROSS_FIT_PARENT_NOT_AVAILABLE: ID_TRANSFORM_DOMAIN:'+group)
        parents[group] = p
        records.append({'held_group': group, 'content_sha256': p.sha256, 'file_sha256': digest(path),
                        'domain_kg': domain, 'training_groups': info['groups'], 'training_shots': info['shots'],
                        'training_projection_sha256': info['training_projection_sha256'],
                        'source_identity': info['source_identity'], 'serialized_transforms_reused_exactly': True})
    final_path = ROOT/'docs/analysis/sci_md_mass_delivery_006/models/C2.json'
    final = md.parent.Model.load(final_path)
    if len(parents) != 15 or final.sha256 != md.FINAL_PARENT_SHA256:
        raise ValueError('CROSS_FIT_PARENT_NOT_AVAILABLE: COMPLETE_PARENT_MATRIX')
    return parents, final, records


def early_projection(coords, rows):
    fit_coords = [r for r in coords if r['shot'].startswith('FIT') and r['fraction'] in (1, 2)]
    pred_coords = [r for r in coords if r['shot'].startswith('PRED') and r['fraction'] in (1, 2)]
    selected = [r for r in rows if r['analyte'] == 'TDS' and int(r['fraction_id']) in (1, 2)]
    fit = old.fit_source.assay_projection([r for r in selected if r['campaign_id'] == 'FIT_2021_12'], fit_coords, (1, 2))
    pred = old.pred_source.selected_assays([r for r in selected if r['campaign_id'] == 'PREDICTION_2022_03'], pred_coords, (1, 2))
    result = {}
    for shot in sorted({r['shot'] for r in coords}):
        rs = sorted([r for r in fit+pred if r['shot'] == shot], key=lambda r: r['fraction'])
        if len(rs) != 2 or any(not r['eligible'] or r['coordinate_status'] != 'QUALIFIED' for r in rs):
            raise ValueError('MISSING_EARLY_MASS_OR_TDS:'+shot)
        first, second = rs
        if first['b0'] != 0 or abs(first['b1']-second['b0']) > 1e-15:
            raise ValueError('EARLY_ORIGIN_OR_CONTIGUITY_MISMATCH')
        result[shot] = [first['mass_kg'], second['mass_kg'], first['q'], second['q']]
    return result, fit+pred


def target_slots(coords, rows, *, campaign, include_values=False):
    """Early caffeine never crosses this projection; PRED metadata has no values."""
    index = {(r['shot_id'], int(r['fraction_id'])): r for r in rows
             if r['campaign_id'] == campaign and r['analyte'] == 'caffeine' and int(r['fraction_id']) in SUFFIX}
    result = []
    for c in coords:
        if c['campaign'] != campaign or c['fraction'] not in SUFFIX:
            continue
        r = index.get((c['shot'], c['fraction']))
        field = 'concentration_value' if campaign == 'FIT_2021_12' else 'measured_concentration'
        reason = 'MISSING_CAFFEINE_SOURCE_ROW' if r is None else (
            r.get('exclusion_reason') or 'INVALID_CAFFEINE' if r['validity'] != 'VALID' else
            'MISSING_CAFFEINE_VALUE' if not r.get(field) else '')
        if r is not None and r['concentration_unit'] != 'mg/g':
            raise ValueError('CAFFEINE_SOURCE_UNITS_MISMATCH')
        item = {k: c[k] for k in ('campaign', 'condition', 'shot', 'fraction', 'b0', 'b1', 'mass_kg', 'coordinate_status')}
        item.update(analyte='caffeine', source_id=r['source_id'] if r else None,
                    source_field=(f"ExperimentalData({int(c['shot'].split('-')[1][1:])}).run({int(c['shot'].split('-')[2][1:])}).cAlcaloids({(1,2,3,5,7,10).index(c['fraction'])+1},1)" if r else None),
                    validity_reason=reason or 'VALID_SOURCE_CAFFEINE', analyte_eligible=not reason,
                    source_reason=reason)
        if include_values:
            item['q'] = md.number(float(r[field]))/1000 if not reason else None
            if item['q'] is not None and item['q'] < 0:
                raise ValueError('NEGATIVE_CAFFEINE_NOT_A_REPAIRABLE_OBSERVATION')
        result.append(item)
    return result


def original_caffeine_check(paths, slots):
    objects = {}
    count = 0
    for r in slots:
        if r.get('q') is None:
            continue
        label, exp, rep = r['shot'].split('-')
        if label not in objects:
            objects[label] = source.mat(paths['P24-MAT-'+label])['ExperimentalData']
        original = float(objects[label][int(exp[1:])-1].run[int(rep[1:])-1].cAlcaloids[(1,2,3,5,7,10).index(r['fraction']), 0])
        if abs(original/1000-r['q']) > 5.001e-12:
            raise ValueError('ORIGINAL_CAFFEINE_EXPORT_MISMATCH')
        count += 1
    return count


def chemical_ordering(slots, rows):
    """Reporting only; never a fitting feature, threshold or eligibility rule."""
    tds = {(r['shot_id'], int(r['fraction_id'])): r for r in rows
           if r['analyte'] == 'TDS' and int(r['fraction_id']) in SUFFIX}
    records = []
    for r in slots:
        t = tds.get((r['shot'], r['fraction']))
        if r.get('q') is None or t is None or t['validity'] != 'VALID':
            continue
        field = 'concentration_value' if r['campaign'] == 'FIT_2021_12' else 'measured_concentration'
        if t['concentration_unit'] != 'percent':
            raise ValueError('TDS_SOURCE_UNITS_MISMATCH')
        q_tds = md.number(float(t[field]))/100
        records.append({'shot': r['shot'], 'fraction': r['fraction'], 'caffeine_exceeds_TDS': r['q'] > q_tds})
    return {'compared_slots': len(records), 'inconsistent_slots': sum(r['caffeine_exceeds_TDS'] for r in records),
            'exclusions_or_clipping_applied': False}, records


def prepare(out, parent_evidence):
    authority = contract()
    paths, history = qualified_sources()
    parents, final, parent_records = retained_parents(parent_evidence)
    out = private_directory(out, create=True)
    coords, rows = old.coordinates(paths), old.all_rows()
    early, projected = early_projection(coords, rows)
    original_early_count = old.verify_original_assays(paths, projected)
    fit_slots = target_slots(coords, rows, campaign='FIT_2021_12', include_values=True)
    pred_slots = target_slots(coords, rows, campaign='PREDICTION_2022_03')
    original_caffeine_count = original_caffeine_check(paths, fit_slots)
    groups = old.condition_groups()
    training = []
    for shot in sorted(s for s in early if s.startswith('FIT')):
        slots = [s for s in fit_slots if s['shot'] == shot]
        ws = []
        for s in slots:
            reason = s['source_reason'] or (s['coordinate_status'] if s['coordinate_status'] != 'QUALIFIED' else '')
            s.update(supported=not reason, reason=reason)
            if not reason:
                anchor = sum(early[shot][:2])
                start, delta = old.source_query_start(s, type('Anchor', (), {'b_anchor': anchor})())
                s.update(integration_start_kg=start, coordinate_allowance_kg=delta)
                ws.append(asdict(train.Window(s['fraction'], start, s['b1'], s['q'])))
        training.append({'shot': shot, 'group': groups[slots[0]['condition']], 'early_values': early[shot], 'windows': ws})
    domain = min(final.domain_kg, max(w['end_kg'] for s in training for w in s['windows']))
    for s in pred_slots:
        reason = s['source_reason'] or (s['coordinate_status'] if s['coordinate_status'] != 'QUALIFIED' else
            'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN' if s['b1'] > domain else '')
        s.update(supported=not reason, reason=reason)
    folds = []
    for g, parent_model in parents.items():
        t = [s for s in training if s['group'] != g]
        held = [s for s in training if s['group'] == g]
        b = min(parent_model.domain_kg, max(w['end_kg'] for s in t for w in s['windows']))
        support = [(s['shot'], w['fraction']) for s in held for w in s['windows'] if w['end_kg'] <= b]
        folds.append({'group': g, 'parent_sha256': parent_model.sha256, 'domain_kg': b,
                      'training_shots': [s['shot'] for s in t], 'held_shots': [s['shot'] for s in held],
                      'intended_slots': 4*len(held), 'support': support,
                      'slots': [{'shot': s['shot'], 'fraction': s['fraction'],
                                 'supported': (s['shot'], s['fraction']) in support,
                                 'reason': s['reason'] or ('OUTSIDE_FOLD_DOMAIN' if (s['shot'],s['fraction']) not in support else '')}
                                for s in fit_slots if s['condition'] == g]})
    if len(training) != 45 or len(folds) != 15 or len(fit_slots) != 180 or len(pred_slots) != 96:
        raise ValueError('ORIGINAL_DENOMINATOR_MISMATCH')
    order, order_rows = chemical_ordering(fit_slots, rows)
    counts = {'fit_shots': 45, 'fit_designs': 15, 'fit_intended_slots': 180,
              'fit_eligible_slots': sum(s['supported'] for s in fit_slots),
              'fit_reasons': dict(Counter(s['reason'] for s in fit_slots if s['reason'])),
              'pred_intended_slots': 96, 'pred_supported_slots': sum(s['supported'] for s in pred_slots),
              'pred_reasons': dict(Counter(s['reason'] for s in pred_slots if s['reason'])),
              'panels': {p: {'shots': 3*len(cs), 'intended': 12*len(cs),
                            'supported': sum(s['supported'] for s in pred_slots if s['condition'] in cs)} for p, cs in PANELS.items()},
              'early_TDS_original_checks': original_early_count, 'FIT_later_caffeine_original_checks': original_caffeine_count,
              'caffeine_eligibility_independently_derived': True, 'FIT_observed_chemical_ordering': order}
    for name, value in {'training': training, 'fit_slots': fit_slots, 'early_inputs': {k:v for k,v in early.items() if k.startswith('PRED')},
                        'queries': pred_slots, 'coordinates': coords, 'development_support': folds,
                        'parent_verification': parent_records, 'source': dict(history, task=TASK, rights=source.RIGHTS),
                        'source_counts': counts, 'information_contract': authority, 'fit_ordering': order_rows}.items():
        write(out/(name+'.json'), value)
    (out/'parents').mkdir()
    for g, model in parents.items():
        model.save(out/'parents'/(g+'.json'))
    write(out/'prepared_hashes.json', {str(p.relative_to(out)): digest(p) for p in out.rglob('*.json')})
    write(out/'preparation_runtime.json', old.imported_files())
    print(md.canonical(counts))


def prepared(out):
    out = private_directory(out)
    contract(); qualified_sources()
    if any((out/n).exists() for n in ('freeze.json', 'score_receipt.json')):
        raise ValueError('FROZEN_RUN_IMMUTABLE')
    for path, sha in read(out/'prepared_hashes.json').items():
        if digest(out/path) != sha:
            raise ValueError('PREPARED_PROJECTION_DRIFT')
    return out


def source_identity(out):
    s = read(out/'source.json')
    return md.identity({'source_files': {k:v for k,v in s['source_files'].items() if k.endswith('-FIT')},
                        'fit_register': s['registers']['fit_fraction_replicates.csv']})


def budget(out):
    if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
        raise ValueError('ONE_BLAS_THREAD_REQUIRED')
    return train.Budget(out/'starts')


def develop(out):
    out = prepared(out)
    dest = out/'development'; dest.mkdir()
    parents = {p.stem: md.parent.Model.load(p) for p in (out/'parents').glob('*.json')}
    return train.develop(read(out/'training.json'), read(out/'development_support.json'), parents,
                         dest, budget(out), source_identity(out), source.RIGHTS)


def final_fit(out):
    out = prepared(out)
    dest = out/'models'; dest.mkdir()
    b = budget(out)
    final = md.parent.Model.load(ROOT/'docs/analysis/sci_md_mass_delivery_006/models/C2.json')
    selection = read(out/'development/development.json')
    for arm in md.ARMS:
        shots = train.project_arm(read(out/'training.json'), arm)
        if arm == 'S0':
            model, audit = train.fit_scalar(shots, final, b, 'final.S0', source_identity(out), source.RIGHTS, scope='FINAL_FIT')
        else:
            lam = selection['arms'][arm]['selected_lambda']
            if lam is None:
                write(dest/(arm+'.failure.json'), {'status': 'NO_SELECTABLE_LAMBDA'}); continue
            model, audit = train.fit(shots, lam, final, b, 'final.'+arm, source_identity(out), source.RIGHTS, scope='FINAL_FIT')
        write(dest/(arm+'.audit.json'), audit)
        if model is not None:
            model.save(dest/(arm+'.json'))


def predict_records(models, early, queries):
    predictions, states = {}, {}
    for arm in md.ARMS:
        ps = []
        model = models.get(arm)
        for q in queries:
            result = dict(q, prediction_status=q['reason'] or 'NOT_PREDICTED', numerical_qualified=False,
                          caffeine_kg=None, caffeine_mg=None, caffeine_mg_g=None, allowance_kg=None,
                          feature_extrapolation=[])
            if q['supported'] and model is not None:
                try:
                    inp = md.EarlyInput(arm, early[q['shot']][:len(md.feature_names(arm))], 'SOURCE_EARLY_INPUT')
                    state = model.condition(inp)
                    start, coord_allowance = old.source_query_start(q, state)
                    p = md.predict_intervals(state, [start], [q['b1']])[0]
                    allowance = p.allowance_kg+coord_allowance
                    result.update(asdict(p), allowance_kg=allowance, integration_start_kg=start,
                                  coordinate_allowance_kg=coord_allowance,
                                  numerical_qualified=p.numerical_qualified and allowance <= 1e-9,
                                  prediction_status='QUALIFIED' if p.numerical_qualified and allowance <= 1e-9 else 'NUMERICALLY_UNQUALIFIED')
                    states[arm+':'+q['shot']] = state.to_dict()
                except (ValueError, FloatingPointError) as exc:
                    result['prediction_status'] = 'PREDICTION_FAILED:'+str(exc)
            elif q['supported']:
                result['prediction_status'] = 'MODEL_NOT_AVAILABLE'
            ps.append(result)
        predictions[arm] = ps
    return predictions, states


def d0_ordering(model, parent_model, early, queries):
    records = []
    knots = np.linspace(0, parent_model.domain_kg, 5)
    for q in queries:
        if not q['supported']:
            continue
        state = model.condition(md.EarlyInput('D0', early[q['shot']][:2], 'SOURCE_EARLY_INPUT'))
        ps = parent_model.condition(md.parent.EarlyInput('C2', early[q['shot']], 'SOURCE_EARLY_INPUT'))
        start, _ = old.source_query_start(q, state)
        cuts = [start]+[x for x in knots if start < x < q['b1']]+[q['b1']]
        # Both logits are linear between the same knots; endpoint signs exactly
        # determine existence of pointwise D0 > T on each requested segment.
        delta = np.interp(cuts, knots, state.logits)-np.interp(cuts, knots, ps.logits)
        direct = md.predict_intervals(state, [start], [q['b1']])[0]
        tds = md.parent.predict_intervals(ps, [start], [q['b1']])[0]
        records.append({'shot': q['shot'], 'fraction': q['fraction'],
            'pointwise_violation': bool(np.max(delta) > 0),
            'interval_mass_violation': direct.caffeine_kg > tds.solute_kg})
    return {'compared_slots': len(records), 'pointwise_violation_slots': sum(r['pointwise_violation'] for r in records),
            'interval_mass_violation_slots': sum(r['interval_mass_violation'] for r in records),
            'clipping_applied': False}, records


def predict(out):
    out = prepared(out)
    models = {arm: md.Model.load(out/'models'/(arm+'.json')) for arm in md.ARMS if (out/'models'/(arm+'.json')).exists()}
    start = time.monotonic()
    predictions, states = predict_records(models, read(out/'early_inputs.json'), read(out/'queries.json'))
    write(out/'predictions.json', predictions); write(out/'states.json', states)
    final_parent = md.parent.Model.load(ROOT/'docs/analysis/sci_md_mass_delivery_006/models/C2.json')
    if 'D0' in models:
        order_summary, order_rows = d0_ordering(models['D0'], final_parent, read(out/'early_inputs.json'), read(out/'queries.json'))
    else:
        order_summary, order_rows = {'status': 'D0_NOT_AVAILABLE'}, []
    write(out/'D0_ordering_summary.json', order_summary)
    write(out/'D0_ordering_rows.json', order_rows)
    logs = [read(p) for p in (out/'starts').glob('*.end.json')]
    execution = {'task': TASK, 'iterative_starts': len(list((out/'starts').glob('*.start.json'))),
        'completed_starts': len(logs), 'closed_form_fits': len(list((out/'scalar_fits').glob('*.start.json'))),
        'actual_residual_calls': sum(r['actual_residual_calls'] for r in logs),
        'numerical_jacobian_residual_calls': sum(r['numerical_jacobian_residual_calls'] for r in logs),
        'max_calls_per_start': max((r['actual_residual_calls'] for r in logs), default=0),
        'optimizer_wall_seconds': sum(r['elapsed_seconds'] for r in logs),
        'failed_starts': sum(r['status'] != 'CONVERGED' for r in logs),
        'boundary_starts': sum(bool(r['boundary_indices']) for r in logs),
        'peak_rss_kib': max((r['peak_rss_kib'] for r in logs), default=0),
        'prediction_wall_seconds': time.monotonic()-start, 'workers': 1, 'blas_threads': 1,
        'max_allowance_kg': max((r['allowance_kg'] for ps in predictions.values() for r in ps if r['allowance_kg'] is not None), default=None),
        'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
        'native_ewp_runs': 0, 'scientific_score_passes': 0, 'imported_first_party_modules': old.imported_files()}
    write(out/'execution.json', execution)
    print(md.canonical({k:v for k,v in execution.items() if k != 'imported_first_party_modules'}))


def freeze(out):
    out = prepared(out)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('COMMIT_IMPLEMENTATION_AND_PUBLIC_MODELS_BEFORE_FREEZE')
    files = set(read(out/'execution.json')['imported_first_party_modules']) | set(read(out/'preparation_runtime.json'))
    files |= {str(p.relative_to(ROOT)) for p in DOC.rglob('*') if p.is_file()}
    files |= {'puckworks/analysis/conditional_caffeine_scoring.py'}
    files |= {str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('test_*caffeine*.py')}
    write(out/'freeze.json', {'task': TASK, 'producer_commit': git('HEAD'), 'producer_tree': git('HEAD^{tree}'),
        'code_and_protocol': {p:digest(ROOT/p) for p in sorted(files)},
        'artifacts': {str(p.relative_to(out)):digest(p) for p in out.rglob('*.json')},
        'arms': list(md.ARMS), 'primary_candidate': 'S2', 'panels': PANELS,
        'scoring_policy': 'ONE_INDEPENDENTLY_APPROVED_SCORE_NO_RETUNING'})
    print('READY_FOR_INDEPENDENT_REVIEW', digest(out/'freeze.json'))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command', choices=('prepare', 'develop', 'fit', 'predict', 'freeze', 'score', 'report'))
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--parent-evidence', type=Path)
    ap.add_argument('--review', type=Path)
    a = ap.parse_args()
    if a.command == 'prepare':
        if a.parent_evidence is None: ap.error('--parent-evidence required')
        prepare(a.out, a.parent_evidence)
    elif a.command in ('score', 'report'):
        from . import conditional_caffeine_scoring as scoring
        if a.command == 'score':
            if a.review is None: ap.error('--review required')
            scoring.score(a.out, a.review)
        else:
            print(md.canonical(scoring.report(a.out)))
    else:
        {'develop': develop, 'fit': final_fit, 'predict': predict, 'freeze': freeze}[a.command](a.out)


if __name__ == '__main__':
    main()

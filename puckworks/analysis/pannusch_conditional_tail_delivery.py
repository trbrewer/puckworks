"""Source preparation, FIT development and exact prediction freeze for task 006.

Only the separately invoked scorer attaches PRED suffix outcomes. Private row
artifacts are exclusive writes outside Git; old scorers are never called.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

import numpy as np
import scipy

from . import conditional_tail_delivery as md
from . import conditional_tail_training as train
from . import pannusch_mass_delivery as source
from . import pannusch_empirical_transfer as fit_source
from . import pannusch_anchored_mass_delivery as pred_source
from . import anchored_mass_delivery as legacy

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_mass_delivery_006'
TASK = 'SCI-MD-MASS-DELIVERY-006'
SUFFIX = (3, 5, 7, 10)
PANELS = {'primary': source.PRIMARY, 'temperature_stress': source.TEMP, 'flow_stress': source.FLOW}
LEGACY = 'FIRST_ASSAY_EMPIRICAL'
LEGACY_MODEL = 'docs/analysis/sci_md_mass_delivery_001/models/BOUNDARY_AWARE_EMPIRICAL.json'
RUNTIME = ('puckworks/analysis/conditional_tail_delivery.py',)
DOC_NAMES = ('MODEL_CARD.md', 'PROTOCOL.md', 'SOURCE_IDENTITIES.json', 'DATA_AVAILABILITY_PREFLIGHT.json')
read = lambda path: md.strict_json(Path(path).read_text())
write = train.write_new
digest = source.digest


def git(expression):
    return subprocess.check_output(['git', 'rev-parse', expression], cwd=ROOT, text=True).strip()


def private_directory(path, create=False):
    path = Path(path).resolve()
    if any((parent/'.git').exists() for parent in (path, *path.parents)):
        raise ValueError('ROW_EVIDENCE_MUST_REMAIN_OUTSIDE_GIT')
    if create:
        path.mkdir(parents=True, exist_ok=False)
    return path


def qualified_sources():
    history = read(DOC/'SOURCE_IDENTITIES.json')
    source.verify_registers(history)
    paths = source.source_paths()
    if {k: digest(v) for k, v in paths.items()} != history['source_files']:
        raise ValueError('SOURCE_IDENTITY_DRIFT')
    return paths, history


def contract():
    value = read(DOC/'INFORMATION_CONTRACT.json')
    if value['task'] != TASK:
        raise ValueError('WRONG_TASK_CONTRACT')
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', value['contract_commit'], 'HEAD'], cwd=ROOT)
    for p, sha in value['files'].items():
        if digest(ROOT/p) != sha:
            raise ValueError('PRE_FIT_CONTRACT_DRIFT')
        old = subprocess.check_output(['git', 'show', value['contract_commit']+':'+p], cwd=ROOT)
        if source.hashlib.sha256(old).hexdigest() != sha:
            raise ValueError('CONTRACT_NOT_COMMITTED_BEFORE_FITTING')
    return value


def coordinates(paths):
    result = (source.coordinates('FIT_2021_12', paths)+fit_source.source_coordinates(paths)
              +source.coordinates('PREDICTION_2022_03', paths))
    for r in result:
        r.setdefault('coordinate_status', 'QUALIFIED')
    expected = {(f'{label}-E{i:02d}-R{r}', f) for label, count in [('FIT', 15), ('PRED', 8)]
                for i in range(1, count+1) for r in (1, 2, 3) for f in (1, 2)+SUFFIX}
    if {(r['shot'], r['fraction']) for r in result} != expected or len(result) != len(expected):
        raise ValueError('PHYSICAL_SHOT_MATRIX_MISMATCH')
    return sorted(result, key=lambda r: (r['shot'], r['fraction']))


def condition_groups():
    """Canonical repeated design labels share one fold; metadata never becomes features."""
    rows = [r for r in source.rows(source.DATA/'experiment_register.csv') if r['campaign_id'] == 'FIT_2021_12']
    keys = ('grind_setting', 'dose_g', 'nominal_temperature_program_id', 'nominal_flow_program_id')
    groups = {}
    for r in rows:
        groups.setdefault(tuple(r[k] for k in keys), set()).add(r['condition_id'])
    return {condition: min(labels) for labels in groups.values() for condition in labels}


def all_rows():
    return source.rows(source.DATA/'fit_fraction_replicates.csv')+source.rows(source.DATA/'prediction_fraction_replicates.csv')


def project_assays(rows, coords, *, outcome=False):
    # A parser may read the source container. Values cross this boundary ONLY
    # for the explicitly allowed campaign/fraction role.
    fit = [r for r in coords if r['shot'].startswith('FIT')]
    pred = [r for r in coords if r['shot'].startswith('PRED')
            and (r['fraction'] in SUFFIX if outcome else r['fraction'] in (1, 2))]
    fit_rows = [] if outcome else fit_source.assay_projection(
        [r for r in rows if r['campaign_id'] == 'FIT_2021_12'], fit, (1, 2)+SUFFIX)
    chosen = [r for r in rows if r['campaign_id'] == 'PREDICTION_2022_03'
              and int(r['fraction_id']) in (SUFFIX if outcome else (1, 2))]
    pred_rows = pred_source.selected_assays(chosen, pred, SUFFIX if outcome else (1, 2))
    return fit_rows, pred_rows


def verify_original_assays(paths, projected):
    """Inspect only already-permitted scalar assays against original TdS arrays."""
    objects = {label: source.mat(paths['P24-MAT-'+label])['ExperimentalData'] for label in ('FIT', 'PRED')}
    count = 0
    for r in projected:
        if r['q'] is None:
            continue
        label, exp, rep = r['shot'].split('-')
        if label == 'PRED' and r['fraction'] not in (1, 2):
            raise ValueError('ORIGINAL_SUFFIX_ACCESS_BEFORE_SCORE')
        value = float(objects[label][int(exp[1:])-1].run[int(rep[1:])-1].TdS[((1, 2)+SUFFIX).index(r['fraction'])])
        if abs(value/100-r['q']) > 5.001e-11:
            raise ValueError('ORIGINAL_ASSAY_EXPORT_ROUNDING_MISMATCH')
        count += 1
    return count


def projections(coords, rows):
    fit, early = project_assays(rows, coords)
    groups = condition_groups()
    training, pred_inputs, status = [], {}, []
    for shot in sorted({r['shot'] for r in coords}):
        selected = [r for r in (fit if shot.startswith('FIT') else early) if r['shot'] == shot]
        inputs = [r for r in selected if r['fraction'] in (1, 2)]
        valid = len(inputs) == 2 and all(r['eligible'] and r['coordinate_status'] == 'QUALIFIED' for r in inputs)
        if not valid:
            raise ValueError('MISSING_EARLY_INPUT:'+shot)
        first, second = sorted(inputs, key=lambda r: r['fraction'])
        if first['b0'] != 0 or abs(first['b1']-second['b0']) > 1e-15:
            raise ValueError('EARLY_COLLECTION_ORIGIN_OR_CONTIGUITY_MISMATCH')
        values = (first['mass_kg'], second['mass_kg'], first['q'], second['q'])
        if shot.startswith('FIT'):
            windows = []
            for r in selected:
                if r['fraction'] not in SUFFIX:
                    continue
                reason = r['coordinate_status'] if r['coordinate_status'] != 'QUALIFIED' else (
                    '' if r['eligible'] else r.get('source_reason', 'MISSING_CHEMISTRY'))
                status.append({'shot': shot, 'fraction': r['fraction'], 'eligible': not reason, 'reason': reason})
                if not reason:
                    windows.append(asdict(train.Window(r['fraction'], r['b0'], r['b1'], r['q'])))
            training.append({'shot': shot, 'group': groups[first['condition']],
                             'early_values': values, 'windows': windows})
        else:
            # Retain exact percent arithmetic for the frozen historical operator.
            pred_inputs[shot] = {'values': values, 'first_tds_percent': first['supplied_tds_percent']}
    flags = {(r['shot_id'], int(r['fraction_id'])): r['validity'] for r in source.deduplicate(
        [{'shot_id': r['shot_id'], 'fraction_id': r['fraction_id'], 'validity': r['validity']}
         for r in rows if r['analyte'] == 'TDS'], ('shot_id', 'fraction_id'))}
    queries = []
    domain = max(w['end_kg'] for s in training for w in s['windows'])
    legacy_domain = legacy.FrozenBase.load(ROOT/LEGACY_MODEL).curve().domain_kg[1]
    for r in coords:
        if not r['shot'].startswith('PRED') or r['fraction'] not in SUFFIX:
            continue
        reason = r['coordinate_status'] if r['coordinate_status'] != 'QUALIFIED' else (
            'OUTSIDE_TRAINING_MASS_DOMAIN' if r['b1'] > domain else '')
        if flags.get((r['shot'], r['fraction'])) != 'VALID':
            reason = 'INVALID_OR_MISSING_TDS_FLAG'
        legacy_reason = r['coordinate_status'] if r['coordinate_status'] != 'QUALIFIED' else (
            'OUTSIDE_LEGACY_MASS_DOMAIN' if r['b1'] > legacy_domain else '')
        queries.append({k: r[k] for k in ('condition', 'shot', 'fraction', 'b0', 'b1', 'mass_kg')} |
                       {'supported': not reason, 'reason': reason, 'tds_validity': flags.get((r['shot'], r['fraction'])),
                        'legacy_supported': not legacy_reason, 'legacy_reason': legacy_reason})
    return training, pred_inputs, queries, status, fit+early


def imported_files():
    return {str(Path(m.__file__).resolve().relative_to(ROOT)): digest(Path(m.__file__).resolve())
            for m in tuple(sys.modules.values()) if getattr(m, '__file__', None)
            and str(m.__file__).endswith('.py') and Path(m.__file__).resolve().is_relative_to(ROOT)}


def prepare(out):
    authority = contract()
    out = private_directory(out, create=True)
    paths, history = qualified_sources()
    coords = coordinates(paths)
    training, early, queries, statuses, inspected = projections(coords, all_rows())
    original_count = verify_original_assays(paths, inspected)
    # Each role is persisted separately; no full source-row object reaches fitting/prediction.
    for name, value in [('training.json', training), ('early_inputs.json', early),
                        ('queries.json', queries), ('training_support.json', statuses),
                        ('coordinates.json', coords), ('information_contract.json', authority)]:
        write(out/name, value)
    folds = train.folds(train.project_arm(training, 'C0'))
    write(out/'development_support.json', [{'group': g, 'domain_kg': b,
        'training_shots': [s.shot for s in t], 'held_shots': [s.shot for s in h],
        'support': support, 'intended_slots': 4*len(h)} for g, t, h, b, support in folds])
    counts = {'fit_conditions': len({s['group'] for s in training}), 'fit_shots': len(training),
        'fit_conditioning_assays': len(training)*2, 'fit_intended_suffix': len(statuses),
        'fit_eligible_suffix': sum(s['eligible'] for s in statuses),
        'fit_support_reasons': dict(Counter(s['reason'] for s in statuses if s['reason'])),
        'pred_shots': len(early), 'pred_early_assays': 2*len(early), 'pred_intended_suffix': len(queries),
        'pred_supported_suffix': sum(q['supported'] for q in queries),
        'legacy_supported_suffix': sum(q['legacy_supported'] for q in queries),
        'panels': {p: {'shots': 3*len(cs), 'intended_slots': 12*len(cs),
            'learned_supported': sum(q['supported'] for q in queries if q['condition'] in cs),
            'legacy_supported': sum(q['legacy_supported'] for q in queries if q['condition'] in cs)}
            for p, cs in PANELS.items()}, 'permitted_original_assays_crosschecked': original_count}
    write(out/'source.json', dict(history, task=TASK, counts=counts, rights=source.RIGHTS,
        roles='45 FIT shots train; former 30 FIT-transfer shots reclassified ONLY for 006',
        shared_pannusch_schmieder_lineage_counted_once=True, inspected_originals=list(paths),
        final_fit_domain_kg=max(w['end_kg'] for s in training for w in s['windows']),
        legacy_domain_kg=legacy.FrozenBase.load(ROOT/LEGACY_MODEL).curve().domain_kg[1],
        source_rounding_is_measurement_uncertainty=False))
    write(out/'preparation_runtime.json', imported_files())
    print(json.dumps(counts, indent=2))


def verify_prepared(out):
    out = private_directory(out)
    if (out/'freeze.json').exists() or (out/'score_receipt.json').exists():
        raise ValueError('FROZEN_OR_SCORED_TASK_REFUSES_FITTING')
    contract()
    qualified_sources()
    return out


def develop(out):
    out = verify_prepared(out)
    folder = out/'development'
    folder.mkdir(exist_ok=False)
    budget = train.Budget(out/'starts')
    return train.develop(read(out/'training.json'), folder, budget,
                         training_source_identity(read(out/'source.json')), source.RIGHTS)


def training_source_identity(history):
    """Model provenance depends on FIT source bytes, not PRED outcome hashes."""
    return md.identity({'originals': {k: v for k, v in history['source_files'].items() if k.endswith('-FIT')},
                        'FIT_assay_export': history['registers']['fit_fraction_replicates.csv']})


def final_fit(out):
    out = verify_prepared(out)
    folder = out/'models'
    folder.mkdir(exist_ok=False)
    budget = train.Budget(out/'starts')
    selection = read(out/'development/development.json')
    for arm in md.ARMS:
        lam = selection['arms'][arm]['selected_lambda']
        if lam is None:
            write(folder/(arm+'.failure.json'), {'status': 'NO_SELECTABLE_LAMBDA'})
            continue
        model, audit = train.fit(train.project_arm(read(out/'training.json'), arm), lam,
            budget, 'final.'+arm, training_source_identity(read(out/'source.json')), source.RIGHTS)
        write(folder/(arm+'.audit.json'), audit)
        if model is not None:
            model.save(folder/(arm+'.json'))
        else:
            write(folder/(arm+'.failure.json'), {'status': audit['status']})


def legacy_predictions(early, queries, retained_path):
    historical = read(ROOT/'docs/analysis/sci_md_mass_delivery_005/PRIVATE_EVIDENCE_MANIFEST.json')
    if digest(Path(retained_path)) != historical['private_artifacts']['predictions.json']:
        raise ValueError('RETAINED_005_PREDICTIONS_IDENTITY_MISMATCH')
    retained = {(r['shot'], r['fraction']): r for r in read(retained_path)[LEGACY] if r['shot'].startswith('PRED')}
    base = legacy.FrozenBase.load(ROOT/LEGACY_MODEL)
    frozen = read(ROOT/'docs/analysis/sci_md_mass_delivery_005/FREEZE.json')
    for path in (LEGACY_MODEL, 'puckworks/analysis/mass_delivery.py',
                 'puckworks/analysis/conditioned_mass_delivery.py', 'puckworks/analysis/anchored_mass_delivery.py'):
        if digest(ROOT/path) != frozen['code_and_protocol'][path]:
            raise ValueError('LEGACY_RUNTIME_OR_MODEL_DRIFT')
    result, states = [], {}
    for q in queries:
        record = prediction_record(q)
        try:
            if not q['legacy_supported']:
                raise ValueError(q['legacy_reason'])
            old = retained.get((q['shot'], q['fraction']))
            if old is not None:
                if any(old[k] != q[k] for k in ('shot', 'fraction', 'b0', 'b1', 'mass_kg')):
                    raise ValueError('LEGACY_QUERY_IDENTITY_MISMATCH')
                record.update({k: old[k] for k in ('predicted_solute_kg', 'predicted_tds_percent',
                    'numerical_allowance_kg', 'numerical_qualified', 'prediction_status')})
                record['origin'] = 'REUSED_005_FROZEN_PREDICTION'
            else:
                shot = q['shot']
                if shot not in states:
                    data = early[shot]
                    observation = legacy.AnchorInput(shot, 'P24-MAT-PRED', 1, 0., data['values'][0],
                        data['first_tds_percent'], 'MEASURED_MASS_G_CONVERTED_TO_KG', source.RIGHTS,
                        'MEASURED_SOURCE_ANCHOR_INPUT')
                    states[shot] = legacy.anchor(base, observation)
                p = states[shot].predict_intervals((legacy.IntervalQuery(q['b0'], q['b1']),))[0]
                record.update(predicted_solute_kg=p.solute_kg, predicted_tds_percent=p.tds_percent,
                    numerical_allowance_kg=p.numerical_allowance_kg,
                    numerical_qualified=p.numerical_allowance_kg <= 1e-9,
                    prediction_status='QUALIFIED' if p.numerical_allowance_kg <= 1e-9 else 'NUMERICALLY_UNRESOLVED',
                    origin='EXACT_LEGACY_OPERATOR_NEW_STRESS_QUERY')
        except ValueError as exc:
            record['prediction_status'] = str(exc)
        result.append(record)
    return result


def prediction_record(q):
    return dict(q, predicted_solute_kg=None, predicted_tds_percent=None,
                numerical_allowance_kg=None, numerical_qualified=False, prediction_status='',
                feature_extrapolation=[])


def source_query_start(query, state):
    """Reconcile ONLY the measured fraction-3 shared boundary in kg arithmetic.

    The accepted source multiplies a cumulative gram sum by .001, whereas the
    forecast anchor sums two separately converted vial masses. Their identical
    physical boundary can differ by ulps. Retain the original coordinate and
    explicitly account for this conversion roundoff; generic runtime queries
    before the anchor still fail, without a tolerance or hidden clipping.
    """
    a = query['b0']
    if query['fraction'] == 3 and a != state.b_anchor:
        delta = abs(a-state.b_anchor)
        if delta > 4*abs(np.spacing(state.b_anchor)):
            raise ValueError('MEASURED_FRACTION_THREE_ANCHOR_MISMATCH')
        return state.b_anchor, 2*delta
    return a, 0.


def predict(out, retained_legacy):
    out = verify_prepared(out)
    started = time.monotonic()
    early, queries = read(out/'early_inputs.json'), read(out/'queries.json')
    models = {arm: md.Model.load(out/'models'/(arm+'.json')) if (out/'models'/(arm+'.json')).exists() else None for arm in md.ARMS}
    predictions, states = {}, {}
    for arm, model in models.items():
        predictions[arm] = []
        for q in queries:
            record = prediction_record(q)
            try:
                if not q['supported']:
                    raise ValueError(q['reason'])
                if model is None:
                    raise ValueError('MODEL_FIT_FAILED')
                key = arm+'/'+q['shot']
                if key not in states:
                    states[key] = model.condition(md.EarlyInput(arm,
                        tuple(early[q['shot']]['values'][:len(model.means)]), 'SOURCE_EARLY_INPUT'))
                state = states[key]
                start, coordinate_allowance = source_query_start(q, state)
                p = state.predict_intervals([start], [q['b1']])[0]
                allowance = p.allowance_kg+coordinate_allowance
                record.update(predicted_solute_kg=p.solute_kg, predicted_tds_percent=p.tds_percent,
                    numerical_allowance_kg=allowance, numerical_qualified=allowance <= 1e-9,
                    prediction_status='QUALIFIED' if allowance <= 1e-9 else 'NUMERICALLY_UNRESOLVED',
                    integration_start_kg=start, coordinate_roundoff_allowance_kg=coordinate_allowance,
                    feature_extrapolation=list(state.feature_extrapolation))
            except ValueError as exc:
                record['prediction_status'] = str(exc)
            predictions[arm].append(record)
    predictions[LEGACY] = legacy_predictions(early, queries, retained_legacy)
    write(out/'predictions.json', predictions)
    write(out/'states.json', {k: s.to_dict() for k, s in states.items()})
    ends = [read(p) for p in sorted((out/'starts').glob('*.end.json'))]
    execution = {'task': TASK, 'fitting_workers': 1, 'blas_threads': 1,
        'starts': len(list((out/'starts').glob('*.start.json'))), 'completed_starts': len(ends),
        'converged_starts': sum(r['status'] == 'CONVERGED' for r in ends),
        'failed_starts': sum(r['status'] != 'CONVERGED' for r in ends),
        'residual_calls': sum(r['actual_residual_calls'] for r in ends),
        'numerical_jacobian_residual_calls': sum(r['numerical_jacobian_residual_calls'] or 0 for r in ends),
        'max_residual_calls_per_start': max(r['actual_residual_calls'] for r in ends),
        'starts_with_boundary_hits': sum(bool(r['boundary_indices']) for r in ends),
        'fit_wall_seconds': sum(r['elapsed_seconds'] for r in ends),
        'prediction_wall_seconds': time.monotonic()-started,
        'peak_fit_rss_kib': max(r['peak_rss_kib'] for r in ends),
        'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
        'imported_first_party_modules': imported_files(), 'legacy_retained_sha256': digest(Path(retained_legacy)),
        'prediction_status_counts': {a: dict(Counter(p['prediction_status'] for p in ps)) for a, ps in predictions.items()},
        'max_allowance_kg': max(p['numerical_allowance_kg'] for ps in predictions.values() for p in ps if p['numerical_allowance_kg'] is not None),
        'scientific_score_passes': 0, 'native_ewp_runs': 0, 'physical_validation': 'NOT_ESTABLISHED'}
    write(out/'execution.json', execution)
    print(json.dumps({k: v for k, v in execution.items() if k != 'imported_first_party_modules'}, indent=2))


def freeze(out):
    out = private_directory(out)
    contract(); qualified_sources()
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('CLEAN_COMMITTED_IMPLEMENTATION_REQUIRED')
    execution = read(out/'execution.json')
    paths = set(execution['imported_first_party_modules']) | set(read(out/'preparation_runtime.json'))
    paths |= {'puckworks/analysis/conditional_tail_scoring.py', LEGACY_MODEL}
    paths |= {str(p.relative_to(ROOT)) for p in DOC.glob('*') if p.is_file()}
    paths |= {str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('test_*conditional_tail*.py')}
    for p, h in execution['imported_first_party_modules'].items():
        if digest(ROOT/p) != h:
            raise ValueError('EVALUATED_RUNTIME_DRIFT')
    artifacts = {str(p.relative_to(out)): digest(p) for p in out.rglob('*.json')}
    write(out/'freeze.json', {'task': TASK, 'producer_commit': git('HEAD'), 'producer_tree': git('HEAD^{tree}'),
        'code_and_protocol': {p: digest(ROOT/p) for p in sorted(paths)}, 'artifacts': artifacts,
        'primary_candidate': 'C2', 'arms': list(md.ARMS)+( [LEGACY]), 'panels': PANELS,
        'scoring_policy': 'ONE_INDEPENDENTLY_APPROVED_PASS_NO_RETUNING'})
    print('READY_FOR_INDEPENDENT_REVIEW', digest(out/'freeze.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'develop', 'fit', 'predict', 'freeze', 'score', 'report'):
        p = sub.add_parser(name); p.add_argument('--out', required=True, type=Path)
        if name == 'predict':
            p.add_argument('--retained-legacy', required=True, type=Path)
        if name == 'score':
            p.add_argument('--review', required=True, type=Path)
    args = parser.parse_args()
    if args.command in ('develop', 'fit'):
        if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
            parser.error('Set OPENBLAS_NUM_THREADS=OMP_NUM_THREADS=MKL_NUM_THREADS=1 before Python starts.')
    if args.command == 'predict':
        predict(args.out, args.retained_legacy)
    elif args.command in ('score', 'report'):
        from . import conditional_tail_scoring as scoring
        if args.command == 'score':
            scoring.score(args.out, args.review)
        else:
            print(json.dumps(scoring.report(args.out), indent=2))
    else:
        {'prepare': prepare, 'develop': develop, 'fit': final_fit, 'freeze': freeze}[args.command](args.out)


if __name__ == '__main__':
    main()

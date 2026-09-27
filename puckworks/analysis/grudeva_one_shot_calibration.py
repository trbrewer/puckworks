"""008 private source preparation, one-shot fitting and outcome-free prediction.

Exactly one calibration shot per forecast. No historical fitting/scoring calls.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import inspect
import math
import os
from pathlib import Path
import platform
import resource
import signal
import time

import numpy as np
import scipy
from scipy.optimize import least_squares

from . import conditional_tail_delivery as md
from . import grudeva_clock as gc
from . import grudeva_pooled_tail_delivery as old
from . import source_calibrated_tail_delivery as api

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_mass_delivery_008'
TASK = 'SCI-MD-MASS-DELIVERY-008'
VERSION = 'grudeva-one-shot/1'
ARMS = ('F2', 'A2', 'A0', 'M')
STARTS = ((.2, .03, 1), (.3, .08, 1), (.1, .02, .5), (.5, .1, 2),
          (.25, .05, 4), (.4, .15, .25), (.15, 0, 1), (.75, .3, 3))
MASS_SETTINGS = {'bounds': [[0, 0, .25], [1, 10, 4]], 'method': 'trf', 'jac': '2-point',
                 'ftol': 1e-10, 'xtol': 1e-10, 'gtol': 1e-10, 'x_scale': [.2, .05, 1],
                 'diff_step': 1e-6, 'max_nfev': 2000, 'tr_solver': 'exact', 'loss': 'linear'}
read, digest, write, private, git = old.read, old.digest, old.write, old.private, old.git
SCIENCE_FILES = ('puckworks/analysis/conditional_tail_delivery.py',
                 'puckworks/analysis/grudeva_clock.py',
                 'puckworks/analysis/grudeva_pooled_tail_delivery.py',
                 'puckworks/analysis/source_calibrated_tail_delivery.py',
                 'puckworks/analysis/grudeva_one_shot_calibration.py',
                 'puckworks/analysis/grudeva_one_shot_scoring.py')


def verify_dependencies():
    models, parent, source = old.verify_dependencies(ROOT, ROOT/'docs/analysis/sci_md_mass_delivery_007')
    if STARTS != gc.SINGLE_STARTS:
        raise ValueError('INHERITED_EIGHT_STARTS_MISMATCH')
    for module in (md, gc, old, api):
        actual = Path(inspect.getfile(module)).resolve()
        expected = ROOT/'puckworks/analysis'/actual.name
        if actual != expected.resolve() or digest(actual) != digest(expected):
            raise ValueError('ACTUAL_IMPORTED_RUNTIME_MISMATCH')
    accepted = read(ROOT/'docs/analysis/sci_md_mass_delivery_007/FREEZE.json')
    for name in SCIENCE_FILES[:3]:
        if digest(ROOT/name) != accepted['code_and_protocol'][name]:
            raise ValueError('ACCEPTED_PARENT_ADAPTER_OR_PARSER_DRIFT')
    for name in ('SOURCE.json', 'PARENT_006_HANDOFF.json'):
        if digest(DOC/name) != digest(old.DOC/name):
            raise ValueError('ACCEPTED_SOURCE_OR_PARENT_HANDOFF_DRIFT')
    return models, parent, source


def verify_manifest(out, name):
    out = Path(out); manifest = read(out/name)
    if manifest['task'] != TASK:
        raise ValueError('WRONG_TASK')
    for relative, expected in manifest['files'].items():
        path = (out/relative).resolve()
        if not path.is_relative_to(out.resolve()) or digest(path) != expected:
            raise ValueError('FROZEN_ARTIFACT_DRIFT:'+relative)
    return manifest


def prepare(source_root, prior, out):
    models, parent, source = verify_dependencies()
    prior = Path(prior); out = private(out, create=True)
    authority = read(DOC/'PARENT_007_MANIFEST.json')
    if md.canonical(authority) != md.canonical(read(old.DOC/'PREDICTION_MANIFEST.json')):
        raise ValueError('ACCEPTED_007_MANIFEST_REQUIRED')
    for name, expected in authority['source_role_support_hashes'].items():
        if digest(prior/name) != expected:
            raise ValueError('ACCEPTED_007_ROLE_PROJECTION_MISMATCH:'+name)
    if digest(prior/'predictions.json') != authority['prediction_sha256']:
        raise ValueError('ACCEPTED_007_PREDICTIONS_REQUIRED')
    for name, expected in source['files'].items():
        if digest(Path(source_root)/name) != expected:
            raise ValueError('ACCEPTED_ORIGINAL_SOURCE_BYTES_REQUIRED')
    records = gc.parse_source(Path(source_root)/'exp13.csv')
    early, queries, support, cohort, pools = old.project(records, models['C2'].means[:2])
    for name, value in zip(('early_inputs.json', 'queries.json', 'support.json', 'cohort.json', 'pools.json'),
                           (early, queries, support, cohort, pools)):
        if md.canonical(value) != md.canonical(read(prior/name)):
            raise ValueError('COHORT_OR_PROJECTION_RECONCILIATION_REQUIRED:'+name)
    source_index = {(r['shot'], r['vial']): r for r in records}
    outcomes = []
    for q in queries:
        r = source_index[(q['shot'], q['vial'])]; status = old.chemistry_status(r)
        outcomes.append({'shot': q['shot'], 'vial': q['vial'], 'chemistry_status': status,
                         'q': r['tds_pct']/100 if status == 'AVAILABLE' else None,
                         'solute_kg': 0. if status == 'STRUCTURAL_ZERO' else
                             r['mass_g']/1000*r['tds_pct']/100 if status == 'AVAILABLE' else None})
    prior_completion = read(old.DOC/'SCORE_COMPLETION.json')
    if (digest(prior/'observed_suffix.json') != prior_completion['observed_suffix_sha256']
            or md.canonical(outcomes) != md.canonical(read(prior/'observed_suffix.json'))):
        raise ValueError('ACCEPTED_OUTCOME_PROJECTION_RECONCILIATION_REQUIRED')
    shots = sorted(r['shot'] for r in cohort if r['eligible'])
    if len(shots) < 2:
        raise ValueError('INSUFFICIENT_CALIBRATION_TARGET_COHORT')
    inputs = old.input_index(early); oi = {(o['shot'], o['vial']): o for o in outcomes}
    files = {'early_inputs.json': [r for r in early if r['arm'] in ('C0', 'C2')],
             'queries.json': queries, 'support.json': support, 'cohort.json': cohort,
             'outcomes.json': outcomes, 'frozen_f2.json': read(prior/'predictions.json')['C2'],
             'counts.json': read(prior/'counts.json'),
             'folds.json': {'calibrators': shots, 'targets': shots,
                            'pairs': [[j, i] for j in shots for i in shots if j != i],
                            'intended_slots_per_arm': (len(shots)-1)*len(queries),
                            'unique_suffix_windows': len(queries), 'original_shots': 13},
             'source_binding.json': {'source': source, 'parent_models': {a: m.sha256 for a, m in models.items()},
                 'parent_commit': parent['producer_commit'], 'parent_tree': parent['producer_tree'],
                 'accepted_007_prediction_sha256': authority['prediction_sha256'],
                 'accepted_007_manifest_sha256': digest(old.DOC/'PREDICTION_MANIFEST.json')}}
    for shot in shots:
        windows = tuple(api.Observation(**q, q=oi[(shot, q['vial'])]['q']) for q in queries if q['shot'] == shot)
        for arm, parent_arm in (('A0', 'C0'), ('A2', 'C2'), ('M', None)):
            record = api.CalibrationRecord(gc.SOURCE_SHA, shot, inputs[(parent_arm, shot)] if parent_arm else None, windows)
            files[f'record-{shot:02}-{arm}.json'] = record.to_dict()
    for name, value in files.items():
        write(out/name, value)
    write(out/'prepare_manifest.json', {'task': TASK, 'version': VERSION,
        'files': {name: digest(out/name) for name in files},
        'source_sha256': gc.SOURCE_SHA, 'source_projection_comparison': 'EXACT_ACCEPTED_007'})
    return files['folds.json']


def fit_mass(record, domain_kg, attempt_sink=None):
    """Task-local weighted-TDS fit; receives exactly one shot and no early assays."""
    if not isinstance(record, api.CalibrationRecord) or record.early is not None:
        raise ValueError('ONE_SHOT_SUFFIX_ONLY_MASS_RECORD_REQUIRED')
    used = [w for w in record.windows if w.mass_kg > 0 and w.q is not None]
    rg = (min(w.start_kg for w in record.windows), max(w.end_kg for w in record.windows))
    base = (record.source_sha256, record.shot, record.sha256)
    if not used or any(w.mass_kg > 0 and w.q is None for w in record.windows):
        return api.MassCalibration(*base, None, domain_kg, rg, 'CALIBRATION_SUPPORT_FAILURE'), []
    rows = api.gram_rows([w.start_kg for w in used], [w.end_kg for w in used])
    weights = np.sqrt(np.array([w.mass_kg for w in used])/math.fsum(w.mass_kg for w in used))
    masses = np.array([w.mass_kg for w in used]); target = 100*np.array([w.q for w in used])
    attempts, solutions = [], []
    for index, start in enumerate(STARTS):
        calls = 0; last = {}; tick = time.monotonic()
        if attempt_sink:
            attempt_sink(index, 'start', {'start_index': index, 'start': list(start), 'status': 'STARTED'})
        def residual(x):
            nonlocal calls
            if calls >= 2000:
                raise RuntimeError('ACTUAL_RESIDUAL_CALL_CAP')
            calls += 1
            theta = gc.unpack(x, 'MASS')
            residuals = (100*(gc.deliver(rows, theta)/1000)/masses-target)*weights
            last.update(theta=list(theta), objective=float(residuals@residuals))
            return residuals
        rec = {'start_index': index, 'start': list(start), 'success': False, 'selected': False}
        interrupted = None
        try:
            result = least_squares(residual, start, **MASS_SETTINGS)
            theta = tuple(map(float, gc.unpack(result.x, 'MASS'))); objective = float(2*result.cost)
            success = bool(result.success and result.status > 0 and np.isfinite(theta).all() and math.isfinite(objective))
            rec.update(success=success, status=int(result.status), termination=str(result.message),
                       theta=list(theta), objective=objective, nfev=int(result.nfev), njev=int(result.njev),
                       numerical_jacobian_calls=calls-int(result.nfev))
            if success:
                solutions.append((objective, index, theta))
        except (ValueError, RuntimeError, FloatingPointError, OverflowError) as exc:
            rec.update(status=-99, termination=str(exc), theta=None, objective=None,
                       nfev=None, njev=None, numerical_jacobian_calls=None)
        except (TimeoutError, MemoryError) as exc:
            interrupted = exc
            rec.update(status=-100, termination=str(exc), theta=None, objective=None,
                       nfev=None, njev=None, numerical_jacobian_calls=None)
        rec.update(actual_residual_calls=calls, last=last, wall_seconds=time.monotonic()-tick)
        t = rec['theta'] or last.get('theta')
        rec['boundary_hits'] = [name for name, value, lo, hi in zip(('c0', 'a_m', 'p'), (t[0], t[2], t[3]),
                                   (0., 0., .25), (1., 10., 4.)) if min(abs(value-lo), abs(value-hi)) <= 1e-7] if t else []
        attempts.append(rec)
        if attempt_sink:
            attempt_sink(index, 'completion', rec)
        if interrupted is not None:
            raise interrupted
    if not solutions:
        return api.MassCalibration(*base, None, domain_kg, rg, 'ALL_STARTS_FAILED'), attempts
    _, selected, theta = min(solutions, key=lambda v: (v[0], v[1]))
    attempts[selected]['selected'] = True
    return api.MassCalibration(*base, theta, domain_kg, rg, 'QUALIFIED'), attempts


def limits(out, previous_seconds=0.):
    """One task worker: enforce remaining scientific wall, address space and artifacts."""
    if any(os.environ.get(k) != '1' for k in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS')):
        raise ValueError('ONE_BLAS_THREAD_REQUIRED')
    if previous_seconds >= 3600:
        raise ValueError('SCIENTIFIC_WALL_CAP')
    resource.setrlimit(resource.RLIMIT_AS, (8*1024**3, 8*1024**3))
    def expired(*_):
        raise TimeoutError('SCIENTIFIC_WALL_CAP')
    signal.signal(signal.SIGALRM, expired); signal.setitimer(signal.ITIMER_REAL, 3600-previous_seconds)
    artifact_limit(out)


def artifact_limit(out):
    if sum(p.stat().st_size for p in Path(out).rglob('*') if p.is_file()) > 2*1024**3:
        raise ValueError('PRIVATE_ARTIFACT_CAP')


def calibrate(out):
    out = private(out); verify_manifest(out, 'prepare_manifest.json')
    models, _, _ = verify_dependencies(); shots = read(out/'folds.json')['calibrators']
    if git(ROOT, 'status', '--porcelain'):
        raise ValueError('COMMITTED_PROTOCOL_AND_CODE_REQUIRED')
    start = time.monotonic(); limits(out)
    write(out/'calibration_start.json', {'task': TASK, 'status': 'STARTED',
          'prepare_manifest_sha256': digest(out/'prepare_manifest.json'),
          'producer_commit': git(ROOT, 'rev-parse', 'HEAD'), 'producer_tree': git(ROOT, 'rev-parse', 'HEAD^{tree}'),
          'planned_scalars': 2*len(shots), 'planned_mass_fits': len(shots), 'planned_starts': 8*len(shots)})
    files, statuses, starts, scalars = {}, {}, [], 0
    try:
        for shot in shots:
            for arm in ('A0', 'A2', 'M'):
                # Only this named shot's task-local record reaches the worker.
                record = api.CalibrationRecord.load(out/f'record-{shot:02}-{arm}.json')
                if record.shot != shot:
                    raise ValueError('WRONG_CALIBRATION_WORKER_RECORD')
                if arm == 'M':
                    def retain_attempt(index, phase, value):
                        name = f'mass-{shot:02}-start-{index:02}-{phase}.json'
                        write(out/name, value); files[name] = digest(out/name)
                    artifact, attempts = fit_mass(record, models['C0'].domain_kg, retain_attempt)
                    name = f'attempts-{shot:02}.json'; write(out/name, attempts); files[name] = digest(out/name)
                    starts.extend(attempts)
                else:
                    scalars += 1; artifact = api.calibrate_source(models['C'+arm[1:]], record)
                name = f'calibration-{shot:02}-{arm}.json'; artifact.save(out/name); files[name] = digest(out/name)
                statuses[f'{shot}/{arm}'] = {'status': artifact.status, 'sha256': artifact.sha256,
                                            'record_sha256': artifact.record_sha256}
                artifact_limit(out)
        write(out/'calibration_manifest.json', {'task': TASK, 'files': files, 'calibrations': statuses})
        completion = {'task': TASK, 'status': 'COMPLETE', 'scalar_calibrations': scalars,
             'mass_fits': len(shots), 'nonlinear_starts': len(starts),
             'actual_residual_calls': sum(r['actual_residual_calls'] for r in starts),
             'maximum_calls_per_start': max(r['actual_residual_calls'] for r in starts),
             'failed_starts': sum(not r['success'] for r in starts),
             'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
             'workers': 1, 'blas_threads': 1, 'wall_seconds': time.monotonic()-start,
             'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             'files': {'calibration_manifest.json': digest(out/'calibration_manifest.json'),
                       'calibration_start.json': digest(out/'calibration_start.json')}}
        write(out/'calibration_completion.json', completion)
    except BaseException as exc:
        write(out/'calibration_failure.json', {'task': TASK, 'reason': str(exc), 'scalar_attempts': scalars,
                                              'completed_starts': len(starts), 'wall_seconds': time.monotonic()-start})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def load_artifact(value, arm, calibrator, source_sha256, parent_models):
    if arm == 'M':
        return api.MassCalibration.from_dict(value, calibrator=calibrator, source_sha256=source_sha256)
    if arm not in ('A0', 'A2'):
        raise ValueError('CALIBRATED_ARM_REQUIRED')
    return api.OffsetCalibration.from_dict(value, calibrator=calibrator, source_sha256=source_sha256,
                                           parent_sha256=parent_models['C'+arm[1:]])


def predict_pair(artifact, target, early, queries):
    """No outcomes-bearing dictionaries or training records can cross this API."""
    api.shot_number(target)
    if artifact.calibrator == target:
        raise ValueError('FORBIDDEN_DIAGONAL')
    if not isinstance(early, md.EarlyInput):
        raise ValueError('TYPED_TARGET_EARLY_INPUT_REQUIRED')
    checked = [old.checked_query(q) for q in queries]
    if any(q['shot'] != target for q in checked) or len({q['vial'] for q in checked}) != len(checked):
        raise ValueError('ONE_TARGET_UNIQUE_COORDINATE_QUERIES_REQUIRED')
    # Validate information privileges even for a failed calibration.
    arm = 'C0' if isinstance(artifact, api.MassCalibration) else artifact.parent.arm
    if early.arm != arm:
        raise ValueError('TARGET_INFORMATION_PRIVILEGE_MISMATCH')
    output = []
    for q in checked:
        rec = dict(q, calibrator=artifact.calibrator, calibration_sha256=artifact.sha256,
                   status=artifact.status, prediction=None, feature_extrapolation=[],
                   calibration_mass_extrapolation=False, integration_start_kg=None,
                   integration_end_kg=None, coordinate_allowance_kg=0.)
        try:
            state = artifact.condition(early)
            rec['feature_extrapolation'] = list(state.feature_extrapolation)
            a, b, allowance = old.runtime_coordinates(q, state.b_anchor)
            if isinstance(artifact, api.MassCalibration):
                lo, hi = artifact.calibration_range_kg
                rec['calibration_mass_extrapolation'] = a < lo or b > hi
            p = asdict(state.predict_intervals([a], [b])[0])
            p['allowance_kg'] += allowance; p['numerical_qualified'] = p['allowance_kg'] <= 1e-9
            if p['solute_kg'] < -p['allowance_kg'] or p['solute_kg'] > q['mass_kg']+p['allowance_kg']:
                raise ValueError('SOLUTE_CONSERVATION_BOUND_FAILURE')
            rec.update(status='QUALIFIED' if p['numerical_qualified'] else 'NUMERICALLY_UNRESOLVED',
                       prediction=p, integration_start_kg=a, integration_end_kg=b, coordinate_allowance_kg=allowance)
        except (ValueError, FloatingPointError, OverflowError) as exc:
            rec['status'] = str(exc)
        output.append(rec)
    return output


def predict_matrix(artifacts, early, queries, folds, frozen_f2, binding):
    md.exact_keys(folds, ('calibrators', 'targets', 'pairs', 'intended_slots_per_arm', 'unique_suffix_windows', 'original_shots'))
    shots = folds['calibrators']
    if (shots != sorted(set(shots)) or folds['targets'] != shots or len(shots) < 2
            or folds['pairs'] != [[j, i] for j in shots for i in shots if j != i]):
        raise ValueError('ALL_OFF_DIAGONAL_FOLDS_REQUIRED')
    inputs = old.input_index(early)
    if set(inputs) != {(a, s) for a in ('C0', 'C2') for s in shots}:
        raise ValueError('EXACT_TARGET_EARLY_MATRIX_REQUIRED')
    if set(artifacts) != {f'{j}/{a}' for j in shots for a in ('A0', 'A2', 'M')}:
        raise ValueError('ALL_CALIBRATION_CHOICES_REQUIRED')
    keys = [(q['shot'], q['vial']) for q in queries]
    if len(set(keys)) != len(keys) or set(q['shot'] for q in queries) != set(shots):
        raise ValueError('EXACT_TARGET_COORDINATE_MATRIX_REQUIRED')
    if len(queries) != folds['unique_suffix_windows'] or len(queries)*(len(shots)-1) != folds['intended_slots_per_arm']:
        raise ValueError('FROZEN_SLOT_DENOMINATOR_REQUIRED')
    ref = {(r['shot'], r['vial']): r for r in frozen_f2}
    if len(ref) != len(frozen_f2) or set(ref) != set(keys):
        raise ValueError('EXACT_F2_REFERENCE_MATRIX_REQUIRED')
    for q in queries:
        old.checked_query(q)
        if any(ref[(q['shot'], q['vial'])][k] != v for k, v in q.items()):
            raise ValueError('F2_REFERENCE_COORDINATE_MISMATCH')
    output = {a: [] for a in ARMS}
    for j, i in folds['pairs']:
        qs = [q for q in queries if q['shot'] == i]
        for q in qs:
            r = ref[(i, q['vial'])]
            output['F2'].append(dict(r, calibrator=j, calibration_sha256=None,
                                     calibration_mass_extrapolation=False,
                                     historical_prediction_sha256=binding['accepted_007_prediction_sha256']))
        for arm in ('A2', 'A0', 'M'):
            artifact = load_artifact(artifacts[f'{j}/{arm}'], arm, j, binding['source']['files']['exp13.csv'], binding['parent_models'])
            output[arm].extend(predict_pair(artifact, i, inputs[('C2' if arm == 'A2' else 'C0', i)], qs))
    return output


def predict(out):
    out = private(out); verify_dependencies(); verify_manifest(out, 'prepare_manifest.json')
    verify_manifest(out, 'calibration_manifest.json'); verify_manifest(out, 'calibration_completion.json')
    elapsed = read(out/'calibration_completion.json')['wall_seconds']; limits(out, elapsed); start = time.monotonic()
    write(out/'prediction_start.json', {'task': TASK, 'status': 'STARTED',
          'prepare_manifest_sha256': digest(out/'prepare_manifest.json'),
          'calibration_manifest_sha256': digest(out/'calibration_manifest.json'),
          'producer_commit': git(ROOT, 'rev-parse', 'HEAD'), 'producer_tree': git(ROOT, 'rev-parse', 'HEAD^{tree}')})
    try:
        folds = read(out/'folds.json')
        artifacts = {f'{j}/{a}': read(out/f'calibration-{j:02}-{a}.json') for j in folds['calibrators'] for a in ('A0', 'A2', 'M')}
        predictions = predict_matrix(artifacts, read(out/'early_inputs.json'), read(out/'queries.json'), folds,
                                     read(out/'frozen_f2.json'), read(out/'source_binding.json'))
        write(out/'predictions.json', predictions)
        write(out/'prediction_completion.json', {'task': TASK, 'status': 'COMPLETE', 'planned_prediction_matrices': 1,
              'scientific_score_passes': 0, 'wall_seconds': time.monotonic()-start,
              'scientific_wall_seconds': elapsed+time.monotonic()-start,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'status_counts': {a: dict(Counter(r['status'] for r in rows)) for a, rows in predictions.items()},
              'maximum_allowance_kg': max((r['prediction']['allowance_kg'] for rows in predictions.values() for r in rows if r['prediction']), default=0.),
              'files': {'predictions.json': digest(out/'predictions.json'), 'prediction_start.json': digest(out/'prediction_start.json')}})
        artifact_limit(out)
    except BaseException as exc:
        write(out/'prediction_failure.json', {'task': TASK, 'reason': str(exc), 'wall_seconds': time.monotonic()-start})
        raise
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def freeze(out, consumer):
    out = private(out); consumer = Path(consumer)
    verify_dependencies()
    for name in ('prepare_manifest.json', 'calibration_manifest.json', 'calibration_completion.json', 'prediction_completion.json'):
        verify_manifest(out, name)
    if any(git(r, 'status', '--porcelain') for r in (ROOT, consumer)):
        raise ValueError('CLEAN_COMMITTED_FREEZE_REQUIRED')
    handoff = consumer/'docs/analysis/sci_md_mass_delivery_008/HANDOFF.json'; pin = read(handoff)
    if pin['producer_commit'] != git(ROOT, 'rev-parse', 'HEAD') or pin['producer_tree'] != git(ROOT, 'rev-parse', 'HEAD^{tree}'):
        raise ValueError('EXACT_CONSUMER_PRODUCER_PIN_REQUIRED')
    parity = read(out/'consumer_equivalence.json')
    if (parity['status'] != 'PASS' or parity['predictions_sha256'] != digest(out/'predictions.json')
            or parity['handoff_sha256'] != digest(handoff)):
        raise ValueError('COMPLETE_CONSUMER_PARITY_REQUIRED')
    bound = list(SCIENCE_FILES)+['tests/test_source_calibrated_tail_delivery.py', 'tests/test_grudeva_one_shot_calibration.py']
    bound += [str(p.relative_to(ROOT)) for p in DOC.iterdir() if p.is_file()]
    cfiles = ['scripts/research_grudeva_one_shot_calibration.py', 'tests/test_research_grudeva_one_shot_calibration.py',
              'scripts/research_conditional_tail_delivery.py', 'docs/analysis/sci_md_mass_delivery_008/HANDOFF.json']
    bases = read(DOC/'BASES.json')['repositories']
    write(out/'freeze.json', {'task': TASK, 'primary': 'A2', 'arms': list(ARMS),
        'producer_commit': git(ROOT, 'rev-parse', 'HEAD'), 'producer_tree': git(ROOT, 'rev-parse', 'HEAD^{tree}'),
        'producer_base': bases['puckworks']['base'], 'consumer_base': bases['espresso-whole-pull']['base'],
        'consumer_commit': git(consumer, 'rev-parse', 'HEAD'), 'consumer_tree': git(consumer, 'rev-parse', 'HEAD^{tree}'),
        'code_and_protocol': {p: digest(ROOT/p) for p in sorted(bound)},
        'consumer_files': {p: digest(consumer/p) for p in cfiles},
        'artifacts': {p.name: digest(p) for p in out.glob('*.json')},
        'scoring_policy': 'ONE_FRESH_INDEPENDENT_APPROVAL_ONE_OUTCOME_JOIN_NO_RETUNING'})
    return 'READY_FOR_INDEPENDENT_REVIEW'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'calibrate', 'predict', 'freeze', 'score', 'report'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source-root', type=Path); parser.add_argument('--prior', type=Path)
    parser.add_argument('--consumer', type=Path); parser.add_argument('--review', type=Path)
    a = parser.parse_args()
    if a.operation == 'prepare':
        prepare(a.source_root, a.prior, a.out)
    elif a.operation == 'calibrate':
        calibrate(a.out)
    elif a.operation == 'predict':
        predict(a.out)
    elif a.operation == 'freeze':
        print(freeze(a.out, a.consumer))
    else:
        from . import grudeva_one_shot_scoring as scoring
        if a.operation == 'score':
            scoring.score(a.out, a.review, a.consumer)
        else:
            print(md.canonical(scoring.report(a.out)))


if __name__ == '__main__':
    main()

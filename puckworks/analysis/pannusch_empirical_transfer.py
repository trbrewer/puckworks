"""Frozen single-anchor empirical transfer; source rows and states remain private.

The new FIT cohort is explicit. Historical adapters and fitted curves are reused
without relaxing their guards. Only score() attaches later outcome chemistry.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from dataclasses import asdict
import json
from pathlib import Path
import platform
import subprocess
from unittest.mock import patch

import numpy as np
import scipy

from . import anchored_mass_delivery as md
from . import pannusch_mass_delivery as source
from . import pannusch_conditioned_mass_delivery as receipt
from tools.pannusch2024_reconstruct import doe_conditions, shot_dates

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/sci_md_mass_delivery_004'
TASK = 'SCI-MD-MASS-DELIVERY-004'
CAMPAIGN = 'FIT_2021_12'
GRINDS = {1: 1.4, 2: 1.4, 3: 2., 4: 2., 5: 1.4, 6: 1.4,
          7: 2., 8: 2., 12: 1.4, 13: 2.}
RECIPES = {1: (80., 1.), 2: (98., 1.), 3: (80., 1.), 4: (98., 1.),
           5: (80., 3.), 6: (98., 3.), 7: (80., 3.), 8: (98., 3.),
           12: (89., 2.), 13: (89., 2.)}
CONDITIONS = tuple(f'FIT-C{i:02d}' for i in GRINDS)
SHOTS = tuple(f'FIT-E{i:02d}-R{r}' for i in GRINDS for r in (1, 2, 3))
CALIBRATION = tuple(f'FIT-E{i:02d}-R{r}' for i in source.FIT for r in (1, 2, 3))
SUFFIX = (2, 3, 5, 7, 10)
ARMS = ('ANCHORED_EMPIRICAL', 'UNANCHORED_EMPIRICAL', 'ANCHORED_MASS',
        'UNANCHORED_MASS', 'ANCHOR_PERSISTENCE')
PRIMARY = ARMS[0]
GROUPS = {'all_ten': CONDITIONS,
          'grind_1.4': tuple(f'FIT-C{i:02d}' for i, g in GRINDS.items() if g == 1.4),
          'grind_2.0': tuple(f'FIT-C{i:02d}' for i, g in GRINDS.items() if g == 2.),
          'common_89C_code2': ('FIT-C12', 'FIT-C13'),
          'corners': CONDITIONS[:8]}
BASE_PATHS = {'MASS': 'docs/analysis/sci_md_mass_delivery_001/models/MASS.json',
              'EMPIRICAL': 'docs/analysis/sci_md_mass_delivery_001/models/BOUNDARY_AWARE_EMPIRICAL.json'}
QUERY_KEYS = ('campaign', 'condition', 'shot', 'fraction', 'b0', 'b1', 'coordinate_status')
BUNDLE_FILES = ('information_contract.json', 'coordinates.json', 'queries.json',
                'coordinate_coverage.json', 'anchors.json', 'anchor_support.json',
                'states.json', 'predictions.json', 'source.json', 'execution.json')
FREEZE_PATHS = tuple('puckworks/analysis/'+n+'.py' for n in (
    'mass_delivery', 'conditioned_mass_delivery', 'anchored_mass_delivery',
    'pannusch_mass_delivery', 'pannusch_conditioned_mass_delivery', 'pannusch_empirical_transfer')) + (
    'tools/pannusch2024_reconstruct.py', 'tools/data_availability_preflight.py',
    'tests/test_pannusch_empirical_transfer.py') + tuple(
    'docs/analysis/sci_md_mass_delivery_004/'+n for n in (
        'PROTOCOL.md', 'QUALIFICATION_CARD.md', 'BASES.json',
        'INFORMATION_CONTRACT.json', 'DATA_AVAILABILITY_PREFLIGHT.json')) + tuple(BASE_PATHS.values())
write_json, digest, canonical_hash = source.write_json, source.digest, source.canonical_hash


def read(path):
    return md.strict_json(Path(path).read_text())


def git(expression):
    return subprocess.check_output(['git', 'rev-parse', expression], cwd=ROOT, text=True).strip()


def role(shot, fraction):
    if shot in CALIBRATION:
        return 'FROZEN_CALIBRATION_EXCLUDED'
    if shot in SHOTS:
        return 'ANCHOR_INPUT_ONLY' if fraction == 1 else 'SCORING_ONLY' if fraction in SUFFIX else 'COORDINATE_PREFIX_ONLY'
    return 'EXCLUDED'


def load_bases():
    contract = read(DOC/'BASES.json')
    for p, expected in contract['reused_files'].items():
        if digest(ROOT/p) != expected:
            raise ValueError('FROZEN_PREDECESSOR_BYTES_CHANGED')
    bases = {name: md.FrozenBase.load(ROOT/path) for name, path in BASE_PATHS.items()}
    for base in bases.values():
        fit = read_model(base)['fit_identity']
        if (set(fit['shots']) != set(CALIBRATION) or set(fit['shots']) & set(SHOTS)
                or fit['campaign'] != CAMPAIGN or fit['grind'] != 1.7):
            raise ValueError('CALIBRATION_IDENTITY_OR_DISJOINTNESS_FAILURE')
    return bases


def read_model(base):
    return md.strict_json(base.artifact_json)


def information_contract():
    contract = read(DOC/'INFORMATION_CONTRACT.json')
    if (contract['task'] != TASK or contract['conditions'] != list(CONDITIONS)
            or contract['shots'] != list(SHOTS) or contract['arms'] != list(ARMS)
            or contract['primary'] != PRIMARY or contract['outcome_fraction_ids'] != list(SUFFIX)
            or contract['status'] != 'FROZEN_BEFORE_ANCHOR_EXTRACTION'):
        raise ValueError('INFORMATION_CONTRACT_MISMATCH')
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', contract['contract_commit'], 'HEAD'], cwd=ROOT)
    for p, sha in contract['files'].items():
        content = subprocess.check_output(['git', 'show', contract['contract_commit']+':'+p], cwd=ROOT)
        if digest(ROOT/p) != sha or source.hashlib.sha256(content).hexdigest() != sha:
            raise ValueError('CONTRACT_DRIFT_OR_NOT_COMMITTED')
    return contract


def qualified_register(register, assignments, designs, dates):
    """Identity selection never grants permission to fit SOURCE_FIT_DATA."""
    chosen = [r for r in register if r['campaign_id'] == CAMPAIGN and r['shot_id'] in SHOTS]
    if len(chosen) != len(SHOTS) or {r['shot_id'] for r in chosen} != set(SHOTS):
        raise ValueError('EXACT_SHOT_MATRIX_REQUIRED')
    mapping = {int(r['source_experiment_id']): float(r['grind_setting']) for r in assignments if r['campaign_id'] == CAMPAIGN}
    for r in chosen:
        i, j = int(r['source_experiment_id']), int(r['physical_replicate_id'])
        d = designs[i]
        if (r['shot_id'] != f'FIT-E{i:02d}-R{j}' or j not in (1, 2, 3)
                or r['condition_id'] != f'FIT-C{i:02d}' or i not in GRINDS
                or float(r['grind_setting']) != GRINDS[i] or mapping[i] != GRINDS[i]
                or d['grind'] != GRINDS[i] or d['dose'] != 20 or float(r['dose_g']) != 20
                or (d['temp0'], d['flow0']) != RECIPES[i]
                or d['temp0'] != d['temp1'] or d['flow0'] != d['flow1']
                or r['machine'] != 'DE1' or r['source_id'] != 'P24-MAT-FIT;P24-DOE-FIT'
                or r['nominal_temperature_program_id'] != f'CONST-{d["temp0"]:g}C'
                or r['nominal_flow_program_id'] != f'CONST-{d["flow0"]:g}ML_S'
                or r['collection_date'] != dates[(i, j)]):
            raise ValueError('SOURCE_ASSIGNMENT_OR_RECIPE_JOIN_MISMATCH')
    return sorted(chosen, key=lambda r: r['shot_id'])


def measured_coordinates(path, shot_index, run):
    """Qualify each complete prefix; never use source-imputed gap masses.

    Reuses the source collection reconstruction. A later missing vial cannot
    invalidate a measured earlier window, but every subsequent prefix is unknown.
    The assayed vial's own measured width can remain eligible chemistry support.
    """
    coords = source.mass_coordinates(run)
    sheet = source.workbook(path)['SampleWeights']
    row, col = (2*shot_index+1, 3) if shot_index <= 32 else (2*(shot_index-32)+1, 15)
    if sheet.cell(row, col-2).value != shot_index or len(run.mE) != 10:
        raise ValueError('SOURCE_WORKBOOK_ID_OR_COLLECTION_COUNT_MISMATCH')
    net = []
    for j in range(10):
        empty, full = (sheet.cell(row+k, col+j).value for k in (0, 1))
        mass = full-empty if all(isinstance(v, (int, float)) for v in (empty, full)) else None
        if mass is not None and (not np.isfinite(mass) or mass <= 0 or abs(mass-run.mE[j]) > 1e-10):
            raise ValueError('WORKBOOK_MEASURED_MASS_MISMATCH')
        net.append(mass)
    missing = [j+1 for j, m in enumerate(net) if m is None]
    for c in coords:
        f = c['fraction']
        c['missing_measured_vials'] = missing
        c['mass_kg'] = float(source.mass_to_kg(net[f-1], 'g')) if net[f-1] is not None else None
        c['collection_mass_kg'] = sum(net)*.001 if not missing else None
        c['coordinate_status'] = 'QUALIFIED'
        if any(m is None for m in net[:f]):
            c.update(b0=None, b1=None, t0=None, t1=None,
                     coordinate_status='UNAVAILABLE_MEASURED_MASS_PREFIX')
        elif abs(c['b1']-c['b0']-c['mass_kg']) > 1e-15:
            raise ValueError('MASS_INTERVAL_MISMATCH')
    if coords[0]['coordinate_status'] == 'QUALIFIED' and (coords[0]['b0'] != 0 or coords[0]['t0'] != 0):
        raise ValueError('COLLECTION_ORIGIN_MISMATCH')
    return coords


def source_coordinates(paths):
    designs = {d['exp']: d for d in doe_conditions(paths['P24-DOE-FIT'], 15)}
    dates = shot_dates(paths['P24-DOE-FIT'], 15)
    register = qualified_register(source.rows(source.DATA/'experiment_register.csv'),
        source.rows(source.DATA/'experiment_grind_assignments.csv'), designs, dates)
    objects = source.mat(paths['P24-MAT-FIT'])['ExperimentalData']
    result = []
    for r in register:
        i, j = int(r['source_experiment_id']), int(r['physical_replicate_id'])
        meta = {k: r[k] for k in ('collection_date', 'coffee_product', 'coffee_lot_id', 'roast_batch_id', 'source_role')}
        meta.update(campaign=CAMPAIGN, condition=r['condition_id'], shot=r['shot_id'],
                    source_id='P24-MAT-FIT', source_grind=GRINDS[i],
                    nominal_temperature_C=RECIPES[i][0], source_flow_setting_code=RECIPES[i][1])
        try:
            run = objects[i-1].run[j-1]
            coords = measured_coordinates(paths['P24-DOE-FIT'], 3*(i-1)+j, run)
            result.extend(dict(c, **meta, task_role=role(r['shot_id'], c['fraction'])) for c in coords)
        except (ValueError, IndexError, AttributeError) as exc:
            result.extend(dict(meta, fraction=f, task_role=role(r['shot_id'], f), b0=None, b1=None,
                mass_kg=None, coordinate_status='SOURCE_COORDINATES_UNAVAILABLE:'+str(exc)) for f in (1,)+SUFFIX)
    return result


def assay_projection(rows, coords, fractions):
    """Only requested roles are converted; later chemistry never leaves prepare."""
    if any(c['fraction'] not in fractions for c in coords):
        raise ValueError('ASSAY_ROLE_VIOLATION')
    expected = {(c['shot'], c['fraction']) for c in coords}
    chosen = source.deduplicate([r for r in rows if r['campaign_id'] == CAMPAIGN
        and r['analyte'] == 'TDS' and int(r['fraction_id']) in fractions
        and (r['shot_id'], int(r['fraction_id'])) in expected],
        ('campaign_id', 'shot_id', 'fraction_id', 'analyte'))
    index = {(r['shot_id'], int(r['fraction_id'])): r for r in chosen}
    result = []
    for c in coords:
        r = index.get((c['shot'], c['fraction']))
        q, reason, rounding = None, '', 0.
        if c['mass_kg'] is None:
            reason = 'UNAVAILABLE_MEASURED_ASSAY_MASS'
        elif r is None:
            reason = 'MISSING_TDS_ASSAY'
        else:
            if (r['condition_id'] != c['condition'] or r['source_id'] != c['source_id']
                    or r['shot_id'] != f"FIT-E{int(r['source_experiment_id']):02d}-R{int(r['physical_replicate_id'])}"
                    or r['concentration_unit'] != 'percent' or r['fraction_basis'] != 'MEASURED_MASS_G'):
                raise ValueError('ASSAY_IDENTITY_OR_MASS_BASIS_MISMATCH')
            if abs(float(r['fraction_liquid_g_or_ml'])*.001-c['mass_kg']) > 5.01e-12:
                raise ValueError('ASSAY_MEASURED_MASS_MISMATCH')
            # TDS validity is analyte-specific. Never apply ALL_HPLC_ANALYTES to TDS.
            if r['validity'] != 'VALID':
                reason = 'SOURCE_INVALID_TDS:'+r['exclusion_reason']
            elif r['concentration_value'] == '':
                reason = 'MISSING_TDS_CHEMISTRY'
            else:
                try:
                    q = float(source.concentration_to_fraction(float(r['concentration_value']), 'percent'))
                except ValueError:
                    reason = 'INVALID_TDS_VALUE'
                if q is not None:
                    rounding = c['mass_kg']*5e-11+q*5e-12+5e-15
                    if abs(c['mass_kg']*q-float(r['analyte_mass_mg'])*1e-6) > rounding+1e-17:
                        raise ValueError('SOURCE_SOLUTE_ROUNDING_MISMATCH')
        result.append(dict(c, eligible=q is not None, q=q,
            supplied_tds_percent=float(r['concentration_value']) if q is not None else None,
            solute_kg=c['mass_kg']*q if q is not None else None,
            source_rounding_allowance_kg=rounding, source_reason=reason))
    return result


def extract_anchors(rows, coords):
    anchors, support = {}, []
    for r in assay_projection(rows, [c for c in coords if c['fraction'] == 1], (1,)):
        a = md.AnchorInput(r['shot'], r['source_id'], 1, r['b0'], r['b1'], r['supplied_tds_percent'],
            'MEASURED_MASS_G_CONVERTED_TO_KG', source.RIGHTS, 'MEASURED_SOURCE_ANCHOR_INPUT') if r['eligible'] else None
        anchors[r['shot']] = a
        support.append({'shot': r['shot'], 'available': a is not None, 'reason': r['source_reason'],
                        'source_rounding_allowance_kg': r['source_rounding_allowance_kg']})
    return anchors, support


def project_queries(coords):
    return [{k: c[k] for k in QUERY_KEYS} for c in coords if c['fraction'] in SUFFIX]


def domain_reason(q, bases):
    if q['coordinate_status'] != 'QUALIFIED':
        return q['coordinate_status']
    try:
        interval = md.IntervalQuery(q['b0'], q['b1'])
        if interval.start_kg == interval.end_kg:
            return 'NONPOSITIVE_SOURCE_INTERVAL'
        if any(not b.curve().domain_kg[0] <= q['b0'] <= q['b1'] <= b.curve().domain_kg[1] for b in bases.values()):
            return 'OUTSIDE_FROZEN_MASS_DOMAIN'
    except ValueError as exc:
        return str(exc)
    return ''


@contextmanager
def no_optimization():
    """Execution guard and observable counters, including imported optimizer aliases."""
    calls = {'optimizer_calls': 0, 'new_base_curve_fits': 0}
    def forbidden(*args, **kwargs):
        calls['optimizer_calls'] += 1
        raise RuntimeError('OPTIMIZATION_FORBIDDEN')
    from contextlib import ExitStack
    with ExitStack() as stack:
        for module in (scipy.optimize, source, receipt):
            for name in ('least_squares', 'lsq_linear', 'minimize', 'differential_evolution', 'curve_fit'):
                if hasattr(module, name):
                    stack.enter_context(patch.object(module, name, forbidden))
        yield calls


def predict_bundle(bases, anchors, queries):
    if (set(bases) != set(BASE_PATHS) or any(set(q) != set(QUERY_KEYS) for q in queries)
            or any(q['fraction'] not in SUFFIX or role(q['shot'], q['fraction']) != 'SCORING_ONLY' for q in queries)):
        raise ValueError('COORDINATE_ONLY_DECLARED_SUFFIX_REQUIRED')
    if any(a is not None and (type(a) is not md.AnchorInput or a.shot_id != s) for s, a in anchors.items()):
        raise ValueError('ANCHOR_IDENTITY_MISMATCH')
    predictions, states, failures = {a: [] for a in ARMS}, {}, {}
    # Make each allowed analytical update once, even when later support is missing.
    for name, base in bases.items():
        for shot, a in anchors.items():
            if a is not None:
                try:
                    states[name+'/'+shot] = md.anchor(base, a)
                except (ValueError, FloatingPointError) as exc:
                    failures[name+'/'+shot] = str(exc)
    for q in queries:
        for arm in ARMS:
            p = dict(q, in_domain=False, numerical_qualified=False, predicted_solute_kg=None,
                integration_allowance_kg=0., unsupported_reason='',
                anchor_error_amplification=None, amplification_allowance=None)
            try:
                reason = domain_reason(q, bases)
                if reason:
                    raise ValueError(reason)
                interval = md.IntervalQuery(q['b0'], q['b1'])
                a = anchors.get(q['shot'])
                if arm == 'ANCHOR_PERSISTENCE':
                    if a is None:
                        raise ValueError('ANCHOR_UNAVAILABLE')
                    if interval.start_kg < a.end_kg:
                        raise ValueError('QUERY_BEFORE_ANCHOR_COMPLETION')
                    value = a.tds_percent/100*(q['b1']-q['b0'])
                    error, amp, ae = md.roundoff(value), 1., 0.
                else:
                    name = arm.split('_', 1)[1]
                    if arm.startswith('ANCHORED_'):
                        if a is None:
                            raise ValueError('ANCHOR_UNAVAILABLE')
                        key = name+'/'+q['shot']
                        if key in failures:
                            raise ValueError(failures[key])
                        prediction = states[key].predict_intervals((interval,))[0]
                        value, error = prediction.solute_kg, prediction.numerical_allowance_kg
                        amp, ae = prediction.anchor_error_amplification, prediction.amplification_allowance
                    else:
                        value, error = md.integral(bases[name].curve(), q['b0'], q['b1'])
                        amp, ae = None, None
                p.update(in_domain=True, numerical_qualified=error <= 1e-9,
                    predicted_solute_kg=value, integration_allowance_kg=error,
                    anchor_error_amplification=amp, amplification_allowance=ae,
                    unsupported_reason='' if error <= 1e-9 else 'NUMERICAL_ALLOWANCE_EXCEEDS_BUDGET')
            except (ValueError, FloatingPointError) as exc:
                p['unsupported_reason'] = str(exc)
            predictions[arm].append(p)
    return predictions, {k: v.to_dict() for k, v in states.items()}, failures


def identity_set(records):
    ids = sorted((r['shot'], r['fraction']) for r in records)
    return {'count': len(ids), 'identity_sha256': canonical_hash(ids),
            'known_mass_kg': sum((r['mass_kg'] or 0.) for r in records),
            'unknown_mass_slots': sum(r['mass_kg'] is None for r in records)}


def coverage(observed, predictions):
    eligible = [o for o in observed if o.get('eligible', o['coordinate_status'] == 'QUALIFIED')]
    pairs = [(o, p) for o, p in zip(observed, predictions) if o in eligible]
    supported = [o for o, p in pairs if p['in_domain']]
    qualified = [o for o, p in pairs if p['in_domain'] and p['numerical_qualified']]
    return {name: identity_set(rows) for name, rows in (
        ('intended', observed), ('source_eligible', eligible),
        ('model_supported', supported), ('numerically_qualified', qualified))}


def prepare(out):
    out = Path(out).resolve()
    if out.is_relative_to(ROOT):
        raise ValueError('PRIVATE_EVIDENCE_MUST_REMAIN_OUTSIDE_GIT')
    contract = information_contract()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out/'information_contract.json', contract)
    history = read(ROOT/'docs/analysis/sci_md_mass_delivery_003/SOURCE.json')
    source.verify_registers(history)
    paths = source.source_paths()
    if {k: digest(v) for k, v in paths.items()} != history['source_files']:
        raise ValueError('PREDECESSOR_SOURCE_DRIFT')
    bases = load_bases()
    coords = source_coordinates(paths)
    queries = project_queries(coords)
    if {(c['shot'], c['fraction']) for c in coords} != {(s, f) for s in SHOTS for f in (1,)+SUFFIX} or len(coords) != 180:
        raise ValueError('COMPLETE_COORDINATE_IDENTITY_MATRIX_REQUIRED')
    write_json(out/'coordinates.json', coords)
    write_json(out/'queries.json', queries)
    # Before anchor extraction and before scoring; contains no chemistry.
    coordinate_check = [dict(q, reason=domain_reason(q, bases)) for q in queries]
    write_json(out/'coordinate_coverage.json', coordinate_check)
    anchors, support = extract_anchors(source.rows(source.DATA/'fit_fraction_replicates.csv'), coords)
    with no_optimization() as counters:
        predictions, states, failures = predict_bundle(bases, anchors, queries)
    write_json(out/'anchors.json', {s: asdict(a) if a else None for s, a in anchors.items()})
    write_json(out/'anchor_support.json', support)
    write_json(out/'states.json', states)
    write_json(out/'predictions.json', predictions)
    write_json(out/'source.json', {'task': TASK, 'source_files': history['source_files'],
        'registers': history['registers'], 'rights': source.RIGHTS,
        'intended_shots': len(SHOTS), 'available_anchors': sum(a is not None for a in anchors.values()),
        'intended_later_assays': len(queries), 'calibration_disjoint': True,
        'calibration_identity_sha256': canonical_hash(sorted(CALIBRATION)),
        'evaluation_identity_sha256': canonical_hash(sorted(SHOTS)),
        'metadata_by_condition': {c: {k: sorted({str(r[k]) for r in coords if r['condition'] == c})
            for k in ('collection_date', 'coffee_product', 'coffee_lot_id', 'roast_batch_id',
                      'source_grind', 'nominal_temperature_C', 'source_flow_setting_code')} for c in CONDITIONS},
        'anchor_origin': 'ZERO_SOURCE_COLLECTION_ORIGIN_CHECKED',
        'mass_coordinate_basis': 'MEASURED_g_TIMES_0.001_ALL_TEN_VIALS_CHECKED_GAPS_BLOCK_SUBSEQUENT_PREFIXES',
        'coordinate_unsupported_reason_counts': dict(Counter(q['reason'] for q in coordinate_check if q['reason'])),
        'state_failure_reason_counts': dict(Counter(failures.values())),
        'source_labels': list(md.REAL_LABELS), 'source_FIT_label_grants_fitting_permission': False,
        'later_TDS_passed_to_predictor': False, 'future_mass_windows': 'SUPPLIED_CONDITIONAL_QUERIES'})
    write_json(out/'execution.json', {'task': TASK, **counters, 'native_ewp_runs': 0,
        'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__,
        'analytical_amplitude_update_attempts': 2*sum(a is not None for a in anchors.values()),
        'qualified_anchored_states': len(states), 'prediction_status_records': sum(map(len, predictions.values())),
        'supported_predictions': sum(p['in_domain'] for pp in predictions.values() for p in pp),
        'numerically_qualified_predictions': sum(p['numerical_qualified'] for pp in predictions.values() for p in pp),
        'scoring': 'NOT_EXECUTED'})
    print(json.dumps(read(out/'execution.json'), indent=2))


def freeze(out):
    out = Path(out)
    if any((out/name).exists() for name in ('freeze.json', 'score_receipt.json', 'scores.json')):
        raise ValueError('FROZEN_OR_SCORED_RUN_REFUSES_OVERWRITE')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('COMMIT_IMPLEMENTATION_BEFORE_FREEZE')
    information_contract()
    load_bases()
    write_json(out/'freeze.json', {'task': TASK, 'producer_commit': git('HEAD'), 'producer_tree': git('HEAD^{tree}'),
        'code_and_protocol': {p: digest(ROOT/p) for p in FREEZE_PATHS},
        'artifacts': {p: digest(out/p) for p in BUNDLE_FILES},
        'primary_candidate': PRIMARY, 'arms': list(ARMS), 'conditions': list(CONDITIONS),
        'review_status': 'INDEPENDENT_EXACT_FREEZE_AUDIT_REQUIRED', 'scoring_policy': 'ONE_PASS_NO_RETUNING'})
    print('Freeze SHA256:', digest(out/'freeze.json'))


def verify_before_score(out, review):
    out = Path(out)
    if any((out/name).exists() for name in ('score_receipt.json', 'scores.json', 'score_completion.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    frozen = receipt.verify_before_score(out, review)
    approved = read(review)
    if (frozen['task'] != TASK or approved.get('task') != TASK or not approved.get('reviewer')
            or approved.get('unresolved_blocking_findings') != []):
        raise ValueError('TASK_INDEPENDENT_REVIEW_REQUIRED')
    if (set(frozen['code_and_protocol']) != set(FREEZE_PATHS)
            or set(frozen['artifacts']) != set(BUNDLE_FILES)):
        raise ValueError('INCOMPLETE_FREEZE_BINDINGS')
    actual = {k: digest(v) for k, v in source.source_paths().items()}
    if actual != read(out/'source.json')['source_files']:
        raise ValueError('SOURCE_FILE_DRIFT')
    return frozen


def conjunction(values):
    if 'FAIL' in values:
        return 'FAIL'
    if all(v == 'PASS' for v in values):
        return 'PASS'
    return 'NUMERICALLY_UNRESOLVED' if 'NUMERICALLY_UNRESOLVED' in values else 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS'


def compare(conditions, comparator):
    a, b = (source.aggregate(conditions[n], CONDITIONS)['metrics'] for n in (PRIMARY, comparator))
    ai, bi = ({c['condition']: c['metrics'] for c in conditions[n]} for n in (PRIMARY, comparator))
    lower, possible = 0, 0
    for c in CONDITIONS:
        if ai[c] is None or bi[c] is None:
            possible += 1
        else:
            delta = bi[c]['R_pp']-ai[c]['R_pp']
            allowance = ai[c]['R_allowance_pp']+bi[c]['R_allowance_pp']
            lower += delta > allowance
            possible += delta > -allowance
    wins = 'PASS' if lower >= 8 else 'FAIL' if possible < 8 else 'NUMERICALLY_UNRESOLVED'
    if a is None or b is None:
        return {'material_gain': conjunction([wins, 'UNSUPPORTED']), 'competitive_status': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS',
                'conditions_improved_definite': lower, 'conditions_improved_possible': possible,
                'material_gain_gates': {'condition_wins': wins, 'balanced_metrics': 'UNSUPPORTED'}}
    delta, de = b['R_pp']-a['R_pp'], a['R_allowance_pp']+b['R_allowance_pp']
    bias, be = a['abs_B_pp']-b['abs_B_pp'], a['B_allowance_pp']+b['B_allowance_pp']
    gain = {'absolute_reduction': source.threshold(-delta, de, -.1),
            'relative_reduction': source.threshold(a['R_pp']-.8*b['R_pp'], a['R_allowance_pp']+.8*b['R_allowance_pp'], 0.),
            'bias': source.threshold(bias, be, .1), 'condition_wins': wins}
    competitive = [source.threshold(-delta, de, .1), source.threshold(bias, be, .1)]
    return {'material_gain': conjunction(list(gain.values())), 'material_gain_gates': gain,
            'competitive_status': conjunction(competitive), 'competitive_gates': competitive,
            'R_reduction_pp': delta, 'R_reduction_allowance_pp': de,
            'relative_R_reduction': delta/b['R_pp'] if b['R_pp'] else None,
            'abs_B_deterioration_pp': bias, 'abs_B_delta_allowance_pp': be,
            'conditions_improved_definite': lower, 'conditions_improved_possible': possible}


def shot_metrics(observed, predictions):
    result = []
    for shot in SHOTS:
        pairs = [(o, p) for o, p in zip(observed, predictions) if o['shot'] == shot]
        use = [(o, p) for o, p in pairs if o['eligible'] and p['in_domain'] and p['numerical_qualified']]
        metric = None
        if use:
            mass = np.array([o['mass_kg'] for o, _ in use])
            error = np.array([100*(p['predicted_solute_kg']-o['solute_kg'])/o['mass_kg'] for o, p in use])
            allowance = np.array([100*p['integration_allowance_kg']/o['mass_kg'] for o, p in use])
            bias = float(sum(mass*error)/sum(mass))
            metric = {'R_pp': float(np.sqrt(sum(mass*error**2)/sum(mass))), 'B_pp': bias, 'abs_B_pp': abs(bias),
                      'R_allowance_pp': float(np.sqrt(sum(mass*allowance**2)/sum(mass))),
                      'B_allowance_pp': float(sum(mass*allowance)/sum(mass))}
        complete = len(use) == len(SUFFIX)
        result.append({'shot': shot, 'condition': pairs[0][0]['condition'], 'full_support': complete,
            'numerically_qualified': all(p['numerical_qualified'] for o, p in pairs if o['eligible']),
            'metrics': metric if complete else None, 'supported_only_diagnostic': metric if not complete else None,
            'coverage': coverage([o for o, _ in pairs], [p for _, p in pairs])})
    return result


def summarize_group(conditions, shots, observed, predictions, selected):
    aggregate = source.aggregate(conditions, selected)
    pairs = [(o, p) for o, p in zip(observed, predictions) if o['condition'] in selected]
    aggregate['coverage'] = coverage([o for o, _ in pairs], [p for _, p in pairs])
    subset = [s for s in shots if s['condition'] in selected and (s['metrics'] or s['supported_only_diagnostic'])]
    by_condition = []
    for c in selected:
        ms = [(s['metrics'] or s['supported_only_diagnostic']) for s in subset if s['condition'] == c]
        if ms:
            by_condition.append({k: float(np.mean([m[k] for m in ms])) for k in ms[0]})
    aggregate['supported_subset_diagnostic'] = {
        'label': 'SUPPORTED_SUBSET_ONLY_NO_ALL_COHORT_ADEQUACY', 'shots': len(subset), 'conditions': len(by_condition),
        'metrics': {k: float(np.mean([m[k] for m in by_condition])) for k in by_condition[0]} if by_condition else None}
    return aggregate


def evaluate(observed, predictions):
    expected = {(s, f) for s in SHOTS for f in SUFFIX}
    if (len(observed) != 150 or {(o['shot'], o['fraction']) for o in observed} != expected
            or any(o['campaign'] != CAMPAIGN or o['condition'] != o['shot'].split('-R')[0].replace('-E', '-C') for o in observed)
            or set(predictions) != set(ARMS)):
        raise ValueError('SCORER_REQUIRES_EXACT_SUFFIX_NO_ANCHOR')
    for arm in ARMS:
        if len(predictions[arm]) != len(observed) or any(any(o[k] != p[k] for k in QUERY_KEYS) for o, p in zip(observed, predictions[arm])):
            raise ValueError('IDENTICAL_FROZEN_SUFFIX_REQUIRED')
    shots = {a: shot_metrics(observed, predictions[a]) for a in ARMS}
    conditions = {a: source.condition_metrics(shots[a]) for a in ARMS}
    groups = {group: {a: summarize_group(conditions[a], shots[a], observed, predictions[a], selected) for a in ARMS}
              for group, selected in GROUPS.items()}
    for a in ARMS:
        for c in conditions[a]:
            c['coverage'] = summarize_group(conditions[a], shots[a], observed, predictions[a], [c['condition']])['coverage']
    comparisons = {a: compare(conditions, a) for a in ('UNANCHORED_EMPIRICAL', 'ANCHOR_PERSISTENCE', 'ANCHORED_MASS')}
    axes = {'A': groups['all_ten'][PRIMARY]['adequacy_status'],
            'B': comparisons['UNANCHORED_EMPIRICAL']['material_gain'],
            'C': comparisons['ANCHOR_PERSISTENCE']['material_gain'],
            'D': conjunction([groups['all_ten'][PRIMARY]['adequacy_status'], comparisons['ANCHORED_MASS']['competitive_status']]),
            'E': comparisons['ANCHORED_MASS']['material_gain']}
    disposition = ('RESTRICTED_ANCHORED_EMPIRICAL_TRANSFER_SUPPORTED' if all(axes[a] == 'PASS' for a in 'ABCD')
        else 'FROZEN_EMPIRICAL_TRANSFER_INADEQUATE' if axes['A'] == 'FAIL'
        else 'TRANSFER_CLAIM_LIMITED_BY_SUPPORT_OR_NUMERICS' if axes['A'] != 'PASS'
        else 'ADEQUATE_WITHOUT_ALL_INCREMENTAL_VALUE_CRITERIA')
    diagnostics = {}
    for a in ARMS:
        pairs = [(o, p) for o, p in zip(observed, predictions[a]) if o['eligible'] and p['in_domain'] and p['numerical_qualified']]
        horizons = {}
        for f in SUFFIX:
            per_condition = []
            for c in CONDITIONS:
                pp = [(o, p) for o, p in pairs if o['fraction'] == f and o['condition'] == c]
                errors = [100*(p['predicted_solute_kg']-o['solute_kg'])/o['mass_kg'] for o, p in pp]
                per_condition.append({'condition': c, 'intended_shots': 3, 'qualified_shots': len(pp),
                    'mean_absolute_error_pp': float(np.mean(np.abs(errors))) if errors else None,
                    'signed_error_pp': float(np.mean(errors)) if errors else None,
                    'numerical_allowance_pp': float(np.mean([100*p['integration_allowance_kg']/o['mass_kg'] for o, p in pp])) if pp else None,
                    'mean_start_kg': float(np.mean([o['b0'] for o, _ in pp])) if pp else None,
                    'mean_end_kg': float(np.mean([o['b1'] for o, _ in pp])) if pp else None})
            good = [c for c in per_condition if c['qualified_shots']]
            horizons[str(f)] = {'conditions': per_condition, 'intended_slots': 30,
                'qualified_slots': sum(c['qualified_shots'] for c in good),
                'scope': 'COMPLETE' if sum(c['qualified_shots'] for c in good) == 30 else 'SUPPORTED_SUBSET_ONLY',
                'balanced_MAE_pp': float(np.mean([c['mean_absolute_error_pp'] for c in good])) if good else None}
        rr = [(s['metrics'] or s['supported_only_diagnostic']) for s in shots[a] if s['metrics'] or s['supported_only_diagnostic']]
        diagnostics[a] = {'horizons': horizons,
            'maximum_complete_shot_R_pp': max((s['metrics']['R_pp'] for s in shots[a] if s['metrics']), default=None),
            'maximum_supported_subset_shot_R_pp': max((r['R_pp'] for r in rr), default=None),
            'assayed_suffix_solute': {'observed_kg': sum(o['solute_kg'] for o, _ in pairs),
                'predicted_kg': sum(p['predicted_solute_kg'] for _, p in pairs),
                'numerical_allowance_kg': sum(p['integration_allowance_kg'] for _, p in pairs),
                'source_rounding_allowance_kg': sum(o['source_rounding_allowance_kg'] for o, _ in pairs),
                'qualified_slots': len(pairs), 'intended_slots': 150, 'whole_cup_measurement': False},
            'source_ineligible_reason_counts': dict(Counter(o['source_reason'] for o in observed if o['source_reason'])),
            'unsupported_reason_counts': dict(Counter(p['unsupported_reason'] for p in predictions[a] if p['unsupported_reason']))}
    return {'task': TASK, 'primary_candidate': PRIMARY, 'axes': axes, 'disposition': disposition,
            'conditions': conditions, 'groups': groups, 'comparisons': comparisons, 'diagnostics': diagnostics,
            'rights': source.RIGHTS, 'source_labels': list(md.REAL_LABELS), 'score_passes': 1,
            'physical_validation': 'NOT_ESTABLISHED'}, shots


def numerical_summary(predictions, states):
    def summary(values):
        return {'count': len(values), 'min': min(values) if values else None,
                'max': max(values) if values else None, 'mean': float(np.mean(values)) if values else None}
    return {'maximum_solute_allowance_kg': max(p['integration_allowance_kg'] for pp in predictions.values() for p in pp),
        'maximum_anchor_relative_allowance': max((s['anchor_integral_allowance_kg']/s['anchor_integral_kg'] for s in states.values()), default=None),
        'amplitudes': {name: summary([s['alpha'] for k, s in states.items() if k.startswith(name+'/')]) for name in BASE_PATHS},
        'error_amplification': {a: {str(f): summary([p['anchor_error_amplification'] for p in predictions[a]
            if p['fraction'] == f and p['anchor_error_amplification'] is not None]) for f in SUFFIX}
            for a in ('ANCHORED_EMPIRICAL', 'ANCHORED_MASS', 'ANCHOR_PERSISTENCE')},
        'interpretation': 'Numerical allowance and analytical amplification; not experimental confidence intervals'}


def score(out, review):
    out = Path(out)
    verify_before_score(out, review)
    write_json(out/'score_receipt.json', {'task': TASK, 'status': 'STARTED',
        'freeze_sha256': digest(out/'freeze.json'), 'review_sha256': digest(review),
        'predictions_sha256': digest(out/'predictions.json')})
    coords = source_coordinates(source.source_paths())
    if canonical_hash(coords) != canonical_hash(read(out/'coordinates.json')):
        raise ValueError('SOURCE_COORDINATE_DRIFT')
    observed = assay_projection(source.rows(source.DATA/'fit_fraction_replicates.csv'),
        [c for c in coords if c['fraction'] in SUFFIX], SUFFIX)
    predictions = read(out/'predictions.json')
    with no_optimization():
        result, shots = evaluate(observed, predictions)
    result['numerics'] = numerical_summary(predictions, read(out/'states.json'))
    write_json(out/'observed_suffix.json', observed)
    write_json(out/'shot_results.json', shots)
    write_json(out/'scores.json', result)
    write_json(out/'score_completion.json', {'task': TASK, 'status': 'COMPLETE',
        'scores_sha256': digest(out/'scores.json'), 'shot_results_sha256': digest(out/'shot_results.json'),
        'score_receipt_sha256': digest(out/'score_receipt.json')})
    print(json.dumps({'axes': result['axes'], 'disposition': result['disposition']}, indent=2))


def report(out):
    """Read-only aggregate reporting: never attaches chemistry or repeats scoring."""
    out = Path(out)
    if not (out/'score_completion.json').exists():
        value = {'task': TASK, 'status': 'FROZEN_PREPARATION_COMPLETE_SCORING_NOT_EXECUTED' if (out/'freeze.json').exists() else 'PREPARATION_NOT_FROZEN',
                 'source': read(out/'source.json'), 'execution': read(out/'execution.json')}
    else:
        completion = read(out/'score_completion.json')
        if digest(out/'scores.json') != completion['scores_sha256']:
            raise ValueError('RESULT_DRIFT')
        value = read(out/'scores.json')
    print(json.dumps(value, indent=2, sort_keys=True, allow_nan=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'freeze', 'score', 'report'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    if args.out.resolve().is_relative_to(ROOT):
        parser.error('Private evidence must remain outside Git')
    if args.operation == 'score':
        if args.review is None:
            parser.error('--review required')
        score(args.out, args.review)
    else:
        {'prepare': prepare, 'freeze': freeze, 'report': report}[args.operation](args.out)


if __name__ == '__main__':
    main()

"""Task-specific private preparation/freeze/once-only scoring for delivery 005.

Only score() attaches future chemistry. Reuses merged source reconstruction,
without invoking historical campaigns or altering their artifacts.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager, ExitStack
from dataclasses import asdict
import json
from pathlib import Path
import platform
import subprocess
import sys
from unittest.mock import patch

import numpy as np
import scipy

from . import two_assay_mass_delivery as md
from . import pannusch_mass_delivery as source
from . import pannusch_conditioned_mass_delivery as settings
from . import pannusch_anchored_mass_delivery as pred_source
from . import pannusch_empirical_transfer as fit_source

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_mass_delivery_005'
TASK = 'SCI-MD-MASS-DELIVERY-005'
ARMS = md.ARMS
PRIMARY = ARMS[0]
SUFFIX = (3, 5, 7, 10)
PANELS = {'PRED': source.PRIMARY, 'FIT-transfer': fit_source.CONDITIONS}
SHOTS = pred_source.SHOTS+fit_source.SHOTS
BASE_PATHS = fit_source.BASE_PATHS
QUERY_KEYS = ('campaign', 'condition', 'shot', 'fraction', 'b0', 'b1',
              'mass_kg', 'coordinate_status', 'tds_validity', 'primary_mask', 'support_reason')
DOC_FILES = ('MODEL_CARD.md', 'PROTOCOL.md', 'BASES.json', 'SUPPORT.json',
             'DATA_AVAILABILITY_PREFLIGHT.json', 'SOURCE_IDENTITIES.json', 'INFORMATION_CONTRACT.json')
FREEZE_PATHS = tuple('puckworks/analysis/'+n+'.py' for n in (
    'mass_delivery', 'conditioned_mass_delivery', 'anchored_mass_delivery',
    'two_assay_mass_delivery', 'pannusch_mass_delivery', 'pannusch_conditioned_mass_delivery',
    'pannusch_anchored_mass_delivery', 'pannusch_empirical_transfer',
    'pannusch_two_assay_mass_delivery')) + (
    'tools/pannusch2024_reconstruct.py', 'tools/data_availability_preflight.py',
    'tests/test_two_assay_mass_delivery.py', 'tests/test_pannusch_two_assay_mass_delivery.py') + tuple(
    'docs/analysis/sci_md_mass_delivery_005/'+n for n in DOC_FILES) + tuple(BASE_PATHS.values())
BUNDLE_FILES = ('information_contract.json', 'coordinates.json', 'support.json', 'observations.json',
                'conditioning_support.json', 'states.json', 'failures.json', 'predictions.json',
                'source.json', 'execution.json')
read, git = fit_source.read, fit_source.git
write_json, digest, canonical_hash = source.write_json, source.digest, source.canonical_hash


def information_contract():
    contract = read(DOC/'INFORMATION_CONTRACT.json')
    if (contract['task'] != TASK or contract['arms'] != list(ARMS)
            or contract['conditioning_fractions'] != [1, 2]
            or contract['outcome_fractions'] != list(SUFFIX)
            or contract['shots'] != list(SHOTS)):
        raise ValueError('INFORMATION_CONTRACT_MISMATCH')
    subprocess.check_call(['git', 'merge-base', '--is-ancestor', contract['contract_commit'], 'HEAD'], cwd=ROOT)
    for path, sha in contract['files'].items():
        content = subprocess.check_output(['git', 'show', contract['contract_commit']+':'+path], cwd=ROOT)
        if digest(ROOT/path) != sha or source.hashlib.sha256(content).hexdigest() != sha:
            raise ValueError('CONTRACT_DRIFT_OR_NOT_COMMITTED_BEFORE_CONDITIONING')
    return contract


def load_bases():
    contract = read(DOC/'BASES.json')
    for p, sha in contract['reused_files'].items():
        if digest(ROOT/p) != sha:
            raise ValueError('FROZEN_PREDECESSOR_BYTES_CHANGED')
    bases = {n: md.FrozenBase.load(ROOT/p) for n, p in BASE_PATHS.items()}
    if any(set(b.curve().fit_identity['shots']) != set(fit_source.CALIBRATION)
           or set(b.curve().fit_identity['shots']) & set(SHOTS) for b in bases.values()):
        raise ValueError('CALIBRATION_IDENTITY_MISMATCH')
    if any(list(b.curve().domain_kg) != read(DOC/'SUPPORT.json')['domain_kg'] for b in bases.values()):
        raise ValueError('FROZEN_DOMAIN_MISMATCH')
    return bases


def qualified_sources():
    history = read(DOC/'SOURCE_IDENTITIES.json')
    source.verify_registers(history)
    paths = source.source_paths()
    if {k: digest(v) for k, v in paths.items()} != history['source_files']:
        raise ValueError('SOURCE_FILE_DRIFT')
    return paths, history


def coordinates(paths):
    designs, _ = settings.qualify_settings(paths)
    coords = pred_source.source_coordinates(paths, designs)+fit_source.source_coordinates(paths)
    for r in coords:
        r.setdefault('coordinate_status', 'QUALIFIED')
        r['task_role'] = 'CONDITIONING_INPUT_ONLY' if r['fraction'] in (1, 2) else 'SCORER_OUTCOME_ONLY'
        if r['shot'].startswith('PRED'):
            r['source_grind'] = 1.7
            r['nominal_temperature_C'] = r['temperature_K']-273.15
    if len(coords) != 252 or {(r['shot'], r['fraction']) for r in coords} != {(s, f) for s in SHOTS for f in (1, 2)+SUFFIX}:
        raise ValueError('EXACT_PHYSICAL_IDENTITY_MATRIX_REQUIRED')
    return coords


def assay_rows():
    return (source.rows(source.DATA/'fit_fraction_replicates.csv')
            + source.rows(source.DATA/'prediction_fraction_replicates.csv'))


def support_mask(coords, rows, domain):
    """Projection reads identity/validity only, NEVER a chemistry field."""
    selected = source.deduplicate([{'shot': r['shot_id'], 'fraction': int(r['fraction_id']),
        'validity': r['validity']} for r in rows if r['analyte'] == 'TDS'], ('shot', 'fraction'))
    flags = {(r['shot'], r['fraction']): r['validity'] for r in selected}
    result = []
    for r in coords:
        if r['fraction'] not in SUFFIX:
            continue
        reason = r['coordinate_status'] if r['coordinate_status'] != 'QUALIFIED' else (
            'OUTSIDE_FROZEN_MASS_DOMAIN' if not domain[0] <= r['b0'] < r['b1'] <= domain[1]
            else ('' if flags.get((r['shot'], r['fraction'])) == 'VALID' else 'INVALID_OR_MISSING_TDS_FLAG'))
        result.append({k: r[k] for k in QUERY_KEYS[:8]} | {
            'tds_validity': flags.get((r['shot'], r['fraction'])),
            'primary_mask': not reason, 'support_reason': reason})
    return result


def project_assays(rows, coords, fractions):
    """Only explicit selected assay roles are passed to predecessor projections."""
    selected = [r for r in coords if r['fraction'] in fractions]
    pred = [r for r in selected if r['shot'].startswith('PRED')]
    fit = [r for r in selected if r['shot'].startswith('FIT')]
    # Filtering precedes either chemistry-bearing projection.
    chosen = [r for r in rows if r['shot_id'] in SHOTS and int(r['fraction_id']) in fractions]
    result = (pred_source.selected_assays(chosen, pred, fractions)
              + fit_source.assay_projection(chosen, fit, fractions))
    if len(result) != len(selected):
        raise ValueError('ASSAY_PROJECTION_IDENTITY_MISMATCH')
    return result


def extract_pairs(rows, coords):
    inputs = project_assays(rows, coords, (1, 2))
    pairs, statuses = {}, []
    for shot in SHOTS:
        entries = sorted([r for r in inputs if r['shot'] == shot], key=lambda r: r['fraction'])
        pair, reason = None, ''
        try:
            if len(entries) != 2 or any(not r['eligible'] or r['coordinate_status'] != 'QUALIFIED' for r in entries):
                raise ValueError('MISSING_OR_INVALID_CONDITIONING_INPUT')
            pair = md.ObservationPair(*(md.Observation(r['shot'], r['source_id'], r['fraction'],
                r['b0'], r['b1'], r['supplied_tds_percent'], 'MEASURED_MASS_G_CONVERTED_TO_KG',
                source.RIGHTS, 'MEASURED_SOURCE_TWO_ASSAY_INPUT') for r in entries))
        except ValueError as exc:
            reason = str(exc)
        pairs[shot] = pair
        statuses.append({'shot': shot, 'available': pair is not None, 'reason': reason,
            'source_rounding_allowance_kg': sum(r['source_rounding_allowance_kg'] for r in entries)})
    return pairs, statuses


@contextmanager
def numerical_counts():
    """Task-local observable counts, not another estimation or fitting stage."""
    counts = Counter()
    def wrap(fn, key):
        def counted(*args, **kwargs):
            counts[key] += 1
            return fn(*args, **kwargs)
        return counted
    original = md.shape_average
    def average(*args, **kwargs):
        method = args[4] if len(args) > 4 else kwargs.get('method', 128)
        counts['shape_average_'+str(method)+'_calls'] += 1
        if method == 'reference' and args[3] == 1.:
            counts['analytic_exponential_reference_calls'] += 1
        return original(*args, **kwargs)
    with ExitStack() as stack:
        stack.enter_context(patch.object(md, 'shape_average', average))
        for module, name, key in ((md, 'quad', 'adaptive_quadrature_calls'),
            (md.kernel, 'quad', 'legacy_adaptive_quadrature_calls'),
            (md, 'shape_derivative', 'moment_refinement_256_calls'),
            (md.legacy, 'integral', 'legacy_integral_refinement_and_reference_calls')):
            stack.enter_context(patch.object(module, name, wrap(getattr(module, name), key)))
        yield counts


def predict_bundle(bases, pairs, queries):
    if set(bases) != set(BASE_PATHS) or set(pairs) != set(SHOTS):
        raise ValueError('EXACT_BASE_AND_SHOT_MATRIX_REQUIRED')
    if any(set(q) != set(QUERY_KEYS) or q['fraction'] not in SUFFIX for q in queries):
        raise ValueError('COORDINATE_ONLY_FUTURE_QUERY_REQUIRED')
    if len(queries) != 168 or {(q['shot'], q['fraction']) for q in queries} != {(s, f) for s in SHOTS for f in SUFFIX}:
        raise ValueError('EXACT_FUTURE_MATRIX_REQUIRED')
    if any(p is not None and (type(p) is not md.ObservationPair or p.first.shot_id != s) for s, p in pairs.items()):
        raise ValueError('PAIR_SHOT_IDENTITY_MISMATCH')
    states, failures, attempts = {}, {}, []
    counters = {'two_parameter_update_attempts': 0, 'analytical_amplitude_update_attempts': 0,
                'primary_scalar_solves': 0, 'qualification_scalar_solves': 0, 'scalar_function_calls': 0}
    for arm in ARMS:
        b = bases['MASS' if arm in ARMS[:3] else 'EMPIRICAL']
        for shot, pair in pairs.items():
            key = arm+'/'+shot
            if pair is None:
                failures[key] = {'status': 'MISSING_OR_INVALID_CONDITIONING_INPUT', 'attempts': []}
                continue
            counters['two_parameter_update_attempts' if arm in ARMS[:2] else 'analytical_amplitude_update_attempts'] += 1
            try:
                states[key] = md.FittedState(b, pair, arm)
                trace = states[key].diagnostics['attempts']
            except (ValueError, FloatingPointError) as exc:
                trace = list(exc.attempts) if isinstance(exc, md.FitFailure) else []
                failures[key] = {'status': str(exc), 'attempts': trace}
            for t in trace:
                counters['primary_scalar_solves' if t['method'] == '128' else 'qualification_scalar_solves'] += 1
                counters['scalar_function_calls'] += t['function_calls']
            attempts.append({'state': key, 'attempts': trace})
    predictions = {arm: [] for arm in ARMS}
    for arm in ARMS:
        for q in queries:
            record = dict(q, predicted_solute_kg=None, predicted_tds_percent=None,
                numerical_allowance_kg=None, numerical_qualified=False,
                tds_sensitivity_pp_per_pp=None, sensitivity_status=None, prediction_status='')
            key = arm+'/'+q['shot']
            try:
                if not q['primary_mask']:
                    raise ValueError(q['support_reason'])
                if key in failures:
                    raise ValueError(failures[key]['status'])
                p = states[key].predict_intervals((md.IntervalQuery(q['b0'], q['b1']),))[0]
                record.update(predicted_solute_kg=p.solute_kg, predicted_tds_percent=p.tds_percent,
                    numerical_allowance_kg=p.numerical_allowance_kg, numerical_qualified=True,
                    tds_sensitivity_pp_per_pp=p.tds_sensitivity_pp_per_pp,
                    sensitivity_status=p.sensitivity_status, prediction_status='QUALIFIED')
            except (ValueError, FloatingPointError) as exc:
                record['prediction_status'] = str(exc)
            predictions[arm].append(record)
    return predictions, {k: v.to_dict() for k, v in states.items()}, failures, counters


def prepare(out):
    out = Path(out).resolve()
    if out.is_relative_to(ROOT):
        raise ValueError('REAL_EVIDENCE_MUST_REMAIN_OUTSIDE_GIT')
    contract = information_contract()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out/'information_contract.json', contract)
    paths, history = qualified_sources()
    bases = load_bases()
    coords = coordinates(paths)
    rows = assay_rows()
    mask = support_mask(coords, rows, bases['MASS'].curve().domain_kg)
    write_json(out/'support.json', mask)
    if digest(out/'support.json') != read(DOC/'SUPPORT.json')['exact_private_support_sha256']:
        raise ValueError('PRECONDITIONING_FROZEN_SUPPORT_MISMATCH')
    write_json(out/'coordinates.json', coords)
    pairs, conditioning = extract_pairs(rows, coords)
    # No chemistry-bearing source rows cross this boundary.
    del rows
    with fit_source.no_optimization() as optimizer_counts, numerical_counts() as numeric_counts:
        predictions, states, failures, counts = predict_bundle(bases, pairs, mask)
    for name, data in [('observations.json', {s: asdict(p) if p else None for s, p in pairs.items()}),
                       ('conditioning_support.json', conditioning), ('states.json', states),
                       ('failures.json', failures), ('predictions.json', predictions)]:
        write_json(out/name, data)
    write_json(out/'source.json', dict(history, task=TASK, rights=source.RIGHTS,
        labels=md.REAL_LABELS, intended_shots=42, intended_conditioning_observations=84,
        available_pairs=sum(p is not None for p in pairs.values()), intended_future_windows=168,
        primary_windows=sum(q['primary_mask'] for q in mask),
        support_reason_counts=dict(Counter(q['support_reason'] for q in mask if not q['primary_mask'])),
        metadata_by_condition={c: {k: sorted({str(r.get(k, 'UNKNOWN')) for r in coords if r['condition'] == c})
            for k in ('collection_date', 'source_design_date', 'coffee_product', 'coffee_lot_id',
                      'roast_batch_id', 'source_grind', 'nominal_temperature_C', 'source_flow_setting_code')}
            for conditions in PANELS.values() for c in conditions},
        later_TDS_passed_to_predictor=False, shared_campaigns_counted_once=True,
        calibration_disjoint=not bool(set(SHOTS) & set(fit_source.CALIBRATION))))
    write_json(out/'execution.json', dict(counts, **optimizer_counts, task=TASK,
        numerical_calls=dict(numeric_counts),
        imported_first_party_modules={str(Path(m.__file__).resolve().relative_to(ROOT)):
            digest(Path(m.__file__).resolve()) for m in tuple(sys.modules.values())
            if getattr(m, '__file__', None) and str(m.__file__).endswith('.py')
            and Path(m.__file__).resolve().is_relative_to(ROOT)},
        global_curve_refits=0, hyperparameter_searches=0, native_ewp_runs=0,
        qualified_states=len(states), state_failure_counts=dict(Counter(f['status'] for f in failures.values())),
        prediction_status_records=sum(map(len, predictions.values())),
        qualified_prediction_records=sum(p['numerical_qualified'] for pp in predictions.values() for p in pp),
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
        scoring='NOT_EXECUTED'))
    print(json.dumps(read(out/'execution.json'), indent=2))


def freeze(out):
    out = Path(out)
    if (out/'freeze.json').exists() or (out/'score_receipt.json').exists():
        raise ValueError('EXISTING_FREEZE_OR_ATTEMPT_REFUSES_OVERWRITE')
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('COMMIT_IMPLEMENTATION_BEFORE_FREEZE')
    information_contract()
    qualified_sources()
    imports = read(out/'execution.json')['imported_first_party_modules']
    if any(digest(ROOT/p) != h for p, h in imports.items()):
        raise ValueError('PREPARATION_RUNTIME_IMPORT_DRIFT')
    write_json(out/'freeze.json', {'task': TASK, 'producer_commit': git('HEAD'), 'producer_tree': git('HEAD^{tree}'),
        'code_and_protocol': {p: digest(ROOT/p) for p in sorted(set(FREEZE_PATHS) | set(imports))},
        'artifacts': {p: digest(out/p) for p in BUNDLE_FILES}, 'primary_candidate': PRIMARY,
        'arms': list(ARMS), 'panels': PANELS, 'scoring_policy': 'ONE_INDEPENDENTLY_AUDITED_PASS_NO_RETUNING'})
    print('Freeze SHA256:', digest(out/'freeze.json'))


def conjunction(values):
    values = list(values)
    if 'FAIL' in values:
        return 'FAIL'
    if all(v == 'PASS' for v in values):
        return 'PASS'
    if any('INCOMPLETE' in v or 'APPLICABILITY' in v for v in values):
        return 'NOT_ADJUDICATED_INCOMPLETE_SUPPORT_OR_APPLICABILITY'
    return 'NUMERICALLY_UNRESOLVED'


def threshold(value, allowance, budget):
    return 'PASS' if value+allowance <= budget else 'FAIL' if value-allowance > budget else 'NUMERICALLY_UNRESOLVED'


def shot_metrics(observed, predictions, restricted):
    result = []
    for shot in SHOTS:
        pairs = [(o, p) for o, p in zip(observed, predictions) if o['shot'] == shot
                 and (o['primary_mask'] or not restricted)]
        use = [(o, p) for o, p in pairs if o['eligible'] and p['numerical_qualified']
               and p['predicted_solute_kg'] is not None]
        complete = bool(pairs) and len(use) == len(pairs)
        metric = None
        if complete:
            m = np.array([o['mass_kg'] for o, _ in use])
            e = np.array([100*(p['predicted_solute_kg']-o['solute_kg'])/o['mass_kg'] for o, p in use])
            de = np.array([100*p['numerical_allowance_kg']/o['mass_kg'] for o, p in use])
            bias = float(np.dot(m, e)/sum(m))
            metric = {'R_pp': float(np.sqrt(np.dot(m, e*e)/sum(m))), 'B_pp': bias, 'abs_B_pp': abs(bias),
                      'R_allowance_pp': float(np.sqrt(np.dot(m, de*de)/sum(m))),
                      'B_allowance_pp': float(np.dot(m, de)/sum(m))}
        result.append({'shot': shot, 'condition': shot.split('-R')[0].replace('-E', '-C'),
            'complete': complete, 'intended_windows': len(pairs), 'qualified_windows': len(use),
            'declared_mass_kg': sum(o['mass_kg'] or 0. for o, _ in pairs), 'metrics': metric,
            'failure_reasons': sorted({p['prediction_status'] for _, p in pairs if not p['numerical_qualified']})})
    return result


def condition_summary(shots, conditions):
    result = []
    for c in conditions:
        ss = [s for s in shots if s['condition'] == c]
        if len(ss) != 3:
            raise ValueError('ORIGINAL_THREE_SHOTS_REQUIRED')
        good = [s['metrics'] for s in ss if s['complete']]
        # Only COMPLETE shot metrics supply full-shot nonnegative lower bounds.
        lower = {key: sum(max(0., m[key]-m[err]) for m in good)/3
                 for key, err in (('R_pp', 'R_allowance_pp'), ('abs_B_pp', 'B_allowance_pp'))}
        metrics = {k: sum(m[k] for m in good)/3 for k in good[0]} if len(good) == 3 else None
        if lower['R_pp'] > 1 or lower['abs_B_pp'] > .5:
            status = 'FAIL'
        elif metrics is not None:
            status = conjunction([threshold(metrics['R_pp'], metrics['R_allowance_pp'], 1.),
                                  threshold(metrics['abs_B_pp'], metrics['B_allowance_pp'], .5)])
        else:
            status = 'NOT_ADJUDICATED_INCOMPLETE_SUPPORT_OR_APPLICABILITY'
        result.append({'condition': c, 'intended_shots': 3, 'complete_shots': len(good),
            'intended_windows': sum(s['intended_windows'] for s in ss),
            'qualified_windows': sum(s['qualified_windows'] for s in ss),
            'metrics': metrics, 'complete_shot_lower_bounds_original_denominator': lower,
            'adequacy_status': status})
    return result


def balanced(conditions):
    ms = [c['metrics'] for c in conditions]
    return {k: float(np.mean([m[k] for m in ms])) for k in ms[0]} if ms and all(m is not None for m in ms) else None


def comparison(candidate, comparator, wins_required):
    a, b = balanced(candidate), balanced(comparator)
    definite, possible = 0, 0
    for ca, cb in zip(candidate, comparator):
        ma, mb = ca['metrics'], cb['metrics']
        if ma is None or mb is None:
            possible += 1
        else:
            delta = mb['R_pp']-ma['R_pp']
            allowance = ma['R_allowance_pp']+mb['R_allowance_pp']
            definite += delta > allowance
            possible += delta > -allowance
    wins = 'PASS' if definite >= wins_required else 'FAIL' if possible < wins_required else (
        'NUMERICALLY_UNRESOLVED' if a is not None and b is not None else 'NOT_ADJUDICATED_INCOMPLETE_SUPPORT')
    result = {'definitely_lower_conditions': definite, 'possibly_lower_conditions': possible,
              'required_condition_wins': wins_required}
    if a is None or b is None:
        return dict(result, material_gain=conjunction([wins, 'NOT_ADJUDICATED_INCOMPLETE_SUPPORT']),
                    competitiveness='NOT_ADJUDICATED_INCOMPLETE_SUPPORT')
    delta, de = b['R_pp']-a['R_pp'], b['R_allowance_pp']+a['R_allowance_pp']
    bias, be = a['abs_B_pp']-b['abs_B_pp'], a['B_allowance_pp']+b['B_allowance_pp']
    gates = {'absolute_gain': threshold(-delta, de, -.1),
             'relative_gain': threshold(a['R_pp']-.8*b['R_pp'], a['R_allowance_pp']+.8*b['R_allowance_pp'], 0.),
             'bias_deterioration': threshold(bias, be, .1), 'condition_wins': wins}
    return dict(result, material_gain=conjunction(gates.values()), material_gates=gates,
        competitiveness=conjunction([threshold(-delta, de, .1), threshold(bias, be, .1)]),
        R_improvement_pp=delta, relative_R_improvement=delta/b['R_pp'] if b['R_pp'] else None,
        abs_B_deterioration_pp=bias, R_comparison_allowance_pp=de, B_comparison_allowance_pp=be)


def assess(observed, predictions, restricted):
    shots = {a: shot_metrics(observed, predictions[a], restricted) for a in ARMS}
    panels = {}
    for panel, names in PANELS.items():
        cond = {a: condition_summary(shots[a], names) for a in ARMS}
        adequate = {a: conjunction(c['adequacy_status'] for c in cond[a]) for a in ARMS}
        wins = 3 if panel == 'PRED' else 8
        cmp = {a: comparison(cond[PRIMARY], cond[a], wins) for a in ARMS[1:5]}
        information = comparison(cond[ARMS[3]], cond[ARMS[5]], wins)
        axes = {'AXIS_A': adequate[PRIMARY], 'AXIS_B': cmp[ARMS[2]]['material_gain'],
                'AXIS_C': conjunction([adequate[PRIMARY]]+[cmp[a]['competitiveness'] for a in (ARMS[1], ARMS[3], ARMS[4])]),
                'AXIS_D': information['material_gain'], 'AXIS_E': cmp[ARMS[1]]['material_gain']}
        panels[panel] = {'conditions': cond, 'balanced_metrics': {a: balanced(cond[a]) for a in ARMS},
                         'adequacy': adequate, 'axes': axes, 'primary_comparisons': cmp,
                         'fixed_empirical_vs_first_empirical': information}
    return {'panels': panels, 'axes': {axis: conjunction(v['axes'][axis] for v in panels.values())
                                     for axis in ('AXIS_A', 'AXIS_B', 'AXIS_C', 'AXIS_D', 'AXIS_E')}}, shots


def diagnostics(observed, predictions, shots):
    result = {}
    for panel, conditions in PANELS.items():
        result[panel] = {}
        for arm in ARMS:
            pairs = [(o, p) for o, p in zip(observed, predictions[arm]) if o['condition'] in conditions]
            use = [(o, p) for o, p in pairs if o['primary_mask'] and o['eligible'] and p['numerical_qualified']]
            horizons = []
            for c in conditions:
                for f in SUFFIX:
                    rows = [(o, p) for o, p in use if o['condition'] == c and o['fraction'] == f]
                    errors = [p['predicted_tds_percent']-100*o['q'] for o, p in rows]
                    horizons.append({'condition': c, 'fraction': f, 'intended_shots': 3, 'qualified_shots': len(rows),
                        'mean_error_pp': float(np.mean(errors)) if errors else None,
                        'mean_absolute_error_pp': float(np.mean(np.abs(errors))) if errors else None,
                        'mean_numerical_allowance_pp': float(np.mean([100*p['numerical_allowance_kg']/o['mass_kg'] for o, p in rows])) if rows else None,
                        'mean_start_kg': float(np.mean([o['b0'] for o, _ in rows])) if rows else None,
                        'mean_end_kg': float(np.mean([o['b1'] for o, _ in rows])) if rows else None})
            ss = [s['metrics'] for s in shots[arm] if s['condition'] in conditions and s['metrics']]
            sensitivities = [v for _, p in use for v in (p['tds_sensitivity_pp_per_pp'] or ())]
            result[panel][arm] = {'fraction_horizon_errors': horizons,
                'worst_complete_primary_shot_R_pp': max((m['R_pp'] for m in ss), default=None),
                'worst_absolute_window_error_pp': max((abs(p['predicted_tds_percent']-100*o['q']) for o, p in use), default=None),
                'observed_solute_on_primary_assayed_support_kg': sum(o['solute_kg'] for o, _ in pairs if o['primary_mask'] and o['eligible']),
                'predicted_solute_on_qualified_primary_assayed_support_kg': sum(p['predicted_solute_kg'] for _, p in use),
                'solute_sum_numerical_allowance_kg': sum(p['numerical_allowance_kg'] for _, p in use),
                'source_rounding_allowance_kg': sum(o['source_rounding_allowance_kg'] for o, _ in pairs if o['primary_mask']),
                'complete_primary_support': len(use) == sum(o['primary_mask'] for o, _ in pairs),
                'sensitivity_range_pp_per_pp': [min(sensitivities), max(sensitivities)] if sensitivities else None,
                'prediction_status_counts': dict(Counter(p['prediction_status'] for _, p in pairs))}
    return result


def parameter_summary(states, failures, predictions):
    def summary(values):
        return {'count': len(values), 'min': min(values) if values else None,
                'max': max(values) if values else None,
                'mean': float(np.mean(values)) if values else None}
    result = {}
    for arm in ARMS:
        rows = [v['diagnostics'] for k, v in states.items() if k.startswith(arm+'/')]
        result[arm] = {'qualified_states': len(rows), 'intended_states': 42,
            'failure_counts': dict(Counter(v['status'] for k, v in failures.items() if k.startswith(arm+'/'))),
            'status_counts': dict(Counter(v['status'] for v in rows)),
            'parameter_ranges': {k: summary([r[k] for r in rows if r.get(k) is not None])
                for k in ('A', 'k', 'lambda', 'alpha', 'jacobian_condition_number', 'denominator_relative_allowance')},
            'by_condition': {c: {'qualified_states': sum(k.startswith(arm+'/'+c.replace('-C', '-E')+'-') for k in states),
                'intended_states': 3, 'failure_reasons': [v['status'] for k, v in failures.items()
                    if k.startswith(arm+'/'+c.replace('-C', '-E')+'-')]}
                for names in PANELS.values() for c in names},
            'max_solute_numerical_allowance_kg': max((p['numerical_allowance_kg'] for p in predictions[arm]
                                                     if p['numerical_qualified']), default=None),
            'sensitivity_by_input_pp_per_pp': {str(j+1): summary([p['tds_sensitivity_pp_per_pp'][j]
                for p in predictions[arm] if p['tds_sensitivity_pp_per_pp'] is not None]) for j in (0, 1)}}
    return result


def evaluate(observed, predictions):
    if (len(observed) != 168 or {(o['shot'], o['fraction']) for o in observed} != {(s, f) for s in SHOTS for f in SUFFIX}
            or set(predictions) != set(ARMS)):
        raise ValueError('EXACT_SIX_ARM_FUTURE_MATRIX_REQUIRED')
    for arm in ARMS:
        if len(predictions[arm]) != len(observed) or any(any(o[k] != p[k] for k in QUERY_KEYS) for o, p in zip(observed, predictions[arm])):
            raise ValueError('IDENTICAL_FROZEN_SUPPORT_AND_ORDER_REQUIRED')
    primary, shots = assess(observed, predictions, True)
    full, full_shots = assess(observed, predictions, False)
    axes = primary['axes']
    disposition = ('TWO_ASSAY_RATE_ADAPTATION_EARNED_ON_DECLARED_SUPPORT'
        if all(axes[k] == 'PASS' for k in ('AXIS_A', 'AXIS_B', 'AXIS_C'))
        else 'TWO_ASSAY_MASS_INADEQUATE_ON_DECLARED_OBSERVED_WINDOWS' if axes['AXIS_A'] == 'FAIL'
        else 'TWO_ASSAY_COMPLEXITY_NOT_EARNED_ON_DECLARED_OBSERVED_WINDOWS' if axes['AXIS_A'] == 'PASS'
        else 'TWO_ASSAY_ASSESSMENT_BLOCKED_ON_DECLARED_OBSERVED_WINDOWS')
    return {'task': TASK, 'primary_candidate': PRIMARY, 'disposition': disposition,
        'scope': 'DECLARED_OBSERVED_WINDOWS', 'restricted_primary': primary, 'full_intended_suffix': full,
        'diagnostics': diagnostics(observed, predictions, shots), 'rights': source.RIGHTS,
        'labels': md.REAL_LABELS, 'physical_validation': 'NOT_ESTABLISHED'}, {'restricted': shots, 'full_intended_suffix': full_shots}


def verify_before_score(out, review):
    out = Path(out)
    if any((out/n).exists() for n in ('score_receipt.json', 'scores.json', 'score_completion.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    frozen = settings.verify_before_score(out, review)
    approved = read(review)
    if (frozen['task'] != TASK or approved.get('task') != TASK or not approved.get('reviewer')
            or approved.get('unresolved_blocking_findings') != []
            or set(frozen['code_and_protocol']) != set(FREEZE_PATHS) | set(read(out/'execution.json')['imported_first_party_modules'])
            or set(frozen['artifacts']) != set(BUNDLE_FILES)):
        raise ValueError('COMPLETE_INDEPENDENT_EXACT_FREEZE_REVIEW_REQUIRED')
    qualified_sources()
    return frozen


def score(out, review):
    out = Path(out)
    verify_before_score(out, review)
    write_json(out/'score_receipt.json', {'task': TASK, 'status': 'STARTED',
        'freeze_sha256': digest(out/'freeze.json'), 'review_sha256': digest(review),
        'predictions_sha256': digest(out/'predictions.json')})
    coords = coordinates(qualified_sources()[0])
    if canonical_hash(coords) != canonical_hash(read(out/'coordinates.json')):
        raise ValueError('SOURCE_COORDINATE_DRIFT')
    rows = project_assays(assay_rows(), coords, SUFFIX)
    mask = read(out/'support.json')
    observed = [dict(r, **q) for r, q in zip(rows, mask)]
    if any((r['shot'], r['fraction']) != (q['shot'], q['fraction']) for r, q in zip(rows, mask)):
        raise ValueError('SCORER_PROJECTION_ORDER_MISMATCH')
    predictions = read(out/'predictions.json')
    with fit_source.no_optimization():
        result, shots = evaluate(observed, predictions)
    result['parameter_and_numerical_diagnostics'] = parameter_summary(read(out/'states.json'), read(out/'failures.json'), predictions)
    write_json(out/'observed_suffix.json', observed)
    write_json(out/'shot_results.json', shots)
    write_json(out/'scores.json', result)
    write_json(out/'score_completion.json', {'task': TASK, 'status': 'COMPLETE',
        'scores_sha256': digest(out/'scores.json'), 'shot_results_sha256': digest(out/'shot_results.json'),
        'score_receipt_sha256': digest(out/'score_receipt.json'), 'scientific_score_passes': 1})
    print(result['disposition'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('prepare', 'freeze', 'score', 'report'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--out', type=Path, required=True)
        if name == 'score':
            cmd.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'score':
        score(args.out, args.review)
    elif args.command == 'report':
        print(json.dumps(read(args.out/'scores.json'), indent=2))
    else:
        {'prepare': prepare, 'freeze': freeze}[args.command](args.out)


if __name__ == '__main__':
    main()

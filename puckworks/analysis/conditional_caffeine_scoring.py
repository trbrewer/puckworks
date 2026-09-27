"""Once-only caffeine-task outcome attachment and retained-artifact reporting.

No fitting, prediction or historical scorer is called here. All numerical
allowances are application-error estimates, not statistical uncertainty.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np

from . import pannusch_conditional_caffeine_delivery as pipeline
from . import pannusch_conditioned_mass_delivery as receipt

INCOMPLETE = 'NOT_ADJUDICATED_INCOMPLETE_SUPPORT'
UNRESOLVED = 'NUMERICALLY_UNRESOLVED'


def conjunction(values):
    values = tuple(values)
    if 'FAIL' in values:
        return 'FAIL'
    if values and all(v == 'PASS' for v in values):
        return 'PASS'
    return INCOMPLETE if INCOMPLETE in values else UNRESOLVED


def upper(value, allowance, budget):
    if value is None or allowance is None:
        return INCOMPLETE
    return 'PASS' if value+allowance <= budget else 'FAIL' if value-allowance > budget else UNRESOLVED


def shot_metrics(rows, predictions):
    if not rows or len(rows) != len(predictions):
        return None
    if any(not r['analyte_eligible'] or r['q'] is None or r['mass_kg'] is None
           or not p['numerical_qualified'] or p['caffeine_mg_g'] is None
           for r, p in zip(rows, predictions)):
        return None
    mass = np.asarray([r['mass_kg'] for r in rows])
    error = np.asarray([p['caffeine_mg_g']-1000*r['q'] for r, p in zip(rows, predictions)])
    allowance = np.asarray([1000*p['allowance_kg']/m for p, m in zip(predictions, mass)])
    weights = mass/mass.sum()
    bias = float(weights @ error)
    return {'R_mg_g': float(np.sqrt(weights @ error**2)), 'B_mg_g': bias, 'absB_mg_g': abs(bias),
            'R_allowance_mg_g': float(np.sqrt(weights @ allowance**2)),
            'B_allowance_mg_g': float(weights @ allowance),
            'absB_allowance_mg_g': float(weights @ allowance), 'assayed_interval_mass_RMSE_mg': float(np.sqrt(np.mean((1e6*mass*error/1000)**2))),
            'assayed_mass_signed_error_mg': float(1e6*sum(p['caffeine_kg']-r['q']*r['mass_kg'] for r,p in zip(rows,predictions))),
            'assayed_interval_mass_MAE_mg': float(np.mean(abs(1e6*mass*error/1000))), 'windows': len(rows),
            'assayed_beverage_kg': float(mass.sum()),
            'observed_assayed_caffeine_kg': sum(r['q']*r['mass_kg'] for r in rows),
            'predicted_assayed_caffeine_kg': sum(p['caffeine_kg'] for p in predictions)}


METRICS = ('R_mg_g', 'B_mg_g', 'absB_mg_g', 'R_allowance_mg_g', 'B_allowance_mg_g', 'absB_allowance_mg_g', 'assayed_interval_mass_RMSE_mg', 'assayed_mass_signed_error_mg', 'assayed_interval_mass_MAE_mg')


def mean_metrics(values):
    if not values or any(v is None for v in values):
        return None
    return {k: float(np.mean([v[k] for v in values])) for k in METRICS}


def panel_metrics(observed, predicted, conditions):
    pi = {(p['shot'], p['fraction']): p for p in predicted}
    ci, private_shots = {}, []
    for condition in conditions:
        shots = sorted({r['shot'] for r in observed if r['condition'] == condition})
        if len(shots) != 3:
            raise ValueError('ORIGINAL_THREE_SHOT_DENOMINATOR_REQUIRED')
        full, diagnostic, coverage = [], [], []
        for shot in shots:
            rows = [r for r in observed if r['shot'] == shot]
            if {r['fraction'] for r in rows} != set(pipeline.SUFFIX) or len(rows) != 4:
                raise ValueError('ORIGINAL_FOUR_SUFFIX_SLOTS_REQUIRED')
            predictions = [pi[(r['shot'], r['fraction'])] for r in rows]
            mask = [p['supported'] for p in predictions]
            restricted = shot_metrics([r for r, keep in zip(rows, mask) if keep],
                                      [p for p, keep in zip(predictions, mask) if keep])
            complete = shot_metrics(rows, predictions) if all(mask) else None
            full.append(complete); diagnostic.append(restricted)
            coverage.append({'intended': 4, 'supported': sum(mask),
                             'qualified': sum(p['numerical_qualified'] and keep for p, keep in zip(predictions, mask))})
            private_shots.append({'shot': shot, 'condition': condition, 'full': complete,
                                  'support_diagnostic': restricted, 'coverage': coverage[-1]})
        complete_metric, support_metric = mean_metrics(full), mean_metrics(diagnostic)
        # Only COMPLETE shots may contribute to full-scope nonnegative lower bounds.
        lower_R = sum(max(0., v['R_mg_g']-v['R_allowance_mg_g']) for v in full if v)/3
        lower_absB = sum(max(0., v['absB_mg_g']-v['absB_allowance_mg_g']) for v in full if v)/3
        if complete_metric is None:
            adequacy = 'FAIL' if lower_R > .50 or lower_absB > .25 else INCOMPLETE
        else:
            adequacy = conjunction([upper(complete_metric['R_mg_g'], complete_metric['R_allowance_mg_g'], .50),
                                   upper(complete_metric['absB_mg_g'], complete_metric['absB_allowance_mg_g'], .25)])
        ci[condition] = {'full_scope_metrics': complete_metric, 'supported_subset_diagnostic': support_metric,
            'full_scope_adequacy': adequacy, 'original_shots': 3, 'complete_shots': sum(v is not None for v in full),
            'original_slots': 12, 'supported_slots': sum(v['supported'] for v in coverage),
            'qualified_slots': sum(v['qualified'] for v in coverage),
            'complete_shot_full_condition_lower_bounds': {'R_mg_g': lower_R, 'absB_mg_g': lower_absB}}
    return {'conditions': ci, 'original_conditions': len(conditions), 'original_shots': 3*len(conditions),
            'original_slots': 12*len(conditions),
            'full_scope_metrics': mean_metrics([v['full_scope_metrics'] for v in ci.values()]),
            'supported_subset_diagnostic': mean_metrics([v['supported_subset_diagnostic'] for v in ci.values()]),
            'full_scope_adequacy': conjunction(v['full_scope_adequacy'] for v in ci.values()),
            'complete_scope': all(v['full_scope_metrics'] is not None for v in ci.values())}, private_shots


def material_gain(candidate, reference):
    if not candidate['complete_scope'] or not reference['complete_scope']:
        return {'status': INCOMPLETE, 'reason': 'FULL_PRIMARY_COMMON_SUPPORT_REQUIRED'}
    c, r = candidate['full_scope_metrics'], reference['full_scope_metrics']
    gain, gain_allowance = r['R_mg_g']-c['R_mg_g'], r['R_allowance_mg_g']+c['R_allowance_mg_g']
    # >=15% gain is c <= .85*r, avoiding unstable percentage division.
    relative = upper(c['R_mg_g']-.85*r['R_mg_g'], c['R_allowance_mg_g']+.85*r['R_allowance_mg_g'], 0.)
    if r['R_mg_g']-r['R_allowance_mg_g'] <= 1e-12:
        relative = 'FAIL'
    wins, possible = 0, 0
    for condition, entry in candidate['conditions'].items():
        a = entry['full_scope_metrics']; b = reference['conditions'][condition]['full_scope_metrics']
        wins += a['R_mg_g']+a['R_allowance_mg_g'] < b['R_mg_g']-b['R_allowance_mg_g']
        possible += a['R_mg_g']-a['R_allowance_mg_g'] < b['R_mg_g']+b['R_allowance_mg_g']
    win_status = 'PASS' if wins >= 3 else 'FAIL' if possible < 3 else UNRESOLVED
    deterioration = c['absB_mg_g']-r['absB_mg_g']
    da = c['absB_allowance_mg_g']+r['absB_allowance_mg_g']
    components = {'absolute_gain': upper(-gain, gain_allowance, -.10),
        'relative_gain': relative, 'condition_wins': win_status,
        'abs_bias_deterioration': upper(deterioration, da, .05)}
    return {'status': conjunction(components.values()), 'components': components,
        'R_improvement_mg_g': gain, 'R_improvement_allowance_mg_g': gain_allowance,
        'relative_improvement': gain/r['R_mg_g'] if r['R_mg_g']-r['R_allowance_mg_g'] > 1e-12 else None,
        'relative_improvement_lower_bound': 1-(c['R_mg_g']+c['R_allowance_mg_g'])/(r['R_mg_g']-r['R_allowance_mg_g']) if r['R_mg_g']-r['R_allowance_mg_g'] > 1e-12 else None,
        'definite_condition_wins': int(wins), 'possible_condition_wins': int(possible),
        'mean_absB_deterioration_mg_g': deterioration, 'mean_absB_allowance_mg_g': da}


def evaluate(observed, predictions):
    expected = {(r['shot'], r['fraction']) for r in observed}
    if len(expected) != 96 or len(observed) != 96 or set(predictions) != set(pipeline.md.ARMS):
        raise ValueError('ALL_INTENDED_PRED_SLOTS_REQUIRED')
    supports = []
    for ps in predictions.values():
        if len(ps) != 96 or {(p['shot'], p['fraction']) for p in ps} != expected:
            raise ValueError('FAILURES_CANNOT_DROP_SLOTS')
        supports.append({(p['shot'], p['fraction']): (p['supported'], p['reason']) for p in ps})
    if any(s != supports[0] for s in supports):
        raise ValueError('IDENTICAL_COMPARISON_SUPPORT_REQUIRED')
    panels, private = {}, {}
    for panel, conditions in pipeline.PANELS.items():
        panels[panel], private[panel] = {}, {}
        for arm in pipeline.md.ARMS:
            panels[panel][arm], private[panel][arm] = panel_metrics(observed, predictions[arm], conditions)
    p = panels['primary']
    adequacy = {arm: p[arm]['full_scope_adequacy'] for arm in pipeline.md.ARMS}
    increments = {axis: material_gain(p['S2'], p[ref]) for axis, ref in [('B','S1'),('C','D0'),('D','S0')]}
    vector = {'A': adequacy['S2'], **{axis: result['status'] for axis, result in increments.items()}}
    simpler = [arm for arm in ('D0','S0','S1') if adequacy[arm] == 'PASS']
    failures = {arm: dict(Counter(r['prediction_status'] for r in ps if r['supported'] and not r['numerical_qualified']))
                for arm, ps in predictions.items()}
    complete = all(v['complete_scope'] for v in p.values())
    if all(s == 'PASS' for s in vector.values()):
        disposition = 'TDS_CONDITIONED_CAFFEINE_MAPPING_EARNED'
    elif simpler:
        disposition = 'SIMPLER_CAFFEINE_PREDICTOR_ADEQUATE_NO_EARNED_COMPLEXITY'
    elif adequacy['S2'] == 'PASS':
        disposition = 'CAFFEINE_ADEQUATE_INCREMENT_UNRESOLVED'
    elif complete and all(s == 'FAIL' for s in adequacy.values()):
        disposition = 'TESTED_CAFFEINE_MODELS_INADEQUATE'
    elif any(failures.values()) or UNRESOLVED in vector.values() or UNRESOLVED in adequacy.values():
        disposition = UNRESOLVED
    else:
        disposition = INCOMPLETE
    extrapolation = {arm: {panel: {'shots': len({r['shot'] for r in ps if r['condition'] in conditions and r['feature_extrapolation']}),
        'feature_counts_by_shot': dict(Counter(feature for shot in sorted({r['shot'] for r in ps if r['condition'] in conditions})
            for feature in set(f for r in ps if r['shot'] == shot for f in r['feature_extrapolation'])))}
        for panel, conditions in pipeline.PANELS.items()} for arm, ps in predictions.items()}
    return {'task': pipeline.TASK, 'disposition': disposition, 'primary_candidate': 'S2', 'decision_vector': vector,
        'adequacy_by_arm': adequacy, 'adequate_simpler_arms': simpler, 'increments': increments, 'panels': panels,
        'feature_extrapolation': extrapolation, 'prediction_failures': failures,
        'claims': list(pipeline.md.CLAIMS), 'rights': pipeline.source.RIGHTS,
        'physical_validation': 'NOT_ESTABLISHED', 'native_ewp_runs': 0, 'scientific_score_passes': 1,
        'merge_authorized': False, 'production_adoption_authorized': False, 'successor_authorized': False}, private


def verify_before_score(out, review):
    if any((out/n).exists() for n in ('score_receipt.json', 'scores.json', 'score_completion.json', 'observed_suffix.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    frozen = receipt.verify_before_score(out, review)
    approved = pipeline.read(review)
    if (frozen['task'] != pipeline.TASK or approved.get('task') != pipeline.TASK
            or not approved.get('reviewer') or approved.get('unresolved_blocking_findings') != []
            or approved.get('future_chemistry_attached') is not False):
        raise ValueError('GENUINE_INDEPENDENT_EXACT_FREEZE_REVIEW_REQUIRED')
    pipeline.qualified_sources()
    return frozen


def score(out, review):
    out = pipeline.private_directory(out)
    verify_before_score(out, review)
    pipeline.write(out/'score_receipt.json', {'task': pipeline.TASK, 'status': 'STARTED',
        'freeze_sha256': pipeline.digest(out/'freeze.json'), 'review_sha256': pipeline.digest(Path(review)),
        'predictions_sha256': pipeline.digest(out/'predictions.json')})
    # The sole PRED outcome join, strictly after exclusive start receipt.
    coords = pipeline.read(out/'coordinates.json')
    rows = pipeline.old.all_rows()
    observed = pipeline.target_slots(coords, rows, campaign='PREDICTION_2022_03', include_values=True)
    paths, _ = pipeline.qualified_sources()
    checked = pipeline.original_caffeine_check(paths, observed)
    ordering, ordering_rows = pipeline.chemical_ordering(observed, rows)
    predictions = pipeline.read(out/'predictions.json')
    result, private = evaluate(observed, predictions)
    result['PRED_observed_chemical_ordering'] = ordering
    result['PRED_original_caffeine_checks'] = checked
    result['D0_predicted_TDS_ordering'] = pipeline.read(out/'D0_ordering_summary.json')
    pipeline.write(out/'observed_suffix.json', observed)
    pipeline.write(out/'outcome_ordering.json', ordering_rows)
    pipeline.write(out/'shot_results.json', private)
    pipeline.write(out/'scores.json', result)
    pipeline.write(out/'score_completion.json', {'task': pipeline.TASK, 'status': 'COMPLETE',
        'scientific_score_passes': 1, 'scores_sha256': pipeline.digest(out/'scores.json'),
        'shot_results_sha256': pipeline.digest(out/'shot_results.json'),
        'observed_suffix_sha256': pipeline.digest(out/'observed_suffix.json'),
        'score_receipt_sha256': pipeline.digest(out/'score_receipt.json')})
    print(result['disposition'])


def report(out):
    out = Path(out)
    completion = pipeline.read(out/'score_completion.json')
    if completion['status'] != 'COMPLETE' or completion['scores_sha256'] != pipeline.digest(out/'scores.json'):
        raise ValueError('RETAINED_COMPLETED_SCORE_REQUIRED')
    return pipeline.read(out/'scores.json')

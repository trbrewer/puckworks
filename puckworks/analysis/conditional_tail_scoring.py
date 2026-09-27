"""Once-only task-006 outcome attachment and retained-artifact reporting.

No fitting, prediction or historical scorer is called here. All numerical
allowances are application-error estimates, not statistical uncertainty.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

import numpy as np

from . import pannusch_conditional_tail_delivery as pipeline
from . import pannusch_conditioned_mass_delivery as receipt

INCOMPLETE = 'SOURCE_SUPPORT_INCOMPLETE'
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
    if any(not r['eligible'] or r['q'] is None or r['mass_kg'] is None
           or not p['numerical_qualified'] or p['predicted_tds_percent'] is None
           for r, p in zip(rows, predictions)):
        return None
    mass = np.asarray([r['mass_kg'] for r in rows])
    error = np.asarray([p['predicted_tds_percent']-100*r['q'] for r, p in zip(rows, predictions)])
    allowance = np.asarray([100*p['numerical_allowance_kg']/m for p, m in zip(predictions, mass)])
    weights = mass/mass.sum()
    bias = float(weights @ error)
    return {'R_pp': float(np.sqrt(weights @ error**2)), 'B_pp': bias, 'absB_pp': abs(bias),
            'R_allowance_pp': float(np.sqrt(weights @ allowance**2)),
            'B_allowance_pp': float(weights @ allowance),
            'absB_allowance_pp': float(weights @ allowance), 'windows': len(rows),
            'assayed_beverage_kg': float(mass.sum()),
            'observed_assayed_solute_kg': sum(r['solute_kg'] for r in rows),
            'predicted_assayed_solute_kg': sum(p['predicted_solute_kg'] for p in predictions)}


METRICS = ('R_pp', 'B_pp', 'absB_pp', 'R_allowance_pp', 'B_allowance_pp', 'absB_allowance_pp')


def mean_metrics(values):
    if not values or any(v is None for v in values):
        return None
    return {k: float(np.mean([v[k] for v in values])) for k in METRICS}


def panel_metrics(observed, predicted, conditions, *, common_legacy=False):
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
            mask = [p['supported'] and (p['legacy_supported'] if common_legacy else True) for p in predictions]
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
        lower_R = sum(max(0., v['R_pp']-v['R_allowance_pp']) for v in full if v)/3
        lower_absB = sum(max(0., v['absB_pp']-v['absB_allowance_pp']) for v in full if v)/3
        if complete_metric is None:
            adequacy = 'FAIL' if lower_R > 1. or lower_absB > .5 else INCOMPLETE
        else:
            adequacy = conjunction([upper(complete_metric['R_pp'], complete_metric['R_allowance_pp'], 1.),
                                   upper(complete_metric['absB_pp'], complete_metric['absB_allowance_pp'], .5)])
        ci[condition] = {'full_scope_metrics': complete_metric, 'supported_subset_diagnostic': support_metric,
            'full_scope_adequacy': adequacy, 'original_shots': 3, 'complete_shots': sum(v is not None for v in full),
            'original_slots': 12, 'supported_slots': sum(v['supported'] for v in coverage),
            'qualified_slots': sum(v['qualified'] for v in coverage),
            'complete_shot_full_condition_lower_bounds': {'R_pp': lower_R, 'absB_pp': lower_absB}}
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
    gain, gain_allowance = r['R_pp']-c['R_pp'], r['R_allowance_pp']+c['R_allowance_pp']
    # >=15% gain is c <= .85*r, avoiding unstable percentage division.
    relative = upper(c['R_pp']-.85*r['R_pp'], c['R_allowance_pp']+.85*r['R_allowance_pp'], 0.)
    if r['R_pp']-r['R_allowance_pp'] <= 1e-12:
        relative = 'FAIL'
    wins, possible = 0, 0
    for condition, entry in candidate['conditions'].items():
        a = entry['full_scope_metrics']; b = reference['conditions'][condition]['full_scope_metrics']
        wins += a['R_pp']+a['R_allowance_pp'] < b['R_pp']-b['R_allowance_pp']
        possible += a['R_pp']-a['R_allowance_pp'] < b['R_pp']+b['R_allowance_pp']
    win_status = 'PASS' if wins >= 3 else 'FAIL' if possible < 3 else UNRESOLVED
    deterioration = c['absB_pp']-r['absB_pp']
    da = c['absB_allowance_pp']+r['absB_allowance_pp']
    components = {'absolute_gain': upper(-gain, gain_allowance, -.10),
        'relative_gain': relative, 'condition_wins': win_status,
        'abs_bias_deterioration': upper(deterioration, da, .10)}
    return {'status': conjunction(components.values()), 'components': components,
        'R_improvement_pp': gain, 'R_improvement_allowance_pp': gain_allowance,
        'relative_improvement': gain/r['R_pp'] if r['R_pp']-r['R_allowance_pp'] > 1e-12 else None,
        'definite_condition_wins': int(wins), 'possible_condition_wins': int(possible),
        'mean_absB_deterioration_pp': deterioration, 'mean_absB_allowance_pp': da}


def competitiveness(candidate, reference):
    if not candidate['complete_scope'] or not reference['complete_scope']:
        return INCOMPLETE
    c, r = candidate['full_scope_metrics'], reference['full_scope_metrics']
    return conjunction(upper(c[k]-r[k], c[k.replace('_pp', '_allowance_pp')]+r[k.replace('_pp', '_allowance_pp')], .1)
                       for k in ('R_pp', 'absB_pp'))


def evaluate(observed, predictions):
    arms = (*pipeline.md.ARMS, pipeline.LEGACY)
    expected = {(r['shot'], r['fraction']) for r in observed}
    if len(expected) != 96 or len(observed) != 96 or set(predictions) != set(arms):
        raise ValueError('ALL_INTENDED_PRED_IDENTITIES_REQUIRED')
    for ps in predictions.values():
        if len(ps) != 96 or {(p['shot'], p['fraction']) for p in ps} != expected:
            raise ValueError('MODEL_FAILURE_CANNOT_REMOVE_RECORDS')
    panels, private = {}, {}
    for panel, conditions in pipeline.PANELS.items():
        panels[panel], private[panel] = {}, {}
        for arm in arms:
            panels[panel][arm], private[panel][arm] = panel_metrics(observed, predictions[arm], conditions,
                common_legacy=arm == pipeline.LEGACY)
    common = {}
    for arm in ('C2', pipeline.LEGACY):
        common[arm], _ = panel_metrics(observed, predictions[arm], pipeline.PANELS['primary'], common_legacy=True)
    primary = panels['primary']
    a = primary['C2']['full_scope_adequacy']
    b = material_gain(primary['C2'], primary['C1'])
    c_parts = {'adequacy': a, 'versus_C0': competitiveness(primary['C2'], primary['C0']),
               'versus_C1': competitiveness(primary['C2'], primary['C1'])}
    c = conjunction(c_parts.values())
    d = material_gain(common['C2'], common[pipeline.LEGACY])
    simpler = {arm: {'adequacy': primary[arm]['full_scope_adequacy'],
                    'C2_material_gain': material_gain(primary['C2'], primary[arm])} for arm in ('C0', 'C1')}
    limitations = []
    if any(not v['complete_scope'] for panel in panels.values() for v in panel.values()):
        limitations.append(INCOMPLETE)
    failures = {arm: dict(Counter(p['prediction_status'] for p in ps if p['supported'] and not p['numerical_qualified']))
                for arm, ps in predictions.items()}
    if any(failures.values()):
        limitations.append(UNRESOLVED)
    if all(v == 'PASS' for v in (a, b['status'], c, d['status'])):
        label = 'LEARNED_TWO_ASSAY_MAPPING_EARNED'
    elif any(v['adequacy'] == 'PASS' and v['C2_material_gain']['status'] == 'FAIL' for v in simpler.values()):
        label = 'SIMPLER_LEARNER_SUFFICIENT'
    elif a == 'FAIL' and 'PASS' in (b['status'], d['status']):
        label = 'LEARNED_MAPPING_IMPROVES_BUT_INADEQUATE'
    elif a == 'FAIL':
        label = 'TESTED_LEARNED_MAPPING_INADEQUATE'
    elif a == INCOMPLETE:
        label = UNRESOLVED if any(failures.values()) else INCOMPLETE
    elif UNRESOLVED in (a, b['status'], c, d['status']):
        label = UNRESOLVED
    else:
        label = 'CONDITIONAL_MAPPING_VALUE_NOT_ESTABLISHED'
    extrapolation = {arm: {panel: {'shots': len({p['shot'] for p in predictions[arm]
        if p['condition'] in conditions and p['feature_extrapolation']}),
        'feature_counts_by_shot': dict(Counter(feature for shot in sorted({p['shot'] for p in predictions[arm] if p['condition'] in conditions})
            for feature in set(f for p in predictions[arm] if p['shot'] == shot for f in p['feature_extrapolation'])))}
        for panel, conditions in pipeline.PANELS.items()} for arm in pipeline.md.ARMS}
    return {'task': pipeline.TASK, 'disposition': label, 'primary_candidate': 'C2',
        'decision_vector': {'A': a, 'B': b['status'], 'C': c, 'D': d['status'], 'limitations': limitations},
        'incremental_second_assay': b, 'competitiveness': c_parts, 'legacy_gain': d,
        'simpler_learned_secondary_results': simpler, 'panels': panels,
        'primary_common_legacy_support': common, 'feature_extrapolation': extrapolation,
        'prediction_failures_on_learned_support': failures, 'claims': list(pipeline.md.CLAIMS),
        'rights': pipeline.source.RIGHTS, 'physical_validation': 'NOT_ESTABLISHED',
        'native_ewp_runs': 0, 'scientific_score_passes': 1, 'production_adoption_authorized': False,
        'merge_authorized': False, 'successor_authorized': False}, private


def verify_before_score(out, review):
    if any((out/n).exists() for n in ('score_receipt.json', 'scores.json', 'score_completion.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    frozen = receipt.verify_before_score(out, review)
    approved = pipeline.read(review)
    if (frozen['task'] != pipeline.TASK or approved.get('task') != pipeline.TASK
            or not approved.get('reviewer') or approved.get('unresolved_blocking_findings') != []
            or approved.get('future_chemistry_attached') is not False):
        raise ValueError('FRESH_INDEPENDENT_EXACT_FREEZE_REVIEW_REQUIRED')
    pipeline.qualified_sources()
    return frozen


def score(out, review):
    out = pipeline.private_directory(out)
    verify_before_score(out, review)
    pipeline.write(out/'score_receipt.json', {'task': pipeline.TASK, 'status': 'STARTED',
        'freeze_sha256': pipeline.digest(out/'freeze.json'), 'review_sha256': pipeline.digest(Path(review)),
        'predictions_sha256': pipeline.digest(out/'predictions.json')})
    # This is the ONLY outcome attachment. Never refit or regenerate predictions.
    coords = pipeline.read(out/'coordinates.json')
    _, observed = pipeline.project_assays(pipeline.all_rows(), coords, outcome=True)
    predictions = pipeline.read(out/'predictions.json')
    result, private = evaluate(observed, predictions)
    pipeline.write(out/'observed_suffix.json', observed)
    pipeline.write(out/'shot_results.json', private)
    pipeline.write(out/'scores.json', result)
    pipeline.write(out/'score_completion.json', {'task': pipeline.TASK, 'status': 'COMPLETE',
        'scientific_score_passes': 1, 'scores_sha256': pipeline.digest(out/'scores.json'),
        'shot_results_sha256': pipeline.digest(out/'shot_results.json'),
        'score_receipt_sha256': pipeline.digest(out/'score_receipt.json')})
    print(result['disposition'])


def report(out):
    out = Path(out)
    completion = pipeline.read(out/'score_completion.json')
    if completion['status'] != 'COMPLETE' or completion['scores_sha256'] != pipeline.digest(out/'scores.json'):
        raise ValueError('RETAINED_COMPLETED_SCORE_REQUIRED')
    return pipeline.read(out/'scores.json')

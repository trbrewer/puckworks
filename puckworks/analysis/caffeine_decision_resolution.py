"""Offline retrospective caffeine reduction; never fits, predicts or invokes scoring.

Inputs are hash-bound retained sufficient statistics, optionally retained fractions.
The historical reducer remains unchanged. All detailed outputs stay outside Git.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
from pathlib import Path

import numpy as np

from .mass_uncertainty_audit import (
    Inputs, IntegrityStop, index, private_output, reconcile, sha, spread, write,
)
from puckworks.validation import decision_resolution as policy

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/val_case_caffeine_decision_resolution_001'
HISTORY = ROOT / 'docs/analysis/sci_md_caffeine_delivery_001'
TASK = 'VAL-CASE-CAFFEINE-DECISION-RESOLUTION-001'
ARMS = ('D0', 'S0', 'S1', 'S2')
REFS = ('S1', 'D0', 'S0')
PANELS = {'primary': ('PRED-C01', 'PRED-C02', 'PRED-C05', 'PRED-C06'),
          'temperature_stress': ('PRED-C03', 'PRED-C04'),
          'flow_stress': ('PRED-C07', 'PRED-C08')}
FRACTIONS = (3, 5, 7, 10)
INCOMPLETE = 'NOT_ADJUDICATED_INCOMPLETE_SUPPORT'
UNRESOLVED = 'NUMERICALLY_UNRESOLVED'
METRICS = ('R_mg_g', 'B_mg_g', 'absB_mg_g', 'R_allowance_mg_g',
           'B_allowance_mg_g', 'absB_allowance_mg_g', 'assayed_interval_mass_RMSE_mg',
           'assayed_mass_signed_error_mg', 'assayed_interval_mass_MAE_mg')
UNKNOWN = ('analytical repeatability and calibration', 'early input propagation',
           'training and model selection', 'new conditions and cross-source', 'population coverage')


def upper(value, allowance, budget):
    """Historical binary64 endpoint arithmetic; helper compares those endpoints."""
    if value is None or allowance is None:
        return INCOMPLETE
    relation = policy.interval_relation(policy.Interval(value-allowance, value+allowance), '<=', budget)
    return {'satisfies': 'PASS', 'violates': 'FAIL', 'overlaps': UNRESOLVED}[relation]


def conjunction(values):
    values = tuple(values)
    if 'FAIL' in values:
        return 'FAIL'
    if values and all(v == 'PASS' for v in values):
        return 'PASS'
    return INCOMPLETE if INCOMPLETE in values else UNRESOLVED


def mean_metrics(values):
    if not values or any(v is None for v in values):
        return None
    return {k: float(np.mean([v[k] for v in values])) for k in METRICS}


def number(value, *, nonnegative=False, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('FINITE_NUMERIC_VALUE_REQUIRED')
    if (nonnegative and value < 0) or (positive and value <= 0):
        raise ValueError('INVALID_SIGN')
    return value


def validate_metric(metric, windows):
    if metric is None:
        raise ValueError('REQUIRED_METRIC_MISSING')
    for k in METRICS:
        number(metric[k], nonnegative=k not in ('B_mg_g', 'assayed_mass_signed_error_mg'))
    if metric['absB_mg_g'] != abs(metric['B_mg_g']):
        raise ValueError('SHOT_ABSOLUTE_BIAS_REQUIRED')
    if metric['B_allowance_mg_g'] != metric['absB_allowance_mg_g']:
        raise ValueError('INCOMPATIBLE_BIAS_ALLOWANCES')
    if type(metric['windows']) is not int or metric['windows'] != windows:
        raise ValueError('WINDOW_COUNT_MISMATCH')
    number(metric['assayed_beverage_kg'], positive=True)
    for k in ('observed_assayed_caffeine_kg', 'predicted_assayed_caffeine_kg'):
        number(metric[k], nonnegative=True)


def validate_shots(data):
    if set(data) != set(PANELS):
        raise ValueError('ALL_PANELS_REQUIRED')
    seen = set()
    for panel, conditions in PANELS.items():
        arms = data[panel]
        if set(arms) != set(ARMS):
            raise ValueError('ALL_FOUR_ARMS_REQUIRED')
        expected = None
        for arm in ARMS:
            rows = arms[arm]
            keyed = index(rows, ('shot',))
            if len(rows) != 3*len(conditions) or {r['condition'] for r in rows} != set(conditions):
                raise ValueError('ORIGINAL_POPULATION_REQUIRED')
            if any(sum(r['condition'] == c for r in rows) != 3 for c in conditions):
                raise ValueError('ORIGINAL_THREE_SHOTS_REQUIRED')
            membership = {k: (r['condition'], r['coverage']) for k, r in keyed.items()}
            if expected is not None and membership != expected:
                raise ValueError('IDENTICAL_ARM_MEMBERSHIP_AND_SUPPORT_REQUIRED')
            expected = membership
            for r in rows:
                c = r['coverage']
                if (set(c) != {'intended', 'supported', 'qualified'} or
                    any(type(v) is not int for v in c.values()) or
                    c['intended'] != 4 or not 0 < c['qualified'] == c['supported'] <= 4):
                    raise ValueError('INVALID_COVERAGE')
                if (r['full'] is not None) != (c['qualified'] == 4):
                    raise ValueError('FULL_SUPPORT_MISMATCH')
                validate_metric(r['support_diagnostic'], c['qualified'])
                if r['full'] is not None:
                    validate_metric(r['full'], 4)
                    if r['full'] != r['support_diagnostic']:
                        raise ValueError('COMPLETE_SUBSET_MISMATCH')
            intended = 4*len(rows)
            if sum(r['coverage']['supported'] for r in rows) != intended-(panel == 'flow_stress'):
                raise ValueError('HISTORICAL_SUPPORT_REQUIRED')
        ids = {r['shot'] for r in arms['S2']}
        if ids & seen:
            raise ValueError('SHOT_IN_MULTIPLE_PANELS')
        seen |= ids
    return data


def condition_result(rows):
    """Original three-shot condition, including nonnegative full-scope bounds."""
    if len(rows) != 3:
        raise ValueError('ORIGINAL_THREE_SHOTS_REQUIRED')
    full = [r['full'] for r in rows]
    m = mean_metrics(full)
    lower = {k: sum(max(0., v[k]-v[k.replace('_mg_g', '_allowance_mg_g')])
                    for v in full if v is not None)/3 for k in ('R_mg_g', 'absB_mg_g')}
    status = ('FAIL' if lower['R_mg_g'] > .50 or lower['absB_mg_g'] > .25 else INCOMPLETE) if m is None else conjunction((
        upper(m['R_mg_g'], m['R_allowance_mg_g'], .50),
        upper(m['absB_mg_g'], m['absB_allowance_mg_g'], .25)))
    return {'full_scope_metrics': m,
            'supported_subset_diagnostic': mean_metrics([r['support_diagnostic'] for r in rows]),
            'full_scope_adequacy': status, 'original_shots': 3,
            'complete_shots': sum(v is not None for v in full), 'original_slots': 12,
            'supported_slots': sum(r['coverage']['supported'] for r in rows),
            'qualified_slots': sum(r['coverage']['qualified'] for r in rows),
            'complete_shot_full_condition_lower_bounds': lower}


def reproduce_panel(rows, conditions):
    ci = {c: condition_result([r for r in rows if r['condition'] == c]) for c in conditions}
    return {'conditions': ci, 'original_conditions': len(conditions), 'original_shots': 3*len(conditions),
            'original_slots': 12*len(conditions),
            'full_scope_metrics': mean_metrics([v['full_scope_metrics'] for v in ci.values()]),
            'supported_subset_diagnostic': mean_metrics([v['supported_subset_diagnostic'] for v in ci.values()]),
            'full_scope_adequacy': conjunction(v['full_scope_adequacy'] for v in ci.values()),
            'complete_scope': all(v['full_scope_metrics'] is not None for v in ci.values())}


def contrast(c, r):
    gain = r['R_mg_g']-c['R_mg_g']
    ug = r['R_allowance_mg_g']+c['R_allowance_mg_g']
    good_denominator = r['R_mg_g']-r['R_allowance_mg_g'] > 1e-12
    relative = gain/r['R_mg_g'] if good_denominator else None
    lower = 1-(c['R_mg_g']+c['R_allowance_mg_g'])/(r['R_mg_g']-r['R_allowance_mg_g']) if good_denominator else None
    rel_value = c['R_mg_g']-.85*r['R_mg_g']
    rel_u = c['R_allowance_mg_g']+.85*r['R_allowance_mg_g']
    d = c['absB_mg_g']-r['absB_mg_g']
    ud = c['absB_allowance_mg_g']+r['absB_allowance_mg_g']
    return {'R_improvement_mg_g': gain, 'R_improvement_allowance_mg_g': ug,
            'relative_improvement': relative, 'relative_improvement_lower_bound': lower,
            'relative_component_mg_g': rel_value, 'relative_component_allowance_mg_g': rel_u,
            'relative_denominator_guard': not good_denominator,
            'mean_absB_deterioration_mg_g': d, 'mean_absB_allowance_mg_g': ud,
            'signed_B_difference_mg_g': c['B_mg_g']-r['B_mg_g'],
            'signed_B_allowance_mg_g': c['B_allowance_mg_g']+r['B_allowance_mg_g'],
            'headroom': {'absolute_gain_mg_g': gain-.10, 'absolute_gain_lower_mg_g': gain-ug-.10,
                         'relative_component_mg_g': -rel_value, 'relative_component_lower_mg_g': -rel_value-rel_u,
                         'bias_mg_g': .05-d, 'bias_lower_mg_g': .05-d-ud}}


def wins(candidate, reference):
    definite = sum(a['R_mg_g']+a['R_allowance_mg_g'] < reference[k]['R_mg_g']-reference[k]['R_allowance_mg_g'] for k, a in candidate.items())
    possible = sum(a['R_mg_g']-a['R_allowance_mg_g'] < reference[k]['R_mg_g']+reference[k]['R_allowance_mg_g'] for k, a in candidate.items())
    return int(definite), int(possible)


def increment(candidate, reference):
    if not candidate['complete_scope'] or not reference['complete_scope']:
        return {'status': INCOMPLETE, 'reason': 'FULL_PRIMARY_COMMON_SUPPORT_REQUIRED'}
    v = contrast(candidate['full_scope_metrics'], reference['full_scope_metrics'])
    dw, pw = wins({k: r['full_scope_metrics'] for k, r in candidate['conditions'].items()},
                  {k: r['full_scope_metrics'] for k, r in reference['conditions'].items()})
    components = {'absolute_gain': upper(-v['R_improvement_mg_g'], v['R_improvement_allowance_mg_g'], -.10),
                  'relative_gain': 'FAIL' if v['relative_denominator_guard'] else upper(v['relative_component_mg_g'], v['relative_component_allowance_mg_g'], 0.),
                  'condition_wins': 'PASS' if dw >= 3 else 'FAIL' if pw < 3 else UNRESOLVED,
                  'abs_bias_deterioration': upper(v['mean_absB_deterioration_mg_g'], v['mean_absB_allowance_mg_g'], .05)}
    keys = ('R_improvement_mg_g', 'R_improvement_allowance_mg_g', 'relative_improvement',
            'relative_improvement_lower_bound', 'mean_absB_deterioration_mg_g', 'mean_absB_allowance_mg_g')
    return {'status': conjunction(components.values()), 'components': components,
            **{k: v[k] for k in keys}, 'definite_condition_wins': dw, 'possible_condition_wins': pw}


def reproduce(shots):
    panels = {p: {a: reproduce_panel(shots[p][a], cs) for a in ARMS} for p, cs in PANELS.items()}
    primary = panels['primary']
    adequacy = {a: primary[a]['full_scope_adequacy'] for a in ARMS}
    increments = {axis: increment(primary['S2'], primary[ref]) for axis, ref in zip(('B', 'C', 'D'), REFS)}
    vector = {'A': adequacy['S2'], **{k: v['status'] for k, v in increments.items()}}
    simpler = [a for a in ('D0', 'S0', 'S1') if adequacy[a] == 'PASS']
    if all(s == 'PASS' for s in vector.values()):
        disposition = 'TDS_CONDITIONED_CAFFEINE_MAPPING_EARNED'
    elif simpler:
        disposition = 'SIMPLER_CAFFEINE_PREDICTOR_ADEQUATE_NO_EARNED_COMPLEXITY'
    elif adequacy['S2'] == 'PASS':
        disposition = 'CAFFEINE_ADEQUATE_INCREMENT_UNRESOLVED'
    elif all(s == 'FAIL' for s in adequacy.values()):
        disposition = 'TESTED_CAFFEINE_MODELS_INADEQUATE'
    elif UNRESOLVED in (*vector.values(), *adequacy.values()):
        disposition = UNRESOLVED
    else:
        disposition = INCOMPLETE
    return {'panels': panels, 'adequacy_by_arm': adequacy, 'increments': increments,
            'decision_vector': vector, 'disposition': disposition, 'adequate_simpler_arms': simpler}


def arithmetic_differences(actual, expected, path='result'):
    reconcile(actual, expected, path)
    differences = []
    if isinstance(expected, dict):
        for k in expected:
            differences.extend(arithmetic_differences(actual[k], expected[k], path+'.'+k))
    elif isinstance(expected, list):
        for i, (a, e) in enumerate(zip(actual, expected)):
            differences.extend(arithmetic_differences(a, e, path+'.'+str(i)))
    elif isinstance(expected, float) and actual != expected:
        differences.append({'path': path, 'original': expected, 'reproduced': actual,
                            'absolute_difference': abs(actual-expected)})
    return differences


def fraction_metric(rows, predictions):
    """Independent fraction reduction using retained concentrations, never a model."""
    mass = np.asarray([number(r['mass_kg'], positive=True) for r in rows])
    error = np.asarray([number(p['caffeine_mg_g'])-1000*number(r['q'], nonnegative=True) for r, p in zip(rows, predictions)])
    u = np.asarray([1000*number(p['allowance_kg'], nonnegative=True)/m for p, m in zip(predictions, mass)])
    w = mass/mass.sum()
    bias = float(w @ error)
    return {'R_mg_g': float(np.sqrt(w @ error**2)), 'B_mg_g': bias, 'absB_mg_g': abs(bias),
            'R_allowance_mg_g': float(np.sqrt(w @ u**2)), 'B_allowance_mg_g': float(w @ u),
            'absB_allowance_mg_g': float(w @ u),
            'assayed_interval_mass_RMSE_mg': float(np.sqrt(np.mean((1e6*mass*error/1000)**2))),
            'assayed_mass_signed_error_mg': float(1e6*sum(p['caffeine_kg']-r['q']*r['mass_kg'] for r, p in zip(rows, predictions))),
            'assayed_interval_mass_MAE_mg': float(np.mean(abs(1e6*mass*error/1000))),
            'windows': len(rows), 'assayed_beverage_kg': float(mass.sum()),
            'observed_assayed_caffeine_kg': sum(r['q']*r['mass_kg'] for r in rows),
            'predicted_assayed_caffeine_kg': sum(p['caffeine_kg'] for p in predictions)}


def validate_windows(rows, shots=None):
    keyed = index(rows, ('shot', 'fraction'))
    if len(rows) != 96:
        raise ValueError('ALL_96_WINDOWS_REQUIRED')
    conditions = {c for cs in PANELS.values() for c in cs}
    if {r['condition'] for r in rows} != conditions:
        raise ValueError('CANONICAL_CONDITIONS_REQUIRED')
    for c in conditions:
        ids = {r['shot'] for r in rows if r['condition'] == c}
        if len(ids) != 3:
            raise ValueError('THREE_CANONICAL_SHOTS_REQUIRED')
        for s in ids:
            if {r['fraction'] for r in rows if r['shot'] == s} != set(FRACTIONS):
                raise ValueError('ALL_FRACTIONS_REQUIRED')
    for r in rows:
        if (r['campaign'] != 'PREDICTION_2022_03' or r['analyte'] != 'caffeine'
                or r['source_id'] != 'P24-MAT-PRED' or not r['analyte_eligible']
                or r['coordinate_status'] != 'QUALIFIED' or not r['source_field']):
            raise ValueError('INCOMPATIBLE_WINDOW_IDENTITY_OR_VALIDITY')
        number(r['b0'], nonnegative=True); number(r['b1'], positive=True)
        number(r['mass_kg'], positive=True)
        if r['b1'] <= r['b0']:
            raise ValueError('INVALID_WINDOW_GEOMETRY')
        if 'q' in r:
            number(r['q'], nonnegative=True)
            if r['q'] > 1:
                raise ValueError('OBSERVATION_KG_KG_REQUIRED')
    if shots is not None:
        expected = {(r['shot'], r['condition']) for a in shots.values() for r in a['S2']}
        if {(r['shot'], r['condition']) for r in rows} != expected:
            raise ValueError('INCOMPATIBLE_SHOT_CROSSWALK')
    return keyed


def window_pairing(observed, predictions, queries=None, shots=None):
    oi = validate_windows(observed, shots)
    qi = validate_windows(queries, shots) if queries is not None else None
    if set(predictions) != set(ARMS):
        raise ValueError('ALL_FOUR_ARMS_REQUIRED')
    supports, prediction_index = [], {}
    identity_fields = ('campaign', 'condition', 'shot', 'fraction', 'analyte', 'source_id', 'source_field', 'b0', 'b1', 'mass_kg')
    for a in ARMS:
        pi = validate_windows(predictions[a], shots)
        if set(pi) != set(oi):
            raise ValueError('COMPLETE_PAIRING_REQUIRED')
        for key, r in oi.items():
            p = pi[key]
            if any(p[k] != r[k] for k in identity_fields):
                raise ValueError('INCOMPATIBLE_WINDOW_COORDINATES')
            if qi is not None and (any(qi[key][k] != r[k] for k in identity_fields)
                                   or (qi[key]['supported'], qi[key]['reason']) != (p['supported'], p['reason'])):
                raise ValueError('QUERY_CROSSWALK_MISMATCH')
            if type(p['supported']) is not bool or p['numerical_qualified'] != p['supported']:
                raise ValueError('QUALIFIED_SUPPORT_REQUIRED')
            if p['supported']:
                for k in ('caffeine_mg_g', 'caffeine_kg', 'allowance_kg', 'coordinate_allowance_kg'):
                    number(p[k], nonnegative=True)
                if p['allowance_kg'] < p['coordinate_allowance_kg'] or p['allowance_kg'] > 1e-9:
                    raise ValueError('INVALID_TOTAL_ALLOWANCE')
        supports.append({k: (p['supported'], p['reason']) for k, p in pi.items()})
        prediction_index[a] = pi
    if any(s != supports[0] for s in supports):
        raise ValueError('IDENTICAL_COMPARISON_SUPPORT_REQUIRED')
    unsupported = [k for k, (s, reason) in supports[0].items() if not s]
    if len(unsupported) != 1 or supports[0][unsupported[0]][1] != 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN':
        raise ValueError('ORIGINAL_UNSUPPORTED_SLOT_REQUIRED')
    return oi, prediction_index


def crosswalk(observed, queries=None, coordinates=None):
    """Reconcile admitted canonical keys/geometry, including optional source coordinates."""
    oi = validate_windows(observed)
    fields = ('campaign', 'condition', 'shot', 'fraction', 'source_id', 'b0', 'b1', 'mass_kg')
    for rows in (queries, coordinates):
        if rows is None:
            continue
        selected = [r for r in rows if r['campaign'] == 'PREDICTION_2022_03' and r['fraction'] in FRACTIONS]
        ri = index(selected, ('shot', 'fraction'), oi)
        if any(any(r[k] != oi[key][k] for k in fields) for key, r in ri.items()):
            raise ValueError('CANONICAL_COORDINATE_CROSSWALK_MISMATCH')
    if queries is not None:
        if (any(type(q['supported']) is not bool for q in queries) or
            sum(q['supported'] for q in queries) != 95 or
            any(q['reason'] != ('' if q['supported'] else 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN') for q in queries)):
            raise ValueError('ORIGINAL_QUERY_SUPPORT_REQUIRED')


def reconstruct(observed, predictions, shots):
    reconstructed = {}
    pi = {a: index(predictions[a], ('shot', 'fraction')) for a in ARMS}
    for panel in PANELS:
        reconstructed[panel] = {}
        for arm in ARMS:
            records = []
            for old in shots[panel][arm]:
                rows = [r for r in observed if r['shot'] == old['shot']]
                ps = [pi[arm][(r['shot'], r['fraction'])] for r in rows]
                kept = [(r, p) for r, p in zip(rows, ps) if p['supported']]
                coverage = {'intended': 4, 'supported': len(kept), 'qualified': sum(p['numerical_qualified'] for _, p in kept)}
                records.append({'shot': old['shot'], 'condition': old['condition'], 'coverage': coverage,
                                'full': fraction_metric(rows, ps) if len(kept) == 4 else None,
                                'support_diagnostic': fraction_metric([r for r, _ in kept], [p for _, p in kept])})
            reconstructed[panel][arm] = records
    return reconstructed


def reduce_scenario(arms, conditions, deleted=None, field='full'):
    result = {}
    for arm in ARMS:
        rows = [r for r in arms[arm] if r['shot'] != deleted]
        ci = {c: mean_metrics([r[field] for r in rows if r['condition'] == c]) for c in conditions}
        if any(v is None for v in ci.values()):
            raise ValueError('SCENARIO_REQUIRES_COMPLETE_METRICS')
        result[arm] = {'conditions': ci, 'balanced': mean_metrics(list(ci.values()))}
    pairs = {}
    for ref in REFS:
        c, r = result['S2'], result[ref]
        dw, pw = wins(c['conditions'], r['conditions'])
        pairs[ref] = {**contrast(c['balanced'], r['balanced']),
                      'definite_condition_wins': dw, 'possible_condition_wins': pw,
                      'condition_win_surplus_to_original_three': dw-3,
                      'conditions': {k: contrast(c['conditions'][k], r['conditions'][k]) for k in conditions}}
    return {'deleted_shot': deleted, 'retained_shots': [r['shot'] for r in arms['S2'] if r['shot'] != deleted],
            'conditions': list(conditions), 'scope': field, 'arms': result, 'comparisons': pairs}


def range_of(values):
    if not values or any(v is None for v in values):
        return None
    return [min(values), max(values)]


def envelope(records, value, allowance):
    return [min(r[value]-r[allowance] for r in records), max(r[value]+r[allowance] for r in records)]


def sensitivity_policy(records, ref, panel):
    """Finite configuration-set scope, not the original physical-shot population."""
    ids = tuple(('baseline' if i == 0 else f'deletion-{i:02d}') for i in range(len(records)))
    scope = policy.Scope('reference RMSE minus S2 RMSE', 'mg/g', panel+' finite scenario set',
        'range over baseline and declared whole-shot deletion statistics',
        'per scenario: equal shots within retained conditions, then equal conditions',
        'frozen '+ref+' and S2; no refitting', tuple((k, k) for k in ids),
        'finite configurations, not independent observations; actual membership mapped privately')
    req = policy.Requirement('positive-gain', False, 'increment', scope, '>', 0.,
        'Descriptive strict sign over finite tested configurations', 'zero contrast, not a practical margin',
        'approved', 'applicable_bound', ('historical numerical allowance',),
        ('No population-confidence or earned-complexity PASS',), comparator=ref)
    bounds = envelope(records, 'R_improvement_mg_g', 'R_improvement_allowance_mg_g')
    basis = policy.Basis('sensitivity', scope, 'Finite min/max with each scenario own propagated allowance',
        ('historical numerical allowance', 'whole-shot deletion'),
        ('Retained numerical allowances are application-error estimates; frozen fits and recorded cohort only',), ids)
    ev = policy.Evidence('sensitivity', scope, basis, ids,
        policy.Quality(True, True, True, True, 'Admitted bytes and exact paired memberships; historical arithmetic reproduced'),
        UNKNOWN, records[0]['R_improvement_mg_g'], policy.Interval(*bounds))
    decision = policy.evaluate(req, ev)
    return asdict(decision)


def summarize_sensitivity(scenarios, ref, panel):
    rs = [s['comparisons'][ref] for s in scenarios]
    ds = rs[1:]
    value_allowance = {'R_improvement_mg_g': 'R_improvement_allowance_mg_g',
        'mean_absB_deterioration_mg_g': 'mean_absB_allowance_mg_g',
        'signed_B_difference_mg_g': 'signed_B_allowance_mg_g',
        'relative_component_mg_g': 'relative_component_allowance_mg_g'}
    gain = [r['R_improvement_mg_g'] for r in ds]
    result = {'baseline': rs[0], 'deletion_count': len(ds),
        'deletion_gain_sign_counts': {'positive': sum(g > 0 for g in gain), 'zero': sum(g == 0 for g in gain), 'negative': sum(g < 0 for g in gain)},
        'all_deletion_point_gains_strictly_positive': all(g > 0 for g in gain),
        'all_deletion_allowance_lower_endpoints_strictly_positive': all(r['R_improvement_mg_g']-r['R_improvement_allowance_mg_g'] > 0 for r in ds),
        'deletion_ranges': {k: range_of([r[k] for r in ds]) for k in (*value_allowance, *value_allowance.values(),
            'relative_improvement', 'relative_improvement_lower_bound', 'definite_condition_wins', 'possible_condition_wins')},
        'baseline_plus_deletions_envelopes': {k: envelope(rs, k, u) for k, u in value_allowance.items()},
        'deletion_headroom_ranges': {k: range_of([r['headroom'][k] for r in ds]) for k in rs[0]['headroom']},
        'historical_budget_diagnostics': {
            'absolute_gain_points_at_least_0_10': sum(g >= .10 for g in gain),
            'absolute_gain_lower_endpoints_at_least_0_10': sum(r['R_improvement_mg_g']-r['R_improvement_allowance_mg_g'] >= .10 for r in ds),
            'relative_component_upper_at_most_zero': sum(r['relative_component_mg_g']+r['relative_component_allowance_mg_g'] <= 0 and not r['relative_denominator_guard'] for r in ds),
            'bias_upper_at_most_0_05': sum(r['mean_absB_deterioration_mg_g']+r['mean_absB_allowance_mg_g'] <= .05 for r in ds)},
        'replacement_historical_decisions': 'NONE'}
    decision = sensitivity_policy(rs, ref, panel)
    result['policy_sensitivity'] = {k: decision[k] for k in ('range_relation', 'contractual', 'resolution', 'interpretation', 'limitations')}
    return result, decision


def analyze(shots):
    public, private = {}, {}
    for panel, conditions in PANELS.items():
        arms = shots[panel]
        field = 'support_diagnostic' if panel == 'flow_stress' else 'full'
        baseline = reduce_scenario(arms, conditions, field=field)
        paired = {ref: [{'shot': c['shot'], 'condition': c['condition'],
                        **contrast(c[field], next(r[field] for r in arms[ref] if r['shot'] == c['shot']))}
                       for c in arms['S2']] for ref in REFS}
        private[panel] = {'paired_shots': paired, 'scenarios': [baseline]}
        public[panel] = {'baseline_comparisons': baseline['comparisons'],
            'paired_shot_sign_counts': {ref: {sign: sum(test(r['R_improvement_mg_g']) for r in rows)
                for sign, test in [('positive', lambda x: x > 0), ('zero', lambda x: x == 0), ('negative', lambda x: x < 0)]} for ref, rows in paired.items()}}
        if panel == 'flow_stress':
            public[panel]['deletions'] = 'NOT_PERFORMED_OR_AUTHORIZED; supported-window baseline retains all six shots'
            continue
        for shot in sorted(r['shot'] for r in arms['S2']):
            private[panel]['scenarios'].append(reduce_scenario(arms, conditions, deleted=shot))
        summaries = {}; policies = {}
        for ref in REFS:
            summaries[ref], policies[ref] = summarize_sensitivity(private[panel]['scenarios'], ref, panel)
        public[panel]['sensitivity'] = summaries
        public[panel]['arm_deletion_ranges'] = {a: {k: range_of([s['arms'][a]['balanced'][k] for s in private[panel]['scenarios'][1:]]) for k in METRICS} for a in ARMS}
        private[panel]['policy_records'] = policies
    return public, private


def variability(observed, support_rows=None):
    validate_windows(observed)
    si = index(support_rows, ('shot', 'fraction')) if support_rows is not None else None
    cells = []
    for panel, conditions in PANELS.items():
        for c in conditions:
            for f in FRACTIONS:
                rows = [r for r in observed if r['condition'] == c and r['fraction'] == f]
                valid = [r for r in rows if r['analyte_eligible'] and r['q'] is not None]
                values = spread([1000*r['q'] for r in valid])
                cells.append({'panel': panel, 'condition': c, 'fraction': f, 'observation_n': len(valid),
                    'scoring_support_n': sum(si[(r['shot'], f)]['supported'] for r in valid) if si is not None else None,
                    'concentration_units': 'mg/g', 'mean': values['mean'], 'sample_sd': values['sd'],
                    'sd_denominator': 'n-1', 'coordinate_units': 'kg',
                    'left_edge_range': range_of([r['b0'] for r in valid]),
                    'right_edge_range': range_of([r['b1'] for r in valid]),
                    'width_range': range_of([r['b1']-r['b0'] for r in valid]),
                    'unavailable': ([] if len(valid) >= 2 else ['sample SD needs two source-valid observations']) +
                                   ([] if si is not None else ['support crosswalk unavailable'])})
    return cells


def admit(directory, tracker):
    manifest = tracker.json(DOC/'INPUT_MANIFEST.json')
    for name, expected in manifest['repository_file_byte_sha256'].items():
        tracker.bytes(ROOT/name, expected)
    binding = tracker.json(HISTORY/'RESULT_BINDING.json')
    data, availability = {}, {}
    expected = manifest['input_byte_sha256']
    if any(expected[k] != binding['private_evidence_hashes'][k] for k in expected):
        raise IntegrityStop('CONTROLLING_BINDING_MISMATCH')
    for name, h in expected.items():
        path = directory/name
        if not path.exists() and name in ('scores.json', 'score_completion.json', 'score_receipt.json'):
            path = HISTORY/{'scores.json': 'RESULTS.json', 'score_completion.json': 'SCORE_COMPLETION.json',
                            'score_receipt.json': 'SCORE_RECEIPT.json'}[name]
        try:
            data[name] = tracker.json(path, h)
            availability[name] = {'status': 'ADMITTED', 'sha256': h}
        except (FileNotFoundError, IntegrityStop) as exc:
            availability[name] = {'status': 'UNAVAILABLE' if isinstance(exc, FileNotFoundError) else 'INTEGRITY_BLOCKED', 'artifact': name, 'reason': type(exc).__name__}
    try:
        freeze = tracker.json(directory/'freeze.json', manifest['historical_freeze_sha256'])
        if freeze['panels'] != {k: list(v) for k, v in PANELS.items()} or freeze['arms'] != list(ARMS) or freeze['primary_candidate'] != 'S2':
            raise IntegrityStop('FROZEN_POPULATION_MISMATCH')
        data['freeze.json'] = freeze
        availability['freeze.json'] = {'status': 'ADMITTED', 'sha256': manifest['historical_freeze_sha256']}
        for name in manifest['optional_freeze_members']:
            try:
                data[name] = tracker.json(directory/name, freeze['artifacts'][name])
                availability[name] = {'status': 'ADMITTED', 'sha256': freeze['artifacts'][name]}
            except (FileNotFoundError, IntegrityStop) as exc:
                availability[name] = {'status': 'UNAVAILABLE' if isinstance(exc, FileNotFoundError) else 'INTEGRITY_BLOCKED', 'reason': type(exc).__name__}
    except (FileNotFoundError, IntegrityStop) as exc:
        availability['freeze.json'] = {'status': 'UNAVAILABLE' if isinstance(exc, FileNotFoundError) else 'INTEGRITY_BLOCKED', 'reason': type(exc).__name__}
    if 'score_completion.json' in data and 'score_receipt.json' in data:
        completion, receipt = data['score_completion.json'], data['score_receipt.json']
        if (completion['status'] != 'COMPLETE' or completion['scientific_score_passes'] != 1 or
            any(completion[n.replace('.json', '_sha256')] != expected[n] for n in ('scores.json', 'shot_results.json', 'observed_suffix.json', 'score_receipt.json')) or
            receipt['freeze_sha256'] != manifest['historical_freeze_sha256'] or receipt['predictions_sha256'] != expected['predictions.json']):
            raise IntegrityStop('COMPLETION_BINDING_MISMATCH')
    for name, h in manifest['historical_model_file_sha256'].items():
        model = tracker.json(ROOT/name, h)
        arm = Path(name).stem
        if model['model_sha256'] != manifest['historical_model_content_sha256'][arm]:
            raise IntegrityStop('MODEL_CONTENT_IDENTITY_MISMATCH')
    return data, availability, manifest


def run(directory, output):
    directory = Path(directory).resolve()
    out = private_output(output, (directory,))
    tracker = Inputs()
    data, available, manifest = admit(directory, tracker)
    public = {'task': TASK, 'classification': ['G1', 'NO_GOVERNING_PHYSICS_CHANGE', 'RESEARCH_ONLY', 'RETROSPECTIVE', 'TARGET_EXPOSED', 'SOURCE_INTERNAL', 'EXPLORATORY'],
        'availability': available, 'manifest_sha256': sha((DOC/'INPUT_MANIFEST.json').read_bytes()),
        'protocol_sha256': sha((DOC/'PROTOCOL.md').read_bytes()), 'implementation_sha256': sha(Path(__file__).read_bytes()),
        'policy_identity': manifest['policy_acceptance'], 'unknown_uncertainty_components': list(UNKNOWN),
        'physical_validation': 'NOT_ESTABLISHED', 'merge_authorized': False, 'production_adoption_authorized': False,
        'new_model_fits': 0, 'new_predictions': 0, 'new_native_simulations': 0, 'native_ewp_runs': 0,
        'historical_score_lifecycle_invocations': 0, 'historical_results_unchanged': True, 'automatic_successor': False,
        'rights': 'Source-derived aggregates: CC-BY-NC-3.0; Pannusch/Schmieder; Mendeley 10.17632/y2tz67f6ry.1. First-party software separately licensed.',
        'practical_incremental_value': 'UNESTABLISHED; no independently justified intended-use criterion supplied',
        'component_completion': {k: 'UNAVAILABLE' for k in ('shot_reproduction', 'fraction_reconstruction', 'primary_sensitivity', 'temperature_sensitivity', 'observed_variability')}}
    private = {'input_locator': str(directory), 'manifest': manifest, 'arithmetic_discrepancies': []}
    shots = None
    if all(n in data for n in ('shot_results.json', 'scores.json', 'score_completion.json', 'score_receipt.json')):
        try:
            shots = validate_shots(data['shot_results.json'])
            reproduced = reproduce(shots)
            original = {k: data['scores.json'][k] for k in reproduced}
            differences = arithmetic_differences(reproduced, original)
            private['arithmetic_discrepancies'] = differences
            public['historical_reproduction'] = {'original': original, 'reproduced': reproduced,
                'nonzero_arithmetic_discrepancies': len(differences),
                'maximum_absolute_discrepancy': max((r['absolute_difference'] for r in differences), default=0.),
                'changed_decisions': 0}
            public['feature_extrapolation'] = data['scores.json']['feature_extrapolation']
            public['analysis'], private['analysis'] = analyze(shots)
            private['retained_shot_results'] = shots
            for key in ('shot_reproduction', 'primary_sensitivity', 'temperature_sensitivity'):
                public['component_completion'][key] = 'COMPLETE'
        except (ValueError, KeyError) as exc:
            shots = None
            public['core_integrity_problem'] = str(exc)
            for key in ('shot_reproduction', 'primary_sensitivity', 'temperature_sensitivity'):
                public['component_completion'][key] = 'INTEGRITY_BLOCKED'
    observed, predictions, queries = (data.get(n) for n in ('observed_suffix.json', 'predictions.json', 'queries.json'))
    if observed is not None:
        try:
            validate_windows(observed, shots)
            crosswalk(observed, queries, data.get('coordinates.json'))
            support = queries
            if support is not None:
                validate_windows(support, shots)
            if predictions is not None:
                oi, pi = window_pairing(observed, predictions, queries, shots)
                support = predictions['S2']
                private['window_crosswalk'] = [{'observation': r, 'predictions': {a: pi[a][k] for a in ARMS},
                    'query': next((q for q in queries or [] if (q['shot'], q['fraction']) == k), None)} for k, r in oi.items()]
                public['unsupported_slot'] = [{k: p[k] for k in ('condition', 'shot', 'fraction', 'reason')} for p in support if not p['supported']]
                if shots is not None:
                    reconstructed = reconstruct(observed, predictions, shots)
                    diffs = arithmetic_differences(reconstructed, shots, 'fraction_reconstruction')
                    private['fraction_arithmetic_discrepancies'] = diffs
                    private['reconstructed_shots'] = reconstructed
                    public['fraction_reconstruction'] = {'nonzero_arithmetic_discrepancies': len(diffs),
                        'maximum_absolute_discrepancy': max((r['absolute_difference'] for r in diffs), default=0.),
                        'windows_checked': 96, 'arms_checked': 4, 'concentration_source': 'retained caffeine_mg_g',
                        'allowance_source': 'retained total allowance_kg, includes coordinate term once'}
                    public['component_completion']['fraction_reconstruction'] = 'COMPLETE'
            public['observed_variability'] = variability(observed, support)
            public['component_completion']['observed_variability'] = 'COMPLETE'
            private['retained_observations'] = observed
        except (ValueError, KeyError) as exc:
            public['fraction_integrity_problem'] = str(exc)
            public['component_completion']['fraction_reconstruction'] = 'INTEGRITY_BLOCKED'
            # Independently admitted observations remain available despite a prediction problem.
            try:
                public['observed_variability'] = variability(observed)
                public['component_completion']['observed_variability'] = 'PARTIAL_SUPPORT_CROSSWALK_UNAVAILABLE'
            except (ValueError, KeyError):
                public['component_completion']['observed_variability'] = 'INTEGRITY_BLOCKED'
    private['coordinates'] = data.get('coordinates.json')
    tracker.recheck()
    locators = {str(p): h for p, h in tracker.identities.items()}
    write(out/'INPUT_LOCATORS.json', locators)
    write(out/'PRIVATE_RESULTS.json', private)
    public['private_bindings'] = {n: sha((out/n).read_bytes()) for n in ('INPUT_LOCATORS.json', 'PRIVATE_RESULTS.json')}
    public['input_preservation'] = {'files_verified_before_and_after': len(locators), 'unchanged': True}
    public['scientific_result_disposition'] = ('HISTORICAL_DECISIONS_PRESERVED_WITH_FINITE_COHORT_SENSITIVITY' if public['component_completion']['shot_reproduction'] == 'COMPLETE' else 'INPUT_LIMITED')
    public['validation_framework_disposition'] = 'CASE_LOCAL_REDUCTION; INDEPENDENT_REVIEW_AND_QA_REPORTED_SEPARATELY'
    public['claim_ceiling'] = 'Descriptive retained-cohort influence conditional on frozen fits; no new-condition robustness, confidence interval, practical-value or physical-validation claim'
    write(out/'RESULTS.json', public)
    write(out/'completion.json', {'task': TASK, 'status': 'COMPLETE', 'results_sha256': sha((out/'RESULTS.json').read_bytes()), **public['private_bindings']})
    return public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--retained', type=Path, help='explicit retained caffeine run directory')
    parser.add_argument('--evidence-root', type=Path, help='configured collection override')
    parser.add_argument('--output', type=Path, required=True, help='new directory outside Git and source')
    args = parser.parse_args()
    directory = args.retained
    if directory is None:
        from tools.inventory_local_corpus import resolve_roots
        roots, _ = resolve_roots(args.evidence_root)
        if 'collection' not in roots:
            parser.error('configured collection or --retained required')
        directory = Path(roots['collection'])/'caffeine-delivery-001-evidence/run-001'
    result = run(directory, args.output)
    print(json.dumps(result['component_completion'], sort_keys=True))


if __name__ == '__main__':
    main()

"""Bounded offline 5CQA retained-evidence arithmetic. No historical runner imports.

Only this case's authenticated JSON is reduced. Detailed outputs are private;
the public projection contains baseline aggregates and whole-family summaries.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

import numpy as np

from puckworks.validation import decision_resolution as dr

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/val_case_5cqa_decision_resolution_001'
HISTORY = ROOT / 'docs/analysis/sci_md_5cqa_assay_002'
TASK = 'VAL-CASE-5CQA-DECISION-RESOLUTION-001'
OLD_TASK = 'SCI-MD-5CQA-ASSAY-002'
ARMS = ('L1M', 'L2M', 'L12')
PANELS = {'primary': ('PRED-C01', 'PRED-C02', 'PRED-C05', 'PRED-C06'),
          'temperature_stress': ('PRED-C03', 'PRED-C04'),
          'flow_stress': ('PRED-C07', 'PRED-C08')}
PAIRS = (('L12', 'L1M'), ('L12', 'L2M'), ('L2M', 'L1M'))
FRACTIONS = (3, 5, 7, 10)
METRICS = ('R_mg_g', 'B_mg_g', 'absB_mg_g', 'R_allowance_mg_g',
           'B_allowance_mg_g', 'absB_allowance_mg_g')
UNKNOWN = ('training_and_model_selection', 'assay_and_calibration',
           'input_measurement', 'new_condition_and_source_transfer')
CB = 'squared_mean_shot_error_contribution_mg_g'
CV = 'within_shot_centered_residual_variation_contribution_mg_g'
FALLBACK = {'scores.json': 'RESULTS.json', 'score_completion.json': 'SCORE_COMPLETION.json',
            'score_receipt.json': 'SCORE_RECEIPT.json', 'freeze.json': 'FREEZE.json'}


class IntegrityError(ValueError):
    """Affected evidence cannot support empirical reliance."""


def require(ok, reason):
    if not ok:
        raise IntegrityError(reason)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def parse(data):
    def unique(pairs):
        result = dict(pairs)
        require(len(result) == len(pairs), 'DUPLICATE_JSON_KEY')
        return result
    return json.loads(data, object_pairs_hook=unique, parse_float=lambda x: finite(float(x)),
                      parse_constant=lambda x: (_ for _ in ()).throw(IntegrityError('NONFINITE_JSON')))


def read(path):
    return parse(Path(path).read_bytes())


def write(path, data):
    with Path(path).open('x') as f:
        f.write(json.dumps(data, sort_keys=True, indent=2, allow_nan=False) + '\n')


def finite(x, *, minimum=None):
    require(type(x) in (int, float) and math.isfinite(x), 'FINITE_REAL_REQUIRED')
    require(minimum is None or x >= minimum, 'VALUE_BELOW_MINIMUM')
    return x


def tolerance(x):
    return 512 * math.ulp(max(1., abs(x)))


def differences(actual, expected, path='result'):
    """Record all differences; never use this arithmetic tolerance in decisions."""
    result = []
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), 'KEY_MISMATCH:' + path)
        for k in expected:
            result += differences(actual[k], expected[k], path + '.' + k)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), 'LENGTH_MISMATCH:' + path)
        for i, (a, e) in enumerate(zip(actual, expected)):
            result += differences(a, e, path + '.' + str(i))
    elif type(expected) in (float, int) and type(actual) in (float, int):
        finite(actual); finite(expected)
        if actual != expected:
            result.append({'field': path, 'actual': actual, 'expected': expected,
                           'absolute_difference': abs(actual - expected),
                           'within_tolerance': abs(actual - expected) <= tolerance(expected),
                           'kind': 'arithmetic'})
    elif actual != expected:
        result.append({'field': path, 'actual': actual, 'expected': expected, 'kind': 'decision_or_identity'})
    return result


def reconciliation_summary(diffs):
    decisions = [d for d in diffs if d['kind'] != 'arithmetic']
    return {'maximum_absolute_discrepancy': max((d['absolute_difference'] for d in diffs
                                                if d['kind'] == 'arithmetic'), default=0.),
            'nonzero_arithmetic_discrepancies': sum(d['kind'] == 'arithmetic' for d in diffs),
            'decision_discrepancies': decisions,
            'pass': not decisions and all(d.get('within_tolerance', False) for d in diffs)}


def upper(v, u, limit):
    if v is None or u is None:
        return 'INCOMPLETE_SUPPORT'
    return 'PASS' if v + u <= limit else 'FAIL' if v - u > limit else 'UNRESOLVED'


def conjunction(values):
    values = tuple(values)
    if 'FAIL' in values:
        return 'FAIL'
    if values and all(v == 'PASS' for v in values):
        return 'PASS'
    return 'INCOMPLETE_SUPPORT' if 'INCOMPLETE_SUPPORT' in values else 'UNRESOLVED'


def mean_metrics(values):
    if not values or any(v is None for v in values):
        return None
    return {k: float(np.mean([v[k] for v in values])) for k in METRICS}


def metric_bounds(v):
    if v is None:
        return None
    return {k: {'lower': v[k] - v[u] if k == 'B_mg_g' else max(0., v[k] - v[u]),
                'upper': v[k] + v[u]}
            for k, u in zip(METRICS[:3], METRICS[3:])}


def members(conditions):
    return {f'PRED-E{c[-2:]}-R{r}': c for c in conditions for r in (1, 2, 3)}


def validate_metric(v, windows):
    require(isinstance(v, dict) and set(METRICS) <= v.keys(), 'METRIC_SCHEMA')
    for k in METRICS:
        finite(v[k], minimum=None if k == 'B_mg_g' else 0.)
    require(v['windows'] == windows and type(v['windows']) is int, 'WINDOW_COUNT')
    require(v['absB_mg_g'] == abs(v['B_mg_g']), 'ABS_BEFORE_AVERAGING')
    require(v['B_allowance_mg_g'] == v['absB_allowance_mg_g'], 'BIAS_ALLOWANCE_MISMATCH')
    for k in ('assayed_beverage_kg', 'observed_assayed_five_cqa_kg', 'predicted_assayed_five_cqa_kg'):
        finite(v[k], minimum=0.)
    require(v['assayed_beverage_kg'] > 0, 'POSITIVE_MEASURED_MASS')
    shot_components(v)


def validate_shots(data):
    require(set(data) == set(PANELS), 'PANEL_MEMBERSHIP')
    for panel, cs in PANELS.items():
        require(set(data[panel]) == set(ARMS), 'ARM_MEMBERSHIP')
        expected = members(cs)
        for arm in ARMS:
            rows = data[panel][arm]
            require(len(rows) == len(expected) and {r['shot']: r['condition'] for r in rows} == expected,
                    'EXACT_SHOT_CONDITION_MEMBERSHIP')
            for r in rows:
                require(set(r) == {'shot', 'condition', 'full', 'bounds', 'supported_subset_diagnostic', 'coverage'},
                        'SHOT_SCHEMA')
                n = 3 if r['shot'] == 'PRED-E07-R1' else 4
                require(r['coverage'] == {'intended': 4, 'supported': n, 'qualified': n}, 'SUPPORT_MISMATCH')
                require(all(type(v) is int for v in r['coverage'].values()), 'INTEGER_SUPPORT_COUNTS')
                require((r['full'] is None) == (n == 3), 'FULL_SCOPE_MISMATCH')
                validate_metric(r['supported_subset_diagnostic'], n)
                if n == 4:
                    validate_metric(r['full'], 4)
                    require(r['full'] == r['supported_subset_diagnostic'], 'FULL_SUBSET_MISMATCH')
                require(not differences(r['bounds'], metric_bounds(r['full'])), 'SHOT_BOUND_MISMATCH')
    return data


def condition_result(rows, *, original=True):
    full = [r['full'] for r in rows]
    v = mean_metrics(full)
    denominator = 3 if original else len(rows)
    lower = {k: sum(max(0., x[k] - x[u]) for x in full if x is not None) / denominator
             for k, u in (('R_mg_g', 'R_allowance_mg_g'), ('absB_mg_g', 'absB_allowance_mg_g'))}
    adequate = (conjunction((upper(v['R_mg_g'], v['R_allowance_mg_g'], .25),
                            upper(v['absB_mg_g'], v['absB_allowance_mg_g'], .125))) if v else
                'FAIL' if lower['R_mg_g'] > .25 or lower['absB_mg_g'] > .125 else 'INCOMPLETE_SUPPORT')
    return {'full_scope_metrics': v, 'bounds': metric_bounds(v),
            'supported_subset_diagnostic': mean_metrics([r['supported_subset_diagnostic'] for r in rows]),
            'adequacy': adequate, 'original_shots': 3, 'original_slots': 12,
            'complete_shots': sum(x is not None for x in full),
            'supported_slots': sum(r['coverage']['supported'] for r in rows),
            'qualified_slots': sum(r['coverage']['qualified'] for r in rows),
            'complete_shot_full_condition_lower_bounds': lower}


def aggregate(rows, conditions, deleted=None):
    require(deleted is None or sum(r['shot'] == deleted for r in rows) == 1, 'DELETION_MEMBERSHIP')
    ci = {}
    for c in conditions:
        kept = [r for r in rows if r['condition'] == c and r['shot'] != deleted]
        require(len(kept) == (2 if deleted in members((c,)) else 3), 'UNEXPECTED_MISSING_SHOT')
        ci[c] = condition_result(kept, original=deleted is None)
    v = mean_metrics([r['full_scope_metrics'] for r in ci.values()])
    return {'conditions': ci, 'original_conditions': len(conditions), 'original_shots': 3 * len(conditions),
            'original_slots': 12 * len(conditions), 'full_scope_metrics': v, 'bounds': metric_bounds(v),
            'supported_subset_diagnostic': mean_metrics([r['supported_subset_diagnostic'] for r in ci.values()]),
            'adequacy': conjunction(r['adequacy'] for r in ci.values()),
            'complete_scope': all(r['full_scope_metrics'] is not None for r in ci.values())}


def comparison(candidate, reference, *, primary=True):
    if not candidate['complete_scope'] or not reference['complete_scope']:
        return {'status': 'INCOMPLETE_SUPPORT', 'reason': 'ALL_ORIGINAL_PRIMARY_SLOTS_REQUIRED'}
    c, r = candidate['full_scope_metrics'], reference['full_scope_metrics']
    g, u = r['R_mg_g'] - c['R_mg_g'], r['R_allowance_mg_g'] + c['R_allowance_mg_g']
    deterioration = c['absB_mg_g'] - r['absB_mg_g']
    du = c['absB_allowance_mg_g'] + r['absB_allowance_mg_g']
    wins = possible = 0
    for key, row in candidate['conditions'].items():
        a, b = row['full_scope_metrics'], reference['conditions'][key]['full_scope_metrics']
        wins += a['R_mg_g'] + a['R_allowance_mg_g'] < b['R_mg_g'] - b['R_allowance_mg_g']
        possible += a['R_mg_g'] - a['R_allowance_mg_g'] < b['R_mg_g'] + b['R_allowance_mg_g']
    components = {'absolute_gain': upper(-g, u, -.05),
                  'relative_gain': upper(c['R_mg_g'] - .85 * r['R_mg_g'],
                                         c['R_allowance_mg_g'] + .85 * r['R_allowance_mg_g'], 0.),
                  'abs_bias_deterioration': upper(deterioration, du, .025)}
    if primary:
        components['condition_wins'] = 'PASS' if wins >= 3 else 'FAIL' if possible < 3 else 'UNRESOLVED'
    lower = r['R_mg_g'] - r['R_allowance_mg_g']
    status = conjunction(components.values()) if primary else 'SECONDARY_DIAGNOSTIC'
    return {'status': conjunction((status, candidate['adequacy'])) if primary else status,
            'gain_status': status, 'candidate_adequacy': candidate['adequacy'], 'components': components,
            'R_improvement_mg_g': g, 'R_improvement_bounds': [g - u, g + u],
            'relative_improvement': g / r['R_mg_g'] if r['R_mg_g'] > 0 else None,
            'relative_improvement_lower_bound': 1 - (c['R_mg_g'] + c['R_allowance_mg_g']) / lower if lower > 0 else None,
            'definite_condition_wins': wins, 'possible_condition_wins': possible,
            'mean_absB_deterioration_mg_g': deterioration,
            'mean_absB_deterioration_bounds': [deterioration - du, deterioration + du]}


def reproduce(shots):
    panels = {p: {a: aggregate(shots[p][a], cs) for a in ARMS} for p, cs in PANELS.items()}
    primary = panels['primary']
    adequacy = {a: primary[a]['adequacy'] for a in ARMS}
    comparisons = {a + '_vs_' + b: comparison(primary[a], primary[b]) for a, b in PAIRS}
    # This addendum admits the single declared completed inadequate case only.
    require(all(x == 'FAIL' for x in adequacy.values()), 'HISTORICAL_INADEQUACY_NOT_REPRODUCED')
    return {'panels': panels, 'adequacy_by_arm': adequacy, 'pairwise_complexity': comparisons,
            'disposition': 'TESTED_EARLY_ASSAY_FAMILIES_INADEQUATE', 'blocker': None,
            'adequate_arms': [], 'adequate_single_assay_contracts': [], 'minimum_tested_assay_count': None,
            'single_assay_placement_earned': False, 'two_assay_route_earned': False,
            'primary_complete_qualified_support': all(v['complete_scope'] for v in primary.values())}


def down(x):
    return math.nextafter(x, -math.inf)


def up(x):
    return math.nextafter(x, math.inf)


def add(a, b):
    return [down(a[0] + b[0]), up(a[1] + b[1])]


def subtract(a, b):
    return [down(a[0] - b[1]), up(a[1] - b[0])]


def square(a):
    values = (a[0] * a[0], a[1] * a[1])
    return [0. if a[0] <= 0 <= a[1] else max(0., down(min(values))), up(max(values))]


def divide(a, b):
    if b[0] <= 0:
        return None
    values = [x / y for x in a for y in b]
    return [down(min(values)), up(max(values))]


def interval(v, u, *, nonnegative=False):
    if u == 0 and v == 0 and nonnegative:
        return [0., 0.]
    lo, hi = down(v - u), up(v + u)
    return [max(0., lo) if nonnegative else lo, hi]


def mean_interval(values):
    if any(v is None for v in values):
        return None
    total = [0., 0.]
    for v in values:
        total = add(total, v)
    return divide(total, [len(values), len(values)])


def shot_components(v):
    r, b = v['R_mg_g'], v['B_mg_g']
    finite(r, minimum=0.); finite(b)
    require(abs(b) - r <= 16 * math.ulp(max(r, abs(b))), 'MATERIALLY_NEGATIVE_POINT_VARIATION')
    r2, b2 = r * r, b * b
    variation = r2 - b2
    eps = 16 * math.ulp(max(r2, b2))
    require(variation >= -eps, 'MATERIALLY_NEGATIVE_POINT_VARIATION')
    ri = interval(r, v['R_allowance_mg_g'], nonnegative=True)
    bi = interval(b, v['B_allowance_mg_g'])
    raw = subtract(square(ri), square(bi))
    require(raw[1] >= 0, 'EMPTY_NONNEGATIVE_VARIATION_ENCLOSURE')
    return {'R2': r2, 'B2': b2, 'V': max(0., variation), 'R_bounds': ri,
            'B2_bounds': square(bi), 'V_unconstrained_bounds': raw,
            'V_bounds': [max(0., raw[0]), raw[1]], 'negative_roundoff_clamped': variation < 0}


def paired_shot(candidate, reference):
    c, r = shot_components(candidate), shot_components(reference)
    denominator = candidate['R_mg_g'] + reference['R_mg_g']
    di = add(c['R_bounds'], r['R_bounds'])
    if denominator == 0:
        require(c['B2'] == r['B2'] == c['V'] == r['V'] == 0, 'INCONSISTENT_ZERO_DENOMINATOR')
        cb = cv = 0.
    else:
        cb, cv = (r['B2'] - c['B2']) / denominator, (r['V'] - c['V']) / denominator
    exact_zero = c['R_bounds'] == r['R_bounds'] == [0., 0.]
    cbi = [0., 0.] if exact_zero else divide(subtract(r['B2_bounds'], c['B2_bounds']), di)
    cvi = [0., 0.] if exact_zero else divide(subtract(r['V_bounds'], c['V_bounds']), di)
    gain = reference['R_mg_g'] - candidate['R_mg_g']
    require(abs(cb + cv - gain) <= tolerance(gain), 'PAIRED_DECOMPOSITION_IDENTITY')
    return {CB: cb, CV: cv, CB + '_bounds': cbi, CV + '_bounds': cvi,
            'gain': gain, 'identity_discrepancy': abs(cb + cv - gain),
            'candidate': c, 'reference': r}


def nested(values, conditions, key, *, bounds=False):
    reducer = mean_interval if bounds else lambda xs: float(np.mean(xs))
    return reducer([reducer([r[key] for r in values if r['condition'] == c]) for c in conditions])


def scenario(arms, panel, deleted=None):
    cs = PANELS[panel]
    reduced = {a: aggregate(arms[a], cs, deleted) for a in ARMS}
    ids = sorted(s for s in members(cs) if s != deleted)
    output = {'deleted': deleted, 'retained_members': ids, 'original_shots': 3 * len(cs),
              'actual_shots_per_arm': len(ids), 'scored_windows_per_arm': 4 * len(ids),
              'arms': reduced, 'comparisons': {}}
    indexes = {a: {r['shot']: r for r in arms[a]} for a in ARMS}
    for a, b in PAIRS:
        rows = [dict(paired_shot(indexes[a][s]['full'], indexes[b][s]['full']),
                     shot=s, condition=indexes[a][s]['condition']) for s in ids]
        comp = comparison(reduced[a], reduced[b], primary=panel == 'primary')
        c, r = reduced[a]['full_scope_metrics'], reduced[b]['full_scope_metrics']
        comp['R_improvement_allowance_mg_g'] = c['R_allowance_mg_g'] + r['R_allowance_mg_g']
        comp['signed_bias_change_mg_g'] = c['B_mg_g'] - r['B_mg_g']
        comp['absolute_gain_headroom_mg_g'] = comp['R_improvement_mg_g'] - .05
        comp['relative_component_headroom_mg_g'] = .85 * r['R_mg_g'] - c['R_mg_g']
        comp['A_budget_headroom_mg_g'] = .025 - comp['mean_absB_deterioration_mg_g']
        comp['signed_bias_change_bounds'] = subtract(interval(c['B_mg_g'], c['B_allowance_mg_g']),
                                                    interval(r['B_mg_g'], r['B_allowance_mg_g']))
        # Direct enclosure also encloses reduction arithmetic; historical bounds above stay exact.
        shot_net = [dict(x, net_bounds=subtract(x['reference']['R_bounds'], x['candidate']['R_bounds'])) for x in rows]
        comp['direct_gain_enclosure'] = nested(shot_net, cs, 'net_bounds', bounds=True)
        for key in (CB, CV):
            comp[key] = nested(rows, cs, key)
            comp[key + '_bounds'] = nested(rows, cs, key + '_bounds', bounds=True)
        comp['decomposition_identity_discrepancy'] = abs(comp[CB] + comp[CV] - comp['R_improvement_mg_g'])
        require(comp['decomposition_identity_discrepancy'] <= tolerance(comp['R_improvement_mg_g']),
                'AGGREGATED_DECOMPOSITION_IDENTITY')
        comp['condition_contrasts'] = {}
        for condition in cs:
            ac, bc = reduced[a]['conditions'][condition]['full_scope_metrics'], reduced[b]['conditions'][condition]['full_scope_metrics']
            subset = [x for x in rows if x['condition'] == condition]
            gain, u = bc['R_mg_g'] - ac['R_mg_g'], bc['R_allowance_mg_g'] + ac['R_allowance_mg_g']
            comp['condition_contrasts'][condition] = {'gain_mg_g': gain, 'gain_bounds': [gain-u, gain+u],
                'definite_win': ac['R_mg_g'] + ac['R_allowance_mg_g'] < bc['R_mg_g'] - bc['R_allowance_mg_g'],
                'possible_win': ac['R_mg_g'] - ac['R_allowance_mg_g'] < bc['R_mg_g'] + bc['R_allowance_mg_g'],
                'signed_bias_change_mg_g': ac['B_mg_g'] - bc['B_mg_g'],
                'A_deterioration_mg_g': ac['absB_mg_g'] - bc['absB_mg_g'],
                **{k: float(np.mean([x[k] for x in subset])) for k in (CB, CV)},
                **{k + '_bounds': mean_interval([x[k + '_bounds'] for x in subset]) for k in (CB, CV)}}
        comp['paired_shots'] = rows
        output['comparisons'][a + '_vs_' + b] = comp
    return output


def extent(values):
    return [min(values), max(values)] if all(x is not None for x in values) else None


def signs(values, intervals):
    return {'point_positive': sum(x > 0 for x in values), 'point_zero': sum(x == 0 for x in values),
            'point_negative': sum(x < 0 for x in values),
            'lower_positive': sum(x is not None and x[0] > 0 for x in intervals),
            'upper_negative': sum(x is not None and x[1] < 0 for x in intervals),
            'bounds_unresolved': sum(x is None for x in intervals)}


def policy_interpretation(panel, name, records, *, baseline=False):
    # Scenarios are repeated evaluations of one cohort, not independent shots.
    ids = ('baseline',) if baseline else tuple('omit:' + x['deleted'] for x in records)
    scope = dr.Scope('balanced paired RMSE gain', 'mg/g', panel,
                     'baseline retained cohort' if baseline else 'exact finite single-physical-shot deletion family',
                     'equal shots within condition; equal conditions; paired complete trajectories',
                     name + '; frozen fitted parameters and retained measured inputs',
                     tuple((s, panel + ':same_original_cohort') for s in ids),
                     'all declared scenarios; original population and actual masks retained privately')
    requirement = dr.Requirement(name + ':' + panel, True, 'increment', scope, '>', 0.,
        'diagnostic sign of observed comparative gain', 'algebraic zero; not a practical-value margin',
        'approved', 'applicable_bound', ('retained_numerical_allowances',),
        ('No practical value, population robustness, confidence coverage or adoption claim.',), name.split('_vs_')[1])
    kind = 'allowance' if baseline else 'sensitivity'
    basis = dr.Basis(kind, scope, 'Outward arithmetic on retained R allowances' if baseline else
        'Extrema of exactly the declared paired physical-shot deletions, each with its own retained allowance',
        ('retained_numerical_allowances',) if baseline else (),
        ('Frozen fits and measured inputs; historical allowance interpretation retained.',),
        () if baseline else ids)
    rows = [r['comparisons'][name] for r in records]
    lo = min(r['direct_gain_enclosure'][0] for r in rows)
    hi = max(r['direct_gain_enclosure'][1] for r in rows)
    evidence = dr.Evidence('bound' if baseline else 'sensitivity', scope, basis, scope.members,
        dr.Quality(True, True, True, True, 'Case-local authentication and arithmetic checks passed.'), UNKNOWN,
        point=rows[0]['R_improvement_mg_g'] if baseline else None, interval=dr.Interval(lo, hi))
    return asdict(dr.evaluate(requirement, evidence))


def summarize_deletions(records, name):
    rows = [s['comparisons'][name] for s in records]
    scalar = ('R_improvement_mg_g', 'R_improvement_allowance_mg_g', 'relative_improvement',
              'relative_improvement_lower_bound', 'signed_bias_change_mg_g',
              'mean_absB_deterioration_mg_g', 'definite_condition_wins', 'possible_condition_wins',
              'absolute_gain_headroom_mg_g', 'relative_component_headroom_mg_g', 'A_budget_headroom_mg_g', CB, CV)
    bounds = ('direct_gain_enclosure', 'signed_bias_change_bounds', 'mean_absB_deterioration_bounds',
              CB + '_bounds', CV + '_bounds')
    return {'scenarios': len(records), 'ranges': {k: extent([r[k] for r in rows]) for k in scalar},
            'numerical_envelopes': {k: [min(r[k][0] for r in rows), max(r[k][1] for r in rows)]
                                   if all(r[k] is not None for r in rows) else None for k in bounds},
            'sign_counts': {k: signs([r[k] for r in rows], [r[b] for r in rows])
                            for k, b in (('R_improvement_mg_g', 'direct_gain_enclosure'),
                                         (CB, CB + '_bounds'), (CV, CV + '_bounds'))},
            'component_status_counts': {k: dict(Counter(r['components'][k] for r in rows)) for k in rows[0]['components']},
            'candidate_adequacy_counts': dict(Counter(r['candidate_adequacy'] for r in rows)),
            'gain_status_counts': dict(Counter(r['gain_status'] for r in rows)),
            'final_status_counts': dict(Counter(r['status'] for r in rows)),
            'maximum_decomposition_identity_discrepancy': max(r['decomposition_identity_discrepancy'] for r in rows)}


def analyze(shots):
    public, private = {}, {}
    max_identity = 0.
    for panel in ('primary', 'temperature_stress'):
        cs = PANELS[panel]
        baseline = scenario(shots[panel], panel)
        deletions = [scenario(shots[panel], panel, s) for s in sorted(members(cs))]
        # Independent algebraic identity uses baseline per-shot contrasts only.
        for deletion in deletions:
            for name, base in baseline['comparisons'].items():
                s = next(r for r in base['paired_shots'] if r['shot'] == deletion['deleted'])
                condition = [r for r in base['paired_shots'] if r['condition'] == s['condition']]
                for key, shot_key in (('R_improvement_mg_g', 'gain'), (CB, CB), (CV, CV)):
                    expected = base[key] + (float(np.mean([r[shot_key] for r in condition])) - s[shot_key]) / (2 * len(cs))
                    error = abs(deletion['comparisons'][name][key] - expected)
                    max_identity = max(error, max_identity)
                    require(error <= tolerance(expected), 'INDEPENDENT_DELETION_IDENTITY')
        private[panel] = {'baseline': baseline, 'deletions': deletions, 'policy': {}}
        public[panel] = {'original_shots': 3 * len(cs), 'original_slots': 12 * len(cs),
            'actual_shots_per_deletion': 3 * len(cs) - 1, 'actual_windows_per_deletion_per_arm': 12 * len(cs) - 4,
            'arm_adequacy_counts_over_deletions': {a: dict(Counter(s['arms'][a]['adequacy'] for s in deletions)) for a in ARMS},
            'baseline': {}, 'deletions': {}}
        for name, comp in baseline['comparisons'].items():
            public[panel]['baseline'][name] = {k: v for k, v in comp.items() if k != 'paired_shots'}
            public[panel]['deletions'][name] = summarize_deletions(deletions, name)
            for label, records, is_baseline in (('baseline', [baseline], True), ('deletions', deletions, False)):
                decision = policy_interpretation(panel, name, records, baseline=is_baseline)
                private[panel]['policy'][name + ':' + label] = decision
                public[panel][label][name]['policy_interpretation'] = {k: decision[k] for k in
                    ('point_relation', 'range_relation', 'contractual', 'resolution', 'interpretation', 'limitations')}
                public[panel][label][name]['policy_interpretation'].update(
                    requirement='Diagnostic balanced RMSE gain > 0 mg/g; separate from historical material-value gate',
                    evidence_kind='bound' if is_baseline else 'sensitivity',
                    evidence_scope='original retained cohort' if is_baseline else f'exact {len(deletions)}-scenario deletion family',
                    historical_acceptance_unchanged=True)
    return public, private, max_identity


def window_index(rows):
    expected = members(tuple(c for cs in PANELS.values() for c in cs))
    index = {(r['shot'], r['fraction']): r for r in rows}
    require(len(rows) == len(index) == 96 and set(index) == {(s, f) for s in expected for f in FRACTIONS},
            'EXACT_96_WINDOW_MEMBERSHIP')
    for (s, f), r in index.items():
        require(type(f) is int, 'INTEGER_FRACTION_IDENTITY')
        require(r['condition'] == expected[s] and r['analyte'] == '5CQA'
                and r['campaign'] == 'PREDICTION_2022_03', 'WINDOW_IDENTITY')
        supported = (s, f) != ('PRED-E07-R1', 10)
        require(type(r['supported']) is bool and r['supported'] == supported, 'WINDOW_SUPPORT')
        require(r['reason'] == ('' if supported else 'OUTSIDE_COMMON_TRAINING_MASS_DOMAIN'), 'SUPPORT_REASON')
        require(r['analyte_eligible'] is True, 'ANALYTE_ELIGIBILITY')
        for k in ('b0', 'b1', 'mass_kg'):
            finite(r[k], minimum=0.)
        require(r['mass_kg'] > 0 and r['b1'] > r['b0'], 'POSITIVE_COORDINATES')
        require(abs(r['b1'] - r['b0'] - r['mass_kg']) <= tolerance(r['mass_kg']), 'MEASURED_COORDINATE_WIDTH')
    return index


def prediction_indexes(predictions):
    require(set(predictions) == set(ARMS), 'PREDICTION_ARM_MEMBERSHIP')
    result = {a: window_index(predictions[a]) for a in ARMS}
    for arm, index in result.items():
        for key, r in index.items():
            require(r['numerical_qualified'] is r['supported'], 'PREDICTION_QUALIFICATION')
            if r['supported']:
                require(r['species'] == '5CQA', 'PREDICTION_SPECIES')
                finite(r['five_cqa_mg_g'], minimum=0.)
                finite(r['allowance_kg'], minimum=0.)
                finite(r['coordinate_allowance_kg'], minimum=0.)
                require(r['coordinate_allowance_kg'] <= r['allowance_kg'], 'COORDINATE_ALLOWANCE_INCLUDED')
                displacement = abs(r['integration_start_kg'] - r['b0'])
                require(displacement == 0 or (r['fraction'] == 3 and
                    displacement <= 4 * max(math.ulp(r['b0']), math.ulp(r['integration_start_kg']))),
                    'ANCHOR_ADJUSTMENT_SCOPE')
                require(r['coordinate_allowance_kg'] >= 2 * displacement, 'ANCHOR_ALLOWANCE')
                require(r['start_kg'] == r['integration_start_kg'] and r['end_kg'] == r['b1'], 'INTEGRATION_COORDINATES')
                require(['concentration_display', 'mg/g'] in r['units'] and ['beverage', 'kg'] in r['units'], 'PREDICTION_UNITS')
            else:
                require(r['five_cqa_mg_g'] is None and r['allowance_kg'] is None, 'UNSUPPORTED_PAYLOAD')
            reference = result['L1M'][key]
            for k in ('condition', 'campaign', 'analyte', 'supported', 'reason', 'mass_kg', 'b0', 'b1'):
                require(r[k] == reference[k], 'SHARED_PREDICTION_IDENTITY')
    return result


def fraction_metric(observed, predicted):
    require(len(observed) == len(predicted) and len(observed) > 0, 'FRACTION_METRIC_MEMBERSHIP')
    for r, p in zip(observed, predicted):
        require((r['shot'], r['fraction']) == (p['shot'], p['fraction']), 'EXACT_FRACTION_JOIN')
        require(r['supported'] and p['supported'] and p['numerical_qualified'], 'FRACTION_SUPPORT')
        finite(r['q'], minimum=0.)
        finite(r['mass_kg'], minimum=0.)
        require(r['mass_kg'] > 0, 'POSITIVE_MEASURED_MASS')
        finite(p['five_cqa_mg_g']); finite(p['allowance_kg'], minimum=0.)
    mass = np.asarray([r['mass_kg'] for r in observed])
    error = np.asarray([p['five_cqa_mg_g'] - 1000 * r['q'] for r, p in zip(observed, predicted)])
    u = np.asarray([1000 * p['allowance_kg'] / m for p, m in zip(predicted, mass)])
    w = mass / mass.sum()
    bias = float(w @ error)
    metric = {'R_mg_g': float(np.sqrt(w @ error**2)), 'B_mg_g': bias, 'absB_mg_g': abs(bias),
              'R_allowance_mg_g': float(np.sqrt(w @ u**2)), 'B_allowance_mg_g': float(w @ u),
              'absB_allowance_mg_g': float(w @ u)}
    return metric, float(w @ (error - bias)**2), {'weights': w.tolist(), 'residuals_mg_g': error.tolist(),
                                                'fraction_allowances_mg_g': u.tolist()}


def direct_check(observed, predictions, shots):
    oi, pi = window_index(observed), prediction_indexes(predictions)
    for key, r in oi.items():
        finite(r['q'], minimum=0.)
        for arm in ARMS:
            for k in r.keys() - {'q'}:
                require(pi[arm][key][k] == r[k], 'OBSERVATION_PREDICTION_CROSSWALK:' + k)
    diffs, details = [], {}
    direct_by_arm = {a: {} for a in ARMS}
    for panel in PANELS:
        for arm in ARMS:
            for row in shots[panel][arm]:
                s = row['shot']
                keys = [(s, f) for f in FRACTIONS if oi[s, f]['supported']]
                metric, v, detail = fraction_metric([oi[k] for k in keys], [pi[arm][k] for k in keys])
                retained = row['supported_subset_diagnostic']
                diffs += differences(metric, {k: retained[k] for k in METRICS}, f'{panel}.{arm}.{s}')
                diffs += differences(v, shot_components(retained)['V'], f'{panel}.{arm}.{s}.V')
                details[arm + ':' + s] = dict(detail, metric=metric, direct_V=v)
                direct_by_arm[arm][s] = dict(metric, V=v)
    for panel in ('primary', 'temperature_stress'):
        indexes = {a: {r['shot']: r['full'] for r in shots[panel][a]} for a in ARMS}
        for a, b in PAIRS:
            for s in members(PANELS[panel]):
                c, r = direct_by_arm[a][s], direct_by_arm[b][s]
                d = r['R_mg_g'] + c['R_mg_g']
                direct = {CB: (r['B_mg_g']**2 - c['B_mg_g']**2) / d if d else 0.,
                          CV: (r['V'] - c['V']) / d if d else 0.}
                core = paired_shot(indexes[a][s], indexes[b][s])
                diffs += differences(direct, {k: core[k] for k in (CB, CV)}, f'{panel}.{a}_vs_{b}.{s}')
    summary = reconciliation_summary(diffs)
    summary.update(observation_slots=96, prediction_slots=288, supported_prediction_slots=285,
                   concentration_source='stored five_cqa_mg_g', allowance_source='total allowance_kg once',
                   original_coordinates_and_unsupported_slot_preserved=True)
    return summary, {'fraction_details': details, 'differences': diffs}


def detailed_flags(predictions=None, states=None):
    all_members = members(tuple(c for cs in PANELS.values() for c in cs))
    flags = {a: {} for a in ARMS}
    if predictions is not None:
        pi = prediction_indexes(predictions)
        for a in ARMS:
            for s in all_members:
                values = [pi[a][s, f]['feature_extrapolation'] for f in FRACTIONS if pi[a][s, f]['supported']]
                allowed = {'L1M': {'m1_kg', 'm2_kg', 'q1_kg_kg'}, 'L2M': {'m1_kg', 'm2_kg', 'q2_kg_kg'},
                           'L12': {'m1_kg', 'm2_kg', 'q1_kg_kg', 'q2_kg_kg'}}[a]
                require(all(isinstance(v, list) and len(v) == len(set(v)) and set(v) <= allowed for v in values),
                        'FLAG_FEATURE_CONTRACT')
                require(all(v == values[0] for v in values), 'INCONSISTENT_SHOT_FLAGS')
                flags[a][s] = sorted(values[0])
    if states is not None:
        require(set(states) == {a + ':' + s for a in ARMS for s in all_members}, 'STATE_MEMBERSHIP')
        for a in ARMS:
            expected_names = {'L1M': ['m1_kg', 'm2_kg', 'q1_kg_kg'], 'L2M': ['m1_kg', 'm2_kg', 'q2_kg_kg'],
                              'L12': ['m1_kg', 'm2_kg', 'q1_kg_kg', 'q2_kg_kg']}[a]
            for s in all_members:
                state = states[a + ':' + s]
                m, inputs = state['model'], state['inputs']
                require(state['species'] == m['species'] == inputs['species'] == '5CQA'
                        and m['arm'] == inputs['arm'] == a, 'STATE_IDENTITY')
                require(m['feature_order'] == m['input_order'] == expected_names, 'STATE_INPUT_CONTRACT')
                require(len(m['minima']) == len(m['maxima']) == len(expected_names), 'STATE_DOMAIN_WIDTH')
                expected_flags = []
                for name, lo, hi in zip(expected_names, m['minima'], m['maxima']):
                    x = finite(inputs[name]); finite(lo); finite(hi)
                    require(lo <= hi, 'STATE_DOMAIN')
                    if x < lo or x > hi:
                        expected_flags.append(name)
                require(sorted(state['feature_extrapolation']) == sorted(expected_flags), 'STATE_FLAG_DOMAIN_MISMATCH')
                if predictions is not None:
                    require(flags[a][s] == sorted(expected_flags), 'STATE_PREDICTION_FLAG_MISMATCH')
                    require(all(pi[a][s, f]['model_sha256'] == state['model_sha256'] for f in FRACTIONS if pi[a][s, f]['supported']),
                            'STATE_PREDICTION_MODEL_IDENTITY')
                flags[a][s] = sorted(expected_flags)
    require(predictions is not None or states is not None, 'FLAG_EVIDENCE_UNAVAILABLE')
    totals = {a: {panel: {'shots': sum(bool(flags[a][s]) for s in members(cs)),
                          'features': sorted({f for s in members(cs) for f in flags[a][s]})}
                  for panel, cs in PANELS.items()} for a in ARMS}
    return totals, flags


class Inputs:
    def __init__(self):
        self.identities = {}

    def load(self, path, expected):
        path = Path(path).resolve()
        data = path.read_bytes()
        actual = sha(data)
        self.identities[str(path)] = actual
        require(actual == expected, 'SHA256_MISMATCH')
        return parse(data)

    def recheck(self):
        require(all(sha(Path(p).read_bytes()) == h for p, h in self.identities.items()), 'INPUT_CHANGED_DURING_REDUCTION')


def authenticate_links(data, manifest, approval):
    expected = manifest['input_byte_sha256']
    f, c, r = (data[n] for n in ('freeze.json', 'score_completion.json', 'score_receipt.json'))
    require(all(x['task'] == OLD_TASK for x in (f, c, r, approval, data['scores.json'])), 'CHAIN_TASK')
    require(c['status'] == 'COMPLETE' and c['scientific_score_passes'] == 1 and r['status'] == 'STARTED', 'CHAIN_COMPLETION')
    require(c['files'] == {n: expected[n] for n in ('scores.json', 'shot_results.json', 'observed_suffix.json', 'score_receipt.json')},
            'NESTED_COMPLETION_BINDINGS')
    require(c['freeze_sha256'] == r['freeze_sha256'] == approval['freeze_sha256'] == expected['freeze.json'], 'CHAIN_FREEZE')
    approval_hash = manifest['repository_file_byte_sha256']['docs/analysis/sci_md_5cqa_assay_002/INDEPENDENT_APPROVAL.json']
    require(c['review_sha256'] == r['review_sha256'] == approval_hash and approval['status'] == 'APPROVED'
            and approval['independent'] is True and approval['unresolved_blocking_findings'] == [], 'CHAIN_APPROVAL')
    require(f['producer_commit'] == approval['reviewed_head'] == manifest['historical_producer']
            and f['producer_tree'] == approval['reviewed_tree'] == manifest['historical_tree'], 'CHAIN_PRODUCER')
    require(f['arms'] == list(ARMS) and f['panels'] == {p: list(cs) for p, cs in PANELS.items()}, 'CHAIN_POPULATION')
    require(r['predictions_sha256'] == f['artifacts']['predictions.json'] == expected['predictions.json']
            and f['artifacts']['states.json'] == expected['states.json'], 'FROZEN_OPTIONAL_IDENTITIES')
    for relative, h in manifest['repository_file_byte_sha256'].items():
        if relative in f.get('code_and_protocol', {}):
            require(f['code_and_protocol'][relative] == h, 'FROZEN_ADMITTED_AUTHORITY_BINDING')


def admit(directory, tracker, manifest, *, history=HISTORY, root=ROOT):
    data, availability, blockers = {}, {}, []
    approval = None
    for relative, expected in manifest['repository_file_byte_sha256'].items():
        try:
            obj = tracker.load(root / relative, expected) if relative.endswith('.json') else None
            if not relative.endswith('.json'):
                path = (root / relative).resolve()
                actual = sha(path.read_bytes()); tracker.identities[str(path)] = actual
                require(actual == expected, 'SHA256_MISMATCH')
            if relative.endswith('/INDEPENDENT_APPROVAL.json'):
                approval = obj
        except (OSError, ValueError) as exc:
            blockers.append({'artifact': relative, 'reason': type(exc).__name__})
    for name, expected in manifest['input_byte_sha256'].items():
        path = directory / name
        fallback = False
        # lexists prevents a present broken symlink from silently becoming a fallback.
        if not os.path.lexists(path) and name in FALLBACK:
            path = history / FALLBACK[name]
            fallback = True
        try:
            data[name] = tracker.load(path, expected)
            availability[name] = {'status': 'ADMITTED', 'sha256': expected, 'public_copy': FALLBACK[name] if fallback else None}
        except (OSError, ValueError) as exc:
            availability[name] = {'status': 'UNAVAILABLE' if isinstance(exc, FileNotFoundError) else 'INTEGRITY_BLOCKED',
                                  'reason': type(exc).__name__, 'expected_sha256': expected,
                                  'actual_sha256': tracker.identities.get(str(path.resolve()))}
            if name in manifest['core_artifacts']:
                blockers.append({'artifact': name, **availability[name]})
    if not blockers:
        try:
            authenticate_links(data, manifest, approval)
        except (ValueError, KeyError, TypeError) as exc:
            blockers.append({'artifact': 'public_evidence_chain', 'reason': str(exc)})
    return data, availability, blockers


def resolve_retained():
    configured = os.environ.get('PANNUSCH2024_MENDELEY_FULL_REPOSITORY') or os.environ.get('PUCKWORKS_EXTERNAL_DATA_ROOT')
    if not configured:
        config = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'puckworks/data_sources.json'
        configured = read(config)['sources']['PANNUSCH2024_MENDELEY_FULL_REPOSITORY']['path']
    return Path(configured).expanduser() / '5cqa-assay-002-evidence-20260929T163451Z/run-001'


def run(directory, output):
    directory, output = Path(directory).resolve(), Path(output).resolve()
    require(output != directory and directory not in output.parents and ROOT not in output.parents and output != ROOT,
            'OUTPUT_MUST_BE_OUTSIDE_GIT_AND_SOURCE')
    # Refuse other checkouts too, including a parent/child of any source artifact directory.
    parent = output.parent
    while not parent.exists():
        parent = parent.parent
    probe = subprocess.run(['git', '-C', str(parent), 'rev-parse', '--show-toplevel'], capture_output=True)
    require(probe.returncode != 0, 'OUTPUT_MUST_BE_OUTSIDE_GIT')
    output.mkdir(parents=True, exist_ok=False)
    specification_paths = [str((DOC / n).relative_to(ROOT)) for n in ('PROTOCOL.md', 'INPUT_MANIFEST.json', 'SYNTHETIC_SPEC.md')]
    for name in specification_paths:
        committed = subprocess.check_output(['git', 'show', 'HEAD:' + name], cwd=ROOT)
        require(committed == (ROOT / name).read_bytes(), 'SPECIFICATION_MUST_BE_COMMITTED_BEFORE_REDUCTION')
    specification_commit = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', *specification_paths], cwd=ROOT, text=True).strip()
    tracker = Inputs()
    manifest = read(DOC / 'INPUT_MANIFEST.json')
    public = {'task': TASK, 'classification': ['G1', 'NO_GOVERNING_PHYSICS_CHANGE', 'RESEARCH_ONLY',
               'RETROSPECTIVE', 'TARGET_EXPOSED', 'SOURCE_INTERNAL'],
        'component_completion': {k: 'NOT_RUN' for k in ('historical_metric_decision_reproduction', 'primary_deletion_sensitivity',
            'temperature_deletion_sensitivity', 'RMSE_decomposition', 'direct_fraction_cross_check', 'detailed_extrapolation_verification')},
        'bindings': {n: sha((DOC / n).read_bytes()) for n in ('PROTOCOL.md', 'INPUT_MANIFEST.json', 'SYNTHETIC_SPEC.md')},
        'implementation_sha256': sha(Path(__file__).read_bytes()), 'specification_commit': specification_commit,
        'policy': manifest['policy_acceptance'],
        'units': {'R_B_A_gains_and_contributions': 'mg/g', 'R2_B2_V': '(mg/g)^2'},
        'contribution_names': {CB: 'Contribution from squared mean shot error',
                              CV: 'Contribution from within-shot centered residual variation'},
        'population_contract': {'species': '5CQA', 'fractions': list(FRACTIONS), 'original_PRED_shots': 24,
            'original_observation_slots': 96, 'common_eligible_FIT_shots': 42, 'original_FIT_shots': 45,
            'retained_q2_INVALID_SPILL_exclusions': 3, 'panels': {p: list(cs) for p, cs in PANELS.items()},
            'inputs': {'L1M': ['m1', 'm2', 'q1'], 'L2M': ['m1', 'm2', 'q2'], 'L12': ['m1', 'm2', 'q1', 'q2']},
            'anchor': 'm1+m2', 'qualification': 'historical qualification reused without fitting or workbook requalification'},
        'unknown_uncertainty_components': list(UNKNOWN), 'physical_validation': 'NOT_ESTABLISHED',
        'analytical_uncertainty': 'NOT_ESTABLISHED', 'automatic_successor': False,
        'new_model_fits': 0, 'new_predictions': 0, 'native_ewp_runs': 0, 'historical_lifecycle_invocations': 0,
        'production_adoption_authorized': False, 'merge_authorized': False,
        'rights': 'Source-derived aggregates: Pannusch/Schmieder CC-BY-NC-3.0; Mendeley 10.17632/y2tz67f6ry.1. Software separately licensed.',
        'numerical_method': 'Binary64 point reductions; 512 ulps at max(1,abs(expected)) reconciliation only; outward nextafter intervals; V bounds intersect nonnegative constraint.',
        'claim_ceiling': 'Frozen-fit retained-input algebra and exact finite deletion-family stability; no causal, analytical, population, intended-use practical-value or physical-validation conclusion.'}
    private = {'retained_directory': str(directory)}
    data, public['availability'], blockers = admit(directory, tracker, manifest)
    public['core_blockers'] = blockers
    shots = None
    if not blockers:
        try:
            producer_tree = subprocess.check_output(['git', 'rev-parse', manifest['historical_producer'] + '^{tree}'], cwd=ROOT, text=True).strip()
            require(producer_tree == manifest['historical_tree'], 'GIT_PRODUCER_TREE')
            shots = validate_shots(data['shot_results.json'])
            reproduced = reproduce(shots)
            expected = {k: data['scores.json'][k] for k in reproduced}
            diffs = differences(reproduced, expected)
            private['historical_differences'] = diffs
            public['historical_reproduction'] = dict(reconciliation_summary(diffs), reproduced=reproduced)
            require(public['historical_reproduction']['pass'], 'HISTORICAL_RECONCILIATION_FAILED')
            public['analysis'], private['analysis'], error = analyze(shots)
            public['independent_deletion_identity_maximum_discrepancy'] = error
            public['flow_diagnostics'] = {'status': 'BASELINE_ONLY', 'full_flow_decomposition': 'UNAVAILABLE_INCOMPLETE_SUPPORT',
                                         'retained_panels': reproduced['panels']['flow_stress']}
            flow = reproduced['panels']['flow_stress']
            public['flow_diagnostics']['supported_subset_baseline_comparisons'] = {}
            for a, b in PAIRS:
                c, r = flow[a]['supported_subset_diagnostic'], flow[b]['supported_subset_diagnostic']
                g, u = r['R_mg_g'] - c['R_mg_g'], r['R_allowance_mg_g'] + c['R_allowance_mg_g']
                public['flow_diagnostics']['supported_subset_baseline_comparisons'][a + '_vs_' + b] = {
                    'scope': 'All six shots, equal condition weights; incomplete shot uses three supported windows; not full-flow metrics',
                    'supported_slots_per_arm': 23, 'original_slots_per_arm': 24,
                    'R_improvement_mg_g': g, 'R_improvement_allowance_mg_g': u, 'R_improvement_bounds': [g-u, g+u],
                    'signed_bias_change_mg_g': c['B_mg_g'] - r['B_mg_g'],
                    'A_deterioration_mg_g': c['absB_mg_g'] - r['absB_mg_g']}
            public['published_extrapolation_totals'] = data['scores.json']['feature_extrapolation']
            components = [shot_components(r['full']) for p in ('primary', 'temperature_stress') for a in ARMS for r in shots[p][a]]
            public['decomposition_integrity'] = {'complete_shot_arm_records': len(components),
                'negligible_negative_point_V_clamps': sum(x['negative_roundoff_clamped'] for x in components),
                'negative_unconstrained_V_lower_endpoints': sum(x['V_unconstrained_bounds'][0] < 0 for x in components)}
            for key in tuple(public['component_completion'])[:4]:
                public['component_completion'][key] = 'COMPLETE'
            private['retained_shot_metrics'] = shots
        except (ValueError, KeyError, TypeError) as exc:
            public['core_blockers'].append({'artifact': 'retained_core_schema_or_arithmetic', 'reason': str(exc)})
            shots = None
            for key in tuple(public['component_completion'])[:4]:
                public['component_completion'][key] = 'NOT_RUN_CORE_INTEGRITY_BLOCKED'
            public.pop('analysis', None)
    if shots is not None and 'predictions.json' in data and 'observed_suffix.json' in data:
        try:
            check, private['direct_cross_check'] = direct_check(data['observed_suffix.json'], data['predictions.json'], shots)
            public['direct_fraction_cross_check'] = check
            if check['pass']:
                public['component_completion']['direct_fraction_cross_check'] = 'COMPLETE'
            else:
                # Authenticated fraction arithmetic contradicting core statistics is shared evidence.
                public['core_blockers'].append({'artifact': 'shot_results.json/retained_fraction_records',
                                               'reason': 'DIRECT_CORE_ARITHMETIC_DISAGREEMENT'})
                public['component_completion']['direct_fraction_cross_check'] = 'INTEGRITY_BLOCKED'
                for key in tuple(public['component_completion'])[:4]:
                    public['component_completion'][key] = 'NOT_RUN_SHARED_EVIDENCE_INTEGRITY_BLOCKED'
                public.pop('analysis', None)
                shots = None
        except (ValueError, KeyError, TypeError) as exc:
            public['component_completion']['direct_fraction_cross_check'] = 'INTEGRITY_BLOCKED'
            public['direct_fraction_problem'] = str(exc)
    if shots is not None and ('predictions.json' in data or 'states.json' in data):
        try:
            totals, flags = detailed_flags(data.get('predictions.json'), data.get('states.json'))
            require(totals == public['published_extrapolation_totals'], 'PUBLISHED_FLAG_TOTAL_MISMATCH')
            public['component_completion']['detailed_extrapolation_verification'] = 'COMPLETE'
            public['detailed_extrapolation_verification'] = {'totals': totals,
                'predictions_checked': 'predictions.json' in data, 'raw_JSON_state_domains_checked': 'states.json' in data}
            private['shot_flags'] = flags
            for panel, result in private['analysis'].items():
                for s in result['deletions']:
                    s['extrapolated_shots'] = {a: sum(bool(flags[a][i]) for i in s['retained_members']) for a in ARMS}
        except (ValueError, KeyError, TypeError) as exc:
            public['component_completion']['detailed_extrapolation_verification'] = 'INTEGRITY_BLOCKED'
            public['detailed_flag_problem'] = str(exc)
    tracker.recheck()
    write(output / 'INPUT_LOCATORS.json', tracker.identities)
    write(output / 'PRIVATE_RESULTS.json', private)
    public['private_bindings'] = {n: sha((output / n).read_bytes()) for n in ('INPUT_LOCATORS.json', 'PRIVATE_RESULTS.json')}
    public['input_preservation'] = {'files_rehashed_unchanged': len(tracker.identities)}
    public['scientific_result_disposition'] = ('HISTORICAL_DECISIONS_PRESERVED_WITH_FINITE_DELETION_SENSITIVITY_AND_ALGEBRAIC_DECOMPOSITION'
                                                if shots is not None else 'EMPIRICAL_CORE_NOT_RUN')
    public['validation_framework_disposition'] = 'CASE_LOCAL_REDUCTION; SOFTWARE_CHECKS_AND_REVIEW_REPORTED_SEPARATELY'
    write(output / 'RESULTS.json', public)
    write(output / 'completion.json', {'task': TASK, 'status': 'COMPLETE', 'results_sha256': sha((output / 'RESULTS.json').read_bytes()),
                                      **public['private_bindings']})
    return public


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('--output', required=True, type=Path, help='new private directory outside Git/source')
    args = parser.parse_args()
    result = run(resolve_retained(), args.output)
    print(json.dumps(result['component_completion'], sort_keys=True))


if __name__ == '__main__':
    main()

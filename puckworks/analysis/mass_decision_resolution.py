"""Retained MASS-001/002/003 arithmetic; no historical lifecycle invocation.

Source-derived outputs retain Pannusch/Schmieder CC-BY-NC-3.0. Complete shot
and deletion records are private. Only whole-family projections are public.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import io
import json
import math
from pathlib import Path
import subprocess

import numpy as np

from . import five_cqa_decision_resolution as algebra
from . import pannusch_mass_delivery as original
from . import pannusch_conditioned_mass_delivery as conditioned
from . import pannusch_anchored_mass_delivery as anchored
from .mass_uncertainty_audit import Inputs, private_output

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/val_case_mass_decision_resolution_001'
TASK = 'VAL-CASE-MASS-DECISION-RESOLUTION-001'
PRIMARY, TEMP, FLOW = original.PRIMARY, original.TEMP, original.FLOW
ARMS = {'001': original.MODELS, '002': conditioned.MODELS, '003': anchored.ARMS}
CANDIDATE = {'001': 'MASS', '002': 'MTF', '003': 'ANCHORED_MASS'}
REFERENCES = {'001': ('TIME', 'BOUNDARY_AWARE_EMPIRICAL', 'TIME_u2', 'TIME_sqrt'),
              '002': ('M0', 'SETTING_AWARE_EMPIRICAL'),
              '003': ('UNANCHORED_MASS', 'ANCHOR_PERSISTENCE',
                      'ANCHORED_EMPIRICAL', 'ANCHORED_SETTING_EMPIRICAL')}
METRICS = ('R_pp', 'B_pp', 'abs_B_pp')
ALLOWANCES = ('R_allowance_pp', 'B_allowance_pp', 'B_allowance_pp')
COMPONENTS = ('delta_B2_pp2', 'delta_V_pp2', 'MSE_gain_pp2',
              'bias_contribution_pp', 'variation_contribution_pp')
UNKNOWN = ('analytical_repeatability', 'calibration_recovery', 'mass_measurement',
           'shared_systematic_error', 'training_model_selection', 'source_campaign_transfer')
require, sha, read, write = algebra.require, algebra.sha, algebra.read, algebra.write


def members(conditions):
    return {c.replace('-C', '-E') + f'-R{r}': c for c in conditions for r in (1, 2, 3)}


def close(a, b, context):
    require(abs(a - b) <= algebra.tolerance(b), context)
    return abs(a - b)


def extent(values):
    values = list(values)
    return [min(values), max(values)] if values else None


def metric_bounds(m):
    return {k: algebra.interval(m[k], m[u], nonnegative=k != 'B_pp')
            for k, u in zip(METRICS, ALLOWANCES)}


def validate_shots(case, shots):
    require(set(shots) == set(ARMS[case]), 'ARM_SET')
    expected = members(PRIMARY + TEMP + FLOW if case == '001' else PRIMARY)
    count = 5 if case == '003' else 6
    reference_support = None
    for arm, rows in shots.items():
        require(len(rows) == len(expected) and {r['shot']: r['condition'] for r in rows} == expected,
                'EXACT_PHYSICAL_SHOTS')
        support = []
        for r in rows:
            require(r['expected_assays'] == r['valid_assays'] == count, 'ASSAY_ACCOUNTING')
            require(r['collection_intervals'] == 11 and r['numerically_qualified'] is True,
                    'COLLECTION_OR_NUMERICAL_QUALIFICATION')
            require(r['full_support'] == (r['supported_assays'] == count), 'SUPPORT_FLAG')
            require((r['metrics'] is not None) == r['full_support'], 'SUPPORT_METRICS')
            require(r['out_of_domain_fractions'] == ([] if r['full_support'] else [10]), 'UNSUPPORTED_FRACTION')
            require(r['full_support'] or (case == '001' and r['condition'] == 'PRED-C07'), 'SUPPORT_SCOPE')
            m = r['metrics'] or r['supported_only_diagnostic']
            require(m is not None, 'MISSING_METRIC')
            for k, v in m.items():
                algebra.finite(v, minimum=None if k in ('B_pp', 'signed_assayed_total_error_g') else 0)
            require(m['abs_B_pp'] == abs(m['B_pp']), 'SHOT_ABSOLUTE_BIAS')
            shot_components(m)
            require(m['max_interval_allowance_kg'] <= 1e-9, 'NUMERICAL_BUDGET')
            require(0 < r['assayed_mass_kg'] <= r['complete_collected_mass_kg'], 'MASS_SUPPORT')
            support.append({k: r[k] for k in r if k not in ('metrics', 'supported_only_diagnostic')})
        if reference_support is None:
            reference_support = support
        require(support == reference_support, 'PAIRED_SUPPORT_MISMATCH')
    return shots


def shot_components(m):
    # Unit-preserving field adapter only; no chemical thresholds are reused.
    return algebra.shot_components({'R_mg_g': m['R_pp'], 'B_mg_g': m['B_pp'],
                                    'R_allowance_mg_g': m['R_allowance_pp'],
                                    'B_allowance_mg_g': m['B_allowance_pp']})


def decomposition(c, r):
    cs, rs = shot_components(c), shot_components(r)
    db, dv = rs['B2'] - cs['B2'], rs['V'] - cs['V']
    dbi = algebra.subtract(rs['B2_bounds'], cs['B2_bounds'])
    dvi = algebra.subtract(rs['V_bounds'], cs['V_bounds'])
    denominator = r['R_pp'] + c['R_pp']
    di = algebra.add(rs['R_bounds'], cs['R_bounds'])
    exact_zero = rs['R_bounds'] == cs['R_bounds'] == [0., 0.]
    cb, cv = (db / denominator, dv / denominator) if denominator else (0., 0.)
    require(denominator != 0 or db == dv == 0, 'INCONSISTENT_ZERO_ERRORS')
    values = {'delta_B2_pp2': db, 'delta_V_pp2': dv,
              'MSE_gain_pp2': rs['R2'] - cs['R2'],
              'bias_contribution_pp': cb, 'variation_contribution_pp': cv}
    bounds = {'delta_B2_pp2': dbi, 'delta_V_pp2': dvi,
              'MSE_gain_pp2': algebra.subtract(algebra.square(rs['R_bounds']), algebra.square(cs['R_bounds'])),
              'bias_contribution_pp': [0., 0.] if exact_zero else algebra.divide(dbi, di),
              'variation_contribution_pp': [0., 0.] if exact_zero else algebra.divide(dvi, di)}
    errors = [close(db + dv, values['MSE_gain_pp2'], 'SHOT_MSE_IDENTITY'),
              close(cb + cv, r['R_pp'] - c['R_pp'], 'SHOT_RMSE_IDENTITY')]
    return {'values': values, 'bounds': bounds, 'maximum_identity_discrepancy': max(errors),
            'negative_roundoff_corrections': int(cs['negative_roundoff_clamped']) + int(rs['negative_roundoff_clamped'])}


def nested(records, conditions, key, *, bounds=False):
    mean = algebra.mean_interval if bounds else lambda x: float(np.mean(x))
    return mean([mean([r[key] for r in records if r['condition'] == c]) for c in conditions])


def contrast(candidate, reference, *, primary=True):
    c, r = candidate['metrics'], reference['metrics']
    g, ug = r['R_pp'] - c['R_pp'], r['R_allowance_pp'] + c['R_allowance_pp']
    d, ud = c['abs_B_pp'] - r['abs_B_pp'], c['B_allowance_pp'] + r['B_allowance_pp']
    relative = g / r['R_pp'] if r['R_pp'] > 0 else None
    affine, ua = c['R_pp'] - .8 * r['R_pp'], c['R_allowance_pp'] + .8 * r['R_allowance_pp']
    values = {'gain_pp': g, 'relative_gain': relative, 'signed_bias_change_pp': c['B_pp'] - r['B_pp'],
              'abs_bias_deterioration_pp': d, 'relative_affine_pp': affine}
    bounds = {'gain_pp': algebra.interval(g, ug),
              'relative_gain': algebra.divide(algebra.interval(g, ug), algebra.interval(r['R_pp'], r['R_allowance_pp'], nonnegative=True)),
              'signed_bias_change_pp': algebra.interval(values['signed_bias_change_pp'], ud),
              'abs_bias_deterioration_pp': algebra.interval(d, ud),
              'relative_affine_pp': algebra.interval(affine, ua)}
    requirements = {'absolute_gain': (-g, ug, -.1), 'relative_20_percent': (affine, ua, 0.),
                    'bias_deterioration': (d, ud, .1), 'RMSE_competitiveness': (-g, ug, .1)}
    # Temperature retains descriptive contrasts only; no primary acceptance tests.
    headroom = {k: {'point': limit - v, 'bounds': algebra.interval(limit - v, u),
                    'relation': original.threshold(v, u, limit)}
                for k, (v, u, limit) in requirements.items()} if primary else {}
    return {'values': values, 'bounds': bounds, 'headroom': headroom,
            'point_gain_positive': g > 0, 'numerical_lower_gain_positive': g - ug > 0,
            'allowances': {'gain_pp': ug, 'bias_change_pp': ud, 'relative_affine_pp': ua}}


def scenario(case, shots, conditions, omitted=None):
    require(omitted is None or omitted in members(conditions), 'OMITTED_MEMBER')
    selected = {a: [r for r in rows if r['condition'] in conditions and r['shot'] != omitted]
                for a, rows in shots.items()}
    expected = set(members(conditions)) - ({omitted} if omitted else set())
    require(all({r['shot'] for r in rows} == expected for rows in selected.values()), 'PAIRED_OMISSION')
    cc = {a: original.condition_metrics(rows) for a, rows in selected.items()}
    groups = {a: original.aggregate(rows, conditions) for a, rows in cc.items()}
    primary = conditions == PRIMARY
    pairs = {}
    for ref in REFERENCES[case]:
        ca = CANDIDATE[case]
        p = contrast(groups[ca], groups[ref], primary=primary)
        by_condition = {c: contrast(next(r for r in cc[ca] if r['condition'] == c),
                                    next(r for r in cc[ref] if r['condition'] == c), primary=primary)
                        for c in conditions}
        definite = sum(r['values']['gain_pp'] > r['allowances']['gain_pp'] for r in by_condition.values())
        possible = sum(r['values']['gain_pp'] > -r['allowances']['gain_pp'] for r in by_condition.values())
        p.update(conditions=by_condition, definite_wins=definite, possible_wins=possible)
        if primary:
            p['headroom']['condition_wins'] = {'point_definite': definite - 3, 'point_possible': possible - 3,
                'relation': 'PASS' if definite >= 3 else 'FAIL' if possible < 3 else 'NUMERICALLY_UNRESOLVED'}
        if case == '003':
            ri = {r['shot']: r for r in selected[ref]}
            rows = [dict(decomposition(r['metrics'], ri[r['shot']]['metrics']),
                         shot=r['shot'], condition=r['condition']) for r in selected[ca]]
            aggregate = {'values': {}, 'bounds': {}}
            for k in COMPONENTS:
                aggregate['values'][k] = nested([dict(condition=r['condition'], v=r['values'][k]) for r in rows], conditions, 'v')
                aggregate['bounds'][k] = nested([dict(condition=r['condition'], v=r['bounds'][k]) for r in rows], conditions, 'v', bounds=True)
            aggregate['maximum_identity_discrepancy'] = max(
                close(aggregate['values']['bias_contribution_pp'] + aggregate['values']['variation_contribution_pp'], p['values']['gain_pp'], 'BALANCED_RMSE_IDENTITY'),
                close(aggregate['values']['delta_B2_pp2'] + aggregate['values']['delta_V_pp2'], aggregate['values']['MSE_gain_pp2'], 'BALANCED_MSE_IDENTITY'))
            aggregate['shots'] = rows
            p['decomposition'] = aggregate
        pairs[ref] = p
    arm_requirements = {}
    for a, rows in cc.items():
        arm_requirements[a] = {r['condition']: {k: {'point': limit - r['metrics'][k],
            'bounds': algebra.interval(limit - r['metrics'][k], r['metrics'][u]),
            'relation': original.threshold(r['metrics'][k], r['metrics'][u], limit)}
            for k, u, limit in [('R_pp', 'R_allowance_pp', 1.), ('abs_B_pp', 'B_allowance_pp', .5)]} for r in rows}
    return {'omitted': omitted, 'physical_shots': len(expected),
            'intervals_per_arm': len(expected) * (5 if case == '003' else 6),
            'conditions': cc, 'arms': groups, 'arm_requirements': arm_requirements, 'pairs': pairs}


def family_summary(records, value, bound):
    base, deleted = records[0], records[1:]
    def box(rows):
        intervals = [bound(r) for r in rows]
        return None if any(i is None for i in intervals) else [min(i[0] for i in intervals), max(i[1] for i in intervals)]
    vals = [value(r) for r in deleted]
    return {'baseline': value(base), 'baseline_bounds': bound(base),
            'deletion_only_range': None if any(v is None for v in vals) else extent(vals),
            'deletion_only_numerical_envelope': box(deleted),
            'baseline_plus_deletion_numerical_envelope': box(records)}


def public_panel(case, records):
    """Deliberate allow-list; no shot IDs, vectors or condition-deletion extrema."""
    base = records[0]
    result = {'baseline': {'arms': base['arms'], 'conditions': base['conditions']},
              'deletion_count': len(records) - 1, 'deleted_scenario_shots': records[1]['physical_shots'],
              'deleted_scenario_intervals_per_arm': records[1]['intervals_per_arm'], 'arms': {}, 'pairs': {}}
    for a in ARMS[case]:
        result['arms'][a] = {k: family_summary(records, lambda s: s['arms'][a]['metrics'][k],
            lambda s: metric_bounds(s['arms'][a]['metrics'])[k]) for k in METRICS}
        result['arms'][a]['condition_requirement_relation_counts'] = {c: {k: dict(Counter(
            s['arm_requirements'][a][c][k]['relation'] for s in records[1:])) for k in ('R_pp', 'abs_B_pp')}
            for c in base['arm_requirements'][a]}
    for ref in REFERENCES[case]:
        pp = [s['pairs'][ref] for s in records]
        out = {k: family_summary(pp, lambda p: p['values'][k], lambda p: p['bounds'][k]) for k in pp[0]['values']}
        out['deletion_gain_positive_count'] = sum(p['point_gain_positive'] for p in pp[1:])
        out['deletion_numerical_lower_gain_positive_count'] = sum(p['numerical_lower_gain_positive'] for p in pp[1:])
        out['definite_win_count_range'] = extent(p['definite_wins'] for p in pp[1:])
        out['possible_win_count_range'] = extent(p['possible_wins'] for p in pp[1:])
        out['requirement_relation_counts'] = {k: dict(Counter(p['headroom'][k]['relation'] for p in pp[1:])) for k in pp[0]['headroom']}
        if case == '003':
            dd = [p['decomposition'] for p in pp]
            out['decomposition'] = {k: family_summary(dd, lambda d: d['values'][k], lambda d: d['bounds'][k]) for k in COMPONENTS}
        result['pairs'][ref] = out
    return result


def analyze(case, shots, conditions=PRIMARY):
    records = [scenario(case, shots, conditions, s) for s in [None, *members(conditions)]]
    errors = []
    for s in records[1:]:
        shot, condition = s['omitted'], members(conditions)[s['omitted']]
        for ref in REFERENCES[case]:
            b = records[0]['pairs'][ref]
            c = next(r['metrics'] for r in shots[CANDIDATE[case]] if r['shot'] == shot)
            r = next(r['metrics'] for r in shots[ref] if r['shot'] == shot)
            expected = b['values']['gain_pp'] + (b['conditions'][condition]['values']['gain_pp'] - (r['R_pp'] - c['R_pp'])) / (2 * len(conditions))
            errors.append(close(s['pairs'][ref]['values']['gain_pp'], expected, 'DELETION_GAIN_IDENTITY'))
            if case == '003':
                all_rows = b['decomposition']['shots']
                for k in COMPONENTS:
                    cm = float(np.mean([r['values'][k] for r in all_rows if r['condition'] == condition]))
                    val = next(r['values'][k] for r in all_rows if r['shot'] == shot)
                    expected = b['decomposition']['values'][k] + (cm - val) / (2 * len(conditions))
                    errors.append(close(s['pairs'][ref]['decomposition']['values'][k], expected, 'DELETION_COMPONENT_IDENTITY'))
    public = public_panel(case, records)
    public['maximum_deletion_identity_discrepancy'] = max(errors)
    return public, records


def reproduce(case, shots, saved):
    cc = {a: original.condition_metrics(rows) for a, rows in shots.items()}
    if case == '003':
        # Core support is complete: intended=eligible=supported mass; same order
        # as original sum of shot masses, reconciled with original row sums.
        for a, conditions in cc.items():
            for c in conditions:
                rows = [r for r in shots[a] if r['condition'] == c['condition']]
                mass = sum(r['assayed_mass_kg'] for r in rows)
                c['coverage'] = {'intended_shots': len(rows), 'supported_shots': c['qualified_shots'],
                    'intended_assays': sum(r['expected_assays'] for r in rows),
                    'eligible_assays': sum(r['valid_assays'] for r in rows),
                    'supported_assays': sum(r['supported_assays'] for r in rows),
                    'intended_mass_kg': mass, 'eligible_mass_kg': mass, 'supported_mass_kg': mass}
        result = dict(anchored.decision_axes(cc), conditions=cc)
    elif case == '002':
        result = dict(conditioned.decision_axes(cc), conditions=cc)
    else:
        result = {'conditions': cc, 'groups': {p: {a: original.aggregate(rows, cs) for a, rows in cc.items()}
                  for p, cs in [('primary', PRIMARY), ('temperature_ramp', TEMP), ('flow_ramp', FLOW)]},
                  'comparisons': {r: original.comparison(cc, b=r) for r in REFERENCES[case]}}
    diffs = algebra.differences(result, {k: saved[k] for k in result})
    summary = algebra.reconciliation_summary(diffs)
    require(summary['pass'], 'HISTORICAL_REPRODUCTION')
    return result, diffs, summary


def authenticate(case, directory, tracker, manifest):
    spec = manifest['cases'][case]
    history = ROOT / f'docs/analysis/sci_md_mass_delivery_{case}'
    for path, expected in manifest['public_authorities'].items():
        tracker.bytes(ROOT / path, expected)
    data, availability = {}, {}
    core = {'scores.json', 'source.json', 'freeze.json', 'execution.json', 'score_receipt.json', 'score_completion.json', 'pre_score_review.json'}
    core.add({'001': 'scores.json', '002': 'primary_metrics.json', '003': 'shot_results.json'}[case])
    for name, entry in spec['retained_files'].items():
        p = directory.parent / name if name == 'pre_score_review.json' else directory / name
        if not p.exists():
            availability[name] = 'UNAVAILABLE'
            require(name not in core, 'MISSING_CORE:' + name)
            continue
        actual = tracker.bytes(p)
        if sha(actual) != entry['sha256']:
            require(name not in core, 'CORE_HASH_MISMATCH:' + name)
            availability[name] = 'HASH_MISMATCH_DEPENDENT_COMPONENT_BLOCKED'
            continue
        data[name] = algebra.parse(actual)
        availability[name] = 'AUTHENTICATED'
    frozen, receipt, completion = (data[n + '.json'] for n in ('freeze', 'score_receipt', 'score_completion'))
    approval = data['pre_score_review.json']
    require(frozen['producer_commit'] == spec['producer_commit'] and frozen['producer_tree'] == spec['producer_tree'], 'PRODUCER_IDENTITY')
    actual_tree = subprocess.check_output(['git', 'rev-parse', spec['producer_commit'] + '^{tree}'], cwd=ROOT, text=True).strip()
    require(actual_tree == spec['producer_tree'], 'PRODUCER_TREE')
    for path, expected in frozen['code_and_protocol'].items():
        producer_bytes = subprocess.check_output(['git', 'show', spec['producer_commit'] + ':' + path], cwd=ROOT)
        require(sha(producer_bytes) == expected, 'HISTORICAL_CODE_IDENTITY')
        # Current functions are only reused when byte-identical to producer.
        if path.startswith('puckworks/analysis/'):
            tracker.bytes(ROOT / path, expected)
    public_review = tracker.json(history / 'PRE_SCORE_REVIEW.json')
    require(approval['status'] == public_review['status'] == 'APPROVED' and approval['independent'] is True, 'ORIGINAL_APPROVAL')
    require(approval['freeze_sha256'] == receipt['freeze_sha256'] == spec['retained_files']['freeze.json']['sha256'], 'FREEZE_APPROVAL_JOIN')
    require(receipt['review_sha256'] == spec['retained_files']['pre_score_review.json']['sha256'], 'REVIEW_RECEIPT_JOIN')
    require(receipt.get('predictions_sha256', receipt.get('prediction_sha256')) == frozen['artifacts']['predictions.json'], 'PREDICTION_RECEIPT_JOIN')
    require(receipt['status'] == 'STARTED' and completion['status'] == 'COMPLETE', 'SCORE_LIFECYCLE')
    require(completion['scores_sha256'] == spec['retained_files']['scores.json']['sha256'] and data['scores.json']['score_passes'] == 1, 'COMPLETE_SINGLE_SCORE')
    for key, name in [('score_receipt_sha256', 'score_receipt.json'), ('shot_results_sha256', 'shot_results.json')]:
        if key in completion:
            require(completion[key] == spec['retained_files'][name]['sha256'], 'COMPLETION_JOIN')
    for name, expected in frozen['artifacts'].items():
        if name in data:
            require(spec['retained_files'][name]['sha256'] == expected, 'FROZEN_ARTIFACT_JOIN')
    require(spec['source_registers'] == data['source.json']['registers'], 'SOURCE_REGISTER_BINDING')
    for name, expected in spec['source_registers'].items():
        tracker.bytes(ROOT / 'puckworks/data/pannusch2024' / name, expected)
    return data, availability


def observation_coordinates(case, data, availability):
    if availability.get('coordinates.json', '').startswith('HASH_MISMATCH'):
        return None
    if 'coordinates.json' in data:
        return data['coordinates.json']
    if case != '003' and 'predictions.json' in data:
        return data['predictions.json'][ARMS[case][0]]
    return None


def observations(case, coordinates, shots, csv_bytes):
    """Only the originally bound TDS rows; no source-workbook reconstruction."""
    candidates = list(csv.DictReader(io.StringIO(csv_bytes.decode())))
    selected = [r for r in candidates if r['campaign_id'] == 'PREDICTION_2022_03' and r['analyte'] == 'TDS']
    index = {}
    duplicates = 0
    for r in selected:
        key = (r['shot_id'], int(r['fraction_id']))
        if key in index:
            require(index[key] == r, 'CONFLICTING_SOURCE_DUPLICATE')
            duplicates += 1
        index[key] = r
    supported_shots = {r['shot']: r for r in shots[ARMS[case][0]]}
    fractions = (2, 3, 5, 7, 10) if case == '003' else (1, 2, 3, 5, 7, 10)
    coords = [r for r in coordinates if r['shot'] in supported_shots and r['fraction'] in fractions]
    expected = {(s, f) for s in supported_shots for f in fractions}
    require(len(coords) == len(expected) and {(r['shot'], r['fraction']) for r in coords} == expected, 'EXACT_SUFFIX_OR_FULL_SUPPORT')
    result = []
    for c in coords:
        r = index[(c['shot'], c['fraction'])]
        require(r['condition_id'] == c['condition'] and r['campaign_id'] == c['campaign'] and r['source_id'] == c['source_id'], 'OBSERVATION_IDENTITY')
        require(r['concentration_unit'] == 'percent' and r['validity'] == 'VALID' and c['mass_basis'] == 'MEASURED_MASS_G', 'TDS_UNITS_VALIDITY')
        require(c['mass_prefix'] == 'SOURCE_SHOT_mE_cum_ALL_INTERVENING_VIALS', 'MASS_PREFIX_CONTRACT')
        require(abs(float(r['fraction_liquid_g_or_ml']) * .001 - c['mass_kg']) <= 5.01e-12, 'ROUNDED_MASS_JOIN')
        close(c['b1'] - c['b0'], c['mass_kg'], 'COORDINATE_WIDTH')
        q = float(original.concentration_to_fraction(float(r['measured_concentration']), 'percent'))
        rounding = c['mass_kg'] * 5e-11 + q * 5e-12 + 5e-15
        solute = c['mass_kg'] * q
        require(abs(solute - float(r['derived_analyte_mass_mg']) * 1e-6) <= rounding + 1e-17, 'SOURCE_ROUNDING_CONSISTENCY')
        result.append(dict(c, eligible=True, q=q, solute_kg=solute,
            source_rounding_allowance_kg=rounding,
            collection_count=supported_shots[c['shot']]['collection_intervals'],
            collection_mass_kg=supported_shots[c['shot']]['complete_collected_mass_kg']))
    return result, duplicates


def direct_check(case, data, shots, obs):
    diffs, residuals, rounding = [], {}, {}
    for a in ARMS[case]:
        pi = {(r['shot'], r['fraction']): r for r in data['predictions.json'][a] if r['shot'] in {o['shot'] for o in obs}}
        require(len(pi) == len(obs) and len(data['predictions.json'][a]) == len(set((r['shot'], r['fraction']) for r in data['predictions.json'][a])), 'PREDICTION_MEMBER_ACCOUNTING')
        pp = [pi[(o['shot'], o['fraction'])] for o in obs]
        for o, p in zip(obs, pp):
            for key in ('shot', 'fraction', 'condition', 'campaign', 'b0', 'b1'):
                require(p[key] == o[key], 'PREDICTION_QUERY_JOIN')
            require(not p['in_domain'] or p['numerical_qualified'] is True, 'PREDICTION_NUMERICS')
        calc = original.shot_metrics(obs, pp)
        diffs += algebra.differences(calc, shots[a], a)
        residuals[a], rounding[a] = [], []
        for s in shots[a]:
            pairs = [(o, p) for o, p in zip(obs, pp) if o['shot'] == s['shot'] and p['in_domain']]
            mass = np.array([o['mass_kg'] for o, p in pairs])
            err = np.array([100 * (p['predicted_solute_kg'] - o['solute_kg']) / o['mass_kg'] for o, p in pairs])
            weights = mass / sum(mass)
            b = sum(weights * err)
            v = float(sum(weights * (err - b) ** 2))
            m = s['metrics'] or s['supported_only_diagnostic']
            close(v, shot_components(m)['V'], 'DIRECT_CENTERED_VARIATION')
            residuals[a].append({'shot': s['shot'], 'condition': s['condition'], 'errors_pp': err.tolist(), 'weights': weights.tolist(), 'V_pp2': v,
                                 'V_discrepancy': abs(v - shot_components(m)['V'])})
            # Export-only, fixed mass/parameters; not an assay uncertainty model.
            u = np.array([5e-9 * (1 + abs(p.get('anchor_error_amplification') or 0) + (p.get('amplification_allowance') or 0)) for o, p in pairs])
            rounding[a].append({'shot': s['shot'], 'condition': s['condition'],
                               'R_pp': float(np.sqrt(sum(weights * u**2))), 'B_pp': float(sum(weights * u))})
    summary = algebra.reconciliation_summary(diffs)
    require(summary['pass'], 'DIRECT_FRACTION_RECONCILIATION')
    summary['maximum_V_discrepancy_pp2'] = max(r['V_discrepancy'] for rows in residuals.values() for r in rows)
    return summary, {'differences': diffs, 'residuals': residuals, 'export_rounding_allowances': rounding}


def variability(obs):
    cells = []
    for c in sorted({o['condition'] for o in obs}):
        for f in sorted({o['fraction'] for o in obs}):
            rows = [o for o in obs if o['condition'] == c and o['fraction'] == f]
            require(len(rows) == 3, 'VARIABILITY_THREE_PHYSICAL_SHOTS')
            cells.append({'condition': c, 'fraction': f, 'n': 3,
                'TDS_sample_SD_pp': float(np.std([100 * o['q'] for o in rows], ddof=1)),
                **{k + '_range_kg': max(o[k] for o in rows) - min(o[k] for o in rows) for k in ('mass_kg', 'b0', 'b1')}})
    # No per-cell spread is public. Whole-panel range and support only.
    return {'physical_shots': len({o['shot'] for o in obs}), 'cells': len(cells), 'shots_per_cell': 3,
            'TDS_sample_SD_pp_across_cells': extent(r['TDS_sample_SD_pp'] for r in cells),
            'maximum_window_start_range_kg': max(r['b0_range_kg'] for r in cells),
            'maximum_window_end_range_kg': max(r['b1_range_kg'] for r in cells),
            'interpretation': 'Between-shot variation at differing measured windows; not assay precision'}, cells


def primitive_mass_map(masses, fractions):
    """Algebraic coordinate/weight map for synthetic verification, no predictions."""
    require(all(math.isfinite(m) and m > 0 for m in masses), 'POSITIVE_VIAL_MASSES')
    require(len(set(fractions)) == len(fractions) and all(2 <= f <= len(masses) for f in fractions), 'SUFFIX_FRACTIONS')
    prefix = np.r_[0., np.cumsum(masses)]
    total = sum(masses[f - 1] for f in fractions)
    return {'anchor_width': masses[0], 'anchor_end': masses[0],
            'windows': [[float(prefix[f - 1]), float(prefix[f])] for f in fractions],
            'widths': [masses[f - 1] for f in fractions],
            'weights': [masses[f - 1] / total for f in fractions]}


def anchor_check(data):
    anchors, states = data['anchors.json'], data['states.json']
    require(set(anchors) == set(members(PRIMARY)), 'TWELVE_ANCHORS')
    require(set(states) == {base + '/' + s for base in ('MASS', 'EMPIRICAL', 'SETTING_EMPIRICAL') for s in anchors}, 'STATE_MEMBERS')
    errors = []
    for s, a in anchors.items():
        require(a['fraction_id'] == 1 and a['start_kg'] == 0 and a['shot_id'] == s and a['tds_unit'] == 'percent', 'ANCHOR_CONTRACT')
    for base, arm in [('MASS', 'ANCHORED_MASS'), ('EMPIRICAL', 'ANCHORED_EMPIRICAL'), ('SETTING_EMPIRICAL', 'ANCHORED_SETTING_EMPIRICAL')]:
        for p in data['predictions.json'][arm]:
            a, state = anchors[p['shot']], states[base + '/' + p['shot']]
            require(state['anchor'] == a, 'STATE_ANCHOR_JOIN')
            expected = (a['end_kg'] - a['start_kg']) * (a['tds_percent'] / 100) / state['anchor_integral_kg']
            errors.append(close(state['alpha'], expected, 'RETAINED_NORMALIZATION'))
            predicted = 100 * p['predicted_solute_kg'] / (p['b1'] - p['b0'])
            errors.append(close(predicted, a['tds_percent'] * p['anchor_error_amplification'], 'ANCHOR_LINEAR_MAPPING'))
    return {'status': 'VERIFIED_RETAINED_MAPPING', 'anchors': 12, 'states': 36,
            'maximum_arithmetic_discrepancy': max(errors),
            'anchor_only_derivative': 'g_i', 'shared_additive_calibration_residual_derivative': 'g_i - 1',
            'uncertainty_magnitude': 'NOT_ESTABLISHED', 'numerical_input_error_campaign': 'NOT_RUN_NOT_DECLARED'}


def run_case(case, directory, output):
    manifest = read(DOC / 'INPUT_MANIFEST.json')
    tracker = Inputs()
    out = private_output(output, [directory, directory.parent])
    write(out / 'started.json', {'task': TASK, 'case': case})
    public = {'task': TASK, 'case': case, 'classification': 'G1/RESEARCH_ONLY/RETROSPECTIVE/TARGET_EXPOSED/SOURCE_INTERNAL',
              'policy': manifest['policy'], 'physical_validation': 'NOT_ESTABLISHED', 'unknown_uncertainty_components': UNKNOWN}
    private = {}
    try:
        review = tracker.json(DOC / 'PRE_ANALYSIS_REVIEW.json')
        require(review['status'] == 'APPROVED', 'METHOD_REVIEW_REQUIRED')
        for f, expected in review['bindings'].items():
            tracker.bytes(DOC / f, expected)
        data, availability = authenticate(case, directory, tracker, manifest)
        shots = data['scores.json']['shots'] if case == '001' else data['primary_metrics.json']['shots'] if case == '002' else data['shot_results.json']
        validate_shots(case, shots)
        historical, diffs, reconciliation = reproduce(case, shots, data['scores.json'])
        private.update(shots=shots, historical_reconciliation=diffs, input_availability=availability)
        public.update(historical=historical, historical_reconciliation=reconciliation, input_availability=availability)
        if case == '002':
            require(data['primary_metrics.json']['conditions'] == data['scores.json']['conditions'], 'SHOT_AGGREGATE_BINDING')
            public['ramps'] = data['scores.json']['ramps']
        if case == '001':
            historical_public = tracker.json(ROOT / 'docs/analysis/sci_md_mass_delivery_001/RESULTS.json')
            require(historical_public['score_sha256'] == manifest['cases'][case]['retained_files']['scores.json']['sha256'], 'PUBLIC_SCORE_BINDING')
            for k in ('conditions', 'groups', 'comparisons', 'bootstrap'):
                require(historical_public[k] == data['scores.json'][k], 'PUBLIC_AGGREGATE_BINDING')
            public['historical_bootstrap'] = {'execution': 'REUSED_NOT_RERUN', 'replicates': 2000, 'summary': data['scores.json']['bootstrap']}
            public['historical_disposition'] = historical_public['disposition']
        public['primary'], private['primary'] = analyze(case, shots)
        if case == '003':
            public['decomposition_integrity'] = {
                'negative_roundoff_corrections_unique_arm_shots': sum(shot_components(r['metrics'])['negative_roundoff_clamped'] for rows in shots.values() for r in rows),
                'maximum_identity_discrepancy': max(p['decomposition']['maximum_identity_discrepancy'] for s in private['primary'] for p in s['pairs'].values()),
                'unresolved_aggregate_contribution_bounds': sum(v is None for s in private['primary'] for p in s['pairs'].values() for v in p['decomposition']['bounds'].values())}
        if case == '001':
            public['temperature'], private['temperature'] = analyze(case, shots, TEMP)
        public['components'] = {'historical_reproduction': 'EXECUTED',
            'primary_paired_sensitivities': {r: 'EXECUTED' for r in REFERENCES[case]},
            'temperature_sensitivity': 'EXECUTED' if case == '001' else 'NOT_APPLICABLE',
            'RMSE_decomposition': 'EXECUTED' if case == '003' else 'NOT_APPLICABLE',
            'numerical_propagation': 'EXECUTED', 'mass_coordinate_dependency': 'ANALYTICALLY_ASSESSED_NO_ERROR_MAGNITUDE',
            'joint_mass_source_rounding_propagation': 'UNEXECUTED_NO_JUSTIFIED_PRIMITIVE_ERROR_MODEL'}
        coords = observation_coordinates(case, data, availability)
        if coords is not None:
            csv_path = ROOT / 'puckworks/data/pannusch2024/prediction_fraction_replicates.csv'
            obs, duplicates = observations(case, coords, shots, tracker.bytes(csv_path))
            private['observations'] = obs
            public['identical_TDS_duplicates_collapsed'] = duplicates
            public['observation_variability'], private['observation_variability'] = {}, {}
            panels = {'primary': PRIMARY, 'temperature': TEMP, 'flow': FLOW} if case == '001' else {'primary': PRIMARY}
            for p, cs in panels.items():
                public['observation_variability'][p], private['observation_variability'][p] = variability([o for o in obs if o['condition'] in cs])
            public['components']['observation_variability'] = 'EXECUTED'
            if 'predictions.json' in data:
                public['direct_fraction_check'], private['direct_fraction_check'] = direct_check(case, data, shots, obs)
                public['export_rounding'] = {'basis': 'Conditional eight-decimal TDS export rounding only, fixed masses/parameters; not assay precision', 'panels': {}}
                for p, cs in panels.items():
                    public['export_rounding']['panels'][p] = {
                        'support': 'SUPPORTED_ONLY_DIAGNOSTIC_NOT_FULL_FLOW' if p == 'flow' else 'COMPLETE_ORIGINAL_PANEL',
                        'arm_allowances': {a: {k: nested(rows, cs, k) for k in ('R_pp', 'B_pp')} for a, rows in private['direct_fraction_check']['export_rounding_allowances'].items()}}
                public['components'].update(direct_fraction_verification='EXECUTED', conditional_TDS_export_rounding='EXECUTED')
            else:
                public['components'].update(direct_fraction_verification='UNEXECUTED_PREDICTIONS_UNAVAILABLE', conditional_TDS_export_rounding='UNEXECUTED_PREDICTIONS_UNAVAILABLE')
        else:
            public['components'].update(direct_fraction_verification='UNEXECUTED_COORDINATE_JOIN_UNAVAILABLE', observation_variability='UNEXECUTED_COORDINATE_JOIN_UNAVAILABLE', conditional_TDS_export_rounding='UNEXECUTED_COORDINATE_JOIN_UNAVAILABLE')
        if case == '003':
            public['historical_anchor_sensitivity'] = {'execution': 'REUSED_NOT_RERUN', 'summary': data['scores.json']['numerics']}
            if all(k in data for k in ('anchors.json', 'states.json', 'predictions.json')):
                public['anchor_dependence'] = anchor_check(data)
                public['components']['anchor_dependency'] = 'EXECUTED_RETAINED_ALGEBRA_NO_ERROR_MAGNITUDE'
            else:
                public['components']['anchor_dependency'] = 'ANALYTICAL_ONLY_RETAINED_MAPPING_CHECK_UNEXECUTED'
        else:
            public['components']['anchor_dependency'] = 'NOT_APPLICABLE'
        tracker.recheck()
        write(out / 'INPUT_LOCATORS.json', {str(p): s for p, s in tracker.identities.items()})
        write(out / 'PRIVATE_RESULTS.json', private)
        public['private_bindings'] = {f: sha((out / f).read_bytes()) for f in ('INPUT_LOCATORS.json', 'PRIVATE_RESULTS.json')}
        public['inputs_unchanged_after'] = True
        public['execution'] = 'COMPLETED_DECLARED_AVAILABLE_COMPONENTS'
        write(out / 'RESULTS.json', public)
        write(out / 'completion.json', {'task': TASK, 'case': case, 'status': 'COMPLETE', 'public_sha256': sha((out / 'RESULTS.json').read_bytes()), **public['private_bindings']})
    except Exception as exc:
        tracker.recheck()
        write(out / 'failure.json', {'task': TASK, 'case': case, 'status': 'FAILED', 'exception': type(exc).__name__, 'message': str(exc)})
        raise
    return public


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=ARMS, required=True)
    parser.add_argument('--retained', type=Path, required=True, help='Existing named original run directory; no corpus scan')
    parser.add_argument('--output', type=Path, required=True, help='Exclusive new private output directory')
    args = parser.parse_args()
    result = run_case(args.case, args.retained.resolve(), args.output)
    print(json.dumps({'case': args.case, 'execution': result['execution'], 'components': result['components']}, indent=2))


if __name__ == '__main__':
    main()

"""One-way, independently approved scoring of already-frozen stopping choices."""
from __future__ import annotations

import argparse
from collections import Counter
from decimal import Decimal
from pathlib import Path
import statistics

from . import grudeva_stopping_decision as p

NOT_ADJUDICATED = 'FROZEN_C2_STOPPING_DECISION_NOT_ADJUDICATED'
INADEQUATE = 'FROZEN_C2_STOPPING_DECISION_INADEQUATE_ON_DECLARED_OFFLINE_CONTRACT'
ADEQUATE = 'FROZEN_C2_STOPPING_DECISION_ADEQUATE_ON_DECLARED_OFFLINE_CONTRACT'
CLASSES = ('SUCCESS', 'FALSE_FEASIBLE', 'ABSTAIN_CORRECT',
           'ABSTAIN_MISSED_FEASIBLE', 'NUMERICALLY_UNRESOLVED')
FREEZE_FIELDS = ('task', 'head', 'tree', 'bases', 'code_and_protocol', 'artifacts',
                 'primary', 'required_shots', 'minimum_decisions', 'minimum_successes',
                 'maximum_false_feasible', 'outcome_joins_allowed', 'claims')
REVIEW_FIELDS = ('task', 'status', 'independent', 'reviewer', 'freeze_sha256',
                 'reviewed_head', 'reviewed_tree', 'reviewed_base',
                 'future_chemistry_attached', 'unresolved_blocking_findings', 'checks')
REVIEW_CHECKS = ('zero_fits', 'frozen_models', 'source_cohort', 'observed_endpoints',
                 'information_separation', 'stopping_intersection', 'comparators',
                 'numerical_allowances', 'contracts_acceptance', 'rights', 'clean_candidate')


def finite_tree(value):
    if isinstance(value, dict):
        for v in value.values():
            finite_tree(v)
    elif isinstance(value, list):
        for v in value:
            finite_tree(v)
    elif isinstance(value, (float, int)) and not isinstance(value, bool):
        p.md.number(value)


def verify_before_score(out, review, source_root):
    for name in ('score_receipt.json', 'score_completion.json', 'scores.json',
                 'shot_results.json', 'observed_suffix.json'):
        if (out / name).exists():
            raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    freeze, approval = p.read(out / 'freeze.json'), p.read(review)
    p.md.exact_keys(freeze, FREEZE_FIELDS)
    p.md.exact_keys(approval, REVIEW_FIELDS)
    p.md.exact_keys(approval['checks'], REVIEW_CHECKS)
    finite_tree(freeze)
    finite_tree(approval)
    if (approval['task'] != p.TASK or approval['status'] != 'APPROVED' or
            approval['independent'] is not True or not approval['reviewer'] or
            approval['future_chemistry_attached'] is not False or
            approval['unresolved_blocking_findings'] != [] or
            approval['freeze_sha256'] != p.digest(out / 'freeze.json') or
            any(v != 'PASS' for v in approval['checks'].values())):
        raise ValueError('INDEPENDENT_EXACT_FREEZE_APPROVAL_REQUIRED')
    if (freeze['task'] != p.TASK or freeze['primary'] != 'C2' or
            [freeze[k] for k in ('required_shots', 'minimum_decisions', 'minimum_successes',
                                 'maximum_false_feasible', 'outcome_joins_allowed')] != [11, 9, 9, 1, 1]
            or freeze['claims'] != list(p.CLAIMS)):
        raise ValueError('FROZEN_ACCEPTANCE_CONTRACT_REQUIRED')
    if (p.parent.git(p.ROOT, 'rev-parse', 'HEAD') != freeze['head'] or
            p.parent.git(p.ROOT, 'rev-parse', 'HEAD^{tree}') != freeze['tree'] or
            p.parent.git(p.ROOT, 'status', '--porcelain') or
            approval['reviewed_head'] != freeze['head'] or approval['reviewed_tree'] != freeze['tree'] or
            approval['reviewed_base'] != freeze['bases']['puckworks']['base']):
        raise ValueError('CLEAN_EXACT_REVIEWED_CANDIDATE_REQUIRED')
    for group, root in (('code_and_protocol', p.ROOT), ('artifacts', out)):
        for name, h in freeze[group].items():
            path = (root / name).resolve()
            if not path.is_relative_to(root.resolve()) or p.digest(path) != h:
                raise ValueError('FROZEN_BYTES_CHANGED')
    p.verify_dependencies()
    p.parent.verify_source(source_root)
    return freeze


def observed_endpoints(queries, observations):
    """Exact decimal source arithmetic on complete vials; no partial-vial chemistry."""
    if len(queries) != len(observations):
        raise ValueError('COMPLETE_OBSERVED_SUFFIX_REQUIRED')
    mass, solute = Decimal(0), Decimal(0)
    result = []
    for query, row in zip(queries, observations):
        p.md.exact_keys(row, ('shot', 'vial', 'mass_g', 'tds_percent'))
        if (query['shot'], query['vial']) != (row['shot'], row['vial']):
            raise ValueError('OBSERVATION_IDENTITY_MISMATCH')
        grams, tds = p.md.number(row['mass_g']), p.md.number(row['tds_percent'])
        if grams <= 0 or not 0 < tds <= 100:
            raise ValueError('BLOCKED_UNAVAILABLE_OBSERVED_CHEMISTRY')
        d = Decimal(str(grams)) / 1000
        if float(d) != query['mass_kg']:
            raise ValueError('OBSERVED_MASS_IDENTITY_MISMATCH')
        mass += d
        solute += d * Decimal(str(tds)) / 100
        result.append({'vial': query['vial'], 'boundary_kg': query['end_kg'],
                       'mass_kg': mass, 'solute_kg': solute, 'tds_percent': 100 * solute / mass})
    return result


def classify(decision, endpoints, contract):
    smin, qmin = Decimal(str(contract.solute_min_kg)), Decimal(str(contract.tds_min_percent))
    feasible = [r for r in endpoints if r['solute_kg'] >= smin and r['tds_percent'] >= qmin]
    oracle = feasible[0] if feasible else None
    result = {'classification': 'NUMERICALLY_UNRESOLVED',
        'oracle_state': 'OBSERVED_FEASIBLE_ENDPOINT_EXISTS' if oracle else 'NO_OBSERVED_FEASIBLE_ENDPOINT',
        'oracle_vial': oracle['vial'] if oracle else None,
        'selected_vial': decision['selected_vial'],
        'predicted_solute_margin_kg': None, 'predicted_tds_margin_pp': None,
        'measured_solute_margin_kg': None, 'measured_tds_margin_pp': None,
        'solute_deficit_mg': None, 'tds_deficit_pp': None, 'mass_regret_g': None,
        'additional_mass_to_later_feasible_g': None,
        'feature_extrapolated': bool(decision['feature_extrapolation'])}
    if decision['status'] == 'NUMERICALLY_UNRESOLVED':
        return result
    if decision['status'] == 'ABSTAIN':
        if decision['selected_vial'] is not None or decision['selected_mass_kg'] is not None:
            raise ValueError('ABSTENTION_CANNOT_HAVE_ENDPOINT')
        result['classification'] = 'ABSTAIN_MISSED_FEASIBLE' if oracle else 'ABSTAIN_CORRECT'
        return result
    if decision['status'] != 'QUALIFIED':
        raise ValueError('UNSUPPORTED_DECISION_STATUS')
    selected = next((r for r in endpoints if r['vial'] == decision['selected_vial']), None)
    if selected is None or selected['boundary_kg'] != decision['selected_mass_kg']:
        raise ValueError('ONLY_FROZEN_OBSERVED_ENDPOINTS_MAY_BE_SCORED')
    ds, dq = selected['solute_kg'] - smin, selected['tds_percent'] - qmin
    prediction = decision['prediction']
    if prediction is not None:
        finite_tree(prediction)
        result.update(predicted_solute_margin_kg=prediction['solute_margin_kg'],
                      predicted_tds_margin_pp=prediction['tds_margin_pp'])
    result.update(measured_solute_margin_kg=float(ds), measured_tds_margin_pp=float(dq),
                  solute_deficit_mg=float(max(Decimal(0), -ds) * 1000000),
                  tds_deficit_pp=float(max(Decimal(0), -dq)))
    if ds >= 0 and dq >= 0:
        result['classification'] = 'SUCCESS'
        result['mass_regret_g'] = float((selected['mass_kg'] - oracle['mass_kg']) * 1000)
    else:
        result['classification'] = 'FALSE_FEASIBLE'
        later = next((r for r in feasible if r['vial'] > selected['vial']), None)
        if later:
            result['additional_mass_to_later_feasible_g'] = float(
                (later['mass_kg'] - selected['mass_kg']) * 1000)
    return result


def aggregate(rows):
    counts = Counter(r['classification'] for r in rows)
    n = len(rows)
    decisions = counts['SUCCESS'] + counts['FALSE_FEASIBLE']
    regrets = [r['mass_regret_g'] for r in rows if r['classification'] == 'SUCCESS']
    return {
        'eligible_physical_shots': n, 'qualified_decisions': decisions,
        'successes': counts['SUCCESS'], 'false_feasible': counts['FALSE_FEASIBLE'],
        'abstentions': counts['ABSTAIN_CORRECT'] + counts['ABSTAIN_MISSED_FEASIBLE'],
        'correct_abstentions': counts['ABSTAIN_CORRECT'],
        'missed_feasible_abstentions': counts['ABSTAIN_MISSED_FEASIBLE'],
        'numerically_unresolved': counts['NUMERICALLY_UNRESOLVED'],
        'observed_feasible_shots': sum(r['oracle_state'] == 'OBSERVED_FEASIBLE_ENDPOINT_EXISTS' for r in rows),
        'feature_extrapolated_shots': sum(r['feature_extrapolated'] for r in rows),
        'successes_among_decisions': counts['SUCCESS'] / decisions if decisions else None,
        'successes_over_all_shots': counts['SUCCESS'] / n if n else None,
        'maximum_solute_deficit_mg': max((r['solute_deficit_mg'] for r in rows
                                        if r['classification'] == 'FALSE_FEASIBLE'), default=0.),
        'maximum_tds_deficit_pp': max((r['tds_deficit_pp'] for r in rows
                                     if r['classification'] == 'FALSE_FEASIBLE'), default=0.),
        'median_successful_mass_regret_g': statistics.median(regrets) if regrets else None,
        'maximum_successful_mass_regret_g': max(regrets) if regrets else None,
        'exact_oracle_choices': sum(r == 0 for r in regrets),
        'successful_choices_later_than_oracle': sum(r > 0 for r in regrets),
    }


def evaluate(queries, cohort, decisions, observations):
    finite_tree(decisions)
    for d in decisions:
        base = ('contract', 'policy', 'shot', 'status', 'selected_vial', 'selected_mass_kg',
                'prediction', 'feature_extrapolation')
        p.md.exact_keys(d, (*base, 'nominal_delta_kg') if d['policy'] == 'FIXED' else
                        (*base, 'candidates', 'inverse'))
        if d['prediction'] is not None:
            p.md.exact_keys(d['prediction'], ('start_kg', 'end_kg', 'solute_kg', 'tds_percent',
                'allowance_kg', 'numerical_qualified', 'coordinate_allowance_kg',
                'solute_margin_kg', 'tds_margin_pp'))
        for c in d.get('candidates', []):
            p.md.exact_keys(c, ('vial', 'mass_kg', 'status'))
    shots = sorted(c['shot'] for c in cohort if c['eligible'])
    expected = {(c.name, policy, shot) for c in p.CONTRACTS for policy in p.POLICIES for shot in shots}
    keys = [(d['contract'], d['policy'], d['shot']) for d in decisions]
    if len(keys) != len(set(keys)) or set(keys) != expected:
        raise ValueError('EXACT_FROZEN_DECISION_MATRIX_REQUIRED')
    index = {(o['shot'], o['vial']): o for o in observations}
    if len(index) != len(observations) or set(index) != {(q['shot'], q['vial']) for q in queries}:
        raise ValueError('EXACT_OBSERVATION_MATRIX_REQUIRED')
    endpoints = {shot: observed_endpoints(
        [q for q in queries if q['shot'] == shot],
        [index[q['shot'], q['vial']] for q in queries if q['shot'] == shot]) for shot in shots}
    private = []
    for d in decisions:
        contract = next(c for c in p.CONTRACTS if c.name == d['contract'])
        row = classify(d, endpoints[d['shot']], contract)
        private.append({k: d[k] for k in ('contract', 'policy', 'shot')} | row)
    metrics = {c.name: {policy: aggregate([r for r in private
        if r['contract'] == c.name and r['policy'] == policy]) for policy in p.POLICIES}
        for c in p.CONTRACTS}
    c2 = metrics['PRIMARY']['C2']
    adequate = (c2['qualified_decisions'] >= 9 and c2['successes'] >= 9 and c2['false_feasible'] <= 1)
    disposition = (NOT_ADJUDICATED if len(shots) != 11 else ADEQUATE if adequate else INADEQUATE)
    return {'task': p.TASK, 'disposition': disposition,
            'primary_decision_adequacy': 'NOT_ADJUDICATED' if len(shots) != 11 else 'PASS' if adequate else 'FAIL',
            'independent_unit': 'PHYSICAL_SHOT', 'N': len(shots), 'metrics': metrics,
            'claims': list(p.CLAIMS), 'scientific_outcome_joins': 1,
            'new_fits': 0, 'optimizer_calls': 0, 'native_ewp_runs': 0,
            'production_adoption': False, 'automatic_successor': None,
            'fixed_rule_prediction_margins': 'NOT_APPLICABLE_NO_CHEMISTRY_PREDICTOR'}, private


def score(out, review, source_root):
    out = p.parent.private(out)
    verify_before_score(out, review, source_root)
    decisions_bytes = (out / 'decisions.json').read_bytes()
    p.write(out / 'score_receipt.json', {'task': p.TASK, 'status': 'STARTED',
        'freeze_sha256': p.digest(out / 'freeze.json'), 'review_sha256': p.digest(review),
        'decisions_sha256': p.digest(out / 'decisions.json')})
    queries, cohort, decisions = (p.read(out / n) for n in
                                 ('queries.json', 'cohort.json', 'decisions.json'))
    selected = {(q['shot'], q['vial']) for q in queries}
    # Sole scientific outcome access. No decision construction or inverse calls here.
    observations = [{'shot': r['shot'], 'vial': r['vial'], 'mass_g': r['mass_g'],
                     'tds_percent': r['tds_pct']}
                    for r in p.parent.gc.parse_source(Path(source_root) / 'exp13.csv')
                    if (r['shot'], r['vial']) in selected]
    result, rows = evaluate(queries, cohort, decisions, observations)
    if (out / 'decisions.json').read_bytes() != decisions_bytes:
        raise ValueError('FROZEN_DECISIONS_MUTATED_PRESERVE_EXPOSED_RUN')
    result['conditioning'] = p.read(out / 'counts.json')
    p.write(out / 'observed_suffix.json', observations)
    p.write(out / 'shot_results.json', rows)
    p.write(out / 'scores.json', result)
    p.write(out / 'score_completion.json', {'task': p.TASK, 'status': 'COMPLETE',
        'scientific_outcome_joins': 1,
        'files': {n: p.digest(out / n) for n in
                  ('score_receipt.json', 'decisions.json', 'observed_suffix.json', 'shot_results.json', 'scores.json')}})
    return result


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--out', type=Path, required=True)
    cli.add_argument('--review', type=Path, required=True)
    cli.add_argument('--source-root', type=Path, required=True)
    args = cli.parse_args()
    try:
        result = score(args.out, args.review, args.source_root)
    except (ValueError, OSError, TypeError, KeyError):
        cli.error('Score blocked; preserve private receipts and inspect without rescoring.')
    print(result['disposition'])


if __name__ == '__main__':
    main()

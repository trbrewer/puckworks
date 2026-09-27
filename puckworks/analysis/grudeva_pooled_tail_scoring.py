"""Task-007 decisions and once-only outcome join; report reads saved results only."""
from __future__ import annotations

from collections import Counter
import math
from pathlib import Path

from . import grudeva_pooled_tail_delivery as p

INCOMPLETE = 'SOURCE_SUPPORT_INCOMPLETE'
UNRESOLVED = 'NUMERICALLY_UNRESOLVED'


def conjunction(values):
    values = list(values)
    if 'FAIL' in values:
        return 'FAIL'
    if values and all(v == 'PASS' for v in values):
        return 'PASS'
    return INCOMPLETE if INCOMPLETE in values else UNRESOLVED


def leq(lo, hi, threshold):
    if lo is None or hi is None:
        return INCOMPLETE
    return 'PASS' if hi <= threshold else 'FAIL' if lo > threshold else UNRESOLVED


def mean(values):
    return math.fsum(values)/len(values)


def shot_metrics(queries, outcomes, predictions):
    """Partial R lower bounds use full mass; partial bias never bounds full bias."""
    mass_known = all(q['mass_kg'] is not None for q in queries)
    total = math.fsum(q['mass_kg'] for q in queries) if mass_known else None
    rows = []
    complete = True
    for q, o, r in zip(queries, outcomes, predictions):
        m, pred = q['mass_kg'], r['prediction']
        good = (m is not None and pred is not None and r['status'] == 'QUALIFIED'
                and pred['numerical_qualified'] and pred['allowance_kg'] <= 1e-9)
        if good:
            vals = [pred['solute_kg'], pred['allowance_kg']]
            if m > 0:
                vals += [pred['tds_percent']]
            if any(not math.isfinite(p.md.number(v)) for v in vals) or pred['allowance_kg'] < 0:
                raise ValueError('NONFINITE_OR_NEGATIVE_PREDICTION_ALLOWANCE')
        if m == 0:
            if not good or pred['solute_kg'] != 0 or pred['tds_percent'] is not None:
                complete = False
            continue
        if not good or o['q'] is None or m is None:
            complete = False
            continue
        concentration = p.md.number(o['q'])
        if not 0 <= concentration <= 1:
            raise ValueError('OUTCOME_MASS_FRACTION_REQUIRED')
        e = pred['tds_percent']-100*concentration
        a = 100*pred['allowance_kg']/m
        rows.append({'vial': q['vial'], 'mass_kg': m, 'e_pp': e, 'allowance_pp': a,
                     'observed_solute_g': 1000*m*concentration,
                     'predicted_solute_g': 1000*pred['solute_kg'],
                     'solute_error_g': 1000*(pred['solute_kg']-m*concentration),
                     'solute_allowance_g': 1000*pred['allowance_kg']})
    complete = complete and total is not None and total > 0 and bool(rows)
    diagnostic = None
    if rows:
        mass = math.fsum(r['mass_kg'] for r in rows)
        R = math.sqrt(math.fsum(r['mass_kg']*r['e_pp']**2 for r in rows)/mass)
        B = math.fsum(r['mass_kg']*r['e_pp'] for r in rows)/mass
        Ra = math.sqrt(math.fsum(r['mass_kg']*r['allowance_pp']**2 for r in rows)/mass)
        Ba = math.fsum(r['mass_kg']*r['allowance_pp'] for r in rows)/mass
        # Outward padding covers floating metric accumulation, not assay uncertainty.
        pad = 128*math.ulp(max(1., R, abs(B)))
        Ra += pad; Ba += pad
        cumulative = []; value = 0.
        for r in rows:
            value += r['solute_error_g']; cumulative.append(value)
        diagnostic = {'R_pp': R, 'B_pp': B, 'absB_pp': abs(B), 'R_allowance_pp': Ra, 'B_allowance_pp': Ba,
            'R_bounds_pp': [max(0., R-Ra), R+Ra],
            'absB_bounds_pp': [max(0., abs(B)-Ba), abs(B)+Ba],
            'B_bounds_pp': [B-Ba, B+Ba], 'mass_kg': mass,
            'solute_rmse_g': math.sqrt(mean([r['solute_error_g']**2 for r in rows])),
            'solute_mae_g': mean([abs(r['solute_error_g']) for r in rows]),
            'signed_suffix_error_g': value, 'absolute_suffix_error_g': abs(value),
            'max_abs_cumulative_error_g': max(map(abs, cumulative)),
            'observed_suffix_solute_g': math.fsum(r['observed_solute_g'] for r in rows),
            'predicted_suffix_solute_g': math.fsum(r['predicted_solute_g'] for r in rows),
            'suffix_solute_allowance_g': math.fsum(r['solute_allowance_g'] for r in rows)}
    lower_R = 0.
    if rows and total is not None and total > 0:
        low = math.sqrt(math.fsum(r['mass_kg']*max(0., abs(r['e_pp'])-r['allowance_pp'])**2 for r in rows)/total)
        lower_R = max(0., low-128*math.ulp(max(1., low)))
    bounds = {'R_pp': lower_R, 'absB_pp': diagnostic['absB_bounds_pp'][0] if complete else 0.}
    individual = conjunction([leq(*diagnostic['R_bounds_pp'], 1.), leq(*diagnostic['absB_bounds_pp'], .5)]) if complete else (
        'FAIL' if lower_R > 1. else INCOMPLETE)
    return {'complete': complete, 'full': diagnostic if complete else None,
            'supported_subset_diagnostic': diagnostic, 'full_scope_lower_bounds': bounds,
            'adequacy': individual, 'declared_mass_kg': total, 'declared_windows': len(queries),
            'scored_positive_windows': len(rows), 'rows': rows}


def aggregate(shots):
    N = len(shots); required = math.ceil(.75*N)
    complete = N > 0 and all(s['complete'] for s in shots)
    lower = {k: math.fsum(s['full_scope_lower_bounds'][k] for s in shots)/N if N else 0. for k in ('R_pp', 'absB_pp')}
    wins = sum(s['adequacy'] == 'PASS' for s in shots)
    possible = sum(s['adequacy'] != 'FAIL' for s in shots)
    metrics = None
    if complete:
        fields = ('R_pp', 'B_pp', 'absB_pp', 'R_allowance_pp', 'B_allowance_pp', 'solute_rmse_g', 'solute_mae_g',
            'signed_suffix_error_g', 'absolute_suffix_error_g', 'max_abs_cumulative_error_g',
            'observed_suffix_solute_g', 'predicted_suffix_solute_g', 'suffix_solute_allowance_g')
        metrics = {k: mean([s['full'][k] for s in shots]) for k in fields}
        for k in ('R_bounds_pp', 'B_bounds_pp', 'absB_bounds_pp'):
            metrics[k] = [mean([s['full'][k][i] for s in shots]) for i in (0, 1)]
        tests = {'mean_R': leq(*metrics['R_bounds_pp'], 1.),
                 'mean_absB': leq(*metrics['absB_bounds_pp'], .5),
                 'individual_shots': 'PASS' if wins >= required else 'FAIL' if possible < required else UNRESOLVED}
    else:
        tests = {'mean_R': 'FAIL' if lower['R_pp'] > 1. else INCOMPLETE,
                 'mean_absB': 'FAIL' if lower['absB_pp'] > .5 else INCOMPLETE,
                 'individual_shots': 'FAIL' if possible < required else INCOMPLETE}
    subset = [s['supported_subset_diagnostic'] for s in shots]
    return {'full_scope_metrics': metrics, 'complete_panel': complete, 'declared_shots': N,
        'complete_shots': sum(s['complete'] for s in shots), 'required_adequate_shots': required,
        'definite_adequate_shots': wins, 'possible_adequate_shots': possible,
        'full_scope_lower_bounds': lower, 'adequacy_components': tests, 'adequacy': conjunction(tests.values()),
        'supported_subset_diagnostic': {k: mean([s[k] for s in subset]) for k in ('R_pp', 'absB_pp', 'B_pp')}
            if subset and all(s is not None for s in subset) else None}


def increment(candidate, reference, cs, rs):
    if not candidate['complete_panel'] or not reference['complete_panel']:
        return {'status': INCOMPLETE}
    c, r = candidate['full_scope_metrics'], reference['full_scope_metrics']
    clo, chi = c['R_bounds_pp']; rlo, rhi = r['R_bounds_pp']
    gain = [rlo-chi, rhi-clo]
    nearzero = rlo <= 1e-12
    relative = None if nearzero else [1-chi/rlo, 1-clo/rhi]
    definite = sum(a['full']['R_bounds_pp'][1] < b['full']['R_bounds_pp'][0] for a, b in zip(cs, rs))
    possible = sum(a['full']['R_bounds_pp'][0] < b['full']['R_bounds_pp'][1] for a, b in zip(cs, rs))
    required = math.ceil(.75*len(cs))
    deterioration = [c['absB_bounds_pp'][0]-r['absB_bounds_pp'][1], c['absB_bounds_pp'][1]-r['absB_bounds_pp'][0]]
    components = {'absolute_gain': leq(-gain[1], -gain[0], -.10),
        'relative_gain': 'FAIL' if nearzero else leq(-relative[1], -relative[0], -.15),
        'paired_shot_wins': 'PASS' if definite >= required else 'FAIL' if possible < required else UNRESOLVED,
        'abs_bias_deterioration': leq(*deterioration, .10)}
    return {'status': conjunction(components.values()), 'components': components,
        'R_improvement_pp': r['R_pp']-c['R_pp'], 'R_improvement_bounds_pp': gain,
        'relative_improvement': None if nearzero else 1-c['R_pp']/r['R_pp'], 'relative_improvement_bounds': relative,
        'mean_absB_deterioration_pp': c['absB_pp']-r['absB_pp'], 'mean_absB_deterioration_bounds_pp': deterioration,
        'definite_paired_wins': definite, 'possible_paired_wins': possible, 'required_wins': required}


def evaluate(queries, outcomes, predictions, cohort):
    primary = sorted(r['shot'] for r in cohort if r['eligible'])
    if len(cohort) != 13 or {r['shot'] for r in cohort} != set(range(1, 14)):
        raise ValueError('NOMINAL_13_SHOT_ACCOUNTING_REQUIRED')
    expected = [(r['shot'], i) for r in cohort if r['eligible'] for i in range(r['k2']+1, 17)]
    if len(set(expected)) != len(expected) or set(predictions) != set(p.md.ARMS):
        raise ValueError('EXACT_ARM_MATRIX_REQUIRED')
    def index(rows):
        keys = [(r['shot'], r['vial']) for r in rows]
        if len(keys) != len(expected) or set(keys) != set(expected):
            raise ValueError('FROZEN_TARGET_DENOMINATOR_REQUIRED')
        return dict(zip(keys, rows))
    qi, oi = index(queries), index(outcomes)
    for q in queries:
        p.checked_query(q)
    pi = {a: index(rows) for a, rows in predictions.items()}
    private_shots, arms, numerical, supported = {}, {}, {}, {}
    for a in p.md.ARMS:
        private_shots[a] = []
        for key, row in pi[a].items():
            if any(row[k] != qi[key][k] for k in qi[key]):
                raise ValueError('PREDICTION_COORDINATE_IDENTITY_MISMATCH')
        for shot in primary:
            keys = sorted(k for k in expected if k[0] == shot)
            private_shots[a].append({'shot': shot, **shot_metrics([qi[k] for k in keys], [oi[k] for k in keys], [pi[a][k] for k in keys])})
        arms[a] = aggregate(private_shots[a])
        supported[a] = sum(r['prediction'] is not None for r in pi[a].values())
        numerical[a] = sum(r['status'] == 'QUALIFIED' and r['prediction'] is not None and r['prediction']['numerical_qualified']
                           and 0 <= r['prediction']['allowance_kg'] <= 1e-9 for r in pi[a].values())
    full = all(v['complete_panel'] for v in arms.values())
    num = 'PASS' if expected and all(n == len(expected) for n in numerical.values()) else UNRESOLVED
    coverage = 'PASS' if len(primary) >= 10 and full and num == 'PASS' else 'EVIDENCE_LIMITED'
    increments = {name: increment(arms['C2'], arms[ref], private_shots['C2'], private_shots[ref]) for name, ref in (('I0', 'C0'), ('I1', 'C1'))}
    A = {a: v['adequacy'] for a, v in arms.items()}
    label = 'MIXED_BLOCKED_OR_UNRESOLVED'
    if all(v == 'FAIL' for v in A.values()):
        label = 'FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT'
    elif coverage == 'PASS' and num == 'PASS':
        if A['C2'] == 'PASS' and all(v['status'] == 'PASS' for v in increments.values()):
            label = 'FROZEN_C2_TRANSFER_EARNED_ON_QUALIFIED_POOLED_PREFIX_COHORT'
        elif any(A[arm] == 'PASS' and increments[inc]['status'] == 'FAIL' for arm, inc in (('C0', 'I0'), ('C1', 'I1'))):
            label = 'SIMPLER_FROZEN_TRANSFER_SUFFICIENT_ON_QUALIFIED_COHORT'
        elif A['C2'] == 'PASS' and not any(A[a] == 'PASS' for a in ('C0', 'C1')):
            label = 'FROZEN_C2_TRANSFER_ADEQUATE_INCREMENT_NOT_ESTABLISHED'
    extrapolation = {}
    for a, rows in pi.items():
        flags = {s: set(f for r in rows.values() if r['shot'] == s for f in r['feature_extrapolation']) for s in primary}
        extrapolation[a] = {'shots': sum(bool(f) for f in flags.values()),
            'feature_counts_by_shot': dict(Counter(f for fs in flags.values() for f in fs)),
            'suffix_windows': sum(bool(r['feature_extrapolation']) for r in rows.values())}
    return {'task': p.TASK, 'disposition': label, 'primary_candidate': 'C2',
        'decision_vector': {'coverage': coverage, 'numerical': num, 'adequacy': A,
                            'I0': increments['I0']['status'], 'I1': increments['I1']['status']},
        'coverage': {'nominal_shots': 13, 'eligible_shots': len(primary), 'minimum_required': 10,
            'intended_suffix_windows': len(expected), 'supported_by_arm': supported, 'numerically_qualified_by_arm': numerical,
            'positive_suffix_windows': sum(q['mass_kg'] is not None and q['mass_kg'] > 0 for q in queries),
            'target_mass_kg': math.fsum(q['mass_kg'] for q in queries) if all(q['mass_kg'] is not None for q in queries) else None,
            'complete_panel': full}, 'arms': arms, 'increments': increments, 'feature_extrapolation': extrapolation,
        'claims': list(p.CLAIMS), 'physical_validation': 'NOT_ESTABLISHED',
        'scientific_score_passes': 1, 'real_fits': 0, 'optimizer_calls': 0, 'native_runs': 0,
        'merge_authorized': False, 'production_adoption_authorized': False, 'successor_authorized': False}, private_shots


def project_outcomes(records, queries):
    selected = {(q['shot'], q['vial']) for q in queries}
    result = []
    for r in records:
        if (r['shot'], r['vial']) in selected:
            status = p.chemistry_status(r)
            result.append({'shot': r['shot'], 'vial': r['vial'], 'chemistry_status': status,
                'q': r['tds_pct']/100 if status == 'AVAILABLE' else None,
                'solute_kg': 0. if status == 'STRUCTURAL_ZERO' else r['mass_g']/1000*r['tds_pct']/100 if status == 'AVAILABLE' else None})
    return result


def reference_diagnostic(reference, queries, outcomes, cohort):
    ri = {(r['shot'], r['vial']): r['retained_row'] for r in reference['rows']}
    preds = []
    for q in queries:
        r = ri[(q['shot'], q['vial'])]; m = q['mass_kg']
        preds.append(dict(q, status='QUALIFIED', feature_extrapolation=[], prediction={
            'solute_kg': r['yhat_g']/1000, 'tds_percent': 100*r['yhat_g']/(1000*m) if m else None,
            'allowance_kg': r['numerical_allowance_g']/1000,
            'numerical_qualified': r['numerical_allowance_g']/1000 <= 1e-9}))
    # No selection comparisons: only a same-support diagnostic aggregate.
    oi = {(o['shot'], o['vial']): o for o in outcomes}; pi = {(r['shot'], r['vial']): r for r in preds}
    shots = []
    for c in cohort:
        if c['eligible']:
            qs = [q for q in queries if q['shot'] == c['shot']]
            shots.append({'shot': c['shot'], **shot_metrics(qs, [oi[(q['shot'], q['vial'])] for q in qs], [pi[(q['shot'], q['vial'])] for q in qs])})
    return {'label': reference['label'], 'same_suffix_only': True, 'fair_ablation': False,
            'manifest_sha256': reference['manifest_sha256'], 'aggregate': aggregate(shots)}, shots


def verify_before_score(out, review, source_root, consumer_root):
    if any((out/n).exists() for n in ('score_receipt.json', 'scores.json', 'score_completion.json')):
        raise ValueError('DUPLICATE_SCORE_OR_PRESERVED_FAILED_ATTEMPT')
    f, r = p.read(out/'freeze.json'), p.read(review)
    if (r.get('task') != p.TASK or r.get('status') != 'APPROVED' or r.get('independent') is not True
            or not r.get('reviewer') or r.get('unresolved_blocking_findings') != []
            or r.get('future_chemistry_attached') is not False or r.get('freeze_sha256') != p.digest(out/'freeze.json')):
        raise ValueError('FRESH_INDEPENDENT_EXACT_FREEZE_APPROVAL_REQUIRED')
    for name, root, label in (('producer', p.ROOT, 'reviewed'), ('consumer', Path(consumer_root), 'ewp_reviewed')):
        if (p.git(root, 'rev-parse', 'HEAD') != f[name+'_commit'] or p.git(root, 'rev-parse', 'HEAD^{tree}') != f[name+'_tree']
                or r.get(label+'_head') != f[name+'_commit'] or r.get(label+'_tree') != f[name+'_tree']
                or r.get(label+'_base') != f[name+'_base']):
            raise ValueError('EXACT_REVIEWED_CANDIDATE_REQUIRED')
    for group, root in (('code_and_protocol', p.ROOT), ('consumer_files', Path(consumer_root)), ('artifacts', out)):
        for name, h in f[group].items():
            path = (root/name).resolve()
            if not path.is_relative_to(root.resolve()) or p.digest(path) != h:
                raise ValueError('FROZEN_BYTES_CHANGED:'+name)
    p.verify_dependencies(); p.verify_source(source_root)
    return f


def score(out, review, source_root, consumer_root):
    out = p.private(out)
    verify_before_score(out, review, source_root, consumer_root)
    p.write(out/'score_receipt.json', {'task': p.TASK, 'status': 'STARTED',
        'freeze_sha256': p.digest(out/'freeze.json'), 'review_sha256': p.digest(review),
        'predictions_sha256': p.digest(out/'predictions.json')})
    queries, cohort = p.read(out/'queries.json'), p.read(out/'cohort.json')
    # Sole outcome projection/join, after exclusive start and independent approval.
    outcomes = project_outcomes(p.gc.parse_source(Path(source_root)/'exp13.csv'), queries)
    expected = {(s['shot'], s['vial']): s['chemistry_status'] for s in p.read(out/'support.json')}
    if {(s['shot'], s['vial']): s['chemistry_status'] for s in outcomes} != expected:
        raise ValueError('FROZEN_SOURCE_VALIDITY_DRIFT')
    result, shots = evaluate(queries, outcomes, p.read(out/'predictions.json'), cohort)
    if (out/'reference.json').exists():
        result['optional_reference_diagnostic'], shots['SOURCE_TRAINED_MASS_DIAGNOSTIC'] = reference_diagnostic(
            p.read(out/'reference.json'), queries, outcomes, cohort)
    else:
        result['optional_reference_diagnostic'] = {'status': 'NOT_AVAILABLE_NOT_BLOCKING'}
    result['conditioning'] = p.read(out/'counts.json')
    p.write(out/'observed_suffix.json', outcomes); p.write(out/'shot_results.json', shots)
    p.write(out/'scores.json', result)
    p.write(out/'score_completion.json', {'task': p.TASK, 'status': 'COMPLETE', 'scientific_score_passes': 1,
        'scores_sha256': p.digest(out/'scores.json'), 'shot_results_sha256': p.digest(out/'shot_results.json'),
        'observed_suffix_sha256': p.digest(out/'observed_suffix.json'), 'score_receipt_sha256': p.digest(out/'score_receipt.json')})
    print(result['disposition'])


def report(out):
    out = Path(out); completion = p.read(out/'score_completion.json')
    if completion['status'] != 'COMPLETE' or completion['scores_sha256'] != p.digest(out/'scores.json'):
        raise ValueError('RETAINED_COMPLETED_SCORE_REQUIRED')
    return p.read(out/'scores.json')

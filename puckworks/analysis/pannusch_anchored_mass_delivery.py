"""SCI-MD-MASS-DELIVERY-003: private preparation, exact freeze and audited scoring.

No fitting or optimizer calls. Only the scorer attaches later TDS. Ordinary tests
use synthetic inputs; source-derived states, rows and shot reports stay private.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import subprocess

import numpy as np

from . import anchored_mass_delivery as md
from . import pannusch_mass_delivery as old
from . import pannusch_conditioned_mass_delivery as previous

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/sci_md_mass_delivery_003'
TASK = 'SCI-MD-MASS-DELIVERY-003'
CAMPAIGN = 'PREDICTION_2022_03'
SUFFIX = (2, 3, 5, 7, 10)
SHOTS = tuple(c.replace('-C', '-E')+f'-R{r}' for c in old.PRIMARY for r in (1, 2, 3))
ARMS = ('UNANCHORED_MASS', 'ANCHORED_MASS', 'UNANCHORED_EMPIRICAL',
        'ANCHORED_EMPIRICAL', 'UNANCHORED_SETTING_EMPIRICAL',
        'ANCHORED_SETTING_EMPIRICAL', 'ANCHOR_PERSISTENCE')
BASE_PATHS = {
    'MASS': 'docs/analysis/sci_md_mass_delivery_001/models/MASS.json',
    'EMPIRICAL': 'docs/analysis/sci_md_mass_delivery_001/models/BOUNDARY_AWARE_EMPIRICAL.json',
    'SETTING_EMPIRICAL': 'docs/analysis/sci_md_mass_delivery_002/models/SETTING_AWARE_EMPIRICAL.json'}
QUERY_KEYS = ('campaign', 'condition', 'shot', 'fraction', 'b0', 'b1',
              'temperature_K', 'source_flow_setting_code')
write_json, digest, canonical_hash = old.write_json, old.digest, old.canonical_hash
FREEZE_PATHS = (
    'puckworks/analysis/anchored_mass_delivery.py',
    'puckworks/analysis/pannusch_anchored_mass_delivery.py',
    'puckworks/analysis/mass_delivery.py',
    'puckworks/analysis/conditioned_mass_delivery.py',
    'puckworks/analysis/pannusch_mass_delivery.py',
    'puckworks/analysis/pannusch_conditioned_mass_delivery.py',
    'tools/pannusch2024_reconstruct.py', 'tools/data_availability_preflight.py',
    'tests/test_anchored_mass_delivery.py',
    'docs/analysis/sci_md_mass_delivery_003/MODEL_CARD.md',
    'docs/analysis/sci_md_mass_delivery_003/PROTOCOL.md',
    'docs/analysis/sci_md_mass_delivery_003/BASES.json',
    'docs/analysis/sci_md_mass_delivery_003/INFORMATION_CONTRACT.json',
    'docs/analysis/sci_md_mass_delivery_003/DATA_AVAILABILITY_PREFLIGHT.json',
) + tuple(BASE_PATHS.values())


def information_contract():
    contract = json.loads((DOC/'INFORMATION_CONTRACT.json').read_text())
    if (contract['status'] != 'FROZEN_BEFORE_ANCHOR_EXTRACTION'
            or contract['anchor_fraction_id'] != 1 or contract['outcome_fraction_ids'] != list(SUFFIX)
            or contract['conditions'] != list(old.PRIMARY)):
        raise ValueError('INFORMATION_CONTRACT_MISMATCH')
    for path, sha in contract['files'].items():
        if digest(ROOT/path) != sha:
            raise ValueError('INFORMATION_CONTRACT_DRIFT')
        content = subprocess.check_output(['git', 'show', contract['contract_commit']+':'+path], cwd=ROOT)
        if old.hashlib.sha256(content).hexdigest() != sha:
            raise ValueError('CONTRACT_NOT_COMMITTED_BEFORE_EXTRACTION')
    return contract


def load_bases():
    identity = json.loads((DOC/'BASES.json').read_text())
    result = {}
    for name, path in BASE_PATHS.items():
        if digest(ROOT/path) != identity['reused_files'][path]:
            raise ValueError('FROZEN_PREDECESSOR_ARTIFACT_DRIFT')
        result[name] = md.FrozenBase.load(ROOT/path)
    return result


def source_coordinates(paths, designs):
    coords = [r for r in previous.coordinates(CAMPAIGN, paths, designs)
              if r['condition'] in old.PRIMARY]
    expected = {(s, f) for s in SHOTS for f in (1,)+SUFFIX}
    if len(coords) != len(expected) or {(r['shot'], r['fraction']) for r in coords} != expected:
        raise ValueError('SOURCE_IDENTITY_MATRIX_MISMATCH')
    for r in coords:
        if (r['source_id'] != 'P24-MAT-PRED' or r['mass_basis'] != 'MEASURED_MASS_G'
                or r['mass_prefix'] != 'SOURCE_SHOT_mE_cum_ALL_INTERVENING_VIALS'
                or r['collection_count'] != 11):
            raise ValueError('UNQUALIFIED_COLLECTION_OPERATOR')
        if r['fraction'] == 1 and (r['b0'] != 0 or r['t0'] != 0 or r['b1'] != r['mass_kg']):
            raise ValueError('FRACTION_ONE_COLLECTION_ORIGIN_MISMATCH')
        if abs(r['b1']-r['b0']-r['mass_kg']) > 1e-15:
            raise ValueError('MASS_INTERVAL_MISMATCH')
    return coords


def selected_assays(source_rows, coords, fractions):
    """Parse values only after filtering the authorized identities and fractions.

    A CSV parser can internally read later fields, but this projection returns
    only the selected information role. Missing rows/chemistry stay missing.
    """
    if any(r['fraction'] not in fractions for r in coords):
        raise ValueError('ASSAY_ROLE_VIOLATION')
    identities = {(r['shot'], r['fraction']) for r in coords}
    chosen = [r for r in source_rows if r['campaign_id'] == CAMPAIGN
              and r['analyte'] == 'TDS' and int(r['fraction_id']) in fractions
              and (r['shot_id'], int(r['fraction_id'])) in identities]
    chosen = old.deduplicate(chosen, ('campaign_id', 'shot_id', 'fraction_id', 'analyte'))
    index = {(r['shot_id'], int(r['fraction_id'])): r for r in chosen}
    out = []
    for c in coords:
        row = index.get((c['shot'], c['fraction']))
        value, rounding, reason = None, 0., 'MISSING_ASSAY'
        if row is not None:
            if (row['condition_id'] != c['condition'] or row['source_id'] != c['source_id']
                    or row['concentration_unit'] != 'percent'):
                raise ValueError('ASSAY_IDENTITY_OR_UNIT_MISMATCH')
            if abs(float(row['fraction_liquid_g_or_ml'])*.001-c['mass_kg']) > 5.01e-12:
                raise ValueError('ASSAY_MEASURED_MASS_MISMATCH')
            raw = row['measured_concentration']
            reason = 'MISSING_CHEMISTRY' if raw == '' else 'INVALID_TDS_ASSAY'
            if row['validity'] == 'VALID' and raw != '':
                value = float(old.concentration_to_fraction(float(raw), 'percent'))
                rounding = c['mass_kg']*5e-11+value*5e-12+5e-15
                derived = float(row['derived_analyte_mass_mg'])*1e-6
                if abs(c['mass_kg']*value-derived) > rounding+1e-17:
                    raise ValueError('SOURCE_SOLUTE_ROUNDING_MISMATCH')
                reason = ''
        out.append(dict(c, eligible=value is not None, q=value,
                        supplied_tds_percent=float(row['measured_concentration']) if value is not None else None,
                        solute_kg=c['mass_kg']*value if value is not None else None,
                        source_rounding_allowance_kg=rounding, unsupported_reason=reason))
    return out


def extract_anchors(source_rows, coords):
    """Prediction-facing output is minimal anchor objects, never full shot rows."""
    selected = [c for c in coords if c['fraction'] == 1]
    result, support = {}, []
    for r in selected_assays(source_rows, selected, (1,)):
        a = None
        if r['eligible']:
            a = md.AnchorInput(r['shot'], r['source_id'], 1, r['b0'], r['b1'], r['supplied_tds_percent'],
                'MEASURED_MASS_G_CONVERTED_TO_KG', old.RIGHTS, 'MEASURED_SOURCE_ANCHOR_INPUT')
        result[r['shot']] = a
        support.append({'shot': r['shot'], 'available': a is not None,
                        'reason': r['unsupported_reason'],
                        'displayed_source_rounding_allowance_kg': r['source_rounding_allowance_kg']})
    return result, support


def project_queries(coords):
    return [{k: r[k] for k in QUERY_KEYS} for r in coords if r['fraction'] in SUFFIX]


def predict_bundle(bases, anchors, queries):
    """No later chemistry accepted, including in ostensibly optional fields."""
    if (set(bases) != set(BASE_PATHS) or any(set(q) != set(QUERY_KEYS) for q in queries)
            or any(q['fraction'] not in SUFFIX for q in queries)):
        raise ValueError('COORDINATE_ONLY_SUFFIX_QUERY_REQUIRED')
    if any(a is not None and (type(a) is not md.AnchorInput or a.shot_id != s)
           for s, a in anchors.items()):
        raise ValueError('ANCHOR_SHOT_IDENTITY_MISMATCH')
    predictions = {arm: [] for arm in ARMS}
    states, failures = {}, {}
    for q in queries:
        a = anchors.get(q['shot'])
        interval = md.IntervalQuery(q['b0'], q['b1'])
        for arm in ARMS:
            record = dict(q, in_domain=False, predicted_solute_kg=None,
                integration_allowance_kg=0., numerical_qualified=False,
                unsupported_reason='', anchor_error_amplification=None, amplification_allowance=None)
            try:
                if arm == 'ANCHOR_PERSISTENCE':
                    if a is None:
                        raise ValueError('ANCHOR_UNAVAILABLE')
                    if interval.start_kg < a.end_kg:
                        raise ValueError('QUERY_BEFORE_ANCHOR_COMPLETION')
                    # Common evaluation domain; no unlimited persistence rescue.
                    if interval.end_kg > bases['MASS'].curve().domain_kg[1]:
                        raise ValueError('OUTSIDE_FROZEN_MASS_DOMAIN')
                    value = a.tds_percent/100*(interval.end_kg-interval.start_kg)
                    error = md.roundoff(value) if value else 0.
                    amp, amp_error = 1., 0.
                else:
                    name = arm.split('_', 1)[1]
                    setting = md.NominalSetting(q['temperature_K'], q['source_flow_setting_code']) if name == 'SETTING_EMPIRICAL' else None
                    if arm.startswith('ANCHORED_'):
                        if a is None:
                            raise ValueError('ANCHOR_UNAVAILABLE')
                        key = (name, q['shot'])
                        if key not in states and key not in failures:
                            try:
                                states[key] = md.anchor(bases[name], a, setting=setting)
                            except ValueError as exc:
                                failures[key] = str(exc)
                        if key in failures:
                            raise ValueError(failures[key])
                        state = states[key]
                        if state.setting != setting:
                            raise ValueError('INCONSISTENT_SHOT_SETTING')
                        p = state.predict_intervals((interval,))[0]
                        value, error = p.solute_kg, p.numerical_allowance_kg
                        amp, amp_error = p.anchor_error_amplification, p.amplification_allowance
                    else:
                        value, error = md.integral(bases[name].curve(setting), q['b0'], q['b1'])
                        amp, amp_error = None, None
                record.update(in_domain=True, predicted_solute_kg=value,
                    integration_allowance_kg=error, numerical_qualified=error <= 1e-9,
                    anchor_error_amplification=amp, amplification_allowance=amp_error)
            except (ValueError, FloatingPointError) as exc:
                record['unsupported_reason'] = str(exc)
            predictions[arm].append(record)
    return predictions, {name+'/'+shot: state.to_dict() for (name, shot), state in states.items()}


def prepare(out):
    out = Path(out).resolve()
    if out.is_relative_to(ROOT):
        raise ValueError('PRIVATE_EVIDENCE_MUST_REMAIN_OUTSIDE_GIT')
    contract = information_contract()
    out.mkdir(parents=True, exist_ok=False)
    write_json(out/'information_contract.json', contract)
    historical = json.loads((ROOT/'docs/analysis/sci_md_mass_delivery_002/SOURCE.json').read_text())
    old.verify_registers(historical)
    paths = old.source_paths()
    if {k: digest(v) for k, v in paths.items()} != historical['source_files']:
        raise ValueError('PREDECESSOR_SOURCE_IDENTITY_DRIFT')
    designs, qualification = previous.qualify_settings(paths)
    coords = source_coordinates(paths, designs)
    # No full-chemistry attachment call: only fraction one values are projected.
    anchors, support = extract_anchors(old.rows(old.DATA/'prediction_fraction_replicates.csv'), coords)
    bases = load_bases()
    queries = project_queries(coords)
    predictions, states = predict_bundle(bases, anchors, queries)
    write_json(out/'coordinates.json', coords)
    write_json(out/'anchors.json', {s: asdict(a) if a else None for s, a in anchors.items()})
    write_json(out/'anchor_support.json', support)
    write_json(out/'states.json', states)
    write_json(out/'predictions.json', predictions)
    source = {'task': TASK, 'source_files': historical['source_files'],
        'registers': historical['registers'], 'rights': old.RIGHTS,
        'setting_qualification': qualification, 'metadata_summary': historical['metadata_summary']['PRED'],
        'coordinates_sha256': canonical_hash(coords), 'queries_sha256': canonical_hash(queries),
        'anchor_identity_sha256': canonical_hash([(s, 1) for s in SHOTS]),
        'outcome_identity_sha256': canonical_hash([(s, f) for s in SHOTS for f in SUFFIX]),
        'intended_shots': len(SHOTS), 'available_anchors': sum(a is not None for a in anchors.values()),
        'intended_later_assays': len(queries), 'anchor_fraction': 1, 'outcome_fractions': list(SUFFIX),
        'conditions': list(old.PRIMARY), 'missing_anchor_shots': [s for s in SHOTS if anchors[s] is None],
        'anchor_origin': 'ZERO_COLLECTED_MASS_AT_SOURCE_COLLECTION_ORIGIN_VERIFIED',
        'intervening_vials': 'ALL_ELEVEN_MEASURED_MASSES_CHECKED_AGAINST_WORKBOOK_AND_mE_cum',
        'later_TDS_available_to_predictor': False, 'new_curve_fits': 0,
        'source_labels': list(md.REAL_LABELS), 'future_mass_windows': 'SUPPLIED_CONDITIONAL_EVALUATION_QUERIES',
        'ramps_other_grinds_exp46_scored': False, 'shared_lineage_independent_cohorts': False}
    write_json(out/'source.json', source)
    write_json(out/'execution.json', {'task': TASK, 'new_curve_fits': 0, 'optimizer_calls': 0,
        'native_ewp_runs': 0, 'later_TDS_used': False, 'numpy': np.__version__,
        'scipy': __import__('scipy').__version__, 'python': __import__('platform').python_version(),
        'predictions': sum(map(len, predictions.values())),
        'supported_predictions': sum(r['in_domain'] for rr in predictions.values() for r in rr)})
    print(json.dumps({'anchors': source['available_anchors'], 'later_queries': len(queries),
                      'prediction_records': sum(map(len, predictions.values())), 'scoring': 'NOT_EXECUTED'}))


def freeze(out):
    out = Path(out)
    if subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip():
        raise ValueError('COMMIT_IMPLEMENTATION_BEFORE_FREEZE')
    write_json(out/'freeze.json', {'task': TASK,
        'producer_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'producer_tree': subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=ROOT, text=True).strip(),
        'code_and_protocol': {p: digest(ROOT/p) for p in FREEZE_PATHS},
        'artifacts': {p.name: digest(p) for p in sorted(out.glob('*.json'))},
        'review_status': 'INDEPENDENT_PRE_SCORE_AUDIT_REQUIRED',
        'primary_candidates': list(ARMS), 'primary_conditions': list(old.PRIMARY),
        'scoring_policy': 'ONE_PASS_NO_POST_SCORE_TUNING', 'physical_validation': 'NOT_ESTABLISHED'})
    print('Freeze SHA256:', digest(out/'freeze.json'))


def verify_before_score(out, review):
    frozen = previous.verify_before_score(out, review)
    approved = json.loads(Path(review).read_text())
    if approved.get('task') != TASK or not approved.get('reviewer') or approved.get('unresolved_blocking_findings') != []:
        raise ValueError('TASK_INDEPENDENT_REVIEW_REQUIRED')
    return frozen


def conjunction(values):
    if any(v not in ('PASS', 'FAIL') for v in values):
        return 'NUMERICALLY_UNRESOLVED' if 'NUMERICALLY_UNRESOLVED' in values else 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS'
    return 'PASS' if all(v == 'PASS' for v in values) else 'FAIL'


def compare(conditions, comparator):
    candidate = 'ANCHORED_MASS'
    aa, bb = (old.aggregate(conditions[n], old.PRIMARY) for n in (candidate, comparator))
    if aa['metrics'] is None or bb['metrics'] is None:
        return {'status': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS',
                'competitive_status': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS',
                'material_gain': 'NOT_ADJUDICATED_SUPPORT_OR_NUMERICS'}
    a, b = aa['metrics'], bb['metrics']
    delta, de = b['R_pp']-a['R_pp'], a['R_allowance_pp']+b['R_allowance_pp']
    bias, be = a['abs_B_pp']-b['abs_B_pp'], a['B_allowance_pp']+b['B_allowance_pp']
    ci = {r['condition']: r['metrics'] for r in conditions[candidate]}
    bi = {r['condition']: r['metrics'] for r in conditions[comparator]}
    lower = sum(bi[c]['R_pp']-ci[c]['R_pp'] > bi[c]['R_allowance_pp']+ci[c]['R_allowance_pp'] for c in old.PRIMARY)
    upper = sum(bi[c]['R_pp']-ci[c]['R_pp'] > -bi[c]['R_allowance_pp']-ci[c]['R_allowance_pp'] for c in old.PRIMARY)
    competitive = [old.threshold(-delta, de, .1), old.threshold(bias, be, .1)]
    gain = [old.threshold(-delta, de, -.1),
            old.threshold(a['R_pp']-.8*b['R_pp'], a['R_allowance_pp']+.8*b['R_allowance_pp'], 0.),
            old.threshold(bias, be, .1),
            'PASS' if lower >= 3 else 'FAIL' if upper < 3 else 'NUMERICALLY_UNRESOLVED']
    return {'status': 'QUALIFIED', 'R_reduction_pp': delta,
        'relative_R_reduction': delta/b['R_pp'] if b['R_pp'] else None,
        'R_delta_allowance_pp': de, 'abs_B_deterioration_pp': bias,
        'abs_B_delta_allowance_pp': be, 'conditions_improved_definite': lower,
        'conditions_improved_possible': upper, 'competitive_gates': competitive,
        'competitive_status': conjunction(competitive+[aa['adequacy_status']]),
        'material_gain_gates': gain, 'material_gain': conjunction(gain)}


def decision_axes(conditions):
    groups = {a: old.aggregate(conditions[a], old.PRIMARY) for a in ARMS}
    comparisons = {a: compare(conditions, a) for a in
                   ('UNANCHORED_MASS', 'ANCHOR_PERSISTENCE', 'ANCHORED_EMPIRICAL', 'ANCHORED_SETTING_EMPIRICAL')}
    axes = {'A': groups['ANCHORED_MASS']['adequacy_status'],
            'B': comparisons['UNANCHORED_MASS']['material_gain'],
            'C': comparisons['ANCHOR_PERSISTENCE']['material_gain'],
            'D': conjunction([groups['ANCHORED_MASS']['adequacy_status']] +
                  [comparisons[a]['competitive_status'] for a in ('ANCHORED_EMPIRICAL', 'ANCHORED_SETTING_EMPIRICAL')]),
            'E': {a: comparisons[a]['material_gain'] for a in ('ANCHORED_EMPIRICAL', 'ANCHORED_SETTING_EMPIRICAL')}}
    if all(axes[a] == 'PASS' for a in 'ABCD'):
        disposition = 'ANCHOR_CONDITIONED_MASS_DELIVERY_SUPPORTED_FOR_TESTED_SUFFIXES'
    elif axes['A'] == 'FAIL':
        disposition = 'SINGLE_ANCHOR_MASS_DELIVERY_INADEQUATE'
    elif any(axes[a] not in ('PASS', 'FAIL') for a in 'ABCD'):
        disposition = 'NUMERICALLY_UNRESOLVED' if any(axes[a] == 'NUMERICALLY_UNRESOLVED' for a in 'ABCD') else 'BLOCKED_SOURCE_OR_INFORMATION_CONTRACT'
    elif axes['D'] == 'FAIL':
        disposition = 'ADEQUATE_NOT_EMPIRICALLY_COMPETITIVE'
    else:
        disposition = 'ADEQUATE_WITHOUT_EARNED_ANCHOR_OR_SHAPE_VALUE'
    return {'axes': axes, 'disposition': disposition, 'balanced': groups, 'comparisons': comparisons}


def evaluate(observed, predictions):
    expected = {(s, f) for s in SHOTS for f in SUFFIX}
    if (len(observed) != len(expected) or {(r['shot'], r['fraction']) for r in observed} != expected
            or any(r['campaign'] != CAMPAIGN for r in observed) or set(predictions) != set(ARMS)):
        raise ValueError('SCORER_REQUIRES_COMPLETE_SUFFIX_IDENTITY_SET_NO_ANCHORS')
    keys = [(r['shot'], r['fraction']) for r in observed]
    for arm in ARMS:
        if [(r['shot'], r['fraction']) for r in predictions[arm]] != keys:
            raise ValueError('SAME_SUFFIX_REQUIRED_FOR_EVERY_ARM')
        for o, p in zip(observed, predictions[arm]):
            if any(p[k] != o[k] for k in QUERY_KEYS):
                raise ValueError('FROZEN_QUERY_DRIFT')
    shots = {a: old.shot_metrics(observed, predictions[a]) for a in ARMS}
    conditions = {a: old.condition_metrics(shots[a]) for a in ARMS}
    for a in ARMS:
        for c in conditions[a]:
            ss = [s for s in shots[a] if s['condition'] == c['condition']]
            c['coverage'] = {'intended_shots': len(ss), 'supported_shots': c['qualified_shots'],
                'intended_assays': sum(s['expected_assays'] for s in ss),
                'eligible_assays': sum(s['valid_assays'] for s in ss),
                'supported_assays': sum(s['supported_assays'] for s in ss),
                'intended_mass_kg': sum(o['mass_kg'] for o in observed if o['condition'] == c['condition']),
                'eligible_mass_kg': sum(s['assayed_mass_kg'] for s in ss),
                'supported_mass_kg': sum(o['mass_kg'] for o, p in zip(observed, predictions[a])
                    if o['condition'] == c['condition'] and o['eligible'] and p['in_domain'])}
    result = decision_axes(conditions)
    result.update(task=TASK, conditions=conditions, rights=old.RIGHTS,
                  source_labels=list(md.REAL_LABELS), physical_validation='NOT_ESTABLISHED', score_passes=1)
    diagnostics = {}
    for a in ARMS:
        pairs = [(o, p) for o, p in zip(observed, predictions[a]) if o['eligible'] and p['in_domain']]
        horizons = {}
        for f in SUFFIX:
            # One interval per physical shot at a given horizon, balanced by condition.
            cc = []
            for c in old.PRIMARY:
                pp = [(o, p) for o, p in pairs if o['fraction'] == f and o['condition'] == c]
                if len(pp) != 3:
                    cc = []
                    break
                err = [100*(p['predicted_solute_kg']-o['solute_kg'])/o['mass_kg'] for o, p in pp]
                allowance = [100*p['integration_allowance_kg']/o['mass_kg'] for o, p in pp]
                cc.append({'condition': c, 'mean_absolute_error_pp': float(np.mean(np.abs(err))),
                    'signed_mean_error_pp': float(np.mean(err)), 'numerical_allowance_pp': float(np.mean(allowance)),
                    'mean_start_kg': float(np.mean([o['b0'] for o, _ in pp])),
                    'mean_end_kg': float(np.mean([o['b1'] for o, _ in pp]))})
            horizons[str(f)] = {'conditions': cc, 'balanced_mean_absolute_error_pp': float(np.mean([c['mean_absolute_error_pp'] for c in cc])) if cc else None,
                'balanced_signed_mean_error_pp': float(np.mean([c['signed_mean_error_pp'] for c in cc])) if cc else None}
        diagnostics[a] = {'by_forecast_fraction': horizons,
            'maximum_shot_R_pp': max((s['metrics']['R_pp'] for s in shots[a] if s['metrics']), default=None),
            'maximum_shot_R_allowance_pp': max((s['metrics']['R_allowance_pp'] for s in shots[a] if s['metrics']), default=None),
            'supported_assayed_suffix_solute': {
                'observed_kg': sum(o['solute_kg'] for o, _ in pairs),
                'predicted_kg': sum(p['predicted_solute_kg'] for _, p in pairs),
                'numerical_allowance_kg': sum(p['integration_allowance_kg'] for _, p in pairs),
                'source_rounding_allowance_kg': sum(o['source_rounding_allowance_kg'] for o, _ in pairs),
                'supported_assays': len(pairs), 'intended_assays': len(expected)},
            'unsupported_reasons': sorted({p['unsupported_reason'] for p in predictions[a] if p['unsupported_reason']})}
    result['diagnostics'] = diagnostics
    return result, shots


def numerical_summary(predictions, states):
    out = {'maximum_solute_allowance_kg': max(p['integration_allowance_kg'] for rr in predictions.values() for p in rr),
           'maximum_anchor_relative_allowance': max((s['anchor_integral_allowance_kg']/s['anchor_integral_kg'] for s in states.values()), default=None),
           'anchor_sensitivity': {}}
    for arm in ('ANCHORED_MASS', 'ANCHORED_EMPIRICAL', 'ANCHORED_SETTING_EMPIRICAL', 'ANCHOR_PERSISTENCE'):
        out['anchor_sensitivity'][arm] = {}
        for f in SUFFIX:
            pp = [p for p in predictions[arm] if p['fraction'] == f and p['anchor_error_amplification'] is not None]
            values = [p['anchor_error_amplification'] for p in pp]
            out['anchor_sensitivity'][arm][str(f)] = {'count': len(values),
                'min': min(values) if values else None, 'max': max(values) if values else None,
                'mean': float(np.mean(values)) if values else None,
                'maximum_numerical_allowance': max((p['amplification_allowance'] for p in pp), default=None)}
    out['interpretation'] = 'Analytical sensitivity, not a confidence interval or sensor specification'
    return out


def score(out, review):
    out = Path(out)
    verify_before_score(out, review)
    write_json(out/'score_receipt.json', {'status': 'STARTED', 'freeze_sha256': digest(out/'freeze.json'),
        'review_sha256': digest(review), 'predictions_sha256': digest(out/'predictions.json')})
    paths = old.source_paths()
    designs, _ = previous.qualify_settings(paths)
    coords = source_coordinates(paths, designs)
    if canonical_hash(coords) != json.loads((out/'source.json').read_text())['coordinates_sha256']:
        raise ValueError('SOURCE_COORDINATE_DRIFT')
    later = [r for r in coords if r['fraction'] in SUFFIX]
    observed = selected_assays(old.rows(old.DATA/'prediction_fraction_replicates.csv'), later, SUFFIX)
    predictions = json.loads((out/'predictions.json').read_text())
    result, shots = evaluate(observed, predictions)
    result['numerics'] = numerical_summary(predictions, json.loads((out/'states.json').read_text()))
    write_json(out/'shot_results.json', shots)
    write_json(out/'scores.json', result)
    write_json(out/'score_completion.json', {'status': 'COMPLETE', 'scores_sha256': digest(out/'scores.json'),
        'shot_results_sha256': digest(out/'shot_results.json'), 'score_receipt_sha256': digest(out/'score_receipt.json')})
    print(json.dumps({'axes': result['axes'], 'disposition': result['disposition']}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('prepare', 'freeze', 'score'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--review', type=Path)
    args = parser.parse_args()
    if args.output.resolve().is_relative_to(ROOT):
        parser.error('row-level evidence must remain outside repository')
    if args.command == 'score':
        if not args.review:
            parser.error('--review required')
        score(args.output, args.review)
    else:
        {'prepare': prepare, 'freeze': freeze}[args.command](args.output)


if __name__ == '__main__':
    main()

"""Retrospective reduction of retained MASS evidence; no campaign execution.

CLI: preflight/audit --evidence-root ROOT --ewp-checkout CHECKOUT --output NEW_DIR;
report --retained DIR. Detailed results and all locators remain outside Git.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/sci_md_mass_uncertainty_001'
TASK = 'SCI-MD-MASS-UNCERTAINTY-001'
METRICS = ('R_pp', 'B_pp', 'absB_pp')
BASE = '3cd308ac5bed39acff3d995108b5178a53c982ee'
EWP = '4284e9460c8057053e95de7cfa2fb3590e68e9db'


class IntegrityStop(ValueError):
    """Do not retry or interpret a mismatching input."""


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, allow_nan=False, separators=(',', ':')).encode()


def read(path):
    from .conditional_tail_delivery import strict_json
    return strict_json(Path(path).read_text())


def git(*args, root=ROOT):
    return subprocess.check_output(['git', '-C', str(root), *args])


class Inputs:
    """Read-only byte verification, including repeat-read and post-run checks."""

    def __init__(self):
        self.identities = {}

    def bytes(self, path, expected=None):
        path = Path(path).resolve()
        data = path.read_bytes()
        actual = sha(data)
        if expected is not None and actual != expected:
            raise IntegrityStop('INPUT_HASH_MISMATCH: ' + path.name)
        if path in self.identities and actual != self.identities[path]:
            raise IntegrityStop('INCONSISTENT_READBACK: ' + path.name)
        self.identities[path] = actual
        return data

    def json(self, path, expected=None):
        from .conditional_tail_delivery import strict_json
        return strict_json(self.bytes(path, expected).decode())

    def recheck(self):
        for path, expected in list(self.identities.items()):
            self.bytes(path, expected)

    def manifest(self, root, records):
        root = Path(root).resolve()
        for relative, expected in records.items():
            path = (root / relative).resolve()
            if not path.is_relative_to(root):
                raise IntegrityStop('MANIFEST_PATH_ESCAPE')
            self.bytes(path, expected)


def private_output(path, inputs=()):
    path = Path(path).resolve()
    if any((p / '.git').exists() for p in (path, *path.parents)):
        raise ValueError('OUTPUT_MUST_BE_OUTSIDE_GIT')
    if any(path == Path(p).resolve() or path.is_relative_to(Path(p).resolve())
           for p in inputs):
        raise ValueError('SOURCE_OVERWRITE_FORBIDDEN')
    path.mkdir(parents=True, exist_ok=False)
    return path


def write(path, value):
    with Path(path).open('x') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def index(rows, names, expected=None):
    result = {}
    for row in rows:
        key = tuple(row[n] for n in names)
        if key in result:
            raise ValueError('DUPLICATE_PHYSICAL_WINDOW_KEY')
        result[key] = row
    if expected is not None and set(result) != set(expected):
        raise ValueError('MISSING_OR_UNEXPECTED_MEMBERSHIP')
    return result


def deduplicate_aliases(rows, aliases):
    """Only explicit lineage aliases collapse; equality of values is irrelevant."""
    result = {}
    for r in rows:
        key = (aliases.get(r['dataset'], r['dataset']), r['campaign'], r['shot'], r['window'])
        value = {k: v for k, v in r.items() if k != 'dataset'}
        if key in result and result[key] != value:
            raise ValueError('CONFLICTING_ALIAS_OBSERVATION')
        result[key] = value
    return result


def reconcile(actual, expected, path='result'):
    """Only reduction arithmetic gets a small binary64 serialization allowance."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict) or set(actual) != set(expected):
            raise IntegrityStop('REPRODUCTION_KEYS: ' + path)
        for key in expected:
            reconcile(actual[key], expected[key], path + '.' + str(key))
    elif isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise IntegrityStop('REPRODUCTION_LENGTH: ' + path)
        for i, (a, e) in enumerate(zip(actual, expected)):
            reconcile(a, e, path + '.' + str(i))
    elif isinstance(expected, float):
        if (isinstance(actual, bool) or not isinstance(actual, (int, float))
                or not math.isfinite(actual)
                or abs(actual - expected) > 512 * math.ulp(max(1., abs(expected)))):
            raise IntegrityStop('REPRODUCTION_VALUE: ' + path)
    elif actual != expected or type(actual) is not type(expected):
        raise IntegrityStop('REPRODUCTION_IDENTITY: ' + path)


def metric(masses, observed, predicted, *, observed_unit='mass_fraction'):
    """Independent arithmetic oracle, also used to check every scored unit."""
    if not masses or len(masses) != len(observed) or len(masses) != len(predicted):
        raise ValueError('COMPLETE_MATCHED_VECTORS_REQUIRED')
    if observed_unit not in ('mass_fraction', 'percent'):
        raise ValueError('EXPLICIT_CHEMISTRY_UNIT_REQUIRED')
    if any(not math.isfinite(v) for v in [*masses, *observed, *predicted]) or min(masses) <= 0:
        raise ValueError('FINITE_POSITIVE_MASS_REQUIRED')
    limit = 1 if observed_unit == 'mass_fraction' else 100
    if any(not 0 <= v <= limit for v in observed):
        raise ValueError('CHEMISTRY_UNITS_OR_RANGE')
    e = [p - o * (100 if observed_unit == 'mass_fraction' else 1) for o, p in zip(observed, predicted)]
    total = math.fsum(masses)
    b = math.fsum(m * x for m, x in zip(masses, e)) / total
    return {'R_pp': math.sqrt(math.fsum(m * x * x for m, x in zip(masses, e)) / total),
            'B_pp': b, 'absB_pp': abs(b)}


def average(values):
    return None if not values or any(v is None for v in values) else {
        k: math.fsum(v[k] for v in values) / len(values) for k in METRICS}


def balanced(units, conditions=None):
    if conditions is None:
        return average([units[k] for k in sorted(units)])
    return average([average([units[k] for k in sorted(units) if conditions[k] == c])
                    for c in sorted(set(conditions.values()))])


def spread(values):
    values = sorted(values)
    if not values:
        return {'n': 0, 'mean': None, 'sd': None, 'min': None, 'q25': None,
                'median': None, 'q75': None, 'max': None}
    def quantile(q):
        at = (len(values) - 1) * q
        lo, hi = math.floor(at), math.ceil(at)
        return values[lo] + (at - lo) * (values[hi] - values[lo])
    mean = math.fsum(values) / len(values)
    return {'n': len(values), 'mean': mean,
            'sd': math.sqrt(math.fsum((v - mean)**2 for v in values) / (len(values) - 1)) if len(values) > 1 else None,
            'min': values[0], 'q25': quantile(.25), 'median': quantile(.5),
            'q75': quantile(.75), 'max': values[-1]}


def distributions(units):
    return {'declared_units': len(units), 'complete_units': sum(v is not None for v in units.values()),
            'scope': 'ALL_DECLARED_UNITS' if all(v is not None for v in units.values()) else 'COMPLETE_UNIT_SUBSET_ONLY',
            **{k: spread([v[k] for v in units.values() if v is not None]) for k in METRICS}}


def gain(candidate, reference):
    if candidate is None or reference is None:
        return None
    r = reference['R_pp']
    return {'R_gain_pp': r - candidate['R_pp'],
            'relative_gain': 1 - candidate['R_pp'] / r if r > 1e-12 else None,
            'absB_deterioration_pp': candidate['absB_pp'] - reference['absB_pp']}


def gains(arms, primary, conditions=None):
    return {a: gain(balanced(arms[primary], conditions), balanced(v, conditions))
            for a, v in arms.items() if a != primary}


def range_records(records):
    valid = [r for r in records if r is not None]
    keys = sorted(set().union(*(r.keys() for r in valid)))
    return {'evaluations': len(records), 'available': len(valid),
            'ranges': {k: spread([r[k] for r in valid if r[k] is not None]) for k in keys}}


def leave_one_out(arms, primary, conditions=None, *, pairs=False):
    keys = set(arms[primary])
    if any(set(v) != keys for v in arms.values()):
        raise ValueError('IDENTICAL_PAIRING_ACROSS_ARMS_REQUIRED')
    identities = sorted({i for k in keys for i in k} if pairs else keys)
    if pairs and keys != {(j, i) for j in identities for i in identities if j != i}:
        raise ValueError('COMPLETE_OFF_DIAGONAL_MATRIX_REQUIRED')
    details = []
    for omitted in identities:
        retained = {a: {k: v for k, v in units.items() if
                       (omitted not in k if pairs else omitted != k)} for a, units in arms.items()}
        cond = {k: v for k, v in conditions.items() if k != omitted} if conditions else None
        if conditions and set(cond.values()) != set(conditions.values()):
            # Deleting a singleton condition cannot redefine a fixed-condition estimand.
            summaries = {a: None for a in arms}
        else:
            summaries = {a: balanced(v, cond) if all(m is not None for m in arms[a].values()) else None
                         for a, v in retained.items()}
        item = {'omitted': omitted, 'remaining_units': len(next(iter(retained.values()))),
                'metrics': summaries,
                'gains': {a: gain(summaries[primary], summaries[a]) for a in arms if a != primary}}
        if pairs:
            ids = [i for i in identities if i != omitted]
            item['remaining_physical_shots'] = len(ids)
            item['calibration_adverse'] = {}; item['target_adverse'] = {}
            for a, units in retained.items():
                for field, pos in (('calibration_adverse', 0), ('target_adverse', 1)):
                    means = [average([v for key, v in units.items() if key[pos] == i]) for i in ids]
                    item[field][a] = {m: max(v[m] for v in means) if means and all(v is not None for v in means) else None for m in ('R_pp', 'absB_pp')}
        details.append(item)
    result = {'label': 'PHYSICAL_SHOT_DELETION_SENSITIVITY_CONDITIONAL_ON_RETAINED_FITS_NOT_CI',
              'deletions': len(details), 'remaining_units': sorted({v['remaining_units'] for v in details}),
              'metrics': {a: range_records([v['metrics'][a] for v in details]) for a in arms},
              'gains': {a: range_records([v['gains'][a] for v in details]) for a in arms if a != primary}}
    if pairs:
        result['remaining_physical_shots'] = sorted({v['remaining_physical_shots'] for v in details})
        for field in ('calibration_adverse', 'target_adverse'):
            result[field] = {a: range_records([v[field][a] for v in details]) for a in arms}
    return result, details


def paired_distributions(arms, primary):
    result = {}
    for a in arms:
        if a == primary:
            continue
        if set(arms[a]) != set(arms[primary]):
            raise ValueError('PAIRED_MEMBERSHIP_REQUIRED')
        values = [gain(arms[primary][k], arms[a][k]) for k in sorted(arms[a])]
        result[a] = range_records(values)
    return result


def headroom(value, threshold, *, minimum=False, bounds=None):
    out = {'value': value, 'threshold': threshold,
           'signed_headroom': (value - threshold if minimum else threshold - value) if value is not None else None}
    if bounds is not None:
        out['numerical_headroom_bounds'] = ([bounds[0] - threshold, bounds[1] - threshold] if minimum
                                           else [threshold - bounds[1], threshold - bounds[0]])
    return out


def metric_headroom(m):
    if m is None:
        return None
    out = {}
    for k, threshold in (('R', 1.), ('absB', .5)):
        allowance = m.get(k + '_allowance_pp', m.get('B_allowance_pp'))
        bounds = m.get(k + '_bounds_pp')
        if bounds is None and allowance is not None:
            bounds = [max(0., m[k + '_pp'] - allowance), m[k + '_pp'] + allowance]
        out[k] = headroom(m[k + '_pp'], threshold, bounds=bounds)
    return out


def increment_headroom(v):
    gain_key = 'R_gain_pp' if 'R_gain_pp' in v else 'R_improvement_pp'
    rel_key = 'relative_gain' if 'relative_gain' in v else 'relative_improvement'
    bias_key = 'absB_deterioration_pp' if 'absB_deterioration_pp' in v else 'mean_absB_deterioration_pp'
    if gain_key not in v:
        return {'status': v['status']}
    gain_bounds = v.get(gain_key.replace('_pp', '_bounds_pp'))
    bias_bounds = v.get(bias_key.replace('_pp', '_bounds_pp'))
    if 'R_improvement_allowance_pp' in v:
        gain_bounds = [v[gain_key]-v['R_improvement_allowance_pp'], v[gain_key]+v['R_improvement_allowance_pp']]
        bias_bounds = [v[bias_key]-v['mean_absB_allowance_pp'], v[bias_key]+v['mean_absB_allowance_pp']]
    return {'absolute_gain': headroom(v[gain_key], .1, minimum=True,
                                      bounds=gain_bounds),
            'relative_gain': headroom(v[rel_key], .15, minimum=True, bounds=v.get(rel_key + '_bounds')),
            'abs_bias_deterioration': headroom(v[bias_key], .1,
                                               bounds=bias_bounds)}


def load_bundle(t, directory, tracker, ewp_checkout):
    d = ROOT / f'docs/analysis/sci_md_mass_delivery_{t}'
    b = tracker.json(d / 'RESULT_BINDING.json')
    bound = b.get('private_evidence_hashes', b.get('private_artifact_hashes', {}))
    freeze_hash = bound.get('freeze.json', b.get('freeze_sha256'))
    f = tracker.json(directory / 'freeze.json', freeze_hash)
    if (f['producer_commit'] != b['evaluated_producer_commit'] or f['producer_tree'] != b['evaluated_producer_tree']
            or git('rev-parse', f['producer_commit'] + '^{tree}').decode().strip() != f['producer_tree']):
        raise IntegrityStop('ORIGINAL_PRODUCER_IDENTITY')
    tracker.manifest(directory, bound)
    tracker.manifest(directory, f['artifacts'])
    for path, expected in f['code_and_protocol'].items():
        if sha(git('show', f['producer_commit'] + ':' + path)) != expected:
            raise IntegrityStop('HISTORICAL_CODE_COMMITMENT: ' + path)
        # Only actually reused source/metric runtime needs to equal current bytes.
        if path.startswith(('puckworks/analysis/', 'tools/')):
            tracker.bytes(ROOT / path, expected)
    if t == '008':
        tracker.bytes(directory / 'predictions.json', b['predictions_sha256'])
        tracker.bytes(directory / 'score_completion.json', b['private_score_completion_sha256'])
        tracker.bytes(directory / 'score_receipt.json', b['private_score_receipt_sha256'])
        tracker.bytes(directory / 'pair_row_column_results.json', b['private_pair_row_column_results_sha256'])
    completion = tracker.json(directory / 'score_completion.json')
    for field, name in [('scores_sha256', 'scores.json'), ('shot_results_sha256', 'shot_results.json'),
                        ('details_sha256', 'pair_row_column_results.json'), ('score_receipt_sha256', 'score_receipt.json'),
                        ('observed_suffix_sha256', 'observed_suffix.json'), ('outcomes_sha256', 'outcomes.json')]:
        if field in completion:
            tracker.bytes(directory / name, completion[field])
    public_hash = b.get('public_result_sha256', b.get('result_sha256', b.get('results_sha256')))
    result = tracker.json(d / 'RESULTS.json', public_hash)
    tracker.bytes(directory / 'scores.json', public_hash)
    if sha(git('show', EWP + f':docs/analysis/sci_md_mass_delivery_{t}/RESULTS.json', root=ewp_checkout)) != public_hash:
        raise IntegrityStop('EWP_CORROBORATION_MISMATCH')
    data = {p.name: tracker.json(p) for p in [directory / n for n in (
        'queries.json', 'predictions.json', 'observed_suffix.json' if t != '008' else 'outcomes.json',
        'shot_results.json' if t != '008' else 'pair_row_column_results.json')]}
    for n in ('coordinates.json', 'cohort.json', 'folds.json', 'counts.json', 'pools.json', 'early_inputs.json', 'reference.json', 'source.json', 'training.json', 'calibration_manifest.json'):
        if n in f['artifacts'] or n in bound:
            data[n] = tracker.json(directory / n)
    data['historical'] = result
    provenance = {'evaluated_producer_commit': f['producer_commit'], 'evaluated_producer_tree': f['producer_tree'],
                  'freeze_sha256': freeze_hash, 'prediction_sha256': tracker.identities[(directory / 'predictions.json').resolve()],
                  'outcome_projection_sha256': tracker.identities[(directory / ('outcomes.json' if t == '008' else 'observed_suffix.json')).resolve()],
                  'result_sha256': public_hash, 'result_binding_sha256': sha((d / 'RESULT_BINDING.json').read_bytes()),
                  'protocol_sha256': f['code_and_protocol'][str((d / 'PROTOCOL.md').relative_to(ROOT))],
                  'frozen_artifact_count_verified': len(f['artifacts']), 'ewp_result_bytes': 'IDENTICAL',
                  'source_record_sha256': sha((d / ('SOURCE_IDENTITIES.json' if t == '006' else 'SOURCE.json')).read_bytes())}
    if t == '008':
        provenance['evaluated_calibration_manifest_sha256'] = tracker.identities[(directory/'calibration_manifest.json').resolve()]
        provenance['evaluated_calibration_artifact_set_sha256'] = sha(canonical({n: h for n, h in f['artifacts'].items() if n.startswith('calibration-')}))
    data['provenance'] = provenance
    return data


def source_check(t, directory, data, tracker):
    """Use original qualified adapters; never generic workbook/mean-table parsing."""
    if t == '006':
        from . import pannusch_conditional_tail_delivery as p
        paths, source = p.qualified_sources()
        tracker.manifest(p.source.DATA, source['registers'])
        for key, path in paths.items():
            tracker.bytes(path, source['source_files'][key])
        coordinates = p.coordinates(paths)
        if coordinates != data['coordinates.json']:
            raise IntegrityStop('SOURCE_COORDINATE_PROJECTION')
        _, outcomes = p.project_assays(p.all_rows(), coordinates, outcome=True)
        if outcomes != data['observed_suffix.json']:
            raise IntegrityStop('SOURCE_OUTCOME_PROJECTION')
        # Assays are the accepted qualified individual-shot export; original MAT
        # values differ only by the historical 8-decimal percent serialization.
        obj = p.source.mat(paths['P24-MAT-PRED'])['ExperimentalData']
        for r in outcomes:
            if r['q'] is None:
                continue
            _, exp, rep = r['shot'].split('-')
            original = float(obj[int(exp[1:])-1].run[int(rep[1:])-1].TdS[((1, 2)+p.SUFFIX).index(r['fraction'])])
            if abs(original / 100 - r['q']) > 5.001e-11:
                raise IntegrityStop('ORIGINAL_ASSAY_EXPORT_SERIALIZATION')
        training = data['training.json']
        if len(training) != 45 or len({r['group'] for r in training}) != 15:
            raise IntegrityStop('ORIGINAL_FIT_MEMBERSHIP')
        data['provenance']['source_files'] = source['source_files']
        data['provenance']['model_artifact_sha256'] = {}
        for arm in ('C0', 'C1', 'C2'):
            path = p.DOC/'models'/f'{arm}.json'
            expected = sha(git('show', data['provenance']['evaluated_producer_commit']+':'+str(path.relative_to(ROOT))))
            tracker.bytes(path, expected)
            data['provenance']['model_artifact_sha256'][arm] = expected
        data['provenance']['observation_interpretation'] = 'QUALIFIED_INDIVIDUAL_SHOT_EXPORT; original MAT crosscheck at accepted 5.001e-11 mass-fraction serialization allowance, not assay uncertainty'
    else:
        from . import grudeva_pooled_tail_delivery as p
        from . import grudeva_pooled_tail_scoring as s
        locator = tracker.json(directory.parent / 'source_locators.json')
        source_root = Path(locator['source_root'])
        authority = tracker.json(ROOT / f'docs/analysis/sci_md_mass_delivery_{t}/SOURCE.json')
        tracker.manifest(source_root, authority['files'])
        models, _, _ = p.verify_dependencies()
        records = p.gc.parse_source(source_root / 'exp13.csv')
        early, queries, support, cohort, pools = p.project(records, models['C2'].means[:2])
        for name, actual in [('queries.json', queries), ('cohort.json', cohort)]:
            if actual != data[name]:
                raise IntegrityStop('ORIGINAL_COHORT_PROJECTION: ' + name)
        expected_outcomes = data['outcomes.json' if t == '008' else 'observed_suffix.json']
        if s.project_outcomes(records, queries) != expected_outcomes:
            raise IntegrityStop('ORIGINAL_OUTCOME_PROJECTION')
        if t == '007' and (early != data['early_inputs.json'] or pools != data['pools.json']):
            raise IntegrityStop('ORIGINAL_PREFIX_PROJECTION')
        selected = {r['shot'] for r in cohort if r['eligible']}
        derived_counts = {
            'raw_blocks': len({r['shot'] for r in records}), 'rectangular_positions': len(records),
            'nominal_physical_shots': len(cohort), 'nominal_regular_vials': 16*len(cohort),
            'eligible_shots': len(selected),
            'excluded_shots_by_reason': dict(Counter(r['reason'] for r in cohort if not r['eligible'])),
            'intended_suffix_vials': len(queries), 'positive_suffix_vials': sum(q['mass_kg'] > 0 for q in queries),
            'zero_width_suffix_vials': sum(q['mass_kg'] == 0 for q in queries),
            'suffix_mass_kg': math.fsum(q['mass_kg'] for q in queries),
            'prefix_mass_kg': math.fsum(r['selection']['prefix_kg'] for r in pools if r['shot'] in selected),
            'original_conditioning_assays': sum(pool['original_assays'] for r in pools if r['shot'] in selected for pool in r['pools']),
            'pooled_conditioning_summaries': 2*len(selected),
            'primary_suffix_missing_chemistry': sum(r['chemistry_status'] == 'UNAVAILABLE_CHEMISTRY' for r in support)}
        counts = data['counts.json']
        reconcile(derived_counts, counts, 'source_membership_counts')
        if (len(cohort), sum(r['eligible'] for r in cohort), len(queries),
                counts['original_conditioning_assays'], counts['pooled_conditioning_summaries']) != (13, 11, 55, 98, 22):
            raise IntegrityStop('SOURCE_COUNTS_REQUIRE_RECONCILIATION')
        data['provenance']['source_files'] = authority['files']
        data['provenance']['immutable_parent_model_identities'] = {a: m.sha256 for a, m in models.items()}


def verify_oracle(rows, predictions, metrics, *, grudeva=False):
    if metrics is None:
        return
    masses = [r['mass_kg'] for r in rows]
    qs = [r['q'] for r in rows]
    ps = [p['prediction']['tds_percent'] if grudeva else p['predicted_tds_percent'] for p in predictions]
    reconcile(metric(masses, qs, ps), {k: metrics[k] for k in METRICS}, 'independent_arithmetic')


def audit006(data):
    from . import conditional_tail_scoring as s
    p = s.pipeline
    observed, predictions, queries = data['observed_suffix.json'], data['predictions.json'], data['queries.json']
    expected = {(f'PRED-E{i:02d}-R{r}', f) for i in range(1, 9) for r in (1, 2, 3) for f in p.SUFFIX}
    oi, qi = index(observed, ('shot', 'fraction'), expected), index(queries, ('shot', 'fraction'), expected)
    if set(predictions) != {'C0', 'C1', 'C2', p.LEGACY}:
        raise ValueError('ALL_ORIGINAL_ARMS_REQUIRED')
    pi = {a: index(v, ('shot', 'fraction'), expected) for a, v in predictions.items()}
    for a in pi:
        for k in expected:
            if any(pi[a][k][n] != v for n, v in qi[k].items()) or any(oi[k][n] != qi[k][n] for n in ('b0', 'b1', 'mass_kg', 'condition')):
                raise IntegrityStop('PREDICTION_GEOMETRY_IDENTITY')
    historical = data['historical']; panels = {}; private = {}; common = {}
    for panel, conditions in p.PANELS.items():
        panels[panel] = {}; private[panel] = {}
        for arm in sorted(predictions):
            panels[panel][arm], private[panel][arm] = s.panel_metrics(observed, predictions[arm], conditions, common_legacy=arm == p.LEGACY)
    reconcile(panels, historical['panels'], '006.panels')
    reconcile(private, data['shot_results.json'], '006.shots')
    for arm in ('C2', p.LEGACY):
        common[arm], _ = s.panel_metrics(observed, predictions[arm], p.PANELS['primary'], common_legacy=True)
    reconcile(common, historical['primary_common_legacy_support'], '006.legacy_support')
    primary = panels['primary']
    second = s.material_gain(primary['C2'], primary['C1'])
    legacy = s.material_gain(common['C2'], common[p.LEGACY])
    competitive = {'adequacy': primary['C2']['full_scope_adequacy'], **{f'versus_{a}': s.competitiveness(primary['C2'], primary[a]) for a in ('C0', 'C1')}}
    for label, actual in [('incremental_second_assay', second), ('legacy_gain', legacy), ('competitiveness', competitive)]:
        reconcile(actual, historical[label], '006.' + label)
    secondary = {a: {'adequacy': primary[a]['full_scope_adequacy'], 'C2_material_gain': s.material_gain(primary['C2'], primary[a])} for a in ('C0', 'C1')}
    reconcile(secondary, historical['simpler_learned_secondary_results'], '006.secondary')
    vector = {'A': competitive['adequacy'], 'B': second['status'],
              'C': s.conjunction(competitive.values()), 'D': legacy['status'],
              'limitations': [s.INCOMPLETE] if any(not v['complete_scope'] for panel in panels.values() for v in panel.values()) else []}
    reconcile(vector, historical['decision_vector'], '006.decision_vector')
    if all(vector[k] == 'PASS' for k in ('A', 'B', 'C', 'D')):
        reconcile('LEARNED_TWO_ASSAY_MAPPING_EARNED', historical['disposition'], '006.disposition')
    result = {'panels': {}, 'paired_gains': {}, 'headroom': {}, 'observed_replicate_variability': [],
              'counts': data['source.json']['counts']}
    detailed = {}
    for panel, conditions in p.PANELS.items():
        units = {a: {v['shot']: v['full'] for v in private[panel][a]} for a in private[panel]}
        groups = {v['shot']: v['condition'] for v in next(iter(private[panel].values()))}
        for a, arm in units.items():
            for shot, m in arm.items():
                keys = sorted(k for k in expected if k[0] == shot)
                verify_oracle([oi[k] for k in keys], [pi[a][k] for k in keys], m)
        sensitivity, details = leave_one_out(units, 'C2', groups)
        detailed[panel] = details
        result['panels'][panel] = {'unit_metric_distribution': {a: distributions(v) for a, v in units.items()},
            'paired_unit_distribution': paired_distributions(units, 'C2'), 'physical_shot_deletion': sensitivity,
            'full_scope_available': {a: balanced(v, groups) is not None for a, v in units.items()}}
        result['paired_gains'][panel] = gains(units, 'C2', groups)
        result['headroom'][panel] = {a: {c: metric_headroom(v['full_scope_metrics']) for c, v in arm['conditions'].items()} for a, arm in panels[panel].items()}
        for c in conditions:
            for f in p.SUFFIX:
                rows = [r for r in observed if r['condition'] == c and r['fraction'] == f]
                result['observed_replicate_variability'].append({'panel': panel, 'condition': c, 'fraction': f,
                    'intended_replicates': len(rows), 'observed_tds_percent': spread([100*r['q'] for r in rows if r['q'] is not None]),
                    'eligible_replicates': sum(r['eligible'] for r in rows),
                    **{k: spread([r[k] for r in rows if r[k] is not None]) for k in ('mass_kg', 'b0', 'b1')}})
    result['comparison_headroom'] = {}
    for label, v in [('B_C2_vs_C1', second), ('D_C2_vs_legacy', legacy), ('secondary_C2_vs_C0', secondary['C0']['C2_material_gain'])]:
        result['comparison_headroom'][label] = {**increment_headroom(v), 'condition_wins': headroom(v['definite_condition_wins'], 3, minimum=True)}
        reference = common[p.LEGACY] if label.startswith('D_') else primary['C0' if label.endswith('C0') else 'C1']
        cm, rm = primary['C2']['full_scope_metrics'], reference['full_scope_metrics']
        linear = .85*rm['R_pp']-cm['R_pp']
        allowance = .85*rm['R_allowance_pp']+cm['R_allowance_pp']
        result['comparison_headroom'][label]['relative_gain_equivalent_linear_headroom_pp'] = headroom(linear, 0., minimum=True, bounds=[linear-allowance, linear+allowance])
    result['competitiveness_headroom'] = {}
    for arm in ('C0', 'C1'):
        cm, rm = primary['C2']['full_scope_metrics'], primary[arm]['full_scope_metrics']
        result['competitiveness_headroom'][arm] = {}
        for k in ('R_pp', 'absB_pp'):
            delta = cm[k]-rm[k]; allowance = cm[k.replace('_pp', '_allowance_pp')]+rm[k.replace('_pp', '_allowance_pp')]
            result['competitiveness_headroom'][arm][k] = headroom(delta, .1, bounds=[delta-allowance, delta+allowance])
    return result, detailed


def grudeva_units(data, *, pairs=False):
    from . import grudeva_pooled_tail_scoring as s7
    from . import grudeva_one_shot_scoring as s8
    cohort = data['cohort.json']; ci = index(cohort, ('shot',), {(i,) for i in range(1, 14)})
    shots = sorted(k[0] for k, c in ci.items() if c['eligible'])
    expected = {(c['shot'], v) for c in cohort if c['eligible'] for v in range(c['k2']+1, 17)}
    qi = index(data['queries.json'], ('shot', 'vial'), expected)
    oi = index(data['outcomes.json' if pairs else 'observed_suffix.json'], ('shot', 'vial'), expected)
    arms = ('F2', 'A2', 'A0', 'M') if pairs else ('C0', 'C1', 'C2')
    if set(data['predictions.json']) != set(arms):
        raise ValueError('ALL_ORIGINAL_ARMS_REQUIRED')
    pair_keys = [(j, i) for j in shots for i in shots if j != i] if pairs else [(i,) for i in shots]
    slots = {(j, i, v) for j, i in pair_keys for s, v in expected if s == i} if pairs else expected
    if pairs:
        folds = data['folds.json']
        if (folds['calibrators'] != shots or folds['targets'] != shots or folds['pairs'] != [list(k) for k in pair_keys]
                or folds['intended_slots_per_arm'] != len(slots) or folds['unique_suffix_windows'] != len(expected)):
            raise ValueError('COMPLETE_OFF_DIAGONAL_FOLDS_REQUIRED')
    details = {}; units = {}
    for a in arms:
        pi = index(data['predictions.json'][a], ('calibrator', 'shot', 'vial') if pairs else ('shot', 'vial'), slots)
        details[a] = {}; units[a] = {}
        for key in pair_keys:
            target = key[-1]; keys = sorted(k for k in expected if k[0] == target)
            ps = [pi[(key[0], *k) if pairs else k] for k in keys]
            for k, pred in zip(keys, ps):
                if any(pred[n] != v for n, v in qi[k].items()):
                    raise IntegrityStop('PREDICTION_GEOMETRY_IDENTITY')
            q, o = [qi[k] for k in keys], [oi[k] for k in keys]
            v = s8.pair_metrics(q, o, ps) if pairs else s7.shot_metrics(q, o, ps)
            m = v['metrics' if pairs else 'full']
            positive = [(dict(qr, q=ob['q']), pr) for qr, ob, pr in zip(q, o, ps) if qr['mass_kg'] > 0]
            verify_oracle([r for r, _ in positive], [p for _, p in positive], m, grudeva=True)
            unit_key = key if pairs else target
            details[a][unit_key] = v; units[a][unit_key] = m
    return shots, details, units


def audit007(data):
    from . import grudeva_pooled_tail_scoring as s
    shots, details, units = grudeva_units(data)
    arms = {a: s.aggregate(list(v.values())) for a, v in details.items()}
    reconcile(arms, data['historical']['arms'], '007.arms')
    for a in arms:
        reconcile([dict(shot=k, **v) for k, v in details[a].items()], data['shot_results.json'][a], '007.shots.'+a)
    increments = {n: s.increment(arms['C2'], arms[a], list(details['C2'].values()), list(details[a].values())) for n, a in [('I0', 'C0'), ('I1', 'C1')]}
    reconcile(increments, data['historical']['increments'], '007.increments')
    qualified = all(p['status'] == 'QUALIFIED' and p['prediction'] is not None and p['prediction']['numerical_qualified'] and 0 <= p['prediction']['allowance_kg'] <= 1e-9 for ps in data['predictions.json'].values() for p in ps)
    full = all(v['complete_panel'] for v in arms.values())
    vector = {'coverage': 'PASS' if len(shots) >= 10 and full and qualified else 'EVIDENCE_LIMITED',
              'numerical': 'PASS' if qualified else s.UNRESOLVED,
              'adequacy': {a: v['adequacy'] for a, v in arms.items()},
              **{n: v['status'] for n, v in increments.items()}}
    reconcile(vector, data['historical']['decision_vector'], '007.decision_vector')
    if all(v['adequacy'] == 'FAIL' for v in arms.values()):
        reconcile('FROZEN_CONDITIONAL_TRANSFER_INADEQUATE_ON_DECLARED_COHORT', data['historical']['disposition'], '007.disposition')
    diagnostic = None
    if 'reference.json' in data:
        ref = data['reference.json']
        index(ref['rows'], ('shot', 'vial'), index(data['queries.json'], ('shot', 'vial')))
        diagnostic, ds = s.reference_diagnostic(ref, data['queries.json'], data['observed_suffix.json'], data['cohort.json'])
        reconcile(diagnostic, data['historical']['optional_reference_diagnostic'], '007.diagnostic')
        reconcile(ds, data['shot_results.json']['SOURCE_TRAINED_MASS_DIAGNOSTIC'], '007.diagnostic_shots')
    sensitivity, private = leave_one_out(units, 'C2')
    return {'counts': data['counts.json'], 'unit_metric_distribution': {a: distributions(v) for a, v in units.items()},
            'paired_unit_distribution': paired_distributions(units, 'C2'), 'paired_gains': gains(units, 'C2'),
            'physical_shot_deletion': sensitivity, 'diagnostic_reproduced': diagnostic is not None,
            'headroom': {a: {**metric_headroom(v['full_scope_metrics']), 'adequate_shots': headroom(v['definite_adequate_shots'], v['required_adequate_shots'], minimum=True)} for a, v in arms.items()},
            'coverage_headroom': headroom(len(shots), 10, minimum=True),
            'comparison_headroom': {n: {**increment_headroom(v), 'paired_wins': headroom(v['definite_paired_wins'], v['required_wins'], minimum=True)} for n, v in increments.items()}}, private


def calibration_status(manifest, shots):
    records = manifest['calibrations']
    expected = {f'{i}/{a}' for i in shots for a in ('A2', 'A0', 'M')}
    if set(records) != expected:
        raise ValueError('COMPLETE_CALIBRATION_MEMBERSHIP_REQUIRED')
    return {a: 'PASS' if all(records[f'{i}/{a}']['status'] == 'QUALIFIED' for i in shots)
            else 'CALIBRATION_BLOCKED' for a in ('A2', 'A0', 'M')}


def audit008(data):
    from . import grudeva_one_shot_scoring as s
    shots, details, units = grudeva_units(data, pairs=True)
    arms = {}; rows = {}; cols = {}; private_reproduction = {}
    for a, pairs in details.items():
        rows[a] = [s.summarize([pairs[j, i] for i in shots if i != j]) for j in shots]
        cols[a] = [s.summarize([pairs[j, i] for j in shots if j != i]) for i in shots]
        overall = s.summarize(list(pairs.values()))
        definite = sum(v['adequacy'] == 'PASS' for v in rows[a]); possible = sum(v['adequacy'] != 'FAIL' for v in rows[a])
        required = math.ceil(.75*len(shots))
        tests = {k: overall['adequacy_components'][k] for k in ('mean_R', 'mean_absB')}
        tests['calibration_choices'] = s.at_least(definite, possible, required, overall['complete'])
        overall.update(adequacy=s.combine(tests.values()), adequacy_components=tests,
                       adequate_calibration_choices=definite, possible_adequate_calibration_choices=possible,
                       required_adequate_calibration_choices=required)
        for name, values in [('calibration_choice_sensitivity', rows[a]), ('target_sensitivity', cols[a])]:
            overall[name] = {k: s.distribution([v['metrics'][k] for v in values if v['metrics']]) for k in ('R_pp', 'absB_pp')}
        ps = data['predictions.json'][a]
        overall['support_counts'] = dict(Counter(v['status'] for v in ps))
        overall['feature_extrapolation_slots'] = sum(bool(v['feature_extrapolation']) for v in ps)
        overall['calibration_mass_extrapolation_slots'] = sum(v['calibration_mass_extrapolation'] for v in ps)
        arms[a] = overall
        private_reproduction[a] = {'pairs': [dict(calibrator=j, target=i, **v) for (j, i), v in pairs.items()],
            'calibration_rows': [dict(calibrator=i, **v) for i, v in zip(shots, rows[a])],
            'target_columns': [dict(target=i, **v) for i, v in zip(shots, cols[a])]}
    reconcile(arms, data['historical']['arms'], '008.arms')
    reconcile(private_reproduction, data['pair_row_column_results.json'], '008.private_pairs_rows_columns')
    increments = {n: s.increment(arms['A2'], arms[a], rows['A2'], rows[a], cols['A2'], cols[a]) for n, a in [('I_CAL', 'F2'), ('I_CHEM', 'A0'), ('I_LOCAL', 'M')]}
    reconcile(increments, data['historical']['increments'], '008.increments')
    vector = {'source': 'PASS' if all(o['chemistry_status'] in ('AVAILABLE', 'STRUCTURAL_ZERO') for o in data['outcomes.json']) else s.INCOMPLETE,
              'coverage': 'PASS' if all(v['complete'] for v in arms.values()) else s.INCOMPLETE,
              'numerical': {a: 'PASS' if all(p['prediction'] and p['prediction']['numerical_qualified'] and p['prediction']['allowance_kg'] <= 1e-9 for p in ps) else s.UNRESOLVED for a, ps in data['predictions.json'].items()},
              'adequacy': {a: v['adequacy'] for a, v in arms.items()},
              'increments': {n: v['status'] for n, v in increments.items()}}
    vector['calibration'] = calibration_status(data['calibration_manifest.json'], shots)
    reconcile(vector, data['historical']['status_vector'], '008.status_vector')
    if arms['A2']['adequacy'] == 'PASS' and any(v['status'] != 'PASS' for v in increments.values()):
        reconcile('ADAPTATION_ADEQUATE_INCREMENT_NOT_ESTABLISHED', data['historical']['disposition'], '008.disposition')
    sensitivity, private = leave_one_out(units, 'A2', pairs=True)
    return {'counts': data['counts.json'], 'ordered_pairs': len(next(iter(units.values()))),
            'slots_per_arm': {a: len(v) for a, v in data['predictions.json'].items()},
            'pair_metric_distribution_not_independent': {a: distributions(v) for a, v in units.items()},
            'paired_pair_distribution_not_independent': paired_distributions(units, 'A2'), 'paired_gains': gains(units, 'A2'),
            'physical_shot_deletion': sensitivity,
            'headroom': {a: {**metric_headroom(v['metrics']), 'adequate_calibration_choices': headroom(v['adequate_calibration_choices'], v['required_adequate_calibration_choices'], minimum=True),
                'calibration_row_R_headroom_distribution': spread([1-r['metrics']['R_pp'] for r in rows[a]]),
                'calibration_row_absB_headroom_distribution': spread([.5-r['metrics']['absB_pp'] for r in rows[a]]),
                'calibration_row_adequate_pair_surplus_distribution': spread([r['definite_adequate_pairs']-r['required_adequate_pairs'] for r in rows[a]])} for a, v in arms.items()},
            'comparison_headroom': {n: {**increment_headroom(v), **{k: headroom(c['definite'], c['required'], minimum=True) for k, c in v['counts'].items()}} for n, v in increments.items()},
            'unused_required_adequate_pairs_is_gate': False}, private


def uncertainty_components():
    return {'numerical_application': 'Retained original allowances reproduced; numerical, not statistical.',
            'between_shot': '006 condition/fraction sample spread; 007 shot distributions; 008 calibration/target dependence retained.',
            'within_shot_analytical_repeatability': None, 'calibration_systematic': None,
            'early_input_propagation': None, 'training_model_uncertainty': None, 'cross_source_uncertainty': None,
            'conditional_sampling_performance': 'Finite-cohort physical-shot deletion sensitivity only; population coverage and confidence intervals unestablished.',
            'missing_components_reason': 'Retained single assays, pooled inputs and predictions do not supply independent repeat assays, calibration covariance, input-perturbed predictions or training refits. Unknown is not zero.'}


def run(evidence_root, output, ewp_checkout, *, preflight=False):
    from tools.inventory_local_corpus import resolve_roots
    roots, _ = resolve_roots(evidence_root)
    if 'collection' not in roots:
        raise FileNotFoundError('CONFIGURED_EXTERNAL_ROOT_UNAVAILABLE')
    root = Path(roots['collection'])
    tracker = Inputs(); start = time.monotonic()
    out = private_output(output, [root])
    write(out / 'started.json', {'task': TASK, 'operation': 'preflight' if preflight else 'audit'})
    result = {'task': TASK, 'base': BASE, 'ewp_reference': EWP,
              'audit_commit': git('rev-parse', 'HEAD').decode().strip(),
              'audit_tree': git('rev-parse', 'HEAD^{tree}').decode().strip(),
              'audit_module_sha256': sha(Path(__file__).read_bytes()), 'protocol_sha256': sha((DOC/'PROTOCOL.md').read_bytes()),
              'classification': ['G1', 'NO_GOVERNING_PHYSICS_CHANGE', 'RESEARCH_ONLY', 'RETROSPECTIVE', 'TARGET_EXPOSED'],
              'physical_validation': 'NOT_ESTABLISHED', 'merge_authorized': False, 'production_adoption_authorized': False,
              'native_ewp_runs': 0, 'new_fits': 0, 'new_predictions': 0, 'historical_campaign_calls': 0,
              'automatic_successor': False, 'uncertainty_components': uncertainty_components(),
              'resampling': {'method': 'NONE', 'seed': None, 'replications': 0, 'confidence_interval': None}, 'tasks': {}}
    private = {}
    try:
        for t, fn in [('006', audit006), ('007', audit007), ('008', audit008)]:
            directory = root / f'mass-delivery-{t}-evidence/run-001'
            try:
                data = load_bundle(t, directory, tracker, ewp_checkout)
                source_check(t, directory, data, tracker)
            except FileNotFoundError as exc:
                result['tasks'][t] = {'status': 'UNAVAILABLE', 'missing_artifact': Path(exc.filename).name if exc.filename else str(exc)}
                continue
            entry = {'status': 'PREFLIGHT_VERIFIED', 'provenance': data['provenance']}
            if not preflight:
                entry['analysis'], private[t] = fn(data)
                entry.update(status='REPRODUCED_AND_ANALYZED', original_contract=data['historical'])
            result['tasks'][t] = entry
        tracker.recheck()
        result['input_preservation'] = {'verified_before_and_after': True, 'files': len(tracker.identities),
            'identity_set_sha256': sha(canonical(sorted(tracker.identities.values())))}
        result['completeness'] = 'COMPLETE' if all(v['status'] != 'UNAVAILABLE' for v in result['tasks'].values()) else 'PARTIAL'
        result['execution'] = {'python': platform.python_version(), 'wall_seconds': time.monotonic()-start,
            'max_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, 'workers': 1}
        if private:
            write(out/'private_details.json', private)
        write(out/'RESULTS.json', result)
        write(out/'input_identities.json', {str(p): h for p, h in tracker.identities.items()})
        write(out/'completion.json', {'status': 'COMPLETE', 'results_sha256': sha((out/'RESULTS.json').read_bytes())})
        return result
    except Exception as exc:
        write(out/'failure.json', {'type': type(exc).__name__, 'message': str(exc), 'results_valid': False})
        raise


def retained_report(path):
    path = Path(path)
    tracker = Inputs()
    completion = tracker.json(path/'completion.json')
    if completion['status'] != 'COMPLETE' or (path/'failure.json').exists():
        raise IntegrityStop('COMPLETED_RETAINED_AUDIT_REQUIRED')
    return tracker.json(path/'RESULTS.json', completion['results_sha256'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    for op in ('preflight', 'audit'):
        p = sub.add_parser(op)
        p.add_argument('--evidence-root', type=Path)
        p.add_argument('--ewp-checkout', type=Path, required=True)
        p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('report'); p.add_argument('--retained', type=Path, required=True)
    args = parser.parse_args()
    if args.operation == 'report':
        result = retained_report(args.retained)
    else:
        result = run(args.evidence_root, args.output, args.ewp_checkout, preflight=args.operation == 'preflight')
    print(json.dumps({'task': TASK, 'completeness': result['completeness'],
                      'tasks': {t: v['status'] for t, v in result['tasks'].items()}}, sort_keys=True))


if __name__ == '__main__':
    main()

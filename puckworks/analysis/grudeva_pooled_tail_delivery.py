"""Task 007: frozen parent models, mass-only prefix selection, private role projections.

No fitting or historical scoring. Parent mathematical runtime and source parser
remain unchanged. Source-derived row artifacts belong outside Git.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import time

from . import conditional_tail_delivery as md
from . import grudeva_clock as gc

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / 'docs/analysis/sci_md_mass_delivery_007'
TASK = 'SCI-MD-MASS-DELIVERY-007'
VERSION = 'grudeva-pooled-tail/1'
RUNTIME = 'puckworks/analysis/conditional_tail_delivery.py'
PARSER = 'puckworks/analysis/grudeva_clock.py'
PARENT_PARSER_COMMIT = '66c09e12916f2d0e1e1b66ecd30705a01aec7b5e'
CLAIMS = ('RESEARCH_ONLY', 'TARGET_EXPOSED', 'RETROSPECTIVE_CROSS_SOURCE_CONDITIONAL_PREDICTION',
          'CONDITIONAL_ON_COLLECTED_BEVERAGE_MASS', 'NO_EXACTLY_TWO_PHYSICAL_ASSAYS_CLAIM',
          'NOT_REAL_TIME_SAMPLING_POLICY', 'PHYSICAL_VALIDATION_NOT_ESTABLISHED')
read = lambda p: md.strict_json(Path(p).read_text())


def digest(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(p, value):
    with Path(p).open('x') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def private(p, create=False):
    p = Path(p).resolve()
    if any((x/'.git').exists() for x in (p, *p.parents)):
        raise ValueError('ROW_EVIDENCE_MUST_REMAIN_OUTSIDE_GIT')
    if create:
        p.mkdir(parents=True, exist_ok=False)
    return p


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def verify_dependencies(root=ROOT, doc=DOC):
    """Byte hashes and canonical identities are deliberately separate checks."""
    pin = read(doc/'PARENT_006_HANDOFF.json')
    if git(root, 'rev-parse', pin['producer_commit']+'^{tree}') != pin['producer_tree']:
        raise ValueError('BLOCKED_PARENT_IDENTITY: evaluated producer tree')
    required = {RUNTIME} | {m['path'] for m in pin['models'].values()}
    if (set(pin['models']) != set(md.ARMS) or pin['runtime_modules'] != [RUNTIME]
            or set(pin['producer_files']) != required):
        raise ValueError('BLOCKED_PARENT_IDENTITY: complete runtime/model matrix')
    for p, h in pin['producer_files'].items():
        path = (root/p).resolve()
        if not path.is_relative_to(root.resolve()) or digest(path) != h:
            raise ValueError('BLOCKED_PARENT_IDENTITY: artifact/runtime byte hash')
        blob = subprocess.check_output(['git', '-C', str(root), 'show', pin['producer_commit']+':'+p])
        if hashlib.sha256(blob).hexdigest() != h:
            raise ValueError('BLOCKED_PARENT_IDENTITY: evaluated commit bytes')
    if md.VERSION != pin['schema'] or md.UNITS != pin['units'] or list(md.CLAIMS) != pin['claims']:
        raise ValueError('BLOCKED_PARENT_IDENTITY: runtime schema')
    models = {a: md.Model.load(root/pin['models'][a]['path']) for a in md.ARMS}
    for a, m in models.items():
        if (m.arm != a or m.sha256 != pin['models'][a]['model_sha256']
                or m.rights != pin['rights'] or [0., m.domain_kg] != pin['domain_kg']):
            raise ValueError('BLOCKED_PARENT_IDENTITY: canonical model/domain/rights')
    old = subprocess.check_output(['git', '-C', str(root), 'show', PARENT_PARSER_COMMIT+':'+PARSER])
    if hashlib.sha256(old).hexdigest() != digest(root/PARSER):
        raise ValueError('BLOCKED_SOURCE_CONTRACT: accepted parser bytes')
    src = read(doc/'SOURCE.json')
    accepted = root/'docs/analysis/sci_md_grudeva_clock_001/SOURCE.json'
    if digest(doc/'SOURCE.json') != digest(accepted) or src['upstream_commit'] != gc.SOURCE_COMMIT or src['files']['exp13.csv'] != gc.SOURCE_SHA:
        raise ValueError('BLOCKED_SOURCE_CONTRACT: accepted source record')
    return models, pin, src


def verify_source(source_root):
    _, _, authority = verify_dependencies()
    for name, h in authority['files'].items():
        path = Path(source_root)/name
        if not path.is_file():
            raise ValueError('BLOCKED_SOURCE_ACCESS: '+name)
        if digest(path) != h:
            raise ValueError('BLOCKED_SOURCE_CONTRACT: '+name)
    return Path(source_root)/'exp13.csv'


@dataclass(frozen=True)
class Geometry:
    shot: int
    vial: int
    mass_g: float | None

    def __post_init__(self):
        if (type(self.shot) is not int or type(self.vial) is not int
                or self.shot < 1 or not 1 <= self.vial <= 16):
            raise ValueError('ORIGINAL_REGULAR_VIAL_IDENTITIES_REQUIRED')
        if self.mass_g is not None and md.number(self.mass_g) < 0:
            raise ValueError('NONNEGATIVE_RECORDED_MASS_REQUIRED')


def boundaries(geometry, means):
    """No chemistry, validity, model predictions or outcomes can enter selection."""
    if (not geometry or any(not isinstance(g, Geometry) for g in geometry)
            or len({g.shot for g in geometry}) != 1
            or [g.vial for g in geometry] != list(range(1, 17))):
        raise ValueError('COMPLETE_ORIGINAL_GEOMETRY_REQUIRED')
    if len(means) != 2 or any(md.number(v) <= 0 for v in means):
        raise ValueError('FROZEN_TWO_TRAINING_MASS_MEANS_REQUIRED')
    if any(g.mass_g is None for g in geometry):
        return None, 'UNAVAILABLE_MEASURED_MASS_PREFIX'
    # Decimal precision 50 is fixed, ample for all binary64 decimal representations.
    with localcontext() as context:
        context.prec = 50
        masses = [Decimal(str(g.mass_g))/1000 for g in geometry]
        b = []; total = Decimal(0)
        for m in masses:
            total += m; b.append(total)
        pos = [i for i, m in enumerate(masses) if m > 0]
        if len(pos) < 2:
            return None, 'INSUFFICIENT_POSITIVE_MASS_ENDPOINTS'
        mu1, mu2 = map(lambda v: Decimal(str(v)), means)
        i = min(pos[:-1], key=lambda k: (abs(b[k]-mu1), geometry[k].vial))
        j = min((k for k in pos if k > i), key=lambda k: (abs(b[k]-b[i]-mu2), geometry[k].vial))
        return {'k1': geometry[i].vial, 'k2': geometry[j].vial,
                'm1_kg': float(b[i]), 'm2_kg': float(b[j]-b[i]),
                'prefix_kg': float(b[j]), 'cumulative_kg': [float(v) for v in b],
                'mass_kg': [float(v) for v in masses]}, 'QUALIFIED'


def chemistry_status(r):
    """Accepted unavailable-zero semantics; values are not projected here."""
    m, t = r['mass_g'], r['tds_pct']
    if m is None:
        return 'UNKNOWN_MASS'
    md.number(m)
    if m < 0:
        raise ValueError('NEGATIVE_SOURCE_MASS')
    if m == 0:
        return 'STRUCTURAL_ZERO'
    if t is None or t == 0:
        return 'UNAVAILABLE_CHEMISTRY'
    if not 0 <= md.number(t) <= 100:
        raise ValueError('UNQUALIFIED_TDS_PERCENT')
    return 'AVAILABLE'


def pooled_input(geometry, selection, prefix):
    """Only selected prefix assays may cross this interface, in mass fractions."""
    end = selection['k2']
    expected = {g.vial for g in geometry[:end] if g.mass_g > 0}
    if set(prefix) != expected:
        raise ValueError('EXACT_PREFIX_ONLY_CHEMISTRY_REQUIRED')
    pools = []
    for lo, hi in ((0, selection['k1']), (selection['k1'], end)):
        members = []
        for g in geometry[lo:hi]:
            q = prefix.get(g.vial)
            if q is not None and not 0 <= md.number(q) <= 1:
                raise ValueError('MASS_FRACTION_REQUIRED')
            d = selection['mass_kg'][g.vial-1]
            members.append({'vial': g.vial, 'mass_kg': d, 'q': q,
                            'solute_kg': 0. if d == 0 else None if q is None else d*q,
                            'status': 'STRUCTURAL_ZERO' if d == 0 else 'UNAVAILABLE_CHEMISTRY' if q is None else 'AVAILABLE'})
        mass = math.fsum(r['mass_kg'] for r in members)
        solute = None if any(r['solute_kg'] is None for r in members) else math.fsum(r['solute_kg'] for r in members)
        pools.append({'vials': members, 'mass_kg': mass, 'solute_kg': solute,
                      'q': None if solute is None else solute/mass,
                      'original_assays': sum(r['mass_kg'] > 0 and r['q'] is not None for r in members),
                      'positive_mass_members': sum(r['mass_kg'] > 0 for r in members)})
    return pools


def project(records, means):
    """Parse container may have chemistry; returned prediction roles do not."""
    early, queries, support, cohorts, pool_records = [], [], [], [], []
    for shot in range(1, 14):
        rows = sorted((r for r in records if r['shot'] == shot and r['window'] == 'regular16'), key=lambda r: r['vial'])
        if any(r['discrepancy_at_source_precision'] for r in rows):
            raise ValueError('BLOCKED_SOURCE_CONTRACT: recorded Weight check')
        geometry = [Geometry(shot, r['vial'], r['mass_g']) for r in rows]
        selection, reason = boundaries(geometry, means)
        flags = {r['vial']: chemistry_status(r) for r in rows}
        pools, n = [], 0
        if selection:
            prefix = {r['vial']: r['tds_pct']/100 if flags[r['vial']] == 'AVAILABLE' else None
                      for r in rows[:selection['k2']] if r['mass_g'] > 0}
            pools = pooled_input(geometry, selection, prefix)
            n = sum(g.mass_g > 0 for g in geometry[selection['k2']:])
            if any(p['q'] is None for p in pools):
                reason = 'UNAVAILABLE_POOLED_CHEMISTRY'
            elif n < 2:
                reason = 'FEWER_THAN_TWO_REMAINING_POSITIVE_VIALS'
        eligible = reason == 'QUALIFIED'
        cohorts.append({'shot': shot, 'eligible': eligible, 'reason': reason,
                        'k1': selection['k1'] if selection else None,
                        'k2': selection['k2'] if selection else None,
                        'remaining_positive_vials': n})
        pool_records.append({'shot': shot, 'selection': selection, 'pools': pools})
        if not eligible:
            continue
        values = (selection['m1_kg'], selection['m2_kg'], pools[0]['q'], pools[1]['q'])
        for arm in md.ARMS:
            early.append({'shot': shot, 'arm': arm, 'input': md.EarlyInput(arm, values[:len(md.feature_names(arm))], 'SOURCE_EARLY_INPUT').to_dict()})
        for g in geometry[selection['k2']:]:
            b = selection['cumulative_kg']
            queries.append({'shot': shot, 'vial': g.vial, 'mass_kg': selection['mass_kg'][g.vial-1],
                            'start_kg': b[g.vial-2], 'end_kg': b[g.vial-1]})
            support.append({'shot': shot, 'vial': g.vial, 'chemistry_status': flags[g.vial],
                            'coordinate_status': 'QUALIFIED'})
    return early, queries, support, cohorts, pool_records


def prepare(source_root, out):
    models, pin, src = verify_dependencies()
    path = verify_source(source_root)
    out = private(out, create=True)
    rows = gc.parse_source(path)
    early, queries, support, cohort, pools = project(rows, models['C2'].means[:2])
    inventory = [{k: v for k, v in r.items() if k != 'tds_pct'} | {'chemistry_status': chemistry_status(r)} for r in rows]
    selected = {r['shot'] for r in cohort if r['eligible']}
    counts = {'raw_blocks': len({r['shot'] for r in rows}), 'rectangular_positions': len(rows),
        'nominal_physical_shots': 13, 'nominal_regular_vials': 208, 'eligible_shots': len(selected),
        'excluded_shots_by_reason': dict(Counter(r['reason'] for r in cohort if not r['eligible'])),
        'intended_suffix_vials': len(queries), 'positive_suffix_vials': sum(q['mass_kg'] > 0 for q in queries),
        'zero_width_suffix_vials': sum(q['mass_kg'] == 0 for q in queries),
        'suffix_mass_kg': math.fsum(q['mass_kg'] for q in queries),
        'prefix_mass_kg': math.fsum(r['selection']['prefix_kg'] for r in pools if r['shot'] in selected),
        'original_conditioning_assays': sum(p['original_assays'] for r in pools if r['shot'] in selected for p in r['pools']),
        'pooled_conditioning_summaries': 2*len(selected),
        'primary_suffix_missing_chemistry': sum(s['chemistry_status'] == 'UNAVAILABLE_CHEMISTRY' for s in support)}
    files = {'early_inputs.json': early, 'queries.json': queries, 'support.json': support,
        'cohort.json': cohort, 'pools.json': pools, 'source_inventory.json': inventory, 'counts.json': counts,
        'source_binding.json': {'task': TASK, 'source': src, 'source_record_sha256': digest(DOC/'SOURCE.json'),
            'parent_handoff_sha256': digest(DOC/'PARENT_006_HANDOFF.json'), 'mu1_mu2_kg': list(models['C2'].means[:2]),
            'parent_producer_commit': pin['producer_commit'], 'parent_producer_tree': pin['producer_tree']}}
    for name, value in files.items():
        write(out/name, value)
    write(out/'prepare_manifest.json', {'task': TASK, 'files': {name: digest(out/name) for name in files},
        'source_sha256': digest(path), 'version': VERSION})
    print(json.dumps(counts, indent=2))


def verify_manifest(out, name):
    manifest = read(out/name)
    if manifest['task'] != TASK:
        raise ValueError('WRONG_TASK')
    for p, h in manifest['files'].items():
        path = (out/p).resolve()
        if not path.is_relative_to(out.resolve()) or digest(path) != h:
            raise ValueError('FROZEN_ARTIFACT_DRIFT:'+p)
    return manifest


def input_index(early):
    result = {}
    for r in early:
        md.exact_keys(r, ('shot', 'arm', 'input'))
        e = md.EarlyInput.from_dict(r['input'])
        key = (r['arm'], r['shot'])
        if key in result or e.arm != r['arm'] or type(r['shot']) is not int:
            raise ValueError('DUPLICATE_OR_WRONG_EARLY_IDENTITY')
        result[key] = e
    return result


def checked_query(q):
    md.exact_keys(q, ('shot', 'vial', 'mass_kg', 'start_kg', 'end_kg'))
    Geometry(q['shot'], q['vial'], None)
    for name in ('mass_kg', 'start_kg', 'end_kg'):
        if q[name] is not None:
            md.number(q[name])
    if q['mass_kg'] is not None and q['mass_kg'] < 0:
        raise ValueError('NEGATIVE_QUERY_MASS')
    if all(q[k] is not None for k in ('mass_kg', 'start_kg', 'end_kg')):
        if q['end_kg'] < q['start_kg'] or abs(q['end_kg']-q['start_kg']-q['mass_kg']) > 8*math.ulp(max(q['end_kg'], q['mass_kg'])):
            raise ValueError('QUERY_MASS_COORDINATE_MISMATCH')
    return q


def runtime_coordinates(q, anchor):
    """Explicit shared-boundary binary conversion, never domain clipping."""
    a, b = q['start_kg'], q['end_kg']
    if a is None or b is None:
        raise ValueError('UNAVAILABLE_MEASURED_MASS_PREFIX')
    original_a, original_b = a, b
    # The only conversion considered is at the pooled-prefix origin boundary;
    # user queries farther before anchor remain unsupported.
    if a != anchor and abs(a-anchor) <= 4*math.ulp(anchor):
        a = anchor
        if b == original_a:  # structural zero interval
            b = anchor
    return a, b, 2*(abs(a-original_a)+abs(b-original_b))


def predict_records(models, early, queries):
    inputs = input_index(early)
    keys = [(q['shot'], q['vial']) for q in queries]
    if len(set(keys)) != len(keys) or set(models) != set(md.ARMS):
        raise ValueError('EXACT_ARM_QUERY_MATRIX_REQUIRED')
    shots = {q['shot'] for q in queries}
    if set(inputs) != {(a, s) for a in md.ARMS for s in shots}:
        raise ValueError('COMMON_SHOT_SUPPORT_REQUIRED')
    predictions, states = {}, {}
    for arm, model in models.items():
        predictions[arm] = []
        for query in queries:
            q = checked_query(query)
            result = dict(q, status='UNSUPPORTED', prediction=None, feature_extrapolation=[],
                          integration_start_kg=None, integration_end_kg=None, coordinate_allowance_kg=0.)
            try:
                key = (arm, q['shot'])
                if key not in states:
                    states[key] = model.condition(inputs[key])
                state = states[key]
                result['feature_extrapolation'] = list(state.feature_extrapolation)
                a, b, coordinate_allowance = runtime_coordinates(q, state.b_anchor)
                p = asdict(state.predict_intervals([a], [b])[0])
                p['allowance_kg'] += coordinate_allowance
                p['numerical_qualified'] = p['allowance_kg'] <= 1e-9
                result.update(status='QUALIFIED' if p['numerical_qualified'] else 'NUMERICALLY_UNRESOLVED',
                    prediction=p, integration_start_kg=a, integration_end_kg=b,
                    coordinate_allowance_kg=coordinate_allowance)
            except (ValueError, FloatingPointError, OverflowError) as exc:
                result['status'] = str(exc)
            predictions[arm].append(result)
    return predictions, {a+'/'+str(s): state.to_dict() for (a, s), state in states.items()}


def predict(out):
    out = private(out)
    verify_manifest(out, 'prepare_manifest.json')
    models, _, _ = verify_dependencies()
    start = time.monotonic()
    write(out/'prediction_start.json', {'task': TASK, 'status': 'STARTED',
        'prepare_manifest_sha256': digest(out/'prepare_manifest.json'),
        'execution_commit': git(ROOT, 'rev-parse', 'HEAD'), 'execution_tree': git(ROOT, 'rev-parse', 'HEAD^{tree}')})
    predictions, states = predict_records(models, read(out/'early_inputs.json'), read(out/'queries.json'))
    write(out/'predictions.json', predictions); write(out/'states.json', states)
    write(out/'prediction_completion.json', {'task': TASK, 'status': 'COMPLETE',
        'prediction_sets': 1, 'real_fits': 0, 'optimizer_calls': 0, 'native_runs': 0,
        'scientific_score_passes': 0, 'python': platform.python_version(),
        'wall_seconds': time.monotonic()-start,
        'status_counts': {a: dict(Counter(p['status'] for p in ps)) for a, ps in predictions.items()},
        'max_allowance_kg': max((p['prediction']['allowance_kg'] for ps in predictions.values() for p in ps if p['prediction']), default=0.),
        'files': {n: digest(out/n) for n in ('predictions.json', 'states.json', 'prediction_start.json')}})


def retain_reference(prior, out):
    """Only copies saved MASS rows after complete manifest and exclusion verification."""
    out = private(out); prior = Path(prior)
    authority = read(ROOT/'docs/analysis/sci_md_grudeva_clock_001/PRIVATE_EVIDENCE_MANIFEST.json')
    manifest_path = prior/'predictions/manifest.json'
    if digest(manifest_path) != authority['files']['predictions/manifest.json']:
        raise ValueError('REFERENCE_MANIFEST_IDENTITY_MISMATCH')
    manifest = read(manifest_path)
    if manifest['source_sha256'] != gc.SOURCE_SHA:
        raise ValueError('REFERENCE_SOURCE_MISMATCH')
    queries = read(out/'queries.json'); saved = []; folds = {}
    for shot in sorted({q['shot'] for q in queries}):
        name = f'primary-{shot:02}.json'; path = prior/'predictions'/name
        if digest(path) != manifest['files'][name]:
            raise ValueError('REFERENCE_FOLD_IDENTITY_MISMATCH')
        fold = read(path)
        if fold['held_shot'] != shot or fold['training_shots'] != [s for s in range(1, 14) if s != shot] or fold['timing'] != 'linear':
            raise ValueError('REFERENCE_SHOT_EXCLUSION_MISMATCH')
        rows = fold['predictions']['MASS']
        if rows is None or len(rows) != 16 or {r['vial'] for r in rows} != set(range(1, 17)):
            raise ValueError('REFERENCE_ROWS_UNAVAILABLE')
        folds[name] = digest(path)
        for q in (q for q in queries if q['shot'] == shot):
            r = next(r for r in rows if r['vial'] == q['vial'])
            if r['shot'] != shot or abs(r['mass_g']/1000-q['mass_kg']) > 1e-15 or abs(r['b_start_g']/1000-q['start_kg']) > 1e-15:
                raise ValueError('REFERENCE_GEOMETRY_MISMATCH')
            saved.append({'shot': shot, 'vial': q['vial'], 'retained_row': r})
    write(out/'reference.json', {'task': TASK, 'label': 'SOURCE_TRAINED_DIAGNOSTIC_DIFFERENT_INFORMATION_PRIVILEGES',
        'manifest_sha256': digest(manifest_path), 'fold_sha256': folds, 'rows': saved,
        'fresh_fits': 0, 'historical_scorer_called': False})


def freeze(out, consumer_root):
    out = private(out); consumer_root = Path(consumer_root)
    verify_dependencies(); verify_manifest(out, 'prepare_manifest.json')
    for root in (ROOT, consumer_root):
        if git(root, 'status', '--porcelain'):
            raise ValueError('CLEAN_COMMITTED_CANDIDATES_REQUIRED')
    completion = read(out/'prediction_completion.json')
    if completion['status'] != 'COMPLETE':
        raise ValueError('COMPLETE_PREDICTION_REQUIRED')
    for n, h in completion['files'].items():
        if digest(out/n) != h:
            raise ValueError('PREDICTION_BYTES_DRIFT')
    bound = [RUNTIME, PARSER, 'puckworks/analysis/grudeva_pooled_tail_delivery.py',
             'puckworks/analysis/grudeva_pooled_tail_scoring.py',
             'tests/test_grudeva_pooled_tail_delivery.py']
    bound += [str(p.relative_to(ROOT)) for p in DOC.iterdir() if p.is_file()]
    handoff = consumer_root/'docs/analysis/sci_md_mass_delivery_007/HANDOFF.json'
    cpin = read(handoff)
    if cpin['execution_producer_commit'] != git(ROOT, 'rev-parse', 'HEAD') or cpin['execution_producer_tree'] != git(ROOT, 'rev-parse', 'HEAD^{tree}'):
        raise ValueError('CONSUMER_EXECUTION_IDENTITY_MISMATCH')
    parity = read(out/'consumer_equivalence.json')
    if parity['status'] != 'PASS' or parity['predictions_sha256'] != digest(out/'predictions.json') or parity['handoff_sha256'] != digest(handoff):
        raise ValueError('CONSUMER_EQUIVALENCE_REQUIRED')
    consumer_files = ['scripts/research_conditional_tail_delivery.py', 'scripts/research_grudeva_pooled_tail_delivery.py',
                      'tests/test_research_grudeva_pooled_tail_delivery.py', 'docs/analysis/sci_md_mass_delivery_007/HANDOFF.json']
    write(out/'freeze.json', {'task': TASK, 'producer_commit': git(ROOT, 'rev-parse', 'HEAD'),
        'producer_tree': git(ROOT, 'rev-parse', 'HEAD^{tree}'),
        'producer_base': read(DOC/'BASES.json')['repositories']['puckworks']['base'],
        'consumer_commit': git(consumer_root, 'rev-parse', 'HEAD'), 'consumer_tree': git(consumer_root, 'rev-parse', 'HEAD^{tree}'),
        'consumer_base': read(DOC/'BASES.json')['repositories']['espresso-whole-pull']['base'],
        'code_and_protocol': {p: digest(ROOT/p) for p in sorted(bound)},
        'consumer_files': {p: digest(consumer_root/p) for p in consumer_files},
        'artifacts': {p.name: digest(p) for p in out.glob('*.json')},
        'primary_candidate': 'C2', 'arms': list(md.ARMS), 'scoring_policy': 'ONE_INDEPENDENTLY_APPROVED_PASS_NO_RETUNING'})
    print('READY_FOR_INDEPENDENT_REVIEW', digest(out/'freeze.json'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('prepare', 'predict', 'retain-reference', 'freeze', 'score', 'report'))
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--source-root', type=Path); parser.add_argument('--prior', type=Path)
    parser.add_argument('--consumer', type=Path); parser.add_argument('--review', type=Path)
    a = parser.parse_args()
    if a.operation == 'prepare':
        prepare(a.source_root, a.out)
    elif a.operation == 'predict':
        predict(a.out)
    elif a.operation == 'retain-reference':
        retain_reference(a.prior, a.out)
    elif a.operation == 'freeze':
        freeze(a.out, a.consumer)
    else:
        from . import grudeva_pooled_tail_scoring as scorer
        if a.operation == 'score':
            scorer.score(a.out, a.review, a.source_root, a.consumer)
        else:
            print(json.dumps(scorer.report(a.out), indent=2))


if __name__ == '__main__':
    main()

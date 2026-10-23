"""Independent scientific review: standard library only; no producer/helper imports.

Reconstructs original decimal coordinates before opening comparison artifacts.
The source PDF/native records are not reopened. Run after the plan commit:
  python docs/analysis/sci_md_corrochano_density_shift_001/review_check.py
Use --reconstruct-only to omit candidate-output comparisons; JSON goes to stdout.
"""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path


BUNDLE = Path('docs/analysis/sci_md_corrochano_density_shift_001')
SOURCE = Path('puckworks/data/romancorrochano2017/fig6_2_dry_compaction')
PREVIOUS = Path('docs/analysis/sci_md_corrochano_dry_compaction_001')


def merge(parts):
    merged = []
    for lo, hi in sorted(parts):
        assert lo <= hi
        if merged and lo <= merged[-1][1]:
            merged[-1][1] = max(hi, merged[-1][1])
        else:
            merged.append([lo, hi])
    return merged


def encloses(parts, interval):
    return any(a <= interval[0] <= interval[1] <= b for a, b in merge(parts))


def difference(left, right):
    return [left[0] - right[1], left[1] - right[0]]


def multiply(interval, scale):
    products = [x * s for x, s in product(interval, scale)]
    return [min(products), max(products)]


def classification(bounds, qualified=True):
    if not qualified:
        return 'UNSUPPORTED_OR_INCOMPLETE'
    return ('STRICTLY_SEPARATED' if bounds[0] > 0 or bounds[1] < 0
            else 'NOT_EXCLUDED_BY_THIS_COMPARISON')


def transform(row, chunk, height):
    sx, sy = map(Q, chunk['scale'])
    tx, ty = map(Q, chunk['translation'])
    ox, oy = map(Q, chunk['local_translation'])
    return (tx + sx * (ox + Q(row['raw_x'])),
            height - ty - sy * (oy + Q(row['raw_y'])))


def clip_all(segments, strip):
    """Intersect every segment, retaining boundary hits and interior vertices."""
    projected, parameters = [], []
    offset, previous_endpoint = 0, None
    for index, (a, b) in enumerate(segments):
        if index and previous_endpoint != a:
            offset += 1  # distinct path components do not acquire a synthetic join
        previous_endpoint = b
        dx, dy = b[0] - a[0], b[1] - a[1]
        if dx == 0:
            if not strip[0] <= a[0] <= strip[1]:
                continue
            begin, end = Q(0), Q(1)
        else:
            hits = sorted((bound - a[0]) / dx for bound in strip)
            begin, end = max(Q(0), hits[0]), min(Q(1), hits[1])
            if begin > end:
                continue
        yy = [a[1] + t * dy for t in [begin, end]]
        projected.append([min(yy), max(yy)])
        parameters.append([index + offset + begin, index + offset + end])
    return merge(projected), merge(parameters)


def query_positions(target, axis, anchor, trace):
    v0, v1 = map(Q, axis['values'])
    p0, p1 = map(Q, axis['positions_pt'])
    assert v0 < v1 and p0 + anchor < p1 - anchor
    weight = (Q(target) - v0) / (v1 - v0)
    positions = [(1 - weight) * a + weight * b
                 for a, b in product([p0 - anchor, p0 + anchor],
                                     [p1 - anchor, p1 + anchor])]
    nominal = (1 - weight) * p0 + weight * p1
    return [min(positions) - trace, max(positions) + trace], nominal


def read(segments, target, contract):
    guard, trace = Q(contract['anchor_guard_pt']), Q(contract['trace_guard_pt'])
    strip, nominal = query_positions(target, contract['axes']['force'], guard, trace)
    support = merge([sorted([a[0], b[0]]) for a, b in segments])
    nominal_y, nominal_components = clip_all(segments, [nominal, nominal])
    info = {'query_pt': strip, 'support_pt': support,
            'nominal_support': encloses(support, [nominal, nominal]),
            'full_support': encloses(support, strip),
            'nominal_branches': len(nominal_components), 'strip_branches': None,
            'status': 'UNSUPPORTED', 'z_bounds': None}
    if not info['full_support']:
        extent = [support[0][0], support[-1][1]] if support else None
        info['reason'] = ('QUERY_EXCEEDS_RECORDED_ENDPOINT' if extent is None or
                          not encloses([extent], strip) else 'QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP')
        return info
    yy, branches = clip_all(segments, strip)
    assert yy
    zz = merge([[-hi - trace, -lo + trace] for lo, hi in yy])
    ambiguous = (len(branches) > 1 or len(nominal_components) > 1 or
                 any(lo != hi for lo, hi in nominal_y))
    info.update(z_bounds=[zz[0][0], zz[-1][1]], z_set=zz, y_set=yy,
                strip_branches=len(branches), path_parameter_components=branches,
                status='AMBIGUOUS' if ambiguous else 'SUPPORTED',
                reason='MULTIPLE_INTERSECTIONS' if ambiguous else 'FULL_QUERY_SUPPORTED')
    # Independently replay accepted marginal density bounds. This adds the
    # density trace guard once to unexpanded y and varies all anchor corners.
    axis = contract['axes']['density']
    v0, v1 = map(Q, axis['values'])
    p0, p1 = map(Q, axis['positions_pt'])
    converted = []
    for low, high in yy:
        values = [v0 + (y - a) * (v1 - v0) / (b - a)
                  for y, a, b in product([low - trace, high + trace],
                      [p0 - guard, p0 + guard], [p1 - guard, p1 + guard])]
        converted.append([min(values), max(values)])
    info['density_set'] = merge(converted)
    info['density_bounds'] = [min(x[0] for x in converted), max(x[1] for x in converted)]
    return info


def reconstruct(root):
    fixed = json.loads((root / BUNDLE / 'calculation_contract.json').read_text())
    src = root / SOURCE
    for name, expected in fixed['inherited_input_hashes'].items():
        assert sha256((src / name).read_bytes()).hexdigest() == expected, name
    for name, expected in fixed['preserved_file_hashes'].items():
        assert sha256((root / name).read_bytes()).hexdigest() == expected, name
    assert sha256((root / BUNDLE / 'PLAN.md').read_bytes()).hexdigest() == fixed['plan_sha256']
    assert json.loads((root / PREVIOUS / 'RESULT.json').read_text())['input_hashes'] == fixed['inherited_input_hashes']
    contract = json.loads((src / 'contract.json').read_text())
    paths = json.loads((src / 'paths.json').read_text())
    rows = defaultdict(list)
    with (src / 'coordinates.csv').open() as stream:
        for row in csv.DictReader(stream):
            rows[row['chunk']].append(row)
    chunks = {c['chunk']: c for c in paths['chunks']}
    assert len(chunks) == len(paths['chunks']) == len(rows) == 80
    assert sum(map(len, rows.values())) == 17971
    points = {}
    for name, rr in rows.items():
        c = chunks[name]
        assert [int(r['vertex']) for r in rr] == list(range(len(rr)))
        assert rr[0]['operation'] == 'm' and all(r['operation'] == 'l' for r in rr[1:])
        points[name] = [transform(r, c, Q(paths['page_height_pt'])) for r in rr]
        assert points[name] == [(Q(r['x_pt']), Q(r['y_pt'])) for r in rr]
        assert all(r['trace'] == (c['trace'] or '') for r in rr)
        assert len(rr) == c['vertex_count']
    curve_chunks = {n for n, c in chunks.items() if c['role'] == 'curve'}
    assert len(curve_chunks) == paths['curve_unique_chunks'] == 76
    assert len(set(chunks) - curve_chunks) == paths['legend_strokes'] == 4
    paintings = [p for p in paths['paintings'] if p['chunk'] in curve_chunks]
    assert len(paintings) == paths['curve_paintings'] == 152
    first = {p['painting']: p for p in paintings if p['duplicate_of'] is None}
    assert len(first) == 76 and {p['chunk'] for p in first.values()} == curve_chunks
    for painting in paintings:
        if painting['duplicate_of'] is not None:
            original = first[painting['duplicate_of']]
            assert (painting['chunk'], painting['raw_path_sha256']) == (original['chunk'], original['raw_path_sha256'])
    # Reconstitute axes as well as curves from retained raw decimal transforms.
    for axis in paths['axes']:
        for x, y, op, px, py in axis['vertices']:
            assert transform({'raw_x': x, 'raw_y': y}, axis, Q(paths['page_height_pt'])) == (Q(px), Q(py))
    used, curves = [], {}
    joins = {(j['trace'], j['left'], j['right']): j for j in paths['joins']}
    assert len(joins) == len(paths['joins']) == 64
    used_joins = []
    for sample in fixed['samples']:
        sequence = paths['trace_chunks'][sample]
        assert all(chunks[c]['trace'] == sample for c in sequence)
        segments = []
        for i, name in enumerate(sequence):
            used.append(name)
            if i:
                previous = sequence[i - 1]
                join = joins[sample, previous, name]
                delta = [b - a for a, b in zip(points[previous][-1], points[name][0])]
                assert max(map(abs, delta)) <= Q(join['max_allowed_pt']) == Q(contract['join_limit_pt'])
                assert delta == list(map(Q, join['delta_pt']))
                segments.append((points[previous][-1], points[name][0]))
                used_joins.append((sample, previous, name))
            segments.extend(zip(points[name], points[name][1:]))
        curves[sample] = segments
    assert len(used) == len(set(used)) == 76 and set(used) == curve_chunks
    assert set(used_joins) == set(joins)
    axis = contract['axes']['density']
    v0, v1 = map(Q, axis['values'])
    p0, p1 = map(Q, axis['positions_pt'])
    anchor = Q(contract['anchor_guard_pt'])
    d = p0 - p1
    assert v1 > v0 and d > 2 * anchor
    beta = [(v1 - v0) / (d + 2 * anchor), (v1 - v0) / (d - 2 * anchor)]
    readings = {(s, f): read(curves[s], f, contract) for s in fixed['samples'] for f in fixed['forces_N']}
    increments, contrasts, envelopes, grind_comparisons = {}, {}, {}, {}
    assert list(map(list, combinations(fixed['forces_N'], 2))) == fixed['intervals_N']
    for a, b in map(tuple, fixed['intervals_N']):
        for sample in fixed['samples']:
            lo, hi = readings[sample, a], readings[sample, b]
            qualified = lo['full_support'] and hi['full_support']
            dz = difference(hi['z_bounds'], lo['z_bounds']) if qualified else None
            increments[sample, a, b] = {'z_bounds': dz, 'full_support': qualified,
                'bounds': multiply(dz, beta) if qualified else None,
                'status': ('UNSUPPORTED' if not qualified else 'AMBIGUOUS' if
                           'AMBIGUOUS' in (lo['status'], hi['status']) else 'SUPPORTED')}
        for left, right in combinations(fixed['samples'], 2):
            i, j = increments[left, a, b], increments[right, a, b]
            complete = i['full_support'] and j['full_support']
            cz = difference(i['z_bounds'], j['z_bounds']) if complete else None
            contrasts[left, right, a, b] = {'z_bounds': cz,
                'bounds': multiply(cz, beta) if complete else None,
                'classification': classification(cz, complete)}
        for grind in fixed['grinds']:
            members = [s for s in fixed['samples'] if s[0] == grind]
            present = [s for s in members if increments[s, a, b]['full_support']]
            dz = [increments[s, a, b]['z_bounds'] for s in present]
            hull = [min(x[0] for x in dz), max(x[1] for x in dz)] if dz else None
            envelopes[grind, a, b] = {'z_bounds': hull, 'present': present,
                'missing': [s for s in members if s not in present],
                'ambiguous': [s for s in present if increments[s, a, b]['status'] == 'AMBIGUOUS'],
                'bounds': multiply(hull, beta) if hull else None,
                'complete': present == members}
        for left, right in combinations(fixed['grinds'], 2):
            i, j = envelopes[left, a, b], envelopes[right, a, b]
            complete = i['complete'] and j['complete']
            cz = difference(i['z_bounds'], j['z_bounds']) if complete else None
            grind_comparisons[left, right, a, b] = {'z_bounds': cz,
                'bounds': multiply(cz, beta) if complete else None,
                'classification': classification(cz, complete)}
    return fixed, contract, beta, readings, increments, contrasts, envelopes, grind_comparisons



def display(bounds):
    if bounds is None:
        return None
    low = (bounds[0] * 10**6).__floor__()
    high = (bounds[1] * 10**6).__ceil__()
    return [('-' if value < 0 else '') + f'{abs(value)//10**6}.{abs(value)%10**6:06d}'
            for value in [low, high]]


def saved_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def encoded(row, key):
    return json.loads(row[key]) if row[key] else None


def rational_field(row, key):
    value = encoded(row, key)
    return list(map(Q, value)) if value is not None else None


def compare_output(root, fixed, beta, readings, increments, contrasts, envelopes, grind_comparisons):
    # This function is called only after reconstruction of every numerical result.
    bundle = root / BUNDLE
    old_rows = saved_rows(root / PREVIOUS / 'density_at_force.csv')
    assert len(old_rows) == len(readings) == 72
    for row in old_rows:
        got = readings[row['trace'], int(row['target'])]
        assert got['status'] == row['status']
        assert got['full_support'] == (row['full_support'] == 'True')
        assert got.get('density_bounds') == rational_field(row, 'bounds')
        if got['full_support']:
            assert got['density_set'] == [list(map(Q, x)) for x in encoded(row, 'output_set')]
    rows = saved_rows(bundle / 'density_at_force_coordinates.csv')
    assert [(r['trace'], int(r['force_N'])) for r in rows] == list(readings)
    assert len({r['id'] for r in rows}) == len(rows)
    for row in rows:
        got = readings[row['trace'], int(row['force_N'])]
        assert row['grind'] == row['trace'][0]
        for field in ['status', 'reason']:
            assert row[field] == got[field], (row['id'], field)
        for field in ['nominal_support', 'full_support']:
            assert (row[field] == 'True') == got[field], (row['id'], field)
        for field in ['nominal_branches', 'strip_branches']:
            assert (int(row[field]) if row[field] else None) == got[field], (row['id'], field)
        assert rational_field(row, 'query_pt') == got['query_pt']
        assert [list(map(Q, x)) for x in encoded(row, 'support_pt')] == got['support_pt']
        assert rational_field(row, 'bounds_pt') == got['z_bounds']
        assert rational_field(row, 'marginal_density_bounds_kg_m3') == got.get('density_bounds')
        if got['full_support']:
            for field, reference in [('downward_y_components_pt', 'y_set'), ('components_z_pt', 'z_set')]:
                assert [list(map(Q, x)) for x in encoded(row, field)] == got[reference]
    families = [('sample_density_increments', increments), ('sample_pair_contrasts', contrasts),
                ('grind_increment_envelopes', envelopes), ('cross_grind_comparisons', grind_comparisons)]
    compared = {}
    for name, expected in families:
        rows = saved_rows(bundle / (name + '.csv'))
        assert len(rows) == len(expected) and len({r['id'] for r in rows}) == len(rows)
        keys = []
        for row in rows:
            interval = (int(row['force_from_N']), int(row['force_to_N']))
            prefix = ((row['first'], row['second']) if 'first' in row else
                      (row['trace'],) if 'trace' in row else (row['grind'],))
            key = prefix + interval
            keys.append(key)
            got = expected[key]
            assert rational_field(row, 'bounds_pt') == got['z_bounds'], row['id']
            assert rational_field(row, 'bounds_kg_m3') == got['bounds'], row['id']
            # Compare exact bounds first; output decimals are only outward displays.
            for field, value in [('display_pt', got['z_bounds']), ('display_kg_m3', got['bounds'])]:
                assert encoded(row, field) == display(value)
            if 'classification' in got:
                assert row['classification'] == got['classification'], row['id']
                assert row['difference_orientation'] == 'first_minus_second'
                sign = (1 if got['z_bounds'][0] > 0 else -1 if got['z_bounds'][1] < 0 else 0) if got['z_bounds'] else None
                assert (int(row['sign']) if row['sign'] else None) == sign
                if name == 'sample_pair_contrasts':
                    assert (row['within_grind'] == 'True') == (row['first'][0] == row['second'][0])
            if name == 'sample_density_increments':
                assert row['status'] == got['status']
                assert row['grind'] == row['trace'][0]
                assert encoded(row, 'endpoints') == [f'z:{row["trace"]}:{force}' for force in interval]
            if name == 'grind_increment_envelopes':
                assert (row['completeness'] == 'COMPLETE') == got['complete']
                for field in ['present', 'missing']:
                    assert encoded(row, field) == got[field]
                assert encoded(row, 'ambiguous_members') == got['ambiguous']
        assert keys == list(expected), name
        compared[name] = len(rows)
    summary = json.loads((bundle / 'RESULT.json').read_text())
    assert list(map(Q, summary['calibration']['beta_kg_m3_per_pt'])) == beta
    assert summary['physical_validation'] == 'NOT_ESTABLISHED'
    assert summary['input_hashes'] == fixed['inherited_input_hashes']
    assert summary['reporting_set']['counts'] == fixed['counts']
    assert summary['counts_are_independent_replications'] is False
    assert summary['numerical_unresolved_readings'] == 0
    assert summary['marginal_replay']['status'] == 'EXACT_MATCH'
    assert summary['marginal_replay']['count'] == 72
    def disposition(records, expected):
        classes = [r['classification'] for r in records]
        if 'STRICTLY_SEPARATED' in classes:
            return 'EXCLUDED_BY_SAMPLE_INCREMENT_SEPARATION'
        if len(classes) == expected and all(c == 'NOT_EXCLUDED_BY_THIS_COMPARISON' for c in classes):
            return 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'
        return 'UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'
    assert summary['overall_disposition'] == disposition(list(contrasts.values()), 990)
    for entry in summary['intervals']:
        interval = tuple(entry['interval_N'])
        pairs = {key: value for key, value in contrasts.items() if key[-2:] == interval}
        assert entry['disposition'] == disposition(list(pairs.values()), 66)
        assert entry['sample_comparisons']['classification_counts'] == dict(Counter(r['classification'] for r in pairs.values()))
        expected_witnesses = [f'contrast:{left}:{right}:{a}:{b}' for (left, right, a, b), v in pairs.items()
                              if v['classification'] == 'STRICTLY_SEPARATED']
        assert entry['witness_ids'] == expected_witnesses
    primary = [r for key, r in contrasts.items() if key[-2:] == tuple(fixed['primary_interval_N'])]
    assert summary['primary_disposition'] == disposition(primary, 66)
    diagnostic = summary['exposed_comparison_diagnostic']
    old_increments = {sample: difference(readings[sample, 250]['density_bounds'], readings[sample, 25]['density_bounds'])
                      for sample in ['B1', 'E2']}
    for sample in ['B1', 'E2']:
        assert list(map(Q, diagnostic[sample]['old_marginal_subtraction_kg_m3'])) == old_increments[sample]
    assert list(map(Q, diagnostic['old_marginal_contrast_kg_m3'])) == difference(old_increments['B1'], old_increments['E2'])
    assert list(map(Q, diagnostic['direct_common_scale_contrast']['bounds_kg_m3'])) == contrasts['B1', 'E2', 25, 250]['bounds']
    compared['density_at_force_coordinates'] = len(readings)
    compared['predecessor_exact_density_marginal_replay'] = len(old_rows)
    return compared



def analytical_controls():
    assert difference([Q(10), Q(11)], [Q(8), Q(9)]) == [1, 3]
    assert multiply([Q(1), Q(3)], [Q(1), Q(2)]) == [1, 6]
    assert difference(multiply([Q(10), Q(11)], [Q(1), Q(2)]),
                      multiply([Q(8), Q(9)], [Q(1), Q(2)])) == [-8, 14]
    assert classification([Q(0), Q(1)]) == 'NOT_EXCLUDED_BY_THIS_COMPARISON'
    assert classification([Q(1, 10**12), Q(1)]) == 'STRICTLY_SEPARATED'
    assert classification(None, False) == 'UNSUPPORTED_OR_INCOMPLETE'
    assert multiply([Q(-2), Q(4)], [Q(3), Q(5)]) == [-10, 20]
    points = [(Q(x), Q(y)) for x, y in [(0, 0), (4, -10), (5, -1), (6, -8), (10, 0)]]
    projected, branches = clip_all(list(zip(points, points[1:])), [Q(4), Q(6)])
    assert projected == [[-10, -1]] and len(branches) == 1
    points = [(Q(x), Q(y)) for x, y in [(0, 0), (10, -10), (0, -20), (10, -30)]]
    projected, branches = clip_all(list(zip(points, points[1:])), [Q(5), Q(5)])
    assert projected == [[-25, -25], [-15, -15], [-5, -5]] and len(branches) == 3
    assert not encloses([[Q(0), Q(4)], [Q(6), Q(10)]], [Q(3), Q(7)])
    assert encloses([[Q(0), Q(4)], [Q(6), Q(10)]], [Q(3), Q(4)])
    assert clip_all([((Q(5), Q(-1)), (Q(5), Q(-9)))], [Q(5), Q(5)])[0] == [[-9, -1]]
    for alpha, beta in product([Q(-3), Q(2, 7)], [Q(1, 5), Q(3)]):
        offsets, levels = [Q(-5), Q(4)], [Q(9), Q(-2)]
        z = [[c + g for g in levels] for c in offsets]
        rho = [[alpha + beta * value for value in row] for row in z]
        assert rho[0][1] - rho[0][0] - rho[1][1] + rho[1][0] == 0
        assert [[(value-alpha)/beta for value in row] for row in rho] == z
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--reconstruct-only', action='store_true')
    args = parser.parse_args()
    analytical_controls()
    fixed, contract, beta, readings, increments, contrasts, envelopes, grind_comparisons = reconstruct(args.root)
    result = {'task': fixed['task'],
        'independence': 'Original-decimal reconstruction; standard library only; no producer/helper imports',
        'synthetic_review_controls_passed': True,
        'source_pdf_reopened': False, 'native_records_reopened': False,
        'source_and_predecessor_hashes_verified': True,
        'source_reconstruction': {'unique_curve_chunks': 76, 'duplicate_paintings_ignored': 76,
            'legends_excluded': 4, 'approved_joins': 64, 'raw_vertices_including_legends': 17971},
        'density_beta_kg_m3_per_pt': beta,
        'row_counts': dict(zip(['density_at_force_coordinates', 'sample_density_increments',
            'sample_pair_contrasts', 'grind_increment_envelopes', 'cross_grind_comparisons'],
            map(len, [readings, increments, contrasts, envelopes, grind_comparisons]))),
        'reading_status_counts': dict(Counter(r['status'] for r in readings.values())),
        'sample_comparison_counts': dict(Counter(r['classification'] for r in contrasts.values())),
        'primary_sample_comparison_counts': dict(Counter(r['classification'] for key, r in contrasts.items() if key[-2:] == (25, 250))),
        'grind_comparison_counts': dict(Counter(r['classification'] for r in grind_comparisons.values())),
        'primary_grind_comparison_counts': dict(Counter(r['classification'] for key, r in grind_comparisons.items() if key[-2:] == (25, 250))),
        'primary_B1_E2': {'B1_delta_z': increments['B1', 25, 250]['z_bounds'],
                          'E2_delta_z': increments['E2', 25, 250]['z_bounds'],
                          'first_minus_second': contrasts['B1', 'E2', 25, 250]},
        'output_comparison_performed': False}
    assert result['row_counts'] == fixed['counts']
    if not args.reconstruct_only:
        result['compared_rows'] = compare_output(args.root, fixed, beta, readings, increments, contrasts, envelopes, grind_comparisons)
        result['output_comparison_performed'] = True
    print(json.dumps(result, default=str, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()

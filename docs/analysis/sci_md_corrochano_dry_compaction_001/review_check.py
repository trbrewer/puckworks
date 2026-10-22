"""Independent review arithmetic; no analysis-producer/extractor imports.

Run with Python >=3.10. Optional --pdf authenticates retained raw operands against
the original thesis, using PyMuPDF only to decode the source stream. JSON goes to
stdout; the caller may preserve it outside Git or in the review receipt.
"""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as Q
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import re


def joined(intervals):
    answer = []
    for low, high in sorted(intervals):
        if answer and low <= answer[-1][1]:
            answer[-1][1] = max(high, answer[-1][1])
        else:
            answer.append([low, high])
    return answer


def transform(row, chunk, height):
    sx, sy = map(Q, chunk['scale'])
    tx, ty = map(Q, chunk['translation'])
    ox, oy = map(Q, chunk['local_translation'])
    return (tx + sx * (ox + Q(row['raw_x'])),
            height - ty - sy * (oy + Q(row['raw_y'])))


def source_audit(pdf, paths, rows):
    import pymupdf
    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    assert digest == paths['pdf_sha256']
    document = pymupdf.open(pdf)
    page = document[247]
    assert len(document) == 359 and page.xref == 2652
    assert page.get_contents() == [2653]
    stream = document.xref_stream(2653)
    assert hashlib.sha256(stream).hexdigest() == paths['decoded_content_sha256']
    colored = [d for d in page.get_drawings()
               if d['color'] in [(0, 0, 1), (1, 0, 0), (0, 1, 0), (1, 0, 1)]]
    assert len(colored) == 156
    chunks = {c['chunk']: c for c in paths['chunks']}
    tokens, states = [], []
    for paint, drawing in zip(paths['paintings'], colored):
        start, count = paint['raw_path_offset'], paint['raw_path_length']
        raw = stream[start:start + count]
        assert hashlib.sha256(raw).hexdigest() == paint['raw_path_sha256']
        parsed = re.findall(rb'([-\d.]+) ([-\d.]+) ([ml])', raw)
        assert not re.sub(rb'([-\d.]+) ([-\d.]+) ([ml])', b'', raw).strip()
        expected = [(r['raw_x'].encode(), r['raw_y'].encode(), r['operation'].encode())
                    for r in rows[paint['chunk']]]
        assert parsed == expected
        whole = stream[paint['raw_paint_offset']:paint['raw_paint_offset'] + paint['raw_paint_length']]
        matrices = re.findall(rb'([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+) cm', whole)
        chunk = chunks[paint['chunk']]
        assert len(matrices) == 2
        outer, inner = [[Q(n.decode()) for n in m] for m in matrices]
        assert outer == [Q(chunk['scale'][0]), 0, 0, Q(chunk['scale'][1]), *map(Q, chunk['translation'])]
        assert inner == [1, 0, 0, 1, *map(Q, chunk['local_translation'])]
        assert chunk['graphics_state'].encode() in whole
        assert tuple(map(int, chunk['color'].split())) == drawing['color']
        assert drawing['lineCap'] == (0, 0, 0) and drawing['lineJoin'] == 1
        assert drawing['dashes'] == chunk['dash']
        tokens.append(raw)
        states.append(whole[:whole.index(raw)])
    assert len(set(tokens[:76])) == 76
    assert tokens[:76] == tokens[76:152] and states[:76] == states[76:152]
    for axis in paths['axes']:
        raw = stream[axis['raw_path_offset']:axis['raw_path_offset'] + axis['raw_path_length']]
        assert hashlib.sha256(raw).hexdigest() == axis['raw_path_sha256']
        assert re.findall(rb'([-\d.]+) ([-\d.]+) ([ml])', raw) == [
            tuple(v.encode() for v in vertex[:3]) for vertex in axis['vertices']]
    return {'pdf_sha256': digest, 'decoded_content_sha256': paths['decoded_content_sha256'],
            'pages': len(document), 'paintings': len(tokens), 'unique_curve_chunks': 76,
            'duplicate_curve_paintings': 76, 'legend_strokes': 4,
            'all_retained_raw_operands_and_transform_matrices_match': True}


def strip(points, query, dimension):
    """Intersect via endpoints and boundary hits; count path-parameter components."""
    projected, path_parameters = [], []
    for index, (a, b) in enumerate(zip(points, points[1:])):
        candidates = {Q(0), Q(1)}
        delta = b[dimension] - a[dimension]
        if delta:
            candidates.update((boundary - a[dimension]) / delta for boundary in query)
        hits = [(t, a[1 - dimension] + t * (b[1 - dimension] - a[1 - dimension]))
                for t in candidates if 0 <= t <= 1
                and query[0] <= a[dimension] + t * delta <= query[1]]
        if hits:
            projected.append([min(v for t, v in hits), max(v for t, v in hits)])
            path_parameters.append([index + min(t for t, v in hits),
                                    index + max(t for t, v in hits)])
    return joined(projected), joined(path_parameters)


def read(points, target, dimension, query_axis, output_axis, anchor_guard, trace_guard):
    v0, v1 = map(Q, query_axis['values'])
    p0, p1 = map(Q, query_axis['positions_pt'])
    weight = (target - v0) / (v1 - v0)
    assert 0 <= weight <= 1  # in-range convex weights make anchor guard constant
    nominal = p0 + weight * (p1 - p0)
    radius = anchor_guard + trace_guard
    query = [nominal - radius, nominal + radius]
    extent = [min(p[dimension] for p in points), max(p[dimension] for p in points)]
    nominal_values, nominal_components = strip(points, [nominal, nominal], dimension)
    result = {'query_pt': query, 'support_pt': [extent],
              'nominal_support': extent[0] <= nominal <= extent[1],
              'full_support': extent[0] <= query[0] <= query[1] <= extent[1],
              'nominal_branches': len(nominal_components), 'strip_branches': None,
              'bounds': None, 'status': 'UNSUPPORTED'}
    if result['full_support']:
        intervals, components = strip(points, query, dimension)
        u0, u1 = map(Q, output_axis['values'])
        s0, s1 = map(Q, output_axis['positions_pt'])
        converted = []
        for low, high in intervals:
            candidates = [u0 + (point - first) * (u1 - u0) / (last - first)
                          for point, first, last in product(
                              [low - trace_guard, high + trace_guard],
                              [s0 - anchor_guard, s0 + anchor_guard],
                              [s1 - anchor_guard, s1 + anchor_guard])]
            converted.append([min(candidates), max(candidates)])
        result.update(output_set=joined(converted), strip_branches=len(components),
                      path_parameter_components=components,
                      bounds=[min(x[0] for x in converted), max(x[1] for x in converted)])
        ambiguous = (len(components) > 1 or len(nominal_components) > 1
                     or any(a != b for a, b in nominal_values))
        result['status'] = 'AMBIGUOUS' if ambiguous else 'SUPPORTED'
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--pdf', type=Path)
    args = parser.parse_args()
    bundle = args.root / 'docs/analysis/sci_md_corrochano_dry_compaction_001'
    data = args.root / 'puckworks/data/romancorrochano2017/fig6_2_dry_compaction'
    paths = json.loads((data / 'paths.json').read_text())
    contract = json.loads((data / 'contract.json').read_text())
    rows = defaultdict(list)
    for row in csv.DictReader((data / 'coordinates.csv').open()):
        rows[row['chunk']].append(row)
    assert sum(map(len, rows.values())) == 17971
    chunks = {c['chunk']: c for c in paths['chunks']}
    coords = {}
    for name, rr in rows.items():
        assert rr[0]['operation'] == 'm' and all(r['operation'] == 'l' for r in rr[1:])
        coords[name] = [transform(r, chunks[name], Q(paths['page_height_pt'])) for r in rr]
        assert coords[name] == [tuple(map(Q, (r['x_pt'], r['y_pt']))) for r in rr]
        assert [int(r['vertex']) for r in rr] == list(range(len(rr)))
    for axis in paths['axes']:
        for x, y, operation, px, py in axis['vertices']:
            assert transform({'raw_x': x, 'raw_y': y}, axis, Q(paths['page_height_pt'])) == (Q(px), Q(py))
    residuals = []
    for tick in paths['ticks']:
        calibration = contract['axes'][tick['axis']]
        v0, v1 = map(Q, calibration['values'])
        p0, p1 = map(Q, calibration['positions_pt'])
        residual = Q(tick['coordinate_pt']) - (p0 + (Q(tick['value']) - v0) * (p1 - p0) / (v1 - v0))
        # Provenance residuals use 28-digit Decimal; arithmetic here is rational.
        assert abs(residual - Q(tick['residual_pt'])) < Q('1e-24') and abs(residual) < Q('.044')
        residuals.append(abs(residual))
    half_stroke = max(3 * Q(s) / 2 for c in chunks.values() for s in c['scale'])
    assert half_stroke == Q('.91107135') < Q(contract['trace_guard_pt'])
    curves, join_count = {}, 0
    for trace in (g + str(j) for g in 'BCDE' for j in (1, 2, 3)):
        members = [c for c, m in chunks.items() if m['trace'] == trace]
        # Independently infer ordering from source endpoint proximity, not trace_chunks.
        edges = [(a, b) for a in members for b in members if a != b and
                 max(abs(x - y) for x, y in zip(coords[a][-1], coords[b][0])) <= Q('0.001')]
        starts = set(members) - {b for a, b in edges}
        assert len(starts) == 1 and len(edges) == len(members) - 1
        chain = [starts.pop()]
        while any(a == chain[-1] for a, b in edges):
            nexts = [b for a, b in edges if a == chain[-1]]
            assert len(nexts) == 1 and nexts[0] not in chain
            chain.append(nexts[0])
        assert set(chain) == set(members) and chain == paths['trace_chunks'][trace]
        assert [(a, b) for a, b in zip(chain, chain[1:])] == [
            (j['left'], j['right']) for j in paths['joins'] if j['trace'] == trace]
        join_count += len(edges)
        curves[trace] = [p for c in chain for p in coords[c]]
    assert len(curves) == 12 and join_count == 64
    result = {'independence': 'standard-library raw-coordinate computation; no producer/extractor imports',
              'curves': len(curves), 'rounding_joins': join_count, 'original_vertices': 17971,
              'maximum_tick_residual_pt': max(residuals), 'maximum_half_stroke_pt': half_stroke}
    if args.pdf:
        result['original_pdf_audit'] = source_audit(args.pdf, paths, rows)
    readings = {}
    for family, targets, dimension, qa, oa in [
        ('force_at_density', contract['density_targets_kg_m3'], 1, 'density', 'force'),
        ('density_at_force', contract['force_targets_N'], 0, 'force', 'density')]:
        for trace, points in curves.items():
            for target in targets:
                readings[f'{family}:{trace}:{target}'] = read(
                    points, Q(target), dimension, contract['axes'][qa], contract['axes'][oa],
                    Q(contract['anchor_guard_pt']), Q(contract['trace_guard_pt']))
    increments, envelopes, comparisons = {}, {}, []
    for first, last in contract['increments_kg_m3']:
        for trace in curves:
            a, b = [readings[f'force_at_density:{trace}:{x}'] for x in [first, last]]
            assert a['full_support'] and b['full_support']
            increments[f'increment:{trace}:{first}:{last}'] = {
                'bounds': [b['bounds'][0] - a['bounds'][1], b['bounds'][1] - a['bounds'][0]],
                'status': 'AMBIGUOUS' if 'AMBIGUOUS' in (a['status'], b['status']) else 'SUPPORTED'}
        for grind in 'BCDE':
            bounds = [increments[f'increment:{grind}{j}:{first}:{last}']['bounds'] for j in (1, 2, 3)]
            envelopes[grind, first, last] = [min(b[0] for b in bounds), max(b[1] for b in bounds)]
        for a, b in combinations('BCDE', 2):
            low_a, high_a = envelopes[a, first, last]
            low_b, high_b = envelopes[b, first, last]
            diff = [low_b - high_a, high_b - low_a]
            comparisons.append({'first': a, 'second': b, 'density_from': first, 'density_to': last,
                                'difference': diff, 'classification': 'STRICTLY_SEPARATED'
                                if diff[0] > 0 or diff[1] < 0 else 'NOT_EXCLUDED_BY_THIS_COMPARISON'})
    # Only after reconstruction do committed output tables enter this check.
    for family in ['force_at_density', 'density_at_force', 'sample_force_increments']:
        saved = list(csv.DictReader((bundle / (family + '.csv')).open()))
        assert len(saved) == {'force_at_density': 60, 'density_at_force': 72, 'sample_force_increments': 24}[family]
        computed = increments if family == 'sample_force_increments' else readings
        for row in saved:
            got = computed[row['request_id']]
            assert got['status'] == row['status'], row['request_id']
            expected_bounds = list(map(Q, json.loads(row['bounds']))) if row['bounds'] else None
            assert got['bounds'] == expected_bounds, row['request_id']
            if family != 'sample_force_increments':
                for flag in ['full_support', 'nominal_support']:
                    assert got[flag] == (row[flag] == 'True'), (row['request_id'], flag)
                for key in ['nominal_branches', 'strip_branches']:
                    assert got[key] == (int(row[key]) if row[key] else None), (row['request_id'], key)
                assert got['query_pt'] == list(map(Q, json.loads(row['query_pt'])))
                if got['full_support']:
                    assert got['output_set'] == [list(map(Q, x)) for x in json.loads(row['output_set'])]
    saved_envelopes = list(csv.DictReader((bundle / 'grind_increment_envelopes.csv').open()))
    assert len(saved_envelopes) == 8
    for row in saved_envelopes:
        assert row['completeness'] == 'COMPLETE'
        assert envelopes[row['grind'], int(row['density_from']), int(row['density_to'])] == list(map(Q, json.loads(row['bounds'])))
        assert json.loads(row['present']) == [row['grind'] + str(j) for j in (1, 2, 3)]
    saved_comparisons = list(csv.DictReader((bundle / 'cross_grind_comparisons.csv').open()))
    assert len(saved_comparisons) == 12
    for got, saved in zip(comparisons, saved_comparisons):
        assert got['difference'] == list(map(Q, json.loads(saved['difference'])))
        assert got['classification'] == saved['classification']
    assert len(readings) == 132 and len(increments) == 24 and len(comparisons) == 12
    saved_support = list(csv.DictReader((bundle / 'support_accounting.csv').open()))
    assert len(saved_support) == 156 and len({r['request_id'] for r in saved_support}) == 156
    for row in saved_support:
        assert row['status'] == (readings | increments)[row['request_id']]['status']
    result['statuses'] = dict(Counter(r['status'] for r in list(readings.values()) + list(increments.values())))
    result['endpoint_requests'] = len(readings)
    result['increment_requests'] = len(increments)
    result['complete_envelopes'] = len(envelopes)
    result['comparisons'] = comparisons
    result['decisive_primary'] = {
        'B_envelope': envelopes['B', 480, 500], 'E_envelope': envelopes['E', 480, 500],
        'B_samples': {f'B{j}': increments[f'increment:B{j}:480:500'] for j in (1, 2, 3)},
        'E_samples': {f'E{j}': increments[f'increment:E{j}:480:500'] for j in (1, 2, 3)},
        'minimum_gap_N': envelopes['E', 480, 500][0] - envelopes['B', 480, 500][1]}
    result['D2_rho360'] = readings['force_at_density:D2:360']
    result['E2_rho500'] = readings['force_at_density:E2:500']
    assert result['D2_rho360']['nominal_support'] and not result['D2_rho360']['full_support']
    assert result['E2_rho500']['nominal_branches'] == 1 and result['E2_rho500']['strip_branches'] == 2
    assert result['E2_rho500']['status'] == 'AMBIGUOUS' and result['E2_rho500']['full_support']
    result['all_saved_reading_increment_bounds_and_comparison_signs_match'] = True
    print(json.dumps(result, default=str, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

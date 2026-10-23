"""Independent raw-operand scientific review; Python standard library only.

No producer or inherited geometry helper imports. Candidate success flags and
bounds are never used to establish admissibility. --reconstruct-only opens no
new candidate results. verify_witness(root, candidate) supports adversarial tests.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

BUNDLE = Path('docs/analysis/sci_md_corrochano_density_normalization_001')
SOURCE = Path('puckworks/data/romancorrochano2017/fig6_2_dry_compaction')
PREVIOUS = Path('docs/analysis/sci_md_corrochano_dry_compaction_001')


def merge(intervals):
    out = []
    for lo, hi in sorted(intervals):
        assert lo <= hi, 'reversed interval'
        if out and lo <= out[-1][1]:
            out[-1][1] = max(hi, out[-1][1])
        else:
            out.append([lo, hi])
    return out


def encloses(parts, interval):
    return any(lo <= interval[0] <= interval[1] <= hi for lo, hi in parts)


def span(values):
    values = list(values)
    return [min(values), max(values)]


def difference(left, right):
    return [left[0]-right[1], left[1]-right[0]]


def quotient(numerator, denominator):
    assert 0 < denominator[0] <= denominator[1], 'nonpositive denominator'
    return span(x/y for x, y in product(numerator, denominator))


def classify(bounds):
    return ('STRICTLY_SEPARATED' if bounds[0] > 0 or bounds[1] < 0
            else 'NOT_EXCLUDED_BY_THIS_COMPARISON')


def sign(bounds):
    return 1 if bounds[0] > 0 else -1 if bounds[1] < 0 else 0


def transform(row, chunk, height):
    sx, sy = map(Q, chunk['scale'])
    tx, ty = map(Q, chunk['translation'])
    ox, oy = map(Q, chunk['local_translation'])
    return (tx+sx*(ox+Q(row['raw_x'])), height-ty-sy*(oy+Q(row['raw_y'])))


def parameter_range(start, finish, interval):
    """Closed preimage of interval under one affine coordinate, clipped to [0,1]."""
    if start == finish:
        return [Q(0), Q(1)] if interval[0] <= start <= interval[1] else None
    hits = sorted((bound-start)/(finish-start) for bound in interval)
    lo, hi = max(Q(0), hits[0]), min(Q(1), hits[1])
    return [lo, hi] if lo <= hi else None


def point_at(segment, t):
    a, b = segment['points_xy']
    return tuple(a[k]+t*(b[k]-a[k]) for k in (0, 1))


def clip_all(segments, strip):
    projected, path_positions = [], []
    offset, previous = 0, None
    for index, segment in enumerate(segments):
        a, b = segment['points_xy']
        if index and previous != a:
            offset += 1
        previous = b
        interval = parameter_range(a[0], b[0], strip)
        if interval is None:
            continue
        yy = [point_at(segment, t)[1] for t in interval]
        projected.append(span(yy))
        path_positions.append([index+offset+interval[0], index+offset+interval[1]])
    return merge(projected), merge(path_positions)


def force_position(target, contract, anchor):
    axis = contract['axes']['force']
    v0, v1 = map(Q, axis['values'])
    p0, p1 = map(Q, axis['positions_pt'])
    assert v0 < v1 and p0+anchor < p1-anchor, 'force slope guard'
    w = (Q(target)-v0)/(v1-v0)
    positions = [(1-w)*x+w*y for x, y in product(
        [p0-anchor, p0+anchor], [p1-anchor, p1+anchor])]
    trace = Q(contract['trace_guard_pt'])
    return [min(positions)-trace, max(positions)+trace], (1-w)*p0+w*p1


def read(segments, force, contract, nominal=False):
    trace = Q(contract['trace_guard_pt'])
    anchor = Q(0) if nominal else Q(contract['anchor_guard_pt'])
    strip, coordinate = force_position(force, contract, anchor)
    support = merge(sorted([s['points_xy'][0][0], s['points_xy'][1][0]]) for s in segments)
    nominal_y, nominal_path = clip_all(segments, [coordinate, coordinate])
    result = dict(query_pt=strip, support_pt=support, nominal_x=coordinate,
                  nominal_support=encloses(support, [coordinate, coordinate]),
                  full_support=encloses(support, strip), status='UNSUPPORTED',
                  nominal_branches=len(nominal_path), nominal_y=nominal_y)
    if not result['full_support']:
        result['reason'] = ('QUERY_EXCEEDS_RECORDED_ENDPOINT' if not support or
                            not encloses([[support[0][0], support[-1][1]]], strip)
                            else 'QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP')
        return result
    yy, positions = clip_all(segments, strip)
    assert yy, 'supported strip without an intersection'
    zz = merge([[-upper-trace, -lower+trace] for lower, upper in yy])
    ambiguous = (len(positions) > 1 or len(nominal_path) > 1
                 or any(lo != hi for lo, hi in nominal_y))
    result.update(z_set=zz, z_bounds=[zz[0][0], zz[-1][1]], y_set=yy,
                  strip_branches=len(positions), status='AMBIGUOUS' if ambiguous else 'SUPPORTED',
                  reason='MULTIPLE_INTERSECTIONS' if ambiguous else 'FULL_QUERY_SUPPORTED')
    axis = contract['axes']['density']
    r0, r1 = map(Q, axis['values'])
    p0, p1 = map(Q, axis['positions_pt'])
    values = [r0+(y-a)*(r1-r0)/(b-a) for low, high in yy
              for y, a, b in product([low-trace, high+trace],
                                    [p0-anchor, p0+anchor], [p1-anchor, p1+anchor])]
    result['density_bounds'] = span(values)
    return result


def raw_source(root):
    """Authenticate preserved bytes; rederive every retained vertex and approved join."""
    root = Path(root)
    fixed = json.loads((root/BUNDLE/'calculation_contract.json').read_text())
    assert sha256((root/BUNDLE/'PLAN.md').read_bytes()).hexdigest() == fixed['plan_sha256']
    for name, expected in fixed['preserved_file_hashes'].items():
        assert sha256((root/name).read_bytes()).hexdigest() == expected, 'preserved: '+name
    old = json.loads((root/PREVIOUS/'RESULT.json').read_text())['input_hashes']
    assert fixed['inherited_input_hashes'] == old
    for name, expected in old.items():
        assert sha256((root/SOURCE/name).read_bytes()).hexdigest() == expected, name
    contract = json.loads((root/SOURCE/'contract.json').read_text())
    paths = json.loads((root/SOURCE/'paths.json').read_text())
    grouped = defaultdict(list)
    with (root/SOURCE/'coordinates.csv').open() as stream:
        for row in csv.DictReader(stream):
            grouped[row['chunk']].append(row)
    chunks = {c['chunk']: c for c in paths['chunks']}
    assert len(chunks) == len(paths['chunks']) == len(grouped) == 80
    points = {}
    for name, rows in grouped.items():
        c = chunks[name]
        assert [int(r['vertex']) for r in rows] == list(range(len(rows)))
        assert rows[0]['operation'] == 'm' and all(r['operation'] == 'l' for r in rows[1:])
        assert len(rows) == c['vertex_count']
        points[name] = [transform(r, c, Q(paths['page_height_pt'])) for r in rows]
        assert points[name] == [(Q(r['x_pt']), Q(r['y_pt'])) for r in rows]
        assert all(r['trace'] == (c['trace'] or '') for r in rows)
    curves = {n for n, c in chunks.items() if c['role'] == 'curve'}
    assert len(curves) == paths['curve_unique_chunks'] == 76
    assert len(chunks)-len(curves) == paths['legend_strokes'] == 4
    paintings = [p for p in paths['paintings'] if p['chunk'] in curves]
    first = {p['painting']: p for p in paintings if p['duplicate_of'] is None}
    assert len(paintings) == paths['curve_paintings'] == 152 and len(first) == 76
    assert {p['chunk'] for p in first.values()} == curves
    for p in paintings:
        if p['duplicate_of'] is not None:
            original = first[p['duplicate_of']]
            assert (p['chunk'], p['raw_path_sha256']) == (original['chunk'], original['raw_path_sha256'])
    for axis in paths['axes']:
        for x, y, op, px, py in axis['vertices']:
            assert transform(dict(raw_x=x, raw_y=y), axis, Q(paths['page_height_pt'])) == (Q(px), Q(py))
    samples = [g+str(i) for g in 'BCDE' for i in range(1, 4)]
    assert fixed['samples'] == samples == sorted(paths['trace_chunks'])
    assert fixed['forces_N'] == contract['force_targets_N'] == [25, 50, 100, 150, 200, 250]
    assert fixed['intervals_N'] == list(map(list, combinations(fixed['forces_N'], 2)))
    joins = {(j['trace'], j['left'], j['right']): j for j in paths['joins']}
    assert len(joins) == len(paths['joins']) == 64
    used_chunks, used_joins, segments = [], [], {}
    for sample in samples:
        sequence = paths['trace_chunks'][sample]
        ss = []
        for i, chunk in enumerate(sequence):
            used_chunks.append(chunk)
            assert chunks[chunk]['trace'] == sample
            if i:
                previous = sequence[i-1]
                key = (sample, previous, chunk)
                if key in joins:
                    join = joins[key]
                    a, b = points[previous][-1], points[chunk][0]
                    delta = [y-x for x, y in zip(a, b)]
                    assert delta == list(map(Q, join['delta_pt']))
                    assert max(map(abs, delta)) <= Q(join['max_allowed_pt']) == Q(contract['join_limit_pt'])
                    ss.append(dict(index=len(ss), kind='APPROVED_JOIN', left_chunk=previous,
                                   right_chunk=chunk, points_xy=(a, b)))
                    used_joins.append(key)
            for vertex, (a, b) in enumerate(zip(points[chunk], points[chunk][1:])):
                ss.append(dict(index=len(ss), kind='ORIGINAL', chunk=chunk,
                               vertex_from=vertex, vertex_to=vertex+1, points_xy=(a, b)))
        segments[sample] = ss
    assert len(used_chunks) == len(set(used_chunks)) == 76 and set(used_chunks) == curves
    assert set(used_joins) == set(joins)
    return fixed, contract, paths, segments


def calibration(contract):
    axis = contract['axes']['density']
    r0, r1 = map(Q, axis['values'])
    p0, p1 = map(Q, axis['positions_pt'])
    guard = Q(contract['anchor_guard_pt'])
    assert r1 > r0 and p0-p1 > 2*guard, 'density slope guard'
    tau = span((r1*(p0+e0)-r0*(p1+e1))/(r1-r0)
               for e0, e1 in product([-guard, guard], repeat=2))
    beta = (r1-r0)/(p0-p1)
    return dict(tau=tau, alpha=r0+beta*p0, beta=beta,
                beta_bounds=[(r1-r0)/(p0-p1+2*guard), (r1-r0)/(p0-p1-2*guard)])


def ratio(before, after, tau):
    assert before[0]+tau[0] > 0, 'nonpositive ratio denominator'
    return span((b+t)/(a+t) for a, b, t in product(before, after, tau))


def determinant(ia, ib, ja, jb, tau):
    assert min(ia[0], ib[0], ja[0], jb[0])+tau[0] > 0, 'nonpositive endpoint'
    c = span(y*v-w*x+t*(y+v-w-x) for x, y, v, w, t in product(ia, ib, ja, jb, tau))
    denominator = span((x+t)*(v+t) for x, v, t in product(ia, ja, tau))
    return c, denominator, quotient(c, denominator)


def reconstruct(root):
    fixed, contract, paths, segments = raw_source(root)
    cal = calibration(contract)
    readings = {(s, f): read(segments[s], f, contract)
                for s in fixed['samples'] for f in fixed['forces_N']}
    # Old output is a check only, after new coordinates and bounds exist.
    with (Path(root)/PREVIOUS/'density_at_force.csv').open() as stream:
        old = {(r['trace'], int(r['target'])): r for r in csv.DictReader(stream)}
    for key, r in readings.items():
        saved = old[key]
        assert r['status'] == saved['status'] and r['full_support'] == (saved['full_support'] == 'True')
        assert r['density_bounds'] == list(map(Q, json.loads(saved['bounds'])))
    ratios, contrasts, envelopes, grind_pairs = {}, {}, {}, {}
    for a, b in fixed['intervals_N']:
        for sample in fixed['samples']:
            lo, hi = readings[sample, a], readings[sample, b]
            assert lo['full_support'] and hi['full_support'], (sample, a, b, 'incomplete retained support')
            ratios[sample, a, b] = ratio(lo['z_bounds'], hi['z_bounds'], cal['tau'])
        for left, right in combinations(fixed['samples'], 2):
            z = [readings[s, f]['z_bounds'] for s, f in [(left, a), (left, b), (right, a), (right, b)]]
            c, denominator, direct = determinant(*z, cal['tau'])
            contrasts[left, right, a, b] = dict(determinant=c, denominator=denominator,
                direct=direct, marginal=difference(ratios[left, a, b], ratios[right, a, b]),
                classification=classify(c), sign=sign(c))
        for grind in fixed['grinds']:
            bounds = [ratios[s, a, b] for s in fixed['samples'] if s[0] == grind]
            envelopes[grind, a, b] = [min(x[0] for x in bounds), max(x[1] for x in bounds)]
        for left, right in combinations(fixed['grinds'], 2):
            pairs = [contrasts[i, j, a, b] for i in fixed['samples'] if i[0] == left
                     for j in fixed['samples'] if j[0] == right]
            signs = [p['sign'] for p in pairs]
            direction = signs[0] if all(s == signs[0] != 0 for s in signs) else 0
            grind_pairs[left, right, a, b] = dict(sign=direction,
                classification='STRICTLY_SEPARATED' if direction else 'NOT_EXCLUDED_BY_THIS_COMPARISON',
                marginal=difference(envelopes[left, a, b], envelopes[right, a, b]))
    return dict(fixed=fixed, contract=contract, paths=paths, segments=segments, calibration=cal,
                readings=readings, ratios=ratios, contrasts=contrasts, envelopes=envelopes,
                grind_pairs=grind_pairs)


def construct_affine(source):
    fixed, contract, segments = (source[k] for k in ['fixed', 'contract', 'segments'])
    nominal = {(s, f): read(segments[s], f, contract, nominal=True)
               for s in fixed['samples'] for f in fixed['forces_N']}
    parameters = {}
    for sample in fixed['samples']:
        assert all(nominal[sample, f]['full_support'] for f in fixed['forces_N']), sample+' support'
        c = sum(nominal[sample, 25]['z_bounds'])/2
        a = sum(nominal[sample, 250]['z_bounds'])/2-c
        assert a > 0, sample+' amplitude'
        parameters[sample] = dict(c=c, a=a, b=source['calibration']['alpha']+source['calibration']['beta']*c,
                                  s=source['calibration']['beta']*a)
    levels = {25: Q(0), 250: Q(1)}
    intersections = {}
    for force in fixed['forces_N'][1:-1]:
        intervals = {}
        for sample in fixed['samples']:
            p = parameters[sample]
            intervals[sample] = [(v-p['c'])/p['a'] for v in nominal[sample, force]['z_bounds']]
        common = [max(x[0] for x in intervals.values()), min(x[1] for x in intervals.values())]
        assert common[0] <= common[1], (force, 'empty common intersection')
        intersections[force] = dict(bounds=common, members=intervals)
        levels[force] = sum(common)/2
    assert all(levels[a] < levels[b] for a, b in zip(fixed['forces_N'], fixed['forces_N'][1:])), 'h order'
    certificates = {}
    trace = Q(contract['trace_guard_pt'])
    for sample in fixed['samples']:
        previous = None
        for force in fixed['forces_N']:
            p = parameters[sample]
            z = p['c']+p['a']*levels[force]
            reading = nominal[sample, force]
            x = reading['nominal_x']
            assert encloses(reading['z_set'], [z, z]), (sample, force, 'hull gap')
            found = None
            for segment in segments[sample]:
                a, b = segment['points_xy']
                tx = parameter_range(a[0], b[0], [x-trace, x+trace])
                tz = parameter_range(-a[1], -b[1], [z-trace, z+trace])
                if tx is None or tz is None:
                    continue
                feasible = [max(tx[0], tz[0]), min(tx[1], tz[1])]
                if feasible[0] > feasible[1]:
                    continue
                t = sum(feasible)/2
                sx, sy = point_at(segment, t)
                position = segment['index']+t
                rho = source['calibration']['alpha']+source['calibration']['beta']*z
                assert rho == p['b']+p['s']*levels[force] > 0
                assert p['s'] > 0
                assert previous is None or previous < position, (sample, force, 'path order')
                previous = position
                found = dict(segment=segment, feasible=feasible, t=t, source_x=sx, source_z=-sy,
                             x=x, z=z, dx=x-sx, dz=z+sy, position=position, rho=rho)
                break
            assert found is not None, (sample, force, 'no source certificate')
            certificates[sample, force] = found
    return dict(readings=nominal, parameters=parameters, levels=levels,
                intersections=intersections, certificates=certificates)


def rational(value):
    """Reject JSON floats: certificate arithmetic must preserve original fractions."""
    assert isinstance(value, (str, int)) and not isinstance(value, bool), 'non-exact certificate scalar'
    return Q(value)


def rationals(values):
    return [rational(x) for x in values]


def unique_rows(rows, keys, expected):
    assert len(rows) == expected, ('row count', keys, expected, len(rows))
    mapping = {tuple(r[k] for k in keys): r for r in rows}
    assert len(mapping) == expected, ('duplicate row', keys)
    assert len({r['id'] for r in rows}) == expected, ('duplicate id', keys)
    return mapping


def check_reading(candidate, expected, label):
    assert candidate['full_support'] == expected['full_support'], (label, 'support')
    assert candidate['status'] == expected['status'], (label, 'status')
    assert rationals(candidate['query_pt']) == expected['query_pt'], (label, 'strip')
    assert [rationals(p) for p in candidate['support_pt']] == expected['support_pt'], (label, 'support union')
    assert [rationals(p) for p in candidate['components_z_pt']] == expected['z_set'], (label, 'component union')
    assert rationals(candidate['bounds_pt']) == expected['z_bounds'], (label, 'hull')
    assert candidate['nominal_support'] == expected['nominal_support'], (label, 'nominal support')
    assert candidate['nominal_branches'] == expected['nominal_branches'], (label, 'nominal branches')
    assert candidate['strip_branches'] == expected['strip_branches'], (label, 'strip branches')


def verify_witness(root, candidate):
    """Verify parsed candidate without trusting its status or producer-derived bounds.

    Rebuild all source segments and construction inputs from retained original
    decimal operands on every invocation, so copied bounds cannot certify points.
    """
    source = reconstruct(root)
    expected = construct_affine(source)
    fixed, contract = source['fixed'], source['contract']
    cc = candidate['calibration']
    assert rationals(cc['force_values_N']) == list(map(Q, contract['axes']['force']['values'])), 'force values'
    assert rationals(cc['force_positions_pt']) == list(map(Q, contract['axes']['force']['positions_pt'])), 'nominal force anchors'
    assert rationals(cc['density_values_kg_m3']) == list(map(Q, contract['axes']['density']['values'])), 'density values'
    assert rationals(cc['downward_density_positions_pt']) == list(map(Q, contract['axes']['density']['positions_pt'])), 'nominal density anchors'
    assert rational(cc['alpha']) == source['calibration']['alpha'], 'nominal alpha'
    assert rational(cc['beta']) == source['calibration']['beta'] > 0, 'nominal beta'
    assert rational(cc['trace_allowance_pt']) == Q(contract['trace_guard_pt']), 'trace guard'
    pp = unique_rows(candidate['parameters'], ['trace'], 12)
    ll = unique_rows(candidate['levels'], ['force_N'], 6)
    ii = unique_rows(candidate['intersections'], ['force_N'], 4)
    rr = unique_rows(candidate['readings'], ['trace', 'force_N'], 72)
    ss = unique_rows(candidate['certificates'], ['trace', 'force_N'], 72)
    assert set(pp) == {(s,) for s in fixed['samples']}, 'parameter sample set'
    assert set(ll) == {(f,) for f in fixed['forces_N']}, 'common level set'
    assert set(ii) == {(f,) for f in fixed['forces_N'][1:-1]}, 'intermediate intersection set'
    expected_keys = set(product(fixed['samples'], fixed['forces_N']))
    assert set(rr) == set(ss) == expected_keys, 'reading/certificate set'
    param_fields = dict(c_pt='c', a_pt='a', b_kg_m3='b', s_kg_m3='s')
    for (sample,), row in pp.items():
        p = expected['parameters'][sample]
        assert row['grind'] == sample[0], (sample, 'grind')
        for name, key in param_fields.items():
            assert rational(row[name]) == p[key], (sample, name, 'fixed parameter')
        assert p['a'] > 0 and p['s'] > 0, (sample, 'positive amplitude')
        assert row['endpoint_refs'] == [rr[sample, f]['id'] for f in (25, 250)], (sample, 'endpoint refs')
    for (force,), row in ll.items():
        assert rational(row['h']) == expected['levels'][force], (force, 'shared h midpoint')
    ordered_h = [rational(ll[f,]['h']) for f in fixed['forces_N']]
    assert ordered_h[0] == 0 and ordered_h[-1] == 1, 'finite gauge'
    assert all(a < b for a, b in zip(ordered_h, ordered_h[1:])), 'h order'
    for (force,), row in ii.items():
        assert rationals(row['bounds']) == expected['intersections'][force]['bounds'], (force, 'intersection')
        assert rational(row['selected_h']) == expected['levels'][force], (force, 'intersection midpoint')
        members = row['members']
        if isinstance(members, dict):
            bounds = {s: rationals(v) for s, v in members.items()}
        else:
            assert len(members) == 12, (force, 'intersection members')
            bounds = {m['trace']: rationals(m['bounds']) for m in members}
            for member in members:
                sample = member['trace']
                assert member['reading_ref'] == rr[sample, force]['id'], (force, sample, 'intersection reading ref')
                assert member['parameter_ref'] == pp[sample,]['id'], (force, sample, 'intersection parameter ref')
        assert bounds == expected['intersections'][force]['members'], (force, 'twelve normalized intervals')
    for key, row in rr.items():
        check_reading(row, expected['readings'][key], ('nominal reading', key))
    previous = {}
    for sample in fixed['samples']:
        for force in fixed['forces_N']:
            key = (sample, force)
            row, target = ss[key], expected['certificates'][key]
            label = ('certificate', sample, force)
            p = expected['parameters'][sample]
            assert row['grind'] == sample[0], (label, 'grind')
            assert row['reading_ref'] == rr[key]['id'], (label, 'reading ref')
            assert row['parameter_ref'] == pp[sample,]['id'], (label, 'parameter ref')
            assert row['level_ref'] == ll[force,]['id'], (label, 'common level ref')
            for name, name_in_p in param_fields.items():
                assert rational(row[name]) == p[name_in_p], (label, name, 'per-force substitution')
            assert rational(row['h']) == expected['levels'][force], (label, 'per-sample h substitution')
            segment = row['segment']
            index = segment['index']
            assert isinstance(index, int) and 0 <= index < len(source['segments'][sample]), (label, 'segment index')
            actual_segment = source['segments'][sample][index]
            assert index == target['segment']['index'], (label, 'first admissible segment tie-break')
            for field in ('kind', 'chunk', 'left_chunk', 'right_chunk', 'vertex_from', 'vertex_to'):
                if field in actual_segment:
                    assert segment.get(field) == actual_segment[field], (label, field)
            a, b = actual_segment['points_xy']
            assert [rationals(v) for v in segment['endpoints_xz']] == [[a[0], -a[1]], [b[0], -b[1]]], (label, 'raw segment endpoints')
            expected_ref = (f"coordinates.csv:{actual_segment['chunk']}:{actual_segment['vertex_from']}:{actual_segment['vertex_to']}"
                            if actual_segment['kind'] == 'ORIGINAL' else
                            f"paths.json:join:{sample}:{actual_segment['left_chunk']}:{actual_segment['right_chunk']}")
            assert segment['source_ref'] == expected_ref, (label, 'source reference')
            t = rational(row['t'])
            assert 0 <= t <= 1, (label, 'segment parameter')
            assert t == target['t'], (label, 'feasible parameter midpoint')
            assert rationals(row['feasible_t']) == target['feasible'], (label, 'feasible parameter interval')
            sx, sy = point_at(actual_segment, t)
            assert rational(row['source_x_pt']) == sx, (label, 'segment x membership')
            assert rational(row['source_z_pt']) == -sy, (label, 'segment z membership')
            nominal_x = expected['readings'][key]['nominal_x']
            z = rational(row['selected_z_pt'])
            assert z == p['c']+p['a']*expected['levels'][force], (label, 'selected affine z')
            assert rational(row['nominal_x_pt']) == nominal_x, (label, 'force coordinate')
            dx, dz = nominal_x-sx, z+sy
            assert rational(row['dx_pt']) == dx and rational(row['dz_pt']) == dz, (label, 'displacement identity')
            assert abs(dx) <= Q(contract['trace_guard_pt']), (label, 'horizontal trace allowance')
            assert abs(dz) <= Q(contract['trace_guard_pt']), (label, 'vertical trace allowance')
            components = expected['readings'][key]['z_set']
            assert encloses(components, [z, z]), (label, 'hull-gap point')
            component_index = row['component_index']
            assert isinstance(component_index, int) and 0 <= component_index < len(components), (label, 'component index')
            component = components[component_index]
            assert component[0] <= z <= component[1], (label, 'actual component membership')
            assert rationals(row['component_z_pt']) == component, (label, 'component reference')
            position = index+t
            assert rational(row['path_position']) == position, (label, 'ordered path position')
            assert sample not in previous or previous[sample] < position, (label, 'path order violation')
            previous[sample] = position
            rho = source['calibration']['alpha']+source['calibration']['beta']*z
            assert rational(row['density_kg_m3']) == rho == p['b']+p['s']*expected['levels'][force], (label, 'physical affine identity')
            assert rho > 0, (label, 'positive density')
    return dict(status='ALL_72_CERTIFICATES_INDEPENDENTLY_VERIFIED', count=len(ss),
                parameters=len(pp), levels=len(ll), intersections=len(ii), calibrations=1)


def saved_rows(path):
    with path.open() as stream:
        rows = list(csv.DictReader(stream))
    integers = {'force_N', 'force_from_N', 'force_to_N', 'component_index',
                'nominal_branches', 'strip_branches', 'sign'}
    for row in rows:
        for key, value in row.items():
            if value == '':
                row[key] = None
            elif value in ('True', 'False'):
                row[key] = value == 'True'
            elif value[0] in '[{':
                row[key] = json.loads(value)
            elif key in integers:
                row[key] = int(value)
    return rows


def outward(bounds, places=6):
    scale = 10**places
    integers = [(bounds[0]*scale).__floor__(), (bounds[1]*scale).__ceil__()]
    return [('-' if n < 0 else '')+f'{abs(n)//scale}.{abs(n)%scale:0{places}d}' for n in integers]


def compare_outputs(root, source):
    root = Path(root)
    tables = {}
    fixed = source['fixed']
    fields = {'density_at_force_coordinates': ['trace', 'force_N'],
              'sample_density_ratios': ['trace', 'force_from_N', 'force_to_N'],
              'sample_pair_contrasts': ['first', 'second', 'force_from_N', 'force_to_N'],
              'grind_ratio_envelopes': ['grind', 'force_from_N', 'force_to_N'],
              'cross_grind_comparisons': ['first', 'second', 'force_from_N', 'force_to_N']}
    for name, count in fixed['counts'].items():
        tables[name] = unique_rows(saved_rows(root/BUNDLE/(name+'.csv')), fields[name], count)
    rr, ratios, contrasts, envelopes, grinds = [tables[name] for name in fields]
    assert set(rr) == set(source['readings']), 'A reading keys'
    for key, row in rr.items():
        expected = source['readings'][key]
        check_reading(row, expected, ('full reading', key))
        assert rationals(row['marginal_density_bounds_kg_m3']) == expected['density_bounds'], (key, 'marginal replay')
        assert row['source_chunks'] == source['paths']['trace_chunks'][key[0]], (key, 'source chunks')
        assert row['display_pt'] == outward(expected['z_bounds']), (key, 'outward z display')
    assert set(ratios) == set(source['ratios']), 'ratio keys'
    for (sample, a, b), row in ratios.items():
        assert row['full_support'] and row['status'] == 'SUPPORTED' and not row['ambiguous']
        bounds = source['ratios'][sample, a, b]
        assert rationals(row['bounds_ratio']) == bounds, (sample, a, b, 'ratio')
        assert row['display_ratio'] == outward(bounds), (sample, a, b, 'ratio display')
        assert row['endpoints'] == [rr[sample, f]['id'] for f in (a, b)], 'ratio endpoint refs'
    assert set(contrasts) == set(source['contrasts']), 'contrast keys'
    for (left, right, a, b), row in contrasts.items():
        expected = source['contrasts'][left, right, a, b]
        assert row['full_support'] and row['status'] == 'SUPPORTED' and not row['ambiguous']
        assert row['classification'] == expected['classification'] and row['sign'] == expected['sign']
        assert row['difference_orientation'] == 'first_minus_second'
        assert row['within_grind'] == (left[0] == right[0])
        assert row['endpoints'] == [rr[s, f]['id'] for s, f in [(left, a), (left, b), (right, a), (right, b)]]
        for field, key in [('determinant_pt2', 'determinant'), ('denominator_pt2', 'denominator'),
                           ('ratio_difference', 'direct')]:
            assert rationals(row[field]) == expected[key], (left, right, a, b, field)
        assert row['determinant_display_pt2'] == outward(expected['determinant'])
        assert row['ratio_difference_display'] == outward(expected['direct'])
    assert set(envelopes) == set(source['envelopes']), 'envelope keys'
    for (grind, a, b), row in envelopes.items():
        members = [s for s in fixed['samples'] if s[0] == grind]
        bounds = source['envelopes'][grind, a, b]
        assert row['full_support'] and row['completeness'] == 'COMPLETE' and not row['descriptive_only']
        assert row['present'] == members and not row['missing'] and not row['ambiguous_members']
        assert rationals(row['bounds_ratio']) == bounds and row['display_ratio'] == outward(bounds)
        assert row['ratio_refs'] == [ratios[s, a, b]['id'] for s in members]
    assert set(grinds) == set(source['grind_pairs']), 'grind keys'
    for (left, right, a, b), row in grinds.items():
        expected = source['grind_pairs'][left, right, a, b]
        assert row['full_support'] and not row['ambiguous']
        assert row['difference_orientation'] == 'first_minus_second'
        assert row['sign'] == expected['sign'] and row['classification'] == expected['classification']
        assert rationals(row['marginal_envelope_difference']) == expected['marginal']
        assert row['marginal_display'] == outward(expected['marginal'])
        expected_class = ('STRICTLY_SEPARATED' if sign(expected['marginal'])
                          else 'OVERLAPPING_OR_CONTACTING')
        assert row['marginal_envelope_classification'] == expected_class
        keys = [(i, j, a, b) for i in fixed['samples'] if i[0] == left
                for j in fixed['samples'] if j[0] == right]
        assert len(keys) == 9 and row['sample_contrast_refs'] == [contrasts[k]['id'] for k in keys]
        assert row['sample_sign_counts'] == dict(Counter(str(source['contrasts'][k]['sign']) for k in keys))
    result = json.loads((root/BUNDLE/'RESULT.json').read_text())
    assert result['physical_validation'] == 'NOT_ESTABLISHED'
    assert result['classification'] == fixed['classification']
    assert result['actual_base'] == fixed['actual_base']
    assert result['read_only_ewp_main'] == fixed['ewp_main']
    assert result['input_hashes'] == fixed['inherited_input_hashes']
    assert result['plan_sha256'] == fixed['plan_sha256']
    assert result['calculation_contract_sha256'] == sha256((root/BUNDLE/'calculation_contract.json').read_bytes()).hexdigest()
    assert result['marginal_replay']['count'] == 72 and result['marginal_replay']['status'] == 'EXACT_MATCH'
    assert rationals(result['calibration']['tau_pt']) == source['calibration']['tau']
    assert rationals(result['calibration']['beta_kg_m3_per_pt']) == source['calibration']['beta_bounds']
    assert result['counts_are_independent_replications'] is False
    for name, count in fixed['counts'].items():
        stats = result['support_summary'][name]
        assert stats['total'] == stats['full_support'] == count and stats['ambiguous'] == 0
    def disposition(rows):
        return ('EXCLUDED_BY_SAMPLE_RATIO_CONTRAST' if any(r['sign'] for r in rows)
                else 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS')
    primary = [row for (i, j, a, b), row in source['contrasts'].items()
               if [a, b] == fixed['primary_interval_N']]
    assert result['A']['primary_disposition'] == disposition(primary)
    assert result['A']['overall_disposition'] == disposition(source['contrasts'].values())
    assert len(result['A']['intervals']) == 15
    for row in result['A']['intervals']:
        a, b = row['interval_N']
        pairs = [r for (i, j, fa, fb), r in source['contrasts'].items() if (fa, fb) == (a, b)]
        assert row['disposition'] == disposition(pairs)
        assert row['comparisons']['total'] == row['comparisons']['full_support'] == 66
        assert row['comparisons']['classification_counts'] == dict(Counter(p['classification'] for p in pairs))
        expected_ids = [contrasts[k]['id'] for k, r in source['contrasts'].items() if k[2:] == (a, b) and r['sign']]
        assert row['witness_ids'] == expected_ids
    strict = [r for r in contrasts.values() if r['sign']]
    assert result['A']['witnesses'] == strict and not result['A']['grind_witnesses']
    witness = json.loads((root/BUNDLE/'affine_witness.json').read_text())
    certificate_result = verify_witness(root, witness)
    assert result['B']['disposition'] == witness['disposition'] == 'FEASIBLE_AT_DECLARED_FORCE_LEVELS_BY_EXPLICIT_WITNESS'
    assert result['B']['failure'] is witness['failure'] is None
    for kind in ['parameters', 'levels', 'intersections', 'readings', 'certificates']:
        rows = saved_rows(root/BUNDLE/('affine_'+kind+'.csv'))
        assert rows == witness[kind], ('affine CSV/JSON disagreement', kind)
    return dict(tables={name: len(rows) for name, rows in tables.items()}, certificates=certificate_result)


def analytical_controls():
    # No retained preview is an oracle. These are mathematical, constructed cases.
    for tau in (Q(-3), Q(0), Q(11)):
        a, b = Q(2), Q(5)
        boxes = [[s*h-tau]*2 for s, h in [(Q(3), a), (Q(3), b), (Q(7), a), (Q(7), b)]]
        assert determinant(*boxes, [tau]*2)[0] == [0, 0]
    boxes = [[Q(2)]*2, [Q(6)]*2, [Q(3)]*2, [Q(7)]*2]
    c = determinant(*boxes, [Q(4), Q(5)])[0]
    assert c[0] > 0
    assert determinant(*boxes[2:], *boxes[:2], [Q(4), Q(5)])[0] == [-c[1], -c[0]]
    for d in [Q(-100), Q(13, 7)]:
        moved = [[x+d for x in box] for box in boxes]
        assert determinant(*moved, [Q(4)-d, Q(5)-d])[0] == c
    assert quotient([Q(-4), Q(-2)], [Q(2), Q(5)]) == [Q(-2), Q(-2, 5)]
    assert quotient([Q(-4), Q(2)], [Q(2), Q(5)]) == [Q(-2), Q(1)]
    assert classify([Q(0), Q(2)]) == 'NOT_EXCLUDED_BY_THIS_COMPARISON'
    assert parameter_range(Q(5), Q(5), [Q(4), Q(6)]) == [0, 1]
    assert parameter_range(Q(5), Q(5), [Q(6), Q(7)]) is None
    assert parameter_range(Q(8), Q(2), [Q(3), Q(5)]) == [Q(1, 2), Q(5, 6)]
    assert not encloses(merge([[Q(0), Q(1)], [Q(2), Q(3)]]), [Q(3, 2)]*2)


def serial(value):
    if isinstance(value, Q):
        return str(value)
    raise TypeError(type(value).__name__)


def summary(source, affine):
    strict = [{'first': i, 'second': j, 'force_from_N': a, 'force_to_N': b, **row}
              for (i, j, a, b), row in source['contrasts'].items() if row['sign']]
    return dict(status='INDEPENDENT_RECONSTRUCTION_COMPLETED', preserved_files=len(source['fixed']['preserved_file_hashes']),
                counts=dict(readings=len(source['readings']), ratios=len(source['ratios']),
                            contrasts=len(source['contrasts']), envelopes=len(source['envelopes']),
                            grind_pairs=len(source['grind_pairs'])),
                reading_statuses=dict(Counter(r['status'] for r in source['readings'].values())),
                tau=source['calibration']['tau'], beta=source['calibration']['beta_bounds'],
                strict_sample_contrasts=strict,
                strict_grind_comparisons=sum(bool(r['sign']) for r in source['grind_pairs'].values()),
                affine_levels=[dict(force_N=f, h=affine['levels'][f]) for f in source['fixed']['forces_N']],
                affine_certificate_count=len(affine['certificates']))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument('--reconstruct-only', action='store_true')
    args = parser.parse_args()
    analytical_controls()
    source = reconstruct(args.root)
    affine = construct_affine(source)
    result = summary(source, affine)
    if not args.reconstruct_only:
        result['candidate_verification'] = compare_outputs(args.root, source)
        result['status'] = 'INDEPENDENT_SCIENTIFIC_CHECK_PASS'
    print(json.dumps(result, default=serial, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()

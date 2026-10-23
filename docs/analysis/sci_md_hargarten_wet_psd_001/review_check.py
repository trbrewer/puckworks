#!/usr/bin/env python3
"""Independent retained-input checker; standard library only, no producer imports.

Log diameters use exact integer nth-root inequalities rather than the producer's
Decimal transcendental path.  The checker recomputes inputs before reading any
reported output.  It is an arithmetic/logic check, not source authentication.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'puckworks/data/hargarten2020/wet_psd_001'
RESULT = Path(__file__).with_name('RESULT.json')
EXCLUDED = 'UNIFORM_DILATION_EXCLUDED_BY_CDF_EXCESS'
NOT_EXCLUDED = 'UNIFORM_DILATION_NOT_EXCLUDED_BY_DECLARED_CONTRASTS'
UNRESOLVED = 'UNRESOLVED_SOURCE_OR_READING'


@lru_cache(None)
def decimal_power10_enclosure(exponent):
    """Enclose 10**exponent at 1e-6 exactly via integer powers, no floats/logs.

    If exponent=n/d, k=floor(10**6 * 10**(n/d)) is uniquely determined by
    k**d <= 10**(n+6*d) < (k+1)**d. Negative target powers use reciprocal
    multiplication. Binary search supplies both inequalities as a certificate.
    """
    exponent = F(exponent)
    n, d = exponent.numerator, exponent.denominator
    power = n + 6*d
    numerator, denominator = (10**power, 1) if power >= 0 else (1, 10**(-power))
    left, right = 0, 10**(max(0, (n+d-1)//d + 6) + 1)
    while left+1 < right:
        middle = (left+right)//2
        if middle**d*denominator <= numerator:
            left = middle
        else:
            right = middle
    assert left**d*denominator <= numerator < (left+1)**d*denominator
    upper = left if left**d*denominator == numerator else left+1
    return F(left, 10**6), F(upper, 10**6)


def diameter_box(row, panel):
    assert panel['x_scale'] == 'log10'
    assert panel['x_anchor_um'] == ['10', '1000']
    a, b = map(F, panel['x_anchors_px'])
    r, c = F(panel['reading_allowance_px']), F(panel['anchor_allowance_px'])
    x = F(row['x_px'])
    assert b-a > 2*c
    # Linear-fractional in each argument separately, denominator positive:
    # its extrema on this rectangular relaxation occur at corners.
    exponents = [1+2*(x+dx-(a+da))/(b+db-a-da)
                 for dx, da, db in product((-r, r), (-c, c), (-c, c))]
    return decimal_power10_enclosure(min(exponents))[0], decimal_power10_enclosure(max(exponents))[1]


def ordinate_box(row, panel, layer, nominal=False):
    if row.get(layer+'_status') != 'SUPPORTED':
        return None
    zero, one = map(F, panel['y_anchors_px'])
    r, c = F(panel['reading_allowance_px']), F(panel['anchor_allowance_px'])
    assert zero-one > 2*c and panel['y_scale'] == 'linear'
    if layer == 'G':
        bottom, top = F(row['y_px'])+r, F(row['y_px'])-r
    else:
        if not row['ci_top_px'] or not row['ci_bottom_px']:
            raise ValueError('supported P row lacks endpoints')
        top, bottom = F(row['ci_top_px'])-r, F(row['ci_bottom_px'])+r
        if F(row['ci_top_px']) > F(row['ci_bottom_px']):
            raise ValueError('inverted source interval')
    shifts = (F(0),) if nominal else (-c, c)
    values = [(zero+dz-y)/(zero+dz-one-do)
              for y, dz, do in product((top, bottom), shifts, shifts)]
    lo, hi = max(F(0), min(values)), min(F(1), max(values))
    if lo > hi:
        raise ValueError('interval excludes [0,1]')
    return lo, hi


def ordered_assignment(rows, panel, layer):
    """One actual monotone assignment at the panel's shared nominal calibration."""
    previous_x, value = None, F(0)
    witness = []
    for row in rows:
        x = F(row['x_px'])
        if previous_x is not None and x <= previous_x:
            return None
        previous_x = x
        bound = ordinate_box(row, panel, layer, nominal=True)
        if bound is None:
            continue
        value = max(value, bound[0])
        if value > bound[1]:
            return None
        witness.append((row['point_id'], value))
    return witness


def cutoff_bracket(points, diameter):
    left = [(p['F'][0], p['id']) for p in points if p['F'] and p['d'][1] <= diameter]
    right = [(p['F'][1], p['id']) for p in points if p['F'] and p['d'][0] >= diameter]
    if not left or not right:
        return None
    lo = max(v for v, _ in left)
    hi = min(v for v, _ in right)
    assert lo <= hi
    return {'bounds': (lo, hi),
            'lower_anchors': [i for v, i in left if v == lo],
            'upper_anchors': [i for v, i in right if v == hi]}


def quantile_bracket(points, q):
    below = [(p['d'][0], p['id']) for p in points if p['F'] and p['F'][1] < q]
    above = [(p['d'][1], p['id']) for p in points if p['F'] and p['F'][0] >= q]
    lo = max((v for v, _ in below), default=None)
    hi = min((v for v, _ in above), default=None)
    if lo is not None and hi is not None:
        assert 0 < lo <= hi
    return {'bounds': (lo, hi),
            'lower_anchors': [i for v, i in below if v == lo],
            'upper_anchors': [i for v, i in above if v == hi]}


def cdf_classification(bounds, consistent=True):
    if not consistent:
        return UNRESOLVED
    if any(b is not None and b[0] > 0 for b in bounds):
        return EXCLUDED
    return NOT_EXCLUDED if all(b is not None for b in bounds) else UNRESOLVED


def ratio_intersection(rows, count, consistent=True):
    if not consistent:
        return {'bounds': None, 'status': UNRESOLVED, 'supported': 0}
    active = [(i, b) for i, b in rows if b is not None]
    if not active:
        return {'bounds': None, 'status': UNRESOLVED, 'supported': 0}
    lo = max([F(1)]+[b[0] for _, b in active])
    hi = min(b[1] for _, b in active)
    if lo > hi:
        status = 'COMMON_SCALE_EXCLUDED_BY_QUANTILE_CONSTRAINTS'
    else:
        status = 'NONEMPTY_OUTER_CANDIDATE_RANGE' if len(active) == count else 'PARTIAL_OUTER_CANDIDATE_RANGE'
    return {'bounds': (lo, hi), 'status': status, 'supported': len(active),
            'lower_rows': ['lambda>=1'] if lo == 1 else [i for i, b in active if b[0] == lo],
            'upper_rows': [i for i, b in active if b[1] == hi]}


def reconstruct(data=DATA):
    contract = json.loads((data/'contract.json').read_text())
    rows = list(csv.DictReader((data/'coordinates.csv').open()))
    assert len({r['point_id'] for r in rows}) == len(rows)
    series = {s['id']: s for s in contract['series']}
    assert set(r['series_id'] for r in rows) == set(series)
    output = {k: {} for k in ('points', 'feasibility', 'cdf', 'contrasts', 'B', 'quantiles', 'ratios', 'intersections')}
    for layer in ('G', 'P'):
        for sid, info in series.items():
            panel = contract['panels'][info['panel']]
            sr = [r for r in rows if r['series_id'] == sid]
            try:
                witness = ordered_assignment(sr, panel, layer)
                points = [{'id': r['point_id'], 'd': diameter_box(r, panel), 'F': ordinate_box(r, panel, layer)} for r in sr]
            except (ValueError, AssertionError):
                witness, points = None, []
            output['feasibility'][layer, sid] = witness
            output['points'][layer, sid] = points
            if info['fraction'] == 'non_sieved':
                for d in contract['cutoffs_um']:
                    output['cdf'][layer, sid, d] = cutoff_bracket(points, F(d)) if witness is not None else None
            else:
                for q in contract['quantiles']:
                    output['quantiles'][layer, sid, q] = quantile_bracket(points, F(q)) if witness is not None else None
        for d in contract['cutoffs_um']:
            for lhs, rhs in [('wet25', 'dry'), ('wet90', 'dry'), ('wet90', 'wet25')]:
                a = output['cdf'][layer, 'non_sieved_'+lhs, d]
                b = output['cdf'][layer, 'non_sieved_'+rhs, d]
                output['contrasts'][layer, lhs, rhs, d] = ((a['bounds'][0]-b['bounds'][1], a['bounds'][1]-b['bounds'][0]) if a and b else None)
        for condition in ('wet25', 'wet90'):
            bnds = [output['contrasts'][layer, condition, 'dry', d] for d in contract['cutoffs_um']]
            consistent = all(output['feasibility'][layer, sid] is not None for sid in ('non_sieved_dry', 'non_sieved_'+condition))
            positive = [d for d, b in zip(contract['cutoffs_um'], bnds) if b is not None and b[0] > 0]
            output['B'][layer, condition] = {'status': cdf_classification(bnds, consistent), 'B': max([F(0)]+[b[0] for b in bnds if b is not None]), 'witness_cutoffs': positive}
        for roast, fractions in [('medium', 'SML'), ('light', 'SM')]:
            all_pairs = []
            all_consistent = True
            for fraction in fractions:
                pairs = []
                dry, wet = roast+'_'+fraction+'_dry', roast+'_'+fraction+'_wet90'
                consistent = all(output['feasibility'][layer, sid] is not None for sid in (dry, wet))
                all_consistent &= consistent
                for q in contract['quantiles']:
                    a, b = output['quantiles'][layer, wet, q], output['quantiles'][layer, dry, q]
                    bounds = None
                    if a and b and all(v is not None and v > 0 for v in a['bounds']+b['bounds']):
                        bounds = (a['bounds'][0]/b['bounds'][1], a['bounds'][1]/b['bounds'][0])
                    key = (layer, roast, fraction, q)
                    output['ratios'][key] = bounds
                    pairs.append((key, bounds))
                output['intersections'][layer, roast, fraction] = ratio_intersection(pairs, len(contract['quantiles']), consistent)
                all_pairs.extend(pairs)
            output['intersections'][layer, roast, 'all'] = ratio_intersection(all_pairs, len(fractions)*len(contract['quantiles']), all_consistent)
    return output


def controls():
    assert cdf_classification([(F(0), F(1))]) == NOT_EXCLUDED
    assert cdf_classification([(F(-1), F(1))]) == NOT_EXCLUDED
    assert cdf_classification([(F(1, 1000), F(1)), None]) == EXCLUDED
    assert cdf_classification([(F(-1), F(1)), None]) == UNRESOLVED
    assert cdf_classification([(F(1, 1000), F(1))], False) == UNRESOLVED
    assert ratio_intersection([('a', (F(1), F(2))), ('b', (F(2), F(3)))], 2)['status'] == 'NONEMPTY_OUTER_CANDIDATE_RANGE'
    assert ratio_intersection([('a', (F(1, 2), F(9, 10))), ('b', None)], 2)['status'] == 'COMMON_SCALE_EXCLUDED_BY_QUANTILE_CONSTRAINTS'
    assert ratio_intersection([('a', (F(1), F(2))), ('b', None)], 2)['status'] == 'PARTIAL_OUTER_CANDIDATE_RANGE'
    assert decimal_power10_enclosure(F(2)) == (F(100), F(100))
    points = [{'id': 'a', 'd': (F(1), F(1)), 'F': (F(1, 2), F(1, 2))},
              {'id': 'b', 'd': (F(2), F(2)), 'F': (F(1, 2), F(1, 2))},
              {'id': 'c', 'd': (F(3), F(3)), 'F': (F(1), F(1))}]
    assert quantile_bracket(points, F(1, 2))['bounds'] == (None, F(1))
    assert quantile_bracket(points, F(3, 4))['bounds'] == (F(2), F(3))
    panel = {'y_anchors_px': [100, 0], 'reading_allowance_px': '3',
             'anchor_allowance_px': '1', 'y_scale': 'linear'}
    raw = [{'point_id': 'a', 'x_px': '10', 'y_px': '10', 'G_status': 'SUPPORTED'},
           {'point_id': 'b', 'x_px': '20', 'y_px': '90', 'G_status': 'SUPPORTED'}]
    assert ordered_assignment(raw, panel, 'G') is None
    raw[1]['y_px'] = '10'
    assert ordered_assignment(raw, panel, 'G') == [('a', F(87, 100)), ('b', F(87, 100))]


def as_pair(value):
    return None if value is None else tuple(None if x is None else F(x) for x in value)


def compare_report(expected, actual):
    """Compare every table and decisive certificate after raw reconstruction."""
    for name in ('cdf_readings', 'contrasts', 'quantile_diameters',
                 'multiplier_intervals', 'intersections', 'witnesses'):
        assert len({r['id'] for r in actual[name]}) == len(actual[name]), name
    assert len({(r['layer'], r['point_id']) for r in actual['marker_bounds']}) == len(actual['marker_bounds'])
    assert len({(r['layer'], r['series_id']) for r in actual['feasibility']}) == len(actual['feasibility'])
    point_map = {(layer, p['id']): p for (layer, _), pp in expected['points'].items() for p in pp}
    assert len(actual['marker_bounds']) == len(point_map)
    for row in actual['marker_bounds']:
        p = point_map[row['layer'], row['point_id']]
        assert as_pair(row['diameter_um']) == p['d'], ('diameter', row['point_id'])
        assert as_pair(row['bounds']) == p['F'], ('CDF marker', row['point_id'])
    assert len(actual['feasibility']) == len(expected['feasibility'])
    for row in actual['feasibility']:
        w = expected['feasibility'][row['layer'], row['series_id']]
        assert row['admissible'] == (w is not None)
        assert [(p['point_id'], F(p['F'])) for p in row['witness']] == w
    assert len(actual['cdf_readings']) == len(expected['cdf'])
    for row in actual['cdf_readings']:
        e = expected['cdf'][row['layer'], row['series_id'], row['cutoff_um']]
        assert as_pair(row['bounds']) == (e['bounds'] if e else None)
        if e:
            assert row['lower_anchor'] in e['lower_anchors']
            assert row['upper_anchor'] in e['upper_anchors']
    assert len(actual['contrasts']) == len(expected['contrasts'])
    for row in actual['contrasts']:
        lhs, rhs = row['contrast'].split('-')
        e = expected['contrasts'][row['layer'], lhs, rhs, row['cutoff_um']]
        assert as_pair(row['bounds']) == e, row['id']
        sign = 'UNRESOLVED' if e is None else 'POSITIVE' if e[0] > 0 else 'NEGATIVE' if e[1] < 0 else 'ZERO_CONTAINING'
        assert row['sign'] == sign
        if e:
            display = as_pair(row['display_pp'])
            assert display[0] <= 100*e[0] <= 100*e[1] <= display[1]
    assert len(actual['conditions']) == len(expected['B'])
    decisive = set()
    for row in actual['conditions']:
        layer, condition = row['layer'], row['condition']
        e = expected['B'][layer, condition]
        assert row['outcome'] == e['status'] and F(row['B']) == e['B']
        ids = {f'{layer}:{condition}-dry:{d}' for d in e['witness_cutoffs']}
        assert set(row['positive_witness_ids']) == ids
        decisive |= ids
        b40 = expected['contrasts'][layer, condition, 'dry', 40]
        assert row['primary']['outcome'] == cdf_classification([b40])
        assert F(row['B_pp_lower']) <= 100*e['B']
        if ids:
            assert F(row['B_pp_lower']) > 0
    actual_witnesses = {r['id']: r for r in actual['witnesses'] if r['type'] == 'CDF_EXCESS'}
    assert set(actual_witnesses) == decisive
    for wid, row in actual_witnesses.items():
        layer, contrast, cutoff = wid.split(':')
        condition, _ = contrast.split('-')
        e = expected['contrasts'][layer, condition, 'dry', int(cutoff)]
        assert e is not None and e[0] > 0 and F(row['certified_excess']) == e[0]
        wet, dry = row['source_operands']
        expected_wet = expected['cdf'][layer, 'non_sieved_'+condition, int(cutoff)]
        expected_dry = expected['cdf'][layer, 'non_sieved_dry', int(cutoff)]
        assert as_pair(wet['bounds']) == expected_wet['bounds']
        assert as_pair(dry['bounds']) == expected_dry['bounds']
        assert F(row['certified_excess']) == expected_wet['bounds'][0]-expected_dry['bounds'][1]
        for operand, reconstructed in [(wet, expected_wet), (dry, expected_dry)]:
            assert operand['lower_anchor'] in reconstructed['lower_anchors']
            assert operand['upper_anchor'] in reconstructed['upper_anchors']
    assert len(actual['quantile_diameters']) == len(expected['quantiles'])
    for row in actual['quantile_diameters']:
        e = expected['quantiles'][row['layer'], row['series_id'], row['q']]
        assert as_pair(row['bounds_um']) == (e['bounds'] if e else (None, None)), row['id']
        if e:
            if e['lower_anchors']:
                assert row['lower_anchor'] in e['lower_anchors']
            if e['upper_anchors']:
                assert row['upper_anchor'] in e['upper_anchors']
    assert len(actual['multiplier_intervals']) == len(expected['ratios'])
    for row in actual['multiplier_intervals']:
        e = expected['ratios'][row['layer'], row['roast'], row['fraction'], row['q']]
        assert as_pair(row['bounds']) == e, row['id']
    assert len(actual['intersections']) == len(expected['intersections'])
    empty = set()
    for row in actual['intersections']:
        key = row['layer'], row['roast'], row['fraction'] or 'all'
        e = expected['intersections'][key]
        assert as_pair(row['bounds']) == e['bounds'] and row['outcome'] == e['status']
        assert row['supported'] == e['supported']
        if e['bounds']:
            def rid(x):
                return x if isinstance(x, str) else f'{x[0]}:{x[1]}_{x[2]}:q{x[3]}'
            assert row['lower_operand'] in [rid(x) for x in e['lower_rows']]
            assert row['upper_operand'] in [rid(x) for x in e['upper_rows']]
        if e['status'] == 'COMMON_SCALE_EXCLUDED_BY_QUANTILE_CONSTRAINTS':
            empty.add(row['id'])
            assert F(row['separation']) == e['bounds'][0]-e['bounds'][1] > 0
    assert {r['id'] for r in actual['witnesses'] if r['type'] == 'EMPTY_SCALE_INTERSECTION'} == empty
    return {'status': 'PASS', 'marker_rows': len(point_map), 'cdf_readings': len(expected['cdf']),
            'contrasts': len(expected['contrasts']), 'quantile_diameters': len(expected['quantiles']),
            'ratios': len(expected['ratios']), 'intersections': len(expected['intersections']),
            'independently_verified_positive_witnesses': len(decisive),
            'independently_verified_empty_intersections': len(empty)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=DATA)
    parser.add_argument('--result', type=Path, default=RESULT)
    args = parser.parse_args()
    controls()
    expected = reconstruct(args.data)
    # Outputs are opened only after independent input reconstruction.
    actual = json.loads(args.result.read_text())
    print(json.dumps(compare_report(expected, actual), indent=2))


if __name__ == '__main__':
    main()

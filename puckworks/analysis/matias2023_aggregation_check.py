"""Independent exact primal/lower-bound reader; never imports the hull producer.

The original CSV defines intervals. A feasible witness and an equal valid lower
bound prove optimality. Optional SciPy LP agreement is numerical QA only.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'puckworks/data/matias2023'


def require(condition, message):
    if not condition:
        raise ValueError('CHECK_FAILURE: '+message)


def check_exact(x, intervals, result):
    """Check serialized rational witness/certificates against original constraints."""
    x = list(map(Q, x))
    bands = [(Q(l), Q(u)) for l, u in intervals]
    require(len(x) == len(bands), 'input dimensions')
    require(all(l <= u for l, u in bands), 'interval order')
    require(all(a < b for a, b in zip(x, x[1:])), 'coordinate order')
    if not x:
        require(result['epsilon'] is None, 'absent support has no numerical verdict')
        return {'status': 'SOURCE_SUPPORT_FAILURE', 'epsilon': None}
    e = Q(result['epsilon'])
    y = list(map(Q, result['predicted_log']))
    require(e >= 0 and len(y) == len(x), 'primal dimensions/nonnegativity')
    require(list(map(Q, result['x'])) == x, 'original coordinates')
    require(all(l-e <= yy <= u+e for yy, (l, u) in zip(y, bands)), 'expanded original intervals')
    slopes = [(y[i+1]-y[i])/(x[i+1]-x[i]) for i in range(len(x)-1)]
    require(all(s <= 0 for s in slopes), 'nonincrease')
    require(all(a <= b for a, b in zip(slopes, slopes[1:])), 'secant convexity')
    nearest = [min(u, max(l, yy)) for yy, (l, u) in zip(y, bands)]
    delta = [yy-n for yy, n in zip(y, nearest)]
    require(max(map(abs, delta)) == e, 'primal objective')
    require(list(map(Q, result['nearest_log'])) == nearest, 'nearest readings')
    require(list(map(Q, result['interval_distance'])) == delta, 'signed distances')
    require(Q(result['maximum_absolute_interval_distance']) == e, 'maximum distance')
    require(list(map(Q, result['monotonicity_slacks'])) == [a-b for a, b in zip(y, y[1:])], 'monotonicity slacks')
    require(list(map(Q, result['convexity_slacks'])) == [b-a for a, b in zip(slopes, slopes[1:])], 'convexity slacks')

    # Verify submitted provenance directly, with no hull construction/optimization.
    provenance = result['provenance']
    anchors = result['hull_anchors']
    require(len(provenance) == len(x), 'provenance dimensions')
    require(anchors == sorted(set(anchors)) and anchors[0] == 0 and anchors[-1] == len(x)-1,
            'ordered hull anchors/endpoints')
    v = [min(u for _, u in bands[:i+1]) for i in range(len(x))]
    h = []
    for i, p in enumerate(provenance):
        require(p['index'] == i and Q(p['x']) == x[i] and Q(p['upper']) == bands[i][1], 'provenance original coordinate/upper')
        require(Q(p['prefix_minimum']) == v[i], 'prefix minimum value')
        source = next(j for j in range(i+1) if bands[j][1] == v[i])
        require(p['prefix_source'] == source, 'earliest tied prefix source')
        require(p['is_hull_anchor'] == (i in anchors), 'anchor flag')
        a, b, pa, pb = (p[k] for k in ('a', 'b', 'p_a', 'p_b'))
        require(a in anchors and b in anchors and a <= i <= b, 'bracketing anchors')
        if a == b:
            require(a == i, 'anchor control')
            weights = Q(1), Q(0)
        else:
            require(anchors.index(b) == anchors.index(a)+1 and a < i < b, 'neighboring hull anchors')
            weights = (x[b]-x[i])/(x[b]-x[a]), (x[i]-x[a])/(x[b]-x[a])
        alpha, beta = weights
        require((Q(p['x_a']), Q(p['x_b'])) == (x[a], x[b]), 'hull-anchor coordinates')
        require((Q(p['alpha']), Q(p['beta'])) == weights, 'hull-coordinate weights')
        require(0 <= pa <= a and 0 <= pb <= b, 'prefix monotonicity implications')
        require(pa == provenance[a]['prefix_source'] and pb == provenance[b]['prefix_source'], 'anchor prefix sources')
        require(bands[pa][1] == v[a] and bands[pb][1] == v[b], 'original source upper bounds')
        hi = alpha*bands[pa][1]+beta*bands[pb][1]
        require(Q(p['h']) == hi and hi <= v[i] and y[i] == hi+e, 'interpolation/translation')
        h.append(hi)
    segment_slopes = [(v[b]-v[a])/(x[b]-x[a]) for a, b in zip(anchors, anchors[1:])]
    require(all(s <= 0 for s in segment_slopes) and all(a < b for a, b in zip(segment_slopes, segment_slopes[1:])),
            'convex nonincreasing hull/collinearity rule')
    require(list(map(Q, result['hull_segment_slopes'])) == segment_slopes, 'hull slopes')
    expected_controls = [i for i in range(len(x)) if (bands[i][0]-h[i])/2 == e]
    controls, lower_bounds, nonnegative = [], [], 0
    for cert in result['certificates']:
        if cert['kind'] == 'NONNEGATIVITY':
            require(Q(cert['bound']) == 0 and e == 0, 'nonnegativity certificate')
            lower_bounds.append(Q(0))
            nonnegative += 1
            continue
        require(cert['kind'] == 'HULL_PREFIX', 'known certificate kind')
        i = cert['index']
        require(0 <= i < len(x), 'control index')
        require(all(cert[k] == value for k, value in provenance[i].items()), 'certificate provenance')
        require(Q(cert['lower']) == bands[i][0], 'original lower bound')
        alpha, beta = Q(cert['alpha']), Q(cert['beta'])
        bound = (bands[i][0]-alpha*bands[cert['p_a']][1]-beta*bands[cert['p_b']][1])/2
        require(Q(cert['bound']) == bound == e, 'dual bound equals primal cost')
        lower_bounds.append(bound)
        controls.append(i)
    require(controls == expected_controls and nonnegative == int(e == 0), 'all tied controls retained')
    require(lower_bounds and max(lower_bounds) == e, 'certified lower bound equals primal')
    return {'status': 'PASS', 'epsilon': str(e), 'original_interval_checks': len(x),
            'nonincrease_checks': len(slopes), 'secant_convexity_checks': max(0, len(slopes)-1),
            'tied_certificates': len(lower_bounds)}


def numerical_lp(x, intervals):
    """Independent epigraph specification, with ALL y sign-unbounded."""
    from scipy.optimize import linprog
    n = len(x)
    if not n:
        return None
    x = list(map(float, x))
    matrix, rhs = [], []
    for i, (l, u) in enumerate(intervals):
        for sign, bound in [(1, u), (-1, -Q(l))]:
            row = [0.]*(n+1)
            row[i], row[-1] = sign, -1
            matrix.append(row)
            rhs.append(float(bound))
    for i in range(n-1):
        row = [0.]*(n+1)
        row[i], row[i+1] = -1, 1
        matrix.append(row)
        rhs.append(0.)
    for i in range(n-2):
        a, b = x[i+1]-x[i], x[i+2]-x[i+1]
        row = [0.]*(n+1)
        row[i], row[i+1], row[i+2] = -1/a, 1/a+1/b, -1/b
        matrix.append(row)
        rhs.append(0.)
    fit = linprog([0.]*n+[1.], A_ub=matrix, b_ub=rhs,
                  bounds=[(None, None)]*n+[(0, None)], method='highs')
    require(fit.success, 'NUMERICAL_CHECK_FAILURE: '+fit.message)
    return float(fit.fun)


def check_source(results_path, *, lp=False):
    packet = json.loads(results_path.read_text())
    with (DATA/'observations.csv').open(newline='') as stream:
        rows = list(csv.DictReader(stream))
    require([r['fraction_id'] for r in rows] == [f'F{i:02}' for i in range(1, 11)], 'ten IDs')
    require([Q(r['x']) for r in rows] == list(range(10)), 'ten original coordinates')
    require(packet['original_slot_count'] == 10 and packet['physical_extraction_count'] == 4, 'cohort')
    for name, value in packet['input_sha256'].items():
        require(sha256((DATA/name).read_bytes()).hexdigest() == value, 'source identity '+name)
    support = {'RECOVERED', 'COVERED_BUT_RECOVERED', 'CLIPPED_BUT_RECOVERED'}
    receipt = {}
    specs = [('N', 'z', 'z', ('center_status',)), ('G', 'G_lower', 'G_upper', ('center_status',)),
             ('P_outer', 'L_minus', 'U_plus', ('L_status', 'U_status')),
             ('P_inner', 'L_plus', 'U_minus', ('L_status', 'U_status'))]
    for layer, lo, hi, statuses in specs:
        original = [r for r in rows if all(r[k] in support for k in statuses)]
        intervals = [(Q(r[lo]), Q(r[hi])) for r in original]
        result = packet['layers'][layer]
        require(result['fraction_ids'] == [r['fraction_id'] for r in original], 'supported IDs')
        require(result['support_status'] == ('COMPLETE' if len(original) == 10 else 'SUBSET_LOWER_BOUND_ONLY'), 'coverage status')
        x = [Q(r['x']) for r in original]
        receipt[layer] = check_exact(x, intervals, result)
        e = Q(result['epsilon'])
        bound = result['mixture_discrepancy_lower_bound']
        require(Q(bound['epsilon_dex']) == e and bound['is_exact_mixture_optimum'] is False, 'mixture lower-bound label')
        with localcontext() as ctx:
            ctx.prec = 90
            value = (Decimal(10).ln()*Decimal(e.numerator)/Decimal(e.denominator)).exp()
            m = result['multiplicative']
            require(Decimal(m['M_lower']) <= value <= Decimal(m['M_upper']), 'transform high-precision agreement')
            require(Decimal(m['ratio_lower_lower']) <= 1/value <= Decimal(m['ratio_lower_upper']), 'reciprocal agreement')
        if lp:
            cost = numerical_lp(x, intervals)
            difference = abs(cost-float(e))
            require(difference < 1e-9, 'NUMERICAL_CHECK_FAILURE: LP agreement')
            receipt[layer]['numerical_lp'] = {'objective': cost, 'absolute_difference': difference,
                                             'tolerance_QA_only': 1e-9, 'y_bounds': 'UNBOUNDED_IN_SIGN'}
        wr = [r for r in packet['witness_residuals'] if r['layer'] == layer]
        require([r['fraction_id'] for r in wr] == [r['fraction_id'] for r in rows], 'ten witness slots')
        for j, r in enumerate(original):
            w = next(w for w in wr if w['fraction_id'] == r['fraction_id'])
            require(w['predicted_log'] == result['predicted_log'][j], 'witness row value')
            require(Q(w['center_residual_log']) == Q(w['predicted_log'])-Q(r['z']), 'center residual')
            require(w['signed_interval_distance_log'] == result['interval_distance'][j], 'interval residual')
        local = [r for r in packet['local_curvatures'] if r['layer'] == layer]
        require(len(local) == 8, 'eight original triples')
        for i, r in enumerate(local):
            lower = Q(rows[i][lo])-2*Q(rows[i+1][hi])+Q(rows[i+2][lo])
            upper = Q(rows[i][hi])-2*Q(rows[i+1][lo])+Q(rows[i+2][hi])
            require(Q(r['lower']) == lower and Q(r['upper']) == upper and r['local_exclusion'] == (upper < 0), 'local curvature')
        receipt[layer]['local_exclusion_count'] = sum(r['local_exclusion'] for r in local)
    files = [results_path, Path(__file__), ROOT/'puckworks/analysis/matias2023_caffeine_aggregation.py',
             ROOT/'puckworks/analysis/matias2023_caffeine_fraction_shape.py',
             ROOT/'tests/test_matias_caffeine_aggregation.py', DATA/'observations.csv', DATA/'figure_geometry.json']
    return {'status': 'PASS', 'review_kind': 'SAME_SESSION_INDEPENDENT_METHOD_NOT_HUMAN_OR_EXTERNAL_AUDIT',
            'method': 'original-constraint rational primal feasibility plus equal rational dual lower bound; no hull producer import',
            'layers': receipt, 'sha256': {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name:
                                        sha256(p.read_bytes()).hexdigest() for p in files}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lp', action='store_true')
    args = parser.parse_args()
    receipt = check_source(args.results, lp=args.lp)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'])


if __name__ == '__main__':
    main()

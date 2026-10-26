"""Independent exact certificate verifier; optional secondary log-LP comparison.

Uses only the accepted source loader, not the new producer's layer constructor,
optimizer, cycle enumeration or path constructor. A lower-bound cycle and a
feasible witness prove the optimum without independently solving it. Four-cell
maxima and all expected keys are independently reconstructed.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
import math
from pathlib import Path

from .khamitova2020_tamping_chemistry import load_observations

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT/'docs/analysis/sci_md_khamitova_common_scaling_001'
PREVIOUS = 'docs/analysis/sci_md_khamitova_tamping_chemistry_001'
FORCES = (10, 15, 20, 30)
SPECIES = ('total CQA', 'caffeine', 'trigonelline', 'nicotinic acid')
LAYERS = ('N', 'D', 'S_outer')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_index(records, key, expected, label):
    keys = [key(r) for r in records]
    require(len(keys) == len(set(keys)), f'Duplicate {label}')
    require(set(keys) == set(expected), f'Missing/unexpected {label}')
    return dict(zip(keys, records))


def bounds_from_source(row, layer):
    """Reconstruct the observation contract without the producer's helper."""
    def numeric(field):
        v = row.get(field)
        if v is None or isinstance(v, bool):
            return None
        try:
            return F(str(v))
        except (ValueError, ZeroDivisionError):
            return None
    def width(field):
        p = row.get(field)
        return F(1, 2*10**p) if type(p) is int and p >= 0 else None
    x, r = numeric('amount'), numeric('rsd')
    h, q = width('amount_decimal_places'), width('rsd_decimal_places')
    why = []
    if row.get('mean_support') != 'SUPPORTED' or x is None or x <= 0:
        why.append('mean_support/strictly_positive_amount')
    if layer in ('D', 'S_outer'):
        if row.get('amount_rounding_support') != 'SUPPORTED' or h is None or h <= 0:
            why.append('amount_rounding_support/nonnegative_integer_decimal_places')
        elif x is not None and x <= h:
            why.append('amount_minus_half_place_not_positive')
    if layer == 'S_outer':
        if row.get('rsd_support') != 'SUPPORTED' or r is None or r < 0:
            why.append('rsd_support/nonnegative_rsd')
        if row.get('rsd_rounding_support') != 'SUPPORTED' or q is None or q <= 0:
            why.append('rsd_rounding_support/nonnegative_integer_decimal_places')
        elif r is not None and r+q >= 100:
            why.append('rsd_plus_half_place_not_below_100')
    if why:
        return None, why
    lower, upper = x, x
    if layer != 'N':
        lower, upper = x-h, x+h
    if layer == 'S_outer':
        lower *= (100-r-q)/100
        upper *= (100+r+q)/100
    require(0 < lower <= upper, 'Reconstructed interval invalid')
    return (lower, upper), []


def root_data(cost):
    r, k = F(cost['radicand']), cost['degree']
    require(type(k) is int and k > 0 and r >= 1, 'Invalid objective root')
    return r, k


def root_order(a, b):
    x, y = a[0]**b[1], b[0]**a[1]
    return (x > y)-(x < y)


def power_value(value, root):
    """The positive monomial raised to k is rational, even for negative e."""
    c, e = F(value['coefficient']), value['exponent']
    require(c > 0 and type(e) is int, 'Invalid positive factor monomial')
    return c**root[1]*root[0]**e


def verify_brackets(cost):
    r, k = root_data(cost)
    for name, target in [('M_bracket', r), ('reciprocal_bracket', 1/r)]:
        endpoints = cost[name]
        require(len(endpoints) == 2, 'Bracket cardinality')
        lo, hi = map(F, endpoints)
        require(0 <= lo <= hi and hi-lo <= F(1, 10**12), 'Bracket precision/order')
        require(lo**k <= target <= hi**k, 'Uncertified decimal bracket')
    require(cost['epsilon_exact'] == f'log10({r})/{k}', 'Exact epsilon expression')
    # Recompute the declared display rounding; no numerical tolerance enters
    # these checks or the exact feasibility/compatibility verdict.
    with localcontext() as ctx:
        ctx.prec = 60
        epsilon = (Decimal(r.numerator).log10()-Decimal(r.denominator).log10())/k
        require(cost['epsilon_dex_approx'] == f'{epsilon:.12f}',
                'Incorrect approximate epsilon display')


def verify_cycle(cert, root, bounds, t=None, p=None, required_length=None):
    r, k = root
    if cert['kind'] == 'OBJECTIVE_FLOOR':
        require(r == 1 and cert == {'kind': 'OBJECTIVE_FLOOR', 'M': '1'}, 'Invalid floor certificate')
        return
    require(cert['kind'] == 'DIRECTED_SIMPLE_CYCLE' and r > 1, 'Invalid nonfloor certificate')
    nodes, edges = cert['nodes'], cert['edges']
    require(len(nodes) == len(set(nodes)) and len(nodes) >= 2 and len(nodes) % 2 == 0,
            'Not a directed simple bipartite cycle')
    require(len(edges) == len(nodes) == cert['k'], 'Cycle length mismatch')
    if required_length is not None:
        require(len(nodes) == required_length, 'Four-cell certificate is not length four')
    ratio = F(1)
    for u, v, edge in zip(nodes, nodes[1:]+nodes[:1], edges):
        require(edge['from'] == u and edge['to'] == v, 'Tampered cycle direction')
        require(u[:2] != v[:2] and {u[:2], v[:2]} == {'F:', 'A:'}, 'Not bipartite')
        f = int((u if u.startswith('F:') else v)[2:])
        s = (v if v.startswith('A:') else u)[2:]
        require((f, s) in bounds, 'Cycle references omitted/missing cell')
        require(edge['cell_key'] == [t, p, f, s], 'Cycle cell-key mismatch')
        lo, hi = bounds[f, s]
        expected_bound = 'L' if u.startswith('F:') else 'U'
        require(edge['bound'] == expected_bound, 'Reversed lower/upper edge')
        ratio = ratio*lo if expected_bound == 'L' else ratio/hi
    require(F(cert['R']) == ratio, 'Cycle product mismatch')
    require(ratio**k == r**len(nodes), 'Cycle/root identity mismatch')


def four_cell_root(bounds, forces, species):
    """Enumerate rectangles directly, independently of graph cycles."""
    maximum = F(1)
    for f, g in combinations(forces, 2):
        for s, z in combinations(species, 2):
            maximum = max(maximum,
                          bounds[f, s][0]*bounds[g, z][0]/(bounds[f, z][1]*bounds[g, s][1]),
                          bounds[f, z][0]*bounds[g, s][0]/(bounds[f, s][1]*bounds[g, z][1]))
    return maximum, 4


def verify_witness(m, bounds, forces, species):
    root = root_data(m['cost'])
    g = m['force_factors']
    a = m['analyte_amplitudes_mg_per_reference_40ml']
    require(set(g) == set(map(str, forces)) and set(a) == set(species), 'Incomplete factor coverage')
    gp = {f: power_value(g[str(f)], root) for f in forces}
    ap = {s: power_value(a[s], root) for s in species}
    require(gp[forces[0]] == 1, 'Gauge not normalized')
    cells = unique_index(m['cells'], lambda c: tuple(c['key'][2:]), bounds, 'witness cell')
    for (f, s), (lo, hi) in bounds.items():
        predicted = gp[f]*ap[s]
        require(power_value(cells[f, s]['prediction'], root) == predicted, 'Prediction/factor mismatch')
        require(lo**root[1]/root[0] <= predicted <= hi**root[1]*root[0], 'Expanded interval violation')
    return len(bounds)


def log_lp(bounds, forces, species):
    import numpy as np
    from scipy.optimize import linprog
    n = len(forces)+len(species)+1
    rows, rhs = [], []
    for i, f in enumerate(forces):
        for j, s in enumerate(species):
            lo, hi = bounds[f, s]
            upper = np.zeros(n)
            upper[i], upper[len(forces)+j], upper[-1] = 1, 1, -1
            lower = -upper.copy()
            lower[-1] = -1
            rows.extend([upper, lower])
            rhs.extend([math.log10(float(hi)), -math.log10(float(lo))])
    objective = np.zeros(n)
    objective[-1] = 1
    fit = linprog(objective, A_ub=rows, b_ub=rhs,
                  bounds=[(0, 0)]+[(None, None)]*(n-2)+[(0, None)], method='highs')
    require(fit.success, 'Secondary LP failed: '+fit.message)
    return float(fit.fun)


def source_index(observations):
    return unique_index(observations,
                        lambda r: (r['temperature_C'], r['pressure_bar'], r['tamp_force_kgf'], r['analyte']),
                        product((88, 93, 98), (7, 9, 11), FORCES, SPECIES), 'source observation')


def check(report, lp=False, observations=None):
    expected_hashes = json.loads((BUNDLE/'input_sha256.json').read_text())
    require(expected_hashes[PREVIOUS+'/artifact_sha256.json'] ==
            'd6fae3f452c319dadadff8dbab34f9b4eb0fec9e751146f6ff0b102f893b4278', 'Preservation authority')
    require(report['input_sha256'] == expected_hashes, 'Input inventory mismatch')
    for path, expected in expected_hashes.items():
        require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, 'Changed input: '+path)
    require(report['authenticated_pdf_sha256'] ==
            json.loads((ROOT/PREVIOUS/'source_metadata.json').read_text())['pdf']['sha256'], 'PDF identity')
    require(report['observation_reference'] == PREVIOUS+'/observations.csv', 'Observation reference')
    loaded = load_observations() if observations is None else observations
    sources = source_index(loaded)
    if observations is None:
        with (ROOT/PREVIOUS/'observations.csv').open(newline='') as stream:
            reference = list(csv.DictReader(stream))
        require(len(reference) == 144, 'Regression reference cardinality')
        for actual, saved in zip(loaded, reference):
            for field, value in saved.items():
                if field in ('amount', 'concentration', 'rsd'):
                    require(actual[field] == F(value), 'Regression source value: '+field)
                else:
                    require(str(actual[field]) == value, 'Regression source qualification/key: '+field)
        require({r['amount_decimal_places'] for r in loaded} == {2}, 'Expected amount half-place .005')
        require({r['rsd_decimal_places'] for r in loaded} == {1}, 'Expected RSD half-place .05')
    expected_matrices = set(product((88, 93, 98), (7, 9, 11), LAYERS, (None, *SPECIES)))
    matrices = unique_index(report['matrices'],
                            lambda m: (m['temperature_C'], m['pressure_bar'], m['layer'], m['omitted_analyte']),
                            expected_matrices, 'matrix')
    interval_checks = primary_checks = supported = 0
    lp_rows, unsupported = [], []
    for (t, p, layer, omitted), m in matrices.items():
        species = tuple(s for s in SPECIES if s != omitted)
        require(m['forces_kgf'] == list(FORCES) and m['analytes'] == list(species), 'Matrix axes')
        cells = unique_index(m['cells'], lambda c: tuple(c['key']),
                             [(t, p, f, s) for f, s in product(FORCES, species)], 'matrix constraint')
        bounds = {}
        for k, cell in cells.items():
            src = sources[k]
            box, why = bounds_from_source(src, layer)
            require(cell['status'] == ('SUPPORTED' if box else 'UNSUPPORTED'), 'Cell support mismatch')
            require(cell['unsupported_reasons'] == why, 'Unsupported reasons mismatch')
            require(cell['qualification'] == src['qualification'], 'Qualification not preserved')
            require(cell['source'] == {'dataset': 'khamitova2020/tamping', 'table': src['table'],
                    'csv_file': src['csv_file'], 'csv_row_1based': src['csv_row_1based']}, 'Cell provenance')
            require((cell['L'], cell['U']) == ((str(box[0]), str(box[1])) if box else (None, None)),
                    'Stored interval differs from independently reconstructed interval')
            if box:
                bounds[k[2:]] = box
        if len(bounds) != len(cells):
            require(m['status'] == 'UNSUPPORTED' and 'cost' not in m, 'Incomplete matrix claimed complete')
            unsupported.append([t, p, layer, omitted])
            continue
        require(m['status'] == 'SUPPORTED', 'Supported matrix missing certificate')
        supported += 1
        root = root_data(m['cost'])
        verify_brackets(m['cost'])
        verify_cycle(m['certificate'], root, bounds, t, p)
        interval_checks += verify_witness(m, bounds, FORCES, species)
        primary_checks += len(bounds) if omitted is None else 0
        four = root_data(m['four_cell_lower_bound'])
        verify_brackets(m['four_cell_lower_bound'])
        verify_cycle(m['four_cell_certificate'], four, bounds, t, p, required_length=4)
        require(root_order(four, four_cell_root(bounds, FORCES, species)) == 0, 'Not the strongest four-cell bound')
        relation = root_order(root, four)
        require(relation >= 0, 'Negative exact gap')
        require(m['longer_cycle_strictly_improves'] == (relation > 0), 'Exact gap flag')
        require(m['gap_exact_relation'] == ('POSITIVE' if relation else 'ZERO'), 'Exact gap relation')
        # Independent Decimal evaluation verifies only display formatting. The
        # positive/zero gap verdict above was already established rationally.
        with localcontext() as ctx:
            ctx.prec = 60
            def displayed_root(pair):
                r, k = pair
                return ((Decimal(r.numerator).ln()-Decimal(r.denominator).ln())/k).exp()
            expected_gap = displayed_root(root)-displayed_root(four)
            require(m['gap_M_minus_M4_approx'] == f'{expected_gap:.12f}', 'Approximate gap display')
        if lp:
            epsilon = log_lp(bounds, FORCES, species)
            delta = abs(epsilon-math.log10(float(root[0]))/root[1])
            require(delta <= 1e-9, 'LP disagreement beyond 1e-9 dex')
            lp_rows.append({'matrix_key': [t, p, layer, omitted], 'epsilon_lp': epsilon,
                            'absolute_difference_dex': delta})
    # Independent expected ratio keys and interval quotient diagnostics.
    ratio_keys = set(product((88, 93, 98), (7, 9, 11), LAYERS, combinations(SPECIES, 2), FORCES))
    ratios = unique_index(report['pairwise_analyte_ratios'], lambda v: (
        v['temperature_C'], v['pressure_bar'], v['layer'],
        (v['numerator_analyte'], v['denominator_analyte']), v['force_kgf']), ratio_keys, 'pairwise ratio')
    for (t, p, layer, (s, z), f), row in ratios.items():
        a, _ = bounds_from_source(sources[t, p, f, s], layer)
        b, _ = bounds_from_source(sources[t, p, f, z], layer)
        require(row['status'] == ('SUPPORTED' if a and b else 'UNSUPPORTED'), 'Ratio support')
        require((row['ratio_L'], row['ratio_U']) ==
                ((str(a[0]/b[1]), str(a[1]/b[0])) if a and b else (None, None)), 'Ratio bounds')
    # Layer nesting and objective ordering, and every symmetric omission.
    for source in loaded:
        boxes = [bounds_from_source(source, layer)[0] for layer in LAYERS]
        for inner, outer in zip(boxes, boxes[1:]):
            if inner and outer:
                require(outer[0] <= inner[0] <= inner[1] <= outer[1], 'Layer nesting')
    for t, p in product((88, 93, 98), (7, 9, 11)):
        for omitted in (None, *SPECIES):
            triplet = [matrices[t, p, layer, omitted] for layer in LAYERS]
            for narrow, wide in zip(triplet, triplet[1:]):
                if narrow['status'] == wide['status'] == 'SUPPORTED':
                    require(root_order(root_data(wide['cost']), root_data(narrow['cost'])) <= 0, 'Layer cost ordering')
        for layer, omitted in product(LAYERS, SPECIES):
            full, reduced = matrices[t, p, layer, None], matrices[t, p, layer, omitted]
            if full['status'] == reduced['status'] == 'SUPPORTED':
                require(root_order(root_data(reduced['cost']), root_data(full['cost'])) <= 0, 'Omission worsens cost')
    complete = not unsupported
    require(report['support_complete'] == complete, 'Support completeness flag')
    receipt = {'status': 'COMPLETE_EXACT_OPTIMA_VERIFIED' if complete else 'INCOMPLETE_SUPPORT',
               'requested_matrices': 135, 'supported_matrices': supported, 'unsupported_matrices': unsupported,
               'primary_interval_checks': primary_checks, 'diagnostic_interval_checks': interval_checks-primary_checks,
               'interval_checks': interval_checks, 'one_sided_inequalities': 2*interval_checks,
               'input_and_predecessor_hashes_verified': len(expected_hashes),
               'proof': 'Controlling directed cycle (or objective floor) and complete positive feasible witness',
               'PHYSICAL_VALIDATION': 'NOT_ESTABLISHED'}
    if lp:
        import scipy
        receipt['secondary_lp'] = {'status': 'AGREES' if complete else 'PARTIAL_SUPPORTED_ONLY',
                'scipy_version': scipy.__version__, 'tolerance_dex': 1e-9, 'matrices': lp_rows,
                'maximum_absolute_difference_dex': max((r['absolute_difference_dex'] for r in lp_rows), default=None)}
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--lp', action='store_true')
    args = parser.parse_args()
    report = json.loads(args.results.read_text())
    receipt = check(report, args.lp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'], receipt['supported_matrices'], 'matrices;', receipt['interval_checks'], 'intervals')


if __name__ == '__main__':
    main()

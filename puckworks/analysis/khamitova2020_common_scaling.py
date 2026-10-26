"""Exact, source-specific common concentration representation; research only.

All feasibility and ordering use rational arithmetic. Decimal logs are displays.
The dimensionless graph divides native amounts by 1 mg/reference 40 mL.
No production registry entry, inference, kinetic model or physical validation.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

from .khamitova2020_tamping_chemistry import (
    ANALYTES, FORCES, PRESSURES, TEMPERATURES, load_observations,
)

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'docs/analysis/sci_md_khamitova_common_scaling_001'
PREDECESSOR = 'docs/analysis/sci_md_khamitova_tamping_chemistry_001'
LAYERS = ('N', 'D', 'S_outer')
BASE = '43a0d0cc70a556de6892772b735952675a04666d'
MANIFEST_SHA = 'd6fae3f452c319dadadff8dbab34f9b4eb0fec9e751146f6ff0b102f893b4278'


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False)+'\n')


def verify_inputs():
    identities = json.loads((BUNDLE/'input_sha256.json').read_text())
    assert identities[PREDECESSOR+'/artifact_sha256.json'] == MANIFEST_SHA
    for path, expected in identities.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != expected:
            raise ValueError(f'Input identity mismatch: {path}')
    return identities


def key(row):
    return [row['temperature_C'], row['pressure_bar'], row['tamp_force_kgf'], row['analyte']]


def index_observations(rows):
    indexed = {}
    for row in rows:
        k = tuple(key(row))
        if k in indexed:
            raise ValueError(f'Duplicate source key: {k}')
        indexed[k] = row
    if set(indexed) != set(product(TEMPERATURES, PRESSURES, FORCES, ANALYTES)):
        raise ValueError('Missing or unexpected source keys; all 144 required')
    return indexed


def rational(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        return Q(str(value))
    except (ValueError, ZeroDivisionError):
        return None


def half_place(places):
    if type(places) is not int or places < 0:
        return None
    return Q(1, 2*10**places)


def layer_bounds(row, layer):
    """Independent support by requested layer; unused concentration never gates it."""
    if layer not in LAYERS:
        raise ValueError(layer)
    reasons = []
    x, r = rational(row.get('amount')), rational(row.get('rsd'))
    dx, dr = half_place(row.get('amount_decimal_places')), half_place(row.get('rsd_decimal_places'))
    if row.get('mean_support') != 'SUPPORTED' or x is None or x <= 0:
        reasons.append('mean_support/strictly_positive_amount')
    if layer != 'N':
        if row.get('amount_rounding_support') != 'SUPPORTED' or dx is None or dx <= 0:
            reasons.append('amount_rounding_support/nonnegative_integer_decimal_places')
        elif x is not None and x-dx <= 0:
            reasons.append('amount_minus_half_place_not_positive')
    if layer == 'S_outer':
        if row.get('rsd_support') != 'SUPPORTED' or r is None or r < 0:
            reasons.append('rsd_support/nonnegative_rsd')
        if row.get('rsd_rounding_support') != 'SUPPORTED' or dr is None or dr <= 0:
            reasons.append('rsd_rounding_support/nonnegative_integer_decimal_places')
        elif r is not None and r+dr >= 100:
            reasons.append('rsd_plus_half_place_not_below_100')
    if reasons:
        return None, reasons
    lo, hi = (x, x) if layer == 'N' else (x-dx, x+dx)
    if layer == 'S_outer':
        lo, hi = lo*(1-(r+dr)/100), hi*(1+(r+dr)/100)
    if not 0 < lo <= hi:
        return None, ['invalid_positive_ordered_interval']
    return (lo, hi), []


def root_compare(a, b):
    """Compare positive roots (rational radicand, positive degree), exactly."""
    left, right = a[0]**b[1], b[0]**a[1]
    return (left > right)-(left < right)


def monomial(c=Q(1), e=0):
    return (Q(c), e)


def mul(a, b):
    return (a[0]*b[0], a[1]+b[1])


def div(a, b):
    return (a[0]/b[0], a[1]-b[1])


def mono_compare(a, b, root):
    r, k = root
    left, right = a[0]**k*r**a[1], b[0]**k*r**b[1]
    return (left > right)-(left < right)


def encode_mono(a):
    return {'coefficient': str(a[0]), 'exponent': a[1]}


def decimal_bracket(root, places=12):
    """Integer bisection; both endpoints independently certify the root."""
    r, k = root
    scale = 10**places
    low, high = 0, scale
    while Q(high, scale)**k < r:
        high *= 2
    while high-low > 1:
        middle = (low+high)//2
        if Q(middle, scale)**k <= r:
            low = middle
        else:
            high = middle
    if Q(high, scale)**k == r:
        low = high
    elif Q(low, scale)**k == r:
        high = low
    assert Q(low, scale)**k <= r <= Q(high, scale)**k
    def fixed(n):
        return f'{n//scale}.{n%scale:0{places}d}'
    return [fixed(low), fixed(high)]


def approximation(root):
    with localcontext() as ctx:
        ctx.prec = 50
        r, k = root
        return (Decimal(r.numerator)/Decimal(r.denominator))**(Decimal(1)/k)


def encode_root(root):
    r, k = root
    with localcontext() as ctx:
        ctx.prec = 50
        eps = (Decimal(r.numerator)/Decimal(r.denominator)).log10()/k
    return {'radicand': str(r), 'degree': k, 'M_bracket': decimal_bracket(root),
            'reciprocal_bracket': decimal_bracket((1/r, k)),
            'epsilon_exact': f'log10({r})/{k}', 'epsilon_dex_approx': f'{eps:.12f}'}


@lru_cache(None)
def cycles(nf, ns):
    """Canonical rotations: smallest node first; retain distinct orientations."""
    result = []
    adjacency = [tuple(range(nf, nf+ns)) if i < nf else tuple(range(nf))
                 for i in range(nf+ns)]
    def visit(path):
        for nxt in adjacency[path[-1]]:
            if nxt == path[0]:
                result.append(tuple(path))
            elif nxt > path[0] and nxt not in path:
                visit(path+[nxt])
    for start in range(nf):
        visit([start])
    return tuple(sorted(result, key=lambda c: (len(c), c)))


def graph(bounds, forces, analytes):
    edges = {}
    nf = len(forces)
    for i, f in enumerate(forces):
        for j, s in enumerate(analytes):
            lo, hi = bounds[f, s]
            if not 0 < lo <= hi:
                raise ValueError('Graph requires positive ordered intervals')
            edges[nf+j, i] = (hi, (f, s), 'U')
            edges[i, nf+j] = (1/lo, (f, s), 'L')
    return edges


def cycle_ratio(cycle, edges):
    ratio = Q(1)
    for u, v in zip(cycle, cycle[1:]+cycle[:1]):
        ratio /= edges[u, v][0]
    return ratio


def solve(bounds, forces=FORCES, analytes=ANALYTES):
    """Full-cycle lower bound and multiplicative Bellman-Ford attaining witness."""
    if set(bounds) != set(product(forces, analytes)):
        raise ValueError('Incomplete or unexpected matrix constraints')
    edges = graph(bounds, forces, analytes)
    optimum = four = (Q(1), 1)
    control = control4 = None
    candidates = cycles(len(forces), len(analytes))
    for cycle in candidates:
        candidate = cycle_ratio(cycle, edges), len(cycle)
        if root_compare(candidate, optimum) > 0:
            optimum, control = candidate, cycle
        if len(cycle) == 4 and root_compare(candidate, four) > 0:
            four, control4 = candidate, cycle
    # Unit super-root edges initialize every potential to 1. Paths through at
    # most n-1 graph edges suffice because no cycle can reduce a path product.
    n = len(forces)+len(analytes)
    potentials = [monomial() for _ in range(n)]
    for _ in range(n-1):
        previous = potentials[:]
        for (u, v), (w, _, _) in sorted(edges.items()):
            trial = mul(previous[u], monomial(w, 1))
            if mono_compare(trial, potentials[v], optimum) < 0:
                potentials[v] = trial
    for (u, v), (w, _, _) in edges.items():
        assert mono_compare(potentials[v], mul(potentials[u], monomial(w, 1)), optimum) <= 0
    g = {f: div(potentials[i], potentials[0]) for i, f in enumerate(forces)}
    a = {s: div(potentials[0], potentials[len(forces)+j]) for j, s in enumerate(analytes)}
    predictions = {(f, s): mul(g[f], a[s]) for f, s in bounds}
    assert mono_compare(g[forces[0]], monomial(), optimum) == 0
    for cell, (lo, hi) in bounds.items():
        assert mono_compare(predictions[cell], monomial(lo, -1), optimum) >= 0
        assert mono_compare(predictions[cell], monomial(hi, 1), optimum) <= 0
    return dict(root=optimum, cycle=control, four=four, cycle4=control4,
                g=g, a=a, predictions=predictions, edges=edges)


def certificate(cycle, edges, temp, pressure, forces, analytes):
    if cycle is None:
        return {'kind': 'OBJECTIVE_FLOOR', 'M': '1'}
    def node(i):
        return f'F:{forces[i]}' if i < len(forces) else 'A:'+analytes[i-len(forces)]
    return {'kind': 'DIRECTED_SIMPLE_CYCLE', 'nodes': [node(i) for i in cycle],
            'k': len(cycle), 'R': str(cycle_ratio(cycle, edges)),
            'edges': [{'from': node(u), 'to': node(v), 'bound': edges[u, v][2],
                       'cell_key': [temp, pressure, *edges[u, v][1]]}
                      for u, v in zip(cycle, cycle[1:]+cycle[:1])]}


def matrix(indexed, temp, pressure, layer, omitted):
    analytes = tuple(s for s in ANALYTES if s != omitted)
    cells, bounds = [], {}
    for f, s in product(FORCES, analytes):
        row = indexed[temp, pressure, f, s]
        box, reasons = layer_bounds(row, layer)
        cell = {'key': key(row), 'status': 'SUPPORTED' if box else 'UNSUPPORTED',
                'unsupported_reasons': reasons, 'qualification': row['qualification'],
                'source': {'dataset': 'khamitova2020/tamping', 'table': row['table'],
                           'csv_file': row['csv_file'], 'csv_row_1based': row['csv_row_1based']},
                'L': str(box[0]) if box else None, 'U': str(box[1]) if box else None}
        cells.append(cell)
        if box:
            bounds[f, s] = box
    out = {'temperature_C': temp, 'pressure_bar': pressure, 'layer': layer,
           'omitted_analyte': omitted, 'analytes': list(analytes), 'forces_kgf': list(FORCES),
           'cells': cells, 'status': 'SUPPORTED' if len(bounds) == len(cells) else 'UNSUPPORTED'}
    if out['status'] != 'SUPPORTED':
        out['incomplete_reason'] = 'Requested matrix retained; at least one unsupported cell/layer'
        return out
    solved = solve(bounds, analytes=analytes)
    out['cost'] = encode_root(solved['root'])
    out['certificate'] = certificate(solved['cycle'], solved['edges'], temp, pressure, FORCES, analytes)
    out['four_cell_lower_bound'] = encode_root(solved['four'])
    out['four_cell_certificate'] = certificate(solved['cycle4'], solved['edges'], temp, pressure, FORCES, analytes)
    comparison = root_compare(solved['root'], solved['four'])
    assert comparison >= 0
    out['longer_cycle_strictly_improves'] = comparison > 0
    out['gap_exact_relation'] = 'POSITIVE' if comparison else 'ZERO'
    with localcontext() as ctx:
        ctx.prec = 50
        out['gap_M_minus_M4_approx'] = f"{approximation(solved['root'])-approximation(solved['four']):.12f}"
    out['force_factors'] = {str(f): encode_mono(v) for f, v in solved['g'].items()}
    out['analyte_amplitudes_mg_per_reference_40ml'] = {s: encode_mono(v) for s, v in solved['a'].items()}
    for cell in cells:
        cell['prediction'] = encode_mono(solved['predictions'][tuple(cell['key'][2:])])
    return out


def build_report(observations=None):
    identities = verify_inputs()
    rows = load_observations() if observations is None else observations
    indexed = index_observations(rows)
    matrices = [matrix(indexed, t, p, layer, omitted)
                for t, p, layer, omitted in product(TEMPERATURES, PRESSURES, LAYERS, (None, *ANALYTES))]
    ratios = []
    for t, p, layer, (s, z), f in product(TEMPERATURES, PRESSURES, LAYERS, combinations(ANALYTES, 2), FORCES):
        first, second = indexed[t, p, f, s], indexed[t, p, f, z]
        b1, _ = layer_bounds(first, layer)
        b2, _ = layer_bounds(second, layer)
        ratios.append({'temperature_C': t, 'pressure_bar': p, 'layer': layer,
                       'numerator_analyte': s, 'denominator_analyte': z, 'force_kgf': f,
                       'ratio_L': str(b1[0]/b2[1]) if b1 and b2 else None,
                       'ratio_U': str(b1[1]/b2[0]) if b1 and b2 else None,
                       'status': 'SUPPORTED' if b1 and b2 else 'UNSUPPORTED'})
    meta = json.loads((ROOT/PREDECESSOR/'source_metadata.json').read_text())
    return {'task': 'SCI-MD-KHAMITOVA-COMMON-SCALING-001', 'actual_base': BASE,
            'dataset': 'khamitova2020/tamping', 'observation_reference': PREDECESSOR+'/observations.csv',
            'classification': 'G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING',
            'PHYSICAL_VALIDATION': 'NOT_ESTABLISHED', 'input_sha256': identities,
            'authenticated_pdf_sha256': meta['pdf']['sha256'],
            'reference_unit': '1 mg per reference 40 mL; g and M dimensionless',
            'monomial_encoding': 'positive rational coefficient * M**integer exponent',
            'support_complete': all(m['status'] == 'SUPPORTED' for m in matrices),
            'matrices': matrices, 'pairwise_analyte_ratios': ratios}


def csv_write(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def write_tables(report, output):
    summaries, predictions = [], []
    for m in report['matrices']:
        base = {k: m[k] for k in ('temperature_C', 'pressure_bar', 'layer', 'omitted_analyte', 'status')}
        summary = dict(base)
        for name, prefix in [('cost', 'M'), ('four_cell_lower_bound', 'M4')]:
            r = m.get(name, {})
            summary.update({prefix+'_radicand': r.get('radicand'), prefix+'_degree': r.get('degree'),
                            prefix+'_lo': r.get('M_bracket', [None, None])[0],
                            prefix+'_hi': r.get('M_bracket', [None, None])[1]})
        cost = m.get('cost', {})
        summary.update(reciprocal_lo=cost.get('reciprocal_bracket', [None, None])[0],
                       reciprocal_hi=cost.get('reciprocal_bracket', [None, None])[1],
                       epsilon_dex_approx=cost.get('epsilon_dex_approx'),
                       controlling_cycle=json.dumps(m.get('certificate', {}).get('nodes', [])),
                       gap_exact_relation=m.get('gap_exact_relation'),
                       gap_M_minus_M4_approx=m.get('gap_M_minus_M4_approx'))
        summaries.append(summary)
        for c in m['cells']:
            f, s = c['key'][2:]
            row = dict(base, force_kgf=f, analyte=s, cell_status=c['status'], L=c['L'], U=c['U'],
                       unsupported_reasons='; '.join(c['unsupported_reasons']))
            for prefix, v in [('g', m.get('force_factors', {}).get(str(f), {})),
                              ('a', m.get('analyte_amplitudes_mg_per_reference_40ml', {}).get(s, {})),
                              ('prediction', c.get('prediction', {}))]:
                row[prefix+'_coefficient'] = v.get('coefficient')
                row[prefix+'_M_exponent'] = v.get('exponent')
                row[prefix+'_approx'] = None
                if v:
                    with localcontext() as ctx:
                        ctx.prec = 50
                        q = Q(v['coefficient'])
                        root = (Q(m['cost']['radicand']), m['cost']['degree'])
                        display = Decimal(q.numerator)/Decimal(q.denominator)*approximation(root)**v['exponent']
                        row[prefix+'_approx'] = f'{display:.12f}'
            predictions.append(row)
    csv_write(output/'primary_summary.csv', [s for s in summaries if s['omitted_analyte'] is None])
    csv_write(output/'analyte_influence.csv', [s for s in summaries if s['omitted_analyte'] is not None])
    csv_write(output/'factors_predictions.csv', predictions)
    csv_write(output/'pairwise_ratios.csv', report['pairwise_analyte_ratios'])


def plot(report, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import math

    primary = [m for m in report['matrices'] if m['omitted_analyte'] is None]
    fig, axes = plt.subplots(1, 2, figsize=(12.8, 5.2), layout='constrained')
    colors = ['#0072B2', '#D55E00', '#009E73']
    for layer, color, marker in zip(LAYERS, colors, ['o', 'x', 's']):
        selected = [m for m in primary if m['layer'] == layer]
        axes[0].plot(range(9), [float(approximation((Q(m['cost']['radicand']), m['cost']['degree'])))
                               if m['status'] == 'SUPPORTED' else float('nan') for m in selected],
                     marker=marker, color=color, label=layer, lw=1)
    axes[0].axhline(1, color='gray', ls='--', lw=1)
    axes[0].set(xticks=range(9), xticklabels=[f'{t} / {p}' for t, p in product(TEMPERATURES, PRESSURES)],
                xlabel='Temperature (°C) / pressure (bar)', ylabel='Minimum multiplicative allowance M',
                title='A  Common scaling across four analytes')
    axes[0].tick_params(axis='x', labelrotation=45)
    axes[0].legend()
    nominal = [m for m in primary if m['layer'] == 'N' and m['status'] == 'SUPPORTED']
    worst = nominal[0]
    for m in nominal[1:]:
        if root_compare((Q(m['cost']['radicand']), m['cost']['degree']),
                        (Q(worst['cost']['radicand']), worst['cost']['degree'])) > 0:
            worst = m
    root = (Q(worst['cost']['radicand']), worst['cost']['degree'])
    value = float(approximation(root))
    epsilon = math.log10(value)
    for s, color, marker in zip(ANALYTES, [*colors, '#CC79A7'], ['o', 's', '^', 'D']):
        cells = [c for c in worst['cells'] if c['key'][3] == s]
        residuals = [math.log10(float(Q(c['L']))/(float(Q(c['prediction']['coefficient']))*
                      value**c['prediction']['exponent'])) for c in cells]
        axes[1].plot(FORCES, residuals, marker=marker, color=color, label=s, lw=1)
    for y in [-epsilon, epsilon]:
        axes[1].axhline(y, color='gray', ls='--', lw=1)
    axes[1].axhline(0, color='gray', lw=.6)
    axes[1].set(xlabel='Nominal force label (kgF)', ylabel='log10(reported amount / representative) [dex]',
                xticks=FORCES, title=f"B  Nominal residuals: {worst['temperature_C']} °C / {worst['pressure_bar']} bar")
    axes[1].legend(fontsize=8)
    fig.suptitle('Khamitova: retrospective, target-exposed representation analysis\n'
                 'One attaining representation; dashed residual limits are ±εN, not confidence bounds', fontsize=11)
    fig.savefig(output/'comparison.png', dpi=170)
    plt.close(fig)
    write_json(output/'plot_environment.json', {'matplotlib': matplotlib.__version__,
               'cross_version_png_identity': 'NOT_ASSERTED'})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    report = build_report()
    args.output.mkdir(parents=True, exist_ok=True)
    write_json(args.output/'results.json', report)
    write_tables(report, args.output)
    if args.plot:
        plot(report, args.output)
    print(f"135 requested matrices; supported={sum(m['status'] == 'SUPPORTED' for m in report['matrices'])}")


if __name__ == '__main__':
    main()

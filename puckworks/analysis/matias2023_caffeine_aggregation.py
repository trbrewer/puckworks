"""Exact necessary-shape bound for fixed positive exponential aggregation.

Research-only, retrospective, target-exposed, source-internal, nonscoring.
Source-derived outputs: Matias et al. (2023), CC BY 4.0. First-party code: MIT.
No source recovery, component fitting or production physics. See task METHOD.md.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

from .matias2023_caffeine_fraction_shape import multiplicative_enclosure

DATA = Path(__file__).resolve().parents[1] / 'data/matias2023'
TASK = 'SCI-MD-MATIAS-CAFFEINE-AGGREGATION-001'
SUPPORTED = {'RECOVERED', 'COVERED_BUT_RECOVERED', 'CLIPPED_BUT_RECOVERED'}
LAYERS = {
    'N': ('z', 'z', ('center_status',)),
    'G': ('G_lower', 'G_upper', ('center_status',)),
    'P_outer': ('L_minus', 'U_plus', ('L_status', 'U_status')),
    'P_inner': ('L_plus', 'U_minus', ('L_status', 'U_status')),
}
INPUT_HASHES = {
    'observations.csv': '6f2f8a426159de950a518768a11b326376ead1f2a1de91f8ca6f0c77d5f6cd0a',
    'figure_geometry.json': '6f56f7a6548d38df0db12602b6528768fb8eecafb15ae61ba59ead0af935928e',
}


def rational(value):
    """Exact string/integer/rational interface; floats are never input authority."""
    if not isinstance(value, (str, int, Q)) or isinstance(value, bool):
        raise ValueError('finite rational string/integer required')
    try:
        return Q(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('finite rational required') from exc


def exact_minimax(x, intervals):
    """Greatest convex minorant of prefix upper minima; no floating decisions.

    Earliest prefix source wins ties. Pop a middle hull anchor on equal slopes,
    leaving endpoints of collinear runs. At an anchor use a=b=i and weights 1,0.
    Zero observations have no objective; one/two are covered without curvature.
    """
    x = list(map(rational, x))
    bounds = [(rational(l), rational(u)) for l, u in intervals]
    if len(x) != len(bounds) or any(l > u for l, u in bounds):
        raise ValueError('matching valid intervals required')
    if any(a >= b for a, b in zip(x, x[1:])):
        raise ValueError('strictly increasing coordinates required')
    if not x:
        return {'epsilon': None, 'support_status': 'SOURCE_SUPPORT_FAILURE'}
    v, sources = [], []
    for i, (_, u) in enumerate(bounds):
        p = i if not v or u < v[-1] else sources[-1]
        sources.append(p)
        v.append(bounds[p][1])
    hull = []
    for i in range(len(x)):
        while len(hull) >= 2:
            a, b = hull[-2:]
            if (v[b]-v[a])/(x[b]-x[a]) < (v[i]-v[b])/(x[i]-x[b]):
                break
            hull.pop()
        hull.append(i)
    h, provenance = [], []
    segment = 0
    for i in range(len(x)):
        while segment+1 < len(hull) and hull[segment+1] < i:
            segment += 1
        if i in hull:
            a = b = i
            alpha, beta = Q(1), Q(0)
        else:
            a, b = hull[segment:segment+2]
            alpha = (x[b]-x[i])/(x[b]-x[a])
            beta = (x[i]-x[a])/(x[b]-x[a])
        hi = alpha*v[a]+beta*v[b]
        h.append(hi)
        provenance.append({
            'index': i, 'x': str(x[i]), 'upper': str(bounds[i][1]),
            'prefix_minimum': str(v[i]), 'prefix_source': sources[i],
            'is_hull_anchor': i in hull, 'a': a, 'b': b,
            'x_a': str(x[a]), 'x_b': str(x[b]),
            'alpha': str(alpha), 'beta': str(beta),
            'p_a': sources[a], 'p_b': sources[b], 'h': str(hi),
            'interpolating_segment_slope': str((v[b]-v[a])/(x[b]-x[a])) if a != b else None,
            'slope_to_next_hull_anchor': (str((v[hull[hull.index(i)+1]]-v[i]) /
                                              (x[hull[hull.index(i)+1]]-x[i]))
                                          if i in hull[:-1] else None),
        })
    epsilon = max([Q(0)]+[(l-hi)/2 for (l, _), hi in zip(bounds, h)])
    certificates = [{'kind': 'NONNEGATIVITY', 'bound': '0'}] if epsilon == 0 else []
    for i, ((l, _), hi) in enumerate(zip(bounds, h)):
        if (l-hi)/2 == epsilon:
            certificates.append({'kind': 'HULL_PREFIX', **provenance[i],
                                 'lower': str(l), 'bound': str(epsilon)})
    y = [hi+epsilon for hi in h]
    nearest = [min(u, max(l, yy)) for yy, (l, u) in zip(y, bounds)]
    delta = [yy-n for yy, n in zip(y, nearest)]
    slopes = [(b-a)/(xb-xa) for a, b, xa, xb in zip(y, y[1:], x, x[1:])]
    if (max(map(abs, delta)) != epsilon or any(s > 0 for s in slopes)
            or any(a > b for a, b in zip(slopes, slopes[1:]))):
        raise ArithmeticError('CHECK_FAILURE: exact original-constraint witness check')
    return {
        'epsilon': str(epsilon), 'x': list(map(str, x)),
        'hull_anchors': hull, 'hull_segment_slopes': [
            str((v[b]-v[a])/(x[b]-x[a])) for a, b in zip(hull, hull[1:])],
        'provenance': provenance, 'certificates': certificates,
        'predicted_log': list(map(str, y)), 'nearest_log': list(map(str, nearest)),
        'interval_distance': list(map(str, delta)),
        'maximum_absolute_interval_distance': str(max(map(abs, delta))),
        'monotonicity_slacks': [str(a-b) for a, b in zip(y, y[1:])],
        'convexity_slacks': [str(b-a) for a, b in zip(slopes, slopes[1:])],
    }


def read_observations():
    for name, expected in INPUT_HASHES.items():
        if sha256((DATA/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f'SOURCE_INPUT_INVALID: changed accepted bytes: {name}')
    with (DATA/'observations.csv').open(newline='') as stream:
        return list(csv.DictReader(stream))


def validate_slots(rows):
    if [r.get('fraction_id') for r in rows] != [f'F{i:02}' for i in range(1, 11)]:
        raise ValueError('SOURCE_INPUT_INVALID: retain ten original ordered fraction IDs')
    for i, row in enumerate(rows):
        expected = {'x': i, 'fraction_index': i+1, 'nominal_start_mL': 5*i,
                    'nominal_end_mL': 5*(i+1), 'displayed_endpoint_mL': 5*(i+1)}
        if any(rational(row.get(k)) != v for k, v in expected.items()):
            raise ValueError('SOURCE_INPUT_INVALID: original slot/window coordinates')


def layer_intervals(rows, layer):
    """Keep unsupported slots; qualified missing/invalid values are input failures."""
    lo, hi, statuses = LAYERS[layer]
    intervals, invalid, empty = [], [], []
    for row in rows:
        if not all(row.get(k) in SUPPORTED for k in statuses):
            intervals.append(None)
            continue
        try:
            l, u = rational(row.get(lo)), rational(row.get(hi))
            # Enclosure orientation is source input validity, unlike empty P_inner.
            groups = [('G_lower', 'z', 'G_upper')] if layer in ('N', 'G') else [
                ('L_minus', 'L', 'L_plus'), ('U_minus', 'U', 'U_plus')]
            for keys in groups:
                a, b, c = (rational(row.get(k)) for k in keys)
                if not a <= b <= c:
                    raise ValueError('invalid marginal enclosure')
            if l > u:
                if layer == 'P_inner':
                    empty.append(row['fraction_id'])
                else:
                    raise ValueError('reversed source interval')
            intervals.append((l, u))
        except ValueError:
            invalid.append(row['fraction_id'])
            intervals.append(None)
    if invalid:
        status = 'SOURCE_INPUT_INVALID'
    elif empty:
        status = 'INNER_UNAVAILABLE'
    elif not any(v is not None for v in intervals):
        status = 'SOURCE_SUPPORT_FAILURE'
    else:
        status = 'COMPLETE' if all(v is not None for v in intervals) else 'SUBSET_LOWER_BOUND_ONLY'
    return intervals, status, invalid, empty


def local_diagnostics(intervals, layer, status):
    rows = []
    for i in range(8):
        triple = intervals[i:i+3]
        r = {'layer': layer, 'fraction_ids': ','.join(f'F{j+1:02}' for j in range(i, i+3)),
             'x_start': i, 'support_status': 'UNSUPPORTED', 'lower': None, 'upper': None,
             'local_exclusion': None}
        if status in ('COMPLETE', 'SUBSET_LOWER_BOUND_ONLY') and all(v is not None for v in triple):
            (l0, u0), (l1, u1), (l2, u2) = triple
            lower, upper = l0-2*u1+l2, u0-2*l1+u2
            r.update(support_status='SUPPORTED', lower=str(lower), upper=str(upper),
                     local_exclusion=upper < 0)
        rows.append(r)
    return rows


def build_report(rows=None):
    rows = read_observations() if rows is None else rows
    validate_slots(rows)
    layers, witnesses, support, local = {}, [], [], []
    for layer in LAYERS:
        intervals, status, invalid, empty = layer_intervals(rows, layer)
        selected = [i for i, band in enumerate(intervals) if band is not None]
        result = {'support_status': status, 'supported_count': len(selected),
                  'fraction_ids': [rows[i]['fraction_id'] for i in selected],
                  'invalid_source_fractions': invalid, 'empty_inner_fractions': empty,
                  'epsilon': None, 'mixture_discrepancy_lower_bound': None}
        valid = status in ('COMPLETE', 'SUBSET_LOWER_BOUND_ONLY')
        if valid:
            result.update(exact_minimax([rows[i]['x'] for i in selected],
                                        [intervals[i] for i in selected]))
            e = rational(result['epsilon'])
            result.update(epsilon_dex_approx=float(e), multiplicative=multiplicative_enclosure(e),
                          relaxed_objective_scope='ALL_TEN' if status == 'COMPLETE' else 'SUPPORTED_SUBSET_ONLY',
                          mixture_discrepancy_lower_bound={
                              'epsilon_dex': str(e), 'is_exact_mixture_optimum': False,
                              'scope': 'same layer bands and nominal fixed-weight equal-volume contract',
                              'endpoint_quantifier': 'EVERY_ADMISSIBLE_REALIZATION' if layer == 'P_outer' else
                              'INNER_BANDS_ONLY_NOT_UNIVERSAL_EXCLUSION' if layer == 'P_inner' else 'DECLARED_LAYER',
                          })
            result['disposition'] = ('NECESSARY_SHAPE_EXCLUDED' if e > 0 else
                                     'NECESSARY_SHAPE_COMPATIBLE_ONLY' if status == 'COMPLETE' else
                                     'FULL_COHORT_COMPATIBILITY_NOT_ESTABLISHED')
        else:
            result['disposition'] = status
        layers[layer] = result
        local.extend(local_diagnostics(intervals, layer, status))
        for i, row in enumerate(rows):
            band = intervals[i]
            support.append({'layer': layer, 'fraction_id': row['fraction_id'], 'x': row['x'],
                            'layer_status': status, 'interval_supported': band is not None,
                            **{k: row.get(k) for k in ('center_status', 'L_status', 'U_status',
                                                       'horizontal_status', 'horizontal_semantics')},
                            'interval_lower': str(band[0]) if band else None,
                            'interval_upper': str(band[1]) if band else None})
            w = {'layer': layer, 'fraction_id': row['fraction_id'], 'x': row['x'],
                 'support_status': status if valid and band else status if not valid else 'UNSUPPORTED',
                 'predicted_log': None, 'predicted_mg_L_approx': None,
                 'nearest_permitted_log': None, 'signed_interval_distance_log': None,
                 'center_residual_log': None, 'center_difference_mg_L_approx': None,
                 'monotonicity_slack_to_next_supported': None,
                 'secant_convexity_slack_at_next_supported': None}
            if valid and band:
                j = selected.index(i)
                y = rational(result['predicted_log'][j])
                w.update(predicted_log=str(y), predicted_mg_L_approx=10**float(y),
                         nearest_permitted_log=result['nearest_log'][j],
                         signed_interval_distance_log=result['interval_distance'][j])
                if row.get('center_status') in SUPPORTED:
                    try:
                        z = rational(row['z'])
                    except ValueError:
                        pass  # Endpoint-supported P calculation need not have a valid center.
                    else:
                        w.update(center_residual_log=str(y-z),
                                 center_difference_mg_L_approx=10**float(y)-10**float(z))
                for key, values in [('monotonicity_slack_to_next_supported', result['monotonicity_slacks']),
                                    ('secant_convexity_slack_at_next_supported', result['convexity_slacks'])]:
                    if j < len(values):
                        w[key] = values[j]
            witnesses.append(w)
    return {'task': TASK, 'dataset_id': 'matias2023/fig3_caffeine_fractions',
            'classification': 'G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING',
            'PHYSICAL_VALIDATION': 'NOT_ESTABLISHED', 'original_slot_count': 10,
            'physical_extraction_count': 4, 'layers': layers, 'support': support,
            'witness_residuals': witnesses, 'local_curvatures': local,
            'objective_family': 'NONINCREASING_CONVEX_LOG_SEQUENCE_NECESSARY_RELAXATION',
            'P_quantifiers': 'epsilon_LC,outer <= epsilon_LC,realized <= epsilon_LC,inner; epsilon_mixture,realized >= epsilon_LC,realized >= epsilon_LC,outer. Inner relaxed optimum is NOT a mixture upper bound.',
            'rights': 'Matias et al. (2023), CC BY 4.0 source-derived replot/results; first-party code MIT'}


def write_csv(path, rows):
    fields = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def plot_report(report, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows = read_observations()
    fig, ax = plt.subplots(figsize=(9, 5.8))
    v = [5*(i+1) for i in range(10)]
    concentration = lambda key: [10**float(rational(r[key])) for r in rows]
    ax.set_yscale('log')
    ax.vlines(v, concentration('L'), concentration('U'), color='0.6', lw=2,
              label='Reported SE endpoints (descriptive)')
    ax.errorbar(v, concentration('z'), yerr=[
        [a-b for a, b in zip(concentration('z'), concentration('G_lower'))],
        [a-b for a, b in zip(concentration('G_upper'), concentration('z'))]],
        fmt='none', ecolor='#d98200', capsize=5, label='Graphical G bands (true scale)')
    ax.plot(v, concentration('z'), 'ks', ms=5, label='Ten aggregate finite-vial means')
    for layer, color, marker in [('N', '#31688e', 'o'), ('P_outer', '#8b3f71', 'D')]:
        fit = report['layers'][layer]
        if fit['support_status'] == 'COMPLETE':
            ax.plot(v, [10**float(rational(y)) for y in fit['predicted_log']],
                    color=color, marker=marker, ms=3, lw=1.4,
                    label=f'{layer}: relaxed shape representative')
    # The first source certificate supplies the controlling chord; no solver controls hard-coded.
    fit = report['layers']['P_outer']
    if fit['support_status'] == 'COMPLETE':
        cert = next(c for c in fit['certificates'] if c['kind'] == 'HULL_PREFIX')
        i, a, b = cert['index'], cert['a'], cert['b']
        ax.annotate(f"Control: F{i+1:02} versus F{a+1:02}–F{b+1:02} chord\nweights {cert['alpha']}, {cert['beta']}",
                    xy=(v[i], concentration('z')[i]), xytext=(24, 2300),
                    arrowprops={'arrowstyle': '->', 'color': '0.35'}, fontsize=9)
    ax.set(xlabel='Nominal cumulative endpoint (mL); each point is a 5 mL vial',
           ylabel='Caffeine concentration (mg/L)', xticks=v,
           title='Matias aggregate caffeine: necessary-shape discrepancy')
    ax.grid(alpha=.15, which='both')
    ax.legend(fontsize=8, loc='lower left')
    fig.text(.08, .025, 'Connecting segments guide the eye; no instantaneous law or mixture components.\n'
             'Caps are display marks, not volume uncertainty. Source: Matias et al. (2023), CC BY 4.0.\n'
             'Retrospective/source-internal; PHYSICAL_VALIDATION=NOT_ESTABLISHED.', fontsize=8)
    fig.tight_layout(rect=(0, .10, 1, 1))
    fig.savefig(output/'comparison.png', dpi=160, metadata={'Software': TASK})
    plt.close(fig)


def write_report(output, *, plot=False):
    output.mkdir(parents=True, exist_ok=True)
    report = build_report()
    report['input_sha256'] = {name: sha256((DATA/name).read_bytes()).hexdigest() for name in INPUT_HASHES}
    (output/'results.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    for name, key in [('support', 'support'), ('witness_residuals', 'witness_residuals'),
                      ('local_curvatures', 'local_curvatures')]:
        write_csv(output/f'{name}.csv', report[key])
    for name, key in [('prefix_hull', 'provenance'), ('certificates', 'certificates')]:
        entries = []
        for layer, result in report['layers'].items():
            for item in result.get(key, []):
                item = dict(item)
                for index in ('index', 'a', 'b', 'p_a', 'p_b', 'prefix_source'):
                    if index in item:
                        item[index+'_fraction_id'] = result['fraction_ids'][item[index]]
                entries.append({'layer': layer, **item})
        write_csv(output/f'{name}.csv', entries)
    if plot:
        plot_report(report, output)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    result = write_report(args.output, plot=args.plot)
    print(json.dumps({k: {'status': v['support_status'], 'epsilon_LC': v['epsilon']}
                      for k, v in result['layers'].items()}, sort_keys=True))


if __name__ == '__main__':
    main()

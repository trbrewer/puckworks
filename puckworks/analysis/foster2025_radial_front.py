"""Finite representation of Foster's published annular fitted interfaces.

Research only: exact rational outer enclosures of graphical readings, not a
physical uncertainty model. PDF/image extraction is deliberately separate.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data/foster2025_2/fig8_fig9_radial_front.json'
FITTED = 'AUTHENTICATED_FITTED_ESTIMATE'
UNSUPPORTED = 'UNSUPPORTED_COMPLETE_COHORT'
FAILURE = 'QUALIFICATION_FAILURE'


def q(value):
    return F(str(value))


def product(x, y):
    v = [a*b for a in x for b in y]
    return min(v), max(v)


def bounds_record(bounds):
    """Outward decimal enclosure plus exact rational certificate."""
    lo, hi = bounds
    n = 10**6
    lower = (lo*n).__floor__() / n
    upper = (hi*n).__ceil__() / n
    return {'lower': lower, 'upper': upper,
            'exact_lower': str(lo), 'exact_upper': str(hi),
            'method': 'conservative rational outer enclosure; not claimed sharp'}


def independent_e(intervals):
    """Sharp per-reading E bounds for genuinely independent center intervals."""
    if not intervals:
        raise ValueError('empty center cohort')
    lo = max(F(0), max(a for a, b in intervals)-min(b for a, b in intervals))/2
    hi = max([F(0)] + [b-c for i, (a, b) in enumerate(intervals)
                       for j, (c, d) in enumerate(intervals) if i != j])/2
    return lo, hi


def classify_g(bounds, feasible=True, supported=True):
    if not feasible:
        return FAILURE
    if not supported:
        return UNSUPPORTED
    lo, hi = bounds
    if lo > 0:
        return 'EXCLUDED_FOR_ALL_ADMISSIBLE_READINGS'
    if hi <= 0:
        return 'COMPATIBLE_FOR_EVERY_ADMISSIBLE_READING'
    return 'GRAPHICALLY_UNRESOLVED'


def calibration(record):
    """Exact vertices of the bounded 2D affine tick polygon.

    Each pixel tick box constrains a shared alpha,beta. Enumerating intersecting
    boundary lines of this explicit polygon is exact rational geometry, not an
    unproved corner check of a nonlinear problem.
    """
    inequalities = []
    for tick in record['ticks']:
        p, h, z = q(tick['p']), q(tick['allowance']), q(tick['z'])
        inequalities.extend([(p-h, F(1), z), (-(p+h), F(-1), -z)])
    vertices = set()
    for (a, b, c), (d, e, f) in itertools.combinations(inequalities, 2):
        determinant = a*e-b*d
        if determinant:
            alpha, beta = (c*e-b*f)/determinant, (a*f-c*d)/determinant
            if alpha > 0 and all(x*alpha+y*beta <= z for x, y, z in inequalities):
                vertices.add((alpha, beta))
    if not vertices:
        raise ValueError('no admissible positive affine calibration')
    nominal = q(record['nominal_alpha']), q(record['nominal_beta'])
    if nominal[0] <= 0 or not all(a*nominal[0]+b*nominal[1] <= c
                                  for a, b, c in inequalities):
        raise ValueError('nominal calibration is not feasible')
    return {'vertices': sorted(vertices), 'nominal': nominal,
            'alpha': (min(a for a, b in vertices), max(a for a, b in vertices))}


def supported(row, feature):
    return row[feature]['support'] == 'SUPPORTED'


def pixel_interval(row, feature):
    return tuple(map(q, row[feature]['enclosure_px']))


def ordinate(row, feature, cals):
    lo, hi = pixel_interval(row, feature)
    vertices = cals[row['calibration_id']]['vertices']
    return min(a*lo+b for a, b in vertices), max(a*hi+b for a, b in vertices)


def nominal(row, feature, cals):
    a, b = cals[row['calibration_id']]['nominal']
    return a*q(row[feature]['nominal_px'])+b


def difference(left, lf, right, rf, cals):
    """Keep shared offsets shared; mixed depictions retain distinct origins."""
    if left['calibration_id'] == right['calibration_id']:
        l, u = pixel_interval(left, lf)
        v, w = pixel_interval(right, rf)
        return product((l-w, u-v), cals[left['calibration_id']]['alpha'])
    l, u = ordinate(left, lf, cals)
    v, w = ordinate(right, rf, cals)
    return l-w, u-v


def e_enclosure(rows, cals):
    ids = {r['calibration_id'] for r in rows}
    if len(ids) == 1:
        e = independent_e([pixel_interval(r, 'center') for r in rows])
        return product(e, cals[rows[0]['calibration_id']]['alpha'])
    # Independent marginal boxes are a superset of the correlated reading set.
    return independent_e([ordinate(r, 'center', cals) for r in rows])


def g_enclosure(rows, cals):
    pairs = [difference(a, 'lower_endpoint', b, 'upper_endpoint', cals)
             for a in rows for b in rows]
    return max(p[0] for p in pairs), max(p[1] for p in pairs)


def check_witness(rows, cals):
    """Check one simultaneous nominal reading, including duplicate linkage.

    Primary nominal pixels define the shared center; the duplicate's *feasible*
    pixel may differ from its separately recorded nominal local pixel. Unreadable
    features remain absent: no hidden reading is put into scientific inputs.
    """
    duplicates = []
    for row in rows:
        for feature in ('center', 'lower_endpoint', 'upper_endpoint'):
            rec = row[feature]
            if supported(row, feature):
                p = q(rec['nominal_px'])
                lo, hi = pixel_interval(row, feature)
                if not lo <= p <= hi:
                    raise ValueError('nominal feature outside graphical enclosure')
            elif rec['nominal_px'] is not None or rec['enclosure_px'] is not None:
                raise ValueError('unsupported reading has numerical pixels')
        ordered = [nominal(row, key, cals) for key in
                   ('lower_endpoint', 'center', 'upper_endpoint') if supported(row, key)]
        if ordered != sorted(ordered):
            raise ValueError('nominal endpoint/center order is infeasible')
        for duplicate in row['duplicate_records']:
            if duplicate['endpoint_linkage'] != 'NOT_AUTHENTICATED_NOT_TRANSFERRED':
                raise ValueError('endpoint sharing is not authenticated by this intake')
            if duplicate.get('lower_endpoint') is not None or duplicate.get('upper_endpoint') is not None:
                raise ValueError('unqualified duplicate endpoints')
            if duplicate['linkage'] == 'AUTHENTICATED_SHARED_CENTER':
                if not supported(row, 'center'):
                    raise ValueError('linked primary center is missing')
                z = nominal(row, 'center', cals)
                a, b = cals[duplicate['calibration_id']]['nominal']
                p = (z-b)/a
                lo, hi = map(q, duplicate['center']['enclosure_px'])
                if not lo <= p <= hi:
                    raise ValueError('shared-center nominal witness conflicts with duplicate')
                duplicates.append({'observation_id': row['observation_id'],
                                   'shared_z': str(z), 'fig8_feasible_pixel': str(p)})
            elif duplicate['linkage'] != 'CORROBORATION_ONLY_NO_NUMERICAL_CONSTRAINT':
                raise ValueError('unknown duplicate linkage')
    return duplicates


def validate_cohort(data):
    rows = data['observations']
    slots = [(r['scan_label_s'], r['shell_id']) for r in rows]
    expected = {(t, f'r{s:02d}') for t in range(9) for s in range(10)}
    if len(rows) != 90 or set(slots) != expected or len(set(slots)) != 90:
        raise ValueError('canonical cohort must contain exactly 90 unique slots')
    if len({r['observation_id'] for r in rows}) != 90:
        raise ValueError('duplicated observation identity')
    for row in rows:
        s = int(row['shell_id'][1:])
        if (q(row['shell_lower']), q(row['shell_upper']), q(row['shell_midpoint'])) != (
                F(s, 10), F(s+1, 10), F(2*s+1, 20)):
            raise ValueError('changed shell membership')
        if row['role'] != ('primary' if row['scan_label_s'] in (3, 4, 5) else 'context'):
            raise ValueError('changed primary cohort')
        if row['eligibility'] not in {FITTED, 'AUTHENTICATED_SOURCE_RULE_ZERO',
                                      'UNRESOLVED_FIT_VERSUS_RULE', 'UNSUPPORTED_READING'}:
            raise ValueError('unknown eligibility')
        if (row['eligibility'] == 'AUTHENTICATED_SOURCE_RULE_ZERO') != (
                row['source_rule_value'] == 0):
            raise ValueError('rule zero must remain distinct from a fitted center')


def scan_result(rows, cals, feasible=True):
    rows = sorted(rows, key=lambda r: r['shell_midpoint'])
    eligible = [r for r in rows if r['eligibility'] == FITTED]
    centers = [r for r in eligible if supported(r, 'center')]
    endpoints = [r for r in eligible if all(supported(r, k) for k in
                 ('lower_endpoint', 'upper_endpoint'))]
    result = {'scan_label_s': rows[0]['scan_label_s'], 'role': rows[0]['role'],
              'fit_eligible_count': len(eligible),
              'eligibility': 'ALL_FITTED' if len(eligible) == 10 else 'MIXED_OR_SOURCE_RULE',
              'E': {'status': UNSUPPORTED, 'supported_centers': len(centers)},
              'D': {'status': UNSUPPORTED},
              'G': {'status': UNSUPPORTED, 'supported_complete_extents': len(endpoints)},
              'partial_obstruction': None}
    if not feasible:
        for key in ('E', 'D', 'G'):
            result[key]['status'] = FAILURE
        return result
    if len(centers) == 10:
        bounds = e_enclosure(rows, cals)
        values = [nominal(r, 'center', cals) for r in rows]
        lo, hi = min(values), max(values)
        invariant = {}
        for name, sign in [('maximum', 1), ('minimum', -1)]:
            invariant[name] = [r['shell_id'] for r in rows if all(
                sign*difference(r, 'center', s, 'center', cals)[0 if sign == 1 else 1] > 0
                for s in rows if s is not r)]
        result['E'].update(status='QUALIFIED', bounds=bounds_record(bounds),
                           nominal=float((hi-lo)/2), nominal_representative=float((hi+lo)/2),
                           nominal_min_shells=[r['shell_id'] for r, v in zip(rows, values) if v == lo],
                           nominal_max_shells=[r['shell_id'] for r, v in zip(rows, values) if v == hi],
                           certified_invariant_extremal_shells=invariant,
                           variation='GRAPHICALLY_RESOLVED' if bounds[0] > 0 else 'NOT_SETTLED_BY_ENCLOSURE')
    inner, outer = rows[0], rows[-1]
    if all(r['eligibility'] == FITTED and supported(r, 'center') for r in (inner, outer)):
        bounds = difference(outer, 'center', inner, 'center', cals)
        result['D'].update(status='QUALIFIED', bounds=bounds_record(bounds),
                           nominal=float(nominal(outer, 'center', cals)-nominal(inner, 'center', cals)),
                           shell_ids=[outer['shell_id'], inner['shell_id']],
                           direction='OUTER_DEEPER' if bounds[0] > 0 else
                           'OUTER_SHALLOWER' if bounds[1] < 0 else 'GRAPHICALLY_UNRESOLVED')
    if len(endpoints) == 10:
        bounds = g_enclosure(rows, cals)
        av = [nominal(r, 'lower_endpoint', cals) for r in rows]
        bv = [nominal(r, 'upper_endpoint', cals) for r in rows]
        a, b = max(av), min(bv)
        result['G'].update(status=classify_g(bounds), bounds=bounds_record(bounds),
                           nominal=float(a-b), nominal_A=float(a), nominal_B=float(b),
                           nominal_common_interval=[float(a), float(b)] if a <= b else None,
                           witness_label='checked joint nominal reading; c may depend on reading',
                           nominal_A_shells=[r['shell_id'] for r, v in zip(rows, av) if v == a],
                           nominal_B_shells=[r['shell_id'] for r, v in zip(rows, bv) if v == b],
                           H_bounds=bounds_record((max(F(0), bounds[0])/2, max(F(0), bounds[1])/2)))
    candidates = [(difference(a, 'lower_endpoint', b, 'upper_endpoint', cals)[0], a, b)
                  for a in eligible if supported(a, 'lower_endpoint')
                  for b in eligible if supported(b, 'upper_endpoint')]
    if candidates:
        lower, a, b = max(candidates, key=lambda x: x[0])
        if lower > 0:
            result['partial_obstruction'] = {'lower_bound': bounds_record((lower, lower)),
                'lower_endpoint_observation': a['observation_id'],
                'upper_endpoint_observation': b['observation_id'],
                'scope': 'supported-pair obstruction; does not create complete range upper bound'}
    return result


def analyze(data):
    validate_cohort(data)
    try:
        cals = {k: calibration(v) for k, v in data['calibrations'].items()}
        duplicate_witness = check_witness(data['observations'], cals)
        feasible, failure = True, None
    except ValueError as exc:
        cals, duplicate_witness, feasible, failure = {}, [], False, str(exc)
    results = [scan_result([r for r in data['observations'] if r['scan_label_s'] == t],
                           cals, feasible) for t in range(9)]
    return {'task_id': data['task_id'], 'dataset_id': data['dataset_id'],
            'classification': data['classification'], 'PHYSICAL_VALIDATION': 'NOT_ESTABLISHED',
            'input_sha256': hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest(),
            'feasibility': 'NONEMPTY_CHECKED_RATIONAL_WITNESS' if feasible else FAILURE,
            'qualification_failure': failure,
            'calibration_certificates': {k: {'alpha_bounds': [str(x) for x in c['alpha']],
                'vertices': [[str(x) for x in p] for p in c['vertices']],
                'nominal': [str(x) for x in c['nominal']]} for k, c in cals.items()},
            'shared_center_witnesses': duplicate_witness,
            'enclosure_scope': 'Full continuous admissible set covered by conservative supersets; shared-figure offsets cancel; duplicate constraints checked for feasibility but not used to tighten bounds.',
            'scans': results}


def plot_report(data, report, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    cals = {k: calibration(v) for k, v in data['calibrations'].items()}
    colors = plt.get_cmap('tab10').colors
    fig, axes = plt.subplots(4, 3, figsize=(15, 16), gridspec_kw={'height_ratios': [1, 1, 1, .85]})
    for t, ax in enumerate(axes[:3].flat):
        color = colors[t]
        rows = [r for r in data['observations'] if r['scan_label_s'] == t]
        for r in rows:
            x = r['shell_midpoint']
            if r['eligibility'] == 'AUTHENTICATED_SOURCE_RULE_ZERO':
                ax.scatter(x, 0, marker='s', facecolors='none', edgecolors=[color], s=32)
                continue
            for key in ('lower_endpoint', 'upper_endpoint'):
                if supported(r, key):
                    y = float(nominal(r, key, cals))
                    lo, hi = map(float, ordinate(r, key, cals))
                    ax.plot([x-.018, x+.018], [y, y], color=color, lw=1.4)
                    ax.fill_between([x-.018, x+.018], lo, hi, color=color, alpha=.14)
            if all(supported(r, k) for k in ('lower_endpoint', 'upper_endpoint')):
                ax.plot([x, x], [float(nominal(r, k, cals)) for k in
                                ('lower_endpoint', 'upper_endpoint')], color=color, lw=2, alpha=.45)
            if supported(r, 'center'):
                y = float(nominal(r, 'center', cals))
                lo, hi = map(float, ordinate(r, 'center', cals))
                ax.errorbar(x, y, yerr=[[y-lo], [hi-y]], fmt='o', color='black', ms=3, capsize=3)
            else:
                ax.scatter(x, 1.1, color='black', marker='x', s=18)
        primary = t in (3, 4, 5)
        ax.set_title(f't = {t} s — {"PRIMARY" if primary else "context"}', fontweight='bold' if primary else 'normal')
        if primary:
            for spine in ax.spines.values():
                spine.set_linewidth(2)
                spine.set_color(color)
        ax.set(xlim=(0, 1), ylim=(1.14, -.15), xlabel='radius / bed radius', ylabel='depth / bed depth ↓')
        ax.set_xticks([.05, .25, .45, .65, .85, .95])
        ax.grid(alpha=.16)
    for j, key in enumerate(('E', 'D', 'G')):
        ax = axes[3, j]
        for t in (3, 4, 5):
            rec = report['scans'][t][key]
            if 'bounds' in rec:
                b, n = rec['bounds'], rec['nominal']
                ax.errorbar(n, t, xerr=[[n-b['lower']], [b['upper']-n]], fmt='o', color=colors[t], capsize=5)
            else:
                ax.text(.04, t, 'Unsupported: missing endpoint', transform=ax.get_yaxis_transform(),
                        fontsize=10, va='center', color=colors[t])
        ax.axvline(0, color='gray', lw=1)
        ax.set(yticks=[3, 4, 5], ylim=(2.6, 5.4), ylabel='printed scan (s)', xlabel='fractional bed depth')
        ax.set_title({'E': 'E: optimal center representation cost', 'D': 'D: outer minus inner depth',
                      'G': 'G: displayed-extent separation'}[key])
        ax.grid(alpha=.2)
    fig.legend(handles=[Line2D([], [], marker='o', color='black', label='Center + graphical reading enclosure'),
                        Line2D([], [], color=colors[4], lw=2, alpha=.5, label='Published front-position extent'),
                        Patch(facecolor=colors[4], alpha=.15, label='Endpoint reading enclosure'),
                        Line2D([], [], marker='s', markerfacecolor='none', color='gray', linestyle='none', label='Authenticated rule zero'),
                        Line2D([], [], marker='x', color='black', linestyle='none', label='Center unsupported (shown below frame data)')],
               loc='lower center', ncol=2, bbox_to_anchor=(.5, .025))
    fig.suptitle('Foster fine grind: nine dependent annular interface profiles\nPrimary center variation and displayed-extent compatibility are separate questions', fontsize=16)
    fig.text(.5, .012, 'Source-internal graphical analysis; extents are not confidence/physical bounds. No physical validation. Missing readings remain missing.', ha='center', fontsize=10)
    fig.tight_layout(rect=(0, .09, 1, .95))
    fig.savefig(output/'comparison.png', dpi=150, metadata={'Software': 'puckworks.analysis.foster2025_radial_front'})
    plt.close(fig)


def write_report(data, report, output, plot=False):
    output.mkdir(parents=True, exist_ok=True)
    (output/'scan_results.json').write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    fields = ['scan_label_s', 'role', 'fit_eligible_count', 'eligibility']
    fields += [f'{k}_{s}' for k in ('E', 'D', 'G') for s in ('status', 'nominal', 'lower', 'upper')]
    with (output/'scan_results.csv').open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        for r in report['scans']:
            row = {k: r[k] for k in fields if k in r}
            for k in ('E', 'D', 'G'):
                row.update({f'{k}_status': r[k]['status'], f'{k}_nominal': r[k].get('nominal'),
                            f'{k}_lower': r[k].get('bounds', {}).get('lower'),
                            f'{k}_upper': r[k].get('bounds', {}).get('upper')})
            writer.writerow(row)
    summary = {'task_id': report['task_id'], 'dataset_id': report['dataset_id'],
               'PHYSICAL_VALIDATION': 'NOT_ESTABLISHED', 'feasibility': report['feasibility'],
               'primary': [r for r in report['scans'] if r['role'] == 'primary'],
               'counts': {'canonical_slots': len(data['observations']), 'primary_slots': 30},
               'source_image_sha256': {k: v['sha256'] for k, v in data['images'].items()},
               'canonical_file_sha256': hashlib.sha256(DATA.read_bytes()).hexdigest()}
    (output/'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True)+'\n')
    if plot:
        if report['feasibility'] == FAILURE:
            raise ValueError('cannot plot an unqualified graphical set')
        plot_report(data, report, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    data = json.loads(DATA.read_text())
    report = analyze(data)
    write_report(data, report, args.output, args.plot)
    print(json.dumps({'feasibility': report['feasibility'], 'primary': [
        {k: r[k] for k in ('scan_label_s', 'E', 'D', 'G')} for r in report['scans'] if r['role'] == 'primary']}, indent=2))
    return 1 if report['feasibility'] == FAILURE else 0


if __name__ == '__main__':
    raise SystemExit(main())

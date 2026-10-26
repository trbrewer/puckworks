"""Figure 12 native-center piecewise-linear comparison; research only.

Offline: python -m puckworks.analysis.moroney2015_fixed_flow_pressure --output DIR
The historical moroney2015_data() loader and raw data are unchanged.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

from puckworks.analysis.cameron2020_pressure_tamp import outward

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'docs/analysis/sci_md_moroney_fixed_flow_pressure_001'
GRID = (50, 100, 200, 400, 600, 800, 900)
NUMERIC = ('x', 'y', 'x_lower', 'x_upper', 'y_lower', 'y_upper',
           'native_y_lower', 'native_y_upper')


def q(value):
    return Fraction(str(value))


def enclosure(values):
    values = list(values)
    return min(values), max(values)


def axis(calibration, name):
    ticks = calibration['ticks'][name]
    a, b = (q(t['coordinate_pt']) for t in (ticks[0], ticks[-1]))
    vmax = q(ticks[-1]['value'])
    checks = [t for t in calibration['all_tick_checks'] if t['axis'] == name]
    residual = max(abs(q(t['coordinate_pt']) - (a + q(t['value']) * (b-a)/vmax))
                   for t in checks)
    pad = q('.25') + max(q(t['stroke_width_pt']) for t in checks)/2 + residual
    return a, b, vmax, pad


def transform(calibration, name, native_bounds):
    a, b, vmax, pad = axis(calibration, name)
    return enclosure((p-aa)*vmax/(bb-aa) for p, aa, bb in product(
        native_bounds, [a-pad, a+pad], [b-pad, b+pad]))


def qualify(source):
    """Native-center coordinates and marginal rectangles, no PDF required."""
    observations = []
    component_ids = {}
    for panel, pressure in product(['a', 'b'], ['2.3', '9.0']):
        number = 1
        markers = sorted([m for m in source['legacy_rows'] if m['panel'] == panel
                          and m['pressure_bar_label'] == pressure], key=lambda m: m['center_pt'][0])
        for m in markers:
            if m['disposition'] == 'legend_sample':
                continue
            if m['disposition'] == 'duplicate_rendering':
                original = next((o for o in markers if o['source_id'] == m.get('duplicate_of')), None)
                if original is None or original['center_pt'] != m['center_pt']:
                    raise ValueError('Duplicate rendering lacks authenticated identical anchor')
                continue
            if m['disposition'] != 'data_marker':
                number += 1  # An unresolved internal object breaks support.
                continue
            component_ids[m['source_id']] = str(number)
    for m in source['legacy_rows']:
        if m['disposition'] != 'data_marker':
            continue
        cal = source['calibration'][m['panel']]
        row = {'id': m['legacy_row_id'], 'source_id': m['source_id'], 'panel': m['panel'],
               'series': 'L' if m['pressure_bar_label'] == '2.3' else 'H',
               'pressure_bar_label': m['pressure_bar_label'],
               'component': component_ids[m['source_id']],
               'lineage_id': m['lineage_id'] or '', 'pdf_page_index': 17,
               'drawing_index': m['drawing_index'], 'seqno': m['seqno'],
               'subpath_index': m['subpath_index'], 'stroke_width_pt': m['stroke_width_pt'],
               'native_center_x_pt': m['center_pt'][0], 'native_center_y_pt': m['center_pt'][1],
               'native_bbox_pt': m['bbox_pt'], 'center_candidates_pt': m['center_candidates_pt'],
               'legacy_mass_g': m['legacy_values']['Mbrew_g'],
               'legacy_concentration_mg_g': m['legacy_values']['concentration_mg_per_g']}
        pad = q('.25') + q(m['stroke_width_pt'])/2
        for j, name in enumerate(('x', 'y')):
            a, b, vmax, tickpad = axis(cal, name)
            candidates = [q(c[j]) for c in m['center_candidates_pt']]
            bounds = min(candidates)-pad, max(candidates)+pad
            central = (q(m['center_pt'][j])-a)*vmax/(b-a)
            row[name] = central
            row[f'{name}_lower'], row[f'{name}_upper'] = transform(cal, name, bounds)
            if name == 'y':
                # Increasing native ordinate -PDF_y retains shared offset cancellation.
                row['native_y_lower'], row['native_y_upper'] = -bounds[1], -bounds[0]
            row[f'{name}_legacy_delta'] = central-q(row['legacy_mass_g' if name == 'x' else 'legacy_concentration_mg_g'])
        observations.append(row)
    return observations


def load_qualified(bundle=BUNDLE):
    """Load this qualified sidecar, never silently filter the historical raw loader."""
    with (bundle / 'qualified_observations.csv').open(newline='') as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for key in NUMERIC:
            row[key] = q(row[key + '_exact'])
    return rows


def components(rows):
    """Explicit components preserve source gaps. Inconsistent duplicate x refuses use."""
    groups = {}
    for row in rows:
        groups.setdefault(str(row['component']), []).append(row)
    for name, group in groups.items():
        group.sort(key=lambda r: r['x'])
        if any(a['x'] == b['x'] for a, b in zip(group, group[1:])):
            raise ValueError(f'Duplicate x in component {name}; no averaging authorized')
    return groups


def evaluate(rows, mass):
    """Exact rational central interpolation with original IDs and convex weights."""
    for r in rows:
        if mass == r['x']:
            return {'value': r['y'], 'ids': [r['id']], 'weights': [q(1)]}
    for a, b in zip(rows, rows[1:]):
        if a['x'] < mass < b['x']:
            w = (mass-a['x'])/(b['x']-a['x'])
            return {'value': (1-w)*a['y']+w*b['y'], 'ids': [a['id'], b['id']],
                    'weights': [1-w, w]}
    return None


def common_components(low, high):
    common = []
    for li, ll in components(low).items():
        for hi, hh in components(high).items():
            start, end = max(ll[0]['x'], hh[0]['x']), min(ll[-1]['x'], hh[-1]['x'])
            if start <= end:
                common.append({'id': f'L{li}-H{hi}', 'start': start, 'end': end,
                               'low': ll, 'high': hh})
    return common


def union_knots(common):
    rows = []
    for c in common:
        knots = sorted({c['start'], c['end']} | {r['x'] for r in c['low']+c['high']
                                              if c['start'] < r['x'] < c['end']})
        for m in knots:
            lo, hi = evaluate(c['low'], m), evaluate(c['high'], m)
            rows.append({'component': c['id'], 'mass_g': m, 'c_L': lo['value'],
                         'c_H': hi['value'], 'delta': hi['value']-lo['value'],
                         'L_bracket': lo, 'H_bracket': hi,
                         'knot_observation_ids': [r['id'] for r in c['low']+c['high'] if r['x'] == m]})
    return rows


def extrema(knots):
    if not knots:
        return None
    out = {}
    for name, value, op in [('minimum', min(k['delta'] for k in knots), lambda v: v),
                            ('maximum', max(k['delta'] for k in knots), lambda v: v),
                            ('maximum_absolute', max(abs(k['delta']) for k in knots), abs)]:
        points = [{'component': k['component'], 'mass_g': k['mass_g'],
                   'signed_delta': k['delta'], 'union_knot_index': i}
                  for i, k in enumerate(knots) if op(k['delta']) == value]
        intervals = []
        for i, (a, b) in enumerate(zip(knots, knots[1:])):
            if a['component'] == b['component'] and a['delta'] == b['delta'] and op(a['delta']) == value:
                intervals.append({'component': a['component'], 'mass_g': [a['mass_g'], b['mass_g']],
                                  'signed_delta': a['delta'], 'union_knot_indices': [i, i+1]})
        out[name] = {'value_mg_g': value, 'attaining_knots': points, 'attaining_intervals': intervals}
    return out


def sensitivity_series(rows, mass):
    # Universal coverage is separate from the enumeration of possible brackets.
    if any(a['x_upper'] >= b['x_lower'] for a, b in zip(rows, rows[1:])):
        return {'status': 'UNSUPPORTED', 'reason': 'Coordinate ordering not certified by rectangular method'}
    if not rows[0]['x_upper'] <= mass <= rows[-1]['x_lower']:
        return {'status': 'UNSUPPORTED', 'reason': 'Universal component coverage not certified'}
    brackets = []
    for a, b in zip(rows, rows[1:]):
        l0, u0, l1, u1 = a['x_lower'], a['x_upper'], b['x_lower'], b['x_upper']
        if not l0 <= mass <= u1:
            continue
        wmin = (mass-min(u0, mass))/(u1-min(u0, mass))
        wmax = (mass-l0)/(max(l1, mass)-l0)
        low = min((1-w)*a['native_y_lower']+w*b['native_y_lower'] for w in (wmin, wmax))
        high = max((1-w)*a['native_y_upper']+w*b['native_y_upper'] for w in (wmin, wmax))
        brackets.append({'ids': [a['id'], b['id']], 'weight_bounds': [wmin, wmax],
                         'native_ordinate_bounds': [low, high]})
    if not brackets:
        return {'status': 'UNSUPPORTED', 'reason': 'No adjacent segment represented by method'}
    return {'status': 'SUPPORTED', 'reason': None,
            'universal_mass_domain_g': [rows[0]['x_upper'], rows[-1]['x_lower']],
            'native_ordinate_bounds': [min(b['native_ordinate_bounds'][0] for b in brackets),
                                      max(b['native_ordinate_bounds'][1] for b in brackets)],
            'possible_brackets': brackets}


def sign(bounds):
    return 'POSITIVE' if bounds[0] > 0 else 'NEGATIVE' if bounds[1] < 0 else 'SIGN_UNRESOLVED'


def contrast_slot(panel, mass, common, calibration):
    r = {'panel': panel, 'mass_g': mass, 'central_support_status': 'UNSUPPORTED',
         'central_reason': 'No common central component', 'component': None,
         'c_L': None, 'c_H': None, 'delta': None, 'L_bracket': None, 'H_bracket': None,
         'sensitivity_support_status': 'UNSUPPORTED', 'sensitivity_sign': 'UNSUPPORTED',
         'sensitivity_reason': 'No common central component', 'delta_bounds': None,
         'delta_bounds_display': None, 'L_sensitivity': None, 'H_sensitivity': None,
         'solute_mass_status': 'UNSUPPORTED', 'delta_S_mg': None, 'delta_S_bounds_mg': None,
         'solute_mass_reason': 'Cumulative mass denominator/withdrawal accounting not authenticated for high-pressure record' if panel == 'a' else 'Exit concentration is not cumulative pot concentration',
         'relative_contrast_status': 'NOT_REQUESTED', 'relative_contrast': None}
    eligible = [c for c in common if c['start'] <= mass <= c['end']]
    if len(eligible) != 1:
        if len(eligible) > 1:
            r['central_reason'] = r['sensitivity_reason'] = 'Multiple overlapping components; ambiguous evaluation'
        return r
    c = eligible[0]
    lo, hi = evaluate(c['low'], mass), evaluate(c['high'], mass)
    r.update(central_support_status='SUPPORTED', central_reason=None, component=c['id'],
             c_L=lo['value'], c_H=hi['value'], delta=hi['value']-lo['value'],
             L_bracket=lo, H_bracket=hi)
    sl, sh = sensitivity_series(c['low'], mass), sensitivity_series(c['high'], mass)
    r.update(L_sensitivity=sl, H_sensitivity=sh)
    if sl['status'] != 'SUPPORTED' or sh['status'] != 'SUPPORTED':
        r['sensitivity_reason'] = '; '.join(s['reason'] for s in (sl, sh) if s['reason'])
        return r
    a, b, vmax, pad = axis(calibration, 'y')
    scale = enclosure([vmax/(a-b-2*pad), vmax/(a-b+2*pad)])
    l, h = sl['native_ordinate_bounds'], sh['native_ordinate_bounds']
    bounds = enclosure(x*s for x, s in product([h[0]-l[1], h[1]-l[0]], scale))
    if not bounds[0] <= r['delta'] <= bounds[1]:
        raise ValueError('Nominal contrast outside sensitivity enclosure')
    r.update(sensitivity_support_status='SUPPORTED', sensitivity_reason=None,
             sensitivity_sign=sign(bounds), delta_bounds=bounds,
             delta_bounds_exact=list(map(str, bounds)),
             delta_bounds_display=outward(bounds, 3))
    return r


def plain(obj):
    if isinstance(obj, Fraction):
        return float(obj)
    if isinstance(obj, dict):
        result = {k: plain(v) for k, v in obj.items()}
        # Preserve exact rational results for signs, reproducibility and attainments.
        result.update({k+'_exact': str(v) for k, v in obj.items() if isinstance(v, Fraction)})
        return result
    if isinstance(obj, (tuple, list)):
        return [plain(v) for v in obj]
    return obj


def write_csv(path, rows, fields=None):
    fields = fields or list(rows[0])
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fields, lineterminator='\n')
        writer.writeheader()
        for r in rows:
            writer.writerow({k: json.dumps(v, sort_keys=True, separators=(',', ':')) if isinstance(v, (dict, list, tuple)) else v for k, v in r.items()})


def analyze(observations, source):
    contrasts, knots, panels = [], [], {}
    for p in ['a', 'b']:
        low = [r for r in observations if r['panel'] == p and r['series'] == 'L']
        high = [r for r in observations if r['panel'] == p and r['series'] == 'H']
        common = common_components(low, high)
        union = union_knots(common)
        knots += [dict(panel=p, **k) for k in union]
        panels[p] = {'observable': 'pot concentration' if p == 'a' else 'filter-exit concentration',
                     'counts': {'L': len(low), 'H': len(high)},
                     'common_domains_g': [{'component': c['id'], 'start': c['start'], 'end': c['end']} for c in common],
                     'extrema': extrema(union), 'union_knot_count': len(union)}
        contrasts += [contrast_slot(p, q(m), common, source['calibration'][p]) for m in GRID]
    return {'task': source['task'], 'dataset_id': source['dataset_id'],
            'scientific_status': 'SOURCE_QUALIFIED_OBSERVATIONAL_COMPARISON',
            'physical_validation': 'NOT_ESTABLISHED', 'counts': source['counts'],
            'panels': panels, 'contrasts': contrasts, 'union_knots': knots,
            'arithmetic': 'Exact rational arithmetic on serialized native decimal coordinates; JSON/CSV numeric display uses nearest binary64; *_exact retains rationals; interval display rounds outward to .001 mg/g. No sign tolerance or graphical allowance hidden in arithmetic.',
            'sensitivity_method': 'Rectangular x marginals include tick and center allowances once; shared x calibration/coordinate dependencies relaxed. Native -PDF_y interpolation then H-L cancels shared vertical offset; one positive uncertain vertical scale applied to the difference. Marker ordinate and x marginals vary independently; marginal extrema need not be jointly realizable; not sharp.',
            'experimental_uncertainty': 'UNKNOWN; graphical bounds are not experimental SD/CI or significance',
            'optional_derivations': {'relative_contrasts': 'OMITTED; no denominator floor or tail ratio',
                                     'solute_mass': 'UNSUPPORTED; high-pressure cumulative mass/withdrawal contract unresolved'},
            'claim_limits': ['Native pressure labels only; differential/absolute terminology unresolved',
                             'No equality, practical equivalence or pressure independence from zero inclusion',
                             'No statistical significance or causal pressure effect',
                             'Nominal common flow/loading do not establish common bed state',
                             'Extrema describe the piecewise-linear representation, not unknown physical curves',
                             'SCI-MD-MORONEY-TRANSFER-001 remains CALIBRATION_INADEQUATE']}


def figure(observations, result, output):
    """One deterministic SVG: native markers/representation and discrete intervals."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    with plt.rc_context({'svg.hashsalt': 'moroney-fixed-flow-001', 'font.size': 10}):
        fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex='col',
                                gridspec_kw={'height_ratios': [1.35, 1]}, layout='constrained')
        for col, panel in enumerate(['a', 'b']):
            for series, color, marker, label in [('L', '#2166ac', 'o', '2.3 bar labelled'),
                                                 ('H', '#b2182b', 's', '9.0 bar labelled')]:
                rr = [r for r in observations if r['panel'] == panel and r['series'] == series]
                for group in components(rr).values():
                    axs[0, col].plot([float(r['x']) for r in group], [float(r['y']) for r in group],
                                     color=color, marker=marker, markersize=3.5, lw=1, label=label)
            slots = [r for r in result['contrasts'] if r['panel'] == panel]
            kk = [r for r in result['union_knots'] if r['panel'] == panel]
            for comp in sorted({r['component'] for r in kk}):
                group = [r for r in kk if r['component'] == comp]
                axs[1, col].plot([float(r['mass_g']) for r in group], [float(r['delta']) for r in group],
                                 color='#333333', lw=1, label='Declared interpolant difference')
            for r in slots:
                if r['sensitivity_support_status'] == 'SUPPORTED':
                    m, y = float(r['mass_g']), float(r['delta'])
                    a, b = map(float, r['delta_bounds'])
                    color = '#b2182b' if r['sensitivity_sign'] == 'NEGATIVE' else '#6a51a3'
                    axs[1, col].errorbar(m, y, yerr=[[y-a], [b-y]], fmt='o', color=color,
                                        capsize=4, markersize=4)
            for ax in axs[:, col]:
                ax.axhline(0, color='#888888', lw=.6)
                ax.set_xlim(0, 1000)
                ax.grid(alpha=.15)
            axs[0, col].set_ylim(-8, 230)
            axs[0, col].set_title('a · Coffee pot' if panel == 'a' else 'b · Filter exit')
            axs[0, col].set_ylabel('Concentration (mg solubles/g beverage)')
            axs[0, col].legend(frameon=False)
            if panel == 'b':
                inset = axs[0, col].inset_axes([.49, .30, .47, .30])
                for series, color, marker in [('L', '#2166ac', 'o'), ('H', '#b2182b', 's')]:
                    rr = [r for r in observations if r['panel'] == panel and r['series'] == series]
                    for group in components(rr).values():
                        inset.plot([float(r['x']) for r in group], [float(r['y']) for r in group],
                                   color=color, marker=marker, markersize=2.5, lw=.8)
                inset.axhline(0, color='#888888', lw=.6)
                inset.set(xlim=(500, 1000), ylim=(-1.1, 2.5), title='Signed exit tail (mg/g)')
                inset.tick_params(labelsize=8)
            axs[1, col].set_ylabel('9.0 − 2.3 bar labelled Δc (mg/g)')
            axs[1, col].set_xlabel('Beverage mass (g)')
            axs[1, col].set_ylim(-40, 20)
        fig.suptitle('Moroney 2015 Figure 12 · Reported 60 g coffee, 250 mL/min\n'
                     'SOURCE INTERNAL · Observational comparison', fontsize=14)
        fig.text(.5, -.06, 'Lines: declared piecewise-linear representation. Bars: discrete graphical sensitivity only; no continuous band.\n'
                 'Red bars resolve a negative sign; purple bars include zero. Experimental uncertainty unknown. PHYSICAL_VALIDATION=NOT_ESTABLISHED.',
                 ha='center', fontsize=9)
        fig.savefig(output / 'COMPARISON.svg', metadata={'Date': None}, bbox_inches='tight')
        svg = output / 'COMPARISON.svg'
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
        plt.close(fig)


def report(result):
    resolved = [f'{r["panel"]} at {float(r["mass_g"]):g} g ({r["sensitivity_sign"]})'
                for r in result['contrasts'] if r['sensitivity_sign'] in ('POSITIVE', 'NEGATIVE')]
    lines = ['# Figure 12 fixed-flow pressure-labelled comparison', '',
             '**Source-qualified observational comparison.** Native Figure 12 centers define two separate',
             'piecewise-linear concentration profiles. All 14 central and graphical requests are',
             'supported. Graphically resolved: ' + ', '.join(resolved) + '.',
             'The other 13 intervals include zero; this does not establish equality or equivalence.', '',
             'G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /',
             'TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.', '',
             '## Fixed beverage masses', '',
             'Units: mg solubles/g beverage; Δc = 9.0-bar-labelled − 2.3-bar-labelled.',
             'Central numbers round to .001; sensitivity endpoints round outward to .001.', '',
             '| Panel | M (g) | c_L | c_H | Δc | Graphical enclosure | Sign |',
             '|---|---:|---:|---:|---:|---|---|']
    for r in result['contrasts']:
        bound = r['delta_bounds_display']
        lines.append(f'| {r["panel"]} | {float(r["mass_g"]):g} | {float(r["c_L"]):.3f} | {float(r["c_H"]):.3f} | {float(r["delta"]):.3f} | [{bound[0]}, {bound[1]}] | {r["sensitivity_sign"]} |')
    lines += ['', '## Central domains and extrema', '',
              'All attaining locations are retained in results.json and linked to union_knots.csv.',
              'These exact rational calculations concern the declared interpolants, not bounds on',
              'unknown physical concentration curves. No extrapolation, clipping or smoothing.', '']
    for p, panel in result['panels'].items():
        c = panel['common_domains_g'][0]
        lines.append(f'Panel {p} common support: [{float(c["start"]):.9f}, {float(c["end"]):.9f}] g; {panel["union_knot_count"]} union knots.')
        for name, e in panel['extrema'].items():
            locations = ', '.join(f'{float(k["mass_g"]):.9f} g' for k in e['attaining_knots'])
            lines.append(f'- {name}: {float(e["value_mg_g"]):.9f} mg/g at {locations}.')
        lines.append('')
    lines += ['There are no tied extremal knots or constant attaining intervals in these data.', '',
              '## Qualification and limits', '',
              'The accepted 19-page publisher PDF was inspected as native paths and rendered pages.',
              'All 94 legacy rows match: 90 observations (22 low + 23 high per panel), four',
              'confirmed legend samples (rows 7, 32, 54, 79), zero ambiguous/omitted markers.',
              'All 44 low-pressure markers reuse Figure 3 observations; no additional campaign or',
              'independent extraction count is inferred. Figure 12 coordinates are primary.', '',
              'The graphical convention is 0.25 PDF point plus half applicable stroke width,',
              'enclosing center candidates and including all tick residuals. Both axes vary.',
              'Horizontal marginal rectangles drop shared-calibration dependencies; native ordinate',
              'contrasts cancel the shared vertical offset and apply a shared scale once.',
              'These conservative outer bounds are not sharp or jointly attaining source geometries.',
              'Universal support and coordinate order are checked independently of possible brackets.', '',
              'The source identifies JK standard drip-filter coffee, nominal 60 g (approximately',
              '4% moisture in the reused baseline), and 250 mL/min. Pressure wording remains',
              'unreconciled: Figure 3 calls the baseline differential pressure; G.3/Figure 12',
              'call the comparison absolute pressure. No gauge conversion or bed-pressure change',
              'is authenticated. Equal nominal flow/loading do not establish equal wetting, porosity,',
              'residence-time distribution or all other conditions.', '',
              'Pot and exit concentrations remain distinct. Replicates, averaging, flow-through',
              'assay error, covariance, sampling windows, pot mixing/withdrawals and run joins',
              'are unknown. Batch Brix calibration is contextual, not Figure 12 uncertainty.',
              'Optional solute-mass differences are unsupported at all seven pot masses because',
              'the high-pressure cumulative-denominator/withdrawal contract is not authenticated.',
              'Relative contrasts are omitted; signed tail readings are retained.', '',
              'The authors interpreted the curves as substantially pressure independent and',
              'reproducible within a few percent. This task establishes only the displayed',
              'source-conditioned differences and their declared graphical sensitivity.',
              'Graphical separation is not statistical significance or a causal pressure effect.',
              'Zero inclusion is not equality, common-curve compatibility or practical equivalence;',
              'no adequacy margin is supplied. Nothing establishes universal pressure-independent',
              'dissolution/diffusion or that pressure acts only through flow.', '',
              'SCI-MD-MORONEY-TRANSFER-001 remains CALIBRATION_INADEQUATE. No model, production',
              'default, solver, dependency pin/lock or EWP change; no successor authorized.', '',
              '[Source contract](SOURCE_NOTES.md) · [Plan](PLAN.md) · [Reproduction and checks](VERIFICATION.md)',
              '· [Independent review](review/REVIEW.md) · [Figure](COMPARISON.svg) · [VizSpec](VIZ_SPEC.json)', '',
              'PHYSICAL_VALIDATION=NOT_ESTABLISHED.']
    return '\n'.join(lines)+'\n'


def produce(output, source_path=BUNDLE/'source_objects.json', make_figure=True):
    source = json.loads(source_path.read_text())
    observations = qualify(source)
    result = analyze(observations, source)
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output/'qualified_observations.csv', [plain(o) for o in observations])
    write_csv(output/'contrasts.csv', [plain(r) for r in result['contrasts']])
    write_csv(output/'union_knots.csv', [plain(r) for r in result['union_knots']])
    (output/'results.json').write_text(json.dumps(plain(result), indent=2, sort_keys=True)+'\n')
    (output/'RESULT.md').write_text(report(result))
    if make_figure:
        figure(observations, result, output)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--source-objects', type=Path, default=BUNDLE/'source_objects.json')
    p.add_argument('--no-figure', action='store_true')
    args = p.parse_args()
    produce(args.output, args.source_objects, not args.no_figure)


if __name__ == '__main__':
    main()

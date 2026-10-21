"""Bounded Figure 6.23 inlet-referenced apparent conductance; research only.

Offline inputs are compact native-raster enclosures, not instrument samples.
No apparatus correction, hydraulic fit, viscosity estimate, or physical validation.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

from .melrose2019bed_transient import affine_enclosure, closure, compatibility

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/romancorrochano2017/fig6_23_pressure_flow_temperature'
OUTPUT = ROOT / 'docs/analysis/sci_md_corrochano_pressure_flow_001'


def _fraction(value):
    return F(str(value))


def _csv(path):
    with path.open() as stream:
        return list(csv.DictReader(line for line in stream if not line.startswith('#')))


def ratio_bounds(q, p):
    """Nonnegative indication rectangle; never divide by a nonpositive lower P."""
    if q is None or p is None:
        return {'status': 'UNSUPPORTED', 'lower': None, 'upper': None}
    ql, qu = map(_fraction, q)
    pl, pu = map(_fraction, p)
    if ql < 0 or ql > qu or pl > pu:
        raise ValueError('invalid indication rectangle')
    if pl <= 0:
        return {'status': 'NONPOSITIVE_DENOMINATOR', 'lower': None, 'upper': None}
    return {'status': 'BOUNDED_INDICATION', 'lower': ql / pu, 'upper': qu / pl}


def contrast_bounds(c, h):
    """Independent-condition outer difference and ratio, not matched brews."""
    if c is None or h is None:
        return {'status': 'UNSUPPORTED', 'difference': None, 'ratio': None}
    cl, cu = map(_fraction, c)
    hl, hu = map(_fraction, h)
    if min(cl, hl) < 0 or cl > cu or hl > hu:
        raise ValueError('invalid conductance bounds')
    difference = [cl - hu, cu - hl]
    if hl == 0:
        # null upper is unbounded, not a finite physical upper flow or resistance.
        return {'status': 'UNBOUNDED_RATIO_DENOMINATOR_INCLUDES_ZERO',
                'difference': difference,
                'ratio': [cl / hu if hu > 0 else None, None]}
    return {'status': 'BOUNDED', 'difference': difference, 'ratio': [cl / hu, cu / hl]}


def required_viscosity_ratio(g_ratio, alpha_ratio=None):
    """Common-geometry Darcy identity; unknown mapping cannot become equal mapping."""
    if alpha_ratio is None:
        return {'status': 'UNRESOLVED_UNKNOWN_ALPHA', 'bounds': None}
    al, au = map(_fraction, alpha_ratio)
    if al <= 0 or au < al:
        raise ValueError('positive mapping factors required')
    if g_ratio is None or g_ratio[0] is None:
        return {'status': 'UNSUPPORTED_OR_UNDEFINED', 'bounds': None}
    lo, hi = g_ratio
    return {'status': 'CONDITIONAL_UNBOUNDED' if hi is None else 'CONDITIONAL_BOUNDED',
            'bounds': [al * lo, au * hi if hi is not None else None]}


def calibration_support(bounds, calibration):
    """Classify against uncertain extrema of observed circles, never axis limits."""
    if bounds is None:
        return 'UNSUPPORTED'
    lo, hi = bounds
    minimum = list(map(_fraction, calibration['minimum_observed_Q_m3_s']))
    maximum = list(map(_fraction, calibration['maximum_observed_Q_m3_s']))
    if hi < minimum[0]:
        return 'BELOW'
    if lo > maximum[1]:
        return 'ABOVE'
    if lo >= minimum[1] and hi <= maximum[0]:
        return 'WITHIN'
    return 'AMBIGUOUS'


def recover(data=DATA):
    contract = json.loads((data / 'contract.json').read_text())
    cal = contract['calibration']
    xa = [[F(x) for x in pair] for pair in cal['x_anchors_px']]
    ya = [[F(x) for x in pair] for pair in cal['y_anchors_px']]
    rows = []
    for original in _csv(data / 'source_coordinates.csv'):
        row = dict(original)
        row['nominal_time_s'] = int(row['nominal_time_s'])
        x0, x1 = F(row['x_min_px']), F(row['x_max_px'])
        row['time_lower_s'], row['time_upper_s'] = affine_enclosure(
            (x0, x1), xa, list(map(F, cal['x_values_s'])))
        row['central'] = None
        if row['status'] != 'READABLE':
            row['lower'] = row['upper'] = None
        else:
            guard = F(cal['ordinate_guard_px'])
            y = (F(row['y_min_px']) - guard, F(row['y_max_px']) + guard)
            lo, hi = affine_enclosure(y, ya, list(map(F, cal['y_values'][row['panel']])))
            row['lower'], row['upper'] = max(F(0), lo), hi
        row['unit'] = contract['units'][row['panel']]
        row['calibration_support'] = calibration_support(
            _bounds(row), contract['apparatus_calibration']) if row['panel'] == 'flow' else 'FLOW_DEPENDENT_CORRECTION'
        row['physical_flow_eligibility'] = 'NOT_ESTABLISHED'
        rows.append(row)
    return contract, sorted(rows, key=lambda r: r['reading_id'])


def _bounds(row):
    if row['lower'] is None or row['upper'] is None:
        return None
    return row['lower'], row['upper']


def complete_envelope(flow, pressure):
    """Whether BOTH ordinates cover every represented stroke at this slot."""
    return all(r['coverage'] == 'COMPLETE_REPRESENTED_INK' and _bounds(r) is not None
               for r in (flow, pressure))


def conductances(readings):
    by_id = {r['reading_id']: r for r in readings}
    out = []
    for q in readings:
        if q['panel'] != 'flow':
            continue
        t, cond = q['nominal_time_s'], q['condition']
        p = by_id[f'{cond}_pressure_{t:02d}']
        r = ratio_bounds(_bounds(q), _bounds(p))
        r.update(point_id=q['reading_id'].replace('_flow_', '_G_'),
                 condition=cond, scope=q['scope'], grid=q['grid'], nominal_time_s=t,
                 flow_reading_id=q['reading_id'], pressure_reading_id=p['reading_id'],
                 time_lower_s=min(q['time_lower_s'], p['time_lower_s']),
                 time_upper_s=max(q['time_upper_s'], p['time_upper_s']), central=None,
                 complete_envelope=complete_envelope(q, p),
                 coverage=q['coverage'] if _bounds(p) is not None else 'INCOMPLETE',
                 censoring=q['censoring'], calibration_support=q['calibration_support'],
                 pairing_quantifier=('Every pressure-flow combination contained in complete condition envelopes'
                                     if complete_envelope(q, p) else
                                     'Documented flow fragment against every pressure partner contained in the condition envelope'
                                     if _bounds(q) is not None else 'UNSUPPORTED'),
                 physical_interpretation='NOT_ESTABLISHED', unit='m^3/(Pa s)')
        out.append(r)
    return sorted(out, key=lambda r: r['point_id'])


def temporal_result(points, universal=False):
    """Exact rational decisions with the existing finite-order implementation."""
    requested = sorted(points, key=lambda r: r['nominal_time_s'])
    eligible = [p for p in requested if _bounds(p) is not None]
    if universal:
        eligible = [p for p in eligible if p['complete_envelope']]
    edges = [(a['point_id'], b['point_id']) for a, b in zip(eligible, eligible[1:])
             if a['time_upper_s'] < b['time_lower_s']]
    # Retain nonadjacent supported edges even when an adjacent band's time is ambiguous.
    edges += [(a['point_id'], b['point_id']) for i, a in enumerate(eligible)
              for b in eligible[i + 2:] if a['time_upper_s'] < b['time_lower_s']]
    comp = compatibility(eligible, edges)
    lookup = {p['point_id']: p for p in eligible}
    quantifier = ('UNIVERSAL_SEPARATION_OF_COMPLETE_CONDITION_ENVELOPES' if universal else
                  'DOCUMENTED_FLOW_FRAGMENT_EVERY_CONTAINED_PRESSURE_PARTNER')
    comp.update(quantifier=quantifier, requested_ids=[p['point_id'] for p in requested],
                eligible_ids=list(lookup), unsupported_ids=[p['point_id'] for p in requested if p not in eligible],
                physical_run_trend_count='UNKNOWN', all_physical_repetitions='UNRESOLVED',
                exact_arithmetic='Fraction from decimal input tokens; strict tests without tolerance')
    for key in ['decline_witness', 'increase_witness']:
        witness = comp.get(key)
        if witness:
            witness.update(quantifier=quantifier,
                           readings=[lookup[witness[k]] for k in ['earlier', 'later']],
                           exact_margin=str(witness['difference']))
    if eligible:
        order = closure(list(lookup), edges)
        triples = [(a, b, c) for i, a in enumerate(eligible) for j, b in enumerate(eligible)
                   for k, c in enumerate(eligible) if i != j and j != k and order[i][j] and order[j][k]]
        # One middle scalar must serve BOTH inequalities. This is only rectangular possibility.
        possible = [[a['point_id'], b['point_id'], c['point_id']] for a, b, c in triples
                    if b['lower'] < min(a['upper'], c['upper'])]
    else:
        possible = []
    comp['same_trough'] = {
        'resolved': comp['decline_recovery'],
        'resolved_status': 'RESOLVED' if comp['decline_recovery'] else 'NOT_RESOLVED',
        'rectangular_possible_triples': possible,
        'possibility_status': 'NOT_EXCLUDED_BY_RECTANGULAR_RELAXATION' if possible else 'NO_SUPPORTED_STRICT_TRIPLE',
        'joint_witness': 'NOT_CHECKED', 'quantifier': quantifier,
        'meaning': 'Finite same-middle comparison only; no intervening shape or continuous minimum'}
    return comp


def _serial(value):
    if isinstance(value, F):
        return float(value)
    if isinstance(value, dict):
        return {k: _serial(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serial(v) for v in value]
    return value


def _record(row):
    """Publish numerical display values plus authoritative exact bound strings."""
    out = _serial(row)
    for key in ('lower', 'upper', 'time_lower_s', 'time_upper_s'):
        if key in row:
            value = row[key]
            out[key + '_exact'] = str(value) if value is not None else None
            if isinstance(value, F):
                v = float(value)
                # The serialized numeric field also encloses the rational bound.
                if key in ('lower', 'time_lower_s') and F(v) > value:
                    v = math.nextafter(v, -math.inf)
                if key in ('upper', 'time_upper_s') and F(v) < value:
                    v = math.nextafter(v, math.inf)
                out[key] = v
    return out


def analyze(data=DATA):
    contract, readings = recover(data)
    ratios = conductances(readings)
    results = {}
    contrasts = []
    for grid, times in contract['grids'].items():
        results[grid] = {}
        for cond in contract['conditions']:
            points = [p for p in ratios if p['scope'] == 'condition_envelope'
                      and p['condition'] == cond and p['grid'] == grid]
            results[grid][cond] = temporal_result(points, universal=True)
        results[grid]['hot_flow_late_upper'] = temporal_result(
            [p for p in ratios if p['scope'] == 'hot_flow_late_upper' and p['grid'] == grid])
        for t in times:
            c, h = [next(p for p in ratios if p['condition'] == cond and
                         p['scope'] == 'condition_envelope' and p['nominal_time_s'] == t)
                    for cond in ('cold', 'hot')]
            contrast = contrast_bounds(_bounds(c), _bounds(h))
            contrast.update(grid=grid, nominal_time_s=t, cold_id=c['point_id'], hot_id=h['point_id'],
                            time_lower_s=min(c['time_lower_s'], h['time_lower_s']),
                            time_upper_s=max(c['time_upper_s'], h['time_upper_s']),
                            complete_envelopes=c['complete_envelope'] and h['complete_envelope'],
                            quantifier='UNIVERSAL_COLD_HOT_CONDITION_ENVELOPE_COMPARISON',
                            cold_greater_resolved=bool(contrast['difference'] and contrast['difference'][0] > 0),
                            hot_censoring=h['censoring'],
                            comparison_unit='Independent condition groups; not matched physical brews',
                            physical_viscosity_ratio=required_viscosity_ratio(contrast['ratio']),
                            equal_alpha_common_geometry_scenario=required_viscosity_ratio(contrast['ratio'], (1, 1)))
            for key in ('difference', 'ratio'):
                contrast[key + '_exact'] = ([str(x) if x is not None else None for x in contrast[key]]
                                            if contrast[key] is not None else None)
            contrasts.append(contrast)
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(data.iterdir()) if p.name in ('contract.json', 'source_coordinates.csv', 'coverage.csv')}
    hashes['PLAN.md'] = contract['plan']['sha256']
    return {'task_id': contract['task_id'], 'classification': contract['classification'],
            'physical_validation': 'NOT_ESTABLISHED', 'units': contract['units'],
            'input_sha256': hashes, 'source_sha256': contract['source']['sha256'],
            'source_panel_identities': contract['source']['panels'],
            'pairing': contract['pairing'], 'coverage_contract': contract['coverage'],
            'relaxed_dependencies': contract['relaxed_dependencies'],
            'readings': [_record(r) for r in readings],
            'conductances': [_record(r) for r in ratios],
            'temporal': _serial(results), 'temperature_contrasts': _serial(contrasts),
            'counts': {'requested_condition_panel_slots': sum(r['scope'] == 'condition_envelope' for r in readings),
                       'recovered_condition_panel_slots': sum(r['scope'] == 'condition_envelope' and _bounds(r) is not None for r in readings),
                       'additional_fragment_readings': sum(r['scope'] != 'condition_envelope' for r in readings),
                       'authenticated_paired_trajectories': 0, 'independent_new_campaigns': 0},
            'apparatus_calibration': contract['apparatus_calibration'],
            'physical_observer': contract['observer'],
            'feasibility_meaning': 'Not excluded by the declared rectangular relaxation; no joint calibration/timing/pairing witness checked'}


def _write_csv(path, rows):
    with path.open('w', newline='') as stream:
        stream.write('# Offline derived Figure6.23 readings; empty values are missing, never zero.\n')
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def plot(result, output):
    """Original observation rectangles; no fitted or interpolated curve."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec

    spec = VizSpec(
        id='corrochano_fig6_23_reading_enclosures', title='Figure 6.23: pressure-referenced readings',
        class_=1, producer=Producer(module='puckworks.analysis.corrochano2017_pressure_flow', function='analyze', result_map={'readings': 'readings'}),
        badge='OBSERVED', evidence_strength='reference', components=[],
        fidelity_ceiling='Source-internal figure-reading enclosures; inlet-referenced apparent conductance, not physical permeability.',
        render_fn='puckworks.analysis.corrochano2017_pressure_flow:plot',
        caption='Condition envelopes at fixed displayed-time bands. No lines or interpolation. Hatched red: floor indication. Grey: unsupported endpoint.',
        outputs=['reconstruction.svg'], used_in='SCI-MD-CORROCHANO-PRESSURE-FLOW-001')
    if spec.validate():
        raise ValueError(spec.validate())
    with matplotlib.rc_context({'svg.hashsalt': 'corrochano-fig6-23', 'font.size': 9}):
        fig, axes = plt.subplots(3, 2, figsize=(11, 9), sharex=True)
        for col, grid in enumerate(('PRIMARY', 'SECONDARY')):
            axes[0, col].set_title(grid + (' (10,20,...,60 s)' if col == 0 else ' (5,15,...,55 s)'))
            for row, panel in enumerate(('flow', 'pressure', 'conductance')):
                ax = axes[row, col]
                source = result['conductances'] if panel == 'conductance' else result['readings']
                scale = {'flow': 1e6, 'pressure': 1e-5, 'conductance': 1e11}[panel]
                for r in source:
                    if r['grid'] != grid or (panel != 'conductance' and r['panel'] != panel):
                        continue
                    if r['scope'] != 'condition_envelope':
                        continue
                    if r['lower'] is None:
                        if r['condition'] == 'cold':
                            ax.axvspan(r['time_lower_s'], r['time_upper_s'], color='0.8', alpha=.6)
                        continue
                    colour = '#2264ad' if r['condition'] == 'cold' else '#c33530'
                    ax.add_patch(Rectangle((r['time_lower_s'], r['lower'] * scale),
                                           r['time_upper_s'] - r['time_lower_s'],
                                           (r['upper'] - r['lower']) * scale,
                                           facecolor=colour, edgecolor=colour, alpha=.40,
                                           hatch='////' if r['censoring'] == 'FLOOR_INDICATION' else None))
                if panel == 'conductance':
                    for r in result['conductances']:
                        if r['scope'] != 'hot_flow_late_upper' or r['grid'] != grid:
                            continue
                        ax.plot([r['nominal_time_s']] * 2, [r['lower'] * scale, r['upper'] * scale],
                                color='#7f1530', linewidth=2)
                ax.set_xlim(2, 63)
                upper = max(r['upper'] * scale for r in source
                            if r['grid'] == grid and r['upper'] is not None
                            and (panel == 'conductance' or r['panel'] == panel))
                ax.set_ylim(0, upper * 1.08)
                ax.grid(alpha=.18)
                ax.set_ylabel({'flow': 'Meter indication (mL/s)', 'pressure': 'Reported bed pressure (bar)',
                               'conductance': 'Inlet-referenced apparent conductance\n(10⁻¹¹ m³/(Pa s))'}[panel])
            axes[2, col].set_xlabel('Displayed time (s); sensor synchronization unqualified')
        fig.suptitle(spec.title + '\nOBSERVED / reference / SOURCE_INTERNAL / TARGET_EXPOSED', fontsize=13)
        fig.text(.08, .045, 'Blue: cold 15°C. Red: hot 80°C. Boxes: reading enclosures, not experimental error bars.\n'
                 'Hatching: floor-limited indication. Grey: unsupported 60 s band. Dark red: late flow fragment + all hot pressures.\n'
                 'No interpolation or connecting lines. Physical validation NOT_ESTABLISHED.', fontsize=9)
        fig.tight_layout(rect=(0, .11, 1, .94))
        fig.savefig(output, metadata={'Date': None, 'Creator': 'Puckworks Figure6.23 offline producer'})
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--plot', action='store_true', help='also render SVG; requires existing figures extra')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    result = analyze()
    (args.output / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + '\n')
    reading_output = DATA if args.output.resolve() == OUTPUT.resolve() else args.output
    _write_csv(reading_output / 'readings.csv', result['readings'])
    _write_csv(args.output / 'conductances.csv', result['conductances'])
    if args.plot:
        plot(result, args.output / 'reconstruction.svg')
    print(json.dumps(result['counts'], sort_keys=True))


if __name__ == '__main__':
    main()

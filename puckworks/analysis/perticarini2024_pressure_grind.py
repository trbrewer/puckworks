"""Exact retrospective duration contrasts for Perticarini Procedure 1.

Offline: python -m puckworks.analysis.perticarini2024_pressure_grind --output DIR
The entrywise box is conditional sensitivity, never experimental uncertainty.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'docs/analysis/sci_md_perticarini_pressure_grind_001'
GRINDS = ('extra_fine', 'fine', 'optimal', 'coarse', 'extra_coarse')
LABELS = dict(zip(GRINDS, ('Extra Fine', 'Fine', 'Optimal', 'Coarse', 'Extra Coarse')))
COFFEES = {'cibao': 'Cibao Altura', 'modoetia': 'Modœtia'}
STRATA = (('cibao', '93.4'), ('cibao', '90.4'), ('modoetia', '93.4'), ('modoetia', '90.4'))
INPUTS = (
    ('perticarini2024/ey_tds_cibao', 'perticarini2024/ey_tds_cibao.csv', 'cibao'),
    ('egidi2024/table2', 'egidi2024/table2_egidi2024_tds_ey.csv', 'modoetia'),
)
SOURCES = [
    {'source_id': 'perticarini_thesis', 'title': 'Predictive Models in Espresso Coffee Percolation',
     'url': 'https://pubblicazioni.unicam.it/retrieve/cf1d5052-f17f-4c11-96e2-07533acdbb41/02_28_24%20-%20Perticarini%20Alessia.pdf',
     'file_sha256': '248d480cc2ab3353799fcaa886bb1be3f6cfbe7a9f15e1cdf9d4950827424c7f',
     'inspected_pdf_pages_one_based': list(range(97, 104)),
     'inspected_printed_pages': '85–91'},
    {'source_id': 'egidi_article', 'title': 'An improved numerical scheme for coffee Extraction Yield evaluation',
     'doi': '10.1016/j.chaos.2024.115625',
     'url': 'https://pubblicazioni.unicam.it/bitstream/11581/485884/1/2024AnImpNumSchEYEval.pdf',
     'file_sha256': '1aba69278444d107ce5172eb29ba7b37883491fe0b32dfd9bc8898632e203a33',
     'inspected_pdf_pages_one_based': [6], 'inspected_printed_pages': '6'},
]
ASSUMPTIONS = {
    'governance': ['G1', 'NO_GOVERNING_PHYSICS_CHANGE', 'RESEARCH_ONLY', 'RETROSPECTIVE',
                   'TARGET_EXPOSED', 'SOURCE_INTERNAL', 'NONSCORING'],
    'physical_validation': 'NOT_ESTABLISHED',
    'duration': 'reported condition duration; statistic, spread, rounding and clock convention unknown',
    'pressure': 'native nominal machine labels; reference, sensor node and actual history unknown',
    'dose_g': '20 +/- 0.1', 'nominal_beverage_endpoint_g': '40 +/- 2',
    'actual_condition_beverage_masses': 'UNKNOWN', 'nominal_tamp_kgF': '20',
    'chemical_repetitions': 'three samples per configuration; TDS and EY explicitly averaged',
    'duration_replicate_n': None, 'sigma': 'TDS standard deviation, not duration uncertainty',
    'lineage': 'thesis Table 4.3 and Egidi Table 2 are the same Modœtia observations; canonical egidi2024/table2',
    'observation_unit': 'reported condition row; not authenticated individual shot',
    'grind': 'ordinal within coffee; Optimal recipe-defined; no calibrated cross-coffee or Cameron mapping',
    'layer_A': 'exact arithmetic on printed durations; reported zero is not physical equality',
    'layer_B': 'one common entrywise box tau_i* in [tau_i-h,tau_i+h], h>=0 seconds',
    'box_meaning': 'deterministic allowance; no probabilistic independence or statistical interpretation',
    'illustration_h_s': '1/2',
    'illustration_meaning': 'conditional nearest-second illustration; source rounding rule not authenticated',
    'composition': 'combine shared source coefficients before bounds; marginal extrema cannot be combined arbitrarily',
    'exclusions': ['Table 4.1 pooled times', 'model times', 'fitted/model Darcy fluxes',
                   '40/tau as measured flow', 'per-shot mass from EY/TDS', 'permeability/resistance',
                   'imputation', 'coffee/temperature pooling', 'causal/population/mechanism inference'],
}


def combine(*scaled_vectors):
    """Sum (multiplier, coefficient mapping) pairs, cancelling shared cells."""
    result = Counter()
    for scale, vector in scaled_vectors:
        for key, value in vector.items():
            result[key] += scale * value
    return {key: value for key, value in sorted(result.items()) if value}


def enclosure(terms, values, h):
    """Exact box image after coefficient cancellation; strings serialize rationals."""
    h = Q(h)
    if h < 0:
        raise ValueError('h must be nonnegative seconds')
    terms = combine((1, terms))
    nominal = sum((a * Q(values[key]) for key, a in terms.items()), Q(0))
    norm = sum(abs(a) for a in terms.values())
    lo, hi = nominal - h * norm, nominal + h * norm
    nominal_status = ('structural_zero' if norm == 0 else 'positive' if nominal > 0
                      else 'negative' if nominal < 0 else 'reported_zero')
    status = ('structural_zero' if norm == 0 else 'positive' if lo > 0
              else 'negative' if hi < 0 else 'unresolved')
    return {'nominal_s': str(nominal), 'nominal_status': nominal_status,
            'coefficient_l1': norm, 'critical_h_s': str(abs(nominal) / norm) if norm else None,
            'h_s': str(h), 'lower_s': str(lo), 'upper_s': str(hi), 'box_status': status}


def expected_keys():
    result = set()
    for dataset, _, coffee in INPUTS:
        for c, temp in STRATA:
            if c != coffee:
                continue
            grinds = GRINDS if (coffee, temp) == ('cibao', '93.4') else GRINDS[1:4]
            for grind in grinds:
                pressures = ('6', '9', '12') if grind in (GRINDS[0], GRINDS[-1]) else ('6', '9')
                result.update((dataset, coffee, temp, p, grind) for p in pressures)
    return result


def condition_key(o):
    return (o['dataset_id'], o['coffee_id'], o['temperature_degC'],
            o['nominal_pressure_bar'], o['grind_id'])


def load_observations(data_root=None):
    data_root = data_root or ROOT / 'puckworks/data'
    observations, inputs = [], []
    for dataset, filename, coffee in INPUTS:
        path = data_root / filename
        raw = path.read_bytes()
        # A Git blob SHA-1 hashes its header as well as the bytes. File SHA-256 does not.
        inputs.append({'dataset_id': dataset, 'path': f'puckworks/data/{filename}',
                       'file_sha256': hashlib.sha256(raw).hexdigest(),
                       'git_blob_sha1': hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()})
        with path.open(encoding='utf-8', newline='') as stream:
            reader = csv.DictReader(stream)
            names = (['coffee', 'granulometry', 'T_degC', 'p_bar', 'tau_s', 'TDS_pct', 'TDS_sd_pct', 'EY_pct']
                     if coffee == 'cibao' else
                     ['T [degC]', 'p [bar]', 'tau [s]', 'Granulometry', 'TDS [%]', 'TDS sigma', 'EY [%]'])
            if reader.fieldnames != names:
                raise ValueError(f'Unexpected schema: {dataset}')
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise ValueError(f'Malformed row: {dataset}')
                if coffee == 'cibao':
                    if row['coffee'] != COFFEES[coffee]:
                        raise ValueError('Unauthenticated coffee label')
                    temp, p, tau, native = [row[k] for k in ('T_degC', 'p_bar', 'tau_s', 'granulometry')]
                else:
                    temp, p, tau, native = [row[k] for k in ('T [degC]', 'p [bar]', 'tau [s]', 'Granulometry')]
                grind = native.lower().replace(' ', '_')
                # Identity preserves the canonical exact decimal spelling, never binary float.
                if temp not in ('93.4', '90.4') or p not in ('6', '9', '12') or grind not in GRINDS:
                    raise ValueError('Unsupported condition identity')
                if Q(tau) <= 0:
                    raise ValueError('Nonpositive duration')
                observations.append({
                    'source_condition_id': f'{dataset}|{coffee}|T{temp}|P{p}|{grind}',
                    'dataset_id': dataset, 'coffee_id': coffee, 'coffee_label': COFFEES[coffee],
                    'temperature_degC': temp, 'nominal_pressure_bar': p, 'grind_id': grind,
                    'source_grind_label': LABELS[grind], 'canonical_grind_label': native,
                    'tau_s': tau, 'duration_semantics': 'reported condition duration',
                    'duration_statistic': 'UNKNOWN', 'duration_replicate_n': 'UNKNOWN',
                    'duration_uncertainty': 'UNKNOWN', 'clock_start_stop': 'UNKNOWN',
                    'rounding_rule': 'UNKNOWN', 'actual_beverage_mass_g': 'UNKNOWN',
                    'pressure_reference_node_history': 'UNKNOWN',
                    'thesis_table': '4.2' if coffee == 'cibao' else '4.3',
                    'thesis_printed_page': 90 if coffee == 'cibao' else 91,
                    'thesis_pdf_page': 102 if coffee == 'cibao' else 103,
                    'egidi_table': '' if coffee == 'cibao' else '2',
                    'egidi_pdf_page': '' if coffee == 'cibao' else 6,
                    'authentication': 'all condition labels and numerical cells agree; SOURCE_NOTES.md',
                })
    keys = [condition_key(o) for o in observations]
    if len(keys) != len(set(keys)) or set(keys) != expected_keys():
        raise ValueError('Duplicate, missing or unexpected source conditions; no imputation')
    observations.sort(key=lambda o: (STRATA.index((o['coffee_id'], o['temperature_degC'])),
                                    GRINDS.index(o['grind_id']), int(o['nominal_pressure_bar'])))
    return observations, inputs


def reversal_status(a, b):
    if a in ('positive', 'negative') and b in ('positive', 'negative'):
        return 'strict_opposite' if a != b else 'strict_same_sign'
    return 'unresolved'


def compute(observations):
    lookup = {condition_key(o): o['source_condition_id'] for o in observations}
    if len(lookup) != len(observations) or set(lookup) != expected_keys():
        raise ValueError('Incomplete or duplicate support')
    values = {o['source_condition_id']: Q(o['tau_s']) for o in observations}
    rows, reversals = [], []
    duration = {}
    interactions = {}
    for family, interval in [('primary', ('6', '9')), ('secondary', ('9', '12')),
                             ('secondary', ('6', '12'))]:
        for coffee, temp in STRATA if family == 'primary' else STRATA[:1]:
            dataset = next(d for d, _, c in INPUTS if c == coffee)
            grinds = (GRINDS if (coffee, temp) == ('cibao', '93.4') else GRINDS[1:4])
            if family == 'secondary':
                grinds = (GRINDS[0], GRINDS[-1])
            common = {'family': family, 'coffee_id': coffee, 'coffee_label': COFFEES[coffee],
                      'temperature_degC': temp, 'pressure_from_bar': interval[0],
                      'pressure_to_bar': interval[1], 'units': 's',
                      'assumption_id': 'common_entrywise_box', 'range_label': 'conditional perturbation range'}
            for grind in grinds:
                cid = f'D-{coffee}-T{temp}-{grind}-P{interval[0]}to{interval[1]}'
                terms = {lookup[(dataset, coffee, temp, interval[1], grind)]: 1,
                         lookup[(dataset, coffee, temp, interval[0], grind)]: -1}
                row = {**common, 'contrast_id': cid, 'kind': 'duration', 'grind_a': grind, 'grind_b': '',
                       'orientation': 'higher nominal pressure minus lower', 'terms': combine((1, terms)),
                       **enclosure(terms, values, Q(1, 2))}
                rows.append(row)
                duration[(coffee, temp, grind, interval)] = row
            for ga, gb in combinations(grinds, 2):
                a, b = (duration[(coffee, temp, g, interval)] for g in (ga, gb))
                cid = f'I-{coffee}-T{temp}-{ga}_minus_{gb}-P{interval[0]}to{interval[1]}'
                terms = combine((1, a['terms']), (-1, b['terms']))
                row = {**common, 'contrast_id': cid, 'kind': 'interaction', 'grind_a': ga, 'grind_b': gb,
                       'orientation': 'finer pressure contrast minus coarser pressure contrast',
                       'terms': terms, **enclosure(terms, values, Q(1, 2))}
                rows.append(row)
                interactions[(coffee, temp, ga, gb, interval)] = row
                opposite = Q(a['nominal_s']) * Q(b['nominal_s']) < 0
                reversals.append({**common, 'diagnostic_id': f'R-{cid[2:]}', 'interaction_id': cid,
                                  'component_a_id': a['contrast_id'], 'component_b_id': b['contrast_id'],
                                  'grind_a': ga, 'grind_b': gb,
                                  'nominal_a_status': a['nominal_status'], 'nominal_b_status': b['nominal_status'],
                                  'nominal_opposite_signs': opposite,
                                  'nominal_status': 'strict_opposite' if opposite else 'nominal_opposite_not_established',
                                  'reversal_critical_h_s': str(min(Q(a['critical_h_s']), Q(b['critical_h_s']))) if opposite else None,
                                  'strict_reversal_domain': '0 <= h < reversal_critical_h_s' if opposite else None,
                                  'h_s': '1/2', 'h_a_status': a['box_status'], 'h_b_status': b['box_status'],
                                  'both_signs_resolved_at_h': all(r['box_status'] in ('positive', 'negative') for r in (a, b)),
                                  'h_status': reversal_status(a['box_status'], b['box_status']),
                                  'opposite_signs_at_h': reversal_status(a['box_status'], b['box_status']) == 'strict_opposite'})
    identities = []
    triples = [[duration[('cibao', '93.4', grind, interval)] for interval in
                [('6', '12'), ('6', '9'), ('9', '12')]] for grind in (GRINDS[0], GRINDS[-1])]
    triples.append([interactions[('cibao', '93.4', GRINDS[0], GRINDS[-1], interval)]
                    for interval in [('6', '12'), ('6', '9'), ('9', '12')]])
    for total, first, second in triples:
        residual = combine((1, total['terms']), (-1, first['terms']), (-1, second['terms']))
        if residual:
            raise ValueError('Coefficient identity failed')
        identities.append({'identity': f'{total["contrast_id"]} = {first["contrast_id"]} + {second["contrast_id"]}',
                           'terms': residual, **enclosure(residual, values, Q(1, 2))})
    breakpoints = []
    for family, kind in [('primary', 'duration'), ('primary', 'interaction'),
                         ('secondary', 'duration'), ('secondary', 'interaction')]:
        group = [r for r in rows if (r['family'], r['kind']) == (family, kind)]
        points = sorted({Q(0)} | {Q(r['critical_h_s']) for r in group})
        for index, h in enumerate(points):
            counts = Counter(enclosure(r['terms'], values, h)['box_status'] for r in group)
            breakpoints.append({'family': family, 'kind': kind, 'h_from_inclusive_s': str(h),
                                'h_to_exclusive_s': str(points[index + 1]) if index + 1 < len(points) else None,
                                'positive': counts['positive'], 'negative': counts['negative'],
                                'unresolved': counts['unresolved']})
    return {'contrasts': rows, 'reversals': reversals, 'arithmetic_identities': identities,
            'breakpoints': breakpoints}


def json_text(value):
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n'


def write_csv(path, rows):
    with path.open('w', encoding='utf-8', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        for row in rows:
            writer.writerow({key: json.dumps(value, ensure_ascii=False, sort_keys=True) if isinstance(value, (dict, list))
                             else value for key, value in row.items()})


def label(row):
    return LABELS[row['grind_a']] + (f" − {LABELS[row['grind_b']]}" if row['grind_b'] else '')


def table_text(result):
    lines = ['# Complete computed contrasts and diagnostics', '',
             'Generated from canonical inputs. All values are exact seconds (fractions retained).',
             'h=1/2 s ranges are conditional perturbation ranges, not experimental uncertainty.',
             'Strict signs require h < critical h; a zero touch is unresolved. No extra contrasts',
             'are created by diagnostics or coefficient identities.', '']
    for family in ('primary', 'secondary'):
        lines += [f'## {family.title()} contrasts', '',
                  '| ID | Native grind / finer minus coarser | Nominal s | A status | L1 | Critical h (s) | h=1/2 range (s) | B status |',
                  '|---|---|---:|---|---:|---:|---|---|']
        for r in result['contrasts']:
            if r['family'] == family:
                lines.append(f"| {r['contrast_id']} | {label(r)} | {r['nominal_s']} | {r['nominal_status']} | {r['coefficient_l1']} | {r['critical_h_s']} | [{r['lower_s']}, {r['upper_s']}] | {r['box_status']} |")
        lines += ['']
    lines += ['## Exact sign breakpoints', '',
              'Each row applies throughout [from, to); status at each zero-touch boundary is',
              'already unresolved. “∞” denotes no upper bound. All boxes share the same cells.', '',
              '| Family | Kind | h from inclusive (s) | h to exclusive (s) | Positive | Negative | Unresolved |',
              '|---|---|---:|---:|---:|---:|---:|']
    for r in result['breakpoints']:
        lines.append(f"| {r['family']} | {r['kind']} | {r['h_from_inclusive_s']} | {r['h_to_exclusive_s'] or '∞'} | {r['positive']} | {r['negative']} | {r['unresolved']} |")
    lines += ['', '## Reversal diagnostics (21; not additional contrasts)', '',
              'Component IDs and their nominal and h=1/2 signs are retained in reversals.csv/json.',
              'No nominal opposite signs means no positive threshold; unresolved is not disproved.', '',
              '| Interaction ID | Nominal opposite signs | Strict reversal until h (s), exclusive | h=1/2 status |',
              '|---|---|---:|---|']
    for r in result['reversals']:
        threshold = r['reversal_critical_h_s'] if r['reversal_critical_h_s'] is not None else 'not established'
        lines.append(f"| {r['interaction_id']} | {r['nominal_opposite_signs']} | {threshold} | {r['h_status']} |")
    lines += ['', '## Structural coefficient identities', '']
    for r in result['arithmetic_identities']:
        lines.append(f"- `{r['identity']}`: combined vector empty; residual=0, L1=0, radius=0 for every h, critical=null.")
    return '\n'.join(lines) + '\n'


def figure(result):
    """Direct SVG from computed records; float conversion is for drawing only."""
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1370" viewBox="0 0 1600 1370">',
             '<title>Reported duration response to nominal pressure by grind</title>',
             '<desc>39 dependent contrasts in seconds. D is higher minus lower nominal pressure; I is finer minus coarser D. Lines are conditional h=0.5 second entrywise perturbation ranges, not timing variability. All four strata and separate extreme-grind secondary comparisons are shown.</desc>',
             '<rect width="1600" height="1370" fill="white"/>',
             '<g font-family="sans-serif" font-size="15" fill="#17212b">']

    def text(x, y, value, size=15, **attrs):
        extra = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in attrs.items())
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" {extra}>{escape(str(value))}</text>')

    def line(x1, y1, x2, y2, color, width=1, dash=''):
        parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>')

    text(30, 32, 'Perticarini Procedure 1 · reported condition duration', 25)
    text(30, 60, 'Dots: exact printed-value contrasts. Lines: conditional perturbation ranges at h=0.5 s per original condition.')
    text(30, 83, 'Blue: strictly positive range · red: strictly negative · grey: unresolved. Hollow dot: reported zero (not physical equality).')
    text(30, 106, 'Native nominal pressure labels; unknown duration statistic / clock / spread. Categorical grinds are not particle-size distances.')
    text(30, 140, 'PRIMARY: 9 − 6 bar · duration D', 20)
    text(815, 140, 'PRIMARY: finer D − coarser D · interaction I', 20)
    y = 175
    for coffee, temp in STRATA:
        selected = [r for r in result['contrasts'] if r['family'] == 'primary'
                    and (r['coffee_id'], r['temperature_degC']) == (coffee, temp)]
        y = panel_pair(selected, y, f'{COFFEES[coffee]} · {temp} °C', -10, 10, text, line, parts)
    text(30, y + 12, 'SECONDARY ONLY: Cibao Altura · 93.4 °C · Extra Fine / Extra Coarse', 20)
    y += 48
    for interval in [('9', '12'), ('6', '12')]:
        selected = [r for r in result['contrasts'] if r['family'] == 'secondary'
                    and (r['pressure_from_bar'], r['pressure_to_bar']) == interval]
        y = panel_pair(selected, y, f'{interval[1]} − {interval[0]} bar', -10, 18, text, line, parts)
    primary = [r for r in result['reversals'] if r['family'] == 'primary']
    nominal_reversals = sum(r['nominal_opposite_signs'] for r in primary)
    retained_reversals = sum(r['opposite_signs_at_h'] for r in primary)
    text(30, y + 10, f'Primary: {nominal_reversals} nominal reversal pairs; {retained_reversals} retain strict reversal at h=0.5 s. Interaction resolution does not imply reversal.')
    domains = []
    for r in result['reversals']:
        if r['family'] == 'secondary':
            threshold = r['reversal_critical_h_s']
            domain = f'0≤h<{float(Q(threshold)):g} s' if threshold is not None else 'not established'
            domains.append(f'{domain} ({r["pressure_to_bar"]}−{r["pressure_from_bar"]})')
    text(30, y + 34, 'Secondary strict reversal: ' + '; '.join(domains) + '. No primary reversal claim from 12-bar evidence.')
    text(30, y + 58, 'SOURCE_INTERNAL / RETROSPECTIVE / NONSCORING · PHYSICAL_VALIDATION=NOT_ESTABLISHED', 16)
    parts += ['</g>', '</svg>']
    return '\n'.join(parts) + '\n'


def panel_pair(rows, y, heading, xmin, xmax, text, line, parts):
    height = 26 * max(sum(r['kind'] == k for r in rows) for k in ('duration', 'interaction'))
    for offset, kind in [(30, 'duration'), (815, 'interaction')]:
        group = [r for r in rows if r['kind'] == kind]
        text(offset, y, heading, 17)
        x0, width = offset + 270, 350
        x = lambda value: x0 + (float(Q(value)) - xmin) / (xmax - xmin) * width
        line(x(0), y + 12, x(0), y + height + 15, '#81909c', 1, '4 3')
        for index, r in enumerate(group):
            yy = y + 28 + index * 26
            text(offset, yy + 5, label(r), 14)
            color = {'positive': '#176a94', 'negative': '#ac3535', 'unresolved': '#626b73'}[r['box_status']]
            lo, hi = x(r['lower_s']), x(r['upper_s'])
            parts.append(f'<g data-contrast-id="{r["contrast_id"]}" data-nominal-s="{r["nominal_s"]}" data-lower-s="{r["lower_s"]}" data-upper-s="{r["upper_s"]}">')
            line(lo, yy, hi, yy, color, 3)
            line(lo, yy - 4, lo, yy + 4, color, 2)
            line(hi, yy - 4, hi, yy + 4, color, 2)
            fill = 'white' if r['nominal_status'] == 'reported_zero' else color
            parts.append(f'<circle cx="{x(r["nominal_s"]):.2f}" cy="{yy}" r="4" fill="{fill}" stroke="{color}" stroke-width="2"/></g>')
            text(offset + 635, yy + 5, f'{r["nominal_s"]} [{r["lower_s"]}, {r["upper_s"]}]', 13)
        axis_y = y + height + 30
        line(x(xmin), axis_y, x(xmax), axis_y, '#a2acb3')
        for value in range(xmin, xmax + 1, 2):
            line(x(value), axis_y, x(value), axis_y + 4, '#a2acb3')
            text(f'{x(value):.2f}', axis_y + 18, value, 12, text_anchor='middle')
        text(offset + 635, axis_y + 18, 'seconds', 12)
    return y + height + 75


def write(output=OUTPUT, data_root=None):
    observations, inputs = load_observations(data_root)
    result = compute(observations)
    bundle = {'schema_version': 1, 'task_id': 'SCI-MD-PERTICARINI-PRESSURE-GRIND-001',
              'sources': SOURCES, 'inputs': inputs, 'assumptions': ASSUMPTIONS,
              'observations': observations, **result}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'contrasts.json').write_text(json_text(bundle), encoding='utf-8')
    (output / 'reversals.json').write_text(json_text({key: bundle[key] for key in
        ('task_id', 'sources', 'inputs', 'assumptions', 'reversals')}), encoding='utf-8')
    for name, rows in [('observations', observations), ('contrasts', result['contrasts']),
                       ('reversals', result['reversals'])]:
        write_csv(output / f'{name}.csv', rows)
    (output / 'CONTRASTS.md').write_text(table_text(result), encoding='utf-8')
    (output / 'COMPARISON.svg').write_text(figure(result), encoding='utf-8')
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    args = parser.parse_args()
    bundle = write(args.output)
    print(f"Wrote {len(bundle['observations'])} reported conditions, {len(bundle['contrasts'])} dependent contrasts and {len(bundle['reversals'])} reversal diagnostics to {args.output}")


if __name__ == '__main__':
    main()

"""Condition-level duration/TDS response; exact, retrospective and nonscoring.

Offline CLI uses committed tables; the figure uses the existing [figures] extra.
No SD-to-uncertainty conversion, exact brew-ratio assumption or model fit.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from . import perticarini2024_pressure_grind as duration

ROOT = duration.ROOT
OUTPUT = ROOT / 'docs/analysis/sci_md_perticarini_pressure_chemistry_001'
PREDECESSOR = duration.OUTPUT
TASK = 'SCI-MD-PERTICARINI-PRESSURE-CHEMISTRY-001'
BASE = 'b3860d47ae6de6f6592add05cfac78fe9fb00487'
HASHES = ('2c5fae8319d41c690b7e23ea00ddfc722e08c01ebcd8f012dafb1820a8fc6703',
          '1b5cd8891472d2d432fcb96a59e167d8fcca8b8e70a0a75187d810bf8a8e4419')
ASSUMPTIONS = {
    'classification': ['G1', 'NO_GOVERNING_PHYSICS_CHANGE', 'RESEARCH_ONLY', 'RETROSPECTIVE',
                       'TARGET_EXPOSED', 'SOURCE_INTERNAL', 'NONSCORING'],
    'physical_validation': 'NOT_ESTABLISHED',
    'exposure': 'sources and preliminary contrasts inspected before PLAN; not preregistered or protected',
    'observation_unit': 'original published condition summary; join is not raw-shot pairing',
    'lineage': 'thesis Table 4.3 = Egidi Table 2; sole canonical identity egidi2024/table2',
    'chemical_operator': 'refractometer aliquot; three samples; C_bar=sum(C_j)/3; E_bar=sum(C_j/r_j)/3; r_j=dose_j/beverage_j',
    'sigma': 'reported TDS SD; estimator unspecified; descriptive, including printed zero',
    'native_format': 'all three tables: TDS means one decimal; EY means two; TDS SD format varies',
    'duration': duration.ASSUMPTIONS['duration'],
    'pressure': duration.ASSUMPTIONS['pressure'],
    'temperature': 'exact source setting; not measured puck temperature history',
    'grind': duration.ASSUMPTIONS['grind'],
    'box': 'C_i*=C_i+delta_i, |delta_i|<=h_C>=0 pp; tau_i*=tau_i+eta_i, |eta_i|<=h_tau>=0 s',
    'allowance': 'TOTAL declared per-condition perturbation; not measured error, SD, SE, CI, tolerance or added rounding allowance',
    'dependence': 'one common original-condition collection; no probabilistic independence; overlapping marginal extrema need not be jointly attainable',
    'strict_sign': 'combine coefficients first; [L0-s*h,L0+s*h]; nonzero L0,s>0: 0<=h<abs(L0)/s; equality unresolved',
    'ties': 'printed zero is not physical equality; structural identity s=0 has zero radius for all allowances',
    'illustration': 'h_C=0.05 pp and h_tau=0.5 s are conditional illustrations, not authenticated measurement bounds',
    'EY': 'published central-value comparisons only; uncertainty unqualified; no SD/h_C propagation or exact brew ratio',
    'unknown': ['raw replicate values', 'EY SDs', 'relevant covariance', 'actual condition masses',
                'authenticated joint timing/chemistry replicate model', 'rounding and measurement accuracy'],
    'excluded': ['model fit', 'causal/population law', 'duration-to-chemistry predictor', 'physical mechanism',
                 'rejection of duration-only physical law', 'measured flow from 40/tau',
                 'individual masses from EY/TDS means', 'sensory/practical equivalence',
                 'EWP comparison', 'production adoption', 'independent confirmation from TDS and EY'],
}


def display(value):
    """Exact terminating decimal where possible; otherwise an exact fraction."""
    q = Q(value)
    denominator, twos, fives = q.denominator, 0, 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        return str(q)
    digits = max(twos, fives)
    integer = abs(q.numerator) * (10 ** digits // q.denominator)
    raw = str(integer).zfill(digits + 1)
    if digits:
        raw = (raw[:-digits] + '.' + raw[-digits:]).rstrip('0').rstrip('.')
    return ('-' if q < 0 else '') + raw


def number(value):
    return {'exact': str(Q(value)), 'display': display(value)} if value is not None else None


def nonnegative(value):
    q = Q(value)
    if q < 0:
        raise ValueError('allowance must be nonnegative')
    return q


def box(terms, values, allowance, units):
    """Task-local exact box on original conditions, after shared-cell cancellation."""
    h = nonnegative(allowance)
    terms = duration.combine((1, terms))
    nominal = sum((a * Q(values[k]) for k, a in terms.items()), Q(0))
    norm = sum(abs(a) for a in terms.values())
    lo, hi = nominal - norm * h, nominal + norm * h
    nominal_status = ('structural_zero' if not norm else 'positive' if nominal > 0
                      else 'negative' if nominal < 0 else 'reported_zero')
    status = ('structural_zero' if not norm else 'positive' if lo > 0
              else 'negative' if hi < 0 else 'unresolved')
    return dict(units=units, nominal=number(nominal), lower=number(lo), upper=number(hi),
                radius=number(norm * h), allowance=number(h), coefficient_l1=norm,
                critical_allowance=number(abs(nominal) / norm) if norm else None,
                nominal_status=nominal_status, printed_tie=bool(norm and nominal == 0),
                conditional_status=status,
                strict_domain='0 <= h < critical_allowance' if nominal and norm else 'empty')


def duration_box(terms, values, allowance):
    """Reuse the predecessor's parameterized seconds contract, without chemical fields."""
    old = duration.enclosure(terms, values, nonnegative(allowance))
    out = box(terms, values, allowance, 's')
    for new, prior in [('nominal', 'nominal_s'), ('lower', 'lower_s'), ('upper', 'upper_s')]:
        if out[new]['exact'] != old[prior]:
            raise ValueError('Duration contract mismatch')
    if (out['conditional_status'] != old['box_status']
            or out['critical_allowance'] != number(old['critical_h_s'])):
        raise ValueError('Duration allowance contract mismatch')
    return out


def load_observations(data_root=None):
    """Augment accepted identities using full-key chemical joins, never row positions."""
    data_root = data_root or ROOT / 'puckworks/data'
    observations, inputs = duration.load_observations(data_root)
    chemistry = {}
    for dataset, filename, coffee in duration.INPUTS:
        with (data_root / filename).open(encoding='utf-8', newline='') as stream:
            for row in csv.DictReader(stream):
                fields = (('T_degC', 'p_bar', 'granulometry', 'TDS_pct', 'TDS_sd_pct', 'EY_pct')
                          if coffee == 'cibao' else
                          ('T [degC]', 'p [bar]', 'Granulometry', 'TDS [%]', 'TDS sigma', 'EY [%]'))
                t, p, g, c, sigma, ey = [row[k] for k in fields]
                key = (dataset, coffee, t, p, g.lower().replace(' ', '_'))
                if key in chemistry:
                    raise ValueError('Duplicate chemical condition')
                if Q(c) <= 0 or Q(ey) <= 0 or Q(sigma) < 0:
                    raise ValueError('Invalid chemical summary')
                chemistry[key] = dict(tds_mean_pct=c, tds_sd_pct=sigma, ey_mean_pct=ey,
                                      tds_mean_exact=str(Q(c)), tds_sd_exact=str(Q(sigma)),
                                      ey_mean_exact=str(Q(ey)), chemical_sample_n=3,
                                      sigma_estimator='UNKNOWN', ey_uncertainty='UNQUALIFIED')
    if set(chemistry) != duration.expected_keys():
        raise ValueError('Incomplete chemical support')
    return [{**o, **chemistry[duration.condition_key(o)]} for o in observations], inputs


def joint_label(tau, c, conditional=False):
    ts = {'negative': 'SHORTER', 'positive': 'LONGER', 'reported_zero': 'DURATION PRINTED TIE',
          'unresolved': 'DURATION SIGN UNRESOLVED'}
    cs = {'negative': 'LOWER TDS', 'positive': 'HIGHER TDS', 'reported_zero': 'TDS PRINTED TIE',
          'unresolved': 'TDS SIGN UNRESOLVED'}
    key = 'conditional_status' if conditional else 'nominal_status'
    return ts[tau[key]] + ' / ' + cs[c[key]]


def joint_region(tau, c):
    ties = [name for name, component in [('duration', tau), ('TDS', c)] if component['printed_tie']]
    return dict(empty=bool(ties), reason='printed zero: ' + ', '.join(ties) if ties else None,
                h_tau_lower_inclusive=number(0), h_C_lower_inclusive=number(0),
                h_tau_upper_exclusive=tau['critical_allowance'], h_C_upper_exclusive=c['critical_allowance'],
                assumptions='common_original_condition_boxes; declared total allowances; no physical uncertainty bound')


def compute(observations, tds_allowance='0.05', duration_allowance='0.5'):
    hc, ht = nonnegative(tds_allowance), nonnegative(duration_allowance)
    # Existing producer verifies exact support and supplies all accepted duration pair IDs/maps.
    old = duration.compute(observations)
    by_id = {o['source_condition_id']: o for o in observations}
    values = {field: {k: o[field] for k, o in by_id.items()}
              for field in ('tau_s', 'tds_mean_pct', 'ey_mean_pct')}
    comparisons = []
    lookup = {}
    for r in old['contrasts']:
        if r['kind'] != 'duration':
            continue
        terms = r['terms']
        low, high = (by_id[next(k for k, a in terms.items() if a == coefficient)] for coefficient in (-1, 1))
        tau = duration_box(terms, values['tau_s'], ht)
        c = box(terms, values['tds_mean_pct'], hc, 'percentage points')
        ey = sum((a * Q(values['ey_mean_pct'][k]) for k, a in terms.items()), Q(0))
        row = dict(comparison_id=r['contrast_id'].replace('D-', 'J-', 1),
                   predecessor_duration_id=r['contrast_id'], family=r['family'],
                   coffee_id=r['coffee_id'], coffee_label=r['coffee_label'],
                   temperature_degC=r['temperature_degC'], grind_id=r['grind_a'],
                   source_grind_label=duration.LABELS[r['grind_a']],
                   pressure_from_bar=r['pressure_from_bar'], pressure_to_bar=r['pressure_to_bar'],
                   orientation='higher nominal pressure minus lower', coefficients=terms,
                   low_condition_id=low['source_condition_id'], high_condition_id=high['source_condition_id'],
                   source_values={side: {k: o[k] for k in ('tau_s', 'tds_mean_pct', 'tds_sd_pct', 'ey_mean_pct')}
                                  for side, o in [('low', low), ('high', high)]},
                   duration=tau, tds=c, ey_delta_pp=number(ey), ey_uncertainty='UNQUALIFIED',
                   nominal_joint=joint_label(tau, c), conditional_joint=joint_label(tau, c, True),
                   joint_strict_region=joint_region(tau, c))
        comparisons.append(row)
        lookup[(r['coffee_id'], r['temperature_degC'], r['grind_a'], r['pressure_from_bar'], r['pressure_to_bar'])] = row
    interactions = []
    for coffee in duration.COFFEES:
        for grind in duration.GRINDS[1:4]:
            hot, cool = [lookup[(coffee, t, grind, '6', '9')] for t in ('93.4', '90.4')]
            terms = duration.combine((1, hot['coefficients']), (-1, cool['coefficients']))
            opposite = Q(hot['tds']['nominal']['exact']) * Q(cool['tds']['nominal']['exact']) < 0
            opposition = (number(min(Q(r['tds']['critical_allowance']['exact']) for r in (hot, cool)))
                          if opposite else None)
            both_shorter = opposite and all(r['duration']['nominal_status'] == 'negative' for r in (hot, cool))
            interactions.append(dict(
                interaction_id=f'IC-{coffee}-{grind}-T93.4minus90.4-P6to9',
                coffee_id=coffee, coffee_label=duration.COFFEES[coffee], grind_id=grind,
                source_grind_label=duration.LABELS[grind],
                orientation='(C9-C6) at 93.4 minus (C9-C6) at 90.4 degC',
                coefficients=terms, component_ids=[hot['comparison_id'], cool['comparison_id']],
                original_values_pct={k: values['tds_mean_pct'][k] for k in terms},
                tds=box(terms, values['tds_mean_pct'], hc, 'percentage points'),
                component_nominal_statuses=[r['tds']['nominal_status'] for r in (hot, cool)],
                component_conditional_statuses=[r['tds']['conditional_status'] for r in (hot, cool)],
                nominal_opposite_directions=opposite,
                opposite_directions_strict_region=dict(empty=not opposite, h_C_upper_exclusive=opposition,
                    domain='0 <= h_C < upper' if opposite else 'empty: no nominal opposite signs'),
                conditional_opposition='strict_opposite' if opposite and hc < Q(opposition['exact']) else 'unresolved' if opposite else 'nominal_opposition_not_established',
                shorter_with_opposite_tds_region=dict(empty=not both_shorter,
                    h_C_upper_exclusive=opposition if both_shorter else None,
                    h_tau_upper_exclusive=number(min(Q(r['duration']['critical_allowance']['exact']) for r in (hot, cool))) if both_shorter else None,
                    domain='0 <= h_C < upper AND 0 <= h_tau < upper' if both_shorter else 'empty: components do not both nominally shorten with opposite TDS')))
    identities = []
    for grind in (duration.GRINDS[0], duration.GRINDS[-1]):
        total, first, second = [lookup[('cibao', '93.4', grind, lo, hi)]
                                for lo, hi in [('6', '12'), ('9', '12'), ('6', '9')]]
        composed = duration.combine((1, first['coefficients']), (1, second['coefficients']))
        residual = duration.combine((1, total['coefficients']), (-1, composed))
        if composed != total['coefficients'] or residual:
            raise ValueError('Shared-condition cancellation failure')
        identities.append(dict(grind_id=grind, total_id=total['comparison_id'],
            component_ids=[first['comparison_id'], second['comparison_id']],
            composed_coefficients=composed, residual_coefficients=residual,
            tds_composed=box(composed, values['tds_mean_pct'], hc, 'percentage points'),
            tds_residual=box(residual, values['tds_mean_pct'], hc, 'percentage points'),
            duration_composed=duration_box(composed, values['tau_s'], ht),
            duration_residual=duration_box(residual, values['tau_s'], ht)))
    accounting = []
    for o in sorted(observations, key=lambda o: o['source_condition_id']):
        oid = o['source_condition_id']
        accounting.append(dict(source_condition_id=oid,
            primary_ids=[r['comparison_id'] for r in comparisons if r['family'] == 'primary' and oid in r['coefficients']],
            secondary_ids=[r['comparison_id'] for r in comparisons if r['family'] == 'secondary' and oid in r['coefficients']],
            interaction_ids=[r['interaction_id'] for r in interactions if oid in r['coefficients']]))
    primary = [r for r in comparisons if r['family'] == 'primary']
    return dict(comparisons=comparisons, interactions=interactions, arithmetic_identities=identities,
                condition_accounting=accounting,
                counts=dict(conditions=len(observations), primary=len(primary), secondary=len(comparisons)-len(primary),
                    interactions=len(interactions), primary_conditions=sum(bool(r['primary_ids']) for r in accounting),
                    nominal_primary_joint=dict(Counter(r['nominal_joint'] for r in primary)),
                    conditional_primary_joint=dict(Counter(r['conditional_joint'] for r in primary)),
                    conditional_interaction_signs=dict(Counter(r['tds']['conditional_status'] for r in interactions))))


def flat_comparison(r):
    row = {k: r[k] for k in ('comparison_id', 'predecessor_duration_id', 'family', 'coffee_label',
           'temperature_degC', 'source_grind_label', 'pressure_from_bar', 'pressure_to_bar',
           'low_condition_id', 'high_condition_id', 'coefficients')}
    for side, values in r['source_values'].items():
        row.update({side + '_' + k: v for k, v in values.items()})
    for field in ('duration', 'tds'):
        row[field + '_units'] = r[field]['units']
        for key, value in r[field].items():
            if isinstance(value, dict):
                row.update({f'{field}_{key}_{kind}': v for kind, v in value.items()})
        row.update({field + '_' + k: r[field][k] for k in ('nominal_status', 'printed_tie', 'conditional_status', 'coefficient_l1')})
    row.update(ey_delta_pp_exact=r['ey_delta_pp']['exact'], ey_delta_pp_display=r['ey_delta_pp']['display'],
               ey_uncertainty=r['ey_uncertainty'], nominal_joint=r['nominal_joint'],
               conditional_joint=r['conditional_joint'], joint_strict_region=r['joint_strict_region'])
    return row


def result_text(bundle):
    comparisons, interactions = bundle['comparisons'], bundle['interactions']
    hc = bundle['allowances']['h_C_pp']['display']
    ht = bundle['allowances']['h_tau_s']['display']
    lines = ['# SCI-MD-PERTICARINI-PRESSURE-CHEMISTRY-001', '',
        '**The reported shorter-duration response can accompany either lower or higher TDS.**', '',
        'G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /',
        'TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**', '',
        'This generated result joins the same 30 original conditions, counted once. The 14 primary',
        'pairs cover 28; two additional 12-bar conditions complete the union. The 14 + 6 + 4',
        'reporting slots are dependent contrasts, not 24 independent experiments or raw-shot pairs.',
        'Sources and preliminary contrasts were exposed before [PLAN](PLAN.md). This is not',
        'preregistration, held-out prediction or a protected score. [SOURCE_NOTES](SOURCE_NOTES.md)',
        'qualifies the operator, native formatting, lineage and unknown uncertainty.', '',
        f'Illustration: h_tau={ht} s and h_C={hc} pp, total per-condition allowances.',
        'Thresholds below are **exclusive**: strict signs require 0 ≤ h < threshold;',
        'at equality an interval touches zero and is unresolved. Threshold 0 denotes a printed',
        'tie with no strict sign even at zero allowance, never physical equality.', '',
        '## Complete primary 9-minus-6-bar pattern', '',
        'All pressure differences are higher nominal pressure minus lower; TDS/EY differences',
        'are percentage points (pp), not relative percent changes. The source pairs, TDS SDs,',
        'separate signs/tie flags and exact joint regions are in [primary.csv](primary.csv).', '']
    def table(rows):
        lines.extend(['| Coffee / °C | Native grind / bar difference | Δ duration (s) | Δ TDS (pp) | Δ EY (pp) | Nominal joint | Conditional joint | h_tau / h_C sign-loss thresholds |',
                      '|---|---|---:|---:|---:|---|---|---|'])
        for r in rows:
            t, c = r['duration'], r['tds']
            lines.append(f"| {r['coffee_label']} / {r['temperature_degC']} | {r['source_grind_label']} / {r['pressure_to_bar']}−{r['pressure_from_bar']} | {t['nominal']['display']} | {c['nominal']['display']} | {r['ey_delta_pp']['display']} | {r['nominal_joint']} | {r['conditional_joint']} | {t['critical_allowance']['display']} s / {c['critical_allowance']['display']} pp |")
        lines.append('')
    table([r for r in comparisons if r['family'] == 'primary'])
    lines += ['Nominal primary counts: ' + '; '.join(f'{n} {label}' for label, n in sorted(bundle['counts']['nominal_primary_joint'].items())) + '.', '',
              'Conditional primary counts at the displayed allowances: ' + '; '.join(f'{n} {label}' for label, n in sorted(bundle['counts']['conditional_primary_joint'].items())) + '.', '',
              'The exact strict two-component region for each nonzero pair is',
              '`0 <= h_tau < |delta_tau|/2 AND 0 <= h_C < |delta_C|/2`.',
              'A printed tie in either component makes that region empty; the other component',
              'retains its own status. [contrasts.json](contrasts.json) records all regions and reasons.', '',
              '## Pressure-by-temperature TDS interactions', '',
              'I_C = (C9−C6) at 93.4 °C minus (C9−C6) at 90.4 °C, directly from four',
              'original means. Each row has coefficient norm 4. Component IDs and their exact',
              'domain intersections are retained in [interactions.csv](interactions.csv).', '',
              '| Coffee | Native grind | I_C (pp) | Exact h_C sign-loss threshold (pp) | Conditional range (pp) | Conditional sign | Opposite component domain | Conditional opposition |',
              '|---|---|---:|---:|---|---|---|---|']
    for r in interactions:
        c = r['tds']
        region = r['opposite_directions_strict_region']
        domain = 'empty' if region['empty'] else '0 ≤ h_C < ' + region['h_C_upper_exclusive']['display']
        lines.append(f"| {r['coffee_label']} | {r['source_grind_label']} | {c['nominal']['display']} | {c['critical_allowance']['display']} | [{c['lower']['display']}, {c['upper']['display']}] | {c['conditional_status']} | {domain} | {r['conditional_opposition']} |")
    optimal = [r for r in comparisons if r['coffee_id'] == 'cibao' and r['grind_id'] == 'optimal']
    optimal_interaction = next(r for r in interactions if (r['coffee_id'], r['grind_id']) == ('cibao', 'optimal'))
    joint = optimal_interaction['shorter_with_opposite_tds_region']
    def centers(rows, field):
        return ' and '.join(r[field]['nominal']['display'] for r in rows)
    lines += ['', f"Cibao Optimal components `{optimal[0]['comparison_id']}` and",
        f"`{optimal[1]['comparison_id']}` report duration changes {centers(optimal, 'duration')} s,",
        f"TDS changes {centers(optimal, 'tds')} pp and published EY changes "
        + ' and '.join(r['ey_delta_pp']['display'] for r in optimal) + ' pp.',
        'Both shorter-duration / opposite-TDS directions persist together exactly for',
        f"**0 ≤ h_tau < {joint['h_tau_upper_exclusive']['display']} s and 0 ≤ h_C < {joint['h_C_upper_exclusive']['display']} pp**.",
        'Equal printed shortening does not establish equal actual shortening.',
        'Their current conditional duration/TDS ranges are respectively:', '']
    for r in optimal:
        t, c = r['duration'], r['tds']
        lines.append(f"- {r['temperature_degC']} °C: [{t['lower']['display']}, {t['upper']['display']}] s; [{c['lower']['display']}, {c['upper']['display']}] pp.")
    fine = next(r for r in interactions if (r['coffee_id'], r['grind_id']) == ('modoetia', 'fine'))
    fine_boundary = fine['opposite_directions_strict_region']['h_C_upper_exclusive']['display']
    by_id = {r['comparison_id']: r for r in comparisons}
    hot_fine = by_id[fine['component_ids'][0]]
    hot_coarse = next(r for r in comparisons if (r['coffee_id'], r['temperature_degC'], r['grind_id']) == ('modoetia', '93.4', 'coarse'))
    long = next(r for r in comparisons if r['family'] == 'primary' and r['duration']['nominal_status'] == 'positive')
    lines += ['', f"Modœtia Fine has I_C={fine['tds']['nominal']['display']} pp "
        f"(threshold {fine['tds']['critical_allowance']['display']} pp), while its supporting",
        f"`{fine['component_ids'][0]}` and `{fine['component_ids'][1]}` components",
        f"oppose strictly only at h_C<{fine_boundary} pp. A strict interaction at h_C={fine_boundary}",
        f"does not establish strict opposition: the hot {hot_fine['tds']['nominal']['display']} pp component touches zero.",
        f"The hot Modœtia Coarse {hot_coarse['tds']['nominal']['display']} pp component also touches zero at that allowance.",
        f"A {long['duration']['nominal']['display']} s duration contrast touches zero at h_tau={long['duration']['critical_allowance']['display']} s.",
        'All such zero-touch cases remain unresolved.', '',
        '## Secondary extreme-grind comparisons', '',
        'Only Cibao / 93.4 °C; these four rows do not enlarge the primary pressure family.',
        'Full source pairs and statuses: [secondary.csv](secondary.csv).', '']
    table([r for r in comparisons if r['family'] == 'secondary'])
    extra = next(r for r in comparisons if r['grind_id'] == 'extra_fine' and r['pressure_from_bar'] == '9')
    lines += [f"Extra Fine 12−9 has {extra['tds']['nominal']['display']} pp TDS and {extra['ey_delta_pp']['display']} pp EY: the differing chemical",
        'directions are retained. Published EY is a related central endpoint with uncertainty',
        'unqualified here; it is not independent confirmation and is not inferred from TDS.', '',
        'At each extreme grind, (12−6)=(12−9)+(9−6). Shared P9 coefficients cancel:',
        'the composed TDS radius is 2*h_C, and the duration radius is 2*h_tau.',
        'Both identity residuals have coefficient norm/radius zero at every allowance,',
        'with threshold null, not a division by zero or an extra observation.', '',
        '![Four primary coffee/temperature panels](COMPARISON.svg)', '',
        '## Scientific increment and limits', '',
        'The chemical columns add the joint direction and temperature-conditioned contrast',
        'pattern to the [accepted duration result](../sci_md_perticarini_pressure_grind_001/RESULT.md).',
        'Duration-only agreement and broad per-grind EY/TDS range bracketing leave this',
        'condition-level joint response untested. This bundle supplies an observation target',
        'for future comparisons; it fits no model and rejects no physical duration-only law.', '',
        'All exact boxes combine original-condition coefficients before taking their L1 norm.',
        'The allowances are a deterministic convention, not experimental error, rounding accuracy,',
        'SD, SE, CI, statistical significance or practical tolerance. Shared variables mean',
        'arbitrary marginal extrema need not be jointly attainable; no probabilistic independence',
        'is asserted. Reported TDS SDs, including zeros, remain descriptive metadata in the',
        'tables. There is no SD-to-mean conversion or EY uncertainty propagation.', '',
        'The sources measure a prepared beverage aliquot by refractometer; C and samplewise',
        'calculated EY are averaged over three chemical extractions. Individual samples, EY SDs,',
        'covariance, condition masses and authenticated joint timing/chemistry replicates are',
        'unavailable. Nominal dose/beverage targets do not imply E_bar=2*C_bar.', '',
        'No causal pressure effect, experimentally resolved reversal, population law, mechanism,',
        'shot covariance or causal duration-to-chemistry relation follows. Nominal pressure is',
        'not measured puck pressure drop; temperature settings are not puck histories; duration',
        'is not instantaneous flow or residence time. No flow from 40g/duration, individual',
        'masses from mean ratios, cross-coffee particle-size mapping, equality, practical',
        'equivalence, sensory value, production adequacy or EWP comparison is established.',
        'Unknown experimental uncertainty remains unknown; existing range-bracket qualification,',
        'models/defaults/pins and predecessor artifacts are unchanged.',
        '**PHYSICAL_VALIDATION=NOT_ESTABLISHED.**', '']
    return '\n'.join(lines)


def figure(bundle, path):
    """Matplotlib SVG, exact data binding; floats only position glyphs, never classify."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    with matplotlib.rc_context({'svg.hashsalt': TASK, 'svg.fonttype': 'none', 'font.size': 10,
                                'font.family': 'DejaVu Sans'}):
        fig, axes = plt.subplots(2, 2, figsize=(12, 9), sharex=True, sharey=True)
        # Callout positions are in points only; data centers and extents never jitter.
        offsets = {('cibao', '93.4'): [(16, 20), (16, -27), (-24, 20), (20, 16), (16, -29)],
                   ('cibao', '90.4'): [(14, 8), (14, 16), (14, -23)],
                   ('modoetia', '93.4'): [(16, 12), (16, 12), (16, -19)],
                   ('modoetia', '90.4'): [(16, -18), (16, 15), (16, -23)]}
        primary = [r for r in bundle['comparisons'] if r['family'] == 'primary']
        ht = Q(bundle['allowances']['h_tau_s']['exact'])
        hc = Q(bundle['allowances']['h_C_pp']['exact'])
        # Include the full requested box even for user-supplied large allowances.
        xmin = min(Q(r['duration']['lower']['exact']) for r in primary)
        xmax = max(Q(r['duration']['upper']['exact']) for r in primary)
        ymin = min(Q(r['tds']['lower']['exact']) for r in primary)
        ymax = max(Q(r['tds']['upper']['exact']) for r in primary)
        for ax, stratum in zip(axes.flat, duration.STRATA):
            rows = [r for r in primary if (r['coffee_id'], r['temperature_degC']) == stratum]
            ax.axhline(0, color='#525b65', lw=1)
            ax.axvline(0, color='#525b65', lw=1)
            ax.grid(alpha=.15)
            ax.set_axisbelow(True)
            for r, offset in zip(rows, offsets[stratum]):
                x, y = float(Q(r['duration']['nominal']['exact'])), float(Q(r['tds']['nominal']['exact']))
                strict = all(r[k]['conditional_status'] in ('positive', 'negative') for k in ('duration', 'tds'))
                color = '#21618c' if strict else '#ad571f'
                artist = ax.errorbar(x, y, xerr=float(2*ht), yerr=float(2*hc), fmt='o',
                                    color=color, capsize=3, ms=5, lw=1.2)
                artist.lines[0].set_gid(r['comparison_id'])
                ax.annotate(r['source_grind_label'], (x, y), xytext=offset, textcoords='offset points',
                            ha='left' if offset[0] >= 0 else 'right', fontsize=9,
                            arrowprops=dict(arrowstyle='-', lw=.6, color=color), color=color)
            ax.set_title(f'{duration.COFFEES[stratum[0]]} · {stratum[1]} °C')
            ax.set_xlim(float(min(xmin, 0))-1.5, float(max(xmax, 0))+2.8)
            ax.set_ylim(float(min(ymin, 0))-.15, float(max(ymax, 0))+.18)
            ax.set_xlabel('Δ reported duration (s), 9 minus 6 bar')
            ax.set_ylabel('Δ reported TDS (percentage points)')
        fig.suptitle('Reported duration and chemical endpoint response\nPrimary nominal 6→9 bar · all 14 native-grind comparisons', fontsize=15, y=.97)
        fig.text(.5, .07, f'CONDITIONAL PERTURBATION RANGES: pair half-widths ±{display(2*ht)} s and ±{display(2*hc)} pp', ha='center', weight='bold')
        fig.text(.5, .043, f'Total per-condition allowances: h_tau={display(ht)} s; h_C={display(hc)} pp. Not experimental error bars or sample SDs.', ha='center', fontsize=10)
        fig.text(.5, .019, 'Blue: both signs strict at these allowances. Brown: at least one unresolved. SOURCE_INTERNAL · PHYSICAL_VALIDATION=NOT_ESTABLISHED', ha='center', fontsize=9)
        fig.subplots_adjust(left=.09, right=.98, bottom=.17, top=.85, hspace=.35, wspace=.24)
        fig.savefig(path, format='svg', metadata={'Date': None, 'Creator': TASK})
        plt.close(fig)
    # Bind exact values and extents to the corresponding plotted points for offline QA.
    tree = ET.parse(path)
    for r in primary:
        group = next(g for g in tree.iter() if g.get('id') == r['comparison_id'])
        for field in ('duration', 'tds'):
            for k in ('nominal', 'lower', 'upper'):
                group.set(f'data-{field}-{k}', r[field][k]['exact'])
    tree.write(path, encoding='utf-8', xml_declaration=True)


def write(output=OUTPUT, tds_allowance='0.05', duration_allowance='0.5', make_figure=True):
    hc, ht = nonnegative(tds_allowance), nonnegative(duration_allowance)
    observations, inputs = load_observations()
    if tuple(r['file_sha256'] for r in inputs) != HASHES:
        raise ValueError('Canonical source bytes differ; investigate before generating results')
    result = compute(observations, hc, ht)
    bundle = dict(schema_version=1, task_id=TASK, actual_base=BASE,
                  sources=duration.SOURCES, inputs=inputs, assumptions=ASSUMPTIONS,
                  allowances=dict(h_C_pp=number(hc), h_tau_s=number(ht)),
                  observations=observations, **result)
    # Accepted evidence dependencies; no source PDF or network reads.
    preserved = [PREDECESSOR / name for name in ('SOURCE_NOTES.md', 'RESULT.md', 'observations.csv', 'contrasts.json')]
    preserved.append(Path(duration.__file__))
    bundle['predecessor_sha256'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in preserved}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'contrasts.json').write_text(duration.json_text(bundle), encoding='utf-8')
    duration.write_csv(output / 'observations.csv', observations)
    for family in ('primary', 'secondary'):
        duration.write_csv(output / f'{family}.csv', [flat_comparison(r) for r in result['comparisons'] if r['family'] == family])
    duration.write_csv(output / 'interactions.csv', result['interactions'])
    (output / 'RESULT.md').write_text(result_text(bundle), encoding='utf-8')
    if make_figure:
        figure(bundle, output / 'COMPARISON.svg')
    return bundle


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--tds-allowance-pp', default='0.05')
    parser.add_argument('--duration-allowance-s', default='0.5')
    parser.add_argument('--no-figure', action='store_true', help='numerical regeneration without optional matplotlib')
    args = parser.parse_args()
    try:
        bundle = write(args.output, args.tds_allowance_pp, args.duration_allowance_s, not args.no_figure)
    except (ValueError, ZeroDivisionError) as error:
        parser.error(str(error))
    print(json.dumps(bundle['counts'], ensure_ascii=False, sort_keys=True))


if __name__ == '__main__':
    main()

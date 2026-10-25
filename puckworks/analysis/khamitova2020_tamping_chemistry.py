"""Source-specific, descriptive representation cost for Khamitova Tables 5.2–5.5.

Offline reproduction from unchanged CSVs and visually audited source precision.
All decision arithmetic is Fraction. JSON preserves exact rational strings; CSV
bounds are rounded outwards to 12 decimal places. No experimental error model,
acceptance threshold, fitted law, causal inference or physical validation.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as Q
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / 'docs/analysis/sci_md_khamitova_tamping_chemistry_001'
DATA = ROOT / 'puckworks/data/khamitova2020'
FORCES = (10, 15, 20, 30)
ANALYTES = ('total CQA', 'caffeine', 'trigonelline', 'nicotinic acid')
TEMPERATURES = (88, 93, 98)
PRESSURES = (7, 9, 11)
SUPPORTED = 'SUPPORTED'
UNSUPPORTED = 'UNSUPPORTED'
BASIS = ('Reported amount per reference 40 mL; 72 extractions / 36 duplicated '
         'configurations, not 144 independent extractions. Mean/RSD aggregation '
         'unresolved. Fixed-grind assertion coexists with manual tuning ambiguity. '
         'Reference volume is not an authenticated measured cup volume. '
         'Decimal rounding is a reporting convention; RSD scales are not confidence '
         'intervals. No causal, population, practical-adequacy or equivalence claim. '
         'PHYSICAL_VALIDATION=NOT_ESTABLISHED.')


def number(value):
    """Finite exact value or unsupported; never propagate NaN/Infinity."""
    if value is None or isinstance(value, bool):
        return None
    try:
        return Q(str(value))
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def interval(value, places):
    """Closed half-last-printed-place box; missing precision does not erase mean."""
    if value is None or not isinstance(places, int) or isinstance(places, bool) or places < 0:
        return None
    h = Q(1, 2 * 10**places)
    return value - h, value + h


def range_bounds(boxes):
    """Sharp extrema of the realizable range, including unequal-width intervals."""
    if len(boxes) != 4 or any(b is None or b[0] > b[1] for b in boxes):
        raise ValueError('Four ordered intervals required')
    lo = max(Q(0), max(b[0] for b in boxes) - min(b[1] for b in boxes))
    hi = max(Q(0), max(boxes[i][1] - boxes[j][0]
                      for i in range(4) for j in range(4) if i != j))
    return lo, hi


def rsd_diagnostic(y, r, y_boxes, r_boxes):
    """Pairwise intersection criterion; interval enclosure relaxes shared y."""
    result = dict(rsd_nominal_status=UNSUPPORTED, reported_rsd_scales=None,
                  lambda_star=None, lambda_attaining_pairs=None,
                  rsd_rounding_status=UNSUPPORTED, lambda_lower=None, lambda_upper=None)
    if any(v is None or v <= 0 for v in y) or any(v is None or v < 0 for v in r):
        return result
    s = [a*b/100 for a, b in zip(y, r)]
    pairs = list(combinations(range(4), 2))
    ratios = [abs(y[i]-y[j])/(s[i]+s[j]) if s[i]+s[j] else
              (Q(0) if y[i] == y[j] else None) for i, j in pairs]
    unbounded = any(v is None for v in ratios)
    lam = None if unbounded else max(ratios)
    result.update(rsd_nominal_status='UNBOUNDED_ZERO_SCALES' if unbounded else 'FINITE',
                  reported_rsd_scales=s, lambda_star=lam,
                  lambda_attaining_pairs=[[FORCES[i], FORCES[j]] for (i, j), v in zip(pairs, ratios)
                                          if v == lam])
    if any(b is None or b[0] <= 0 for b in y_boxes) or any(b is None for b in r_boxes):
        return result
    rb = [(max(Q(0), b[0]), b[1]) for b in r_boxes]
    sb = [(a[0]*b[0]/100, a[1]*b[1]/100) for a, b in zip(y_boxes, rb)]
    lower, upper = [], []
    for i, j in pairs:
        a, b = y_boxes[i], y_boxes[j]
        nlo = max(Q(0), a[0]-b[1], b[0]-a[1])
        nhi = max(abs(a[1]-b[0]), abs(b[1]-a[0]))
        dlo, dhi = sb[i][0]+sb[j][0], sb[i][1]+sb[j][1]
        # Under half-place boxes around valid nonnegative RSDs, dhi is positive.
        lower.append(nlo/dhi)
        upper.append(nhi/dlo if dlo else (Q(0) if nhi == 0 else None))
    result.update(lambda_lower=max(lower),
                  lambda_upper=None if None in upper else max(upper),
                  rsd_rounding_status='CONSERVATIVE_UNBOUNDED_UPPER_ENCLOSURE' if None in upper
                  else 'FINITE_CONSERVATIVE_ENCLOSURE')
    return result


def analyze_block(means, rsds=None, mean_places=None, rsd_places=None):
    """Return separate support for endpoint, four-level, normalization and RSD work.

    Inputs are keyed by nominal force. Missing/invalid means retain the request;
    an incomplete four-level range is exported only as a nominal lower bound.
    """
    rsds, mean_places, rsd_places = rsds or {}, mean_places or {}, rsd_places or {}
    y = [number(means.get(f)) for f in FORCES]
    r = [number(rsds.get(f)) for f in FORCES]
    boxes = [interval(v, mean_places.get(f)) for f, v in zip(FORCES, y)]
    rb = [interval(v, rsd_places.get(f)) for f, v in zip(FORCES, r)]
    out = dict(means=y, rsd_percent=r, supported_mean_count=sum(v is not None for v in y),
               endpoint_status=UNSUPPORTED, endpoint_normalization_status=UNSUPPORTED,
               Delta=None, Percent_change=None, Delta_lower=None, Delta_upper=None,
               Percent_change_lower=None, Percent_change_upper=None,
               endpoint_rounding_status=UNSUPPORTED, endpoint_normalized_rounding_status=UNSUPPORTED,
               representation_status=UNSUPPORTED, representation_normalization_status=UNSUPPORTED,
               R=None, E=None, c_star=None, E_percent_reference=None,
               minimum_forces=None, maximum_forces=None, interior_minimum_forces=None,
               interior_maximum_forces=None, endpoint_missed_range=None,
               partial_range_lower_bound=None, R_lower=None, R_upper=None, E_lower=None, E_upper=None,
               E_percent_reference_lower=None, E_percent_reference_upper=None,
               representation_rounding_status=UNSUPPORTED,
               representation_normalized_rounding_status=UNSUPPORTED)
    if y[0] is not None and y[3] is not None:
        d = y[3]-y[0]
        out.update(endpoint_status=SUPPORTED, Delta=d)
        if y[0] > 0:
            out.update(endpoint_normalization_status=SUPPORTED, Percent_change=100*d/y[0])
        if boxes[0] is not None and boxes[3] is not None:
            a, b = boxes[0], boxes[3]
            dl, du = b[0]-a[1], b[1]-a[0]
            status = ('POSITIVE_UNDER_ROUNDING_CONVENTION' if dl > 0 else
                      'NEGATIVE_UNDER_ROUNDING_CONVENTION' if du < 0 else 'ROUNDING_UNRESOLVED')
            out.update(Delta_lower=dl, Delta_upper=du, endpoint_rounding_status=status)
            if a[0] > 0 and b[0] > 0:
                out.update(Percent_change_lower=100*(b[0]/a[1]-1),
                           Percent_change_upper=100*(b[1]/a[0]-1),
                           endpoint_normalized_rounding_status=SUPPORTED)
    valid = [v for v in y if v is not None]
    if len(valid) != 4:
        if valid:
            out['partial_range_lower_bound'] = max(valid)-min(valid)
    else:
        mn, mx = min(y), max(y)
        e = (mx-mn)/2
        low_forces = [f for f, v in zip(FORCES, y) if v == mn]
        high_forces = [f for f, v in zip(FORCES, y) if v == mx]
        out.update(representation_status=SUPPORTED, R=mx-mn, E=e, c_star=(mx+mn)/2,
                   minimum_forces=low_forces, maximum_forces=high_forces,
                   interior_minimum_forces=[f for f in low_forces if f in (15, 20)],
                   interior_maximum_forces=[f for f in high_forces if f in (15, 20)],
                   endpoint_missed_range=mx-mn-abs(y[3]-y[0]))
        if y[0] > 0:
            out.update(representation_normalization_status=SUPPORTED, E_percent_reference=100*e/y[0])
        if all(b is not None for b in boxes):
            rl, ru = range_bounds(boxes)
            el, eu = rl/2, ru/2
            out.update(R_lower=rl, R_upper=ru, E_lower=el, E_upper=eu,
                       representation_rounding_status='POSITIVE_LOWER_BOUND_UNDER_ROUNDING_CONVENTION'
                       if el > 0 else 'ZERO_NOT_EXCLUDED_UNDER_ROUNDING_CONVENTION')
            if boxes[0][0] > 0:
                out.update(E_percent_reference_lower=100*el/boxes[0][1],
                           E_percent_reference_upper=100*eu/boxes[0][0],
                           representation_normalized_rounding_status='FINITE_CONSERVATIVE_ENCLOSURE')
    out.update(rsd_diagnostic(y, r, boxes, rb))
    return out


def load_observations(bundle=BUNDLE, data=DATA):
    """Join audited source strings to unchanged CSV values; preserve every key."""
    observations, keys, files = [], set(), {}
    with (bundle/'cell_audit.csv').open(encoding='utf-8', newline='') as f:
        audit = list(csv.DictReader(f))
    for row in audit:
        record = dict(row)
        for field in ('temperature_C', 'pressure_bar', 'tamp_force_kgf', 'printed_page',
                      'pdf_page', 'csv_row_1based'):
            record[field] = int(row[field])
        key = tuple(record[k] for k in ('analyte', 'temperature_C', 'pressure_bar', 'tamp_force_kgf'))
        if key in keys:
            raise ValueError(f'Duplicate observation: {key}')
        keys.add(key)
        filename = row['csv_file']
        if filename not in files:
            with (data/filename).open(newline='') as f:
                files[filename] = list(csv.DictReader(f))
        source = files[filename][record['csv_row_1based']-2]
        if (int(source['temperature_C']), int(source['pressure_bar'])) != key[1:3]:
            raise ValueError(f'CSV row mapping mismatch: {key}')
        for name, suffix in [('amount', 'mg_per_40ml'), ('concentration', 'mg_per_ml'), ('rsd', 'RSD_pct')]:
            s = row[f'{name}_string']
            v = number(s)
            csv_string = source[f'{key[3]}kgF_{suffix}']
            if v != number(csv_string):
                raise ValueError(f'Audit/CSV disagreement: {key} {name}')
            record[f'{name}_csv_string'] = csv_string
            record[name] = v
            places = row[f'{name}_decimal_places']
            places = int(places) if places else None
            if places is not None and ('.' not in s or len(s.split('.')[1]) != places):
                raise ValueError(f'Precision mismatch: {key} {name}')
            record[f'{name}_decimal_places'] = places
        record['mean_support'] = (SUPPORTED if row['mean_support'] == SUPPORTED
                                  and record['amount'] is not None else UNSUPPORTED)
        record['rsd_support'] = (SUPPORTED if row['rsd_support'] == SUPPORTED
                                 and record['rsd'] is not None and record['rsd'] >= 0 else UNSUPPORTED)
        for name in ('amount', 'concentration', 'rsd'):
            record[f'{name}_rounding_support'] = (SUPPORTED if row['precision_support'] == SUPPORTED
                and interval(record[name], record[f'{name}_decimal_places']) is not None else UNSUPPORTED)
        record['precision_support'] = (SUPPORTED if all(record[f'{name}_rounding_support'] == SUPPORTED
            for name in ('amount', 'concentration', 'rsd')) else UNSUPPORTED)
        a = interval(record['amount'], record['amount_decimal_places'])
        c = interval(record['concentration'], record['concentration_decimal_places'])
        consistent = None if a is None or c is None else max(a[0], 40*c[0]) <= min(a[1], 40*c[1])
        record['related_unit_status'] = (UNSUPPORTED if consistent is None else
                                        'INTERSECTS_UNDER_ROUNDING_CONVENTION' if consistent else
                                        'SOURCE_PAIR_INCONSISTENT_UNDER_ROUNDING_CONVENTION')
        record['qualification'] = ('REFERENCE_40_ML; AGGREGATION_UNRESOLVED; GRIND_TUNING_AMBIGUITY'
                                   + ('; SOURCE_UNIT_PAIR_MISMATCH' if consistent is False else ''))
        record['amount_unit'] = 'reported amount per reference 40 mL (mg)'
        record['cell_locator'] = (f"Table {row['table']}; row {row['source_row_label']}; "
                                  f"group {row['source_force_label']}; columns mg/40ml, mg/ml, RSD")
        observations.append(record)
    expected = set(product(ANALYTES, TEMPERATURES, PRESSURES, FORCES))
    if keys != expected:
        raise ValueError('Audit must retain exactly all 144 requested keys')
    return sorted(observations, key=lambda r: (ANALYTES.index(r['analyte']),
                   r['temperature_C'], r['pressure_bar'], r['tamp_force_kgf']))


def build_report(bundle=BUNDLE, data=DATA):
    observations = load_observations(bundle, data)
    results = []
    for analyte, temp, pressure in product(ANALYTES, TEMPERATURES, PRESSURES):
        rows = [r for r in observations if (r['analyte'], r['temperature_C'], r['pressure_bar'])
                == (analyte, temp, pressure)]
        def values(field):
            support = {'amount': 'mean_support', 'rsd': 'rsd_support',
                       'amount_decimal_places': 'amount_rounding_support',
                       'rsd_decimal_places': 'rsd_rounding_support'}[field]
            return {r['tamp_force_kgf']: r[field] if r[support] == SUPPORTED else None for r in rows}
        result = dict(analyte=analyte, temperature_C=temp, pressure_bar=pressure,
                      native_unit='mg per reference 40 mL', force_labels_kgf=list(FORCES))
        result.update(analyze_block(values('amount'), values('rsd'),
                                    values('amount_decimal_places'), values('rsd_decimal_places')))
        result['source_qualifications'] = sorted({r['qualification'] for r in rows})
        results.append(result)
    identities = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(data.glob('*.csv'))}
    for name in ('cell_audit.csv', 'ground_audit.csv', 'source_metadata.json'):
        identities[name] = hashlib.sha256((bundle/name).read_bytes()).hexdigest()
    count = lambda field, value: sum(r[field] == value for r in results)
    return dict(task='SCI-MD-KHAMITOVA-TAMPING-CHEMISTRY-001', dataset='khamitova2020/tamping',
        classification='G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / '
                       'TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING',
        PHYSICAL_VALIDATION='NOT_ESTABLISHED', observation_basis=BASIS,
        numeric_encoding='Exact rational strings in JSON; CSV nominal nearest and bounds outward at 12 decimals',
        rounding_convention='Closed +/- half a unit in each last printed decimal place; no confidence coverage',
        enclosure_qualification='E bounds optimize separately for each realization, not one fixed constant; '
            'normalized E and lambda enclosures relax shared variables and are not claimed sharp or jointly attainable',
        source_sha256=json.loads((bundle/'source_metadata.json').read_text())['pdf']['sha256'],
        input_sha256=identities,
        coverage=dict(observation_requests=144, observations=len(observations), endpoint_requests=36,
            mean_supported=sum(r['mean_support'] == SUPPORTED for r in observations),
            rsd_supported=sum(r['rsd_support'] == SUPPORTED for r in observations),
            mean_rounding_metadata_supported=sum(r['amount_rounding_support'] == SUPPORTED for r in observations),
            rsd_rounding_metadata_supported=sum(r['rsd_rounding_support'] == SUPPORTED for r in observations),
            four_level_requests=36, endpoint_supported=count('endpoint_status', SUPPORTED),
            four_level_supported=count('representation_status', SUPPORTED),
            endpoint_normalization_supported=count('endpoint_normalization_status', SUPPORTED),
            representation_normalization_supported=count('representation_normalization_status', SUPPORTED),
            endpoint_rounding_supported=36-count('endpoint_rounding_status', UNSUPPORTED),
            representation_rounding_supported=36-count('representation_rounding_status', UNSUPPORTED),
            endpoint_normalized_rounding_supported=count('endpoint_normalized_rounding_status', SUPPORTED),
            representation_normalized_rounding_supported=count('representation_normalized_rounding_status', 'FINITE_CONSERVATIVE_ENCLOSURE'),
            rsd_nominal_finite=count('rsd_nominal_status', 'FINITE'),
            rsd_rounding_finite=count('rsd_rounding_status', 'FINITE_CONSERVATIVE_ENCLOSURE')),
        observations=observations, blocks=results)


def exact(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {k: exact(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [exact(v) for v in value]
    return value


def decimal_view(q, direction=0, places=12):
    """Exact integer rounding: floor lower, ceil upper, nearest nominal."""
    scale = 10**places
    scaled = q*scale
    if direction < 0:
        n = scaled.numerator // scaled.denominator
    elif direction > 0:
        n = -((-scaled.numerator) // scaled.denominator)
    else:
        n = (scaled + Q(1, 2)).numerator // (scaled + Q(1, 2)).denominator
    sign = '-' if n < 0 else ''
    integer, fraction = divmod(abs(n), scale)
    return (f'{sign}{integer}.{fraction:0{places}d}').rstrip('0').rstrip('.')


def write_csv(path, rows):
    def cell(key, value):
        if isinstance(value, Q):
            return decimal_view(value, -1 if key.endswith('_lower') else 1 if key.endswith('_upper') else 0)
        if isinstance(value, (list, dict)):
            return json.dumps(exact(value), ensure_ascii=False, separators=(',', ':'))
        return value
    with path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows({k: cell(k, v) for k, v in r.items()} for r in rows)


def write_report(output, plot=False):
    report = build_report()
    output.mkdir(parents=True, exist_ok=True)
    (output/'results.json').write_text(json.dumps(exact(report), indent=2, ensure_ascii=False,
                                                allow_nan=False)+'\n', encoding='utf-8')
    write_csv(output/'observations.csv', report['observations'])
    write_csv(output/'representation.csv', report['blocks'])
    fields = ('analyte', 'temperature_C', 'pressure_bar', 'native_unit', 'means',
              'endpoint_status', 'endpoint_normalization_status', 'Delta', 'Percent_change',
              'Delta_lower', 'Delta_upper', 'Percent_change_lower', 'Percent_change_upper',
              'endpoint_rounding_status', 'endpoint_normalized_rounding_status',
              'endpoint_missed_range', 'source_qualifications')
    write_csv(output/'endpoints.csv', [{k: r[k] for k in fields} for r in report['blocks']])
    if plot:
        plot_report(report, output/'chemistry.png')
    return report


def plot_report(report, output):
    """Display only; matplotlib is the existing optional figures extra."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    colors = ('#0072B2', '#D55E00', '#009E73')
    fig, axes = plt.subplots(4, 4, figsize=(17, 15), gridspec_kw={'width_ratios': [1, 1, 1, 1.15]})
    for ai, analyte in enumerate(ANALYTES):
        blocks = [r for r in report['blocks'] if r['analyte'] == analyte]
        all_y = [float(v) for r in blocks for v in r['means']]
        span = max(all_y)-min(all_y)
        for ti, temp in enumerate(TEMPERATURES):
            ax = axes[ai, ti]
            for pi, pressure in enumerate(PRESSURES):
                r = next(b for b in blocks if b['temperature_C'] == temp and b['pressure_bar'] == pressure)
                y = [float(v) for v in r['means']]
                obs = [o for o in report['observations'] if o['analyte'] == analyte
                       and o['temperature_C'] == temp and o['pressure_bar'] == pressure]
                h = [float(Q(1, 2*10**o['amount_decimal_places'])) for o in obs]
                ax.plot(FORCES, y, 'o-', color=colors[pi], markersize=4, linewidth=1.2)
                ax.errorbar(FORCES, y, yerr=h, fmt='none', ecolor='black', capsize=3, linewidth=1)
            ax.set_title(f'{analyte} · {temp} °C', fontsize=11)
            ax.set_xticks(FORCES)
            ax.set_ylim(min(all_y)-0.08*span, max(all_y)+0.08*span)
            ax.grid(alpha=0.18)
            if ti == 0:
                ax.set_ylabel('Reported mg per reference 40 mL')
            if ai == 3:
                ax.set_xlabel('Nominal tamping force (kgF)')
        ax = axes[ai, 3]
        for j, r in enumerate(blocks):
            d = float(r['Delta'])
            ax.errorbar(d, j, xerr=[[d-float(r['Delta_lower'])], [float(r['Delta_upper'])-d]],
                        fmt='o', color=colors[PRESSURES.index(r['pressure_bar'])],
                        ecolor='black', capsize=3, markersize=4)
        ax.set_yticks(range(9), [f"{r['temperature_C']} °C / {r['pressure_bar']} bar" for r in blocks], fontsize=8)
        ax.invert_yaxis()
        ax.axvline(0, color='gray', linestyle=':', linewidth=1)
        ax.set_title('Fixed 30 − 10 kgF contrast', fontsize=11)
        ax.set_xlabel('Δ (reported mg per reference 40 mL)')
        ax.grid(axis='x', alpha=0.18)
    fig.suptitle('Khamitova 2020 · all 144 reported means and 36 fixed endpoint contrasts', fontsize=17, y=0.99)
    handles = [Line2D([0], [0], color=c, marker='o', label=f'{p} bar') for c, p in zip(colors, PRESSURES)]
    handles += [Line2D([0], [0], color='black', marker='|', linestyle='none', label='Half-last-place rounding (often smaller than markers)')]
    fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.5, 0.967), ncol=4, frameon=False)
    fig.text(0.5, 0.012, 'Lines connect nominal force labels only. Black caps: conditional decimal rounding, not experimental uncertainty. No RSD bars.\n'
             '72 extractions / 36 duplicated configurations; mean/RSD aggregation unresolved. Fixed-grind assertion and tuning ambiguity retained.\n'
             'Reference 40 mL is not authenticated cup volume. Descriptive benchmark only; PHYSICAL_VALIDATION=NOT_ESTABLISHED.',
             ha='center', fontsize=9)
    fig.tight_layout(rect=(0, 0.067, 1, 0.94), h_pad=2, w_pad=1.5)
    fig.savefig(output, dpi=150, metadata={'Software': 'Puckworks Khamitova descriptive analysis'})
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    report = write_report(args.output, args.plot)
    print(json.dumps(report['coverage'], sort_keys=True))


if __name__ == '__main__':
    main()

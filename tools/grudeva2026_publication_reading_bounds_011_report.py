"""Render the bounded 011 result; no scientific execution or private locators."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def render(result, destination):
    destination.mkdir(parents=True, exist_ok=True)
    # All rows and native interval pieces remain machine-readable. Execution
    # timing is factual metadata; calculations and row order are deterministic.
    (destination/'RESULTS.json').write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False)+'\n')
    with (destination/'ROWS.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(result['rows'][0]), lineterminator='\n')
        writer.writeheader()
        for row in result['rows']:
            writer.writerow({k: json.dumps(v, sort_keys=True, allow_nan=False) if isinstance(v, (dict, list)) or v is None else v for k, v in row.items()})
    summary = result['summary']['ALL_INPUT_ROWS']['ALL_FAMILIES']
    complete = result['complete_under_declared_readouts']
    sign, threshold = summary['zero_exclusion'], summary['threshold']
    sensitive = sorted({r['target_id'] for r in result['rows'] if r['witnesses'] and r['witnesses']['demonstrated_threshold_sensitivity']})
    unresolved_zero = sorted({r['target_id'] for r in result['rows'] if r['reading'] and r['reading']['zero_exclusion'] == 'UNRESOLVED'})
    arrival = [r['reading']['signed'][0] for r in result['rows'] if r['family'] == 'figure4_arrival' and r['reading']]
    lines = ['# Grudeva publication discrepancy under figure-reading uncertainty', '',
        '**'+('Complete under the declared retained readouts.' if complete else 'Partial: retain the operation-specific unavailable results.')+'** '
        'The original nominal result remains 17 failures and the F3F-001 pass per input. '
        'The new enclosures answer separate questions about signed separation and the unchanged thresholds.', '',
        f"Of 72 historically included input-target rows, {summary['reading_available']} have reading enclosures. "
        f"Signed separation is positive for {sign.get('POSITIVE',0)}, negative for {sign.get('NEGATIVE',0)}, "
        f"and unresolved for {sign.get('UNRESOLVED',0)}. "
        f"The original limit is exceeded throughout for {threshold.get('EXCEEDED_THROUGHOUT',0)}, "
        f"satisfied throughout for {threshold.get('WITHIN_THROUGHOUT',0)}, and unresolved for {threshold.get('UNRESOLVED',0)}. "
        f"Compatible witnesses demonstrate threshold sensitivity in {summary['demonstrated_threshold_sensitivity']} rows.", '',
        'Targets with demonstrated threshold sensitivity: '+(', '.join(sensitive) or 'none demonstrated')+'. '
        'Targets whose signed enclosure does not exclude zero: '+', '.join(unresolved_zero)+'. '
        'The individual table retains every arm and distinguishes these two questions.', '',
        f"Vertical-only reading bounds leave {summary['vertical_only_threshold'].get('UNRESOLVED',0)} threshold classifications unresolved; "
        +(f"the complete coordinate propagation leaves {threshold.get('UNRESOLVED',0)} unresolved. " if complete else
          f"available calculations leave {threshold.get('UNRESOLVED',0)} unresolved among {summary['reading_available']} available included rows, with missing horizontal results reported separately. ")
        +(f"The smallest arrival residual lower bound is {min(arrival):.9g}, compared with its unchanged 0.025 limit. " if arrival else '')
        +('Horizontal sensitivity therefore narrows some nominal discrepancy claims while retaining the arrival discrepancy under the named reading scope. ' if complete else
          'Partial coordinate availability does not establish the missing horizontal conclusions; retained scalar findings keep their named reading scope. ')
        +'This supports more careful use of the source-model evidence in later wetting/extraction decisions; it does not explain the publication discrepancy.', '',
        'These are 31 publication targets evaluated by four retained inputs, not 124 independent source observations. '
        'All 52 historical exclusions remain visible and unscored. Zero historical unavailable rows remain zero. '
        'No reading bound or original acceptance threshold was changed.', '',
        'GOVERNANCE_CLASS=G1; NO_GOVERNING_PHYSICS_CHANGE; PUBLIC_NUMERICAL_REFERENCE_COMPARISON; '
        'TARGET_EXPOSED; PHYSICAL_VALIDATION=NOT_ESTABLISHED. This is a retrospective comparison with selected '
        'published numerical curves, not independent experimental validation.', '',
        '## Per-input and per-family accounting', '',
        '| Input / family | Included / requested | Excluded | Reading available / included | Positive / negative / unresolved | Exceeded / within / unresolved | Demonstrated sensitivity |',
        '|---|---:|---:|---:|---|---|---:|']
    for identity in ('P0', 'P1', 'C0', 'C1'):
        for family, row in result['summary'][identity].items():
            sign, threshold = row['zero_exclusion'], row['threshold']
            lines.append(f"| {identity} / {family} | {row['historically_included']} / {row['requested']} | "
                         f"{row['historically_excluded']} | {row['reading_available']} / {row['historically_included']} | "
                         f"{sign.get('POSITIVE',0)} / {sign.get('NEGATIVE',0)} / {sign.get('UNRESOLVED',0)} | "
                         f"{threshold.get('EXCEEDED_THROUGHOUT',0)} / {threshold.get('WITHIN_THROUGHOUT',0)} / {threshold.get('UNRESOLVED',0)} | "
                         f"{row['demonstrated_threshold_sensitivity']} |")
    lines += ['', 'Unavailable counts, when present, are separate in JSON; they are not included in the unresolved counts above.', '',
              '## Individual target conclusions', '',
              'All bounds below are signed model minus publication, in the original dimensionless observable. '
              'Each input is retained. The original limits are concentration .015, front .008 and arrival .025. '
              'Full coordinates, unchanged nominal values/residuals, masks, vertical-only enclosures, range pieces, '
              'absolute bounds and witness coordinates are in [RESULTS.json](RESULTS.json) and [ROWS.csv](ROWS.csv).', '',
              '| Input | Target | Original | Vertical-only signed bounds | Combined reading signed bounds | Zero | Threshold | Sensitivity witnessed |',
              '|---|---|---|---|---|---|---|---|']
    def bounds(value):
        return 'unavailable' if value is None else '['+', '.join(f'{x:.9g}' for x in value['signed'])+']'
    for r in result['rows']:
        if r['original']['classification'] != 'INCLUDED':
            continue
        reading, w = r['reading'], r['witnesses']
        lines.append(f"| {r['input']} | {r['target_id']} | {r['original']['status']} | {bounds(r['vertical_only'])} | "
                     f"{bounds(reading)} | {reading['zero_exclusion'] if reading else 'UNAVAILABLE'} | "
                     f"{reading['threshold'] if reading else 'UNAVAILABLE'} | {bool(w and w['demonstrated_threshold_sensitivity'])} |")
    lines += ['', '## Common-coordinate method and refinement sensitivity', '',
        'Publication ordinate uncertainty cancels in each direct difference. Ranges below summarize all included '
        'targets in the family; each target retains its own range/pieces in JSON. The reported family hull does not '
        'claim that all targets or every value between extrema are jointly attainable. Refinements are empirical '
        'sensitivities, not certified continuum-error bounds or an extension of 008 PASS.', '',
        '| Difference | Family | Available / historically included | Hull of direct target ranges |', '|---|---|---:|---|']
    for pair in (('P0','C0'),('P1','C0'),('P0','C1'),('P1','C1'),('P1','P0'),('C1','C0')):
        for family in ('figure3_concentration','figure3_front','figure4_concentration','figure4_arrival'):
            group = [p for p in result['pairs'] if (p['first'],p['second']) == pair and p['family'] == family and p['status'] != 'HISTORICALLY_EXCLUDED']
            valid = [p['range'] for p in group if p['range'] is not None]
            span = 'unavailable' if not valid else f'[{min(r[0] for r in valid):.9g}, {max(r[1] for r in valid):.9g}]'
            lines.append(f"| {pair[0]} − {pair[1]} | {family} | {len(valid)} / {len(group)} | {span} |")
    lines += ['', '## Readout and numerical scope', '',
        'Production F3 uses the native raw-state diagnostic quadratic; production F4 uses the distinct native '
        'BDF outlet. Comparator F3 uses saved native cell-average reconstruction. Comparator F4 is conditional '
        'on the event-split accepted-step linear interpolant used by the existing discrete cup audit. Exact '
        'knots and event sides are retained; cup consistency does not certify an instantaneous or continuum-error bound.', '',
        'The outward Decimal interval calculation encloses coefficient arithmetic, stationary regions and '
        'one-sided stencil limits. The 1e-11 subdivision criterion bounds range overestimation, not physical '
        'uncertainty. Fixed-time production state floats are inputs to the spatial reduction. New reduction '
        'verification, faithful replay, original campaign qualification and continuum accuracy remain separate.', '',
        'Every expanded numerical enclosure is null: no independently justified instantaneous readout or '
        'continuum allowance is available for these new intervals. Unknown components are not zero. Neither '
        'solver tolerances, synthetic fixture limits, historical comparison thresholds, P1’s particular replay '
        'certificate nor cup-integral consistency is repurposed as such an allowance.', '',
        'An unresolved threshold enclosure is not by itself demonstrated sensitivity. A sensitivity claim '
        'requires the reported acceptable and unacceptable native evaluations at compatible coordinates and '
        'publication ordinates. These witnesses are conditional on the marginal rectangle, not evidence '
        'that the real reading or a common calibration shift attains them. An enclosure containing zero '
        'does not establish equality, adequacy, equivalence or reconciliation of the complete curve.', '',
        '## Evidence access and limits', '']
    for identity, a in result['admissions'].items():
        checks = [r['nominal_adapter'] for r in result['rows'] if r['input'] == identity and r['nominal_adapter']]
        maximum = max((c[k] for c in checks for k in ('error', 'reduction_error') if c[k] is not None), default=None)
        passed = sum(c['passed'] for c in checks)
        lines += [f"* {identity}: {a['status']}; {len(checks)} concentration nominal checks attempted, {passed} passed, {len(checks)-passed} failed; maximum absolute difference {maximum}. "
                  +(f"Discrete cup consistency {a['discrete_cup_consistency']:.9g}." if 'discrete_cup_consistency' in a else a.get('reason',''))]
    missing = [r for r in result['rows'] if r['original']['classification']=='INCLUDED' and r['reading'] is None]
    if missing:
        lines += ['', 'Affected rows and smallest missing requirement:']
        lines += [f"* {r['input']}/{r['target_id']}: {r['unavailable_reason']}; requires admission of this original archive or correction/qualification of this named observation operation, without changing the historical identity." for r in missing]
    lines += ['', 'Original P1 failed replay metadata and DIAGNOSTIC_ONLY origin remain bound alongside its accepted '
        '007 certificate route. Available event brackets/sides are retained as provenance; support brackets are '
        'not reinterpreted as certified event-location error.', '',
        '009’s completed equation/parameter/observation crosswalk and source re-extraction evidence are reused '
        'by verified identity. The original figure-producing configuration, revision, arrays and plotting/readout '
        'remain unresolved. This addendum does not choose a cause or infer author error. No author contact or '
        'source acquisition was performed. FIG5_REFERENCE_INCOMPLETE and 010 / PR #333 remain separate.', '',
        'See [PROTOCOL.md](PROTOCOL.md), [BINDINGS.json](BINDINGS.json), [HANDOFF.md](HANDOFF.md) and '
        '[QA.json](QA.json) for the frozen method, reproduction, independent audit and software/hosted statuses. '
        'No new trajectory, fit, full reference, numerical qualification campaign, EWP change or adoption. '
        'PHYSICAL_VALIDATION=NOT_ESTABLISHED.', '']
    (destination/'RESULTS.md').write_text('\n'.join(line.rstrip() for line in lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    render(json.loads(args.results.read_text()), args.destination)


if __name__ == '__main__':
    main()

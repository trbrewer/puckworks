"""Render an existing 009 assessment; no admission, scoring or solver calls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def number(value):
    return 'unavailable' if value is None else format(value, '.17g')


def location(coordinates):
    return ', '.join(f'{key}={number(value)}' for key, value in coordinates.items())


def render(result):
    lines = ['# 009 publication reconciliation results', '',
             f"**{result['primary_outcome']}**. Complete: **{result['complete']}**; "
             f"mixed findings: **{result['mixed_findings']}**.", '',
             'PUBLIC_NUMERICAL_REFERENCE_COMPARISON / TARGET_EXPOSED. '
             'PHYSICAL_VALIDATION=NOT_ESTABLISHED. Positive residual means model minus publication.', '',
             '## Separate per-input and family results', '',
             '| Input | Family | Requested / included / excluded / unavailable | Verdict |',
             '|---|---|---|---|']
    for key in ('P0', 'C0', 'P1', 'C1'):
        for family, f in result['inputs'][key]['families'].items():
            counts = ' / '.join(str(f[k]) for k in ('requested', 'included', 'excluded', 'unavailable'))
            lines.append(f"| {key} | {family} | {counts} | {f['status']} |")
    lines += ['', '## Included-support maxima', '',
              'All exact ties are reported in fixture order. Excluded values never enter these maxima. '
              'Acceptance is inclusive at full stored precision; extraction bounds remain in RESULTS.json.', '',
              '| Input | Family | Target / location | Model | Publication | Signed residual | Absolute residual | Limit |',
              '|---|---|---|---:|---:|---:|---:|---:|']
    for key in ('P0', 'C0', 'P1', 'C1'):
        for family, f in result['inputs'][key]['families'].items():
            for r in f['maxima']:
                vals = ' | '.join(number(r[k]) for k in ('model', 'publication', 'signed_residual', 'absolute_residual', 'limit'))
                lines.append(f"| {key} | {family} | {r['target_id']}: {location(r['coordinates'])} | {vals} |")
    lines += ['', '## Shared failure witnesses and refinement persistence', '',
              '| Family | Primary shared failures | Refined shared failures | Same-direction persistent failures |',
              '|---|---|---|---|']
    for family, f in result['primary']['families'].items():
        refined = result['refinement_outcomes']['pair']['families'][family]
        persistent = result['refinement_outcomes']['witness_persistence'][family]
        lines.append('| '+family+' | '+', '.join(f['shared_failure_ids'])+' | '+', '.join(refined['shared_failure_ids'])+' | '+', '.join(persistent['persistent_shared_ids'])+' |')
    lines += ['', 'Method-specific failures, support differences, changed witnesses and verdict changes '
              'are retained explicitly in RESULTS.json; they cannot be inferred from two FAIL labels.', '',
              '## Primary residuals on common included support', '',
              '| Target | Location | P0 − publication | C0 − publication | P0 − C0 | Shared failure |',
              '|---|---|---:|---:|---:|---|']
    for family in result['primary']['families'].values():
        for r in family['common_included']:
            vals = ' | '.join(number(r[k]) for k in ('production_minus_publication', 'comparator_minus_publication', 'production_minus_comparator'))
            lines.append(f"| {r['target_id']} | {location(r['coordinates'])} | {vals} | {r['shared_failure']} |")
    lines += ['', '## Retained refinement sensitivity on common included coordinates', '',
              'These differences are empirical sensitivity diagnostics, not continuum-error bounds. '
              'They do not replace any per-input headline. The machine-readable rows also retain '
              'both pairs’ publication residuals and scale-aware arithmetic identity checks.', '',
              '| Target | Location | P1 − P0 | C1 − C0 |', '|---|---|---:|---:|']
    for r in result['common_support_sensitivity']:
        lines.append(f"| {r['target_id']} | {location(r['coordinates'])} | {number(r['production_refinement'])} | {number(r['comparator_refinement'])} |")
    lines += ['', 'All 124 input-target rows, including excluded and unavailable rows, are in '
              '[RESULTS.json](RESULTS.json). Each row records the exact requested and retained coordinates, '
              'field identity, source value/bounds, model value, residual, mask, limit and status. '
              'The t=6.4 reference-side z=1 boundary is mask-only; Figure 3 still has three measured fronts.', '',
              'Figure 5 remains FIG5_REFERENCE_INCOMPLETE. Causal interpretation, historical comparison '
              'differences, execution accounting and use limits are in [HANDOFF.md](HANDOFF.md).', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = json.loads(args.results.read_text())
    args.output.write_text(render(result))


if __name__ == '__main__':
    main()

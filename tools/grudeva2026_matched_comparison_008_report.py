"""Render 008 results and localize already-scored saved differences; no solver."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from puckworks.analysis import grudeva2026_matched_comparison_008 as score
from puckworks.analysis.grudeva2026_matched_comparison_008_io import READ


def write(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n')


def localize(folder, result):
    t, z = score.support()
    output = dict(kind='DIAGNOSTIC_ONLY_SAVED_DIFFERENCES', pairs=[])
    for pair in result['pairs']:
        path = folder/(pair['production']+'-'+pair['comparator']+'.npz')
        if not path.exists():
            output['pairs'].append(dict(pair=pair['pair'], status='UNAVAILABLE'))
            continue
        with np.load(path, allow_pickle=False) as arrays:
            fronts = [arrays['front__'+k] for k in ('production', 'comparator')]
            arrivals = [arrays['arrival__'+k][0] for k in ('production', 'comparator')]
            families = {}
            for name, row in pair['families'].items():
                difference, selected = arrays[name+'__difference'], arrays[name+'__selected']
                excess = selected & (abs(difference) > row['limit'])
                indices = np.argwhere(excess)
                item = dict(exceedance_count=int(excess.sum()), location=row['location'],
                            signed_difference=row['signed_difference'], production=row['production'],
                            comparator=row['comparator'])
                if name not in ('arrival', 'activation') and len(indices):
                    item['exceedance_time_range'] = [float(t[indices[:, 0].min()]), float(t[indices[:, 0].max()])]
                coords = (np.asarray(score.obs.HISTORY_Z) if name == 'grain_histories' else z
                          if name in ('activation', 'liquid_profiles', 'grain_profiles') else None)
                if coords is not None and len(indices):
                    item['exceedance_z_range'] = [float(coords[indices[:, -1].min()]), float(coords[indices[:, -1].max()])]
                location = row['location']
                if location and 't' in location:
                    k = location['index'][0]
                    time = location['t']
                    item['temporal_region'] = ('before_first_drip' if time < 1 else
                                              'both_fronts_exited' if time >= max(arrivals) else
                                              'between_arrivals' if time >= min(arrivals) else 'front_advancing')
                    item['front_at_maximum'] = dict(production=float(fronts[0][k]), comparator=float(fronts[1][k]))
                    if 'z' in location:
                        position = location['z']
                        item['spatial_region'] = ('inlet' if position == 0 else 'outlet_endpoint' if position == 1
                                                  else 'inlet_region_z_le_0.1' if position <= .1
                                                  else 'outlet_region_z_ge_0.9' if position >= .9 else 'interior')
                        item['distance_from_front'] = dict(production=float(position-fronts[0][k]),
                                                           comparator=float(position-fronts[1][k]))
                families[name] = item
            # Actual separately evolved cup and phase amounts, all on full common support.
            amounts = ['cup', 'liquid_inventory', 'fines_inventory', 'boulder_inventory']
            available = np.logical_and.reduce([arrays[n+'__available'] for n in amounts])
            p = sum(arrays[n+'__production'] for n in amounts)
            c = sum(arrays[n+'__comparator'] for n in amounts)
            balance, _ = score.metric(p, c, True, available, np.finfo(float).max, times=t)
            balance.pop('limit')
            balance.pop('status')
            balance.pop('qualified_disagreement_detected')
            balance['meaning'] = 'Diagnostic difference of actual cup plus all actual phases; no complement reconstruction or new gate'
            output['pairs'].append(dict(pair=pair['pair'], families=families, actual_total_inventory_difference=balance))
    return output


def number(value):
    return 'unavailable' if value is None else format(value, '.17g')


def render(result, diagnostics):
    lines = ['# 008 matched baseline comparison', '', '**'+result['primary_disposition']+'**.', '',
             'G1 / NO_GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.', '',
             'All differences below are **production minus comparator**, in the inherited dimensionless definitions. '
             'Cup and phases use `phi_T*L*A*c_sat`; their values are not divided by initial inventory. '
             'Neither implementation is designated exact truth.', '',
             'Overall four-pair task completeness: **'+str(result['complete']).upper()+'**. '
             'Integration, software QA, evidence access, execution and independent review remain separate receipts.', '',
             '## Pair dispositions', '', '| Pair | Inputs | Complete | Qualified disagreement | Disposition |',
             '|---|---|---|---|---|']
    for p in result['pairs']:
        lines.append(f"| {p['pair']} | {p['production']}/{p['comparator']} | {p['complete']} | {p['qualified_disagreement_detected']} | {p['disposition']} |")
    for p in result['pairs']:
        lines += ['', '## '+p['pair']+' — '+p['production']+'/'+p['comparator'], '',
                  '| Family | Requested / included / excluded / unavailable | Max absolute | Signed difference | Production | Comparator | Location | Limit | Result |',
                  '|---|---|---|---|---|---|---|---|---|']
        for name in score.LIMITS:
            r = p['families'][name]
            counts = '/'.join(str(r[k]) for k in ('requested','included','excluded','unavailable'))
            location = json.dumps(r['location'], separators=(',', ':'))
            lines.append(f"| {name} | {counts} | {number(r['max_absolute'])} | {number(r['signed_difference'])} | {number(r['production'])} | {number(r['comparator'])} | `{location}` | {number(r['limit'])} | {r['status']} |")
        lines += ['', '| History z | Requested / included / excluded / unavailable | Max absolute | Signed difference | Production | Comparator | Time | Result |',
                  '|---|---|---|---|---|---|---|---|']
        for r in p['histories']:
            counts = '/'.join(str(r[k]) for k in ('requested','included','excluded','unavailable'))
            time = r['location'].get('t') if r['location'] else None
            lines.append(f"| {r['history_z']} | {counts} | {number(r['max_absolute'])} | {number(r['signed_difference'])} | {number(r['production'])} | {number(r['comparator'])} | {number(time)} | {r['status']} |")
        d = next(v for v in diagnostics['pairs'] if v['pair'] == p['pair'])
        for name, r in d.get('families', {}).items():
            if not r['exceedance_count']:
                continue
            lines += ['', f"**{name}:** {r['exceedance_count']} included observations exceed the unchanged limit. "
                      f"Time range: {r.get('exceedance_time_range', 'event/activation observable')}; "
                      f"physical-z range: {r.get('exceedance_z_range', 'not spatial')}. "
                      f"The maximum occurs in {r.get('temporal_region', 'the event/activation observable')}, "
                      f"{r.get('spatial_region', 'without a spatial coordinate')}. "
                      f"Front values and signed distances at the maximum are retained in DIAGNOSTICS.json."]
    lines += ['', '## Refinement sensitivity', '',
              '| Family | P0/C0 | P1/C0 (production refined) | P0/C1 (comparator refined) | P1/C1 (both refined) | Included counts in pair order |',
              '|---|---|---|---|---|---|']
    for name in score.LIMITS:
        rows = [p['families'][name] for p in result['pairs']]
        lines.append('| '+name+' | '+' | '.join(number(r['max_absolute']) for r in rows)+' | '+', '.join(str(r['included']) for r in rows)+' |')
    lines += ['', 'Every pair uses its own qualified mask. A lower maximum on a changed mask alone is not evidence '
              'of convergence. RESULTS.json includes a separately labelled intersection diagnostic at the same '
              'coordinates; it does not replace any acceptance result. Empirical refinements are not certified '
              'continuum-error bounds.', '',
              'DIAGNOSTICS.json localizes all demonstrated excesses and records actual cup-plus-phase consistency. '
              'Event-side observations are preserved separately in RESULTS.json. Concentrations at each method’s '
              'own arrival are not treated as same-time comparisons. Disagreement does not establish which method '
              'is more accurate or demonstrate a production bug.', '',
              '## Evidence and limits', '',
              'P0 is original 006-spatial-512, qualified by final 007. P1 is original 007 combined, admitted through '
              'the unchanged accepted replay certificate and exact diagnostic-origin observation artifact. Its '
              'original replay failure and diagnostic label remain preserved. C0/C1 are qualified 004 '
              'normal-final/combined-final. The comparator retains its permission-attributed modified reference '
              'lineage and existing notices; it is not an untouched author execution.', '',
              'New production simulations = **0**. New comparator simulations = **0**. Full arrays and private '
              'logs remain external. No publication rescore, physical validation, continuum accuracy, adoption, '
              'EWP/default/dependency change, issue closure, merge or successor follows. See HANDOFF.md and '
              'ACCOUNTING.json for actual execution costs, reproduction and review/QA status.', '']
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('attempt', type=Path)
    p.add_argument('output', type=Path)
    args = p.parse_args()
    ledger = [json.loads(s) for s in (args.attempt/'ledger.jsonl').read_text().splitlines()]
    score.require([r['event'] for r in ledger] == ['start','end'] and ledger[-1]['status'] == 'COMPLETED', 'attempt not closed')
    for name, digest in ledger[-1]['outputs'].items():
        score.require(score.obs.sha(args.attempt/name) == digest, 'scored artifact changed')
    result = READ(args.attempt/'results.json')
    diagnostics = localize(args.attempt, result)
    args.output.mkdir(exist_ok=True, parents=True)
    write(args.output/'RESULTS.json', result)
    write(args.output/'DIAGNOSTICS.json', diagnostics)
    (args.output/'RESULTS.md').write_text(render(result, diagnostics))


if __name__ == '__main__':
    main()

"""Saved-result comparison of four fixed Grudeva captures; no solver entry point.

The 002 inter-method policy is distinct from the narrower 004/005 refinement
policies. All signed differences are production minus comparator. Derived
comparator observations retain the permission-attributed reference lineage.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_conservative_003_report as inherited

TASK = 'MODEL-GRUDEVA2026-MATCHED-COMPARISON-008'
ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/analysis/model_grudeva2026_matched_comparison_008'
PAIRS = (('PRIMARY', 'P0', 'C0'), ('SECONDARY 1', 'P1', 'C0'),
         ('SECONDARY 2', 'P0', 'C1'), ('SECONDARY 3', 'P1', 'C1'))
LIMITS = dict(outlet=1e-3, liquid_profiles=1e-3, front=1e-3, arrival=1e-3,
              activation=1e-3, grain_profiles=5e-4, grain_histories=5e-4,
              cup=1e-4, liquid_inventory=1e-4, fines_inventory=1e-4,
              boulder_inventory=1e-4)
AGREEMENT = 'MATCHED_BASELINE_AGREEMENT_ON_DECLARED_CASE'
DISAGREEMENT = 'QUALIFIED_BASELINE_DISAGREEMENT_ON_DECLARED_CASE'
INCOMPLETE = 'MATCHED_COMPARISON_INCOMPLETE'
# 0 = complete agreement; 2 = complete with disagreement; 3 = incomplete;
# 1 = implementation/contract/operational failure. A normal exit is not a PASS.
EXIT_CODES = {AGREEMENT: 0, DISAGREEMENT: 2, INCOMPLETE: 3}
CANONICAL_PHYSICS = dict(phi_f=.64, phi_b=.16, phi_l=.2, phi_T=.2, varphi_lb=0,
                         q=1, D_sb=1, gamma=1, c_f_init=1.388, c_b_init=1.388,
                         beta=3.2, delta=.8, a=4.2, s_w='min(t,1)', horizon=8)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def support():
    return obs.observation_support(8.)


def support_identity():
    t, z = support()
    return {k: obs._array_identity(np.asarray(v, dtype=float))
            for k, v in [('times', t), ('z', z), ('history_z', obs.HISTORY_Z)]}


def vector(value, shape):
    """Missing or nonfinite values remain unavailable, even outside a mask."""
    if value is None:
        return np.full(shape, np.nan)
    a = np.asarray(value, dtype=float)
    require(a.shape == shape, 'malformed observation shape')
    return a


def aligned(run):
    """Check record alignment before using the inherited nearest-time rule."""
    t, z = support()
    require(np.array_equal(run['z'], z), 'wrong physical-z support')
    require(np.array_equal(run['grain_history_z'], obs.HISTORY_Z), 'wrong history support')
    observations = run['observations']
    records = (np.empty((0, 8)) if len(observations) == 0 and len(run['records']) == 0
               else vector(run['records'], (len(observations), 8)))
    ts = np.asarray([o['t'] for o in observations], float)
    require(np.all(np.isfinite(ts)) and np.all(np.diff(ts) > 0), 'invalid time coordinates')
    require(np.array_equal(records[:, 0], ts), 'observation/record misalignment')
    fields = {k: np.asarray([vector(o.get(k), (n,)) for o in observations]).reshape(-1, n)
              for k, n in [('liquid_profile', len(z)), ('grain_profile', len(z)),
                           ('grain_history', len(obs.HISTORY_Z))]}
    if len(ts):
        indices, available = inherited.samples(run, t)
        result = {k: v[indices] for k, v in fields.items()}
        result['records'] = records[indices]
        result['matched_times'] = ts[indices]
    else:
        available = np.zeros(len(t), bool)
        result = {k: np.full((len(t), v.shape[1]), np.nan) for k, v in fields.items()}
        result['records'] = np.full((len(t), 8), np.nan)
        result['matched_times'] = np.full(len(t), np.nan)
    result.update(available=available, activation=vector(run.get('activation'), z.shape),
                  history_activation=vector(run.get('grain_history_activation'), (7,)),
                  arrival=float(run['arrival']) if run.get('arrival') is not None else np.nan)
    return result


def event_reasons(run):
    """Admission of required sides; own-arrival values are never same-time scores."""
    events = run.get('events', [])
    if len(events) != 2 or {e.get('kind') for e in events} != {'first_drip', 'desaturation_exit'}:
        return ['required event sides missing or duplicated']
    reasons = []
    for e in events:
        expected = 1. if e['kind'] == 'first_drip' else run.get('arrival')
        if expected is None or e.get('t') != expected:
            reasons.append('event time/arrival mismatch')
        if 'sides' in e:
            sides = e['sides']
            if len(sides) != 2 or [s.get('side') for s in sides] != ['left', 'right']:
                reasons.append('event side provenance mismatch')
                continue
            left, right = [s.get('outlet') for s in sides]
        else:
            left, right = e.get('outlet_left'), e.get('outlet_right')
        if left is None or right is None or not np.all(np.isfinite([left, right])):
            reasons.append('event value unavailable')
        elif e['kind'] == 'first_drip' and (left != 0 or right != 1):
            reasons.append('first-drip side convention differs')
        elif e['kind'] == 'desaturation_exit' and left != 1:
            reasons.append('exit side convention differs')
    return reasons


def metric(production, comparator, include, available, limit, *, times=None, z=None):
    p, c = np.asarray(production, float), np.asarray(comparator, float)
    require(p.shape == c.shape, 'difference shape mismatch')
    include = np.broadcast_to(include, p.shape)
    available = np.broadcast_to(available, p.shape) & np.isfinite(p) & np.isfinite(c)
    # Subtract only validated values. Overflow is unavailable, never hidden.
    difference = np.full(p.shape, np.nan)
    with np.errstate(over='ignore', invalid='ignore'):
        np.subtract(p, c, out=difference, where=available)
    available &= np.isfinite(difference)
    selected = include & available
    row = dict(requested=int(p.size), included=int(selected.sum()),
               excluded=int((available & ~include).sum()), unavailable=int((~available).sum()),
               max_absolute=None, signed_difference=None, production=None, comparator=None,
               location=None, limit=limit, status='UNAVAILABLE', reasons=[])
    if np.any(selected):
        k = np.unravel_index(np.argmax(np.where(selected, abs(difference), -1)), p.shape)
        location = dict(index=[int(i) for i in k])
        if times is not None:
            location['t'] = float(times[k[0]])
        if z is not None:
            location['z'] = float(z[k[-1]])
        row.update(max_absolute=float(abs(difference[k])), signed_difference=float(difference[k]),
                   production=float(p[k]), comparator=float(c[k]), location=location)
    excess = row['max_absolute'] is not None and row['max_absolute'] > limit
    row['qualified_disagreement_detected'] = excess
    if row['unavailable']:
        row['reasons'].append('required values, matching samples, or mask prerequisites unavailable')
    if not row['included']:
        row['reasons'].append('empty required comparable support')
    if not row['reasons']:
        row['status'] = 'FAIL' if excess else 'PASS'
    if excess:
        row['reasons'].append('absolute difference exceeds unchanged inter-method limit')
    assert row['requested'] == row['included'] + row['excluded'] + row['unavailable']
    return row, dict(production=p, comparator=c, difference=difference, selected=selected,
                     available=available, include=include)


def pair_verdict(families, admission=True, reasons=()):
    complete = (admission and not reasons and set(families) == set(LIMITS)
                and all(r['unavailable'] == 0 and r['included'] > 0 and r['status'] in ('PASS', 'FAIL')
                        for r in families.values()))
    disagreement = admission and any(r['qualified_disagreement_detected'] for r in families.values())
    return dict(complete=bool(complete), qualified_disagreement_detected=bool(disagreement),
                disposition=INCOMPLETE if not complete else DISAGREEMENT if disagreement else AGREEMENT,
                reasons=list(reasons), families=families)


def compare(production, comparator):
    """Recompute pair-specific 003/005 masks, with 008 limits and full availability."""
    a, b = aligned(production), aligned(comparator)
    t, z = support()
    ar, br = a['records'], b['records']
    available = a['available'] & b['available']
    events_available = np.isfinite(a['arrival']) and np.isfinite(b['arrival'])
    lo, hi = sorted([a['arrival'], b['arrival']])
    smooth = ((t < lo-.025) | (t > hi+.025)) & (abs(t-1) > .025)
    spatial = ((z[None, :] < np.minimum(ar[:, 1], br[:, 1])[:, None]-.008)
               | (z[None, :] > np.maximum(ar[:, 1], br[:, 1])[:, None]+.008))
    spatial |= (t >= hi)[:, None]
    spatial &= (t >= 1)[:, None] | (abs(z[None, :]-np.minimum(t, 1)[:, None]) > .008)
    liquid = spatial.copy()
    liquid[:, z == 1] &= smooth[:, None]
    aa, ba = a['activation'], b['activation']
    age = t[:, None]-np.maximum(aa, ba)[None, :] >= .02
    ha, hb = a['history_activation'], b['history_activation']
    aged = t[:, None]-np.maximum(ha, hb)[None, :] >= .02
    act_available = np.isfinite(aa) & np.isfinite(ba)
    history_available = np.isfinite(ha) & np.isfinite(hb)
    spatial_available = available & np.isfinite(ar[:, 1]) & np.isfinite(br[:, 1]) & events_available
    rows, details = {}, {}

    def add(name, p, c, mask, avail, **coordinates):
        rows[name], details[name] = metric(p, c, mask, avail, LIMITS[name], **coordinates)

    add('outlet', ar[:, 2], br[:, 2], smooth, available & events_available, times=t)
    add('front', ar[:, 1], br[:, 1], True, available, times=t)
    add('arrival', [a['arrival']], [b['arrival']], True, events_available)
    if rows['arrival']['location'] is not None:
        rows['arrival']['location'].update(z=1., production_t=a['arrival'], comparator_t=b['arrival'])
    add('activation', aa, ba, True, act_available, z=z)
    add('liquid_profiles', a['liquid_profile'], b['liquid_profile'], liquid,
        spatial_available[:, None], times=t, z=z)
    add('grain_profiles', a['grain_profile'], b['grain_profile'], spatial & age,
        spatial_available[:, None] & act_available[None, :], times=t, z=z)
    add('grain_histories', a['grain_history'], b['grain_history'], aged,
        available[:, None] & history_available[None, :], times=t, z=obs.HISTORY_Z)
    histories = []
    for k, position in enumerate(obs.HISTORY_Z):
        row, _ = metric(a['grain_history'][:, k], b['grain_history'][:, k], aged[:, k],
                        available & history_available[k], LIMITS['grain_histories'], times=t)
        row['history_z'] = position
        if row['location'] is not None:
            row['location'].update(z=position, history_index=k)
        histories.append(row)
    if any(r['status'] == 'UNAVAILABLE' for r in histories):
        rows['grain_histories']['status'] = 'UNAVAILABLE'
        rows['grain_histories']['reasons'].append('one or more required individual histories incomplete or empty')
    for k, name in [(3, 'cup'), (4, 'liquid_inventory'), (5, 'fines_inventory'), (6, 'boulder_inventory')]:
        add(name, ar[:, k], br[:, k], True, available, times=t)
    reasons = event_reasons(production) + event_reasons(comparator)
    result = pair_verdict(rows, reasons=reasons)
    result.update(histories=histories, sign='PRODUCTION_MINUS_COMPARATOR',
                  event_provenance=dict(production=production.get('events'), comparator=comparator.get('events')),
                  support_sha256={name: obs.digest(d['selected'].tolist()) for name, d in details.items()})
    return result, details


def unavailable_pair(reason):
    t, z = support()
    sizes = dict(outlet=len(t), front=len(t), arrival=1, activation=len(z),
                 liquid_profiles=len(t)*len(z), grain_profiles=len(t)*len(z),
                 grain_histories=len(t)*7, cup=len(t), liquid_inventory=len(t),
                 fines_inventory=len(t), boulder_inventory=len(t))
    rows = {name: metric(np.full(sizes[name], np.nan), np.full(sizes[name], np.nan),
                         True, False, limit)[0] for name, limit in LIMITS.items()}
    result = pair_verdict(rows, admission=False, reasons=[reason])
    result['histories'] = []
    for position in obs.HISTORY_Z:
        row, _ = metric(np.full(len(t), np.nan), np.full(len(t), np.nan), True, False,
                        LIMITS['grain_histories'])
        row.update(history_z=position, reasons=[reason])
        result['histories'].append(row)
    return result


def task_disposition(pairs):
    if len(pairs) != 4 or not all(p['complete'] for p in pairs):
        return INCOMPLETE
    return DISAGREEMENT if any(p['qualified_disagreement_detected'] for p in pairs) else AGREEMENT


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path,
                        help='Existing owner evidence parent directory')
    parser.add_argument('--output', required=True, type=Path, help='New external attempt directory')
    parser.add_argument('--contract', type=Path, default=DOCS/'CONTRACT.json')
    parser.add_argument('--review', type=Path)
    parser.add_argument('--admission-only', action='store_true', help='Read-only preflight; no cross-method scoring')
    parser.add_argument('--integration', required=True, type=Path)
    args = parser.parse_args(argv)
    from .grudeva2026_matched_comparison_008_io import execute
    try:
        result = execute(args)
    except Exception as exc:
        print(json.dumps(dict(execution='IMPLEMENTATION_OR_CONTRACT_FAILURE', reason=str(exc))))
        return 1
    if args.admission_only:
        print(json.dumps(result))
        return 0 if result['complete'] else 3
    print(json.dumps(dict(primary=result['pairs'][0]['disposition'],
                          overall=result['disposition'], complete=result['complete'])))
    return EXIT_CODES[result['disposition']]


if __name__ == '__main__':
    raise SystemExit(main())

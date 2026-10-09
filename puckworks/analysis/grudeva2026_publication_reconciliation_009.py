"""Publication-only scoring of admitted retained observations; never runs a solver.

All targets survive as rows. Availability precedes historical publication masks;
only included qualified rows enter maxima. Public targets are already exposed.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np

from . import grudeva2026_matched_comparison_008 as prior

ROOT = prior.ROOT
DOCS = ROOT / 'docs/analysis/model_grudeva2026_publication_reconciliation_009'
TASK = 'MODEL-GRUDEVA2026-PUBLICATION-RECONCILIATION-009'
INPUTS = ('P0', 'C0', 'P1', 'C1')
LIMITS = dict(figure3_concentration=.015, figure3_front=.008,
              figure4_concentration=.015, figure4_arrival=.025)
COUNTS = dict(zip(LIMITS, (19, 3, 8, 1)))
TIME_ATOL = 2e-13  # inherited retained-observation matching; no physical shift
IDENTITY_ULPS = 8
FIXTURE = 'puckworks/data/grudeva2026/publication_reference.json'
FIXTURE_SHA = '15260e44cfcdcb1b87b105fd0484b27a8ff7ac45cd9b81539431aab13a9cd6c2'
CURVE = 'epsilon -> 0, asymptotic, gray'
AGREEMENT = 'PUBLICATION_AGREEMENT'
SHARED = 'CORROBORATED_PUBLICATION_DISCREPANCY'
MIXED = 'MIXED_RESULT'
INCOMPLETE = 'INCOMPLETE_COMPARISON'
require = prior.require


def targets(fixture):
    """Stable fixture-order IDs; the mask-only boundary creates no target."""
    require(fixture['source']['curve_identity'] == CURVE, 'wrong publication curve')
    require(fixture['source']['axes'] == 'dimensionless z,t,c_l; linear', 'wrong axes')
    result = []
    for family, key, prefix, value in [
        ('figure3_concentration', 'figure3', 'F3C', 'c'),
        ('figure3_front', 'figure3_fronts', 'F3F', 'z'),
        ('figure4_concentration', 'figure4', 'F4C', 'c'),
        ('figure4_arrival', 'figure4_event', 'F4A', 't'),
    ]:
        entries = [fixture[key]] if key == 'figure4_event' else fixture[key]
        require(len(entries) == COUNTS[family], 'wrong publication inventory')
        for i, entry in enumerate(entries):
            coordinates = ({'z': 1.} if value == 't' else
                           {'t': entry['t'], 'z': entry['z']} if key == 'figure3' else
                           {'t': entry['t'], 'z': 1.} if key == 'figure4' else
                           {'t': entry['t']})
            bounds = {k: v for k, v in entry.items() if k.endswith('_uncertainty')}
            require(all(math.isfinite(v) for v in [entry[value], *coordinates.values(), *bounds.values()]),
                    'nonfinite publication target')
            result.append(dict(target_id=f'{prefix}-{i+1:03d}', family=family,
                               fixture_pointer=f'/{key}' + ('' if value == 't' else f'/{i}'),
                               coordinates=coordinates, publication=entry[value],
                               extraction_bounds=bounds, units='dimensionless', curve=CURVE,
                               limit=LIMITS[family]))
    return result


def unique_match(coordinates, requested, allowance):
    a = np.asarray(coordinates, float)
    require(a.ndim == 1 and np.all(np.isfinite(a)), 'malformed/nonfinite coordinates')
    hits = np.flatnonzero(abs(a-requested) <= allowance)
    require(len(hits) == 1, 'missing or ambiguous coordinate support')
    return int(hits[0])


def finite(value):
    require(value is not None and np.isscalar(value), 'missing/malformed value')
    result = float(value)
    require(math.isfinite(result), 'nonfinite value')
    return result


def observe(run, target):
    """Read the qualified channels verbatim, without any reconstruction.

    records columns: t, desaturation front, native outlet, cup, three phases,
    conservation residual. observations[i].liquid_profile is the qualified
    005 raw-state/004 conservative observation, never Result.liquid_profiles.
    """
    family, coord = target['family'], target['coordinates']
    require(isinstance(run, dict), 'malformed observation object')
    if family in ('figure4_concentration', 'figure4_arrival'):
        events = run.get('events')
        require(isinstance(events, list) and all(isinstance(e, dict) for e in events),
                'malformed event records')
        for event in events:
            if 'sides' in event:
                require(isinstance(event['sides'], list)
                        and all(isinstance(side, dict) for side in event['sides']),
                        'malformed event sides')
        require(not prior.event_reasons(run), 'missing/malformed one-sided event provenance')
        arrival = finite(run.get('arrival'))
        if family == 'figure4_arrival':
            return arrival, dict(z=1., event_t=arrival), 'arrival (desaturation_exit)', {}
    observations = run['observations']
    require(isinstance(observations, list) and all(isinstance(o, dict) for o in observations),
            'malformed observation records')
    records = np.asarray(run['records'], float)
    times = np.asarray([o['t'] for o in observations], float)
    require(times.ndim == 1 and np.all(np.isfinite(times)) and np.all(np.diff(times) > 0),
            'invalid/duplicate time coordinates')
    require(records.shape == (len(times), 8), 'malformed/empty record support')
    require(np.array_equal(records[:, 0], times), 'observation/record misalignment')
    i = unique_match(times, coord['t'], TIME_ATOL)
    matched = dict(t=float(times[i]), record_index=i)
    if family == 'figure3_front':
        return finite(records[i, 1]), matched, 'records[i][1] (desaturation_front)', {}
    if family == 'figure4_concentration':
        matched['z'] = 1.
        return finite(records[i, 2]), matched, 'records[i][2] (native_outlet)', dict(model_arrival=arrival)
    z = np.asarray(run['z'], float)
    require(z.ndim == 1 and np.all(np.isfinite(z)) and np.all(np.diff(z) > 0),
            'invalid/duplicate depth coordinates')
    j = unique_match(z, coord['z'], 0.)
    field = observations[i].get('liquid_profile')
    require(field is not None, 'qualified liquid_profile missing; legacy profiles inadmissible')
    profile = np.asarray(field, float)
    require(profile.shape == z.shape, 'malformed liquid_profile support')
    matched.update(z=float(z[j]), depth_index=j)
    return (finite(profile[j]), matched, 'observations[i].liquid_profile[j]',
            dict(model_front=finite(records[i, 1])))


def publication_mask(target, prerequisites, fixture):
    """Closed displaced intervals exactly as verification.publication_comparison."""
    family, coord = target['family'], target['coordinates']
    if family == 'figure3_concentration':
        fronts = [r['z'] for r in fixture['figure3_fronts'] if r['t'] == coord['t']]
        if coord['t'] == 6.4:
            require(not fronts, '6.4 mask boundary is not a measured front')
            reference, convention = 1., 'INHERITED_POST_EXIT_MASK_BOUNDARY_NOT_MEASURED_FRONT'
        else:
            require(len(fronts) == 1, 'reference mask front unavailable/ambiguous')
            reference, convention = finite(fronts[0]), 'MEASURED_REFERENCE_FRONT'
        model = finite(prerequisites['model_front'])
        low, high = min(model, reference)-.008, max(model, reference)+.008
        return low <= coord['z'] <= high, dict(axis='z', low=low, high=high,
                                               model_boundary=model, reference_boundary=reference,
                                               convention=convention, closed=True)
    if family == 'figure4_concentration':
        model, reference = finite(prerequisites['model_arrival']), finite(fixture['figure4_event']['t'])
        low, high = min(model, reference)-.025, max(model, reference)+.025
        return low <= coord['t'] <= high, dict(axis='t', low=low, high=high,
                                               model_boundary=model, reference_boundary=reference,
                                               convention='DISPLACED_ARRIVAL_INTERVAL', closed=True)
    return False, None


def score_input(identity, run, admission, fixture):
    rows = []
    for target in targets(fixture):
        row = dict(target, input=identity, qualified=bool(admission.get('qualified')),
                   model=None, matched_coordinates=None, observation_field=None,
                   signed_residual=None, absolute_residual=None, mask=None,
                   classification='UNAVAILABLE', status='UNAVAILABLE', reason='')
        try:
            require(row['qualified'] and run is not None,
                    'input not admitted: '+admission.get('reason', 'missing qualification'))
            model, matched, field, prerequisites = observe(run, target)
            # Required support and mask prerequisites are checked before exclusion.
            excluded, mask = publication_mask(target, prerequisites, fixture)
            residual = finite(model-target['publication'])
            row.update(model=model, matched_coordinates=matched, observation_field=field,
                       signed_residual=residual, absolute_residual=abs(residual), mask=mask,
                       classification='EXCLUDED' if excluded else 'INCLUDED',
                       status='EXCLUDED' if excluded else 'PASS' if abs(residual) <= target['limit'] else 'FAIL',
                       reason='within closed publication displacement mask' if excluded else
                       'within inclusive publication limit' if abs(residual) <= target['limit'] else
                       'exceeds unchanged publication limit')
        except (ValueError, KeyError, TypeError, IndexError, OverflowError) as exc:
            row['reason'] = str(exc)
        rows.append(row)
    families = {name: summarize([r for r in rows if r['family'] == name]) for name in LIMITS}
    complete = all(f['complete'] for f in families.values())
    failure = any(f['qualified_failure'] for f in families.values())
    return dict(input=identity, rows=rows, families=families, complete=complete,
                qualified_failure=failure, verdict='INCOMPLETE' if not complete else 'FAIL' if failure else 'PASS')


def summarize(rows):
    counts = {k.lower(): sum(r['classification'] == k for r in rows)
              for k in ('INCLUDED', 'EXCLUDED', 'UNAVAILABLE')}
    require(len(rows) == sum(counts.values()), 'support count partition')
    included = [r for r in rows if r['classification'] == 'INCLUDED']
    maximum = max((r['absolute_residual'] for r in included), default=None)
    # Exact ties retain all IDs in immutable fixture order, never rounded ties.
    maxima = [{k: r[k] for k in ('target_id', 'coordinates', 'model', 'publication',
                                 'signed_residual', 'absolute_residual', 'limit')}
              for r in included if r['absolute_residual'] == maximum]
    failures = [r['target_id'] for r in included if r['status'] == 'FAIL']
    complete = counts['unavailable'] == 0 and counts['included'] > 0
    return dict(requested=len(rows), **counts, complete=complete, qualified_failure=bool(failures),
                failure_ids=failures, max_absolute=maximum, maxima=maxima,
                status='INCOMPLETE' if not complete else 'FAIL' if failures else 'PASS')


def residual_identity(p, c, reference):
    rp, rc, pc = p-reference, c-reference, p-c
    error = (rp-rc)-pc
    allowance = IDENTITY_ULPS*np.finfo(float).eps*max(1., abs(p), abs(c), abs(reference), abs(rp), abs(rc), abs(pc))
    return dict(production_minus_publication=rp, comparator_minus_publication=rc,
                production_minus_comparator=pc, identity_error=error,
                identity_allowance=float(allowance), identity_passed=abs(error) <= allowance)


def pair_summary(production, comparator):
    families = {}
    for family in LIMITS:
        p = [r for r in production['rows'] if r['family'] == family]
        c = [r for r in comparator['rows'] if r['family'] == family]
        common, witnesses, p_only, c_only, support_differences = [], [], [], [], []
        for a, b in zip(p, c):
            require(a['target_id'] == b['target_id'] and a['coordinates'] == b['coordinates']
                    and a['publication'] == b['publication'], 'pair target misalignment')
            if a['classification'] != b['classification']:
                support_differences.append(dict(target_id=a['target_id'], production=a['classification'],
                                                comparator=b['classification']))
            shared = (a['classification'] == b['classification'] == 'INCLUDED'
                      and a['qualified'] and b['qualified'])
            witness = (shared and a['status'] == b['status'] == 'FAIL'
                       and ((a['signed_residual'] > 0) == (b['signed_residual'] > 0)))
            if shared:
                diag = residual_identity(a['model'], b['model'], a['publication'])
                require(diag['identity_passed'], 'residual arithmetic identity failed')
                common.append(dict(target_id=a['target_id'], coordinates=a['coordinates'],
                                   publication=a['publication'], production=a['model'], comparator=b['model'],
                                   limit=a['limit'], shared_failure=witness, **diag))
            if witness:
                witnesses.append(a['target_id'])
            else:
                if a['status'] == 'FAIL':
                    p_only.append(a['target_id'])
                if b['status'] == 'FAIL':
                    c_only.append(b['target_id'])
        families[family] = dict(common_included=common, shared_failure_ids=witnesses,
                                production_failures_without_shared_witness=p_only,
                                comparator_failures_without_shared_witness=c_only,
                                support_differences=support_differences)
    shared = any(f['shared_failure_ids'] for f in families.values())
    complete = production['complete'] and comparator['complete']
    mixed = (production['verdict'] != comparator['verdict'] or
             any(f['production_failures_without_shared_witness'] or f['comparator_failures_without_shared_witness']
                 for f in families.values()))
    outcome = (SHARED if shared else INCOMPLETE if not complete else
               AGREEMENT if production['verdict'] == comparator['verdict'] == 'PASS' else MIXED)
    return dict(production=production['input'], comparator=comparator['input'], complete=complete,
                outcome=outcome, shared_discrepancy=shared, mixed_findings=mixed, families=families)


def assess(inputs, admissions, fixture):
    results = {key: score_input(key, inputs.get(key), admissions.get(key, {}), fixture) for key in INPUTS}
    primary = pair_summary(results['P0'], results['C0'])
    refined = pair_summary(results['P1'], results['C1'])
    sensitivity = []
    for rows in zip(*(results[k]['rows'] for k in INPUTS)):
        if all(r['classification'] == 'INCLUDED' and r['qualified'] for r in rows):
            a, b, c, d = rows
            sensitivity.append(dict(target_id=a['target_id'], family=a['family'], coordinates=a['coordinates'],
                                    production_refinement=c['model']-a['model'],
                                    comparator_refinement=d['model']-b['model'],
                                    primary=residual_identity(a['model'], b['model'], a['publication']),
                                    refined=residual_identity(c['model'], d['model'], a['publication'])))
    changes = [{k: v for k, v in dict(input=k, family=f, baseline=results[k+'0']['families'][f]['status'],
                                     refined=results[k+'1']['families'][f]['status']).items()}
               for k in ('P', 'C') for f in LIMITS
               if results[k+'0']['families'][f]['status'] != results[k+'1']['families'][f]['status']]
    persistence = {}
    for family in LIMITS:
        a = primary['families'][family]['shared_failure_ids']
        b = refined['families'][family]['shared_failure_ids']
        primary_sign = {r['target_id']: r['production_minus_publication'] > 0
                        for r in primary['families'][family]['common_included']}
        refined_sign = {r['target_id']: r['production_minus_publication'] > 0
                        for r in refined['families'][family]['common_included']}
        persistence[family] = dict(persistent_shared_ids=[k for k in a if k in b and primary_sign[k] == refined_sign[k]],
                                   direction_changed_shared_ids=[k for k in a if k in b and primary_sign[k] != refined_sign[k]],
                                   primary_only_shared_ids=[k for k in a if k not in b],
                                   refinement_only_shared_ids=[k for k in b if k not in a])
    witness_changes = any(f['primary_only_shared_ids'] or f['refinement_only_shared_ids'] or f['direction_changed_shared_ids']
                          for f in persistence.values())
    complete = all(r['complete'] for r in results.values())
    all_pass = all(r['verdict'] == 'PASS' for r in results.values())
    require(sum(len(r['rows']) for r in results.values()) == 124, '124-row coverage failure')
    return dict(task=TASK, complete=complete, primary_outcome=primary['outcome'],
                primary=primary, refinement_outcomes=dict(P1=results['P1']['verdict'], C1=results['C1']['verdict'],
                                                         pair=refined, family_verdict_changes=changes,
                                                         witness_persistence=persistence),
                shared_discrepancy=primary['shared_discrepancy'],
                mixed_findings=primary['mixed_findings'] or refined['mixed_findings'] or bool(changes) or witness_changes,
                inputs=results, common_support_sensitivity=sensitivity,
                exit_code=3 if not complete else 0 if all_pass else 2,
                causal_resolution='UNRESOLVED_ORIGINAL_RUN_PROVENANCE',
                figure5=fixture['figure5'], physical_validation='NOT_ESTABLISHED')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--contract', type=Path, default=DOCS/'CONTRACT.json')
    parser.add_argument('--integration', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    from .grudeva2026_publication_reconciliation_009_io import execute
    result = execute(args)
    print(result['primary_outcome'], 'complete='+str(result['complete']))
    return result['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())

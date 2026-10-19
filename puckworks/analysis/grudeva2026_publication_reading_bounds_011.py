"""Retrospective figure-reading addendum; archive-only, never a solver campaign.

Grudeva, Moroney & Foster, DOI 10.1017/S095679252500018X (CC-BY-4.0
figure-derived reference). PHYSICAL_VALIDATION=NOT_ESTABLISHED.
"""
from __future__ import annotations

import argparse
from collections import Counter
import copy
import csv
import gc
import json
from pathlib import Path
import time

import numpy as np

from . import grudeva2026_baseline_observation_005 as obs
from . import grudeva2026_matched_comparison_008_io as admission
from . import grudeva2026_publication_reconciliation_009 as historical
from . import grudeva2026_replay_reassessment_007 as diagnostic
from .grudeva2026_reading_bounds_011_adapters import Production, Comparator
from .grudeva2026_reading_bounds_011_range import Interval as I, native_function, range_pieces, paired_pieces

ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT/'docs/analysis/model_grudeva2026_publication_reading_bounds_011'
OLD = ROOT/'docs/analysis/model_grudeva2026_publication_reconciliation_009'
PRIOR = ROOT/'docs/analysis/model_grudeva2026_matched_comparison_008'
TASK = 'MODEL-GRUDEVA2026-PUBLICATION-READING-BOUNDS-011'
INPUTS = ('P0', 'P1', 'C0', 'C1')
PAIRS = (('P0', 'C0'), ('P1', 'C0'), ('P0', 'C1'), ('P1', 'C1'), ('P1', 'P0'), ('C1', 'C0'))
NOMINAL_ATOL = 1e-10


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def decision(bounds, limit):
    low, high = bounds
    if low > high or not np.isfinite([low, high, limit]).all():
        raise ValueError('invalid residual enclosure')
    absolute_low = 0. if low <= 0 <= high else min(abs(low), abs(high))
    absolute_high = max(abs(low), abs(high))
    sign = 'POSITIVE' if low > 0 else 'NEGATIVE' if high < 0 else 'UNRESOLVED'
    threshold = ('EXCEEDED_THROUGHOUT' if absolute_low > limit else
                 'WITHIN_THROUGHOUT' if absolute_high <= limit else 'UNRESOLVED')
    return dict(signed=bounds, absolute=[absolute_low, absolute_high],
                zero_exclusion=sign, threshold=threshold,
                extrema_attainability='NOT_INFERRED_FROM_ENCLOSURE')


def residual(model_range, publication, width, limit):
    return decision((I(*model_range)-(I(publication)+I(-width, width))).floats(), limit)


def widths(row):
    family, bounds, coordinates = row['family'], row['extraction_bounds'], row['coordinates']
    if family.endswith('concentration'):
        axis = 'z' if family == 'figure3_concentration' else 't'
        center, width = coordinates[axis], bounds[axis+'_uncertainty']
        return axis, (I(center)+I(-width, width)).floats(), bounds['c_uncertainty']
    axis = 'z' if family == 'figure3_front' else 't'
    return None, None, bounds[axis+'_uncertainty']


def verify_history():
    bindings = read(DOC/'BINDINGS.json')
    for path, digest in bindings['files'].items():
        if obs.sha(ROOT/path) != digest:
            raise ValueError('immutable source/authority identity changed: '+path)
    old, prior = read(OLD/'CONTRACT.json'), read(PRIOR/'CONTRACT.json')
    for contract in (old, prior):
        for group in ('sources', 'implementation', 'prior_authorities'):
            for path, digest in contract.get(group, {}).items():
                if obs.sha(ROOT/path) != digest:
                    raise ValueError('historical dependency changed: '+path)
    fixture = read(ROOT/old['fixture']['file'])
    if old['inputs'] != prior['inputs'] or old['targets'] != historical.targets(fixture):
        raise ValueError('input or publication-target identities differ')
    b9, b8 = read(OLD/'EVIDENCE_BINDINGS.json'), read(PRIOR/'EVIDENCE_BINDINGS.json')
    if b9['verified_numerical_contents'] != b8['verified_numerical_contents']:
        raise ValueError('009 admission bindings differ from 008')
    result = read(OLD/'RESULTS.json')
    rows = [copy.deepcopy(r) for k in INPUTS for r in result['inputs'][k]['rows']]
    if len(rows) != 124 or Counter(r['classification'] for r in rows) != {'INCLUDED': 72, 'EXCLUDED': 52}:
        raise ValueError('historical population differs')
    for identity in INPUTS:
        selected = [r for r in rows if r['input'] == identity]
        if len(selected) != 31 or Counter(r['status'] for r in selected) != {'FAIL': 17, 'PASS': 1, 'EXCLUDED': 13}:
            raise ValueError('historical per-input population differs')
        if [r['target_id'] for r in selected if r['status'] == 'PASS'] != ['F3F-001']:
            raise ValueError('historical pass identity differs')
    for r in rows:
        signed = r['model']-r['publication']
        if signed != r['signed_residual'] or abs(signed) != r['absolute_residual']:
            raise ValueError('historical nominal residual does not reproduce')
        expected = 'PASS' if abs(signed) <= r['limit'] else 'FAIL'
        if r['limit'] != historical.LIMITS[r['family']] or (r['classification'] == 'INCLUDED' and r['status'] != expected):
            raise ValueError('historical limit arithmetic differs')
    return rows, old, prior, b9['verified_numerical_contents']


def retained_rows(rows):
    out = []
    for old in rows:
        axis, horizontal, width = widths(old)
        included = old['classification'] == 'INCLUDED'
        mask = old['mask']
        outside = None if horizontal is None else horizontal[1] < mask['low'] or horizontal[0] > mask['high']
        vertical = residual([old['model']]*2, old['publication'], width, old['limit']) if included else None
        out.append(dict(input=old['input'], target_id=old['target_id'], family=old['family'],
                        original=old, horizontal_axis=axis, horizontal_interval=horizontal,
                        publication_interval=(I(old['publication'])+I(-width, width)).floats(),
                        entire_interval_outside_original_mask=outside,
                        vertical_only=vertical, horizontal_model_range=None,
                        reading=vertical if included and axis is None else None,
                        expanded=None, expanded_unavailable_reason='Instantaneous readout and continuum error allowances unestablished',
                        new_status='RETAINED_SCALAR_COMPLETE' if included and axis is None else
                        'PENDING_HORIZONTAL' if included else 'HISTORICALLY_EXCLUDED',
                        new_qualification='Retained scalar reading arithmetic only' if included and axis is None else None,
                        new_support=dict(mask_check=outside, captured_support='NOT_YET_CHECKED' if axis else 'RETAINED_SCALAR',
                                         observation_operation='NOT_YET_CHECKED' if axis else 'UNCHANGED_RETAINED_SCALAR'),
                        nominal_adapter=None, range_pieces=None, witnesses=None,
                        null_reasons=dict(horizontal='No horizontal model query for scalar observable' if axis is None else
                                          'Historically excluded' if not included else 'Pending admission and full interval calculation',
                                          expanded='No independently justified instantaneous readout or continuum allowance'),
                        missing_components=['Certified instantaneous readout error', 'Continuum error', 'Original figure-producing provenance'],
                        unavailable_reason=None if included else 'Original closed displacement mask; not rescored'))
    selected = [r for r in out if r['original']['classification'] == 'INCLUDED' and r['horizontal_axis']]
    if len(selected) != 56 or not all(r['entire_interval_outside_original_mask'] for r in selected):
        raise ValueError('56 full concentration reading intervals do not reproduce outside-mask check')
    return out


def point_enclosure(pieces, x):
    return native_function(pieces, x).value(I(x)).floats()


def witnesses(row, candidates, native, declared=None):
    """Actual compatible coordinate/ordinate evaluations; padding is no witness."""
    old = row['original']
    _, _, width = widths(old)
    exact = I(old['publication'])+I(-width, width)
    low, high = exact.floats()
    if I(low).lo < exact.lo:
        low = float(np.nextafter(low, high))
    if I(high).hi > exact.hi:
        high = float(np.nextafter(high, low))
    horizontal = None
    if row['horizontal_axis']:
        axis = row['horizontal_axis']
        half = old['extraction_bounds'][axis+'_uncertainty']
        horizontal = I(old['coordinates'][axis])+I(-half, half)
    found = {}
    for x in sorted(set(candidates)):
        if horizontal is not None:
            if I(x).lo < horizontal.lo:
                x = float(np.nextafter(x, old['coordinates'][row['horizontal_axis']]))
            if I(x).hi > horizontal.hi:
                x = float(np.nextafter(x, old['coordinates'][row['horizontal_axis']]))
            if not horizontal.lo <= I(x).lo <= horizontal.hi:
                continue
        value = float(native(x))
        model_bounds = declared(x) if declared is not None else [value, value]
        closest = min(max(value, low), high)
        for d in (closest, low, high):
            signed = (I(value)-d).floats()
            # Guard only the demonstration against nominal-adapter roundoff;
            # this is not an uncertainty allowance or enlarged acceptance limit.
            guard = NOMINAL_ATOL if row['horizontal_axis'] else 0.
            judged = decision((I(*signed)+I(-guard, guard)).floats(), old['limit'])['threshold']
            certified = decision((I(*model_bounds)-d).floats(), old['limit'])['threshold']
            if judged != certified:
                continue
            label = 'acceptable' if judged == 'WITHIN_THROUGHOUT' else 'unacceptable' if judged == 'EXCEEDED_THROUGHOUT' else None
            if label and label not in found:
                found[label] = dict(coordinate=x, publication=d, model=value,
                                    residual=value-d, classification_guard=guard,
                                    declared_model_enclosure=model_bounds)
    return dict(demonstrated_threshold_sensitivity=len(found) == 2, examples=found,
                assumptions='Compatible marginal rectangle; not a shared calibration model or evidence of physical attainability')


def scalar_witnesses(rows):
    for r in rows:
        if r['new_status'] == 'RETAINED_SCALAR_COMPLETE':
            r['witnesses'] = witnesses(r, [0.], lambda x, v=r['original']['model']: v)
            for w in r['witnesses']['examples'].values():
                w['coordinate'] = None


def check_nominals(rows, run, adapter):
    """A readout failure is local to its family, never an archive rejection."""
    failures = {}
    for r in rows:
        previous = r['original']
        try:
            value, _, _, _ = historical.observe(run, previous)
            if value != previous['model']:
                raise ValueError('retained native observation differs from historical value')
            if previous['classification'] != 'INCLUDED' or not r['horizontal_axis']:
                continue
            if r['family'] in failures:
                raise ValueError('operation isolated after earlier nominal failure: '+failures[r['family']])
            coordinate = previous['coordinates'][r['horizontal_axis']]
            native = adapter.native(r['family'], previous['coordinates'], coordinate)
            error = abs(native-value)
            point = point_enclosure(adapter.pieces(r['family'], previous['coordinates'], coordinate, coordinate), coordinate)
            reduction_error = max(abs(v-value) for v in point)
            r['nominal_adapter'] = dict(native=native, historical=value, error=error, tolerance=NOMINAL_ATOL,
                                        declared_reduction=point, reduction_error=reduction_error,
                                        passed=max(error, reduction_error) <= NOMINAL_ATOL)
            if max(error, reduction_error) > NOMINAL_ATOL:
                failures[r['family']] = 'new adapter fails nominal reproduction'
        except (ValueError, KeyError) as exc:
            reason = str(exc)
            failures.setdefault(r['family'], reason)
            r['nominal_adapter'] = dict(passed=False, reason=reason, error=None, reduction_error=None,
                                        tolerance=NOMINAL_ATOL, failure_kind='READOUT_FAILURE')
    return failures


def summarize(rows):
    out = {}
    for identity in (*INPUTS, 'ALL_INPUT_ROWS'):
        selected = rows if identity == 'ALL_INPUT_ROWS' else [r for r in rows if r['input'] == identity]
        out[identity] = {}
        for family in (*historical.LIMITS, 'ALL_FAMILIES'):
            group = selected if family == 'ALL_FAMILIES' else [r for r in selected if r['family'] == family]
            included = [r for r in group if r['original']['classification'] == 'INCLUDED']
            out[identity][family] = dict(requested=len(group), historically_included=len(included),
                historically_excluded=len(group)-len(included), historically_unavailable=0,
                historical_status=dict(Counter(r['original']['status'] for r in group)),
                new_status=dict(Counter(r['new_status'] for r in group)),
                reading_available=sum(r['reading'] is not None for r in included),
                zero_exclusion=dict(Counter(r['reading']['zero_exclusion'] if r['reading'] else 'UNAVAILABLE' for r in included)),
                threshold=dict(Counter(r['reading']['threshold'] if r['reading'] else 'UNAVAILABLE' for r in included)),
                vertical_only_threshold=dict(Counter(r['vertical_only']['threshold'] for r in included)),
                vertical_only_zero_exclusion=dict(Counter(r['vertical_only']['zero_exclusion'] for r in included)),
                demonstrated_threshold_sensitivity=sum(bool(r['witnesses'] and r['witnesses']['demonstrated_threshold_sensitivity']) for r in included))
    return out


def execute(args):
    args.output.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    rows, old, prior, expected = verify_history()
    protocol = obs.sha(DOC/'PROTOCOL.md')
    review = read(args.review)
    implementation = {str(p.relative_to(ROOT)): obs.sha(p) for p in sorted((ROOT/'puckworks/analysis').glob('*reading_bounds_011*.py'))}
    if (review['protocol_sha256'] != protocol or review['implementation'] != implementation
            or review['bindings_sha256'] != obs.sha(DOC/'BINDINGS.json') or review['disposition'] != 'APPROVED'):
        raise ValueError('independent pre-propagation method audit does not bind candidate')
    result = dict(task=TASK, protocol_sha256=protocol, pre_propagation_review_sha256=obs.sha(args.review),
                  implementation=implementation, environment=obs.environment(), rows=retained_rows(rows),
                  admissions={}, pairs=[], new_trajectories=0, physical_validation='NOT_ESTABLISHED',
                  figure5='FIG5_REFERENCE_INCOMPLETE')
    result['components'] = dict(
        figure_reading=dict(status='RECORDED_MARGINAL_BOUNDS', source='publication_reference.json; target.extraction_bounds',
                            units='dimensionless concentration, depth or time as named', dependence='Same target perturbation for all arms; cross-target joint law unknown'),
        range_arithmetic=dict(status='OUTWARD_ENCLOSED', source='011 range module; 60-digit directed Decimal',
                              units='observable units', scope='New coefficient/range arithmetic; fixed-time native production state floats are inputs',
                              dependence='Direct paired function, no independence assumption', double_counted=False),
        instantaneous_readout_allowance=dict(value=None, reason='Not established for these new intervals'),
        comparator_time_readout=dict(status='CONDITIONAL_DISCRETE_INTERPOLANT', source='004 audit_run cup convention',
                                    scope='Event-split accepted-step linear; no instantaneous-error certificate'),
        refinement=dict(status='EMPIRICAL_SENSITIVITY_ONLY', source='Direct P1-P0 and C1-C0 at common coordinates'),
        continuum_error=dict(value=None, reason='No certified continuum bound'),
        source_provenance=dict(status='ORIGINAL_FIGURE_RUN_UNRESOLVED', source='009 HANDOFF crosswalk'))
    scalar_witnesses(result['rows'])
    write(args.output/'retained.json', result)
    print('A/B: historical 124/72/52/0 verified; retained reading results saved', flush=True)
    functions = {}
    for identity in INPUTS:
        tr = None
        current = [r for r in result['rows'] if r['input'] == identity]
        try:
            if obs.environment() != old['environment']:
                raise ValueError('historically bound numerical environment unavailable; retained-value results remain valid')
            loader = admission.admit_production if identity.startswith('P') else admission.admit_comparator
            run, receipt = loader(identity, args.evidence, prior)
            if receipt != expected[identity]:
                raise ValueError('admission differs from 009 bindings')
            result['admissions'][identity] = dict(status='ADMITTED', receipt=receipt, events=run['events'])
            if identity.startswith('P'):
                folder = args.evidence/('grudeva2026-spatial-resolution-006' if identity == 'P0' else 'grudeva2026-fine-baseline-qualification-007')
                path = folder/old['inputs'][identity]['metadata']['file']
                tr = obs.Trajectory(path) if identity == 'P0' else diagnostic.DiagnosticTrajectory(path)
                adapter = Production(tr)
                result['admissions'][identity]['captured_segments'] = [dict(
                    valid_interval=s.meta['valid_interval'], dense_side=s.meta['dense_side'],
                    terminal_underlying_step=s.step_bounds[-1].tolist(),
                    terminal_accepted_bracket=s.t[-2:].tolist()) for s in tr.segments]
            else:
                adapter = Comparator(run)
            result['admissions'][identity]['bracket_scope'] = 'Captured accepted support and event-side provenance; not a certified event-location error'
            # All nominal operations checked BEFORE horizontal propagation.
            failures = check_nominals(current, run, adapter)
            if isinstance(adapter, Comparator) and adapter._temporal_ready:
                result['admissions'][identity]['discrete_cup_consistency'] = adapter.cup_consistency
                j = int(np.flatnonzero(adapter.t == adapter.arrival)[0])
                result['admissions'][identity]['arrival_accepted_bracket'] = adapter.t[j-1:j+1].tolist()
            print(identity+': admission and nominal checks complete', flush=True)
            for r in current:
                previous = r['original']
                if previous['classification'] != 'INCLUDED' or not r['horizontal_axis']:
                    continue
                try:
                    if r['family'] in failures:
                        raise ValueError(failures[r['family']]+'; operation isolated')
                    low, high = r['horizontal_interval']
                    if not r['entire_interval_outside_original_mask']:
                        raise ValueError('interval crosses original closed mask')
                    pieces = adapter.pieces(r['family'], previous['coordinates'], low, high)
                    enclosed = range_pieces(pieces, low, high)
                    functions[(identity, r['target_id'])] = pieces
                    r['horizontal_model_range'], r['range_pieces'] = enclosed['bounds'], enclosed['pieces']
                    r['reading'] = residual(enclosed['bounds'], previous['publication'], previous['extraction_bounds']['c_uncertainty'], previous['limit'])
                    candidates = [low, high, previous['coordinates'][r['horizontal_axis']]]
                    for piece in enclosed['pieces']:
                        candidates.extend(piece['candidates'])
                        for x in (piece['low'], piece['high']):
                            candidates.extend([x, float(np.nextafter(x, low)), float(np.nextafter(x, high))])
                    candidates = [x for x in candidates if low <= x <= high]
                    r['witnesses'] = witnesses(r, candidates,
                        lambda x, reader=adapter: reader.native(r['family'], previous['coordinates'], x),
                        lambda x: point_enclosure(pieces, x))
                    r['new_status'] = 'DECLARED_READOUT_COMPLETE'
                    r['new_support'] = dict(mask_check=True, captured_support='FULL_INTERVAL',
                                            observation_operation='NOMINAL_REPRODUCED_AND_SYNTHETIC_RANGE_VERIFIED')
                    r['null_reasons']['horizontal'] = None
                    r['new_qualification'] = ('Native raw-state spatial reconstruction at fixed labeled time' if r['family'] == 'figure3_concentration' else
                                              'Retained BDF native-outlet polynomial' if identity.startswith('P') else
                                              'CONDITIONAL_ON_EVENT_SPLIT_ACCEPTED_STEP_LINEAR_INTERPOLANT')
                except ValueError as exc:
                    r['new_status'], r['unavailable_reason'] = 'HORIZONTAL_UNAVAILABLE', str(exc)
                    r['null_reasons']['horizontal'] = str(exc)
            del adapter, run
        except (OSError, ValueError) as exc:
            # Never publish private locators from operating-system messages.
            reason = 'Known archive unavailable at bound owner location' if isinstance(exc, OSError) else str(exc)
            if result['admissions'].get(identity, {}).get('status') == 'ADMITTED':
                result['admissions'][identity].update(readout_status='UNAVAILABLE', readout_reason=reason)
            else:
                result['admissions'][identity] = dict(status='UNAVAILABLE' if isinstance(exc, OSError) else 'NOT_ADMITTED', reason=reason)
            for r in current:
                if r['new_status'] == 'PENDING_HORIZONTAL':
                    r['new_status'], r['unavailable_reason'] = 'HORIZONTAL_UNAVAILABLE', reason
                    r['null_reasons']['horizontal'] = reason
        finally:
            if tr is not None:
                tr.close()
            gc.collect()
        write(args.output/'partial.json', result)
        print(identity+': individual results saved', flush=True)
    indexed = {(r['input'], r['target_id']): r for r in result['rows']}
    for first, second in PAIRS:
        for target in old['targets']:
            a, b = indexed[(first, target['target_id'])], indexed[(second, target['target_id'])]
            pair = dict(first=first, second=second, target_id=target['target_id'], family=target['family'],
                        range=None, pieces=None, reason=None, source_ordinate_cancels=True,
                        interpretation='Empirical sensitivity; no certified continuum bound')
            if any(r['original']['classification'] != 'INCLUDED' for r in (a, b)):
                pair.update(status='HISTORICALLY_EXCLUDED', reason='Required individual historical exclusion')
            elif a['horizontal_axis'] is None:
                pair.update(status='RETAINED_SCALAR_COMPLETE', range=(I(a['original']['model'])-b['original']['model']).floats())
            elif all((k, target['target_id']) in functions for k in (first, second)):
                low, high = a['horizontal_interval']
                try:
                    pieces = paired_pieces(functions[(first, target['target_id'])], functions[(second, target['target_id'])], low, high)
                    enclosed = range_pieces(pieces, low, high)
                    pair.update(status='DECLARED_READOUT_COMPLETE', range=enclosed['bounds'], pieces=enclosed['pieces'])
                except ValueError as exc:
                    pair.update(status='UNAVAILABLE', reason=str(exc))
            else:
                pair.update(status='UNAVAILABLE', reason='Required individual readout unavailable; no replacement by intersection')
            result['pairs'].append(pair)
        print(first+' minus '+second+': direct common-coordinate ranges complete', flush=True)
    result['summary'] = summarize(result['rows'])
    result['execution_seconds'] = time.monotonic()-start
    result['complete_under_declared_readouts'] = all(r['reading'] is not None for r in result['rows'] if r['original']['classification'] == 'INCLUDED') and all(p['status'] != 'UNAVAILABLE' for p in result['pairs'])
    result['continuum_accuracy'] = 'UNESTABLISHED'
    write(args.output/'results.json', result)
    with (args.output/'rows.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(result['rows'][0]))
        writer.writeheader()
        for row in result['rows']:
            writer.writerow({k: json.dumps(v, sort_keys=True, allow_nan=False) if isinstance(v, (dict, list)) or v is None else v for k, v in row.items()})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--review', required=True, type=Path)
    args = parser.parse_args()
    result = execute(args)
    print(json.dumps(result['summary']['ALL_INPUT_ROWS']['ALL_FAMILIES'], sort_keys=True))
    return 0 if result['complete_under_declared_readouts'] else 3


if __name__ == '__main__':
    raise SystemExit(main())

"""Figure-2 reading enclosures and exact finite-poset compatibility, research only.

No physical-flow reconstruction, model fitting, or experimental uncertainty model.
Run ``python -m puckworks.analysis.melrose2019bed_transient --output DIR``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / 'data' / 'melrose2019bed'
DEFAULT_OUTPUT = Path(__file__).resolve().parents[2] / 'docs/analysis/sci_md_melrose_transient_hydraulics_001'


def closure(ids, edges):
    """Reflexive transitive closure; reject unknown IDs, self edges and cycles."""
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate IDs')
    index = {p: i for i, p in enumerate(ids)}
    order = [[i == j for j in range(len(ids))] for i in range(len(ids))]
    for a, b in edges:
        if a not in index or b not in index or a == b:
            raise ValueError('invalid strict edge')
        order[index[a]][index[b]] = True
    for k in range(len(ids)):
        for i in range(len(ids)):
            for j in range(len(ids)):
                order[i][j] |= order[i][k] and order[k][j]
    if any(order[i][j] and order[j][i] for i in range(len(ids)) for j in range(i)):
        raise ValueError('cyclic temporal order')
    return order


def compatibility(points, edges):
    """Exact inequalities for declared finite rectangular intervals and order.

    Decisions use input floats without display rounding or tolerance. Witness
    roundoff is checked separately in tests, never used to change a verdict.
    The expansion is an algebraic discrepancy, not an experimental error bar.
    """
    ids = [p['point_id'] for p in points]
    for p in points:
        lo, hi = p['lower'], p['upper']
        if not (math.isfinite(lo) and math.isfinite(hi) and lo <= hi):
            raise ValueError('invalid interval')
        c = p.get('central')
        if c is not None and not (math.isfinite(c) and lo <= c <= hi):
            raise ValueError('invalid central estimate')
    order = closure(ids, edges)
    n = len(ids)
    pairs = [(i, j) for i in range(n) for j in range(n) if i != j and order[i][j]]
    triples = [(i, j, k) for i, j in pairs for k in range(n)
               if k != j and order[j][k]]
    eligibility = ('no_data' if not n else 'single_point' if n == 1 else
                   'order_free' if not pairs else 'informative_temporal')
    if not n:
        return dict(eligibility=eligibility, point_count=0, comparable_pairs=0,
                    supported_chains=0, nondecreasing=None, nonincreasing=None,
                    constant=None, D_up=None, D_down=None, delta_up=None,
                    delta_down=None, delta_constant=None, decline_recovery=[])
    lo = [p['lower'] for p in points]
    hi = [p['upper'] for p in points]

    def margin(reverse):
        values = [(lo[j]-hi[i] if reverse else lo[i]-hi[j], i, j) for i, j in pairs]
        # Stable IDs break exact ties, independently of iteration order.
        values.sort(key=lambda v: (-v[0], ids[v[1]], ids[v[2]]))
        if not values or values[0][0] <= 0:
            return 0.0, None
        d, i, j = values[0]
        return d, dict(earlier=ids[i], later=ids[j], lower=lo[j] if reverse else lo[i],
                      upper=hi[i] if reverse else hi[j], difference=d,
                      order_support='transitive_closure_of_retained_edges')

    du, wu = margin(False)
    dd, wd = margin(True)
    gap = max(0.0, max(lo)-min(hi))

    def witness(reverse, delta):
        return {ids[j]: max(lo[i]-delta for i in range(n)
                           if (order[j][i] if reverse else order[i][j])) for j in range(n)}

    dr = [dict(earlier=ids[i], trough=ids[j], later=ids[k],
               decline_margin=lo[i]-hi[j], recovery_margin=lo[k]-hi[j])
          for i, j, k in triples if lo[i] > hi[j] and lo[k] > hi[j]]
    dr.sort(key=lambda r: (r['earlier'], r['trough'], r['later']))
    return dict(
        eligibility=eligibility, point_count=n, comparable_pairs=len(pairs),
        supported_chains=len(triples), nondecreasing=du == 0,
        nonincreasing=dd == 0, constant=gap == 0,
        D_up=du, D_down=dd, delta_up=du/2, delta_down=dd/2, delta_constant=gap/2,
        decline_witness=wu, increase_witness=wd,
        constant_extremes=dict(max_lower_point=min(ids[i] for i in range(n) if lo[i] == max(lo)),
                               min_upper_point=min(ids[i] for i in range(n) if hi[i] == min(hi)),
                               gap=gap),
        witness_up=witness(False, 0) if du == 0 else None,
        witness_down=witness(True, 0) if dd == 0 else None,
        witness_constant=max(lo) if gap == 0 else None,
        expanded_witness_up=witness(False, du/2),
        expanded_witness_down=witness(True, dd/2),
        expanded_witness_constant=max(lo)-gap/2,
        decline_recovery=dr,
        supported_pairs=[[ids[i], ids[j]] for i, j in pairs],
        rectangular_interpretation={
            'nondecreasing': 'excluded' if du > 0 else 'not_excluded_by_relaxation',
            'nonincreasing': 'excluded' if dd > 0 else 'not_excluded_by_relaxation',
            'constant': 'excluded' if gap > 0 else 'not_excluded_by_relaxation'},
        joint_witness_status='NOT_TESTED',
    )


def affine_enclosure(pixel_bounds, anchors, values):
    """All corners of a monotone affine calibration (shared uncertain anchors)."""
    a, b = anchors
    if a[1] >= b[0]:
        raise ValueError('calibration anchors not separated')
    if not all(math.isfinite(v) for v in (*pixel_bounds, *a, *b, *values)):
        raise ValueError('nonfinite calibration')
    if pixel_bounds[0] > pixel_bounds[1]:
        raise ValueError('reversed pixel bounds')
    vals = [values[0]+(x-aa)*(values[1]-values[0])/(bb-aa)
            for x, aa, bb in itertools.product(pixel_bounds, a, b)]
    return min(vals), max(vals)


def _write_csv(path, rows, fields=None):
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


def recover(data=DATA):
    contract = json.loads((data/'contract.json').read_text())
    profiles = json.loads((data/'profiles.json').read_text())
    by_id = {p['profile_id']: p for p in profiles}
    cal = contract['calibration']
    rows = []
    for r in csv.DictReader((data/'source_coordinates.csv').open()):
        p = by_id[r['profile_id']]
        x0, x1, y0, y1 = [float(r[k]) for k in ['x_min', 'x_max', 'y_min', 'y_max']]
        guard = cal['raster_guard_px']
        tl, tu = affine_enclosure((x0-guard, x1+guard), cal['x_anchors'], [0, 100])
        ql, qu = affine_enclosure((y0-guard, y1+guard), cal['y_anchors'], [6, 0])
        xc = float(r['x_center']) if r['x_center'] else None
        yc = float(r['y_center']) if r['y_center'] else None
        if xc is not None and not x0 <= xc <= x1:
            raise ValueError('x center outside glyph')
        if yc is not None and not y0 <= yc <= y1:
            raise ValueError('y center outside glyph')
        t = None if xc is None else (xc-80)*100/820
        q = None if yc is None else (548-yc)*6/490
        rows.append(dict(source_id=contract['source_id'], figure_id='Figure_2',
                         profile_id=r['profile_id'], condition_id=p['condition_id'],
                         identity_candidates=';'.join(p['identity_candidates']),
                         point_id=r['point_id'], x_min=x0, x_max=x1, y_min=y0, y_max=y1,
                         x_center=xc, y_center=yc, time_s=t, time_lower_s=tl, time_upper_s=tu,
                         flow_ml_s=q, lower_ml_s=ql, upper_ml_s=qu,
                         flow_m3_s=None if q is None else q*1e-6,
                         lower_m3_s=ql*1e-6, upper_m3_s=qu*1e-6,
                         source_units='mL/s; s', calibration_reference='native_jpeg_affine_1',
                         order_eligibility='separated_display_times_with_collection_sequence_support',
                         inclusion_status='retained', reason=r['reason']))
    if len({r['point_id'] for r in rows}) != len(rows):
        raise ValueError('duplicate source point')
    return contract, profiles, rows


def analyze(data=DATA):
    contract, profiles, rows = recover(data)
    results = []
    for p in profiles:
        points = [r for r in rows if r['profile_id'] == p['profile_id']]
        edges = [(a['point_id'], b['point_id']) for a in points for b in points
                 if a['time_upper_s'] < b['time_lower_s']]
        result = compatibility([dict(point_id=r['point_id'], lower=r['lower_ml_s'],
                                     upper=r['upper_ml_s'], central=r['flow_ml_s']) for r in points], edges)
        result.update(p)
        result.update(
                      source_id=contract['source_id'], figure_id='Figure_2',
                      observer_contract_reference='contract.json#/observer',
                      preparation_contract_reference='contract.json#/preparation',
                      pressure_statement_reference='contract.json#/pressure',
                      preprint_reported_applied_overpressure_bar=contract['pressure']['preprint_bar'][p['pressure_regime']],
                      pressure_value_applicability='REPORTED_PREPRINT_VALUE; THESIS_MAPPING_DISCREPANCY_UNRESOLVED',
                      collection_interval_endpoints=None, replicate_membership=None, replicate_weights=None,
                      order_edges=edges, order_support='disjoint_time_enclosures_and_sequential_aliquots',
                      aggregation_status=contract['observer']['aggregation_status'],
                      collection_order_support='campaign_methods; exact endpoints unknown',
                      hydraulic_applicability='UNQUALIFIED',
                      physical_validation='NOT_ESTABLISHED',
                      jointly_admissible_monotone_witness='NOT_TESTED',
                      uncertainty_model='rectangular_outer_envelope_of_shared_calibration',
                      delta_interpretation='exact_uniform_rectangular_expansion_only',
                      units='mL/s; SI values in normalized observations',
                      early_thermal_relation='first HF reading near reported 5–10 s transient; '
                      'LF first reading near its reported end; interval endpoints unknown; '
                      'later outlet temperature does not establish isothermality')
        results.append(result)
    coverage = []
    for condition in contract['intended_conditions']:
        confirmed = [r for r in results if r['condition_id'] == condition]
        candidate = [r for r in results if condition in r['identity_candidates'] and not r['condition_id']]
        status = ('confirmed_represented_partial_recovery' if confirmed else
                  'ambiguous_mapping' if candidate else 'not_distinguishable_in_figure')
        coverage.append(dict(condition_id=condition, status=status,
                             confirmed_profile_ids=';'.join(r['profile_id'] for r in confirmed),
                             candidate_profile_ids=';'.join(r['profile_id'] for r in candidate),
                             retained_condition_assigned_points=sum(r['point_count'] for r in confirmed),
                             candidate_points_not_credited=sum(r['point_count'] for r in candidate),
                             nondecreasing=confirmed[0]['nondecreasing'] if len(confirmed) == 1 else None,
                             nonincreasing=confirmed[0]['nonincreasing'] if len(confirmed) == 1 else None,
                             constant=confirmed[0]['constant'] if len(confirmed) == 1 else None,
                             eligibility=confirmed[0]['eligibility'] if len(confirmed) == 1 else 'condition_unresolved',
                             hydraulic_applicability='UNQUALIFIED', aggregation_status='UNSPECIFIED_PUBLISHED_AGGREGATE',
                             physical_validation='NOT_ESTABLISHED'))
    inputs = ['contract.json', 'profiles.json', 'source_coordinates.csv', 'ambiguous_regions.csv']
    output = dict(task='SCI-MD-MELROSE-TRANSIENT-HYDRAULICS-001',
                  classification=['G1', 'NO_GOVERNING_PHYSICS_CHANGE', 'RESEARCH_ONLY',
                                  'RETROSPECTIVE', 'TARGET_EXPOSED', 'SOURCE_INTERNAL'],
                  physical_validation='NOT_ESTABLISHED', implementation_base=contract['implementation_base'],
                  source_hashes=contract['source_hashes'],
                  input_sha256={f: hashlib.sha256((data/f).read_bytes()).hexdigest() for f in inputs},
                  units='mL/s', profile_results=results, condition_coverage=coverage,
                  coverage=dict(intended_conditions=len(coverage), observed_profile_fragments=len(results),
                                condition_assigned_profiles=sum(bool(r['condition_id']) for r in results),
                                retained_points=len(rows), confirmed_conditions=sum(bool(c['confirmed_profile_ids']) for c in coverage),
                                physically_qualified_profiles=0, obscured_point_count=None,
                                distinguishable_trace_lower_bound=12,
                                total_source_profiles=None),
                  ewp_reference=dict(commit='aace2cc6b6c2a393d2dbfb0274104192ca6c7203',
                                     conclusion='UNRESOLVED_BOUNDED_ANALYSIS', line_pressure='NOT_ASSESSED'),
                  missing_facts=contract['missing_facts'])
    return output, rows, coverage


def write(output, data=DATA, observations_output=None):
    output.mkdir(parents=True, exist_ok=True)
    result, rows, coverage = analyze(data)
    (output/'RESULT.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    _write_csv(observations_output or output/'observations.csv', rows)
    _write_csv(output/'condition_results.csv', coverage)
    fields = ['profile_id', 'condition_id', 'eligibility', 'point_count', 'comparable_pairs',
              'supported_chains', 'nondecreasing', 'nonincreasing', 'constant', 'D_up', 'D_down',
              'delta_up', 'delta_down', 'delta_constant', 'aggregation_status', 'hydraulic_applicability',
              'uncertainty_model', 'jointly_admissible_monotone_witness']
    summary = [{k: r[k] for k in fields} for r in result['profile_results']]
    for row, r in zip(summary, result['profile_results']):
        row['decline_recovery_triples'] = len(r['decline_recovery'])
    _write_csv(output/'profile_results.csv', summary)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = write(args.output, observations_output=DATA/'observations.csv'
                   if args.output == DEFAULT_OUTPUT else None)
    print(json.dumps(result['coverage'], sort_keys=True))

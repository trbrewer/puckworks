"""Exact finite density normalization under the retained Figure 6.2 reading contract.

Research only; retrospective, target exposed, source internal and nonscoring.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No constitutive or joint-calibration solver.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from fractions import Fraction as F
from itertools import combinations, product
import json
from pathlib import Path

from puckworks.analysis import corrochano2017_density_shift as inherited
from puckworks.analysis import corrochano2017_dry_compaction as geometry

ROOT = geometry.ROOT
OUTPUT = ROOT / 'docs/analysis/sci_md_corrochano_density_normalization_001'
CONTRACT = OUTPUT / 'calculation_contract.json'
TASK = 'SCI-MD-CORROCHANO-DENSITY-NORMALIZATION-001'
TABLES = ['density_at_force_coordinates', 'sample_density_ratios', 'sample_pair_contrasts',
          'grind_ratio_envelopes', 'cross_grind_comparisons']
SUCCESS = 'FEASIBLE_AT_DECLARED_FORCE_LEVELS_BY_EXPLICIT_WITNESS'
NO_CERTIFICATE = 'NO_CERTIFICATE_FOUND_BY_DECLARED_CONSTRUCTION'


def authenticate():
    fixed = json.loads(CONTRACT.read_text())
    inherited.authenticate()
    if inherited.sha256(OUTPUT/'PLAN.md') != fixed['plan_sha256']:
        raise ValueError('Plan identity changed')
    for name, digest in fixed['preserved_file_hashes'].items():
        if inherited.sha256(ROOT/name) != digest:
            raise ValueError(f'Protected evidence changed: {name}')
    previous = json.loads((inherited.OUTPUT/'calculation_contract.json').read_text())
    if previous['inherited_input_hashes'] != fixed['inherited_input_hashes']:
        raise ValueError('Accepted input identities changed')
    return fixed


def calibration(contract):
    """Independent anchor rectangle, with no independence claim for beta and tau."""
    result = inherited.calibration(contract)  # proves beta positive on entire set
    r0, r1 = result['density_values_kg_m3']
    p0, p1 = result['downward_positions_pt']
    guard = result['independent_anchor_allowance_pt']
    values = [(r1*(p0+e0)-r0*(p1+e1))/(r1-r0)
              for e0, e1 in product((-guard, guard), repeat=2)]
    result['tau_pt'] = (min(values), max(values))
    result['tau_display_pt'] = geometry.outward(result['tau_pt'])
    result['positive_separation_pt'] = (p0-p1-2*guard, p0-p1+2*guard)
    return result


def divide_positive(numerator, denominator):
    """Signed interval division; denominator is a strictly positive enclosure."""
    if numerator[0] > numerator[1] or not 0 < denominator[0] <= denominator[1]:
        raise ValueError('Invalid interval or nonpositive denominator')
    values = [a/b for a, b in product(numerator, denominator)]
    return min(values), max(values)


def ratio_bounds(before, after, tau):
    if before[0] > before[1] or after[0] > after[1] or tau[0] > tau[1]:
        raise ValueError('Reversed enclosure')
    if before[0]+tau[0] <= 0:
        raise ValueError('Nonpositive density-ratio denominator')
    values = [(b+t)/(a+t) for a, b, t in product(before, after, tau)]
    return min(values), max(values)


def determinant_bounds(ia, ib, ja, jb, tau):
    """Multiaffine C; its extrema on the outer rectangle are among 32 corners."""
    for box in (ia, ib, ja, jb, tau):
        if box[0] > box[1]:
            raise ValueError('Reversed enclosure')
    if any(box[0]+tau[0] <= 0 for box in (ia, ib, ja, jb)):
        raise ValueError('Nonpositive shifted density enclosure')
    values = [b*c-d*a+t*(b+c-d-a)
              for a, b, c, d, t in product(ia, ib, ja, jb, tau)]
    return min(values), max(values)


def qualify_coordinate_readings(readings):
    numerical = any(r['status'] == 'NUMERICALLY_UNRESOLVED' for r in readings)
    full = all(inherited.qualified(r) for r in readings)
    ambiguous = any(r['status'] == 'AMBIGUOUS' for r in readings)
    return dict(full_support=full, ambiguous=ambiguous,
                status=('NUMERICALLY_UNRESOLVED' if numerical else 'UNSUPPORTED' if not full
                        else 'AMBIGUOUS' if ambiguous else 'SUPPORTED'),
                reason='QUALIFIED_OUTER_ENCLOSURE' if full else ';'.join(
                    r.get('id', 'endpoint')+':'+r['reason'] for r in readings
                    if not inherited.qualified(r)))


def density_ratio(before, after, tau):
    r = qualify_coordinate_readings([before, after])
    r.update(bounds_ratio=None, display_ratio=None)
    if r['full_support']:
        try:
            r['bounds_ratio'] = ratio_bounds(before['bounds_pt'], after['bounds_pt'], tau)
            r['display_ratio'] = geometry.outward(r['bounds_ratio'])
        except (ArithmeticError, ValueError) as exc:
            r.update(status='NUMERICALLY_UNRESOLVED' if isinstance(exc, ArithmeticError)
                     else 'INVALID_POSITIVITY_OR_ENCLOSURE', reason=str(exc), full_support=False)
    return r


def density_ratio_contrast(ia, ib, ja, jb, tau):
    r = qualify_coordinate_readings([ia, ib, ja, jb])
    r.update(difference_orientation='first_minus_second', determinant_pt2=None,
             determinant_display_pt2=None, denominator_pt2=None, ratio_difference=None,
             ratio_difference_display=None, sign=None)
    if r['full_support']:
        try:
            aa, ab, ba, bb = [v['bounds_pt'] for v in [ia, ib, ja, jb]]
            c = determinant_bounds(aa, ab, ba, bb, tau)
            # Both factors are positive and increasing in their coordinate and shared tau.
            den = ((aa[0]+tau[0])*(ba[0]+tau[0]),
                   (aa[1]+tau[1])*(ba[1]+tau[1]))
            direct = divide_positive(c, den)
            r.update(determinant_pt2=c, determinant_display_pt2=geometry.outward(c),
                     denominator_pt2=den, ratio_difference=direct,
                     ratio_difference_display=geometry.outward(direct),
                     sign=1 if c[0] > 0 else -1 if c[1] < 0 else 0)
        except (ArithmeticError, ValueError) as exc:
            r.update(status='NUMERICALLY_UNRESOLVED' if isinstance(exc, ArithmeticError)
                     else 'INVALID_POSITIVITY_OR_ENCLOSURE', reason=str(exc), full_support=False)
    r['classification'] = ('STRICTLY_SEPARATED' if r['sign'] in (-1, 1) else
                           'NOT_EXCLUDED_BY_THIS_COMPARISON' if r['full_support'] else
                           'UNSUPPORTED_OR_INCOMPLETE' if r['status'] == 'UNSUPPORTED'
                           else r['status'])
    return r


def disposition(rows, expected):
    if any(r['classification'] == 'STRICTLY_SEPARATED' for r in rows):
        return 'EXCLUDED_BY_SAMPLE_RATIO_CONTRAST'
    if len(rows) == expected and all(r['classification'] == 'NOT_EXCLUDED_BY_THIS_COMPARISON'
                                     for r in rows):
        return 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'
    return 'UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'


def envelope(ratios, expected):
    present = [s for s in expected if s in ratios and ratios[s]['full_support']]
    missing = [s for s in expected if s not in present]
    bounds = geometry.hull(ratios[s]['bounds_ratio'] for s in present)
    return dict(completeness='INCOMPLETE' if missing else 'COMPLETE', present=present,
                missing=missing, full_support=not missing, descriptive_only=bool(missing),
                ambiguous_members=[s for s in present if ratios[s]['ambiguous']],
                bounds_ratio=bounds, display_ratio=geometry.outward(bounds))


def grind_comparison(first, second, pairs):
    """Every one of nine cross-sample contrasts must order in the same direction."""
    full = first['full_support'] and second['full_support'] and len(pairs) == 9 and all(
        r['full_support'] for r in pairs)
    signs = {r['sign'] for r in pairs}
    sign = next(iter(signs)) if full and signs in ({1}, {-1}) else 0 if full else None
    marginal = geometry.subtract(first['bounds_ratio'], second['bounds_ratio']) if full else None
    return dict(full_support=full, ambiguous=any(r['ambiguous'] for r in pairs),
                sign=sign, difference_orientation='first_minus_second',
                classification='UNSUPPORTED_OR_INCOMPLETE' if not full else
                'STRICTLY_SEPARATED' if sign else 'NOT_EXCLUDED_BY_THIS_COMPARISON',
                sample_contrast_refs=[r['id'] for r in pairs],
                sample_sign_counts=dict(Counter(str(r['sign']) for r in pairs)),
                marginal_envelope_difference=marginal,
                marginal_display=geometry.outward(marginal),
                marginal_envelope_classification='UNSUPPORTED_OR_INCOMPLETE' if not full else
                'STRICTLY_SEPARATED' if marginal[0] > 0 or marginal[1] < 0 else
                'OVERLAPPING_OR_CONTACTING')


def source_segments(paths, traces):
    """Attach stable raw-source references to the already authenticated path order."""
    chunks = {c['chunk']: c for c in paths['chunks']}
    joins = {(j['trace'], j['left'], j['right']) for j in paths['joins']}
    result = {}
    for sample in traces:
        chain = paths['trace_chunks'][sample]
        records, previous = [], None
        for cid in chain:
            if (sample, previous, cid) in joins:
                records.append(dict(kind='APPROVED_JOIN', left_chunk=previous, right_chunk=cid,
                                    source_ref=f'paths.json:join:{sample}:{previous}:{cid}'))
            for vertex in range(chunks[cid]['vertex_count']-1):
                records.append(dict(kind='ORIGINAL', chunk=cid, vertex_from=vertex,
                                    vertex_to=vertex+1,
                                    source_ref=f'coordinates.csv:{cid}:{vertex}:{vertex+1}'))
            previous = cid
        if len(records) != len(traces[sample]):
            raise ValueError(f'Segment accounting differs: {sample}')
        for index, (record, (a, b)) in enumerate(zip(records, traces[sample])):
            record.update(index=index, endpoints_xz=((a[0], -a[1]), (b[0], -b[1])))
        result[sample] = records
    return result


def feasible_parameter(endpoints, x, z, allowance):
    """Intersection of t constraints for BOTH coordinates, including constants/reversals."""
    if allowance < 0:
        raise ValueError('Negative trace allowance')
    low, high = F(0), F(1)
    a, b = endpoints
    for k, target in enumerate((x, z)):
        delta = b[k]-a[k]
        if delta == 0:
            if abs(a[k]-target) > allowance:
                return None
        else:
            u, v = sorted(((target-allowance-a[k])/delta,
                           (target+allowance-a[k])/delta))
            low, high = max(low, u), min(high, v)
            if low > high:
                return None
    return low, high


def recover(segments, x, z, allowance):
    for segment in segments:
        bounds = feasible_parameter(segment['endpoints_xz'], x, z, allowance)
        if bounds is not None:
            t = sum(bounds)/2
            a, b = segment['endpoints_xz']
            source = tuple(a[k]+t*(b[k]-a[k]) for k in (0, 1))
            return dict(segment=segment, feasible_t=bounds, t=t,
                        source_x_pt=source[0], source_z_pt=source[1], nominal_x_pt=x,
                        dx_pt=x-source[0], dz_pt=z-source[1], selected_z_pt=z,
                        path_position=segment['index']+t)
    raise ValueError('NO_ADMITTED_SOURCE_POINT')


def verify_assignment(witness, segments, force_axis):
    """Producer-side fail-visible checks; independent raw-operand review is separate."""
    parameters, levels, readings, certs = [witness[key] for key in
                                          ('parameters', 'levels', 'readings', 'certificates')]
    expected_samples = list(segments)
    expected_forces = [25, 50, 100, 150, 200, 250]
    if ([p['trace'] for p in parameters] != expected_samples or len(parameters) != 12
            or [h['force_N'] for h in levels] != expected_forces or len(levels) != 6
            or len(witness['intersections']) != 4):
        raise ValueError('COMMON_PARAMETER_OR_LEVEL_ACCOUNTING')
    if levels[0]['h'] != 0 or levels[-1]['h'] != 1 or any(
            a['h'] >= b['h'] for a, b in zip(levels, levels[1:])):
        raise ValueError('SHARED_LEVEL_GAUGE_OR_ORDER')
    pp = {p['trace']: p for p in parameters}
    hh = {h['force_N']: h for h in levels}
    rr = {(r['trace'], r['force_N']): r for r in readings}
    keys = [(s, f) for s in expected_samples for f in expected_forces]
    if (len(certs) != 72 or {(c['trace'], c['force_N']) for c in certs} != set(keys)
            or len(readings) != 72 or set(rr) != set(keys)):
        raise ValueError('READING_OR_CERTIFICATE_ACCOUNTING')
    cal = witness['calibration']
    alpha, beta, allowance = cal['alpha'], cal['beta'], cal['trace_allowance_pt']
    if beta <= 0:
        raise ValueError('NONPOSITIVE_CALIBRATION')
    positions = {}
    for c in certs:
        row_id = c['id']
        s, f = c['trace'], c['force_N']
        p, h, r = pp[s], hh[f], rr[s, f]
        if p['a_pt'] <= 0 or p['s_kg_m3'] <= 0:
            raise ValueError(f'{row_id}:NONPOSITIVE_AMPLITUDE')
        if not inherited.qualified(r):
            raise ValueError(f'{row_id}:UNSUPPORTED_READING')
        for key in ('c_pt', 'a_pt', 'b_kg_m3', 's_kg_m3'):
            if c[key] != p[key]:
                raise ValueError(f'{row_id}:PARAMETER_SUBSTITUTION:{key}')
        if (c['h'] != h['h'] or c['level_ref'] != h['id'] or
                c['parameter_ref'] != p['id'] or c['reading_ref'] != r['id']):
            raise ValueError(f'{row_id}:SHARED_REFERENCE_MISMATCH')
        z = c['selected_z_pt']
        if not geometry.contains(r['components_z_pt'], (z, z)):
            raise ValueError(f'{row_id}:HULL_GAP_OR_COMPONENT_FAILURE')
        if (not 0 <= c['component_index'] < len(r['components_z_pt']) or
                c['component_z_pt'] != r['components_z_pt'][c['component_index']]):
            raise ValueError(f'{row_id}:COMPONENT_REFERENCE')
        selected = c['segment']
        index, t = selected['index'], c['t']
        if not 0 <= index < len(segments[s]) or selected != segments[s][index] or not 0 <= t <= 1:
            raise ValueError(f'{row_id}:SEGMENT_MEMBERSHIP')
        a, b = selected['endpoints_xz']
        x0, z0 = (a[k]+t*(b[k]-a[k]) for k in (0, 1))
        x = force_axis.coordinate(f)
        if (c['source_x_pt'] != x0 or c['source_z_pt'] != z0 or c['nominal_x_pt'] != x
                or c['dx_pt'] != x-x0 or c['dz_pt'] != z-z0
                or abs(x-x0) > allowance or abs(z-z0) > allowance):
            raise ValueError(f'{row_id}:SOURCE_OR_DISPLACEMENT')
        if c['path_position'] != index+t:
            raise ValueError(f'{row_id}:PATH_POSITION')
        positions[s, f] = index+t
        if not (c['density_kg_m3'] == alpha+beta*z == p['b_kg_m3']+p['s_kg_m3']*h['h']
                and z == p['c_pt']+p['a_pt']*h['h'] and c['density_kg_m3'] > 0
                and p['b_kg_m3'] == alpha+beta*p['c_pt'] and p['s_kg_m3'] == beta*p['a_pt']):
            raise ValueError(f'{row_id}:AFFINE_IDENTITY')
    for s in expected_samples:
        if any(positions[s, a] >= positions[s, b] for a, b in zip(expected_forces, expected_forces[1:])):
            raise ValueError(f'{s}:PATH_ORDER')
    return dict(status='VERIFIED', certificates=72, identities=72, positive_amplitudes=12,
                common_levels=6, intermediate_intersections=4, common_calibrations=1)


def affine_witness(contract, paths, traces):
    w = dict(disposition=NO_CERTIFICATE, failure=None, parameters=[], levels=[], intersections=[],
             readings=[], certificates=[], verification=None)
    stage = 'calibration'
    try:
        allowance = F(contract['trace_guard_pt'])
        axes = {name: geometry.Axis(c, F(0), allowance) for name, c in contract['axes'].items()}
        density = axes['density']
        beta = (density.v1-density.v0)/(density.p0-density.p1)
        alpha = density.v0+beta*density.p0
        if beta <= 0:
            raise ValueError('NONPOSITIVE_NOMINAL_DENSITY_SLOPE')
        w['calibration'] = dict(force_values_N=[axes['force'].v0, axes['force'].v1],
                                force_positions_pt=[axes['force'].p0, axes['force'].p1],
                                density_values_kg_m3=[density.v0, density.v1],
                                downward_density_positions_pt=[density.p0, density.p1],
                                alpha=alpha, beta=beta, trace_allowance_pt=allowance)
        segments = source_segments(paths, traces)
        readings = {}
        forces = contract['force_targets_N']
        for sample, ss in traces.items():
            for force in forces:
                stage = f'nominal:{sample}:{force}'
                r = inherited.read_coordinates(ss, force, axes['force'], axes['density'])
                r.update(id=stage, trace=sample, grind=sample[0], force_N=force)
                readings[sample, force] = r
                w['readings'].append(r)
                if not inherited.qualified(r):
                    raise ValueError(r['reason'])
        params = {}
        for sample in traces:
            stage = f'parameter:{sample}'
            start, end = readings[sample, 25], readings[sample, 250]
            c = sum(start['bounds_pt'])/2
            a = sum(end['bounds_pt'])/2-c
            p = dict(id=stage, trace=sample, grind=sample[0], c_pt=c, a_pt=a,
                     b_kg_m3=alpha+beta*c, s_kg_m3=beta*a,
                     endpoint_refs=[start['id'], end['id']])
            w['parameters'].append(p)
            params[sample] = p
            if a <= 0:
                raise ValueError('NONPOSITIVE_AMPLITUDE')
        for force in forces:
            stage = f'intersection:{force}'
            if force in (25, 250):
                h = F(0) if force == 25 else F(1)
            else:
                members = [dict(trace=s, reading_ref=readings[s, force]['id'],
                                parameter_ref=params[s]['id'],
                                bounds=tuple((v-params[s]['c_pt'])/params[s]['a_pt']
                                             for v in readings[s, force]['bounds_pt'])) for s in traces]
                bounds = (max(m['bounds'][0] for m in members), min(m['bounds'][1] for m in members))
                h = sum(bounds)/2 if bounds[0] <= bounds[1] else None
                w['intersections'].append(dict(id=stage, force_N=force, bounds=bounds,
                                               selected_h=h, members=members))
                if h is None:
                    raise ValueError('EMPTY_COMMON_INTERSECTION')
            w['levels'].append(dict(id=f'level:{force}', force_N=force, h=h))
        if any(a['h'] >= b['h'] for a, b in zip(w['levels'], w['levels'][1:])):
            raise ValueError('NONINCREASING_SHARED_LEVELS')
        for sample in traces:
            p = params[sample]
            for level in w['levels']:
                force, h = level['force_N'], level['h']
                stage = f'certificate:{sample}:{force}'
                z = p['c_pt']+p['a_pt']*h
                r = readings[sample, force]
                if not geometry.contains(r['components_z_pt'], (z, z)):
                    raise ValueError('HULL_GAP_OR_COMPONENT_FAILURE')
                component = next(i for i, (lo, hi) in enumerate(r['components_z_pt']) if lo <= z <= hi)
                cert = recover(segments[sample], axes['force'].coordinate(force), z, allowance)
                cert.update(id=stage, trace=sample, grind=sample[0], force_N=force,
                            density_kg_m3=alpha+beta*z, component_index=component,
                            component_z_pt=r['components_z_pt'][component], reading_ref=r['id'],
                            parameter_ref=p['id'], level_ref=level['id'], h=h,
                            **{key: p[key] for key in ('c_pt', 'a_pt', 'b_kg_m3', 's_kg_m3')})
                w['certificates'].append(cert)
        stage = 'assignment_verification'
        w['verification'] = verify_assignment(w, segments, axes['force'])
        w['disposition'] = SUCCESS
    except (ArithmeticError, ValueError) as exc:
        w['failure'] = dict(row=stage, reason=f'{type(exc).__name__}: {exc}',
                            arithmetic_failure=isinstance(exc, ArithmeticError))
    return w


def analyze():
    fixed = authenticate()
    contract, paths, axes, traces = geometry.load()
    if list(traces) != fixed['samples'] or contract['force_targets_N'] != fixed['forces_N']:
        raise ValueError('Fixed reporting set differs')
    cal = calibration(contract)
    tau = cal['tau_pt']
    tables = {key: [] for key in TABLES}
    readings = {}
    for sample in fixed['samples']:
        for force in fixed['forces_N']:
            try:
                r = inherited.read_coordinates(traces[sample], force, axes['force'], axes['density'])
            except ArithmeticError as exc:
                r = inherited.numerical_failure(exc)
            r.update(id=f'z:{sample}:{force}', trace=sample, grind=sample[0], force_N=force,
                     source_chunks=paths['trace_chunks'][sample],
                     source_reference='coordinates.csv + paths.json; Figure6.2 printed223/PDF248/index247')
            tables[TABLES[0]].append(r)
            readings[sample, force] = r
    replay = inherited.replay(tables[TABLES[0]])
    # Check the second predecessor's coordinate enclosures too, as verification only.
    with (inherited.OUTPUT/'density_at_force_coordinates.csv').open() as stream:
        old = {r['id']: r for r in csv.DictReader(stream)}
    for r in tables[TABLES[0]]:
        if r['status'] != 'NUMERICALLY_UNRESOLVED':
            previous = old[r['id']]
            saved = json.loads(previous['bounds_pt']) if previous['bounds_pt'] else None
            saved = tuple(map(F, saved)) if saved else None
            if r['bounds_pt'] != saved or r['status'] != previous['status']:
                raise ValueError(f'Density-shift coordinate replay differs: {r["id"]}')
    intervals = []
    for a, b in fixed['intervals_N']:
        ratios, envelopes, pairs = {}, {}, []
        for sample in fixed['samples']:
            before, after = readings[sample, a], readings[sample, b]
            r = dict(id=f'ratio:{sample}:{a}:{b}', trace=sample, grind=sample[0],
                     force_from_N=a, force_to_N=b, endpoints=[before['id'], after['id']],
                     **density_ratio(before, after, tau))
            tables[TABLES[1]].append(r)
            ratios[sample] = r
        for first, second in combinations(fixed['samples'], 2):
            endpoints = [readings[s, f] for s in (first, second) for f in (a, b)]
            r = dict(id=f'contrast:{first}:{second}:{a}:{b}', first=first, second=second,
                     within_grind=first[0] == second[0], force_from_N=a, force_to_N=b,
                     endpoints=[q['id'] for q in endpoints],
                     **density_ratio_contrast(*endpoints, tau))
            tables[TABLES[2]].append(r)
            pairs.append(r)
        for grind in fixed['grinds']:
            members = [s for s in fixed['samples'] if s[0] == grind]
            r = dict(id=f'envelope:{grind}:{a}:{b}', grind=grind, force_from_N=a, force_to_N=b,
                     ratio_refs=[ratios[s]['id'] for s in members], **envelope(ratios, members))
            envelopes[grind] = r
            tables[TABLES[3]].append(r)
        for first, second in combinations(fixed['grinds'], 2):
            selected = [p for p in pairs if p['first'][0] == first and p['second'][0] == second]
            tables[TABLES[4]].append(dict(id=f'grind:{first}:{second}:{a}:{b}', first=first,
                                         second=second, force_from_N=a, force_to_N=b,
                                         **grind_comparison(envelopes[first], envelopes[second], selected)))
        intervals.append(dict(interval_N=[a, b], disposition=disposition(pairs, 66),
                              comparisons=inherited.summarize(pairs),
                              witness_ids=[r['id'] for r in pairs if r['sign'] in (-1, 1)]))
    for key, count in fixed['counts'].items():
        if len(tables[key]) != count or len({r['id'] for r in tables[key]}) != count:
            raise ValueError(f'Reporting count differs: {key}')
    primary = next(r for r in intervals if r['interval_N'] == fixed['primary_interval_N'])
    witness = affine_witness(contract, paths, traces)
    return dict(task=TASK, classification=fixed['classification'], physical_validation='NOT_ESTABLISHED',
                actual_base=fixed['actual_base'], read_only_ewp_main=fixed['ewp_main'],
                input_hashes=fixed['inherited_input_hashes'], dataset_id=fixed['dataset_id'],
                plan_sha256=fixed['plan_sha256'], calculation_contract_sha256=inherited.sha256(CONTRACT),
                preserved_files_verified=len(fixed['preserved_file_hashes']),
                source_authentication='ACCEPTED_PREDECESSOR_REUSED_NO_FRESH_PDF_AUTHENTICATION',
                exposure=fixed['exposure'], arithmetic=fixed['arithmetic'],
                counts_are_independent_replications=False,
                reporting_set={k: fixed[k] for k in ('samples', 'grinds', 'forces_N', 'intervals_N',
                                                    'primary_interval_N', 'primary_pair', 'counts')},
                calibration=cal, marginal_replay=replay,
                support_summary={k: inherited.summarize(v) for k, v in tables.items()},
                A=dict(primary_disposition=primary['disposition'],
                       overall_disposition=disposition(tables[TABLES[2]], 990), intervals=intervals,
                       witnesses=[r for r in tables[TABLES[2]] if r['sign'] in (-1, 1)],
                       grind_witnesses=[r for r in tables[TABLES[4]] if r['sign'] in (-1, 1)]),
                B={k: witness[k] for k in ('disposition', 'failure', 'verification')},
                limits=['Finite graphical comparison only; not statistical confidence or population inference',
                        'A rectangular outer bounds are sufficient contradictions, not joint-feasibility solutions',
                        'B finite compatibility does not identify actual or continuous material response shapes',
                        'No intrinsic modulus, unloaded density, preparation mechanism or physical validation',
                        'Equal force is not authenticated equal material stress',
                        'Unrestricted simultaneous force/density translations remain unexcluded',
                        'No independent replication, wet-bed, permeability, causal or EWP validation claim'],
                affine_witness=witness, **tables)


def produce(output=OUTPUT, plot_figure=False):
    result = analyze()
    output.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        geometry.csv_rows(output/(name+'.csv'), result[name])
    w = result['affine_witness']
    for name in ('parameters', 'levels', 'intersections', 'readings', 'certificates'):
        geometry.csv_rows(output/('affine_'+name+'.csv'), w[name])
    for filename, value in [('affine_witness.json', w), ('RESULT.json',
                             {k: v for k, v in result.items() if k not in TABLES+['affine_witness']})]:
        (output/filename).write_text(json.dumps(value, default=geometry.serial, indent=2, sort_keys=True)+'\n')
    if plot_figure:
        plot(result, output/'comparison.svg')
    return result


def plot(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec = VizSpec(
        id='corrochano_fig6_2_density_normalization', title='Finite dry-loading density normalization',
        class_=1, producer=Producer(module=__name__, function='analyze',
                                   result_map={'support_summary': 'support_summary'}),
        badge='OBSERVED', evidence_strength='reference', components=[],
        fidelity_ceiling='Graphical outer enclosures and one finite witness; no physical validation.',
        render_fn='puckworks.analysis.corrochano2017_density_normalization:plot',
        caption='Original comparison, not source artwork; no fitted continuous response or confidence bands.',
        outputs=['comparison.svg'], used_in=TASK)
    if spec.validate():
        raise ValueError(spec.validate())
    with matplotlib.rc_context({'svg.hashsalt': TASK, 'font.size': 10, 'path.simplify': False}):
        fig, axes = plt.subplots(1, 3, figsize=(15, 5.8), gridspec_kw={'width_ratios': [1.15, 1, 1.2]})
        colors = dict(zip('BCDE', ['#215dad', '#ba3c32', '#277b42', '#883b9f']))
        rows = [r for r in result[TABLES[1]] if [r['force_from_N'], r['force_to_N']] == [50, 250]]
        for i, r in enumerate(rows):
            if r['full_support']:
                lo, hi = map(float, r['bounds_ratio'])
                axes[0].plot([lo, hi], [i, i], color=colors[r['grind']], lw=3)
            else:
                axes[0].text(0.5, i, r['status'])
        axes[0].set(yticks=range(12), yticklabels=[r['trace'] for r in rows],
                    xlabel='Density ratio, 250 N / 50 N', title='A: marginal ratio enclosures')
        axes[0].invert_yaxis()
        decisive = next(r for r in result[TABLES[2]] if r['id'] == 'contrast:B3:D2:50:250')
        if decisive['full_support']:
            lo, hi = map(float, decisive['ratio_difference'])
            axes[1].plot([lo, hi], [0, 0], color='#333333', lw=4)
            span = max(abs(lo), abs(hi), .001)
            axes[1].set_xlim(min(lo, 0)-.08*span, max(hi, 0)+.08*span)
        axes[1].axvline(0, color='gray', ls=':')
        axes[1].set(yticks=[0], yticklabels=['B3 − D2'], ylim=(-1, 1),
                    xlabel='Direct shared-calibration ratio contrast', title='A: direct contrast')
        w = result['affine_witness']
        if w['disposition'] == SUCCESS:
            axes[2].scatter([r['force_N'] for r in w['levels']],
                            [float(r['h']) for r in w['levels']], color='#272727', s=45)
        else:
            axes[2].text(.5, .5, 'No certificate found', ha='center', transform=axes[2].transAxes)
        axes[2].set(xlabel='Applied force (N)', ylabel='Common finite level h',
                    title='B: one certified simultaneous assignment',
                    xticks=[25, 50, 100, 150, 200, 250], ylim=(-.05, 1.05))
        fig.suptitle('Figure 6.2 retained readings: pure scaling versus baseline + positive amplitude')
        fig.text(.5, .03, 'SOURCE_INTERNAL · TARGET_EXPOSED · RESEARCH_ONLY · PHYSICAL_VALIDATION=NOT_ESTABLISHED\n'
                 'Graphical bounds; no confidence bands. B shows six levels only, with no continuous response implied.',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=(0, .1, 1, .94))
        fig.savefig(output, metadata={'Date': None, 'Description': spec.caption})
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    result = produce(args.output, args.plot)
    print(json.dumps({'A_primary': result['A']['primary_disposition'],
                      'A_overall': result['A']['overall_disposition'], 'B': result['B']}, indent=2))


if __name__ == '__main__':
    main()

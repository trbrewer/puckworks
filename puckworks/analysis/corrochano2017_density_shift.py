"""Offline common-calibration density-offset comparison of Figure 6.2.

Graphical outer enclosures; SOURCE_INTERNAL / TARGET_EXPOSED / RESEARCH_ONLY.
PHYSICAL_VALIDATION=NOT_ESTABLISHED. No fit or joint-feasibility solver.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

from puckworks.analysis import corrochano2017_dry_compaction as geometry

ROOT = geometry.ROOT
OUTPUT = ROOT / 'docs/analysis/sci_md_corrochano_density_shift_001'
CONTRACT = OUTPUT / 'calculation_contract.json'
TASK = 'SCI-MD-CORROCHANO-DENSITY-SHIFT-001'
TABLES = ['density_at_force_coordinates', 'sample_density_increments',
          'sample_pair_contrasts', 'grind_increment_envelopes', 'cross_grind_comparisons']
QUALIFIED = {'SUPPORTED', 'AMBIGUOUS'}
ORIENTATION = 'first_minus_second'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authenticate():
    """Reject changed accepted evidence, rather than silently repair the predecessor."""
    contract = json.loads(CONTRACT.read_text())
    if sha256(OUTPUT/'PLAN.md') != contract['plan_sha256']:
        raise ValueError('Task plan identity changed')
    retained = json.loads((geometry.OUTPUT/'RESULT.json').read_text())['input_hashes']
    if retained != contract['inherited_input_hashes']:
        raise ValueError('Predecessor input identities changed')
    for name, digest in retained.items():
        if sha256(geometry.DATA/name) != digest:
            raise ValueError(f'Accepted input identity changed: {name}')
    for name, digest in contract['preserved_file_hashes'].items():
        if sha256(ROOT/name) != digest:
            raise ValueError(f'Preserved predecessor evidence changed: {name}')
    return contract


def calibration(inherited):
    """Derive a positive shared density slope from the inherited anchor rectangle."""
    axis = inherited['axes']['density']
    v0, v1 = map(F, axis['values'])
    p0, p1 = map(F, axis['positions_pt'])
    guard = F(inherited['anchor_guard_pt'])
    d = p0-p1
    if guard < 0 or v1 <= v0 or d-2*guard <= 0:
        raise ValueError('Nonpositive or degenerate common density calibration')
    beta = ((v1-v0)/(d+2*guard), (v1-v0)/(d-2*guard))
    return dict(mapping='rho=alpha+beta*z', density_values_kg_m3=[v0, v1],
                downward_positions_pt=[p0, p1], independent_anchor_allowance_pt=guard,
                nominal_separation_pt=d, beta_kg_m3_per_pt=beta,
                beta_display=geometry.outward(beta),
                provenance='inherited contract.json axes.density; paths.json axes/ticks')


def scale(bounds, beta):
    """One common positive slope applied AFTER coordinate subtraction; sign safe."""
    if bounds is None:
        return None
    if beta[0] <= 0 or beta[1] < beta[0] or bounds[1] < bounds[0]:
        raise ValueError('Invalid interval or slope')
    values = [x*b for x, b in product(bounds, beta)]
    return min(values), max(values)


def qualified(reading):
    return (reading['full_support'] and reading['status'] in QUALIFIED
            and reading['bounds_pt'] is not None)


def read_coordinates(segments, target, force_axis, density_axis):
    """Full strip / all branches, with the inherited trace guard retained once."""
    q = force_axis.query(target)
    nominal = force_axis.coordinate(target)
    support = geometry.union(tuple(sorted((a[0], b[0]))) for a, b in segments)
    nominal_set, nominal_branches = geometry.intersections(segments, (nominal, nominal), 0)
    full = geometry.contains(support, q)
    result = dict(status='UNSUPPORTED', reason='', full_support=full,
                  nominal_support=geometry.contains(support, (nominal, nominal)),
                  query_pt=q, support_pt=support, nominal_y_components_pt=nominal_set,
                  nominal_branches=nominal_branches, strip_branches=None,
                  downward_y_components_pt=[], components_z_pt=[], bounds_pt=None,
                  display_pt=None, marginal_density_bounds_kg_m3=None)
    if not full:
        extent = geometry.hull(support)
        result['reason'] = ('QUERY_EXCEEDS_RECORDED_ENDPOINT' if extent is None or
                            not geometry.contains([extent], q)
                            else 'QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP')
        return result
    intervals, branches = geometry.intersections(segments, q, 0)
    if not intervals:
        raise ArithmeticError('Full support without a strip intersection')
    t = density_axis.trace_guard
    if t < 0:
        raise ValueError('Negative density trace allowance')
    components = geometry.union((-upper-t, -lower+t) for lower, upper in intervals)
    ambiguous = (nominal_branches > 1 or len(nominal_set) > 1 or
                 any(a != b for a, b in nominal_set) or branches > 1)
    bounds = geometry.hull(components)
    result.update(status='AMBIGUOUS' if ambiguous else 'SUPPORTED',
                  reason='MULTIPLE_INTERSECTIONS' if ambiguous else 'FULL_QUERY_SUPPORTED',
                  strip_branches=branches, downward_y_components_pt=intervals,
                  components_z_pt=components, bounds_pt=bounds,
                  display_pt=geometry.outward(bounds),
                  # Unexpanded y goes to Axis.output: its trace guard is added ONCE.
                  marginal_density_bounds_kg_m3=geometry.hull(
                      density_axis.output(interval) for interval in intervals))
    return result


def numerical_failure(exc):
    return dict(status='NUMERICALLY_UNRESOLVED', reason=f'{type(exc).__name__}: {exc}',
                full_support=False, bounds_pt=None, display_pt=None,
                marginal_density_bounds_kg_m3=None)


def interval_record(bounds, beta):
    physical = scale(bounds, beta)
    return dict(bounds_pt=bounds, display_pt=geometry.outward(bounds),
                bounds_kg_m3=physical, display_kg_m3=geometry.outward(physical))


def increment(before, after, beta):
    numerical = any(r['status'] == 'NUMERICALLY_UNRESOLVED' for r in (before, after))
    full = all(qualified(r) for r in (before, after))
    ambiguous = any(r['status'] == 'AMBIGUOUS' for r in (before, after))
    bounds = geometry.subtract(after['bounds_pt'], before['bounds_pt']) if full else None
    return dict(status=('NUMERICALLY_UNRESOLVED' if numerical else 'UNSUPPORTED' if not full
                        else 'AMBIGUOUS' if ambiguous else 'SUPPORTED'),
                reason=('SAME_SAMPLE_OUTER_SUBTRACTION' if full else
                        ';'.join(f'{name}:{r["reason"]}' for name, r in
                                 [('lower_force', before), ('upper_force', after)] if not qualified(r))),
                full_support=full, **interval_record(bounds, beta))


def compare(first, second, beta):
    numerical = any(r['status'] == 'NUMERICALLY_UNRESOLVED' for r in (first, second))
    full = all(qualified(r) for r in (first, second))
    bounds = geometry.subtract(first['bounds_pt'], second['bounds_pt']) if full else None
    sign = (1 if bounds[0] > 0 else -1 if bounds[1] < 0 else 0) if full else None
    classification = ('NUMERICALLY_UNRESOLVED' if numerical else
                      'UNSUPPORTED_OR_INCOMPLETE' if not full else
                      'STRICTLY_SEPARATED' if sign else 'NOT_EXCLUDED_BY_THIS_COMPARISON')
    return dict(classification=classification, full_support=full,
                ambiguous=any(r['status'] == 'AMBIGUOUS' for r in (first, second)),
                difference_orientation=ORIENTATION, sign=sign,
                more='first' if sign == 1 else 'second' if sign == -1 else None,
                **interval_record(bounds, beta))


def envelope(readings, expected, beta):
    present = [s for s in expected if s in readings and qualified(readings[s])]
    missing = [s for s in expected if s not in present]
    ambiguous = [s for s in present if readings[s]['status'] == 'AMBIGUOUS']
    numerical = [s for s in expected if s in readings and
                 readings[s]['status'] == 'NUMERICALLY_UNRESOLVED']
    bounds = geometry.hull(readings[s]['bounds_pt'] for s in present)
    return dict(completeness='INCOMPLETE' if missing else 'COMPLETE',
                present=present, missing=missing, ambiguous_members=ambiguous,
                numerical_members=numerical, full_support=not missing,
                status=('NUMERICALLY_UNRESOLVED' if numerical else 'UNSUPPORTED' if missing
                        else 'AMBIGUOUS' if ambiguous else 'SUPPORTED'),
                descriptive_only=bool(missing), **interval_record(bounds, beta))


def null_disposition(comparisons, expected):
    classes = Counter(r['classification'] for r in comparisons)
    if classes['STRICTLY_SEPARATED']:
        return 'EXCLUDED_BY_SAMPLE_INCREMENT_SEPARATION'
    if len(comparisons) == expected and classes['NOT_EXCLUDED_BY_THIS_COMPARISON'] == expected:
        return 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'
    return 'UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'


def replay(readings):
    """Compare reconstructed exact marginals/statuses, never use CSV bounds as input."""
    with (geometry.OUTPUT/'density_at_force.csv').open() as stream:
        old = {(r['trace'], int(r['target'])): r for r in csv.DictReader(stream)}
    if len(old) != len(readings):
        raise ValueError('Predecessor replay row count differs')
    unresolved = []
    for r in readings:
        if r['status'] == 'NUMERICALLY_UNRESOLVED':
            unresolved.append(r['id'])
            continue
        previous = old[r['trace'], r['force_N']]
        bounds = tuple(map(F, json.loads(previous['bounds']))) if previous['bounds'] else None
        if (r['marginal_density_bounds_kg_m3'] != bounds or r['status'] != previous['status'] or
                r['full_support'] != (previous['full_support'] == 'True')):
            raise ValueError(f'Predecessor replay mismatch: {r["id"]}')
    return dict(status='NUMERICALLY_UNRESOLVED' if unresolved else 'EXACT_MATCH',
                count=len(readings)-len(unresolved), numerical_unresolved_ids=unresolved,
                reference='docs/analysis/sci_md_corrochano_dry_compaction_001/density_at_force.csv')


def summarize(rows):
    result = dict(total=len(rows), full_support=sum(r['full_support'] for r in rows))
    for field in ('status', 'classification', 'completeness'):
        if rows and field in rows[0]:
            result[field+'_counts'] = dict(Counter(r[field] for r in rows))
    result['ambiguous'] = sum(r.get('status') == 'AMBIGUOUS' or r.get('ambiguous', False)
                              or bool(r.get('ambiguous_members')) for r in rows)
    return result


def analyze():
    contract = authenticate()
    inherited, paths, axes, traces = geometry.load()
    if list(traces) != contract['samples'] or inherited['force_targets_N'] != contract['forces_N']:
        raise ValueError('Inherited sample/force identity differs')
    cal = calibration(inherited)
    beta = cal['beta_kg_m3_per_pt']
    tables = {name: [] for name in TABLES}
    readings = {}
    for sample in contract['samples']:
        for force in contract['forces_N']:
            try:
                r = read_coordinates(traces[sample], force, axes['force'], axes['density'])
            except ArithmeticError as exc:
                r = numerical_failure(exc)
            r.update(id=f'z:{sample}:{force}', trace=sample, grind=sample[0], force_N=force,
                     source_chunks=paths['trace_chunks'][sample],
                     source_reference='coordinates.csv + paths.json; Figure6.2 printed223/PDF248/index247')
            readings[sample, force] = r
            tables[TABLES[0]].append(r)
    replay_result = replay(tables[TABLES[0]])
    interval_summaries = []
    for a, b in contract['intervals_N']:
        increments = {}
        envs = {}
        for sample in contract['samples']:
            before, after = readings[sample, a], readings[sample, b]
            r = dict(id=f'increment:{sample}:{a}:{b}', trace=sample, grind=sample[0],
                     force_from_N=a, force_to_N=b, endpoints=[before['id'], after['id']],
                     **increment(before, after, beta))
            increments[sample] = r
            tables[TABLES[1]].append(r)
        pairs = []
        for first, second in combinations(contract['samples'], 2):
            r = dict(id=f'contrast:{first}:{second}:{a}:{b}', first=first, second=second,
                     force_from_N=a, force_to_N=b, within_grind=first[0] == second[0],
                     increment_refs=[increments[first]['id'], increments[second]['id']],
                     **compare(increments[first], increments[second], beta))
            tables[TABLES[2]].append(r)
            pairs.append(r)
        for grind in contract['grinds']:
            members = [s for s in contract['samples'] if s[0] == grind]
            r = dict(id=f'envelope:{grind}:{a}:{b}', grind=grind, force_from_N=a, force_to_N=b,
                     increment_refs=[increments[s]['id'] for s in members],
                     **envelope(increments, members, beta))
            envs[grind] = r
            tables[TABLES[3]].append(r)
        grind_pairs = []
        for first, second in combinations(contract['grinds'], 2):
            r = dict(id=f'grind_contrast:{first}:{second}:{a}:{b}', first=first, second=second,
                     force_from_N=a, force_to_N=b,
                     envelope_refs=[envs[first]['id'], envs[second]['id']],
                     **compare(envs[first], envs[second], beta))
            tables[TABLES[4]].append(r)
            grind_pairs.append(r)
        interval_summaries.append(dict(interval_N=[a, b], disposition=null_disposition(pairs, 66),
                                       sample_comparisons=summarize(pairs),
                                       grind_comparisons=summarize(grind_pairs),
                                       witness_ids=[r['id'] for r in pairs if r['sign'] in (-1, 1)]))
    for name, count in contract['counts'].items():
        if len(tables[name]) != count or len({r['id'] for r in tables[name]}) != count:
            raise ValueError(f'Fixed reporting set differs: {name}')
    primary = next(r for r in interval_summaries if r['interval_N'] == contract['primary_interval_N'])
    a, b = contract['primary_interval_N']
    diagnostic = {}
    for sample in ('B1', 'E2'):
        before, after = readings[sample, a], readings[sample, b]
        full = qualified(before) and qualified(after)
        diagnostic[sample] = dict(
            coordinate_increment_pt=(geometry.subtract(after['bounds_pt'], before['bounds_pt'])
                                     if full else None),
            old_marginal_subtraction_kg_m3=geometry.subtract(
                after['marginal_density_bounds_kg_m3'], before['marginal_density_bounds_kg_m3']) if full else None)
    old_bounds = [diagnostic[s]['old_marginal_subtraction_kg_m3'] for s in ('B1', 'E2')]
    diagnostic['old_marginal_contrast_kg_m3'] = (geometry.subtract(*old_bounds)
                                              if all(b is not None for b in old_bounds) else None)
    diagnostic['direct_common_scale_contrast'] = next(r for r in tables[TABLES[2]]
                                                      if r['id'] == f'contrast:B1:E2:{a}:{b}')
    return dict(task=TASK, classification=contract['classification'], physical_validation='NOT_ESTABLISHED',
                actual_base=contract['actual_base'], source_pdf_sha256=contract['source_pdf_sha256'],
                dataset_id=contract['dataset_id'], input_hashes=contract['inherited_input_hashes'],
                preserved_predecessor_files_verified=len(contract['preserved_file_hashes']),
                plan_sha256=contract['plan_sha256'], calculation_contract_sha256=sha256(CONTRACT),
                inherited_contract_sha256=contract['inherited_input_hashes']['contract.json'],
                coordinate_convention=contract['coordinate'], calibration=cal,
                reporting_set={k: contract[k] for k in ['samples', 'grinds', 'forces_N', 'intervals_N',
                                                       'primary_interval_N', 'counts', 'contrast_orientation']},
                arithmetic=contract['arithmetic'], exposure=contract['exposure'], limits=contract['limits'],
                counts_are_independent_replications=False, marginal_replay=replay_result,
                support_summary={name: summarize(rows) for name, rows in tables.items()},
                numerical_unresolved_readings=sum(r['status'] == 'NUMERICALLY_UNRESOLVED'
                                                  for r in tables[TABLES[0]]),
                primary_disposition=primary['disposition'],
                overall_disposition=null_disposition(tables[TABLES[2]], contract['counts'][TABLES[2]]),
                intervals=interval_summaries,
                witnesses=[r for r in tables[TABLES[2]] if r['classification'] == 'STRICTLY_SEPARATED'],
                grind_witnesses=[r for r in tables[TABLES[4]] if r['classification'] == 'STRICTLY_SEPARATED'],
                exposed_comparison_diagnostic=diagnostic, **tables)


def produce(output=OUTPUT, plot_figure=False):
    result = analyze()
    output.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        geometry.csv_rows(output/(name+'.csv'), result[name])
    summary = {k: v for k, v in result.items() if k not in TABLES}
    (output/'RESULT.json').write_text(json.dumps(summary, default=geometry.serial,
                                                indent=2, sort_keys=True)+'\n')
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
        id='corrochano_fig6_2_density_shift', title='Dry-loading density increments', class_=1,
        producer=Producer(module='puckworks.analysis.corrochano2017_density_shift', function='analyze',
                          result_map={'support_summary': 'support_summary'}),
        badge='OBSERVED', evidence_strength='reference', components=[],
        fidelity_ceiling='Graphical outer enclosures for twelve represented samples; no physical validation.',
        render_fn='puckworks.analysis.corrochano2017_density_shift:plot',
        caption='Original common-calibration comparison; no fitted response or source artwork.',
        outputs=['comparison.svg'], used_in=TASK)
    if spec.validate():
        raise ValueError(spec.validate())
    colors = dict(zip('BCDE', ['#215dad', '#ba3c32', '#277b42', '#883b9f']))
    primary = result['reporting_set']['primary_interval_N']
    def selected(rows):
        return [r for r in rows if [r['force_from_N'], r['force_to_N']] == primary]
    with matplotlib.rc_context({'svg.hashsalt': TASK, 'font.size': 10, 'path.simplify': False}):
        fig, axes = plt.subplots(1, 3, figsize=(15, 6), gridspec_kw={'width_ratios': [1.4, .85, 1.1]})
        for ax, rows, label in [(axes[0], selected(result[TABLES[1]]), 'trace'),
                                (axes[1], selected(result[TABLES[3]]), 'grind')]:
            for k, r in enumerate(rows):
                if not r['full_support']:
                    ax.text(.5, k, 'INCOMPLETE', transform=ax.get_yaxis_transform(), ha='center')
                    continue
                lo, hi = map(float, r['bounds_kg_m3'])
                ax.plot([lo, hi], [k, k], color=colors[r[label][0]], lw=3, marker='|', ms=10)
            ax.set_yticks(range(len(rows)), [r[label] for r in rows])
            ax.invert_yaxis()
            ax.set_xlabel('Density increment (kg/m³)')
            ax.grid(axis='x', alpha=.2)
        axes[0].set_title('25→250 N · all twelve samples')
        axes[1].set_title('Complete grind envelopes')
        rows = result['exposed_comparison_diagnostic']
        direct = rows['direct_common_scale_contrast']
        bounds = direct['bounds_kg_m3']
        if bounds:
            axes[2].plot(list(map(float, bounds)), [0, 0], color='#222222', marker='|', ms=13, lw=3)
            axes[2].text(.04, .78, 'Direct shared-scale contrast\n['+', '.join(direct['display_kg_m3'])+'] kg/m³',
                         transform=axes[2].transAxes, fontsize=9)
        else:
            axes[2].text(.5, .5, 'INCOMPLETE', transform=axes[2].transAxes, ha='center')
        axes[2].axvline(0, color='#777777', ls='--', lw=1)
        axes[2].set(yticks=[0], yticklabels=['B1 − E2'], ylim=(-1, 1),
                    xlabel='Increment contrast (kg/m³)', title='25→250 N · direct witness')
        axes[2].grid(axis='x', alpha=.2)
        fig.suptitle('Corrochano (2017), Figure 6.2 · OBSERVED / reference\n'
                     'Source-internal, target-exposed graphical outer enclosures', fontsize=13)
        fig.text(.5, .045, 'Bars include full force-strip and density trace allowances; incomplete support is labelled.\n'
                 'One common density scale acts after subtraction: subtracting separately displayed physical intervals loses that dependency.\n'
                 'Graphical IDs are not native run IDs. Not confidence intervals. PHYSICAL_VALIDATION=NOT_ESTABLISHED.',
                 ha='center', fontsize=9)
        fig.tight_layout(rect=(0, .16, 1, .89))
        fig.savefig(output, metadata={'Date': None, 'Creator': 'Puckworks original density-increment comparison'})
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    produce(args.output, args.plot)


if __name__ == '__main__':
    main()

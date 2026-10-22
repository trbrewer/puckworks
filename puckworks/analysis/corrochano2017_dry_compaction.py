"""Offline Figure 6.2 dry-loading readings and limited additive-force-offset test.

SOURCE_INTERNAL / TARGET_EXPOSED / RESEARCH_ONLY. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Exact rational graphical outer enclosures, not statistical or instrument uncertainty.
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

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/romancorrochano2017/fig6_2_dry_compaction'
OUTPUT = ROOT / 'docs/analysis/sci_md_corrochano_dry_compaction_001'
TASK = 'SCI-MD-CORROCHANO-DRY-COMPACTION-001'
IDS = {g: [g+str(j) for j in range(1, 4)] for g in 'BCDE'}
TABLES = ['force_at_density', 'density_at_force', 'sample_force_increments',
          'grind_increment_envelopes', 'cross_grind_comparisons', 'support_accounting']


def union(intervals):
    """Closed interval union; positive gaps are never filled."""
    out = []
    for a, b in sorted(intervals):
        if a > b:
            raise ValueError('Reversed interval')
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(b, out[-1][1]))
        else:
            out.append((a, b))
    return out


def contains(support, interval):
    return any(a <= interval[0] <= interval[1] <= b for a, b in support)


def hull(intervals):
    intervals = list(intervals)
    return (min(a for a, b in intervals), max(b for a, b in intervals)) if intervals else None


def subtract(after, before):
    """Outer subtraction; no nonnegative clipping or independent-grind subtraction."""
    return after[0]-before[1], after[1]-before[0]


def outward(bounds, places=6):
    if bounds is None:
        return None
    scale = 10**places
    low, high = [F(x)*scale for x in bounds]
    integers = [low.numerator//low.denominator, -((-high.numerator)//high.denominator)]
    return [('-' if v < 0 else '') + f'{abs(v)//scale}.{abs(v)%scale:0{places}d}'
            for v in integers]


class Axis:
    """Shared affine anchor uncertainty; coordinate orientation may be reversed."""
    def __init__(self, values, guard=F(1), trace_guard=F(1)):
        self.v0, self.v1 = map(F, values['values'])
        self.p0, self.p1 = map(F, values['positions_pt'])
        self.guard, self.trace_guard = F(guard), F(trace_guard)
        self.corners = list(product([self.p0-self.guard, self.p0+self.guard],
                                    [self.p1-self.guard, self.p1+self.guard]))
        if self.v0 >= self.v1 or any((b-a)*(self.p1-self.p0) <= 0 for a, b in self.corners):
            raise ValueError('Degenerate calibration')

    def coordinate(self, value):
        return self.p0+(F(value)-self.v0)*(self.p1-self.p0)/(self.v1-self.v0)

    def value(self, p):
        return self.v0+(F(p)-self.p0)*(self.v1-self.v0)/(self.p1-self.p0)

    def query(self, value):
        w = (F(value)-self.v0)/(self.v1-self.v0)
        points = [(1-w)*a+w*b for a, b in self.corners]
        return min(points)-self.trace_guard, max(points)+self.trace_guard

    def output(self, interval):
        values = [self.v0+(p-a)*(self.v1-self.v0)/(b-a) for a, b in self.corners
                  for p in (interval[0]-self.trace_guard, interval[1]+self.trace_guard)]
        return min(values), max(values)


def clip_segment(a, b, query, coordinate):
    """Exact clipping to query strip; handles reversed and constant coordinates."""
    x0, x1 = a[coordinate], b[coordinate]
    if x0 == x1:
        return (a, b) if query[0] <= x0 <= query[1] else None
    t0, t1 = sorted((F(q-x0)/(x1-x0) for q in query))
    lo, hi = max(F(0), t0), min(F(1), t1)
    if lo > hi:
        return None
    return tuple(tuple(a[k]+t*(b[k]-a[k]) for k in (0, 1)) for t in (lo, hi))


def intersections(segments, query, coordinate):
    """Retain every crossing and disconnected strip branch, in path order."""
    intervals, branches = [], 0
    previous = None
    for a, b in segments:
        clipped = clip_segment(a, b, query, coordinate)
        if clipped is None:
            previous = None
            continue
        c, d = clipped
        if previous != c:
            branches += 1
        previous = d
        intervals.append(tuple(sorted((c[1-coordinate], d[1-coordinate]))))
    return union(intervals), branches


def read_trace(segments, target, query_axis, output_axis, coordinate):
    q = query_axis.query(target)
    nominal = query_axis.coordinate(target)
    support = union(tuple(sorted((a[coordinate], b[coordinate]))) for a, b in segments)
    nominal_set, nominal_branches = intersections(segments, (nominal, nominal), coordinate)
    full = contains(support, q)
    if not full:
        extent = hull(support)
        reason = ('QUERY_EXCEEDS_RECORDED_ENDPOINT' if not extent or not contains([extent], q)
                  else 'QUERY_INTERSECTS_UNSUPPORTED_PATH_GAP')
        return dict(status='UNSUPPORTED', reason=reason, full_support=False,
                    nominal_support=contains(support, (nominal, nominal)), query_pt=q,
                    support_pt=support, nominal_crossings_pt=nominal_set,
                    nominal_branches=nominal_branches, strip_branches=None,
                    output_set=[], bounds=None, display=None)
    intervals, branches = intersections(segments, q, coordinate)
    values = union(output_axis.output(p) for p in intervals)
    # Any non-degenerate nominal interval is infinitely many crossings (plateau).
    ambiguous = (nominal_branches > 1 or len(nominal_set) > 1 or
                 any(a != b for a, b in nominal_set) or branches > 1)
    bounds = hull(values)
    return dict(status='AMBIGUOUS' if ambiguous else 'SUPPORTED',
                reason='MULTIPLE_INTERSECTIONS' if ambiguous else 'FULL_QUERY_SUPPORTED',
                full_support=True, nominal_support=True, query_pt=q, support_pt=support,
                nominal_crossings_pt=nominal_set, nominal_branches=nominal_branches,
                strip_branches=branches, output_set=values, bounds=bounds, display=outward(bounds))


def increment(before, after):
    if not before['full_support'] or not after['full_support']:
        failed = [name+':'+r['reason'] for name, r in [('lower_density', before), ('upper_density', after)]
                  if not r['full_support']]
        return dict(status='UNSUPPORTED', reason=';'.join(failed), full_support=False,
                    bounds=None, display=None)
    bounds = subtract(after['bounds'], before['bounds'])
    ambiguous = any(r['status'] == 'AMBIGUOUS' for r in [before, after])
    return dict(status='AMBIGUOUS' if ambiguous else 'SUPPORTED',
                reason='MULTIPLE_INTERSECTIONS_OUTER_HULL' if ambiguous else 'SAME_SAMPLE_OUTER_SUBTRACTION',
                full_support=True, bounds=bounds, display=outward(bounds))


def envelope(readings, expected):
    present = [s for s in expected if s in readings and readings[s]['full_support']]
    missing = [s for s in expected if s not in present]
    ambiguous = [s for s in present if readings[s]['status'] == 'AMBIGUOUS']
    bounds = hull(readings[s]['bounds'] for s in present) if present else None
    return dict(completeness='INCOMPLETE' if missing else 'COMPLETE', present=present,
                missing=missing, ambiguous=ambiguous, bounds=bounds, display=outward(bounds))


def compare(first, second):
    if first['completeness'] != 'COMPLETE' or second['completeness'] != 'COMPLETE':
        return dict(classification='UNSUPPORTED_OR_INCOMPLETE', difference=None,
                    display=None, sign=None, more=None, minimum_gap=None)
    difference = subtract(second['bounds'], first['bounds'])
    sign = 1 if difference[0] > 0 else -1 if difference[1] < 0 else 0
    return dict(classification='STRICTLY_SEPARATED' if sign else 'NOT_EXCLUDED_BY_THIS_COMPARISON',
                difference=difference, display=outward(difference), sign=sign,
                more='second' if sign > 0 else 'first' if sign < 0 else None,
                minimum_gap=difference[0] if sign > 0 else -difference[1] if sign < 0 else None)


def null_disposition(comparisons):
    classes = [r['classification'] for r in comparisons]
    if 'STRICTLY_SEPARATED' in classes:
        return 'EXCLUDED_BY_COMPLETE_INCREMENT_SEPARATION'
    if len(classes) != 12 or 'UNSUPPORTED_OR_INCOMPLETE' in classes:
        return 'UNRESOLVED_DUE_TO_SUPPORT_OR_READING_LIMITS'
    return 'NOT_EXCLUDED_BY_THE_DECLARED_COMPARISONS'


def load(data=DATA):
    contract = json.loads((data/'contract.json').read_text())
    paths = json.loads((data/'paths.json').read_text())
    rows = list(csv.DictReader((data/'coordinates.csv').open()))
    by_chunk = {}
    for row in rows:
        by_chunk.setdefault(row['chunk'], []).append(row)
    chunks = {c['chunk']: c for c in paths['chunks']}
    for cid, rr in by_chunk.items():
        if len(rr) != chunks[cid]['vertex_count'] or [int(r['vertex']) for r in rr] != list(range(len(rr))):
            raise ValueError('Vertex accounting differs')
        if rr[0]['operation'] != 'm' or any(r['operation'] != 'l' for r in rr[1:]):
            raise ValueError('Unrecognized subpath; never join a move')
        for r in rr:
            if (r['trace'] or None) != chunks[cid]['trace']:
                raise ValueError('Trace assignment mismatch')
            c = chunks[cid]
            sx, sy = map(F, c['scale']); tx, ty = map(F, c['translation'])
            ox, oy = map(F, c['local_translation'])
            expected = (tx+sx*(ox+F(r['raw_x'])), F(paths['page_height_pt'])-ty-sy*(oy+F(r['raw_y'])))
            if expected != (F(r['x_pt']), F(r['y_pt'])):
                raise ValueError('Path transform mismatch')
    paintings = paths['paintings']
    for k in range(76):
        a, b = paintings[k], paintings[k+76]
        if a['chunk'] != b['chunk'] or b['duplicate_of'] != k or a['raw_path_sha256'] != b['raw_path_sha256']:
            raise ValueError('Duplicate provenance mismatch')
    ids = [s for g in IDS.values() for s in g]
    if sorted(paths['trace_chunks']) != ids or set(by_chunk) != set(chunks):
        raise ValueError('Sample/chunk accounting mismatch')
    joins = {(j['trace'], j['left'], j['right']): j for j in paths['joins']}
    traces = {}
    for trace in ids:
        segments, previous, previous_id = [], None, None
        for cid in paths['trace_chunks'][trace]:
            points = [(F(r['x_pt']), F(r['y_pt'])) for r in by_chunk[cid]]
            if previous is not None:
                join = joins.get((trace, previous_id, cid))
                if join:
                    delta = tuple(b-a for a, b in zip(previous, points[0]))
                    if delta != tuple(map(F, join['delta_pt'])) or max(map(abs, delta)) > F(contract['join_limit_pt']):
                        raise ValueError('Unqualified join')
                    segments.append((previous, points[0]))
                # No declared join: disconnected segments remain disconnected.
            segments.extend(zip(points, points[1:]))
            previous, previous_id = points[-1], cid
        traces[trace] = segments
    axes = {name: Axis(c, F(contract['anchor_guard_pt']), F(contract['trace_guard_pt']))
            for name, c in contract['axes'].items()}
    for t in paths['ticks']:
        residual = F(t['coordinate_pt'])-axes[t['axis']].coordinate(t['value'])
        if abs(residual) > F(contract['tick_check_limit_pt']):
            raise ValueError('Tick calibration residual exceeds contract')
    return contract, paths, axes, traces


def analyze(data=DATA):
    contract, paths, axes, traces = load(data)
    tables = {name: [] for name in TABLES}
    lookup = {}
    for name, targets, coordinate, qa, oa, unit in [
        ('force_at_density', contract['density_targets_kg_m3'], 1, 'density', 'force', 'N'),
        ('density_at_force', contract['force_targets_N'], 0, 'force', 'density', 'kg/m^3')]:
        for trace, segments in traces.items():
            for target in targets:
                r = dict(request_id=f'{name}:{trace}:{target}', trace=trace, grind=trace[0], target=target,
                         target_unit='kg/m^3' if coordinate else 'N', output_unit=unit,
                         **read_trace(segments, target, axes[qa], axes[oa], coordinate))
                tables[name].append(r)
                lookup[name, trace, target] = r
    envs = {}
    for a, b in contract['increments_kg_m3']:
        readings = {}
        for trace in traces:
            before, after = lookup['force_at_density', trace, a], lookup['force_at_density', trace, b]
            r = dict(request_id=f'increment:{trace}:{a}:{b}', trace=trace, grind=trace[0],
                     density_from=a, density_to=b, output_unit='N',
                     endpoints=[before['request_id'], after['request_id']],
                     before_bounds=before['bounds'], after_bounds=after['bounds'], **increment(before, after))
            tables['sample_force_increments'].append(r); readings[trace] = r
        for grind, ids in IDS.items():
            r = dict(grind=grind, density_from=a, density_to=b, unit='N', **envelope(readings, ids))
            envs[grind, a, b] = r; tables['grind_increment_envelopes'].append(r)
        for first, second in combinations(IDS, 2):
            ea, eb = envs[first, a, b], envs[second, a, b]
            r = dict(first=first, second=second, density_from=a, density_to=b, unit='N',
                     difference_orientation='second_minus_first', first_bounds=ea['bounds'],
                     second_bounds=eb['bounds'], **compare(ea, eb))
            r['more_grind'] = first if r['more'] == 'first' else second if r['more'] == 'second' else None
            # Descriptive only: these nine pairings do not authorize a complete
            # grind conclusion and are not independent matched experiments.
            r['descriptive_sample_pairs'] = [dict(first=s, second=t, **compare(
                envelope(readings, [s]), envelope(readings, [t])))
                for s in IDS[first] for t in IDS[second]]
            tables['cross_grind_comparisons'].append(r)
    for name in TABLES[:3]:
        for r in tables[name]:
            tables['support_accounting'].append({k: r.get(k) for k in [
                'request_id', 'trace', 'grind', 'status', 'reason', 'full_support', 'nominal_support',
                'target', 'target_unit', 'density_from', 'density_to', 'query_pt', 'support_pt',
                'nominal_branches', 'strip_branches']})
    summary = {name: dict(total=len(tables[name]), full_support=sum(r['full_support'] for r in tables[name]),
                         statuses=dict(Counter(r['status'] for r in tables[name]))) for name in TABLES[:3]}
    trace_support = {}
    for trace, segments in traces.items():
        trace_support[trace] = {name: union(tuple(sorted((axis.value(a[k]), axis.value(b[k]))))
                                         for a, b in segments)
                                for k, (name, axis) in enumerate([('force', axes['force']), ('density', axes['density'])])}
    return dict(task=TASK, physical_validation='NOT_ESTABLISHED', target_exposure='TARGET_EXPOSED',
                arithmetic='EXACT_RATIONAL', numerical_unresolved=0,
                null_disposition=null_disposition(tables['cross_grind_comparisons']),
                input_hashes={n: hashlib.sha256((data/n).read_bytes()).hexdigest()
                              for n in ['coordinates.csv', 'paths.json', 'contract.json', 'holdings_checked.json']},
                summary=summary, trace_support=trace_support, **tables)


def serial(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


def csv_rows(path, rows):
    def cell(value):
        if isinstance(value, (dict, list, tuple)):
            return json.dumps(value, default=serial, separators=(',', ':'), sort_keys=True)
        return value
    with path.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for row in rows for k in row)), lineterminator='\n')
        writer.writeheader(); writer.writerows({k: cell(v) for k, v in row.items()} for row in rows)


def produce(output=OUTPUT, plot_figure=False):
    result = analyze()
    output.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        csv_rows(output/(name+'.csv'), result[name])
    summary = {k: v for k, v in result.items() if k not in TABLES}
    (output/'RESULT.json').write_text(json.dumps(summary, default=serial, indent=2, sort_keys=True)+'\n')
    if plot_figure:
        plot(result, output/'comparison.svg')
    return result


def plot(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec = VizSpec(id='corrochano_fig6_2_dry_compaction', title='Dry loading and force increments', class_=1,
                   producer=Producer(module='puckworks.analysis.corrochano2017_dry_compaction', function='analyze', result_map={'summary': 'summary'}),
                   badge='OBSERVED', evidence_strength='reference', components=[],
                   fidelity_ceiling='Twelve published graphical samples and outer reading bounds; no population or physical validation.',
                   render_fn='puckworks.analysis.corrochano2017_dry_compaction:plot',
                   caption='Original reconstruction; complete source support, requested density levels and same-sample force increments.',
                   outputs=['comparison.svg'], used_in=TASK)
    if spec.validate():
        raise ValueError(spec.validate())
    contract, paths, axes, traces = load()
    colors = {'B': '#215dad', 'C': '#c13b30', 'D': '#27833b', 'E': '#9633a2'}
    styles = {'1': '-', '2': '--', '3': '-.'}
    with matplotlib.rc_context({'svg.hashsalt': 'corrochano6-2', 'font.size': 9, 'path.simplify': False}):
        fig, aa = plt.subplots(2, 2, figsize=(13, 10), gridspec_kw={'height_ratios': [1.5, 1]})
        ax = aa[0, 0]
        for tid, segments in traces.items():
            # Source chains include only explicitly authorized rounding connectors.
            xs, ys, prev = [], [], None
            for a, b in segments:
                if prev != a:
                    xs += [None, float(axes['force'].value(a[0]))]
                    ys += [None, float(axes['density'].value(a[1]))]
                xs.append(float(axes['force'].value(b[0]))); ys.append(float(axes['density'].value(b[1])))
                prev = b
            ax.plot(xs, ys, color=colors[tid[0]], ls=styles[tid[1]], lw=1, label=tid)
        for rho in contract['density_targets_kg_m3']:
            ax.axhline(rho, color='#777777', ls=':', lw=.6)
        ax.set(xlabel='Applied axial force (N)', ylabel='Dry bulk density (kg/m³)',
               title='Twelve source loading paths; no endpoint extension', xlim=(0, 300), ylim=(300, 650))
        ax.legend(ncol=4, fontsize=8)
        status_ax = aa[0, 1]
        requests = result['force_at_density']+result['density_at_force']+result['sample_force_increments']
        for r in requests:
            tid = r['trace']; row = list(traces).index(tid)
            if r['request_id'].startswith('force_at_density'):
                col = contract['density_targets_kg_m3'].index(r['target'])
            elif r['request_id'].startswith('density_at_force'):
                col = 5+contract['force_targets_N'].index(r['target'])
            else:
                col = 11+contract['increments_kg_m3'].index([r['density_from'], r['density_to']])
            marker = {'SUPPORTED': 'o', 'UNSUPPORTED': 'x', 'AMBIGUOUS': 's'}[r['status']]
            status_ax.scatter(col, row, marker=marker, s=24,
                              color=colors[tid[0]] if r['full_support'] else '#777777')
        status_ax.set_yticks(range(12), list(traces)); status_ax.invert_yaxis()
        status_ax.set_xticks(range(13), ['ρ360','ρ400','ρ480','ρ500','ρ520','F25','F50','F100','F150','F200','F250','Δ1','Δ2'], rotation=60)
        status_ax.set_title('All 156 requests: ○ supported; × unsupported; □ ambiguous')
        status_ax.set_xlabel('ρ in kg/m³; F in N; Δ1=480→500; Δ2=500→520')
        for n, (a, b) in enumerate(contract['increments_kg_m3']):
            ax = aa[1, n]
            for r in result['sample_force_increments']:
                if (r['density_from'], r['density_to']) != (a, b):
                    continue
                x = list(traces).index(r['trace'])
                if r['bounds']:
                    lo, hi = map(float, r['bounds']); ax.plot([x, x], [lo, hi], color=colors[r['grind']], lw=2)
                    ax.plot([x-.12, x+.12], [lo, lo], color=colors[r['grind']])
                    ax.plot([x-.12, x+.12], [hi, hi], color=colors[r['grind']])
                else:
                    ax.text(x, .5, '×', transform=ax.get_xaxis_transform(), ha='center', color='#777777')
            for e in result['grind_increment_envelopes']:
                if (e['density_from'], e['density_to']) == (a, b) and e['bounds']:
                    pos = 'BCDE'.index(e['grind'])*3
                    lo, hi = map(float, e['bounds'])
                    ax.fill_between([pos-.4, pos+2.4], lo, hi, color=colors[e['grind']], alpha=.12,
                                    hatch='//' if e['completeness'] != 'COMPLETE' else None)
            ax.axhline(0, color='#777777', lw=.6); ax.set_xticks(range(12), list(traces))
            ax.set(title=f'{a}→{b} kg/m³: same-sample increments', ylabel='Additional axial force (N)')
        fig.suptitle('Corrochano (2017), Fig. 6.2 • OBSERVED / reference • source-internal, target-exposed')
        fig.text(.5, .015, 'Bars: outer graphical-reading enclosures; shading: grind envelopes (hatched if incomplete).\n'
                 'These are not confidence intervals. Graphical IDs are not instrument IDs. PHYSICAL_VALIDATION=NOT_ESTABLISHED.', ha='center')
        fig.tight_layout(rect=(0, .06, 1, .96))
        fig.savefig(output, metadata={'Date': None, 'Creator': 'Puckworks Figure 6.2 original analysis'})
        plt.close(fig)


def main():
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('--output', type=Path, default=OUTPUT)
    p.add_argument('--plot', action='store_true'); a = p.parse_args(); produce(a.output, a.plot)


if __name__ == '__main__':
    main()

"""Independent offline verifier: reconstruct source mappings and check exact certificates.

No analysis-producer import. The frozen production Mo kernel is separately called
at N240; rational graph certificates are checked without its feasibility algorithm.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'puckworks/data/hargarten2020/swelling_kinetics_001'
DEFAULT = Path(__file__).resolve().parent
REFERENCE = F(1200)


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def q(value):
    return F(str(value))


def read_json(path):
    return json.loads(path.read_text())


def linear(pixel, first, last, span):
    return (q(pixel) - q(first)) * q(span) / (q(last) - q(first))


def reconstruct():
    c = read_json(DATA / 'contract.json')
    trace_rows = read_json(DATA / 'traces.json')
    traces = {r['trace_id']: r for r in trace_rows}
    raw = list(csv.DictReader((DATA / 'coordinates.csv').open()))
    require(len(traces) == len(trace_rows) == 17, '17 distinct authenticated particles')
    require(len({r['observation_id'] for r in raw}) == len(raw), 'unique source IDs')
    require(c['source']['sha256'] == '4a41545954e6748a33ec1d956fd690bea58aba9c2e38955dfbb3ae9f5bffbfb0', 'source PDF identity')
    derived = {}
    for r in raw:
        require(r['source_sha256'] == c['source']['sha256'] and r['doi'] == c['source']['doi'], 'row provenance')
        if r['support_status'] != 'supported':
            continue
        tr = traces[r['trace_id']]
        require(all(str(r[k]) == str(tr[k]) for k in ('roast', 'protocol', 'diameter_um', 'marker')), 'trace assignment metadata')
        panel = c['panels'][r['panel_id']]
        x, y, a = q(r['x_px']), q(r['y_px']), q(c['marker_allowance_px'])
        sx = lambda z, u=0, v=0: linear(z, panel['x0'] + u, panel['x1'] + v, panel['t_max'])
        sy = lambda z, u=0, v=0: linear(z, panel['y0'] + u, panel['y1'] + v, panel['y_max_percent']) / 100
        ca = c['axis_allowance_px']
        corners = list(product((-ca, ca), repeat=2))
        tx = [sx(x + s*a, u, v) for u, v in corners for s in (-1, 1)]
        yy = [sy(y + s*a, u, v) for u, v in corners for s in (-1, 1)]
        derived[r['observation_id']] = dict(r, figure=panel['figure'], t=sx(x),
            L=sy(y+a), U=sy(y-a), value=sy(y),
            outer_L=min(yy), outer_U=max(yy),
            t_lo=max(F(0), min(tx)), t_hi=min(q(panel['t_max']), max(tx)))
    return c, traces, raw, derived


def independent_baseline(rows, relaxed=False):
    if not rows:
        return None
    lower = 'outer_L' if relaxed else 'L'
    upper = 'outer_U' if relaxed else 'U'
    result = max([F(0)] + [max(r[lower]-1, -r[upper]) for r in rows])
    if relaxed:
        for later in rows:
            prior = [r[lower] for r in rows if r['t_hi'] <= later['t_lo']]
            if prior:
                result = max(result, (max(prior)-later[upper])/2)
    else:
        running_lower = None
        for time in sorted({r['t'] for r in rows}):
            same = [r for r in rows if r['t'] == time]
            lo, hi = max(r[lower] for r in same), min(r[upper] for r in same)
            running_lower = lo if running_lower is None else max(running_lower, lo)
            result = max(result, (running_lower-hi)/2)
            if time == 0:
                result = max(result, lo)
            if time == REFERENCE:
                result = max(result, 1-hi)
    return result


def residual(p, lo, hi):
    return max(lo-p, p-hi, 0)


def check_baseline(rows, record, expected, relaxed=False):
    require(q(record['B']) == expected, 'independently reconstructed monotone optimum')
    if relaxed:
        require(record['disposition'] == 'EXACT_PARTIAL_ORDER_OUTER_OPTIMUM_NECESSARY_ONLY', 'outer baseline label')
    witness = {x['observation_id']: x for x in record['witness']}
    require(set(witness) == {r['observation_id'] for r in rows}, 'baseline witness coverage')
    for r in rows:
        value = q(witness[r['observation_id']]['p'])
        require(q(witness[r['observation_id']]['t']) == r['t'], 'baseline time')
        require(0 <= value <= 1, 'baseline bounded normalized witness')
        lo, hi = (r['outer_L'], r['outer_U']) if relaxed else (r['L'], r['U'])
        require(residual(value, lo, hi) <= expected, 'baseline witness interval residual')
        for other in rows:
            ordered = r['t_hi'] <= other['t_lo'] if relaxed else r['t'] <= other['t']
            if ordered:
                require(value <= q(witness[other['observation_id']]['p']), 'baseline witness order')
        if not relaxed and r['t'] in (0, REFERENCE):
            require(value == r['t']/REFERENCE, 'baseline endpoint')


def check_graph(graph, rows, trs, epsilon, relaxed):
    """Reconstruct constraints independently; stored edge order only addresses certificates."""
    radius = lambda d: q(d) / 2_000_000
    expected_times = {'zero': F(0)} if relaxed else {'0': F(0)}
    intervals = {'zero': (F(0), F(0))} if relaxed else {}
    references, observations = {}, {}
    dr = F('0.5')
    for tid, tr in trs.items():
        d = q(tr['diameter_um'])
        s = REFERENCE/radius(d)**2
        name = 'ref:'+tid if relaxed else str(s)
        references[tid] = name
        expected_times[name] = s
        if relaxed:
            intervals[name] = (REFERENCE/radius(d+dr)**2, REFERENCE/radius(d-dr)**2)
    for r in rows:
        d = q(trs[r['trace_id']]['diameter_um'])
        s = r['t']/radius(d)**2
        name = r['observation_id'] if relaxed else str(s)
        observations[r['observation_id']] = name
        expected_times[name] = s
        if relaxed:
            intervals[name] = (r['t_lo']/radius(d+dr)**2, r['t_hi']/radius(d-dr)**2)
    nodes = graph['nodes']
    index = {n['key']: j for j, n in enumerate(nodes)}
    require(len(index) == len(nodes) and set(index) == set(expected_times), 'shared exact node identity / ties')
    require(q(graph['epsilon']) == epsilon and graph['relaxed'] == relaxed, 'graph tolerance and layer')
    for name, s in expected_times.items():
        require(q(nodes[index[name]]['scaled_time']) == s, 'scaled-time arithmetic')
        if relaxed:
            require(tuple(map(q, nodes[index[name]]['interval'])) == intervals[name], 'outer scaled-time envelope')
    require(graph['references'] == {k: index[v] for k, v in references.items()}, 'distinct finite-reference denominators')
    require(graph['observations'] == {k: index[v] for k, v in observations.items()}, 'observation node binding')
    expected_edges = []
    if relaxed:
        for a, (alo, ahi) in intervals.items():
            for b, (blo, bhi) in intervals.items():
                if a != b and ahi <= blo:
                    expected_edges.append((index[a], index[b], F(1), 'forced_scaled_order'))
    else:
        ordered = sorted(expected_times, key=expected_times.get)
        expected_edges += [(index[a], index[b], F(1), 'scaled_order') for a, b in zip(ordered, ordered[1:])]
    zeros = {index['zero' if relaxed else '0']}
    negative_uppers = set()
    for r in rows:
        v, u = index[observations[r['observation_id']]], index[references[r['trace_id']]]
        lo, hi = (r['outer_L'], r['outer_U']) if relaxed else (r['L'], r['U'])
        if lo > epsilon:
            expected_edges.append((u, v, lo-epsilon, r['observation_id']+':lower'))
        if hi+epsilon > 0:
            expected_edges.append((v, u, 1/(hi+epsilon), r['observation_id']+':upper'))
        elif hi+epsilon == 0:
            zeros.add(v)
        else:
            negative_uppers.add(r['observation_id'])
    actual_edges = [(u, v, q(a), reason) for u, v, a, reason in graph['edges']]
    require(Counter(actual_edges) == Counter(expected_edges), 'complete independently reconstructed shared constraints')
    require(set(graph['zero_nodes']) == zeros, 'H(0) and zero-upper protections')
    require((graph['direct_negative_upper'] in negative_uppers) if negative_uppers else graph['direct_negative_upper'] is None, 'negative upper disposition')
    return actual_edges


def check_lower(graph, cert, rows, trs, epsilon, baseline, relaxed):
    edges = check_graph(graph, rows, trs, epsilon, relaxed)
    refs = set(graph['references'].values())
    kind = cert['kind']
    if kind == 'independent_baseline':
        require(epsilon == baseline, 'independent lower bound')
        return
    if kind == 'negative_upper':
        r = next(r for r in rows if r['observation_id'] == cert['observation_id'])
        require((r['outer_U'] if relaxed else r['U'])+epsilon < 0, 'negative upper certificate')
        return
    def walk(path, initial):
        node, multiplier = initial, F(1)
        for edge_id in path:
            u, v, a, reason = edges[edge_id]
            require(u == node and a > 0, 'contiguous positive certificate path')
            node, multiplier = v, multiplier*a
        return node, multiplier
    if kind == 'forced_zero':
        path = cert['path']
        seed = edges[path[0]][0] if path else cert['terminal']
        require(seed in refs, 'positive-reference path seed')
        terminal, factor = walk(path, seed)
        require(terminal == cert['terminal'] and terminal in graph['zero_nodes'] and factor > 0, 'forced-zero contradiction')
        return
    require(kind == 'positive_cycle', 'recognized lower certificate')
    require(cert['seed'] in refs, 'cycle positive reference seed')
    start, reach_factor = walk(cert['reach_path'], cert['seed'])
    finish, cycle_factor = walk(cert['cycle'], start)
    require(finish == start and cycle_factor > 1 and reach_factor > 0, 'exact amplifying positive cycle')
    require(cycle_factor == q(cert['product']), 'reported exact cycle product')


def check_shared(record, rows, trs, baseline, relaxed, precision):
    lo, hi = q(record['epsilon_lower']), q(record['epsilon_upper'])
    require(baseline <= lo <= hi and hi-lo <= precision, 'certified optimum bracket')
    require(q(record['baseline_max']) == baseline, 'shared comparison baseline')
    require(q(record['delta_lower']) == lo-baseline and q(record['delta_upper']) == hi-baseline, 'nonnegative incremental discrepancy')
    check_lower(record['lower_graph'], record['lower_certificate'], rows, trs, lo, baseline, relaxed)
    graph, witness = record['upper_graph'], record['upper_witness']
    edges = check_graph(graph, rows, trs, hi, relaxed)
    require(witness['feasible'] is True, 'upper witness feasibility flag')
    h = list(map(q, witness['h']))
    require(len(h) == len(graph['nodes']) and min(h) >= 0, 'nonnegative shared witness')
    require(all(h[k] >= 1 for k in graph['references'].values()), 'strictly positive reference scaling')
    require(all(h[k] == 0 for k in graph['zero_nodes']), 'shared fixed zeros')
    require(all(h[v] >= a*h[u] for u, v, a, _ in edges), 'all exact witness inequalities')
    for r in rows:
        model = h[graph['observations'][r['observation_id']]] / h[graph['references'][r['trace_id']]]
        l, u = (r['outer_L'], r['outer_U']) if relaxed else (r['L'], r['U'])
        require(residual(model, l, u) <= hi, 'finite-reference witness residual')
    expected = 'NONEMPTY_OUTER_FEASIBLE_SET_ONLY' if relaxed else 'CONSTRUCTED_COMPATIBLE_WITNESS'
    require(record['disposition'] == expected, 'no relaxed compatibility mislabeled joint proof')
    require(record['source_joint_disposition'] == 'UNRESOLVED_FIGURE_AND_CLOCK_CONSISTENCY', 'source joint ceiling')
    return lo, hi


def close(a, b, label, tolerance=2e-11):
    require(abs(float(a)-float(b)) <= tolerance, label)


def verify(output):
    c, traces, raw, obs = reconstruct()
    primary = {k:r for k,r in obs.items() if r['figure'] == 10}
    reported_obs = read_json(output / 'observations.json')
    require(len(reported_obs) == len(raw), 'retained supported and unsupported source coverage')
    out_obs = {r['observation_id']:r for r in reported_obs}
    require(len(out_obs) == len(reported_obs), 'no duplicate observations')
    for raw_row in raw:
        rr = out_obs[raw_row['observation_id']]
        require(all(rr[k] == v for k,v in raw_row.items()), 'native readings unchanged')
    for ident, r in obs.items():
        for key in ('t','L','U','value','outer_L','outer_U','t_lo','t_hi'):
            require(q(out_obs[ident][key]) == r[key], 'independent pixel-to-data mapping: '+ident+':'+key)
    base, outer = read_json(output/'baselines.json'), read_json(output/'outer_baselines.json')
    particles = {r['trace_id']:r for r in read_json(output/'particles.json')}
    require(set(particles) == set(traces), 'all particle summaries')
    B, BO = {}, {}
    for tid, tr in traces.items():
        rows = [r for r in primary.values() if r['trace_id'] == tid]
        B[tid], BO[tid] = independent_baseline(rows), independent_baseline(rows, True)
        check_baseline(rows, base[tid], B[tid])
        check_baseline(rows, outer[tid], BO[tid], True)
        p = particles[tid]
        require(q(p['B']) == B[tid] and q(p['B_outer']) == BO[tid], 'particle baseline summary')
        require(p['supported_count'] == len(rows) and p['group_id'] == tr['group_id'], 'particle coverage and group')
        require(q(p['modeled_radius_m']) == q(tr['diameter_um'])/2_000_000, 'projected diameter to assumed radius')
        require(q(p['earliest_s']) == min(r['t'] for r in rows) and q(p['latest_s']) == max(r['t'] for r in rows), 'native temporal span')
        first = min(rows,key=lambda r:r['t'])
        require(q(p['earliest_p']) == first['value'] and q(p['earliest_lower']) == first['L'] and q(p['earliest_upper']) == first['U'], 'earliest source progress')
    certificates = read_json(output/'certificates.json')
    groups = {g['group_id']:g for g in read_json(output/'groups.json')}
    require(set(groups) == {t['group_id'] for t in traces.values()} == set(certificates), 'four independent groups')
    summaries = []
    for group, g in groups.items():
        trs = {k:v for k,v in traces.items() if v['group_id'] == group}
        rows = [r for r in primary.values() if r['trace_id'] in trs]
        bmax, bomax = max(B[k] for k in trs), max(BO[k] for k in trs)
        lo, hi = check_shared(certificates[group]['fixed'], rows, trs, bmax, False, q(c['shared_epsilon_bracket_fraction']))
        olo, ohi = check_shared(certificates[group]['outer'], rows, trs, bomax, True, q(c['shared_epsilon_bracket_fraction']))
        require(q(g['baseline_max']) == bmax and q(g['epsilon_lower']) == lo and q(g['epsilon_upper']) == hi, 'group optimum summary')
        require(q(g['delta_lower']) == lo-bmax and q(g['delta_upper']) == hi-bmax, 'group penalty summary')
        require(q(g['outer_epsilon_lower']) == olo and q(g['outer_epsilon_upper']) == ohi, 'outer group summary')
        require(g['outer_disposition'] == 'NONEMPTY_OUTER_FEASIBLE_SET_ONLY', 'outer summary claim ceiling')
        require(g['fixed_disposition'] == 'CONSTRUCTED_COMPATIBLE_WITNESS', 'fixed summary witness disposition')
        require(g['particles'] == len(trs) and g['supported_count'] == len(rows), 'group counts')
        summaries.append(dict(group=group, baseline_pp=float(100*bmax), epsilon_pp=[float(100*lo),float(100*hi)], penalty_pp=[float(100*(lo-bmax)),float(100*(hi-bmax))]))
    # Independent calls use the unmodified production kernel, not the analysis wrapper.
    sys.path.insert(0,str(ROOT))
    import numpy as np
    from puckworks.models.mo2023_2 import swelling
    require(swelling.D_W == 1.25e-10 and swelling.C_M == .1, 'frozen Mo defaults')
    mo = list(csv.DictReader((output/'mo_predictions.csv').open()))
    require(len(mo) == len(primary) and {r['observation_id'] for r in mo} == set(primary), 'Mo supported-observation coverage, no Figure7 doubling')
    diagnostics = {r['trace_id']:r for r in read_json(output/'mo_numerics.json')}
    for tid,tr in traces.items():
        rows = [r for r in mo if r['trace_id'] == tid]
        times = np.unique([0.,1200.] + [float(primary[r['observation_id']]['t']) for r in rows])
        volume = swelling.swelling_volume_ratio(float(q(tr['diameter_um'])/2_000_000),times,D_w=1.25e-10,c_m=.1,N=240)
        model = np.expm1(np.log(volume)/3)/np.expm1(np.log(volume[-1])/3)
        errs = []
        for r in rows:
            source = primary[r['observation_id']]
            require(q(r['t_s']) == source['t'], 'Mo exact source-time identity')
            pred = model[np.searchsorted(times,float(source['t']))]
            close(r['p240'],pred,'independent frozen Mo N240 reproduction')
            err = residual(float(r['p240']),float(source['L']),float(source['U']))
            close(r['distance240'],err,'Mo interval discrepancy')
            errs.append(err)
        close(particles[tid]['mo_discrepancy240'],max(errs),'particle Mo maximum')
        close(particles[tid]['mo_increment'],max(errs)-float(B[tid]),'particle Mo increment')
        d = diagnostics[tid]
        require(len(d['runs']) == 4, '60/120/240 plus tolerance runs')
        for run, cells, rt, at in zip(d['runs'],[60,120,240,240],[1e-7]*3+[1e-9],[1e-9]*3+[1e-11]):
            require(run['cells'] == cells and run['D_W'] == 1.25e-10 and run['C_M'] == .1, 'frozen numerical metadata')
            require(run['solver']['success'] and run['solver']['status'] == 0, 'Mo solver success')
            require(-1e-8 <= run['solver']['state_min'] <= run['solver']['state_max'] <= .1+1e-8, 'Mo concentration bounds on recorded states')
            require(run['solver']['rtol'] == rt and run['solver']['atol'] == at, 'documented integrator tolerances')
            initial = 1+1/(2*cells*cells)+1/(6*cells)
            close(run['initial_volume'],initial,'raw initial quadrature defect')
            close(run['discrete_quadrature_ceiling'],(1+1/(2*cells*cells))/.9,'discrete volume ceiling')
            require(run['reference_progress'] == 1 and run['initial_progress_pp'] > 0 and run['endpoint_disposition'] == 'RAW_FINITE_GRID_INITIAL_ENDPOINT_DEFECT', 'honest finite-grid endpoint limitation')
        close(d['max_60_120_pp'],100*max(abs(float(r['p60'])-float(r['p120'])) for r in rows),'60/120 mesh discrepancy')
        close(d['max_120_240_pp'],100*max(abs(float(r['p120'])-float(r['p240'])) for r in rows),'120/240 mesh discrepancy')
        close(d['max_240_tolerance_pp'],100*max(abs(float(r['p240'])-float(r['p240_tight'])) for r in rows),'tolerance discrepancy')
    for group,g in groups.items():
        candidates = [p for p in particles.values() if p['group_id'] == group]
        worst = max(candidates,key=lambda p:p['mo_discrepancy240'])
        require(g['mo_worst_trace'] == worst['trace_id'], 'worst Mo particle identity')
        close(g['mo_worst240'],worst['mo_discrepancy240'],'group worst Mo discrepancy')
    result = read_json(output/'RESULT.json')
    require(result['PHYSICAL_VALIDATION'] == 'NOT_ESTABLISHED' and result['primary_count'] == len(primary), 'result claim ceiling and coverage')
    require(result['source_consistency'] == 'UNRESOLVED_MATERIAL_FIGURE7_FIGURE10_CONTRADICTION', 'source contradiction preserved')
    # Reconstruct every conditional Figure7 transformation and matched-frame gap.
    converted = {r['observation_id']:r for r in read_json(output/'figure7_converted.json')}
    f7 = {k:r for k,r in obs.items() if r['figure']==7}
    require(set(converted) == set(f7), 'Figure7 conversion coverage')
    expected_pairs = {}
    for ident, r in f7.items():
        refs = [z for z in f7.values() if z['trace_id']==r['trace_id'] and z['t']==REFERENCE]
        entry = converted[ident]
        if len(refs)!=1 or refs[0]['outer_L']<=0:
            require(entry['status'] == 'NO_AUTHENTICATED_EXACT_T_GRAPHICAL_REFERENCE', 'missing Figure7 reference not invented')
            continue
        ref = refs[0]
        lo, hi = r['outer_L']/ref['outer_U'], r['outer_U']/ref['outer_L']
        if ident == ref['observation_id']:
            lo = hi = F(1)
        require(entry['reference_id']==ref['observation_id'] and q(entry['lower'])==lo and q(entry['upper'])==hi, 'conditional reference ratio')
        require(entry['status']=='CONDITIONAL_FIG7_CONVERSION_SHARED_REFERENCE_OUTER_ONLY', 'reference correlation limit')
        for second in primary.values():
            same_trace = second['trace_id']==r['trace_id']
            time_overlap = r['t_lo']<=second['t_hi'] and second['t_lo']<=r['t_hi']
            if same_trace and time_overlap:
                expected_pairs[(ident,second['observation_id'])] = (lo,hi,max(F(0),second['outer_L']-hi,lo-second['outer_U']))
    pairs = read_json(output/'figure_consistency.json')
    require(len(pairs)==len(expected_pairs), 'complete conditional figure comparison')
    for row in pairs:
        key = row['figure7_id'],row['figure10_id']
        lo,hi,gap = expected_pairs.pop(key)
        require(list(map(q,row['figure7_progress_outer']))==[lo,hi] and q(row['separated_by'])==gap, 'exact conditional source gap')
        require(row['disposition']==('INCONSISTENT_UNDER_SAME_FRAME_MAPPING' if gap>0 else 'NOT_SEPARATED'), 'conditional consistency disposition')
        require('conditional same-source-frame correspondence' in row['time_relation'], 'frame correspondence not certified by time overlap alone')
    require(not expected_pairs, 'no omitted conditional source comparisons')
    decisive = next(r for r in pairs if r['figure7_id']=='f7a-m018' and r['figure10_id']=='f10a-m044')
    require(q(decisive['separated_by'])==F(3469,8165), 'approximately120s medium543 source discrepancy')
    for filename in ['monotone_baselines.csv','mo_comparison.csv']:
        summary_rows = list(csv.DictReader((output/filename).open()))
        require(len(summary_rows)==17 and {r['trace_id'] for r in summary_rows}==set(traces), 'CSV particle coverage')
        for row in summary_rows:
            tid = row['trace_id']; particle=particles[tid]
            require(int(row['supported_count'])==particle['supported_count'], 'CSV coverage count')
            if filename=='monotone_baselines.csv':
                require(q(row['B_fraction'])==B[tid], 'CSV exact baseline')
                close(row['B_pp'],100*B[tid],'CSV baseline percentage points')
                close(row['B_outer_pp'],100*BO[tid],'CSV outer baseline percentage points')
            else:
                close(row['Mo240_pp'],100*particle['mo_discrepancy240'],'CSV Mo percentage points')
                close(row['baseline_pp'],100*B[tid],'CSV Mo baseline')
                close(row['increment_pp'],100*particle['mo_increment'],'CSV Mo increment')
    progress_rows = list(csv.DictReader((output/'progress_summary.csv').open()))
    require(len(progress_rows)==34, 'requested30s and240s summaries')
    for row in progress_rows:
        tid,target = row['trace_id'],q(row['target_s'])
        series = sorted((r for r in primary.values() if r['trace_id']==tid),key=lambda r:r['t'])
        exact = [r for r in series if r['t']==target]
        prior,nexts = [r for r in series if r['t']<target],[r for r in series if r['t']>target]
        if exact:
            lo,hi,status = min(r['L'] for r in exact),max(r['U'] for r in exact),'direct_native'
            ids = [r['observation_id'] for r in exact]
        elif prior and nexts:
            left,right=prior[-1],nexts[0]
            weight=(target-left['t'])/(right['t']-left['t'])
            lo,hi=(1-weight)*left['L']+weight*right['L'],(1-weight)*left['U']+weight*right['U']
            status='CONDITIONAL_LINEAR_INTERPOLATION_NOT_MEASURED'
            ids=[left['observation_id'],right['observation_id']]
        else:
            require(row['status']=='INSUFFICIENT_SOURCE_SUPPORT' and not row['lower_fraction'] and not row['upper_fraction'], 'no synthetic unsupported target estimate')
            continue
        require(row['status']==status and row['support_ids']==';'.join(ids),'source interpolation labels and brackets')
        require(q(row['lower_fraction'])==lo and q(row['upper_fraction'])==hi,'independent conditional interpolation')
    hashes = read_json(output/'hashes.json')
    for filename,digest in hashes.items():
        require(hashlib.sha256((output/filename).read_bytes()).hexdigest() == digest, 'artifact digest '+filename)
    return dict(status='PASS', source_points=len(raw), supported_primary=len(primary), particles=len(traces), groups=summaries,
        independent_Mo_calls=17, source_joint_disposition='UNRESOLVED', PHYSICAL_VALIDATION='NOT_ESTABLISHED')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=DEFAULT)
    args=parser.parse_args()
    print(json.dumps(verify(args.output),indent=2,sort_keys=True))


if __name__=='__main__':
    main()

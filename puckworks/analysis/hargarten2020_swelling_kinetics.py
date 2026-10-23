"""Offline, source-internal Hargarten graphical kinetics; no production physics change.

The rational constraint graph is a finite feasibility algorithm, not a fitted
analytic swelling law. Original-source consistency remains separately unresolved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path
from unittest.mock import patch

import numpy as np

from puckworks.models.mo2023_2 import swelling

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/hargarten2020/swelling_kinetics_001'
DEFAULT_OUTPUT = ROOT / 'docs/analysis/sci_md_hargarten_swelling_kinetics_001'
T = Q(1200)


def rational(x):
    return x if isinstance(x, Q) else Q(str(x))


def radius_m(diameter_um):
    d = rational(diameter_um)
    if d <= 0:
        raise ValueError('projected diameter must be positive')
    return d / 2_000_000


def mapped(x, a, b, maximum):
    return (rational(x) - rational(a)) * rational(maximum) / (rational(b) - rational(a))


def read_inputs(data=DATA):
    contract = json.loads((data / 'contract.json').read_text())
    traces = json.loads((data / 'traces.json').read_text())
    raw = list(csv.DictReader((data / 'coordinates.csv').open()))
    if len({r['observation_id'] for r in raw}) != len(raw):
        raise ValueError('duplicate observation identifier')
    ids = {t['trace_id'] for t in traces}
    observations = []
    for r in raw:
        p = contract['panels'][r['panel_id']]
        z = dict(r)
        z['figure'] = p['figure']
        if r['support_status'] != 'supported':
            observations.append(z)
            continue
        if r['trace_id'] not in ids or r['source_sha256'] != contract['source']['sha256']:
            raise ValueError('unbound source or trace')
        x, y = rational(r['x_px']), rational(r['y_px'])
        allowance = Q(contract['marker_allowance_px'])
        z.update(t=mapped(x, p['x0'], p['x1'], p['t_max']),
                 L=mapped(y + allowance, p['y0'], p['y1'], p['y_max_percent']) / 100,
                 U=mapped(y - allowance, p['y0'], p['y1'], p['y_max_percent']) / 100,
                 value=mapped(y, p['y0'], p['y1'], p['y_max_percent']) / 100)
        tx, py = [], []
        for a, b, sign in itertools.product([-1, 1], repeat=3):
            tx.append(mapped(x + sign * allowance, p['x0'] + a, p['x1'] + b, p['t_max']))
            py.append(mapped(y + sign * allowance, p['y0'] + a, p['y1'] + b, p['y_max_percent']) / 100)
        # Domain clipping restricts latent coordinate, NEVER the observed ordinate.
        z.update(t_lo=max(Q(0), min(tx)), t_hi=min(Q(p['t_max']), max(tx)),
                 outer_L=min(py), outer_U=max(py))
        observations.append(z)
    return contract, traces, observations


def distance(value, lower, upper):
    return max(lower - value, 0, value - upper)


def baseline(obs, relaxed=False):
    """Exact L-infinity isotonic interval projection with fixed0/T endpoints."""
    if not obs:
        return dict(disposition='INSUFFICIENT_SOURCE_SUPPORT', B=None, witness=[])
    bounds = lambda o: (o['outer_L'], o['outer_U']) if relaxed else (o['L'], o['U'])
    before = lambda a, b: a['t_hi'] <= b['t_lo'] if relaxed else a['t'] <= b['t']
    candidates = [(Q(0), ['nonnegative_discrepancy'])]
    for o in obs:
        l, u = bounds(o)
        candidates.extend([(l - 1, [o['observation_id'], 'endpoint_T']),
                           (-u, ['endpoint_0', o['observation_id']])])
        if not relaxed and o['t'] == 0:
            candidates.append((l, [o['observation_id'], 'endpoint_0']))
        if not relaxed and o['t'] == T:
            candidates.append((1-u, ['endpoint_T', o['observation_id']]))
        for b in obs:
            if before(o, b):
                candidates.append(((l - bounds(b)[1]) / 2,
                                   [o['observation_id'], b['observation_id']]))
    B, decisive = max(candidates, key=lambda x: x[0])
    witness = []
    for o in obs:
        m = max([Q(0), bounds(o)[0] - B] + [bounds(a)[0] - B for a in obs if before(a, o)])
        if o['t'] == T and not relaxed:
            m = Q(1)
        if o['t'] == 0 and not relaxed:
            m = Q(0)
        witness.append(dict(observation_id=o['observation_id'], t=o['t'], p=m))
    return dict(disposition=('EXACT_PARTIAL_ORDER_OUTER_OPTIMUM_NECESSARY_ONLY' if relaxed
                             else 'EXACT_SUPPORTED_SUBSET_OPTIMUM'), B=B,
                decisive=decisive, witness=witness,
                coordinate_layer='outer_partial_order' if relaxed else 'fixed_native')


def graph_constraints(obs, traces, epsilon, relaxed=False):
    """h[v]>=a*h[u]. Exact ties share a variable in the fixed-coordinate graph."""
    epsilon = rational(epsilon)
    if epsilon < 0:
        raise ValueError('negative discrepancy')
    ts = {t['trace_id']: t for t in traces}
    values = {}; intervals = {}; refs = {}; obskeys = {}
    def node(key, value, lo=None, hi=None):
        values[key] = value
        intervals[key] = (value if lo is None else lo, value if hi is None else hi)
        return key
    zero = node('zero' if relaxed else Q(0), Q(0))
    for tid, tr in ts.items():
        d = rational(tr['diameter_um']); r = radius_m(d)
        s = T / r**2
        key = 'ref:' + tid if relaxed else s
        refs[tid] = node(key, s, T/radius_m(d+Q('0.5'))**2,
                        T/radius_m(d-Q('0.5'))**2)
    for o in obs:
        d = rational(ts[o['trace_id']]['diameter_um']); r = radius_m(d)
        s = o['t'] / r**2
        key = o['observation_id'] if relaxed else s
        obskeys[o['observation_id']] = node(key, s,
            o['t_lo']/radius_m(d+Q('0.5'))**2,
            o['t_hi']/radius_m(d-Q('0.5'))**2)
    keys = sorted(values, key=lambda k: (values[k], str(k)))
    idx = {k: i for i, k in enumerate(keys)}; edges = []
    def edge(u, v, a, reason):
        edges.append([idx[u], idx[v], a, reason])
    if relaxed:
        for a in keys:
            for b in keys:
                if a != b and intervals[a][1] <= intervals[b][0]:
                    edge(a, b, Q(1), 'forced_scaled_order')
    else:
        for a, b in zip(keys, keys[1:]):
            edge(a, b, Q(1), 'scaled_order')
    zeros = {idx[zero]}; direct = None
    for o in obs:
        v = obskeys[o['observation_id']]; u = refs[o['trace_id']]
        l = o['outer_L'] if relaxed else o['L']
        h = o['outer_U'] if relaxed else o['U']
        if l-epsilon > 0:
            edge(u, v, l-epsilon, o['observation_id'] + ':lower')
        if h+epsilon > 0:
            edge(v, u, 1/(h+epsilon), o['observation_id'] + ':upper')
        elif h+epsilon == 0:
            zeros.add(idx[v])
        else:
            direct = o['observation_id']
    return dict(nodes=[dict(key=str(k), scaled_time=values[k], interval=intervals[k]) for k in keys],
                edges=edges, references={k: idx[v] for k, v in refs.items()},
                observations={k: idx[v] for k, v in obskeys.items()},
                zero_nodes=sorted(zeros), direct_negative_upper=direct,
                epsilon=epsilon, relaxed=relaxed)


def feasible(graph):
    """Exact Bellman-style longest products, seeded by every positive reference.

    All refs>=1 is equivalent under free multiplicative scaling to strict
    positivity of finitely many denominators. No arbitrary physical cutoff.
    """
    n = len(graph['nodes']); edges = graph['edges']; h = [Q(0)] * n
    paths = [[] for _ in range(n)]
    for i in graph['references'].values():
        h[i] = Q(1)
    if graph['direct_negative_upper']:
        return dict(feasible=False, certificate=dict(kind='negative_upper',
            observation_id=graph['direct_negative_upper']))
    for _ in range(n):
        old = h[:]; oldpaths = [p[:] for p in paths]; changed = []
        for j, (u, v, a, _) in enumerate(edges):
            candidate = old[u] * a
            if candidate > h[v]:
                h[v] = candidate; paths[v] = oldpaths[u] + [j]; changed.append(v)
        for v in graph['zero_nodes']:
            if h[v] > 0:
                return dict(feasible=False, certificate=dict(kind='forced_zero',
                    path=paths[v], terminal=v))
        if not changed:
            return dict(feasible=True, h=h, convention='all_references_ge_1_scale_equivalent')
    # An n-edge improving path must contain a strictly amplifying cycle.
    for v in changed:
        path = paths[v]
        if not path:
            continue
        nodes = [edges[path[0]][0]] + [edges[e][1] for e in path]
        for j in range(len(nodes)):
            product = Q(1)
            for k in range(j+1, len(nodes)):
                product *= edges[path[k-1]][2]
                if nodes[k] == nodes[j] and product > 1:
                    return dict(feasible=False, certificate=dict(kind='positive_cycle',
                        reach_path=path[:j], cycle=path[j:k], product=product,
                        seed=nodes[0]))
    return dict(feasible=None, disposition='NUMERICALLY_UNRESOLVED')


def shared(obs, traces, lower, relaxed=False, precision=Q('0.0001')):
    if not obs or any(not any(o['trace_id']==t['trace_id'] for o in obs) for t in traces):
        return dict(disposition='INSUFFICIENT_SOURCE_SUPPORT')
    def run(e):
        g = graph_constraints(obs, traces, e, relaxed)
        return g, feasible(g)
    lo = lower; gl, fl = run(lo)
    if fl['feasible'] is None:
        return dict(disposition='NUMERICALLY_UNRESOLVED')
    if fl['feasible']:
        hi = lo; gh, fh = gl, fl; low_certificate = {'kind':'independent_baseline'}
    else:
        hi = max(Q(2), lo+1); gh, fh = run(hi)
        if not fh['feasible']:
            return dict(disposition='NUMERICALLY_UNRESOLVED')
        while hi-lo > precision:
            mid = (lo+hi)/2; gm, fm = run(mid)
            if fm['feasible'] is None:
                return dict(disposition='NUMERICALLY_UNRESOLVED')
            if fm['feasible']:
                hi, gh, fh = mid, gm, fm
            else:
                lo, gl, fl = mid, gm, fm
        low_certificate = fl['certificate']
    return dict(disposition='NONEMPTY_OUTER_FEASIBLE_SET_ONLY' if relaxed else
                'CONSTRUCTED_COMPATIBLE_WITNESS', epsilon_lower=lo, epsilon_upper=hi,
                baseline_max=lower, delta_lower=max(Q(0),lo-lower), delta_upper=hi-lower,
                lower_graph=gl, lower_certificate=low_certificate,
                upper_graph=gh, upper_witness=fh,
                lower_exclusion='CERTIFIED_INCOMPATIBILITY' if lo>lower else 'BASELINE_BOUND',
                source_joint_disposition='UNRESOLVED_FIGURE_AND_CLOCK_CONSISTENCY')


def mo_prediction(diameter_um, times, cells=120, tight=False):
    """Call frozen production kernel unchanged; preserve raw t=0 defect."""
    if swelling.D_W != 1.25e-10 or swelling.C_M != .1:
        raise ValueError('frozen production parameters changed')
    requested = np.asarray([float(t) for t in times])
    if np.any(~np.isfinite(requested)) or np.any(requested < 0) or np.any(requested > float(T)):
        raise ValueError('times outside finite reference domain')
    ordered = np.unique(np.r_[requested, 0., float(T)])
    original = swelling.solve_ivp; receipts = []
    def monitored(*a, **kw):
        if tight:
            kw.update(rtol=1e-9, atol=1e-11)
        sol = original(*a, **kw)
        receipts.append(dict(success=bool(sol.success), status=int(sol.status),
            rtol=kw['rtol'], atol=kw['atol'], state_min=float(np.min(sol.y)),
            state_max=float(np.max(sol.y))))
        if not sol.success or sol.y.shape[1] != len(ordered) or not np.isfinite(sol.y).all():
            raise RuntimeError('Mo solver failed or returned incomplete/nonfinite states')
        return sol
    with patch.object(swelling, 'solve_ivp', monitored):
        volume = swelling.swelling_volume_ratio(float(radius_m(diameter_um)), ordered,
            D_w=1.25e-10, c_m=.1, N=cells)
    growth = np.cbrt(volume)-1
    if growth[-1] <= 0 or not np.isfinite(volume).all():
        raise RuntimeError('invalid finite-reference denominator')
    progress = growth/growth[-1]
    # Numerical checks use explicit recorded tolerances; no claim of exact physical bounds.
    if np.min(np.diff(volume)) < -1e-8 or np.min(volume) < 1-1e-10:
        raise RuntimeError('nonmonotone or sub-dry native volume')
    quadrature_ceiling = (1+1/(2*cells**2))/(1-.1)
    if np.max(volume) > quadrature_ceiling+1e-8:
        raise RuntimeError('volume exceeds discrete quadrature ceiling')
    diagnostics = dict(cells=cells, D_W=1.25e-10, C_M=.1, solver=receipts[0],
        initial_progress_pp=float(100*progress[0]), initial_volume=float(volume[0]),
        reference_progress=float(progress[-1]), reference_volume=float(volume[-1]),
        physical_volume_ceiling=1/(1-.1), discrete_quadrature_ceiling=quadrature_ceiling,
        physical_bound_excess=max(0.,float(np.max(volume))-1/(1-.1)),
        endpoint_disposition='RAW_FINITE_GRID_INITIAL_ENDPOINT_DEFECT',
        minimum_volume_increment=float(np.min(np.diff(volume))))
    return progress[np.searchsorted(ordered, requested)], diagnostics


def serial(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {k:serial(v) for k,v in value.items()}
    if isinstance(value, (list,tuple)):
        return [serial(v) for v in value]
    return value


def write_json(path, value):
    path.write_text(json.dumps(serial(value), indent=2, sort_keys=True, allow_nan=False)+'\n')


def write_csv(path, rows):
    if not rows:
        return
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader()
        w.writerows(serial(rows))


def at_time(obs, target):
    """Direct only at exact native coordinate; otherwise labelled linear estimate."""
    direct=[o for o in obs if o['t']==target]
    if direct:
        return dict(status='direct_native', ids=[o['observation_id'] for o in direct],
                    lower=min(o['L'] for o in direct),upper=max(o['U'] for o in direct))
    left=[o for o in obs if o['t']<target];right=[o for o in obs if o['t']>target]
    if not left or not right:
        return dict(status='INSUFFICIENT_SOURCE_SUPPORT')
    a=max(left,key=lambda o:o['t']);b=min(right,key=lambda o:o['t'])
    w=(target-a['t'])/(b['t']-a['t'])
    return dict(status='CONDITIONAL_LINEAR_INTERPOLATION_NOT_MEASURED',
                ids=[a['observation_id'],b['observation_id']], bracket_s=[a['t'],b['t']],
                lower=(1-w)*a['L']+w*b['L'],upper=(1-w)*a['U']+w*b['U'])


def source_consistency(observations):
    """Separate conditional Fig7 conversion; shared reference is NOT independent error."""
    supported=[o for o in observations if o['support_status']=='supported']
    converted=[]; findings=[]
    for o in supported:
        if o['figure']!=7:
            continue
        refs=[r for r in supported if r['figure']==7 and r['trace_id']==o['trace_id'] and r['t']==T]
        if len(refs)!=1 or refs[0]['outer_L']<=0:
            converted.append(dict(observation_id=o['observation_id'],trace_id=o['trace_id'],
                status='NO_AUTHENTICATED_EXACT_T_GRAPHICAL_REFERENCE'))
            continue
        ref=refs[0]
        lo=o['outer_L']/ref['outer_U'];hi=o['outer_U']/ref['outer_L']
        if o is ref:
            lo=hi=Q(1)
        converted.append(dict(observation_id=o['observation_id'],trace_id=o['trace_id'],
            reference_id=ref['observation_id'],t=o['t'],lower=lo,upper=hi,
            status='CONDITIONAL_FIG7_CONVERSION_SHARED_REFERENCE_OUTER_ONLY'))
        for b in supported:
            if b['figure']==10 and b['trace_id']==o['trace_id'] and max(o['t_lo'],b['t_lo'])<=min(o['t_hi'],b['t_hi']):
                gap=max(Q(0),b['outer_L']-hi,lo-b['outer_U'])
                findings.append(dict(trace_id=o['trace_id'],figure7_id=o['observation_id'],
                    figure10_id=b['observation_id'],reference_id=ref['observation_id'],
                    figure7_progress_outer=[lo,hi],figure10_progress_outer=[b['outer_L'],b['outer_U']],
                    separated_by=gap,time_relation='overlapping_graphical_time_bounds; conditional same-source-frame correspondence',
                    disposition='INCONSISTENT_UNDER_SAME_FRAME_MAPPING' if gap>0 else 'NOT_SEPARATED'))
    return converted,findings


def produce(output=DEFAULT_OUTPUT, plot=False):
    output.mkdir(parents=True,exist_ok=True)
    contract,traces,observations=read_inputs()
    primary=[o for o in observations if o['figure']==10 and o['support_status']=='supported']
    baselines={}; outer_baselines={}; particles=[]; mo_rows=[]; diagnostics=[]
    for tr in traces:
        tid=tr['trace_id'];obs=[o for o in primary if o['trace_id']==tid]
        b=baseline(obs);bo=baseline(obs,True);baselines[tid]=b;outer_baselines[tid]=bo
        if not obs:
            particles.append(dict(trace_id=tid,disposition='INSUFFICIENT_SOURCE_SUPPORT'))
            continue
        times=[o['t'] for o in obs]
        p60,d60=mo_prediction(tr['diameter_um'],times,60)
        p120,d120=mo_prediction(tr['diameter_um'],times,120)
        p240,d240=mo_prediction(tr['diameter_um'],times,240)
        ptight,dtight=mo_prediction(tr['diameter_um'],times,240,True)
        diagnostics.append(dict(trace_id=tid,runs=[d60,d120,d240,dtight],
            max_60_120_pp=float(np.max(np.abs(p60-p120))*100),
            max_120_240_pp=float(np.max(np.abs(p120-p240))*100),
            max_240_tolerance_pp=float(np.max(np.abs(p240-ptight))*100)))
        residual=[]
        for o,a,bm,c,d in zip(obs,p60,p120,p240,ptight):
            err=float(distance(c,float(o['L']),float(o['U'])));residual.append(err)
            mo_rows.append(dict(observation_id=o['observation_id'],trace_id=tid,t_s=o['t'],
                p60=float(a),p120=float(bm),p240=float(c),p240_tight=float(d),distance240=err))
        first=min(obs,key=lambda o:o['t'])
        particles.append(dict(trace_id=tid,group_id=tr['group_id'],diameter_um=tr['diameter_um'],
            modeled_radius_m=radius_m(tr['diameter_um']),supported_count=len(obs),
            earliest_s=min(times),latest_s=max(times),earliest_p=first['value'],
            earliest_lower=first['L'],earliest_upper=first['U'],B=b['B'],
            B_outer=bo['B'],decisive=b['decisive'],mo_discrepancy240=max(residual),
            mo_increment=max(residual)-float(b['B']),
            progress30=at_time(obs,Q(30)),progress240=at_time(obs,Q(240)),
            coverage='PARTIAL_NATIVE_FIGURE10_MARKERS; OVERLAPS_RETAINED_UNSUPPORTED'))
    groups=[];certificates={}
    for group in sorted({t['group_id'] for t in traces}):
        trs=[t for t in traces if t['group_id']==group];ids={t['trace_id'] for t in trs}
        obs=[o for o in primary if o['trace_id'] in ids]
        bmax=max(baselines[t]['B'] for t in ids);bouter=max(outer_baselines[t]['B'] for t in ids)
        fixed=shared(obs,trs,bmax);outer=shared(obs,trs,bouter,True)
        certificates[group]=dict(fixed=fixed,outer=outer)
        groups.append(dict(group_id=group,particles=len(trs),supported_count=len(obs),
            baseline_max=bmax,epsilon_lower=fixed.get('epsilon_lower'),
            epsilon_upper=fixed.get('epsilon_upper'),delta_lower=fixed.get('delta_lower'),
            delta_upper=fixed.get('delta_upper'),fixed_disposition=fixed['disposition'],
            outer_epsilon_lower=outer.get('epsilon_lower'),outer_epsilon_upper=outer.get('epsilon_upper'),
            outer_disposition=outer['disposition'],
            source_disposition='UNRESOLVED_FIGURE_AND_CLOCK_CONSISTENCY',
            mo_worst240=max(p['mo_discrepancy240'] for p in particles if p['group_id']==group),
            mo_worst_trace=max((p for p in particles if p['group_id']==group),key=lambda p:p['mo_discrepancy240'])['trace_id']))
    converted,consistency=source_consistency(observations)
    write_json(output/'figure7_converted.json',converted)
    write_json(output/'figure_consistency.json',consistency)
    write_json(output/'observations.json',observations)
    write_json(output/'baselines.json',baselines)
    write_json(output/'outer_baselines.json',outer_baselines)
    write_json(output/'particles.json',particles)
    flat=[{k:v for k,v in p.items() if k not in ['progress30','progress240','decisive']} for p in particles]
    write_csv(output/'particles.csv',flat)
    write_csv(output/'monotone_baselines.csv',[dict(trace_id=p['trace_id'],supported_count=p['supported_count'],
        B_fraction=p['B'],B_pp=float(p['B'])*100,B_outer_pp=float(p['B_outer'])*100,
        decisive_ids=';'.join(p['decisive'])) for p in particles])
    write_csv(output/'mo_comparison.csv',[dict(trace_id=p['trace_id'],group_id=p['group_id'],
        supported_count=p['supported_count'],Mo240_pp=p['mo_discrepancy240']*100,
        baseline_pp=float(p['B'])*100,increment_pp=p['mo_increment']*100) for p in particles])
    write_csv(output/'progress_summary.csv',[dict(trace_id=p['trace_id'],target_s=t,
        status=p[key]['status'],lower_fraction=p[key].get('lower'),upper_fraction=p[key].get('upper'),
        support_ids=';'.join(p[key].get('ids',[]))) for p in particles for t,key in [(30,'progress30'),(240,'progress240')]])
    write_json(output/'groups.json',groups);write_csv(output/'groups.csv',groups)
    write_json(output/'certificates.json',certificates)
    write_csv(output/'mo_predictions.csv',mo_rows);write_json(output/'mo_numerics.json',diagnostics)
    result=dict(task=contract['task'],PHYSICAL_VALIDATION='NOT_ESTABLISHED',
        source_consistency='UNRESOLVED_MATERIAL_FIGURE7_FIGURE10_CONTRADICTION',
        primary='Figure10 supported native graphical coordinates; no physical measurement-error authority',
        primary_count=len(primary),native_supported_count=sum(o['support_status']=='supported' for o in observations),
        unsupported_clusters=sum(o['support_status']=='unsupported_overlap_or_identity' for o in observations),
        definition_only_rows=sum(o['support_status']=='definition_only' for o in observations),
        groups=groups,
        max_mesh120_240_pp=max(d['max_120_240_pp'] for d in diagnostics),
        max_tolerance_pp=max(d['max_240_tolerance_pp'] for d in diagnostics))
    write_json(output/'RESULT.json',result)
    if plot:
        make_plot(output,traces,primary,baselines,certificates,mo_rows)
        native_plot(output,traces,observations)
        # Normalize Matplotlib's line-end whitespace without changing SVG tokens.
        for name in ('comparison.svg', 'figure7_native.svg'):
            path = output / name
            path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines())+'\n')
    files=sorted(p for p in output.iterdir() if p.suffix in ('.csv','.json','.svg') and p.name not in ('hashes.json','review_receipt.json','verification_record.json'))
    write_json(output/'hashes.json',{str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    return result


def make_plot(output,traces,obs,baselines,certificates,mo_rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    matplotlib.rcParams['svg.hashsalt']='hargarten-swelling-kinetics-001'
    fig,axs=plt.subplots(6,3,figsize=(13,18),sharex=True,sharey=True)
    mo={m['observation_id']:m for m in mo_rows}
    for ax,tr in zip(axs.flat,traces):
        rows=sorted([o for o in obs if o['trace_id']==tr['trace_id']],key=lambda o:o['t'])
        ts=[float(o['t']) for o in rows]
        ax.errorbar(ts,[100*float(o['value']) for o in rows],
            yerr=[100*float(o['U']-o['value']) for o in rows],fmt='o',ms=3,c='black',label='Fig. 10 ±3 px')
        bw={w['observation_id']:w['p'] for w in baselines[tr['trace_id']]['witness']}
        ax.plot(ts,[100*float(bw[o['observation_id']]) for o in rows],c='tab:blue',label='monotone witness')
        s=certificates[tr['group_id']]['fixed'];g=s['upper_graph'];h=s['upper_witness']['h']
        ref=h[g['references'][tr['trace_id']]]
        ax.plot(ts,[100*float(h[g['observations'][o['observation_id']]]/ref) for o in rows],
                '--',c='tab:green',label='shared witness')
        ax.plot(ts,[100*mo[o['observation_id']]['p240'] for o in rows],c='tab:orange',label='fixed Mo N240')
        ax.axhline(100,c='gray',lw=.6);ax.set_title(f"{tr['trace_id']} µm · {tr['protocol']}",fontsize=10)
        ax.set_xlim(0,305);ax.set_ylim(-5,155);ax.grid(alpha=.2)
    axs.flat[-1].axis('off');handles,labels=axs.flat[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower right',bbox_to_anchor=(.96,.07))
    fig.supxlabel('Native plotted time / s — all connecting lines are synthetic guides')
    fig.supylabel('Progress / percent of 1200 s diameter-growth reference')
    fig.suptitle('Conditional Figure 10 graphical comparison; Figure 7 depicts the same particles and is inconsistent\n'
                 'Bounds are reading allowances, not experimental uncertainty. Missing overlaps are not filled.',fontsize=12)
    fig.tight_layout(rect=(.02,.03,1,.96));fig.savefig(output/'comparison.svg',metadata={'Date':None});plt.close(fig)


def native_plot(output,traces,observations):
    import matplotlib.pyplot as plt
    fig,axs=plt.subplots(6,3,figsize=(13,18),sharex=True)
    for ax,tr in zip(axs.flat,traces):
        obs=sorted([o for o in observations if o['figure']==7 and o['support_status']=='supported' and o['trace_id']==tr['trace_id']],key=lambda o:o['t'])
        ax.errorbar([float(o['t']) for o in obs],[100*float(o['value']) for o in obs],
            yerr=[100*float(o['U']-o['value']) for o in obs],fmt='o',ms=3,c='black')
        ax.set_title(tr['trace_id']+' µm · '+tr['protocol'],fontsize=10)
        ax.set_xlim(0,1220);ax.grid(alpha=.2)
    axs.flat[-1].axis('off')
    fig.supxlabel('Native graphical time / s; no interpolated observations')
    fig.supylabel('Figure 7 relative projected-diameter increase / percent')
    fig.suptitle('Same 17 particles as Figure 10; supported marker subset only\n'
                 'Reading allowances ±3 px; missing overlaps retained in intake. Hargarten et al. (2020), CC BY-NC',fontsize=12)
    fig.tight_layout(rect=(.02,.03,1,.96));fig.savefig(output/'figure7_native.svg',metadata={'Date':None});plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    p.add_argument('--plot',action='store_true');args=p.parse_args()
    print(json.dumps(serial(produce(args.output,args.plot)),indent=2))


if __name__=='__main__':
    main()

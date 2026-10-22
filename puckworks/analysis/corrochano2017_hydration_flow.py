"""Fixed reported-flow Figure 6.22 comparison; offline compact factual inputs only.

G1 / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL.
NO_GOVERNING_PHYSICS_CHANGE. PHYSICAL_VALIDATION=NOT_ESTABLISHED.
Exact rational reading enclosures are a conservative shared-axis outer relaxation.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as F
import hashlib
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT/'puckworks/data/romancorrochano2017/fig6_22_hydration_flow'
OUTPUT = ROOT/'docs/analysis/sci_md_corrochano_hydration_flow_rescaling_001'
TASK = 'SCI-MD-CORROCHANO-HYDRATION-FLOW-RESCALING-001'
SEPARATED = 'SEPARATED_UNDER_DECLARED_READING_CONTRACT'
OVERLAP = 'NOT_EXCLUDED_BY_DECLARED_COMPARISON'
UNSUPPORTED = 'UNSUPPORTED'
IDS = {'low': ['L1', 'L2', 'L3'], 'high': ['H1', 'H2', 'H3']}


def union(intervals):
    """Union without filling positive gaps."""
    out = []
    for a, b in sorted(intervals):
        if b < a:
            raise ValueError('Reversed support')
        if out and a <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def intersection(a, b):
    return union((max(x, u), min(y, v)) for x, y in a for u, v in b
                 if max(x, u) <= min(y, v))


def contains(support, query):
    return any(a <= query[0] <= query[1] <= b for a, b in support)


class Calibration:
    def __init__(self, values):
        self.c = {k: F(v) for k, v in values.items() if not isinstance(v, list)}
        self.guard = self.c['stroke_guard_pt']+self.c['reconstruction_guard_pt']
        g = self.c['anchor_guard_pt']
        self.x_corners = list(product([self.c['x_20']-g, self.c['x_20']+g],
                                      [self.c['x_80']-g, self.c['x_80']+g]))
        self.y_corners = list(product([self.c['y_0']-g, self.c['y_0']+g],
                                      [self.c['y_1']-g, self.c['y_1']+g]))
        if any(b <= a for a, b in self.x_corners) or any(a <= b for a, b in self.y_corners):
            raise ValueError('Degenerate calibration')

    def x(self, t):
        return self.c['x_20']+(F(t)-20)*(self.c['x_80']-self.c['x_20'])/60

    def time(self, x):
        return 20+60*(F(x)-self.c['x_20'])/(self.c['x_80']-self.c['x_20'])

    def y(self, p):
        return (self.c['y_0']-F(p))/(self.c['y_0']-self.c['y_1'])

    def query(self, t):
        a = (F(t)-20)/60
        xs = [(1-a)*x20+a*x80 for x20, x80 in self.x_corners]
        return min(xs)-self.guard, max(xs)+self.guard

    def ordinate(self, bounds):
        ys = [(zero-p)/(zero-one) for zero, one in self.y_corners
              for p in [bounds[0]-self.guard, bounds[1]+self.guard]]
        return min(ys), max(ys)

    def time_support(self, support, full):
        if not full:
            return [(self.time(a), self.time(b)) for a, b in support]
        # Every anchor-corner query plus stroke/reconstruction must be contained.
        # Each inverse affine corner has positive slope, so these are exact bounds.
        result = []
        for a, b in support:
            lower = max(20+60*(a+self.guard-x20)/(x80-x20)
                        for x20, x80 in self.x_corners)
            upper = min(20+60*(b-self.guard-x20)/(x80-x20)
                        for x20, x80 in self.x_corners)
            if lower <= upper:
                result.append((lower, upper))
        return union(result)


def curve_extrema(segments, query):
    """Extrema over an entire admitted x range, including vertical segments."""
    values = []
    for (x0, y0), (x1, y1) in segments:
        a, b = max(query[0], min(x0, x1)), min(query[1], max(x0, x1))
        if a > b:
            continue
        if x0 == x1:
            values.extend([y0, y1])
        else:
            values.extend(y0+(x-x0)*(y1-y0)/(x1-x0) for x in [a, b])
    if not values:
        raise ValueError('No represented curve in query')
    return min(values), max(values)


def read_trace(trace, time, cal):
    q = cal.query(time)
    nominal = contains(trace['support_x'], (cal.x(time), cal.x(time)))
    full = contains(trace['support_x'], q)
    return dict(nominal_support=nominal, full_support=full, query_x_pt=q,
                bounds=cal.ordinate(curve_extrema(trace['segments'], q)) if full else None,
                reason='FULL_QUERY_CONTAINED' if full else 'QUERY_CROSSES_ENDPOINT_OR_GAP')


def classify(bounds):
    if bounds is None:
        return UNSUPPORTED
    if bounds[0] > bounds[1]:
        raise ValueError('Invalid difference enclosure')
    return SEPARATED if bounds[1] < 0 or bounds[0] > 0 else OVERLAP


def subtract(low, high):
    return low[0]-high[1], low[1]-high[0]


def outward(bounds, places=6):
    if bounds is None:
        return None
    scale = 10**places
    a = bounds[0]*scale
    b = bounds[1]*scale
    lower = a.numerator//a.denominator
    upper = -((-b.numerator)//b.denominator)
    def token(v):
        return ('-' if v < 0 else '')+f'{abs(v)//scale}.{abs(v)%scale:0{places}d}'
    return [token(lower), token(upper)]


def envelope(readings, ids):
    present = [t for t in ids if readings[t]['full_support']]
    missing = [t for t in ids if t not in present]
    b = [readings[t]['bounds'] for t in present]
    return dict(contributing_ids=present, missing_ids=missing, ambiguous_ids=[],
                completeness='COMPLETE' if not missing else 'INCOMPLETE',
                nominal_support=all(readings[t]['nominal_support'] for t in ids),
                full_support=not missing,
                bounds=(min(x[0] for x in b), max(x[1] for x in b)) if b else None)


def load(data=DATA):
    contract = json.loads((data/'contract.json').read_text())
    paths = json.loads((data/'paths.json').read_text())
    cal = Calibration(contract['calibration'])
    chunks = {}
    with (data/'coordinates.csv').open() as f:
        for row in csv.DictReader(f):
            chunk = chunks.setdefault(row['chunk'], [])
            if int(row['vertex']) != len(chunk):
                raise ValueError('Original vertex order changed')
            chunk.append((F(row['x_pt']), F(row['y_pt'])))
    joins = {(j['left'], j['right']): j for j in paths['joins']}
    traces = {}
    for tid, members in paths['trace_chunks'].items():
        segments = []
        for i, member in enumerate(members):
            points = chunks[member]
            segments.extend(zip(points, points[1:]))
            if i:
                left = members[i-1]
                # No connector unless source membership and bounded join were recorded.
                if (left, member) in joins:
                    a, b = chunks[left][-1], points[0]
                    if max(abs(a[k]-b[k]) for k in [0, 1]) > F(str(joins[left, member]['bound_pt'])):
                        raise ValueError('Reconstruction exceeds declared bound')
                    segments.append((a, b))
        support = union((min(a[0], b[0]), max(a[0], b[0])) for a, b in segments)
        traces[tid] = dict(segments=segments, support_x=support)
    return contract, paths, cal, traces


def analyze(data=DATA):
    contract, paths, cal, traces = load(data)
    c = contract['calibration']
    tick_residuals = {
        'time_ticks_pt': [F(v)-cal.x(t) for t, v in zip([20,40,60,80], c['x_ticks'])],
        'Y_ticks_pt': [F(v)-(F(c['y_0'])-F(n, 5)*(F(c['y_0'])-F(c['y_1'])))
                       for n, v in enumerate(c['y_ticks'])]}
    if max(abs(x) for xs in tick_residuals.values() for x in xs) > F(c['tick_residual_limit_pt']):
        raise ValueError('Axis tick calibration residual exceeds frozen check')
    trace_support = {tid: {kind: cal.time_support(t['support_x'], full)
                           for kind, full in [('nominal', False), ('full_contract', True)]}
                     for tid, t in traces.items()}
    supports, pairs, envelopes, readings = [], [], [], []
    cache = {}
    for family, interpretation in [('same-clock', 'not_applicable'),
                                   ('fixed-rescaling', 'caption'), ('fixed-rescaling', 'prose')]:
        ratio = F(1) if family == 'same-clock' else F(contract['ratios'][interpretation])
        qhigh = F(contract['flows']['high'])
        qlow = F(contract['flows'][interpretation]) if family != 'same-clock' else None
        for lid, hid in product(IDS['low'], IDS['high']):
            s = dict(family=family, interpretation=interpretation, low_id=lid, high_id=hid, ratio=ratio)
            for kind in ['nominal', 'full_contract']:
                low_s, high_s = trace_support[lid][kind], trace_support[hid][kind]
                s[kind+'_low_time_s'] = intersection(low_s, [(a/ratio,b/ratio) for a,b in high_s])
                if qlow is not None:
                    s[kind+'_mean_throughput_proxy_m3'] = intersection(
                        [(a*qlow,b*qlow) for a,b in low_s], [(a*qhigh,b*qhigh) for a,b in high_s])
            supports.append(s)
        for grid, times in contract['grids'].items():
            for time in times:
                base = dict(family=family, grid=grid, interpretation=interpretation,
                            low_flow_m3_s=qlow, high_flow_m3_s=qhigh,
                            same_clock_low_flow_interpretations=contract['flows'] if qlow is None else None,
                            ratio=ratio, low_time_s=F(time), high_time_s=ratio*time)
                rr = {}
                for condition in ['low', 'high']:
                    t = F(time) if condition == 'low' else ratio*time
                    for tid in IDS[condition]:
                        key = (tid,t)
                        if key not in cache:
                            cache[key] = read_trace(traces[tid], t, cal)
                        rr[tid] = cache[key]
                        readings.append(dict(**base, condition=condition, trace_id=tid, **rr[tid]))
                for lid, hid in product(IDS['low'], IDS['high']):
                    lo, hi = rr[lid], rr[hid]
                    d = subtract(lo['bounds'],hi['bounds']) if lo['full_support'] and hi['full_support'] else None
                    pairs.append(dict(**base,low_id=lid,high_id=hid,low_reading=lo,high_reading=hi,
                                      difference=d,display_difference=outward(d),classification=classify(d),
                                      reason='PAIR_SPECIFIC_ONLY' if d is not None else 'FULL_QUERY_UNSUPPORTED'))
                lo, hi = envelope(rr,IDS['low']), envelope(rr,IDS['high'])
                complete = lo['full_support'] and hi['full_support']
                d = subtract(lo['bounds'],hi['bounds']) if complete else None
                envelopes.append(dict(**base,low_envelope=lo,high_envelope=hi,
                                      completeness='COMPLETE' if complete else 'INCOMPLETE',
                                      difference=d,display_difference=outward(d),classification=classify(d),
                                      reason='COMPLETE_REPRESENTED_CONDITIONS' if complete else 'MISSING_FULL_SUPPORT_TRACE',
                                      display_touches_zero=d is not None and '0.000000' in outward(d),
                                      exact_contains_zero=d is not None and d[0] <= 0 <= d[1]))
    summaries=[]
    for family, interpretation in [('same-clock','not_applicable'),('fixed-rescaling','caption'),('fixed-rescaling','prose')]:
        for grid in contract['grids']:
            ee=[e for e in envelopes if (e['family'],e['interpretation'],e['grid'])==(family,interpretation,grid)]
            pp=[p for p in pairs if (p['family'],p['interpretation'],p['grid'])==(family,interpretation,grid)]
            separated=[e for e in ee if e['classification']==SEPARATED]
            complete=sum(e['completeness']=='COMPLETE' for e in ee)
            summaries.append(dict(family=family,interpretation=interpretation,grid=grid,
                                  disposition='SUPPORTED_DISCREPANCY' if separated else
                                  ('NON_EXCLUSION_BY_DECLARED_COMPARISONS' if complete else 'INSUFFICIENT_SUPPORT'),
                                  envelope_requests=len(ee),complete=complete,incomplete=len(ee)-complete,
                                  unsupported=sum(e['classification']==UNSUPPORTED for e in ee),
                                  separated=len(separated),not_excluded=sum(e['classification']==OVERLAP for e in ee),
                                  witnesses=[dict(low_time_s=e['low_time_s'],high_time_s=e['high_time_s'],difference=e['difference'],display_difference=e['display_difference']) for e in separated],
                                  pair_requests=len(pp),pair_classes={k:sum(p['classification']==k for p in pp) for k in [SEPARATED,OVERLAP,UNSUPPORTED]}))
    return dict(task=TASK,physical_validation='NOT_ESTABLISHED',target_exposure='TARGET_EXPOSED',
                classification=contract['classification'],contract_sha256=hashlib.sha256((data/'contract.json').read_bytes()).hexdigest(),
                input_hashes={n:hashlib.sha256((data/n).read_bytes()).hexdigest() for n in ['coordinates.csv','paths.json','contract.json']},
                shared_axis_treatment=contract['dependence'],arithmetic='EXACT_RATIONAL',numerical_unresolved=0,
                calibration_checks=tick_residuals,left_frame_time_s=cal.time(F('186.3758544921875')),
                trace_support=trace_support,pair_support=supports,envelopes=envelopes,pairs=pairs,
                readings=readings,summary=summaries)


def serial(value):
    if isinstance(value,F):
        return str(value)
    raise TypeError(type(value).__name__)


def csv_rows(path, rows):
    def cell(x):
        return json.dumps(x,default=serial,sort_keys=True,separators=(',',':')) if isinstance(x,(dict,list,tuple)) else x
    with path.open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for row in rows for k in row)),lineterminator='\n');w.writeheader()
        w.writerows({k:cell(v) for k,v in r.items()} for r in rows)


def produce(output=OUTPUT, plot_figure=False):
    result=analyze()
    output.mkdir(parents=True,exist_ok=True)
    # Tables contain all retained requests, including unsupported rows.
    for name in ['envelopes','pairs','readings','pair_support']:
        csv_rows(output/(name+'.csv'),result[name])
    summary={k:v for k,v in result.items() if k not in ['envelopes','pairs','readings','pair_support']}
    (output/'RESULT.json').write_text(json.dumps(summary,default=serial,indent=2,sort_keys=True)+'\n')
    if plot_figure:
        plot(result,output/'comparison.svg')
    return result


def plot(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec=VizSpec(id='corrochano_fig6_22_flow_rescaling',title='Published normalized resistance and fixed flow rescaling',
                 class_=1,producer=Producer(module='puckworks.analysis.corrochano2017_hydration_flow',function='analyze',result_map={'summary':'summary'}),
                 badge='OBSERVED',evidence_strength='reference',components=[],
                 fidelity_ceiling='Published graphical histories, shared-axis outer reading relaxation; not physical validation or authenticated instrument samples.',
                 render_fn='puckworks.analysis.corrochano2017_hydration_flow:plot',
                 caption='All six represented curves. Mean-throughput proxy uses caption means; full-contract common support retains positive lower boundary.',
                 outputs=['comparison.svg'],used_in=TASK)
    if spec.validate():
        raise ValueError(spec.validate())
    contract,paths,cal,traces=load()
    common=None
    for tid in traces:
        q=F(contract['flows']['high' if tid[0]=='H' else 'caption'])
        s=[(a*q,b*q) for a,b in result['trace_support'][tid]['full_contract']]
        common=s if common is None else intersection(common,s)
    with matplotlib.rc_context({'svg.hashsalt':'corrochano6-22','font.size':10,'path.simplify':False}):
        fig,axes=plt.subplots(1,2,figsize=(12,5.8))
        colors={'H':'#235ca5','L':'#c24732'}
        styles={'1':'-','2':'--','3':':'}
        for tid,trace in traces.items():
            q=F(contract['flows']['high' if tid[0]=='H' else 'caption'])
            # Each actual segment is retained; no interpolation across gaps.
            for panel in [0,1]:
                xs,ys=[],[]
                for a,b in trace['segments']:
                    x0,x1=cal.time(a[0]),cal.time(b[0]);y0,y1=cal.y(a[1]),cal.y(b[1])
                    if panel:
                        x0*=q;x1*=q
                        for lo,hi in common:
                            l,h=max(x0,lo),min(x1,hi)
                            if l<=h:
                                v0=y0 if x0==x1 else y0+(l-x0)*(y1-y0)/(x1-x0)
                                v1=y1 if x0==x1 else y0+(h-x0)*(y1-y0)/(x1-x0)
                                xs.extend([float(l)*1e6,float(h)*1e6,None]);ys.extend([float(v0),float(v1),None])
                    else:
                        xs.extend([float(x0),float(x1),None]);ys.extend([float(y0),float(y1),None])
                axes[panel].plot(xs,ys,color=colors[tid[0]],linestyle=styles[tid[1]],lw=.8,alpha=.85,label=tid)
        for ax in axes:
            ax.set_ylabel('Published HR / HR_max');ax.grid(alpha=.2);ax.set_ylim(-.025,1.08)
        axes[0].set_xlabel('Published time (s)');axes[0].set_title('Published clock • actual trace supports')
        axes[0].legend(ncol=3,fontsize=8,loc='lower right')
        axes[1].set_xlabel('Caption mean-throughput proxy, Q_mean × t (mL)')
        axes[1].set_title('Fixed caption ratio • complete common support')
        for lo,hi in common:
            axes[1].axvline(float(lo)*1e6,color='#555555',ls='--',lw=.8)
            axes[1].axvline(float(hi)*1e6,color='#555555',ls='--',lw=.8)
            axes[1].set_xlim(float(lo)*1e6,float(hi)*1e6)
        # Sparse predeclared envelope bars show reading completeness without smoothing.
        for e in result['envelopes']:
            if e['family']=='fixed-rescaling' and e['interpretation']=='caption' and e['grid']=='PRIMARY' and e['completeness']=='COMPLETE':
                x=float(e['low_time_s']*F(contract['flows']['caption']))*1e6
                for key in ['low_envelope','high_envelope']:
                    lo,hi=map(float,e[key]['bounds']);axes[1].plot([x]*2,[lo,hi],lw=2,color=colors['L' if key=='low_envelope' else 'H'])
        fig.suptitle('OBSERVED / reference • source-internal, target-exposed graphical comparison')
        fig.text(.5,.025,'Blue H1–H3: high flow; red L1–L3: low flow. Bars: complete outer reading envelopes.\nPositive common-support boundary retained. Proxy is not actual volume. PHYSICAL_VALIDATION=NOT_ESTABLISHED.',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.1,1,.94))
        fig.savefig(output,metadata={'Date':None,'Creator':'Puckworks Figure 6.22 factual reconstruction'})
        plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=OUTPUT)
    p.add_argument('--plot',action='store_true');a=p.parse_args();produce(a.output,a.plot)


if __name__=='__main__':
    main()

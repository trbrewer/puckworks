"""Bounded midpoint-coordinate CDF comparison; no runtime physics or physical validation.

Offline: python -m puckworks.analysis.hargarten2020_wet_psd --output OUT --plot
Acquisition and manual source reading are separate from this deterministic producer.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from itertools import product
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'puckworks/data/hargarten2020/wet_psd_001'
OUTPUT = ROOT / 'docs/analysis/sci_md_hargarten_wet_psd_001'
TASK = 'SCI-MD-HARGARTEN-WET-PSD-001'
EXCLUDED = 'UNIFORM_DILATION_EXCLUDED_BY_CDF_EXCESS'
NOT_EXCLUDED = 'UNIFORM_DILATION_NOT_EXCLUDED_BY_DECLARED_CONTRASTS'
UNRESOLVED = 'UNRESOLVED_SOURCE_OR_READING'
SCALE_EXCLUDED = 'COMMON_SCALE_EXCLUDED_BY_QUANTILE_CONSTRAINTS'
TABLES = ('marker_bounds', 'feasibility', 'cdf_readings', 'contrasts',
          'quantile_diameters', 'multiplier_intervals', 'intersections', 'witnesses', 'coverage')


def _pow10_enclosure(value):
    """Enclose 10**rational to 1e-6 using correctly-rounded Decimal ln/exp.

ln(10) and each exp are correctly rounded (nearest); one next-minus/plus
covers their rounding. Rational division and products use directed rounding;
all four products cover either sign. No platform libm result decides a sign.
"""
    v = F(value)
    with localcontext() as ctx:
        ctx.prec = 60
        log = Decimal(10).ln()
        logs = [log.next_minus(), log.next_plus()]
        ctx.rounding = ROUND_FLOOR
        t0 = Decimal(v.numerator) / Decimal(v.denominator)
        lows = [t * l for t in [t0] for l in logs]
        ctx.rounding = ROUND_CEILING
        t1 = Decimal(v.numerator) / Decimal(v.denominator)
        highs = [t * l for t in [t1] for l in logs]
        # Include cross corners also for negative t or negative interval endpoints.
        ctx.rounding = ROUND_FLOOR
        lo = min(lows + [t1 * l for l in logs]).exp().next_minus()
        ctx.rounding = ROUND_CEILING
        hi = max(highs + [t0 * l for l in logs]).exp().next_plus()
        return (F(lo.quantize(Decimal('0.000001'), rounding=ROUND_FLOOR)),
                F(hi.quantize(Decimal('0.000001'), rounding=ROUND_CEILING)))


def diameter_bounds(x, panel, nominal=False):
    """Shared-panel axis model; marginal rectangle is an outer relaxation."""
    a, b = map(F, panel['x_anchors_px'])
    va, vb = map(F, panel['x_anchor_um'])
    if panel['x_scale'] != 'log10' or (va, vb) != (10, 1000):
        raise ValueError('Only authenticated log10 10/1000 um calibration is supported')
    e = F(0) if nominal else F(panel['anchor_allowance_px'])
    r = F(0) if nominal else F(panel['reading_allowance_px'])
    if b - a <= 2 * e:
        raise ValueError('Nonpositive axis scale')
    powers = [1 + 2 * (xx - aa) / (bb - aa)
              for xx, aa, bb in product([F(x)-r, F(x)+r], [a-e, a+e], [b-e, b+e])]
    return _pow10_enclosure(min(powers))[0], _pow10_enclosure(max(powers))[1]


def ordinate_bounds(top, bottom, panel, nominal=False):
    a, b = map(F, panel['y_anchors_px'])
    e = F(0) if nominal else F(panel['anchor_allowance_px'])
    r = F(panel['reading_allowance_px'])
    if a-b <= 2*e or F(top) > F(bottom):
        raise ValueError('Invalid ordinate calibration/endpoints')
    values = [(aa-y)/(aa-bb) for y, aa, bb in
              product([F(top)-r, F(bottom)+r], [a-e, a+e], [b-e, b+e])]
    # Intersect with the observable's [0,1], never force tail readings or renormalize.
    return max(F(0), min(values)), min(F(1), max(values))


def cdf_feasibility(points, panel, layer):
    """Construct a witness under ONE common nominal calibration, without fitting.

Only constraint endpoints enter the increasing-prefix construction. It selects a
permitted realization; it never overwrites central readings or applies isotonic fit.
No witness means affected use is unresolved, not proof all calibrations fail.
"""
    previous_x = None
    level = F(0)
    witness = []
    for p in points:
        x = F(p['x_px'])
        if previous_x is not None and x <= previous_x:
            return {'admissible': False, 'reason': 'NONINCREASING_OR_DUPLICATE_SOURCE_X', 'witness': []}
        previous_x = x
        if p[layer+'_status'] != 'SUPPORTED':
            continue
        top, bottom = ((p['y_px'], p['y_px']) if layer == 'G'
                       else (p['ci_top_px'], p['ci_bottom_px']))
        lo, hi = ordinate_bounds(top, bottom, panel, nominal=True)
        level = max(level, lo)
        if level > hi:
            return {'admissible': False, 'reason': 'NO_NOMINAL_MONOTONE_CDF_WITNESS', 'witness': []}
        witness.append({'point_id': p['point_id'], 'x_px': x, 'F': level, 'bounds': [lo, hi]})
    return {'admissible': True, 'reason': 'SHARED_NOMINAL_CALIBRATION_WITNESS' if witness
            else 'NO_SUPPORTED_READINGS', 'witness': witness}


def cutoff_enclosure(points, cutoff):
    lower = [p for p in points if p['bounds'] and p['diameter_um'][1] <= cutoff]
    upper = [p for p in points if p['bounds'] and p['diameter_um'][0] >= cutoff]
    a = max(lower, key=lambda p: p['bounds'][0]) if lower else None
    b = min(upper, key=lambda p: p['bounds'][1]) if upper else None
    return {'bounds': [a['bounds'][0], b['bounds'][1]] if a and b else None,
            'lower_anchor': a['point_id'] if a else None,
            'upper_anchor': b['point_id'] if b else None,
            'reason': 'MONOTONICITY_BRACKET' if a and b else 'MISSING_BRACKETING_ANCHOR'}


def quantile_enclosure(points, q):
    below = [p for p in points if p['bounds'] and p['bounds'][1] < q]
    above = [p for p in points if p['bounds'] and p['bounds'][0] >= q]
    a = max(below, key=lambda p: p['diameter_um'][0]) if below else None
    b = min(above, key=lambda p: p['diameter_um'][1]) if above else None
    lo, hi = a['diameter_um'][0] if a else None, b['diameter_um'][1] if b else None
    return {'bounds_um': [lo, hi], 'lower_anchor': a['point_id'] if a else None,
            'upper_anchor': b['point_id'] if b else None,
            'status': 'SUPPORTED' if lo is not None and hi is not None and 0 < lo <= hi
            else 'UNSUPPORTED_OR_ONE_SIDED', 'reason': 'STRICT_BELOW_AND_WEAK_ABOVE_BRACKET'}


def cdf_disposition(rows):
    supported = [r for r in rows if r['bounds'] is not None]
    positive = [r for r in supported if r['bounds'][0] > 0]
    return {'outcome': EXCLUDED if positive else NOT_EXCLUDED if len(supported) == len(rows)
            else UNRESOLVED, 'supported': len(supported), 'required': len(rows),
            'ambiguous_comparisons': 0,
            'positive_witness_ids': [r['id'] for r in positive],
            'B': max([F(0)] + [r['bounds'][0] for r in supported]),
            'largest_witness_id': max(positive, key=lambda r: r['bounds'][0])['id'] if positive else None}


def ratio_enclosure(dry, wet):
    if any(x is None or x <= 0 for x in dry + wet):
        return None
    if dry[0] > dry[1] or wet[0] > wet[1]:
        raise ValueError('Invalid quantile interval')
    return [wet[0]/dry[1], wet[1]/dry[0]]


def scale_intersection(rows):
    supported = [r for r in rows if r['bounds'] is not None]
    lo, hi = F(1), None
    lo_id, hi_id = 'lambda>=1', None
    for r in supported:
        if r['bounds'][0] > lo:
            lo, lo_id = r['bounds'][0], r['id']
        if hi is None or r['bounds'][1] < hi:
            hi, hi_id = r['bounds'][1], r['id']
    empty = hi is not None and lo > hi
    outcome = (SCALE_EXCLUDED if empty else UNRESOLVED if not supported
               else 'NONEMPTY_OUTER_CANDIDATE_RANGE' if len(supported) == len(rows)
               else 'PARTIAL_OUTER_CANDIDATE_RANGE')
    return {'outcome': outcome, 'bounds': [lo, hi] if supported else None,
            'supported': len(supported), 'required': len(rows),
            'lower_operand': lo_id, 'upper_operand': hi_id,
            'separation': lo-hi if empty else None, 'necessary_only': True}


def _display_bounds(bounds, factor=1):
    if bounds is None:
        return None
    with localcontext() as ctx:
        ctx.prec = 60
        result = []
        for v, mode in zip(bounds, [ROUND_FLOOR, ROUND_CEILING]):
            if v is None:
                result.append(None)
            else:
                v = F(v)*factor
                ctx.rounding = mode
                d = Decimal(v.numerator)/Decimal(v.denominator)
                result.append(str(d.quantize(Decimal('0.000001'), rounding=mode)))
        return result


def analyze(input_dir=INPUT):
    input_dir = Path(input_dir)
    c = json.loads((input_dir/'contract.json').read_text())
    raw = list(csv.DictReader((input_dir/'coordinates.csv').open()))
    by_series = {s['id']: [p for p in raw if p['series_id'] == s['id']] for s in c['series']}
    if len(raw) != sum(map(len, by_series.values())) or len({p['point_id'] for p in raw}) != len(raw):
        raise ValueError('Unknown series or duplicated point IDs')
    result = {t: [] for t in TABLES}
    result.update(task=TASK, interpretation=c['observable'],
                  physical_cutoff_mapping=c['physical_cutoff_mapping'],
                  PHYSICAL_VALIDATION='NOT_ESTABLISHED', uncertainty=c['layers'], conditions=[])
    for layer in ['G', 'P']:
        markers, feasible, readings, quantiles = {}, {}, {}, {}
        for s in c['series']:
            sid, panel = s['id'], c['panels'][s['panel']]
            feasibility = cdf_feasibility(by_series[sid], panel, layer)
            feasible[sid] = feasibility['admissible']
            result['feasibility'].append(dict(series_id=sid, layer=layer, panel=s['panel'], **feasibility))
            markers[sid] = []
            for p in by_series[sid]:
                supported = p[layer+'_status'] == 'SUPPORTED' and feasible[sid]
                top, bottom = ((p['y_px'], p['y_px']) if layer == 'G'
                               else (p['ci_top_px'], p['ci_bottom_px']))
                bounds = list(ordinate_bounds(top, bottom, panel)) if supported else None
                row = dict(point_id=p['point_id'], series_id=sid, panel=s['panel'], layer=layer,
                           diameter_um=list(diameter_bounds(p['x_px'], panel)), bounds=bounds,
                           reason='GRAPHICAL_OUTER_ENCLOSURE' if supported else
                           'CDF_FEASIBILITY_UNRESOLVED' if not feasible[sid] else p['reason'])
                markers[sid].append(row)
                result['marker_bounds'].append(row)
            if s['fraction'] == 'non_sieved':
                for d in c['cutoffs_um']:
                    row = dict(id=f'{layer}:{sid}:{d}', series_id=sid, layer=layer,
                               cutoff_um=d, **cutoff_enclosure(markers[sid], d))
                    row['display_fraction'] = _display_bounds(row['bounds'])
                    row['status'] = 'SUPPORTED' if row['bounds'] else UNRESOLVED
                    readings[sid, d] = row
                    result['cdf_readings'].append(row)
            else:
                for q in c['quantiles']:
                    row = dict(id=f'{layer}:{sid}:q{q}', series_id=sid, layer=layer,
                               q=q, **quantile_enclosure(markers[sid], F(q)))
                    quantiles[sid, q] = row
                    row['display_um'] = _display_bounds(row['bounds_um'])
                    result['quantile_diameters'].append(row)
        for d in c['cutoffs_um']:
            for a,b in [('wet25','dry'),('wet90','dry'),('wet90','wet25')]:
                wet, dry = readings['non_sieved_'+a,d], readings['non_sieved_'+b,d]
                bounds = [wet['bounds'][0]-dry['bounds'][1], wet['bounds'][1]-dry['bounds'][0]] if wet['bounds'] and dry['bounds'] else None
                row = dict(id=f'{layer}:{a}-{b}:{d}', layer=layer, contrast=a+'-'+b,
                           cutoff_um=d, bounds=bounds, operands=[wet['id'],dry['id']],
                           display_fraction=_display_bounds(bounds), display_pp=_display_bounds(bounds,100),
                           sign='UNRESOLVED' if bounds is None else 'POSITIVE' if bounds[0] > 0
                           else 'NEGATIVE' if bounds[1] < 0 else 'ZERO_CONTAINING')
                result['contrasts'].append(row)
                if b == 'dry' and bounds and bounds[0] > 0:
                    result['witnesses'].append(dict(row, type='CDF_EXCESS', certified_excess=bounds[0],
                                                  source_operands=[wet,dry]))
        for condition in ['wet25','wet90']:
            rr = [r for r in result['contrasts'] if r['layer'] == layer and r['contrast'] == condition+'-dry']
            overall = cdf_disposition(rr)
            result['conditions'].append(dict(condition=condition,layer=layer,**overall,
                      B_pp_lower=_display_bounds([overall['B'],overall['B']],100)[0],
                      primary=cdf_disposition([r for r in rr if r['cutoff_um'] == c['primary_cutoff_um']]),
                      observation_coordinate='PLOTTED_INTERVAL_MIDPOINT; physical mapping unresolved'))
        for roast, fractions in [('medium','SML'),('light','SM')]:
            roast_rows = []
            for fraction in fractions:
                rows=[]
                for q in c['quantiles']:
                    prefix=roast+'_'+fraction
                    dry, wet=quantiles[prefix+'_dry',q],quantiles[prefix+'_wet90',q]
                    bounds=ratio_enclosure(dry['bounds_um'],wet['bounds_um'])
                    row=dict(id=f'{layer}:{prefix}:q{q}',layer=layer,roast=roast,fraction=fraction,
                             q=q,bounds=bounds,operands=[dry['id'],wet['id']],
                             status='SUPPORTED' if bounds else UNRESOLVED,
                             display_ratio=_display_bounds(bounds))
                    result['multiplier_intervals'].append(row);rows.append(row)
                roast_rows.extend(rows)
                result['intersections'].append(dict(id=layer+':'+roast+'_'+fraction,layer=layer,
                       scope='fraction',roast=roast,fraction=fraction,**scale_intersection(rows)))
            result['intersections'].append(dict(id=layer+':'+roast,layer=layer,scope='within_roast',
                       roast=roast,fraction=None,**scale_intersection(roast_rows)))
        for r in result['intersections']:
            if r['layer'] == layer:
                r['display_ratio'] = _display_bounds(r['bounds'])
                if r['outcome'] == SCALE_EXCLUDED:
                    result['witnesses'].append(dict(r,type='EMPTY_SCALE_INTERSECTION'))
        for table, key in [('marker_bounds','bounds'), ('cdf_readings','bounds'),('contrasts','bounds'),
                           ('quantile_diameters','bounds_um'),('multiplier_intervals','bounds')]:
            rows=[r for r in result[table] if r['layer']==layer]
            supported=sum(r[key] is not None and all(v is not None for v in r[key]) for r in rows)
            result['coverage'].append(dict(layer=layer,table=table,required=len(rows),supported=supported,
                                           unresolved=len(rows)-supported,retained_ambiguities=
                                           sum(p['G_status']=='UNSUPPORTED_IDENTITY' for p in raw) if table=='marker_bounds' else 0))
    return result


def _json_default(v):
    if isinstance(v,F):
        return str(v)
    raise TypeError(type(v).__name__)


def produce(output=OUTPUT, plot_figure=False, input_dir=INPUT):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    result=analyze(input_dir)
    for name in ['RESULT',*TABLES]:
        data=result if name=='RESULT' else result[name]
        (output/(name+'.json')).write_text(json.dumps(data,indent=2,default=_json_default)+'\n')
        if name!='RESULT':
            keys=list(dict.fromkeys(k for row in data for k in row))
            with (output/(name+'.csv')).open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader()
                for row in data:
                    writer.writerow({k:json.dumps(v,default=_json_default) if isinstance(v,(dict,list)) else v
                                     for k,v in row.items()})
    if plot_figure:
        plot(result,output/'comparison.svg')
    return result


def plot(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec=VizSpec(id='hargarten_wet_psd_001',title='Dry/wet plotted CDF constraints',class_=1,
         producer=Producer(module=__name__,function='analyze',result_map={'conditions':'conditions'}),
         badge='OBSERVED',evidence_strength='reference',components=[],
         fidelity_ceiling='Midpoint-coordinate graphical outer bounds; no physical validation.',
         render_fn=__name__+':plot',caption='Hargarten et al. 2020, DOI 10.1002/jsfa.10440; source-derived readings CC BY-NC. No simultaneous confidence band.',
         outputs=['comparison.svg'],used_in=TASK)
    if spec.validate():
        raise ValueError(spec.validate())
    with matplotlib.rc_context({'svg.hashsalt':TASK,'font.size':9,'path.simplify':False}):
        fig,axes=plt.subplots(1,3,figsize=(16,6))
        colors={'dry':'#373737','wet25':'#17739b','wet90':'#be4a32'}
        for condition,color in colors.items():
            pp=[p for p in result['marker_bounds'] if p['layer']=='G' and p['series_id']=='non_sieved_'+condition and p['bounds']]
            xs=[sum(map(float,p['diameter_um']))/2 for p in pp]
            ys=[sum(map(float,p['bounds']))/2 for p in pp]
            axes[0].errorbar(xs,ys,yerr=[[y-float(p['bounds'][0]) for y,p in zip(ys,pp)],
                            [float(p['bounds'][1])-y for y,p in zip(ys,pp)]],fmt='.',ms=4,color=color,label=condition)
        axes[0].set(xscale='log',xlabel='Displayed midpoint diameter (µm)',ylabel='Cumulative volume fraction',title='Figure 2: retained G readings',ylim=(-.02,1.03))
        axes[0].legend();axes[0].axvline(40,color='gray',ls=':',lw=1)
        for j,contrast in enumerate(['wet25-dry','wet90-dry','wet90-wet25']):
            for i,r in enumerate([r for r in result['contrasts'] if r['layer']=='G' and r['contrast']==contrast]):
                if r['bounds']:
                    lo,hi=[100*float(x) for x in r['bounds']]; y=i+(j-1)*.22
                    axes[1].plot([lo,hi],[y,y],color=list(colors.values())[j],lw=2,label=contrast if i==0 else None)
        for i,r in enumerate([r for r in result['contrasts'] if r['layer']=='P' and r['contrast']=='wet90-wet25']):
            if r['bounds']:
                axes[1].plot([100*float(v) for v in r['bounds']],[i+.36]*2,color='#53804a',ls='--',lw=1.5,label='P wet90-wet25' if i==2 else None)
        axes[1].set(yticks=range(6),yticklabels=['10','25','40 (primary)','50','100','250'],xlabel='Contrast (percentage points)',ylabel='Cutoff on displayed coordinate (µm)',title='Fixed-cutoff outer contrasts')
        axes[1].axvline(0,color='gray',ls=':');axes[1].legend(fontsize=8)
        gg=[r for r in result['intersections'] if r['layer']=='G']
        for i,r in enumerate(gg):
            if r['bounds'] and r['bounds'][1] is not None:
                lo,hi=map(float,r['bounds']);axes[2].plot([lo,hi],[i,i],lw=4 if r['scope']=='within_roast' else 2,color='#17739b')
            else:
                axes[2].text(1,i,'unresolved')
            if r['scope']=='fraction':
                qq=[a for a in result['multiplier_intervals'] if a['layer']=='G' and a['roast']==r['roast'] and a['fraction']==r['fraction']]
                for k,a in enumerate(qq):
                    if a['bounds']:
                        axes[2].plot(list(map(float,a['bounds'])),[i+(k-2.5)*.08]*2,color='#7e9aab',lw=.7)
        axes[2].set(yticks=range(len(gg)),yticklabels=[r['id'][2:] for r in gg],xlabel='Multiplier ratio; thick intersections impose λ ≥ 1',title='Prepared G: thin quantiles / thick candidates')
        axes[2].axvline(1,color='gray',ls=':');axes[2].invert_yaxis()
        fig.suptitle('Uniform diameter scaling and measured fine-particle distributions — OBSERVED / reference')
        pcount=next(r for r in result['coverage'] if r['layer']=='P' and r['table']=='multiplier_intervals')
        fig.text(.5,.045,f"P endpoints partly obscured: wet-minus-dry 0/12 supported; prepared ratios {pcount['supported']}/30. P is unresolved for dilation.\n"
                 'Graphical midpoint coordinates; physical-cutoff mapping unresolved. Ranges are necessary only, not joint compatibility.\n'
                 'SOURCE_INTERNAL · TARGET_EXPOSED · RESEARCH_ONLY · PHYSICAL_VALIDATION=NOT_ESTABLISHED',ha='center',fontsize=9)
        fig.tight_layout(rect=(0,.14,1,.94));fig.savefig(output,metadata={'Date':None,'Description':spec.caption});plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=OUTPUT);p.add_argument('--plot',action='store_true')
    a=p.parse_args();r=produce(a.output,a.plot)
    print(json.dumps(r['conditions'],indent=2,default=_json_default))


if __name__=='__main__':
    main()

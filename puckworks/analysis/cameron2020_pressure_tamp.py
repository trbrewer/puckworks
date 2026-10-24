"""Bounded, descriptive Cameron S2 contrasts; no model or statistical inference.

Reproduce with ``python -m puckworks.analysis.cameron2020_pressure_tamp --output DIR``.
All interval arithmetic uses exact rational representations of committed coordinates.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/cameron2020/s2/observations.json'
OUTPUT = ROOT / 'docs/analysis/sci_md_cameron_pressure_tamp_001'


def q(x):
    return Q(str(x))


def interval(values):
    values = list(values)
    return [min(values), max(values)]


def outward(values, places=2):
    """Decimal strings rounded outwards, without a binary-float rounding step."""
    scale=10**places
    low=(values[0]*scale).__floor__()
    high=(values[1]*scale).__ceil__()
    def fmt(n):
        sign='-' if n<0 else ''
        return f'{sign}{abs(n)//scale}.{abs(n)%scale:0{places}d}'
    return [fmt(low),fmt(high)]


def mapping(data, axis):
    c=data['calibration']
    ticks=c[f'{axis}_ticks']
    a,b=ticks[0],ticks[-1]
    unit='time_s' if axis=='y' else 'force_N'
    return q(a['coordinate_pt']),q(b['coordinate_pt']),q(a[unit]),q(b[unit]),q(c['tick_allowance_pt'])


def read_coordinate(data,axis,point_range):
    a,b,u,v,pad=mapping(data,axis)
    return interval(u+(r-aa)*(v-u)/(bb-aa) for r,aa,bb in product(
        map(q,point_range),[a-pad,a+pad],[b-pad,b+pad]))


def nominal_read(data,axis,coord):
    a,b,u,v,_=mapping(data,axis)
    return u+(q(coord)-a)*(v-u)/(b-a)


def scale_interval(data):
    a,b,u,v,pad=mapping(data,'y')
    return interval([(v-u)/(b-a-2*pad),(v-u)/(b-a+2*pad)])


def qualify(data):
    """Attach usable plotted units, retain source coordinates as authority."""
    for axis in ['x','y']:
        a,b,u,v,pad=mapping(data,axis)
        unit='time_s' if axis=='y' else 'force_N'
        residuals=[]
        for t in data['calibration'][f'{axis}_ticks']:
            expected=a+(q(t[unit])-u)*(b-a)/(v-u)
            residuals.append(abs(q(t['coordinate_pt'])-expected))
        residual=max(residuals)
        if residual>pad:
            raise ValueError('Tick residual exceeds declared graphical allowance')
        data['calibration'][f'{axis}_max_affine_tick_residual_pt']=float(residual)
    data['calibration']['signed_time_scale_s_per_pt']=list(map(float,scale_interval(data)))
    for o in data['observations']:
        for j,(axis,name) in enumerate([('x','force_N'),('y','time_s')]):
            o[f'plotted_{name}']=float(nominal_read(data,axis,o['nominal_xy_pt'][j]))
            o[f'plotted_{name}_bounds']=list(map(float,read_coordinate(data,axis,o['central_xy_enclosure_pt'][j])))
        bar=o['bar_y_endpoints_pt']
        if bar is not None:
            pad=q(o['bar_endpoint_allowance_pt'])
            o['displayed_time_endpoints_s']=[float(nominal_read(data,'y',bar[1])),float(nominal_read(data,'y',bar[0]))]
            o['displayed_time_extent_with_reading_bounds_s']=list(map(float,read_coordinate(data,'y',[q(bar[0])-pad,q(bar[1])+pad])))
        else:
            o['displayed_time_endpoints_s']=None
            o['displayed_time_extent_with_reading_bounds_s']=None
    groups=[]
    for f in ['F1','F2','F3','F4']:
        obs=[o for o in data['observations'] if o['force_group']==f]
        ranges=[list(map(q,o['central_xy_enclosure_pt'][0])) for o in obs]
        intersection=[max(r[0] for r in ranges),min(r[1] for r in ranges)]
        if len(obs)!=4 or intersection[0]>intersection[1]:
            raise ValueError('Common nominal force group not authenticated')
        groups.append({'force_group':f, 'observation_ids':[o['observation_id'] for o in obs],
                       'common_x_intersection_pt':list(map(float,intersection)),
                       'plotted_force_union_N':[min(o['plotted_force_N_bounds'][0] for o in obs),max(o['plotted_force_N_bounds'][1] for o in obs)],
                       'nominal_force_N':None,
                       'join_basis':'shared x cluster across all four labelled series; common reading intersection; widely separated ordered groups',
                       'actual_equal_applied_force':'NOT_ESTABLISHED'})
    data['force_groups']=groups
    return data


def specifications():
    def oid(p,g,f):
        return f'S2-P{p}-G{g}-{f}'
    specs=[]
    def add(cid,family,terms,grinds,forces,pressures):
        specs.append({'contrast_id':cid,'family':family,'terms':terms,
                      'grind_labels':grinds,'force_groups':forces,'pressure_labels_bar':pressures})
    for g in ['1.3','1.5']:
        for f in ['F1','F2','F3','F4']:
            add(f'DP-G{g}-{f}','DP',{oid(9,g,f):1,oid(6,g,f):-1},[g],[f],[9,6])
    for f in ['F1','F2','F3','F4']:
        add(f'I-{f}','I',{oid(9,'1.3',f):1,oid(6,'1.3',f):-1,
                          oid(9,'1.5',f):-1,oid(6,'1.5',f):1},['1.3','1.5'],[f],[9,6])
    for p in [6,9]:
        for g in ['1.3','1.5']:
            add(f'DF-P{p}-G{g}','DF',{oid(p,g,'F4'):1,oid(p,g,'F1'):-1},[g],['F1','F4'],[p])
    for g in ['1.3','1.5']:
        add(f'J-G{g}','J',{oid(9,g,'F4'):1,oid(6,g,'F4'):-1,
                          oid(9,g,'F1'):-1,oid(6,g,'F1'):1},[g],['F1','F4'],[9,6])
    return specs


def contrast(data,spec,layer):
    obs={o['observation_id']:o for o in data['observations']}
    terms=spec['terms']
    if sum(terms.values()) != 0:
        raise ValueError('This analysis requires zero-sum contrasts')
    row={**spec,'layer':layer,'units':'s'}
    missing=[oid for oid in terms if oid not in obs or
             (layer=='B' and obs[oid]['bar_y_endpoints_pt'] is None)]
    # The nominal central-summary contrast stays visible in B, even when extents are missing.
    nominal=None if any(oid not in obs for oid in terms) else sum(
        c*nominal_read(data,'y',obs[oid]['nominal_xy_pt'][1]) for oid,c in terms.items())
    row['nominal_central_contrast_s']=float(nominal) if nominal is not None else None
    row['missing_source_objects']=[{'observation_id':oid,'object':'displayed bar endpoints' if layer=='B' else 'central anchor'} for oid in missing]
    row['anchor_ambiguities']=[oid for oid in terms if oid in obs and
        (obs[oid]['marker_shape']=='triangle' or len({c['xy_pt'][1] for c in obs[oid]['anchor_candidates']})>1)]
    if missing:
        row.update({'bounds_s':None,'exact_bounds_s':None,'reported_bounds_s':None,
                    'sign':'UNSUPPORTED/INCOMPLETE','reason':'Required source endpoints are unrecoverable; no zero-width substitution.'})
        return row
    low=high=Q(0)
    for oid,c in terms.items():
        o=obs[oid]
        if layer=='A':
            a,b=map(q,o['central_xy_enclosure_pt'][1])
        else:
            a,b=map(q,o['bar_y_endpoints_pt'])
            pad=q(o['bar_endpoint_allowance_pt'])
            a-=pad
            b+=pad
        lo,hi=sorted([c*a,c*b])
        low+=lo
        high+=hi
    bounds=interval(y*s for y,s in product([low,high],scale_interval(data)))
    sign='POSITIVE' if bounds[0]>0 else 'NEGATIVE' if bounds[1]<0 else 'UNRESOLVED'
    row.update({'bounds_s':list(map(float,bounds)),'exact_bounds_s':list(map(str,bounds)),
                'reported_bounds_s':outward(bounds),'sign':sign,
                'reason':{'POSITIVE':'Entire supported interval > 0.', 'NEGATIVE':'Entire supported interval < 0.',
                          'UNRESOLVED':'Interval includes zero; equality/equivalence not established.'}[sign]})
    return row


def compute(data):
    rows=[contrast(data,spec,layer) for layer in ['A','B'] for spec in specifications()]
    return {'dataset_id':data['dataset_id'],'source_sha256':data['source_sha256'],
            'classification':['G1','NO_GOVERNING_PHYSICS_CHANGE','RESEARCH_ONLY','RETROSPECTIVE','TARGET_EXPOSED','SOURCE_INTERNAL','NONSCORING'],
            'PHYSICAL_VALIDATION':'NOT_ESTABLISHED',
            'layer_A':'central-summary graphical reading enclosure',
            'layer_B':'sensitivity to displayed extents, not statistical inference',
            'method':'signed coordinate sum followed by one common negative axis scale; affine offset cancels; exact rational arithmetic; outward report rounding',
            'contrasts':rows}


def figure(data,result):
    """Small bundle-local VizSpec consumer; newly drawn numerical plot only."""
    bits=['<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="850" viewBox="0 0 1120 850">',
          '<rect width="1120" height="850" fill="white"/>',
          '<style>text{font-family:Arial,sans-serif;fill:#243746;font-size:13px}.title{font-size:21px;font-weight:bold}.panel{font-size:16px;font-weight:bold}</style>']
    def text(x,y,s,cl=''):
        bits.append(f'<text x="{x}" y="{y}" class="{cl}">{escape(s)}</text>')
    def line(x1,y1,x2,y2,color='#cbd5df',width=1):
        bits.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="{width}"/>')
    def cross(x,y):
        line(x-4,y-4,x+4,y+4,'#b45309',2);line(x-4,y+4,x+4,y-4,'#b45309',2)
    def marker(x,y,p,color):
        if p==9:
            bits.append(f'<path d="M {x:.3f} {y-5:.3f} L {x-5:.3f} {y+4:.3f} L {x+5:.3f} {y+4:.3f} Z" fill="{color}"/>')
        else:
            bits.append(f'<circle cx="{x:.3f}" cy="{y:.3f}" r="4" fill="{color}"/>')
    text(35,30,'Cameron 2020 · Figure S2 · nominal pressure and tamp force','title')
    text(35,52,'16 plotted summaries; raw shots, per-point n and bar semantics unresolved. SOURCE_INTERNAL / RESEARCH_ONLY')
    colors={6:'#176d9c',9:'#9b4264'}
    text(35,76,'● 6 bar   ▲ 9 bar   |   coloured rectangles: central reading bounds   |   grey bars: displayed extents + reading allowance')
    text(35,96,'× = displayed extent unrecoverable (not zero variability). Axes retain native labels; no pressure conversion.')
    for k,g in enumerate(['1.3','1.5']):
        left=70+550*k;top=140;w=430;h=270
        fx=lambda x:left+(x-80)/240*w
        fy=lambda y:top+h-(y-25)/30*h
        text(left,top-15,f'Grind setting {g}','panel')
        for y in range(25,56,5):
            line(left,fy(y),left+w,fy(y));text(left-28,fy(y)+4,str(y))
        for x in [100,150,200,250,300]:
            text(fx(x)-12,top+h+20,str(x))
        text(left+125,top+h+42,'Plotted tamp force (N)')
        text(left,top-33,'Shot time (s)')
        for o in data['observations']:
            if o['grind_label']!=g:continue
            x=o['plotted_force_N'];y=o['plotted_time_s'];p=o['pressure_label_bar']
            ext=o['displayed_time_extent_with_reading_bounds_s']
            if ext:
                line(fx(x),fy(ext[0]),fx(x),fy(ext[1]),'#a8afb5',3)
                for e in ext:line(fx(x)-5,fy(e),fx(x)+5,fy(e),'#a8afb5',2)
            else:cross(fx(x)+12,fy(y))
            xb=o['plotted_force_N_bounds'];yb=o['plotted_time_s_bounds']
            bits.append(f'<rect x="{fx(xb[0]):.3f}" y="{fy(yb[1]):.3f}" width="{fx(xb[1])-fx(xb[0]):.3f}" height="{fy(yb[0])-fy(yb[1]):.3f}" fill="{colors[p]}" fill-opacity="0.3" stroke="{colors[p]}"/>')
            marker(fx(x),fy(y),p,colors[p])
        for group in data['force_groups']:
            x=sum(group['plotted_force_union_N'])/2
            text(fx(x)-8,top+h+61,group['force_group'])
    # Contrast panels use groups on x; B bounds displaced visually, never force interpolation.
    for k,family in enumerate(['DP','I']):
        left=70+550*k;top=535;w=430;h=220
        lo,hi=(-10,22) if family=='DP' else (-3,25)
        fy=lambda y:top+h-(y-lo)/(hi-lo)*h
        fx=lambda f:left+55+(int(f[-1:])-1)*100
        text(left,top-25,'9 − 6 bar pressure contrasts (s)' if family=='DP' else 'Pressure-by-grind interaction (s)','panel')
        for y in range((lo//5)*5,hi+1,5):
            if y<lo:continue
            line(left,fy(y),left+w,fy(y),'#596b7a' if y==0 else '#dfe5ea');text(left-28,fy(y)+4,str(y))
        for f in ['F1','F2','F3','F4']:text(fx(f)-7,top+h+22,f)
        for r in result['contrasts']:
            if r['family']!=family:continue
            f=r['force_groups'][0];layer=r['layer']
            offset=(-13 if r['grind_labels']==['1.3'] else 13) if family=='DP' else 0
            x=fx(f)+offset+(5 if layer=='B' else -5)
            color=('#9b4264' if r['grind_labels']==['1.3'] else '#176d9c') if family=='DP' else '#31574c'
            if layer=='B':color='#9aa2a9'
            if r['bounds_s'] is None:
                cross(x,top+h-5);continue
            a,b=r['bounds_s'];line(x,fy(a),x,fy(b),color,4 if layer=='B' else 2)
            for e in [a,b]:line(x-4,fy(e),x+4,fy(e),color,1)
            if layer=='A':marker(x,fy(r['nominal_central_contrast_s']),6,color)
    text(70,805,'Pressure panel: rose = grind 1.3; blue = grind 1.5. Dark = layer A; grey = layer B; × = incomplete B.')
    text(70,828,'Bounds are graphical enclosures / extent sensitivity, not confidence intervals. PHYSICAL_VALIDATION=NOT_ESTABLISHED.')
    bits.append('</svg>')
    return '\n'.join(bits)+'\n'


def write(data,out):
    out.mkdir(parents=True,exist_ok=True)
    result=compute(data)
    (out/'contrasts.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    fields=['contrast_id','family','layer','grind_labels','force_groups','pressure_labels_bar','terms','nominal_central_contrast_s','bounds_s','reported_bounds_s','sign','reason','missing_source_objects','anchor_ambiguities']
    with (out/'contrasts.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader()
        for r in result['contrasts']:
            writer.writerow({k:json.dumps(r[k],separators=(',',':')) if isinstance(r[k],(list,dict)) else r[k] for k in fields})
    fields=['observation_id','pressure_label_bar','grind_label','force_group','nominal_force_N',
            'plotted_force_N','plotted_force_N_bounds','plotted_time_s','plotted_time_s_bounds',
            'displayed_time_endpoints_s','displayed_time_extent_with_reading_bounds_s',
            'bar_recovery_status','summary_statistic','replicate_n','bar_semantics','shot_clock_origin',
            'nominal_xy_pt','central_xy_enclosure_pt','bar_y_endpoints_pt']
    with (out/'observations.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");writer.writeheader()
        for o in data['observations']:
            writer.writerow({k:json.dumps(o[k],separators=(',',':')) if isinstance(o[k],list) else o[k] for k in fields})
    table=['# Generated contrasts','', 'Produced by `python -m puckworks.analysis.cameron2020_pressure_tamp`. Bounds rounded outward to 0.01 s; nominal values are connector-referenced readings.', '',
           '| ID | Nominal (s) | A bounds (s) | A sign | B bounds (s) | B sign |','|---|---:|---|---|---|---|']
    for a,b in zip(result['contrasts'][:18],result['contrasts'][18:]):
        def fmt(r):return '['+', '.join(r['reported_bounds_s'])+']' if r['reported_bounds_s'] else 'INCOMPLETE'
        table.append(f"| {a['contrast_id']} | {a['nominal_central_contrast_s']:.2f} | {fmt(a)} | {a['sign']} | {fmt(b)} | {b['sign']} |")
    (out/'CONTRASTS.md').write_text('\n'.join(table)+'\n')
    (out/'COMPARISON.svg').write_text(figure(data,result))
    return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--observations',type=Path,default=DATA)
    ap.add_argument('--output',type=Path,default=OUTPUT)
    args=ap.parse_args()
    data=json.loads(args.observations.read_text())
    result=write(data,args.output)
    for layer in ['A','B']:
        rows=[r for r in result['contrasts'] if r['layer']==layer]
        print(layer,{s:sum(r['sign']==s for r in rows) for s in ['POSITIVE','NEGATIVE','UNRESOLVED','UNSUPPORTED/INCOMPLETE']})


if __name__=='__main__':
    main()

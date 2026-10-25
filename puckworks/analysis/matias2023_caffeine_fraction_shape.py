"""Exact one-rate representation cost for Matias Figure 3 finite-vial means.

Research-only, retrospective, target-exposed, source-internal, nonscoring.
No experimental/physical validation. Core calculation uses only the stdlib;
matplotlib is optional for --plot. PDF tools belong to source recovery only.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
import math
from pathlib import Path

DATA = Path(__file__).resolve().parents[1]/'data/matias2023'
TASK = 'SCI-MD-MATIAS-CAFFEINE-FRACTION-SHAPE-001'
CLASSIFICATION = 'G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING'
SUPPORTED = {'RECOVERED', 'COVERED_BUT_RECOVERED', 'CLIPPED_BUT_RECOVERED'}


def rational(value):
    """Reject unsupported/nonfinite inputs; never silently log-clip."""
    if value is None:
        raise ValueError('unsupported coordinate')
    try:
        return Q(str(value))
    except (ValueError, ZeroDivisionError) as exc:
        raise ValueError('finite rational required') from exc


def positive_log(value):
    """Only a secondary diagnostic interface; raw rational logs are authoritative."""
    if not math.isfinite(value) or value <= 0:
        raise ValueError('positive finite concentration required')
    return math.log10(value)


def calibrate(y, a, b, radius=Q(1, 100), offset=Q(2), scale=Q(1)):
    """Shared affine calibration and a rectangular marginal enclosure."""
    y, a, b, radius = map(rational, (y, a, b, radius))
    if radius < 0 or abs(a-b) <= 2*radius:
        raise ValueError('invalid calibration enclosure')
    def f(t, p, q):
        return offset+scale*(p-t)/(p-q)
    nominal = f(y, a, b)
    corners = [f(t, p, q) for t,p,q in product(
        (y-radius, y+radius), (a-radius, a+radius), (b-radius, b+radius))]
    return nominal, min(corners), max(corners)


def endpoint_status(coordinate, center, *, clipped=False):
    if coordinate is None:
        return 'UNSUPPORTED', 'source segment endpoint absent; no interpolation'
    if clipped:
        return 'CLIPPED_BUT_RECOVERED', 'stored geometry survives right clipping/spine occlusion'
    if abs(rational(coordinate)-rational(center)) <= 2:
        return 'COVERED_BUT_RECOVERED', 'endpoint covered by filled square plus half stroke'
    return 'RECOVERED', 'visible endpoint; stored source segment recovered directly'


def observations(geometry):
    c = geometry['calibration']
    a,b = [rational(t[1]) for t in c['y_major_segments_tokens']]
    xa,xb = [rational(c['x_major_segments_tokens'][i][0]) for i in (0,-1)]
    rho = rational(c['uniform_coordinate_radius_pt'])
    rows = []
    for s in geometry['observations']:
        i = s['fraction_index']
        row = {'fraction_id': s['fraction_id'], 'fraction_index': i, 'x': i-1,
               'nominal_start_mL': 5*(i-1), 'nominal_end_mL': 5*i,
               'displayed_endpoint_mL': 5*i, 'source_locator': f"img/experiment.pdf; Fig3; {s['source_objects']}",
               'coordinate_radius_pt': str(rho)}
        rect = s.get('marker_rectangle_tokens')
        if rect is None:
            row.update(center_status='UNSUPPORTED', center_reason='marker geometry absent')
            cy = None
        else:
            rx,ry,rw,rh = map(rational, rect)
            cx,cy = rx+rw/2, ry+rh/2
            z,lo,hi = calibrate(cy,a,b,rho)
            row.update(center_native_x=str(cx), center_native_y=str(cy),
                       z=str(z), G_lower=str(lo), G_upper=str(hi),
                       concentration_mg_L_approx=10**float(z),
                       concentration_kg_m3_approx=0.001*10**float(z),
                       center_status='CLIPPED_BUT_RECOVERED' if i==10 else 'RECOVERED',
                       center_reason='square center from complete stored rectangle; right clipping' if i==10 else 'square origin plus half width/height')
            vx,vl,vu = calibrate(cx,xa,xb,rho,offset=Q(0),scale=Q(50))
            row.update(displayed_coordinate_mL=str(vx), displayed_coordinate_lower_mL=str(vl), displayed_coordinate_upper_mL=str(vu))
        vertical = s.get('vertical_tokens')
        for label,idx in [('L',1),('U',3)]:
            val = vertical[idx] if vertical is not None else None
            status,reason = endpoint_status(val,cy if cy is not None else 0,clipped=i==10)
            row[f'{label}_status'],row[f'{label}_reason'] = status,reason
            if val is not None:
                z,lo,hi = calibrate(val,a,b,rho)
                row.update({f'{label}_native_x': vertical[0 if idx==1 else 2], f'{label}_native_y': val,
                            label: str(z), f'{label}_minus': str(lo), f'{label}_plus': str(hi),
                            f'{label}_mg_L_approx': 10**float(z)})
        h = s.get('horizontal_tokens')
        row['horizontal_status'] = 'UNSUPPORTED' if h is None else ('CLIPPED_BUT_RECOVERED' if i==10 else 'COVERED_BUT_RECOVERED')
        row['horizontal_reason'] = ('source segment absent' if h is None else
            'stored right endpoint beyond clip' if i==10 else 'segment centerline covered by marker footprint')
        row['horizontal_semantics'] = 'UNDOCUMENTED_SEMANTICS'
        if h is not None:
            for label,k in [('left',0),('right',2)]:
                z,lo,hi = calibrate(h[k],xa,xb,rho,offset=Q(0),scale=Q(50))
                row.update({f'horizontal_{label}_native_x': h[k], f'horizontal_{label}_native_y': h[k+1],
                            f'horizontal_{label}_mL': str(z), f'horizontal_{label}_lower_mL': str(lo), f'horizontal_{label}_upper_mL': str(hi)})
        rows.append(row)
    if [r['fraction_index'] for r in rows] != list(range(1,11)):
        raise ValueError('retain exactly the ten original ordered slots')
    return rows


def exact_minimax(x, intervals):
    """Finite exact strip certificate; full ORDERED Cartesian product of pairs.

    Eliminating alpha gives (a_p-2e)/d_p <= beta <= (b_p+2e)/d_p.
    Intersect these with beta<=0. All lower/upper comparisons give precisely
    the enumerated bounds. A common slope makes all intercept intervals overlap,
    proving sufficiency; each bound is necessary. No rate grid/solver authority.
    """
    x = list(map(rational,x))
    bounds = [(rational(l),rational(u)) for l,u in intervals]
    if not x or len(x)!=len(bounds) or any(l>u for l,u in bounds):
        raise ValueError('nonempty matching finite valid intervals required')
    if any(a>=b for a,b in zip(x,x[1:])):
        raise ValueError('distinct increasing coordinates required')
    pairs=[]
    for i,j in combinations(range(len(x)),2):
        pairs.append((f'{i+1},{j+1}',x[j]-x[i],bounds[j][0]-bounds[i][1],bounds[j][1]-bounds[i][0]))
    candidates=[('NONNEGATIVITY',Q(0))]
    candidates += [(f'NONINCREASING:{p}',a/2) for p,d,a,b in pairs]
    candidates += [(f'ORDERED:{p}|{r}',(a*dr-br*d)/(2*(d+dr)))
                   for p,d,a,b in pairs for r,dr,ar,br in pairs]
    epsilon=max(v for _,v in candidates)
    beta_lo=max(((a-2*epsilon)/d for p,d,a,b in pairs),default=Q(0))
    beta_hi=min([Q(0)]+[(b+2*epsilon)/d for p,d,a,b in pairs])
    assert beta_lo<=beta_hi
    beta=(beta_lo+beta_hi)/2
    alpha_lo=max(l-epsilon-beta*t for t,(l,u) in zip(x,bounds))
    alpha_hi=min(u+epsilon-beta*t for t,(l,u) in zip(x,bounds))
    assert alpha_lo<=alpha_hi
    alpha=(alpha_lo+alpha_hi)/2
    predicted=[alpha+beta*t for t in x]
    nearest=[min(u,max(l,y)) for y,(l,u) in zip(predicted,bounds)]
    delta=[y-z for y,z in zip(predicted,nearest)]
    assert beta<=0 and all(l-epsilon<=y<=u+epsilon for y,(l,u) in zip(predicted,bounds))
    assert max(map(abs,delta))==epsilon
    return {'epsilon':str(epsilon), 'pair_count':len(pairs), 'ordered_pair_pair_count':len(pairs)**2,
            'attaining_constraints':[k for k,v in candidates if v==epsilon],
            'beta_interval':list(map(str,(beta_lo,beta_hi))), 'alpha_interval_at_beta':list(map(str,(alpha_lo,alpha_hi))),
            'alpha':str(alpha),'beta':str(beta), 'predicted_log':list(map(str,predicted)),
            'nearest_log':list(map(str,nearest)), 'interval_distance':list(map(str,delta)),
            'witness_verified_exactly':True, 'certificate_value_verified_exactly':True}


def multiplicative_enclosure(epsilon, places=12):
    """Directed Decimal enclosure, not float exponentiation plus formatting.

    Decimal.ln/exp are correctly rounded (ROUND_HALF_EVEN). Adjacent representable
    numbers enclose each result. Rational division and products use directed
    rounding at precision 60. Finally quantize OUTWARDS to the displayed grid.
    """
    e=rational(epsilon)
    if e<0:
        raise ValueError('nonnegative epsilon required')
    if e==0:
        return {'M_lower':'1','M_upper':'1','ratio_lower_lower':'1','ratio_lower_upper':'1',
                'ratio_envelope_outer':['1','1'], 'M_approx':1.0}
    with localcontext() as ctx:
        ctx.prec=60
        ln10=Decimal(10).ln()
        lnlo,lnhi=ln10.next_minus(),ln10.next_plus()
        ctx.rounding=ROUND_FLOOR
        elo=Decimal(e.numerator)/Decimal(e.denominator)
        tlo=elo*lnlo
        ctx.rounding=ROUND_CEILING
        ehi=Decimal(e.numerator)/Decimal(e.denominator)
        thi=ehi*lnhi
        ml=tlo.exp().next_minus()
        mu=thi.exp().next_plus()
        ctx.rounding=ROUND_FLOOR
        rl=Decimal(1)/mu
        ctx.rounding=ROUND_CEILING
        ru=Decimal(1)/ml
        grid=Decimal(1).scaleb(-places)
        down=lambda v: format(v.quantize(grid,rounding=ROUND_FLOOR),'f')
        up=lambda v: format(v.quantize(grid,rounding=ROUND_CEILING),'f')
        return {'M_lower':down(ml),'M_upper':up(mu), 'ratio_lower_lower':down(rl),
                'ratio_lower_upper':up(ru),'ratio_envelope_outer':[down(rl),up(mu)],
                'M_approx':10**float(e)}


def finite_bin_mean(A,k,start,width=5.0):
    if A<=0 or k<0 or width<=0 or start<0 or not all(map(math.isfinite,(A,k,start,width))):
        raise ValueError('positive A/width, nonnegative k/start required')
    return A if k==0 else A*math.exp(-k*start)*(-math.expm1(-k*width))/(k*width)


def diagnostics(rows):
    result=[]
    for label,weights in [('adjacent_log_ratio',(-1,1)),('adjacent_log_curvature',(1,-2,1))]:
        for i in range(11-len(weights)):
            subset=rows[i:i+len(weights)]
            r={'kind':label,'first_fraction_id':subset[0]['fraction_id'],
               'fraction_ids':','.join(v['fraction_id'] for v in subset),
               'support_status':'SUPPORTED' if all(v['center_status'] in SUPPORTED for v in subset) else 'UNSUPPORTED',
               'enclosure':'CONSERVATIVE_RECTANGULAR_OUTER_RELAXATION'}
            if r['support_status']=='SUPPORTED':
                z=sum(w*rational(v['z']) for w,v in zip(weights,subset))
                lo=sum(w*rational(v['G_lower' if w>0 else 'G_upper']) for w,v in zip(weights,subset))
                hi=sum(w*rational(v['G_upper' if w>0 else 'G_lower']) for w,v in zip(weights,subset))
                r.update(nominal=str(z),lower=str(lo),upper=str(hi),nominal_dex_approx=float(z))
            result.append(r)
    return result


def build_report(geometry=None):
    if geometry is None:
        geometry=json.loads((DATA/'figure_geometry.json').read_text())
    rows=observations(geometry)
    layers={}
    witness_rows=[]
    for label,keys,statuskeys in [('N',('z','z'),('center_status',)),
                                  ('G',('G_lower','G_upper'),('center_status',)),
                                  ('P_outer',('L_minus','U_plus'),('L_status','U_status')),
                                  ('P_inner',('L_plus','U_minus'),('L_status','U_status'))]:
        supported=[r for r in rows if all(r[k] in SUPPORTED for k in statuskeys)]
        invalid=[r['fraction_id'] for r in supported if rational(r[keys[0]])>rational(r[keys[1]])]
        if invalid or not supported:
            layers[label]={'support_status':'INNER_UNAVAILABLE' if label=='P_inner' else 'SOURCE_SUPPORT_FAILURE',
                           'invalid_intervals':invalid,'supported_count':len(supported),'epsilon':None}
            continue
        cert=exact_minimax([r['x'] for r in supported],[(r[keys[0]],r[keys[1]]) for r in supported])
        cert.update(support_status='COMPLETE' if len(supported)==10 else 'SUBSET_LOWER_BOUND_ONLY',
                    supported_count=len(supported),fraction_ids=[r['fraction_id'] for r in supported],
                    epsilon_dex_approx=float(rational(cert['epsilon'])),
                    multiplicative=multiplicative_enclosure(cert['epsilon']))
        for r,y,n,delta in zip(supported,cert['predicted_log'],cert['nearest_log'],cert['interval_distance']):
            yy=10**float(rational(y)); nn=10**float(rational(n))
            w={'layer':label,'fraction_id':r['fraction_id'],'interval_lower_log':r[keys[0]],'interval_upper_log':r[keys[1]],
               'predicted_log':y,'predicted_mg_L_approx':yy,'nearest_permitted_log':n,
               'interval_distance_log':delta,'interval_distance_mg_L_approx':yy-nn,
               'center_residual_log':None,'center_difference_mg_L_approx':None}
            if r['center_status'] in SUPPORTED:
                w['center_residual_log']=str(rational(y)-rational(r['z']))
                w['center_difference_mg_L_approx']=yy-r['concentration_mg_L_approx']
            witness_rows.append(w)
        layers[label]=cert
    coverage={'slots':len(rows),'centers':sum(r['center_status'] in SUPPORTED for r in rows),
              'vertical_lower_endpoints':sum(r['L_status'] in SUPPORTED for r in rows),
              'vertical_upper_endpoints':sum(r['U_status'] in SUPPORTED for r in rows),
              'horizontal_segments':sum(r['horizontal_status'] in SUPPORTED for r in rows)}
    return {'task':TASK,'classification':CLASSIFICATION,'PHYSICAL_VALIDATION':'NOT_ESTABLISHED',
            'dataset_id':geometry['dataset_id'],'geometry_sha256':sha256(json.dumps(geometry,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'coverage':coverage,'calibration_checks':calibration_checks(geometry),'observations':rows,'layers':layers,'diagnostics':diagnostics(rows),
            'witness_residuals':witness_rows,
            'residual_convention':'prediction minus nominal center; interval distance = prediction minus clip(prediction,l,u)',
            'graphical_contract':'CONSERVATIVE_RECTANGULAR_OUTER_RELAXATION; favorable readings; shared calibration not necessarily jointly realizable',
            'P_quantifier':'for every admissible endpoint realization: epsilon_outer <= epsilon_realized <= epsilon_inner (if inner valid)',
            'unequal_volume_robustness':'NOT_ESTABLISHED','practical_adequacy':'UNADJUDICATED_NO_AUTHORIZED_TOLERANCE'}



def calibration_checks(geometry):
    c=geometry['calibration']; checks=[]
    a,b=[rational(v[1]) for v in c['y_major_segments_tokens']]
    xa,xb=[rational(c['x_major_segments_tokens'][i][0]) for i in (0,-1)]
    for label,t in zip(c['x_major_labels_mL'],c['x_major_segments_tokens']):
        residual=rational(t[0])-(xa+rational(label)*(xb-xa)/50)
        checks.append({'axis':'volume','tick_label':label,'coordinate_token':t[0],
                       'residual_pt_exact':str(residual),'residual_pt_approx':float(residual)})
    for labels,segments in [('y_major_labels_mg_L','y_major_segments_tokens'),('y_minor_labels_mg_L','y_minor_segments_tokens')]:
        for label,t in zip(c[labels],c[segments]):
            residual=float(rational(t[1]))-(float(a)-float(a-b)*(math.log10(label)-2))
            checks.append({'axis':'log_concentration','tick_label':label,'coordinate_token':t[1],
                           'residual_pt_exact':None,'residual_pt_approx':residual})
    if any(abs(r['residual_pt_approx'])>=.005 for r in checks):
        raise ValueError('source calibration consistency exceeds declared recovery derivation')
    return checks


def write_csv(path,rows):
    if not rows:
        return
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n')
        writer.writeheader(); writer.writerows(rows)


def result_markdown(report):
    complete = all(c.get('support_status')=='COMPLETE' for c in report['layers'].values())
    excluded = complete and all(rational(c['epsilon'])>0 for c in report['layers'].values())
    conclusion = ('One nonincreasing exponential cannot exactly represent all ten aggregate finite-vial means under the declared nominal or graphical contract. The reported-SE outer result below also remains positive.' if excluded else
                  'Consult each layer support status and exact objective below. An incomplete layer supplies only a supported-subset lower bound; no unavailable full-cohort optimum or ten-fraction compatibility is claimed.')
    lines=[f'# {TASK} — result','', conclusion,
           '',CLASSIFICATION+'. PHYSICAL_VALIDATION=NOT_ESTABLISHED.','',
           f"Coverage: {json.dumps(report['coverage'],sort_keys=True)}. All original slots retained.",
           '', '| Layer | Exact epsilon (dex) | Approx. dex | Certified M enclosure | Certified outer ratio envelope |',
           '|---|---|---:|---|---|']
    for name,c in report['layers'].items():
        if c['epsilon'] is None:
            lines.append(f"| {name} | {c['support_status']} | — | — | — |")
            continue
        m=c['multiplicative']; ratio=m['ratio_envelope_outer']
        lines.append(f"| {name} | {c['epsilon']} | {c['epsilon_dex_approx']:.9f} | [{m['M_lower']}, {m['M_upper']}] | [{ratio[0]}, {ratio[1]}] |")
    lines += ['', 'N uses exact serialized centers. G chooses favorable readings inside graphical bands; it is not worst-case error. G/P use conservative rectangular relaxations of shared calibration. Positive relaxed optima exclude the original joint contract; witnesses need not be jointly realizable figure readings.',
              '', 'P_outer and P_inner retain graphical endpoint recovery. For every admissible endpoint realization, epsilon_outer <= epsilon_realized <= epsilon_inner. A positive outer optimum excludes exact representation throughout the declared endpoint-reading contract. Outer zero alone is relaxation intersection; inner zero supplies a universal intersecting line; outer zero with inner positive is unresolved by these enclosures. SE sensitivity is descriptive; it is not a simultaneous confidence region, statistical rejection, equivalence test or independent replication.',
              '', '## Operator and certificate', '',
              'For c(V)=A exp(-kV), A>0, k>=0 and w=5 mL, the bin integral divided by w is B q^(i−1), q=exp(−kw), B=A(1−q)/(kw). At k=0, q=1 and B=A. Thus zhat=alpha+beta(i−1), beta<=0, in dimensionless log10(c/(1 mg/L)). Any common coordinate offset is absorbed by alpha. x=i−1 is fixed; horizontal segments do not set spacing.',
              '', 'Eliminating alpha gives (a_p−2epsilon)/d_p <= beta <= (b_p+2epsilon)/d_p. Their intersection with beta<=0 is nonempty exactly when epsilon is at least 0, every a_p/2 and every ordered (a_p*d_r−b_r*d_p)/(2(d_p+d_r)). All 45 pairs and 2,025 ordered terms are evaluated. A feasible slope makes the intercept intervals intersect, proving sufficiency. Midpoints choose a deterministic rational witness. Original expanded-strip inequalities and max absolute interval distance are verified exactly. Exactness concerns the declared graphical contract, not exact experimental knowledge.', '']
    for name,c in report['layers'].items():
        if c['epsilon'] is not None:
            lines += [f"- {name}: attaining lower bounds `{'; '.join(c['attaining_constraints'])}`; beta interval {c['beta_interval']}; alpha interval at chosen beta {c['alpha_interval_at_beta']}; witness (alpha,beta)=({c['alpha']},{c['beta']})."]
    diag=report['diagnostics']
    lines += ['', '## Shape and residual diagnostics','',
              'All nine adjacent log ratios and all eight adjacent log curvatures (with exact nominal values and conservative G enclosures) are in diagnostics.csv. They describe these same ten means, not extra experiments. Local overlap cannot replace the simultaneous certificate.', '',
              '| Diagnostic | First fraction | Nominal dex | Graphical enclosure (approx. dex) |','|---|---|---:|---|']
    for r in diag:
        if r['support_status']=='SUPPORTED':
            lines.append(f"| {r['kind']} | {r['first_fraction_id']} | {r['nominal_dex_approx']:.6f} | [{float(rational(r['lower'])):.6f}, {float(rational(r['upper'])):.6f}] |")
    lines += ['', 'witness_residuals.csv retains predicted logs and mg/L, prediction-minus-center residuals, nearest permitted readings and signed interval distances. Only the maximum absolute interval distance is the interval objective. G/P center residuals can exceed it. Native mg/L differences are secondary diagnostics. All mg/L values and ordinary display decimals are approximate; certified M and reciprocal enclosures use correctly rounded Decimal ln/exp with adjacent-number bounds, directed rational conversion/multiplication/division, then outward decimal quantization.',
              '', '## Development consequence and limits','',
              'The repository gains a reusable source-qualified Matias fraction benchmark and the exact cost of reducing this aggregate sequence to one decay rate under nominal equal collection windows. When the full-cohort outer optimum is positive, exact compression loses supported shape information even within the reported vertical-SE outer relaxation. Practical adequacy remains unadjudicated without an authorized tolerance.',
              '', 'An average of extraction-specific exponentials with different rates can curve in log coordinates. Aggregate failure does not by itself reject exponential behavior in each extraction. No mixture is fitted or established, and aggregation cannot explain an arbitrary shape by assumption. No particular mechanism, internal diffusion, failure of the complete Matias continuum model, independent validation or production adoption follows. Shape parameters are descriptive representatives, not independently calibrated physical rates. Actual unequal-volume robustness NOT_ESTABLISHED. EWP and its lock remain unchanged; no automatic successor.',
              '', 'Offline: `python -m puckworks.analysis.matias2023_caffeine_fraction_shape --output /tmp/matias-fraction-shape --plot`. See SOURCE_NOTES.md, PLAN.md and VERIFICATION.md.']
    return '\n'.join(lines)+'\n'


def plot_report(report,path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    rows=report['observations']; x=[r['nominal_end_mL'] for r in rows]
    y=[r['concentration_mg_L_approx'] for r in rows]
    fig,ax=plt.subplots(figsize=(9,6))
    ax.set_yscale('log')
    # No artificial magnification of graphical bands: wide transverse caps distinguish them.
    for xx,r in zip(x,rows):
        ax.plot([xx,xx],[r['L_mg_L_approx'],r['U_mg_L_approx']],color='#888888',lw=3,zorder=2)
        gl,gu=[10**float(rational(r[k])) for k in ('G_lower','G_upper')]
        ax.vlines(xx,gl,gu,color='#D55E00',lw=2,zorder=5)
        ax.hlines([gl,gu],xx-.55,xx+.55,color='#D55E00',lw=1,zorder=5)
    ax.plot(x,y,'ks',ms=4,label='Aggregate fraction means (n=4 extractions)',zorder=4)
    pred=report['layers']['N']['predicted_log']
    ax.plot(x,[10**float(rational(t)) for t in pred],'-o',color='#0072B2',ms=3,label='N minimax representative exponential sequence')
    handles,labels=ax.get_legend_handles_labels()
    handles += [Line2D([0],[0],color='#888888',lw=3),Line2D([0],[0],color='#D55E00',lw=2)]
    labels += ['Reported vertical SE extents','G recovery (true scale; often thinner than a pixel)']
    ax.legend(handles,labels,fontsize=9)
    ax.set(xlabel='Nominal cumulative fraction endpoint (mL)',ylabel='Finite-vial caffeine concentration (mg/L)',
           title='Matias Figure 3 · all ten nominal 5 mL fractions',xlim=(2,53))
    ax.set_xticks(x);ax.grid(alpha=.2,which='both')
    fig.text(.5,.025,'[reference] · post-fit reconstruction · SOURCE_INTERNAL · Matias et al. (2023), CC BY 4.0\n'
             'Graphical bands retain true scale; cap width is display only. SE is descriptive, not simultaneous confidence.\n'
             'Nominal equal windows; horizontal source segments omitted (semantics unresolved). PHYSICAL_VALIDATION=NOT_ESTABLISHED.',
             ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.11,1,1))
    fig.savefig(path,dpi=160,metadata={'Software':'Puckworks Matias fraction shape'})
    plt.close(fig)


def write_report(output,plot=False):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    report=build_report()
    (output/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n')
    for name,key in [('calibration_checks','calibration_checks'),('observations','observations'),('diagnostics','diagnostics'),('witness_residuals','witness_residuals')]:
        write_csv(output/f'{name}.csv',report[key])
    certificates=[]
    for name,c in report['layers'].items():
        for identity in c.get('attaining_constraints',[]):
            certificates.append({'layer':name,'constraint_id':identity,'epsilon_exact':c['epsilon'],
                                 'alpha':c['alpha'],'beta':c['beta'],
                                 'beta_lo':c['beta_interval'][0],'beta_hi':c['beta_interval'][1],
                                 'alpha_lo':c['alpha_interval_at_beta'][0],'alpha_hi':c['alpha_interval_at_beta'][1]})
    write_csv(output/'certificates.csv',certificates)
    (output/'RESULT.md').write_text(result_markdown(report))
    for name in ('PLAN.md','SOURCE_NOTES.md','VIZ_SPEC.json'):
        source=DATA/name
        if source.exists() and source.resolve()!=(output/name).resolve():
            (output/name).write_bytes(source.read_bytes())
    if plot:
        plot_report(report,output/'comparison.png')
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--plot',action='store_true')
    args=p.parse_args();r=write_report(args.output,args.plot)
    print(json.dumps({'coverage':r['coverage'],'epsilon_dex':{k:v['epsilon'] for k,v in r['layers'].items()}},sort_keys=True))


if __name__=='__main__':
    main()

"""Mo Figure 14/16 displayed-segment analysis; no physical model or PDF dependency.

Offline: python -m puckworks.analysis.mo2023_wet_ct_profiles --output DIR --plot
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/mo2023'
BUNDLE = ROOT / 'docs/analysis/sci_md_mo_wet_ct_profiles_001'
LOWER = (12., 14.)
UPPER = (17., 19.)
LATE = (19., 21.)
RADII = (0.92, 2.77, 4.61, 6.45, 8.30, 10.14)
ARITHMETIC_GUARD = 1e-7


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def deterministic_dot(left, right):
    """Fixed scalar products and compensated sum; no CPU-specific BLAS reduction."""
    return math.fsum(float(a)*float(b) for a,b in zip(left,right,strict=True))


@dataclass
class Curve:
    """One original, continuous increasing subpath. No sorting or bridging."""
    x: np.ndarray
    z: np.ndarray

    def __post_init__(self):
        self.x = np.asarray(self.x, dtype=float)
        self.z = np.asarray(self.z, dtype=float)
        if len(self.x) < 2 or len(self.x) != len(self.z) or not np.all(np.diff(self.x) > 0):
            raise ValueError('Curve must preserve a single-valued increasing source subpath')
        if not np.all(np.isfinite(self.x)) or not np.all(np.isfinite(self.z)):
            raise ValueError('Nonfinite source coordinate')

    def range(self, lo, hi):
        """Exact PL extrema: endpoints plus every enclosed original vertex."""
        if lo < self.x[0] or hi > self.x[-1] or lo > hi:
            raise ValueError('Range outside continuous source support')
        ends = np.interp([lo, hi], self.x, self.z)
        inside = self.z[np.searchsorted(self.x, lo, side='left'):
                        np.searchsorted(self.x, hi, side='right')]
        return (min(float(ends.min()), float(inside.min()) if len(inside) else float('inf')),
                max(float(ends.max()), float(inside.max()) if len(inside) else -float('inf')))


def integral_weights(x, lo, hi):
    """Analytical linear-segment integration, including partial boundary segments."""
    x = np.asarray(x, dtype=float)
    if lo < x[0] or hi > x[-1] or lo > hi or not np.all(np.diff(x) > 0):
        raise ValueError('Incomplete or non-single-valued integration support')
    dx = np.diff(x)
    left = np.maximum(x[:-1], lo)
    right = np.minimum(x[1:], hi)
    keep = right > left
    # Product form avoids subtracting two large squares at short partial segments.
    t0 = (left[keep]-x[:-1][keep])/dx[keep]
    t1 = (right[keep]-x[:-1][keep])/dx[keep]
    upper = (right[keep]-left[keep])*(t0+t1)/2
    lower = (right[keep]-left[keep])-upper
    weights = np.zeros(len(x))
    idx = np.flatnonzero(keep)
    np.add.at(weights, idx, lower)
    np.add.at(weights, idx+1, upper)
    return weights


def band_terms(terms):
    """Combine shared spatial support before interval/local-box relaxation."""
    edges = sorted({float(t) for _,band in terms for t in band})
    out = []
    for lo,hi in zip(edges,edges[1:]):
        density = sum(c/(v-u) for c,(u,v) in terms if u <= lo and hi <= v)
        if density:
            out.append((density*(hi-lo), (lo,hi)))
    return out


def inverse(cal, y, a=None, b=None):
    a = cal['x12'] if a is None else a
    b = cal['x22'] if b is None else b
    return a+(b-a)*(np.asarray(y)-12)/10


def source_coefficients(curve, cal, terms):
    weights = np.zeros(len(curve.x))
    alpha = 10/(cal['x22']-cal['x12'])
    for c,(u,v) in band_terms(terms):
        lo,hi = inverse(cal,[u,v])
        weights += c*alpha/(v-u)*integral_weights(curve.x,lo,hi)
    return weights


def nominal_contrast(curve, cal, terms):
    # Sum coefficients before the local box; a common ordinate delta is absent.
    if abs(sum(c for c,_ in terms)) > 1e-12:
        raise ValueError('Contrast coefficients must sum to zero')
    weights = source_coefficients(curve,cal,terms)
    return float(cal['gamma']*deterministic_dot(weights,curve.z))


def local_box_radius(weights, heights):
    return deterministic_dot(np.abs(weights), np.broadcast_to(heights, np.shape(weights)))


def inverse_union(cal, band, allowance):
    aa = [cal['x12']-allowance,cal['x12']+allowance]
    bb = [cal['x22']-allowance,cal['x22']+allowance]
    corners = [float(inverse(cal,y,a,b)) for a,b,y in itertools.product(aa,bb,band)]
    return min(corners),max(corners)


def support(parts, info, panel, bands, qualified):
    """All calibrations/local coordinates must remain in authenticated display."""
    cal = panel['calibration']
    h = info['local_allowance_pt'] if qualified else 0.
    q = cal['anchor_allowance_pt'] if qualified else 0.
    clip = info['effective_clip_pdf_pt']
    mask = panel['opaque_mask_pdf_pt']
    reasons = []
    for band in bands:
        lo,hi = inverse_union(cal,band,q)
        # Small outward arithmetic pad, distinct from the declared graphical box.
        lo -= h + (1e-10 if qualified else 0.)
        hi += h + (1e-10 if qualified else 0.)
        candidates = [p for p in parts if p.x[0] <= lo and hi <= p.x[-1]]
        if len(candidates) != 1:
            reasons.append(f'{list(band)}: SOURCE_SUBPATH_GAP_OR_NOT_SINGLE_VALUED')
        for part in parts:
            pl,ph=max(lo,part.x[0]),min(hi,part.x[-1])
            if pl > ph:
                continue
            zlo,zhi = part.range(pl,ph)
            if pl < clip[0] or ph > clip[2] or -zhi-h < clip[1] or -zlo+h > clip[3]:
                reasons.append(f'{list(band)}: AXIS_CLIPPED')
            ml,mh = max(pl,mask[0]),min(ph,mask[2])
            if ml <= mh:
                zl,zh = part.range(ml,mh)
                if -zh-h <= mask[3] and -zl+h >= mask[1]:
                    reasons.append(f'{list(band)}: LEGEND_OCCLUDED')
    if reasons:
        return False, '; '.join(dict.fromkeys(reasons)), None
    return True, 'complete displayed support', None


def membership_support(alternatives, predicate):
    """An incomplete finite alternative prevents complete qualification."""
    if not alternatives:
        return False, 'UNAUTHENTICATED'
    return (all(predicate(a) for a in alternatives),
            'AUTHENTICATED' if len(alternatives)==1 else 'FINITE_ALTERNATIVES_ENCLOSED')


def enclosing_integral(curve, cal, band, abox, bbox, h, cells):
    """Full y-cell interval enclosure over a CONTINUOUS calibration rectangle.

    x(y,a,b) is multilinear, so corners bound each cell. The PL range includes
    every internal vertex. Cell ranges enclose the integral, not just samples.
    """
    ys = np.linspace(band[0],band[1],cells+1)
    vals = np.array([inverse(cal,ys,a,b) for a,b in itertools.product(abox,bbox)])
    lows = np.minimum(vals[:,:-1].min(axis=0),vals[:,1:].min(axis=0))-h-1e-10
    highs = np.maximum(vals[:,:-1].max(axis=0),vals[:,1:].max(axis=0))+h+1e-10
    ranges = np.array([curve.range(lo,hi) for lo,hi in zip(lows,highs)])
    return ranges.mean(axis=0)  # every cell has equal FULL physical y width


def certified_contrast(curve, cal, terms, h, parameter_cells=4, integration_cells=256):
    terms = band_terms(terms)
    if not terms:
        return 0.,0.
    q = cal['anchor_allowance_pt']
    aa = np.linspace(cal['x12']-q,cal['x12']+q,parameter_cells+1)
    bb = np.linspace(cal['x22']-q,cal['x22']+q,parameter_cells+1)
    lower,upper = float('inf'),-float('inf')
    # Enclose all moving interpolation coefficients: nonnegative and unit-sum
    # within a band, after common support terms cancel. No nominal-weight shortcut.
    vertical_radius = h*sum(abs(c) for c,_ in terms)
    for ai,bi in itertools.product(range(parameter_cells),repeat=2):
        low=high=0.
        for c,band in terms:
            l,u = enclosing_integral(curve,cal,band,aa[ai:ai+2],bb[bi:bi+2],h,integration_cells)
            low += min(c*l,c*u)
            high += max(c*l,c*u)
        lower=min(lower,low-vertical_radius)
        upper=max(upper,high+vertical_radius)
    dz = cal['z04']-cal['z0']
    if dz <= 2*q:
        raise ValueError('Nonpositive admissible ordinate scale')
    gammas = (.4/(dz+2*q),.4/(dz-2*q))
    products = [v*g for v,g in itertools.product((lower,upper),gammas)]
    return (float(np.nextafter(min(products)-ARITHMETIC_GUARD,-np.inf)),
            float(np.nextafter(max(products)+ARITHMETIC_GUARD,np.inf)))


def classify(lower, upper, family, qualified=True):
    if not qualified:
        return 'NUMERICALLY_UNRESOLVED','ORDERING_WITHHELD_NUMERICS'
    if lower is None or upper is None:
        return 'UNSUPPORTED','ORDERING_WITHHELD_MISSING_DISPLAY_SUPPORT'
    if lower > 0:
        return 'POSITIVE', ('CONTRAST_INCREASED' if family=='delta' else 'LOWER_INTERIOR_HIGHER')
    if upper < 0:
        return 'NEGATIVE', ('CONTRAST_DECREASED' if family=='delta' else 'UPPER_INTERIOR_HIGHER')
    return 'SIGN_UNRESOLVED','ORDERING_WITHHELD_NOT_EQUALITY'


def load(data_dir=DATA):
    meta=json.loads((data_dir/'fig14_fig16_profile_metadata.json').read_text())
    csv_path=data_dir/'fig14_fig16_segmented_profiles.csv'
    if sha256(csv_path)!=meta['canonical_csv_sha256']:
        raise ValueError('Canonical profile identity mismatch')
    rows=list(csv.DictReader(csv_path.open()))
    grouped={pid:[] for pid in meta['profiles']}
    for r in rows:
        grouped[r['profile_id']].append(r)
    curves={}
    for pid,rr in grouped.items():
        parts=[]
        for sub, sr in itertools.groupby(rr,key=lambda r:r['subpath_id']):
            sr=list(sr);x=[float(sr[0]['pdf_x0'])];z=[-float(sr[0]['pdf_y0'])]
            for r in sr:
                if x[-1]!=float(r['pdf_x0']) or z[-1]!=-float(r['pdf_y0']):
                    raise ValueError('Source topology discontinuity inside subpath')
                x.append(float(r['pdf_x1']));z.append(-float(r['pdf_y1']))
            parts.append(Curve(x,z))
        curves[pid]=parts
    return meta,grouped,curves


def witness():
    F=Fraction
    cases=[((F(6,25),F(4,25)),(F(1,2),F(1,2))),
           ((F(1,5),F(1,5)),(F(2,5),F(3,5))),
           ((F(4,25),F(6,25)),(F(1,4),F(2,3)))]
    result=[]
    for phi,sat in cases:
        assert all(0 <= v <= 1 for v in phi+sat)
        g=tuple(p*(1-s) for p,s in zip(phi,sat))
        assert g==(F(3,25),F(2,25))
        result.append({'phi':list(map(str,phi)),'saturation':list(map(str,sat)),
                       'g':list(map(str,g)),'porosity_contrast':str(phi[0]-phi[1]),
                       'physical_ranges_verified':True})
    return result


def analyze(data_dir=DATA):
    meta,grouped,curves=load(data_dir)
    requests=[];diagnostics=[];by_id={}
    for pid,info in meta['profiles'].items():
        panel=meta['panels'][info['panel']];cal=panel['calibration'];parts=curves[pid]
        for family,upper in [('post_primary' if info['stage']=='post' else 'pre_context',UPPER)]+(
                [('post_late',LATE)] if info['stage']=='post' else []):
            bands=[LOWER,upper];terms=[(1.,LOWER),(-1.,upper)]
            nominal_ok,nominal_reason,_=support(parts,info,panel,bands,False)
            qual_ok,reason,_=support(parts,info,panel,bands,True)
            member_ok,membership=membership_support(info['alternatives'],lambda p:
                support(curves[p],meta['profiles'][p],panel,bands,True)[0])
            qual_ok=qual_ok and member_ok
            nom=None;lower_bound=upper_bound=None
            if nominal_ok:
                # The requested windows must each be in the same continuous part
                # here. Disjoint parts are never sorted/joined by this producer.
                part=next(p for p in parts if p.x[0]<=inverse(cal,12.) and p.x[-1]>=inverse(cal,upper[1]))
                nom=nominal_contrast(part,cal,terms)
            if qual_ok:
                enclosures=[]
                for alt in info['alternatives']:
                    ai=meta['profiles'][alt]
                    part=next(p for p in curves[alt] if p.x[0]<=inverse(cal,12.) and p.x[-1]>=inverse(cal,upper[1]))
                    enclosures.append(certified_contrast(part,cal,terms,ai['local_allowance_pt']))
                lower_bound=min(p[0] for p in enclosures);upper_bound=max(p[1] for p in enclosures)
            sign,interpretation=classify(lower_bound,upper_bound,family)
            req={'request_id':f'{family}_{pid}','family':family,'panel':info['panel'],
                 'history':info['history'],'radius_mm':info['radius_mm'],
                 'operand_ids':[pid], 'bands_mm':[list(b) for b in bands],
                 'nominal_estimate':nom,'qualified_lower':lower_bound,'qualified_upper':upper_bound,
                 'nominal_support':nominal_ok,'nominal_support_reason':nominal_reason,
                 'support_status':'COMPLETE' if qual_ok else 'INCOMPLETE', 'support_reason':reason,
                 'membership_status':membership,'numerical_qualification':'QUALIFIED' if qual_ok else 'NOT_EVALUATED_SOURCE_SUPPORT',
                 'sign':sign,'scientific_interpretation':interpretation,
                 'claim_scope':'displayed signal only; no geometric porosity or mechanism identification'}
            requests.append(req);by_id[req['request_id']]=req
        for band in [LOWER,UPPER]+([LATE] if info['stage']=='post' else []):
            ok,reason,_=support(parts,info,panel,[band],False)
            value=None
            if ok:
                lo,hi=inverse(cal,band)
                part=next(p for p in parts if p.x[0]<=lo and hi<=p.x[-1])
                value=float(cal['delta']+cal['gamma']*cal['alpha']/(band[1]-band[0])*deterministic_dot(
                    integral_weights(part.x,lo,hi),part.z))
            diagnostics.append({'profile_id':pid,'band_mm':list(band),'nominal_mean':value,
                                'support':ok,'reason':reason,'role':'supporting diagnostic, not a contrast request'})
    for history,pre,post in [('medium_delayed','14a','14b'),('dark_immediate','16a','16b')]:
        for radius in RADII:
            a=by_id[f'pre_context_{pre}_r{radius:.2f}'];b=by_id[f'post_primary_{post}_r{radius:.2f}']
            ok=a['support_status']==b['support_status']=='COMPLETE'
            lo=float(np.nextafter(b['qualified_lower']-a['qualified_upper'],-np.inf)) if ok else None
            hi=float(np.nextafter(b['qualified_upper']-a['qualified_lower'],np.inf)) if ok else None
            nom=b['nominal_estimate']-a['nominal_estimate'] if a['nominal_support'] and b['nominal_support'] else None
            sign,interpretation=classify(lo,hi,'delta')
            requests.append({'request_id':f'delta_{history}_r{radius:.2f}','family':'delta',
                'panel':f'{post}-{pre}','history':history,'radius_mm':radius,'operand_ids':[b['request_id'],a['request_id']],
                'bands_mm':[list(LOWER),list(UPPER)],'nominal_estimate':nom,'qualified_lower':lo,'qualified_upper':hi,
                'nominal_support':nom is not None,'nominal_support_reason':'both primary operands' if nom is not None else 'incomplete operand',
                'support_status':'COMPLETE' if ok else 'INCOMPLETE',
                'support_reason':'complete displayed operands; no material registration' if ok else 'incomplete primary operand',
                'membership_status':'AUTHENTICATED' if all(r['membership_status']=='AUTHENTICATED' for r in [a,b]) else 'FINITE_ALTERNATIVES_ENCLOSED',
                'numerical_qualification':'QUALIFIED' if ok else 'NOT_EVALUATED_SOURCE_SUPPORT','sign':sign,
                'scientific_interpretation':interpretation,
                'claim_scope':'display-coordinate contrast difference; no measured geometric change or causal extraction effect'})
    requests.sort(key=lambda r:(['post_primary','pre_context','delta','post_late'].index(r['family']),
                                r['history'],r['radius_mm']))
    assert len(requests)==48 and len({r['request_id'] for r in requests})==48
    counts=[]
    for family,history in itertools.product(['post_primary','pre_context','delta','post_late'],['medium_delayed','dark_immediate']):
        group=[r for r in requests if r['family']==family and r['history']==history]
        c=Counter(r['sign'] for r in group)
        counts.append({'family':family,'history':history,'requests':len(group),
                       **{k:c[k] for k in ['POSITIVE','NEGATIVE','SIGN_UNRESOLVED','UNSUPPORTED','NUMERICALLY_UNRESOLVED']},
                       'complete':sum(r['support_status']=='COMPLETE' for r in group),
                       'finite_membership_ambiguity':sum(r['membership_status']=='FINITE_ALTERNATIVES_ENCLOSED' for r in group)})
    summary={'task_id':'SCI-MD-MO-WET-CT-PROFILES-001','classification':[
        'G1','NO_GOVERNING_PHYSICS_CHANGE','RESEARCH_ONLY','RETROSPECTIVE','TARGET_EXPOSED','SOURCE_INTERNAL','NONSCORING'],
        'PHYSICAL_VALIDATION':'NOT_ESTABLISHED','profiles':24,'histories':2,'requests':48,
        'segment_count':sum(len(r) for r in grouped.values()),'counts':counts,
        'overall_sign_counts':dict(Counter(r['sign'] for r in requests)),
        'unsupported':[{'id':r['request_id'],'reason':r['support_reason']} for r in requests if r['sign']=='UNSUPPORTED'],
        'witness':witness(),'input_identities':{
            'canonical_csv_sha256':sha256(data_dir/'fig14_fig16_segmented_profiles.csv'),
            'metadata_sha256':sha256(data_dir/'fig14_fig16_profile_metadata.json')},
        'all_six_primary':{history:all(r['sign']=='POSITIVE' for r in requests if r['family']=='post_primary' and r['history']==history)
                           for history in ['medium_delayed','dark_immediate']},
        'physical_identification':'geometric porosity ordering/change and mechanism NOT_IDENTIFIED',
        'enclosure':'outer graphical reading bounds, not experimental error bars; endpoints need not be jointly attainable'}
    return requests,diagnostics,summary


def outward(value, lower, places=5):
    if value is None:
        return '—'
    factor=10**places
    rounded=(np.floor(value*factor) if lower else np.ceil(value*factor))/factor
    return f'{rounded:.{places}f}'


def result_text(requests,summary):
    lines=['# Mo segmented-image spatial contrasts', '',
        'The immediate dark-roast display resolves lower-interior-higher signal at all six radii. '
        'The delayed medium-roast display does not support that all-six claim: its central '
        '0.92-mm profile has the contrary primary ordering. These are source-conditioned '
        'contrasts of the published segmented signal; **geometric porosity ordering or change '
        'is not identified, and no mechanism is established or excluded.**', '',
        'G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE / TARGET_EXPOSED / '
        'SOURCE_INTERNAL / NONSCORING. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**', '',
        '## Complete denominators', '',
        '24 annular-region profiles, four panels, six printed radii, two capsule histories; '
        '48 dependent contrast requests. These are not sample sizes or independent extractions. '
        'All rows survive below and in contrasts.csv/json. Nulls indicate unavailable evidence.', '',
        '| Family | History | Requests | Positive | Negative | Unresolved | Unsupported | Numerical unresolved |',
        '|---|---|---:|---:|---:|---:|---:|---:|']
    for c in summary['counts']:
        lines.append(f"| {c['family']} | {c['history']} | {c['requests']} | {c['POSITIVE']} | {c['NEGATIVE']} | {c['SIGN_UNRESOLVED']} | {c['UNSUPPORTED']} | {c['NUMERICALLY_UNRESOLVED']} |")
    lines += ['', 'All supported memberships are authenticated by the six source colors and legends; '
        'no finite ambiguous membership remains in this intake. The delayed central late-band '
        'request is unsupported because the [19,21]-mm window intersects the opaque legend and '
        'axis clipping. Its hidden PDF path is audit-only: no late estimate/bound is imputed. '
        'Unresolved signs are not evidence of equality.', '',
        '## Fixed estimands and full request ledger', '',
        'A = mean[12,14] − mean[17,19]; A_late = mean[12,14] − mean[19,21], in native mm. '
        'DeltaA = A_post − A_pre within each displayed capsule history/radius. Positive A/A_late '
        'means LOWER_INTERIOR_HIGHER; negative means UPPER_INTERIOR_HIGHER. Positive/negative '
        'DeltaA means CONTRAST_INCREASED/CONTRAST_DECREASED. The unrounded qualified bounds '
        'determine strict signs; displayed endpoints below are rounded outward.', '',
        '| Request | Nominal | Graphical outer enclosure | Sign |', '|---|---:|---|---|']
    for r in requests:
        nominal='—' if r['nominal_estimate'] is None else f"{r['nominal_estimate']:.6f}"
        bounds='—' if r['qualified_lower'] is None else f"[{outward(r['qualified_lower'],True)}, {outward(r['qualified_upper'],False)}]"
        lines.append(f"| {r['request_id']} | {nominal} | {bounds} | {r['sign']} |")
    lines += ['', '## What the contrasts establish', '',
        'The central delayed rise remains visible in the full-profile figure and the late-band '
        'ledger. Resolved contrary orderings defeat an all-six statement on that support. '
        'One unresolved or unsupported request leaves an all-six statement unestablished. '
        'Even six positive primary contrasts establish neither monotonicity nor whole-section '
        'coverage nor a population trend. Printed radii do not supply whole-bed volume weights.', '',
        'DeltaA compares two printed coordinate windows. Matching capsule identity and coordinates '
        'do not establish material registration or an unchanged observation operator. Roast, '
        'capsule and scan delay are confounded; immediate/dark and delayed/medium are separate '
        'histories, not a roast or drying-time experiment.', '',
        '## Source review versus graphical/numerical qualification', '',
        'The final journal article controls methods and captions. Its Figure 14 medium history '
        'is before/three days after extraction; Figure 16 dark history is before/immediately '
        'after. Final pages 12/13 and arXiv v2 pages 14/15 contain matching segment geometries '
        'within production rounding, counted once. The separate seven-page final supplement '
        'was inspected. The 1-hour and 24-hour mentions are narrative-only, not extra profiles. '
        'See [SOURCE_NOTES.md](SOURCE_NOTES.md) for identities, rights, masks and locators.', '',
        'Dry segmentation matches a reference porosity (0.17); wet segmentation manually selects '
        'a threshold between histogram peaks. Wet imaging cannot adequately distinguish liquid '
        'from solid. These observation limitations, segmentation sensitivity, repeatability and '
        'physical variability are unquantified and are not covered by graphical enclosures.', '',
        'Nominal means integrate the retained straight segments analytically with partial '
        'boundary segments and the affine Jacobian. Qualified bounds cover the entire declared '
        'panel-shared calibration set and horizontal/vertical local stroke allowances using '
        'interval integration. The fixed 4×4 parameter boxes and 256 cells per band cover '
        'continuous sets; endpoints and every enclosed PL vertex bound each cell. This is '
        'an outer relaxation, not an optimizer estimate or a jointly attainable reconstruction. '
        'No bootstrap, p-values or experimental confidence interval is used. [PLAN.md](PLAN.md) '
        'fixes decisions before computation; [VERIFICATION.md](VERIFICATION.md) separates software '
        'checks and hosted status from [REVIEW.md](REVIEW.md).', '',
        '## Constructed identification witness', '',
        'For the deliberately idealized g=phi(1−S), exact rational arithmetic verifies physical '
        'ranges 0≤phi,S≤1 and the same g_lower=3/25=0.12, g_upper=2/25=0.08 in all three cases:', '',
        '| phi (lower,upper) | S (lower,upper) | phi contrast |', '|---|---|---|',
        '| (6/25,4/25) | (1/2,1/2) | +2/25 = +0.08 |',
        '| (1/5,1/5) | (2/5,3/5) | 0 |',
        '| (4/25,6/25) | (1/4,2/3) | −2/25 = −0.08 |', '',
        'This is a constructed nonidentification witness, not a fit to Mo, scanner calibration '
        'or assertion that the plotted signal equals gas volume. Even that favorable idealization '
        'does not identify porosity ordering with unknown spatial saturation. Displayed signal '
        'contrast and difference of displayed contrasts are the only numerical targets. '
        'Geometric porosity ordering/change and identification of fines migration, erosion, '
        'swelling or consolidation are separate, unestablished claims.', '',
        '## Reproduction', '', '```sh',
        'python -m puckworks.analysis.mo2023_wet_ct_profiles --output /tmp/mo-wet-ct-replay --plot',
        'python -m pytest -q tests/test_mo2023_wet_ct_profiles.py', '```', '',
        'Offline generation reads only committed canonical CSV/JSON; no network or PDF parser. '
        'The separate extraction route is documented in SOURCE_NOTES.md. No production/default, '
        'EWP or dependency-lock changes, physical fitting, solver run or successor.']
    return '\n'.join(lines)+'\n'


def plot(output,requests,data_dir=DATA):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    meta,rows,_=load(data_dir)
    plt.rcParams.update({'font.size':9,'svg.hashsalt':'mo-wet-ct-profiles-001','font.family':'DejaVu Sans'})
    fig=plt.figure(figsize=(16,12),layout='constrained')
    gs=fig.add_gridspec(3,4,height_ratios=[1,1,1.35])
    colors=['#171077','#1748f5','#00a6c8','#25ab48','#bba300','#ee4c16']
    for idx,pid in enumerate(['14a','14b','16a','16b']):
        ax=fig.add_subplot(gs[idx//2,(idx%2)*2:(idx%2)*2+2])
        p=meta['panels'][pid];cal=p['calibration']
        for band,color in [(LOWER,'#2a9d8f'),(UPPER,'#d4a25a'),(LATE,'#b792cc')]:
            ax.axvspan(*band,color=color,alpha=.13)
        for k,radius in enumerate(RADII):
            rr=rows[f'{pid}_r{radius:.2f}'];xx=[];ss=[]
            for r in rr:
                for ta,tb,status in json.loads(r['visibility_parts']):
                    if status!='VISIBLE':
                        continue
                    ya,yb=float(r['y0_mm']),float(r['y1_mm'])
                    sa,sb=float(r['published_segmented_signal0']),float(r['published_segmented_signal1'])
                    xx.extend([ya+ta*(yb-ya),ya+tb*(yb-ya),np.nan])
                    ss.extend([sa+ta*(sb-sa),sa+tb*(sb-sa),np.nan])
            ax.plot(xx,ss,color=colors[k],lw=1.1,label=f'{radius:.2f} mm')
        rect=p['opaque_mask_pdf_pt']
        y0=cal['alpha']*rect[0]+cal['beta'];y1=cal['alpha']*rect[2]+cal['beta']
        s0=-cal['gamma']*rect[3]+cal['delta'];s1=-cal['gamma']*rect[1]+cal['delta']
        ax.add_patch(Rectangle((y0,s0),y1-y0,s1-s0,facecolor='#eeeeee',edgecolor='#aaaaaa',hatch='///',lw=.5))
        ax.text((y0+y1)/2,(s0+s1)/2,'opaque source legend',ha='center',va='center',color='#555555')
        ax.set(xlim=(10.4,22.3),ylim=(0,.405),xlabel='y (mm): bottom/outlet → top/inlet',ylabel='published_segmented_signal',
               title=f'Figure {pid} · type H {p["roast"]} · {p["timing"]}')
        if pid=='14b':
            ax.annotate('central rise: legend / axis clipped',xy=(19.75,.285),xytext=(13,.255),
                        arrowprops={'arrowstyle':'->','color':'#171077'},color='#171077',fontsize=8)
        ax.grid(alpha=.15)
    handles,labels=fig.axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside upper center',ncols=6,
               title='Mo 2023 · two capsule histories · printed annular radial labels (not independent extractions)')
    titles={'post_primary':'Primary post: A','pre_context':'Descriptive pre: A','delta':'Display difference: DeltaA','post_late':'Post sensitivity: A_late'}
    for k,family in enumerate(titles):
        ax=fig.add_subplot(gs[2,k]);rr=[r for r in requests if r['family']==family]
        for i,r in enumerate(rr):
            color={'POSITIVE':'#146e85','NEGATIVE':'#b73737','SIGN_UNRESOLVED':'#777777','UNSUPPORTED':'#333333'}[r['sign']]
            if r['qualified_lower'] is None:
                ax.text(.02,i,'× unsupported',transform=ax.get_yaxis_transform(),va='center',fontsize=8)
            else:
                ax.plot([r['qualified_lower'],r['qualified_upper']],[i,i],color=color,lw=2)
                ax.plot(r['nominal_estimate'],i,'o',color=color,ms=3)
        ax.axvline(0,color='black',lw=.7)
        ax.axhline(5.5,color='#bbbbbb',lw=.6)
        ax.set_yticks(range(len(rr)),[f'{"D/immediate" if r["history"]=="dark_immediate" else "M/3 days"} {r["radius_mm"]:.2f}' for r in rr],fontsize=8)
        ax.invert_yaxis();ax.set_title(titles[family]);ax.set_xlabel('signal contrast (dimensionless)');ax.grid(axis='x',alpha=.15)
    fig.supxlabel('Dots: nominal segment integrals. Lines: conservative graphical outer bounds, NOT experimental error bars.\n'
                  'Fixed bands: lower [12,14], primary upper [17,19], late [19,21] mm. '
                  'PHYSICAL_VALIDATION=NOT_ESTABLISHED.',fontsize=9)
    fig.savefig(output/'COMPARISON.svg',metadata={'Date':None,'Creator':'Puckworks mo2023_wet_ct_profiles'})
    svg_path=output/'COMPARISON.svg'
    svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines())+'\n')
    fig.savefig(output/'COMPARISON.png',dpi=130,metadata={'Software':'Puckworks mo2023_wet_ct_profiles'})
    plt.close(fig)


def generate(output, make_plot=False, data_dir=DATA):
    output.mkdir(parents=True,exist_ok=True)
    requests,diagnostics,summary=analyze(data_dir)
    json_write(output/'contrasts.json',requests)
    json_write(output/'band_means.json',diagnostics)
    json_write(output/'summary.json',summary)
    with (output/'contrasts.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(requests[0]),lineterminator='\n');w.writeheader()
        for r in requests:
            w.writerow({k:json.dumps(v,separators=(',',':')) if isinstance(v,(list,dict)) else v for k,v in r.items()})
    (output/'RESULT.md').write_text(result_text(requests,summary))
    if make_plot:
        plot(output,requests,data_dir)
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,default=BUNDLE)
    p.add_argument('--plot',action='store_true')
    args=p.parse_args()
    print(json.dumps(generate(args.output,args.plot)['overall_sign_counts'],sort_keys=True))

"""Independent review checks; does not import the producer or its extraction code.

Run with the task's separate PDF environment. Source PDFs remain external.
"""
from collections import Counter
import argparse
import csv
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import subprocess

import numpy as np
import pymupdf

ROOT = Path(__file__).resolve().parents[3]
BUNDLE = Path(__file__).resolve().parent
DATA = ROOT / 'puckworks/data/mo2023'
BASE = '13c750c7d08d1fc868e24ad500dced5fb34127e4'
LD = np.longdouble


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exact_mean(segments, cal, band):
    a, b = F(cal['x12']), F(cal['x22'])
    lo, hi = [a + (b-a)*F(y-12)/10 for y in band]
    integral = F(0)
    covered = F(0)
    for x0, z0, x1, z1 in segments:
        x0, z0, x1, z1 = map(F, (x0, z0, x1, z1))
        l, r = max(lo, x0), min(hi, x1)
        if r <= l:
            continue
        fl = z0 + (z1-z0)*(l-x0)/(x1-x0)
        fr = z0 + (z1-z0)*(r-x0)/(x1-x0)
        integral += (r-l)*(fl+fr)/2
        covered += r-l
    assert covered == hi-lo
    gamma = F(2, 5)/(F(cal['z04'])-F(cal['z0']))
    return gamma * (integral/(hi-lo)-F(cal['z0']))


def linear_range(x, z, lo, hi):
    """Vector cell ranges in extended precision, including every enclosed vertex."""
    assert np.min(lo) >= x[0] and np.max(hi) <= x[-1]
    ends = []
    for query in (lo, hi):
        j = np.clip(np.searchsorted(x, query, side='right')-1, 0, len(x)-2)
        ends.append(z[j]+(z[j+1]-z[j])*(query-x[j])/(x[j+1]-x[j]))
    inside = (x[None, :] >= lo[:, None]) & (x[None, :] <= hi[:, None])
    lower = np.minimum(np.minimum(*ends), np.min(np.where(inside, z, np.inf), axis=1))
    upper = np.maximum(np.maximum(*ends), np.max(np.where(inside, z, -np.inf), axis=1))
    return lower, upper


def independent_bounds(segments, cal, band, h):
    # Qualified profiles have a continuous original subpath covering both windows.
    x = np.array([segments[0][0]]+[s[2] for s in segments], dtype=LD)
    z = np.array([segments[0][1]]+[s[3] for s in segments], dtype=LD)
    a, b, q, h = map(LD, (cal['x12'], cal['x22'], cal['anchor_allowance_pt'], h))
    boxes_a = a-q + np.arange(5, dtype=LD)*q/2
    boxes_b = b-q + np.arange(5, dtype=LD)*q/2
    results = []
    for i, j in itertools.product(range(4), repeat=2):
        bands = []
        for u, v in ((12, 14), tuple(band)):
            ys = LD(u)+np.arange(257, dtype=LD)*LD(v-u)/256
            # All eight corners of each (a,b,y) cell, using independent arrays.
            native = np.array([aa+(bb-aa)*(ys-12)/10 for aa, bb in
                               itertools.product(boxes_a[i:i+2], boxes_b[j:j+2])])
            lo = np.min(np.minimum(native[:, :-1], native[:, 1:]), axis=0)-h-LD('1e-10')
            hi = np.max(np.maximum(native[:, :-1], native[:, 1:]), axis=0)+h+LD('1e-10')
            l, r = linear_range(x, z, lo, hi)
            bands.append((np.sum(l, dtype=LD)/256, np.sum(r, dtype=LD)/256))
        results.append((bands[0][0]-bands[1][1]-2*h, bands[0][1]-bands[1][0]+2*h))
    span = LD(cal['z04'])-LD(cal['z0'])
    scales = ((LD(2)/5)/(span-2*q), (LD(2)/5)/(span+2*q))
    products = [g*v for g in scales for v in (min(r[0] for r in results), max(r[1] for r in results))]
    return min(products), max(products)


def check_support(segments, gaps, cal, band, clip, mask, h, q):
    a, b, h, q = map(LD, (cal['x12'], cal['x22'], h, q))
    xx = [aa+(bb-aa)*LD(y-12)/10 for aa, bb, y in
          itertools.product((a-q, a+q), (b-q, b+q), band)]
    lo, hi = min(xx)-h, max(xx)+h
    if lo < segments[0][0] or hi > segments[-1][2] or any(lo < r and hi > l for l, r in gaps):
        return False
    for x0, z0, x1, z1 in segments:
        l, r = max(lo, x0), min(hi, x1)
        if r < l:
            continue
        x0, z0, x1, z1 = map(LD, (x0, z0, x1, z1))
        pp = [-z0-(z1-z0)*(t-x0)/(x1-x0) for t in (l, r)]
        if l < clip[0] or r > clip[2] or min(pp)-h < clip[1] or max(pp)+h > clip[3]:
            return False
        ml, mr = max(l, mask[0]), min(r, mask[2])
        if ml <= mr:
            pp = [-z0-(z1-z0)*(t-x0)/(x1-x0) for t in (ml, mr)]
            if max(pp)+h >= mask[1] and min(pp)-h <= mask[3]:
                return False
    return True


def main(source_dir, receipt_output):
    meta = json.loads((DATA/'fig14_fig16_profile_metadata.json').read_text())
    rows = list(csv.DictReader((DATA/'fig14_fig16_segmented_profiles.csv').open()))
    requests = json.loads((BUNDLE/'contrasts.json').read_text())
    diagnostics = json.loads((BUNDLE/'band_means.json').read_text())
    sources = {}
    for name, info in meta['sources'].items():
        assert digest(source_dir/name) == info['sha256']
        sources[name] = pymupdf.open(source_dir/name)
    assert [len(sources[n]) for n in ('final.pdf','arxiv-v2.pdf','supplement.pdf')] == [15,18,7]
    crop_hashes = {}
    for figure, page in ((14, 11), (16, 12)):
        rendered = sources['final.pdf'][page].get_pixmap(
            matrix=pymupdf.Matrix(2, 2), clip=pymupdf.Rect(70, 45, 557, 243)).tobytes('png')
        assert rendered == (BUNDLE/f'figure{figure}_source.png').read_bytes()
        crop_hashes[str(figure)] = hashlib.sha256(rendered).hexdigest()
    paths, gaps, masks, clips = {}, {}, {}, {}
    worst_version_x = worst_version_signal = 0.
    visibility_counts = Counter()
    for panel_id, panel in meta['panels'].items():
        page = sources['final.pdf'][panel['source_page']-1]
        ds = page.get_drawings()
        ads = sources['arxiv-v2.pdf'][panel['arxiv_page']-1].get_drawings()
        axis = ds[panel['axis_path_id']]
        legend = ds[panel['legend_path_id']]
        assert legend['fill'] == (1., 1., 1.) and legend['fill_opacity'] == 1.
        mask = np.array(legend['rect'])+np.array([-1,-1,1,1])*legend['width']/2
        assert list(mask) == panel['opaque_mask_pdf_pt']
        masks[panel_id] = mask
        cal = panel['calibration']
        offset = 0 if panel_id.endswith('a') else 133
        for index, target in zip([18,21,24,27,30,33], cal['x_ticks_pt']):
            assert ds[index+offset]['items'][0][1].x == target
            assert ds[index+offset]['width'] == cal['tick_stroke_width_pt']
        for index, target in zip([41,46,51,56,61,66,71,76,81], cal['z_ticks_pt']):
            assert -ds[index+offset]['items'][0][1].y == target
            assert ds[index+offset]['width'] == cal['tick_stroke_width_pt']
        profiles = [p for p in meta['profiles'].values() if p['panel'] == panel_id]
        assert sorted(p['radius_mm'] for p in profiles) == [0.92,2.77,4.61,6.45,8.30,10.14]
        assert len({tuple(p['stroke_rgb']) for p in profiles}) == 6
        aoffset = 0 if panel_id.endswith('a') else 137
        axs = [ads[i+aoffset]['items'][0][1].x for i in (2,17)]
        azs = [-ads[i+aoffset]['items'][0][1].y for i in (25,65)]
        for pid, info in meta['profiles'].items():
            if info['panel'] != panel_id:
                continue
            path = ds[info['path_id']]
            k = sorted(p['radius_mm'] for p in profiles).index(info['radius_mm'])
            assert path['color'] == ds[95+offset+9*k]['color'] == tuple(info['stroke_rgb'])
            assert path['seqno'] < legend['seqno']
            clip = list(axis['rect'])
            active_clip = None
            for d in page.get_drawings(extended=True):
                if d['type'] == 'clip' and d['level'] == 0:
                    active_clip = list(d['scissor'])
                if d.get('seqno') == path['seqno']:
                    break
            assert active_clip is not None
            clip = [max(clip[0],active_clip[0]),max(clip[1],active_clip[1]),
                    min(clip[2],active_clip[2]),min(clip[3],active_clip[3])]
            assert clip == info['effective_clip_pdf_pt']
            clips[pid] = clip
            native, discontinuities = [], []
            previous = None
            rr = [r for r in rows if r['profile_id'] == pid]
            apath = ads[info['arxiv_path_id']]
            assert len(rr) == len(path['items']) == len(apath['items'])
            for n, (item, other, row) in enumerate(zip(path['items'], apath['items'], rr)):
                assert item[0] == other[0] == row['operator'] == 'l'
                _, start, end = item
                assert end.x > start.x
                if previous is not None and previous != start:
                    discontinuities.append([previous.x,start.x])
                previous = end
                assert int(row['subpath_id']) == len(discontinuities)
                assert [float(row[t]) for t in ('pdf_x0','pdf_y0','pdf_x1','pdf_y1')] == [start.x,start.y,end.x,end.y]
                native.append((start.x,-start.y,end.x,-end.y))
                for t0, t1, status in json.loads(row['visibility_parts']):
                    assert 0 <= t0 < t1 <= 1
                    t=(t0+t1)/2
                    xx=start.x+t*(end.x-start.x); yy=start.y+t*(end.y-start.y)
                    expected = ('AXIS_CLIPPED' if not (clip[0] <= xx <= clip[2] and clip[1] <= yy <= clip[3]) else
                                'LEGEND_OCCLUDED' if mask[0] <= xx <= mask[2] and mask[1] <= yy <= mask[3] else 'VISIBLE')
                    assert expected == status
                    visibility_counts[status] += 1
                pieces = json.loads(row['visibility_parts'])
                assert pieces[0][0] == 0 and pieces[-1][1] == 1
                assert all(a[1] == b[0] for a,b in zip(pieces,pieces[1:]))
                for point, apoint in zip((start,end), other[1:]):
                    x = 12+10*(point.x-cal['x12'])/(cal['x22']-cal['x12'])
                    y = .4*(-point.y-cal['z0'])/(cal['z04']-cal['z0'])
                    ax = 12+10*(apoint.x-axs[0])/(axs[1]-axs[0])
                    ay = .4*(-apoint.y-azs[0])/(azs[1]-azs[0])
                    worst_version_x = max(worst_version_x,abs(x-ax))
                    worst_version_signal = max(worst_version_signal,abs(y-ay))
            assert discontinuities == info['gaps_pdf_x_pt']
            paths[pid], gaps[pid] = native, discontinuities
    assert len(paths) == 24 and len(rows) == 12494
    max_nominal_error = max_mean_error = max_guard_difference = 0.
    independent = {}
    for request in requests:
        if request['family'] == 'delta':
            continue
        pid = request['operand_ids'][0]
        info = meta['profiles'][pid]; cal = meta['panels'][info['panel']]['calibration']
        good = all(check_support(paths[pid],gaps[pid],cal,b,clips[pid],masks[info['panel']],
                                 info['local_allowance_pt'],cal['anchor_allowance_pt']) for b in request['bands_mm'])
        assert good == (request['support_status'] == 'COMPLETE')
        if not good:
            assert request['request_id'] == 'post_late_14b_r0.92'
            assert request['nominal_estimate'] is request['qualified_lower'] is request['qualified_upper'] is None
            continue
        band = request['bands_mm'][1]
        nominal = float(exact_mean(paths[pid],cal,(12,14))-exact_mean(paths[pid],cal,band))
        max_nominal_error = max(max_nominal_error,abs(nominal-request['nominal_estimate']))
        # The one gapped profile is continuous throughout the qualified primary span.
        segments = paths[pid]
        if gaps[pid]:
            segments = [s for s in segments if s[2] <= gaps[pid][0][0]]
        lower, upper = independent_bounds(segments,cal,band,info['local_allowance_pt'])
        assert request['qualified_lower'] < lower <= nominal <= upper < request['qualified_upper']
        max_guard_difference = max(max_guard_difference,
            abs(float(lower-LD(request['qualified_lower']))-1e-7),
            abs(float(LD(request['qualified_upper'])-upper)-1e-7))
        independent[request['request_id']] = (nominal,lower,upper)
    for row in diagnostics:
        if row['support']:
            pid=row['profile_id']; cal=meta['panels'][meta['profiles'][pid]['panel']]['calibration']
            exact=float(exact_mean(paths[pid],cal,row['band_mm']))
            max_mean_error=max(max_mean_error,abs(exact-row['nominal_mean']))
    for request in requests:
        if request['family'] == 'delta':
            post, pre = [independent[key] for key in request['operand_ids']]
            nominal,lower,upper=post[0]-pre[0],post[1]-pre[2],post[2]-pre[1]
            assert request['qualified_lower'] < lower <= nominal <= upper < request['qualified_upper']
            assert abs(nominal-request['nominal_estimate']) < 3e-15
        if request['qualified_lower'] is not None:
            expected='POSITIVE' if request['qualified_lower']>0 else 'NEGATIVE' if request['qualified_upper']<0 else 'SIGN_UNRESOLVED'
            assert request['sign'] == expected
    assert len(requests) == len({r['request_id'] for r in requests}) == 48
    assert max_nominal_error < 3e-15 and max_mean_error < 3e-15 and max_guard_difference < 3e-14
    witness=[]
    for phi,s in [((F(6,25),F(4,25)),(F(1,2),F(1,2))),
                  ((F(1,5),F(1,5)),(F(2,5),F(3,5))),
                  ((F(4,25),F(6,25)),(F(1,4),F(2,3)))]:
        assert all(0 <= x <= 1 for x in phi+s)
        assert tuple(p*(1-v) for p,v in zip(phi,s)) == (F(3,25),F(2,25))
        witness.append(str(phi[0]-phi[1]))
    protocol='docs/PROTOCOL_kappa_t_discrimination.md'
    old=subprocess.check_output(['git','show',BASE+':'+protocol],cwd=ROOT).decode()
    current=(ROOT/protocol).read_text()
    extract=lambda text:text[text.index('## Protocol 1'):text.index('## Protocol 4')]
    assert extract(old) == extract(current)
    names=subprocess.check_output(['git','diff','--name-only',BASE,'--'],cwd=ROOT).decode().splitlines()
    names+=subprocess.check_output(['git','ls-files','--others','--exclude-standard'],cwd=ROOT).decode().splitlines()
    names=sorted(set(n for n in names if Path(n).name not in {'REVIEW.md','independent_review_receipt.json','VERIFICATION.md'}))
    minimum_dx = min(s[2]-s[0] for segments in paths.values() for s in segments)
    maximum_slope = max(abs((s[3]-s[1])/(s[2]-s[0])) for segments in paths.values() for s in segments)
    assert minimum_dx > .117 and maximum_slope < 24.601
    notes = (BUNDLE/'SOURCE_NOTES.md').read_text()
    assert 'dx >0.117' in notes and 'dx>0.117' in notes and '0.127' not in notes
    receipt={
        'task':'SCI-MD-MO-WET-CT-PROFILES-001','reviewer':'independent nonhuman review agent',
        'date':'2026-10-24',
        'base_head':BASE,
        'producer_imported':False,'source_pages':[15,18,7],
        'source_sha256':{n:digest(source_dir/n) for n in sources},
        'fresh_source_crop_sha256':crop_hashes,
        'minimum_segment_dx_pt':minimum_dx,
        'maximum_absolute_segment_slope':maximum_slope,
        'profiles':len(paths),'segments':len(rows),'requests':len(requests),
        'visibility_piece_counts':dict(visibility_counts),
        'source_version_max_abs_x_mm':worst_version_x,
        'source_version_max_abs_signal':worst_version_signal,
        'exact_rational_nominal_max_abs_error':max_nominal_error,
        'exact_rational_mean_max_abs_error':max_mean_error,
        'extended_precision_enclosure_guard_max_abs_difference':max_guard_difference,
        'longdouble_mantissa_bits':int(np.finfo(LD).nmant),
        'independent_within_panel_enclosures':len(independent),'delta_enclosures':12,
        'sign_counts':dict(Counter(r['sign'] for r in requests)),
        'witness_porosity_contrasts':witness,
        'protocols_1_3_byte_unchanged':True,
        'reviewed_sha256':{name:digest(ROOT/name) for name in names if (ROOT/name).is_file()},
    }
    receipt_output.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in receipt.items() if k!='reviewed_sha256'},indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True,
                        help='External directory containing the three authenticated PDFs')
    parser.add_argument('--receipt-output', type=Path, required=True,
                        help='Explicit output path; use a path outside Git for replay')
    args = parser.parse_args()
    main(args.source_dir, args.receipt_output)

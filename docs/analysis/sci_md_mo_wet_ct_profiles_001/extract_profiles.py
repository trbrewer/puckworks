"""Task-local PDF extraction. Requires PyMuPDF==1.26.7; offline analysis does not."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[3]
RADII = [0.92, 2.77, 4.61, 6.45, 8.30, 10.14]
HASHES = {
    'final.pdf': '101720c58cabd32ce2852025a3d61e2b41c3f4d315f32c853f303a929542ffb8',
    'arxiv-v2.pdf': '5cb62413c80f70916f4ccf6e2a432bffdc5def0cc817e5f0e1685502720ece0c',
    'supplement.pdf': '9ba14a679900eb1f460c13ab164272d19b9ea896b88798a35a20d57f05cba464',
}
URLS = {
    'final.pdf': 'https://www.nature.com/articles/s41598-023-42380-y.pdf',
    'arxiv-v2.pdf': 'https://arxiv.org/pdf/2305.03911v2',
    'supplement.pdf': 'https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41598-023-42380-y/MediaObjects/41598_2023_42380_MOESM1_ESM.pdf',
}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_json(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def calibration(drawings, xt, zt):
    xs = [float(drawings[i]['items'][0][1].x) for i in xt]
    zs = [-float(drawings[i]['items'][0][1].y) for i in zt]
    alpha = 10 / (xs[-1] - xs[0])
    gamma = .4 / (zs[-1] - zs[0])
    return dict(x12=xs[0], x22=xs[-1], z0=zs[0], z04=zs[-1],
                alpha=alpha, beta=12-alpha*xs[0], gamma=gamma, delta=-gamma*zs[0],
                x_ticks_pt=xs, x_tick_values_mm=list(range(12, 23, 2)),
                z_ticks_pt=zs, s_tick_values=[i*.05 for i in range(9)],
                tick_stroke_width_pt=drawings[xt[0]]['width'],
                anchor_allowance_pt=drawings[xt[0]]['width']/2+.003,
                max_x_tick_residual_pt=max(abs(x-(xs[0]+i*(xs[-1]-xs[0])/5))
                                           for i,x in enumerate(xs)),
                max_z_tick_residual_pt=max(abs(z-(zs[0]+i*(zs[-1]-zs[0])/8))
                                           for i,z in enumerate(zs)))


def partition_segment(x0, p0, x1, p1, clip, legend):
    """Partition a line at rectangle boundaries, preserving source orientation."""
    cuts = {0., 1.}
    for rect in (clip, legend):
        for val in (rect[0], rect[2]):
            if x1 != x0 and 0 < (val-x0)/(x1-x0) < 1:
                cuts.add((val-x0)/(x1-x0))
        for val in (rect[1], rect[3]):
            if p1 != p0 and 0 < (val-p0)/(p1-p0) < 1:
                cuts.add((val-p0)/(p1-p0))
    pieces = []
    ss = sorted(cuts)
    for ta,tb in zip(ss,ss[1:]):
        t=(ta+tb)/2; x=x0+t*(x1-x0); p=p0+t*(p1-p0)
        inside = clip[0] <= x <= clip[2] and clip[1] <= p <= clip[3]
        opaque = legend[0] <= x <= legend[2] and legend[1] <= p <= legend[3]
        status = 'AXIS_CLIPPED' if not inside else 'LEGEND_OCCLUDED' if opaque else 'VISIBLE'
        pieces.append((ta,tb,status))
    return pieces


def extract(source_dir, data_dir, evidence_dir):
    if pymupdf.VersionBind != '1.26.7':
        raise ValueError('Reproducible route pins PyMuPDF==1.26.7')
    for name, expected in HASHES.items():
        if digest(source_dir/name) != expected:
            raise ValueError(f'{name}: different bytes require explicit content authentication')
    data_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    final=pymupdf.open(source_dir/'final.pdf')
    arxiv=pymupdf.open(source_dir/'arxiv-v2.pdf')
    meta={'dataset_id':'mo2023/fig14_fig16_segmented_profiles',
          'ordinate':'published_segmented_signal', 'native_ordinate':{'symbol':'epsilon','word':'porosity'},
          'spatial_coordinate':'y_mm; bottom/outlet to top/inlet; annular regions, not points',
          'source_coordinate':'PDF page points, x right, page_y down; z=-page_y',
          'extraction_tool':f'PyMuPDF {pymupdf.VersionBind} / MuPDF {pymupdf.VersionFitz}',
          'csv_coordinate_serialization':'full Python float repr of parsed PDF coordinates',
          'sources':{n:{'url':URLS[n],'sha256':h,'retrieval_method':'HTTPS GET; requests; 2026-10-24',
                        'version':{'final.pdf':'journal 29 September 2023',
                                   'arxiv-v2.pdf':'arXiv v2 8 October 2023',
                                   'supplement.pdf':'journal final supplementary information'}[n]}
                     for n,h in HASHES.items()},
          'chronology':{'arxiv_v1':'2023-05-06','journal':'2023-09-29','arxiv_v2':'2023-10-08'},
          'rights':{'license':'CC-BY-4.0','url':'https://creativecommons.org/licenses/by/4.0/',
                    'attribution':'Mo, Johnston, Navarini, Suggi Liverani & Ellero (2023), Scientific Reports 13, 16374, DOI 10.1038/s41598-023-42380-y',
                    'exceptions':'No separate credit-line exception in Figures 14/16 or their captions.',
                    'modifications':'Panel crops rendered at 144 dpi; canonical vector transcription, visibility masks and numerical redraw are derivatives.'},
          'reading_contract':{'anchor_extra_pt':.003,'local_extra_pt':.003,'parameter_cells_per_axis':4,
                              'integration_cells_per_band':256,'arithmetic_guard_signal':1e-7,
                              'membership':'AUTHENTICATED; unique stroke RGB matches legend; crossings retained',
                              'enclosure':'deterministic outer graphical enclosure; not experimental confidence interval'},
          'panels':{}, 'profiles':{}}
    rows=[]; comparisons=[]
    for fig,page,apage,history,timing in [(14,11,13,'medium_delayed','three days after extraction'),
                                         (16,12,14,'dark_immediate','immediately after extraction')]:
        fp=final[page]; ds=fp.get_drawings(); ads=arxiv[apage].get_drawings()
        fp.get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(70,45,557,243)).save(evidence_dir/f'figure{fig}_source.png')
        for side,offset,aoffset in [('a',0,0),('b',133,137)]:
            panel=f'{fig}{side}'
            cal=calibration(ds,[i+offset for i in [18,21,24,27,30,33]],
                            [i+offset for i in [41,46,51,56,61,66,71,76,81]])
            acal=calibration(ads,[i+aoffset for i in [2,5,8,11,14,17]],
                             [i+aoffset for i in [25,30,35,40,45,50,55,60,65]])
            legend=ds[94+offset]
            raw_legend=list(legend['rect']); border=legend['width']/2
            mask=[raw_legend[0]-border,raw_legend[1]-border,raw_legend[2]+border,raw_legend[3]+border]
            axis=list(ds[93+offset]['rect'])
            meta['panels'][panel]={'source_page':page+1,'arxiv_page':apage+1,'history':history,
              'stage':'pre' if side=='a' else 'post','timing':'before extraction' if side=='a' else timing,
              'roast':'medium' if fig==14 else 'dark','capsule_type':'H', 'calibration':cal,
              'axis_rectangle_pdf_pt':axis,'legend_rectangle_pdf_pt':raw_legend,
              'legend_border_width_pt':legend['width'],'opaque_mask_pdf_pt':mask,
              'legend_path_id':94+offset,'axis_path_id':93+offset}
            for k,r in enumerate(RADII):
                path_id=87+offset+k; apath_id=71+aoffset+k
                path=ds[path_id]; other=ads[apath_id]
                assert all(a[0]=='l' for a in path['items'])
                assert len(path['items'])==len(other['items'])
                assert all(a[0]=='l' and a[2].x>a[1].x for a in other['items'])
                assert [a[2]!=b[1] for a,b in zip(path['items'],path['items'][1:])] == [
                    a[2]!=b[1] for a,b in zip(other['items'],other['items'][1:])]
                assert path['color']==ds[95+offset+9*k]['color']
                pid=f'{panel}_r{r:.2f}'
                clip=axis[:]
                if panel=='14b' and k==0:
                    # The PDF has an additional explicit clip around this one path.
                    clip=[364.4540100097656,72.97393798828125,545.8389892578125,204.38397216796875]
                    clip=[max(clip[0],axis[0]),max(clip[1],axis[1]),min(clip[2],axis[2]),min(clip[3],axis[3])]
                info={'panel':panel,'history':history,'stage':meta['panels'][panel]['stage'],
                      'radius_mm':r,'path_id':path_id,'paint_sequence_id':path['seqno'],
                      'arxiv_path_id':apath_id,'source_page':page+1,'stroke_rgb':list(path['color']),
                      'stroke_width_pt':path['width'],'local_allowance_pt':path['width']/2+.003,
                      'effective_clip_pdf_pt':clip,'membership_status':'AUTHENTICATED',
                      'alternatives':[pid], 'segment_count':len(path['items']),
                      'hidden_coordinates':'AUDIT_ONLY; masked fractions excluded from displayed means/bounds',
                      'gaps_pdf_x_pt':[]}
                meta['profiles'][pid]=info
                maxdy=maxds=0.; subpath=0; prev=None
                for j,(item,aitem) in enumerate(zip(path['items'],other['items'])):
                    _,start,end=item; _,astart,aend=aitem
                    if prev is not None and start!=prev:
                        info['gaps_pdf_x_pt'].append([prev.x,start.x]);subpath+=1
                    prev=end
                    assert end.x>start.x, 'not single-valued increasing topology'
                    pieces=partition_segment(start.x,start.y,end.x,end.y,clip,mask)
                    y0=cal['alpha']*start.x+cal['beta'];y1=cal['alpha']*end.x+cal['beta']
                    s0=cal['gamma']*(-start.y)+cal['delta'];s1=cal['gamma']*(-end.y)+cal['delta']
                    for pt,apt in [(start,astart),(end,aend)]:
                        dy=abs(cal['alpha']*pt.x+cal['beta']-(acal['alpha']*apt.x+acal['beta']))
                        dz=abs(-cal['gamma']*pt.y+cal['delta']-(-acal['gamma']*apt.y+acal['delta']))
                        maxdy=max(maxdy,dy);maxds=max(maxds,dz)
                    rows.append(dict(profile_id=pid,panel=panel,history=history,stage=info['stage'],radius_mm=r,
                        source_page=page+1,path_id=path_id,paint_sequence_id=path['seqno'],subpath_id=subpath,
                        segment_id=j,operator='l',pdf_x0=start.x,pdf_y0=start.y,pdf_x1=end.x,pdf_y1=end.y,
                        y0_mm=y0,y1_mm=y1,published_segmented_signal0=s0,published_segmented_signal1=s1,
                        stroke_width_pt=path['width'],visibility_parts=json.dumps(pieces,separators=(',',':'))))
                info['subpath_count']=subpath+1
                comparisons.append({'profile_id':pid,'segments':len(path['items']),
                    'max_abs_y_mm_after_tick_scaling':maxdy,'max_abs_signal_after_tick_scaling':maxds,
                    'same_operators_and_topology':all(a[0]==b[0] for a,b in zip(path['items'],other['items']))})
    with (data_dir/'fig14_fig16_segmented_profiles.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n'); w.writeheader();w.writerows(rows)
    meta['canonical_csv_sha256']=digest(data_dir/'fig14_fig16_segmented_profiles.csv')
    write_json(data_dir/'fig14_fig16_profile_metadata.json',meta)
    write_json(evidence_dir/'source_geometry_comparison.json',{'sources':meta['sources'],
        'method':'Match path/segment endpoints in original order after separate per-panel tick affine scaling; do not count arXiv again.',
        'profiles':comparisons,'counted_profiles':24,'capsule_histories':2})
    print(f'Extracted {len(rows)} segments, 24 profiles; no contrasts computed by extraction.')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--data-dir',type=Path,default=ROOT/'puckworks/data/mo2023')
    p.add_argument('--evidence-dir',type=Path,default=Path(__file__).parent)
    args=p.parse_args();extract(args.source_dir,args.data_dir,args.evidence_dir)

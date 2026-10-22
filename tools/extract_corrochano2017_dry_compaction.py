#!/usr/bin/env python3
"""Optional exact-source Figure 6.2 audit; PyMuPDF 2.0, no download.

Only compact factual coordinates/provenance are written. Keep PDF/artwork external.
The ordinary offline producer never imports this extractor or opens a PDF.
"""
import argparse
import csv
from decimal import Decimal as D
import hashlib
import json
from pathlib import Path
import re

PDF_SHA = 'f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818'
RUNS = {'B1': (0, 6), 'C1': (6, 12), 'D1': (12, 18), 'E1': (18, 25),
        'B2': (25, 31), 'B3': (31, 37), 'C2': (37, 43), 'C3': (43, 49),
        'D2': (49, 56), 'D3': (56, 62), 'E2': (62, 69), 'E3': (69, 76)}
COLORS = {'0 0 1': 'B', '1 0 0': 'C', '0 1 0': 'D', '1 0 1': 'E'}
PATTERN = (r'q ([-.\d]+) 0 0 ([-.\d]+) ([-.\d]+) ([-.\d]+) cm '
           r'([^qQ]*?) q 1 0 0 1 ([-.\d]+) ([-.\d]+) cm (.*?) S Q Q')


def transform(x, y, scale, translation, local, height):
    """Compose local translation, anisotropic CTM, then PDF-to-top-left reflection."""
    sx, sy = map(D, scale)
    tx, ty = map(D, translation)
    ox, oy = map(D, local)
    return tx + sx * (ox + D(x)), D(height) - ty - sy * (oy + D(y))


def parse(match, height):
    scale = match.group(1, 2)
    translation = match.group(3, 4)
    local = match.group(6, 7)
    raw = match.group(8)
    tokens = re.findall(r'([-.\d]+) ([-.\d]+) ([ml])', raw)
    if re.sub(r'([-.\d]+) ([-.\d]+) ([ml])', '', raw).strip():
        raise ValueError('Unrecognized geometry; audit before extraction')
    vertices = [(x, y, op, *transform(x, y, scale, translation, local, height))
                for x, y, op in tokens]
    return dict(scale=scale, translation=translation, local_translation=local,
                graphics_state=match.group(5).strip(), vertices=vertices,
                raw_path_sha256=hashlib.sha256(raw.encode()).hexdigest(),
                raw_path_offset=match.start(8), raw_path_length=len(raw),
                raw_paint_offset=match.start(), raw_paint_length=len(match.group()))


def extract(pdf, output):
    import pymupdf

    if pymupdf.VersionBind != '2.0':
        raise ValueError('Reaudit API geometry before using another extractor version')
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != PDF_SHA:
        raise ValueError('Unauthenticated PDF: resolve source identity first')
    doc = pymupdf.open(pdf)
    page = doc[247]
    if len(doc) != 359 or page.xref != 2652 or page.get_contents() != [2653]:
        raise ValueError('Unexpected pagination or objects')
    height = '841.8898'
    if doc.xref_get_key(page.xref, 'MediaBox')[1] != '[0 0 595.2756 841.8898]':
        raise ValueError('Unexpected page geometry')
    stream = doc.xref_stream(2653)
    matches = list(re.finditer(PATTERN, stream.decode('latin1'), re.S))
    raw = [parse(m, height) for m in matches]
    colored = [r for r in raw if '/CS0 CS' in r['graphics_state']]
    drawings = page.get_drawings()
    selected = [(i, d) for i, d in enumerate(drawings)
                if d['color'] in [(0, 0, 1), (1, 0, 0), (0, 1, 0), (1, 0, 1)]]
    if len(raw) != 176 or len(colored) != 156 or len(selected) != 156:
        raise ValueError('Unexpected drawing accounting')
    rows, chunks, paintings = [], [], []
    for k, (r, (index, drawing)) in enumerate(zip(colored, selected)):
        points = r['vertices']
        if points[0][2] != 'm' or any(p[2] != 'l' for p in points[1:]):
            raise ValueError('Unexpected move: cannot silently bridge a gap')
        rgb = re.search(r'/CS0 CS ([01] [01] [01])', r['graphics_state'])[1]
        if tuple(map(float, rgb.split())) != drawing['color']:
            raise ValueError('Raw/API color mismatch')
        # MuPDF sometimes folds several collinear lines into a quad. Raw ml tokens
        # remain authoritative; audit API bounds plus every API line/quad point.
        xy = [(float(p[3]), float(p[4])) for p in points]
        bbox = [min(p[0] for p in xy), min(p[1] for p in xy),
                max(p[0] for p in xy), max(p[1] for p in xy)]
        discrepancy = max(abs(x-y) for x, y in zip(bbox, drawing['rect']))
        for item in drawing['items']:
            api_points = item[1:] if item[0] == 'l' else list(item[1])
            if item[0] not in ('l', 'qu'):
                raise ValueError('Unexpected API geometry')
            for p in api_points:
                discrepancy = max(discrepancy, min(max(abs(p.x-x), abs(p.y-y))
                                                   for x, y in xy))
        sx, sy = map(D, r['scale'])
        if discrepancy > .0002 or abs(drawing['width']-3*float(sx*sy)**.5) > .0002:
            raise ValueError('Composed path/stroke transform mismatch')
        original = k if k < 76 or k >= 152 else k-76
        chunk = f'C{original:02}' if k < 152 else f'L{k-152+1}'
        painting = dict(chunk=chunk, painting=k, drawing_index=index,
                        seqno=drawing['seqno'], duplicate_of=k-76 if 76 <= k < 152 else None,
                        raw_paint_offset=r['raw_paint_offset'],
                        raw_paint_length=r['raw_paint_length'],
                        raw_path_offset=r['raw_path_offset'], raw_path_length=r['raw_path_length'],
                        raw_path_sha256=r['raw_path_sha256'], transform_check_max_pt=discrepancy)
        paintings.append(painting)
        if 76 <= k < 152:
            a, b = colored[k-76], r
            if any(a[key] != b[key] for key in ['scale', 'translation', 'local_translation',
                                               'graphics_state', 'vertices', 'raw_path_sha256']):
                raise ValueError('Repeated painting is not identical')
            continue
        trace = next((t for t, (l, h) in RUNS.items() if l <= k < h), None)
        if trace and trace[0] != COLORS[rgb]:
            raise ValueError('Membership/color mismatch')
        chunks.append(dict(chunk=chunk, trace=trace, role='curve' if trace else 'legend_excluded',
                           scale=r['scale'], translation=r['translation'],
                           local_translation=r['local_translation'],
                           graphics_state=r['graphics_state'], color=rgb,
                           local_width='3', effective_width_xy_pt=[str(3*sx), str(3*sy)],
                           api_width_pt=drawing['width'], line_caps=drawing['lineCap'],
                           line_join=drawing['lineJoin'], dash=drawing['dashes'],
                           vertex_count=len(points), start=[str(p) for p in points[0][3:]],
                           end=[str(p) for p in points[-1][3:]],
                           bbox_pt=[str(min(p[3] for p in points)), str(min(p[4] for p in points)),
                                    str(max(p[3] for p in points)), str(max(p[4] for p in points))]))
        for j, (x, y, op, px, py) in enumerate(points):
            rows.append(dict(trace=trace or '', grind=trace[0] if trace else COLORS[rgb],
                             chunk=chunk, vertex=j, operation=op, raw_x=x, raw_y=y,
                             x_pt=str(px), y_pt=str(py)))
    joins=[]
    membership={t: [f'C{k:02}' for k in reversed(range(l, h))] for t, (l, h) in RUNS.items()}
    by_id={c['chunk']:c for c in chunks}
    for trace, members in membership.items():
        for a,b in zip(members,members[1:]):
            delta=[D(y)-D(x) for x,y in zip(by_id[a]['end'],by_id[b]['start'])]
            if max(map(abs,delta)) > D('.001'):
                raise ValueError('Unjustified chunk join; retain as unsupported gap')
            joins.append(dict(trace=trace,left=a,right=b,delta_pt=list(map(str,delta)),
                              treatment='bounded source-rounding connector', max_allowed_pt='0.001'))
    axes=[]
    for n in range(18):
        r=raw[n]
        axes.append({k:v for k,v in r.items() if k!='vertices'} | {
            'drawing_index':n+2,'seqno':drawings[n+2]['seqno'],
            'vertices':[[x,y,op,str(px),str(py)] for x,y,op,px,py in r['vertices']]})
    ticks=[]
    for axis, indices, values, coordinate in [('force',[2,3,4,5,6,7,8],range(0,301,50),3),
                                               ('density',range(9,17),range(300,651,50),4)]:
        positions=[raw[n]['vertices'][0][coordinate] for n in indices]
        values=list(values)
        for i,(value,pos) in enumerate(zip(values,positions)):
            pred=positions[0]+D(value-values[0])*(positions[-1]-positions[0])/D(values[-1]-values[0])
            ticks.append(dict(axis=axis,value=value,coordinate_pt=str(pos),
                              residual_pt=str(pos-pred),drawing_index=list(indices)[i]+2))
    metadata=dict(source_url='https://etheses.bham.ac.uk/7176/2/Roman-Corrochano17EngD.pdf',
                  pdf_sha256=PDF_SHA,pdf_pages=359,printed_page=223,pdf_page=248,pdf_index=247,
                  page_xref=2652,content_xrefs=[2653],page_height_pt=height,
                  decoded_content_sha256=hashlib.sha256(stream).hexdigest(),
                  coordinate_convention='page points, top-left origin; exact composition of decimal PDF operands',
                  extractor='PyMuPDF 2.0 plus raw decimal operands',
                  raw_hash_scope='path operands only; offsets in decoded content stream',
                  trace_chunks=membership,chunks=chunks,paintings=paintings,joins=joins,axes=axes,ticks=ticks,
                  curve_unique_chunks=76,curve_paintings=152,legend_strokes=4,
                  unassigned_colored_marks=[],physical_sample_ids='UNAUTHENTICATED',
                  dash_policy='Explicit continuous PDF path recovered beneath dash styling; dash spaces are not missing path data',
                  clip_pt=['174.801','216.9848','438.480','424.9118'],
                  occlusion_note='Legend lies below curves at its x range; no curve support extended by clipping or legend')
    output.mkdir(parents=True,exist_ok=True)
    with (output/'coordinates.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    (output/'paths.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pdf',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();extract(a.pdf,a.output)

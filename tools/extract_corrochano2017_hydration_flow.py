#!/usr/bin/env python3
"""Optional exact-copy Figure 6.22 vector audit (PyMuPDF 2.0); no download.

Run separately from the offline analysis. Source PDF/render/full stream stay external.
"""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

PDF_SHA = 'f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818'
# Authenticated stream runs, in chronological chunk order. Not a colour sort.
GROUPS = {'H1': [1, 0], 'L1': [4, 3, 2], 'H2': [6, 5],
          'H3': [8, 7], 'L2': [11, 10, 9], 'L3': [14, 13, 12]}


def extract(pdf, output):
    import pymupdf
    if pymupdf.VersionBind != '2.0':
        raise ValueError('Reaudit extractor identity before using another version')
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != PDF_SHA:
        raise ValueError('Source identity differs; resolve edition before extraction')
    doc = pymupdf.open(pdf)
    page = doc[288]
    if len(doc) != 359 or page.xref != 3193 or page.get_contents() != [3194]:
        raise ValueError('Unexpected source pagination/content')
    stream = doc.xref_stream(3194)
    pattern = (r'q ([-.\d]+) 0 0 ([-.\d]+) ([-.\d]+) ([-.\d]+) cm /CS0 CS '
               r'([01] [01] [01])  SCN 3 w 1 j  /GS0 gs q 1 0 0 1 '
               r'([-.\d]+) ([-.\d]+) cm (.*?) S Q Q')
    raw = list(re.finditer(pattern, stream.decode('latin1'), re.S))
    drawings = page.get_drawings()
    selected = [(i, d) for i, d in enumerate(drawings)
                if d['color'] in [(0, 0, 1), (1, 0, 0)]]
    if len(raw) != 17 or len(selected) != 17:
        raise ValueError('Unexpected coloured stroke accounting')
    rows, chunks = [], []
    for k, (match, (index, d)) in enumerate(zip(raw, selected)):
        sx, sy, tx, ty = map(float, match.group(1, 2, 3, 4))
        ox, oy = map(float, match.group(6, 7))
        points = re.findall(r'([-.\d]+) ([-.\d]+) ([ml])', match.group(8))
        if points[0][2] != 'm' or any(p[2] != 'l' for p in points[1:]):
            raise ValueError('Unexpected subpath; never bridge a move')
        if len(points) != len(d['items'])+1:
            raise ValueError('Raw stream/API path mismatch')
        actual = [d['items'][0][1]] + [item[2] for item in d['items']]
        # Check API has ALREADY transformed positions, independently from raw tokens.
        discrepancy = max(max(abs(a.x-(tx+sx*(ox+float(p[0])))),
                              abs(a.y-(page.rect.height-ty-sy*(oy+float(p[1])))))
                          for a, p in zip(actual, points))
        if discrepancy > .0002 or abs(d['width']-3*(sx*sy)**.5) > .0002:
            raise ValueError('Graphics transform/stroke audit failed')
        if any(item[0] != 'l' for item in d['items']):
            raise ValueError('Nonlinear path requires separate audit')
        if any(d['items'][j-1][2] != item[1] for j, item in enumerate(d['items']) if j):
            raise ValueError('Disconnected subpath must not be joined')
        chunk = dict(chunk=f'C{k:02}', drawing_index=index, seqno=d['seqno'],
                     raw_stream_offset=match.start(), raw_stream_length=match.end()-match.start(),
                     raw_path_sha256=hashlib.sha256(match.group(8).encode()).hexdigest(),
                     color=d['color'], width_api_pt=d['width'], local_width=3,
                     graphics_scale=[sx, sy], graphics_translation=[tx, ty],
                     local_translation=[ox, oy], effective_width_upper_pt=3*max(sx, sy),
                     transform_check_max_pt=discrepancy, subpath=0,
                     item_count=len(d['items']), start=list(actual[0]), end=list(actual[-1]),
                     role='curve' if k < 15 else 'legend_excluded')
        chunks.append(chunk)
        if k < 15:
            trace = next(t for t, members in GROUPS.items() if k in members)
            for j, a in enumerate(actual):
                rows.append(dict(trace=trace, condition='high' if trace[0]=='H' else 'low',
                                 chunk=f'C{k:02}', chunk_order=GROUPS[trace].index(k),
                                 drawing_index=index, seqno=d['seqno'], subpath=0,
                                 vertex=j, item=max(0, j-1), endpoint='start' if j==0 else 'end',
                                 x_pt=a.x, y_pt=a.y))
    joins=[]
    for trace, members in GROUPS.items():
        for left, right in zip(members, members[1:]):
            a, b = chunks[left]['end'], chunks[right]['start']
            bound=max(abs(a[0]-b[0]), abs(a[1]-b[1]))
            if bound > .001:
                raise ValueError('Join exceeds independently justified stream-rounding bound')
            joins.append(dict(trace=trace,left=f'C{left:02}',right=f'C{right:02}',
                              delta_pt=[b[0]-a[0],b[1]-a[1]], bound_pt=.002,
                              treatment='bounded straight connector; original endpoints retained'))
    axes=[]
    for i in range(3, 15):
        d=drawings[i]
        axes.append(dict(drawing_index=i,seqno=d['seqno'],width_pt=d['width'],
                         items=[[item[0],*[list(p) for p in item[1:]]]
                                for item in d['items']]))
    # Repeated frame lines are retained in axes but are not observations.
    metadata=dict(pdf_sha256=PDF_SHA,pdf_pages=359,printed_page=264,pdf_page=289,
                  page_xref=3193,content_xrefs=[3194],
                  decoded_content_sha256=hashlib.sha256(stream).hexdigest(),
                  extractor='PyMuPDF 2.0', coordinate_convention='page points; top-left origin; y downward',
                  page_height_pt=page.rect.height, chunks=chunks, joins=joins,
                  trace_chunks={t:[f'C{k:02}' for k in ks] for t,ks in GROUPS.items()},
                  axes=axes, curve_clip_pt=[186.37600708007812,104.434814453125,450.05499267578125,312.3577880859375],
                  clipping_note='Centreline differs from clip at earliest boundary by <0.0002 pt; enclosed by 0.002 pt reconstruction guard. No terminal support extension.',
                  duplicate_curve_chunks=[], duplicate_artwork='Repeated black frame/tick items retained; no identical coloured curve chunks; legend excluded',
                  physical_repetition_ids='UNAUTHENTICATED')
    output.mkdir(parents=True,exist_ok=True)
    with (output/'coordinates.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    (output/'paths.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('pdf',type=Path)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();extract(a.pdf,a.output)

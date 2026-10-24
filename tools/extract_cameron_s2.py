#!/usr/bin/env python3
"""Audit/recover Cameron S2 numerical objects from the authenticated private PDF.

Optional extraction dependency: PyMuPDF. No PDF or page image is redistributed.
Run from the repository root with PYTHONPATH=.; --output is a fresh directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from puckworks.analysis.cameron2020_pressure_tamp import qualify

SI_SHA = '37530ec8c450c6fe5b231a7d4e3b65347555454b366ed4730ec106a4fb56775f'
# These object associations were inspected against S2's direct series labels.
# Per row: pressure, grind, markers F1..F4, bar segment pairs, connector paths.
SERIES = [
    (9, '1.3', [113, 116, 119, 122], [[111,112],[114,115],[117,118],[120,121]], [102,104,105,106]),
    (6, '1.3', [125, 107, 128, 131], [[123,124],[],[126,127],[129,130]], [89,90,91]),
    (6, '1.5', [134, 140, 143, 146], [[132,133],[138,139],[141,142],[144,145]], [94,85,95]),
    (9, '1.5', [137, 108, 109, 110], [[135,136],[],[],[]], [99,100,101]),
]


def recover(pdf: Path) -> dict:
    import pymupdf

    if hashlib.sha256(pdf.read_bytes()).hexdigest() != SI_SHA:
        raise ValueError('Source hash differs: content/version comparison required')
    doc = pymupdf.open(pdf)
    if len(doc) != 8:
        raise ValueError('Expected standalone eight-page SI')
    page = doc[6]
    drawings = page.get_drawings()
    if len(drawings) != 159 or '9 bar' not in page.get_text():
        raise ValueError('Unexpected page/object structure; inspect before extraction')

    def obj(i):
        d = drawings[i]
        data = {'path_index': i, 'paint_sequence': d['seqno'],
                'bbox_pt': list(d['rect']), 'stroke_width_pt': d['width']}
        if len(d['items']) == 1 and d['items'][0][0] == 'l':
            data['line_pt'] = [list(p) for p in d['items'][0][1:]]
        return data

    records = []
    for pressure, grind, markers, bars, connectors in SERIES:
        for k, (marker_id, bar_ids) in enumerate(zip(markers, bars)):
            marker = obj(marker_id)
            x0,y0,x1,y1 = marker['bbox_pt']
            xc = (x0+x1)/2
            candidates = [{'role':'marker_bbox_centre', 'object':marker_id,
                           'xy_pt':[xc,(y0+y1)/2]}]
            if pressure == 9:
                vertices = [list(item[1]) for item in drawings[marker_id]['items']]
                marker['vertices_pt'] = vertices
                candidates.append({'role':'triangle_vertex_centroid_candidate',
                                   'object':marker_id,
                                   'xy_pt':[sum(v[j] for v in vertices)/3 for j in range(2)]})
            endpoints = []
            for cid in connectors:
                pts = obj(cid)['line_pt']
                # Paths 102/104 are short solid ends of a manually dashed
                # connector. Only their end nearest the marker symmetry axis
                # is an anchor; the other end is the end of a dash, not a value.
                n, pt = min(enumerate(pts), key=lambda item:abs(item[1][0]-xc))
                # Association is within the marker's horizontal footprint,
                # not a fitted force tolerance. No interpolation is performed.
                if x0 <= pt[0] <= x1:
                    c = {'role':'connector_endpoint', 'object':cid,
                         'endpoint':n, 'xy_pt':pt}
                    endpoints.append(c)
                    candidates.append(c)
            if not endpoints:
                raise ValueError('No associated connector anchor')
            nominal = endpoints[0]['xy_pt']
            bar_objects = [obj(i) for i in bar_ids]
            for bar in bar_objects:
                pts = bar['line_pt']
                junction = min(pts, key=lambda p:abs(p[1]-nominal[1]))
                candidates.append({'role':'bar_segment_junction',
                                   'object':bar['path_index'],'xy_pt':junction})
            all_bar_y = [p[1] for b in bar_objects for p in b['line_pt']]
            records.append({
                'observation_id':f'S2-P{pressure}-G{grind}-F{k+1}',
                'pressure_label_bar':pressure, 'grind_label':grind,
                'force_group':f'F{k+1}', 'nominal_force_N':None,
                'marker_shape':'triangle' if pressure == 9 else 'circle',
                'marker_fill':'dark' if grind == '1.3' else 'light',
                'marker_object':marker,
                'connector_objects':[obj(i) for i in connectors
                                     if any(c['object']==i for c in endpoints)],
                'bar_objects':bar_objects, 'anchor_candidates':candidates,
                'nominal_anchor_rule':'first associated connector endpoint nearest marker horizontal symmetry axis in declared series order',
                'nominal_xy_pt':nominal,
                'central_xy_enclosure_pt':[
                    [min(c['xy_pt'][j] for c in candidates)-(.25+marker['stroke_width_pt']/2),
                     max(c['xy_pt'][j] for c in candidates)+(.25+marker['stroke_width_pt']/2)]
                    for j in range(2)],
                'bar_y_endpoints_pt': [min(all_bar_y),max(all_bar_y)] if all_bar_y else None,
                'bar_endpoint_allowance_pt':.25+marker['stroke_width_pt']/2 if bar_ids else None,
                'bar_recovery_status':'ENCODED_ENDPOINTS_RECOVERED' if bar_ids else 'NO_RECOVERABLE_VERTICAL_PATH',
                'summary_statistic':'UNRESOLVED_S2_SPECIFIC', 'replicate_n':None,
                'bar_semantics':'UNRESOLVED_S2_SPECIFIC', 'shot_clock_origin':'UNRESOLVED',
            })
    frame = obj(84)
    pad = .25+frame['stroke_width_pt']/2
    ticks_y = [{'time_s':55,'coordinate_pt':frame['bbox_pt'][1], 'object':84},
               *[{'time_s':t, 'coordinate_pt':obj(i)['line_pt'][0][1], 'object':i}
                 for i,t in zip(range(147,152),[50,45,40,35,30])],
               {'time_s':25,'coordinate_pt':frame['bbox_pt'][3], 'object':84}]
    ticks_x = [{'force_N':f,'coordinate_pt':obj(i)['line_pt'][0][0], 'object':i}
               for i,f in zip([96,97,98],[100,200,300])]
    out = {
        'dataset_id':'cameron2020/figS2_pressure_tamp',
        'source_sha256':SI_SHA, 'pdf_page':7, 'printed_page':6,
        'coordinate_system':'PDF page points; origin top left, y increases down',
        'extraction':{'library':'PyMuPDF','version':pymupdf.VersionBind,
                      'page_content_xref':33,'figure_form_xref':74,
                      'form_to_page_xy':'x=54.141+0.93796*u; y=657.721-0.93796*v',
                      'form_source_name':'Figures/FigureS2_Tamp.pdf'},
        'calibration':{'x_ticks':ticks_x,'y_ticks':ticks_y,
                       'tick_allowance_pt':pad,'stroke_width_pt':frame['stroke_width_pt'],
                       'graphical_floor_pt':.25,
                       'method':'outer labelled ticks; all interior ticks checked for affine consistency'},
        'source_object_accounting':{
            'frame':84,'tick_paths':[86,87,88,92,93,96,97,98,147,148,149,150,151,152,153,154],
            'connector_paths':[85,89,90,91,94,95,99,100,101,102,103,104,105,106],
            'marker_paths':[i for s in SERIES for i in s[2]],
            'bar_segment_paths':[i for s in SERIES for b in s[3] for i in b],
            'excluded_paths':[155,156,157,158],
            'exclusion_reason':'off-plot curve artwork; all x <=77.590 pt, left of S2 frame x=79.466 pt; no force-group association',
            'bar_count_unit':'12 paired vertical bar objects = 24 separately drawn segments',
            'unassigned_in_frame_paths':[],
        },
        'observations':records,
    }
    return qualify(out)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--pdf',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    result=recover(args.pdf)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'observations.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__ == '__main__':
    main()

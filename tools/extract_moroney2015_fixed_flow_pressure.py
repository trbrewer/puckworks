#!/usr/bin/env python3
"""Re-extract ONLY the authenticated Moroney 2015 Figure 12, from an external PDF.

No network or PDF redistribution. The analysis module needs no PDF/PyMuPDF.
Drawing/subpath identities are specific to the accepted publisher PDF.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHA = '896672a997e585a50d97f988caa66259a9a8ed0067300ea7d19725a13c01c4a8'
BUNDLE = ROOT / 'docs/analysis/sci_md_moroney_fixed_flow_pressure_001'
RAW = ROOT / 'puckworks/data/moroney2015/fig12_pressure_comparison.csv'


def split_markers(drawing):
    """Split four-Bezier circles and EACH rectangle; never count a path as a point."""
    items = drawing['items']
    if all(i[0] == 'c' for i in items) and len(items) % 4 == 0:
        for j in range(0, len(items), 4):
            chunk = items[j:j + 4]
            anchors = [tuple(i[1]) for i in chunk]
            xs, ys = zip(*anchors)
            box = [min(xs), min(ys), max(xs), max(ys)]
            center = [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]
            candidates = [center] + [[(anchors[k][a] + anchors[k + 2][a]) / 2
                                     for a in (0, 1)] for k in (0, 1)]
            geometry = [[i[0], *[list(p) for p in i[1:]]] for i in chunk]
            yield j // 4, box, center, candidates, geometry
    elif all(i[0] == 're' for i in items):
        for j, i in enumerate(items):
            box = list(i[1])
            center = [(box[0] + box[2]) / 2, (box[1] + box[3]) / 2]
            yield j, box, center, [center], [['re', box, i[2]]]
    else:
        raise ValueError('Unrecognized colored marker geometry: audit required')


def extract(pdf):
    if hashlib.sha256(pdf.read_bytes()).hexdigest() != SHA:
        raise ValueError('PDF identity mismatch; independent edition qualification required')
    import pymupdf
    doc = pymupdf.open(pdf)
    if len(doc) != 19:
        raise ValueError('Page mapping mismatch')
    page = doc[17]
    drawings = page.get_drawings()
    words = page.get_text('words')
    axes = {}
    for panel, xids, yids, frame_id, legend_id, end in [
        ('a', list(range(326, 347, 4)), list(range(348, 369, 5)), 325, 324, 420),
        ('b', list(range(463, 484, 4)), list(range(485, 506, 5)), 462, 461, 557),
    ]:
        axes[panel] = {'frame': {'drawing_index': frame_id,
                               'bbox_pt': list(drawings[frame_id]['rect'])},
                       'legend': {'drawing_index': legend_id,
                                  'seqno': drawings[legend_id]['seqno'],
                                  'bbox_pt': list(drawings[legend_id]['rect'])},
                       'ticks': {}}
        for axis, ids, values in [('x', xids, range(0, 1001, 200)),
                                  ('y', yids, range(0, 201, 50))]:
            ticks = []
            for i, value in zip(ids, values):
                d = drawings[i]
                _, p, r = d['items'][0]
                coord = p[0 if axis == 'x' else 1]
                candidates = [w for w in words if w[4] == str(value)
                              and (abs((w[0] + w[2]) / 2 - coord) < 3 and 324 < w[1] < 326
                                   if axis == 'x' else
                                   abs((w[1] + w[3]) / 2 - coord) < 3
                                   and abs(w[2] - drawings[frame_id]['rect'].x0) < 8)]
                if len(candidates) != 1:
                    raise ValueError(f'Unresolved tick label {panel}/{axis}/{value}')
                ticks.append({'value': value, 'coordinate_pt': coord,
                              'drawing_index': i, 'seqno': d['seqno'],
                              'line_pt': [list(p), list(r)], 'stroke_width_pt': d['width'],
                              'label_bbox_pt': list(candidates[0][:4]), 'label': str(value)})
            axes[panel]['ticks'][axis] = ticks
        # Also retain unlabeled minor and mirrored tick paths. All are checked
        # against their nearest native minor-tick value, never fitted away.
        checks = []
        for i in range(frame_id + 1, end):
            d = drawings[i]
            if len(d['items']) != 1 or d['items'][0][0] != 'l':
                continue
            _, p, r = d['items'][0]
            if abs(p - r) > 2:
                continue
            axis = 'x' if p.x == r.x else 'y'
            coord = p.x if axis == 'x' else p.y
            t = axes[panel]['ticks'][axis]
            c0, c1 = t[0]['coordinate_pt'], t[-1]['coordinate_pt']
            value_max, step = (1000, 50) if axis == 'x' else (200, 10)
            expected_value = round((coord - c0) * value_max / (c1 - c0) / step) * step
            residual = coord - (c0 + expected_value * (c1 - c0) / value_max)
            checks.append({'drawing_index': i, 'seqno': d['seqno'], 'axis': axis,
                           'value': expected_value, 'coordinate_pt': coord,
                           'line_pt': [list(p), list(r)], 'stroke_width_pt': d['width'],
                           'residual_pt': residual,
                           'role': 'labelled' if i in xids + yids else 'minor_or_mirrored'})
        axes[panel]['all_tick_checks'] = checks
        for axis in ['x', 'y']:
            res = max(abs(t['residual_pt']) for t in checks if t['axis'] == axis)
            width = max(t['stroke_width_pt'] for t in checks if t['axis'] == axis)
            axes[panel][f'{axis}_max_residual_pt'] = res
            axes[panel][f'{axis}_tick_allowance_pt'] = .25 + width / 2 + res
    rows = list(csv.DictReader(line for line in RAW.read_text().splitlines() if not line.startswith('#')))
    markers = []
    for i, d in enumerate(drawings):
        if d['fill'] not in [(0, 0, 1), (1, 0, 0)] or not 230 < d['rect'].y0 < 322:
            continue
        for sub, box, center, candidates, geometry in split_markers(d):
            panel = 'a' if center[0] < 300 else 'b'
            legend = axes[panel]['legend']['bbox_pt']
            is_legend = legend[0] <= center[0] <= legend[2] and legend[1] <= center[1] <= legend[3]
            t = axes[panel]['ticks']
            mass = (center[0] - t['x'][0]['coordinate_pt']) * 1000 / (t['x'][-1]['coordinate_pt'] - t['x'][0]['coordinate_pt'])
            conc = (center[1] - t['y'][0]['coordinate_pt']) * 200 / (t['y'][-1]['coordinate_pt'] - t['y'][0]['coordinate_pt'])
            pressure = '2.3' if d['fill'] == (0, 0, 1) else '9.0'
            matches = [(j, r) for j, r in enumerate(rows, 1) if r['panel'] == panel
                       and f'_{pressure}bar_' in r['series']
                       and abs(float(r['Mbrew_g']) - mass) < .15
                       and abs(float(r['concentration_mg_per_g']) - conc) < .03]
            if len(matches) != 1:
                raise ValueError(f'Unmatched/ambiguous marker {i}/{sub}: {matches}')
            j, row = matches[0]
            markers.append({'source_id': f'p17:d{i}:s{d["seqno"]}:sub{sub}',
                            'legacy_row_id': f'fig12_pressure_comparison.csv:data:{j}',
                            'legacy_row_number': j, 'panel': panel, 'pressure_bar_label': pressure,
                            'pdf_page_index': 17, 'printed_page': 233, 'drawing_index': i,
                            'seqno': d['seqno'], 'subpath_index': sub, 'geometry_pt': geometry,
                            'bbox_pt': box, 'center_pt': center, 'center_candidates_pt': candidates,
                            'stroke_width_pt': d['width'] or 0., 'fill_rgb': list(d['fill']),
                            'disposition': 'legend_sample' if is_legend else 'data_marker',
                            'reason': 'Inside rounded labelled legend box beside series label' if is_legend else 'Experimental filled marker outside legend; full-panel render inspected',
                            'legacy_values': row, 'reextracted_mass_g': mass,
                            'reextracted_concentration_mg_g': conc,
                            'legacy_delta_mass_g': mass - float(row['Mbrew_g']),
                            'legacy_delta_concentration_mg_g': conc - float(row['concentration_mg_per_g'])})
    if len(markers) != len(rows) or len({m['legacy_row_id'] for m in markers}) != len(rows):
        raise ValueError('Incomplete one-to-one legacy accounting')
    # Use the accepted Fig3 object identities for lineage, verifying their
    # geometry directly against the same source; do not use Fig3 as primary data.
    prior = json.loads((ROOT / 'docs/analysis/sci_md_moroney_transfer_001/source_objects.json').read_text())
    baseline = prior['audits']['fig3']['marker_objects']
    fig3draw = doc[3].get_drawings()
    lineage = []
    for panel in ['a', 'b']:
        low = sorted([m for m in markers if m['panel'] == panel and m['pressure_bar_label'] == '2.3'
                      and m['disposition'] == 'data_marker'], key=lambda m: m['center_pt'][0])
        old = sorted([m for m in baseline if m['panel'] == panel], key=lambda m: m['pdf_center'][0])
        if len(low) != len(old):
            raise ValueError('Reuse count mismatch')
        cal = prior['audits']['fig3']['axis_coordinates'][panel]
        for m, b in zip(low, old):
            obj = list(split_markers(fig3draw[b['drawing_index']]))[b['subpath']]
            if max(abs(x-y) for x, y in zip(obj[2], b['pdf_center'])) > .0001:
                raise ValueError('Figure3 geometry differs from accepted identity')
            bx, by = obj[2]
            bm = (bx-cal['x0'])*1000/(cal['x1000']-cal['x0'])
            bc = (by-cal['y0'])*200/(cal['y200']-cal['y0'])
            dm, dc = m['reextracted_mass_g']-bm, m['reextracted_concentration_mg_g']-bc
            if abs(dm) > .1 or abs(dc) > .1:
                raise ValueError('Reuse correspondence outside transcription check')
            m['lineage_id'] = b['row_id']
            lineage.append({'figure12_id': m['source_id'], 'figure3_row_id': b['row_id'],
                            'figure3_pdf_page_index': 3, 'figure3_drawing_index': b['drawing_index'],
                            'figure3_seqno': b['seqno'], 'figure3_subpath': b['subpath'],
                            'figure3_center_pt': obj[2], 'delta_mass_g': dm,
                            'delta_concentration_mg_g': dc,
                            'basis': 'Same JK baseline identified by source Fig3/G.3; ordered one-to-one independently recalibrated matching; rendering differences retained'})
    for m in markers:
        m.setdefault('lineage_id', None)
    return {'task': 'SCI-MD-MORONEY-FIXED-FLOW-PRESSURE-001', 'dataset_id': 'moroney2015/data',
            'pdf_sha256': SHA, 'pages': len(doc), 'edition': 'CES 137 (2015) 216–234 publisher article',
            'doi': '10.1016/j.ces.2015.06.003', 'pdf_redistributed': False,
            'coordinate_convention': 'PDF points; top-left origin, x right, y down; page/drawing/seq/subpath zero-based; legacy rows one-based excluding comments/header',
            'render_inspected': True, 'calibration': axes,
            'legacy_rows': sorted(markers, key=lambda m: m['legacy_row_number']),
            'lineage': lineage,
            'counts': {'raw_rows': len(rows), 'marker_candidates': len(markers),
                       'retained': sum(m['disposition'] == 'data_marker' for m in markers),
                       'legend_samples': sum(m['disposition'] == 'legend_sample' for m in markers),
                       'ambiguous': 0, 'unsupported': 0, 'duplicate_renderings_in_fig12': 0,
                       'omitted_marker_candidates': 0, 'reused_fig3_markers': len(lineage),
                       'physical_extraction_count': None},
            'connecting_paths': 'No colored connecting paths in Fig12; marker subpaths only. New analysis lines are declared interpolation, not source measurements.',
            'unrelated_page_objects': 'Fig11, references and decorative glyph paths not catalogued'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pdf', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True, help='Numerical JSON only; never copies the PDF')
    args = p.parse_args()
    result = extract(args.pdf)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Optional source-only PDF recovery; never imported by the offline calculation.

Usage: python tools/recover_matias2023_figure.py --source-dir DIR --output JSON
DIR contains paper.pdf, source.tar (arXiv v2). No author code is executed.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import tarfile

HASHES = {
    'paper.pdf': '500edb0bf2f76e2f616b4abed291ad2ca8208128a5f78cb3114e59ca85cb417b',
    'source.tar': '5e114561670c7253417ea47cd14b6288020bbde9fad57c6eecba16c77943015f',
    'img/experiment.pdf': '7757b8cc762f26e60e0c77a1d4a7f4da5e1791f1b3ab2da9526d6b50c98d61c9',
}
NUMBER = r'(-?\d+(?:\.\d+)?)'
SEGMENT = re.compile(r' '.join([NUMBER, NUMBER, 'm', NUMBER, NUMBER, 'l S']))
RECT = re.compile(r' '.join([NUMBER, NUMBER, NUMBER, NUMBER, 're B']))


def recover(source_dir):
    import pymupdf
    for name in ('paper.pdf', 'source.tar'):
        assert hashlib.sha256((source_dir/name).read_bytes()).hexdigest() == HASHES[name]
    with tarfile.open(source_dir/'source.tar') as archive:
        members = archive.getmembers()
        assert len(members) < 10000 and sum(m.size for m in members) < 256*1024**2
        for m in members:
            p = PurePosixPath(m.name)
            assert not p.is_absolute() and '..' not in p.parts
            assert not m.issym() and not m.islnk() and m.size < 64*1024**2
        raw = archive.extractfile('img/experiment.pdf').read()
        body = archive.extractfile('body.tex').read().decode()
        main = archive.extractfile('continuum_equation.tex').read().decode()
        assert r'\includegraphics[width=\linewidth]{experiment}' in body
        assert r'\graphicspath{{./img/}}' in main
    assert hashlib.sha256(raw).hexdigest() == HASHES['img/experiment.pdf']
    doc = pymupdf.open(stream=raw, filetype='pdf')
    paper = pymupdf.open(source_dir/'paper.pdf')
    page = doc[0]
    stream = page.read_contents()
    # Exact embedded-stream equality authenticates more strongly than visual similarity.
    embedded = next(ref for ref, name, parent, box in paper[3].get_xobjects()
                    if name == 'Im3' and parent == 0)
    assert paper.xref_stream(embedded) == stream
    forms = {name: doc.xref_stream(ref).decode() for ref, name, parent, box in page.get_xobjects()}
    embedded_forms = {name: paper.xref_stream(ref).decode()
                      for ref, name, parent, box in paper[3].get_xobjects() if parent == embedded}
    assert forms == embedded_forms
    markers = RECT.findall(forms['x27'])
    assert len(markers) == 10
    rows = []
    for i, rect in enumerate(markers, 1):
        h, v = f'x{i+6}', f'x{i+16}'
        hs, vs = SEGMENT.findall(forms[h]), SEGMENT.findall(forms[v])
        assert len(hs) == len(vs) == 1
        rows.append({'fraction_id': f'F{i:02}', 'fraction_index': i,
                     'marker_rectangle_tokens': list(rect),
                     'horizontal_tokens': list(hs[0]), 'vertical_tokens': list(vs[0]),
                     'source_objects': {'marker': 'x27', 'horizontal': h, 'vertical': v}})
    # Keep decimal lexemes, not parser float strings. Axis glyphs authenticated by rendering.
    axes = SEGMENT.findall(stream.decode())
    major_x = [list(v) for v in axes if v[1] == '134.711' and v[3] == '138.211']
    major_y = [list(v) for v in axes if v[0] == '37.395' and v[2] == '33.895']
    minor_y = [list(v) for v in axes if v[0] == '37.395' and v[2] == '35.395']
    return {
        'dataset_id': 'matias2023/fig3_caffeine_fractions', 'schema_version': 1,
        'source_hashes': HASHES, 'source_bytes': {'paper.pdf': 2302283, 'img/experiment.pdf': 26421},
        'license': 'CC-BY-4.0', 'attribution': 'Matias et al. (2023), DOI 10.1063/5.0176273; arXiv:2304.03161v2 Figure 3; derived geometry',
        'coordinate_system': 'native figure points, x right and y down after the initial PDF cm',
        'page_transform_tokens': ['1', '0', '0', '-1', '0', '166.461365'],
        'form_matrices': 'identity (no /Matrix); all shapes use the same parent coordinate system',
        'article_embedding': {'page': 4, 'translation_tokens': ['54', '569.06'], 'scale_token': '1.02646', 'all_embedded_streams_byte_identical': True},
        'clip_rectangle_tokens': ['37.395', '7.199', '189.719', '127.512'],
        'right_spine_x_token': '227.113', 'marker_stroke_width_token': '1',
        'segment_stroke_width_token': '1.5',
        'calibration': {'x_major_labels_mL': [0, 10, 20, 30, 40, 50], 'x_major_segments_tokens': major_x,
                        'y_major_labels_mg_L': [100, 1000], 'y_major_segments_tokens': major_y,
                        'y_minor_labels_mg_L': [50,60,70,80,90,200,300,400,500,600,700,800,900,2000,3000,4000,5000,6000,7000,8000],
                        'y_minor_segments_tokens': minor_y,
                        'uniform_coordinate_radius_pt': '1/100',
                        'band_contract': 'corner-enclosed shared affine calibration, then conservative per-feature rectangular outer relaxation'},
        'source_stream_sha256': hashlib.sha256(stream).hexdigest(),
        'forms': {k: v for k,v in forms.items() if k != 'x6'},
        'observations': rows,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    args.output.write_text(json.dumps(recover(args.source_dir), indent=2, sort_keys=True)+'\n')


if __name__ == '__main__':
    main()

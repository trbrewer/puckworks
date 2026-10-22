#!/usr/bin/env python3
"""Optional exact-copy native-path extraction; requires PyMuPDF 2.0, no download.

The offline scientific producer consumes these committed factual coordinates.
No PDF, page render, or source artwork is copied into the repository.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

PDF_SHA = 'f131d9893e2ac78ce0664d5528beac4be51a02cf1ae684e41920fbc6cadc8818'


def extract(pdf, output):
    import pymupdf

    if hashlib.sha256(pdf.read_bytes()).hexdigest() != PDF_SHA:
        raise ValueError('Unqualified PDF identity; inspect edition/pagination first')
    doc = pymupdf.open(pdf)
    if len(doc) != 359:
        raise ValueError('Unexpected pagination')
    page = doc[260]
    drawings = page.get_drawings()
    if drawings[23]['items'] != drawings[32]['items']:
        raise ValueError('Duplicate error paths disagree')
    if page.xref != 2817 or page.get_contents() != [2818]:
        raise ValueError('Unexpected page/content identity')
    indices = [4, 8, 9, 10, 11, 12, 13, 14, *range(15, 33)]
    paths = []
    for i in indices:
        d = drawings[i]
        paths.append({'drawing_index': i, 'seqno': d['seqno'], 'type': d['type'],
                      'width_pt': d['width'], 'color': d['color'], 'fill': d['fill'],
                      'items': [[v if isinstance(v, (str, int)) else list(v)
                                 for v in item] for item in d['items']]})
    # Quad includes Point objects: flatten only for JSON representation.
    def serial(value):
        if isinstance(value, pymupdf.Point):
            return list(value)
        raise TypeError(type(value).__name__)
    rows = []
    for n, (grind, alias, chamber) in enumerate([
            ('Psi_B', 'A', '2:1'), ('Psi_B', 'A', '6:1'),
            ('Psi_E', 'D', '2:1'), ('Psi_E', 'D', '6:1')]):
        outline = drawings[16+2*n]['items'][0][1]
        repeated = drawings[25+2*n]['items'][0][1]
        if outline != repeated:
            raise ValueError('Duplicate bar paths disagree')
        err = drawings[32]['items'][3*n:3*n+3]
        rows.append(dict(condition=f'{grind}_{chamber}', grind=grind, journal_grind=alias,
                         chamber=chamber, mean_y_pt=outline.rect.y0,
                         fill_top_y_pt=drawings[15+2*n]['rect'].y0,
                         bar_left_x_pt=outline.rect.x0, bar_right_x_pt=outline.rect.x1,
                         error_x_pt=err[0][1].x, upper_endpoint_y_pt=err[1][1].y,
                         lower_endpoint_y_pt=err[2][1].y,
                         outline_indices=f'{16+2*n};{25+2*n}',
                         fill_indices=f'{15+2*n};{24+2*n}',
                         error_drawing_index=32, error_seqno=48,
                         upper_cap_item=3*n+1, lower_cap_item=3*n+2))
    output.mkdir(parents=True, exist_ok=True)
    with (output/'source_coordinates.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    metadata = dict(pdf_sha256=PDF_SHA, pdf_pages=359, printed_page=236, pdf_page=261,
                    page_xref=page.xref, content_xrefs=page.get_contents(),
                    decoded_content_sha256=hashlib.sha256(doc.xref_stream(2818)).hexdigest(),
                    coordinate_convention='page points; origin top left; y downward',
                    extractor=f'PyMuPDF {pymupdf.VersionBind}', paths=paths)
    (output/'source_paths.json').write_text(json.dumps(metadata, default=serial, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    extract(args.pdf, args.output)

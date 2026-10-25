#!/usr/bin/env python3
"""Optional native extraction/overlays. Not needed by the offline analysis.

Extraction: python tools/foster_radial_source.py extract --pdf SOURCE.pdf --output DIR
Audit: python tools/foster_radial_source.py overlay --output DIR
Dependencies: PyMuPDF 1.26.6 for extraction; Pillow for audit overlays.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/'puckworks/data/foster2025_2/fig8_fig9_radial_front.json'


def extract(pdf, output):
    import pymupdf
    data = json.loads(DATA.read_text())
    wanted = {v['sha256']: k for k, v in data['images'].items()}
    output.mkdir(parents=True, exist_ok=True)
    document = pymupdf.open(pdf)
    receipt = {'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
               'pdf_bytes': pdf.stat().st_size, 'pages': len(document),
               'PyMuPDF': pymupdf.VersionBind, 'MuPDF': pymupdf.VersionFitz,
               'images': {}, 'rights': 'Article CC BY-NC 4.0; UL cover CC BY-NC-SA 4.0'}
    for page_no, page in enumerate(document, 1):
        for image in page.get_images(full=True):
            obj = document.extract_image(image[0])
            sha = hashlib.sha256(obj['image']).hexdigest()
            if sha in wanted:
                name = wanted[sha]
                (output/f'{name}.{obj["ext"]}').write_bytes(obj['image'])
                receipt['images'][name] = {'sha256': sha, 'pdf_page': page_no,
                    'xref': image[0], 'width': obj['width'], 'height': obj['height'],
                    'format': obj['ext']}
    if set(receipt['images']) != set(wanted.values()):
        raise ValueError('native identity mismatch: authenticate pixels/content; do not substitute DOI')
    (output/'extraction_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    return receipt


def overlay(output):
    from PIL import Image, ImageDraw
    data = json.loads(DATA.read_text())
    output.mkdir(parents=True, exist_ok=True)
    for image_id in ('fig9', 'fig8'):
        source = ROOT/data['images'][image_id]['path']
        if hashlib.sha256(source.read_bytes()).hexdigest() != data['images'][image_id]['sha256']:
            raise ValueError('source image identity changed')
        raw = Image.open(source).convert('RGB')
        layer = raw.copy()
        draw = ImageDraw.Draw(layer)
        for row in data['observations']:
            records = [row] if image_id == 'fig9' else [r for r in row['duplicate_records']
                              if r['linkage'] == 'AUTHENTICATED_SHARED_CENTER']
            for rec in records:
                x = rec['x_px']
                for feature, color in [('center', '#000000'), ('lower_endpoint', '#00BFFF'),
                                       ('upper_endpoint', '#F00000')]:
                    reading = rec.get(feature)
                    if not reading or reading['support'] != 'SUPPORTED':
                        continue
                    lo, hi = reading['enclosure_px']
                    draw.rectangle((x-11, lo, x+11, hi), outline=color, width=1)
        layer.save(output/f'{image_id}_overlay.png')
        if image_id == 'fig9':
            for name, box in [('legend',(105,335,315,540)), ('plateau',(140,845,1400,955))]:
                original, annotated = raw.crop(box), layer.crop(box)
                combined = Image.new('RGB', (original.width*2+10, original.height+20), 'white')
                combined.paste(original, (0,20)); combined.paste(annotated,(original.width+10,20))
                labels = ImageDraw.Draw(combined)
                labels.text((0,0), 'Native pixels', fill='black')
                labels.text((original.width+10,0), 'Reading boxes (same native scale)', fill='black')
                combined.save(output/f'{name}_audit.png')
    return {'canonical_sha256': hashlib.sha256(DATA.read_bytes()).hexdigest(),
            'legend': 'black=center box; blue=literal lower-ordinate endpoint; red=upper-ordinate endpoint; no box=no pixel support'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['extract', 'overlay'])
    parser.add_argument('--pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.mode == 'extract' and args.pdf is None:
        parser.error('--pdf is required for extraction')
    result = extract(args.pdf, args.output) if args.mode == 'extract' else overlay(args.output)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Regenerate the CC BY 3.0 source-reading audit overlay (requires PyMuPDF/Pillow)."""
import argparse
import hashlib
from pathlib import Path

from puckworks.analysis.cor15_shape_001 import read_inputs


def main():
    import pymupdf
    from PIL import Image, ImageDraw
    import io

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-pdf', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    contract, rows = read_inputs()
    if hashlib.sha256(args.source_pdf.read_bytes()).hexdigest() != contract['source_pdf_sha256']:
        raise ValueError('Source PDF hash differs from the inspected copy')
    with pymupdf.open(args.source_pdf) as doc:
        raw = doc.extract_image(contract['xobject'])['image']
    if hashlib.sha256(raw).hexdigest() != contract['native_image_sha256']:
        raise ValueError('Native figure hash differs')
    im = Image.open(io.BytesIO(raw)).convert('RGB')
    d = ImageDraw.Draw(im)
    for r in rows:
        x, y, g = map(float, (r['x_px'],r['y_px'],r['mean_guard_px']))
        color = {'A':'#e73535','B':'#008800','C':'#0055dd','D':'#bb00bb'}[r['grind']]
        d.rectangle((x-g,y-g,x+g,y+g), outline=color, width=1)
        d.text((x+7,y-14), r['point_id'], fill=color)
        if r['sd_left_px']:
            d.line((float(r['sd_left_px']),y,float(r['sd_right_px']),y), fill=color)
        if r['sd_top_px']:
            d.line((x,float(r['sd_top_px']),x,float(r['sd_bottom_px'])), fill=color)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    im.save(args.output)


if __name__ == '__main__':
    main()

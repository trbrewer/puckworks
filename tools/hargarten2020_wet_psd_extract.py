#!/usr/bin/env python3
"""Optional source-artifact extraction, NOT used by the offline analysis producer.

Requires PyMuPDF and an explicitly supplied authenticated TUM published PDF copy.
Does not perform automatic digitization or infer raw instrument measurements.
"""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads((Path(__file__).resolve().parents[1] /
        'puckworks/data/hargarten2020/wet_psd_001/contract.json').read_text())
    if hashlib.sha256(args.pdf.read_bytes()).hexdigest() != contract['source']['sha256']:
        raise ValueError('Source PDF identity differs; do not reuse pixel calibration')
    import pymupdf
    doc = pymupdf.open(args.pdf)
    args.output.mkdir(parents=True, exist_ok=True)
    for panel, xref in [('fig2', 62), ('fig3b', 73), ('fig5b', 72)]:
        image = doc.extract_image(xref)['image']
        expected = contract['panels'][panel]
        if hashlib.sha256(image).hexdigest() != expected['image_sha256']:
            raise ValueError('Embedded artwork differs: ' + panel)
        path = args.output / expected['image']
        path.write_bytes(image)
        print(panel, path)
    print('Source artwork remains CC BY-NC, outside repository software license.')


if __name__ == '__main__':
    main()

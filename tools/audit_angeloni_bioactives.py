#!/usr/bin/env python3
"""Verify the HEADLINE corpus against the Angeloni et al. (2023) article PDF.

Twelve review rounds reported "stale-number category: empty" and meant it — but that check is
INTERNAL consistency: the same value copied correctly from the artefact to the manuscript to the
caption. It cannot tell you the value was transcribed correctly in the first place, and the source
contract says so in as many words:

    structure, controlled tokens, finite decimal coordinates, parseability and optimal-grind support
    membership; NOT transcription, units or measurement accuracy against the source publication

`docs/data_intake/ANGELONI_TRANSCRIPTION_AUDIT.md` (2026-07-13) audited Tables 1–3 against the
article and passed. But it verified `angeloni2023_total_solids_lipids_rsd.csv` — total solids and
lipids. The file that carries the paper's entire headline result is `bioactives.csv`, from Tables
4–5, and it had never been machine-compared to the source. The 132 scored observations behind
8.44 % vs 8.83 % rested on a hand transcription nobody had checked.

This script closes that. It downloads the author-deposited PDF, pins its SHA-256, parses Tables 1,
4 and 5, and compares every cell against the committed CSV — including the derived `on_grid` flag,
because grid membership decides which records are training and which are held out.

Network-dependent by nature, so it is NOT a CI gate: it is a release/intake audit, run deliberately,
with its result recorded in the audit document. Offline it fails with a clear reason rather than
silently passing — a check that cannot look must not look like a check that looked and found
nothing.

CLI::

    python tools/audit_angeloni_bioactives.py            # fetch, verify, print a report
    python tools/audit_angeloni_bioactives.py --pdf FILE # verify against a local copy
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import pathlib
import re
import sys
import urllib.request

_REPO = pathlib.Path(__file__).resolve().parents[1]
COMMITTED_CSV = _REPO / "puckworks" / "data" / "angeloni2023" / "bioactives.csv"

#: The author-deposited copy at the Università di Camerino repository. MDPI itself is
#: Cloudflare-blocked for automated fetch; this mirror is what the Tables 1–3 audit used, and its
#: digest is pinned so a substituted document fails rather than being audited against.
SOURCE_URL = ("https://pubblicazioni.unicam.it/retrieve/"
              "d8b5f72e-eff9-4d85-b92d-7df02046c4a7/2023ComPerMod.pdf")
SOURCE_SHA256 = "2600ef731c37d088838eaabb3d88e8b9ad09a7ff7b7d63d566b6a13329fc6ea7"

#: Column order exactly as printed in the Tables 4/5 header.
ANALYTE_COLUMNS = ("TR", "TA", "AA", "CA", "3CQA", "5CQA", "CF", "FA", "3_5diCQA",
                   "totCQA", "totOA")

#: The declared 3x3 calibration grid. `on_grid` is a DERIVED flag, so it is re-derived here from the
#: article's own conditions rather than read back from the file being audited.
GRID_T = {"88", "93.4", "98"}
GRID_P = {"6", "9", "12"}

_ANALYTE_ROW = re.compile(r"^([AR]\d{1,2})\s+((?:-?\d+\.\d+\s+){10}-?\d+\.\d+)\s*$", re.M)
_CONDITION_ROW = re.compile(
    r"^(A\d{1,2})\s+([\d.]+)\s+(\d+)\s+([OCF])\s+(R\d{1,2})\s+([\d.]+)\s+(\d+)\s+([OCF])\s*$", re.M)


def load_pdf_text(pdf_bytes: bytes) -> str:
    try:
        import pypdf
    except ImportError:                                     # pragma: no cover - env-dependent
        raise SystemExit("pypdf is required to read the article PDF: pip install pypdf")
    import io

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def fetch_pdf(path: pathlib.Path | None) -> bytes:
    if path is not None:
        return path.read_bytes()
    try:
        with urllib.request.urlopen(SOURCE_URL, timeout=120) as response:
            return response.read()
    except Exception as exc:                                # pragma: no cover - network-dependent
        raise SystemExit(
            "could not fetch the article PDF (%s). This audit compares the committed corpus with "
            "the SOURCE, so it cannot run offline; supply a local copy with --pdf, and do not "
            "record a pass without it." % exc)


def parse_analytes(text: str) -> dict:
    start = text.index("Table 4. Contents of bioactive")
    end = text.index("Table 6.", start)
    out = {}
    for match in _ANALYTE_ROW.finditer(text[start:end]):
        values = match.group(2).split()
        if len(values) != len(ANALYTE_COLUMNS):             # pragma: no cover - layout guard
            raise SystemExit("row %s parsed %d values, expected %d"
                             % (match.group(1), len(values), len(ANALYTE_COLUMNS)))
        out[match.group(1)] = dict(zip(ANALYTE_COLUMNS, values))
    return out


def parse_conditions(text: str) -> dict:
    start = text.index("Table 1. Extraction conditions")
    end = text.index("2.2.1. Chemicals", start)
    out = {}
    for m in _CONDITION_ROW.finditer(text[start:end]):
        out[m.group(1)] = (m.group(2), m.group(3), m.group(4))
        out[m.group(5)] = (m.group(6), m.group(7), m.group(8))
    return out


def committed_rows() -> dict:
    lines = [ln for ln in COMMITTED_CSV.read_text(encoding="utf-8").splitlines()
             if not ln.lstrip().startswith("#")]
    return {r["sample"]: r for r in csv.DictReader(lines)}


def audit(pdf_bytes: bytes) -> tuple[dict, list[str]]:
    digest = hashlib.sha256(pdf_bytes).hexdigest()
    problems = []
    if digest != SOURCE_SHA256:
        problems.append("the fetched PDF hashes to %s, not the pinned %s; a different document "
                        "cannot audit this corpus" % (digest[:16], SOURCE_SHA256[:16]))
        return {"source_sha256": digest}, problems

    text = load_pdf_text(pdf_bytes)
    analytes, conditions, committed = parse_analytes(text), parse_conditions(text), committed_rows()

    for label, parsed in (("Tables 4/5", analytes), ("Table 1", conditions)):
        missing = sorted(set(committed) - set(parsed))
        extra = sorted(set(parsed) - set(committed))
        if missing:
            problems.append("%s: samples in the CSV but not in the article: %r" % (label, missing))
        if extra:
            problems.append("%s: samples in the article but not in the CSV: %r" % (label, extra))

    cells = 0
    for sample in sorted(set(analytes) & set(committed)):
        for column in ANALYTE_COLUMNS:
            got = committed[sample].get(column)
            if got is None:
                continue
            cells += 1
            if float(got) != float(analytes[sample][column]):
                problems.append("%s.%s: article %s, CSV %s"
                                % (sample, column, analytes[sample][column], got))

    for sample in sorted(set(conditions) & set(committed)):
        T, p, grind = conditions[sample]
        row = committed[sample]
        if float(row["T_degC"]) != float(T):
            problems.append("%s.T_degC: article %s, CSV %s" % (sample, T, row["T_degC"]))
        if float(row["p_bar"]) != float(p):
            problems.append("%s.p_bar: article %s, CSV %s" % (sample, p, row["p_bar"]))
        if row["granulometry"] != grind:
            problems.append("%s.granulometry: article %s, CSV %s"
                            % (sample, grind, row["granulometry"]))
        # `on_grid` is derived, so derive it from the ARTICLE and compare.
        expected = (T in GRID_T and p in GRID_P)
        if (row["on_grid"] == "True") != expected:
            problems.append("%s.on_grid: the article's (%s C, %s bar) implies %s, CSV says %s"
                            % (sample, T, p, expected, row["on_grid"]))

    return {"source_sha256": digest, "article_samples": len(analytes),
            "csv_samples": len(committed), "analyte_cells_compared": cells,
            "condition_rows_compared": len(set(conditions) & set(committed))}, problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pdf", type=pathlib.Path, help="verify against a local copy of the article")
    args = ap.parse_args(argv)

    summary, problems = audit(fetch_pdf(args.pdf))
    for key, value in summary.items():
        print("  %-26s %s" % (key, value))
    if problems:
        print("\nAngeloni bioactives audit FAILED: %d problem(s)" % len(problems), file=sys.stderr)
        for p in problems[:40]:
            print("  - %s" % p, file=sys.stderr)
        return 1
    print("\nAngeloni bioactives audit OK: every scored cell and condition matches the article.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Generate Paper 1's author-year reference list FROM references.bib.

Both Paper 1 files carried an instruction where the bibliography should be -- "Generate the final
author-year list from docs/literature_search/references.bib after the citation-key and DOI audit"
-- while the body made 27 distinct author-year citations. A reviewer could not check a single one.

This generates the list instead of hand-writing it, so it cannot drift from the .bib, and it
reports any citation with no matching entry rather than silently omitting it. It deliberately
matches on EVERY author surname in an entry, not just the first: the manuscript cites two-author
works as "Banga & Balsa-Canto, 2008", "Ellero & Navarini, 2019" and "Simpson & Maclaren (2023)",
and a first-author-only matcher reports those as missing.

    python tools/paper_a_references.py            # report coverage
    python tools/paper_a_references.py --write    # splice into both manuscripts
"""
from __future__ import annotations

import pathlib
import re
import sys
import unicodedata

REPO = pathlib.Path(__file__).resolve().parents[1]
BIB = REPO / "docs" / "literature_search" / "references.bib"
TARGETS = (REPO / "docs" / "PAPER_A_DRAFT.md",
           REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md")

BEGIN = "<!-- references:begin -->"
END = "<!-- references:end -->"

# TeX accent commands -> the Unicode combining mark they stand for. The previous version was a
# lookup table of the exact spellings that happened to appear, so `K\"unsch` (unbraced) and
# `Bia{\l}as`/`{\L}` (glyph commands, not accents) survived into the rendered bibliography as raw
# TeX -- exactly what a reviewer sees first. Accents are now decomposed generically and recomposed
# to real characters, so the list prints Künsch, Tönsing and Sánchez-López rather than mojibake.
_COMBINING = {"`": "̀", "'": "́", "^": "̂", "~": "̃", '"': "̈",
              "=": "̄", ".": "̇", "u": "̆", "v": "̌", "H": "̋",
              "c": "̧", "k": "̨", "b": "̱", "d": "̣", "r": "̊"}
# Standalone glyph commands, which take no argument letter.
_GLYPH = {r"\l": "ł", r"\L": "Ł", r"\o": "ø", r"\O": "Ø",
          r"\ss": "ß", r"\aa": "å", r"\AA": "Å", r"\ae": "æ",
          r"\AE": "Æ", r"\i": "i", r"\j": "j", r"\&": "&"}

# `{\"o}`, `\"{o}`, `\"o` and `{\'{a}}` all mean the same thing.
_ACCENT = re.compile(r"\{?\\(?P<acc>[`'\"^~=.]|[uvHckbdr](?=[\s{]))\s*\{?(?P<ch>[A-Za-z])\}?\}?")
# Longest-first so `\AA` is not consumed as `\A`+`A` and `\ss` not as `\s`+`s`.
_GLYPH_RE = re.compile("|".join(re.escape(k) for k in sorted(_GLYPH, key=len, reverse=True))
                       + r"(?![A-Za-z])")


def _clean(s: str) -> str:
    s = _ACCENT.sub(lambda m: unicodedata.normalize("NFC", m["ch"] + _COMBINING[m["acc"]]), s)
    s = _GLYPH_RE.sub(lambda m: _GLYPH[m.group(0)], s)
    # BibTeX `--` is an en dash; it reached the rendered list as a literal double hyphen in every
    # page range and in compound titles ("reaction--advection--diffusion").
    s = re.sub(r"(?<=\w)---?(?=\w)", "–", s)
    return " ".join(s.replace("{", "").replace("}", "").split())


def _fields(chunk: str) -> dict:
    """Brace-balanced BibTeX field parser.

    A regex that stopped at the first newline truncated multi-line author and title fields, and a
    greedy one swallowed the following fields whole (Apgar's journal came out as
    "Molecular BioSystems, volume = 6, pages = ..."). Scanning with a brace counter is the only
    thing that gets both right.
    """
    out, i, n = {}, 0, len(chunk)
    while i < n:
        m = re.compile(r"(\w+)\s*=\s*").search(chunk, i)
        if not m:
            break
        name, j = m.group(1).lower(), m.end()
        if j < n and chunk[j] == "{":
            depth, k = 0, j
            while k < n:
                if chunk[k] == "{":
                    depth += 1
                elif chunk[k] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                k += 1
            out[name] = chunk[j + 1:k]
            i = k + 1
        elif j < n and chunk[j] == '"':
            k = chunk.find('"', j + 1)
            out[name] = chunk[j + 1:k if k != -1 else n]
            i = (k + 1) if k != -1 else n
        else:
            k = chunk.find(",", j)
            out[name] = chunk[j:k if k != -1 else n]
            i = (k + 1) if k != -1 else n
    return {k: _clean(v) for k, v in out.items()}


def entries() -> list[dict]:
    raw = BIB.read_text(encoding="utf-8")
    out = []
    for chunk in re.split(r"(?m)^@", raw):
        if not chunk.strip():
            continue
        key = re.match(r"\w+\{([^,]+),", chunk)
        if not key:
            continue
        f = _fields(chunk)
        authors = f.get("author", "")
        out.append(dict(
            key=key.group(1).strip(), authors=authors, year=f.get("year", ""),
            title=f.get("title", ""), journal=f.get("journal") or f.get("booktitle", ""),
            volume=f.get("volume", ""), pages=f.get("pages", ""), doi=f.get("doi", ""),
            # BibTeX's `others` is the "et al." marker, not a person: it must not become a
            # candidate surname, or a citation to a genuine "Others" would silently resolve.
            surnames={_surname(a) for a in authors.split(" and ")
                      if a.strip() and a.strip().lower() != "others"},
        ))
    return out


def _surname(a: str) -> str:
    a = _clean(a)
    return (a.split(",")[0] if "," in a else a.split()[-1] if a.split() else "").lower()


# A citation's author token. `\w` is Unicode-aware in Python 3, so this admits Tönsing and
# Sánchez-López; the old `[A-Z][A-Za-z\-']+` stopped dead at the first non-ASCII letter and the
# citation vanished. The leading character is checked for case in `cited()` rather than in the
# class, because there is no portable ASCII spelling of "any uppercase Unicode letter".
_NAME = r"[^\W\d_][\w\-'’]*"
_YEAR = r"(?:19|20)\d{2}[a-z]?"
_CITE = re.compile(
    rf"(?P<name>{_NAME})"
    # `\s+` spans newlines, so "Raue et\nal. (2009)" -- broken across a wrapped line -- matches.
    rf"(?:\s+(?:et\s+al\.?|(?:and|&)\s+{_NAME}))?"
    rf"[,)]?\s*\(?"
    # Grouped citations attach several years to one author string ("Transtrum et al., 2011, 2015").
    # Capturing only the first year silently dropped the second work from the bibliography.
    rf"(?P<years>{_YEAR}(?:\s*,\s*{_YEAR})*)")

_SKIP = {"table", "figure", "section", "appendix", "paper", "result", "fig", "eq",
         "equation", "supplementary", "note", "panel", "row", "step", "item"}


def cited(text: str) -> set[tuple[str, str]]:
    """(surname, year) pairs appearing as citations in the body."""
    body = text.split(BEGIN)[0].split("## References")[0]
    out = set()
    for m in _CITE.finditer(body):
        name = m["name"]
        if not name[0].isupper() or name.lower() in _SKIP:
            continue
        for year in re.findall(_YEAR, m["years"]):
            out.add((name.lower(), year[:4]))
    return out


def _first_surname(rec: dict) -> str:
    return _surname(rec["authors"].split(" and ")[0])


def _leads(surname: str, rec: dict) -> bool:
    """Does `surname` name the FIRST author of `rec`?

    Compound surnames ("Vaca Guerra", "Roman Corrochano") are cited by their last token, so the
    final token counts as a match too.
    """
    lead = _first_surname(rec)
    return bool(lead) and (lead == surname or lead.split()[-1] == surname)


def resolve(text: str):
    """Bind each in-text citation to exactly one bib entry, matching on the FIRST author only.

    An earlier version matched any author in the entry, to accommodate two-author citations such
    as "Banga & Balsa-Canto, 2008". That was unnecessary -- an author-year citation always leads
    with the first author, so the lead-author rule resolves those too -- and it aliased: two 2016
    entries both list Villaverde, so "Villaverde et al. (2016)" bound to whichever appeared first
    in the .bib. Deleting the correct entry left the audit reporting a clean pass while the
    citation silently pointed at Chis et al. (2016).
    """
    recs = entries()
    used, missing, ambiguous = {}, [], []
    for surname, year in sorted(cited(text)):
        hits = [r for r in recs if r["year"] == year and _leads(surname, r)]
        if len(hits) == 1:
            used[hits[0]["key"]] = hits[0]
        elif not hits:
            missing.append((surname, year))
        else:
            ambiguous.append((surname, year, tuple(r["key"] for r in hits)))
    resolve.last_ambiguous = ambiguous
    return used, missing


resolve.last_ambiguous = []


def render(used: dict) -> str:
    def sort_key(r):
        first = sorted(r["surnames"])[0] if r["surnames"] else ""
        au = r["authors"].split(" and ")[0]
        return (_surname(au) or first, r["year"])
    lines = [BEGIN, "<!-- generated by tools/paper_a_references.py — do not edit by hand -->", ""]
    for r in sorted(used.values(), key=sort_key):
        # BibTeX's `others` printed literally ("Browning, Alexander P.; others (2024)"). It is the
        # et-al marker and must render as one.
        names = [a for a in r["authors"].split(" and ") if a.strip()]
        elided = bool(names) and names[-1].strip().lower() == "others"
        if elided:
            names = names[:-1]
        authors = "; ".join(names) + (" et al." if elided else "")
        bits = [f"{authors} ({r['year']}). {r['title']}."]
        if r["journal"]:
            bits.append(f" *{r['journal']}*")
            if r["volume"]:
                bits.append(f" {r['volume']}")
            if r["pages"]:
                bits.append(f", {r['pages']}")
            bits.append(".")
        if r["doi"]:
            bits.append(f" doi:{r['doi']}")
        lines.append("- " + "".join(bits))
    lines += ["", END]
    return "\n".join(lines)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    rc = 0
    for path in TARGETS:
        text = path.read_text(encoding="utf-8")
        used, missing = resolve(text)
        ambiguous = resolve.last_ambiguous
        print(f"{path.name}: {len(used)} references resolved, {len(missing)} unmatched, "
              f"{len(ambiguous)} ambiguous")
        for s, y in missing:
            print(f"    UNMATCHED: {s} {y}")
            rc = 1
        for s, y, keys in ambiguous:
            print(f"    AMBIGUOUS: {s} {y} -> {', '.join(keys)}")
            rc = 1
        if "--write" in argv:
            block = render(used)
            if BEGIN in text and END in text:
                new = text.split(BEGIN)[0] + block + text.split(END, 1)[1]
            elif "## References" in text:
                head, sep, tail = text.partition("## References")
                nxt = tail.find("\n## ")
                rest = tail[nxt:] if nxt != -1 else ""
                new = head + "## References\n\n" + block + "\n" + rest
            else:
                # The canonical draft had NO References section at all -- not even a placeholder.
                # Insert one before the appendix-like trailing sections rather than at EOF, so the
                # bibliography sits where a reader expects it.
                anchors = ["\n## Figures", "\n## Reproducibility", "\n## Data and code availability"]
                at = min([text.find(a) for a in anchors if text.find(a) != -1] or [len(text)])
                new = (text[:at].rstrip() + "\n\n## References\n\n" + block + "\n"
                       + text[at:])
            path.write_text(new, encoding="utf-8")
            print(f"    wrote {len(used)} entries into {path.name}")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())

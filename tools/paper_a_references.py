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

REPO = pathlib.Path(__file__).resolve().parents[1]
BIB = REPO / "docs" / "literature_search" / "references.bib"
TARGETS = (REPO / "docs" / "PAPER_A_DRAFT.md",
           REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md")

BEGIN = "<!-- references:begin -->"
END = "<!-- references:end -->"

_TEX = {r"\`{e}": "e", r"\'{e}": "e", r"\'{i}": "i", r'\"{o}': "o", r"\'{o}": "o",
        r"{\"o}": "o", r"{\'e}": "e", r"{\'i}": "i", r"{\'a}": "a", r"\&": "&"}


def _clean(s: str) -> str:
    for a, b in _TEX.items():
        s = s.replace(a, b)
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
            surnames={_surname(a) for a in authors.split(" and ") if a.strip()},
        ))
    return out


def _surname(a: str) -> str:
    a = _clean(a)
    return (a.split(",")[0] if "," in a else a.split()[-1] if a.split() else "").lower()


def cited(text: str) -> set[tuple[str, str]]:
    """(surname, year) pairs appearing as citations in the body."""
    body = text.split(BEGIN)[0].split("## References")[0]
    skip = {"table", "figure", "section", "appendix", "paper", "result", "fig", "eq"}
    out = set()
    for m in re.finditer(r"([A-Z][A-Za-z\-']+)(?:\s+et al\.?)?[,)]?\s*\(?((?:19|20)\d{2})", body):
        if m.group(1).lower() in skip:
            continue
        out.add((m.group(1).lower(), m.group(2)))
    return out


def resolve(text: str):
    recs = entries()
    used, missing = {}, []
    for surname, year in sorted(cited(text)):
        # Compound surnames ("Vaca Guerra", "Balsa-Canto", "Roman Corrochano") are cited by their
        # last token, so an exact set membership test misses them. Accept a match on the final
        # token of any recorded surname as well.
        hit = next((r for r in recs if r["year"] == year
                    and (surname in r["surnames"]
                         or any(s.split()[-1] == surname for s in r["surnames"] if s))), None)
        if hit:
            used[hit["key"]] = hit
        else:
            missing.append((surname, year))
    return used, missing


def render(used: dict) -> str:
    def sort_key(r):
        first = sorted(r["surnames"])[0] if r["surnames"] else ""
        au = r["authors"].split(" and ")[0]
        return (_surname(au) or first, r["year"])
    lines = [BEGIN, "<!-- generated by tools/paper_a_references.py — do not edit by hand -->", ""]
    for r in sorted(used.values(), key=sort_key):
        authors = r["authors"].replace(" and ", "; ")
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
        print(f"{path.name}: {len(used)} references resolved, {len(missing)} unmatched")
        for s, y in missing:
            print(f"    UNMATCHED: {s} {y}")
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

"""Paper A cross-reference and scaffolding linter (Paper 1 second review MC8 + MC9).

Two failure modes the phrase guard in ``paper_a_consistency.py`` cannot see:

**MC9 — cross-references.** The venue conversion inherited the canonical draft's section
numbering even though the two files have different top-level structures, so a printed ``§4``
resolved to "Results" in the conversion when it meant "Result 2 — the degeneracy" (conversion
§4.2). Existence checks cannot catch this: the wrong number *does* name a real section. So each
reference names its target inline::

    §4.2<!--sec:result2-->

The HTML comment renders as nothing. This linter reads the pair, looks the label up in the file's
OWN heading table, and fails when the printed number is not that section's number. Renumbering a
section therefore breaks the build instead of silently re-pointing every reference to it.

**MC8 — repository scaffolding.** Internal review IDs, status words ("delivered", "owed",
"deferred"), bug history and prior-draft narrative belong in the change log, not the article. They
were removed once; this makes the removal stick.

CLI::

    python tools/paper_a_xref.py            # exit 1 and list every problem
    python tools/paper_a_xref.py report     # human-readable status (exit 0)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
DRAFT = _REPO / "docs" / "PAPER_A_DRAFT.md"
CONVERSION = _REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
FILES = (DRAFT, CONVERSION)

#: label -> substrings that identify that section's heading. The two files title several sections
#: differently (the draft's "Open gaps"/"Related work" are the conversion's "Limitations and future
#: work"/"Literature context"), so each label accepts any of its aliases.
SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "methods": ("Methods",),
    "evidence_vocab": ("Evidence vocabulary",),
    "result1": ("Result 1",),
    "result2": ("Result 2",),
    "result3": ("Result 3",),
    "temporal": ("In-sample fraction verification",),
    "discussion": ("Discussion",),
    "limitations": ("Limitations", "Open gaps"),
    "related": ("Related work", "Literature context"),
}

#: A numbered markdown heading: "## 4. Results" / "### 4.2 Result 2 — ...".
_HEADING = re.compile(r"^#{1,4}\s+(\d+(?:\.\d+)?)\.?\s+(.*?)\s*$", re.M)
#: An annotated reference: "§4.2<!--sec:result2-->".
_TAGGED = re.compile(r"§(\d+(?:\.\d+)?)<!--sec:([a-z_0-9]+)-->")
#: Any section reference at all, so bare ones can be reported.
_ANY_REF = re.compile(r"§(\d+(?:\.\d+)?)")

#: Text ranges exempt from the scaffolding lint. The canonical WORKING draft opens with an
#: explicitly-marked repository note that the venue conversion does not carry; it is scaffolding by
#: design and self-declares as strip-before-submission.
_EXEMPT_BLOCK = ("*__[REPOSITORY NOTE — strip before submission.__", "]_*")

_REVIEW_ID = re.compile(
    r"\breview\s+[A-Z]|"
    r"\b(?:MAJ-\d+|MC\d+\b|A\d-\d+|A-\d{2}|P0-\d+)\b")

#: (compiled pattern, why it must not appear). Word-bounded so ordinary prose is unaffected --
#: "delivered" as a status word, not the verb in "the shot delivered 40 mL".
_SCAFFOLD = [
    (re.compile(r"\*delivered\*|\*\*delivered\*\*|\bis delivered\b|\bare delivered\b"),
     "MC8: repository status language -- state the final result, not its delivery status"),
    (re.compile(r"\bstill owed\b|\bremains owed\b|\bis owed\b|\bowed follow-up\b|\bOwed:"),
     "MC8: 'owed' tracks the repository backlog, not a limitation of the study"),
    (re.compile(r"\bdeferred\b"),
     "MC8: 'deferred' is a project-management state; say what was not evaluated and why"),
    (re.compile(r"\bour earlier draft\b|\bpre-correction\b|\bprior draft\b"),
     "MC8: revision history belongs in the change log, not the article"),
    (re.compile(r"tuple-indexing bug|\bbug\b.{0,20}\bcorrected\b"),
     "MC8: implementation bug history does not help a reader understand the final study"),
    (re.compile(r"\bhandoff\b"),
     "MC8: internal handoff references are repository scaffolding"),
]


def _headings(text: str) -> dict[str, str]:
    """label -> the number that section carries in THIS file."""
    out: dict[str, str] = {}
    for number, title in _HEADING.findall(text):
        for label, aliases in SECTION_ALIASES.items():
            if any(a.lower() in title.lower() for a in aliases) and label not in out:
                out[label] = number
    return out


def _exempt_spans(text: str) -> list[tuple[int, int]]:
    spans = []
    start = text.find(_EXEMPT_BLOCK[0])
    if start != -1:
        end = text.find(_EXEMPT_BLOCK[1], start)
        spans.append((start, len(text) if end == -1 else end + len(_EXEMPT_BLOCK[1])))
    return spans


def _in_span(pos: int, spans) -> bool:
    return any(a <= pos < b for a, b in spans)


def check() -> list[str]:
    problems: list[str] = []
    for path in FILES:
        if not path.exists():
            problems.append(f"missing manuscript: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        name = path.name
        exempt = _exempt_spans(text)
        numbers = _headings(text)

        # --- MC9: every reference must be annotated, and point at the right number ---------
        for m in _TAGGED.finditer(text):
            printed, label = m.group(1), m.group(2)
            if label not in SECTION_ALIASES:
                problems.append(f"{name}: unknown cross-reference label «{label}»")
                continue
            actual = numbers.get(label)
            if actual is None:
                problems.append(
                    f"{name}: reference to «{label}» but no heading matches "
                    f"{SECTION_ALIASES[label]} in this file")
            elif actual != printed:
                problems.append(
                    f"{name}: §{printed} is tagged «{label}», but that section is "
                    f"§{actual} in this file -- the printed number is wrong")

        tagged_at = {m.start() for m in _TAGGED.finditer(text)}
        for m in _ANY_REF.finditer(text):
            if m.start() in tagged_at or _in_span(m.start(), exempt):
                continue
            before = text[max(0, m.start() - 9):m.start()]
            if before.endswith("ROADMAP "):        # a reference to another document
                continue
            line = text.count("\n", 0, m.start()) + 1
            problems.append(
                f"{name}:{line}: bare cross-reference §{m.group(1)} -- annotate it as "
                f"§N<!--sec:label--> so the number can be checked")

        # --- MC8: no repository scaffolding in the article ---------------------------------
        for m in _REVIEW_ID.finditer(text):
            if _in_span(m.start(), exempt):
                continue
            line = text.count("\n", 0, m.start()) + 1
            problems.append(f"{name}:{line}: internal review ID «{m.group(0)}» (MC8)")
        for rx, why in _SCAFFOLD:
            for m in rx.finditer(text):
                if _in_span(m.start(), exempt):
                    continue
                line = text.count("\n", 0, m.start()) + 1
                problems.append(f"{name}:{line}: «{m.group(0)}» -- {why}")
    return problems


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    problems = check()
    if argv and argv[0] == "report":
        for path in FILES:
            print(f"{path.name}: sections {_headings(path.read_text(encoding='utf-8'))}")
        print(f"problems: {len(problems)}")
        for p in problems:
            print(f"  - {p}")
        return 0
    if problems:
        print("Paper A cross-reference / scaffolding lint FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("Paper A cross-references resolve and no repository scaffolding remains.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

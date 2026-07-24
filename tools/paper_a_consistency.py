"""Paper A manuscript-consistency verifier (Paper 1 review MC1).

A deterministic, offline check that the venue conversion of Paper A does not silently drift back
to overclaim wording that the **canonical** working draft has already corrected. It encodes the
review's #1 recommendation: choose one canonical source (``docs/PAPER_A_DRAFT.md``) and fail when
the submission conversion (``docs/submission/PAPER_A_JFE_MANUSCRIPT.md``) disagrees with it on
designated load-bearing phrases.

It fails on **objective phrase drift**, never on subjective wording, and it never edits either file.
It is intentionally narrow: a curated list of retired/adopted phrase pairs, not a semantic diff.

Direction of truth: ``PAPER_A_DRAFT.md`` is canonical (decision recorded 2026-07-24,
``docs/paper1_resource/PAPER_1_REVIEW_ACTION_PLAN.md``). The conversion is a synced view.

CLI::

    python tools/paper_a_consistency.py verify     # exit 1 on any drift, listing every problem
    python tools/paper_a_consistency.py report      # human-readable status (exit 0)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
CANONICAL = _REPO / "docs" / "PAPER_A_DRAFT.md"
CONVERSION = _REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"

# Retired overclaim wording: MUST NOT appear in the conversion. Each is also asserted ABSENT from the
# canonical draft (config sanity — the list stays honest: if a phrase re-enters the canonical source
# the tool flags its own config rather than silently passing). Sourced from Paper 1 review MC1/MC8.
BANNED_IN_CONVERSION: list[tuple[str, str]] = [
    ("identifiability ratio", "MC8: metric is a domain-dependent localization contrast, not an identification test → 'profile range ratio'"),
    ("nested reduced-model ladder", "MC7: the comparator models are non-nested and unequally flexible → 'in-sample comparator ladder'"),
    ("frozen-parameter transfer", "MC6: the cross-grind test is not a blind mechanism transfer → 'cross-grind endpoint prediction versus a level-only baseline'"),
    ("essentially nothing", "MC7: 'explains essentially nothing' overstates a descriptive in-sample comparison"),
    ("matched 40 g cups", "MC5: the endpoint is a 40 mL matched-volume proxy for the nominal 40 g cup, not a matched 40 g cup"),
]

# Adopted corrected wording: MUST appear in the conversion (it is present in the canonical draft).
REQUIRED_IN_CONVERSION: list[tuple[str, str]] = [
    ("profile range ratio", "corrected metric name (MC8)"),
    ("conditional one-dimensional intersection band", "corrected Table 7 framing (MC5)"),
    ("in-sample comparator ladder", "corrected comparator framing (MC7)"),
    ("cross-grind endpoint prediction", "corrected Result 3 framing (MC6)"),
    ("40 mL matched-volume", "corrected endpoint framing (MC5)"),
    ("qualitative, not a quantitative rate constraint", "MC5/P0-4: the Table 7 intersection is demoted to qualitative for an undefended unit basis (docs/paper1_resource/PAPER_A_TABLE7_UNITS_AUDIT.md); must not silently re-promote"),
]


def check_paper_a() -> list[str]:
    """Return a list of human-readable consistency problems; empty means the conversion is in sync."""
    problems: list[str] = []
    for path in (CANONICAL, CONVERSION):
        if not path.exists():
            problems.append(f"missing manuscript: {path.relative_to(_REPO)}")
    if problems:
        return problems

    canonical = CANONICAL.read_text(encoding="utf-8").lower()
    conversion = CONVERSION.read_text(encoding="utf-8").lower()

    for phrase, why in BANNED_IN_CONVERSION:
        p = phrase.lower()
        # config sanity: a banned phrase must be genuinely retired (absent from the canonical draft),
        # otherwise the pair is stale and the tool would give false confidence.
        if p in canonical:
            problems.append(f"CONFIG STALE: banned phrase «{phrase}» is present in the canonical draft — update the phrase list ({why})")
        if p in conversion:
            problems.append(f"DRIFT: retired phrase «{phrase}» present in the conversion — {why}")

    for phrase, why in REQUIRED_IN_CONVERSION:
        p = phrase.lower()
        if p not in canonical:
            problems.append(f"CONFIG STALE: required phrase «{phrase}» is absent from the canonical draft — update the phrase list ({why})")
        if p not in conversion:
            problems.append(f"MISSING: corrected phrase «{phrase}» absent from the conversion — {why}")

    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["verify", "report"], nargs="?", default="verify")
    args = parser.parse_args(argv)

    problems = check_paper_a()
    if args.mode == "report":
        print(f"Paper A consistency — canonical: {CANONICAL.relative_to(_REPO)}")
        print(f"                      conversion: {CONVERSION.relative_to(_REPO)}")
        print(f"  banned phrases checked:   {len(BANNED_IN_CONVERSION)}")
        print(f"  required phrases checked: {len(REQUIRED_IN_CONVERSION)}")
        print(f"  problems: {len(problems)}")
        for p in problems:
            print(f"    - {p}")
        return 0

    if problems:
        print("Paper A consistency FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print("Paper A consistency OK (conversion is in sync with the canonical draft).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

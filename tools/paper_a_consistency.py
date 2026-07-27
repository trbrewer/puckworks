"""Paper A submission contract — a multi-file check, not a phrase guard.

Originally (Paper 1 first review MC1) this was a curated list of retired/adopted phrase pairs
between the canonical draft and the venue conversion. The third review (P0-6) found that it passed
while:

* the package used a different title and abstract from the manuscript;
* the manuscript abstract exceeded the venue's word limit;
* the package and manuscript had different keyword lists;
* the cover-letter text quoted the retired title;
* supporting results disagreed over an 18- versus 29-point rate grid;
* the bibliography omitted six cited works;
* the supplement did not exist; and
* the reproducibility manifest was stale and dirty.

None of those are phrase drift, so none were visible to it. It is now a contract over every
submission-facing artefact, composed from the specialised checkers rather than duplicating them:

======================  =========================================================================
front matter            ``tools/paper_a_front_matter.py`` — one title/abstract/keywords/Highlights
citations               ``tools/paper_a_references.py`` — every citation resolves, unambiguously
cross-references        ``tools/paper_a_xref.py`` — section numbers and scaffolding
phrase drift            the original curated pairs, updated to the third review's wording
new here                placeholders, supplementary targets, grid records, figure labels, release
======================  =========================================================================

Two modes, because they answer different questions:

``verify`` (the CI lane)
    Everything that must be true of the *working tree at every commit*. Drift, wording, structure.

``submission`` (the release gate)
    ``verify`` plus the things that can only be true at release time: a clean, fresh reproducibility
    manifest, a minted DOI, resolved author metadata, and the completed endpoint propagation. This
    is expected to fail during development; that is its purpose.

CLI::

    python tools/paper_a_consistency.py verify       # exit 1 on any drift
    python tools/paper_a_consistency.py submission   # + release-state blockers
    python tools/paper_a_consistency.py report       # human-readable status (exit 0)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

CANONICAL = _REPO / "docs" / "PAPER_A_DRAFT.md"
CONVERSION = _REPO / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
PACKAGE = _REPO / "docs" / "submission" / "PAPER_A_JFE_PACKAGE.md"
HIGHLIGHTS = _REPO / "docs" / "submission" / "PAPER_A_JFE_HIGHLIGHTS.txt"
COVER_LETTER = _REPO / "docs" / "submission" / "PAPER_A_JFE_COVER_LETTER.md"
SUPPLEMENT = _REPO / "docs" / "submission" / "PAPER_A_JFE_SUPPLEMENT.md"
MANIFEST = _REPO / "docs" / "reproducibility" / "paper_a_manifest.json"
OBJECTIVE_JSON = _REPO / "docs" / "paper1_resource" / "PAPER_A_OBJECTIVE_FAMILY_PANELS.json"
ENDPOINT_JSON = _REPO / "docs" / "paper1_resource" / "PAPER_A_ENDPOINT_PROPAGATION.json"
P05_NOTES = _REPO / "docs" / "paper1_resource" / "PAPER_A_P0-5_RESULTS.md"

#: Every file a reviewer or editor could receive.
SUBMISSION_FILES = (CONVERSION, PACKAGE, HIGHLIGHTS, COVER_LETTER)

# ── phrase drift (the original check, updated) ────────────────────────────────────────────────
# Retired overclaim wording: MUST NOT appear in the conversion. Each is also asserted ABSENT from
# the canonical draft (config sanity — if a phrase re-enters the canonical source the tool flags
# its own config rather than silently passing).
BANNED_IN_CONVERSION: list[tuple[str, str]] = [
    ("identifiability ratio",
     "metric is a domain-dependent localization contrast, not an identification test"),
    ("nested reduced-model ladder",
     "the comparator models are non-nested and unequally flexible"),
    ("frozen-parameter transfer",
     "the cross-grind test is not a blind mechanism transfer"),
    ("essentially nothing",
     "'explains essentially nothing' overstates a descriptive in-sample comparison"),
    ("matched 40 g cups",
     "the endpoint is a 40 mL volume proxy for a reported 40 +/- 2 g beverage"),
    # --- third review ---
    ("conditional one-dimensional intersection band",
     "third review MC7: the Table 7 assay and the model inventory are not demonstrably "
     "commensurate, so NO intersection band is claimed at all -- this wording re-promotes it"),
    ("independently measured Table 7",
     "third review MC7: use 'orthogonal same-campaign inventory assay'; 'independently measured' "
     "reads as an independent campaign"),
    ("to good approximation, `C_cup",
     "third review MC2: inventory factorises EXACTLY; it is the cross-condition compensation "
     "that is approximate"),
    ("almost always performed",
     "third review MC9: unsupported categorical claim -- use 'commonly'"),
    ("95 % resampling interval",
     "third review MC5: the fixed-predictor result is a clustered percentile sensitivity range, "
     "not a calibrated confidence interval"),
    ("always constrains the rate",
     "third review MC6: overstates a 1.19-1.30 boundary-censored result under the shape loss"),
    ("the repo's internal labels",
     "third review MC8: repository-facing vocabulary in the article"),
]

# Adopted corrected wording: MUST appear in the conversion (and in the canonical draft).
REQUIRED_IN_CONVERSION: list[tuple[str, str]] = [
    ("profile range ratio", "corrected metric name"),
    ("in-sample comparator ladder", "corrected comparator framing"),
    ("cross-grind endpoint prediction", "corrected Result 3 framing"),
    # --- third review ---
    ("not demonstrably commensurate",
     "MC7: the Table 7 discussion must LEAD with non-commensurability"),
    ("orthogonal same-campaign inventory assay",
     "MC7: the standing name for the Table 7 assay"),
    ("no quantitative rate intersection is claimed",
     "MC7: the withdrawal must be explicit, not implied"),
    ("This is not an approximation and does not depend on the design",
     "MC2: the exact multiplicative-level result must be stated AS exact, distinct from the "
     "approximate cross-condition compensation"),
    ("mass-transfer-rate multiplier",
     "MC10: the operational definition of the estimated rate parameter"),
    ("clustered percentile sensitivity range",
     "MC5: the non-calibrated name for the fixed-predictor resampling result"),
    ("Sauter (surface-weighted) mean diameter",
     "MC4.1: d32 must be defined"),
    ("as a percentage of the mean observation",
     "MC4.6: the normalised-RMSE denominator must be stated"),
]

#: Placeholders that must not survive into a submission-facing file.
_PLACEHOLDER = re.compile(r"\[insert[^\]]*\]|\[TODO[^\]]*\]|\bTBD\b|\bXXX\b", re.I)

#: Repository/process vocabulary that must not appear in submission-facing files.
_PROCESS_WORDS = [
    (re.compile(r"\bPI actions?\b", re.I), "repository process language"),
    (re.compile(r"\bstill owed\b|\bremains owed\b|\bis owed\b", re.I), "backlog language"),
    (re.compile(r"\bdeferred\b", re.I), "project-management state"),
    (re.compile(r"\b(?:MC\d+|P0-\d+|P1-\d+|MAJ-\d+)\b"), "internal review ticket ID"),
]


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.exists() else ""


def _flat(s: str) -> str:
    """Collapse whitespace so a phrase check is not defeated by Markdown line wrapping.

    Both manuscripts are hard-wrapped, so a required phrase straddling a newline was reported as
    absent while being present in the rendered text.
    """
    return " ".join(s.split()).lower()


# ── the checks ────────────────────────────────────────────────────────────────────────────────
def _phrase_drift() -> list[str]:
    problems: list[str] = []
    canonical, conversion = _flat(_read(CANONICAL)), _flat(_read(CONVERSION))
    if not canonical or not conversion:
        return ["missing a Paper A manuscript"]
    for phrase, why in BANNED_IN_CONVERSION:
        p = _flat(phrase)
        if p in canonical:
            problems.append(
                f"CONFIG STALE: banned phrase <<{phrase}>> is in the canonical draft ({why})")
        if p in conversion:
            problems.append(f"DRIFT: retired phrase <<{phrase}>> in the conversion -- {why}")
    for phrase, why in REQUIRED_IN_CONVERSION:
        p = _flat(phrase)
        if p not in canonical:
            problems.append(
                f"CONFIG STALE: required phrase <<{phrase}>> absent from the canonical draft ({why})")
        if p not in conversion:
            problems.append(f"MISSING: corrected phrase <<{phrase}>> absent from the conversion -- {why}")
    return problems


def _front_matter() -> list[str]:
    from tools import paper_a_front_matter as FM
    return [f"front matter: {p}" for p in FM.check(FM.load())]


def _citations() -> list[str]:
    from tools import paper_a_references as REF
    out = []
    for path in (CANONICAL, CONVERSION):
        _used, missing = REF.resolve(_read(path))
        out += [f"{path.name}: citation <<{s} {y}>> resolves to no bib entry" for s, y in missing]
        out += [f"{path.name}: citation <<{s} {y}>> is ambiguous between {list(k)}"
                for s, y, k in REF.resolve.last_ambiguous]
    return out


def _cross_references() -> list[str]:
    from tools import paper_a_xref as X
    return X.check()


def _placeholders_and_process_language() -> list[str]:
    problems = []
    for path in SUBMISSION_FILES:
        text = _read(path)
        for m in _PLACEHOLDER.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            problems.append(f"{path.name}:{line}: unresolved placeholder <<{m.group(0)}>>")
        for rx, why in _PROCESS_WORDS:
            for m in rx.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                problems.append(f"{path.name}:{line}: <<{m.group(0)}>> -- {why}")
    return problems


def _supplementary_targets() -> list[str]:
    """Every "Supplementary X" the article promises must exist as a numbered item.

    Third review P0-3: the main text repeatedly said material was "reported in the supplement"
    while the submission directory contained no supplement at all.
    """
    text = _read(CONVERSION)
    promised = set(re.findall(
        r"Supplementary\s+(?:Table|Figure|Note|Method)s?\s+(S\d+)", text))
    if not promised:
        return []
    if not SUPPLEMENT.exists():
        return [f"the article cites {len(promised)} supplementary items "
                f"({', '.join(sorted(promised))}) but no supplement exists at "
                f"{SUPPLEMENT.name}"]
    supp = _read(SUPPLEMENT)
    declared = set(re.findall(
        r"(?m)^#{2,4}\s+(?:Supplementary\s+)?(?:Table|Figure|Note|Method)s?\s+(S\d+)", supp))
    return [f"the article cites Supplementary {m} but the supplement does not define it"
            for m in sorted(promised - declared)]


def _grid_record() -> list[str]:
    """The rate-grid count and domain must agree across the JSON, the notes and the manuscript."""
    if not OBJECTIVE_JSON.exists():
        return ["objective-family JSON is missing"]
    rec = json.loads(_read(OBJECTIVE_JSON))
    n, domain = rec["n_rate_grid"], tuple(rec["rate_domain"])
    problems = []
    for name, panel in rec["panels"].items():
        if panel["n_rate_grid"] != n or tuple(panel["rate_domain"]) != domain:
            problems.append(f"objective-family panel <<{name}>> disagrees with the record grid")
    notes = _read(P05_NOTES)
    if notes and not re.search(rf"\*\*{n}\*\*\s*\n?points", notes):
        problems.append(f"the P0-5 results note does not state the {n}-point objective-family grid")
    if f"**{n}** points for the" not in _read(CONVERSION):
        problems.append(f"the manuscript does not state the {n}-point objective-family grid")
    return problems


def _figure_labels() -> list[str]:
    """Figures must not carry embedded "Fig N" titles that can contradict presentation numbering."""
    captions = _REPO / "docs" / "figures" / "PAPER_A_CAPTIONS.md"
    if not captions.exists():
        return []
    return ([] if "no embedded figure number" in _read(captions).lower() else
            ["the caption map does not record that figures carry no embedded 'Fig N' title "
             "(third review, cross-cutting figure issue)"])


def _release_state() -> list[str]:
    """Release-time only. Expected to fail during development; that is its purpose."""
    problems = []
    if not MANIFEST.exists():
        return ["no reproducibility manifest"]
    m = json.loads(_read(MANIFEST))
    if m.get("git_dirty"):
        problems.append("reproducibility manifest reports git_dirty=true")
    if not m.get("bundle_matches_head"):
        problems.append("reproducibility manifest reports bundle_matches_head=false")
    if not m.get("release_fresh"):
        problems.append("reproducibility manifest reports release_fresh=false")
    if not m.get("timestamp_utc"):
        problems.append("reproducibility manifest has no generation timestamp")

    from tools import paper_a_front_matter as FM
    problems += [f"unresolved submission metadata: {g}" for g in FM.submission_gaps(FM.load())]

    # The endpoint propagation must be ARCHIVED, not merely described. Checking for the artefact
    # rather than for a phrase is the difference between a gate and a spell-checker.
    if not ENDPOINT_JSON.exists():
        problems.append("the 38/40/42 mL endpoint propagation has not been run and archived")
    else:
        ep = json.loads(_read(ENDPOINT_JSON))
        if sorted(ep.get("v_targets", [])) != [38.0, 40.0, 42.0]:
            problems.append("the endpoint propagation does not cover 38/40/42 mL")
        if "reading" not in ep:
            problems.append("the endpoint propagation carries no recorded reading")
        # If the sweep showed the conclusion is NOT endpoint-invariant, the manuscript must say so
        # rather than reporting robustness the sweep does not support.
        if not ep.get("conclusion_stable") and \
                "not endpoint-invariant" not in _flat(_read(CONVERSION)):
            problems.append("the endpoint sweep did not find a stable conclusion, but the "
                            "manuscript does not report the dependence")
    return problems


CHECKS = (
    ("phrase drift", _phrase_drift),
    ("front matter", _front_matter),
    ("citations", _citations),
    ("cross-references", _cross_references),
    ("placeholders / process language", _placeholders_and_process_language),
    ("supplementary targets", _supplementary_targets),
    ("grid record", _grid_record),
    ("figure labels", _figure_labels),
)


def check_paper_a(include_release: bool = False) -> list[str]:
    problems: list[str] = []
    for _name, fn in CHECKS:
        problems += fn()
    if include_release:
        problems += _release_state()
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Paper A submission contract")
    parser.add_argument("mode", choices=["verify", "submission", "report"],
                        nargs="?", default="verify")
    args = parser.parse_args(argv)

    if args.mode == "report":
        print(f"Paper A submission contract -- canonical: {CANONICAL.relative_to(_REPO)}")
        total = 0
        for name, fn in CHECKS:
            found = fn()
            total += len(found)
            print(f"  {name:34s} {'OK' if not found else str(len(found)) + ' problem(s)'}")
            for p in found:
                print(f"      - {p}")
        rel = _release_state()
        label = "OK" if not rel else f"{len(rel)} blocker(s)"
        print(f"  {'release state (submission only)':34s} {label}")
        for p in rel:
            print(f"      - {p}")
        print(f"  drift problems: {total}; release blockers: {len(rel)}")
        return 0

    problems = check_paper_a(include_release=args.mode == "submission")
    if problems:
        print(f"Paper A submission contract FAILED ({args.mode}):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 1
    print(f"Paper A submission contract OK ({args.mode}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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
    Everything that must be true of the *working tree at every commit*. Drift, wording, structure —
    and, since round-8 P0-3, every SCIENCE contract, including the collected-mass endpoint schema.

``submission`` (the release gate)
    A strict superset of ``verify``, adding only what can be true exclusively at release time: a
    clean, fresh reproducibility manifest, a minted DOI and resolved author metadata. This is
    expected to fail during development; that is its purpose.

The split matters. The endpoint contract used to live in ``submission`` alone, where it looked for
a key the artefact had not carried since the round-7 unit correction. Because the command anyone
actually runs is ``verify``, a broken release gate and a green development lane coexisted for a
whole review round. **No scientific check may live only in the release mode**: if a contract can
be checked against the working tree, it belongs in ``verify``, and ``submission`` adds metadata
and freshness on top rather than holding science hostage to an unminted DOI.

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

#: Repository-facing figure bookkeeping: producer stems, numbering rationale, review history, test
#: paths. NOT a submission file, and deliberately not scanned — it is allowed to contain exactly the
#: things the scanner keeps out of the paper. The upload-ready captions are generated from it.
FIGURE_MAP_INTERNAL = _REPO / "docs" / "figures" / "PAPER_A_FIGURE_MAP_INTERNAL.md"
UPLOAD_CAPTIONS = _REPO / "docs" / "submission" / "PAPER_A_JFE_FIGURE_CAPTIONS.md"

#: Every file a reviewer or editor could receive.
#:
#: Round-9 P2-1: this tuple described itself that way while omitting the supplement and the
#: separately supplied caption file — both of which go to the journal, and both of which were
#: carrying reader-facing process language nobody was scanning.
#:
#: Round-10 P2-1: the caption entry pointed at a file titled "submission-ready figure captions" whose
#: first three paragraphs were review and test narration. The scanner was looking at the right file
#: for the wrong reason — that file is the internal map. It is replaced here by the generated
#: upload-ready caption file, which is what the package manifest lists.
SUBMISSION_FILES = (CONVERSION, PACKAGE, HIGHLIGHTS, COVER_LETTER, SUPPLEMENT, UPLOAD_CAPTIONS)


def prose_scanned_files() -> tuple:
    """Every submission file, plus the canonical draft.

    The draft is not submitted, but it is the file the claim-coverage audit defaults to and the file
    a reviewer is pointed at, and the round-9 remediation plan asked for its inclusion explicitly.

    A function rather than a constant so that a test which redirects ``SUBMISSION_FILES`` and
    ``CANONICAL`` at temporary copies redirects the scanner too. A module-level tuple computed at
    import time silently kept reading the real tree, which would have made the non-vacuity tests
    assert against files the test had not modified.
    """
    return tuple(SUBMISSION_FILES) + (CANONICAL,)


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
    # Round-7 P0-2 INVERTS the previous rule here. "matched 40 g cups" used to be banned on the
    # grounds that the endpoint was a volume proxy; the solver-contract audit settled that the
    # stopping rule is a mass one, so the volume vocabulary is what must not appear.
    ("matched-volume proxy",
     "round-7 P0-2: the endpoint is a matched COLLECTED MASS -- t_end = M_target / Q with the "
     "source flow consumed in g/s. There is no volume proxy"),
    ("40 mL",
     "round-7 P0-2: the endpoint is 40 g, not 40 mL; the token '40' is identical either way, "
     "which is exactly why this needs a phrase check rather than a numeral check"),
    ("mass-to-volume substitution",
     "round-7 P0-2: retired narrative -- nothing is substituted; the source's own flow column "
     "carries the residual labelling ambiguity, and that is stated directly"),
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
    # --- round 11 P0-1 ---
    # `claim_policy` catches these as a CLASS, derived from the declared inferential status. They are
    # pinned here as literal strings too, and deliberately: round 11 found the round-10 verdict back
    # in the manuscript by paraphrase, so the exact wording that shipped gets a second, dumber
    # authority that cannot be argued with. This list also asserts absence from the canonical draft,
    # which is how the two files are held together on authored (ungenerated) narrative.
    ("adding little to a baseline",
     "round-11 P0-1: a practical-negligibility verdict. The analysis has no calibrated coverage and "
     "no predeclared margin, so it cannot decide that the increment is too small to matter"),
    ("adds little",
     "round-11 P0-1: same verdict, shorter. Report the observed difference and its sign"),
    ("incremental skill over a level-only comparator is small",
     "round-11 P0-1: 'small' is a decision against a margin that was never declared"),
    ("incremental skill over a level-only baseline is small",
     "round-11 P0-1: the strength-ladder rendering of the same verdict"),
    ("nearly matched by an O-trained level-only constant",
     "round-11 P0-1: an equivalence-adjacent verdict; give 8.44 % against 8.83 % and the "
     "−0.394 pp difference instead"),
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
    # --- round 11 P0-1: the replacements, asserted PRESENT in both files ---
    # The authored (ungenerated) paragraphs the P0 correction rewrote have no generated-block parity
    # to hold them together, so the corrected wording is required in both the canonical draft and the
    # venue conversion. Removing the caveat from one file alone now fails.
    ("does not determine whether that observed advantage is reproducible or practically useful",
     "round-11 P0-1: the Introduction must state the decision boundary where it states the contrast"),
    ("does not establish equivalence or absence of incremental value",
     "round-11 P0-1: non-establishment has to be SYMMETRICAL — the standing position must rule out "
     "an absence/equivalence reading as explicitly as a superiority one"),
    ("−0.394 pp of pooled MAPE",
     "round-11 P0-1: the observed contrast replaces the magnitude adjective, and must stay "
     "prominent in §6"),
]

#: Placeholders that must not survive into a submission-facing file.
_PLACEHOLDER = re.compile(r"\[insert[^\]]*\]|\[TODO[^\]]*\]|\bTBD\b|\bXXX\b", re.I)

#: Repository/process vocabulary that must not appear in submission-facing files.
#:
#: Each entry is ``(pattern, why, rule_id)``. The rule id names the class in the diagnostic and is
#: what the internal-path allowance is keyed on — a rule that could only be identified by matching
#: its human-readable reason string was a bug waiting to happen.
_PROCESS_WORDS = [
    (re.compile(r"\bPI actions?\b", re.I), "repository process language", "process_vocabulary"),
    (re.compile(r"\bstill owed\b|\bremains owed\b|\bis owed\b", re.I), "backlog language",
     "process_vocabulary"),
    (re.compile(r"\bdeferred\b", re.I), "project-management state", "process_vocabulary"),
    (re.compile(r"\b(?:MC\d+|P0-\d+|P1-\d+|P2-\d+|MAJ-\d+)\b"), "internal review ticket ID",
     "review_history"),
    # Round-9 P2-1. A journal reader should not be made to read our changelog. Each of these was
    # found in reader-facing analysis, Results or supplement prose at the round-9 target commit.
    (re.compile(r"\bearlier draft\b|\bprevious draft\b|\ban earlier version\b", re.I),
     "draft-history narration", "review_history"),
    (re.compile(r"\bround-\d+\b", re.I), "review-round identifier", "review_history"),
    # Round-10 P2-1: the "submission-ready" caption file opened with "The second review asked for
    # four to five main figures" and "The rendered images previously carried their producer number",
    # and the manuscript still said an earlier version of a paragraph "was wrong".
    (re.compile(r"\b(?:the\s+)?(?:first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|"
                r"tenth|next|previous|last)\s+review\b", re.I),
     "review-history narration", "review_history"),
    (re.compile(r"\breview(?:er)?s?\s+(?:asked|requested|required|noted|found|objected)\b", re.I),
     "review-history narration", "review_history"),
    (re.compile(r"\bthat was wrong\b|\bwe corrected\b|\bwas corrected in\b|\bthis corrects\b",
                re.I),
     "correction narration; state the current fact, not the history of the draft",
     "review_history"),
    (re.compile(r"\bpreviously carried\b|\bused to (?:say|read|carry|state)\b", re.I),
     "draft-history narration", "review_history"),
    (re.compile(r"\balready in (?:the )?repo\b|\bin the repository\b", re.I),
     "repository-location narration", "internal_narration"),
    (re.compile(r"\bcannot disagree\b|\bgenerated from the archived\b", re.I),
     "generator self-description", "internal_narration"),
    # Producer/module/test identifiers. `fig4_transfer` is presentation Figure 3: the identifier is
    # internal bookkeeping and naming it in a caption tells a reader nothing they can use.
    (re.compile(r"\bfig\d+_[a-z_]+\b"), "figure producer identifier", "internal_narration"),
    (re.compile(r"\bproducer identifiers?\b|\bfile stems?\b", re.I),
     "figure-production bookkeeping", "internal_narration"),
    # Internal paths, all five prefixes the prior remediation plan asked for, back-ticked or bare.
    (re.compile(r"`?\b(?:docs|tools|tests|puckworks)/[\w./-]+`?"), "internal repository path",
     "internal_path"),
    (re.compile(r"`?\.github/[\w./-]+`?"), "internal repository path", "internal_path"),
]

#: The ONE narrow path exemption, and it is not a section.
#:
#: Round-11 P1-6. This used to be fourteen whole SECTIONS — including "data availability",
#: "reproducibility" and "figure captions" — inside which any repository path was legal. That is far
#: wider than the thing it exists for: at the reviewed commit every path in an upload deliverable was
#: in an unsupplied-metadata placeholder, and those blocks are stripped before submission (they are
#: the out-of-scope material the round-11 brief names). Exempting the surrounding section as well
#: meant a genuine leak in the availability statement would have been legal.
#:
#: So the exemption is keyed to the PLACEHOLDER, structurally: a block that announces itself as
#: not-yet-supplied may name the field and file the missing metadata is tracked in. Nothing else may.
_UNSUPPLIED_METADATA = re.compile(
    r"\bnot\s+yet\s+(?:supplied|minted|filled\s+in)\b"
    r"|\bthis\s+letter\s+is\s+not\s+ready\s+to\s+send\b"
    r"|\bis\s+unset\s+in\b", re.I)

#: Submitted figure filenames and public deposit links, which a caption or an availability statement
#: legitimately names. Narrow by construction: an exact filename shape, and an absolute public URL.
_ALLOWED_TARGETS = (
    re.compile(r"^(?:\./)?figures/[A-Za-z0-9_-]+\.(?:png|pdf|svg|eps|tif|tiff)$"),
    re.compile(r"^https://(?:doi\.org|zenodo\.org|dx\.doi\.org)/[\w./-]+$"),
)

#: Files whose SUBMISSION ROLE requires repository paths, and why. Everything else that is actually
#: uploaded is scanned. Round-11 P1-6: the path rule used to apply to the manuscript and supplement
#: only, while the cover letter, the Highlights file and the standalone captions all go to the
#: journal too — an internal path in any of them is still a leak.
_PATH_EXEMPT_FILES = {
    "PAPER_A_JFE_PACKAGE.md":
        "an assembly instruction sheet whose file table is the content; never uploaded as science",
    "PAPER_A_DRAFT.md":
        "the repository-facing working draft, which carries a strip-before-submission banner and a "
        "producer-to-figure mapping table; it is not an upload deliverable",
}

#: Every true upload deliverable, plus the canonical draft, minus the documented exemptions above.
_PATH_SCANNED_FILES = tuple(
    p.name for p in (CONVERSION, PACKAGE, HIGHLIGHTS, COVER_LETTER, SUPPLEMENT, UPLOAD_CAPTIONS,
                     CANONICAL)
    if p.name not in _PATH_EXEMPT_FILES)

#: Which files each rule CLASS applies to. Stated as data because the alternative — one flat rule
#: list over one flat file list — forces a choice between false positives and silence:
#:
#: * ``internal_path`` and ``internal_narration`` are about a READER seeing our repository. They
#:   apply to the two documents an editor receives as science. The package is an assembly
#:   instruction sheet whose whole purpose is to name repository files; the canonical draft carries a
#:   strip-before-submission banner and a producer→figure mapping table for the same reason. Scanning
#:   either for repository vocabulary would demand deleting the content they exist to hold.
#: * ``review_history`` applies more widely, including the canonical draft: round-10 P1-1 found the
#:   draft's ACTIVE abstract narrating the correction of an earlier version, and that is a scientific
#:   claim surface regardless of which file it lives in. The package is exempt for the reason above —
#:   its preamble explains why its front matter is generated, which is repository documentation.
#: * ``process_vocabulary`` applies to everything reader-facing.
_RULE_SCOPE = {
    "process_vocabulary": tuple(p.name for p in SUBMISSION_FILES),
    "review_history": tuple(p.name for p in SUBMISSION_FILES if p != PACKAGE)
                      + (CANONICAL.name,),
    "internal_narration": _PATH_SCANNED_FILES,
    "internal_path": _PATH_SCANNED_FILES,
}


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


def _generated_block_parity() -> list[str]:
    """The generated scientific blocks must be IDENTICAL in the canonical draft and the conversion.

    Round-10 P1-1. `_phrase_drift()` below tests a curated list of required and banned phrases and
    is described, in this module's own docstring and in the review brief, as holding the two
    manuscripts "in content agreement". It does not: at the round-10 target commit the two abstracts
    made materially different central claims and every phrase on the list matched anyway.

    A curated phrase list can only find the drift someone already thought of. This check is
    structural instead — for every block the generator writes into BOTH files, the rendered text must
    match after whitespace normalisation. Whitespace is normalised because the two files are wrapped
    differently; nothing else is, so a changed sign, a dropped negation or a lost caveat fails.
    """
    from tools import paper_a_front_matter as FMB
    from tools import paper_a_transfer_text as TT

    problems: list[str] = []
    shared = {name: paths for name, (_fn, paths) in TT.BLOCKS.items()
              if TT.MANUSCRIPT in paths and TT.DRAFT in paths}
    if not shared:
        return ["no generated block targets both manuscripts; the parity contract has nothing to "
                "compare, which means the two files are no longer bound to one source"]

    canonical, conversion = _read(CANONICAL), _read(CONVERSION)
    for name in sorted(shared):
        try:
            a = _flat(TT.extract_block(canonical, name))
            b = _flat(TT.extract_block(conversion, name))
        except KeyError as exc:
            problems.append("generated block %r: %s" % (name, exc))
            continue
        if a != b:
            problems.append(
                "generated block %r differs between the canonical draft and the conversion; the "
                "two manuscripts are not rendering the same scientific text (regenerate with "
                "`python tools/paper_a_transfer_text.py --write`)" % name)

    # The abstract is front matter, not a transfer block, and it is the specific pair the round-10
    # review found disagreeing.
    #
    # It is compared in TWO steps, because the second needs pyyaml and the first does not. That split
    # is deliberate: the minimum-dependency lane has no pyyaml, and the first version of this check
    # returned early there — so a canonical abstract mutated to say "an incremental skill of ≈4.5 %
    # relative", the exact round-10 defect, passed on that lane. A check that cannot run must not
    # look like a check that ran and found nothing.
    rendered = {}
    for label, text, transform in (("canonical", canonical, lambda s: s),
                                   ("conversion", conversion, lambda s: s),
                                   ("package", _read(PACKAGE),
                                    lambda s: s.split("\n\n", 1)[-1])):
        try:
            rendered[label] = transform(FMB.block(text, "abstract"))
        except (KeyError, IndexError):
            problems.append("the %s abstract is not a generated block; it is not bound to the one "
                            "front-matter source" % label)

    # Step 1, always: the renderings must agree with EACH OTHER. This needs no YAML parser, and it is
    # what catches two active manuscripts carrying different central claims.
    if len(rendered) > 1:
        reference_label = "conversion" if "conversion" in rendered else sorted(rendered)[0]
        reference = _flat(rendered[reference_label])
        for label, got in sorted(rendered.items()):
            if label != reference_label and _flat(got) != reference:
                problems.append("the %s abstract differs from the %s abstract; two active "
                                "manuscripts must not carry different central claims"
                                % (label, reference_label))

    # Step 2, where the environment allows: they must agree with the SOURCE, not merely with one
    # another — three identical copies of a hand-edited abstract would satisfy step 1.
    global abstract_source_unavailable
    abstract_source_unavailable = None
    try:
        fm = FMB.load()
    except ImportError as exc:
        abstract_source_unavailable = (
            "pyyaml unavailable (%s); the abstract was compared across renderings but NOT against "
            "docs/submission/paper_a_front_matter.yaml" % exc)
        return problems
    want = _flat(FMB._one_line(fm["abstract"]))
    for label, got in sorted(rendered.items()):
        if _flat(got) != want:
            problems.append("the %s abstract is not the one source's abstract; regenerate with "
                            "`python tools/paper_a_front_matter.py --write`" % label)
    return problems


def _claim_policy() -> list[str]:
    """No reader-facing surface may make a decision the declared analysis cannot make.

    Round-10 P0-1, the submission blocker. The paper said its ranges have no calibrated coverage and
    support no distinguishability, non-distinguishability or equivalence claim — and then concluded,
    on six surfaces, that the model supplied "no resolvable skill". That is a decision about absence,
    and the analysis makes no decision in either direction.

    The rule is derived from the artefact's own declared `inferential_status`, so this is not a
    banned-word list that a future calibrated analysis would have to fight: declare the decision in
    the status object, and the corresponding phrase class unlocks. Explicit disclaimers are
    recognised, because a paper must be able to say what it is NOT claiming.

    The positive half is checked too. Prohibiting the verdict is not enough if a surface then says
    nothing about the limits of its evidence, so each named surface must carry the propositions
    `claim_policy.SURFACE_ASSERTIONS` requires of it.
    """
    from puckworks.paper_a import claim_policy as CP
    from tools import paper_a_transfer_text as TT

    if not ENDPOINT_JSON.exists():
        return ["the endpoint artefact is missing, so the analysis's inferential status is unknown "
                "and no claim can be checked against it"]
    ep = json.loads(_read(ENDPOINT_JSON))
    try:
        estimand, status = TT.validated_analysis(ep)
    except (KeyError, ValueError) as exc:
        return ["the endpoint artefact does not declare a usable inferential status: %s" % exc]

    problems: list[str] = []
    # Every reader-facing file, plus the canonical draft and the front-matter source that generates
    # four of them. Scanning only the rendered files would let a template regenerate the retired
    # verdict later.
    for path in prose_scanned_files():
        if not path.exists():
            continue
        for line_no, para in _visible_paragraphs(_read(path)):
            problems += ["%s:%d: %s" % (path.name, line_no, p)
                         for p in CP.scan(para, status)]

    try:
        from tools import paper_a_front_matter as FMB
        fm = FMB.load()
    except ImportError:
        fm = None
    if fm is not None:
        for field in ("abstract", "editor_significance", "title", "running_title"):
            problems += CP.scan(str(fm[field]), status, "paper_a_front_matter.yaml:%s" % field)
        for i, highlight in enumerate(fm["highlights"], 1):
            problems += CP.scan(str(highlight), status,
                                "paper_a_front_matter.yaml:highlights[%d]" % i)
        problems += CP.missing_assertions(FMB._one_line(fm["abstract"]), "abstract")
        problems += CP.missing_assertions(FMB._one_line(fm["editor_significance"]),
                                          "editor_significance")

    # The propositions each surface must carry.
    #
    # Round-11 P1-3 added the two STANDALONE upload files. Both are read without the paragraphs that
    # supply the limits, so both must carry the evidence boundary themselves — and neither was
    # governed by the positive half of the policy at all.
    for surface, source in (("cover_letter", _read(COVER_LETTER)),
                            ("conclusion", _section(_read(CONVERSION), "## 8. Conclusions")),
                            ("highlights", _read(HIGHLIGHTS)),
                            ("figure3_caption", _upload_caption(3))):
        problems += CP.missing_assertions(source, surface)
    for surface, name, path in (("results_headline", "paper-a:transfer-headline", CONVERSION),
                                ("endpoint_synthesis", "paper-a:transfer-endpoint-reading",
                                 CONVERSION),
                                ("supplement_reading", "paper-a:transfer-endpoint-table-supp",
                                 SUPPLEMENT)):
        try:
            block = TT.extract_block(_read(path), name)
        except KeyError as exc:
            problems.append("%s: %s" % (surface, exc))
            continue
        problems += CP.missing_assertions(block, surface)

    # The estimand's direction must be stated wherever the sign is load-bearing, and stated the way
    # the artefact declares it — not in a hand-written paraphrase that a reversed estimand would
    # leave untouched.
    if _flat(estimand.direction_clause) not in _flat(_read(CONVERSION)):
        problems.append("the conversion does not state the artefact's declared sign convention "
                        "(%r); a reader cannot tell which arm a negative difference favours"
                        % estimand.direction_clause)
    return problems


def _upload_caption(number) -> str:
    """One caption from the GENERATED upload file, addressed by its exact label.

    Round-11 P1-3 asks for Figure 3's caption to be a governed claim surface, which needs an
    extractor that cannot silently audit the wrong paragraph. Matching is on the exact
    ``**Figure 3.`` label at the start of a block, so ``Figure S3`` — a different figure with a
    similar name, in the same file — can never be mistaken for it, and a missing caption returns a
    NAMED problem rather than an empty string that would satisfy nothing and be reported as nothing.
    """
    label = "**Figure %s." % number
    for block in _read(UPLOAD_CAPTIONS).split("\n\n"):
        block = block.strip()
        if block.startswith(label):
            return block
    return ("MISSING: the upload-ready caption file carries no `%s` caption, so its claim coverage "
            "cannot be checked" % label)


def _section(text: str, heading: str) -> str:
    """The body of one `##` section, by exact heading. Empty string if it is absent."""
    if heading not in text:
        return ""
    after = text.split(heading, 1)[1]
    return after.split("\n## ", 1)[0]


#: Set when the front-matter check could not run for an ENVIRONMENT reason (not a drift).
front_matter_unavailable = None

#: Set when the abstract could be compared across renderings but not against its YAML source.
abstract_source_unavailable = None


def _front_matter() -> list[str]:
    """Front-matter drift, if this environment can parse the YAML source.

    pyyaml is a radar/dev extra. On the minimum-dependency lane it is absent, and this check
    genuinely cannot run there. That is an environment limitation, NOT evidence of drift, so it is
    RECORDED rather than reported as a failure -- reporting it as drift would make a lane that
    cannot look claim to have found something. `report` mode prints the reason, and
    `tests/test_paper_a_submission_contract.py` covers the check itself on lanes that have pyyaml.
    """
    global front_matter_unavailable
    front_matter_unavailable = None
    try:
        from tools import paper_a_front_matter as FM
        fm = FM.load()
    except ImportError as exc:
        front_matter_unavailable = f"pyyaml unavailable ({exc}); front-matter check not run"
        return []
    return [f"front matter: {p}" for p in FM.check(fm)]


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


def _strip_html_comments(text: str) -> str:
    """Blank out HTML comments while preserving every line break and every character position.

    Comment characters become spaces rather than disappearing, so a diagnostic can still name the
    source line a problem is on. HTML comments are excluded from reader-facing checks because the
    generated blocks carry schema/manifest stamps that are assurance devices, not prose — but the
    journal conversion must strip them too, which is a separate check on the built package.
    """
    out, in_comment, i = [], False, 0
    while i < len(text):
        if not in_comment and text.startswith("<!--", i):
            in_comment, i = True, i + 4
            out.append("    ")
            continue
        if in_comment and text.startswith("-->", i):
            in_comment, i = False, i + 3
            out.append("   ")
            continue
        ch = text[i]
        out.append(ch if (ch == "\n" or not in_comment) else " ")
        i += 1
    return "".join(out)


# ── structural Markdown scanning (round-11 P1-6) ─────────────────────────────────────────────
#
# The predecessor called itself "what a reader sees" and was two regexes: replace `[text](target)`
# with `text`, then collapse whitespace. It therefore did not see through the most ordinary markup
# in the language, and every one of these passed at the reviewed commit:
#
#     An earlier **version** was wrong.          -> not caught
#     An earlier <em>version</em> was wrong.     -> not caught
#     An earlier ver**sion** was wrong.          -> not caught
#     An earlier&nbsp;version was wrong.         -> not caught
#     See [the internal analysis](docs/internal/review.md).  -> not caught
#
# The first four are the same defect as round-10 P2-1 (a phrase invisible to the scanner and plainly
# visible on the page), one level down. The last is different in kind: discarding link TARGETS is
# right for prose semantics — the SI's own figure filenames are not leaked identifiers — and wrong
# for leakage, because the target stays in the submitted source and surfaces in conversion,
# accessibility metadata and editor inspection.
#
# So: parse properly, and scan two channels. Text a reader sees, and destinations a reader does not.
try:
    from markdown_it import MarkdownIt

    _MD = MarkdownIt("commonmark").enable("table").enable("strikethrough")
except ImportError:                                             # pragma: no cover - env-dependent
    _MD = None

#: Set when the structural parser is absent. A check that CANNOT run must not look like a check that
#: ran and found nothing — round-10 found exactly that shape in the abstract comparison, so this is
#: reported AND returned as a blocking problem rather than recorded and skipped.
structural_parser_unavailable = None

_HTML_TAG = re.compile(r"<[^>]*>")
_HTML_TARGET = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)


def _parser_problem() -> list[str]:
    global structural_parser_unavailable
    if _MD is not None:
        structural_parser_unavailable = None
        return []
    structural_parser_unavailable = (
        "markdown-it-py is not installed, so submission files were NOT structurally scanned; "
        "install the `submission` extra (`pip install -e \".[submission]\"`)")
    return ["SCAN NOT RUN: " + structural_parser_unavailable]


def _inline_visible(token) -> str:
    """Concatenate an inline token's children into the text a reader sees.

    Adjacent text nodes are joined with NO separator, which is the whole point: CommonMark splits
    ``ver**sion**`` into the text ``ver``, a strong-open, and the text ``sion``, and a reader sees
    one word. Emphasis and inline-code delimiters disappear because they are markers, not content;
    inline HTML has its tags removed but its text kept; image alt text is kept because a reader of
    the rendered document gets it.
    """
    out = []
    for child in token.children or []:
        if child.type in ("text", "code_inline"):
            out.append(child.content)
        elif child.type in ("html_inline", "html_block"):
            out.append(_HTML_TAG.sub("", child.content))
        elif child.type == "image":
            out.append(child.attrGet("alt") or "")
            if child.children:
                out.append(_inline_visible(child))
        elif child.type in ("softbreak", "hardbreak"):
            out.append(" ")
    return "".join(out)


#: Characters that are invisible on the page and split a word for a regular expression.
#:
#: Found by a self-check AFTER the round-11 remediation merged: a soft hyphen inside "version"
#: renders as "version" and did not match `\ban earlier version\b`. Zero-width space, zero-width
#: non-joiner/joiner, word joiner, soft hyphen and the BOM are all removed before matching, because
#: a reader cannot see any of them and a rule should not be defeated by one.
_INVISIBLE = dict.fromkeys(
    [0x200B, 0x200C, 0x200D, 0x2060, 0x00AD, 0xFEFF], None)


def _normalise_visible(text: str) -> str:
    """One space between words, ordinary punctuation, no residual or invisible markers.

    ``&nbsp;`` arrives from the parser as U+00A0, which is not matched by ``\\s`` in a rule written
    with a plain space \u2014 the same bypass class as the line wrap, two levels down.

    Emphasis markers are stripped here as well as by the parser. Inside a raw ``html_block`` the
    CommonMark parser does not interpret Markdown at all, so ``<div>An earlier **version** was
    wrong.</div>`` reaches this function with its asterisks still in place.
    """
    text = text.translate(_INVISIBLE)
    text = text.replace("\u00a0", " ").replace("\u2011", "-").replace("\u2013", "-")
    # Asterisks, tildes and backticks never occur inside a repository path, so they go unconditionally.
    # Underscores DO \u2014 `paper_a_transfer_text.py`, `fig4_transfer` \u2014 so only a run at a word boundary
    # is treated as an emphasis delimiter. Stripping them all turned `tools/paper_a_transfer_text.py`
    # into `tools/paperatransfertext.py` and the internal-path rule stopped recognising its own
    # target: a fix for one bypass opening another, caught by the existing leakage tests.
    text = re.sub(r"[*~`]{1,3}", "", text)
    text = re.sub(r"(?<!\w)_{1,3}|_{1,3}(?!\w)", "", text)
    return " ".join(text.split())


def _visible_paragraphs(text: str):
    """Yield ``(first_source_line, visible_text)`` for each reader-facing block.

    Round-10 P2-1 established the unit: a reader reads BLOCKS, not physical lines, so a phrase
    wrapped across three source lines is one phrase. Round-11 P1-6 keeps the unit and replaces the
    renderer — headings, paragraphs, block quotes, list items, table cells and footnote bodies all
    arrive through the CommonMark token stream with their source line ranges attached, so emphasis,
    inline HTML, entities and split words cannot hide a phrase inside one.
    """
    if _MD is None:                                             # pragma: no cover - env-dependent
        return []
    blocks, line_no = [], 1
    for token in _MD.parse(_strip_html_comments(text)):
        if token.map:
            line_no = token.map[0] + 1
        if token.type == "inline":
            visible = _normalise_visible(_inline_visible(token))
            if visible:
                blocks.append((line_no, visible))
        elif token.type == "html_block":
            visible = _normalise_visible(_HTML_TAG.sub("", token.content))
            if visible:
                blocks.append((line_no, visible))
        elif token.type in ("fence", "code_block"):
            # A self-check after the round-11 merge found these produced NO visible text at all:
            # only `inline` and `html_block` were handled, so a repository path or a review sentence
            # inside a fenced block was invisible to every rule. A reader sees a code block, and the
            # submission files do contain them.
            visible = _normalise_visible(token.content)
            if visible:
                blocks.append((line_no, visible))
    return blocks


def _link_targets(text: str):
    """Yield ``(source_line, target)`` for every destination the submitted source carries.

    Inline and reference links, images, autolinks, and raw ``href``/``src`` attributes in inline or
    block HTML. Reference DEFINITIONS are collected from the parser environment, because a
    definition that is never used produces no token at all and its destination still ships in the
    file.
    """
    if _MD is None:                                             # pragma: no cover - env-dependent
        return []
    stripped = _strip_html_comments(text)
    env: dict = {}
    out, line_no = [], 1
    for token in _MD.parse(stripped, env):
        if token.map:
            line_no = token.map[0] + 1
        children = (token.children or []) if token.type == "inline" else [token]
        for child in children:
            if child.type in ("link_open", "image"):
                for attr in ("href", "src"):
                    target = child.attrGet(attr)
                    if target:
                        out.append((line_no, target))
            elif child.type in ("html_inline", "html_block"):
                out += [(line_no, m.group(1)) for m in _HTML_TARGET.finditer(child.content)]

    for label, ref in (env.get("references") or {}).items():
        target = (ref or {}).get("href")
        if not target:
            continue
        found = re.search(r"(?m)^\s*\[%s\]\s*:" % re.escape(label), stripped, re.I)
        out.append((stripped[:found.start()].count("\n") + 1 if found else 1, target))
    return out


def _normalise_target(target: str) -> str:
    """Percent-decode and tidy a destination before a path rule looks at it.

    ``docs%2Finternal%2Freview.md`` is the same repository path as ``docs/internal/review.md``, and
    a rule that only sees the second is a rule with a documented bypass.
    """
    from urllib.parse import unquote

    out = unquote(target).strip().replace("\\", "/")
    while out.startswith("./"):
        out = out[2:]
    return out



#: The deliverables the package manifest says are uploaded EXACTLY as they stand, with no conversion
#: step to strip editorial notes. Anything invisible in these still reaches the editor.
#:
#: The manuscript, package and cover letter are converted to .docx or .tex first ("remove editorial
#: notes" is a listed conversion edit), so their generator stamps never ship.
_UPLOADED_VERBATIM = ("PAPER_A_JFE_HIGHLIGHTS.txt", "PAPER_A_JFE_FIGURE_CAPTIONS.md")

#: The internal-path pattern, named so the comment channel can use it without re-deriving the rule.
_INTERNAL_PATH_RX = re.compile(r"`?\b(?:docs|tools|tests|puckworks)/[\w./-]+`?|`?\.github/[\w./-]+`?")

_HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.S)


def _html_comments(text: str):
    """Yield ``(source_line, comment_body)`` for every HTML comment in the file."""
    for m in _HTML_COMMENT.finditer(text):
        yield text[:m.start()].count("\n") + 1, m.group(1)


def _placeholders_and_process_language() -> list[str]:
    problems = _parser_problem()
    if problems:
        return problems
    for path in prose_scanned_files():
        if not path.exists():
            continue
        text = _read(path)
        # Placeholders stay LINE-scoped: they do not wrap, and a line number is the more useful
        # diagnostic for a `[TODO]`.
        for line_no, line in enumerate(_strip_html_comments(text).splitlines(), 1):
            for m in _PLACEHOLDER.finditer(line):
                problems.append(f"{path.name}:{line_no}: unresolved placeholder "
                                f"<<{m.group(0)}>>")

        # Channel A — what a reader sees, structurally reconstructed.
        for line_no, para in _visible_paragraphs(text):
            exempt = bool(_UNSUPPLIED_METADATA.search(para))
            for rx, why, rule in _PROCESS_WORDS:
                if path.name not in _RULE_SCOPE[rule]:
                    continue
                if rule == "internal_path" and exempt:
                    continue
                for m in rx.finditer(para):
                    problems.append(f"{path.name}:{line_no}: <<{m.group(0)}>> "
                                    f"[{rule}] -- {why}")

        # Channel B — destinations, which are not prose but ARE submitted. Only the path rules
        # apply: a link target is not a sentence, so review-history and process vocabulary would be
        # meaningless against it, while a repository path in it is exactly the leak.
        if path.name not in _RULE_SCOPE["internal_path"]:
            continue

        # HTML comments are excluded from PROSE because the generated blocks carry schema and
        # manifest stamps that are assurance devices, not sentences a reader reads. But a comment
        # still SHIPS when the file is uploaded as-is: invisible on the page, plainly present in the
        # source an editor receives. So the path rule — and only the path rule — looks inside them,
        # for the files the package manifest says are uploaded WITHOUT conversion.
        #
        # The manuscript, package and cover letter are converted to .docx/.tex first, with "remove
        # editorial notes" an explicit conversion step, so their stamps do not reach anyone. Scoping
        # this channel to the whole set would have flagged eleven legitimate generator stamps and
        # forced churn for no reader's benefit; scoping it to none would have missed the caption
        # file, which is uploaded exactly as it stands.
        for line_no, comment in (_html_comments(text)
                                 if path.name in _UPLOADED_VERBATIM else ()):
            for m in _INTERNAL_PATH_RX.finditer(comment):
                if any(rx.match(_normalise_target(m.group(0).strip("`"))) for rx in _ALLOWED_TARGETS):
                    continue
                problems.append(
                    f"{path.name}:{line_no}: <<{m.group(0)}>> [internal_path] -- internal "
                    f"repository path inside an HTML comment; no reader sees it, but it ships in "
                    f"the submitted source")
        exempt_lines = {ln for ln, para in _visible_paragraphs(text)
                        if _UNSUPPLIED_METADATA.search(para)}
        for line_no, raw_target in _link_targets(text):
            target = _normalise_target(raw_target)
            if any(rx.match(target) for rx in _ALLOWED_TARGETS) or line_no in exempt_lines:
                continue
            for rx, why, rule in _PROCESS_WORDS:
                if rule != "internal_path":
                    continue
                for m in rx.finditer(target):
                    problems.append(
                        f"{path.name}:{line_no}: <<{m.group(0)}>> [internal_path] -- {why}; it is "
                        f"a LINK TARGET rather than visible prose, and ships in the submitted "
                        f"source even though no reader sees it")
    return problems


#: A supplementary reference carries a TYPE as well as a number. Comparing numbers alone is what
#: let "Supplementary Table S2" be satisfied by a "Supplementary Note S2" -- a false pass caused by
#: discarding semantic type (round-4 review P0-3). Types are normalised to singular.
_SUPP_KIND = {"table": "Table", "tables": "Table", "figure": "Figure", "figures": "Figure",
              "note": "Note", "notes": "Note", "method": "Methods", "methods": "Methods"}


def _typed_supp_refs(text: str, heading_only: bool = False):
    """Return the set of (kind, number) pairs, e.g. {("Table", "S3"), ("Note", "S2")}."""
    prefix = r"(?m)^#{2,4}\s+(?:Supplementary\s+)?" if heading_only else r"Supplementary\s+"
    pat = prefix + r"(Table|Figure|Note|Method)s?\s+(S\d+)"
    return {(_SUPP_KIND[k.lower()], n) for k, n in re.findall(pat, text)}


def _supplementary_targets() -> list[str]:
    """Every "Supplementary X" the article promises must exist as an item of the SAME TYPE.

    Third review P0-3: the article promised items while no supplement existed at all.
    Round-four review P0-3: the supplement existed, but this check compared only the NUMBER, so a
    promise of Table S2 was satisfied by the presence of Note S2. It also tolerated a
    non-sequential numbering scheme that made such a gap easy to miss.
    """
    text = _read(CONVERSION)
    promised = _typed_supp_refs(text)
    if not promised:
        return []
    if not SUPPLEMENT.exists():
        return [f"the article cites {len(promised)} supplementary items but no supplement exists "
                f"at {SUPPLEMENT.name}"]
    supp = _read(SUPPLEMENT)
    declared = _typed_supp_refs(supp, heading_only=True)

    problems = [f"the article cites Supplementary {k} {n} but the supplement defines no such item "
                f"(it defines: {', '.join(sorted(f'{a} {b}' for a, b in declared)) or 'nothing'})"
                for k, n in sorted(promised - declared)]

    # Sequential numbering, per type. A gap is not fatal in itself, but it is exactly the condition
    # under which a missing item reads as an intentional omission, so it must be deliberate.
    by_kind: dict[str, list[int]] = {}
    for kind, num in declared:
        by_kind.setdefault(kind, []).append(int(num[1:]))
    for kind, nums in sorted(by_kind.items()):
        nums.sort()
        gaps = [i for i in range(1, max(nums) + 1) if i not in nums]
        if gaps:
            problems.append(
                f"supplementary {kind} numbering is non-sequential: defines "
                f"{[f'S{n}' for n in nums]}, missing {[f'S{g}' for g in gaps]}. Renumber "
                f"sequentially or record why the gap is intentional")
    return problems


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
    if not FIGURE_MAP_INTERNAL.exists():
        return []
    return ([] if "no embedded figure number" in _read(FIGURE_MAP_INTERNAL).lower() else
            ["the internal figure map does not record that figures carry no embedded 'Fig N' title "
             "(third review, cross-cutting figure issue)"])


def _upload_captions_are_generated_and_clean() -> list[str]:
    """The uploaded caption file must be current, and must be the upload file, not the map.

    Round-10 P2-1. Three separate failures are possible here and all three have precedent in this
    repository: the caption file drifts from the source (round-8 P0-1, a caption quoting a superseded
    benchmark); the internal bookkeeping file is uploaded by mistake (its title said
    "submission-ready"); or the package manifest keeps listing the old path after a split.
    """
    from tools import paper_a_figure_captions as FC

    problems = []
    if not UPLOAD_CAPTIONS.exists():
        return ["the upload-ready caption file is missing; generate it with "
                "`python tools/paper_a_figure_captions.py --write`"]
    if _read(UPLOAD_CAPTIONS) != FC.render():
        problems.append("the upload-ready caption file is stale against the internal figure map; "
                        "run `python tools/paper_a_figure_captions.py --write`")
    package = _read(PACKAGE)
    if FIGURE_MAP_INTERNAL.name in package:
        problems.append("the package manifest lists %s, which is internal bookkeeping and must not "
                        "be uploaded" % FIGURE_MAP_INTERNAL.name)
    if UPLOAD_CAPTIONS.name not in package:
        problems.append("the package manifest does not list the upload-ready caption file %s"
                        % UPLOAD_CAPTIONS.name)
    # The stamp is read from the GENERATOR rather than duplicated here, so changing it in one place
    # cannot leave this check asserting a string that no longer exists — which would silently permit
    # every comment in the file.
    from tools import paper_a_figure_captions as FCAP

    stamp = next((ln for ln in FCAP.render().splitlines() if ln.startswith("<!--")), "")
    if "<!--" in _read(UPLOAD_CAPTIONS).replace(stamp, ""):
        problems.append("the upload-ready caption file carries an HTML comment other than its own "
                        "generation stamp; source stamps must not reach an editor")
    return problems


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

    # Same environment guard as _front_matter(). The release gate is only ever run where the
    # release is actually being cut, but it must not crash on a minimal-dependency lane either.
    try:
        from tools import paper_a_front_matter as FM
        problems += [f"unresolved submission metadata: {g}" for g in FM.submission_gaps(FM.load())]
    except ImportError as exc:
        problems.append(f"submission metadata not checked: pyyaml unavailable ({exc})")

    return problems


def _endpoint_science() -> list[str]:
    """The collected-mass endpoint contract. Runs in ROUTINE `verify`, not only at release.

    Round-8 P0-3. This check used to live in `_release_state()` and looked for a ``v_targets``
    key against an artefact that has stored ``m_targets`` since the round-7 unit correction. It
    could therefore never validate the corrected artefact — a false negative at release time —
    while ordinary development ran `verify`, which did not include it at all. A central
    scientific contract must not be exercised only by the one mode nobody runs until the end.

    It also used to demand the literal phrase "not endpoint-invariant" in the manuscript. A
    release gate should bind the declared interpretation semantically; an editorial rewording is
    not a scientific regression. The interpretation now travels as a structured code in the
    artefact and is matched against the generated block's stamp.
    """
    from puckworks.paper_a import transfer_contract as TC

    problems: list[str] = []
    if not ENDPOINT_JSON.exists():
        problems.append("the %s endpoint propagation has not been run and archived"
                        % TC.endpoint_label())
        return problems

    ep = json.loads(_read(ENDPOINT_JSON))
    problems += TC.validate_endpoint_contract(ep)

    if int(ep.get("schema_version", 0)) < TC.SCHEMA_VERSION:
        problems.append("the endpoint artefact is schema_version %r; this contract requires >= %d "
                        "(regenerate with `python tools/paper_a_transfer_artifacts.py --write`)"
                        % (ep.get("schema_version"), TC.SCHEMA_VERSION))

    if "reading" not in ep:
        problems.append("the endpoint propagation carries no recorded reading")

    # Structured interpretation, not a magic phrase: the artefact declares what the sweep found
    # and the manuscript's generated block carries the same code.
    sens = ep.get("endpoint_sensitivity")
    if not isinstance(sens, dict) or not sens.get("interpretation_code"):
        problems.append("the endpoint artefact declares no structured `endpoint_sensitivity."
                        "interpretation_code`; a bare conclusion_stable boolean hides which "
                        "conclusion is being tested")
    else:
        code = sens["interpretation_code"]
        if code not in _flat(_read(CONVERSION)):
            problems.append(
                "the endpoint sweep's interpretation code %r does not appear in the manuscript's "
                "generated endpoint block; the archived interpretation and the published one "
                "have diverged" % code)
    return problems


def _sign_stability_claims_match_the_audit() -> list[str]:
    """Round-9 P0-2. The paper must not contradict its own archived audit.

    At the round-9 target the abstract said the bound near zero was "unresolved at the precision
    this resampling attains" while the Results said its sign was numerically settled at ~8 Monte
    Carlo standard errors and the artefact recorded ``upper_bound_sign_is_stable = true``. Both
    statements were about the same 40 g bound. A reader could not tell whether the endpoint
    sensitivity was a scientific result or a numerical artefact, because the paper said both.

    This binds the direction of the claim to the archived flag, in both directions.
    """
    from puckworks.paper_a import transfer_semantics as TS

    if not ENDPOINT_JSON.exists():
        return []
    ep = json.loads(_read(ENDPOINT_JSON))
    try:
        audit = TS.find_exact_audit(ep, TS.AUDITED_TARGET)
    except KeyError as exc:
        return ["the endpoint artefact has no audit for the declared target: %s" % exc]

    stable = bool(audit.get("upper_bound_sign_is_stable"))
    problems = []
    # Phrases that assert the sign/side is NOT numerically resolved.
    unresolved_claims = ("not a resolved quantity", "unresolved at the precision",
                         "sign is not resolved", "not numerically resolved")
    for path in (CONVERSION, CANONICAL, SUPPLEMENT, PACKAGE, COVER_LETTER):
        if not path.exists():
            continue
        flat = _flat(_read(path))
        for phrase in unresolved_claims:
            if phrase in flat and stable:
                problems.append(
                    "%s says %r, but the archived audit for %s records "
                    "upper_bound_sign_is_stable=true. Numerical sign stability, endpoint "
                    "sensitivity of the zero relation, and absence of calibrated coverage are "
                    "three different statements and must not be collapsed."
                    % (path.name, phrase, TS.AUDITED_TARGET.prose))
        if not stable and "numerically stable" in flat:
            problems.append("%s claims the bound is numerically stable, but the archived audit "
                            "says it is not" % path.name)
    return problems


def _no_active_volume_endpoint() -> list[str]:
    """No active submission-facing path may describe the collected endpoint as a volume.

    Round-8 P0-3. Historical reviews and changelogs legitimately record that mL was once wrong,
    so this scans only the active submission surfaces, not the whole repository.
    """
    import re

    problems = []
    pattern = re.compile(r"(38\s*/\s*40\s*/\s*42\s*mL|\b3[08]\s*mL\b|\b4[02]\s*mL\b|v_targets)")
    for path in (PACKAGE, CONVERSION, SUPPLEMENT, HIGHLIGHTS, COVER_LETTER):
        if not path.exists():
            continue
        for n, line in enumerate(_read(path).splitlines(), 1):
            if pattern.search(line):
                problems.append("%s:%d describes the collected endpoint as a volume: %r"
                                % (path.name, n, line.strip()[:120]))
    return problems


CHECKS = (
    ("phrase drift", _phrase_drift),
    ("generated block parity", _generated_block_parity),
    ("claim policy", _claim_policy),
    ("upload-ready captions", _upload_captions_are_generated_and_clean),
    ("front matter", _front_matter),
    ("citations", _citations),
    ("cross-references", _cross_references),
    ("placeholders / process language", _placeholders_and_process_language),
    ("supplementary targets", _supplementary_targets),
    ("grid record", _grid_record),
    ("figure labels", _figure_labels),
    ("endpoint science contract", _endpoint_science),
    ("no active volume endpoint", _no_active_volume_endpoint),
    ("sign-stability claims match the audit", _sign_stability_claims_match_the_audit),
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
        if front_matter_unavailable:
            print(f"  {'front matter':34s} NOT RUN -- {front_matter_unavailable}")
        if abstract_source_unavailable:
            print(f"  {'abstract vs its source':34s} PARTIAL -- {abstract_source_unavailable}")
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

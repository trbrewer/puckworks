"""Curated-corpus method and denominators (Paper 3 MC15, with the U7 protocol table).

MC15's two demands are separable.

**Denominators.** "27 components" is the least informative count available, and it invites the
reading that the registry rests on 27 independent studies. It does not: the components trace to a
much smaller number of source publications, and smaller still of empirical campaigns. Reporting
component count alone makes that impossible to see, so this module derives the other denominators
from the registry and the dataset manifest and prints them together.

**Method.** "Curated" is a legitimate choice; "undocumented" is not. `CORPUS_METHOD` records the
selection procedure — seeds, sources searched, dates, strings, tracing, inclusion and exclusion
rules, language limits, how rights-blocked sources are handled, and how project-created components
are distinguished from published ports — so a reader can reconstruct how the corpus came to hold
what it holds, even though the search was exploratory rather than systematic.

Neither part upgrades the corpus to systematic. The indexed search remains a submission gate that
has not been executed, and this module states that rather than obscuring it.

CLI::

    python -m puckworks.paper3.corpus                # human-readable
    python -m puckworks.paper3.corpus --json
    python -m puckworks.paper3.corpus --splice       # write into the manuscript
    python -m puckworks.paper3.corpus --verify       # CI: fail if stale
"""
from __future__ import annotations

import collections
import csv
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_CSV = REPO_ROOT / "puckworks" / "data" / "MANIFEST.csv"
CARDS_DIR = REPO_ROOT / "docs" / "cards"
MANUSCRIPT = REPO_ROOT / "docs" / "PAPER_3_PUCKWORKS_DRAFT.md"
GENERATED = REPO_ROOT / "docs" / "paper3_resource" / "generated"
DENOM_JSON = GENERATED / "corpus_denominators.json"
DENOM_MD = GENERATED / "corpus_denominators.md"

_BEGIN = "<!-- corpus:begin -->"
_END = "<!-- corpus:end -->"

#: The corpus-construction method, recorded because "curated" must not mean "irreproducibly
#: selected". Every field is a statement about how the corpus was BUILT, not about how good it is.
CORPUS_METHOD: dict[str, str] = {
    "status": (
        "EXPLORATORY AND CURATED, not systematic. No indexed database search has been executed. "
        "An indexed search is a declared submission gate (§2.3) and remains outstanding; the "
        "denominators below therefore describe a convenience corpus."),
    "seed_papers": (
        "Selection began from espresso-specific process models with published equations AND "
        "either public data or reproducible published figures: Cameron 2020 (extraction "
        "kinetics), Waszkiewicz 2025 (poroelastic flow), Foster 2025 (machine/infiltration), "
        "Maille 2024 (grind/timescales). These were chosen because each supplies a different "
        "STAGE of the process chain, which is what a stage-typed registry needs in order to be "
        "exercised at all."),
    "sources_searched": (
        "Publisher sites and DOIs reached from the seeds; arXiv; Zenodo and Mendeley Data for "
        "accompanying deposits; the SCA/coffee-science grey literature reachable without a "
        "subscription. Two publisher hosts (MDPI, Royal Society) are Cloudflare-blocked from this "
        "environment and were reached, when at all, through DOI metadata rather than full text."),
    "search_dates": "Rolling, 2026-05 through 2026-07-26. No frozen search date exists.",
    "search_strings": (
        "Exploratory rather than fielded, e.g. 'espresso extraction model', 'coffee bed "
        "permeability', 'poroelastic coffee puck', 'espresso flow rate model', 'grind size "
        "extraction kinetics'. Strings were adapted as interface gaps appeared and were not held "
        "constant, which is one reason the corpus cannot be called systematic."),
    "citation_tracing": (
        "Backward tracing from each seed's reference list; forward tracing via Crossref/Google "
        "Scholar citing-article lists. Tracing stopped at the point where candidates no longer "
        "supplied a stage contract the registry could type."),
    "inclusion_rules": (
        "(1) a written model or calibration with stated equations or a stated fitted form; "
        "(2) enough parameter provenance to implement it without inventing values; "
        "(3) a stage the registry types; "
        "(4) at least one checkable quantity — a published constant, curve, or dataset — so a "
        "gate can be wired to something other than our own output."),
    "exclusion_rules": (
        "Excluded: non-espresso brewing without a transferable mechanism; ANOVA/sensory studies "
        "with no process model; papers whose parameters are not recoverable ('not provided' in "
        "the card, never guessed); and models superseded by a later paper from the same group "
        "unless the earlier one carries data the later one drops."),
    "derivative_and_duplicate_handling": (
        "A model re-expressed by a later paper is registered ONCE, against the source that "
        "supplies the parameters used. A dataset appearing in several papers gets one manifest "
        "row per distinct extraction, with the extraction method recorded, so the same underlying "
        "measurement is not counted twice as independent evidence."),
    "language_limits": (
        "English only. No translation was attempted and no non-English candidate was assessed, so "
        "any non-English literature is missing rather than judged."),
    "inaccessible_and_rights_blocked": (
        "Paywalled articles are cited from DOI metadata and NOT ingested; no figure, table or text "
        "is copied. GPL-licensed author code is not ingested into this MIT package — components "
        "are re-expressed from the published equations. A rights-blocked source is registered as "
        "`reference_only` with the block recorded, rather than omitted, so the gap is visible."),
    "project_vs_published": (
        "`provenance_class` separates them at the schema level: `published_port` re-expresses a "
        "published model; `project_model` and `project_synthesis` are ours. No project-created "
        "component is presented as literature-derived, and the counts below are reported by class "
        "for exactly this reason."),
    "response_to_interface_gaps": (
        "The search was steered by missing stage contracts rather than by topic coverage: when a "
        "stage had no component able to supply a downstream input, candidates were sought for that "
        "stage specifically. This makes the corpus useful for exercising the registry and makes it "
        "an explicitly biased sample of the espresso literature."),
}

#: U7 — the protocol choices behind the §4.5/§7.5 timescale comparison, stated in one place instead
#: of scattered through prose.
PROTOCOL_CHOICES: tuple[tuple[str, str, str], ...] = (
    ("Integration horizon", "400 s",
     "long enough for the slow branch to flatten in every compared model"),
    ("Initial condition", "tau = 0",
     "all models started from the same zero-time origin so timescales are comparable"),
    ("Fine particle class", "20 um radius",
     "the selected fine class; the coarse d[4,3] is NOT reported by the source and was not invented"),
    ("Coarse particle class", "not evaluated",
     "recorded as `coarse_class_status=not_evaluated_missing_radius` rather than estimated"),
    ("Fit comparison", "one- vs two-exponential",
     "replaces an earlier 50% distance heuristic; reports single_exp_like and two_exp_r2_gain"),
    ("Bath ratio / window", "as published per source",
     "reproduced by `roman_protocol_sensitivity()`; the window choice moves the ratio 15.8 -> 8.6"),
    ("Curve status", "model-generated",
     "the compared curves are model output, so these are qualitative model-to-model probes, "
     "not validation"),
)


def denominators() -> dict:
    """Counts that make 'how many components' impossible to misread as 'how many studies'."""
    import puckworks.models  # noqa: F401  (registers components)
    from puckworks import registry as R

    comps = list(R.components())
    rows = list(csv.DictReader(MANIFEST_CSV.open(encoding="utf-8")))
    dataset_sources = {r["dataset_id"].split("/")[0] for r in rows if r.get("dataset_id")}

    by_provenance = collections.Counter(c.provenance_class for c in comps)
    by_evidence = collections.Counter(c.evidence_strength for c in comps)
    by_role = collections.Counter(c.execution_role for c in comps)
    by_stage = collections.Counter(c.stage for c in comps)

    dois = {c.doi for c in comps if c.doi}
    papers = {c.paper for c in comps if c.paper}

    # "Independent data" here means: the component's evidence rests on something other than a
    # reconstruction of its own source's output. Derived from the registry's own evidence axis,
    # not asserted.
    reconstruction_like = {"post_fit_reconstruction", "source_curve_reproduction",
                           "qualitative_capacity", "exploratory_synthesis"}
    with_independent = [c.name for c in comps
                        if c.evidence_strength not in reconstruction_like]

    import puckworks.rights as rights
    blocked = [c.name for c in comps if not rights.may_execute_locally(c.name).allowed]

    calibration_only = [c.name for c in comps if c.execution_role == "calibration"]
    reference_only = [c.name for c in comps if c.provenance_class == "reference_only"]

    return dict(
        n_components=len(comps),
        n_unique_source_publications=len(papers),
        n_unique_dois=len(dois),
        n_unique_dataset_sources=len(dataset_sources),
        n_manifest_records=len(rows),
        n_cards=len(list(CARDS_DIR.glob("*.md"))),
        components_by_provenance_class=dict(sorted(by_provenance.items())),
        components_by_evidence_relation=dict(sorted(by_evidence.items())),
        components_by_execution_role=dict(sorted(by_role.items())),
        components_by_stage=dict(sorted(by_stage.items())),
        n_components_with_independent_evidence=len(with_independent),
        components_with_independent_evidence=sorted(with_independent),
        n_rights_or_data_blocked=len(blocked),
        rights_or_data_blocked=sorted(blocked),
        n_calibration_only=len(calibration_only),
        n_reference_only=len(reference_only),
        components_per_publication=round(len(comps) / len(papers), 2) if papers else None,
    )


def render(d: dict) -> str:
    out = [
        "<!-- generated by puckworks.paper3.corpus — do not edit by hand -->",
        "",
        "**Table 1a. Corpus denominators.** Component count is the least informative number "
        "available. The "
        f"registry's **{d['n_components']} components** derive from only "
        f"**{d['n_unique_source_publications']} source publications** "
        f"({d['n_unique_dois']} carrying a DOI in the registry), i.e. "
        f"**{d['components_per_publication']} components per publication**. They are not "
        f"{d['n_components']} independent studies and not "
        f"{d['n_components']} independent bodies of evidence.",
        "",
        "| denominator | count |",
        "|---|---:|",
        f"| registered components | {d['n_components']} |",
        f"| unique source publications | {d['n_unique_source_publications']} |",
        f"| unique DOIs recorded | {d['n_unique_dois']} |",
        f"| unique dataset sources (empirical campaigns) | {d['n_unique_dataset_sources']} |",
        f"| dataset manifest records | {d['n_manifest_records']} |",
        f"| model/source cards written | {d['n_cards']} |",
        f"| components with evidence beyond reconstruction of their own source | "
        f"{d['n_components_with_independent_evidence']} |",
        f"| components rights- or data-blocked | {d['n_rights_or_data_blocked']} |",
        f"| components that are calibration objects only | {d['n_calibration_only']} |",
        f"| components that are reference-only | {d['n_reference_only']} |",
        "",
        "**By provenance class.** " + ", ".join(
            f"`{k}`: {v}" for k, v in d["components_by_provenance_class"].items())
        + " — the project-created components are counted separately from published ports by schema,"
          " not by convention.",
        "",
        "**By evidence relation.** " + ", ".join(
            f"`{k}`: {v}" for k, v in d["components_by_evidence_relation"].items())
        + ".",
        "",
        "**By execution role.** " + ", ".join(
            f"`{k}`: {v}" for k, v in d["components_by_execution_role"].items())
        + ".",
    ]
    return "\n".join(out) + "\n"


def render_method() -> str:
    out = ["**Table 1b. Corpus-construction method.** How the corpus was built, aspect by "
           "aspect; declared, not derived.", "",
           "| aspect | statement |", "|---|---|"]
    for key, value in CORPUS_METHOD.items():
        out.append(f"| {key.replace('_', ' ')} | {value} |")
    return "\n".join(out) + "\n"


def render_protocol() -> str:
    out = ["**Table 1c. Protocol choices behind the timescale comparison.** Including the "
           "choices NOT made, such as the coarse particle class left unevaluated.", "",
           "| protocol choice | value | why |", "|---|---|---|"]
    for name, value, why in PROTOCOL_CHOICES:
        out.append(f"| {name} | {value} | {why} |")
    return "\n".join(out) + "\n"


def _block() -> str:
    return (_BEGIN + "\n" + render(denominators()) + "\n" + render_method() + "\n"
            + render_protocol() + _END)


def write() -> dict:
    d = denominators()
    GENERATED.mkdir(parents=True, exist_ok=True)
    DENOM_JSON.write_text(json.dumps(d, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DENOM_MD.write_text(render(d) + "\n" + render_method() + "\n" + render_protocol(),
                        encoding="utf-8")
    return d


def splice(write_it: bool = True) -> str:
    text = MANUSCRIPT.read_text(encoding="utf-8")
    if _BEGIN not in text or _END not in text:
        return "corpus markers missing from the manuscript"
    block = _block()
    current = _BEGIN + text.split(_BEGIN, 1)[1].split(_END, 1)[0] + _END
    if current.strip() == block.strip():
        return ""
    if not write_it:
        return "corpus block is STALE -- run --splice"
    MANUSCRIPT.write_text(text.split(_BEGIN)[0] + block + text.split(_END, 1)[1], encoding="utf-8")
    return ""


def verify() -> list[str]:
    problems = []
    d = denominators()
    for path, fresh in ((DENOM_JSON, json.dumps(d, indent=2, sort_keys=True) + "\n"),
                        (DENOM_MD, render(d) + "\n" + render_method() + "\n" + render_protocol())):
        if not path.exists():
            problems.append(f"missing: {path.relative_to(REPO_ROOT)}")
        elif path.read_text(encoding="utf-8") != fresh:
            problems.append(f"STALE: {path.relative_to(REPO_ROOT)}")
    stale = splice(write_it=False)
    if stale:
        problems.append(stale)
    return problems


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    if "--splice" in argv:
        write()
        problem = splice(write_it=True)
        print(problem or "corpus block spliced")
        return 1 if problem else 0
    if "--verify" in argv:
        problems = verify()
        for p in problems:
            print("  -", p, file=sys.stderr)
        print("corpus artifacts up to date." if not problems else "corpus STALE")
        return 1 if problems else 0
    if "--json" in argv:
        print(json.dumps(denominators(), indent=2, sort_keys=True))
    else:
        print(render(denominators()))
        print(render_method())
        print(render_protocol())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

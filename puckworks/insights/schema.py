"""Insight Foundry schema — entity, relation, tension, and candidate types + integrity guards.

The Foundry is an OVERLAY on the existing authorities (registry, cards, MANIFEST, public
claims). It is never the source of truth for a model's physics or a dataset's evidence class:
every record carries the authority path it was read from, and every evidence label is copied
VERBATIM from that authority (`docs/insights/INSIGHT_FOUNDRY_DESIGN.md` §2).

Two guards in this module are load-bearing and are the reason the types are not plain dicts:

  * `assert_verbatim` — a Foundry record may add DERIVED TAGS beside an authority's wording but
    may never replace it. Derived lineage tags are conservative by construction: a manifest cell
    reading "independent within-rig (equilibrium) / post-fit (9-bar Q(t) reproduction)" carries
    BOTH `independent` and `post_fit`, and `mixed_strength` on top, because collapsing it to the
    stronger half is exactly the upgrade CLAUDE.md rule 4 forbids.
  * `scoring_admissible` — `llm_suggested` relations are hypotheses. They may appear in the atlas
    and may motivate a candidate, but they may not drive automated shortlist scoring
    (blueprint §7.3). Nothing in the foundation scores anything; the guard exists so the first
    scorer cannot quietly consume a suggestion as if it were evidence.

Nothing here adjudicates. A candidate produced by this package is a QUESTION with provenance,
status `SEED`, and no scores.
"""
from __future__ import annotations

import dataclasses as dc
import hashlib
import json
import re
import subprocess
from pathlib import Path

SCHEMA_VERSION = 1

REPO_ROOT = Path(__file__).resolve().parents[2]

# ---- controlled vocabularies -------------------------------------------------------------

#: How confident the Foundry is that a relation is REAL, independent of whether it is important.
#: `explicit` = the authority states it in so many words; `deterministically_inferred` = a rule
#: over authority fields (e.g. two components share a stage); `llm_suggested` = proposed by a
#: model and not yet checked; `human_confirmed` / `scientifically_tested` = a person or a screen
#: has since ruled on it. Only the last two can ever be created outside this package's extractors.
RELATION_CONFIDENCES = ("explicit", "deterministically_inferred", "llm_suggested",
                        "human_confirmed", "scientifically_tested")

#: Confidences admissible as an input to automated scoring. `llm_suggested` is deliberately absent.
SCORING_ADMISSIBLE_CONFIDENCES = ("explicit", "deterministically_inferred",
                                  "human_confirmed", "scientifically_tested")

#: Relation predicates the corpus graph supports (blueprint §7.2). The foundation emits a subset;
#: the rest are declared so a later lens does not invent a synonym for an existing edge.
#:
#: `CARD_NAMES_IN_OVERLAPS` is a Foundry addition to the blueprint's list, and deliberately
#: colourless: it records that card A names component B in its "Overlaps and conflicts" section.
#: The blueprint offers only `COMPETES_WITH`/`COMPLEMENTS` for that section, but a card often
#: names a neighbour without ruling on it, and choosing one of those two for it would be the
#: extractor inventing a scientific verdict. The typed edges are emitted only when the card's own
#: sentence says so.
RELATION_TYPES = (
    "PREDICTS", "MEASURES", "USES", "CALIBRATED_FROM", "VALIDATED_AGAINST", "DERIVED_FROM",
    "RECONSTRUCTS", "COMPETES_WITH", "COMPLEMENTS", "SHARES_OBSERVABLE_WITH",
    "SHARES_PARAMETER_WITH", "CONTRADICTS", "AGREES_WITH", "EXTRAPOLATES_BEYOND",
    "CONSUMES_CLOSURE", "PRODUCES_CLOSURE", "REQUIRES_MEASUREMENT", "SUPPORTS_CLAIM",
    "LIMITS_CLAIM", "FALSIFIES_CANDIDATE", "CARD_NAMES_IN_OVERLAPS",
)

#: Tension lenses (blueprint §9). `A`…`M` keep the blueprint's letters so a row is traceable to
#: the design section that motivated it.
LENSES = {
    "model_disagreement": "A",
    "observational_equivalence": "B",
    "composition_failure": "C",
    "closure_portability": "D",
    "lineage_circularity": "E",
    "regime_transition": "F",
    "hidden_discriminator": "G",
    "cross_species_inconsistency": "H",
    "scale_mismatch": "I",
    "negative_result": "J",
    "evidence_asymmetry": "K",
    "missing_experiment": "L",
    "public_story": "M",
}

#: Candidate lifecycle (blueprint §10.3). The foundation may only ever emit `SEED`; every other
#: state is entered by a human decision or a screen result, never by a generator.
CANDIDATE_STATUSES = (
    "SEED", "TRIAGED", "CHEAP_SCREEN_ACTIVE", "FALSIFIED", "SURVIVED_CHEAP_SCREEN",
    "DEEP_SCREEN_ACTIVE", "PUBLIC_STORY", "TECHNICAL_NOTE", "PAPER_CANDIDATE",
    "NEEDS_NEW_DATA", "SOLVER_BACKLOG", "RETIRED",
)
GENERATOR_EMITTABLE_STATUSES = ("SEED",)

#: Cheap-screen outcomes (blueprint §12 Stage C).
SCREEN_DECISIONS = ("SURVIVE", "RETIRE", "NEEDS_NEW_DATA")

#: Audience tracks kept SEPARATE on purpose (blueprint §3.6): a striking public story and a
#: publishable result are different axes, and merging them is how claim inflation starts.
AUDIENCE_TRACKS = ("public_story", "practitioner", "technical_note", "methods_paper",
                   "domain_paper", "experiment_design", "solver_backlog", "data_note")

#: Derived lineage tags (blueprint §8.3). These SIT BESIDE the manifest's own wording; see
#: `assert_verbatim`. `mixed_strength` marks a cell that names more than one strength — the case
#: a careless reader collapses upward.
LINEAGE_TAGS = ("raw_measurement", "post_fit", "digitized", "same_campaign", "independent",
                "reference_only", "restricted", "rights_blocked", "verification",
                "qualitative", "mixed_strength", "unclassified")

#: Espresso-process observables the model/observable matrix is built over. Deliberately a small
#: named list rather than free text so the matrix has stable columns; `Fo_F`/`Fo_diff` naming
#: discipline (CLAUDE.md rule 8) applies to any dimensionless group added here.
OBSERVABLES = (
    "pressure", "flow", "first_drip_time", "wetting_front", "permeability", "porosity",
    "extraction_yield", "tds", "species_concentration", "fraction_history", "cumulative_mass",
    "bed_deformation", "fines_distribution", "temperature", "particle_size",
)


class SchemaError(ValueError):
    """A Foundry record violated a structural invariant."""


# ---- provenance --------------------------------------------------------------------------


@dc.dataclass(frozen=True)
class Provenance:
    """Where a record or relation came from. Every entity and every edge carries one."""

    source_path: str                     # repo-relative path of the AUTHORITY
    source_locator: str = ""             # section heading, CSV column, registry field, ...
    source_commit: str = ""
    extraction_mode: str = ""            # live_registry | structured_card_section | csv_row | ...
    confidence: str = "explicit"

    def __post_init__(self):
        if not self.source_path:
            raise SchemaError("provenance requires a source_path")
        if self.confidence not in RELATION_CONFIDENCES:
            raise SchemaError("bad relation confidence %r (not in %r)"
                              % (self.confidence, RELATION_CONFIDENCES))

    def as_dict(self) -> dict:
        return dc.asdict(self)


@dc.dataclass
class Entity:
    """A node in the corpus map: a model, dataset, card, observable, closure, claim, or result."""

    id: str                              # "<kind>:<local id>"
    kind: str                            # model | dataset | observable | closure | claim | result
    label: str
    provenance: Provenance
    attrs: dict = dc.field(default_factory=dict)

    def __post_init__(self):
        if ":" not in self.id:
            raise SchemaError("entity id %r must be '<kind>:<local id>'" % self.id)
        if not self.id.startswith(self.kind + ":"):
            raise SchemaError("entity id %r does not match kind %r" % (self.id, self.kind))

    def as_dict(self) -> dict:
        return {"id": self.id, "kind": self.kind, "label": self.label,
                "provenance": self.provenance.as_dict(), "attrs": self.attrs}


@dc.dataclass
class Relation:
    """A typed, provenance-carrying edge between two entities."""

    type: str
    source: str
    target: str
    provenance: Provenance
    attrs: dict = dc.field(default_factory=dict)

    def __post_init__(self):
        if self.type not in RELATION_TYPES:
            raise SchemaError("bad relation type %r (not in %r)" % (self.type, RELATION_TYPES))

    @property
    def confidence(self) -> str:
        return self.provenance.confidence

    def as_dict(self) -> dict:
        return {"type": self.type, "source": self.source, "target": self.target,
                "provenance": self.provenance.as_dict(), "attrs": self.attrs}


@dc.dataclass
class Tension:
    """One row of the tension atlas: a potentially productive disagreement, not a finding.

    `human_status` is `UNREVIEWED` on generation and stays there until a person rules. No lens
    may write a scientific verdict into a row — the atlas reports what the authorities say about
    each other, and what would separate them.
    """

    tension_id: str
    lens: str
    entity_ids: tuple
    difference_summary: str
    provenance: tuple                    # tuple[Provenance]
    shared_observable: str = ""
    shared_domain: str = ""
    difference_type: str = ""
    evidence_basis: str = ""
    why_it_matters: str = ""
    candidate_discriminator: str = ""
    data_available: str = "UNKNOWN"      # YES | NO | PARTIAL | UNKNOWN
    cheap_test_possible: str = "UNKNOWN"  # YES | NO | UNKNOWN
    candidate_id: str = ""
    human_status: str = "UNREVIEWED"

    def __post_init__(self):
        if self.lens not in LENSES:
            raise SchemaError("bad lens %r (not in %r)" % (self.lens, sorted(LENSES)))
        if not self.entity_ids:
            raise SchemaError("tension %r cites no entities" % self.tension_id)
        if not self.provenance:
            raise SchemaError("tension %r carries no provenance" % self.tension_id)

    @property
    def relation_confidences(self) -> tuple:
        return tuple(p.confidence for p in self.provenance)

    def as_dict(self) -> dict:
        return {"tension_id": self.tension_id, "lens": self.lens,
                "lens_letter": LENSES[self.lens], "entity_ids": list(self.entity_ids),
                "shared_observable": self.shared_observable, "shared_domain": self.shared_domain,
                "difference_type": self.difference_type,
                "difference_summary": self.difference_summary,
                "evidence_basis": self.evidence_basis, "why_it_matters": self.why_it_matters,
                "candidate_discriminator": self.candidate_discriminator,
                "data_available": self.data_available,
                "cheap_test_possible": self.cheap_test_possible,
                "candidate_id": self.candidate_id, "human_status": self.human_status,
                "provenance": [p.as_dict() for p in self.provenance]}


@dc.dataclass
class Candidate:
    """An insight candidate: one falsifiable question, one cheap test, one stop condition.

    A generated candidate carries NO scores. Scores are a human/LLM triage aid applied later
    (blueprint §11) and are meaningless before a person has read the question.
    """

    id: str
    title: str
    question: str
    lens: str
    tension_ids: tuple
    entity_ids: tuple
    cheap_test: str
    stop_condition: str
    status: str = "SEED"
    insight_types: tuple = ()
    audience_tracks: tuple = ()
    why_it_may_matter: str = ""
    why_it_may_surprise: str = ""
    strongest_alternative: str = ""
    minimum_figure: str = ""
    survive_if: str = ""
    retire_if: str = ""
    inconclusive_if: str = ""
    existing_evidence: tuple = ()
    lineage_risks: tuple = ()
    novelty_search_terms: tuple = ()
    scores: dict = dc.field(default_factory=dict)
    history: tuple = ()
    source_commit: str = ""

    def __post_init__(self):
        if not re.fullmatch(r"I-\d{3}", self.id):
            raise SchemaError("candidate id %r must look like I-001" % self.id)
        if self.status not in CANDIDATE_STATUSES:
            raise SchemaError("candidate %s: bad status %r" % (self.id, self.status))
        for field_name in ("question", "cheap_test", "stop_condition"):
            if not getattr(self, field_name).strip():
                raise SchemaError("candidate %s: %s is required (blueprint §19.1)"
                                  % (self.id, field_name))
        for t in self.audience_tracks:
            if t not in AUDIENCE_TRACKS:
                raise SchemaError("candidate %s: bad audience track %r" % (self.id, t))

    def as_dict(self) -> dict:
        d = dc.asdict(self)
        for k, v in list(d.items()):
            if isinstance(v, tuple):
                d[k] = list(v)
        d["schema_version"] = SCHEMA_VERSION
        return d


# ---- integrity guards --------------------------------------------------------------------


def assert_verbatim(record: dict, field: str, authority_value: str) -> None:
    """A Foundry record's copy of an authority's wording must be byte-identical to it.

    This is the mechanical form of CLAUDE.md rule 4 (never promote a validation rung). Derived
    tags live in a SEPARATE field; this asserts the original survived untouched next to them.
    """
    got = record.get(field)
    if got != authority_value:
        raise SchemaError("%r is not verbatim: record has %r, authority has %r"
                          % (field, got, authority_value))


def scoring_admissible(confidence: str) -> bool:
    """True when a relation of this confidence may be an input to automated scoring.

    `llm_suggested` is a hypothesis until a person or a screen rules on it (blueprint §3.4/§7.3).
    """
    if confidence not in RELATION_CONFIDENCES:
        raise SchemaError("bad relation confidence %r" % (confidence,))
    return confidence in SCORING_ADMISSIBLE_CONFIDENCES


def derive_lineage_tags(validation_strength: str) -> tuple:
    """Conservative lineage tags from a MANIFEST `validation_strength` cell.

    The cell is FREE PROSE in this repo (110 rows, ~90 distinct spellings), so tags are keyword
    matches over lowercased text and are additive: a cell naming two strengths gets both, plus
    `mixed_strength`. Nothing here replaces the cell — see `assert_verbatim` — and no tag is ever
    stronger than a word the author actually wrote.
    """
    t = (validation_strength or "").lower()
    tags = set()
    if "post-fit" in t or "post fit" in t or "postfit" in t:
        tags.add("post_fit")
    if "independent" in t:
        tags.add("independent")
    if "digitiz" in t or "digitis" in t or "figure-read" in t or "figure-digitized" in t:
        tags.add("digitized")
    if "same rig" in t or "within-rig" in t or "same apparatus" in t or "same campaign" in t:
        tags.add("same_campaign")
    if "reference" in t:
        tags.add("reference_only")
    if "verification" in t or "verifies" in t or "reproduces" in t:
        tags.add("verification")
    if "qualitative" in t:
        tags.add("qualitative")
    if "measured" in t and "post-fit" not in t:
        tags.add("raw_measurement")
    if not tags:
        tags.add("unclassified")
    # more than one named strength in one cell -> the reader must not collapse it upward
    strength_like = tags & {"post_fit", "independent", "reference_only", "verification",
                            "qualitative", "raw_measurement"}
    if len(strength_like) > 1:
        tags.add("mixed_strength")
    bad = tags - set(LINEAGE_TAGS)
    if bad:
        raise SchemaError("derived unknown lineage tags %r" % sorted(bad))
    return tuple(sorted(tags))


# ---- helpers -----------------------------------------------------------------------------


def source_commit() -> str:
    """The HEAD sha, or `UNKNOWN` outside a git checkout (mirrors `puckworks.public.export`)."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       cwd=str(REPO_ROOT),
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "UNKNOWN"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_path(path) -> str:
    p = Path(path)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else ""


def canonical_json(obj) -> str:
    """Stable JSON for hashing and for tracked generated files (sorted keys, trailing newline)."""
    return json.dumps(obj, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

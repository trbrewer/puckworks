"""Corpus extractors — read the AUTHORITIES into typed records, verbatim.

Sources, in the order the blueprint (§8) names them:

  * the LIVE registry (`puckworks.registry`), never a README table;
  * `docs/cards/*.md` — the source of truth for each model's physics;
  * `puckworks/data/MANIFEST.csv` — dataset lineage, uncertainty, caveats, permitted use;
  * `docs/public/generated/claims.json` — already-published claims, so the Foundry does not
    propose a "new" public story that exists;
  * an ALLOWLIST of standing analyses (never a recursive sweep of every Markdown file).

Three rules the extractors obey and the tests enforce:

  1. **Verbatim.** Every evidence/validation label is carried across byte-identical
     (`schema.assert_verbatim`). Derived tags sit in separate fields.
  2. **Never invent.** A component whose card cannot be resolved gets `card_path=None` and a
     build warning — not a guessed path. Seven components are in that state today (four
     `brewer2026.*` project models, three `sourcing2026.*` aggregators over multiple source
     cards); the map reports them rather than papering over them.
  3. **Label the inference.** Relations read from an authority's own words are `explicit`;
     relations produced by a rule over authority fields are `deterministically_inferred` and
     record the matched text so a reader can check the rule fired for the right reason.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

from . import schema as S
from .schema import Entity, Provenance, Relation

CARDS_DIR = S.REPO_ROOT / "docs" / "cards"
MANIFEST_PATH = S.REPO_ROOT / "puckworks" / "data" / "MANIFEST.csv"
CLAIMS_PATH = S.REPO_ROOT / "docs" / "public" / "generated" / "claims.json"

#: Standing-analysis allowlist (blueprint §8.5). An explicit list, NOT a recursive docs sweep:
#: the Foundry reads verdict documents, and a wildcard over `docs/` would pull in drafts,
#: reviews, and handoffs whose sentences are not standing verdicts.
ANALYSIS_ALLOWLIST = (
    "docs/ANALYSIS_P2.md",
    "docs/ANALYSIS_transfer.md",
    "docs/ANALYSIS_cv_residual.md",
    "docs/P3_hypotheses.md",
    "docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md",
)

#: The card template's canonical headings (`docs/cards/TEMPLATE.md`). A card missing any of these
#: is flagged `template_deviation`, not silently parsed as if the section were empty.
TEMPLATE_SECTIONS = (
    "Scope and mechanism", "Governing equations", "Parameters",
    "Calibration and validation offered by the source", "Assumptions and validity range",
    "Interface mapping", "Extractable data", "Overlaps and conflicts",
    "Implementation estimate",
)

#: Observable aliases for the deterministic model/observable matrix. Matching is over the card's
#: interface/scope/extractable sections only, and every hit records the alias that fired — the
#: matrix is a NAVIGATION aid whose cells are checkable, not a claim about what a model validates.
OBSERVABLE_ALIASES = {
    "pressure": ("pressure", "p_of_t", "bar", "machinestate.p", "pressuretrace"),
    "flow": ("flow rate", "flow-rate", "flow", "q(t)", "flux", "ml/s", "m^3/s"),
    "first_drip_time": ("first drip", "first-drip", "first arrival", "breakthrough time"),
    "wetting_front": ("wetting front", "front position", "filling front", "sharp front",
                      "infiltration front"),
    "permeability": ("permeability", "darcy", "k_m2", "bedstate.k", "kozeny", "kappa"),
    "porosity": ("porosity", "void fraction", "epsilon_b", "eps_b"),
    "extraction_yield": ("extraction yield", "ey_pct", " ey ", "yield"),
    "tds": ("tds", "total dissolved solids", "strength"),
    "species_concentration": ("caffeine", "trigonelline", "chlorogenic", "5-cqa", "cqa",
                              "species", "solute concentration", "analyte"),
    "fraction_history": ("fraction", "timed fractions", "fraction-resolved"),
    "cumulative_mass": ("beverage mass", "beverage_g", "cumulative mass", "extracted mass",
                        "m_d(t)", "dissolved mass"),
    "bed_deformation": ("deformation", "compaction", "swelling", "poroelastic", "bed height",
                        "settling"),
    "fines_distribution": ("fines", "particle migration", "clogging"),
    "temperature": ("temperature", "thermal", "°c", "deg c"),
    "particle_size": ("particle size", "psd", "grind size", "d32", "granulometry"),
}

#: Words that turn a card's "Overlaps and conflicts" mention into a TYPED scientific relation.
#: Absent one of these the edge stays neutral (`CARD_NAMES_IN_OVERLAPS`) — the card named the
#: other component, which is a fact; that they compete is a reading the card must actually state.
_COMPETES_MARKERS = ("compet", "conflict", "supersede", "rival", "disagree", "contradict")
_COMPLEMENTS_MARKERS = ("complement", "orthogonal", "feeds", "provides for", "unblocks")


def _rel(path: Path) -> str:
    """Repo-relative POSIX path, for provenance that reads the same on every machine."""
    return Path(path).resolve().relative_to(S.REPO_ROOT).as_posix()


# ---- registry ----------------------------------------------------------------------------


def extract_registry(commit: str = "") -> tuple:
    """Live registry -> model entities. Returns `(entities, warnings)`.

    `evidence_strength` is copied from the live component and asserted verbatim: the Foundry is
    forbidden from restating a component's validation rung in its own words.
    """
    from puckworks.registry import components, load_builtin_components
    load_builtin_components()

    entities, warnings = [], []
    card_stems = {p.stem for p in CARDS_DIR.glob("*.md")}
    for c in sorted(components(), key=lambda x: x.name):
        card_path, resolution = _resolve_card(c.name, card_stems)
        if card_path is None:
            warnings.append("UNRESOLVED_CARD: component %r has no card at docs/cards/%s.md or "
                            "docs/cards/%s.md" % (c.name, c.name.replace(".", "_"),
                                                  c.name.split(".")[0]))
        attrs = {
            "registry_name": c.name,
            "stage": c.stage,
            "execution_role": c.execution_role,
            "provenance_class": c.provenance_class,
            "evidence_strength": c.evidence_strength,
            "paper": c.paper,
            "doi": c.doi,
            "module": c.module,
            "assumptions": c.assumptions,
            "valid_range": c.valid_range,
            "gates": [getattr(g, "__name__", str(g)) for g in c.gates],
            "notes": c.notes,
            "card_path": card_path,
            "card_resolution": resolution,
        }
        S.assert_verbatim(attrs, "evidence_strength", c.evidence_strength)
        S.assert_verbatim(attrs, "valid_range", c.valid_range)
        entities.append(Entity(
            id="model:" + c.name, kind="model", label=c.name,
            provenance=Provenance(source_path="puckworks/registry.py",
                                  source_locator="live registry component %r" % c.name,
                                  source_commit=commit, extraction_mode="live_registry",
                                  confidence="explicit"),
            attrs=attrs))
    return entities, warnings


def _resolve_card(component_name: str, card_stems) -> tuple:
    """`(card_path | None, resolution)` for a registry component.

    Two deterministic rules only — full name with dots as underscores, then the source prefix.
    Searching card BODIES for the component id was tried and rejected: the hits are other cards
    citing the component, not its authority, and following them would attribute a model's physics
    to a card that never claimed it.
    """
    full = component_name.replace(".", "_")
    if full in card_stems:
        return "docs/cards/%s.md" % full, "EXACT"
    prefix = component_name.split(".")[0]
    if prefix in card_stems:
        return "docs/cards/%s.md" % prefix, "SOURCE_PREFIX"
    return None, "UNRESOLVED"


# ---- cards -------------------------------------------------------------------------------


def parse_card(path) -> dict:
    """Parse one model card into header metadata + `## ` sections + a per-section hash."""
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    title = lines[0].lstrip("# ").strip() if lines else p.stem
    header = "\n".join(lines[:12])

    def meta(*labels):
        for label in labels:
            m = re.search(r"\*\*%s:?\*\*\s*(.+)" % re.escape(label), header)
            if m:
                return m.group(1).strip()
        return ""

    sections, current, buf = {}, None, []
    for line in lines:
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current, buf = m.group(1), []
        elif current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()

    missing = [s for s in TEMPLATE_SECTIONS if s not in sections]
    return {
        "card_id": p.stem,
        "card_path": _rel(p),
        "title": title,
        "paper": meta("Paper/thesis", "Paper", "Source"),
        "stages": meta("Stage(s)", "Stages", "Stage"),
        "kind": meta("Kind"),
        "status": meta("Status"),
        "sections": sections,
        "section_hashes": {k: S.sha256_text(v) for k, v in sections.items()},
        "missing_template_sections": missing,
        "template_deviation": bool(missing),
        "card_sha256": S.sha256_text(text),
    }


def extract_cards(commit: str = "") -> tuple:
    """All model cards -> card entities. Returns `(entities, warnings)`.

    Every card is a node, including the ~80 carded-but-unimplemented sources: the gap between
    "carded" and "registered" is itself a thing the atlas reads.
    """
    entities, warnings = [], []
    for p in sorted(CARDS_DIR.glob("*.md")):
        if p.stem == "TEMPLATE":
            continue
        card = parse_card(p)
        if card["template_deviation"]:
            warnings.append("TEMPLATE_DEVIATION: %s is missing %s"
                            % (card["card_path"], ", ".join(card["missing_template_sections"])))
        entities.append(Entity(
            id="card:" + card["card_id"], kind="card", label=card["title"],
            provenance=Provenance(source_path=card["card_path"], source_locator="whole card",
                                  source_commit=commit,
                                  extraction_mode="structured_card_section",
                                  confidence="explicit"),
            attrs={k: v for k, v in card.items() if k != "sections"} |
                  {"section_names": sorted(card["sections"])}))
    return entities, warnings


def card_sections(card_id: str) -> dict:
    """Section text for one card (kept out of the map payload, which stores hashes only)."""
    p = CARDS_DIR / (card_id + ".md")
    return parse_card(p)["sections"] if p.exists() else {}


# ---- manifest ----------------------------------------------------------------------------


def extract_manifest(commit: str = "") -> tuple:
    """`MANIFEST.csv` -> dataset entities. Returns `(entities, warnings)`.

    `validation_strength` and `caveat` are carried verbatim; `lineage_tags` is the derived,
    conservative, additive companion (`schema.derive_lineage_tags`).
    """
    entities, warnings = [], []
    if not MANIFEST_PATH.exists():
        return entities, ["MISSING_MANIFEST: %s" % _rel(MANIFEST_PATH)]

    card_stems = {p.stem for p in CARDS_DIR.glob("*.md")}
    with MANIFEST_PATH.open(newline="", encoding="utf-8") as fh:
        for i, row in enumerate(csv.DictReader(fh), start=2):
            ds_id = (row.get("dataset_id") or "").strip()
            if not ds_id:
                warnings.append("MANIFEST_ROW_NO_ID: line %d" % i)
                continue
            attrs = {k: (v or "").strip() for k, v in row.items()}
            attrs["manifest_line"] = i
            attrs["lineage_tags"] = list(S.derive_lineage_tags(row.get("validation_strength", "")))
            attrs["uncertainty_retained_flag"] = attrs.get("uncertainty_retained", "").lower() in (
                "y", "yes", "true")
            # resolved here, at record construction, so no consumer depends on a later extractor
            # having run first to populate the field
            src_card = attrs.get("source_card", "")
            resolved = resolve_source_card(src_card, card_stems) if src_card else None
            attrs["source_card_resolved"] = resolved or ""
            if src_card and not resolved:
                warnings.append("MANIFEST_SOURCE_CARD_UNRESOLVED: row %d (dataset %s) names "
                                "source_card %r, which is not a card stem under docs/cards/"
                                % (i, ds_id, src_card))
            S.assert_verbatim(attrs, "validation_strength",
                              (row.get("validation_strength") or "").strip())
            S.assert_verbatim(attrs, "caveat", (row.get("caveat") or "").strip())
            entities.append(Entity(
                id="dataset:" + ds_id, kind="dataset", label=ds_id,
                provenance=Provenance(source_path=_rel(MANIFEST_PATH),
                                      source_locator="row %d (dataset_id=%s)" % (i, ds_id),
                                      source_commit=commit, extraction_mode="csv_row",
                                      confidence="explicit"),
                attrs=attrs))
    return entities, warnings


# ---- public claims -----------------------------------------------------------------------


def extract_claims(commit: str = "") -> tuple:
    """Generated public claims -> claim entities (blueprint §8.4).

    Reads the GENERATED registry rather than `puckworks.public.claims`, so the Foundry sees what
    was actually published, with its badge and payload hash.
    """
    entities, warnings = [], []
    if not CLAIMS_PATH.exists():
        return entities, ["MISSING_CLAIMS: %s (run the public exporter)" % _rel(CLAIMS_PATH)]

    claims = json.loads(CLAIMS_PATH.read_text(encoding="utf-8"))
    for c in claims:
        attrs = {
            "claim_id": c.get("claim_id", ""),
            "public_question": c.get("public_question", ""),
            "headline": c.get("headline", ""),
            "evidence_strength": c.get("evidence_strength", ""),
            "badge": c.get("badge", ""),
            "dataset_manifest_ids": c.get("dataset_manifest_ids", []),
            "components": c.get("components", []),
            "primary_caveat": c.get("primary_caveat", ""),
            "validity_range": c.get("validity_range", ""),
            "producer": (c.get("producer") or {}).get("ref", ""),
            "reproduction": c.get("reproduction", ""),
            "payload_sha256": c.get("payload_sha256", ""),
            "claim_source_commit": c.get("source_commit", ""),
        }
        S.assert_verbatim(attrs, "evidence_strength", c.get("evidence_strength", ""))
        S.assert_verbatim(attrs, "badge", c.get("badge", ""))
        entities.append(Entity(
            id="claim:" + c.get("claim_id", "?"), kind="claim",
            label=c.get("headline", "")[:120],
            provenance=Provenance(source_path=_rel(CLAIMS_PATH),
                                  source_locator="claim %s" % c.get("claim_id", "?"),
                                  source_commit=commit, extraction_mode="generated_claim_registry",
                                  confidence="explicit"),
            attrs=attrs))
    return entities, warnings


# ---- standing analyses -------------------------------------------------------------------

#: Verdict markers scanned for in the allowlisted analyses (blueprint §9.10 Lens J). A hit is a
#: POINTER to a line a human should read, never a parsed conclusion.
_NEGATIVE_MARKERS = (
    "does not transfer", "worse than baseline", "unphysical", "non-identifiable",
    "nonidentifiable", "retired", "indeterminate", "negative result", "downgraded",
    "not validated", "fails", "no effect",
)


def extract_results(commit: str = "") -> tuple:
    """Allowlisted standing analyses -> result entities with verdict-marker pointers."""
    entities, warnings = [], []
    for rel in ANALYSIS_ALLOWLIST:
        p = S.REPO_ROOT / rel
        if not p.exists():
            warnings.append("MISSING_ANALYSIS: %s (allowlisted but absent)" % rel)
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        markers = []
        for n, line in enumerate(lines, start=1):
            low = line.lower()
            for m in _NEGATIVE_MARKERS:
                if m in low:
                    markers.append({"line": n, "marker": m, "text": line.strip()[:240]})
                    break
        entities.append(Entity(
            id="result:" + Path(rel).stem, kind="result", label=Path(rel).stem,
            provenance=Provenance(source_path=rel, source_locator="whole document",
                                  source_commit=commit, extraction_mode="allowlisted_analysis",
                                  confidence="explicit"),
            attrs={"path": rel, "n_lines": len(lines),
                   "negative_marker_hits": markers[:80],
                   "n_negative_markers": len(markers),
                   "sha256": S.sha256_text(text),
                   "classification": "standing_verdict"}))
    return entities, warnings


# ---- observables + derived relations -----------------------------------------------------


def observable_entities(commit: str = "") -> list:
    """One entity per named observable — the columns of the model/observable matrix."""
    return [Entity(id="observable:" + o, kind="observable", label=o.replace("_", " "),
                   provenance=Provenance(source_path="puckworks/insights/schema.py",
                                         source_locator="OBSERVABLES",
                                         source_commit=commit,
                                         extraction_mode="foundry_vocabulary",
                                         confidence="deterministically_inferred"),
                   attrs={"observable": o})
            for o in S.OBSERVABLES]


def observables_in_text(text: str) -> dict:
    """`{observable: matched alias}` for aliases occurring in `text` (lowercased substring)."""
    low = " " + (text or "").lower().replace("\n", " ") + " "
    hits = {}
    for obs, aliases in OBSERVABLE_ALIASES.items():
        for alias in aliases:
            if alias in low:
                hits[obs] = alias
                break
    return hits


def split_interface_mapping(text: str) -> dict:
    """Split an `Interface mapping` section into its `Inputs consumed` / `Outputs produced` clauses.

    Returns `{"inputs": str, "outputs": str, "rest": str, "has_outputs_marker": bool}`. The card
    template writes the section as prose with those two labels; 15 of the 20 carded components use
    them. Where the labels are absent the whole section comes back as `rest` and the caller must
    say so — see `model_observable_relations`.
    """
    body = text or ""
    m_in = re.search(r"\*{0,2}Inputs consumed:?\*{0,2}", body)
    m_out = re.search(r"\*{0,2}Outputs produced:?\*{0,2}", body)
    m_cpl = re.search(r"\*{0,2}Couplings:?\*{0,2}", body)
    if not m_out:
        return {"inputs": body[m_in.end():] if m_in else "", "outputs": "",
                "rest": body if not m_in else body[:m_in.start()],
                "has_outputs_marker": False}
    inputs = body[m_in.end():m_out.start()] if m_in else ""
    end = m_cpl.start() if (m_cpl and m_cpl.start() > m_out.end()) else len(body)
    return {"inputs": inputs, "outputs": body[m_out.end():end],
            "rest": body[:m_in.start()] if m_in else "", "has_outputs_marker": True}


def model_observable_relations(model_entities, commit: str = "") -> tuple:
    """Observable edges for each model, read from its card's `Interface mapping` section only.

    An earlier version scanned scope/equations/extractable text too. It matched an alias for
    almost every observable on almost every model (369 edges over 27 models × 15 observables) and
    the resulting matrix said nothing — "flow" and "kappa" appear in the prose of every hydraulics
    card whether or not the model produces them. The section that states what a component
    CONSUMES and PRODUCES is the one that answers the question, so it is the only one scanned:

      * alias inside `Outputs produced:`  -> `PREDICTS`
      * alias inside `Inputs consumed:`   -> `USES`
      * section present but unlabelled    -> `PREDICTS`, `extraction_mode` records the weaker read
      * no `Interface mapping` at all     -> NO edges, and a warning naming the card

    Every edge stores the alias and clause that fired, so any cell of the matrix is checkable.
    """
    rels, warnings = [], []
    for m in model_entities:
        card_path = m.attrs.get("card_path")
        if not card_path:
            continue
        sections = card_sections(Path(card_path).stem)
        section = sections.get("Interface mapping", "")
        if not section:
            warnings.append("NO_INTERFACE_MAPPING: %s (component %s) — no observable edges "
                            "inferred" % (card_path, m.label))
            continue
        parts = split_interface_mapping(section)
        if parts["has_outputs_marker"]:
            clauses = (("PREDICTS", "Outputs produced", parts["outputs"],
                        "interface_outputs_clause"),
                       ("USES", "Inputs consumed", parts["inputs"], "interface_inputs_clause"))
        else:
            clauses = (("PREDICTS", "Interface mapping (no Outputs marker)", section,
                        "interface_section_no_outputs_marker"),)
        for rtype, locator, clause, mode in clauses:
            for obs, alias in observables_in_text(clause).items():
                rels.append(Relation(
                    type=rtype, source=m.id, target="observable:" + obs,
                    provenance=Provenance(source_path=card_path, source_locator=locator,
                                          source_commit=commit, extraction_mode=mode,
                                          confidence="deterministically_inferred"),
                    attrs={"matched_alias": alias, "clause": locator}))
    return _dedupe_relations(rels), warnings


def dataset_relations(dataset_entities, model_entities, commit: str = "") -> tuple:
    """Dataset edges: to its source card (explicit), to observables and to same-source models.

    The same-source edge is the lineage lens's raw material: a model evaluated against a dataset
    from its OWN source card is not independent of it, whatever a later summary might say.
    """
    rels, warnings = [], []
    by_prefix = {}
    for m in model_entities:
        by_prefix.setdefault(m.label.split(".")[0], []).append(m)

    for d in dataset_entities:
        # both fields were resolved in extract_manifest, which also raised the warning
        src_card = d.attrs.get("source_card", "")
        resolved = d.attrs.get("source_card_resolved", "")
        if resolved:
            rels.append(Relation(
                type="DERIVED_FROM", source=d.id, target="card:" + resolved,
                provenance=Provenance(source_path=_rel(MANIFEST_PATH),
                                      source_locator="row %s, column source_card"
                                                     % d.attrs.get("manifest_line", "?"),
                                      source_commit=commit, extraction_mode="csv_row",
                                      confidence="explicit"),
                attrs={"source_card_as_written": src_card, "resolved_to": resolved}))
        blob = " ".join([d.attrs.get("source_artifact", ""), d.attrs.get("units_as_published", ""),
                         d.attrs.get("gate_use", ""), d.label])
        for obs, alias in observables_in_text(blob).items():
            rels.append(Relation(
                type="MEASURES", source=d.id, target="observable:" + obs,
                provenance=Provenance(source_path=_rel(MANIFEST_PATH),
                                      source_locator="row %s (source_artifact/units/gate_use)"
                                                     % d.attrs.get("manifest_line", "?"),
                                      source_commit=commit,
                                      extraction_mode="manifest_alias_match",
                                      confidence="deterministically_inferred"),
                attrs={"matched_alias": alias}))
        # match the component's source prefix against the cell as written AND as resolved, so a
        # card stem carrying a suffix (romancorrochano2017_extraction) still finds its component
        keys = {k for k in (src_card, resolved) if k}
        keys |= {k.split("_")[0] for k in list(keys)}
        for m in sorted({m.id: m for k in keys for m in by_prefix.get(k, [])}.values(),
                        key=lambda x: x.id):
            rels.append(Relation(
                type="CALIBRATED_FROM", source=m.id, target=d.id,
                provenance=Provenance(source_path=_rel(MANIFEST_PATH),
                                      source_locator="row %s: source_card=%s matches the "
                                                     "component's source prefix"
                                                     % (d.attrs.get("manifest_line", "?"), src_card),
                                      source_commit=commit,
                                      extraction_mode="shared_source_card",
                                      confidence="deterministically_inferred"),
                attrs={"note": "same source card — NOT an independence claim in either direction",
                       "dataset_validation_strength": d.attrs.get("validation_strength", "")}))
    return _dedupe_relations(rels), warnings


def overlap_relations(model_entities, commit: str = "") -> tuple:
    """Edges read from each card's `Overlaps and conflicts` section.

    A mention is a fact (`CARD_NAMES_IN_OVERLAPS`, `explicit`). It is upgraded to `COMPETES_WITH`
    or `COMPLEMENTS` only when the sentence containing the mention says so in the card's own
    words — the card's judgement, not the extractor's.
    """
    rels, warnings = [], []
    known = {m.label for m in model_entities}
    for m in model_entities:
        card_path = m.attrs.get("card_path")
        if not card_path:
            continue
        sections = card_sections(Path(card_path).stem)
        text = sections.get("Overlaps and conflicts") or sections.get("Overlaps") or ""
        if not text:
            continue
        for other in sorted(known):
            if other == m.label or other not in text:
                continue
            sentence = _sentence_containing(text, other)
            low = sentence.lower()
            rtype = "CARD_NAMES_IN_OVERLAPS"
            if any(k in low for k in _COMPETES_MARKERS):
                rtype = "COMPETES_WITH"
            elif any(k in low for k in _COMPLEMENTS_MARKERS):
                rtype = "COMPLEMENTS"
            rels.append(Relation(
                type=rtype, source=m.id, target="model:" + other,
                provenance=Provenance(source_path=card_path,
                                      source_locator="Overlaps and conflicts",
                                      source_commit=commit,
                                      extraction_mode="structured_card_section",
                                      confidence="explicit"),
                attrs={"quoted": sentence[:300]}))
    return _dedupe_relations(rels), warnings


def claim_relations(claim_entities, known_ids, commit: str = "") -> tuple:
    """`dataset --SUPPORTS_CLAIM--> claim` edges from the claim's own binding fields.

    A claim citing a dataset id the manifest does not contain is a WARNING, not a dropped edge:
    it means a published claim points at data that has moved or been renamed.
    """
    rels, warnings = [], []
    for c in claim_entities:
        for ds in c.attrs.get("dataset_manifest_ids", []):
            target = "dataset:" + ds
            if target not in known_ids:
                warnings.append("CLAIM_DATASET_UNRESOLVED: %s cites %r, not in MANIFEST"
                                % (c.id, ds))
                continue
            rels.append(Relation(
                type="SUPPORTS_CLAIM", source=target, target=c.id,
                provenance=Provenance(source_path=_rel(CLAIMS_PATH),
                                      source_locator="%s.dataset_manifest_ids" % c.attrs["claim_id"],
                                      source_commit=commit,
                                      extraction_mode="generated_claim_registry",
                                      confidence="explicit"),
                attrs={"badge": c.attrs.get("badge", "")}))
    return _dedupe_relations(rels), warnings


def resolve_source_card(value: str, card_stems) -> str | None:
    """Resolve a MANIFEST `source_card` cell to a card stem, or `None`.

    The column is free text and four cells today are not bare stems: one names two cards
    (`"wadsworth2026_grindmap / wadsworth2026 (one paper)"`), one carries a parenthetical, one
    (`"romancorrochano2017"`) is a source prefix whose card is `romancorrochano2017_extraction`,
    and one (`"(registry [RS])"`) names no card at all. The rules below are ordered and each is
    reversible by eye; a cell that survives all of them returns `None` and is WARNED about rather
    than attached to a plausible-looking neighbour.
    """
    raw = (value or "").strip()
    if raw in card_stems:
        return raw
    first = raw.split("/")[0]                       # "a / b (one paper)" -> "a "
    first = re.sub(r"\(.*?\)", "", first).strip()   # drop parentheticals
    if first in card_stems:
        return first
    # a source PREFIX whose card carries a suffix, but only when that card is unambiguous
    if first:
        matches = sorted(s for s in card_stems if s.startswith(first + "_"))
        if len(matches) == 1:
            return matches[0]
    return None


def _sentence_containing(text: str, needle: str) -> str:
    for chunk in re.split(r"(?<=[.;])\s+|\n", text):
        if needle in chunk:
            return chunk.strip()
    return text[:300].strip()


def _dedupe_relations(rels):
    """Collapse duplicate edges, keeping the first (and its provenance)."""
    seen, out = set(), []
    for r in rels:
        key = (r.type, r.source, r.target, r.provenance.source_locator)
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
    return out

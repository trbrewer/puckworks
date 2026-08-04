"""Corpus map — the machine-readable graph of what the repository knows.

`build()` returns entities + relations + build warnings, all commit-pinned and source-bound.
The map is a NAVIGATION layer: it holds identifiers, labels, verbatim authority fields, and
typed edges. It holds no verdicts, and it is not an authority for anything — a consumer that
needs a model's physics follows `card_path` to the card (blueprint §4.2).

Counts are always computed from the tree (blueprint §4.3). Nothing downstream may hand-maintain
"27 models" in prose; it asks the map.
"""
from __future__ import annotations

from . import extract, schema as S

GENERATOR_VERSION = 1


def build(commit: str | None = None) -> dict:
    """Build the corpus map. Deterministic for a given tree — no wall clock, no ordering by set."""
    commit = S.source_commit() if commit is None else commit
    warnings = []

    models, w = extract.extract_registry(commit);      warnings += w
    cards, w = extract.extract_cards(commit);          warnings += w
    datasets, w = extract.extract_manifest(commit);    warnings += w
    claims, w = extract.extract_claims(commit);        warnings += w
    results, w = extract.extract_results(commit);      warnings += w
    observables = extract.observable_entities(commit)

    entities = models + cards + datasets + claims + results + observables
    ids = {e.id for e in entities}

    relations = []
    r, w = extract.model_observable_relations(models, commit);          relations += r; warnings += w
    r, w = extract.dataset_relations(datasets, models, commit);         relations += r; warnings += w
    r, w = extract.overlap_relations(models, commit);                   relations += r; warnings += w
    r, w = extract.claim_relations(claims, ids, commit);                relations += r; warnings += w
    relations += _shared_observable_relations(relations, commit)

    # dangling edges are a build DEFECT, not a silent drop: an edge to an id the map does not
    # contain means an extractor invented a target or an authority moved underneath us.
    dangling = [r for r in relations if r.source not in ids or r.target not in ids]
    for d in dangling:
        warnings.append("DANGLING_RELATION: %s %s -> %s" % (d.type, d.source, d.target))
    relations = [r for r in relations if r.source in ids and r.target in ids]

    return {
        "schema_version": S.SCHEMA_VERSION,
        "generator_version": GENERATOR_VERSION,
        "commit": commit,
        "entities": [e.as_dict() for e in entities],
        "relations": [r.as_dict() for r in relations],
        "warnings": sorted(set(warnings)),
        "counts": counts(entities, relations),
        "inputs": _input_hashes(),
    }


def _shared_observable_relations(relations, commit: str):
    """`model --SHARES_OBSERVABLE_WITH--> model` wherever two models predict the same observable.

    This is the deterministic precondition of Lens A: sharing an observable makes two models
    COMPARABLE. It does not make them disagree — that requires matched-scenario execution, which
    the foundation does not do and does not fake (see `docs/insights/INSIGHT_FOUNDRY_DESIGN.md`
    §5, and RP-A in ROADMAP §9 for the execution programme this defers to).
    """
    from .schema import Provenance, Relation
    by_obs = {}
    for r in relations:
        if r.type == "PREDICTS":
            by_obs.setdefault(r.target, []).append(r)

    out = []
    for obs, rs in sorted(by_obs.items()):
        srcs = sorted({r.source for r in rs})
        for i, a in enumerate(srcs):
            for b in srcs[i + 1:]:
                where = {r.source: r for r in rs}
                out.append(Relation(
                    type="SHARES_OBSERVABLE_WITH", source=a, target=b,
                    provenance=Provenance(
                        source_path=where[a].provenance.source_path,
                        source_locator="both cards name %s (%s / %s)"
                                       % (obs.split(":")[-1],
                                          where[a].provenance.source_path,
                                          where[b].provenance.source_path),
                        source_commit=commit, extraction_mode="shared_observable_join",
                        confidence="deterministically_inferred"),
                    attrs={"observable": obs,
                           "a_alias": where[a].attrs.get("matched_alias", ""),
                           "b_alias": where[b].attrs.get("matched_alias", "")}))
    return out


def counts(entities, relations) -> dict:
    """Generated counts — the only place prose may get its numbers from (blueprint §4.3)."""
    by_kind, by_rel = {}, {}
    for e in entities:
        by_kind[e.kind] = by_kind.get(e.kind, 0) + 1
    for r in relations:
        by_rel[r.type] = by_rel.get(r.type, 0) + 1
    by_stage, by_evidence = {}, {}
    for e in entities:
        if e.kind == "model":
            st = e.attrs.get("stage", "?")
            ev = e.attrs.get("evidence_strength") or "unassigned"
            by_stage[st] = by_stage.get(st, 0) + 1
            by_evidence[ev] = by_evidence.get(ev, 0) + 1
    return {
        "entities_total": len(entities),
        "relations_total": len(relations),
        "entities_by_kind": dict(sorted(by_kind.items())),
        "relations_by_type": dict(sorted(by_rel.items())),
        "models_by_stage": dict(sorted(by_stage.items())),
        "models_by_evidence_strength": dict(sorted(by_evidence.items())),
    }


def _input_hashes() -> list:
    """sha256 of every file the map was built from — the staleness detector (blueprint §19.7)."""
    paths = ["puckworks/registry.py", "puckworks/data/MANIFEST.csv",
             "docs/public/generated/claims.json"] + list(extract.ANALYSIS_ALLOWLIST)
    out = []
    for rel in paths:
        p = S.REPO_ROOT / rel
        if p.exists():
            out.append({"path": rel, "sha256": S.sha256_path(p)})
    for p in sorted(extract.CARDS_DIR.glob("*.md")):
        out.append({"path": extract._rel(p), "sha256": S.sha256_path(p)})
    return out


# ---- convenience views -------------------------------------------------------------------


def index(corpus: dict) -> dict:
    """`{entity id: entity dict}`."""
    return {e["id"]: e for e in corpus["entities"]}


def entities_of(corpus: dict, kind: str) -> list:
    return [e for e in corpus["entities"] if e["kind"] == kind]


def relations_of(corpus: dict, rtype: str) -> list:
    return [r for r in corpus["relations"] if r["type"] == rtype]


def model_observable_matrix(corpus: dict) -> tuple:
    """`(header, rows)` for the model/observable matrix (blueprint §15.2).

    Cells are `predicts` (the card names the observable) or `-`. There is no `validates` cell:
    the foundation has no evidence that a model was VALIDATED on an observable, and printing one
    would be exactly the promotion CLAUDE.md rule 4 forbids.
    """
    preds = {}
    for r in relations_of(corpus, "PREDICTS"):
        preds.setdefault(r["source"], set()).add(r["target"].split(":")[-1])
    models = sorted(e["id"] for e in entities_of(corpus, "model"))
    header = ["model", "stage", "evidence_strength"] + list(S.OBSERVABLES)
    idx = index(corpus)
    rows = []
    for m in models:
        a = idx[m]["attrs"]
        rows.append([m.split(":", 1)[1], a.get("stage", ""), a.get("evidence_strength") or ""] +
                    ["predicts" if o in preds.get(m, ()) else "-" for o in S.OBSERVABLES])
    return header, rows

"""Tension atlas — where the corpus disagrees with itself, and what would settle it.

A tension row is NOT a finding. It is a source-bound statement that two parts of the repository
are comparable and differ in some declared respect, plus the observable that would separate them.
Every row cites the authorities it was read from; no lens writes a verdict; `human_status` starts
at `UNREVIEWED` and only a person moves it.

Ten of the blueprint's thirteen lenses (§9) are implemented here. Three are NOT, on purpose, and
the atlas says so in `DEFERRED_LENSES` rather than emitting weak rows to look complete:

  * **B observational equivalence** and **F regime transition** need matched-scenario EXECUTION of
    the components — that is RP-A's programme (ROADMAP §9), which has its own spec and gates. A
    static read of the cards cannot tell you two models agree numerically, and a row asserting it
    would be the automated scientific verdict this layer is forbidden to produce.
  * **G hidden discriminator** is implemented only in its data-availability half (which observable
    is predicted by several models), not its ranking half (`between-model separation / within-model
    uncertainty`), which is again an execution quantity.

The lenses take the corpus map and nothing else, so a row can always be re-derived from a commit.
"""
from __future__ import annotations

from . import ids as IDS
from .corpus_map import entities_of, index, relations_of
from .schema import Provenance, Tension

#: Lenses the foundation does not implement, and why. Surfaced in the generated atlas so a reader
#: knows a lens is absent by decision rather than by oversight.
DEFERRED_LENSES = {
    "observational_equivalence": "needs matched-scenario execution of the components "
                                 "(ROADMAP §9 RP-A); a card read cannot establish numerical "
                                 "agreement",
    "regime_transition": "needs a dimensionless-group sweep per component (RP-A/RP-C); the cards "
                         "declare validity ranges in prose, not comparable thresholds",
    "hidden_discriminator_ranking": "separation/uncertainty ranking is an execution quantity; the "
                                    "availability half of Lens G is implemented",
}

#: Registry evidence strengths that are NOT an empirical test of the model against data.
#: Used by Lens K to spot prominence/evidence asymmetry; the terms are the registry's own
#: (`puckworks.registry.EVIDENCE_STRENGTHS`) and are never restated.
_WEAK_EVIDENCE = ("qualitative_capacity", "exploratory_synthesis", "code_verification",
                  "sign_or_compatibility", "proposed_experiment")


def build(corpus: dict, allocator=None) -> list:
    """Run every implemented lens over the corpus map and return the atlas rows, IDs assigned.

    Rows are SORTED for stable presentation but their IDs come from the fingerprint registry, not
    from sort position — inserting an early-sorting row must not renumber the rows after it
    (`puckworks.insights.ids`).
    """
    rows = []
    for lens in (lens_model_disagreement, lens_lineage_circularity,
                 lens_calibration_artifact_portability, lens_composition_failure,
                 lens_cross_species, lens_hidden_discriminator, lens_matrix_blind_spot,
                 lens_missing_experiment, lens_negative_result, lens_evidence_asymmetry,
                 lens_scale_mismatch, lens_public_story):
        rows.extend(lens(corpus))
    rows.sort(key=lambda t: (t.lens, tuple(t.entity_ids), t.difference_summary))
    alloc = allocator if allocator is not None else IDS.Allocator()
    for t in rows:
        t.tension_id = alloc.tension_id(t)
    return rows


def _prov(entity_or_dict, locator="", commit="", mode="corpus_map_join",
          confidence="deterministically_inferred") -> Provenance:
    # accepts either an entity dict (which nests its provenance) or a provenance dict directly
    p = entity_or_dict
    if isinstance(p, dict) and "provenance" in p:
        p = p["provenance"]
    return Provenance(source_path=p["source_path"],
                      source_locator=locator or p.get("source_locator", ""),
                      source_commit=commit or p.get("source_commit", ""),
                      extraction_mode=mode, confidence=confidence)


# ---- Lens A — model disagreement ---------------------------------------------------------


def lens_model_disagreement(corpus: dict) -> list:
    """Pairs of models that answer the same question and are declared differently.

    Two triggers, kept separate because their evidence differs:

      * a card's own `Overlaps and conflicts` section calls another component a competitor
        (`COMPETES_WITH`, confidence `explicit`) — the repository already asserts the tension;
      * two models share an observable and sit in the same stage (`deterministically_inferred`) —
        they are COMPARABLE. Whether they actually differ numerically is unresolved here (see
        `DEFERRED_LENSES`), and the row says so in `difference_type`.
    """
    idx, rows = index(corpus), []
    for r in relations_of(corpus, "COMPETES_WITH"):
        a, b = idx.get(r["source"]), idx.get(r["target"])
        if not (a and b):
            continue
        rows.append(Tension(
            tension_id="", lens="model_disagreement", entity_ids=(a["id"], b["id"]),
            shared_domain="%s / %s" % (a["attrs"].get("stage"), b["attrs"].get("stage")),
            difference_type="declared_competitor",
            difference_summary="%s's card names %s as a competitor/conflict: %s"
                               % (a["label"], b["label"],
                                  (r["attrs"].get("quoted") or "")[:200]),
            evidence_basis="%s (%s) vs %s (%s) — registry evidence strengths, verbatim"
                           % (a["label"], a["attrs"].get("evidence_strength"),
                              b["label"], b["attrs"].get("evidence_strength")),
            why_it_matters="A competitor named by the source card is a disagreement the "
                           "repository already owns; what is missing is a matched run.",
            candidate_discriminator="an observable both predict, run under one matched scenario",
            data_available="UNKNOWN", cheap_test_possible="UNKNOWN",
            provenance=(_prov(r["provenance"], mode="structured_card_section",
                              confidence="explicit"),)))

    stage_pairs = {}
    for r in relations_of(corpus, "SHARES_OBSERVABLE_WITH"):
        a, b = idx.get(r["source"]), idx.get(r["target"])
        if not (a and b) or a["attrs"].get("stage") != b["attrs"].get("stage"):
            continue
        key = (a["id"], b["id"])
        stage_pairs.setdefault(key, []).append(r)

    for (aid, bid), rs in sorted(stage_pairs.items()):
        a, b = idx[aid], idx[bid]
        obs = sorted({r["attrs"]["observable"].split(":")[-1] for r in rs})
        rows.append(Tension(
            tension_id="", lens="model_disagreement", entity_ids=(aid, bid),
            shared_observable=", ".join(obs), shared_domain=a["attrs"].get("stage", ""),
            difference_type="comparable_not_yet_executed",
            difference_summary="%s and %s both operate on stage %s and both name %s among their "
                               "interface outputs. Whether they agree is NOT established here."
                               % (a["label"], b["label"], a["attrs"].get("stage"), ", ".join(obs)),
            evidence_basis="evidence strengths (verbatim): %s=%s, %s=%s"
                           % (a["label"], a["attrs"].get("evidence_strength"),
                              b["label"], b["attrs"].get("evidence_strength")),
            why_it_matters="Comparability is the precondition for a disagreement result; the "
                           "matched run is RP-A's job, not this layer's.",
            candidate_discriminator=", ".join(obs),
            data_available="UNKNOWN", cheap_test_possible="YES",
            provenance=tuple(_prov(r["provenance"]) for r in rs[:4])))
    return rows


# ---- Lens E — data-lineage circularity ---------------------------------------------------


def lens_lineage_circularity(corpus: dict) -> list:
    """Datasets whose own manifest wording names more than one strength, or that a same-source
    model is calibrated from, or whose source card cannot be resolved at all.

    The strongest rows are the `mixed_strength` ones: a cell reading "independent within-rig
    (equilibrium) / post-fit (9-bar Q(t) reproduction)" is BOTH, and a summary that keeps only the
    first half has silently promoted the dataset. The row quotes the cell verbatim so a reader
    never has to trust the tag.
    """
    idx, rows = index(corpus), []
    calibrated = {}
    for r in relations_of(corpus, "CALIBRATED_FROM"):
        calibrated.setdefault(r["target"], []).append(r)

    for d in sorted(entities_of(corpus, "dataset"), key=lambda e: e["id"]):
        a = d["attrs"]
        tags = set(a.get("lineage_tags", []))
        consumers = [idx[r["source"]]["label"] for r in calibrated.get(d["id"], [])
                     if r["source"] in idx]

        if "mixed_strength" in tags:
            rows.append(Tension(
                tension_id="", lens="lineage_circularity", entity_ids=(d["id"],),
                difference_type="mixed_strength_cell",
                difference_summary="MANIFEST validation_strength for %s names more than one "
                                   "strength: %r (derived tags: %s)"
                                   % (d["label"], a.get("validation_strength"),
                                      ", ".join(sorted(tags))),
                evidence_basis="manifest cell, verbatim",
                why_it_matters="A downstream summary that keeps only the stronger half promotes "
                               "the dataset — the upgrade CLAUDE.md rule 4 forbids.",
                candidate_discriminator="which half of the cell each consuming gate actually uses",
                data_available="YES", cheap_test_possible="YES",
                provenance=(_prov(d, mode="csv_row", confidence="explicit"),)))

        if consumers and ("post_fit" in tags or "same_campaign" in tags):
            rows.append(Tension(
                tension_id="", lens="lineage_circularity", entity_ids=(d["id"],),
                difference_type="same_source_consumer",
                difference_summary="%s (%s) shares a source card with the component(s) %s that "
                                   "the manifest links to it; its strength is recorded as %r"
                                   % (d["label"], ", ".join(sorted(tags)), ", ".join(consumers),
                                      a.get("validation_strength")),
                evidence_basis="MANIFEST source_card == component source prefix",
                why_it_matters="A model evaluated on data from its own source is not independent "
                               "of it, whatever a later summary says.",
                candidate_discriminator="an out-of-source dataset measuring the same observable",
                data_available="YES", cheap_test_possible="YES",
                provenance=(_prov(d, mode="csv_row", confidence="explicit"),)))

        if a.get("source_card") and not a.get("source_card_resolved"):
            rows.append(Tension(
                tension_id="", lens="lineage_circularity", entity_ids=(d["id"],),
                difference_type="unresolvable_source_card",
                difference_summary="%s names source_card %r, which resolves to no single card — "
                                   "its lineage cannot be followed mechanically"
                                   % (d["label"], a.get("source_card")),
                evidence_basis="MANIFEST source_card vs docs/cards/ stems",
                why_it_matters="An untraceable lineage cannot be checked for circularity at all.",
                candidate_discriminator="the specific card/chapter the rows were taken from",
                data_available="YES", cheap_test_possible="YES",
                provenance=(_prov(d, mode="csv_row", confidence="explicit"),)))
    return rows


# ---- Lens D — calibration-artifact portability ---------------------------------------------


def lens_calibration_artifact_portability(corpus: dict) -> list:
    """Calibration components carrying a declared validity range, and what might consume them.

    Two words this lens deliberately does NOT use, because the static metadata does not support
    either:

      * **closure.** `execution_role == "calibration"` means the component supplies parameters
        offline. That covers closures, but also lookup tables, geometry generators, reference
        datasets and verification twins. Calling every one of them a closure asserts a functional
        form the registry never stated. The row says *calibration artifact*; the word closure is
        reserved for cases where a card, interface or relation establishes one.
      * **consumer.** Sharing a stage with a runtime component makes it a POSSIBLE DOWNSTREAM
        component, not an established consumer — nothing here checked that the producer's output
        reaches that component's input. `brewer2026.lb_taichi` and `wadsworth2026.inertial` share
        the flow stage; whether one feeds the other is a question, and the screen's first step is
        to answer it.

    `cheap_test_possible` is therefore `UNKNOWN` rather than `YES` wherever a same-stage neighbour
    exists: the screen is cheap only once a path is shown to exist.
    """
    rows = []
    models = sorted(entities_of(corpus, "model"), key=lambda e: e["id"])
    runtime_by_stage = {}
    for m in models:
        if m["attrs"].get("execution_role") == "runtime":
            runtime_by_stage.setdefault(m["attrs"].get("stage"), []).append(m)

    for m in models:
        a = m["attrs"]
        if a.get("execution_role") != "calibration":
            continue
        downstream = runtime_by_stage.get(a.get("stage"), [])
        rows.append(Tension(
            tension_id="", lens="calibration_artifact_portability",
            entity_ids=tuple([m["id"]] + [c["id"] for c in downstream]),
            shared_domain=a.get("stage", ""),
            difference_type="calibration_artifact_producer",
            canonical_discriminator="source_swap_sensitivity",
            difference_summary="%s is a calibration component on stage %s (provenance %s, "
                               "evidence %s). Declared validity: %s. POSSIBLE DOWNSTREAM "
                               "components (same stage, runtime role — a consuming path is NOT "
                               "established): %s"
                               % (m["label"], a.get("stage"), a.get("provenance_class"),
                                  a.get("evidence_strength"),
                                  a.get("valid_range") or "NOT DECLARED",
                                  ", ".join(c["label"] for c in downstream)
                                  or "none registered on this stage"),
            evidence_basis="registry execution_role + valid_range + evidence_strength, verbatim. "
                           "Same-stage co-location only; no output-to-input path was checked.",
            why_it_matters="A calibration artifact fitted in one source and reused in another is "
                           "the commonest silent extrapolation; the declared range is the only "
                           "thing that says when it stops applying.",
            candidate_discriminator="first establish whether any named component actually consumes "
                                    "this artifact, then source-swap sensitivity on that path",
            data_available="YES" if a.get("valid_range") else "NO",
            # a same-stage neighbour is not a consumer, so a screen is only cheap once a path
            # is shown to exist; that check is the screen's first step, not a precondition
            cheap_test_possible="UNKNOWN" if downstream else "NO",
            provenance=(_prov(m, locator="registry component %s (execution_role, valid_range)"
                                         % m["label"], mode="live_registry",
                              confidence="explicit"),)))
    return rows


# ---- Lens C — model-composition failure --------------------------------------------------


def lens_composition_failure(corpus: dict) -> list:
    """Same-source component pairs that need a composition audit before any comparison is designed.

    An earlier version called these `same_source_variant_pair` and described each as a
    base/base-plus-mechanism pair. **Sharing a source prefix does not make two components a
    base/superset pair.** `maille2024.phi_closure` and `maille2024.two_regime` are two calibration
    roles on different stages; `mo2023_2.swelling` and `mo2023_2.coupled_bed` are a reduced and a
    depth-resolved model that the repository keeps side by side on purpose. Only some same-source
    pairs are base/superset, and a held-out base-versus-base-plus-mechanism comparison is
    meaningless for the rest.

    So the row now asks the classification question FIRST — base/superset, alternative reductions,
    or independent components — and only a pair confirmed base/superset proceeds to the held-out
    comparison. The separately evidence-backed generalisation candidate (public claim PV-05, an
    actual measured composition failure) is unaffected and stays its own row.
    """
    idx, rows = index(corpus), []
    by_source = {}
    for m in sorted(entities_of(corpus, "model"), key=lambda e: e["id"]):
        by_source.setdefault(m["label"].split(".")[0], []).append(m)

    for source, group in sorted(by_source.items()):
        if len(group) < 2:
            continue
        for i, a in enumerate(group):
            for b in group[i + 1:]:
                rows.append(Tension(
                    tension_id="", lens="composition_failure", entity_ids=(a["id"], b["id"]),
                    shared_domain="%s / %s" % (a["attrs"].get("stage"), b["attrs"].get("stage")),
                    difference_type="same_source_pair_requires_composition_audit",
                    canonical_discriminator="pair_relationship_classification",
                    difference_summary="%s and %s are both registered from source %s (roles %s / "
                                       "%s; stages %s / %s; evidence %s / %s). Their RELATIONSHIP "
                                       "is unclassified: sharing a source does not make them a "
                                       "base/superset pair, and they may equally be alternative "
                                       "reductions or independent components."
                                       % (a["label"], b["label"], source,
                                          a["attrs"].get("execution_role"),
                                          b["attrs"].get("execution_role"),
                                          a["attrs"].get("stage"), b["attrs"].get("stage"),
                                          a["attrs"].get("evidence_strength"),
                                          b["attrs"].get("evidence_strength")),
                    evidence_basis="registry: two components sharing one source prefix. That is "
                                   "ALL it establishes — no card relation was read as declaring "
                                   "one a superset of the other.",
                    why_it_matters="Only a base/superset pair can be asked whether added physics "
                                   "earns its place; asking it of alternative reductions produces "
                                   "a meaningless comparison.",
                    candidate_discriminator="classify the pair first (base/superset · alternative "
                                            "reductions · independent); only base/superset "
                                            "proceeds to a held-out comparison",
                    data_available="UNKNOWN", cheap_test_possible="UNKNOWN",
                    provenance=(_prov(a, locator="registry component %s" % a["label"],
                                      mode="live_registry", confidence="explicit"),
                                _prov(b, locator="registry component %s" % b["label"],
                                      mode="live_registry", confidence="explicit"))))

    for c in sorted(entities_of(corpus, "claim"), key=lambda e: e["id"]):
        head = (c["attrs"].get("headline") or "").lower()
        if "worse" in head or "made this tested model worse" in head:
            rows.append(Tension(
                tension_id="", lens="composition_failure", entity_ids=(c["id"],),
                difference_type="published_composition_failure",
                difference_summary="Public claim %s already reports a composition failure: %r "
                                   "(badge %s, caveat: %s)"
                                   % (c["attrs"].get("claim_id"), c["attrs"].get("headline"),
                                      c["attrs"].get("badge"),
                                      (c["attrs"].get("primary_caveat") or "")[:160]),
                evidence_basis="generated public claim registry, verbatim",
                why_it_matters="The generalisation — WHICH added mechanisms help — is open; the "
                               "single case is published and scoped.",
                candidate_discriminator="the same base+one-mechanism protocol across other "
                                        "component combinations",
                data_available="YES", cheap_test_possible="YES",
                provenance=(_prov(c, mode="generated_claim_registry", confidence="explicit"),)))
    return rows


# ---- Lens H — cross-species inconsistency -------------------------------------------------


def lens_cross_species(corpus: dict) -> list:
    """Datasets and models touching multi-solute chemistry, where one kinetic story must serve
    several species at once."""
    rows = []
    species_datasets = [d for d in sorted(entities_of(corpus, "dataset"), key=lambda e: e["id"])
                        if any(r["target"] == "observable:species_concentration"
                               for r in relations_of(corpus, "MEASURES") if r["source"] == d["id"])]
    species_models = [m for m in sorted(entities_of(corpus, "model"), key=lambda e: e["id"])
                      if any(r["target"] == "observable:species_concentration"
                             for r in relations_of(corpus, "PREDICTS") if r["source"] == m["id"])]
    if not (species_datasets and species_models):
        return rows
    for m in species_models:
        rows.append(Tension(
            tension_id="", lens="cross_species_inconsistency",
            entity_ids=tuple([m["id"]] + [d["id"] for d in species_datasets[:6]]),
            shared_observable="species_concentration",
            difference_type="one_state_many_species",
            difference_summary="%s predicts per-species concentration (evidence %s). %d "
                               "manifest datasets measure species concentration. Whether one "
                               "hydraulic+transport state explains every species at once is not "
                               "established by the corpus map."
                               % (m["label"], m["attrs"].get("evidence_strength"),
                                  len(species_datasets)),
            evidence_basis="card interface outputs + manifest rows, verbatim labels retained",
            why_it_matters="A shared kinetic state that fits one species and fails another "
                           "points at species-specific diffusion, inventory mis-specification, "
                           "or a measurement-lineage difference.",
            candidate_discriminator="per-species residual structure under one shared fit",
            data_available="YES", cheap_test_possible="YES",
            provenance=(_prov(m, locator="Interface mapping (Outputs produced)",
                              mode="structured_card_section"),) +
                       tuple(_prov(d, mode="csv_row", confidence="explicit")
                             for d in species_datasets[:3])))
    return rows


# ---- Lens G/L — discriminators and missing experiments ------------------------------------


def _observable_support(corpus: dict) -> dict:
    """`{observable id: (predicting models, measuring datasets)}`."""
    support = {o["id"]: ([], []) for o in entities_of(corpus, "observable")}
    for r in relations_of(corpus, "PREDICTS"):
        if r["target"] in support:
            support[r["target"]][0].append(r["source"])
    for r in relations_of(corpus, "MEASURES"):
        if r["target"] in support:
            support[r["target"]][1].append(r["source"])
    return {k: (sorted(set(v[0])), sorted(set(v[1]))) for k, v in support.items()}


def lens_hidden_discriminator(corpus: dict) -> list:
    """Observables that several models predict AND some dataset measures — a discrimination that
    could be attempted with data already in the repository."""
    idx, rows = index(corpus), []
    for obs, (models, datasets) in sorted(_observable_support(corpus).items()):
        if len(models) < 2 or not datasets:
            continue
        rows.append(Tension(
            tension_id="", lens="hidden_discriminator",
            entity_ids=tuple(models + datasets[:6]),
            shared_observable=obs.split(":")[-1],
            difference_type="discriminator_with_data",
            difference_summary="%d registered models name %s among their interface outputs and "
                               "%d manifest dataset(s) measure it: %s"
                               % (len(models), obs.split(":")[-1], len(datasets),
                                  ", ".join(idx[m]["label"] for m in models)),
            evidence_basis="; ".join("%s=%s" % (idx[m]["label"],
                                                idx[m]["attrs"].get("evidence_strength"))
                                     for m in models),
            why_it_matters="Discrimination is possible without new measurement — the cheapest "
                           "kind of decisive screen.",
            candidate_discriminator=obs.split(":")[-1],
            data_available="YES", cheap_test_possible="YES",
            provenance=tuple(_prov(idx[m], locator="Interface mapping (Outputs produced)",
                                   mode="structured_card_section") for m in models[:4])))
    return rows


def lens_matrix_blind_spot(corpus: dict) -> list:
    """Where the model/observable matrix is blind, and what that hides.

    This lens exists because of a defect it found in itself. `first_drip_time` shows ZERO
    predicting models — not because no model predicts first drip, but because `foster2025.md`
    (the sharp-front infiltration card whose headline result is a predicted first-drip time) uses
    non-template headings and has no `Interface mapping` section for the extractor to read. The
    blueprint's own flagship candidate ("first-drip delay as a mechanism discriminator") is
    therefore invisible to the matrix.

    Two row families:

      * `card_without_interface_mapping` — a registered component whose card cannot contribute
        observable edges. The matrix under-reports it, and the fix is a card edit, not code.
      * `measured_but_unmodelled` — an observable datasets measure that no card's outputs clause
        names. Either nothing models it, or a blind spot above is hiding the model that does.
    """
    idx, rows = index(corpus), []
    from .extract import card_sections

    for m in sorted(entities_of(corpus, "model"), key=lambda e: e["id"]):
        card_path = m["attrs"].get("card_path")
        if not card_path:
            continue
        if card_sections(card_path.split("/")[-1][:-3]).get("Interface mapping"):
            continue
        rows.append(Tension(
            tension_id="", lens="hidden_discriminator", entity_ids=(m["id"],),
            difference_type="card_without_interface_mapping",
            difference_summary="%s is registered but its card %s has no `Interface mapping` "
                               "section, so it contributes NO observable edges. Any observable "
                               "it predicts is under-reported by the matrix."
                               % (m["label"], card_path),
            evidence_basis="card section index vs docs/cards/TEMPLATE.md",
            why_it_matters="A blind spot in the matrix reads exactly like an absence of physics. "
                           "first_drip_time shows zero predicting models for this reason.",
            candidate_discriminator="add the template section to the card, then re-run the map",
            data_available="YES", cheap_test_possible="YES",
            provenance=(_prov(m, locator="whole card (no Interface mapping heading)",
                              mode="structured_card_section", confidence="explicit"),)))

    for obs, (models, datasets) in sorted(_observable_support(corpus).items()):
        if models or not datasets:
            continue
        rows.append(Tension(
            tension_id="", lens="hidden_discriminator",
            entity_ids=tuple([obs] + datasets[:6]),
            shared_observable=obs.split(":")[-1],
            difference_type="measured_but_unmodelled",
            difference_summary="%d manifest datasets measure %s and NO card's outputs clause "
                               "names it — either nothing registered models it, or a card "
                               "without an interface section is hiding the one that does"
                               % (len(datasets), obs.split(":")[-1]),
            evidence_basis="manifest MEASURES edges vs card outputs clauses",
            why_it_matters="Measured-but-unmodelled is either a modelling gap or a card gap, and "
                           "the two call for opposite work.",
            candidate_discriminator="which registered component, if any, claims this output",
            data_available="YES", cheap_test_possible="YES",
            provenance=tuple(_prov(idx[d], mode="csv_row", confidence="explicit")
                             for d in datasets[:4])))
    return rows


def lens_missing_experiment(corpus: dict) -> list:
    """Observables several models predict that NO manifest dataset measures — a measurement
    request, ranked ahead of any modelling work that pretends the data exists."""
    idx, rows = index(corpus), []
    for obs, (models, datasets) in sorted(_observable_support(corpus).items()):
        if len(models) < 2 or datasets:
            continue
        rows.append(Tension(
            tension_id="", lens="missing_experiment", entity_ids=tuple(models),
            shared_observable=obs.split(":")[-1],
            difference_type="predicted_but_unmeasured",
            difference_summary="%d registered models name %s among their interface outputs and "
                               "NO manifest dataset measures it: %s"
                               % (len(models), obs.split(":")[-1],
                                  ", ".join(idx[m]["label"] for m in models)),
            evidence_basis="model/observable matrix vs manifest MEASURES edges",
            why_it_matters="Models can disagree about this observable indefinitely because "
                           "nothing in the corpus can referee it.",
            candidate_discriminator="a measurement campaign for %s" % obs.split(":")[-1],
            data_available="NO", cheap_test_possible="NO",
            provenance=tuple(_prov(idx[m], locator="Interface mapping (Outputs produced)",
                                   mode="structured_card_section") for m in models[:4])))
    return rows


# ---- Lens J — negative results ------------------------------------------------------------


def lens_negative_result(corpus: dict) -> list:
    """Standing analyses carrying negative-verdict markers.

    The marker is a POINTER to a line, never a parsed conclusion: the row tells a reader which
    document and which line to go and read.
    """
    rows = []
    for res in sorted(entities_of(corpus, "result"), key=lambda e: e["id"]):
        hits = res["attrs"].get("negative_marker_hits", [])
        if not hits:
            continue
        markers = sorted({h["marker"] for h in hits})
        rows.append(Tension(
            tension_id="", lens="negative_result", entity_ids=(res["id"],),
            difference_type="standing_negative_verdict",
            difference_summary="%s carries %d negative-verdict marker lines (%s). First: L%d %r"
                               % (res["attrs"]["path"], len(hits), ", ".join(markers[:6]),
                                  hits[0]["line"], hits[0]["text"][:140]),
            evidence_basis="allowlisted standing analysis, line pointers only",
            why_it_matters="A recorded negative result is publishable material and protects "
                           "future work from rediscovering it.",
            candidate_discriminator="whether the negative result generalises beyond its "
                                    "tested configuration",
            data_available="YES", cheap_test_possible="YES",
            provenance=(_prov(res, locator="lines %s"
                                           % ", ".join(str(h["line"]) for h in hits[:8]),
                              mode="allowlisted_analysis", confidence="explicit"),)))
    return rows


# ---- Lens K — evidence asymmetry -----------------------------------------------------------


def lens_evidence_asymmetry(corpus: dict) -> list:
    """Components other cards lean on, whose own registry evidence strength is not empirical.

    Prominence is counted as inbound `Overlaps and conflicts` mentions — how often the rest of the
    corpus positions itself against a component. That is a corpus-internal proxy, NOT citation
    count and NOT importance; the row says which terms it compared.
    """
    idx, rows = index(corpus), []
    inbound = {}
    for rtype in ("CARD_NAMES_IN_OVERLAPS", "COMPETES_WITH", "COMPLEMENTS"):
        for r in relations_of(corpus, rtype):
            inbound.setdefault(r["target"], []).append(r)

    for mid, rs in sorted(inbound.items()):
        m = idx.get(mid)
        if not m or m["kind"] != "model":
            continue
        ev = m["attrs"].get("evidence_strength")
        if ev not in _WEAK_EVIDENCE or len(rs) < 2:
            continue
        citing = sorted({idx[r["source"]]["label"] for r in rs if r["source"] in idx})
        rows.append(Tension(
            tension_id="", lens="evidence_asymmetry", entity_ids=tuple([mid] + sorted(
                {r["source"] for r in rs})),
            difference_type="leaned_on_but_not_empirically_tested",
            difference_summary="%s carries registry evidence_strength %r, and %d other cards "
                               "position themselves against it (%s)"
                               % (m["label"], ev, len(citing), ", ".join(citing)),
            evidence_basis="registry evidence_strength (verbatim) vs inbound overlaps mentions",
            why_it_matters="Corpus-internal prominence and evidence strength are different axes; "
                           "where they diverge, a reader may over-read the component.",
            candidate_discriminator="an empirical test of the component on its own stage",
            data_available="UNKNOWN", cheap_test_possible="UNKNOWN",
            provenance=(_prov(m, locator="registry component %s (evidence_strength)" % m["label"],
                              mode="live_registry", confidence="explicit"),) +
                       tuple(_prov(r["provenance"], mode="structured_card_section",
                                   confidence="explicit") for r in rs[:3])))
    return rows


# ---- Lens I — scale mismatch --------------------------------------------------------------


def lens_scale_mismatch(corpus: dict) -> list:
    """Pore-scale solvers and continuum closures that both speak about permeability."""
    idx, rows = index(corpus), []
    perm_models = sorted({r["source"] for r in relations_of(corpus, "PREDICTS")
                          if r["target"] == "observable:permeability"} |
                         {r["source"] for r in relations_of(corpus, "USES")
                          if r["target"] == "observable:permeability"})
    pore = [m for m in perm_models if idx[m]["attrs"].get("stage") in ("flow", "packing")]
    continuum = [m for m in perm_models if idx[m]["attrs"].get("stage") not in ("flow", "packing")]
    if not (pore and continuum):
        return rows
    rows.append(Tension(
        tension_id="", lens="scale_mismatch", entity_ids=tuple(pore + continuum),
        shared_observable="permeability",
        difference_type="pore_scale_vs_continuum",
        difference_summary="Permeability is spoken about at two scales: %s (pore/pack scale) and "
                           "%s (continuum/bed scale). Whether the continuum closures preserve the "
                           "pore-scale trend is not established by the corpus map."
                           % (", ".join(idx[m]["label"] for m in pore),
                              ", ".join(idx[m]["label"] for m in continuum)),
        evidence_basis="; ".join("%s=%s" % (idx[m]["label"],
                                            idx[m]["attrs"].get("evidence_strength"))
                                 for m in pore + continuum),
        why_it_matters="A closure that does not preserve the pore-scale trend silently limits "
                       "every bed-scale prediction built on it.",
        candidate_discriminator="RVE size at which permeability stabilises; closure vs solver on "
                                "one geometry family",
        data_available="UNKNOWN", cheap_test_possible="UNKNOWN",
        provenance=tuple(_prov(idx[m], locator="registry component %s" % idx[m]["label"],
                               mode="live_registry", confidence="explicit")
                         for m in (pore + continuum)[:5])))
    return rows


# ---- Lens M — public-story extraction ------------------------------------------------------


def lens_public_story(corpus: dict) -> list:
    """Tensions with data already in hand and no published claim covering them.

    Every row is checked against the GENERATED claim inventory first (blueprint §19.3): the
    Foundry must not propose a "new" public story the repository already published.
    """
    idx, rows = index(corpus), []
    claimed_models, claimed_datasets = set(), set()
    for c in entities_of(corpus, "claim"):
        claimed_models |= {str(x) for x in c["attrs"].get("components", [])}
        claimed_datasets |= {"dataset:" + str(x)
                             for x in c["attrs"].get("dataset_manifest_ids", [])}

    for obs, (models, datasets) in sorted(_observable_support(corpus).items()):
        if len(models) < 2 or not datasets:
            continue
        fresh = [d for d in datasets if d not in claimed_datasets]
        if not fresh:
            continue
        rows.append(Tension(
            tension_id="", lens="public_story", entity_ids=tuple(models + fresh[:6]),
            shared_observable=obs.split(":")[-1],
            difference_type="unclaimed_contrast_with_data",
            difference_summary="%s is predicted by %d model(s) and measured by %d manifest dataset(s), "
                               "of which %d are not cited by any existing public claim"
                               % (obs.split(":")[-1], len(models), len(datasets), len(fresh)),
            evidence_basis="existing claim inventory (%d claims) checked for overlap"
                           % len(entities_of(corpus, "claim")),
            why_it_matters="A contrast with data in hand and no published claim is the cheapest "
                           "route to a public output — subject to a scope sentence and a badge.",
            candidate_discriminator=obs.split(":")[-1],
            data_available="YES", cheap_test_possible="YES",
            provenance=tuple(_prov(idx[d], mode="csv_row", confidence="explicit")
                             for d in fresh[:4])))
    return rows

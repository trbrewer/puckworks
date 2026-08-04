"""Candidate generation — tension rows into falsifiable questions.

Every generated candidate carries one question, one cheap test, one stop condition, and status
`SEED`. Nothing here scores, ranks, or adjudicates: scoring is a human/LLM triage aid applied
after a person has read the portfolio (blueprint §11), and a generator that scored its own output
would be the "LLM score as a scientific decision" the blueprint's §2.3 non-goals rule out.

Generation is deterministic and grouped. 170 tension rows do not become 170 candidates: rows are
grouped by `(lens, difference_type, grouping key)` so that fifteen manifest rows sharing one
lineage problem become one question about that problem, with all fifteen cited. That is the
blueprint's §19.1 control against candidate explosion — dedupe by question and evidence unit.

Each `(lens, difference_type)` pair has a TEMPLATE giving the question shape, the cheap screen,
the decision rule, and the audience tracks. Templates state the SHAPE of an answer, never its
direction: "does the sign survive the swap" is a question, "the sign survives the swap" would be
a finding this layer may not produce.
"""
from __future__ import annotations

from .corpus_map import index
from .schema import Candidate

GENERATOR_VERSION = 1


def _label(idx, eid):
    e = idx.get(eid)
    return e["label"] if e else eid.split(":", 1)[-1]


def _stage_of(idx, eid):
    e = idx.get(eid)
    return (e or {}).get("attrs", {}).get("stage", "")


def _source_of(eid):
    """Source prefix of an entity id — the grouping key for same-source families."""
    local = eid.split(":", 1)[-1]
    return local.split(".")[0].split("/")[0]


# ---- grouping keys -----------------------------------------------------------------------
#
# One entry per (lens, difference_type) the generator handles. `key` maps a tension row to the
# group it joins; rows with no entry fall back to one candidate per row.

def _key_by_stage_observable(t, idx):
    return (t.shared_domain or "", t.shared_observable or "")


def _key_by_first_source(t, idx):
    return (_source_of(t.entity_ids[0]),) if t.entity_ids else ("",)


def _key_single(t, idx):
    return ("all",)


def _key_by_lineage_tags(t, idx):
    """Group mixed-strength datasets by WHICH strengths the cell mixes, not by which paper.

    Grouping these by source produced 22 near-identical candidates — one per paper — asking the
    same question 22 times. The interesting unit is the failure mode: a cell claiming both
    `independent` and `post_fit` is a different problem from one claiming both `reference_only`
    and `qualitative`, and each grouping cites every dataset that exhibits it.
    """
    e = idx.get(t.entity_ids[0]) if t.entity_ids else None
    tags = (e or {}).get("attrs", {}).get("lineage_tags", [])
    return (" + ".join(sorted(x for x in tags if x != "mixed_strength")) or "unclassified",)


GROUPING = {
    ("model_disagreement", "comparable_not_yet_executed"): _key_by_stage_observable,
    ("lineage_circularity", "mixed_strength_cell"): _key_by_lineage_tags,
    ("lineage_circularity", "same_source_consumer"): _key_by_first_source,
    ("lineage_circularity", "unresolvable_source_card"): _key_single,
    ("composition_failure", "same_source_variant_pair"): _key_by_first_source,
    ("cross_species_inconsistency", "one_state_many_species"): _key_single,
    ("hidden_discriminator", "card_without_interface_mapping"): _key_single,
}


# ---- templates ---------------------------------------------------------------------------
#
# `question`/`cheap_test`/etc. are format strings over `{subject}` (a short description of the
# group) and `{n}` (how many tension rows it covers).

TEMPLATES = {
    ("model_disagreement", "declared_competitor"): {
        "title": "Do {subject} actually disagree, or only claim to?",
        "question": "Under one matched scenario, do {subject} differ in sign, ordering, or "
                    "magnitude on an observable they both produce?",
        "insight_types": ("model_disagreement",),
        "audience_tracks": ("technical_note", "domain_paper"),
        "cheap_test": "Run both components over one matched, physically coherent scenario and "
                      "plot the shared observable. No refit, no new physics.",
        "minimum_figure": "The shared observable versus its controlling input, one curve per "
                          "component, with each component's declared validity range shaded.",
        "survive_if": "The components differ by more than their declared uncertainty on a "
                      "point inside both validity ranges.",
        "retire_if": "The curves overlap within declared uncertainty, or the ranges do not "
                     "intersect at all (they answer different questions).",
        "inconclusive_if": "Neither component can be run in a matched configuration without "
                           "inventing a parameter the cards do not provide.",
        "stop_condition": "Predictions overlap once each component's declared uncertainty is "
                          "drawn.",
        "why_it_may_matter": "A card-declared competitor that turns out to agree is a merge "
                             "opportunity; one that disagrees is a discrimination experiment.",
        "strongest_alternative": "The two components are not answering the same question — the "
                                 "observable is named the same but defined differently "
                                 "(pressure-node or observable-convention mismatch).",
        "novelty_search_terms": ("espresso extraction model comparison", "model discrimination "
                                 "porous media", "matched-scenario model benchmarking"),
    },
    ("model_disagreement", "comparable_not_yet_executed"): {
        "title": "Do the {subject} components agree where they overlap?",
        "question": "Across the {n} comparable component pairs on {subject}, which agree within "
                    "declared uncertainty and which do not?",
        "insight_types": ("model_disagreement", "methods"),
        "audience_tracks": ("technical_note", "methods_paper"),
        "cheap_test": "Matched-scenario sweep over the pairs, one shared observable at a time; "
                      "classify each pair agree / disagree / not comparable.",
        "minimum_figure": "A pair-by-pair agreement matrix with the not-comparable cells marked "
                          "and their reason given.",
        "survive_if": "At least one pair disagrees materially inside both declared ranges.",
        "retire_if": "Every pair either agrees or is not comparable for a stated reason.",
        "inconclusive_if": "Matched scenarios cannot be constructed from carded parameters alone.",
        "stop_condition": "Every pair is classified, with reasons for the not-comparable ones.",
        "why_it_may_matter": "This is the disagreement map the registry implies but has never "
                             "been made to state.",
        "strongest_alternative": "Apparent disagreement is a units or convention artifact "
                                 "(ledger A1/A7/A10), not physics.",
        "novelty_search_terms": ("multi-model comparison espresso", "structural model "
                                 "uncertainty porous media"),
    },
    ("lineage_circularity", "mixed_strength_cell"): {
        "title": "Which strength is load-bearing where the manifest says '{subject}'?",
        "question": "For the {n} datasets whose validation_strength names both {subject}, which "
                    "of those strengths does each consuming gate actually rely on?",
        "insight_types": ("data_lineage",),
        "audience_tracks": ("data_note", "technical_note"),
        "cheap_test": "For each cell, read the consuming gate and record which half of the "
                      "strength statement its assertion depends on. Source audit, no execution.",
        "minimum_figure": "A table of dataset, verbatim strength cell, consuming gate, and the "
                          "half of the cell the gate leans on.",
        "survive_if": "At least one gate leans on the stronger half of a cell whose relevant "
                      "half is the weaker one.",
        "retire_if": "Every consuming gate already reads the correct half.",
        "inconclusive_if": "The consuming gate's assertion is too coarse to attribute to either "
                           "half.",
        "stop_condition": "Every mixed cell is attributed to a gate and a half.",
        "why_it_may_matter": "A promotion here propagates into every downstream claim citing the "
                             "dataset.",
        "strongest_alternative": "The cell is mixed only in wording; both halves support the "
                                 "same gate assertion equally.",
        "novelty_search_terms": ("validation data provenance", "circular validation model "
                                 "calibration"),
    },
    ("lineage_circularity", "same_source_consumer"): {
        "title": "Is {subject} evaluated against data it is not independent of?",
        "question": "For the {n} {subject} datasets sharing a source card with a component the "
                    "manifest links to them, does any gate read that pairing as independent?",
        "insight_types": ("data_lineage",),
        "audience_tracks": ("data_note", "technical_note"),
        "cheap_test": "Cross-read the manifest lineage against each gate's claimed evaluation "
                      "relationship; list every same-source pairing and how it is labelled.",
        "minimum_figure": "A lineage graph of dataset to source card to consuming component, "
                          "with same-source edges highlighted.",
        "survive_if": "A same-source pairing is labelled independent anywhere downstream.",
        "retire_if": "Every same-source pairing is already labelled as within-campaign or "
                     "post-fit.",
        "inconclusive_if": "The manifest cannot say whether the fit and evaluation rows come "
                           "from the same campaign.",
        "stop_condition": "Every same-source pairing carries an accurate relationship label.",
        "why_it_may_matter": "Same-source evaluation is the most common way a model looks better "
                             "validated than it is.",
        "strongest_alternative": "Sharing a source card does not mean sharing a campaign — the "
                                 "rows may be a genuine held-out split.",
        "novelty_search_terms": ("held-out validation same campaign", "data leakage model "
                                 "calibration"),
    },
    ("lineage_circularity", "unresolvable_source_card"): {
        "title": "The manifest's source_card column is not mechanically traceable",
        "question": "For the {n} manifest rows whose source_card resolves to no single card, "
                    "which card did the data actually come from?",
        "insight_types": ("data_lineage", "methods"),
        "audience_tracks": ("data_note",),
        "cheap_test": "Resolve each unresolvable cell by hand against the cited artifact and "
                      "record the correct stem; note whether the ambiguity is real (one paper, "
                      "two cards) or a formatting slip.",
        "minimum_figure": "A table of unresolvable cells with the resolved stem and the reason.",
        "survive_if": "Any row's lineage turns out to differ from what a reader would assume.",
        "retire_if": "Every cell is a formatting slip with one obvious correct stem.",
        "inconclusive_if": "The source artifact does not say which chapter the rows came from.",
        "stop_condition": "Every unresolvable cell is resolved or explicitly marked ambiguous.",
        "why_it_may_matter": "Lineage that cannot be followed mechanically cannot be checked for "
                             "circularity at all.",
        "strongest_alternative": "The ambiguity is cosmetic and no downstream claim depends on "
                                 "which of the two cards is meant.",
        "novelty_search_terms": ("dataset provenance metadata quality",),
    },
    ("closure_portability", "closure_producer"): {
        "title": "Does {subject} survive being used outside the range it was fitted in?",
        "question": "Does a result that consumes {subject} change materially when the closure is "
                    "swapped for another source's, or driven outside its declared validity?",
        "insight_types": ("closure_portability",),
        "audience_tracks": ("technical_note", "methods_paper"),
        "cheap_test": "Source-swap sensitivity: hold the consuming configuration fixed, swap the "
                      "closure, and record the change in the consuming observable. Then sweep to "
                      "the edge of the declared range.",
        "minimum_figure": "Consuming observable versus the closure's driving variable, one curve "
                          "per closure source, with the declared range shaded.",
        "survive_if": "The consuming result moves by more than its own stated uncertainty under "
                      "the swap, or the closure is already consumed outside its declared range.",
        "retire_if": "The consuming result is insensitive to the swap across the used range.",
        "inconclusive_if": "No second source exists for the closure and no range is declared.",
        "stop_condition": "The swap changes the consuming result by less than its uncertainty.",
        "why_it_may_matter": "Closures travel between sources far more readily than the "
                             "conditions they were fitted under.",
        "strongest_alternative": "The consuming model is insensitive to this closure entirely, "
                                 "so portability is moot for it.",
        "novelty_search_terms": ("closure transferability porous media", "correlation "
                                 "extrapolation validity range", "permeability correlation "
                                 "portability"),
    },
    ("composition_failure", "same_source_variant_pair"): {
        "title": "Does the extra mechanism in the {subject} components earn its place?",
        "question": "For the {n} {subject} component pairs where one adds a mechanism the other "
                    "lacks, does the addition improve held-out prediction or only fit?",
        "insight_types": ("model_composition",),
        "audience_tracks": ("methods_paper", "technical_note"),
        "cheap_test": "Held-out comparison of base versus base-plus-mechanism on one evidence "
                      "unit, run twice: without recalibration and with.",
        "minimum_figure": "Held-out error for base and base-plus-mechanism, both branches, with "
                          "replicate variation drawn.",
        "survive_if": "The added mechanism worsens held-out error, or improves it only after "
                      "recalibration (compensating error).",
        "retire_if": "The addition improves held-out error in both branches.",
        "inconclusive_if": "No held-out unit exists for the pair.",
        "stop_condition": "The held-out difference is smaller than replicate variation.",
        "why_it_may_matter": "More physics is not automatically better prediction, and the "
                             "repository already holds one case where it was worse.",
        "strongest_alternative": "The two components are not a base/superset pair at all — they "
                                 "are alternative reductions of one source.",
        "novelty_search_terms": ("model complexity held-out prediction", "compensating errors "
                                 "model calibration"),
    },
    ("composition_failure", "published_composition_failure"): {
        "title": "Does the published composition failure generalise?",
        "question": "Beyond the one published case, which added mechanisms improve held-out "
                    "observables across component combinations, and which do not?",
        "insight_types": ("model_composition", "methods"),
        "audience_tracks": ("methods_paper",),
        "cheap_test": "Apply the published case's base-plus-one-mechanism protocol to a "
                      "predeclared set of other combinations, same objective and evidence unit.",
        "minimum_figure": "Held-out error change per added mechanism, one row per combination.",
        "survive_if": "The direction varies across combinations — the phenomenon is general "
                      "enough to be worth a method.",
        "retire_if": "Every other combination behaves the same way as the published one.",
        "inconclusive_if": "Fewer than three combinations can be run on a common evidence unit.",
        "stop_condition": "The protocol cannot be applied to a second combination.",
        "why_it_may_matter": "One case is an anecdote; a protocol over many is a method.",
        "strongest_alternative": "The published failure is specific to that swelling branch and "
                                 "says nothing about composition in general.",
        "novelty_search_terms": ("model composition benchmark", "added physics prediction "
                                 "degradation"),
    },
    ("cross_species_inconsistency", "one_state_many_species"): {
        "title": "Can one transport state explain every measured species at once?",
        "question": "Under one shared hydraulic and transport state, do the per-species residuals "
                    "show structure that a single kinetic story cannot absorb?",
        "insight_types": ("cross_species", "identifiability"),
        "audience_tracks": ("domain_paper", "technical_note"),
        "cheap_test": "Fit one shared state across species and inspect the per-species residual "
                      "structure; compare against per-species independent fits.",
        "minimum_figure": "Per-species residuals versus time under the shared fit, with the "
                          "independent-fit residuals overlaid.",
        "survive_if": "Residual structure is species-specific and survives the independent-fit "
                      "comparison.",
        "retire_if": "Residuals are unstructured, or the structure is common to all species "
                     "(a shared model-form problem, not a species one).",
        "inconclusive_if": "Species measurements come from too few campaigns to separate "
                           "species effects from campaign effects.",
        "stop_condition": "Per-species residual structure is within measurement uncertainty.",
        "why_it_may_matter": "It separates species-specific diffusion from inventory "
                             "mis-specification — two very different corrections.",
        "strongest_alternative": "The apparent species difference is a measurement-lineage "
                                 "difference between the assays, not chemistry.",
        "novelty_search_terms": ("multi-solute extraction kinetics coffee", "species-specific "
                                 "diffusion coffee", "trigonelline caffeine chlorogenic "
                                 "extraction"),
    },
    ("hidden_discriminator", "discriminator_with_data"): {
        "title": "Can {subject} discriminate between the models that predict it?",
        "question": "Does {subject}, measured by data already in the manifest, separate the "
                    "models that predict it by more than their within-model uncertainty?",
        "insight_types": ("hidden_discriminator", "experiment_design"),
        "audience_tracks": ("technical_note", "experiment_design", "public_story"),
        "cheap_test": "Signature atlas: predicted {subject} per model over a matched domain, "
                      "against the manifest measurements, with replicate variation drawn.",
        "minimum_figure": "Predicted {subject} per model versus its controlling input, with the "
                          "measured points and their spread overlaid.",
        "survive_if": "Between-model separation exceeds within-model uncertainty somewhere the "
                      "data lands.",
        "retire_if": "Model predictions overlap once uncertainty is drawn, or the measurements "
                     "fall outside every model's validity range.",
        "inconclusive_if": "The measurements are single-replicate and no spread can be drawn.",
        "stop_condition": "Predictions overlap after declared uncertainty.",
        "why_it_may_matter": "Discrimination without new measurement is the cheapest decisive "
                             "screen the corpus can offer.",
        "strongest_alternative": "The observable is defined differently by each model, so the "
                                 "separation is a convention artifact.",
        "novelty_search_terms": ("model discrimination observable selection", "espresso "
                                 "extraction mechanism discrimination"),
    },
    ("hidden_discriminator", "card_without_interface_mapping"): {
        "title": "The model/observable matrix has {n} blind spots from card template deviations",
        "question": "Which observables do the {n} registered components without an Interface "
                    "mapping section actually produce, and what does the matrix currently hide?",
        "insight_types": ("methods", "corpus_hygiene"),
        "audience_tracks": ("data_note",),
        "cheap_test": "Read each affected card and write its Interface mapping section from the "
                      "card's own content; re-run the corpus map and diff the matrix.",
        "minimum_figure": "The model/observable matrix before and after, with the recovered "
                          "cells marked.",
        "survive_if": "A recovered cell changes which observables have two or more predicting "
                      "models — that is, it opens or closes a discrimination.",
        "retire_if": "Every recovered cell duplicates a mapping the matrix already had.",
        "inconclusive_if": "The card's content does not state what the component outputs.",
        "stop_condition": "Every affected card carries the section and the matrix is stable.",
        "why_it_may_matter": "first_drip_time reads as unmodelled today purely because of this; "
                             "the blueprint's own flagship candidate is invisible to the matrix.",
        "strongest_alternative": "The deviating cards are deliberately non-template (audits, "
                                 "search targets) and have no interface to declare.",
        "novelty_search_terms": (),
    },
    ("hidden_discriminator", "measured_but_unmodelled"): {
        "title": "{subject} is measured but no card claims to produce it",
        "question": "Is {subject} genuinely unmodelled by the registry, or hidden by a card that "
                    "never declared its outputs?",
        "insight_types": ("corpus_hygiene", "experiment_design"),
        "audience_tracks": ("data_note", "technical_note"),
        "cheap_test": "Check each registered component on the relevant stages against its card "
                      "for an undeclared {subject} output; if none, record it as a modelling gap.",
        "minimum_figure": "Components on the relevant stages versus whether they declare "
                          "{subject}, with the measuring datasets listed.",
        "survive_if": "A component produces {subject} without declaring it — a matrix repair "
                      "that opens a discrimination.",
        "retire_if": "No registered component produces it: a genuine modelling gap, recorded "
                     "as such.",
        "inconclusive_if": "Whether the component produces it depends on an unimplemented "
                           "coupling.",
        "stop_condition": "Every candidate component is checked against its card.",
        "why_it_may_matter": "Measured-but-unmodelled is either a modelling gap or a card gap, "
                             "and the two call for opposite work.",
        "strongest_alternative": "The measurement and the model output share a name but not a "
                                 "definition.",
        "novelty_search_terms": (),
    },
    ("missing_experiment", "predicted_but_unmeasured"): {
        "title": "{subject} is predicted by several models and measured by none",
        "question": "What is the minimum measurement of {subject} that would separate the models "
                    "predicting it?",
        "insight_types": ("experiment_design", "missing_measurement"),
        "audience_tracks": ("experiment_design", "public_story"),
        "cheap_test": "Predicted-signature spread across the models over a feasible domain, to "
                      "size the measurement precision a discriminating experiment would need.",
        "minimum_figure": "Predicted {subject} per model with the measurement precision required "
                          "to separate them marked.",
        "survive_if": "A feasible measurement precision separates at least two models.",
        "retire_if": "The required precision is beyond any feasible apparatus.",
        "inconclusive_if": "Model predictions cannot be put on a common domain.",
        "stop_condition": "The required precision is established, feasible or not.",
        "why_it_may_matter": "Models can disagree about this indefinitely because nothing in the "
                             "corpus can referee it.",
        "strongest_alternative": "The observable is already constrained indirectly by a "
                                 "measurement the manifest records under another name.",
        "novelty_search_terms": ("experimental design model discrimination", "optimal "
                                 "measurement selection"),
    },
    ("negative_result", "standing_negative_verdict"): {
        "title": "Does the negative result in {subject} generalise beyond its configuration?",
        "question": "Is the negative verdict recorded in {subject} a property of the mechanism, "
                    "or of the one configuration it was tested in?",
        "insight_types": ("negative_result",),
        "audience_tracks": ("technical_note", "domain_paper"),
        "cheap_test": "Re-run the recorded analysis under a second configuration drawn from the "
                      "same declared validity range, changing one factor.",
        "minimum_figure": "The verdict statistic under both configurations, with the decision "
                          "threshold drawn.",
        "survive_if": "The verdict reverses or weakens materially under the second "
                      "configuration — the result was configuration-specific.",
        "retire_if": "The verdict holds, which strengthens the existing negative record rather "
                     "than producing a new one.",
        "inconclusive_if": "No second configuration is available inside the declared range.",
        "stop_condition": "The second configuration is run and the verdict compared.",
        "why_it_may_matter": "A recorded negative result is publishable material and stops the "
                             "same ground being retrodden.",
        "strongest_alternative": "The negative result is already correctly scoped in the "
                                 "document and no generalisation was ever claimed.",
        "novelty_search_terms": ("negative results modelling", "reproducibility negative "
                                 "findings"),
    },
    ("evidence_asymmetry", "leaned_on_but_not_empirically_tested"): {
        "title": "{subject} is leaned on more than its evidence supports",
        "question": "Do the results that position themselves against {subject} depend on it in a "
                    "way its registry evidence strength does not support?",
        "insight_types": ("evidence_asymmetry",),
        "audience_tracks": ("technical_note", "data_note"),
        "cheap_test": "For each citing card, read what it actually takes from the component and "
                      "check that against the component's verbatim evidence strength.",
        "minimum_figure": "Citing card versus what it borrows versus the component's evidence "
                          "strength.",
        "survive_if": "A citing result depends on the component for something stronger than its "
                      "evidence strength supports.",
        "retire_if": "Every citing card borrows only what the evidence strength covers.",
        "inconclusive_if": "What the citing card borrows is not stated precisely enough to "
                           "check.",
        "stop_condition": "Every citing card is checked.",
        "why_it_may_matter": "Corpus-internal prominence is not evidence, and readers routinely "
                             "read one as the other.",
        "strongest_alternative": "The citing cards position against it rhetorically without "
                                 "depending on it at all.",
        "novelty_search_terms": ("evidence strength model reuse",),
    },
    ("scale_mismatch", "pore_scale_vs_continuum"): {
        "title": "Do the continuum permeability closures preserve the pore-scale trend?",
        "question": "Across the geometries the pack generator can produce, does the continuum "
                    "closure reproduce the pore-scale solver's permeability trend?",
        "insight_types": ("scale_bridging", "closure_portability"),
        "audience_tracks": ("methods_paper", "technical_note"),
        "cheap_test": "Permeability from the pore-scale solver versus the continuum closure over "
                      "one geometry family, plus an RVE-size sweep for stabilisation.",
        "minimum_figure": "Permeability versus porosity, solver and closure overlaid, with the "
                          "RVE size at which the solver stabilises marked.",
        "survive_if": "The closure and solver trends diverge inside the geometry family, or no "
                      "RVE size stabilises the solver.",
        "retire_if": "Closure and solver agree within solver uncertainty across the family.",
        "inconclusive_if": "The solver cannot be run at an RVE size large enough to stabilise.",
        "stop_condition": "The trends agree within solver uncertainty.",
        "why_it_may_matter": "A closure that does not preserve the pore-scale trend silently "
                             "limits every bed-scale prediction built on it.",
        "strongest_alternative": "The synthetic geometries are not representative of a real "
                                 "puck, so neither curve is the reference.",
        "novelty_search_terms": ("REV size permeability packed bed", "pore-scale to continuum "
                                 "upscaling permeability"),
    },
    ("public_story", "unclaimed_contrast_with_data"): {
        "title": "Is {subject} a public story the repository has not told?",
        "question": "Does {subject} carry one defensible surprise, with data already in the "
                    "manifest and no existing public claim covering it?",
        "insight_types": ("public_story",),
        "audience_tracks": ("public_story", "practitioner"),
        "cheap_test": "Draft the contrast against the existing claim inventory and check it can "
                      "be stated within the badge its weakest supporting evidence allows.",
        "minimum_figure": "The contrast in one panel, with the badge and scope sentence on the "
                          "figure itself.",
        "survive_if": "The contrast is defensible at a badge the evidence supports and no "
                      "existing claim already makes it.",
        "retire_if": "It needs a badge the evidence does not support, or duplicates a claim.",
        "inconclusive_if": "The supporting datasets are single-replicate, so the contrast "
                           "cannot be separated from run-to-run variation.",
        "stop_condition": "The contrast cannot be stated without exceeding its evidence badge.",
        "why_it_may_matter": "The public track consumes results; a contrast with data in hand is "
                             "the cheapest honest output.",
        "strongest_alternative": "The contrast is an artifact of pooling datasets from different "
                                 "rigs and coffees.",
        "novelty_search_terms": (),
    },
}


# ---- generation ---------------------------------------------------------------------------


def _subject(lens: str, dtype: str, group_key, rows, idx) -> str:
    """A short human phrase naming what a candidate group is about."""
    first = rows[0]
    if (lens, dtype) == ("model_disagreement", "declared_competitor"):
        return " and ".join(_label(idx, e) for e in first.entity_ids[:2])
    if (lens, dtype) == ("model_disagreement", "comparable_not_yet_executed"):
        stage, obs = group_key
        return "%s-stage %s" % (stage or "cross-stage", obs or "shared-observable")
    if lens == "closure_portability":
        return _label(idx, first.entity_ids[0])
    if lens in ("hidden_discriminator", "missing_experiment", "public_story") and \
            first.shared_observable:
        return first.shared_observable
    if lens == "negative_result":
        return first.entity_ids[0].split(":", 1)[-1]
    if lens == "evidence_asymmetry":
        return _label(idx, first.entity_ids[0])
    if group_key and group_key[0] not in ("", "all"):
        return str(group_key[0])
    return lens.replace("_", " ")


def generate(corpus: dict, tensions) -> list:
    """Group the tension rows and emit one `SEED` candidate per group.

    Deterministic: groups are built in sorted key order, so the same tree yields the same ids.
    """
    idx = index(corpus)
    commit = corpus.get("commit", "")

    groups = {}
    for t in tensions:
        key_fn = GROUPING.get((t.lens, t.difference_type))
        gkey = key_fn(t, idx) if key_fn else (t.tension_id,)
        groups.setdefault((t.lens, t.difference_type, gkey), []).append(t)

    candidates = []
    ordered = sorted(groups.items(),
                     key=lambda kv: (kv[0][0], kv[0][1], tuple(map(str, kv[0][2]))))
    for (lens, dtype, gkey), rows in ordered:
        tpl = TEMPLATES.get((lens, dtype))
        if tpl is None:
            continue
        subject = _subject(lens, dtype, gkey, rows, idx)
        fmt = {"subject": subject, "n": len(rows)}
        entity_ids = []
        for t in rows:
            for e in t.entity_ids:
                if e not in entity_ids:
                    entity_ids.append(e)
        candidates.append(Candidate(
            id="I-%03d" % (len(candidates) + 1),
            title=tpl["title"].format(**fmt),
            question=tpl["question"].format(**fmt),
            lens=lens,
            tension_ids=tuple(t.tension_id for t in rows),
            entity_ids=tuple(entity_ids),
            cheap_test=tpl["cheap_test"].format(**fmt),
            stop_condition=tpl["stop_condition"].format(**fmt),
            status="SEED",
            insight_types=tuple(tpl["insight_types"]),
            audience_tracks=tuple(tpl["audience_tracks"]),
            why_it_may_matter=tpl["why_it_may_matter"].format(**fmt),
            why_it_may_surprise="",
            strongest_alternative=tpl["strongest_alternative"].format(**fmt),
            minimum_figure=tpl["minimum_figure"].format(**fmt),
            survive_if=tpl["survive_if"].format(**fmt),
            retire_if=tpl["retire_if"].format(**fmt),
            inconclusive_if=tpl["inconclusive_if"].format(**fmt),
            existing_evidence=tuple(sorted({t.evidence_basis for t in rows if t.evidence_basis})),
            lineage_risks=(),
            novelty_search_terms=tuple(tpl["novelty_search_terms"]),
            scores={},
            history=(),
            source_commit=commit))
        for t in rows:
            t.candidate_id = candidates[-1].id
    return candidates


def portfolio_summary(candidates) -> dict:
    """Generated counts over the portfolio — diversity by lens, track, and status."""
    by_lens, by_track, by_status = {}, {}, {}
    for c in candidates:
        by_lens[c.lens] = by_lens.get(c.lens, 0) + 1
        by_status[c.status] = by_status.get(c.status, 0) + 1
        for t in c.audience_tracks:
            by_track[t] = by_track.get(t, 0) + 1
    return {"total": len(candidates), "by_lens": dict(sorted(by_lens.items())),
            "by_audience_track": dict(sorted(by_track.items())),
            "by_status": dict(sorted(by_status.items()))}

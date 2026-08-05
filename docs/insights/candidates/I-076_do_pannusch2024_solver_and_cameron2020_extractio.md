# I-076 — Do pannusch2024.solver and cameron2020.extraction_bdf actually disagree, or only claim to?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Under one matched scenario, do pannusch2024.solver and cameron2020.extraction_bdf differ in sign, ordering, or magnitude on an observable they both produce?

## Insight type

model_disagreement

## Target audiences

technical_note, domain_paper

## Why it may matter

A card-declared competitor that turns out to agree is a merge opportunity; one that disagrees is a discrimination experiment.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:pannusch2024.solver`
- `model:cameron2020.extraction_bdf`

## Tension rows

T-0156

## Existing evidence

- pannusch2024.solver (post_fit_reconstruction) vs cameron2020.extraction_bdf (code_verification) — registry evidence strengths, verbatim

## Strongest alternative explanation

The two components are not answering the same question — the observable is named the same but defined differently (pressure-node or observable-convention mismatch).

## Cheap scientific screen

Run both components over one matched, physically coherent scenario and plot the shared observable. No refit, no new physics.

## Minimum viable figure

The shared observable versus its controlling input, one curve per component, with each component's declared validity range shaded.

## Decision rule

- **SURVIVE if** The components differ by more than their declared uncertainty on a point inside both validity ranges.
- **RETIRE if** The curves overlap within declared uncertainty, or the ranges do not intersect at all (they answer different questions).
- **INCONCLUSIVE if** Neither component can be run in a matched configuration without inventing a parameter the cards do not provide.

## Stop condition

Predictions overlap once each component's declared uncertainty is drawn.

## Possible outputs

- technical_note
- domain_paper

## External novelty search terms

- espresso extraction model comparison
- model discrimination porous media
- matched-scenario model benchmarking

_Run only after the candidate survives its cheap screen (blueprint §13.4)._

## Status

SEED

Transitions require a one-line reason appended here.

---

## Human triage (IF-5)

*Hand-written on 2026-08-04, after the generated body above. Everything above this line is generator
output at the `c1b7d79e…` corpus snapshot and is preserved byte-identical — question, stable ID,
entity relations, tension rows and provenance included. The decision record is
[`../IF5_HUMAN_TRIAGE_DECISION.md`](../IF5_HUMAN_TRIAGE_DECISION.md).*

**Provenance of this card.** Content derives from corpus snapshot
`c1b7d79e8f6800df16ad4fc195d45bf156e4ec8b`; the card file was materialised by
`python -m puckworks.insights card I-076` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-076
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Wave 2 — after Wave 1 reports.** The most executable of the eighteen `model_disagreement`
candidates: both components are registered runtimes that already run against the same
angeloni total-solids target, so a matched scenario is reachable without inventing a card
parameter.

**Held back from Wave 1 deliberately.** A matched-scenario comparison is **RP-A's** scope
(ROADMAP §9, `docs/analysis/COMPONENT_RESPONSE_ATLAS_SPEC.md`). Wave 1 must not smuggle
response-sweep machinery into the Foundry — that is the standing constraint, not a preference.
This screen runs a **single** matched scenario, not a sweep, and consumes RP-A's output when RP-A
lands rather than rebuilding it.

### Strongest alternative explanation (human)

As generated — *the observable is named the same but defined differently* — with the concrete
mechanism named: `pannusch2024.solver` reports a **fraction-averaged outlet concentration** per
solute, integrated over a stopping rule; `cameron2020.extraction_bdf` reports whole-cup TDS. The
manifest already records that "cameron reads ~2–4 pts LOW" against the angeloni total-solids
envelope. A difference of that size is fully consistent with an observable-convention and
stopping-rule mismatch (ledger A10, §5.10) rather than with a physical disagreement.

Second alternative: the two carry different evidence strengths (`post_fit_reconstruction` vs
`code_verification`), so a difference may sit inside cameron's unvalidated region rather than
between two validated predictions.

### Precise cheap screen

One matched, physically coherent scenario; no refit, no new physics. Before any comparison, fix and
record: the pressure-node convention (§5.9 / ledger A1), the observable definition and stopping rule
(§5.10 / ledger A10), the inventory basis, and the intersection of the two declared validity ranges.
Plot the shared observable with each component's declared validity range shaded.

**Quarantine:** `cameron2020.paper_mode` is import-order sensitive and stays out of this package
(CLAUDE.md rule 10). Only `cameron2020.extraction_bdf` is in scope.

### Primary figure

Shared observable vs its controlling input, one curve per component, each declared validity range
shaded, with the convention actually used stated on the figure.

### Decision criteria

- **SURVIVE** — the components differ by more than their declared uncertainty at a point inside
  **both** validity ranges, **after** the observable definition and stopping rule are matched.
- **RETIRE** — the curves overlap within declared uncertainty, the ranges do not intersect, or the
  difference is fully accounted for by the observable/stopping-rule convention.
- **NEEDS_NEW_DATA** — neither component can be run in a matched configuration without inventing a
  parameter the cards do not provide.

### Likely output class

`technical_note`. A confirmed agreement is a merge opportunity; a confirmed disagreement is a
discrimination-experiment design, which hands off to RP-A / PV-08 rather than to a manuscript.

### Screen outcome (appended after the Wave-2 screen ran)

**NEEDS_NEW_DATA** — `docs/insights/screens/I-076/`. Not a retirement, so **not** recorded in
`RETIRED_CANDIDATES.md`, and not in the IF-7 queue either.

**No model was executed.** The protocol was frozen and committed before any result-producing
commit, and the determination is reached at scenario construction. A good scenario exists — the
source's own DoE Central Point, with measured flow, measured temperature, a matched 40 g endpoint
and six replicates of a shared whole-cup TDS observable — but two independent blockers prevent the
two components from receiving the same intervention: their grind inputs are settings on
**different grinders** (Mahlkönig E65S vs EK43) with no declared adapter, and
`cameron2020.extraction_bdf` has **no temperature input at all**.

This card's high-risk framing anticipated a convention mismatch on the *observable*. The observable
was in fact bridgeable; the obstacle is upstream, at the **intervention**.

Missing evidence named: a measured E65S PSD at GL 1.4/1.7/2.0 on the same basis as
`cameron2020/psd_figure2`, **and** a temperature basis for cameron. Neither is sufficient alone.

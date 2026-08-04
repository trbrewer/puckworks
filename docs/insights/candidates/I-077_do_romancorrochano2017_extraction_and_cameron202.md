# I-077 — Do romancorrochano2017.extraction and cameron2020.extraction_bdf actually disagree, or only claim to?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Under one matched scenario, do romancorrochano2017.extraction and cameron2020.extraction_bdf differ in sign, ordering, or magnitude on an observable they both produce?

## Insight type

model_disagreement

## Target audiences

technical_note, domain_paper

## Why it may matter

A card-declared competitor that turns out to agree is a merge opportunity; one that disagrees is a discrimination experiment.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:romancorrochano2017.extraction`
- `model:cameron2020.extraction_bdf`

## Tension rows

T-0158

## Existing evidence

- romancorrochano2017.extraction (sign_or_compatibility) vs cameron2020.extraction_bdf (code_verification) — registry evidence strengths, verbatim

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
`python -m puckworks.insights card I-077` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-077
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**RESERVE.** Dominated by I-076: same lens, same method, weaker pairing.
`romancorrochano2017.extraction` carries `sign_or_compatibility` and `cameron2020.extraction_bdf`
carries `code_verification`, so **neither side's evidence is strong enough for an observed
difference to be attributable** to physics rather than to either component's own unvalidated
region. Running it before I-076 would spend a slot on the less informative of two near-identical
screens.

**Reserve is not retirement.** Not recorded in `RETIRED_CANDIDATES.md`; keeps its stable ID.

**Promotion condition:** if I-076 produces a usable matched-scenario protocol — a fixed pressure
node, observable definition, stopping rule and validity-range intersection — this candidate becomes
cheap (it reuses that protocol against a third component) and can be promoted without a new
decision.

### Strongest alternative explanation (human)

As generated — *the observable is named the same but defined differently* — and here it is
compounded: `romancorrochano2017.extraction` is a **stirred-vessel / lumped-bed** sphere-release
model, and `cameron2020.extraction_bdf` a whole-cup TDS runtime. Their natural observables are an
extraction *fraction* and a cup *concentration*. Relating them requires an inventory basis and a
stopping rule, and the choice of either can produce or erase an apparent disagreement.

### Precise cheap screen (once promoted)

Reuse I-076's protocol verbatim. One matched scenario, no refit, no new physics, conventions fixed
and recorded first. Do not build a sweep — that is RP-A.

**Quarantine:** `cameron2020.paper_mode` stays out (CLAUDE.md rule 10); only
`cameron2020.extraction_bdf` is in scope.

### Primary figure

Shared observable vs its controlling input, one curve per component, declared validity ranges
shaded, with the inventory basis and stopping rule stated on the figure.

### Decision criteria

- **SURVIVE** — the components differ by more than their declared uncertainty at a point inside both
  validity ranges, after the observable definition and stopping rule are matched. Note the standing
  constraint: with `sign_or_compatibility` on one side, a SURVIVE here can support a **sign**
  disagreement claim at most, never a magnitude one.
- **RETIRE** — curves overlap within declared uncertainty, ranges do not intersect, or the
  difference is accounted for by the observable/inventory/stopping-rule convention.
- **NEEDS_NEW_DATA** — no matched configuration exists without inventing a card parameter.

### Likely output class

Absorbed into I-076's `technical_note` as a third component, rather than a standalone output.

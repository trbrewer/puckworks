# I-072 — Do mo2023_2.swelling and brewer2026.streamtube actually disagree, or only claim to?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Under one matched scenario, do mo2023_2.swelling and brewer2026.streamtube differ in sign, ordering, or magnitude on an observable they both produce?

## Insight type

model_disagreement

## Target audiences

technical_note, domain_paper

## Why it may matter

A card-declared competitor that turns out to agree is a merge opportunity; one that disagrees is a discrimination experiment.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:mo2023_2.swelling`
- `model:brewer2026.streamtube`

## Tension rows

T-0147

## Existing evidence

- mo2023_2.swelling (source_curve_reproduction) vs brewer2026.streamtube (within_campaign_held_out) — registry evidence strengths, verbatim

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
`python -m puckworks.insights card I-072` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-072
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**High-risk — high value, high chance of a null.** Kept active because a confirmed
convention mismatch between two registered components is itself reportable; flagged high-risk
because it will probably retire on "they answer different questions", and settling it properly is
RP-A execution rather than a cheap screen.

### Strongest alternative explanation (human)

The generated alternative is not merely plausible here, it is the **expected** outcome:
`mo2023_2.swelling` produces a bed-deformation / porosity response under a fixed pressure drop,
while `brewer2026.streamtube` produces a lateral flow-distribution response. A "shared observable"
between them is a name, not a definition. The standing record already contains the concrete case:
`gate_kappa_t_composition_diagnostic` records that mo2023_2's fixed-ΔP swelling branch, imported
unrefitted into a shared porosity state, **over-closes** a saturated pre-wet bed — diagnosed as a
mis-scaled branch, "reported not tuned away". Any matched-scenario difference must be shown not to
be that same mis-scale.

`brewer2026.streamtube` also carries `UNRESOLVED_CARD`, so its declared validity range and
uncertainty are not card-sourced.

### Precise cheap screen

One matched, physically coherent scenario; no refit, no new physics. **Before running anything**,
establish that a shared observable exists under one definition — pressure node (§5.9 / ledger A1)
and observable convention (§5.10 / ledger A10) fixed and recorded. If it does not, the screen ends
there with a RETIRE on "different questions", and no execution is performed.

Do **not** build a response sweep. A sweep is RP-A (ROADMAP §9) and is out of scope for the Foundry.

### Readiness note

`brewer2026.streamtube` has no card at `docs/cards/brewer2026_streamtube.md` or
`docs/cards/brewer2026.md`. Its declared uncertainty must come from the registry entry
(`within_campaign_held_out`) and `gate_streamtube_heldout`, and that provenance must be stated on
the result rather than assumed.

### Primary figure

The shared observable vs its controlling input, one curve per component, each declared validity
range shaded — or, if no shared definition survives step 1, the two observable definitions side by
side showing why they are not the same quantity.

### Decision criteria

- **SURVIVE** — the components differ by more than their declared uncertainty at a point inside
  both validity ranges, under one fixed and recorded observable definition.
- **RETIRE** — the curves overlap within declared uncertainty, the validity ranges do not intersect,
  or no shared observable definition exists (the expected outcome).
- **NEEDS_NEW_DATA** — neither component can be run in a matched configuration without inventing a
  parameter the cards do not provide — including the case where `brewer2026.streamtube`'s missing
  card leaves its validity range undeclarable.

### Likely output class

`technical_note` at best. A confirmed "different questions" result is a **registry** finding about
declared-competitor rows, not a domain result.

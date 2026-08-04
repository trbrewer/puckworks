# I-015 — Does anything consume wadsworth2026.permeability, and does it survive outside its declared range?

> Generated from the insight portfolio at commit `56060e5b58`. A card is created when a person decides to work a candidate; everything below the Question is a STARTING POINT, not a result.

## Question

Which registered component, if any, actually consumes wadsworth2026.permeability's output — and does that consuming result change materially when the artifact is swapped for another source's or driven outside its declared validity?

## Insight type

calibration_artifact_portability

## Target audiences

technical_note, methods_paper

## Why it may matter

Calibration artifacts travel between sources far more readily than the conditions they were fitted under — but only along paths that actually exist, and the registry does not record those paths.

## Why it may be surprising

_not yet written — this is a seed._

## Models, datasets, and other entities

- `model:wadsworth2026.permeability`

## Tension rows

T-0015

## Existing evidence

- registry execution_role + valid_range + evidence_strength, verbatim. Same-stage co-location only; no output-to-input path was checked.

## Strongest alternative explanation

Nothing consumes this artifact at all, or the named same-stage component is insensitive to it, so portability is moot for it.

## Cheap scientific screen

Step 1 — establish the path: trace the artifact's produced output to a named component's consumed input, via the cards' Interface mapping sections and the registry module. If no path exists, STOP and record that. Step 2, only if a path exists — source-swap sensitivity: hold the consuming configuration fixed, swap the artifact, record the change in the consuming observable, then sweep to the edge of the declared range.

## Minimum viable figure

Consuming observable versus the artifact's driving variable, one curve per source, with the declared range shaded — or, where step 1 fails, the producer/consumer path diagram showing the missing edge.

## Decision rule

- **SURVIVE if** A consuming path exists AND the consuming result moves by more than its own stated uncertainty under the swap, or the artifact is already consumed outside its declared range.
- **RETIRE if** A consuming path exists and the consuming result is insensitive to the swap across the used range.
- **INCONCLUSIVE if** No consuming path can be established from the cards and registry — in which case the finding is the missing path, not a portability result.

## Stop condition

Either no consuming path is found, or the swap changes the consuming result by less than its uncertainty.

## Possible outputs

- technical_note
- methods_paper

## External novelty search terms

- closure transferability porous media
- correlation extrapolation validity range
- permeability correlation portability

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
`python -m puckworks.insights card I-015` at the foundation merge
`56060e5b589132c496c432fa09e61efea305d5cf`, which is what the generated header line stamps.
`python -m puckworks.insights verify` returns `OK` at both, so the snapshot did not drift.

**Shortlist status: `SHORTLISTED`** — recorded here only. The generated portfolio entry for I-015
is still `SEED` and still unscored; this selection is a human decision, not a generator score.

### Human lane

**Candidate-readiness — and the sharpest case in the lane, which is why it was shortlisted.** The
Foundry build itself already emits the finding: `NO_INTERFACE_MAPPING: docs/cards/wadsworth2026.md
(component wadsworth2026.permeability) — no observable edges inferred`. The corpus map has recorded
that this artifact has no traceable consumer edge; the candidate is the follow-through.

### Strongest alternative explanation (human)

As generated — *nothing consumes this artifact* — and here the corpus map has already said so, one
level up. The alternative to beat is therefore the opposite one: **the edge exists in code but not
in the card.** `gate_wadsworth_collapse` runs, so the component is executable and gated; the
question is whether any *other* component consumes its permeability output, or whether it is a
standalone gated artifact. Establishing that from module imports alone would be the
"co-location is not a relationship" error inverted — an edge asserted from code without a declared
interface is still not a declared relationship.

### Readiness prerequisite

Same as I-014, and explicitly recorded by the build: `docs/cards/wadsworth2026.md` has no
*Interface mapping* section, so no observable edges could be inferred for this component.

**Prerequisite: the Interface mapping section of `docs/cards/wadsworth2026.md`**, repaired once for
both I-014 and I-015.

### Precise cheap screen (once ready)

Step 1 — from the repaired Interface mapping, determine whether any registered component consumes
this permeability output. If none does, STOP: the result is that a gated calibration artifact has
no consumer, which is a registry finding worth recording and not a failure of the screen. Step 2,
only if a path exists — fixed-configuration source swap against the declared validity range.

### Primary figure

The producer/consumer path diagram showing the missing edge — the generated card's own fallback
figure, which here is the expected figure rather than the fallback.

### Decision criteria

- **SURVIVE** — a consuming path exists **and** the consuming result moves beyond its stated
  uncertainty under the swap, or the artifact is already consumed outside its declared range.
- **RETIRE** — a path exists and the consuming result is insensitive across the used range.
- **NEEDS_NEW_DATA** — no consuming path can be established from the repaired card. Expected
  outcome; the deliverable is then the recorded absence of the edge.

### Likely output class

`technical_note` on registry hygiene — specifically, on gated calibration artifacts with no
declared consumer. Not a physical result.
